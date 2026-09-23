> **FROZEN 2026-08-26 — the loader is normative, this document is not**
> (owner ruling, plan amendment A-P4-46.1). This describes the loader
> and producer as of commit `84dc192`. **Where this document and the
> code differ, THE CODE IS RIGHT**: `contract.py` enforces the format
> in executable form, the test suite pins what a description may hold,
> and the docstrings state each function's promises. This document is
> no longer edited as part of a landing; it is REGENERATED from the
> code before the first release, which is a release precondition
> recorded in the Phase 4 close list.
>
> **Why.** One new published fact had to be written in about ten
> places, and the landing before this ruling was 4,477 lines of which
> 60 were product code. The audience this document was written for —
> a stranger reimplementing synthtwin from the specification — does not
> exist yet, because nothing is released. It will exist at the release,
> and the regeneration is owed then.

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
absence map at five keys while version 6 introduces fourteen roles and
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

**1.7a Version 6 is extended in place until the first release**
(owner ruling 2026-08-26, plan amendment A-P4-41). Keys and a role
were added to version 6 after it was declared -- `kurtosis`,
`n_distinct_values`, `value_histogram`, `pad_widths`,
`forced_codes`, `forced_measurements`, `forced_decimal_commas`,
the census of written forms, `field_widths`, `empty_bins`,
`empty_edges`,
`group_separator` on the numeric blocks,
`datetime_separators` and `all_at_midnight` on the datetime block,
`min_length` and `max_length` on the unrepresentable role,
`value_histogram` on the numeric roles, and the joined-numbers role -- each time on the argument that no version 6
description exists outside this repository. The owner accepted that
argument rather than spending a version bump on it, and the rule it
suspends is stated here so no reader has to infer it: **a change that
adds a key or a member advances `profile_version` FROM THE FIRST
RELEASE ON**, and until that release version 6 is a moving target
inside this repository alone.

**What that costs, stated rather than discovered.** A description
written earlier on this branch is stamped 6, as is the reader, so the
version integers MATCH and the loader gives a plain missing-key refusal
instead of the message naming which options to supply again. Measured:
removing `forced_codes` from a current document yields "The description
has no entry called 'forced_codes'... make the description again",
where a version 5 document yields the sentence naming every option to
bring back. The route is to describe the table once more. **This
suspension does not reach section 4.6's reserved slots**, whose filling
is a structural change and advances the version whenever it happens.

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
| **raw identity** | a present cell's text exactly as the file spells it. `n_distinct` counts raw identities — except on the four roles that publish a level list, where it counts the spellings the block SPEAKS OF (plan P4-D276): the difference between it and a level's `variants` census counted the spellings the absorption took away, and while that absorption reached one-row spellings alone the difference was a count of one |
| **folded identity** | a present cell's text after trimming and a Unicode `casefold()`. `n_distinct_folded` counts folded identities, and every published label is a folded identity |
| **the floor** | `settings.small_cell_floor`, the smallest number of rows a published group may cover. Its value is in the document and the document is the only place it is fixed: it is at least 1, and 11 is what `synthtwin profile` writes when nobody asks for another (owner, 2026-09-22; plan P4-D316). The settings section states the range, and what each floor gives up |
| **withheld** | held back by the floor and pooled into a counted remainder, never named |
| **the ladder** | the fixed eleven rungs `min`, `p01`, `p05`, `p10`, `p25`, `p50`, `p75`, `p90`, `p95`, `p99`, `max`, in that order |

**Equality per path** (plan P2-D6). `n_distinct` counts RAW present
spellings — except on the four roles that publish a level list, and on
a compound column's label half, where it counts the spellings the block
SPEAKS OF (plan P4-D276), so that the absorption of a spelling below the
floor leaves no residual to subtract; and a compound column's OWN
`n_distinct` is its two halves' counts added, `n_numeric_distinct +
labels.n_distinct`, for the same reason (the carried numbers pass of
2026-09-18: left raw, it published one more than that sum wherever the
label half absorbed a spelling, and section 7.14 refuses exactly that). `n_distinct_folded` counts FOLDED
identities. Numeric
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
| **a nothing-publishing column** | a column whose publication class permits no value of the table anywhere in its block: `role` in `numeric_unrepresentable`, `identifier` or `free_text`, or `structural_role` `identifier` whatever the role. The term is BINARY — a column either is one or is not — and the role `empty` does not by itself make a column one. It bars the TABLE's text and not this format's own: such a column still names which members of the published vocabulary its absent cells were spelled with (C6-126) | C6-50, C6-51, C6-52, C6-126 |
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
  (invariant B8), a multiplicity map may be `{}` (section 5.3),
  `fraction_widths` is the empty object in case P5.b, `pad_widths`
  is the empty object in the same case of its own (C6-30b),
  `field_widths` is the empty object on a column no cell of which was
  written as a whole number (C6-30c), and
  `shape_forms` is the empty object on every column no form of which
  was shared by enough cells to name — which is every column of prose
  (C6-31c);
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
denotes.** Three of this contract's mappings key themselves on the
figures of a whole number, and THEY DO NOT ALL READ THE SAME WAY, so
none may be inferred from another:

- `fraction_widths` writes its width keys BARE — no sign, no leading
  zero unless the width is itself zero, no space, no other character
  (C6-29) — so its code point order is not a numeric order. Under the
  code point order `(withheld)` precedes every digit, `1` precedes
  `10`, and `10` precedes `2`; so a `fraction_widths` object carrying
  the widths `0`, `1`, `2` and `10` and a pooled remainder is written
  in the order `(withheld)`, `0`, `1`, `10`, `2`, and any other order
  is a document section 10.4 refuses.
- `pad_widths` writes its width keys by the SAME grammar and reads the
  same way (C6-29 governs both), and it would be a poor joke for the
  census of padding to write a padded key. A `pad_widths` object
  carrying the widths `2`, `5` and `10` is written in the order `10`,
  `2`, `5`.
- `field_widths` writes its width keys by that same grammar and in that
  same order (C6-29 governs all three censuses), the narrowest width it
  can name being `1` rather than `2` (C6-29c).
- `kurtosis` is the moment ratio and NOT the excess, so a normal curve
  reads 3 here and not 0. That is the same measure `skew` beside it
  uses -- both are the plain moment statistics -- and a reader who
  wants the excess subtracts three. It is `null` where fewer than four
  values were used or where every value used is the same one, and
  invariant Q16 holds it between 1 and `n - 2 + 1/(n - 1)`, which is
  where every sample of `n` values lies whatever the values are.
- `percentiles_between` holds the ninety percents `percentiles` does
  not name, so the two together are the hundred and one rungs from 0 to
  100. It is ONE FACT: no rung of it has a subcheck of its own, and no
  file is held to any of them. What invariant Q19 requires is the shape
  a consumer relies on — the keys are exactly those ninety, each entry
  is a number or null, and **the hundred and one rungs of the named
  ladder and this one together never go down**. That last clause is the one that matters:
  checking the ninety alone would let a finer rung sit outside the
  named pair it lies between, and a generator interpolating that ladder
  would then place a value outside two rungs the description publishes
  as exact.

  What it buys is not a check but FIDELITY. An eleven-rung ladder says
  nothing about how many values lie inside a gap between two rungs, so
  a twin drawn from one puts too few where the real column crowded
  them. Measured on 400-row columns with a threshold at 1000: where the
  threshold fell mid-gap the eleven-rung twin was thirty-nine cells out
  of the count below it, a tenth of the column, and the finer twin was
  exact.
- `mode` and `mode_count` are the number this column held most often
  and how many cells held the commonest number. They are published
  TOGETHER or not at all, which invariant Q18 enforces: a value with no
  count says a number dominated without saying by how much, and a count
  with no value says it without saying which. Two rules bound them.
  The **tie rule**: where several numbers share the largest count, the
  SMALLEST of them is the mode — deterministic, and naming no value the
  ladder does not already publish one of. The **floor rule**: the pair
  is published only where the count clears the small-cell floor AND
  reaches two, because a mode held by one cell is not a mode at all —
  every value ties there, and the tie rule would publish the column's
  smallest number under a name saying it dominates. Identity is the
  canonical triple, as for `n_distinct_values` below: two spellings of
  one number are one value here. The pair stays REPORT-ONLY, and the
  generator reads `mode_count` as a CEILING: generation method G5.2a
  holds every stratum of the twin at or under it (landing 2b.1).
- `n_distinct_values` counts NUMBERS where `n_distinct` beside it
  counts SPELLINGS, and the difference is the whole reason it exists.
  `1` and `01` are two spellings and one number, so the two keys can
  differ on any column whose values wear more than one form, and a
  consumer reading `n_distinct` as a count of values is reading the
  wrong key. Two spellings denote the same number exactly when the
  canonical triple `sign * digits * 10 ** power` — the digits stripped
  of both leading and trailing zeros — is equal, which is the same rule
  section 7.5 states for comparing a declared value with a cell.
- `value_histogram` writes BIN NUMBERS by that same grammar and in that
  same order. Its keys are bin numbers and not widths: the method
  divides the range between a column's published `min` and `max` into a
  fixed number of equal bins, and each key says how many of the values
  the statistics used fall in that bin. The bins ascend with the values
  they hold, which is what lets a consumer read the object as a shape;
  **this census is all or nothing**: where any bin holds fewer cells
  than the publication floor, the column publishes no histogram at all
  rather than a partial one. A field-width census with a pooled
  remainder still says something a consumer can use, because a cell can
  be written at a named width whatever the pooled ones do; a histogram
  is read by RANK, and a remainder does not say which bins its values
  are in. Where the object is present its counts account for every
  value the statistics used and for no more.
- `empty_bins` writes bin numbers TOO, and writes them as NUMBERS in a
  list rather than as keys of a mapping. The bins are the same ones,
  measured between the same two published ends; what the list names is
  the bins holding NONE of the column's values, ascending, each named
  once. There is no count beside a bin here and there could not be:
  the count is nought, and a nought standing where every other entry
  of this format stands for a cell somebody's table holds would be a
  reader's trap rather than a fact. **This is the one fact of a
  numeric block the publication floor does not reach**, and 7.11 says
  why: the floor exists to keep a group too small to name from being
  named, and there is no group smaller than nobody.
- `empty_edges` writes PAIRS of values, one for each run of those
  empty bins: the two numbers the run really lies between. They are
  values and not bin numbers, written as numbers, and 7.11a says why
  the key exists beside `empty_bins` rather than instead of it. The
  floor does not reach it either, for the same reason and for one
  more: a pair names two values and not a group.
- a multiplicity map — `n_distinct_by_occurrences` and
  `variants_withheld` — pads its row-count keys with leading zeros to a
  uniform width, and section 5.3, which states that key form, gives
  THIS RULE as the reason for it: padded, the canonical sorted-key
  order and the numeric order coincide, where written bare `10` would
  sort before `2`. Section 5.3 fixes the form; this clause only records
  why the form is shaped that way, and a producer that writes an
  unpadded multiplicity key writes a document section 10.4 refuses.

**`shape_forms` is the one census keyed on TEXT, and it needs no rule
of its own.** Its keys are written forms — `@%%.%`, `%%%%-%` — not the
figures of a number, so the code point order is the only order there
is and the paragraph above does not reach it. It is named here so that
a reader counting this format's censuses does not go looking for a
fourth numeric key grammar. Under the code point order `(withheld)`
precedes every form, because `(` is below every figure and letter.

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
`fraction_widths`, `pad_widths` and `field_widths` — each a key of the
block, a sibling of `numeric_styles` — `shape_forms`, a key of the block on the five
roles that carry it, `resolution_mix`, `datetime_separators`, `all_at_midnight`, `min_length`, `max_length`, the `(date-sentinel)` key
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

`source` is an object with exactly these seven keys and no others.

| key | JSON type | permitted values | meaning | disposition |
|---|---|---|---|---|
| `dialect` | object | section 4.3a | how the table's file is written: its delimiter, quoting, line endings and the lines that are not records | EXACT-CONTROL |
| `encoding` | string | `utf-8-sig`, `latin-1`, `cp1252`, `utf-16-le`, `utf-16-be` | the encoding that read the table, which the twin is written in | REPORT-ONLY |
| `used_fallback_encoding` | boolean | — | true when the fallback rather than the primary encoding read the file | REPORT-ONLY |
| `workbook` | `null` or object | section 4.3b | how a spreadsheet workbook holds the table, or `null` where the file was delimited text | EXACT-CONTROL |
| `header_source` | string | `file`, `generated` | `file`: the column names came from the table's first row. `generated`: the names are synthtwin's own — the person said the first row was a record, or the first row could not be TOLD from a record (the owner's ruling of 2026-09-17, item 8; plan P4-D232) — and the columns are named `column_1`, `column_2`, … | EXACT-CONTROL |
| `header_by_convention` | boolean | — | true when the first row was taken as names because nothing in the file said otherwise, rather than because the file showed it | REPORT-ONLY, with a required sentence |
| `header_evidence` | string | any non-empty text | the header verdict in one plain sentence | REPORT-ONLY, with a required sentence |

**Membership rule.** All seven keys are REQUIRED. No other key may
appear under `source`.

**Invariant S5.** `used_fallback_encoding` is true exactly when
`encoding` is `latin-1` or `cp1252`.

**Invariant S6.** `header_by_convention` may be true only when
`header_source` is `file`. Generated names are not a convention about
somebody's first record; they are names synthtwin made.

**The required sentence.** When `header_by_convention` is true, the
generation report MUST say, in plain words, that the twin's column
names may in fact be a first data row of the real table rather than
names — not merely that a header was written. Phase 1's R1 residual is
exactly this uncertainty, and a report that says only "a header was
written" hides a warning the profile is carrying (plan P2-D6).

**AND WHERE THE FIRST ROW COULD NOT BE TOLD FROM A RECORD** (the
owner's ruling of 2026-09-17, item 8; plan P4-D232). Three shapes of
file settle nothing about their first row and are answered the same
way: one whose every first-row value reads as a number, one whose
values below show the first row to be a record, and one where a line
that is not a record — a title, a comment, a row of one cell in a
workbook — stands above the row the reader would take as names, while
no column of the file shows that row to be names. In each,
`header_source` is `generated`, `header_by_convention` is false, the
columns are named `column_1`, `column_2` and so on, EVERY row of the
file is described including that one, and `header_evidence` is the
enumerated sentence `taxonomy.HEADER_NAMES_NOT_TOLD`, which quotes no
cell. The questions file puts the question, and `--first-row names`
publishes the real names. The two refusals that stood here until then —
"the first row does not look like column names" and "synthtwin cannot
tell whether the first row holds the names" — are withdrawn: the
reading taken is the one that publishes nothing of a row that may be
somebody's data, and the question reaches the person where every other
question about their file does.

**Neither shape is settled by ONE cell.** The second shape reads a
record made of structured text by its silhouette, and it used to demand
that EVERY value below the first row wear that silhouette; so writing
one identifier of 239 in a second system's layout, which the owner's
seventh ruling says a file may hold, or leaving it `NA`, left the rule
silent and published the whole first record as the column names with
the table one row short. The first row's silhouette must now be worn by
TWO or more of the non-empty values below it, and a minority layout or a
missing-value word is counted and beaten rather than obeyed. Asking that
it be the COMMONEST below moved the threshold rather than removing it:
measured at a floor of eleven on the same 239 records, 119 identifiers
reading `NA` was caught and 120 was not, and at 120 the whole record was
published as the three column names with nothing asked (plan P4-D280).
Two rows wearing the first row's layout say it is one of a population,
however many wear another. A first record whose layout NO row below
repeats is still read as names, and widening the rule to any structured
silhouette recurring below costs an ordinary headed table its real
names; that is left with the owner. The third shape is waived only by an autofilter
whose range begins at the header row, and never by a frozen pane (plan
P4-D281): a freeze says where the scrolling stops, it falls where the
person dragged it, and counting it turned a `<pane ySplit="2"/>` on an
otherwise ambiguous sheet into a licence to publish both of that row's
values as column names.

**Why the furniture rule is asked AFTER the file's own evidence.** A
title over a real header is the commonest shape a spreadsheet exports.
Where a column below the header holds numbers while the header's own
value does not, the file SHOWS the row is names, and that reading
stands. Asked the other way round, `Extract for unit 7` over
`record_id,age,arm,site,reading` read as a headerless table, the header
row became a value of every column, and the twin failed its own
description at exit 3.

### 4.3a EXACT-CONTROL: `source.dialect`, the table's written form

Owner ruling 2026-09-15, plan P4-D86: the twin is written the way its
source file was. `dialect` is an object with exactly these twenty-two keys,
all REQUIRED; the loader is the executable statement of every rule
below (`contract._dialect_block`, `contract._dialect_rules`).

| key | JSON type | permitted values | meaning |
|---|---|---|---|
| `blank_lines` | array of objects `{after, lines, text}` | at most 64 | blank lines standing after `after` data records, `lines` of them, each holding `text` (nothing, or only spaces and tabs); empty where `blank_lines_spread` is not `null`, and empty where the places number fewer than the census line, max(2, `small_cell_floor`), because a place is a RECORD POSITION and a handful of them are a handful of records (plan P4-D290: one blank line after record 57 of 120 published `{after: 57, lines: 1}`). The census line is the floor itself at the default of 11 and at every floor of two or more; at a floor of one, which a person has to ask for and at which the column censuses beside this one publish a level covering one row, the line is not asked and the file's form is kept exactly as the source wrote it (P4-D290 as amended 2026-09-18). The loader asks the same line (FD4, plan P4-D317), so a hand-edited description publishing fewer places than it is refused. A place also publishes a FORM -- how many lines stood there and what each holds -- and a form worn by fewer places than that same line is published as the COMMONEST form instead, a tie going to the form standing earliest in the file (plan P4-D311, ruling 6 of 2026-09-17 read on a file's own blank lines: eleven ordinary blank lines beside one holding a single space after record 57 published `{after: 57, lines: 1, text: " "}`, naming the sole record beside that spelling, and eleven runs of one beside three lines after record 57 published `{after: 57, lines: 3}` the same way). The lines a published place does not keep -- those of a withheld place, and the difference where a run was absorbed into a longer or a shorter one -- leave `line_endings` with them, which then collapses to one run, because FD2 has the endings account for every line the description keeps. WHAT THAT COSTS THE CHECK, STATED (plan P4-D314): `synthtwin validate` reads the checked file by this same rule, so the two sides of `bytes.blank-lines` meet AFTER the absorption and a file differing from the description only in a rare blank line's spelling or run length is reported HELD -- measured at a floor of eleven on twelve ordinary places, where a twelfth holding one space, a tab or three lines was MISSED at exit 3 before P4-D311 and is HELD at exit 0 after it, while a place that MOVES is still MISSED. The obligation cannot see what this field is forbidden to publish; the check's own sentence says so, on both sides, wherever the floor is above one |
| `blank_lines_spread` | `null` or object `{first, last, lines, text}` | more than 64 `lines` | past the cap of 64 places, the blank lines counted in their place: `lines` of them in all, the first after `first` data records and the last after `last`, `text` what the most of them hold; the twin writes them evenly between those two places, the k-th of n after `first + k * (last - first) // (n - 1)` records. Published only where the places number at least the census line, as `blank_lines` is, so `lines` reaches that line too, and the loader refuses a count below it (FD4, plan P4-D317) |
| `byte_order_mark` | boolean | — | a byte-order mark leads the file |
| `columns` | array of objects `{pad, quoting, sequence_start}` | one per column | `quoting`: one rule per cell class `absent`, `empty`, `number`, `text` — `needed`, `bare`, `always`, `mixed`; `pad`: `null` or `{side: left or right, width}`; `sequence_start`: `null`, `0` or `1` for a column holding the row sequence — published ONLY for a first column named as a written row index is (`Unnamed: 0`, `rownames`), never for a column declared with `--identifier`, and never for a column with an absent cell (FD12, plan P4-D76) |
| `delimiter` | string | `,` `;` tab `\|` | the field delimiter |
| `empty_rows` | object `{interior, leading, trailing}` | whole numbers | records holding nothing in every cell, where they stand. A cell holding nothing but spaces and tabs holds NOTHING here, which is what the column's own description counts absent and what the twin writes empty (plan P4-D84, review item CODEX-7); counting it as something published no such record for a file of ninety ` , ` records whose twin held ninety, and the twin then missed `bytes.empty-rows` against its own description. Only the counts are published, never which rows they are, and a count below the census line, max(2, `small_cell_floor`), is published as NOUGHT (plan P4-D290, ruling 4 of 2026-09-17: an empty row is a record of the table, and replacing record 57 of 120 with a bare comma published `interior 1`). The line is the floor itself at the default of 11 and at every floor of two or more, and is not asked at a floor of one, at which the column censuses beside it publish a level covering one row (the amendment of 2026-09-18). The loader asks the same line of each of the three counts (FD5, plan P4-D317) |
| `end_of_file_mark` | boolean | — | a Ctrl-Z byte follows the last line |
| `escape` | string | `doubled`, `backslash` | how a quote character is written inside a quoted field |
| `final_line_ending` | boolean | — | the last line ends with a line ending |
| `header_quoting` | string | a quoting rule | how the header's cells are quoted |
| `header_rows` | array of arrays of strings | none, or two | the rows under the column names that DESCRIBE those columns, one cell per column, published only where the person declared them with `--metadata-rows` or in the questions file (`settings.forced_metadata_rows`, FD9, plan P4-D81). Undeclared, such rows are records of the table and are described as data |
| `header_rows_quoting` | string | a quoting rule | how those rows' cells are quoted |
| `initial_space` | boolean | — | one space follows every delimiter (`"a", "b"`) |
| `line_endings` | array of objects `{ending, lines}` | `lf`, `crlf`, `cr`, `crcrlf`; at most 64 | the line endings of every line in file order, as runs; empty where `line_endings_spread` is not. Where any ending is written by fewer lines than max(2, `small_cell_floor`), OR ANY RUN IS SHORTER THAN THAT, the whole file is published as ONE run of the commonest ending (plan P4-D290, ruling 6 of 2026-09-17 read on a file's own spelling): the runs together say exactly where each ending changed, so changing record 57's ending alone to CRLF published `[{lf: 57}, {crlf: 1}, {lf: 63}]`, which is that record's position, and giving lines 0 to 20 CRLF endings as well left the run of ONE standing until the RUNS were read too (amended 2026-09-18). Both tests are asked at the census line, which is the floor itself at the default of 11 and at every floor of two or more, and neither is asked at a floor of one. AND BOTH ARE ASKED OF THE RECORDS' OWN ENDINGS TOO, once the lines the description publishes above the table -- the separator hint, the preamble's runs, the header, the rows of column descriptions -- are taken off the front (round 2 of the review, the disclosure pass, item 7): ten title lines, a header and record 1 written with a bare newline against 119 records written with a carriage return and a newline published `[{lf: 12}, {crlf: 119}]`, and 12 less 11 is that one record |
| `line_endings_spread` | array of objects `{ending, lines}` | two or more endings, in the order above | past the cap of 64 runs, how many lines end each way, in place of the runs; the twin ends every line with the commonest ending (the earlier on a tie) except the rarer ones' lines, each rarer ending taking its c lines at the middles of c equal stretches of the file, the next free line where one is taken |
| `preamble` | array of objects `{kind, lines, mark}` | at most 16 runs | the lines before the header or first record, as RUNS OF ONE SHAPE and never as their text. `kind` is `blank`, `comment` or `text`; `lines` is how many such lines stand together; `mark` is the punctuation a comment line began with (`# `) or the spaces and tabs a blank line held, and is empty for a line of text; it holds no quote character and not the table's own delimiter, because the twin writes it and the line the twin writes has to stay one record (plan P4-D83). NO TEXT of such a line is published at any smallest group, a floor of one included (plan P4-D80). The twin writes a neutral line of the same shape in each one's place |
| `preamble_withheld` | boolean | — | one of those lines held text, so the twin carries a stand-in of the same shape rather than the line. True exactly when some run's `kind` is not `blank` |
| `row_order` | `null` or object `{collation, column, direction}` | `number`, `text`, `decimal_comma`; `ascending`, `descending` | the leftmost column the rows are sorted by, and the grammar its cells are read under. `decimal_comma` is published only for a column named in `settings.forced_decimal_commas`: such a column writes `0,5` and `10,0`, which the ordinary number grammar reads as no number at all, so the column fell to `text` — where `10,0` sorts before `9,9` — and a table genuinely sorted by it published no order, or one its twin then wrote out of order (review item CODEX-9). The grammar is published here rather than left to be re-derived, so the generator and the validator both read it off the description instead of being told the declaration a second time |
| `separator_line` | boolean | — | an Excel `sep=` line comes first |
| `short_rows` | boolean | — | records leave out their trailing empty cells |
| `trailing_delimiter` | object `{header, rows}` | booleans | a delimiter ends the header line, each record |
| `written_names` | array of objects `{position, text}` | — | header cells written other than their column's name: blank or repeated, named `Unnamed: N` (N counted from 0) or with `.1`, `.2` after them |

**Invariants FD1-FD13** (`contract.INVARIANTS`): FD1 one column form per
column; FD2 the line endings account for every line the file holds, in
runs that each end their lines one way, or past the cap on runs and in
their place as counts of two or more endings in listed order, and no ending's total, no run's length and neither of those over the records alone falls under the census line -- the smallest group size and never under two, not asked at a floor of one; FD3 a mark only on UTF-8 or
UTF-16, and always on UTF-16; FD4 blank lines in file order, within the
table, spaces and tabs only, and in a one-column table only after its
last record, within their caps, and blank lines published counted only
past that cap, in place of places, within the table, in two or more
columns, and the places, the places wearing each form of them and the
lines counted in their place each reaching the census line (plan
P4-D317); FD5 records holding nothing only in a table of two or more
columns with no row sequence, no more than any column's absent cells,
and each of their three counts nought or at the census line (plan
P4-D317); FD6 a row-sequence column has every
cell present; FD7 the sort column is a column, not the row sequence, holding no
empty cell and no absent cell the twin writes empty outside the records
holding nothing, in three or more rows (the order is read over the
records that hold something, and the twin sorts those around its
records of nothing). The cells the twin writes empty are counted the way
the generator decides them: the column's absent cells less the
`missing_by_source` spellings it reproduces, which is every one of them,
a spelling a judged pass put there included (C6-115, C6-116). They were counted as the
blank and pooled cells with the judged ones added, which missed every
absent cell no field names -- a free-text column's `--missing-value`
cells -- and a twin then missed `rows.order` (plan P4-D173); FD8 written header cells stand
under a header read from the file, in order, and name every column what
the description names it; FD9 rows of column descriptions only under
such a header, exactly as many of them as the person declared and no
more than two, each as wide as the table; FD10 only a header read from the file
carries a trailing delimiter or a quoting rule, and rows do not both
carry a trailing delimiter and leave out empty cells; FD11 the lines
before the table are published as runs of one shape, within the cap,
each with a mark holding no line break, no quote character, not the
table's own delimiter and no text of the line, each
the shape the line the twin writes for it is read back as, and recorded
as withheld exactly when one of them held text; FD12 a column declared to hold record numbers
publishes no row sequence and is not the column the rows are sorted
by, and a row sequence is published only for a first column named as
a written row index is; FD13 a delimiter the person declared
(`settings.forced_delimiter`, plan P4-D110) is the delimiter the
written form publishes, and a workbook carries no such declaration.

**What it discloses.** Every key describes the file's writer, not a
person, except one: the metadata rows, which are column-level text,
reach a description only where the person DECLARED them and are then
published like names (4.4, plan P4-D81).

A LINE BEFORE THE TABLE IS NEVER PUBLISHED AS TEXT, AT ANY SMALLEST
GROUP (plan P4-D80). Such a line is free text somebody wrote above
their table -- `Extract for unit 7`, `# exported for Dr Vance` -- and
the twin definition's third clause says the description reveals nothing
about any individual. The rule this replaced published the line whole
at a smallest group of one, which was this version's DEFAULT until
2026-09-22: a floor governs how many rows share a value, and one line of prose is not a
group of rows at all, so the floor was never a defence for it. Review
item CODEX-3 measured a person's name travelling through that branch
into the description and into the twin.

What a description carries instead is that such lines exist, how many
there are, and the SHAPE of each run of them: blank, a comment and the
mark it began with, or a line of text. Every one of those is a fact
about the tool that wrote the file. The twin writes
`dialect.preamble_line` for each -- a blank line stays blank and keeps
its spaces, a comment keeps its mark and reads `# withheld line`, a
line of text reads `withheld line` -- so a reader that skips a title
line, and code that passes `comment="#"`, skip as many lines in the
twin as in the table. The loader's half of the rule is that the line
the twin would write is read back as the very shape published, which
is what makes a mark carrying a word impossible rather than merely
unusual; the producer's half is `profile._PREAMBLE_MARK`, which
refuses a mark holding any letter or digit.

**AND THE MARK HOLDS NOTHING THE TWIN COULD NOT WRITE** (plan P4-D83).
The mark is written into the twin ahead of the stand-in, so a mark
carrying a quote character or the table's own delimiter leaves a twin
that is not a file. Measured on the repair itself: a title line written
`"Extract for unit 7"` gave the mark `"`, the twin's first line was
written `"withheld line` -- a quoted field nothing closes -- the twin
missed about 120 obligations of the description that asked for it, and
`synthtwin profile` refused to read the twin at all, where the same
bytes were twinned cleanly before lines before a table were withheld at
all. The delimiter breaks it the other way, cutting the stand-in into
fields a reader takes for the table's header. So `dialect.preamble_shape`
ends the mark before the first such character -- a line whose
punctuation begins with one is a line of TEXT, whose stand-in is the two
neutral words -- and FD11 refuses a description carrying one, against
the form's own delimiter.

**THE LIMIT OF THIS RULE, STATED** (review item MAJOR-2 of the 2b.11
review). It reaches only the lines synthtwin READS as standing before
the table: a blank line, a line beginning `#`, and a line of one field
holding a space. A title line that holds the delimiter -- `Extract for
Dr Vance, unit 7` above a two-column table -- reads as a row of cells
of the table's own width, so it is taken for the header and its words
are published as the column names and written into the twin, and the
row count is one too high. Column names ARE published as written, by
S4 and by 4.4: the twin's header line has to carry them. What synthtwin
owes such a person is to say so, and the summary's paragraph about the
first row says it -- that the names were assumed, that what that row
holds is published as written, and that `--first-row data` is the way
to say the row is a record. Recognising such a line as a title instead
would take the first row of every table whose header cells hold spaces
-- `Gewicht, kg` -- out of the description, so this version tells
rather than guesses.

**S4 still holds of the names.** A blank or repeated header cell is not a
name: the column is named by the rule in `written_names` above, which
yields names that are non-empty and pairwise distinct, and the cell as
written stands in `written_names` to be written back.

### 4.3b EXACT-CONTROL: `source.workbook`, how a workbook holds the table

Plan P4-D77, extended by P4-D79. `null` where the table was read from
delimited text. Otherwise an object with exactly these sixteen keys, all
REQUIRED; the loader is the executable statement of every rule below
(`contract._workbook_block`, `contract._workbook_rules`).

**This block is an OBLIGATION, not only a record** (plan P4-D79). A
workbook's twin is a workbook, so every fact here is a promise the twin
has to keep and the validator measures each one, under subchecks named
`workbook.*` filed against this fact. The validation method states the
rule and what it does and does not withhold on a workbook.

| key | JSON type | permitted values | meaning |
|---|---|---|---|
| `autofilter` | boolean | — | the sheet or its defined table carries a filter |
| `columns` | array of objects `{cell_classes, format_code, format_kinds, formulas, value_class}` | one per column | the census of what each column's cells WERE, below |
| `date_system` | string | `1900`, `1904` | which epoch the workbook counts its dates from; the 1904 system shifts every date by 1,462 days |
| `defined_names` | integer | ≥ 0 | how many defined names the workbook carries |
| `defined_table` | boolean | — | the sheet carries a defined table |
| `empty_rows_inside` | integer or `null` | ≥ 0, or `null` where the disclosure rule held it back | records holding nothing in every cell, standing inside the table. This counts ROWS OF THE TABLE, so it is held exactly as a census is (WB3, plan P4-D164): published where it is every record or reaches the line at both ends, and `null` otherwise -- a nought included, so that a withheld count is never told from a real nought |
| `frozen_rows` | integer | ≥ 0 | how many rows are FROZEN at the top of the sheet, bounded by the worksheet's own last row and never by the rows the table fills (WB4, plan P4-D288). The split is held ONE ROW INSIDE that last row, because the split's top-left cell is the row below it: a pane freezing every row of the sheet spells `A1048577`, which no spreadsheet has, so the reader reads such a pane as the largest split a sheet can spell and WB4 refuses a description claiming more. A pane that is SPLIT rather than frozen freezes none, and its `ySplit` is a distance rather than a count of rows: a split at `3000` was published as three thousand frozen rows and the loader then refused the workbook's own description (plan P4-D169). **A freeze is not evidence about which row holds the NAMES** (plan P4-D281): the reader waives the first-row question of the owner's ruling 8 only for an autofilter whose range BEGINS at the header row, because a freeze is a viewing convenience that falls where the person dragged it, and counting it published a row that ruling 8 protects as the column names |
| `macro_project` | boolean | — | the workbook carries a macro project. It is never read and never copied; the report names it |
| `rows_above_header` | integer | ≥ 0 | rows standing above the header — a title, a merged banner, a note, and the blank rows between. The header is the first row of content holding two cells or more, or the one row a table one column wide begins with, or the written row index (one cell short, missing its first); a title above a table holds one. Where rows of one cell stand above that header and the sheet neither freezes its panes nor starts its autofilter at the header row, each is asked what a delimited file's line of one field is asked (`dialect.lone_field_leads_a_table`, plan P4-D186, which withdraws P4-D174's question): a cell of text that is empty, holds a space or begins with `#` is furniture and counted here, never published as text, and the first such row that is not -- one word, one number -- holds the names, which then meet the same first-row question a delimited header does; `--first-row names` puts the names on the first row of content (plan P4-D174). `0` where the person declared with `--first-row data` that every row is a record (plan P4-D165) |
| `sheet_count` | integer | ≥ 1 | how many sheets the workbook has |
| `sheet_extents` | array of object-or-`null` | one per sheet, in workbook order | the block of cells each sheet that is NOT the table's holds, as `{rows, columns}` counted from the first cell, and `null` for the sheet the table was read from, whose own facts describe it. A sheet holding nothing is `0` by `0`, and no block reaches two rows, however few columns (WB7, plan P4-D170). The twin writes a sheet of that shape carrying one word of synthtwin's own in every cell |
| `sheet_hidden` | boolean | — | the sheet the table was read from is hidden |
| `sheet_names` | array of string-or-`null` | one per sheet, in workbook order | each sheet's name where it may be published, `null` where it was WITHHELD. A name may be published only when it is one this version would publish itself -- one of `dialect.SHEET_SAFE_NAMES`, optionally followed by ONE OR TWO figures not beginning with a nought -- because a sheet name can hold a person's name, and a longer run of figures can be a subject's number (`Report123456789` was published whole until plan P4-D171). No two published names are one name in any case. A withheld sheet is written under a neutral name no published name takes in any case |
| `sheet_position` | integer | ≥ 1 | WHICH sheet the table was read from, by its place in workbook order |
| `trailing_blank_columns` | integer | ≥ 0 | columns of formatted blanks standing beyond the table |
| `trailing_blank_rows` | integer | ≥ 0 | rows of formatted blanks standing below the table |

**A column's census — exactly five keys.** `format_code` is the number
format the column's twin WEARS: one of `dialect.SHEET_FORMAT_CODES`,
which is Excel's own built-in vocabulary plus one canonical code per
kind, or a code built of the number format language's own tokens alone
(`dialect.sheet_format_code_speakable`: figure placeholders, the date
and clock letters, `AM/PM`, a colour or elapsed bracket, escaped and
quoted punctuation, at most four sections and sixty-four characters),
published as the source wrote it (plan P4-D189, WB6) -- `00000` and
`yyyy-mm-dd hh:mm` are published as written, `0.0" kg"` and
`[$USD-409]#,##0.00` as the canonical code of their kind; it is the commonest
code AMONG THE CELLS HOLDING A VALUE where that code is worn by the line,
else the canonical code of the commonest kind among them where that kind
is worn by the line, else the general format (plan P4-D164). **A column
whose value-holding cells wear TWO codes of one kind, neither of them the
general format, each worn by the
line, is REFUSED rather than described** (`workbook.mixed_number_formats`,
plan P4-D283), for the reason `mixed_storage` refuses a mix of kinds one
level up: the column carries one code here, so the twin would put the
commoner of the two on every cell. Measured at a floor of five on 120
cells, sixty written `0%` and sixty `0.0`: the description published
`0%`, the twin wore it 120 times, and both files validated with nothing
missed while sixty values a person reads as `0.5` read as `50%` off the
twin. A code worn by FEWER cells than the line is not a second
population and is counted into the commonest, which is the owner's sixth
ruling of 2026-09-17. NEITHER IS THE GENERAL FORMAT A SECOND POPULATION:
it is what a cell wears when nobody gave it a format, and it is also the
code this rule falls back to when nothing else reaches the line, so a
column somebody formatted part of the range of is read rather than
refused. Measured at a floor of five on 120 numeric cells, sixty
carrying no style at all beside sixty carrying `0.00`: read at exit 0,
publishing `0.00`, and its twin wears `0.00` on all 120 cells -- which is
what such a column loses here, and is what `c5d09d5` did with it.
Publishing a census of codes is the repair that
would keep such a column; until a description can carry one, the column
is declined by name (principle 5). `cell_classes`
counts the class of every cell of that column, over the closed set
`absent`, `blank`, `empty`, `text`, `number`, `boolean`, `error`, `date`
(`workbook.CELL_CLASSES`), counting a cell holding a value whose spelling
the column reads as absent and does not reproduce -- a spelling under the
floor -- as `absent`, the class
its twin writes it as (plan P4-D174); `date` is a cell the file stores as ISO date
text (`t="d"`), which every reader hands back as a date and which used to
be counted a number and written back as text (plan P4-D168); the twin
writes such a cell back as ISO date text and converts to the day count a
workbook stores only the cells it is to store as NUMBERS, which is
settled from this census before the conversion and not after it (plan
P4-D284) -- asked the other way round, the ISO spelling was gone before
anything could fit the `date` class and 120 date cells came back as the
strings `"45315"`. `empty` is a cell present in the sheet holding the
empty string, which an inline string element spells `<is><t></t></is>`
as readily as a shared string does (plan P4-D285): the element's
PRESENCE is what tells it from `blank`, the styled cell holding no value
at all, and reading the element's emptiness instead published 60 such
cells as blanks whose twin every reader handed back as nothing.
`format_kinds` counts what kind of thing each cell's number format makes
of it, over `plain`, `date`, `datetime`, `time`, `elapsed`, `text`
(`workbook.FORMAT_KINDS`); a colour, a currency and a condition written
in square brackets are not read as tokens of a date, while an elapsed
count (`[h]`, `[mm]`) is (plan P4-D169). `formulas` counts the cells
carrying a formula. `value_class` names the class most of the column's
value-holding cells are -- `error`, `boolean`, `date`, `number` or `text`
-- WITHOUT a count, and is `null` where no class is held by the line; it
is what still tells a twin a column of digit texts from a column of
numbers where the census beside it withheld every count (WB8). Every
count is a whole number, or `null` where the disclosure rule held it
back.

**The disclosure rule every count here keeps** (plan P4-D164,
`dialect.sheet_census`, `dialect.sheet_count`). THE LINE is the smallest
group or two, whichever is larger. A census publishes every count
exactly where none is SMALL -- neither nought nor the whole column, and
under the line or leaving a complement under it. Where one is, every
small count and every nought is withheld together, so a withheld key
never says "some, but few"; and the counts withheld, taken together, are
never under the line and number at least two, the smallest published
count joining them until they are. A census with nothing left published
stands in a table shorter than the line: the row count beside it is all
a reader can subtract from, and it names nobody (plan P4-D174). A single count -- `formulas`,
`empty_rows_inside` -- is published where it is the whole or reaches the
line at both ends, and withheld otherwise, a nought included. A review
measured the rule this replaced: sixty numbers, thirty-nine texts and one
boolean published `60, 39, null` beside noughts at a floor of five, and
100 - 60 - 39 rebuilt the count of one.

**A column whose numbers wear two kinds of format is refused** (plan
P4-D166, `errors.workbook_column_mixes_storage`). The description
publishes how many cells wear each kind, and the column's values as one
distribution -- nothing that says which values were the dates. Where
the column's NUMBER cells wear more than one kind of format (dates
beside plain numbers), the profile is refused and the person told how
to give the column one format. **Numbers stored as text are read**
(plan P4-D187, withdrawing that rule's other half): a text cell holding
figures beside number cells -- thirty numbers of 10 beside thirty texts
of `1000` -- is read as the text cell it is, both counts are published,
and the twin writes the text count spread evenly over the column. Which
values were stored which way is not published, so a calculation over
the numeric cells alone differs between the twin and the table, and the
twin's report says so for every such column.

**A stored number is read without its writer's noise** (plan P4-D174).
A number cell's stored text holding a point or an exponent is read as
the shortest spelling of the same binary64 wherever that spelling needs
fewer significant figures than the stored text, in the same notation --
an exponent keeps its letter, its sign and its count of figures, and a
leading plus stays -- so a trailing nought after a point, which pads a
width and is no noise, is kept (`workbook.stored_number_spelling`, the
one reading of the noise kept at the merge of this repair into the
integration, which had written its own): openpyxl stores 73.1 as `73.09999999999999`
and Excel as `73.099999999999994`, and the figures were published as a
fraction width of fourteen that the person's unchanged workbook then
failed. No other stored text is moved.

**Why the classes are the cell's own and not a reader's.** A workbook
cell is typed, and what a reader shows a person is derived from the
type, the stored number and a format code kept elsewhere. The readers
disagree about nearly every one of those answers: a text cell of
digits comes back as an integer from pandas and as its characters from
openpyxl, and an empty-string cell, an absent cell and a styled blank
are three things in the file and one missing value to pandas. A
description that recorded what a reader made of a cell could not be
written back, so what is recorded is what the file holds.

**A sheet that is not the table's, and the one workbook that is
refused** (plan P4-D82). A twin used to write every other sheet EMPTY,
and a reader then met a different workbook: measured with pandas, the
default sheet of a book whose first sheet is a notes page reads back as
one column and no rows on the real file and as nothing at all on the
twin. The person's own text may not be written back, and cells holding
the empty string change nothing — every reader folds those into a
missing value and trims the frame away again, measured as the same
nothing. So `sheet_extents` publishes how much ROOM each such sheet's
cells take and the twin writes a block of that shape carrying one word
of synthtwin's own, which is the most a twin may hold of a sheet this
description does not describe.

A sheet holding a TABLE cannot be carried that way at all: its values
are somebody's rows, so a twin would hand a reader a frame of withheld
cells where a table stood, and statistics taken from it would be false
while the file still opened. Such a workbook is REFUSED, in a sentence
naming BOTH sheets and saying that each table has to be saved in a
workbook of its own (`errors.workbook_other_sheet_holds_a_table`); a
block of two rows is where that line falls, however many columns it
spans (WB7). It fell at two rows AND two columns until plan P4-D170,
and a sheet holding a header over thirty values in one column was
accepted and written back as a column of withheld words.

That sentence used to ask which sheet held the table and tell the
person to run the command again with `--sheet`, and landing 2b.17's
repair pass measured that the remedy it named is refused too:
whichever of two table-holding sheets is named, the other is then the
sheet holding a table, and the same refusal comes back. Naming a sheet
settles which sheet is DESCRIBED; it cannot settle what the twin would
have to carry on the sheets it does not describe. A message that sends
a person back to the command line for a second refusal is worse than a
plain one, so the sentence now names the only thing that does settle
it.

**The owner's ruling of 2026-09-17, item 3, keeps the refusal and has it
ask again** (plan P4-D203). A workbook with a second table on another
sheet stays refused and WB7 stands; the sentence names the sheet it
found, asks which sheet is the table, and points to
`--sheet` — on a COPY of the workbook with every other sheet that holds
a table deleted or moved to a workbook of its own (the refusal stops at
the first other such sheet, so a workbook may hold more than the two it
names; wording repaired the same day), and it says that naming a
sheet of the workbook as it stands is not enough, which is what the
measurement above showed. The questions file cannot carry this question:
it is written by a `profile` run that described a table, and this
refusal stops the run before any table is described.

**Invariants WB1-WB8** (`contract.INVARIANTS`): WB1 one column census
per column; WB2 the sheet the table was read from is one the workbook
has, counted from one; WB3 every published count of cells, and the count
of records holding nothing, is all of them or reaches the line at both
ends, and a census that withholds a count withholds at least two,
publishes no nought beside them and leaves them together at nought, at
the line or more, or at the whole column where nothing is published, and
a column's count of numbers passes its census's number cells -- the
figures stored as text -- by nought or by the line or more (plan
P4-D197), so that no count, complement or difference a reader can take
names one row; WB4 the records holding nothing inside the
table are no more than the table itself holds, and no more rows are
frozen than a WORKSHEET has -- 1,048,576, and not the rows the
populated table fills, because freezing rows splits the window and a person
may split it below everything they have written (plan P4-D288): a
legal `ySplit="200"` over a header and 120 records was published as
`frozen_rows 200` and then refused by this very rule, with advice to
describe the table again that repeated the refusal for ever; WB5 a workbook names one sheet for every
sheet it has, every name it publishes is one this version would
publish itself, and no two of them are one name in any case; WB6 the
number format a column's twin wears is one of the published codes -- one
of Excel's own, a canonical code, or one of the format language's own
tokens alone (plan P4-D189) -- and its kind, read off the code, is one
the column's own census does not say no cell wears; WB7
a workbook describes the block of cells held by every sheet that is not
the table's and none for the sheet the table was read from, and no such
block reaches two rows; WB8 the class a column names as its commonest is
one its own census does not say no cell holds.

**Which counts the disclosure rule holds, and which it does not.** Every
per-column census, each column's `formulas` and `empty_rows_inside`
count ROWS OF THE TABLE, so each is held by the rule above and published
as `null` where it, its complement or a difference would name one row
(WB3). The layout counts are exempt and each for the same
reason: `rows_above_header`, `trailing_blank_rows`,
`trailing_blank_columns`, `frozen_rows`, `defined_names`, `sheet_count`
and `sheet_position` count the SHEET'S FURNITURE and not its records --
one title row, one frozen row, one column of formatted blanks beyond
the last, one defined name. None of them is a row of anybody's data, so
publishing a count of one names nobody. The earlier wording of this
section and of `workbook.py` claimed every count was floored while five
were published raw; the claim is now the exact list above.

**A published nought and a withheld count are different facts.** A
count of `0` says no cell of that class is in the column; `null` says
the number was not published. Both the writer and the validator read
them apart: the twin never writes a cell of a class published as
nought, and never writes a format code whose kind was withheld, while
a withheld count is one the checked file is not held to at all. The
validation method states which facts of this block a twin cannot be held
to, and why each is withheld rather than measured.

**What it discloses, and what it refuses to.** Every key above
describes the FILE. The facts of a workbook that name or measure one
person are not published at all: not the sheet's own NAME (a sheet or a
title can be somebody's name), not a column width (an autofit width
measures the longest value in that column, so it is a measurement of
one cell), not a comment or its author, not a hidden row, not per-row
styling, not a hyperlink's target, not the document's author or
company, and not any cache of real values. The sheet is published by
its position, the person is told on their own screen which sheet was
read, and a name is published only where this version would have
written that name itself.

**The format code, and why part 1's narrowing was reversed** (plan
P4-D79). Part 1 published the format KIND and withheld the CODE,
because a custom code is text out of the file. That reasoning stands,
and it is also true that a twin cannot be written from the kind alone:
a date is a number wearing a format, so a date column written with no
code comes back from every reader as a column of five-digit numbers. So
a code IS published — but only ever one of `SHEET_FORMAT_CODES`, which
is Excel's own published vocabulary and synthtwin's own, never the
person's. A custom code is published as the CANONICAL code of its kind.
THE LIMIT, unchanged in substance: the twin wears the standard spelling
of a date rather than the one somebody typed.

**What a NUMBER cell reads as** (repair of the stage-2b integration).
Two readings are applied to a number cell before any column rule sees
it, and both are the value's and not the writer's:

- *The stored spelling loses its binary noise.* A workbook stores a
  double, and the characters it stores it under are the writer's
  choice: openpyxl and pandas store 79.1 as `79.09999999999999` and
  Excel as `79.099999999999994`. A stored text holding a point or an
  exponent is read as the shortest spelling of the same double wherever
  that needs fewer significant figures, keeping its notation
  (`workbook.stored_number_spelling`); a text of figures alone is never
  touched, so a whole number past 2**53 keeps the figures stored.
  Measured before: a column of one-decimal values stored at sixteen
  figures published `fraction_widths {1: 233, 14: 119}` and the REAL
  workbook failed its own description.
- *A number wearing a date or datetime format is read as its date*
  (`dialect.sheet_serial_moment`): `YYYY-MM-DD` for a whole day wearing
  a date format, and `YYYY-MM-DD HH:MM:SS` (with `.fff` where the time
  is not a whole second) otherwise, in the workbook's own date system.
  A time or elapsed format is a length of time and stays a number, and
  so does a count no date can be shown for. Measured before: a
  `dd.mm.yyyy` column was described as role `count` with percentiles
  44937 to 45579, a column of moments as `continuous`, and the twin lost
  110 of 1394 moments at midnight. The twin writes each such date back as the day
  count it was read as, wearing a date format (method G2.2).

**A mixture of kinds is reproduced as its counts, not collapsed to the
majority.** `format_kinds` publishes a count per kind and the twin
writes a cell per count; an absent cell is always `plain`, because
nothing is written for it and every reader sees the general format
there.

### 4.4 `settings`

An object with exactly these twenty-two keys. Its whole subtree is
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
| `day_first` | boolean | — | true when the person declared, with `--day-first`, that dates in this table are day-first wherever the day and month are BOTH written as numbers — the slashed pair, the slashed stamp pair, the dotted pair and the two-figure-year pair; false otherwise. Default false. It records that the DECLARATION was made, and not which reading any column took — see below |
| `declaration_matching` | string | exactly `exact_number_when_it_reads_as_one_else_spelling` | the one rule that says which cells a declared value matches: a declared value that reads as a number this format can hold matches every cell holding that EXACT NUMBER, whatever either is spelled like, so `-999` covers a file that writes `-999.00`; any other declared value matches by spelling, after trimming and case folding |
| `declaration_publication` | string | exactly `settings_counts_only_columns_unchanged` | what this block publishes about a declaration and what it does not: counts and synthtwin's own words here, and the columns unchanged |
| `declared_missing_values` | object | exactly the five keys below | the declaration record for `--missing-value` |
| `forced_codes` | array of strings | — | the names the person passed to `--code`, sorted ascending, pairwise distinct. A column named here is read as LABELS: the rules that read a cell as a number, a date, a clock time or a number wearing an affix are silenced for it, so the roles left are the five that publish spellings. Unlike `forced_identifiers` this does NOT suppress the column — its distribution is why it was declared. A name may not appear in both arrays |
| `forced_decimal_commas` | array of strings | — | the names the person passed to `--decimal-comma`, sorted ascending, pairwise distinct. A column named here, AND READ AS PLAIN NUMBERS, has its numbers READ with the comma as the decimal point and the point dropped, so `1,5` is one and a half and `1.234,56` is one thousand two hundred and thirty-four and fifty-six hundredths; and the twin WRITES that column's numbers the same way, because a column declared this way and reproduced with points hands a person cells their own tools read as thousands separators. TWO QUESTIONS LIVE HERE AND THEY HAVE DIFFERENT ANSWERS, which an earlier revision of this row ran together. **Where the declaration is HONOURED** — where the published description differs because it was made — is `affixed_number`, `binary`, `constant`, `continuous`, `count` and `numeric_unrepresentable`. The profiler swaps a declared column's cells BEFORE it chooses a role, so `constant` and `binary`, which are chosen ahead of the numeric roles, read with the comma exactly as the numeric ones do; an earlier revision named only the last three and the tool told those columns' owners their numbers were "NOT read" that way about a description whose profiler had read exactly that way. **Where the GENERATOR must spell the numbers itself** is narrower: the numeric and unrepresentable roles, whose cells it writes as numbers. A `constant` column's twin writes the published spelling straight out, so there is nothing to swap and swapping would corrupt it. **THE AFFIXED ROLE IS HONOURED OVER ITS CORE** (landing 2b.16, plan P4-D106, closing the affixed half of residual R-P4-52). Such a cell is a number wearing one shared piece of text, and the two halves are read differently on purpose: the CORE is read, and written back, in the column's declared grammar, while the WRAPPER is published character for character and is never translated — a wrapper carrying either mark, `U.S.$ ` or a unit written `kg.`, is the file's own text and not a number this tool spelled. Before it, the commonest European export there is — `795,64 EUR`, `37,5 %` — had no substring the splitter's reader could hold, so every cell proposed a wrapper of its own, none reached the parse line, and the column was described as free text and rebuilt as punctuation stand-ins, with `synthtwin validate` reporting exit 0 on both files. Every OTHER role is unhonoured, because its cells carry the number inside a larger spelling — a separator between several numbers, or a label published character for character — and which mark of that spelling is the decimal point is a question this declaration does not answer; on `joined_numbers` the same mark may be the separator itself, and that half of residual R-P4-52 is open. A declaration that lands on such a column is honoured for nothing, and `synthtwin profile` SAYS SO on the screen, naming the column and the role it took; the array still records what was declared, because what a person asked for is part of how the description was made. THIS IS NOT ONE OF THE THREE ROLE DECLARATIONS and does not share their exclusion rule: they are three answers to the question *what does this column hold* and no column may carry two of them, while this answers *how are its numbers spelled*. A column may therefore be named here AND in `forced_measurements` — that pairing is the commonest true thing a person has to say about a European file. It may NOT be named here and in `forced_identifiers` or `forced_codes`: both of those silence the numeric reading, so the declaration would be accepted and then ignored, and a declaration a tool quietly ignores is worse than one it refuses. No heuristic ever adds a name to this array (P4-D26) |
| `forced_delimiter` | string | empty, or one of `,` `;` tab `\|` | THE SIXTH DECLARATION (plan P4-D110, review item CODEX-4): the character the person said separates the columns of their file, with `--delimiter` or by answering `about_your_file` in the questions file, or empty where they said nothing. A declared delimiter is READ and never guessed: the survey takes it in place of the reading the cells favour. It exists because some files read equally well under two delimiters -- `id,pair|code` over rows such as `1,2|3` is two columns under the comma and two different columns under the vertical bar -- and nothing in the cells can say which the person's file is. **The competing readings need not give the table the same NUMBER of columns** (plan P4-D282): a header `id,measure|low|high` over rows such as `1,101|90|110` reads as two whole columns under the comma and three whole columns under the bar, both at a share of 1.0, and while a competitor had to tie on the width as well, the wider reading took such a file silently -- the first field became a QUANTITY, and code using the source's own comma delimiter read a measurement of `029` off a twin row of `3,029|90|110`. The share is what says a candidate reads the whole file; the width may break a tie but may not hide one. Such a file is still READ the way the cells favour where nobody declares, because a file an earlier version twinned may not become refused; the tie is said on the screen and put as a question in the questions file, and the validator reads a checked file with the declaration so that a twin and its source are split the same way. A declaration that contradicts a separator line the file itself carries is refused, and so is one given on a workbook, which has no delimiter. FD13 holds it to `source.dialect.delimiter` |
| `forced_identifiers` | array of strings | — | the names the person passed to `--identifier`, sorted ascending, pairwise distinct |
| `forced_measurements` | array of strings | — | the names the person passed to `--measurement`, sorted ascending, pairwise distinct. A column named here whose cells hold two or more numbers joined by one repeated separator takes the `joined_numbers` role of section 6.15; a column named here whose cells do not are read by the ordinary rules, so the declaration decides nothing on its own. A name may not appear in more than one of the three declaration arrays |
| `forced_metadata_rows` | integer | ≥ 0, and at most 2 rows may be published | THE FIFTH DECLARATION (plan P4-D81), and the only one that is a count rather than a list of names: how many rows immediately under the column names DESCRIBE those columns rather than holding somebody's record. Some survey exports write two — a question wording, then a row of `ImportId` markers. synthtwin RECOGNISES that shape but never acts on it unasked: undeclared, those rows stay in the table and are described as data. Declared, they are taken out of the table and published under `source.dialect.header_rows`, where they are schema text and are published like column names — but only where the file BEARS THE DECLARATION OUT, or the person confirmed it by answering `about_your_file` in the questions file. A `--metadata-rows` typed on a file wearing none of the shape is read and not acted on: the rows stay in the table, the person is told so and asked in the questions file, and answering there is what makes the declaration act (review of landing 2b.17). The reason is the same one the guess was taken out for, read from the other side — measured on an ordinary table of 122 records, `--metadata-rows 2` published two people's records verbatim as the columns' description, exempt from the smallest group, and left the table counted at 120 — and a notice on the screen is no safeguard against it, because by the time it is read the description has been written. So the settings value alone no longer says whether those rows left the table; the published rows say it, and `validate` reads a checked file by them. The guess this replaced took the rows out on its own, so a file it recognised WRONGLY had two real records removed from every count and published verbatim as schema, one of them a person's own row (review item CODEX-2). A declaration that finds no such rows publishes none and is not a refusal: the safe reading is the one where the rows stayed in the table |
| `identifier_minimum_rows` | integer | ≥ 0 | below this many rows nothing is said about a column being all-different, because in a short column almost every measurement is. It decides no role |
| `identifier_uniqueness` | number | 0.0 ≤ x ≤ 1.0 | how different a column's values have to be before synthtwin SAYS SO. It decides no role: nothing decides the identifier role but the person who owns the table |
| `kept_values` | object | exactly the five keys below | the declaration record for `--keep-value` |
| `long_tail_minimum_level` | integer | exactly `11` | the long-tail detection line, recorded on the document's own face |
| `minimum_parse_rate` | number | 0.0 ≤ x ≤ 1.0 | THE line for the numeric roles and for the datetime role, and the only one: at least this share of the present values must read as numbers this format can hold before the column is described as numbers, and at least this share must parse under one date format before it is described as dates. Applied as a COUNT, never as a compared share, so no rounding of a division decides a role |
| `near_threshold_slack` | integer | ≥ 0 | a column is reported as borderline when this many values, or fewer, separate it from a different reading. Counting values rather than comparing shares keeps the report meaningful at the ends of the scale |
| `sentinel_minimum_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells a stand-in candidate must reach to count as frequent |
| `sentinel_outlier_iqr_multiple` | number | ≥ 0.0 | how many interquartile ranges beyond the quartiles of the column's other numbers a stand-in candidate must lie to count as an outlier |
| `small_cell_floor` | integer | ≥ 1 | the disclosure floor: the smallest number of rows a group may cover and still be NAMED anywhere in this description |

**C6-20 (membership).** All TWENTY-TWO keys are REQUIRED. No other key
may appear under `settings`; a loader refuses one that does, naming
it. A block of twenty-one keys or of twenty-three — one of the
twenty-two skipped, or a key of somebody's own added — is a document
this contract does not describe. (It said TWENTY while section 4.4
said twenty-one and the producer wrote twenty-one, from the landing
that added `forced_metadata_rows` until landing 2b.17's repair pass
added `forced_delimiter` and corrected all three counts together; the
guard that compares this clause with the producer read only a word
without a hyphen, so it could not state a count past twenty.)

**THE COUNT WAS WRONG IN THREE PLACES AT ONCE and is corrected here
(2026-08-26).** This clause said seventeen, the key list of section
14 said eighteen, and the producer wrote nineteen. Two declarations
reached the code without fully reaching this document — `forced_codes`
by amendment A-P4-38, which corrected the list and not this clause,
and `forced_measurements` by A-P4-39, which corrected neither — so
every description the tool wrote was a document THIS CONTRACT DOES NOT
DESCRIBE, which is the one thing C6-20 exists to make impossible. It
was found by an adversarial re-check of an unrelated residual rather
than by a guard, and residual R-P4-42 records that nothing compares
this count with the producer's. **No settings key exists for the affix
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
written is that member's canonical form. It enters `built_in_dates` when it IS
one of the two calendar placeholders or DENOTES one under any of the
readings section 6.6.1 lists, and what is written is that
placeholder's canonical day spelling. Denotation, and not text alone,
because the two members are written in ISO while a person types the
spelling their own table uses: `01/01/1900` on a month-first column
names the member `1900-01-01`, and matching by text alone recorded the
person as having named a word of their own — so nothing could rebuild
the instruction where the column's own verdict fell below the
publication floor, and the table checked against its own description
missed fourteen obligations (plan P4-D252). The question is asked of
the typed text under this package's own readings, so no cell of any
table is consulted and a value never held by any cell is recorded
exactly as one every cell held. A declared value that is
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

**Invariant S8.** Every name in EACH of the four declaration arrays —
`forced_identifiers`, `forced_codes`, `forced_measurements` and
`forced_decimal_commas` — is the `name` of some column block. A name
that matches no column is a refusal: it means the profile and the
schema disagree about which columns were declared. The arrays are
checked separately and by the same rule, so a misspelt `--code` name
is refused exactly as a misspelt `--identifier` name is — and for the
same reason, which is that a description in which a coding system was
quietly read as a quantity must not be produced by a typo.

**Invariant S8a (no column carries two readings).** No name appears in
`forced_decimal_commas` and also in `forced_codes` or in
`forced_identifiers`. THIS IS A DIFFERENT FAULT FROM S8 AND CARRIES ITS
OWN CODE, because the two say different things to a reader: S8 says a
declared name is not a column of this table, and this says the name IS
a column and has been given two readings that cannot both be acted on.
A column read as codes or as record numbers is not read as numbers at
all, so the comma reading could never be used, and a document carrying
both would have the declaration recorded and silently ignored. The
command line refuses the pair when both are typed; this is where a
document that carries it anyway is refused.

The three ROLE declarations are governed separately and more strictly,
because they are three answers to one question: no column may carry two
of them at all. That rule is stated with them in 4.4.

**Invariant S9.** `categorical_floor <= categorical_ceiling`.

#### The floor, its minimum, and what a floor of one means

**The smallest permitted `small_cell_floor` is ONE** (owner ruling
2026-08-14; plan amendment A-P3-11). **THE DEFAULT IS 11** (owner,
2026-09-22; plan P4-D316): the floor `synthtwin profile` writes when
nobody asks for another is 11, the value it held before 2026-08-25 and
the same number as the line under which the readable files say a
description names small groups (`contract.SMALL_GROUP_NOTICE_LINE`), so a description
nobody lowered names no group of fewer than eleven rows. From
2026-08-25 to 2026-09-22 the default was 1 (plan P4-D20), and a
description made in that time carries 1 and is read as one made under a
lowered floor.

**WHY A FLOOR OF ONE IS PERMITTED, in the owner's terms.** synthtwin
publishes no structure between columns — section 4.6's eight reserved
names are all empty, and invariant S12 keeps them that way — so a
description says what each column holds ONE COLUMN AT A TIME and never
which values met in a row. What a named rare value therefore discloses
is that somebody in the table had it, and nothing else about them: not
their other columns, not which row they are. The owner ruled that this
is the disclosure the tool is for, that a rare finding must reach the
twin or the twin is not one, and that the pooling be available to
anybody whose review board asks for it rather than imposed on
everybody. That was the reasoning for the default of 1; on 2026-09-22
the owner returned the default to 11 and kept the floor of one
available to anybody who asks for it. **What a lowered floor gives up
is stated below unchanged.**

**WHAT THE RULING DOES NOT REACH, named so nobody reads it wider than
it is.** It is a ruling about MARGINAL publication. Were a later
version to publish anything that crosses two columns, the argument
above would not carry to it, and the floor would have to be decided
again on its own facts. Eleven was once also the smallest a loader
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
that `(withheld)`, `suppressed_levels`, `suppressed_rows`,
`variants_withheld` and the pooled remainders of this contract exist
to perform. On whose authority: the owner's, ruled on 2026-08-14 with
the consequence stated to them and accepted.

**No other rule of this contract is relaxed by it.** Every
floor-governed invariant is written as "at least the floor" and "below
the floor", so each one still binds at the value the document carries:
the absence-class and absence-source rules (N2, N4), the label rules
(B5, W5), the offset rule (D3), the separator rule (D12), the numeric-style rule (P2), the
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

`suppressed_levels`; `suppressed_rows`; the `n_cells` of every
`suppressed_numbers` block, whose `mean` is then `null`;
every `variants_withheld` block; `n_sentinel_candidates_unpublished`;
`n_missing_withheld`; and the `(withheld)` ENTRIES of
`missing_by_class`, `utc_offsets`, `datetime_separators`,
`numeric_styles`, `fraction_widths`, `pad_widths`, `field_widths` and
`shape_forms`.

**Amended by plan P4-D220 (stage 2 closed by the owner rulings of
2026-09-17): the `(withheld)` entries of `utc_offsets` and
`datetime_separators` are OFF this list.** Those two censuses name no
count below `parsing.census_floor`, which is two at a floor of one
(D3, D12), so at a floor of one the range below THEIR line is not empty:
a count of one is pooled rather than named, and a pool there is the
rule working, not a floor-one document holding something back. The
places a loader and a producer's guard read that exception from are one
list, `canonical.POOLED_AT_ANY_FLOOR`.

**Amended again by plan P4-D221 (stage 2 closed by the owner rulings of
2026-09-17): the `(withheld)` entries of `numeric_styles`,
`fraction_widths`, `pad_widths` and `field_widths` are OFF this list
too**, on a column, on each part of a composite column and on the
`numbers` block of a compound or affixed column. Those four censuses
name no count below `parsing.census_floor` either (P2, P5, P6b, P6c),
and a pool of theirs is held by P6, P8 and P9c at every floor; the same
list carries them.

**Amended by plan P4-D222 (stage 2 closed by the owner rulings of
2026-09-17), and the list stands.** These six censuses count a name
below `parsing.census_floor` into their commonest named count, so a
`(withheld)` entry of theirs stands only alone, where no name reaches
the line -- at a floor of one, a column whose population is one cell, or
a closed census whose names are each one cell and too few to fill a
pool that would say every name was written (`parsing.census_pools`).
Where that pool is refused the whole population is counted under the
commonest name the CELLS wrote, ties to the first in sorted order (plan
P4-D242), and never under a name no cell of the column wore.

A document that fills one of them is refused. The rule is checked with
the top-level rules, before any column block is read, because the
floor is a top-level setting and what the rule states is a fact about
the whole description.

**On EIGHT of those positions the added thing is the ENTRY, not the
field, and the difference matters.** At a floor of 1 a decimal column
of two cells written at width 2 publishes `fraction_widths: {"2": 2}`,
which is correct and must not be refused: at a floor of one every
named width reaches the floor, so widths are NAMED rather than pooled,
and the field is nonempty precisely because nothing is held back. What
must be zero or absent there is the `(withheld)` entry alone, for the
rule's own reason — at a floor of one there is nothing to pool. The
same reading applies to `missing_by_class`, `numeric_styles`,
`pad_widths`, `field_widths` and `shape_forms`: the map stays, the
pooled remainder goes. (`utc_offsets` and `datetime_separators` stood
here until plan P4-D220 took their pools off the list, and
`numeric_styles`, `fraction_widths`, `pad_widths` and `field_widths`
until plan P4-D221 took theirs; only `missing_by_class` and
`shape_forms` keep the reading.)

**What does NOT join the list, named so no reader adds it.**
`missing_by_source` is not on it: its keys are spellings of the table
and nothing else, so it carries no pooled `(withheld)` entry at any
floor, and the count of the cells whose spelling fewer than the floor
shared is `n_missing_withheld`, which IS on the list. `n_missing_blank`
is not on it and must not be added: at a floor of one every blank
group reaches the floor, so blanks are named rather than pooled, which
is what the rule requires. And `resolution_mix` is not on it because
it is floor-free — it never withholds at any floor, so a rule about
what a floor of one holds back has nothing to say about it. The
datetime block's other map, `datetime_separators`, is floor-governed
with a `(withheld)` pool, and since plan P4-D220 its pool, like
`utc_offsets`', may stand at a floor of one.

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
rule: the multiplicity rules read `variants_withheld`'s keys against
the range below the floor, and B4 holds `suppressed_rows` between
`suppressed_levels` and `suppressed_levels` times one less than the
floor, which at a floor of one is nought for both. For the others it
is not. N2, D3, P2 and P6 each say a
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
number under `settings` and needs no further wording. Of the six
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
   TWENTY-ONE and is written out rather than gathered, because a tuple
   written out is what stops a spelling of somebody's table from
   becoming an argument:

   `iso-date`, `iso-datetime`, `compact-date`, `month-first-date`,
   `day-first-date`, `textual-day-first-date`,
   `textual-month-first-date`, `dotted-month-first-date`,
   `dotted-day-first-date`, `two-digit-month-first-date`,
`two-digit-day-first-date`, `dotted-two-digit-month-first-date`,
   `dotted-two-digit-day-first-date`, `year-quarter`, `slashed-iso-date`,
   `iso-month`, `iso-mixed`, `month-first-datetime`,
   `day-first-datetime`, `slashed-iso-datetime` — the twenty `format`
   members — and
   `day-first`, `month-first`, the two reading names the
   day-and-month remark needs, and `hours_and_minutes`,
   `hours_minutes_and_seconds`, the two clock words NF46 names a form
   by. No other string is a word of this class. **The two clock words
   are NOT `format` members** and never stand at a `format` key; a
   consumer that admitted only the twenty-one would refuse NF46, which
   the shipped producer has written since the clock role landed.

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
   string, and only at FIVE positions: the two the affixed-column
   remark NF35 fixes, the two NF48 fixes on the same terms, and the
   ONE separator position of NF47. **The binding is POSITIONAL.** On
   NF35 and NF48, argument 1 conforms only when it is
   character-for-character the `affix_prefix`, and argument 2 only when
   it is character-for-character the `affix_suffix`, of the column
   block NAMED BY THE NOTE'S OWN SIBLING `column` FIELD. On NF47,
   argument 3 conforms only when it is character-for-character that
   block's `separator`. **A consumer that admitted only NF35's two
   would refuse NF47 and NF48**, which the shipped producer has
   written since the joined and affixed roles landed.

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

**The census.** The table holds 58 forms and 96 argument positions.
Of those, 83 are whole numbers, 4 are package words, 4 are nested
forms, and 5 are bound affix strings. No position is a string of any
other kind.

**This paragraph stated the count twice and the two disagreed** — 56
whole numbers in one sentence and 53 in the next, which sum to 65 and
62 against the same total. It was written that way before this phase
and no guard compared them, which is the same silence that let four
whole forms ship undefined. It states the count ONCE now.

**Notation.** «*k*» marks where argument *k* is written into the
rendering. Renderings are given character for character, including the
double hyphen `--` where the text carries one. Where a rendering writes
an argument through a fixed table rather than as its own digits, the
table is given with the form.

---

##### A. The withheld-value notes (seven forms)

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
> published: only how long they are, how many words they hold, how
> often they repeat, and -- where enough of them were written the same
> way -- the shape of that writing, which carries no letter and no
> figure of any value

**THE LAST CLAUSE IS NOT DECORATION, and C6-120 is why it is here.**
That rule makes the rendering written above the WHOLE of what this
form may say, character for character. So when the form census landed
on this role, the sentence the producer prints gained a clause and
this one did not, and every free-text profile then had two different
canonical texts depending on which of the two an implementation
followed (review round 2 finding 15). They are one sentence again.

**NF6. `identifier_publishes_no_values`** — arity 0.

> this column holds record numbers or codes, so no value of it is
> published anywhere in its description: only how many there are, how
> long they are, how often they repeat, and what synthtwin decided
> about them

**NF52. `evidence_numbers_with_labels`** — arity 4. Argument 1: how
many present cells read as ordinary numbers. Argument 2: how many do
not. Argument 3: the detection line the words are measured against,
which is the recorded floor or eleven, whichever is larger. Argument
4: rows. The sentence is the evidence for the `numbers_with_labels`
role of section 6.16 **on the ground that one of its words REPEATS
enough to be published**: the numbers are too few a share to read the
whole column as a quantity, the cells that are not numbers hold at
least one value shared by that many rows or more, and so each half is
described in its own terms.

**NF53. `evidence_numbers_with_a_few_labels`** — arity 4. Argument 1:
how many present cells read as ordinary numbers. Argument 2: how many
do not. Argument 3: how many DIFFERENT values those cells hold between
them. Argument 4: rows. The same role on its OTHER ground: 5.2's rule
admits a label half whose words are a SMALL SET however few rows each
covers, and a column of 295 readings beside five `NOT DETECTED` is
admitted by that ground and by no other. **NF52 was the only sentence
until 2026-09-03**, so such a column was published saying that one of
its values is shared by eleven rows or more when none is. One rule with
two grounds needs two sentences, and each column carries the one that
admitted it.

**NF49. `histogram_publishes_no_shape`** — arity 0.

> the shape of this column's numbers is not published: the values
> spread out far enough that at least one stretch between two edges
> holds fewer rows than your smallest group size, and a shape published
> in part would say less than nothing — it names some stretches and
> leaves the reader to guess where the rest of the values sit

---

##### B. The detection-evidence forms (fifteen forms)

**Its members are NF7 through NF16, NF45 through NF48, NF52 and
NF53.** NF53 was defined and emitted for a landing before this
membership statement named it, so a consumer following the closed list
would have read a valid producer sentence as outside the family
(review round 4 of landing L8, item 6). The second
group arrived with the four roles Phase 4 added and is written at the
foot of this section rather than among the first ten, because a form
number is an IDENTIFIER and not a position: renumbering twenty-eight
forms to keep one section contiguous would move every reference to them
in this document, in the plans and in the tests, and a renumber of that
size has already eaten one repair in this phase. Nothing else in this
document depends on a section's numbers running without a gap.

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
| `textual-day-first-date` | `17 Mar 2024` |
| `textual-month-first-date` | `Mar 17, 2024` |
| `dotted-month-first-date` | `03.17.2024 (month first)` |
| `dotted-day-first-date` | `17.03.2024 (day first)` |
| `two-digit-month-first-date` | `03/17/24 (month first)` |
| `two-digit-day-first-date` | `17/03/24 (day first)` |
| `dotted-two-digit-month-first-date` | `03.17.24 (month first)` |
| `dotted-two-digit-day-first-date` | `17.03.24 (day first)` |
| `year-quarter` | `2024-Q1` |

A format name with no row of its own is written out as itself, so
`slashed-iso-date`, `iso-month`, `iso-mixed`, `month-first-datetime`,
`day-first-datetime` and `slashed-iso-datetime` render as their own
wire spellings. The rendering is therefore fixed for all twenty members
and two implementations cannot diverge, but the six that fall through
the table read badly ("are dates written as slashed-iso-date"), and an
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

**NF45. `evidence_long_tail_of_labels`** — arity 5. Argument 1:
different values, counted after trimming and case folding. Argument 2:
the categorical ceiling. Argument 3: rows. Argument 4: the detection
line a level had to cover, which is the recorded floor or eleven,
whichever is larger. Argument 5: how many folded levels covered it.
**The sentence names argument 5 before argument 4**, which is the one
place in this section where the rendering order and the argument order
differ; it is written out below rather than left to be inferred.

> there are «1» different values, more than the «2» a set of categories
> may have in a table of «3» rows -- but «5» level(s) of it are shared
> by at least «4» rows each, so this column is a long tail of labels
> rather than free text

**NF46. `evidence_clock_times`** — arity 3. Argument 1: present cells
that read as clock times under the winning form. Argument 2: a package
word naming that form, and it is one of the two clock words of 14.6 —
never a `format` member. Argument 3: present cells that do not.
Argument 2 is written through this fixed table:

| «2» | rendered as |
|---|---|
| `hours_and_minutes` | hours and minutes, `09:30` |
| `hours_minutes_and_seconds` | hours, minutes and seconds, `09:30:00` |

> «1» value(s) are clock times written as «2-rendered», and «3»
> value(s) are not

**NF47. `evidence_numbers_joined_in_one_cell`** — arity 3. Argument 1:
present cells the joined reading accepted. Argument 2: how many
numbers each such cell holds — **numbers and not WHOLE numbers**, and
the distinction is not pedantry: the reading admits a decimal part, so
a column of `1:1.5` is read by this role, and a sentence saying "2
whole numbers" of it is false on the page a person reads. The producer
function was itself called `splits_into_wholes` until 2026-08-26, and
the name was where the false sentence came from.
Argument 3: the separator, a BOUND AFFIX
STRING — the fourth argument class — bound by identity to the
`separator` key of the block this evidence sentence stands on, so the
sentence names no spelling the block does not already publish.

> «1» value(s) are «2» numbers written in one cell and joined by «3»

**NF48. `evidence_numbers_wearing_one_affix`** — arity 3. Argument 1:
the prefix. Argument 2: the suffix. Both are BOUND AFFIX STRINGS, bound
POSITIONALLY to `affix_prefix` and `affix_suffix` of the block this
sentence stands on — the positional binding that review item P4-X5-F8
required, so a swapped pair cannot render a sentence that misdescribes
the column. Argument 3: present cells wearing the pair. **Three
renderings, selected by which sides are empty**, because a column
wearing only a suffix has no prefix to name and a sentence that named
one would describe a shape no cell has:

> where both sides are written: «3» value(s) are written as «1», a
> number, then «2»
>
> where only the prefix is written: «3» value(s) are written as «1»
> followed by a number
>
> where only the suffix is written: «3» value(s) are written as a
> number followed by «2»

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

##### D. The remarks (twenty-three forms)

> This heading read "nineteen" while the section declared twenty,
> and NF55 made it twenty-one (landing L18); NF56 made it twenty-two
> (landing 2b.2) and NF57 twenty-three (its verification). It counts the forms
> banner-declared below and nothing else; the note grammar's own
> totals are 4.5.1's and 14.8's, which the disposition guard binds
> to `taxonomy.NOTE_ARITY` in both directions.

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

**NF26. `remark_slashed_dates_are_month_first`** — arity 0. Carried
when the chosen `format` is a month-first reading of a grammar whose
day and month are BOTH written as numbers: the slashed pair, the
slashed stamp pair, the dotted pair and the two-figure-year pair. Not
carried for the textual pair, whose order a month name settles.

> where the day and the month are both written as numbers, they are
> read month first (03/04/2024 is the 4th of March); if this table
> writes the day first, the profile has the month and day the wrong
> way round

**The sentence names no punctuation** (plan P4-D15). It said "written
with slashes" while three grammars carried the same ambiguity, so a
person holding a dotted column read a true sentence as a statement
about some other column.

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

**NF54. `remark_two_readings_both_fit` — the ambiguous-column
question** — arity 1. Argument 1: how many present cells hold a number
with a short piece of text beside it.

> «1» of this column's values are a number with a short word or letter
> beside it, and synthtwin cannot tell from the values alone which of
> three things that means. It may be a MEASUREMENT that some cells
> carry a marker beside — a laboratory result flagged high or low; it
> may be numbers beside a small set of LABELS whose spellings hold a
> figure, such as a stage; or the whole column may be a CODING SYSTEM,
> some of whose codes end in a letter. The three are described very
> differently: as measurements, every one of these numbers joins this
> column's average, spread and ends; as labels, only the values wearing
> no marker are described that way; as codes, no average is published
> at all, and the codes themselves are published under the
> smallest-group size in force — at the default of 11, every code that
> 11 or more rows carried, with the rows that carried it. synthtwin has
> described the unmarked values as numbers and the marked ones as
> labels, and has not guessed further. If they are measurements, run
> the command again with --measurement and this column's name, and
> every one of its numbers will be described; if they are codes, run it
> again with --code and this column's name, and no average, smallest or
> largest will be published over them

**THE ASKING, IN THE ONE PLACE IT EXISTS SO FAR** (plan amendment
A-P4-58, owner ruling 2026-09-09; residual R-P4-157). A column of
readings beside `H` and `L` flags satisfies rule 7b and rule 9 both,
and three rules written over the TEXT to separate them were each
measured wrong — the last read `Stage 1` and `Stage 2` labels as a
quantity. Where both readings fit, the CAUTIOUS one is taken and this
sentence says what was not settled and which declaration settles it.
The two errors are not the same size: read as labels a measurement
column publishes fewer numbers than it holds and every number it
publishes is true, while read as measurements a label column publishes
a mean of stage numbers, which is a quantity that does not exist.

**WHICH READING FITS IS ASKED OF THE WALK AS IF THE COLUMN WERE
DECLARED** (landing L16). The question was put to the affix reading
with the person's own declaration, which cannot see the tie it exists
to find: undeclared, the letter guard refuses a letter written flush
against the digits, so the reading answered "none" and the tie was
invisible. A register of 280 five-digit procedure codes beside fifteen
`3074F` and five `3075F` took the cautious role in silence and
published an average of 54,239 over its bare codes. Two refusals are
kept rather than inherited from the declared walk: an electronic
address is NF50's sentence and not this one, and a wrapper carrying no
letter raises no question at all — `<0.5` is a detection limit, `$98`
is money, and neither is a coding system.

**NF55. `remark_a_letter_against_the_digits` — the flush-letter
decline** — arity 1. Argument 1: how many present cells hold a number
with a word or letter beside it, counted as NF54 counts it.

> «1» of this column's values are a number with a letter written
> against it, and synthtwin does not read such a column as a quantity
> unless it is told to: `13.5H` is a flagged laboratory result and
> `1234F` is a category of procedure code, and the values cannot say
> which. Nothing was assumed, so this column is described without a
> distribution. If these are measurements, run the command again with
> --measurement and this column's name; if they are codes, run it again
> with --code and this column's name, and no average, smallest or
> largest will be published over them

**THE ADDRESS REMARK'S SIBLING, AND OWED FOR THE SAME REASON** (landing
L16; residual R-P4-157). The decline itself is right and is not touched:
nothing in the text tells a flagged measurement from a code register, so
the guard refuses the shape and asks. What was missing is the second
half of principle 5 — a column is either handled or declined with a
plain-language explanation — and this decline had none. A person met
NF29 telling them to rewrite their data as plain numbers while two
declarations that read the column correctly had already shipped and
neither was named. It routes nothing: no role, no published fact and no
cell moves. It is not carried where `--measurement` was given, because
under that declaration rule 9 read the column and there is no decline
to speak about, nor where `--code` was given, for the reason NF50
gives. A column carrying NF50 never carries this sentence, because an
address is refused before this question is asked.

**NF56. `remark_brackets_around_the_affix` — brackets around a number
and its text together** — arity 0. Carried on an `affixed_number` column
whose commonest wrapper or a published wrapper of its set has a prefix
beginning with `(` and a suffix ending with `)`, and on no other column.

> some values of this column are written inside brackets together with
> the text around the number -- `($12.50)` or `(5 mg)` -- and synthtwin
> reads the number inside as it is written, without a sign, because
> accounting writes a negative amount that way and a note in brackets
> looks the same. The twin writes those values the same way. If the
> brackets mean negative amounts, the average, the spread and the ends
> published for those values are of the amounts without their sign, and
> the column's count of negative numbers does not include them

**A SPELLING NAMED RATHER THAN READ** (landing 2b.2). Brackets around
the figures alone, `(1,234.56)`, and brackets inside a currency prefix,
`$(1,234.56)`, are read as negative and published as `negative_form`
`brackets`. Brackets around the prefix as well, `($1,234.56)`, stand
where a parenthetical note stands, `(5 mg)`, and nothing in the values
tells the two apart, so the wrapper is kept as written and this remark
says what its numbers are. It routes nothing: no role, no published fact
and no cell moves. It carries no argument, for the reason NF50 gives:
the wrapper is published in the block beside it.

**NF57. `remark_a_minus_after_the_figures` — a minus after whole
figures** — arity 0. Carried on an `affixed_number` column whose
commonest wrapper or a published wrapper of its set has a suffix ending
with `-`, and on no other column.

> some values of this column are written with a minus after their
> figures and no decimal point -- `500-` -- and synthtwin keeps that
> minus as text written after the number rather than reading it as a
> sign, because a whole amount owed is written that way and so is a
> grade or a code. The twin writes those values the same way. If the
> minus means a negative amount, the average, the spread and the ends
> published for those values are of the amounts without their sign, and
> the column's count of negative numbers does not include them

**A SPELLING NAMED RATHER THAN READ** (the verification of landing
2b.2). A hyphen-minus after figures carrying a decimal point,
`1,483.65-`, is read as negative and published as `negative_form`
`trailing_minus`. After figures with no point it is not: `500-` is
written the same way as a grade `3-`, and a thousands mark does not
settle it, because a ledger writing `1,234-` beside `500-` would then
split one column into numbers and text by the size of each value. So
the minus stays in the wrapper for every such cell, and this remark
says what its numbers are. It routes nothing: no role, no published fact
and no cell moves. It carries no argument, for the reason NF50 gives.

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
> rather than measurements, run the command again with --code NAME,
> where NAME is this column's name, and no average will be published
> over them; each code a smallest-group's worth of rows share is kept
> exactly as written, with the number of rows that carried it. If
> instead they are record numbers nothing should publish, --identifier
> NAME leaves them out of the profile altogether.

**IT NAMES `--code`, NOT `--identifier`** (residual R-P4-72, landing
L19). This sentence was written before `--code` existed (amendment
A-P4-38, 2026-08-25) and named the OPPOSITE declaration: a person told
"if these are codes, run with --identifier", doing exactly as they were
told, published no value of the column at all — throwing away the
distribution of codes that is the reason for declaring it. NF43 shed
the same flaw at landing L16 and this one kept it, because it is quoted
inside a frozen reference vector
(`tests/reference/generation-branch-vectors.json`), so repairing it
moves committed bytes and the independent oracle in the same commit.
That is what landing L19 did.

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

Carried whenever `day_first` was given and an ambiguous numeric
reading — slashed, slashed stamp, dotted or two-figure-year — was in
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

**Carried once for each such level, in the order of the three-member
list, and only for levels the block PUBLISHES.** A column publishing
both `-999` and `9999` carries two of these remarks, because a form
naming only the first would leave the reader's other level unexplained
— and the one left out is the one they had not thought of. A level the
small-cell floor held back is not published, so no remark describes it:
a sentence naming a value the same block promises to withhold is the
contradiction 6.4's floor exists to prevent.

**The level is matched by NUMBER and not by spelling**, which is the
rule `settings.declaration_matching` states for a declared value: `-999`, `-999.0` and `-999.00`
are one number, and a column spelling it with a fraction is exactly the
column whose owner has not noticed.

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

**NF42. `remark_two_figure_years_are_read_at_a_pivot`** — arity 0.
Carried on every column read under the two-figure-year pair, whichever
way its month and day were settled.

> this column writes its years with two figures, which do not say which
> century they are in; 00 to 68 are read as 2000 to 2068 and 69 to 99
> as 1969 to 1999, so any year this table means outside 1969 to 2068 is
> read as the wrong one

**The consequence is a RANGE and not a distance.** An earlier wording
said such a table is read forward "by a hundred years", which holds
only for the century either side of the pivot: `68` meaning 1868 is
read as 2068, two hundred years out, and `75` meaning 2075 is read as
1975, out in the other direction and not warned about at all.

**It stands outside the month-first chain, not inside it** (plan
P4-D15). The century is a guess whether the month and day were settled
by the column's own evidence, by a declaration or by the default, so
the sentence is carried in all three cases and not only where something
else was also guessed.

**NF43. `remark_padded_numbers_may_be_codes`** — arity 1. Argument 1:
how many of the column's cells were written with a leading zero, the
count `numeric_styles` names for `leading_zero`. Carried on a `count` or
`continuous` column whose forms map names that form, and on no other
(amended by plan P4-D221, citing the owner rulings of 2026-09-17: the
argument was counted off the cells so that padding the map pooled was
still told, and a pooled count of one was printed here by that route).

> «1» of this column's values are written with a leading zero, and
> synthtwin described them as quantities: their average, their spread
> and their ends are in this profile. A number written `00100` is
> usually a code rather than a measurement — nothing is assumed from
> that, and the column is described as numbers either way, which keeps
> its distribution. If these are codes, run the command again with
> --code NAME, where NAME is this column's name, and no average will
> be published over them; each code a smallest-group's worth of rows
> share is kept exactly as written, leading zeros and all, with the
> number of rows that carried it. If instead they are record numbers
> nothing should publish, --identifier NAME leaves them out of the
> profile altogether

**IT NAMES `--code`, NOT `--identifier`** (landing L16). This sentence
was written before `--code` existed (amendment A-P4-38, 2026-08-25)
and went on proposing the declaration that WITHHOLDS a column to a
person whose column is codes — while the screen notice raised on the
same column by the same signal said `--code`. Two surfaces of one
profile named opposite declarations for one column: `--code` keeps
every code with the rows that carried it, `--identifier` publishes
none of them. The sentence names the route that keeps the codes
first, and `--identifier` after it, for the column that really is a
record number. **NF35's affixed sentence carries the same flaw and
is NOT repaired here**: it is pinned by a frozen reference vector,
so it moves with the code-wording landing that also moves the
oracle, and residual R-P4-72 carries it until then.

**IT DECIDES NOTHING, and the sentence says so** (plan P4-D16). The
README's ratified rule is that no rule may DECIDE the identifier role
from a column's values, and this does not: the column is described as
numbers either way. It PROPOSES, which is what NF32's all-different
sentence and NF35's affixed sentence already do — and between those
two a column of `00100` fell through. NF32 reaches a column whose every
value differs, which a code column is not, because codes repeat; NF35
reaches a column wearing an affix. A procedure code, a vaccine code or
a zip written with its leading zero had no pointer at all while being
published with an average and a spread.

**Why leading zeros and not some other signal.** Because it is a fact
the producer already reads and already publishes a census of (7.8), and
because nobody writes a MEASUREMENT as `00100`. It is evidence about
how the column was written, not a guess about what it means.

**NF44. `remark_commas_read_as_thousands`** — arity 2. Argument 1: how
many cells read as a number by way of a comma that SETTLED NOTHING —
one comma, exactly three figures after it, no point. Argument 2: how
many present cells SETTLE the question as a decimal comma — a group
that is not three figures, a first group longer than three, or a point
before the comma. Argument 2 is counted over every present cell and not
only over the numbers, because a cell that settles it is usually not a
number this format reads. Carried on `count`, `continuous`,
`affixed_number` (over the cores) and `free_text`, wherever either
count is not zero.

**It renders two sentences, one per situation.** Where argument 2 is
zero:

> «1» of this column's values are written with a comma inside the
> number that could be read either way, and synthtwin read every one of
> them with the comma as a thousands separator — so `1,795` was read as
> one thousand seven hundred and ninety-five. MANY COUNTRIES WRITE THE
> DECIMAL POINT AS A COMMA, and if this table is one of them then
> `1,795` means 1.795 and each of those values has been read as a
> thousand times its real size, carrying any average, spread or ends
> this profile publishes for this column with them. Nothing in this
> column settles which was meant. If your file writes decimals with a
> comma, run the command again with --decimal-comma and this column's
> name, and this column is read that way. Rewriting the column with a
> decimal point works too, and changes your file where the declaration
> does not

and where it is not:

> «2» of this column's values cannot be read with the comma as a
> thousands separator — a thousands group is exactly three figures and
> these are not — so THIS COLUMN CONTAINS VALUES WRITTEN WITH A DECIMAL
> COMMA, and synthtwin does not read those as numbers at all. Of the
> rest, «1» could be read either way and were read with the comma as a
> thousands separator, so `1,795` was read as one thousand seven
> hundred and ninety-five; every one of those that was meant the way
> the values above are written has been read a thousand times too
> large, and any average, spread or ends this profile publishes for
> this column are wrong with them. Run the command again with
> --decimal-comma and this column's name, and every one of them is
> read as a decimal number. Rewriting the column with a decimal point
> works too, and changes your file where the declaration does not

**A CELL CAN SETTLE IT, AND AN EARLIER WORDING HERE SAID OTHERWISE**
(plan P4-D17). That wording was wrong in both directions. A point AFTER
the comma settles it as a thousands separator, and so does a second
comma: `1,234.56` and `1,234,567` are not ambiguous, and warning such a
column was a false alarm on a common shape — which is how a true alarm
stops being read. A first group longer than three settles it the other
way, because `1000,000` cannot be thousands-grouped at all, so a
European column carries its own proof as soon as one of its values
reaches a thousand. What settles nothing is a column every one of whose
values is under a thousand and written to three figures.

**A CELL OF FIGURES, POINTS AND COMMAS IS NOT THEREFORE A NUMBER.**
`1.2.3,4` is a software version and carries only those characters, and
its point before the comma made it proof of a decimal comma — so a
column of versions would have been told in capital letters that this
file writes decimals with commas. A body carrying more than one point
speaks only where the fields those points separate GROUP: the first one
to three figures, every later one exactly three. That is what tells
`1.2.3,4` from `1.234.567,89`, which is a million and a bit written the
German way. A body carrying no figure at all — `.,` — says nothing
either.

**ONLY A CELL TRYING TO BE A NUMBER MAY SPEAK.** Argument 2 reaches
every present cell rather than only the numbers, because a cell that
settles the question is usually not a number this format reads —
`1000,000` is why the count exists. That reach is also its danger: a
cell carrying any character that is not a figure, a point or a comma
says NOTHING, because without that guard `Hello.World,Foo` is a point
before a comma and a column of names or addresses would be told, in
capital letters, that this file writes the decimal point as a comma.

**NEITHER SENTENCE PROMISES A PARTICULAR STATISTIC IS WRONG.** A
column whose values are symmetric about zero has the same mean under
either reading, because a factor of a thousand applied to every value
cancels — so "any average this profile publishes is wrong" is not
universally true. What is true, and what both sentences say, is that
every statistic was COMPUTED FROM those numbers.

**NEITHER SENTENCE CLAIMS A STATISTIC THE COLUMN MAY NOT HAVE, AND
NEITHER SPEAKS FOR THE FILE.** A column that PROVES a decimal comma is
usually `free_text`, because the cells that prove it are not numbers
this format reads and the column drops below the parse line because of
them — so a sentence naming "this column's average" would be false
exactly where it matters. Both say "any average, spread or ends this
profile publishes", which is true whether it publishes them or none.
And two proof cells beside two hundred legitimate thousands-grouped
ones do not make the FILE European: the settled sentence says what it
saw, that this COLUMN contains such values.

**A SHARED SUFFIX THAT BEGINS WITH A COMMA IS NOT DECIDED HERE, AND
THE ATTEMPT TO DECIDE IT WAS WITHDRAWN.** `10,5` through `249,5` is
read by the affix rule as the number 10 wearing the suffix `,5`, so the
cores are comma-free, a scan of them finds nothing, and the block
publishes statistics over 10 to 249 for values running 10.5 to 249.5. A
clause once stood here saying such a suffix is the fractional part of a
European number and counting every cell wearing one as proof. It is
withdrawn: `10,5` as a revision identifier with a genuine `,5` suffix
is OBSERVATIONALLY IDENTICAL, and the clause asserted one reading and
told the person to rewrite their file with a decimal point — which on
the other reading corrupts every identifier in the column. Silence is
not good here and is not defended as good; it is better than a
confident wrong answer that instructs somebody to damage their data.
The gap is residual R-P4-33.

**It counts CELLS and speaks of them, never of "every value".** A
column of fifty comma-bearing cells beside fifty plain ones is not
uniformly a thousand times out, and its average is not out by that
factor either.

**It states the size of the error on purpose.** A column read the wrong
way here is wrong by a factor of a thousand, and every statistic
published about it is wrong by that factor. A sentence that hedged
would be a sentence a reader could pass over.

**NF50. `remark_an_address_is_not_a_quantity`** — arity 0. Carried on
the column the affixed-number rule declined BECAUSE its winning affix
pair is an electronic address — every other test of that role having
passed — and on no other column. It carries no argument: see below.

> the values in this column are a number wrapped in an electronic
> address -- some text, then the number, then an at sign, a host and a
> dot label -- and synthtwin did NOT read them as a number wearing a
> shared piece of text. Reading them that way publishes an average, a
> spread and two ends over the numbers inside real addresses, which
> are whatever numbers those addresses were given and are not a
> quantity of anything. THIS SENTENCE DECIDES NOTHING, and no rule of
> synthtwin can decide it either: it is here so that you can recognize
> your own column and say what it holds. Three declarations say it,
> each a different thing. Run the command again with --identifier NAME
> to say these are record numbers, and no value of this column is
> published at all; with --code NAME to say they are a coding system,
> and each spelling a smallest-group's worth of rows share is published
> with how many rows carried it; or
> with --measurement NAME to say the number inside is a quantity after
> all, and the column is described as numbers wearing that address.
> NAME is this column's name

**Its number is appended, on the NF45–NF48 precedent.** A form number
is an IDENTIFIER and not a position, so a remark added after the
header-verdict group is numbered after everything rather than inserted
among the remarks of group D and renumbering every clause behind it.
Group D's stated size is NF19 through NF37 and does not move; NF42,
NF43 and NF44 are remarks appended the same way before this one.

**WHY IT EXISTS: the decline had no words** (plan P4-D27, residual
R-P4-39). `user12345@example.org` was read as a number wearing the
affix pair `user` / `@example.org` and published a mean of 53,574.055
over 400 rows — the average of real identifiers. The rule that stops
that shipped without a sentence: the column simply stopped being
described as numbers, and the profile, the summary beside it and the
twin's report all said nothing about why. The second half of
principle 5 is that a column is either handled or **declined with a
plain-language explanation**, and this decline had none.

**IT ROUTES NOTHING, and that is a property of this clause rather than
a hope about the producer.** The remark is carried into whatever role
the later rules give the column, and its presence changes no role, no
published fact and no cell of the twin. What decides this column is
one of the three declarations it names. A declaration is made by
whoever holds the table, and no rule here may arrive at that decision
by reading the column (the standing ruling of review item P1-R6-F8).

**IT NAMES ALL THREE ROUTES, WITH WHAT EACH ONE DOES.** A list of
flags with no consequence beside them is a list nobody can choose
from, so each is stated with its outcome, and each outcome was
measured on the column this form exists for: `--identifier` gives the
`identifier` role and publishes no value of the column; `--code` gives
`long_tail_labels` and publishes each spelling with how many rows
carried it; `--measurement` restores the `affixed_number` reading,
whose block describes the cores.

**ARITY 0, AND THE TWO CANDIDATE ARGUMENTS ARE BOTH REFUSED.** A count
of the cells that wore the pair is a count of a reading this column
does NOT publish — the block that would have held `n_affixed` is
exactly the block the decline refused to write — so it would be the
one whole number in this grammar that no key beside it answers for.
And the pair itself is the fourth argument class of 4.5.1, admitted
only where the SAME block publishes the spelling under `affix_prefix`
and `affix_suffix`; this block publishes neither. The sentence
therefore names the shape in its own fixed words and no number and no
spelling of this column reaches it.

**NF51. `remark_whole_numbers_could_be_times` — the time-band remark**
— arity 7. Carried on a `count` column, and on no other role, when
every number it holds lies in one of the two bands below. Its number is
appended, on the NF45–NF48 and NF50 precedent.

| # | class | meaning |
|---|---|---|
| 1 | whole number | which band: 1 for seconds, 2 for milliseconds, and nothing else |
| 2 | whole number | the year of the smallest value, read in that band |
| 3 | whole number | its month |
| 4 | whole number | its day |
| 5 | whole number | the year of the largest value, read in that band |
| 6 | whole number | its month |
| 7 | whole number | its day |

**The two bands, stated as calendar years and not as large numbers.** A
band runs from the first day of the year 2000 up to, and not including,
the first day of the year 2051. The whole numbers themselves are that
pair of days multiplied by how many units the band counts in a day —
86,400 for seconds, 86,400,000 for milliseconds — so the bound is
derived from the calendar and is not a constant anybody types. A column
is IN a band when every number it holds is a whole number this format
can hold and lies at or above the band's first value and below its
last.

**Why the band does not begin at zero.** Zero is the 1st of January
1970, so a band starting there covers every ordinary count a table
holds — ages, tallies, row counts — and the remark would fire on nearly
every column of whole numbers. A remark that routes nothing can afford
that least of all.

The rendering writes UNIT from argument 1 through this fixed table:

| «1» | UNIT |
|---|---|
| 1 | `seconds` |
| 2 | `milliseconds` |

and writes each of the two days as «*year*»-«*month*»-«*day*» with the
year in four figures and the month and the day in two, each padded with
zeros on the left:

> every value in this column is a whole number, and every one of them
> sits in the band a computer writes a moment in time into when it
> counts UNIT from the 1st of January 1970. Read that way this column
> runs from «2»-«3»-«4» to «5»-«6»-«7». synthtwin read them as plain
> numbers and describes them as a count of things. THIS SENTENCE
> DECIDES NOTHING and moves nothing: no rule of synthtwin reads a
> number as a moment in time, and no declaration makes one. It changes
> nothing about your twin either -- reading the column as plain numbers
> keeps every value where it was and every distance between two of
> them, so turning the twin's column into dates the way you would turn
> your own gives dates over the same span. What was missing is being
> told, so that you can recognize your own column and say in its name
> what it holds

**IT NAMES NO DECLARATION, and that is not an omission.** Every other
advisory remark of this grammar ends by naming the flag that would
change the reading. There is none here: no rule of this version reads a
number as a moment in time, and no declaration makes one. A sentence
naming a flag that does not exist would be worse than silence, so the
remark says what the column looks like, says the twin is unaffected,
and stops.

**Why the twin is unaffected, stated in the sentence itself.** The
numeric reading keeps the column's range and the spacing of its values,
which is what every published fact of a `count` column is about — so
converting the twin's column to dates the way the source column would
be converted gives dates over the same span. What was missing was never
fidelity; it was the person being told (residual R-P4-9).

**Both ends are facts the block already publishes.** They are `min` and
`max` of the same block, written a second way, so the sentence
discloses nothing the description does not already hold.

**Why the definition is over every value, stated exactly.** A band is
one interval, so on this role — where every value is a whole number —
asking the two ends answers the same question as asking every value,
and both were run against each other. The definition is written over
every value because that is the property the sentence asserts, and
because it survives what the equivalence does not: a band ever written
as two intervals, or a role ever admitting a value whose text does not
settle it as whole, breaks the equivalence and leaves the definition
standing. A producer may compute it either way and write the same
sentence.

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
| NG14 | the form is one of the 58 in section 4.5.1 |
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

**NF58. `header_names_could_not_be_told`** — arity 0. The verdict
where the first row could not be told from a record of the table (owner
ruling of 2026-09-17, item 8; plan P4-D232). It names no column, quotes
no cell, and cannot: the row it is about is the one the reading
withholds.

> The first row could not be told from a record of the table, so
> synthtwin named the columns itself -- column_1, column_2, and so on --
> and kept every row of the file, that first row included. No text of it
> appears anywhere in this description. The questions file beside this
> one asks which reading is right: run the command again with
> --first-row names if that row holds the column names, or leave it as
> it is if it is the first record.

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
| `role` | string | one of the fifteen role names fixed by the table in section 5.2 | the type path the taxonomy chose | EXACT-CONTROL |
| `statistical_type` | string | one of the fifteen statistical types fixed by the table in section 5.2 | the shape of the column's values | EXACT-CONTROL |
| `quality_state` | string | `ok`, `empty`, `unrepresentable` | whether the column has usable values at all | EXACT-CONTROL |
| `structural_role` | string | `data`, `identifier` | whether the column was declared to hold record numbers or codes | EXACT-CONTROL |
| `n_present` | integer ≥ 0 | ≤ `n_rows` | how many cells hold a value | EXACT-OBSERVABLE |
| `n_missing` | integer ≥ 0 | ≤ `n_rows` | how many cells hold no value | EXACT-OBSERVABLE |
| `missing_by_class` | object | exactly six keys, section 5.4 | absent cells by the reason each was counted absent | REPORT-ONLY |
| `missing_by_source` | object | section 5.4 | absent cells by the exact spelling that made them absent, under the floor | EXACT-OBSERVABLE — recounted per spelling from the written twin, every key alike, a key a judged pass put there (a spelling reading as a stand-in number, or as a calendar placeholder) included |
| `n_missing_blank` | integer ≥ 0 | — | how many absent cells of this column held the EMPTY spelling — nothing at all, not even space (C6-125); a cell that held only space wore a spelling and is a key of `missing_by_source` — written when at least `small_cell_floor` cells did, and `0` otherwise, those cells being counted in `n_missing_withheld` instead | REPORT-ONLY, bound by the sum identity the twin's reproduction rule states: the twin's recounted blank absent cells equal `n_missing_blank` plus `n_missing_withheld`, because a per-field equality would be false by construction |
| `n_missing_withheld` | integer ≥ 0 | — | how many absent cells of this column wore a spelling — or a blankness — that fewer than `small_cell_floor` cells of the column shared, pooled together and unnamed | REPORT-ONLY, bound by the same sum identity |
| `n_distinct` | integer ≥ 0 | ≤ `n_present` | how many different RAW present spellings the column holds — except on the four roles that publish a level list, and on a compound column's label half, where it counts the spellings the block SPEAKS OF (plan P4-D276) | set per role group, section 9 |
| `n_distinct_folded` | integer ≥ 0 | ≤ `n_distinct` | how many different FOLDED identities it holds | set per role group, section 9 |
| `n_numeric` | integer ≥ 0 | — | present cells that read as a number this file format can hold | EXACT-OBSERVABLE by class-preserving construction |
| `n_not_numeric` | integer ≥ 0 | — | present cells that are not numeric notation at all | EXACT-OBSERVABLE by class-preserving construction |
| `n_out_of_range` | integer ≥ 0 | — | present cells that are well-formed numbers too large or too small for binary64 | EXACT-OBSERVABLE by class-preserving construction |
| `n_contradictory` | integer ≥ 0 | — | present cells written in numeric notation whose meaning conflicts with itself — a sign inside accounting parentheses | EXACT-OBSERVABLE by class-preserving construction |
| `n_sentinel_candidates_unpublished` | integer ≥ 0 | — | how many stand-in candidates were judged but occurred in too few rows to be named | REPORT-ONLY |
| `sentinel_verdicts` | array of objects | section 5.5 | what was decided about each named stand-in candidate — a stand-in number or a calendar placeholder — why, and which of this column's published absent spellings the decision took out | REPORT-ONLY |
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
the fifteen roles a second time, as the order its rules are tested in;
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

**THE FOUR ARE PROTECTED ON A DECLARED RECORD NUMBER AND NOWHERE ELSE,
AND THAT IS A KNOWN GAP** (plan P4-D277, recorded by the repair pass of
2026-09-18). Invariant X2 counts a part below max(2, `small_cell_floor`)
into the largest part on `structural_role` `identifier`, because a
declared record number's block promises to name no value of the table
and a part of one names the one record that holds it. `free_text` carries
the same promise (F3) and does NOT get the same protection. **Measured**
at a floor of eleven: 999 different notes of eight words each beside one
cell reading `42` publish `n_numeric 1` and `n_not_numeric 999` against
`n_present 1000`, and a notes column with one stray number is an ordinary
shape. It is not closed here because these three counts are what the
NUMERIC roles are described BY -- a column of measurements publishes
`n_not_numeric` beside a form census checked against it (SF3,
`parsing.form_never_a_number`) -- so absorbing them on `free_text` alone
would make one role's four counts mean something different from every
other role's, and absorbing them everywhere changes what those roles
describe. Whether the partition moves for every role at once is the
owner's, and it is put to them with this measurement rather than settled
here. Until it is, a reader of a `free_text` block should read these four
counts as UNPROTECTED by the floor.

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
total over the fifteen roles and admits no other combination. The
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
| `joined_numbers` | `joined_numbers` | `ok` |
| `numbers_with_labels` | `numbers_with_labels` | `ok` |

**Fifteen rows, fifteen statistical types, one row each.** The table
is a bijection: no two roles answer the same `statistical_type`, and
every one of the fifteen types is reached by exactly one role. The
row order above is presentational; what is normative is the set of
rows, and invariant A4 is what a loader enforces against it.

**Four roles answer something other than their own name, and each is a
case where the role name and the shape of the values are not the same
fact.** An `empty` column has no shape to report and no usable values;
a `numeric_unrepresentable` column was written as numbers and holds
none this format can carry; an `identifier` column holds codes; and
`free_text` holds text. The other ten name their own shape. The table
is written out row by row rather than derived from the role string,
because a mapping a reader can check is worth more than one line of
cleverness.

**C6-19.** `time_of_day`, `affixed_number`, `long_tail_labels` and
`joined_numbers` each name themselves. That is a stated cost rather than an oversight: for
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

**A2 and A3 stay narrow across all fifteen roles, and here is why they
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

**Invariant A5.** The table above is total over the fifteen roles:
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

**C6-1.** The role vocabulary has fifteen members. Which one a column
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
12. `joined_numbers`, read from the values in the one shape section
    6.15 names — two plain whole numbers joined by a slash;
13. `free_text`.

Fourteen roles in thirteen rules: `count` and `continuous` are decided
by one rule, which then chooses between the two. `joined_numbers` is
also reached by the person's declaration ahead of the rules that read
values, in its full reading, as section 6.15 states.

**Why rules 9 through 12 sit after `categorical`.** They are tested
last before the fallback, so they claim only columns every earlier rule
declined; no column an earlier rule can claim is diverted into one of
them, and no earlier rule's reach depends on them. Their internal order
is `time_of_day` before `affixed_number` — clock text rarely splits as
an affixed number, but the time reading is the more specific claim —
and `affixed_number` before `long_tail_labels`, because a distribution
beats labels where both could fire. `joined_numbers` comes last before
the fallback (plan P4-D40): a column of slashed pairs that repeat often
enough to be labels keeps the label reading it had, and the rule claims
only a column that would otherwise publish nothing.

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
| `variants_withheld` | different spellings of one published label that stayed below the floor — empty at every raised floor since plan P4-D275 counted them into the level's commonest spelling | section 7.4: W4 closes its weighted sum inside the level entry, W5 holds every key between 1 and `small_cell_floor - 1` |

The sizes of a label column's held-back levels were the same CLASS of
fact — sizes of unnamed groups — published as a sorted array rather
than a map. Since the owner's ruling of 2026-09-17 (item 2, option A;
plan P4-D201) they are not published at all: section 6.3 publishes only
their pooled total, `suppressed_rows`.

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

**C6-125 (a spelling of nothing but space is a spelling).** A cell
holding one space, two spaces, a tab or a no-break space held
something: a mark the file carries, which the reader of that file
meets. Such a cell is therefore keyed here under its exact characters,
held to the floor like every other spelling, and the twin writes it
back (C6-115). Only the EMPTY spelling — no characters at all — is
counted in `n_missing_blank`, and it is never a key of this map, since
a document naming it both ways would count one cell twice in N3.

Until this clause, `n_missing_blank` held both, and the spelling was
lost: a 500-row column of readings whose 315 absent cells included 177
holding a space, two spaces or a no-break space published
`n_missing_blank: 315`, and its twin wrote 315 empty cells. Nothing the
description published could tell the two files apart, while
`pandas.to_numeric` runs on the twin and raises on the table, and a
reader handed `na.strings=c("","NA")` finds levels on the table that
the twin does not have — which is the first goal failing silently.

**Invariant N3 (the source accounting closes).** On a column that is
not a nothing-publishing column (6.10):

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    == n_missing
```

**On a nothing-publishing column the same three numbers are an UPPER
BOUND rather than a total** (C6-126):

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    <= n_missing
```

Such a column used to publish `{}` with both counts at 0 whatever
`n_missing` was, on the reasoning that naming a spelling there would
publish a value out of a column that publishes none. That reasoning is
right about the TABLE's text and wrong about this format's own: `NA`,
`N/A` and `NULL` are members of the published vocabulary, which C6-31
fixes as containing no text from any table, so naming one discloses
nothing of the column. The bound is an inequality rather than a total
because the cells whose spelling is NONE of synthtwin's own words are
withheld by the class and counted by nothing — they are not added to
`n_missing_withheld`, since that remainder is what the FLOOR held back
and a description written at a floor of one holds nothing back (S13).
What the old rule cost is measured at C6-126.

**And no key of the map is the empty spelling** (C6-125). Cells that
held nothing at all are `n_missing_blank`; a key of no characters would
count them a second time and the sum above would no longer close.

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

**Invariant N6.** A consumer decides whether a column is
nothing-publishing from `role` and `structural_role`, both of which
every block publishes, and NEVER from a count reading zero.

**The two absence counts stopped signalling the class** (C6-126). They
were 0 on exactly the nothing-publishing columns, which let a consumer
infer the class from the zeros; since such a column accounts for its
absent cells like any other, both counts now mean on it exactly what
they mean everywhere else. The inference path is withdrawn rather than
narrowed, and the sentence above is what replaces it: the class is
published outright, so nothing needs to be inferred from a nought.

**Invariant N7 (producer).** A `missing_by_source` key is the source
spelling character for character. A loader holds one document and never
the table it describes, so it cannot check that the spelling published
is the spelling a cell wore.

#### 5.4.4 Why the blank count and the blank CLASS are two numbers

`n_missing_blank` is not the same number as
`missing_by_class["(blank)"]`, and neither replaces the other. The
class count is pooled when the CLASS falls below the floor; the field
is pooled when the SPELLING — here, blankness — falls below it.

**They also answer two different questions about space, and C6-125 is
where that shows.** The CLASS asks why a cell is absent, and a cell of
nothing but space is absent for the blank reason, so it reads
`(blank)`. The FIELD asks what was written, and a space was written, so
that cell is keyed in `missing_by_source` and is not in
`n_missing_blank`. A column of forty absent cells, twenty-five of them
empty and fifteen holding one space, publishes
`missing_by_class["(blank)"]: 40`, `n_missing_blank: 25` and
`missing_by_source: {" ": 15}` — three numbers that disagree only if a
reader takes the first two to be answers to one question. A
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
exactly these five keys:

| key | JSON type | permitted values |
|---|---|---|
| `candidate` | string | the stand-in number as text; the canonical ISO day spelling of a calendar placeholder (6.6.4); or exactly `(withheld)` |
| `verdict` | string | `read_as_missing`, `kept_as_a_number` |
| `reason` | string | `outlier_and_frequent`, `not_an_outlier`, `too_rare`, `too_few_other_values`, `kept_by_you` |
| `n_occurrences` | integer ≥ 1 | how many rows held the candidate |
| `spellings` | array of strings | the keys of this column's `missing_by_source` whose cells THIS decision took out, in the document's own key order and each named once, no spelling named by two decisions of the column, and together covering at most `n_occurrences` absent cells; empty on a decision that kept its candidate, on a nothing-publishing column, and where every spelling the pass took fell below the floor |

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

**Invariant V5 (the spellings a decision took out).** Every member of
`spellings` is a key of this column's `missing_by_source`; the members
are in ascending order and each appears once; no spelling is named by
two decisions of one column, because a cell is taken out once; the
cells those spellings cover never outnumber `n_occurrences`, because a
decision cannot have removed more cells than the rows it says held its
candidate; on a column that publishes values of the table, the cells
the `read_as_missing` decisions took out and name no spelling for —
each decision's `n_occurrences` less the cells its spellings cover,
added over ALL of them — are at most `n_missing_withheld`, because a
spelling the floor did not let the column name goes to that one pool
and nowhere else, and the pool is spent once (plan P4-D135); and a
decision whose `verdict` is `kept_as_a_number` names none, because it
took no cell out of the column.

**The omission part closes what the two before it left open (review of
158c811, plan P4-D135).** They bound a decision's named spellings from
above, so a decision edited to name NONE of the spellings it took out
still loaded: twenty judged `1900-01-01 00:00:00` beside a pool of
nought. With the link gone the validator read that spelling as a
declaration reaching the whole table, and an unchanged second column
fell from 500 values to 420 with 13 obligations missed. No producer
writes that document.

**The last two parts are what make the key CHECKABLE rather than
merely published, and they were added by landing 2b.14 (P4-D95).** The
key was introduced because no count in the block can separate a judged
spelling from a declared one — which is also why a description that
names the wrong one cannot be caught by reading the counts back. A
consumer must therefore be able to refuse the claim on the block's own
arithmetic, and it can: a declared spelling's cells push a decision's
total past the rows it says held its candidate. Without that bound a
description could say a word the PERSON DECLARED was one column's own
judged pass, and every consumer would believe it — the generator would
stop reserving that word for the whole table and write it into another
column as a present value, and the validator would stop recovering it
as a declaration. That is the defect of landing 2b.3 restored through
a document instead of through a count.

**The bound is AT MOST and not EXACTLY, and the floor is why.** A pass
takes every cell of its candidate, but the description names only the
spellings the floor let it publish. Demanding equality would refuse a
description a producer writes: a column whose second spelling reaches
the floor names both, and the difference is nought; a column whose
second spelling does not reach it names neither, because the pool
takes the first as well, and the difference is the decision's whole
total against a census that covers none of it, which says nothing.

**...AND WHAT IS LEFT OVER IS NOUGHT OR REACHES THE FLOOR (review
round 2, the disclosure pass, item 2 and its repair pass).** The
difference between `n_occurrences` and the cells a decision's named
spellings cover is the count of cells wearing the spellings the floor
POOLED, and nothing in the document publishes that count — so it is
held to `census_floor` like every other count synthtwin withholds,
which is the one disclosure rule asked at the one line
(`parsing.census_names_one_row` over the pair, at the smallest group
size). Measured at a floor of eleven: twenty `-999` beside one
`-999.0` published `missing_by_source {"-999": 20}` against an
`n_occurrences` of 21, and 21 less 20 is one person; two, five and ten
of the second spelling gave two, five and ten the same way. The
producer pools the named spellings until the difference is nought or
reaches the line, and this loader refuses any description — written by
hand or not — that says otherwise. At a floor of one nothing
moves, because `census_floor(1)` is two, which is the line this part
asked when it was written.

It publishes no group the floor pooled and no spelling the block does
not already carry. What it adds is the LINK between a published hole
spelling and the pass that made those cells absent, and that link is
not derivable from any count in this document: a column whose twenty
`1900-01-01 00:00:00` cells a calendar-placeholder pass judged, beside
thirty `1900-01-01T00:00:00` cells the person declared missing, has two
keys writing ONE candidate day, and every count the block carries reads
the same under either assignment. Both consumers need the answer — the
generator decides from it which spellings reach the whole table and
which stay the judging column's own (section 9's `missing_by_source`
row, and the twin's write rule), and the validator reads the
person's declarations back out of the columns the same way — and both were
guessing from counts. Each guess failed in its own direction on a real
table: one promoted a judged spelling to a declaration and made a
second column's ordinary values read as absent, so the REAL table
missed thirteen obligations of its own description; the other narrowed
a person's declared word to one column, so the twin wrote it as a
present value elsewhere.

A DECLARED CELL CAN NEVER STAND HERE. Declarations are applied before
any pass judges anything (3.2), so a cell a judged pass removed is a
cell no declaration claimed, and the producer records the spelling at
the moment it removes the cell rather than working it out afterwards.

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

**L2 IS READ ON A BLOCK WITHOUT `tails` AND ON A HEAPED END** (stage 3,
section 6.7a). On a block that carries `tails` the two ends are
published only where at least max(`small_cell_floor`, 3) rows held the
value -- a HEAPED end, a value of a group -- and they are then the
smallest and the largest exactly as here, checked ONE-SIDED: no cell of
a file beyond them. Where they are withheld they carry no obligation at
all and the tail facts of 6.7a carry what the description says about
those rows.

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

**A NULL RUNG OUTSIDE A TAIL'S BOUNDARY MEANS SOMETHING ELSE** (stage
3, section 6.7a). On a block carrying `tails`, a rung outside
`[tails.low.percent, tails.high.percent]` is null BY RULE -- the rung
would read one of the outermost rows, and those rows are described by
the tail facts and never one by one (TL1) -- and the value written in
its place is the tail reading of
`docs/spec/generation-method-v1.md` G5.3b rather than G5.1's fill. A
null rung INSIDE the two boundaries keeps the meaning above.

---

<!-- r1: the roles; empty; numeric_unrepresentable -->

## 6. The roles, one section each

There are **fifteen** roles. In the order section 5.2's rules test
them, they are `empty`, `identifier`, `numeric_unrepresentable`,
`constant`, `binary`, `datetime`, `count`, `continuous`,
`categorical`, `time_of_day`, `affixed_number`, `long_tail_labels`,
`joined_numbers`, `numbers_with_labels`, `free_text` — fifteen roles
in fourteen rules,
because `count` and `continuous` are decided by one rule that then
chooses between the two. `joined_numbers`, like `identifier`, is
reached only where the person declared the column and never from the
values (section 6.15). This is the same fifteen the axis table of section 5.2 carries,
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

**Invariant U4.** This role is a nothing-publishing column, so every
key of `missing_by_source` names a member of the published vocabulary
and no spelling of the table stands there, the two absence counts stand
inside N3's upper bound, and every `sentinel_verdicts` entry has
`candidate == "(withheld)"` (N3, V2, C6-126).

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
LEVELS. Their FIVE shared keys are specified once here; sections 6.4
and 6.5, section 6.6.1, and the section for `long_tail_labels` state
only what each adds or restricts. The five are the labels publication
class, and the forbidden-key matrix admits `levels` on no other role.

**THE FOURTH SHARED KEY IS `shape_forms`, AND IT STANDS ON ALL FOUR**
because whether a label role holds levels back is a fact about the
FLOOR and not about the role. Section 6.11's matrix is the authority
on where it stands; section 7.9 states what it holds.

**THE FIFTH IS `suppressed_numbers`, AND IT STANDS ON ALL FOUR FOR THE
SAME REASON** (plan P4-D301). Whether the labels a floor holds back are
WORDS or NUMBERS is a fact about the table, not about the role, and a
column whose rare values are numbers loses their scale entirely when
the pool says only how many there were: 100 `alpha`, twenty `100` and
ten each of 200 to 209 at a floor of eleven publishes one number, and
its twin wrote 95 to 105 — a numeric mean of 100 where the table has
187.083333 and a spread of 3.027650 where it has 39.033017, with both
files passing every check, because until this key no published fact
spoke of the pool at all.

| key | JSON type | meaning |
|---|---|---|
| `levels` | array of level entries | the published labels and their counts, section 6.3.1 |
| `suppressed_levels` | integer ≥ 0 | how many labels the floor held back |
| `suppressed_rows` | integer ≥ 0 | how many rows those held-back labels covered in total — the POOLED TOTAL, and the only size of them this format publishes |
| `shape_forms` | object | the census of WRITTEN FORMS the column's cells wore, section 7.9; REQUIRED on all four label roles, written even when empty |
| `suppressed_numbers` | object | the SCALE of the held-back cells that read as numbers, section 6.3.3; REQUIRED on all four label roles, written even where it says nothing |

The floor named throughout this section is `small_cell_floor`, the
setting of section 4.4. Every rule below that reads it is written as
"at least the floor" or "below the floor", so each binds at whatever
value the document carries; at a floor of one the second half is the
empty range, so a description written at that floor holds nothing back
at all. Invariant S13 states that as a rule and lists every field it
reaches — this section's `suppressed_levels`, `suppressed_rows` and
`variants_withheld` among them.

**THE HELD-BACK LABELS ARE PUBLISHED AS A POOL** (owner ruling of
2026-09-17, item 2, option A; plan P4-D201). How many labels the floor
held back, and how many rows they covered together — and no size of any
one of them. Until that ruling a sorted array `suppressed_level_counts`
gave each size; it is withdrawn, and a document carrying it is refused
as carrying a key this format does not have.

What the pool still lets a reader work out, stated rather than waved
away (repair pass of 2026-09-17): every held-back label covers at least
one row, so where `suppressed_rows` is less than twice
`suppressed_levels` at least `2 * suppressed_levels - suppressed_rows`
of them are provably single rows, and where `suppressed_levels` is 1
that one label's size is the pool itself. **THAT WHOLE BAND IS CLOSED**
(owner ruling of 2026-09-17, item 5; plan P4-D231, widened by P4-D239
after the final review of 2026-09-18; invariant B4b): where the rows
come to fewer than twice the levels a count of one is FORCED, and no
description carries such a pool any more — the cells of every held-back
level are counted as missing instead. Three one-patient sites among
2,000 rows published three levels over three rows, which can only be one
and one and one; the first writing of the ruling closed only one label
on one row and left that shape standing. A pool whose rows reach twice
its levels forces nothing about any one of them — four labels over ten
rows leaves every one of them free to cover two or more — and that pool
still stands. Its remainder is a count about unnamed groups of the kind
`n_distinct_by_occurrences` publishes for the columns that carry it
(U3, I2 and F2), and P4-D231 puts the wider readings to the owner.

#### 6.3.1 A level entry

An object with exactly these FIVE keys. A loader refuses an entry that
carries any other key, or that is missing one of these, naming the key
and the column.

| key | JSON type | meaning |
|---|---|---|
| `label` | string | the published label, as a FOLDED identity: trimmed and case-folded |
| `count` | integer ≥ 1 | how many present rows carry this folded identity |
| `shape_form_cells` | integer ≥ 0 | how many of those rows wrote the label in the label's own WRITTEN FORM, section 7.4.8 |
| `variants` | object | exact spelling → count, for every spelling of this label that cleared the floor |
| `variants_withheld` | multiplicity map | how many different spellings of this label covered one row, two rows, … below the floor |

Section 7.4 specifies `variants` and `variants_withheld` in full: what
their keys hold, what a value means, where the two keys may and may not
appear, and invariants W1 to W7. Section 7.4.8 specifies
`shape_form_cells` and invariant W8. Section 5.3 fixes the form of a
multiplicity map.

#### 6.3.3 The scale of the held-back numbers

An object with exactly these TWO keys. A loader refuses a block that
carries any other key inside it, or that is missing one of these.

| key | JSON type | meaning |
|---|---|---|
| `n_cells` | integer ≥ 0 | how many cells of the held-back levels read as numbers — nought where the block says nothing |
| `mean` | number or null | the arithmetic mean of those cells |

**THE POPULATION SPREAD THAT STOOD BESIDE THEM IS WITHDRAWN, by the
owner's decision of 2026-09-21 (plan P4-D302), and this section is
written from that decision rather than amended into it.** The landing
of 2026-09-21 published a cell count, a mean and a population spread.
A mean and a spread are TWO equations over the pool's values, and two
equations over a pool packed as closely as its own grid allows leave
ONE arrangement: the reproduction ledger K-2B-50 is measured on
published a spread of 2.8722813232690143, which is exactly
`sqrt((10 × 10 − 1) / 12)`, the smallest a pool of ten distinct whole
numbers can have — so its ten held-back values came back as 200 to 209
by arithmetic from the description. A mean alone is ONE equation over
as many unknowns as the pool has different values.

**WHAT IT COSTS IS STATED WHERE IT IS PAID.** Method G12.12's window
was drawn from the published spread; it is drawn from the column's own
published magnitudes instead, and NO CHECK ANYWHERE now says anything
about how far apart a file's held-back numbers lie. The owner was told
this in those words and accepted it: statistics improve, verification
weakens.

**WHAT MAKES THESE TWO SAFE TO PUBLISH IS THAT THEY ARE TAKEN OVER A
GROUP**, and that is asked rather than assumed. The producer asks
`parsing.census_nameable` with `n_cells` as the one count it would
print and the column's `n_numeric` as the population a reader can
subtract it from, at the document's own floor; the loader asks the same
question of the same two numbers as invariant B4d. So the pool reaches
`parsing.census_floor`, and so does whatever is left of the column's
numbers once the pool is taken off it. A pool of one cell would BE that
cell's value written under the name `mean`; a pool leaving one
published numeric cell behind hands that cell over by subtraction. Both
are refused.

**AND ONE PRODUCER OBLIGATION, WHICH THE LOADER CANNOT RE-ASK: THE
PUBLISHED MEAN MUST LEAVE THE VALUES ROOM TO MOVE.** The census rule
above asks whether the pooled COUNT names a group. This asks whether
the MEAN names a value, and it asks it by counting.

**THE COUNT, EXACTLY.** Take the numbers the pool holds: `k` different
ones, standing on the grid its own values stand on — the closest two of
them stand, which is the coarsest grid the producer can read off them
and so the fewest answers — inside the places the column's width and
its sign census allow. How many SETS of `k` different places add up to
what the mean and the cell count say the pool adds up to? Choosing `k`
different places out of `n` with a fixed sum is the same question as
splitting the room the pool has above the smallest such sum into at
most `k` parts, none larger than `n − k`, and the number of those is
one coefficient of a Gaussian binomial. `taxonomy._arrangements` walks
it, checked against an exhaustive count of every subset over 980 cases
at four range sizes and seven level counts. The count is symmetric
about the middle of its own range and never falls on the way up, so the
walk folds the room to the nearer end and stops at 256 steps of it: past
that, the answer is a floor rather than the total, and a caller
comparing against a bound is answered either way.

**THE BOUND IS A THOUSAND ARRANGEMENTS** (`taxonomy.
_POOLED_SCALE_ROOM`). MEASURED, over twenty-five random pools of
distinct whole numbers at each level count, with the sizes given to the
reader and the search over every value the column's own width allows:

| held-back numeric levels | solved outright | down to four | median arrangements |
|---|---|---|---|
| 1 | 25 of 25 | 25 of 25 | 1 |
| 2 | none | none | 224 |
| 3 | none | none | 47,502 |
| 4 | none | none | 4,219,740 |
| 5 | none | none | 457,634,000 |
| 6 | none | none | 76,176,700,000 |

The level rule of six this replaces was accepted with a measured median
of 118 arrangements and two pools of twenty-five down to four answers;
a thousand is asked of EVERY pool rather than of the family's median.

**THE FOUR RULES THIS ONE REPLACES, and why each goes.** The landing of
2026-09-21 guarded the mean and the spread with four producer refusals.
All four asked one question badly.

1. **A pool of SIX held-back numeric levels or more.** The count was
   standing in for "more unknowns than equations". With one equation
   the protection is room and not arity, and the room is counted.
2. **A pool with a spread above nought.** Nothing publishes a spread,
   so there is nothing to ask. Its reason — every level of a pool is a
   different FOLDED value but different folded values can be the same
   NUMBER, so `5`, `5.0`, `05` and `5.00` are four levels and one five,
   whose mean IS what each of those cells held — is the ONE-arrangement
   case of the rule above, and is refused there.
3. **A pool standing clear of the tightest arrangement its own values
   could take.** WITHDRAWN, with the number that withdrew it. The
   tightest arrangement is what a published SPREAD names outright; a
   mean names no arrangement at all. Measured: the owner's own shape,
   ten consecutive whole numbers, leaves 429,466,368,887,745,697 sets
   of ten different whole numbers sharing its mean over the thousand
   places its column's three-figure width allows, and over the same
   twenty-five pools at each level count a family drawn AT the tightest
   arrangement leaves a median of 189, 45,757 and 6,318,400 answers at
   two, three and four levels against a loose family's 224, 47,502 and
   4,219,740. The rule bought nothing once the spread was gone.
4. **A pool fitting inside the width the column shows.** WITHDRAWN, and
   this one by proof. Method G8.3a step 3 allows no made-up number more
   figures before the mark than the widest the column publishes, so a
   SCALE wider than that was an obligation no conforming twin could
   meet. What a description now states is the MEAN, every arrangement
   stands on the grid inside that width, so a mean beyond it has no
   arrangement at all and the count above is nought. What the width
   rule still refused was a pool holding one wide value beside small
   ones — 1, 5 and 2089 beside a three-figure column, whose mean is
   698.33 — and that mean is one a twin writes exactly. Measured over
   200,000 random pools at four widths: not one had a mean the twin
   could not write and room enough to publish, while 2,915 were refused
   with a mean it could.

**WHAT THE COUNT OF LEVELS NEVER SAW, and this rule does.** A pool of
six different ONE-FIGURE numbers beside a published one-figure number
passed every one of the four rules above: six levels, a spread of 2.75,
and a looseness well past two and a half times the tightest. Six
different one-figure numbers are six of the ten there are, and the mean
says which six to within SIXTEEN answers. Measured over every pool of
one-figure numbers at every level count from one to seven, the smallest
count of surviving arrangements is ONE — a pool standing against either
end of the range its width allows is named whatever its level count.
What protects the values is ROOM, and the room is what is counted.

**THE LOADER DOES NOT RE-ASK IT**, and that is a decision rather than an
omission: how many of the held-back levels hold numbers, what grid they
stand on and how wide they were written are not published facts, and
publishing them so the loader could check them would be further numbers
about the pool — a worse trade than leaving the rule to the producer,
which is the trade invariants B4b and B4c already make for the level
pass. **What the loader LOST with the spread is named rather than
left**: invariant B4d used to re-ask that a published spread stood above
nought, which stopped a HAND-WRITTEN description carrying a pool of one
value. Nothing here stops one now. The producer refuses to write one and
the producer is the only guard.

**NOUGHT IS THE ONE STATE THIS BLOCK SAYS NOTHING WITH**, and it is
reached several ways on purpose: by a column whose held-back levels hold
no number at all, and by a column where any of the questions above was
answered no. A refusal a reader could tell apart from nought would
itself publish that the pool holds numbers and how few of them — the
count the floor exists to withhold. `mean` is `null` exactly there.

**WHAT IT STILL LETS A READER NARROW, stated rather than waved away.**
`suppressed_levels` with `suppressed_rows` pins the held-back levels'
sizes wherever the pool stands at the top of invariant B4's band, and
`n_cells` equal to `suppressed_rows` says that every held-back level
holds a number. Nothing here rests on either. What a reader is left
with is a cell count and a mean over a pool whose values have at least a
thousand arrangements on their own grid — a SET of populations and not a
point. It is not a continuum, and no rule here makes it one while the
held-back values are whole numbers. What a reader can take is the
SCALE of a group of at least `parsing.census_floor` cells: about where
those rare numbers sat. That is the same class of fact as the pool's own
two counts, and it is no wider than what the twin already gives them,
because the twin writes its made-up numbers at that mean.

**WHAT IT COSTS THE OWNER'S ACCEPTED LIMIT, measured.** Ledger K-2B-19
counts the held-back cells a twin reproduces exactly. On its committed
sweep of nineteen columns, ONE column publishes a pool under this
section, and placing that column's made-up numbers on its published mean
takes the count from 55 of 251 to 63, with the count of columns rebuilt
whole unmoved at 1 of 19. Withdrawing method G8.3c's placement puts it
back at 55, which is how that was measured. The owner is told rather
than the ceiling moved quietly.

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

**Invariant B4 (the held-back pool).** Every held-back label covers at
least one row and fewer rows than the floor, so
`suppressed_levels <= suppressed_rows <= suppressed_levels * (floor - 1)`;
at a floor of one both are therefore nought. **A pool of one row is
not refused** (owner ruling of 2026-09-17, item 2, option A; plan
P4-D201, repair pass of the same day). A pool of one row names the one
row whose value is none of the published labels, and `n_present` less
the published counts reads it whether or not `suppressed_rows` is
printed, so no key can hide it; the first writing of the ruling held
the smallest published label back beside such a pool, and that was
withdrawn because the label it held back had cleared the floor and the
twin then wrote none of it. **That limit is closed by invariant B4b
below** (owner ruling of 2026-09-17, item 5; plan P4-D231): the pool of
one is no longer written at all, because the cells that would leave it
are counted as missing.

**Invariant B4b (a pool that forces a count of one).** The labels held
back never come to fewer rows than twice their number, and never come to
exactly their number while covering fewer rows than the published levels
do: `not parsing.pool_names_a_level(suppressed_levels, suppressed_rows,
the rows the published levels cover)` (owner ruling of 2026-09-17, item
5; plan P4-D231, widened by P4-D239, bounded by P4-D271 and pinned by
its amendment of the repair pass of 2026-09-18).
Such a pool forces a count of one -- and B3 above makes that subtraction
available to every reader whether or not `suppressed_rows` is printed,
which is why no key left out could hide it. 480 `F`, 519 `M` and one `U`
at a floor of eleven said one row holds a third value, and its twin wrote
an invented label in exactly that person's row; three one-patient sites
among 2,000 rows published (3, 3), which can only be one and one and one,
and its twin wrote three single-row labels. Such a document is refused
here. The producer does not write one: every cell of the held-back level
is counted as MISSING, spelled as nothing, so the description is that of
the table with those cells blank, the twin writes a blank in those rows,
and no label that clears the floor is ever held back to hide one.

**Invariant B4c (a sibling total that leaves one row).** The four totals
of 6.2 that say what a column's present cells READ AS -- `n_numeric`,
`n_not_numeric`, `n_out_of_range` and `n_contradictory` -- are
subtractable exactly as `n_present` is, one class at a time, and B4b
cannot see them: **no such total, less the published levels that read
that way, is exactly one** (Codex blocker 2 of the extra round,
2026-09-18; plan P4-D261). The question is
`parsing.census_names_one_row`, asked of the class's own held-back rows
as a POOL and of the pair together -- one call, both of the rule's
readings, no second copy of it. **A class NO published level counts into
is read too**, and this clause said the opposite until the skeptic's pass
of 2026-09-18 measured it. The pair alone answers nothing there, on the
reasoning C6-131b gives: a census that covers none of a total leaves a
reader nothing to subtract. But a class whose every level the floor held
back is exactly that shape, and the count of one survived in all three of
the classes a column of words has no published level for. **Measured
then**, at a floor of eleven: `alpha` and `beta` a hundred rows each,
`gamma` six, `delta` five and ONE further cell. With `77` the block
published `n_numeric` 1 beside two published WORDS and `n_missing` 0, so
exactly one row of the column reads as a number and its value is
withheld; with `1e999` the same of `n_out_of_range`; with `(+5)` the same
of `n_contradictory`, which names the accounting notation ONE
individual's cell was written in. A pool of one is the rule's FIRST
reading and needs no census beside it, so the class's own held-back rows
are handed in as that pool. **Measured before this clause:** `alpha` and `beta` a hundred rows
each, `1` five rows, `2` six rows and `gamma` one row, at a floor of
eleven. The pool was three levels over twelve rows -- far outside B4b's
forced band, and every printed count cleared the floor -- while
`n_not_numeric` 201 less the two published words' 200 said the withheld
WORD level occurs once. The twin wrote one `group-1` and both files
passed every executable check. The producer counts the cells of every
held-back level of that class as MISSING instead, by the same pass that
serves B4b, so it writes no document this refuses; one pass suffices,
because a class that fires gives up fewer rows than twice its levels and
so cannot pull the whole pool into B4b's band. **A label whose class the
plain and the decimal-comma grammars disagree about takes the check off
that column altogether**, because a loader that guessed the declaration
wrong would refuse a description nobody had edited.

**What B4b deliberately does NOT refuse**, and plan P4-D231 puts both to
the owner with what each was measured to cost on the full suite. (a) One
level over MORE than one row: the pool is still that level's own count,
and the number is below the floor by construction, so a `region` column
of four places beside seven `outlying` rows says seven people share a
value it will not name. Refusing it moves 53 witnesses and turns a
`constant` column whose one value is below the floor into an EMPTY
column. (b) A pool that does not reach `parsing.census_floor`: that is
the one disclosure rule asked of the subtraction, and it empties the
held-back machinery P4-D201 built wherever the floor is high -- 66
witnesses, three frozen cases unwritable, and the rare VALUES of every
small column at a raised floor turned into holes. A pool of ten rows
over four levels says nothing about any one of them. The standing limit
of 6.3 above -- that where `suppressed_rows` is less than twice
`suppressed_levels` some of them are provably single rows -- stays a
stated limit for the same reason: it is true of every ordinary long
tail, and the demonstration's `note` holds back 182 levels over 217
rows.

**What the width does NOT let through** (plan P4-D271 as amended by the
repair pass of 2026-09-18). The exception above is a width, and a width
would otherwise let the band's sharpest point through wherever the pool
is wide enough. `suppressed_levels` equal to `suppressed_rows` says
every held-back level covers exactly ONE row -- a count of one for each
of them, read off two published numbers -- so such a pool is refused
whenever it covers fewer rows than the published levels do, whatever the
width says. Measured at a floor of eleven: 100 `NORTH` and 100 `SOUTH`
beside 120 site codes written once each published (120, 120) and no
missing cell, and 600 and 600 beside 700 such codes published (700, 700);
both cleared the width and both are refused now. A pool that is the
column rather than an exception beside it is still not refused: 780
unique codes over 780 rows beside one published value of twenty are
pinned too and still stand, because the pool covers more rows than the
published levels do.

**AND `n_present`/`n_missing`, WHICH IS WHERE THIS RULE SENDS THE CELLS,
IS ITSELF FLOOR-FREE.** Section 11 lists the presence split among the
universal counts that are floor-free on every role, and it is not asked
`parsing.census_nameable` anywhere. So a column of 1,977 `NORTH`, 11
`SOUTH` and ONE one-row site at a floor of eleven publishes `n_present
1988` and `n_missing 1` against `n_rows 1989`, and its twin holds one
blank cell -- naming the one record whose site stands outside the
published labels. That is the exception this format carries knowingly:
publishing that a row is MISSING is ruling 5's own consequence, and
asking the disclosure rule of the presence split would change every
column block this format writes rather than repair this one. Plan
P4-D271 records the measurement and puts the question to the owner.

**Invariant B4d (a pooled scale is taken over a group).** The block of
6.3.3 speaks only of a group: `suppressed_numbers.n_cells` is nought,
or `parsing.census_nameable([n_cells], [n_numeric], floor)` holds — the
pool reaches `parsing.census_floor` and so does whatever the pool
leaves of the column's numbers. `mean` is written exactly where
`n_cells` is above nought and is `null` everywhere else. **The clause
about a published SPREAD is gone with the spread** (owner's decision of
2026-09-21, plan P4-D302): B4d used to re-ask that a written spread
stood above nought, which stopped a hand-written description carrying a
pool of one value whose mean IS that value, and no spread is published
for it to ask about. That guard is the producer's alone now, and 6.3.3
says so. Inside a compound column's label
half the `n_numeric` beside it counts the OTHER half's numbers, so it
is not a population this pool is subtractable from and the second
clause is not asked there; the first still is. Measured at a floor of
eleven: a pool of three numeric cells publishes a mean that is three
people's values averaged, and a pool of one publishes that person's
value under another name.

**Invariant B5 (the floor).** Every `entry.count` is at least the floor.

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

`levels`, `suppressed_levels` and `suppressed_rows` are
EXACT-OBSERVABLE: the twin writes each published label at exactly its
count and invents exactly `suppressed_levels` neutral labels covering
exactly `suppressed_rows` rows together, at the sizes the generation
method reads off that pooled total (method G8.3), each below the floor.

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

**Added keys: twenty.**

| key | JSON type | permitted values | meaning |
|---|---|---|---|
| `format` | string | one of the TWENTY members of the table below | the parser family that read the REAL file |
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
| `datetime_separators` | object | `lower_t`, `space`, `upper_t` or `(withheld)` → count | how many parsed cells wrote each mark between the day and the clock, under the floor; `{}` where `resolution` is not `datetime` |
| `all_at_midnight` | boolean | — | `true` where every parsed cell of a datetime column names exactly midnight on its own wall clock, the parsed cells reach the floor, and on the `utc` clock no offset is pooled |
| `n_at_midnight` | integer ≥ 2, or `null` | — | how many parsed cells name exactly midnight on their own wall clock, where at least the floor — never fewer than two — did and at least that many did not, or every parsed cell did and they reach that floor; `null` otherwise, a real nought included (landing 2b.6) |
| `date_field_widths` | object | `padded`, `unpadded`, `first-padded`, `second-padded`, `first-field-padded`, `first-field-unpadded`, `second-field-padded` or `second-field-unpadded` → count | how many parsed cells wrote each width convention — a JOINT word where both month and day are below ten, the word of the one field that showed otherwise — counted only over the cells that could show one, a one-field count folded into the joint word agreeing with it (P4-D139), under the disclosure rule of P4-D131; `{}` on a member whose fields are of fixed width, and where the census is withheld whole (landing 2b.6) |
| `month_name_styles` | object | one of the THIRTY-SIX joint style words → count | how many parsed cells wrote a month NAME in each joint style — case, length, field mark, and whether a comma followed the day — a name of May counted under the length its column's other cells of that case, mark and comma wrote, or as `either` where none did (P4-D133, P4-D139), under the disclosure rule of P4-D131; `{}` outside the two textual members, and where the census is withheld whole (landing 2b.6) |
| `quarter_marker_case` | object | `upper` or `lower` → count | how many parsed cells wrote a quarter's marker as `Q` and how many as `q`, under the disclosure rule of P4-D131; `{}` outside `year-quarter`, and where the census is withheld whole (landing 2b.6) |
| `zulu_case` | object | `upper` or `lower` → count | how many parsed cells wrote a zulu offset marker as `Z` and how many as `z`, under the disclosure rule of P4-D131; `{}` unless `utc_offsets` NAMES `Z`, and where the census is withheld whole (landing 2b.6) |

**Eight closed vocabularies stand in that table** — `format` with
TWENTY members, `resolution` with FOUR, `time_precision` with SIX,
the `datetime_separators` names with THREE, and the four written-form
vocabularies landing 2b.6 added: `date_field_widths` with EIGHT,
`month_name_styles` with THIRTY-SIX, `quarter_marker_case` with TWO and
`zulu_case` with TWO — and the first three are
each written again below inside a table that BINDS it: the
twenty formats are the rows of the next table, where D1 fixes each one's
resolution; the four resolutions are the rows of the canonical-forms
table, which fixes what each one's instants are written as, and of D6's
table; and the six precisions are named in D6's table, which admits no
pair outside it. The three separator names are bound by D12, which
refuses any other key. A closed list copied with nothing binding the copies
is a list two implementations can read differently; each copy here is
the subject of a rule, so a member missing from one of them is a defect
that rule catches. Section 14 indexes all four.

##### The format vocabulary, its readings and its resolutions

Twenty members, each with the shape it reads and the `resolution` it
requires:

| `format` | reads | `resolution` |
|---|---|---|
| `iso-date` | `YYYY-MM-DD`: a four-digit year, two-digit month and day, hyphen-delimited, exactly ten characters | `date` |
| `month-first-date` | a slashed month-first date: a one- or two-digit month, a one- or two-digit day, a four-digit year, slash-delimited | `date` |
| `day-first-date` | a slashed day-first date: a one- or two-digit day, a one- or two-digit month, a four-digit year, slash-delimited | `date` |
| `textual-day-first-date` | a one- or two-digit day, a month NAME, a four-digit year, delimited by a space or a hyphen — the same one both times, and no field carrying space of its own | `date` |
| `textual-month-first-date` | a month NAME, a one- or two-digit day with an optional trailing comma, a four-digit year, delimited by a space or a hyphen — the same one both times, and no field carrying space of its own | `date` |
| `dotted-month-first-date` | a dotted month-first date: a TWO-digit month, a TWO-digit day, a four-digit year, dot-delimited. Padded, and the one family that is — C6-22 says why | `date` |
| `dotted-day-first-date` | a dotted day-first date: a TWO-digit day, a TWO-digit month, a four-digit year, dot-delimited. Padded, and the one family that is — C6-22 says why | `date` |
| `two-digit-month-first-date` | a slashed month-first date whose year is TWO figures, read at the pivot C6-D8P fixes | `date` |
| `two-digit-day-first-date` | a slashed day-first date whose year is TWO figures, read at the pivot C6-D8P fixes | `date` |
| `dotted-two-digit-month-first-date` | a DOTTED month-first date whose year is TWO figures, read at the pivot C6-D8P fixes. Padded, for C6-22's reason: `1.2.24` is a version identifier | `date` |
| `dotted-two-digit-day-first-date` | a DOTTED day-first date whose year is TWO figures, read at the pivot C6-D8P fixes. Padded, for C6-22's reason | `date` |
| `compact-date` | `YYYYMMDD`: exactly eight digits and nothing else | `date` |
| `slashed-iso-date` | `YYYY/MM/DD`, fields padded | `date` |
| `iso-month` | `YYYY-MM` | `month` |
| `year-quarter` | `YYYY-Qn`: a four-digit year, a hyphen, the letter Q in either case, and a quarter digit `1` to `4` | `quarter` |
| `iso-datetime` | an `iso-date`, one separator — the letter T in either case, or a space — then a clock `HH:MM` or `HH:MM:SS`, an optional fractional part, and an optional UTC offset | `datetime` |
| `iso-mixed` | the joint ISO family reading below | `datetime` |
| `month-first-datetime` | a slashed month-first date, one space, then a clock in one of the two forms the `time_of_day` role fixes | `datetime` |
| `day-first-datetime` | a slashed day-first date, one space, then a clock in one of the two forms the `time_of_day` role fixes | `datetime` |
| `slashed-iso-datetime` | a `slashed-iso-date` (`YYYY/MM/DD`, fields padded), one space, then a clock in one of the two forms the `time_of_day` role fixes (landing 2b.3) | `datetime` |

**C6-D8P (the century a two-figure year is read into).** A year
written with two figures does not carry its century. `00` to `68` are
read as `2000` to `2068`; `69` to `99` as `1969` to `1999`. This is the
POSIX pivot, chosen because it is the convention the tools around this
one already use, and it is a GUESS about somebody's data rather than a
fact their file states — so every column read under either two-figure
member carries note NF42, which says the rule and says what it costs a
table reaching further back than 1969.

**Invariant D1 (resolution follows format).** A document's `format` and
`resolution` are one row of the table above. The binding is exact and
total: every member of the format vocabulary appears exactly once, a
document whose pair is not a row does not conform, and a loader refuses
it naming both the format and the resolution it found. Totality is the
point of writing all twenty rows out. A partial binding — one that
named the resolutions of some members and left the rest unbound — would
let a document pair `format: iso-date` with `resolution: datetime` and
be refused by no rule at all, so a whole-date source could be routed as
a datetime column with nothing in the document saying so.

**An `iso-datetime` cell's fractional part is read and discarded**, the
profile recording whole seconds; how many digits the source wrote is
`subsecond_digits`, and that a column wrote any is `time_precision`.
The two fields are where that notation is recorded, and the published
instants are not. `all_at_midnight` is the one fact that reads the
discarded fraction: a cell counts as midnight only where every
fractional digit it wrote is zero.

**C6-D8N (the month-name vocabulary, closed).** The two textual
members read a month NAME, and the names they read are these and no
others: `jan`, `feb`, `mar`, `apr`, `may`, `jun`, `jul`, `aug`, `sep`,
`oct`, `nov`, `dec`, and the full words `january`, `february`, `march`,
`april`, `may`, `june`, `july`, `august`, `september`, `october`,
`november`, `december`. Matched after trimming and case folding, so
`MAR`, `Mar` and `mar` are one name.

THE ABBREVIATION IS EXACTLY THREE LETTERS. `Sept` is not read, and
that is a limit rather than an oversight: a vocabulary left open is a
vocabulary two implementations spell differently, and a column of
`17 Sept 2024` read as dates by one tool and as text by another is
worse for a person than either answer alone. A column this vocabulary
does not reach is read as text, exactly as it was before these members
existed.

ENGLISH ONLY, for the same reason. A name read in one language and not
another gives one table its dates and the table beside it free text.

**C6-22 (the unpadded widening).** Six families accept one- or
two-digit month and day fields: `month-first-date`, `day-first-date`,
`month-first-datetime`, `day-first-datetime`,
`two-digit-month-first-date` and `two-digit-day-first-date`. The first
four are a one- or two-digit month and day, a four-digit year, and the
slash delimiter; the last two are the same with a TWO-figure year. The
textual pair accepts a one- or two-digit day beside a month NAME.

**THE DOTTED PAIR IS PADDED, AND IT IS THE ONE FAMILY THAT IS** (plan
P4-D15). `1.2.2024` is how a version identifier is written and, character
for character, how an unpadded dotted date would be written — so an
unpadded dotted grammar routed a column of version numbers into the
datetime role, published endpoints and a ladder over them, and handed
back a twin of ISO days. Nothing in such a cell settles which it is.
The padding does, well enough to be worth a rule: `17.03.2024` is how
the places that write dotted dates write them, and no version is
written `01.02.2024`. So `dotted-month-first-date` and
`dotted-day-first-date` require both fields at exactly two figures, and
an unpadded dotted date is read as text.

`slashed-iso-date` stays fully padded and `compact-date` stays exactly
eight digits, so no family overlaps another, and no fixed
character-count rule stands over the widened families.

**The day-first reading rule.** `--day-first` tells the profiler that
dates in this table are day-first wherever the day and month are BOTH
written as numbers — the slashed pair, the slashed stamp pair, the
dotted pair and the two-figure-year pair (plan P4-D15) — and the
settings key `day_first` (section 4.4) records that the declaration was
made. It does NOT reach the textual pair, whose order a month name
settles, so a declaration changes nothing there.
Its mechanics are NOT a bare order swap, because a swap can silently
reverse a column against its own evidence: with ninety-nine ambiguous
slashed cells and one cell only the month-first reading can parse, a
swapped table lets the day-first reading clear the line first and reads
the whole column backwards, counting the one contrary cell — the
column's only evidence — as unparsed. The rule is therefore
evidence-first: where the option is given and a column's ambiguous
numeric cells are in play, BOTH readings of that column's pair are
counted, and the reading that parses strictly more cells wins whatever
the declaration said; the
declaration decides only a count tie. Which reading a column took is
that column's own `format` and is recorded nowhere else. Absent the
declaration the ordinary reading stands: the vocabulary is tried in its
own fixed order, month-first before day-first, and the first member
that clears the line wins.

**DF-P (producer).** Both readings of the column's own pair were
counted, the reading used is the one that parsed strictly more cells,
and the declaration decided only a count tie.

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
are exact, and the disclosure rule is asked of them BEFORE they are
counted rather than of the mapping afterwards (plan P4-D250). This
paragraph said no floor governed them, because with a two-member space
beside the published parsed total a pooled remainder is recoverable by
subtraction, so a floor would withhold nothing. The arithmetic holds
and the conclusion did not: it is an argument against POOLING the rare
form, and the count of that form is itself the disclosure — 118 ISO
dates beside one `2024-07-01T00:00:00` published `{"iso-date": 118,
"iso-datetime": 1}` at a smallest group size of eleven, and the one is
that row. A form fewer cells than `census_floor` wrote is counted into
the commonest form, as ruling 6 of 2026-09-17 counts a rare spelling
into the commonest spelling, and the column is then published WHOLLY in
that form: its cells written in it, its `format` named as it, and its
`resolution`, `time_precision` and `datetime_separators` following from
the rewritten cells, so that no dependent count hands the absorbed
cells back by subtraction. A count of nought remains permitted and
names nobody.

**Invariant RM1.** `resolution_mix` keys are exactly the set C6-25
permits for the column's own `format`.

**Invariant RM2.** `resolution_mix` values sum to
`n_present - n_unparsed`. On an `iso-mixed` column the chosen format IS
the joint reading, so `n_unparsed` there counts the cells that read
under neither ISO member.

**Invariant RM3.** Where more than one form carries cells, every
non-nought `resolution_mix` count is at least `census_floor` of the
smallest group size. A census naming ONE form is exempt: its count is
`n_present - n_unparsed` itself, which the block already prints, so it
cuts the column nowhere.

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

**C6-25a (`datetime_separators`).** Every datetime block carries
`datetime_separators`, a mapping from the name of the mark a parsed
cell wrote between its day and its clock to how many cells wrote it:
`upper_t` for the letter T, `space` for a space, `lower_t` for the
letter t. A name is published only where its count reaches
`parsing.census_floor` -- the floor, and never fewer than two (plan
P4-D220) -- and **a mark below that line is counted into the commonest
named mark** (plan P4-D222; stage 2 closed by the owner rulings of
2026-09-17, as ruling 4 counts missing-value words below a raised floor
as absent): the map describes the column with its rare marks written the
commonest way. Where no mark reaches the line EVERY mark pools under
`(withheld)` -- except over more clock-writing cells than two marks can
hold below the line, where a pool would say all three were written, and
there the map is `{"upper_t": N}`. The marks are a closed vocabulary, and
a pool beside a named mark would say that a rarer mark was not nought, so
none stands there. Plan P4-D220 pooled the whole map where any mark fell
short, and one `T` among 5,000 spaces made the twin write `T` on 4,998
rows. Only a cell that writes a clock is counted, so the map
is `{}` where `resolution` is not `datetime`, and the whole-date cells
of an `iso-mixed` column are left out. A `month-first-datetime`,
`day-first-datetime` or `slashed-iso-datetime` cell counts as `space`,
the one mark its reader takes. D12 and D13 hold the map.

**C6-25b (`all_at_midnight`).** Every datetime block carries
`all_at_midnight`. It is `true` only where `resolution` is `datetime`,
the parsed cells number at least `small_cell_floor`, and every parsed
cell names exactly midnight on its own wall clock: clock `00:00`,
seconds `00`, every fractional digit zero. A whole-date cell of an
`iso-mixed` column counts as midnight. On the `utc` clock it is asked of
the same local cell text, and only where `utc_offsets` pools no offset
under `(withheld)` (landing 2b.3): a column wearing `+01:00` in winter
and `+02:00` in summer at midnight is a column at midnight. It is
`false` everywhere else. D14 holds the flag.

**C6-25c (`n_at_midnight`, landing 2b.3).** Every datetime block
carries `n_at_midnight`: how many parsed cells name exactly midnight on
their own wall clock, by C6-25b's test, published where at least
`small_cell_floor` — never fewer than two — did and at least that many
did not, or where every parsed cell did and they number at least that
floor; `null` everywhere else, a real nought included, and including
every column whose `resolution` is not `datetime` and every `utc`
column pooling an offset. NOUGHT IS NOT A VALUE OF THIS FIELD (landing
2b.6): a reader who can tell a published nought from a suppressed count
of one has been told that count, so the two are ONE absent state, and a
count of one — or one leaving a single value off midnight — is never
published. It is every parsed
cell exactly where `all_at_midnight` is `true`. D15 holds the count.

**C6-25d to C6-25g (how the dates were WRITTEN, landing 2b.6).** Every
datetime block carries four further censuses. They exist because the
owner reversed decision 5 on 2026-09-15: a twin datetime cell is
written in the member that read the real column rather than in ISO, and
a member alone does not fix a spelling. `month-first-date` is written
`03/17/2024` by one export and `3/17/2024` by the next;
`textual-day-first-date` covers `17-MAR-2024`, `17 Mar 2024` and
`17 March 2024`; `textual-month-first-date` makes the comma of
`Mar 17, 2024` optional; `year-quarter` reads either case of its
marker; and the zulu reading folds `z` onto `Z`. Each census counts
FORMS and never a value, and each is held to THE DISCLOSURE RULE OF
PLAN P4-D131, `parsing.census_nameable` asked with no pool, because a form used by one
row describes how THAT row was written: every named count reaches
`small_cell_floor` and never falls below two; NOTHING IS POOLED, since
a census of a handful of forms cannot pool without naming what it pools
— `{"upper": 399, "(withheld)": 1}` named the one row that wrote `z`;
and the cells the named counts leave over of the total they count over
are none or at least that many — `n_present - n_unparsed` for the names
and the quarter's marker, `utc_offsets["Z"]` for `zulu_case`, and for
`date_field_widths` the cells that could SHOW a width, which the block
does not publish (plan P4-D139): a date whose two fields are both ten or
more wrote no convention, so it is no form a reader could learn by
subtraction. A census failing any of the three is published `{}`, which
is also what a column that cannot show the convention publishes.
*Amended by the review of 158c811:* this paragraph said each census was
held to `small_cell_floor` with a `(withheld)` pool exactly as
`datetime_separators` is. *Amended again by its skeptic (plan P4-D139):*
it counted the widths' remainder over `n_present - n_unparsed`, and one
`12/25/2019` among 244 dates written `m/d/yyyy` withheld the census whole
and had 212 of the twin's 245 cells written padded.

- **C6-25d (`date_field_widths`).** Keys `padded`, `unpadded`,
  `first-padded`, `second-padded`, `first-field-padded`,
  `first-field-unpadded`, `second-field-padded`, `second-field-unpadded`.
  ONE WORD PER CELL AND NOT ONE PER FIELD: on a column half written
  `%m/%d/%Y` and half `m/d/yyyy`, no real cell mixes the two, and two
  independent censuses would let a twin write about half its eligible
  cells as `03/5/2024`, a style no row used. On a cell whose two numeric
  fields are BOTH below ten, `padded` means both were padded, `unpadded`
  that neither was, and `first-padded` and `second-padded` that the
  first or the second alone was. On a cell where only ONE field is below
  ten, the word names that field — `first-field-padded` and so on — in
  the member's own field order (plan P4-D132): counted under the bare
  `padded` or `unpadded` instead, as the first revision did, a column
  written `m/dd/yyyy` published words its twin spent on cells showing
  both fields, and 106 of 400 twin cells were written `5/4/2024` or
  `08/28/2022`. AND A ONE-FIELD COUNT IS FOLDED INTO A JOINT WORD
  (plan P4-D139): a cell showing one field is consistent with the two
  joint words that pad that field its way, and it is counted under
  whichever of them the column's cells showing both fields wrote more
  often — `padded`, `unpadded`, `first-padded`, `second-padded` order on
  a tie — keeping its one-field word only where no cell wrote either.
  Counted apart, those classes held a twin to how many of its dates
  happen to fall past the ninth or in October to December: 150 dates
  written `m/d/yyyy` at a floor of eleven published
  `second-field-unpadded: 14`, and a twin holding fewer such dates failed
  its own check. Counted over the cells that could SHOW a width, so the
  total is at most the parsed cells and is usually fewer. `{}` on every
  member of fixed field width; on the two textual members only `padded`
  and `unpadded` can appear, the month there being a name and the day
  the one field. D17 holds it.
- **C6-25e (`month_name_styles`).** Keys are the joint word
  `<case>-<length>-<mark>-<comma>` over `upper`/`title`/`lower`,
  `abbreviated`/`full`/`either`, `space`/`hyphen` and `comma`/`no-comma`
  — 36 in all. Joint for C6-25d's reason: a hand-entered column mixing
  `17-MAR-2024` with `17 Mar 2024` carries its case and its mark
  together, and independent censuses would invent `17 MAR 2024`. A cell
  whose month is MAY shows no length, its two written forms being one
  word, and is counted with the length `either` (plan P4-D133): it still
  shows its case, its mark and its comma. Counted under no key instead,
  as the first revision did, a column of `17-MAY-2024` published `{}`
  and its twin was written `25 May 2024`. AND A NAME OF MAY IS FOLDED
  INTO A LENGTH (plan P4-D139): it is counted under the style of the
  same case, mark and comma its column's other cells wrote more often —
  `abbreviated` on a tie — and keeps the length `either` only where no
  other cell wrote that case, mark and comma. Counted apart, one
  `15-MAY-2023` among 269 `DD-MON-YYYY` dates was a count of one, the
  census was withheld whole, and the twin was written `20 Jan 2022`.
  `{}` outside the two textual
  members, and on `textual-day-first-date` only the eighteen `no-comma`
  styles can appear: a comma there would follow a month name, which no
  member of this contract reads. D18 holds it.
- **C6-25f (`quarter_marker_case`).** Keys `upper`, `lower`. `{}`
  outside `year-quarter`. D19 holds it.
- **C6-25g (`zulu_case`).** Keys `upper`, `lower`. `{}`
  unless `utc_offsets` NAMES `Z`: the case census counts a subset of
  the cells carrying one offset, so publishing it beside a POOLED `Z`
  would hand back the count the pool exists to withhold — the same
  contradiction review item P1-R1-F10 found for the endpoint offsets.
  It is a census of its own rather than a second `utc_offsets` key,
  because `z` as a key would count as a second OFFSET and trip D5 and
  the shared-clock reading when it is one offset written two ways. D20
  holds it.

**Two are EXACT-OBSERVABLE IN THEIR KEY SET and two are EXACT, and that
is stated here rather than left to be discovered (plan P4-D134).** What a
file is held to on `date_field_widths` and `month_name_styles` is every
convention the description names, each on at least a floor's worth of
that file's own cells — counted on those cells as the producer counts
and folds them, not read off the file's own floored description, and a
one-field width or an `either` name owed on a floor's worth or on every
cell of that kind the file holds, whichever is fewer (plan P4-D139) —
and no convention the description does not name beyond the cells the
named counts leave over of their total. Those two
are NOT held to the counts, and the reason is the same fact that makes
the counts interesting: whether a cell can SHOW a width or a name's
length depends on its own value, so how many cells of a file could carry
one is a fact about that file's values, and a twin whose interior
instants fall a day either side of the real ones carries a different
number of them. A count check would accuse a faithful twin. The case of
a quarter's marker and of a zulu marker is shown by EVERY cell those
censuses count over, and a twin writes exactly the published number of
each, so `quarter_marker_case` and `zulu_case` are held COUNT FOR COUNT:
held only as a set, a file with eighty lower-case and 320 upper-case
markers turned the other way round met both. The validation method
states the measurement.

**The census and both midnight facts are EXACT-OBSERVABLE** (plan
P4-D39, added after the freeze; held to a file since landing 2b.3). A
file's own description, made by the same producer, is compared with the
published census, with the statement where it is published `true` and
with the count where it is above nought. What they buy is code meeting
the same spelling on the twin as on the real table, a date-only field
that stays a date, and a column partly at midnight that stays so.

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
other than `(withheld)` maps to a count at least the floor, and never
below two. **A `(withheld)` count stands ALONE**: it is the whole map,
whose one count is the total D2 already publishes, and it is admitted at
any size and at any floor. **Amended by plan P4-D220 and again by plan
P4-D222 (stage 2 closed by the owner rulings of 2026-09-17).** The rule
named an offset at the settings floor, so at the then default floor of one a
row written at `+01:00` beside 399 at `Z` was named, and at a floor of
eleven the pool beside `Z` was that one row. P4-D220 folded a pool below
the line into the smallest named offset, and one `Z` among `+01:00` and
`+02:00` then folded `+01:00` in and the twin wrote half the column with
no offset. The producer now counts an offset below the line into the
commonest named offset and reads those values at it -- the clock the
column is published on, its ends and their offsets follow
(`parsing.absorbed_census`) -- and where no offset reaches the line the
map is one pool, beside which the clock is `utc` and both ends are held
back.

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
P4-DATE5-F4): the slashed stamp members -- two then, three since
landing 2b.3 -- reach `datetime` resolution, so a reader that took the
four-member list would accept
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
  `YYYY-MM-DD`, a mark, then `HH:MM` has no seconds field to carry anything else; and
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

**Invariant D12 (the separator names and the floor).** Every key of
`datetime_separators` is `upper_t`, `space`, `lower_t` or
`(withheld)`. Every key other than `(withheld)` maps to a count at
least the floor, and never below two, and `(withheld)` appears only
when the pooled remainder is non-zero. **A `(withheld)` count stands
ALONE: no mark is named beside it** (plan P4-D220), and **it stands only
over a population a pool names no one in** (plan P4-D222; stage 2 closed
by the owner rulings of 2026-09-17; `parsing.census_pools`): fewer
clock-writing values than the line, or no more than the permitted marks
less one can hold below it. The permitted marks are the three names, or
`space` alone on a `month-first-datetime`, `day-first-datetime` or
`slashed-iso-datetime` column. A pool over more values than that says
every permitted mark was written, which is the state nought reaches told
apart from a count below the floor, so the producer publishes the
commonest mark there — the commonest mark THE CELLS WROTE, for the whole
population, where no mark reaches the line (plan P4-D242, the final
review of 2026-09-18). It was `upper_t` outright until then, and that
published a mark no cell of the column wore: twenty-four moments written
twelve with a space and twelve with a lower-case `t`, at a floor of
eleven, published `{"upper_t": 24}`. Ruling 6 of 2026-09-17 counts a
rare spelling into the COLUMN's commonest spelling, and where none
reaches the line the commonest is still one of them. The bound P4-D220 replaced allowed a pool of at
most (floor − 1) times the unnamed marks (the stage 2 audit, 2026-09-14;
landing 2b.3), and admitted both ways a pool of marks names a row:
`{"upper_t": 399, "(withheld)": 1}` named the one row that wrote a `t`.

**Invariant D13 (the separator totals).** `datetime_separators` is
`{}` where `resolution` is not `datetime`. On a datetime column whose
`format` is not `iso-mixed` its values sum to
`n_present - n_unparsed`; on `iso-mixed` they sum to
`resolution_mix["iso-datetime"]`, the cells that wrote a clock. A
`month-first-datetime`, `day-first-datetime` or `slashed-iso-datetime`
column carries only `space` or `(withheld)`.

**Invariant D14 (a column at midnight).** `all_at_midnight` is `true`
only where `resolution` is `datetime`, `n_present - n_unparsed` is at
least the floor, `earliest` and `latest` each stand at midnight on the
wall clock of the offset published for that end, and every rung of
`date_percentiles` stands at midnight under some offset `utc_offsets`
names; on the `local` clock that is every one of those instants ending
in `00:00:00`, and on the `utc` clock the map pools no offset under
`(withheld)` (landing 2b.3). The rule reads in that one direction: the
canonical form drops the fraction, so a loader can refuse a `true` no
column could carry and cannot confirm one (producer obligation MN-P).

**Invariant D15 (the count at midnight, landing 2b.3; the floor of two
and the absent state, landing 2b.6).** `n_at_midnight` is absent —
written `null` — or it is at most `n_present - n_unparsed`, at least
the floor, and either every parsed cell or leaves at least the floor off
midnight. THE FLOOR HERE IS NEVER BELOW TWO, whatever
`small_cell_floor` is, because one is not a group: a count of one names
the person who holds the value, and a count one short of every value
names the person who does not. WHERE THAT RAISE IS WITNESSED (landing
2b.14): at any raised floor the ordinary floor above refuses such a
count first, so the raise decides nothing there and a battery whose
base is written at a floor of eleven cannot show it working — withdrawn
from the loader, every entry of that battery still passes. It is
witnessed at a floor of ONE, where the ordinary floor would admit a
count of one and the raise alone refuses it, in both directions: the
count itself and the count one short of every value. It is present only
where `resolution` is `datetime` and, on the `utc` clock, the map pools
no offset. It equals
`n_present - n_unparsed` exactly where `all_at_midnight` is `true`, so
the statement and the count cannot disagree; below the floor both are
empty, and the statement's own floor is not contradicted.

**Invariant D16 (whole dates wear no offset, landing 2b.3).** On a
column whose `format` is `iso-mixed`, `resolution_mix["iso-date"]` is
at most the count of `utc_offsets` under `(none)` and `(withheld)`
together: every whole-date cell carries no offset, and is counted
there.

**Invariant D17 (the joint width census, landing 2b.6).** Every key of
`date_field_widths` is `padded`, `unpadded`, `first-padded`,
`second-padded`, `first-field-padded`, `first-field-unpadded`,
`second-field-padded` or `second-field-unpadded`, and `(withheld)` is
none of them; and every key maps to a count at least the floor and
never below two — the first two parts of the disclosure rule of plan
P4-D131, `parsing.census_nameable` asked with no pool, whose third part D18 to D20 hold
over the totals their blocks publish. *Amended by the review of
158c811:* D17 admitted a `(withheld)` pool of at most (floor − 1) times
the words the census left unnamed, and a count at a floor of one, and
both named one row. *Amended by its skeptic (plan P4-D139):* D17 also
held `n_present - n_unparsed` less the census's total to nought or that
same number, and a date showing no width at all is not a form: the
remainder is taken over the cells that could show a width, which the
block does not publish, so the producer holds it and the loader cannot.
The
census is `{}` unless `format` is one of the six
variable-width members — `month-first-date`, `day-first-date`,
`two-digit-month-first-date`, `two-digit-day-first-date`,
`month-first-datetime`, `day-first-datetime` — or one of the two
textual members, and on a textual member only `padded` and `unpadded`
may appear, the month there being a NAME and the day the only numeric
field. Its values sum to AT MOST `n_present - n_unparsed`, and the
bound is a ceiling rather than an equality because only a field below
ten can show a width at all.

**Invariant D18 (the joint month-name census, landing 2b.6).** Every
key of `month_name_styles` is one of the thirty-six joint style words
— `<case>-<length>-<mark>-<comma>` over `upper`, `title`, `lower` ×
`abbreviated`, `full`, `either` × `space`, `hyphen` × `comma`,
`no-comma` — and on `textual-day-first-date` one of the eighteen ending
`-no-comma`, a comma there following a month name, which no member of
this contract reads. The census is held to the disclosure rule of plan
P4-D131 over `n_present - n_unparsed`: every count at least the floor
and never below two, and what the counts leave over of that total
nought or at least that many. It is `{}` unless `format` is one of the
two textual members, and its values sum to at most
`n_present - n_unparsed`: a cell whose month is May shows no length,
`May` being its own abbreviation, and is counted under the length its
column's other cells of the same case, mark and comma wrote, or with the
length `either` where none did (plans P4-D133 and P4-D139).

**Invariant D19 (the quarter marker's case, landing 2b.6).** Every key
of `quarter_marker_case` is `upper` or `lower`; the census is held to
D18's disclosure rule over `n_present - n_unparsed`; it is `{}` unless
`format` is `year-quarter`;
and its values sum to at most `n_present - n_unparsed`.

**Invariant D20 (the zulu marker's case, landing 2b.6).** Every key of
`zulu_case` is `upper` or `lower`; the census is held to D18's
disclosure rule over `utc_offsets["Z"]`, the total it counts over; it
is `{}` unless `utc_offsets` NAMES `Z`; and its values sum to at most
`utc_offsets["Z"]`. The key-set rule is the one D4 makes
for the endpoint offsets and for the same reason: this census counts a
subset of the cells carrying ONE offset, so publishing it beside a
POOLED `Z` would hand back in one field the count another field of the
same block promises to withhold.

**A consequence, stated rather than left to be discovered.** The
canonical `datetime` form carries seconds and no fractional part, so
`earliest`, `latest` and every rung of `date_percentiles` are at second
resolution EVEN WHEN `time_precision` is `subsecond` and
`subsecond_digits` is 3. The finer precision is a fact about the
column's notation, published in its own two fields, not a property of
the eleven published instants. A generator that must write subsecond
cells reads `time_precision` and `subsecond_digits`, never the ladder.
Where `all_at_midnight` is `true`, D14 puts every published instant at
`00:00:00`, and it is the flag, not the ladder, that says every cell
of the column stood at midnight.

**Twin datetime cells** follow the REVERSAL of owner decision 5 (owner
ruling 2026-09-15, plan P4-D61, landing 2b.6): a twin datetime cell is
written in the MEMBER that read the real column — the block's own
`format` — at the precision the profile records, and an offset is
written only where the profile records a real one. So a date-only
column read as `iso-date` writes `2024-03-15`, one read as
`month-first-date` writes `03/17/2024` or `3/17/2024` as its
`date_field_widths` census says, one read as `textual-day-first-date`
writes `17-MAR-2024` or `17 Mar 2024` as its `month_name_styles` census
says, one read as `compact-date` writes `20240317`, a month column
writes `2024-03`, and a quarter column writes `2024-Q1` or `2024-q1` as
its `quarter_marker_case` census says. While decision 5 stood every one
of those was written `2024-03-17`, and residual R-P2-7 disclosed the
price: a person's own parsing call needed a different format argument
on the twin than on their table. Method G7.5 carries the per-member
table and C6-25d to C6-25g the four censuses. A column whose `format` is
`iso-mixed` writes every parsed cell at the finest recorded form, its
mix recorded and not reproduced, EXCEPT where its `all_at_midnight` is
`true` (landing 2b.3, narrowing owner decision 4): there its
`resolution_mix` is spent over the ranks and a whole-date rank is
written as its bare day, after every rank whose instant the published
tail fixes takes the form and the offset that instant stands at
midnight under (repair pass of landing 2b.3). A datetime cell carries, between its day and
its clock, the mark method G7.5 allocates from `datetime_separators`:
a withheld pool is written with the permitted marks the census leaves
unnamed (landing 2b.3), and ranks the counts still do not cover take
the commonest named mark, or where none is named `T` on an ISO reading
and a space on a slashed stamp. A column on the `local` clock whose
`all_at_midnight` is `true` is generated in whole days, and every cell
is written as its day with a midnight clock at the column's
`time_precision` and `subsecond_digits`; a column counted in seconds
that publishes `n_at_midnight` above nought has that many of its
cells moved onto a midnight of its own wall clock (landing 2b.3). No
column publishes a nought there any more, so the move of an accidental
value at midnight off a column publishing one is withdrawn with the
nought that bought it (landing 2b.6). The rule is scoped to twin CSV cells
and does not touch the profile's own canonical serialization: a
published instant stays space-separated whatever mark the cells
carry.

**`format` is EXACT-OBSERVABLE** (landing 2b.6). It names the REAL
file's parser family, and the twin is written in that same member, so
describing the twin again names it. It could not be reproduced at all
while owner decision 5 stood: the twin was then written in ISO syntax
at the recorded precision rather than in the source's lexical family,
and a month-first column's twin reprofiled as `iso-date`. That narrowed loss was residual R-P2-7 — code
parsing dates with an explicit source format argument needed that
argument changed when it moved from the twin to the real table — and
the owner's reversal of decision 5 on 2026-09-15 retires it. ONE
CORNER remains, and it is `resolution_mix`'s: on an `iso-mixed` column
not wholly at midnight the twin writes every value with a time of day,
so it reads back as `iso-datetime` and the member is listed rather than
checked (residual R-P4-12). The widened readings above widen what is read, not what is
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
spelling this pass put there is written in the twin at its count, as
the hole-spelling reproduction rule states for every key (C6-115, with
the reading of such a cell at C6-116).

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

Both roles carry exactly the same key set — the TWENTY-SIX keys
below, added to the universal set of section 5.1. They differ only in
the verdict that produced them.

**It read "sixteen" until 2026-09-09**, and the table under it had listed twenty-five for as long as the later keys have existed —
`kurtosis`, `n_distinct_values`, `mode`, `mode_count`,
`percentiles_between`, `field_widths`, `value_histogram`, `empty_bins`
and `empty_edges` all arrived after the number was written and none of
them moved it. `NUMERIC_KEYS` in the loader held twenty-five, and an
independent producer following "sixteen" wrote a block missing nine
obligations the loader requires. `group_separator` made it twenty-six
on 2026-09-14 (plan P4-D38), and every count below moved with it in
the same commit.

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
| `percentiles_between` | object of ninety rungs | Q19 below | the ninety rungs the named ladder does not carry: every percent from 1 to 99 it does not name | REPORT-ONLY, one fact and not ninety |
| `mean` | number or `null` | — | the arithmetic mean of the parsed values | APPROXIMATED |
| `std` | number or `null` | ≥ 0 when a number | the sample standard deviation, divided by n−1 | APPROXIMATED |
| `skew` | number or `null` | — | the moment-based skewness | APPROXIMATED |
| `kurtosis` | number or `null` | Q16 below | the moment-based kurtosis, not the excess: a normal curve reads 3 | APPROXIMATED |
| `n_distinct_values` | whole number | Q17 below | how many different NUMBERS the column holds, as distinct from how many different spellings | EXACT-OBSERVABLE (amendment A-P4-55; REPORT-ONLY until 2026-09-04) |
| `mode` | number or null | Q18 below | the number the column held most often, or null where the pair is withheld | REPORT-ONLY |
| `mode_count` | whole number | Q18 below | how many cells held the commonest number, and nought exactly where `mode` is null | REPORT-ONLY |
| `std_unrepresentable` | boolean | — | true when the exact spread is larger than binary64 can hold | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | — | parsed values equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | present cells whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range cells whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | — | how many present cells the statistics were computed from | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | — | how many present cells were not | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | the share of present cells whose writer meant a number | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking cell is a whole number | EXACT-OBSERVABLE, routed by the published FACT and not by role; REPORT-ONLY only where no stratum that may take a value has a share holding a number a double can represent with anything after the point, which the report then names (A-P4-48, `beyond-whole-steps`) |
| `n_rows` | integer ≥ 0 | `== n_rows` at the top level | the table's row count, echoed | LOADER-ONLY |
| `numeric_styles` | object | section 7.5 | how many cells were written in each spelling style, under the floor | EXACT-OBSERVABLE against the recount identity of section 7.5.7 |
| `group_separator` | string | `""`, `","`, `"."`, a space, `"'"`, U+2019, U+00A0, U+202F or U+2009 | the mark the column writes between thousands. A cell PROVES a mark where it has four or more whole figures, is written `plain`, `leading_plus` or `decimal`, and its whole part reads as groups of three around that one mark, a lone group such as `12,345` or `12 345` included; such a cell carrying no valid grouping is BARE, and accounting brackets and signs are not figures. The commonest proven mark is published where its cells reach `small_cell_floor` AND outnumber every other such cell, bare or grouped with another mark, and no mark is published where a padded or exponent cell holds one. On a column named in `settings.forced_decimal_commas` that the declaration reaches, each cell is read with its points and commas exchanged and a proven comma is published as `"."`, the one `42.037,34` writes; the other marks are not exchanged (GS1). `""` otherwise (the stage 2 audit, 2026-09-14; landing 2b.2, 2026-09-15) | EXACT-OBSERVABLE (plan P4-D41) |
| `negative_form` | string | `"minus"`, `"brackets"`, `"minus_sign"` or `"trailing_minus"` | how the column writes its negative numbers: the hyphen-minus in front, accounting brackets around the figures, the minus sign U+2212 in front, or the hyphen-minus after figures carrying a decimal point (after whole figures it is not read, and NF57 names it). Each numeric cell reading as a negative number counts under the notation it wrote; a notation other than `minus` is published where its cells reach `small_cell_floor` and outnumber every other negative cell together, and `minus` otherwise (NS1; landing 2b.2) | EXACT-OBSERVABLE (plan P4-D41) |
| `wide_runs` | string | `"none"`, `"canonical"` or `"respelled"` | whether the column's WIDE runs of figures are the text their own values write. A cell is such a run where its CORE — the cell with any surrounding space, accounting brackets, minus sign of the character tables and thousands marks taken off, exactly as section 7.5.4 reads a form off it — is a point-free run of base-ten figures with or without a sign, its form is `plain`, `leading_plus` or `leading_zero`, and its value is at or past 2**53 in either direction — the bound past which more than one run of figures reads back as one double, so that "a spelling of its own value" stops naming a single text. A cell written `leading_zero` IS one, once its pad is read off (landing 2b.16 part 2, plan P4-D107; the defining clause above went on naming two forms while this sentence admitted the third, and that contradiction is repaired in the clause itself by plan P4-D108 rather than left for a re-implementer to resolve): its figures are not its value's figures until the padding comes off, and the leading zeros ARE the padding, because past 2**53 every value is a whole number and the figures a whole number writes never begin with a zero. The split is therefore a fact of the cell's text and NOT of the published width — a column pooling its width under `(withheld)`, or publishing none, is read exactly as one naming `19` — so no census decides it and the producer consults none. Measured before this reading: 800 zero-padded nineteen-wide keys, every cell respelled, published `"none"` and were checked by nothing, and a column of 800 plus-signed PADDED keys, every one canonical, was counted 800 of 800 respelled. `"none"` where fewer such cells than `small_cell_floor` were written; `"canonical"` where at least that many were and FEWER than the census floor max(2, `small_cell_floor`) of them are anything but the figures their own values write; `"respelled"` where at least that many were and at least the census floor of them are not. THE LINE BETWEEN THE LAST TWO WORDS IS THE CENSUS FLOOR AND NOT ONE (plan P4-D140, the final Codex review's first BLOCKER): measured with the line at one, 800 canonical keys at a floor of eleven published `"canonical"` and the same column with ONE key respelled into its binary64 neighbour published `"respelled"`, both loading, so a reader who knew the other 799 cells read the last one's spelling off the word. It carries no count and never pools, but the floor holds it as NS1 holds the notation beside it, because the word names the FORM of the cells it is about and below the floor the forms map has pooled that form away: the word is a fact about the column's WRITER, naming no cell, no count and no figure (WR1; landing 2b.13, repaired by plan P4-D91) | EXACT-OBSERVABLE (plan P4-D90) |
| `decimal_plus` | object | `{}`, `{"+": n}` with n ≥ max(2, `small_cell_floor`), or `{"(unavailable)": 0}` | how many cells written with a point carried a plus in front, which the first-match ladder files under `decimal`. `{}` only where the column wrote no cell with a point at all; `{"+": n}` only where n reaches the census floor AND the cells with a point that carried no plus are nought or reach it too; `{"(unavailable)": 0}` otherwise, which is the one state nought and every below-floor count share. Both halves are the disclosure rule every census of this section is held to, stated once as `parsing.census_nameable` (plan P4-D140): every printed count reaches the census floor, and so does every complement a reader can take from a total, or it is nought. It never pools: `+` is this census's only category, so a `(withheld)` remainder beside it would name the category it held back. The total is no more than the cells the forms map can place in `decimal` (DP1; landing 2b.2, amended by landing 2b.7) | EXACT-OBSERVABLE (plan P4-D41, P4-D65.1) |
| `negative_notations` | object | `{}`, or a map of `"minus"`, `"brackets"`, `"minus_sign"` and `"trailing_minus"` to counts ≥ max(2, `small_cell_floor`) with an optional `"(withheld)"` remainder of at least that, or `{"(unavailable)": 0}` | how many of the column's negative cells wore each notation, counted over the cells `negative_form` is counted over and under the notation each wrote. `negative_form` publishes the MAJORITY and the twin used to write every negative that way, so a column mixing two came back written wholly as one; this census carries the mixture and the generator spends it cell by cell. A notation used by fewer cells than the census floor is pooled, and a pool that is itself below the floor makes the whole census unavailable; so does a census whose printed counts leave of the column's negatives a remainder neither nought nor at the census floor (P4-D140), which every negative wearing exactly one notation makes nought by construction. `{}` where the column has no negative cell, and on a position of a `joined_numbers` column (NS2; landing 2b.7) | EXACT-OBSERVABLE (plan P4-D65.2) |
| `thousands_marks` | object | `{}`, or a map of the marks `group_separator` may publish other than `""` to counts ≥ max(2, `small_cell_floor`) with an optional `"(withheld)"` remainder of at least that | how many of the column's grouped cells wore each mark, counted over the cells that PROVE a mark by `group_separator`'s own evidence rule — ONE rule, asked of each cell once for both keys, so a declared decimal comma that proves a point for the one proves it for the other (plan P4-D141) — and read in the column's own grammar, so a declared decimal comma counts the point it writes. A BARE groupable cell names no mark, but it IS counted by the disclosure rule: the census is published only where its counts, its remainder, and what it leaves of the groupable cells AND of every number of the column each reach the census floor or are nought (plan P4-D140; measured without the groupable clause, 1,200 grouped prices at a floor of eleven with one rewritten bare published `{",": 1199}` beside a row count of 1,200). Where the rule refuses, and wherever a cell refuses `group_separator` its mark, the census is `{}` — the state a column in which no cell proves a mark reaches, so nought and a count below the floor are one published state — and never `{"(unavailable)": 0}`. Where the column publishes a mark of its own, a non-empty census names that mark. `{}` on a position of a `joined_numbers` column (TM1; landing 2b.7) | EXACT-OBSERVABLE (plan P4-D65.2) |
| `fraction_widths` | object | C6-28 to C6-30 below | how many `decimal`-styled cells were written at each fraction width, under the floor | EXACT-OBSERVABLE, under the producer obligation FW-P |
| `pad_widths` | object | C6-27b to C6-30b below | how many PADDED cells wrote each field width, under the floor: every `leading_zero`-styled cell, and every `leading_plus` cell whose figures begin with a redundant zero (plan P4-D145), except in the two cases C6-28b names, where the census writes what a column with no plus-signed padded cell writes (plans P4-D145 as amended and P4-D148) | EXACT-OBSERVABLE, under the producer obligation PW-P |
| `field_widths` | object | C6-27c to C6-30c below | how many cells written as a WHOLE NUMBER — padded or not — wrote each field width, under the floor, a width pooled where what it leaves beside `pad_widths` would be a count below the census floor (P6c, plan P4-D148) | REPORT-ONLY, under the producer obligation XW-P |
| `value_histogram` | object | C6-31 below | how many of the values the statistics used fall in each of the fixed bins between `min` and `max`; published only when EVERY bin clears the floor | REPORT-ONLY |
| `empty_bins` | array | C6-122 to C6-123 below | which of those same fixed bins hold NONE of the values the statistics used, ascending; published whatever the floor is | REPORT-ONLY |
| `empty_edges` | array | C6-123a to C6-123b below | one `[below, above]` pair for each RUN of consecutive empty bins: the two values the statistics used that the run really lies between | REPORT-ONLY |
| `number_spellings` | object | section 7.13 | on a `count` block ALONE: every spelling of a column that wrote one number more than one way, with how many cells wrote it; `{}` on every other `count` block | EXACT-OBSERVABLE |

Thirty-one keys. Every one is present in every block of these two
roles — this format has no optional keys — and every key not listed
here or in section 5.1 is FORBIDDEN on them (section 6.11). A `count`
block carries thirty-two keys: these and `number_spellings`, which is
that role's alone and forbidden on `continuous` (section 7.13).

### 6.7a The tail rule: `tails` and `bin_groups` (stage 3)

**A block carries these two keys or neither, and that is this format's
one exception to "no optional keys."** A block written before stage 3
carries neither and is read exactly as it always was, so every
description already written still loads and its twin does not move. A
block that carries `tails` carries `bin_groups` too, is a TAIL BLOCK,
and is read by the rules below. Nothing else about the block's key set
changes.

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `tails` | object or `null` | TL1 to TL6 | `null` on a block of fewer values than a tail's own rows; otherwise `low` and `high`, each `null` where only the moments are published, and otherwise an object naming the boundary percent, the rows beyond it, and how far from it they lie | the leaves below carry the classes |
| `tails.low.percent`, `tails.high.percent` | whole number | 1 to 99 | the percent the published ladder stops at on that side | LOADER-ONLY: it follows from the count of values and the smallest group size, and the loader holds the description to it |
| `tails.low.rows`, `tails.high.rows` | whole number | TL4 | how many rows lie beyond that percent | LOADER-ONLY: it follows from the percent and the count of values, and the loader holds the description to it |
| `tails.low.mean_distance`, `tails.high.mean_distance` | number ≥ 0 | TL5 | the mean distance of those rows from the boundary rung, in the column's own unit | APPROXIMATED, inside the window of `docs/spec/generation-method-v1.md` G12.13 |
| `tails.low.rms_distance`, `tails.high.rms_distance` | number ≥ 0 | TL5 | the root-mean-square of the same distances, computed exactly and rounded once | APPROXIMATED, inside the window of `docs/spec/generation-method-v1.md` G12.13 |
| `tails.low.values`, `tails.high.values` | array of numbers | TL6 | on a block whose values stand on a grid, the tail's own different values, ascending, WITHOUT how many rows hold each; `[]` elsewhere | EXACT-OBSERVABLE: a file's own tail at that percent lists the same values |
| `bin_groups` | array of objects | BG1 | the histogram of the rows between the two tails, in groups of bins: `{"first": bin, "last": bin, "count": rows}` | REPORT-ONLY, for the reason `value_histogram` is |

**Why the two ends are not published.** A `min` or a `max` is one row's
value wherever one row holds it, and the rungs beside them read the
next rows in. The rule withholds every rung whose type-7 reading
touches one of the outermost max(`small_cell_floor`, 3) values, on each
side, and publishes instead what those rows look like as a GROUP: how
many there are, how far from the last published rung they lie on
average, and the root-mean-square of that distance. Measured over
sixteen shapes at a floor of eleven, the numbers a description
published that equalled a value fewer than eleven rows held went from
13 to 46 per shape to none.

| id | statement | loader? |
|---|---|---|
| TL1 | with `tails` published and both sides objects, every rung outside `[low.percent, high.percent]` is `null` except an end at least max(`small_cell_floor`, 3) rows held, the two boundary rungs hold numbers, `1 <= low.percent <= 50 <= high.percent <= 99`, and each percent is the smallest whole percent whose type-7 reading leaves at least max(`small_cell_floor`, 3) values strictly outside it | yes |
| TL2 | `tails` is `null` exactly where `n_used_in_statistics` is below max(`small_cell_floor`, 3), and such a block publishes no rung and no moment at all | yes |
| TL3 | `low` and `high` are both `null` or both objects; both `null` exactly where no percent clears two tails at once, and then every rung is `null` | yes |
| TL4 | `rows` is `ceil((n - 1) * low.percent / 100)` on the low side and `n - 1 - floor((n - 1) * high.percent / 100)` on the high, `n` being `n_used_in_statistics`, and never below max(`small_cell_floor`, 3) | yes |
| TL5 | `mean_distance` and `rms_distance` are numbers of nought or more, and the mean is no larger than the root-mean-square | yes |
| TL6 | `values` is ascending and different, no longer than `rows`, whole on a block publishing `integer_valued: true`, at or beyond the side's boundary rung, and led by the published end where there is one | yes |
| BG1 | `bin_groups` is empty, or groups that follow one another from bin 0 to the last bin of C6-31f's division, each counting at least max(`small_cell_floor`, 3) and together counting `n_used_in_statistics` less the two tails' rows | yes |

**The tail facts are computed exactly** (`docs/spec/generation-method-v1.md`
G5.3b states what reads them): every value and the boundary rung as
whole numbers of one shared power of two, the two sums exact, and each
result rounded to binary64 once -- the mean as a quotient and the
root-mean-square by the exact integer square root, with the tie rule
of the quotient.

**A LISTED TAIL, and the owner's ruling it rests on** (2026-09-22). On
a block whose values stand on a grid -- `integer_valued`, or one
published fraction width -- a tail of few different values is published
BY THOSE VALUES, without how many rows hold each. The owner ruled it
for bounded scales: "we don't need to be worried about the tails ...
many people will be there and there is no big deal in knowing that it's
there." Without it the smooth reading of G5.3b rounded onto such a grid
wrote values the scale does not have -- 11 on a pain score of 0 to 10 --
and never wrote the scale's own end. A tail is also listed where its
rows, its two distances, its boundary, the grid and the sign counts
would otherwise leave one answer for its end (plan P4-D324): the
description would then name that end in all but name, and naming it
outright at least says so.

**THE NUMERAL WAS STALE AGAIN, AND IS CORRECTED AGAIN** (landing 2b.18
part 2). It read "twenty-six" while `contract.NUMERIC_KEYS` held
twenty-eight — `negative_form` and `decimal_plus` arrived at landing
2b.2 and this sentence did not move — and the guard below had been red
on it since.

**THE NUMERAL WAS STALE AND IS BOUND TO THE TABLE NOW.** It read
"eighteen" while the table held twenty-four, and the same drift was in
this section's sibling below and in section 6.11's per-role
breakdown: one fact written twice, one half updated at each landing.
`tests/test_p4d18_role_topology.py` counts the rows of both tables and
the entries of `contract.NUMERIC_KEYS` and `contract.AFFIXED_KEYS`
against these words, so a landing that adds a key and leaves a numeral
behind now turns red.

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

#### `pad_widths`

This role carries `pad_widths`, the other sibling of `numeric_styles`
on the block rather than a key inside it. **Section 7.8 states it in
full** — what it holds, its key grammar, and invariants P5b, P6b and
P7b — for the reason section 7.6 is written that way: it stands on
three roles, and a rule stated at one of them would be a rule the
other two carry by inference.

Its reach is the same: `pad_widths` is REQUIRED on `count`,
`continuous` and `affixed_number`, and FORBIDDEN on every other role.

#### `field_widths`

This role carries `field_widths`, the THIRD sibling of `numeric_styles`
on the block rather than a key inside it. **Section 7.10 states it in
full** — what it holds, its key grammar, and invariants P6c, P7c and
P9c — for the reason sections 7.6 and 7.8 are written that way.

Its reach is the same: `field_widths` is REQUIRED on `count`,
`continuous` and `affixed_number`, and FORBIDDEN on every other role.

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

**Invariant Q16 (`kurtosis` nulls and bound).** `kurtosis` is `null`
when `n_used_in_statistics < 4`, and when every parsed value is
identical. It is a number otherwise, and for the `n` values the
statistics used that number lies between 1 and `n - 2 + 1/(n - 1)`,
which is where every sample of `n` values lies whatever the values
are: the upper end is reached exactly when one value stands apart from
`n - 1` equal ones.

**Invariant Q17 (`n_distinct_values` bound).**
`n_distinct_values <= n_numeric`, and `n_distinct_values >= 1` wherever
`n_used_in_statistics > 0`. The bound is against the numeric cells and
not against `n_distinct`, because the same block is read at three
grains -- a column, one position of a `joined_numbers` column, and the
cores of an `affixed_number` column -- and only the first of them has a
spelling count over the same cells.

**Invariant Q18 (`mode` and `mode_count` stand together).** `mode` is
`null` exactly when `mode_count` is 0. Where `mode` is a number,
`2 <= mode_count <= n_numeric`: one cell is not a mode, and no more
cells can hold the commonest number than read as a number at all.

**Invariant Q19 (`percentiles_between` never goes down).**
`percentiles_between` names exactly the ninety percents from 1 to 99
that `percentiles` does not name, each holding a number or `null`; and
walking the hundred and one rungs of the named ladder and this one
together in percent order, passing over every `null`, no rung is smaller than the
rung before it.

**Where else this family is enforced.** On `affixed_number` every
invariant of this section is read over the CORES, with
`n_core_numeric` in place of `n_numeric` (AF7), and nowhere else. The
four universal cell-census counts answer for the cells on that role as
on every other.

**Invariant GS1 (the mark between thousands and the decimal mark)**
(the stage 2 audit, 2026-09-14). `group_separator` is `"."` only on a
column named in `settings.forced_decimal_commas` that the declaration
reaches, and is never `","` there. The declaration reaches a column's
own numbers and the numeric partition of a `numbers_with_labels`
column; a numeric block nested in an `affixed_number` or
`joined_numbers` column never carries `"."`. The twin groups such a column with a comma and then
exchanges its points and commas, so a `","` there would be written
`23,648,37`, which no reader takes for a number. A space, an apostrophe,
U+2019, U+00A0, U+202F and U+2009 are neither decimal mark and stand
under either (landing 2b.2): `1 234,56` publishes a space. A position of a
`joined_numbers` column is read from figures and one point alone, so its
block carries `""` and no other mark.

**Invariant NS1 (a notation needs negatives)** (landing 2b.2).
`negative_form` other than `"minus"` only where `n_negative` is at least
`small_cell_floor` and at least one.

**Invariant DP1 (signed decimals at the census floor, in the room, and
never pooled)** (landing 2b.2, amended by landing 2b.7). `decimal_plus`
names `+` only with a count of at least the CENSUS FLOOR — max(2,
`small_cell_floor`) — and never pools: `+` is this census's only
category, so a `(withheld)` remainder beside it would name the category
it held back, and `{}` beside `{"(withheld)": 1}` told a reader which
single cell of 1,200 carried a plus. Where it cannot name a count it
carries `{"(unavailable)": 0}`, which is the one state nought and every
below-floor count share; the unavailable key carries no other number.
Its total is no larger than the `decimal` count of `numeric_styles` plus
that map's `(withheld)` remainder; it is `{}` on a position of a
`joined_numbers` column, whose parts carry no sign.

**Invariant NS2 (the notations a negative wore)** (landing 2b.7).
`negative_notations` names a notation of `negative_form`'s own four only
with a count of at least the census floor, pools what is left under
`(withheld)` only at that floor and only where `small_cell_floor` is
above one — below which C5-S13 leaves nothing to hold back — and carries
`{"(unavailable)": 0}` where it can do neither. The counts together are
no more than `n_negative`. It is `{}` on a position of a
`joined_numbers` column.

**Invariant TM1 (the marks a grouped number wore)** (landing 2b.7,
amended by plan P4-D140). `thousands_marks` names a mark
`group_separator` may publish, other than `""`, at the census floor and
pooling as NS2 does, but it NEVER carries `{"(unavailable)": 0}`: where
it cannot speak it is `{}`, the state a column no cell of which proves a
mark reaches, so a reader cannot tell nought from a count below the
floor. What its total leaves of `n_numeric` is nought or at least the
census floor. Where `group_separator` publishes a mark and the census
names any, it names that mark: a majority the mixture does not carry is
a majority no cell proved; that clause is read after GS1. It is `{}` on
a position of a `joined_numbers` column.

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

**Added keys** — eight, beyond the universal keys of section 5.1:

| key | JSON type | range | meaning |
|---|---|---|---|
| `layout_forms` | object | section 7.12 | how many present cells were written in each shared LAYOUT, under the floor, with the pooled key `(withheld)` |
| `layout_prefixes` | object | section 7.12a | the literal text every present cell opens with, under the key `(column)`, or the text every cell of one named layout opens with, under that layout; `{}` where there is none (owner ruling of 2026-09-17, item 1) |
| `min_length` | integer ≥ 1 | ≤ `max_length` | the shortest present value's length in characters |
| `max_length` | integer ≥ 1 | ≥ `min_length` | the longest present value's length in characters |
| `all_whole_numbers` | boolean | — | true when every present cell is a whole number and there is at least one |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … |

**`layout_forms` IS THIS ROLE'S ALONE, AND IT IS THE KEY THAT SAYS
WHAT A RECORD NUMBER LOOKS LIKE** (section 7.12). The six beside it
give the two length ends and the two alphabet counts, and between them
they say nothing about the SHAPE of a value — which is why a column of
UUIDs published every fact this role had and its twin still wrote
`A----------------------------------J`. Measured at two source seeds
and two generate seeds: the column's pattern matched 800 real cells
and 0 twin cells, and `synthtwin validate` exited 0 on the twin and 0
on the table, so no line of either report named it. It is NOT
`shape_forms`
under another name: that census belongs to the five label roles, is
forbidden here by C6-31b, stops at twenty-four characters and marks a
letter without its case, and each of those three would lose a UUID.

`layout_prefixes` is this role's alone as well, and it is the ONE key of
the block that carries text of the table, by the owner's ruling of
2026-09-17 (section 7.12a and invariant I3 below).

None of the other six is this role's alone except `all_whole_numbers`. A
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

**Invariant I3 (this block publishes nothing of the table).** Every
key of `missing_by_source` names a member of the published vocabulary
(C6-126), the two absence counts stand inside N3's upper bound, and
every `sentinel_verdicts` entry has `candidate == "(withheld)"`
(N3, V2). It is a property of the whole BLOCK: no value of the column,
no spelling of one and no fragment of one stands anywhere in it — and a
vocabulary member is none of those three, being this package's own word
and the same in every installation — WITH ONE EXCEPTION, AMENDED BY THE
OWNER'S RULING OF 2026-09-17 (item 1, plan P4-D202): the literal prefix
of section 7.12a, a fragment every present cell of the column opens
with, or every cell of one named layout, published only where invariant
LP1 and the disclosure rule of 7.12a admit it. That is the only fragment
this invariant admits and `layout_prefixes` the only key it may stand
in. What is published is the role, the counts, the shortest and longest
length, whether every value is a whole number, how many cells are all
digits or all code alphabet, the shape of repetition, the census of
LAYOUTS (7.12) — lengths and counts, never values — and that prefix.

**THE LAYOUT CENSUS STANDS INSIDE I3, AND IT IS THE ONE KEY OF THIS
BLOCK A READER COULD MISTAKE FOR A FRAGMENT**, so the ground is
written here rather than left to 7.12. A layout carries one mark per
character saying what KIND of character stood at each position —
`~~~~~~~~-~~~~-~~~~-~~~~-~~~~~~~~~~~~` says a record number was
written as a UUID and says nothing whatever about WHICH UUID. Every
figure and every letter of the cell is replaced before the key is
built, and the marks that remain are this contract's own closed list,
the same in every installation. So no value of the column, no spelling
of one and no fragment of one stands in a key, which is exactly what
this invariant requires of the whole block.

**A LITERAL RUN IS A FRAGMENT, AND BY THE OWNER'S RULING OF 2026-09-17
ONE KIND OF IT IS PUBLISHED** (landing 2b.15, landing 2b.18; ruling item
1, plan P4-D202). A constant run shared by a whole column — a hospital's
own record prefix, or `ABC-` in front of a study number — is a
character-for-character fragment of every value in that column, which
this invariant and F3 forbade. It is a POPULATION-wide fragment rather
than any one person's, which made it a question for the owner rather
than a settled refusal, and while it waited the twin wrote the layout's
own alphabet in its place: measured at 800 rows, `^P\d{5}$` matched 800
real cells and 30 twin cells, `^REC\d{7}$` 800 and 0, and both files
passed. The owner ruled it published where every present cell carries
the same prefix and the column clears the smallest group size, and this
invariant is amended for that case ONLY: section 7.12a states the rule,
and the per-layout reading of it — each named layout's own prefix where
the whole column shares none — is flagged to the owner as this
version's extension of the ruling. No other literal run of a cell is
published: a run that is not an opening, a run holding a figure, and a
run that stops inside a run of letters are not.

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

**Added keys** — six, beyond the universal keys of section 5.1:

| key | JSON type | shape | meaning |
|---|---|---|---|
| `length` | object | exactly `min`, `max`, `mean`, `p50` | statistics of the present values' lengths in characters |
| `words` | object | exactly `min`, `max`, `mean` | statistics of the present values' word counts |
| `n_all_digits` | integer ≥ 0 | ≤ `n_present` | present cells that are ASCII digits and nothing else, after trimming |
| `n_code_alphabet` | integer ≥ 0 | ≤ `n_present` | present cells drawn from the code alphabet, after trimming |
| `n_distinct_by_occurrences` | multiplicity map | section 5.3 | how many different RAW present values covered one row, two rows, … |
| `shape_forms` | object | section 7.9 | how many present cells were written in each shared WRITTEN FORM, under the floor |


**The two alphabet counts ask the disclosure rule** (`parsing.absorbed_total`,
plan P4-D277). Each is a census of two groups written as one number --
the cells inside the alphabet, and the cells a reader takes by
subtracting it from `n_present` -- so where either side is below
max(2, `small_cell_floor`) the smaller is counted into the larger and the
count is published as nought or as every present cell. Measured at a
floor of eleven: 999 declared record numbers beside one `X Y` published
`n_code_alphabet 999` against `n_present 1000`, naming the one
identifier outside the alphabet, while the layout census that would have
named it was withheld for the same reading. The censuses checked against
these counts -- `layout_forms` under C6-131b, `shape_forms` under SF3 --
are checked against the counts AS PUBLISHED, so the two can never part.

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

**Invariant F3 (this block publishes nothing of the table).** Every
key of `missing_by_source` names a member of the published vocabulary
(C6-126), the two absence counts stand inside N3's upper bound, and
every `sentinel_verdicts` entry has `candidate == "(withheld)"`
(N3, V2). As at I3 this binds the whole BLOCK, not any one field: no
value, no spelling of one and no fragment of one stands anywhere in
it. **The owner's ruling of 2026-09-17, item 1, amends this invariant
for the case it names and no other** (plan P4-D202): the literal prefix
of section 7.12a is admitted where a block carries `layout_prefixes`,
and that key stands on the declared `identifier` role alone (6.11). A
`free_text` block carries no layout census and no prefix, so on this
role the amendment admits nothing and F3 binds exactly as it did.

**WHAT F3 DOES NOT COVER, NAMED RATHER THAN LEFT TO BE FOUND.** F3 binds
the block's values, spellings and fragments; it does not bind the four
universal reading counts of section 5.1, which are numbers and not
spellings. `n_numeric`, `n_not_numeric`, `n_out_of_range` and
`n_contradictory` are absorbed under X2 on a declared record number and
are NOT absorbed here, so on this role a part of one stands: 999 notes
beside one `42` publish `n_numeric 1` against `n_present 1000`. The two
alphabet counts above ARE absorbed, by `parsing.absorbed_total`. Section
5.1 states the gap, what it would cost to close, and that it is the
owner's to rule on.

**AND `shape_forms` DOES NOT BREAK F3, WHICH IS WHY IT MAY STAND ON
THIS ROLE AT ALL.** A form is built by replacing every figure of a
cell with `%` and every letter with `@` (C6-31a), so the one thing it
cannot carry is a figure or a letter of anybody's value. What survives
is how many there were and where the marks between them fell:
`E11.9` and `Z99.1` are one form and the form tells them apart from
nothing. Section 7.9 states this as a checked property of every KEY
rather than as a property of the producer, so a hand-edited document
in which a real value survived into a key is a loader refusal and not
a leak. The other half of F3's protection is the floor: a form fewer
than `small_cell_floor` cells share is not named (SF1), so a cell
whose form is its own — every cell of prose — puts nothing in the
census, and this key is `{}` on the columns the free-text promise was
written for.

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
whatever its role. On those columns, and only those, every sentinel
candidate reads `(withheld)` and `missing_by_source` is confined to the
published vocabulary by C6-126. **This is a property of the whole
BLOCK, not of any one field: it is what stops the next field somebody
adds from being the one that leaks.**

**C6-126 (such a column still says which of SYNTHTWIN'S OWN words its
holes wore).** Every key of `missing_by_source` on a nothing-publishing
column names a member of the published vocabulary — the comparison
being C6-32's one operation, so a folded member is named after trimming
and case folding and the exact-spelling member byte for byte — and a
key naming no member is refused. Both absence counts are written as on
any other column and N3's sum closes. A spelling of NOTHING BUT SPACE
names the empty member and is admitted on that ground, which is the
same key every other column may carry (C6-125).

**Why a member of the vocabulary is not a value of the table.** It is
this package's own word, fixed in the closed list C6-31 states,
identical in every installation, and C6-31 says in terms that the
vocabulary "contains no text from any table". A column publishing
`{"NA": 174}` says that 174 of its cells were spelled with a word
synthtwin ships. It does not say what any value of that column is, and
no reader can rebuild a row from it.

**What the empty map cost, measured.** A 500-row free-text column whose
absent cells were 101 blanks and 174 `NA`/`N/A` published `n_missing:
275`, named no spelling, and put both absence counts at 0. Three things
followed. The twin wrote 275 EMPTY cells where the table wrote 101, so
`df[df.note != "NA"]` dropped 174 rows of the table and none of the
twin. The description could not be read back: re-describing the very
table it was written from found 399 present cells against the published
225 and reported BOTH presence counts MISSED at exit 3 — the real table
failing its own description, on a run with no options typed at all.
And a reader could infer the publication class from the two zeros,
which is the inference N6 now withdraws. With the vocabulary named,
that column publishes `{"N/A": 95, "NA": 79}` with `n_missing_blank:
101`, its twin writes each spelling at its published count, and both
validations return 0.

**A COLUMN THAT PUBLISHES NO VALUE OF THE TABLE PUBLISHES NONE OF THE
PERSON'S OWN SPELLINGS EITHER WAY, declared or not, and the reason is
what a LOADER can check.** A
declaration is recorded as a count and never as text (C5-17), so no
document distinguishes `Not documented` declared from `Not documented`
written in a cell. A rule admitting declared spellings here could be
obeyed by a producer and not checked by any consumer, and this format
does not write rules of that kind.

**Those cells are counted by NOTHING, and that is why N3 is an
inequality here.** They are not added to `n_missing_withheld`: that
remainder is what the FLOOR held back, and a description written at a
floor of one holds nothing back (S13), so a class withholding recorded
there would make a floor-one document claim what S13 forbids. This is
exactly where such cells stood before this clause, so nothing regresses;
what changes is that the format now SAYS they are unaccounted instead of
implying by a closed sum that there are none. The cost is stated rather
than discovered: a person who declares a word of their own on a
free-text or declared identifier column gets a twin whose holes for
that word are blank, and a reader of that description can tell how many
such cells there were by subtraction but never what they said.

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
appear in the output. Every one of the fifteen roles sits in exactly
one row of the table below:

| class | roles | what the class means |
|---|---|---|
| labels | `constant`, `binary`, `categorical`, `long_tail_labels` | the values themselves appear, folded, with counts, and only when at least `small_cell_floor` rows share them |
| ranges | `count`, `continuous`, `datetime`, `time_of_day`, `affixed_number`, `joined_numbers` | no spelling appears; order statistics computed from the values do. TWO named exceptions, each confined by section 6.11 to its own keys: C6-9's, at `affix_prefix`, `affix_suffix` and the `prefix`/`suffix` of each `affix_variants` entry — a column may wear a SET of wrappers (C6-7a) and every member of the vocabulary is published on the same terms as the commonest, which is what the exception was always about — and section 6.15's, at `separator` |
| nothing | `numeric_unrepresentable`, `identifier`, `free_text` | no value, no spelling, no fragment of one, anywhere — not in levels, not in `missing_by_source`, not in the evidence, not in a remark, not in a publication note, not in a sentinel verdict. ONE named exception, by the owner's ruling of 2026-09-17 (item 1): the literal prefix of section 7.12a, confined by section 6.11 to `layout_prefixes` on `identifier` |
| **no value-publishing class** | `empty` | it has no value to publish, and it is NOT thereby a nothing-publishing column (C6-51) |

The three value-publishing classes carry exactly twelve of the
fifteen roles, each in exactly one row. Membership is a property of
the whole block, on the same reasoning C6-49 gives: a class stated
per field is a class the next field escapes.

**The affix exception is an exception and not a fourth class.** A
fourth class would have to be given a meaning everywhere the three
are enforced; an exception is confined by one matrix, which is where
section 6.11 confines it. The labels class is untouched by it, and
the nothing class's "no value, no spelling, no fragment of one"
sentence is untouched by it. **The prefix exception is an exception in
the same sense** (owner ruling of 2026-09-17, item 1): it is confined by
the same matrix to one key of one role, and every other key of a
nothing-publishing block stands under that sentence exactly as before.

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
class table as a three-way partition of all fifteen roles puts
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
so it is written down here, once, in one place, for all fifteen
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

The fifteen columns, abbreviated for width: `emp` `empty`, `unr`
`numeric_unrepresentable`, `con` `constant`, `bin` `binary`, `cat`
`categorical`, `ltl` `long_tail_labels`, `dtm` `datetime`, `tod`
`time_of_day`, `cnt` `count`, `ctn` `continuous`, `afx`
`affixed_number`, `idn` `identifier`, `txt` `free_text`, `jnd`
`joined_numbers`, `nwl` `numbers_with_labels`.

**THE FIFTEENTH COLUMN WAS MISSING UNTIL 2026-09-04.** This section
said "for all fifteen roles" from the landing that added the compound
role and carried fourteen columns, so a consumer treating it as the
only statement of where a key lives had no topology for a shipped
compound profile at all. The column is here now and
`tests/test_p4d18_role_topology.py` reads every role the loader knows
rather than a list of its own, so the two cannot part again.

| key | emp | unr | con | bin | cat | ltl | dtm | tod | cnt | ctn | afx | idn | txt | jnd | nwl |
|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| `levels` | | | ● | ● | ● | ● | | | | | | | | | |
| `suppressed_levels` | | | ● | ● | ● | ● | | | | | | | | | |
| `suppressed_rows` | | | ● | ● | ● | ● | | | | | | | | | |
| `suppressed_numbers` | | | ● | ● | ● | ● | | | | | | | | | |
| `level_ceiling` | | | | | ● | | | | | | | | | | |
| `format` | | | | | | | ● | | | | | | | | |
| `resolution` | | | | | | | ● | | | | | | | | |
| `resolution_mix` | | | | | | | ● | | | | | | | | |
| `datetime_separators` | | | | | | | ● | | | | | | | | |
| `all_at_midnight` | | | | | | | ● | | | | | | | | |
| `n_at_midnight` | | | | | | | ● | | | | | | | | |
| `date_field_widths` | | | | | | | ● | | | | | | | | |
| `month_name_styles` | | | | | | | ● | | | | | | | | |
| `quarter_marker_case` | | | | | | | ● | | | | | | | | |
| `zulu_case` | | | | | | | ● | | | | | | | | |
| `time_precision` | | | | | | | ● | | | | | | | | |
| `subsecond_digits` | | | | | | | ● | | | | | | | | |
| `datetimes_read_at` | | | | | | | ● | | | | | | | | |
| `earliest` | | | | | | | ● | ● | | | | | | | |
| `latest` | | | | | | | ● | ● | | | | | | | |
| `earliest_utc_offset` | | | | | | | ● | | | | | | | | |
| `latest_utc_offset` | | | | | | | ● | | | | | | | | |
| `date_percentiles` | | | | | | | ● | | | | | | | | |
| `utc_offsets` | | | | | | | ● | | | | | | | | |
| `n_unparsed` | | | | | | | ● | ● | | | | | | ● | |
| `clock_form` | | | | | | | | ● | | | | | | | |
| `clock_percentiles` | | | | | | | | ● | | | | | | | |
| `percentiles` | | | | | | | | | ● | ● | ● | | | | |
| `percentiles_between` | | | | | | | | | ● | ● | ● | | | | |
| `mean` | | | | | | | | | ● | ● | ● | | | | |
| `std` | | | | | | | | | ● | ● | ● | | | | |
| `skew` | | | | | | | | | ● | ● | ● | | | | |
| `kurtosis` | | | | | | | | | ● | ● | ● | | | | |
| `n_distinct_values` | | | | | | | | | ● | ● | ● | | | | |
| `mode` | | | | | | | | | ● | ● | ● | | | | |
| `mode_count` | | | | | | | | | ● | ● | ● | | | | |
| `std_unrepresentable` | | | | | | | | | ● | ● | ● | | | | |
| `n_zero` | | | | | | | | | ● | ● | ● | | | | |
| `n_negative` | | ● | | | | | | | ● | ● | ● | | | | |
| `n_negative_unrepresentable` | | | | | | | | | ● | ● | ● | | | | |
| `n_used_in_statistics` | | | | | | | | | ● | ● | ● | | | | |
| `n_left_out_of_statistics` | | | | | | | | | ● | ● | ● | | | | |
| `numeric_share` | | | | | | | | | ● | ● | ● | | | | |
| `integer_valued` | | | | | | | | | ● | ● | ● | | | | |
| `n_rows` (echo) | | | | | | | | | ● | ● | ● | | | | |
| `numeric_styles` | | | | | | | | | ● | ● | ● | | | | |
| `group_separator` | | | | | | | | | ● | ● | ● | | | | |
| `negative_form` | | | | | | | | | ● | ● | ● | | | | |
| `wide_runs` | | | | | | | | | ● | ● | ● | | | | |
| `decimal_plus` | | | | | | | | | ● | ● | ● | | | | |
| `negative_notations` | | | | | | | | | ● | ● | ● | | | | |
| `thousands_marks` | | | | | | | | | ● | ● | ● | | | | |
| `fraction_widths` | | | | | | | | | ● | ● | ● | | | | |
| `pad_widths` | | | | | | | | | ● | ● | ● | | | | |
| `field_widths` | | | | | | | | | ● | ● | ● | | | | |
| `value_histogram` | | | | | | | | | ● | ● | ● | | | | |
| `empty_bins` | | | | | | | | | ● | ● | ● | | | | |
| `empty_edges` | | | | | | | | | ● | ● | ● | | | | |
| `number_spellings` | | | | | | | | | ● | | | | | | |
| `affix_prefix` | | | | | | | | | | | ● | | | | |
| `affix_variants` | | | | | | | | | | | ● | | | | |
| `n_core_distinct` | | | | | | | | | | | ● | | | | |
| `n_core_distinct_folded` | | | | | | | | | | | ● | | | | |
| `affix_suffix` | | | | | | | | | | | ● | | | | |
| `n_affixed` | | | | | | | | | | | ● | | | | |
| `n_core_numeric` | | | | | | | | | | | ● | | | | |
| `n_core_out_of_range` | | | | | | | | | | | ● | | | | |
| `n_core_contradictory` | | | | | | | | | | | ● | | | | |
| `n_core_not_numeric` | | | | | | | | | | | ● | | | | |
| `n_whole` | | ● | | | | | | | | | | | | | |
| `n_fraction` | | ● | | | | | | | | | | | | | |
| `n_whole_unknown` | | ● | | | | | | | | | | | | | |
| `n_positive` | | ● | | | | | | | | | | | | | |
| `n_sign_unknown` | | ● | | | | | | | | | | | | | |
| `min_length` | | ● | | | | | | | | | | ● | | | |
| `max_length` | | ● | | | | | | | | | | ● | | | |
| `all_whole_numbers` | | | | | | | | | | | | ● | | | |
| `layout_forms` | | | | | | | | | | | | ● | | | |
| `layout_prefixes` | | | | | | | | | | | | ● | | | |
| `length` | | | | | | | | | | | | | ● | | |
| `words` | | | | | | | | | | | | | ● | | |
| `n_all_digits` | | | | | | | | | | | | ● | ● | | |
| `n_code_alphabet` | | | | | | | | | | | | ● | ● | | |
| `n_distinct_by_occurrences` | | ● | | | | | | | | | | ● | ● | | |
| `shape_forms` | | | ● | ● | ● | ● | | | | | | | ● | | |
| `n_joined` | | | | | | | | | | | | | | ● | |
| `n_parts` | | | | | | | | | | | | | | ● | |
| `part_above` | | | | | | | | | | | | | | ● | |
| `part_agreements` | | | | | | | | | | | | | | ● | |
| `part_min_widths` | | | | | | | | | | | | | | ● | |
| `parts` | | | | | | | | | | | | | | ● | |
| `separator` | | | | | | | | | | | | | | ● | |
| `n_numeric_cells` | | | | | | | | | | | | | | | ● |
| `n_numeric_out_of_range` | | | | | | | | | | | | | | | ● |
| `n_numeric_contradictory` | | | | | | | | | | | | | | | ● |
| `n_label_cells` | | | | | | | | | | | | | | | ● |
| `n_numeric_distinct` | | | | | | | | | | | | | | | ● |
| `n_numeric_distinct_folded` | | | | | | | | | | | | | | | ● |
| `numbers` | | | | | | | | | | | | | | | ● |
| `labels` | | | | | | | | | | | | | | | ● |

**One hundred rows, one hundred and eighty-nine marked cells**,
distributed `empty` 0, `numeric_unrepresentable` 9, `constant` 5,
`binary` 5, `categorical` 6, `long_tail_labels` 5, `datetime` 20,
`time_of_day` 5, `count` 32, `continuous` 31, `affixed_number` 41,
`identifier` 8, `free_text` 6, `joined_numbers` 8,
`numbers_with_labels` 8. The counts are stated so that a reader can
check a column of the matrix against the role's own section without
counting twice.

**RESTATED AT THE POOLED-SCALE LANDING** (2026-09-21, plan P4-D301):
`suppressed_numbers` is one row and one mark on each of the four label
roles, so the rows go from ninety-nine to a hundred and the marked
cells from a hundred and eighty-five to a hundred and eighty-nine.

**THE COUNTS WERE STALE AGAIN AND ARE CORRECTED AGAIN** (landing
2b.18). They were `Eighty-seven rows, one hundred and sixty-six marked
cells` while the matrix held ninety and one hundred and seventy-three
BEFORE this landing's own row was added, and the per-role breakdown was
short on four roles at once — `datetime` 15 against 16, `count` and
`continuous` 26 against 28, `affixed_number` 36 against 38. This
landing added `layout_forms` to the `idn` column, which made the
sentence wrong in a new way as well as an old one, so both are repaired
here and the numbers above are taken from the matrix by
`tests/test_p4d18_role_topology.py` rather than counted by hand. The owner's ruling of 2026-09-17 (item 2, option A; plan
P4-D201) then withdrew the `suppressed_level_counts` row, one mark on
each of the four label roles, and item 1 of the same ruling (plan
P4-D202) added the `layout_prefixes` row, one mark on `identifier`.

**AND RESTATED AT THE INTEGRATION OF LANDINGS 2b.6 TO 2b.8**
(2026-09-16). Landing 2b.6 added four keys to `datetime` and marked none
of them here, landing 2b.7 added three rows to the numeric columns, and
landing 2b.18 added `layout_forms` and `number_spellings`; the merged
matrix marks all nine, and the numbers above are its own.

**THE PER-ROLE COUNTS WERE STALE AND ARE CORRECTED HERE**, which is
recorded rather than quietly repaired. The total has been right at
every landing, and the guard in
`tests/test_p4d18_role_topology.py` checks the total; the breakdown
said `count` 18, `continuous` 18 and `affixed_number` 25 while the
matrix held 24, 24 and 31, and named no column for `joined_numbers`
at all. One fact written twice, one half updated.

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
  `numeric_styles`, with `fraction_widths`, `pad_widths` and
  `field_widths` beside it —
  describes the CORES, not the cells. The four universal cell-census counts answer
  for the cells on that role as on every other, and the cores have
  four counts of their own beginning with `n_core_numeric` (C6-7).
  Every quantitative invariant this format states over `n_numeric` is
  read on that role over `n_core_numeric`, and nowhere else (AF7).

**Four confinements this matrix is where a reader finds enforced.**
`numeric_styles`, `fraction_widths`, `pad_widths` and `field_widths`
stand on exactly `count`, `continuous` and `affixed_number`, and are
forbidden everywhere else including `numeric_unrepresentable`. `shape_forms`
stands on exactly the four LABEL roles and `free_text` — every role
whose twin can hold a made-up spelling in place of one the floor held
back — and is forbidden on the other eight (7.9). `level_ceiling` stands on
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

**C6-5a (the space belongs to the WRAPPER).** The classifier trims, so
the longest parsing substring of `5 mg` is `5 ` and not `5`. The split
then moves every edge character of the core for which
`parsing.trimmed` reads nothing — the plain space, the tab, the
no-break space, the em space, every kind — OUT of the core and into
the side it touches. So `5 mg` splits as prefix `""`, core `5`, suffix
`" mg"`.

This document said the opposite until 2026-09-05, and the code did the
opposite with it. The value stage rewrites a core as a NUMBER and has
no space to write, so **every column of this role lost the space before
its unit**: a source cell of `165.1 mg` came back `165.1mg`, on all 240
cells of the shipped demonstration and in a committed golden, and a
person splitting the twin on a space got one field where their own
table gives two.

A consequence a reader will not assume: `5mg` and `5 mg` wear DIFFERENT
wrappers — `mg` and `" mg"` — and a column holding both wears a set of
two. It was one pair under the old rule. Whether such a column takes
this role is settled by the test below like any other set.

**C6-5 (the pair's identity).** The pair is the EXACT text of the
trimmed cell on either side of the core — no case folding, no inner
trimming. `mg` and `MG` are two pairs and not one, and so are `$` and
`EUR`.

**The test.** A column takes this role when no earlier rule has
claimed it and both of these hold:

1. at least the parse-line count of its present cells are affixed
   numbers wearing a wrapper of ONE SMALL SET — the count
   `minimum_parse_rate` fixes (section 4.4), applied as a COUNT and
   never as a compared share, so no rounding of a division decides a
   role; and
2. every wrapper the description publishes is worn by at least
   `small_cell_floor` cells.

**The floor is read at DETECTION time, deliberately:** a wrapper is
published, so publishing a floor-clearing spelling is constitutive of
the role, and a column that cannot publish one under the recorded
settings takes the next rule instead. **The floor is read again over
what WEARS each wrapper**, because those are two populations: the cells
that propose a wrapper are the ones that read as a number wearing it,
and the cells that wear it are more or fewer. A column of `$1` to
`$99` beside eleven cells spelled `1`, with `1` declared a hole,
proposes the bare wrapper twelve times and is worn by it once. A
wrapper failing the second reading is not published and its cells are
STRAGGLERS.

**C6-7a (a column may wear a SET of wrappers).** Until 2026-09-05 this
document required ONE pair and said a column wearing more "declines to
the later rules". That rule cost the shape this role most needs to
reach: a laboratory column of `13.5`, `4.2 H` and `9.8 L` wears three
wrappers, no one of them reaches the parse line, and the whole column
fell to free text — no ladder, no mean, no distribution, nothing about
a haemoglobin reading at all.

So the vocabulary is a SET, under five conditions. The commonest
wrapper is published under `affix_prefix` and `affix_suffix`, unchanged,
so a column wearing ONE is described exactly as it was. Every other is
an entry of `affix_variants`.

1. **The BARE wrapper is a member of the vocabulary** — nothing on
   either side — proposed by a cell that reads as a number wearing
   nothing and worn only by such a cell. It may be the commonest one,
   and on the shape above it usually is, because most laboratory
   results carry no flag. It cannot be the WHOLE vocabulary: a column
   whose every cell wears nothing is a column of bare numbers, which
   is a different role (AF1).
2. **No wrapper of a SET may carry a digit.** A column of feet and
   inches proposes one wrapper per inches value and a dozen clear the
   floor together, and the column then published a ladder over the
   feet of some cells and the inches of others. A column wearing ONE
   wrapper may carry digits — `mL/min/1.73m2` is a real unit — so this
   is asked of a set alone.
3. **No wrapper of a SET may put a LETTER flush in FRONT of the
   digits.** That is where a code scheme puts its letter — `E10.0`,
   `I11.2`, `J44.9`, `D0140` — and reading the rest as a quantity
   publishes a ladder over code numbers and writes codes nobody
   issued. No declaration reaches this half of the rule.

   **BEHIND the digits a flush letter is AMBIGUOUS, and the person
   settles it with `--measurement`.** `13.5H` is an abnormal flag on a
   laboratory result and `1234F` is a category of procedure code, and
   nothing in the text tells them apart. Two automatic rules were
   written and both were measured wrong: refusing the shape outright
   sent every laboratory column whose flags are written flush to free
   text, and admitting it where the cores are not all of one width
   refused an ordinary column of two-digit readings while admitting a
   register whose bare codes had lost their leading zeros to a
   spreadsheet. Undeclared, such a column is read as it was before this
   role was widened; declared, its wrappers are read like any other.

   A letter that STANDS APART — `13.5 H` — needs no declaration: a code
   register does not put a space before its category letter.
4. **Every wrapper of a SET is ONE WORD.** A unit or an annotation is
   a word — `H`, `kg`, `months`, `EUR`, `$`; a sentence is not. A
   column of `free comment number 03 written out` beside its
   upper-case variants proposes two wrappers of four words each, both
   clearing the floor, and published a ladder over a sequence number
   inside prose.
5. **Every wrapper's cores are written like the commonest wrapper's**,
   with a point where those have one.

A column failing any of these declines to the later rules exactly as
it did, and its competing-readings remark says how far the affix
reading got (section 4.5, the form `remark_no_reading_fits`,
argument 6).

**C6-7b (every published wrapper carries its own numbers).** A column
wearing a set published ONE quantitative block over ALL its cores
until the owner's ruling of 2026-09-08, and that is a statistic of no
quantity where the wrappers are units: a hundred weights written
`60.0 kg` to `69.9 kg` beside a hundred written `132.3 lb` to
`153.8 lb` published **mean 104.722**, with the column's ends running
from 60 to 153.8.

So each published wrapper carries a quantitative block read over its
own cores, on the arrangement `joined`'s positions already have
(section 6.14): **the block a wrapper carries echoes that wrapper's
own count in `n_rows`, and every population key in it — its ladder,
its moments, its spelling census, `n_used_in_statistics`,
`n_left_out_of_statistics` and `numeric_share` — answers for that
wrapper's cells and for no others.**

The COLUMN's own block is the COMMONEST wrapper's. On a column wearing
one wrapper that is every core it holds, so nothing about such a column
moves; on a column wearing a set it is the commonest wrapper's cells,
and its `n_rows` echoes their count rather than the table's. **There is
no pooled ladder, mean or histogram over a column wearing more than one
wrapper**, and that is deliberate: such a number is either the same as
the parts, where the wrappers share a scale, or a statistic of nothing,
where they do not, and this format cannot tell which.

The counts that are COUNTS stay whole. `n_affixed` and the four
`n_core_*` classes answer for every counted cell and close on
`n_affixed` (AF4) — a count of how many cores read as numbers is true
whatever scale those numbers are on. `n_core_distinct` and
`n_core_distinct_folded` belong to the block above them and are
therefore the COMMONEST wrapper's, with each other wrapper's pair
beside its own block: a count of different things does not subtract, so
a commonest wrapper's budget could not be recovered from a column total
and the others'.

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

**AND A WHOLE-CELL DECLARATION CARRIED ACROSS THE PAIR PROTECTS THE
CANDIDATE NUMBER, HENCE EVERY SPELLING OF IT IN THIS COLUMN**
(residual R-P4-22, closed 2026-08-26). The code has done this since
A-P4-19 and a test pins it; this document was silent, and a reader
following the declaration-matching rule alone would expect a rescue
granular to the SPELLING, which the wire cannot represent. It cannot
because what a column publishes about a stand-in candidate is the
NUMBER and its count, with no room for "this spelling of it was
declared and that one was not". So the declaration is carried at the
number: naming `-999` protects `-999` wherever it appears in this
column, in any spelling of that number, and naming `-999 mg` protects
the cell spelled that way. That is wider than a spelling-granular rule
would be and is stated here so nobody reads the narrower one into it.

#### C6-6. Added keys: thirty-six

TEN of this role's own, and the TWENTY-SIX a `count` or
`continuous` block carries, the quantitative ones computed over the
CORES of the COMMONEST wrapper (C6-7b). Ten and twenty-six make the
thirty-six the block-size sentence below already states, and
`AFFIXED_KEYS` in the loader holds exactly those thirty-six.

**THIS COUNT HAS BEEN WRONG TWICE AND IN TWO DIFFERENT WAYS.** It read
"seven" and "twenty-three" until 2026-09-08, three keys after the
wrapper set added them; the repair moved the role's own half to ten and
left the numeric half at "sixteen", a number no version of this
document has been able to justify against `NUMERIC_KEYS`, which held
twenty-five then. An independent producer following "sixteen" wrote a
block missing nine obligations the loader requires.

**Each entry of `affix_variants` carries ten keys of its own**: its two
spellings, its `count`, its four class counts, its two counts of
different cores, and a `numbers` block holding exactly the TWENTY-SIX
keys a `count` or `continuous` block holds — the same set, read over
that wrapper's cores, echoing that wrapper's `count` in `n_rows`. No
entry carries an eleventh key, and a description whose entry does is
refused rather than read.

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
| `percentiles_between` | object of ninety rungs | Q19 | the same ninety rungs read over the CORES | REPORT-ONLY, as on `count` |
| `mean` | number or `null` | — | arithmetic mean of the parsed CORES | APPROXIMATED, as on `count` |
| `std` | number or `null` | ≥ 0 when a number | sample standard deviation of the parsed CORES, divided by n−1 | APPROXIMATED, as on `count` |
| `skew` | number or `null` | — | moment-based skewness of the parsed CORES | APPROXIMATED, as on `count` |
| `kurtosis` | number or `null` | Q16 | moment-based kurtosis of the parsed CORES | APPROXIMATED, as on `count` |
| `n_distinct_values` | whole number | Q17 | how many different NUMBERS the CORES hold | EXACT-OBSERVABLE (amendment A-P4-55) |
| `mode` | number or null | Q18 | the number the CORES held most often | REPORT-ONLY |
| `mode_count` | whole number | Q18 | how many cores held it | REPORT-ONLY |
| `std_unrepresentable` | boolean | — | true when the CORES' exact spread exceeds binary64 | EXACT-OBSERVABLE |
| `n_zero` | integer ≥ 0 | — | parsed CORES equal to zero | EXACT-OBSERVABLE |
| `n_negative` | integer ≥ 0 | — | CORES whose notation settles a negative sign, including ones no statistic could use | EXACT-OBSERVABLE |
| `n_negative_unrepresentable` | integer ≥ 0 | — | out-of-range CORES whose notation settles a negative sign | EXACT-OBSERVABLE |
| `n_used_in_statistics` | integer ≥ 0 | — | cells of the COMMONEST wrapper that contributed a core to the statistics | EXACT-OBSERVABLE |
| `n_left_out_of_statistics` | integer ≥ 0 | — | cells of that same population that did not | EXACT-OBSERVABLE |
| `numeric_share` | number | 0.0 ≤ x ≤ 1.0 | share of them whose writer meant a number, read over the cores | EXACT-OBSERVABLE |
| `integer_valued` | boolean | — | true when every numeric-looking CORE is whole | EXACT-OBSERVABLE, routed by the FACT and not by role |
| `n_rows` | integer ≥ 0 | the table's row count where ONE wrapper is worn; the COMMONEST wrapper's own count where a SET is (C6-7b, AF13) | the row count of the population this block describes, echoed | LOADER-ONLY |
| `numeric_styles` | object | section 7.5 | CORES per spelling style, under the floor | EXACT-OBSERVABLE, recount identity of section 7.5.7 |
| `group_separator` | string | as on `count` and `continuous`, and `"."` only where the column is named in `settings.forced_decimal_commas` | the mark between thousands the CORES were written with, under the same evidence rule as on `count` and `continuous` (GS1). Since landing 2b.16 the declaration reaches this role's cores, so the point stands here under exactly the condition it stands under on a plain numeric column and never otherwise. **THE LIMIT THIS ROW CARRIED IS CLOSED (plan P4-D108, landing 2b.16's repair pass).** A declared column whose cores group their thousands with a point — `645.121,62 EUR` — published `""` about a column where 800 of 800 cells carried the mark, and its twin wrote the value ungrouped, `62391,86 EUR`, at exit 0 on BOTH files with nothing missed, so a spelling every real cell wore was lost in silence. **The cause was not the reading**, which keeps the core's own text and was measured doing so: it was the TALLY the cores are counted into. The cores are classified under the declaration and the record built from them was built without it, so every rule that asks the record which grammar this column writes — this one above all — answered for an undeclared column. The record now carries the declaration its cells were classified under, and the point stands here under exactly the condition it stands under on a plain numeric column and never otherwise. Measured after it, 800 cells at floor eleven, seeds 1 and 7: `group_separator: "."`, `thousands_marks: {".": 800}`, the twin writes `62.391,86 EUR` with 800 of 800 grouped, the twin's own re-description returns the mark, and both files exit 0 with nothing missed | EXACT-OBSERVABLE (plan P4-D41, P4-D106, P4-D108) |
| `negative_form` | string | as on `count` and `continuous` | how the CORES write their negative numbers, under the same rule; brackets inside the wrapper, `$(1,234.56)`, are the core's own. Brackets around the wrapper too, `($1,234.56)`, are part of the wrapper and carry NF56 | EXACT-OBSERVABLE (plan P4-D41) |
| `wide_runs` | string | as on `count` and `continuous` | whether the CORES' wide runs of figures are the text their own values write, under the same rule and read over the cores | EXACT-OBSERVABLE (plan P4-D90) |
| `decimal_plus` | object | as on `count` and `continuous` | how many CORES written with a point carried a plus | EXACT-OBSERVABLE (plan P4-D41, P4-D65.1) |
| `negative_notations` | object | as on `count` and `continuous` | how many negative CORES wore each notation, under the same census floor (NS2) | EXACT-OBSERVABLE (plan P4-D65.2) |
| `thousands_marks` | object | as on `count` and `continuous` | how many grouped CORES wore each mark, under the same census floor (TM1) | EXACT-OBSERVABLE (plan P4-D65.2) |
| `fraction_widths` | object | C6-27 to C6-30 | `decimal`-styled CORES per fraction width, under the floor | EXACT-OBSERVABLE |
| `pad_widths` | object | C6-27b to C6-30b | `leading_zero`-styled CORES per field width, under the floor | EXACT-OBSERVABLE |
| `field_widths` | object | C6-27c to C6-30c | whole-written CORES per field width, under the floor | REPORT-ONLY |
| `value_histogram` | object | C6-31 | the CORES falling in each bin between the core ends; published only when every bin clears the floor | REPORT-ONLY |
| `empty_bins` | array | C6-122 to C6-123 | which of those same bins hold none of the CORES, ascending; published whatever the floor is | REPORT-ONLY |
| `empty_edges` | array | C6-123a to C6-123b | one `[below, above]` pair per run of those empty bins, read over the CORES | REPORT-ONLY |
| `affix_variants` | array | C6-7a below | the OTHER wrappers this column's cells wear, each with the count wearing it, ascending by their own text; empty on a column wearing one | EXACT-OBSERVABLE |
| `n_core_distinct` | count | AF10 | how many DIFFERENT cores the cells carry | EXACT-OBSERVABLE |
| `n_core_distinct_folded` | count | AF10 | the same over the folded identities | EXACT-OBSERVABLE |
| `affix_variants[].prefix` | string | possibly empty | the exact text cells wearing this wrapper carry before their core | EXACT-OBSERVABLE |
| `affix_variants[].suffix` | string | possibly empty | the exact text they carry after it | EXACT-OBSERVABLE |
| `affix_variants[].count` | integer | `small_cell_floor` .. `n_rows` | CELLS wearing this wrapper | EXACT-OBSERVABLE |
| `affix_variants[].n_core_numeric` | count | AF11 | its CORES reading as a number this format can hold | EXACT-OBSERVABLE |
| `affix_variants[].n_core_out_of_range` | count | AF11 | its CORES too large or too small to hold | EXACT-OBSERVABLE |
| `affix_variants[].n_core_contradictory` | count | AF11 | its CORES whose written form contradicts itself | EXACT-OBSERVABLE |
| `affix_variants[].n_core_not_numeric` | count | AF11 | its CORES that are no number at all | EXACT-OBSERVABLE |
| `affix_variants[].n_core_distinct` | count | AF11 | how many DIFFERENT cores this wrapper's cells carry | EXACT-OBSERVABLE |
| `affix_variants[].n_core_distinct_folded` | count | AF11 | the same over the folded identities | EXACT-OBSERVABLE |
| `affix_variants[].numbers` | object | AF13 | the thirty-one keys of a `continuous` block, read over this wrapper's cores and echoing its `count` in `n_rows` | as on `count` and `continuous` |

**The block is sixty-three keys**: the twenty-two universal keys of
section 5.1 and the forty-one above — a `continuous` block's thirty-one
additions plus this role's own ten; a `count` block's own thirty-second,
`number_spellings`, is not among them. The matrix of section 6.11 marks
exactly those forty-one cells in its `afx` column. (These numerals
read fifty-eight, thirty-six and twenty-six until landing 2b.18's
second part, two keys behind the loader since landing 2b.2, and were
restated from the loader's merged tuples at the integration of
landings 2b.6 to 2b.8.) There is no
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

**AF1.** `affix_prefix` and `affix_suffix` are not both empty, UNLESS
`affix_variants` is non-empty. The bare wrapper is a member of a
vocabulary and may be the commonest member of one (C6-7a), and on a
laboratory column of readings beside abnormal flags it usually is. It
cannot be the whole of a vocabulary: at least one published wrapper
carries text, because a column whose every cell wears nothing is a
column of bare numbers and that is a different role.

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

**AF9.** `affix_variants` names each wrapper once, ascending by its own
text, each with a count of at least `small_cell_floor` and at most
`n_rows`; none of them is the pair `affix_prefix`/`affix_suffix` names
(AF14).

**AF10.** `1 <= n_core_distinct <= ` the COMMONEST wrapper's own count,
which is `n_affixed` less every entry's `count`; and
`1 <= n_core_distinct_folded <= n_core_distinct`. These two belong to
the column's block, that block is the commonest wrapper's (C6-7b), and
bounding them by `n_affixed` let a description say a wrapper worn by
sixty cells holds two hundred different cores — a budget the core stage
would then be laid out from. A published zero is a description no
column wrote.

**AF11.** Each entry of `affix_variants` carries its own four class
counts and they close on that entry's `count`, exactly as AF4 closes
the column's four on `n_affixed`; and `1 <= n_core_distinct <= count`
within the entry, with the folded count bounded by the raw one.

**AF12.** The commonest wrapper's own count — `n_affixed` less every
entry's `count` — is at least `small_cell_floor` wherever
`affix_variants` is non-empty. It is published like any other wrapper,
and a wrapper worn by fewer cells than may be named is not published at
all. This also refuses a set of counts summing above `n_affixed`,
whose remainder is negative.

**AF13.** Each entry's `numbers` block satisfies section 6.7's
invariants over that entry's own counts, and echoes that entry's
`count` in `n_rows` — the reading `joined` positions take (C6-7b).

**AF14.** No wrapper is named twice across the whole vocabulary. AF9
orders the entries and so refuses a duplicate among them; the commonest
pair is read elsewhere, so a variant repeating it satisfied both.

**AF15.** The vocabulary holds no more wrappers than a set of
categories may hold levels on this table — `1 + len(affix_variants)` is
at most the category ceiling of section 4.4. A wrapper is published
text drawn from the table, so what bounds how many may be named is what
bounds how many levels a categorical column may name.

**AF7.** Every quantitative key above obeys the invariant section 6.7
states for it on `count` and `continuous`, read over the CORES **of the
population the block it sits in describes** (C6-7b; review round 4,
item 7).

For a column wearing ONE wrapper that population is every counted core
and every reading below is unchanged, which is every column of this
role until a set is worn. For a column wearing a SET it is not: the
column's own block describes the COMMONEST wrapper's cores and each
entry's block describes that entry's, so `n_rows`, `n_used_in
_statistics`, `n_left_out_of_statistics` and `numeric_share` answer for
that wrapper's cells and Q1 is read against that wrapper's count rather
than the table's. A consumer that adds the wrappers' populations gets
the column's counted cells; one that reads the column's block as
covering them all gets a description of the commonest wrapper and
nothing about the rest.


Wherever such an invariant names a cell-census count it is read here
over the matching core-class count — `n_core_numeric` for `n_numeric`,
`n_core_out_of_range` for `n_out_of_range`, `n_core_contradictory` for
`n_contradictory` — and over no other count.

**`n_present` and `n_rows` READ FOR THE BLOCK'S OWN POPULATION** (C6-7b;
review round 5, item 6). On a column wearing ONE wrapper that is the
column's cells and the table's row count, which is what this paragraph
said and what every column of this role meant until a set could be
worn. On a column wearing a SET it is the wrapper the block belongs
to: the column's own block reads for the COMMONEST wrapper's cells and
echoes their count, and each entry's block reads for that entry's and
echoes its `count`. The six readings below are written for the
one-wrapper column, and on a set each is read with the block's own
population standing where `n_present` and `n_rows` stand here:

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
something the generator can discharge. `pad_widths` is REQUIRED here
on the same terms and for the same reason, its census likewise a census
of the CORES: a padded record number behind a prefix is a fixed-width
code exactly as a bare one is, and a twin that wrote its core at
another width would break the same length check. `field_widths` is
REQUIRED here on those same terms and is likewise a census of the
CORES: a dental code `D0120` beside a `D1110` is a column of
four-figure cores whether or not a core wears a redundant zero, and
that is the shape residual R-P4-30 was opened on. `fraction_widths`
sits beside it
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

**The all-different remark this role carries is NF32, the NUMBERS
form, and this clause names it** (residual R-P4-21, closed 2026-08-26).
The contract said "the wording section 4.5 fixes" without saying WHICH
of the two all-different forms, and the plainest-language parts of the
plan and of the derivation notes said the remark extends to this role
"verbatim", which reads as NF34, the TEXT form. The shipped producer
emits NF32 and is right to: NF34 says "nothing from this column is
published either way -- no value of it, and no distribution", which is
FALSE of an affixed column, whose distribution is published over its
cores. A false sentence in the plainest-language part of a document is
the one thing that may not stand, so the text catches up with the code
rather than the other way round.

The remark reaches this role on its own trigger, in NF32's wording and
no other; and the block
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
forms the `month-first-datetime`, `day-first-datetime` and
`slashed-iso-datetime` members of the format vocabulary read as the
tail of a slashed date; they are
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

- **The other thirteen datetime keys.** `format`, `resolution`,
  `resolution_mix`, `time_precision`, `subsecond_digits`,
  `datetimes_read_at`, `earliest_utc_offset`, `latest_utc_offset`,
  `date_percentiles`, `utc_offsets`, `datetime_separators`,
  `all_at_midnight` and `n_at_midnight` are `datetime`'s. `clock_form`
  answers the form question here, and a clock with no date carries no
  zone: an offset moves an instant, and this role publishes none.
- **Every quantitative key.** `percentiles`, `mean`, `std`, `skew`,
  `numeric_styles`, `fraction_widths`, `integer_valued` and the rest
  belong to `count`, `continuous` and `affixed_number`, as does the
  per-column `n_rows` echo, which Q1 confines to those three.
- **Every label key.** `levels`, `suppressed_levels` and
  `suppressed_rows` belong to the four
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
other. At a floor of `11` the two terms coincide. Raising
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
`suppressed_levels`; `suppressed_rows`; and
`shape_forms`, the census of written forms section 7.9 states. Their
JSON types and meanings are section 6.3's, identically, and `variants`
and `variants_withheld` are specified in full in section 7.4.

**The census is not this role's own key, and the record of why says
so.** It stood here alone for one landing, on the reasoning that the
other three label roles publish every level the floor admits, so their
twins hold the column's own spellings and have nothing whose shape
needs describing. That reasoning was wrong: every label role suppresses
levels, and whether it does is a fact about the FLOOR rather than about
the role. A `categorical` column of five common diagnosis codes and
twenty-six rare ones is the case the census was raised for, and it is
not this role (A-P4-36, P4-D18, and the correction recorded with it).

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
completeness), B4 (the held-back pool), B4b (the pool a reader subtracts), B5 (the floor), B6 (label order), B7 (labels are distinct) and B8 (levels may
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
`suppressed_levels` and `suppressed_rows` are EXACT-OBSERVABLE, as
section 6.3.2 states for every label role: the twin writes each
published label at exactly its count and invents that many neutral
labels covering the pooled rows together, at the sizes the generation
method reads off the pool. The published
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
- **The NUMBER and the POOLED ROWS of the BELOW-FLOOR folded
  identities**, through `suppressed_levels` and `suppressed_rows`.
  Until the owner's ruling of 2026-09-17 (item 2, option A; plan
  P4-D201) the size of each one was published too, as a sorted array,
  which told a reader which unnamed spellings shared a trim-and-case
  identity; that array is withdrawn, and what remains is two counts
  about the unnamed groups taken together — never a spelling, and never
  the size of any one of them.

**Document size, stated rather than found later.** The pool is two
integers whatever the number of below-floor levels, so this role's
block no longer grows with them.

### 6.15 `joined_numbers`

**What the role is.** A column whose cells each hold TWO OR MORE
numbers written in one cell and joined by one repeated separator: a
blood pressure `120/80`, a ventilator ratio `1:1.5`, a pressure charted
`120 / 80`. Each position is described as a quantity of its own.

**A part is not required to be WHOLE**, and this document said it was
until 2026-08-26 while offering `1:1.5` as an example in the same
sentence. A part is one or more ASCII figures which may carry at most
one decimal point, and that point may be neither the first character
nor the last; a part with no figure, two points, an exponent or a sign
is refused and the cell is not read by this role.

**IT IS REACHED BY DECLARATION, AND FROM THE VALUES IN ONE SHAPE
ONLY**, and the reason is a measurement rather than a caution (plan
P4-D21, narrowed by P4-D40 on 2026-09-15). A rule reading every joined
shape from the values would claim a date (`2023-02-12` is three whole
numbers joined by `-`), a clock time (`09:30` is two joined by `:`),
and — past any rule order that could save those two — a laboratory code
(`1923-1`) and a drug code (`00052-0052-52`), which are CODES.
Claiming those would describe each of their parts as a quantity --
publishing its ladder, its two groups of outer rows and any end enough
rows share, all of them fragments of real codes. So the full reading of
this section is the person's to ask for, with `--measurement`.

**The one shape read without the declaration** is rule 12 of section
5.2's order, tested last before `free_text`, so it claims only a column
that would otherwise publish nothing. At least the parse-line count of
the present cells are each exactly TWO parts joined by a slash — the
separator `/`, `/ ` or ` / ` — and each part is figures alone with no
point, no sign, and no leading zero on a part of two or more figures.
Every other present cell is counted in `n_unparsed`. None of the
columns P4-D21 measured wears that shape: the full date and the clock are
claimed by earlier rules, both codes are joined by a hyphen and one is
padded, and a part carrying a point is left to the declaration. A
blood pressure written `128/79` was `free_text` at 300 rows and at
2,000 until this rule, so its twin held stand-in text and neither
position was described. A coding system written as two slashed figures
is still a code this rule cannot tell from a measurement, so every
column read this way is asked about in the questions file, with codes
and record numbers offered beside the reading taken.

**What rule 12 does not reach, stated at its size.** It stands after
`long_tail_labels`, so a column of such pairs in which one whole reading
covers the long-tail line (the publication floor or eleven, whichever is
larger) is a long tail and not this role. Measured on 2026-09-15: a
blood pressure of 6,000 or 12,000 rows, and one charted to the nearest 5
at 300 and 2,000 rows, is `long_tail_labels`, so neither position is
described; between about 3,500 and 5,000 rows of plain readings, and
1,200 and 1,600 of readings charted to the nearest even number, which of
the two roles a column takes turns on its sample. The declaration reads
every one of them. Nor is every slashed pair a date: a month and year
written without padding (`4/2020`) is no date form this contract reads,
so a column of them that no earlier rule claims is read by rule 12, and
so is a register number written as year and serial (`2019/4821`); both
are asked about. A file checked against a description that took this
reading from the values is read the same way, ahead of the long-tail
rule (validation method V2.2-A2), so a faithful twin whose randomly
paired readings cross the line is not reported as another role.

**The eight keys this role adds**, and no ninth; the forbidden-key
matrix of 6.11 is what stops one:

| key | type | range | meaning |
| --- | --- | --- | --- |
| `separator` | string | one mark of `/ - : \| ; _`, with at most one space on each side | the whole text a cell is split on, written as the table wrote it |
| `n_parts` | integer | ≥ 2 | how many numbers a cell holds. One is a bare number, which is another role |
| `n_joined` | integer | ≥ the detection line, ≤ `n_present` | present cells that split this way |
| `n_unparsed` | integer | ≥ 0 | present cells that did not. `n_joined + n_unparsed == n_present` |
| `parts` | array of objects | exactly `n_parts` | one quantitative block per position, in cell order, each carrying exactly the keys of 6.7 and read over that position's numbers alone |
| `part_min_widths` | array of integers | exactly `n_parts`, each ≥ 1 | the smallest number of characters each position was written in. It is what tells a padded position (`007` beside `080`) from a plain one, and it is a width and never a spelling |
| `part_agreements` | array of numbers | exactly one per PAIR of positions, each −1 ≤ x ≤ 1 | how strongly two positions rise and fall together, by RANK, in the order (1,2), (1,3), … (2,3), … |
| `part_above` | array of integers | exactly one per pair, each ≤ `n_joined` | in how many rows the earlier position held the larger number |

**WHY THE LAST TWO ARE HERE AT ALL, and why they are about the PAIRING
and nothing else.** What each position holds is published exactly in
`parts`, so a description carrying only those says nothing about which
numbers met in a row — and a twin built from it draws each position
independently. Measured on four hundred readings whose real numbers
agreed at 0.83, such a twin agreed at −0.01 and held cells with a
diastolic at or above its systolic. Rank agreement is used rather than
agreement between values precisely because it repeats nothing `parts`
already carries: it does not move when a position's own numbers change,
only when the pairing does.

**Both are aggregates over every row and name no cell**, so this role
publishes exactly one spelling of the table — `separator` — on the same
terms `affixed_number` publishes its pair.

**The invariants a loader checks (J1–J8).**

| # | rule | checkable |
| --- | --- | --- |
| J1 | `separator` is one admitted mark with at most one space on each side | yes |
| J2 | `n_parts` ≥ 2 | yes |
| J3 | `n_joined + n_unparsed == n_present`, and `n_joined` clears the detection line the role's own reading had to clear | yes |
| J4 | `parts` and `part_min_widths` each hold exactly `n_parts` entries | yes |
| J5 | every entry of `parts` carries exactly the keys of 6.7 and satisfies that section's invariants over `n_joined` values | yes |
| J6 | every published width is at least one character | yes |
| J7 | `part_agreements` holds exactly one entry per pair of positions, each from −1 to 1 | yes |
| J8 | `part_above` holds exactly one entry per pair, each at most `n_joined` | yes |

**Publication class: RANGES** (6.10). No spelling of the table appears
except `separator`, and the forbidden-key rule is what confines it to
that key.

**What a twin owes, and the one thing it may not always reach.** Each
position's numbers follow that position's published block exactly, and
the pairing is chosen to meet `part_agreements`, `part_above` and the
column's own `n_distinct`. The three cannot always be met together:
numbers drawn to a published ladder repeat more evenly than a real
column's do, so fewer different pairs can be made from them. Where the
count of different cells falls short the twin REPORTS it. Residual
R-P4-40 records the cause and the fix, which is a description change
and not a generation one.

### 6.16 `numbers_with_labels`

**What the role is.** A column whose cells hold NUMBERS and WORDS in
one cell space: the long-format panel export, where `7.2` sits beside
`POSITIVE`, or a result column of readings beside `NOT DETECTED`.
Both populations are described, each in its own terms.

**Why the role exists, measured.** Such a column declined to
`long_tail_labels` before, and that decline is wrong in both
directions. On a 300-row column of 222 readings beside two markers: at
a floor of one every reading clears the line and is published as its
own LEVEL — 177 of them — so the description carries the readings
themselves; at a floor of eleven the levels fall to two and the twin
holds NO numeric cell at all. The protective setting destroys the
numeric population and the permissive one carries it verbatim.
Neither DESCRIBES it.

**The six keys.**

| key | type | what it holds |
|---|---|---|
| `n_numeric_cells` | count | present cells that read as ordinary numbers |
| `n_numeric_out_of_range` | count | present cells the number rules read as a numeral this format cannot hold — one too large or too small |
| `n_numeric_contradictory` | count | present cells whose notation contradicts itself, so no number can be read from them |
| `n_label_cells` | count | every other present cell |
| `n_numeric_distinct` | count | how many DIFFERENT written cells the numeric half holds |
| `n_numeric_distinct_folded` | count | the same over the folded identities |
| `numbers` | object | a quantitative block over the numeric cells, carrying what one position of a `joined_numbers` column carries |
| `labels` | object | a label block over the rest, carrying what a label-publishing column carries, plus `n_present` and `n_distinct_folded` of its own half |

**Invariant NL1.** `n_numeric_cells + n_numeric_out_of_range +
n_numeric_contradictory + n_label_cells == n_present`. Every present
cell is in exactly one of the three published populations and none is
in two. This is the whole answer to review item P1-R6-F7, which
deleted a rule that published a distribution over one population and
said nothing about the other: a reader checks the arithmetic rather
than trusting the prose.

**THERE ARE THREE POPULATIONS AND TWO SUB-BLOCKS**, and the third is
counted with the FIRST (residual R-P4-149, closed by the owner's
ruling of 2026-09-04). A cell the number rules recognise as a numeral
this format cannot hold IS a number, and it used to join the labels:
so a laboratory column of 280 readings with one `9e999` published that
cell as a WORD beside `positive`, and the numeric half reported nought
cells left out of its statistics on a column that had one. Worse at a
raised smallest-group size, where one such cell does not clear it: the
spelling was held back and the twin wrote `group-N` — a made-up word
where the source had a numeral.

Those cells now belong to the numeric half's population. The `numbers`
block's four class counts are the ones a plain numeric column
publishes and they sum to that half — `n_numeric` the usable cells,
`n_out_of_range` and `n_contradictory` these, and `n_not_numeric`
always nought, because a cell that is not a numeral at all is in the
label half. The half's `n_rows` echo is that same sum, and its
`n_left_out_of_statistics` says how many of its cells the statistics
could not use.

**Invariant NL2.** The `labels` block carries its OWN `n_present`,
`n_distinct` and `n_distinct_folded`, and B2 is stated over those. The column's own
counts include the numbers, so a reader checking the label half
against them would be checking the wrong sum.

**Invariant NL5.** Every published label of this role — a level's own
spelling and every variant of it — is a spelling that does NOT read as
an ordinary number under this column's own grammar, the decimal-comma
declaration included. The rule that makes the role puts a cell in the
label half exactly when it is not a number, so a label that IS one
describes a cell of the other half, and a description carrying it is
one no file can satisfy: the twin writes that spelling and
re-describing the twin counts it into the numeric half. Measured: a
description whose every label was `1` was accepted, and its twin held
294 numeric-looking cells against a published 274.

**Invariant NL4.** Both counts of the split are at least 1. A column
of this role holds BOTH populations; a description with an empty half
describes some other kind of column, and the loader refuses it rather
than reading a plain numeric description as this role.

**Invariant NL3.** `n_numeric_distinct_folded <= n_numeric_distinct <=
n_numeric_cells`, and `n_numeric_distinct <= n_distinct`. The four
counts of different cells are ONE arithmetic and each of these holds
as well: `numbers.n_distinct_values <= n_numeric_distinct_folded`,
because two different numbers are never written the same way;
`n_numeric_distinct_folded + labels.n_distinct_folded ==
n_distinct_folded`, because the two halves hold no spelling in common —
a cell that reads as a number is in the numeric half by the rule that
made the column; and `n_numeric_distinct + labels.n_distinct == n_distinct`, because the
two halves share no spelling and nothing else can add one. Four bounds
that each held separately admitted a set of counts no file can meet: a
half of ninety-seven different numeric cells published as one. These are the
NUMERIC half's counts of different written cells, and they are
published because the twin is laid out from them: they are the budget
of different SPELLINGS the numeric half may write. The block's own
`n_distinct_values` will not serve, because that counts different
NUMBERS and `07` and `7` are one number written two ways; the column's
own `n_distinct` will not serve either, because it counts the labels
too. Measured before it was published: without them, a column of 300
cells holding sixty values written two ways beside twenty markers
published 113 different cells and its twin held 56 at every seed.

**A DECLARED DECIMAL COMMA REACHES THIS ROLE'S NUMERIC HALF** (plan
P4-D34). Both halves are read under the declaration the column was
described with, the twin spells the half's numbers with a comma, and
the validator reads them back that way. A published label is never
rewritten, in the description or in the twin. When either checking side
recounts a declared column -- the generator's own report and the
validator alike -- it reads each cell's class, and every absent
spelling's identity, under the declared grammar on the file's own text,
and translates a cell to a point only after the absent cells are set
aside. So a label such as `1,234,567`, which the ordinary reader takes
for a number, is counted as a label, a marker spelled `E11.9` keeps its
dot, and a grouped `-999.000` is a number rather than the absent
`-999,000` (stage 2 confirmation review, 2026-09-15; the recounts had
mixed the two readings since before stage 2). Before this the profiler split the cells under the comma grammar
and then re-read the halves without it, which left an empty numeric
half and ended the run in an internal error.

**What the two halves are read by.** The same readers that read those
blocks anywhere else — the quantitative reader over the numeric cells,
and a label reader over the rest. The label half is NOT read by the
constant-and-binary reader, which demands one value or two, nor by the
long-tail reader, which demands a level covering the detection line
and a count above the categorical ceiling: this half is neither of
those columns, and the rule that gave the role has already decided
what it is.

**What the role does not claim.** A column whose numbers are a CODE
SET rather than a quantity — `1`, `2`, `3` on thirty rows each — is a
set of categories and is described as one. A column whose words are
PROSE rather than labels stays free text. Neither is decided by this
document; section 5.2's rules decide, and this section describes what
is published once they have.

**AND A LONE UNREPEATED SPELLING IN THE LABEL HALF IS PUBLISHED, at a
floor of one, exactly as it is on every label role at that floor.** The
rule asks the label half to be a vocabulary — more than nine tenths of
its cells wearing a spelling that repeats, and most of its identities
repeating — so a half of prose is refused. A half of markers with ONE
stray in it is admitted, and at a floor of one that stray is a level
with the count 1. Refusing it instead is worse and was measured: the
same column read without this rule is `long_tail_labels` and publishes
**282 levels** — the stray AND all 280 readings, each verbatim. The
protection against publishing a group of one is `--smallest-group`,
which is what it is for.

**AND THE CODE-SET TEST IS A COUNT, so it has a boundary and the
boundary is stated rather than left to be met.** The rule asks whether
the numeric half holds more different values than a set of categories
may — a share of the half's own cells — and near that line a code set
and a measurement are indistinguishable to any count. Measured: twelve
month codes on nine rows each beside twelve `unknown` cells takes this
role, because twelve values in a hundred and eight numeric cells is
above a ten-value ceiling, while the same twelve values in a
hundred-and-twenty-cell column would have been a set of categories. The
rule cannot tell a twelve-point code from a twelve-point measurement
and neither can any other count; `--code` is how a person says which it
is, and residual R-P4-150 carries the boundary.

---

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
is the same class of fact the sizes of a label column's withheld levels
were, published for the same reason until the owner's ruling of
2026-09-17 pooled them into `suppressed_rows` (plan P4-D201). What it does
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
`small_cell_floor - 1` (W5) and never include 1 itself (W5b, owner
ruling of 2026-09-17 item 5, plan P4-D240: a spelling ONE row wrote is
counted into the label's commonest spelling instead), and `{}` is valid
— a published label with no held-back spelling. At a floor of one that range is empty, so every
map of this key is `{}`; and since plan P4-D275 the producer counts
every spelling below a raised floor into the level's commonest, so the
producer writes `{}` at every floor; `variants_withheld` is one of the fields S13
names, and S13 is checked before any column block is read.

Worked example — floor 11, one entry of a `categorical` column:

```
{
  "count": 40,
  "label": "north",
  "variants": {
    "North": 25,
    "north": 15
  },
  "variants_withheld": {}
}
```

The column holds twenty-two rows written `North`, fifteen written
`north`, and three further spellings written by ONE row each. A spelling
one row wrote is counted into the level's commonest (W5b, plan P4-D240),
so the three are counted under `North` and the entry publishes 25 and 15.
25 + 15 = 40, the entry's own `count`. **This example read 22 and
`variants_withheld {"1": 3}` until P4-D240**, which is the count of one
that key states outright. With three spellings of TWO rows each instead,
the entry read `{"North": 22, "north": 12}` beside
`variants_withheld {"2": 3}` until plan P4-D275, which counts EVERY
spelling below the floor into the level's commonest: it now reads
`{"North": 28, "north": 12}` beside `variants_withheld {}`, the six
rows of the three spellings counted under `North`, and 28 + 12 = 40.

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
which no floor suppresses, the same class as the repetition multiset
and as the held-back level sizes this format published until the
owner's ruling of 2026-09-17 pooled them (plan P4-D201). What it discloses, stated rather than
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

**Invariant W5b (a spelling ONE row wrote).** No key of
`variants_withheld`, read as a number, is 1 (owner ruling of
2026-09-17, item 5; plan P4-D240). Such a key says, in this census's own
definition, that a held-back spelling covered exactly one row — a count
of one stated outright rather than derived, and the twin then wrote that
row's spelling in exactly one row. Measured: 490 `F`, 500 `M` and one
`f` at a floor of eleven published, for the level `f`,
`variants {"F": 490}` beside `variants_withheld {"1": 1}`. The producer
counts such a cell into the level's COMMONEST spelling before either
census is taken off it — ruling 6 of the same day, asked of a label's
spellings — so no description it writes reaches this refusal, and at a
floor of one nothing is held back and nothing moves. W5 above still
bounds every key to `1 .. floor - 1`; this closes the bottom of that
range.

**Invariant W6 (variant keys are distinct).** They are object keys, so
this is a property of the JSON, but it is stated because two spellings
that differ only by a character the canonical form does not
distinguish would be one key and must not be produced as two.

**Invariant W7 (at least one spelling exists).** `variants` and
`variants_withheld` are never BOTH empty on one entry, because a
published label covers at least `small_cell_floor` rows and every row
was written some way.

[ASSEMBLY: 6.3.1 points here for W1–W7, W5b among them, and this is their home; the
checkable list of §8.8 restates them, which is that list's stated
purpose. Add `W-P` to that list's producer rows.]

#### 7.4.8 `shape_form_cells` — the level's own form count

**C6-124 (what it counts).** `shape_form_cells` is how many of the
level's present rows wrote the label in the LABEL'S OWN WRITTEN FORM,
where a written form is what 7.9 defines. It is REQUIRED on every entry
of `levels` on the four label roles and FORBIDDEN everywhere else, and
it is written even when it is nought, because this format has no
optional keys and a key that appears only where the answer is
interesting is a key whose absence speaks.

**C6-97 (why it is ONE NUMBER and not a census).** A spelling belongs
to a level when trimming and case folding it gives the label. A
spelling that HAS a form holds only ASCII letters, ASCII figures and
the thirteen marks — no space, so trimming changes nothing — and
folding an ASCII letter leaves an ASCII letter in the same place, so
`shape_form` answers the same string for a spelling and for its fold.
**Every form-bearing spelling of a level therefore wears exactly the
form of its label**, a level's census can name at most that one form,
and the fact is a count rather than a map. A label with no form of its
own has no form-bearing spelling at all and carries nought.

**C6-98 (why the format carries it).** Owner ruling of 2026-08-31,
plan amendment A-P4-47. The column-wide census of 7.9 cannot say WHICH
of a published label's held-back spellings wore that label's form, and
the twin has to decide: the made-up spellings of 7.4 come from the case
flips and then the edge spaces (generation method G8.2), and only the
case flips keep the form. Without this number the generator guessed,
and the guess was wrong in BOTH directions — short by a held-back
group's rows on some columns and past the published count on others.
Two source columns whose entries were identical key for key published
different censuses, so no rule reading the description could be right
about both. That is residual R-P4-34, and this key closes it.

**WHAT IT DOES AND DOES NOT DISCLOSE.** It names no spelling and no
form KEY: the form it counts is the form of the level's own published
`label`, which the reader already holds. What a reader CAN take from it
is which held-back group of that level was written in the label's shape
— presence and shape, attached to a group the floor does not name. The
owner ruled that in on the ground that a code's SHAPE identifies
nobody, and weighed against it that category columns are what analysis
code is written against, so a twin whose invented codes wear the wrong
shape breaks that code silently. The floor still governs which VALUES
are named, and this names none. Section 12 carries the row.

**Invariant W8 (two bounds, and NO SUM).** `shape_form_cells` is at
least the rows covered by the entry's own `variants` whose spelling has
a form, and at most those plus every row `variants_withheld` accounts
for; and where the `label` has no written form it is exactly nought.
Both ends are facts of THIS ENTRY.

**Invariant W9 (the spellings the block speaks of).** Let `S` be the
spellings the published levels name: the keys of every entry's
`variants` and the spellings every entry's `variants_withheld` counts.
Then `S + suppressed_levels <= n_distinct <= S + suppressed_rows`, taken
over the column's own `n_distinct` on the four label roles and over the
half's own `n_distinct` on a compound column's `labels`. It is plan
P4-D276's definition of the count read as a rule: a held-back level
wrote at least one spelling and at most one per row, and a description
holding nothing back — every floor-one description — has the two ends
meet at `n_distinct == S`. Added by the carried numbers pass of
2026-09-18, because P4-D276 made the count move with the floor while no
rule tied it to the levels beside it, and a floor-eleven count grafted
into a floor-one description was accepted either way round.

**AND THERE IS NO SUM RULE AGAINST `shape_forms`, WHICH A READER WILL
LOOK FOR.** The column census is a fact of its own beside these and not
their total, for three reasons, each of which breaks the sum on its own
(residual R-P4-80):

1. **Suppressed levels' cells belong to no published level.** The
   column census counts every present cell that has a form; a level the
   floor held back publishes no entry, so its cells are in the column
   total and in no level's number.
2. **The floor applies to a smaller population.** A form shared by
   fewer than `small_cell_floor` cells of ONE level would pool there
   while the same form clears the floor column-wide.
3. **The room refusal is column-wide.** `form_room` is compared against
   `n_distinct` plus the floor (7.9), which is a fact about the COLUMN;
   a refused form's cells are counted nowhere in the column census and
   are still counted in their level's number.

**WHAT A LOADER DOES NOT CHECK, stated rather than left to be
noticed.** That the rows outstanding after the named spellings can be
made up of WHOLE held-back groups is a subset-sum question whose cost
is bounded by nothing this document states. The generator asks it under
a budget of its own (G8.1a) and names the shortfall where it cannot
settle it exactly.

**Disposition: EXACT-OBSERVABLE**, on the same terms `shape_forms` is:
a person opens the twin, reads the shape off each cell carrying one
published label, and gets the published number back. The quality report
asks it level by level.

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
key, and one used by fewer rows than max(2, `small_cell_floor`) pools
into `(withheld)` instead, so a single oddly-written cell cannot be
singled out. **A style below that line is counted into the commonest
named style** (plan P4-D222, citing the owner rulings of 2026-09-17; the
first in name order on a tie), so the map names styles alone and no
remainder stands beside them; where no style reaches the line the map is
the one key `(withheld)` holding the whole numeric count -- except over
more cells than five styles can hold below the line, where a pool would
say all six were written, and there the map names `plain` (or `decimal`
on a column whose values are not all whole) for the whole count.
Measured before: 1,200 two-place prices with one padded, one exponent
and one three-place cell published `{"decimal": 1198, "exponent_lower":
1, "leading_zero": 1}` at a floor of one and `{"decimal": 1198,
"(withheld)": 2}` at eleven, and plan P4-D221's fold published
`{"(withheld)": 1200}` at eleven, whose twin wrote integers and
fifteen-place decimals; both floors now publish `{"decimal": 1200}`. The
rule is `parsing.census_nameable`, asked through
`parsing.absorbed_census`.

#### 7.5.4 Invariants

**P1 (the population).** The values sum to `n_numeric` — the present
cells that read as a number binary64 can hold — and to `n_core_numeric`
on `affixed_number` (AF7). Out-of-range and contradictory cells are NOT
counted: plan P2-D9's class-preserving construction writes them in
forms the six styles cannot express, so counting them would oblige a
form no generator writes.

**P2 (the floor, both ways).** Every value under a style NAME is at
least max(2, `small_cell_floor`) (amended by plan P4-D221, citing the
owner rulings of 2026-09-17; it read `small_cell_floor`, and at the
then default floor of one a style used by one cell was named). `(withheld)`
appears only when the pooled remainder is at least 1, and **only
alone** (plan P4-D222, citing the owner rulings of 2026-09-17): a map
whose one key is `(withheld)` restates the numeric count, and it stands
only over no more numeric cells than five styles hold below the line, or
fewer than the line -- the loader's P6.

**P3 (never empty here).** Never `{}`: the numeric count is at least 1
on these roles (Q3) and every counted cell lands in a key.

**P4 (independent of `integer_valued`).** `integer_valued: true` does
not forbid `decimal` or an exponent style — `5.0` is whole, written
with a point. A loader checks neither against the other.

#### 7.5.5 Disposition, and the recount identity

EXACT-OBSERVABLE. **The twin writes each named style in its published
count**, and **may write only the six of 7.5.1, never a seventh** —
a thousands separator only where `group_separator` publishes one (plan
P4-D38; a cell holding a comma is quoted and reads back unchanged),
and never accounting parentheses, excluded by decision 8 and kept for
the contradictory-notation stand-in. Both are classified by digit form,
and brackets are written on no column: a cell standing for `(05)` is written as a signed
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

**C6-137 (a whole numeral the format cannot hold exactly).** Every
spelling above is computed from the value a cell reads back as, and at
or above 2**53 — the first whole number binary64 cannot hold exactly —
that value is not the numeral that was written: a cell holding
`9007199254740993` reads back as 9007199254740992.0. A cell whose text
is FIGURES ALONE after an optional minus, which reads back as exactly
the value compared against, and whose value is at or above that
boundary, is in a permitted spelling of that value. Without this clause
a real register of long whole numbers meets no spelling of its own
description, however it is written, which no description of a real file
may ask of it.

The three conditions are each a way this still fails, and they are
stated so that no wider reading is available: a point, an exponent or a
mark between thousands puts a cell outside the clause, so a fraction
width the census does not name is reported exactly as it was; and a
numeral naming a different value is outside it at any width. A twin
writes the canonical figures for such a column, which is a limit of
what the description carries rather than a licence taken here.

**Numbered C6-86 on its landing's branch and C6-137 here** (the
integration of landings 2b.6 to 2b.10, 2026-09-16): landing 2b.7 had
already given C6-86 to the placement of its two mixture censuses. The
same integration found this clause's rule written TWICE in the
validator, once by landing 2b.10 and once, wider, by landing 2b.7's
source-spelling family (validation method V1.4, plan P4-D66.2), which
also admits such a run carrying its sign, its thousands marks or a
padded exponent. Every cell this clause admits is admitted there,
measured over 264,387 such texts, so the validator keeps the one rule,
and the three conditions above bound THIS clause rather than the whole
family.

`NW` is read off the VALUES, never the spellings: counting cells
WRITTEN with a point would make the identity circular, a twin spelling
a whole `1000` as `1000.0` inflating its own `D`. Where nothing pooled,
`D` is zero and every style matches its count exactly; **an alternate
spelling is used ONLY where the counts require it**, so an
all-canonical whole-number column publishes `{"plain": n}` and stays
byte-plain. The report names the remainder, the cells it covered and
how many lacked a point-free spelling.

### 7.5a `negative_notations` and `thousands_marks`

**C6-86 (where they live).** A `count`, `continuous` or `affixed_number`
block carries both as keys of the BLOCK, siblings of `numeric_styles`
rather than keys inside it, for the reason `fraction_widths` is one: the
forms map is a partition whose counts close on the numeric count, and a
grouped cell is also a decimal one. A position of a `joined_numbers`
column carries `{}` for each (NS2, TM1).

**C6-87 (what they count).** `negative_notations` counts the cells
`negative_form` is counted over — every cell reading as a negative
number this format holds — under the notation it wrote.
`thousands_marks` counts the cells that PROVE a mark under
`group_separator`'s evidence rule of 7.5: four or more whole figures, a
groupable form, and a whole part reading as groups of three around one
mark, read with points and commas exchanged on a declared decimal-comma
column. A BARE groupable cell proves no mark and is counted in neither
census: it is not a small group, it is a cell with no convention to
reproduce — but it is COUNTED by C6-88's complement clause, because a
reader can take it back out of a total (plan P4-D140). Both keys ask ONE
evidence rule of each cell (plan P4-D141): where the two asked it
separately a declared decimal comma proved a point for the majority key
and nothing for the census, and 780 `1097.001,01` beside 20
`197 001,01` published a description the loader refused.

**C6-88 (the census floor).** Both are floored PER CONVENTION at max(2,
`small_cell_floor`), never at one. A published count of one names an
individual outright — the reader who knows how every other cell was
written can tell how that cell was — and `small_cell_floor` may be
lowered to one. What falls below is pooled under `(withheld)`, which names no
convention here because these censuses have four and eight possible
keys; a pool that is itself below the floor would name its own cells, so
such a census publishes `{"(unavailable)": 0}` and no number at all. At
`small_cell_floor` of one nothing may be pooled (C5-S13) and the
unavailable state stands instead. The complement clause of the owner's
twin definition is ASKED and not assumed (plan P4-D140, which withdraws
the sentence that said it was met by construction): among the printed
counts it holds by construction, but a reader can also subtract the
printed total from a total published elsewhere, so a census prints
nothing unless what it leaves of each such total — the negatives, for
`negative_notations`; the groupable cells and every number of the
column, for `thousands_marks` — is nought or at least the census floor.
`thousands_marks` then publishes `{}` rather than the unavailable state,
because its own empty state is the state nought reaches. The rule is
stated once, `parsing.census_nameable`, and the producer, the loader and
the checker all read it.

**C6-89 (disposition).** Both EXACT-OBSERVABLE (plan P4-D65.2). **The
twin writes each named convention on that many cells**, spending the
census cell by cell as generation method G6.1 states; a pooled remainder
is written with a mark the census does not name, and the groupable cells
left over are written BARE wherever at least the census floor of them
are left, since the census is published beside no smaller bare remainder
(plan P4-D142). The quality report compares each named convention —
one named convention as much as two — with what describing the twin on
its own publishes for it, and WITHHOLDS the comparison where the twin
holds fewer cells that could wear a convention than the census counts,
or leaves over a number of them strictly between nought and the census
floor, or its own description names no convention: how many of a twin's
cells reach four whole figures, or fall below zero, follows from its
ladder and is not itself pinned cell for cell, and the generator's
report names that shortfall as a deviation of the census. A twin whose
own description names no convention although the published counts could
have been named from its own totals is MISSED, because those counts are
then not the ones it holds.

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
width. A width fewer than max(2, `small_cell_floor`) cells share is
counted into the commonest named width (plan P4-D222, citing the owner
rulings of 2026-09-17; plan P4-D221 had folded a remainder below that
line into the smallest named width, and 1,200 prices with one cell at
three places published `{"2": 1197, "3": 1}` at a floor of one before
either), and the census counts the `decimal` count the forms map
publishes, the cells that map counted into `decimal` at the commonest
width; where no width reaches the line, or where the widest width named
is narrower than the published `min` or `max` needs, the census is the
one key `(withheld)`; read over the cores on `affixed_number` (AF7).

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
- **P5.c — no `decimal` key but a `(withheld)` key.** `fraction_widths`
  is `{}` (invariant P8, amended by plan P4-D221, citing the owner
  rulings of 2026-09-17). Since plan P4-D222 the `(withheld)` key stands
  only alone, so no form is named and a total printed here would say how
  many of the pooled cells carried a point. Until P4-D221 the census
  could carry the pooled decimal cells under its own `(withheld)`,
  bounded by four conditions (A-P4-6, A-P4-8): 1,200 prices with one
  cell at three places and one padded at a floor of eleven published
  `{"(withheld)": 1}` there. Those conditions are withdrawn with the
  shape they bounded, and what the pool can hold is P6's.

**P6.** Every NAMED width's count, and a `(withheld)` count, is at or
above max(2, `small_cell_floor`) (plan P4-D221), and a `(withheld)` key
stands alone (plan P4-D222, citing the owner rulings of 2026-09-17).
**P8 (a held-back form's widths).** Where `numeric_styles` carries a
`(withheld)` key and names no `decimal`, `fraction_widths` is `{}`; and
where it carries one and names no `leading_zero`, `pad_widths` is `{}`;
and where it carries one, `field_widths` is `{}` (plan P4-D222)
(plan P4-D221, citing the owner rulings of 2026-09-17; P8 read, until
then, that the pool fit inside the forms left once both width censuses
had spoken for their pooled cells, which they no longer do).
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

<!-- a7e: the census of padded field widths -->

### 7.8 `pad_widths`

**C6-27b (where it lives).** A `count`, `continuous` or
`affixed_number` block carries `pad_widths` as a key of the BLOCK, a
sibling of `numeric_styles` and NOT a key inside it, and forbidden on
every other role. Inside is impossible for the reason C6-27 gives: P1
makes every value of `numeric_styles` an integer summing to the numeric
count, and an object is neither.

**C6-28b (what it holds).** A mapping from a FIELD WIDTH — the figures
a cell writes before any point, the sign not counted — to the number of
PADDED cells at that width — every `leading_zero`-styled cell, and
every `leading_plus` cell whose figures after the plus begin with a zero
and are more than that zero (plan P4-D145) — with the pooled key
`(withheld)` standing alone where no width reaches max(2,
`small_cell_floor`), a width below that line counted into the commonest
padded width and the cells the forms map counted into `leading_zero`
counted at that width (plan P4-D222, citing the owner rulings of
2026-09-17; plan P4-D221 folded a remainder into the smallest named
width); read
over the cores on `affixed_number`, exactly as AF7 reads the fraction
census there. A PLUS DOES NOT HIDE THE PAD: the ladder files
`+00100000000000000000` under `leading_plus`, and measured before this
clause 800 such keys at a floor of eleven published `pad_widths {}`
beside `field_widths {"20": 800}`, and the twin wrote every one of them
two figures narrower with no check missed.

**Why the styles map cannot say it, which is the whole reason this key
exists.** `numeric_styles` counts how many cells began with a redundant
zero. It cannot say whether they were written five figures wide or
nine — a five-figure procedure code and a nine-figure record number are
both `leading_zero` to that map — so a twin honouring the map exactly
could write a field of another width and break a width check, a
fixed-width slice or a join, with no published fact to name what it
had done. A census of the width is what closes that (**A-P4-34**).

**WHEN THE PLUS-SIGNED PADS ARE NOT COUNTED** (plan P4-D145 as amended,
and plan P4-D148, the repair pass of the final Codex review). The
census counts `leading_zero` cells alone, and no plus-signed padded
cell, in two cases, and in each it is the census a column with no
plus-signed padded cell writes: **(1)** where `numeric_styles` names no
`leading_zero` key but carries a `(withheld)` key — the held-back cells
may be padded ones, which a twin writes as their own values are
written, and measured before this clause eight values written `+0100`
twice and `0100` once at a floor of eleven published `{"4": 24}` and
their twin missed `pads.published.4` at exit 3 — and since plan P4-D221
the census is then `{}` whatever the plus-signed cells (invariant P8):
the padded cells of the pool are fewer than the line, or they are the
named count a pool below the line took in; **(2)** where counting
them would leave a reader, at any `small_cell_floor` (plan P4-D221; it
read "above one"), a difference that is neither nought nor at least
max(2, that floor) — the census's total less the named `leading_zero`
count, or the named `leading_plus` count less that, or where
`leading_plus` is held back, the forms map's pool less it (invariant
P5b). Measured before: 800 padded codes, fifty `+k` and one
`+00123` at a floor of eleven published `{"5": 801}` beside
`leading_zero: 800`, and the one plus-signed padded cell was read off by
subtraction.

**C6-29b (key grammar, and the narrowest field there is).** A width
key is the decimal spelling of an integer of AT LEAST TWO, by the
grammar C6-29 fixes and for the same reason: no sign, no leading zero,
no space, no other character. It would be a poor joke for the census of
padding to write a padded key. `(withheld)` is the only non-numeric key
permitted.

TWO IS THE FLOOR BECAUSE ONE IS NOT REACHABLE. A padded cell writes at
least one zero, in front of at least one figure, so its narrowest field
is two characters wide. A census naming width `0` or `1` describes
cells no producer can have read and no twin can write, and a loader
admitting it hands the generator a width it must then refuse -- a
document accepted at one end of the tool and impossible at the other.
Invariant P7b refuses it.

**C6-30b (invariants, by cases).** The census counts LEADING-ZERO
styled cells, so its invariants are the cases of C6-30 with
`leading_zero` in the place of `decimal`, and each binds the same
thing. **P5b (the sum).** Let *F* be the sum of ALL values,
`(withheld)` included; an empty census has *F* = 0.

- **P5b.a — a `leading_zero` key is published.** *F* is at least that
  key's value and at most that value plus the `leading_plus` value and
  the `(withheld)` value, the plus-signed padded cells being a number no
  key holds (plan P4-D145). **And the disclosure rule binds it** (plan
  P4-D148): *F* less the `leading_zero` value is nought or at least
  max(2, `small_cell_floor`), and where `leading_plus` is named, that
  value less (*F* less the `leading_zero` value) is too, and where it is
  held back, the `(withheld)` value less that difference is too — at
  every `small_cell_floor` (plan P4-D221, citing the owner rulings of
  2026-09-17; it read "above one", where the census named counts of one
  under keys of their own).
- **P5b.b — no `leading_zero` key and no `(withheld)` key.** No
  `leading_zero` cell exists, so every cell the census counts is a
  plus-signed padded one: *F* is at most the `leading_plus` value, and
  zero where that key is not published (plan P4-D145). The disclosure
  rule binds *F* as P5b.a binds the difference, at every floor (plan
  P4-D221): nought or at least max(2, `small_cell_floor`), and so is the
  `leading_plus` value less *F* (plan P4-D148).
- **P5b.c — no `leading_zero` key but a `(withheld)` key.** The census
  is `{}` (P8, as P5.c; plan P4-D221, citing the owner rulings of
  2026-09-17, which withdrew the four conditions of P5.c that bound a
  pooled padded census here). **No plus-signed padded cell is counted in this case**
  (C6-28b, plan P4-D145 as amended by the repair pass): the window P4-D145
  first opened here -- *F* up to `small_cell_floor` − 1 plus the
  `leading_plus` value, and up to *W* plus that value -- is withdrawn,
  because the held-back cells a twin writes unpadded made the census a
  width no twin reached.

**P6b.** Every NAMED width's count, and a `(withheld)` count, is at or
above max(2, `small_cell_floor`) (plan P4-D221), and a `(withheld)` key
stands alone (plan P4-D222, citing the owner rulings of 2026-09-17).
**P7b.** Every NAMED width is at least 2, by C6-29b, and a width key is
present only if its count is nonzero.

**A NAMED WIDTH IS HONOURED BY PADDING AND NEVER BY MOVING THE VALUE.**
This is the one place the two censuses part company, and it is what
makes this one the simpler of the pair. A fraction width is reached by
adjusting the value — writing 9.53 at one place makes it 9.5 — so
C6-30's census must be kept from spending a published rung, an
endpoint or the zero stratum to buy a width. Padding spends nothing:
`000123` and `123` read back as the same number, so no statistic, no
rung and no endpoint is ever at stake here. A width narrower than the
value's own figures is therefore not reachable at all and is never
taken.

**WHAT A NAMED WIDTH DOES COST is the leading-zero family**, and the
cost is stated here rather than discovered. Every order of that family
writes one more figure, so a value has exactly ONE leading-zero
spelling at a named width and a twin reaching for a second would leave
the width. Where a width is named, raw `n_distinct` therefore falls to
its own two-sided envelope under the authorization owner decision 11
already carries — "only where even those cannot supply" — and the
report prints the shortfall. It is not a new lowering: it is the case
that authorization was written for, reached by a new route.

**Disposition: EXACT-OBSERVABLE**, against a C6-85-shaped recount:
padded cells recounted at a named width number at least the published
count and at most it plus the pooled `(withheld)` value. **P5b to P7b
do not reach producer obligation PW-P**: they bound the census against
published numbers, and none checks that a width count IS the count of
source cells at that width — a loader holds no table and cannot
recompute it.

---

<!-- a7f: the census of whole-number field widths -->

### 7.10 `field_widths`

**C6-27c (where it lives).** A `count`, `continuous` or
`affixed_number` block carries `field_widths` as a key of the BLOCK, a
sibling of `numeric_styles` and NOT a key inside it, and forbidden on
every other role. Inside is impossible for the reason C6-27 gives.

**C6-28c (what it holds).** A mapping from a FIELD WIDTH — the figures
a cell writes, the sign not counted — to the number of cells written as
a WHOLE NUMBER at that width, with the pooled key `(withheld)` for
widths fewer than max(2, `small_cell_floor`) cells share standing
alone; read over the cores on `affixed_number`, exactly as AF7 reads the
other two censuses there. **Since plan P4-D222 (citing the owner rulings
of 2026-09-17) it counts the cells of the point-free forms the forms map
names, and the cells that map counted into one of them at that form's
commonest width**; the unpadded cells at a width, where fewer than the
line, are counted into the commonest unpadded width at the line; and the
census is one pool where no unpadded width reaches the line beside
unpadded cells, or where no width reaches it. Plan P4-D221 left out the
held-back cells whose count or complement named rows (the pool route),
which no longer arises, since no pool stands beside a named form.

**WHICH CELLS ARE "WRITTEN AS A WHOLE NUMBER" IS THE STYLES MAP'S OWN
QUESTION, ASKED ONCE.** Three of the six forms 7.5.4 fixes carry
neither a point nor an exponent — `plain`, `leading_plus` and
`leading_zero` — and those three are exactly the cells that have a
figure field and nothing else. A `decimal` or exponent-styled cell is
counted NOWHERE by this census, `(withheld)` included: that key means a
group too small to name, and a cell this census does not describe is
not a small group. The rule is the one 7.9 states for a cell with no
form at all.

**WHY THE OTHER TWO CENSUSES CANNOT SAY IT, which is the whole reason
this key exists.** `pad_widths` counts only the cells wearing a
redundant zero and `fraction_widths` only the figures after a point, so
a cell written `199` — no padding, no point — has its width published
by neither. A vaccine-code column running `000` to `199` is the shape
that shows it: the padded half is censused, the hundred and three cells
of the unpadded half are not, and a twin honouring every published fact
of that column wrote some of them two figures wide with no report
naming it (residual **R-P4-35**). A column of plain codes is the same
shape with no padded half at all (residual **R-P4-30**).

**IT OVERLAPS `pad_widths` DELIBERATELY rather than partitioning the
column with it.** A padded cell is a whole-written cell, so it is
counted in both, and the pair then says two different things: the
padded census says how wide the PADDING was written, this one how wide
the field is however it was written, and the difference between them is
how many cells at that width wore no padding at all. That difference is
what tells a generator the MAGNITUDE its values must have, and it is
what closes R-P4-30 and R-P4-27 (plan P4-D30).

**C6-29c (key grammar, and the narrowest field there is).** A width key
is the decimal spelling of an integer of AT LEAST ONE, by the grammar
C6-29 fixes and for the same reason. ONE IS THE FLOOR BECAUSE NOUGHT IS
NOT REACHABLE: a cell written as a whole number writes at least one
figure, so a census naming width `0` describes cells no producer can
have read and no twin can write. Invariant P7c refuses it.
`(withheld)` is the only non-numeric key permitted.

**C6-30c (invariants).** Three bind, and their identifiers are P6c,
P7c and P9c. Let *F* be the sum of ALL values,
`(withheld)` included; an empty census has *F* = 0, which is what a
column no cell of which was written as a whole number publishes.

- **P9c (the sum, bounded on both sides).** Let *N* be the sum of the
  `numeric_styles` values for whichever of `plain`, `leading_plus` and
  `leading_zero` that map NAMES, and *W* its `(withheld)` value or 0.
  Then **N ≤ F ≤ N + W**. Both halves are provable from C6-28c rather
  than assumed: every cell counted by a named point-free style is a
  cell this census counts, and every further cell it counts was held
  back from the styles map. Where all three point-free forms are named,
  *W* has nothing of theirs in it and the two bounds meet. Since plan
  P4-D222 (citing the owner rulings of 2026-09-17) *W* is nought
  wherever a form is named, so the bounds meet on every document a
  producer writes, and where *W* is not nought the census is `{}` (P8).
  Plan P4-D221's clause here -- *F* − *N* and *W* − (*F* − *N*) each
  nought or a group -- had a pool beside a named form to bound, and is
  withdrawn with it.
- **There is no separate ceiling against `n_numeric`, and its absence
  is a rule.** P1 makes the styles map sum to the numeric count
  exactly, so *N* + *W* IS `n_numeric` — read over `n_core_numeric` on
  `affixed_number` (AF7) — and P9c's upper bound is that ceiling
  already. A loader that compared *F* against `n_numeric` as well
  would be running a check that cannot fail, which this format counts
  as a defect and not as caution.
- **P6c.** Every NAMED width's count, and a `(withheld)` count, is at or
  above max(2, `small_cell_floor`) (plan P4-D221, citing the owner
  rulings of 2026-09-17), and a `(withheld)` key stands alone (plan
  P4-D222).
  **And at a width `pad_widths` names too, the difference is nought or
  a group** (plan P4-D148, the repair pass of the final Codex review):
  this census's count less `pad_widths`' count at that width — the cells
  written there with no redundant zero — is nought or at least
  max(2, `small_cell_floor`), at every floor (plan P4-D221; it read
  "wherever that floor is above one", where both censuses named counts
  of one outright and S13 forbade the pool this rule's remedy needs). Where `pad_widths` carries a `(withheld)` key,
  this census carries none, and exactly one width of two figures or
  more this census names is not named by `pad_widths`, the pooled
  padded cells are at that width, and are taken off there too. Where
  the difference would break this, the producer moves that width's
  count into this census's `(withheld)` remainder, a mixture of widths
  no reader takes apart; the padded cells keep their width in
  `pad_widths`. Measured before: 800 padded five-figure codes and fifty
  short ones beside one unpadded `12345` at a floor of eleven published
  `{"5": 801}` here beside `{"5": 800}` there, and the one cell was read
  off by subtraction; now `{"2": 41, "(withheld)": 810}`.
- **P7c.** Every NAMED width is at least 1, by C6-29c, and a width key
  is present only if its count is nonzero.

**THIS CENSUS IS COMPARED AGAINST `pad_widths` BY A LOADER ONLY WHERE A
READER CAN SUBTRACT THEM** (amended by plan P4-D148; it read "by any
loader" until a reader was shown to take one person off the difference).
A padded cell at field width *w* is a whole-written cell at field width
*w*, but otherwise the arithmetic is not checkable at the loader,
because either census may have pooled a group the other named, and a
loader that inferred one from the other would refuse documents this
profiler writes. The one comparison P6c makes is the disclosure rule's,
at a width both censuses name. What holds the pair together is producer obligation
XW-P, and no rule of this section reaches it.

**A NAMED WIDTH HERE IS A FACT ABOUT THE VALUE, WHICH IS WHERE THIS
CENSUS PARTS COMPANY WITH `pad_widths`.** Padding spends nothing:
`000123` and `123` read back as the same number, so no rung, endpoint
or statistic is ever at stake there. An UNPADDED cell has no such
freedom — it is exactly as wide as its value — so a width this census
names is a constraint on MAGNITUDE, and the only stage that can meet it
is the one that chooses the values. `docs/spec/generation-method-v1.md`
G6.6 states how, and states its bound: a stratum may take any whole
number its own share and G5.4's integer rule could together have
reached — every one within HALF A UNIT of its share, which is the half
unit that rule already spends and G12.2 already widens the rung window
by. A width no stratum can reach that way is reported rather than
bought with a value the rung windows would then miss, and no stratum's
value is ever moved further than amendment A-P4-18 permits, whose bound
is on the REACH of a move and not on which of two roundings a stratum
settles on.

**Disposition: REPORT-ONLY, and this is the one of the three width
censuses that is not exact.** The other two are facts about SPELLING: a
padded width is bought with a zero and a fraction width by adjusting a
value inside its own stretch, so the writing stage can meet either
exactly. An unpadded cell is exactly as wide as its VALUE, so a width
here is a fact about MAGNITUDE, and magnitudes are placed by the
ladder — which says nothing about how many cells lie below a decade
boundary falling INSIDE a gap between two rungs.

**Measured before the class was chosen**, because a fact the twin
cannot meet, published as one it must, is a defect this format has paid
for before: eighty generation runs over forty described columns at the
then default floor of one, thirty-six of them missing at least one named width, the
widest gap seventy-one cells. A check here would call the shipped
generator's own twin broken on nearly half the columns it is handed.

**What REPORT-ONLY buys, and it is not nothing.** The census is
CONSUMED: `docs/spec/generation-method-v1.md` G6.6 turns it into a
constraint on each stratum's value, and on a dental-code column of
`D0120`, `D1110` and `D2740` it took the seeds writing a cell at a
width the source never used from fourteen in forty to none. Where a
width is not reached the twin's own report NAMES it, with the published
count beside the achieved one, and `synthtwin validate` LISTS the
census with a sentence saying the twin follows it without being held to
it. What a file does not do is FAIL on it. Upgrading the class is
residual R-P4-114, whose obstacle is the CELL ALLOTMENT rather than
this census.

**P6c, P7c and P9c do not reach producer obligation XW-P**: they bound
the census against published numbers, and none checks that a width
count IS the count of source cells at that width — a loader holds no
table and cannot recompute it.

---

<!-- a7g: the bins that hold nothing -->

### 7.11 `empty_bins`

**C6-31f (THE DIVISION, stated here because three surfaces read it).**
A block's reach is the closed interval between its published `min`
and `max`. It is divided into `HISTOGRAM_BINS` = 32 equal bins. The
bin of a value `v` is `floor((v - min) / (max - min) * 32)`, clamped
into `0 .. 31`, so **every bin is half-open at the TOP and a value
standing exactly on a shared edge belongs to the UPPER bin — the one
that starts there** — except the last bin, which is closed so the
published maximum has somewhere to go.

**THE TWO CASES WITH NO DIVISION, and they are not the same case.**

- **`max` equals `min`** — every value is one number. The clamp above
  puts all of them in bin 0, so the census has ONE occupied bin and
  reads `{"0": n}` under the ordinary floor rule of C6-31 — which
  governs this census like any other, so where `n` is below the
  smallest group size the whole census is withheld and reads `{}`,
  exactly as it would on any column with a bin under the floor. But
  there is no width to divide, so the other thirty-one bins are not
  empty — they do not exist — and `empty_bins` and `empty_edges` are
  both EMPTY at every floor. A description saying thirty-one bins of a
  one-value column hold nothing would be describing a division nothing
  made.
- **An end this format cannot hold, or two finite ends whose
  DIFFERENCE it cannot hold** — there is no scale at all. The census
  is ABSENT, and `empty_bins` and `empty_edges` are both empty.
  "There is no scale" and "the scale has no empty bin" are different
  sentences, and the absent census is what tells them apart.

**IT IS STATED BECAUSE IT WAS NOT.** 7.11 and the producer obligation
below both said "the bins of C6-31's division", and C6-31 is the
closed vocabulary list and states no division at all — so the one rule
the producer, the loader and the generator must share was written down
in none of them, and the code comment that carried it said a shared
edge belongs to the LOWER bin while the arithmetic put it in the
upper. A producer written to that sentence and the shipped loader
would place a boundary value in different bins.

**C6-122 (where it lives, and what it holds).** A `count`, `continuous`
or `affixed_number` block carries `empty_bins` as a key of the BLOCK,
a sibling of `value_histogram`, and forbidden on every other role. It
is an ARRAY of bin numbers, ascending, each named once, naming every
one of the `HISTOGRAM_BINS` equal bins between the block's published
`min` and `max` that holds NONE of the values the statistics used —
read over the CORES on `affixed_number`, exactly as `value_histogram`
is read there. The bins are the same bins, divided by the same rule
C6-31f fixes; nothing here introduces a second division.

**THE FLOOR DOES NOT REACH IT, AND THAT IS THE WHOLE OF WHY THIS KEY
EXISTS BESIDE `value_histogram` RATHER THAN INSIDE IT.** The
publication floor exists to stop a group too small to name being
named. A bin holding one value is such a group; a bin holding fewer
than `small_cell_floor` values is such a group; a bin holding NOTHING
is not a group at all, and there is no group smaller than nobody. The
owner ruled on exactly that question on 2026-08-31 — asked whether a
bin holding zero may be published while the bins holding one to
one-below-the-floor stay hidden — and ruled that it may.

**THE ALL-OR-NOTHING RULE ON THE CENSUS IS UNTOUCHED, and its
reasoning comes through this key without a word of it being weakened.**
C6-31 refuses a partial census because a census is read by RANK: a
pooled remainder does not say which bins its values are in, so the
ranks the named bins cover are unknown and a generator cannot build
the map it needs. **This list is not read by rank.** It says where NO
value is, which is the same sentence whatever the floor is and
whatever the other bins hold, and a generator reads it as a set of
stretches to keep OUT of rather than as a place to put a value. A bin
holding one to one-below-the-floor values is named by neither key and
stays exactly as hidden as it was.

**WHAT IT SURVIVES, and it is the reason the key is worth its cost.**
`value_histogram` is all or nothing, so at any floor above one it
vanishes on nearly every column — and it vanishes FIRST on the columns
whose shape matters most, because a column with two clusters and an
empty middle has thin bins at the edges of each cluster. Measured on a
300-row column of a hundred and fifty values around twenty and a
hundred and fifty around eighty: at a floor of one the census names
thirteen bins, and at a floor of two, three, five or eleven it names
none. `empty_bins` names the same nineteen empty bins at every one of
those floors.

**C6-123 (invariants).** One binds, and its identifier is Q20. Three
conditions, each refusing a description of a column no table holds:

- **Each bin is named once and in ascending order.** Order is not
  decoration on this key: it is the one fact of the block read as a
  set of stretches rather than as a mapping, and a list a producer may
  write two ways is a list two producers write two ways.
- **Neither the first bin nor the last is ever named.** The scale runs
  from the block's smallest value to its largest, so the smallest is
  in the first bin and the largest in the last. A description naming
  either is describing a column with no smallest value.
- **Where `value_histogram` is present, the two are complements.** The
  census is all or nothing, so where it is present it names every bin
  that holds something; the bins holding nothing are then exactly the
  rest, and every one of the thirty-two is named by exactly one of the
  two. This is the guard against ONE FACT WRITTEN TWICE: a description
  whose two shape facts disagree is refused rather than read.

**AND WHERE THE BLOCK HAS NO SCALE THE LIST IS EMPTY.** A ladder whose
ends this format cannot hold, or whose ends are finite and whose WIDTH
is not, divides into no bins at all, and a block whose statistics used
no value has nothing to divide. "No bin holds anything" and "there is
nothing to divide" are different sentences, and the second is written
as the empty list. The producer's note that breaks the silence of an
absent `value_histogram` is unchanged and still says which of the two
a reader is looking at.

**Disposition: REPORT-ONLY, and the class was MEASURED rather than
chosen.** The fact is CONSUMED —
`docs/spec/generation-method-v1.md` G6.7 makes the value stage read it
and move any stratum that landed in a named stretch — and on the
three two-cluster columns it was built against, at forty seeds each
and at both a floor of one and a floor of eleven, the cells landing in
a named stretch went from 4–6, 2–3 and 3–6 of 300 to NONE at every
seed. It is not EXACT-OBSERVABLE because the twin cannot always
hold it: over forty described columns at forty seeds each, 119 of the
1600 runs still wrote one cell into a named stretch. Re-measured on
the same committed battery after this landing: 130 of 1600 in a named
BIN against 135 before, and 213 of 1600 inside a stretch the SOURCE
really leaves empty against 1058, with the worst run of either falling
from twelve cells to four. Every one of
those is a column whose OTHER published facts leave the twin no room
beside the stretch — a whole-number column whose bins are barely wider
than a unit, or a stratum whose sign band ends at the edge it would
have to cross — and holding a file to this fact would call the shipped
generator's own twin broken on one run in fourteen. Where the move
cannot be made, the twin's own report NAMES the stretch and the value,
and `synthtwin validate` LISTS the fact with a sentence saying the
twin keeps out of the stretches without being held to them. Upgrading
the class is residual **R-P4-140**.

**AND WHERE IT MEETS AN EXACT FACT IT GIVES WAY, which is what
REPORT-ONLY means and is stated here rather than left to the method.**
`docs/spec/generation-method-v1.md` G6.7.4 refuses a move that would
cost `n_distinct` or `pad_widths` — a stratum that does not hold its
value alone, and a move that would change a point-free value's figure
count — because those two are EXACT-OBSERVABLE and this one is not.
Both refusals were found by the suite rather than by review, on the
floored witness of P3-V7-F4, and neither costs anything measurable on
the corpus 7.11 was decided against.

**Q20 DOES NOT REACH THE PRODUCER**, and that is stated rather than
left to be found: it bounds the list against other published facts,
and nothing in it checks that a named bin IS a bin no source cell fell
in. A loader holds no table. What holds that is producer obligation
EB-P: `empty_bins` names exactly the bins of C6-31f's division that no
value the statistics used falls in, counted with the same bin rule the
census is counted with and from the same values.

---

<!-- a7e: empty_edges -->

### 7.11a `empty_edges`

**C6-123a (where it lives, and what it holds).** Every block that
carries `empty_bins` carries `empty_edges` beside it, and it is
forbidden wherever `empty_bins` is. It is an ARRAY of PAIRS. Each pair
is `[below, above]`, two numbers, `below` strictly less than `above`.
There is exactly one pair for each maximal RUN of consecutive bin
numbers in `empty_bins`, in the same ascending order the runs are in.
`below` is the LARGEST value the statistics used that falls in a bin
before the run; `above` is the SMALLEST that falls in a bin after it.
Both always exist: the smallest value of the block is in the first bin
and the largest in the last, so no run reaches an end. On
`affixed_number` the values are the CORES, exactly as `empty_bins` and
`value_histogram` are read there.

**WHY IT EXISTS BESIDE `empty_bins` RATHER THAN INSTEAD OF IT.** The
bins are a thirty-second of the block's reach, so the bins a column
leaves empty lie strictly INSIDE the stretch it really leaves empty. A
column of a hundred and fifty values around twenty and a hundred and
fifty around eighty holds nothing between 26.6 and 72.7, and its empty
bins cover about 26.7 to 71.3. A generator repairing a cell to the
edge of the nearest occupied BIN therefore put it back inside the
source's own gap. `empty_bins` still answers "which bins hold
nothing", which is what the complement rule against `value_histogram`
is written in and what a reader of the shape asks; `empty_edges`
answers "where does the gap really begin and end", which is what a
generator needs.

**WHAT IT COSTS A READER TO KNOW, priced on its own and not by
comparison.** Each edge IS the value of a real cell. It says that some
row holds 26.6 and some row holds 72.7, and nothing about which rows,
how many, or what those rows hold anywhere else — which is the ground
the owner's rulings of 2026-08-31 and 2026-09-03 stand on, and their
ruling of 2026-09-04 ("follow you recommendation") settles this key.

**THE CEILING, COMPUTED AND THEN REACHED ON PURPOSE.** A reach is
divided into thirty-two bins; the FIRST and the LAST always hold the
two endpoints, so at most fifteen of the thirty between them can be
empty runs — runs are separated by at least one occupied bin. A block
therefore carries **at most fifteen pairs and thirty exact values**,
and they can all be different: a 32-row column occupying bins 0, 2,
4 … 28 with TWO values each and bins 30 and 31 with one each publishes
fifteen pairs naming thirty distinct values, and with the two
endpoints row 3 publishes beside them the description names EVERY
value that column holds. On a dense column there is usually no run at all and so no
value here, which is the ordinary case.

**AND IT IS NOT TWO MORE BESIDE ELEVEN, which is what this passage
said before 2026-09-04 and was wrong about.** A ladder's two ENDPOINTS
are exact values of real cells; its nine interior rungs are
interpolated between the order statistics either side, and measured on
six columns of 17 to 250 drawn values, between three and nine of the
nine were held by no cell. So the ladder puts TWO exact values into a
block and this key may add THIRTY. `mode` names one more, being the
value the column holds most often, so a whole numeric block may expose
**thirty-three distinct values** — a number about the BLOCK and not
about this key, and the one a disclosure review should weigh.

**THE OWNER WAS SHOWN THAT NUMBER AND KEPT THE KEY** (2026-09-04,
reaffirming 2026-08-31 and 2026-09-03). Their ground is that a value
standing ALONE — no row attached, no date beside it, nothing else from
that row — is a fact about a distribution and not about a person, and
that this holds in the sparse case too: naming every value a small
column holds names the column's SET of values and still names no row,
no order, no pairing with another column and no time. `SECURITY.md`
carries the ruling and what it does not cover.

**THE FLOOR DOES NOT REACH IT**, for the reason 7.11 gives for
`empty_bins` and for one more: a pair names two values, not a group,
and the same two values are already published as candidates for a
ladder rung. There is no group here for a floor to protect.

**AND WHERE THERE IS NO STRETCH THE LIST IS EMPTY.** `empty_bins`
empty means `empty_edges` empty, which C6-123b's first condition states
as an identity rather than as a special case.

**C6-123b (invariants).** One binds, and its identifier is Q21. Five
conditions, each refusing a description of a column no table holds:

- **As many pairs as `empty_bins` has runs.** Runs are counted on the
  ascending, once-named list Q20 already guarantees, so the two facts
  cannot disagree about how many stretches there are. This is the
  guard against ONE FACT WRITTEN TWICE.
- **Each pair ascends**, `below` strictly under `above`. A pair that
  does not is not a stretch.
- **The pairs ascend and never cross**, so a description is read as an
  ordered set of stretches. **Two stretches MAY share the one value
  that stands between them**: a single value alone in its bin with an
  empty run either side is the upper edge of one and the lower edge of
  the next, and it is one real cell. Refusing that equality refused a
  240-row column its own producer had just described.
- **Every edge is inside the published ends**, between `percentiles.min`
  and `percentiles.max` inclusive. An edge is a value of a real cell,
  so an edge outside the block's own reach describes no column.
- **Each pair stands in the bins NEXT TO its own run**, by C6-31f's
  division: the lower edge falls in the bin immediately before the
  run's first bin and the upper edge in the bin immediately after its
  last. Two things follow from the definition and both are refused
  without it. A pair could name two values that fall in bins the same
  description says hold nothing — ends 0 and 32, a run of bins 10 to
  12, the pair `[11, 12]` — which describes no column any table holds
  and was read by the value stage as two real cells. And a pair could
  reach FURTHER than the run — the same ends and run with the pair
  `[0, 32]` — although every bin the description does not name as
  empty holds something, so the largest value below the run is in bin
  9 and the smallest above it in bin 13.

**Q21 DOES NOT REACH THE PRODUCER.** It bounds the pairs against other
published facts and cannot check that a named edge IS the nearest real
value; a loader holds no table. What holds that is producer obligation
EE-P: for each run of `empty_bins`, `below` is the largest and `above`
the smallest of the values the statistics used on either side of it,
read with the same bin rule and from the same values as `empty_bins`.

**Disposition: REPORT-ONLY, and the class was MEASURED.** The fact is
CONSUMED: `docs/spec/generation-method-v1.md` G6.7 walks from these
two values rather than from the bin edges. THE LEDGER, on the three
two-cluster witnesses of `tests/test_p4d32_empty_bins.py`, in three stages, each measured the same way — forty seeds on each of the
three two-cluster witnesses, counting cells inside the SOURCE's own
widest gap rather than inside a bin:

* moved to the nearest occupied BIN: one cell per column per seed,
  15.7 to 23.0 units from the nearest real value;
* walking from the published EDGES, queue still gathered from the
  bins: **8, 4 and 27** of 12,000;
* asking the published PAIRS which stretch a stratum stands in:
  **0, 0 and 0** of 12,000, which is where the shipped pass is. It is not EXACT-OBSERVABLE
for the reason `empty_bins` is not — a block whose other published
facts leave no free value beside a stretch cannot always be moved out
of it, and where it cannot the value STAYS and the report names the
stretch — which is residual **R-P4-140**, the same one the bins
carry.

---

<!-- a7e: shape_forms -->

### 7.9 `shape_forms`

**C6-31a (what a form is).** The **written form** of a cell is that
cell with every FIGURE replaced by `%`, every LETTER replaced by `@`,
and every other character required to be one of THIRTEEN MARKS this
contract names, standing as itself. A diagnosis code `E11.9` has the
form `@%%.%`; a laboratory code `4548-4` has `%%%%-%`; a
dispensed-drug code `0002-8215-01` has `%%%%-%%%%-%%`; a blood
pressure `120/80` has `%%%/%%`. The marks are the STRUCTURE and the
figures and letters are the content, and the form is what is left when
the content is taken out.

**"EVERY DIGIT" AND "EVERY LETTER" ARE `0`–`9`, `a`–`z` AND `A`–`Z`,
AND A CELL HOLDING ANYTHING ELSE HAS NO FORM.** The ranges are fixed
by this contract and are NOT the running language's idea of a letter.

Both halves of that were learned the hard way. Replacing only the
ASCII ranges and letting every other character STAND left a column of
Japanese clinical text publishing a key that held the words
themselves. Replacing every letter the interpreter recognises instead
made the census depend on which Unicode database that interpreter
carries: five supported versions give five answers — U+16AC0 is a
digit in one and not the one before it, U+1E4D0 a letter in one and
not the one before it — so one table produced two different
descriptions, two different twins, and a quality report that called a
conforming twin MISSING on two exact counts, purely from where it ran.

A fixed range with everything outside it FORMLESS answers both: no
character of a value can stand in a key, because a cell holding one
has no form; and the census says the same thing everywhere. What it
costs is the census on a column of non-ASCII codes, which the twin
could not have written in its own alphabet in any case (7.9.1).

**THE THIRTEEN MARKS, and the list is CLOSED**: `-` `.` `/` `_` `:`
`#` `*` `(` `)` `[` `]` `+` `,`. **A cell holding any character that
is neither a letter, nor a digit, nor one of those thirteen has NO
FORM AT ALL** — a space among them, and so is every mark this list
leaves out. The list is closed rather than open because the guarantee
the census rests on is that a key carries no fragment of anybody's
value, and "every other character stands as itself" does not give it:
it is checkable that a key holds only `%`, `@` and these thirteen, and
not checkable that whatever else survived was harmless.

**AND THE SPACE IS EXCLUDED ON ITS OWN GROUND.** Two hundred and forty
different short sentences written to one template — `xxxxx, yyyy!` —
all share the form `@@@@@, @@@@!`, which names every word's length,
where the spaces fall and where the punctuation falls. That is a fact
about a sentence, which is what the length limit below was already
there to keep out, and it reached past the limit because the sentences
were short. Without a space, the cells that share a form are the cells
written to a scheme.

**A cell longer than TWENTY-FOUR characters has no form either, and
neither does an empty one.** The limit is deliberate and it is not a
performance limit: it is the same judgement as the space, applied to
the cells a scheme could not have produced.

**AND A FORM OF ONE KIND OF SYMBOL IS NOT A FORM.** `@@@@@` says five
letters; `length` already publishes the five exactly, and
`n_all_digits` and `n_code_alphabet` already publish which alphabet
the cells were drawn from. Such a key adds a published fact carrying
no information and costs a disclosure line for it. What a form is FOR
is the ORDER of the kinds and where the marks fall between them:
`@%%%%` says a letter and then four figures, which no other published
fact says, and `%%%%-%` says where the hyphen is. **So a cell has a
form only where at least TWO of the three kinds — figure, letter,
mark — appear in it.** That line is what keeps four region names from
publishing a census nobody can use while a procedure code `J1200`
keeps one.

**A FORM KEY MAY CARRY ITS CASE, AND THE CENSUS DECIDES WHERE** (landing
2b.18, plan P4-D121, audit LTM-6). The written form of a cell marks
every letter `@` whatever its case, and a twin reading only that wrote
capitals: a column of 800 lower-case codes `e9z-1i1` came back
`Y6O-7P3` on every row, a case-sensitive pattern matched 800 real
cells and 0 twin cells, and both files passed. So the census may name,
beside or instead of a form, that form's **LOWER-CASE KEY** — the form
with `&` in every letter place — counting the cells of the form whose
every letter was lower case. Per form, with `L` those cells, `R` the
rest, and the LINE the larger of `small_cell_floor` and two:

- `L` under the line, or the lower-case key's own supply short of the
  small-supply bound of C6-31c's test (a lower-case letter is one of
  twenty-six), or the column's `n_distinct` differing from its
  `n_distinct_folded`: the form is named blind to case, exactly as
  before this clause;
- `L` at the line and `R` nought: the lower-case key alone, counting `L`;
- `L` and `R` both at the line: both keys, the form's own key counting
  `R`;
- `L` at the line and `R` from one to under the line: the lower-case key
  ALONE, counting every cell of the form, `L` and `R` together (plan
  P4-D160). It named `L` and pooled `R`, and an `R` of one was a pool of
  one: 799 `abc-00001` beside one `ABC-00799` at a floor of twenty
  published `{"&&&-%%%%%": 799, "(withheld)": 1}`. Naming the form blind
  to case instead turned the twin's 799 lower-case codes into capitals.

**A LOWER-CASE KEY NAMED WITHOUT THE FORM'S OWN KEY COUNTS EVERY CELL OF
THAT FORM**, whatever its case, exactly as a form's own key named
without its lower-case key counts every cell of the form (plan P4-D160).
A recount counts under such a key the form's cells not in lower case
where they number fewer than the line, and none of them where they do
not, so a file writing the column in capitals still misses it. The key
then says the convention the form was written in, and the few cells
that broke it are counted nowhere apart.

**AND NO READING OF THE CENSUS NAMES ONE ROW** (plan P4-D160, the
disclosure rule of P4-D150, asked of the one helper the producer and the
loader share). A reader holds the pool, `n_present`, and on a free-text
column `n_code_alphabet`, beside the census. Until the `(withheld)` pool
is not one, `n_present` less every cell the census counts is not one,
and `n_code_alphabet` less the cells of the named forms made only of
`%`, `@`, `&`, `-` and `_` is not one:

- a pool of one takes in the smallest FAMILY of named keys (a form's own
  key and its lower-case key together; the earliest form in sorted order
  on a tie), or, where no key is named, is not written;
- a difference of one against `n_present` gives the pool up where it is
  written;
- otherwise the smallest family that total covers is no longer named.

A census that counts no cell is asked nothing. Measured before this
rule, at a floor of twenty: 799 `ABC-00001` beside one `WXYZ-123456`
published `{"@@@-%%%%%": 799, "(withheld)": 1}`, and beside one sentence
too long to have a form `{"@@@-%%%%%": 799}` against 800 present cells.

**WHY THE CASE IS PER FORM AND NOT PER POSITION.** A mark per letter
in its own case — `Ab12` against `aB12` — splits a mixed column into
forms the floor then pools, so a column publishing a form today would
publish none. Counting the all-lower-case cells of a form beside it
keeps every form a column had and adds only a count.

**WHY NO LOWER-CASE KEY ON A COLUMN WHOSE VALUES FOLD TOGETHER.** Its
twin writes values that differ only in case or edge spacing — the
partners of the generation method's G9.3 and the made-up variants of
G8.2 — and a case flip of a lower-case value is not lower case, so it
settles the form's own key and never the lower-case one. Measured on 240
cells, 200 `a-b` beside twenty `x00` and twenty `X00`: named apart,
the twin missed three keys by thirty-three cells. The test reads two
PUBLISHED counts, so the absence it causes is one a reader predicts, and so
tells them nothing.

**WHAT A READER GAINS, AND WHAT STAYS OUT.** The count of cells of a
form whose letters were all lower case, where enough of them share it
to name — and nothing about any one cell. Cells mixing the two cases
are counted under the form's own key and the twin writes them in
capitals; a pattern testing for upper case alone then matches more twin
cells than real ones, which is this clause's stated limit.

**C6-31b (where it lives, and what it holds).** A `constant`,
`binary`, `categorical`, `long_tail_labels` or `free_text` block
carries `shape_forms` as a key of the BLOCK. It is REQUIRED on those
FIVE roles, written even when empty, and FORBIDDEN on the other EIGHT;
section 6.11's matrix is the authority and this clause restates it. It
maps a written form to the number of present cells written in it, with
the pooled key `(withheld)` for the forms fewer than
`small_cell_floor` cells share.

**ON THE FOUR LABEL ROLES A CELL IS COUNTED AS ITS LEVEL ENTRY SPEAKS OF
IT** (plan P4-D275.1). W5 counts every spelling below the floor into its
level's commonest, so the block describes the table with those cells
written that way, and the census counts them there too: a cell of a
published level is counted in the spelling its level entry counts it
in, and a cell of a level the floor holds back in its own. The number of
different spellings C6-31c and C6-31d ask about is then the block's own
`n_distinct`. Measured before this sentence, at a floor of eleven: a
level of twenty `E11.9`, three `e11.9` and five `E11.9` with trailing
spaces published `variants {"E11.9": 28}` beside a census counting 23 of
its cells in the form, and the twin, writing the 28, was reported
MISSED.

**A FORM IS NAMED ON ITS COUNT ALONE, AND NEVER ON WHAT ELSE THE
COLUMN HOLDS.** The guarantee above reaches every cell that HAS a
form; a FORMLESS cell — one carrying a placeholder — is under no such
rule, so a column holding `E11.9` eleven times beside the literal text
`@%%.%` three times publishes the key `@%%.%` while also holding that
string. **The rule that would stop it is REFUSED, and refused twice**:
"do not name a form spelled the same as a present cell" makes
suppression DATA-DEPENDENT, and a reader runs the dependency
backwards — the published levels wear a form covering enough rows that
SF1 REQUIRES the key, the key is absent, only the collision rule
removes it, therefore a cell is spelled exactly like it. That is a
floor-suppressed value recovered EXACTLY from published facts.

What it would prevent discloses nothing to begin with: `@%%.%` is the
key ANY letter-figure-figure-point-figure column publishes, and a
reader cannot tell whether some cell is also spelled that way. The
coincidence tells nobody anything; the cure hands over a value. **A
census key is a fact about writing and is never withheld on account of
another cell.**

**IT STANDS ON ALL FOUR LABEL ROLES BECAUSE SUPPRESSION IS A FACT
ABOUT THE FLOOR AND NOT ABOUT THE ROLE.** It stood on
`long_tail_labels` alone for one landing, on the reasoning that the
other three publish their levels so their twins hold them and have no
stand-in to shape. That reasoning was wrong: a diagnosis column of
five common codes and twenty-six rare ones is under the categorical
ceiling, so it takes `categorical`, and the floor holds every rare one
back (P4-D18 corrected, A-P4-36).

**A CELL WITH NO FORM IS NOT POOLED. It is not counted at all.**
`(withheld)` means one thing in this format — a group too small to
name — and a cell over the limit is not a small group, it is a cell
this census does not describe. Pooling them would also break the
floor-of-one rule of section 4.6: at `small_cell_floor` of `1` nothing
is below the floor, so no `(withheld)` key may exist, and a producer
pooling formless cells would write one. C5-S13 refuses it.

**C6-31c (why the census is empty on a column of prose, and what
actually makes it so).** Two things do, and the FIRST is the one that
matters: a cell holding a space has no form, so no cell of a column of
notes, addresses or typed comments is counted at all and
`shape_forms` is `{}` there — not because every such cell's form is
its own, which was the earlier claim here and was FALSE. Where every
cell's form really is its own, the floor pools them and the census
reads `{"(withheld)": n}`; it never reads `{}` by that route.

The second is the floor, and it does the rest: a form fewer than
`small_cell_floor` cells share is pooled and never named. **Between
them the census selects for STRUCTURE with no rule anywhere deciding
which columns are structured** — no rule that could decide wrongly.
What a scheme's cells have in common is that they are short, they use
a small set of marks, and they hold no space; what prose has is the
opposite of each. The census is the intersection, not a judgement.

**C6-31d (key grammar, checked as a CLOSED ALPHABET).** A key is
either exactly `(withheld)` or a written form: at least one character,
at most twenty-four, every one of which is one of the three PLACEHOLDERS
— `%`, `@`, and `&` in a lower-case key, never `@` and `&` in one key —
or one of the thirteen marks C6-31a names, AND CARRYING AT LEAST TWO
OF THE THREE KINDS. A loader CHECKS this key by key and refuses the
document otherwise, rather than trusting that the producer built the
key by the replacement C6-31a states.

**BOTH HALVES, AND THE SECOND WAS MISSING.** The loader enforced the
two-kinds rule while this grammar stated only the alphabet, so the
contract admitted `%%%%` and `@@@@` that the shipped loader refuses --
a rule enforced by code and not stated here, which is the one thing
this document exists to prevent. It is stated now, and one predicate
in the producer answers for all three readings of it.

**The check is an alphabet and not a replacement audit, and the
difference is the whole guarantee.** Asking only that no OTHER figure
or letter survived leaves every character that is neither free to
stand in the key, which is how a column of Japanese clinical text
published its words. Under a closed alphabet nothing a table wrote can
pass, whatever wrote the key — a producer, or a file edited by hand.
This is what makes the key safe on `free_text`, whose F3 promises that
no fragment of a value stands anywhere in the block.

**C6-31e (invariants).** **SF1.** Every NAMED form's count is at least
`small_cell_floor` and at least two, whatever the floor (plan P4-D181):
below that line a form is pooled where the floor pools and counted
nowhere at a floor of one; a LOWER-CASE key's count, and the count of the
form's own key where it stands beside one, is at least two as well; and
the census holds no `(withheld)` count of one.
**SF3.**
Every count is at least 1, and the sum of all counts, `(withheld)`
included, is at most `n_present` — at most, and not exactly, because
the formless cells C6-31b excludes are present cells this census does
not count — and, where the census counts any cell, never exactly one
less than `n_present`; on a free-text column the named forms made only
of `%`, `@`, `&`, `-` and `_` count, where they count any cell, never
exactly one less than `n_code_alphabet`, nor than `n_code_alphabet` less
`n_all_digits` (plan P4-D160, P4-D175); and the named forms no number
can be written in -- a form with no `%`, with two letter marks, or with a
mark other than `.`, `,`, `+`, `-`, `(` and `)` -- count, where they
count any cell, never exactly one less than `n_not_numeric` (plan
P4-D175). **SF5.** A lower-case key is named only on a column whose
`n_distinct` equals its `n_distinct_folded`.

**Disposition: EXACT-OBSERVABLE**, on the same terms as the two width
censuses and against a recount identity of the same shape: cells of the
measured file recounted at a named form number AT LEAST the published
count and AT MOST that count plus the pooled `(withheld)` value. The
pool names no form, so it is checked as the pool it is and never
form by form.

#### 7.9.1 The binding generation rule

**C6-D18 (a stand-in wears a published form).** A twin's cells for a
label column come from three places: the published spellings, written
byte for byte; the made-up spellings standing in for a published
label's held-back ones (7.4, generation method G8.2); and the made-up
labels standing in for the levels the floor held back (G8.3). Only the
third is free to be anything, and where the column publishes a form
census it is written in one of the published forms.

**WHY, IN ONE CASE.** `group-14` is what a stand-in used to be, and on
a column of clinical codes it is wrong every way a stand-in can be: it
is the wrong length, it is lower-case where the codes are not, and on
a hyphenated scheme it carries a hyphen OF ITS OWN — so it passes a
"looks segmented" check, crashes a split into a fixed number of parts,
and, the word being exactly five characters, makes a width check on the
leading segment answer plausibly and wrongly. A person developing
against the twin then finds all three at once against the real file.

**THE FORM IS FILLED FROM A COUNTER AND NEVER FROM A READING.** Every
`%` of the form takes a figure, every `@` a capital letter and every
`&` of a lower-case key a lower-case letter, all taken off a step that
counts stand-ins; every other character of the form
stands as itself. The form was built by removing every figure and
letter before it was published, so nothing put back can be a fragment
of any value.

**A FREE-TEXT GROUP MAY TAKE A FORM OF ANY ADMITTED LENGTH, AND MUST
BE ABLE TO.** A form fixes a length, so which lengths a group may be
offered is the whole question. A group carrying a published length end
keeps its length exactly, because `length.min` and `length.max` are
EXACT-OBSERVABLE. Every OTHER group may take any form whose length
lies between those two ends: the length the packing gave it came from
`length.mean` and `length.p50`, which are APPROXIMATED, and this
format's precedence rule is that an exact count outranks an
approximated average. Holding every group to its assigned length was
how a blood-pressure column met the ONE form its middle length carried
and missed the two beside it -- the packing had put almost every group
at six characters, so no group was left to write `%%/%%` or `%%%/%%%`,
and sixty cells came out of the wide alphabet instead.

**THE CELLS ALREADY WRITTEN PAY THE CENSUS FIRST.** The census counts
every present cell of the column, and the first two of the three
populations above are already on the page wearing their forms. What a
stand-in owes is therefore the published count MINUS what those cells
paid, counted over the twin's own cells; a walk that took its debt
from the census alone would write every form twice over and miss every
count it was built to meet. Each stand-in covers its level's size,
which the description fixes, so the walk chooses only WHERE to pay and
settles the largest outstanding debt first.

**A STAND-IN KEEPS THE FOUR PROPERTIES THE NEUTRAL SPELLING HAD BY
CONSTRUCTION**, and they are now ASKED rather than had: it is not one
of the spellings that mean "no value", it reads as neither a number nor
a date, it carries no comma and no quote, and it does not begin with a
character a spreadsheet reads as the start of a formula. A candidate
failing any of them is stepped past, as is one already used in the
column, raw or folded.

**Where the census OWES THIS STAND-IN NO FORM, it wears the SHAPE OF
THE COLUMN'S OWN PUBLISHED LABELS** (landing 2b.18, plan P4-D122, the
carried item of landing 2b.12). Three ways a stand-in is owed no form,
and none of them is "a role that does not carry the key" — all four
label roles carry it (6.11, C6-31b). The census may be empty; it may
name only forms the published cells have already settled; or the
arrangement may deliberately leave THIS place neutral, because
settling a debt exactly can require a size to go unspent. **So C6-D18
does not say every suppressed level wears a CENSUS form**: it says a
stand-in the census owes a form to is written in it, and one owed none
is written in the shape the published labels wear. That shape is a
published fact already, because the labels are written byte for byte:
the shape worn by the most published rows, with `&` where every
spelling wearing it was lower case, provided the census names it in
neither case and it reads as no number. Its spellings are spent on the
LARGEST places the census owes nothing, and a large place paying a
named form trades with single rows summing to it exactly where that
lets the shape cover more rows — the named form keeps its count either
way (generation method G8.3b). Measured on the carried column, a code
column of `4-F` beside `12-AB` and longer at a floor of twenty: the
real mean cell length 7.204 against the twin's 9.907 before, and
7.204 against 7.204 after, with the length mix exact. **Where no
published label has such a shape, or its supply is spent, the stand-in
is `group-1`, `group-2`, … exactly as before.**

**WHICH MADE-UP SPELLINGS OF A PUBLISHED LABEL KEEP ITS FORM IS THE
LEVEL'S OWN FACT.** A made-up spelling of a PUBLISHED label must fold
onto that label, and the fold-preserving supply is the case flips and
then edge spaces (G8.2) — of which only the case flips keep the written
form. Which held-back group takes a form-keeping spelling is fixed by
that level's `shape_form_cells` (7.4.8): the published spellings cover
what they cover, and the walk gives the form to whole held-back groups
adding up to the rest (G8.1a).

**THIS PASSAGE ONCE DESCRIBED A DEFECT AND NOW DESCRIBES A RULE**, and
the history is kept because it is the argument for the key. The
description did not carry the fact, so the walk guessed: it offered the
label's own spelling to the LARGEST held-back group, on the reasoning
that the scarce form-keeping spelling covers the most cells there.
Where the source's own form-bearing held-back spelling covered a
SMALLER group, that offer wrote the form MORE often than any source
cell wore it, and where the largest group's flip was already published
it wrote it LESS often — a miss in both directions, measured on 120
columns of one family at a floor of eleven as 57 met, 31 short and 32
past. Two source columns whose entries were identical key for key
published different censuses, so no rule reading the description could
be right about both. Residual R-P4-34 carries that measurement;
amendment A-P4-47 publishes the fact and closes it.

**WHAT A SUPPLY STILL CANNOT ALWAYS REACH, stated because it is a real
limit and not an oversight.** A label of one letter has one case flip.
A hand-written description asking more held-back groups of such a label
to keep the form than the supply can spell is met as far as the supply
goes, and the twin's own report names the rest; no producer writes such
a description, because a source that spelled those groups had the
spellings to do it.

---

<!-- a7h: the layout of a record number -->

### 7.12 `layout_forms`

**C6-127 (what a layout is).** The **layout** of a cell is that cell
with every FIGURE and every LETTER replaced by ONE MARK SAYING WHAT
KIND OF CHARACTER STOOD THERE, and every other character required to
be one of FIFTEEN MARKS this contract names, standing as itself. A
UUID `a46d6753-ec14-8cb4-8e73-ca47ea90a8f0` in a lower-hexadecimal
column has the layout `~~~~~~~~-~~~~-~~~~-~~~~-~~~~~~~~~~~~`; a site
code `NYC-7480` has `@@@-%%%%`; a record number `REC4972605` has
`@@@%%%%%%%`; a national number `657 240 7282` has `%%% %%% %%%%`;
and `00282669`, being figures alone with a fill of two noughts, has
`!!%%%%%%`.

**THE SIX PLACEHOLDERS**: `%` a figure, `@` an upper-case letter, `&`
a lower-case letter, `~` a lower-hexadecimal character, `^` an
upper-hexadecimal character, and `!` A NOUGHT OF THE ZERO FILL OF A
CELL WRITTEN IN FIGURES ALONE IN A PLAIN COLUMN.

**THE ZERO FILL IS EVERY NOUGHT, NOT ONLY THE FIRST (plan P4-D126).**
It is every nought standing before the first other figure of a cell
written in figures alone, the LAST character of the cell excepted, so
`0` has the layout `%` and `000` has `!!%`; and it is marked only in a
PLAIN column (C6-128), where a figure is a figure and a leading nought
is a fill somebody wrote. A key holding `!` is therefore a run of `!`
followed by at least one `%` and nothing else. Marking only the first
nought said a cell was filled and not how far: measured on 800 cells of
`%08d` over 1 to 499,999, the real column opened `00` on 800 cells and
the twin on 78, and `len(x.lstrip('0')) <= 5` counted 158 real cells
against 1. How many noughts fill a cell is how many decades short of its
width the number was — a census of magnitudes under the floor, never a
value.

**THE FIFTEEN MARKS, and the list is CLOSED**: `-` `.` `/` `_` `:`
`#` `*` `(` `)` `[` `]` `+` `,` `{` `}`. They are the thirteen of
C6-31a and the two BRACES, which are here because a braced GUID —
`{B8B6D8FE-442E-3D43-7204-E52DB2221A58}`, which is how common database
and runtime exports write one — wears them, and a closed list that
omitted them would give that column no layout at all while appearing
to describe it.

**AND ONE SPACE BETWEEN TWO OTHER CHARACTERS (plan P4-D127)**, which
stands as itself. A national number written in groups wears it, and a
census that refused it gave that column no layout at all: measured, 800
real cells of `657 240 7282` matched `\d{3} \d{3} \d{4}` and 0 twin
cells did, both files at exit 0. What the space was kept out for is
prose, and prose is kept out by the rest of the rule: a space may not
open or close a cell or a key and may not stand beside another space,
and no other space character is admitted.

**A CELL HOLDING ANYTHING ELSE HAS NO LAYOUT AT ALL** — a space that
opens or closes it or stands beside another, a letter of another
alphabet, a mark this list leaves out, a placeholder, a cell longer
than SIXTY-FOUR characters, and a cell made of marks alone. The limit is sixty-four because the widest identifier
scheme in ordinary use is a braced GUID at thirty-eight. The last two
exclusions are each a PROPERTY and not a preference: between them they
are what makes "no cell that HAS a layout can be spelled the same as
any layout" true, in any column and in any table, which is the same
guarantee C6-31a's two placeholders buy the form census.

**C6-128 (the alphabet convention is the COLUMN's, and never one
cell's).** A column is hexadecimal exactly where every letter of every
cell this census describes is one of `abcdef` in EITHER case, at least
one letter appears anywhere, and, among the described cells of one
length, some position holds a letter in one cell and a figure in
another (plan P4-D154); its figures and letters then take
`~` where at least as many of those letters are lower case as upper,
and `^` where more are upper, and a cell written in the other case
wears the same marks. Every other column is PLAIN, and its letters take
`@` or `&` according to their own case.

**A LETTER THAT NEVER TRADES PLACES WITH A FIGURE IS A LETTER (plan
P4-D154).** Letters inside `a` to `f` do not show an encoding on their
own: `A1000000` to `F1000799` is a letter and seven figures, and read as
hexadecimal it published `^^^^^^^^` and its twin put a figure where
every real cell has its letter on 786 of 800 rows, both files passing.
What a hexadecimal encoding shows that a letter-then-figures scheme does
not is a position holding a letter in one cell and a figure in another.

**THE CASE DECIDES THE MARK AND NEVER WHETHER A COLUMN IS HEXADECIMAL
(plan P4-D125).** It did: a column whose letters appeared in both cases
was plain, and one upper-case UUID among 799 lower-case ones then gave
every UUID its own mask of figures and letters — 800 layouts of one cell
each, the mask of one person's identifier on the page — and at a floor
of eleven a census of nothing but its pool, whose twin wrote
`A----...J` on every row. A cell in the minority case is not counted
apart, so nothing about it is published; what that costs is the case of
those cells, which the twin writes in the column's case.

**THE RULE IS ALL-OR-NOTHING OVER THE COLUMN, AND THAT WAS MEASURED
RATHER THAN ASSUMED.** A hexadecimal mark decided character by
character gives eight hundred braced GUIDs eight hundred different
layouts, not one of which reaches two cells, because a figure is
ambiguous between the two cases — so a floored census publishes
nothing at all for the very column the mark was introduced for. On a
column of site codes `BOS-1234` it gives three layouts, because `B` is
a hexadecimal letter and `O` is not. Decided once for the column, each
of those two publishes exactly one layout covering 800 of 800.

**C6-129 (where it lives, and what it holds).** An `identifier` block
carries `layout_forms` as a key of the BLOCK. It is REQUIRED on that
ONE role, written even when empty, and FORBIDDEN on the other
FOURTEEN; section 6.11's matrix is the authority and this clause
restates it. It maps a layout to the number of present cells written
in it, with the pooled key `(withheld)` for the layouts too few cells
share to name (C6-130).

**IT IS NOT `shape_forms` UNDER ANOTHER NAME.** That census belongs to
the five label roles, is forbidden on this one by C6-31b, stops at
twenty-four characters where a UUID is thirty-six, and marks a letter
without its case — and each of those three alone would lose a UUID.
C6-31a's limit is a judgement about where a fact stops being about a
code and starts being about a sentence; it is right for those roles,
it does not reach this one, where no run of prose arrives because the
column is a record number by its owner's declaration, and it is left
exactly where it was.

**THE LENGTH CENSUS RIDES IN THIS KEY.** A layout is one mark per
character and is therefore exactly as long as its cell, so the census
of layouts IS the census of lengths. A column mixing a ten-character
and a seven-character system publishes `{"@@@%%%%%%%": 573,
"@%%%%%%": 227}`, which carries the length mix `{10: 573, 7: 227}`
that `min_length` and `max_length` cannot: those two give only the
ends. Nothing separate is published for it and nothing separate can
drift out of step with it.

**A KEY OF ONE KIND IS A KEY HERE, and that is a difference from
C6-31a rather than an oversight.** `@@@@@` is refused there because
`length` and the two alphabet counts already say five letters. On this
role they do not, and `%%%%%%%` beside `%%%%%%%%%%` is exactly the
fact the two length ends lose.

**C6-130 (the line, the small supply, the fill, and the pool).** A
layout is named only where at least THE LINE of cells share it: the
larger of `small_cell_floor` and TWO, because no count of one is ever
published (plan P4-D124). At a floor above one a layout under the line
is counted into the `(withheld)` remainder, and the remainder is written
only where it holds at least two cells; at a floor of one there is no
remainder (C5-S13) and such a layout is counted nowhere. Measured
before the line was two: 800 random codes of capitals and figures
published 56 layouts of one cell each, and a UUID column with one
upper-case row published 800. **AND A LAYOUT UNDER WHOSE KEY FEWER CELLS COULD EVER HAVE BEEN COUNTED
THAN `n_distinct` PLUS THE FLOOR IS NOT NAMED EITHER**,
because a layout with a small supply NAMES the values it describes:
`%-` has exactly ten cells that could have worn it, so a column
holding nine of them often enough to publish would hand a reader the
tenth. The test is over PUBLISHED facts only — the supply is a
property of the KEY, and `n_distinct` and the floor are already on the
page — so a reader can work out which layouts this rule refuses, and
an absence they can predict tells them nothing.

**THE SUPPLY IS THE CENSUS'S OWN CAPACITY AND NOT THE GENERATOR'S**
(`parsing.layout_supply`, plan P4-D260). A key of figures alone is
written only in a plain column, where the zero fill takes every nought
before the first other figure — the last character excepted — into a key
of its own, so `%%%` is worn by `100` to `999` and never by `012`: its
supply is 900, not the 1,000 spellings a generator can build from three
figure marks, and `!%%` is 90 and not 100. A key holding one `%` alone
keeps the full ten, because that figure is the last character and the
fill rule excepts it; every other key — one holding a mark, a space, a
letter or a hexadecimal place — keeps the enumeration count, because no
fill is marked in it. **Measured before this clause:** 900 record
numbers `100` to `999`, declared an identifier at a floor of eleven,
published `layout_forms={"%%%": 900}` beside `n_distinct` 900, because
1,000 clears 900 plus 11 — and the census then named every cell that
could wear the layout, which is the source's own value set. The twin
generated all 900 and both files validated at exit 0.

**A FILL DEPTH TOO RARE TO NAME IS COUNTED ONE NOUGHT SHALLOWER
(plan P4-D126).** A layout of two or more fill noughts that the line or
the small supply refuses gives its cells to the layout with one fewer
`!` — `!!!%%%%%` to `!!%%%%%%` — deepest first, which is a true statement
about them: a cell filled with three noughts was filled with at least
two. The step stops at one nought. A reader of the census reads a cell
the same way: under its own layout where that is named, and otherwise
under the nearest shallower named one.

**A SMALL-SUPPLY LAYOUT IS DROPPED AND NOT POOLED.** Pooling it would
write a `(withheld)` key into a description made at a smallest group
size of one, where there is no group below the floor for anything to
be held back into, and C5-S13 refuses such a document. A cell with NO
LAYOUT AT ALL is likewise counted NOWHERE — not named and not pooled —
because `(withheld)` means one thing in this format, a group too small
to name, and a cell this census does not describe is not a small
group.

**What that costs, stated plainly.** A column of very short codes
publishes little or nothing. Measured: a column holding `007` beside
`7` publishes `%%%` and nothing else, because `%` has ten spellings
and `!%%` a hundred. That is this contract's disclosure rule working
as written, and a reader must not read the absence as a defect.

**C6-131b (no count of one by subtraction, plan P4-D124).** A reader
holds three totals beside the census — `n_present`, `n_code_alphabet`,
and in a plain column `n_all_digits` — and subtracting from each the
named layouts inside its alphabet counts the cells that wear no named
layout. **NO SUCH DIFFERENCE IS ONE** where any named layout lies inside
that alphabet, because a difference of one says that one row of the
table is unlike every other, which the disclosure rule forbids as it
forbids a count of one. Measured before this clause: 799 record numbers
beside one `REC 123456` published `{"@@@%%%%%%%": 799}` against 800
present cells. The producer applies it until no difference is one:
where the difference against `n_present` is one and the pool is written,
the pool is not written; otherwise the smallest named layout that no
shallower named layout stands behind — the earliest in sorted order on
a tie, and for an alphabet total the smallest inside that alphabet — is
no longer named, and joins the pool at a floor above one. The rule is
asked of a census that writes ONLY its pool as well (plan P4-D151): 800
record numbers beside one cell of another layout, at a floor of eleven,
published `{"(withheld)": 800}` beside 801 present cells, and the pool
is not written there. It is asked of NOTHING where the census counts no
cell at all (plan P4-D152): an empty census leaves a reader nothing to
subtract, and a column of one present cell publishes one. **What it
costs, stated plainly:** a column in which exactly one cell wears no
named layout, and whose only named layout is the one taken back,
publishes no layout at all — `REC` and seven figures on 799 rows beside
one `TMP-42` publish `{}` and the twin is written by the enumeration.

**C6-131 (invariants).** **LF1.** Every NAMED layout's count is at
least the line: `small_cell_floor`, and never under two. **LF2.** The
`(withheld)` count, where written, is at least two. **LF3.** Every count
is at least 1, and the sum of all counts, `(withheld)` included, is at
most `n_present` — at most, because a cell this census does not
describe has no layout and is counted nowhere. **LF4.** Where that sum
is at least one, it is not exactly one less than `n_present`. **LF5.** Where a named layout is made
only of placeholders, `-` and `_`, the named layouts so made do not count
exactly one cell fewer than `n_code_alphabet`; and on a census carrying
no hexadecimal mark, where a named layout is made only of `%` and `!`,
the named layouts so made do not count exactly one cell fewer than
`n_all_digits`. **LF6.** Every key is written under one convention: no
`~` beside `^`, and no hexadecimal mark beside `@`, `&` or `!`.

**C6-132 (the binding generation rule).** Where the column publishes a
layout, the twin writes its cells to it. The census counts CELLS and
the generator spends GROUPS, and every cell of a group carries the
same spelling, so a group wears one layout or none. The census is
SPREAD over the identities by a smooth weighted rotation, largest
group first, so that no layout is bound to how often its values recur;
each group is then offered the layout the rotation gave it and every
other published layout after it, each only where the remaining count
covers the group and the length fits the group's own slot. **A GROUP NO
NAMED LAYOUT SERVES — a pooled cell, a cell too few to name, a cell of a
layout C6-131b took back — IS WRITTEN TO A MIX OF THE COLUMN'S OWN KINDS
(plan P4-D128)**: the figures and case letters the named layouts use
between them, placed over the figure and letter positions of a named
plain layout with no fill, never a mix the census names, so it is
counted into no published layout. Measured before the mixes: 800 random
eight-character codes of capitals and figures at a floor of eleven
pooled 448 cells, the twin wrote them `A-----2S`, and `[A-Z0-9]{8}`
matched 800 real cells and 352 twin cells. A group no mix serves either
is written by the enumeration that always wrote it, so a column
publishing no layout keeps its cells byte for byte. The disposition is EXACT-OBSERVABLE against the recount identity
below, and method section G9.6 states the construction.

**A CELL IS WRITTEN TO A LAYOUT ONLY WHERE IT RECOUNTS INTO THAT
LAYOUT.** A layout is filled from a counter, and a counter does not
know what this census's own reader will make of what it wrote: `%%%%`
filled at a step whose leading figure is nought spells `0123`, whose
layout is `!%%%`. Measured, before that requirement was written: a
column publishing `!%%%%%%%` 480 and `%%%%` 320 wrote 33 of its 320
four-character cells with a leading nought — a zero-filled four-figure
spelling its source never wrote.

**THE RECOUNT IDENTITY.** A person who opens the twin and reads the
layout off each cell, under every rule of C6-130, finds for every NAMED
layout at least its published count and at most that count plus the
pooled remainder. The pooled key names no layout, so it bounds rather
than binds, exactly as it does at 7.9. **THE RECOUNT DOES NOT APPLY
C6-131b** (plan P4-D124): that clause takes decisions about which of a
file's OWN layouts it may name, and a conforming file whose made-up
cells left one cell off its named layouts would otherwise have a layout
it holds at the published count taken back and be told it missed it.

**`!` IS THE ONE PLACE A MADE-UP WHOLE NUMBER MAY OPEN WITH A
NOUGHT**, and the mark is confined to cells written in figures alone,
so it can carry no text anybody chose: it is a writer's field width,
the zero fill a reader loses when a spreadsheet or a statistics
package reads `01586982` as 1586982. A run of noughts INSIDE a cell
that is not figures alone — the `000123` of `S23-000123` — is not
marked, and its twin writes those places from the figures.

**AND A LITERAL RUN IS NOT A LAYOUT.** A constant run of letters shared
by a whole column is a character-for-character fragment of every value
in that column, which invariants I3 and F3 forbade. It is a
population-wide fragment rather than any one person's, which made it a
question for the owner rather than a settled refusal, and this census
still names no literal: a layout key holds no letter. The owner's ruling
of 2026-09-17, item 1, publishes the one literal run that ruling names,
the prefix, in a key of its own beside this census; section 7.12a states
it.

### 7.12a `layout_prefixes`

**C6-138 (what is published, and the ruling it rests on).** A declared
identifier whose every present cell opens with the SAME literal text —
`REC` before seven figures, `P` before five, `ABC-` before a study
number — publishes that text, and its twin writes it, so a pattern or a
starts-with test written against the twin selects the rows it selects on
the table. This is the owner's ruling of 2026-09-17, item 1 (plan
P4-D202), and it amends invariants I3 and F3 for this case ONLY. Measured
before it, at 800 rows each: `^P\d{5}$` matched 800 real cells and 30
twin cells, `^REC\d{7}$` 800 and 0, `^ABC-\d{4}$` 800 and 0, and every
file validated at exit 0.

**C6-139 (the prefix, stated once).** The prefix of a set of cells is
the longest opening every one of them shares, cut back by four rules:
(1) it holds no figure; (2) a figure or a letter of every cell stands
after it, so no cell is ever published whole, not even as its prefix
beside the marks its layout names; (3) where it ends in a letter and some
cell goes on with another letter, it is cut back to its last character
that is not a letter, so `REC` beside `REX` publishes nothing and
`ST-A123` beside `ST-B456` publishes `ST-`; (4) it is made only of ASCII
letters, the fifteen marks of C6-127 and single spaces neither opening it
nor standing beside another, and holds at least one letter — an opening
holding anything else publishes nothing, and one of marks alone is
already in the layout. A HEXADECIMAL column (C6-128) is read under the
same four rules, with rule (3) asked of its own figures: every letter
there is one of `abcdef` in either case, so every letter is a figure of
base sixteen and the opening is cut back to its last character that is
not one. A hexadecimal prefix therefore always ends in a mark — 800
cells of `DE-` and six hexadecimal figures publish `DE-`, while `ab12`
beside `ab34` publishes nothing, `ab` being half a number (plan P4-D233,
closing the limit P4-D202 recorded). `parsing.literal_prefix`
is the one statement of this rule.

**C6-140 (the two scopes, and the disclosure rule).** The block carries
`layout_prefixes`, REQUIRED on `identifier` and FORBIDDEN on the other
fourteen roles (6.11), written `{}` where nothing is published — and
`{}` wherever `layout_forms` names no layout, because the twin writes a
prefix as part of a named layout and the band walk's own shapes cannot
carry it without spellings colliding: measured on 120 `S` and five
figures one of which held a stray byte, whose census C6-131b emptied, a
published `(column)` prefix left 43 twin cells not opening with `S` and
the twin failed at exit 3. Where the
column's present cells have a prefix, it is published under the key
`(column)` and nothing else is written. Otherwise, each NAMED layout of
`layout_forms` whose own cells have a prefix publishes it under that
layout's key. The second scope is THIS VERSION'S READING of the ruling,
which names the whole column, and is flagged to the owner: a column of
`REC` and seven figures beside `E` and six publishes
`{"@%%%%%%": "E", "@@@%%%%%%%": "REC"}`. EVERY ENTRY ASKS THE DISCLOSURE
RULE of `parsing.census_nameable`: the present cells opening with the
prefix reach the line, and the present cells that do not are nought or
reach it too, so no entry says that one row of the table is written
otherwise. Under `(column)` the second half is nought by construction and
the first is that the column clears the line.

AND EVERY ENTRY ASKS THE ROOM RULE (`parsing.prefix_leaves_room`; plan
P4-D270). C6-130 names a layout only where `layout_room` is at least
`n_distinct + small_cell_floor`, so that a named shape never spells the
column's own value set out. A published prefix FIXES characters of that
layout, and the count that has to clear the line is therefore
`prefix_room` — the layout's room once the prefix's own marks are
taken off it. Measured at a floor of eleven: 1,000 declared record
numbers `REC000` to `REC999` beside a constant column published
`layout_forms {"@@@%%%": 1000}`, `layout_prefixes {"(column)": "REC"}`
and `n_distinct 1000`; `layout_room("@@@%%%")` is 17,576,000 and clears
1,011 easily, `prefix_room` is 1,000 and does not, and seed 4 wrote all
1,000 of the table's own record numbers with both files at exit 0.
Where the room is short the PREFIX gives way and the census stands: the
census is what the twin's shape is built from and LP1 lets a prefix
stand only beside a named layout, so taking the census back would leave
the prefix nothing to stand on. `REC` and seven figures over 800 rows
leaves 10,000,000 cells for 811 and is published exactly as before.

**C6-141 (invariants).** **LP1.** `(column)` stands alone; every other
key is a layout `layout_forms` names; a census naming no layout carries
no prefix. **LP2.** Each prefix's own layout — every character marked as
`layout_form` marks it under the census's own convention, so a letter by
its CASE in a plain column and by the column's hexadecimal mark in a
hexadecimal one — opens every layout it is
published for (every named layout under `(column)`), and a figure or a
letter mark stands after it in each. That a `(column)` prefix stands
on a column whose present cells reach the line needs no invariant of its
own: LP1 puts it beside a named layout, and LF1 puts that layout's
cells at the line. **LP3.** Every layout a prefix is published for could
still have come from at least `n_distinct + small_cell_floor` different
cells once the prefix's own characters are fixed
(`parsing.prefix_room`, plan P4-D270). A value that is not a
prefix by rule (4) and C6-139's figure rule is a refusal (R16), and no
refusal quotes it.

**C6-142 (the binding generation rule).** A prefixed layout is written
as its TEMPLATE: the layout with its opening marks replaced by the
prefix, `@@@%%%%%%%` under `REC` being `REC%%%%%%%`. Every fill of G9.6
reads a layout character by character, fills a placeholder from the step
and leaves every other character standing, so a template is filled as a
layout is — the prefix standing where every real cell holds it — and a
cell is counted into the template only where it recounts into the layout
AND holds the prefix. The mixes of the pooled cells are made over
templates, and a mix whose layout is a named one is stepped over. A cell
of the band walk that owes a prefix — every cell under `(column)`, a cell
of a prefixed layout otherwise — has its opening overwritten with it
wherever the result is unwritten, keeps its class and band, is no hole
and no date, and wears no named layout the walk's cell did not; a
fold-collision partner not opening with a prefix it owes is taken only
where no member of its family keeps it. Method G9.6a states the
construction.

**The disposition is EXACT-OBSERVABLE:** a person opens the twin and
finds every cell a prefix governs opening with it — every present cell
under `(column)`, every cell wearing the layout otherwise — and the
validator recounts exactly that. **What it does not reach, measured and
stated.** Pooled cells written by the band walk still wear that walk's
own shapes: 790 `P` and five figures beside ten `P` and six at a floor
of eleven wrote all 800 twin cells opening with `P`, and `^P\d{5,6}$`
matched 790 twin cells against 800 real ones. And a column whose partner
is pinned to a length only a case flip reaches — 750 record numbers and
fifty of them again with a trailing space — writes one flipped prefix,
which the twin's report and the validator both name.

---

<!-- a7i: the spellings of a count column -->

### 7.13 `number_spellings`

**C6-133 (what it holds).** A `count` block carries `number_spellings`
as a key of the BLOCK. It is REQUIRED on that ONE role, written even
when empty, and FORBIDDEN on the other fourteen — `continuous` among
them, and every block reusing the numeric key set inside `affixed_number`,
`joined_numbers` and `numbers_with_labels`; section 6.11's matrix is the
authority and this clause restates it. It maps a SPELLING — the cell's
own text, `007` — to the number of cells that wrote it.

**WHY IT EXISTS** (landing 2b.18, plan P4-D123; the audit of numbers and
codes, its missed item on mixed padding). A column of coded answers
written `7` 115 times, `07` 119, `007` 123 and `0` 143 was described as a
count, and a count publishes how many cells wore each field width and
how many were padded — never WHICH number wore which. Its twin came back
`7` 178, `007` 123, `0` 80, `00` 63, `07` 55 and `05` 1: six spellings for
four, two of them spellings the real column never wrote, and both files
passed. No published fact could have said otherwise.

**C6-134 (when it names anything, and the disclosure line).** The census
is ALL OR NOTHING. It names every spelling with its count exactly where
ALL of these hold, and is `{}` otherwise:

- every cell read as a number is written in figures alone, one to
  fifteen of them — so every key is a whole number this format holds;
- at least two of those spellings write ONE number, which is the only
  thing the census is for: a column writing each number one way is
  already described by its field widths;
- EVERY spelling is written by at least the larger of `small_cell_floor`
  and two cells. A spelling too rare to name is never pooled, because
  beside the named ones a pool's count would be the complement of
  numbers anybody can add up, and a count of one is never published;
- and the spellings number no more than the categorical ceiling of the
  table, so a long column of counts is never turned into a list of every
  value it holds.

An empty census says only that one of the four did not hold, and no
count of anybody.

**THE ROLE DOES NOT MOVE.** The column stays `count`, its ladder, moments
and widths stand beside the census, and no column is routed by its
shape — review item P1-R6-F7's policy, reaffirmed by amendment A-P4-60,
which measured routing padded figures to codes and withdrew it. What
moves is one published fact on the columns that write a number two ways.

**C6-135 (invariants).** **SC1.** Every named spelling's count is at
least `small_cell_floor` and at least two. **SC2.** A census naming any
spelling sums to `n_numeric`, holds two keys writing one number, and
names no more spellings than the categorical ceiling. **SC3.** Its
spellings of nought count exactly `n_zero`.

**C6-136 (the binding generation rule).** Where the census names
anything, the twin's numbers ARE the census: each spelling written as
many times as it counts, in the order of the number it spells and then
of the spelling, the rows made random by the placement every content
list takes. Nothing is drawn for them, and every statistic published
beside the census was computed from exactly these cells, so the ladder,
the moments, the styles and the widths all hold. Generation method G6.8
states it.

**Disposition: EXACT-OBSERVABLE.** A person who opens the twin and
counts each spelling finds exactly its published count; the census
pools nothing, so no key is a window.

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

1. each `missing_by_source` spelling at exactly its published count,
   character for character — a spelling a JUDGED PASS put there
   included;
2. every other absent cell empty: the blank count and the withheld
   remainder;
3. all of them placed by the same single permutation that places
   everything else, with spellings assigned to absent slots in a fixed
   sorted order before the permutation runs.

A judged pass is either of the two this version has: the stand-in
number pass (over whole cells and over an affixed column's cores), and the
calendar placeholder pass of 6.6.4.

**C6-116 (why a judged pass's cells are written as the table wrote
them).** A reproduced TEXT spelling is read back as absence by a fixed
rule of the description alone — it is a member of the published
vocabulary (5.4.1), or a value the person named with `--missing-value`.
A stand-in NUMBER and a CALENDAR PLACEHOLDER are judged instead, by the
producer's outlier-and-share rule over the measured file's own values,
and a twin's generated distribution is not guaranteed to fire that
rule a second time. So the reading of a judged spelling is fixed by the
description as well: a checked file is read with every candidate a
column's `sentinel_verdicts` names as `read_as_missing` counted absent
in THAT column, without the rule being asked again (validation method
V2.4-A8). The file the description was written from reaches the same
reading either way. A twin's cells then read back as absence
by a fixed rule, and they are written the way the table wrote them,
so code that tests a column against its own stand-in — `== -999`, an
integer conversion, a filter on `9999-12-31` — does on the twin what it
does on the table. A judged spelling below the floor is not a key of
`missing_by_source`; its cells are counted in `n_missing_withheld` and
are written empty with that pool.

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
two pools of absent cells as empty fields, no per-field equality
holds between the twin's blank cells and any single published count.
What holds is a sum: the twin's recounted blank absent cells equal
`n_missing_blank` plus `n_missing_withheld`. The cells a judged pass
put there are not in it, because the twin writes them under their
published spellings; an identity adding them would be false by
construction, and a validator checking it would report a failure
against a correct twin — which is worse than no check, because it
teaches its reader to stop believing the report.

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
| S8 | every name in each of the four declaration arrays — `forced_identifiers`, `forced_codes`, `forced_measurements`, `forced_decimal_commas` — is some column's `name`; a name matching no column means the profile and the schema disagree | yes |
| S8a | no name is in `forced_decimal_commas` and also in `forced_codes` or `forced_identifiers`; those two silence the numeric reading, so the comma declaration could never be used and would be recorded and ignored | yes |
| S9 | `settings.categorical_floor <= settings.categorical_ceiling` | yes |
| S10 | every `publication_notes[i].column` is some column's `name` | yes |
| S11 | `publication_notes` is grouped by column in schema order, and within one column in producer emission order; the grouping is decidable, the within-column order canonical bytes a loader does not re-derive | yes |
| S12 | `relationships` has exactly the eight reserved keys, no ninth, every value exactly `null` | yes |
| S13 | at `small_cell_floor` 1 every field carrying what the floor held back is empty or zero, over 4.4's closed list; on each of the eight maps that list names the `(withheld)` ENTRY goes, never the map -- save the six censuses plans P4-D220 and P4-D221 took off it (owner rulings of 2026-09-17), whose pools stand at any floor and, since plan P4-D222, only alone. Checked before any column block is read | yes |
| S14 | each declaration record has exactly five keys | yes |
| C6-20 | `settings` has exactly its twenty-two keys; twenty-one or twenty-three is a document this contract does not describe | yes |
| C6-53 | a column block's key set is exactly the twenty-two universal keys plus the marked cells of its role's column in the forbidden-key matrix; every other key is FORBIDDEN, and refused by name | yes |

**Four membership rules of this part carry no identifier**, so no list
can cite them: the nine top-level keys (4.1), the seven `source` keys
(4.3), a level entry's four (6.3.1), a `publication_notes` entry's two
(4.5). THE `source` COUNT READ FIVE while the block held six, and is
corrected here with the seventh (`workbook`, 4.3b): a synopsis that
counts wrong is how a loader written from it comes to accept a
document this contract does not describe.

**AND S13's OWN LIST IS THE EIGHT MAP POSITIONS IT NAMES, NOT FOUR.**
An earlier synopsis here counted four pooled-entry maps and omitted
`pad_widths` and `shape_forms`, so a loader written from the synopsis
would accept a floor-one document carrying a pooled form entry that
the shipped loader refuses. The defining list at S13 is the authority
and it names eight: `missing_by_class`, `utc_offsets`,
`datetime_separators`, `numeric_styles`, `fraction_widths`, `pad_widths`, `field_widths` and
`shape_forms`. Each is normative where stated, and a loader enforces it
-- save that plan P4-D220 took the pools of `utc_offsets` and
`datetime_separators` off it, and plan P4-D221 the pools of
`numeric_styles`, `fraction_widths`, `pad_widths` and `field_widths`,
where S13 says so.

### 8.2 The cell census — X

| id | statement | loader? |
|---|---|---|
| X1 | `n_present + n_missing == n_rows`, the DOCUMENT's `n_rows`, never the per-column echo, a different quantity | yes |
| X2 | `n_numeric + n_not_numeric + n_out_of_range + n_contradictory == n_present`. The four classify the complete present CELL on all fourteen roles; on `affixed_number` they stand BESIDE its four core counts, never in place of them. ON A DECLARED RECORD NUMBER a part below max(2, `small_cell_floor`) is counted into the LARGEST part before they are published, ties to the first of the four (plan P4-D277, ruling 6 of 2026-09-17): the four are a census of two or more groups written as scalars, and 999 `REC` identifiers beside one `42` published `n_numeric 1`, `n_all_digits 1` and `n_not_numeric 999` while the layout census beside them was withheld for saying the same thing. The sum is unchanged, so this invariant is unmoved | yes |
| X3 | `n_distinct_folded <= n_distinct <= n_present` | yes |
| X4 | `n_distinct == 0` ⇔ `n_present == 0` ⇔ `n_distinct_folded == 0` | yes |
| X5 | `1 <= position <= n_columns` | yes |

### 8.3 Absent cells — N

| id | statement | loader? |
|---|---|---|
| N1 | `missing_by_class` carries exactly SIX keys — `(blank)`, `(date-sentinel)`, `(declared-missing)`, `(numeric-sentinel)`, `(text-code)`, `(withheld)` — always all six, on every column block of every role, and their six values sum to `n_missing` | yes |
| N2 | each `missing_by_class` value other than `(withheld)` is 0 or at least `small_cell_floor`: a class counting between 1 and the floor is pooled into `(withheld)` and reads 0 here. `(withheld)` is exempt — the remainder the named counts were pooled out of, and one remainder pools several classes | yes |
| N3 | on a column that is not a nothing-publishing column, `sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld == n_missing`; on a nothing-publishing column the same three are an upper bound, `<= n_missing`, and every key additionally names a member of the published vocabulary (C6-126). No key of the map is the empty spelling (C6-125), which would count a blank cell twice | yes |
| N4 | every value of `missing_by_source` is at least `small_cell_floor`, with no exemption, and `n_missing_blank` is 0 or at least the floor. `n_missing_withheld` is bounded in neither direction, for N2's reason | yes |
| N5 | no key of `missing_by_source` carries a first-party meaning — not the six class words nor any other name this format uses (`n_missing_withheld`, `n_sentinel_candidates_unpublished` among them), because a cell can say those too: such a key means cells of the table held that text. `levels[].variants` is the other map the TABLE keys | reading |
| N6 | the nothing-publishing class is decided from `role` and `structural_role`, which every block publishes, and never from a count reading zero: since C6-126 both absence counts mean the same thing on every column | reading |
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
| A4 | the triple (`role`, `statistical_type`, `quality_state`) is exactly one row of 5.2's fifteen-row table; refused rather than repaired, naming the column and its three values | yes |
| A5 | that table is total over the fifteen roles: every role of the vocabulary has a row, and no role has two | contract |

### 8.6 The label roles — B, and the six that restrict them

The eight B rows are stated over a block carrying `levels`, not over a
list of roles, so each binds `constant`, `binary`, `categorical` and
`long_tail_labels` identically.

| id | statement | loader? |
|---|---|---|
| B1 | every `label` is a folded identity: it equals its own trimmed, case-folded form, so a published label may never have appeared byte for byte in the table; what the table held is in `variants` | yes |
| B2 | `len(levels) + suppressed_levels == n_distinct_folded` | yes |
| B3 | `sum(entry.count for entry in levels) + suppressed_rows == n_present` | yes |
| B4 | `suppressed_levels <= suppressed_rows <= suppressed_levels * (floor - 1)` — owner ruling of 2026-09-17, plan P4-D201 | yes |
| B4b | `not parsing.pool_names_a_level(suppressed_levels, suppressed_rows, the rows the published levels cover)`: the labels held back never come to fewer rows than twice their number, because that pool forces a count of one — owner ruling of 2026-09-17 item 5, plan P4-D231, widened by P4-D239, and bounded against HALF the rows the published levels cover, rather than against the smallest published level, by P4-D271 — whose amendment of 2026-09-18 refuses a pool of exactly one row per level outright wherever it covers fewer rows than the published levels do | yes |
| B4c | `parsing.census_names_one_row` over each of `n_numeric`, `n_not_numeric`, `n_out_of_range` and `n_contradictory` against the published levels that read that way, with the class's own held-back rows handed in as a pool so a class no published level counts into is read too: no such difference is exactly one — plan P4-D261 | yes |
| B5 | every `entry.count` is at least the floor | yes |
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
| W5 | every `variants` value is at least the floor; every `variants_withheld` key is in `1 .. floor - 1`, which at a raised floor is empty, because the producer counts EVERY spelling below the floor into the level's commonest one (plan P4-D275, ruling 6 of 2026-09-17; the rule reached one-row spellings alone until then, so 490 `F`, 500 `M` and two `f` published `variants_withheld {"2": 1}` and the twin wrote two `f` cells) | yes |
| W5b | no `variants_withheld` key, read as a number, is 1, because a spelling ONE row wrote is a count of one — owner ruling of 2026-09-17 item 5, plan P4-D240 | yes |
| W6 | variant keys are distinct | yes |
| W7 | `variants` and `variants_withheld` are not both empty on one entry | yes |
| W8 | `shape_form_cells` is at least the `variants` rows whose spelling has a form and at most those plus the rows `variants_withheld` accounts for; a label with no written form carries nought. There is NO sum against the column's `shape_forms` (7.4.8, R-P4-80) | yes |
| W9 | with `S` the spellings the published levels name (every `variants` key and every spelling `variants_withheld` counts), `S + suppressed_levels <= n_distinct <= S + suppressed_rows`, on the four label roles and on a compound column's `labels` half — plan P4-D276's count read as a rule | yes |

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
| Q4 | `std` is `null` exactly when `n_used_in_statistics < 2` or `std_unrepresentable` is true; the two are different facts, so a reader never guesses which a `null` is. On a tail block below its own floor (TL2) every moment is `null` and this row is not asked | yes |
| Q5 | `skew` is `null` when `n_used_in_statistics < 3`, and when every parsed value is identical; it is a number otherwise. On a tail block below its own floor (TL2) it is `null` and this row is not asked | yes |
| Q6 | where every parsed value is identical and `n_used_in_statistics >= 2`, `std` is `0.0` and `std_unrepresentable` is false | yes |
| Q7 | where every parsed value is identical the exact mean is that value and this format holds it, so a `null` there is refused; `mean` is `null` only when the exact mean is not a finite binary64 value, and that general clause refuses no document, a loader holding no values to recompute a mean from | yes, in the identical-value direction |
| Q8 | the twin's integer rule is routed by the published `integer_valued`, never by whether the role name is `count`; a `continuous` column may publish `integer_valued: true` and its twin cells are whole numbers | reading — it binds the consumer, and no document is refused for it |
| Q9 | `numeric_share == (n_numeric + n_out_of_range + n_contradictory) / n_present`, a share of the present cells, and `0.0` where `n_present` is 0 — which Q3 forbids on these roles | yes |
| Q10 | `n_negative_unrepresentable <= n_out_of_range` and `n_negative_unrepresentable <= n_negative` | yes |
| Q11 | `n_zero <= n_numeric` | yes |
| Q16 | `kurtosis` is `null` when `n_used_in_statistics < 4` and when every parsed value is identical, a number otherwise, and for the `n` values used it lies between 1 and `n - 2 + 1/(n - 1)`. On a tail block below its own floor (TL2) it is `null` and this row is not asked | yes |
| Q17 | `n_distinct_values <= n_numeric`, and `n_distinct_values >= 1` wherever `n_used_in_statistics > 0` | yes |
| Q18 | `mode` is `null` exactly when `mode_count` is 0, and where `mode` is a number `2 <= mode_count <= n_numeric` | yes |
| Q19 | `percentiles_between` names exactly the ninety percents `percentiles` does not, each a number or `null`, and the hundred and one rungs of the named ladder and this one in percent order, `null`s passed over, never go down | yes |

**Q5, Q6 and Q7 all turn on "every parsed value is identical".** The
numeric roles fix that test where they state those three rules —
`percentiles.min == percentiles.max`, with a `null` endpoint under L3
reading NOT identical, so a `null` `skew` at `n_used_in_statistics >=
3` is refused there as on any column whose endpoints differ. It is the
only route to these three rows from a parsed document, and a reader who
supplied a different test would refuse different files.

**ON A TAIL BLOCK THE TEST IS `std == 0.0`** (stage 3, section 6.7a).
The two ends are usually withheld there, so "identical" cannot be read
off them; the spread is nought exactly where every value the statistics
used is one value, and `std_unrepresentable` false beside it. A block
below its own floor publishes no spread and none of these three rows is
asked of it.

#### GS1 — `group_separator`, on every numeric block

| id | statement | loader? |
|---|---|---|
| GS1 | `group_separator` is `"."` only on a column named in `settings.forced_decimal_commas` that the declaration reaches, and never `","` there; the numeric partition of a `numbers_with_labels` column the declaration reaches may carry `"."`, and so may the block nested in an `affixed_number` column the declaration reaches (landing 2b.16, plan P4-D106; the loader asks `a_decimal_comma_reaches` and no list of roles, which is what made that a change in one place), while a block nested in a `joined_numbers` column never does; a space, `"'"`, U+2019, U+00A0, U+202F and U+2009 may stand under either; a position of a `joined_numbers` column carries `""` | yes |

#### NS1, DP1 and WR1 — `negative_form`, `decimal_plus` and `wide_runs`, on every numeric block

| id | statement | loader? |
|---|---|---|
| NS1 | `negative_form` other than `"minus"` only where `n_negative` ≥ max(1, `small_cell_floor`) | yes |
| WR1 | `wide_runs` is one of `"none"`, `"canonical"` and `"respelled"`, and anything but `"none"` only where the point-free counts of `numeric_styles` — `plain`, `leading_plus` and `leading_zero` — plus its `(withheld)` remainder leave room for at least max(1, `small_cell_floor`) cells (the third form added by landing 2b.16 part 2, plan P4-D107; without it a padded column's own producer wrote a description this loader refused). It carries no count and never pools, and the floor holds it for the reason NS1 holds `negative_form` (plan P4-D91) | yes |
| DP1 | `decimal_plus` names `+` only at ≥ max(2, `small_cell_floor`) and never pools, carrying `{"(unavailable)": 0}` where it cannot name a count; its total ≤ the `decimal` count of `numeric_styles` plus its `(withheld)` remainder, and where that count is named what `+` leaves of it is nought or at least max(2, `small_cell_floor`) (plan P4-D140); `{}` on a position of a `joined_numbers` column | yes |
| NS2 | `negative_notations` names a notation only at ≥ max(2, `small_cell_floor`), counts a notation below that line into the COMMONEST NAMED one (plan P4-D274: with no such absorption `n_negative 12` beside `negative_form brackets` and `{"(unavailable)": 0}` proved eleven bracketed cells and one other notation), pools under `(withheld)` only where no notation reaches the line and only where `small_cell_floor` > 1, else `{"(unavailable)": 0}`; its total ≤ `n_negative`, and what it leaves of `n_negative` less `n_negative_unrepresentable` is nought or at least max(2, `small_cell_floor`) (plan P4-D140); `{}` on a position of a `joined_numbers` column | yes |
| TM1 | `thousands_marks` names a mark other than `""` on NS2's counting terms, never carries `(unavailable)` — a census that cannot speak is `{}` — leaves of `n_numeric` nought or at least max(2, `small_cell_floor`), and names whatever mark `group_separator` publishes wherever it names any (that last clause asked after GS1, plan P4-D140); `{}` on a position of a `joined_numbers` column | yes |

#### The U family — `numeric_unrepresentable`

| id | statement | loader? |
|---|---|---|
| U1 | `n_whole + n_fraction + n_whole_unknown == n_present` | yes |
| U2 | `n_positive + n_negative + n_sign_unknown == n_present` | yes |
| U3 | M1 and M2 hold of `n_distinct_by_occurrences`: its values sum to `n_distinct`, and its keys weighted by its values sum to `n_present` | yes |
| U4 | the role is a nothing-publishing column, so every key of `missing_by_source` names a member of the published vocabulary, both absence counts stand inside N3's upper bound, and every `sentinel_verdicts` entry has `candidate == "(withheld)"` (N3, V2, C6-126) | yes |
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
| D1 | the pair (`format`, `resolution`) is one row of the format table, and the binding is exact and TOTAL over all TWENTY members: `iso-date`, `month-first-date`, `day-first-date`, `compact-date`, `slashed-iso-date`, `textual-day-first-date`, `textual-month-first-date`, `dotted-month-first-date`, `dotted-day-first-date`, `two-digit-month-first-date`, `two-digit-day-first-date`, `dotted-two-digit-month-first-date` and `dotted-two-digit-day-first-date` take `date`; `iso-month` takes `month`; `year-quarter` takes `quarter`; `iso-datetime`, `iso-mixed`, `month-first-datetime`, `day-first-datetime` and `slashed-iso-datetime` take `datetime` | yes |
| D2 | `sum(utc_offsets.values()) == n_present - n_unparsed` — only cells that parsed have an offset | yes |
| D3 | every key of `utc_offsets` other than `(withheld)` maps to a count at least the floor and never below two, and `(withheld)` appears only when the pooled remainder is non-zero, and only alone (plans P4-D220 and P4-D222, owner rulings of 2026-09-17) | yes |
| D4 | an endpoint offset field naming a real offset names a key of `utc_offsets`: a value published in one field of a block that another field of the same block promises to withhold is a contradiction this format forbids | yes, in that direction — that `(none)` marks an endpoint cell wearing no offset, and `(withheld)` an offset the map is holding back, is *producer* |
| D5 | `datetimes_read_at` is `local` when the whole column shares one UTC offset, `utc` when two or more appear | yes, in the direction a document supports — two or more non-`(withheld)` keys in `utc_offsets` require `utc`; where the map is fully withheld either value is accepted, because it reads the same whether one offset wrote the column or ten — EXCEPT under a format whose reader takes no offset at all (`month-first-datetime`, `day-first-datetime`, `slashed-iso-datetime`), where `local` is the only value any column could have held (review item P4-DATE5-F1) |
| D6 | the pair (`resolution`, `time_precision`) is one row of this map, TOTAL over the FOUR resolutions and the SIX precisions, so all twenty-four pairs are decided: `date` permits `date`; `datetime` permits `minute`, `second` and `subsecond`; `quarter` permits `quarter`; `month` permits `month` — with ONE format-family narrowing inside the datetime row: `month-first-datetime`, `day-first-datetime` and `slashed-iso-datetime` read a clock in the `time_of_day` role's two forms, which carry no fraction, so those three members permit `minute` and `second` and not `subsecond` | yes |
| D7 | `subsecond_digits > 0` implies `time_precision == "subsecond"`, and `time_precision == "subsecond"` implies `subsecond_digits > 0` | yes |
| D8 | `n_unparsed < n_present` — the checkable form of "the ladder covers the parsed cells", so both endpoints are always real values | yes |
| D9 | every key of `utc_offsets`, and both endpoint offset fields, are `(none)` or `(withheld)` unless `resolution` is `datetime` AND `format` is an ISO member; under D1 that reaches every format member but TWO — only `iso-datetime` and `iso-mixed` may carry an offset at all, because the three slashed stamp members take a clock in the `time_of_day` role's two forms and no offset (review item P4-DATE5-F4; landing 2b.3) | yes |
| D10 | where `resolution` is `datetime`, the seconds field of `earliest` and of `latest` is `00` when `time_precision` is `minute`, and is not `60` when `datetimes_read_at` is `utc`; and where `resolution` is `datetime` and `datetimes_read_at` is `utc`, each endpoint moved onto the clock its own endpoint offset names stays inside the years `0001` to `9999` | yes — the loader holds all three fields it needs: the endpoint, its offset, the clock |
| D11 | `date_percentiles.min == earliest` and `date_percentiles.max == latest` | yes |
| D12 | every key of `datetime_separators` is `upper_t`, `space`, `lower_t` or `(withheld)`; every key other than `(withheld)` maps to a count at least the floor and never below two, and `(withheld)` appears only when the pooled remainder is non-zero; a `(withheld)` count stands alone, with no mark named beside it (plan P4-D220), and only over a population `parsing.census_pools` lets a pool stand on -- fewer values than the line, or no more than the permitted marks less one hold below it (plan P4-D222; stage 2 closed by the owner rulings of 2026-09-17) | yes |
| D13 | `datetime_separators` is `{}` where `resolution` is not `datetime`; on a datetime column whose `format` is not `iso-mixed` its values sum to `n_present - n_unparsed`, and on `iso-mixed` to `resolution_mix["iso-datetime"]`; a `month-first-datetime`, `day-first-datetime` or `slashed-iso-datetime` column carries only `space` or `(withheld)` | yes |
| D14 | `all_at_midnight` is `true` only where `resolution` is `datetime`, `n_present - n_unparsed` is at least the floor, each end stands at midnight on the wall clock of its own published offset and every `date_percentiles` rung at midnight under some offset `utc_offsets` names, and on the `utc` clock no offset is pooled; a `false` is never refused, because the canonical form drops the fraction (MN-P) | yes |
| D15 | `n_at_midnight` is absent (`null`), or at most `n_present - n_unparsed`, at least the floor — never fewer than two — and every parsed cell or at least that floor short of it; present only where `resolution` is `datetime` and, on the `utc` clock, no offset is pooled; equal to `n_present - n_unparsed` exactly where `all_at_midnight` is `true` | yes |
| D16 | on an `iso-mixed` column, `resolution_mix["iso-date"]` is at most `utc_offsets["(none)"]` plus `utc_offsets["(withheld)"]`, either absent key counting nought | yes |
| D17 | every key of `date_field_widths` is `padded`, `unpadded`, `first-padded`, `second-padded`, `first-field-padded`, `first-field-unpadded`, `second-field-padded` or `second-field-unpadded`, never `(withheld)`; every key maps to a count at least the floor and never below two (the disclosure rule, P4-D131); the census is `{}` unless `format` is one of the six variable-width members or one of the two textual members, and on a textual member only `padded` and `unpadded` may appear; and its values sum to at most `n_present - n_unparsed` while leaving none of those cells over or at least the floor (landing 2b.6, plan P4-D278: a cell that could show no width is counted into the commonest width by the producer, because both conventions spell such a cell the same way, so a census that names anything reaches the parsed total and the remainder is asked of it like the other three) | yes |
| D18 | every key of `month_name_styles` is one of the thirty-six joint style words, a name of May with the length `either` (P4-D133), and on `textual-day-first-date` one of the eighteen `no-comma` words; the census is held to the disclosure rule over `n_present - n_unparsed`, a count at least the floor and never below two and a remainder of nought or at least that many; the census is `{}` unless `format` is one of the two textual members; and its values sum to at most `n_present - n_unparsed` (landing 2b.6) | yes |
| D19 | every key of `quarter_marker_case` is `upper` or `lower`; the census is held to D18's disclosure rule; the census is `{}` unless `format` is `year-quarter`; and its values sum to at most `n_present - n_unparsed` (landing 2b.6) | yes |
| D20 | every key of `zulu_case` is `upper` or `lower`; the census is held to D18's disclosure rule over `utc_offsets["Z"]`; the census is `{}` unless `utc_offsets` names `Z`; and its values sum to at most `utc_offsets["Z"]` (landing 2b.6) | yes |

#### The V family — `sentinel_verdicts`, wherever a block carries one

| id | statement | loader? |
|---|---|---|
| V1 | every entry has `n_occurrences` at least the floor. A candidate below it is not listed at all: it is counted, unnamed, in `n_sentinel_candidates_unpublished`, the one field of this format that records a thing held back in its NAME rather than under the `(withheld)` word, and S13 puts that count at zero at a floor of one | yes |
| V2 | `candidate` is `(withheld)` on exactly the columns where `missing_by_source` is empty for N3's reason — a column whose publication class permits no value of the table anywhere in its block. Naming a candidate there would publish a value out of a column that publishes none, and on every other column no candidate reads `(withheld)` | yes |
| V3 | `verdict` is `read_as_missing` only when `reason` is `outlier_and_frequent`; the other four reasons all keep the candidate as an ordinary number of the column | yes |
| V4 | entries appear in three groups, in this order, and the rule is TOTAL over the candidates this format permits: (1) NUMBERS, ascending by the number; (2) CALENDAR DAY SPELLINGS, ascending by the candidate text; (3) `(withheld)`, ordered by `n_occurrences`, then `verdict`, then `reason`, so no position can say which of two withheld candidates is the smaller. The datetime section states the rule entire, with the reason it is written total rather than for the mixed case alone | yes |
| V5 | every member of `spellings` is a key of this column's `missing_by_source`, the members are in ascending order and each appears once, no spelling is named by two decisions of one column, the cells those spellings cover never outnumber `n_occurrences` and what is left over is nought or reaches `census_floor` of the smallest group size, the cells a column's `read_as_missing` decisions took out and name no spelling for come, over all of them, to at most `n_missing_withheld` on a column that publishes values (P4-D135), and a decision whose `verdict` is `kept_as_a_number` names none. It publishes no group the floor pooled and no spelling the block does not already carry: what it adds is the LINK between a published hole spelling and the pass that made those cells absent, which no count in this document can supply. The count bound is what makes that link checkable on the block's own arithmetic, so a description cannot claim a DECLARED word was one column's judgement (P4-D95) | yes |

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
| P2 | every value under a style NAME is at least max(2, `small_cell_floor`); `(withheld)` is present only when the pooled remainder is at least 1, and only alone, over no more cells than five styles hold below that line or fewer than it (P6, plans P4-D221 and P4-D222, owner rulings of 2026-09-17) |
| P3 | `numeric_styles` is never `{}` on the three roles carrying it |
| P4 | *reading*: `integer_valued` and the census are independent — `5.0` is whole, written with a point; a loader checks neither against the other |
| P5 | *F*, the sum of ALL `fraction_widths` values including `(withheld)`, obeys the case below that `numeric_styles` selects; an empty census has *F* = 0 throughout |
| P6 | every NAMED width's count, and a `(withheld)` count, is at or above max(2, `small_cell_floor`), and a `(withheld)` key stands alone (plans P4-D221 and P4-D222, owner rulings of 2026-09-17) |
| P7 | a width key is present only if its count is nonzero, so a present `(withheld)` value is at least 1 and *F* is zero exactly where the census is empty |
| P8 | where `numeric_styles` holds cells back and names no `decimal`, `fraction_widths` is `{}`, where it names no `leading_zero`, `pad_widths` is `{}`, and `field_widths` is `{}` (plans P4-D221 and P4-D222, owner rulings of 2026-09-17) |

- **P5.a — a `decimal` key is published.** *F* equals its value.
- **P5.b — no `decimal` and no `(withheld)` key.** No decimal cell
  exists: the census is `{}` and *F* is zero.
- **P5.c — no `decimal` key but a `(withheld)` key.** The census is
  `{}` (P8): a form the forms map holds back has no widths published
  (plan P4-D221, citing the owner rulings of 2026-09-17, which withdrew
  the four conditions that bounded a pooled census here; since plan
  P4-D222 the pool is the whole map).

### 8.x The affixed-number role — AF

| id | statement |
|---|---|
| AF1 | `affix_prefix` and `affix_suffix` are not both the empty string, UNLESS `affix_variants` is non-empty: the bare wrapper is a member of a vocabulary and may be the commonest member of one (C6-7a), and at least one published wrapper carries text |
| AF2 | `small_cell_floor <= n_affixed <= n_present` |
| AF3 | `n_affixed` is at least the parse-line count of `n_present`, applied as a COUNT, never a compared share |
| AF4 | `n_core_numeric + n_core_out_of_range + n_core_contradictory + n_core_not_numeric == n_affixed`, beside X2, not in place of it |
| AF5 | `n_core_numeric >= 1`, Q3 read over the cores |
| AF6 | *reading*: `integer_valued` is a fact about the CORES and is what a consumer routes on, never the role name |
| AF7 | every quantitative key obeys the invariant stated for it on `count` and `continuous`, read over the CORES of the population the block it sits in describes (C6-7b): every core on a column wearing ONE wrapper, and that wrapper's own cores on a column wearing a SET, `n_present` and `n_rows` reading for that same population |
| AF9 | `affix_variants` names each wrapper once, ascending by its own text, each count in `small_cell_floor .. n_rows` |
| AF10 | `1 <= n_core_distinct <=` the commonest wrapper's own count; `1 <= n_core_distinct_folded <= n_core_distinct` |
| AF11 | each entry's four class counts close on that entry's `count`, and its two core-distinct counts are bounded by it |
| AF12 | the commonest wrapper's own count — `n_affixed` less every entry's `count` — is at least `small_cell_floor` where a set is worn |
| AF13 | each entry's `numbers` block obeys section 6.7 over that entry's own counts and echoes its `count` in `n_rows` |
| AF14 | no wrapper is named twice across the whole vocabulary, the commonest pair included |
| AF15 | `1 + len(affix_variants)` is at most the category ceiling of section 4.4 |
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

### 8.x The census of written forms — SF

Binding on the five roles that carry `shape_forms` -- `constant`,
`binary`, `categorical`, `long_tail_labels` and `free_text` -- and
stated in full at section 7.9.

| id | statement |
|---|---|
| SF1 | every NAMED form's count is at least `small_cell_floor` and at least two, and a lower-case key's count, with the count of the form's own key standing beside one, is at least two as well, and the census holds no `(withheld)` count of one |
| SF3 | every count is at least 1, and the sum of all counts, `(withheld)` included, is at most `n_present` — at most, because a cell over the length limit has no form and is counted nowhere — and, where any cell is counted, never exactly one less; the forms no number can be written in never count exactly one less than `n_not_numeric`; on free text the forms of the code alphabet never count exactly one less than `n_code_alphabet`, nor than `n_code_alphabet` less `n_all_digits` |
| SF5 | a lower-case key is named only where `n_distinct` equals `n_distinct_folded` |
| LF1 | every NAMED layout's count is at least the line: `small_cell_floor`, and never under two |
| LF2 | the `(withheld)` count, where written, is at least two |
| LF3 | every count is at least 1, and the sum of all counts, `(withheld)` included, is at most `n_present` — at most, because a cell this census does not describe has no layout and is counted nowhere |
| LF4 | where the sum of all counts is at least one, it is not exactly one less than `n_present` (C6-131b) |
| LF5 | where a named layout lies inside the code alphabet, the named layouts inside it do not count exactly one cell fewer than `n_code_alphabet`; and on a census with no hexadecimal mark, where a named layout is figures alone, those do not count exactly one cell fewer than `n_all_digits` (C6-131b) |
| LF6 | every key is written under one convention: no `~` beside `^`, and no hexadecimal mark beside `@`, `&` or `!` |
| LF7 | every NAMED layout's supply, `parsing.layout_supply` of its key, is at least `n_distinct` plus `small_cell_floor` (C6-130, plan P4-D260) |
| LP1 | `layout_prefixes` holds `(column)` alone, or only keys `layout_forms` names; a census naming no layout, or carrying a hexadecimal mark, carries no prefix (C6-141, owner ruling of 2026-09-17) |
| LP2 | each prefix's own layout opens every layout it is published for, and a figure or a letter mark stands after it in each |
| LP3 | `parsing.prefix_room` of every layout a prefix is published for is at least `n_distinct + small_cell_floor`: a published prefix fixes characters of the layout it stands on, and the shape left must not spell the column's own values out — plan P4-D270 |

A key that is neither `(withheld)` nor a written form by the grammar of
C6-31d is a refusal and not an invariant: the loader checks the key
before it reads the count.

### 8.x The census of spellings of a count column — SC

Binding on the one role that carries `number_spellings`, `count`, and
stated in full at section 7.13.

| id | statement |
|---|---|
| SC1 | every spelling the census names was written by at least `small_cell_floor` cells and by at least two |
| SC2 | a census naming any spelling names every cell read as a number, so its counts sum to `n_numeric`; at least two of its keys write one number; and it names no more spellings than the categorical ceiling |
| SC3 | its spellings of nought count exactly `n_zero` cells |

A key that is not one to fifteen figures and nothing else is a refusal
and not an invariant, and `(withheld)` is never a key of this census.

### 8.x The resolution mix — RM

| id | statement |
|---|---|
| RM1 | `resolution_mix` keys are exactly what the column's `format` permits: on a single-format column that member, on `iso-mixed` exactly `iso-date` and `iso-datetime`. The counts are exact and no floor governs them, and that is safe only because a form written by fewer cells than max(2, `small_cell_floor`) is COUNTED INTO the commonest form before this census is taken, so by the time it counts anything either both forms reach the line or only one form is left (plan P4-D250; 395 ISO dates beside one moment publish `{"iso-date": 396}` and `datetime_separators {}`, naming no record) |
| RM2 | values sum to `n_present - n_unparsed`; on `iso-mixed`, the joint reading being the chosen format, `n_unparsed` counts cells reading under neither member |
| RM3 | where more than one form carries cells, every non-nought count is at least `census_floor` of the smallest group size: a form fewer cells wrote is counted into the commonest form and the column is published wholly in that form |

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
| NG14 | for every form: one of the 58 the note grammar enumerates |
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
| DF-P | both readings of the column's own ambiguous pair were counted, the reading used parsed strictly more cells, and the declaration decided only a tie | the winning `format` is recorded, the losing count is not |
| DF-R | where the option was given and a slashed reading was in play, the column bears that remark exactly once, over the EVIDENCE, not the winner | whether a reading was in play is a fact about the table |
| CP-P | a published calendar-placeholder verdict is the one the outlier-and-share rule reached over the source's written days | the rule ran over a table a loader never holds |
| RM-P | the `resolution_mix` counts are the counts the source's own cells wore | a 40/60 and a 50/50 split of a hundred cells both satisfy RM1 and RM2 |
| DS-P | every `datetime_separators` count is the count of parsed source cells written with that mark, the commonest named mark's count with every cell whose mark was written by fewer rows than `parsing.census_floor` added (plan P4-D222), and the pooled value the count of every cell that writes a clock where no mark reaches that line | D12 bounds the entries and D13 the total; a 40/60 and a 50/50 split of a hundred cells both satisfy them |
| MN-P | `all_at_midnight` is `true` exactly where D14's conditions hold and every parsed source cell named midnight on its own wall clock, every fractional digit zero | the published instants carry no fraction and name eleven of the cells, so a column with one cell off midnight reads the same |
| NM-P | `n_at_midnight` is the count of parsed source cells that named midnight on their own wall clock, where C6-25c publishes it | D15 bounds it and ties it to `all_at_midnight`; a column with 361 values at midnight and one with 360 both satisfy it, and a column publishing nothing there may hold none, one, or all but one |
| FW-P | every `fraction_widths` count is the count of source cells written at that fraction width, the commonest width's count with the cells of rarer widths and the cells the forms map counted into `decimal` added (plan P4-D222) | P5 bounds the total and P6 and P7 the entries; none checks the census's SHAPE |
| PW-P | every `pad_widths` count is the count of source cells written at that field width | P5b bounds the total and P6b and P7b the entries; none checks the census's SHAPE |
| XW-P | every `field_widths` count is the count of source cells written as a whole number at that field width | P9c bounds the total from both sides against the styles map, P6c and P7c bound the entries; none checks the census's SHAPE, and none compares it against `pad_widths`, whose cells are a subset of these, beyond P6c's disclosure rule at a width both name (plan P4-D148) |
| SF-P | every `shape_forms` count is the count of source cells written in that form, and the pooled value the count of cells whose form too few shared | SF3 bounds the total from above and SF1 the named entries; none checks the census's SHAPE, and none can see the cells that had no form at all |
| SC-P | where a count column writes one number more than one way, every cell read as a number is written in figures alone, every spelling clears the line of 7.13 and the spellings are within the ceiling, `number_spellings` names every spelling with its count, and it is `{}` otherwise | SC1 to SC3 check a census that is published; none can see a census that should have been and was not |
| LP-P | a `layout_prefixes` entry is written exactly where C6-139 finds a prefix over the cells of its scope and C6-140's disclosure rule admits it, `(column)` first | LP1 and LP2 check an entry that is written; none can see the source cells, so none can tell a prefix that should have been published from one that was not, nor whether the published text is the one the cells hold |
| LF-P | every `layout_forms` count is the count of source cells written in that layout, and the pooled value the count of cells whose layout too few shared | LF3 bounds the total from above and LF1 the named entries; neither checks the census's SHAPE, and neither can see the cells that had no layout at all. LF7 now checks the small-supply rule of C6-130 in the one direction a loader can — no named key has too small a supply — but not the other, because a key the rule REMOVED leaves no trace a loader could require; nor can any of LF1 to LF7 see the fill step of C6-130, which moves a rare depth's cells under a shallower key, or which named layout C6-131b took back — LF4 and LF5 check that no difference is one, not that the smallest layout was the one taken |
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
every one of the fifteen roles, plus every top-level key, and FAILS
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
| `source` | STRUCTURAL | membership: its six keys, section 4.3 |
| `n_rows` (document) | EXACT-OBSERVABLE | the twin has this many data rows |
| `n_columns` | EXACT-OBSERVABLE | the twin has this many columns |
| `profile_version` | LOADER-ONLY | the integer 6 |
| `settings` | LOADER-ONLY | whole subtree: all seventeen keys, `day_first` and `long_tail_minimum_level` among them, and both declaration records with all five of their keys — `built_in_dates` included |
| `created_with` | LOADER-ONLY | |
| `publication_notes` | LOADER-ONLY | whole subtree |
| `relationships` | LOADER-ONLY | whole subtree; eight `null` slots |
| `source.encoding` | REPORT-ONLY | how the table was read; the twin is written back in it, which the byte rule `bytes.encoding` checks (plan P4-D86, which closes residual R-P2-5) |
| `source.dialect` | EXACT-CONTROL | decides how the twin's bytes are written: section 4.3a |
| `source.workbook` | EXACT-CONTROL | how a workbook holds the table, and what the twin has to be written as: section 4.3b |
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
| `missing_by_source` | EXACT-OBSERVABLE, recounted per spelling from the written twin — every key, a key a JUDGED PASS put there included |
| `missing_by_class` | REPORT-ONLY, all six classes — the classes are not recoverable from bytes |
| `n_missing_blank`, `n_missing_withheld` | REPORT-ONLY, bound by the sum identity: the twin's recounted blank absent cells equal `n_missing_blank` plus `n_missing_withheld`. A per-field equality would be false by construction, because the twin writes both pools blank |
| `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory` | EXACT-OBSERVABLE by class-preserving construction, over the CELLS on every role |
| `n_sentinel_candidates_unpublished`, `sentinel_verdicts`, `detection_evidence`, `remarks` | REPORT-ONLY |

**A judged pass's key is held at the reproduction rule's own width,
and a narrower reading is a defect.** The rule the twin obeys writes a
spelling a judged pass put there — one reading as a stand-in NUMBER,
*or* as a CALENDAR PLACEHOLDER — at its published count like every
other key, and both read back as absence for one reason: a checked
file is read with the candidates each column's own verdicts name as
`read_as_missing` counted absent in that column (C6-116), so the
reading does not wait on the outlier-and-share rule firing again over
the twin's generated values. A row holding only the stand-in numbers
would let a producer leave a published placeholder spelling out, and
code testing a date column against its own `9999-12-31` would then
select rows of the table and none of the twin.

`sentinel_verdicts` is REPORT-ONLY for calendar-placeholder entries
exactly as for stand-in numbers: a placeholder entry publishes the
placeholder's canonical ISO day spelling as its `candidate`, with its
occurrence count, verdict and reason. The twin holds the cells of a
`read_as_missing` entry under the spellings `missing_by_source`
publishes for them, and holds no cell of a spelling below the floor.

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
| `integer_valued` | EXACT-OBSERVABLE, routed by the published FACT and not by role; REPORT-ONLY only where no stratum that may take a value has a share holding a number a double can represent with anything after the point, which the report then names (A-P4-48, `beyond-whole-steps`) |
| `mean`, `std`, `skew` | APPROXIMATED, fixed formula and two-sided bound — G12.3 |
| `tails` | LOADER-ONLY: the container carries no obligation of its own, each leaf below it is disposed on its own line, and invariants TL1 to TL6 are what the loader holds the block to |
| `tails.low.mean_distance`, `tails.low.rms_distance`, `tails.high.mean_distance`, `tails.high.rms_distance` | APPROXIMATED, inside the window `docs/spec/generation-method-v1.md` G12.13 draws from G5.6's rank form over the tail ladder, and HELD where the file's own number equals the published one, as `docs/spec/validation-method-v1.md` has it for every approximated fact. The file's tail is read AT THE PUBLISHED PERCENT; where the file's own tail stands elsewhere the comparison is withheld rather than made at another percent |
| `tails.low.values`, `tails.high.values` | EXACT-OBSERVABLE: the generator writes a listed tail on those values and on no others, each at least once (G5.3e), so a file's own tail at that percent lists the same values. Empty on every tail the rule does not list, where there is nothing to check |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE using the spellings owner decisions 7, 8 and 10 permit — the ordinary case; APPROXIMATED under the two-sided envelope only where even those cannot supply the count, with the report naming the profile's count beside the twin's. The envelope is G12.8, and BOTH of its ends are measured and printed on every run, because a fallback whose range is never shown is a fallback a reader cannot check (review item P2-C2-F4) |
| `numeric_styles` | EXACT-OBSERVABLE against the recount identity of section 7.5.7: every published count is met or exceeded, the three forms the remainder cannot reach are exact, and the remainder is spelled by its own cells' values |
| `wide_runs` | EXACT-OBSERVABLE where the column publishes `"canonical"`: FEWER than max(2, `small_cell_floor`) point-free cells of the twin past 2**53 — `plain`, `leading_plus` or `leading_zero`, the padded cell read after its pad comes off (plan P4-D107) — may be anything but the figures their own values write, which is the same line the producer draws between `"canonical"` and `"respelled"` (plan P4-D140), so that the real table still meets its own description where one of its keys is respelled, which is the one ceiling the published count of a form cannot supply — on a column of identifiers that count IS the row count, so the ceiling beside it licenses every cell. Where the column publishes `"respelled"` the description has said its own writer respells them and holding the file to a ceiling of nought would be the false accusation plan P4-D66.2 ends; where it publishes `"none"` fewer cells than the floor are such runs, so there is no published cell for the ceiling to govern. `synthtwin validate` LISTS the fact in both of those states rather than holding the file to it |
| `pad_widths` | EXACT-OBSERVABLE against a recount identity of the same shape as `fraction_widths`: recounted padded cells at a named width number at least the published count and at most that count plus the pooled `(withheld)` value. A named width is honoured by PADDING and never by adjusting the value — `000123` and `123` read back as the same number — so no rung, endpoint or statistic is ever spent to reach one. Where a width is named the leading-zero family is spent on it, because every further spelling of a value is one figure wider; raw `n_distinct` then falls to its own two-sided envelope under the authorization owner decision 11 already carries, "only where even those cannot supply" |
| `fraction_widths` | EXACT-OBSERVABLE against a recount identity of the same shape: recounted cells at a named width number at least the published count and at most that count plus the pooled `(withheld)` value — exact where nothing pooled, windowed where something did. Widths are met by value adjustment inside the value-construction stage, so a pinned cell counts toward a width only when its value already fits it |
| `number_spellings` | EXACT-OBSERVABLE, on `count` alone: every published spelling is recounted on the measured file and must number exactly its published count. The census pools nothing, so no key is a window (section 7.13) |
| `field_widths` | REPORT-ONLY, and 7.10 carries the measurement the class was chosen on. Unlike `pad_widths`, a named width here is a fact about the VALUE and not only about the spelling — an unpadded cell is exactly as wide as its value — so it can be met only by the value-construction stage, and that stage places values by the ladder. `docs/spec/generation-method-v1.md` G6.6 takes the census as a constraint on the figure count of each stratum's value, within the half unit G5.4's integer rule already spends; where a width has no such value to reach it, the twin's report names the shortfall with the count it reached and `synthtwin validate` LISTS the census rather than holding the file to it |
| `empty_bins` | REPORT-ONLY, and 7.11 carries the measurement the class was chosen on. The value stage READS it — `docs/spec/generation-method-v1.md` G6.7 moves any stratum that landed in a named stretch to the nearer of the two values `empty_edges` names for that stretch, and no further past it than one bin — and on the two-cluster columns it was built against that took the cells landing in a named stretch from 4–6 of 300 to none at forty seeds of forty. It is not exact because a column whose other published facts leave no room beside a stretch cannot always be moved out of it: 119 of 1600 runs over forty described columns still wrote one such cell, and each is named in the twin's own report while `synthtwin validate` LISTS the fact rather than holding the file to it |
| `empty_edges` | REPORT-ONLY, and 7.11a carries the measurement. It is the fact the value stage actually walks from: `empty_bins` names bins, and a bin is a thirty-second of the column's reach, so the empty bins lie strictly INSIDE the stretch the source really leaves empty and a cell moved to a bin edge was still in the source's own gap. The pairs name the two real values each stretch lies between. Measured over three two-cluster witnesses at forty seeds each: cells inside a source's own gap fell from one per column per seed, 15.7–23.0 units from a real value, to NONE — 0 of 12,000 on each. It is REPORT-ONLY for the same reason `empty_bins` is, and the shortfall it can still have is the one the bins carry at residual R-P4-140 |
| `tails.low.percent`, `tails.high.percent`, `tails.low.rows`, `tails.high.rows` | LOADER-ONLY, and section 6.7a carries the reason: each follows from `n_used_in_statistics` and the smallest group size alone, TL1 and TL4 hold the description to both, and a file of the same count of values re-describes them identically -- so a check here would repeat `n_used_in_statistics` under another name. `synthtwin validate` LISTS them |
| `bin_groups` | REPORT-ONLY, for the reason `value_histogram` is: the twin's cells are allotted to values by the runs of the published ladder and not by a census of bins, so meeting a group's count exactly would mean the allotment following the census. It is what makes a histogram survive a raised floor at all -- the all-or-nothing census vanishes on every non-uniform shape at a floor of eleven and these groups do not |
| `n_rows` (echo) | LOADER-ONLY |

A mutant that collapses the nine interior rungs onto the endpoints
must FAIL the rung envelope. So must a mutant that ignores, permutes
or swaps rungs.

**`affixed_number`.** The four universal census counts of 9.2 answer
for the CELLS on this role as on every other. The keys below describe
the CORES, and every quantitative disposition above is read here over
the cores and over `n_core_numeric` in place of `n_numeric`.

**A KEY THIS ROLE SHARES WITH THE NUMERIC ROLES IS DELEGATED, NEVER
RESTATED, AND ITS CELL IS EXACTLY THE DELEGATION AND NOTHING ELSE.**
The disposition cell of such a row reads `as on `count` and
`continuous` above`, character for character, with no note beside it.
There is then exactly one place a shared disposition is written, and
nothing in this table can qualify, except or contradict it. Only the
keys this role ADDS carry a class below, because those are disposed
here and nowhere else.

**FOUR adversarial rounds beat four successive checks** that tried to
hold a restatement to what it restated: by the second class word in a
row, then by a conditional clause attached to it, then by free prose
beside a delegation that named no class at all ("for affixed cores
this value need only be mentioned in the report"). The answer was to
stop having two statements to compare, and then to leave the cell no
room to make a second one (review items P4-A1-R3-F1, P4-A1-R4-F1).

**What the delegated rows used to say, kept here because it is the
scope of the whole table rather than a per-key rule.** Every
quantitative disposition of 9.4 is read over the CORES and over
`n_core_numeric` in place of `n_numeric`: the ladder ends are exact
values of real cores, the interior rungs take G12.2's envelope and the
moments G12.3's bounds read over them, the three spelling censuses
take the same three recount identities read over them, **the census
of whole-number field widths is REPORT-ONLY over the cores exactly as
it is over a plain numeric column's cells (P4-D30)** -- a fourth map
beside those three, and the one of the four that no recount identity
holds -- and the
distinctness counts are met by the numeric mechanism supplying
spellings over the cores while the affix pair stands unchanged on
every counted cell. **`integer_valued` is computed over the cores and
routed on as the published FACT, never inferred from the role name
(AF6)** -- a rule of this role's own, stated here because its row is
now a bare delegation.

| field | disposition |
|---|---|
| `affix_prefix`, `affix_suffix` | EXACT-OBSERVABLE — written byte-for-byte around every counted cell's core, and recounted from the written twin |
| `affix_variants` | EXACT-OBSERVABLE — the other wrappers this column wears (plan P4-D36), each written byte-for-byte around the count of cores the description gives it, and recounted from the written twin. A column wearing one wrapper carries an empty list and is described exactly as it was |
| `n_core_distinct`, `n_core_distinct_folded` | EXACT-OBSERVABLE, on the same terms as the column's own two counts of different cells — including G12.8's two-sided envelope, which reaches these for the reason it reaches those: the cores are handed to the numeric block as a column of their own, so a count the published core spellings cannot supply is a shortfall that block already authorizes. On a column wearing ONE wrapper the two pairs are one shortfall measured twice, and the exact bar written here first reported it as an authorized deviation on the cells and a MISS on the cores in the same run. They are the counts of different CORES, which is a different number once a column wears more than one wrapper: the generator spends them as its budget of core spellings, and spending the cell counts there asked the core stage for spellings it does not need and cannot reach |
| `n_affixed` | EXACT-OBSERVABLE — the twin writes exactly this many cells wearing the pair; the remaining present cells are reproduced by class through the straggler constructions |
| `n_core_numeric`, `n_core_out_of_range`, `n_core_contradictory`, `n_core_not_numeric` | EXACT-OBSERVABLE by class-preserving construction over the cores |
| `percentiles.min`, `percentiles.max` | as on `count` and `continuous` above |
| `percentiles` interior rungs | as on `count` and `continuous` above |
| `mean`, `std`, `skew` | as on `count` and `continuous` above |
| `tails` | as on `count` and `continuous` above |
| `tails.low.mean_distance`, `tails.low.rms_distance`, `tails.high.mean_distance`, `tails.high.rms_distance` | as on `count` and `continuous` above |
| `tails.low.values`, `tails.high.values` | as on `count` and `continuous` above |
| `n_zero`, `n_negative`, `std_unrepresentable`, `n_negative_unrepresentable`, `n_used_in_statistics`, `n_left_out_of_statistics`, `numeric_share` | as on `count` and `continuous` above |
| `integer_valued` | as on `count` and `continuous` above |
| `numeric_styles`, `fraction_widths`, `pad_widths` | as on `count` and `continuous` above |
| `field_widths` | as on `count` and `continuous` above |
| `empty_bins`, `empty_edges` | as on `count` and `continuous` above |
| `tails.low.percent`, `tails.high.percent`, `tails.low.rows`, `tails.high.rows` | as on `count` and `continuous` above |
| `bin_groups` | as on `count` and `continuous` above |
| `n_distinct`, `n_distinct_folded` | as on `count` and `continuous` above |
| `wide_runs` | as on `count` and `continuous` above |
| `n_rows` (echo) | as on `count` and `continuous` above |

### 9.4a The joined role: `joined_numbers`

**Section 9 asserted completeness over all fifteen roles and had no
table for this one.** The role landed with plan P4-D21 and its pairing
facts with P4-D23; eight published facts stood with no disposition at
all, so an institutional reader following the promised exhaustive
inventory found no treatment for the separator, the positional
statistics or the within-cell pairing aggregates. Opened and closed
together on 2026-08-26.

| field | disposition |
|---|---|
| `separator` | EXACT-OBSERVABLE. The twin writes the same mark with the same spacing around it, so a reader splitting on it reads the twin as it reads the table (P4-D24) |
| `n_parts` | EXACT-OBSERVABLE over the SPLIT cells. The `n_joined` cells hold this many numbers each; the `n_unparsed` cells are counted stand-ins and hold none, so a rule stated over every PRESENT cell would be false of them |
| `n_joined`, `n_unparsed` | EXACT-OBSERVABLE. Counts of the cells the reading took and the cells it did not; the unsplit remainder is written as counted stand-ins |
| `parts[]` | STRUCTURAL — the container's own key carries no VALUE obligation, exactly as `length` and `words` do on `free_text`; EACH POSITION CARRIES A QUANTITATIVE BLOCK AND TAKES 9.4's DISPOSITIONS, because the generator hands each position to the same machinery: its endpoints and ladder rungs, its moments, its sign and zero counts and its censuses are disposed exactly as `count` and `continuous` are. The validator checks a position's spellings as well as its endpoints (residual R-P4-43, closed 2026-08-27), and counts a cell into a position only where the cell splits into exactly `n_parts` pieces AND every piece reads as a number — the profiler's own test, so a stand-in the parse line tolerated is never measured into a position it does not belong to |
| `part_min_widths` | EXACT-OBSERVABLE per position — the SMALLEST written width of that position's cells, one number per position and no maximum. A count of characters, never a value. The key names what it holds: there is no published upper width for a position |
| `part_above` | EXACT-OBSERVABLE per PAIR. It is a number of rows, and a row out of it is a cell holding a reading that cannot happen — a diastolic above its systolic — so it is pinned rather than windowed |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE, recounted from the written twin. **These two were disposed NOWHERE until 2026-08-31**: 9.2 sets them "per role group, in 9.3 to 9.7" and this role's table set neither, so a validator filed them under the disposition of another role entirely. They are exact because a FILE can be wrong about them while every other published fact holds: a file keeping each position's multiset and re-pairing the two numbers has the same endpoints, moments, widths, styles, separator, part count and above-count, an agreement inside G12.9's window, and twice the different cells — and it passes with no miss at all if these are not checked. The GENERATOR does not always reach the count, which is residual R-P4-40 and is a limit of the pairing rather than a reason to hold no file to the fact |
| `part_agreements` | APPROXIMATED, on EVERY pair. The window is method G12.9's — two hundredths either side, published there rather than in a plan (residual R-P4-42, closed 2026-08-27) — and both the twin's report and the quality report name the fact and measure it at the same precision the description publishes it at. This row read "per SCORED pair" until landing L7, and the qualifier was load-bearing: the pairing walk moved the last position and no other, so a pair between two earlier positions was not aimed at, was not approximated, and G12.9 did not reach it (residual R-P4-51). The walk moves every position but the first now, so every pair is aimed at and every pair takes the window. Aiming is not reaching: a pair that lands outside the window is a MISS on both pages, with the achieved value beside the published one |

**THE APPROXIMATED FACTS OF THIS ROLE REACH THE TWIN'S REPORT**
(residual R-P4-44, closed 2026-08-27). Until they did, a twin of a
joined column carried a report saying "This twin has no approximated
fact at all" while every position's ladder and the pairing's agreement
were approximated by construction — the same defect found and repaired
one role earlier, on `affixed_number`, and not carried across. Each
record NAMES its position, in the identifier and in the sentence, so
two positions' rungs are told apart; and only facts each position's own
block publishes are compared, so no per-position line appears for a
fact the description publishes for whole cells alone.

**What this role does NOT hold exactly, stated here rather than left to
be discovered.** The count of different CELLS is not always reached:
each position is drawn to its own published ladder, that draw repeats a
value more evenly than the real column did, and fewer different pairs
can be made from values that repeat more. Residual R-P4-40 prices it
and names the description change that would close it.

### 9.4b The compound role: `numbers_with_labels`

**The fifteenth role, landed with residual R-P4-13 on 2026-09-03.** A
column of this role holds a quantity and a vocabulary at once — a lab
result beside `NOT DETECTED`, a dose beside `PRN` — and publishes a
count of each half followed by two sub-blocks. Only the two counts are
this role's own facts. Each sub-block is the block another group
already disposes, read over its own half of the column, and takes that
group's dispositions (plan P4-D33).

| field | disposition |
|---|---|
| `n_numeric_cells`, `n_numeric_out_of_range`, `n_numeric_contradictory`, `n_label_cells` | EXACT-OBSERVABLE. The three populations of the split, pinned rather than windowed: analysis code filters on them, and they sum to `n_present` by construction, so a window on either would let a description speak about part of a column without saying what the rest is — which review item P1-R6-F7 forbids |
| `numbers` | STRUCTURAL — the container's own key carries no VALUE obligation, exactly as `parts[]` does on `joined_numbers` and as `length` and `words` do on `free_text`. IT CARRIES A QUANTITATIVE BLOCK AND TAKES 9.4's DISPOSITIONS, read over the numeric half's cells: its endpoints and ladder rungs, its moments, its sign and zero counts and its censuses are disposed exactly as `count` and `continuous` are |
| `n_distinct`, `n_distinct_folded` | EXACT-OBSERVABLE, recounted from the written twin, using the spellings the description permits — the ordinary case; APPROXIMATED under the two-sided envelope only where even those cannot supply the count. **THE WINDOW IS THE TWO HALVES' WINDOWS ADDED**, because the column's count is the two halves' counts added (NL3) and the halves share no spelling: the numeric half's ends come from G12.8 and the label half's RAW end from G12.7, while its folded end is exact — folding is not a spelling question, so the published levels settle it. A window built by shifting the numeric half's by the label half's PUBLISHED count says the label half is always exact, which it need not be — the numeric group's own bar, because the half a shortfall comes from is a numeric block. The exact comparison is tried first on every file. They are stated HERE because 9.2 sets them "per role group, in 9.3 to 9.7" and a role whose own table sets neither has them filed under whatever group a validator's dispatch falls through to — the defect residual R-P4-62 found on `joined_numbers`, not repeated here |
| `n_numeric_distinct`, `n_numeric_distinct_folded` | EXACT-OBSERVABLE the same way, and APPROXIMATED under the two-sided envelope only where even those cannot supply the count. The NUMERIC HALF's own counts of different written CELLS, and the twin is laid out from them: they are the budget of different SPELLINGS the half may write. The block's `n_distinct_values` cannot serve — it counts different NUMBERS, so `07` and `7` are one — and the column's own counts include the labels. Published because a twin built without them held 56 of a published 113 different cells at every seed |
| `labels` | STRUCTURAL, on the same ground. IT CARRIES A LABEL BLOCK AND TAKES 9.5's DISPOSITIONS, read over the label half's cells: its levels, its held-back counts and its form census are disposed exactly as `categorical` and `long_tail_labels` are. The block is written by this role's own reader rather than by another role's, because neither label role's entry condition is met by a half column — but the FACTS in it are the label group's facts and are held to the label group's classes |

**NL1 and NL2 (section 6.16) are the invariants a reader may rely on**:
the two counts sum to `n_present`, and each sub-block describes its own
half and no other cell. A twin that moved a cell from one half to the
other would keep every interior fact and break both.

**What this role does NOT claim about its own twin.** A column whose
numeric half holds exactly the detection line's worth of different
numbers has a twin that may not be read as this role at all: the
numeric construction reaches about nine tenths of a published count of
different values, so such a half writes fewer than the line and a
re-description returns `free_text` or `long_tail_labels`. Measured over
forty seeds: 31 of 40 keep the role at a floor of one, 13 of 40 at a
floor of twenty-five, and every seed keeps it two or three values above
the line. The twin still HOLDS its numbers — both counts of the split
are met exactly — so what is lost is the re-description and not the
data. Residual R-P4-151 carries it, with the margin that was built for
it and taken out again.

**The distinctness counts were MEASURED before they were pinned**, on
four shapes chosen to break them: readings that almost never repeat, a
numeric half of forty values over two hundred and eighty cells, a
coarse half of twenty-five, and a label half whose markers differ only
in case so the folded count is one below the raw one. Four seeds each.
Every published count was reached exactly. The pinning rests on that
rather than on the reasoning above it.

### 9.5 The label roles: `constant`, `binary`, `categorical`, `long_tail_labels`

| field | disposition |
|---|---|
| `levels` (normalized `label` and `count`) | EXACT-OBSERVABLE |
| `variants`, `variants_withheld` | EXACT-OBSERVABLE |
| `shape_form_cells` (all four label roles) | EXACT-OBSERVABLE, per published level: a person reads the shape off each cell carrying one published label and gets the number back. It is a fact of its own beside `shape_forms` below and NOT a part of it — 7.4.8 states the three reasons no sum holds (residual R-P4-80) |
| `suppressed_levels`, `suppressed_rows` (the pooled total; no size of any one held-back label is published since the owner's ruling of 2026-09-17, plan P4-D201) | EXACT-OBSERVABLE |
| `n_distinct_folded` | EXACT-OBSERVABLE |
| `n_distinct` | EXACT-OBSERVABLE where the published variants and the withheld-variant map supply enough spellings — the ordinary case; APPROXIMATED under the two-sided envelope only where they do not, with the report naming the profile's count beside the twin's. The envelope is G12.7 |
| `level_ceiling` (`categorical` only) | LOADER-ONLY |
| `suppressed_numbers` (all four label roles) | STRUCTURAL — the container's own key carries no VALUE obligation; its membership is the two keys below, and both are disposed in their own right |
| `suppressed_numbers.n_cells` | LOADER-ONLY: the loader reads it to ask `parsing.census_nameable` of the pool against the column's numbers (invariant B4d), and it puts no obligation on the twin — what the twin owes is the aggregate below |
| `suppressed_numbers.mean` | APPROXIMATED under the window G12.12 draws: `taxonomy.pooled_window` either side of the published mean, which is TWO PLACES of the coarsest grid this column's description writes its numbers at, and whole numbers where it publishes none. Method G8.3c places the pool's made-up numbers on the mean, rounds each value onto a place the column writes at, and makes the groups carry each other's arrears, so the twin's own pool lands within the grid's own rounding of the published mean rather than on it. The window was a fifth of the largest magnitude the description stated until this landing, which is a number that has nothing to do with the pool: on a column publishing `990` beside a pooled mean of 944.5 it admitted an error of 198.0, and the defect ledger K-2B-50 names passed inside it. The POPULATION SPREAD that stood beside it is withdrawn by the owner's decision of 2026-09-21 (plan P4-D302), so this row is one obligation and not two, and nothing in this document now asks a file how far apart its held-back numbers lie. Both keys are floor-free in the sense every aggregate over a group is: `parsing.census_nameable` is asked of the pooled count against the column's numeric total before the block speaks at all, and where it answers no the block publishes nought and a null — the same state a column whose held-back levels hold no number publishes (invariant B4d) |
| `shape_forms` (all four label roles) | EXACT-OBSERVABLE against the recount identity 7.9 states: cells recounted at a named form number at least the published count and at most that count plus the pooled `(withheld)` value. It is met by the published spellings, which wear their own forms, then by the made-up spellings of each published label, whose forms are fixed by that level's own `shape_form_cells` (7.4.8), and then by the STAND-INS. The description used to say nothing about which held-back spelling of a label wore that label's form, so the census could fall short of the published count OR run past it; amendment A-P4-47 publishes the fact and closes residual R-P4-34. What can still fall short is the STAND-IN half, where a form's supply is spent or every spelling of it is refused, and the report names it |

The first five rows bind `long_tail_labels` exactly as they bind the
other three label roles: it publishes the four shared label keys under
the shared label invariants, its twin is written by the label
construction — published variants byte-for-byte at their counts,
made-up labels at the sizes read off the pooled total, fold collisions
reproduced — and it carries no `level_ceiling`, so the sixth row
reaches it with nothing to dispose. **What is no longer neutral is the
made-up label's SPELLING**, and the seventh row is where that is
disposed, on all four roles alike: where the census owes a stand-in a
form, the stand-in is written in it (7.9.1).

### 9.6 The calendar and clock roles: `datetime`, `time_of_day`

**`datetime`**

| field | disposition |
|---|---|
| `earliest`, `latest` | EXACT-OBSERVABLE in the representation owner decision 5 fixes. No corner, no exception: the last second of a leap minute is written back unchanged |
| `date_percentiles.min`, `date_percentiles.max` | EXACT-OBSERVABLE, in the same representation and on the same terms. No corner, no exception: they are the same two instants, and D11 makes that a rule the loader enforces rather than a sentence a document may contradict |
| `date_percentiles` interior rungs | APPROXIMATED — the window is G12.4 |
| `resolution`, `time_precision`, `subsecond_digits`, `utc_offsets`, `earliest_utc_offset`, `latest_utc_offset` | EXACT-OBSERVABLE, outside the withheld-offset corner below |
| `datetimes_read_at` | EXACT-OBSERVABLE outside that corner — derived from the offset diversity present in the cells, so it is recomputable from the written twin and must be checked that way. A dispatch assertion cannot detect a twin that reprofiles from `utc` to `local` because one invented rare offset changed the diversity while the pooled offset map and the endpoints still matched |
| `format` | EXACT-OBSERVABLE since the owner reversed decision 5 on 2026-09-15 (landing 2b.6) — the twin is written in the member that read the REAL column, at that member's own field order, delimiter, field widths, year length, month-name case and length, marks and marker cases, so describing the twin again names the same member. While decision 5 stood the twin was written in ISO syntax at the recorded precision, a month-first column's twin reprofiled as `iso-date`, and the field could not be reproduced at all (residual R-P2-7, now retired). ONE CORNER, and it is the same one `resolution_mix` carries: on an `iso-mixed` column NOT wholly at midnight the twin writes every value with a time of day, so its twin reads back as `iso-datetime` and the member is listed rather than checked (residual R-P4-12) |
| `resolution_mix` | REPORT-ONLY — the twin writes every parsed cell at the column's finest recorded precision, exactly as the datetime rule writes every column, and the report names the recorded mix as not reproduced, per column, every run (residual R-P4-12); since landing 2b.3 a column whose `all_at_midnight` is `true` writes its whole-date ranks as whole dates, and the report names nothing |
| `n_unparsed` | EXACT-OBSERVABLE as counted neutral stand-ins, explicitly OUTSIDE the parsed-value representation obligation |
| `n_distinct`, `n_distinct_folded` | APPROXIMATED — the envelope is G12.5, and it is stated there that it need not contain the published count; held to the published count itself where that count lies inside the envelope on a column method G7.3's count pass applies to (`contract.datetime_counts_reachable`), which the pass reaches (plan P4-D192) |
| `date_field_widths`, `month_name_styles`, `quarter_marker_case`, `zulu_case` | EXACT-OBSERVABLE IN THEIR KEY SET for the first two and EXACT for the last two (landing 2b.6, plan P4-D61, the reversal of owner decision 5; plan P4-D134). Every convention the description names must come back on at least a floor's worth of the file's own cells — on the two marker censuses at exactly its published count, since every cell they count over shows the marker — and no convention it does not name beyond the cells the named counts leave over. On the first two each convention is counted on the file's own cells as the producer folds them, and a one-field width or an `either` name is owed on a floor's worth or on every cell of that kind the file holds, whichever is fewer (plan P4-D139). On the first two the COUNTS are not compared, and that is the rule rather than a weaker reading of it: whether a cell can show a convention depends on its own value — a day above the ninth shows no field width, a month of May shows no name length — so how many of a file's cells could carry one is a fact about that file's values, and a twin whose interior instants fall a day either side of the real ones carries a different number of them. C6-25d to C6-25g state each census and D17 to D20 hold them |

`datetime_separators`, `all_at_midnight` and `n_at_midnight` have no
row here: all three were added after the freeze and are EXACT-OBSERVABLE
under plan P4-D39 since landing 2b.3, as `group_separator` is disposed
under P4-D38 with no row in 9.4.

**The four written-form censuses DO have a row**, immediately above,
rather than an exemption like the three named here: they were added
after the freeze too, by the owner's reversal of decision 5 on
2026-09-15, but what they owe a file is unusual enough — the key set
and each key's floor, never the count — that leaving it to a sentence
outside the matrix would be leaving the reader to find it.

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
the whole-second ordinal arithmetic the interior ranks use, so the
published `2024-11-02 04:55:60` is written in the twin as
`2024-11-02T04:55:60` — or with a space or a `t`, where G7.5 allocates
that mark to the rank — and describing the twin again gives back
`2024-11-02 04:55:60` character for character (G7.5). An exact representation exists, and
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
| `clock_percentiles.min`, `clock_percentiles.max` | EXACT-OBSERVABLE — they ARE the two endpoints, which T2 makes a rule the loader enforces rather than a sentence a document may contradict |
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
| `shape_forms` | EXACT-OBSERVABLE against the recount identity 7.9 states. On a column of prose it is `{}` and the row is vacuous, which is the usual case for this role; a free-text column that DID share forms — a code scheme no earlier rule claimed — publishes them and its invented values are written in them |

**`identifier`**

| field | disposition |
|---|---|
| `min_length`, `max_length`, `n_all_digits`, `n_code_alphabet` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length |
| `all_whole_numbers` | EXACT-OBSERVABLE in every case, since owner decision 6 keeps the length. A published length range in which a value that must stand outside the figures can be no whole number at all — one character cannot be both — is a document whose own facts cannot all hold, and generation is refused before any cell is built (G12, `generation-whole-numbers-need-room`). No producer-written profile carries that pair |
| `n_distinct`, `n_distinct_folded`, `n_distinct_by_occurrences` | EXACT-OBSERVABLE outside owner decision 6's infeasible corner; all THREE REPORT-ONLY inside it, with the report naming the achieved value beside the published one |
| `layout_prefixes` | EXACT-OBSERVABLE: every cell a published prefix governs — every present cell under `(column)`, every cell wearing the layout otherwise — opens with it (7.12a, owner ruling of 2026-09-17, item 1). Owed inside owner decision 6's infeasible corner as well as outside it, for the reason `layout_forms` is |
| `layout_forms` | EXACT-OBSERVABLE against the recount identity 7.12 states, on the same terms the form census stands on: a recounted layout numbers at least its published count and at most that count plus the pooled remainder. It is owed INSIDE owner decision 6's infeasible corner as well as outside it, because that corner lowers three DISTINCTNESS facts and says nothing about what a cell LOOKS like — a twin whose record numbers repeat still writes every one of them to a published layout |

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

### 9.8 The all-different obligation, and the four places it cannot bind

Whenever a column publishes `n_distinct == n_present`, its present
values are all different, on every role, in that column's own notion
of equality — because an undeclared key column arrives as free text or
as a numeric role, not as an identifier. **The obligation can bind
only on facts the profile actually publishes.** Where the raw
distinctness of a column was produced by something the disclosure
rules WITHHELD, the twin cannot reproduce it without making facts up,
so raw distinctness is REPORT-ONLY there and the report names the
achieved count beside the published one. Four instances are known and
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
4. **Joined columns.** A column of two numbers in one cell publishes
   `n_distinct == n_present` when every reading it holds is different,
   and the twin does not always reach it: each position is drawn to
   its own ladder and the PAIRING then decides which numbers meet, so
   how many different CELLS result is a consequence of that walk
   rather than a target it aims at. Measured on the generator's own
   every-role description: 240 different readings published, 238 held.
   The generation method has carried this as its fourth instance since
   the joined role landed; this table said three until 2026-08-31 and
   was the stale half of the pair (review item P4-A2-R5-F1).

   **IT IS NOT AN EXCUSE, AND THE TWO COUNTS STAY EXACT-OBSERVABLE**
   (9.4a). A file that misses them is reported by `synthtwin validate`
   and the twin's own report names the shortfall before anybody runs
   the check -- which is the difference between an obligation this
   contract withdraws and one the generator has not yet learned to
   meet. Residual R-P4-71 carries the shortfall and R-P4-40 the
   description change that would close it.

Stating the obligation as one rule with named instances is what stops
a fifth instance arriving undetected -- and the fourth arrived
undetected exactly because no fixture that reaches the rule ever built
the role.

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
> line, and how dates whose day and month are both numbers were read —
> so this file cannot be read back exactly. Please make the
> description again by running 'synthtwin profile' on your table,
> giving it every option you gave the first time: --keep-value,
> --missing-value, --identifier, --code, --measurement,
> --decimal-comma, --smallest-group, --first-row, --day-first,
> --metadata-rows, --sheet, --delimiter and --answers. Every one of
> them changes what the description PUBLISHES about your table, so any
> option you leave out can put something into the new description that
> the old one held back: without the --smallest-group you gave, a
> value that fewer rows share can be named; without the --identifier
> you gave, a column of record numbers is described like any other
> column; without the --code you gave, a column of codes is described
> as measurements, so its values are described by a ladder and by the
> two groups beyond it, and an end a group of rows shares — which is a
> real code — is published; its twin loses any leading zeros; without
> the --measurement you gave, a column of readings written as two
> numbers in one cell, such as a blood pressure, is described as text
> and its twin holds no readings at all; without the --decimal-comma
> you gave, a column whose numbers are written with a comma where the
> decimal point goes is read by the ordinary rules, so a column of
> quantities is described as text and every number in it is lost, or a
> value such as 1,234 is published as one thousand two hundred and
> thirty-four; without the --missing-value you gave, a stand-in is
> read as a real reading, and the stand-in itself can be published as
> the column's smallest value; without the --keep-value you gave, a
> word you had counted as an ordinary value becomes a gap, which can
> change what kind of column synthtwin sees and publish both that word
> and the column's own numbers; without the --first-row you gave, the
> first line of your file is read as the column names and published as
> them; and without the --day-first you gave, a date whose day and
> month are both written as numbers — with slashes, with dots, or with
> a two-figure year — can be read the other way round, which changes
> the dates the description publishes and can leave the column
> described as text instead; without the --metadata-rows you gave, the
> rows under your column names that describe your columns are read as
> records of your table, so their text is counted and described as
> data and every count is two rows out; without the --sheet you gave,
> another sheet of your workbook can be described, and everything the
> new description publishes is then about that sheet's table; without
> the --delimiter you gave, a file that reads equally well with two
> delimiters can be split the other way, which changes every column
> name the description publishes and every value it describes; and
> without the --answers you gave, every answer you wrote in the
> questions file is gone — each of them was a --code, an --identifier,
> a --measurement, a --decimal-comma, a --metadata-rows or a
> --delimiter, so leaving the file out costs whichever of those you
> had given, and this same sentence says what each one costs. If you
> do not hold the table yourself, ask whoever made this description to
> run it again for you. Read the summary page synthtwin writes beside
> the new description before either file goes anywhere, and use the
> description exactly as synthtwin writes it.

**Why it names thirteen options and prices each.** `--metadata-rows`
(plan P4-D81) and `--sheet` (plan P4-D77) each reached the command
line without reaching this clause, and the test deriving the owed set
from the shipped parser was red for both. Landing 2b.17's repair pass
added them beside `--delimiter` (plan P4-D110): leaving out the first
counts two rows of column descriptions as records and describes their
text as data, leaving out the second can describe a different sheet's
table, and leaving out the third can split a file that reads equally
well two ways the other way, which changes every column name. The
`--answers` clause now names every declaration an answer can stand
for, which grew past the three it listed.

**Why it names ten options and prices each.** `--answers` joined them
on 2026-09-10 with the hand-back (amendment A-P4-60), and it is not a
new KIND of option: every answer written into a questions file becomes
one of `--code`, `--identifier` or `--measurement`, so leaving the file
out of a re-run costs exactly what leaving those out costs — which this
sentence already prices, and now says so. It is named because a person
who answered forty columns in a file and then re-runs from a command
line that names none of them has lost all forty and been told nothing.

**Why it names eight options and prices each.** `--measurement` joined
them on 2026-08-26 with the fourteenth role (plan P4-D21): a re-run
without it describes a column of readings as free text, which publishes
no reading at all.

**Why it names seven options and prices each.** `--code` joined them on
2026-08-25 with the declaration itself (plan amendment A-P4-38): a
re-run without it moves a column off the label roles and back onto the
numeric ones, and the new description publishes a ladder of real codes
the old one never named. The message names EVERY
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
that `suppressed_levels` calls for. Every one is finite only if
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
column block of every one of the fifteen roles, and every sentence
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
| `missing_by_source` | the EXACT absent-value SPELLINGS the cells wore, with counts | floor-governed; on a nothing-publishing column confined to members of the published vocabulary (C6-126), which are synthtwin's own words and no table's |
| `sentinel_verdicts` | the candidate as text — a stand-in number, or a calendar placeholder's ISO day — with occurrence count, verdict and reason | `(withheld)` on a nothing-publishing column |
| labels-class blocks (`constant`, `binary`, `categorical`, `long_tail_labels`) | folded label spellings with row counts; each label's exact spellings under `variants`; how many levels were held back and how many rows they cover together (`suppressed_levels`, `suppressed_rows`) and, since the owner's ruling of 2026-09-17 (plan P4-D201), no size of any one of them; and the census of WRITTEN FORMS its cells wore (`shape_forms`), and for each PUBLISHED label how many of its rows wrote it in that label's own form (`shape_form_cells`, 7.4.8) | every named spelling floor-governed; the two held-back facts publish the COUNT and the POOLED ROWS of unnamed groups, floor-free, and never one label on one row, which `n_present` less the published counts reads as a count of one anyway (B4 and B4b; the owner's ruling of 2026-09-17 item 5, plan P4-D231, which counts that cell as missing instead); the form census floor-governed with a `(withheld)` pool, and every key of it built only from `%`, `@` and thirteen named marks -- characters no cell that HAS a form may contain; `shape_form_cells` names no spelling and no form KEY -- the form it counts is the shape of the level's own published `label`, which the reader already holds -- and it is NOT floor-governed, because it is a count of the rows of a label the floor has already admitted. What a reader can take from it is which held-back group of that level was written in the label's shape: presence and shape attached to an unnamed group, which is a widening of the two held-back facts beside it and is the owner's ruling of 2026-08-31 (plan amendment A-P4-47), on the ground that a code's SHAPE identifies nobody while category columns are what analysis code is written against |
| `level_ceiling`, on `categorical` | the effective category cap the run applied, computed from `categorical_ceiling`, `categorical_share`, `categorical_floor` and `n_rows` | publishes nothing the settings block and `n_rows` do not already publish |
| ranges-class blocks (`count`, `continuous`, `datetime`, `time_of_day`, `affixed_number`, `joined_numbers`) | endpoints and the eleven ladder rungs — the two ENDPOINTS are exact values of real cells on every role, and so are the nine interior rungs of a DATE ladder and of a CLOCK ladder; a NUMERIC ladder's nine interior rungs are INTERPOLATED between the order statistics either side and are usually numbers no cell holds (corrected 2026-09-04, measured on columns of 17 to 250 drawn values); moments and shape statistics; sign and zero counts; the style census, the fraction-width census, the padded-field-width census, the WHOLE-NUMBER field-width census, the bins of the range that hold NO value (`empty_bins`), the two values each run of those bins really lies between (`empty_edges`) and the offset map; `resolution_mix`; the separator census `datetime_separators` and the flag `all_at_midnight`; the affix pair; and on `joined_numbers` the separator, the part and split counts, each position's written-width bounds, and the two pairing aggregates | endpoints and rungs FLOOR-FREE under the ranges-class endpoint policy; the style, fraction-width, padded-width, whole-number-width, offset and separator maps floor-governed with a `(withheld)` pool; `all_at_midnight` `true` only where the parsed cells reach the floor; `empty_bins` and `empty_edges` under NO floor at all — the first being the one published fact of this format that names only where nobody is (row 20), the second naming two values a stretch lies between and no group at all (row 21); the affix pair floor-governed by its own detection rule; the separator floor-governed by the role's own detection rule, and the pairing aggregates FLOOR-FREE — they are computed over every row and name no cell |
| nothing-class blocks (`numeric_unrepresentable`, `identifier`, `free_text`) | lengths, word statistics, digit and code-alphabet counts, the whole-number test, the repetition multiset, on `numeric_unrepresentable` the whole-number and sign counts, on `free_text` the census of WRITTEN FORMS its cells wore (`shape_forms`), and on `identifier` the census of LAYOUTS (`layout_forms`, 7.12) and, by the owner's ruling of 2026-09-17, the literal PREFIX every cell of the column or of one named layout opens with (`layout_prefixes`, 7.12a, row 22) | no value, no spelling, no fragment of one but the prefix of row 22 — the form census included, whose every key is built from `%`, `@` and thirteen named marks -- characters no cell that has a form may contain, so a key can carry no letter and no figure of any cell; the multiplicity map publishes SIZES of unnamed groups under no floor, the form census under the floor with a `(withheld)` pool |
| `empty` columns nobody declared | the absent SPELLINGS their cells wore and the two absence counts, exactly as any column that is not nothing-publishing | floor-governed |
| `settings` | the rules the run applied, the floor's own value, how many values each declaration named, and which of THIS package's published words were among them | carries no cell, no column and no count of the table; a person's own spelling never enters |
| `source.header_evidence`, `publication_notes[].note`, `detection_evidence`, `remarks` | sentences of the 58 closed forms: 96 argument positions, of which 83 are whole numbers, 4 package words, 4 nested forms and 5 bound affix strings | the whole numbers are counts the block beside them already publishes, EXCEPT the positions priced at rows 16 and 18 |
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
   `n_rows`, `numeric_styles` with its siblings `group_separator`,
   `negative_form`, `wide_runs`, `decimal_plus`, `negative_notations`,
   `thousands_marks`,
   `fraction_widths`, `pad_widths` and `field_widths`, `n_affixed`, and the four core-class counts
   `n_core_numeric`, `n_core_out_of_range`, `n_core_contradictory`,
   `n_core_not_numeric`, `affix_variants`, `n_core_distinct`,
   `n_core_distinct_folded`, `kurtosis`, `percentiles_between`,
   `n_distinct_values`, `mode` and `mode_count`, and the three shape
   keys `value_histogram`, `empty_bins` and `empty_edges` — each under
   the treatment the same fact has on a plain numeric column, all of
   it reaching columns that were free text. With row 2 this prices all
   forty-one keys the role adds; rows 4, 7, 20 and 21 restate four of
   them at their own floor or disclosure treatment and add nothing to
   the set.

   **EIGHT OF THOSE WERE MISSING FROM THIS ROW** until 2026-09-04 —
   `kurtosis`, `percentiles_between`, `n_distinct_values`, `mode`,
   `mode_count`, `value_histogram`, `empty_bins` and `empty_edges` —
   while the sentence beside them said all thirty-two were priced.
   `tests/test_p4d18_role_topology.py` reads this row against
   `contract.AFFIXED_KEYS` now, so a key added to the role and not to
   this row turns red.
4. **Core endpoints and ladder rungs of affixed columns, and clock
   endpoints and rungs of time-of-day columns. NEW.** Exact values of
   real cells, published floor-free under the ratified ranges-class
   endpoint policy, newly reaching columns that were free text.
5. **Every ROLE-ADDED fact a datetime block publishes**, on every
   column the five calendar members `slashed-iso-date`, `iso-month`,
   `iso-mixed`, `month-first-datetime` and `day-first-datetime` -- and,
   since landing 2b.3, the year-first stamp `slashed-iso-datetime`,
   whose column was free text and now publishes every fact below --, the
   unpadded reading of the slashed month and day fields, the SIX
   members of plan P4-D15 — `textual-day-first-date`,
   `textual-month-first-date`, `dotted-month-first-date`,
   `dotted-day-first-date`, `two-digit-month-first-date` and
   `two-digit-day-first-date` — or the TWO of residual R-P4-4,
   `dotted-two-digit-month-first-date` and
   `dotted-two-digit-day-first-date`, newly claim.
   **NEW for such a column.** The universal keys it newly fills are
   priced at row 15, not here. The role-added set is fifteen keys, of
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
   - **One SPELLING census that is floor-GOVERNED:**
     `datetime_separators`, under D12's floor with a `(withheld)` pool.
     Its KEYS are this package's three names for the mark a moment
     writes between its day and its clock, never cell text; its VALUES
     are how many parsed cells wrote each named mark. It names
     spellings, not values. Since plan P4-D220 neither map names a count
     below two at any floor, so no name stands for one row's spelling or
     offset, and since plan P4-D222 a name below the line is counted into
     the commonest, so no pool stands beside a named one.
   - **One statement about every parsed cell at once, floor-GATED:**
     `all_at_midnight`, whether every parsed cell of a `local` datetime
     column named exactly midnight. It names no value, and it is `true`
     only where the parsed cells reach the floor. Where it is `true` it
     tells a reader the time of day of every parsed row, which the
     endpoints and the ladder already show for eleven of them.
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
     same fifteen while it STOPS publishing that column's label
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
    column**, via the array `suppressed_level_counts`, WITHDRAWN by the
    owner's ruling of 2026-09-17 (item 2, option A; plan P4-D201), which
    publishes only their pooled total. The row as it stood: **NEW, and narrower than
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
    5, the six P4-D15 members named beside them, the unpadded reading,
    the clock rule, the affix rule or the long-tail rule — newly
    publishes four kinds of fact about its ABSENT cells:
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
    twin WRITES those spellings at their published counts — **a
    spelling a JUDGED PASS put there included**, one reading as a
    stand-in number or as a calendar placeholder (C6-116), and section
    9's row says the same in its own words. This is the class of fact row 12's
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
18a. **The census of written forms. NEW.** How many present cells of
    a label-class or `free_text` column wore each WRITTEN FORM — the
    cell with every figure replaced by `%`, every letter by `@`, and
    every other character required to be one of thirteen marks this
    contract names — under the floor, with a `(withheld)` pool for the
    forms too few cells shared.

    **What it publishes is a count of cells per SHAPE and nothing
    else**, and the key grammar is what makes that true rather than
    argued: a key is `%`, `@` and those thirteen marks or the loader
    refuses the document, so no letter and no figure of any cell can
    stand in one. A cell holding a character outside that list — a
    space among them — has no form, so THIS CENSUS does not count it,
    which is what keeps a sentence's word lengths and punctuation out
    of the census and leaves a column of prose publishing `{}`. What
    such a cell contributes to the block's other keys is unchanged:
    its length, its words and its repetition are counted exactly as
    any other cell's are.

    **The floor governs a named form as it governs a level.** Its
    price is therefore the price of every floor-governed count: a
    published form asserts that at least `small_cell_floor` cells of
    the column were written that way. On `free_text` this is the FIRST
    fact of the block that is about the values' writing rather than
    their size, and it is what makes that role's twin usable for a
    column of codes (plan P4-D18, amendment A-P4-36).

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
      the treatment `n_distinct_by_occurrences` already has;
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

19. **The census of whole-number field widths. NEW.** How many cells
    of a numeric column were written as a whole number at each width
    (`field_widths`, 7.10), under the floor with a `(withheld)` pool.
    Its keys are counts of characters and its values counts of cells;
    no figure of any cell, and no spelling, appears in it.

    **AND WHAT IT DISCLOSES IS MORE THAN "A COUNT OF CHARACTERS", which
    is said here plainly because the short description is the one a
    reader would otherwise carry away.** On the PADDED cells a width is
    a fact about the writing alone — `000123` and `123` are the same
    number — and `pad_widths` at row 12 already prices that. On the
    UNPADDED cells a width is exactly the value's decimal order of
    magnitude, so `field_widths {"3": 103}` beside `pad_widths
    {"3": 127}` says that 103 of this column's cells held a value
    between 100 and 999 and that 127 held one below 100. That is a
    BINNED count of the column's own magnitudes at decade resolution,
    computed over real cells, and it is floor-governed exactly as every
    other census here is: a decade fewer than `small_cell_floor` cells
    share is pooled and never named.

    **What it does not publish**, so that the bound is as clear as the
    cost: no value, no endpoint, no rung, and nothing about WHICH cells
    fall in a decade. Row 3's ladder already publishes values of real
    cells, floor-free — its two endpoints on every role and, on the
    date and clock roles, its interior rungs too (corrected
    2026-09-04: a NUMERIC ladder's interior rungs are interpolated and
    are usually held by no cell, while a date ladder and a clock
    ladder place every rung on a real value, measured on columns of 17
    to 250 drawn values); this row publishes
    no value at all and is under the floor. The owner ruled it in on
    2026-08-26 (close-plan decision 2, plan decision P4-D30) on the
    ground that a fixed-width code column whose twin comes back at two
    lengths is a twin that breaks a length check, a fixed-width slice
    and a join, and that nothing published said how long a code was.

20. **The bins of a numeric range that hold NO value. NEW.** Which of
    the fixed bins between a numeric block's published `min` and `max`
    hold none of the values the statistics used (`empty_bins`, 7.11),
    ascending. Read over the CORES on `affixed_number`, per position
    on `joined_numbers`, and over the numeric half on
    `numbers_with_labels`.

    **IT IS THE ONE ROW OF THIS SECTION THE FLOOR DOES NOT REACH, and
    that is the whole of what a reader has to weigh here.** Every other
    census in this document is floor-governed because a group too small
    to name must not be named. This list names no group: it names the
    stretches where there is NOBODY, and there is no group smaller than
    nobody. The owner ruled on exactly that question on 2026-08-31 —
    shown a two-cluster column whose twin put cells in the empty middle,
    and asked whether a bin holding ZERO may be published while the bins
    holding one to one-below-the-floor stay hidden — and ruled that it
    may, on their standing ground that a fact naming nobody is
    publishable.

    **What it publishes, exactly.** The bins are a division of two ends
    row 3 already publishes, so no edge here is one a reader could not
    already compute; what is added is the sentence "no cell of the real
    column lies between these two edges". No value, no count, no cell,
    and nothing about any row. **What it does NOT publish** is the
    complement: a bin holding one value and a bin holding
    one-below-the-floor values are named by nothing, here or in row 3's
    census, and stay exactly as hidden as they were.

    **Why it is not simply read off `value_histogram`.** That census is
    all or nothing, so at any smallest group size above one it is absent
    — and it is absent FIRST on the columns whose shape matters most,
    because a column with an empty middle has thin bins at the edges of
    its clusters. Measured on a 300-row two-cluster column: thirteen
    bins named at a floor of one, none at two, three, five or eleven,
    and the same nineteen empty bins named at every one of them.

21. **The two values each of those stretches really lies between.
    NEW.** For each run of consecutive empty bins, the largest value
    below it and the smallest above it (`empty_edges`, 7.11a). Read
    over the CORES on `affixed_number`, per position on
    `joined_numbers`, and over the NUMERIC HALF on
    `numbers_with_labels` — the same three places row 20's bins are
    read, and every one of them a place a reader of a description
    meets these values.

    **This row publishes VALUES, and row 20 does not** — which is why
    it is weighed separately rather than folded into it. Each edge is
    the value of a real cell.

    **The weighing, stated as a ceiling rather than as a comparison.**
    An edge says that some row holds 26.6 and some row holds 72.7 —
    and nothing about which rows, how many, or what those rows hold
    anywhere else, which is the ground the owner's rulings of
    2026-08-31 and 2026-09-03 stand on. A reach is divided into
    thirty-two bins whose first and last always hold the two
    endpoints, so this row names **at most fifteen pairs and thirty
    exact values in one numeric block**, and they can all be
    different. On a dense column there is usually no run at all and so
    no value here; on a SPARSE column the ceiling is reached — a
    32-row column occupying bins 0, 2, 4 … 28 with two values each and
    bins 30 and 31 with one each publishes fifteen pairs naming thirty
    distinct values, and with row 3's two endpoints beside them the
    description names EVERY value that column holds.
    A person describing a small, widely spread numeric column should
    weigh this row before sharing the description, and the smallest
    group size does not reduce it.

    **THIS WAS FIRST WRITTEN AS "two more beside eleven" AND THAT WAS
    WRONG**, corrected on 2026-09-04. Row 3's ladder puts TWO exact
    values into a block, not eleven: the endpoints are order
    statistics and the nine rungs between them are interpolated
    between the order statistics either side. Measured on six columns
    of 17 to 250 drawn values, between three and nine of the nine
    interior rungs were held by no cell. So this row is a larger
    addition than the sentence it replaced claimed, and it is the
    ceiling above rather than the comparison that a reader should
    weigh.

    **Why the bins alone were not enough.** A bin is a thirty-second of
    the block's reach, so the bins a column leaves empty sit strictly
    inside the stretch it really leaves empty: a twin repairing a cell
    to the edge of the nearest occupied BIN put it back inside the
    source's own gap. Measured on the three two-cluster witnesses at
    forty seeds each: the furthest such cell fell from 15.7–23.0 units
    from a real value to 1.3. The owner was shown that measurement and
    ruled "follow you recommendation" on 2026-09-04.

22. **The literal prefix of a declared record number. NEW, by the
    owner's ruling of 2026-09-17, item 1** (7.12a, plan P4-D202). TEXT
    OF THE TABLE on a nothing-class block: the opening every present
    cell of a declared identifier shares — `REC`, `P`, `ABC-` — or, as
    this version reads the ruling and puts to the owner, the opening
    every cell of one named layout shares. It is a fragment of every
    value it governs and of no one value: it holds no figure, a figure
    or letter of every value stands after it, it stops before a run of
    letters goes on, and it is published only where the cells opening
    with it reach the floor and the present cells that do not are none
    or reach it too (C6-140). What it costs is the literal itself — a
    local numbering scheme's letters, a site's own code — on the page
    wherever a whole declared column, or a whole layout of one, wears it.

### 12.4 The files, and the handling rule

Every file a full run leaves behind — the description, the
plain-language summary beside it, the questions file, the twin, the
twin's report and the quality report — carries real-derived published
facts, and each is handled under the institution's rules for
real-derived material. synthtwin claims no formal privacy guarantee.
Three of the six are
counted because a narrower reading once left them out, and each is
named with the reason it belongs: the questions file is written on
every `profile` run, and it names columns of the real table beside the
shapes measured from their cells; the quality report `synthtwin
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
is closed at six. Accounting parentheses are excluded from twin output
by decision 8; a thousands separator is written only where
`group_separator` publishes one (plan P4-D38).

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
roles" while listing ten, and the count is now fourteen. The reason it
is fourteen is not that a shipped tuple has fourteen entries — no
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
twenty formats rather than six and is still `D1`. This is not a style
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
| `joined_numbers` | `joined_numbers` | `ok` |
| `numbers_with_labels` | `numbers_with_labels` | `ok` |

Four roles answer something other than their own name — `empty`,
`numeric_unrepresentable`, `identifier` and `free_text` — and the other
ten name their own shape.

**`quality_state` — 3:** `ok`, `empty`, `unrepresentable`.
**`structural_role` — 2:** `data`, `identifier`.

**Publication buckets — 4** (6.10). Every role is in exactly one.

| bucket | roles | count |
|---|---|---|
| labels | `constant`, `binary`, `categorical`, `long_tail_labels` | 4 |
| ranges | `count`, `continuous`, `datetime`, `time_of_day`, `affixed_number`, `joined_numbers` | 6 |
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

**Forbidden-key matrix — 87 rows over 15 role columns**, 166 marked
cells, defined in 6.11. Not reproduced here; a matrix is not a list.

### 14.2 Document and block key sets

**Top-level keys — 9** (4.1): `columns`, `created_with`, `n_columns`,
`n_rows`, `profile_version`, `publication_notes`, `relationships`,
`settings`, `source`.
**`profile_version` — 1 permitted value:** the integer `6`.

**`source` keys — 7** (4.3): `dialect`, `encoding`,
`header_by_convention`, `header_evidence`, `header_source`,
`used_fallback_encoding`, `workbook`.
**`source.encoding` — 5:** `utf-8-sig`, `latin-1`, `cp1252`, `utf-16-le`,
`utf-16-be`.
**`source.dialect` keys — 22** (4.3a).
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

**`settings` keys — 22** (4.4), in the ascending code-point order every
object of a canonical document takes: `categorical_ceiling`,
`categorical_floor`, `categorical_share`, `day_first`,
`declaration_matching`, `declaration_publication`,
`declared_missing_values`, `forced_codes`, `forced_decimal_commas`,
`forced_delimiter`, `forced_identifiers`,
`forced_measurements`, `forced_metadata_rows`,
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

**`format` — 20** (6.6.2), each with the `resolution` it requires:

| `format` | `resolution` |
|---|---|
| `iso-date` | `date` |
| `month-first-date` | `date` |
| `day-first-date` | `date` |
| `compact-date` | `date` |
| `slashed-iso-date` | `date` |
| `textual-day-first-date` | `date` |
| `textual-month-first-date` | `date` |
| `dotted-month-first-date` | `date` |
| `dotted-day-first-date` | `date` |
| `two-digit-month-first-date` | `date` |
| `two-digit-day-first-date` | `date` |
| `dotted-two-digit-month-first-date` | `date` |
| `dotted-two-digit-day-first-date` | `date` |
| `iso-month` | `month` |
| `year-quarter` | `quarter` |
| `iso-datetime` | `datetime` |
| `iso-mixed` | `datetime` |
| `month-first-datetime` | `datetime` |
| `day-first-datetime` | `datetime` |
| `slashed-iso-datetime` | `datetime` |

**`resolution` — 4:** `date`, `datetime`, `quarter`, `month`.
**`time_precision` — 6:** `subsecond`, `second`, `minute`, `date`,
`quarter`, `month`.
**`datetimes_read_at` — 2:** `local`, `utc`.
**`clock_form` — 2:** `hh-mm`, `hh-mm-ss`.
**`resolution_mix` keys** are `format` members: on a single-format
column exactly the column's own member; on an `iso-mixed` column
exactly `iso-date` and `iso-datetime`. No other key set conforms.
**`datetime_separators` keys — 3**, plus the pooled key (6.6.2, D12):
`lower_t`, `space`, `upper_t`; and `(withheld)`.
**`all_at_midnight`** is a boolean, and **`n_at_midnight`** a count of
two or more or else `null` (landing 2b.3; the absent state and the floor
of two, landing 2b.6), on the `datetime` block alone.

**The four written-form vocabularies — 8, 36, 2 and 2**, with no pooled
key (6.6.2 C6-25d to C6-25g, D17 to D20; landing 2b.6, and plans P4-D131
to P4-D133):

- **`date_field_widths` keys — 8:** `padded`, `unpadded`,
  `first-padded`, `second-padded`, `first-field-padded`,
  `first-field-unpadded`, `second-field-padded`, `second-field-unpadded`.
  On a textual member only the first two.
- **`month_name_styles` keys — 36:** every
  `<case>-<length>-<mark>-<comma>` over `upper`, `title`, `lower` ×
  `abbreviated`, `full`, `either` × `space`, `hyphen` × `comma`,
  `no-comma`. On `textual-day-first-date` only the eighteen ending
  `-no-comma`.
- **`quarter_marker_case` keys — 2:** `upper`, `lower`.
- **`zulu_case` keys — 2:** `upper`, `lower`.

### 14.7 Numeric spelling

**Numeric styles — 6**, plus the pooled key (7.5): `plain`,
`leading_zero`, `leading_plus`, `decimal`, `exponent_lower`,
`exponent_upper`; and `(withheld)`.

**`fraction_widths` keys** are the decimal spelling of a non-negative
integer — no sign, no leading zero unless the width is itself zero, no
space, no other character (`0`, `1`, `2`, `10`) — plus the pooled key
`(withheld)`, which is the only non-numeric key permitted.

**`pad_widths` keys** are written by the same grammar and read the same
way, with one difference: the width is at least TWO (`2`, `3`, `10`),
a padded cell writing at least one zero in front of at least one figure
(C6-29b). `(withheld)` is again the only non-numeric key permitted.

**`field_widths` keys** are written by that same grammar, with the
width at least ONE (`1`, `2`, `10`), a cell written as a whole number
writing at least one figure (C6-29c). `(withheld)` is again the only
non-numeric key permitted.

### 14.8 The note grammar — 58 forms

Defined in 4.5.1, which is the authority on every rendering and every
argument. 96 argument positions: 83 whole numbers, 4 package words, 4
nested forms, 5 bound affix strings.

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
| NG42 | `remark_two_figure_years_are_read_at_a_pivot` | 0 |
| NG43 | `remark_padded_numbers_may_be_codes` | 1 |
| NG44 | `remark_commas_read_as_thousands` | 2 |
| NG45 | `evidence_long_tail_of_labels` | 5 |
| NG46 | `evidence_clock_times` | 3 |
| NG47 | `evidence_numbers_joined_in_one_cell` | 3 |
| NG48 | `evidence_numbers_wearing_one_affix` | 3 |
| NG49 | `histogram_publishes_no_shape` | 0 |
| NG50 | `remark_an_address_is_not_a_quantity` | 0 |
| NG51 | `remark_whole_numbers_could_be_times` | 7 |
| NG52 | `evidence_numbers_with_labels` | 4 |
| NG53 | `evidence_numbers_with_a_few_labels` | 4 |
| NG54 | `remark_two_readings_both_fit` | 1 |
| NG55 | `remark_a_letter_against_the_digits` | 1 |
| NG56 | `remark_brackets_around_the_affix` | 0 |
| NG57 | `remark_a_minus_after_the_figures` | 0 |
| NG58 | `header_names_could_not_be_told` | 0 |

**The package-word vocabulary — 24**, the whole of the second argument
class (4.5.1): the twenty `format` members of 14.6, plus `day-first`
and `month-first`, the two reading names the day-and-month remark
needs, plus `hours_and_minutes` and `hours_minutes_and_seconds`, the
two clock words NF46 names a form by. **The count read nineteen and
omitted the two clock words until 2026-08-26**, while the shipped
producer had carried twenty-one since the clock role landed -- so a
producer written to this document would have refused the clock
evidence sentence the tool writes. The two clock words are NOT
`format` members and never appear in a `format` key.
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

**Where `(withheld)` appears — 10 places, and three keys where it is never written.**

| place | meaning |
|---|---|
| `missing_by_class` | the pooled count of absent-value CLASSES whose own counts fell below the floor |
| `sentinel_verdicts[].candidate` | the column is a nothing-publishing column, so no value of the table appears anywhere in its block |
| `utc_offsets` | the count of every parsed cell, where no OFFSET was carried by enough rows to name (plans P4-D220 and P4-D222) |
| `datetime_separators` | the count of every parsed cell that writes a clock, where no MARK between day and clock was written by enough rows to name (plans P4-D220 and P4-D222) |
| `earliest_utc_offset`, `latest_utc_offset` | the map is withholding every offset (plan P4-D222) |
| `numeric_styles` | the count of every numeric cell, where no spelling STYLE was used by enough rows to name (plan P4-D222) |
| `fraction_widths` | the count of every `decimal`-styled cell, where no fraction WIDTH was used by enough rows to name or the widths named cannot write a published end (plan P4-D222) |
| `pad_widths` | the count of every padded cell, where no FIELD WIDTH was used by enough of them to name (plan P4-D222) |
| `field_widths` | the count of every whole-written cell, where no FIELD WIDTH, or no width of the unpadded cells, was used by enough rows to name (plan P4-D222) |
| `value_histogram` | never written: a column that cannot publish every bin publishes no histogram at all, because a pooled remainder does not say which bins its values are in and the census is read by rank |
| `empty_bins` | never written, and never needed: this list names only the bins holding NOBODY, and there is no group smaller than nobody for the floor to protect. It is the one row of this table whose fact is published in full at every floor |
| `empty_edges` | never written either, and for the same reason plus one: a pair names two VALUES and not a group, and both are values the ladder already publishes the class of. Published in full at every floor |
| `shape_forms` | the pooled count of cells whose WRITTEN FORM was worn by too few rows to name |

One token, one meaning: a group too small to name, counted rather than
named. It is never a value, and it is never a key a generator has to
invert. Every list it appears in draws its other keys from a fixed
first-party vocabulary — class words, offset texts, separator names, style names, width
digits, and the form alphabet `%`, `@` and thirteen marks — so there
is no field of this format in which a value of
somebody's table and one of synthtwin's own words can land in the same
slot. A field added later that breaks that property breaks this
sentence.

**Where `(none)` appears — 2 places:** as a key of `utc_offsets`, and
as the value of `earliest_utc_offset` or `latest_utc_offset`. It means
the cell carried no offset at all.

**`(blank)`** is a key of `missing_by_class` and of nothing else.
`resolution_mix` carries no reserved key: it is floor-free and never
withholds. `datetime_separators`, the datetime block's other map, does
carry `(withheld)`.

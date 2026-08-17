# Profile contract, version 5 — the normative specification

**Status: SHIPPED, and this document was written before any of it,
which is this repository's standing process.** `synthtwin profile`
writes version 5, the loader reads version 5, and an older description
is refused with the message section 10.2 fixes word for word. Every
rule below describes the file the tree produces today.

**The status paragraph this replaces, and why replacing it is the
point** (plan amendment A-P3-30). Until the implementation stages
landed, this document opened by saying what the shipped producer and
loader did instead, and by forbidding anybody to write about version 5
anywhere as though it were built. Both of those sentences became false
on the commit that landed the producer and the loader, and they stayed
here for a stage afterwards while `CHANGELOG.md`, `SECURITY.md` and the
plan all correctly described version 5 as shipped — so the one document
that GOVERNS the format was the one document still denying it. That is
the stale-claim defect this project has now found in five separate
rounds, and `tests/test_claim_inventory.py` walks this sentence from
here on: it derives the shipped wire version from the product and turns
the suite red on any surface that names another one as what synthtwin
writes or reads.

**Authority.** This document carries out the owner's ruling of
2026-08-17, recorded as amendment A-P3-27 of `docs/plans/phase-3-product.md`.
That ruling chose to extend the format now, at version `0.1.0.dev0`,
with no release, no tags and no users, rather than after a release when
the same change costs other people a migration. The plan governs on
conflict, exactly as it does for version 4.

**What this document is for.** A strict loader and a producer must both
be writable from this text together with the version 4 contract, without
reading any source and without guessing. Every key that version 5 adds,
removes or changes meaning for is named here with its type, when it is
present, what it means, its disposition, and every invariant that binds
it.

**What this document is not.** It does not say how the twin's values are
computed — that is `docs/spec/generation-method-v1.md` — and it does not
say what `synthtwin validate` checks — that is
`docs/spec/validation-method-v1.md`. Neither of those two documents is
amended here; each is amended at its own stage, against this text.

---

## 1. What changed from version 4, and why

**Read this section first. It is the whole story in plain words, and
nothing below it is a surprise if this section is understood.**

A description file has to answer a question nobody asked it when it was
designed: **how did a cell of the table become "no value"?** A cell can
be blank. It can hold one of synthtwin's own words for nothing, like
`NA`. It can hold a stand-in number like `-999`. Or the person running
the tool can have named a word of their own with `--missing-value`, or
rescued one of synthtwin's words with `--keep-value`, so that it means
the opposite of what it usually means. Call the answer **the reading
rule**.

`synthtwin generate` never needed the reading rule: the twin writes
every absent cell as an empty field, so there is nothing to read back.
`synthtwin validate` does need it. It describes the file it is pointed
at using the profiler's own machinery and compares the two descriptions
fact by fact — and to describe the file *the same way*, it has to read
that file the same way. It rebuilds the reading rule from the
description, because the description is all it has.

**A version 4 description does not carry the reading rule**, and the
consequence was not a missing feature but a wrong answer: a table
checked against its own genuine description came back with obligations
reported as missed, with numbers printed beside them, when the file was
its own description's perfect match. Amendment A-P3-26 stopped the wrong
answer by moving those obligations to NOT CHECKABLE with a printed
reason. It did not put the information back. Version 5 puts as much of
it back as can be put back safely.

There are five ways the reading rule was lost. Version 5 closes three of
them, and it closes them by copying, field for field, what the format
already does correctly one key away:

1. **The spelling is stored exactly, and escaped only when it is
   printed.** A column's `missing_by_source` records the spellings that
   made cells absent — but version 4 rewrote each spelling into a
   printable form *before storing it*, so a word holding an invisible
   character became indistinguishable from a word holding the printable
   characters that stand for it. That rewriting is a rule about not
   scrambling somebody's terminal. It is a presentation rule doing a
   protection rule's work. The neighbouring field `variants` already
   stores its keys exactly and escapes them only at the moment of
   printing, for the stated reason that something has to read them back
   (version 4 section 7.4.2 and decision 13.5). Section 4 below applies
   the same rule to `missing_by_source`.

2. **The pooled count and the blank count leave the map.** Version 4
   put two of synthtwin's own words — `(withheld)` and `(blank)` — into
   the same list as the person's spellings, with nothing to tell them
   apart. A table whose cells literally read `(withheld)` published the
   key the pool wears, so two descriptions needing opposite readings
   came out byte for byte alike. The format already knows the answer
   here too: `variants_withheld` keeps the pooled remainder of the
   variants in a field of its own, so `variants`' key space belongs to
   the table alone. Section 5 below gives `missing_by_source` the same
   treatment, with a count of its own for each of the two words.

3. **Which of synthtwin's own words were named is recorded.** The
   settings block records a declaration as a count and never as text,
   because a spelling a person types is compared against every cell of
   every column and could be data. That rule is right, and version 5
   does not withdraw it. But part of what a person can name is not their
   text at all: it is synthtwin's own vocabulary — the ten spellings the
   tool treats as "no value" and the three stand-in numbers — published
   in this contract, the same in every installation, and identical
   whatever table it is run on. Section 6 below records which members of
   that closed list a declaration named, and nothing else. What a person
   typed that is *not* on that list stays a count, exactly as in
   version 4.

**Two ways stay lost, and section 7 says so plainly.**

- On a column that publishes no value of the table at all — free text,
  record numbers, and columns whose numbers are unrepresentable — the
  source list is emptied on purpose. Publishing the marker word there
  would publish text out of a column that exists to publish none. **No
  change to this format can close that**, and version 5 does not
  pretend to.
- A spelling shared by fewer than `small_cell_floor` cells is pooled,
  unnamed, exactly as version 4 pooled it. Naming it would name a group
  the floor exists to keep too large to point at.

Both remain covered by amendment A-P3-26: where the description shows
the reading rule cannot be rebuilt, the affected obligations are listed
as not checkable with a printed reason, rather than reported as missed.

**What version 5 does not touch.** No cell of any twin changes: no
generation rule reads any field this document moves, and the twin still
writes every absent cell as an empty field. No statistic, no level, no
variant, no percentile, no style count, no date fact, no role and no
axis changes. The relationship manifest stays eight nulls.

---

## 2. Scope, authority, and how version 4 is carried

### 2.1 What this document governs

2.1.1 This contract governs one artifact: the machine-readable profile
document, written by `synthtwin profile` as `<stem>-profile.json`. It
does not govern the plain-language summary beside it, the twin CSV, the
generation report, or the quality report.

2.1.2 Where this contract and `docs/plans/phase-3-product.md` disagree
on a fact the plan decided, the plan governs and this document is
defective.

### 2.2 Version 4 is carried by reference, and this is the rule

**2.2.1 Version 5 is version 4 with the changes in sections 4, 5, 6, 8,
9 and 10, and nothing else.** Every rule of
`docs/spec/profile-contract-v4.md` that this document does not name is a
rule of version 5, at its version 4 wording, with its version 4
identifier. That includes, without the list being exhaustive: the
encoding and canonical serialization rules of its section 3 and the
number grammar of its 3.2.1; the top-level structure of its 4.1 to 4.6;
the column block of its 5.1 to 5.6 except where section 5 below amends
it; every role of its section 6 and the forbidden-key matrix of its
6.11; the five version 4 additions of its section 7; the invariant list
of its section 8 except where section 9 below amends it; the disposition
matrix of its section 9 except where section 11 below amends it; the
loader of its section 10 except where section 10 below amends it; the
carried condition of its section 11; and the enumerations of its
section 14 except where section 14 below amends them.

**2.2.2 Why by reference and not by copy.** A copy of two thousand eight
hundred lines is a second place for a rule to live, and this repository
has a four-entry history of an obligation being restored in one place
and weakened in the paragraph after it. A copy would also give the
document two disposition matrices, one of which no guard reads. The
diff a reviewer has to read is therefore the change itself, which is
what makes it reviewable.

**2.2.3 The rule that keeps version 4 a record.**
`docs/spec/profile-contract-v4.md` stays in the tree as the record of
what version 4 meant, AND it is the referenced text of every version 5
rule this document does not restate. Those two roles are compatible
under one rule, which is normative:

> **The version 4 document is not edited to change what version 5
> requires.** A change to any rule version 5 inherits is written into
> THIS document as a numbered clause that names the version 4 rule it
> supersedes. A change made by editing the version 4 text instead is a
> defect, whatever the change says, because it rewrites the record of a
> version the tree no longer produces.

Editorial repairs to the version 4 document — a typo, a broken
reference — are not changes to what version 5 requires and are outside
this rule. Every one of them still moves a digest in
`tests/disposition_seal.py` and is therefore visible.

**2.2.4 Precedence.** Where this document and the version 4 document
state different things about the same key, this document governs for a
version 5 profile, and the version 4 document governs for a version 4
profile. No profile is ever both.

### 2.3 Terms this document adds

The vocabulary of version 4 section 2.3 is carried unchanged. Four terms
are used here that version 4 does not define in one place.

| term | meaning in this document |
|---|---|
| **the reading rule** | how each cell's raw text became either a value or no value: the blanks, synthtwin's own built-in words, the stand-in numbers, the words named with `--missing-value`, and the words rescued with `--keep-value` |
| **the display boundary** | the rewriting that turns a character which instructs a display — a control code, a bidirectional override, a zero-width mark — into a printable form that shows itself, so that printing text cannot scramble somebody's terminal |
| **the published vocabulary** | the closed list in section 14.1: the ten spellings synthtwin reads as "no value" and the three stand-in numbers it judges. It is synthtwin's own, it is the same in every installation, and it contains no text from any table |
| **a nothing-publishing column** | a column whose publication class permits no value of the table anywhere in its block: version 4 section 6.10 — `role` in `numeric_unrepresentable`, `identifier`, `free_text`, or `structural_role == "identifier"` |

---

## 3. The reading rule, and what the producer must write for each way

**This section is the requirement the rest of the document serves.** It
is stated first so that every clause below can be read against the job
it does.

### 3.1 The five ways a cell becomes absent, and the one way a cell is rescued

The producer has five ways to make a cell absent and no sixth. Two of
them are the person's declaration, applied at two different moments by
two different matching rules, which is why they are counted as two: a
declared value that reads as a number is matched by the number it
denotes, and a declared value that does not is matched by its trimmed,
case-folded spelling. This is what `settings.declaration_matching`'s
one permitted value, `exact_number_when_it_reads_as_one_else_spelling`,
already says.

| # | the way | class word in `missing_by_class` |
|---|---|---|
| 1 | the cell held nothing, or nothing but space | `(blank)` |
| 2 | the cell's spelling is one of synthtwin's built-in words for "no value" | `(text-code)` |
| 3 | the cell held a stand-in number, and the column's own rule judged that stand-in to mean "no value" | `(numeric-sentinel)` |
| 4 | the person named the cell's spelling with `--missing-value` | `(declared-missing)` |
| 5 | the person named the cell's NUMBER with `--missing-value` | `(declared-missing)` |

`(withheld)`, the fifth key of `missing_by_class`, is not a sixth way. It
is what the floor does to any of the five when the class it belongs to
covers fewer rows than the floor.

And one way a cell that would have been absent is a value instead:

| # | the way | where it shows |
|---|---|---|
| 6 | the person rescued the cell's spelling or its number with `--keep-value` | nowhere in a version 4 description, except where the rescued value happens to be published as a level, a variant or a sentinel verdict |

### 3.2 What a version 5 producer writes for each way

| # | what is written, so the way is reconstructible | what is NOT written |
|---|---|---|
| 1 | `n_missing_blank`, when at least `small_cell_floor` cells of the column were blank; otherwise those cells are counted in `n_missing_withheld` | nothing: a blank cell has no spelling to write |
| 2 | the cell's exact spelling as a key of `missing_by_source`, when at least the floor share it; and, when the same word was ALSO named with `--missing-value`, its membership in `settings.declared_missing_values.built_in_texts`, which is what separates way 2 from way 4 for that word | the spelling, when fewer than the floor share it |
| 3 | the cell's exact spelling as a key of `missing_by_source`, when at least the floor share it; and the candidate's own entry in `sentinel_verdicts`, carrying the number, the verdict, the reason and the occurrences | the spelling, when fewer than the floor share it; and, on a nothing-publishing column, the candidate, which reads `(withheld)` |
| 4 | the cell's exact spelling as a key of `missing_by_source`, when at least the floor share it; and, when the declared value is a member of the published vocabulary, its membership in `settings.declared_missing_values.built_in_texts` | the declared spelling itself, whenever it is not a member of the published vocabulary and no cell wearing it reached the floor |
| 5 | the cell's exact spelling as a key of `missing_by_source`, when at least the floor share it; and, when the declared number is one of the three stand-ins, its membership in `settings.declared_missing_values.built_in_numbers` | the declared number itself, whenever it is not one of the three stand-ins and no cell wearing it reached the floor |
| 6 | every member of the published vocabulary the person rescued, in `settings.kept_values.built_in_texts` and `settings.kept_values.built_in_numbers` — which section 6.4 proves is the WHOLE of what a rescue can change | the rescued values that are not members of the published vocabulary, which section 6.4 proves change no cell's reading |

### 3.3 What a consumer may conclude, and what it may not

**3.3.1 The derivation is stated, so that no consumer has to invent
one.** Given a version 5 profile and nothing else, a consumer that has
to read a CSV file the way the profile's own run read it derives:

- the set of blank spellings: every cell that is empty or holds nothing
  but space, which needs nothing from the document;
- the built-in words and the three stand-in numbers, which are section
  14.1 and are the same in every installation;
- the values rescued with `--keep-value`, in full: `kept_values.built_in_texts`
  and `kept_values.built_in_numbers` (section 6.4);
- the values named with `--missing-value`, in part: every key of every
  published `missing_by_source` that is not blank and not a member of
  the published vocabulary is a declared spelling, since ways 1, 2 and 3
  are the only other ways a spelling reaches that map and each is
  recognisable on its own; plus every member of the published vocabulary
  named in `declared_missing_values.built_in_texts` and
  `declared_missing_values.built_in_numbers`.

**3.3.2 And where the derivation is incomplete, the description says
so.** Two counts remain that no spelling accounts for:
`n_missing_withheld`, which is cells whose spelling the floor pooled,
and the whole absent-cell accounting of a nothing-publishing column,
which is empty by its publication class. A consumer that must read a
file exactly cannot do so for those cells and knows it from the document
alone. What `synthtwin validate` does about that is amendment A-P3-26's
ruling and `docs/spec/validation-method-v1.md`'s to state; this contract
states only that the deficit is visible in the document.

**3.3.3 A consumer may not conclude that a named value occurred.** The
two vocabulary lists of section 6 record what the person TYPED. A person
may name a word their table does not hold, and the lists are written the
same either way (invariant C5-K5). Nothing in them is evidence that any
cell of the table wore the word.

---

## 4. Part one — the spelling is stored exactly

### 4.1 The change

**C5-1.** In version 4, a key of `missing_by_source` is the absent-value
spelling "after passing through the display boundary that escapes line,
control and bidirectional formatting characters" (version 4 section 5.4).
**In version 5, a key of `missing_by_source` is the spelling exactly as
the file wrote it, character for character, before trimming and before
any fold.** This supersedes the corresponding sentence of version 4
section 5.4 and the second sentence of its decision 13.5.

The rule is now the same rule `variants` carries, for the same reason
version 4 gives for `variants` (its 7.4.2): a key something has to read
back is a key that must survive being written down.

### 4.2 Where the spelling may appear, and where it may not

**C5-2.** The exact spelling may appear in exactly one place: as a key
of `missing_by_source` in the profile document, on a column whose
publication class permits it (version 4 section 6.10, carried).

**C5-3.** The exact spelling may NOT appear anywhere a person reads.
Every surface that shows a `missing_by_source` key to a person puts that
key through the display boundary first, at the moment of showing, and
never stores the result: the plain-language summary, the generation
report, the quality report, and any command output. A surface that
interpolates a stored key without the boundary is a defect in the
implementation, not in this contract.

**C5-4.** The printed form is therefore unchanged from version 4. A
version 5 run and a version 4 run over the same table with the same
options print the same characters for the same key. What changed is the
file, not the page.

### 4.3 The file itself, stated because it is a real consequence

**C5-5.** A version 5 profile may hold, inside a JSON string, a
character that a terminal would obey rather than print. Canonical JSON
escapes the C0 controls, the quote and the backslash, so the commonest
of them cannot reach a terminal from the file; a bidirectional override
or a zero-width mark is written as itself and could. **This is not a new
kind of exposure**: a version 4 profile's `variants` keys already have
exactly this property, by version 4 decision 13.5, and the position was
taken there deliberately. The profile is a machine file; every surface a
person reads goes through the boundary (C5-3).

**C5-6.** Every exact spelling is representable. The readers of record
decode the table as UTF-8 or as latin-1, neither of which can produce an
unpaired surrogate, so no spelling can reach the document that the
canonical round trip would refuse under version 4's R6. A producer that
finds itself unable to write a spelling has a defect, not a case.

### 4.4 The floor is untouched, and in one corner it binds harder

**C5-7.** The floor decides WHICH spellings are named. Part one decides
only HOW a named spelling is written. Every floor rule of version 4
holds at its version 4 wording: a spelling shared by fewer than
`small_cell_floor` cells is not named, in version 5 exactly as in
version 4.

**C5-8.** One consequence runs the other way and is recorded because it
is the opposite of a relaxation. In version 4 the floor was applied to
the ESCAPED key, so two different source spellings that escape to the
same text were counted as one group, and their combined count could
reach the floor although neither spelling alone did. Version 4 could
therefore name a group no single spelling of the table reached. **In
version 5 the floor is applied to the exact spelling**, so each is
counted on its own and each is pooled on its own. Version 5 names
strictly fewer groups in that corner, never more.

### 4.5 Disposition

**C5-9.** `missing_by_source` stays **REPORT-ONLY**. The twin writes
every absent cell as an empty field; no absent-value spelling is
reproduced in any twin, and the generation report names the published
spellings so a person can see what was not carried over. Version 4's
residual R-P2-2 is unchanged.

**C5-10, and it is the correction that made this part necessary.**
REPORT-ONLY says what the TWIN owes a field. It says nothing about
whether the text stored for that field must be exact. Version 4
decision 13.5 read the two as one — "`missing_by_source` is REPORT-ONLY
and never written into a cell, while `variants` is EXACT-OBSERVABLE and
must read back byte for byte" — and that reading was true of the twin
and false of the description. A field can owe the twin nothing and still
have to be stored exactly, because something other than the generator
reads it. **In this contract, "REPORT-ONLY" is never a licence to store
a lossy form of a value.** Where a field's stored form must be exact,
this document says so in the field's own clause, and C5-1 says so for
`missing_by_source`.

### 4.6 The disclosure delta of part one, at its size and priced

**What is published that version 4 withheld.** For a spelling that is
already named — that is, one at least `small_cell_floor` cells of the
column shared, which version 4 already published as a key — version 5
publishes the spelling exactly where version 4 published a form that
several different spellings share. The delta is exactly the ambiguity
the escape introduced, on groups the floor already permitted to be
named.

**How large it is.** It is empty for every spelling made only of
characters that show themselves, which is every ordinary word. It is
non-empty only for a spelling that holds a character which instructs a
display, or that holds a run of characters identical to the printable
form the boundary writes for one. For such a spelling, a reader of a
version 5 profile sees which of the candidate spellings it was; a
reader of a version 4 profile sees only the set. **No group that version 4
withheld becomes named. No count changes. No column changes. No row is
identified.**

**And it is smaller in one direction**, by C5-8: the merge corner
version 4 permitted is gone, so there are groups version 4 named that
version 5 pools.

**Priced.** The owner ruled this on 2026-08-17 with the delta stated
above. What it buys is that two tables needing opposite readings stop
producing byte-identical descriptions — which was not a matter of
detail: a file wearing one of the two spellings passed against the other
one's description with a census of zero missed, and its own description
reported seven obligations missed against the very file it was written
from.

---

## 5. Part two — the pooled count and the blank count leave the map

### 5.1 The change

**C5-11.** Version 4's `missing_by_source` mixes two key spaces: the
person's spellings, and two of synthtwin's own words, `(blank)` and
`(withheld)`. **In version 5 the map holds one key space.** Its keys are
spellings some cell of the table held, and nothing else. The two words
move to two counts of their own.

This is the shape `variants` and `variants_withheld` already have, for
the reason version 4's 7.4.4 gives: the remainder is a different kind of
fact from a named group, and a field that carries both cannot be read.

### 5.2 The two new keys

Both are UNIVERSAL: present on every column block, on every role,
including when their content is zero. Version 5 has no optional keys,
exactly as version 4 has none.

| key | JSON type | range | meaning | disposition |
|---|---|---|---|---|
| `n_missing_blank` | integer | ≥ 0 | how many absent cells of this column held nothing, or nothing but space — written when at least `small_cell_floor` cells did, and `0` otherwise, those cells being counted in `n_missing_withheld` instead | REPORT-ONLY |
| `n_missing_withheld` | integer | ≥ 0 | how many absent cells of this column wore a spelling — or a blankness — that fewer than `small_cell_floor` cells of the column shared, pooled together and unnamed | REPORT-ONLY |

**C5-12.** `missing_by_class` is unchanged: five keys, always all five,
the same five words, the same meanings, invariants N1 and N2 at their
version 4 wording. Its keys are a closed first-party enumeration into
which no text of the table can land, so it carries no collision to
close.

**C5-13.** `n_missing_blank` is not the same number as
`missing_by_class["(blank)"]` and neither replaces the other. The class
count is pooled when the CLASS falls below the floor; this count is
pooled when the SPELLING — here, blankness — falls below it. Version 4
published both, the second as the `(blank)` key of `missing_by_source`.
Version 5 publishes both, in two fields instead of one.

### 5.3 The amended invariants

**C5-N3 (the source accounting closes).** This supersedes version 4's
N3. On a column that is not a nothing-publishing column:

```
sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld
    == n_missing
```

On a nothing-publishing column, `missing_by_source == {}`,
`n_missing_blank == 0` and `n_missing_withheld == 0`, whatever
`n_missing` is.

**C5-N4 (the floor, with no exemption left).** This supersedes version
4's N4. Every value of `missing_by_source` is at least
`small_cell_floor`, and `n_missing_blank` is either `0` or at least
`small_cell_floor`. Version 4 exempted its two class keys in the
invariant although the producer applied the floor to them anyway; in
version 5 the exemption is gone, which makes the rule the one the
producer already followed. `n_missing_withheld` carries no such bound
in either direction: it is what the published counts were pooled out
of, one remainder pools several groups at once, and version 4 bounded
its `(withheld)` value the same way, which is not at all.

**C5-N5 (the map has no reserved key).** No key of `missing_by_source`
has a first-party meaning. A key reading `(withheld)`, `(blank)`,
`(declared-missing)`, `(numeric-sentinel)` or `(text-code)` means that
cells of the table held exactly that text. A consumer that treats any
key as a marker is defective.

**C5-N6 (the two counts follow the publication class).** `n_missing_blank`
and `n_missing_withheld` are zero on exactly the columns where
`missing_by_source` is empty for the publication-class reason of version
4 section 6.10. The publication class is derivable from `role` and
`structural_role`, which every block publishes, so a consumer can always
tell "this column publishes no source accounting" from "this column had
nothing to account for".

**C5-N7 (a producer obligation, stated because a loader cannot check
it).** A key of `missing_by_source` is the source spelling character for
character. A loader holds no table and cannot verify this; it is
verified on the producer's side, by a test that profiles two tables
differing only in a spelling the display boundary would merge and
requires the two descriptions to differ.

### 5.4 What is deliberately NOT copied from `variants_withheld`

**C5-14.** `variants_withheld` is a multiplicity map: it publishes how
many withheld spellings covered one row, two rows, and so on.
`n_missing_withheld` is a single integer. The shape is not copied, and
the reason is not economy:

- a multiplicity map would publish the SIZES of groups the floor held
  back, which version 4's `missing_by_source` does not publish for
  absent-value spellings — it publishes one pooled total;
- and it would buy the reader of the description nothing. What a
  consumer needs from the pool is how many cells it cannot attribute.
  Knowing that the pool is three spellings of four cells rather than one
  spelling of twelve does not recover a single spelling.

A field that publishes more and buys nothing is a field written the
wrong way round. `variants_withheld` has the shape it has because the twin
has to invent exactly that many spellings at exactly those sizes; no
twin has to invent an absent-value spelling at all.

### 5.5 The disclosure delta of part two: none, and here is the proof

Part two publishes exactly the numbers version 4 published, under
different names:

| version 4 | version 5 | same number? |
|---|---|---|
| `missing_by_source["(blank)"]`, present when at least the floor of cells were blank | `n_missing_blank` | yes — same rule, same floor, same count |
| `missing_by_source["(withheld)"]`, present when anything was pooled | `n_missing_withheld` | yes — same rule, same floor, same count |
| every other `missing_by_source` key and value | the same key and value, spelled exactly (part one) | the value is the same number; the key's spelling is part one's delta and is priced in 4.6 |

No count is added, no count is removed, and no count is computed under a
different rule. The only thing part two changes is which field a number
lives in — and therefore whether a consumer can tell a person's word
from synthtwin's.

---

## 6. Part three — which of synthtwin's own words were named

### 6.1 The published vocabulary

**C5-15.** Section 14.1 fixes two closed lists: the ten spellings
synthtwin reads as "no value", and the three stand-in numbers it judges.
Together they are **the published vocabulary**. In version 5 these lists
are NORMATIVE: a producer whose built-in lists differ from section 14.1
does not write version 5 documents, and adding a word to either list is
a change to this contract and advances `profile_version`.

**This raises a bar that did not exist.** In version 4 the built-in
lists are an implementation detail, changeable without touching any
document. From version 5 they are part of the wire format, because a
consumer decides what a key means by asking whether it is one of them.
The cost is that the lists cannot be extended quietly; the buy is that
"is this word synthtwin's or the person's?" has one answer both sides
compute the same way.

### 6.2 The two new keys, inside the two declaration records

Version 4's `settings.kept_values` and
`settings.declared_missing_values` each hold exactly two keys. In
version 5 each holds exactly four. `settings` itself still has exactly
fifteen keys; nothing is added at its top level.

| key | JSON type | contents | disposition |
|---|---|---|---|
| `n_declared` | integer ≥ 0 | how many values were named this way, unchanged from version 4 | LOADER-ONLY |
| `values_recorded` | boolean | exactly `false`, unchanged from version 4 | LOADER-ONLY |
| `built_in_texts` | array of strings | which members of section 14.1's spelling list this declaration named; sorted ascending by code point; pairwise distinct; possibly empty | LOADER-ONLY |
| `built_in_numbers` | array of numbers | which members of section 14.1's stand-in list this declaration named; sorted ascending; pairwise distinct; possibly empty | LOADER-ONLY |

Worked example — `synthtwin profile table.csv --keep-value " N/A " --keep-value -999.00 --missing-value WOMBAT`:

```
"kept_values": {
  "built_in_numbers": [
    -999.0
  ],
  "built_in_texts": [
    "n/a"
  ],
  "n_declared": 2,
  "values_recorded": false
},
"declared_missing_values": {
  "built_in_numbers": [],
  "built_in_texts": [],
  "n_declared": 1,
  "values_recorded": false
}
```

Three things in that example are the whole of section 6, and each is
required:

- the person typed `" N/A "`; the document holds `"n/a"`, which is the
  VOCABULARY MEMBER, not their spacing and not their capitals;
- the person typed `-999.00`; the document holds `-999.0`, which is the
  vocabulary member. The two denote one number, which is the identity
  `settings.declaration_matching` already fixes;
- the person typed `WOMBAT`, which is their own word; the document holds
  it nowhere, and `n_declared` counts it.

### 6.3 The rule that makes this safe, stated as an obligation

**C5-16 (the lists are a function of the command line alone).** The
contents of `built_in_texts` and `built_in_numbers` are computed from
what the person typed and from section 14.1, and from nothing else. No
cell of the table is consulted. **A declared value that matched no cell
of any column is recorded exactly as one that matched every cell.** Two
runs with the same options over two different tables write the same four
lists.

**C5-17 (only a vocabulary member is ever written).** A declared value
enters `built_in_texts` when its trimmed, case-folded form equals a
member of section 14.1's spelling list, and what is written is that
MEMBER. A declared value enters `built_in_numbers` when it reads as a
number and that number is one of section 14.1's three, and what is
written is that member's canonical form. A declared value that is
neither is written nowhere. **No character a person typed reaches the
document through these lists.**

**C5-18 (the counts are unchanged).** `n_declared` counts every value
named that way, whether or not it is a vocabulary member. So
`len(built_in_texts) + len(built_in_numbers) <= n_declared`, and a
consumer reading a shortfall knows only that some values named were not
synthtwin's own words — never what they were.

### 6.4 What part three closes, proved

**C5-19.** The values for which `--keep-value` can change how any cell
is read are exactly the members of the published vocabulary. Therefore
`kept_values.built_in_texts` and `kept_values.built_in_numbers` record
the WHOLE of the kept side's effect on the reading rule, and the kept
half of the loss closes completely.

**The proof is a walk over the producer's own rules, and it is
reproduced here so a reviewer need not take it on trust.** A rescue can
only matter for a cell that would otherwise have been absent, and
section 3.1 is total over the ways a cell becomes absent:

- way 1, blank: rescued only by a declaration whose folded form is the
  empty spelling, which is a member of the vocabulary;
- way 2, a built-in word: rescued only by a declaration whose folded
  form equals that word, which is a member by construction;
- way 3, a stand-in number: the three stand-ins are the only candidates
  the column-level rule can judge, so a rescue reaches this way only by
  naming one of the three, which is a member;
- ways 4 and 5, the person's own declaration: a value named with
  `--keep-value` and with `--missing-value` at once is refused before
  the table is opened, and the refusal names the two words, so no cell
  is reached this way;
- and a cell that would have been PRESENT anyway is unaffected by being
  rescued.

A `--keep-value` naming anything else changes no cell's reading, so
recording it would record a fact with no consequence. That is why C5-18's
shortfall is not a gap: a consumer reading `n_declared: 3` beside one
vocabulary member may soundly conclude that the other two rescues
changed nothing, and that conclusion is sound.

**C5-20.** On the `--missing-value` side, part three closes what a
built-in word costs and no more. Naming a built-in word as missing does
not make its cells absent — they already were — but it moves them from
class `(text-code)` to class `(declared-missing)`, and a consumer
comparing class counts needs to know that. Part three records it. A
`--missing-value` naming the person's own word is recovered from
`missing_by_source` where the floor permits and the column publishes,
and is not recovered otherwise; that is section 7.

### 6.5 Invariants

**C5-K1 (membership).** Every element of `built_in_texts` is a member of
section 14.1's spelling list. Every element of `built_in_numbers` is a
member of section 14.1's stand-in list. A loader refuses any other value,
naming it, because a value outside the list is a value from somebody's
table.

**C5-K2 (form).** Both arrays are sorted ascending — `built_in_texts` by
code point, `built_in_numbers` numerically — and pairwise distinct.
Order is part of the canonical bytes and a producer may not shuffle it
between runs.

**C5-K3 (the count bounds the lists).**
`len(built_in_texts) + len(built_in_numbers) <= n_declared`, in each of
the two records.

**C5-K4 (the two records do not overlap).** No member appears in both
`kept_values` and `declared_missing_values`: not in the two text lists,
and not in the two number lists. A value named both ways is refused
before the table is opened, so a document carrying one is a document its
own settings contradict.

**C5-K5 (a producer obligation, stated because a loader cannot check
it).** The lists are a function of the command line alone (C5-16). A
loader holds no command line and cannot verify this; it is verified on
the producer's side, by a test that profiles two tables — one holding
the named word and one not — with the same options, and requires the
four lists to be identical.

**C5-S7 (`values_recorded`, restated).** This supersedes version 4's S7.
`values_recorded` is `false` in both records of every version 5
document, and a loader refuses `true`. Its meaning is fixed here so that
it cannot be read as contradicting the two new lists:

> `values_recorded: false` says that this record does not carry the text
> the person typed. The two lists beside it are not that text: each
> holds members of the closed vocabulary printed in section 14.1 of this
> contract, which is synthtwin's own and identical in every
> installation, written in the vocabulary's spelling and never in the
> person's (C5-17).

Its version 4 role as a discriminator against a much older format that
carried an array of spellings under the same key is unchanged.

**C5-S14 (membership).** Each declaration record has exactly the four
keys of 6.2. No other key may appear under either; a loader refuses one
that does, naming it and the record.

### 6.6 The confidentiality rule: what this changes, and what it does not

**THIS LOWERS the Phase 1 settings-block rule, and the lowering is
stated at its size, with its price and on whose authority.**

**What the rule said.** Phase 1 fixed, at review item P1-R7-F2, that the
settings block carries the POLICY — how many values were named each way,
and the rules that matched them — and **never a spelling**. The reason
is sound and is not withdrawn: a declaration is compared against every
cell of every column, including the columns whose values never appear in
a description at all, so a spelling written into the settings would
publish a value out of all of them at once.

**What the rule says from version 5.** The settings block carries the
policy, and it names which members of synthtwin's own published
vocabulary a declaration named. It still never carries a spelling of the
person's own.

**What that gives up, stated at its size.** A reader of a version 4
description is told how many values were named each way. A
reader of a version 5 description is told, in addition, which members of
a thirteen-member list published in this contract were among them. That
is the whole delta. It carries no count of cells, no column, no row and
no text of the table (C5-17), and it is written the same whether the
named word occurs in the table or not (C5-16), so the field itself is
not evidence that any cell wore the word.

**What a reader can still infer, said rather than waved away.** A person
usually types a word because it is in their table. A version 5
description therefore makes a guess available that a version 4
description made only coarser: not "one value was rescued" but "the
value rescued was `n/a`". The word guessed at is one of ten synthtwin
publishes in its own documentation; it can never be a name, a code, a
diagnosis or a free-text answer, because a value outside the list is
never written (C5-K1). The guess is about which of thirteen fixed words
somebody typed, and nothing else.

**The one place it can be combined, and its bound.** A reader holding
the whole description can put a vocabulary member beside a column's own
`missing_by_class` and `n_missing_withheld` and, where a column's
accounting leaves one explanation, conclude that a below-floor group of
cells wore that word. The bound on this is exact: the SIZE of that group
is a number version 4 published too — `n_missing_withheld` is version
4's pooled `(withheld)` count under a new name (5.5) — and the word is
one of thirteen synthtwin publishes. So what version 5 adds to that
combination is the same thirteen-member guess, not a new count and not a
new group.

**Priced, and on whose authority.** The owner's, ruled on 2026-08-17
with this delta stated to them, and taken because the alternative leaves
a researcher who rescues one of synthtwin's own words without a usable
check on the table the description was written from. The analysis that
was put to the owner named this as the part of the change that touches a
Phase 1 rule and said explicitly that the call was theirs and not the
implementer's; it has now been made.

**What is NOT relaxed, in as many words.** `values_recorded` stays
`false`. A declared value that is not a member of the published
vocabulary is still recorded nowhere. Every publication class of version
4 section 6.10 is unchanged: a nothing-publishing column publishes no
value of the table in version 5 either. Every floor rule is unchanged.
No column block publishes anything version 4 did not.

**The obligation this carries to the readable surfaces.** The new fact
is named in `SECURITY.md` and in the plain-language summary beside the
description, on the precedent of version 4's label-variant fact
(residual R-P2-11 and version 4 section 7.4.5). That obligation belongs
to the implementation stage and to the plan, not to this contract; it is
recorded here because a reader of this section will ask where the
disclosure went.

---

## 7. What version 5 does NOT close

**This section is normative and may not be softened. Both entries are
limits, not defects, and each is stated at the size it was measured at.**

### 7.1 A column that publishes no value of the table

**C5-21.** On a nothing-publishing column — free text, declared
identifiers, record-number columns, and columns whose numbers are
unrepresentable — `missing_by_source` is empty, `n_missing_blank` is
zero and `n_missing_withheld` is zero, whatever made the cells absent
(C5-N6). A word the person named with `--missing-value` on such a column
is recorded nowhere unless it is a member of the published vocabulary.

**No change to this format can close it.** The whole of what those
columns publish is counts and shapes; publishing the marker word would
publish text out of a column that exists to publish none. This is the
one place where publishing safely and describing completely genuinely
conflict, and version 5 leaves the conflict standing.

**What it costs, measured.** On a free-text column of sixty comments and
twelve cells holding a declared marker, the twelve markers are measured
as if they were comments. Two such tables — one with a three-character
marker, one with a twenty-character marker — produce byte-identical
descriptions, and each is wrong about the file in front of it in the
same eleven obligations. Under amendment A-P3-26 those obligations are
listed as not checkable with a printed reason instead of reported as
missed; twenty-one of thirty-one obligations move and ten checks remain.
Version 5 changes none of those numbers.

### 7.2 A spelling the floor pooled

**C5-22.** A spelling shared by fewer than `small_cell_floor` cells of a
column is pooled into `n_missing_withheld` and is not named, in version
5 exactly as in version 4. Where that spelling is a member of the
published vocabulary, section 6 records the declaration anyway; where
it is the person's own word, it is not recovered.

**Closing it would mean naming a group the floor exists to keep too
large to point at**, which is the floor's entire purpose. Version 5 does
not close it and does not weaken the floor to close it.

**What it costs, measured.** A column with one declared word published
by name and a second pooled beneath the floor rebuilds half its reading
rule; under amendment A-P3-26 forty-three of fifty-three obligations
move to not checkable and ten checks remain. Version 5 changes those
numbers only where the pooled word is one of synthtwin's own.

### 7.3 Where these two are handled

**C5-23.** Both are handled by amendment A-P3-26's routing, unchanged:
the description is asked, before any file is read, whether the reading
rule can be rebuilt for each column, and where it cannot the column's
cell-counted obligations go to the NOT-CHECKABLE census with a sentence
saying what the description does not record. Version 5 makes that
question answer YES in more cases; it does not remove the question, and
the two limits above are exactly the cases where the answer stays NO.

---

## 8. Every new and changed key, in one table

| key | where | JSON type | when present | meaning | disposition |
|---|---|---|---|---|---|
| `profile_version` | top level | integer | always | the contract version. In this contract, exactly `5` | LOADER-ONLY |
| `missing_by_source` | every column block | object | always | absent cells by the EXACT spelling that made them absent, under the floor; keys are the table's text and never a first-party word (C5-1, C5-N5) | REPORT-ONLY |
| `n_missing_blank` | every column block | integer ≥ 0 | always | absent cells that held nothing but space, when at least the floor did; `0` otherwise | REPORT-ONLY |
| `n_missing_withheld` | every column block | integer ≥ 0 | always | absent cells whose spelling fewer than the floor shared, pooled and unnamed | REPORT-ONLY |
| `built_in_texts` | `settings.kept_values`, `settings.declared_missing_values` | array of strings | always | which members of section 14.1's spelling list this declaration named | LOADER-ONLY |
| `built_in_numbers` | `settings.kept_values`, `settings.declared_missing_values` | array of numbers | always | which members of section 14.1's stand-in list this declaration named | LOADER-ONLY |

**Nothing is removed.** Every key of a version 4 document appears in a
version 5 document with its version 4 name, type and meaning, except
that two RESERVED KEYS of one object are gone: `missing_by_source` no
longer has a `(blank)` key or a `(withheld)` key with a first-party
meaning. Those are not keys of the format — they are values a key could
take — and the counts they carried are carried by the two new integers.

**What a version 4 consumer must do.** Refuse. A strict version 4 loader
refuses a version 5 document, because keys it does not know have
appeared and because `profile_version` is not 4, and that refusal is
correct. There is no partial reading and none is offered.

---

## 9. Every new and changed invariant, in one checkable list

Version 4's section 8 list is carried entire, with the four
substitutions marked. Each statement below is either true or false of a
parsed document, with no interpretation left, except the two marked as
producer obligations, which are true or false of a producer.

| id | supersedes | statement |
|---|---|---|
| C5-N3 | N3 | on a column that publishes source accounting, `sum(missing_by_source.values()) + n_missing_blank + n_missing_withheld == n_missing`; on a nothing-publishing column the map is empty and both counts are 0 |
| C5-N4 | N4 | every value of `missing_by_source` is ≥ `small_cell_floor`, with no exemption, and `n_missing_blank` is 0 or ≥ `small_cell_floor` |
| C5-N5 | — | no key of `missing_by_source` carries a first-party meaning |
| C5-N6 | — | `n_missing_blank` and `n_missing_withheld` are 0 on exactly the nothing-publishing columns of version 4 section 6.10 |
| C5-N7 | — | *(producer)* a `missing_by_source` key is the source spelling character for character |
| C5-K1 | — | every `built_in_texts` element is in section 14.1's spelling list; every `built_in_numbers` element is in its stand-in list |
| C5-K2 | — | both arrays are sorted ascending and pairwise distinct |
| C5-K3 | — | `len(built_in_texts) + len(built_in_numbers) <= n_declared`, in each record |
| C5-K4 | — | no member appears in both declaration records |
| C5-K5 | — | *(producer)* the four lists are a function of the command line alone |
| C5-S7 | S7 | `values_recorded` is `false` in both records, and means that the person's own typed text is not carried |
| C5-S13 | S13 | at a floor of one, `n_missing_withheld` joins the fields that must be zero and `missing_by_source` leaves the list; `n_missing_blank` is not on it |
| C5-S14 | — | each declaration record has exactly the four keys of 6.2 |
| C5-VER | — | `profile_version` is exactly the integer `5` |

**C5-S13 (a floor of one holds nothing back, restated).** This
supersedes version 4's S13, which lists the fields that must be empty
or zero where `small_cell_floor` is 1. Two edits and no others: the
list LOSES `missing_by_source`, whose pooled `(withheld)` entry no
longer exists, and GAINS `n_missing_withheld`, which is zero there for
S13's own reason — at a floor of one the range of group sizes below the
floor is empty, so nothing may be held back at all. `n_missing_blank`
is NOT on the list and must not be added to it: at a floor of one every
blank group reaches the floor, so blanks are named rather than pooled,
which is what the rule requires. Every other field S13 names —
`suppressed_levels`, `suppressed_rows`, `suppressed_level_counts`,
every `variants_withheld` block, `n_sentinel_candidates_unpublished`,
and the `(withheld)` entries of `missing_by_class`, `utc_offsets` and
`numeric_styles` — stays on it unchanged. The rule is still checked
with the top-level rules, before any column block is read.

**The other version 4 invariants that are touched, and how.** N1 and N2
are unchanged: `missing_by_class` did not move. V1 to V4 are unchanged:
`sentinel_verdicts` did not move, and V2 still ties `(withheld)`
candidates to the nothing-publishing columns. S8 and S9 are unchanged.
W1 to W7 are unchanged. Every role invariant that says
"`missing_by_source` empty, candidates withheld" — U4, I3, F3 — is read
with C5-N6 beside it, so it now says the two counts are zero as well.

---

## 10. The version rule and the refusal

### 10.1 The rule

**C5-24.** `profile_version` MUST be exactly the integer `5`. The
loader's order of operations is version 4's section 10.1, unchanged,
including that the version is read at step 5 before the canonical
round trip at step 6 and why. The refusal catalogue is version 4's
section 10.7, unchanged, with R11 and R12 reading against 5 instead of
against 4.

**C5-25.** The loader is fail-closed and reads exactly one version. It
does not upgrade a version 4 document, does not partially accept one,
and does not offer to. A description carries facts computed from a table
under rules that changed; converting it would mean making up the facts
the older rules did not record, which is the whole reason this version
exists.

### 10.2 The refusal a researcher acts on, word for word

**C5-26.** R11's message, for the case that matters — a version 4
document, which is every description written before the implementation
stage lands — is exactly this text, with only the two version numbers
filled in from the document and the loader:

> This description was written by an older version of synthtwin: it says
> it is version 4, and this synthtwin reads version 5. A version 5
> description records which of synthtwin's own words for "no value" you
> named on the command line, and a version 4 description does not, so
> this file cannot be read back exactly. Please make the description
> again by running 'synthtwin profile' on your table, giving the same
> --keep-value and --missing-value options you gave the first time, and
> use the file it writes exactly as it writes it.

**Why the advice is safe to give, and when it stops being safe.** It
assumes the person still holds the table. That is true of every
description in existence on the day this lands: the version is
`0.1.0.dev0`, there is no release, there are no tags, and every
description belongs to somebody who made it themselves. **After the
first release this assumption is no longer safe for every reader**, and
the wording above is then re-examined rather than inherited — which is
exactly the reasoning that made this the moment to change the format.

**Why it names the two options.** A person who ran with no declarations
loses nothing by re-running; a person who ran with declarations and
forgets them gets a description that reads their table differently from
the first one. Naming the options is the difference between advice that
can be followed and advice that can be followed wrongly.

**C5-27.** R12's message — a document NEWER than this loader reads — is
version 4's, unchanged in substance: it says which version this
synthtwin reads and which the document claims, tells the person to
update synthtwin, and NEVER tells them to make the description again,
because a newer description means this synthtwin is behind and the
machine in front of them may not hold the table.

**C5-28.** Neither message quotes anything from the document except the
two version numbers.

---

## 11. The disposition matrix, delta only

Version 4's section 9 is carried entire. These are the rows that change
or are added; every other row is unchanged, including every row of its
9.4, 9.5, 9.6, 9.7 and 9.8.

| field | disposition | note |
|---|---|---|
| `missing_by_class`, `missing_by_source` | REPORT-ONLY | unchanged in class. `missing_by_source`'s STORED form must be exact (C5-1, C5-10); REPORT-ONLY has never meant otherwise and now says so |
| `n_missing_blank` | REPORT-ONLY | every absent cell is written empty in the twin; the generation report names the count |
| `n_missing_withheld` | REPORT-ONLY | as above |
| `settings` | LOADER-ONLY | whole subtree, unchanged — the two new arrays are inside it |
| `profile_version` | LOADER-ONLY | unchanged in class; the value is 5 |

**C5-29.** REPORT-ONLY is evidenced by the fact being asserted present
in the generation report. The two new counts therefore join the report,
beside the two maps that are already there. Printing them prints
numbers version 4 already printed under other names (5.5).

**C5-30.** A completeness assertion enumerates every key the producer
emits, for every role, plus every top-level key, and FAILS when any key
has no disposition in version 4's matrix as amended here. It must pass
against the two documents read together; it may not acquire exceptions
during implementation.

---

## 12. The disclosure delta of version 5, in one place

Stated in one place because it is the part a person must be able to
weigh.

| part | what it publishes that version 4 did not | size |
|---|---|---|
| 1 — exact spelling | for a spelling the floor already permitted to be named, which of the spellings sharing one printable form it was | empty for every spelling made of characters that show themselves; non-empty only where a spelling holds a character that instructs a display, or a run identical to the printable form of one. No new group is named, no count changes, and in the merge corner of C5-8 version 5 names strictly fewer groups than version 4 |
| 2 — the pooled and blank counts leave the map | nothing | the same two numbers, under two names, computed by the same rules under the same floor (5.5) |
| 3 — the named vocabulary members | which members of a thirteen-member list published in section 14.1 a declaration named | no count of cells, no column, no row, no text of the table; written identically whether or not the word occurs (C5-16); bounded by C5-K1 to that list and no other value |

**What is unchanged.** Every published fact of a version 4 column block
is published by a version 5 column block, at the same width, under the
same floor. No role's publication class moves. No nothing-publishing
column publishes a value. The relationship manifest is eight nulls.

**And the handling rule is unchanged.** Every file a full run leaves
behind — the profile, the plain-language summary beside it, the twin,
the twin's report and the quality report — carries facts computed from
real data, so the institution's rules for real-derived material apply to
all five. synthtwin claims no formal privacy guarantee, and version 5
makes no privacy claim of any kind.

---

## 13. Decisions this document took, and why

Each is listed so a reviewer can accept or reject it here, at the
cheapest place, rather than discover it in code.

**13.1 Version 4 is carried by reference rather than copied** (2.2), and
the rule that keeps the version 4 document a record while it is also the
referenced text is written down rather than left to convention. The cost
is that an implementer reads two documents; the buy is that no rule has
two homes.

**13.2 `missing_by_source` keeps its name.** Its key space changed and
its storage rule changed, and a rename would have made every passage of
every other document ambiguous about which field it meant. The version
number is what tells the two apart, which is what a version number is
for.

**13.3 The pooled remainder is an integer, not a multiplicity map**
(5.4). The shape `variants_withheld` uses would publish group sizes the
floor held back and would buy a consumer nothing.

**13.4 The blank count is floor-governed, exactly as version 4's
`(blank)` key was.** A blank count exempt from the floor would have been
a wider publication than version 4's, on every column, for no reason
anybody asked for.

**13.5 The two vocabulary lists are two arrays, not one mixed array.**
A single array holding both strings and numbers is a shape that has to
be type-tested at every read, and the two are matched by two different
rules — folded spelling and exact number — which is the same reason
`settings.declaration_matching` has the value it has.

**13.6 The vocabulary member is written, never the person's spelling**
(C5-17). Writing what they typed would have put their spacing and their
capitals in the document for no gain: the matching rule is over the
folded form and over the number, so the member carries everything a
consumer needs.

**13.7 The lists are written whether or not the word occurs** (C5-16).
The alternative — recording only the words that actually matched a
cell — would have made the field evidence about the table, which is
exactly what section 6 exists not to be. It would also have been wrong
for the consumer, which needs the RULE the run applied and not its
outcome.

**13.8 The published vocabulary becomes normative** (C5-15). The cost is
that the built-in lists can no longer be extended without a contract
change; the alternative is that two installations disagree about whether
a key is synthtwin's word or the person's.

**13.9 `values_recorded` keeps its name and its value.** Renaming it
would have cost the discriminator its job against the much older format
that carried an array of spellings under the same key. Its meaning is
therefore fixed in words instead (C5-S7), because a boolean beside two
lists is a place a reader can draw the wrong conclusion.

**13.10 Two producer obligations are stated as invariants although a
loader cannot check them** (C5-N7, C5-K5). Leaving them out would have
left the two properties the whole change rests on unwritten; marking
them is what tells an implementer to prove them on the producer's side
instead of looking for a loader rule that cannot exist.

**13.11 Route 4 and the below-floor route are written into the
normative text** (section 7) rather than into a residual list. A limit a
reader has to find somewhere else is a limit a reader does not find.

**13.12 No feasibility rule, no generation rule and no method text is
changed here.** No field this document moves is read by any generation
rule, so no twin cell changes and no frozen twin byte moves. The frozen
reference vectors carry profile fragments and are regenerated as
bookkeeping, which is a changelogged event under the plan's D12 and is
not a change to any twin.

---

## 14. Appendix: the enumerations version 5 adds or changes

### 14.1 The published vocabulary — NORMATIVE from version 5

**The spellings synthtwin reads as "no value"**, compared after trimming
and a Unicode case fold. Ten members, and this list is the whole of it:

| # | member | note |
|---|---|---|
| 1 | `` (the empty spelling) | a cell holding nothing, or nothing but space |
| 2 | `-` | |
| 3 | `--` | |
| 4 | `.` | |
| 5 | `?` | |
| 6 | `n/a` | |
| 7 | `na` | |
| 8 | `nan` | |
| 9 | `none` | |
| 10 | `null` | |

**The stand-in numbers synthtwin judges**, compared as numbers. Three
members, and this list is the whole of it:

| # | member | canonical form in a document |
|---|---|---|
| 1 | minus nine thousand nine hundred and ninety-nine | `-9999.0` |
| 2 | minus nine hundred and ninety-nine | `-999.0` |
| 3 | nine thousand nine hundred and ninety-nine | `9999.0` |

A stand-in is read as "no value" only where the column's own rule judges
it to be one, and every candidate's fate is published in
`sentinel_verdicts` either way. Being on this list is not a verdict.

### 14.2 Where `(withheld)` appears in a version 5 document

This supersedes the corresponding table of version 4 section 14.

| place | meaning |
|---|---|
| `missing_by_class` | the pooled count of absent-value CLASSES whose own counts fell below the floor |
| `sentinel_verdicts[].candidate` | the block's publication class permits no value of the table anywhere in it |
| `utc_offsets` | the pooled count of cells whose OFFSETS fell below the floor |
| `earliest_utc_offset`, `latest_utc_offset` | that endpoint's offset is one the map is withholding |
| `numeric_styles` | the pooled count of cells whose spelling STYLE was used by too few rows to name |

**`missing_by_source` is no longer on this list**, and neither is the
`(blank)` key it carried. In a version 5 document those two counts live
in `n_missing_withheld` and `n_missing_blank`.

**One token, one meaning, and now one key space.** Wherever `(withheld)`
appears above, it is a group too small to name, counted rather than
named, and every list it appears in draws its other keys from a fixed
first-party vocabulary — style names, time-zone offsets, class words.
**After version 5 there is no field of this format in which a value of
somebody's table and one of synthtwin's own words can land in the same
slot.** That property is what part two bought, and a field added later
that breaks it breaks this sentence.

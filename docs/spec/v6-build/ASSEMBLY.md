# Assembling the self-contained version 6 contract

Working notes for the assembly step, kept in the build folder and
removed when the document lands. Sections are written independently by
design — that is what lets each one be checked against source without
the checker holding the whole document in its head — and the cost of
that design is paid here: identifiers, cross-references and section
numbers have to be made consistent in one pass, by one reader.

Nothing in this file is normative. It records decisions so that the
assembly is not a series of small judgement calls made twice.

## 1. The identifier convention, decided

The sections disagree, so one convention wins. Three kinds of thing get
identifiers in this document, and each gets its own form.

**Inherited invariant families keep their exact identifiers.** `D1`,
`N3`, `Q1`, `S10`, `B5`, `P1`, `U1`, `V4`, `A4`, `K3`, `E1`, `X2` and
the rest. This is not a style preference: the sealed generation method,
the validation method and the test suite cite these by name, and a
document that renames them silently breaks every citation pointing at
it. An inherited invariant that this version widens still keeps its
identifier — `D1` binds eleven formats instead of six and is still
`D1`.

**New invariants join a family.** Version 6's own checkable rules
extend the family that owns their subject: `T1`–`T5` for the
time-of-day role, `LT1`–`LT2` for long-tail labels, `AF1`–`AF4` for
affixed numbers, `RM1`–`RM2` for the resolution mix. A new family is
coined only where no existing one owns the subject.

**Everything else takes a plain `C6-` NUMBER**, in one sequence over
the whole document. Prose rules, definitions, role descriptions and
statements that are not checkable invariants.

**No `C6-` letter identifiers, anywhere.** `C6-N3`, `C6-V4`, `C6-S13`,
`C6-PUB`, `C6-ARG`, `C6-GRAMMAR`, `C6-COMPLETE`, `C6-FKM`: every one
of these existed only to name the rule it superseded, under a
convention this version abolishes (plan amendment A-P4-11). A rule that
had a letter keeps the bare letter; a rule that did not takes a number.

### What must be renamed at assembly

| written as | becomes | where |
|---|---|---|
| `C6-COMPLETE` | the next free `C6-` number | `s1.md` |
| `C6-GRAMMAR` | a `C6-` number | `s45.md` |
| `C6-ARG` | a `C6-` number | `s45.md` |
| `C6-NG1` … `C6-NG18` | `NG1` … `NG18` | `s45.md` |
| `C6-PUB`, `C6-PUB-A`, `C6-PUB-B`, `C6-FKM` | already renumbered `C6-49` … `C6-53` | `r6.md` |

### The one real collision, and its repair

`s45.md` numbers the 41 note forms in five lettered groups — `A1`–`A6`,
`B1`–`B10`, `C1`–`C2`, `D1`–`D19`, `E1`–`E4` — one group per surface
the form is sent to. Those are catalogue labels rather than invariants,
but **four of the five letters are already invariant families in this
same document**: `A` is the axes family, `B` the shared label shape,
`D` the datetime family, `E` the empty role. A reader meeting `B5` or
`D1` would have two rules to choose from, in one document, with no way
to tell which.

**Repair: the forms are numbered `NG1` through `NG41` in one sequence**,
and the five group headings stay as prose — "the six forms a producer
sends to `publication_notes`", and so on — because the grouping is the
shipped producer's convention rather than a rule, and the publication
guard explicitly declines to check which form stands at which path.

## 2. Section numbering

Sections were written against version 4's numbering so each author had
a stable base. The assembled document renumbers once, in reading order,
and every internal cross-reference is repointed in the same pass. Four
sections carry explicit placeholders where an author knew they were
pointing at a section somebody else was writing; those are listed in
the per-section notes and must all be resolved.

## 3. Rules whose placement two authors both declined

Each of these was left deliberately unwritten by one author and flagged,
so the assembler places it exactly once. Placing it zero times is the
failure this list exists to prevent.

- **Label spelling variants** (version 4 §7.4): flagged by the label
  roles author as possibly belonging to a later additions section.
- **Multiplicity parity** for `free_text` and `numeric_unrepresentable`
  (version 4 §7.2): flagged the same way by two authors.
- **`numeric_styles` in full** (version 4 §7.5): the numeric roles
  author transcribed the role's use of it and left the full
  specification for the additions section.

## 3A. Two sections have TWO independently verified versions

An earlier run was thought lost to an API error and was relaunched;
the first run then finished after all. The result is that two sections
exist twice, each written and checked by a different pair of readers
who never saw each other's work:

| section | versions | verifier item counts |
|---|---|---|
| the numeric roles | `r4a.md`, `r4a_alt.md` | 22 and 15 |
| `time_of_day` | `r5b.md`, `r5b_alt.md` | 14 and 22 |

**This is worth more than the duplication cost, and the assembly takes
the UNION rather than picking one.** Two independent checks of the same
draft agree on the substantive question and disagree about what else
they noticed, which is exactly the shape that makes a union sound. The
agreement worth recording: both numeric-roles verifiers independently
rejected a FIFTH bound on the pooled fraction census and reached four,
reading amendment A-P4-8's condition 4 over its own defined quantity at
a total of zero. That reading is now confirmed twice and stands.

Items found by only ONE of the two and therefore easy to lose:

- **`r4a_alt` alone** found that the section told a loader author that a
  null endpoint suspends invariant Q5 entirely, while the shipped
  loader refuses a document with a null endpoint, three or more values
  in the statistics, and no skew. Two implementations following the
  text and the code would refuse different documents. The code is
  right.
- **`r4a_alt` alone** found a transcribed rule that changed its
  addressee: version 4 states an obligation on the rung ENVELOPE — it
  must be tight enough that a mutant collapsing the interior rungs
  FAILS it — and the transcription turned it into a remark about
  twins, dropping the obligation the validation method's mutation set
  is sized against.
- **`r4a_alt` alone** found invariant AF7 extended past its source: AF7
  puts in place of ONE count on the affixed role, and the transcription
  substituted four. It also declares a real gap nobody has settled —
  whether Q9's denominator and Q2's subtrahend on `affixed_number` are
  `n_present` or `n_affixed`. **The affixed-number section must settle
  that, and it is the one open question this build has raised that no
  artifact answers.**
- **`r4a` alone** found five invented range cells in a key table that
  version 4 leaves blank, one of them stating an invariant WEAKER than
  the invariant does.

**The affixed-number role also exists twice**, as `r5a.md` (written
whole) and `r5a1.md` + `r5a2.md` (written in two halves by different
authors). Same treatment: `r5a.md` is the primary, the split pair is
the second opinion, and the assembly takes the union.

### The open question is SETTLED, and not by a guess

This build raised one question no artifact answered: on
`affixed_number`, does invariant Q9's denominator and Q2's subtrahend
read `n_present` or `n_affixed`? The two versions answered it
differently — and version 4's own key definitions settle it. `n_used_in
_statistics` is "how many present cells the statistics were computed
from", `n_left_out_of_statistics` is "how many present cells were not",
`numeric_share` is "the share of present cells whose writer meant a
number", and Q9 says "computed as a share of the present cells".

**So `n_present` and `n_rows` are read unchanged on this role**, and
the core substitution reaches only the three numeric-looking census
counts. The reason is worth keeping beside the rule: under the
`n_affixed` reading a straggler cell wearing no affix pair falls into
NEITHER `n_used_in_statistics` nor `n_left_out_of_statistics`, so both
keys would silently answer for a narrower population than their own
published meanings — a fact that reads one way and is computed
another, which is the defect this contract exists to make impossible.

Two further corrections came with it. **X2 is not withdrawn from this
role**: the four universal census counts still close over the CELLS
here as on every role, and the core census AF4 stands BESIDE X2 rather
than in place of it. And **Q10 is part of the substitution**, which is
what makes it reach three counts rather than one: on a ninety-of-a-
hundred milligram column, the un-substituted Q10 reads `10 <= 0` and a
conforming document is refused.

## 3B. Two conflicts settled at assembly, with their grounds

**`clock_form` is EXACT-OBSERVABLE.** Two written sections gave one key
two dispositions — `r5b.md` and the old delta say EXACT-CONTROL, the
disposition matrix says EXACT-OBSERVABLE — and the format allows a
fact exactly one. The evidence settles it without an owner ruling.
EXACT-CONTROL means "a metadata or dispatch decision a CSV cannot
evidence"; a CSV plainly can evidence which clock form its cells wear,
since `09:20` and `09:20:00` are different bytes. And the plan's own
validation section lists "the one form" among the time-of-day checks
that RE-DESCRIBE the written twin, which is EXACT-OBSERVABLE's
evidence route by definition. **`r5b.md` takes the matrix's answer.**

**The SUM identity widens, and it needed a plan amendment (A-P4-12).**
The disposition matrix wrote the identity over judged-pass-sourced
cells while three other places — `s5.md`, the old delta, and the
ratified plan itself — wrote it over stand-in-sourced cells. The
matrix is right and the others widen. The reason is arithmetic: the
reproduction rule leaves a spelling blank when EITHER judged pass put
it there, so the twin writes four pools blank and the narrow identity
names three. On a column carrying judged calendar placeholders a
validator would have reported a failure against a correct twin. The
`missing_by_source` exception beside it widens the same way.

## 3C. The checks are mechanical now, and they found two more collisions

`tools/spec/check_assembly.py` collects every identifier each section
DEFINES and every one it CITES, and reports duplicates, unresolved
citations, surviving delta framing and `C6-` letter identifiers. It
exists because the first collision this build found was found by
READING, which was luck: a document this size has more identifiers
than a person checks reliably, and the failure it produces is the worst
kind — two implementations obeying different rules while both believe
they are obeying the text.

It found two collisions on its first run that no reader had noticed:

- **`D5` is defined twice** — the datetime family's invariant D5, and a
  note form named `D5` in the grammar section. This is the collision
  section 1 predicted from the lettered form groups, now confirmed by
  measurement rather than by argument. The `NG1`–`NG41` renumbering
  fixes it.
- **`C6-54` is defined twice**, by two sections that never saw each
  other — one for a completeness rule, one for the stand-in pass. Two
  authors reaching for the next free number independently is exactly
  what a single renumbering pass at assembly is for, and exactly what
  no author could have prevented alone.

**The exemption is auditable.** A paragraph explaining WHY the document
is self-contained has to name the mechanism the rest of the document
forbids, and no sentence test separates that from a rule being pointed
at. So the author marks it in the text — `<!-- framing-ok: ... -->` —
where a reader meets the mark beside the words it excuses, and the
mark dies at the next blank line so an exemption cannot spread down a
document by being forgotten.

Unresolved citations are expected while sections are still being
written; they are forward references to sections not yet delivered.
The check is a gate only against the ASSEMBLED document, where every
one of them must resolve.

## 4. Standing checks before the document is called finished

1. **Every enumeration is written out, with its count stated beside
   it**, and the two agree. The counts: 13 roles, 13 statistical types,
   11 formats, 4 resolutions, 6 time precisions, 2 clock forms, 6
   absence classes, 23 vocabulary members, 17 settings keys, 41 note
   forms, 6 numeric styles, 5 declaration-record keys.
2. **No delta framing survives.** No "supersedes", no "carried", no
   "unchanged from version 5", no "as version 4 has it", and no rule
   referenced by identifier without being stated somewhere in this
   document.
3. **Every cross-reference resolves** to a clause that exists here.
4. **Every identifier is unique.** One pass over the whole document
   collecting identifiers and asserting no duplicates — the collision
   above is what this check exists for, and it was found by reading
   rather than by a check, which is not a method that scales.
5. **The batteries gain the version 6 enumerations**: the disposition
   registry and the claim inventory pin exact lists, and amendment
   A-P4-11 makes extending them part of the price of the rewrite.
6. **The scanner sees the file.** Decontamination only reads tracked
   files, so a section is scanned after `git add`, never before.

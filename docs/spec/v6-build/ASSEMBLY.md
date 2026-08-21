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

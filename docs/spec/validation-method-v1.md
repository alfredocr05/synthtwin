# Validation method v1 — measuring a written table against a description

**Status:** revision 0, written before any validator code exists, under
the Phase 3 plan (`docs/plans/phase-3-product.md`), which governs on
every conflict. **Not ratified.** This is the third of the phase's
artifacts and the fifth governing document under the disposition seal.

**What this document fixes, and what revision 1 owes.** Revision 0
fixes the MEASUREMENT and the OBLIGATIONS: where a verdict comes from,
which facts are checked and at what grain, which are not checkable and
why, what a report may say out loud about a file nobody promised was a
twin, and what makes a check non-vacuous. Where the Phase 2 contract
says what a published fact MEANS and the Phase 2 method says how the
twin WRITES it, this says how a reader checks that the writing met the
meaning.

**It does not yet carry the two artifacts that make it an oracle**
(review item P3-C1-F5), and it says so rather than implying otherwise:
the COMPLETED entry table — every (fact, predicate, subcheck) row with
its kind and its named red case — and the report's normative byte
layout. Without those, two conforming validators could differ, and each
could then register its own fixtures as its own oracle, which is the
failure this project names by name. Both land in revision 1, written
beside the implementation and reviewed before the implementation is
ratified; the shipped tables are checked against this document, never
the other way round.

**What it does not fix.** No envelope of its own: every bound an
APPROXIMATED fact is checked against lives in
`docs/spec/generation-method-v1.md` G12 and is CITED here, never
restated, so the two can never drift apart. No cross-column check of any
kind: this version carries none, because the profile publishes none.

---

## V1. The boundary, the inputs, and what validation may touch

**V1.1 Two inputs, and nothing else.** The profile document, through the
same strict loader the generator uses (`contract.load_profile`, no
second loader and no relaxed mode), and one measured CSV. The generation
report is NEVER read: every fact about what the twin was allowed to do
is recomputed from the profile alone (V4), so no prose is an input to a
verdict.

**V1.2 The measured file may be anything.** Nothing distinguishes a
twin's path from a real table's, and a person will one day point this
command at the wrong file, or at the very table the profile describes.
The method is written for that: every rule below holds whatever the file
turns out to be, and V5 is the rule that keeps it safe to exist.

**V1.3 What validation writes.** One file, the quality report, through
the write transaction in its one-target form. Validation never writes,
moves, truncates or re-encodes the measured file or the profile, and the
report may not resolve onto either of them by path, by resolved path, by
link, by alias, or by a substitution between the check and the write.

**V1.4 What validation never imports.** The generation module. The
corner classifier of V4 is independent code written from this document,
and a validator that called `plan_generation` would share every planner
defect with the generator it is checking — which is the one thing a
second opinion may not do. No random number generator is constructed or
consumed anywhere in the validate path.

**V1.5 The reading is derived from the profile, never guessed.**

- The header is present exactly when `source.header_source` says the
  names came from the file. A twin whose names were generated is read
  first-row-as-data. The profiler's automatic header detection is never
  invoked here.
- The expected column count, and the expected names where a header
  exists, are known before the first byte is read.
- A profile publishing `n_rows: 0` leads to the degenerate forms of V6.4,
  which the profiler's own reader refuses and this one accepts.
- Every other reading refusal the profiler catalogues is reachable here,
  in the parameterized form of V9.

---

## V2. The measurement: re-describe, then compare

**V2.1 The measurement is the profiler's own.** The validator builds a
description of the measured file with the SHIPPED producer — the same
role rules, the same fold, the same parsers, the same exact-fraction
quantiles — and compares that description to the one it was given. This
is what the contract's EXACT-OBSERVABLE means in as many words:
"recounted from the written twin CSV, independently of the generator's
own bookkeeping". Re-implementing seventy-two recounts beside the
producer's would be a second implementation of the profiler and would
drift from it; running the producer is the only way the recount is the
same measurement the description was made with.

**V2.2 The settings it re-describes under** are the profile's own,
field by field, exactly as the Phase 3 plan's P3-D3 table fixes them.
Every classifier and publication threshold is read from the profile's
`settings`; the two declaration tuples are EMPTY, because the contract
deliberately does not record declared spellings; `forced_identifiers`
is applied, so a declared identifier is described as one; and the read
mode comes from `source.header_source` rather than from any settings
key. A sixteenth key, or a key skipped, is a defect in the validator.

**V2.3 The kept set, derived from the profile** (Phase 3 plan owner
decision 8, as amended). A twin can validly hold a spelling the
profiler would otherwise read as an absence, by three published routes,
and all three are recovered:

- every key of every published level's `variants`, as an exact
  spelling;
- every `sentinel_verdicts` candidate whose `reason` is exactly
  `kept_by_you`, matched at the profiler's own declaration-matching
  identity — numeric identity for a numeric candidate, never a byte
  comparison;
- every published `levels[].label`, at the FOLDED identity: a measured
  cell counts as data when its trimmed, case-folded form equals a
  published label's, which is the producer's own pooling rule.

**V2.4 And the kept set governs only what PRINTS, never a verdict.** On
the check side an absence is BLANKNESS, by the contract's own rule for
twins: every absent cell is written as an empty field, so `n_present`,
`n_missing` and every count that depends on them are measured from
blank and non-blank cells alone, with no sentinel or declaration
machinery anywhere in the verdict path. No gap in the reconstruction
can move a verdict; the worst it can do is withhold a measurement that
could have been printed, which is the safe direction.

**Which of V2.1 and V2.4 governs where they disagree, stated because
they can** (review item P3-C1-F4). The producer reads a cell equal to a
built-in missing marker as an absence, and residual R-P2-13 records
that a generated numeric value can BE such a text — so a conforming
twin's re-description can show an absence where the twin holds a
present cell. **V2.4 governs the verdict: present and missing are
counted from blank and non-blank cells, and the re-description's own
absence classification is not consulted for them.** Every count that
depends on presence is taken the same way. **And presence is not two counts alone** (review item P3-C2-F2): which
cells are present decides which cells a style map, a ladder or a
distinctness count is taken over, so EVERY measurement whose input is
the set of present cells is taken over the blank/non-blank split too,
and the re-description's own absence classification is consulted for
none of them. V2.1's re-description governs what does not depend on that
split — which role a column reads as, which label a value folds to, how
a cell is spelled — and it governs the disclosure gate of V5, where a
collision can only move a column toward MORE withholding, never toward
printing more. The two rules therefore never decide the same number: one
owns which cells are counted, the other owns how they read.

---

## V3. The entry table: what is checked, at what grain, in three kinds

**V3.1 An entry's identity is the triple (registry fact, profile
predicate, subcheck).** The registry fact is the (group, field) the
disposition registry carries, and the registry stays the authority on
its class. The profile predicate is the condition on the loaded profile
under which the entry applies — `always` for most; the named ones are
`header-written`, `zero-rows-headerless`, `zero-rows-headered`, and the
four corner predicates of V4. The subcheck is one obligation at the
finest grain the contract governs.

**V3.2 The subcheck grain, stated so it cannot be quietly coarsened.**
Each of the eleven percentile rungs separately, the two ends exact and
the nine interior rungs each against its own window. Each published
style key. Each published level with its count, its `variants` map and
its `variants_withheld` multiplicity map. Each offset key and each of
the two endpoint offsets. Each length and word extreme. Each
absent-cell obligation. Each byte-level rule of V6.

**V3.3 Three kinds, and the partition is total over OBLIGATIONS.**

- an **executable subcheck** produces a verdict, and V8 binds it: it
  must carry a registered, named way to fail;
- a **listing entry** is an obligation the matrix itself says cannot be
  checked from a CSV — every REPORT-ONLY fact, the EXACT-CONTROL
  remainder that a CSV cannot evidence, and the structural facts of the
  zero-byte form. It produces no verdict, appears in the report's
  NOT-CHECKABLE census, and its failure mode is that census: removing
  its line is red against the report's exact-shape and golden tests;
- an **input-side entry** is a fact whose whole obligation lives on the
  profile — every LOADER-ONLY fact, and the profile-side membership
  rules of the STRUCTURAL containers. The contract says these impose no
  output obligation, so they may neither carry a verdict nor be listed
  as an unverified twin fact; the strict loader the validator already
  runs is what settles them, and the projection test asserts each is
  bound to a loader refusal or a structural loader rule rather than
  silently absent.

Totality is over obligations, not over facts: one fact may contribute
entries of more than one kind. `columns` contributes its profile-side
membership rule as an input-side entry AND its twin-side order rule —
that the list order IS the CSV's column order — as an executable
subcheck, which is the contract's own split. No obligation may be
unbound, double-bound, or bound to the wrong kind.

**V3.4 No vacuity, in either direction.** No executable subcheck may be
unable to fail, and no listing or input-side entry may be presented as
a check. Those are the two ways vacuity enters and both are refused by
name.

---

## V4. The corners: an independent classifier

**V4.1 What a corner is.** A condition on the profile alone under which
the ratified plan names a lesser outcome for some fact — so a twin that
does not carry that fact is conforming, and a validator that called it
MISSED would be wrong. There are exactly four corners, and each is a
predicate over published numbers (this count is the CORNERS' own and is
unrelated to the number of G12 refusals, which method G12 fixes):

- **identifier-infeasible** (owner decision 6): a declared identifier
  whose published length range cannot supply `n_present` distinct
  values. Then `n_distinct`, `n_distinct_folded` and
  `n_distinct_by_occurrences` are REPORT-ONLY for that column, and
  nothing else is.
- **datetime-offsets-withheld** (P2-D9): a datetime column whose
  `utc_offsets` map is the single `(withheld)` key. Then `utc_offsets`,
  both endpoint offsets and `datetimes_read_at` are REPORT-ONLY, and
  the two ends are not.
- **label-variants-short** (P2-D6): a label column whose published
  variants and withheld-variant multiset together cannot supply the
  published raw `n_distinct`. Then raw `n_distinct` falls to the G12.7
  envelope.
- **numeric-spellings-short** (P2-D6): a numeric column whose permitted
  spellings cannot reach the published raw or folded distinctness. Then
  those fall to the G12.8 envelope.

**V4.2 The classifier is written from this document, not imported.**
The generator decides the same question from its own text; the two are
compared in the suite, over every producer-battery description and every
frozen conflict case, and any disagreement is red. A shared design error
now needs the same mistake written twice from two texts.

**V4.3 The G12 refusals are NOT corners.** They refuse GENERATION,
so no conforming twin exists for such a profile at all. A validate run
on one is a catalogued REFUSAL (V9), never a verdict and never a pass —
treating them as corners would launder an impossible obligation into a
passing report.

---

## V5. The disclosure gate: what a report may say about the measured file

**V5.1 The rule.** The quality report may state about the measured file
only what `synthtwin profile`, run on THAT FILE under the profile's own
settings, would publish about it.

**V5.2 Why the submitted profile's floor is not the envelope.** The
producer routes a two-valued numeric-looking column to a label role
BEFORE it reaches the numeric path, and withholds both labels when they
sit below the floor. A crafted numeric profile would walk a naive
validator straight past that routing and print the measured mean of a
column whose every published fact the producer would have withheld. So
the gate consults the FILE's own description, which V2.1 already builds.

**V5.3 What the gate governs: the verdict as well as the value.** A
within-bound or missed line stated against a candidate value is itself a
measurement-derived statement, and repeated candidate profiles would
binary-search a number the file's own description withholds. So where
the gate closes over a subcheck, its verdict is WITHHELD: neither the
measurement nor its outcome is shown, one fixed sentence says the file's
own description would not publish what this check measures, and the
count of withheld subchecks appears in the census. That the column
classifies differently than the submitted profile expects is itself a
fact the producer publishes about any file — the role axis — so the
signal stays inside the envelope.

**V5.4 What may be printed, exactly.**

- No string from the measured file, ever — not in the report, not on
  screen, not in a refusal. Every label named in the report is the
  profile's own published label.
- Whole-column counts print exactly: rows, present, missing,
  distinctness. The producer publishes these for a column of any role.
- A numeric summary prints exactly only for a column the FILE's own
  description sends down a numeric path.
- A per-label, per-style or per-offset measured count prints exactly
  when it clears the floor. Below the floor the line states only what
  omission from the file's own description already publishes: not held
  at its published count, the measured count below the publication
  floor and possibly zero, withheld. The exact sub-floor number never
  appears beside a name. What may print namelessly is exactly what the
  producer publishes namelessly, which differs by kind: the suppressed
  count list for labels, and only the single pooled total for styles
  and offsets.
- An unpublished-content line says the file holds values the
  description does not publish, in N rows, with N floor-governed the
  same way, and never says what they are.

**V5.5 On the ordinary case the gate does not close.** When the measured
file IS the twin built from this profile, Phase 2's owner decisions 5, 8
and 10 give it back the same types, the two descriptions agree on every
role, and everything prints. The withholding bites on a mismatched
file, which is where it must. **The one exception is named rather than
claimed away**: residual R-P2-13's missing-marker collision can move a
column's re-described role, and there the gate may withhold on a twin
that is otherwise conforming. It costs detail in the report and never a
verdict (V2.4), and the green battery of V8.4 asserts zero withheld
verdicts over fixtures built clear of that corner, with the corner
itself pinned by its own case.

---

## V6. Verdicts, byte rules, and exit status

**V6.1 The five verdicts.** HELD (the exact obligation was met);
WITHIN-BOUND (an APPROXIMATED fact inside both ends of its cited G12
envelope); AUTHORIZED-DEVIATION (a lesser outcome the ratified plan
names for this profile's corner, shown with the exact plan passage or
owner decision that authorizes it, taken from the registry's own
citations); WITHHELD (V5.3); MISSED (an obligation the ratified matrix
sets that the file does not meet). Listing entries carry no verdict and
appear only in the NOT-CHECKABLE census.

**V6.2 Byte rules, each an executable subcheck.** UTF-8; no byte-order
mark; LF line endings; a terminal newline; the row count; the column
count and order; the header present exactly when
`source.header_source` says so and its names read back byte for byte,
including the quoted U+FEFF exception.

**V6.3 The numeric-style identity** is contract 7.5.7's, clause by
clause, with each published count a floor.

**V6.4 The degenerate zero-row forms** (Phase 3 plan owner decision 7).
A zero-row profile whose names were generated expects exactly zero
bytes; one whose names came from the file expects the header line and
its terminal newline and nothing more. The expected byte form IS the
executable subcheck, and the structural facts that zero bytes cannot
evidence — how many columns the schema has, their order, their
positions — are listing entries for exactly that predicate, with one
plain sentence in the census.

**V6.5 Exit status.** 0 when validation ran to completion and no
subcheck MISSED; 3 when it ran to completion and at least one did; 1 on
a catalogued refusal, which is validation that could not run at all; 2
on a usage error. Automation therefore tells a bad twin from a file it
never evaluated without reading prose.

---

## V7. The quality report

**V7.1 Order.** The verdict summary first, then the honest bounds, then
the fact-by-fact detail, then the analyst-expectations section, then the
handling rule. Every interpolated string passes the display boundary
once, label variants included. The report's normative byte layout and
its golden hashes are revision 1's, with the completed entry table; this
revision fixes the order and the obligations, not the bytes.

**V7.2 The summary is generated from the census alone.** It states how
many subchecks HELD, how many landed WITHIN their stated windows, how
many were AUTHORIZED-DEVIATIONS with their citations, how many were
WITHHELD, how many MISSED, and how many obligations were NOT CHECKABLE
and why. There is no sentence of the form "every published fact was
found": on a profile with corners or approximated facts it would be
false by construction, and it cannot be written from these verdicts at
all. A pass means **no checkable obligation was missed**, with the other
counts standing beside it and never folded into it.

**V7.3 The limits it carries, every run.** No cross-column structure was
validated because none is carried; rows independent and the grain
undescribed; numbers computed on the twin are not research results; and
the verdict-scope sentence — a passing report is not a fitness verdict
for any analysis, it validates nothing the profile does not publish, and
it cannot tell a synthetic file from a real one, because nothing in a
CSV proves provenance.

**V7.4 The analyst-expectations section** names what this version checks
(single-column shares of published labels, distribution ladder positions within
stated windows, spread and shape summaries within stated windows,
missing-value counts, value-format read-back) and what it does not (any
target tying two columns, and any target about row grouping), saying
that those need cross-column structure this version deliberately does
not carry, and that carrying them is later work with its own plan and
its own contract change. It promises no version, no slot and no date.

**V7.5 The fourth artifact.** The report states measured facts about a
real-derived file, so it is real-derived material exactly as the
profile, the twin and the generation report are, and it says so.

---

## V8. Non-vacuity

**V8.1 Every executable subcheck carries a registered red case**: a
perturbation of a valid twin that must produce MISSED — per rung, per
style, per level, per variant map, per offset, per extreme, per
structural rule. Wrong count, moved cell, re-cased label, re-spelled
number, shifted date, truncated file, re-encoded bytes, reordered
columns, edited header, injected byte-order mark, nonempty bytes in the
zero-row form.

**V8.2 A red case NAMES the subcheck it must fail**, and the battery
asserts that THAT subcheck reports MISSED. Other subchecks failing
alongside is fine; a perturbation caught only by a neighbour — the mean
tripping while a hard-coded rung check sleeps — is a red battery,
because the named subcheck did not do its job.

**V8.3 The coverage identity** walks the shipped executable-subcheck
table and asserts every entry has at least one registered, named,
passing red case.

**V8.4 The green direction.** Producer → generator → validator over the
every-role fixture and every frozen conflict case: zero MISSED and zero
WITHHELD, and on the conflict cases the AUTHORIZED-DEVIATION verdicts
must APPEAR with their citations.

**V8.5 The vacuity floor.** A counted floor of distinct red-case classes
per disposition class, so the battery cannot rot into one shared
perturbation.

---

## V9. Refusals

Validation refuses, rather than returning a verdict, when it cannot run:
the measured file missing, unreadable, a folder, or not readable as CSV;
the profile failing the strict loader; the profile meeting any G12 refusal
(method G12 fixes their number and their names, and this document
follows it rather than restating a count), whose message mirrors the
generation refusal and adds
that whatever the file is, it cannot be that profile's twin; the quality
target already present without `--replace`; the target resolving onto
either input; and memory exhaustion.

**Every refusal reachable from validation names positions, never
values** — which column, which row — wherever the profiler's own form
would quote measured content. On this path the file may not be the
person's own table, and refusal text travels as freely as a report does.

A structural mismatch is NOT a refusal: a wrong column count or a wrong
name is a MISSED verdict with a plain explanation, because the report is
the product even when the news is bad.

---

## V10. Determinism

The quality report's bytes are a fixed function of (the profile bytes,
the measured file's bytes, the synthtwin version) on one platform under
the locked dependency set — the same scope D12 gives the twin.
Cross-platform agreement is verified empirically by golden report hashes
on every CI cell, exactly as the twin's are. Validation consumes no
randomness, and the offline scanner's policy asserts that the validate
closure cannot reach one.

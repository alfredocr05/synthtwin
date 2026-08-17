# Phase 3 — the end-to-end product: validate, the quality report, and the first release

**Status:** revision 4, 2026-08-12 — **RATIFIED at plan review round
5**, after rounds 1 (REJECT, eleven items), 2 (REJECT, five), 3
(REJECT, three) and 4 (REJECT, two blocking and one condition), every
item repaired and its repair verified by the round that followed;
round 5, the final abbreviated verification, replayed the round-4
counterexamples against the repaired mechanisms, verified all three
closed, and returned RATIFY with no conditions. The closure tables
sit in the review record at the end. This is the ratified design
Phase 3 is built from. The design was first written as a
maintainer-private outline and put through four adversarial review
rounds on 2026-08-12: rounds 1–3 rejected it with seventeen, nine and
five items, every one repaired and re-verified; round 4 verified all
repairs closed, raised no finding, and ratified the outline with three
bounded drafting conditions, each satisfied in this document where its
section says so. The eight owner decisions of P3-D0 were taken on
2026-08-12. This plan's own review record is at the end and governs;
the plan is the fourth governing document under the disposition seal
from the commit that lands it.

**Charter (CLAUDE.md):** profile, generate, and validate through one
zero-code CLI; earliest possible first PyPI release. Phase 1 residual
R3 — the project wheel's own digest is not verified in the documented
institutional install, and closes when Phase 3 publishes one — closes
here.

**Scope:** one new command path — `synthtwin validate <profile>` —
that measures a written twin against the profile that generated it and
writes the plain-language quality report; the command teaching chain
that makes profile → generate → validate a zero-code workflow; the
repair of the two OPEN defects in the disposition registry; the
repository's move to public with its deferred controls applied; and
the first PyPI release, executed against the release requirements
Phase 0 D10 and SECURITY.md already ratified.

**Non-goals:** no cross-column validation and no relationship content
(Phase 5) — the `validation_targets` slot stays `null`, and the check
inventory derives from published per-column facts and the ratified
disposition matrix, never from a manifest slot; **no profile WIRE
change — `profile_version` stays 4 (AMENDED, once, by A-P3-27 — read
the note that follows this paragraph)**, the validator consumes v4
exactly as shipped, no new published fact, no producer change (the
twin-side pooled-cell sentence of contract 7.5.7 may be amended under
owner decision 1's repair, by counted re-seal — that sentence governs
what the GENERATOR writes, not what the profile carries, so the wire
and the version are untouched); no new
roles or subtypes (Phase 4); no row-count override; no new input or
output formats; no machine-readable verdict file (the refusal/verdict
exit-code split of P3-D2 is the machine channel this phase ships); no
chaining command (owner decision 4); no standalone build (Phase 6).
The generator's outputs at a fixed (profile, seed, version) change
only if the OPEN-defect repairs of owner decision 1 require it, and
any such change is a changelogged regeneration event under D12.

**The wire non-goal is amended, once, and only it** (owner ruling
2026-08-17, amendment A-P3-27, written out in full where the
amendments stand). The profile wire DOES change in this phase:
`profile_version` becomes 5 and the format is
`docs/spec/profile-contract-v5.md`. Every other non-goal above holds
exactly as written — no cross-column validation, no relationship
content, the `validation_targets` slot still `null`, no new roles or
subtypes, no row-count override, no new input or output formats, no
machine-readable verdict file, no chaining command, no standalone
build. Why the change was taken inside this phase rather than left to
the next one is priced at the amendment: after the first release the
same change costs strangers a migration, and today it costs a line in
the changelog.

## Sequencing — artifacts, in order

1. **This plan**, ratified through adversarial review before anything
   below it exists. Landing it turns the registry guard's exact-list
   assertion red (the guard enumerates `docs/plans/` file by file), so
   the plan lands together with its seal entry, the `GOVERNING`
   addition, and the guard's updated list. Stated honestly: the tree
   test proves the STATE — an unsealed governing document is visible
   at every CI run — not the history; same-commit landing is
   procedure, and the phase-close audit confirms each governing
   document's introducing commit carried its seal.
2. **The OPEN-defect repairs** (owner decision 1): the first
   implementation work of the phase, bounded in P3-D8.1, each closing
   with its OPEN line deleted and its battery green.
3. **`docs/spec/validation-method-v1.md`** — the complete normative
   check inventory (P3-D2). Blocking before validator implementation
   under the standing process; it joins the seal at its own landing,
   making the governing set five. If the owner overrides sequencing
   (as in Phases 1 and 2), the spec is still WRITTEN before code and
   the override is recorded by the same mechanism as those two.
4. **The implementation**, reviewed against plan and spec.
5. **Release execution** — the mechanical checklist of P3-D8, gated on
   an explicit owner go decision naming the commit digest it approves.

## P3-D0. Owner decisions taken for this phase

All eight were taken on 2026-08-12, on the outline's fourth review
round. They are recorded here in the project's standing convention:
the decision, its cost stated plainly, and what it buys.

1. **The two OPEN defects are repaired in code, first, and both block
   the release.** The registry carries two open defects — the pooled
   numeric-style remainder that a published decimal endpoint can
   contradict (P2-C5-F3 residue), and the declared-identifier
   whole-number corner at short lengths (P2-C5-F4 residue). The owner
   directed that both be FIXED, not amended away: each repair lands as
   code plus the method-specification amendment that states its rule,
   under a counted re-seal, and closes by deleting its OPEN line with
   its battery green. Where analysis shows two ratified bars genuinely
   exclude each other in the identifier corner — a whole-number
   spelling that must begin with a character the formula-context
   policy bars — the repair is the NAMED refusal the standing anchor
   reserves for descriptions no rule can satisfy, recorded in the
   amendment; never a quiet miss. If either repair changes twin bytes
   at a fixed seed, that is a changelogged regeneration event under
   D12. Neither obligation is lowered; the release gate (P3-D8) does
   not open while either OPEN line stands.
2. **The repository goes public at the commit that lands this plan.**
   The owner directed: "in the next commit, we go public." Concretely:
   the plan lands on the default branch while private; the visibility
   flip is executed immediately after, with SECURITY.md's own
   procedure — the eight deferred controls and fork-pull-request run
   approval applied and confirmed through the API at the moment of the
   flip, the active-control list re-verified at that same moment, and
   the two owner-personal attestations (recovery-code storage, no
   shared credentials) re-checked by the owner then. Every later
   Phase 3 commit rides the then-active rules: pull requests only, the
   aggregate gate required, self-merge only after green. What this
   buys: the open-source commitment becomes fact early, and the
   release preconditions that need a public repository (tag rulesets,
   the signed-tag demonstration) stop being deferred. The cost: review
   repairs move at pull-request speed from the flip onward.
3. **Phase 2 is closed by owner decision.** The Phase 2 record stands
   exactly as written — five code-review rounds, the fifth a REJECT,
   no further round authorized, neither the code nor either
   specification ratified by review. The owner accepts Phase 2 as
   built and closes it, by the same mechanism as the Phase 0 closure
   decision. Closure is an owner act, not a review verdict, and this
   plan never describes Phase 2 as review-ratified. The charter's
   phase ledger moves Phase 2 to complete-and-closed and Phase 3 to
   current in the commit that lands this plan (P3-D7).
4. **Three commands, no chaining command.** The generate invocation's
   ratified boundary (P2-D1) includes a red mutation at a post-write
   step reaching the reader, so `generate` may never read back the
   twin it wrote, and validation cannot run inside the generate
   invocation. Instead each command's success output teaches the next
   step in plain words. A chaining command can arrive in a later phase
   without contract changes.
5. **First release identity: version 0.1.0.** SemVer 0.x per Phase 0;
   signed annotated tag `v0.1.0`; CHANGELOG's `[Unreleased]` converts
   to `[0.1.0]` with the date. Trove classifiers stay omitted — the
   standard license classifier's wording collides with the
   decontamination manifest, PyPI functions without them, and the
   pyproject comment records why. Inherited and still NOT assumed:
   R-P2-1 (width facts for unrepresentable numbers) stays flagged for
   the owner, untouched by this phase.
6. **The read-boundary charter sentence is amended when the validator
   ships.** The charter says the profiler is the only code path that
   reads the real table. A validator reads a CSV by design, and
   nothing distinguishes a twin's path from a real table's, so the
   sentence becomes false the day validate exists. The owner accepted
   the amendment: the sentence becomes — the profiler and the
   validator are the only code paths that read a table, and the
   generator never reads any table, consuming only the profile — with
   the consequence disclosed beside it: the validator will measure
   whatever CSV it is pointed at, including a real table, and the
   disclosure gate of P3-D3 is designed for exactly that. The edit
   lands with the validator implementation, every surface carrying the
   old sentence moves in the same commit (the P3-D7 table), and the
   old wording joins the banned list then, not before, because until
   the validator ships the old sentence is still true.
7. **The degenerate zero-byte form: the byte form is the check.** A
   zero-row profile whose column names were generated validly yields a
   twin of exactly zero bytes, and zero bytes cannot evidence how many
   columns the schema has — twenty columns and one column write the
   same nothing. The owner ratified: the expected BYTE FORM of the
   degenerate case is itself the executable check (the file must equal
   the exact bytes the method fixes for this profile — empty for the
   headerless zero-row form, header plus terminal newline for the
   headered form; a nonempty or wrong-byte file MISSES), and the
   structural facts an empty file cannot evidence are NOT-CHECKABLE
   for exactly this case, listed as such in the census with one plain
   sentence. No generator byte changes, no domain exclusion.
8. **The disclosure gate runs declaration-blind, with the kept set
   recovered from the profile itself.** The gate of P3-D3 classifies
   the measured file under the profile's reconstructible settings and
   NO user-declared spellings, because the contract deliberately
   refuses to record them (`values_recorded: false` is an invariant —
   recording them was rejected as a disclosure widening, and this
   phase refuses to reopen it). Stated precisely, the two declaration
   kinds differ and the gate treats them differently:
   - **Declared-missing spellings** are genuinely unrecoverable AND
     genuinely absent from every twin — an absent cell is written
     empty (R-P2-2) — so the gate declares none, exactly.
   - **Kept spellings CAN appear in a twin**, by two published routes,
     and the gate derives both: a kept value published as a label
     carries its exact spelling in the level's `variants` keys, and a
     kept NUMERIC value is published through its `sentinel_verdicts`
     entry — the candidate spelling with the kept verdict — which the
     generator likewise writes as data. A gate with no kept set would
     read such twin cells as built-in missing markers and misclassify
     the very twin it must validate; plan review round 2 demonstrated
     this executably on a generated twin holding kept numeric
     markers, and round 3 found the third route: a level whose
     spellings all sit below the floor publishes empty `variants` and
     only the `variants_withheld` multiplicity map, and the generator
     INVENTS that level's spellings from the normalized parent label —
     so the invented cells fold to the parent and to nothing the two
     exact-spelling fields name. **So the gate derives its kept set
     from the profile itself, at the identity each entry carries:
     every `variants` key as an exact spelling; every
     `sentinel_verdicts` candidate whose `reason` is exactly
     `kept_by_you`, matched at the profiler's own
     declaration-matching identity — numeric identity for numeric
     candidates, never a byte comparison;
     and every published `levels[].label` as a FOLDED identity — a
     measured cell is data whenever its trimmed, case-folded form
     equals a published label's folded identity, which is exactly the
     pooling rule the producer itself applies.** The validation
     specification enumerates the exact fields and enum values; the
     set is derived entirely from the v4 document, so nothing new is
     recorded anywhere.

     **And the kept set governs only what PRINTS, never what
     verdicts** — the boundary that makes the last corner honest. On
     the check side, absence in a measured file is BLANKNESS, by the
     contract's own rule for twins: the generator writes every absent
     cell empty, so `n_present`, `n_missing` and every count that
     depends on them are recounted from blank and non-blank cells
     alone, with no sentinel machinery ~~or declaration machinery~~
     anywhere in the
     verdict path — ~~no reconstruction gap can move a verdict~~.
     **Two strikes, both by amendment A-P3-15 below, which states what
     is true in their place and nothing here may be re-derived from
     them: clause 2 strikes "or declaration machinery", because a cell
     is also absent to these counts when it wears a spelling the
     description ITSELF publishes as the source of its holes; clause 3
     strikes the last clause outright, because a gap in the
     reconstruction moved five verdicts on the table a description was
     written from.** What
     remains is a GENERATOR-side residual this phase inherits rather
     than creates: the method's R-P2-13 records that generated
     numeric values can collide with built-in missing markers when a
     file is re-profiled, and round 4 demonstrated the collision with
     a kept marker below the sentinel-publication floor, where no
     published field can name the spelling. For the disclosure gate
     that collision can at worst shift a column's classification
     toward the conservative side — more withholding, never more
     printing — so the leak direction is safe; the green battery's
     zero-WITHHELD assertion runs over the battery fixtures, and the
     R-P2-13 collision corner is named in the residual ledger
     (P3-D11) as the one exception, owned by the residual that
     already records it.
     **This is an owner amendment to the original decision** — which
     said reconstruct nothing — **taken 2026-08-12 when review proved
     the original breaks conforming twins**; the green battery of
     P3-D4 (zero WITHHELD on every twin validated against its own
     profile) is the executable proof the reconstruction suffices on
     the twin domain.
   For files that are NOT the twin — including the original table —
   the gate remains the profiler's default-declaration judgment
   augmented by the published spellings, and its divergence from a
   declaration-aware profiling is wider than a display difference: an
   undeclared spelling the original profiling removed before role
   selection is retained by the gate, which can shift the column's
   role and its statistics, not merely which counts print. No spelling
   is ever printed under any classification; the divergence is named
   honestly as residual R-P3-6.

## P3-D1. The validate command

- **Invocation:** `synthtwin validate <profile>`, with `--twin PATH`
  (default: the derived `<stem>-twin.csv` beside the profile),
  `--out-dir`, and `--replace`. Output: `<measured stem>-quality.txt`
  — the name derived from the file MEASURED, in the folder the
  description is in or the one `--out-dir` names — collision-free with
  every other file a run writes by construction. **This sentence read
  `<stem>-twin-quality.txt`, derived from the profile, until amendment
  A-P3-4** (2026-08-14, review item P3-V2-G); the ordinary run's file
  name is unchanged by the move, because the default measured file is
  `<stem>-twin.csv`. An existing target is refused without `--replace`,
  in the same shape as the generate refusal (R-P2-12 parity).
- **Inputs are exactly two files.** The profile, through the SAME
  strict loader — no second loader, no relaxation — and the measured
  CSV. The validator never reads the generation report: everything it
  needs to know about authorized corners is recomputed from the
  profile alone (P3-D2), so prose is never an input.
- **The read mode is derived from the profile, never guessed.** Header
  presence comes from `source.header_source` — a headerless twin is
  read first-row-as-data, never auto-interpreted; expected column
  count and, when a header exists, expected names are known before the
  first byte is read; and a profile publishing zero rows leads to a
  read path that accepts the header-only and empty-byte forms the
  generator validly writes, where the profiler's own reader would
  refuse them. The profiler's automatic header detection is never
  invoked on the validate path. Genuinely malformed files still meet
  catalogued refusals.
- **Validate refusals quote nothing from the measured file.** The
  reading refusals are already parameterized by artifact words; on the
  validate path they are further parameterized to name POSITIONS —
  which column, which row — never values, wherever the profiler's
  forms would quote measured content, because on this path the file
  may not be the user's own table and refusal text travels as freely
  as a report. An exact-shape battery covers every reading refusal
  reachable from validate and asserts no measured-file string appears.
- **Boundary.** The validate branch lazily imports the reader, as the
  profile branch does; the generate branch is untouched and its
  boundary battery must pass unchanged — the generate invocation
  remains provably free of the reader at every instant. New boundary
  obligations, each with a red mutation: the validate invocation never
  imports the generation module (the corner classifier of P3-D2 is
  independent code); validation never writes or mutates the twin or
  the profile — its only write is the quality report, through the
  transaction.
- **The write is one file, so the transaction is generalized.** The
  shipped transaction is two-files-or-neither; the quality report is a
  single artifact. The transaction gains a one-target form with the
  same working-name, rollback and refusal properties, a third
  `ArtifactWords` set — and a forbidden-target set carrying BOTH
  inputs: the quality report may not resolve onto the profile or the
  measured file by lexical path, resolved path, link, alias, or
  between-check-and-write substitution; each input crossed with each
  alias class is a test, extending the shipped same-file machinery
  from one guarded source to a set. The statement and opcode
  fault-injection measurement is RE-RUN against the generalized code,
  exactly as P2-D10 required when the transaction moved modules.
- **Determinism, at the ratified scope.** Validation consumes no
  randomness: no RNG import by any SYNTHTWIN MODULE in the validate
  closure, asserted by the offline scanner's policy (the numpy origin
  rules stay scoped to generation) and a red mutation; no draw from any
  random source in the process, asserted by a trap over every one of
  them with the whole command run at it; and no reach to the generation
  module, asserted in a fresh interpreter. **The scope of the first
  clause is named rather than left to "the validate closure", and the
  other two are new, under amendment A-P3-4** (2026-08-14, review item
  P3-V2-F-F2). Quality-report bytes are a fixed function of (profile
  bytes, the measured file's name, measured-file bytes, synthtwin
  version) on one platform under the locked dependency set — the same
  scope D12 gives the twin — with cross-platform agreement verified
  empirically by golden quality-report hashes on every CI cell,
  exactly as the twin's hashes are.

## P3-D2. What the validator checks: the inventory derives from the ratified matrix

**The identity scheme, fixed here** (outline round-4 condition B,
satisfied in this section). The validation-method specification
refines the ratified disposition matrix into a table of ENTRIES. An
entry's full identity is the triple **(registry fact, profile
predicate, subcheck)**:

- the **registry fact** is the (group, field) the disposition registry
  already carries — the registry stays the class authority;
- the **profile predicate** is the condition on the loaded profile
  under which this entry applies — `always` for most, and a named
  predicate where the matrix itself is conditional: header written or
  not (which routes `name` between recountable and non-evidencible),
  the zero-row degenerate case of owner decision 7 (which routes the
  structural facts to their byte-form check and NOT-CHECKABLE
  listings), the authorized corners of P3-D2's classifier, and the
  approximated fallbacks the matrix names;
- the **subcheck** is one obligation at the finest granularity the
  contract governs: each of the eleven percentile rungs separately
  (endpoints exact, nine interior rungs each against its own window),
  each published style key, each published level with its count, its
  `variants` map and its `variants_withheld` multiplicity map, each
  offset key and both
  endpoint offsets, each length and word extreme, each absent-cell
  obligation, each byte-level rule.

**Kind derives from the full identity, not from the disposition
alone.** Every entry is exactly one of three kinds, and the partition
is TOTAL over the registry:

- an **executable subcheck** — it produces a verdict, and the
  non-vacuity rule of P3-D4 binds it: it must carry a registered,
  named way to fail;
- a **listing entry** — an obligation the matrix says cannot be
  checked from a CSV under this entry's predicate (REPORT-ONLY facts;
  the non-evidencible EXACT-CONTROL remainder; the structural facts of
  the zero-byte case). It produces no verdict, appears in the report's
  NOT-CHECKABLE census, and its failure mode is the census itself:
  removing its line is red against the report's exact-shape and golden
  tests;
- an **input-side entry** — a fact whose whole obligation lives on the
  profile (LOADER-ONLY facts; the profile-side membership rules of
  STRUCTURAL containers). The contract says these impose no output
  obligation, so they can neither verdict nor be listed as unverified
  twin facts without making up an obligation the matrix refuses; their
  discharge is the strict loader the validator already runs, their
  failure mode is the loader battery that already exists, and the
  projection test asserts each is bound to a loader refusal or
  structural loader rule rather than silently absent. A STRUCTURAL
  fact that ALSO states a twin-side obligation — the `columns` list
  order that is the twin's column order — contributes that obligation
  as its own executable subcheck; the split follows the contract's own
  sentences.

No executable subcheck may be unable to fail, and no listing or
input-side entry may be dressed as a check — the two ways vacuity
enters, each refused by name. The shipped validator carries its own
entry table; one test asserts the table is
exactly the registry projection — same facts, same classes, same
authorized lesser outcomes, same kinds, the kinds derivable from the
registry's dispositions plus the named predicates, so nothing can be
re-decided in code — and a second asserts totality **over
OBLIGATIONS, not over facts**: every obligation the contract states
for a fact under an applicable predicate is bound by exactly one
entry; a single fact may therefore contribute entries of more than
one kind — `columns` contributes its profile-side membership rule as
an input-side entry AND its twin-side order rule as an executable
subcheck, which is the contract's own split — and no obligation may
be left unbound, double-bound, or bound to the wrong kind. The
zero-row predicate is itself two predicates, because the two valid
degenerate forms differ: the headerless zero-row profile expects the
empty-byte form, the headered one expects the header line with its
terminal newline, and each form is its own executable byte check with
its own listings. Every entry binds to a registry fact; drift in any
direction is red.

**Check classes, by disposition:**

- EXACT-OBSERVABLE: recounted from the written CSV using the
  PROFILER'S measurement primitives — the fold, the parsers, the
  exact-fraction quantile — never the generator's bookkeeping. This is
  the contract's own definition of the class, executed by a shipped
  command instead of only by the test suite.
- APPROXIMATED: measured from the CSV and checked against BOTH ends of
  the generation-method G12 envelopes. The method specification stays
  the single home of those bounds; the validation specification cites,
  never restates, each bound. Verdict WITHIN-BOUND or MISSED.
- EXACT-CONTROL: the CSV-evidencible subset only — header names when a
  header was written, column order, header presence per
  `source.header_source`, and the five per-column facts named in
  amendment A-P3-1 below. The remainder is a listing entry with one
  fixed census sentence.
- REPORT-ONLY: listing entries, named and never counted toward a pass.
- LOADER-ONLY and STRUCTURAL: input-side entries as above.

**Amendment A-P3-1 — five EXACT-CONTROL facts are executable, not
listed. This RAISES the obligation and is recorded rather than taken
silently.** The paragraph above was written naming three CSV-evidencible
EXACT-CONTROL facts. Implementation found five, and leaving the other
two as listings would have been the quieter sentence, so they are named
here instead. The five are `universal.position`, `universal.role`,
`universal.statistical_type`, `universal.quality_state` and
`universal.structural_role`. Each is genuinely evidencible from the
measured file: position by which column number the published name
stands at (headerless, by whether a column stands there at all), and the
three axes by re-describing the file with the profiler's own producer
and comparing the axis it assigns. Each carries a registered red case —
swapped columns for `position`, a rewritten column for `role`, a renamed
declared identifier for `structural_role` — so none of the five is a
check that cannot fail. `statistical_type` was already executable in the
shipped validator on the strength of this section's own type-read-back
sentence; the amendment regularizes it alongside the other four.

The deviation is one-directional by construction: it moves facts from
the listing side to the checked side, so a file that would have passed
under the literal reading cannot fail under this one for any reason
other than actually missing an obligation the profile publishes. The
owner may reverse it to the literal three-fact reading at any time; the
reversal would be a lowering, and so would have to be recorded here in
those words.

**Amendment A-P3-2 — five entries that could not fail: four of them
LOWER an obligation and two RAISE one, and each is named as which**
(2026-08-13, review items P3-V2-C-F1, F2, F3, F7 and F8). The charter's
rule is that a check that cannot fail is a defect and a passing report
must mean what it says. Round 2 of the validator review found five
executable subchecks the shipped validator filed against descriptions no
file of the published length could make them miss on. Two of them —
`universal.structural_role` and `universal.position` — are facts
A-P3-1 above moved from the listing side to the checked side, so
moving either back is a partial reversal of that amendment, and A-P3-1
says in as many words that such a reversal is a lowering and has to be
recorded here in those words. It is. **No file's verdict changes under
any of the four lowerings**, because no file could fail any of the four
entries; what changes is that the report stops counting them toward a
pass and says in its NOT-CHECKABLE census why nothing in a CSV settles
them.

1. **`universal.structural_role` becomes a listing entry, on every
   column. THIS LOWERS.** The axis says whether the person who owns the
   table declared the column with `--identifier`. The taxonomy computes
   it from that declaration alone — its own docstring says no value of
   the column is consulted — and the validator re-describes the measured
   file under the description's own declaration list (V2.2), so the two
   sides read the same word for every column of every description that
   declares no identifier, which is the zero-code default. Measured: 16
   runs across four fixtures and four whole-column rewritings, HELD
   every time. On the one suite fixture that DOES declare an identifier
   the entry could be made to miss, and only by renaming that column in
   the header — which `header.names` states outright and `position.at`
   states for that column, so the axis was a third copy of one piece of
   evidence. It is the EXACT-CONTROL remainder V3.3 already describes: a
   fact whose whole obligation lives on the description.
2. **`universal.position` becomes a listing entry on the FIRST column
   of a description whose names were generated, and nowhere else. THIS
   LOWERS.** The check has two failure branches and where there are no
   names to compare only one is live: the file stops before this column
   number. Nothing stops before the first column — a file carrying no
   columns at all is refused by the reader before any verdict exists.
   The second and later columns of such a description keep the check and
   still miss on a file that stops short, and every column of a headed
   description keeps it unchanged.
3. **`numeric.skew` becomes a listing entry on a description whose
   G12.3 window is the statistic's whole attainable range. THIS
   LOWERS.** Method G12.3 ends with a finite fallback: where the
   published ladder's own spread does not exceed the displacement the
   construction can produce, the skew bound becomes the range every
   sample of that many values lies in whatever they are. G12.3 is right
   to PRINT that — a wide bound tells a reader the ladder is too coarse
   to say anything about the shape — but a CHECK against it admits every
   file, and two of the six skew windows the suite's own fixtures draw
   are exactly it. The validator may not draw a narrower window of its
   own: the validation method's opening paragraph fixes that every
   APPROXIMATED bound lives in G12 and is cited, never restated, so a
   tighter envelope is a change to the generation method, made where
   that method is written and reviewed against the construction it
   describes. A description whose ladder does bound its shape keeps its
   skew check.
4. **`styles.canonical.<form>` becomes a listing entry where the
   published count of that form is not below the description's own row
   count. THIS LOWERS.** The ceiling P3-D8.1 ratifies is the published
   count, and the arithmetic is right: at most `p(s)` of the cells
   written in form `s` may carry anything but their own value's
   canonical text, because the pooled cells — the ones no count names —
   are the ones that owe it. What was wrong was filing it where it
   cannot bite. A column of 240 cells publishing 240 `decimal` ones has
   a ceiling of 240 and licenses every cell a file of the published
   length can carry. A LONGER file could exceed it; such a file misses
   `rows.n_rows` and every count taken over its cells, and what it no
   longer does is contribute a MISSED line here. That is the whole of
   what this costs, and it is the only one of the four whose cost is
   not literally nothing.
5. **`styles.spelled` is a new executable subcheck on every numeric
   column. THIS RAISES.** Method G6.1 says a numeric cell is written in
   exactly one of six styles "and in no other form", and G6.3 fixes the
   exact text each of the six writes for a value, with owner decision
   8's leading-zero family available inside every style but `plain`.
   Nothing in the validator asked that question: the style entries
   counted how many cells wore each FORM and the ceiling of clause 4
   asked how many were not canonical, and both are arithmetic over
   counts. So a twin whose every decimal cell carried one trailing zero
   — `66.60138701960640` where the shortest round trip of that same
   number is `66.6013870196064` — met every style obligation there was
   and validated through the shipped commands with exit 0 under "NO
   CHECKABLE OBLIGATION WAS MISSED". The new entry is that sentence of
   G6.1, counted per cell from the value alone, with a ceiling of zero.
6. **`header.presence` in the headerless direction loses its second
   conjunct. THIS RAISES.** The check called a first line a header only
   when it read back as the published names AND the file held more rows
   than the description publishes. A conjunction is only as strong as
   the conjunct an editor can pay off separately: a header line written
   in and one data row taken out leaves the row count where it was, and
   the check then reported "no header line, the first row is a record"
   about a file whose first line was the published names — the opposite
   of the truth about the bytes it governs, defeated by the exact
   perturbation class it exists for. The row count is `rows.n_rows`,
   which is its own subcheck and misses on its own terms. What the
   one-sided rule costs is stated rather than left to be found: a
   conforming twin whose first record spells every published name is
   reported as carrying a header line it does not carry, and that file
   is one no reader could tell from a headered file, which is the
   confusion `source.header_source` exists to settle.

**What the four lowerings are NOT.** They are not a narrowing of what
the twin owes: every fact stays in the entry table, at the same grain,
bound to the same registry fact, and every one of them is printed in the
report on every run. They are a correction to the KIND of entry each is,
which V3.3 makes a three-way partition and V3.4 makes vacuity-free in
both directions. The owner may reverse any of the four by making the
fact evidencible — by giving the validator something in the file to
compare that is not already checked elsewhere — and such a reversal
would be a raising and would be recorded here as one.

**Amendment A-P3-3 — the disclosure gate reaches the style clauses,
and four paths that were refusals or listings become verdicts. One
clause LOWERS, four RAISE, and two are rulings that change no
obligation** (2026-08-13, review items P3-V2-D-F1, D-F2, D-F6, E-F2,
E-F4, E-F5 and E-F6).

1. **Every numeric-style clause is settled against what the FILE'S OWN
   description publishes about its own spellings. THIS LOWERS, and the
   cost is written out below rather than left to be found.** Nine of the
   ten style subchecks recounted the written cells and compared the
   recount with a count the SUBMITTED description chose. A publication
   floor exists so that a form fewer cells carry than the floor is never
   named: every description of such a file carries one pooled total
   instead. So a verdict stated against a chosen count told two files
   apart that `synthtwin profile` describes byte for byte alike — the
   review ran that, `1E5` against `1e5` in one pooled cell, five
   subchecks differing and two different censuses — and six candidate
   descriptions differing only in their style map pinned a sub-floor
   count exactly, at two plain cells and one leading-zero cell under a
   floor of eleven. That second one is verbatim the situation V5.3 says
   the gate exists to stop.

   Each clause is now settled against the window the file's own
   description leaves: an exact count for each form it names, and for
   the forms it pools, the room its pooled total leaves them. Where
   every count in that window answers the clause the same way the
   verdict is reported; where they do not it is WITHHELD, with its own
   sentence saying the file's own description does not publish the count
   this check compares.

   **What that costs, stated plainly.** A file can hold up to one below
   the floor of cells in a form the description forbids and no style
   clause will say so — including the three forms contract 7.5.7 says
   the remainder never reaches. And the canonical-split ceiling of
   P3-V1-F7 can no longer produce a verdict on a column whose forms are
   ALL pooled, which is the fixture that review item was found on: a
   pooled cell re-spelled `1.50` where its value's canonical text is
   `1.5` leaves the same form, the same value, and the same description
   byte for byte, so no report can tell the two files apart. The clause
   keeps its teeth wherever the form is named — eleven cells reach the
   floor on that same description and the subcheck misses again — and
   the alternative was to keep an oracle for the counts the floor
   exists to hide. **A file can therefore buy a silence here**, which
   is the shape the presence-split defect had, and the difference is
   that this silence is forced by V5.1 rather than chosen: the two
   files a reader would want told apart are two files the producer
   describes identically.

   **THIS CLAUSE STANDS ON THE FIRST OF ITS TWO WITNESSES, AND
   AMENDMENT A-P3-13 WITHDRAWS THE SECOND** (2026-08-14, owner ruling).
   The `1E5`/`1e5` witness is ONE report telling two files apart that
   the producer describes byte for byte alike, and that is what this
   clause is for; the six candidate descriptions pinning a sub-floor
   count are the reader the owner has now put out of scope. Nothing
   here changes: no verdict moves, no window widens, and the cost this
   clause records is still paid. What changes is that the clause may
   not be re-derived from the withdrawn half.

   **And one half of the same class was left OPEN here. IT IS CLOSED BY
   AMENDMENT A-P3-5 CLAUSE 3, in the direction that keeps the
   subcheck.** Where the form IS named the canonical ceiling is still
   shown, and it still tells apart two files the producer describes byte
   for byte alike: forty whole numbers beside twenty halves written
   `1.5`, against the same twenty written `01.5` — the same form, the
   same values, one description — give it HELD on the first and MISSED
   on the second, measured. It was left open because closing it removes
   the subcheck. The odd cells of a form are a subset of that form's
   cells, so their count is at most the form's count, which is the most
   the file's own description settles; settling the clause from that
   description alone therefore gives HELD wherever the form's count is
   within the licence and nothing wherever it is not, and the subcheck
   could never report MISSED on any file at all. V3.4 and the charter
   call that a defect and V3.5 makes such an entry a LISTING — which
   reverses this plan's own P3-D8.1 ceiling and takes review item
   P3-V1-F7's repair with it. A-P3-5 clause 3 rules that canonicality is
   a fact about the file's own form rather than about the table it
   holds, on the test that the producer publishes it about no file at
   any count, and states the bound on what escapes. Nothing in that
   ruling reaches the numbers this clause governs: which of the six
   written forms a cell wears is published and floored, and every one of
   those counts is settled here exactly as before.

2. **The header question is settled on the first RECORD, and the
   reader's own name check takes the position-naming forms. THIS
   RAISES.** Round 1 settled a blank or repeated header name before the
   reader is called, and settled it on the first PHYSICAL LINE. The
   reader drops blank lines and honours a newline inside a quoted value,
   so a leading blank line and a quoted newline both walked past the
   pre-check into the reader's own refusal, which QUOTES the repeated
   name — a string out of a file nobody promised was the reader's, on
   the screen, with the suite green. Both files now reach a report at
   exit 3 naming the column NUMBERS at fault, and
   `reading._check_the_names_are_usable` takes the `refusals` argument
   its two neighbours have taken since round 1, so a future
   disagreement about which row is the first one cannot spend what
   those two saved.

3. **A file whose first row cannot name columns MISSES its per-column
   obligations instead of having them listed. THIS RAISES.** They were
   listing entries, and a listing entry says something specific: that no
   written CSV can evidence this obligation either way. The twin of the
   same description evidences every one of them. So one description told
   one reader it sets three hundred and fifteen checkable obligations
   and another that it sets eight, and told the second that three
   hundred and seventy-two of its obligations are beyond any CSV, of
   which three hundred and seven had been answered by another CSV three
   commands earlier. V7.2 fixes that the census names the obligations
   the DESCRIPTION sets. The row count is measured on that path too,
   counted in records the way the reader counts them.

4. **A file holding no data rows is settled by counting records, not by
   measuring the text. THIS RAISES.** `header\n` gave a full census at
   exit 3 and `header\n\n` gave a refusal at exit 1 with no report,
   carrying the profiler's advice to go and find a file that has the
   rows in it — when the true answer was that this file misses the
   published row count. Headerless, the same step stood between a file
   of no bytes and a file of one newline. Both sides of both steps now
   report.

5. **The two zero-row predicates bind the structural facts they left
   unbound, and stop binding one twice. THIS RAISES.** V6.4 makes the
   expected byte form the executable subcheck and the structural facts
   ZERO BYTES cannot evidence listing entries — and a headed zero-row
   file is not zero bytes: it carries its header line. That line
   evidences the column count, the names and the order, and all three
   sat inside the byte check's conjunction, which V3.6 forbids and
   which left `document.n_columns` and `universal.name` bound by
   nothing at all while the census called itself every obligation the
   description sets. They are checks of their own now, and the byte
   check answers for the bytes it names. The headerless form gains
   `header.presence`, which a file of no bytes evidences exactly, and
   loses a document-level `universal.position` listing that duplicated
   the per-column ones — a double binding V3.3 forbids in the same
   words it forbids an unbound one, and one obligation the description
   does not set counted in the not-checkable census.

6. **V6.2's byte rules state facts inside V5.1's envelope: a ruling, and
   it changes no obligation.** `bytes.line-endings` and
   `bytes.terminal-newline` state something about the measured file that
   `synthtwin profile` publishes about no file — its key set carries
   `source.encoding` and nothing about line endings or a terminal
   newline. V6.2 mandates the checks and V5.1 forbids the statement, and
   the specification did not say which governs. It is settled the only
   way it can be: withholding them would withhold them on EVERY file,
   because no description of any file publishes the fact, and a check
   that can never produce a verdict is the vacuity V3.4 refuses by name
   and the charter calls a defect. So the ruling is that V5.1's envelope
   is drawn round facts about the TABLE a file holds, and these two are
   facts about the file's form: no cell, no name, no count and no
   person is in either of them. Nothing changes in the code; what
   changes is that the conflict is settled in writing.

7. **The report's own gloss on WITHHELD is re-derived. No obligation
   changes.** The census line read "WITHHELD — measured, and not
   shown", which was true of the presence-split withholdings that
   amendment V2.4-A1 turned into measurements and is false of what is
   left: where the file's own description carries no fact of that kind,
   nothing was measured. The report now says WITHHELD means nothing is
   shown and the line says why, and the closing paragraph writes out
   both ways the gate closes, including clause 1's.

**Authorized corners: an independent classifier plus an agreement
battery — and refusals are refusals, never deviations.** Which facts
lawfully fall to lesser outcomes for a given profile — the identifier
infeasible corner, the datetime withheld-offset corner, the label
variants shortfall, the style-capacity fallbacks — is a pure function
of the profile. The validator does NOT import the generator's planning
stage: `plan_generation` builds planned cell content and shares every
planner defect with the generator, so reusing it would let one bug
classify a feasible case as a corner on both sides and pass every
end-to-end test. Instead the validation specification restates the
corner conditions as checkable predicates over the profile; the
validator implements them independently; and an agreement battery — in
tests, where both sides may be imported — runs every producer-battery
profile and every frozen conflict case through both classifiers and is
red on any disagreement. A shared design error now needs the same bug
written twice from two texts, and the frozen conflict cases pin the
expected classification of every case independently of both. The validator never
compares measured cells to any generator-planned cell content:
expectations come from the profile's published facts only.

The G12 refusal conditions are a DIFFERENT kind and are kept apart —
method G12 fixes how many there are and this plan follows it rather
than carrying a count of its own, which the fifth refusal of P3-D8.1
would otherwise have made stale: they refuse GENERATION, so no
conforming twin exists for such a profile, and a validate run on one is
a catalogued REFUSAL whose message mirrors the generation refusal — the
description is valid, the two facts that cannot both hold are named,
and whatever the measured file is, it cannot be that profile's twin.
Treating them as
authorized-lesser corners would launder an impossible obligation into
a passing report, which is exactly the class of quiet lowering this
project refuses. Red case: each G12-refusal profile plus any CSV must
produce the refusal, never a verdict.

**Structure and byte checks:** UTF-8, no byte-order mark, LF, terminal
newline (with owner decision 7's byte-form rule in the zero-row case);
row count; the U+FEFF quoted-header exception read back byte-for-byte;
`datetimes_read_at` recomputed from the cells, which the contract
demands be checked exactly this way; numeric styles recounted under
the pooled-cell identity P3-D8.1 ratifies — the amended form of
contract 7.5.7's rule, exact and two-sided over the whole map; and
type read-back —
the promises owner decisions 5, 8 and 10 of Phase 2 bought — asserted:
datetime precision and offset state re-read identically, numeric
columns re-read as the type the styles imply.

**Verdict vocabulary, fixed here.** Each executable subcheck lands on
exactly one of:

- **HELD** — the exact obligation was met;
- **WITHIN-BOUND** — approximated, inside both ends;
- **AUTHORIZED-DEVIATION** — a lesser outcome the ratified plan names
  for this profile's corner, shown with the exact plan passage or
  owner decision that authorizes it, drawn from the registry's own
  authorization citations;
- **WITHHELD** — the disclosure gate of P3-D3 closed over this check;
  counted in its own census line, never passed or failed;
- **MISSED** — an obligation the ratified matrix sets that the file
  does not meet.

Listing entries appear only in the NOT-CHECKABLE census.

**Exit codes — refusal distinct from verdict:** 0, validation ran to
completion and no subcheck MISSED; 3, validation ran to completion and
at least one subcheck MISSED, listed first in the report; 1, a
catalogued refusal — validation could not run (missing or unreadable
file, invalid profile, a G12-infeasible profile, memory) — consistent
with the other two commands' refusal exit; 2, usage. Automation
distinguishes a bad twin (3) from not-evaluated (1) without parsing
prose; the split is documented on every teaching surface and
exact-shape tested.

## P3-D3. The quality report: plain language, and what it may state

- **Audience and order:** a non-statistician reads it top to bottom;
  the verdict summary first, then the honest bounds, then
  fact-by-fact detail. Golden-tested bytes; every interpolated string
  through the display boundary, label variants included (contract
  13.5).
- **The verdict summary never claims more than the census.** The
  headline states the counts in fixed sentences: how many subchecks
  HELD exactly, how many landed WITHIN their stated windows, how many
  were AUTHORIZED-DEVIATIONS (each listed with its citation), how many
  were WITHHELD by the disclosure gate, how many MISSED, and how many
  obligations were NOT CHECKABLE and why. There is no "every fact was
  found" sentence: on a profile with authorized corners or
  approximated facts such a sentence is false by construction, so the
  wording that exists cannot be written from these verdicts — the
  summary is generated from the census alone, and a test asserts the
  all-facts-found form appears on no output for a corner-bearing
  fixture. A pass means: **no checkable obligation was missed**, with
  the other counts standing beside it, never folded into it.
- **The disclosure gate: the report may state about the measured file
  only what profiling THAT FILE would publish.** The measured file may
  be ANY CSV — a twin, a real table, or the wrong real table — and the
  report must be safe to exist in every case. The submitted profile's
  floor alone is not the envelope: the profiler routes a two-valued
  numeric-looking column to a label role BEFORE the numeric path and
  withholds sub-floor labels, and a crafted numeric profile would walk
  a naive validator straight past that routing. So the enforcement
  consults the FILE's own classification:
  - The validator runs the profiler's own role classification — the
    shipped taxonomy, under the profile's reconstructible settings
    (the table below) — on each measured column. A measured fact
    appears in the report only when the file's own classification
    publishes that class of fact for that column, **and "appears"
    covers the VERDICT as well as the value**: a within-bound or
    missed line against a candidate value is itself a
    measurement-derived statement, ~~and repeated candidate profiles
    would otherwise binary-search a value the file's own profile
    withholds~~ — **the second half of that ground is withdrawn by
    amendment A-P3-13 and this rule stands on the first, which is
    enough on its own: a verdict is something one report says about
    the measured file, and one report is read by people who do not
    hold it.** Where the gate closes, the subcheck's verdict is
    WITHHELD, with one fixed sentence saying the file's own
    description would not publish what this check measures, so
    neither the measurement nor its outcome is shown. What the
    withholding itself reveals — that the column classifies
    differently than the submitted profile expects — is a fact the
    profiler publishes about any file (the role axis), so the signal
    stays inside the envelope. On the ordinary case — the file IS the
    twin built from this profile — Phase 2's decisions 5, 8 and 10
    guarantee the twin re-reads as the same type, the classification on each side
    agrees, and everything prints; the withholding bites only on
    mismatched files, which is exactly where it must.
  - No string from the measured file is ever quoted — not in the
    report, not on screen, not in a refusal (P3-D1). Labels named in
    the report are the profile's published labels only.
  - Per-label, per-style, per-offset measured counts print exactly
    when they clear the floor. Below it, the named line states ONLY
    the fact that omission already publishes, and the plan spells out
    why that is inside the envelope rather than assuming it: when a
    file's own profile omits a published-in-the-submitted-profile
    label from its levels, that omission tells any reader of that
    profile exactly one thing — this identity covers fewer rows than
    the floor in this file, possibly zero. So the report's named line
    says exactly that and no more: not held at its published count;
    the measured count is below the publication floor, possibly
    zero, and is withheld. The exact sub-floor number NEVER appears
    beside a name — what may print namelessly is exactly what the
    profiler publishes namelessly, which differs by kind: the
    suppressed-count list for labels, and only the single pooled
    total for styles and offsets. The internal check still compares
    exactly;
    the MISSED verdict itself is derivable from the two statements
    already made (published at or above the floor, measured below
    it). An unpublished-content line says the file holds values the
    description does not publish, in N rows, with N floor-governed
    the same way, and never says what they are.
  - Whole-column counts — row counts, present and missing counts,
    distinctness — print exactly: the profiler publishes these for
    every column of any role. Numeric summaries print exactly ONLY
    for a column the file's own classification sends down a numeric
    path.

  **The settings the gate reconstructs, field by field** (outline
  round-4 condition A, satisfied here). The contract's `settings`
  block carries fifteen keys; the gate's use of every one is fixed:

  | settings key | the gate's use |
  |---|---|
  | `small_cell_floor` | the floor for both sides — what the profile published under, and what the gate prints under |
  | `identifier_uniqueness` | advisory-remark threshold, read from the profile and applied as the profiler applies it — it routes NO role; the identifier role is reached only by declaration |
  | `identifier_minimum_rows` | same — advisory-remark threshold from the profile, routing no role |
  | `minimum_parse_rate` | same — role-detection threshold from the profile |
  | `categorical_share` | same — from the profile |
  | `categorical_ceiling` | same — from the profile |
  | `categorical_floor` | same — from the profile |
  | `sentinel_outlier_iqr_multiple` | same — sentinel detection knob from the profile |
  | `sentinel_minimum_share` | same — from the profile |
  | `near_threshold_slack` | same — from the profile |
  | `kept_values` | DERIVED by owner decision 8 as amended: the user's spellings are unrecorded (`values_recorded: false`), and the gate instead treats as kept data every `variants` key (exact), every sentinel candidate carrying the kept verdict enum (exact), and every published `levels[].label` (at the folded identity, the producer's own pooling rule) — sufficient for the twin domain by the green battery |
  | `declared_missing_values` | DERIVED by amendment A-P3-15 clause 1: the user's spellings are unrecorded in the settings block (`values_recorded: false`), and the gate instead treats as declared-missing every `missing_by_source` key that is not one of this package's placeholder names, not a spelling the built-in missing table already reads as an absence, and not a spelling reading as one of the three numeric stand-ins — the three other ways a cell becomes a hole, so what is left can only be a declaration. Was EMPTY by owner decision 8 under "genuinely absent from every twin, whose absent cells are written empty", which is true of a twin and false of the table the description was written from (V1.2) |
  | `declaration_matching` | carried and applied to the derived kept set exactly as the profiler applies it to a declared one |
  | `declaration_publication` | carried but inert: no user-declared spelling exists to govern |
  | `forced_identifiers` | applied — the declared identifier columns are classified as declared, exactly as profiling declared them |

  The read mode is selected separately by `source.header_source`
  (P3-D1), not by any settings key. The validation specification
  carries this table normatively and a test asserts the gate consumes
  exactly these fifteen keys this way — a sixteenth key or a skipped
  key is red against the contract's own settings enumeration.

  The disclosure battery extends to the complete quality report, the
  complete screen output, and validate-path refusal text, with hostile
  fixtures including the crafted-numeric-profile shape above,
  asserting the measured magnitudes and every measured string are
  absent from every output byte. Validation adds no disclosure channel
  the profiler does not already have, because the profiler's own
  classification of the measured file governs every printed measurement.
- **The fourth artifact.** The quality report states measured facts
  about the measured file, so it is real-derived material exactly as
  the profile, the twin and the generation report are. The handling
  sentence extends everywhere from three artifacts to every file a full
  run leaves behind — FIVE, per amendment A-P3-8 clause 2, the
  profiler's plain-language summary among them — with the
  claim-inventory pinned strings updated in the same commit (P3-D7),
  and the report carries the handling rule itself, as the generation
  report does.
- **Honest limits, inherited verbatim** (the structure marks): no
  cross-column structure was validated because none is carried; rows
  independent, the grain undescribed; numbers computed on the twin are
  not research results. Plus the verdict-scope sentence, new and
  pinned by test: a passing quality report means no checkable
  obligation was missed — with the within-window,
  authorized-deviation, withheld and not-checkable counts beside it —
  it is not a fitness verdict for any analysis, it validates nothing
  the profile does not publish, and it cannot tell a synthetic file
  from a real one, because nothing in a CSV proves provenance; one
  fixed sentence says so.
- **The analyst-expectations section.** One fixed section answers the
  question a methodologist brings: which of the checks I care about
  does this report perform? Split honestly. Checked in this version:
  single-column shares of published labels; distribution ladder positions
  within stated windows; spread and shape summaries within stated
  windows; missing-value counts; value-format read-back. NOT checkable
  in this version, and named as such: any target tying two columns —
  rates within a subgroup defined by another column, model
  coefficients, time-to-event structure, agreement between a
  prediction column and an outcome column — and any target about row
  grouping. The wording commits to nothing about later phases: it says
  these need cross-column structure this version deliberately does not
  carry, that carrying them is later work with its own plan and its
  own contract change, and no more.
- **Silence never reads as a pass.** The report prints the check
  census — subchecks checkable on this profile, checked (the identity
  must hold), per-verdict counts, and the full list of what was NOT
  checkable and why.

## P3-D4. Non-vacuity: provable from the start

"A check that cannot fail is a defect" becomes machinery:

- **The red-case battery, at subcheck granularity, bound by name.**
  The validation specification enumerates, for EVERY executable
  subcheck, at least one perturbation of a valid twin that must
  produce MISSED — per rung, per style, per level, per variant map,
  per offset, per extreme, per structural rule: wrong count, moved
  cell, re-cased label, re-spelled number, shifted date, truncated
  file, re-encoded bytes, reordered columns, edited header, injected
  byte-order mark, nonempty bytes in the zero-row form. **Each
  red-case registration NAMES the subcheck identity it must fail, and
  the battery asserts that THAT subcheck reports MISSED** — other
  subchecks failing alongside is fine, but a perturbation caught only
  by a neighbour, the mean tripping while a hard-coded rung check
  sleeps, is a red battery, because the named subcheck did not do its
  job. The suite builds each perturbation at test time from seeded
  neutral fixtures; a coverage identity test walks the shipped
  executable-subcheck table and asserts every entry has at least one
  registered, named, passing red case. Listing entries are outside
  this battery and inside the census tests.
- **The green direction.** Producer → generator → validator over the
  every-role fixture and every frozen conflict case: zero MISSED and
  zero WITHHELD — a twin validated against its own profile must not
  trip the disclosure gate, because type read-back agreement is
  itself a Phase 2 promise. The one corner where that promise itself
  is short is R-P2-13's missing-marker collision, a generator-side
  residual named in P3-D11; the battery fixtures avoid it by
  construction and a dedicated fixture pins its behaviour (verdicts
  unmoved, withholding conservative) so the exception stays exactly
  one residual wide. On the conflict cases the
  AUTHORIZED-DEVIATION verdicts must APPEAR with their citations. An
  authorized deviation the validator fails to name is itself a red
  test. Zero-row profiles, in both header modes, must produce
  verdicts.
- **The pairing battery.** Twin of profile A against profile B, where
  A and B are a DELIBERATELY chosen mismatching fixture pair whose
  shapes guarantee at least one checkable miss — not a universal claim
  about arbitrary pairs: at least one MISSED and never a clean pass,
  with WITHHELD verdicts permitted where the gate closes and the
  summary asserted to refuse to read as a pass. A twin regenerated at
  a different seed against the same profile: passes. The real table a
  fixture was profiled from, validated against its own profile: the
  battery records the outcome and asserts the provenance sentence is
  present.
- **Vacuity floor.** As with the loader battery: a counted floor of
  distinct red-case classes per disposition class, so the battery
  cannot rot into one shared perturbation.

## P3-D5. Governing documents, registry, seal

- **The governing set grows from three to five.** This plan joins the
  seal at its landing (the fourth document); the validation-method
  specification joins at its own landing (the fifth). Each lands
  together with its seal entry and the registry guard's updated
  exact-list assertions; the tree test makes an unsealed governing
  document visible at every CI run, same-commit landing is procedure,
  and the phase-close history audit confirms it. The registry extends
  so every fact binds its entry identities, countersigned in the
  judgment digests.
- Any Phase 2 amendment flowing from owner decisions 1 and 3 follows
  the exact amendment procedure: amend in the open, re-seal with the
  tool, one counted line per passage, commit document and seal
  together. **Never lower a ratified obligation silently: emit a named
  deviation or refuse** — the standing rule, restated as binding on
  this phase.

## P3-D6. CLI, UX, and errors that speak human

- `validate` joins the command positional — no subparsers, one help
  screen, the same display boundary, the same exit-code discipline
  extended by the verdict exit of P3-D2. The bare `synthtwin` status
  screen names all three commands once validate ships.
- **The teaching chain:** `profile` success output ends by teaching
  the `generate` command line for this profile; `generate` success
  output ends by teaching the `validate` command line for this twin —
  replacing the generation report's sentence that a fidelity verdict
  is Phase 3's work; `validate` success output says what the verdict
  means, what it does not, and what exit code automation saw. All
  three sentences are exact-shape tested.
- **Failure catalog extensions**, each with exact-shape and
  reachability tests: measured file missing, unreadable, a folder, or
  not readable as CSV — the validate-parameterized, position-naming
  forms of P3-D1; the quality target already present without
  `--replace`; an output resolving onto either input; the
  G12-infeasible refusal of P3-D2; out-of-memory during validation.
  Structural mismatch — wrong column count, wrong names — is a MISSED
  verdict with a plain explanation, never a refusal: the report is the
  product even when the news is bad.
- **Zero-code check:** every new message names what happened and what
  to do next; no message assumes the person can read code or holds the
  real table.

**Amendment A-P3-4 — the quality report says which file it is about and
is named after it; one stated guarantee about randomness is LOWERED to
the property that is actually enforced, with three enforcements RAISED
under it; and three test-side assertions that could not fail, or did not
exist, are repaired** (2026-08-14, review items P3-V2-G, P3-V2-F-F1,
F-F2, F-F3 and F-F4).

1. **The report names the measured file, and its own name is derived
   from that file. THIS MOVES A SHIPPED OUTPUT NAME and the golden
   quality-report hash; it lowers no obligation and raises one.** The
   output name came from the PROFILE's stem, so `validate
   clinic-profile.json --twin tampered.csv` wrote
   `clinic-twin-quality.txt` — a report named after the twin, left
   beside the twin, about a different file — whose bytes held the word
   `tampered` zero times and no path of any kind, while its own third
   paragraph said "It is a report about ONE file". Checking a second
   candidate was then refused for a name collision that had nothing to
   do with what was measured, or with `--replace` silently replaced the
   first file's report under the first file's name. Which file was
   measured is the one fact about a run that a reader cannot recover
   from anywhere else once the shell scrollback is gone.

   Both halves are repaired. `validation.Outcome` carries the measured
   file's NAME — the last component of the path as the person typed it,
   never a folder, never a path — the report prints it above everything
   else (spec V7.1-A1), and the output is `<measured stem>-quality.txt`.
   **The ordinary run's file name does not move**: the default measured
   file is `<stem>-twin.csv`, so its report is still
   `<stem>-twin-quality.txt` and the command a finished `generate` run
   teaches still writes exactly the file it always wrote. What moves is
   the name a run with `--twin` writes, and the golden quality hash,
   which is re-recorded with the reason beside it.

   **What this costs, stated rather than left to be found.** The report's
   bytes now depend on the measured file's name as well as its bytes, so
   V10's determinism clause names the name as an input; renaming a file
   and measuring it again is a different report, deliberately. And the
   LEXICAL route by which an output could land on the MEASURED file is
   no longer reachable — no name is a fixed point of "stem plus
   `-quality.txt`" — so no test drives it there any more. It is still
   reachable at the DESCRIPTION, where a description named
   `<something>-quality.txt` collides with the report for
   `<something>.csv`, and that case is driven through the command. The
   link, hardlink, alias and substitution routes to both inputs are
   untouched.

2. **"No random source is in the validate closure at all" is replaced
   by the three properties that are true. THIS LOWERS A STATED
   GUARANTEE, and no file's verdict changes.** Nine surfaces said it
   absolutely — this plan, the validation specification's V10, the
   charter, `README.md`, two docstrings and a comment in `cli.py`, and
   two in `quality.py`. It was false and measurable: a fresh interpreter
   running only `validate` gains `numpy.random`, `numpy.random.mtrand`,
   `random`, `secrets` and `uuid`, and a live `default_rng` is reachable
   by attribute from `quality` itself, whose docstring said it was not.
   The route is not an accident and cannot be closed: validation must
   read a CSV, reading a CSV means pandas, and pandas imports numpy.

   The sentences now say what is enforced, and each level is enforced by
   something that can fail: no synthtwin module on the validate path
   imports a random source (the offline scanner and a static closure
   walk); the validate path never reaches the generation module, where
   this package's own generator lives (a fresh-interpreter `sys.modules`
   check); and a validate run draws from no random source at all (a trap
   over every source in the process, with the command run at it). **The
   third is new and is a RAISE**: no test in the suite could see a live
   draw inside the validate path before it. The owner may restore the
   absolute the day the reader stops needing pandas — a test asserts
   `numpy.random` IS in a validate run's module cache and says, when it
   stops being, that the wording can be raised again.

3. **Two names in the runtime boundary assertion could not fail. THIS
   RAISES.** `numpy` and `numpy.random` were in a forbidden tuple
   checked against import statements recorded during a run; under pytest
   both modules are in `sys.modules` before the test starts, so no
   module body re-executes and a live `numpy.random.default_rng(0)`
   added to `quality.py` left the assertion GREEN. They are removed,
   with the reason written where they stood, and replaced by the
   fresh-interpreter check of clause 2 — which catches, with a warm
   module cache, a module-level `from synthtwin import rendering` in
   `quality.py` that the recorder does not.

4. **The line-ending guard reaches the files the product READS, not
   descriptions alone. No obligation changes; a false verdict against
   the product is prevented.** `tests/test_twin_golden.py` wrote the
   twin it measures with `write_text(..., encoding="utf-8")` and no
   `newline`, so on `windows-latest` the file handed to
   `validation.measure` was a CRLF twin: `bytes.line-endings` MISSED,
   `GOLDEN_QUALITY_SHA256` moved, and the message a Windows maintainer
   would read called it a release-blocking determinism defect in the
   product. The product was innocent — `writing.write_text_file` pins
   the line ending — and this is the second time the same class has bitten
   on the same suite. The guard that exists for the first shape now
   governs `.csv` names as well as `.json` ones, with a floor asserting
   each half still matches a real write, and with the property it
   protects asserted directly: a measured file whose lines end the
   Windows way MISSES the byte rule it should miss.

5. **The alias matrix gains the class `is_the_same_file`'s own docstring
   names as the one it cannot settle. THIS RAISES.** P3-D1 requires each
   input crossed with each alias class; the shipped matrix carried
   lexical, resolved, link, hardlink and case-fold, and not the one that
   function names in as many words — two names that do not exist yet,
   spelled differently, that the filesystem treats as one file. Both
   inputs are now crossed with a Unicode-normalization alias, and a test
   beside it pins WHICH rule catches it, because the first two rules
   provably cannot: the two spellings resolve to different strings and
   are different after the case-blind comparison, and only the
   filesystem's own identity settles them.

**Amendment A-P3-5 — the blank split is reported only where describing
the file publishes it, and canonical SPELLING is ruled outside V5.1's
envelope. One clause LOWERS a residual's bound, one RAISES, and one is
a ruling that changes no obligation. THIS DEFINES WHAT THE
CONFIDENTIALITY GUARANTEE MEANS AND THE OWNER MAY WANT IT THE OTHER
WAY; clause 4 says exactly what reversing it costs** (2026-08-14,
review items P3-V3-F1 and P3-V3-F2).

**The conflict, stated before the ruling, because it is a real one.**
V2.4 counts presence by BLANKNESS, so that a file cannot buy silence
with marker cells; amendment V2.4-A1 made every presence-dependent
measurement take its number from a second description built that way,
after round 2 found that withholding instead let a file carrying almost
none of its published facts exit 0. V5.1 says the report may state
about the measured file only what describing THAT FILE would publish.
The producer counts presence by its own absence rules, and the two
readings differ exactly on the cells that are non-blank and read as
holes. **So every verdict taken over the blank split is a statement the
file's own description makes only when that description says how its
missing cells were spelled — and that is a FLOORED fact.**
`missing_by_source` names an exact spelling only where at least
`small_cell_floor` cells share it and pools the rest into one unnamed
total, because a count of two cells sharing a rare spelling is a count
the floor exists to hide. Measured here, on the shipped code, and
measured again after the repair: two sixty-row files, fifty-nine
`north` and one hole, one hole written empty and the other written
`n/a`, whose full descriptions `synthtwin profile` writes BYTE FOR BYTE
ALIKE — **48 HELD, 0 MISSED and exit 0 against 40 HELD, 8 MISSED and
exit 3**, the eight being both presence counts, `n_not_numeric`, both
distinctness counts and all three suppression counts.

1. **A presence-dependent verdict is taken over the blank split where
   the file's own description names the source of every missing cell,
   and off that description itself where it pools any of them. THIS
   LOWERS residual R-P2-13's bound, and lowers nothing else.** Where
   every source is named, a reader of that description knows the exact
   multiset of spellings the holes wear, so every measurement the split
   takes is derivable from what profiling the file publishes and
   reporting it states nothing new — which is the ordinary case, and
   covers every column of the every-role fixture: no missing cells at
   all, or blanks that reach the floor and are named `(blank)`. Where
   the description pools, the file's own description supplies the
   verdict. That is inside the envelope by construction, because it IS
   the description.

   **It is deliberately NOT a withholding, and that is the whole of the
   design.** A silence is something any file could buy by writing one
   marker cell, and that is verbatim the defect amendment V2.4-A1
   exists to close; a validator that answered this conflict by
   withholding would have traded a confidentiality defect for the
   vacuity V3.4 refuses and handed back A1's repair. Every obligation
   still lands on a verdict, taken from one description or the other.
   **Zero new withholdings are produced on any file**, and the green
   battery's zero-WITHHELD property is untouched.

   **The two presence COUNTS ask a weaker question than the rest, and
   asking one question for both would have thrown teeth away.** They
   need only how MANY holes are non-blank; distinctness and the rest
   need what those holes SPELL. `missing_by_class` counts holes under
   synthtwin's own five words, which carry nothing from the table, so it
   is published for every role — including the three that publish no
   value of the table at all, whose `missing_by_source` is empty by
   policy. So where its pooled remainder is empty the two counts are
   settled over the split even on a free-text or declared-identifier
   column, and round 2's own witness is still caught there: thirty holes
   spelled one way clear the floor, the class map names them
   `(text-code): 30`, and `presence.n_present` misses again. A single
   gate keyed on the source map alone would have passed that file.

   **What it costs, stated rather than left to be found.** Below the
   floor the report can no longer tell a hole written empty from a hole
   written `n/a`, and it must not: those are two files the producer
   describes identically. The bite is on residual R-P2-13, whose Phase 3
   bound reads "verdicts are blankness-based and immune". That bound is
   now narrower: in a column whose own description pools its missing
   sources, a conforming twin holding a generated value that reads back
   as a hole — a numeric sentinel at the edge of its own range — is
   measured as the producer measures it, so the collision can cost a
   MISSED verdict where it previously cost only report detail. The
   residual's text is corrected to say so. The trade is deliberate and
   arguably favours the reader: a twin that holds a value every profiler
   reads as "no value" is a twin whose own description differs from the
   one it was built from, which is a fidelity fault worth a line in a
   report rather than one worth absorbing in silence.

2. **The style clauses read the cells that description reads, on the
   same branch. THIS RAISES, and it is the half of the class the review
   item did not name.** The style clauses recount the WRITTEN cells and
   settle each recount against the room the file's own description
   leaves — room `_unread_cells` widens by exactly the disputed cells.
   So the leak had a second half, measured on the shipped code with the
   same shape of witness: fifty-nine numbers and one empty cell beside
   fifty-nine numbers and one `n/a`, one description between them,
   **seven style subchecks changing verdict** and the census going from
   19 MISSED to 17 MISSED plus 7 WITHHELD. Repairing only the presence
   counts the review named would have left it open. Where the split is
   not published the gated side now sees the cells with every disputed
   spelling removed, which is the same cell list for every file that
   description cannot tell apart.

   **THIS CLAUSE'S ACCOUNT OF ITSELF WAS WRONG, AND AMENDMENT A-P3-9
   CLAUSE 1 CORRECTS IT** (2026-08-14, review item P3-V4-F1). "Every
   disputed spelling removed" was implemented as every cell wearing a
   built-in missing spelling and every cell whose value is one of the
   three built-in numeric stand-ins, whatever the description says
   about them — and a description can NAME such a value as data, by
   every one of V2.3's published routes. A cell so named is disputed by
   nobody: both readings count it as a value. Deleting it is a
   measurement error, not a report-detail cost, and this clause priced
   it as the second while it was the first: the twin the shipped
   generator writes from a description keeping `-999` was reported
   `styles.at-least.plain` and `styles.remainder` MISSED, at exit 3.
   The cost recorded below is the pooled-presence cost, which is real
   and stands; the false rejection is A-P3-9's to state, and it is not
   a cost this plan accepted.

3. **Whether a number's TEXT is a spelling its own value licenses is
   outside V5.1's envelope: a ruling, and it changes no obligation. It
   closes the residual A-P3-3 clause 1 left open, in the direction that
   keeps the subcheck.** `styles.spelled` and `styles.canonical.<form>`
   compare a cell's text against texts computed from the VALUE that text
   reads back as. Two files differing only there — sixty canonical
   decimals against the same sixty values carrying a trailing zero — are
   described byte for byte alike and get HELD and MISSED, measured. The
   question A-P3-3 clause 6 asks of any such fact is whether it is a
   fact about the TABLE a file holds or about the file, and the test
   that settles it is the destination: **the profiler publishes
   canonicality about NO file at ANY count.** Its own form ladder
   discards it by design — `1.5` and `01.5` are both `decimal`, by a
   first-match-wins order the contract fixes, and `numeric_style`'s
   docstring says no spelling and no magnitude travels out through it.
   So there is no floor to appeal to and no window to draw: withholding
   these two would withhold them on every file forever, which is the
   vacuity V3.4 refuses by name and which V3.5 would then turn into a
   LISTING whose census sentence — that no written CSV can evidence
   this — the twin falsifies every time it is generated.

   **This is a weaker ruling than A-P3-3 clause 6's and is recorded as
   weaker.** A line ending is one fact for a whole file and carries
   nothing per record; a spelling is per cell and CAN carry a person's
   own data, since `1.50` beside `1.5` records the precision a
   measurement was taken at. What makes it rulable anyway is the size
   and shape of what escapes, which is bounded here rather than
   asserted: neither subcheck prints a measured count, and
   `styles.spelled` takes NO number from the submitted description at
   all — its only profile input is the boolean `integer_valued` —
   **which is now written as a fact and not as a bound, for the reason
   the next paragraph gives.**

   **WHAT A RULING OF THIS KIND OWES IS NARROWER FROM 2026-08-14, AND
   AMENDMENT A-P3-13 IS THE RULING.** The first half — neither subcheck
   prints a measured count — is what a reader of one report is
   protected by and is still owed. The half that was about somebody
   submitting one description after another is no longer owed by any
   ruling here, because no rule in this plan defends against that
   person. What this clause used to conclude from `styles.spelled`
   taking no number — that such a person could get nothing through it —
   is therefore struck as a promise and left standing only as the fact
   it rested on, so that no reader takes it for a guarantee about that
   person. A-P3-10 clause 1 — which was written to make the same
   conclusion true of the other subcheck — is withdrawn by A-P3-13
   clause 2.

   **THE BOUND THIS CLAUSE STATED FOR THE PAIR WAS TRUE OF ONE OF THEM,
   AND AMENDMENT A-P3-10 CLAUSE 1 CORRECTS IT** (2026-08-14, review item
   P3-V4-F2). "What a report can carry is one bit per column" is what
   stood here, and `styles.canonical.<form>` never had that property: it
   compares its recount against a count the SUBMITTED description names,
   so eleven candidate descriptions read the exact number of
   non-canonical cells off the verdict, and two files the producer
   describes byte for byte alike got HELD and MISSED. The recount is now
   read at the publication floor's own resolution, which is the bound
   A-P3-10 clause 1 states, measures and prices; the sentence about
   `styles.spelled` stands as written, and the ruling itself is
   unchanged.

   **The FORM counts stay gated exactly as A-P3-3 clause 1 left them**,
   and nothing here relaxes them: which of the six forms a cell wears IS
   published and IS floored, `styles.canonical.<form>` MISSING on a
   pooled form would put a lower bound on that form's count, and its
   pooled-form window is what stops it. The ruling reaches only the
   residual where the form is NAMED, where the count is published
   exactly and only canonicality is left to leak.

4. **How to reverse this, since it defines what the guarantee means.**
   Clause 1 reverses by taking the split's verdict unconditionally —
   restoring `_governed`'s pre-amendment form — which restores
   R-P2-13's old bound and reopens P3-V3-F1 exactly as measured above;
   or by WITHHOLDING where the split is not published, which is
   V5-honest too and was measured rather than reasoned about. Both
   alternatives were reinstated in memory against the shipped suite.
   **The withholding one satisfies the equivalence battery and then
   costs three things this one does not:** the witness file's census
   becomes 46 HELD, 12 WITHIN, **18 WITHHELD**, 0 MISSED where this
   resolution withholds nothing; V2.4-A1's own battery goes red at
   `test_one_marker_cell_leaves_every_miss_standing` and
   `test_silence_is_never_free_and_never_the_validator_s_own_difficulty`,
   which is A1's repair handed back; and the green direction goes red at
   `test_a_twin_of_its_own_description_misses_nothing`, because a
   conforming twin whose missing cells do not reach the floor in any one
   class loses its presence-dependent verdicts. Choosing it is a
   lowering of this plan's own non-vacuity floor and of acceptance
   criterion 3. Clause 3 reverses by
   making both subchecks LISTING entries under V3.5, which is what
   A-P3-3 clause 1 said the alternative was: it reverses this plan's
   P3-D8.1 canonical ceiling and takes review item P3-V1-F7's repair
   with it, so a twin holding `2.50` where its value's canonical text is
   `2.5` passes every style check again. Either reversal is recorded
   here in the same form as this one.

**Amendment A-P3-6 — three checks that gave the WRONG ANSWER, and the
one thing they had in common. Two clauses RAISE an obligation, one
moves a conjunct back to the subcheck that owns it and changes no
file's outcome, and none LOWERS anything** (2026-08-14, review items
P3-V3-F4, P3-V3-F5 and P3-V3-F6).

**What they had in common, stated first, because it is the reason they
are one amendment.** A validator answers two different questions and
each of these three confused them: what the DESCRIPTION says a file
owes, and what THIS CODE happens to be able to read. Where the second
was mistaken for the first, an obligation went quiet, a conforming
generated file was called wrong, and a whole report was written about a
file nobody had read. The repairs are all of the same shape: the
validator's own reading is made total over what the METHOD defines, and
where it cannot read a file at all it says so instead of reporting.

1. **A column of quarters is measured, not silenced. THIS RAISES.**
   Method G7.1 fixes one ordinal unit per resolution — one second for a
   date and time, one day for a date, ONE QUARTER for a quarter — and
   G12.4 and G12.5 draw their windows in that space, saying in as many
   words that a quarter cell carries its own unit exactly. The shipped
   validator read every instant through the profiler's
   `parsing.instant_key`, which returns nothing for a quarter by design,
   and turned that into WITHHELD. Measured here, with the shipped
   behaviour put back in memory: a description publishing twelve
   distinct quarters from `2018-Q1` to `2024-Q4`, against a twelve-row
   file holding five `2018-Q1`, two `2021-Q3` and five `2024-Q4`, gives
   **31 HELD, 11 WITHHELD, 0 MISSED and exit 0** with the pass
   conclusion printed. (The review reported the same file as 22 HELD,
   11 WITHHELD, 0 MISSED; the held count differs with how the twelve
   published quarters are chosen and the eleven silences do not.) Those
   eleven were both distinctness counts and all nine rungs between the
   ends, and the file was wrong about every one of them. The same run
   now gives 31 HELD, 2 WITHIN-BOUND, 0 WITHHELD, **9 MISSED** and exit
   3, with both ends still HELD — so the nine and the two did the
   catching on their own terms.

   **What it costs: nothing any file was owed, and one branch of the
   validator is gone.** No obligation is added; eleven per quarter
   column move from a silence to a verdict. The branch that produced
   the silence is removed rather than narrowed, so no resolution can
   reach it again: the ordinal space is total, and a published instant
   that names no point in its own resolution's space is an internal
   contradiction the code raises on rather than withholds. The non-
   vacuity fixtures gain a QUARTER predicate — the finding notes there
   was none, which is why nothing saw this — and two registered red
   cases whose whole point is that the ends hold while the interior
   misses.

2. **The degenerate zero-row form is checked against the bytes the
   METHOD writes, and against nothing else. THIS RAISES for the
   spelling; it moves the line-ending conjunct to the byte rule that
   owns it; and it stops a conforming file being called wrong.** Owner
   decision 7 above makes the expected BYTE FORM the executable check.
   The shipped check asked instead for one physical line ending in a
   line feed, which is neither exact nor record-aware:

   - for a one-column zero-row description named `reading` the renderer
     writes `reading\n`, and the file `"reading"\n` passed every check
     the run filed — quoting was nobody's obligation, because reading
     the names back is `header.names`' question and it is answered from
     the parsed record;
   - a published name holding a line feed is written `"alpha\nbeta"\n`,
     which is ONE record over two physical lines, and the conforming
     file the shipped renderer writes was reported MISSED.

   The subcheck now answers for what no other one does: **the file holds
   exactly one record, that record is written the way method G2 writes
   it, and nothing follows it.** Which names they are stays
   `universal.name`'s, the count stays `document.n_columns`', the order
   stays `document.columns`', and the line ending and the terminal
   newline stay the two byte rules' — so the terminator is taken off
   before the comparison rather than being a fourth thing this check
   accuses a file of. That last part is the only movement in the
   lowering direction and it lowers no obligation: a file with no final
   newline still MISSES, at `bytes.terminal-newline`, which is V3.6's
   own rule that a fact another subcheck checks is that subcheck's to
   miss. The canonical writing is derived from the METHOD in the
   validator, because it may not import the renderer (V1.4), and the
   suite compares the two writings character for character over every
   class of name quoting turns on — the same arrangement V4.2 makes for
   the corner classifier.

   **And the same class reached a byte rule, which re-deriving it
   found.** `bytes.line-endings` asked whether a carriage return was
   among the file's bytes. The method writes one inside a quoted field
   whenever a published name or label holds one, so that rule also told
   a conforming twin it had broken a rule it kept; and the measured file
   was read with the ordinary text reading, which turns every carriage
   return into a line feed, so such a twin's names read back under a
   name it does not carry and three more checks missed with it. The rule
   now asks what V6.2 names — whether a carriage return ends one of the
   file's RECORDS — and the file is read without translating anything,
   which is also what the reader does.

3. **The walk that stands in for the reader reads what the reader
   reads. THIS RAISES nothing and lowers nothing; it stops a report
   being written about a file nobody read.** Validation settles two
   questions before calling the shipped reader, and settles them with a
   CSV walk of its own. The field size limit is a setting of the whole
   `csv` module: the reader raises it to its own published ceiling for
   the length of its pass, and the walk ran under whatever the
   interpreter started with. Measured: a strict-valid constant
   description of eleven values one character past that default
   generates a conforming twin, the reader reads every row of it, the
   walk parsed the header and stopped, and the conforming twin got a
   **whole report of MISSED verdicts without the reader ever being
   asked**. The walk now sets `reading.FIELD_SIZE_LIMIT` itself — the
   reader's own name, so the two cannot be moved apart by editing one
   place — and puts the module-wide setting back on every exit.

   **And a reading that stopped part way is no longer read as a file
   with no rows.** Beyond the shared ceiling both readings fail, and
   there the walk says so: the file goes on to the reader and gets the
   catalogued refusal V9 asks for, in the position-naming form, instead
   of a report built on the records the walk happened to reach. The
   drift guard that compares the two readings is extended in both the
   ways this finding shows it needed: it is driven over the FILE as
   `measure` reads it rather than over a string the test wrote, and its
   twelve files gain seven that cross the limit — in a value, in a name,
   inside quotes and beside a quoted line break.

**How to reverse any of the three.** Clause 1 reverses by making
`_instant_of` the profiler's instant reading alone, which restores the
eleven withholdings on every quarter column and the exit-0 pass above;
it is a lowering and would be recorded here in those words. Clause 2
reverses by comparing the first physical line again, which restores both
witnesses at once — the quoted name that passes and the conforming twin
that fails. Clause 3 reverses by leaving the module-wide limit alone,
which restores the full-MISSED report on the conforming twin. Each was
reinstated in memory against the shipped suite to check that the tests
which assert it go red, and each does.

**Amendment A-P3-7 — a report about a file the producer REFUSES says
what that refusal says and no more. One clause LOWERS, by turning eight
verdicts into withholdings on the two classes of file this reaches; one
RAISES, by putting a third class back on the reportable side; and one is
a RULING that leaves a residual open, states its size, and says what
closing it would cost. THIS ALSO DEFINES WHAT THE CONFIDENTIALITY
GUARANTEE MEANS WHERE THERE IS NO DESCRIPTION TO DRAW IT FROM**
(2026-08-14, review item P3-V3-F3).

**The conflict, stated before the ruling, because it is a real one and
it is not the one A-P3-5 settled.** V5.1 draws the envelope round what
`synthtwin profile`, run on the measured file, would publish about it,
and A-P3-5 answered the case where that description PUBLISHES LESS than
the validator measured. This is the case where there is no description
at all: the profiler's reader refuses a file with no data rows, and
refuses one whose first row leaves a name blank or uses a name twice.
Validation reports on both rather than refusing — V9 is explicit that a
structural mismatch is a MISSED verdict with a plain explanation — and
it did so with an early return, before the file's own description was
built, settling four structural obligations and every column's position
against a header line nothing describing that file publishes. Measured
here, on the shipped code, with a two-column description publishing two
hundred and forty rows: the header-only files `age,site` and `foo,bar`,
under the same name, gave **11 HELD, 1 WITHHELD, 73 MISSED** and
**6 HELD, 1 WITHHELD, 78 MISSED** — five verdicts apart, on a file the
profiler refuses to say one word about. Repeated candidate descriptions
read the header off those five, one guess at a time, which is what V5.3
was written against at the time this amendment was made and no longer
is: V5-A1 withdrew that reader later the same day, and the paragraph
below is what this amendment now rests on.

**THIS AMENDMENT STANDS ON THE FIVE VERDICTS AND NOT ON THE REPEATED
CANDIDATES, AND A-P3-13 WITHDRAWS THE SECOND** (2026-08-14, owner
ruling). Five verdicts apart is ONE report telling its reader what the
checked file's header line spells, about a file `synthtwin profile`
will not say a word about — and that reader may hold nothing, which is
what the withholding is for. The person trying one candidate
description after another is the reader the owner has put out of scope.
Nothing in the clauses below changes; what changes is which sentence
they rest on.

1. **On a path where the producer refuses the measured file, every
   verdict whose outcome varies with what that file holds is WITHHELD,
   under a sentence of its own. THIS LOWERS.** Seven subchecks in all.
   On the no-data path: the column count, the header's presence, its
   names, its order, and each column's position. On the unusable-header
   path: the row count and the column count. And on both, the rule that
   asks whether the file is written as UTF-8, because which encoding a
   file was read under is a fact the producer PUBLISHES —
   `source.encoding`, with `used_fallback_encoding` beside it — while
   the other three byte rules are the ones A-P3-3 clause 6 ruled outside
   the envelope for being published about no file at any count. The same two files
   above now give **5 HELD, 7 WITHHELD, 73 MISSED and exit 3** — the same
   report, byte for byte, as each other and as a header-only file four
   columns wide, one padded with blank lines, and one whose bytes are
   not UTF-8. On the other path, `a,a` over two data rows and `a,a` over
   four gave reports differing in the row count they printed, and now do
   not differ at all.

   **What it costs is nothing any file was owed, and that is what makes
   it a withholding rather than a conflict.** Both paths are reached
   only by a file this description's own twin is not: a description that
   publishes rows has a twin that carries them, and a description whose
   names came from the file has a twin whose header reads them back. So
   every one of the eight still answers on the file the description says
   is right, and the file that reaches these paths still misses its row
   count and every obligation of every column — an exit-3 report whatever
   its header says, before and after. The census moves and the
   conclusion does not.

   **One of the eight is withheld for honesty rather than for
   confidentiality, and it is named rather than folded in.** Each
   column's `position.at` was MISSED on the no-data path under the
   sentence that says this file holds no cells — which is the wrong
   reason, because a position is evidenced by the header line and not by
   a cell, and the miss asserted something about that header the report
   may not assert. It could have stayed a miss without leaking anything:
   every file reaching there got the same one. It is withheld because
   MISSED there says a thing this validator does not know.

2. **What the refusal ITSELF publishes is still reported, because that
   is what a reader gets by running the profiler on the file.** The
   no-data refusal names the file and says it holds no rows, so the row
   count MISSES with its measured zero, and every obligation of every
   column MISSES because a column with no cells carries none of them.
   The unusable-header refusal says which fault it is, so the header's
   presence, its names and its order all MISS with that fault on the
   line. What that refusal does not carry is a count: it stops at the
   first row, so the file's width and its record count are numbers no
   run of the producer on that file ever publishes, and those are the
   two clause 1 withholds there.

   **THIS CLAUSE NAMED THE COLUMN NUMBERS AND SAID THAT PUBLISHED
   STRICTLY LESS THAN DESCRIBING THE FILE WOULD; IT DOES NOT, AND
   AMENDMENT A-P3-10 CLAUSES 2 AND 3 CORRECT IT** (2026-08-14, review
   item P3-V4-F3). The profiler's own refusal for a REPEATED name quotes
   the name and names no position, so the positions are a fact of their
   own rather than a smaller one: `dup,a,dup` and `a,dup,dup` draw one
   sentence out of the producer and drew two reports. The report now
   states the fault and not the place. The BLANK-name refusal is
   unchanged, because the profiler's own form of that one does name the
   column number.

3. **The zero-row predicates are NOT gated, and this is a ruling with a
   residual left open. It changes no obligation and no line of code; it
   says why the same reasoning stops here.** A zero-row description's
   own conforming twin IS a file the producer refuses — V1.5 says in as
   many words that the profiler's reader refuses the degenerate forms
   and this one accepts them, and owner decision 7 makes the expected
   byte form the executable subcheck. So closing the gate there would
   silence the obligation on the only file the description calls
   conforming: `bytes.zero-row-form` could never HELD on any file at all,
   the column count, the names and the order would answer only on files
   with rows, and a header-only file could carry any header whatever and
   pass. That is the vacuity V3.4-A1 named this round, and it takes
   review item P3-V3-F5's repair with it. Measured, with that
   alternative reinstated in memory against the shipped suite: **four
   tests go red**, `test_the_headered_zero_row_form_is_the_check` and
   all three of P3-V3-F5's own.

   **What stays open, stated at its size rather than left to be found.**
   Against a zero-row description, the two header-only files above still
   receive different reports, so the header of a file with no rows can
   still be read off one candidate description at a time. What escapes
   is bounded: no measured number of that file is printed except its
   width, no string of it is printed at all (V5.4), and the file in
   question holds no cell, no value and nobody's record — a zero-row
   file identifies no one, which is what the publication floor exists to
   do. It is not claimed to be free.

   **HALF OF THIS RESIDUAL IS NO LONGER A RESIDUAL, AND THE OTHER HALF
   IS** (2026-08-14, owner ruling; amendment A-P3-13). "Read off one
   candidate description at a time" is the reader that ruling puts out
   of scope, so against that reader nothing here is owed and nothing is
   open. What remains open is the same fact seen by the reader who is
   handed ONE report and holds no file: a report on a header-only file
   states, in its verdicts, whether that file's header line spells the
   published names, and describing that file publishes nothing at all.
   The residual therefore stays on the register at the smaller size, for
   the same reason it was left open — closing it costs owner decision
   7's executable check and the four tests below.

   **The owner may want it closed**,
   and closing it costs the four tests above and owner decision 7's
   executable check with them; that is the trade, and it is recorded
   here rather than argued away. A third way would keep the check and
   drop the residual only by making the profiler describe a zero-row
   table, which is a Phase 1 change to what `synthtwin profile` refuses
   and is not this plan's to make.

4. **A file with no rows is one file whether or not its bytes are
   UTF-8. THIS RAISES.** The no-data question was asked of the UTF-8
   reading alone and answered False where there was none, so a
   header-only file whose bytes are not UTF-8 walked past it into the
   reader and came back a REFUSAL at exit 1 with no report, while the
   same file written in UTF-8 got a full report at exit 3. The producer
   refuses both and publishes nothing about either, so which of the two
   answers came back was that file's own encoding, told by the shape of
   the reply rather than by a verdict. The question is now asked of the
   text the reader settled on, both files report, and their reports are
   identical — which is why the encoding rule is one of clause 1's
   eight on these paths.

**How to reverse any of the three.** Clause 1 reverses by settling the
four structural obligations against the first record again and by
printing the two counts, which restores the five-verdict gap measured
above and the row count that moved with the file. Clause 3 reverses by
closing the gate over the zero-row predicates too, which is V5-honest
and was measured rather than reasoned about: it costs the four tests
named there, and the report on a conforming zero-row twin becomes one
with no HELD verdict about its own bytes in it. Clause 4 reverses by
asking the no-data question of the UTF-8 reading alone, which restores
the refusal for one of the two files. Each was reinstated in memory
against the shipped suite to check that the tests which assert it go
red, and each does.

**Amendment A-P3-8 — the claim migration is finished, its guard COUNTS
instead of remembering, and the handling rule reaches the fifth file.
Two clauses RAISE — one of them widening what the institution's rules
are stated over, which is the only direction that rule may move — and
one is machinery that lowers nothing. THE FIFTH FILE IS A CHANGE TO A
SENTENCE THIS PLAN ITSELF FIXED AT FOUR, and clause 2 says exactly what
it costs** (2026-08-14, review items P3-V3-F8, F9 and F10).

**What went wrong, stated before the repair, because the shape of it is
the point.** P3-D7 requires every retired Stage-2 form removed AND
banned, and its catch-all is the claim inventory's ban lists — "a stale
sentence on ANY surface, in the table or not, fails the ban test the
moment its stage lands". It did not. `synthtwin validate` shipped, and
six surfaces went on saying the tool has two commands and that a run
leaves three artifacts, with every test in `tests/test_claim_inventory.py`
green: the twin's report told an auditor, in the contract of the public
function that writes it, that all three artifacts need controlled
handling — leaving out the one that carries measurements taken from the
file that was checked — and the front page walked a reader from a clone
to a twin and stopped, so a README-only reader could follow it to the
end and never learn that the file they now hold can be checked. The
guard could not see any of it, and the reason it could not is worth
more than the six repairs: it was a LIST OF SENTENCES SOMEBODY HAD
THOUGHT TO WRITE DOWN. Nobody writes down the sentence they are about
to forget.

1. **The guard counts what the product has, from the product. It
   changes no obligation; it makes an existing one checkable.** Two
   totals are now derived at import and every surface is held to them:
   the commands, read from the shipped parser's own refusal of a word
   it does not know, and the files a full run leaves behind, read from
   the output-name constants the modules carry and filtered to the
   endings a run's output can have. A fourth command or a sixth output
   file therefore reddens every stale total in the repository on the
   commit that ships it, with no list to remember. Three rules stand on
   those totals — a count of the commands or of the run's files that
   disagrees with them; a built capability placed in a phase, which is
   the shape that left the front page promising that the quality report
   of Phase 3 WILL say so plainly and the generation method telling an
   independent implementer that fidelity measurement and the quality
   report ARE Phase 3; and a runnable sequence that invokes two of the
   three commands and stops. Each was reinstated in memory against the
   shipped suite and each goes red.

2. **The handling rule names the profiler's plain-language summary, so
   it names five files rather than four. THIS RAISES, and it corrects a
   sentence this plan wrote.** P3-D7 stage 2 says "the three-artifact
   handling forms becoming four-artifact forms", and four was wrong the
   moment it was counted in FILES: `synthtwin profile` writes its
   description TWICE, once for a program and once in words, and the
   plain-language half was named on no surface of this project — not in
   Phase 2's three, not in this phase's four. It is not a duplicate of
   the machine-readable half in the sense that matters here: it is the
   one a person reads, it is printed on the screen as well as written,
   and it repeats the published labels and the published endpoints in
   the words a reader will quote. A rule that enumerated four files and
   stopped told that reader, by omission, that the fifth was free to
   travel — which is verbatim the failure P2-D11 was written to close,
   one file further along. **What it costs, stated rather than left to
   be found:** the sentence moves on nine surfaces including the
   charter, both reports' bytes move with it and both goldens were
   re-recorded, and the profile contract's own disclosure sentence gains
   an amendment under counted re-seal. Nothing published moves and no
   check's verdict changes: measured, the two reports differ from their
   predecessors at the handling paragraph and nowhere else, and the
   quality report's census is identical entry for entry, 300 for 300.
   **To reverse it**, drop the summary from the enumeration and put the
   totals back to four — and then say, in the same commit, where a
   reader is told that the file the profiler prints for them is
   real-derived material, because after the reversal no surface says it.

3. **The randomness trap opens every door the module has, and the
   line-ending guard governs a write by what it IS rather than by what
   it is named. Both RAISE; neither changes an obligation.** The trap
   that proves a validate run draws no randomness was a hand-written
   list of 37 names, and `numpy.random.beta`, `poisson` and `binomial`
   went straight through it — a check that could not fail for the calls
   it did not list. It now takes every public callable of every
   randomness module in the process, with a counted floor and a named
   floor beneath it so a derivation that silently returns little cannot
   pass. The line-ending guard governed a `write_text` whose target was
   named `.json` or `.csv` and expressly excluded a file named anything
   else, while the product accepts arbitrary local names: a test writing
   `tmp_path / "measured"` and handing it to `validation.measure` was a
   CRLF file on Windows and outside the rule. The rule now follows the
   file to what it is HANDED TO — a write whose target reaches a
   product entry point that reads a file is governed however it is
   named — and keeps the name-based half beside it, because a file
   written in one function and read in another is still a file the
   product reads.

4. **The necessity claim about hazardous invented cells is withdrawn
   where it is false and kept where it is true. THIS LOWERS a claim,
   which is the honest direction: the claim was not true.** The plan
   recorded that the report "no longer claims the cells were forced".
   It did, in the block above the one that was repaired, and so did the
   generation method — the document an independent implementer works
   from. Both now say it conditionally: where the published counts leave
   no other spelling of that width the inference about the real column
   holds and is stated in as many words; where they do not, the report
   says the twin may carry more such cells than the counts force and
   that it cannot tell the reader which cell is which, and the method
   carries the measured counterexample and says that writing fewer of
   them conforms. **What it costs:** a reader can no longer take every
   sign-leading invented cell as evidence that their own column held
   one. That is not a cost so much as the removal of a false permission
   — and the generation report's bytes moved for it, with the golden
   re-recorded.

**Amendment A-P3-9 — four readings that contradicted the construction
they are a second opinion on, and one of them REJECTED A FILE THE
SHIPPED GENERATOR WROTE. Clauses 1 to 3 RAISE and none of them lowers
an obligation; clause 4 WIDENS one cited envelope in the only direction
this document may take and leaves the other direction as an owner item
against method G12.5. Clause 1 also corrects amendment A-P3-5 clause
2's account of what that amendment did** (2026-08-14, review items
P3-V4-F1, P3-V4-F4 and P3-V4-F5, and one divergence the repair's own
comparison found).

**What they have in common, stated first, because it is the reason they
are one amendment.** V1.4 keeps the generator out of the validator's
import graph so that a verdict cannot inherit the planner's own
defects, and V4.2 says what that costs: the same rule is then WRITTEN
TWICE, once in each module, from the specification. A second writing
that says something the first does not is not a second opinion — it is
a third rule, and every file is measured against a construction that
does not exist. Each of these was such a writing, each was found by
comparing the two rather than by reading either, and the repair in
every case is the same: write the rule out from the method, and put the
comparison in the suite so the next drift is red on the commit that
writes it. **Two of the four were not in the review at all**: the
review named the pinning and the 119, and writing the window out from
the method found the ladder being read with floating-point arithmetic
in the wrong unit, while extending the comparison to a column that
carries offsets found the fourth.

1. **A cell the file's own description reads as DATA is measured, not
   deleted. THIS RAISES: two obligations that reported MISSED on
   conforming files now report what is true of them, and no obligation
   is weakened.** Amendment A-P3-5 clause 2 sends the gated side of a
   pooling column a cell list with the disputed spellings removed; the
   implementation removed every built-in missing spelling and every
   built-in numeric stand-in unconditionally. The producer reads
   neither kind as a hole where the description names it as data, and a
   researcher who keeps `-999` as a real measurement has a description
   that does — `--keep-value -999`, published as the candidate verdict
   `kept_by_you`. Measured here, on the shipped code: a sixty-row
   description with eleven kept `-999` readings, forty-eight decimals
   and one pooled blank, against **the twin `synthtwin generate` writes
   from that very description**, gives 60 HELD, 15 WITHIN, 0 WITHHELD,
   **2 MISSED** and exit 3 — `styles.at-least.plain` and
   `styles.remainder` — where the repaired reading gives 62 HELD, 15
   WITHIN, 0 MISSED and exit 0.

   **The route the review named is one of four, and the class is the
   other three.** A description names a spelling as data by every
   published route of V2.3, and the FILE's own description names one
   more: a stand-in it read as an ordinary number because the column's
   own spread makes it no outlier. That one is not rescuable from the
   submitted description at all, and it was live on the same line: a
   sixty-row column of readings around minus a thousand, measured
   against **the very table it was described from**, reported the same
   two obligations MISSED. Its twin holds no `-999` cell at all, so a
   repair tested only through the generator would have called that
   route closed.

   **What the reading is now, and what it leaves open at its exact
   size.** A cell is dropped only where the file's own description reads
   it as a hole: the producer's own order is followed — the settings'
   kept set first, the built-in table of missing spellings next, and a
   stand-in's fate is the column's own published verdict on that
   candidate — and where that description publishes no verdict for a
   candidate, because fewer than `small_cell_floor` cells share it, the
   one number it does publish settles it: how many of its cells are
   non-blank and read as holes. Where the certain holes already account
   for all of them, nothing more is dropped. **What is left open** is
   the case where they do not: a column whose description pools some
   missing source AND holds a sub-floor stand-in it keeps as data AND
   reads some other non-blank cell as a hole loses those sub-floor cells
   from its recount. That is at most `small_cell_floor - 1` cells per
   candidate, it is residual R-P2-13's own corner, and clause 1 of
   A-P3-5 already records that corner as a place a value reading back
   as a hole can cost a verdict. **The confidentiality half is
   untouched and is asserted rather than argued:** the recount never
   keeps a cell the file's own description does not count as a value,
   and two files that description cannot tell apart still get the same
   census, on a column holding kept stand-ins.

2. **The datetime rank window is the METHOD's, ends pinned and
   allowance the method's own. THIS RAISES: a bound that passed a file
   the construction forbids now misses it, and a rung that missed by
   most of a minute is no longer called WITHIN.** Method G12.4 pins rank
   `0` to the published `earliest` and rank `P - 1` to the published
   `latest` — G7.3 writes those two cells from the endpoint's own
   fields, so they have no room at all — and the shipped validator gave
   both of them the interior band. G12.5's separateness walk then let
   the first window swallow ranks that cannot share its instant.
   Measured: a twelve-rank quarterly description against twelve rows
   holding six different quarters, both published ends among them,
   reported `n_distinct` and `n_distinct_folded` **WITHIN** a window
   whose lower end the pinned construction puts at seven. The same file
   now MISSES both, with both ends still HELD. (The review's own witness
   passed four where the construction forces five; its published
   quarters are not recorded, so the file kept in the suite is one of
   the same shape rather than that one.)

   **And `u` is one unit of the ordinal SPACE, not one step of the
   published precision.** G12.4's allowance is "one unit for the
   downward rounding of the whole-number interpolation itself, plus 59
   seconds where the precision is minutes"; the ordinal unit of a column
   of dates and times is ONE SECOND whatever its precision, so the
   allowance is 60 and the validator used 60 + 59 = 119. Measured: a
   sixty-minute sequential description against three cells at the first
   minute, fifty-six at the second and one at the last reported
   `date-ladder.p05` WITHIN a window it sits a whole minute below. **The
   previous round's own repair test asserted the 119**, and no fixture
   in the suite published minute precision at all, so the branch was
   reached by nothing: the test was written around the implementation
   instead of around the method, and a test that reads the code it
   checks can only ever agree with it. The suite now walks the
   producer's own list of precisions, so a precision with no fixture is
   red on the commit that adds it.

3. **The ladder is read by the method's whole-number interpolation, in
   the method's own unit. THIS RAISES, it was found by writing the rule
   out rather than by patching the two numbers above, and it removes a
   false rejection nobody had reported.** G12.4 reads `Ladder_d` "by the
   same whole-number interpolation G7.3 builds cells with", and "no
   float is formed anywhere in G7" is the method's sentence about that
   space. The validator read the datetime ladder with the piecewise-
   linear FLOAT reader the numeric ladder uses, and worked the rung's
   rank out through a floating-point share. Those are different
   functions: the float reading sits above the method's floor by the
   fraction the floor discards, so a window's low end was up to one
   ordinal unit too HIGH — the strict direction, which is a conforming
   twin reported MISSED. It also hid the third divergence, since one
   fixture's rungs happened to sit where the difference did not show.
   For a column of whole DATES the two writings differ by up to a whole
   day, because the method's unit there is one day and this reading
   counts in seconds, and a floor does not commute with a change of
   unit. The suite now compares the two writings of the window itself —
   every rank, at eight column heights, at every resolution and every
   precision the producer can publish — rather than comparing the
   ordinal spaces and reasoning that the rest follows.

   **What moved in the shipped output, and the one direction of it that
   is a WIDENING, said plainly.** The demonstration twin's quality
   report changes at eleven windows of one column: every one of the nine
   rung windows of `recorded_on` now ends on a whole day where the
   seconds-floored reading ended part way through one — `between
   1703980800.0 and 1704132000.0` ended at two in the afternoon, which
   is not an instant a column of whole dates can hold at all — and the
   two distinctness lines read `84 (between 106.0 and 240.0)` where they
   read `119.0`. **That lower end moved DOWN**, so a file whose date
   distinctness lands between the two numbers is now reported WITHIN
   where it was MISSED. **It is not a bar this plan is lowering, and the
   difference matters:** G12.5 fixes that envelope, this document cites
   it and may not restate it, and V3.5 says in as many words that a
   narrower envelope is the generation method's change to make. The old
   number was a bound the validator drew for itself out of arithmetic
   the method does not use — the same arithmetic that would have
   reported a conforming twin MISSED at a rung. Withdrawing an invented
   bound and reporting the cited one is the only reading V1.4 leaves.
   Anyone who wants the tighter bound writes it into G12.5, where the
   generator will be held to it too. The census is unchanged entry for
   entry and the golden is re-recorded.

   One registered red case moved with it and is named rather than
   quietly rebound: `date-ladder.p10` on the quarter fixture was covered
   by an edit that piles the column's middle LOW, and that rung's window
   begins AT the published earliest, so no file can miss it from below —
   the edit could only appear to catch it while the window was a
   fraction of a quarter too narrow. The battery gains the same edit the
   other way up, and the rung is covered by a case that can actually
   fail it.

4. **A fourth divergence the comparison found, resolved in the only
   direction this document may take, and left as an OWNER ITEM against
   method G12.5.** The upper end of G12.5 multiplies the instants a
   range holds by `M`, "the number of named offsets", and derives that
   from every cell being "spelled with one of the offsets `utc_offsets`
   names by name". G7.4 says otherwise about two of that map's keys: a
   cell allocated `(none)` is written with NO offset, and so is one
   allocated `(withheld)` — "and this is a loss, named as one". So a
   column mixing a named offset with either key writes its instants one
   more way than `M` counts, and the generator's own writing of `M`
   counts the named offsets alone. **The validator takes the wider
   reading — one per named offset, plus one where any cell is written
   with none —** because the tighter one is a bound a conforming twin
   can be reported MISSED against, and V3.5 says a narrower envelope is
   the generation method's change to make and not this document's. The
   two readings are identical on every column that does not mix the
   two, so no verdict on any existing fixture moves, and the suite pins
   where they may differ with a column reaching all three keys.
   **The owner item:** G12.5's upper end is understated for such a
   column in the generation method itself, so the generator's own report
   can name `n_distinct` a deviation on a twin that is doing exactly
   what G7.4 tells it to. Fixing that is a Phase 2 method change with
   its own counted re-seal; nothing here does it quietly.

**Amendment A-P3-10 — two guarantees this plan wrote down that the code
did not have, and the class behind the second. Clause 1 RAISES a
confidentiality bound from "the exact count, by candidate search" to
"the count at the publication floor's own resolution" and LOWERS one
subcheck's teeth by less than one floor, priced exactly; clause 2 makes
an equivalence hold BY CONSTRUCTION, which RAISES, and LOWERS one line
of detail in one refusal and one report; clause 3 corrects amendment
A-P3-7 clause 2's account of what it did. THIS DEFINES WHAT A RULING
THAT PUTS A FACT OUTSIDE THE ENVELOPE OWES, AND CLAUSE 1 SAYS WHAT
REVERSING IT COSTS** (2026-08-14, review items P3-V4-F2 and P3-V4-F3).
**CLAUSE 1'S REPAIR IS WITHDRAWN BY AMENDMENT A-P3-13 CLAUSE 2 AND ITS
TEETH ARE BACK AT ONE CELL; clauses 2 and 3 stand unchanged, and what
this amendment says a ruling OWES is narrowed to the half a report's
reader is protected by** (2026-08-14, owner ruling, later the same day).

**What they have in common, stated first, because it is the reason they
are one amendment.** V5 is not a rule the code follows; it is a
PROPERTY the code either has or does not have, and both of these were
written into this document as properties and then not had. One was a
bound a ruling carried — a ruling may put a fact outside V5.1's
envelope, and what makes that rulable rather than convenient is the
size of what escapes, so the size is the whole of the ruling. The other
was an equivalence two pieces of code were supposed to keep between
them by hand. Neither survived being measured. A bound nobody measures
is a sentence, and an equivalence nobody constructs is a maintenance
task somebody will lose.

1. **THIS CLAUSE'S REPAIR IS WITHDRAWN BY AMENDMENT A-P3-13 CLAUSE 2,
   AND THE TEETH IT PRICED ARE BACK** (2026-08-14, owner ruling). Read
   the clause as written for the record it makes — the exact-oracle
   measurement stands, and so does the price — but the rounding
   function it installs no longer exists: the owner has ruled the
   candidate sweep out of scope, the recount is compared exactly again,
   and a file ONE cell over its licence MISSES. Round 5 also measured
   that the rounding never had the bound stated below, because the
   publication floor is itself a number the submitted description
   chooses. Everything this clause says about what a ruling of the
   "outside the envelope" kind OWES is narrowed by A-P3-13 clause 1 to
   the half a report's reader is protected by: it prints no measured
   count.

   **The canonical ceiling reads its recount at the publication floor's
   own resolution, so a sequence of candidate descriptions locates the
   block and not the count. THIS RAISES the bound amendment A-P3-5
   clause 3 claimed and did not have, and LOWERS that subcheck's teeth
   by less than one floor.** A-P3-5 clause 3 ruled canonicality outside
   V5.1's envelope on a stated bound: "neither subcheck prints a
   measured count", and "what a report can carry is one bit per column".
   The first half is true. The second is not, and `styles.canonical.
   <form>` is where it fails: it compares the exact number of cells of a
   form that are not their own value's canonical text — a number the
   producer publishes about no file at any count, which is the very
   ground the ruling stands on — against the count the SUBMITTED
   description names. So the verdict flips at exactly that number.
   Measured here, on the shipped code, on a sixty-row column carrying
   forty-eight `decimal` cells of which thirty-seven are written with a
   leading zero: candidate descriptions publishing 0, 11, 15, 20, 25,
   30, 33 and 36 `decimal` cells give MISSED and 37, 38, 40, 44 and 48
   give HELD. **The flip sits at thirty-seven, which IS the hidden
   number**, so a bisection over the column's own length reads it out.
   And two measured files carrying thirty-six and thirty-seven of them —
   whose full descriptions `synthtwin profile` writes BYTE FOR BYTE
   ALIKE — got HELD and MISSED.

   **The repair is one function and it is the only way the recount
   reaches a verdict.** `_at_the_floors_resolution` rounds the recount
   DOWN to a whole number of publication floors before the comparison,
   so the same sweep now flips between 30 and 33 — three floors of
   eleven — and all it establishes is that the count lies between 33 and
   43, whatever else is asked. That is
   the resolution the producer's own floor sets everywhere else: a
   description names no count below `small_cell_floor` and pools every
   one of them (V5.4), so a report that cannot separate two counts
   inside one such block states nothing that description would not.
   **Rounding DOWN is the direction that cannot accuse a file**: the
   result is never more than the count, so a MISSED here is a file
   genuinely over its licence and a conforming twin — whose count is at
   most its licence — is HELD whatever the floor is.

   **What it costs, priced rather than left to be found.** A file
   between ONE cell and one floor over its licence is no longer missed
   at this subcheck. The round-1 red case moved with it, from "one cell
   over the licence" to "one floor over", and both halves are pinned:
   the file one cell over is asserted HELD, so the cost cannot grow back
   into the oracle unnoticed. **And there is no third way**, which is an
   argument rather than a preference: the licence is a number the
   submitted description chooses, so a verdict that separates a count of
   `p` from a count of `p + 1` for every `p` IS an exact oracle on that
   count, whatever else is done to it. Teeth at one cell and a bound
   better than exact cannot both be had.

   **What is left open, at its exact size. THIS PARAGRAPH IS SUPERSEDED
   BY AMENDMENT A-P3-13 CLAUSE 2 and is kept only as the record of what
   this clause bought while it stood** (correction of 2026-08-14, review
   item P3-V6-F3; the paragraph was true when it was written and stopped
   being true the day `_at_the_floors_resolution` was deleted, and no
   line said so). What follows describes the floor-rounding bound. There
   is no floor-rounding bound: the second reader is out of scope, the
   function is gone, and the recount is compared exactly, so a sweep of
   candidate descriptions locates the count of non-canonical cells
   EXACTLY and this plan does not try to stop it. Read A-P3-13 clause 2
   for what the subcheck does now.

   As it stood, and it no longer stands: for a form the FILE's own
   description NAMES, a candidate sweep located the count of
   non-canonical cells to within one publication floor — eleven by
   default — and no closer, and it reached neither which cells they are,
   nor their values, nor their spellings.
   Where that description POOLS the form nothing escaped at all: that
   side of the subcheck reports HELD where the room the description
   leaves cannot reach the licence and WITHHELD otherwise, and never
   consults the recount — and THAT half is unchanged and still holds.
   And a description written under a floor of ONE was the identity —
   such a description names every count it has exactly and pools
   nothing — so the bound degraded exactly as far as the person who set
   that floor asked it to.

   **How to reverse this.** Settle the clause from the window on both
   sides, which is V5-honest and leaks nothing: HELD where the room the
   file's own description leaves cannot reach the licence, WITHHELD
   where it can. It was reinstated in memory against the shipped suite
   and it costs the subcheck's whole ability to verdict — the odd cells
   of a form are a subset of that form's cells, so the recount can never
   exceed what that description already allows, and the subcheck could
   then never report MISSED on any file. That is the vacuity V3.4
   refuses by name; it reverses this plan's own P3-D8.1 ceiling and
   takes review item P3-V1-F7's repair with it. Measured: **eleven tests
   go red**, including `test_every_registered_red_case_misses_the_site_
   it_names` and the entry table's coverage identity.

2. **The report on a file the producer REFUSES is chosen by the refusal
   the reader actually raises, so the equivalence V5.1-A1 promises holds
   BY CONSTRUCTION. THIS RAISES: a whole class closes rather than four
   paths. It LOWERS one line of detail in one refusal and in one
   report.** Amendment A-P3-7 put two of the reader's refusals on the
   reporting side, because V9 makes a structural mismatch a MISSED
   verdict with a plain explanation. The shipped code decided WHICH of
   those two reports a file gets by walking the file itself, before the
   reader was called — two predicates of the validator's own, over the
   validator's own record walk. The reader asks the same two questions
   in its own order, with a zero-byte check and a ragged check standing
   between them, so the two readings had a PRECEDENCE to agree about as
   well as a pair of answers. Four ways they did not, measured here with
   the shipped predicates reinstated in memory:

   - `dup,a,dup` and `a,dup,dup` over the same forty rows draw one
     sentence out of `synthtwin profile` — it quotes the repeated NAME —
     and drew two reports, differing at `header.names` and
     `columns.order`, which carried the two column numbers;
   - a NUL-bearing header alone and the same header with one data row
     under it draw one sentence out of the producer — the reader raises
     its zero-byte refusal inside its own streaming loop, before it has
     counted a row — and drew a REPORT and a REFUSAL, so the existence
     of that row was told by the shape of the reply;
   - a ragged file and the same ragged file with a name repeated in its
     header draw one sentence — the reader refuses for raggedness first
     — and drew a REFUSAL and a REPORT. The same with a name left blank;
   - and the same three files reached that report at all, which is a
     report about a file no reading of it finished.

   **The repair is a construction and not a rule.** There is no second
   walk: `measure` calls the reader, catches the refusal, and chooses
   the report from WHICH refusal it is — a word of the error module's
   own vocabulary carried on the refusal object, so nothing matches on
   prose. Two files the reader refuses with the same word cannot reach
   different reports, because the same word chooses the report. The
   suite asserts the rule itself over a battery crossing every refusal
   the reader has: **two files `synthtwin profile` refuses with the same
   sentence get the same report**, with the four routes above among the
   named cases. The header-presence question is answered from the
   reader's own first record for the same reason, so the last second
   reading of the bytes is gone from that path too; no obligation
   changes.

   **What it costs, and it is two things.** The checked-file
   repeated-name REFUSAL and the repeated-name REPORT no longer name the
   two column numbers — clause 3 says why that is a correction and not a
   loss — so a person told their checked file repeats a name is told
   which fault it is and not where. The blank-name case is unchanged and
   still names its position, because the profiler's own refusal for that
   one names it. And a file the reader refuses for something else BEFORE
   it reaches the header question — ragged, a zero byte, a blank line in
   a one-column file — now comes back as that refusal where it used to
   come back as a header report. Nothing is lost by that beyond a
   report: the refusal is the more actionable of the two, it is the one
   `synthtwin profile` gives for the same file, and every obligation
   that report would have missed is one no file reaching there can meet.

3. **Amendment A-P3-7 clause 2's account of its own naming was wrong,
   and this corrects it in place.** That clause reads "the profiler's
   own form of that refusal quotes the repeated NAME, so naming
   positions publishes strictly less than describing the file would".
   The two are not ordered: a NAME and a pair of POSITIONS are different
   facts, and the positions are not derivable from the name. `dup,a,dup`
   and `a,dup,dup` are the counterexample and it is one line long — one
   refusal between them, two reports. The clause's ruling that the
   report may state what the refusal states stands unchanged and is
   right; what was wrong was the claim that the numbers were inside it.
   Clause 2 above is the repair, and V5.1-A1 is corrected with it.

**Amendment A-P3-11 — `--smallest-group` below eleven runs the whole
workflow, and every file the run leaves says so. THIS LOWERS a
confidentiality bound, on the owner's ruling of 2026-08-14, and prices
it here rather than softening it. It RAISES what four artifacts must
state about themselves** (2026-08-14, owner ruling; the question put to
the owner was what `--smallest-group` should do when given a value below
eleven, and the ruling was: let it through everywhere).

**The defect the ruling closes.** `synthtwin profile t.csv
--smallest-group 2` exited 0 and wrote both files. `synthtwin generate`
and `synthtwin validate` then refused that description, because contract
4.4 required `small_cell_floor >= 11` and the strict loader enforced it
— and the refusal ended by telling the person to make the description
again by running `synthtwin profile` and to use the file exactly as it
writes it, which is precisely what they had done. A documented option
produced an unusable file and a refusal that could not be acted on.

1. **The contract's minimum moves from eleven to one, and the loader
   with it. THIS LOWERS.** `docs/spec/profile-contract-v4.md` section
   4.4 and its glossary row carry the amendment in place, under a
   counted re-seal. What is given up is stated there at its size and is
   restated here because this plan is where a bar is lowered or not: the
   floor is the whole of what keeps a published group too large to point
   at one person, and at a floor of `f` a description names groups of
   `f`. Where one row of the real table is one person, a description
   written at a low floor publishes that a value exists together with
   how many people have it — and at a floor of one, that exactly one
   person has it. The count is the disclosure, not a route to one.

   **What is NOT lowered, and it is the larger part.** Every
   floor-governed invariant is written as "at least the floor" and
   "below the floor" and still binds at the value the document carries:
   B5, D3, N2, N4, P2, V1 and W5 hold at `f` exactly as at eleven. At
   `f = 1` the "below the floor" half is the empty range, so nothing may
   be held back at all and `suppressed_level_counts`,
   `variants_withheld` and every pooled `(withheld)` remainder must be
   empty; a document that fills one is refused for breaking the
   invariant it always broke. Zero and below are still refused under
   R16: "below the floor" at zero would name counts of nothing at all,
   and no count is. **One is the smallest workable floor**, measured
   rather than assumed — the sweep is recorded in clause 4.

   **On whose authority.** The owner's, ruled 2026-08-14, with the
   consequence stated and accepted. No review verdict and no
   implementer's judgment stands behind this clause.

2. **Four artifacts must say on their own face that the description was
   made under a lowered floor. THIS RAISES.** The reasoning is the one
   that put the handling rule on all five files (amendment A-P3-8
   clause 2): a person is handed ONE of these files, not the set, and
   the floor lives in the description's JSON as a number a
   non-programmer does not open. So the profiler's plain-language
   summary, the generation report and the quality report each state it
   without reference to the others, and the `profile` command prints an
   unmissable warning BEFORE either file exists — the same ordering
   control P1-D6 fixes for the disclosure itself. Each of the four says
   what a group that small can reveal about a person, in those words:
   not "the floor was lowered" but that somebody who already knows one
   true thing about a person in the table can find the small group that
   person must be in and read the rest of what it says.

   **The twin CSV is the fifth file and carries no sentence**, because a
   CSV has nowhere to put one without corrupting the table its whole
   purpose is to be. Its report is written beside it and is one of the
   four; that is the same reasoning under which the twin has always
   carried its warnings in the report rather than in the cells.

   **All four are CONDITIONAL, and that is the opposite of the rule the
   honest bounds are written under.** A limit true of every run is
   printed on every run so that nobody comes to expect its absence.
   These state a fact about ONE description that is false of an ordinary
   one, and a paragraph appearing on every run to say the floor was NOT
   lowered is how a reader is trained to skip the paragraph that
   matters. The bytes of a report made at the default floor are
   therefore unchanged by this amendment, with one exception, which is
   clause 3.

3. **The quality report names the floor it is running at, on every run.
   THIS RAISES.** Its withholding rule read "a group fewer rows carry
   than the publication floor is never named in any description — that
   is what the floor is for". That was written when every description
   had one floor. It is not one number any more, so "any description"
   now invites a reader to supply eleven and be wrong about what the
   lines above are showing them. The number is printed at the point
   where it decides something, which is also the one place a reader of
   an ordinary report is told what protects them. **This is the only
   change to the bytes of an artifact made at the default floor**, and
   `GOLDEN_QUALITY_SHA256` is re-recorded for it in the same commit,
   with the diff read line by line first.

   **And `validate` is deliberately the loudest of the four**, because
   it is the file that travels: the quality report goes to whoever is
   deciding whether to trust a twin, and under a lowered floor its
   obligation lines print published and measured counts down to that
   floor where at eleven they would have been withheld. Its section says
   that in as many words. The gate itself is unchanged — it asks what a
   description of the measured file would publish, and under a lowered
   floor such a description names small groups — so what changed is what
   the report tells the reader about its own reach, not the reach.

4. **The sweep for arithmetic that assumed eleven, and its result.**
   Every floor-consuming site was read and the whole workflow was run at
   floors 1 and 2 end to end. Three sites take a value derived from the
   floor rather than the floor: `_recount_window`'s `room = floor - 1`,
   which is clamped at zero and correct at one; `_at_the_floors_
   resolution`, whose own docstring already ruled the floor-of-one case
   the identity (amendment A-P3-10 clause 1); and `_multiplicity`, whose
   permitted key range is `1 .. floor - 1` and which at a floor of one
   is the empty range. The last of the three composed its refusal as "a
   number of rows from 1 to 0", which is a sentence sending a person to
   look for a number that cannot exist, and it now says the block must
   be empty and why. **Nothing else in the product reads the floor as a
   magnitude.** The generator reads it not at all — contract 4.4 makes
   the settings subtree loader-only — so no published count and no
   window moves with it.

   **One wart is recorded rather than repaired**, because it lives in a
   file this change was told not to edit: `validation._below_the_floor`
   prints "fewer than 1" for a published label the measured file does
   not hold at all, on a description written at a floor of one. It is
   true — zero is fewer than one — and it is the correct verdict path;
   it reads oddly. The honest wording is "not there at all" and it is
   one line in `validation.py`.

**Amendment A-P3-12 — the fold-collision layout is CHECKED against what
the families actually supplied, and repaired where a collision could
not be built. THIS RAISES: a published `n_distinct_folded` the twin
missed on 3.7 per cent of a battery of descriptions a real producer
wrote is met on every one of them. It LOWERS nothing, and the one
thing it costs is priced below** (2026-08-14, owner ruling on the
recorded fidelity miss; the question put to the owner was repair the
fold feasibility or authorize the miss, and the ruling was: fix the
generator now).

> **CORRECTION OF 2026-08-14, review item P3-V6-F2.** Clause 2 below
> reads "zero, on both batteries", and clause 5 gives the one thing
> still open as budget exhaustion. **Both were measured on two batteries
> and neither is true of every description.** A third battery, built to
> the shape the review's own witness has, found the miss again on 12 of
> 4,696 runs — and the cause was not the budget being spent, it was the
> budget being spent on questions already answered. That is repaired by
> amendment **A-P3-17 clause 2**, which also measures what remains: **4
> of those 4,696 runs, one column at four seeds, and its cause is
> neither of the two named here.** Read A-P3-12 as what it measured on
> the two batteries it built, not as a statement about every
> description. What A-P3-17 replaces is the reach of the claim, not the
> rule.

**The defect the ruling closes, in the terms the study that found it
left it.** A column of record numbers publishing fewer folded
identities than raw spellings owes `n_distinct - n_distinct_folded`
collisions, and G9.3 settles which slots carry them BEFORE any spelling
exists. What a family can supply is a fact about spellings: its
identities' own case positions, and whatever edge spacing their lengths
leave inside the taking slot's window. Edge spacing only LENGTHENS, so
an identity pinned to the longest published length supplies no spaced
partner at all; a family whose flips are spent supplies no further one.
A layout could therefore ask one family for more collisions than it
holds while another family of the same column had room to spare, and
the twin then wrote a fresh identity where a partner was owed. The
pre-generation feasibility check `_fold_room` never fires on these: it
counts the whole wide alphabet and knows nothing about families, slots
or windows.

**Measured before anything was changed, twice, on two independently
built batteries of hazard-shaped producer descriptions — every column
built from real values, so the column's own multiset is a conforming
assignment of every count its description publishes.** On the battery
the earlier study built, 1,200 columns at seed 0: **44 missed
`n_distinct_folded`, 3.7 per cent**, which reproduces that study's
recorded number exactly. On a second battery built for this amendment,
918 columns that publish a fold collision, at seed 0: **68 missed it,
7.4 per cent**. At four seeds the two batteries give 176 of 4,800 runs
and 272 of 3,672 runs. Every miss was `n_distinct_folded` and no other
published fact was ever missed.

1. **The layout is laid out again where a collision could not be
   built, and the layouts are offered in a fixed order whose FIRST
   member is the layout that shipped. THIS RAISES.**
   `docs/spec/generation-method-v1.md` section G9.3 carries the rule as
   a new step 5 and G9.6's collision-slot bullet points at it, under a
   counted re-seal. Four handles, in this order: the shipped layout
   unchanged; then every family that fell short asked for no more
   collisions than it was just shown to supply; then the slots carrying
   the two published length ends offered a collision before any other
   slot of their family; then each further exact packing of G9.6,
   including the packings its search reaches by holding one group to
   one family. At most two hundred and fifty-six candidate packings are
   examined on one column, and where every offered layout falls short
   the column keeps the first and the shortfall is recounted from the
   finished cells and named, exactly as before.

   **Why this is not the change that was rejected on 2026-08-13.** That
   proposal re-ranked the collision choice on EVERY column, and an
   adversary measured it losing `n_distinct_folded` on twelve runs of
   this project's own 200-description battery while cutting hazardous
   cells there by zero. This one cannot reach a column the shipped rule
   already answered: the shipped layout is offered first and is
   returned the moment it supplies every collision it owes, so a
   description that layout answers is answered by it, byte for byte.
   The property is measured rather than argued — see clause 3.

2. **After: zero, on both batteries, at four seeds.** Shipped 44 of
   1,200 and 68 of 918 at seed 0; repaired **0 and 0**. At seeds 0, 1,
   17 and 63: shipped 176 and 272 runs missing, repaired **0 and 0**.
   No run of either battery, before or after, missed any published fact
   other than `n_distinct_folded`, and every miss that remains — there
   are none on these batteries — is named in the generation report as a
   deviation carrying the published value and the achieved one.

3. **What it does NOT move, measured rather than asserted.** On this
   project's own 200-description identifier battery at four seeds, 800
   runs: **not one byte moved**, no run missed a fact before or after,
   and the count of cells opening with a character a spreadsheet reads
   as a formula is 140 before and 140 after. Across both hazard
   batteries the same property holds run by run: **every run whose bytes
   moved is a run the shipped generator got wrong**, 176 of 176 and 272
   of 272, and no run that was exact before is exact-but-different
   after. All fifteen frozen generation reference vectors and their
   mutants pass unchanged.

4. **What it costs, priced rather than left to be found.** Two things,
   and both are named here because this plan is where a price is paid.

   **First, spreadsheet hazards, on two columns in 1,200.** The cells a
   twin writes that open with a formula leader are counted in the bound
   this plan states above; the repair moves them only inside the columns
   it repairs. Measured over the 1,200-column battery: 42 of the 44
   repaired columns write the same number as before, and two write 9
   and 12 where they wrote none — 1,036 cells to 1,120 over four seeds.
   No column writes fewer. On the 918-column battery the total is
   unchanged at 744. Nothing published is traded for this: the columns
   in question now meet a published count they missed, the hazardous
   cells are named in the report as they always were, and the bound
   this plan states — that carrying more of them than the counts force
   is a limit of synthtwin — is where it was.

   **Second, work, bounded and counted.** A column whose first layout
   supplies every collision costs exactly what it cost before: the
   packing search stops at its first success, as it always did, and the
   repair never runs. A column that falls short is the one that carries
   the cost of the further layouts, and it carries all of it. Measured
   end to end on the shipped code, the old rule against the new over the
   same 4,800 and 3,672 generations: **16.1 seconds to 18.5, and 26.0 to
   27.9** — fifteen per cent and seven, with every failing column of
   both batteries included in the total. The deepest single column of
   either battery examined **twenty-one** candidate packings against the
   stated ceiling of 256.

5. **What is still open, said plainly.** Both batteries are batteries;
   they are wide but they are not a proof. The rule ends in a stated
   number of steps and a description can spend that budget, so the
   deviation path is live and is the reason it is still built and still
   named. And the divergence this plan already records at P3-D8.1 —
   that the reference oracle models neither `_collision_order` nor this
   repair, and raises rather than states cells for a description whose
   collisions cannot be built — is unchanged and is not widened: the
   repair is reachable only on descriptions for which that oracle
   already refuses to state an answer, so no frozen case reaches it and
   none can be added without widening the oracle first.

**Amendment A-P3-13 — the quality report stops promising that a person
who writes the descriptions cannot narrow a withheld number by running
the check again. THIS LOWERS A CONFIDENTIALITY GUARANTEE, on the
owner's ruling of 2026-08-14, and prices it here rather than softening
it. Clause 2 RAISES one subcheck by exactly the amount amendment
A-P3-10 clause 1 priced, which is the one place the code was paying for
the withdrawn promise and can stop** (2026-08-14, owner ruling; the
question put to the owner was whether the validator should defend
against someone submitting hand-crafted descriptions to extract hidden
numbers, and the ruling was: no — say so honestly instead).

**What was promised, in the words this plan and the specification used.**
V5 says the report may state about the measured file only what
`synthtwin profile` run on that file would publish, and P3-D3 and V5.3
extended that to the VERDICT as well as the value on a stated ground:
"repeated candidate profiles would otherwise binary-search a value the
file's own profile withholds". So the guarantee had two readers in it.
One is handed a report. The other writes descriptions, runs `validate`
on the same file with each, and reads a hidden number off which verdicts
flip. Rounds 3, 4 and 5 each found a route open to the second reader —
the pooled style counts (P3-V3-F2), the header of a file the producer
refuses (P3-V3-F3), the canonical ceiling twice (P3-V4-F2, and round 5's
verification that A-P3-10 clause 1 had not closed it either) — and
closing each cost checking strength that is written down in this plan.

1. **The second reader is out of scope. THIS LOWERS.** No rule in this
   plan or in the validation method is written to stop a person who
   holds the measured file from narrowing a withheld number by
   submitting descriptions of their own and watching the verdicts move.
   Where such a person can do it, that is a limit of the product and not
   a defect in it, and it is written where a reader meets it rather than
   where a maintainer would: the specification's V5-A1, the validator
   module's own contract, and the quality report's own page.

   **On whose authority.** The owner's, ruled 2026-08-14, with the
   consequence stated and accepted. No review verdict and no
   implementer's judgment stands behind this clause.

   **The reasoning, and exactly how far it reaches.** Running this check
   on a file requires holding the file: `validate` answers questions
   about a file whoever runs it already has in hand, and a question
   they could settle by reading that file is not one this product has to
   refuse. **What the reasoning does not reach is the report itself**,
   which is a separate artifact that travels to people holding nothing —
   so every rule about what a report SAYS binds exactly as before.

   **What is given up, at its size.** For a numeric column, the count of
   cells written in a form but not in that form's canonical spelling can
   be recovered exactly by a sweep of candidate descriptions (clause 2
   makes that sweep shorter, and it worked before clause 2 anyway). For
   a column whose own description pools a style count, a sequence of
   candidates can pin the sub-floor count, which is the witness A-P3-3
   clause 1 recorded. For a file the producer refuses — one with no rows,
   or with an unusable header — the header's names and the file's width
   can be narrowed one candidate description at a time, which is the
   residual A-P3-7 clause 3 recorded and priced. **In every one of them
   the person doing it holds the file the number is about.**

   **What is NOT given up, and it is the larger part.** V5.4 is
   untouched: no measured value, no string of the measured file, and no
   count its own description pools is ever printed — not in the report,
   not on the screen, not in a refusal — and V9's refusals still name
   positions rather than content. V5.1 binds on every surface for the
   reader of ONE report, which is the reader who may hold nothing, so
   two files `synthtwin profile` describes alike still get one report
   wherever that fact is inside the envelope, and the equivalence
   A-P3-10 clause 2 made hold by construction still holds. Every
   withholding this plan records stands: A-P3-3 clause 1's style
   windows, A-P3-5 clause 1's pooled-description verdicts, A-P3-7 clause
   1's seven withholdings on the refused paths. **None of those was
   bought by this defence alone** — each has a measured witness in which
   ONE report told two files apart — so none of them is handed back
   here, and this amendment lowers no bar that reasoning does not
   already require.

2. **The canonical ceiling reads its recount EXACTLY again, and a file
   one cell over its licence MISSES. THIS RAISES, by exactly what
   amendment A-P3-10 clause 1 priced.** That clause put every recount of
   non-canonical cells through `_at_the_floors_resolution`, which rounds
   it DOWN to a whole number of `small_cell_floor` before the comparison,
   so that a sweep of candidate descriptions could locate the count no
   closer than a floor-wide block. It priced what that cost in one
   sentence: **"A file between ONE cell and one floor over its licence is
   no longer missed at this subcheck."** With the second reader out of
   scope the rounding buys nothing this plan promises, so the function is
   deleted — not left unused — and the one call site compares `odd`
   against the licence again. V5.3-A2 is withdrawn in place and says so.

   **Why this one and not the others.** Whether a numeric cell's TEXT is
   a spelling its own value licenses was already ruled OUTSIDE V5.1's
   envelope (A-P3-5 clause 3, on the test that the producer publishes it
   about no file at any count). So the single-report equivalence never
   governed this subcheck, by ruling; two files described alike getting
   different verdicts here is what that ruling authorized in as many
   words. What A-P3-10 clause 1 added on top was a bound against the
   candidate sweep, and the sweep is the one thing the owner has now put
   out of scope. Every other lowering in this plan has a single-report
   witness underneath it and therefore stays.

   **And it did not even buy what it cost.** Round 5 measured the sweep
   working straight through it: `small_cell_floor` is itself a number the
   submitted description chooses, so varying the floor from 11 to 48
   against a fixed file made the subcheck miss for floors 11 through 37
   and hold from 38 up, and the largest missing floor IS the hidden
   count. That is recorded as fact and not as the reason — the reason is
   the ruling — but it settles that nothing measurable is being traded
   away by the deletion.

   **What this raises, counted.** Every numeric column whose description
   NAMES a canonical form regains a verdict at one-cell resolution:
   measured on the shipped suite's own fixture, a sixty-row column
   licensed for 24 non-canonical decimal cells and holding 25 reports
   MISSED where it reported HELD, and each of the eleven counts inside
   that floor-wide block reports MISSED where all eleven reported HELD.
   **No verdict moves in the other direction**: the comparison it
   replaces was never more than the count, so every file that missed
   still misses and every conforming twin still holds. The green
   direction is asserted over the shipped generator's own output.

   **What stays true of the subcheck, and it is the half that reaches a
   report's reader.** It prints no measured count on any file: the line
   carries the licence and the verdict and never the recount, so one
   report says no more than it did. The pooled-form side is untouched and
   still settles against the room the file's own description leaves,
   because which of the six FORMS a cell wears IS published and IS
   floored — a MISSED there would put a lower bound on a floored count in
   a single report, which is V5.1's business and not this ruling's.

3. **Nothing in the repository may still assert the wider promise.**
   Six surfaces carried it as a live guarantee — this plan's P3-D3, the
   specification's V5.3 and V5.3-A1, and three comment blocks in
   `validation.py` — and each is corrected in place, keeping the rule
   and withdrawing the reason, because a governing document asserting a
   property the code does not have is the defect round 4 found in
   A-P3-5. The amendments this ruling touches keep their text and gain a
   pointer at this one: A-P3-3 clause 1 and A-P3-7 clauses 1 and 3
   record witnesses of both kinds and stand on the single-report half;
   A-P3-5 clause 3's bound keeps the half that is still owed; A-P3-10
   clause 1's rule is withdrawn by clause 2 above.

4. **What the reader is told, since the ruling is only honest if it is
   readable.** The quality report's own page carries the limit in plain
   words on every run — that the withholding rule is about what one
   report says, that it is not a defence against somebody who has the
   file and re-runs the check with descriptions of their own, and that
   whoever can run the check on a file can read the file — and
   `SECURITY.md` carries it as a named residual risk beside the other
   controls a user can weigh. **This moves the bytes of every quality
   report**, so `GOLDEN_QUALITY_SHA256` is re-recorded in the same
   commit with the diff read line by line first.

**How to reverse this.** Clause 1 reverses by putting the second reader
back in scope, which is the owner's to decide and which re-opens
P3-V3-F2, P3-V4-F2 and round 5's floor sweep as blocking defects with no
repair in the tree; clause 2 would then have to be reversed with it.
Clause 2 reverses on its own by restoring `_at_the_floors_resolution` and
its one call, which costs the teeth priced above — every file inside one
floor-wide block of its licence stops being missed — and buys a
block-resolution bound against a person who holds the file anyway, and
which round 5 measured to be defeatable by sweeping the floor. Either
reversal is recorded here in the same form as this one.

**Amendment A-P3-14 — the identifier corner is method G9.4's capacity
rule instead of a ceiling the validator invented. Clause 1 RAISES: a
file whose record-number column has collapsed to one repeated value is
MISSED where it received a passing report. Clause 2 LOWERS: a
description whose published width genuinely runs out now reaches owner
decision 6's lesser outcome, where the same three facts used to be
checked and missed. Clause 3 narrows a claim this plan's specification
made about its own test and never met** (2026-08-14, review item
P3-V6-F1).

**What the code did.** `identifier-infeasible` is the one corner that
takes THREE checks off a column — raw `n_distinct`, `n_distinct_folded`
and `n_distinct_by_occurrences` all become REPORT-ONLY — so it is the
corner a wrong answer costs the most. The predicate summed
`alphabet ** L` over the published length range and read the alphabet
off one published count: ten characters where `n_code_alphabet` is
zero, thirty-six otherwise. Neither is a domain synthtwin writes from.
G9.1 fixes three alphabets of ten, sixty-four and ninety-five
characters; G9.5 step 4 divides a column's cells between them by its
own two published counts; G9.4 counts each band's spellings under the
positional rules, which is where the widest band's twenty-five
one-character values come from.

1. **A description the generator answers may not be called a corner.
   THIS RAISES.** The review's witness is a declared column of eleven
   different one-character values outside the code alphabet: the
   producer publishes eleven present, eleven different, eleven
   different folded, one row each and a width of one, and the shipped
   generator writes eleven different conforming values. The old
   arithmetic read ten and called it infeasible, so a candidate file
   holding ONE of those values eleven times lost all three distinctness
   checks, kept a census of zero misses, and ended
   `NO CHECKABLE OBLIGATION WAS MISSED.` over a column that had
   collapsed. That file now reports three MISSED verdicts and the
   report says obligations were missed.

   **Counted, on producer-derived descriptions.** Over 500 randomly
   built declared identifier columns spanning all three bands and one
   to three characters of width, **43 descriptions the shipped
   generator answers in full were called infeasible by the old
   predicate and are not by this one** — every one of them a column
   whose three distinctness facts came back as checks. Seven more, on
   which the generator falls short for a reason owner decision 6 does
   NOT authorize — a fold-collision shortfall, which is A-P3-12's
   subject and not this one's — also had their checks restored and now
   report MISSED, which is the true answer for them.

2. **Where the published width truly runs out, the lesser outcome is
   granted. THIS LOWERS, and here is its size.** The old predicate
   withheld real corners while it invented false ones, and a withheld
   corner is a conforming twin reported MISSED. Ten one-character whole
   numbers is the smallest witness: figures alone open with a figure
   that is not zero (G9.6), so one character spells nine values, the
   shipped generator writes nine where ten are published, and owner
   decision 6 says that twin is conforming. The old predicate read
   thirty-six characters of room, claimed no corner, and reported three
   MISSED verdicts against the product's own output. **What is given
   up** is exactly what the plan already grants: on such a description
   the three distinctness facts are listings with their achieved values
   named beside the published ones, and no verdict is passed on them.
   Over the same 500-description battery this reached **7
   descriptions**, each one a column the generator provably cannot
   answer. No fact outside those three moves on any of them, and the
   corner is claimed only where every one of the three bands falls
   short together, which is the direction that keeps checks: supply is
   an upper bound on what the construction writes and demand a lower
   bound on what it is asked for.

3. **V4.2's account of its own test is narrowed to what runs. THIS
   NARROWS A CLAIM.** The specification said the two writings were
   compared "over every producer-battery description and every frozen
   conflict case, and any disagreement is red." No test did that. The
   green direction catches a corner the generator NEEDS and the
   classifier withholds, because the twin then misses; the reverse — a
   corner claimed where none is needed — is silent there, since the
   twin passes either way while three checks vanish. That silence is
   why this defect lived under a green suite for four review rounds,
   and the corner test in place asserted determinism and membership
   only. V4.2 now says which side each mechanism catches, and
   `tests/test_p3v6f1_identifier_corner.py` asserts the reverse
   direction directly against the shipped generator's own cells over a
   battery reaching all three bands, both whole-number readings, widths
   of one to three characters and four capacity boundaries taken from
   BOTH sides. **The reverse direction is still unasserted for the
   other three corners**, and clause 3 says so rather than implying
   otherwise; closing them is a later item, not a claim made here.

**What this does NOT close.** The corner answers whether the published
width can SPELL the values. It does not answer whether a fold collision
can be BUILT on the spellings that result: the battery's one remaining
disagreement is a 93-row column of one-character codes publishing 62
raw and 37 folded identities, where the spellings exist and the case
flips to pair them do not. Method G9.4 grants no corner there — only a
column whose one permitted length holds no character with a case
reaches it — so the twin's shortfall is a shortfall and the report's
MISSED is the honest answer. A-P3-12 owns that surface.

**How to reverse this.** Clause 1 and clause 2 are one predicate and
reverse together, by restoring the `alphabet ** L` ceiling; that
re-opens P3-V6-F1 with a measured witness in the tree and gives back
nothing, since the old arithmetic was wrong in both directions at once.
Clause 3 reverses only by making its wider sentence true, which means
asserting the reverse direction for the other three corners.

**Amendment A-P3-15 — the settings the validator re-describes under are
a RECONSTRUCTION of what the person declared, and this plan claimed the
reconstruction could not move a verdict. It can, and it did. Clause 1
RAISES: the person's `--missing-value` spellings are recovered from the
description's own published hole sources, which takes seven false
MISSED verdicts off one table and seventeen off another. Clause 2
RAISES and narrows blankness: the two presence counts come off the
split description that every other presence-dependent obligation is
already read off, instead of a blank recount beside it. Clause 3
NARROWS A CLAIM AND CLOSES NOTHING: what is left open is stated at its
size, with the reason it cannot be closed in the validator at all**
(2026-08-14, review items P3-V4-F1 and P3-V5-F2).

**What this plan said, and what was true.** P3-D3 above: "`n_present`,
`n_missing` and every count that depends on them are recounted from
blank and non-blank cells alone … no reconstruction gap can move a
verdict", and, in the settings table, `declared_missing_values` "EMPTY
by owner decision 8 — unrecorded, and genuinely absent from every twin,
whose absent cells are written empty". Both sentences are about a TWIN.
The other file a person points `synthtwin validate` at is the table the
description was written from (V1.2, and the repair of round 5 already
turned on it), and that table is exactly where a declared spelling is
still written in the cells. And the gap cannot only cost detail, because
amendment A-P3-5 takes the split's number only where the FILE'S OWN
description publishes the split — a description built under these very
settings. A spelling the reconstruction misses is a spelling that
description reads as a hole; the gate then closes on a conforming file
and the file's own wrong count lands on the verdict.

1. **The fourth published route. THIS RAISES.** ~~`missing_by_source`
   publishes the exact spelling of every hole whose count reaches
   `small_cell_floor`~~ — **that half-sentence is false and amendment
   A-P3-19 below corrects it: the field is DISPLAY-ESCAPED and
   REPORT-ONLY by the profile contract's own section 13.5, so it
   publishes the spelling AS A REPORT SHOWS IT and not byte for byte.
   What this clause bought stands where the boundary changes nothing,
   which is where both of its measured witnesses sit; where the boundary
   does change something the route is withdrawn, and A-P3-19 states both
   directions.** So a `--missing-value` declaration IS in the
   description — the settings block records it as a count, the COLUMN
   records the spelling. It is read back by the same act that reads
   back a level's variants, and which keys are a declaration is derived
   rather than guessed: the producer has four ways to make a cell a
   hole and no fifth, and the other three — a blank or the package's
   own placeholder names, a spelling the built-in missing table already
   reads as an absence, and a spelling reading as one of the three
   numeric stand-ins — are each recognisable from the description
   alone. **Measured:** a table profiled `--missing-value XX`, validated
   against its own profile, reported `presence.n_present`,
   `presence.n_missing`, `axes.role`, `axes.statistical_type`,
   `counts.n_not_numeric` and both distinctness counts MISSED — seven,
   and the column re-read as free text. Declared `--missing-value -777`
   instead, the same table missed SEVENTEEN, the ladder and the moments
   with them. Both now miss nothing. No obligation stops being checked
   and no new withholding is produced.

2. **The two presence counts come off the SPLIT DESCRIPTION. THIS
   RAISES, and it narrows blankness by exactly one clause.** V2.4 reads
   every presence-dependent obligation off the split description; these
   two were recounted separately from the cells, and while both
   declaration tuples were empty the two answers were the same number,
   so nothing showed. They are not the same number once a declaration
   is recovered: one report said 211 present beside a distinctness count
   of 199 taken over the cells that number claims are present. Two
   numbers for one question is not a measurement. So a cell is absent to
   these counts when it is empty, OR when it wears a spelling the
   description ITSELF publishes as the source of its holes — which is
   the phrase "or declaration machinery" struck from P3-D3's sentence
   above, and the strike is the whole of the narrowing. **The reason
   blankness exists reaches only the first:** residual R-P2-13 says a
   generated value can BE the text of a built-in marker, and no file may
   be failed for colliding with synthtwin's OWN vocabulary — nothing of
   synthtwin's own vocabulary is in the recovered set, by construction.
   **What it costs, said as a cost:** a generated value that collides
   with a spelling the DESCRIPTION declares is now counted as a hole,
   which is R-P2-13's shape on a declared spelling. It is bounded by
   the cells wearing that spelling, and it is recorded here rather than
   found.

3. **What is NOT closed, at its size, and why not here. THIS CLAIMS
   NOTHING.** Two gaps remain, and neither is recoverable from what the
   contract publishes:

   - **a `--keep-value` spelling that is one of the built-in missing
     texts, on a column publishing no level that carries it** — a column
     of numbers, of datetimes, of identifiers, of free text. The review's
     own witness: two hundred readings and one kept `n/a`, published as
     201 present, 0 missing, 1 not numeric. No field of the document
     carries the spelling, and the suite proves it by comparing the
     marker with every string the document holds, key and value alike.
     The table reports `presence.n_present`, `presence.n_missing`,
     `counts.n_not_numeric`, `counts.n_left_out_of_statistics`,
     `counts.numeric_share`, `distinct.n_distinct` and
     `distinct.n_distinct_folded` MISSED — ~~five~~ **seven**, against
     its own profile. **It was five until G12.8's supply was given its
     second summand; the two that joined are a bar going up rather than
     this gap growing, amendment A-P3-25 clause 3 states why, and the
     one cause of the gap is unchanged. (CLOSED 2026-08-17 by amendments
     A-P3-27 and A-P3-29, which are the decision this clause's last
     paragraph says it waits on: contract version 5 records which of
     this package's own published words a `--keep-value` named, and the
     validator reads that record. All seven are checked and all seven
     HOLD on the witness above.);**
   - **a declaration of either kind whose cells sit below
     `small_cell_floor` in every column**, pooled into `(withheld)` and
     named nowhere. Bounded by the floor per spelling per column, and
     measured in the suite at seven subchecks on the witness that
     reaches it. **(AMENDED by A-P3-29: this reaches only a word of the
     PERSON'S own now. One of this package's thirteen published words is
     recorded in the settings block whatever the floor did with its
     cells.)**

   **Reading the split anyway is not available, and that is why this is
   a ruling and not a repair.** Two hundred readings and one `n/a`,
   beside the same table with that cell written `NULL`: the producer
   describes the two BYTE FOR BYTE ALIKE under every settings object the
   validator can build from the description, the first meets every fact
   a `--keep-value n/a` description publishes and the second does not.
   Any rule that passes the first passes the second, and stating 201
   present about the second states a count `synthtwin profile` run on
   that file would not publish, which is V5.1. **What would close it is
   a decision about what the PROFILE publishes** — the only part of the
   declaration the validator needs is which of synthtwin's own twelve
   built-in markers and stand-ins the person named as data, which is a
   subset of this package's own published vocabulary rather than text
   out of the table — and that decision is the owner's, because
   `values_recorded: false` is a confidentiality rule of Phase 1
   (P1-R7-F2) and this plan may not narrow it. Until it is taken, no
   sentence in this repository may say the bound of P3-D3 is met.
   **(THE DECISION WAS TAKEN on 2026-08-17 and is amendment A-P3-27,
   at the size and price recorded there; A-P3-29 is the validator
   reading what it records. The bound of P3-D3 is still NOT met, and
   this sentence still binds, because two kinds of declaration stay
   unrecoverable — a word of the person's own that the floor pooled,
   and a word of the person's own on a column that publishes no value
   of the table. What changed is which descriptions they are.)**

**How to reverse this.** Clause 1 reverses by making `declared_spellings`
answer the empty tuple, which re-opens both measured witnesses with the
tables in the tree. Clause 2 reverses with it and only with it: the two
counts agree with a blank recount exactly when clause 1 finds
nothing, so reversing clause 2 alone leaves the self-contradicting
report this clause exists to stop. Clause 3 reverses only by closing
what it says is open, which is the ruling above and not an edit.

**Amendment A-P3-16 — amendment A-P3-11 promised a floor-of-one
invariant that nothing enforced, and the quality report said something
false beside it. Clause 1 RAISES: the strict loader refuses a floor-one
description carrying any FIELD that records something held back —
reached by walking for the format's own word for it rather than by the
five field names a reviewer happened to list, and bounded in clause 5.
Clause 2 RAISES:
the profiler's own publication guard refuses to WRITE one. Clause 3
NARROWS A SENTENCE that was not true. Clause 4 records a defect found
while measuring the other three and repaired with them, and clause 5
states what none of this closes** (2026-08-14, review item P3-V5-F1).

**What A-P3-11 said, and what was enforced.** Its clause 1, and section
4.4 of the contract with it, say that at a floor of one the "below the
floor" half is the empty range, "so nothing may be held back at all and
`suppressed_level_counts`, `variants_withheld` and every pooled
`(withheld)` remainder must be empty; a document that fills one is
refused for breaking the invariant it always broke". Three of those were
refused and the sentence was right about them. Five were not, and the
sentence's reason is why: N2, N4, D3 and P2 each hold a PUBLISHED count
to the floor and each EXEMPTS the pooled remainder, because the
remainder is what those counts were pooled out of. An exemption does not
become a rule at a floor of one by itself. And V1 holds a stand-in
number's occurrences to the floor the same way, putting the ones below
it into `n_sentinel_candidates_unpublished` — a count no rule of the
contract bounded at any floor. A
producer-derived floor-one description stayed accepted after
`(withheld)` was put into `missing_by_class`, `missing_by_source`,
`utc_offsets` or `numeric_styles`, and after
`n_sentinel_candidates_unpublished` — which no rule of the contract
bounded at any floor — was made nonzero.

1. **Contract invariant S13, checked over the whole document. THIS
   RAISES.** `docs/spec/profile-contract-v4.md` section 4.4 carries it
   under a counted re-seal, and section 5.5's V1 gains the sentence that
   ties the unnamed tally to it. The loader runs it with the top-level
   rules, before any column is read, because the floor is a top-level
   setting and what the rule states is a fact about the description as a
   whole.

   **The pooled remainder is found by WALKING, not by a list of fields,
   and that is the repair rather than a detail of it.** `(withheld)` is
   the format's one word for "held back" (contract section 14), so every
   pooled remainder is a count standing under that word. Four fields
   carry one today; a fifth added later is reached by the same walk on
   the commit that adds it, without anybody remembering. Listing the
   four is exactly the shape of the defect: each of them WAS checked
   where it was written, and each check exempted the remainder.

   **One field is named rather than walked to, with its reason.**
   `n_sentinel_candidates_unpublished` records what it holds back in its
   NAME instead of under the marker word, so a walk cannot find it. It
   is the only such field in version 4, and that is measured rather than
   asserted: `tests/test_p3v5f1_floor_one.py` describes one table with
   the real producer at the default floor and at a floor of one, reads
   the floor-governed positions off the difference between the two
   documents, and grafts each one back into the floor-one document,
   where the loader must refuse it. Its second half derives the same
   class leaf by leaf, without the marker: a count the producer writes
   NONZERO at eleven and ZERO at one is a tally of what the floor held
   back, whatever it is called, and every member of that class must
   make the loader refuse. No field name is written down in either.
   What it costs to hold: `fixtures.every_withholding_table` has to
   keep exercising every way the format has of holding something back,
   and its docstring says which column buys which.

2. **The profiler refuses to WRITE one. THIS RAISES.** The publication
   guard checks the finished document before a byte is written, and its
   rule for a pooled entry accepted any count of one or more whatever
   the floor was — so the two halves of the product disagreed about what
   a floor of one means, and only the reading half was even asked. The
   guard now has vocabulary for the floor's other half: a tally of what
   was held back, and one group size below the floor. Nothing changes
   for a document the producer actually writes, at any floor.

3. **"At 1 nothing is withheld at all" was false on its own page. THIS
   NARROWS A SENTENCE.** The quality report's lowered-floor section said
   it, and added "every line below that would have read WITHHELD carries
   its number instead". Two rules put WITHHELD on a line and only one of
   them is the floor's: the other is the type gate, which asks whether
   describing the CHECKED FILE would publish a measurement of that kind
   at all. Measured: a floor-one description checked against a file
   whose columns hold words where it publishes numbers printed that
   sentence and then eighty-three obligation lines reading WITHHELD,
   with "83 WITHHELD" in its own verdict summary fourteen lines below.
   The narrower wording already existed one section down — "nothing is
   held back this way at all" — and the head of the report now says the
   same bounded thing and names the other rule. **This changes the bytes
   of no artifact made at the default floor**, because the section it
   sits in is printed only under a lowered one. The other two written
   pages were read at the default floor and at a floor of one and carry
   no sentence of this shape; a test now asserts that of all three.

4. **A table whose times are stamped in UTC could not be described at
   all, and this repairs it.** Found while building the fixture clause 1
   is derived from. The producer writes `Z` as the offset of a cell
   ending in one and the strict loader accepts `Z` wherever an offset
   may stand, but the profiler's publication guard did not know the
   string — so `synthtwin profile` refused every table of UTC-stamped
   times with the message that says this is a fault in synthtwin itself
   and there is nothing to fix in your file, leaving the person no way
   to describe their table. The two writings of "what a UTC offset is"
   now accept the same strings, and a test compares them string by
   string over a built alphabet rather than trusting either. The same
   comparison found the disagreement in the other direction — the
   guard accepted `+99:00` and `+00:60`, which the loader refuses — and
   that half is closed with it, though no table reaches it: an offset
   out of range never parses as a date, so the producer never writes
   one.

5. **What none of this closes, stated at its size.**

   **A remark or a note can still carry a sentence about something
   nothing in the document holds back.** The floor moves prose as well
   as counts — a remark saying how many stand-in numbers were too rare
   to name, a note saying how many labels were pooled — and the loader
   reads neither for numbers. A hand-edited floor-one description whose
   remark says a count was held back is accepted with that sentence in
   it. What is refused is every FIELD that records it. Closing the prose
   half means reading sentences for numbers, which is a different kind
   of rule and is not attempted here.

   **The derivation sees only what a fixture exercises.** A
   floor-governed field no table in the tree makes the floor move is a
   field the measurement cannot see. Two things narrow that: the walk
   finds a pooled remainder whether or not a fixture reaches it, and the
   test pins the prose positions, so a new COUNT cannot arrive disguised
   as one. A new field that records withholding in its own name, as the
   sentinel tally does, and that no fixture exercises, is not covered.

   **`sentinel_verdicts` is short at a low floor and nothing says so.**
   The floor changes that list by leaving an entry out, and no invariant
   ties its length to a number the document publishes — so a floor-one
   description carrying the floor-eleven list, and nothing else from
   that document, is accepted. The tally beside it is what records the
   omission, and the tally is now enforced; the list on its own is not,
   at any floor. This is measured by the derivation test rather than
   assumed, and the test goes red if any other position joins it.

**How to reverse this.** Clause 1 reverses by making
`contract._nothing_is_held_back` return without looking, which re-opens
all five measured witnesses. Clause 2 reverses by giving the guard's
pooled entry back its floor-blind rule. Clause 3 reverses by restoring
the absolute sentence, which the report test measures directly. Clause 4
reverses by taking `Z` out of the profiler's offset rule, which stops
the whole workflow on any UTC-stamped table.

**Amendment A-P3-17 — three ceilings that did not mean what they said,
and the claims that rested on them. THIS RAISES three bars and LOWERS
none; what it also does, and what it exists for, is cut two claims down
to what was measured** (2026-08-14, review round 6, items P3-V6-F2,
P3-V4-F6 and P3-V6-F3).

**The shape all three share, because it is the shape worth naming.** A
guard states a reach — 256 candidate packings, every shipped site, every
surface that speaks in synthtwin's voice — and then reaches less than
that, silently, while the sentence claiming the reach goes on standing.
None of the three was a wrong rule. Each was a right rule whose stated
scope was wider than its walk, and in every one of the three the gap was
invisible from inside: the suite was green, the amendment said "every
one of them", and the thing that found it was somebody counting.

1. **The withdrawn-defence ban walks the GOVERNING PLANS. THIS RAISES**
   (review item P3-V6-F3). The ban of amendment A-P3-13 clause 1 named
   this plan's own P3-D3 as one of the passages the ruling had to
   correct — and `tests/test_claim_inventory.py` did not open this plan
   at all. It now walks `DEFENCE_SURFACES`: every surface it walked
   before, plus the two documents the disposition seal calls governing,
   held to that set by a test rather than by a list somebody remembers
   to extend. **The other three families of that file are unchanged and
   still stop at the user-facing surfaces**, because they count what the
   product HAS and a plan states what a later phase will have, on
   purpose; only a promise about what somebody can be stopped from doing
   is normative wherever it stands.

   **What walking the plan found, on the first run.** One stale claim,
   in A-P3-10 clause 1's "what is left open" paragraph: it states the
   floor-rounding bound against a sweep of candidate descriptions, and
   A-P3-13 clause 2 DELETED `_at_the_floors_resolution` the same day.
   The paragraph is now marked superseded in place, with what it bought
   while it stood kept as the record. **No obligation moved**: A-P3-13
   clause 2 already made the change and priced it; what was missing was
   a line saying so where a reader meets it.

   **Two further gaps in the ban itself, both closed, and one that
   cannot be.** *[NARROWED by amendment A-P3-24 clause 3, 2026-08-15:
   there was a THIRD gap, and it was not the one this paragraph calls
   unclosable. The guard read ONE STATEMENT AT A TIME, so a promise
   split across two — "a person can re-run the check with descriptions
   they wrote themselves; the withheld number remains unknowable" —
   walked past it using no vocabulary the lists did not already hold
   (review item P3-V7-F8). That promise is withdrawn on every surface of
   this repository; what round 7 showed is that the guard could not see
   it. It is read there now, at a stated reach. What this paragraph says
   about the two gaps below, and about the list being unsound, stands
   exactly as written.]* The guard reads a
   sentence as a defect when it NAMES the out-of-scope reader and
   PROMISES something about them. Round 6 walked three sentences past
   it. *Promising by outcome rather than by
   barrier* — "repeated profiles reveal nothing about a count this
   report withholds" — is now its own family, a word for knowing paired
   with nothing. *A withdrawal standing in FRONT of the promise* — "this
   protection is no longer offered. No sequence of candidate
   descriptions can narrow a number this report withholds" — no longer
   cures it: a withdrawal reaches forward only inside its own statement,
   and backward a paragraph, which is the direction the honest passages
   here are actually written in. All three sentences are kept as the
   guard's own red cases.

   **AND THE THIRD IS A LIST, AND NO LIST OF THIS KIND IS SOUND.** The
   third sentence — "a succession of custom specifications leaves a
   suppressed tally unknowable" — named the reader with a noun the guard
   did not carry, and that reader is out of scope. `specification` and
   `spec` are now carried, and that is a patch and not a repair: no
   finite list of nouns bounds an infinite set of paraphrases, and the
   next reviewer will find another word. **What is sound, stated so somebody can build it rather than
   left as a wish**: one canonical passage about this reader, quoted
   verbatim wherever the subject is raised, with every OTHER mention of
   it refused outright — the ban inverted, so that silence is the
   default and speech has to match a fixed text. That was measured
   before it was proposed and it is not free: inverted against the tree
   at this commit, **thirty-four statements name that reader without
   withdrawing in the same breath**, and most of them are about
   something else entirely — `sweep` in the changelog, `over and over`
   in the reader, `again and again` in the generator's own comment
   about its packing search, `descriptions of their own` in the advice
   telling somebody to re-run `synthtwin profile`. Several are
   statements of this amendment. It is a change to how this repository
   is allowed to write, not a change to a test, and it is left to the
   owner. **Until it is taken, the reader-naming list is the
   one place in this family where a miss is a false NEGATIVE, and that
   is written into the file beside the list.**

2. **The fold repair's ceiling is spent on questions, not on repeats,
   and a repaired layout is held to what it WROTE. THIS RAISES twice**
   (review item P3-V6-F2).

   **What A-P3-12 claimed and what was true.** Clause 2 said "zero, on
   both batteries, at four seeds", and clause 5 gave the one remaining
   route as the stated budget being spent. A third battery — 1,174
   producer-built columns publishing a fold collision, shaped like the
   review's own witness, at four seeds, 4,696 runs — missed
   `n_distinct_folded` on **12** of them. The review's own witness is a
   column of that shape and is measured beside them rather than counted
   among them: a forced identifier holding `-716`×4, `-716 `×5,
   `^OTAL`×5, `^otal`×5, `1e999`×3 and ` 3e999 `×3, whose own values
   answer its own description exactly, and whose twin published six raw
   spellings and FIVE folded identities where the description publishes
   four, at every seed tried.

   **The cause, which is neither of the two A-P3-12 named.** The second
   tier of `_identifier_packings` walks positions — a candidate
   end-carrier pair, a group, a family — and hands the allocator a
   permission vector that does not depend on the end-carriers except
   through the two places carrying them. So the same question comes
   round again and again. On the witness: **2,466 positions carrying 246
   different questions**, nine positions in ten a repeat. The ceiling of
   256 ran out having answered **82** of the 246 — 168 of the 250 it
   gave the second tier bought nothing — and the first candidate that
   tier had to offer sits at position 420, past the ceiling in
   positions and well inside it in questions. **A ceiling counted in
   repeats is a ceiling that reaches whatever the loop order leaves
   over, which is a number the code never stated.** A question is now
   asked once and remembered, the ceiling
   counts questions PUT TO THE ALLOCATOR — so the allocator's work
   stays exactly where clause 4 priced it — and a second stated ceiling,
   `_FOLD_LOOKS`, bounds the positions so the walk still ends in a
   stated number of steps.

   **AND THE ACCEPTANCE TEST STOPS ARGUING. THIS RAISES.** Widening the
   enumeration reached candidates the shipped rule never saw, and the
   driver accepted them on an argument: that every candidate packing
   meets every margin, so no other published count can move. It can. A
   packing settles which class and which alphabet each group answers
   for; whether that family holds a spelling AT THE LENGTH the slot is
   pinned to is a different question, and where it does not the walk
   falls back to the band's own alphabet and a class count met on paper
   is missed on the page. `_identifier_shortfall` now RECOUNTS the
   finished cells — the four class counts, both alphabet counts, both
   length ends and both distinctness counts — and a repaired layout is
   accepted only where it gives up nothing the first layout held.

   **WHAT THAT GUARD IS WORTH, MEASURED, AND IT IS LESS THAN THE
   PARAGRAPH ABOVE READS LIKE.** Emptying the recount and running both
   batteries again changes **nothing at all**: 0 missed counts either
   way on the A-P3-12 battery, and the same 4 on the new one. On the
   two batteries this amendment measures, the candidates the repaired
   enumeration actually reaches all keep every count, so the guard
   never fires. It is kept anyway, and on stated grounds rather than on
   a measurement it does not have. First, a wrong candidate IS
   reachable and the witness is written down: the description of `-3`
   ×11, `-3 `×11 and `1e0`×11 has a layout writing `0E0`, `0e0` and
   `10`, which holds every class count, both length ends and the folded
   count while giving up `n_all_digits` — a count none of the real
   values has. Second, a version of this repair that widened the
   enumeration while a second defect left the first tier handing back
   nothing DID reach such candidates in quantity: **2,116 missed counts
   over 3,672 runs**, `n_numeric`, `n_out_of_range`, `n_all_digits` and
   four more. That number is what the ARGUMENT is worth when a wrong
   candidate is reached; it is not a claim about the shipped
   enumeration, which reaches none on these batteries. Third, clause 1
   of A-P3-12 states the property as a property and not as a
   measurement, and a property is enforced by checking it.

   **After, measured on two batteries at four seeds, each built through
   the real producer.** The first is A-P3-12's own hazard shape, taken
   from the builder the shipped test file carries and run to 1,200
   seeds: **918** columns publish a fold collision, 3,672 runs. 0 missed
   before, **0 missed after, and not one byte moved** — the repair
   cannot reach a column the shipped rule already answered, which is
   A-P3-12 clause 1's licence and is measured here rather than argued.
   Cells opening with a character a spreadsheet reads as a formula: 744
   before, **744** after. The second is the review's own shape, also
   1,200 seeds: **1,174** columns, 4,696 runs, **12 missed before, 4
   after**; bytes moved on **8** runs and **every one of the 8 is a run
   the shipped rule got wrong**; no run exact before is
   exact-but-different after; formula-leader cells 620 before and
   **620** after. Cost, end to end over the same runs: 26.1 seconds to
   26.7, and 100.3 to 112.8 — two per cent and thirteen.

   **THE RESIDUE, AT ITS MEASURED SIZE AND WITH ITS CAUSE.** Four runs
   of 4,696 remain, and they are ONE column at four seeds: `' 13e999 '`,
   `'(-89)'`, `'(-89) '`, `'-56'`, `'13E999'`, `'13e999'`, `'@N'`,
   `'@N '` — eight spellings, four folded identities, four collisions
   owed. Its twin writes five folded identities and the report names the
   deviation. **The cause is not the ceiling and not the enumeration.**
   With every ceiling removed the walk offers **2,097** candidate
   packings for that column and **not one of them builds every collision
   it owes**: the shortfall is in G9.3's layout rule — which slot may
   carry a collision, and what a family can supply once its flips are
   spent — and no packing reaches it. So the deviation path is live,
   it is why it is still built, and this amendment does not say the
   miss is gone.

   **What this does NOT claim.** A battery is a battery, and A-P3-12
   was rejected for reading two of them as every description. Two are
   measured here, one of them A-P3-12's own shape and one built to the
   shape the review found: the first misses nothing after the repair
   and the second misses four. A third shape may find more, so the
   claim this amendment makes is the measured one — these runs, these
   shapes — and not "every description".

3. **The non-vacuity proof is total over the PREDICATES the validator
   ships, not over the ordinary ones. THIS RAISES** (review item
   P3-V4-F6). V3.1 makes an entry's identity a profile predicate, a
   column and a subcheck, and owner decision 7 ships four predicates.
   `tests/test_p3v1f2_entry_table.py` walked six fixtures that are all
   the one ordinary predicate, and called the result every shipped site.

   **What was outside it.** The two zero-row predicates file fifteen
   executable subchecks between them — nine on the headed form, six on
   the headerless one — and no test in this suite bound any of their
   facts or showed any of them able to fail. `bytes.zero-row-form` was
   stated by no line of `SUBCHECK_FACTS` at all; `header.names` and
   `columns.order` on the headed form could swap registry facts with
   every assertion green; and `columns.order` there could be pinned to
   HELD, which is the review's own witness, with nothing turning red.

   **What is now enforced.** The binding walk runs over the six runs AND
   the four predicates, and asserts that the predicates reach a subcheck
   the ordinary runs do not, so widening it is measured and not
   asserted. Every one of the fifteen sites carries a registered edit
   that names it and makes THAT site report MISSED, in both directions:
   a site with no edit is red, and an edit naming a site the predicate
   does not file is red. Nothing is excused.

   **One measurement is recorded rather than repaired**, and it is not a
   defect in the validator. `synthtwin profile` REFUSES a zero-row table
   in both header modes, so no producer can write a zero-row
   description; the only way to have one is to cut an ordinary
   description down, which leaves it carrying the line-ending fact of
   the file it was cut from. A headerless zero-row description therefore
   misses `bytes.terminal-newline` against a file of no bytes —
   correctly, against a description no producer would write. That is
   pinned as a red case rather than asserted away. The headed form's
   conforming file, its header line, misses nothing and withholds
   nothing, and that is asserted.

**How to reverse this.** Clause 1 reverses by taking the two governing
plans out of `DEFENCE_SURFACES`, which re-opens the stale claim it
found and every future one; the directional cure reverses by widening
the window back to both sides, which re-opens the withdraw-then-promise
sentence. Clause 2 reverses by charging the ceiling for repeats again,
which re-opens the 12 measured runs, and by making
`_identifier_shortfall` return nothing, which re-opens no measured run
on either battery and re-opens the property clause 1 states. Clause 3
reverses by walking the six ordinary fixtures alone, which re-opens all
fifteen zero-row sites.

**Amendment A-P3-18 — the comparison V4.2 always specified, built at
last, and the five divergences it found. Clause 1 RAISES two bars.
Clauses 2, 3 and 4 LOWER four, each with its size measured. Clause 5
states the boundary this validator cannot cross and what it costs**
(2026-08-15, review round 7, items P3-V7-F2, F3 and F4).

**The shape all five share, and why they were repaired together.**
Specification V4.2 says the corner classifier is written from the
validation method and compared against the generator's own in the suite,
where both may be imported. Round 6 found that no test had ever done
that, and A-P3-14 clause 3 narrowed V4.2's claim to the one corner and
the one direction that ran. Round 7 then found three more divergences of
a single shape — the validator's independent arithmetic disagrees with
the generator's, and the validator REJECTS OR MIS-CLASSIFIES FILES THE
SHIPPED GENERATOR ITSELF WRITES — and two of the three were introduced
by round 6's own repair. So this amendment does not patch
them one at a time. It builds the comparison, in
`tests/test_p3v7f2_corner_parity.py`, over EVERY corner the validator
classifies and a producer-built space of 219 descriptions -- 13 of them
reaching the identifier corner, 9 the label corner, 47 the numeric one
and 5 the withheld-offset one -- and repairs what that comparison found.

**What the comparison asks, in four questions.** (i) The shipped
generator writes a twin for each description, the shipped validator
measures it, and no corner-governed fact may be MISSED where the
GENERATION REPORT's own account says the twin holds it. (ii) Where the
classifier claims no corner it is asserting that the description pins
the count, and the generation report must say the same thing in its own
words: the two ends of the bound it prints for that fact must meet.
(iii) The identifier corner's supply is method G9.4's FAMILY capacity,
and the shipped family maps are WALKED, index by index, and counted.
(iv) Every distinctness bar the space prints must be one some file can
miss, and where it would license every count a column of that
description can hold it is a listing instead. Six `REINSTATE` values put
one piece of the pre-repair behaviour back, so each guarantee has a
demonstrated red.

1. **The identifier supply is the FAMILY's above one character too, and
   a band that cannot cover its own cells is short whatever the others
   hold. THIS RAISES twice** (review item P3-V7-F2).

   A-P3-14 replaced the `alphabet ** L` ceiling with G9.4's band rule
   and counted the one-character families out exactly. Above one
   character it still counted every string the positional rules of G9.1
   leave, which is not a domain any family of G9.6 writes from: the
   widest band spells **8,460** values two characters wide by that
   reading and **2,538** by its own family's, twenty-seven permitted
   leading characters against ninety-four for the second. A
   producer-derived declared column of 2,539 two-character values
   outside the code alphabet was therefore called feasible, the shipped
   generator necessarily repeated, and validation reported all three
   identifier cardinality obligations MISSED against the product's own
   output. The supply is now the two families that write those cells —
   the band's ordinary-text walk, and the ordinary-number family of
   G9.5 step 3 where the description gives the numbers class a cell —
   and the boundary is asserted from both sides at 2,538 and 2,539.

   **And the summed reach is not the whole question.** It lets the
   smallest published groups answer for every band at once, so it can
   read a supply the three bands cannot jointly deliver. G9.4's own
   sentence is asked beside it now: a band answering for `cells` of them
   needs at least `ceil(cells / widest group)` different spellings.
   The witness is producer-built and 54 cells long — one repeated
   figure, one code value, and twenty-six values outside the code
   alphabet of which twenty-five stand in two rows each — where the
   widest band needs twenty-six spellings and holds twenty-five while
   the summed reach reads twenty-eight against twenty-eight. Its twin
   holds 27 of the 28 published record numbers, and the three checks it
   used to miss are now the listings owner decision 6 grants.

2. **The two spelling corners are G12.8's envelope in BOTH directions,
   and the label supply counts withheld multiplicity the way the method
   writes it. THIS RAISES one bar and LOWERS one** (review items
   P3-V7-F3 and P3-V7-F4).

   *The label arithmetic was simply wrong.* A withheld-variant key is an
   OCCURRENCE COUNT and its value is how many spellings covered that
   many rows each, so the rows such an entry covers are `key x value`.
   The validator added the value alone, so a level its withheld variants
   covered exactly looked short, one more spelling was invented for it,
   no corner was claimed, and the exact bar was put on a count the
   shipped generator cannot meet. The review's witness — `alpha`x6,
   `Alpha`x6, `beta`x5, `Beta`x5 under the floor of eleven — publishes
   raw distinctness four; G12.7 supplies three; the generator writes
   three; the report said MISSED. **THIS RAISES**: the validator's `S`
   is now the generator's, and the suite asserts the two are equal on
   every label description in the space.

   *The numeric corner was asked in one direction only.* V4.1 named it
   as a supply that "cannot reach" the published count, and G12.8's
   envelope is two-sided: `min(supply, n_distinct) <= n_distinct(twin)
   <= max(supply, n_distinct)`. A floored style map naming fifteen
   leading-zero cells on a column publishing nine different values has a
   supply ABOVE its published count, the shipped generator writes twelve
   identities, its own report calls that inside the bound, and the exact
   bar called it MISSED. The corner is now claimed wherever the
   description does not pin the count.

   **THIS LOWERS, and here is its size.** On a column whose own
   permitted spellings can carry more identities than it publishes, a
   file holding more different values than the description names is now
   an AUTHORIZED DEVIATION rather than a miss. Two registered red cases
   moved because of it and both are recorded in
   `tests/test_p3v1f2_entry_table.py` beside the rows: `spread-amount`,
   whose column publishes 240 decimal cells and 238 different values, so
   the even spread's 240 sits inside an envelope the generation report
   itself prints; and `pooled/fractioned-reading`, whose style map the
   floor has pooled. Both sites keep a red case — the narrowest edit
   that still makes them miss, by this plan's own rule — and the ladder
   rungs catch the even spread as they did before.

3. **A bar that licenses every count is a listing, not a check. THIS
   LOWERS, and it is the charter's own rule** (review item P3-V7-F4,
   second half). Forced integers 1 to 200 publish two hundred present
   cells, two hundred different values and the single style `plain`.
   All the plain cells together supply ONE identity, so the envelope
   runs from one value to two hundred — every count a file of that
   length can hold. The check could not fail. V3.4 forbids a subcheck
   that cannot fail and V3.5 decides it per entry, so the entry is a
   listing carrying the passage that authorizes the lesser outcome, and
   the census counts it where it counts an obligation nothing settles.
   **What is given up** is a comparison that was already empty; what is
   gained is a report that says so. The rule bites only where the
   envelope's low end reaches one AND its high end reaches every present
   cell, so the ordinary plain column — ten different values in
   two hundred and twenty-nine cells — keeps its check.

4. **Two obligations no CSV can evidence, found by the same battery and
   named here rather than left because the review did not name them.
   THIS LOWERS two bars.**

   *A withheld endpoint offset.* A datetime column whose offset map
   names real offsets can still have its own earliest or latest END
   below the publication floor, published as the withheld label. The
   description then names no offset for that end, and the comparison
   that stood asked whether the measured file's OWN floor had suppressed
   the same end — a fact about how many rows shared an offset, not about
   the file's dates — and reported MISSED against the shipped
   generator's twin. It is a listing now. P2-D9's corner, where the
   WHOLE map is withheld, is unchanged.

   *A pooled style count.* The floor pools every numeric form fewer
   cells wear than the floor into one withheld key and publishes no
   count for any of them, so a cell in that pool has no published form
   and a twin may give it any form the description permits. The exact
   bar compared a NAMED form's recount as though the pool were not
   there: eleven plain cells published against forty-five written came
   back MISSED, on every one of the twelve descriptions in the committed
   space whose style map the floor had pooled. The bar is a window now — at least the published count and at
   most that count plus the pool — and it keeps its teeth in the
   direction that matters, since the published cells are still owed.

5. **What this does NOT close, and it is a boundary and not an
   oversight.** G12.8's supply is a property of the twin's FINISHED
   CELLS: each (value, style) group of the numbers class supplies one
   spelling where the style is `plain` and its own cell count otherwise.
   ~~How many different VALUES the plain cells carry is decided by the
   value construction of G5 and G7, which V1.4 keeps out of this module
   and which this repair does not rewrite.~~ **That sentence named the
   right residue and then wrote a floor giving up far more than it, and
   amendment A-P3-25 clause 3 below corrects it: G12.8's formula has a
   SECOND summand — for each class that is not the numbers class,
   `min(its cell count, its share of the budget in G6.5)` — which is
   arithmetic on published counts and was left out of this validator
   altogether. It is counted now, at both ends. The plain cells' value
   count is what remains unknowable here, and it is the only thing.** So
   the description settles
   two numbers rather than one — a FLOOR, where all the plain cells
   carry one value between them, and a CEILING, where each carries its
   own, bounded by the published count of different values — and the
   validator's envelope is the pair. On a column of labels there is no
   second number and the two writings print the SAME envelope; on a
   column of numbers the validator's is wider than the generation
   report's, and the suite asserts containment rather than equality and
   says which it is asserting. **How much wider is measured rather than
   described** (A-P3-25 clause 3): a file one different value short of a
   count the generation report pins is an AUTHORIZED DEVIATION here and
   not a MISS. Narrowing it means writing the value
   construction out from G5 and G7 here, as V3.4-A2 did for the
   datetime windows. That is a later item, and no sentence in this
   repository may say the two numeric envelopes agree until it is taken.

**How to reverse this.** Clause 1 reverses in two pieces: restoring the
alphabet reading above one character re-opens the 2,539-value witness,
and making `_band_falls_short` answer False re-opens the 54-cell one.
Clause 2 reverses by restoring the withheld-count-as-coverage
arithmetic and by asking the numeric corner in the short direction only,
which re-opens both witnesses and gives back the two red cases. Clause 3
reverses by making `_envelope_admits_every_count` answer False, which
puts a bar that admits every count back on the report. Clause 4 reverses
by checking a withheld endpoint against the file's own floor and by
passing the pooled count as zero. Clause 5 reverses only by being made
untrue, which means writing the value construction out.

**Amendment A-P3-19 — amendment A-P3-15 clause 1 called a
DISPLAY-ESCAPED field the exact spelling, and the profile contract says
in terms that it is not. Clause 1 CORRECTS that sentence. Clause 2
RAISES, by taking a passing report off a file the description's own
declaration rejects. Clause 3 LOWERS, at the size measured beside it.
Clause 4 states the boundary and why it is not this module's to cross**
(2026-08-15, review round 7, item P3-V7-F1).

**What was claimed, and what the contract says.** A-P3-15 clause 1 and
validation method V2.3-A1 both read that `missing_by_source` carries
"the exact spelling" of every hole whose count reaches the floor. The
profile contract's section 5.4 says its keys are the spelling "after
passing through the display boundary that escapes line, control and
bidirectional formatting characters", and its own decision 13.5 draws
the difference deliberately: `variants` is stored EXACTLY because a twin
writes it back into a cell, and `missing_by_source` is REPORT-ONLY and
escaped because nothing ever writes it back. An amendment that claims
more than the format carries is a defect, and this is one.

1. **The correction, made in place. THIS CLAIMS NOTHING NEW.** The
   half-sentence in A-P3-15 clause 1 is struck above and V2.3-A1 is
   corrected in the method. What that route bought stands wherever the
   boundary changes nothing, and both of its measured witnesses — `XX`
   and `-777` — sit there: neither holds a character the boundary
   shows, both are still recovered, and both tables still miss nothing
   against their own profile.

2. **A passing report on a file the declaration rejects. THIS RAISES,
   and it is the direction the review did not name.** Seventy-two rows
   whose holes are spelled `X`, U+0001, `Y` publish the key `X\x01Y`.
   So do seventy-two rows whose holes are spelled with those six
   PRINTABLE characters. **The two whole descriptions come out BYTE FOR
   BYTE ALIKE, 6,733 bytes each**, so nothing a validator can read tells
   the two apart. Round 6 read the key as exact, which meant reading it
   as the printable spelling — and a file wearing that printable
   spelling, checked against the CONTROL-CHARACTER table's description,
   came back with a census of ZERO MISSED and exit 0. `synthtwin
   profile` under that description's own declaration reads that file as
   free text with 72 present cells and no holes, against a description
   publishing a numeric role with 60 and 12. A passing report must mean
   what it says; that one did not. Seven obligations are reported MISSED
   about it now.

3. **A declaration the boundary shows is not recovered at all. THIS
   LOWERS.** Recovery is restricted to keys the boundary provably left
   alone — decidable from the key, proved in `parsing.shows_only_itself`
   — so a declaration holding a line, control or bidirectional
   formatting character is not recovered. **Measured:** the
   control-character table validated against its own profile reports
   `presence.n_present`, `presence.n_missing`, `axes.role`,
   `axes.statistical_type`, `counts.n_not_numeric` and both distinctness
   counts MISSED — the same seven A-P3-15 clause 1 took off the `XX`
   table, given back on this class alone. And the printable table, which
   round 6 did pass, now misses the same seven: the two are one report
   again, which is the only honest answer while one description
   describes both.

   **Why the wider match is not the repair, since it is the obvious
   one.** Matching a cell as a hole when its DISPLAYED form equals the
   key passes both tables — and it is exactly what manufactures clause
   2's false pass, because it re-describes the other file as the one the
   description asks for. Any rule that passes the first passes the
   second, which is amendment A-P3-15 clause 3's own reasoning about the
   kept-`n/a` gap, reached again from the other declaration. A false
   MISS is a defect the report states; a false PASS is a defect the
   report hides, and where the format forces a choice this plan takes
   the stated one.

4. **What is left open, and where it can be closed. THIS CLOSES
   NOTHING.** The class is not closable inside `validation.py` under the
   current format, and the byte-identity above is the proof rather than
   the argument. What would close it is a decision about what the
   PROFILE publishes — a second, unescaped key beside the shown one, or
   a declaration recorded in the settings block — and both are changes
   to the profile contract, taken in the open, not edits to the
   validator. Until one is taken, the third gap joins the two amendment
   A-P3-15 clause 3 already records, and no sentence in this repository
   may call `missing_by_source` exact.

**How to reverse this.** Make `parsing.shows_only_itself` answer True
for every key, which restores round 6's unrestricted recovery, gives
back the seven misses on the escaped class, and puts the passing report
of clause 2 back on the file its own declaration rejects.
`tests/test_p3v7f1_escaped_declarations.py` is what goes red, and it
carries that reinstatement as `REINSTATE=P3-V7-F1`.

**Amendment A-P3-20 — the report a ZERO-ROW description gives was built
without calling the reader, so amendment A-P3-10 clause 2's construction
had one branch outside it. THIS RAISES; what it costs is two files
becoming refusals that used to be reports, and one registered red case
changing shape** (2026-08-15, review round 7 carrying review item
P3-V4-F3).

**What A-P3-10 clause 2 fixed and where it stopped.** That clause
removed this module's own walk of the measured file and made the
reader's refusal choose the report, so two files `synthtwin profile`
refuses with one sentence cannot reach two reports. It repaired the
paths a description that publishes rows takes. A zero-row description
never reached them: the branch on `n_rows == 0` RETURNED before the
reader was called at all, and the whole report was built on this
module's own record walk of the file's characters.

**What that cost, measured.** Against a headed zero-row description, the
file `column_1` over `1,2` and the file `other` over `1,2` are one
ragged refusal to the producer and drew **8 HELD / 1 MISSED** against
**5 HELD / 4 MISSED**. `header.names` reported HELD about a file no
reading of which finishes, which is a verdict on an obligation nothing
measured. The same held for a file with an unclosed quotation mark and
for a header repeating a name.

**What is enforced now.** The reader is called first on this path too,
and the degenerate report is reached by two routes, both of which have
had the reader speak: its own NO-DATA refusal, which is what the
conforming file draws, and a reading that finished, which is a file
holding rows against a description asking for none. Every other refusal
— ragged, a zero byte, a file that is not text, a first row that cannot
name columns — reaches the report or the refusal that word chooses,
exactly as it does against a description that publishes rows.

**What it costs, and it is two things.** A file the reader refuses for
something OTHER than no-data now comes back as that refusal where it
used to come back as a zero-row report; nothing is lost by it beyond a
report, because the refusal is the one `synthtwin profile` gives for the
same file and every obligation that report stated about it was stated
about a file nobody read. And the zero-row red battery's encoding edit
was a UTF-16 byte-order mark, which is a file the reader refuses
outright; it is now the single Latin-1 byte the ordinary battery already
uses — a file that is not UTF-8, that the reader accepts through its
documented fallback, and that leaves `bytes.utf8` a verdict to reach.

**What does NOT move.** Amendment A-P3-7 clause 3's ruling and its
residual are untouched: the disclosure gate still does not close on this
predicate, owner decision 7's byte form can still HOLD on the file its
description asks for, and two header-only files the producer refuses
alike still receive different reports. That residual is reached through
the reader's own no-data word now instead of around it, and it is still
pinned by `test_the_zero_row_residual_is_where_the_amendment_left_it`.

**How to reverse this.** Return the degenerate report on `n_rows == 0`
before calling the reader, which restores the 8-against-5 gap on the two
ragged files and `header.names` HELD on a file that is not a readable
table. `tests/test_p3v4f3_refusal_equivalence.py` is what goes red, and
it carries that reinstatement as `REINSTATE=P3-V4-F3-zero-rows`.

**Amendment A-P3-21 — the entry table's binding proof walked CHECKS and
called itself total over the shipped sites; a LISTING is the other half
of that table and its registry fact was compared with nothing. THIS
RAISES** (2026-08-15, review round 7 carrying review item P3-V4-F6).

**What A-P3-17 clause 3 said, and what was true.** That clause widened
the proof from six ordinary fixtures to the four profile predicates and
recorded it as total. It was total over CHECKS. V3.1 makes an entry's
identity (registry fact, profile predicate, subcheck) and V3.3 makes a
not-checkable obligation an entry of the same table, so half the table's
third term was asserted nowhere: `Listing.fact` was read by no test in
the suite.

**What was outside it.** Nine entries exist only where a corner sends a
fact to REPORT-ONLY — four offset facts, three identifier cardinalities
and two distinctness bars — and no fixture the proof walked reached a
corner at all. Rebinding `offsets.map` to another registry fact of the
same column left every assertion in
`tests/test_p3v1f2_entry_table.py` green while the report duplicated
one offset fact and omitted another. Beside them, fifty whole-grain
listings across eight fact families, and the seven
`axes.structural_role` listings amendment A-P3-2 made listings, were
bound by nothing.

**What is enforced now.** The walk collects checks AND listings, over
the six ordinary runs, the four predicates, and three corner
descriptions built here by the real producer — a datetime column whose
whole offset map the floor withholds, a declared identifier column
whose one-character family is one spelling short, and a numeric column
whose single style supplies one spelling for two hundred different
values. A listing carrying a subcheck is held to the same statement its
check-side twin is held to; a listing at the whole grain is held to a
set per family, because one family lists several such facts and they are
different facts. Both directions, as everywhere else in that file: no
entry may bind a fact outside the statement, and no line of the
statement may go unreached. The corner fixtures are held to the corner
each is for, so the proof cannot go green over a set the classifier
quietly emptied.

**What this does NOT claim.** The corner descriptions are three, not
every description that reaches a corner; what is asserted is that the
nine corner entries are filed and bound, not that no other corner exists.
They are outside `runs` on purpose: `runs` drives the red battery, where
every executable subcheck owes a perturbation that makes it MISS, and a
listing owes none because a listing has no verdict to make miss.

**How to reverse this.** Walk checks alone, or drop the corner runs from
the walk, either of which lets `offsets.map` bind whatever it likes.
`tests/test_p3v1f2_entry_table.py` is what goes red, and it carries the
rebinding as `REINSTATE=P3-V4-F6-listings`.

**Amendment A-P3-22 — amendment A-P3-16 clause 1 found the pooled
remainder by WALKING and clause 2 wrote the other half of the same rule
as a list of leaves, so the field whose kind was not on the list stayed
open. Clause 1 RAISES: the profiler's publication guard finds a pooled
remainder by the word it stands under, wherever it stands. Clause 2
RAISES: the floor-one derivation is run against BOTH halves of the
product, which is what would have found this. Clause 3 states what
neither closes** (2026-08-15, review round 7, item P3-V7-F6).

**What A-P3-16 clause 2 claimed, and what was enforced.** It said the
guard "now has vocabulary for the floor's other half: a tally of what
was held back, and one group size below the floor". That is true of the
three fields whose leaves carry the `count-at-the-floor-or-withheld`
kind and of the two that carry the held-back kinds. A `missing_by_class`
count carries the ordinary `count` kind, which accepts any whole number
of zero or more at any floor — so the real floor-eleven map, carrying
`(withheld): 2`, was grafted into a floor-one document and
`profile.check_publication` accepted it, while the strict loader refuses
it under S13. The two halves of the product disagreed about what a floor
of one means, in exactly the shape clause 1 of that amendment was
written to stop: each field WAS checked where it was written, and one
check did not know about the remainder.

1. **The guard reads the marker word before it reads the field's kind.
   THIS RAISES.** `profile._remainder_is_published` refuses a positive
   count standing under `(withheld)` at a floor of one, whatever field
   it sits in and whatever rule that field's leaf carries, and it runs
   before the kind is consulted. This is the loader's own reach, on the
   writing side: `(withheld)` is the format's one word for "held back"
   (contract section 14), so a fifth field putting a count under it is
   covered on the commit that adds it. Nothing changes for a document
   the producer actually writes, at any floor.

2. **The derivation asks both halves. THIS RAISES.** The floor-one
   derivation describes one table at the default floor and at one, reads
   the floor-governed positions off the difference, and grafts each back
   into the floor-one document. It was run against the strict loader
   alone, so a position the loader refused and the guard would have
   written sat inside the derived class and outside its reach. Two of
   the three walks it makes now put the same graft to
   `profile.check_publication` as well: every positive count standing
   under the marker word, and every tally the floor writes nonzero at
   eleven and zero at one. No field is named in either.

   **Why the graft had to be built twice, said because it is the reason
   this was never asked.** The loader reads BYTES, so its graft goes
   through JSON. The publication guard runs before serialization, on a
   document whose sentences are still enumerated note objects, and a
   JSON round trip turns every one of them into text the guard refuses
   for a reason that has nothing to do with the floor. A derivation that
   handed the guard the loader's graft would have reported every field
   refused and the invariant enforced everywhere, which is worse than
   not asking.

3. **What this does not close.** The THIRD derivation — the one that
   grafts a whole field rather than a leaf — is still put to the loader
   alone, and that is deliberate rather than pending: a floor-eleven
   `levels` array and a floor-eleven `sentinel_verdicts` block are both
   things the publication guard accepts at a floor of one, because
   nothing in them is a record of something held back; what the loader
   refuses them for is a total, which is a different invariant. Making
   the guard refuse them would mean teaching it arithmetic the loader
   already does. The prose exemption of A-P3-16 clause 5 is unchanged
   and still carries its residual: a hand-edited remark can say a group
   was suppressed at a floor that suppressed nothing, and no rule here
   reads it.

**How to reverse this.** Put the `missing_by_class` entry back under the
ordinary count kind and take the marker rule out of
`_leaf_is_published`. `tests/test_p3v5f1_floor_one.py` is what goes red,
in both of the walks that derive the class, and it carries the change as
`REINSTATE=P3-V7-F6`.

**Amendment A-P3-23 — plan section P3-D6 lists the G12-infeasible
refusal among the messages owed exact-shape and reachability tests, and
it had neither, because it was built by a private helper of
`validation.py` and the failure catalog walks `errors.py`. Clause 1
RAISES: the message joins the catalog. Clause 2 RAISES: its exact shape
is pinned for all four refusals. Clause 3 RAISES: it is reached by
running the shipped command. Clause 4 records the one wording rule that
moved and what it cost** (2026-08-15, review round 7, item P3-V7-F7).

**What was open.** Every rule the catalog keeps — that a message opens
as a sentence, ends as one, speaks no programmer's language, and tells
the reader something to DO — reached ninety-odd messages and not this
one. What tested it were two fragment assertions, `"cannot be this
description's twin"` and `"is valid"`. Replacing the whole message with
"The description is valid, but it cannot be this description's twin."
left both green and left the reader with no idea which two facts
collide, that the description is not corrupt, which file was being
checked, or what to do next.

1. **The message is a catalog entry. THIS RAISES.**
   `errors.no_twin_of_this_description_exists` holds the sentence and
   the four trouble clauses, and `validation.measure` calls it. The four
   refusal names method G12 fixes are spelled once, in `errors`, and
   `validation` re-exports them under the names it already published, so
   no caller and no test outside this repository sees a change. A test
   compares the names `refusal_of` can answer with the names the message
   is written for, so a fifth refusal added on one side without the
   other is red rather than an error on the way to the screen.

2. **The exact shape is pinned, per refusal. THIS RAISES.** For each of
   the four names the message must say which two published facts
   collide, that the description is valid, that it was written by
   synthtwin and loads, that no file can be its twin, that there is
   nothing to measure against, which file was checked, and BOTH
   instructions — describe the table again, and ask whoever wrote the
   description. The review's own vague replacement fails all four cases.

3. **It is driven through the shipped command. THIS RAISES.** The
   driven battery gains a ninth case: a table of twenty-six
   one-character values outside the code alphabet is written, `synthtwin
   profile` describes it, and `synthtwin validate` on that description
   must stop with this refusal at exit code 1. Every part of it is the
   real product; no document is edited by the test.

4. **What it cost, stated.** The catalog's list of what counts as an
   instruction gains "Describe the table again". That is not a
   loosening: it is the instruction this refusal gives, and it is the
   only sound one — nothing done to the measured file helps, because the
   trouble is in the description. **What this does not close:** the
   driven case reaches ONE of the four refusals through the command.
   The other three are pinned in shape here and reached from
   `validation.measure` by their own tests, which is a weaker claim than
   the plan's word "reachability" carries for the one, and it is said
   rather than counted.

**How to reverse this.** Build the message inside `validation.py` again.
`tests/test_failure_catalog.py` is what goes red — the reachability case
alone, which is the exact hole round 7 found — and it carries both
routes as `REINSTATE=P3-V7-F7` and `REINSTATE=P3-V7-F7-vague`.

**Amendment A-P3-24 — two guards whose stated reach was wider than
their walk, and the amendment sentence that said so about one of them.
Clause 1 RAISES: the exact-identity closure guard is total over the ways
a call can be spelled. Clause 2 RAISES: the withdrawn-defence ban reads
a promise the next statement makes. Clause 3 NARROWS A SENTENCE of
amendment A-P3-17 that claimed more than was true** (2026-08-15, review
round 7, items P3-V7-F5 and P3-V7-F8).

1. **Every spelling of a call is now judged. THIS RAISES** (item
   P3-V7-F5). The guard that walks the closure of the rule deciding
   which cells a file's own description reads reduced a call target to a
   dotted path, and answered NOTHING for a target that was not a name or
   an attribute — so `readers = (float,); readers[0]("1")` put a reader
   that answers in binary64 inside the closure and the walk reported it
   clean. The reduction is now total: a target is a path of plain names,
   or it carries a mark saying the walk lost sight of it, and each mark
   is refused where the thing being CALLED is what the mark stands for.
   **The ways covered**, each with a probe of its own: a subscript; what
   another call handed back, which is also how a name written out as
   text is reached; a conditional, a walrus and anything else the reader
   cannot read; a call spelled as a double-underscore attribute; and a
   bare name this scope binds by an assignment, an annotated assignment,
   an augmented assignment, a walrus, a loop, a comprehension, a `with`,
   a caught error, or a PARAMETER — which is how a reader arrives from
   outside. A second rule refuses a rounding reader NAMED where a value
   belongs even when nothing here calls it, because `map(float, cells)`
   hands it every cell and spells no call on it; a reader named where a
   TYPE belongs is left alone, and three functions of the closure carry
   one.

   **What this does not close, measured rather than promised.** A
   rounding reader reached as an ordinarily-named method of a value the
   walk cannot name — `_chosen().reads(cell)` — has the same shape as
   the honest method calls the closure really makes on text, and telling
   them apart needs the types this walk does not have. Reaching it means
   adding a function whose whole purpose is to hand back a reader under
   a name that is not one of the four. The three marks are refused at
   the CALLED position only, and that is measured: refusing a mark
   anywhere in the path reports `text[0].strip()` and
   `text.strip().casefold()`, which are the ordinary way this package
   handles text.

2. **A promise may be carried to the next statement. THIS RAISES** (item
   P3-V7-F8). The ban reads a defect as one statement that names the
   out-of-scope reader AND promises something about them. "A person can
   re-run the check with descriptions they wrote themselves; the
   withheld number remains unknowable" is that promise written across a
   semicolon. It is withdrawn everywhere here, and every word of it was
   already in the lists. A statement that names the reader and promises
   nothing is now read together with the statements following it, within
   the same reach the cure is allowed.

   **The price was measured before the rule was written.** Carrying a
   bare promise mark forward reports honest prose — between four and ten
   statements of this tree, depending on the reach, where a naming about
   one subject sits beside `never` or `cannot` about another. So a
   carried promise has to be ABOUT THE WITHHELD THING, in the format's
   own words for it. With that requirement the carry reports nothing at
   all on this tree at any reach up to four hundred characters, and
   reports the review's sentence. **What it does not close:** a promise
   carried further than that reach, and a promise about a withheld
   number that uses none of those words for it. The naming half is
   unchanged and keeps the bound A-P3-17 clause 1 states.

3. **A-P3-17 clause 1 said "two further gaps in the ban itself, both
   closed, and one that cannot be". THIS NARROWS THAT SENTENCE.** There
   was a third gap, it was neither of the two, and it was not the one
   the clause called unclosable: the ban read one statement at a time.
   The sentence is corrected where it stands rather than deleted,
   because what it recorded about the other two is true and is the
   history. Nothing about the finite reader-noun list moves: it is still
   the one place in this family where a miss is a false negative, the
   sound alternative is still one canonical passage with every other
   mention refused, and it was still measured at thirty-four statements
   to rewrite. That decision is still the owner's and is still open.

**How to reverse this.** Read a call target as a dotted path again, or
read one statement at a time again. `tests/test_p3v4f1_kept_values.py`
and `tests/test_claim_inventory.py` are what go red, and they carry the
two as `REINSTATE=P3-V7-F5` and `REINSTATE=P3-V7-F8`.

**Amendment A-P3-25 — three ordinary defects of round 8, and the two
sentences of this plan that were wider or narrower than the code.
Clause 1 RAISES and re-roots a guard: a key the description states in
figures is read as figures, and the guard against reading it otherwise
now follows the KEY rather than one rule. Clause 2 RAISES: a corner
authorizes the facts its own passage names, asked per fact. Clause 3
RAISES and CORRECTS amendment A-P3-18 clause 5, which stated a boundary
wider than the one that exists** (2026-08-15, review round 8, items
P3-V8-F5, F3 and F4).

1. **A published key is decimal text and is read as decimal text, and
   the guard for that is rooted at the key. THIS RAISES, and it is the
   fourth repair of one class** (item P3-V8-F5).

   The keys of a multiplicity map are row counts written in figures; the
   contract's loader admits them with `_all_digits` and reads them with
   `int`, and so does the generator. The validator read them through
   `parse_number`, which answers in binary64 and is exact only below
   nine quadrillion. A contract-valid description publishing ten groups
   of `9007199254740993` rows each therefore came back with a widest
   group ONE ROW SHORT, ninety quadrillion cells divided by it needed
   ELEVEN different spellings where ten answer exactly, and the figures
   band at one character holds ten -- so `synthtwin validate` stopped at
   exit code 1 with the sentence that no file can be this description's
   twin, on a description the shipped generator builds. On a DECLARED
   column the same arithmetic claims owner decision 6's corner instead,
   which takes three checks off the report rather than stopping the run:
   the quieter cost, and the one a green suite says nothing about. Four
   sites read a key that way -- `_group_sizes`, `_widest_group`,
   `_group_span` and `_occurrence_key` -- and all four now read it
   through `contract.occurrence_size`, the contract's own reader. A
   sweep of the shipped source found no fifth: `summary._number_in`,
   `profile._within_the_floor` and the loader itself already read a key
   with `int` after a digit check.

   **WHY THE GUARD THAT EXISTS DID NOT CATCH IT, which is the part that
   matters.** The guard round 5 built and rounds 6 and 7 widened walks
   the CLOSURE OF ONE RULE -- the rule deciding which cells a file's own
   description reads. These readers were never in that closure: they
   belong to the corner classifier and the refusal classifier, reached
   from different entry points entirely. The guard was rooted at a
   DECISION while the class is about a KIND OF VALUE, so rooting it at
   one more decision would leave the next site open exactly as this one
   was. **So a second guard is added that follows the value**
   (`tests/test_p3v8f5_published_keys.py`): every field the profile
   contract annotates `dict[str, ...]` is a mapping whose keys are the
   description's own text, and the walk follows those keys out of the
   mapping, through assignments, through `sorted` and `keys` and
   `items`, and through calls into other shipped functions, refusing
   `parse_number`, `float`, `round` and `complex` wherever one arrives.
   `int` is deliberately permitted: on decimal text it is exact at every
   size and it is what the loader reads the key with. The published
   field list is read off the contract's own dataclasses, so a field
   added to the profile is inside the guard on the commit that adds it.
   Eight probes drive it, one of them the shipped site exactly as the
   review found it.

   **What this does not close.** The walk reads a call whose target is a
   path of plain names, resolving import aliases and plain assignments;
   a key handed to a target it cannot name is refused rather than
   followed, which is safe but is a refusal and not a reading. And it
   judges kinds without statement order, treating a name that holds a
   key anywhere in a function as holding one throughout -- the direction
   that reports more, not less.

2. **A corner authorizes the facts its own passage names, and the
   question is asked per fact. THIS RAISES** (item P3-V8-F3).

   The three corners that reach a distinctness count do not reach the
   same ones. Owner decision 6's identifier corner names `n_distinct`,
   `n_distinct_folded` and `n_distinct_by_occurrences`; G12.8's numeric
   envelope is written for the raw count and, in its own last sentence,
   "the same over the folded identities"; G12.7's label envelope is RAW
   `n_distinct` and nothing else, in V4.1's words and in the disposition
   registry's. One field-blind question was asked for both counts, so
   G12.7's authorization landed on a folded count it does not name. The
   witness is round 7's own label column -- `alpha`x6, `Alpha`x6,
   `beta`x5, `Beta`x5 -- which publishes folded distinctness 2 against a
   supply of 3: a file holding THREE folded identities was printed as
   `2 (between 2.0 and 3.0)` and reported an AUTHORIZED DEVIATION where
   the exact published count is 2 and it must MISS.

   **AND THE TWO TESTS THAT SHOULD HAVE CAUGHT IT ARE REPAIRED, because
   otherwise the hole stays open behind a green suite.** The corner
   comparison skipped any fact the generation report does not name --
   and it names only what its construction could not meet exactly, so
   the folded count of a label column, which the generator meets
   exactly, was never compared at all. Silence there means the generator
   PINNED the fact, so the comparison now asserts that this validator
   pinned it too, and it is asserted on at least four such entries. The
   registered red case that builds files to prove every printed
   distinctness bar can be missed asked the question of the raw count
   alone; it asks it of both counts now, over more than two hundred
   entries.

3. **G12.8's supply has two summands and only the first was ever
   written. THIS RAISES, and it CORRECTS amendment A-P3-18 clause 5**
   (item P3-V8-F4).

   The method's formula is the numbers class, counted by (value, style)
   group, PLUS, for each other class, `min(its cell count, its share of
   the budget in G6.5)`. The second summand was absent from this
   validator entirely, and both of its inputs are published numbers: the
   four class cell counts and the count being checked. A column of
   twenty whole numbers written one way beside two cells that are not
   numbers -- `0,100,...,1900,alpha,beta` under a parse-rate line of
   .8 -- publishes twenty-two present cells and twenty-two different
   values; the generation report prints the bound `[22,22]` for both
   distinctness facts; this validator computed `[1,22]`, which reaches
   from one value to every cell of the column. A bar admitting every
   count is a bar that cannot fail, so amendment A-P3-18 clause 3 turned
   BOTH obligations into listings, and a file holding twenty-one
   different values against a published twenty-two was told that no
   checkable obligation was missed, at exit code 0. With the second
   summand the floor is three, both entries are checks again, and a
   column collapsed onto one repeated value MISSES.

   **A-P3-18 clause 5 said the plain cells' value count was the whole
   of what this validator cannot compute, and then wrote a floor that
   gave up far more than that.** The sentence is corrected where it
   stands: the classes are exactly knowable and are now counted at BOTH
   ends, the ceiling among them -- it added the other classes' CELL
   COUNT where its own comment already said "their share of the G6.5
   budget", and the share is what it adds now. **What is still open is
   one thing and it is measured rather than described:** how many
   different VALUES the plain cells carry is decided by the value
   construction of G5, which V1.4 keeps out of this module. So on the
   witness above the floor is three where the generation report prints
   twenty-two, and a file ONE different value short of the published
   count is an AUTHORIZED DEVIATION here rather than a MISS.
   `test_the_class_witness_gets_g12_8s_second_summand` asserts that
   residue at its size and goes red if it moves in either direction.
   Narrowing it still means writing G5's value construction out here, as
   V3.4-A2 did for the datetime windows; that is still a later item.

   **WHAT ELSE MOVED, and it is a bar going up rather than a gap
   growing.** Amendment A-P3-15 clause 3 records the unrecoverable
   kept-marker gap at five subchecks. It is SEVEN now, and the two that
   joined it are `distinct.n_distinct` and `distinct.n_distinct_folded`
   on that same witness. The description publishes two hundred decimal
   cells and one cell that is not a number; the two summands together
   reach two hundred and one, which is the published count exactly, so
   the description pins both counts and the exact bar is theirs. While
   the class summand was missing the supply read two hundred, a corner
   the generator does not need was claimed, and the envelope it opened
   -- two hundred to two hundred and one -- was wide enough to call this
   very file's two hundred an AUTHORIZED DEVIATION. The one cause of the
   gap is unchanged; two of its consequences stopped being hidden inside
   a bar that should never have been lowered. Clause 3 of A-P3-15 is
   corrected where it stands.

**How to reverse this.** Clause 1 reverses by reading a key through
`parse_number` again, which re-opens the refusal and the corner;
`tests/test_p3v8f5_published_keys.py` carries it as
`REINSTATE=P3-V8-F5`, and its guard's own red is the eight probes it
runs whether or not that variable is set. Clause 2 reverses by asking
the corner without the field, and clause 3 by writing G12.8's supply
with its first summand alone and its ceiling with the other classes'
cell counts; `tests/test_p3v7f2_corner_parity.py` carries both as
`REINSTATE=P3-V8-F3` and `REINSTATE=P3-V8-F4`.

**Amendment A-P3-26 — a description that cannot be read back says so
per obligation, instead of printing a failure it cannot support. THIS
LOWERS what is checked on an affected column and RAISES the report's
truthfulness, and both are stated below with the sizes they were
measured at** (2026-08-16, OWNER RULING of that date, taken after the
four options were put with their costs; review items P3-V4-F1's
remainder, P3-V7-F1's remainder, P3-V8-F1 and P3-V8-F2).

**One cause, five routes, and it was found by four review rounds
arriving at the same place by different roads.** `synthtwin validate` is
defined as: rebuild the reading rule from the description, re-describe
the measured file with it, compare (validation method V2.2). That
definition needs the description to pin the reading rule. It does not.
The settings block records a declaration as a COUNT and never as text
(`values_recorded: false`, the Phase 1 confidentiality rule), and the
one field where a spelling survives — a column's `missing_by_source` —
is narrowed on the way out in four separate ways, with a fifth defect
beside them:

1. the named spellings are never written into the settings block at
   all, so a `--keep-value` on a column publishing no level and no
   sentinel verdict is published nowhere (P3-V4-F1's remainder);
2. a key crosses the DISPLAY BOUNDARY, so any spelling holding an
   invisible character is unrecoverable and two tables needing opposite
   rules are described byte for byte alike (P3-V7-F1's remainder);
3. a spelling whose cells sit below the publication floor is pooled,
   unnamed, into the withheld remainder;
4. a column whose publication class publishes no value of the table —
   free text — publishes an EMPTY source map, on purpose (P3-V8-F1);
5. and that map's keys are the person's own text and this package's
   class words in one list with nothing to tell them apart, so a table
   whose cells literally read the pooled remainder's own word publishes
   the key the pool wears (P3-V8-F2).

**Only route 4 is a conflict between publishing safely and describing
completely.** Route 2 is a presentation rule doing a protection rule's
work; route 5 is two alphabets in one list; route 1 is drawn at the
wrong width. Those are not repaired here — repairing them is a change
to what a description publishes, and the owner's ruling is that this
amendment does not make one.

**WHAT WAS HAPPENING, AND WHY IT IS THE WORST KIND OF WRONG OUTPUT.**
On every one of the five routes, a table validated against its OWN
genuine description came back with obligations MISSED — seven on the
rescued-word witness, seven on the escaped-key witness, seven on the
pooled and class-word witnesses, eleven on the free-text witness — with
the numbers the incomplete reading produced printed beside them. The
file was its own description's perfect match. This plan holds a passing
report to meaning exactly what it says; this is the mirror, and a
specific, numeric, plausible falsehood is harder to disbelieve than a
silence.

**WHAT HAPPENS NOW.** Before any file is read, the description is asked
whether the reading rule can be rebuilt for each column. Where it
cannot, that column's cell-counted obligations go to the NOT-CHECKABLE
census — the bucket that already exists, is counted separately, is never
folded into a pass, and carries a printed reason on every line — with a
sentence saying what the description does not record. Nothing about the
measured file decides it.

**The question is decidable from the description even where the rule is
not recoverable, and it is asked as the UNION of two tests** because
neither alone is both sound and complete. Per column: are there cells
the description says a declaration made absent that no brought-back
spelling accounts for? Per document: does the settings block name more
words, in either of the two ways, than the description carries? The
structural test alone walks past the table where one named word is
published and another is pooled; the head count alone reports a gap on
a table where somebody named a word the table never held. The union
never misses a real gap. **Where it over-fires it moves obligations to
not-checkable on a file that would have passed anyway, and that
direction is the safe one**; the other one prints a number about a file
that is not true of it. The over-fire is asserted at its size in
`tests/test_ap326_unrebuildable_reading_rule.py` so that narrowing it
later is a change somebody chose.

**The one narrowing taken, and it is a proof rather than a preference.**
On the absence side the head count is asked only of a column whose
`missing_by_class` publishes a declared hole or a pooled remainder. The
producer counts every absent cell into one of five classes and pools any
class below the publication floor into the fifth, so a cell a
declaration made absent is in one of those two numbers; zero in both is
a column no declared word appeared in, and a word no cell of that column
wore cannot change how that column reads. On the kept side no such count
exists — a rescued cell is PRESENT and no published number says how many
present cells were rescued — so that half is asked of every column, and
that is the wider of the two costs. **(AMENDED by A-P3-29: one does
now. Contract version 5's settings block records which of this
package's own words a `--keep-value` named, contract 5 section 6.4
proves those are the whole of what a rescue can change, and the
kept-side head count is deleted rather than narrowed. This paragraph's
absence-side half is unchanged and still binds.)**

**WHAT IT LOWERS, MEASURED.** Every obligation of an affected column
whose measurement is counted over its cells becomes a listing. Only
`position.at` stays a check, because it is measured from the file's own
names and column count and no cell touches it.

| witness | checkable before | MISSED before | moved | checks left |
|---|---|---|---|---|
| free text, marker declared (route 4) | 31 | 11 | 21 | 10 |
| rescued word on a numeric column (route 1) | 53 | 7 | 43 | 10 |
| escaped key (route 2) | 53 | 7 | 43 | 10 |
| pooled spellings (route 3) | 53 | 7 | 43 | 10 |
| class word as a person's own cell (route 5) | 53 | 7 | 43 | 10 |
| one word published, one pooled | 53 | 7 | 43 | 10 |

**(AMENDED by A-P3-29, and four of those six rows no longer describe
the shipped tree.** Routes 1, 2 and 5 are closed, so their witnesses are
measured in full — 53 checks and nothing moved — and the free-text row
holds only where the marker is a word of the PERSON'S own. The two rows
that stand unchanged are route 3's and route 4's, which contract 5
section 7 says no version of the format closes. The table that binds is
A-P3-29's; this one is the record of what the ruling of 2026-08-16
bought and cost on the day it was taken.**)**

**The width is wider than the misses, deliberately.** Which obligations
the unattributable cells reach depends on the spelling nobody recorded:
the free-text witness's twelve three-character markers move
`length.min`, and twelve twenty-character markers move `length.max`
instead. A rule that moved only the obligations that missed on one
marker would keep printing false failures for another spelling of the
same gap, so the rule moves every obligation the cells decide.

**WHAT IT RAISES.** The report stops stating about a measured file
anything the description does not support stating. That is the whole of
what these four review items were, and it reaches all of them at once —
including route 4, which no change to the description's format can
close, because publishing the marker word of a free-text column would
publish text out of a column that exists to publish none.

**WHAT IT LOWERS IN THE VERDICT ITSELF, in one construction, and this
is the first of the two risks the ruling was taken against.** A file
that really does violate one of the moved obligations now returns exit
code 0 with those obligations named, because a not-checkable line is not
a failure. The construction is amendment A-P3-19's: one description, two
files it cannot tell apart, one of them conforming and one not. Under
A-P3-19 both came back at exit 3 with seven misses; both come back at
exit 0 now with the same seven obligations named as ones this
description cannot support asking. What the report no longer does is
claim to have measured them. Both halves are asserted in
`tests/test_p3v7f1_escaped_declarations.py`.

**AND THE TWIN CARRIES THE SAME LIMIT, which is the second risk and is
stated because it is a real cost to the ordinary workflow.** All five
routes vanish on the twin — it writes every absent cell as an empty
field, so no marker word survives into it — but which obligations a run
can check is a function of the DESCRIPTION (validation method V3.3), and
the twin shares its description with the table. So the twin of an
affected description passes with exit 0 and nothing missed, and its
cell-counted obligations are named as not-checkable exactly as the
table's are. **This is not avoidable inside the validator**: deciding it
from the file is deciding it from something the description cannot see,
and two files one description cannot tell apart would then get two
reports, which is V5.1. It is avoidable in the FORMAT, and that is the
argument for taking option B before the first release.

**WHAT WOULD NARROW EITHER RISK, named rather than left implicit.**
Three routes, none taken here: a distinct exit status for a run whose
census is short; a bound on each moved obligation drawn from the count
of unattributable cells the description publishes, which would turn a
listing back into an envelope with teeth; and the format change that
records which words were named, which closes routes 1, 2, 3 and 5 at
the root and leaves route 4 as a stated limit. Each is an owner
decision.

**WHAT DOES NOT MOVE.** No profile format change, no version bump, no
regenerated golden, no change to the twin's bytes, and no narrowing of
`validate`'s promise to measure whatever file it is pointed at. The
three gaps amendment A-P3-15 clause 3 and amendment A-P3-19 clause 4
record are exactly as unrecoverable as they were; what changed is what
the report does about them.

**How to reverse this.** `REINSTATE=A-P3-26` makes no column
unrebuildable, so every witness re-describes the file under an
incomplete rule and reports the misses again.
`tests/test_ap326_unrebuildable_reading_rule.py` carries it, and
`tests/test_p3v4f1_kept_values.py` and
`tests/test_p3v7f1_escaped_declarations.py` carry it too, because the
two gaps they measure at their size are measured differently now.

**Amendment A-P3-27 — the description format is extended so that the
reading rule survives being written down: contract version 5. THIS
RAISES what a description carries and what a report can honestly
check, and it LOWERS one Phase 1 confidentiality rule by a stated and
bounded amount; both are written out below with the sizes they were
measured at** (2026-08-17, OWNER RULING of that date, taken after four
options were put with their costs; review items P3-V4-F1's remainder,
P3-V7-F1's remainder, P3-V8-F1 and P3-V8-F2, and residuals R-P3-4,
R-P3-5, R-P3-6 and R-P2-13, which are the same one cause under four
more names).

**THE RULING.** Amendment A-P3-26 stopped `synthtwin validate` from
printing failures it could not support. It did not put back the
information whose absence caused them: a description does not carry
the reading rule, so a table checked against its own genuine
description has whole columns' worth of obligations listed as not
checkable — and so does the TWIN of that description, because which
obligations a run can check is a function of the description and the
twin shares its description with the table. A-P3-26 named the format
change as the thing that would close four of the five routes at the
root and said each of the three ways to narrow its two residual risks
was an owner decision. The owner has now taken it: **extend the
format.**

**WHY NOW, AND THIS IS THE WHOLE OF THE TIMING ARGUMENT.** The version
is `0.1.0.dev0`. There is no release, there are no tags, the changelog
has one `[Unreleased]` section, and every description in existence
belongs to somebody who still holds the table it describes. A version
bump therefore costs one sentence and one refusal message. After the
first PyPI release the same change costs a migration story, a
deprecation, and other people's regenerated files, and that price
never comes down again. The owner's reason is recorded as given: this
is Phase 5 groundwork brought forward while it is free. A phase that
carries cross-column structure needs a version bump anyway, and it
needs to know which cells were absent and why in order to model which
cells are empty together — so the fields this amendment adds are
fields that phase would have had to add.

**WHAT IS BUILT, IN THREE PARTS, EACH CLOSING ONE ROUTE.** The
normative document is `docs/spec/profile-contract-v5.md`, written
before any code as this plan's own process requires, and it governs
the implementation stages that follow it.

1. **The spelling is stored exactly, and escaped only when printed**
   (contract 5 section 4). A `missing_by_source` key becomes the source
   spelling character for character, and the display boundary is
   applied where the key is SHOWN. This is what `variants` already
   does, for the reason version 4 already states about it. Closes
   route 2.
2. **The pooled count and the blank count leave the map** (contract 5
   section 5). `missing_by_source` keeps one key space — the table's
   own spellings — and `(withheld)` and `(blank)` become two counts of
   their own, `n_missing_withheld` and `n_missing_blank`. This is what
   `variants_withheld` already does. Closes route 5, and with it the
   last field of the format in which somebody's data and this
   package's own word could land in the same slot.
3. **Which of this package's own words a declaration named is
   recorded** (contract 5 section 6). Each of the two declaration
   records gains `built_in_texts` and `built_in_numbers`, holding
   members of a closed thirteen-member vocabulary the contract
   publishes. Closes route 1.

**WHAT IT RAISES, item by item.**

- A description that carries a declared spelling carries it exactly,
  so two tables needing opposite readings can no longer produce
  byte-identical descriptions. Under A-P3-19 that pair cost a verdict
  in both directions: the control-character table missed seven
  obligations against its own description, and a file wearing the
  printable spelling PASSED against the other table's description with
  a census of zero missed.
- A table whose cells literally read `(withheld)` or `(blank)` is
  describable. Version 4 published, for those cells, the key this
  package's own pool wears.
- The whole of the `--keep-value` side of the reading rule becomes
  recoverable, and contract 5 section 6.4 proves it is the whole
  rather than a part: the values for which a rescue can change any
  cell's reading are exactly the members of the published vocabulary,
  so a rescue of anything else changes nothing and recording it would
  record a fact with no consequence.
- A-P3-26's own wider cost narrows with it. That amendment asks its
  head count of EVERY column on the kept side, "because no published
  number says how many present cells were rescued", and calls that the
  wider of its two costs. Under version 5 the kept side is answered
  from the two lists, so the question is decided rather than assumed.
- The published vocabulary becomes normative (contract 5 C5-15). In
  version 4 the built-in lists are an implementation detail that can
  change without touching any document; from version 5 they are part
  of the wire, because a consumer decides what a key means by asking
  whether it is one of them.

**WHAT IT LOWERS, AT ITS SIZE, AND ON WHOSE AUTHORITY.** One rule, and
it is a Phase 1 rule this plan is otherwise forbidden to narrow.

Phase 1 fixed at review item P1-R7-F2 that the settings block carries
the POLICY — how many values were named each way, and the rules that
matched them — and **never a spelling**, because a declaration is
compared against every cell of every column and a spelling written
there would publish a value out of all of them at once, free-text and
record-number columns included. **From version 5 the settings block
names which members of this package's own published vocabulary a
declaration named.** It still carries no spelling of the person's own.

The size of the loss, stated exactly:

- what is added is which members of a THIRTEEN-MEMBER list, printed in
  the contract's own appendix, were among the values typed — ten
  spellings and three stand-in numbers, identical in every
  installation, the same whatever table the tool is run on;
- it carries no count of cells, no column, no row and no text of the
  table, and the member's own spelling is written rather than the
  person's, so their spacing and their capitals do not travel either;
- it is written identically whether or not the named word occurs in
  the table (contract 5 C5-16), so the field itself is not evidence
  that any cell wore the word;
- what a reader can still infer is said rather than waved away: people
  usually type a word because it is in their table, so a version 5
  description makes available a guess a version 4 description made
  only coarser — not "one value was rescued" but "the value rescued
  was one of these thirteen". The word guessed at can never be a name,
  a code, a diagnosis or a free-text answer, because a value outside
  the list is never written;
- and where a reader puts a vocabulary member beside a column's own
  `missing_by_class` and `n_missing_withheld` and concludes that a
  below-floor group wore that word, the bound is exact: the SIZE of
  that group is a number version 4 published too, and the word is one
  of thirteen this package publishes. What version 5 adds to that
  combination is the thirteen-member guess, not a new count and not a
  new group.

On whose authority: the owner's, ruled on 2026-08-17 with this delta
stated to them. The analysis put to them named this as the part that
touches a Phase 1 rule and said the call was theirs and not the
implementer's; it has now been made.

**AND ONE SECOND-ORDER PUBLICATION, PRICED SEPARATELY.** Storing the
spelling exactly publishes, for a group the floor already permits to
be named, which of the spellings sharing one printable form it was. It
is empty for every spelling made of characters that show themselves,
which is every ordinary word. No group version 4 withheld becomes
named, no count changes and no row is identified. **In one corner it
runs the other way and version 5 publishes LESS**: version 4 applied
the floor to the ESCAPED key, so two different spellings that escape
alike were counted together and their combined count could reach the
floor although neither alone did; version 5 applies the floor to the
exact spelling, so each is pooled on its own.

**WHAT IT DOES NOT LOWER, in as many words.** `values_recorded` stays
`false`. A declared value that is not a member of the published
vocabulary is recorded nowhere. Every publication class of contract
6.10 is unchanged, so a nothing-publishing column publishes no value
of the table in version 5 either. Every floor rule is unchanged, at
every floor including one. No column block publishes a fact version 4
did not publish. The relationship manifest stays eight nulls and
`validation_targets` stays `null`.

**WHAT IT DOES NOT CLOSE, and this is stated here as plainly as the
contract states it.** Two of the five routes stay open, and neither is
a defect this amendment is deferring.

- **Route 4, and it is a genuine conflict.** On a column that
  publishes no value of the table — free text, record numbers,
  declared identifiers, unrepresentable numbers — the source
  accounting is emptied on purpose. Publishing the marker word there
  would publish text out of a column that exists to publish none. **No
  change to this format can close it.** The eleven obligations
  A-P3-26 moves on the free-text witness stay moved; twenty-one of
  thirty-one move and ten checks remain, and version 5 changes none of
  those numbers.
- **Route 3, and it is a small one.** A spelling shared by fewer than
  `small_cell_floor` cells is pooled and unnamed, in version 5 exactly
  as in version 4, unless it is one of this package's own words, which
  section 6 records anyway. Closing it would mean naming a group the
  floor exists to keep too large to point at.

**AND A-P3-26'S OWN FORWARD-LOOKING SENTENCE IS CORRECTED HERE, rather
than left to be discovered.** That amendment named, among the three
narrowings it did not take, "the format change that records which
words were named, which closes routes 1, 2, 3 and 5 at the root and
leaves route 4 as a stated limit". **Route 3 is not closed by the
change actually taken, and counting it as closed was wrong.** Naming a
spelling that fewer than `small_cell_floor` cells share is the one
thing the floor exists to refuse, so no version of this format closes
route 3 for a word of the person's own; version 5 closes it only where
the word is one of this package's own, which section 6 records for a
different reason. The sentence stands where it is as the record of
what was thought at the time; the count that binds is this one — three
routes closed, two left, and both of the two named above.

Both stay covered by A-P3-26's routing, which is not withdrawn and not
weakened: the description is still asked whether the reading rule can
be rebuilt for each column, and where it cannot the column's
cell-counted obligations still go to the NOT-CHECKABLE census with a
printed reason. **What version 5 changes is how often the answer is
yes.**

**THE MEASURED COST, counted at commit `1179250` with the shipped
tree rather than estimated.**

| what moves | where | count |
|---|---|---|
| `missing_by_source` | product modules | 40 places in 7 modules — `profile`, `taxonomy`, `contract`, `rendering`, `summary`, `quality`, `validation` |
| `missing_by_source` | tests | 72 places in 19 files |
| `missing_by_source` | governing and historical documents | 42 places in 6 documents, plus 5 in the review records, which are not edited |
| `profile_version` | everywhere | 74 places |
| the two declaration records | product, tests, documents | `kept_values` 36 / 30 / 9; `declared_missing_values` 26 / 34 / 7; `values_recorded` 11 / 14 / 9 |
| the frozen reference vectors | `tests/reference/` | 2 of the 3 files carry profile fragments naming the field, 15 places, regenerated as bookkeeping |
| the specification itself | `docs/spec/profile-contract-v5.md` | 1,172 lines, 302 sealed passages, landed with this amendment |

It is a bounded, mechanical change with a large blast radius — more
tedious than difficult — and that was put to the owner before the
ruling was taken.

**AND WHAT DOES NOT MOVE, which is the reason the radius is smaller
than it looks.** **No cell of any twin changes.** No generation rule
reads any field this amendment moves: the generation module never
names `missing_by_source`, and the twin still writes every absent cell
as an empty field. So no golden twin's bytes move, no determinism
event under D12 touches the twin, and the reference-vector
regeneration is bookkeeping over profile fragments rather than a
change to anything a person receives. The printed form of a key does
not move either, because the display boundary is applied at the moment
of printing and prints the same characters it printed before.

**SEQUENCING, and it is the standing process rather than a new one.**
The specification lands first, alone, with no product code — this
amendment and `docs/spec/profile-contract-v5.md` in one commit with
their seal entries and the registry guard's updated exact list, which
grew by one line because a fourth specification appeared beside the
three. The producer, the loader, the validator, the reports and the
documents that quote the field follow in later stages and are held to
what the specification says. `docs/spec/validation-method-v1.md` and
`docs/spec/generation-method-v1.md` are NOT amended here; each is
amended at its own stage, against the contract, by counted re-seal.
Until those stages land, the shipped producer and the shipped loader
stay at the wire version this phase opened with, and no sentence
anywhere may say otherwise. **(AMENDED by A-P3-28, which landed the
producer and the loader: the shipped producer now writes version 5, the
shipped loader reads version 5, and it is that sentence which binds.
The two method specifications are still not amended. AND THE STRUCK
SENTENCE NO LONGER SPELLS THE NUMBER IT NAMED, under A-P3-30: this
paragraph said in as many words which version the shipped producer
wrote, that number went stale the moment the next stage landed, and a
governing document is now walked for exactly that sentence shape by
`tests/test_claim_inventory.py`'s fifth family. What the clause meant
is preserved -- the wire does not move until the stage lands -- without
a digit that only one commit makes true.)**

**How to reverse this.** There is no `REINSTATE` variable, because no
product code changed: this stage is a specification and this
amendment. The reversal is that the implementation stages do not land
and `docs/spec/profile-contract-v5.md` is withdrawn from the tree,
with the registry guard's exact list, `tests/dispositions.py`'s
governing set, the claim inventory's surface list and the seal moved
back in the same commit — and this amendment struck rather than
deleted, so that the ruling and its price stay readable. Once the
producer writes version 5, reversal is a second version bump and is no
longer free; that is exactly the property that made the owner take it
now.

**Amendment A-P3-28 — the producer writes version 5 and the loader
reads it. THIS RAISES what every description carries and what a
version 4 file is worth; it LOWERS nothing that A-P3-27 did not
already price, and the two new counts are disposed here so that no
published field of the format is left without a class** (2026-08-17,
carrying out A-P3-27 on the owner's ruling of the same date; the
implementation stage that amendment's own SEQUENCING paragraph names
first).

**WHAT LANDED.** `synthtwin profile` writes `profile_version: 5`, and
the strict loader reads 5 and refuses everything else. All three parts
of A-P3-27 are in the shipped code:

1. a `missing_by_source` key is the source spelling character for
   character, and the display boundary is applied where a key is SHOWN
   — in the plain-language summary and in the generation report, which
   print the same characters they printed before;
2. `n_missing_blank` and `n_missing_withheld` are on every column
   block of every role, and `missing_by_source` holds one key space,
   the table's own;
3. `settings.kept_values` and `settings.declared_missing_values` each
   carry `built_in_texts` and `built_in_numbers`, holding members of
   the thirteen-member vocabulary contract 5 section 14.1 fixes.

**THE DISPOSITION OF THE TWO NEW COUNTS, stated here because the
registry reads this plan and not the contract.**

| field | disposition |
|---|---|
| `n_missing_blank`, `n_missing_withheld` | REPORT-ONLY — every absent cell is written empty |

No generation rule reads any field this amendment moves: the twin
still writes every absent cell as an empty field, so neither count is
an obligation the twin can meet or miss, and each is evidenced by
being named in the generation report beside the two maps that were
already there. That is the same sentence, for the same reason, that
disposes `missing_by_class` and `missing_by_source`.

**WHAT THIS RAISES.**

- A description that names a declared spelling names it exactly, so
  two tables needing opposite readings no longer describe alike. The
  pair that cost a verdict in both directions under A-P3-19 now
  produces two different files.
- A table whose cells literally read `(withheld)` or `(blank)` is
  describable, and the description says which of the two it means.
- The whole of the `--keep-value` side of the reading rule is
  recoverable from the settings block.
- `validation.declared_spellings` brings back a key that holds a
  character the display boundary shows, and a key that reads as one of
  this package's own class words. Both exclusions existed because
  version 4's map could not be read as exact; version 5's can, and
  keeping them would have walked past a spelling the table wore.

**WHAT THIS LOWERS.** Nothing beyond A-P3-27's own priced lowering of
the Phase 1 settings-block rule, which is now in force rather than
specified: the settings block names which members of this package's
thirteen published words were typed, in the member's own spelling,
written identically whether or not the word occurs, and it still
carries no spelling of the person's own. Three tests state that at its
size rather than by assertion of good intent —
`tests/test_p1r7f2_disclosure_is_true.py` checks that a word which is
nobody's but the person's is written nowhere, that the member and not
the typed form is what travels, and that a named word absent from the
table is recorded exactly as one every cell wears.

**AND ONE GUARD REACHES ONE FIELD LESS, on the contract's own
instruction (contract 5 C5-S13, C5-N5).** The pooled-remainder walk of
A-P3-22 finds a held-back count by the WORD it stands under, which was
sound while every mapping carrying that word drew its other keys from
a first-party vocabulary. `missing_by_source` no longer does, so the
walk skips that one mapping and finds the remainder that used to live
there by its own name, `n_missing_withheld`, instead. The reach is the
same: both halves — the publication guard that decides what may be
written, and the loader's invariant that decides what may be read —
refuse a pooled count at a floor of one, and
`tests/test_p3v5f1_floor_one.py` proves it over every position of a
description that moves between the two floors.

**A-P3-27'S OWN CLOSING SENTENCE IS AMENDED HERE, because it is now
false.** That amendment ends by naming the wire version the shipped
producer wrote and the shipped loader read while its own
implementation stages were still outstanding, and by forbidding any
sentence anywhere to say otherwise. The producer and the loader stage
has landed. The sentence is replaced by this one: **the shipped
producer writes version 5 and the shipped loader reads version 5, and
no sentence anywhere may say otherwise.** The stages A-P3-27 names
that have NOT landed are named here so the difference is readable.
**(A-P3-30 describes the struck sentence rather than quoting it, for
the reason `tests/test_claim_inventory.py` gives about every ban in
that file: a quotation of a retired claim is a retired claim, and an
exception list for the paragraph that retires it is how the ban
rots.)**

- `docs/spec/generation-method-v1.md` is NOT amended, and needs no
  amendment: no generation rule reads any field this amendment moves.
- `docs/spec/validation-method-v1.md` IS amended here, in one clause
  and by counted re-seal, and the reason is that this stage changed the
  validator rather than only the producer.
  `validation.declared_spellings` stopped applying two exclusions that
  version 4's format forced on it, so the document that fixes what that
  function does had to say so or stop being true. The clause is
  **V2.3-A3**, it says THIS RAISES, and what it raises is measured:
  the seven obligations A-P3-19 recorded as a residual are checked and
  held, and the file that PASSED against another table's description
  with a census of zero missed now misses the seven it always owed.
- **AND V2.3-A3 STATES ONE LIMIT OF THIS STAGE RATHER THAN CLOSING
  IT.** The validator's head count still asks its question of the KEPT
  side in the version 4 way: it counts how many `--keep-value` words
  come back through the published routes and does not read the two
  vocabulary lists the settings block now carries. So a description
  that records a rescued word still moves that column's cell-counted
  obligations to NOT CHECKABLE, on a description whose reading rule
  version 5 does record. That over-fires in the safe direction A-P3-26
  chose deliberately -- obligations become not-checkable on a file that
  would have passed -- and closing it means rewriting the validator's
  reconstruction of the settings, which is the validator stage's work
  and not this one's. It is a stated limit until that stage lands.
  **(AMENDED by A-P3-29: that stage has landed and the limit is
  closed.)**

**How to reverse this.** `REINSTATE=A-P3-28` is not a variable, for
the reason A-P3-27 gives: reversing a wire version is a second wire
version, not a switch. What reversal means here is the specific
revert of this commit — `profile.PROFILE_VERSION` and
`contract.PROFILE_VERSION` back to 4, the two counts and the two
vocabulary lists removed from the producer, the loader, the publication
guard and the reference vectors, and the goldens regenerated — and it
costs a changelog entry saying that every description written in
between must be made again. That is exactly the price the owner took
this change now to avoid paying later.

**Amendment A-P3-29 — the validator rebuilds the reading rule from what
version 5 records, and what A-P3-26 put in its place is retired where it
is no longer needed. THIS RAISES what a report checks and lowers
nothing; it corrects A-P3-26's measured table and residual R-P3-8 to
what is now true, and it states one bound that got WIDER** (2026-08-17,
carrying out A-P3-27 on the owner's ruling of the same date; the
validator stage A-P3-28's own closing paragraph names as not yet
landed).

**WHAT LANDED.** `synthtwin validate` rebuilds the reading rule from the
two records contract version 5 added, instead of inferring it from facts
a description publishes for other reasons.

1. **`validation.kept_spellings` reads `settings.kept_values`'s two
   vocabulary lists and consults no column.** The three inferred routes
   of validation method V2.3 — a `kept_by_you` sentinel verdict, a
   published level's label, a level's `variants` keys — are DELETED, not
   kept beside. Contract 5 section 6.4 proves the two lists are the
   whole of what a `--keep-value` can change about any cell's reading; a
   label is a spelling of a cell the producer read as a VALUE, so naming
   it as kept changed nothing, and the routes answered a question about
   levels while the question asked is about the command line.
2. **`validation.declared_spellings` reads
   `settings.declared_missing_values`'s two lists beside its walk over
   `missing_by_source`.** A built-in word named as "no value" moves its
   cells from class `(text-code)` to `(declared-missing)`; a stand-in
   number named as "no value" takes its cells out before the column's
   own sentinel rule judges them. Both were skipped as unrecoverable
   under version 4 and both are answered outright now.
3. **`validation.rescued_spellings` is deleted with the kept-side head
   count it existed for**, and `validation.settings_over_the_split` no
   longer names as kept a built-in marker the description declares as
   missing — because that pair is now reachable, and manufacturing a
   contradiction the person never typed is a refusal the producer would
   raise.
4. **`unrebuildable_columns` is narrowed in four places**, written out
   in validation method clause V2.4-A6: the kept-side head count is
   deleted; the absence-side head count asks only about words of the
   PERSON'S own; the per-column structural test is not asked where the
   publication class empties the source accounting (contract 5 C5-N6);
   and where it is asked, a published key is matched to a recovered
   declaration at `settings.declaration_matching`'s own identity rather
   than by exact key lookup.

**WHAT IT RAISES, MEASURED ON A-P3-26'S OWN WITNESSES AND ITS FOUR
CONTROLS.** Every number was produced by running the shipped code; none
is estimated.

| witness | A-P3-26: checks / moved | now: checks / moved | missed, then and now |
|---|---|---|---|
| rescued word on a numeric column (route 1) | 10 / 43 | **53 / 0** | 0 / 0 |
| rescued word on a label column (route 1) | 10 / 27 | **37 / 0** | 0 / 0 |
| rescued stand-in number (route 1) | 55 / 0 | 55 / 0 | 0 / 0 |
| named stand-in number as "no value" | 10 / 43 | **53 / 0** | 0 / 0 |
| a built-in word named on a free-text column | 10 / 21 | **31 / 0** | 0 / 0 |
| invisible character in a named word (route 2) | 53 / 0 | 53 / 0 | 0 / 0 |
| cell spelling one of this package's class words (route 5) | 53 / 0 | 53 / 0 | 0 / 0 |
| the person's own word on a free-text column (route 4) | 10 / 21 | 10 / 21 | 0 / 0 |
| the person's own words all below the floor (route 3) | 10 / 43 | 10 / 43 | 0 / 0 |
| one word published, one pooled (route 3) | 10 / 43 | 10 / 43 | 0 / 0 |
| a word of the person's own the table never held (over-fire) | 10 / 43 | 10 / 43 | 0 / 0 |
| a named word that comes back cleanly (control) | 53 / 0 | 53 / 0 | 0 / 0 |
| no word named at all (control) | 52 / 0 | 52 / 0 | 0 / 0 |

**The 43-of-53 retreat reverses on five rows of that table and stands on
four, and the four are named.** They are route 3's two — a word of the
person's own that the floor pooled — route 4's one, and the head count's
own over-fire. All four are limits somebody chose: the first three are
groups the format exists to refuse to publish, and the last is the safe
direction of a union that may not walk past a real gap.

**WHAT IT LOWERS.** Nothing. No file loses a check, no verdict that HELD
stops holding, no new withholding appears, no obligation moves onto the
not-checkable census that was not already there, and no cell of any twin
moves. `GOLDEN_TWIN_SHA256` is untouched and no golden was re-recorded.

**AND ONE BOUND THAT GOT WIDER, stated rather than found.** Validation
method V2.4-A4 clause 2 narrowed blankness to "empty, OR wearing a
spelling the description ITSELF publishes as the source of its holes",
and said beside it that nothing of this package's own vocabulary is in
the recovered set. That was true of version 4 and is false now: a word
this package publishes CAN be a recovered declaration, because the
settings block says the person named it. So a generated cell colliding
with that word is counted as a hole where version 4 counted it as data
— residual R-P2-13's own shape, on the one word class it did not
previously reach. It reaches only a word the description declares, never
the built-in table at large; it is the reading the description was
written under; and under version 4 it was not smaller but HIDDEN,
because such a description had that column's cell-counted obligations
moved to NOT CHECKABLE wholesale and no verdict could be wrong where no
verdict was given. The clause is amended in the method document rather
than left standing false.

**WHAT IS CORRECTED IN THE RECORD, because an amendment that claims more
or less than the code does is a defect this repository has now made
three times.**

- **A-P3-26's measured table** is marked amended above: four of its six
  rows no longer describe the shipped tree, and the two that stand are
  route 3's and route 4's.
- **A-P3-26's "wider of the two costs" paragraph** is marked amended
  above: the kept-side half is deleted, and its absence-side half still
  binds.
- **A-P3-28's closing limit** — "the validator's head count still asks
  its question of the KEPT side in the version 4 way" — is marked
  closed above.
- **Residual R-P3-8** is rewritten below to the two routes that remain,
  with its two costs restated at the descriptions they now stand on.
- **Validation method V2.3's three routes** are withdrawn by V2.3-A4,
  **V2.4-A4 clause 3's first entry** is struck as closed, and
  **V2.4-A5's routing** is narrowed by V2.4-A6. The method document is
  amended by counted re-seal, because this stage changed what it fixes.

**ONE DEFECT WAS FOUND AND IS NOT REPAIRED HERE, because it is not this
stage's and repairing it needs its own ruling.** `styles.spelled` asks
every WRITTEN cell of a numeric column to wear one of the six published
forms of its own value, including a cell the description reads as a
HOLE. A table whose declared-missing cells are spelled non-canonically
— sixty readings and twelve cells written `-777.00`, declared with
`--missing-value -777.00` — therefore reports `styles.spelled` MISSED
against its own genuine description. It is present at this plan's own
commit `1179250` and is reachable there by the same witness, so it is
neither introduced nor widened here; what this stage does is stop the
not-checkable routing from masking it on a second class of description,
the one whose declared word is a stand-in number. The repair is a
question about which cells the per-cell style obligation is asked of,
which is validation method V2.4-A3's own subject, and it is recorded
here so that the next round finds it written down rather than by
running into it.

**How to reverse this.** Six variables, each putting back exactly one
thing, and `tests/test_ap329_reading_rule_from_version_5.py` carries all
six: `REINSTATE=A-P3-29-K` infers the kept side again and restores the
kept-side head count; `-D` stops the absence side reading the two
vocabulary lists; `-H` counts every declared word instead of the
person's own; `-S` asks the structural test where the publication class
empties the accounting; `-M` matches a key by exact lookup; `-T` removes
the structural test. `tests/test_p3v4f1_kept_values.py` and
`tests/test_ap326_unrebuildable_reading_rule.py` carry
`REINSTATE=A-P3-29`, which is `-K` under one name, because the class
each of them measures is the kept marker's.

**Amendment A-P3-30 — the sweep after the version bump, and the guard
that makes the next one cheap. THIS RAISES what a guard can see and
what four user-facing pages say; it LOWERS nothing.** Owner ruling of
2026-08-17, carrying out A-P3-27's third stage: A-P3-28 landed the
producer and the loader and A-P3-29 the validator, and this is the
sweep of every surface those two stages left describing version 4, plus
the four sentences the version bump made false without naming a version
at all.

**THE STALE CLAIM THAT MATTERED MOST, and it was in the governing
document itself.** `docs/spec/profile-contract-v5.md` opened by saying
the shipped producer wrote version 4, that the shipped loader read
version 4 and nothing else, and that nothing in it might be written
about anywhere in this repository as though it were built. That
paragraph is correct process — the specification is written before the
code — and it went false on the commit that landed the code. It then
stood for two stages while `CHANGELOG.md`, `SECURITY.md`, this plan and
the shipped product all correctly described version 5, so the one
document an institution's reviewer opens FIRST was the one document
still denying the format it governs. It is replaced by a status
paragraph that says the format shipped and records what the old one
said, in the shape this repository's own ban requires: describing the
retired sentence rather than spelling it.

**WHAT ELSE MOVED, each because a reader acts on it.**

- `docs/spec/generation-method-v1.md` pointed the INDEPENDENT
  implementer it is written for at `profile-contract-v4.md` as the
  profile's wire shape. It now names version 5 and states how version 4
  is carried by reference, so a version 4 section number cited below it
  reads as what it is. No generation rule moves and no twin byte moves;
  A-P3-28's finding that this document needs no RULE amendment stands.
- **The shipped command line carried the retired confidentiality
  claim on both declaration options.** `--keep-value` and
  `--missing-value` each said the profile records how many values you
  named and the rule that matched them, "never the values themselves".
  From contract 5 section 6 that is false: the settings block names
  which of synthtwin's own thirteen published words were typed. This is
  the screen a person reads BEFORE deciding what to type, and it
  contradicted `SECURITY.md`, the profile's own summary page and the
  settings block itself. Both now state the exception where they make
  the claim, and keep the claim contract 5 holds to — a word of the
  person's OWN is never written into the settings.
- **The profiler's summary page contradicted itself on the one run that
  matters.** It said the spellings YOU typed are not written into the
  settings, and eight lines lower told the person who typed `n/a` that
  the description records which of synthtwin's own words they named.
  The opening now names its exception where it is made.
- **The generation report called a blank a spelling.** Contract 5
  section 5 took the blank count out of `missing_by_source`, and the
  report kept printing it under the heading "By the spelling your table
  used", so a column whose absent cells were all empty read `By the
  spelling your table used: 11 cell(s) with nothing written in them`.
  The heading now asks what the table WROTE in those cells, which is a
  question "nothing" is an answer to. `GOLDEN_REPORT_SHA256` moves for
  it; the description and twin digests do not.

**THE GUARD, so that the sixth round does not find this again.**
`tests/test_claim_inventory.py` gains a FIFTH family, built the way its
third family is built: the wire version is read from the product — both
module constants, checked against a description the producer actually
writes — and every surface, plus BOTH governing plans, is held to it.
Only a present-tense claim about what synthtwin itself writes, reads,
emits, produces or accepts is banned; history, the refusal, and a rule
about what an older document means are all permitted, and a test asserts
that they stay permitted so a later widening cannot forbid explaining a
format change. A positive half refuses a repository that satisfies the
ban by silence, and requires the contract that governs the format to be
one of the surfaces stating it.

**WHAT THIS RAISES, MEASURED.** Four false user-facing sentences
removed; one governing document that denied its own subject corrected;
one cross-reference that misdirected the reader this project writes
specifications for; and a guard that turns the suite red on the next
half-applied version bump, on a constant that stops reaching the wire,
and on any surface that names a version synthtwin does not speak.

**WHAT THIS LOWERS.** Nothing. No obligation narrows, no bar moves, no
verdict changes, no check is withdrawn, no count in any report moves,
and `GOLDEN_TWIN_SHA256`, `GOLDEN_DESCRIPTION_SHA256` and
`GOLDEN_QUALITY_SHA256` are untouched. The one golden that moves is the
generation report's, for the one heading above.

**WHAT THIS DOES NOT CLOSE, named rather than left to be found.** Two
results of the sweep are stated and NOT repaired here, because each
needs an owner ruling on a document that fixes its wording:

1. **The migration refusal names two options and the person may have
   used five.** Contract 5 section 10.2 fixes R11's message word for
   word, and it tells the person to describe the table again "giving
   the same --keep-value and --missing-value options you gave the first
   time". A run that also used `--identifier`, `--smallest-group` or
   `--first-row` is not covered, and following the advice literally
   produces a DIFFERENT description of the same table with no warning.
   The repair is a clause in contract 5 section 10.2 widening the named
   options to every option the description's own settings record, and
   it is an amendment to a word-for-word contract clause, which is the
   owner's to take.
2. **A real table whose absent cells hold a stand-in number still
   misses obligations against its own description.** Validation method
   V2.4 rules that on the check side an absence is BLANKNESS, on the
   contract's own rule for twins. Contract 5 section 3.2 way 3 records
   enough to rebuild that reading — `sentinel_verdicts` carries the
   number, the verdict, the reason and the occurrences — and V2.4
   forbids using it. So a 180-row table with twelve cells reading
   `-999`, checked against its own genuine description, reports
   eighteen missed obligations on that column with numbers beside them,
   and A-P3-26's routing does not fire because the description looks
   complete. This behaviour is unchanged by contract version 5 and was
   measured identical at the commit before it, so it is not a
   regression; it is the fifth route of the 2026-08-15 analysis, seen
   from the sentinel side rather than the declaration side, and closing
   it means amending V2.4.

**How to reverse this.** `REINSTATE=A-P3-30` puts the contract's stale
opening paragraph back in memory and reds the version ban;
`-silent` deletes every wire sentence instead of correcting it and reds
the positive half; `-wide` draws the ban without a synthtwin subject
and reds the permitted-sentence test; `-drift` separates the producer's
constant from the version it writes.
`tests/test_claim_inventory.py` carries all four. The four page
corrections reverse by reverting their commit, and
`tests/test_p1r7f2_disclosure_is_true.py` and
`tests/test_p1r7f2_declaration_disclosure.py` hold the two declaration
pages to what they now say.

## P3-D7. Repository claims, staged honestly

**The claim-inventory migration table is a deliverable of this plan's
implementation, and its edits are staged so no sentence is ever ahead
of the code.** Three stages, each moving its surfaces and its pinned
test strings in the same commit as the change that makes the new
sentences true:

1. **At this plan's landing** (with the visibility flip of owner
   decision 2): the charter's phase ledger — Phase 2 to complete,
   closed by owner decision 2026-08-12 with its review record standing
   as written; Phase 3 to current — and the README status banner to
   Phase 3, with the phase-statement test strings updated. Nothing
   else: the boundary sentence stays (still true), the front-page
   tags stay planned (still true), the command words stay two (still
   true).
2. **At the validator implementation:** owner decision 6's boundary
   amendment on every surface carrying the old sentence — the charter,
   the README security section, SECURITY.md, the package docstring,
   the command status text and its comment-claims — with the old
   wording joining the banned list; `synthtwin validate` joining the
   command words on all teaching surfaces; the front-page tags moving
   validation from planned to built; the three-artifact handling forms
   becoming whole-run forms on every claim-bearing surface — FIVE files
   rather than four, per amendment A-P3-8 clause 2, because the
   profiler's plain-language summary is a file of the run and was never
   named; the
   new validator and quality-report modules joining the inventory's
   surfaces, claim-bearing and structure-bearing lists; the
   generation report's "Phase 3's work" sentence replaced by the
   teaching sentence.
3. **At the release:** the install section — connected install by
   package name, the air-gapped wheelhouse path gaining the project
   wheel's own digest (closing R3); the not-on-PyPI sentences retired;
   SECURITY.md's release-integrity section moving from planned to a
   dated record with evidence. **The truthful commit boundary is
   stated, because upload is an act no commit can contain — and an
   instruction is as binding as a claim:** the release commit and the
   signed tag carry NO package-name install instruction, because a
   tagged tree is immutable and an install command naming a package
   that upload might fail to secure would send a reader to whatever a
   third party later parks on that name. The tagged tree's install
   text says a release is being prepared and points at the release
   record. The package-name install instruction, together with the
   project wheel's own digest (closing R3), lands ONLY in the
   post-release closure commit, after the post-publish verification
   confirms the artifacts are live and correct — the outline's
   original placement, restored. The bounded cosmetic cost is named:
   the published package page renders the tagged README, so the first
   release's page shows the release-in-progress wording until the
   next release; the release record and the repository carry the
   verified install path from the closure commit onward. A failed or
   abandoned upload leaves nothing to revert — no tree ever carried
   the instruction — and Phase 0's name-loss fallback stands.

**The migration table.** This is the binding enumeration — every
known sentence the phase falsifies, its surface, its stage, its
replacement intent — and it is backed by a catch-all so that
completeness does not rest on the table alone: each stage's retired
forms join the claim inventory's banned lists AT that stage, so a
stale sentence on ANY surface, in the table or not, fails the ban
test the moment its stage lands.

| surface | sentence or region | stage | becomes |
|---|---|---|---|
| CLAUDE.md | "The current phase is Phase 2." and the phase-ledger entries | 1 | Phase 2 complete, closed by owner decision 2026-08-12 with its review record standing as written; Phase 3 current |
| README.md | "Status: early (Phase 2)" banner | 1 | "Status: early (Phase 3)", pinned phase statement updated |
| CHANGELOG.md | — | 1 | gains the plan-landing and flip entries |
| AGENTS.md, CLAUDE.md, README.md, SECURITY.md, CONTRIBUTING.md | every "temporarily private" repository-status sentence and every deferred-because-private control framing | 1, then 1b | stage 1 (the landing commit, immediately before the flip): reworded to name the flip being executed — the repository goes public at this phase's flip, with the controls' state recorded in SECURITY.md's activation record; stage 1b (the activation record, the first pull request after the flip): the private-mode framing replaced by the public-state facts with their API confirmations, so the public tree never asserts it is private and never claims a control before its evidence exists |
| .github/workflows/ci.yml, tools/hooks/install.sh, tools/provenance/check_provenance.py, tools/provenance/guard_runner.py, tools/provenance/fixture-manifest.json | the operational comment-claims written for private mode — that no ruleset blocks a push, that CI is not a mechanically enforced merge barrier, and their siblings | 1, then 1b | the same two-step wording as the row above; and because the claim inventory's surfaces deliberately exclude `.github/` and `tools/`, the stage-1 enforcement for BOTH rows is a dedicated flip-migration test that walks the ENTIRE tracked tree for the retired private-mode forms — the inventory's catch-all cannot see these files, so this test, not that one, is the control |
| docs/plans/phase-1-profiler.md | the sentence that the future validator consumes only the profile | 2 | a dated amendment recorded in the Phase 1 plan itself (the antecedent-plan mechanism of P2-R4-F7): the validator reads the profile AND the twin, per owner decision 6; the Phase 1 plan is a closed phase's plan and does not govern, so it sits outside the claim inventory altogether and the table, not the catch-all, carries this one. The two GOVERNING plans are walked by the withdrawn-defence family since 2026-08-14 (A-P3-17 clause 1) |
| CLAUDE.md | the profiler-only boundary sentence (rules of the road) | 2 | owner decision 6's two-reader sentence; old form joins the banned list |
| CLAUDE.md | outputs list: quality report named as not built, Phase 3 | 2 | quality report listed as built, written by `synthtwin validate` |
| README.md | front-page tags: validation "[planned]"; two built commands | 2 | "[built] `synthtwin validate`"; pinned front-page tags updated |
| README.md | "What works today" two-command walkthrough and options | 2 | three-command walkthrough; validate options documented |
| README.md | generation-report framing: "passes no verdict", "will say so plainly" | 2 | the verdict exists; the quality report says it; sentences updated where they appear |
| README.md | security section's profiler-only import claim | 2 | two-reader claim per owner decision 6 |
| SECURITY.md | phase banner; profiler-only boundary text; three-artifact handling forms | 2 | Phase 3; two-reader text; whole-run forms naming all five files (A-P3-8 clause 2) |
| src/synthtwin/__init__.py | package docstring: two commands, three artifacts | 2 | three commands, all five files of a full run (A-P3-8 clause 2) |
| src/synthtwin/cli.py | status screen; module docstring; the comment-claim that the reader is imported only when `profile` was typed | 2 | three commands; reader imported for `profile` and `validate` only; teaching-chain sentences |
| src/synthtwin/rendering.py | "a fidelity verdict … is Phase 3's work" | 2 | the sentence that teaches the validate command (report bytes change; goldens re-recorded in the same commit) |
| src/synthtwin/summary.py | the what-generate-will-do paragraph | 2 | extends the teaching chain to validate |
| src/synthtwin/errors.py | two-command artifact-word framing around the transaction messages | 2 | third artifact-word set; wording covers the quality report |
| src/synthtwin/writing.py | module docstring bounded to the two-file transaction | 2 | covers the generalized one-target form |
| docs/spec/generation-method-v1.md | "Fidelity measurement and the quality report are Phase 3." | 2 | names the shipped validator; a sealed-document amendment under counted re-seal |
| tests/test_claim_inventory.py | SURFACES, CLAIM_BEARING, STRUCTURE_BEARING, COMMAND_WORDS, artifact forms, front-page tags, phase statements | 1 and 2 | each pinned string moves in the same commit as the sentence it pins |
| README.md | "not on PyPI" (banner and install section); clone-based install | 3 — the post-release closure commit, after post-publish verification, never the tagged tree | package-name install plus the digest-bearing wheelhouse path |
| SECURITY.md | release-integrity [planned]; release-tooling "none" inventory row; deferred-controls list | 3 (inventory row and tooling lock BEFORE the release runs) | dated records with evidence; the tooling inventory entry; the activation record from P3-D8.0 |
| CHANGELOG.md | `[Unreleased]` | 3 | `[0.1.0]` with the date |

A tree-walking test carries this table: each row names its stage, and
the test asserts, per landed stage, that the row's old form is gone,
its new form is present, and its pinned string (where one exists)
matches — so a stale sentence and its stage cannot drift apart, and
the stage-keyed bans catch what no row anticipated. The test's
positive and negative patterns are stated per stage and scoped so
that historical audit text — changelog entries, review records, and
the test's own fixtures — cannot self-match a retired form it is
quoting rather than asserting.

## P3-D8. The public flip, the defect repairs, and the release

### P3-D8.0 The visibility flip (owner decision 2)

Executed immediately after this plan lands on the default branch.
**Before the flip, the pre-public battery Phase 0 requires for first
public exposure runs and must be clean, with results recorded:** the
ordinary decontamination scan over the final tracked tree AND its
paths at the flip commit — content clean is not path clean, and both
are required; the maintainer-private scanner coverage run with its
attestation-bound result; the all-objects history scan over every
object in the repository — reachable AND unreachable, not the tracked
tree — so a blob an old commit held and a later commit deleted cannot
go public unscanned; and the provenance and offline scans re-run at
the flip commit. **The whole run is recorded in a signed note whose
digest is attestation-bound**, exactly as Phase 0 specifies — a scan
whose record cannot be verified later is not a control. Only on clean,
recorded results does the flip proceed, per SECURITY.md's own
procedure: the repository becomes public; the eight deferred
controls and fork-pull-request run approval are applied and each
confirmed through the API at the moment of the flip; the
active-control list is re-verified at that same moment; the two
owner-personal attestations are re-checked by the owner; and the
evidence lands in SECURITY.md's activation record as the first
pull request under the newly active rules. From that moment: pull
requests only, the aggregate gate required, self-merge only after
green, tag rules active.

### P3-D8.1 The OPEN-defect repairs (owner decision 1)

The first implementation work of the phase, before the validation
specification is written, because both repairs can move generator
bytes and the validator's golden fixtures should be built once:

- **The pooled-style remainder** (P2-C5-F3 residue). The conflict is
  mechanical: contract 7.5.7 writes every pooled cell `plain`, and a
  published non-whole endpoint is a cell that CANNOT be plain, so the
  plain-plus-remainder recount comes up short by that cell. **The
  repair this plan ratifies is a deterministic split of the
  remainder by spellability**, landed as amendments to the governing
  sentences that state the rule (contract 7.5.7's twin-side pooled-
  cell sentence, method G6.4), each under a counted re-seal. **The
  complete allocation rule:** the generator assigns the published
  style counts first, giving non-whole values first claim on the
  styles that can spell them; every remaining pooled cell is then
  written by its value alone — a whole value plain, a non-whole value
  in its value's canonical text (fixed-point or exponent exactly as
  the canonical number grammar decides, deterministic per value).
  **The complete independent recount identity**, computable from the
  written cells and the published map with no generator bookkeeping —
  writing recount(s) for the cells counted in style s, p(s) for the
  published count, R for the published pool, and NW for the written
  cells whose VALUE HAS NO POINT-FREE SPELLING — corrected from
  "non-whole parsed values" on 2026-08-12 (review item P3-C2-F1) and
  flagged for the owner as a wording measurement disproves rather than
  a decision an implementer took: a whole value outside the fixed-point
  window, such as one of size ten to the twentieth, is whole and still
  has no point-free spelling the method may write, so "non-whole" would
  let the identity demand a plain cell that cannot exist. Spellability
  is the property the arithmetic needs, and it is equally beyond the
  writer's choice:
  - recount(leading_zero) == p(leading_zero) and
    recount(leading_plus) == p(leading_plus) — the pool never uses
    the invention family;
  - recount(exponent_upper) == p(exponent_upper) — canonical text is
    never upper-case;
  - **every named style keeps its own floor**: recount(plain) ≥
    p(plain), recount(decimal) ≥ p(decimal), recount(exponent_lower)
    ≥ p(exponent_lower) — so a written column can never SUBSTITUTE
    one published style for another and still balance the totals,
    which an aggregate-only identity would have allowed (round 3
    demonstrated the substitution arithmetically);
  - the non-plain excess D := (recount(decimal) − p(decimal)) +
    (recount(exponent_lower) − p(exponent_lower)) must equal
    max(0, NW − p(decimal) − p(exponent_lower) − p(exponent_upper))
    — exactly the non-whole cells the published counts cannot cover,
    no more and no fewer;
  - recount(plain) − p(plain) == R − D, closing the map exactly;
  - **and the pool's split between the two canonical forms is
    enforced per cell, not assumed**: for each of `decimal` and
    `exponent_lower`, the number of cells written in that style whose
    spelling is NOT the canonical text of their own parsed value must
    be at most that style's published count — the published counts
    are the only license for a non-canonical non-whole spelling, so
    every pooled cell must carry exactly its value's canonical text,
    which the validator computes per cell from the value alone.
    Round 4 showed the aggregate equations without this line let a
    withheld pool be re-spelled wholesale into the wrong canonical
    form; with it, that column fails on every re-spelled cell.
  The identity is therefore independent end to end: floors, totals,
  and the canonical split, each computable from the written cells and
  the published map with no generator bookkeeping.
  Nothing in the profile changes. **The superseded sentence is
  superseded everywhere:** the recount obligation P3-D2 states for
  numeric styles IS this identity from the repair onward — the old
  all-remainder-to-plain form survives nowhere in any governing text
  once the amendment lands. The producer battery that measured 8 of
  240 columns filing the shortfall line must measure zero; the OPEN
  line is deleted. This paragraph is the owner's ratified mechanism,
  so the repair cannot drift into a quieter sentence.
- **The identifier whole-number corner** (P2-C5-F4 residue): the
  length-end and band packing is corrected to allocate jointly, as the
  free-text packer does; for the two-character corner where the only
  whole-number spellings begin with a character the formula-context
  policy bars, the amendment records the resolution under owner
  decision 1 — met exactly where a spelling exists, and the NAMED
  refusal reserved for descriptions no rule can satisfy where the two
  ratified bars genuinely exclude each other; the batteries prove the
  outcome and the OPEN line is deleted.

Each repair is code plus its amendment under a counted re-seal; any
twin-byte change at a fixed seed is a changelogged regeneration event
under D12 with goldens re-recorded in the same commit.

**What the repairs found, recorded here because it is new and needs the
owner** (2026-08-12, during the repair itself). Withdrawing the
two-character code family from the whole-number path showed the SAME
family one path over: `_number_at` writes `-0` through `-9` for a
two-character code-alphabet value that reads as a number on a column
whose values are NOT all whole numbers. That is the same breach of
G9.1 — an invented value opening with the character a spreadsheet reads
as the start of a formula — and it was introduced deliberately by review
item P2-C4-F2 to reach a two-character code-alphabet count, which is a
ratified rule traded for a published count.

It is **not** the defect owner decision 1 settled, and its two possible
outcomes are the owner's, not the implementer's, so it is flagged here
rather than fixed quietly or left unsaid. **Measured** over the
200-description producer battery of
`tests/test_p2c5f2_identifier_classes.py`, withdrawing the family from
that path too leaves 195 descriptions writing every count exactly, 3
meeting the fifth refusal, and 2 missing `n_all_digits` — and takes
every sign-leading invented cell to zero. The 2 are genuinely
infeasible once the bar is kept, their own real tables being the proof
that a table exists and G9.1 the only thing stopping the twin from
writing one, which is exactly the shape owner decision 1 settled by
refusal on the whole-number path. **The owner's choice is therefore the
same pair as before: extend the refusal to this path, or authorize the
miss in this plan.** Meanwhile the bar is asserted on the whole-number
path by name
(`test_no_invented_whole_record_number_opens_with_a_formula_character`),
and the breach is stated rather than implied.

**OWNER DECISIONS 9, 10 AND 11, taken 2026-08-13**, settling the three
records this section carried. They are written before the records
themselves so a reader meets the ruling before the history.

9. **An invented record number MAY open with a sign, where the
   published counts leave no other spelling — and it is counted and
   warned about, never quiet.** The owner directed that the twin
   reproduce what the table had rather than refuse. The reasoning is
   the published facts' own: a two-character value that is in the code
   alphabet, is not figures alone, and reads back as a whole number has
   no spelling but a sign in front of a figure, so a description
   carrying those counts PROVES the real column held such values. The
   twin therefore inherits a hazard the table already had instead of
   manufacturing one, which is the distinction G9.1's bar was written
   to draw, and G9.1 is amended to say so rather than being quietly
   crossed.

   **Two things this decision does NOT buy, stated because the owner
   asked for them and they are not available.** There is no way to make
   a spreadsheet stop reading a leading `-` as a formula: ordinary CSV
   quoting is not a mitigation, which Phase 2 established by test and
   this decision does not reopen. And an identifier column publishes no
   value of the table at all, so the twin cannot copy `-3`; it
   reproduces the CHARACTER the counts require, not the values. What
   the person gets instead is the truth: the formula paragraph counts
   these cells and names their columns every run.

   **The fifth refusal of method G12 is withdrawn with this decision**,
   by the same amendment procedure that landed it: the descriptions it
   stopped now have an answer, so a refusal there would deny a twin
   over a character the source itself used. **And the report's own
   false sentence is corrected**: its formula paragraph told the reader
   every hazardous cell was a value the description published, which an
   invented one is not. It now names the columns whose cells were
   invented, says why the counts left no other spelling, and points at
   the real table, where the same cells behave the same way.

   **How "no other spelling" is decided, which took three attempts and
   is recorded because two of them were wrong.** The rule is a last
   resort, so something has to decide when the resort is reached. Two
   predicates over the published numbers were tried and both were
   wrong: one permitted a sign on a column with room for three
   characters, which manufactures a hazard the description never
   required; the other refused one on a column whose remaining bands
   genuinely could not carry a short cell, which cost a published count
   the source's own values prove is reachable. **The packing decides
   it instead**: the class-and-alphabet search runs first with the
   two-character code family CLOSED and reaches for it only when no
   assignment of whole groups meets every published count without it.
   That is what "no other spelling" means, stated as the question the
   packer already answers completely, and it needs no second opinion
   about the arithmetic to disagree with.

10. **A whole number is written without a decimal point, however wide
    it is.** The owner declined to move any cutoff and asked the
    simpler question — why is the `.0` there at all — and the answer is
    that nothing requires it. A `plain` cell owes two things: it must
    read back as the same number, and it must classify as `plain`. The
    full digit expansion of a whole value does both at any width. The
    sixteen-digit limit belongs to the canonical FLOAT spelling of
    section 3.2.1 and was being applied where it does not govern, so a
    column of very wide whole numbers came out as
    `100000000000000000000.0` when the source had written the digits.
    The limit is lifted from the point-free spelling only; the
    canonical grammar itself is untouched. **This changes twin bytes on
    such columns and is a changelogged regeneration event under D12.**

11. **The frozen reference oracle is brought into agreement with the
    shipped code now**, rather than waiting. It implemented the retired
    pooled-plain rule on a branch no frozen case exercised, so its
    independent check was not in force there -- the disagreement was
    real and every vector stayed green. **Done**: the oracle carries
    the pooled cell spelled by its own value and decision 10's
    point-free spelling at any width; a sixth branch case,
    `numeric_pooled_spelling`, reaches both in one column, whose
    published smallest value carries a point and whose largest is a
    whole number wider than the canonical window; and the case carries
    a mutant that puts the sixteen-figure ceiling back and must change
    its cells. The check cannot go quiet on that branch again.

**A SECOND defect the reviews found, also for the owner** (2026-08-12,
review item P3-C2-F1). A producer column whose values are whole but lie
outside the fixed-point window -- twenty cells of ten to the twentieth
beside twenty of twice that, with two fractional ends -- publishes
`{"plain": 40, "(withheld)": 6}`, because the source wrote those values
in figures. The generator writes them with a decimal point instead --
measured, not inferred: forty cells come out as `100000000000000000000.0`
and its neighbours, five as lower-case exponents, and none plainly --
so the recount names TWO misses, a forty-cell plain shortfall and forty
decimal cells spelled in no way their own values' canonical text allows. This is not the pooled-remainder defect and not a
regression: it is the fixed-point window of the method's own canonical
spelling meeting a source that wrote wider numbers plainly, and it has
been there since the generator shipped. It falsified method G6.4's
sentence that no shape a producer writes is left, which is corrected
there rather than left standing.

**The outcomes open to the owner are the same two as for the first**:
widen what the twin may write for a whole value outside the window --
which changes twin bytes and is a changelogged regeneration event under
D12 -- or authorize the misses here and let the report name them, which
is what the twin already does. Neither is an implementer's to take.

**And one control is known broken until it is settled** (review item
P3-C4-F2): the frozen reference oracle under `tools/reference/` still
implements the retired rule that adds the whole remainder to `plain`,
so on this branch it disagrees with the shipped generator. No frozen
case exercises the branch, which is why every vector stayed green
through this repair -- the oracle's independence is real everywhere it
is exercised and absent exactly here. Whichever outcome the owner
takes, the oracle is brought back into agreement and given a case that
covers the branch in the same change; until then the independent check
on pooled spelling is not in force and this sentence is the record of
that.

**The bound decision 9 had is closed** (review item P3-C6-F1,
2026-08-13). The permission to write a sign is the GROUP's, but a
fold-collision PARTNER carries its parent's spelling and reached it
before that gate: a column of eleven `-3`, eleven `-3 ` and eleven
`1e0` wrote twenty-two hazardous cells where eleven would do, because
the partner of `-0` can only be an edge-spaced `-0 `. Every count was
exact; what was wrong was the hazard, doubled for nothing.

The parent is now chosen with the flip in mind: one that can be
case-flipped is taken first, so the collision lands on `0e0` and `0E0`
and the signed group keeps its eleven cells. Both passes keep the
cyclic order the method fixes, so a column whose parents all hold
letters, or none of which do, is laid out exactly as it was -- no
frozen vector moved. The oracle carries the same preference, and the
counterexample is a test.

**The bound decision 9 actually has, stated after two rounds of
narrowing it** (review item P3-C7-F1). A sign is written only where a
group's own length window admits nothing else -- and the collision
placement around it is improved rather than optimal. The parent choice
now avoids a caseless parent WITHIN a family; it cannot move a
collision to a DIFFERENT family, because `_collision_slots` trades only
between groups of equal size and `_partner_of` searches only the family
the packing already gave the slot. A producer column of `-3` twelve
times, `-34023` twice, `8e999` three times and `8E999` twice therefore
writes fourteen hazardous cells where an allocation putting the
collision on the out-of-range pair would write two, with every
published fact preserved either way.

**Nothing published is lost in any of these cases** -- the counts are
exact and the report names the cells -- so what is left is a
minimisation the twin does not perform, not an obligation it breaks.
The report no longer claims the cells were forced; it says synthtwin
reached for that shape to meet a count, and that carrying more of them
than the description forced is a limit of synthtwin written down here.

**That sentence was written before it was true, and it is true now**
(review round 3's standing owner item, closed by amendment A-P3-8
clause 4, 2026-08-14). The claim was withdrawn from one paragraph of
the report and left standing in two other places: the report's own
made-up-cells block still told a reader that the description's counts
"leave no other way to spell a value of that width", eighteen lines
above the paragraph admitting the twin carries more of them than the
counts force, and the generation method still told an INDEPENDENT
implementer that every invented record number opening with such a
character does so because the counts leave no other way to spell it.
Both are now conditional -- where the counts leave no other spelling,
the inference about the real column holds and is stated; where they do
not, the report says so and says it cannot tell the reader which cell
is which. The method carries the counterexample and says plainly that
writing fewer such cells conforms.

**It was designed, measured and NOT TAKEN, on 2026-08-13, and the
reason is worth more than the change would have been.** Three
independent passes -- a mechanism study, a measurement battery and an
adversarial attack on the proposal before any of it was written --
settled it:

- **The obvious forms do nothing.** Preferring a collision slot whose
  FAMILY, or whose own SLOT, can carry a case flip leaves the
  counterexample at fourteen hazardous cells, because the slot's family
  IS flip-capable; what is caseless is the parent it inherits, which is
  the length-pinned carrier. Only a parent-aware rule moves it.
- **The parent-aware rule costs a published fact.** On this project's
  own 200-description battery at four seeds it loses `n_distinct_folded`
  on twelve runs -- while reducing hazardous cells there by ZERO,
  because all five hazard-writing cases in that battery write the
  forced floor and none has a collision to move. A reach guard removes
  most of the loss and one case survives it: a preference concentrates
  collisions on one family, and a family's supply of partners is a
  function of a spelling that does not exist when the order is chosen.
- **The trade is the one this module refuses.** On one producer column
  the rule halves the hazard AND misses the folded count in the same
  run, which `_partner_of`'s own docstring names as the trade never
  made silently.
- **The measured benefit is three columns in twelve hundred.**

So the bound stands as written above, and the door is left where the
information actually is: the packing, `_identifier_families`, is the one
place that can see the group sizes and both margins before any spelling
is chosen, and could prefer an exact packing that does not put the
length-pinned carrier in the same family as a group owing a collision.
That is unmeasured and would need its own review.

**And the study found something larger, which IS an obligation and is
flagged for the owner.** Over a 1,200-column battery of hazard-shaped
producer descriptions, the SHIPPED generator already misses
`n_distinct_folded` on 44 of them -- 3.7 per cent -- and every one is a
description a real producer wrote, so the column's own values are a
conforming assignment and the miss is a fidelity defect rather than
owner decision 6's infeasible corner. `_fold_room`, the pre-generation
check, counts the whole wide alphabet and knows nothing about families,
slots or windows, so it never fires on these. This is not the hazard
question and does not wait on it: it is a published count the twin does
not meet on a shape a producer reaches. **It needed an owner decision on
the same two terms as the others -- repair the fold feasibility, or
authorize the miss -- and it should be measured against the shipped
baseline before anything else in this area is changed.**

**RULED, AND CLOSED BY AMENDMENT A-P3-12** (2026-08-14). The owner ruled
repair. The shipped baseline was measured first and independently, on
this battery and on a second one built for the repair: 44 of 1,200 and
68 of 918 at seed 0, which reproduces the number above. Both are now
nought, at four seeds, with no other published fact moved and not one
byte moved on any column the shipped generator already answered. The
price -- two of the 1,200 columns now write hazardous cells where they
wrote none -- is stated in A-P3-12 clause 4.

**The battery now watches it.** The 800-run identifier battery asserted
eleven published facts and neither the folded count nor the report, so
the change above would have landed green. It asserts both now, shown
green on shipped code first.

**What the oracle does NOT yet carry, said plainly.** The reference
oracle chooses one parent per partner -- `taking % identities` -- while
the shipped code has always walked every parent in turn, so the
preference cannot be expressed there without widening that search. The
widening is almost certainly right, since it is what the shipped code
does, but it makes a fixture in
`tests/test_p2c2f7_oracle_identifier_bands.py` reachable that was
written to be infeasible, and replacing that fixture is work this
change did not do. **The divergence is older than this repair and no
frozen case reaches it**; it is written here so the next person meets
it as a known item rather than as a surprise, and closing it means
widening the oracle's parent walk and giving that test a fixture whose
infeasibility survives the wider search.

### P3-D8.2 Release preconditions (each verified, none assumed)

1. Phase 3 code review record permits release, **and the review
   verdict names the exact commit digest it reviewed; the owner go
   decision names the digest it approves; and the two digests are
   EQUAL**, recorded together in the release record on the default
   branch. Code merged after the reviewed commit is outside the
   permission: releasing it means a new review record and a new owner
   go naming the new digest.
2. Both OPEN lines deleted per P3-D8.1.
3. The flip of P3-D8.0 long active; the control list re-verified
   against the API in release week.
4. **The two ratified per-release decontamination steps:** the
   maintainer-private scanner coverage run with its attestation-bound
   result, and the all-objects history scan — every reachable blob,
   not the tracked tree — both re-run for this release and recorded.
   These are Phase 0's standing per-release obligations, restated so
   the checklist cannot pass on tracked-file scans alone.
5. **The signed-tag demonstration, in a non-publishing namespace:**
   performed with a tag the ruleset covers but the publish trigger
   cannot match — the publish trigger matches exactly
   `v<digits>.<digits>.<digits>` and nothing else; the demonstration
   uses a suffixed tag — showing signed accepted and unsigned, update,
   deletion each rejected, before any publishing tag exists.

### P3-D8.3 The release itself

Per Phase 0 D10 and SECURITY.md — already ratified; this plan adds no
requirement and drops none:

- Trusted Publishing (OIDC, no long-lived tokens) from a tag-triggered
  workflow in a protected release environment; actions pinned by full
  commit SHA; minimal permissions; the workflow file is a sensitive
  path.
- **Publication bound to the reviewed SHA and the gate, not just the
  tag:** before upload the workflow verifies the tag is a signed
  annotated tag; that its target commit EQUALS the single digest the
  release record carries — the one the review verdict names and the
  owner go approves — read from the DEFAULT BRANCH's copy of that
  record, never from the tagged tree; that the commit is reachable
  from the default branch; that the aggregate gate succeeded for
  exactly that SHA; and that tag version, the project version, the
  command's own version output, and the CHANGELOG's top entry agree.
  The protected environment additionally requires the owner's runtime
  approval with the SHA printed on the approval surface. Any mismatch
  stops the release with nothing uploaded.
- **Reproducibility and a substantive SBOM, bound to the uploaded
  bytes:** two builds on distinct runners with no shared caches or
  artifacts, each from a clean checkout of the tag in the pinned
  container, compared digest-for-digest with a hard failure on
  mismatch. One digest record is then carried through the whole chain: the
  upload job consumes exactly one of the two compared artifact sets,
  re-hashes it immediately before upload, and asserts equality with
  the compared digests; the SBOM binds those same artifact digests;
  the release record publishes them; and the post-publish
  verification downloads from PyPI and compares against the SAME
  record. The SBOM is generated from the locked install closure,
  schema-validated, and asserted by test to name exactly the lock's
  pinned packages with their hashes, the build toolchain, and the
  project artifacts by digest — an empty or hollow SBOM is a red
  check, not a filename.
- **PyPI attestations, explicitly** (outline round-4 condition C):
  attestation generation stays enabled on the trusted publish; each
  attestation is bound to the published artifact's digest — the same
  digest the reproduction chain carries — and to the reviewed source
  commit; the attestations are VERIFIED after publication and the
  evidence recorded in the release record. This is Phase 0 D10's own
  separate requirement, carried here so the checklist cannot satisfy
  OIDC, SBOM and hashes while dropping it.
- **Release tooling enters the supply-chain inventory before it
  runs:** every tool the release workflow executes is named in
  SECURITY.md's inventory with its role, pin and trust root — Python
  tools (builder, SBOM generator, twine) installed from a
  hash-pinned, validator-checked lock, the D5 discipline extended to
  release tooling; GitHub Actions pinned by full commit SHA as the
  existing workflow pins them; the two regimes named separately
  because they are different mechanisms. The inventory row saying
  release tooling is none-until-the-first-release is retired by that
  entry, not contradicted by practice.
- Published artifact hashes; the hash-pinned install lock attached as
  a release artifact; the wheel and sdist content allowlist
  re-checked; `twine check --strict`; sensitive-path changes collected
  from git history into the release notes.
- Version 0.1.0 (owner decision 5); CHANGELOG converted; the signing
  key recorded in SECURITY.md — deferred item 8 activates.

### P3-D8.4 Post-release closure

- **R3 CLOSED:** the documented institutional install gains the real
  project-wheel digest, verified in the wheelhouse procedure; the
  README teaches the package-name install for the connected case and
  keeps the hash-verified wheelhouse path for the air-gapped case,
  now with the project wheel's own hash.
- SECURITY.md's release-integrity section moves from planned to a
  dated record with evidence; the post-publish verification result is
  recorded.

What CI can and cannot prove is stated, not blurred: the workflow's
static properties — pins, OIDC, environment, trigger pattern, the
verification steps' presence — are tested in the suite; the release
run's own evidence — both build digests, SBOM content, attestation
verification, API confirmations, post-publish comparison — is
recorded in the release record, and the runbook names each item the
owner sees before and after the upload.

## P3-D9. Testing strategy

The batteries, by name: the red-case battery at subcheck granularity
with vacuity floor, named-subcheck binding and coverage identity; the
green end-to-end and frozen-conflict batteries, zero-row and
headerless forms included; the pairing battery; the corner-classifier
agreement battery over the producer battery and frozen conflict
cases; the G12-refusal battery (refusal, never a verdict); the
disclosure battery over complete quality reports, screen output and
validate-path refusal text with hostile fixtures including the
crafted-profile shape; the fifteen-key settings-consumption test; the
determinism battery — byte-stable report at the D12 scope, golden
quality-report hashes on all CI cells including the minimums job; the
boundary battery extended — generate unchanged and still reader-free,
the validate closure free of generation and randomness, red mutations
at each; the transaction battery re-run against the generalized
one-target writer with the two-input forbidden set; failure-catalog
exact-shape and reachability extensions; the claim-inventory staged
migration per the P3-D7 table with its tree-walking test; the
registry and seal five-document extension tests with the three-way
partition totality assertions; packaging tests — content allowlist,
typed-marker shipped, version agreement between project metadata,
CHANGELOG and the version output; and the release-workflow structural
tests as bounded in P3-D8.3.

## P3-D10. Honest limits of this phase

- A passing quality report means no checkable obligation was missed —
  the within-window, authorized-deviation, withheld and not-checkable
  counts stand beside the pass, never inside it. It is not a
  fitness-for-analysis verdict; it validates nothing about
  relationships, rows, or meaning; it cannot prove a file is
  synthetic.
- EXACT-CONTROL facts are certified only to their CSV-evidencible
  subset; the report says so.
- The corner classifier is written twice from two texts and
  cross-checked; the plan claims agreement-under-test, not formal
  independence.
- The validator will measure whatever CSV it is pointed at; the
  disclosure gate is designed for that, and every file a full run
  leaves behind is real-derived material under the institution's rules
  (five of them, per amendment A-P3-8 clause 2); no formal
  privacy guarantee; the record claim stays qualified (P2-D11) on
  every new surface.
- The disclosure gate governs what ONE report says, to a reader who may
  hold no file. It is not a defence against a person who holds the
  measured file and runs the check repeatedly with descriptions of
  their own, watching which verdicts change; that person can narrow a
  number a single report withholds, and the product says so on its own
  face rather than implying otherwise (owner ruling 2026-08-14,
  amendment A-P3-13).

## P3-D11. Residuals

- **R-P3-1.** The quality report cannot evidence EXACT-CONTROL facts
  from a CSV beyond the header-written subset; bounded and disclosed
  in-report.
- **R-P3-2.** Validation cannot prove provenance of the measured
  file; by design, one sentence in the report.
- **R-P3-3.** Release reproducibility is demonstrated per release,
  not continuously; the two-build comparison is recorded each
  release.
- **R-P3-4.** Sub-floor measured counts are withheld from the report
  by the profiler's own floor discipline, so a MISSED verdict on a
  small group states the direction, not the number.
- **R-P3-5.** Measured magnitudes AND their verdicts are withheld
  wherever the measured file's own classification would not publish
  them, so validating a mismatched file yields deliberately less than
  validating the twin the profile describes.
- **R-P3-7.** The disclosure gate is a rule about one report, not a
  defence against a person who chooses the descriptions. Someone
  holding the measured file can run `validate` against descriptions
  they wrote and narrow a number one report withholds — a sub-floor
  count, the count of non-canonical cells in a named form, or the
  header of a file the producer refuses. Ruled out of scope by the
  owner on 2026-08-14 (amendment A-P3-13) on the ground that such a
  person can read the file; stated on the quality report's own page,
  in `SECURITY.md`, in the validation method's V5-A1 and in the
  validator module's contract, so that nobody has to discover it.
- **R-P3-6.** The disclosure gate classifies declaration-blind with
  the kept set derived from published spellings (owner decision 8):
  exact for twins, proven by the zero-WITHHELD green battery. For
  files that are NOT the twin and carry spellings the original
  profiling declared, the divergence is real and wider than display:
  a spelling the original run removed before role selection is
  retained by the gate, which can change the column's classified
  role, its statistics, and therefore which outcomes print or are
  withheld — in either direction. No spelling is ever printed under
  any classification.
- **R-P3-8.** A description written with `--missing-value` does not
  always record the word, and where it does not, the reading rule
  cannot be rebuilt (amendment A-P3-26, owner ruling 2026-08-16). The
  affected column's cell-counted obligations are NOT CHECKABLE and the
  report says so per obligation, rather than printing a failure it
  cannot support. **REWRITTEN 2026-08-17 to the two routes that
  remain** (amendments A-P3-27, A-P3-28 and A-P3-29). Contract version
  5 records the reading rule and the validator reads it, so this
  residual no longer reaches `--keep-value` at all — the settings block
  carries the whole of that side, and contract 5 section 6.4 is the
  proof — and on the `--missing-value` side it reaches only **a word of
  the PERSON'S OWN**, never one of this package's thirteen published
  words. Two routes are left, both of them contract 5 section 7's, and
  neither is closable by any version of this format: a word of the
  person's own that fewer than `small_cell_floor` cells of every column
  share, which the floor pools unnamed; and a word of the person's own
  on a column whose publication class permits no value of the table,
  where publishing the marker would publish text out of a column that
  exists to publish none. A third case is the union's own over-fire and
  is a chosen safe direction rather than a lost fact: a word named that
  no cell of the table wore. **Two costs stand with what remains and
  neither is closable inside the validator.** A file that really does
  violate one of the moved obligations returns exit code 0 with them
  named, because a not-checkable line is not a failure. And the TWIN of
  such a description carries the same limit as the table — its holes
  are written empty and no marker survives into it, but which
  obligations a run can check is a function of the description and both
  runs share one, so narrowing it from the file would give two reports
  to two files the description cannot tell apart (V5.1). Both costs
  now stand on those three descriptions and on no others: on every
  description whose declared and rescued words are recoverable, the
  twin and the table alike are measured in full.
- **R-P3-9.** The refusal that turns away an older description names
  two of the options a person may have used. Contract 5 section 10.2
  fixes R11's wording word for word and tells the person to describe
  the table again giving the same `--keep-value` and `--missing-value`
  options; a run that also used `--identifier`, `--smallest-group` or
  `--first-row` is not covered, and following the advice literally
  yields a DIFFERENT description of the same table with no warning.
  Found by the A-P3-30 sweep, stated rather than repaired because the
  wording is a contract clause and widening it is an owner amendment.
  Its cost is bounded: the settings block of the description in the
  person's hand records every one of those options, so the fact is
  recoverable — by somebody who knows to look, which is the part the
  message owes and does not pay.
- **R-P3-10.** A real table whose absent cells hold a STAND-IN NUMBER
  misses obligations against its own genuine description. Validation
  method V2.4 rules that on the check side an absence is blankness, on
  the contract's own rule for twins; contract 5 section 3.2 way 3
  records enough to rebuild that reading — `sentinel_verdicts` carries
  the number, the verdict, the reason and the occurrences — and V2.4
  forbids consulting it. Measured on a 180-row table with twelve cells
  reading `-999`: eighteen obligations MISSED on that column against
  its own description, with numbers printed beside them, and A-P3-26's
  routing does not fire because nothing about the description looks
  incomplete. **Not a regression:** the same table at the commit before
  contract version 5 misses the same eighteen. It is the 2026-08-15
  analysis's cause seen from the sentinel side rather than the
  declaration side, it is the one route neither A-P3-26 nor A-P3-27
  reaches, and closing it means amending V2.4 — which is the ruling
  A-P3-30 declined to take on the owner's behalf.
- **Closed here:** R3 (Phase 1), on the first release's evidence.
- **Carried untouched:** R1, R2, R-P2-1 (still owner-flagged), and
  R-P2-2 through R-P2-14 — the ledger runs to FOURTEEN, not twelve,
  because the method's own residual list does (round 4 caught the
  ledger stopping short):
  - **R-P2-13**, the missing-marker collision: a generated numeric
    value can equal a built-in missing marker and re-read as absent
    when the twin is re-profiled. Phase 3 inherits it and does not
    close it — closing it is generator work with its own amendment if
    ever taken. **Its validator bound is NARROWER than this ledger
    first stated, under amendment A-P3-5.** It read "verdicts are
    blankness-based and immune; the disclosure gate can only
    over-withhold in the collision corner". Blankness-based verdicts
    are reportable only where the file's own description names the
    source of every missing cell, because below the publication floor
    the split is a fact that description withholds. So in a column
    whose own description POOLS its missing sources, a conforming twin
    holding such a value is measured as the producer measures it, and
    the collision can cost a MISSED verdict rather than only report
    detail. Where the description names its sources — no missing cells,
    or blanks that reach the floor — the old bound holds exactly.
  - **R-P2-14**, the packing-walk bound: a contract-valid hand-edited
    text profile near the complete-packing search boundary can make
    generation impractically slow; validation of an existing twin is
    unaffected, and the residual carries unchanged.

## Acceptance criteria

1. The artifacts of the sequencing section are ratified in order; the
   governing set is five sealed documents before implementation
   review ends; the phase-close history audit confirms each governing
   document's introducing commit carried its seal.
2. The shipped entry table equals the registry projection in both
   directions, three-way split and predicates included; the red-case
   coverage identity holds at subcheck granularity with each red case
   failing its NAMED subcheck; every battery in P3-D9 exists and
   passes; no executable subcheck without a demonstrated failure, and
   no listing or input-side entry dressed as a check.
3. Producer → generator → validator: zero MISSED and zero WITHHELD on
   the every-role fixture and the zero-row and headerless forms; the
   frozen conflict cases produce exactly the authorized deviations
   this plan fixes, named with their citations in the quality report;
   the corner-classifier agreement battery is green; every
   G12-infeasible profile meets the refusal, never a verdict.
4. The disclosure battery proves the file-classification envelope on
   report, screen and refusal text with hostile fixtures; the
   fifteen-key settings table is consumed exactly; golden report
   hashes verified on every CI cell.
5. The staged claim migration of P3-D7 is fully applied, each stage in
   the same commit as the change making it true, with the
   four-artifact forms, the amended boundary sentence, validate on
   every teaching surface, and retired wordings banned.
6. Both OPEN defects are repaired per P3-D8.1, their lines deleted,
   their batteries green, their amendments sealed.
7. The visibility flip of P3-D8.0 is executed with every control
   applied and API-confirmed, the personal attestations re-checked,
   and the activation record landed.
8. The first release satisfies every Phase 0 D10 and SECURITY.md
   requirement — the per-release decontamination steps, the
   digest-bound reproduction and SBOM, the verified PyPI
   attestations, the reviewed-digest binding, the tool inventory —
   with recorded evidence; R3 closed; post-publish verification
   recorded.
9. Every artifact scans clean as a tracked file; the seal is current;
   CI green on every cell including Windows.

## Review protocol for this phase

Plan and specification reviews before the artifacts they anchor; code
review against the ratified texts after implementation. Every review
ends with an explicit verdict — ratify, ratify-with-conditions with
each condition bounded and verifiable, or reject with the blocking
items named — and a list of what was checked. Up to five rounds per
artifact, stopping early when remaining items are wording rather than
control gaps.

## Review record

- **Outline reviews (maintainer-private, 2026-08-12):** four rounds on
  the pre-plan outline — three rejections (seventeen, nine and five
  items, all repaired and re-verified) and a fourth-round
  ratify-with-conditions whose three conditions this plan satisfies
  in P3-D2 (identity scheme), P3-D3 (settings table) and P3-D8.3
  (attestations). The outline and its review records are
  maintainer-private working material; this plan is self-contained
  and the public record.
- **Plan reviews (this document):**
  - **Round 1** (2026-08-12) — **REJECT**, eleven items P3-P1-F1 to
    P3-P1-F11, seven blocking. Revision 1 applied repairs for all
    eleven; round 2 verified six closed and re-opened five, repaired
    again in revision 2 below:

    | item | answered in |
    |---|---|
    | P3-P1-F1 the draft tripped the decontamination scan | eight passages reworded; the target scans clean before landing, and the pre-flip battery of P3-D8.0 is the standing control |
    | P3-P1-F2 declaration-blind gate false for kept-value twins | owner decision 8 corrected: the kept set is DERIVED from the profile's published variant spellings; settings table rows updated; the green battery is the executable proof |
    | P3-P1-F3 below-floor named verdicts | P3-D3: the named line states only what omission from the file's own profile publishes — below the floor, possibly zero, count withheld — with the derivation written out and the exact sub-floor number never beside a name |
    | P3-P1-F4 pooled-style repair had no mechanism | non-goal scoped to the WIRE; P3-D8.1 ratifies the deterministic remainder-by-spellability rule, landed as counted-re-seal amendments to contract 7.5.7 and method G6.4 |
    | P3-P1-F5 flip omitted the pre-public history scan | P3-D8.0: the full pre-public battery — private coverage run, all-objects scan over reachable and unreachable objects, provenance and offline scans — runs clean before the flip |
    | P3-P1-F6 totality contradicted the STRUCTURAL split | P3-D2: totality is over OBLIGATIONS, one entry each; a fact may contribute several kinds; the zero-row predicate split into its two byte forms |
    | P3-P1-F7 migration table deferred out of the plan | P3-D7 carries the binding table plus the stage-keyed ban catch-all |
    | P3-P1-F8 the PyPI claim had no truthful boundary | P3-D7 stage 3: imperative install text; existence stated only post-verification; failed upload reverts |
    | P3-P1-F9 R-P3-6 understated divergence | residual rewritten: role and statistics can shift, not merely displayed counts |
    | P3-P1-F10 two settings keys mis-described | the table now calls both advisory-remark thresholds that route no role |
    | P3-P1-F11 metadata check weakened | `twine check --strict`, verbatim |

  - **Round 2** (2026-08-12) — **REJECT**, five items P3-P2-F1 to
    P3-P2-F5, four blocking. It verified six round-1 repairs closed
    (F1, F3, F6, F9, F10, F11) and re-opened five. Revision 2 applies
    these repairs, **verification pending**:

    | item | repair applied in revision 2 |
    |---|---|
    | P3-P2-F1 kept set incomplete; silent change to a ratified decision | owner amendment taken 2026-08-12: the kept set derives from ALL published data spellings — variants keys and kept sentinel-verdict candidates; decision 8 and the settings table carry the amendment |
    | P3-P2-F2 style repair not deterministic; P3-D2 contradiction | P3-D8.1 states the complete allocation rule and the four-line independent recount identity; P3-D2 now cites the amended identity; the superseded sentence survives nowhere |
    | P3-P2-F3 pre-flip battery weaker than Phase 0 | tracked-tree AND path scan added; the run recorded in a signed, attestation-bound note |
    | P3-P2-F4 private-mode claims would go public | migration table gains the five repository-status surfaces at stage 1 with flip-in-progress wording and a stage 1b activation record, plus the Phase 1 plan's validator sentence as a dated antecedent amendment |
    | P3-P2-F5 unsafe package-name instruction in the tagged tree | the tagged tree never carries the instruction; it lands only in the post-release closure commit after verification, the outline's original placement restored; the package-page cost named |

  - **Round 3** (2026-08-12) — **REJECT**, three items P3-P3-F1 to
    P3-P3-F3, all blocking, each a narrowing of a round-2 repair; it
    verified P3-P2-F3 and P3-P2-F5 closed and all three drafter notes
    folded. Revision 3 applies these repairs, **verification
    pending**:

    | item | repair applied in revision 3 |
    |---|---|
    | P3-P3-F1 kept set missed invented withheld variants | the kept set adds every published `levels[].label` matched at the FOLDED identity — the producer's own pooling rule — beside the two exact-spelling fields, with the sentinel predicate named by its exact enum |
    | P3-P3-F2 recount identity permitted style substitution | per-key floors added: plain, decimal and exponent-lower each keep recount ≥ published, with the excess equation pinning the pool — substitution can no longer balance |
    | P3-P3-F3 operational private-mode claims in `.github/` and `tools/` | a migration-table row for the five operational files, enforced by a dedicated whole-tree flip-migration sweep, because the claim inventory's surfaces deliberately exclude those folders |

  - **Round 4** (2026-08-12) — **REJECT**, two blocking items and one
    condition (P3-P4-F1 to P3-P4-F3); it verified P3-P3-F3 closed,
    the two others narrowed, and all round-3 wording notes folded,
    and directed a final abbreviated verification after repair.
    Revision 4 applies these repairs, **verification pending**:

    | item | repair applied in revision 4 |
    |---|---|
    | P3-P4-F1 sub-floor kept numeric markers unreachable by any published field | verdicts decoupled from reconstruction entirely — check-side absence is blankness, the contract's own twin rule, so no gap can move a verdict; the gate's remaining corner is R-P2-13's generator-side collision, named and bounded to conservative over-withholding, with a dedicated fixture pinning it |
    | P3-P4-F2 pooled canonical split unenforced | per-cell canonicality bound added: non-canonical spellings in each canonical style are capped by that style's published count, so every pooled cell must carry its value's canonical text |
    | P3-P4-F3 residual ledger stopped at twelve | carried list runs to R-P2-14; R-P2-13 and R-P2-14 carried explicitly with their Phase 3 interplay stated |

  - **Round 5** (2026-08-12), the final abbreviated verification —
    **RATIFY revision 4.** All three round-4 repairs verified closed
    by replaying the rounds' own executable counterexamples: the
    blankness-based recount returns the correct verdicts on the
    kept-marker twin; the per-cell canonicality bound fails the
    re-spelled withheld pool on every cell; the residual ledger runs
    to R-P2-14. Both drafter notes folded; the target scanned clean
    (1,151 surfaces, zero hits). No review items, no conditions.

  The five plan reviews are in `docs/plans/reviews/` as
  `phase-3-plan-review-round-1.md` through `-round-5.md`.

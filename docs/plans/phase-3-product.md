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
change — `profile_version` stays 4**, the validator consumes v4
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
     alone, with no sentinel or declaration machinery anywhere in the
     verdict path — no reconstruction gap can move a verdict. What
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
  `--out-dir`, and `--replace`. Output: `<stem>-twin-quality.txt`,
  derived by the same suffix construction as the existing pairs and
  collision-free with all four existing artifacts by construction. An
  existing target is refused without `--replace`, in the same shape as
  the generate refusal (R-P2-12 parity).
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
  randomness: no RNG import in the validate closure, asserted by the
  offline scanner's policy (the numpy origin rules stay scoped to
  generation) and a red mutation. Quality-report bytes are a fixed
  function of (profile bytes, measured-file bytes, synthtwin version)
  on one platform under the locked dependency set — the same scope
  D12 gives the twin — with cross-platform agreement verified
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
  `source.header_source`. The remainder is a listing entry with one
  fixed census sentence.
- REPORT-ONLY: listing entries, named and never counted toward a pass.
- LOADER-ONLY and STRUCTURAL: input-side entries as above.

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
    measurement-derived statement, and repeated candidate profiles
    would otherwise binary-search a value the file's own profile
    withholds. Where the gate closes, the subcheck's verdict is
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
  | `declared_missing_values` | EMPTY by owner decision 8 — unrecorded, and genuinely absent from every twin, whose absent cells are written empty |
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
  sentence extends everywhere from three artifacts to four, with the
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
   becoming four-artifact forms on every claim-bearing surface; the
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
| docs/plans/phase-1-profiler.md | the sentence that the future validator consumes only the profile | 2 | a dated amendment recorded in the Phase 1 plan itself (the antecedent-plan mechanism of P2-R4-F7): the validator reads the profile AND the twin, per owner decision 6; plans sit outside the claim-inventory sweep, so the table, not the catch-all, carries this one |
| CLAUDE.md | the profiler-only boundary sentence (rules of the road) | 2 | owner decision 6's two-reader sentence; old form joins the banned list |
| CLAUDE.md | outputs list: quality report named as not built, Phase 3 | 2 | quality report listed as built, written by `synthtwin validate` |
| README.md | front-page tags: validation "[planned]"; two built commands | 2 | "[built] `synthtwin validate`"; pinned front-page tags updated |
| README.md | "What works today" two-command walkthrough and options | 2 | three-command walkthrough; validate options documented |
| README.md | generation-report framing: "passes no verdict", "will say so plainly" | 2 | the verdict exists; the quality report says it; sentences updated where they appear |
| README.md | security section's profiler-only import claim | 2 | two-reader claim per owner decision 6 |
| SECURITY.md | phase banner; profiler-only boundary text; three-artifact handling forms | 2 | Phase 3; two-reader text; four-artifact forms |
| src/synthtwin/__init__.py | package docstring: two commands, three artifacts | 2 | three commands, four artifacts |
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
   invented one is not.

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
    shipped code now**, rather than waiting. It still implements the
    retired pooled-plain rule on a branch no frozen case exercises, so
    its independent check is not in force there; decisions 9 and 10
    settle what it must agree with, and it is updated to that with a
    case that covers the branch, so the disagreement cannot return
    invisibly.

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
  disclosure gate is designed for that, and all four artifacts are
  real-derived material under the institution's rules; no formal
  privacy guarantee; the record claim stays qualified (P2-D11) on
  every new surface.

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
- **Closed here:** R3 (Phase 1), on the first release's evidence.
- **Carried untouched:** R1, R2, R-P2-1 (still owner-flagged), and
  R-P2-2 through R-P2-14 — the ledger runs to FOURTEEN, not twelve,
  because the method's own residual list does (round 4 caught the
  ledger stopping short):
  - **R-P2-13**, the missing-marker collision: a generated numeric
    value can equal a built-in missing marker and re-read as absent
    when the twin is re-profiled. Phase 3 inherits it, bounds its
    validator consequence (verdicts are blankness-based and immune;
    the disclosure gate can only over-withhold in the collision
    corner), and does not close it — closing it is generator work
    with its own amendment if ever taken.
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

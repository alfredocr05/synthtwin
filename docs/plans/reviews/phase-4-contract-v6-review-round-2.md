<!-- Phase 4 contract v6 review, round 2. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-20. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it. -->

# Phase 4 contract v6 review — round 2

## Round-1 verification

| Round-1 item | Status | Evidence |
|---|---|---|
| P4-X1-F1 | **NARROWED** | C6-20 now attempts to replace the fifteen-key settings rule, but cites version 4 §4.3 rather than §4.4, and C6-41 still does not supersede C5-24 or C5-VER: `docs/spec/profile-contract-v6.md:324`, `docs/spec/profile-contract-v6.md:708`; `docs/spec/profile-contract-v4.md:274`; `docs/spec/profile-contract-v5.md:1018`, `docs/spec/profile-contract-v5.md:1063`. |
| P4-X1-F2 | **CLOSED** | Declaration records now have five keys, the three-list identity is C6-K3, C5-16 and C5-K4 are expressly retained, and keep-value precedence reaches every pass: `docs/spec/profile-contract-v6.md:482`, `docs/spec/profile-contract-v6.md:491`, `docs/spec/profile-contract-v6.md:495`, `docs/spec/profile-contract-v6.md:533`. |
| P4-X1-F3 | **CLOSED** | C6-1 conditions no-regression on equal cell readings and C6-2 bounds the missing-vocabulary exception: `docs/spec/profile-contract-v6.md:157`, `docs/spec/profile-contract-v6.md:167`. |
| P4-X1-F4 | **CLOSED** | The cell/core populations now have separate four-count censuses, and imported quantitative rules are directed to the core population: `docs/spec/profile-contract-v6.md:204`, `docs/spec/profile-contract-v6.md:216`, `docs/spec/profile-contract-v6.md:230`. |
| P4-X1-F5 | **NARROWED** | DF-P records the evidence-first winner, but its antecedent does not require both readings to be counted and the mandatory four-count, two-clause remark remains absent: `docs/spec/profile-contract-v6.md:675`; `docs/plans/phase-4-columns.md:882`. |
| P4-X1-F6 | **CLOSED** | C6-34 excludes every judged-pass spelling, including calendar placeholders, and C6-36 gives `--keep-value` precedence: `docs/spec/profile-contract-v6.md:505`, `docs/spec/profile-contract-v6.md:533`. |
| P4-X1-F7 | **CLOSED** | AF3, T5, LT1 and LT2 now bind the recorded thresholds as count invariants: `docs/spec/profile-contract-v6.md:230`, `docs/spec/profile-contract-v6.md:271`, `docs/spec/profile-contract-v6.md:293`, `docs/spec/profile-contract-v6.md:676`. |
| P4-X1-F8 | **CLOSED** | When both clock forms clear, `hh-mm-ss` wins by a fixed rule: `docs/spec/profile-contract-v6.md:259`. |
| P4-X1-F9 | **NARROWED** | The new matrix treats `fraction_widths` as a column key, but C6-27 and §8 still place it inside `numeric_styles`; its canonical key grammar is still absent: `docs/spec/profile-contract-v6.md:399`, `docs/spec/profile-contract-v6.md:587`, `docs/spec/profile-contract-v6.md:642`. |
| P4-X1-F10 | **CLOSED** | Both role and statistical-type counts are thirteen, and §14 repeats the corrected rule order: `docs/spec/profile-contract-v6.md:157`, `docs/spec/profile-contract-v6.md:872`, `docs/spec/profile-contract-v6.md:881`. |
| P4-X1-F11 | **NARROWED** | A full replacement matrix exists, but it conflicts with the fraction-width placement and contains stale clause references: `docs/spec/profile-contract-v6.md:570`. |
| P4-X1-F12 | **NARROWED** | Both required remarks are now required by C6-GRAMMAR, but no exact form identifier, arity or rendering is specified: `docs/spec/profile-contract-v6.md:599`; `docs/plans/phase-4-columns.md:909`. |
| P4-X1-F13 | **CLOSED** | AF-P, T-P, U-P and DF-P explicitly mark the four source-only obligations identified in round 1: `docs/spec/profile-contract-v6.md:658`, `docs/spec/profile-contract-v6.md:672`. |
| P4-X1-F14 | **CLOSED** | The disclosure delta now names the full affixed block, widened calendar endpoints/rungs and `built_in_dates`: `docs/spec/profile-contract-v6.md:769`. |
| P4-X1-F15 | **NARROWED** | A claim-migration table now exists, but it does not transcribe the ratified table completely and names the wrong residual pair: `docs/spec/profile-contract-v6.md:816`; `docs/plans/phase-4-columns.md:1248`. |
| P4-X1-F16 | **CLOSED** | The landing count is corrected to eight: `docs/spec/profile-contract-v6.md:8`; the shipped registry currently contains seven: `tests/dispositions.py:100`. |
| P4-X1-F17 | **NARROWED** | The refusal advice now handles a holder without the table, but its preceding holder-population bound remains false and carried C5-26 still contains the wider assumption: `docs/spec/profile-contract-v6.md:728`; `docs/spec/profile-contract-v5.md:1170`. |

## Numbered review items

1. **P4-X2-F1 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** A document has `profile_version: 6` and exactly seventeen settings keys. C6-20/C6-41 require it, but the carrying rule retains C5-VER and C5-24’s integer 5 because neither is superseded by name. C6-20 also purports to replace version 4 §4.3, while the fifteen-key settings enumeration is actually §4.4. A literal loader therefore rejects every required version 6 document either for its version or for having two extra settings keys.

**EVIDENCE:** Carrying is total except for rules superseded by name at `docs/spec/profile-contract-v6.md:104`; C6-20 and C6-41 are at `docs/spec/profile-contract-v6.md:324` and `docs/spec/profile-contract-v6.md:708`. The live older rules are `docs/spec/profile-contract-v4.md:274`, `docs/spec/profile-contract-v5.md:1018` and `docs/spec/profile-contract-v5.md:1063`. The plan requires exactly seventeen keys and one-version-only loading at `docs/plans/phase-4-columns.md:1193` and `docs/plans/phase-4-columns.md:1235`.

2. **P4-X2-F2 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** A version 6 document carries role `affixed_number` or format `slashed-iso-date`. C6-1/C6-21 require those members, but neither clause names and supersedes the inherited closed `role`, `statistical_type`, `format`, resolution-binding or publication-class rules. Under §2.2’s own discipline, the carried version 4 enumeration still excludes the member. A strict loader must refuse a document the version 6 delta requires.

**EVIDENCE:** The by-name-only carrying rule is `docs/spec/profile-contract-v6.md:104` and `docs/spec/profile-contract-v6.md:111`; the new members are at `docs/spec/profile-contract-v6.md:157`, `docs/spec/profile-contract-v6.md:242`, `docs/spec/profile-contract-v6.md:317` and `docs/spec/profile-contract-v6.md:343`. The carried closed sets and date binding are at `docs/spec/profile-contract-v4.md:974` and `docs/spec/profile-contract-v4.md:2780`. The plan requires all those enumerations to move at `docs/plans/phase-4-columns.md:1153` and `docs/plans/phase-4-columns.md:1164`.

3. **P4-X2-F3 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** A person rescues `1900-01-01` with `--keep-value`. The version 6 record correctly puts it in `built_in_dates`, but carried C5-19 still says `built_in_texts` and `built_in_numbers` record the whole kept-side effect. A consumer following that carried rule ignores the third list and can reconstruct the rescued value as a calendar hole, changing the datetime population and its endpoints.

**EVIDENCE:** C5-19’s two-list completeness claim is at `docs/spec/profile-contract-v5.md:716`. It remains live under `docs/spec/profile-contract-v6.md:104`; version 6 adds `built_in_dates` at `docs/spec/profile-contract-v6.md:482` and makes rescue win at `docs/spec/profile-contract-v6.md:533`, without superseding C5-19. A-P4-1 requires the third list and keep precedence at `docs/plans/phase-4-columns.md:1657`.

4. **P4-X2-F4 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** A loader or disposition registry stores invariant handlers by identifier. The second `AF3` overwrites the parse-line check and the second `AF4` overwrites the core-count sum check—or the reverse, depending on construction order. A block whose pair never clears the parse line or whose core counts do not sum can therefore pass while the implementation still reports that every listed invariant ran.

**EVIDENCE:** The duplicate identifiers are at `docs/spec/profile-contract-v6.md:677` and `docs/spec/profile-contract-v6.md:680`, and at `docs/spec/profile-contract-v6.md:678` and `docs/spec/profile-contract-v6.md:681`. The primary clause assigns the latter rules the distinct identifiers AF6 and AF7 at `docs/spec/profile-contract-v6.md:230`. P4-D7 requires every key’s invariants to be complete and bindable at `docs/plans/phase-4-columns.md:1153`.

5. **P4-X2-F5 — SEVERITY: serious.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** An implementer follows the new matrix’s citations. It reaches C6-24 for `min_length`/`max_length`, but C6-24 is the month-resolution rule; C6-23 for `resolution_mix`, but C6-23 is the joint-ISO reading; and C6-26 for `fraction_widths`, but C6-26 is the unrepresentable-length rule. The migration table likewise claims residuals close through clauses that govern different facts. Registry and migration bindings can therefore attach evidence to the wrong control.

**EVIDENCE:** The stale references are at `docs/spec/profile-contract-v6.md:572`, `docs/spec/profile-contract-v6.md:585`, `docs/spec/profile-contract-v6.md:586`, `docs/spec/profile-contract-v6.md:587`, `docs/spec/profile-contract-v6.md:593` and `docs/spec/profile-contract-v6.md:832`. The actual clauses are C6-23 through C6-27 at `docs/spec/profile-contract-v6.md:363`, `docs/spec/profile-contract-v6.md:370`, `docs/spec/profile-contract-v6.md:375`, `docs/spec/profile-contract-v6.md:389` and `docs/spec/profile-contract-v6.md:399`. The plan’s correct grouping is at `docs/plans/phase-4-columns.md:1164`.

6. **P4-X2-F6 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** A producer nests `fraction_widths` under `numeric_styles`, as C6-27 and §8 require. The carried P1 rule rejects it because every `numeric_styles` value must be an integer and all values must sum to `n_numeric`. If the producer instead writes `fraction_widths` as a column-level sibling, as §7A requires, it violates C6-27 and §8. Even choosing one side leaves width keys such as `2` and `02` indistinguishable in meaning but both permitted by “decimal text”.

**EVIDENCE:** Nested placement is stated at `docs/spec/profile-contract-v6.md:399` and `docs/spec/profile-contract-v6.md:642`; sibling placement is stated at `docs/spec/profile-contract-v6.md:587` and `docs/spec/profile-contract-v6.md:591`. P7 supplies no canonical positive-integer key grammar at `docs/spec/profile-contract-v6.md:689`. The incompatible carried shape and P1 invariant are at `docs/spec/profile-contract-v4.md:1676` and `docs/spec/profile-contract-v4.md:1698`. The plan requires one closed fraction-width fact at `docs/plans/phase-4-columns.md:820` and `docs/plans/phase-4-columns.md:1183`.

7. **P4-X2-F7 — SEVERITY: blocking.**

**SIDE:** Control gap; silent statistical wrongness.

**CONCRETE FAILURE SCENARIO:** With `day_first: true`, ninety-nine ambiguous slashed cells and one month-first-only cell are profiled. A producer counts only the declared reading. DF-P’s antecedent—“where both readings were counted”—is false, so it does not require the evidence winner; the producer may reverse the ninety-nine ambiguous dates and emit no four-count conflict remark. The document still satisfies every stated loader invariant.

**EVIDENCE:** Version 6 records the setting at `docs/spec/profile-contract-v6.md:324`, but DF-P is conditional at `docs/spec/profile-contract-v6.md:675`, and C6-GRAMMAR enumerates only two other new sentences at `docs/spec/profile-contract-v6.md:599`. The plan unconditionally requires both readings to be counted, the strictly larger count to win, and exactly one two-clause remark built from four counts at `docs/plans/phase-4-columns.md:875`.

8. **P4-X2-F8 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** Two producers both emit an affixed-column warning and recoverable-distribution advice, but use different sentence forms and omit different arguments. Both satisfy C6-GRAMMAR’s semantic paraphrase because it fixes no constructor identifier, arity, argument types or exact rendering. A publication guard or loader has no normative form against which either string can be rebuilt or refused.

**EVIDENCE:** C6-GRAMMAR says each sentence “needs a form of its own” but supplies only prose descriptions at `docs/spec/profile-contract-v6.md:601`. The plan requires the note grammar and exact-shape tests to move with the roles at `docs/plans/phase-4-columns.md:514` and requires every remark to be an enumerated grammar form at `docs/plans/phase-4-columns.md:909`. A-P4-3 confirms that this obligation governs profile-document sentences at `docs/plans/phase-4-columns.md:1767`.

9. **P4-X2-F9 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** An `affixed_number` block contains the four required `n_core_*` keys. The disposition registry tries to bind every emitted key, but §8’s exhaustive table lists `n_affixed` and then the quantitative set, omitting the four counts that C6-6 distinguishes from that set. The implementation must either reject required keys or invent their disposition, contradicting the no-exception completeness assertion.

**EVIDENCE:** The four counts are separately required before the quantitative set at `docs/spec/profile-contract-v6.md:204`. They are absent from the table that claims to contain every new and changed key at `docs/spec/profile-contract-v6.md:628`; §11’s completeness assertion is at `docs/spec/profile-contract-v6.md:765`. The plan requires exactly one disposition for every new fact at `docs/plans/phase-4-columns.md:1208`.

10. **P4-X2-F10 — SEVERITY: blocking.**

**SIDE:** Control gap; silent statistical wrongness.

**CONCRETE FAILURE SCENARIO:** A source contains an ordinary endpoint equal to a calendar candidate, but the producer falsely reports it as `read_as_missing` even though the outlier/share rule would retain it. The document’s candidate, reason, count and sum relationships can all be internally valid. A loader lacks the source values needed to recompute the ordinal IQR, yet C6-31 is not marked as a producer obligation among §9’s purportedly complete exceptions. The wrong cell disappears from the published datetime distribution.

**EVIDENCE:** The source-dependent judgment rule is at `docs/spec/profile-contract-v6.md:460`. Section 9 says only four version 6 rules are producer-only and lists none for this pass at `docs/spec/profile-contract-v6.md:658` and `docs/spec/profile-contract-v6.md:672`. A-P4-1 fixes the outlier/share producer rule and its statistical consequence at `docs/plans/phase-4-columns.md:1630` and `docs/plans/phase-4-columns.md:1664`.

11. **P4-X2-F11 — SEVERITY: blocking.**

**SIDE:** Control gap; privacy/disclosure.

**CONCRETE FAILURE SCENARIO:** The same command line names one calendar placeholder while profiling two tables, only one of which contains it. A producer writes the member in `built_in_dates` only for the table containing it. Both documents pass membership, sorting and `n_declared` checks. The settings block now reveals occurrence in the table, although the contract says the list is command-line-only, and the loader cannot detect the violation.

**EVIDENCE:** The command-line-only sentence is at `docs/spec/profile-contract-v6.md:495`, but the new list has no producer invariant in §9 at `docs/spec/profile-contract-v6.md:658`. The carried C5-K5 explicitly covers only the four old lists at `docs/spec/profile-contract-v5.md:786` and `docs/spec/profile-contract-v5.md:1014`. A-P4-1 requires the third list to have the numeric list’s rules at `docs/plans/phase-4-columns.md:1657`.

12. **P4-X2-F12 — SEVERITY: blocking.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** Stage 6 follows C6-MIG exactly. It moves the rows listed there, closes R-P3-12 and leaves R-P2-2 untouched. It also leaves the phase statements, STATUS entry and loud-decline sentences alone because C6-MIG says an unlisted sentence does not move. The implementation then contradicts the ratified migration table while its contract-defined migration battery can still pass.

**EVIDENCE:** The purported complete migration table is `docs/spec/profile-contract-v6.md:816`; it names R-P2-1 and R-P3-12 at `docs/spec/profile-contract-v6.md:832`. The plan instead requires R-P2-1 and R-P2-2, the phase statements, STATUS and loud-decline surfaces at `docs/plans/phase-4-columns.md:1248`. A-P4-1 additionally requires the format/vocabulary-count surfaces at `docs/plans/phase-4-columns.md:1683`, while A-P4-4 fixes when the phase-state surfaces moved at `docs/plans/phase-4-columns.md:1829`.

13. **P4-X2-F13 — SEVERITY: serious.**

**SIDE:** Control gap.

**CONCRETE FAILURE SCENARIO:** One person builds a version 6 description from a source checkout and hands the file to a colleague. The colleague is a holder but did not build it, directly falsifying C6-44’s asserted bound on holders. Moreover, C5-26’s stronger “every description belongs to somebody who made it” sentence remains carried because C6-43/C6-44 never supersede C5-26. The conditional advice is improved, but the normative analysis supporting it is still self-contradictory.

**EVIDENCE:** Transfer to a colleague is expressly permitted at `docs/spec/profile-contract-v6.md:18`; the contrary holder bound is at `docs/spec/profile-contract-v6.md:732`. Total carrying is at `docs/spec/profile-contract-v6.md:104`, while the inherited assumption is `docs/spec/profile-contract-v5.md:1170`. The plan requires the refusal analysis to stop assuming every reader holds the table at `docs/plans/phase-4-columns.md:1235`.

The protocol does not stop early: the remaining items are control gaps, including impossible wire shapes and paths to silent statistical wrongness, not wording-only defects.

## VERDICT

**Reject.** Blocking items: **P4-X2-F1 through P4-X2-F4 and P4-X2-F6 through P4-X2-F12**.

Revision 1 repairs substantial parts of round 1, but it is not yet a carry-correct, total or enforceable version 6 contract. In particular, older closed rules remain live, the fraction-width wire has two incompatible locations, day-first misreading remains conforming, required producer obligations are unbindable, and the migration table omits ratified rows.

## What was checked

- The complete `af2da86..375319a` diff and every round-1 item P4-X1-F1 through P4-X1-F17.
- P4-D3; P4-D4.1 through P4-D4.7; P4-D5; P4-D6.1 through P4-D6.3; P4-D7 items 1–9.
- A-P4-1 items 1–4, including their disclosure and migration pricing; A-P4-2’s cell-settled invention classification; A-P4-3’s profile-document grammar boundary; A-P4-4’s phase-history amendment.
- Carrying and supersession against both `profile-contract-v5.md` and `profile-contract-v4.md`, including C5-9, C5-15, C5-19, C5-24 through C5-28, C5-K3 through C5-K5, C5-S13/C5-S14, the version 4 axes, role, settings, ladder, format, matrix and numeric-style rules.
- Enumeration arithmetic: thirteen roles; thirteen statistical types; eleven formats; four resolutions; six time precisions; two clock forms; six absence classes; twenty-three published-vocabulary members; seventeen settings keys as fifteen inherited plus two.
- Axes totality, publication-class closure, forbidden-key closure, required/forbidden key sets, no-optional-key discipline, invariant identifiers and cross-references.
- Affix cell/core population routing, clock-form tie selection, day-first evidence, widened calendar readings, placeholder judgment, declaration precedence, hole-spelling reproduction, fraction widths and long-tail detection.
- Loader-checkable versus producer-only obligations and whether every new key can bind to `tests/dispositions.py`.
- Disclosure floors, floor-free facts, settings disclosures, disposition changes and every claim-migration row.
- Shipped `contract.py`, `profile.py`, `taxonomy.py`, `parsing.py` and `tests/dispositions.py`. They remain version 5, with ten roles, six date formats, fifteen settings keys and seven governing documents, as expected before stage 6.
- Release state: Phase 3’s owner record says it closed on 2026-08-19 without release at `docs/plans/phase-3-product.md:7480`; `STATUS.md:4` remains `0.1.0.dev0` and unreleased; the checkout has no tags.
- Offline/security boundary: the specification introduces no network, subprocess, native-call, dynamic-loading or profile/generator-boundary route.
- Decontamination: the target specification and review-record directory scanned clean; no digest-prefix concern was reported.
- The worktree remained unchanged. `pytest` was not run.
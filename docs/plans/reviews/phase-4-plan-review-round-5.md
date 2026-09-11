<!-- Phase 4 plan adversarial review, round 5 — the final abbreviated
verification round. Reviewer: codex (gpt-5.6-sol, high effort),
2026-08-19. Paths in this record are repository-relative. Wording was
adjusted only where the repository's vocabulary scanner required it;
no meaning was changed. -->

# Phase 4 plan review — round 5

Reviewer: Codex (GPT-5.6), adversarial reviewer — 2026-08-19.

## Round-4 repair verification

- **P4-P4-F1 — CLOSED.** Replaying the all-absent declared `id` column, the empty rule now settles first and preserves `structural_role: identifier`; declaration dispatch follows only for nonempty columns. This matches the contract and shipped producer. Evidence: `docs/plans/phase-4-columns.md:451-470`; `docs/spec/profile-contract-v4.md:524-541`; `src/synthtwin/taxonomy.py:4572-4581`.

- **P4-P4-F2 — CLOSED.** Replaying 50 `yes` cells and 50 newly recognized error-literal cells, the column’s binary-to-constant transition is now an explicit, bounded reading-layer exception rather than a violation of the no-regression claim. The plan names that exact transition, authorizes only consequences of re-reading the enumerated literals, and requires separate batteries for fixed readings and changed readings, including label narrowing and numeric recovery. Evidence: `docs/plans/phase-4-columns.md:61-86`, `docs/plans/phase-4-columns.md:279-293`, `docs/plans/phase-4-columns.md:1363-1372`, `docs/plans/phase-4-columns.md:1531-1535`. The inherited machinery removes recognized missing text before role selection and derives constant/binary roles from the survivors: `src/synthtwin/taxonomy.py:2687-2727`, `src/synthtwin/taxonomy.py:3713-3759`; version 5 makes the built-in list normative, so the proposed extension is correctly treated as a version event: `docs/spec/profile-contract-v5.md:566-580`.

- **P4-P4-F3 — CLOSED.** Replaying headerless one-of-a-kind prices and clock times, revision 5 supplies positive record-membership tests: the first price must wear the column’s affix pair, and the first clock must use the column’s form. Either condition stops and asks instead of consuming the value as a header. This is the same positive-evidence shape the shipped reader uses for numbers and dates. Evidence: `docs/plans/phase-4-columns.md:495-510`; `src/synthtwin/reading.py:68-84`, `src/synthtwin/reading.py:93-121`, `src/synthtwin/reading.py:136-146`.

- **P4-P4-F4 — CLOSED.** Replaying the 40-label column with one label occurring 11 times, the role now carries exactly the four shared label keys and explicitly excludes `level_ceiling`. B1–B8 remain satisfiable: the 40 folded identities partition between published and suppressed levels, while the exceeded ceiling is evidence text rather than a block key. Evidence: `docs/plans/phase-4-columns.md:886-919`; `docs/spec/profile-contract-v4.md:800-856`. The contradictory categorical-only rule remains confined to categorical columns: `docs/spec/profile-contract-v4.md:893-908`.

- **P4-P4-F5 — CLOSED.** Replaying the distinct affixed-price column, the owner-decision cost now names the whole numeric block, and the disclosure delta groups every newly exposed core fact—moments, sign and zero counts, whole-number status, styles, fraction widths and affixed-cell count—then separately prices the exact endpoints and ladder. The affix pair is floor-governed; the core facts inherit their numeric/ranges treatment; exact endpoints and rungs are expressly floor-free. Evidence: `docs/plans/phase-4-columns.md:227-240`, `docs/plans/phase-4-columns.md:604-616`, `docs/plans/phase-4-columns.md:1162-1183`. This is now a complete delta from the inherited free-text publication doctrine, under which no table value appears in the block: `docs/spec/profile-contract-v4.md:1296-1312`.

- **P4-P4-F6 — CLOSED.** Replaying widths 1, 2 and 2 over values `1.2`, `2.20` and `3.30`, the minimum takes the largest unfilled width it fits, then the maximum does the same, leaving the remaining quota for the interior cell. The former endpoint tie therefore has one answer. The plan requires this order to enter the method amendment rather than remain implementation choice. Evidence: `docs/plans/phase-4-columns.md:782-807`. This matches the governing method’s existing discipline of explicit cell order, largest-remaining quotas and fixed tie order: `docs/spec/generation-method-v1.md:979-1021`; fixed call and word order remain mandatory: `docs/spec/generation-method-v1.md:170-179`, `docs/plans/phase-2-generator.md:723-730`.

- **P4-P4-F7 — CLOSED.** Replaying the clock column with one in-slack unparsed cell, the quality-report clause now requires a per-column sentence stating the uncarryable count, that a conforming twin writes counted stand-ins there, and that the check cannot distinguish those stand-ins from real cells. Acceptance is total over all three invention classes. Evidence: `docs/plans/phase-4-columns.md:415-433`, `docs/plans/phase-4-columns.md:1521-1528`. This is consistent with validation’s total-over-obligations rule and provenance limit: `docs/spec/validation-method-v1.md:1060-1088`, `docs/spec/validation-method-v1.md:1987-1993`.

- **P4-P4-F8 — CLOSED.** Replaying the one-column table with suppressed levels, the screen now reports two disjoint quantities: columns holding only invented values and additional columns holding some invented values. The example therefore reports zero in the first class and one in the second, rather than “0 of 1” as though no invention occurred. Evidence: `docs/plans/phase-4-columns.md:380-414`, `docs/plans/phase-4-columns.md:1521-1527`. Suppressed levels do produce invented neutral labels under the governing method: `docs/spec/generation-method-v1.md:1629-1643`.

- **P4-P4-F9 — CLOSED.** Revision 5 now distinguishes the six inherited datetime formats from the nine-member version 6 vocabulary and fixes all three additions and their resolution bindings. Evidence: `docs/plans/phase-4-columns.md:1115-1130`; the inherited six are enumerated at `docs/spec/profile-contract-v4.md:914-918`.

## Numbered review items

None. No P4-P5 finding is warranted.

## VERDICT

**RATIFY Revision 5.**

All nine round-4 counterexamples now have one controlled outcome consistent with the ratified contract documents, the methods and shipped behavior. No blocking or serious control gap remains, and no condition is needed.

## What was checked

- Canonical reviewer and implementer briefs, revision 5, the four earlier Phase 4 review records, and each operative repair—not merely the review-record table.
- Exact target: 1,673 lines, SHA-256 `f143d9065e67acba725b204ee09026817a36591321a5945b5f7868a7ea8cff33`; repository HEAD `4de1519ef347652116a703eb91b9c6e56fef5d93`.
- Ratified Phase 1–3 conventions and the v4-to-v5 contract relationship: role order, empty/declaration axes, fixed key sets, label invariants, publication classes, normative vocabularies, one-version loading and carry-by-reference.
- Generation and validation methods: endpoint protection, quota and tie ordering, single-stream determinism, regeneration consequences, label invention, report totality, provenance limits and checkability partitions.
- Shipped repair-relevant paths in `taxonomy.py`, `parsing.py`, `reading.py`, `generation.py` and the governing claims affecting validation/report surfaces.
- All nine prescribed attacks: the all-absent declaration; error-literal binary transition; unique headerless prices and clocks; 40-label long tail; affixed-core disclosure; endpoint width tie; clock stand-in sentence; suppressed-level count; and format-vocabulary cardinality.
- Privacy deltas involving long-tail labels, affix fragments, numeric shape facts, endpoints, the rung facts, widths, resolution counts, fraction widths and reproduced hole spellings.
- D12 risks involving allocation ties, sorted assignment, single-stream draw order, seed-invariance scope and changelogged regeneration events.
- Landing mechanics: the draft is present in the exact plan list but not yet in `GOVERNING`; revision 5 requires the governing-list, seal and claim-inventory additions in the ratification commit. The current seal reports current, the three relevant guard assertions passed by direct invocation, and staged whitespace checking passed.
- The tracked-tree decontamination scan completed cleanly.
- No full pytest result is claimed: the read-only environment supplied no writable temporary directory for pytest’s capture machinery.
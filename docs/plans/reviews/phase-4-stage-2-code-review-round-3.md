<!-- Phase 4 stage 2 code review, round 3. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-19. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it.
Verdict: ratify-with-conditions; conditions 1-3 are applied in the
commit that lands this record, condition 4 is the owner's. -->

# Phase 4 stage 2 code review — round 3

## Round-2 verification

- **P4-C2-F1 — NARROWED.** The separate `all_invented` list is the correct split: a fully invented label column may still publish a folded label, so moving it into `without_values` would be false. Declared nonempty columns enter both applicable lists; declared empty columns enter neither; partially invented labels do not enter `all_invented` (`src/synthtwin/summary.py:990-1015`). The repair nevertheless introduced a false explanation and left its rendered integration unguarded; see P4-C3-F1 and P4-C3-F2.
- **P4-C2-F2 — CLOSED.** A-P4-3 and R-P4-14 now state the controls honestly: display safety is not publication authorization, the inventory is not a semantic reader, and screen/summary have no golden (`docs/plans/phase-4-columns.md:1537-1554`, `1768-1794`). The complete screen sentence is pinned at `tests/test_p4d2_loud_decline.py:539-556`.
- **P4-C2-F3 — STILL OPEN.** The Phase 3 owner gate remains unmet; see P4-C3-F3.
- **P4-C2-F4 — CLOSED as a control defect.** The variant-only route now has a direct oracle and an independent producer/loaded-profile comparison (`tests/test_p4d2_loud_decline.py:562-594`, `600-652`). Duplicating the arithmetic is acceptable because the summary receives the producer’s dictionary while rendering receives a loaded typed profile. The agreement test binds those two calculations, though not their connection to rendered summary output; that separate gap is P4-C3-F2.
- **P4-C2-F5 — CLOSED.** The golden comment now names the reworded preamble and no longer calls the report change purely additive (`tests/test_twin_golden.py:497-517`). The description and twin digests remain unchanged while only the report digest moved (`tests/test_twin_golden.py:193-195`, `241-243`, `518-520`); no generation file is in the stage diff, so “no twin byte moved” is true.

## Numbered review items

1. **P4-C3-F1 — SEVERITY: serious (wording-side). The new summary gives a false reason for fully invented variant-only labels.**

   **CONCRETE FAILURE SCENARIO:** At floor 11, profile 22 present rows containing one folded label through eleven case spellings, each used twice. The producer publishes the folded label and its count, with `variants == {}` and a `variants_withheld` multiplicity covering all 22 rows. The summary first lists the column among the real labels present in the profile, then says there is “nothing of yours in this description for it to write.” That reason is false: the folded label is explicitly in the description. The true statement is narrower—the description carries no published source spelling the generator can write, so generation invents every spelling.

   **EVIDENCE:** A-P4-2 expressly defines this route as a published label whose every spelling is withheld (`docs/plans/phase-4-columns.md:1708-1717`). The producer writes `label`, `count`, `variants`, and `variants_withheld` for such a level (`src/synthtwin/taxonomy.py:3115-3125`), and generation invents one variant for each withheld multiplicity (`src/synthtwin/generation.py:4287-4300`). The summary itself acknowledges that the published folded label is something of the table (`src/synthtwin/summary.py:1007-1015`) and lists such columns under real labels (`src/synthtwin/summary.py:1045-1062`), but then prints the contradictory explanation (`src/synthtwin/summary.py:1115-1121`). P4-D2 item 4 requires a true forward statement about the twin, not this broader denial (`docs/plans/phase-4-columns.md:459-463`).

2. **P4-C3-F2 — SEVERITY: serious (control gap). The agreement test does not bind the all-invented calculation to the rendered summary list.**

   **CONCRETE FAILURE SCENARIO:** Delete only the label-specific append at `src/synthtwin/summary.py:1014-1015`. `_all_labels_held_back` remains correct, and the agreement test remains green because it invokes that helper directly. The exact summary test also remains green because its fixture is free text, which enters `all_invented` through the separate role branch. Report and classifier tests are unaffected. The summary once again omits every all-invented label column—the exact P4-C2-F1 failure—while all Stage 2 tests remain green.

   **EVIDENCE:** The helper-to-renderer comparison is direct at `tests/test_p4d2_loud_decline.py:636-652`; it never calls `summary.render`. The only rendered-summary assertion uses a free-text column at `tests/test_p4d2_loud_decline.py:393-415`. The actual label-to-list wiring is at `src/synthtwin/summary.py:1007-1015`. P4-D2 requires the summary statement for fully invented columns and exact-shape coverage (`docs/plans/phase-4-columns.md:459-475`), while A-P4-2 makes all-invented labels members of that class (`docs/plans/phase-4-columns.md:1719-1730`).

3. **P4-C3-F3 — SEVERITY: blocking (owner/process gate). Phase 4 Stage 2 still predates its required Phase 3 closure act.**

   **CONCRETE FAILURE SCENARIO:** Commit `de24b1d` contains Phase 4 behavior and an Unreleased Phase 4 changelog, but the public brief still calls Phase 3 current, the README still labels the project Phase 3, STATUS still says Phase 4 has not started, and the inventory requires those Phase 3 statements. There is no release tag or recorded Phase 3 owner closure. Stage 2 therefore cannot be called ratified, merged, or authority to begin Stage 3 under the current sequencing text.

   This remains an owner action, not an implementer repair. Declining to impersonate the owner was correct.

   **EVIDENCE:** The precondition requires Phase 3 closure before Stage 2 and requires the phase statements to move in Stage 2’s first commit (`docs/plans/phase-4-columns.md:169-175`, `1252-1257`, `1803-1808`). The contradictory state remains at `CLAUDE.md:225-245`, `README.md:3-10`, `STATUS.md:27-34`, and `tests/test_claim_inventory.py:743-749`; Phase 4 release notes already begin at `CHANGELOG.md:9-42`. The brief records that phase closure is an owner act at `CLAUDE.md:235-240`.

4. **P4-C3-F4 — SEVERITY: wording (wording-side). The new mutation record understates which tests fail.**

   **CONCRETE FAILURE SCENARIO:** Delete the `variants_withheld` loop from `_held_back_cells`. The direct variant-only test fails, as recorded, but the producer/renderer agreement test also fails: the summary helper still returns true while `_made_up_class` now returns no invention. A later auditor relying on “this test and nothing else” therefore records the wrong control coverage.

   **EVIDENCE:** The one-test claim is at `tests/test_p4d2_loud_decline.py:571-573`. The second failing dependency is explicit at `tests/test_p4d2_loud_decline.py:617-645`, against the loop at `src/synthtwin/rendering.py:503-510`. This overstates no product guarantee; it is a stale audit sentence only.

## VERDICT

**RATIFY-WITH-CONDITIONS.** The implementation’s classifier, arithmetic, report, screen, boundary, and determinism work are sound. The only blocking condition is the owner’s Phase 3 gate, P4-C3-F3. Conditions:

1. Replace the false summary explanation in P4-C3-F1 with wording true for both publishing-nothing roles and all-spellings-withheld labels.
2. Add one rendered-summary test that proves an all-invented label is named while a partially invented label and a declared empty column are not; this must fail if `src/synthtwin/summary.py:1014-1015` is removed.
3. Correct the mutation statement identified by P4-C3-F4.
4. Before merge, ratification, or Stage 3 authority, the owner must either:
   - supply dated evidence that Phase 3 closure preceded `ec941f6` and resolve the unmet first-commit phase-statement requirement by history or ratified amendment; or
   - ratify an amendment explicitly authorizing and pricing the branch-first history and later closure.
   
   In either case, `CLAUDE.md`, `README.md`, `STATUS.md`, and `PHASE_STATEMENTS` must then state the same true phase status.

Because P4-C3-F2 is a remaining control gap rather than mere wording, the protocol’s wording-only early-stop rule is not yet reached.

## What was checked

- Reviewed the complete `5a5c3f8..de24b1d` stage diff and `1baec05..de24b1d` repair diff.
- Replayed every P4-C2-F1 through P4-C2-F5 scenario.
- Traced `_made_up_class` over declared nonempty and declared-empty columns, free text, `numeric_unrepresentable`, all label roles, datetime, numeric, and empty facts.
- Confirmed constant-below-floor and all-variants-withheld labels become `EVERYTHING`; partially withheld labels become `HELD_BACK`.
- Confirmed `_held_back_cells` uses multiplicity size × number of withheld spellings, matching generation. `occurrence_size(None)` is skipped, but loaded profiles cannot supply such a key because `_multiplicity` rejects nondecimal, zero, and out-of-range keys (`src/synthtwin/contract.py:1918-1952`, `1992-2034`, `3609-3627`).
- Confirmed datetime counts only `n_unparsed`, including when all four universal class counts are nonzero; generation writes exactly those stand-ins (`src/synthtwin/rendering.py:553-573`, `src/synthtwin/generation.py:4037-4100`).
- Confirmed numeric K/O/C/N behavior: K comes from the numeric construction; O, C, and N receive class spellings (`src/synthtwin/generation.py:3380-3454`). Contract X2 partitions `n_present`, and Q3 requires K to be nonzero (`src/synthtwin/contract.py:3123-3138`, `4110-4129`).
- Confirmed report body, report foot, and screen totals share `_made_up_class` and therefore agree on every loaded-profile shape, not only the fixture.
- Confirmed A-P4-3 now legitimately scopes the enumerated grammar to profile-document sentences. The grammar’s shipped scope is explicit at `src/synthtwin/taxonomy.py:480-504`, while report and summary prose already use their own renderers (`src/synthtwin/rendering.py:1204-1232`, `src/synthtwin/summary.py:1170-1183`).
- Confirmed report, summary, and screen output cross `visible_lines`; dynamic column names use the value boundary. `made_up_warning` is public by naming, documented, deterministic, and reached by the CLI (`src/synthtwin/rendering.py:666-689`, `src/synthtwin/cli.py:1293-1301`).
- Ran the offline static scanner read-only: 16 product modules, zero violations. No new regex, network, subprocess, native-call, dynamic-loading, prohibited computed-value method call, import, or forbidden list-growth route was found.
- Ran the decontamination scanner read-only; it was clean, with no digest concern.
- Confirmed Stage 2 does not touch P4-D2 item 3, generation behavior, wire format, or exit code 0.
- Confirmed the golden cause comment and unchanged description/twin digests support the “no twin byte moved” claim.
- Inspected test reachability, exact shapes, mutation statements, shared-classifier agreement, and assertion vacuity.
- Did not run pytest, as instructed.
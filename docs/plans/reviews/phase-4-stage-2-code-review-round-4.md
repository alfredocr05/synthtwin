<!-- Phase 4 stage 2 code review, round 4. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-19. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it.
Verdict: ratify-with-conditions; its one implementation condition is
applied in the commit that lands this record. -->

# Phase 4 stage 2 code review — round 4

## Round-3 condition verification

- **Condition 1 — NOT MET, but narrowed to wording only.** The replacement explanation remains false for the all-spellings-withheld label route; see P4-C4-F1.
- **Condition 2 — MET; P4-C3-F2 is CLOSED.** The rendered-summary test creates an all-invented label, a partially invented label, and a declared empty column, then requires only the first to appear (`tests/test_p4d2_loud_decline.py:660-703`). Removing the label append at `src/synthtwin/summary.py:1014-1015` leaves no route into `all_invented` for that fixture, so the explicit paragraph-presence assertion fails.
- **Condition 3 — MET; P4-C3-F4 is CLOSED.** The mutation record now says that deleting the withheld-variant loop fails both the direct variant-only test and the producer/loaded-profile agreement test (`tests/test_p4d2_loud_decline.py:571-578`).
- **P4-C3-F1 remains open only in its narrowed form below.** The principal warning and membership are now correct; one explanatory clause is not.
- No fresh classifier, arithmetic, reachability, boundary, determinism, or test-control gap was found.

## Numbered review items

1. **P4-C4-F1 — SEVERITY: wording. The summary says below-floor spellings are published, when the contract requires them to be withheld.**

   **CONCRETE FAILURE SCENARIO:** At floor 11, profile 22 present rows containing one folded label written through eleven case variants, each used twice. The folded label and count are published, `variants` is empty, and `variants_withheld` covers all 22 rows. The column correctly enters the summary’s all-invented list, and generation correctly invents all 22 spellings. The summary then says “the spellings it publishes are below the floor.” That is false: a spelling below the floor is precisely one the description does not publish.

   The other clauses survive. Publishing-nothing roles and wholly suppressed labels satisfy the first alternative; the statement that every twin value is invented is true; and the report does repeat the classification. Only the second alternative uses the wrong publication verb.

   **EVIDENCE:** A-P4-2 defines this exact route as a published folded label whose every spelling sits below the floor and is withheld (`docs/plans/phase-4-columns.md:1714-1717`). The producer sends spellings at or above the floor to `variants` and smaller ones to `variants_withheld` (`src/synthtwin/taxonomy.py:3060-3068`); the loader independently enforces the same boundary (`src/synthtwin/contract.py:3583-3611`). Generation invents replacements for the withheld multiplicities (`src/synthtwin/generation.py:4287-4300`). The summary correctly recognizes the column (`src/synthtwin/summary.py:1007-1015`) but prints the contradictory clause at `src/synthtwin/summary.py:1125-1129`.

   The exact-shape test pins that wording without establishing its truth (`tests/test_p4d2_loud_decline.py:409-417`). This survives the claim inventory by design: A-P4-3 says the inventory recognizes enumerated known-bad families, not novel false prose (`docs/plans/phase-4-columns.md:1772-1790`). Thus this is the residual R-P4-14 materializing, not a missing test-reachability control.

## VERDICT

**RATIFY-WITH-CONDITIONS (implementation).** The remaining implementation condition is bounded and wording-only:

1. Replace the clause at `src/synthtwin/summary.py:1127-1128` with wording that says the source spellings were below the floor and therefore withheld—without claiming the description publishes them—and update the exact-shape assertion at `tests/test_p4d2_loud_decline.py:409-417`.

All behavioral and control gaps are closed. This correction does not warrant a fifth adversarial-review round.

### Standing owner condition

The Phase 3 gate remains unmet and is separate from the implementation verdict. The plan requires Phase 3 closure before Stage 2 and requires the phase statements to move in Stage 2’s first commit (`docs/plans/phase-4-columns.md:169-175`, `1252-1257`, `1803-1808`). Current surfaces still say Phase 3 is current and Phase 4 has not started (`CLAUDE.md:225-245`, `README.md:3-10`, `STATUS.md:27-34`, `tests/test_claim_inventory.py:743-749`).

Before merge or Stage 3 authority, the owner must either document qualifying earlier closure and resolve the first-commit requirement, or ratify an amendment authorizing and pricing the branch-first history; the four phase-status surfaces must then agree.

## What was checked

- Reviewed `de24b1d..1f90732` and the complete `5a5c3f8..1f90732` stage.
- Replayed P4-C3-F1, F2, and F4 and verified conditions 1–3 individually.
- Traced every contract-permitted role and axis combination. A declared nonempty column can only be `identifier`; a declared empty column can only be `empty`, while other declared-role combinations are rejected (`src/synthtwin/contract.py:2789-2803`).
- Verified free text, declared identifiers, and `numeric_unrepresentable` enter `EVERYTHING`; an empty column enters no class.
- Verified wholly suppressed and all-variants-withheld labels promote to `EVERYTHING`; partially withheld labels remain `HELD_BACK`.
- Verified `_held_back_cells` computes suppressed rows plus occurrence size multiplied by the number of withheld spellings, matching generation. `occurrence_size(None)` is skipped, but a loaded profile cannot contain such a key because `_multiplicity` rejects it (`src/synthtwin/contract.py:1918-1952`, `1992-2034`, `3609-3627`).
- Verified datetime classification uses only `n_unparsed`, even when all four universal K/O/C/N counts are nonzero, matching the stand-ins written at `src/synthtwin/generation.py:4037-4100`.
- Verified every valid numeric K/O/C/N shape: K is generated numerically, while O, C, and N receive class spellings (`src/synthtwin/generation.py:3380-3454`). X2 partitions `n_present`, and Q3 requires K to be nonzero (`src/synthtwin/contract.py:3123-3138`, `4110-4129`).
- Confirmed the per-column lines, report foot, and screen totals share `_made_up_class`, so their counts agree for every loaded-profile shape.
- Confirmed P4-D2 items 1, 2, 4, and 5 are implemented; item 3 remains untouched as required.
- Confirmed A-P4-3 now scopes the enumerated grammar to profile-document sentences (`docs/plans/phase-4-columns.md:1732-1794`), matching the grammar’s shipped purpose (`src/synthtwin/taxonomy.py:480-504`). Direct report/summary prose is therefore not a current plan deviation.
- Confirmed report, summary, and screen output cross the display boundary (`src/synthtwin/cli.py:288-306`, `962-966`, `1293-1301`).
- Confirmed `made_up_warning` is public, documented, deterministic, and reached by the CLI.
- Inspected all new tests for reachability and vacuity. The two recorded mutation measurements are honest; the remaining formula-condition and exit-code red mechanisms are concrete, and no additional mutation-coverage obligation is stated.
- Confirmed the golden comment names the reworded preamble and affected report areas. The description and twin digests remain unchanged, no generation file moved, and “no twin byte moved” is true (`tests/test_twin_golden.py:193-195`, `241-243`, `481-520`).
- Ran the offline static scanner read-only: 16 product modules, zero violations.
- Ran the decontamination scanner read-only: clean, with no digest concern.
- Confirmed the worktree remained clean.
- Did not run pytest, as instructed.
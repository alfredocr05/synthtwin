<!-- Phase 4 stage 2 code review, round 5 -- the final abbreviated
verification. Reviewer: codex (gpt-5.6-sol, xhigh effort),
2026-08-19. Paths are repository-relative. Wording adjusted only
where the vocabulary scanner required it. Verdict: RATIFY for the
implementation; the owner's Phase 3 gate stands separately. -->

# Phase 4 stage 2 code review — round 5 (final verification)

## Round-4 condition

**CLOSED.**

The complete sentence is now true for every route into `all_invented`:

- Declared identifiers, free text, and `numeric_unrepresentable` publish no values, satisfying the first alternative (`src/synthtwin/summary.py:1002-1004`).
- A wholly suppressed label column has no published level; its suppressed rows cover every present row.
- An all-spellings-withheld label column may publish a folded label, but every source spelling is below the floor. The loader requires published spellings to meet the floor and withheld multiplicities to remain below it (`src/synthtwin/contract.py:3583-3621`).
- `_all_labels_held_back` admits the label routes only when suppressed and withheld-spelling rows cover every present row (`src/synthtwin/summary.py:956-987`), matching the generator’s neutral replacements (`src/synthtwin/generation.py:4287-4324`).
- The report independently reaches the same classification through `_held_back_cells` and `_made_up_class` (`src/synthtwin/rendering.py:493-550`).

The correction is at `src/synthtwin/summary.py:1125-1129`. Its exact-shape assertion moved word-for-word with it at `tests/test_p4d2_loud_decline.py:409-417`.

## Earlier counterexamples replayed

- **P4-C1-F1 — CLOSED.** The one-character identifier counterexample no longer receives an achievement claim. The report says invented cells were “built to meet” published facts and directs the reader to named deviations (`src/synthtwin/rendering.py:598-608`, `1577-1580`).
- **P4-C1-F2 — CLOSED.** The preamble distinguishes published values from synthtwin’s constructions (`src/synthtwin/rendering.py:1530-1540`).
- **P4-C1-F3 / P4-C2-F1 — CLOSED.** Wholly invented label columns are promoted to `EVERYTHING` by cell count and enter the profiler summary’s separate `all_invented` list (`src/synthtwin/rendering.py:513-550`; `src/synthtwin/summary.py:1007-1015`).
- **P4-C2-F4 — CLOSED.** The variant-only path has a direct producer fixture, classifier assertion, generated-report assertion, and producer/loaded-profile agreement check (`tests/test_p4d2_loud_decline.py:564-657`).
- **P4-C3-F2 — CLOSED.** The rendered-summary test requires the wholly invented label to appear while excluding a partially invented label and declared empty column (`tests/test_p4d2_loud_decline.py:660-703`).

None reopened. The correction diff changes only the summary wording, its exact assertion, and the round-4 review record.

## Stage boundaries

The complete `5a5c3f8..d016785` stage:

- changes no machine-readable wire format or specification;
- changes no profiler, taxonomy, contract, or generation rule;
- changes no twin serialization path or twin bytes;
- leaves successful generation returning exit code 0 (`src/synthtwin/cli.py:1348`);
- leaves the description and twin golden digests unchanged; only the human-readable report golden moved.

The offline scanner checked 16 product modules with zero violations. The decontamination scan was clean, with no digest-prefix concern to report. The worktree was clean. Pytest was not run, as instructed.

## Remaining matter

There are **no P4-C5 implementation items**.

The only remaining matter is **P4-C3-F3 — blocking owner/process gate**. Phase 4 implementation was required to begin after the owner settled Phase 3, with phase statements moving in Stage 2’s first commit (`docs/plans/phase-4-columns.md:169-175`, `1252-1257`, `1803-1808`). The public brief, README, STATUS, and claim inventory still retain the Phase 3 state.

The owner must either document qualifying prior closure and resolve the first-commit requirement, or ratify an amendment authorizing the branch-first history; the four phase-status surfaces must then agree. This is a standing owner condition, not an implementation defect.

## Verdict

**RATIFY — IMPLEMENTATION.**

The owner’s Phase 3 gate remains separately blocking before merge, Stage 2 ratification, or Stage 3 authority.
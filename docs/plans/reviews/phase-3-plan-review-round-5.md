<!-- Phase 3 plan adversarial review, round 5. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-12. Paths in this record are
repository-relative; references to the maintainer-private planning
outline name that document without reproducing it. -->

# Phase 3 plan review — round 5

## Numbered review items

None. No P3-P5 finding is warranted.

## Round-4 item verification

- **P3-P4-F1 — verified closed.** Replaying the 204-row counterexample, the two generated `-999` cells are nonblank. The repaired recount therefore produces `n_missing = 0` and `n_present = 204`, matching the profile; the prior erroneous `n_missing = 2` disappears. Declaration reconstruction affects only disclosure, never verdicts. R-P2-13 is conservatively bounded to possible over-withholding and has a dedicated fixture requiring unchanged verdicts and conservative disclosure behavior (phase-3-product.md:206, phase-3-product.md:644).

- **P3-P4-F2 — verified closed.** In the withheld-pool counterexample, all 22 values canonically require fixed-point text but are re-spelled in lower-exponent form. All 22 lower-exponent cells are therefore non-canonical, while `p(exponent_lower) = 0`; the new bound requires `22 ≤ 0`, so the altered file fails. The aggregate equations can no longer conceal the substitution (phase-3-product.md:883).

- **P3-P4-F3 — verified closed.** The carried ledger explicitly runs through R-P2-14. R-P2-13 and R-P2-14 are both individually stated with their Phase 3 consequences (phase-3-product.md:1095).

## Drafter notes

Both round-4 notes are folded:

- Sentinel candidates use the profiler’s declaration-matching identity, explicitly including numeric identity rather than byte comparison (phase-3-product.md:192).
- The whole-tree migration test requires stage-specific positive and negative patterns scoped to prevent historical records and fixtures from self-matching (phase-3-product.md:803).

No remaining drafter note affects ratification.

## Verdict

**RATIFY Revision 4.**

All three authorized repairs pass their own verification, both drafter notes are folded, and the exact current target scans clean.

## Checked surfaces

- Canonical reviewer and implementer briefs.
- Phase 3 plan-review rounds 1–4 and their exact counterexamples.
- Only the Revision 4 passages implementing P3-P4-F1 through P3-P4-F3 and the two folded notes; no broad re-review.
- Exact target: 1,229 lines, SHA-256 `fde6aad2ef311a23e98905556217871e6106c0c16d5252ac7ca985688c2fe1be`.
- Target-only decontamination scan using the repository scanner’s manifest loader, surface decoder, tokenizer, and hash matcher: **1,151 surfaces, zero hits, zero violations**.
- Repository HEAD `038bbb8d17aa680e74ec2e42b54cae418aaa15b8`; target remains untracked. No files modified.
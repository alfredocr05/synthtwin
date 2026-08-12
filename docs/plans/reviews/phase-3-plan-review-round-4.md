<!-- Phase 3 plan adversarial review, round 4. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-12. Paths in this record are
repository-relative; references to the maintainer-private planning
outline name that document without reproducing it. -->

# Phase 3 plan review — round 4

## Numbered review items

1. **P3-P4-F1 — The three-part kept set still misses a published numeric-sentinel route.**  
   **Severity: blocking.**

   **Concrete failure scenario:** I profiled 204 rows containing numeric strings `1`–`200` plus four `-999` values, with `kept_values=("-999",)`, then generated with seed `0`. The source profile correctly remained continuous with zero missing values. Because four occurrences are below the sentinel-publication floor, the profile published no `sentinel_verdicts` entry, while `-999` was still published as the numeric minimum. The three-part kept set was therefore empty. Generation produced two numeric cells equal to `-999`; declaration-blind recount classified both as missing, changing `n_missing` from `0` to `2`.

   Thus, adding `levels.label` closes the Round-3 categorical counterexample, but the claim that the three-part set is sufficient for every possible twin remains false at phase-3-product.md:166, phase-3-product.md:191, and phase-3-product.md:620. The existing method already records this collision route as R-P2-13 at generation-method-v1.md:3174.

   The plan needs a complete twin-domain construction, including sentinel-looking numeric values reachable through published statistics or numeric generation—not merely published sentinel candidates.

2. **P3-P4-F2 — The amended numeric identity still does not enforce the promised canonical split of pooled non-whole styles.**  
   **Severity: blocking.**

   **Concrete failure scenario:** take a valid profile with `numeric_styles={"(withheld)": 22}`, no published named-style counts, and 22 generated non-whole values whose canonical writer form is fixed-point. The correct recount is therefore 22 decimal and zero lower-exponent cells. Re-spell all 22 values in lower-exponent form. The amended checks still pass:

   - every named-style floor is zero;
   - `D = 22 = max(0, 22 - 0 - 0 - 0)`;
   - `r_plain - p_plain = 0 = R - D`.

   Yet the output violates the per-value canonical spelling rule promised at phase-3-product.md:825 and phase-3-product.md:850. The new floors reject the original decimal-to-exponent substitution when decimal has a published floor, but they do not constrain how withheld pooled demand is divided between decimal and lower exponent.

   The validator needs independently derived canonical-form expectations—or an equivalent per-cell canonicality check—for that split. The aggregate excess equation alone is not complete.

3. **P3-P4-F3 — The Phase-3 residual ledger drops two current Phase-2 residuals.**  
   **Severity: moderate; ratification condition.**

   **Concrete failure scenario:** a contract-valid hand-edited free-text profile near the complete-packing search boundary can cause generation to take an impractically long walk, as recorded by R-P2-14 at generation-method-v1.md:3181. A release reader relying on D11 would see only residuals through R-P2-12 at phase-3-product.md:1053 and receive no warning. R-P2-13 is also omitted and is directly shown concretely by P3-P4-F1.

   Carry R-P2-13 and R-P2-14 forward explicitly. R-P2-13 may instead be closed only if the repaired kept-domain mechanism proves that closure.

## Round-3 verification

- **P3-P3-F1 — Partially closed.** The exact categorical counterexample is closed: adding the folded `levels.label` changes its recount from empty with 11 missing cells to constant with zero missing cells. P3-P4-F1 shows a remaining numeric published-data route.

- **P3-P3-F2 — Partially closed.** The original substitution—11 published decimal cells replaced by 11 lower-exponent cells—is now rejected by the decimal floor. P3-P4-F2 shows that pooled withheld demand can still be assigned to the wrong canonical style while satisfying every amended equation.

- **P3-P3-F3 — Closed.** The migration table now explicitly covers `.github/workflows/ci.yml` and the relevant `tools/` files, with a dedicated entire-tracked-tree flip-migration sweep at phase-3-product.md:753.

## Drafter list

- All three bounded Round-3 wording notes are folded:

  - `variants_withheld` is described as a multiplicity map.
  - The exact enum spelling `kept_by_you` is used.
  - Stage 3 is explicitly labeled the post-release-closure commit.

- Replace the sentinel-candidate wording “exact spelling” with the profiler’s declaration-matching identity. Numeric declarations use exact numeric identity, not merely byte-exact or folded string identity. The settings-table reference to profiler declaration matching already points toward the correct mechanism.

- In the eventual whole-tree migration test, state the stage-specific positive and negative patterns precisely so historical audit text and the test’s own fixtures do not create accidental self-matches.

## Verdict

**REJECT Revision 3.**

P3-P4-F1 and P3-P4-F2 are genuine validator/control gaps, not bounded drafting details. P3-P4-F3 is a bounded ratification condition. With the first two mechanisms repaired and the residual ledger corrected, the plan should be suitable for a final abbreviated verification rather than another broad review round.

## Checked surfaces

- Entire current `docs/plans/phase-3-product.md`.
- All three prior Phase-3 plan reviews.
- Ratified Phase-3 outline and all outline-review records.
- Canonical reviewer and implementer briefs.
- Kept-value declaration matching, categorical level/variant publication, sentinel detection and publication floors, and recount behavior.
- Executable replay of the Round-3 categorical counterexample.
- Executable numeric-sentinel generation/recount counterexample.
- Numeric-style parsing grammar, published floors, withheld allocation, canonical output rules, and amended recount equations.
- `.github/`, `tools/`, claim-inventory boundaries, and the proposed whole-tree migration sweep.
- Phase-2 residual ledger, including R-P2-13 and R-P2-14.
- Exact current target scanned with the decontamination scanner’s own surface enumeration, tokenization, and hash matching primitives: **1,086 surfaces, zero hits, zero violations**.
- Repository status and target provenance; no files were modified.
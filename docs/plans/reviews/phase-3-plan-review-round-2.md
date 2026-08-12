<!-- Phase 3 plan adversarial review, round 2. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-12. Paths in this record are
repository-relative; references to the maintainer-private planning
outline name that document without reproducing it. -->

# Phase 3 plan review — round 2

## Numbered review items

1. **P3-P2-F1 — The derived kept set is incomplete and silently changes owner decision H**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Profile a 215-row numeric column containing 15 kept `-999` values and 200 ordinary readings, then generate at seed 7 and validate that twin. The profile publishes the kept number through `sentinel_verdicts`, not label `variants`. The proposed derivation therefore reconstructs an empty kept set. In an in-memory producer → generator → taxonomy recount, the generated twin contained eleven `-999` cells; the proposed gate classified all eleven as missing, changing `n_missing` from 0 to 11 and forcing a `MISSED` on a conforming twin.

   The repository already tests that numeric kept values are published as `sentinel_verdicts` with reason `kept_by_you` (test_p1r6f9_declared_values.py:145). The repaired plan derives only `variants` keys (phase-3-product.md:174, phase-3-product.md:514).

   This is also not the ratified owner decision: outline decision H and round-4 condition A require **no value declarations and empty declaration tuples** (outline:215, round-4.md:15). Any reconstructed-declaration design needs a complete rule and an explicit owner amendment.

2. **P3-P2-F2 — The remainder-by-spellability repair is neither independently deterministic nor reconciled with validation**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Use one of the documented producer profiles whose pooled style remainder includes a non-whole endpoint. The repaired generator writes that endpoint canonically, adding the cell to `decimal` or `exponent_lower`. But P3-D2 still requires every non-`plain` style to equal its published count and adds the entire remainder to `plain`; the validator therefore reports two `MISSED` outcomes on the repaired, conforming twin.

   P3-D8.1 instead says each style receives a “computable share” of the remainder (phase-3-product.md:769), contradicting P3-D2’s retained old rule (phase-3-product.md:383).

   The new mechanism also never defines which value positions consume the anonymous pool or how an independent validator computes that allocation without generator bookkeeping. Deriving the “share” from the finished style recount would be circular and allow arbitrary pool redistribution to certify itself. Contract 7.5.7 and method G6.4 currently specify the old full-to-`plain` allocation exactly (profile-contract-v4.md:1674, generation-method-v1.md:912); their replacement must fix a complete allocation and independent recount rule in the plan.

3. **P3-P2-F3 — The pre-public battery is still weaker than Phase 0**

   **SEVERITY: blocking**

   **Concrete failure scenario:** The plan-landing commit introduces a manifest-matching path component while all blob contents remain clean. The private coverage run tests scanner behavior, the history scan inspects repository objects, and provenance/offline scans pass. Because P3-D8.0 never explicitly runs the ordinary decontamination scanner over the final tracked tree and paths, the bad pathname becomes public.

   Phase 0 separately requires the final tracked tree to scan clean and the full pre-first-public run to be recorded in a signed note whose digest is attestation-bound (phase-0-public-skeleton.md:351, phase-0-public-skeleton.md:524). P3-D8.0 names coverage, all-objects, provenance and offline runs, but omits both the explicit tracked-tree/path scan and signed-note/digest binding (phase-3-product.md:744).

4. **P3-P2-F4 — The migration table leaves the first public tree carrying false private-mode claims**

   **SEVERITY: blocking**

   **Concrete failure scenario:** The plan lands, then the visibility flip executes immediately. The newly public tree still says the repository is private and branch/tag controls are deferred in AGENTS.md, CLAUDE.md, README, SECURITY.md and CONTRIBUTING.md. D7’s stage 1 expressly changes only the phase ledger and README status banner; SECURITY’s deferred-control migration is assigned to stage 3. The catch-all does not fire because these forms have not been retired at stage 1.

   Current contradictory surfaces include AGENTS.md:7, CLAUDE.md:43, README.md:16, SECURITY.md:456 and CONTRIBUTING.md:96. The table also omits Phase 1’s timeless claim that the validator will consume only the profile (phase-1-profiler.md:93); plans are deliberately excluded from the existing claim-inventory sweep.

5. **P3-P2-F5 — The PyPI boundary still leaves a permanent unsafe install instruction**

   **SEVERITY: condition**

   **Concrete failure scenario:** The reviewed release commit and signed tag change README to the imperative package-name install command. The upload then fails because another party claimed the name. A reader of that immutable tagged commit follows the instruction and installs the other party’s package. Reverting the default branch does not remove the signed tag, commit, or historical instruction.

   Phase 0 treats the name as unverified until an authorized upload succeeds (phase-0-public-skeleton.md:33), and the ratified outline puts the README package-name switch in post-release closure (outline:742). Calling the pre-upload text “imperative” rather than an existence claim does not make the instruction safe (phase-3-product.md:687).

## Round-1 repair verification

- **P3-P1-F1 — closed:** exact current-file run through `file_surfaces`, `tokenize`, `_match_hash`, the committed manifest and magic table produced 989 surfaces, zero hits and zero violations.
- **P3-P1-F2 — not closed:** `variants` omits numeric kept sentinels; the executable counterexample changes eleven generated cells from present to missing.
- **P3-P1-F3 — closed:** under an applicable same-role fact class, absence of the submitted identity from the measured file’s own published map derives only “below floor, possibly zero”; the exact count remains hidden.
- **P3-P1-F4 — not closed:** allocation is underspecified and P3-D2 still mandates the superseded all-remainder-to-`plain` recount.
- **P3-P1-F5 — partially closed:** reachable/unreachable history, coverage, provenance and offline runs were added; tracked-tree/path scanning and signed-note attestation binding remain absent.
- **P3-P1-F6 — closed:** totality is now stated over obligations, permits multiple kinds per registry fact, and splits both zero-row byte predicates.
- **P3-P1-F7 — partially closed:** the earlier command/artifact omissions are tabulated, but public/private-state claims are omitted or assigned to the wrong stage, and the Phase 1 boundary claim remains outside table and catch-all.
- **P3-P1-F8 — partially closed:** completed-publication language is delayed, but the pre-upload tagged commit still carries an unsafe package-name instruction.
- **P3-P1-F9 — closed:** R-P3-6 now admits changes to role, statistics and outcomes in either direction.
- **P3-P1-F10 — closed:** both identifier thresholds are correctly described as advisory-only and role-neutral.
- **P3-P1-F11 — closed:** `twine check --strict` is required verbatim.

## For the drafter

- In P3-D3, distinguish the anonymous label-count multiset from the single pooled totals used for numeric styles and offsets.
- Change “No entry of any kind may carry a check that cannot fail” to refer specifically to executable subchecks; listing and input-side entries deliberately carry no verdict check.
- After repair, update the status and closure table without calling an item settled until this review verifies it.

## Verdict

**REJECT.**

Blocking items: **P3-P2-F1 through P3-P2-F4**. P3-P2-F5 is a bounded release condition but does not alter the rejection: the kept-set gate fails on a generated twin, the style repair lacks a coherent independent recount, the first-exposure battery remains weaker than Phase 0, and the visibility-flip migration would publish false operational claims.

## Checked surfaces

- Repository HEAD `038bbb8d17aa680e74ec2e42b54cae418aaa15b8`; sole worktree change is the untracked target; `diff --check` clean.
- Canonical reviewer and implementer briefs; full revision-1 target and Round-1 plan review.
- Ratified revision-4 outline, all four outline-review records, owner decisions and drafting conditions A–C.
- Exact target-only decontamination scan using the scanner’s own decoder, surface producer, tokenizer, manifest parser and n-gram hash matcher.
- Taxonomy declaration matching/removal, numeric-sentinel decisions, label variants, settings serialization, publication classes and role routing.
- In-memory producer → strict typed profile → generator → declaration-derived taxonomy recount for the kept numeric-sentinel counterexample.
- Contract 7.5.7, method G6.4, generation style allocation/recount code, producer-battery residue and registry OPEN entry.
- Registry obligation identities, STRUCTURAL splits, zero-row forms, G12 refusals and three-way totality language.
- Phase 0 decontamination, first-public-exposure, provenance, governance and release requirements; SECURITY active/deferred claims.
- Claim inventory, migration table, operational public surfaces, Phase 1 boundary statement and stage-keyed catch-all.
- Release identity, name-loss posture, tag/commit/upload ordering, R3, attestations, SBOM chain and `twine check --strict`.
- No repository files were modified.
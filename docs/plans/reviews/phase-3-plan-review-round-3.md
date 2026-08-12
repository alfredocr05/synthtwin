<!-- Phase 3 plan adversarial review, round 3. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-12. Paths in this record are
repository-relative; references to the maintainer-private planning
outline name that document without reproducing it. -->

# Phase 3 plan review — round 3

## Numbered review items

1. **P3-P3-F1 — The amended kept set still misses generated label spellings**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Profile an 11-row label column whose eleven distinct source spellings each occur once, all trim and fold to one documented missing-marker identity, with that identity declared kept. The valid profile publishes:

   - one level with count 11;
   - `variants: {}`;
   - `variants_withheld: {"1": 11}`;
   - no sentinel verdict.

   Generation invents eleven variants from `levels.label`. Neither named kept-set field contains them. I executed this producer → typed profile → generator → taxonomy recount: the empty derived set changed `n_missing` from 0 to 11 and the role from `constant` to `empty`; adding the published parent label to the kept set restored the correct recount.

   The plan says there are only two routes at phase-3-product.md:176. Contract v4 expressly permits empty `variants` when all spellings are below the floor at profile-contract-v4.md:1386, while G8 generates withheld variants from the normalized parent label at generation-method-v1.md:1501 and generation.py:4216.

   The kept-set derivation must also cover published parent labels from which generated variants can inherit missing-marker semantics.

2. **P3-P3-F2 — The pooled-style recount identity accepts loss of a published style**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Take a numeric profile with eleven whole values and:

   - `p(decimal) = 11`;
   - every other published style count zero;
   - `R = 0`;
   - `NW = 0`.

   Alter the CSV so the same eleven numeric values use lower-case exponent spellings. Then `recount(decimal)=0` and `recount(exponent_lower)=11`. The proposed equations still pass:

   - `D = (0 + 11) − (11 + 0) = 0`;
   - the required right side is `max(0, 0 − 11) = 0`;
   - the plain, leading, plus, and upper-exponent equations also hold.

   The validator therefore accepts complete substitution of the published decimal style even though contract 7.5.7 requires each named style to be reproduced in its published count (profile-contract-v4.md:1637). The four-line identity aggregates decimal and lower exponent and supplies no per-key lower bound (phase-3-product.md:815).

   The arithmetic closes the total population but is not “two-sided over the whole map.” At minimum, each named decimal/lower-exponent count must remain independently enforceable, with only deterministic canonical pool spill permitted above it.

3. **P3-P3-F3 — The first-public-tree migration still omits known private-mode operational claims**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Stage 1 edits the five tabulated documents and the visibility flip activates the branch ruleset. The first public tree nevertheless still contains current operational text saying that the ruleset is deferred or that CI is not a mechanically enforced merge barrier in:

   - .github/workflows/ci.yml:3;
   - tools/hooks/install.sh:26;
   - tools/provenance/check_provenance.py:53;
   - tools/provenance/guard_runner.py:30;
   - tools/provenance/fixture-manifest.json:2.

   None appears in the binding migration table’s stage-1 row (phase-3-product.md:740). The claimed “ANY surface” catch-all is not presently capable of finding them because `SURFACES` excludes `.github/` and `tools/` (test_claim_inventory.py:112). The table and stage-1 enforcement surface must include these current operational claims before the flip.

## Round-2 repair verification

- **P3-P2-F1 — partially closed:** the amended fields cover the kept numeric-marker counterexample and the owner amendment is explicit, but the `levels.label` → `variants_withheld` generation route remains uncovered.
- **P3-P2-F2 — partially closed:** P3-D2 cites the amended identity and the old rule survives nowhere in this plan, but the identity accepts decimal/lower-exponent substitution and is therefore not an independent exact recount.
- **P3-P2-F3 — closed:** the final tracked-tree content-and-path scan, private coverage run, reachable-and-unreachable object scan, provenance/offline scans, and signed attestation-bound note now match Phase 0’s pre-first-public requirements.
- **P3-P2-F4 — partially closed:** the five named documents and Phase 1 antecedent amendment are covered, but current `.github/` and `tools/` private-mode claims remain outside both the table and catch-all.
- **P3-P2-F5 — closed:** the release commit and signed tag carry no package-name installation instruction; it lands only after successful publication and post-publish verification.

## For the drafter

- Folded: P3-D3 now distinguishes the anonymous label-count list from the single pooled totals for styles and offsets.
- Folded: the vacuity prohibition is correctly scoped to executable subchecks; listing and input-side entries may not be presented as checks.
- Folded: Revision 2’s closure table is explicitly verification-pending, and the introduction says repairs become settled only after review.
- Bounded wording: change P3-D2’s “withheld multiset” to the exact `variants_withheld` multiplicity-map terminology.
- Bounded wording: state the sentinel predicate using the exact schema enum rather than “whose verdict says the person kept it.”
- Bounded wording: label the package-name-install row explicitly as post-release closure so its stage notation matches the otherwise unambiguous `ONLY` sequencing.

## Verdict

**REJECT.**

Blocking items: **P3-P3-F1, P3-P3-F2, and P3-P3-F3**. The current plan can misclassify a conforming kept-label twin, certify a CSV that discarded a published numeric style, and expose a first public tree carrying false governance claims.

## Checked surfaces

- Repository HEAD `038bbb8d17aa680e74ec2e42b54cae418aaa15b8`; target remains untracked; `diff --check` clean; no files modified.
- Canonical reviewer and implementer briefs; Revision 2 plan; plan-review rounds 1–2; ratified outline and all four outline-review records.
- Declaration matching, label publication, `variants`/`variants_withheld`, G8 invention, sentinel publication, numeric-marker generation, and an executable 11-row kept-label counterexample.
- Numeric-style classification, contract 7.5.7, method G6.2–G6.4, P3-D2/P3-D8.1, and adversarial arithmetic against all four recount lines.
- Phase 0 tracked-tree/path, private-coverage, all-object history, provenance, offline, signed-note, and attestation requirements.
- Repository-status claims across the five tabulated documents, `.github/`, `tools/`, the claim-inventory surface enumeration, and the Phase 1 antecedent boundary statement.
- Release/tag/upload/post-verification sequencing, package-name installation placement, name-loss posture, and post-release R3 closure.
- Exact target-only decontamination scan using `load_manifest`, `load_magic`, `file_surfaces`, `tokenize`, and `_match_hash`: **1,054 surfaces, zero hits, zero violations**.
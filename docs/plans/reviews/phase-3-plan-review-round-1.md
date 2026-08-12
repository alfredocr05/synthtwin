<!-- Phase 3 plan adversarial review, round 1. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-12. Paths in this record are
repository-relative; references to the maintainer-private planning
outline name that document without reproducing it. -->

# Phase 3 plan review — round 1

## Numbered review items

1. **P3-P1-F1 — The ratification target fails the Class-A scan**

   **SEVERITY: blocking**

   **Concrete failure scenario:** The plan is committed and sealed, then the ordinary tracked-tree scanner runs. It reports eight hits and turns CI red. If the visibility flip follows the commit immediately as planned, the file becomes public before repair.

   **Evidence:** Direct use of the scanner’s own manifest loader, surface decoder, tokenizer, and hash matcher returned hits at `phase-3-product.md:277,331,430,484,506,702,740,897`, with digest prefixes `29269f61a2cd`, `8c71ff76e316`, `7a3b3573cac2`, `69d8d90caad3`, and `2e9ecdb7a13c`. No matched text is reproduced here. The normal scanner currently omits the file only because it is untracked and enumerates `git ls-files`: check.py:4, check.py:116, phase-3-product.md:277.

2. **P3-P1-F2 — Declaration-blind validation is not exact for all generated twins**

   **SEVERITY: blocking**

   **Concrete failure scenario:** A table has eleven copies of a built-in missing-marker spelling, and the user declares that spelling kept as data. The profile publishes it as a constant label and exact variant; generation writes that spelling byte-for-byte. Validation reconstructs an empty kept-value tuple, reads every generated cell as missing, assigns the wrong role, and emits WITHHELD outcomes instead of the required zero-WITHHELD self-validation.

   **Evidence:** The plan claims a twin never contains a declared spelling and empties `kept_values`: phase-3-product.md:157, phase-3-product.md:466, phase-3-product.md:544. The taxonomy expressly says the wider claim is false and that a kept spelling can be published: taxonomy.py:1174, taxonomy.py:1204. The generator writes published variants exactly: generation.py:4209.

3. **P3-P1-F3 — Floor-masked counts still leak through named verdicts**

   **SEVERITY: blocking**

   **Concrete failure scenario:** A valid submitted categorical profile has three neutral labels with counts 21, 12, and 11. The measured file has the same role and counts 22, 12, and 10. Its own profile suppresses the third label’s identity and publishes only anonymous suppressed-group facts. The proposed report nevertheless names that submitted-profile label, prints “fewer than 11,” and emits MISSED. It has associated a below-floor group with a name the measured file’s own profile would not associate with it.

   **Evidence:** The plan withholds an outcome only when the file’s role prevents the fact class from appearing, but explicitly retains exact comparison and a named lesser-than-floor display for label/style/offset checks: phase-3-product.md:403, phase-3-product.md:433. The producer omits the label entry entirely below the floor: taxonomy.py:2833, taxonomy.py:2863. Styles and offsets use the same withholding rule: taxonomy.py:2996, taxonomy.py:3081.

4. **P3-P1-F4 — The pooled-style OPEN repair has no satisfiable mechanism**

   **SEVERITY: blocking**

   **Concrete failure scenario:** A numeric profile has a non-whole endpoint whose source style was pooled below the floor. Contract v4 requires pooled cells to recount as `plain`, but a non-whole value necessarily recounts as decimal or exponent. The plan forbids a contract change and merely promises a method amendment plus code. The implementer must therefore leave the OPEN defect, violate the endpoint, or weaken `numeric_styles` while deleting the OPEN line.

   **Evidence:** The plan rules out a profile-contract change and provides no exact arbitration rule: phase-3-product.md:30, phase-3-product.md:671. Contract v4 makes the conflict mechanical: profile-contract-v4.md:1530, profile-contract-v4.md:1569, profile-contract-v4.md:1674. The OPEN record says an owner amendment or an actual compatible rule is still required: dispositions.py:855.

5. **P3-P1-F5 — The public flip omits the required current-history scan**

   **SEVERITY: blocking**

   **Concrete failure scenario:** A Phase 2 commit contained Class-A text that a later commit deleted. The tracked-tree scan is green. The plan commit lands and the repository immediately becomes public, exposing the old blob. The all-object scan occurs only later during release preparation, after disclosure.

   **Evidence:** The flip checklist contains governance API work but no current full-history/provenance/offline run: phase-3-product.md:652. The all-object run is deferred to release preparation: phase-3-product.md:702. Phase 0 requires the full battery before first public exposure, including reachable and unreachable objects: phase-0-public-skeleton.md:524.

6. **P3-P1-F6 — Condition B’s totality rule contradicts its own STRUCTURAL split**

   **SEVERITY: blocking**

   **Concrete failure scenario:** The single registry fact `document/columns` needs an input-side subcheck for profile membership and an executable subcheck for output order. The proposed totality test instead requires each fact/predicate pair to have exactly one kind. An implementation can satisfy that test only by dropping one obligation or contradicting the test.

   **Evidence:** The plan correctly says `columns` contributes both kinds, then incorrectly reduces totality to one kind per registry fact and predicate: phase-3-product.md:273, phase-3-product.md:282, phase-3-product.md:287. Contract S1–S4 contains both profile and output duties: profile-contract-v4.md:215. Round-4 condition B required totality per full `(fact, predicate, subcheck)` identity: outline:929.

7. **P3-P1-F7 — The exhaustive claim-migration table was deferred out of the plan**

   **SEVERITY: blocking**

   **Concrete failure scenario:** Implementation creates a migration table containing only the grouped surfaces named in P3-D7. Its tree walker passes, while stale two-command text remains in README, transaction/module comments remain bounded to two commands, and the generation specification still calls the quality report future work. The test proves only the completeness of an incomplete table.

   **Evidence:** The ratified outline requires the plan itself to enumerate every sentence, surface, stage, replacement, and pinned form: outline:624. The plan instead says its later implementation will carry the full table: phase-3-product.md:613, phase-3-product.md:645. Existing omitted examples include README.md:37, errors.py:416, writing.py:15, and generation-method-v1.md:25.

8. **P3-P1-F8 — The PyPI claim flip has no truthful commit boundary**

   **SEVERITY: condition**

   **Concrete failure scenario:** The reviewed tag removes the current “not on PyPI” text before upload; the upload fails or the name is unavailable, leaving a false public claim. If the text remains until a later commit, the released wheel and PyPI project page retain the false statement after successful publication.

   **Evidence:** P3-D7 requires claim edits in the same commit as the change making them true and assigns these edits to “at the release”: phase-3-product.md:613, phase-3-product.md:639. Upload is an external operation after the reviewed/tagged commit is fixed: phase-3-product.md:692, phase-3-product.md:724. The current claim appears in README.md:3, and Phase 0 explicitly says name availability is unverified until upload succeeds: phase-0-public-skeleton.md:33.

9. **P3-P1-F9 — R-P3-6 understates declaration-blind divergence**

   **SEVERITY: condition**

   **Concrete failure scenario:** A numeric-looking spelling was declared missing during profiling. In an arbitrary file, declaration-aware profiling removes it before role selection and statistics; declaration-blind validation retains it. That can change the role, mean, percentiles, and resulting outcomes—not merely which counts are shown or hidden.

   **Evidence:** The plan limits the cost to counts: phase-3-product.md:157, phase-3-product.md:856. Declarations run before any role or statistic: taxonomy.py:2511, taxonomy.py:4233.

10. **P3-P1-F10 — Two settings keys are assigned the wrong semantics**

    **SEVERITY: condition**

    **Concrete failure scenario:** A high-uniqueness undeclared text column reaches validation. An implementer following the normative settings table treats `identifier_uniqueness` and `identifier_minimum_rows` as role-routing thresholds and sends the column down the identifier path, although the profiler permits only an explicit `--identifier` declaration to select that role.

    **Evidence:** The plan calls both classifier thresholds: phase-3-product.md:457. The shipped taxonomy says both decide only whether advisory text is printed and decide no role: taxonomy.py:1136, taxonomy.py:1143, taxonomy.py:4193.

11. **P3-P1-F11 — The release metadata check is weaker than the ratified outline**

    **SEVERITY: condition**

    **Concrete failure scenario:** The workflow uses a generic metadata check or invokes `twine check` without the required strict option. The plan’s acceptance language can still be claimed satisfied even though the exact ratified check was dropped.

    **Evidence:** The outline requires `twine check --strict`: outline:715. The plan weakens this to “strict metadata check”: phase-3-product.md:769.

## Conditions A/B/C

- **Condition A — NOT SATISFIED.** The table names exactly the same 15 keys as `contract.SETTINGS_KEYS`, with no missing or extra key, and treats `header_source` separately. Its semantics are nevertheless unsound: empty `kept_values` is not exact for all twins (F2), two keys are misdescribed (F10), and the stated residual is incomplete (F9).

- **Condition B — NOT SATISFIED.** The triple is introduced and the named cases appear, but the asserted totality test collapses back to one kind per fact/predicate and conflicts with the required STRUCTURAL split (F6). The zero-row predicate also needs to distinguish the empty-byte form from the header-bearing zero-row form.

- **Condition C — SATISFIED.** P3-D8.3 keeps generation enabled, binds attestations to artifact digest and reviewed source commit, requires post-publication verification, records evidence, and repeats the requirement in acceptance criterion 8: phase-3-product.md:751, phase-3-product.md:896. This matches Phase 0 D10 and SECURITY.md:560.

## Verdict

**REJECT.**

Blocking items: **P3-P1-F1 through P3-P1-F7**. The target cannot land cleanly, the declaration gate is false on a valid twin, the report still has a below-floor outcome channel, one OPEN repair has no contract-consistent mechanism, the public flip omits its history control, condition B is internally inconsistent, and the exhaustive claim-migration obligation was deferred out of the ratification document.

## Checked surfaces

- HEAD `038bbb8d17aa680e74ec2e42b54cae418aaa15b8`; worktree contains only the untracked target.

- Canonical reviewer and implementer briefs; full revision-0 plan; full revision-4 outline; all four outline-review records.

- Contract v4: all 15 settings keys, declaration wire form, header modes, zero-row forms, STRUCTURAL rules, label variants, floor behavior, numeric styles, offsets, relationships, disposition tables, and G12-linked cases.

- Registry: 110 facts; class counts `72/10/6/11/7/4`; both OPEN entries; authorization map; governing set, seal, and exact-list guard.

- Profiler and generator: declaration order, kept-value publication, role routing, label/style/offset suppression, exact variant writing, zero-row rendering, and OPEN-defect paths.

- CLI, strict loader, reader boundary, one/two-file transaction controls, alias handling, and the stated check-to-use residual.

- Phase 0/1/2 plans and Phase 2 round-5 record; public-flip governance, release integrity, history/provenance duties, name-loss posture, and R3.

- CI topology: 11-cell main test matrix, minimums job, aggregate gate, SHA-pinned actions, locks, build container, and current private-mode claims.

- Claim inventory: `SURFACES`, claim-bearing/structure-bearing sets, command words, phase statements, artifact forms, front-page tags, and currently stale command/release text.

- Target-only Class-A scan using the repository scanner’s exact primitives; tracked-tree scan behavior; whitespace check.

- Attack classes: kept-declaration self-validation failure, below-floor named-outcome oracle, conditional-entry omission, impossible exact obligations, stale claim-table self-validation, public-history exposure, tag/readme timing, reviewed-SHA substitution, hollow SBOM, missing provenance evidence, and release-command weakening.

For the drafter: no drafting-only preferences; every material issue found meets the numbered-finding threshold.
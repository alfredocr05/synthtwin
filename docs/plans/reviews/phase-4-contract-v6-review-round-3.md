<!-- Phase 4 contract v6 review, round 3. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-20. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it. -->

# Phase 4 contract v6 review — round 3

Reviewed revision 2 at `f50fcce` against the ratified plan, both carried contract documents, shipped loader/producer/taxonomy, and disposition registry.

## Round-2 verification

| Round-2 item | Status | Evidence |
|---|---|---|
| P4-X2-F1 | **NARROWED** | Settings and version now appear in the supersession table at `docs/spec/profile-contract-v6.md:145` and `:152`; C6-20 still misidentifies the old settings section as §4.3 at `:354`, while the enumeration is `docs/spec/profile-contract-v4.md:274`. |
| P4-X2-F2 | **NARROWED** | Role, axes, format and resolution enumerations are now named at `docs/spec/profile-contract-v6.md:138-142`; the publication-class replacement at `:143` is not complete. |
| P4-X2-F3 | **NARROWED** | C5-19 is now named at `docs/spec/profile-contract-v6.md:150`, but its alleged replacement C6-40 is the collision rule at `:589`, not a three-list completeness rule. |
| P4-X2-F4 | **CLOSED** | AF3, AF4, AF6 and AF7 are distinct at `docs/spec/profile-contract-v6.md:744-749`. |
| P4-X2-F5 | **NARROWED** | Several citations were repaired, but stale or nonexistent targets remain at `docs/spec/profile-contract-v6.md:147`, `:150`, `:354`, `:415`, `:622`, `:683`, `:759` and `:903`. |
| P4-X2-F6 | **NARROWED** | The contract now gives one sibling location and a canonical width-key grammar at `docs/spec/profile-contract-v6.md:429-455`; that location contradicts the governing plan, and P5 remains non-total when `decimal` is pooled. |
| P4-X2-F7 | **NARROWED** | DF-P and DF-R now make counting both readings a producer obligation at `docs/spec/profile-contract-v6.md:740-741`; the form still omits the reading-used argument and the exact two-clause rendering. |
| P4-X2-F8 | **NARROWED** | Three identifiers, arities and argument lists now exist at `docs/spec/profile-contract-v6.md:674-678`; no exact rendering exists. |
| P4-X2-F9 | **CLOSED** | All four core counts now have dispositions at `docs/spec/profile-contract-v6.md:696-700`. |
| P4-X2-F10 | **CLOSED** | CP-P is explicitly producer-only at `docs/spec/profile-contract-v6.md:742`. |
| P4-X2-F11 | **CLOSED** | BD-P explicitly binds `built_in_dates` to the command line alone at `docs/spec/profile-contract-v6.md:743`. |
| P4-X2-F12 | **NARROWED** | The migration table now contains the formerly absent residual, phase and loud-decline rows at `docs/spec/profile-contract-v6.md:901-905`, but it remains incomplete and one clause range is wrong. |
| P4-X2-F13 | **CLOSED** | C6-47 now distinguishes the maker from a later holder and gives both paths at `docs/spec/profile-contract-v6.md:796-821`. A narrower release-state overclaim remains as a new item below. |

## Section 2.2.2A — all sixteen rows audited

| Row | Result |
|---|---|
| Role enumeration | **Correct.** The old ten-role closure is the blocker; C6-1 and §14 replace it. |
| Statistical types and axes | **Correct.** C6-19 and §14 provide thirteen rows/members. |
| Format and resolution bindings | **Correct.** C6-21/C6-22 and §14 supply the eleven-member set and bindings. |
| Resolution | **Correct.** C6-24 and §14 add `month`. |
| Time precision | **Correct.** C6-24 and §14 add `month`. |
| Publication classes | **Incorrect.** Version 4 §6.10 fixes the existing nothing-publishing membership; C6-9/C6-14/C6-18 classify only the three new roles and do not replace the old thirteen-role class map. |
| Forbidden-key matrix | **Substantively correct replacement.** Section 7A supplies the union, although its introductory C6-24 citation is stale. |
| Settings enumeration | **Correct in the table.** C6-20 replaces the fifteen-key enumeration; C6-20’s own §4.3 citation remains wrong. |
| Absence classes | **Correct.** C6-N3 supplies all six keys and both carried invariants. |
| Published vocabulary | **Incorrect citation.** The replacement is C6-31, not C6-34. |
| Declaration-record shape | **Correct.** C6-S14 supplies exactly five keys. |
| Declaration count | **Correct.** C6-K3 extends the identity to three lists. |
| Kept-side completeness | **Incorrect.** C6-40 is unrelated and no three-list successor to C5-19 is stated. |
| Empty absent cells | **Correct.** C6-37 replaces C5-9. |
| Version and single-version loading | **Correct.** C6-44 covers both. |
| C5-26 holder assumption | **Partial.** C6-47 repairs the holder assumption, but C5-26 was an exact-message clause and C6-46/C6-47 do not supply an exact replacement message. |

The table also omits closed inherited rules that version 6 changes: version 5’s “five ways and no sixth” reading enumeration, its exhaustive C5-S13 floor-one list, and C5-17’s declaration-matching rule. It also omits C6-V4 despite that clause expressly superseding V4.

## Plan-delta coverage

| Governing item | Result |
|---|---|
| P4-D7.1 — roles through every closed enumeration | **Open:** publication-class replacement is incomplete. |
| P4-D7.2 — existing-role facts and format additions | **Open:** fraction-width placement contradicts the plan and P5 is not total. Other format, resolution and length additions are present. |
| P4-D7.3 — vocabulary and declaration consequences | **Open:** carrying and claim migration remain incomplete. |
| P4-D7.4 — reproduction rule | **Complete:** C6-37 through C6-40 and the disposition moves are present. |
| P4-D7.5 — exactly seventeen settings | **Complete in C6-20:** fifteen inherited plus two; §14 omits the enumeration. |
| P4-D7.6 — dispositions | **Complete for the enumerated facts.** |
| P4-D7.7 — disclosure delta | **Complete as an inventory of sections 3–6.** The grammar escape in P4-X3-F6 remains a separate publication-boundary defect. |
| P4-D7.8 — version/refusal | **Narrowed:** version and fail-closed behavior are complete; exact refusal text is not. |
| P4-D7.9 — migration | **Open.** |
| A-P4-1.1/.2 | **Complete:** unpadded and slashed-datetime readings are bounded as required. |
| A-P4-1.3 | **Open:** date-placeholder mechanics exist, but inherited reading/declaration rules conflict. |
| A-P4-1.4 | **Narrowed:** the trigger is a producer obligation, but its grammar form is incomplete. |
| A-P4-2 | **Checked:** it adds no contract-v6 wire delta contradicted here. |
| A-P4-3 | **Open:** raw affix fragments violate its argument boundary. |
| A-P4-4 | **Complete:** phase/release history matches the checked repository state. |

## Numbered review items

1. **P4-X3-F1 — SEVERITY: blocking.**

   **SIDE:** Control gap.

   **CONCRETE FAILURE SCENARIO:** A version 6 document judges `1900-01-01` absent through the calendar-placeholder pass. C6-34 requires that route, but carried version 5 §3.1 still says there are five ways a cell becomes absent “and no sixth,” while §3.3’s supposedly complete consumer derivation knows only those five. The loader and consumer cannot both follow the carried and new rules. Separately, a floor-one document can carry a pooled `fraction_widths` remainder because C5-S13’s exhaustive closed list remains live while the supersession table omits C6-S13.

   **EVIDENCE:** Total carrying and the assertion that the table contains every exception are `docs/spec/profile-contract-v6.md:104-157`; the calendar route is `docs/spec/profile-contract-v6.md:501-525`; the omitted C6-S13 supersession is nevertheless asserted at `docs/spec/profile-contract-v6.md:768`. The conflicting old reading enumeration and consumer derivation are `docs/spec/profile-contract-v5.md:224-282`; C5-S13 says its floor-one list is exhaustive at `docs/spec/profile-contract-v5.md:1020-1046`. A-P4-1 requires the new absence route at `docs/plans/phase-4-columns.md:1630-1660`.

2. **P4-X3-F2 — SEVERITY: blocking.**

   **SIDE:** Control gap; privacy-class closure.

   **CONCRETE FAILURE SCENARIO:** An implementer generates the publication-class registry from the supersession table. Because version 4 §6.10 is superseded entire but C6-9/C6-14/C6-18 describe only the three new roles, the registry has no normative class row for the ten inherited roles. It must either invent those memberships or omit the exact-one-class check, weakening the block-level privacy control.

   **EVIDENCE:** The entire-replacement row is `docs/spec/profile-contract-v6.md:143`; the three replacement clauses cover only the new roles at `docs/spec/profile-contract-v6.md:272-278`, `:319` and `:342-343`. The displaced rule is `docs/spec/profile-contract-v4.md:1304-1312`. The plan requires every role to remain in exactly one publication class at `docs/plans/phase-4-columns.md:545-557` and `:1153-1159`.

3. **P4-X3-F3 — SEVERITY: blocking.**

   **SIDE:** Control gap; type misrouting and declaration closure.

   **CONCRETE FAILURE SCENARIO:** A command line declares the exact spelling `NaT`. C6-32 requires raw-byte matching and records the exact member; carried C5-17 instead applies trimming and case folding. Two conforming implementations can therefore disagree about whether the declaration enters `built_in_texts`. A second document can place the same calendar placeholder in both `kept_values.built_in_dates` and `declared_missing_values.built_in_dates`: the prose claims C5-K4 “now covers” it, but the carried rule names only the text and number lists and §9 contains no date-list non-overlap invariant.

   **EVIDENCE:** Exact matching is required at `docs/spec/profile-contract-v6.md:477-488`; the five-key records and asserted extension of C5-K4 are `docs/spec/profile-contract-v6.md:529-548`; §9’s purported complete list is `docs/spec/profile-contract-v6.md:721-770`. C5-17’s folded rule is `docs/spec/profile-contract-v5.md:653-660`; C5-K4’s two-list scope is `docs/spec/profile-contract-v5.md:780-784`. A-P4-1 requires `built_in_dates` to inherit the numeric list’s identity rules at `docs/plans/phase-4-columns.md:1657-1660`.

4. **P4-X3-F4 — SEVERITY: blocking.**

   **SIDE:** Control gap; silent statistical wrongness.

   **CONCRETE FAILURE SCENARIO:** With floor 11, a numeric column has ninety `plain` cells and ten `decimal` cells, all at fraction width two. Version 4 correctly publishes `numeric_styles` with `plain: 90` and `(withheld): 10`; there is no `decimal` key. Version 6 requires `fraction_widths` with `(withheld): 10`, but P5 requires its sum to equal the nonexistent `decimal` value. No document can satisfy the rule. In addition, the contract puts the fact beside `numeric_styles` while the ratified plan explicitly places it inside that block.

   **EVIDENCE:** The sibling location and P5 are `docs/spec/profile-contract-v6.md:429-455`. The inherited style-floor behavior and P1/P2 are `docs/spec/profile-contract-v4.md:1676-1708`. The plan requires the fraction fact inside the numeric-styles block at `docs/plans/phase-4-columns.md:1183-1184` and governs every conflict at `docs/spec/profile-contract-v6.md:3-12`.

5. **P4-X3-F5 — SEVERITY: blocking.**

   **SIDE:** Control gap; determinism.

   **CONCRETE FAILURE SCENARIO:** Two producers use the same identifier, arity and counts but render the recoverable-distribution or slashed-date sentence differently. Both satisfy the contract because it supplies no literal rendering or template. The publication guard has no normative text to rebuild. For the slashed-date form, the four arguments also omit the reading used and do not define the plan’s two independent clauses, so evidence-decided but internally contradictory columns can be described differently.

   **EVIDENCE:** The table and unsupported assertion of “one fixed text” are `docs/spec/profile-contract-v6.md:647-687`; no rendering follows. The plan requires four counts plus the reading used and two independently triggered clauses at `docs/plans/phase-4-columns.md:873-900`, and exact grammar forms at `docs/plans/phase-4-columns.md:909-922`. The shipped grammar’s enforceable pattern is an explicit rendering branch at `src/synthtwin/taxonomy.py:506-509` and `:753-775`.

6. **P4-X3-F6 — SEVERITY: blocking.**

   **SIDE:** Security/privacy control gap.

   **CONCRETE FAILURE SCENARIO:** The affix sentence passes raw prefix and suffix strings as grammar arguments. The shipped guard rejects them because string arguments are confined to the package’s date-format vocabulary. If implementation simply widens that guard to arbitrary strings, a source-derived value can be inserted into a sentence and rebuilt successfully. The contract supplies no contextual equality check binding the arguments to that column’s already floor-cleared `affix_prefix` and `affix_suffix`.

   **EVIDENCE:** Raw affix arguments and the attempted authorization are `docs/spec/profile-contract-v6.md:674-687`. A-P4-3 limits profile-sentence arguments to whole numbers and the package’s own words at `docs/plans/phase-4-columns.md:1753-1758`. The shipped guard’s closed string vocabulary and recursive check are `src/synthtwin/taxonomy.py:617-625` and `:674-714`; the publication guard checks form, arity, enumerated arguments and reconstruction, but not path-specific argument identity, at `src/synthtwin/profile.py:953-981`.

7. **P4-X3-F7 — SEVERITY: blocking.**

   **SIDE:** Control gap.

   **CONCRETE FAILURE SCENARIO:** Stage 6 follows C6-MIG literally. It updates the three locations named for the vocabulary count but leaves other public assertions at thirteen, including README prose and source claims. Because C6-MIG says unlisted sentences do not move, its own migration battery can pass while public surfaces contradict the 23-member wire. The R-P3-12 row also seals C6-27 through C6-33, thereby treating vocabulary and placeholder clauses as fraction-width controls.

   **EVIDENCE:** The exhaustive claim and incomplete rows are `docs/spec/profile-contract-v6.md:886-905`. Current additional vocabulary-count claims include `README.md:217`, `src/synthtwin/contract.py:2514`, `src/synthtwin/profile.py:233-248`, `src/synthtwin/taxonomy.py:2611-2617` and `CHANGELOG.md:366`. The plan requires every vocabulary-count surface and one row per moving sentence at `docs/plans/phase-4-columns.md:1248-1265` and `:1683-1691`.

8. **P4-X3-F8 — SEVERITY: serious.**

   **SIDE:** User-facing control gap and unsupported release inference.

   **CONCRETE FAILURE SCENARIO:** Two loaders issue materially different older-version refusals while both claim to retain C5-26’s “shape,” because C6-46/C6-47 supersede the exact-message clause without supplying exact replacement text. Separately, a maintainer can build an unreleased wheel from the checkout and give that wheel to a colleague, who then makes a description without running a source checkout. That state preserves “no tag and nothing published” but falsifies C6-47’s asserted maker bound.

   **EVIDENCE:** C6-46/C6-47 are `docs/spec/profile-contract-v6.md:788-821`; the table supersedes C5-26 at `docs/spec/profile-contract-v6.md:153`. C5-26 makes its message word-for-word normative at `docs/spec/profile-contract-v5.md:1077-1106`. The plan requires the message to be rewritten and the release analysis bounded at `docs/plans/phase-4-columns.md:1235-1247`. The release facts themselves are supported by `docs/plans/phase-3-product.md:7480-7498`, `STATUS.md:3-4`, `README.md:3-4`, `CHANGELOG.md:7-16`, and the empty repository tag set; only the source-checkout inference exceeds that evidence.

9. **P4-X3-F9 — SEVERITY: serious.**

   **SIDE:** Control gap; registry and migration misbinding.

   **CONCRETE FAILURE SCENARIO:** An implementation resolves normative citations mechanically. It binds unrepresentable lengths to C6-24, which governs month resolution; cannot resolve C6-DF at all; records invariant `FKM` separately from primary rule `C6-FKM`; and searches §9 for the `resolution_mix` disposition although §9 contains invariants. Controls can therefore be registered under the wrong identifier while an audit reports every cited clause visited.

   **EVIDENCE:** The stale references are `docs/spec/profile-contract-v6.md:354-356`, `:415`, `:619-623`, `:683`, `:759` and `:903`. The actual controls are C6-26 at `docs/spec/profile-contract-v6.md:419-425`, C6-FKM at `:619`, DF-P/DF-R at `:740-741`, and the `resolution_mix` disposition at `:708` and `:919-924`. The old settings enumeration is §4.4 at `docs/spec/profile-contract-v4.md:274-297`.

10. **P4-X3-F10 — SEVERITY: minor.**

   **SIDE:** Wording/provenance and appendix closure.

   **CONCRETE FAILURE SCENARIO:** A reviewer relying on the document’s status and declared enumeration appendix reads revision 0, “two sentences,” and no settings enumeration, despite this being revision 2, the grammar table containing three forms, and C6-20 fixing seventeen settings keys.

   **EVIDENCE:** The stale status is `docs/spec/profile-contract-v6.md:3`; round 2 already describes revision 1 at `docs/plans/reviews/phase-4-contract-v6-review-round-2.md:141`. The two-versus-three contradiction is `docs/spec/profile-contract-v6.md:647-678`. C6-20 states seventeen settings at `docs/spec/profile-contract-v6.md:354-367`, but §14 ends without enumerating them at `docs/spec/profile-contract-v6.md:943-975`.

The protocol does not stop early: P4-X3-F1 through P4-X3-F7 are control gaps, including privacy and silent-statistical-wrongness paths. P4-X3-F10 is on the wording side; the rest are not.

## VERDICT

**Reject.**

Blocking items: **P4-X3-F1, P4-X3-F2, P4-X3-F3, P4-X3-F4, P4-X3-F5, P4-X3-F6 and P4-X3-F7**.

## What was checked

- Exact target commit `f50fcce`, branch state, and the complete `375319a..f50fcce` repair diff.
- Every round-2 item P4-X2-F1 through P4-X2-F13.
- Every one of the sixteen section 2.2.2A supersession rows, plus omitted inherited enumerations and every explicit `supersedes` declaration elsewhere in revision 2.
- P4-D3; P4-D4.1 through P4-D4.7; P4-D5; P4-D6; all nine P4-D7 delta items; amendments A-P4-1 through A-P4-4.
- All cross-references in the supersession table, forbidden-key matrix, grammar, invariant table, migration table and disposition rows.
- Grammar identifiers, arities, argument domains, missing renderings, day-first evidence, and the shipped publication guard.
- Role, axis, publication-class, format, resolution, precision, absence, vocabulary, settings and forbidden-key closure.
- Arithmetic: **13 roles**—the target does not state twelve—13 statistical types, 11 formats, 4 resolutions, 6 time precisions, 2 clock forms, 6 absence classes, 23 vocabulary members, and 17 settings keys. The numerical totals are correct.
- Disclosure section 12 against every publication added in sections 3–6.
- Shipped `contract.py`, `profile.py`, `taxonomy.py`, and `tests/dispositions.py`; both shipped version constants remain 5, as expected before version 6 implementation.
- Phase 3’s 2026-08-19 owner closure, unreleased status, changelog, README, and absence of tags.
- The decontamination scanner and `git diff --check`; both completed cleanly. No scanner concern arose.
- No files were written or changed. `pytest` was not run.
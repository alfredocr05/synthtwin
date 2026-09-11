# Phase 4 — the obligations landing, adversarial review round 3

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only, 2026-08-26.
**Verdict: REJECT**, six blocking and one serious. Every item was real;
none was wording; all seven are repaired. **This was written as the
last round under A-P4-30's cap of three. The owner withdrew that cap
the same day**, raising it back to five, so rounds 4 and 5 follow.

**THE ROUND FOUND MORE OF EACH CLASS THAN IT NAMED, and that is the
useful part.** Where it named one site, there were two:

| item | named | actually found |
|---|---|---|
| 1 the joined role still described as WHOLE numbers | five surfaces | five, plus the function name `splits_into_wholes` itself, which was the origin of the false sentence on all of them |
| 2 a ninth site stating 44 forms | one (NG14 in section 8) | TWO — NG14 appears in section 4 and section 8 |
| 3 `joined_numbers` absent from the disposition matrix | section 9 and section 12 | both, plus the appendix's ranges-class row, which counted five roles where section 4 counts six |

**Item 1 is a product defect and the second this landing has found.** A
column of `1:2.0` published "2 WHOLE numbers" while
`splits_into_numbers` admits a decimal point in its own docstring. The
function is renamed and all six surfaces corrected.

**Item 3 was a governance gap for a SHIPPED role.** Section 9 asserts
completeness over fourteen roles and had no table for the fourteenth;
eight published facts — the separator, the part and split counts, the
per-position width bounds and the two pairing aggregates — had no
disposition at all. Section 9.4a is written, lettered so nothing
renumbers.

**Item 6 is the one that mattered most, and it changed a decision.**
The landing had DEFERRED R-P4-25 as "its own commit". The reviewer
showed that deferring left `profile-contract-v6.md` outside
`GOVERNING` — so the contract governing every description this tree
writes was the one document outside the seal, and the landing's own 156
changed contract lines were unsealed. Version 6 joined the sealed set
in this landing: 1,987 distinct passages. Verified by lowering a version 6
disposition from exact to report-only and watching the suite turn red.

**Items 2, 4, 5 and 7 were repaired and measured.** The grammar's size
is now computed rather than restated, at every site that states it; the
exemption ban grew four wordings and a sixth obligation shape; the bare
pronouns were split from the plain ones and are admitted only to CARRY
a claim into the very next statement, never to EXCUSE one and never
across a bridge — which was unsound in both directions and had a
comment beside it claiming they were gone; and the state page no longer
records the go decision as both taken and waiting.

**Measured after the repair:** 28 of 28 attack wordings caught, 6 of 6
honest wordings clean, zero offenders on the whole governed tree, and
every count guard mutation-verified.

**Round 4 followed**, under the owner's ruling of 2026-08-26 raising
the cap back to five.

---

## The review as written

## Verdict: reject

Blocking items 1–6 prevent ratification. Item 7 is serious.

## Items

1. **SEVERITY: blocking — NF47 is corrected, but the product still describes decimal joined readings as whole numbers.**

   **CONCRETE FAILURE SCENARIO:** A researcher profiles `1:2.0` / `1:2.5` interactively. The reader accepts every cell, but the question says every value contains “whole numbers.” Relying on that description, the researcher leaves the column as text; the profile then publishes no readings and the twin loses the joined quantities.

   The false wording remains in [cli.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/cli.py:929>), [README.md](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/README.md:194>), [CHANGELOG.md](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/CHANGELOG.md:65>), and two normative contract passages: [settings](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:600>) and [role definition](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:5255>).

   The repaired evidence rendering itself is true. Direct probes confirmed that accepted parts contain ASCII figures with at most one internal decimal point; `NaN`, `.5`, and exponent notation are refused. The summary uses the corrected evidence. I found no remaining joined-role “whole” claim in the generation or quality report producers.

2. **SEVERITY: blocking — there is a ninth grammar site, and it still says 44 forms.**

   **CONCRETE FAILURE SCENARIO:** A consumer enforces NG14 in [contract section 8](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6621>). It accepts only “one of the 44” forms and therefore refuses one or more of NF45–NF48, although sections 4.5.1, 12.2, and 14.8 say 48.

   The new guard reads defining clauses, appendix rows, arities, and one package-word count. It does not read NG14, any of the three census passages, or the bound-affix-position count; see [the parser and checks](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p4d27_note_grammar_matches_the_code.py:80>). Thus this live contradiction does not turn it red.

3. **SEVERITY: blocking — `joined_numbers` has no complete disposition or disclosure account.**

   **CONCRETE FAILURE SCENARIO:** A profile of `1:2.5` publishes `separator`, `n_parts`, `n_joined`, `n_unparsed`, `parts`, `part_min_widths`, `part_agreements`, and `part_above`. Section 9 claims every fact of all fourteen roles has exactly one disposition, but supplies no joined-role table. Section 12 claims every disclosed fact has a row, but its ranges row expressly lists five roles and omits `joined_numbers`.

   An institutional reviewer using the promised exhaustive inventory consequently receives no treatment for the separator, positional statistics, or within-cell pairing aggregates. See the [section 9 completeness assertion](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6656>) and [section 12 ranges row](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:7553>).

4. **SEVERITY: blocking — ordinary exemption wording still walks past both phrase inventories.**

   **CONCRETE FAILURE SCENARIO:** Add “Synthetic data does not need ethics review” to README. The obligation half matches, but “does not need” is absent from the exemption forms, so `_grants_an_exemption` returns no offender. I reproduced the same miss for:

   - “Institutional approval can be skipped for synthetic data.”
   - “Synthetic files are exempt under the privacy policy.”
   - “Synthetic data lets you ignore institutional rules.”

   The stored 23 attacks remain green, but they do not cover these ordinary constructions. The relevant lists are at [test_claim_inventory.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6323>).

5. **SEVERITY: blocking — bare `it` and `this` make carry and cure unsound.**

   **CONCRETE FAILURE SCENARIO:** “The twin is exempt from data-use agreements. It still applies a publication floor.” The second sentence is about the twin, not the agreement, but bare `it` is accepted as a regime back-reference and “still applies” cures the real banned claim. The matcher returns no offender.

   The reverse also fails: “Privacy rules govern generated files. This package reads CSV. It does not apply to Parquet.” is reported as an exemption from privacy rules because the final `it` is attached across the bridge. The comment says bare `it` is gone, but `_REFERS_BACK` contains both `it` and `this`; see [lines 6493–6505](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6493>). The new `step` offset is arithmetically correct; this defect is in reference identity, not the offset.

6. **SEVERITY: blocking — deferring R-P4-25 leaves the current contract outside the seal.**

   **CONCRETE FAILURE SCENARIO:** Lower version 6’s `time_of_day` endpoint disposition from exact to report-only. The seal remains current because `profile-contract-v6.md` is absent from `dispositions.GOVERNING`; the companion control still labels it a draft that will join at ratification, although it is now the current contract. See [dispositions.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/dispositions.py:100>) and [the stale draft exception](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p2c4f1_disposition_registry.py:376>).

   All twelve newly added seal digests belong to the Phase 4 plan; none covers the 156 changed contract lines. Given items 2 and 3, repointing is not merely administrative—it would expose live contract gaps. R-P4-25 should not be deferred from this seal landing.

7. **SEVERITY: serious — STATE records the go decision as both taken and waiting.**

   **CONCRETE FAILURE SCENARIO:** The next agent reads the mandatory state page. Lines 36–41 say the owner gave “Go. Lean 15,” while lines 86–90 say the go decision and standing authorization are still waiting. Following the latter stops work or re-asks a settled decision. See [STATE.md](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/STATE.md:36>).

## Checked

- Read both repository briefs, STATE, both prior review records, and the complete staged diff from `792e380`.
- Recomputed the grammar: 48 defining clauses and 79 positions; 48 appendix rows and 79 positions; producer 47 forms and 72 positions, with the five named exceptions accounting for the difference.
- Directly rendered NF47 and probed accepted and refused joined-number spellings.
- Searched the summary, interactive CLI, generation report, quality report, contract, README, changelog, and relevant source surfaces for joined-role “whole” claims.
- Exercised the claim matcher directly without pytest: 23/23 stored attacks caught, 5/5 stored honest sentences clean, zero current-tree offenders, plus the new bypass and false-positive probes above.
- Verified `_carried_exemption`’s new offset begins after the carrying statement.
- Mapped all twelve newly sealed passages against the baseline. No sealed passage lowers a bar without an amendment: A-P4-40 and A-P4-41 are the only reductions; both are explicit. R-P4-23 correctly closes by ruling, and contract 1.7a states the retained cost.
- Confirmed the seal generator reports current, the decontamination scan returns clean, and `git diff --check` is clean.
- Did not run pytest.
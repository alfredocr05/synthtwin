# Phase 4 — the obligations landing, adversarial review round 4

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only, 2026-08-26,
under the owner's ruling of the same day raising the cap from three
rounds to five. **Verdict: REJECT**, nine blocking. Every item real.

**THE ROUND FOUND A PRODUCT DEFECT WORSE THAN EITHER OF THE FIRST
THREE.** A twin of a joined column carried a report saying **"This twin
has no approximated fact at all"** while every position's ladder and
both pairing aggregates were approximated by construction.
`_approximations` had no branch for the role and returned an empty
list. Measured on 400 blood pressures before and after; the report now
names each fact with its published value, its achieved value and its
range. **The identical defect had been found and repaired one role
earlier, on `affixed_number`, whose branch carries a comment saying so
— and it was not carried across.** A report that tells a person the
twin gave nothing up, of a twin that did, is the failure this project
puts ahead of every ordinary bug.

**What was repaired here**

| item | what it was | how it was verified |
|---|---|---|
| 1 | the seal detected a passage WRITTEN or CHANGED and not one DELETED — an obligation could be removed and the digest silently orphaned | a reverse check added; verified by deleting the `part_above` row and watching the suite turn red. My own "1,989 passages" was wrong too: 2,191 instances, 1,987 distinct |
| 2 | the count guard could be walked past three ways | duplicate appendix rows now stop the read; any number before the word `forms` is held to the count. Both mutation-verified |
| 4 | the generation report omitted every joined approximation | closed, measured on 400 readings |
| 6 | section 9.4a carried THREE false dispositions of my own writing | `n_parts` holds of the SPLIT cells and not every present cell; `part_min_widths` is a minimum only, with no maximum published; the agreement window is in the PLAN and in neither method specification |
| 7 | the exemption guard was still unsound both ways, with `they` behaving exactly as `it` had | plural pronouns moved to the vague set; a bare pronoun now reaches only the next statement, and cures only where it AGREES IN NUMBER with the obligation named — which is the one thing about reference a regular expression can settle |
| 8 | the joined-number wording survived in `asking.py`, the plan, and NF47's naming of the retired symbol | all three corrected |
| 9 | the state page still told the next agent that three rounds were the maximum | corrected to five, and the round-3 record no longer calls itself final |

**Items 3 and 5 are NOT repaired here, and are recorded instead as
residuals R-P4-43 and an unnumbered defect beside them.** Both are
gaps in the joined role itself rather than in this landing: the
validator checks a position's endpoints and whole-number test and not
its styles or fraction census, and a THREE-part column cannot honour
its (1,2) pair because the repair walk permutes only the last position.
Two-part columns — every blood pressure, every ratio — are unaffected,
which is why four reads did not meet it. They belong to L7, which
reopens that walk anyway, and half-fixing them inside a landing about
an unrelated claim would have been the worse trade.

**Measured after the repair:** 32 of 32 attack wordings caught, 7 of 7
honest wordings clean, zero offenders on the whole governed tree, every
guard mutation-verified.

---

## The review as written

## Round 4 items

1. **SEVERITY: blocking — the disposition seal does not detect deletion.**

   **CONCRETE FAILURE SCENARIO:** Delete the newly sealed `part_above` disposition row. The guard converts the seal to a set and asks only whether each remaining passage is known. My in-memory deletion left zero unknown passages; the deleted digest merely remained stale in the seal. The suite therefore need not turn red when a governing obligation is removed. See the [one-directional comparison](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p2c4f1_disposition_registry.py:275>).

   The volume statement is also inaccurate: version 6 currently contains 2,191 passage instances and the seal stores 1,987 unique digests, neither 1,989. The manual seal command reports current, but it is not an enforced test of exact equality.

2. **SEVERITY: blocking — the grammar-count guard remains non-exhaustive.**

   **CONCRETE FAILURE SCENARIOS:**

   - Add a duplicate NG48 appendix row. The appendix grows from 48 to 49 rows, but `_appendix()` collapses it into the same dictionary and every count input remains unchanged.
   - Add “The note grammar contains 47 forms.” None of the five patterns recognizes that shape; every existing pattern still matches elsewhere, so the asserted non-vacuity does nothing.
   - Change all three breakdowns consistently from 66 whole-number positions and 4 package-word positions to 65 and 5. They still sum to 79, agree with one another, and retain five bound positions, so the guard accepts the false classification.

   The unresolved dictionary collapse is at [_appendix](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p4d27_note_grammar_matches_the_code.py:142>); the closed pattern inventory and self-consistency-only breakdown are at [the count guard](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p4d27_note_grammar_matches_the_code.py:262>).

3. **SEVERITY: blocking — the validator does not enforce `parts[]` “field by field.”**

   **CONCRETE FAILURE SCENARIO:** Start with joined readings whose first position uses plain spellings `100`, `200`, and `300`. In the checked file, retain `100` but rewrite every `200` and `300` as `200.0` and `300.0`. Numeric values, endpoints, minimum width, distinct counts, integer status, rank agreement, above-count, separator, and row counts remain unchanged. The published `numeric_styles` and `fraction_widths` are wrong, but `_joined_part_checks` checks only the two endpoints and `integer_valued`, so the quality report can miss the mismatch.

   This contradicts the contract’s [unchanged field-by-field disposition](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6838>) and even the validator docstring’s assertion that the average is checked. The actual return path is at [_joined_part_checks](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/validation.py:6640>).

4. **SEVERITY: blocking — the generation report omits every joined-role approximation.**

   **CONCRETE FAILURE SCENARIO:** Generate a profile containing only a joined column. Its per-position interior rungs and moments are approximated, and `part_agreements` is explicitly approximated. `_approximations()` has no `JoinedFacts` branch and returns an empty list. The report can consequently say the twin has no approximated fact at all instead of printing the published value, achieved value, and bound promised by section 9.4a.

   See the [missing dispatch](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/generation.py:13968>) and the [report guarantee](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/rendering.py:1521>).

5. **SEVERITY: blocking — three-part joined columns cannot honor every published pair.**

   **CONCRETE FAILURE SCENARIO:** Profile `1-100-50`, `2-99-50`, …, `100-1-50` under `--measurement`. Positions one and two have rank agreement −1 and a nonzero published above-count. Generation sorts both positions ascending, giving agreement +1 and above-count zero. The repair walk permutes only the last position; pair `(1,2)` is never scored or moved.

   The omission is explicit in [the pair selection](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/generation.py:4617>). Validation will report the miss if run, but item 4 leaves the generation report silent.

6. **SEVERITY: blocking — section 9.4a contains three false disposition statements.**

   **CONCRETE FAILURE SCENARIOS:**

   - With 90 joined cells and 10 accepted unsplit cells, the twin contains 10 text stand-ins. Therefore `n_parts` is not true of “every present cell”; it is true only of the `n_joined` cells.
   - `part_min_widths` contains one minimum per position, not “the smallest and largest written width.” The minimum itself is produced and compared exactly; no maximum is published.
   - The agreement window is not stated in the validation method. The code cites Phase 4 plan P4-D25, while both method specifications contain no joined-agreement clause.

   These assertions are together in [section 9.4a](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6835>).

7. **SEVERITY: blocking — the exemption guard remains unsound in both directions and still misses ordinary wording.**

   **CONCRETE FAILURE SCENARIOS:** Direct matcher probes produced these results:

   - “The twin is exempt from data-use agreements. The generator has deterministic rules. They still apply.” returned no offender because `they` excused the first claim across a bridge.
   - “Privacy rules govern generated files. These converters read CSV files. They do not apply to Parquet.” returned an offender even though `they` refers to the converters.
   - “Privacy rules cease to apply to synthetic twins,” “Synthetic records are excluded from institutional policy,” and “Institutional policy is inapplicable to synthetic records” all returned no offender.

   Bare plural pronouns remain in the supposedly plain set and retain window-distance carry and cure authority. See [the reference sets and walks](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6505>).

8. **SEVERITY: blocking — the joined-number wording repair still missed governing and executable surfaces.**

   **CONCRETE FAILURE SCENARIO:** Call `why_joined_is_worth_asking(["1:1.5"])`. It returns the joined-question reason, while its docstring says every part is a whole number. The governing Phase 4 amendment likewise says the role is taken only where cells are whole numbers, so an implementer following the ratified plan rejects a case the shipped producer accepts.

   The stale claims remain in [asking.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/asking.py:138>) and [the Phase 4 plan](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/plans/phase-4-columns.md:5141>). NF47 also names the retired `splits_into_wholes` symbol at [contract line 1347](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:1347>).

9. **SEVERITY: blocking — the mandatory state record contradicts the owner’s five-round ruling.**

   **CONCRETE FAILURE SCENARIO:** The next agent reads STATE first and obeys its instruction that three rounds are the maximum. They stop reviewing this landing and never perform rounds 4 or 5, contrary to the ruling supplied for this review. The round-3 record also declares itself final and says no round 4 will run.

   See [STATE](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/STATE.md:71>) and the [round-3 record](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/plans/reviews/phase-4-obligations-review-round-3.md:5>).

## Checked

- Read both repository briefs, STATE, all three prior records, and the complete diff from `792e380`.
- Traced joined profiling, loading, generation, validation, quality checks, generation-report measurement, and three-part pairing.
- Mutation-checked the grammar guard for an unmatched count sentence, a duplicate appendix row, and a consistently false class breakdown.
- Counted seal coverage, ran the seal command read-only, and mutation-checked deletion of an exact disposition.
- Probed the exemption matcher directly in both carry/cure directions and against additional ordinary wordings.
- Searched all governed and implementation surfaces for the retired joined-number wording and symbol.
- Ran `git diff --check` and the decontamination scanner; both returned clean.
- Inspected security/offline boundaries and found no new I/O, subprocess, native-call, or dynamic-loading path.
- Did not run pytest and did not modify any file.

**Verdict: reject — blocking items 1–9.**
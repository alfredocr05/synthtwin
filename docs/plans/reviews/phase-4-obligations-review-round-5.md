# Phase 4 — the obligations landing, adversarial review round 5

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only, 2026-08-26.
**Verdict: REJECT**, six blocking. **This is the fifth and last round**
under the owner's cap. Rounds 1-5 returned 11, 11, 7, 9 and 6 items and
**every one was real**.

**THE ROUND'S MOST IMPORTANT ITEM IS THAT MY ROUND-4 REPAIR MADE THINGS
WORSE, and it is why that repair is now WITHDRAWN.** Round 4 caught a
twin report saying "This twin has no approximated fact at all" of a
joined column whose every position is approximated. The branch built to
fix it printed, on a three-value column measured directly:

- per-position comparisons of `n_distinct` and `n_distinct_folded`,
  which the profile publishes for NO position — they are the whole
  CELL's counts, inherited through `_part_view`;
- both positions as "this column", with `percentiles.p01` appearing
  twice at different values and nothing saying which position either
  belonged to;
- an unsplit stand-in `text-1` measured into position two, because it
  splits on `-`;
- and no measurement of `part_agreements` at all — the one fact this
  role's own decision calls approximated.

**A report printing ambiguous numbers is worse than one printing
none.** The branch is withdrawn, the contract now states the silence as
the defect it is, and the whole cluster is residual R-P4-44 for the
joined role's own landing. Restoring a recorded defect beats shipping a
half-built repair, and the measurement is what settled it rather than
the argument.

**The other five, all repaired:**

| item | what it was | how it was closed |
|---|---|---|
| 4 | the seal reduced passages to a SET, so a document carrying the same sentence twice could lose one copy with neither direction firing | the seal now records each document's passage COUNT beside its digests; mutation-verified by deleting one copy of a duplicated row |
| 5 | number agreement did not settle pronoun identity, and broke in BOTH directions | **no pronoun rule survived three rounds of contact.** A cure must now NAME the regime — which is sound, and is better prose, so this repository's own sentences were rewritten to name it |
| 6 | a breakdown falsified consistently at every site still passes | recorded as R-P4-45 rather than closed, and the reason is real: the contract is now INSIDE the seal, so a coordinated edit of three breakdown sentences moves three sealed passages and needs a counted re-seal |
| 1, 2, 3 | the withdrawn branch | withdrawn; R-P4-44 |

**The reviewer also ruled on the deferrals, having been right about
R-P4-25 in round 3:** none needs pulling into this landing for
sequencing, R-P4-42 belongs to L10 and R-P4-43 and the three-part
pairing defect to L7 — but all are **Phase 4 close blockers**, not
acceptable release residuals. That ruling is carried into the close
list.

**Measured after the repair:** 33 of 33 attack wordings caught, 8 of 8
honest wordings clean, zero offenders on the whole governed tree.

---

## The review as written

# Verdict: reject

Blocking items 1–6 remain.

## Items

1. **SEVERITY: blocking — pair agreement is still absent from the generation report.**

   **CONCRETE FAILURE SCENARIO:** Generate a two-position blood-pressure twin whose profile publishes `part_agreements[0]`. The contract classifies it as approximate and promises its published value, achieved value, and range in the report. The new branch measures only each position’s numeric facts and returns without measuring any pair. No `part_agreements` record is produced.

   Direct probing returned zero agreement records. See [generation.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/generation.py:14044>) and the governing promise in [profile-contract-v6.md](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6843>).

2. **SEVERITY: blocking — positions are unnamed and inherit cardinalities the profile never publishes for them.**

   **CONCRETE FAILURE SCENARIO:** Use joined cells `1-10`, `1-20`, `1-30`. Position one is constant; the whole joined column has three distinct cells. The report prints for the first position:

   - `n_distinct`: description says 3; twin holds 1
   - `n_distinct_folded`: description says 3; twin holds 1

   Those are not published per-position facts. They are the whole-cell counts inherited through `_part_view`. `_numeric_approximations` appends them unconditionally at [generation.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/generation.py:13276>).

   The report also prints both positions as the same column and repeats names such as `mean` without a position index; [rendering.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/rendering.py:943>) has no way to distinguish them. An all-null ladder emitted only these four invented cardinality records—two per position.

3. **SEVERITY: blocking — an unsplit stand-in can be measured as a joined cell.**

   **CONCRETE FAILURE SCENARIO:** Profile 100 `-`-separated cells where 99 split into two numbers and one does not. This satisfies the default parse line. Generation writes the unsplit stand-in `text-1`. `_split_written("text-1", "-")` returns `["text", "1"]`, so the report admits the invented `1` into position two.

   The position was built over 99 joined cells, but its report is measured over 100 values. In a direct probe this shifted the second position’s rungs and moments and produced false outside-range outcomes. The length-only admission is at [generation.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/generation.py:14068>).

4. **SEVERITY: blocking — the seal still loses passage multiplicity.**

   **CONCRETE FAILURE SCENARIO:** Delete the `free_text` row stating that `n_distinct` and `n_distinct_folded` are exact at [profile-contract-v6.md](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:6987>). An identical row remains under `numeric_unrepresentable` at line 7027.

   I simulated that deletion from the passage sequence: the row count fell from two to one, while the forward check reported zero unknown passages and the reverse check reported zero orphaned digests. Both the seal generator and reverse check reduce passages to sets at [seal.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tools/dispositions/seal.py:85>) and [test_p2c4f1_disposition_registry.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p2c4f1_disposition_registry.py:352>).

5. **SEVERITY: blocking — number agreement does not settle pronoun identity.**

   **CONCRETE FAILURE SCENARIO:** Add:

   > The twin is exempt from data-use agreements. Its output formats have rules, and they still apply.

   The matcher returns no offender. `they` agrees in number with “agreements,” but refers naturally to the nearer formatting rules. The unrelated sentence therefore cures the banned claim.

   The opposite direction also fails: “Privacy policy and institutional approval do not apply to synthetic twins. They still apply.” is reported despite withdrawing the claim, because `_named_text` selects the first singular match and rejects plural `they`. Both outcomes were reproduced directly. See [test_claim_inventory.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6636>).

6. **SEVERITY: blocking — round 4’s consistently false argument-class breakdown remains accepted.**

   **CONCRETE FAILURE SCENARIO:** Change all three grammar summaries from 66 whole-number positions and 4 package-word positions to 65 and 5. The totals still equal 79 and all copies agree. The guard passes.

   I mutation-verified this in memory. The current check derives the total and bound-affix count but deliberately checks the other classes only for agreement and arithmetic at [test_p4d27_note_grammar_matches_the_code.py](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p4d27_note_grammar_matches_the_code.py:327>). Thus the third failure scenario from round 4 was not repaired.

## Deferred joined-role defects

None needs to be pulled into L0 solely for sequencing, but all remain Phase 4 close blockers:

- R-P4-42 fits L10, where the arithmetic method clauses are scheduled. The current public plan sends it to L10, not L7.
- R-P4-43 fits L7 because that landing adds per-position numeric census and validator work.
- The three-part pairing defect also fits L7 because that landing reopens the position draw and pairing walk.

They are acceptable intermediate deferrals on this unreleased branch, not acceptable release residuals.

## Checked

| Surface | Verification |
|---|---|
| Full scope | Read both briefs, STATE, all four prior records, and the complete staged diff from `792e380`. |
| Joined bounds | Traced construction and reporting through `_part_view`, `_numeric_layout`, `_numeric_content`, `_split_written`, `_numeric_approximations`, and rendering. Genuine split cells use the same deterministic layout; stand-in population selection and cardinality routing do not. |
| Joined edge cases | Directly probed ordinary positions, a constant position, an all-null ladder, and an unsplit stand-in colliding with `-`. |
| Seal | Confirmed the generated seal is current; counted duplicate passages and simulated removal of an exact duplicated obligation. |
| Pronouns | Existing battery: 32/32 attacks caught, 7/7 honest cases accepted, zero current-tree offenders. Both new number-rule probes failed as described. |
| Grammar | Current contract has 48 unique defining clauses and 48 unique appendix rows, both totaling 79 positions. The consistent 65/5 class mutation passed. |
| Offline boundary | Source audit checked 17 product modules with zero violations. `_split_written` has both recognized type checks before its method call. No other added product-code call has the same untraced-method shape. |
| Hygiene | Decontamination scan clean; `git diff --check 792e380` clean. |
| Constraints | No file was written or modified. Pytest was not run. |
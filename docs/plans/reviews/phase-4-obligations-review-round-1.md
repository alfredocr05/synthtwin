# Phase 4 — the obligations landing, adversarial review round 1

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only, 2026-08-26.
**Target:** the commit adding the seventh claim family and `docs/STATE.md`.
**Verdict: REJECT**, six blocking items.

**Every item was verified before it was repaired, and three were
verified by measurement rather than by reading:**

| item | verified how | outcome |
|---|---|---|
| 1 the tracked tree scans dirty | ran the scanner on the committed tree | **TRUE.** `test_repo_tree_is_clean_under_real_manifest` failed. The earlier green run was made while the file was still UNTRACKED, so it was never scanned. Repaired, and the lesson is now rule 1 of the state page. |
| 2 claim carried across a statement boundary | fed the reviewer's own sentence to the matcher | TRUE. Repaired with a bound carry into the next statement. |
| 3 phrase inventories miss ordinary prose | fed all four wordings | TRUE, four of four walked past. All four are now in the vacuity floor. |
| 4 the two pages outside every ban | read `DEFENCE_SURFACES` | TRUE. Both added. |
| 5 cure by proximity, not meaning | fed both scenarios | TRUE. The cure and the carry are now bound to the obligation, and the in-statement cure is directional. |
| 6 true scoped statements refused | fed the reviewer's sentence | TRUE as a risk, and it MATERIALIZED during the repair on a different sentence — see below. |
| 7 the disclosure sentence is false | profiled a free-text column | **TRUE.** `free_text`, `identifier` and `numeric_unrepresentable` publish no value at any floor. The sentence is corrected. |
| 8 an open decision recorded as settled | read residual R-P4-23 | TRUE. The ruling is recorded and the entry now points at it. |
| 9 freshness is only a promise | read the tree for a check | TRUE. The suite size is now compared against a whole-suite run. |
| 10 the family test counts banners, not families | renamed one family's tests | TRUE, it passed. Every banner must now carry a test of its own. |
| 11 "roughly sixty commits" | `git rev-list --count` | TRUE, it is 84. Corrected. |

**THE MOST USEFUL THING THIS ROUND PRODUCED IS ITEM 6, BECAUSE IT CAME
TRUE WHILE THE REPAIR WAS BEING MADE.** Widening the obligation names
to a bare `approval` — with a comment ARGUING it was safe — reported
this contract's own honest sentence, "a privacy approval given for an
earlier description does not cover a marked row", as the banned claim.
That sentence says an obligation reaches FURTHER than a reader might
think, which is the opposite of an exemption. The widening is
withdrawn and the shape is named instead of the noun broadened. The
comment that asserted safety without measuring is replaced by one that
records the measurement that refuted it.

**Round 2 is owed on the repair**, since six blocking items moved.

---

## The review as written

## Items

1. **SEVERITY: blocking — the commit violates decontamination.**

   **CONCRETE FAILURE SCENARIO:** `docs/STATE.md:80` contains the denied three-letter abbreviation for a review board, and the commit message repeats it. The scanner walks every tracked file, so `test_repo_tree_is_clean_under_real_manifest` will scan that line and return nonzero. Consequently, the stated “3,851 passed” result cannot describe this committed tree. Removing the line later would not remove the term from this commit’s message/history.

2. **SEVERITY: blocking — ordinary banned claims cross a statement boundary undetected.**

   **CONCRETE FAILURE SCENARIO:** Add:

   > Data-use agreements govern source tables. They do not apply to synthetic twins.

   `_STATEMENT_END` separates the sentences. The first names the obligation but has no exemption marker; the second has the exemption marker but no repeated obligation name. `_grants_an_exemption` returns no offender. This repeats the fourth family’s prior one-statement failure despite that lesson being cited in the new comments.

3. **SEVERITY: blocking — the phrase inventories miss natural formulations.**

   **CONCRETE FAILURE SCENARIOS:**

   - “Synthetic twins are exempt from regulatory requirements.” The exemption matches, but “regulatory requirements” is absent from `_OBLIGATION_NAMES`.
   - “Synthetic files need not comply with institutional policy.” Neither “need not comply” nor singular “institutional policy” is covered.
   - “Approval is unnecessary when the table is synthetic.” Bare approval and “is unnecessary” are both missed.
   - “Synthetic output is outside the review board’s jurisdiction.” The obligation is named, but “is outside” is not `falls outside`.

   These are normal prose, not contrived encodings. The six vacuity examples merely prove six listed shapes remain listed; they do not establish compositional coverage.

4. **SEVERITY: blocking — required public documents are outside the guard.**

   **CONCRETE FAILURE SCENARIO:** Put “The twin is exempt from compliance requirements” in `docs/STATE.md` or `STATUS.md`. Neither file belongs to `DEFENCE_SURFACES`, so the seventh-family test never reads it. This is especially material for `docs/STATE.md`, which CLAUDE.md now makes the mandatory first read and which itself claims the seventh family guards the rule.

5. **SEVERITY: blocking — the cure suppresses real defects by proximity, not meaning.**

   **CONCRETE FAILURE SCENARIOS:**

   - “The twin is exempt from data-use agreements. Cross-column facts are absent. The small-group publication rule still applies.” The unrelated “still applies” occurs within 300 characters and cures the first sentence.
   - “Privacy rules still apply to the source, but synthetic outputs are exempt from those privacy rules.” The earlier clause’s cure marker causes the whole statement to be skipped even though its final clause makes the banned claim.

   The cure is not tied to the same obligation, the same subject, or the direction of the assertion.

6. **SEVERITY: serious — true scoped statements will become false positives.**

   **CONCRETE FAILURE SCENARIO:** A future installation section says:

   > No review is required by the package installer; institutional requirements may govern generated files.

   The guard combines “no review is required” with “institutional requirements” and rejects the sentence, although the clauses concern different subjects and the second preserves the obligation. The implementation detects co-occurrence, not a claim that synthetic status caused an exemption.

7. **SEVERITY: serious — CLAUDE.md’s disclosure assertion is false.**

   **CONCRETE FAILURE SCENARIO:** Profile a table containing a free-text column with unique narrative values at the default floor of one. The contract and README state that free-text values are never published; only shape facts are retained. Nevertheless, `CLAUDE.md:171-173` now says every value in the table is named with its row count. Identifier and unrepresentable-number columns provide further counterexamples. A decision-maker relying on that sentence receives an inaccurate account of what the description carries.

   The surrounding provenance claim remains properly qualified: values are derived from the profile, and equality with a real row is not ruled out. The five-file handling rule also remains intact.

8. **SEVERITY: blocking — STATE.md records an unresolved version decision as settled.**

   **CONCRETE FAILURE SCENARIO:** `docs/STATE.md:46-47` tells the next agent not to reconsider extending version 6 before release. But residual R-P4-23 at `docs/plans/phase-4-columns.md:5531-5553` says the proper repair is a version bump and explicitly leaves acceptance or withdrawal of the in-place-extension argument to the owner. Following STATE.md causes an older version-6 description missing a later key to receive a generic missing-key refusal instead of the intended migration guidance.

9. **SEVERITY: serious — STATE.md freshness is only a promise.**

   **CONCRETE FAILURE SCENARIO:** A later commit adds one test or closes a residual without touching `docs/STATE.md`. No test or CI rule compares changed work with a changed STATE.md, so every gate can pass while its suite count or open-work section remains stale. This commit follows the same-commit rule once; nothing enforces the next commit.

10. **SEVERITY: minor — the family-counting test does not count families.**

    **CONCRETE FAILURE SCENARIOS:**

    - Add an eighth family in the module docstring, like the first two, while retaining the five recognized comment banners and the literal “SEVEN FAMILIES…” string. The test passes.
    - Delete the seventh family’s guard, constants, and behavioral tests but retain its banner and the banner-counting test. The test passes.

    It asserts one hard-coded tuple against another hard-coded sentence, not the presence of functioning family tests.

11. **SEVERITY: minor — one STATE.md history count is inaccurate.**

    **CONCRETE FAILURE SCENARIO:** STATE.md attributes the lint drift to “roughly sixty commits” since `af2da86`; `git rev-list --count af2da86..792e380` returns 84. A maintainer using that range estimate to divide or audit the lint regression searches a materially shorter history than the actual one.

## Checked

- Read `AGENTS.md`, `CLAUDE.md`, the full target diff, the parent state, and the relevant fourth-family mechanics.
- Traced `SURFACES`, `DEFENCE_SURFACES`, statement splitting, phrase matching, carried claims, and cure direction.
- Checked the decontamination scanner’s tracked-file traversal without executing the suite.
- Compared the new README and CLAUDE.md text with the record-provenance qualification, five-file inventory, default floor, and nothing-publishing roles.
- Compared STATE.md with the Phase 4 amendments and residual triage. The 15 deliberate, 11 large, and 7 owner counts agree with the plan.
- Verified the branch is clean, the target is not merged into `main`, branch protection is recorded as active, the release remains parked, and only the CI workflow exists.
- Did not run pytest. The exact lint totals have no committed result artifact, so I did not independently accept them as verified current facts.

Verdict: reject — blocking items 1–5 and 8 named above.
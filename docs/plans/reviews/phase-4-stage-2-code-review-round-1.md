<!-- Phase 4 stage 2 code review, round 1. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-19. Paths are repository-relative.
Wording was adjusted only where the repository's vocabulary scanner
required it; no meaning was changed. -->

# Phase 4 stage 2 code review — round 1

1. **P4-C1-F1 — SEVERITY: blocking. The report falsely claims invented columns meet facts that the same report records as missed.**

   **CONCRETE FAILURE SCENARIO:** Load the contract-valid, one-character declared-identifier profile used by the existing owner-decision-6 test. Generation preserves the one-character width but repeats identifiers, missing `n_distinct`, `n_distinct_folded`, and `n_distinct_by_occurrences`. Its column block nevertheless says the twin “meets its counts, lengths and shapes,” and the page foot says made-up values “carry the counts and shapes.” The same report therefore claims both that the counts were met and that three were missed.

   A `numeric_unrepresentable` column exposes the same overgeneralization differently: its contract deliberately publishes no length or width, yet it receives the sentence saying its “lengths” were met.

   **EVIDENCE:** P4-D2 requires the sentence to say that only published facts were matched, not that every published fact was successfully met (`docs/plans/phase-4-columns.md:424-430`). The known identifier counterexample and its three deviations are established at `tests/test_generation.py:1211-1238`. The false new claims are at `src/synthtwin/rendering.py:572-578` and `src/synthtwin/rendering.py:1528-1530`. The unrepresentable role’s deliberate lack of width is stated at `src/synthtwin/contract.py:1017-1024` and implemented at `src/synthtwin/generation.py:7308-7370`.

2. **P4-C1-F2 — SEVERITY: serious. The report still says invented source values were reproduced.**

   **CONCRETE FAILURE SCENARIO:** Generate a twin containing an ordinary nonempty `free_text` column. Before reaching that column’s new loud-decline sentence, the column section says, without qualification, “The twin reproduces the values and the counts.” The block then says all of those values were made up because the description publishes none. A reader receives mutually contradictory provenance claims on one page.

   **EVIDENCE:** P4-D2 requires every affected surface to say what was invented and acceptance requires that no surface still imply the content was measured beyond published facts (`docs/plans/phase-4-columns.md:397-422`, `docs/plans/phase-4-columns.md:1694-1703`). The retained universal preamble is at `src/synthtwin/rendering.py:1485-1491`; the contradicting free-text sentence is at `src/synthtwin/rendering.py:569-578`. “THIS RAISES … and lowers nothing” does not authorize retaining a false pre-existing sentence (`docs/plans/phase-4-columns.md:467-472`).

3. **P4-C1-F3 — SEVERITY: blocking. A label column containing only invented cells is counted and described as partly invented.**

   **CONCRETE FAILURE SCENARIO:** Use a floor of 11 and a constant column with four present copies of one label and forty missing cells. The producer validly emits `levels == []` and `suppressed_rows == 4`; generation writes four neutral labels. Every present twin cell is invented. `_made_up_class` assigns `HELD_BACK`, however, so the screen and page foot report zero wholly invented columns and one column holding “some made-up cells beside values your description publishes.” There are no such beside-values.

   The same failure occurs with no suppressed level when a published folded label has `variants == {}` and `variants_withheld` covering every row: generation invents every spelling, but the column remains in the partial bucket.

   **EVIDENCE:** The constant-below-floor shape is already demonstrated at `tests/test_taxonomy.py:56-61`; the contract explicitly permits every level to be suppressed at `docs/spec/profile-contract-v4.md:828-856`. It also permits a published label with no published spelling at `docs/spec/profile-contract-v4.md:1454-1481`. Generation writes the invented variants and levels at `src/synthtwin/generation.py:4287-4300` and `src/synthtwin/generation.py:4320-4324`. Classification and aggregation place both shapes in the partial bucket at `src/synthtwin/rendering.py:525-531` and `src/synthtwin/rendering.py:611-620`; the false screen/report wording is at `src/synthtwin/rendering.py:642-646` and `src/synthtwin/rendering.py:1517-1526`. P4-D2 item 2 requires an actual count of columns holding only invented values versus those holding some (`docs/plans/phase-4-columns.md:431-437`).

   P4-D2’s role-based class description does not settle this edge consistently with item 2. The plan must be amended to define it before the implementation silently chooses a meaning.

4. **P4-C1-F4 — SEVERITY: serious. Two per-column class sentences omit a clause P4-D2 requires.**

   **CONCRETE FAILURE SCENARIO:** A reader opens the block for a categorical column with seven suppressed cells, or a numeric column with one nonnumeric straggler, and stops at the next column—as the renderer’s own placement comment anticipates. The block says stand-ins were made but never says that a number computed from invented content means nothing about the real table. That warning appears only for fully invented columns and in a generic page-foot paragraph much later.

   **EVIDENCE:** P4-D2 item 1 requires each affected column’s class line to state the construction, the published-fact boundary, and that numbers computed on invented content mean nothing (`docs/plans/phase-4-columns.md:424-430`). The fully invented branch carries that clause at `src/synthtwin/rendering.py:569-578`; the held-back and uncarried branches omit it at `src/synthtwin/rendering.py:580-607`. The code itself says the per-column placement exists for a reader who stops early (`src/synthtwin/rendering.py:1176-1179`), so the later footer at `src/synthtwin/rendering.py:1528-1530` is not equivalent.

5. **P4-C1-F5 — SEVERITY: blocking. Every new sentence bypasses the ratified enumerated grammar.**

   **CONCRETE FAILURE SCENARIO:** A future edit directly changes the made-up warning, a per-column continuation, or the profiler-summary claim and adds arbitrary free-form prose. No note form or rendered branch needs to change, and the profile publication guard cannot reject it. This is exactly the publication route P4-D2 forbids.

   **EVIDENCE:** P4-D2 unambiguously says every new sentence uses “a new note form plus a rendered branch per sentence” and that no free-form text can be published (`docs/plans/phase-4-columns.md:467-469`). The existing taxonomy grammar describes itself as controlling sentences in the finished profile document (`src/synthtwin/taxonomy.py:480-504`, `src/synthtwin/taxonomy.py:567-571`); that historical scope does not narrow the later P4-D2 requirement. The new report and screen text are assembled directly at `src/synthtwin/rendering.py:558-607` and `src/synthtwin/rendering.py:624-647`; the new summary prose is a list of plain strings at `src/synthtwin/summary.py:1054-1070`. No grammar form was added.

   The fact that the shipped renderer already contains older free-form report prose accounts for the architectural mismatch; it does not amend the ratified sentence. This requires either grammar-backed implementation or a ratified plan amendment.

6. **P4-C1-F6 — SEVERITY: serious. The required exact-shape and surface-reachability coverage is incomplete.**

   **CONCRETE FAILURE SCENARIOS:**

   - Delete the CLI call at `src/synthtwin/cli.py:1301`. The new tests still pass because they call `rendering.made_up_warning` directly rather than invoking `generate`.
   - Delete or arbitrarily rewrite the profiler-summary addition at `src/synthtwin/summary.py:1065-1068`. The new test file neither imports nor renders `summary`.
   - Change the continuation lines of the uncarried sentence while preserving its first count line. The assertions still pass because they check only substrings.
   - Omit `n_out_of_range` or `n_contradictory`, or mishandle a variant-only label. The fixture reaches only a nonnumeric numeric straggler and a suppressed level.

   **EVIDENCE:** Exact-shape tests and claim-inventory verification of the summary are explicit obligations at `docs/plans/phase-4-columns.md:457-472`. The test imports only rendering-side modules at `tests/test_p4d2_loud_decline.py:65-77`; count assertions are substring tests at `tests/test_p4d2_loud_decline.py:260-269` and `tests/test_p4d2_loud_decline.py:289-304`. Its fixture describes only one nonnumeric numeric cell and one suppressed label at `tests/test_p4d2_loud_decline.py:134-140` and `tests/test_p4d2_loud_decline.py:160-172`. The agreement test at `tests/test_p4d2_loud_decline.py:325-335` checks two outputs of the same classifier and therefore cannot expose a shared misclassification such as P4-C1-F3.

   The report golden is exact for its one fixture, but it covers fully invented, suppressed-label, and footer branches only; it does not supply exact shapes for the screen, summary, or uncarried branch.

   The two recorded mutation measurements are honestly described as measurements, and the other two claims name plausible red mechanisms rather than pretending they were measured. That honesty does not satisfy the missing surface and exact-shape obligations.

7. **P4-C1-F7 — SEVERITY: blocking. Stage 2 began before its ratified phase-state gate was executed.**

   **CONCRETE FAILURE SCENARIO:** At `ec941f6`, users receive Phase 4 behavior and a Phase 4 changelog while the public project brief still says the current phase is Phase 3, the README still labels the project Phase 3, and STATUS says Phase 4 has not started. The pinned claim-inventory expectation still requires those stale statements.

   **EVIDENCE:** The plan says implementation from stage 2 onward starts only after Phase 3’s closing state is settled, and says the phase ledger, README, and claim-inventory statements move in stage 2’s first commit (`docs/plans/phase-4-columns.md:169-175`; see also `docs/plans/phase-4-columns.md:1248-1252`). The contradictory current statements remain at `CLAUDE.md:225-245`, `README.md:3-10`, and `STATUS.md:27-34`; the inventory remains pinned to Phase 3 at `tests/test_claim_inventory.py:743-749`. None is in the reviewed diff.

8. **P4-C1-F8 — SEVERITY: wording. The golden’s cause comment mislabels a declared identifier as free text.**

   **CONCRETE FAILURE SCENARIO:** A later reviewer uses the cause-naming comment to determine which class the golden exercised and concludes that both `record_code` and `comment` covered the free-text role. `record_code` is explicitly declared and therefore exercises the identifier role.

   **EVIDENCE:** The fixture declares `record_code` at `tests/test_twin_golden.py:102-114`; declaration is the exclusive identifier route at `src/synthtwin/taxonomy.py:3647-3655`. The new comment groups “`record_code` and `comment` (free text …)” at `tests/test_twin_golden.py:481-490`.

## VERDICT

**REJECT.** Blocking items: **P4-C1-F1** (false exactness claims), **P4-C1-F3** (wrong only-versus-some classification), **P4-C1-F5** (enumerated-grammar breach), and **P4-C1-F7** (unmet stage gate). P4-C1-F3 requires a ratified plan amendment because the existing class description and item-2 count wording disagree on all-withheld label columns.

## What was checked

- Reviewed the complete `5a5c3f8..ec941f6` diff and all six touched files.
- Traced every contract-permitted role/axis path, including declared and declared-empty columns, `numeric_unrepresentable`, constant-below-floor, label suppression, variant-only withholding, datetime with overlapping universal class counts, and numeric K/O/C/N combinations.
- Verified `_uncarried_cells` against generation: datetime writes exactly `n_unparsed` stand-ins (`src/synthtwin/generation.py:4024-4114`); numeric generation writes stand-ins for O/C/N and not K (`src/synthtwin/generation.py:3380-3454`).
- Verified `_held_back_cells` arithmetic: occurrence size multiplied by the number of spellings matches the label generator. `occurrence_size(None)` would be skipped, but a loaded profile cannot reach that state because the loader rejects non-decimal multiplicity keys (`src/synthtwin/contract.py:1918-1952`, `src/synthtwin/contract.py:1955-1981`, `src/synthtwin/contract.py:3609-3627`).
- Checked page-foot, screen, and per-column count derivation. They share one classifier and agree mechanically; P4-C1-F3 shows that shared agreement can still be wrong.
- Checked offline and security properties: no new imports, regex, network, subprocess, native-call, dynamic-loading, prohibited method-call, or list-growth path. The offline scanner checked 16 product files with zero violations.
- Checked display boundaries: report and summary cross `visible_lines`, `_warn` applies the screen boundary, and the new classifier output contains only first-party prose and counts.
- Checked determinism: profile order and sorted multiplicity keys are used; no random source or environment input was added.
- Confirmed `made_up_warning` is a public, documented module function.
- Confirmed item 3, the quality-report work, was not touched.
- Confirmed exit code 0 remains unchanged.
- Confirmed the description and twin golden digests did not move and no generation code changed; the comment’s substantive “no twin byte moved” claim is true.
- Ran the decontamination scanner read-only; it exited successfully with no scanner concern.
- Did not run pytest, as instructed.
<!-- Phase 4 stage 2 code review, round 2. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-19. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it. -->

# Phase 4 stage 2 code review — round 2

## Round-1 verification

- **P4-C1-F1 — CLOSED.** The achievement claim was replaced with “built to meet,” with deviations named separately (`src/synthtwin/rendering.py:587-608`, `1577-1580`).
- **P4-C1-F2 — CLOSED.** The column preamble now distinguishes published values from synthtwin’s constructions (`src/synthtwin/rendering.py:1530-1540`).
- **P4-C1-F3 — CLOSED as a classifier/count defect.** `_how_much` promotes an all-invented label column to `EVERYTHING` (`src/synthtwin/rendering.py:513-550`). The amendment’s unimplemented summary consequence is fresh item P4-C2-F1.
- **P4-C1-F4 — CLOSED.** Held-back and uncarried branches now carry the required computation warning (`src/synthtwin/rendering.py:629-631`, `646-648`).
- **P4-C1-F5 — NARROWED.** A-P4-3 formally scopes the grammar, but materially understates the resulting control gap; see P4-C2-F2.
- **P4-C1-F6 — NARROWED.** CLI reachability, summary coverage and exact class lines were added, but the screen shape and variant-only path remain insufficiently guarded; see P4-C2-F2 and P4-C2-F4.
- **P4-C1-F7 — STILL OPEN.** The Phase 3 gate remains unmet; see P4-C2-F3.
- **P4-C1-F8 — CLOSED.** The golden now identifies `record_code` as declared (`tests/test_twin_golden.py:487-490`). A new contradiction later in the same comment is P4-C2-F5.

## Numbered review items

1. **P4-C2-F1 — SEVERITY: blocking. The profiler summary omits fully invented label columns created by A-P4-2.**

   **CONCRETE FAILURE SCENARIO:** At the default floor of 11, profile a constant column with four present copies of one neutral label and forty missing cells. The valid profile has `role == constant`, `levels == []`, and `suppressed_rows == n_present == 4`. A-P4-2 and `_made_up_class` correctly put it in `EVERYTHING`; its report and screen count it as wholly invented. The profiler summary does not: its invention paragraph is reached only for identifier, free-text, and unrepresentable roles. The person therefore sees no forward sentence saying every present twin cell of this newly defined fully-invented column will be made up.

   The second A-P4-2 edge fails similarly: a published label with `variants == {}`, `variants_withheld` covering every row, and no suppressed level is `EVERYTHING` by cells, but still never enters the summary’s `without_values` list.

   **EVIDENCE:** A-P4-2 makes every all-invented label column fully invented regardless of role (`docs/plans/phase-4-columns.md:1698-1724`), and P4-D2 item 4 requires the summary sentence for fully-invented columns (`docs/plans/phase-4-columns.md:459-463`). The contract permits empty published levels and accounts all label cells through `covered + suppressed_rows == n_present` (`src/synthtwin/contract.py:3424-3430`, `3558-3568`). The renderer implements the amended class (`src/synthtwin/rendering.py:513-550`), but the summary’s closed role list excludes all label roles (`src/synthtwin/summary.py:47-60`) and constructs `without_values` from that role list alone (`src/synthtwin/summary.py:956-970`, `1030-1068`). The new all-withheld test exercises only the report and totals, never the summary (`tests/test_p4d2_loud_decline.py:463-486`).

2. **P4-C2-F2 — SEVERITY: blocking. A-P4-3 hides a wider lowering than R-P4-14 admits.**

   **CONCRETE FAILURE SCENARIO:** Append a novel false plain-ASCII claim to `made_up_warning` while retaining its existing count clauses. The display boundary accepts and prints it; both screen tests still pass because they assert only substrings; the claim inventory sees only source text and rejects enumerated retired forms rather than arbitrary semantic overclaims; and no golden pins screen output. The same route could interpolate a published label: the display boundary would make it terminal-safe, not refuse publication.

   A-P4-3 says the four replacement controls catch an overclaiming or value-bearing sentence and leave only a “merely useless” sentence as residual. They do not. The residual includes false and value-bearing additions, so the amendment understates the obligation it lowers.

   **EVIDENCE:** The amendment makes the stronger control claim at `docs/plans/phase-4-columns.md:1753-1768`, repeated in R-P4-14 at `docs/plans/phase-4-columns.md:1537-1548`. The display boundary only renders control characters safely (`src/synthtwin/parsing.py:303-350`; `src/synthtwin/cli.py:289-306`). The screen tests retain-text substrings rather than pinning the complete sentence (`tests/test_p4d2_loud_decline.py:309-315`, `357-374`). The inventory normalizes source and compares it with written pattern lists (`tests/test_claim_inventory.py:808-854`, `857-871`); it does not render and semantically assess arbitrary output. The golden suite pins description, twin, report, and quality-report bytes, not screen or summary bytes (`tests/test_twin_golden.py:193-257`, `514-539`, `877-917`).

   This also leaves P4-D2’s current exact-shape obligation unmet for the screen sentence (`docs/plans/phase-4-columns.md:469-475`).

3. **P4-C2-F3 — SEVERITY: blocking. The Phase 3 owner gate remains unmet, and branch status does not waive it.**

   **CONCRETE FAILURE SCENARIO:** Commit `1baec05` carries Phase 4 implementation and an Unreleased Phase 4 changelog while the public ledger still calls Phase 3 current, README still labels the project Phase 3, STATUS says Phase 4 has not started, and the inventory requires those old statements. No owner release or closure act is recorded.

   The implementer was right to decline this repair: Phase closure is explicitly an owner act, so taking it would have been impersonating the owner, not implementation. That is not a dodge. Nevertheless, the stage is not conforming.

   The commits may remain on the branch as an audit record, but Stage 2 may not stand as ratified, completed, merged, or as authority to advance Stage 3 while the gate is unmet. Because the plan says closure occurred *before Stage 2* and that the phase statements moved in Stage 2’s first commit, a later closure alone cannot make the existing history satisfy those sentences. The owner must either evidence that closure already predated `ec941f6`, or amend the sequencing and price the branch-first history before this stage can be ratified.

   **EVIDENCE:** The precondition and same-first-commit requirement are explicit at `docs/plans/phase-4-columns.md:169-175`, `1252-1257`, and `1783-1784`. Current contradictory state remains at `CLAUDE.md:225-245`, `README.md:3-10`, `STATUS.md:27-34`, and `tests/test_claim_inventory.py:743-749`; the Phase 4 changelog is already present at `CHANGELOG.md:9-42`. The owner-act precedent is stated at `CLAUDE.md:235-240`.

4. **P4-C2-F4 — SEVERITY: serious. The variant-only invention path still has no red check.**

   **CONCRETE FAILURE SCENARIO:** Delete the `variants_withheld` loop from `_held_back_cells`. A label with `suppressed_rows == 0`, `variants == {}`, and `variants_withheld == {"1": 11}` is then classified as making up nothing, although generation writes eleven invented spelling cells. Its report loses the sentence and both totals lose the column. The Stage 2 tests remain green: their ordinary label and all-invented-label fixtures reach suppressed levels, not variant-only withholding.

   **EVIDENCE:** A-P4-2 expressly identifies the variant-only route (`docs/plans/phase-4-columns.md:1708-1711`), and acceptance requires totality over every label column with invented cells (`docs/plans/phase-4-columns.md:1785-1794`). The correct but unguarded arithmetic is at `src/synthtwin/rendering.py:493-510`; generation repeats each invented spelling over the multiplicity-key row count at `src/synthtwin/generation.py:4287-4300`. The Stage 2 fixtures exercise a suppressed rare level (`tests/test_p4d2_loud_decline.py:155-169`) and an entirely suppressed level (`tests/test_p4d2_loud_decline.py:463-486`), while every direct test of the new private helpers is confined to this file.

   The mutation record at `tests/test_p4d2_loud_decline.py:42-62` is otherwise honest: it distinguishes the two measured mutations from two reasoned red mechanisms. Mutation measurement itself is not separately required, but this specific path was already named as missing in round 1 and still lacks any failure mechanism.

5. **P4-C2-F5 — SEVERITY: wording. The golden comment contradicts its own cause record.**

   **CONCRETE FAILURE SCENARIO:** A later reviewer reads the final cause paragraph and concludes the Stage 2 report change was purely additive because it states that no line was reworded or removed. Eight lines earlier, the same record correctly says the class sentences and pre-existing column preamble were reworded. The diff did replace that preamble.

   The separate claim that no twin byte moved is true: the description and twin digest constants did not change, and Stage 2 touched no generation rule.

   **EVIDENCE:** The rewording is recorded at `tests/test_twin_golden.py:497-506` and implemented at `src/synthtwin/rendering.py:1530-1540`; the contradictory “no line was reworded” assertion is at `tests/test_twin_golden.py:508-513`. The unchanged description and twin digests remain at `tests/test_twin_golden.py:193-195` and `241-243`, while only the report digest is re-recorded at `tests/test_twin_golden.py:514-539`.

## VERDICT

**REJECT.** Blocking items: **P4-C2-F1** (A-P4-2’s fully-invented label class is silent in the profiler summary), **P4-C2-F2** (A-P4-3 hides a wider control lowering), and **P4-C2-F3** (the Phase 3 owner gate remains unmet).

## What was checked

- Reviewed the complete `5a5c3f8..1baec05` stage diff, the `ec941f6..1baec05` repairs, both amendments, the seal update, all Stage 2 source/tests, and all eight round-1 items.
- Traced every contract-permitted role/axis combination. A declared nonempty column can only be `identifier`, and a declared empty column can only be `empty`; the loader rejects other declared-role combinations (`src/synthtwin/contract.py:2789-2803`). Both permitted shapes are classified correctly.
- Verified `_made_up_class` is total and single-valued for loaded version-5 profiles, including free text, identifier, `numeric_unrepresentable`, empty, label, datetime, and numeric facts.
- Verified constant-below-floor and all-variant-withheld labels settle to `EVERYTHING`; partially withheld labels settle to `HELD_BACK`.
- Verified `_held_back_cells`: multiplicity size × number of spellings matches generation. `occurrence_size(None)` is skipped, but a loaded profile cannot reach it because `_multiplicity` rejects non-decimal and out-of-range keys (`src/synthtwin/contract.py:1918-1952`, `1988-2033`).
- Verified datetime ignores the universal K/O/C/N partition and counts only `n_unparsed`, matching generation (`src/synthtwin/rendering.py:553-573`; `src/synthtwin/generation.py:4024-4114`).
- Verified numeric K/O/C/N: K is constructed from the numeric ladder; O, C and N each receive class spellings (`src/synthtwin/generation.py:3380-3454`). Contract X2 partitions `n_present`, and Q3 requires K ≥ 1 (`src/synthtwin/contract.py:3123-3138`, `4110-4129`).
- Checked all “other N” arithmetic. Valid label, numeric, and datetime profiles keep invented counts within `0..n_present`; `_how_much` promotes equality to `EVERYTHING`, so no valid branch can print a negative remainder.
- Confirmed report body, report foot, and screen totals share one classifier and agree mechanically; the summary omission in P4-C2-F1 is the divergent surface.
- Confirmed `made_up_warning` is public by naming convention, documented, deterministic, and reached by the CLI (`src/synthtwin/rendering.py:666-689`; `src/synthtwin/cli.py:1295-1301`).
- Confirmed display-boundary passage for report, summary, and warning; fixed profile order and sorted multiplicity keys preserve determinism.
- Ran the offline static scanner read-only: 16 product files, zero violations. No new regex, import, native call, dynamic loading, subprocess, computed-value method call, or forbidden list-growth path was found.
- Confirmed item 3, the quality-report work, remains untouched, and generate still returns 0 (`src/synthtwin/cli.py:1340-1348`).
- Ran the decontamination scanner read-only; it completed with no concern.
- Did not run pytest, as instructed.
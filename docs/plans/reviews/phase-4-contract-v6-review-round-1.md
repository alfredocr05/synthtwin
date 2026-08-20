<!-- Phase 4 contract v6 review, round 1. Reviewer: codex
(gpt-5.6-sol, xhigh effort), 2026-08-20. Paths are repository-relative.
Wording adjusted only where the vocabulary scanner required it. -->

# Phase 4 contract v6 review — round 1

1. **P4-X1-F1 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A document with `profile_version: 6` and seventeen settings keys is required by C6-18/C6-37, but the carrying rule leaves C5-24’s requirement for version 5 and version 5’s exact fifteen-key setting shape in force. No document can satisfy both versions and both key counts; a literal loader implementation must reject every version 6 document.

**EVIDENCE:** The contract carries every older rule unless superseded by name at `docs/spec/profile-contract-v6.md:104`, but C6-18 and C6-37 do not name the older rules at `docs/spec/profile-contract-v6.md:269` and `docs/spec/profile-contract-v6.md:545`. The conflicting requirements remain at `docs/spec/profile-contract-v5.md:587` and `docs/spec/profile-contract-v5.md:1063`. The plan instead requires producer and loader to move together to exactly one version at `docs/plans/phase-4-columns.md:1235`.

2. **P4-X1-F2 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A producer writes the required `built_in_dates` list. Carried C5-S14 refuses it because each declaration record must still have exactly four keys. At the same time, C6-31 incorrectly supersedes C5-16—the command-line-only privacy obligation—and C6-K5 incorrectly supersedes C5-K4’s no-overlap rule. A producer can therefore make `built_in_dates` depend on whether a table contains a placeholder, or put the same placeholder in the kept and missing records, while claiming C6 conformance.

**EVIDENCE:** C6-31 and C6-K5 are at `docs/spec/profile-contract-v6.md:425` and `docs/spec/profile-contract-v6.md:430`. C5-16 is actually the table-independent producer obligation at `docs/spec/profile-contract-v5.md:645`; C5-K3 is the count identity at `docs/spec/profile-contract-v5.md:769`; C5-K4 is the cross-record no-overlap rule at `docs/spec/profile-contract-v5.md:780`; and C5-S14 fixes four keys at `docs/spec/profile-contract-v5.md:808`. Amendment A-P4-1 requires the third list, the extended count identity, and `--keep-value` precedence at `docs/plans/phase-4-columns.md:1651`. The supersession identifiers also violate the contract’s own keep-the-older-suffix discipline at `docs/spec/profile-contract-v6.md:111`; the same defect appears in `C6-9R`, `C6-26`, and `C6-N3` at `docs/spec/profile-contract-v6.md:435`, `docs/spec/profile-contract-v6.md:357`, and `docs/spec/profile-contract-v6.md:388`.

3. **P4-X1-F3 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A 24-row column containing twelve `A` cells and twelve `#N/A` cells is binary under version 5. Version 6 reads `#N/A` as absent, leaving a constant column. C6-1 nevertheless normatively says every earlier-rule column keeps its former role. A producer must either violate C6-1 or violate the new missing vocabulary.

**EVIDENCE:** The plan expressly authorizes and bounds this exception to no-regression at `docs/plans/phase-4-columns.md:61` and gives the binary-to-constant shape at `docs/plans/phase-4-columns.md:65`. The exception is absent from the unconditional statements at `docs/spec/profile-contract-v6.md:54` and `docs/spec/profile-contract-v6.md:145`, while the new spelling is required at `docs/spec/profile-contract-v6.md:361`.

4. **P4-X1-F4 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** One hundred cells such as `u:1`, `u:2`, … take `affixed_number`. Under the carried universal meaning, none of the complete cell spellings reads as a number, so `n_numeric == 0`; imported Q3 then forbids the role’s numeric block. Writing `n_numeric == 100` to count cores makes the universal cell-class census false instead. The proposed wire has no coherent population for the affixed distribution.

**EVIDENCE:** C6-5 imports the complete numeric block over cores and AF4 imports all numeric invariants at `docs/spec/profile-contract-v6.md:178` and `docs/spec/profile-contract-v6.md:188`. The carried meaning of `n_numeric` concerns present cells at `docs/spec/profile-contract-v4.md:495`; Q2 and Q3 tie the statistics population to it at `docs/spec/profile-contract-v4.md:1152`. The plan requires the numeric details to be computed over cores at `docs/plans/phase-4-columns.md:637`. C6 must explicitly redefine the affected universal counts for this role or add distinct core-count fields.

5. **P4-X1-F5 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** With `day_first: true`, a column contains ninety-nine ambiguous `01/02/2024` cells and one `12/31/2024` cell. The plan requires month-first because it parses strictly more cells and requires a remark explaining the override. The contract only defines a boolean setting; a producer that blindly obeys the declaration can reverse ninety-nine dates while still satisfying the stated v6 schema.

**EVIDENCE:** The evidence-first winner, tie rule, four counts, and two-clause remark are normative at `docs/plans/phase-4-columns.md:873`. The contract only records the setting at `docs/spec/profile-contract-v6.md:269` and mentions the option in the refusal at `docs/spec/profile-contract-v6.md:557`; no clause transcribes P4-D4.6’s producer rule or remark.

6. **P4-X1-F6 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A datetime column has twenty ordinary dates and eleven `1900-01-01` cells judged absent. Its `missing_by_source` names that spelling. C6-9R item 1 says reproduce it because it is not one of the three numeric stand-ins, while item 2 can be read to say every stand-in-sourced cell stays blank. If reproduced, re-profiling the generated distribution is not guaranteed to re-judge the date as an outlier; if blanked, item 1 is violated. A `--keep-value 1900-01-01` run is also unresolved because C6 never states that rescue wins over the new date pass.

**EVIDENCE:** The plan excludes stand-in-sourced spellings from reproduction and amends that context with the date candidates at `docs/plans/phase-4-columns.md:1130`; it explicitly requires `--keep-value` to win at `docs/plans/phase-4-columns.md:1657`. C6-9R limits its named exception to numbers at `docs/spec/profile-contract-v6.md:441`, and C6-29 states the date pass without declaration precedence at `docs/spec/profile-contract-v6.md:403`.

7. **P4-X1-F7 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A hand-written `time_of_day` block has `n_present: 100`, `n_unparsed: 99`, and `minimum_parse_rate: 0.99`. T4 passes because 99 is less than 100, although only one cell parsed and the role requires ninety-nine. The same gap exists for `affixed_number`: AF2 checks the floor but not the parse line. A `long_tail_labels` block can satisfy B1–B8 without any level reaching eleven because §9 adds no detection invariant for it. Such documents misroute columns yet pass the purported complete invariant list.

**EVIDENCE:** The role predicates are stated at `docs/spec/profile-contract-v6.md:161`, `docs/spec/profile-contract-v6.md:205`, and `docs/spec/profile-contract-v6.md:238`; the purported checkable list weakens them to AF2, T4, and “no level_ceiling” at `docs/spec/profile-contract-v6.md:519`. The plan requires detection thresholds to be recorded and applied as counts at `docs/plans/phase-4-columns.md:559`.

8. **P4-X1-F8 — SEVERITY: serious.**

**CONCRETE FAILURE SCENARIO:** With permitted `minimum_parse_rate: 0.5`, a column has ten `HH:MM` cells and ten `HH:MM:SS` cells. Both forms independently clear the line. There is no joint reading and no tie order, so two producers may choose different `clock_form`, endpoints, rung lists, and `n_unparsed` for the same table and settings.

**EVIDENCE:** Both the plan and contract require one form to clear but fix no winner when both do at `docs/plans/phase-4-columns.md:684` and `docs/spec/profile-contract-v6.md:205`. The inherited settings range permits 0.5 at `docs/spec/profile-contract-v4.md:286`.

9. **P4-X1-F9 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** C6 requires `numeric_styles` to contain `fraction_widths`, an object. The carried v4 wire requires every `numeric_styles` value to be an integer and requires all its values to sum to `n_numeric`. Including the object violates v4; omitting it violates C6. Even after that conflict, width keys such as `2`, `02`, and `-1` are not given a canonical non-negative-integer grammar, so two producers can encode the same width differently.

**EVIDENCE:** The new nested fact is required at `docs/spec/profile-contract-v6.md:342`. The carried shape and invariants are at `docs/spec/profile-contract-v4.md:1676` and `docs/spec/profile-contract-v4.md:1696`. The plan requires one styles fact with a pooled remainder at `docs/plans/phase-4-columns.md:820`, but does not authorize silently discarding the existing closed map.

10. **P4-X1-F10 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** An implementer sizes `ROLES`, `STATISTICAL_TYPES`, the axes completeness check, or a fixture loop from the stated count twelve. The enumeration actually contains thirteen roles—version 5’s ten plus three—and thirteen statistical types. It also lists `affixed_number` before `time_of_day`, while C6-1 requires the opposite rule order. One role can be omitted or the two new readings tested inconsistently across consumers.

**EVIDENCE:** The contradictory count and thirteen-name enumeration are at `docs/spec/profile-contract-v6.md:669`; A5 repeats “twelve” at `docs/spec/profile-contract-v6.md:539`. Version 4 fixes ten roles at `docs/spec/profile-contract-v4.md:699`; P4-D7 adds three at `docs/plans/phase-4-columns.md:1153`. C6-1 orders time before affix at `docs/spec/profile-contract-v6.md:145`, while §14 reverses them at `docs/spec/profile-contract-v6.md:671`. Formats do correctly total eleven, absence classes six, and the published vocabulary twenty-three.

11. **P4-X1-F11 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A `numeric_unrepresentable` block must include `min_length` and `max_length` under C6-24, but the carried forbidden-key matrix permits those keys only on `identifier`. A loader generated from the matrix rejects every such v6 block; a loader generated from C6-24 accepts a document the carried matrix forbids. New-role columns and the remaining new keys have no total matrix row or column at all.

**EVIDENCE:** P4-D7 requires the complete forbidden-key matrix at `docs/plans/phase-4-columns.md:1153`. C6-24 requires the fields at `docs/spec/profile-contract-v6.md:332`; the carried matrix places them only under identifier at `docs/spec/profile-contract-v4.md:1319` and `docs/spec/profile-contract-v4.md:1357`. Version 6 contains no superseding full matrix.

12. **P4-X1-F12 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A column of opaque tokens such as `r:101`, `r:102`, … takes `affixed_number` and publishes a numeric distribution. Because the standing “these may be codes; use `--identifier`” remark is absent from the contract, a conforming producer can publish the block with no warning and a researcher treats code order as quantity. A declined column that would become numeric after removing one floor-clearing nonnumeric spelling can likewise omit A-P4-1’s truthful `--missing-value` advice.

**EVIDENCE:** The unconditional affix misroute remark is required at `docs/plans/phase-4-columns.md:663`; the recoverable-distribution clause is required at `docs/plans/phase-4-columns.md:1670`. P4-D3 also requires the note grammar to move at `docs/plans/phase-4-columns.md:524`, and A-P4-3 confines that grammar obligation to profile-document sentences at `docs/plans/phase-4-columns.md:1767`. The v6 role clauses and exhaustive new-key/invariant tables end without either grammar form at `docs/spec/profile-contract-v6.md:489`.

13. **P4-X1-F13 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** A producer fabricates a well-formed, ordered clock ladder whose values never occurred in the table, or writes an affix pair different from the source pair. A loader has no table and cannot detect either lie. The contract presents these as rules but marks no v6 clause as a producer obligation, so the implementation and registry have no explicit side on which source truth must be verified.

**EVIDENCE:** Source-only assertions appear at `docs/spec/profile-contract-v6.md:173`, `docs/spec/profile-contract-v6.md:226`, `docs/spec/profile-contract-v6.md:332`, and `docs/spec/profile-contract-v6.md:318`; §9 calls its list checkable without identifying exceptions at `docs/spec/profile-contract-v6.md:517`. Version 5 states the required discipline explicitly and marks producer-only rules at `docs/spec/profile-contract-v5.md:519` and `docs/spec/profile-contract-v5.md:998`.

14. **P4-X1-F14 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** An implementer follows §12 as the complete disclosure ledger. The summary and security text then omit that newly read unpadded/slashed datetime columns publish floor-free endpoints and rungs, and omit the new `built_in_dates` settings lists. The grouped affix row also fails to name several facts C6-5 publishes, including `std_unrepresentable`, `n_negative_unrepresentable`, the statistics-population counts, and `numeric_share`. Real-derived facts reach the profile without the plan-required pricing.

**EVIDENCE:** P4-D7 requires the whole affixed block, every fact named, and a surface sentence per row at `docs/plans/phase-4-columns.md:1213`. A-P4-1 adds the slashed-family and `built_in_dates` disclosure rows at `docs/plans/phase-4-columns.md:1683`. C6-5 enumerates the omitted affix facts at `docs/spec/profile-contract-v6.md:178`, while the claimed complete delta at `docs/spec/profile-contract-v6.md:594` omits them and both A-P4-1 rows.

15. **P4-X1-F15 — SEVERITY: blocking.**

**CONCRETE FAILURE SCENARIO:** Stage 6 retires the “all absent cells are empty” statement in the renderer but misses the same claim in `SECURITY.md`, or updates the vocabulary count in one surface but not the Phase 3 residual. Because the required stage-keyed claim-migration table is absent, the contract supplies no closed set against which that partial migration is red.

**EVIDENCE:** P4-D7 item 9 requires one stage-keyed row per moving surface and declares unlisted movement red at `docs/plans/phase-4-columns.md:1248`. Version 6 proceeds from disclosure decisions to enumerations and review record at `docs/spec/profile-contract-v6.md:631` and `docs/spec/profile-contract-v6.md:667`; it contains no claim-migration table.

16. **P4-X1-F16 — SEVERITY: serious.**

**CONCRETE FAILURE SCENARIO:** At landing, an implementer makes the governing set “seven” as the contract instructs. It can do that only by omitting v6 from the seal or removing an already governing document, leaving normative text unsealed.

**EVIDENCE:** The contract says v6 makes seven at `docs/spec/profile-contract-v6.md:8`. The shipped registry already contains seven governing documents at `tests/dispositions.py:100`; adding v6 makes eight.

17. **P4-X1-F17 — SEVERITY: serious.**

**CONCRETE FAILURE SCENARIO:** Before any release, a source-checkout user creates a profile and hands it to a colleague, exactly as §2 says profiles may travel. The colleague does not hold the table. C6-40 nevertheless concludes from “no release” that every profile holder holds the table and preserves advice to profile it again. The advice is impossible to follow and may prompt profiling a different table.

**EVIDENCE:** The contract itself says a profile may be handed to a colleague at `docs/spec/profile-contract-v6.md:18`, then makes the contrary universal inference at `docs/spec/profile-contract-v6.md:565`. Version 5 correctly recognizes that the machine in front of a profile holder may not hold the table at `docs/spec/profile-contract-v5.md:1196`. The narrower release fact is supported: Phase 3’s closure records no tag or publication at `docs/plans/phase-3-product.md:7493`, the project remains `0.1.0.dev0` at `STATUS.md:3`, and the checkout has no tags. The defect is the holder inference, not the release-state sentence.

## VERDICT

**Reject.** Blocking items: **P4-X1-F1 through P4-X1-F7 and P4-X1-F9 through P4-X1-F15**.

The contract is not presently a total, carry-correct, enforceable version 6 wire: no document can satisfy several inherited and new clauses simultaneously, multiple ratified delta items are absent, and conforming producers can disagree on or misdescribe typed data.

## What was checked

- P4-D3, every P4-D4 subsection, P4-D5, P4-D6, and P4-D7 items 1–9.
- A-P4-1 items 1–4 and its added disclosure/migration pricing.
- A-P4-2’s cell-settled invention classification; it adds no wire key and is appropriately outside this contract’s artifact scope.
- A-P4-3’s profile-document grammar boundary and its effect on new evidence/remark forms.
- A-P4-4’s phase and release history.
- Every stated enumeration against v5/v4: roles and statistical types fail at 13 versus 12; formats pass at 11; resolution passes at 4; time precision passes at 6; absence classes pass at 6; published vocabulary passes at 23; settings arithmetic is 15 + 2 = 17, but §14 omits the enumeration and inheritance leaves the fifteen-key rule live.
- Axes totality, publication-class placement, forbidden-key closure, required/forbidden key sets, and no-optional-key discipline.
- Affix-core population routing, clock-form selection, date-direction selection, calendar-placeholder judging, missing-spelling reproduction, fraction-width shape, and long-tail detection.
- Loader-checkable versus producer-only obligations and disposition-registry bindability.
- Disclosure floors, floor-free facts, settings disclosures, and carrier-surface migration.
- Shipped `contract.py`, `profile.py`, `taxonomy.py`, and `tests/dispositions.py`; current code remains version 5, as expected before stage 6.
- Release-state repository evidence and tag state; the stronger table-holder inference was not accepted.
- Offline/security boundary: the specification adds no executable network, subprocess, native-call, dynamic-load, or profile/generator-boundary path.
- Decontamination scan: no digest-prefix concern was reported.
- No files were changed or created. `pytest` was not run.
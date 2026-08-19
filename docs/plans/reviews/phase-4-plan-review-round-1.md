<!-- Phase 4 plan adversarial review, round 1. Reviewer: codex
(gpt-5.6-sol, high effort), 2026-08-19. Paths in this record are
repository-relative. Wording was adjusted only where the repository's
vocabulary scanner required it; no meaning was changed. -->

# Phase 4 plan review — round 1

**Reviewer:** Codex, adversarial reviewer, 2026-08-19.

The staged target identifies itself as revision 1; this review applies to the bytes currently staged at `docs/plans/phase-4-columns.md`.

## Numbered review items

1. **P4-P1-F1 — `--day-first` can silently reverse a column whose one contrary cell proves it is month-first**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A 100-row column has 99 slashed dates drawn from 20 distinct spellings whose first and second fields are both at most 12, plus `12/31/2024`. The column exceeds the categorical ceiling. The day-first parser reads 99 cells, the month-first parser reads all 100, and the parse-line count is 99. With `--day-first`, merely swapping the formats makes day-first win immediately, reverses the meaning of the 99 ambiguous dates, and records the contrary cell as unparsed. The promised contradiction remark never fires because the implementation stops at the first format that clears the line.

   **EVIDENCE:** The plan defines the option as an order swap and promises that contradictory evidence is read month-first and reported: `docs/plans/phase-4-columns.md:669-685`. The shipped classifier stops at the first format reaching the count, without comparing a later format’s stronger evidence: `src/synthtwin/taxonomy.py:3345-3364`. The ratified taxonomy fixes the shared 99% line and ordered explicit-format behavior: `docs/plans/phase-1-profiler.md:368-381`. Direct measurement of this shape gives day-first 99, month-first 100, required 99.

2. **P4-P1-F2 — The “complete” v6 delta has no wire value for the new datetime formats**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** The producer recognizes a `YYYY/MM/DD`, `YYYY-MM`, or mixed ISO column and must emit the required datetime `format` field. Reusing an existing value lies about which parser read the file; adding values such as a month or mixed-family name violates the closed v4 enumeration and is absent from the plan’s supposedly complete v6 delta. A conforming loader must therefore reject the producer’s output or accept a semantically false field.

   **EVIDENCE:** The plan introduces three new readings, including a joint reading that is explicitly not one existing single format: `docs/plans/phase-4-columns.md:592-630`. Its “delta, complete” adds `resolution_mix` and `month` to two enumerations but never adds or defines any `format` member: `docs/plans/phase-4-columns.md:890-919`. The carried contract requires `format`, limits it to six values, defines it as the parser family that read the real file, and binds resolution to it: `docs/spec/profile-contract-v4.md:910-926`, `docs/spec/profile-contract-v4.md:974-976`.

3. **P4-P1-F3 — The time-of-day refusal rejects a profile whose source table is its satisfiability witness**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A column contains every one of the 1,440 valid `HH:MM` spellings once plus one distinct unparsed text cell. It has 1,441 distinct present values, exceeds the categorical ceiling, and 1,440 cells clear the 99% time parse line. The proposed producer therefore emits `time_of_day`, `n_unparsed == 1`, and `n_distinct == n_present == 1441`. The proposed feasibility rule then refuses because 1,441 exceeds the form’s 1,440-spelling capacity—even though the source itself satisfies the profile by using the separately published unparsed class.

   **EVIDENCE:** The plan publishes an unparsed count but computes capacity from the clock form alone: `docs/plans/phase-4-columns.md:571-590`; it repeats that refusal without adding the straggler domain: `docs/plans/phase-4-columns.md:1014-1025`. The ratified all-different obligation covers every present value on every role, and the refusal discipline reserves refusal for documents no construction can satisfy: `docs/spec/generation-method-v1.md:2864-2877`, `docs/spec/generation-method-v1.md:2915-2935`. Existing datetime precedent expressly treats `n_unparsed` as counted stand-ins outside the parsed-value representation: `docs/plans/phase-2-generator.md:630-632`.

4. **P4-P1-F4 — Affix detection and sentinel normalization have no coherent order**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** At the default floor, use 13 distinct cells with one exact affix pair and cores `10` through `19` plus the three built-in stand-in numbers. All 13 cells initially satisfy the affix predicate. Judged over the ordinary cores, all three candidates are outliers and individually exceed the minimum-share threshold, leaving ten present affixed cells. If detection occurs first, the role publishes an affix whose surviving present count is below the constitutive floor. If sentinel normalization occurs first, the role must decline. The plan permits both readings by saying only that judging occurs before statistics, not before detection.

   **EVIDENCE:** Affix detection counts present cells and says the count clearing the floor is what authorizes publication: `docs/plans/phase-4-columns.md:493-517`. Sentinel judging is stated only as preceding statistics: `docs/plans/phase-4-columns.md:507-513`. The ratified rule is stronger: sentinel normalization runs before every role test: `docs/plans/phase-1-profiler.md:505-515`. The shipped producer likewise removes judged candidates and rebuilds the cell tally before `_decide` performs any role test: `src/synthtwin/taxonomy.py:4518-4557`.

5. **P4-P1-F5 — The affixed-number rule creates an unremarked code-to-quantity misroute**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A 100-row column contains 20 opaque tokens of the form `A-1.01` through `A-20.01`, each repeated five times. It exceeds the categorical ceiling and every cell has the same affix pair, so the plan publishes a numeric distribution over the decimal cores. The proposed code warning does not fire: the cores are not whole, the column is only 20% distinct rather than nearly all-different, and the cores are not fixed-width leading-zero strings. The result is a silent type miscast created by Phase 4.

   **EVIDENCE:** The affixed-number predicate accepts any longest numeric substring under one repeated pair: `docs/plans/phase-4-columns.md:485-505`. Its dedicated warning requires whole cores and near non-repetition, while the later remark text covers only the listed shapes: `docs/plans/phase-4-columns.md:541-549`, `docs/plans/phase-4-columns.md:687-698`. The shipped taxonomy records why this inference class was withdrawn: numeric-bearing measurements and opaque labels can have the same textual shape, meaning is not in the values, and a wrong guess destroys a distribution: `src/synthtwin/taxonomy.py:10-24`. Charter principle 5 forbids silent miscasting: `CLAUDE.md:63-66`.

6. **P4-P1-F6 — The long-tail disclosure delta omits a new folded-group fact**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** In 100 rows, one spelling repeats 11 times, two one-off spellings differ only by case, and 87 other spellings are unique. The column is over the categorical ceiling and qualifies for long-tail handling. Today its free-text repetition map reports the frequent group and 89 raw singleton groups. The proposed `suppressed_level_counts` instead reveals that two of the suppressed rows form one folded identity. The plan calls this “the same information” and tells the owner that only the published labels are new, so owner decision 1 is priced on an incomplete disclosure delta.

   **EVIDENCE:** The plan claims the suppressed-size multiset is already published by free text and that labels are the only delta: `docs/plans/phase-4-columns.md:713-735`. The carried contract defines the free-text multiplicity map over raw present values: `docs/spec/profile-contract-v4.md:1396-1409`. Label grouping is instead performed after trimming and case folding: `src/synthtwin/taxonomy.py:3071-3088`. Those groupings are not equivalent on the scenario above.

7. **P4-P1-F7 — The width disclosure is not necessarily a magnitude fact**

   **SEVERITY: serious**

   **CONCRETE FAILURE SCENARIO:** A 100-row column contains 99 unrepresentable numerals of length 400 and one nonnumeric text cell of length 1,000. The numeric-looking count reaches the 99% line, so the column takes `numeric_unrepresentable`. Because the proposed widths range over all present cells, `max_length` publishes the one text straggler’s length, not any numeral’s order of magnitude. The owner-facing cost statement therefore mischaracterizes what the floor-free one-cell fact can reveal.

   **EVIDENCE:** The plan defines both lengths over all present cells but prices `max_length` as the largest withheld number’s order of magnitude: `docs/plans/phase-4-columns.md:632-649`. The shipped rule permits a numeric-unrepresentable role with parse-line numeric intent and a below-line representable population, retaining nonnumeric stragglers in the present population and repetition facts: `src/synthtwin/taxonomy.py:3637-3708`. The default parse line is 0.99: `src/synthtwin/taxonomy.py:1154-1164`.

8. **P4-P1-F8 — The fixed-fraction pooled remainder has no deterministic writing or validation rule**

   **SEVERITY: serious**

   **CONCRETE FAILURE SCENARIO:** A numeric column has twenty decimal cells with fraction width two and one with width three at floor 11. The new fact publishes width two at 20 and pools one unnamed width. The plan does not say which width the generator writes for that pooled cell, how value spellability constrains that choice, or the lower and upper bound for each width’s validation recount. One implementation may write width two, another canonical width, and a third invent width three; all can claim to “write decimal cells at the published widths.”

   **EVIDENCE:** The plan promises a pooled fact, generated widths, and a window without defining the pool’s allocation or window arithmetic: `docs/plans/phase-4-columns.md:651-667`. The generation amendment merely adds widths to quotas and the recount identity: `docs/plans/phase-4-columns.md:1010-1013`. The validation section says the normative window must live in the generation method: `docs/plans/phase-4-columns.md:1049-1056`; the ratified validation method forbids creating or tightening an approximated bound locally: `docs/spec/validation-method-v1.md:1162-1165`. The plan must require a complete allocation and independently computable bound, not only the word “window.”

9. **P4-P1-F9 — The settings enumeration claimed as exact is not enumerated**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** One implementer adds `day_first` and `long_tail_minimum_count`; another also records an affix-pair threshold; a third derives that threshold and adds no key. Each can point to P4-D7, which says “any affix-rule constant the contract needs.” The contract’s exact key count, loader shape, validator consumption table, and version-refusal option list cannot be written or tested from the plan.

   **EVIDENCE:** P4-D3 says P4-D7 enumerates an exact count: `docs/plans/phase-4-columns.md:476-479`. P4-D7 supplies neither the count nor a closed key list and expressly leaves an open-ended affix constant: `docs/plans/phase-4-columns.md:916-919`. The ratified validation method treats even one extra or skipped settings key as a defect: `docs/spec/validation-method-v1.md:139-148`. Acceptance criterion 5 nevertheless requires equality in both directions: `docs/plans/phase-4-columns.md:1263-1267`.

10. **P4-P1-F10 — The quality-report invention sentence is not provenance-safe**

    **SEVERITY: serious**

    **CONCRETE FAILURE SCENARIO:** A researcher validates the original source CSV against its own profile. A label column has suppressed levels. Following the plan literally, the quality report says that N of “its cells stand in” for withheld values. Those cells are genuine source cells, not invented stand-ins. The validator has no basis to change that sentence because it cannot determine whether the checked CSV is a generated twin or a real file.

    **EVIDENCE:** The plan requires the quality report to say that N of a label column’s cells are stand-ins: `docs/plans/phase-4-columns.md:376-385`. The charter fixes that validation reads an arbitrary CSV and cannot tell a synthetic file from a real one: `CLAUDE.md:93-103`. The normative validation method defines every report statement as a statement about the measured file: `docs/spec/validation-method-v1.md:1501-1515`. The plan must instead require provenance-neutral wording about what a generated twin would contain or what the description withholds.

11. **P4-P1-F11 — Mixed clock forms both take the time role and must decline it**

    **SEVERITY: serious**

    **CONCRETE FAILURE SCENARIO:** A 100-row, over-ceiling column contains 99 `HH:MM` cells across more than ten distinct times and one `HH:MM:SS` cell. Under the stated parse-line rule, the `HH:MM` form reaches the required 99 cells and the column takes `time_of_day` with one unparsed cell. Four lines later, the plan says mixed `HH:MM`/`HH:MM:SS` columns are excluded and decline to later rules. Either result conforms to one sentence and violates the other.

    **EVIDENCE:** Both incompatible outcomes appear in the same rule: `docs/plans/phase-4-columns.md:557-569`. The plan explicitly preserves the count-based 99% line: `docs/plans/phase-4-columns.md:326-333`. Its mixed-ISO section demonstrates that a 99/1 form split normally lets the 99-cell single form stand: `docs/plans/phase-4-columns.md:609-613`. The clock rule must state whether any second form vetoes detection or only a mix beyond the ordinary slack does.

12. **P4-P1-F12 — `affixed_number` has no single publication-class membership**

    **SEVERITY: serious**

    **CONCRETE FAILURE SCENARIO:** The implementer extends the existing exact-one-class guard. `time_of_day` is assigned to ranges and `long_tail_labels` to labels. For `affixed_number`, the plan says it has a ranges-class block but widens the labels-class doctrine to authorize its affixes, without saying whether the role belongs to ranges, labels, both, or a fourth hybrid class. Assigning both fails the exact-one invariant; assigning either one requires an unstated exception to the other class’s key rules.

    **EVIDENCE:** The ambiguity is in the publication-class paragraph itself: `docs/plans/phase-4-columns.md:448-459`. The shipped taxonomy defines three disjoint class tuples and describes the class as deciding the whole block: `src/synthtwin/taxonomy.py:247-264`. The executable invariant requires every role to belong to exactly one of labels, ranges, nothing, or empty: `tests/test_column_analysis.py:573-583`. P4-D7 promises a total forbidden-key matrix but does not resolve this membership: `docs/plans/phase-4-columns.md:893-902`.

## VERDICT

**REJECT.**

Blocking items: **P4-P1-F1 through P4-P1-F6 and P4-P1-F9**.

The plan currently creates a silent date reversal, specifies a datetime wire the carried contract cannot express, refuses a producer-reachable time profile, leaves sentinel normalization inconsistent with affix detection, creates an unremarked code-to-quantity path, understates the long-tail disclosure delta presented to the owner, and does not provide the exact settings enumeration its contract and validator require.

## What was checked

- Canonical reviewer and implementer briefs; the complete staged Phase 4 target, which identifies itself as revision 1.
- Ratified Phase 1, Phase 2, and Phase 3 plans, including amendments and residuals relevant to settings, declarations, numeric spelling, validation totality, publication classes, and Phase 4 reservations.
- The profile contract, v4 and v5: required keys, closed vocabularies, axes, role invariants, publication classes, forbidden-key matrix, missing-source rules, settings, version refusal, dispositions, and no-optional-key discipline.
- Generation method: single-stream ordering, per-column permutation, draw budgets, all-different totality, datetime and straggler construction, feasibility/refusal rules, numeric styles, and regeneration events.
- Validation method: producer-based re-description, exact settings replay, entry-table totality, independently computable windows, disclosure gate, measured-file wording, and report verdict honesty.
- Shipped taxonomy and parsing: actual rule order, categorical ceiling, count-based 99% line, first-matching date format, month/day ambiguity, sentinel removal before role selection, raw versus folded multiplicity, and current role/publication enumerations.
- Shipped generation, validation, contract, profile, reading, rendering, summary, quality, errors, and CLI surfaces where the plan asserts existing behavior or requires enumeration changes.
- Privacy attacks over long-tail folded identities, affix fragments, range endpoints, resolution mix, fraction widths, unrepresentable widths, and reproduced hole spellings.
- Statistical/type attacks over ambiguous slashed dates, opaque numeric-bearing labels, affix sentinels, mixed clock precision, parsed/unparsed distinctness capacity, and pooled formatting facts.
- Determinism attacks over new draws, iteration order, form assignment, reproduced-hole ordering, the single placement permutation, seed-invariance scope, and D12 regeneration.
- Guard machinery: governing-document list, exact plan/spec list, disposition registry, seal generation, claim-inventory governing-surface derivation, and staged-draft handling.
- The tracked-tree decontamination scan completed cleanly; staged whitespace checking completed cleanly. No repository file was modified.
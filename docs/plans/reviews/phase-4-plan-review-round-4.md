<!-- Phase 4 plan adversarial review, round 4. Reviewer: codex
(gpt-5.6-sol, high effort), 2026-08-19. Paths in this record are
repository-relative. Wording was adjusted only where the repository's
vocabulary scanner required it; no meaning was changed. -->

# Phase 4 plan review — round 4

Reviewer: Codex (GPT-5.6), adversarial reviewer — 2026-08-19.

## Round-3 repair verification

- **P4-P3-F1 — CLOSED.** Revision 4 now states explicitly that the clock ladder uses a linear axis, that a midnight-spanning cluster can generate values in the empty middle, and that only the selected rungs remain exact. The same limitation appears in the phase’s honest-limits section. Evidence: `docs/plans/phase-4-columns.md:636-647`, `docs/plans/phase-4-columns.md:1360-1365`.

- **P4-P3-F2 — NARROWED.** Snapping now occurs inside value construction; endpoints and the zero stratum are protected, sign and zero-ness are preserved, and merges are routed through the distinctness machinery. The remaining deterministic allocation ambiguity is P4-P4-F6 below. Evidence: `docs/plans/phase-4-columns.md:756-777`.

- **P4-P3-F3 — CLOSED.** Affix-based sentinel eligibility now runs only after rules 0–7 decline the original population. The shipped numeric sentinel pass remains before role selection, so an existing binary or categorical column never reaches the new pass. Evidence: `docs/plans/phase-4-columns.md:536-551`; `src/synthtwin/taxonomy.py:4518-4555`.

- **P4-P3-F4 — CLOSED.** The collision argument now separately covers invented label variants, neutral labels for suppressed levels, and published variants. Both invented label families have unbounded continuations and are placed under the extended candidate-rejection rule. Evidence: `docs/plans/phase-4-columns.md:960-984`; `docs/spec/generation-method-v1.md:1607-1643`.

- **P4-P3-F5 — CLOSED AS FRAMED.** `resolution_mix` now has closed key sets: the column’s own format on a single-format column and exactly the two constituent ISO formats on an `iso-mixed` column. Evidence: `docs/plans/phase-4-columns.md:1068-1083`. The stale vocabulary count in the same paragraph is separately P4-P4-F9.

- **P4-P3-F6 — CLOSED.** The winner-selection clause and the contradictory-evidence clause are independent. Unequal evidence with nonzero evidence in both directions therefore reports both the winner and the conflict. Evidence: `docs/plans/phase-4-columns.md:805-824`.

- **P4-P3-F7 — STILL OPEN.** The added sentence specifies evidence that the first row contains names, not positive evidence that it contains a record. It therefore does not protect the headerless unique-value case. This is P4-P4-F3.

## Numbered review items

### P4-P4-F1 — SEVERITY: blocking

**CONCRETE FAILURE SCENARIO:** A two-column file has an `id` column containing only absent cells, and the user supplies `--identifier id`. Revision 4’s first-match order sends that column to `identifier` at rule 0. The shipped and ratified behavior sends it to `empty`, with `structural_role: identifier`, because empty is the explicit exception that settles before identifier dispatch. Following the plan would therefore reclassify an existing column and contradict the contract’s axis rules.

**EVIDENCE:** Revision 4 puts declared identifiers before empty and calls both positions unchanged; it also says declaration wins at rule 0: `docs/plans/phase-4-columns.md:426-440`, `docs/plans/phase-4-columns.md:451-459`. The ratified contract expressly says an all-absent declared column has role `empty`, and permits `structural_role: identifier` with role `empty`: `docs/spec/profile-contract-v4.md:524-541`. Shipped code chooses `empty` before calling the value-based decision function containing the identifier branch: `src/synthtwin/taxonomy.py:3650-3655`, `src/synthtwin/taxonomy.py:4572-4581`.

### P4-P4-F2 — SEVERITY: blocking

**CONCRETE FAILURE SCENARIO:** A 100-row column contains 50 `yes` cells and 50 cells containing one of P4-D6.2’s newly added spreadsheet-error literals. Today the literal is data, so the column is binary. Under decision 7, those 50 cells become holes before role selection, leaving one present folded value and therefore a constant column. A numeric column obstructed by the same new literal can likewise move from free text into an existing numeric role. Both transitions are forbidden by the plan’s universal no-regression rule and its executable acceptance battery.

**EVIDENCE:** The plan says the only permitted role movements are from free text to a new role or newly read datetime format: `docs/plans/phase-4-columns.md:59-71`, `docs/plans/phase-4-columns.md:1309-1314`, `docs/plans/phase-4-columns.md:1471-1473`. P4-D6.2 simultaneously requires the new literals to read as holes everywhere and acknowledges that affected columns change behavior: `docs/plans/phase-4-columns.md:1013-1033`. Shipped processing removes built-in missing text before classification and decides constant or binary from the survivors: `src/synthtwin/taxonomy.py:2687-2727`, `src/synthtwin/taxonomy.py:3713-3759`, `src/synthtwin/taxonomy.py:4500-4516`.

The plan must either authorize and test the complete set of decision-7 transitions or change the missing-literal design. The current acceptance criterion is impossible for an adequate decision-7 fixture and vacuous if that fixture is omitted.

### P4-P4-F3 — SEVERITY: blocking

**CONCRETE FAILURE SCENARIO:** A headerless one-column file starts with `$1.00`, followed by unique values `$2.00`, `$3.00`, and so on. The first cell is not a plain number, date, or repeated label under the shipped reader. Revision 4 says that a first cell which is *not* an affixed number above affixed numbers is evidence for names. Here it is an affixed number, so that negative test does nothing, and the plan supplies no positive “affixed number among affixed numbers” record test. The file falls to the header convention: `$1.00` becomes the column name and the first record is lost.

The same failure occurs for a headerless column of unique clock values.

**EVIDENCE:** The claimed repair is worded as a not-affixed/not-clock test proving names: `docs/plans/phase-4-columns.md:468-474`. The shipped reader protects a headerless record only through positive membership tests—number among numbers, date among dates, or a repeated label—and otherwise assumes names by convention: `src/synthtwin/reading.py:93-127`, `src/synthtwin/reading.py:136-145`. The reader’s own governing explanation identifies the consequences of a wrong header decision: loss of a record and publication of its value as schema text: `src/synthtwin/reading.py:68-84`.

P4-P3-F7 therefore remains open. The repair needs positive record-membership rules for both new readings, including their comparison/order rules.

### P4-P4-F4 — SEVERITY: blocking

**CONCRETE FAILURE SCENARIO:** In a 100-row column, 40 folded labels exceed the categorical ceiling of 10, while one label occurs 11 times. P4-D5 assigns `long_tail_labels`. If “exactly what a categorical column publishes, under the same invariants, verbatim” includes `level_ceiling`, the block carries `n_distinct_folded = 40` and `level_ceiling = 10`, violating categorical invariant G1. If `level_ceiling` is omitted, the implementation contradicts the plan’s “exactly” and “same invariants” language. Version 6 forbids resolving the ambiguity through an optional key.

**EVIDENCE:** Long-tail detection requires the column to be past the categorical ceiling, while its publication clause claims categorical publication and invariants verbatim: `docs/plans/phase-4-columns.md:845-872`. In the inherited contract, `level_ceiling` is an added categorical key and G1 requires `n_distinct_folded <= level_ceiling`: `docs/spec/profile-contract-v4.md:893-908`. Revision 4 also says the new role sections have fixed key sets with no optional keys: `docs/plans/phase-4-columns.md:1057-1067`.

The plan must state explicitly whether `level_ceiling` exists on `long_tail_labels` and define a satisfiable role-specific invariant.

### P4-P4-F5 — SEVERITY: blocking

**CONCRETE FAILURE SCENARIO:** A 100-row column of distinct currency-prefixed measurements currently lands in free text and publishes no value distribution. Under P4-D4.1 it publishes the core mean, standard deviation, skewness, sign and zero counts, integer-valued fact, numeric styles, fixed-fraction widths, affixed-cell count, endpoints, and ladder. The owner-decision cost and supposedly complete disclosure-delta section price the affix spellings and the endpoints/ladder, but omit most of those newly exposed aggregate and shape facts. The owner can therefore approve the role without the plan recording the full disclosure change it says the decision weighs.

**EVIDENCE:** The role publishes the complete numeric details block and the affixed-cell count: `docs/plans/phase-4-columns.md:568-580`. The owner-decision entry prices two affix spellings and the misrouting risk but does not enumerate the numeric block’s new disclosures: `docs/plans/phase-4-columns.md:212-222`. The “complete” disclosure delta names affixes and endpoints/rungs but omits the other numeric facts: `docs/plans/phase-4-columns.md:1114-1129`. Under the inherited publication doctrine, a free-text column publishes no value anywhere in its block: `docs/spec/profile-contract-v4.md:1296-1312`.

Every newly published affixed-core fact needs a delta row or an explicit grouped row naming its floor treatment or inherited ranges-class justification. Until then, decision 3 is not fully priced.

### P4-P4-F6 — SEVERITY: serious

**CONCRETE FAILURE SCENARIO:** A producer-valid continuous profile comes from three decimal cells `1.2`, `2.20`, and `3.30`, publishing one width-1 cell and two width-2 cells. Both pinned endpoints can be padded to either width. Revision 4 says a pinned value counts toward a width when it “already fits” but does not say which quota claims it when several widths fit. One implementation can write the minimum as `1.2` and maximum as `3.30`; another can write `1.20` and `3.3`. Both preserve endpoints, sign, zero-ness, and width counts, but produce different bytes from the same profile and seed.

**EVIDENCE:** The revised construction protects pinned values and specifies allocation only for unpinned cells; no pinned-width selection order is given: `docs/plans/phase-4-columns.md:748-780`. The governing method fixes call, iteration, and tie orders specifically so implementation detail cannot move a byte: `docs/spec/generation-method-v1.md:170-179`, `docs/spec/generation-method-v1.md:979-1021`. Phase 2’s determinism rule likewise requires draws and output to follow one fixed method: `docs/plans/phase-2-generator.md:723-730`.

The generation-method amendment must be required to define a deterministic pinned-width allocation, including ties among widths a value can wear. The four current rules do not settle it.

### P4-P4-F7 — SEVERITY: serious

**CONCRETE FAILURE SCENARIO:** A time-of-day column has 99 cells in its selected form and one in-slack unparsed cell. Generation writes a counted invented stand-in for that cell. P4-D2 declares this its third invention class, but the quality-report amendment specifies sentences only for fully invented columns and label suppression. A passing quality report can therefore omit the promised explanation for this stand-in class.

**EVIDENCE:** Counted stand-in cells are one of the three classes requiring unconditional explanation: `docs/plans/phase-4-columns.md:351-378`. The quality-report clause covers the first two classes but provides no sentence for counted stand-ins: `docs/plans/phase-4-columns.md:392-406`. Acceptance nevertheless requires the quality report’s per-class sentences to be total: `docs/plans/phase-4-columns.md:1463-1469`.

### P4-P4-F8 — SEVERITY: serious

**CONCRETE FAILURE SCENARIO:** A table has one categorical column with one or more suppressed levels. The generator invents neutral labels for those levels, but the proposed screen count includes only fully invented columns and prints “0 of 1 columns hold invented values.” The screen therefore states the opposite of what the generated twin contains.

**EVIDENCE:** The plan acknowledges that label suppression creates invented cells: `docs/plans/phase-4-columns.md:365-368`. It then limits the screen count to fully invented columns while wording the count as all columns holding invented values: `docs/plans/phase-4-columns.md:387-391`. The governing generation method confirms that every suppressed level receives an invented neutral label: `docs/spec/generation-method-v1.md:1629-1643`.

The count must either include every affected column or say explicitly that it counts only columns whose present cells are all invented.

### P4-P4-F9 — SEVERITY: wording

**CONCRETE FAILURE SCENARIO:** The version 6 contract author follows the phrase “closed six-value vocabulary” literally and retains six format members, despite the same paragraph adding three members to the six inherited ones. Another author follows the explicit additions and writes nine. The plan then fails its purpose of fixing a closed vocabulary unambiguously.

**EVIDENCE:** Version 4 already has six datetime format members: `docs/spec/profile-contract-v4.md:914-918`. Revision 4 adds exactly three but calls the result a six-value vocabulary: `docs/plans/phase-4-columns.md:1071-1083`.

Replace “six-value” with “nine-value.” The explicit member additions and bindings otherwise settle the design.

## VERDICT

**REJECT.**

Blocking items: **P4-P4-F1, P4-P4-F2, P4-P4-F3, P4-P4-F4, and P4-P4-F5**.

This is not a wording-only remainder. Revision 4 still has a shipped-role inversion, an impossible no-regression condition, an unresolved first-record loss, an inconsistent long-tail contract shape, and incomplete privacy pricing. P4-P4-F6 through P4-P4-F8 are additional serious control gaps; P4-P4-F9 is bounded wording.

## What was checked

- The complete revision-4 plan and all round-1 through round-3 review records.
- Each of P4-P3-F1 through P4-P3-F7 against its operative repair, not only the review-record table.
- Charter principle 5 and the one-column statistical-fidelity and honest-limits requirements.
- Ratified Phase 1–3 role order, declaration behavior, first-row evidence, residuals, owner-decision conventions, and acceptance mechanics.
- The profile contract, v4 and v5: carry-by-reference rules, axes, publication classes, forbidden-key discipline, exact key sets, settings enumeration, missing-source accounting, floor rules, datetime formats and dispositions.
- Generation method: one-stream draw order, placement, numeric safeguards, style allocation, label inventions, collision families, exact/approximated obligations, refusal closure, and regeneration consequences.
- Validation method: settings reconstruction, missing-value reading, disclosure gating, report totality, and executable-subcheck obligations.
- Shipped `taxonomy.py`, `parsing.py`, `generation.py`, `validation.py`, `contract.py`, `profile.py`, `reading.py`, `rendering.py`, `summary.py`, `quality.py`, `errors.py`, and `cli.py` where the plan makes behavioral or enumeration claims.
- Privacy attacks over affix fragments and core statistics, long-tail labels, width facts, resolution counts, fixed-fraction widths, and reproduced hole spellings.
- Type-misrouting and order attacks involving empty declared identifiers, new missing literals, binary/constant transitions, datetime widening, affixed sentinels, and headerless files.
- Determinism attacks involving candidate rejection, sorted missing-spelling placement, width assignment, draw budgets, and seed-invariance claims.
- Guard and landing mechanics in the disposition registry, exact-list guard, claim inventory, sealing tool, and tracked-tree scanner.
- Read-only checks: disposition seal current; tracked-tree decontamination scan clean; staged whitespace check clean; draft exact-list and governing-surface assertions passed by direct invocation. No full pytest result is claimed.
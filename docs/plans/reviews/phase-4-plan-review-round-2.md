<!-- Phase 4 plan adversarial review, round 2. Reviewer: codex
(gpt-5.6-sol, high effort), 2026-08-19. Paths in this record are
repository-relative. Wording was adjusted only where the repository's
vocabulary scanner required it; no meaning was changed. -->

# Phase 4 plan review — round 2

**Reviewer:** Codex, adversarial reviewer, 2026-08-19.

**Target:** revision 2 of `docs/plans/phase-4-columns.md`.

## Round-1 repair verification

| Round-1 item | Status | Verification |
|---|---|---|
| P4-P1-F1 | **NARROWED** | Comparing both slashed readings closes the reported 99-versus-100 reversal, but equal contradictory evidence is still treated as a fully ambiguous tie without a remark. See P4-P2-F1. `docs/plans/phase-4-columns.md:720-737`; `docs/plans/phase-1-profiler.md:368-379`. |
| P4-P1-F2 | **NARROWED** | Three format members and resolution bindings are now required, but their wire spellings remain unnamed. See P4-P2-F2. `docs/plans/phase-4-columns.md:965-974`; `docs/spec/profile-contract-v4.md:914-926`. |
| P4-P1-F3 | **CLOSED** | Capacity now subtracts unparsed stand-in cells before comparison, so the round-1 producer witness is not refused. `docs/plans/phase-4-columns.md:620-629`, `docs/plans/phase-4-columns.md:1089-1101`; `docs/spec/generation-method-v1.md:2864-2877`. |
| P4-P1-F4 | **CLOSED** | The revised text unambiguously computes affix readings during cell classification, removes judged cores, re-tallies, and only then performs role selection. `docs/plans/phase-4-columns.md:521-535`; `docs/plans/phase-1-profiler.md:505-515`. The widened eligibility creates a separate fall-through defect, P4-P2-F6. |
| P4-P1-F5 | **CLOSED** | Every `affixed_number` column now receives the code-versus-quantity remark, including repeating decimal-cored tokens. `docs/plans/phase-4-columns.md:563-576`; `CLAUDE.md:63-66`. |
| P4-P1-F6 | **CLOSED** | The plan now distinguishes raw repetition groups from folded suppressed identities and prices the additional fact. `docs/plans/phase-4-columns.md:180-191`, `docs/plans/phase-4-columns.md:770-781`; `docs/spec/profile-contract-v4.md:101-108`. |
| P4-P1-F7 | **CLOSED** | Both width facts now range only over numeric-looking cells, excluding text stragglers. `docs/plans/phase-4-columns.md:671-681`; `docs/spec/profile-contract-v4.md:740-775`. |
| P4-P1-F8 | **NARROWED** | The pooled remainder receives a canonical-writing rule and a nominal window, but assignment of named and pooled widths to generated values remains undefined and may be infeasible. See P4-P2-F5. `docs/plans/phase-4-columns.md:693-707`, `docs/plans/phase-4-columns.md:1085-1088`; `docs/spec/generation-method-v1.md:979-1021`. |
| P4-P1-F9 | **CLOSED** | The settings block is fixed at seventeen keys, with exactly two additions named and the affix/time rules explicitly reusing existing settings. `docs/plans/phase-4-columns.md:985-994`; `docs/spec/profile-contract-v5.md:583-588`. One new key’s permitted range remains defective separately; see P4-P2-F11. |
| P4-P1-F10 | **CLOSED** | The quality-report wording now speaks about the description and what a generated twin would contain, not the measured file’s provenance. `docs/plans/phase-4-columns.md:384-398`; `CLAUDE.md:93-103`. |
| P4-P1-F11 | **STILL OPEN** | P4-D4.2 accepts an in-slack second clock form, while R-P4-5 still says columns mixing the two forms decline. See P4-P2-F8. `docs/plans/phase-4-columns.md:584-603`, `docs/plans/phase-4-columns.md:1272-1276`. |
| P4-P1-F12 | **STILL OPEN** | P4-D3 assigns `affixed_number` to ranges, but P4-D7 still calls its affix publication a labels-class widening. See P4-P2-F7. `docs/plans/phase-4-columns.md:461-473`, `docs/plans/phase-4-columns.md:955-960`, `docs/plans/phase-4-columns.md:1000-1005`. |

## Numbered review items

1. **P4-P2-F1 — Equal but contradictory slashed-date evidence is silently called a fully ambiguous tie**

   **SEVERITY: serious**

   **CONCRETE FAILURE SCENARIO:** A 100-row column contains 98 dates whose two leading fields are both at most 12, one date only the day-first reading accepts, and one date only the month-first reading accepts. Each reading parses 99 cells. With `--day-first`, the declaration wins the tie, the month-first-only cell becomes unparsed, and no evidence-override remark appears. This is not the “fully ambiguous case where evidence cannot” decide described by the plan: the column contains explicit evidence in both directions and is internally inconsistent. The output silently presents one direction as settled instead of reporting the conflict and its counts.

   **EVIDENCE:** Revision 2 says every strict count tie is exactly the fully ambiguous case and gives no remark when the declared direction wins: `docs/plans/phase-4-columns.md:727-736`. The ratified rule currently describes ambiguity specifically as every value being ambiguous and requires the chosen reading to be stated: `docs/plans/phase-1-profiler.md:368-379`. The shipped parser’s first-clearing behavior shows why an explicit conflict outcome is necessary rather than implicit: `src/synthtwin/taxonomy.py:3345-3364`.

2. **P4-P2-F2 — The three new datetime wire members still have no exact values**

   **SEVERITY: serious**

   **CONCRETE FAILURE SCENARIO:** One implementation emits `iso-slash-date` for the new year-leading slashed form; another emits `slashed-iso-date`. A loader written from the other implementation’s contract refuses the document. Both can claim compliance because revision 2 names what each member means but never fixes the literal string. The same ambiguity applies to the month and joint-family members and to the member names used inside `resolution_mix`.

   **EVIDENCE:** The “complete” delta specifies three descriptive members but gives none of their exact wire spellings or the `resolution_mix` key vocabulary: `docs/plans/phase-4-columns.md:952-976`. The carried contract defines the existing format vocabulary as six exact strings and binds each exact member to a resolution: `docs/spec/profile-contract-v4.md:910-926`, `docs/spec/profile-contract-v4.md:974-976`. The shipped parser likewise dispatches on exact format strings: `src/synthtwin/parsing.py:61-80`, `src/synthtwin/parsing.py:842-919`.

3. **P4-P2-F3 — `HH:MM` generation interpolates in an ordinal space its published form cannot represent**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A 100-row, over-ceiling column contains eleven distinct `HH:MM` values between `00:00` and `00:10`, repeated across the rows. It takes `time_of_day`. Revision 2 converts the ladder to seconds of day and floor-divides interior ranks. Most resulting ordinals have non-zero seconds. Writing them as `HH:MM` either truncates the generated value, violating the stated interpolation and potentially its rung window, or adds seconds, violating the exact published form and causing the column to re-profile differently. The correct ordinal unit must be minutes for `HH:MM` and seconds for `HH:MM:SS`, with the construction and windows derived in that form-specific space.

   **EVIDENCE:** The plan defines every clock ladder in seconds of day, requires floor-division interpolation, and simultaneously requires all cells to use the one published form: `docs/plans/phase-4-columns.md:605-626`. The ratified datetime method makes the ordinal unit a function of the published resolution precisely so every ordinal has a canonical representation: `docs/spec/generation-method-v1.md:1286-1310`; its interpolation promises ordinals inside that representable space: `docs/spec/generation-method-v1.md:1327-1366`. The Phase 2 plan requires datetime generation “in ordinal space at the recorded resolution”: `docs/plans/phase-2-generator.md:696-711`.

4. **P4-P2-F4 — Mixed-ISO form quotas can be incompatible with the generated datetime ordinals**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A 100-row column contains 50 ISO date-only cells across distinct days and 50 ISO datetime cells. Neither single format clears the 99% line, so the joint format takes the column at `datetime` resolution and publishes exact 50/50 form counts. The existing datetime transform generates interior second ordinals. Assigning date-only forms to ranks in a fixed order can assign a date form to a non-midnight ordinal. Writing that rank as a date truncates its time and changes its measured value; writing the time preserves the value but misses the exact form count. The source proves some association between forms and values existed, but `resolution_mix` publishes only margins and loses that association.

   **EVIDENCE:** Revision 2 publishes exact form counts and merely says forms are assigned to ranks in a fixed order: `docs/plans/phase-4-columns.md:648-666`, `docs/plans/phase-4-columns.md:1085-1088`. The ratified generator produces datetime-resolution interiors in whole seconds: `docs/spec/generation-method-v1.md:1288-1296`, `docs/spec/generation-method-v1.md:1327-1366`. Its current representation table is deliberately complete and states that a date-form cell cannot represent a datetime-resolution value: `docs/spec/generation-method-v1.md:1436-1465`. Revision 2 supplies no replacement packing, feasibility rule, or authorized disposition for this new conflict.

5. **P4-P2-F5 — Fraction-width quotas still lack a deterministic and value-preserving allocation**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** At floor 11, a numeric column has twenty decimal cells of fraction width two and one cell of width three. The profile publishes width two at 20 and pools one cell. Revision 2 says the pooled cell uses its own value’s canonical spelling, but it never determines which generated value receives that pooled status, which twenty receive the named width, or what happens when a generated non-whole value cannot be written at width two without changing its value. Two implementations can select different pooled cells and produce different bytes; an implementation that rounds a value to force width two silently alters the numeric distribution.

   **EVIDENCE:** P4-D4.5 provides only per-width recount bounds and the pooled cell’s final spelling: `docs/plans/phase-4-columns.md:693-707`. P4-D8 says widths “join” quotas without defining assignment order, spellability, tie-breaking, or a conflict outcome: `docs/plans/phase-4-columns.md:1085-1088`. The cited G6.4 precedent does not supply those missing width rules: its deterministic behavior comes from an explicit stratum walk, candidate restrictions, quota ordering, and tie order spanning more than forty lines: `docs/spec/generation-method-v1.md:979-1021`. D12 requires draw order and output bytes to be fixed, including when a method change shifts later columns: `docs/plans/phase-2-generator.md:723-741`.

6. **P4-P2-F6 — Widened sentinel eligibility can remove a value and then make the affix role disappear**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** In 100 rows, 98 cells use prefix `A` with twenty ordinary numeric cores repeated fewer than eleven times each, one cell is `A-999`, and one cell is ordinary text. Before sentinel removal, the exact affix pair covers 99 cells and clears the parse line. The `-999` core passes the outlier/share rule and is removed. After re-tallying, only 98 of 99 surviving cells carry the pair, so `affixed_number` fails its 99% line; categorical and long-tail also fail, and the column becomes free text. A valid opaque token was converted to a hole, but the standing code-versus-quantity remark is emitted only for columns that actually retain the affixed role. The no-regression battery sees no forbidden role transition because both old and new outcomes are `free_text`.

   **EVIDENCE:** Revision 2 widens sentinel eligibility to an affixed reading, removes candidates before role selection, and explicitly permits the role to disappear after removal: `docs/plans/phase-4-columns.md:521-535`. Its standing warning is limited to “EVERY affixed-number column”: `docs/plans/phase-4-columns.md:563-576`. Its regression battery compares roles only: `docs/plans/phase-4-columns.md:1188-1193`. Shipped sentinel judging currently runs only when the combined numeric-looking population reaches the line and rebuilds every tally after removal: `src/synthtwin/taxonomy.py:4518-4555`. If the resulting role publishes nothing, the exact candidate spelling is filtered from the block: `src/synthtwin/taxonomy.py:4406-4441`. The charter forbids silent miscasting: `CLAUDE.md:63-66`.

7. **P4-P2-F7 — `affixed_number` still has contradictory publication-class doctrine**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** An implementer extends the exact-one-class tuples and forbidden-key matrix. P4-D3 directs them to put `affixed_number` in ranges and add an exception to the ranges doctrine. P4-D7 directs them to widen the labels-class sentence, and the disclosure delta again calls the affix a labels-sentence widening. Following D3 leaves the labels class untouched; following D7 changes it. Both cannot be the “complete” v6 contract.

   **EVIDENCE:** P4-D3 assigns the role to ranges and says the labels class is untouched: `docs/plans/phase-4-columns.md:461-473`. P4-D7 item 1 instead requires a widened labels-class sentence: `docs/plans/phase-4-columns.md:955-960`; item 7 repeats that description: `docs/plans/phase-4-columns.md:1000-1005`. The shipped doctrine makes the three role classes disjoint and defines ranges as carrying no spelling: `src/synthtwin/taxonomy.py:247-264`. This is the same unresolved design question as P4-P1-F12, not a complete repair.

8. **P4-P2-F8 — The mixed-clock contradiction remains in the residual register**

   **SEVERITY: serious**

   **CONCRETE FAILURE SCENARIO:** A 100-row, over-ceiling column contains 99 `HH:MM` cells across more than ten distinct values and one `HH:MM:SS` cell. P4-D4.2 says the minute form clears the line and the second-form cell becomes one unparsed stand-in. R-P4-5 says columns mixing those forms decline. The contract, profiler, summary, and residual ledger can therefore implement opposite outcomes from the same plan.

   **EVIDENCE:** Acceptance of the minority form as unparsed is explicit in P4-D4.2: `docs/plans/phase-4-columns.md:584-603`. The residual says the mixed column declines: `docs/plans/phase-4-columns.md:1272-1276`. The ratified taxonomy uses a count-based 99% line rather than a veto by any contrary cell: `docs/plans/phase-1-profiler.md:368-383`. P4-P1-F11 is therefore still open.

9. **P4-P2-F9 — An EXACT-OBSERVABLE hole fact is still permitted to miss as a named deviation**

   **SEVERITY: blocking**

   **CONCRETE FAILURE SCENARIO:** A numeric profile publishes a floor-cleared hole spelling representing `1`, while its generated range and interpolation can produce a present value spelling that also reads as `1`. If the collision repair cannot find another value inside its allowed window, P4-D6.1 permits the implementation to write the collision and print a named deviation. Re-description then counts the generated present cell as absent, so presence totals and the per-spelling hole recount miss. The plan nevertheless classifies `missing_by_source` as EXACT-OBSERVABLE and allows the same deviation in acceptance criterion 7.

   **EVIDENCE:** The collision paragraph permits either proving the corner empty or naming a deviation: `docs/plans/phase-4-columns.md:872-886`. The next paragraph strengthens `missing_by_source` to EXACT-OBSERVABLE: `docs/plans/phase-4-columns.md:888-903`. Acceptance still authorizes the collision if a deviation prints: `docs/plans/phase-4-columns.md:1349-1353`. The ratified definition of EXACT-OBSERVABLE requires exact reproduction independently recounted from the CSV; only APPROXIMATED facts may use a bounded lesser result: `docs/spec/profile-contract-v4.md:76-89`. A newly discovered impossible corner must either be refused, proved unreachable, or explicitly reclassified by owner-authorized amendment; an exact fact cannot acquire a report-only escape.

10. **P4-P2-F10 — Owner decision 8 is allowed after the contract artifact that already encodes it**

    **SEVERITY: serious**

    **CONCRETE FAILURE SCENARIO:** Decisions 1–7 are taken and the v6 contract is ratified at stage 3 with required setting `day_first`. The plan permits decision 8 to remain pending until stage 6. The owner then declines decision 8. The already-ratified contract contains a required key and format behavior whose authority was never taken, so it must be amended and re-sealed after the sequencing section said the complete contract was already ratified.

    **EVIDENCE:** The precondition says decisions 1–7 precede stage 3 but decision 8 need only precede stage 6: `docs/plans/phase-4-columns.md:157-167`; acceptance repeats that split: `docs/plans/phase-4-columns.md:1316-1321`. The supposedly complete stage-3 contract requires `day_first` as one of its exactly seventeen settings: `docs/plans/phase-4-columns.md:985-994`. The plan’s own general rule is that every decision precedes the artifact that encodes it: `docs/plans/phase-4-columns.md:169-178`. Decision 8 must therefore precede stage 3 as well.

11. **P4-P2-F11 — `long_tail_minimum_level` has no closed permitted range, allowing the privacy lower bound to disappear**

    **SEVERITY: blocking**

    **CONCRETE FAILURE SCENARIO:** One conforming loader treats `long_tail_minimum_level` as exactly 11 because P4-D5 calls 11 a constant. Another accepts any positive whole number because P4-D7 calls 11 only the default and gives no permitted range. Under the second reading, settings with both the publication floor and this key set to 1 make an over-ceiling all-different column qualify for `long_tail_labels` and publish every singleton. That directly contradicts the promised invariant that lowering the publication floor cannot make a new column label-publishing.

    **EVIDENCE:** P4-D5 says the fixed lower bound of eleven keeps all-different columns free text at every floor: `docs/plans/phase-4-columns.md:759-768`. P4-D7 defines the key only as “a whole number, default eleven,” without saying `== 11` or `>= 11`: `docs/plans/phase-4-columns.md:985-994`. The carried contract gives every settings key an explicit type and permitted range: `docs/spec/profile-contract-v4.md:274-297`. The validator must consume every settings field exactly because a skipped or invented threshold changes re-description and can bypass the disclosure gate: `docs/spec/validation-method-v1.md:139-148`; the shipped implementation states the same consequence: `src/synthtwin/validation.py:938-1009`.

## VERDICT

**REJECT.**

Blocking items: **P4-P2-F3, P4-P2-F4, P4-P2-F5, P4-P2-F6, P4-P2-F7, P4-P2-F9, and P4-P2-F11**.

Revision 2 still cannot be implemented without making up behavior for minute-form interpolation, mixed-ISO form allocation, fraction-width assignment, publication-class membership, and a privacy-bearing settings range. It also expressly permits an exact hole obligation to miss, and the widened sentinel path can convert a valid affixed value to missing while falling out of the role whose standing warning was meant to guard the misroute.

## What was checked

- Canonical reviewer and implementer briefs, including principle 5, statistical-fidelity claims, validation provenance, the profile/generator boundary, and D12.
- Every round-1 item against revision 2, classified above as CLOSED, NARROWED, or STILL OPEN.
- Complete revision-2 plan: sequencing, owner decision gating, taxonomy order, new roles, long-tail detection, missing-data reproduction, v6 delta, method amendments, validation amendments, acceptance criteria, residuals, and review record.
- Ratified Phase 1, Phase 2, and Phase 3 conventions governing parse-line arithmetic, sentinel order, publication classes, exact dispositions, datetime ordinal spaces, single-stream determinism, settings replay, and method-owned validation windows.
- The profile contract, v4 and v5: exact settings counts, format and resolution vocabularies, no-optional-key rule, publication classes, forbidden-key matrix, missing-source invariants, and disposition meanings.
- Generation method: numeric style allocation, datetime ordinal units and representation totality, all-different scope, finite-domain refusals, exact-versus-approximated outcomes, draw ordering, and regeneration events.
- Validation method: producer-based re-description, exact settings consumption, independently specified windows, measured-file-neutral wording, disclosure gating, and verdict honesty.
- Shipped taxonomy and parsing: actual role order, count-based 99% line, first-clearing date format, sentinel eligibility/removal/re-tally, publication filtering, folded versus raw identities, exact format strings, and current class tuples.
- Shipped generation, validation, contract, profile, reading, rendering, summary, quality, errors, and CLI enumeration or rendering surfaces implicated by the plan.
- Statistical and type attacks over contradictory slashed dates, minute-form clock interpolation, mixed clock forms, mixed ISO resolutions, affixed opaque tokens, sentinel-triggered fall-through, and fraction-width spellability.
- Privacy attacks over long-tail lower bounds, affix fragments, folded suppressed groups, floor-free ranges and widths, resolution mixes, fraction widths, and reproduced hole spellings.
- Determinism attacks over named-versus-pooled width assignment, mixed-form rank assignment, sorted hole-spelling placement, draw budgets, single-stream shifts, seed-invariance scope, and D12 regeneration.
- Governance machinery: draft exact-list admission, `GOVERNING` timing, disposition seal coverage, claim-inventory derivation, owner-decision sequencing, stage ordering, and acceptance verifiability.
- The tracked-tree decontamination scan completed cleanly; staged whitespace checking completed cleanly; the current disposition seal reported current. No repository file was modified.
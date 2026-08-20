VERDICT SOUND_WITH_CORRECTIONS errors=12

## ERRORS

1. §4.4 settings table, `day_first` row — INTERNAL CONTRADICTION, and the plan governs against it. The cell reads "true when the person declared that slashed dates in this table are day-first, so slashed dates were read day-first-preferring", which is version 6's gloss transcribed unaltered (docs/spec/profile-contract-v6.md:1186; docs/spec/profile-contract-v6.md:375-376). The paragraph the section itself places three blocks below says "It does not record which reading any column took". Both cannot stand. The ratified plan is evidence-first — "BOTH slashed readings are counted, and the reading that parses strictly more cells wins whatever the declaration said; the declaration decides only a count tie" (docs/plans/phase-4-columns.md:890-893) — and the plan governs on conflict (the writer reported this disagreement and resolved it correctly in prose, then left the contradicting gloss in the normative cell). Cell rewritten to record the DECLARATION and to point at the paragraph.

2. §4.4, "What does NOT join the list" — WRONG REASON TRANSCRIBED for `missing_by_source`. The section says it leaves the list because "this contract applies the floor to the exact spelling, so at a floor of one every spelling is named and the map carries no pooled remainder to be zero", citing the exact-spelling floor (docs/spec/profile-contract-v5.md:363-371, C5-8). That is not why it left. Version 5's own stated reason is that the map has no pooled key AT ANY FLOOR: "the list LOSES `missing_by_source`, whose pooled `(withheld)` entry no longer exists" (docs/spec/profile-contract-v5.md:1023-1024), the key having been struck from the format with its count moved to `n_missing_withheld` (docs/spec/profile-contract-v5.md:984-987; docs/spec/profile-contract-v5.md:554). As transcribed the sentence implies `missing_by_source` DOES carry a pooled remainder at floors above one, which C5-N5 forbids outright — "No key of `missing_by_source` has a first-party meaning" (docs/spec/profile-contract-v5.md:491-495). Reason replaced with the sourced one.

3. §4.4, "Why S13 is a rule of its own" — STALE ACCOUNTING that no longer covers the section's own ten-position list. The paragraph is version 4's, transcribed at its version 4 arithmetic — "N2, N4, D3 and P2 each say a PUBLISHED count is at least the floor, and each exempts the pooled remainder… Four exemptions and one unbounded count" (docs/spec/profile-contract-v4.md:365-373) — while the list above it is version 6's, with ten positions. Two independent shifts break it. (a) N4 no longer exempts anything: "in version 5 the exemption is gone… `n_missing_withheld` carries no such bound in either direction" (docs/spec/profile-contract-v5.md:480-489; the invariant row is docs/spec/profile-contract-v5.md:1006), so `n_missing_withheld` is an UNBOUNDED count, not an exemption. (b) `fraction_widths`'s `(withheld)` is a new exemption nobody counted: P6 reads "the `(withheld)` value is 0 or at least 1" (docs/spec/profile-contract-v6.md:593-594) and P5.a permits it nonzero at any floor (docs/spec/profile-contract-v6.md:549-551), so only S13 forces it to zero at a floor of one — exactly the case this paragraph exists to justify. The section already names P6 in its "No other rule is relaxed" list (from docs/spec/profile-contract-v6.md:593-594) and then omits it here, so the section contradicts itself. Corrected to FOUR exemptions (N2, D3, P2, P6) and TWO unbounded counts (`n_missing_withheld`, `n_sentinel_candidates_unpublished`), which accounts for six positions; with the four caught by B5, the multiplicity rule and B4, the ten-position list closes exactly.

4. §4.4, K3 — the disjointness proof is short one pair. The transcription widens version 5's two-list argument ("no declaration can be in both lists, since nothing section 14.1 spells reads as a number", docs/spec/profile-contract-v5.md:773-775) to three lists by adding text-vs-date, but never rules out one declaration landing in both `built_in_numbers` and `built_in_dates`. C6-K3 states only the arithmetic (docs/spec/profile-contract-v6.md:747-749), so nothing else in the document closes it. The missing clause is true of the fixed lists — no stand-in number (−9999, −999, 9999) is a calendar day spelling and neither placeholder reads as a number (docs/spec/profile-contract-v6.md:652-653) — and is now written out, because K3's whole `<=`-not-`==` argument rests on the three-way partition.

5. §4.4, settings-block scope paragraph — DROPPED OBLIGATION. Version 5 states "Every readable surface must state the column route where it states the settings rule — plan amendment A-P3-31 fixes that obligation, and the claim inventory holds the surfaces to it" (docs/spec/profile-contract-v5.md:863-865). It appears nowhere in the transcription, although the parallel floor obligation (A-P3-11, docs/spec/profile-contract-v4.md:381-391) is carried in full three blocks later. Restored.

6. §4.4, "What a reader can infer FROM THE SETTINGS BLOCK" — DROPPED REASON. The transcription ends "Priced, and on the owner's authority, ruled 2026-08-17 with this delta stated to them." Version 5 states WHY the ruling went that way: "taken because the alternative leaves a researcher who rescues one of synthtwin's own words without a usable check on the table the description was written from" (docs/spec/profile-contract-v5.md:878-882). The brief requires a rule's stated reason to travel with it — that reason is how a reviewer tells this ruling from an accident. Restored.

7. §4.4, K5 — DROPPED BOUND. Version 5 states of the lists that "It carries no count of cells, no column, no row and no text of the table" (docs/spec/profile-contract-v5.md:839-842). The transcription keeps only the second half of that sentence ("not evidence that any cell wore the word") and drops the enumeration of what the lists do not carry. It survived version 5 only inside a delta-shaped paragraph ("a reader of a version 4 description is told…"), which is presumably why de-delta-ing lost it; the bound itself is not delta-shaped. Restored to K5.

8. §4.4, C6-20 membership sentence — INCOHERENT AS WRITTEN. "A sixteenth key, an eighteenth key, or one of the seventeen skipped, is a document this contract does not describe" follows "All seventeen keys are REQUIRED", under which a "sixteenth key" is one of the required seventeen, not a violation. The plan's sentence is about the SIZE of the block: "A sixteenth-or-eighteenth key, or a key skipped, is red against the contract's own enumeration in both directions" (docs/plans/phase-4-columns.md:1218-1219). Rewritten as a block of sixteen keys or of eighteen.

9. §4.4, `long_tail_minimum_level` paragraph — wrong word for a threshold this section also names as a key. It says "a column past the categorical cap"; C6-15 says "A column past the categorical ceiling" (docs/spec/profile-contract-v6.md:340-341). In this very table `categorical_ceiling` is a key and "the effective cap" is the different quantity `min(categorical_ceiling, categorical_share of n_rows)` bounded below by `categorical_floor` (docs/spec/profile-contract-v4.md:287-289; src/synthtwin/taxonomy.py:1165-1176). The two must not be swapped in a normative summary of another section's rule. Corrected to "ceiling".

10. §4.4, "THE LIST IS EXHAUSTIVE" paragraph — DROPPED PROVENANCE. Version 5 carries "(plan amendment A-P3-32, review item P3-V9-F2)" on this heading (docs/spec/profile-contract-v5.md:1036-1037). The transcription drops it while keeping every other amendment citation in the section (A-P3-11, A-P3-16). Word-for-word diff otherwise clean. Restored.

11. §4.4, "What enters a list", final sentence — AMBIGUITY IMPORTED FROM A NARROWER SOURCE. "A declared value that is none of these enters no list, and `n_declared` counts it" is version 5's sentence about one specific value (`WOMBAT`, docs/spec/profile-contract-v5.md:626-627); lifted into a general rule it reads as though `n_declared` counted only non-members. `n_declared` counts EVERY different value named, member or not (docs/spec/profile-contract-v5.md:674-676). Misreading this field is the documented consumer failure the 2026-08-17 amendment exists to end (docs/spec/profile-contract-v5.md:690-695). Clarified.

12. VERIFICATION RECORD (not an error), so the assembler need not redo it. Every enumeration in this section was checked element by element in BOTH directions against its shipped constant. Top-level keys: 9, set-identical to `TOP_LEVEL_KEYS` (src/synthtwin/contract.py:129-139). `source` keys: 5, set-identical to `SOURCE_KEYS` (src/synthtwin/contract.py:141-147); `encoding` values match `ENCODINGS` and `header_source` values match `HEADER_SOURCES` (src/synthtwin/contract.py:305-307). Settings keys: 17 rows, all distinct, in true ascending code-point order; set difference against `SETTINGS_KEYS` (src/synthtwin/contract.py:149-165) is exactly {`day_first`, `long_tail_minimum_level`}, nothing missing, nothing extra (docs/spec/profile-contract-v6.md:373-376). Declaration-record keys: 5, being `DECLARATION_KEYS` (src/synthtwin/contract.py:167-176) plus `built_in_dates` (docs/spec/profile-contract-v6.md:738-740). Vocabulary arithmetic used by K1/K2/"What enters a list": 17 folded + 1 exact-spelling = 18 text spellings, 3 stand-ins, 2 placeholders (docs/spec/profile-contract-v6.md:646-655) — correct, and the section rightly avoids restating version 5's stale "thirteen" at docs/spec/profile-contract-v5.md:849-852. `relationships` "eight keys" matches `RELATIONSHIP_KEYS`, 8 members (src/synthtwin/contract.py:196-205). "eighteen characters" for `n_missing_withheld` is 18. S13's list holds ten positions, the same set as docs/spec/profile-contract-v6.md:608-612. Word-level diffs: §4.1 (table + paragraph), §4.2 (S1-S4) and §4.3 (table, membership rule, S5, S6, required sentence) are byte-identical to docs/spec/profile-contract-v4.md:195-272 apart from `4`→`6`; the floor's "What is given up" paragraph is identical to docs/spec/profile-contract-v4.md:322-335 apart from the section-number pointer; the exhaustive-walk paragraph is identical to docs/spec/profile-contract-v5.md:1036-1047 apart from the dropped citation noted above. S5/S6 are enforced as stated at src/synthtwin/contract.py:2337 and :2344. The two sentinel meaning cells match the shipped judging code (src/synthtwin/taxonomy.py:2958-2964). No delta framing survives: no "supersedes", no "carried", no "unchanged from version 5". The four declared gaps (the §14.1 vocabulary cross-reference, the §3.3/§10/absent-cell section numbers, the version rule's identifier, and the N2/N4 letters) are real and correctly left to the assembler; none of them is resolvable from the artifacts in this range.

## GAPS

- CROSS-REFERENCE TO THE PUBLISHED VOCABULARY. K1, K2, K5 and S7 all point at the section that enumerates the 23 members. I wrote "section 14.1", following version 5's placement (v5:1350, "14.1 The published vocabulary — NORMATIVE from version 5"), because my sections follow version 4's skeleton and version 4's section 14 is the enumeration appendix. The delta version 6 puts the same list at its section 5.1 (v6:640). The assembler must settle one number and fix these four references; I could not establish it from the artifacts.
- SECTION REFERENCES I COULD NOT PIN. §4.1's version paragraph points at "section 3.3" (canonical round trip, v4:180-182) and "section 10" (loader order of operations and the refusal text, v6:1261-1275) without naming a clause identifier; §4.4's S7 scope paragraph points at "this contract's absent-cell rules" instead of a number, because version 5 cited its own "3.2 way 4" and version 6 cites six ways (v6:774), and I could not establish which section of the self-contained document will carry them.
- IDENTIFIER FOR THE VERSION RULE. Version 6's delta gives it C6-44 (v6:1265) and version 5 gave it C5-24 plus a C5-VER row (v5:1063, v5:1018). I stated the rule in §4.1 without an identifier and left the numbering to whoever writes §10; if §10 keeps C6-44, a back-reference here would be an improvement.
- N2's IDENTIFIER MAY DANGLE. My floor paragraph names N2 and N4 among the floor-governed invariants, following v4:337-344. Version 6's delta folds version 4's N1 and N2 into a single clause C6-N3 (v6:676-681), and version 5 restated N4 as C5-N4 (v5:1006). Whatever the absent-cells section of the self-contained document letters these, my two references must be reconciled with it. I kept the version 4 letters because the identifier rule says a transcribed rule keeps its identifier.
- PLAIN-NUMBERED CLAUSES I FOLDED RATHER THAN RENUMBERED. C5-16 (the lists are a function of the command line alone, v5:645-651), C5-17 (only a vocabulary member is written into the lists, v5:653-660) and C5-18 (what n_declared counts, v5:674-681) carry no letter, so the identifier rule gives no guidance on what they become. I folded C5-16 into K5's statement, C5-17 into "What enters a list", and C5-18 into the n_declared table cell and the paragraph under it, rather than minting new C6- numbers that could collide with another section's. The assembler must confirm nothing was lost and that C6-48's six-way closure proof (v6:768-827) and C5-19/C5-20 (v5:716-754) land in whichever section carries the absent-cell walk — none of that is in my range.
- BD-P IS FOLDED INTO K5. Version 6's invariant list carries a separate producer row BD-P for `built_in_dates` (v6:1228). In a self-contained document that is the same obligation K5 already states, so I wrote K5 over all six lists and did not keep BD-P as a second identifier. Flagging it so the assembler does not report a dropped rule.
- TWO MEANING CELLS ARE NOT FROM A SPEC SOURCE. `sentinel_outlier_iqr_multiple` and `sentinel_minimum_share` have a RANGE in version 4 (v4:290-291) and no meaning anywhere in versions 4, 5 or 6, and no comment in `taxonomy.Settings` (taxonomy.py:1177-1178). I wrote their meanings from the shipped judging code (taxonomy.py:2958-2964): the IQR multiple sets the outlier test, the share sets the frequency test. These are the only two meaning cells in my seventeen-row table not transcribed from a specification source, and they should be checked by whoever owns the sentinel section.
- DEFAULTS ARE NOT STATED FOR FIFTEEN OF THE SEVENTEEN KEYS. `taxonomy.Settings` carries a default for every key (taxonomy.py:1141-1234), but no source states any of them as a normative wire fact, so I put none in the table. The two exceptions I did state are `small_cell_floor`'s default of 11 (contract.py:190, and version 4's §4.4 already speaks of "under the default", v4:381) and `day_first`'s default of false (v6:375-376, plan:1208).
- `forced_identifiers` MAY BE EMPTY — not stated anywhere. Version 4's row (v4:297) gives no minimum length and A1 (v4:532-533) is a biconditional that is satisfied by an empty list, so an empty array conforms. I did not add a sentence saying so, because no source says it.
- THE SHIPPED VOCABULARY IS BEHIND THIS CONTRACT, AND THAT IS EXPECTED. K1 points at a 23-member vocabulary (v6:646-655), while the shipped source still carries version 5's thirteen. I took the enumeration from the contract and the plan rather than from the shipped constant, because the closure material warns (closure:33) that "the shipped constant governs" is stated in v6 §14 of the SETTINGS LIST ONLY (v6:1651-1655), and generalizing it would make version 6's own `format`, `resolution` and `profile_version` defective. For the settings key spellings, which is where that rule does apply, I transcribed contract.py:149-165 element by element.

## DISAGREEMENTS

- SETTINGS KEY ORDER: version 4's table and the shipped constant differ in ORDER, not in membership. v4:282-297 lists the fifteen in a reading order beginning `small_cell_floor`; `contract.SETTINGS_KEYS` (contract.py:149-165) lists them in ascending code-point order beginning `categorical_ceiling`. I checked the two SETS element by element and they are identical, and the count is 15 both ways. I used the shipped order, because it is also the canonical wire order (v4:122-127, `sort_keys=True`) and because version 6 §14 writes them that way for auditability (v6:1642-1648). No rule is affected.
- "VERSION 5'S FIFTEEN" vs "VERSION 4'S FIFTEEN": C6-20 says the seventeen are "version 5's fifteen" (v6:374) while §14 says "Version 4's fifteen" (v6:1641). Both are true of the same set — version 5 added `built_in_texts` and `built_in_numbers` INSIDE the two declaration records and states "`settings` itself still has exactly fifteen keys; nothing is added at its top level" (v5:587-588). Not a substantive conflict; I wrote neither phrase, since a self-contained document names the seventeen directly.
- WHAT `day_first` RECORDS. Version 6's key table glosses it as "slashed dates read day-first-preferring" (v6:1186) and C6-20 as "recording that slashed dates were read day-first-preferring" (v6:375-376), which reads as though the key recorded the reading a column TOOK. The plan's own mechanics are evidence-first: both slashed readings are counted, the one parsing strictly more cells wins whatever the declaration said, and the declaration breaks only a count tie (plan:889-893). Version 6 resolves it elsewhere — the slashed-date remark is "carried whenever the OPTION WAS GIVEN and a slashed reading was in play" (v6:1112-1113). The plan governs on conflict, so I wrote the key as recording that the DECLARATION was made, with a paragraph saying explicitly that it does not record which reading a column took. Reporting it rather than conforming silently.
- S13's TAIL. Version 4's S13 ends its list with an open-ended "and under that word wherever else a counted block may carry it" (v4:351-352). Version 5 removed that tail and declared the list exhaustive (v5:1036-1047), and version 6 restates it exhaustive with one position added (v6:600-605, v6:632-633). I wrote the exhaustive ten-position list and dropped version 4's tail deliberately; a reader comparing my §4.4 with version 4 will see a sentence missing, and this is why.
- C6-S13 IN THE DELTA IS ITSELF DEFECTIVE ON THE CLOSURE MATERIAL'S JUDGEMENT, and I repaired it. v6:634-636 ends by re-importing version 5's "which keys a searching loader must not read as names" paragraph by reference — "stands entire and unrepeated here" — after superseding the list that paragraph quantifies over. The closure material scores that row PARTIAL and names it as exactly the defect a self-contained document ends (closure:70, closure:112). I transcribed that paragraph in full from v5:1036-1047 rather than pointing at it.
- COUNT CHECKS AGAINST THE BRIEF'S VERIFIED LIST, all confirmed, none in disagreement: 17 settings keys (15 in contract.py:149-165 plus `day_first` and `long_tail_minimum_level`); 5 declaration-record keys (4 in contract.py:171-176 plus `built_in_dates`, v6:738-740); 23 published-vocabulary members (18 + 3 + 2, v6:646-655) as used by K1; 9 top-level keys and 5 `source` keys, both matching contract.py:129-147. My section touches none of the role, format, resolution, precision, clock-form, absence-class or note-form enumerations.

## SOURCES

All paths are relative to the repo root
`/Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin`.
"v4" = `docs/spec/profile-contract-v4.md`, "v5" =
`docs/spec/profile-contract-v5.md`, "v6" =
`docs/spec/profile-contract-v6.md`, "plan" =
`docs/plans/phase-4-columns.md`, "closure" =
`docs/plans/reviews/material/phase-4-v6-derivation-closure.md`.

| rule / element in my section | source (file:line) |
|---|---|
| §4.1 nine-key table, all nine rows verbatim | v4:195-209 |
| the nine names and their count checked against the shipped tuple | `src/synthtwin/contract.py`:129-139 (`TOP_LEVEL_KEYS`, 9 members) |
| `profile_version` row changed from `4` to `6` | v6:1265-1266 |
| `created_with` fallback spelling `0+unknown` | v4:201; `src/synthtwin/profile.py`:315 |
| "settings, publication_notes and relationships each carry ONE disposition" paragraph | v4:210-213 |
| top-level dispositions (STRUCTURAL / LOADER-ONLY / EXACT-OBSERVABLE) cross-checked | v4:2015-2033 (§9.1 disposition matrix) |
| **The version key** paragraph — producer writes 6, loader reads exactly 6, refuses every other integer | v6:1265-1267 |
| — no upgrade, no partial acceptance, converting would mean making up facts | v6:1271-1273 |
| — read before the canonical round trip, direction-correct advice | v6:1267-1269; v5:1063-1068 (order of operations, step 5 before step 6) |
| §4.2 head sentence ("These four rules… plan P2-D6, item P2-R5-F6") | v4:217-219 |
| **S1 — length** | v4:221 |
| **S2 — position** | v4:223-225 |
| **S3 — list order is the schema**, all three bullets + the "Without S3" reason | v4:227-238 |
| **S4 — names** | v4:240-243 |
| S1–S4 restated form cross-checked | v4:1841-1844 |
| §4.3 head, "exactly these five keys and no others" | v4:247 |
| §4.3 five-key table, all five rows verbatim | v4:249-255 |
| the five names and their count checked against the shipped tuple | `contract.py`:141-147 (`SOURCE_KEYS`, 5 members) |
| `encoding` permitted values `utf-8-sig`, `latin-1` | v4:251; `contract.py`:305 (`ENCODINGS`) |
| `header_source` permitted values `file`, `generated` | v4:253; `contract.py`:307 (`HEADER_SOURCES`) |
| §4.3 membership rule | v4:257-258 |
| **S5** | v4:260-261; enforcement `contract.py`:2337 |
| **S6** | v4:263-265; enforcement `contract.py`:2344 |
| **The required sentence** (Phase 1 R1 residual, plan P2-D6) | v4:267-272 |
| §4.4 head — "exactly these seventeen keys", subtree LOADER-ONLY, generator reads it only for floor-governed facts | v4:274-279 (fifteen → seventeen from v6:371-373) |
| seventeen = fifteen + two | v6:373-376; v6:1640-1651; plan:1205-1219 |
| ascending code-point order is the canonical object order | v4:122-127 (§3.2, `sort_keys=True`) |
| the fifteen inherited key SPELLINGS, transcribed element by element | `contract.py`:149-165 (`SETTINGS_KEYS`, 15 members) |
| the same fifteen cross-checked against the contract text | v4:282-297; v6:1643-1648 |
| `categorical_ceiling`, `categorical_floor`, `categorical_share` ranges | v4:287-289 |
| — their meanings | `src/synthtwin/taxonomy.py`:1165-1176 |
| `day_first` type, default and meaning | v6:375-376; v6:1186; plan:1208-1209 |
| `declaration_matching` permitted value | v4:294; `taxonomy.py`:470 (`DECLARATION_MATCHING`) |
| — its meaning (the exact-number-else-spelling rule) | `taxonomy.py`:1185-1191 |
| `declaration_publication` permitted value | v4:295; `src/synthtwin/profile.py`:294 |
| — its scope ("settings counts only, columns unchanged") | `profile.py`:255-294 |
| `declared_missing_values`, `kept_values` as objects | v4:292-293, raised to five keys by v6:738-740 |
| `forced_identifiers` | v4:297 |
| `identifier_minimum_rows` range / meaning | v4:285 / `taxonomy.py`:1149-1153 |
| `identifier_uniqueness` range / meaning | v4:284 / `taxonomy.py`:1142-1148 |
| `long_tail_minimum_level` type and only-value | v6:376-379; v6:1187; plan:1209-1215 |
| `minimum_parse_rate` range / meaning | v4:286 / `taxonomy.py`:1154-1164 |
| `near_threshold_slack` range / meaning | v4:296 / `taxonomy.py`:1228-1234 |
| `sentinel_minimum_share` range / meaning | v4:291 / `taxonomy.py`:2964 (the share test) |
| `sentinel_outlier_iqr_multiple` range / meaning | v4:290 / `taxonomy.py`:2958-2963 (the IQR test) |
| `small_cell_floor` range / meaning | v4:283, v4:312 (≥ 1) / v4:322-326 |
| default floor of 11 | `contract.py`:178-190 (`DEFAULT_SMALL_CELL_FLOOR`) |
| **C6-20 (membership)** — all seventeen required, no other key, sixteenth/eighteenth refused | v6:371-373; plan:1218-1219 |
| — no settings key for the affix / clock / placeholder rules | v6:381-384; plan:1215-1218 |
| **`day_first`** explanation — declaration recorded, reading is evidence-first, tie only, remark carried | plan:881-915; v6:1112-1113 |
| — "never silently overruled… never silently obeyed into free text" | plan:909-911 |
| — "a reader never has to guess which version of the rules produced it" | `taxonomy.py`:1126-1127 |
| **`long_tail_minimum_level`** explanation — the `max` detection line | v6:340-343 (C6-15) |
| — only value 11, `declaration_matching` precedent, loader refuses any other | v6:376-379 |
| — the privacy-boundary reason | v6:1589-1593; plan:1210-1215 |
| **S14** — each record has exactly FIVE keys | v6:738-740 (五 keys named); v5:808-810 (the membership rule's wording) |
| the four inherited declaration keys, spellings | `contract.py`:167-176 (`DECLARATION_KEYS`, 4 members) |
| declaration-record table rows for `n_declared`, `values_recorded`, `built_in_texts`, `built_in_numbers` | v5:590-595 |
| `built_in_dates` row (array, always present, possibly empty, sorted, distinct, LOADER-ONLY) | v6:742-745; v6:1185 |
| `n_declared` counts DIFFERENT values at `declaration_matching`'s identity | v5:592; v5:674-681 |
| "Two spellings of one value being one declaration…" | v5:700-712 |
| **What enters a list** (member written, not the person's spelling) | v5:653-660 (texts, numbers); v6:815-821 (dates) |
| — folded for the seventeen folded members, raw byte equality for the exact-spelling member | v6:795-801 |
| **K1** membership, over three lists | v5:758-762 widened by v6:742-745 (`built_in_dates` "the same shape and identity rules `built_in_numbers` has") |
| **K2** form, over three lists | v5:764-767; v6:744; date-order-equals-text-order reasoning v6:722-723 |
| **K3** the count bounds the lists, three-list sum | v6:747-749; the `<=` reasoning v5:769-778 |
| **K4** no overlap across all three lists | v6:751-753; v5:780-784 |
| **K5** producer obligation, six lists | v5:786-791 (four lists) + v6:1228 (the `built_in_dates` producer row) |
| — "a function of the command line alone", no cell consulted, matched-no-cell recorded as matched-every-cell | v5:645-651; v6:762-764 |
| **S7** — `false` in both records, loader refuses `true` | v4:299-304; v5:793-795; v6:765-766 |
| — the indented meaning block (adapted from two lists to three) | v5:798-803 |
| — the discriminator reason | v4:299-304; v5:805-806 |
| "the settings block carries the policy… and that is a sentence about the settings block" | v5:817-833; v5:854-865 |
| "what a reader can infer FROM THE SETTINGS BLOCK" + the combination bound + the owner ruling of 2026-08-17 | v5:844-852; v5:867-879 |
| **S8** | v4:306-308 |
| **S9** | v4:310 |
| floor minimum is ONE; the `--smallest-group 2` failure that is its reason | v4:312-320 |
| **What is given up, stated at its size** | v4:322-335 |
| **No other rule of this contract is relaxed by it** (B5, D3, N2, N4, P2, V1, W5) | v4:337-344; the letters checked at v4:1913, 1925, 1873, 1875, 1966, 1876, 1962 |
| — P6 added to that list (the fraction-width floor rule) | v6:593-594 |
| — the long-tail line does not move | v6:340-343; v6:1589-1593 |
| **S13** — the exhaustive ten-position list | v6:598-612 |
| — checked with the top-level rules before any column block is read | v6:633-634; v4:355-357 |
| **the ENTRY not the FIELD** paragraph | v6:614-624 |
| **What does NOT join the list** (`missing_by_source`, `n_missing_blank`, `resolution_mix`) | v6:626-632; v5:1023-1029 |
| — the exact-spelling floor that makes `missing_by_source` leave the list | v5:363-371 (C5-8) |
| **THE LIST IS EXHAUSTIVE, AND THAT MATTERS TO A WALK** (restated in full rather than re-imported) | v5:1036-1047; required to be restated by closure:70 and closure row 19 (closure:112) |
| **Why S13 is a rule of its own** | v4:359-374 |
| **Zero and below are still refused** (R16) | v4:376-379 |
| **What the artifacts owe when the floor is under the default** | v4:381-391 |
| count check: 17 settings keys, 5 declaration keys, 9 top-level, 5 source, 23 vocabulary members | `contract.py`:149-165 + v6:373; v6:738-740; `contract.py`:129-139; `contract.py`:141-147; v6:646-655 |
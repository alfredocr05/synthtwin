VERDICT SOUND_WITH_CORRECTIONS errors=8

## ERRORS

1. INVENTED, contradicts the forbidden-key matrix. Section text: "The other four appear on this role and on `free_text`, and nowhere else." Wrong twice. (a) `all_whole_numbers` stands on `identifier` ALONE: docs/spec/profile-contract-v4.md:1358 matrix row (only the identifier column is marked), docs/spec/v6-build/r6.md matrix row `all_whole_numbers` (only `idn`), and v4's own free_text key table at profile-contract-v4.md:1270-1275 lists five keys with no `all_whole_numbers`. (b) `n_distinct_by_occurrences` stands on THREE roles, not two: profile-contract-v4.md:1362 (unrep., identifier, free_text), profile-contract-v4.md:1396-1399 ("Version 4 adds it to `free_text` and `numeric_unrepresentable`"), v6-build/r6.md matrix row, and v6-build/r1.md 6.2 key table. No source authorizes the sentence. Corrected to name each key's actual reach and to point at section 6.11's matrix.

2. CROSS-REFERENCE DOES NOT RESOLVE. Section text: "the arithmetic of the count is section 4.5.2's". docs/spec/v6-build/s45.md:713-720 defines the parse-line count as the smallest whole number reaching `settings.minimum_parse_rate` × t — it is bound to `minimum_parse_rate` and states no arithmetic for `identifier_uniqueness`. r5b.md:17 borrows the pointer legitimately because it IS talking about the parse line; C6-81 is not. Corrected by stating the ceiling inline, matching src/synthtwin/taxonomy.py:1666-1676 `_needed` exactly (whole part of the exact product, plus one where the whole part falls below it).

3. UNDER-SPECIFIED, leaves a v6 role unresolved. Section text: "one form on the numeric roles, one on `free_text`". docs/plans/phase-4-columns.md:683 — "The all-different remark additionally extends to this role verbatim" — puts the remark on `affixed_number` too, and "the numeric roles" does not obviously include it. Corrected to name `count`, `continuous` and `affixed_number` for the firing question and to defer WHICH form each carries to section 4.5, because that is contested (see disagreement below).

4. SELF-CONTRADICTION AND MISDESCRIPTION in the closing sentence of 6.9: "Multiplicity parity — what a document must satisfy for `n_distinct_by_occurrences` to be consistent with `n_distinct`, `n_distinct_folded` and `n_present` on these two roles — is stated once, at section 7.2, and is not restated here." Three faults. (a) I2 and F2, in this same section, state exactly that parity — so "stated once … and is not restated here" is false of its own section, the precise failure mode v6 exists to kill. (b) profile-contract-v4.md:1396-1432 never involves `n_distinct_folded`; the map is over RAW present values and agrees with `n_distinct` (v4:1408-1409). (c) "these two roles" reads as identifier + free_text, while §7.2's title names `free_text` and `numeric_unrepresentable`. Corrected to point at what §7.2 actually adds — key form and serialization, the floor-free publication class, the disposition — which also preserves the placement flag ASSEMBLY.md section 3 depends on.

5. DELTA FRAMING SURVIVED. "is unchanged and still binding wherever it is feasible" (transcribed from profile-contract-v4.md:1264). docs/spec/v6-build/ASSEMBLY.md standing check 2 bans "unchanged". Replaced with "is not touched by that decision and still binds wherever it is feasible", which is what v4 means and carries no version reference.

6. DELTA FRAMING SURVIVED. C6-82's closing clause "nothing about what this role publishes moves in version 6." Replaced with "nothing about what this role publishes is relaxed by it." The rest of C6-82 is self-referential ("Three rules of this version") and stands.

7. INTERNAL INCONSISTENCY LEFT STANDING. 6.9 gives `length.min` the range "integer ≥ 0" while invariant F4, four paragraphs later, requires `length.min >= 1`. The section tightened exactly this tension on `min_length`/`max_length` in 6.8 (v4:1207-1208 → ≥ 1, matching I4, C6-26 and r6.md) and then declined to tighten the identical one here. The code cannot produce zero — a length-zero cell is blank, hence absent. Tightened `length.min` and `length.max` to ≥ 1; `words.min` stays ≥ 0 per F4.

8. NOT AN ERROR, FLAGGED FOR ASSEMBLY: invariant I1's citation "(A2)" is transcribed verbatim from profile-contract-v4.md:1215-1216, but A2 (v4:535-537) reads `statistical_type == "code"` ⇒ `structural_role == "identifier"`. The implication `role == "identifier"` ⇒ `structural_role == "identifier"` runs through the axis table row `identifier | code | ok` (v4:521) and A4. Kept verbatim; the assembler may prefer "(A2 via A4)".

## GAPS

- C6-80, C6-81 and C6-82 are PLACEHOLDER numbers. ASSEMBLY.md fixes one `C6-` sequence over the whole document and r6.md already occupies C6-49 through C6-53; the assembler must renumber these three into the single sequence and repoint any citation of them.
- The two all-different remark forms are pointed at as "section 4.5" rather than by their NG identifiers, because the NG1-NG41 renumbering is being done by the notes-section author and I could not establish which NG number each takes. Shipped constants are `remark_every_value_is_different` (free text) and `remark_every_number_is_different` (numeric roles), taxonomy.py:552-554. The assembler should replace "Section 4.5 fixes their wording" with the two NG identifiers.
- Cross-references are written against version 4 / current-draft numbering and must be repointed in the assembly pass: section 4.4 (settings), 4.5 (note forms), 4.5.2 (count arithmetic — the phrasing is borrowed from r5b.md, which assumes that section exists), 5.1 (universal keys), 5.2 (rule order), 5.3 (multiplicity map), 6.8 (referenced from 6.9 for the length and code-alphabet definitions), 7.2 (multiplicity parity).
- The clause "a `numeric_unrepresentable` block carries the same two keys, under the rule stated at that role" depends on the numeric_unrepresentable section actually stating C6-26. If that section omits it, `min_length`/`max_length` are left with no home outside `identifier` and my sentence dangles.
- Dispositions for these two roles (v4 §9.7, lines 2176-2192) are NOT transcribed here — they belong to the dispositions section. Two phrases must stay consistent with it: the corner's "THREE distinctness facts become REPORT-ONLY", and "Outside that corner every one of them is EXACT-OBSERVABLE".
- The two feasibility refusals v4 §9.7 names (`generation-words-exceed-length` for free text, `generation-whole-numbers-need-room` for identifiers) are generation-method obligations, not profile-format rules, so they are not stated here; if the assembled contract wants them visible they belong in the dispositions section, not in 6.8/6.9.
- I did not establish whether the `--identifier` declaration is matched against column names raw or under `declaration_matching`. contract.py:2597 validates each `forced_identifiers` entry as a known column name and cli.py:946 refuses unknown names, but the matching rule itself is the declarations section's; C6-80 says only "named that column with --identifier".

## CONFLICTS NOTED

- THE TASK BRIEF'S PREMISE IS WRONG, AND I DID NOT WRITE IT. The brief says a column reaches `identifier` "by `--identifier` declaration AND by the uniqueness rule, both stated exactly". There is no uniqueness route. The ratified plan (docs/plans/phase-4-columns.md line 492) says "declared identifier (unchanged — declaration is the only route)"; taxonomy.py:3581-3593 `_all_different` opens "This answer decides NO role" and records that the uniqueness clause "was the first clause of the identifier rule through three revisions, and every revision was defeated by a column of measurements that also never repeated (review item P1-R6-F8), so the rule it served no longer exists"; the `Settings` comments at taxonomy.py:1143-1153 say the same of both thresholds. I wrote the declaration as the only route (C6-80) and stated the uniqueness thresholds exactly as what they are — a remark trigger that decides no role (C6-81). If the brief meant something else, this is the point to correct before assembly.
- LIVE DEFECT IN SHIPPED CODE — the `identifier_minimum_rows` guard is applied on one remark path and skipped on the other. The free-text path calls `_all_different(cells)` (taxonomy.py:4025), which returns False below `identifier_minimum_rows` (taxonomy.py:3600). The numeric path at taxonomy.py:4286-4289 tests `cells.raw_distinct >= _needed(settings.identifier_uniqueness, n_present)` inline and never consults `identifier_minimum_rows`. Consequence at the shipped defaults: a 5-row all-different NUMERIC column gets the every-value-is-different remark (`_needed(0.95, 5) == 5`), while a 5-row all-different TEXT column correctly gets nothing — which is exactly the outcome the setting's own comment says it exists to prevent ("in a short column almost every measurement is all-different -- so nothing is said about it"). C6-81 as written states the rule with BOTH conditions binding on both paths, per the setting's stated purpose. Either the numeric path gains the guard, or C6-81 must be split into two different firing rules; it should not be resolved silently.
- v4's §6.8 key table gives `min_length` and `max_length` the range "integer >= 0" while v4's own invariant I4 requires `min_length >= 1`, so the table and the invariant contradict each other in the same subsection. The code cannot produce zero (a length-zero cell is blank, hence absent, hence not present). I tightened the table to "integer >= 1" for both keys and kept I4 verbatim. The same tension exists in §6.9 between `length.min` "integer >= 0" and F4's `length.min >= 1`; there I left v4's wording alone, because `length` is a sub-object whose JSON-type row and whose invariant row read as different layers. A reviewer may reasonably want both handled the same way.
- v4 §6.9's key table annotates `n_distinct_by_occurrences` as "(version 4 addition)". That is delta framing and amendment A-P4-11 forbids it, so I dropped the parenthetical from both role tables. No rule content changed.

## SOURCES

Section text is 11,275 characters (limit 14,000).

BASE. docs/spec/profile-contract-v4.md lines 1198-1303 (v4 §6.8 and
§6.9), transcribed key by key; v4 §5.3 lines 556-585 (multiplicity map,
M1/M2); v4 §5.4 line 588ff (absent-cell maps); v4 §4.4 lines 281-287
(settings key table: `identifier_uniqueness` number 0.0-1.0,
`identifier_minimum_rows` integer >= 0); v4 §9.7 lines 2176-2192
(dispositions for both roles — consulted, deliberately NOT transcribed,
that section is another author's).

PLAN (governs). docs/plans/phase-4-columns.md line 492 — the rule order
lists "declared identifier (unchanged — declaration is the only route)";
line 490 — an all-absent declared column is `empty` with
`structural_role: identifier`; line 521 — the declaration "still forces
`identifier`, winning right after the empty rule settles"; line 108 —
"value-based identifier inference — withdrawn three times under review";
line 2212 — a declared column is nothing-publishing whatever its role.

V6 DELTA. docs/spec/profile-contract-v6.md C6-1 (rule order, thirteen
roles), C6-3 (empty settles before the declaration), C6-19 (a
declaration forces `structural_role: identifier`), C6-42 (a column no
reading claims is still `free_text`, publishes no value, twin is still
invention; the set is smaller and that is a reporting obligation),
C6-PUB / C6-PUB-B (nothing class = `numeric_unrepresentable`,
`identifier`, `free_text`, plus any `structural_role: identifier`
column; `missing_by_source` empty, both absence counts zero, every
sentinel candidate `(withheld)`), C6-26 (`min_length`/`max_length` now
also on `numeric_unrepresentable`), C6-4/C6-10/C6-15 (the three new
rules that claim columns ahead of the fallback).

ADJACENT SECTIONS. docs/spec/v6-build/ASSEMBLY.md (identifier
convention: inherited families keep their letters, everything else a
plain `C6-` NUMBER; no `C6-` letter identifiers; NG1-NG41 for note
forms); v6-build/r1.md (roles preamble, rule numbering, `empty` at 6.1,
per-role forbidden-key discipline — not restated here); v6-build/r6.md
(publication class, C6-49); v6-build/r5b.md (the "arithmetic of the
count is section 4.5.2's" phrasing, adopted verbatim for C6-81);
v6-build/r5c.md (`long_tail_labels` as rule 11).

SHIPPED SOURCE, read for every count and threshold.
src/synthtwin/taxonomy.py:4227-4247 — the identifier verdict, evidence
`EVIDENCE_DECLARED_IDENTIFIER`, and the exact six added keys
(`min_length`, `max_length`, `all_whole_numbers`, `n_all_digits`,
`n_code_alphabet`, `n_distinct_by_occurrences`);
taxonomy.py:3186-3216 `_text_details` — the exact five free-text added
keys and the `length`/`words` sub-key sets; taxonomy.py:3581-3605
`_all_different` ("This answer decides NO role"); taxonomy.py:1140-1155
`Settings` defaults (`small_cell_floor` 11, `identifier_uniqueness`
0.95, `identifier_minimum_rows` 20) with the comments stating both
decide no role; taxonomy.py:1666-1676 `_needed` (smallest whole number
reaching the share); taxonomy.py:1703-1705 `_lengths` — `len(value)` on
the RAW present value, untrimmed; taxonomy.py:2225-2237 `_classify` —
`all_digits`/`code_alphabet` computed on `parsing.trimmed(text)`;
taxonomy.py:552-554 the two remark constants
(`remark_every_value_is_different`, `remark_every_number_is_different`);
taxonomy.py:4025-4026 (free-text remark) and 4286-4289 (numeric remark).
src/synthtwin/parsing.py:1009-1038 `is_code_text` — the code alphabet is
ASCII letters, ASCII digits, hyphen, underscore, nothing else, empty
string excluded; parsing.py:933-941 `token_count` — `text.split()`,
whitespace-separated runs. src/synthtwin/contract.py:284 axis triple
`(identifier, code, ok)`; contract.py:156-158 the settings key names.

PLACEHOLDER IDENTIFIERS USED: `C6-80`, `C6-81`, `C6-82` (see gaps).
INHERITED IDENTIFIERS KEPT EXACTLY: `I1`-`I4`, `F1`-`F4`, and the
pointers `A2`, `E1`, `N3`, `V2`, `M1`, `M2`.
VERDICT SOUND_WITH_CORRECTIONS errors=9

## ERRORS

1. DROPPED / POINTER LOOP — W1-W7 are left with no home, and the section's own ASSEMBLY placeholder cannot resolve it. docs/spec/v6-build/r2.md:39-41 says 'Section 7.4 specifies variants and variants_withheld in full: ... and invariants W1 to W7'. docs/spec/v6-build/a8a.md:1-3 opens 'This section restates the rules above as one list a loader or a test can walk ... the identifiers are the ones the sections above use' — by its own words a8a is a RESTATEMENT of rules stated above, not their normative home. The evidence settles the placeholder rather than leaving it open: 7.4 is the home. 7.4.7 now states W1-W7 in full (source: docs/spec/profile-contract-v4.md:1494-1535), and the compact rows at docs/spec/v6-build/a8a.md:139-147 stand as the loader walk.

2. DROPPED REASONS — four of v4's stated reasons vanish from the whole build if 7.4 declines to state W1-W7, because a8a.md:139-147 carries none of them. W2's ('it would be a spelling of some other label filed under this one', profile-contract-v4.md:1508-1511); W4's ('Nothing about a published label's rows is unaccounted for', v4:1516-1518); W6's ('two spellings that differ only by a character the canonical form does not distinguish would be one key and must not be produced as two', v4:1525-1530); W7's ('a published label covers at least small_cell_floor rows and every row was written some way', v4:1531-1535). All four restored in 7.4.7.

3. WRONG IDENTIFIER FORM — `C6-96` for the producer obligation breaks the convention every sibling section follows. docs/spec/v6-build/ASSEMBLY.md:24-27: 'New invariants join a family.' Every producer obligation in this document is named <family>-P: AF-P, T-P, U-P, DF-P, DF-R, CP-P, BD-P, RM-P, FW-P, TU-P at docs/spec/profile-contract-v6.md:1220-1230, restated as FW-P at docs/spec/v6-build/r4a.md:256, AF-P at docs/spec/v6-build/r5a2.md:69, T-P/TU-P at docs/spec/v6-build/r5b.md:162 and r5b_alt.md:134-138. Renamed `W-P`. This also settles the section's own gap note: it is NOT `W8` — a bare W number would read as loader-checkable beside W1-W7, which docs/spec/v6-build/a8a.md:139-147 marks 'yes'. The publication class takes the freed C6-96.

4. DUPLICATION — the `variants_withheld` bullets restate three rules 5.3 owns, against the section's own provenance claim of 'pointers rather than restatement'. The padding rule, the key range and the value range are C6-90 at docs/spec/v6-build/a7a.md:8-20, restated for the loader walk as M3 and M4 at docs/spec/v6-build/a8a.md:131-136. Reduced to a pointer at C6-90 plus the one bound specific to this key, 1..small_cell_floor-1, which is W5's and which a7a.md:31 already routes here.

5. INVENTED — 'A spelling of a label the description declines to name may not appear beside its count under any other key.' No artifact states it: not profile-contract-v4.md:1451-1456, not W1 (v4:1494-1498), not the forbidden-key rule C6-53 (docs/spec/v6-build/a8a.md:31). Removed.

6. BOUND STATED TWO WAYS INSIDE ONE SECTION — C6-94's first bullet says variant keys are stored 'byte for byte' while C6-95 says 'character for character'. The sources for the STORAGE rule all say character for character: profile-contract-v5.md:307-311 (C5-1), :522-526 (C5-N7), docs/spec/v6-build/a14.md:398-407 (13.5), src/synthtwin/taxonomy.py:1307-1308. 'Byte for byte' is the phrase the sources use for what the TWIN WRITES (docs/plans/phase-4-columns.md:968, docs/spec/v6-build/a9.md:165-168), and it is kept there. Unified.

7. DISAGREEMENT WITH SHIPPED CODE (report, do not resolve) — src/synthtwin/contract.py:3577-3582, the `_variants` docstring, still carries the false contrast this section correctly drops: keys are stored exactly '-- unlike the spellings of an empty cell, which are for a person to read and are escaped for display.' That is the sentence profile-contract-v5.md:306-312 superseded, and docs/spec/v6-build/a14_meta.md:5 already recorded it as a blocking defect in the register. The provenance cites this docstring as AGREEING with the section; its last clause does not. Code behaviour is fine (src/synthtwin/taxonomy.py:1306-1312 stores missing_by_source keys exactly); only the docstring is stale.

8. DISAGREEMENT WITH A WRITTEN SECTION (report, do not resolve) — docs/spec/v6-build/a14.md:555-561 states '13.25 Two producer obligations are stated as invariants although a loader cannot check them' (N7 and K5). docs/spec/profile-contract-v6.md:1220-1230 marks ten more *producer* (AF-P, T-P, U-P, DF-P, DF-R, CP-P, BD-P, RM-P, FW-P, TU-P), and written sections restate them. The count is already wrong; adding W-P makes it wrong by one more. The register entry needs rewriting — not this section's to fix.

9. CONFIRMED, and it stands — the section's report that docs/spec/v6-build/a14.md:93 omits `variants_withheld` from the disclosure inventory is accurate: the row names `variants` and 'the three held-back facts' (suppressed_levels, suppressed_rows, suppressed_level_counts). The fourth published label fact is missing from the inventory. Its class is stated at C6-96 here.

## GAPS

- Empty-string variant key: no artifact says whether "" may be a `variants` key. The loader types it `_SPELLING` and only requires it to fold to the parent; a label whose folded identity is empty would be needed, and an all-space cell is absent rather than present, so the case looks unreachable — but nothing states it. Left unstated here rather than invented.
- The producer obligation is written as `C6-96` because the W family belongs to another author. If that author states it as `W8`, `C6-96` must be dropped rather than left standing beside it — the assembler must place it exactly once.
- Section 7.4's own placement is one of the three ASSEMBLY §3 items left deliberately unwritten by the label-roles author. This text assumes it lands as 7.4 in the additions section, with the number repointed at assembly.

## CONFLICTS NOTED

- Version 4 §7.4.2 (lines 1465-1468) justifies exact storage by CONTRAST: variant keys are not display-escaped 'unlike `missing_by_source`, whose keys are REPORT-ONLY and are escaped for display.' Both halves of that contrast are false in this document — v5 C5-1 makes `missing_by_source` keys stored character for character too, and a14.md 13.5 plus plan P4-D6 (TAKEN 2026-08-19) make that map EXACT-OBSERVABLE with its keys written into twin cells. A transcription that carried the sentence would state a rule this format no longer has. The section states the reason directly instead and drops the contrast.
- a8a.md §8.8 marks all seven W invariants loader-checkable ('yes'). W2 is loader-checkable, but the property the whole mechanism rests on — that a variant key is the SOURCE spelling character for character — is not: a loader holds no table. `missing_by_source` has exactly this obligation written down as N7 and marked 'producer' in the same table (a8a.md line 61, register 13.25), and the W family has no counterpart. Either W gains a producer-side member or `C6-96` above carries it; leaving it unwritten leaves the byte-for-byte property unstated for the one map whose keys are written back into twin cells.
- a14.md's disclosure inventory row for the labels-class blocks (line 93) names `variants` and the three suppression facts but not `variants_withheld`, so the fourth published label fact is missing from the inventory that is supposed to enumerate what a description discloses. Its class is stated at C6-97 above: counts about unnamed groups, floor-free, the same class as `suppressed_level_counts`.
- Two sections point at each other for W1-W7: r2.md's 6.3.1 says 'Section 7.4 specifies ... invariants W1 to W7', while a8a.md states them in §8.8. Only one home is possible; flagged in the section text as an assembly placeholder.

## SOURCES

Transcribed element by element:

- v4 §7.4.1–7.4.6 (lines 1439–1578): the fix and the owner's reversal of
  the implementer's recommendation; the two keys' shape, key/value
  meanings and both `{}` cases; the worked example (floor 11, 22/15/3×1
  = 40) reproduced verbatim; §7.4.4 "why the withheld map is needed";
  §7.4.5 the casefold breadth, `ß`/`SS`, owner confirmation, the bounded
  delta, SECURITY.md + summary + report + battery scanning the complete
  profile (R-P2-11), and the correction that case and edge spacing ARE
  preserved above the floor; §7.4.6 EXACT-OBSERVABLE for both.
- Four roles, not v4's three: v6 delta line 347–348 (`long_tail_labels`
  publishes `levels` with `label`, `count`, `variants`,
  `variants_withheld` under B1–B8) and plan P4-D5, lines 946–947, 968.
- `{}` `variants` with `variants_withheld` covering every row is a
  reachable edge: plan amendment A-P4-2, lines 1783–1786.
- Storage exactly / display boundary at showing: v5 C5-1 and lines
  310–320; v6-build a14.md 13.5 (both maps EXACT-OBSERVABLE, keys
  written back into twin cells); s1.md glossary line 194 defines the
  display boundary; shipped `contract._variants` docstring
  (src/synthtwin/contract.py:3571-3582) and taxonomy.py:1306-1312.
- Table-keyed, no first-party meaning: v5 C5-N5 (lines 491–510) and
  lines 1039–1043; `canonical.TABLE_TEXT_KEY_SPACES`
  (src/synthtwin/canonical.py:77-80); a8a.md N5 row.
- Producer-side verification wording modeled on v5 C5-N7 (lines 522–526).
- Pointers rather than restatement: 5.3 multiplicity-map form and the
  padding reason (a7a.md C6-90, M1/M2 and its table row for
  `variants_withheld`); 6.3.1 level entry and S13's field list (r2.md
  lines 25–41, 16–23); disposition matrix rows and the `n_distinct`
  consequence (a9.md lines 160–176); register entries 13.5, 13.6, 13.7
  (a14.md).
- Code checked against the text: loader `_variants` enforces W5 (floor),
  W2 (fold), W3 (≤ count), W7, W4 in that order; publication guard types
  a variant key `_SPELLING` and its value `_FLOOR_COUNT`
  (profile.py:713-716); producer writes the two keys only on entries that
  cleared the floor (taxonomy.py:3149-3160). All agree with the text
  above.
- Identifiers: `C6-93`–`C6-97` chosen as the first free numbers after
  a7a.md's `C6-90`–`C6-92` (whole-build scan of used `C6-` numbers).
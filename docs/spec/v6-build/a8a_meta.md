VERDICT SOUND_WITH_CORRECTIONS errors=14

## ERRORS

1. A5 OVER-EXTENDED (invention). The section's A5 reads '...every role has a row, no role has two, AND THE THIRTEEN STATISTICAL TYPES ARE REACHED ONE EACH'. A5's source states role-totality only: docs/spec/v6-build/s5.md:166-168 ('The table above is total over the thirteen roles: every role of the vocabulary has a row, and no role has two') and docs/spec/profile-contract-v6.md:1259 ('the axes table is total over the thirteen roles'). The bijection clause is a SEPARATE statement at docs/spec/v6-build/s5.md:101-105, carrying NO identifier. Corrected: A5 narrowed to its source; the bijection stays 5.2's, unidentified.

2. THE THIRD COLUMN BREAKS ITS OWN CLOSED VOCABULARY, so three rows cannot be walked. The legend declares exactly three values (yes / producer / reading), then A5 reads 'a property of this contract's table, not of a document', S11 reads 'yes for the grouping; the within-column order is not re-derived', and B1 reads 'yes, as idempotence'. Corrected: a fourth term `contract` added to the legend for A5 (a row true of a table printed in this contract, which no parsed document can violate); S11's and B1's qualifications moved into the statement column so the third column holds one value per row.

3. N5 STATED WEAKER THAN ITS SOURCE — a bound narrowed in transcription. docs/spec/profile-contract-v5.md:497-509 (plan amendment A-P3-32, review item P3-V9-F2) extends the no-first-party-key rule past the class words: 'not only for the five class words, but for ANY name this format uses, `n_missing_withheld` and `n_sentinel_candidates_unpublished` among them, because a cell can say those too'. The section named only the six class words, which is exactly the short reading v5 says two implementations already made. Restored, with both example names.

4. N2 DROPPED ITS STATED MECHANISM. docs/spec/profile-contract-v4.md:601-603 states N2 as 'A class other than `(withheld)` is either 0 or at least the floor. A CLASS WHOSE REAL COUNT FELL BETWEEN 1 AND THE FLOOR IS POOLED INTO `(withheld)` AND READS 0 HERE.' That second sentence is why the bound reads '0 or at least the floor' rather than '>= floor', and without it the 0 branch looks arbitrary. Restored.

5. G2 DROPPED ITS STATED REASON. The section took v4:1922's bare substance ('`level_ceiling` imposes no output obligation') and left the reason behind at docs/spec/v6-build/r3.md:39-42: 'it must not be read as a cap the generator has to respect, because the generator reproduces counts, not the rule that produced them'. Restored as a reason (v4's substance kept; r3.md's disposition word 'LOADER-ONLY' correctly left to the key table, which is the section's own call and is right).

6. B1's DECIDABILITY IS THE SECTION'S OWN INFERENCE, correctly flagged and now written out rather than gestured at. No artifact states how a loader checks 'is a folded identity' (docs/spec/v6-build/r2.md:50-54 and docs/spec/profile-contract-v4.md:1909 both state only the property). Kept at `yes` with the check spelled out — the label equals its own trimmed, case-folded form — because W2 (docs/spec/profile-contract-v4.md:1959) states the structurally identical check as loader-decidable in the same list. The assembler must ratify this or move B1's third column to `producer`; it is the one row here whose column is not transcribed.

7. S11's TWO MERITS: the split is sound and is now stated in one column. docs/spec/profile-contract-v4.md:1851 states it flatly; docs/spec/v6-build/s45.md:15-18 adds the within-column emission order and says 'a loader does not need to re-derive it'. s45 says a loader need not, not that it cannot, so the section's split is strictly stronger than s45 and consistent with v4. Rewritten so the third column stays a single value.

8. IDENTIFIER COLLISION ON N3 — the section's resolution is CORRECT and is not unilateral, and the evidence is stronger than the section claims. Two other verified sections reached it independently: docs/spec/v6-build/r6_meta.md:33 and :46 ('Under the stated discipline the six-class rule keeps N1 and N2 and leaves N3 free') and docs/spec/v6-build/r1_meta.md:23. Decisive evidence the section did not cite: the delta's own supersession table, docs/spec/profile-contract-v6.md:1253, lists C6-N3 as superseding 'C5-12, N1, N2' — NOT any rule named N3 — so under ASSEMBLY.md:23-25 and :41 the letters it inherits are N1 and N2 and the 'N3' in `C6-N3` is a letter that rule never had. LIVE CONFLICT WITH A WRITTEN SECTION: docs/spec/v6-build/s1.md:164 and :190 cite `C6-N3` for the six classes; the assembler must repoint both to N1, or the mechanical `C6-` strip merges the six-class rule with the source accounting that r6.md:28,100,118,134, r1.md:90,105,195 and r4b.md:90,191 all cite as N3.

9. SHIPPED-CODE DISAGREEMENT, CONFIRMED AND EXPECTED. src/synthtwin/contract.py:309-315 defines MISSING_CLASS_KEYS with FIVE members — (blank), (declared-missing), (numeric-sentinel), (text-code), (withheld) — no (date-sentinel); src/synthtwin/contract.py:109 sets PROFILE_VERSION = 5. N1's six is fixed by docs/plans/phase-4-columns.md:1713-1717 (the map 'gains the one key `(date-sentinel)` ... with the membership, sum and floor invariants restated over six'), docs/spec/profile-contract-v6.md:676-681, docs/spec/v6-build/a14.md:845-848 and ASSEMBLY.md:239 ('6 absence classes'), and by NO shipped constant. Element-by-element check of N1 against all three prose sites: six for six, both directions, in the same code-point order.

10. THE SECTION'S GAP REPORT ON THE V FAMILY IS ONE ROW TOO WIDE, and the assembler will act on it, so: V4 IS ALREADY WRITTEN — docs/spec/v6-build/r3.md:490-510 states 'Invariant V4 (the order of `sentinel_verdicts` entries)' in its widened three-group form, matching docs/spec/profile-contract-v6.md:709-734. Carrying V4 again here would duplicate it. V1, V2 and V3 (docs/spec/profile-contract-v4.md:1876-1878) are genuinely stated in NO v6-build section, while V2 is CITED at docs/spec/v6-build/r1.md:195 and r4b.md:90,191 — a rule referenced by identifier and stated nowhere, which is exactly ASSEMBLY.md standing check 2.

11. WORSE EXPOSURE THE SECTION FLAGGED CORRECTLY: L1-L4 (docs/spec/profile-contract-v4.md:1894-1897) are stated in NO v6-build section and cited by FOUR — docs/spec/v6-build/r4a.md:111-112 ('Section 5.6 states L1, L2 and L3'), r4a_alt.md:100-101,305-307, r5a.md:250, r3.md:236, r5b_alt.md:115. Nothing in the build states them. Verified by grep over docs/spec/v6-build/*.md.

12. W1-W7 ARE CORRECTLY CARRIED HERE, AND THE SECTION'S WARNING IS THE RIGHT ONE INVERTED: no other v6-build section states them (verified by grep), while docs/spec/v6-build/r2.md:38-40 CITES them ('Section 7.4 specifies `variants` and `variants_withheld` in full ... and invariants W1 to W7'). Dropping them would leave r2.md's citation dangling. ASSEMBLY.md:85-86 lists v4 section 7.4's placement among the three rules two authors declined, so the assembler must confirm exactly one copy survives — deleting this one without another in place breaks standing check 2.

13. NO ERROR FOUND, RECORDED SO IT IS NOT RE-LITIGATED. Enumerations checked element by element, both directions: the six absence classes (N1) against v6:678-680, a14.md:845-848 and plan:1713-1717 — six for six; the eight `relationships` keys (S12) against docs/spec/v6-build/s45.md:830-838 and src/synthtwin/contract.py:195-204 — deterministic, grain, hierarchy, keys, missing_data_process, statistical, temporal, validation_targets, eight for eight in both; seventeen settings keys (C6-20) against s4.md:107-125 — seventeen rows counted; five declaration-record keys (S14) against s4.md:177-183; twenty-two universal keys (C6-53) against s5.md:9-38 and r6.md:314-315; thirteen axis rows (A4/A5) against s5.md:85-99 and a14.md:693-707. M1-M4 verbatim from v4:1885-1888, and the section's header naming two maps matches v4:1881 (v4:580-584's 'three places' counts `suppressed_level_counts`, an array whose rule is B4, not a map). W1-W7 verbatim from v4:1958-1964. S13's four ENTRY-not-map positions match s4.md:369-373 and 380-389 and the delta's v6:1257. No `C6-` letter identifier appears; no delta framing ('supersedes', 'carried', 'unchanged from version 5', 'as version 4 has it') appears; every identifier this list cites internally (C1, B2, B7, Y1, N2) is stated in the list itself.

14. REFUSAL-CATALOGUE WALK (this section does not carry the catalogue, but C6-44 is the row that fires). profile_version 4 → C6-44 refuses; 5 → C6-44 refuses; 6 → accepted, no row fires; 7 → C6-44 refuses. The exact message and the no-upgrade rule are section 10's (C6-45, C6-46 at docs/spec/profile-contract-v6.md:1271-1290) and are correctly not restated here; C6-44's row keeps the ordering reason (read before the canonical round trip) because that is what makes the refusal direction-correct.

## GAPS

- Sections 5.3 (multiplicity maps), 5.4 (absent cells) and 5.5 (`sentinel_verdicts`) have NO written section in docs/spec/v6-build/ — s5.md stops after 5.2 and forwards to all three. M1-M4 and the whole N family are therefore transcribed from version 4, version 5 and the delta with no version-6 section to check them against; the six-class enumeration exists in exactly two readable places (delta 676-681, a14.md:845-848) plus the plan (phase-4-columns.md:1714-1717).
- Section 7.4 (`variants`, `variants_withheld`) is unwritten as well, and ASSEMBLY.md:85-91 lists its placement as one of three rules two authors declined. I carried W1-W7 here from v4:1958-1964 so the list is not short by seven rows — if part two or an additions section also lists them, the assembler must delete exactly one copy, never both.
- The V family is in NEITHER part's brief: V1, V2, V3 and the widened V4 (delta 709-734: numbers ascending, then calendar day spellings ascending as text, then `(withheld)` by `n_occurrences`, `verdict`, `reason`) are not among the families I was given and are not 'numeric, datetime, new-role or producer'. If part two reads its brief as literally as I read mine, four invariants leave the contract. The ladder rows L1-L4 (v4:1894-1897) have the same exposure: they belong to no role section.
- Four membership rules in my area carry no identifier and so cannot be walked from a list: the nine top-level keys (s4.md:5-6), the five `source` keys (s4.md:68,78-79), the four keys of a level entry (r2.md:27-29), the two keys of a `publication_notes` entry (s45.md:3-9). I invented no identifiers; the paragraph after the S table names them instead. The assembler must either coin identifiers or accept that the list is not walkable end to end.
- Section 3's canonical round trip (s3.md:100-111) is a document-level rule with no identifier, so this list carries no row for it. Standing check 2 of ASSEMBLY.md requires that no rule be referenced by identifier without being stated; this is the inverse — a rule stated without one.
- B1's decidability is my inference and not a transcription: no artifact says how a loader checks 'is a folded identity'. I wrote 'yes, as idempotence' (the label equals its own trimmed, case-folded form). W2's check IS stated (v4:1959); B1's is not, and if the assembler disagrees the third column of B1 should read `producer`.
- The `C6-` numbers I cite — C6-20, C6-44, C6-53 — are taken from s4.md, r6.md and the delta and must be repointed when the assembler renumbers `C6-` in one sequence over the whole document (ASSEMBLY.md:33-35).
- Version 5's version rule was `C5-VER` (v5:1018), a lettered identifier. ASSEMBLY.md:41 says a rule that had a letter keeps the bare letter, which would make it `VER`; the delta already numbers it C6-44 and s4.md:25-34 gives it no identifier at all. Three answers, no ruling.
- Whether LT1, LT2 and G1L belong to my label-role block or to part two's new-role block is settled by neither brief. I left all three to part two (they are stated at r5c.md:102-127), while my B-family paragraph says the eight B rows bind `long_tail_labels` too — so the two parts must not both claim them, and neither may drop them.

## CONFLICTS NOTED

- IDENTIFIER COLLISION ON `N3`, and it is live in the written sections. The delta names the six-class rule `C6-N3` (profile-contract-v6.md:676-681, §9 row 1253), and ASSEMBLY.md:41 says a rule that had a letter keeps the bare letter — which would make it `N3`. But `N3` is already the inherited identifier of the source-accounting closure (v4:1874; v5's C5-N3 at 468-479 and list row 1005), and r6.md cites `N3` for exactly that closure at lines 28, 100, 118 and 134. Two rules cannot both be `N3` in a document whose standing check 4 asserts identifier uniqueness. I stated the six-class rule at N1 (six keys, always all six, sum to `n_missing`) and N2 (the floor), whose subjects it widens — ASSEMBLY.md:22-25 says a widened invariant keeps its identifier — and left N3 on the source accounting. The plan supports the split, calling them 'the membership, sum and floor invariants restated over six' (phase-4-columns.md:1715-1716), plural. This is a resolution I made rather than one I found, and it needs the assembler's ruling: keeping the delta's single `C6-N3` forces either renaming the source-accounting N3 (breaking the r6.md citations the convention exists to protect) or shipping two rules named N3.
- SHIPPED CONSTANT DISAGREES WITH N1, and is stated so nobody 'verifies' the contract against it. src/synthtwin/contract.py:309-315 defines MISSING_CLASS_KEYS with FIVE members — `(blank)`, `(declared-missing)`, `(numeric-sentinel)`, `(text-code)`, `(withheld)` — with no `(date-sentinel)`, and contract.py:109 sets PROFILE_VERSION = 5. That is expected for a version this tree has not implemented, but it means the enumeration in N1 is fixed by the plan (phase-4-columns.md:1714-1717) and the delta (676-681) and by no shipped constant. A reviewer checking six against the constant will find five and report the contract wrong.
- S11 IS STATED AT TWO MERITS. v4:1851 states it flatly — '`publication_notes` is grouped by column in schema order' — reading as fully loader-checkable, while s45.md:15-18 adds the within-column emission order and says 'a loader does not need to re-derive it'. I split the row: the grouping is decidable, the within-column order is canonical bytes a loader does not re-derive. If the assembler wants one strength, this row changes.
- G2 IS WORDED TWO WAYS. v4:1922 reads '`level_ceiling` imposes no output obligation'; r3.md:39-44 reads '`level_ceiling` is LOADER-ONLY. It records the line the column passed and imposes no obligation on the twin'. Same content, but one is an invariant and the other is a disposition. I used v4's substance; if the disposition word belongs in the invariant, the row changes.

## SOURCES

Every row transcribed from a named artifact; nothing completed from pattern.

S1-S12, X1-X5, N1-N4, M1-M4, B1-B8, C1/C2/Y1/Y2/G1/G2, W1-W7: v4's one-table
list, docs/spec/profile-contract-v4.md:1839-1968 (S 1841-1852; A 1858-1861;
X 1867-1871; N 1872-1875; M 1885-1888; B 1909-1916; C/Y/G 1917-1922; W
1958-1964). v5 states "W1 to W7 are unchanged" (profile-contract-v5.md:1053).

S1-S4 wording and reasons: v6-build/s4.md:42-64. S5-S6: s4.md:81-86.
S7: s4.md:254-270 (discriminator; `true` refused). S8-S9: s4.md:315-320.
S10-S11: v6-build/s45.md:11-18. S12: s45.md:840-846. S13: s4.md:363-378 with
380-389 (the ENTRY-not-the-map reading on four maps; checked before any column
block is read). S14: s4.md:172-175 and delta profile-contract-v6.md:738-740.
C6-20 (17 settings keys): s4.md:127-136. C6-53 (key set = 22 universal keys +
the marked cells; every other key forbidden): v6-build/r6.md:167-182, 314-316;
delta row "FKM" at profile-contract-v6.md:1247. C6-44: delta 1265-1269;
s4.md:25-34.

X1's "document `n_rows`, not the per-column echo": r6.md:288-292 with s5.md
key table lines 23-24. X2's totality over the CELLS on every role, standing
beside the affixed cores: s5.md:55-62, r5a.md:195, r5a2.md:64-66,
ASSEMBLY.md:164-167.

N1-N2 (six classes, always all six, sum, floor): delta C6-N3,
profile-contract-v6.md:676-681; the six-member enumeration re-read element by
element from v6-build/a14.md:845-848 and plan phase-4-columns.md:1714-1717.
N3, N4, N5, N6, N7: profile-contract-v5.md:468-527 and its list rows
1005-1009; the nothing-publishing term they are written in: r6.md:14-35.

K1-K5: s4.md:204-252; K3 and K4 over THREE lists also delta 747-759; K5 is
C5-16/C5-K5 (v5:1014; delta 761-766).

A1-A5 and the thirteen-row table: v6-build/s5.md:85-99 (rows), 101-105
(bijection), 138-168 (A1-A5). Role and statistical-type lists re-checked
against a14.md:677-708.

B1-B8: v6-build/r2.md:43-89, stated over any block carrying `levels`
(r2.md:45-48). C1/C2: r2.md:100-105. Y1/Y2: r2.md:115-119. G1/G2:
v6-build/r3.md:37-44.

M1-M4: v4:1885-1888 only; referenced as "section 5.3" by r1.md:167,188-189 and
r4b.md:60,83,170,185. W1-W7: v4:1958-1964; referenced as "section 7.4" by
r2.md:38-41.

Shipped source consulted: src/synthtwin/contract.py:195-204 (RELATIONSHIP_KEYS,
eight names, for S12), :309-315 (MISSING_CLASS_KEYS), :109 (PROFILE_VERSION).

Conventions: ASSEMBLY.md:18-41 (identifiers), 196-206 (standing checks). Plan:
phase-4-columns.md:1714-1717 (the wire for the sixth class and the third
declaration list), A-P4-10 at 2158-2226, A-P4-11 at 2227ff.
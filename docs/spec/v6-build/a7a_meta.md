VERDICT SOUND_WITH_CORRECTIONS errors=16

## ERRORS

1. ENUMERATIONS — ALL VERIFIED BOTH DIRECTIONS, no element added or dropped. (a) C6-90's four form rules = 4: Key form, Key range, Value range, Empty map, transcribed verbatim from profile-contract-v4.md:561-571; taxonomy.py:4125-4131 states the same key form and taxonomy.py:4163-4170 the same guarantees. (b) Published multiplicity maps = 2: `grep -n '_multiplicity_map(' src/synthtwin/taxonomy.py` returns callers at 3102 (`variants_withheld`) and 4141 (`n_distinct_by_occurrences`) only, and the already-written docs/spec/v6-build/s3.md:60-61 independently names exactly those two. (c) Roles carrying `n_distinct_by_occurrences` = 3: docs/spec/v6-build/r6.md:246 marks columns 2, 12 and 13 of 13, and the column identities from the count line at r6.md:248-250 make those `numeric_unrepresentable`, `identifier`, `free_text`; profile-contract-v4.md:1362 matrix row agrees; r1.md:166, r4b.md:60 and r4b.md:170 carry the key in exactly those three role tables and nowhere else. (d) Relationship keys = 8: src/synthtwin/profile.py:187-196 `RELATIONSHIP_SLOTS`, profile-contract-v4.md:445-454, docs/spec/v6-build/s45.md:830-839 and a14.md:751-754 all give the same eight spellings in the same order. (e) Distinctness facts lost in the corner = 3: docs/spec/v6-build/r4b.md:113-115 and a9.md:291 both give `n_distinct`, `n_distinct_folded`, `n_distinct_by_occurrences`. (f) W1-W7 = 7 at profile-contract-v4.md:1505-1531.

2. ERROR 1 — DUPLICATION, the failure this rewrite exists to end. Section 7.2's "**Exact shape.**" paragraph re-spells C6-90's Key form bullet word for word ("left-padded with zeros to the width of the largest key in the same mapping"). Version 4 could carry it twice — profile-contract-v4.md:561-566 and again at 1402-1406 — because 7.2 was an additions section; this version may not, and docs/spec/v6-build/r4b.md:207-209 already routes a reader to 5.3 for exactly this. Corrected: 7.2 binds by explicit reference to section 5.3 (the reference is stated in full, so standing check 2 at ASSEMBLY.md:240-243 is satisfied) and keeps only the two facts 7.2 alone adds — that the values count RAW present values, and `{}` when the column has no present value.

3. ERROR 2 — DUPLICATION, and the section's own conflict note misdescribes it. Section 7.3 as submitted reproduces S12's refusal message (docs/spec/v6-build/s45.md:840-845) and the whole "Why the block exists empty" paragraph including the P2-D5 dispatch seam and the `profile_version` sentence (s45.md:846-853) and the four named non-facts (s45.md:852-857). Its note claims it "did NOT restate the eight-key table" — true, but it restated everything else in 4.6. Version 4's own 7.3 (profile-contract-v4.md:1434-1438) is two sentences and states no refusal message and no reason. Corrected to that shape. ASSEMBLER: `relationships` is now stated once, at 4.6 in s45.md; if 4.6 is dropped or folded, the eight keys, S12's message and the "no cross-column fact enters this version" sentence (C6-43, profile-contract-v6.md:892-894) must land somewhere.

4. ERROR 3 — OVERCLAIM in the 5.3 table. The column head "where M1 and M2 are made concrete" against the cell "section 7.4; invariants W1 to W7" is not true of W1-W7. Read at profile-contract-v4.md:1505-1531: W4 (1518-1520) closes `sum(variants.values()) + sum(key x value for variants_withheld) == count`, which is M2 folded into the level entry's own closure, and W5 (1522-1525) holds every `variants_withheld` key between 1 and `small_cell_floor - 1`. NO W invariant states M1 for `variants_withheld`, because the number of withheld spellings is not separately published, so M1 has no published quantity to close on. W1, W2, W3, W6 and W7 are about `variants`, not about the map. Corrected: the column head is now "where its bounds are stated" and the cell names W4 and W5 for what they actually do.

5. ERROR 4 — MISDIRECTED POINTER, self-contradicting inside the submitted text. The 5.3 table cell reads "section 7.2; invariants U3, I2, F2" for where M1 and M2 are made concrete, while the submitted 7.2 says in its own body that "The concrete pairs are stated once per role, at U3, I2 and F2". Verified: the concrete pairs are at r1.md:186-188 (U3), r4b.md:83-85 (I2) and r4b.md:185-186 (F2); section 7.2 owns the shape, the publication class and the disposition, per r4b_meta.md item 4. Corrected: the cell now names the three invariants for the bounds and 7.2 for shape, class and disposition.

6. ERROR 5 — DROPPED REASON. The unlinkability half of the extremes argument is absent. src/synthtwin/taxonomy.py:4114-4116 states "Knowing that some value covers four of six rows does not say which value, and no value of this column appears anywhere in its block" — that is the clause that turns "the size of each repetition group" from a disclosure into a floor-free one, and the brief requires stated reasons to be carried. Restored verbatim in substance.

7. ERROR 6 — DROPPED CROSS-REFERENCE. profile-contract-v4.md:1431-1433 points the infeasible corner at "(section 6.8)"; the submitted Disposition paragraph drops the pointer, leaving "owner decision 6's infeasible corner" with no clause to reach. `identifier` is section 6.8 in this build (docs/spec/v6-build/r4b.md:1) and the corner is written there at r4b.md:104-125. Restored.

8. ERROR 7 — INVENTED CLAUSE, over-broad, and it collides with two written sections. "**`n_distinct_folded` is not part of this map and not part of any parity obligation on it**". The first half is sound and worth keeping — profile-contract-v4.md:1408-1410 binds the map to RAW present values and `n_distinct_folded` appears nowhere in v4:1396-1433 (confirmed independently at r4b_meta.md item 4). The second half is authorized by no source and reads as a general release: docs/spec/v6-build/a9.md:324-330 imposes a fold-collision obligation on precisely these roles ("a real 200-row single-character identifier profile publishes 200 raw and 122 folded, so 78 values must fold onto a partner"), and r4b.md:200-203 requires the free-text generator to honour "the multiplicity map including fold collisions". Narrowed to "this map does not bind `n_distinct_folded`, which is a separate count under its own obligations".

9. ERROR 8 — UNSUPPORTED REASON attached to a disposition. "LOADER-ONLY — nothing in the block describes any table, so no twin can evidence it and no validator checks it." No artifact states the validator half. Version 4 gives the actual reason at profile-contract-v4.md:210-212: `settings`, `publication_notes` and `relationships` "each carry ONE disposition covering their whole subtree, because nothing under them is an output obligation", which a9.md:57 records as "LOADER-ONLY | whole subtree; eight `null` slots". Substituted.

10. ERROR 9 — MINOR, but a mechanical check will trip on it. "which this profile has always carried" (transcribed from taxonomy.py:4112) contains the token "carried", which ASSEMBLY.md:240-241 lists among the delta-framing words `tools/spec/check_assembly.py` scans for. Reworded to "which every profile of this contract publishes" — same fact, no flagged token.

11. DISAGREEMENT WITH SHIPPED CODE, not reported by the transcriber and needing a code fix. src/synthtwin/taxonomy.py:4147 opens `_multiplicity_map`'s docstring with "THE ONE SHAPE, BUILT IN ONE PLACE. Three published mappings are this same fact about three different things" and then names TWO — `n_distinct_by_occurrences` and `variants_withheld` (taxonomy.py:4148-4151). The function has exactly two callers (taxonomy.py:3102, 4141), and the only candidate third, `suppressed_level_counts`, is a sorted array of integers, not a mapping (docs/spec/v6-build/r2.md:14). So the docstring carries the same miscount as version 4's section 5.3 heading at profile-contract-v4.md:556. The retitle to "published in two places" is right and is corroborated by an already-written section (s3.md:60-61 names exactly the two), but the transcriber cited the code as clean when its own comment says three. Recommend the docstring be corrected to two in the same change that lands this contract.

12. DISAGREEMENT WITH THE SUBMITTED TEXT'S CONFLICT NOTE 4, resolved differently. r4b.md:207-209 reads "its key form and serialization (section 5.3), its floor-free publication class and its disposition — is stated once at section 7.2". With ERROR 1 applied the sentence is no longer ambiguous in a harmful way: 5.3 now solely owns the key form and 7.2 solely owns the class and the disposition, so the parenthetical is the operative pointer. ASSEMBLER: still repoint the main clause so it reads "...its key form and serialization at section 5.3, its floor-free publication class and its disposition at section 7.2".

13. NUMBERING GAP STANDS, unchanged. C6-90, C6-91 and C6-92 are provisional. Verified by scanning every `C6-<digits>` in docs/spec/v6-build/: the highest live plain number is C6-82 (r4b.md:143), and C6-54 is defined twice (a14.md and r5a1.md:75), already logged at ASSEMBLY.md:222-226. No artifact fixes the next free number; the single renumbering pass must assign all three. C6-92 is a new identifier for what version 4 left unnumbered — it names only the disposition and the pointer, so folding it into 4.6/S12 at assembly costs nothing.

14. GAP CONFIRMED, NOT CLOSED. Section 7.4 is unwritten: `grep -rn 'W1\|variants_withheld' docs/spec/v6-build/*.md` returns only deferring pointers, and ASSEMBLY.md:98-99 lists label spelling variants among the rules both candidate authors declined. The 5.3 table's `variants_withheld` row therefore forward-references a section that does not yet exist. Kept the row — dropping it would leave the second of the two published maps unnamed anywhere — but the assembler must place 7.4 or the row dangles and W4/W5 are cited without being stated (ASSEMBLY.md:240-243, standing check 2).

15. CHECKS THAT PASSED. No delta framing survives in the corrected text (no "supersedes", "carried", "unchanged from version 5", "as version 4 has it", no version-3/4/5 comparison). No `C6-` letter identifier. Every identifier cited is either defined here (C6-90, C6-91, C6-92, M1, M2) or defined in a written section (U3 at r1.md:186, I2 at r4b.md:83, F2 at r4b.md:185, S12 at s45.md:840, W4/W5 at v4:1518-1525 pending 7.4). No addressee drift found: v4's 7.2 states no producer obligation for this key and none was invented; the gap note about a possible producer obligation is accurate and no artifact states one. This section carries no refusal catalogue, so the `profile_version` 4/5/6/7 walk does not apply to it.

16. LENGTH. Corrected section is 6,014 characters, under the 11,000 limit.

## GAPS

- C6-90, C6-91 and C6-92 are PROVISIONAL numbers, not established ones. The build folder's highest live plain number is C6-82 (r4b.md:143), a14.md defines C6-54 and r5a1.md:75 defines C6-54 again (already logged at ASSEMBLY.md:214), and a parallel section draft has claimed C6-83 through C6-85. No artifact fixes the next free number, so the assembly's one renumbering pass must assign these three. I picked 90-92 to leave headroom, not because any source says 90 is next.
- My section 5.3 table forward-references "section 7.4; invariants W1 to W7" for `variants_withheld`. W1-W7 exist in version 4 (lines 1505-1531), but ASSEMBLY.md section 3 lists label spelling variants (v4 section 7.4) among the rules BOTH candidate authors declined to place, and I found no file under v6-build/ that writes it (`grep -rn 'W1\|variants_withheld' v6-build/*.md` returns only the deferring pointers in r2.md and r4b.md). If section 7.4 is never written, this cross-reference dangles and the second of the two multiplicity maps has no specification anywhere in the document.
- I could not establish whether any role beyond `numeric_unrepresentable`, `identifier` and `free_text` carries `n_distinct_by_occurrences` in version 6, and I did not add one from pattern. `grep -n n_distinct_by_occurrences docs/spec/profile-contract-v6.md docs/plans/phase-4-columns.md` returns nothing at all, so neither the delta nor the ratified plan ever proposes the key for a new role; r6_meta.md item 13 records the same finding for `time_of_day` and `long_tail_labels` independently. Three roles is what the matrix and the version 4 key tables carry, and that is what I wrote.
- Version 4 section 7.2 gives the publication class and the disposition but states no PRODUCER obligation for this key (nothing in the FW-P / RM-P shape). The map is fully loader-checkable through M1 and M2 against `n_distinct` and `n_present`, so I wrote none; if the owner intends a producer obligation that the group sizes be the source's own, no artifact states it.

## CONFLICTS NOTED

- THE RELATIONSHIP MANIFEST IS ALREADY WRITTEN, and my brief assigned it to me anyway. s45.md:824-853 contains a complete section 4.6 — the eight-key table, invariant S12 with its refusal message, and the 'why the block exists empty' reason — reached by `grep -rn relationships v6-build/*.md`. My brief pointed me at v4:1434-1438, which is version 4's section 7.3, and that is the SUMMARY-plus-disposition entry, not the specification: v4 deliberately carries both, 4.6 stating the shape and 7.3 stating only 'Specified in section 4.6 ... Disposition: LOADER-ONLY'. I therefore wrote 7.3 in exactly that shape and did NOT restate the eight-key table. ASSEMBLER: keep both or fold them, but the manifest is PLACED either way — it is correctly absent from ASSEMBLY.md section 3's list of rules both candidate authors declined.
- s5.md DOES NOT OWN THE MULTIPLICITY MAP'S SHAPE, contrary to what my brief expected. Its headings are 5.1 universal keys, 5.2 the three axes, and 'The rule order: which role claims a column' — it stops there; `grep -n 'multiplicity\|M1\|M2\|n_distinct_by_occurrences' s5.md` returns NOTHING. Section 5.3 was unowned, and four already-written sections point at it BY NAME: s3.md:30 ('a multiplicity map may be `{}` (section 5.3)'), s3.md:60-68 (which cites 5.3 as the clause that fixes the padded key form), r1.md:167, r2.md:36-41, r4b.md:60,170,207. M1 and M2 are also cited without definition by r1.md:188 (U3) and r4b.md:83,185 (I2, F2). Without this section, five cross-references dangle and three invariants cite two undefined ones. I wrote it.
- VERSION 4'S OWN SECTION 5.3 HEADING CONTRADICTS ITS BODY. The heading reads 'one shape, used in three places' (v4:554) but the body's own list says the third, `suppressed_level_counts`, is 'in the same class of fact though not the same shape ... a sorted array rather than a map' (v4:580-585). The shipped code settles which is right: `_multiplicity_map` has exactly two callers, taxonomy.py:3102 (`variants_withheld`) and taxonomy.py:4141 (`n_distinct_by_occurrences`). I retitled it 'published in two places' and kept the third as an explicit class-not-shape note, because a heading that miscounts an enumeration is precisely the failure this rewrite exists to end. This is a wording change, not a rule change.
- A CROSS-REFERENCE IN r4b.md POINTS AT THE WRONG SECTION FOR ONE ITEM. r4b.md:207-209 says the multiplicity map's 'key form and serialization (section 5.3), its floor-free publication class and its disposition — is stated once at section 7.2'. The parenthetical is right and the sentence's main clause then passes all three into 7.2. As written here, key form and serialization live at 5.3 (C6-90) and the publication class and disposition live at 7.2 (C6-91). ASSEMBLER: repoint that sentence so it names 5.3 for the form and 7.2 for the class and disposition, or a reader chasing the key form lands in the wrong clause.

## SOURCES

TRANSCRIBED, NOT REASONED. Every element below was read.

MULTIPLICITY MAP FORM (§5.3) — profile-contract-v4.md:556-585,
transcribed rule by rule: definition sentence (557-559), Key form
(561-566), Key range (567), Value range (568-569), Empty map (570-571),
M1 (573-574), M2 (576-578). The four bullets and the two invariants are
copied, not paraphrased.

Shipped code confirms the same form: src/synthtwin/taxonomy.py:4125-4131
("THE KEY FORM, because JSON object keys are text ... left-padded with
zeros to the width of the largest key in the SAME mapping ... written
bare, `"10"` sorts before `"2"`"), and 4133-4138 restates M1 and M2 as
the function's guarantees. src/synthtwin/profile.py:787-789 is the
loader's path table: `_OBJECT`, keys `_DIGITS`, values `_COUNT`.

THE TWO USES OF THE SHAPE. `grep -n "_multiplicity_map(" taxonomy.py`
returns exactly two call sites: 3102 (`variants_withheld`) and 4141
(`n_distinct_by_occurrences`). v4:580-585 names three uses but says of
the third, `suppressed_level_counts`, "in the same class of fact though
not the same shape ... a sorted array rather than a map". W1-W7 verified
at v4:1505-1531 and in the index at v4:1958,1964.

PARITY (§7.2) — profile-contract-v4.md:1396-1433, transcribed:
adds-to sentence with "the identifier field's exact shape and
serialization ... no variation of any kind" (1398-1400); Exact shape
(1402-1406); "Distinctness is over RAW present values ... so the two
always agree (M1)" (1408-1410); Publication class with no small-cell
floor, the `suppressed_level_counts` comparison, and the `"1": 1`
disclosure sentence (1412-1421); Why it is needed, with the six-row
worked pair (1423-1429); Disposition (1431-1433). The extremes argument
is taxonomy.py:4108-4116, which is the reason the floor-free class was
"checked here rather than assumed".

n_distinct_folded IS ABSENT from v4:1396-1433 — verified by reading the
whole span. Also recorded independently at v6-build/r4b_meta.md item 4.

THE KEY'S THREE ROLES — v6-build/r6.md:246 matrix row, marks in columns
2, 12, 13 of 13; column identities from r6.md:248-250 count line
(`empty` first, `numeric_unrepresentable` second) and r6_meta.md:102,
106, 107 which cite v4:750-756, 1208-1213, 1271-1275. Matrix defined in
section 6.11 per a14.md:735. Corroborated by r4b_meta.md item 1.

DISPOSITIONS — v6-build/a9.md:320 (`numeric_unrepresentable`
EXACT-OBSERVABLE), a9.md:280 (`free_text` EXACT-OBSERVABLE), a9.md:291
(`identifier`: all three distinctness facts REPORT-ONLY inside the
corner). Agrees with v4:1431-1433. The three-facts count and the
200-row worked case are at r4b.md:113-125.

MANIFEST (§7.3) — v4:1434-1438 is the summary entry I mirror
("Specified in section 4.6 ... Disposition: LOADER-ONLY"). Full spec at
v4:441-470. The eight key names transcribed one by one from v4:445-454
and independently from the shipped constant
src/synthtwin/profile.py:187-196 `RELATIONSHIP_SLOTS`, which lists
`deterministic`, `grain`, `hierarchy`, `keys`, `missing_data_process`,
`statistical`, `temporal`, `validation_targets` — 8, same spellings,
same order. Third confirmation: v6-build/a14.md:751-754. Loader refusal
per S12 (v4:457-462); LOADER-ONLY per v4:206 and a9.md:57. Reason from
v4:464-470 and s45.md:845-853. "No cross-column fact enters this
version" from profile-contract-v6.md:892-894 (C6-43); the four named
non-facts from phase-4-columns.md:103-106 and CLAUDE.md's limits.
_relationships_block docstring (profile.py:462-482) confirms the block
consults nothing about any column.
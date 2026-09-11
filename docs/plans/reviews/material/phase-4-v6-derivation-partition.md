# partition

**VERDICT:** SOUND_WITH_CORRECTIONS

## Errors the verifier found (11)

1. GOVERNANCE, item (a), CHECK A3.3 — UNFLAGGED CONFLICT WITH THE RATIFIED PLAN. The plan fixes condition 4 as `F ≥ W − 5 × (small_cell_floor − 1)` at docs/plans/phase-4-columns.md:2043, derived at :2039-2040 ("if decimal is pooled then at most FIVE other styles share the pool with it, so `W − F ≤ 5 × (floor − 1)`") and explicitly declared vacuous where the right-hand side is ≤ 0 at :2046-2048. The report's (5 − P) form REFUSES documents amendment A-P4-8 admits — its own worked case K=11, P=2, W=35, F=1 satisfies plan:2043 (F ≥ −15) and is refused by A3.3. The plan governs on every conflict, so this is a RAISE needing a new plan amendment, on the pattern the contract itself records at docs/spec/profile-contract-v6.md:522-524 ("the plan governs, so the plan was amended rather than this document deviating from it"). The report presents it as a repair of a contract defect with no amendment named.

2. GOVERNANCE, item (a), CHECK A3 binding in the EMPTY-object sub-branch — SECOND UNFLAGGED CONFLICT. Amendment A-P4-6 states condition 1 as "its total is at least 1 wherever the census is non-empty" (docs/plans/phase-4-columns.md:1945) and then says "The census may also be empty in that case, which is what a column with no decimal cell at all writes" (:1951-1952) with no arithmetic attached to that branch. The report's headline counterexample (K=11, W=51, fraction_widths={}) is refused ONLY by extending the bound into a branch the ratified plan leaves free — again a RAISE requiring an amendment, not a restatement.

3. CITATION, item (a) — the load-bearing premise is cited to lines that do not state it. The report's trichotomy arm "s_i ≥ K → named, with value s_i" is cited to "v4:1705, P2", and A2/A3's "the pool draws only from unnamed styles" to v4:1692-1694. docs/spec/profile-contract-v4.md:1705-1706 states only the converse ("Every value under a style name is at least `small_cell_floor`"), and :1692-1694 mandates pooling only for below-floor styles; neither forbids pooling a style at or above the floor, which is what the whole capacity argument needs. The rule is fixed elsewhere: docs/spec/profile-contract-v5.md:1391 ("`numeric_styles` | the pooled count of cells whose spelling STYLE was used by too few rows to name") with :1397-1398 ("Wherever `(withheld)` appears above, it is a group too small to name, counted rather than named"), and the prose at docs/spec/profile-contract-v6.md:577-579. Uncorrected, the derivation rests on an inference in exactly the place the task warns about.

4. SUPERSESSION, item (a), CHECK A2 — v4's P2 affirmatively PERMITS what A2 refuses, and the report says only that A2 is "not stated" and "not enforced". docs/spec/profile-contract-v4.md:1707-1708 reads "`(withheld)` appears only when the pooled remainder is at least 1, and its own value may be anything from 1 upwards." v6 carries v4 totally except where a v6 clause supersedes BY NAME, so a clause bounding W at (6 − P)(K − 1) must name v4 §7.5.6 invariant P2's last clause as superseded. Transcribing A2 without that leaves two live rules in contradiction.

5. ARITHMETIC SLIP inside the material proposed for transcription, item (a), COMPLETENESS paragraph: "tiling the residue W − F into at most 5 − P (Case 2) or 6 − P (Case 1) parts". In Case 1 `decimal` is NAMED (docs/spec/profile-contract-v6.md:549-551), so its F cells are not in the pool and the residue to tile is W, not W − F. The report's own derivation body has it right ("Case 1 is the same tiling with R = W"); the transcribable version does not.

6. OVERSTATED READING, item (a) — "the EITHER-empty branch at v6:557-560 carries no arithmetic at all" and "is untouched by conditions 1-4 and passes" is not what v6 says. docs/spec/profile-contract-v6.md:561-562 attaches all FOUR conditions to case P5.c ("FOUR conditions bind, and a document breaking any of them does not conform"), condition 1 at :564 is "*F* is at least 1", and the §9 summary row at :1249 restates it the same way ("bounded FOUR ways where it is"). Read literally, v6 REFUSES the empty census in P5.c, contradicting its own :558-559. v6 is self-contradictory here; what resolves it in favour of the report's reading is the governing plan (docs/plans/phase-4-columns.md:1945, :1951-1952), which the report does not cite.

7. DECLARED GAP #1 IS NOT A GAP, item (c) — the report says it "could NOT establish which the author intended" for argument 1. Three artifacts settle it, none consulted: (i) v6's own rendering of the form says "written as numbers", not "read as" — docs/spec/profile-contract-v6.md:1049-1050; (ii) the shipped code records the distinction deliberately — src/synthtwin/taxonomy.py:3886-3889 ("'Written as' rather than 'read as', and deliberately … Saying they 'read as numbers' would claim more than the column shows"); (iii) the amendment's own verification record names this exact ambiguity and rules on it — docs/plans/reviews/phase-4-amendment-a-p4-1-verification.md:19, item P4-A1-F6, correction C6 ("define the half test as the existing numeric-looking count using integer arithmetic"), applied to the amendment text per that file's header at :1-5. The intent is fixed: numeric-looking. docs/spec/profile-contract-v6.md:1026 is a wording defect to repair, not an open fork.

8. CITATION ERROR, item (c) ARTIFACTS — "`missing_by_source` is empty there by F3 at v4:1292-1293". F3 is at docs/spec/profile-contract-v4.md:1289-1290; :1292-1293 is invariant F4 ("`length.min >= 1` and `words.min >= 0`").

9. LOADER-DECIDABILITY, item (c), CHECK C4 — stated as "The remark is carried if and only if N >= line(n_present - C)" under a heading of guard checks. Only the forward direction is decidable from a parsed document: where the remark is absent the loader holds no C to test. docs/spec/profile-contract-v6.md:1198-1207 requires precisely this distinction, and :1230 (FW-P) shows the form it takes; the converse must be marked *producer* or it will be transcribed as a check a loader cannot run.

10. OVER-REFUSAL RISK MISPLACED, item (c), CHECK C5 — `N < line(n_present)` is presented as a check while the meaning of "a declined column" is left open in the gaps. If "declined" also covers `numeric_unrepresentable`, C5 refuses every legitimate such document, because that role is reached only when `numeric_looking >= strict_needed` (src/synthtwin/taxonomy.py:3674-3676). The scope caveat belongs at the check, not only in a gaps list a transcriber may not carry across.

11. WEAK AUTHORITY, item (c), CHECK C3 — `C >= small_cell_floor` is derived from N4 at docs/spec/profile-contract-v4.md:1875, which governs `missing_by_source` keys and even there excludes `(blank)`; the report itself calls it "the pattern". "Floor-clearing" is never defined in any contract document — the only occurrences are docs/spec/profile-contract-v6.md:1012 and :1026 and docs/plans/phase-4-columns.md:1703 — so C3 rests on an analogy and belongs among the declared gaps unless the term is defined.

## GAPS declared

- Argument 1 of `remark_a_declaration_would_restore_the_distribution` is described two different ways by the two governing artifacts. profile-contract-v6.md:1026 says "how many present cells read as numbers" (= n_numeric); phase-4-columns.md:1704-1706 says "the numeric-looking count ... the same count its existing sentences call written as numbers" (= n_numeric + n_out_of_range + n_contradictory, taxonomy.py:2383-2387). They differ whenever n_out_of_range + n_contradictory > 0. I transcribed the plan's reading because the plan governs, but I could NOT establish which the author intended, and the choice changes both the equality check and the trigger.
- "A declined column" (profile-contract-v6.md:1011) is never defined by role name anywhere in v4, v5 or v6. I inferred `free_text` because the remark this one joins -- the competing-readings remark of phase-4-columns.md:1699-1700 -- is emitted only on the free-text path (taxonomy.py:3861-3862 feeding `_free_text_verdict` at 3864). I could not rule out that the author also means `numeric_unrepresentable` or a declared `identifier`, and if so the check set needs a role clause I cannot write from the artifacts.
- No published key equals argument 2 of the recoverable-distribution form. The floor-clearing non-numeric folded spellings and their per-spelling counts are not published on a declined block (a free-text block publishes `n_distinct_by_occurrences` over RAW spellings, v4:1275 and F2 at v4:1287, and `missing_by_source` is empty there by F3 at v4:1292-1293). So argument 2 can be BOUNDED (checks C2 and C3) but never equated to a published number, and no loader check can confirm the coverage figure itself. A producer-side obligation, in the shape of FW-P/RM-P (v6:1229-1230), is the only way to reach it, and none is written.
- No lower bound on D or M is fixed anywhere. profile-contract-v6.md:1112-1113 says the form is carried "whenever the option was given and a slashed reading was in play", and phase-4-columns.md:891-892 says "every slashed column read under the option carries exactly one remark" -- neither says whether a column all of whose slashed cells parse under NEITHER reading (D = M = 0) carries it. The tie rendering at v6:1063 would then read "both readings parse 0 of these values". I did not add D + Y >= 1 because no artifact fixes it.
- The population the four slashed counts range over is bounded only by n_present (v6:1103). Whether the intended population is the column's SLASHED cells specifically -- a tighter and more natural bound -- I could not establish, and no count of slashed cells is published anywhere, so n_present is the only bound a loader can use.
- Whether `fraction_widths` is REQUIRED or merely PERMITTED on `count`, `continuous` and `affixed_number`. C6-27 (v6:515-517) says such a block "carries" it and C6-FKM (v6:975) states only the forbidding direction ("Every key not listed for a role is FORBIDDEN on that role"). I read "carries" as required, matching v4's usage; if it is optional, case P5.b acquires a fourth sub-branch (key absent) that no clause covers.
- The parse line has no arithmetic definition in ANY of the three contract documents. v6 uses "the parse-line count" (v6:234, 279-281, 299, 1103-area, AF3 at v6:1233, T5 at v6:1242) and v4 publishes `minimum_parse_rate` as a setting (v4:286) but never says how a rate becomes a count. The only place the function is fixed is taxonomy.py:1666-1676 plus phase-4-columns.md:395. Check C4 depends on it, so the contract should name the function rather than leaving a transcriber to find it in source.
- C6-GRAMMAR at profile-contract-v6.md:998-1001 announces "Three sentences ... each needs a form of its own" and then numbers only two (v6:1003-1010, v6:1011-1017); the slashed-date form is present only in the arity table (v6:1027) and a trailing prose sentence (v6:1111-1113). I am reporting this rather than assuming which of the two counts is right.

## CORRECTED MATERIAL

All paths are relative to the repo root "/Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin". Every element below is quoted from the line given. The arithmetic of all three check sets is confirmed: I found no document passing them that describes no table, and no legitimate document they refuse EXCEPT where noted as a conflict with the ratified plan. What follows is the report with its four governance defects, one arithmetic slip, one false gap and two bad citations repaired.

=====================================================================
CHECK SET (a) — fraction_widths against numeric_styles
=====================================================================

DEFINITIONS. K = settings.small_cell_floor (v4:283, integer ≥ 1). W = numeric_styles["(withheld)"], or 0 when the key is absent (v4:1689, v4:1705-1708). P = the number of keys of numeric_styles other than "(withheld)" (v4:1689). F = the sum of ALL values of fraction_widths, its own "(withheld)" value included (v6:546-547). The three roles that carry both keys are `count`, `continuous` and `affixed_number`: C6-27 at v6:515-517, C6-NS at v6:402-404 with v6:409-410 ("`fraction_widths` sits beside it under C6-27, on the same three roles, by the same argument"), and C6-FKM at v6:982-983 and v6:988. On an `affixed_number` block read n_core_numeric wherever n_numeric appears (C6-6 lists `numeric_styles` at v6:261; AF7 at v6:285-287 and v6:1237).

THE MASTER IDENTITY, from which every clause below is derived:
  F = the number of `decimal`-styled cells.
  [C6-28, v6:528-531 "the number of `decimal`-styled cells"; C6-30, v6:540-541 "a census of the DECIMAL-styled cells"; plan phase-4-columns.md:822-824 and the ratifying sentence at plan:1905 "The values of `fraction_widths` sum to the count of decimal-styled cells."]

THE TRICHOTOMY, total and exclusive over the six styles:
  a style with no cell has no key                     [v4:1691]
  a style with 1..K−1 cells is pooled into `(withheld)` and has no key of its own  [v4:1692-1694]
  a style with K or more cells is NAMED, and the pool holds nothing but below-floor styles
      [THE CORRECTED CITATION. v4:1705 does NOT state this — it states the converse. The rule is fixed by v5:1391, "`numeric_styles` | the pooled count of cells whose spelling STYLE was used by too few rows to name", generalised at v5:1397-1398, "Wherever `(withheld)` appears above, it is a group too small to name, counted rather than named", and asserted in v6's own reasoning at v6:577-579, "a style holding twelve at a floor of eleven is published by name rather than pooled". Every capacity bound below rests on this line and on nothing in v4.]
  There are exactly six styles.                       [contract.py:438-445; v4:1612]
  Every counted cell is assigned exactly one style.   [v4:1625]
  The values sum to n_numeric.                        [P1, v4:1698 and v4:1965]

CHECK A1 (Case 1 — numeric_styles publishes a `decimal` key of value V).
  F = V, exactly.  [Restates P5.a, v6:549-551.]
  Consequences: F ≥ K by P2 (v4:1705, v4:1966), so fraction_widths is non-empty by P7 (v6:594-595, v6:1245).

CHECK A2 (Case 1 — the pool's capacity when `decimal` is named).  ** RAISE — requires a plan amendment and one named supersession. **
  W ≤ (6 − P) × (K − 1).
  [Derivation: with decimal named, the pool draws only from the 6 − P unnamed styles (trichotomy above), each holding at most K − 1.]
  Catches, at K = 11: numeric_styles = {"decimal": 60, "(withheld)": 51}, n_numeric = 111, fraction_widths totalling 60. P = 1, so five unnamed styles hold at most 50; W = 51 is impossible. No rule in force today refuses it: the shipped loader checks membership (contract.py:4282-4288), P2 (:4289-4295), P1 (:4296-4303) and P3 (:4274-4280), and nothing else, the `(withheld)` value being bounded only at ≥ 1 by `_counts(..., 1)` at contract.py:4273.
  TWO THINGS A TRANSCRIBER MUST DO WITH IT, and the report omitted both:
   1. No plan amendment states any bound on the pool in the named-decimal case — A-P4-6 (plan:1941-1949) and A-P4-8 (plan:2036-2043) both bound the CENSUS, not the pool. This is a RAISE and needs its own amendment, on the pattern v6:522-524 records for A-P4-5.
   2. It contradicts a sentence of v4 that is carried in force: P2 at v4:1707-1708, "and its own value may be anything from 1 upwards." A version 6 clause imposing A2 must supersede that clause BY NAME, or the two rules stand together and disagree.

CHECK A3 (Case 2 — numeric_styles publishes NO `decimal` key). Three inequalities:
  A3.1  F ≤ W
  A3.2  F ≤ K − 1
  A3.3  F ≥ W − (5 − P) × (K − 1)      ** RAISE — narrows the ratified plan; see below **
  [Derivation: decimal is unnamed, so it is one of the 6 − P unnamed styles and its entire contribution to the pool is F; the OTHER unnamed styles number 5 − P and each holds at most K − 1. A3.1 and A3.3 are the two sides of W = F + (cells pooled from non-decimal styles). A3.2 is the trichotomy.]
  A3.1 subsumes P5.b (v6:552-554): with no `(withheld)` key W = 0, so F ≤ 0 and F = 0. F = 0 if and only if fraction_widths is the empty object, by P7 (v6:594-595).
  WHAT A3.3 CHANGES ABOUT THE RATIFIED PLAN, stated because the plan governs on every conflict:
   • The constant. Amendment A-P4-8 fixes the condition as "F ≥ W − 5 × (small_cell_floor − 1)" (plan:2043), from "if decimal is pooled then at most FIVE other styles share the pool with it" (plan:2039-2040). That is true only at P = 0. The P-aware form is tighter and REFUSES documents A-P4-8 admits — at K = 11, numeric_styles = {"plain": 30, "leading_plus": 20, "(withheld)": 35}, n_numeric = 85, fraction_widths = {} or {"(withheld)": 1}: three unnamed styles hold at most 30, so W = 35 is impossible, yet plan:2043 gives F ≥ −15 and admits it. Transcribing (5 − P) is a RAISE requiring a new plan amendment; transcribing it as a repair of contract wording is a deviation from a ratified plan.
   • The branch. Binding these three in the EMPTY-object sub-branch also raises the plan: A-P4-6 states condition 1 as "its total is at least 1 wherever the census is non-empty" (plan:1945) and adds "The census may also be empty in that case, which is what a column with no decimal cell at all writes" (plan:1951-1952). The empty census carries no arithmetic under the plan as ratified.
   • And v6 as it stands does not say what the report says it says: v6:561-562 attaches all four conditions to case P5.c, condition 1 at v6:564 is "F is at least 1", and the §9 row at v6:1249 restates the same. Read literally, v6 already refuses the empty census in P5.c — contradicting its own v6:558-559. That internal contradiction should be named and closed in the same clause, not left for the next round.
  CATCHES (all four hold under the corrected form):
   • K = 11, n_numeric = 51, numeric_styles = {"(withheld)": 51}, fraction_widths = {}. P = 0, W = 51, F = 0; A3.3 requires F ≥ 1. Refused.
   • The A-P4-8 case the contract names (v6:573-579, plan:2026-2034): K = 11, n_numeric = 60, {"(withheld)": 60}, {"(withheld)": 1}. A3.3 requires F ≥ 10. Refused.
   • The revision-3 hole (v6:583-585, plan:1931-1934): {"(withheld)": 1000} on a hundred-cell column. A3.1 with P1 gives F ≤ W ≤ n_numeric. Refused.
   • The P-blind case above, at P = 2.

CHECK A4 (Case 2 — the key set, a corollary of A3.2 and P6).
  When numeric_styles publishes no `decimal` key, fraction_widths is either the empty object or exactly {"(withheld)": F} with 1 ≤ F ≤ K − 1. No NAMED width key may appear.
  [Every named width's count is at least K — P6, v6:593-594 and v6:1250 — and F ≤ K − 1 by A3.2, so no width can reach the floor.]

COMPLETENESS. A1-A4, with P1 (v4:1965), P2 (v4:1966), P6 (v6:593-594), P7 (v6:594-595) and C6-S13 (v6:598-612), are necessary and sufficient over K, W, P, F and n_numeric. Sufficiency, CORRECTED: in Case 2 give decimal its F cells and tile the residue R = W − F into at most 5 − P parts each in [1, K − 1]; in Case 1 decimal is NAMED, so the residue is R = W and it tiles into at most 6 − P such parts. Either tiling exists exactly when R is at most that capacity — take ceil(R/(K − 1)) parts. At K = 1, C6-S13 (v6:605-612) forces W = 0, so R = 0 and the tiling is empty.

NOTE FOR THE TRANSCRIBER. P6's clause "the `(withheld)` value is 0 or at least 1" (v6:594) is vacuous over non-negative integers; the intended rule is carried by P7, and §9's own row for P6 at v6:1250 already omits the clause.

=====================================================================
CHECK SET (b) — remark_slashed_dates_read_against_your_declaration
=====================================================================
Unchanged from the report; I verified every element and found no defect.

DEFINITIONS as the form fixes them (v6:1027): D, M, X, Y and the reading USED. n = n_present of the column named by the note's own sibling `column` field (v6:1103; resolution route fixed at v6:1134-1136; S10 at v4:402-403 and v4:1850).

THE PARTITION: the n present cells fall into four exclusive, exhaustive blocks — B (both readings parse), X (only day-first), Y (only month-first), N (neither). B + X + Y + N = n, all ≥ 0, D = B + X, M = B + Y.

B1. D, M, X, Y are whole numbers ≥ 0.  [Argument class, v6:1127-1130.]
B2. D − X = M − Y.  [v6:1095-1102, unchanged.]
B3. X ≤ D.  [Equivalent to B ≥ 0. Given B2, "Y ≤ M" follows; v6:1094 states both and one is redundant.]
B4. D + Y ≤ n_present, equivalently M + X ≤ n_present.  [NEW; REPLACES check 4 at v6:1103-1104, which bounds D and M separately and so bounds nothing about their union. Check 4 then follows: D ≤ D + Y and M ≤ M + X.]
B5. The reading-used argument is `day-first` where D ≥ M, `month-first` where M > D.  [v6:1092-1093, unchanged; DF-P at v6:1225 and plan:885-887.]
  CATCHES n_present = 100, D = 80, M = 80, X = 30, Y = 30: B2, B3 and old check 4 all pass; D + Y = 110 > 100, refused. And D = 90, M = 80, X = 10, Y = 20 (v6:1099-1102) fails B2.
COMPLETENESS. Given values passing B1-B4, set B = D − X ≥ 0 and N = n_present − D − Y ≥ 0; the four blocks realize (D, M, X, Y) exactly. Four checks plus B5 on the fifth argument.

=====================================================================
CHECK SET (c) — remark_a_declaration_would_restore_the_distribution
=====================================================================

DEFINITIONS. Argument 1 = N; argument 2 = C (v6:1026, arity 2). n = n_present of the column the note's `column` field names. K = settings.small_cell_floor. line(t) = the smallest whole number reaching minimum_parse_rate × t (taxonomy.py:1666-1676 `_needed`; minimum_parse_rate = 0.99 at taxonomy.py:1164; "Applied as a COUNT, never as a compared share" at taxonomy.py:1158-1159; plan:395).

CHECK C1 (an equality, not a bound).
  N = n_numeric + n_out_of_range + n_contradictory; equivalently N = n_present − n_not_numeric by X2 (v4:1868).
  [Shipped definition `_numeric_looking` at taxonomy.py:2383-2387; n_numeric is `len(cells.numbers)` at taxonomy.py:4627; it is the count fed to the existing sentence at taxonomy.py:3859 and 3897, rendered at taxonomy.py:881-891. Same numerator as Q9, v4:1188 and v4:1942. All four keys universal (v4:495-498), so this is loader-decidable on a declined block.]
  THE READING IS SETTLED, NOT OPEN — three artifacts agree and only one line disagrees:
   • plan:1705-1706, "the numeric-looking count the remark already carries, the same count its existing sentences call written as numbers";
   • v6's OWN rendering of this form, v6:1049-1050, "N of this column's values are WRITTEN as numbers";
   • taxonomy.py:3886-3889, which records the distinction deliberately: "'Written as' rather than 'read as', and deliberately … Saying they 'read as numbers' would claim more than the column shows";
   • and the amendment's verification record, docs/plans/reviews/phase-4-amendment-a-p4-1-verification.md:19 (item P4-A1-F6, correction C6): "define the half test as the existing numeric-looking count using integer arithmetic" — applied to the amendment's text per that file's header at :1-5, which is why plan:1705-1706 now reads as it does.
  ACTION: v6:1026's "how many present cells read as numbers" is a wording defect against v6:1050 in the same clause. Repair it to "written as numbers" and write the equality above.

CHECK C2. C ≤ n_not_numeric, equivalently N + C ≤ n_present.
  [The covered cells are present and NON-numeric by the trigger's own words (v6:1012-1013), so they are counted in n_not_numeric; X2 at v4:1868 closes it. This restriction is also what makes C4's arithmetic valid: an out-of-range or contradictory spelling is counted IN N, so removing it would move both sides.]

CHECK C3. C ≥ small_cell_floor.
  [DECLARED WEAK. "Floor-clearing" is defined nowhere: its only occurrences are v6:1012, v6:1026 and plan:1703. The nearest treatment is N4 (v4:1875), which governs `missing_by_source` keys and excludes `(blank)`, and small_cell_floor ≥ 1 at v4:283. This check is an analogy, not a quotation; either define the term in the same clause or move C3 to the gaps.]

CHECK C4 (the trigger). LOADER-DECIDABLE DIRECTION: where the remark is carried, N ≥ line(n_present − C) — argument 1 is at least the smallest whole number reaching minimum_parse_rate times (n_present minus argument 2). PRODUCER DIRECTION, marked *producer* in §9's own sense (v6:1198-1207, and FW-P at v6:1230 for the form it takes): where that arithmetic holds, the remark IS written. A loader holding a document with no remark holds no C and cannot test the converse.
  [Declaring those spellings missing makes their cells ABSENT, so the surviving present population is n_present − C while N is unchanged; the column is re-tested against the same one line applied to the smaller population — plan:1702-1705, v6:1011-1015. Where it does not hold, no advice fires and nothing implies one declaration would suffice (v6:1015-1017).]

CHECK C5 (the declined precondition). N < line(n_present).
  [Sound for the role the remark is actually emitted on: the competing-readings remark is built at taxonomy.py:3861-3862 and returned into `_free_text_verdict` at :3864, and free text is reached only after RULE 6 fails at taxonomy.py:3800-3801, i.e. only when numeric_looking < strict_needed. With C4 this forces C ≥ 1 independently of C3.]
  SCOPE CAVEAT, stated here and not only in the gaps: if "a declined column" (v6:1011) is meant to include `numeric_unrepresentable`, C5 refuses every legitimate such document, because that role is reached only when numeric_looking ≥ strict_needed (taxonomy.py:3674-3676). C5 may be transcribed only with the role scope named.
  CATCHES, since v6:1085-1108 gives argument checks for the slashed-date and affixed forms only and none for this one: C = 1000 on a hundred-cell column (C2); N = 40, C = 5, n_present = 100 (C4: line(95) = 95); a remark rendered against a different column's facts (C1). The intended positive case N = 96, C = 5, n_present = 100 passes C4 (line(95) = 95 ≤ 96) and its inconsistent variant fails C2 (96 + 5 > 100).

NOT TRANSCRIBED, RAISED FOR THE OWNER. C4 as the plan words it clears the line on the NUMERIC-LOOKING count, which does not deliver the rendering's promise that "this column's distribution will be described" (v6:1052-1053): survivors clearing the line on numeric-looking but not on holdable cells take `numeric_unrepresentable` and publish no statistic (taxonomy.py:3674-3676, :3685, message at :924-935); survivors with one or two distinct values take `constant`/`binary` ahead of the numeric rule (order at taxonomy.py:3623-3626; the binary branch and its own "also numbers" remark at taxonomy.py:3736-3752; the trade named at plan:376-377). The truth-preserving trigger is n_numeric ≥ line(n_present − C) plus survivor distinctness of at least three — the first loader-decidable, the second not. plan:1700-1701 calls the trigger "the arithmetic that makes the advice TRUE rather than hopeful", so this is a conflict inside the governing text and an owner call.

=====================================================================
CROSS-CUTTING (confirmed, verbatim)
=====================================================================
C6-GRAMMAR at v6:998-1001 opens "Three sentences of the profile document are new … each needs a form of its own" and then numbers only TWO — v6:1003-1010 and v6:1011-1017. `remark_slashed_dates_read_against_your_declaration` appears only in the arity table at v6:1027 and in a trailing sentence at v6:1111-1113. A count stated as three over an enumeration of two.

=====================================================================
GAPS, corrected
=====================================================================
1. WITHDRAWN — the "which count is argument 1" fork is settled; see CHECK C1. What remains is a wording repair at v6:1026.
2. STANDS — "a declined column" (v6:1011) is named by no role anywhere in v4, v5 or v6. The emission path fixes free text (taxonomy.py:3861-3864); `numeric_unrepresentable` and a declared `identifier` cannot be ruled out from the artifacts, and C5's validity depends on the answer.
3. STANDS — no published key equals argument 2. A free-text block publishes `n_distinct_by_occurrences` over RAW spellings (v4:1275, F2 at v4:1287) and its `missing_by_source` is empty (F3 at v4:1289-1290 — NOT :1292-1293, which is F4). So C can be bounded and never equated, and a producer obligation in the shape of FW-P/RM-P (v6:1229-1230) is the only route to the figure itself; none is written.
4. STANDS — no lower bound on D or M is fixed. v6:1112-1113 and plan:891-892 do not say whether a column whose slashed cells parse under NEITHER reading (D = M = 0) carries the form; the tie rendering at v6:1063 would then read "both readings parse 0 of these values".
5. STANDS — the population of the four slashed counts is bounded only by n_present (v6:1103); no count of slashed cells is published anywhere.
6. STANDS — whether `fraction_widths` is REQUIRED or merely PERMITTED. C6-27 says a block "carries" it (v6:516-517) and C6-FKM states only the forbidding direction (v6:975). Note in support of "required": C6-NS says `numeric_styles` is "REQUIRED on `count`, `continuous` and `affixed_number`" (v6:402-404) and puts `fraction_widths` beside it "on the same three roles, by the same argument" (v6:409-410) — strong but not the word itself.
7. STANDS — the parse line has no arithmetic definition in any contract document. Neither v4 nor v5 contains the phrase at all; v6 says only "the count `minimum_parse_rate` fixes, applied as a count" (v6:280-281, :323) and v4 publishes the setting at :286. The function is fixed only at taxonomy.py:1666-1676 with plan:395. C4 depends on it, so the contract should name the function.
8. STANDS — the C6-GRAMMAR count of three over an enumeration of two.
9. NEW — items (a)'s A2 and A3.3 and its empty-branch extension all narrow or add to ratified amendments A-P4-6 (plan:1941-1952) and A-P4-8 (plan:2036-2048). Since the plan governs on every conflict, they cannot be transcribed as contract repairs; they need an amendment of their own, and A2 needs v4 P2's last clause (v4:1707-1708) named as superseded.
10. NEW — v6's case P5.c is self-contradictory as written: v6:558-559 permits the empty census, v6:561-564 and the §9 row at v6:1249 refuse it via condition 1. Whatever bound is transcribed must close this, not sit beside it.
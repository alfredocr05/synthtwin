VERDICT SOUND_WITH_CORRECTIONS errors=19

## ERRORS

1. ENUMERATIONS VERIFIED, BOTH DIRECTIONS — NO ERROR. Six styles: src/synthtwin/contract.py:438-445 ships NUMERIC_STYLES = plain, leading_zero, leading_plus, decimal, exponent_lower, exponent_upper. Six in source, six in the table, same order, no seventh, none missing; each 'what it names' cell matches profile-contract-v4.md:1610-1622. Count agrees with ASSEMBLY.md §4 item 1 ('6 numeric styles'). Loader key set = NUMERIC_STYLES + (WITHHELD,) at contract.py:4285-4288, WITHHELD == '(withheld)' at taxonomy.py:339. Ladder: 7 steps in the draft, 7 at profile-contract-v4.md:1631-1643, identical order and predicates. Recount identity: 6 clauses in the draft, 6 at profile-contract-v4.md:1775-1806 and repeated clause for clause at generation-method-v1.md:979-995.

2. SCOPE NARROWED — a universal obligation on the twin was demoted to a remark about one special column. The draft's only carrier of the comma/parentheses prohibition was '...stays byte-plain, and no cell of it wears a comma or brackets (R-P2-9)' inside the all-canonical-column sentence of its §7.5.5. profile-contract-v4.md:1712-1718 states it as a rule over every twin cell ('classified by their digit form and are never written by the twin'), and profile-contract-v4.md:1724-1728 repeats it in the disposition ('Never a thousands separator — the comma breaks the CSV row itself — and never accounting parentheses, which are kept for the contradictory-notation stand-in'); a14.md:392-395 (13.3) says the same. As drafted, an implementer reading only this section may write `1,234` for a `plain` cell on a mixed column. RESTORED as a universal clause in §7.5.5 with both reasons and v4's `(05)` consequence.

3. ENUMERATION ELEMENT DROPPED. profile-contract-v4.md:1580-1584 names THREE identical-block families — `0`,`00`,`000`; `0.0`,`00.0`,`000.0`; and `0e0`,`00e0`,`000e0` — and r4a.md:129-134 carries all three. The draft's opening named only two, dropping the exponent family. Count restored to three.

4. ROLE CLAUSE AND REASON DROPPED. profile-contract-v4.md:1597-1609 and profile-contract-v6.md:407-410 both say FORBIDDEN 'on every other role INCLUDING `numeric_unrepresentable`', with the reason (that role's twin cells are invented digit strings at one canonical width, R-P2-1). The draft said only 'FORBIDDEN on every other role' and carried no reason. Restored, compressed.

5. CITATION DROPPED FROM P1. profile-contract-v4.md:1697-1703 grounds the exclusion in 'the class-preserving construction of plan P2-D9'; a14.md:392-395 (13.4) repeats it. The draft's P1 dropped the P2-D9 citation, which is the construction that makes the exclusion checkable. Restored.

6. REPORT OBLIGATION DROPPED. profile-contract-v4.md:1826-1827 and generation-method-v1.md:965-967 both require the report to name the remainder, how many cells it covered and how many had no point-free spelling of their own. No other written v6-build section carries it (a9.md's matrix does not), so it belongs here. Restored.

7. BAN-REASON DROPPED. profile-contract-v4.md:1757-1760 says the first withdrawn wording is unmeetable BECAUSE every numeric cell text falls in one of the six by the total rule of the ladder; generation-method-v1.md:993-995 states the same as 'there is no outside-the-styles bucket'. The draft banned the wording without its ground. Restored.

8. P6 CLAUSE DROPPED — ASSEMBLER MUST CONFIRM. profile-contract-v6.md:592-594 states P6 as 'Every named width's count is at or above `small_cell_floor`, AND the `(withheld)` value is 0 or at least 1'; the draft dropped the second clause. As literally written that clause is vacuous over non-negative integers, and profile-contract-v6.md:1249's own §9 row for P6 also omits it. The corrected text keeps P6 as the draft has it and folds the only meetable reading into P7 ('a present `(withheld)` value is at least 1'), which is what P7 already implies. Flagged rather than resolved.

9. IDENTIFIER ORDER — ASSEMBLY.md §1 fixes 'one sequence over the whole document'. The draft's heading introduced C6-84 (the recount identity) but the body defined C6-85 (the pooled-cell rule) first, so document order and number order disagreed. Corrected by making C6-84 the pooled-cell rule and C6-85 the identity; both numbers are provisional after C6-82 (r4b.md:143), as the transcriber notes. C6-27 to C6-30 are LEFT UNCHANGED — the draft's numbering of them was right and must not move (they are cited by profile-contract-v6.md:513-585, r4a.md:155-260 and r4a_alt.md:136-262).

10. UNSOURCED INFERENCE REMOVED. The draft's P5.a added 'by P2 the census is non-empty here'. It is true (a `decimal` key is ≥ floor ≥ 1) but appears in neither profile-contract-v6.md:544-546 nor the plan; profile-contract-v6.md:545-546 says instead 'This is the ordinary case'. Removed as an invention rather than transcribed.

11. CONDITION-4 COUNTEREXAMPLE SUBSTITUTED. The draft replaced the ratified illustration with its own. phase-4-columns.md:2056-2066 and profile-contract-v6.md:575-585 both use `small_cell_floor: 11`, `n_numeric: 60`, `numeric_styles: {"(withheld)": 60}`, `fraction_widths: {"(withheld)": 1}` (F ≥ 10 required). Restored the plan's example; the draft's own F = 0 example is kept where it belongs, in the 'no fifth condition' paragraph.

12. THE DRAFT IS RIGHT AND THE v6 DELTA IS WRONG ON P5.c CONDITION 1 — kept as drafted. phase-4-columns.md:1979 (A-P4-6) reads 'its total is at least 1 wherever the census is non-empty'; profile-contract-v6.md:566 flattens it to '1. *F* is at least 1', which contradicts P5.c's own 'EITHER the empty object' two lines above (profile-contract-v6.md:559-563) and would make the empty branch unreachable. The plan governs, so the branch confinement stands and must survive assembly.

13. CONFLICT CONFIRMED AND CARRIED, NOT FIXED — the plan's constant 5 in condition 4 is too weak. phase-4-columns.md:2072-2076 fixes `F ≥ W − 5 × (floor − 1)` unconditionally. I re-derived the transcriber's counterexample and it holds: at floor 11, `numeric_styles: {"plain": 30, "leading_plus": 20, "(withheld)": 35}` with `fraction_widths: {}` leaves the pool to leading_zero, exponent_lower and exponent_upper only (decimal holds 0 when F = 0), so at most 3 × 10 = 30 < 35, yet the plan's form reads F ≥ −15 and admits it. The true bound is `F ≥ W − (5 − P) × (floor − 1)` for P styles named besides decimal. Transcribed as ratified; needs an owner amendment.

14. NO DISAGREEMENT WITH SHIPPED CODE ON P1-P4. src/synthtwin/contract.py:4261-4304 enforces exactly what §7.5.4 states: `_counts(..., 1)` gives values ≥ 1, the empty-map check raises P3, the loop refuses a name outside NUMERIC_STYLES + (WITHHELD,) and applies the floor to NAMED styles only (P2), and `_added(styles) != n_numeric` raises P1. `integer_valued` is checked against nothing (P4), and the docstring at contract.py:4270-4277 says so.

15. NO SHIPPED CODE FOR §7.6 — confirmed. `grep -rn fraction_widths src/` returns nothing, so C6-27 to C6-30, P5, P6, P7 and FW-P are written ahead of the loader; a document breaking C6-29's key grammar or any of P5-P7 loads today. Legitimate, but the assembled contract states refusals no shipped loader performs, and only the stage-4 vectors named in phase-4-columns.md:1998-1999 and :2081-2085 will catch it.

16. DUPLICATION THE ASSEMBLER MUST RESOLVE (unchanged from the transcriber's note, verified). ASSEMBLY.md §3 assigns only '`numeric_styles` in full' here, yet r4a.md:115-152 already carries the role restriction WITH its reason, the FORM-not-values sentence, the three families and the six-style table, and r4a.md:155-260 plus r4a_alt.md:136-262 carry C6-27 to C6-30, P5, P6 and P7 in full. r4a.md:150-152 explicitly defers the wire shape, ladder, P1-P4 and recount obligation to §7.5, which is the clean division. Place each rule once; if r4a's opening is cut, the motivation and role reason must move here.

17. DROPPED FROM a9.md AND NOT RESTORED (a9 owns the matrix, so this is a note, not a correction): a9.md:134's clause 'Widths are met by value adjustment inside the value-construction stage, so a pinned cell counts toward a width only when its value already fits it' has no home in §7.6. If the assembler compresses a9's matrix cell to the disposition sentence used here, that clause is lost.

18. OPEN, UNSETTLED BY ANY ARTIFACT (carried, not resolved): (a) P3's ground on `affixed_number` — profile-contract-v4.md:1710-1712 cites Q3 for `count` and `continuous` only, and nothing found guarantees `n_core_numeric ≥ 1` there except AF5 (profile-contract-v6.md:1235), which the assembler should cite if P3 is to stand on three roles; (b) whether P2's floor and P5.c's *W* on `affixed_number` are read over cells or cores — AF7 (r6.md:294-300) puts in place of only `n_core_numeric` for `n_numeric`; (c) a9.md:156 says both keys are EXACT-OBSERVABLE 'read over the cores' on that role, which leaves `NW`, `D` and the pooled-spelling clause unassigned between cores and whole cells. The affixed-number section and this one must agree before assembly.

19. DELTA FRAMING AND LETTER IDENTIFIERS: none. Grep over the corrected section finds no 'supersede', 'carried', 'unchanged from', 'as version 4 has it', and no `C6-` letter identifier. Every identifier it cites is stated here (C6-83, C6-84, C6-85, C6-27 to C6-30, P1-P7) except the cross-artifact citations v4 itself makes (decisions 8 and 10, Q3, AF7, R-P2-1, R-P2-9, R-P3-12, P2-D9, A-P4-5/6/8, canonical text 3.2.1), which are pointers to other sections of the same document or to the plan, not rules referenced in place of being stated. This section does not carry the refusal catalogue, so no `profile_version` walk applies to it.

## GAPS

- `fraction_widths` IS NOT IMPLEMENTED. `grep -rn fraction_widths src/` returns no occurrence, so C6-27 to C6-30, P5, P6, P7 and FW-P have no shipped code to be checked against; they rest on the plan and the v6 delta alone. The shipped loader today enforces only P1, P2, P3 and style-name membership (src/synthtwin/contract.py:4261-4304).
- NO RECOUNT IDENTITY FOR `fraction_widths` IS FIXED BY ANY SEALED ARTIFACT. `numeric_styles` has one (v4 §7.5.7, repeated in generation-method-v1.md G6.4); `fraction_widths` appears nowhere in docs/spec/generation-method-v1.md and nowhere in src/. The window I wrote into its disposition (published count <= recount <= count + pooled value) is taken from docs/spec/v6-build/a9.md:134, which is another unassembled build section, not a source that outranks this one. If the assembler cannot confirm it, the disposition cell should read EXACT-OBSERVABLE with FW-P and nothing more.
- DUPLICATION THE ASSEMBLER MUST RESOLVE. ASSEMBLY.md §3 assigns only '`numeric_styles` in full' to this section, but my instructions also assign `fraction_widths` — and `fraction_widths` is already written in full (C6-27 to C6-30, P5, P6, P7) in r4a.md:155-260 AND r4a_alt.md:136-262, while the six-style table and the role restriction are already in r4a.md:115-152. Three drafts now carry the same rules. Place each exactly once; the pooled-case wording here matches r4a_alt's, which ASSEMBLY.md §3A records as the twice-confirmed reading.
- P3's REASON MAY NOT REACH `affixed_number`. Version 4 states P3's ground as 'n_numeric >= 1 on `count` and `continuous` (Q3)'. I wrote 'the numeric count is at least 1 on these roles (Q3)' over three roles, but no artifact I found says Q3, or any equivalent, guarantees `n_core_numeric >= 1` on `affixed_number`. If it does not, P3 is unfounded on the new role and either needs a stated ground there or must be confined to two roles.
- WHETHER P2's FLOOR AND P5.c's *W* ARE READ OVER CELLS OR CORES ON `affixed_number` IS NOT STATED. AF7 (r6.md:294-300, a14.md 13.4) puts in place of `n_core_numeric` for `n_numeric`, which settles P1 and the census population, but nothing settles whether `small_cell_floor` on that role is applied to core counts or cell counts. Both keys' floors are read from the same setting elsewhere, so an implementer will guess.
- TWO REPORT/PROVENANCE CLAUSES WERE DROPPED FOR LENGTH and must appear somewhere in the assembled document if they are to survive: v4 §7.5.7's requirement that the report name the remainder, how many cells it covered and how many had no point-free spelling (also in generation-method-v1.md G6.4); and P1's citation of plan P2-D9 as the construction that writes out-of-range and contradictory cells (v4:1697-1703).
- IDENTIFIER NUMBERS ARE PROVISIONAL. C6-83, C6-84 and C6-85 were chosen because C6-82 is the highest `C6-` number now present across docs/spec/v6-build/ and the v6 delta. ASSEMBLY.md §1 requires one sequence over the whole document, so all three will move at assembly; the inherited P1-P7, C6-27 to C6-30 and AF7 must not.

## CONFLICTS NOTED

- THE PLAN'S CONSTANT 5 IN CONDITION 4 IS TOO WEAK, AND I TRANSCRIBED IT ANYWAY BECAUSE THE PLAN GOVERNS. A-P4-8 fixes `F >= W - 5 x (small_cell_floor - 1)` unconditionally. The vetted derivation (docs/plans/reviews/material/phase-4-v6-derivation-partition.md, CHECK A3.3, and r4a_meta.md item 'THE (5 - P) TIGHTENING') shows that with P styles NAMED in `numeric_styles`, only 5 - P unnamed styles can share the pool with decimal, so the true bound is `F >= W - (5 - P) x (floor - 1)`. At a floor of 11, `numeric_styles: {"plain": 30, "leading_plus": 20, "(withheld)": 35}` with `fraction_widths: {}` describes no table — three unnamed styles hold at most 30, not 35 — and the plan's form admits it (F >= -15). This is a hole in ratified text, not a wording defect, and it needs an owner amendment; a contract that quietly tightened it would be deviating from the plan.
- THE SHIPPED LOADER DOES NOT REFUSE WHAT §7.5 SAYS A LOADER REFUSES. src/synthtwin/contract.py:4261-4304 checks P1, P2, P3 and key membership only. Nothing in src/ checks `fraction_widths` at all, so a document violating C6-29's key grammar or any of P5, P6, P7 loads today. Version 6 is being written ahead of the code here, which is legitimate, but the assembled contract will state refusals no shipped loader performs, and the stage-4 vectors named in A-P4-6 and A-P4-8 are the only thing that will catch it.
- ONE PLAN SENTENCE IS STILL FALSE AS WRITTEN AND ITS REPAIR IS ONLY PARTIAL. A-P4-5's 'the sum obligation then binds nothing' (phase-4-columns.md:1936-1941) is corrected by A-P4-6 and again by A-P4-8, but the sentence stands in the ratified text with a pointer after it. I wrote the four bounds and did not carry the retracted clause. If the assembled contract is expected to reflect the plan sentence by sentence, this one does not survive that test.
- a9.md AND v4 §7.5.7 GIVE `numeric_styles` TWO DIFFERENT DISPOSITION SHAPES, and I took v4's. a9.md:156 says that on `affixed_number` both keys are 'EXACT-OBSERVABLE against the same two recount identities, read over the cores', which implies the C6-84 identity applies unchanged there; a9.md:133 states C6-84 for the other roles. Neither says whether `NW`, `D` and the pooled-spelling clause are computed over cores or over whole cells on `affixed_number` — the affix pair sits outside the core, so a cell's written text and its core's text differ. The affixed-number section and this one must agree before assembly.

## SOURCES

ENUMERATION, transcribed element by element, both directions. The six
styles: src/synthtwin/contract.py:438-445 ships NUMERIC_STYLES =
("plain","leading_zero","leading_plus","decimal","exponent_lower",
"exponent_upper") — six members, in that order, and my table carries
those six wire spellings and no others. Their "what it names" column is
copied from docs/spec/profile-contract-v4.md:1610-1622. Count agrees
with docs/spec/v6-build/ASSEMBLY.md §4 item 1 ("6 numeric styles"). The
loader's accepted key set is NUMERIC_STYLES + WITHHELD (contract.py:
4282-4288); WITHHELD == "(withheld)" at taxonomy.py:339.

V4 BASE (transcribed, delta framing dropped): profile-contract-v4.md
§7.5.1 :1579-1596 (the three identical-block families and the
form-not-values sentence); §7.5.2 :1597-1609 (role restriction and its
reason); §7.5.3 :1610-1622; §7.5.4 :1623-1675 (the seven-step ladder,
the priority reason, "this ladder is what a twin cell's style IS", the
parentheses/comma rule); §7.5.5 :1676-1695 (wire shape bullets); §7.5.6
:1696-1718 (P1, P2, P3, P4 verbatim in substance); §7.5.7 :1719-1830
(disposition, "why all six", the pooled-cell rule and its withdrawal,
the recount identity clause by clause, the NW-off-VALUES reason, the
ordinary-column reading).

PLAN (governs): docs/plans/phase-4-columns.md A-P4-5 :1916-1954
(sibling placement, its reason, and its own last clause moved by
A-P4-6); A-P4-6 :1955-1999 (conditions 1-3); A-P4-8 :2051-2100
(condition 4 as F >= W - 5 x (small_cell_floor - 1), the six-styles
argument, the vacuity sentence, the floor-11/W-60/F-1 counterexample).

V6 DELTA (content taken, framing dropped): profile-contract-v6.md
:402-410 (numeric_styles and fraction_widths on count, continuous and
affixed_number, with the affix-pair reason); :513-527 (C6-27); :528-532
(C6-28); :533-539 (C6-29); :540-585 (C6-30, P5.a/b/c, the four
conditions); :593-595 (P6, P7 and the R-P3-12 closure); :1182
(fraction_widths EXACT-OBSERVABLE); :1230 (FW-P); :1245-1250 (the §9
rows for P5, P6, P7).

SIBLING V6-BUILD SECTIONS read for agreement, not restated:
ASSEMBLY.md §3 (this section owns "numeric_styles in full"), §3A (both
numeric-roles verifiers independently reached FOUR pooled conditions,
reading condition 4 at a total of zero — the reading my "no fifth
condition" paragraph states), §1 (identifier convention); r4a.md:115-152
and r4a_alt.md:120-262 (role restriction, six-style table, and both
carrying fraction_widths in full — see gaps); r6.md:294-315
(affixed_number quantitative keys read over the CORES, AF7; the
confinement of both keys to exactly three roles; "the matrix is total",
which makes fraction_widths REQUIRED rather than optional); a9.md:133-
134 and :156 (numeric_styles against §7.5.7's identity; the
fraction_widths window I transcribed into the disposition); a14.md:365-
395 (13.1-13.4) and :602-606 (13.33); s3.md:52-56 (bare width keys);
s4.md:363-373 (S13's ten withheld places, which the settings section
owns and this one does not restate).

SEALED GENERATION METHOD, checked and AGREEING: docs/spec/generation-
method-v1.md G6.4 :959-995 states "A pooled cell is written by its own
value" and repeats the recount identity clause for clause, including
the NW reason and the "no outside-the-styles bucket" sentence; G6.5 is
the exponent-case route by which a folded count falls below a raw one.
Its line :477-480 ("the (withheld) remainder added to `plain`") is the
carrier-step ALLOCATION accounting, not the withdrawn spelling rule —
checked so that it would not be mistaken for a conflict.

V5: profile-contract-v5.md:1033 (numeric_styles stays as it is) and
:1391 (the pooled key means a group too small to name).

CODE BEHAVIOUR: contract.py:4261-4304 — the loader enforces P3 (empty
map), key membership, P2 for NAMED styles only, and P1 against
n_numeric; values >= 1 come from _counts(..., 1). `grep -rn
fraction_widths src/` returns nothing.
VERDICT SOUND_WITH_CORRECTIONS errors=15

## ERRORS

1. CORRECTED — INVENTED COUNT (section 10.1, C6-44 binding paragraph): "it has failed twice by omission". Only ONE omission is evidenced. docs/spec/profile-contract-v5.md:1066-1068 binds the catalogue explicitly ("with R11 and R12 reading against 5 instead of against 4"); docs/spec/profile-contract-v6.md:1265-1269 drops that sentence. No artifact records a second occurrence. This is exactly the reason-from-pattern failure the brief names. Changed to "leaving it implicit has already gone wrong, and it goes wrong two ways" — the two DIRECTIONS (4 trips nothing, 5 trips R12) are evidenced; two OCCURRENCES are not.

2. CORRECTED — DROPPED RULE + REASON: docs/spec/profile-contract-v5.md:1183-1190 ("What it still does NOT do, said here rather than left to be found") states that the message does NOT tell the person which options THEIR description was made with, although their settings block records every one, because the no-quoting rule forbids it and the version is read before the settings block has been validated. That rule and its reason are absent from the draft. The v6 delta could omit it (it carried v5 by reference); a self-contained v6 cannot. Restored as "What the message does NOT do", repointed to C6-83 which carries the no-quoting rule. The trailing "reading their own settings block back to them would need a separate command, and none is built" is dropped for length; the operative rule and its reason are kept.

3. FLAGGED, NOT CORRECTED — BOUND STATED WEAKER THAN SOURCE: docs/spec/profile-contract-v5.md:1063-1066 fixes the read POSITION ("the version is read at step 5 before the canonical round trip at step 6"), and src/synthtwin/contract.py:38 pins the same step ("5. read `profile_version`, which must be 5   R11, R12"). The draft says only "before the canonical round trip". Not repaired, because naming steps 5 and 6 would be a dangling reference: no v6-build section carries the loader's ordered path (see the s4.md forward-reference item below). The assembler must either restore the step numbers here or place the ordered list in a 10a section.

4. UNFILLED FORWARD REFERENCE (assembly-blocking, not this section's text): docs/spec/v6-build/s4.md:33 says "Section 10 carries the loader's order of operations and the exact words of the refusal." This section carries the exact words but NOT the order of operations, and grep for R11/R12/R19 across docs/spec/v6-build/*.md returns hits in no other section — no written section carries version 4's §10.1 step list, §10.2 (what the loader does NOT do), §10.3 (parser bounds), §10.4 (canonical round trip) or §10.5 (T1-T4). Unless a 10a section exists, C6-83's required reachability tests for R1-R10 have nothing to locate them against, and s4.md's pointer resolves to nothing.

5. VERIFIED CORRECT — CATALOGUE, both directions, mechanically diffed: the 19 rows were extracted and diffed against docs/spec/profile-contract-v4.md:2475-2495 with only `profile_version < 4`→`< 6` and `> 4`→`> 6` applied; the diff is EMPTY. 19 rows, ids R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,R14,R15,R16,R17,R18,R19 — no gap, no duplicate, no extra, no cell reworded. Framing paragraph = v4:2468-2473 verbatim; the R13-R17 rider = v4:2497-2499 verbatim; "Neither message quotes anything from the document except the two version numbers" = v4:2463-2464; R12's advice and its whole reason = v4:2455-2461 verbatim in substance.

6. VERIFIED CORRECT — MESSAGE: the blockquote was extracted, unwrapped and compared against docs/spec/profile-contract-v6.md:1288-1315; identical, no edit, no reflow damage. Six options named: --keep-value, --missing-value, --identifier, --smallest-group, --first-row, --day-first, and all six are priced in the same clause order the delta has.

7. VERIFIED CORRECT — VERSION WALK under the section as written: `4` → R11 (4 < 6); `5` → R11 (5 < 6); `6` → NO row fires, the loader proceeds to the remaining checks; `7` → R12 (7 > 6). A non-integer `profile_version` falls to R15 (wrong type) via src/synthtwin/contract.py:1480-1485, which the section does not claim otherwise.

8. CONFLICT RESOLVED IN THE SECTION'S FAVOUR, by the source that GOVERNS: the draft flagged plan line 746 ("only that shape joins the refusal catalogue by name (P4-D8)") against docs/spec/v6-build/r5b.md:274-283. docs/plans/phase-4-columns.md:1331-1333 settles it: "**Refusal catalogue:** the closed list of four grows by exactly one named refusal — a time-of-day description whose distinct demand net of its unparsed stand-ins (`n_distinct − n_unparsed`) exceeds its form's finite space". The LOADER catalogue has nineteen rows, not four; the closed list of four is the generation method's (r5b.md:277-278). So "the refusal catalogue" at plan:746 is the GENERATION list. The section's nineteen rows stand, no R20 is owed, and docs/spec/v6-build/r5b_alt.md:25 is the loose phrasing. Section text kept.

9. CONFIRMED CONTRACT/CODE MISMATCH (expected, name it in the assembled document's known-state note, not a text defect): src/synthtwin/profile.py:167 and src/synthtwin/contract.py:109 both set `PROFILE_VERSION = 5`, and src/synthtwin/contract.py:38 reads "read `profile_version`, which must be 5". The stage-6 flip is plan item 8, docs/plans/phase-4-columns.md:1249-1260. The section's OTHER code claim is TRUE as verified: src/synthtwin/contract.py:1487-1493 compares `stated < PROFILE_VERSION` / `stated > PROFILE_VERSION` against the constant at line 109, never against a literal — the binding is genuinely written in code.

10. DISAGREEMENT — THE STANDING TEST IS BIDIRECTIONAL AND THE TEXT STATES ONE DIRECTION. tests/test_profile_version_5.py:679-682 describes tests/test_p3v9f6_migration_names_every_option.py as holding "the set of options named here to the shipped parser's own" — a set EQUALITY. The section (following docs/spec/profile-contract-v6.md:1324-1326) says only that an option added later and not named here turns the suite red. Today src/synthtwin/cli.py's add_argument calls (lines 466-605) ship exactly five publication-changing options — `--smallest-group`, `--identifier`, `--keep-value`, `--missing-value`, `--first-row` — and NO `--day-first`; the other parser entries are `command`, `path`, `--version`, `--twin`, `--out-dir`, `--seed`, `--replace`, none publication-changing. So the contract names an option the parser lacks until P4-D4.6 lands (docs/plans/phase-4-columns.md:880-894, 1405-1407). Not repaired: the one-directional wording is the delta's own, and the plan (1252-1254) requires `--day-first` to be named. Owner or assembler note.

11. DISAGREEMENT — THE EXACT MESSAGE IS FALSE OF A VERSION 5 DOCUMENT. R11 fires for every `profile_version < 6`, and only the two version numbers are filled in, so a version 5 document reads "A version 6 description records things an older description does not — which of synthtwin's own words for 'no value' you named on the command line". A version 5 description DOES record that; it is the premise of docs/spec/profile-contract-v5.md:1053-1056. The sentence is true of a version 4 document and false of a version 5 one. The text is EXACT TEXT fixed by docs/spec/profile-contract-v6.md:1288-1315 and required by the plan, so it is NOT changed here — it needs an owner ruling (either a second filled slot for the reason clause, or wording that does not enumerate what the older version lacked).

12. AGREED WITH THE DRAFT'S GAP — R12 IS FIXED IN SUBSTANCE ONLY. src/synthtwin/errors.py:1471-1483 holds exact R12 wording, but no contract artifact promotes it to EXACT TEXT the way C6-46 does for R11 (v4:2455-2461 and v5 C5-27 at line 1196 both fix substance). Correctly left unpromoted; needs a ruling, not a transcription.

13. IDENTIFIER: `C6-83` verified unused — grep over docs/spec/ finds no `C6-83` anywhere and the highest existing number is `C6-82`. `C6-48` is taken at docs/spec/profile-contract-v6.md:158, `C6-49`-`C6-53` by r6.md per docs/spec/v6-build/ASSEMBLY.md:51, and `C6-54` is doubly claimed (ASSEMBLY.md records the same collision). No `C6-` LETTER identifier appears in the section; no "supersedes", "carried", "unchanged from version 5" or "as version 4 has it"; no rule cited by identifier without being stated (C6-46 is cited in 10.2 and stated in 10.4; C6-83 is cited in 10.4 and stated in 10.3). The assembler still repoints C6-83 into the single sequence.

14. ASSEMBLY NOTE — SECTION-NUMBER COLLISION: this section numbers its parts 10.1-10.4, but version 4 assigns §10.1 to the loader's order of operations, §10.2 to what the loader does NOT do, §10.3 to the two parser bounds (cited as "contract 10.3" in src/synthtwin/contract.py:110) and §10.4 to the canonical round trip. docs/spec/v6-build/ASSEMBLY.md:2 says sections were written against version 4's numbering and the assembler renumbers once, so this is not an error in the text — but if a 10a section is written against v4's slots, two "### 10.3" headings collide and one of them is the parser bounds a code comment points at.

15. NOT AN ERROR, recorded so it is not re-found: version 4's stated reason for R11's advice (docs/spec/profile-contract-v4.md:2451-2453, "That advice is safe to give, because the person who holds an old profile of their own table is normally the person who holds the table") is absent by design — C6-47 narrows and replaces it, and the section carries that narrowing in full. Version 5's measured evidence for pricing the three once-excused options (v5:1117-1160) is also absent; the section preserves its conclusion and its evidential character ("which is what nobody could show for the three that were once excused on exactly that ground"), which is the load-bearing part.

## GAPS

- IDENTIFIER NUMBER for the catalogue rule is provisional. `C6-48` is taken by the delta (kept-side completeness, v6 line 158), `C6-49`-`C6-53` by r6.md per ASSEMBLY line 51, and `C6-54` is claimed TWICE (v6-build/a14.md:70 and v6-build/r5a1.md:75). I took `C6-83`, one above the highest number found anywhere (`C6-82`); the assembler renumbers in one sequence and must repoint it. C6-44 through C6-47 are the delta's own numbers for these same subjects and are kept.
- R12's message is fixed only IN SUBSTANCE by every contract artifact (v4 §10.6, v5 C5-27) — which version is read, which the document claims, update synthtwin, never re-run. The shipped code does have exact wording (errors.py:1466-1483), but no artifact promotes it to EXACT TEXT the way C6-46 does for R11, so I did not promote it either. If the owner wants R12 exact too, the text is in errors.py and needs a ruling, not a transcription.
- No artifact anywhere names a NEW loader refusal row for version 6 — nothing in the delta or in v6-build uses R20 or higher. I invented none. If any other section's rule needs a loader refusal that R13-R17 do not already cover, it takes R20 at assembly and this table grows by that row.
- R18's trigger is transcribed as v4 wrote it (`relationships` carries non-null content). Version 6's relationship manifest is eight reserved slots; whether the loader checks all eight identically is another section's subject and I did not restate it here.

## CONFLICTS NOTED

- THE TIME-OF-DAY CAPACITY REFUSAL: two artifacts and the plan disagree about WHICH catalogue it joins. The ratified plan line 746 (P4-D8) says the infeasible shape "joins the refusal catalogue by name"; v6-build/r5b_alt.md:25 calls it "a generator refusal, named in the refusal catalogue rather than checked here"; v6-build/r5b.md:274-283 says flatly that such a document is VALID, that a LOADER ACCEPTS IT, and that it is refused at the generation-feasibility stage as the fifth member of the generation method's closed list of four. I followed r5b.md and left the loader catalogue at nineteen rows, saying so explicitly. If "the refusal catalogue" in the plan means THIS table, my 10.3 is wrong and the row is R20 — an owner or assembler call, not one I made silently.
- THE DELTA'S C6-44 DROPPED THE BINDING COMPONENT. v5 C5-24 bound the catalogue to the version in force; the delta restated the version integer and the read position but not the binding, which is the defect described in the walk above. Recording it as a disagreement with the delta text, now repaired in this section.
- SHIPPED CODE STILL SAYS 5. `profile.py:167` and `contract.py:109` both set `PROFILE_VERSION = 5`, and `contract.py:38`'s step list reads "read `profile_version`, which must be 5". Expected until the stage-6 version move lands (plan item 8, lines 1249-1260), but a reviewer reading code against C6-44 today sees a contract/code mismatch, so it is named rather than left to be rediscovered.
- "CHARACTER FOR CHARACTER" IS TRUE ONLY UP TO THE LIST CONNECTIVES. The delta (v6 line 1321) says every priced clause other than the new one is C5-26's wording "character for character". Checked against v5 lines 1096-1101: in C5-26 the `--first-row` clause is the last and reads "; and without the --first-row you gave, ..."; in C6-46 it is next-to-last and reads "; without the --first-row you gave, ...", with the "and" moved onto the `--day-first` clause. Substance identical, wording necessarily not. Flagged so a reviewer diffing the two does not record a real edit as a broken promise — the transcription above is the v6 text exactly as the delta has it.

## SOURCES

THE VERSION WALK (the point of this section). Under the catalogue as
written above: `4` fires R11 (4 < 6); `5` fires R11 (5 < 6); `6` fires
NO row and the loader proceeds; `7` fires R12 (7 > 6). The R11 message
fills both numbers from the document and the loader, so 4 and 5 each
read their own version back.
THE HOLE, evidenced. v5 C5-24 (v5 lines 1063-1068) bound the catalogue
explicitly: "The refusal catalogue is version 4's section 10.7,
unchanged, with R11 and R12 reading against 5 instead of against 4."
The v6 delta's C6-44 (v6 lines 1263-1268) drops that whole sentence and
says only that the loader "reads exactly 6". With no binding, the
catalogue in force is v4's own §10.7, whose rows read `< 4` and `> 4`:
then `4` trips NOTHING (the message of C6-46 is unreachable) and `5`
trips R12 and is told to update synthtwin — the exact advice v4 §10.6
forbids for an older document. C6-44's second paragraph above closes it.

CATALOGUE: transcribed element by element from
docs/spec/profile-contract-v4.md lines 2466-2500 — 19 rows, R1..R19,
counted: R1,R2,R3,R4,R5,R6,R7,R8,R9,R10,R11,R12,R13,R14,R15,R16,R17,
R18,R19. Every cell is v4's own text character for character EXCEPT
R11's and R12's trigger cells, where `4` becomes `6`. The framing
paragraph (own message, exact-shape test, reachability test, the
`n_rows` prohibition and its reason) is v4 lines 2461-2465; the "R13 to
R17 each name the KEY and the RULE" paragraph is v4 lines 2498-2500.
R11/R12 advice and reasons: v4 §10.6 (lines 2436-2462); v5 C5-27 (line
1196) keeps R12 in substance. Quoting rule: v4 §10.6 last line + v5
C5-28.
VERSION RULE: v6 C6-44/C6-45 (lines 1263-1273); v5 C5-24/C5-25 (lines
1063-1078). Shipped code confirms the binding: contract.py:1487-1493
compares `stated < PROFILE_VERSION` / `stated > PROFILE_VERSION`
against contract.py:109's constant, not a literal.
MESSAGE: transcribed verbatim from v6 lines 1288-1315 (blockquote, no
edits). Its provenance/pricing paragraphs: v6 lines 1277-1287 and
1316-1325. Six options, counted against the shipped parser
(src/synthtwin/cli.py add_argument calls): `--smallest-group`,
`--identifier`, `--keep-value`, `--missing-value`, `--first-row` exist
today; `--day-first` is the sixth and is NOT yet in cli.py — the plan
adds it (P4-D4.6, plan lines 881-894; "One new option (--day-first)",
plan line 1405) and plan line 1252-1254 requires the message to name
and price EVERY publication-changing option "including --day-first".
The parser's other options are not publication-changing: `--version`,
`--twin`, `--out-dir`, `--seed`, `--replace` (the last three are
generate/validate-only). The pricing of the five older options is
measured evidence, not judgement: v5 lines 1117-1160.
STANDING TEST: v6 line 1324 ("A test derives the option set from the
shipped parser"); tests/test_profile_version_5.py:681 names
tests/test_p3v9f6_migration_names_every_option.py as the test that
"holds the set of options named here to the shipped parser's own".
C6-47: compressed from v6 lines 1327-1367, keeping the struck
inference, the surviving bound, and the recurring obligation.
GENERATION-FEASIBILITY note in 10.3: v6-build/r5b.md lines 268-283
("Such a document is a VALID description and a loader accepts it").
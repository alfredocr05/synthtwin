VERDICT SOUND_WITH_CORRECTIONS errors=12

## ERRORS

1. INVENTED GLOSS, WRONG FOR S11 (the one substantive defect). Submitted C6-104 bullet 1: 'S8, S10 and S11, each of which checks a name against the set of column names'. S11 does not check a name against a set: docs/spec/profile-contract-v4.md:1849 states it as '`publication_notes` is grouped by column in schema order', and src/synthtwin/contract.py:4479-4480 as 'the notes are grouped by column, in the order the columns come in the table'. Neither source characterises the three as name checks; both say only that they need BOTH halves (src/synthtwin/contract.py:4757-4762). An implementer building S11 from the submitted gloss writes a membership test and never checks the grouping. CORRECTED: the three are named individually with their v4/shipped wordings.

2. DROPPED RIDER, C6-112. docs/spec/profile-contract-v4.md:2415-2417 reads 'The check is a re-serialization and a byte comparison; it does not install a parse hook of any kind, AND THE OFFLINE POLICY'S CALLBACK RULES ARE NOT ENGAGED BY IT.' The submitted text drops the final clause when replacing it with the step-4 material from src/synthtwin/contract.py:1421-1428. The dropped clause is the one that tells a reviewer the round trip is outside the callback policy rather than merely compliant with it. RESTORED.

3. AMBIGUOUS PLAN CITATION, C6-112: '(plan D6.2)'. Transcribed bare from src/synthtwin/contract.py:1425, where it means the offline guarantee's decision (docs/plans/phase-0-public-skeleton.md:171 'D6. The offline guarantee'; docs/plans/phase-2-generator.md:982 'Offline-scanner policy extensions (D6.2)'). But the plan that GOVERNS this contract has its own P4-D6.2 = 'Excel-artifact spellings join the missing table' (docs/plans/phase-4-columns.md:1108) and P4-D6.1 = the hole-spelling reproduction rule (docs/plans/phase-4-columns.md:1016). A reader of the assembled v6 resolves 'D6.2' against the wrong decision. CORRECTED to 'offline-guarantee plan D6.2, not P4-D6.2'. (v4's other citation, 'plan P2-D1' in C6-107, is prefixed and unambiguous — left alone.)

4. ENUMERATION COUNT NOT STATED, 10.4. The catch table has eight rows and the text states no count, against ASSEMBLY.md standing check 1 ('every enumeration is written out, with its count stated beside it'). This is precisely where the live discrepancy hides: src/synthtwin/contract.py:1519-1526 says 'ONE CHECK CATCHES SEVEN DEFECTS' and this contract now makes it eight. CORRECTED: '— EIGHT defects'.

5. MINOR, POLARITY OF S13, C6-104 bullet 2: 'what it SAYS is a fact about the whole description — it was made at a floor of one and it holds something back'. Transcribed from the code comment at src/synthtwin/contract.py:4780-4786, but read cold it inverts the rule: S13 states that at a floor of one NOTHING is held back (docs/spec/profile-contract-v6.md:1257). CORRECTED to 'what it REPORTS', which is what the comment means and what the refusal says.

6. VERIFIED, NO CHANGE — order table, docs/spec/profile-contract-v4.md:2302-2312 vs the section, both directions: 8 rows, 8 rows; every step text and every refusal id matches, including 'R13 … R18' at step 7. The step-5 additions R14/R15 are correct against src/synthtwin/contract.py:1443-1470 (non-dict document -> wrong-type; absent `profile_version` -> missing-key; non-integer -> wrong-type), and the accompanying paragraph states the reason. Both 'why' paragraphs (v4:2314-2327) are word for word.

7. VERIFIED, NO CHANGE — 10.2: three items, three items (v4:2329-2340), verbatim with 'profile'->'description' and the phase framing of v4:2294 removed. The no-upgrade sentence matches docs/spec/profile-contract-v5.md:1070-1075 and docs/spec/profile-contract-v6.md:1271-1273; deferring its reason to part two is legitimate under the no-restatement rule.

8. VERIFIED, NO CHANGE — 10.3: 32 and 64 are src/synthtwin/contract.py:119-120 (`MAXIMUM_DEPTH = 32`, `MAXIMUM_NUMBER_CHARACTERS = 64`); the 'exactly two / neither scales / no other cap / R19 / two halves of the product' wording is the shipped comment at contract.py:106-118, and 'the profiler's own reader ... the two halves of the product' is that comment verbatim, not a paraphrase invented to de-phase v4. Four pre-scan bullets against four in v4:2354-2363, each matching `_scanned` (contract.py:1363-1407), `_begins_a_number` (1325-1327: `-` or `0`-`9`) and `_continues_a_number` (1330-1340: `0`-`9` `.` `e` `E` `+` `-`). No bound is stated weaker anywhere in the section than in the constants.

9. VERIFIED, NO CHANGE — 10.4/10.5/10.6: seven catch rows are v4:2386-2396 unaltered and the eighth (CR LF / byte length) is s3.md:119-136 plus src/synthtwin/contract.py:1534-1537; the two not-caught items are v4:2398-2413 verbatim; T1-T4 are v4:2424-2443 word for word (only 'contract'->'format'); the return members are v4:2503-2506 plus `publication_notes`, which `Profile` (contract.py:1184-1201) and `TOP_LEVEL_KEYS` (contract.py:129-139) both carry, so transcribing WITH it is right and v4's omission is the defect. No delta framing, no `C6-` letter identifier, and `C6-100`-`C6-113` collide with nothing in docs/spec/v6-build (highest in use: `C6-54`, plus `C6-80`-`C6-82`).

10. CONFIRMED DISAGREEMENT (author flagged; I re-checked and agree, not fixable here) — the `T1` collision is real and live: loader `T1` at v4:2424 and cited by tests/test_p2c1f8_specification_agreement.py:13-14, `time_of_day` `T1` at docs/spec/profile-contract-v6.md:318-321 and the invariant table at v6:1238, both sanctioned to keep their letters by ASSEMBLY.md section 1. Prose disambiguation in this section and in s3.md:99-102 is not uniqueness and tools/spec/check_assembly.py will report it. Owner or assembler must rename one family.

11. CONFIRMED DISAGREEMENT WITH ANOTHER WRITTEN SECTION, not flagged by the author and not repairable in this section: docs/spec/v6-build/s3.md:120 says 'Section 10.4 makes this the loader's first semantic check', while this section's step 5 (version) precedes step 6 (round trip). Already recorded at s3_meta.md:21 as inherited from v4:181-182. The assembled document would carry both sentences; s3.md owns the fix.

12. CONFIRMED CONFLICTS NOTED WITH SHIPPED CODE (all as the author reported; each re-verified): `_round_tripped`'s docstring lists '`05`' among what the round trip catches (contract.py:1519-1526) while C6-111 and s3.md:109-111 say `05` stops the parse at step 4 — documentation defect, behaviour correct. `load_profile` wraps steps 3-8 in a MemoryError handler raising R19 (contract.py:4866-4875) though v4's table gives R19 to step 2 only — left as v4 has it, part two should settle. `validate_local_path(raw_path, purpose='description')` and `PathValidationError` (contract.py:4841) appear in no version of the contract — grep of v4, v5, v6 finds nothing. `_validated` returns `profile_version=PROFILE_VERSION` rather than the integer read (contract.py:4800). And `PROFILE_VERSION = 5` (contract.py:109) while C6-44 fixes 6 (v6:1265-1269) — part two's, but the step-5 row's forward reference is written so that it stays correct.

## GAPS

- Two section numbers are placeholders, marked in the text with [assembly: ...]: the section holding the version rule and refusal catalogue (part two), and the time-of-day invariant table that T1-T5 live in. ASSEMBLY.md section 2 says such placeholders must all be resolved in the renumbering pass.
- The `C6-` numbers used here are the block 100-113, chosen only to miss numbers other drafts already hold (`C6-1`...`C6-54` across the build folder, and `C6-80`...`C6-82` in r4b.md). They carry no meaning; the assembly renumbers into one sequence over the whole document.
- Whether R2 is raised at step 1 or step 2 is not established. Version 4's table assigns it to step 1 ('resolve and open'), the shipped loader raises it from the read call at step 2. Left exactly as version 4 has it, because no artifact settles which the contract means and the refused documents are the same either way.
- No source states a rule for the loader's PATH argument beyond 'a filesystem path to the description'. The shipped loader applies a lexical local-path check (plan D6.1) before any filesystem call; whether that belongs in this contract at all is unsettled (see conflicts noted).

## CONFLICTS NOTED

- IDENTIFIER COLLISION, `T1`-`T4` against `T1`-`T5`, and standing check 4 of ASSEMBLY.md exists for exactly this. The loader's type rules are `T1`-`T4` (v4 lines 2424-2443); they are cited by v6-build/s3.md 3.2.1 and by tests/test_p2c1f8_specification_agreement.py:13, so they cannot be renamed silently. ASSEMBLY.md section 1 sanctions `T1`-`T5` for the `time_of_day` role, and the v6 delta already ships them (v6 lines 318-325 and the invariant table at 1238-1242). One document would carry two different `T1`s. s3.md's workaround and mine are prose disambiguation ('NOT the time_of_day invariant that carries the same letter'), which is not uniqueness. The assembler or the owner must rename one family; I did not, because both sides are cited.
- VERSION 4 SECTION 10.8 IS INCOMPLETE against the shipped loader and against version 6's top level. It lists the top-level facts, the source block, the settings block, the relationship manifest and the columns; the shipped `Profile` (src/synthtwin/contract.py:1184-1201) also carries `publication_notes`, which is a top-level key of this format. I transcribed WITH `publication_notes` rather than reproducing the omission.
- VERSION 4'S STEP-5 ROW IS INCOMPLETE. It lists R11 and R12 only. Shipped `_versioned` (contract.py:1434-1470ff) also refuses at that step when the whole document is not a block of named entries (R15), when `profile_version` is absent (R14) and when it is not a whole number (R15). Two implementations built from v4's table alone would disagree about where a version-less document is refused and therefore about which message its holder sees. I transcribed with R14 and R15 added.
- VERSION 4 SECTION 10.4 IS INSUFFICIENT ON ITS OWN and would let two conforming implementations accept different files. It says only 'requires the result to equal the file's text byte for byte'. A loader whose only permitted read call decodes with universal newlines never sees the CR bytes, so a CR LF file passes a text-only comparison. The shipped loader compares the UTF-8 byte length with the file size as well (`_round_tripped` at contract.py:1500-1537, reasoned in `_utf8_length` at 1266-1288), and v6-build/s3.md 3.3 states that as normative. My section carries the conjunct and adds a row to the catch table; flagged because the version 4 base text this section was pointed at does not contain it.
- SHIPPED DOCSTRING CONTRADICTS THE CONTRACT (documentation defect, behaviour is correct). `_round_tripped`'s docstring, contract.py near line 1519, lists among the seven defects 'a non-canonical number spelling such as `1.0e2` or `05`'. Version 4 section 10.4 says in terms that `05` NEVER reaches this check, because JSON has no grammar for a redundant leading zero and the parse stops at step 4 with R5; v6-build/s3.md lines 109-111 repeats that. The code does the right thing, its own docstring describes a check it does not perform, and this contract's text is what an implementer would build the test around.
- SHIPPED R19 IS WIDER THAN VERSION 4'S TABLE. Version 4 assigns R19 to step 2 alone. `load_profile` (contract.py:4811ff) also wraps steps 3 through 8 in a MemoryError handler that raises R19. The wider behaviour is right - a large document can exhaust memory at the parse or the re-serialization, not only at the read - but the contract's order table says otherwise. I left the table as version 4 has it, since the refusal catalogue is part two's and this is best settled there.
- SHIPPED PATH VALIDATION IS UNSTATED IN EVERY VERSION OF THIS CONTRACT. `load_profile` calls `validate_local_path(raw_path, purpose='description')` (plan D6.1) before any filesystem call and raises `PathValidationError`, not one of the catalogued refusals; grep finds no mention of D6.1, of a local-path rule, or of that error in v4, v5 or v6. It does not affect which DOCUMENTS are accepted, so I left it out of the section rather than making up a rule, but step 1 of the contract's own order table is silent about a check that runs before it.
- MINOR, RECORDED SO IT IS NOT REDISCOVERED: `_validated` (contract.py:4798-4801) builds the returned object with `profile_version=PROFILE_VERSION`, the loader's own constant, not the integer read from the document. Harmless while step 5 demands exact equality, but it means the returned object cannot be used as evidence of what the file said.

## SOURCES

Base transcription, element by element:

- ORDER OF OPERATIONS table (8 rows), the two "why" paragraphs, the
  duplicated-`profile_version` consequence: profile-contract-v4.md
  lines 2292-2327. Version 5 C5-24 (v5 lines 1063-1068) points at
  v4 10.1 for the order; version 6 C6-44 (v6 lines 1265-1269) says the
  version is read "exactly where version 5 reads it". No source alters
  the order, so v4 is the base throughout part one.
- WHAT IT DOES NOT DO (3 items, with v4's reasons): v4 lines 2329-2340
  (feasibility / repair / table, plan P2-D1). The no-upgrade sentence
  pointing at part two: v5 C5-25 (lines 1070-1075), v6 C6-45 (lines
  1271-1273).
- THE TWO BOUNDS: v4 lines 2342-2377. Values 32 and 64 confirmed against
  the shipped constants src/synthtwin/contract.py:119-120
  (`MAXIMUM_DEPTH = 32`, `MAXIMUM_NUMBER_CHARACTERS = 64`) and its
  comment at 110-118, which states the same "exactly two, neither
  scales with the table, no other cap" rule. Four pre-scan bullets
  transcribed from v4 2354-2363 and checked line by line against
  `_scanned` (contract.py:1343-1409): quote toggling with
  odd-backslash escape, nothing counts inside a string, `{`/`[` up and
  `}`/`]` down against 32, numeric token starting at `-` or a digit and
  continuing over `0`-`9 . e E + -` against 64. Depth-six claim:
  v6-build/s3.md 3.4 (lines 138-157).
- THE ROUND TRIP: v4 lines 2379-2417. The seven-row catch table is v4's
  own, unchanged. The eighth row and the byte-length conjunct come from
  v6-build/s3.md 3.3 (lines 123-136), which states them normatively,
  and from shipped `_round_tripped` / `_utf8_length`
  (contract.py:1500-1537, 1266-1288).
- WHAT IT DOES NOT CATCH (review item P2-C1-F8): v4 lines 2398-2413,
  reinforced by v6-build/s3.md lines 104-111.
- NO CALLBACK SLOT: v4 lines 2310 and 2415-2417 plus shipped `_parsed`
  (contract.py:1410-1432), which names plan D6.2 and gives the
  duplicate-key reason.
- TYPE RULES T1-T4, word for word: v4 lines 2419-2443. T1 is also
  restated in v6-build/s3.md lines 96-102 and cited by
  tests/test_p2c1f8_specification_agreement.py:13.
- ORDER WITHIN STEP 7 (S8/S10/S11 last, S13 with the top level): shipped
  `_validated` docstring and body (contract.py:4756-4797) and
  `_cross_checks` (4468-4480). S8/S10/S11 wordings checked against v4
  lines 1848-1851; S3 against v4 line 1843; S13 against v6 line 1257.
- WHAT THE LOADER RETURNS: v4 lines 2501-2508, plus the shipped
  `Profile` dataclass (contract.py:1184-1201) for the
  `publication_notes` member v4's sentence omits.
- Identifier convention and the "no C6- letter" rule: v6-build/
  ASSEMBLY.md sections 1 and 4; amendment A-P4-11.
- The ratified plan (docs/plans/phase-4-columns.md) was grepped for
  "loader": every hit concerns the version integer, role enumerations,
  settings keys or role invariants. Nothing in it touches the order of
  operations, the bounds, the round trip, the type rules or the return
  value, so the plan neither governs against nor amends this section.
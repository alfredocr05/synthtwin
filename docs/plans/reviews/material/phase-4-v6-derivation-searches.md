# searches

**VERDICT:** SOUND_WITH_CORRECTIONS

## Errors the verifier found (19)

1. HEADLINE, load-bearing: the transcribed runnable form does not produce the transcribed manifest — the F15 defect repeated inside the fix for F15. Run over the stated scope it emits FIFTY-TWO output lines (fifty outside §12A) against a manifest of forty-three, because `rg -U` prints every line a multi-line match touches. The seven wrap-crossing matches each print two lines: CHANGELOG.md:466+467, SECURITY.md:304+305, src/synthtwin/profile.py:150+151, src/synthtwin/taxonomy.py:2616+2617, tests/test_p3v4f1_kept_values.py:57+58, tests/test_p3v9f6_migration_names_every_option.py:481+482, tests/test_profile_version_5.py:23+24. A battery built on the stated command is red on the day it lands.

2. HEADLINE, load-bearing over-refusal: Specification 2's window rule, run over the scope it inherits from Specification 1 (which admits docs/spec/profile-contract-v6.md outside §12A), flags two windows that are NOT in its manifest and NOT excluded — docs/spec/profile-contract-v6.md:456-468 (C6-D1's eleven-member binding table, six distinct old members) and docs/spec/profile-contract-v6.md:1620-1623 (the §14 `format` (11) enumeration, six distinct old members). Both are the CORRECT version-6 text. The search as transcribed demands an edit to the very statements the migration moves toward, and is red on landing.

3. INVENTED ELEMENT: 'Running the pattern list over the excluded plan finds FOURTEEN vocabulary-count statements in docs/plans/phase-3-product.md ... :2826, :4256, :4302, :4316, :4328, :4329, ...'. The pattern list finds THIRTEEN. `:4328` is a phantom: docs/plans/phase-3-product.md:4327-4328 reads 'the word is one / of thirteen this package publishes' — 'one of thirteen', which P4 requires as 'one of the/these thirteen' and does not match. The :4329 hit is a separate `thirteen-member` match. Doubly instructive: :4328 IS a real count statement the eight patterns miss, so the list is not closed over natural phrasings — which the derivation nowhere declares.

4. WRONG COUNT: 'all 47 `###` entries beneath it' (repeated as 'Every one of the 47 headings below it is `###`'). CHANGELOG.md has 45 `###` headings. 47 is the count of ALL heading lines: `# Changelog` at CHANGELOG.md:1, `## [Unreleased]` at CHANGELOG.md:7, plus 45 `###`.

5. WRONG LINE CITATION: 'src/synthtwin/generation.py:4119, :4121' are cited as per-member format dispatch sites. Neither line carries a format member. src/synthtwin/generation.py:4119 is `if resolution == "date":` and :4121 is `if resolution == "quarter":`. The members are at :4120 `return "iso-date"`, :4122 `return "year-quarter"` and :4123 `return "iso-datetime"` — and :4123 is omitted from the list entirely.

6. MISSING FROM THE SOURCE SIDE: src/synthtwin/parsing.py:1299 — `if format_name != "iso-datetime":`, inside `_clock_of` (src/synthtwin/parsing.py:1293-1300) — is a per-member format branch absent from Specification 2's dispatch-ladder list. It must gain `iso-mixed`, `month-first-datetime` and `day-first-datetime` at the flip; without it those three formats silently return no clock.

7. MISSING FROM PART E: adding docs/spec/profile-contract-v6.md to dispositions.GOVERNING is red at tests/test_p2c4f1_disposition_registry.py:334, which asserts `set(RELATIVE) == set(dispositions.GOVERNING)`. Part E names GOVERNING, the seal and SURFACES but never names the RELATIVE map at tests/test_p2c4f1_disposition_registry.py:123-131 nor the CONTRACT6 path constant it needs beside :122.

8. MISSING FROM PART C: four live `profile-contract-v5.md` naming surfaces are absent. tests/test_claim_inventory.py:3357 — `if asked == "A-P3-30" and relative.endswith("profile-contract-v5.md"):` — is LIVE CODE keyed on the v5 filename inside `_surface_text`. tests/test_p2c4f1_disposition_registry.py:369 is a LIVE ASSERTION listing v5 by name. Also absent: tests/test_claim_inventory.py:2979 and tests/test_p2c4f1_disposition_registry.py:359.

9. FALSE JUSTIFICATION: 'P7 carries the tail `not spelled` because `the thirteen are` alone also catches tests/test_p3v4f1_kept_values.py:2265 ("THE OTHER THIRTEEN ARE ROUND 7's")'. The string `the thirteen are` occurs exactly ONCE in the whole tracked tree, at src/synthtwin/summary.py:845 — which is the target, not the collision. tests/test_p3v4f1_kept_values.py:2265 reads 'THE OTHER THIRTEEN ARE'; the colliding form is the shorter `thirteen are`.

10. THREE OF FOUR WITNESSES DO NOT WITNESS: the wrap-tolerance justification cites 'SECURITY.md:304-305, src/synthtwin/profile.py:233-234, CHANGELOG.md:366-367, tests/test_p3v9f6_migration_names_every_option.py:48-49'. Only SECURITY.md:304-305 is a wrap-crossing match ('one of the\n  thirteen'). src/synthtwin/profile.py:233 and CHANGELOG.md:366 are each matched by P3 (`own thirteen`) wholly within one line, and at tests/test_p3v9f6_migration_names_every_option.py:49 both words of `own thirteen` sit on line 49. The genuine witnesses are the seven listed in `corrected`.

11. FALSE GENERALISATION IN A NORMATIVE RULE: 'The reported line is the line carrying the word `thirteen`, which for a match spanning a wrap is the second line of the two.' False at src/synthtwin/taxonomy.py:2616-2617, where the match is `all thirteen\n    printed` and `thirteen` is on the FIRST line — :2616, which is the line the manifest itself lists.

12. MISDESCRIBED ARTIFACT: 'tests/test_claim_inventory.py:3835 the same message quoted in a comment'. It is not a comment. tests/test_claim_inventory.py:3832-3836 is an assertion message string; :3835 reads `"this synthtwin reads version 5' -- before calling this closed."` inside it.

13. MISATTRIBUTED QUOTE: the `_AMOUNTS_TO` entry attaches to tests/test_claim_inventory.py:3237 the words '"was/were are deliberately absent ... history is not what this ban is drawn around"'. :3237 is only `_AMOUNTS_TO = r"(?:is|are)\b"`. The quoted comment is at tests/test_claim_inventory.py:3233-3236.

14. FALSE AUDIT STATEMENT: 'Widening to `\bsix\b` within 100 chars of format|calendar|parser over the whole tree returns only excluded documents'. It returns thirteen lines, two of them not excluded: tests/test_p2c5f2_identifier_classes.py:38 ('every one of the six exact counts asserted') is IN the search scope, and docs/spec/generation-method-v1.md:2800 ('parser's own answers tie those six to the published counts') is a governing spec, neither a plan nor a review. Both are noise so the conclusion survives, but the parenthetical also lists docs/spec/profile-contract-v4.md:914-918 as one of that search's returns — it is not returned by it at all, and it is an enumeration, not a statement of the count.

15. TRANSCRIPTION INFIDELITY IN A NORMATIVE QUOTE: the C6-31 quote renders the stand-in numbers as ASCII `-9999, -999`. docs/spec/profile-contract-v6.md:652 uses U+2212 MINUS SIGN for both signs. Verified by codepoint.

16. INTERNAL CONTRADICTION THAT WOULD BE TRANSCRIBED WHOLE: the EXCLUSIONS section concludes that docs/plans/phase-3-product.md's count statements 'must be ENUMERATED IN THE CLAIM-MIGRATION TABLE' per docs/plans/phase-4-columns.md:1120-1124, but Specification 1's 'WHERE IT LOOKS' admits no `docs/plans/` path, its 43-line manifest contains none, and its battery asserts that set exactly. The finding is stated and then not carried; as transcribed the two halves conflict.

17. OMITTED FROM THE EXCLUDED-SURFACE CENSUS: docs/plans/phase-4-columns.md:1122 itself states the count — 'a sealed governing sentence that counts thirteen / words' — and is matched by the pattern list. The census of surfaces stating the size outside the scope names only docs/plans/phase-3-product.md and misses the governing plan's own sentence.

18. UNDISCLOSED LATENT OVER-REFUSAL: P3, P4 and P6 are not role-safe, and version 6 gives the ROLE vocabulary thirteen members (docs/spec/profile-contract-v6.md:204, restated at :151, :896, :911, :1259, :1608). A true version-6 sentence of the form 'one of the thirteen roles' is matched by P4 and, under 'a hit not in it ... is red at once', turns the tree red for stating a fact the contract requires. The tree passes today only because :896, :911 and :1259 happen to be phrased otherwise.

19. MINOR CITATION SLIP: 'test_every_governing_document_is_a_surface (:2584-2604)'. The function runs to tests/test_claim_inventory.py:2606.

## GAPS declared

- The 'ten spellings / three stand-in numbers' ARITHMETIC has no vetted manifest. C6-MIG's row at docs/spec/profile-contract-v6.md:1560 covers 'the count of the published vocabulary -- "thirteen words" AND EVERY ARITHMETIC ON IT', and the ten-spellings half changes to eighteen under C6-31 (docs/spec/profile-contract-v6.md:646-651). I ran a census (rg -U -P -i '\bten[\s#*]+(?:fixed[\s#*]+)?(?:spellings|text[\s#*]+spellings|words)') and it returns 21 lines including src/synthtwin/taxonomy.py:1213, :2547, :2614; src/synthtwin/contract.py:842, :2419; src/synthtwin/validation.py:949, :1222, :1296; src/synthtwin/profile.py:234, :806; README.md:218; SECURITY.md:281; CHANGELOG.md:367; tests/test_p1r7f2_declaration_disclosure.py:161; tests/test_p1r6f9_declared_values.py:107; tests/test_ap326_unrebuildable_reading_rule.py:508 -- but it ALSO returns unrelated hits (tests/test_p3v6f1_identifier_corner.py:452 'the ten spellings that open with a sign' is about numeric forms; tests/test_p3v8f5_published_keys.py:208 and src/synthtwin/contract.py:1928-1929 need reading). I did not design or verify a phrase list that separates them, so I cannot give an exact manifest. Do not transcribe the raw census as a manifest.
- I did not build searches for the two adjacent enumerations that also move at the same flip and have no row in section 12A: `resolution` 3 -> 4 (src/synthtwin/contract.py:432 and src/synthtwin/taxonomy.py:455, against docs/spec/profile-contract-v6.md:1625) and `time_precision` 5 -> 6 (src/synthtwin/contract.py:434, against docs/spec/profile-contract-v6.md:1627-1628). I confirmed the constants and the new counts by reading, but produced no hit manifest for the prose that states them.
- For the FORMAT search I could not find any live prose count in scope, so the manifest is enumeration-only. I cannot rule out a surface that states the count in words I did not think to search for. The phrasings I tried were: six/6 followed by formats, format members, parser families, families, calendar formats; and 'six' within 100 characters of format/calendar/parser across the whole tracked tree including docs/. An honest reading is: I found no count prose in scope and I looked in those places.
- The 'four or more distinct members in a ten-line window' rule for the FORMAT search is my own threshold, not derived from anything in the repository. It happens to separate the three real enumerations from per-member test rows in this tree, but it is a heuristic and I did not test it against a hostile case (for example a doc paragraph naming four members in passing).
- I did not run the test suite. Every claim about what goes red at the flip is derived from reading the assertions and from executing the claim inventory's own pattern functions read-only through importlib; I did not actually set PROFILE_VERSION to 6 and run pytest, and I was told to change nothing. In particular, the twelve tests/test_contract_loader.py fixtures carrying "profile_version": 5 are listed as version surfaces on the reading that the loader gate at src/synthtwin/contract.py:1435 refuses anything other than the shipped number; I did not execute them to confirm each one actually fails at 6.
- I established that no test pins DATE_FORMATS' membership, length, or the agreement of the two tuples by grepping for len(...), == comparisons, and set(...) constructions over src/ and tests/. A test that pinned it by some other route -- for example by comparing a produced document against a golden file that happens to enumerate the members -- would not appear in that grep. tests/reference/generation-reference-vectors.json:2371 carries "format": "year-quarter" but that is a single-member value, not an enumeration.
- The C6-MIG row at docs/spec/profile-contract-v6.md:1559 ('the twin writes every absent cell as an empty field'), :1563 ('publishes no values at all'), :1564-1566 (the three residuals) and :1568 (the loud-decline sentences) were outside my task and I ran no searches for them. I cannot say whether their 'where it lives' columns are complete.

## CORRECTED MATERIAL

================================================================================
WHAT I RE-VERIFIED AND FOUND CORRECT (transcribe these unchanged)
================================================================================
- The 43-line hit manifest: all 43 file:line quotes resolve exactly at the
  lines named. Per-file counts (3,1,5,1,5,9,4,2,1,4,2,1,1,1,2,1) sum to 43
  across 16 files. Verified by reading every line.
- The 22-line complement: exact and complete. 67 lines in scope carry
  `thirteen`; the eight patterns match 45 distinct thirteen-lines (43 targets
  + docs/spec/profile-contract-v6.md:1513 and :1560); 67 - 45 = 22.
- F15: the clause's own search at docs/spec/profile-contract-v6.md:1522-1527
  returns THIRTEEN lines, the thirteenth being :1560. Confirmed by running.
- Part D: running the shipped machinery with shipped=6 yields exactly the ten
  stale claims listed, at exactly those lines. Confirmed by execution.
- docs/spec/profile-contract-v6.md:996 and :1289 carry version-6 claims;
  v6 is absent from SURFACES and VERSION_SURFACES. Confirmed by execution.
- All Part A and Part B citations. All disposition/seal/registry citations.
- The CHANGELOG argument: one `##` at CHANGELOG.md:7; CHANGELOG.md:15 says
  "there is no tag and nothing is published"; :366, :444, :467 all sit between
  `### Changed in Phase 3` (:314) and the next `###` (:485); :311 and :2172
  are correctly not matched.
- The six-forms noise census: exactly ten sites, every one correctly named.
- docs/spec/profile-contract-v5.md holds exactly five (838, 852, 875, 1139,
  1244); docs/spec/profile-contract-v4.md holds zero.
- Both DATE_FORMATS tuples, _FORMAT_EXAMPLES, the 6/5/5 test-table arities,
  and the finding that nothing pins the tuples.
- No surface states the vocabulary size as the numeral `13`.

================================================================================
SPECIFICATION 1 — THE VOCABULARY-COUNT SEARCH (published vocabulary, 13 -> 23)
================================================================================

NEW COUNT AUTHORITY (quote before transcribing any arithmetic):
  docs/spec/profile-contract-v6.md:642-656  "C6-31 (supersedes C5-15). The
    published vocabulary is a closed list of THREE parts ... Eighteen text
    spellings ... Three stand-in numbers, unchanged: -9999, -999, 9999. ...
    Two calendar placeholders: `1900-01-01` and `9999-12-31`. Twenty-three
    members in all."
    TRANSCRIBER'S NOTE: the file writes the stand-in numbers with U+2212
    MINUS SIGN, not ASCII hyphen-minus. docs/spec/profile-contract-v6.md:652
    reads exactly: "- **Three stand-in numbers**, unchanged: -9999, -999,
    9999." where each leading sign is U+2212. Reproduce the codepoint or
    state that the sign has been normalised; do not silently substitute.
  docs/spec/profile-contract-v6.md:1636-1638  "**The published vocabulary
    (23):** eighteen text spellings ... three stand-in numbers; two calendar
    placeholders."

WHERE IT LOOKS (unchanged from the clause, PLUS CHANGELOG.md):
  Tracked files under `src/` or `tests/`, or one of `README.md`, `SECURITY.md`,
  `STATUS.md`, `CLAUDE.md`, `AGENTS.md`, `CHANGELOG.md`, and
  `docs/spec/profile-contract-v6.md` OUTSIDE lines 1491-1569 (section 12A).
  Section 12A begins at docs/spec/profile-contract-v6.md:1491 ("## 12A. The
  claim-migration table") and its last non-blank line is :1568; section 13
  begins at :1570.

WHAT IT MATCHES — a list of EIGHT patterns, case-insensitive, applied to the
whole file as one string (not line by line). `S` abbreviates `[\s#*]+` and `Z`
abbreviates `[\s#*]*`.

  P1  thirteen S (?:published S |fixed S )? words
  P2  thirteen Z - Z member
  P3  own S thirteen
  P4  one S of S (?:the|these) S thirteen
  P5  outside S (?:the|those) S thirteen
  P6  member S of S the S thirteen
  P7  thirteen S are S not S spelled
  P8  all S thirteen S printed

WHY THE SEPARATOR IS WRAP-TOLERANT. This repository hard-wraps prose at about
seventy-two characters. SEVEN of the forty-five matches genuinely cross a line
break, and a line-bound separator would lose all seven:
  CHANGELOG.md:466-467                                  'own\n  thirteen'
  SECURITY.md:304-305                                   'one of the\n  thirteen'
  src/synthtwin/profile.py:150-151                      'own\n#    thirteen'
  src/synthtwin/taxonomy.py:2616-2617                   'all thirteen\n    printed'
  tests/test_p3v4f1_kept_values.py:57-58                'own\nthirteen'
  tests/test_p3v9f6_migration_names_every_option.py:481-482  'own\n    thirteen'
  tests/test_profile_version_5.py:23-24                 'own\n   thirteen'
  Those seven, and only those seven, are the witnesses. (SECURITY.md:304-305
  is the only one of the four witnesses the earlier draft named that is
  genuinely a wrap-crossing match: src/synthtwin/profile.py:233,
  CHANGELOG.md:366 and tests/test_p3v9f6_migration_names_every_option.py:49
  are each matched by P3 wholly within one line.)

WHICH LINE IS REPORTED — and how to implement it without contradicting the
manifest. The reported line is the line carrying the word `thirteen`. For six
of the seven wrap-crossing matches that is the SECOND line; for
src/synthtwin/taxonomy.py:2616-2617 it is the FIRST, because the match is
`all thirteen\n    printed` and `thirteen` sits on :2616.

  THE `rg` FORM BELOW IS A LOCATOR, NOT THE BATTERY. Run over the scope it
  emits FIFTY-TWO output lines, because `rg -U` prints every line a multi-line
  match touches: the forty-five matches plus the seven continuation lines
  above. Fifty outside section 12A. An implementation that compares those
  fifty lines against the forty-three-line manifest is red on the day it
  lands, which is the exact defect F15 raised. The battery must reduce each
  match to its `thirteen`-bearing line before comparing.

  rg -U -P -i -n --no-heading \
  '(?:thirteen[\s#*]+(?:published[\s#*]+|fixed[\s#*]+)?words|thirteen[\s#*]*-[\s#*]*member|own[\s#*]+thirteen|one[\s#*]+of[\s#*]+(?:the|these)[\s#*]+thirteen|outside[\s#*]+(?:the|those)[\s#*]+thirteen|member[\s#*]+of[\s#*]+the[\s#*]+thirteen|thirteen[\s#*]+are[\s#*]+not[\s#*]+spelled|all[\s#*]+thirteen[\s#*]+printed)' \
  $(git ls-files -- 'src/**' 'tests/**' README.md SECURITY.md STATUS.md \
    CLAUDE.md AGENTS.md CHANGELOG.md docs/spec/profile-contract-v6.md)

WHY THREE PATTERNS CARRY TAILS — each collision verified by running:
  P4 is `one of the/these thirteen` and not `of the thirteen`, because
     tests/test_twin_golden.py:873-874 reads "Each / of the thirteen is a line
     whose ..." and docs/spec/profile-contract-v6.md:911 reads "carry exactly
     twelve of the thirteen".
  P8 carries the tail `printed` because `all thirteen` alone also catches
     tests/test_generation_reference.py:1203 ("all thirteen were covered") and
     docs/spec/profile-contract-v6.md:151 ("which restates all thirteen").
  P7 carries the tail `not spelled` because `thirteen are` alone also catches
     tests/test_p3v4f1_kept_values.py:2265 ("THE OTHER THIRTEEN ARE ROUND
     7's"). The colliding form is `thirteen are`, NOT `the thirteen are`: the
     string `the thirteen are` occurs exactly once in the whole tree, at
     src/synthtwin/summary.py:845, which is the target.

THE OTHER TRUE THIRTEEN, which no search of this document may disturb: version
6 gives the ROLE vocabulary thirteen members —
  docs/spec/profile-contract-v6.md:204   "C6-1. The role vocabulary grows from
                                          ten members to THIRTEEN"
  docs/spec/profile-contract-v6.md:151   "C6-PUB, which restates all thirteen"
  docs/spec/profile-contract-v6.md:896   "restated over all thirteen roles"
  docs/spec/profile-contract-v6.md:911   "twelve of the thirteen"
  docs/spec/profile-contract-v6.md:1259  "total over the thirteen roles"
  docs/spec/profile-contract-v6.md:1608  "**Roles (13):**"
None of the eight patterns matches any of them today; verified by running.

  THE PATTERNS ARE NOT ROLE-SAFE, and this must be said rather than left to a
  reader to discover. P3, P4 and P6 key on `thirteen` plus a generic
  connective. A sentence such as "one of the thirteen roles" — a TRUE version
  6 statement — is matched by P4 and, under the hit-set rule below, turns the
  tree red for stating a fact version 6 requires. The tree is clean today only
  because :896, :911 and :1259 happen to be phrased otherwise. Either add a
  negative lookahead for `[\s#*]+roles?` to P3, P4 and P6, or record here that
  role sentences must avoid those three shapes.

THE EXPECTED-HIT MANIFEST — FORTY-THREE lines across SIXTEEN files, each
verified by reading the named line:

  CHANGELOG.md:366:  - **The settings block names which of synthtwin's own thirteen published
  CHANGELOG.md:444:    synthtwin's thirteen published words is recorded whatever the floor
  CHANGELOG.md:467:    thirteen words you named, it scopes its no-spelling-is-kept sentence
  README.md:217:  is one of synthtwin's own thirteen published words for "no value" -- the
  SECURITY.md:280:    which members of a thirteen-member list synthtwin publishes in its own
  SECURITY.md:287:    is told which of those thirteen fixed words were typed, and nothing
  SECURITY.md:297:    one of these thirteen". **The word guessed at THERE can never be a
  SECURITY.md:305:    thirteen is still recorded nowhere IN THE SETTINGS. Every publication
  SECURITY.md:326:    outside synthtwin's thirteen published words is written nowhere in the
  src/synthtwin/contract.py:2514:      synthtwin's own thirteen words, but naming it here would put the
  src/synthtwin/profile.py:151:  #    thirteen published words were typed -- and never the person's text
  src/synthtwin/profile.py:233:  # records also name WHICH MEMBERS of synthtwin's own thirteen published
  src/synthtwin/profile.py:239:  # is not stated: what is added is which members of a THIRTEEN-MEMBER
  src/synthtwin/profile.py:248:  # value was rescued") is made at thirteen words. The word guessed at
  src/synthtwin/profile.py:287:  # outside the thirteen was written anywhere at all. The one that
  src/synthtwin/summary.py:446:      of synthtwin's own thirteen published words is a spelling somebody
  src/synthtwin/summary.py:452:      keep a record of any word outside those thirteen, printed four
  src/synthtwin/summary.py:642:        which members of synthtwin's own thirteen published words were
  src/synthtwin/summary.py:698:      made that false of synthtwin's own thirteen words, since the
  src/synthtwin/summary.py:729:      exactly the reader who typed one of the thirteen. The opening now
  src/synthtwin/summary.py:802:  # The thirteen words of the published vocabulary, counted rather than
  src/synthtwin/summary.py:831:      of any word outside the thirteen, on the ground that synthtwin
  src/synthtwin/summary.py:845:      # THE THIRTEEN ARE NOT SPELLED OUT HERE, and that is deliberate.
  src/synthtwin/summary.py:852:          "    synthtwin has thirteen words of its own that it already",
  src/synthtwin/taxonomy.py:1212:      # names WHICH MEMBERS of synthtwin's own thirteen published words a
  src/synthtwin/taxonomy.py:2546:      THE WHOLE OF WHAT THIS MAY WRITE is a member of the thirteen the
  src/synthtwin/taxonomy.py:2611:      """Whether this spelling is one of synthtwin's own thirteen words.
  src/synthtwin/taxonomy.py:2616:      stand-in numbers `parsing.NUMERIC_SENTINELS` judges, all thirteen
  tests/test_claim_inventory.py:3882:  # they typed outside its own thirteen; `SECURITY.md` said such a value
  tests/test_claim_inventory.py:4949:              "A declared value that is not one of the thirteen is still "
  tests/test_p1r7f2_declaration_disclosure.py:296:      # typed one of the thirteen. What is pinned is that the claim keeps
  tests/test_p1r7f2_disclosure_is_true.py:28:    synthtwin's own thirteen published words were among the values typed
  tests/test_p1r7f2_disclosure_is_true.py:312:      # it says which of thirteen fixed words was typed, and nothing about
  tests/test_p1r7f2_disclosure_is_true.py:382:      # AND WHAT IS CARRIED IS ONE OF SYNTHTWIN'S OWN THIRTEEN, written in
  tests/test_p1r7f2_disclosure_is_true.py:500:      # recording which of synthtwin's own thirteen words were typed --
  tests/test_p3v4f1_kept_values.py:58:  thirteen published words a declaration named -- from the command line,
  tests/test_p3v4f1_kept_values.py:1261:      a word outside those thirteen is still written nowhere in the
  tests/test_p3v9f1_declared_words_disclosed.py:15:  typed outside its own thirteen. `SECURITY.md` and the governing
  tests/test_p3v9f3_escaping_is_display_only.py:41:  whether it is one of synthtwin's own thirteen words, and returned the
  tests/test_p3v9f4_declarations_not_keys.py:67:  # thirteen published words, and neither is produced by any builder.
  tests/test_p3v9f6_migration_names_every_option.py:49:    own thirteen, the column reads as numbers, and the description
  tests/test_p3v9f6_migration_names_every_option.py:482:      thirteen words, named as REAL DATA. Named, twelve of the column's
  tests/test_profile_version_5.py:24:     thirteen published words were typed, and never the person's text

  Per file: CHANGELOG.md 3; README.md 1; SECURITY.md 5;
  src/synthtwin/contract.py 1; src/synthtwin/profile.py 5;
  src/synthtwin/summary.py 9; src/synthtwin/taxonomy.py 4;
  tests/test_claim_inventory.py 2; tests/test_p1r7f2_declaration_disclosure.py 1;
  tests/test_p1r7f2_disclosure_is_true.py 4; tests/test_p3v4f1_kept_values.py 2;
  tests/test_p3v9f1_declared_words_disclosed.py 1;
  tests/test_p3v9f3_escaping_is_display_only.py 1;
  tests/test_p3v9f4_declarations_not_keys.py 1;
  tests/test_p3v9f6_migration_names_every_option.py 2;
  tests/test_profile_version_5.py 1.  Total 43.

TWO SECTION-12A LINES the search finds and the section exclusion removes:
  docs/spec/profile-contract-v6.md:1513  (matched by P2, `thirteen-member`)
  docs/spec/profile-contract-v6.md:1560  (matched by P1, `thirteen words`)

WHAT THE SEARCH DELIBERATELY DOES NOT FLAG — the complete complement, being all
twenty-two remaining lines in the scope carrying the word `thirteen`, each
verified by reading:
  CHANGELOG.md:311 (report lines); CHANGELOG.md:2172 (bound expectations);
  STATUS.md:62 (rounds of review); docs/spec/profile-contract-v6.md:151, 204,
  896, 911, 1259 (the ROLE vocabulary, true in version 6);
  docs/spec/profile-contract-v6.md:1522, 1530 (this clause describing itself);
  src/synthtwin/parsing.py:102 (characters); src/synthtwin/validation.py:6932
  (held lines); tests/test_generation_reference.py:872, 1202, 1203 (mutant
  cases); tests/test_p2c5f2_identifier_classes.py:74, 230 (out-of-range and
  too-large values); tests/test_p3v1f2_entry_table.py:78 (sites);
  tests/test_p3v4f1_kept_values.py:2265 (review-round items);
  tests/test_twin_golden.py:788, 870, 874 (report lines and moved checks).

THE PATTERN LIST IS NOT CLOSED OVER NATURAL PHRASINGS, and that is recorded
here rather than assumed away. Running it over docs/plans/phase-3-product.md
shows the gap concretely: :4327-4328 reads "the word is one / of thirteen this
package publishes" — a vocabulary-count statement in plain English that NO
pattern matches, because it says "one of thirteen" and P4 requires "one of the
thirteen" or "one of these thirteen". The eight patterns are a floor on what
the battery catches, not a ceiling on what exists.

THE BATTERY ASSERTS THE HIT SET, after reduction to `thirteen`-bearing lines.
Before the flip it equals the forty-three above; a hit not in it is a surface
written after this clause and is red at once. After the flip the set is EMPTY.

================================================================================
SPECIFICATION 2 — THE FORMAT SEARCH (`format` vocabulary, 6 -> 11)
================================================================================

NEW COUNT AUTHORITY:
  docs/spec/profile-contract-v6.md:426-427  "C6-21 (five new format members).
    The closed `format` vocabulary grows from six members to ELEVEN."
  docs/spec/profile-contract-v6.md:1620-1623  "**`format` (11):** `iso-date`,
    `iso-datetime`, `compact-date`, `month-first-date`, `day-first-date`,
    `year-quarter`, `slashed-iso-date`, `iso-month`, `iso-mixed`,
    `month-first-datetime`, `day-first-datetime`."
  docs/spec/profile-contract-v6.md:456-468   C6-D1's binding table, total over
    all eleven.
  Governing plan: docs/plans/phase-4-columns.md:1170-1173  "six members
    inherited and NINE after these additions **(AMENDED by A-P4-1: ELEVEN --
    the two slashed datetime members join by owner ruling)**".

WHERE IT LOOKS. The scope of Specification 1, MINUS
`docs/spec/profile-contract-v6.md` entire. The version 6 document's own format
tables are the NEW authority and are already correct; a search that flags them
demands an edit to the very text it is migrating toward. See the excluded-hit
list below, which names them so the exclusion is auditable.

THE COUNT HALF IS EMPTY IN SCOPE, and that is a finding rather than an
oversight. Run:

  rg -U -P -i -n --no-heading \
  '(?:six|6)[\s#*]+(?:date[\s#*]+)?(?:formats|format[\s#*]+members|parser[\s#*]+families|families|calendar[\s#*]+formats)' \
  $(git ls-files -- 'src/**' 'tests/**' README.md SECURITY.md STATUS.md \
    CLAUDE.md AGENTS.md CHANGELOG.md)

  Manifest: EMPTY (exit status 1). No live surface in scope states the format
  count in prose. The count is stated in prose only in excluded documents:
    docs/plans/phase-4-columns.md:1170 ("six members inherited")
    docs/plans/reviews/phase-4-plan-review-round-5.md:29 ("the six inherited
      datetime formats")
  docs/spec/profile-contract-v4.md:914-918 is an ENUMERATION of the six, not a
  statement of the count; the review record at :29 cites it as where the
  inherited six are enumerated. Do not list it as a place the count is stated.

  WHAT THE WIDENED PROBE ACTUALLY RETURNED, stated accurately because an audit
  trail that misreports its own output is worthless. Searching `\bsix\b` within
  100 characters of `format|calendar|parser` across the WHOLE tracked tree
  returns thirteen lines. Two of them are NOT excluded documents:
    tests/test_p2c5f2_identifier_classes.py:38 -- "the shipped parser and
      every one of the six exact counts asserted" (in scope; noise)
    docs/spec/generation-method-v1.md:2800 -- "parser's own answers tie those
      six to the published counts" (a governing spec; the six SHAPES of a
      wide cell, docs/spec/generation-method-v1.md:2795-2801; noise)
  Both are noise, so the conclusion stands; the earlier claim that the probe
  "returns only excluded documents" does not.

THE NOISE THIS SEARCH MUST NOT PRODUCE. In this repository "six forms" is the
NUMERIC-STYLE vocabulary of owner decision 10, not `format`:
    src/synthtwin/taxonomy.py:342-344  "HOW A NUMBER WAS WRITTEN, and nothing
      about what it is (owner decision 10). Six forms, and no seventh may be
      added by an implementation"
    src/synthtwin/parsing.py:575   "six forms of owner decision 10"
    src/synthtwin/parsing.py:596; src/synthtwin/taxonomy.py:3188;
    src/synthtwin/validation.py:6847, :6988;
    tests/test_p3v4f2_canonical_ceiling.py:40, :387;
    tests/test_p3v3f1_description_equivalence.py:621; CHANGELOG.md:1852.
  Exactly ten sites; a phrase list keying on "six" plus "forms" flags all ten
  true sentences.

THE ENUMERATION HALF IS THE SEARCH. Match a window of ten consecutive lines
holding four or more DISTINCT members of the old six, each matched standalone
(`(?<![\w-])member(?![\w-])`, so `iso-date` does not match inside
`iso-datetime`, and `month-first-date` does not match inside
`month-first-datetime`). The old six are `iso-date`, `iso-datetime`,
`compact-date`, `month-first-date`, `day-first-date`, `year-quarter`.

  THE THRESHOLD IS A CHOSEN HEURISTIC, not derived from the repository. It was
  tested against this tree only, and it is not hostile-tested: a paragraph
  naming four members in passing would be flagged.

MANIFEST — the closed enumerations, quoted:

  src/synthtwin/parsing.py:61-63   comment: "# The date and time formats, in
      the order they are tried. The first / # format that parses at least the
      required share of a column's values / # wins, and the profile records
      which one it was."
  src/synthtwin/parsing.py:64-71   DATE_FORMATS = ( "iso-date", "iso-datetime",
      "compact-date", "month-first-date", "day-first-date", "year-quarter", )
  src/synthtwin/parsing.py:73-80   _FORMAT_EXAMPLES = { six keys, one per
      member, with an example spelling each }
  src/synthtwin/contract.py:423-430  DATE_FORMATS = ( "iso-date",
      "iso-datetime", "compact-date", "month-first-date", "day-first-date",
      "year-quarter", )   -- a SECOND, independent tuple
  tests/test_parsing.py:84-93      the must-parse table, all six members
  tests/test_parsing.py:105-115    the must-not-parse table, five members
                                   (`day-first-date` absent)
  tests/test_taxonomy.py:145-152   the detection table, five members
                                   (`day-first-date` absent)

  EXCLUDED HITS, named so the exclusion is auditable rather than assumed. The
  window rule finds these two and the scope removes them; both are the CORRECT
  version 6 text and neither moves:
    docs/spec/profile-contract-v6.md:456-468   C6-D1's eleven-member binding
      table (six distinct old members inside one ten-line window)
    docs/spec/profile-contract-v6.md:1620-1623 the section 14 `format` (11)
      enumeration (six distinct old members inside one ten-line window)

  The per-member dispatch chains, which are total over the six today and gain
  a branch per new member (they enumerate but do not count):
  src/synthtwin/parsing.py:864, :876, :897, :904, :912, :919; :1299; :1326
    -- :1299 is `if format_name != "iso-datetime":` in `_clock_of`
    (src/synthtwin/parsing.py:1293-1300); it must gain `iso-mixed`,
    `month-first-datetime` and `day-first-datetime`, and was missing from the
    earlier draft of this list.
  src/synthtwin/taxonomy.py:3448, :3450, :3781
  src/synthtwin/contract.py:3707 (the `_one_of` gate for `format`),
    :3720, :3722 (D1)
  src/synthtwin/generation.py:4117-4123, the whole of `_parser_family`: the
    format members are at :4120 (`return "iso-date"`), :4122 (`return
    "year-quarter"`) and :4123 (`return "iso-datetime"`). :4119 and :4121 are
    `if resolution == "date":` and `if resolution == "quarter":` and carry no
    format member at all; the earlier draft cited those two lines and dropped
    the fall-through at :4123.
  tests/test_generation.py:724-730, the whole of `_format_for`, members at
    :727, :729, :730.

  Derived, and therefore moving on their own once the tuples move:
  src/synthtwin/taxonomy.py:625  NOTE_ARGUMENT_WORDS = parsing.DATE_FORMATS
    (with src/synthtwin/taxonomy.py:617-620 describing it as "the names of the
    date formats, each of which the profile already publishes under `format`")
  src/synthtwin/profile.py:841  ("columns", _EACH, "format"): parsing.DATE_FORMATS
  src/synthtwin/taxonomy.py:3354, :3383, :3385; src/synthtwin/generation.py:2351;
  src/synthtwin/reading.py:517; tests/test_generation.py:711, :1189
  Naming the tuple in prose without enumerating it, and therefore not moving:
  src/synthtwin/parsing.py:89, :851.

TWO FACTS THE ROW MUST RECORD:
  1. Nothing pins the tuple. `rg -P 'len\((?:parsing\.|contract\.)?DATE_FORMATS\)|DATE_FORMATS\s*==|set\(DATE_FORMATS'` over src/ and tests/ returns nothing.
     There is no test that the two `DATE_FORMATS` tuples AGREE -- unlike
     PROFILE_VERSION, whose two constants are held equal at
     tests/test_claim_inventory.py:3389. A half-applied format landing ships.
     The reference vectors carry single-member `format` values, not
     enumerations: tests/reference/generation-reference-vectors.json:37, :568,
     :2218, :2371 and tests/reference/generation-branch-vectors.json:189.
  2. Adjacent enumerations move in the same commit and have no row today:
     src/synthtwin/contract.py:432  RESOLUTIONS = ("date","datetime","quarter")
       -> four members, docs/spec/profile-contract-v6.md:1625
     src/synthtwin/contract.py:434  TIME_PRECISIONS = five members
       -> six members, docs/spec/profile-contract-v6.md:1627-1628
     src/synthtwin/taxonomy.py:452-455  the constants and the second
       RESOLUTIONS tuple built from them
     Their guards move with them: src/synthtwin/contract.py:3708-3710
       (`resolution`) and :3711-3713 (`time_precision`).

================================================================================
SPECIFICATION 3 — THE VERSION-INTEGER SEARCH (`profile_version`, 5 -> 6)
================================================================================

THE SEARCH ALREADY EXISTS IN THE TREE AND MUST BE CITED, NOT REINVENTED.
  tests/test_claim_inventory.py:3054      _NAMES_A_VERSION
  tests/test_claim_inventory.py:3228-3231 _A_VERSION_NOUN
  tests/test_claim_inventory.py:3237      _AMOUNTS_TO = r"(?:is|are)\b"; the
    reason `was`/`were` are absent is the comment at :3233-3236 -- "`was` and
    `were` are deliberately absent ... history is not what this ban is drawn
    around" -- which is a separate citation from :3237 itself.
  tests/test_claim_inventory.py:3240-3338 _predicative_version_claim()
  tests/test_claim_inventory.py:3341      _claims_in()
  tests/test_claim_inventory.py:3366-3395 _shipped_wire_version(), which reads
    profile.PROFILE_VERSION and asserts contract.PROFILE_VERSION equals it
  tests/test_claim_inventory.py:3014      VERSION_SURFACES = DEFENCE_SURFACES
  tests/test_claim_inventory.py:208-212   DEFENCE_SURFACES = SURFACES + three plans
  tests/test_claim_inventory.py:158-186   SURFACES (27 entries; 30 with the plans)
  tests/test_claim_inventory.py:3429-3457 the negative half of the ban
  tests/test_claim_inventory.py:3460-3489 the positive half, which at :3483
    computes  governing = f"docs/spec/profile-contract-v{shipped}.md"  and at
    :3484 asserts that document is among those making the claim.

PART A — THE SHIPPED INTEGER AND ITS GATE (all quoted):
  src/synthtwin/profile.py:167   PROFILE_VERSION = 5
  src/synthtwin/contract.py:109  PROFILE_VERSION = 5
  src/synthtwin/contract.py:38     "  5. read `profile_version`, which must be 5       R11, R12"
  src/synthtwin/contract.py:1435   '"""Check `profile_version` is exactly 5, before anything else (10.6).'
  src/synthtwin/profile.py:180   "# advances PROFILE_VERSION; versions 4 and 5 are both versions in which"
  Written into the document at src/synthtwin/profile.py:1365 and
  src/synthtwin/contract.py:4799; refused at src/synthtwin/contract.py:1487-1493.
  NOT a surface: src/synthtwin/errors.py:1358 and :1466 build R11/R12 from the
  two parameters (found, reads), so their wording moves with the constant.

PART B — TEST-SIDE ASSERTIONS OF THE INTEGER:
  tests/test_profile_version_5.py:660   assert profile.PROFILE_VERSION == 5
  tests/test_profile_version_5.py:661   assert contract.PROFILE_VERSION == 5
  tests/test_profile_version_5.py:662   assert declarations.document["profile_version"] == 5
  tests/test_profile_version_5.py:663   assert declarations.loaded.profile_version == 5
  tests/test_profile_version_4.py:356   assert profile.PROFILE_VERSION == 5
  tests/test_profile_version_4.py:357   assert document["profile_version"] == 5
  tests/test_generation_reference.py:269        "profile_version": 5,
  tests/test_failure_catalog.py:128     "profile_version_is_newer": (5, 4),
  tests/test_twin_golden.py:188         "# `profile_version: 5`, two counts on every column block and two"
  tests/test_profile_document.py:186    "# * `profile_version` reads 5;"
  tests/test_contract_loader.py:1022, 1033, 1041, 1081, 1083, 1090, 1091, 1092,
    1093, 1094, 1095, 1098  -- twelve hand-built JSON fixtures each carrying
    "profile_version": 5, which the loader must accept
  tests/test_profile_version_5.py:692   the R11 message text: "it says it is
    version 4, and this synthtwin reads version 5. A "
  tests/test_claim_inventory.py:3835    the same message quoted inside an
    ASSERTION MESSAGE STRING opened at :3832 -- not a comment.

PART C — NAMING AND REGISTRY SURFACES (the governing contract named by version).
Complete over `profile-contract-v5` in the scope: twenty references.
  src/synthtwin/contract.py:3      "The normative text is `docs/spec/profile-contract-v5.md`, which carries"
  src/synthtwin/profile.py:138     "# its name and its type. `docs/spec/profile-contract-v5.md` is the"
  src/synthtwin/errors.py:1230     "# against 5 (`docs/spec/profile-contract-v5.md` section 10), and carried"
  STATUS.md:241                    "- `docs/spec/profile-contract-v5.md` — what a description may contain"
  tests/dispositions.py:110        inside GOVERNING (tests/dispositions.py:100-113); v6 ABSENT
  tests/disposition_seal.py:2002   the per-passage seal for v5; no v6 key exists
                                   (the seal keys seven documents: :34, :208,
                                    :905, :1115, :2002, :2300, :2852)
  tests/test_claim_inventory.py:183   inside SURFACES (:158-186); v6 ABSENT
  tests/test_claim_inventory.py:4771  inside KEPT_BEARING (:4768-4775), where
    tests/test_claim_inventory.py:4765 calls it "the contract that governs the
    format"
  tests/test_claim_inventory.py:3357  LIVE CODE, missing from the earlier
    draft: `if asked == "A-P3-30" and relative.endswith("profile-contract-v5.md"):`
    inside `_surface_text` (:3349-3363) -- a reinstatement route keyed on the
    v5 filename.
  tests/test_claim_inventory.py:2979  prose naming v5 as the document that
    opened by denying its own version.
  tests/test_p2c4f1_disposition_registry.py:122, :125  CONTRACT5 binding
  tests/test_p2c4f1_disposition_registry.py:369  LIVE ASSERTION, missing from
    the earlier draft: v5 as an element of the asserted `specifications` list
    (:363-376).
  tests/test_p2c4f1_disposition_registry.py:359  the docstring naming v5's
    landing as the precedent.
  tests/test_p2c1f4_approximation_bounds.py:304 and tests/dispositions.py:786
    dispositions.contract5_delta(...), a function named for the version
  tests/test_profile_version_5.py:3, tests/test_contract_loader.py:3,
  tests/test_profile_version_4.py:10, tests/test_p3v9f6_migration_names_every_option.py:261
  CHANGELOG.md:341   "A-P3-28; the format is `docs/spec/profile-contract-v5.md`)."
  Already anticipating the flip, and quoted because it names the obligation:
  tests/test_p2c4f1_disposition_registry.py:370-374  "# The version 6 contract,
    DRAFT under adversarial review. Listed / # here so the tree stays green
    while the rounds run, on the / # precedent of the Phase 4 plan; it joins
    GOVERNING and the seal / # at its ratification."  ->  "profile-contract-v6.md",

PART D — WHAT THE SHIPPED BAN ITSELF REPORTS AT THE FLIP. Running
tests/test_claim_inventory.py's own _claims_in() over VERSION_SURFACES with the
shipped number taken as 6 yields exactly TEN stale claims, and every one is in a
document C6-MIG-B forbids editing (reproduced by execution):
  docs/spec/profile-contract-v5.md:5     'the loader reads version 5'
  docs/spec/profile-contract-v5.md:12    'loader did instead, and by forbidding anybody to write about version 5'
  docs/spec/profile-contract-v5.md:253   'version 5 producer writes'
  docs/spec/profile-contract-v5.md:1085  'this synthtwin reads version 5'
  docs/plans/phase-3-product.md:4443     'producer and the loader: the shipped producer now writes version 5'
  docs/plans/phase-3-product.md:4444     'shipped loader reads version 5'
  docs/plans/phase-3-product.md:4462     'producer writes version 5'
  docs/plans/phase-3-product.md:4466     'the producer writes version 5'
  docs/plans/phase-3-product.md:4556     'producer writes version 5'
  docs/plans/phase-3-product.md:4556     'the shipped loader reads version 5'
  The conflict, stated exactly: docs/spec/profile-contract-v5.md:3-7 opens
  "**Status: SHIPPED ...** `synthtwin profile` writes version 5, the loader
  reads version 5", and docs/spec/profile-contract-v6.md:176-180 says "The older
  documents are NEVER edited to change what version 6 requires." The migration
  row must say which of the two gives way, and how.
  The version 6 document already carries its own claims, so the positive half
  is satisfiable: docs/spec/profile-contract-v6.md:996 ('version 6 producer
  must be able to write') and :1289 ('this synthtwin reads version 6'), both
  confirmed by running _claims_in over it. Note that v6 is in NEITHER SURFACES
  nor VERSION_SURFACES today, so those two claims are not yet walked.

PART E — WHAT THE FLIP MUST ADD, derived rather than guessed:
  tests/dispositions.py:100-113   add "docs/spec/profile-contract-v6.md" to GOVERNING
  tests/disposition_seal.py       add its per-passage seal entry, which
    tests/test_p2c4f1_disposition_registry.py:333 forces by asserting
    set(disposition_seal.SEALED) == set(dispositions.GOVERNING)
  tests/test_p2c4f1_disposition_registry.py:118-131  add a CONTRACT6 path
    constant and a "docs/spec/profile-contract-v6.md" entry to RELATIVE, which
    tests/test_p2c4f1_disposition_registry.py:334 forces by asserting
    set(RELATIVE) == set(dispositions.GOVERNING). MISSING from the earlier
    draft; without it, adding v6 to GOVERNING is red at :334.
  tests/test_claim_inventory.py:158-186  add it to SURFACES, which
    test_every_governing_document_is_a_surface (:2584-2606) forces from
    dispositions.GOVERNING, and which :3483-3489 forces by computing
    f"docs/spec/profile-contract-v{shipped}.md"

================================================================================
EXCLUSIONS — BY NAME, WITH THE REASON, AND WITH THE COUNT EACH HOLDS
================================================================================

EXCLUDED, and the reason holds:
  docs/spec/profile-contract-v4.md -- holds ZERO vocabulary-count statements
    (verified by running the pattern list over it), and is out of scope by path.
  docs/spec/profile-contract-v5.md -- holds FIVE, all true of version 5:
    :838, :852, :875, :1139, :1244. Section 2.2.3
    (docs/spec/profile-contract-v6.md:176-180) forbids editing it.
  docs/plans/reviews/** -- round-by-round records of what was found when.
  Section 12A of this document, lines 1491-1569 -- it quotes the old count
    because the count is what it migrates. Two lines fall inside it: :1513
    and :1560.

EXCLUDED TODAY AND MUST NOT BE, because the governing plan says otherwise.
  docs/plans/phase-4-columns.md:1120-1124, which governs on every conflict:
    "every surface that states the vocabulary's size -- including the Phase 3
    plan's residual R-P3-8 entry, a sealed governing sentence that counts
    thirteen words -- moves by counted re-seal in the same landing, ENUMERATED
    IN THE CLAIM-MIGRATION TABLE."
  The word is "including". Running the pattern list over the excluded plan
  finds THIRTEEN vocabulary-count statements in docs/plans/phase-3-product.md,
  of which R-P3-8 is only the last:
    :2826, :4256, :4302, :4316, :4329, :4488, :4523, :4807, :4937, :4951,
    :5201, :5855, :7293
  (:4328 is NOT among them and must not be listed: docs/plans/phase-3-product.md:4327-4328
  reads "the word is one / of thirteen this package publishes", which no
  pattern matches, and :4329 is a separate `thirteen-member` hit. It is a real
  count statement the pattern list misses -- see the closure note in
  Specification 1 -- not a fourteenth hit.)
  A fourteenth surface, in the governing plan itself and omitted from the
  earlier draft's census: docs/plans/phase-4-columns.md:1122, "a sealed
  governing sentence that counts thirteen / words".
  R-P3-8 itself is docs/plans/phase-3-product.md:7293: "the PERSON'S OWN**,
  never one of this package's thirteen published / words."
  The migration row at docs/spec/profile-contract-v6.md:1560 names R-P3-8 in the
  singular. Transcribed as written, twelve further sealed governing sentences
  stay stale behind a green seal.

  THIS FINDING IS NOT YET CARRIED INTO SPECIFICATION 1 ABOVE, and the
  contradiction must be resolved before transcription. Specification 1's
  "WHERE IT LOOKS" admits no `docs/plans/` path and its forty-three-line
  manifest contains none, while the battery asserts that set exactly. Either
  widen Specification 1's scope to the named plan surfaces and extend the
  manifest by the fourteen lines above, or state in the row that the plan
  surfaces move by counted re-seal OUTSIDE the search and are enumerated here
  rather than found by it. Do not transcribe both halves as they stand.

CHANGELOG.md -- MUST BE INCLUDED, and the exclusion's own reason proves it.
  The exclusion (docs/spec/profile-contract-v6.md:1516-1517) reads
  "`CHANGELOG.md`, whose RELEASED entries describe the state at their own
  release." There are no released entries. The file carries exactly one `##`
  heading -- `## [Unreleased]` at CHANGELOG.md:7 -- above 2531 lines, and every
  one of the 45 entries beneath it is a `###` (the file's 47 heading lines are
  `# Changelog` at CHANGELOG.md:1, `## [Unreleased]` at :7, and 45 `###`).
  CHANGELOG.md:15 says so in the product's own words: "there is no tag and
  nothing is published."
  The three vocabulary-count lines all sit under
  CHANGELOG.md:314 "### Changed in Phase 3: the description format is version 5"
  (the next `###` is at CHANGELOG.md:485), and all three are present tense:
    CHANGELOG.md:366  "- **The settings block NAMES which of synthtwin's own thirteen published / words you typed** -- ten spellings it reads as "no value" and three / stand-in numbers."
    CHANGELOG.md:444  "one of / synthtwin's thirteen published words IS RECORDED whatever the floor / and the column class did with its cells."
    CHANGELOG.md:467  "it NOW SAYS which of synthtwin's own / thirteen words you named"
  The two CHANGELOG "thirteen"s that must NOT move are CHANGELOG.md:311
  (report lines) and CHANGELOG.md:2172 (bound expectations); the pattern list
  excludes both, verified by running.
  Also live in the same entry and belonging to the same row is the ARITHMETIC:
  CHANGELOG.md:367 "ten spellings it reads as "no value" and three" -- ten
  becomes eighteen under C6-31.

================================================================================
GAPS, CARRIED FORWARD AND EXTENDED
================================================================================
Every gap the derivation declared stands: the "ten spellings / three stand-in
numbers" arithmetic has no vetted manifest; no search was built for
`resolution` 3->4 or `time_precision` 5->6 prose; the format count half is
enumeration-only; the ten-line window threshold is a chosen heuristic; the
suite was not run; a golden-file pin of DATE_FORMATS would not appear in the
greps used; and rows :1559, :1563, :1564-1566 and :1568 were not searched.
Two further gaps found in verification:
- The eight-pattern list is demonstrably not closed over natural phrasings
  (docs/plans/phase-3-product.md:4327-4328). Its hit set is a floor.
- The patterns are not role-safe against version 6's thirteen-member role
  vocabulary (docs/spec/profile-contract-v6.md:204); P3, P4 and P6 would match
  plausible true sentences about roles.
# Phase 4 — the obligations landing, adversarial review round 2

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only, 2026-08-26.
**Target:** the round-1 repair, plus the note-grammar landing beside it.
**Verdict: REJECT**, seven blocking.

**TWO OF THESE ARE PRODUCT DEFECTS AND NOT PAPERWORK, and both were
confirmed by running the tool rather than by reading it.**

- **Item 8: a shipped sentence was FALSE.** A column of `1:2.0`,
  `1:2.5`, `1:3.0` declared with `--measurement` published "400
  value(s) are 2 WHOLE numbers written in one cell and joined by ':'".
  `splits_into_wholes` admits a decimal part -- that is what lets a
  ratio be read at all, and the changelog offers `1:1.5` as a feature
  -- so the sentence became false the day that feature landed and no
  guard compared the word with the rule. The producer now says
  "numbers"; NF47 carries the same correction.
- **Item 7: the contract stated TWO grammars at once.** The landing
  moved section 12's census and left 4.5.1's and 14.8's saying 44 forms
  and 65 positions, and left C6-119 admitting nineteen package words
  and two bound affix positions -- so a consumer written to it would
  refuse NF46, NF47 and NF48. **And 4.5.1's census contradicted ITSELF
  at HEAD**, saying 56 whole numbers in one sentence and 53 in the
  next; that predates this phase and no guard compared them. All four
  sites now state one grammar, once.

**The other five blocking items were guard weaknesses, all real, all
measured before repair and after:**

| item | what it was | after the repair |
|---|---|---|
| 1 | ordinary back-references (`it`, `this`, `the agreement`) and a bridging sentence defeated the carry | caught; the widening was measured against the whole tree and reports zero |
| 2 | the carried exemption was not directional | caught |
| 3 | a DIFFERENT regime cured the claim -- preserving privacy rules erased an exemption from data-use agreements | caught; the cure must now name the same regime or refer back |
| 4 | six ordinary wordings walked past, one of them a shape round 1 had added to the wrong side | all six caught |
| 6 | STATE cited an amendment that did not exist | A-P4-41 is written, and R-P4-23 closes BY RULING with the register saying so |

**Item 5 (serious) was a false positive the reviewer predicted before it
existed**: "this contract does not cover institutional requirements"
limits a document's reach and releases nobody. The `cover` and `reach`
shapes are withdrawn and the honest sentence now lives in a standing
list of prose the ban must NOT refuse.

**Item 9 (serious) closed a hole in the new grammar guard**: a clause
written "takes 1 argument" was not parsed, and a duplicate clause lost
silently to `setdefault`, so the guard could omit a form and report
green. Banners are now counted against parsed clauses and a duplicate
is a failure.

**Item 10** replaced a literal three-thousand floor with a check of
whether anything was SELECTED, which is what actually distinguishes a
whole run. **Item 11** is accepted as written: a placeholder test under
a banner would still pass, and the narrow condition holds today.

**Measured after the repair:** 16 of 16 attack sentences caught, 5 of 5
honest sentences clean, zero offenders on the whole governed tree.

**Round 3 is owed**, seven blocking items having moved.

---

## The review as written

I reproduced seven blocking failures. Several round-1 paths remain open, and the new grammar landing introduces contract contradictions.

## Items

1. **SEVERITY: blocking — ordinary back-references still defeat the carry.**

   **CONCRETE FAILURE SCENARIO:** Add “A privacy rule governs the source table. It does not apply to the synthetic twin.” The second statement uses the ordinary singular pronoun deliberately excluded from [_REFERS_BACK](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6444>), and the matcher returns no offender.

   It also misses “This does not apply,” “The agreement does not apply,” and “For synthetic twins, the rules do not apply.” A bridge defeats the next-statement limit: “Privacy rules govern source data. Synthetic output is treated differently. Those rules do not apply.”

2. **SEVERITY: blocking — directionality was not applied to carried exemptions.**

   **CONCRETE FAILURE SCENARIO:** Add “Privacy rules govern source tables. They still apply to the source, but do not apply to synthetic twins.” [_carried_exemption](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6477>) returns no claim whenever any cure marker appears, without comparing positions. The directional check later in `_grants_an_exemption` is never reached for this carried form.

3. **SEVERITY: blocking — a different regime still cures the banned claim.**

   **CONCRETE FAILURE SCENARIO:** Add “The twin is exempt from data-use agreements. Privacy rules still apply.” [_cured_after](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6501>) asks only whether the later sentence names some obligation. It does not retain the earlier regime. The matcher returns no offender, so preserving privacy rules erases a separate exemption from data-use agreements.

4. **SEVERITY: blocking — the expanded phrase inventory still misses ordinary prose, including one apparently added shape.**

   **CONCRETE FAILURE SCENARIO:** Each of these returned no offender:

   - “Approval is not required when the table is synthetic.”
   - “No ethics review is necessary for synthetic data.”
   - “Synthetic files are not governed by institutional policy.”
   - “Regulatory requirements do not extend to synthetic twins.”
   - “Using synthetic data obviates the need for ethics approval.”
   - “Synthetic output is beyond the review board’s jurisdiction.”

   In particular, [_OBLIGATION_NAMES](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6350>) recognizes “approval is not required,” but no exemption pattern recognizes that word order. The added shape is inert unless another exemption phrase stands nearby.

5. **SEVERITY: serious — the widened “does not cover” shape has a scoped false positive.**

   **CONCRETE FAILURE SCENARIO:** A contract introduction says “This contract does not cover institutional requirements; consult your institution.” That limits the contract’s scope; it does not release anyone from institutional requirements. The matcher reports it because the obligation name and the new marker co-occur.

   I scanned every current `DEFENCE_SURFACES` entry and found zero current offenders, including the honest earlier-approval sentence. The present tree is clean, but this natural scoped sentence cannot be added without a false red.

6. **SEVERITY: blocking — round-1 item 8 remains unresolved in the governing record.**

   **CONCRETE FAILURE SCENARIO:** [STATE](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/STATE.md:56>) cites A-P4-41 and says R-P4-23 closes by ruling. A-P4-41 does not exist elsewhere, `phase-4-columns.md` has no repair diff, and the [live residual](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/plans/phase-4-columns.md:5531>) still says the proper repair is a version bump, the choice belongs to the owner, and the residual is not closed.

   A maintainer following STATE again treats an unresolved choice as settled; an older version-6 description still receives the generic missing-key refusal recorded by the residual.

7. **SEVERITY: blocking — the new clauses were not propagated into the governing argument-class rules or the two main censuses.**

   **CONCRETE FAILURE SCENARIO:** An independent consumer implements [C6-119](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:1045>). It admits nineteen package words and permits bound affix strings only at the affixed remark’s two positions. It therefore refuses NF46’s clock words and NF47/NF48’s three new bound positions.

   The [4.5.1 census](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:1115>) still says 44 forms and 65 positions. The [14.8 heading](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:8357>) repeats 44 and 65, while section 12.2 says 48 and 79. The moved totals—48 forms, 79 positions, 66 whole numbers, 4 package words, 4 nested forms, and 5 bound strings—are arithmetically right; the contract states both grammars.

8. **SEVERITY: blocking — NF47 codifies a false rendering.**

   **CONCRETE FAILURE SCENARIO:** Profile a forced-measurement column of repeated `1:1.5` cells. [`splits_into_wholes`](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/taxonomy.py:5088>) accepts the decimal part explicitly, but [`EVIDENCE_JOINED`](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/src/synthtwin/taxonomy.py:1116>) renders “2 whole numbers.” [NF47](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/docs/spec/profile-contract-v6.md:1305>) repeats that claim. `1.5` is not whole, so the profile publishes plausible but false detection evidence while the arity-only guard remains green.

9. **SEVERITY: serious — the defining-clause parser can omit clauses while all new checks remain green.**

   **CONCRETE FAILURE SCENARIO:** Add a second exact-syntax clause defining `evidence_clock_times` with arity 4. [`_defining()`](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_p4d27_note_grammar_matches_the_code.py:90>) uses `setdefault`, so the earlier arity 3 silently wins. My in-memory mutation left the 48-entry dictionary unchanged.

   A new clause using “takes 1 argument” rather than “arity 1” is not matched at all and likewise leaves the dictionary unchanged. `_APPENDIX` also collapses duplicate names into a dictionary. The guard compares name-to-arity maps; it does not check clause completeness, unique numbering, renderings, argument classes, or totals.

10. **SEVERITY: minor — the freshness floor does not identify a whole-suite run.**

    **CONCRETE FAILURE SCENARIO:** Run a legitimate subset whose `session.testscollected` is 3,100 and which includes this module. Because 3,100 exceeds the [literal floor](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6719>), the check compares the subset with 3,907 and fails falsely. Conversely, if a future cleanup reduces the whole suite below 3,000, the check always skips.

    The current number itself is right: 3,851 passed plus 48 skipped was 3,899 collected; three new claim tests plus five grammar tests produce 3,907.

11. **SEVERITY: minor — the family repair proves a substring, not a functioning family test.**

    **CONCRETE FAILURE SCENARIO:** During a refactor, remove a family’s guard and behavioral tests but leave an unrelated placeholder test below its banner. The [raw search](</Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin/tests/test_claim_inventory.py:6686>) sees `def test_` and passes.

    The current five banner regions each contain at least one real test, so the narrow stated condition holds now.

## Checked

- Read both repository briefs, the complete diff from `792e380`, that commit, the round-1 record, STATE, the Phase 4 residual register, the contract, `taxonomy.py`, and both affected test modules.
- Executed the matcher directly from its parsed definitions, without pytest, against carry, cure, direction, natural-phrase, and scoped-positive probes.
- Confirmed STATE and STATUS are now governed surfaces; the corrected CLAUDE disclosure is consistent with the nothing-publishing roles; the commit count is 84; and `git diff --check` is clean.
- Counted 48 unique defining clauses and 48 appendix rows totaling 79 contract positions. Counted 21 package words and five bound positions in code. `NOTE_ARITY` has 47 forms and 72 positions because the five named exceptions account for four arity reductions and one absent form.
- Compared NF45, NF46, and NF48 order and rendering branches directly with the code; they agree. NF45 renders argument 5 before 4. NF47’s arity, order, and binding agree, but its whole-number meaning does not.
- Verified the family regions and suite-count arithmetic statically. Did not run pytest.
- Ran the value-silent scanner on the tracked tree; it returned clean.

Verdict: reject — blocking items are the carry/back-reference bypass, carried direction and wrong-regime cures, ordinary phrase misses, unresolved version ruling, contradictory grammar classes and censuses, and NF47’s false whole-number claim.
# classconflict

**VERDICT:** SOUND_WITH_CORRECTIONS

## Errors the verifier found (10)

1. FABRICATED LINE CITATION (derivation §3, step 2). The report cites `src/synthtwin/taxonomy.py:4816-4825` for the `_missing_maps` docstring ("THE ROLE IS NOT CONSULTED HERE"). That range does not exist: the file is 4635 lines (`wc -l src/synthtwin/taxonomy.py` = 4635). The docstring is at src/synthtwin/taxonomy.py:2816-2825 (`_missing_maps` is defined at src/synthtwin/taxonomy.py:2775). A 2000-line transposition — the exact class of defect this task exists to catch. Not in the transcribable, but it is an unverified element in the derivation that supports it.

2. MISATTRIBUTED AND MISAPPLIED RULE (in the transcribable, EDIT 2, and again in derivation §5 reason (e)). The draft says the change would be "a silent regression of exactly the kind the no-regression rule of P4-D3's header forbids", and §5(e) cites docs/plans/phase-4-columns.md:505-508 as "the plan's own no-regression rule for this phase". Two errors. (a) Wrong location: :505-508 is P4-D3 REFERRING to it — "Rules 8 through 10 sit AFTER categorical by design — the no-regression rule of the header" — and "the header" is the PLAN's header, docs/plans/phase-4-columns.md:52 ("**The one rule that shapes everything below — no regression by reclassification.**", running to :77). P4-D3's header is a section title and contains no rule. (b) Wrong rule: it is about role reclassification only. Its executable battery is a ROLE-equality battery — docs/plans/phase-4-columns.md:1422-1424, "every column's role under the Phase 4 tree equals its role under the shipped tree" — and acceptance criterion 4, docs/plans/phase-4-columns.md:2156, "no fixture column changes role". Moving `empty` into the nothing class changes NO column's role; it changes what the block publishes. The cited rule does not forbid it, so the amendment's central justification rests on a rule that does not reach the case.

3. UNSUPPORTED PROVENANCE CLAIM, CONTRADICTED BY THE ARTIFACT (in the transcribable, EDIT 2): "The 'every role in exactly one' clause entered this plan as the answer to P4-P1-F12". The closure row says the opposite — docs/plans/phase-4-columns.md:2243 records the repair as "the exact-one-class invariant kept", i.e. pre-existing and preserved — and the round-1 reviewer calls it pre-existing in as many words: docs/plans/reviews/phase-4-plan-review-round-1.md:106, "The implementer extends the existing exact-one-class guard." Nothing in any artifact shows the clause entering at F12; the plan's pre-ratification revisions are not in git (the whole plan lands in one commit, 5a5c3f8), so the claim is not checkable and must not be transcribed as fact.

4. DECISIVE ARTIFACT MISSED, and it inverts the provenance argument. docs/plans/reviews/phase-4-plan-review-round-1.md:108 states the invariant in its FOUR-bucket form, with the test citation, in the very item the plan's paragraph was repaired to answer: "The executable invariant requires every role to belong to exactly one of labels, ranges, nothing, or empty: `tests/test_column_analysis.py:573-583`." So the plan's author was handed the correct four-bucket form and the exact artifact that fixes it, and the repaired sentence at docs/plans/phase-4-columns.md:545 compressed it to three anyway. This is stronger and fully citable provenance than anything the report offers, and it belongs in A-P4-10 in place of the F12 claim above.

5. WRONG COUNT PROPOSED FOR TRANSCRIPTION (EDIT 3: "eight of the ten"). No artifact supports eight. Provenance lines, all read: A-P4-5 docs/plans/phase-4-columns.md:1887-1888 (contract v6 review rounds 1 to 3), A-P4-6 :1926-1927 (round 4), A-P4-7 :1974-1976 (round 4), A-P4-8 :2022-2023 (round 5) — four; A-P4-9 :2072-2088 is about the contract review's own round budget — five at most; A-P4-1 :1624 (owner ruling), A-P4-2 :1743-1744 and A-P4-3 :1771-1773 (stage-2 code review round 1), A-P4-4 :1835-1837 (owner ruling plus stage-2 code review). With A-P4-10 added the count is FIVE, or six counting A-P4-9 — never eight. The report flagged the base number as unreconciled and then shipped a mechanical +1 anyway; transcribing it writes a second wrong number into a governing document on top of the existing one at docs/plans/phase-4-columns.md:2106.

6. FABRICATED REVIEW-ITEM NUMBER IN THE TRANSCRIBABLE (EDIT 2 header): "(contract v6 review, item P4-X5-F18)". No such item exists. Round 5's items are P4-X5-F1 through P4-X5-F10 — docs/plans/reviews/phase-4-contract-v6-review-round-5.md:66-75 — and the plan records the five rounds as 17, 13, 10, 13, 10 items (docs/plans/phase-4-columns.md:2091). The report declared this gap honestly, but the invented number is still sitting inside the block marked for transcription and must be removed, not carried.

7. MISDATED COUNT (in the transcribable, EDIT 1): "the twelve non-`empty` roles are each in exactly one of the three, which is how the shipped battery has written the invariant since Phase 1". The shipped battery covers TEN roles, nine of them non-`empty`: `ROLES` at src/synthtwin/taxonomy.py:234-245 has ten members; the tuples at :258-264 name three each; the fixture set at tests/test_column_analysis.py:511-522 has ten entries. Twelve is the POST-Phase-4 count, and it comes from the contract, not the tree — docs/spec/profile-contract-v6.md:911, "The three value-publishing classes carry exactly twelve of the thirteen roles". As written the clause attaches a Phase-1 provenance to a count that has never existed in the shipped tree. Only the four-bucket SHAPE dates to Phase 1 (verified: `git log -S "role == taxonomy.ROLE_EMPTY" -- tests/test_column_analysis.py` returns only dd9402f, "Phase 1 redesign").

8. MINOR — incomplete citation (derivation §1): "`empty` appears in P4-D3 only as rule 0 of the rule order (docs/plans/phase-4-columns.md:488-491)". It also appears at docs/plans/phase-4-columns.md:521, "winning right after the empty rule settles". The substantive point (nowhere in P4-D3 is `empty` connected to publication classes) survives.

9. MINOR — off-by-one in a precedent citation (derivation §5): the in-place marker cited as docs/plans/phase-4-columns.md:1171-1172 actually spans :1171-1173 ("**(AMENDED by / A-P4-1: ELEVEN — the two slashed datetime members join by owner / ruling)**"). The other precedent, :413-415, is exact.

10. COMPLETENESS GAP NOT DECLARED: the review record is governing prose and still carries the three-bucket reading. docs/plans/phase-4-columns.md:13-14 says "The closure tables sit in the review record at the end, which governs", and the closure row at :2243 reads "the exact-one-class invariant kept". EDIT 1 amends :545 but leaves the governing record asserting the invariant under its old name with no pointer to A-P4-10. The amendment should name that row so the governing surface is not left standing against it.

## GAPS declared

- Review item number P4-X5-F18: I could not place it. docs/plans/reviews/phase-4-contract-v6-review-round-5.md:66-75 records that round's items as P4-X5-F1 through P4-X5-F10 only, docs/plans/phase-4-columns.md:2091 states the five contract rounds returned 17, 13, 10, 13, 10 items, and no round-6 file exists in docs/plans/reviews/ (only rounds 1-5 for phase-4-contract-v6). My A-P4-10 draft therefore cites '(contract v6 review, item P4-X5-F18)' WITHOUT a round number, unlike A-P4-5 through A-P4-8, which all name theirs. Fill in the round before transcribing.
- The 'seven of the nine amendments ... came out of contract review' claim at docs/plans/phase-4-columns.md:2106 does not reconcile with the amendments' own provenance lines (I count four cited to contract v6 review, five if A-P4-9 is included). I did not resolve which count the plan intends; EDIT 3 renumbers it mechanically and is flagged in the transcribable as needing the owner to settle the base number.
- I did not verify the arithmetic of C6-PUB-A's own worked example beyond its internal consistency. Its 'eleven cells that all hold one built-in absent word' publishing 'the count 11' is consistent with small_cell_floor 11 (src/synthtwin/taxonomy.py:2857-2861), but I ran the shipped producer only on the test suite's own empty fixture (['', 'NA'] * 20), not on an eleven-cell single-word column.
- I did not check whether the version 6 contract needs any further edit BEYOND the optional EDIT 4 to stay consistent once the plan is amended. I read section 6A whole (docs/spec/profile-contract-v6.md:896-960), C6-37/38/39/40 (:829-873) and the disposition rows (:1377-1382), but did not read the version 6 document end to end, so another clause elsewhere in it may restate the three-class partition without the carve-out.
- I did not establish whether the plan's own governing-surface machinery needs a companion entry: docs/plans/phase-4-columns.md:15-19 says the plan joins 'the disposition seal, the GOVERNING set, and the claim-inventory surface list' and that its prose is walked by claim-inventory guard families. Whether an amended sentence requires a re-seal or a claim-inventory re-walk is not something I could determine from the plan text alone.
- I grepped the other governing surfaces for a restatement of the three-class partition and found none — docs/spec/generation-method-v1.md has no hit; docs/spec/validation-method-v1.md:296, :351, :353, :777, :841 and SECURITY.md:346-348 all use the binary 'publishes no value of the table' framing with the same three roles and no mention of empty — but this was a keyword grep on 'publication class' / 'publishing class', not a full read of those documents, so a paraphrase using different words could have escaped it.
- src/synthtwin/taxonomy.py:247-248 carries the same three-class compression the plan does ('THE THREE PUBLICATION CLASSES. A role belongs to exactly one') over a ROLES of ten and tuples covering nine. I report it but propose no code change: whether a comment fix lands, and at which stage, is outside a contract review and outside this read-only task.

## CORRECTED MATERIAL

VERDICT ON THE DERIVATION ITSELF: the judgment is right and the decisive artifact is real. I re-verified, independently, every load-bearing fact:

- src/synthtwin/taxonomy.py:258-264 — ROLES_PUBLISHING_LABELS = (constant, binary, categorical); ROLES_PUBLISHING_RANGES = (count, continuous, datetime); ROLES_PUBLISHING_NOTHING = (numeric_unrepresentable, identifier, free_text). Three each, nine of the ten in ROLES (src/synthtwin/taxonomy.py:234-245). `empty` in none.
- src/synthtwin/contract.py:265-269 ships ROLES_PUBLISHING_NOTHING alone; a repo-wide grep finds no other definition of the LABELS or RANGES tuples.
- tests/test_column_analysis.py:573-583 — four buckets, the fourth `role == taxonomy.ROLE_EMPTY`; fixture set at :511-522 includes `empty`. Added in Phase 1 (git: dd9402f).
- v4 §6.10 (docs/spec/profile-contract-v4.md:1304-1312) states only the nothing-publishing membership; N3 (:1874) and V2 (:1877) are binary; the matrix note (:1316-1317) explains the blank `empty` column. No three-class partition anywhere in v4, v5, generation-method-v1, validation-method-v1 or SECURITY.md (grepped).
- v5 C5-N3 (:468-478), the closed term at :214, C5-N6 (:511-514), C5-21 (:915-921), rows :1005 and :1008 — all binary, all quoted correctly.
- Shipped run, executed read-only against src/ with default small_cell_floor 11: undeclared ["","NA"]*20 -> role empty, missing_by_source {'NA': 20}, n_missing_blank 20, n_missing_withheld 0, n_missing 40 (20+20+0 == 40, C5-N3 closes). Declared -> role empty, structural identifier, {} / 0 / 0. publishes_no_values('empty', False) is False, ('empty', True) is True.
- I ALSO CLOSED THEIR DECLARED GAP 3: eleven cells of 'NA' at floor 11 profile as role empty with missing_by_source {'NA': 11}, n_missing_blank 0, n_missing_withheld 0. C6-PUB-A's worked example (docs/spec/profile-contract-v6.md:931-933) is arithmetically correct, and 'NA' is a built-in TEXT word, so C6-37's judged-pass exception (docs/spec/profile-contract-v6.md:837-839) does not withhold it — the twin does reproduce all eleven.
- I ALSO CLOSED THEIR DECLARED GAP 4 as far as keyword sweeps can: no other v6 clause restates a three-class partition over all roles. §13.2 (docs/spec/profile-contract-v6.md:1577-1580) says `affixed_number` gets a named exception "rather than a fourth publication class ... everywhere the three are enforced" — that is the three VALUE-PUBLISHING classes and is consistent with C6-PUB's fourth, explicitly-labelled no-class row at :909.
- generation.py:8122 writes every absent cell empty and `missing_by_source` appears nowhere in generation.py — their correction about present-tense twin behavior is right.

So: amend the PLAN, not the contract. But the material below must replace what they proposed. Four things in their transcribable are not in any artifact.

================================================================
EDIT 1 — in-place marker in the plan.
File: docs/plans/phase-4-columns.md, line 545.

OLD (one line, exact — verified):
Publication classes — every role in exactly one, the invariant kept:

NEW (replaces that one line; wrap matches the surrounding paragraph):
Publication classes — every role in exactly one, the invariant kept
**(AMENDED by A-P4-10: exactly one of FOUR buckets — the three
value-publishing classes, plus `empty`, which is in none of them. The
four-bucket shape is how the shipped battery has written this
invariant since Phase 1; after the three roles this phase adds, the
three value-publishing classes carry the twelve non-`empty` roles,
each in exactly one)**:

Lines 546-557 are unchanged.
[Changed from their draft: their version said "the twelve non-`empty`
roles ... is how the shipped battery has written the invariant since
Phase 1". The battery covers ten roles, nine non-`empty`
(src/synthtwin/taxonomy.py:234-245, :258-264; tests/test_column_analysis.py:511-522).
Twelve is the post-Phase-4 count from the contract
(docs/spec/profile-contract-v6.md:911), not from the tree. Only the
SHAPE dates to Phase 1.]

================================================================
EDIT 2 — new amendment section.
File: docs/plans/phase-4-columns.md, inserted after Amendment A-P4-9
(which begins at :2072) and immediately before `## Acceptance criteria`
(:2125).

## Amendment A-P4-10 — the exactly-one invariant counts `empty` as its own bucket

**THIS CORRECTS a sentence of this plan that was never true of the
shipped code, and lowers no obligation** (contract v6 review, round and
item number TO BE FILLED IN AT TRANSCRIPTION — no item numbered
P4-X5-F18 exists; round 5's items are P4-X5-F1 to P4-X5-F10, at
`docs/plans/reviews/phase-4-contract-v6-review-round-5.md:66-75`).
P4-D3's publication-class paragraph opens "Publication classes — every
role in exactly one, the invariant kept". Read over the three
value-publishing classes that sentence is false, and has been false
since Phase 1 shipped: `ROLES_PUBLISHING_LABELS`,
`ROLES_PUBLISHING_RANGES` and `ROLES_PUBLISHING_NOTHING`
(`src/synthtwin/taxonomy.py:258-264`) name three roles each — nine of
the ten in `ROLES` (`src/synthtwin/taxonomy.py:234-245`) — and `empty`
is deliberately in none of them.

**The invariant, as the code has always written it.** The shipped
battery states it over FOUR buckets, not three:
`test_every_role_belongs_to_exactly_one_publication_class`
(`tests/test_column_analysis.py:573-583`) tests membership in the
three tuples AND `role == taxonomy.ROLE_EMPTY`, and asserts exactly
one of the four is true, over a fixture set that includes `empty`
(`tests/test_column_analysis.py:511-522`). That is the invariant. This
plan compressed it to three and dropped the bucket that has no value
to publish.

**And the four-bucket form was put in front of this plan in writing.**
Round 1 of the plan review raised P4-P1-F12 — `affixed_number` had no
single publication-class membership — and its evidence line states the
invariant correctly, with the artifact that fixes it:
"The executable invariant requires every role to belong to exactly one
of labels, ranges, nothing, or empty: `tests/test_column_analysis.py:573-583`"
(`docs/plans/reviews/phase-4-plan-review-round-1.md:108`). The same item
calls the guard pre-existing — "the implementer extends the existing
exact-one-class guard" (`:106`) — and the closure row records the repair
as keeping it (`docs/plans/phase-4-columns.md:2243`). The repaired
sentence dropped the fourth bucket anyway. F12 was a ruling about
`affixed_number`; it was never a ruling about `empty`, and this
amendment restores the form the reviewer supplied.

**Nor does the contract this plan governs state a three-class
partition.** Version 4 section 6.10
(`docs/spec/profile-contract-v4.md:1304-1312`) names the
nothing-publishing membership and nothing else — three roles plus any
column whose `structural_role` is `identifier` — and version 5's C5-N3
(`docs/spec/profile-contract-v5.md:468-478`) is binary on exactly that
term, over the closed definition at
`docs/spec/profile-contract-v5.md:214`, which does not contain `empty`.

**Why the plan moves and not the contract.** Putting `empty` into the
nothing class would change what a shipped run writes.
`publishes_no_values("empty", False)` is False
(`src/synthtwin/taxonomy.py:4333-4357`), so
`_publication_class_applied` returns the maps untouched
(`src/synthtwin/taxonomy.py:4423-4424`) and an UNDECLARED all-absent
column publishes its hole spellings under the floor
(`src/synthtwin/taxonomy.py:2857-2866`): forty cells alternating a
blank and `NA`, at `small_cell_floor: 11`, yield
`missing_by_source: {"NA": 20}`, `n_missing_blank: 20` and
`n_missing_withheld: 0`. Moving `empty` into the nothing class would
force that map empty and both counts to zero, break C5-N3's closing
sum for the column (20 + 20 + 0 == 40 becomes 0 + 0 + 0 != 40), and —
after the C6-37 flip this phase lands — write twenty blank fields
where the twin should write `NA`. Deliverable 4 of this plan is that
the twin "reproduces the recorded hole spellings the description
already publishes" (`docs/plans/phase-4-columns.md:86-89`); this change
would delete the record on every `empty` column instead, pushing a
fact the description holds today into the permanently-open route
P4-D6.1 names — "a person's own word on a nothing-publishing column"
(`docs/plans/phase-4-columns.md:1094-1098`, carried as C6-41 at
`docs/spec/profile-contract-v6.md:879-885`) — with no rule saying it
moved. Bought for one word in a plan sentence.
[Changed from their draft, which grounded this on "the no-regression
rule of P4-D3's header". That rule lives in the PLAN's header
(`docs/plans/phase-4-columns.md:52-77`), P4-D3 only refers to it at
:505, and it governs ROLE reclassification only — its battery asserts
"every column's role under the Phase 4 tree equals its role under the
shipped tree" (:1422-1424) and acceptance criterion 4 says "no fixture
column changes role" (:2156). This change moves no role, so that rule
does not reach it.]

**The structural override is where the exactly-one question actually
bites, and it does not move.** A column whose `structural_role` is
`identifier` is nothing-publishing whatever its role
(`src/synthtwin/taxonomy.py:4357`,
`src/synthtwin/contract.py:2727-2736`,
`src/synthtwin/validation.py:1789-1802`), so a DECLARED all-absent
column carries `role: empty` with an empty source map and both counts
zero, while the undeclared one publishes. Those two columns differ,
they are meant to, and neither reading changes here.

**Cost.** One clause in P4-D3 and this section. No rule, no key, no
role, no byte moves, and no stage gains work. The plan now carries ten
amendments rather than nine; the closure row at
`docs/plans/phase-4-columns.md:2243`, which is governing prose under
this plan's own :13-14, keeps its wording and is read through this
amendment: "the exact-one-class invariant" there means the four-bucket
invariant stated above.

**What it buys.** The plan stops requiring of the version 6 contract a
membership the shipped tuples refuse, so the contract can state the
`empty` carve-out plainly — which is what C6-PUB-A already does —
instead of standing red against its own governing plan on a fact
neither document intends to change.

================================================================
EDIT 3 — companion count, same file. DO NOT TRANSCRIBE THE ORIGINAL
DRAFT OF THIS EDIT.
File: docs/plans/phase-4-columns.md, line 2106.

OLD (one line, exact — verified):
this plan — seven of the nine amendments this plan now carries came

Their draft's NEW was "eight of the ten". Eight is supported by
nothing. Verified provenance, every line read: A-P4-5 (:1887-1888),
A-P4-6 (:1926-1927), A-P4-7 (:1974-1976), A-P4-8 (:2022-2023) cite
contract v6 review — FOUR. A-P4-9 (:2072-2088) is about the contract
review's own round budget — FIVE at most. A-P4-1 (:1624) cites an
owner ruling; A-P4-2 (:1743-1744) and A-P4-3 (:1771-1773) cite stage-2
code review round 1; A-P4-4 (:1835-1837) cites both. Adding A-P4-10
gives FIVE, or six counting A-P4-9. The existing "seven" is itself a
pre-existing defect of this plan. "three of them touching one key"
checks out under either count — A-P4-5, A-P4-6 and A-P4-8 all touch the
pooled fraction census.

Two options; the owner picks, and neither may be applied blind:

  (3a) Correct base and total together —
       NEW: this plan — five of the ten amendments this plan now carries came
       (or "six" if A-P4-9 is intended to count; the sentence then also
       needs A-P4-9's own status named, since it cites no review item).

  (3b) Move only the total, leaving the disputed base for a separate
       amendment —
       NEW: this plan — seven of the ten amendments this plan now carries came
       This propagates a wrong base and is only defensible if 3a is
       raised as its own item in the same commit.

The total "nine" -> "ten" is correct regardless.

================================================================
EDIT 4 (SECONDARY, non-blocking, contract-side accuracy only).
File: docs/spec/profile-contract-v6.md, lines 923-926 inside C6-PUB-A.
OLD text verified exact at :923-926. Their NEW text is verified
correct in every element and stands as drafted:

OLD (exact):
conclusion broke a shipped fact: the three publication tuples in
`src/synthtwin/taxonomy.py` and `src/synthtwin/contract.py` list
exactly `numeric_unrepresentable`, `identifier` and `free_text`, and
`empty` is deliberately absent from all three.

NEW:
conclusion broke a shipped fact: the three publication tuples in
`src/synthtwin/taxonomy.py` — `ROLES_PUBLISHING_LABELS`,
`ROLES_PUBLISHING_RANGES`, `ROLES_PUBLISHING_NOTHING` — name three
roles each, nine of the ten in `ROLES`, and `empty` is deliberately
absent from all three; `src/synthtwin/contract.py` ships the nothing
tuple alone, listing exactly `numeric_unrepresentable`, `identifier`
and `free_text`. The shipped battery writes the exactly-one invariant
over FOUR buckets accordingly — the three tuples and `empty` — in
`test_every_role_belongs_to_exactly_one_publication_class`.

Basis, all re-verified: all three tuples at src/synthtwin/taxonomy.py:258-264;
src/synthtwin/contract.py defines only ROLES_PUBLISHING_NOTHING, at
:265-269 (repo-wide grep confirms no second definition of the other
two); the four-bucket test at tests/test_column_analysis.py:573-583.

================================================================
GAPS THAT REMAIN OPEN AFTER MY PASS — stated so nobody fills them from
pattern:

1. The contract-review round and item number for A-P4-10's provenance
   line. P4-X5-F18 does not exist. I could not locate any round-6
   review file (docs/plans/reviews/ holds phase-4-contract-v6 rounds
   1-5 only). Whoever is running the current round must supply it.
2. Which base number line 2106 intends. Four, five and seven are each
   reachable by a different reading of "came out of contract review";
   none of them is eight. Not resolvable from the plan text.
3. Whether an amended sentence needs a re-seal or a claim-inventory
   re-walk (plan :15-19). I read tests/test_claim_inventory.py — it
   lists docs/plans/phase-4-columns.md as a walked surface (:211) but
   pins no publication-class sentence I could find by keyword. I did
   not read that 6000-line file end to end, so I cannot rule out a
   guard that this edit trips.
4. My sweep for a restated three-class partition was keyword-based
   ("publication class", "publishing class", "exactly one",
   "value-publishing", "three classes", "thirteen roles", "`empty`")
   across profile-contract-v4/v5/v6, generation-method-v1,
   validation-method-v1, SECURITY.md and the plan. A paraphrase in
   different words could have escaped it.
5. src/synthtwin/taxonomy.py:247-249 carries the same three-class
   compression ("THE THREE PUBLICATION CLASSES. A role belongs to
   exactly one") over a `ROLES` of ten and tuples covering nine. The
   test twelve lines below it is the precise statement. I propose no
   code change; it belongs to stage 6, not to a contract review.
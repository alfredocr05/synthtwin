# datetime

**VERDICT:** SOUND_WITH_CORRECTIONS

## Errors the verifier found (12)

1. FABRICATED IDENTIFIER (the failure mode itself). The proposed transcription cites `P4-X5-F17` three times as a normative source ("round 5, P4-X5-F17"; "the four keys P4-X5-F17 names"; "the defect round 5 found at P4-X5-F17"). No such finding exists. Round 5 has exactly TEN items, P4-X5-F1 through P4-X5-F10: docs/plans/reviews/phase-4-contract-v6-review-round-5.md:7 ("Ten items, all ten blocking") and the disposition table at docs/plans/reviews/phase-4-contract-v6-review-round-5.md:66-75. A repo-wide grep for `P4-X5-F1[1-9]` returns nothing, and the only P4-X5 identifiers the contract itself cites are F1 (v6:388), F2 (v6:615), F5 (v6:787), F6/F7 (v6:1041) and F9 (v6:1456). The nearest real precedent for "§12 priced only part of a mechanism" is P4-X5-F9 (review-round-5.md:74), which is what added row 12's second bullet.

2. RULE-ORDER CLAIM IS BACKWARDS. Proposed row 5's closing sentence reads "For a column that was `constant`, `binary` or `categorical` under version 5 rather than free text — reachable, because `datetime` is tested before `categorical` in C6-1's order — the same thirteen are new". C6-1's order is `empty`; declared `identifier`; `numeric_unrepresentable`; `constant`; `binary`; `datetime`; `count` or `continuous`; `categorical` (docs/spec/profile-contract-v6.md:206-209). `constant` and `binary` are tested BEFORE `datetime`, so the widened datetime rule can never take a column either of them claims; C6-1 itself says "a column any earlier rule claims under version 5 is claimed by the same rule under version 6" (v6:210-212), and C6-34 says it in words: "a constant or binary column keeps its claim" (v6:699-700). The cited justification supports only `categorical`. In the other direction the sentence is also short: `count` and `continuous` are tested AFTER `datetime` (v6:208) and so are reachable prior roles by the same argument the sentence uses for `categorical`. Same error in the report's prose at "Reverse direction, for completeness".

3. ROW 15 OMITS `long_tail_labels`, AND THE COMPLETENESS AMENDMENT MAKES THE OMISSION NORMATIVE. Row 15 is scoped to "the ranges-class source accounting" over `datetime`, `time_of_day` and `affixed_number`. But `long_tail_labels` is a LABELS-class role (C6-18, v6:359-360; C6-PUB, v6:906) whose columns were `free_text` under version 5 (C6-15, v6:340-344; order, v6:208-209), so it makes exactly the same nothing-class-to-publishing-class crossing and newly publishes exactly the same four absent-cell facts. §12 row 1 prices only its floor-cleared LEVEL spellings (v6:1392-1395); nothing prices its `missing_by_source` spellings and counts, `n_missing_blank`, `n_missing_withheld`, or its named sentinel candidates. With the amendment asserting completeness over §3 through 7B, §3.4 introduces a fact no row prices, so the amended claim would be false on its own terms.

4. ROW 15 DROPS C6-37'S NAMED EXCEPTION, on precisely the case the row is about. Row 15 states flatly "under C6-37 the twin writes those spellings at their published counts". C6-37 writes each `missing_by_source` spelling at its published count "EXCEPT a spelling a JUDGED PASS put there — one reading as a stand-in number, or as a CALENDAR PLACEHOLDER — which stays blank" (v6:837-839), with C6-38 giving the reason (v6:846-857); §11's own row reads "EXACT-OBSERVABLE, per-spelling recount, stand-in-spelled keys excepted" (v6:1379). Row 15's fourth bullet is about calendar placeholders, so the exception is not a corner case here — it is the case. The report's §3 table carries the same unqualified sentence.

5. ROW 16 MISCOUNTS WHICH PARSE COUNTS NO KEY CARRIES. It says "two of them — the only-day-first and only-month-first counts — are carried by no key of any block". Three of the four are carried by no key. The total for the reading USED is recoverable from the block: `n_unparsed` is "present cells that did not read as a date under the chosen format" (v4:926), so that total is `n_present − n_unparsed`, which RM2 also fixes (v6:1252). The other reading's total, *X* and *Y* are carried by no key at all; of those three, two are independent and the third follows from the both-readings identity *D* − *X* = *M* − *Y* (v6:1095).

6. ROW 17 CALLS `(date-sentinel)` "THE SIXTH" KEY. In C6-N3's own enumeration the six are `(blank)`, `(date-sentinel)`, `(declared-missing)`, `(numeric-sentinel)`, `(text-code)`, `(withheld)` (v6:678-680), repeated in the same order at §14 (v6:1632-1634). `(date-sentinel)` is listed SECOND; the sixth is `(withheld)`. An ordinal that disagrees with the enumeration it points at is the same class of defect this review exists to catch — name the key.

7. ROW 16 OMITS THE FORM'S TRIGGER, so the row overstates the disclosure. The slashed-date form is "carried whenever the option was given and a slashed reading was in play" (v6:1112-1114), i.e. only where `--day-first`/`day_first` was set (C6-20, v6:375-376; §8, v6:1186). A §12 row that does not say when the fact appears cannot be read as a price. The report's own declared gap — whether the form can attach to a column that was read both ways and then DECLINED to datetime — is genuine (neither v6:1112-1114 nor DF-R at v6:1226 settles it) and should be carried into the row as a stated open question rather than dropped from the transcription.

8. THE AMENDMENT WIDENS THE COMPLETENESS SCOPE TO §7B BUT ACCOUNTS FOR ONLY TWO OF §7B's THREE NEW FORMS. C6-GRAMMAR says "Three sentences of the profile document are new" (v6:998) and none of the three appears in the shipped `NOTE_ARITY` table (src/synthtwin/taxonomy.py:572-611), confirming all three are additions. Form 1 is argued to carry nothing new because the affix pair is already in the block (C6-ARG, v6:1158-1161). Form 3 gets the drafted row 16. Form 2, `remark_a_declaration_would_restore_the_distribution`, is carried by a DECLINED column (v6:1011-1014) — a nothing-publishing `free_text` column — and its second argument is "how many cells the floor-clearing non-numeric spellings cover" (v6:1026), a count of the table carried by no key of a `free_text` block (its added keys are `length`, `words`, `n_all_digits`, `n_code_alphabet`, `n_distinct_by_occurrences`, v4:1271-1275). The plan asserts the remark is "built from counts the remark already carries plus the floor" (docs/plans/phase-4-columns.md:1708-1710) and the plan governs, so this may resolve to "publishes nothing new" — but the transcription must SAY which, because extending the scope to §7B brings the form into it.

9. ROW 15's C6-41 SENTENCE CONTRADICTS THE REPORT'S OWN HANDLING AND IS SELF-DEFEATING AS WRITTEN. The report says of the C6-41 observation "I flag it rather than fold it in", then folds it into row 15's closing sentence. As drafted it is also incoherent: C6-41's second route is "a word of the person's own on a column whose publication class permits no value of the table" (v6:882-883); a column that has crossed out of `free_text` is no longer such a column, so "a person's own marker word on such a column is now recorded" describes a column the route no longer reaches. Either drop the sentence or state it as the separate observation the report itself judged it to be.

10. ROW 5's HEADING OVER-CLAIMS RELATIVE TO ITS BODY. "Every fact a datetime block publishes" is followed by only the thirteen role-added keys; the twenty-two universal keys of the block (v4:483-502 plus v5:450-451) are priced — partly — at row 15. In an inventory whose whole job is a completeness claim, a heading broader than its body invites a reader to believe the universal keys are covered here.

11. ROW 5's FIRST BULLET HEADER SAYS "floor-free" AND THEN NAMES A FLOOR-GOVERNED MEMBER. The bullet is headed "VALUES of real cells, floor-free under the ranges-class endpoint policy" and includes the keys of `utc_offsets`, which the same bullet then says are floor-governed by D3 (v4:981-983). Split the floor-free endpoints from the floor-governed offset map.

12. CITATION SLIPS (each individually minor; all would be transcribed). (a) `contract.py:343-356` for DATETIME_KEYS — the twelve entries are src/synthtwin/contract.py:345-356, the tuple src/synthtwin/contract.py:344-357. (b) `parsing.py:63-70` — the six members are src/synthtwin/parsing.py:65-70, the tuple 64-71. (c) plan P4-D7 item 7 is docs/plans/phase-4-columns.md:1216-1237, not 1216-1236 (line 1237 completes the sentence). (d) "grepping v5 ... returns only two lines" — the grep returns three: docs/spec/profile-contract-v5.md:1032, :1389, :1390. (e) `v4:1319-1337` glossed as "matrix rows `format` … `utc_offsets`" — those twelve rows are v4:1326-1337; v4:1321-1325 are the label-key rows. (f) `v6:982-983` cited for `fraction_widths` on three roles — those lines name only `count` and `continuous`; `affixed_number` comes from v6:988 and C6-27 at v6:516.

## GAPS declared

- Whether the slashed-date remark attaches ONLY to datetime columns. C6-GRAMMAR says it is "carried whenever the option was given and a slashed reading was in play" (v6:1112-1114) and DF-R says "the column carries the slashed-date remark form" (v6:1226), but neither says whether a column that was read both ways and then DECLINED to datetime still carries it. If it can attach to a declined column, row 16's four counts reach columns outside the datetime block entirely, and I could not settle that from the contract or the plan.
- The JSON type of `time_of_day`'s `clock_percentiles` is stated two ways and I could not resolve which governs. §8 says "array of 11 strings" (v6:1178); C6-11 says "an eleven-rung ladder of clock values in the ladder's fixed rung order" (v6:316); version 4 §5.6 says a ladder is an OBJECT with exactly eleven named keys but names only two fields as carrying one, `percentiles` and `date_percentiles` (v4:668-673), so §5.6 does not cover the new key. T2/T3 use "first rung"/"last rung"/"non-decreasing" language (v6:1239-1240), which fits either. This is not my review item but it affects how row 4 of §12 should describe the fact.
- No clause I could find states the disposition of `n_distinct` and `n_distinct_folded` on the three NEW roles. Version 4 §9.2 explicitly defers them to the per-role-group sections 9.3-9.7 (v4:2045-2046), version 6 §11 is delta-only and adds no row for them (v6:1372-1386), and §8's key table does not list them because they are not new keys (v6:1166-1187). So a `time_of_day`, `affixed_number` or `long_tail_labels` block has two universal keys with no disposition, against §11's own completeness assertion at v6:1384-1386. Flagged rather than filled.
- Invariant D6 is not named as superseded in 2.2.2A (v6:144-171) and its text (v4:1012-1015) is total over version 4's five `time_precision` members but says nothing about the new member `month` that C6-24 adds (v6:486-489). I could not find any clause binding `time_precision: month` to `resolution: month`, so on my reading a document pairing `resolution: datetime` with `time_precision: month` is refused by no stated rule. Adjacent to my item, not part of it, and I did not chase it.
- Whether `subsecond_digits` can be nonzero on any of the five new format members. C6-10 says fractional seconds do not parse for the clock forms (v6:307), and the two slashed-datetime members are date + space + a clock of C6-10 (v6:435-436), so they cannot carry one; `iso-mixed` includes `iso-datetime` and shipped `parsing.py` reads a fractional part there, so it can. I state this as a reading of the cited grammars, not as a rule either document writes down.
- I did not verify the five new format members against a shipped parser, because none exists yet: `parsing.py:63-70` still holds the six version-4/5 members and `contract.py:422-434` still holds six formats, three resolutions and five precisions. Every version-6 claim above rests on the contract text alone. The shipped code DID confirm the version-4 datetime key set (contract.py:343-356, taxonomy.py:3459-3477) and the twenty-two universal keys (contract.py:212-233), key for key.
- I could not establish whether a `datetime` block can in practice carry a NUMERIC sentinel candidate (as opposed to a calendar-placeholder one). Row 15's fourth bullet says "the stand-in number as text, or a calendar placeholder's ISO day spelling" because C6-CAND permits both (v6:412-420); whether the numeric half is reachable on a column of dates is a producer question the contract does not answer and I did not trace through taxonomy.py to settle it. If it is unreachable, that bullet should name the placeholder spelling alone.

## CORRECTED MATERIAL

CORRECTED TRANSCRIBABLE MATERIAL

Every element below is quoted from a file with its file:line. Repo-relative paths;
v4/v5/v6 = docs/spec/profile-contract-v{4,5,6}.md.

WHAT SURVIVED VERIFICATION UNCHANGED (so the transcriber knows what not to re-derive)

- The key set: 35 = 22 universal + 12 + 1. The twelve are v4:916-927 verbatim; the
  twenty universal are v4:483-502 plus version 5's two at v5:450-451; the one added is
  `resolution_mix` (C6-25, v6:491-501; §7A, v6:981-982). Version 5 adds no datetime key
  (its whole added-key table is v5:975-980). Shipped code agrees key-for-key:
  contract.py:211-234 (twenty-two) and contract.py:344-357 (twelve), and taxonomy.py:3459-3478
  emits exactly those twelve.
- Every disposition cited resolves: v4:2038-2043 (universal), v4:2090-2097 (datetime),
  v6:1379-1381 (§11 delta), v6:1183 (`resolution_mix` REPORT-ONLY), v6:1184 (`(date-sentinel)`).
- Vocabularies: `format` 11 (v6:1620-1623), `resolution` 4 (v6:1625), `time_precision` 6
  (v6:1627-1628), absence classes 6 (v6:1632-1634). C6-D1's bindings at v6:456-468.
- The gap arithmetic: 13 role keys − 3 priced by row 5 − 1 priced by row 8 = NINE unpriced.
- `affixed_number` 44 keys, of which rows 2/3/4/7 price 21 and `n_rows` is priced nowhere;
  `time_of_day` 27 keys, all five priced by rows 4 and 13. Both confirmed.
- The declared gaps about `clock_percentiles`' type (v6:1178 "array of 11 strings" vs
  C6-11 v6:316 and v4:668-673, which names only `percentiles` and `date_percentiles`),
  about D6 (v4:1012-1015) saying nothing about the new `month` precision (C6-24, v6:486-489)
  while 2.2.2A does not supersede D6 (v6:144-171), and about `n_distinct`/`n_distinct_folded`
  having no disposition on the three new roles (v4:2045-2046 defers to §§9.3-9.7;
  v6:1372-1386 adds no row) are all real and correctly evidenced. Keep them as declared gaps.

ONE DECLARED GAP CAN BE CLOSED. "Whether a `datetime` block can carry a NUMERIC sentinel
candidate": yes. The numeric-sentinel pass is gated only on the numeric-looking population
clearing the parse line (taxonomy.py:4518-4528, with `_numeric_looking` at taxonomy.py:2383-2387)
and runs BEFORE the role is decided (taxonomy.py:4580-4581). A `compact-date` column is
all-digit and clears that gate, so floor-clearing cells spelling a stand-in inside the
parse-line slack publish a numeric candidate on a block that then takes `datetime`.
Row 15's fourth bullet naming both kinds is therefore correct as written.

---

REPLACEMENT FOR ROW 5 (currently v6:1411-1415)

 5. **Every ROLE-ADDED fact a datetime block publishes, on every column
    the five new calendar members and the unpadded widening newly
    claim.** The universal keys such a column newly fills are priced at
    row 15, not here. The role-added key set is version 4's TWELVE
    datetime keys (version 4 §6.6.2, the added-keys table) plus version
    6's `resolution_mix` (C6-25); version 5 adds none. A `free_text`
    block carries not one of the thirteen — version 4's §6.11 matrix
    leaves every datetime row blank in the `free_text` column, and §7A
    restates that as "every key not listed for a role is FORBIDDEN on
    that role" — so every one of them is new for such a column. Priced
    by what each carries:
    - **VALUES of real cells, floor-free under the ratified ranges-class
      endpoint policy:** `earliest` and `latest`, the two end instants;
      `date_percentiles`, whose `min` and `max` ARE those two texts by
      D11 and whose nine interior rungs are interpolated; and
      `earliest_utc_offset` and `latest_utc_offset`, each the offset
      text that endpoint's own cell carried.
    - **One VALUE map that is floor-GOVERNED rather than floor-free:**
      the KEYS of `utc_offsets`, each an offset spelling written as the
      source wrote it, under D3's floor with a `(withheld)` pool.
    - D9 flattens both endpoint offset fields and every key of
      `utc_offsets` to `(none)` or `(withheld)` unless `resolution` is
      `datetime`, so of the five new members only `iso-mixed`,
      `month-first-datetime` and `day-first-datetime` may carry an
      offset at all (C6-D1).
    - **SHAPE facts, carrying no cell but fixing how every cell of the
      column was written, floor-free:** `format`, the parser family that
      read the REAL file, REPORT-ONLY because the twin is written in ISO
      syntax; `resolution`, the canonical form the published datetimes
      are written in; `time_precision`, the FINEST precision any cell
      writes; `subsecond_digits`, the most fractional-second digits any
      cell writes; `datetimes_read_at`, which clock the endpoints and
      the ladder are on — and therefore, by D5, whether the column mixed
      offsets at all; and the KEYS of `resolution_mix`, whose counts row
      8 prices.
    - **COUNTS of the table, floor-free:** `n_unparsed`, the present
      cells that did not read as a date under the chosen format — the
      datetime sibling of the time-of-day count row 13 prices; and the
      VALUES of `utc_offsets`, how many rows carried each named offset.
    Revision 4 priced this row as "endpoints and rungs" alone, which
    named three of the thirteen. A privacy reviewer reading it learned
    nothing about the nine shape and count facts, and nothing about the
    block-class move row 15 now prices.
    **A column newly claimed here need not have been free text.**
    `datetime` is tested BEFORE `count`/`continuous` and before
    `categorical` in C6-1's order, so a column either of those rules
    claimed under version 5 can be taken by the widened datetime rule
    under version 6 — a column of `YYYY-MM` month values sitting under
    the categorical ceiling is the clean case — and such a block gains
    the same thirteen while it STOPS publishing that column's label
    spellings. A column that was `constant` or `binary` under version 5
    is NOT reachable: both rules are tested BEFORE `datetime`, C6-1
    keeps an earlier rule's claim, and C6-34 says it in its own words —
    "a constant or binary column keeps its claim".

Citations, in order:
- twelve datetime keys, each key's type, permitted values and meaning: `v4:916-927`
- `resolution_mix` on every datetime block: `v6:491-501` (C6-25), `v6:981-982` (§7A)
- version 5 adds no datetime key: `v5:975-980` (its whole added-key table)
- forbidden on `free_text`: `v4:1319-1320` (the matrix's header and its `free_text`
  column) with rows `v4:1326-1337`; restated `v6:975-984` (§7A)
- `earliest`, `latest`: `v4:921-922`; EXACT-OBSERVABLE `v4:2090`
- `date_percentiles`: `v4:925`; eleven named rungs `v4:668-673`; D11 `v4:1085-1086`;
  ends EXACT-OBSERVABLE `v4:2091`, interior APPROXIMATED `v4:2092`
- `earliest_utc_offset`, `latest_utc_offset`: `v4:923-924`; the offset forms `v4:964-972`
- `utc_offsets`: `v4:927`; floor rule D3 `v4:981-983`
- D9: `v4:1029-1033`; resolution bindings of the five new members `v6:430-436` (C6-21)
  and `v6:456-468` (C6-D1)
- `format` REPORT-ONLY: `v4:916`, `v4:1113-1119`, `v4:2095`
- `resolution`: `v4:917`; four members `v6:1625`
- `time_precision`: `v4:918`; six members `v6:1627-1628`
- `subsecond_digits`: `v4:919`
- `datetimes_read_at`: `v4:920`; D5, "a published fact, not one a consumer may
  re-derive" `v4:993-1010`
- the four EXACT-OBSERVABLE-outside-the-corner shape facts: `v4:2093-2094`
- `n_unparsed`: `v4:926`; EXACT-OBSERVABLE `v4:2096`; row 13's time-of-day-only
  wording `v6:1472-1476`
- `resolution_mix` REPORT-ONLY and floor-free: `v6:500-501`, `v6:1183`
- the rule order, and that an earlier rule's claim survives: `v6:206-212` (C6-1)
- constant and binary keep their claim: `v6:699-700` (C6-34)

---

NEW ROW 15

15. **The BLOCK-CLASS source accounting, reaching columns that published
    none.** `free_text` is a NOTHING-class role; `datetime`,
    `time_of_day` and `affixed_number` are RANGES-class roles and
    `long_tail_labels` is a LABELS-class role (C6-PUB). On the nothing
    class `missing_by_source` is empty, both absence counts are zero,
    and every sentinel candidate reads `(withheld)`. On the other
    classes none of that holds. So every column crossing out of free
    text into one of the FOUR — by the five new calendar members, by the
    unpadded widening, by the clock rule, by the affix rule, or by the
    long-tail rule — newly publishes FOUR kinds of fact about its ABSENT
    cells that version 5 withheld from it absolutely:
    - the EXACT absent-value SPELLINGS its cells wore, every key of
      `missing_by_source` being text of the table with no first-party
      meaning (C5-N5), floor-governed by C5-N4;
    - each spelling's ROW COUNT, at or above `small_cell_floor`;
    - `n_missing_blank` and `n_missing_withheld`, two counts of the
      table that read zero on every nothing-class column;
    - the NAME of each sentinel candidate — the stand-in number as text,
      or a calendar placeholder's ISO day spelling under C6-CAND — where
      version 5 published only `(withheld)`.
    And `missing_by_source` is EXACT-OBSERVABLE in version 6, not
    REPORT-ONLY (§11), so under C6-37 the twin WRITES those spellings at
    their published counts — with C6-37's own named exception: a
    spelling a JUDGED PASS put there, one reading as a stand-in number
    or as a calendar placeholder, stays blank in the twin (C6-38), and
    §11's row carries the same exception in its own words.
    This is the same class of fact row 12's second bullet already prices
    for the error-literal mechanism; it is priced here for the five
    mechanisms row 12 does not reach. Row 1 prices a long-tail column's
    floor-cleared LEVEL spellings and not this, which is why
    `long_tail_labels` is named here as well.

Citations:
- publication classes over thirteen roles: `v6:904-916` (C6-PUB); ranges row `v6:907`,
  labels row `v6:906`, nothing row `v6:908`; nothing-class sentence `v6:913-916`
- `affixed_number` ranges: `v6:289-295` (C6-9); `time_of_day` ranges: `v6:336` (C6-14);
  `long_tail_labels` labels: `v6:359-360` (C6-18)
- the three new roles are tested after `categorical`, so their columns were free text:
  `v6:206-212` (C6-1); `long_tail_labels` is for a column past the categorical ceiling
  `v6:340-344` (C6-15)
- version 4's statement of the nothing class: `v4:616-620` (N3), `v4:649-653` (V2),
  `v4:1304-1312` (§6.10)
- version 5's statement, with the two absence counts: `v5:915-923` (C5-21),
  `v5:468-489` (C5-N3, C5-N4)
- keys are table text, no reserved key: `v5:491-495` (C5-N5)
- `n_missing_blank`, `n_missing_withheld` definitions: `v5:450-451`
- `candidate` domain widened: `v6:412-420` (C6-CAND), `v6:703-707` (C6-35)
- disposition move to EXACT-OBSERVABLE, stand-in-spelled keys excepted: `v6:1379`
- the twin writes the spellings, and the judged-pass exception: `v6:837-839` (C6-37),
  `v6:846-857` (C6-38)
- row 12's second bullet, the mechanism already priced: `v6:1455-1466`
- row 1, which prices long-tail level spellings and not this: `v6:1392-1395`

[Separate flagged observation, NOT folded into row 15 and not proposed for
transcription: C6-41 (v6:879-885) calls its two routes unchanged and unclosable.
The ROUTE is unchanged, but the SET of columns on which the second route bites
shrank, since a column crossing out of `free_text` leaves the class the route
quantifies over. Whether that makes C6-41's last clause require a qualifier is a
question for the contract's author; it is adjacent to this item, not part of it.]

---

NEW ROW 16

16. **The slashed-reading parse counts, carried in a sentence.** Where
    the `day_first` option was given and a slashed reading was in play,
    the column carries the
    `remark_slashed_dates_read_against_your_declaration` form, whose
    arity is five: cells the day-first reading parsed (*D*), cells the
    month-first reading parsed (*M*), cells only day-first parsed (*X*),
    cells only month-first parsed (*Y*), and the reading used. Four of
    the five are COUNTS OF THE TABLE. The total for the reading USED is
    already a block fact — it is `n_present` less `n_unparsed`. The
    other THREE are carried by no key of any block; two of them are
    independent and the third follows from the both-readings identity
    *D* − *X* = *M* − *Y*. The sentence is where they are published.
    Each is bounded by the named column's `n_present`, and the
    contradiction clause fires only where both *X* and *Y* are nonzero.
    No value of the table enters: C6-ARG's four argument classes admit a
    whole number, one of this package's own words, a nested form, and a
    bound affix string, and this form uses only the first two.
    **Open, and stated rather than assumed:** neither C6-GRAMMAR nor
    DF-R says whether a column read both ways that then DECLINES to
    `datetime` still carries the form. If it can, these counts reach a
    column with no `n_unparsed` key at all, and all four are carried by
    no key.

Citations:
- the form, its arity and its five arguments: `v6:1027`
- the three first-clause renderings and the contradiction clause: `v6:1054-1075`
- the four argument-consistency checks, including the both-readings identity and the
  `n_present` bound: `v6:1090-1104`
- `n_unparsed`'s meaning, which is what makes the used reading's total a block fact:
  `v4:926`; and `v6:1252` (RM2)
- the argument classes closed at four: `v6:1127-1130`; no source-derived string but the
  bound affix pair: `v6:1153-1162`
- the trigger: `v6:1112-1114`; the `day_first` setting `v6:375-376` (C6-20), `v6:1186` (§8)
- DF-R, the producer obligation that the column carries the form: `v6:1226`
- the open question: `v6:1112-1114` and `v6:1226` between them do not settle it

---

NEW ROW 17

17. **The `(date-sentinel)` absence-class count.** `missing_by_class`
    carries SIX keys in version 6, always all six, on every column block
    of every role. The one version 6 adds is `(date-sentinel)` — second
    in C6-N3's own listing — and it counts the cells a calendar
    placeholder pass read as absent: a count of the table,
    floor-governed like every other non-`(withheld)` class, REPORT-ONLY.
    It is nonzero only where the placeholder pass entered, which C6-34
    confines to a column whose non-candidate remainder clears the
    datetime rule's parse line. Row 14 prices the placeholder VERDICTS;
    this row prices the CLASS COUNT beside them, which is a different
    key.

Citations:
- six keys, always all six, summing to `n_missing`, each non-`(withheld)` value 0 or
  at least the floor: `v6:676-681` (C6-N3)
- the six spellings enumerated in the same order: `v6:1632-1634` (§14)
- `(date-sentinel)` REPORT-ONLY: `v6:1184` (§8)
- when the pass enters: `v6:691-701` (C6-34)
- row 14, which prices the verdicts and not this key: `v6:1477-1483`

---

AMENDMENT TO THE COMPLETENESS SENTENCE (currently v6:1485-1489)

Each row is named in `SECURITY.md` and in the profiler's own summary,
where a person meets it. **The inventory is complete over sections 3,
4, 5, 6, 6A, 7A and 7B** — enumerated rather than given as a range,
because this document's section numbers are not monotonic — : every
fact those sections introduce is either in a row above or publishes
nothing of the table, and a fact added to this document without a row
here is red against the delta battery. The scope reaches 7B rather than
stopping at 6 because C6-GRAMMAR introduces three new sentence forms,
one of which carries counts of the table published by no key (row 16),
and a completeness claim that stops short of the facts it must cover is
what this revision is repairing. Of the other two forms, the affixed
remark carries no spelling the block does not already hold (C6-ARG),
and the recoverable-distribution remark's second argument is carried by
the ratified plan's own ruling that the remark is built from counts it
already carries plus the floor — recorded here so a reader can check it
rather than infer it.

Citations: current wording scoped to "sections 3 through 6" `v6:1486-1487`; the three
new forms `v6:998` and `v6:1025-1027`, none of which appears in the shipped
`NOTE_ARITY` table at `src/synthtwin/taxonomy.py:572-611`; the affixed form carries
nothing new `v6:1158-1161`; the recoverable-distribution form is carried by a declined
column `v6:1011-1014` with its second argument at `v6:1026`, and the plan's ruling that
it is "built from counts the remark already carries plus the floor" at
`docs/plans/phase-4-columns.md:1708-1710`.

---

PLAN CHECK (the plan governs on conflict, `v6:106-108`)

P4-D7 item 7 requires the delta section to state "in one place everything version 6
publishes that version 5 withheld, each row priced" — `docs/plans/phase-4-columns.md:1216-1237`
— and requires that "Each row names its floor treatment or its justification, its
SECURITY.md sentence and its summary sentence" (`:1235-1237`), which the rows above meet
for floor treatment and which the existing blanket sentence at `v6:1485` carries for the
other two. The 2026-08-19 amendment adds two rows, for the widened slashed families and
for `built_in_dates` — `docs/plans/phase-4-columns.md:1712-1720`. The plan's own
illustrative list also stops at "endpoints and rungs" (`:1226-1231`), so the rows above
are additions the plan's "everything" clause requires rather than deviations from a plan
enumeration; no plan sentence is contradicted. Note also that §12 row 3's phrase
"`numeric_styles` with its fraction widths" (`v6:1403`) matches the plan's own wording
"the styles block with its fraction widths" (`:1223`), so it is not a defect against the
plan even though C6-27 fixes `fraction_widths` as a SIBLING (`v6:515-526`); it needs no
change here.

CITATION CORRECTIONS to carry into any prose that survives from the report:
contract.py DATETIME_KEYS entries are `src/synthtwin/contract.py:345-356` (tuple 344-357);
the six shipped format members are `src/synthtwin/parsing.py:65-70` (tuple 64-71);
`fraction_widths` on three roles is `v6:988` and `v6:516`, not `v6:982-983`, which names
only `count` and `continuous`; and every reference to `P4-X5-F17` must be struck — round
5's items are P4-X5-F1 through F10 only
(`docs/plans/reviews/phase-4-contract-v6-review-round-5.md:7`, `:66-75`). Where a
precedent citation is wanted for "§12 priced only part of a mechanism", the real one is
P4-X5-F9 (`docs/plans/reviews/phase-4-contract-v6-review-round-5.md:74`), which is what
put the second bullet into row 12.
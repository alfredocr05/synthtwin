VERDICT SOUND_WITH_CORRECTIONS errors=7

## ERRORS

1. BANNED IDENTIFIER FORM — `C6-FKM` is a `C6-` LETTER identifier. Section text, 6.6.1, last paragraph of the level_ceiling discussion: "under the rule that every key not listed for a role is FORBIDDEN on that role (C6-FKM)". The task forbids `C6-` letter identifiers outright; the bare identifier the checkable list itself uses is `FKM` (docs/spec/profile-contract-v6.md:1247 — `| FKM | v4 6.11 | every key not listed for a role is forbidden on it |`). The `C6-` prefix at docs/spec/profile-contract-v6.md:968 exists only to name what it superseded. FIXED: `(FKM)`, with the rule still stated in words in the same sentence so the identifier is a pointer and not a substitute.

2. DF-R'S TRIGGER IS LOOSER THAN THE SOURCE. Section text: "A column read under the option carries the slashed-date remark form of section 4.5 — exactly once —". The sources both condition on a SLASHED reading being in play, not merely on the option being given: docs/spec/v6-build/s45.md:601-602 ("Carried whenever `day_first` was given and a slashed reading was in play, exactly once per such column"), docs/spec/profile-contract-v6.md:1112-1114 ("carried whenever the option was given and a slashed reading was in play"), and docs/plans/phase-4-columns.md:897-899 ("every slashed column read under the option carries exactly one remark"). As written, the transcription attaches the remark to every column of a table profiled with `--day-first`. FIXED to "Where the option was given and a column's slashed reading was in play, that column carries…".

3. C6-34'S ADDED REASON MISQUOTES THE PLAN. Section text: "This ordering is tighter than the affixed rule's, because a removal here could otherwise demote a column that publishes today." The plan's words are "Ordering, tighter than the affix pass because a removal here could otherwise demote an existing datetime column" (docs/plans/phase-4-columns.md:1694-1696). The clause is absent from C6-34 in the contract (docs/spec/profile-contract-v6.md:691-701), so the plan is the only source and it names the specific risk — an existing DATETIME column — which "a column that publishes today" blurs into every publishing role. FIXED to the plan's wording.

4. INVENTED CLAIM, NO SOURCE. Section text, closing the date-beside-datetime reason: "Every other pair the table refuses is refused on the same footing." Version 4's reason (docs/spec/profile-contract-v4.md:1017-1027) argues the one named pair and stops; no clause of the plan or of version 6 generalizes it to the other twenty-two refused pairs. The D6 paragraph already carries the totality claim it needs ("all twenty-four pairs are decided"). FIXED by deleting the sentence.

5. DELTA FRAMING SURVIVED (three sites). (a) "the profile's own canonical serialization is unchanged" is version 4's amendment framing at docs/spec/profile-contract-v4.md:1111-1112 ("The amendment is scoped to twin CSV cells; the profile's own canonical serialization is unchanged") — in a self-contained document "unchanged" names a prior version. FIXED to "…is scoped to twin CSV cells and does not touch the profile's own canonical serialization." (b) "Checking the shape alone has a cost the rule that did it did not see" still carries version 4's revision history (docs/spec/profile-contract-v4.md:954-956, "Earlier revisions checked the shape alone… That reasoning had a cost the revision did not see"). FIXED to a counterfactual that keeps the whole reason and names no revision. (c) "Absent the declaration nothing changes" (docs/plans/phase-4-columns.md:1676-1678, "Ambiguity handling is untouched") reads against a prior baseline; FIXED to "Absent the declaration the ordinary reading stands". A fourth, milder site — "The widened readings of this version" — is FIXED to "The widened readings above".

6. D9'S REASON CREDITS THE SHIPPED READER WITH A READING IT DOES NOT HAVE. Section text: "A whole date, a month and a quarter carry no clock, the shipped reader reads none of them with an offset". Version 4's sentence covered `date` and `quarter` only, both of which the shipped parser reads (docs/spec/profile-contract-v4.md:1031-1033). `iso-month` is not a shipped member — src/synthtwin/parsing.py:64-71 still holds exactly six formats and src/synthtwin/contract.py:423-430 the same six — so "the shipped reader reads none of them" is a claim about a member no shipped reader reads at all. The transcriber correctly reported adding `month` to the enumeration; the noun needed to move with it. FIXED to "the date reader reads none of them with an offset".

7. DROPPED RIDER — the declaration's precedence over the placeholder pass is stated nowhere in the section. C6-39 (docs/spec/profile-contract-v6.md:859-865) names "the numeric pass, the CALENDAR PASS and the built-in vocabulary alike", and the plan's wire paragraph for this very pass ends "`--keep-value` wins exactly as today" (docs/plans/phase-4-columns.md:1720). The section defines the calendar pass and its entry conditions in full but never says a rescued cell is outside it, so a reader building the pass from this text alone would judge a declared value as a hole. FIXED by one sentence after CP-P that states the rule in words and points at C6-39 rather than restating it whole.

## GAPS

- SECTION NUMBERS ARE ASSUMED TO FOLLOW VERSION 4's, exactly as the already-written section 5 assumed (build/s5_meta.md gaps). My text points at section 4.4 (settings), 4.5 (the note grammar), 5.2 (the axes and the rule order), 5.4 (the absence classes), 5.5 (a sentinel verdict entry), 5.6 (the ladder), 6.3 (the shared label keys), 9 (the disposition matrix), 13 (the decisions) and 14 (the enumerations index). If the self-contained document renumbers, these ten pointers must move with it. Nothing else in my section depends on a number.
- THE TRIAL ORDER OVER THE ELEVEN FORMAT MEMBERS IS FIXED BY NO ARTIFACT. src/parsing.py:61-71 fixes an order for the six it ships and says the first format clearing the required share wins; plan:1676-1678 says month-first is tried before day-first. Where the five added members sit in that order — in particular whether `slashed-iso-date` is tried before the two ambiguous slashed families, and where the two slashed datetime members sit relative to the slashed date ones — is stated nowhere I could find. I wrote 'the vocabulary is tried in its own fixed order, month-first before day-first' and named no full order. Two producers could disagree about a column that clears the line under more than one member.
- WHETHER `subsecond_digits` CAN BE NONZERO ON THE FIVE ADDED FORMAT MEMBERS IS NOT STATED. The two clock forms of C6-10 exclude fractional seconds (v6:305-306), and the two slashed datetime members read 'a clock in a form of C6-10' (v6:435-436), so on my reading they can never carry a nonzero `subsecond_digits`; `iso-mixed` includes `iso-datetime`, whose shipped reader does read a fractional part (src/parsing.py:795-800), so it can. This is a reading of the cited grammars and not a rule either document writes down, and material:37 declared the same gap. I wrote nothing normative about it — D7 binds `subsecond_digits` to `time_precision` and nothing binds either to the format member.
- WHETHER A COLUMN READ BOTH WAYS THAT THEN DECLINES TO `datetime` STILL CARRIES THE SLASHED-DATE REMARK. v6:1112-1114 gives the trigger as 'the option was given and a slashed reading was in play' and v6:1226 (DF-R) says only that 'the column carries the slashed-date remark form'; neither settles the declined case. I worded DF-R as 'a column read under the option', which does not decide it either. If a declined column can carry the form, four counts of the table are published by a block with no `n_unparsed` key at all — the same open question material:33 registered for the disclosure inventory.
- `n_unparsed` ON AN `iso-mixed` COLUMN IS AN ENTAILMENT I STATED, NOT A CLAUSE I TRANSCRIBED. Version 4's definition is 'present cells that did not read as a date under the chosen format' (v4:926), and on a joint reading 'the chosen format' has two members. RM2 (v6:1252) with C6-25's key sets (v6:491-496) forces the reading I wrote — cells reading under neither ISO member — but no clause says it. If the owner prefers, it belongs in `n_unparsed`'s own row rather than under RM2.
- THE MONTH CASES OF TWO ENUMERATED SENTENCES ARE APPLICATIONS OF A RULE, NOT TRANSCRIBED EXAMPLES. (a) The canonical-forms example `2024-03` is mine; C6-24 fixes the form `YYYY-MM` (v6:486-489) and gives no example. (b) 'A month column writes `2024-03`' in the twin-cells paragraph applies owner decision 5's rule — 'the ISO form matching the precision the profile records' (v4:1106-1108) — to a precision version 4 did not have. Neither is an enumeration I completed from pattern, but both are sentences no artifact spells out.
- NO ARTIFACT FIXES AN EXAMPLE SPELLING FOR THE FIVE ADDED FORMAT MEMBERS, which matters one step outside my section: `format_example` (src/parsing.py:73-96) returns the member's own name for anything it does not know, so the `evidence_dates` and `said_read_as_dates` note forms would render 'are dates written as slashed-iso-date'. Already registered at build/s45_meta.md:39; repeated here because my format table is the list those renderings quantify over.
- WHETHER A BELOW-FLOOR CALENDAR PLACEHOLDER COUNTS IN `n_sentinel_candidates_unpublished` IS STILL UNSTATED. C6-35 says a judged placeholder publishes 'through the standing verdict machinery' (v6:703-707) and version 4's V1 puts below-floor candidates into that count (v4:642-647), so the entailment is clean, but no clause writes it down. I transcribed C6-35 as it stands and did not settle it; build/s5_meta.md registered the same gap for section 5.5.
- I COULD NOT ESTABLISH WHETHER THE PLACEHOLDER PASS CAN FIRE ON A COLUMN WHOSE FORMAT IS NOT A DATE-ONLY ONE — for instance whether `9999-12-31 00:00:00` in an `iso-datetime` column matches the placeholder. C6-33 says the match is on 'its own WRITTEN fields, under the column's own format' (v6:685-689), which reads as requiring the written day to denote that calendar day and says nothing about a clock field beside it. I transcribed C6-33 unchanged rather than narrowing or widening it.

## CONFLICTS NOTED

- THE D FAMILY RUNS D1 THROUGH D11, NOT D1-D6. The task's identifier list gives 'D1-D6'; version 4 states and checklists eleven (v4:974-1095, checklist v4:1923-1933). I kept all eleven at their own identifiers. If the list was meant as a cap rather than a family name, D7 through D11 would have to be renumbered, and the generation method, the validation method and the test suite cite them.
- D6's `month` ROW IS DERIVED FROM THE PLAN'S QUARTER PRECEDENT, NOT FROM A CLAUSE THAT BINDS IT. No artifact says in words that `time_precision: month` occurs only with `resolution: month`. What exists is plan:764-767 — the two vocabularies 'each gain the member `month` — the quarter precedent shows the two move together' — and C6-24 (v6:486-489), which repeats it. I wrote the binding into D6's table because a total invariant is what the task asked for and because without it a document pairing `resolution: datetime` with `time_precision: month` is refused by no rule (the hole material:36 registered). This is the one row of my section a reviewer should check against the owner's intent rather than against a transcription.
- D9's REASON GAINED A WORD. Version 4 reasons 'A whole date and a quarter carry no clock' (v4:1032); with four resolutions the enumeration is incomplete, so I wrote 'a whole date, a month and a quarter'. The rule itself is unchanged — it quantifies over `resolution` being `datetime`, which is already total.
- VERSION 4's 'All three sort correctly as plain text' IS STALE AND I WROTE FOUR, as instructed. `YYYY-MM` sorting as text is stated at v6:487 and plan:763, so the four-row claim is grounded and not inferred.
- THE DAY-FIRST READING RULE NOW STANDS IN TWO PLACES. build/s4.md:138-153 already states it inside the `day_first` settings paragraph, and I state it here because it decides a datetime column's `format`. Amendment A-P4-11 exists to end two-site rules: my recommendation is that section 4.4 keep only what the SETTING records (that the declaration was made, and that it does not record which reading a column took) and point here for the mechanics. I did not edit the written section.
- THE CEILING ARITHMETIC LIKEWISE STANDS IN TWO PLACES. build/s4.md:111 carries it in the `categorical_share` row ('the effective cap is min(categorical_ceiling, categorical_share of n_rows), never below categorical_floor'), and my 6.6.1 carries it beside the key it produces. One of the two should become a pointer.
- V4 AND C6-33 THROUGH C6-35 GOVERN KEYS DEFINED ELSEWHERE. V4 orders `sentinel_verdicts`, a universal key whose entry shape is section 5.5's; the placeholder pass feeds `missing_by_class`'s `(date-sentinel)`, which is section 5.4's. I wrote them here because this section is where the calendar reading lives and because the task assigned them. If whoever writes sections 5.4 and 5.5 also states them, one site must become a pointer — and section 5.5's `candidate` row must in any case carry the three-way domain (stand-in number, calendar day spelling, `(withheld)`), which I referenced rather than restated.
- VERSION 6's DISPOSITION ROW FOR `missing_by_source` IS NARROWER THAN C6-37. v6:1379 excepts only 'stand-in-spelled keys'; C6-37 (v6:837-839) excepts 'a spelling a JUDGED PASS put there — one reading as a stand-in number, or as a CALENDAR PLACEHOLDER'. I wrote the placeholder exception at C6-37's width. Already reported by build/s5_meta.md; repeated because my section is where the placeholder half of it is created.
- COUNT CHECK — EVERY VERIFIED COUNT IN MY SCOPE AGREES. 11 `format` members (mine set-equal to v6:1620-1623 and to D1's eleven rows), 4 `resolution` members, 6 `time_precision` members. One count in my section is not on the verified list and is transcribed from two places that agree: `datetimes_read_at` has two members, `local` and `utc` (v4:920, src/contract.py:436). The shipped constants still read six formats, three resolutions and five precisions (src/contract.py:423-434), which is expected — the code has not moved to version 6 — and I did NOT treat the shipped tuples as governing for the added members.
- I DID NOT VERIFY THE FIVE ADDED FORMAT MEMBERS AGAINST A SHIPPED PARSER, because none exists: src/parsing.py:64-71 still holds six. Every claim about what those five READ rests on v6:426-436 and plan:1666-1689. The readings I wrote for the six inherited members ARE checked against src/parsing.py:864-929 line by line.

## SOURCES

Paths are repo-relative to `/Users/alfredowork/Library/CloudStorage/OneDrive-UniversityofIowa/Research/0- Synthetic dataset/synthtwin`. Shorthand: v4/v5/v6 = `docs/spec/profile-contract-v{4,5,6}.md`; plan = `docs/plans/phase-4-columns.md`; build = `docs/spec/v6-build/`; src = `src/synthtwin/`; material = `docs/plans/reviews/material/phase-4-v6-derivation-datetime.md`.

### 6.6 head and 6.6.1 `categorical`

| rule / claim | source |
|---|---|
| section head, "Two roles with nothing in common but their place in this ordering" | v4:888-891, verbatim |
| "At most a ceiling of different folded identities, each shared by rows" | v4:895, verbatim |
| categorical is rule 8, claiming only a column every earlier rule declined | v6:206-212 (C6-1); build/s5.md:180-197 (the twelve-rule order as already written); plan:499 ("categorical (unchanged, ceiling and all)") |
| "Added keys: the four shared label keys of section 6.3, plus:" | v4:897, verbatim |
| `level_ceiling` row (type, range, meaning, LOADER-ONLY) | v4:901, verbatim; disposition also v4:2084; shipped key set `CATEGORICAL_KEYS = LABEL_KEYS + ("level_ceiling",)` at src/contract.py:342 |
| the ceiling arithmetic: smaller of `categorical_ceiling` and the largest whole number of rows within `categorical_share` of `n_rows`, never below `categorical_floor` | src/taxonomy.py:3573-3605 (`_categorical_ceiling`, lines 3603-3605 are the arithmetic), with `_at_most` at src/taxonomy.py:1679-1690; settings keys v4:287-289; the same arithmetic already stated in the settings section at build/s4.md:111 |
| ROWS not present values, with the 100-row / 30-filled / 6-label example and the free-text consequence | src/taxonomy.py:3580-3588 (docstring, review item P1-R6-F7) |
| "Which labels may then be SHOWN is a separate question, settled by `small_cell_floor`" | src/taxonomy.py:3585-3586 |
| "the comparison is between whole numbers, so no rounding of a division decides a role" | src/taxonomy.py:1682-1684; the same phrasing for the parse line at build/s4.md:121 |
| "no invariant ties the published value to that arithmetic; G1 and G2 are what a loader enforces" | v4:903-908 states only G1 and G2; checklist v4:1921-1922 carries only those two |
| **G1** `n_distinct_folded <= level_ceiling` | v4:903, verbatim; checklist v4:1921; shipped check src/contract.py:3674-3690 |
| **G2** LOADER-ONLY, records the line the column passed, no obligation on the twin, "the generator reproduces counts, not the rule that produced them" | v4:905-908, verbatim; shipped comment src/contract.py:1049-1052 |
| `level_ceiling` FORBIDDEN on every other role | v4:863 (`constant`), v4:877 (`binary`), v6:351-357 (C6-17, `long_tail_labels`), v6:1258 (G1L), v6:968-994 (C6-FKM: "Every key not listed for a role is FORBIDDEN on that role") |
| the reason it is forbidden on `long_tail_labels` — past the ceiling, so G1 is what such a column violates; no optional keys; the ceiling recorded in `detection_evidence` | v6:351-357, transcribed |
| a column above the ceiling is not necessarily free text | v6:340-344 (C6-15); plan:934-936; rule order v6:206-209 |

### 6.6.2 `datetime` — the role and its keys

| rule / claim | source |
|---|---|
| the role's condition (parse-line count, one member of the vocabulary, no earlier rule claiming it, rule 6) | build/s4.md:121 (`minimum_parse_rate`: "at least this share must parse under one date format before it is described as dates. Applied as a COUNT, never as a compared share"); v6:206-209 (order); src/taxonomy.py:3625 ("dates, under one documented format, at the parse rate") |
| the twelve inherited datetime keys, each with type, permitted values and meaning | v4:916-927, transcribed row for row; shipped `DATETIME_KEYS` src/contract.py:344-357 (the twelve entries at 345-356), emitted at src/taxonomy.py:3459-3478 |
| version 5 adds no datetime key (so the count is 12 + 1) | v5:971-981 is version 5's whole added-key table and names none; a grep of v5 for `datetime` returns nothing; material:50-55 verified the same |
| `resolution_mix` as the thirteenth key | v6:491-501 (C6-25); v6:981-982 (the key list for datetime blocks) |
| `format` permitted values = the eleven of the next table | v6:1620-1623 (§14); v6:426-436 and v6:456-468 |
| `resolution` permitted values `date`, `datetime`, `quarter`, `month` | v6:1625 (§14), in that order; v6:486-489 |
| `time_precision` permitted values `subsecond`, `second`, `minute`, `date`, `quarter`, `month` | v6:1627-1628 (§14), in that order; the five inherited are src/contract.py:434 |
| `datetimes_read_at` two values `local`, `utc` | v4:920; shipped `CLOCKS` src/contract.py:436 |
| the "three closed vocabularies, each copy bound by a rule" paragraph | pattern and reason taken from the already-written build/s5.md:40-53 (the "three closed lists" paragraph as corrected); the bindings themselves are D1 and D6 below |

### The format vocabulary, its readings, D1

| rule / claim | source |
|---|---|
| the six inherited members, at their wire spellings | src/parsing.py:64-71 (tuple; the six members at 65-70), and src/contract.py:423-430 |
| the five added members, at their wire spellings | v6:426-436 (C6-21) |
| `iso-date` reads `YYYY-MM-DD`, exactly ten characters, padded, hyphen-delimited | src/parsing.py:864-875 |
| `month-first-date` / `day-first-date` read slashed dates, one- or two-digit month and day, four-digit year | src/parsing.py:904-918 for the family; the field widths from v6:438-444 (C6-22) and plan:1666-1675 |
| `compact-date` reads exactly eight digits | src/parsing.py:897-903; v6:442-444 |
| `slashed-iso-date` reads `YYYY/MM/DD`, fields padded | v6:432 |
| `iso-month` reads `YYYY-MM` | v6:433; plan:762-764 |
| `year-quarter` reads a four-digit year, hyphen, `Q` in either case, quarter digit 1-4 | src/parsing.py:919-929 |
| `iso-datetime` reads a date, one separator (`T` in either case or a space), a clock `HH:MM` or `HH:MM:SS`, an optional fractional part, an optional offset | src/parsing.py:876-896, with `_parse_clock` at src/parsing.py:772-803 and `_split_offset` at src/parsing.py:806-839 |
| `iso-mixed` reads the joint ISO family reading | v6:434, v6:479-484 |
| `month-first-datetime` / `day-first-datetime` read a slashed date, one space, a clock in one of the two `time_of_day` forms | v6:435-436; the two clock forms v6:299-311 (C6-10); plan:1680-1685 |
| **D1**, total over all eleven members, with its refusal and its reason | v6:446-477, transcribed as plain `D1`; the eleven-row table is v6:456-468 verbatim; the "iso-date paired with datetime would be refused by no rule at all" reason is v6:449-452; version 4's own three-clause D1 (v4:974-976) is subsumed by the six inherited rows, as v6:474-477 says of them |
| the fractional part is read and discarded, whole seconds recorded | src/parsing.py:775-776, 795-800; `subsecond_digits` v4:919 |
| **C6-22** (the unpadded widening) | v6:438-444, transcribed; plan:1666-1675 (A-P4-1 item 1), including "no family overlaps another" and the retirement of the fixed character-count rule for the four families (plan:1673-1675) |

### The day-first reading rule

| rule / claim | source |
|---|---|
| the option, and the settings key recording the declaration | plan:881-883, 911-915; v6:371-376 (C6-20); build/s4.md:112, 138-153 |
| not a bare order swap; the ninety-nine-plus-one counterexample | plan:884-889, transcribed |
| evidence-first: both readings counted, strictly more cells wins, the declaration decides only a count tie | plan:889-893; v6:1225 (DF-P) |
| "which reading a column took is that column's own `format`" | build/s4.md:145-147 |
| month-first tried before day-first absent the declaration; first member clearing the line wins | src/parsing.py:61-71 (the tuple's order and its comment); plan:1676-1678 ("Ambiguity handling is untouched: month-first tried first") |
| **DF-P** as a producer row | v6:1225 |
| **DF-R**: the column carries the slashed-date remark form, built from the four counts and the reading used, once per column | v6:1226; v6:1027 (arity and the five arguments); v6:1112-1114 (the trigger); build/s45.md:591-602 (form D18, already written) |
| the remark is written over the evidence, not the winner; a tie is not always full ambiguity | plan:893-900, transcribed; the two-clause structure is left to section 4.5 (build/s45.md:604-638) rather than restated |
| why both are producer obligations | v6:1198-1207 |

### The joint ISO reading and `resolution_mix`

| rule / claim | source |
|---|---|
| **C6-23**: single-format pass first, its verdict stands; the joint test only where no single format clears the line; `iso-mixed` at the family's finest resolution | v6:479-484, transcribed; the ninety-nine-and-one example plan:770-774 |
| only the ISO family mixes; slashed and compact do not | plan:797-800 |
| a month-with-day mix is a recorded decline, residual R-P4-6 | plan:1530-1533 |
| **C6-25** (`resolution_mix`): required on every datetime block, closed key sets, exact counts, floor-free with its reason | v6:491-501, transcribed; plan:778-786 |
| **RM1** | v6:1251 |
| **RM2** | v6:1252; `n_unparsed`'s meaning v4:926 |
| the `iso-mixed` reading of `n_unparsed` | entailed by v6:491-496 with v6:1252 and v4:926; no clause states it in words (declared in gaps) |
| **RM-P**, with the 40/60-versus-50/50 argument | v6:1229, transcribed |
| `resolution_mix` REPORT-ONLY, and why | v6:500-501, v6:1183, v6:1582-1587 (13.3); plan:786-796; residual R-P4-12 at plan:1550-1556 |

### Canonical forms, ranges, offsets

| rule / claim | source |
|---|---|
| the `date`, `datetime` and `quarter` rows and their examples | v4:931-935, verbatim |
| the `month` row, canonical `YYYY-MM` | v6:486-489 (C6-24); plan:762-764. The example `2024-03` is mine (declared in gaps) |
| "All four sort correctly as plain text, which is why L1 compares `date_percentiles` as text" | v4:937-939 written at four; `YYYY-MM` sorts as text at v6:487 and plan:763; L1 itself is v4:675-679 |
| the RANGES table, all seven rows including the `SS` 00-60 cell and its leap-second reason | v4:940-952, verbatim; the Gregorian rule and the calendar check in src/parsing.py:744-756 |
| the "checking the shape alone has a cost" paragraph | v4:954-962, with its version-history framing dropped and the reasoning kept |
| the offset forms and the offset range (hours 00-14, minutes 00-59, 14 requires 00) | v4:964-972, verbatim; enforced at src/parsing.py:830-838 |

### The datetime invariants

| rule / claim | source |
|---|---|
| **D2** | v4:978-979, verbatim |
| **D3** | v4:981-983, verbatim |
| **D4** with its contradiction reason | v4:985-991, verbatim |
| **D5** with the local-text reason | v4:993-999, verbatim |
| D5 is a published fact, not re-derivable; the one direction a loader checks | v4:1001-1010, verbatim |
| **D6**, restated as a total four-by-six table | version 4's three clauses at v4:1012-1015 give the `date`, `quarter` and `datetime` rows; the `month` row rests on plan:764-767 ("the resolution enumeration AND its sibling `time_precision` enumeration each gain the member `month` — the quarter precedent shows the two move together") and v6:486-489. The hole this closes was registered at material:36 |
| why `date` beside `datetime` is refused | v4:1017-1027, transcribed |
| **D9**, with `month` added to its enumerated reason | v4:1029-1033; the added `month` follows from the canonical form at v6:487; the four offset-bearing members from D1's table (v6:465-468) and material:103-106 |
| **D7** | v4:1035-1037, verbatim |
| **D8**, with the checkable form | v4:1039-1043; the checkable form `n_unparsed < n_present` from the checklist v4:1930 |
| **D10**, both bullets and the year-boundary clause | v4:1044-1063, transcribed; the pointer to "6.6.2's canonical form" rewritten as "the canonical forms above" |
| why D10 is refused rather than reported | v4:1065-1083, transcribed; the "(13.16)" pointer written as "section 13 records the four" |
| **D11** | v4:1085-1095, verbatim |
| the second-resolution consequence | v4:1097-1105, verbatim |
| twin datetime cells, owner decision 5 | v4:1106-1112; the `iso-mixed` sentence from plan:789-796 and v6:1585-1587 |
| `format` is REPORT-ONLY, residual R-P2-7 | v4:1113-1119, verbatim; "widens what is read, not what is remembered" from plan:1640-1642 |

### The calendar placeholders

| rule / claim | source |
|---|---|
| the two placeholders are `1900-01-01` and `9999-12-31`, members of the published vocabulary | v6:653 and v6:1638 (C6-31); plan:1690-1692 |
| **C6-33** (identity at the written calendar day) | v6:685-689, verbatim; plan:1692-1696 |
| **C6-34** (the pass, its settings, its position, its entry condition, and what happens when it does not run) | v6:691-701, verbatim; plan:1696-1710. "The first five rules of section 5.2's order" is v6:695 read against C6-1's numbering (v6:206-209); the plan's own wording is "rules 0 through 4" in the older numbering (plan:1701) |
| "no settings key of its own" | v6:381-384; plan:1698-1699 |
| the judged cells are counted absent and the column described from the remainder | entailed by v6:697-698 ("no cell is removed" in the negative case) with the `(date-sentinel)` class at v6:676-681; plan:1711-1713 |
| **C6-35** (verdicts through the standing machinery) | v6:703-707, verbatim |
| the `candidate` domain admitting a canonical ISO day spelling | v6:412-420 (stated here as the reason section 5.5's row carries three alternatives, not restated as a rule) |
| **CP-P** | v6:1227, verbatim |
| `(date-sentinel)` counts these cells, REPORT-ONLY | v6:676-681 (C6-N3), v6:1184 |
| the twin leaves such a spelling blank | v6:837-839 (C6-37) with its reason at v6:846-857 (C6-38) |
| **V4**, the three-group ordering with its reasons | v6:709-734, transcribed as plain `V4`; groups 1 and 3 are version 4's own two sentences (v4:659-663); the "calendar-only block ordered by nothing at all" reason is v6:712-716 with its revision framing dropped |

### Counts checked against the artifacts

| count | check |
|---|---|
| `format` = 11 | my table has 11 rows; set-equal to v6:1620-1623 and to D1's 11 rows (v6:456-468); six of them set-equal to src/parsing.py:65-70 |
| `resolution` = 4 | v6:1625; used identically in the key table, the canonical-forms table and D6 |
| `time_precision` = 6 | v6:1627-1628; all six appear in D6's table, each once |
| datetime keys = 13 | 12 at v4:916-927 and src/contract.py:345-356, plus `resolution_mix` (v6:491-501); material:50-55 verified the same arithmetic |
| `datetimes_read_at` = 2 | v4:920; src/contract.py:436 |
| 13 roles / 13 statistical types | used only by pointer to section 5.2 (build/s5.md:85-105); not restated here |
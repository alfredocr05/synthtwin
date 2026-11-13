# STATE — read this first

**One page, kept current, for whoever picks this up next — a person
returning after a week, or an assistant starting a conversation with no
memory of the last one.** Everything here is a fact about *right now*.
History lives in `CHANGELOG.md`, the phase plans and `git log`.

**The rule that keeps it true: this file moves in the same commit as
the work it describes.** A landing that does not update it is not
finished.

**And the rule that keeps it SHORT.** This page reached 3,814 lines by
growing a section per landing, and at that size no session read it. **A
landing adds nothing to this page except by changing a fact already
stated here.** What a landing DID belongs in `CHANGELOG.md`.

**One fact, one place.** Every count here that also exists elsewhere has
gone stale at least once. State a fact where it is measured and point at
it from everywhere else.

---

## THE TWIN, DEFINED (owner, 2026-09-12)

> **At the population level the twin is identical to the real table.
> None of its rows is a real row. And the description needed to build
> that population reveals nothing about any individual.**

Three clauses, all three binding. The first is the fidelity goal and now
includes structure ACROSS columns, not only within them. The second is
the provenance claim. The third is new and is the one that bites: it
supersedes the floor-of-one reasoning of A-P4-37, because a published
value held by exactly one person reveals that person's value.

**Two goals, both mandatory, neither ranked above the other** (owner,
2026-09-12): code developed on the twin runs unchanged on the real
table, AND statistics computed on the twin are reliable — within a
column and between columns.

**Out of scope, permanently:** joins. The table handed to synthtwin is
the final analysis table. Several rows per subject is NOT a join and
stays in scope.

## Where the work is

| | |
|---|---|
| branch | `phase-5-relationships`, cut from `main`. `main` is pull-request only. Stage 2b was built on `carried-2b-integration`, cut from it at `53bb012`, and lands on it whole |
| phase | **Phase 4 REOPENED 2026-09-12** — it closed on 2026-09-11 with silent within-column defects live inside its own charter. Phase 5 does not start until the ordered list below reaches it |
| plan | This page is the plan of record. `docs/plans/phase-5-relationships.md` is a DRAFT whose scope is superseded: it deferred correlation, and correlation is now mandatory |
| suite | 19,194 collected on batch 4s's fix head `85eb6754` (by `pytest --collect-only` under Python 3.11 over the whole tree and placed by `tools/ci/shards.py --of 5 --prove`, 410 files, every file in exactly one shard): the merged line's 19,172 and the 22 cases of the fix round's new gate file `tests/test_merged_line_review_items.py` (its shard weight 403.77 s). The whole suite ran on the fix head (2026-11-12, 19:29 to 22:25, the five shards at once through the suite runner, Python 3.11 only; GitHub's run covers Python 3.11 to 3.14 on three systems): shards 1, 3, 4 and 5 exit 0 and shard 2 exit 1, 19,120 passed, 56 skipped, 15 expected to fail and 3 failed, the 19,194 collected there; the three are the disposition registry's seal cases (`test_no_passage_of_a_governing_document_is_unsealed`, `test_no_sealed_passage_has_been_deleted_from_its_document` and `test_the_registry_judgment_is_sealed`), which batch 4s's seal clears. The merged line's 19,172 were counted on its owed items' head `ce75ec54` by the same means (409 files): batch 4r's sealed head's 18,193 and the 979 that batch 4s's merge steps and owed items add, each step's count in its own records. Batch 4r's final whole suite on its sealed head `9545edee` (2026-11-10, every shard exiting 0, Python 3.11 only) is read at batch 4s's seal by `tools/measurements/kpi_suite_shards.py`: `K-P0-11` registered from it, and `K-P0-10` read and not stamped (the KPI row). Batch 4r's sealed head held 18,193 (counted on its fix head `59267e6b` by `pytest --collect-only` under Python 3.11 over the whole tree and placed by `tools/ci/shards.py --of 5 --prove`, 399 files, every file in exactly one shard): the merged line's 18,170 and the 23 cases batch 4r's fix round adds (P4-D467), 22 in `tests/test_stage6_chain_recount.py` and 1 in `tests/test_zoo_dates_in_disguise.py`, in no new file, so no shard weight moves. Batch 4r's whole suite ran on its reviewed head `820d55c3`, beside the batch's proofs (2026-11-09, Python 3.11 only): shards 1, 3, 4 and 5 exit 0 and shard 2 exit 1, 18,097 passed, 56 skipped, 15 expected to fail and 2 failed, the 18,170 collected there; the two are the disposition registry's two seal cases, which the seal clears, and the two test files the fix round changed ran whole on its head in its verify (39 and 174 passed); `tools/measurements/kpi_suite_shards.py` refuses that suite (its failed cases), so `K-P0-10`'s two seconds stay unresolved and `K-P0-11` unregistered, owed to the final whole suite on the sealed head (read at batch 4s's seal). The merged line's 18,170 were counted on its merge steps' head `fd8fa3ec` by the same means (399 files): batch 4q's records head's 18,032 and the 138 batch 4r's merges add, named at the end of this row. Batch 4q's records head's 18,032 were collected on the sealed head `b159eb50` with its four fix rounds' eighteen commits and the records (counted by `pytest --collect-only` under Python 3.11 over the whole tree and placed by `tools/ci/shards.py --of 5 --prove`, 395 files, every file in exactly one shard; the count over every test file the first two rounds changed and every file importing their two changed helpers, 1,139 cases against 1,039 on the merged head `b93f128a`, agrees): the sealed head's 17,846 and the 186 the fix rounds add: 2 in the three commits the outside review read with the merged line (one case each in `tests/test_held_dates_off_the_real_typed.py` and `tests/test_stage6_band_totals.py`), 58 in the first round (54 in its three new files, `tests/test_record_numbers_beside_text.py`, `tests/test_held_dates_reader_readings.py` and `tests/test_chain_grades_held_dates.py`, and one each in four files), 40 in the second (37 in the new `tests/test_held_dates_field_readings.py` and 3 in the record-number file), 29 in the third (the new `tests/test_held_dates_spellings.py`) and 57 in the fourth (the new `tests/test_held_dates_export_spellings.py`; the third's file grew no case). THE FINAL WHOLE SUITE ran on `41377220`, the records head before the last wording passes (2026-11-09, 05:13 to 06:22): shards 1 to 5 exit 0, 17,961 passed, 56 skipped, 15 expected to fail and 0 failed, the 18,032 collected; the commits after it change records, one row of `tools/measurements/README.md`, docstring lines and the seal only. The fourth round ran no whole suite (its builder ran the targeted files and the whole-source guards). The third round's whole suite on its head `36023624`, the code evidence before the fourth round: 17,901 passed, 56 skipped, 15 expected to fail and 3 failed, the 17,975 collected (shards 1, 3 and 5 exit 0, 2 and 4 exit 1); the three are the records' own, as in the second round's suite, which the fix branch does not carry, and `tools/measurements/kpi_suite_shards.py` refuses it alike. The second round's whole suite on its head `c22837e6`: 17,872 passed, 56 skipped, 15 expected to fail and 3 failed, the 17,946 collected (shards 1, 3 and 5 exit 0, 2 and 4 exit 1); the three are the records' own, the disposition registry's two seal cases and the ledger's case on `K-HZ-06`'s stamp, which the records round's stamps and seal clear; `tools/measurements/kpi_suite_shards.py` refuses it as no finished run (its failed cases), so `K-P0-10`'s two seconds stay unresolved and `K-P0-11` unregistered, owed to a green whole suite. The first round's whole suite on its head `037d4fcd` collected 17,906 and failed 4: the registry's two seal cases and `K-HZ-06`'s stamp, which wait for the records, and the source guard against quadratic growth, fixed by the second round; the regression of the merged line below passed there. The sealed head's 17,846 (its merged head `b93f128a` and the seal's records; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 389 files, every file in exactly one shard): batch 4p's records round's 16,862 and the 984 batch 4q's merges add net, named at the end of this row. Its whole suite on the merged head `b93f128a`, run beside the batch's proofs: 17,771 passed, 56 skipped, 15 expected to fail and 4 failed, the 17,846 collected; the seal clears two (the disposition registry's two cases), the ledger's case that each entry's expected value is true of itself stays red on `K-HZ-06` alone until the batch's records round stamps it from its fix round's proof, and the fourth, `tests/test_numeric_strata_round_trip.py`'s 2,000-row case of whole hundreds, is a regression of the batch's line (lane CZ-A's blank hold beside lane TT's keyboard rule at their merge), batch 4q's fix round's. Batch 4p's records round's 16,862 were collected (counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 374 files, every file in exactly one shard): the fix round's 16,860 and the records round's two cases, a third gate case in lane GRa's gate file (a position list's first entry, from the fix round's scoped verify) and one in the source test of names bound twice (a `for` and a `with` target); the records round changes no product code, and its two changed test files ran green on its tree, 90 passed. The fix round's 16,860: the sealed head's 16,856, the fix round's two gate cases in lane GRa's gate file (Codex's review of the sealed head `d8f5e147`, item 1, and the year of birth its sibling sweep found) and the two cases of its new source test that no module-level name is bound twice; its whole suite on the fix round's head `ba87102b` green in five shards: 16,789 passed, 56 skipped and 15 expected to fail, the 16,860 collected. The sealed head's 16,856: batch 4o's 16,645 and the 211 batch 4p's merges add, named at the end of this row. Batch 4o's 16,645 were collected on its second fix round (the independent verify of the fix round, LANE I4m RULINGS 27 (1): its gate file adds 8 cases to the fix round's 16,637; 367 files), its whole suite on `4324aced` green in five shards: 16,574 passed, 56 skipped and 15 expected to fail, the 16,645 collected. The fix round's whole suite on `fcd01166` read 16,565 passed, 56 skipped, 15 expected to fail and 1 failed, the source-loading guard's count of files loaded as modules (59 against 58 recorded: the fix round's pool test loads the committed generation oracle), moved to 59 in this round. The fix round's 16,637 (Codex's review of the sealed head `015d5003`: the three gate files of its three High items add 15 cases to the seal's 16,621, and the sibling sweep's held column in the age reach one more; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 366 files, every file in exactly one shard), its whole suite run after the fix round. The sealed head's whole suite read 16,544 passed, 56 skipped, 14 expected to fail and 7 failed, each failure this batch's (LANE I4m RULINGS 22): six cases of lane SH2's five age tails, read as held by the table of the date-count question the tests-only fix 3355025d put them in, fixed; and the perioperative export's day counts, which the zoo's truthful `yes` holds (owner lane CZ-H2), marked expected to fail, strict, so 15 expected to fail from the fix round. The seal's 16,621 (`3355025d` with the seal's records, 363 files): batch 4n's 16,068 and the 553 this batch adds, named below. Batch 4n's 16,068 were collected on its second fix round `f18c3638`, whose whole suite ran green in five shards (15,998 passed, 56 skipped, 14 expected to fail; its 3 gate cases, P4-D442, on the fix round's 16,065, whose 8 gate cases stand on the 16,057 of batch 4n's merged head `322b92de`, which held lane HB's 74 cases and lane CL's and the batch's owed records' 9 on batch 4m's 16,075, less lane SPD's move of 120 cases into its slow drivers beside its 19 added, P4-D444; lane HB's branch read 16,149: lane HB's fix 4 of close round 2: one case added, LANE HB RULINGS 14's differential case of the form term, three gate cases amended to rule 42's restatement and renamed, and the seven cases of ordinary tables green again, P4-D442; lane HB's fix 3 of close round 2: 3 gate cases on the repair's 16,145; lane HB's repair of close round 2: 7 gate cases on close round 2's 16,138; lane HB's close round 2: 8 gate cases on the close round's 16,130, which held lane HB merged on batch 4m, its close round included: its gate, its hunt's files and the cases it amended, 55 on batch 4m's 16,075, which held lanes UN-1a, CODES-1, GG, CHb, SH2 and UN-1b on batch 4l part b's 15,564; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 357 files, every file in exactly one shard). Lane MR's rules page adds 29 cases in one new file (its branch read 16,104 on batch 4m's 16,075); Lane PL's gate and the cases it amended add 93 (its branch read 16,167 on batch 4m's 16,074), and the merge's two cases pinning its loader's and its profiler's split of a pool 2 more; lane SH3's gate and the cases it amended add 109 (its branch read 16,184 on batch 4m's 16,075); lane CZ-D's gate adds 68 cases in one new file (its branch read 15,841 on batch 4m's records head `a5702b71` before its repair 3 added one); lane CZ-H's gate and the cases it added and amended add 181 (its branch read 15,955 on batch 4m's records head `a5702b71`), and the merge's three gate cases of its limit (h) 3 more; lane MPOL2's page adds 10 cases to its test file (its branch read 15,784 on batch 4m's records head `a5702b71`); lane MPp's gate and the cases it added and amended add 54 (its branch read 16,129 on batch 4m's 16,075); with the owes of the merges, lane MR's two pinned helper legs and lane SH3's two street cases, they make batch 4o's 553. Batch 4p's merges add to batch 4o's 16,645: lane BT2's reader, clock-mirror and gate cases add 59 (its branch read 15,833 on batch 4m's records head `a5702b71`); lane CHa2's gate's 37 cases and its four oracle cases add 41 (its branch read 16,115 on batch 4m's 16,074); lane GRa's gate adds 83 cases in one new file (its branch read 16,198 on lane CHa2's 16,115), and the merge's case of the patient table's pooled top category 1 more; lane MPg's gate and its sort's cases add 27 in two new files (its branch read 16,156 on lane MPp's 16,129); they make batch 4p's 211, counted at its seal. Batch 4q's merges add to batch 4p's records round's 16,862: lane ARR-a's helper, computer and scanner cases add 382, 147 in the new `tests/test_arrays.py`, 6 in the new `tests/test_computer.py` and 229 in `tests/test_offline_scan.py` (its branch read 17,019 on batch 4o's fix round's 16,637); lane TT's gate's two new files add 42 cases and the failure catalog's 16 for its eight new messages, 58 (its branch read 16,126 on batch 4n's 16,068); lane RO's gate adds 41 cases in one new file (its branch read 16,649 at its follow-up, 16,648 at its repair 2, 16,636 at its repair 1 and 16,628 at its build, on batch 4o's step-2 head `5220c90c`; the 99 per cent bar on the stay's duration is withdrawn as a bar, a figure of MR.13 limit 18); lane ST's gate adds 95 cases in one new file, `tests/test_stage6_selftest_reports.py` (56 at its repair 1, 29 more at its repair 2, 10 more at its follow-up), and its repair 1 one case to `tests/test_analyst_battery.py` (its branch read 16,704 on batch 4o's step-2 head's 16,608; 16,635 at its build, 16,665 at its repair 1, 16,694 at its repair 2; its suite repair adds none and marks one case of the base expected to fail, strict, as batch 4o's fix round marks it), P4-D458, and the merge's two cases of its private report beside lane GRa's patient layer and subject question 2 more; lane ID-ROOM2's six gate files add 103 cases (its branch read 16,171 on batch 4n's second fix round's 16,068: its follow-up grew the gate's 79 to 80, a unit case red on the verify's mutant X6; repair 2 grew the gate's 70 to 79 and added two files of shapes at 20,000 rows, 5 and 4 cases; repair 1 grew the gate's 51, split its zoo runs into two files of their own and added its shapes at 20,000 rows), P4-D457; lane CZ-A's gate adds 323 cases, 286 in `tests/test_zoo_safe_harbor_forms.py` and 21 in `tests/test_zoo_safe_harbor_forms_walk.py`, two new files, and 16 of `tests/test_health_zoo.py`'s over the catalogue's eight new tables (its branch read 16,391 at its repair 2 head on batch 4n's 16,068; 16,295 at its repair 1 head, 16,218 at its first), P4-D445; lane CHs's gate adds 17 cases in one new file, `tests/test_stage6_chain_describe_scale.py` (its branch read 16,625 on batch 4o's step-2 head `5220c90c`'s 16,608, two of them its repair 1's and six its repair 2's), P4-D462; lane SPD2 moves 55 cases of four files out of the suite into `K-HZ-21`'s slow driver, `tools/measurements/kpi_moved_cases.py`, and adds 16, a net 39 fewer (six 20,000-row legs of the zoo's hold routes kept in the suite for their size-gated mutants; its branch read 16,029 on its repair-2 head `58aae335`, on batch 4n's second fix round's 16,068), P4-D461; its whole suite on its own head `9f6e061d` ran green in five shards, 5,800, 6,075, 5,866, 6,193 and 6,112 s a shard (15,959 passed, 56 skipped, 14 expected to fail); on its tree the new packing first ran on `f9be5138`, 5,956, 6,125, 5,954, 6,040 and 6,025 s a shard, its shard 1 red on one case (the decontamination scan of P4-D461's own text, rewritten in repair 1), and on repair 1's head `8ad59431` green, 5,438, 5,570, 5,499, 5,599 and 5,550 s; base run 1 ran 6,927, 4,871, 10,314, 5,427 and 9,580 s, and the earlier measurement `e45eaecc` (the old packing, one-minute load 44 to 140) 6,457, 4,341, 8,267, 5,972 and 9,114 s, its shard 1 red with 4 failed (records in progress); the lane merged in batch 4q, so its acceptance is read from batch 4q's whole suite on the sealed head against base run 1, and `K-P0-11` is registered from that run (P4-D461); they are counted at batch 4q's seal. Batch 4r's merges add to batch 4q's records head's 18,032: lane SR2a's gate adds 76 cases in one new file (its branch read 16,697 on batch 4o's records head `c47a6aee`, 16,621, after its repair 2's 9; its suite repair adds none and marks one case of the base expected to fail, strict, as batch 4o's fix round marks it); lane PRT-a's gate adds 39 cases in one new file, `tests/test_readers_once_a_spelling.py` (its branch read 16,895 at its repair 2 on batch 4p's line `fc01f095`'s 16,856, 16,891 at its repair 1 and 16,888 at its build; its whole suite at its repair 1 and at its build read 3 failed, the three that fail on `fc01f095` alone and pass on batch 4p's fix round `ba87102b`: two key-name cases and the stand-ins page's citation case); lane BT3a's gate adds 22 cases in two new files, `tests/test_stage6_chain_recount.py` (17) and `tests/test_stage6_chain_recount_settled.py` (5) (its branch read 16,878 at its repair 2 on batch 4p's line `fc01f095`, its repair 3 adding none; its whole suite on its final head `36cd6c36` read 2 failed, the two key-name cases that fail on `fc01f095` alone, as above), and batch 4r's merge of it adds one case to the second file, its rule steps reading the cells of the reading that stands (6 there, 23 in the two): 138 in all, counted in the merged line's 18,170 above. Lane LM1's branch (plan P4-D475) collects 18,213 at its repair 2 (counted by `pytest --collect-only` under Python 3.11 over the whole tree on its code head `d2fc8c94`: 18,195 with `tests/test_ci_shards.py` refused while its weight was being written, and that file's 18 collected alone after it): the merged line's 18,170 and the lane's 43 -- its gate file's 42 cases in one new file, `tests/test_lm1_numbers_as_written.py`, and K-S3-64's code shape `expcode` at 600 rows, 1; the exponent form's cases left with it (repair 1 counted 81). Lane TR's branch collects 18,220 at its follow-up head: its repair-2 head's 18,210 and the 10 cases the follow-up adds (8 in its gate file, 45 against 37 there, and 2 in `tests/test_failure_catalog.py` for the message its new entry names; counted by `pytest --collect-only` under Python 3.11 over the whole tree, 400 files). The 18,210 on lane TR's repair-2 head: its repair head's 18,200 (`700c8ee5`, counted by `pytest --collect-only` under Python 3.11 over the whole tree, 400 files) and the 10 cases its repair 2 adds to its gate file (37 against 27 there, counted by `pytest --collect-only` over that file; no other test file changed since). Those 18,200 are batch 4r's merged line's 18,170 and the 30 cases of lane TR (plan P4-D473): 27 in its new gate file `tests/test_zoo_time_readers.py` (15 at its build, 12 at its repair 1), one in `tests/test_profile_document.py` and two in `tests/test_chain_grades_held_dates.py` (its repair 1; `tests/test_held_dates_off_the_real.py`'s stamp reading moved from a parametrized case to a case of its own, no case more). Lane DST's branch collects 18,224 (plan P4-D474, repair 2): batch 4r's merged line's 18,170 above and the 54 cases of the lane's new gate file, `tests/test_offsets_follow_the_date.py` (30 at the build, 9 added by repair 1, 15 by repair 2), collected alone by `pytest --collect-only` under Python 3.11 (one of them a case that holds zone words once lane TR's reading stands beside the lane, and skips until then). The lane's whole suite on its build head `d6aeb437` had 12 red cases in seven files, none red on `820d55c3`; repair 1 fixed each at its cause (P4-D474's repair round 1, item (1)); the whole suite of repair 1's head `32db00de` exited 0 on all five shards (Python 3.11 only), and that of repair 2's head runs in a step of its own. Lane CODES-2's follow-up micro-step head collects 18,145 (plan P4-D471): the follow-up's 18,141 and the 4 the micro-step adds, all in the gate file `tests/test_zoo_rare_names.py` (106 cases against the follow-up's 102: the glued grammar enumerated on the four roads, number words glued with `eight` through the commands at the owner's floor, and the two sides of the re-ruled week), each file collected on the follow-up's head and on the micro-step's (`tests/test_description_line_endings.py` 15 on both); no other file's cases move. 18,141 collected on lane CODES-2's follow-up head (plan P4-D471): repair 2's 18,131 and the 10 the follow-up adds, all in the gate file `tests/test_zoo_rare_names.py` (102 cases against repair 2's 92: one generated case of a character that prints nothing inside a word or a number, one of number words glued into one, one of the week reader, four of the neighbour families, one of `c` glued before a number, one of `SSN` glued to figures, and one case at the owner's floor through the commands), each file collected on repair 2's head and on the follow-up's (`tests/test_description_line_endings.py` 15 on both); no other file's cases move. The whole suite of repair 2's head `b26d2b0a` (Python 3.11 only): 18,059 passed, 56 skipped, 15 expected to fail and 1 failed, the 18,131 collected (shards 1, 3, 4 and 5 exit 0, shard 2 exit 1); the one, the line-ending rule over the suite's writes, is the lane's own, fixed by the lane's suite repair (three keyword arguments in the gate file's driver case, no case added), which the follow-up carries. 18,131 collected on lane CODES-2's repair 2 head (plan P4-D471): repair 1's 18,115 and the 16 repair 2 adds, 14 in the gate file `tests/test_zoo_rare_names.py` (92 cases against repair 1's 78) and 2 in `tests/test_contract_loader.py`'s refused descriptions (B4g: a named pool naming a number its counts leave no row, and one said to be counted in people; 439 cases against 437), each file collected on repair 1's head and on repair 2's; no other file's cases move. Repair 1's 18,115 collected on lane CODES-2's repair 1 head: batch 4q's records head `a391424c`'s 18,032 and the lane's new gate file, `tests/test_zoo_rare_names.py`, 78 cases (12 at the build), 396 files; the repair adds 4 to `tests/test_contract_loader.py`'s refused descriptions (B4f to B4h) and 1 to `tests/test_zoo_stand_ins_page.py`'s pinned sentences, each file collected on the build head and on the repair's; no other file's cases move. Lane CZ-F's repair-2 head collects 18,468 (counted on its records head, whose tests are those of `466023fb`, by `pytest --collect-only` under Python 3.11 over the whole tree and placed by `tools/ci/shards.py --of 5 --prove`, 400 files, every file in exactly one shard): batch 4r's merged line's 18,170 and the 298 cases of the lane's new gate file `tests/test_zoo_persons_names.py` (P4-D478; 142 at the lane's build, 143 from its repair 1, 13 from its repair 2). Lane CZ-A2's follow-up 4 head collects 18,093: batch 4q's records head's 18,032 and the 61 cases of the lane's new `tests/test_labelled_record_numbers.py`, 15 at its build, 25 added by its repair 1, 17 by its repair 2, 2 by its follow-up and 2 by its follow-up 4 (counted by `pytest --collect-only` over that file, 396 files; plan P4-D469). Lane HB2's repair 2 head collects 18,204 (counted by `pytest --collect-only` under Python 3.11 over the whole tree, 401 files): batch 4r's merged line's 18,170 and the lane's 34, 17 in its new `tests/test_safe_harbor_age_words.py` and 17 in its new `tests/test_safe_harbor_ends_and_bounds.py`. Lane CZ-E's repair 2 head collects 18,275 (plan P4-D472; counted by `pytest --collect-only` under Python 3.11 over the whole tree and placed by `tools/ci/shards.py --of 5 --prove`, 396 files, every file in exactly one shard): batch 4q's 18,032 and the 243 cases of the lane's gate file, `tests/test_zoo_value_readers.py` (75 at the lane's build, 70 more at its repair 1, 98 more at its repair 2). Lane SV's repair 2 head collects 18,210 (plan P4-D476; counted over the two test files the lane changed, its gate `tests/test_stage4_validate_groups.py` and `tests/test_kpi_ledger_integrity.py`, by `pytest --collect-only` under Python 3.11, 85 cases against 45 on batch 4r's reviewed head `820d55c3`): batch 4r's merged line's 18,170 and the 40 cases of the lane's gate, its other changed test file keeping its count. The lane's whole suite on `3d339e4b`, its repair 1's head (2026-11-11, Python 3.11 only): shards 1 to 5 exit 0, 18,132 passed, 56 skipped, 15 expected to fail and 0 failed, the 18,203 collected (on `139d70cb`, before repair 1, shard 3 had exited 1 on two line-ending cases of the gate file, which repair 1 pinned); a whole suite on repair 2's head is its own step. One process took about 66 minutes when the suite held 9,138 cases (ledger `K-P0-10` carried those seconds until its dated amendment of 2026-11-06, which bounds the five shards' instead); at 13,553, on `b85200be` (batch 4f), the five shards took 24.5 to 48.5 minutes each beside other lanes' runs. In CI it runs as **five shards**. Re-measure here whenever the count moves |
| KPIs | `tests/kpi/ledger.json`: 289 KPIs over phases 0-4, stages 1, 2, 2b, 3, 3b, 4, 5 and 6, the terminal, the health data zoo and the broad between-columns program, 37 of them headlines under a cap of 37 (raised from 30 at 3b.K, plan P4-D364, for `K-S3-38`; from 31 to 35 by the orchestrator's recorded call D15 of the December plan, plans P4-D397, P4-D399 and P4-D398, for `K-S8-01`, `K-HZ-01`, `K-BC-01` and `K-BC-02`; to 36 for lane S5a's `K-S5-01`, plan P4-D437; to 37 for lane RO's `K-S6-06`, plan P4-D459; the owner may veto any); 225 green, 48 open, 16 limits the owner accepted: batch 4s's seal registers lane SPD2's `K-P0-11`, green, and moves no status of an existing entry; batch 4r's ledger read 220, 42 and 16 at its seal (no status moved there), as batch 4q's at its seal and its records round, and batch 4s's merge of lane LM1 adds its `K-HZ-28`, green (P4-D475; its stamp is the lane's repair-2 code `45a52e0`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane TR adds its `K-HZ-26`, open (P4-D473; its stamp is the lane's repair-2 code `3080e7a`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane DST adds its `K-HZ-27`, open (P4-D474; its stamp is the lane's repair-2 code `f0111ce`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane CODES-2 adds its `K-HZ-23`, open, and its `K-HZ-24`, green (P4-D471; their stamps are the lane's repair-2 commit `d5c88ab`'s, its src that of repair 2's head, re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane CZ-F adds its `K-HZ-30`, open (P4-D478; its stamp is the lane's repair-2 code `52ccef3`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane CZ-A2 adds its `K-HZ-22`, green (P4-D469; its stamp is the lane's repair-2 code `d3f6a04`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane HB2 adds its `K-HZ-29`, open (P4-D477; its stamp is the lane's repair-2 code `a245c77`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane CZ-E adds its `K-HZ-25`, green (P4-D472; its stamp is the lane's repair-1 code `efed5b4`'s re-taken at batch 4s's seal on its fix head `85eb6754`), and its merge of lane SV adds its `K-S4-23`, open (P4-D476; OPEN-held on the lane's code `e59d5c1`, one run a size on a loaded machine, its projected peaks withdrawn; judged only from sizes reaching 1,000,000 rows, lane SX's night) (batch 4q's merges: lane TT's `K-S8-03` and `K-S8-05` added, both green, and its `K-S8-01` green, P4-D460; lane RO's `K-S6-06` added, open, a headline, P4-D459; lane ST's `K-BC-11` green, restated to the two reports and measured on the product's chain twin, and its `K-S6-04` widened to the two reports, P4-D458; lane ID-ROOM2's `K-HZ-06` restated, OPEN-held, owner lane ID-ROOM3, P4-D457, its stamp batch 4p's merged head's until the batch's records round; lane CZ-A's `K-HZ-14` added, open, P4-D445; lane CHs's `K-S6-15` added, open, P4-D462; lane SPD2's `K-HZ-21` added, green, and its `K-P0-10` restated by dated amendment, its two seconds unresolved until a whole suite is read against base run 1 (read at batch 4s's seal), P4-D461; batch 4s's seal: twenty-nine entries stamped from its nine proof runners on its fix head `85eb6754` (the reviewed head `ce75ec54` and the fix round's ten commits, code and tests; the proofs ran on the fix head itself), every key compared key by key with its last stamp (batch 4r's reviewed head's, and each lane's own for `K-HZ-22` to `K-HZ-30`), each move named in its entry, with the lane that moved it where one is named (measured where so said, else read so and not split by a run; the keys moved with no lane named are listed in STATE's carries): `K-HZ-16` OPEN-WORSE on two keys of one attack (`case_iso_zone_not_asked` and `case_iso_zone_not_held` 0 to 1: lane CZ-E's question holds the attack's answer column whole as an identifier, so it is neither put its dates question nor held by the dated-values rule; 0 real date elements shown and 0 twin cells carrying one; red at the stamp; ruled: the hold stands and the key's reading is the fault, lane CZ-H's); `K-HZ-14`'s two failing items none (lane CZ-A2's implant log fixture); `K-HZ-27`'s zone-word column read right on the merged line (lanes TR and DST); `K-HZ-19`'s recorded twin mean of a pooled number column moved (`code_per_person` 9.0041 to 23.4041 at 20,000 rows, the real 7.5878, not split by a run; at 600 rows, below the table floor, the form run puts the move at lane HB2's merge), a named fidelity cost, the first item of lane HB3-a3; `K-S4-09` stamped from batch 4r's own full driver on `820d55c3` (OPEN-held, 11.3 traced bytes a cell against 17.7); `K-P0-11` registered from batch 4r's final whole suite on `9545edee`, green, and `K-P0-10` read from it and not stamped (its two seconds above both bounds on a machine that was not quiet; the entry stands, a run on a quiet machine owed, owner the orchestrator, not a push condition); the chain's entries and `K-S4-23` not run on batch 4s's heads, at their stamps; batch 4r's seal: twenty-nine entries stamped from its nine proof runners on its reviewed head `820d55c3`, and `K-S6-02` and `K-S6-03` from the one on its fix head `59267e6b` (the reviewed head's run of those two stopped at clause (x), whose driver's wrapper the fix round repaired, and stamps nothing; `git diff` of the two heads over src is empty), every key, compared key by key, as its last stamp read it (batch 4q's, and lane BT3a's for `K-S6-02`) but machine kinds (seconds, peaks and their projections) and four named moves: `K-HZ-13`'s ratio of two timings, 1.96 against its bound of 2.5 (1.99 at batch 4q's stamp); `K-S6-02`'s clause (x), lane BT3a's (its reach grown by five tables, `scan_hits` 0 with its one accepted case named apart), and three wide tables' chains as batch 4q's lanes leave them (read so, not split by a run); `K-S6-03`'s coverage, lane BT3a's (92 twins and 645 families checked, 90 and 627 before); and `K-S6-13`'s projected footprints, machine kinds; `K-S4-09` on that head owed to its full driver, still running when the batch was sealed, and stamped from that run at batch 4s's seal; `K-S6-15` not re-run, its run owed by hand (P4-D462); batch 4q's seal: its proofs stamped on its merged head `b93f128a`, each entry on the head its proof ran on (`K-P0-01` by the seal's own run), but five that read RED there (`K-HZ-06`, `K-HZ-13`, `K-HZ-14`, `K-HZ-16` and `K-BC-11`); batch 4q's records round: twenty-one entries stamped from its second fix round's fifteen proofs on that round's head `c22837e6`, the five among them (`K-HZ-06` OPEN-held, every held date column 0 equal, merging and naming the same day, its zoo bounds restated to lane CZ-A's 154 tables and 311 identifier columns and the table the command refuses for the people floor counted apart, at most 1, none once lane CZ-A2 gives that fixture its 1,000 people; `K-HZ-13` OPEN-held, 1 invalid date string; `K-HZ-14` OPEN at its bounds, 84 items, 2 failing, the count lane CZ-A stamped, 0 complete real record tokens inside wider twin cells; `K-HZ-16` OPEN-held, its price's two bounds restated to the measured 28 and 9, 22 and 6 its targets, owner lane CZ-A2; `K-BC-11` green, no overclaim), and sixteen read every key as on the merged head but machine kinds (seconds, and `K-HZ-03`'s peak memory), all twenty-one standing for the records head, whose src is the fourth fix round's: the third and fourth rounds act only on a held date column's room, and their reach is null on every table each round measured (the third's 174 tables at the room's own call; the fourth's the same and the proofs' own 917 tables read cell by cell) and on those 917 tables read cell by cell against the second round's head at the records round, the 3 columns there that could enter a room asked at the room's own call and differing in nothing (the ledger's measurement note), and `K-S6-15`, not run, its run on the merged head owed (P4-D462); batch 4p's seal: its proofs stamped on its merged head `fc01f095`, `K-S6-12` on the seal's fix of its driver `f397dbdc`, each entry on the head its proof ran on; `K-HZ-16` and `K-HZ-20` on the fix round's head `ba87102b`, every key as batch 4o stamped them, where the sealed head's second list of key words had moved four of `K-HZ-16`'s keys and put ten fewer of `K-HZ-20`'s questions at 20,000 rows; `K-HZ-17`, `K-HZ-19` and `K-S3-65` on batch 4o's heads, their runs on the sealed head `d8f5e147` reading every key as stamped (`K-HZ-17`'s seconds aside); and `K-S6-05` on the sealed head `d8f5e147`, its three fixed-seed bounds restated at the fix round to the chain's twin's new figures, its meaning, no more whole real rows than a fresh real sample, unchanged), lane PL's `K-HZ-19` (green), lane SH3's `K-HZ-20` (open), lane CZ-D's `K-HZ-17` (open), lane CZ-H's `K-HZ-16` (open since the seal, LANE I4m RULINGS 20 (3)) and lane MPp's `K-S6-14` (green) among them; batch 4p's merges add lane BT2's `K-S6-03` (green, every fidelity key as lane BT2's head stamped it, its coverage counts restated with the cause the batch's merges give them, P4-D448) and lane MPg's `K-S6-12` and `K-S6-13` (both open, P4-D456). Of the 48 open, as each one's `target_stage` reads: 42 have the stage or lane that owns the whole (batch 4s's six: `K-HZ-23` lane KV, `K-HZ-26` lanes TR-e and TR2, `K-HZ-27` lane TR's zone-word reading beside lane DST's rule, `K-HZ-29` lane GRb2, `K-HZ-30` lane CZ-G and `K-S4-23` lane SX's night; `K-S6-06` lanes RD, RZ, GR, RO2 and CHON, `K-HZ-16` lane CZ-H2, the recorded keys batch 4o's merges moved on its five forms, and lane CZ-A2, its price's two bounds (P4-D445), `K-HZ-17` lanes CZ-B, CODES-2 and SX, each its stated limit (lane PL's part closed at batch 4o's stamp), `K-HZ-20` lane ID-ROOM2, on the orchestrator's ruling, its one record-number key, a live leak on the base too, and eleven of its twin's twenty misses at 20,000 rows, lane HB2 the other nine (two of a held county code's layout census; seven of a held column of ages written with a unit letter, whose twin the top-code writes in its own values since batch 4o's first fix round's generator change, `90y`, the top category, and `1079m`, the month below it, on 240 cells each equal to a real one, P4-D454), `K-P4-06`, `K-S6-01`, `K-S6-12` and `K-S6-13` stage 6, `K-S6-15` lane SX's named nights, measured there and never projected (P4-D462), `K-P4-22` stage 3, `K-P4-23` the carried reference vectors, `K-S1-06` and `K-S4-04` stage 4, `K-S3-64` lane HB2, its held padded age and `reglistmixR`'s own validation, `K-HZ-13` lane HB2, lane HB's stated limits, `K-S3-44` lane S4bc2, its one census miss, `K-S4-09` the scale gate, lanes SR, SG and SV, then SX, its describe part OPEN-WORSE on 589f3d72 in the night of 2026-10-27 under Python 3.11 (20.3 traced bytes a cell at 200,000 rows against 17.7, and 20.3 on batch 4l part a's head in the night of 2026-10-29 and on part b's 591b356f in the night of 2026-10-30; 20.4 on batch 4n's merged head 322b92de on 2026-11-04, traced peak 204,367,671 bytes, the first reading since 591b356f, so batches 4m and 4n together; 20.4 on its first fix round's head 7c0e8a26 (traced peak 204,368,975 bytes) and on its second, f18c3638 (204,366,849 bytes); 20.6 on batch 4o's merged head c47a6aee (traced peak 206,029,374 bytes), the describe-side changes of lanes PL, SH3 and CZ-H, not split per lane; its two fix rounds' small describe changes not traced, their reading owed; 20.6 on batch 4p's merged head fc01f095 (traced peak 206,037,794 bytes), with those rounds in it, its reading on batch 4q's merged head owed, and 11.3 on batch 4r's reviewed head `820d55c3` by its full driver, which finished after that batch's push and is stamped at batch 4s's seal (lane SR2a's own reading at its build head `afb48553`, not read again after its two repairs, 11.3 traced bytes a cell at 200,000 rows, P4-D463); batch 4j's head read 2,375 MB resident at 2,000,000 x 50 with every candidate open in the night of 2026-10-26, lane SX's to win back), `K-HZ-01` and `K-HZ-02` the lanes each zoo failure names, lane G2T2 for the one 20,000-row failure that had none at batch 4l, lanes CZ-H2 and CZ-B for the four batch 4o's stamp found (named at its seal, LANE I4m RULINGS 20 (2); 0 without an owner on `fcd01166`), lane MG for the person census and lane PS2 for what lane PS left held or pooled, `K-S6-02` lane BT3, its clause (vii) alone, the edge values left after lane BT2 restored its battery (P4-D448; batch 4m's merged code had moved it and `K-S6-03`, on the chain's switched path alone), `K-HZ-06` lane ID-ROOM3 (P4-D457), OPEN-held on a held birth-date column whose layout census is withheld whole, and lane CZ-A2, the zoo table its fixture holds below the people floor (P4-D445), `K-HZ-14` lane MG, the device log's lot in the people's union (P4-D445's limit (f)), and lane CZ-A2, the closed lists of codes the forms' rule holds until `no` (P4-D445's price), `K-HZ-10` and `K-HZ-11` as each reads, and `K-BC-01` to `K-BC-10`, `K-BC-12` and `K-BC-13` the broad between-columns program's checkpoint 4); 1 is owned in part (`K-2B-47`: stage 3 the carried fidelity items, lane RT2 the date remainder, 9 missed checks against its bound of 6; its identifier-layout residue of 2026-09-19 has no stage set); 5 have none set (`K-2B-28`, `K-2B-49`, `K-S3-12`, `K-S3-22`, `K-S3-50`). By stage: stage 3's `K-S3-01` to `K-S3-25` (`K-S3-11`, the tail leak, a headline), lane HX's `K-S3-64`, lane HX2's `K-S3-65` and lane AQ's `K-S3-66`; stage 3b's `K-S3-30` to `K-S3-32` and `K-S3-34` to `K-S3-62` (`K-S3-33` retired; `K-S3-31`, the weekday, and `K-S3-38`, time of day, headlines); stage 4's `K-S4-02` to `K-S4-09`, `K-S4-11`, lane SG's `K-S4-12`, `K-S4-15` to `K-S4-22` (`K-S4-10`, `K-S4-13` and `K-S4-14` reserved; `K-S4-03` a headline in `K-2B-14`'s place); stage 5's `K-S5-01`, a headline, and `K-S5-02` (lane S5a, P4-D437); stage 6's `K-S6-01`, lane BT's `K-S6-02` (layer L0's band totals behind the switch, P4-D429) and lane CHa's `K-S6-08`, the chain's tables part, green: no description its keyed draw can publish fixes or bounds a count of 1 to 10, the chain still behind its switch (P4-D418), lane MPp's `K-S6-14`, the moment layer under the owner's rule B behind the same switch, green (P4-D455), and lane CHv's `K-S6-04`, `K-S6-05` and `K-S6-10`, V12 checking each family behind the same switch (P4-D430), and lane RO's `K-S6-06`, a headline, rules between columns on the twin behind the same switch, open (P4-D459), and lane CHs's `K-S6-15`, the chain's describe at scale behind the same switch, open (P4-D462); the terminal's `K-S8-01`, a headline, and `K-S8-04` (lane TI), `K-S8-03` and `K-S8-05` (lane TT, P4-D460); the zoo's `K-HZ-01`, a headline, `K-HZ-02`, `K-HZ-03` and `K-HZ-05` (lanes E0a and E0c, P4-D431, with lane CZ-H's five forms, P4-D446: 98 kinds over 69 exports, judged at 20,000 rows with the shipped floor), 53 of 98 kinds passing and 158 failures over 45 kinds at 20,000 rows on batch 4o's merged head, on its first fix round's `fcd01166`, on batch 4p's merged head `fc01f095` and on batch 4q's merged head `b93f128a`, lane CZ-H's five forms among them (51 of 93 and 139 over 42 on batch 4m's merged code; 21, and 261 over 72, on lane E0c's head), every failure owned (the seal's two OWNERS lines, read on `fcd01166` and `fc01f095`), two of them since lane CZ-A's merge a stated price of its rule, owner lane CZ-A2, its first item (the PCORnet export's `DX` and `RAW_DX` no longer write their codes of nine figures, a form 11 or more of their real cells hold, which lane CZ-A holds whole as record numbers: the kind fails 3 checks at 20,000 rows on `b93f128a` where batch 4p's final head `f0ce1e06` fails 1; it holds more and shows nothing; P4-D445), lane CODES-3's `K-HZ-04`, the zoo's identifier cells out of pattern, 0, lane ID-ROOM's `K-HZ-06`, twin identifier cells equal to or merging with a real one, 0 over every key, the zoo's six held date columns 0 on lane ID-ROOM2's head, on batch 4q's merged head `b93f128a` and on its fix head `c22837e6` (P4-D457), OPEN-held on a held birth-date column whose layout census is withheld whole (P4-D432, P4-D434, P4-D442; owner lane ID-ROOM3, P4-D457), lane PS2's `K-HZ-07`, no date one to ten people or rows hold published, 0 over 60 tables (P4-D433), lane SH3's `K-HZ-20`, no age of 90 years or more published or written in any unit and no part of an address published, at 600 and 20,000 rows, OPEN on record numbers its values alone read as ages, 19,778 twin cells equal to a real one at 20,000 rows while their identifier question is open, as on the base, and on the twin's 20 misses at 20,000 rows, 13 older than the lane and seven since batch 4o's first fix round, all on one held column whose twin the top-code writes in its own values, as on 2af926ce (P4-D454), lane PL's `K-HZ-19`, levels one to ten people hold, none named, green (P4-D453), lane CZ-H's `K-HZ-16`, Safe Harbor dates in disguise over five invented forms, none shown and none in a twin cell, OPEN since batch 4o's seal on recorded keys its merges moved (owner lane CZ-H2; P4-D446) and its price's two bounds restated at batch 4q's records round to six of lane CZ-A's held identifier columns (owner lane CZ-A2; P4-D445), lane CZ-D's `K-HZ-17`, types, codes and flags over eight invented forms at 600 and 20,000 rows, OPEN on its stated limits (P4-D447), lane HB's `K-HZ-13`, held and unanswered columns' twins in their own valid layouts, OPEN-held at its stated limits (P4-D442), lane SPD's `K-HZ-15`, lane SH's Safe Harbor number cases at 20,000 rows, 0 failing over 61 (P4-D444), and lane CZ-A's `K-HZ-14`, eight Safe Harbor identifier forms and the variants repairs 1 and 2 read at 20,000 rows, 0 real values shown, 0 twin cells equal to one and, since batch 4q's fix rounds, 0 complete real record tokens inside wider twin cells, OPEN at 2 items the person census refused and 3 closed lists of codes only `no` frees (P4-D445); the analyst battery's `K-BC-01` and `K-BC-02`, headlines, and `K-BC-03` to `K-BC-13` (lane E0b). `K-2B-42`, the oracle's independence, is bounded since batch 4c by a share, at most 0.363 of its scored functions close to shipped code, a changed policy whose larger allowance the orchestrator accepted and named (P4-D299). **One command re-measures them all:** `.venv/bin/python tools/measurements/kpi_run.py` (add `--slow` for timings and scale). Run it at every stage close: **a KPI that drops is a regression even when every test is green** The ledger's byte bound rose once for this batch, from 1,100,000 to 1,200,000 (the orchestrator's recorded call D15; the owner may veto): lane ST's merge took the ledger past the old bound (1,110,710 bytes); 1,150,990 bytes with every lane of the batch merged, before its stamps; 1,154,215 after the seal's; 1,163,160 after the records round's stamps; 1,169,259 after its records of the third fix round; 1,173,601 after its records of the fourth; batch 4r's ledger 1,182,594 bytes with its three merges and 1,181,259 after its seal's stamps. The bound rose once more for batch 4s, from 1,200,000 to 1,300,000 (the orchestrator's recorded call D15; the owner may veto): lanes LM1, TR and DST merged under the old bound (1,194,040 bytes after lane DST's merge) and lane CODES-2's merge took the ledger past it (1,211,857 bytes); batch 4s's merges and owed items left it at 1,258,441 bytes, and its seal's stamps, its catch-up stamp of `K-S4-09` and `K-P0-11`'s registration take it to 1,281,035 bytes. |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan (since lane ARR-a, plan P4-D466, numpy's ten array names admitted in `synthtwin.arrays` alone under a closure rule, and the computer's reader in `synthtwin.computer` alone), the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request: Python 3.11 to 3.14 on Ubuntu and Windows and 3.14 on macOS, and the minimums job on 3.11 against the declared floors (lane DEP-1, merged 2026-10-20 at batch 4d, P4-D410, on lane MDEP's dependency page, P4-D409: the four runtime libraries numpy, pandas, pyarrow and scipy held to their byte-identity zones; until then five Pythons from 3.10). Since batch 4f (lane DEP-2, P4-D416) three jobs more, each required by `gate`: `bundle-build` (three platforms by four Pythons), `bundle-test` (four Pythons by three systems) and `numba-vectors` (three systems by four Pythons), 27 cells. Its first runs on PR #6 (2026-09-20) were red on what only CI could see -- tests asserting their own machine's answer, a 3.13-only spelling, Windows paths holding `AppData`, workbook cases failing where openpyxl is absent -- each repaired with a guard that now fails HERE. Batches 4h to 4j (pushed 2026-10-25) failed 26 of 86 jobs on CI-only causes, repaired by `8cd9b743` (the floor fixture steps aside without the package, the floor-of-eleven tests read the pages beside the test file, the bundle's invented table holds 20,000 rows; run 40274066871, 83 of 86) and `f677d6a0` (`K-S4-07`'s allocation bound 1.1, the gate's own allowance; run 40293692822, 86 of 86). Batch 4k (pushed 2026-10-26): run 40453073905, 86 of 86. Batch 4l (pushed 2026-10-29 21:00, both parts): run 40989180482, 81 of 86, red on Windows shard 2 (the stage-5 gate compared a next command's folder as text) and the minimums shard 4 (the zoo's leak scans read a workbook without openpyxl), both test-only, repaired at batch 4m (`e6b63074`). No job sets `timeout-minutes`, so each may run 360 minutes; local shards took 47 to 64 minutes at 591b356f, when shard 1 held lane SH's 45-minute test file (92.92 s since lane SPD, P4-D444, so those shard times are history), so the default stands, shards 1 and 5 watched (push critic 16). Batches 4m and 4n (pushed 2026-11-04 20:25 as one commit, `506249bf`): run 41955136439 on that head, success, 86 of 86. Batch 4o (pushed 2026-11-06 03:36 as one commit, `2018de5c`, with its records round after push critic 19): run 42196304205 on that head, success, 86 of 86. Batch 4p (pushed 2026-11-07 08:53 (-0600) as one commit, `d0eaa273`, on `2018de5c`, its tree batch 4p's final sealed head's): run 42383694868 on that head, success, 86 of 86. Batch 4q (pushed 2026-11-09 08:14 (-0600) as one commit, `97a28db0`, on `d0eaa273`, its tree batch 4q's final head `a391424c`'s): run 42632688161 on that head, success, 86 of 86. Batch 4r (pushed 2026-11-10 11:44 (-0600) as one commit, `658d2b13`, on `97a28db0`, its tree batch 4r's final head `548abf89`'s): run 42868109912 on that head failed one case of 2,783 on Python 3.14 on all three systems (`tests/test_stage4_describe_memory.py`'s notes memory case at 2,000 rows, 200.095 traced bytes a row against its bound of 200); lane CI-4r repaired it in tests only, merged in batch 4s after round HYG-1, measured under pytest on Python 3.11 and 3.13 only, its Python 3.14 readings from a verbatim copy of the case's helpers, so the run on the push that carries batch 4s is the evidence for 3.14. Batch 4s is sealed on its fix head `85eb6754` (its reviewed head `ce75ec54` and the fix round's ten commits) with its records; not pushed; its whole suite and every proof ran on Python 3.11 only, and CI judges the batch on the push that carries it. A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
| review | **ONE round per landing** (owner, 2026-09-12), `codex exec -m gpt-6-astra -c model_reasoning_effort="ultra" -s read-only`. Fix what it raises; never send the fixes back |

## What is being built, in order

Each line is a landing: one commit, one review round, scope frozen at
this page. Nothing starts until the line above has passed its gate.
Weeks are elapsed from 2026-09-12 and assume one builder.

| # | landing | gate | wk |
|---|---|---|---|
| 1 | **DONE 2026-09-13. The list idiom and the heap merge.** Generate at 20,000 rows x 20 numeric: 1,113 s to 19 s. Describe at 200,000 rows: 390 s to 10 s. Both linear now | MET: 9 output files byte-identical; `tests/test_no_quadratic_list_growth.py` turns red on the idiom, and KPIs `K-S1-02`, `K-S1-03` and `K-S1-07` hold the growth ratios | done |
| 2 | **DONE 2026-09-14. The three silent defects.** A grouped number keeps its mark, a moment keeps its separator, a date at midnight stays at midnight | MET: `tests/test_stage2_round_trip.py`, 19 shapes, every stage-2 fact returned. KPIs `K-S2-*` | done |
| 2b | **DONE 2026-09-19. The twin writes each column as the source wrote it.** Numbers keep their distribution and every common spelling; dates their own format; labels, text and missing values their spellings; record numbers and codes their layout; the file its dialect; Excel in and out. Every published count asks one floor rule. Owner rulings of 2026-09-17 built. Three review rounds closed | MET: the KPI ledger's `K-2B-*` entries, green or at their recorded ceiling, and the whole suite green | done |
| 3 | **DONE 2026-09-23. The extremes, and the population floor.** Its review round closed 2026-09-24. Built as FIVE landings on five branches from one base — 3.1 the default floor of 11 and the floor holes, 3.2 the population floor and the person rule, 3.3 the numeric tail, 3.4 the date and clock tails, 3.5 the sentences — and integrated last. No numeric, date or clock column publishes either end now; no sentence carries a count a key withholds. **Lane HX, merged 2026-10-20 (batch 4d):** a column whose question offers `identifier` and is unanswered publishes no value, and the twin writes made-up record numbers there, until it is answered (`K-S3-64`; P4-D401). **Lane AQ, merged 2026-10-20 (batch 4d):** the questions file keeps every answer across rounds, so the same answers given in one round or in several write the same description, summary, questions file and twin, and a run that would drop a kept answer, or read the table another way than the run that wrote the file, refuses and writes nothing (`K-S3-66`; P4-D408). **Lane HX2, merged 2026-10-21 (batch 4e):** on a table of several rows a person, every value published beside a declared or candidate person column is counted in people, and a column holding a value one to ten people hold is held whole, the twin writing made-up values there, except the rungs and tail boundaries of a measurement or code column not attached to its subject, which are still judged in rows (the orchestrator's ruling of 2026-10-19, item 2: on `K-S3-14`'s repeated-measures table a score still publishes two rungs, each on 11 rows of 10 people; the limit below); a column declared as counted dates whose cells did not read so is held on every table (`K-S3-65`; P4-D406). **Lane HX3, merged 2026-10-22 (batch 4f):** route four's person question offers `code` in its first round, so a code column the person knows is answered there (`K-S3-66`, `K-HZ-02`; P4-D420). **Lane PS, merged 2026-10-22 (batch 4f):** dates and times beside a person column are described at a coarser grain their published facts choose, counted in people, and a held one's twin writes valid dates in its own layouts (`K-HZ-01`, `K-S3-65`; P4-D417). **Lane ZR-a, merged 2026-10-23 (batch 4g):** the zoo-fix reading page, where each new reading stands in the classifier, the questions it adds and what it may publish, written before its code (P4-D419). **Lane HX4, merged 2026-10-23 (batch 4h):** a column of lists written as record numbers is asked one question and held until answered: the register lists of the exposure found that day publish 0 of 40 keys at 600 and 20,000 rows, pure and with one word (`K-S3-64`; P4-D424). **Lane POP, merged 2026-10-23 (batch 4i), the owner's table floor (P4-D425, amending 3.2's P4-D341):** `synthtwin profile` refuses, writing nothing, a table under 20,000 rows that hold a value, or under 1,000 people where a declared or answered person column repeats (spellings merged, `parsing.subject_key`); an open question never refuses; 3.2's 100 is reached only through `cli.main`'s internal `small_tables_refused`, which no option sets. **Lane MIN, merged 2026-10-23 (batch 4i, P4-D426):** the floor of 11 is a minimum: `--smallest-group` raises it, a number under 11 is refused writing nothing, and `generate` and `validate` refuse a description recorded under 11; the suite reaches lower floors only through `cli.main`'s internal `internal_smallest_group` (`tests/lowered_floor.py`). **Lane ZR-b, merged 2026-10-23 (batch 4i):** the zoo-fix stand-ins page, written before its code: stand-ins A1 to A3, rare values under Z1 (B), few-valued numbers (P4-D422). **Lane CODES-3, merged 2026-10-24 (batch 4j):** a UID column publishes only its organisation's root, a record number written as a decimal and a prefixed id keep their layouts, and plain prefixed keys, alone or beside words, are held through the identifier question: 0 of the zoo's identifier cells out of pattern (`K-HZ-04`; P4-D428); a twin identifier cell can still equal a real one by chance where the real values fill their room densely: lane ID-ROOM's (P4-D432). **Lane SH, merged 2026-10-26 (batch 4k, P4-D427):** ages over 89 read as 90 and ZIP-shaped numbers held while the Safe Harbor question is open, in every role (`K-S3-64`). **Lane PS2, merged 2026-10-28 (batch 4l, P4-D433):** on a table the command describes, a date one to ten people hold, or rows where no person column counts it, sends its column to a coarser grain or holds it (`K-HZ-07`). **Lane HX5, merged 2026-10-28 (batch 4l, P4-D436):** a column of whole numbers each on one row or in sequence, five figures or more or letters and five figures, is asked P4-D401's question and held until answered (`K-S3-64`). **Lane ID-ROOM, merged 2026-10-29 (batch 4l, P4-D432):** no twin identifier cell equals a real identifier of its column, by construction, as written and by the merged key, held columns included; where the real values fill a layout's room the twin's are written wider (`K-HZ-06`). **Lane E0c, merged 2026-10-28 (batch 4l, P4-D431):** the health data zoo widened to every kind of the zoo plan's section 6 (b), 93 kinds over 64 exports, judged at the owner's table floor, its general answers truthful (`K-HZ-01`, `K-HZ-02`, `K-HZ-05`). **Lane UN-1a, merged 2026-10-29 (batch 4m, P4-D438):** a number beside a unit with a level below the floor, or answered `measurement`, is read as the numbers it writes, and a unit column kept as labels is asked once (`K-HZ-08`, `K-HZ-09`). **Lane CODES-1, merged 2026-10-29 (batch 4m, P4-D439):** held-back codes are written in their published pattern (rule A1's pool in the commonest form, rule A2's positional census counted in people and refused where it pins a held-back spelling, rule A3's class split), and `=` is a mark (`K-HZ-10`, `K-HZ-11`). **Lane GG, merged 2026-10-29 (batch 4m, P4-D440):** a few-valued number column with a wide gap is listed, after `no` to its Safe Harbor question, as its own values, its mode pair met, and keys beside a placeholder of any share are held unanswered (`K-HZ-12`). **Lane SH2, merged 2026-10-30 (batch 4m, P4-D434):** years showing an age of 90 or more, places smaller than a state, coordinates and device numbers are put the Safe Harbor question and held until `no`; a top-coded age column holds no fact or cell above 90 (`K-S3-64`). **Lane UN-1b, merged 2026-10-30 (batch 4m, P4-D443):** a unit column is published as its bare numbers, units holding figures are read, and a decimal comma is read where the cells settle it, P4-D401's question first at five figures or more (`K-HZ-08` 9 of 9, `K-HZ-09` 0) | MET: `tests/test_stage3_gate.py` (`K-S3-13`) and `K-S3-01` to `K-S3-15`, and `K-P3-03` and `K-2B-05` reached their targets on the way | done |
| 3b | **Dates keep their calendar shape.** Weekday, time of day, heaps and schedules, each a new published fact that must meet stage 3's floor. **3b.0 landed 2026-09-28**: on the gate's 11 filled ranges of days, seconds and moments the twin comes back with as many different ones -- the same ones where each tail's derived end is the real end, and where one stands a unit past it that unit in place of a real one inside (4 of the 11, plan P4-D358); over small filled columns about three in ten come back with fewer, MISSED (known limits) -- and every rank of a merged run stays inside its gap except where no placement inside the gaps meets the published count of different values (plan P4-D354, `K-S3-30`, `K-S3-39`). **3b.1 landed 2026-09-27**: a column of whole dates publishes its weekday census (plan P4-D355), and its twin meets it -- admissions' weekend share 14.7 per cent real against 14.8 twin where it was 28.5; since 3b.D1 the full-fill certificate is gone and a census is withheld only where a group holds fewer than three different dates, fewer than seven and a half a group on average, or no room beside a published hole (plan P4-D365, `K-S3-35`). **In on the integration branch since 2026-10-02:** 3b.K, the base every landing builds on (P4-D364); 3b.D1; 3b.G1, every tail publishes its pair and a date or clock tail ends at its pair's reach (P4-D375); 3b.T1, Excel's hour and the 12-hour clock read and written back (P4-D370); 3b.R0, numbers written in full (P4-D380); 3b.R1, the day-or-month and date-code questions (P4-D381); 3b.R3, workbook cells read as stored (P4-D382); D0, one weekday pass for every census of bins (P4-D366); T2 (3b.2-H), the hour census on moments (P4-D371); C1 (3b.5), clock columns with their census, heaps, step and codes (P4-D373); G3, the count pass's paid merge keeping its book (P4-D376); G2, the tail pair's wider cell (P4-D377); R2a, dates no member reads written back as written (P4-D383); R2K, the second key cut (P4-D386); D1b, the weekday census withheld where the count leaves too little room (P4-D388); G4, the subtraction guard dropped (P4-D390); the route-2 correction (P4-D390, P4-D373); D2, the weekday census on timestamp columns (P4-D367); R4, numbers that are dates, read as dates and written back as the same counts (P4-D384); R5, a trailing delimiter on one side read as the table's (P4-D387); J, the weekday and the hour of a moment met together (P4-D379); D3, the day-of-month census (P4-D368); R2b and R2c, the clock half and partial dates of the layout reader with Q6 (P4-D383); D4s, the count pass splitting the two tails' ranks first (P4-D369 part one); D4 (3b.6), dates that stand out, each listed date at its exact count (P4-D369, `K-S3-45` to `K-S3-47`); 3b.7, the shared clock and the joint member, each census counted on the clock a value is written on (P4-D378, `K-S3-53`); L1, codes and tables written as the source wrote them (P4-D390, P4-D384, `K-S3-61`); T3 (3b.4), the minutes and seconds of a timestamp counted and met with the hour (P4-D372, `K-S3-41`, `K-S3-42`), merged through lane J2, which meets them beside the weekday census on moments (P4-D391, `K-S3-62`); C2 (3b.5's second step), the minute of the hour on clock-only columns (P4-D374, `K-S3-48`, `K-S3-49`); merged 2026-10-15 (batch 4a), J3, repeated grids of timestamps meeting their counts (P4-D391), R6, a trailing delimiter closed `""` read and written back as the source closed it (P4-D387), and L2, a clock's form holding the one space before its marker (P4-D392); and, merged 2026-10-16 (batch 4b), L3, a stamp's form holding the space between its date and its clock (P4-D393). **The gate is met for the weekday on date columns** (`tests/test_stage3b_gate.py`, `K-S3-31`, `K-S3-32`): weekend share and weekday come back and no weekday count stands below the floor; time of day has landed on moments (3b.2-H) and on clock columns with their heaps (C1), its minutes and seconds on moments (T3 through J2) and its minute on clock columns (C2), and the dates that stand out on date columns (D4); the 3b finish test is met at 254f6419 (both gate files green; `K-S3-31`, `K-S3-38` and `K-S3-42` PASS, `K-S3-41` accepted-held); schedules remain | weekend share, hour of day and heaps come back; no calendar count below the floor | 6 |
| 4 | **The numeric path per stratum, not per row.** The ladder work happens once per distinct value. **Under way.** Before batch 4a: a large table's reading memory, three paths grown with the rows, the packing walk bounded and G5.5's sign repairs (P4-D387, P4-D389; `K-S4-02` to `K-S4-05`). **Lane S4b-num, merged 2026-10-15 (batch 4a):** the dense tail's push, the identity walk, G4's decimal codes and a register's quality report grow with the rows, every twin the same bytes (494 s to 13.7 s generating 100,000 dense-tail rows; 803 s to 32.6 s for 1,000,000 rows of decimal codes; P4-D377, P4-D387, P4-D390). **Lane S4c, merged 2026-10-15 (batch 4a):** `validate` prints and writes its report in pieces (798 MB at 997,770 register rows where it held 1,317; `K-S4-06`), and a dense tail's twin meets its published mean distance (G6.6.8 rule 4, `K-S4-07`; P4-D390, P4-D377). **Lane S4d, merged 2026-10-16 (batch 4b):** `describe` holds one answer per spelling, every description the same bytes (the 2,990,700-row register in 780 MB where it took 2,389; `K-S4-08`; P4-D390); lane S4b-num's work counts have their own KPI since then (`K-S4-15`, the orchestrator's decision; `K-S4-09` to `K-S4-14` are reserved by the December plan). **Lanes H1 and H2, merged 2026-10-19 (batch 4c):** padded code and record-number columns generate in linear time (`K-S4-16`, `K-S4-17`; P4-D402), and the packing walk reads the counts of one margin together, so a column of signed changes no longer stalls `generate` (`K-S4-18`, `K-S4-19`; P4-D403). **Lanes SR and XW, merged 2026-10-20 (batch 4d):** `synthtwin profile` reads and describes a big table one group of columns at a time, every description the same bytes (`K-S4-09` open, its describe part worse on 8a02faa3 under Python 3.11, lanes SR-A's (P4-D414) and H3's; `K-S4-11`; P4-D400), and the workbook twin is written as a stream, the same file byte for byte (`K-S4-22`; P4-D411). **Lane G2T, merged 2026-10-21 (batch 4e):** a number tail meets its own description on big tables -- the shared staircase, rule 4 on a crowded end and the windows it draws -- and the twin writes nothing past the published range (`K-S4-20`, `K-S4-21`; P4-D405). **Lane SR-A, merged 2026-10-22 (batch 4f):** a big table's group is read again by pyarrow's CSV reader and handed over only where a digest proves it the standard reader's reading, every description the same bytes (P4-D414). **Lane SG, merged 2026-10-23 (batch 4h):** `generate` holds the twin once, each finished column packed and the twin written a piece at a time, every twin the same bytes (`K-S4-12`, recorded; P4-D415). **Lane H3, merged 2026-10-24 (batch 4j):** a column whose values all differ, and free text, are described with fewer objects a row, and the person answer's date questions are asked a group at a time, every description the same bytes; 2,000,000 x 50 read 1,420 MB resident with every candidate open and 1,386 MB with a declared person column (P4-D423). Open: `K-S1-06`, `K-S4-04`, lane S4b's calendar half, `validate` describing the file again (lane SV) and the number tails held by a width or the pair's reach, which keep the pushed staircase (lane G2T2; G2's dense tail at 1,000,000 rows closed by lane G2T, P4-D405, `K-S4-21`) | two million rows by fifty columns, end to end, under an hour (`K-S1-06`) | 8 |
| 5 | **The seam the interface needs.** Results become data with a rank decided once, before any sentence exists; a callable entry point returns results instead of printing them. **Its method is written, before any code (lane M5, merged 2026-10-19, batch 4c; P4-D395):** one result per run, its misses ranked once, an entry point that prints nothing. **Lane S5a, merged 2026-10-28 (batch 4l, P4-D437):** `synthtwin.cli.run` returns one result a run and prints nothing, `main`'s exit status is read from it alone, the rank is decided once (`src/synthtwin/results.py`); the golden battery is recorded once and reproduced under the provenance guard in CI; `K-S5-01` (headline) 53 of 53 cases told apart from the result alone, `K-S5-02` 0 of 255 records moved (recorded again at the merge). **Lane S5b, merged 2026-10-29 (batch 4l, P4-D441):** profile's questions and carried are data -- one record for each entry of the questions file, which is rendered from them byte for byte, the profile's tally, and what the written description carries; a column's time grain has its registry group. The summary stays rendered from the description (lane TW owns its made-up sentence) | a caller distinguishes a good run from a bad one without reading prose; reports byte-identical | 13 |
| 6 | **Cross-column: the chain of floored family tables** (P4-D407, which supersedes P4-D394's pairwise rank correlation over cut indicators), with the patient layer and the moments beside it. **Inherits:** today a rank correlation of 0.747 comes back 0.027 (`K-S6-01`), and the pairing walk of three- and four-number cells (`K-P4-06`). **Measured and written before its code (batch 4d, merged 2026-10-20):** lane E0b's analyst battery, what an analysis of the twin gives back against a fresh sample and a shuffled twin (`K-BC-01` to `K-BC-13`, two headlines; P4-D398), lane BTp's layer L0, each eligible column meeting its band totals (P4-D404), and lane MBC's chain, the between-columns method with its settings (P4-D407). **Written before its code (batch 4e, merged 2026-10-21):** lane MG's patient page, several rows per patient with the visit trend and the derived parents first (P4-D412), and lane MPOL's moment page, numbers read finer than the bands under a proof, with ruling R12's amendment of the chain's slopes (P4-D413). **Built behind its switch, with its oracle (batch 4g, merged 2026-10-23):** lane CHa's chain profile side, which no user reaches (`K-S6-08`; P4-D418), and lane CHo's exact oracle with the moment route's class `cho1` (P4-D421); on a switched run at the merge the product's bands, family tables, anchors and words equal the oracle's, its floor holds and RULE W1 holds on the oracle's reading over the merge's sub-bands. **Its validator behind the switch (batch 4k, merged 2026-10-26):** lane CHv's V12 checks a file against each family at layer L1 (`K-S6-04`, `K-S6-05`, `K-S6-10`; P4-D430). **Layer L0 behind the same switch (batch 4l, merged 2026-10-28):** lane BT, each eligible column at its published band totals, every shipped twin the same bytes (`K-S6-02`; P4-D429). **The chain's generator behind the same switch (batch 4m, merged 2026-10-29):** lane CHb, layer L1, every family table met at its published levels on the product's own twins, every shipped twin the same bytes (`K-S6-03`, `K-S6-05`; P4-D435) | every marginal unchanged; a known odds ratio comes back; the report names what it carries per relationship | 21 |
| 7 | **Higher-order structure.** Design pending measurement (four prototypes scored as this page was written) | a known three-way interaction comes back with the right sign, or the limit declared per relationship | 25 |
| 7b | **Higher-order structure, chosen.** A declared model plus one cross-tabulation for the outcome; the cross-column floor is ABOVE one, which is what lifts the reviewer's veto | a known three-way comes back at the real table's own estimate; no published cell names one subject | 25 |
| 8 | **The screen: DROPPED on 2026-10-15** (the owner: no screen; synthtwin runs in the terminal, with easy instructions and commands). The bundled toolkit, its scripting engine stripped, is not built. **The terminal takes stage 8's ids (the orchestrator's recorded call D15 of the December plan; the owner may veto it). Lane TI, merged 2026-10-16 (batch 4b):** one install command per system keeping the hash-checked offline install, `python -m synthtwin`, `synthtwin doctor`, and `profile` naming the next command (P4-D397; `K-S8-01`, a headline, open toward lanes TT and TS; `K-S8-04`). **Lane DEP-2, merged 2026-10-22 (batch 4f):** the hash-checked offline bundle, one zip a platform that CI builds and installs with the network denied, is the only install (P4-D416; the owner's D3: no PyPI) | the screen's gate went with it; the terminal's is `K-S8-01`'s, from a folder to a validated twin by the commands it prints | 33 |

**Eight months, one builder.** The estimate is deliberately not
optimistic: every estimate in the 2026-09-12 review came back from its
skeptic short by about two and a half times, and these are the corrected
ones.

## What the owner has decided, and must not be re-asked

- **The twin's definition above.** It replaces the floor-of-one
  reasoning, which it contradicts.
- **Both goals are mandatory.** Reliable statistics is no longer second.
- **Joins are out of scope.** Repeated rows per subject are not.
- **The twin writes everything as the source wrote it** (2026-09-15).
  This reversed ISO dates and every earlier decision that wrote
  otherwise, including judged placeholders written blank.
- **Excel workbooks and delimited text only** (2026-09-15). `openpyxl`
  is a TEST-ONLY dependency.
- **The eight rulings of 2026-09-17:** a record number's constant prefix
  is published where every cell carries it, per system; held-back rare
  labels publish a pooled total only; a workbook with a second table is
  refused and asks which sheet; missing words pooled below a raised
  floor count as absent; a label row recoverable by subtraction counted
  as missing, until the orchestrator set that ruling aside under the
  owner's principle of 2026-10-01 (plan P4-D390, reversible: a held-back
  level is pooled whatever its size); a spelling below the floor counts
  into the commonest; an ambiguous first row gets placeholder names and
  a question, and no record's text is ever published.
- **The rulings that set stage 3, 2026-09-22.** The default smallest
  group is **11** again (it was 1 since A-P4-37); since 2026-10-23 it
  is a minimum (the owner; P4-D426): raised, never lowered. **Written-form extremes stay published** — text
  length and word counts, identifier and unrepresentable lengths, joined
  part widths, the dialect pad width, subsecond digits: they say how a
  cell is written, not a person's measurement. **The column's own mean,
  spread, skew and kurtosis stay exact**, and a tail may carry the outer
  cells' mean and root-mean-square distance, although a lone far value
  can then be estimated closely — the owner weighed that against the
  twin's statistics and chose the statistics.
- **Accepted limits, 2026-09-18** (plan: "Owner decisions of
  2026-09-18"): real record numbers can reach the twin when a declared
  identifier has little spare room; held-back rare values can be rebuilt
  (63 of 251 cells, `K-2B-19`, accepted again on 2026-09-22: "just
  showing that the value exists is not an issue; what matters is not
  showing the relation in a descriptive file") -- and that ruling is
  about BOUNDED SCALES, so one rule asks its premise before any tail
  lists its values, on every role (plan P4-D346); **a warning whose
  count would hand back a withheld cell keeps the warning and drops
  the number** (2026-09-23, plan P4-D347), which is what brought the
  decimal-comma warning back on 1,199 grouped prices beside one bare
  cell; an autofilter can still make an ambiguous first row the header; a
  workbook date cell naming no day is read; free text's "one cell is a
  number" and a pooled label's one missing cell stay published (left as
  is once the owner's questions were answered, not accepted); and
  **the disclosure floor counts ROWS, not people** (2026-09-23, plan
  P4-D348), so a value held by twelve visits of one patient is
  published with its count -- 68 such values over three seeded
  repeated-measures shapes, held there by `K-S3-14`, while the
  POPULATION floor beside it does count people. And **a twin row may
  match a real row whole where a made-up identifier coincides with a
  real one** (2026-09-21: "Yes, it may be a real row!", confirmed
  2026-09-25; `K-2B-45`: 1 of 400 rows on each of two shapes, 0 to 7
  over 40 seeds); and **the readings trade on three- and four-number
  cells** (2026-09-21: "Accepted", at 609 outside and 3 missed;
  `K-P4-06` keeps its target).
  **Judge any such question by its effect on the owner's code and
  results; if there is none, do not spend time on it.**
- **Tail pairs, 2026-09-25 and 26** (plan P4-D353): a pinned tail's
  pair is published only where withholding it costs the twin its mean
  or spread ("Publish anyway", "Only where it costs", `K-S3-18`; the
  plan, not the owner, extends it to unsettled sides and orders the
  candidates). That rule is GONE since plan P4-D375 (2026-10-01, under
  the principle below): every pair binary64 holds is published, so
  nothing is withheld for a cost rule to weigh. A column's own values
  rebuilt from its description are
  accepted -- never another column, and never which row except on a
  table sorted by that column, whose `row_order` puts the k-th value in
  row k (told 2026-09-30: "Yes, it stands"): by the exact skew
  and kurtosis ("Accept it", `K-S3-17`: 65 of 110), by subtraction
  beside a published pair ("Allow it", `K-S3-21`: 701), beside a listed
  tail and from the whole description ("Accept both", `K-S3-23`: 24;
  `K-S3-24`: 14,115, 0 to 1,100 whole).
- **The principle, 2026-10-01** (plan P4-D363), in the owner's words:
  "This code should be reliable, with good statistical results for as
  many as possible statistical tests and this twin needs to be built in
  an accptable time. The only privacy concern is to not have a hippaa
  violation. ... We don't need to think that someone will try to
  discovery the data with the twin". Every guard that exists only
  against a reader reconstructing the data is re-weighed for statistics
  and build time, landing by landing (the orchestrator's reading).
- **"Keep as built"** (2026-09-29): the weekday certificate keeps its
  band and its 20,000-arrangement cap (plan P4-D359).
- **"Measure, then raise"** (2026-09-30): no cap up to 160,000 frees
  the 24 clinics it holds at about a minute each; under the principle
  the cap stays 20,000 in this push, the orchestrator's call (P4-D359).
- **"Accept as a limit"** (2026-09-30): a withheld weekday census may
  say a half of the week holds 1 to 10 rows -- a range, never a value,
  a date or a row (`K-S3-34`).
- **"Push now, add a guard"** (2026-09-30): the 134 commits pushed at
  `82b1f1a` stay as published; every new message is scanned (P4-D362).
- **"Yes, it stands"** (2026-09-30): "Accept both" answered a question
  that said "never which row holds them"; on a table sorted by the
  column, `row_order` places each rebuilt value in its row (P4-D353).
- **"Accept the class"** (2026-09-30): within one column, a count below
  11 worked out from several published facts is accepted; across
  columns, nothing is (P4-D363).
- **Asking the person is part of the product** (A-P4-56, A-P4-58).
- **Being synthetic is not an answer to an obligation.** The screen may
  not present the twin as settling a privacy rule. What it MAY say: your rows never leave this
  machine, nothing is sent anywhere, no model sees your data, and the
  files produced are yours to govern like any other export. Guarded by
  the seventh family of `tests/test_claim_inventory.py`.
- **The documentation regime is LEAN** (A-P4-40), and tightened on
  2026-09-12: stop producing text that describes the project. What is
  NOT cut: the tests, the reference vectors, the claim inventory, the
  decontamination scan, the KPI ledger.
- **Version 6 is extended in place** until the first release (A-P4-41).
- **The release is parked** until the tool has been used on real tables.

## What is broken right now

Each item is an OPEN entry in the KPI ledger, held at a ceiling so it
cannot get worse unseen.


- **Live HIPAA exposures found since 2026-10-23** (pre-existing). CLOSED:
  register lists, lane HX4 (batch 4h, P4-D424); short prefixed keys and
  padded ZIPs beside words, lane CODES-3 (batch 4j, P4-D428); ages over
  89 and ZIP-shaped numbers in every role, beside words or placeholders,
  answered `code`, `measurement` or `keep`, lane SH (batch 4k, P4-D427):
  0 ZIPs and 0 real ages over 89 in any file or twin over `K-S3-64`'s
  400 shapes at 600 and 20,000 rows, the column held until `no`; dates
  one to ten people or rows hold, lane PS2 (batch 4l, P4-D433;
  `K-HZ-07` 0); whole numbers one a row or in sequence (the zoo's `RPT`
  references, 19,998 of 20,000 copied on `ccebc947`), lane HX5 (batch
  4l, P4-D436); a made-up identifier equal to a real one by chance, lane
  ID-ROOM (batch 4l, P4-D432; `K-HZ-06` reads 0 over its 186 room shapes
  and the zoo's keys, at the width price below, and is OPEN for the
  held birth dates its zoo leg reads, named just below);
  keys of one width beside a placeholder of any share (`-99` on 2 %,
  `-1` on 40 %, `-1` and `-9999`: 60 of 60 keys printed and up to 19,617
  of 20,000 twin cells real on the pushed head), lane GG (batch 4m,
  P4-D440): held unanswered, 0 keys in their own facts; a top-coded age
  column beside a placeholder such as `999`, a typed `--date-count` on a
  ZIP-shaped column, years indicative of an age over 89, places smaller
  than a state, coordinates, device numbers and ages written `104Y`,
  lane SH2 (batch 4m, P4-D434); keys in free text and the label stand-in
  walk's keys, but limit (ae) below, lane HB (batch 4n, P4-D442, by
  construction; measured again on the merged head `322b92de` at 20,000
  rows): keys of four figures or more in free text (`num4000_comma`,
  LIVE on the pushed line: 4,000 real keys and 3,265 equal cells; keys
  1000 to 4999 joined by `;`: 4,000 and 3,265; padded keys among notes,
  in any script and at the table's floor: 9,998, 9,997 and 9 cells),
  keys read as labels with no question (`R100000` upward once each
  beside `pending` on 35 % of rows: 8,366 of 12,936 twin cells real on
  batch 4m's head, 8 on the pushed line; beside a published level of two
  to four runs: 7,202 to 11,253; beside a level holding as many rows of
  their width, or beside 400 levels of another form: 10,000 of 10,000
  and 9,604 of 9,800), beside key `3` a longer made-up run holding a
  real padded one (2,750 cells), made-up members of a held list
  (`reglistmixR`'s 4 cells of chance) and keys of two figures beside
  `-1` named as a key (20,000 cells): 0 now, each; and by batch 4n's fix
  round (P4-D442, Codex's review of batch 4n, by construction), two
  exposures new against the pushed line: UID-style keys written as dates
  by the date pass (`1.2.1000` to `1.2.2999` declared under the root
  `1.2.`: 260 twin cells equal to 26 real keys and 19,740 off the root at
  20,000 rows on the sealed head, none on the pushed line; beside other
  layouts, as identifiers or as free text, 90 to 1,229 cells) and list
  members carrying a real key of four figures (`R9000` beside `R10000`:
  the run `9000` in 20 cells, some real run of four figures in 2,178;
  keys of four to six figures, 3,898 cells merging with a real key): 0
  now, each, at 20,000 rows; and by batch 4n's second fix round
  (P4-D442, the independent verify of the first, by construction) list
  layouts with a field of four figures beside keys of three, every first
  figure held, written as the spill (1,172 to 3,504 twin cells holding a
  real key of four at 20,000 rows, none on `286c8ba6`): 0 now at 20,000
  rows; and by batch 4o (P4-D446, P4-D453 and P4-D454, measured on its
  merged head `c47a6aee`): ages of 90 years or more written in other
  units (months, weeks, days) and house, apartment, unit and suite
  numbers in the parts of an address, lane SH3 (`K-HZ-20`: none
  published or written at 20,000 rows); a person's dates that
  no column name or cell shape marks as dates, lane CZ-H (`K-HZ-16`: 0
  shown in any file and 0 in a twin cell over five invented forms and
  41 attacks, each column asked and held while its question is open);
  and levels one to ten people hold, pooled in people where such a
  level once held its whole column, lane PL (`K-HZ-19` and `K-S3-65`:
  none shown); and by batch 4o's fix round (P4-D453 and P4-D454,
  Codex's review of the sealed batch, items 1 to 3, by construction,
  through the command at 20,000 rows), three columns the batch's rules
  released that 591b356f and 2af926ce held: record numbers in a column
  whose name says age, held while their question is open or by the
  count in people (19,600 twin cells equal to a real key, and 19,442
  merging with one beside a person column, on the sealed head 015d5003),
  two-letter given names read as codes with no question put (four
  names published and 19,980 twin cells), and a person's declared key
  printed as a pool's start (`8888`: one description text and 20 twin
  cells): 0 now, each; the round's sibling sweep (LANE I4m RULINGS 21
  (6)) found two more of those classes, 0 on the same rules (each
  person's own number under `age_no` beside a person column, 19,442
  merging; one-letter initials, 19,980 twin cells), and one more
  release value by value, a held column whose cells put it in the age
  reach and whose name says age (`001` to `125`, unanswered: all
  20,000 twin cells on 54 real keys, where 2af926ce wrote the top-code
  `90` alone), the generator's fold of a held column named as ages,
  which it passes for no column now (P4-D454, method G7.14): `90`
  alone, as on 2af926ce; and by batch 4o's second fix round (P4-D453,
  the independent verify of the first, LANE I4m RULINGS 27 (1), by
  construction, through the command at 20,000 rows) first initials that
  are all yes-no letters (`Y`, `N` or `T` a person beside two `F`:
  published with no question put and 19,960 twin cells equal to a real
  initial on `fcd01166`, held on 591b356f and 2af926ce): 0 now, the
  column held and asked; and by batch 4p's merge of lane GRa (P4-D449
  beside lane SH3's rule, P4-D454, behind the chain's switch, through
  the switched command at 24,000 rows), a top-coded category few
  patients hold published in the patient table's block (five patients
  aged 92 to 101 in its high tail on the merged head): 0 now, pooled as
  the rows' description pools it; and by batch 4p's fix round (Codex's
  review of its sealed head, item 1, and its sibling sweep; behind the
  switch, through the switched command at 24,000 rows), cells the
  patient layer read as the file wrote them beside a description that
  top-codes them: ages 91 and 92 in a position list beside ages
  top-coded at 90, and years before 1937 in a position list (1925 to
  1936), an own mean's edge (1936.1) and a patient-fixed block (from
  1925) beside years top-coded at 1937: 0 now, each column read as its
  description read it (the round's scoped verify, by a counter of its
  own: 0 on 39 invented tables of 20,000 to 24,000 rows, six shapes of
  its own among them that the sealed head published too: a year of birth
  beside a stray cell, a run of years, ages in months past 1080, a run
  of 12 visits from 80, a first visit at 92, ages written with a leading
  space; a third gate case pins the list's first position, P4-D449);
  and on the shipped path, by the same round, a
  repeating key named `CSN`, `EMPI` or `uuid`, which the merge's second
  list of key words had left unasked (nothing real published where
  measured): asked again; and on the shipped path, by batch 4q's merge of lane TT (P4-D460), Enter
  at an on-screen question, read as `keep` (19,998 of 20,000 real record
  numbers in a twin of the skeptic's table at 20,000 rows): a defect of
  the public head, FIXED, Enter leaving the question open as nobody's run
  does (its gate cases `test_enter_keeps_the_record_numbers_held` and
  `test_enter_at_every_question_writes_what_nobody_s_run_writes`); and on
  the shipped path, by batch 4q's merge
  of lane ID-ROOM2 (P4-D457 part (b), C1), a defect of the public head,
  FIXED: sequential keys with a
  constant prefix and suffix (`P200000Q4444` upward), read as affixed
  numbers with no question put (19,998 of 20,000 twin cells real at
  20,000 rows on the public head `2af926ce`): asked and held, 0 real
  twin cells and none of their figures in a written file (its gate
  case `test_c1_keys_with_a_prefix_and_a_suffix_are_asked_and_held`); and by batch 4q's merge of lane CZ-A (P4-D445), eight Safe Harbor identifier forms
  the zoo did not test, answered a reading that publishes (`code`,
  `keep` or `measurement`, the person question `keep` for every column):
  on the base `2af926ce` at 20,000 rows each form's column was published
  whole -- social security numbers, member numbers, names beside record
  numbers, tokens, serial, accession and unit numbers and identifiers of
  16 and 19 figures 1,000 of 1,000 real values in the description and
  20,000 of 20,000 twin cells equal to one each, a partner's numbers 666
  and 13,320, the lots 40 and 20,000 -- and three of them were put no
  question; and on the lane's first head `7808fd75` seven variants of
  them (another dash or a small letter after a social security number,
  base64 tokens of 24 characters, a name beside a labelled number, UDIs
  in square brackets, unit numbers with a check character, accession
  numbers in two undashed layouts) 1,000 real values and 20,000 twin
  cells each, and long numbers among shorter, read as a count, 1 value
  and 20 cells; and on repair 1's head `bde23570` seven spellings more
  (UUIDs, identifiers stored as a spreadsheet's number cells, accession
  numbers the year first with their dash or with a dash after their
  capitals, a name with a sole initial or a curly apostrophe, serial
  numbers in a column named `sn`) 1,000 and 20,000 each: 0 now over
  `K-HZ-14`'s 38 items at 20,000 rows (OPEN at 2 the person
  census refused, nothing written, and 3 closed lists of codes the
  forms' rule holds until `no`, the price, lane CZ-A2's); and by batch
  4q's fix rounds, before any push, two defects of the batch's own line
  found by the outside review on its review head `29fdf3aa`, each new
  against the public head, with the neighbours the first round's verify
  found and one sibling on the public tree: names beside record numbers held
  as identifiers kept only the whole cell, so complete real record
  numbers stood inside wider twin cells (46 on the review's table of
  20,000 rows, 1,000 people of 20 records each, and 46, 46 and 47 with
  the number glued to its label, after `#` and a label or before a
  letter; none on batch 4p's final head), and the public tree's own
  sibling, a blood unit's sequence beside its facility code (40 such
  cells on batch 4p's final head): a run of five figures or more inside
  a value of two words or more now opens as no real run of its width
  opens, 0 on each (P4-D432, P4-D445); and a held date column's room for
  made-up years ignored date spellings the product's own reader accepts
  (`Jan 01, 2028`) and two-figure ones it does not (`Jan 01, 28`, `Jan
  01 '28`, `28-01-01`), so the twin wrote real singleton days as dates
  (8 of 11 on each such table of 20,000 rows; none on batch 4p's final
  head): each of those readings now holds its years, 0 on each (the
  classes still open are stated below)
  (P4-D457); the glued and two-figure tables measured by the second
  round's builder and re-derived by its scoped verify, which closed
  31 tables of record numbers and fifteen more neighbours of the date
  spellings, and found a class of date spellings, compact stamps and a
  clock written first (8 real days written for each of six compact
  stamps on the second round's head, none on the public tree), which fix
  round 3 closed for the spellings its generator writes save four
  classes: of 153,450
  generated spellings that name a year of the room, 23,589 were open on
  the second round's head and 720 on the third's, every one in the
  four classes stated below; a spelling the generator does not write is
  not measured by it (P4-D457); and the third round's verify found four
  families of the product's own date vocabulary open on the third
  round's head (a zone or a meridiem glued to a stamp's run-on clock,
  `20280101091530Z`; Excel's serials and Unix seconds, `46753`; a day of
  the year, `2028001`: 8 of 11 real days written on each such table of
  20,000 rows, Excel's serials withheld 7 of 10; SAS's datetime,
  `01JAN28:09:15:30`, ten cells withheld leaving 2028 in the room), none
  on the public tree, whose twin of the same table publishes no room and
  writes about 11,753 cells equal to a real ISO day by chance: fix round
  4, the last round of date spellings, reads the four families as
  P4-D457's rule states them (0 days and no
  room on each such table) and writes them into the generator (SAS's
  datetimes with a year of four figures or a two-figure year from 28,
  the day of the year with no clock), whose
  232,596 spellings hold 197,442 that name a year of the room, 3,902 of
  them open, every one in the four classes, where the third round's head
  left 5,836 open outside them; the room is claimed closed for the
  generated spellings save the four classes, which take in the four
  families of the product's own date vocabulary the third round's verify
  found open in the forms the generator writes, and for nothing more
  (P4-D457's stopping rule). The orchestrator applied that stopping rule
  to what the fourth round's own verify then found, two forms of those
  families the generator does not write still writing real days and a
  price the round had not named, each stated below with its numbers and
  its reason, and further spellings of the product's date vocabulary are
  the next batch's first work (LANE I4q RULINGS 26).
  Their price, measured at 200,000 rows: the record numbers' rule within
  noise, the date rules about 1.9, 0.3 to 0.4 and 0.7 CPU s more a held
  date column (the second and third rounds' in interleaved pairs) and no
  increase measured for the fourth on the mixed birth dates (interleaved),
  at most 3.2 CPU s more to describe 200,000 births 40 per cent in one of
  its families; PROJECTED (linear, a quiet machine) at 2,000,000 x 50
  with a few such columns, under 0.02, 0.01, 0.01 and 0.03 CPU hours for
  the date rules' four rounds and 0.01 for the record numbers' rule.
  And by lane CZ-F (P4-D478, `K-HZ-30`, measured at 20,000 rows on its
  head): a column of persons' names with no record number and no person
  column beside it, under a neutral name or one that says a name, a
  patient's, a clinician's or a staff member's, written apart or run
  together in capitals (1,000 of 1,000 names published and 20,000 of
  20,000 twin cells real on the public head), held whole and put the
  Safe Harbor question in the spellings the reader reads (a comma,
  given name first, a health message's name field, every space and
  dash of one definition; under a name that says one, a family name
  alone with a suffix or none, one or two of them held as sixty are):
  0 shown and 0 real twin cells; its residual classes (names in small
  letters or a script with no capitals, single names and fewer than
  100 names under a neutral name, a share under two in three of the
  values read, staff headings outside the closed list, names inside a
  wider text) owned by lane CZ-G.
  OPEN, each with its
  owner and its numbers, none of them claimed closed: three exposures
  of the public head that batch 4r's records name, none new in batch 4r
  and none made worse by it (an invented column of each shape, 20,000
  rows of 1,000 people, writes the same description, questions file,
  summary and twin bytes on the public head's tree `a391424c` and on
  batch 4r's sealed head, measured by batch 4r's records verify): a
  column that holds
  only persons' names
  (one name a person, for example `Family, Given`) under a neutral
  heading, with no record number and no person column beside it, is
  read as categories and published whole (1,000 people of 20 rows each:
  the description shows all 1,000 names and 20,000 of 20,000 twin cells
  are real names, measured on the public head's tree by lane CZ-A2's
  statistics check; beside a person column the column is held), owner
  lane CZ-F, its first item (lane CZ-E's reader of names by their values
  leaves this shape published, its limit (a)); a column whose levels are
  ages written with a word before the
  number (`Age 18` to `Age 95`, one a person) is published with no Safe
  Harbor question, `Age 90` to `Age 95` included (84 people, 1,680
  rows), and the twin writes them, measured on the public head's tree
  by lane CZ-A2's skeptic (an age word after the number, `95 yrs`,
  `95y` or `95 years old`, is read today, P4-D434 and P4-D454), owner
  lane HB2, with lane CZ-E's age bands; and a held stamp column read as
  plain, `+HH:MM` or
  UTC stamps writes made-up stamps from the years 2000 to 2029, so a few
  twin cells fall on a real birth date by chance (1,000 patients born
  1928 to 2005, 20 rows each: 80 of 20,000 twin cells fall on 3 real
  birth dates, each held by one patient, on batch 4r's reviewed head and
  on lane TR's, measured by lane TR's skeptic; the date-only column is
  placed in the made-up-date room and reads 0), owner lane TR, its fix
  under way, and lane ID-ROOM3; a column whose
  every cell is `#MR` and a record number (one value a row, 1,000
  people of 20 rows, nothing declared or answered), read as an affixed
  number: its twin writes 19,999 of 20,000 cells equal to a real cell,
  merging with one too, on batch 4p's final head `f0ce1e06`, whose tree
  is the public head's, as on both fix heads (the same label without
  the sign, `MR` or `MR-` and the number, is held: 0 equal), lane CZ-A2,
  its first item (P4-D445); a column whose every cell is a family name,
  a given name and a record number joined by commas with no space
  (`Cedar,Abc,1000000`, 1,000 people of 20 rows, nothing declared or
  answered), read as an affixed number: its description publishes 1,000
  person prefixes (`Cedar,Aab,` and on, each count 20) with their record
  numbers' statistics, 1,000 real seven-figure runs in it, and its twin
  writes 18,000 of 20,000 cells equal to a real cell and 1,998 more
  holding a complete real record number, the same on the public tree
  `d0eaa273` as on the records head `a9228c17` (batch 4q's push critic),
  lane CZ-A2, among its first items (P4-D445 (3)(g)); four classes of the generated date spellings
  the fourth fix round leaves open, 3,902 of the 197,442 that name a
  year of the room (720 of 153,450 on the third round's generator; a
  spelling the generator does not write is not measured by it), each a
  reading whose year stands where common
  layouts put a day or a year's own figures, so that holding it would
  take the room of every held column of those layouts: a two-figure year
  of 31 or less written first beside a month's word (`28-Jan-01`,
  `28JAN01`, `28 Jan 01`), read year last as its layout's orders read
  it, which on the outside review's construction (eleven such days
  beside 19,989 ISO births, 20,000 rows) writes 8 real days each as ISO
  dates, 9, 9 and 8 twin cells, on the second fix round's head as on the
  first's, unchanged by the third and the fourth, none on the public
  tree `f0ce1e06`, a two-figure year above 31 so written being held (42
  generated spellings); a two-figure year between the month and the day
  that reads as a day (`01-28-05`; 32); a compact run with its year
  between the month and the day (`012805`; 3,476); and a three-figure
  year in a compact stamp, its clock run on (`02801050915`; 352); lane
  ID-ROOM2 (P4-D457); spellings beyond the generator, each a stated
  limit by the last round's stopping rule (beyond the product's own date
  vocabulary, not shown written by an export, or naming no year of the
  room, or, for SAS's two-figure years below, not new against the public
  head and writing fewer of its days), lane ID-ROOM3 (P4-D457):
  month words outside English (`01-ENE-28`: 8 real days, 9 by a broader
  reading), roman months (`01.I.28`: 8), ranges of days (`Jan 1 to 4
  '28`: 8), a month alone (`202801`: the room holds 2028 and 22 twin
  cells name January 2028, at seeds 0 to 3), and letters glued to a
  date's run and the rare compact forms (`DOB20280101`, `028001`,
  `12801010915`, `28010109`: 8 days each), each on the outside review's
  construction at 20,000 rows, measured by the third round's verify and
  read the same on the fourth round's head, none on the public tree;
  measured by the fourth round's verify, a day of the year with its
  clock run on in its figures (`28001091530`, `20280010915`,
  `280010915`, `2028001091530Z`, `28-001091530`: 8 of 11 real days
  written as ISO twin cells on that construction, on the fourth round's
  head `15c89b3b` as on the third's, none on the public tree; no export
  in the product's vocabulary is shown writing it), an hour alone run on
  a date of a two-figure year with a zone or a meridiem (`28010109Z`: 8
  of 11 real days; `28122511PM`), and SAS's datetime with a two-figure year of
  00 to 23, read as the hour, where the two-figure room wraps past 99 as
  it does by design (on a table of 20,000 rows that wraps it, ten such
  cells of January 2003 withheld beside `dd-Mon-yy` and `dd Mon yy` days
  of 2009 to 2027, the room `[[0, 7], [28, 99]]` holds 03 and the twin
  writes 3 of the ten real days, and 3 and 2 of ten such cells of 2000
  and 2001, where the public tree, which has no room, writes 8, 4 and 8);
  and, not measured by the generator, a zone glued to a compact date
  with no clock (`20280105Z`), a day of the year in six figures, counts
  outside the count grammar (grouped, in brackets, with a plus) and a
  zone word outside the clock's list glued to a stamp's clock
  (`20280101091530IST`); a run inside a value of one word, which keeps
  the whole-key exclusion, a fragment at chance (the forms' `specimen_accession`,
  `block_ref` and `slide_ref` 20 cells each, `MR` and a record number
  48, the same on batch 4p's final head), lane CZ-A2 (P4-D445); list keys beside a
  real key of one figure, the spill as before (20 to 1,550 cells at 20,000
  rows), and lists mixed with lone keys under a published letter, the lone
  layouts' fillings short and the rest the spill (on ten shapes at 20,000
  rows: 0 cells equal to a real key and 0 merging with one, where the
  pushed line writes equal cells on four of them, 558, 1,780, 3,602 and
  697; cells holding a real run of four figures or more inside a longer
  made-up number, a fragment, 177 to 1,020 on six shapes where the pushed
  line writes 356 to 4,596, and 397 to 865 on four where it writes 34 to
  495), lane HB2 (P4-D442), not a blocker of batch 4n (LANE I4m RULINGS
  16); day-first dates
  written with points and a lone figure, read as record numbers, written
  by the final pass and not as valid dates (the fix round's price), lane
  ID-ROOM2 (P4-D457); keys of two letters before their figures, or with
  letters after them, in lists are no list keys and their twins hold a
  real run inside (122 to 415 cells at 20,000 rows; 60 equal for keys of
  three figures and a letter after; the same on the pushed line), lane
  ID-ROOM2 (P4-D457); a held date
  column's made-up dates equal to real ones BY CHANCE, MEASURED
  (`K-HZ-06`'s zoo leg on `fcd01166`, as on `c47a6aee` and `f18c3638`, each column at its own bound: the
  five birth-date columns lane SH2 holds, 7,055 and 7,656 of their cells
  on the two-figure `registry_extract.dob_short`, each twin matching the
  same table drawn at another seed as often as its own; since lane HB's
  merge `tumor_registry.dx_date`, month-and-year dates lane HB's rule 10
  writes as valid dates, 3,138 twin cells equal to a real date at 20,000
  rows against 3,186.5 expected by chance; the description prints none;
  on the pushed 591b356f, role `datetime`, the five held 51,476 and
  52,971 such cells and 189 real date spellings stood in its outputs),
  lane ID-ROOM2 (P4-D457), whose head and batch 4q's merged head
  `b93f128a` read 0 on those six columns at 20,000 rows (equal, merging
  or naming the same day); it stays OPEN, owner lane ID-ROOM3 (P4-D457 repair 2 (3);
  `K-HZ-06` OPEN-held), for a held birth-date column held in people whose
  layout census is withheld whole (a rare layout held by too few people):
  its G1 floor draws from its grain's span, 17,513 to 17,517 of 20,000
  twin cells equal to a real birth date by chance at 20,000 rows and
  validation exiting 3, the same on the public head `2af926ce`, no birth
  at or before the cut named; a held column's date layout of figures
  alone with a two-figure year written as record numbers at the table
  floor whatever its real years, and with a four-figure layout beside
  it the whole column, and a held column whose census withholds a pool
  of the other year width, whose years take the named kind's block,
  written as record numbers too: a held date column of an ordinary
  table written as record numbers, no value of it real, the twin
  validating (P4-D457 (b), the price LANE ID-ROOM2 RULINGS 5 (2)
  accepted), lane ID-ROOM3; the held padded age `naaccr`, held
  unanswered, its twin writing `00090` in every cell and its two failing
  twins counted apart in `K-S3-64`, lane HB2; from lane HB's close round
  2 (P4-D442's limits), label columns holding two key forms, or a number
  on the pooled scale, whose held-back numbers keep their spelling there
  (limit (ae), on the pushed line's code too: `R` keys beside bare
  six-figure keys 1,391 and 2,780 twin cells real at 20,000 rows, 1,393
  and 2,782 on the pushed line; bare seven-figure keys 1,391 real and
  2,781 holding a real run; two code shapes 202 and 2,694 holding one,
  3,685 and 4,118 before; the pooled scale's moments and percentiles
  print numbers of the keys' range), lane HB2; the spent-room fallback's
  noughts, limit (af) open at the original width (keys zero-filled from
  nought beside a word write their one real key of noughts alone, the
  first of the sequence, as itself: 497, 1 and 267 twin cells at 20,000
  rows on three shapes, one real value each; the pushed
  line wrote 62 other equal cells on the first shape, so a net
  reduction), lane HB2; keys of their published levels' own form held on
  49 % of rows beside 400 such levels (9,794 of 9,800 twin cells holding
  a real run at 20,000 rows and 2 equal, chance among 9,800 held keys
  written from the same place lists; 208 and 0 on the pushed line, the
  same on batch 4m's line before lane HB), lane HB2, not a blocker of
  batch 4n (LANE HB RULINGS 13 (4)): closing it needs a rule that moves
  G1's code columns; the identifier route's stand-ins carrying a real
  key inside a wider run or under another letter (padded keys beside a
  note on 60 % of rows: 6,901 of 7,882 twin key cells, 7,879 equal on
  the pushed line; 2,182, 1,116, 155 to 218, 65, 6,022 and 378 on other
  shapes; keys asked at a published share of 50.05 to 70 %: 217 to 351; the UID
  shape `u_codex`: 7,560 twin cells holding a real run of four figures
  inside a five-figure stand-in, the same on 591b356f, f39334aa and
  7c0e8a26), lane ID-ROOM2 (P4-D457); 23 twin tokens
  equal to a real key in held cells of two keys, lane HB2; record
  numbers that lane SH3's age reach reads as ages, held while their
  identifier question is open, write 19,778 twin cells equal to a real
  record number at 20,000 rows, all on one constant value, as on the
  base (`K-HZ-20`'s `register_entry`), lane ID-ROOM2; the carries of
  batch 4o's two fix rounds (LANE I4m RULINGS 23 (3), 27 (3), 28 (2)
  and 30), each at 20,000 rows: after the answer `no` on a column of
  numbers that is no key, a pool's constant start, which never reads
  the data, is printed and written on one person's 20 rows where it
  equals the column's one rare value (`8888` beside the key `8889`, or
  `88` beside levels `1` to `5`; a rare `7777` or `77` gets the same
  start and 0 equal cells), a column the public line 506249bf held as an
  identifier with no question put and the person said identifies no
  one, under the accepted limits of 2026-09-18, lane HB2's first item
  (P4-D442's stand-in rule applied to a pool after `no`); made-up
  record numbers merging with a real key of
  the person column, 24 and 22 cells, a chance across columns, as on
  506249bf, lane ID-ROOM2; first initials holding one yes-no pair or
  one such letter, and a column `kind` holding `No` and `Yes`, `No`
  alone or yes-no words and letters mixed, each beside letters or names
  one person each, released with no question where 506249bf held them
  unasked: every published level held by 495 people or more, no rare
  value published, 19,800 twin cells equal to real cells of those
  levels on each of 13 shapes, two candidate rules priced and not
  applied, lane HB2; the held `age_letter` (ages written with a unit
  letter, its identifier question open): 257 twin cells equal to a real
  cell, 240 of them the top category in years and the month below it
  (`90y`, `1079m`) and 17 one made-up value equal to a real age by
  chance, as many as on 506249bf, none a record number or an age past
  the top category, lanes HB2 and ID-ROOM2, its seven validate misses
  among `K-HZ-20`'s twenty, the ledger's bound, since `1b60d5fa` (eleven
  lane ID-ROOM2's, nine lane HB2's); the top-code's constant on held
  columns of short numbers named as ages, `0090` on 19,778 cells
  (`0001` to `0125`), `90` on 19,778 (`1` to `125`) and `90` merging
  with the real `090` on all 20,000 (`001` to `125`), as on 506249bf,
  lanes HB2 and ID-ROOM2; a made-up `999` in `age_padded07`'s twin, 270
  cells, none real, lane HB2; and plain `1` to `2000` under `age_no`,
  `age_ref` or `age_code` with no person column, read as counts with the
  age question put first, lane ID-ROOM2 (P4-D453 and P4-D454 name
  each); and the moment layer under the owner's rule B (P4-D455,
  behind the chain's switch) publishes no count of 1 to 10 directly, a
  count worked out by combining several of its rounded statistics
  being the residual the owner accepted, its twin meeting the
  published moments through lane MPg's polish since batch 4p
  (P4-D456), `K-S6-12` OPEN on its named pair; and from batch 4p,
  behind the chain's switch, three rules of the rows' description the
  patient table does not take (dates in disguise a question holds turn
  the patient layer off; an age column's unit answer, read in years
  there; a column too few people fill, ineligible there), measured
  through the command at 24,000 rows with no value fewer than 11
  patients hold and no age or birth year past the top category
  published, lane GRb's stack (P4-D449), which also carries a source
  column named like the layer's census, `(rows per patient)`, that
  stops the switched profile (Codex's review of batch 4p, item 2;
  nothing published), one named like the layer's own-mean label, whose
  derived column is then not drawn (nothing published wrong), and a
  twin generated from a switched description that holds the layer,
  which stops with an `IndexError` (no twin written; measured on
  Codex's table, 24,000 rows); the layer turned off where the
  description set placeholders aside, inferred a decimal comma, held
  dates in disguise or read ages written with their unit, lane BT3a,
  whose reader replaces that gate; the method's two sections numbered
  G7.15, lane CZ-H2 (P4-D449); and two combinations of
  published facts the owner's principle of 2026-10-01 accepts, each
  named with its owner: a column almost every row of which is nought,
  whose few other values its published facts solve to (19,995 noughts,
  3 ones and 2 threes at 20,000 rows, the same with the switch off),
  lane MPp2's question (P4-D455), and on the shipped path a count
  column's upper end counted in rows (one patient's 900 visit rows
  worked out from three published facts), the table layer's, lanes
  MPp2 or HB2, if the owner wants it closed (P4-D449). A code
  column's 779 rare held codes come back as they are, privacy-neutral.
  Keys under five figures beside words over one value in three, lane
  LISTS (ZR.9); a candidate person column repeating a few values leaves
  the real table missing its own repetition pattern: validate of a real
  table against a description that holds a column as record numbers
  misses `identifier.n_distinct_by_occurrences`, the held description
  publishing a made-up repetition pattern, and exits 3, on every commit
  batch 4q's diagnosis measured, lane PS3.
  Batch 4s's merges and fix round, each of these the same on the public
  head as measured: THREE CLASSES OF CHARACTERS publish ages past 89 at
  20,000 rows and 1,000 people through the commands, unanswered, each
  the same on the public tree `548abf89` (the merged line's combined
  sweep of 23 reader entry points by 43 marks in 7 positions, 628,814
  variants in the owed positions, 9,024 missed): (X1) age bands written
  with the soft hyphen U+00AD for the dash (`90<U+00AD>94`), which lane
  CZ-E's band reader reads as a space only, are read as categories with
  no question, 18 levels published, `100+` among them, and 20,000 of
  20,000 twin cells real (the same bands written `90-94` are top-coded
  and asked), owner lane CZ-G; (X2) bare ages with a character that
  prints nothing at a cell's edge (`<U+200B>95`), whose edges the age
  reach's number reader cuts by Python's whitespace and not by the one
  definition: 87 levels published with every age 90 to 104 and 3,220 of
  20,000 twin cells past 90 (the control `95` top-coded at 90), owner
  lane HB3-a, its repair 1; and (X3) the same character inside the age
  word (`Ag<U+200B>e 95`), 87 levels published, owner lane HB3-a (each
  owner to close its readers by the one definition, its acceptance a
  generated sweep of the owed marks and positions; the batch closed two
  neighbours: `95<U+200B>years` held, 0 real cells where the public tree
  writes 3,220, and bands with a doubled space before the unit
  top-coded). Two exposures of the public head that lane LM1's verify
  measured at 20,000 rows, the same bytes on batch 4r's reviewed head,
  owner lane ID-ROOM4 (planned as plan P4-D489, not yet written): C4,
  codes spelt with one figure, a
  small `e` and an exponent of three figures from 400 (`1e400` to
  `9e622`, ten rows each), written as 20,000 of 20,000 twin cells equal
  to a real code (with a capital `E`: 0 equal as written and 19,459 of
  19,459 once case is folded); C5, a second person key read as a number
  once the person's other codes are answered identifier (`P100000` to
  `P101999`, 2,000 people of ten rows each, read as an affixed number
  and offered identifier unanswered: 19,990 of 20,000 twin cells equal
  to a real key; left blank, or with the codes answered measurement, the
  key is asked and 0 real keys are written). Lane HB2's C5: a tail
  block's bin group that the count in people's rounds never enter is
  published though 1 to 10 people hold it (a top-coded age column beside
  a declared person column, 1,000 people of 20 rows: bin group 0, 100
  rows, whose interior rows belong to 5 people; a one-decimal
  measurement of the same values alike), the same on the public head,
  owner lane HB3-a2, its first HIPAA item. Lane CZ-E's C1, limit (k):
  adult age groups under a generic name are read as no ages, so on 1,000
  people aged 25 to 104 2 or 3 bands past 89 are published and 3,900
  twin cells equal one, unanswered and with no question, the public
  tree's numbers again on the fix head (the merged line's reach had
  top-coded them and the fix round restricted it, P4-D472), owner lane
  CZ-G, its first item, re-measured in lane CZ-H; and its C2, a
  character that prints nothing inside a run of figures, read as a space
  that parts the run (5 of 15 such cells unread at the unit level),
  owner lane CZ-G. Until these land, the owner's guard (the how-to): a
  column that may carry characters that print nothing (copied from a web
  page or a document) is cleaned first; a column of age groups past 89
  or of coordinates written with hemisphere letters is declared with
  `--identifier`, held whole, or left out of the export; and every
  record-number column, the patient key included, is declared in one
  command.
- **Unit and decimal-comma columns read as labels, in part** (lanes
  UN-1a and UN-1b, P4-D438 and P4-D443, `K-HZ-08`, `K-HZ-09`: restamped on the merged head, see the ledger).
  A suffix unit with a level below the floor, and any affix reading
  answered `measurement`, is read as numbers and published exactly as
  the same numbers written bare; units holding figures (`10*3/uL`,
  `mL/min/1.73m2`), units written each one way (`kg` beside `lb`) and a
  decimal comma the cells settle (`36,9 °C`, `72,5 kg`, `25,5`) are read
  too; a comma the cells cannot settle (`2,5`, two picks `3,11`, three
  figures after it) is asked (Q-COMMA and its mirror); five figures or
  more before every comma (`1002345,7`) is P4-D401's question first, at
  any count of keys, a measurement so written costing that one question
  (read with the comma once answered `keep`). Still open, each
  with its lane: rule 7's templated and list stand-asides (`5'10"`,
  `37+5`; `E11.9;I10`), lanes UN-2 and LISTS; a two-pick list whose
  second picks stand nowhere else, or written larger first (`15,3`, 3 of 3 seeds at 600 and 20,000 rows), read as decimals, lane LISTS; weights with 30 % whole cells inferred but failing validate on six facts at 20,000 rows (the same with points), lane G2T2; `<0,5` beside `1,2` categorical at 20,000 rows, lane UN-2; clock
  forms read before rule 7 (`HHMM`, zone words), lane TR; at 20,000 rows
  the zoo's temp misses its count of values by one generator placement
  (`035,2 °C`, the same with points), lane G2T2. Below the table floor
  (600 rows) a unit column whose value one to ten people hold is held
  whole by lane HX2's count in people, as its bare numbers are. Values
  beside a lab's flag (`4.4 H`), lane UN-2.
- **A published `mode_count` the twin misses on a column of numbers outside
  lane GG's class** (batch 4m, P4-D440, method G12.16; `K-HZ-12` counts
  the class at 0). A column of many values (503 weights at 20,000 rows:
  103 published at the mode, 83 written; lane S5a's step-0 table, its
  weight answered `no`, 17 against 10 at seeds 0 to 2 on batch 4m's
  merged code) or a gapless scale (4,076 at `3`, 4,000 written) is named
  in the twin's report, not met; a listed tail beyond the last published
  rung is written evenly (a heart rate's 102 to 109 on 22 each, real 42
  down to 8); a MANY-VALUED column beside a code (a weight to one decimal
  beside `-99`, 717 values) keeps its old twin (`-99.0` on 950 to 1,207
  cells, 14 to 191 cells in its published gap, a mean of 72.7 against
  78.1): owner GG2. Lane GG's own class -- few values with a wide gap --
  lists them only after `no` to its Safe Harbor question (unanswered, the
  twin of before), which the zoo puts to 4 more columns at 600 rows.
- ~~**The description names individuals; spread too wide on normal
  columns.**~~ **CLOSED by landing 3, 2026-09-23** (`K-P4-22`, `K-S3-11`,
  `K-P3-03` GREEN). `K-S3-11`'s residual, open by choice since P4-D375
  (14 edge-pinned and 8 pinned tails of 105 cases give back that tail's
  own outer values), is accepted under the owner's principle of 2026-10-01.
- **Relationships between columns are not carried.** Landing 6. The moment page written for it (plan P4-D413) states its own limits before any code: a refusal's residual under ruling R3; "own facts" as rulings R9 and R11 read them (a union that splits one column's small group across two regions counts that group's rows, 1 to 3 rows measured, while inside one region the witness refuses the measured cases where that reading would publish a count of two columns, exactly 3 rows and 1 to 9 rows); every published moment needs a proof (ruling R10), so none stands beside a slope the chain publishes outside its regions; the witness December can decide publishes almost nothing on the measured 50-column table (one region of 20 number columns and 38 of 50 families, every number column in a family where a slope may stand), the main fidelity risk before the stage-6 gate: with the witness `cho1` no region publishes, so no moment and (R12) no slope: 115 of 287 estimates at 200,000 rows on the seeded chain, against 134 walked with slopes, 202 polished and 213 for a fresh sample (P4-D421), E0b's ST2 to ST6 chains measured with the chain alone at 20,000 rows on one key (lane CHa2, P4-D451 (4), each table's owner named there) and ST1's at 200,000 rows unmeasured (lanes MPp and CHa); the oracle's moment comparison (4.6d) has never run, since the product publishes no moment (lanes MPp and CHb); and no average or correlation of a repeated measurement in December. Under ruling R12 (2026-10-20) the chain's slopes are published only inside a publishing region of the moment page, so while its GATE stays closed no chain slope is published in December, on any table (P4-D413, contract 4.6d.10's limit 6; 19 estimates at 200,000 rows, P4-D421). RULE ONE_BAND's few-value columns and `w_te` are settled behind the switch (lane CHa2, P4-D451: the rule built; `w_te` decided at nought on the product's twins at 20,000 and 200,000 rows). The chain's profile side (P4-D418) owes, each with its owner (the orchestrator, 2026-10-22 17:46 and 2026-10-23 12:17): the subject question on a table of several rows a subject before stage 6, lanes MG, GR and ST; an independent check of 4.6b.8's cell-by-cell row hash and the sample key, which the oracle does not compute, lane CHb (built: its oracle hashes a cell of spaces and tabs as the empty text, and lane CHa's `chain.row_hashes` changed by one line to meet it, behind the switch). THE CHAIN'S GENERATOR, layer L1 (lane CHb, batch 4m, P4-D435), is built behind the same switch: every family table met at its published levels on the product's own twins (`K-S6-03`), whole real rows beside a fresh real sample (`K-S6-05`), every shipped twin the same bytes (the zoo at 600 rows, 192 files, and the goldens, at the merge). Its limits: a switched description of 1,000,000 or 2,000,000 rows cannot be made under any guard, `chain.describe` holding the whole table (lane CHa's follow-up with `K-S6-15`, before lane SX's scale gate; the generator at 2,000,000 rows projects to 1,976 MB); label scans that may grow quadratically at 2,000,000 rows, unmeasured (lane SX); and a stamp written inside its grain (lane PS2's date floor) was dealt at the grain's start and spelled inside it only as it left, so its family read back off G16.6's table (the encounters' `discharge_ts` at 20,000 rows, measured at batch 4m's merge): lane BT2 closed it (P4-D448: such a date is dealt by the band its written text reads in, so the encounters' family meets G16.6).
- **Cells of three or four numbers** sit at 552 of 2,160 pair agreements
  outside their window and no above-count missed (lane G2T's shared
  staircase, P4-D405), the ledger's ceiling since batch 4f's records,
  against a target of 550 and 0 (`K-P4-06`, whose note keeps how stage 3
  moved it). The pairing walk is the open cause. Landing 6. The same
  walk lets a column of two numbers whose pairs repeat write more
  different cells than it publishes: the stage-5 every-role table's
  `pressure` at 20,000 rows, 601 published and 3,143 written, so its
  `validate` exits 3, as on the public line 591b356f before the yield
  (on the public line 506249bf the yield read the column as its list;
  P4-D438's batch 4o paragraph).
- **Clock and calendar limits, each with its owner** (written in one
  place at batch 4g's records, 2026-10-23, from the eight bullets that
  held them; the cases and figures behind each stand in the plan
  decision named; the owners are the orchestrator's rulings of
  2026-10-08 to 2026-10-16, the owner may reverse any).
  - *Stated, no lane named.* Moments in the joint member, wholly at
    midnight, without both tails or with a middle half under four days
    still spread over the day, where a column on its own clock meets
    its hour census (P4-D371, `K-S3-38`). The twin's own check fails
    on one shape each: two date-width allocations, one identifier
    layout, a sign band given more slots than it has numbers (the
    ledger's known-miss entry). Each held by
    `tests/test_stage3b_gate.py`: a date or clock tail's derived end
    stands one unit past the real first or last value, a real one
    fewer inside (12 of 36 cases, P4-D354); of 316 twins of 158 small
    filled ISO columns, 90 hold fewer days, both distinct counts
    missed; a range filled but for a declared-missing unit comes back
    a unit short (6 of 600 twins); a tail rank whose stratum is one
    declared-missing day, month or quarter writes an absent cell
    (about 1 twin in 40 at a floor of 11, 1 in 5 to 1 in 3 at 36) or a
    present day one more than published (4 of 596 day-first twins at
    36); a moment counted in minutes on a member with one mark is
    written with an absent spelling (9 of 25 twins); and where the
    count pass's splits break a tail's summed window a count G12.5
    holds exactly is missed (6 of 1,200 twins at a floor of 50)
    (P4-D358). ISO moments at midnight come back a day short where the
    count pass merges, no check missed, so `validate` cannot report it
    (5 of 2,360 twins with one mark, 2 of 549 with both; strict xfail
    in `tests/test_stage3b_split_order.py`; P4-D367, P4-D369). Of 21
    weekday censuses on logs just above one row an open day that cost
    their twins a different value, 1 still does, beside the
    Tuesday-to-Thursday clinic at 11 (P4-D388, `K-S3-59`); seven-day
    logs holding every day stay one to three values short and fifteen
    Mondays at 36 stay long (strict xfails); the workbook date system
    moves the rules only where a column's first value is the system's
    first day (not built). On the shared clock (P4-D378) the count of
    different values stays in G12.5's envelope, its shortfall said
    (C1's c0 and c551 hold 99 to 177 for 63 and 83).
  - *ACCEPTED.* A far cell one figure wider than every real cell (382
    of 1,080 padded twins; none wider than 110cb46's, `K-S3-22`), so
    code reading such a column at a fixed width may meet one wider far
    cell (P4-D377). An all-different column of 800 ISO datetimes and
    200 ISO dates comes back 999 of 1,000 at 11 and 998 at 36, inside
    the envelope, said in the twin's report. A 10,000-row `HH:MM`
    column with 203 `UNK` is read as clock times under the answer
    `missing` and asked at 11 and 36, and at 36 at 300 and 1,000 rows
    the question is not put (strict xfail; P4-D383). R4's `%.15g`
    column writes 990 cells at midnight and passes because the check
    of a count withheld for its size reads either side. The payers'
    walk grows 2.04 to 2.16 times a doubling, and a wall of more than
    1,024 payers that keep nothing still ends a search
    (`_CLOCK_PAYER_REACH`), the count one value short. A clock-only
    column's minute census is asked over the fine table too (P4-D374):
    the clinic column at 1,000 rows is withheld and at 36 comes back
    0.515 on `:00`/`:30` against 0.706 (0.673 published), the silent
    distortion ruled worse.
  - *Lane S4b.* Moments at a million rows short of their hours, each
    said by a deviation: a clinic 767 ranks of 1,000,000 off, noon
    stamps over 118 days 2,344, ward rounds missing their hour census
    alone (P4-D379); the day pass at 67 per cent of generating against
    a budget of half at 40,000 rows (`K-S3-44`).
  - *Lane 3b-REST* (its clock half lane RT1, its calendar half lane
    RT2). A 12-hour dial column read at UTC whose offsets carry the
    instant past local noon or midnight exits 3 (offsets allocated
    before the instants, P4-D383). On the shared clock (P4-D378):
    consecutive-minute stamps beside bare dates come back 754 to 805
    of 1,000 values (strict xfail); `z_plus` withholds its weekday
    census at 1,000 rows and at 10,000 at 36; bare dates under an hour
    census capped at hour 0 are written as moments (98 of 100 at 400
    rows, 2,498 of 2,500 at 10,000; `resolution_mix` missed, strict
    xfail), and dates sharing days with stamps are spread evenly over
    the span. `wide_three_mid` comes back 647 against 644 at 36,
    `n_at_midnight` a named deviation (G7.3h, P4-D378); a
    declared-missing spelling withheld below the floor is still
    written on tail ranks (109 of 400 at front 400, 23 of 60 at 60;
    P4-D369). Beside a weekday census the hour pass leaves a small
    bursty table's count long (83 of 105 twins, G7.3g step 6,
    P4-D391); the half-hour grid misses `second_heaps.counts` in 2
    twins; a daytime grid with a few night stamps at 11 misses its
    count (982 to 1,046 written of 1,024 to 1,057; the J3 verifier's
    weighted draw the starting point); a state probe with payers on
    both sides ends one value short at a wall of 40; NF74's unit-room
    rule withholds a noon census the twins now meet. Lane RT1's: 500
    stamps five minutes apart at 36 come back 496 to 500 values, and
    1,000 half-hour stamps with 60 % of the slots empty wrote 1,001
    values in 1 twin of 8.
  - *Lane D5.* A daylight-saving column's twin writes the offset not
    in force on its date for 50 to 52 % of its rows; the remedy,
    publishing each key's first and last day (P4-D378).
  - *Lane C2.* A clock column's cells of the other hour width on an
    absent place written in the column's width (P4-D373, strict
    xfail); route 1's 198 blank cells over 2 columns, to go under the
    corrected route-2 ruling; the label twins' hour-of-day distance at
    small tables (P4-D390).
  - *The forms lane FM.* A stamp beside rare words is written in its
    source's shape (P4-D393) but reads as no date like every held-back
    stand-in (`7000-00-01 26:23`); a `T` stamp whose marker alone is
    lower case is written `AM`; a stamp with a month word, a compact
    date, an offset after a space, more than 32 characters or a comma
    after the date keeps no form (a year-first stamp's `Z` or offset
    keeps its `T` and `Z`); a zone after a year-last date keeps no
    stamp form; free text of zoned stamps misses `length.mean` at a
    floor of eleven by G9.5's length pin.
  - *Lane L1.* R4's whole counts written with a needless exponent come
    back in full (P4-D384).
  - *Lane J2.* D2's older fault (b), the leap-second columns' count of
    different values and count at midnight (P4-D379), and a local dial
    column just after midnight (00:00 to 00:08, written 12:mm) missing
    `n_distinct`.
  - *Closed, the rules that closed them.* A column nine in ten at
    midnight with fewer cells than the line off 00:00:00 withholds its
    minute and second facts (NF123, NF124); regular stamps crowding
    their lattice withhold them (NF121, NF122) and dense grids of
    random times keep them; a repeated grid publishes them under the
    looser fifth only where no value is written once, no count at
    midnight is published, it holds at most 1,000 values and its
    lattice stands on midnight (lane J3, P4-D391: the 93
    grid-and-floor pairs of 1,001 to 2,500 values that met now
    withhold, and of a 512-grid sweep 254 pairs that missed now meet
    and 372 that met lose them; drawing such grids at their own phase
    could keep them, untested, not built); the minute and second
    censuses stand on the shared clock (P4-D378, P4-D391).
- **Stated limits given their owners at batches 4c to 4e (2026-10-19 to
  10-21)** (the orchestrator's rulings and namings on those batches'
  critics and reviews; the owner may reverse any). J3's six published
  pairs that still miss (stamps five minutes apart written four times at
  floor 11, P4-D391): lane RT1. On Windows PowerShell 5.1 a printed
  command drops an empty value, and `doctor` weighs total memory, free
  memory being unreadable without native code: lane TT (P4-D397).
  `K-2B-47`'s date remainder, 9 checks missed against its bound of 6:
  lane RT2 (P4-D320). `K-S3-44`'s one census miss: lane S4bc2 (P4-D368).
  `K-2B-42` is bounded by a share, 0.363 of its scored functions close to
  shipped code, a changed policy the orchestrator accepted (P4-D299). The
  zoo's mixed result column's mean, which `validate` misses: lane G2T2.
  A column of signed changes whose style question has no answer keeps the
  cell walk's styles: lane FM (P4-D403). The install scripts run on
  Windows and macOS only in CI, the offline bundle the only install
  (P4-D416). Lane SR's and H3's describe costs (P4-D400, P4-D423): the
  100 bytes a row asked of record numbers and stamps, the mixed table's
  heaviest describe now a clock column (370 bytes a row), a wide note
  column read alone (about 408 s a column at 1,000,000 rows): lane SX
  (speed; lane SV's describe-once the first cut); the grouped describe's
  peak, bounded at 0.6 of the whole table's (0.462 on H3's head, 3.11),
  the register's peak of about 245 MB a million rows and a text whose
  sightings past the bound are over 8,192 new texts apart answered once
  a row (P4-D390): lane H3's, merged at batch 4j (P4-D423);
  workbooks past `workbook.MAXIMUM_CELLS`: lane XL. `analyst_kit.chi2_sf`
  0.7 % off at 69,295 degrees of freedom and p 0.5: lane E0L (P4-D398).
  Each code the zoo's SNOMED twin writes being a real one: a `codes`
  check only names meet, lane CODES-2 (ZS.2). A column a
  point-between-thousands answer declared, asked again under
  `read_as_now: measurement`: lane HB; a questions file whose kept
  reading entry and name list are both deleted or both edited alike:
  lane AQ2. A column declared as counted dates with no present cell is
  named nowhere: lane ST (P4-D406). What stage 5's result reads for the
  chain: lane CHv (P4-D395). Lane HX2's (P4-D406): the pages that explain
  the floor still say a value one person holds is published with its rows'
  count, lane MG; a table of ten people or fewer whose person question is
  open counts the columns not attached to its candidate in rows, the
  orchestrator's to decide since lane PS (P4-D417); the identifier
  generator missing published forms on held twins (`GENERATOR_LIMITS` in
  `K-S3-65`'s driver): lane HB; the zoo's person censuses pooled by lane
  HX2's count in people: lane MG (the census in subject bands).
- **Types, codes and flags on eight invented forms** (lane CZ-D,
  P4-D447; `K-HZ-17` OPEN-held, measured on batch 4o's merged head).
  Lane PL's pool in people (P4-D453), merged beside it, closes limits
  (3) and (4): no rare count published, every filter share kept and no
  present count of a near-empty column (`rare_counts_published`,
  `filter_share` and `blank_share` 0 at 20,000 rows), its
  spelling count read with P4-D453 (g). What stays: date-times pooled
  in people lose their whole minute (limit (1), lane CZ-B), a stand-in
  in the column's own width and the words a column may publish (limits
  (7) and (8), lane CODES-2), and the wide mart's unjudged time (limit
  (2), lane SX).
- **A code a person holds once loses its attachment** (measured on
  lane PL's head, P4-D453): the twin's people hold several values of
  such a code, 99.4 to 99.6 per cent of them, where no real person
  does; a fidelity item, nothing real shown; lane GRb, which attaches
  cells to people.
- **Ages in days beside held day counts are written moved** (lane CZ-H,
  P4-D446 limit (k), merged in batch 4o). The date rule keeps such ages
  (limit (h), wired at the merge), but method G7.15 moves a twin's numbers
  off the date bands without the unit's oldest age, so the column's twin
  ages are written off the bands and `validate` misses its percentiles,
  tails and mean (exit 3 at 20,000 rows; nothing real is shown or
  written). The widening's frozen oracle vector is not built, so no frozen
  case reaches the oracle's mirror of the widening. Both are lane
  CZ-H2's first two items, the method and its oracle moving together;
  three spellings of a date the rule does not read (an ISO week date, a
  date run together after a letter, a date in quotes or brackets; held
  whole while asked, P4-D446 (l)) are lane CZ-H2's too, and so are a column the person says counts
  days from a date, held as the date element it is with its twin's
  made-up numbers off its span (the zoo's perioperative serial dates
  fall after 2030, so its check of them is one case expected to fail,
  strict; P4-D446 (m)), and the recorded keys `K-HZ-16` moved at batch
  4o (OPEN, P4-D446 (o)). The day-number form's charges stay blank
  after their answers `measurement` and `no` (17,626 of 20,000 cells
  at 20,000 rows, on the lane's own head too; P4-D446 (n)), lane
  CZ-B's.
- **Dates and times beside a person column, pooled in people** (lane
  PS, P4-D417, merged at batch 4f). Such a column is described at a
  coarser grain its published facts choose, or held with a twin of
  valid dates in its own layouts; no count of one to ten people is
  left to subtraction, and absent spellings stay absent. Still so,
  each with its owner (lane PS2, P4-D433, kept each of lane PS's
  follow-ups below as a named limit with its reason, none built: each
  changes the count in people or a published census; their owner is
  lane PS3, which the orchestrator opens after lane PS2 merges (its
  ruling of 2026-10-25 13:22); the owners the orchestrator named on
  2026-10-23, written at batch 4g's records): a stamp of a few evenly filled hours misses its count of
  different values and its count at midnight (`wearables` at 20,000
  rows: 32 of 39 hours, 1,208 rows at midnight against 515), lane PS3;
  a measurement attached to its person (`labs`' `viral_load`) is held
  whole with made-up numbers in its layouts, lane PS3 (no date: outside
  lane PS2's columns); the time of day and the weekday of a stamp
  pooled at the day or coarser beside a person column are not described
  (admit hour TVD 0.37 at 200,000 rows; the census of hours in people
  holds the floor, the fewest 378 people an hour at 20,000 rows, but
  every day-by-hour cell a draw would read holds one to ten people,
  so the hours must be drawn apart from the days: a new census, its
  proof under R10, the draw and its oracle) and the pooled tails are drawn inside
  their end bucket (635 rows on one day against 80), lane PS3; a birth
  date beside about four people a year is held with no span and drawn
  from 2000 to 2029, lane PS3 (a rung of five or ten years, a new rung
  of TG1, the draw and the oracle); the missing spellings of a pooled
  column print as the base's held block printed them, lane PS3; a held column's length no valid
  date has is missed and named (three people's `pending`: `min_length`
  7 against 10), restated by lane HB (P4-D442, `GENERATOR_LIMITS`); a stamp with
  UTC offsets publishes no count at its rung, lane DST; a table of ten
  people or fewer whose person question is open still publishes per
  rows (P4-D406's limit (2)), the orchestrator's to decide.
- **Dates counted in rows where no person column counts them** (lane
  PS2, P4-D433; the rule in stage 3's row). Still so: it reaches tables
  of 20,000 rows and more, and below the floor the library keeps its
  bytes (581 stage 3b cases would turn red), a date-floor rule the
  orchestrator confirmed on 2026-10-25, identifier rules holding at
  every size; a blank person cell on a table of one row a person is its
  own holder; a clock time of day beside no person column is counted by
  the row floor alone; a date written as a number nobody declared is
  not reached; a column of dates held in PEOPLE is still put the date
  question Q6, lane PS3; a stamp on the shared clock pooled at a rung is
  drawn inside its local bucket, so the offsets shape's twin misses two
  points and its weekday census at 20,000 rows while the real table
  meets them, lane DST (P4-D417); a column described at a grain spends
  one draw a row, so the twin's later columns are drawn again (9,984 of
  20,000 cells of a two-level column beside 20,000 consecutive days, its
  description and counts unchanged); a column of dates beside the
  candidate of an open identifier question, of fewer than the floor's
  values, is held until answered (4 date columns of the zoo's 24 tables
  at 20,000 rows, each restored by the zoo's general answers).
- **Lists of record numbers (lane HX4, P4-D424), still so:** values no
  route reaches (names, dotted ICD codes) or lists split by `+`, `^`,
  `~`, `/`, `.` or `;;` (the last three: 1 of 40 at 600 rows, 13 twin
  cells), and a held list written without its mark (11 of 600 twin
  cells against 398), lane LISTS'; codes `101` to `106` in lists
  published as categories, as before;
  `all_whole_numbers` beside one list cell, CODES-1 part C's; prices: `1,0001` decimal
  commas and a count column with one `a;b` cell held until answered.
- **Safe Harbor years, places, ages and devices** (lane SH2, batch 4m,
  P4-D434; close rounds 1 and 2 on 2026-10-29). While a column's Safe
  Harbor question is open: years of birth showing an age of 90 or more
  against this release's year (2027; raised each year, the gate's
  tripwire goes red on 1 January 2028) are one group ("1937 or
  earlier"); a column named as a place, a ZIP area, a GS1, HIBCC or
  ICCBBA device identifier, coordinates and places beside their states
  are held whole until `no`; a top-coded age column reads every
  placeholder (`999`, `-1`, `-88`) blank and a value past 125 as 90 (up
  to three such values the floor's rows repeat are set aside); ages
  written `090Y` are read in years; no reading typed on the command line
  frees a ZIP-shaped column. Still so, each with its owner: a birth-date
  column holding a date at or before 1937 publishes no date (lane PS3);
  a place column whose name says nothing of a place, lane CODES-2; four
  values past 125 beside ages, each on over one row in twenty; a DICOM
  age of months, weeks or days answered `keep` one cell off a published
  level at 600 rows (lane PS3). The price, by design: the zoo's city of
  birth and UDIs answered `yes` fail the analyst's checks of their real
  values (on the merged head `K-HZ-01` 51 of 93 kinds passing, `K-HZ-02`
  139 failures over 42 kinds at 20,000 rows, every one owned). Any
  zero-filled whole-number column the age reach takes collapses to one
  value, off its width and its count of values, unanswered only: at
  20,000 rows `naaccr`'s age padded to three figures writes `00090` on
  19,587 cells, a lab value beside `999` writes `00090` on 19,621 cells,
  a score `000` to `100` writes `90`, an age padded to four figures
  writes `0000090`, each with validate exit 3 and no real value in any
  case; lane SH2's clamp at 90 meets lane ID-ROOM's spill (`K-S3-64`'s
  run read 2 twins failing validation on `naaccr`, listed since as a
  held limit, which no shape of the other columns pins), lane HB2.
- **Codes and tables written or read unlike the source, older than this
  week** (recorded 2026-10-09; `K-S3-61`'s note carries them). Lane L1
  (P4-D390, P4-D384, `K-S3-61`) writes made-up figure codes at the
  source's width, label columns' exponent codes in their forms and
  range, a code with one letter among figures in its form, and free
  text's durations and face columns in theirs. Still so: a column of
  numbers beside labels writes its number half's exponent codes as
  integers of up to 280 figures or in G6.3's own spelling (P4-D390),
  which needs a published fact of the spelling. Lane LM1 (P4-D475,
  `K-HZ-28` 0 at 20,000 rows): a label's bound (`<20`,
  `90+`) holds the numbers beside it in a column read as numbers and
  labels, moved inward onto the grid they are written on and read in the
  column's decimal grammar; the exponent form and census it built for
  magnitudes past a double's range were withdrawn after review, so such a
  column writes as on its base, byte for byte (a redesign, owner LM2);
  still so, owner LM2, counts and measures in exponent style with a fixed
  number of figures write more figures (14,482 of 20,000 cells at two), a
  fraction of a day writes 5 cells at or past 1, and a joined range
  answered `joined` writes each position's style apart from its value (6
  crossed pairs, 10,858 ends with other decimals and 4,791 padded ends
  against none real). ACCEPTED (the
  orchestrator's rulings of 2026-10-15 on the sixth push's critic, the
  owner may reverse any): a pooled placement held to `figures_cap`
  misses the pool's mean, named (L1's measured trade: no wide integers),
  and seventeen-figure cells stand outside `styles.spelled`'s family
  (older, rare; P4-D390).
  A table whose rows end in its delimiter and whose header does not,
  or the reverse, is read as its columns since lane R5 (P4-D387), and
  since lane R6 also where a line closes `""`, each closing written back
  as the source wrote it; closings fewer than the census line are written
  the commonest way, as line endings are, except that where the header
  trails too a single closing is the bare one (a header ending in its
  delimiter over records all closed `""` reads as one column more), so
  `[bare 1, quoted 119]` under such a header is written bare throughout.
  Six twins of plain cells beside quoted closings miss
  `free_text.shape_forms` at exit 3, as the same tables with no trailing
  delimiter did before R6 (owner the forms lane FM); a header closed
  `""` over a straight three-column reading writes its blank name bare,
  and a description of a one-column fallback written before R6 misses at
  exit 3 on the real table, which now reads as its columns (owner lane
  LM2; both the orchestrator's ruling of 2026-10-16; P4-D387).
  A headerless one still reads
  an empty last column, written back empty -- lane R7's, the next
  reader lane, as lane R6's head (2d5f2a3) still reads it so.
- **Held-back codes written in pattern (lane CODES-1, batch 4m, P4-D439;
  `K-HZ-10`, `K-HZ-11`), still so:** a stand-in in a dense code space
  (ICD, NDC, procedure codes) can be a real, different code, and rule A2
  reproduces real held-back combinations (accepted 2026-09-18; at 20,000
  rows over three seeds 1,426 of NAACCR's 1,765 held-back codes, 19 of
  21 TNM, 84 of 144 GCS, 74 of 3,253 ICD-10); the patterns read a shape,
  not a registry's rules (43 of 43 Gleason stand-ins break their sum,
  10,990 of 12,243 LOINC stand-ins a check figure, 818 of 1,264 NAACCR
  stand-ins past C809), and closed lists (a blood type `AB-` written
  `C+`), codes publishing no form and a registry's own leading rule are
  CODES-2's; the balanced walk brings each listed character to the
  census line, not its real share (GCS of 8 or less: 272 against 172); a
  figure code's grain and a declared code's ends are kept only where the
  grid has room; rule A1 absorbs a pool only whole (`1.2.3` on 2 cells
  keeps 110 cells `group-N`); a code holding a list separator wears no
  form until lane LISTS (i2b2's `DEM|`, 23 of 12,578 stand-in cells); A2's
  census waits for the Safe Harbor question's `no` once CODES-2 puts it to
  code columns.
- **A level few people hold, pooled in people (lane PL, P4-D453;
  `K-HZ-19`), still so:** lane PL2's: a day-first date's stand-in is
  written month first (`12/31/1999`, which `%d/%m/%Y` refuses); the held twins of nineteen-figure codes (uint64
  against int64), of a declared decimal comma (a word beside numbers)
  and of `8.0` beside whole numbers (int64 against float64) keep dtypes
  older than the lane; the frozen vectors count content, not its order.
  A column of dates written as text that ten people or fewer fill writes
  the word `Z` in eleven cells, which `pandas.to_datetime` refuses (lane
  CZ-B: a change of the thin column's contract). A 0/1 column whose held
  value is not the other member, or a flag named with a word such as
  `no`, `day` or `id`, bears the prices P4-D453 (e) and (f) state.
  Lane CODES-2 (P4-D471) names a pool's rare levels beside its total
  only where the floor pooled by rows, so a key column whose rare keys
  few people hold, each on many rows, keeps made-up keys (the zoo's flow
  keys: 2,185 twin cells off the real list at 20,000 rows, `K-HZ-23`);
  the owner answered yes on 2026-11-10 to naming such keys beside the
  pooled total after the column's Safe Harbor question is answered `no`
  (never counted, never while an identifier question is open, at 20,000
  rows and 1,000 people or more): lane KV builds it (P4-D471's limit
  (g), answered).
- **With every pair published, a raised floor still costs some twins
  their mean and spread.** Since plan P4-D375 every tail pair binary64
  holds is published, so no twin of `K-S3-20`'s 37 shapes at floors 11
  to 50 misses an obligation and `K-S3-15` is green. Left, over 36
  column-floors at three seeds (`K-S3-22`): 21 moment obligations,
  where 110cb46 left 114 before lane G2's width rule (P4-D377) -- the two
  blocks that publish moments only, of 40 and 60 values at 36 (12), and
  Pareto(2.5) at 400 rows, seeds 1, 4 and 6, at 50 (9), their spread
  0.90 to 0.94 of the real one. No date or clock tail is withheld any
  more, so none narrows its twin for want of a pair.
- **A census of NOTATIONS that is only a pool is written as the
  majority.** Where no negative notation reaches the floor and the pool
  is no more than three notations hold below it, `negative_notations`
  publishes only `(withheld)`, and the twin writes every negative with
  the published notation, so its own description names a notation the
  census pooled, with nothing named by validation: 30 negatives written
  ten each in brackets, with the minus sign and with a trailing minus, at
  a floor of 11, came back as 30 hyphen-minuses at five seeds of five.
  The census of MARKS had the same gap and is closed, and a pool of
  either census that the rest of its block would let a reader pin is
  now counted under one convention every counted cell can wear, or left
  silent (plans P4-D352, P4-D356).
- **The largest tables** are measured to about 1,000,000 rows on
  identifiers (P4-D389); the end-to-end 2M x 50 run is `K-S1-06`.
  Landing 4 (stage 4's row names what lanes S4b-num, S4c and S4d
  brought). Left: a column whose values never repeat still holds a
  record a row (G2's dense tail: 2,287 MB at 3,000,000 rows, past the
  2 GB rule), reading holds the file's bytes and decoded text beside
  the table (both lane SR's, which reads and describes in groups of
  columns, and lane SV's in `validate`: the orchestrator's ruling on
  push critic 8, written at batch 4c), and `validate` took 493 s of CPU at 2,990,700 rows, since
  it describes the file again (2,000 MB and 585 s there before lane
  S4d; owner lane SV, the orchestrator's ruling of 2026-10-16). At
  1,000,000 rows of G2's dense tail the twin misses nothing since lane
  G2T (P4-D405, `K-S4-21`). A number tail whose end a field width or the
  pair's reach holds keeps the pushed staircase and G6.6.8's width walk:
  150 two-figure readings beside one `185` at a floor of fifty write 38
  cells on `97` and `98` against the source's 5, nothing missed, and the
  pushed staircase rounds a high tail's rank up (owner lane G2T2, the
  orchestrator's addendum of 2026-10-19).
  Left, and not calendar: the push still moves each stratum it passes one point at a
  time, so on long runs its work is the strata times the pushes (about
  4 times a doubling, measured to 4,000 strata; P4-D377), it walks each
  way in full where a collision's holders are of two kinds, and the
  identity walk's column text is the square of a value's spellings
  (111 MB at 1,000,000 rows of the Codex column; P4-D387): all three
  owned by the scale track's hot-spot lanes, chosen from lane B0's cost
  table (the orchestrator's ruling of 2026-10-16). The 1,000,000-row twin of
  decimal codes validates at exit 3 on the `%%%.%%` count, as on
  3434682 (P4-D390; owner lane LM1, the orchestrator's ruling of 2026-10-16). Left to
  S4b's calendar half, after stage 3b's last merge: G3's trade on a few
  instants held thousands of times (about 40 minutes at 1,000,000 rows
  by the x3.4 a doubling measured to 200,184) and its stall on wide
  gaps (four 10-day clusters a decade apart: 200,000 rows unfinished
  after 20.5 minutes of CPU), the weekday census's target search on
  sparse dates (103.8 of 163.6 s at 200,000 rows), J's million-row hours
  and `K-S3-44` (P4-D376), whose one census miss (`visit_10th_business`,
  the same on 3d893032) is lane S4bc2's (the orchestrator's ruling on
  push critic 8, written at batch 4c).
- **The packing walk can still take a long time on a few identifiers
  written in several forms.** Stage 4 bounds what the walk remembers at
  64 MB and has it read the counts together, so Codex's identifier of
  100 values builds in about a second and the battery's 300 values in
  four forms in three; but of sixty seeded declared identifiers of 100
  to 160 values in two to five forms, 2 still take it past 100,000
  states at the floor of 11, one unanswered after ten minutes, and 7 of
  sixty more drawn after the walk was written; at a floor of 36, 12
  of the 120 do (`K-S4-04`, plan P4-D389). Exact packing is the
  partition question; a stronger reading of the counts is the open
  cause. The held block's layout packing (method G9.6, plan P4-D182)
  files no deviation for a layout it leaves short: the held surname of
  lane CODES-2's gate table missed its three layouts with the twin's
  notes empty, on the public head's tree `a391424c` and on that lane's
  repair 1 head `5accf643` alike, and only validate named them; since
  that lane a column of at most 64 groups is asked at most 64 questions,
  which writes that column's layouts, and a column of more keeps
  sixteen. Owner lane HB3-b (P4-D471).
- **Checking a file costs more.** The checker now has tails to check:
  20,000 rows by 20 columns take about 30 per cent longer than the
  70.2 s they took before stage 3, measured quiet (`K-P3-12` carries
  the seconds). Building a twin costs nothing extra (`K-S1-01`).
  Landing 4 owns the scale work.
- **A bounded scale of few rows can lose its own top step.** Where a
  scale's outermost value stands on ONE cell the tail may not name it,
  so the twin writes a value just off the scale: over six clinical
  scales at 900 rows, four of their twelve tail sides are refused and
  their twins write 31 cells the scale does not have -- 18 on a pain
  score and 13 on a coma score -- with the worst column mean 11.33 per
  cent out; at 1,800 rows every side lists, no cell stands off the scale
  and the worst mean is 0.97 per cent out (`K-S3-05`, plan P4-D346, held
  at a ceiling by `tests/test_stage3_tail_rule.py`). `K-S3-09` measures
  another shape and never this one.
- **The floor counts ROWS where nobody has said who the rows are**
  (owner, 2026-09-23; plan P4-D348). Since lane HX2 (P4-D406, batch 4e)
  every value published beside a declared or candidate person column is
  counted in people (`K-S3-65` at 0), but the rungs of a measurement or
  code column not attached to its subject are still judged in rows (the
  orchestrator's ruling of 2026-10-19, item 2): on `K-S3-14`'s three
  repeated-measures shapes `synthtwin profile` publishes 2 values held
  by 11 rows of 10 people, both rungs of a score, and refuses the table
  of 12 patients outright (all three shapes are now under the table
  floor, P4-D425, so the command refuses them; the rung case can arise
  at any size, and the floor does not close it); the library call without
  subjects, the validator's, still publishes the 68 `K-S3-14` holds.
- **The written summary and the twin's report still say "100 rows is
  the smallest table synthtwin describes"** (`summary.py`, measured in a
  20,000-row run's plain-language summary; `rendering.py`), false since
  the table floor (P4-D425); rewording moves bytes of every table, which
  lane POP may not. Owner: lane FLW (the floor's words in every written
  output, a byte-change landing after POP and MIN merge, the
  orchestrator's ruling of 2026-10-23). The status screen and the
  package say the new floor.
- **A name, street address or birth date is held beside a patient
  key, declared or asked about by any question offering `identifier`,
  and published where nothing says who the rows are.** Beside a subject column, of any number of people,
  every published value, written form, remainder and census entry is
  counted in people (plan P4-D406, `K-S3-65` at 0), but for the rungs and
  tail boundaries of a measurement or code column not attached to its
  subject, still judged in rows (the limit above); a long table whose
  only clue to the person is the name itself has no people to count in:
  69 real values over 600 and 20,000 rows (`K-S3-64`'s stated shapes),
  names and addresses owned by CODES-2's allowlist, birth dates by
  CODES-1 part C.
- **Dates published as plain numbers when a declared date count is
  declined: CLOSED by lane HX2** (plan P4-D406, contract NF127): such a
  column is held on every table and named in the screen, the summary
  and the questions file's `held` section.
- **A record-number key written beside `-1` meets its published forms:
  CLOSED by lane HB** (plan P4-D442; `K-HZ-13`): the keys of 44 patients
  beside `-1` (2 % and 40 %) and a key exported as `100001.0` validate at
  exit 0 at 600 and 20,000 rows (as they did on lane ID-ROOM's head), a
  telephone number opening `+` keeps its `+` (exit 3 there), and lane HB
  took `durable`, `key_m1_40` and `phone_plus` out of K-S3-64's
  `VALIDATION_LIMITS`; four stay: two read at 600 rows only, below the table floor
  (LANE I4m RULINGS 18), and two stated limits with their owners:
  `seqm1` (a held run beside `-1`, exit 3 at 200,000 rows; CODES-1 part
  C's, kept until K-S3-64's driver reads it at exit 0 at 20,000 rows) and
  `reglistmixR` (lists marked `;`, `,` and `|` cell by cell, exit 3 at
  20,000 rows and exempt from `twins_failing_validation`; limit (q), lane
  HB2). The search beside a negative placeholder
  passes over a layout of figures alone in one step: record numbers beside
  `-1` generate in about twice the time of the same column with those
  cells blank at 20,000 and 200,000 rows (226.8 s against 4.2 s at 20,000
  rows on daed36fb).
- **A second record number beside a declared person column is held**
  (plan P4-D406): each of its values is one person's, so the column is
  described as record numbers counted in people and publishes none
  (`K-S3-64`, 0 at 600 and 20,000 rows).
- **A twin record number never equals a real one, and a dense layout is
  written wider** (lane ID-ROOM, plan P4-D432; `K-HZ-06`, 0 at 600 and
  20,000 rows, as written and by the merged key the product counts a
  person by). Where the real values fill a layout's room -- record
  numbers `1` to `N`, a person on twenty rows, `P` and five figures at
  20,000 rows -- or spread thinly over a block's spellings, which then
  passes over none 1 to 10 keys hold -- random seven or eight figures and
  `REC` beside `rec` at 20,000 rows (338,776 of 1,700,000 cells over the
  gate's shapes) -- its twin values are written longer than every real one,
  its census entry and the column's lengths are listed rather than
  checked (or, where only some values widen, met within the cells written
  wider), and the report names the values moved. Code testing a width
  meets those rows otherwise, and where a layout holds characters the
  merged key does not read a widened value is longer than `max_length` + 1
  (`two_long_prefixes`: 124 characters beside a published 63; 5,381 cells
  over 15 of the gate's 92 shapes at 600 rows). Lane CODES-3's stated
  limit (4) is closed. TWO PERSONS ARE NEVER WRITTEN AS ONE, by the walk or
  the pass: CLOSED by lane HB (plan P4-D442). The walk's own merges at
  20,000 rows on lane ID-ROOM's head (20,000 real persons written as
  13,684 merged keys on `pad_split`, 19,220 numbers beside their `.0`,
  19,669 and 19,284 on a dotted pad, 12,707 of 17,222 `P`/`P-` keys) are
  0: the walk refuses a spelling naming a person written before it; and
  the pass's per-member fallback, which wrote 79 and 54 walk numbers as one
  there, claims each member as it is chosen. Rootless twin UIDs and a held
  UID's twin are written in the UID grammar (about seven in ten off it
  there). Outside lane HB, each with its owner: the product publishes no
  check digit, so an NPI-like twin's Luhn digit was never the table's
  (identifier forms, owner lane CODES-1 part C, P4-D432 (9)); the
  made-up dates of a held date column, and since lane HB the valid dates
  of a date's form, may equal real dates (an attribute, never a key: an
  accepted chance equality, 2026-10-27, counted in `K-HZ-13`); an
  identifier written with spaces
  around it is written without them (exit 3 on the base and the head
  alike). Lane HB's repair 1 CLOSES: record numbers between commas read
  as free text or labels (4,008 real keys and 3,265 equal cells at 20,000
  rows, here and on the merged line) are held and written key by key off
  the real; keys named by number words (`patient_num`, `med_rec_no`) are
  held; two-figure years, month words and eight-figure dates beside ISO,
  and the zoo's `dx_date` read as record numbers, are written as valid
  dates. Lane HB's stated limits, owner lane HB2 (P4-D442): a held count
  written `%e` misses `type.all_whole_numbers`; `labs.viral_load`, read
  as record numbers, writes about 3,900 twin cells as no number; one
  real person written two ways across rows becomes two twin persons
  (5,000 persons zero filled or not: 9,369 at 20,000 rows); a held key's
  `-1` cells are written with a power of ten (`8038913e7`; for the
  orchestrator: the hold publishes no placeholder); the free text's
  carrier of its longest length is written in no form (one census cell,
  validate exit 3); the UID pool past `max_length` + 1 (37 against 29)
  and a `-374` placeholder; the walk beside a negative placeholder at
  about twice the blank column (1.88 to 2.25, linear: up to five whole
  builds, P4-D182; `K-HZ-13` bounds the ratio at 2.5); a column named by
  the three-letter abbreviation of a medical record number is asked by
  its values' routes alone (the word is in the denied vocabulary); and
  the name route's price, one question each for code columns named
  `*_ID` or `*_KEY` (`UNIT_ID`, `WARD_ID`, `VISIT_ID`, `LOT_ID`,
  `ORDER_KEY`). Lane SH2's held years written `1932.0` are not
  reproduced on this base (SH2's, or the integrator's at its merge).
  Lane HB's RULINGS 3 round: a list key's opening is the shortest no
  real key of its width opens with, a single key beside lists kept off
  the same way, so no list member equals or carries a real key on any
  draw (`K-HZ-13`'s `list_cells_carrying_a_real_key` 0); stated, owner
  HB2 (P4-D442 (q), (r)): a list cell marked `;` or `|` has no layout
  and is written as a stand-in (declared, the prefix missed, exit 3),
  and such a held list takes about 470 processor seconds to generate at
  20,000 rows. Lane HB's second repair: no run of figures a free-text
  twin writes is a real key (`figure_openings`, P4-D442 rule 14: keys
  joined by `;` or `|`, alone among notes or once each between commas
  wrote 4,000 real key tokens and 3,265 equal cells at 20,000 rows, now 0
  and 0); a wider list member carries no narrower real key; a column of
  rootless UIDs is not written as dates; `patient_IDs` names a key;
  random keys between commas stay lists at their exact width, kept off the
  real by noughts (P4-D442 rule 22: 0 of 13,269 list cells written as lists
  and exit 3 at 20,000 rows, now 13,269 and exit 0, 0 real keys as text or
  as a run; the one-key layout of figures alone reports its census only).
  Stated, owner HB2 (P4-D442 (r), (t) to (x)): a held list's generate
  grows far faster than its rows (`reglistmixR` 13.3, 17.4, 142.6 and
  4,973.6 processor seconds at 5,000, 10,000, 15,000 and 30,000 rows,
  measured before rule 22), a threat to the 2,000,000-row budget; once-only
  key lists in free text miss their mean length, as on the base. Lane HB's
  close round (on batch 4m's merge): no made-up run of a label column or of
  free text is a real run or holds one, runs read from four figures
  (`figure_openings` on the label roles too; a declared code names none);
  bare five-figure list keys stay lists (`0%%%%`); the hunt reads a real
  run inside a longer one; padded keys among notes are asked. Stated, owner
  HB2 (P4-D442 (y), (z), (q)): a register of four figures in free text whose
  made-up cells spend the room free of real runs is written a figure wider
  or as noughts (731 cells, exit 3, at 20,000 rows); a label column whose
  runs fill their room likewise; `reglistmixR` misses its validation at
  20,000 rows on the merged code; a label column's held-back level written
  as a number keeps the class walk's spelling (P4-D442 (aa)). Lane HB's
  close round 2 (Codex's review, LANE HB RULINGS 8): a label width is
  weighed by rows, a note beside padded keys reads any letter, key `3`
  lets no longer run carry a real one, a rebuilt cell is never a declared
  absent spelling (12 absent cells for 11 before), the report counts what
  is written, and the loader refuses an opening naming a figure twice.
  Stated, owner HB2 (P4-D442 (ab), (ac), (ad)): beside key `3` a run
  longer than a width whose opening is two figures has no room but
  noughts; a rebuilt cell where every room is spent may stay absent; the
  walk's own function asks every alternative the loader hands it. Lane HB's
  repair of close round 2 (LANE HB RULINGS 9 and 10): a cell read as absent
  asks every run of it before it is written absent, the absence repair is
  linear in the cells (7.46 s at 1,600 cells before), the oracle reads a
  declared number as a number, and the hunt's count is read from the
  registry; noughts alone are written one figure wider than every width
  named, save at a width a published form writes, which they keep (rule 42
  as lane HB's fix 4 restates it). Stated, owner HB2 (P4-D442 (ae), (af)):
  a label column's held-back numbers keep their spelling on the pooled
  scale; a held key of noughts alone at a published form's width comes back
  where the room is spent (497, 1 and 267 twin cells on three shapes at
  20,000 rows); zero-filled record numbers beside a word write every held
  stand-in as letters and noughts (validate exit 3 on two of the three).
  Held ZIP columns: 0 twin cells holding a real ZIP at 20,000 rows on the merged code
  (`zip_plus4`, 9 before; `zipplus4_30`, `zip9_unk`, `zip9pad_unk`, the
  zoo's `patients.zip5`); ruling 7's ZIPs drawn from the unassigned
  prefixes 000 to 004 are not built (the owner's reversal, ID-ROOM RULINGS 7).
- **A pool's spread is no longer verified.** The owner chose on
  2026-09-21 to publish a pooled column's mean and not its spread,
  because publishing both solved for the held-back values. The twin's
  pooled mean is now exact and its spread is unchecked, about 2 out
  (`K-2B-50`, green on the mean). Stated, not hidden.
- **The patient layer's within-patient correlation** (2026-10-20;
  specified, not built, plan P4-D412). On the design's invented long
  table (a median of 20 rows a patient) the study's route brought the
  correlation back 0.076 to 0.081 below the real one, outside
  `K-BC-06`'s 0.07; the cause, measured, is the patient weight fitted on
  real rows inside cells that include the child's band, not the banding.
  The page's route (G16.15's weight read on the published row family):
  within 0.0093 of the real on the
  three long-table runs of the page's run 3, with PWIT judging the row
  family (OPEN until lane CHa measures the floored split on long tables
  and lane GR confirms on the built generator). Clause (5), where run 3 still misses it: `ST2` at 20,000 rows seed 1 (the
  correlation, -0.0210 against BASE's -0.0105, yardstick 0.0075) and
  `ST2-AGE` at 100,000 rows on its (arm, old) route (the lag-1
  correlation); owner
  the January stretch item. The visit trend publishes no cell on long
  tables (arm by visit 0.012 to 0.019 of the real on run 3's long
  tables; owner the January `r`-band form). Complete follow-up, a
  December limit: on a table where every patient has every visit,
  change over visits is not published in December, since the trend's
  cells then hold every row and their code total is fixed (measured
  price, run 3: one table, `ST2`
  without dropout, its trend at 0.003 and 0.006 of the real; 22 of 24
  route-runs meet `K-BC-06`'s clauses (1) to (4); owner lane GR in
  January, a certificate covering cells that hold every row, measured
  on that table). The third candidate, moments (the design study's run
  3c), is measured and not adopted: on the long tables it carries the
  trend at 0.903 to 0.931 and the correlation within +0.005 to +0.034,
  but no existing witness covers its moments, which pin small counts of
  patients on exhaustive fixtures; it waits for its certificate (the
  `r`-band SWING proof and a joint witness of its sum of squares with
  the column's square sum), January's stretch unless proven in
  December. Counts of
  patients by their exact readings beside a trend or an own mean leak on
  the fixtures' worst cases (the page's limit 9; owner the
  orchestrator's ruling and lane CHa's product-scale run).
- **A twin gives up a number column's mode count at the table floor**
  (lane S5a, P4-D437): at 20,000 rows, whatever the seed, each named in
  the twin's report, exit 0 -- the stage-5 battery's weight (`mode_count`
  17 published, 10 in the twin), and on lane S5a's verify's table of no
  weight (`planning-notes/work-2026-10/wave6/S5a-verify-work/`) the age
  (323 and 277) and the lab value (79 and 52); owner lane GG (the
  orchestrator's ruling of 2026-10-26: a published `mode_count` met
  exactly by the twin at 20,000 rows, or a named limit).
- **The switched command stops when a caller asks for the rule steps**
  (lane RO, P4-D459; carried, lane RO2's first item, the orchestrator's
  LANE I4q RULINGS 6 (1)). On lane RO's invented event table
  (`tests/rules_event_table.py`, seed 7), `cli.ChainRun(rules=True)` with
  the subject question answered `one row each` raises a `KeyError` in
  `summary._tail_lines` at 4,000 and at 20,000 rows, on the batch's line
  before lane CHs's merge (`fd29238b`) and on lane RO's own head
  (`6e33105e`); the switch off, and on without the rule steps, exit 0.
  Behind the switch, only where a caller asks for the rule steps; nothing
  is published past the stop.
- ~~**A held date column loses its room at 200,000 rows of mixed birth
  dates**~~ **CLOSED by batch 4q's fix round** (lane ID-ROOM2, P4-D457;
  the orchestrator's LANE I4q RULINGS 9 and 11). On the zoo's mixed
  birth dates at 200,000 rows, where `K-HZ-13` read
  `invalid_date_strings` 200,001 on the merged head `b93f128a` (the twin
  writing record numbers for every cell, no real value published), a
  layout written year first beside one written year last takes the
  block's years whose second figure is a nought: the room is `[[2028,
  2719], [3000, 3099], [4000, 4099], [5000, 5000]]` and the twin writes
  0 invalid dates, 0 equal and 0 merged; `K-HZ-13` is stamped from the
  second round's proof on its head `c22837e6`, OPEN-held, 1 invalid
  date string. Its price, stated: a made-up full date there may fall
  in 3000 to 9099, unreadable by a nanosecond date type past 2262.
- ~~**Layer L0 hands out a cell no stratum gave**~~ **CLOSED by batch
  4q's fix round** (lane BT2's step 2b, P4-D448, in the public tree
  since batch 4p, behind the chain's switch; the orchestrator's LANE I4q
  RULINGS 9 and 11). Step 2b moves nothing where neither the edge value
  nor the next value holds a cell of its piece, so the analyst battery's
  ST1 at 20,000 rows, table seed 3, generates; the oracle's mirror takes
  the same guard, which no case pins since no frozen vector meets the
  class, owner lane BT2's successor. `K-BC-11` is stamped from the
  second round's proof on its head `c22837e6`: PASS, no overclaim.
- ~~**A blank in the answers file overrides an answer typed at the
  prompt**~~ **CLOSED by batch 4q's fix round** (batch 4q's merge of
  lanes CZ-A and TT, P4-D445 and P4-D460; the orchestrator's LANE I4q
  RULINGS 11 (3)). A question offering `identifier` answered at the
  prompt now frees the column over a blank under `identifier` in the
  answers file (at 20,000 rows with the key typed: read as a count, and
  validate of the real table against its own description exits 0);
  Enter, a question the prompt did not put and a run with nobody at the
  keyboard hold as before.
- **Batch 4q's carries, each with its owner and its numbers** (P4-D445,
  P4-D454, P4-D457 and P4-D458; the orchestrator's LANE I4q RULINGS 12,
  15, 17, 19, 21, 22, 23, 24, 26 and 27; each at 20,000 rows). Lane CZ-A2:
  among its first items, a name and a record number joined by commas
  with no space (`Cedar,Abc,1000000`), read as an affixed number, its
  description publishing 1,000 person prefixes and its twin writing
  18,000 of 20,000 cells equal to a real cell and 1,998 more holding a
  complete real record number, on the public tree as on the records head
  (the HIPAA bullet above; P4-D445 (3)(g)); `K-HZ-16` prices
  six of lane CZ-A's held identifier columns (`price_dated_columns` 28
  and `price_dated_columns_answered` 9 against targets of 22 and 6, the
  bounds restated to 28 and 9 at the records round;
  nothing more is shown); and `implant_log`'s fixture holds 40 people
  at 20,000 rows, so the command refuses it for the people floor, which
  `K-HZ-06`'s zoo leg counts under `refused_by_floor` (the fixture's
  1,000 people change `K-HZ-14`'s items). Lane ID-ROOM2: a held date
  column one of whose real cells names a year of its block, by any
  reading the room now holds, has no room for that kind of year and its
  twin writes record numbers (NF137, the owned price; the outside
  review's table of eleven days of 2028 beside ISO births now so, and
  since the third fix round a column beside compact stamps or a clock
  written first, its 17 measured tables and 23 of its 64 sampled
  spellings, and a held birth-date column beside ten-figure stamps
  written year first in two figures, whose first eight figures read as
  a full date name years of the room: 6,951 of 19,987 such stamps of
  2000 to 2025 at the unit level by the builder's draw and reading (a
  room year outside the stamp's own days), 8,996 of 20,000 by the third
  round's verify (any held room year not the stamp's own), an over-hold
  kept as the conservative side's price; and since the fourth fix round
  a column beside the four families it reads, and a held birth-date
  column beside stamps written with their zone, whose two-figure year
  the cross rule holds in both centuries (births `760101091530Z`:
  `[[2028, 2103]]` on the third round's head, `[]` on the fourth's); the
  builder's probes of births beside a few written as counts (Excel's
  serials, Unix seconds) published no room on the third round's head
  already, and a count is read now in all twelve counting systems too
  (`46753` holds 1582, 1960, 1969, 1970, 2028, 2032, 2088 and 2098, so a
  five-figure count of a birth after about 1958 names a year from 2028),
  an over-hold); years past 9998 and digits outside ASCII are not
  measured beyond the generator; and
  a room published where the date pass writes no date, its layout
  withheld (ten `01/01/28 00:00` cells held with `--identifier`:
  `[[2028, 2137]]`, 0 of 20,000 twin cells a day), F10 reading E there.
  Lane ID-ROOM3, its first item (the fourth round's verify, its item 3;
  LANE I4q RULINGS 26 (1)): a held date column holding a figures-only
  cell that is no date and that some counting system reads as a day of a
  year of the block loses its room too since the fourth fix round:
  three `99999`, a placeholder, beside 19,997 ISO births of 1930 to
  1999, `[[2028, 2137]]` on the third round's head and `[]` on the
  fourth's, every twin cell a record number, and so with eleven `99999`,
  eleven `55555` and three `77777`, because `counted_years` reads every
  figures-only cell in all twelve counting systems and a five-figure
  value from about 21,184 names a year of the room in one of them:
  NF137's price widened, the column keeping no real date, not an
  exposure; the remedy sets the product's placeholder spellings,
  all-nines and all-noughts, aside before the count reading, as the age
  and ZIP reaches do. Its two date forms still writing real days, a day
  of the year with its clock run on and SAS's two-figure years of 00 to
  23 where the two-figure room wraps past 99, are in the HIPAA bullet
  above with their numbers (P4-D457).
  Lane HB2, its second item: the zoo's vitals export, whose weight
  column (`kg` after each value) is read as possibly holding ages,
  publishes the top code 90 and no weight above it, and the command says
  the twin writes none above 90, yet its twin writes 4 weight cells above
  it, 130.9, 138.8, 148.3 and 159.5 kg, made up, none equal to a real
  cell, three of them (138.8, 148.3, 159.5) beyond the real column's
  largest, 131.0 (11 real cells at or past 125 kg): reproduced
  on batch 4q's fix head (the export at its catalogue seed, nobody at the
  keyboard, generate at seed 0); no real value is published, and lane
  BT3a's check read four such cells on its base and head alike, the
  default walk's (P4-D454's carries). Lane BT2's successor: no case pins
  the oracle's guard of step 2b (above). The second round's scoped verify
  (LANE I4q RULINGS 22 (7)): lane ID-ROOM2, a held date column with a
  few cells of a day and a month and no year (`Jan 28`, read as January
  2028 too) loses its room where the first round's head published one
  and wrote no real day (P4-D457's price); lane CZ-A2, among its first
  items, a name column lane CZ-A's route holds whose cells carry no
  layout (an apostrophe in a family name, two spaces, a tab or a letter
  outside ASCII) is written by the spill, generate taking 106 to 115
  CPU s at 20,000 rows against about 8 for the same column without the
  mark (P4-D445).
- **Batch 4r's carries, each with its owner, and its numbers where it
  was measured** (batch 4r's fix round, P4-D467; the orchestrator's
  LANE I4r RULINGS 3 (4) and 6 (2); no exposure measured on any of the
  fix round's carries by its verify; the two seam limits at the end are
  not measured). The first three are FIXED by round HYG-1 and its repair
  HYG-1b (tests and tools, no src line; merged first in batch 4s, plan
  P4-D467's paragraph of the round), none of them new against the public
  head: four
  closed stage-3b gate tests read the numbers of a validation check's
  own text with a split that does not read a count followed by a point
  or a bracket
  (`tests/test_stage3b_clock_minutes.py:594`,
  `tests/test_stage3b_day_of_month.py:569`,
  `tests/test_stage3b_gate.py:3434` and
  `tests/test_stage3b_weekday_review.py:327`; they look for counts under
  the floor in texts the product writes from counts);
  `tests/test_stage3b_layout.py:3888`, a check at 400 rows whose needle
  misses a real cell at a string's end, before a point, in brackets or
  before a semicolon and finds it only written `example: X, then`; and
  `tools/measurements/kpi_stage3_tail_leak.py`'s `_tokens`, which cuts a
  value at a comma or a percent sign (`36,8`, `1,234` and `12%` missed;
  its battery's reach not measured in batch 4r; round HYG-1's verify
  reads no withheld value anywhere in that battery's pages, 0 in 136,959
  lines and 3,997 strings, at 400 to 1,500 rows). Owner clause (x)'s
  line, the
  orchestrator's: the word rule's edges (a value joined to another by an
  inner mark with no space, or with a letter or figure beside it, is no
  word of its own; code points and case compared as written) and the
  chain's texts compared whole, each null on the 37 scan calls the fix
  round kept (no set-aside spelling of three characters or more stands
  anywhere in their decoded private texts, and none stands as a word of
  a chain text without being equal to it). Two limits of the seam of
  lane BT3a's merge (P4-D467), behind the chain's switch and not
  measured, each with its owner: the rule steps (lane RO, P4-D459) read
  an ineligible candidate `B` that is not refused (free text, empty,
  unrepresentable or a sequence) on the file's cells under the
  description's declarations, so its held dates in disguise or its cells
  counted absent reach those steps as written (owner lane CHON); and a
  column whose cells the description changes is read again by taxonomy
  without lane CHs's kept reading (lane CHs's paths table, `level_b`),
  its time at 2,000,000 rows not measured (owner lane CHs2).
- **Round HYG-1's carries, owner the orchestrator, each with its
  numbers** (the round and its repair, tests and tools with no src line,
  merged first in batch 4s). Two readers of the kind the round fixed
  are named legitimate, each reading nothing hidden by construction:
  `tests/dates_held.py` lines 868 to 871
  (`K-HZ-07`'s search of a column's block) find a date only after a
  quotation mark or a space, missing 8 of 12 placements at the unit
  level, while the block holds a date only as a whole JSON string or
  key, or at the start of a moment string, and its sentences come from
  the closed grammar `taxonomy.rendered`, whose arguments are
  enumerated; and `tests/test_stage3_tail_rule.py` lines 268 and 519
  (`_NUMBER` in `_leaks`) cut a value at a comma (`36,8` reads as 36
  and 8), while the tail rule's 14 shapes write no comma (formats
  `str(int)` and `:.2f`). Its stated limits: a list glued by a
  semicolon or a slash is read neither by the old reading nor by the
  word rule (6 of 30 runs of the check that the questions file's q6
  names no cell, ten placements of the example in three shapes); a cell
  of marks alone is seen only whole (4,112 of 18,000 generated
  questions); and a count glued to a word or a range (`3-10`, `3/4`) is
  read as no count, and the product writes none (`_shown_count` writes
  figures alone); the battery's real table is written with every comma
  dropped (0 of its 1,759 outermost cells carry one); description
  strings are compared whole only (0 of 3,997 hold a withheld value);
  and two regex readers are replaced without a union
  (`tests/test_stage3b_gate.py:3440` and
  `tests/test_stage3b_weekday_review.py:331-332`: the old reading read
  602 of 1,044 glued placements in the gate's frame; the weekday site
  not measured in its own frame).
- **Batch 4s's carries, each with its owner and its numbers** (its
  merges, owed items and fix round; plans P4-D469 and P4-D471 to
  P4-D478; the HIPAA classes stand in the first bullet above; on the
  tables the fix round's verify measured, no exposure of a real value is
  new against the public head). `K-HZ-16`'s attack `iso_zone` (dates
  spelled `2024-03-05 00:00 EST` among the answers of a key-value form,
  20,000 rows): lane CZ-E's question, answered `yes` as the zoo answers,
  holds the answer column whole as an identifier, so it is neither put
  its dates question nor held by the
  dated-values rule (`case_iso_zone_not_asked` and
  `case_iso_zone_not_held` 0 to 1, red at the stamp; 0 real date
  elements shown and 0 twin cells carrying one); ruled (LANE I4s RULINGS
  4 (1)): the hold stands, the key is to read a column held whole as an
  identifier as held, and whether such a column is also put its dates
  question is a fidelity item priced on the zoo, both lane CZ-H's. The
  fix round's: a
  number of months from 90 to 125 beside year bands is pooled into the
  oldest band as years (3,000 cells of children aged 8 and 9 in the
  oldest group on a 20,000-row table; new against the public head as a
  wrong group, no real value written), lane CZ-H's second item; a band
  of months, weeks or days with open words written `90 months and over`
  by the number path (71 of 4,000 generated columns; not new), lane
  CZ-H; a measure's bands beside one number of 0 to 125 reached until
  `no` (`80+` on 14,000 of 20,000 rows; 14,030 beside 100 such numbers,
  14,360 beside 1,000), lane CZ-G with limit (k); a label's bound at
  2^52 steps or more of its grid (6,729 of 65,856 cases miss the exact
  point on both heads) and the validator's reading of a label's bound,
  not built (measured: three real `15`s under a bound of 20.0, so such a
  check would fail the real table), lane LM1-b; a zone word outside the
  closed list's nine families, or none for an offset (`HST`), held as
  before, lane TR2. A recorded fidelity cost of pooling a rare far code
  in people: the twin mean of `K-HZ-19`'s pooled number column
  `code_per_person` 9.0041 to 23.4041 at 20,000 rows against the real
  7.5878, not split by a run (at 600 rows, below the table floor and no
  finding, 38.2333 to 4320.9, put at lane HB2's merge by the form run
  alone on the line's heads); owner lane HB3-a3, its first item,
  measured and bisected at 20,000 rows (the orchestrator's LANE I4s
  RULINGS 4 (4)). A stated cost of lane CZ-F's hold of persons' names,
  owner lane CZ-H (LANE I4s RULINGS 4 (5)): on `K-S3-65`'s batteries the
  tables of persons' names (`g-caps-2000` and `g-caps-20000` beside an
  open record key, `t-name_keyzero-20000` beside keys written with
  noughts) withhold nothing now (77, 119 and 144 values to 0, the name
  column held whole), and the two `g-caps` twins, which failed their own
  validation (exit 3) through the count alone on the public tree, fail
  it without the count too (`twins_failing_without_it_too` 3 to 5; the
  judged `twins_failing_validation` stays 0), split by the driver's
  per-table lines on `548abf89` and `85eb6754`. The fix round's item 7
  (one index of a
  column's present runs for all its layouts, P4-D469): the review's own
  table reaches the exclusion test at each of its 50 layouts when its
  column is declared a record number (on `ce75ec54` 50 scans and
  1,000,000 row visits at 20,000 rows; on the fix head one read of the
  20,000 rows for the 50 questions, the description byte-identical), and
  undeclared, the command's default path, it does not reach the test (0
  calls at 20,000 and at 200,000 rows). `K-HZ-24`'s driver reads no
  family for the micro-step's two spellings (eight glued before an end
  word in y, a week joined to its year by a point), which its gate file
  carries: the driver's two families and its re-run, owner the
  orchestrator. Lane CODES-2's limits in plain words (P4-D471): (a) a
  rare word of letters alone typed into a measurement column, a name or
  a place (`Dr Smith`, `Cook County`), is named beside its pooled total
  with no question, the residual the owner's answer names, his to veto;
  (h) a declared code answered `no` names its whole long tail, readings
  and extremes included (15,665 readings named at 20,000 rows on the
  statistics check's table), owner lane CODES-3, a veto item for the
  owner; (k) a spelling the floor folds into a published level is
  written as that level's commonest spelling, so a mapping read off the
  twin can miss one (`po` folded into `PO`), owner lane CODES-2's
  successor; (l) a declared code ending in a number from 90 to 125 and
  `Y` names nothing (3 of 20,000 generated procedure codes), owner lane
  CODES-3; (m) figures written in superscript, ages past 89 in another
  language's words and a month's short form alone are not read as dates
  or ages, owner lane CZ-F or CZ-G; (n) characters that print nothing
  but are no format character inside a month's name or a number word,
  `SSN` glued to nine figures on path (i), and whitespace controls
  inside a word are read apart from their plain forms (45 names and 90
  twin cells at 20,000 rows on every road for the first, the same on the
  lane's base), owner lane CODES-3 (planned), and the held writer's
  short layouts (12 twin cells equal to a real spelling where nothing is
  published, validate exiting 3 on those tables), owner lane HB3-b-b.
  Keys the seal read moved with no lane named, none a judged key and
  none showing or writing a real value, owner lane CZ-H, whose first
  step splits them by a run of the line's heads (LANE I4s RULINGS 4
  (3)): `K-HZ-02`'s
  `typed_day_numbers` 8 to 5 failures (lane HB2's head read 8) and
  validate's misses over the zoo 12 to 11; `K-HZ-01`'s questions put at
  600 rows 322 to 327; `K-HZ-23`'s Safe Harbor questions over its
  twenty-seven target tables 26 to 30; `K-HZ-24`'s chance twin cells on
  road (iii) (`age with more` 70 to none, a month and day 32 to 36, a
  month and year 35 to 31); and `K-S3-65`'s zoo `patients` table, 88
  values withheld to 87. Read as a lane's and not measured: `K-HZ-06`'s
  zoo identifier columns 311 to 317 beside lane CZ-A2's implant log
  table, and `K-HZ-14`'s description fragments 84 to 4 and twin
  fragments 20 to 12 and `K-S3-64`'s one-a-row chance cells 6,100 to 10,
  each read as lane CZ-A2's.

## The rules an assistant breaks first here

1. **Never change the decontamination scanner to make text pass** —
   change the text. Some ordinary words are denied. **A file you have
   not staged is not scanned**, because the scanner walks the TRACKED
   tree.
2. **The generator never reads a table.** Only the profiler and the
   validator open a CSV. No test helper crosses that line.
3. **Every published sentence is an enumerated form**, not a string
   written at the call site. Check `taxonomy.NOTE_ARITY`.
4. **A closed enumeration is stated in up to eight places.** Adding a
   role or a settings key means finding all of them.
5. **Never close a residual on a reading.** Build the column it
   describes and run it.
6. **Grow a list with `x += [item]`, never `x = x + [item]`.** The
   second is quadratic; stage 1 removed it from 661 places and a guard
   now forbids it. The scanner forbids `.append`.
7. **Run the guards AFTER `git add`**, then the seal LAST, then ONE full
   suite. Breaking that order costs another hour.
8. **A branch is not done until the WHOLE suite has run on it.** Four
   fix branches each ran only their own area's tests and together left
   56 tests red elsewhere.
9. **A test may open no process pool, no thread pool that takes a
   socket, and no socket.** The suite is network-dead and the conftest
   guard fires on the pool's own machinery. And **a number the machine
   decides — an absolute time, a peak memory — is recorded by the
   ordinary suite and judged only on the quiet reference machine, never
   on a CI runner** (`kpi_rules.MACHINE_KINDS`, `kpi_rules.on_a_runner`);
   what the suite judges everywhere is the property of the CODE beside
   it.

## Already tried here, and it does not work

- **A pronoun cannot be resolved by a regular expression.** Demand that
  the prose NAME the thing.
- **Widening a ban's noun list reports honest prose.** Name the SHAPE of
  the claim, never broaden the noun.
- **A guard that passes is not a guard.** Mutation-verify every new one.
- **Where a review names one site, there are usually two or three.**
- **A count restated in several places will disagree.**
- **A GIT WORKTREE HAS NO `.venv`, AND BORROWING THE SHARED ONE TESTS
  THE WRONG SOURCE.** Set `PYTHONPATH=<worktree>/src` or give it a venv.
  But the guard that catches it asks whether the imported package IS
  this tree's code, not where it sits: CI installs the wheel built from
  the commit and tests THAT on purpose.
- **A MUTATION LINE IN A DOCSTRING GOES STALE** when a second statement
  covers the same ground. Re-run the mutation before citing it; a stale
  one reads as a guard that does not exist.
- **A repair that prints ambiguous numbers is worse than the silence it
  replaced.**
- **Measure a ruling against the suite BEFORE building it.** The tests
  are the record of decisions already taken.
- **A test that fails after a ruling is not fixed by copying the new
  output into it.** Derive the new number from the rule, or it is not a
  test.
- **Declaring column types does not make generation faster.** It helps
  only the describing step, and only by skipping the reading cascade.
  The generator's cost is the idiom and the ladder.

## How a new conversation gets its bearings

| what | how it reaches you |
|---|---|
| `CLAUDE.md` | loaded automatically in every conversation here |
| **this page** | `CLAUDE.md`'s first instruction is to read it |
| the assistant's own memory | loaded at session start, outside the repository |
| **the docstrings** | read whenever the code is read, which is when it matters |

**The docstrings ARE the specification**, and the tests are the other
half: when you would have written a contract clause, write a test.

## Where the detail lives

| you want | read |
|---|---|
| the principles and the honest limits | `CLAUDE.md` |
| what the reviewer holds this to | `AGENTS.md` |
| what a description may contain | `docs/spec/profile-contract-v6.md` |
| what changed, in order | `CHANGELOG.md` |
| what must still hold, measured | `tests/kpi/ledger.json` and `tools/measurements/kpi_run.py` |
| the project in plain language | `STATUS.md` |

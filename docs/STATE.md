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
| suite | 16,645 collected on batch 4o's second fix round (the independent verify of the fix round, LANE I4m RULINGS 27 (1): its gate file adds 8 cases to the fix round's 16,637; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 367 files, every file in exactly one shard), its whole suite on `4324aced` green in five shards: 16,574 passed, 56 skipped and 15 expected to fail, the 16,645 collected. The fix round's whole suite on `fcd01166` read 16,565 passed, 56 skipped, 15 expected to fail and 1 failed, the source-loading guard's count of files loaded as modules (59 against 58 recorded: the fix round's pool test loads the committed generation oracle), moved to 59 in this round. The fix round's 16,637 (Codex's review of the sealed head `015d5003`: the three gate files of its three High items add 15 cases to the seal's 16,621, and the sibling sweep's held column in the age reach one more; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 366 files, every file in exactly one shard), its whole suite run after the fix round. The sealed head's whole suite read 16,544 passed, 56 skipped, 14 expected to fail and 7 failed, each failure this batch's (LANE I4m RULINGS 22): six cases of lane SH2's five age tails, read as held by the table of the date-count question the tests-only fix 3355025d put them in, fixed; and the perioperative export's day counts, which the zoo's truthful `yes` holds (owner lane CZ-H2), marked expected to fail, strict, so 15 expected to fail from the fix round. The seal's 16,621 (`3355025d` with the seal's records, 363 files): batch 4n's 16,068 and the 553 this batch adds, named below. Batch 4n's 16,068 were collected on its second fix round `f18c3638`, whose whole suite ran green in five shards (15,998 passed, 56 skipped, 14 expected to fail; its 3 gate cases, P4-D442, on the fix round's 16,065, whose 8 gate cases stand on the 16,057 of batch 4n's merged head `322b92de`, which held lane HB's 74 cases and lane CL's and the batch's owed records' 9 on batch 4m's 16,075, less lane SPD's move of 120 cases into its slow drivers beside its 19 added, P4-D444; lane HB's branch read 16,149: lane HB's fix 4 of close round 2: one case added, LANE HB RULINGS 14's differential case of the form term, three gate cases amended to rule 42's restatement and renamed, and the seven cases of ordinary tables green again, P4-D442; lane HB's fix 3 of close round 2: 3 gate cases on the repair's 16,145; lane HB's repair of close round 2: 7 gate cases on close round 2's 16,138; lane HB's close round 2: 8 gate cases on the close round's 16,130, which held lane HB merged on batch 4m, its close round included: its gate, its hunt's files and the cases it amended, 55 on batch 4m's 16,075, which held lanes UN-1a, CODES-1, GG, CHb, SH2 and UN-1b on batch 4l part b's 15,564; counted by `pytest --collect-only` under Python 3.11 and placed by `tools/ci/shards.py --of 5 --prove`, 357 files, every file in exactly one shard). Lane MR's rules page adds 29 cases in one new file (its branch read 16,104 on batch 4m's 16,075); Lane PL's gate and the cases it amended add 93 (its branch read 16,167 on batch 4m's 16,074), and the merge's two cases pinning its loader's and its profiler's split of a pool 2 more; lane SH3's gate and the cases it amended add 109 (its branch read 16,184 on batch 4m's 16,075); lane CZ-D's gate adds 68 cases in one new file (its branch read 15,841 on batch 4m's records head `a5702b71` before its repair 3 added one); lane CZ-H's gate and the cases it added and amended add 181 (its branch read 15,955 on batch 4m's records head `a5702b71`), and the merge's three gate cases of its limit (h) 3 more; lane MPOL2's page adds 10 cases to its test file (its branch read 15,784 on batch 4m's records head `a5702b71`); lane MPp's gate and the cases it added and amended add 54 (its branch read 16,129 on batch 4m's 16,075); with the owes of the merges, lane MR's two pinned helper legs and lane SH3's two street cases, they make batch 4o's 553. One process took about 66 minutes when the suite held 9,138 cases (ledger `K-P0-10` carries the seconds); at 13,553, on `b85200be` (batch 4f), the five shards took 24.5 to 48.5 minutes each beside other lanes' runs. In CI it runs as **five shards**. Re-measure here whenever the count moves |
| KPIs | `tests/kpi/ledger.json`: 270 KPIs over phases 0-4, stages 1, 2, 2b, 3, 3b, 4, 5 and 6, the terminal, the health data zoo and the broad between-columns program, 36 of them headlines under a cap of 36 (raised from 30 at 3b.K, plan P4-D364, for `K-S3-38`; from 31 to 35 by the orchestrator's recorded call D15 of the December plan, plans P4-D397, P4-D399 and P4-D398, for `K-S8-01`, `K-HZ-01`, `K-BC-01` and `K-BC-02`; to 36 for lane S5a's `K-S5-01`, plan P4-D437; the owner may veto any); 214 green, 40 open, 16 limits the owner accepted, as batch 4o's ledger reads at its second seal (stamped on its merged head `c47a6aee`, on its tests-only fix `3355025d` and on its two fix rounds' heads `fcd01166` and `4324aced`, each entry on the head its proof ran on), lane PL's `K-HZ-19` (green), lane SH3's `K-HZ-20` (open), lane CZ-D's `K-HZ-17` (open), lane CZ-H's `K-HZ-16` (open since the seal, LANE I4m RULINGS 20 (3)) and lane MPp's `K-S6-14` (green) among them. Of the 40 open, as each one's `target_stage` reads: 34 have the stage or lane that owns the whole (`K-HZ-16` lane CZ-H2, the recorded keys batch 4o's merges moved on its five forms, `K-HZ-17` lanes CZ-B, CODES-2 and SX, each its stated limit (lane PL's part closed at batch 4o's stamp), `K-HZ-20` lane ID-ROOM2, on the orchestrator's ruling, its one record-number key, a live leak on the base too, and eleven of its twin's twenty misses at 20,000 rows, lane HB2 the other nine (two of a held county code's layout census; seven of a held column of ages written with a unit letter, whose twin the top-code writes in its own values since batch 4o's first fix round's generator change, `90y` and `1079m` on 240 cells each equal to a real one, P4-D454), `K-P4-06` and `K-S6-01` stage 6, `K-P4-22` stage 3, `K-P4-23` the carried reference vectors, `K-S1-06` and `K-S4-04` stage 4, `K-S3-64` lane HB2, its held padded age and `reglistmixR`'s own validation, `K-HZ-13` lane HB2, lane HB's stated limits, `K-S3-44` lane S4bc2, its one census miss, `K-S4-09` the scale gate, lanes SR, SG and SV, then SX, its describe part OPEN-WORSE on 589f3d72 in the night of 2026-10-27 under Python 3.11 (20.3 traced bytes a cell at 200,000 rows against 17.7, and 20.3 on batch 4l part a's head in the night of 2026-10-29 and on part b's 591b356f in the night of 2026-10-30; 20.4 on batch 4n's merged head 322b92de on 2026-11-04, traced peak 204,367,671 bytes, the first reading since 591b356f, so batches 4m and 4n together; 20.4 on its first fix round's head 7c0e8a26 (traced peak 204,368,975 bytes) and on its second, f18c3638 (204,366,849 bytes); 20.6 on batch 4o's merged head c47a6aee (traced peak 206,029,374 bytes), the describe-side changes of lanes PL, SH3 and CZ-H, not split per lane; its two fix rounds' small describe changes not traced, their reading owed; batch 4j's head read 2,375 MB resident at 2,000,000 x 50 with every candidate open in the night of 2026-10-26, lane SX's to win back), `K-S8-01` the terminal's lanes TT and TS, `K-HZ-01` and `K-HZ-02` the lanes each zoo failure names, lane G2T2 for the one 20,000-row failure that had none at batch 4l, lanes CZ-H2 and CZ-B for the four batch 4o's stamp found (named at its seal, LANE I4m RULINGS 20 (2); 0 without an owner on `fcd01166`), lane MG for the person census and lane PS2 for what lane PS left held or pooled, `K-S6-02` and `K-S6-03` lane BT2 (batch 4m's merged code moved both, on the chain's switched path alone), `K-HZ-06` lane ID-ROOM2 (P4-D457), `K-HZ-10` and `K-HZ-11` as each reads, and `K-BC-01` to `K-BC-13` the broad between-columns program's checkpoint 4); 1 is owned in part (`K-2B-47`: stage 3 the carried fidelity items, lane RT2 the date remainder, 9 missed checks against its bound of 6; its identifier-layout residue of 2026-09-19 has no stage set); 5 have none set (`K-2B-28`, `K-2B-49`, `K-S3-12`, `K-S3-22`, `K-S3-50`). By stage: stage 3's `K-S3-01` to `K-S3-25` (`K-S3-11`, the tail leak, a headline), lane HX's `K-S3-64`, lane HX2's `K-S3-65` and lane AQ's `K-S3-66`; stage 3b's `K-S3-30` to `K-S3-32` and `K-S3-34` to `K-S3-62` (`K-S3-33` retired; `K-S3-31`, the weekday, and `K-S3-38`, time of day, headlines); stage 4's `K-S4-02` to `K-S4-09`, `K-S4-11`, lane SG's `K-S4-12`, `K-S4-15` to `K-S4-22` (`K-S4-10`, `K-S4-13` and `K-S4-14` reserved; `K-S4-03` a headline in `K-2B-14`'s place); stage 5's `K-S5-01`, a headline, and `K-S5-02` (lane S5a, P4-D437); stage 6's `K-S6-01`, lane BT's `K-S6-02` (layer L0's band totals behind the switch, P4-D429) and lane CHa's `K-S6-08`, the chain's tables part, green: no description its keyed draw can publish fixes or bounds a count of 1 to 10, the chain still behind its switch (P4-D418), lane MPp's `K-S6-14`, the moment layer under the owner's rule B behind the same switch, green (P4-D455), and lane CHv's `K-S6-04`, `K-S6-05` and `K-S6-10`, V12 checking each family behind the same switch (P4-D430); the terminal's `K-S8-01`, a headline, and `K-S8-04` (lane TI); the zoo's `K-HZ-01`, a headline, `K-HZ-02`, `K-HZ-03` and `K-HZ-05` (lanes E0a and E0c, P4-D431, with lane CZ-H's five forms, P4-D446: 98 kinds over 69 exports, judged at 20,000 rows with the shipped floor), 53 of 98 kinds passing and 158 failures over 45 kinds at 20,000 rows on batch 4o's merged head and on its first fix round's `fcd01166`, lane CZ-H's five forms among them (51 of 93 and 139 over 42 on batch 4m's merged code; 21, and 261 over 72, on lane E0c's head), every failure owned (the seal's two OWNERS lines, read on `fcd01166`), lane CODES-3's `K-HZ-04`, the zoo's identifier cells out of pattern, 0, lane ID-ROOM's `K-HZ-06`, twin identifier cells equal to or merging with a real one, 0 over every key, OPEN on the zoo's held dates by chance (P4-D432, P4-D434, P4-D442; owner lane ID-ROOM2, P4-D457), lane PS2's `K-HZ-07`, no date one to ten people or rows hold published, 0 over 60 tables (P4-D433), lane SH3's `K-HZ-20`, no age of 90 years or more published or written in any unit and no part of an address published, at 600 and 20,000 rows, OPEN on record numbers its values alone read as ages, 19,778 twin cells equal to a real one at 20,000 rows while their identifier question is open, as on the base, and on the twin's 20 misses at 20,000 rows, 13 older than the lane and seven since batch 4o's first fix round, all on one held column whose twin the top-code writes in its own values, as on 2af926ce (P4-D454), lane PL's `K-HZ-19`, levels one to ten people hold, none named, green (P4-D453), lane CZ-H's `K-HZ-16`, Safe Harbor dates in disguise over five invented forms, none shown and none in a twin cell, OPEN since batch 4o's seal on recorded keys its merges moved (owner lane CZ-H2; P4-D446), lane CZ-D's `K-HZ-17`, types, codes and flags over eight invented forms at 600 and 20,000 rows, OPEN on its stated limits (P4-D447), lane HB's `K-HZ-13`, held and unanswered columns' twins in their own valid layouts, OPEN-held at its stated limits (P4-D442), and lane SPD's `K-HZ-15`, lane SH's Safe Harbor number cases at 20,000 rows, 0 failing over 61 (P4-D444); the analyst battery's `K-BC-01` and `K-BC-02`, headlines, and `K-BC-03` to `K-BC-13` (lane E0b). `K-2B-42`, the oracle's independence, is bounded since batch 4c by a share, at most 0.363 of its scored functions close to shipped code, a changed policy whose larger allowance the orchestrator accepted and named (P4-D299). **One command re-measures them all:** `.venv/bin/python tools/measurements/kpi_run.py` (add `--slow` for timings and scale). Run it at every stage close: **a KPI that drops is a regression even when every test is green** |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request: Python 3.11 to 3.14 on Ubuntu and Windows and 3.14 on macOS, and the minimums job on 3.11 against the declared floors (lane DEP-1, merged 2026-10-20 at batch 4d, P4-D410, on lane MDEP's dependency page, P4-D409: the four runtime libraries numpy, pandas, pyarrow and scipy held to their byte-identity zones; until then five Pythons from 3.10). Since batch 4f (lane DEP-2, P4-D416) three jobs more, each required by `gate`: `bundle-build` (three platforms by four Pythons), `bundle-test` (four Pythons by three systems) and `numba-vectors` (three systems by four Pythons), 27 cells. Its first runs on PR #6 (2026-09-20) were red on what only CI could see -- tests asserting their own machine's answer, a 3.13-only spelling, Windows paths holding `AppData`, workbook cases failing where openpyxl is absent -- each repaired with a guard that now fails HERE. Batches 4h to 4j (pushed 2026-10-25) failed 26 of 86 jobs on CI-only causes, repaired by `8cd9b743` (the floor fixture steps aside without the package, the floor-of-eleven tests read the pages beside the test file, the bundle's invented table holds 20,000 rows; run 40274066871, 83 of 86) and `f677d6a0` (`K-S4-07`'s allocation bound 1.1, the gate's own allowance; run 40293692822, 86 of 86). Batch 4k (pushed 2026-10-26): run 40453073905, 86 of 86. Batch 4l (pushed 2026-10-29 21:00, both parts): run 40989180482, 81 of 86, red on Windows shard 2 (the stage-5 gate compared a next command's folder as text) and the minimums shard 4 (the zoo's leak scans read a workbook without openpyxl), both test-only, repaired at batch 4m (`e6b63074`). No job sets `timeout-minutes`, so each may run 360 minutes; local shards took 47 to 64 minutes at 591b356f, when shard 1 held lane SH's 45-minute test file (92.92 s since lane SPD, P4-D444, so those shard times are history), so the default stands, shards 1 and 5 watched (push critic 16). Batches 4m and 4n (pushed 2026-11-04 20:25 as one commit, `506249bf`): run 41955136439 on that head, success, 86 of 86. Batch 4o is sealed and not yet pushed: CI judges it on the push that carries it. A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
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
  column held and asked. OPEN, each with its
  owner and its numbers, none of them claimed closed: list keys beside a
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
  lane ID-ROOM2 (P4-D457); the held padded age `naaccr`, held
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
  7c0e8a26)
  and sequential keys with a constant prefix and suffix read as affixed
  numbers (19,998 of 20,000 twin cells real at 20,000 rows,
  the same on the pushed line), lane ID-ROOM2 (P4-D457); 23 twin tokens
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
  cell, 240 of them the top category's own values in the column's units
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
  being the residual the owner accepted, its twin meeting no moment
  until lane MPg's polish. A code
  column's 779 rare held codes come back as they are, privacy-neutral.
  Keys under five figures beside words over one value in three, lane
  LISTS (ZR.9); a candidate person column repeating a few values leaves
  the real table missing its own repetition pattern, lane PS3.
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
- **Relationships between columns are not carried.** Landing 6. The moment page written for it (plan P4-D413) states its own limits before any code: a refusal's residual under ruling R3; "own facts" as rulings R9 and R11 read them (a union that splits one column's small group across two regions counts that group's rows, 1 to 3 rows measured, while inside one region the witness refuses the measured cases where that reading would publish a count of two columns, exactly 3 rows and 1 to 9 rows); every published moment needs a proof (ruling R10), so none stands beside a slope the chain publishes outside its regions; the witness December can decide publishes almost nothing on the measured 50-column table (one region of 20 number columns and 38 of 50 families, every number column in a family where a slope may stand), the main fidelity risk before the stage-6 gate: with the witness `cho1` no region publishes, so no moment and (R12) no slope: 115 of 287 estimates at 200,000 rows on the seeded chain, against 134 walked with slopes, 202 polished and 213 for a fresh sample (P4-D421), E0b's ST2 to ST6 chains and ST1's at 200,000 rows unmeasured (lanes MPp and CHa); the oracle's moment comparison (4.6d) has never run, since the product publishes no moment (lanes MPp and CHb); and no average or correlation of a repeated measurement in December. Under ruling R12 (2026-10-20) the chain's slopes are published only inside a publishing region of the moment page, so while its GATE stays closed no chain slope is published in December, on any table (P4-D413, contract 4.6d.10's limit 6; 19 estimates at 200,000 rows, P4-D421). The chain's profile side (P4-D418) owes, each with its owner (the orchestrator, 2026-10-22 17:46 and 2026-10-23 12:17): RULE ONE_BAND's few-value columns, lane CHa2; `w_te`, lane A0b's 200,000-row leg; the subject question on a table of several rows a subject before stage 6, lanes MG, GR and ST; an independent check of 4.6b.8's cell-by-cell row hash and the sample key, which the oracle does not compute, lane CHb (built: its oracle hashes a cell of spaces and tabs as the empty text, and lane CHa's `chain.row_hashes` changed by one line to meet it, behind the switch). THE CHAIN'S GENERATOR, layer L1 (lane CHb, batch 4m, P4-D435), is built behind the same switch: every family table met at its published levels on the product's own twins (`K-S6-03`), whole real rows beside a fresh real sample (`K-S6-05`), every shipped twin the same bytes (the zoo at 600 rows, 192 files, and the goldens, at the merge). Its limits: a switched description of 1,000,000 or 2,000,000 rows cannot be made under any guard, `chain.describe` holding the whole table (lane CHa's follow-up with `K-S6-15`, before lane SX's scale gate; the generator at 2,000,000 rows projects to 1,976 MB); label scans that may grow quadratically at 2,000,000 rows, unmeasured (lane SX); and a stamp written inside its grain (lane PS2's date floor) is dealt at the grain's start and spelled inside it only as it leaves, so its family reads back off G16.6's table (the encounters' `discharge_ts` at 20,000 rows, measured at the merge), lane BT2's.
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
  which needs a published fact of the spelling. ACCEPTED (the
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
  cause.
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
  (identifier forms, not in lane HB's brief, for the orchestrator to
  name); the made-up dates of a held date column, and since lane HB the
  valid dates of a date's form, may equal real dates (an attribute, never
  a key: no owner, counted in `K-HZ-13`); an identifier written with spaces
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

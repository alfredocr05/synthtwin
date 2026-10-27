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
| suite | 14,125 collected (lane BT, 77 cases after its repair 2, on batch 4h's 14,048: lanes HX4, 88 cases, and SG, 119, merged on batch 4g's 13,841; counted by `pytest --collect-only` under Python 3.11 and 3.13 alike and placed by `tools/ci/shards.py --of 5 --prove`, 338 files, every file in exactly one shard). One process took about 66 minutes when the suite held 9,138 cases (ledger `K-P0-10` carries the seconds); at 13,553, on `b85200be` (batch 4f), the five shards took 24.5 to 48.5 minutes each beside other lanes' runs. In CI it runs as **five shards**. Re-measure here whenever the count moves |
| KPIs | `tests/kpi/ledger.json`: 247 KPIs over phases 0-4, stages 1, 2, 2b, 3, 3b, 4 and 6, the terminal, the health data zoo and the broad between-columns program, 35 of them headlines under a cap of 35 (raised from 30 at 3b.K, plan P4-D364, for `K-S3-38`; from 31 to 35 by the orchestrator's recorded call D15 of the December plan, plans P4-D397, P4-D399 and P4-D398, for `K-S8-01`, `K-HZ-01`, `K-BC-01` and `K-BC-02`; the owner may veto any); 201 green, 30 open, 16 limits the owner accepted, as the merged ledger of batch 4h reads. Of the 30 open, as each one's `target_stage` reads: 24 have the stage or lane that owns the whole (`K-P4-06` and `K-S6-01` stage 6, `K-P4-22` stage 3, `K-P4-23` the carried reference vectors, `K-S1-06` and `K-S4-04` stage 4, `K-S3-44` lane S4bc2, its one census miss, `K-S4-09` the scale gate, lanes SR, SG and SV, then SX, its describe part OPEN-WORSE on 8a02faa3 under Python 3.11, to be re-stamped on lane SR-A's merged code in a night window, the keyed subject cells, the person-column run and the column text lane H3's, `K-S8-01` the terminal's lanes TT and TS, `K-HZ-01` and `K-HZ-02` the lanes each zoo failure names, lane G2T2 for the one 20,000-row failure that had none, lane MG for the person census and lane PS2 for what lane PS left held or pooled, and `K-BC-01` to `K-BC-13` the broad between-columns program's checkpoint 4); 1 is owned in part (`K-2B-47`: stage 3 the carried fidelity items, lane RT2 the date remainder, 9 missed checks against its bound of 6; its identifier-layout residue of 2026-09-19 has no stage set); 5 have none set (`K-2B-28`, `K-2B-49`, `K-S3-12`, `K-S3-22`, `K-S3-50`). By stage: stage 3's `K-S3-01` to `K-S3-25` (`K-S3-11`, the tail leak, a headline), lane HX's `K-S3-64`, lane HX2's `K-S3-65` and lane AQ's `K-S3-66`; stage 3b's `K-S3-30` to `K-S3-32` and `K-S3-34` to `K-S3-62` (`K-S3-33` retired; `K-S3-31`, the weekday, and `K-S3-38`, time of day, headlines); stage 4's `K-S4-02` to `K-S4-09`, `K-S4-11`, lane SG's `K-S4-12`, `K-S4-15` to `K-S4-22` (`K-S4-10`, `K-S4-13` and `K-S4-14` reserved; `K-S4-03` a headline in `K-2B-14`'s place); stage 6's `K-S6-01` and lane CHa's `K-S6-08`, the chain's tables part, green: no description its keyed draw can publish fixes or bounds a count of 1 to 10, the chain still behind its switch (P4-D418); the terminal's `K-S8-01`, a headline, and `K-S8-04` (lane TI); the zoo's `K-HZ-01`, a headline, `K-HZ-02` and `K-HZ-03` (lane E0a), re-measured on batch 4f's merged code, 20 of 40 kinds passing at 600 rows and 28 at 20,000, 104 analyst checks failing, every failure owned; the analyst battery's `K-BC-01` and `K-BC-02`, headlines, and `K-BC-03` to `K-BC-13` (lane E0b). `K-2B-42`, the oracle's independence, is bounded since batch 4c by a share, at most 0.363 of its scored functions close to shipped code, a changed policy whose larger allowance the orchestrator accepted and named (P4-D299). **One command re-measures them all:** `.venv/bin/python tools/measurements/kpi_run.py` (add `--slow` for timings and scale). Run it at every stage close: **a KPI that drops is a regression even when every test is green** |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request: Python 3.11 to 3.14 on Ubuntu and Windows and 3.14 on macOS, and the minimums job on 3.11 against the declared floors (lane DEP-1, merged 2026-10-20 at batch 4d, P4-D410, on lane MDEP's dependency page, P4-D409: the four runtime libraries numpy, pandas, pyarrow and scipy held to their byte-identity zones; until then five Pythons from 3.10). Since batch 4f (lane DEP-2, P4-D416) three jobs more, each required by `gate`: `bundle-build` (three platforms by four Pythons), `bundle-test` (four Pythons by three systems) and `numba-vectors` (three systems by four Pythons), 27 cells. Its first runs on PR #6 (2026-09-20) were red on what only CI could see -- tests asserting their own machine's answer, a 3.13-only spelling, Windows paths holding `AppData`, workbook cases failing where openpyxl is absent -- each repaired with a guard that now fails HERE; run 39949505139 on `4682d6ad` (batch 4e) passed 59 of 59 jobs and run 39951917644 on `b85200be` (batch 4f) 86 of 86, DEP-2's bundle and numba cells first run there; run 39993807950 on `af69aaef` (batch 4g) 86 of 86, lanes CHa, CHo and ZR-a's first. A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
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
| 3 | **DONE 2026-09-23. The extremes, and the population floor.** Its review round closed 2026-09-24. Built as FIVE landings on five branches from one base — 3.1 the default floor of 11 and the floor holes, 3.2 the population floor and the person rule, 3.3 the numeric tail, 3.4 the date and clock tails, 3.5 the sentences — and integrated last. No numeric, date or clock column publishes either end now; a table under 100 is refused and one under 1,000 carries a notice it cannot turn off; no sentence carries a count a key withholds. **Lane HX, merged 2026-10-20 (batch 4d):** a column whose question offers `identifier` and is unanswered publishes no value, and the twin writes made-up record numbers there, until it is answered (`K-S3-64`; P4-D401). **Lane AQ, merged 2026-10-20 (batch 4d):** the questions file keeps every answer across rounds, so the same answers given in one round or in several write the same description, summary, questions file and twin, and a run that would drop a kept answer, or read the table another way than the run that wrote the file, refuses and writes nothing (`K-S3-66`; P4-D408). **Lane HX2, merged 2026-10-21 (batch 4e):** on a table of several rows a person, every value published beside a declared or candidate person column is counted in people, and a column holding a value one to ten people hold is held whole, the twin writing made-up values there, except the rungs and tail boundaries of a measurement or code column not attached to its subject, which are still judged in rows (the orchestrator's ruling of 2026-10-19, item 2: on `K-S3-14`'s repeated-measures table a score still publishes two rungs, each on 11 rows of 10 people; the limit below); a column declared as counted dates whose cells did not read so is held on every table (`K-S3-65`; P4-D406). **Lane HX3, merged 2026-10-22 (batch 4f):** route four's person question offers `code` in its first round, so a code column the person knows is answered there (`K-S3-66`, `K-HZ-02`; P4-D420). **Lane PS, merged 2026-10-22 (batch 4f):** dates and times beside a person column are described at a coarser grain their published facts choose, counted in people, and a held one's twin writes valid dates in its own layouts (`K-HZ-01`, `K-S3-65`; P4-D417). **Lane ZR-a, merged 2026-10-23 (batch 4g):** the zoo-fix reading page, where each new reading stands in the classifier, the questions it adds and what it may publish, written before its code (P4-D419). **Lane HX4, merged 2026-10-23 (batch 4h):** a column of lists written as record numbers is asked one question and held until answered: the register lists of the exposure found that day publish 0 of 40 keys at 600 and 20,000 rows, pure and with one word (`K-S3-64`; P4-D424) | MET: `tests/test_stage3_gate.py` (`K-S3-13`) and `K-S3-01` to `K-S3-15`, and `K-P3-03` and `K-2B-05` reached their targets on the way | done |
| 3b | **Dates keep their calendar shape.** Weekday, time of day, heaps and schedules, each a new published fact that must meet stage 3's floor. **3b.0 landed 2026-09-28**: on the gate's 11 filled ranges of days, seconds and moments the twin comes back with as many different ones -- the same ones where each tail's derived end is the real end, and where one stands a unit past it that unit in place of a real one inside (4 of the 11, plan P4-D358); over small filled columns about three in ten come back with fewer, MISSED (known limits) -- and every rank of a merged run stays inside its gap except where no placement inside the gaps meets the published count of different values (plan P4-D354, `K-S3-30`, `K-S3-39`). **3b.1 landed 2026-09-27**: a column of whole dates publishes its weekday census (plan P4-D355), and its twin meets it -- admissions' weekend share 14.7 per cent real against 14.8 twin where it was 28.5; since 3b.D1 the full-fill certificate is gone and a census is withheld only where a group holds fewer than three different dates, fewer than seven and a half a group on average, or no room beside a published hole (plan P4-D365, `K-S3-35`). **In on the integration branch since 2026-10-02:** 3b.K, the base every landing builds on (P4-D364); 3b.D1; 3b.G1, every tail publishes its pair and a date or clock tail ends at its pair's reach (P4-D375); 3b.T1, Excel's hour and the 12-hour clock read and written back (P4-D370); 3b.R0, numbers written in full (P4-D380); 3b.R1, the day-or-month and date-code questions (P4-D381); 3b.R3, workbook cells read as stored (P4-D382); D0, one weekday pass for every census of bins (P4-D366); T2 (3b.2-H), the hour census on moments (P4-D371); C1 (3b.5), clock columns with their census, heaps, step and codes (P4-D373); G3, the count pass's paid merge keeping its book (P4-D376); G2, the tail pair's wider cell (P4-D377); R2a, dates no member reads written back as written (P4-D383); R2K, the second key cut (P4-D386); D1b, the weekday census withheld where the count leaves too little room (P4-D388); G4, the subtraction guard dropped (P4-D390); the route-2 correction (P4-D390, P4-D373); D2, the weekday census on timestamp columns (P4-D367); R4, numbers that are dates, read as dates and written back as the same counts (P4-D384); R5, a trailing delimiter on one side read as the table's (P4-D387); J, the weekday and the hour of a moment met together (P4-D379); D3, the day-of-month census (P4-D368); R2b and R2c, the clock half and partial dates of the layout reader with Q6 (P4-D383); D4s, the count pass splitting the two tails' ranks first (P4-D369 part one); D4 (3b.6), dates that stand out, each listed date at its exact count (P4-D369, `K-S3-45` to `K-S3-47`); 3b.7, the shared clock and the joint member, each census counted on the clock a value is written on (P4-D378, `K-S3-53`); L1, codes and tables written as the source wrote them (P4-D390, P4-D384, `K-S3-61`); T3 (3b.4), the minutes and seconds of a timestamp counted and met with the hour (P4-D372, `K-S3-41`, `K-S3-42`), merged through lane J2, which meets them beside the weekday census on moments (P4-D391, `K-S3-62`); C2 (3b.5's second step), the minute of the hour on clock-only columns (P4-D374, `K-S3-48`, `K-S3-49`); merged 2026-10-15 (batch 4a), J3, repeated grids of timestamps meeting their counts (P4-D391), R6, a trailing delimiter closed `""` read and written back as the source closed it (P4-D387), and L2, a clock's form holding the one space before its marker (P4-D392); and, merged 2026-10-16 (batch 4b), L3, a stamp's form holding the space between its date and its clock (P4-D393). **The gate is met for the weekday on date columns** (`tests/test_stage3b_gate.py`, `K-S3-31`, `K-S3-32`): weekend share and weekday come back and no weekday count stands below the floor; time of day has landed on moments (3b.2-H) and on clock columns with their heaps (C1), its minutes and seconds on moments (T3 through J2) and its minute on clock columns (C2), and the dates that stand out on date columns (D4); the 3b finish test is met at 254f6419 (both gate files green; `K-S3-31`, `K-S3-38` and `K-S3-42` PASS, `K-S3-41` accepted-held); schedules remain | weekend share, hour of day and heaps come back; no calendar count below the floor | 6 |
| 4 | **The numeric path per stratum, not per row.** The ladder work happens once per distinct value. **Under way.** Before batch 4a: a large table's reading memory, three paths grown with the rows, the packing walk bounded and G5.5's sign repairs (P4-D387, P4-D389; `K-S4-02` to `K-S4-05`). **Lane S4b-num, merged 2026-10-15 (batch 4a):** the dense tail's push, the identity walk, G4's decimal codes and a register's quality report grow with the rows, every twin the same bytes (494 s to 13.7 s generating 100,000 dense-tail rows; 803 s to 32.6 s for 1,000,000 rows of decimal codes; P4-D377, P4-D387, P4-D390). **Lane S4c, merged 2026-10-15 (batch 4a):** `validate` prints and writes its report in pieces (798 MB at 997,770 register rows where it held 1,317; `K-S4-06`), and a dense tail's twin meets its published mean distance (G6.6.8 rule 4, `K-S4-07`; P4-D390, P4-D377). **Lane S4d, merged 2026-10-16 (batch 4b):** `describe` holds one answer per spelling, every description the same bytes (the 2,990,700-row register in 780 MB where it took 2,389; `K-S4-08`; P4-D390); lane S4b-num's work counts have their own KPI since then (`K-S4-15`, the orchestrator's decision; `K-S4-09` to `K-S4-14` are reserved by the December plan). **Lanes H1 and H2, merged 2026-10-19 (batch 4c):** padded code and record-number columns generate in linear time (`K-S4-16`, `K-S4-17`; P4-D402), and the packing walk reads the counts of one margin together, so a column of signed changes no longer stalls `generate` (`K-S4-18`, `K-S4-19`; P4-D403). **Lanes SR and XW, merged 2026-10-20 (batch 4d):** `synthtwin profile` reads and describes a big table one group of columns at a time, every description the same bytes (`K-S4-09` open, its describe part worse on 8a02faa3 under Python 3.11, lanes SR-A's (P4-D414) and H3's; `K-S4-11`; P4-D400), and the workbook twin is written as a stream, the same file byte for byte (`K-S4-22`; P4-D411). **Lane G2T, merged 2026-10-21 (batch 4e):** a number tail meets its own description on big tables -- the shared staircase, rule 4 on a crowded end and the windows it draws -- and the twin writes nothing past the published range (`K-S4-20`, `K-S4-21`; P4-D405). **Lane SR-A, merged 2026-10-22 (batch 4f):** a big table's group is read again by pyarrow's CSV reader and handed over only where a digest proves it the standard reader's reading, every description the same bytes (P4-D414). **Lane SG, merged 2026-10-23 (batch 4h):** `generate` holds the twin once, each finished column packed and the twin written a piece at a time, every twin the same bytes (`K-S4-12`, recorded; P4-D415). Open: `K-S1-06`, `K-S4-04`, lane S4b's calendar half, `validate` describing the file again (lane SV) and the number tails held by a width or the pair's reach, which keep the pushed staircase (lane G2T2; G2's dense tail at 1,000,000 rows closed by lane G2T, P4-D405, `K-S4-21`) | two million rows by fifty columns, end to end, under an hour (`K-S1-06`) | 8 |
| 5 | **The seam the interface needs.** Results become data with a rank decided once, before any sentence exists; a callable entry point returns results instead of printing them. **Its method is written, before any code (lane M5, merged 2026-10-19, batch 4c; P4-D395):** one result per run, its misses ranked once, an entry point that prints nothing | a caller distinguishes a good run from a bad one without reading prose; reports byte-identical | 13 |
| 6 | **Cross-column: the chain of floored family tables** (P4-D407, which supersedes P4-D394's pairwise rank correlation over cut indicators), with the patient layer and the moments beside it. **Inherits:** today a rank correlation of 0.747 comes back 0.027 (`K-S6-01`), and the pairing walk of three- and four-number cells (`K-P4-06`). **Measured and written before its code (batch 4d, merged 2026-10-20):** lane E0b's analyst battery, what an analysis of the twin gives back against a fresh sample and a shuffled twin (`K-BC-01` to `K-BC-13`, two headlines; P4-D398), lane BTp's layer L0, each eligible column meeting its band totals (P4-D404), and lane MBC's chain, the between-columns method with its settings (P4-D407). **Written before its code (batch 4e, merged 2026-10-21):** lane MG's patient page, several rows per patient with the visit trend and the derived parents first (P4-D412), and lane MPOL's moment page, numbers read finer than the bands under a proof, with ruling R12's amendment of the chain's slopes (P4-D413). **Built behind its switch, with its oracle (batch 4g, merged 2026-10-23):** lane CHa's chain profile side, which no user reaches (`K-S6-08`; P4-D418), and lane CHo's exact oracle with the moment route's class `cho1` (P4-D421); on a switched run at the merge the product's bands, family tables, anchors and words equal the oracle's, its floor holds and RULE W1 holds on the oracle's reading over the merge's sub-bands | every marginal unchanged; a known odds ratio comes back; the report names what it carries per relationship | 21 |
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
  group is **11** again (it was 1 since A-P4-37), and a lower one stays
  legal with its alarm. **Written-form extremes stay published** — text
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

- **Live HIPAA exposures found on 2026-10-23** (pre-existing). CLOSED by
  lane HX4 (batch 4h, P4-D424): register lists (`R100000`, `R1000`,
  `AB100`, padded `0100`; pure and with `;OTHER`), 0 of 40 keys in any
  file and 0 twin cells at 600 and 20,000 rows on the merged head
  `8503b843`. OPEN, lane SH (P4-D427): ages over 89 printed (45 CFR
  164.514(b)(2)(i)(C): max 103, p99 99 at 20,000 rows); a five-figure
  ZIP column losing P4-D401's hold to one word cell (9 or 10 ZIPs);
  placeholder shares (`-1`, `888`, `-99`) switching either off; ages in
  label roles (`NN years`); four-figure ZIPs (beside `99999` too);
  binary and constant roles. OPEN, lane CODES-3: a plain column of short
  prefixed keys (`R1000`, `AB100`), held while pure, publishes all 40
  beside one word cell (599 twin cells of 600; padded `0100` with words
  in a fifth of its cells, 32 of 40), measured on `af69aaef` and on the
  merged head at 600 and 20,000 rows. NOT BUILT, lane LISTS': keys under
  five figures beside words over one value in three, which ZR-a's page
  would read as a list publishing 40 of 40 (ZR.9).
- ~~**The description still names individuals.**~~ **CLOSED by landing
  3, 2026-09-23** (`K-P4-22`, `K-S3-11`). Its residual is open again by
  choice since plan P4-D375 publishes every pair: `K-S3-11` records 14
  edge-pinned and 8 pinned tails of its 105 cases, whose pairs give a
  reader back that tail's own outer values -- accepted under the owner's
  principle of 2026-10-01, never another column, and never which row
  except on a table sorted by that column (`row_order`).
- ~~**Spread too wide on normal-shaped columns.**~~ **CLOSED by landing
  3, 2026-09-23.** `K-P3-03` is GREEN: the twin's spread 0.04 to 0.20
  per cent from the published one at 5,000 rows and 0.09 to 0.16 at
  20,000.
- **Relationships between columns are not carried.** Landing 6. The moment page written for it (plan P4-D413) states its own limits before any code: a refusal's residual under ruling R3; "own facts" as rulings R9 and R11 read them (a union that splits one column's small group across two regions counts that group's rows, 1 to 3 rows measured, while inside one region the witness refuses the measured cases where that reading would publish a count of two columns, exactly 3 rows and 1 to 9 rows); every published moment needs a proof (ruling R10), so none stands beside a slope the chain publishes outside its regions; the witness December can decide publishes almost nothing on the measured 50-column table (one region of 20 number columns and 38 of 50 families, every number column in a family where a slope may stand), the main fidelity risk before the stage-6 gate: with the witness `cho1` no region publishes, so no moment and (R12) no slope: 115 of 287 estimates at 200,000 rows on the seeded chain, against 134 walked with slopes, 202 polished and 213 for a fresh sample (P4-D421), E0b's ST2 to ST6 chains and ST1's at 200,000 rows unmeasured (lanes MPp and CHa); the oracle's moment comparison (4.6d) has never run, since the product publishes no moment (lanes MPp and CHb); and no average or correlation of a repeated measurement in December. Under ruling R12 (2026-10-20) the chain's slopes are published only inside a publishing region of the moment page, so while its GATE stays closed no chain slope is published in December, on any table (P4-D413, contract 4.6d.10's limit 6; 19 estimates at 200,000 rows, P4-D421). The chain's profile side (P4-D418) owes, each with its owner (the orchestrator, 2026-10-22 17:46 and 2026-10-23 12:17): RULE ONE_BAND's few-value columns, lane CHa2; `w_te`, lane A0b's 200,000-row leg; the subject question on a table of several rows a subject before stage 6, lanes MG, GR and ST; an independent check of 4.6b.8's cell-by-cell row hash and the sample key, which the oracle does not compute, lane CHb.
- **Cells of three or four numbers** sit at 552 of 2,160 pair agreements
  outside their window and no above-count missed (lane G2T's shared
  staircase, P4-D405), the ledger's ceiling since batch 4f's records,
  against a target of 550 and 0 (`K-P4-06`, whose note keeps how stage 3
  moved it). The pairing walk is the open cause. Landing 6.
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
- **Stated limits given their owners at batch 4c (2026-10-19)** (the
  orchestrator's rulings on the critics of the batch 4b and CF4b pushes,
  and on push critic 9 and Codex's merge review of batch 4c, the owner
  may reverse any). J3's six published pairs that still miss -- 2,500
  stamps five minutes apart written four times at floor 11, and four
  grids fifteen minutes apart written four times, in one twin of three
  (P4-D391) -- are lane RT1's, 3b-REST's clock half. On Windows
  PowerShell 5.1 a printed command drops an empty value: a new stated
  limit of lane CF4b, owned by the terminal track's lane TT (P4-D397).
  `K-2B-47`'s date remainder misses 9 checks against its bound of 6, the
  same on 3d893032: lane RT2's, 3b-REST's calendar half (P4-D320).
  `K-S3-44`'s one census miss is lane S4bc2's (P4-D368). `K-2B-42` was
  GREEN at 175 of 485 oracle functions close to shipped code while the
  run read 297 of 873 against a count of 176, set over 371: it is now
  bounded by a share, 0.363 (176 of 485, the reference chosen, rounded
  up), a changed policy whose extra allowance -- up to 316 close
  functions at 873 scored, where the count allowed 176 -- the
  orchestrator accepted and named (P4-D299). The health data zoo's one
  failure at 20,000 rows that had no lane, the mixed result column's
  mean, which `validate` misses, is lane G2T2's since batch 4e's
  records: `validate` measures the twin's held-back numbers exactly as
  `generate` wrote them, kept to one figure before the point, their mean
  just under its window (`tests/health_zoo.py`'s OWNERS). A column of signed changes whose style
  question has no answer keeps the cell walk's styles, the recount
  naming the style miss: the forms lane FM's (P4-D403).
- **Stated limits given their owners at batch 4d (2026-10-20)** (the
  orchestrator's namings of 2026-10-19 and 2026-10-20, written at the
  batch's integration; the owner may reverse any). The clone install,
  which fetched pip's build backend unpinned, is gone: the offline
  bundle is the only install (lane DEP-2, P4-D416), and the install
  scripts run on Windows and macOS only in CI, where `bundle-test`
  installs each platform's bundle with the network denied (by pip's own
  options there, by the kernel on Linux). Free memory cannot be read
  without native code, so `doctor` weighs total memory: the terminal
  track's lane TT (both P4-D397). The register's peak growing about
  245 MB a million rows, and a text whose sightings past the bound are
  always more than 8,192 new texts apart answered once a row (P4-D390),
  were lane SR's or its follow-up's: SR closed at this batch, so both
  are lane H3's. Lane SR's own (P4-D400): describe's cost on a column
  whose values all differ, 0.8 to 0.9 KB a row at its peak, so
  `K-S4-09` stays OPEN with describe's part RED, and one wide note
  column read alone, about 2.7 GB at 2,000,000 rows and about 408 s a
  column at 1,000,000, are lane H3's (the identity walk's column text;
  lane SV's describe-once is the first cut); workbooks at scale, refused
  past `workbook.MAXIMUM_CELLS`, are lane XL's. `analyst_kit.chi2_sf`
  stops at 500 terms, 0.7 % off at 69,295 degrees of freedom and p 0.5:
  lane E0L's (P4-D398). The zoo's SNOMED ids answered `code` a round
  late: CLOSED by lane HX3 (P4-D420); their twin's codes the real never
  writes (2 codes on 14 cells at 600 rows at the zoo's own seed, on
  lane HX3's head as on batches 4f and 4g: HX3's 7 cells came from
  another fixture seed) stay CODES-1's.
- **Stated limits given their owners at batch 4e (2026-10-21)** (push
  critic 10's items and the lanes' close reports, the owners the
  orchestrator named; the owner may reverse any). A column a
  point-between-thousands answer declared, asked again under
  `read_as_now: measurement`: CODES-1 part C's; a questions file whose
  kept reading entry and name list are both deleted or both edited
  alike, read as a file older than P4-D408: lane AQ2's. The grouped
  describe's peak under 0.6 of the whole table's (0.51 to 0.56 on Python
  3.11, 0.53 to 0.58 on 3.13, macOS; 3.12, 3.14, Linux and Windows
  unmeasured), not SR's "under half": lane H3's (P4-D400). A column
  declared as counted dates with no present cell is named nowhere: lane
  ST's notice (P4-D406). What stage 5's result reads for the chain now
  P4-D407 supersedes P4-D394: lane CHv's (P4-D395). In the health data
  zoo, lane HX2's count in people pools two person censuses (the census
  in subject bands is lane MG's) and holds two code columns whole; its
  held dates and times are lane PS's, merged at batch 4f (below). Lane HX2's stated limits (P4-D406): (1) the pages
  that explain the floor still say a value one person holds is published
  with the count of their rows, an overstatement beside a person column,
  where it is held: lane MG's; (2) a table of ten people or fewer whose
  person question is open counts the columns not attached to its
  candidate (visit dates, measurements) in rows: the orchestrator's to
  decide since lane PS (P4-D417); (3) a held date or time column's twin
  writing figures no date parser reads (`4191-54-63`, `77:21`): CLOSED
  by lane PS (P4-D417); (4) the identifier generator
  misses published forms on held twins (`GENERATOR_LIMITS` in the
  `K-S3-65` driver; a held count written two ways missing
  `type.all_whole_numbers`): CODES-1 part C's. `K-S4-09`, re-measured on
  8a02faa3 under Python 3.11 in the night window of 2026-10-21, is
  OPEN-WORSE: the mixed describe peak projects to 2,694.2 MB at
  2,000,000 x 50, 19.6 traced bytes a cell against 17.7 (`K-S4-11`
  passes, 6,151.6 s): lane SR-A (P4-D414, merged at batch 4f) reads a
  group again with pyarrow, its re-stamp on the merged code a night
  window's. `profile.build_document` keeping each repeating subject
  column's keyed cells for the whole describe (about 2,000,000 strings
  at 2,000,000 rows), and `K-S4-09` with a person column, are lane H3's
  (the orchestrator's addendum of 2026-10-22: on H3's build head the
  2,000,000 x 50 describe with a declared person column was stopped by
  its guard at 2,400 MB).
- **Dates and times beside a person column, pooled in people** (lane
  PS, P4-D417, merged at batch 4f). Such a column is described at a
  coarser grain its published facts choose, or held with a twin of
  valid dates in its own layouts; no count of one to ten people is
  left to subtraction, and absent spellings stay absent. Still so,
  each with its owner (lane PS2 is lane PS's follow-up, the
  time-of-day and weekday censuses counted in people; the owners the
  orchestrator named on 2026-10-23, written at batch 4g's records): a
  stamp of a few evenly filled hours misses its count of different
  values and its count at midnight (`wearables` at 20,000 rows: 32 of
  39 hours, 1,208 rows at midnight against 515), lane PS2; a
  measurement attached to its person (`labs`' `viral_load`) is held
  whole with made-up numbers in its layouts, lane PS2; the time of day
  and the weekday of a stamp pooled at the day or coarser are not
  described (admit hour TVD 0.37 at 200,000 rows) and the pooled tails
  are drawn inside their end bucket (635 rows on one day against 80),
  lane PS2; a birth date beside about four people a year is held with
  no span and drawn from 2000 to 2029, lane PS2 (a rung of five or ten
  years); the missing spellings of a pooled column print as the base's
  held block printed them, lane PS2; a held column's length no valid
  date has is missed and named (three people's `pending`: `min_length`
  7 against 10), CODES-1 part C's (`GENERATOR_LIMITS`); a stamp with
  UTC offsets publishes no count at its rung, lane DST; a table of ten
  people or fewer whose person question is open still publishes per
  rows (P4-D406's limit (2)), the orchestrator's to decide.
- **Lists of record numbers (lane HX4, P4-D424), still so:** values no
  route reaches (names, dotted ICD codes) or lists split by `+`, `^`,
  `~`, `/`, `.` or `;;` (the last three: 1 of 40 at 600 rows, 13 twin
  cells), and a held list written without its mark (11 of 600 twin
  cells against 398), lane LISTS'; codes `101` to `106` in lists
  published as categories, as before; chance equality of a made-up
  record number (2 to 7 twin cells at 20,000 rows) and `all_whole_numbers`
  beside one list cell, CODES-1 part C's; prices: `1,0001` decimal
  commas and a count column with one `a;b` cell held until answered.
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
  of 12 patients outright (under 100 people); the library call without
  subjects, the validator's, still publishes the 68 `K-S3-14` holds.
- **A name, street address or birth date is held beside a patient
  key, declared or asked about by any question offering `identifier`,
  and published where nothing says who the rows are.** Beside a subject column, of any number of people,
  every published value, written form, remainder and census entry is
  counted in people (plan P4-D406, `K-S3-65` at 0), but for the rungs and
  tail boundaries of a measurement or code column not attached to its
  subject, still judged in rows (the limit above); a long table whose
  only clue to the person is the name itself has no people to count in:
  214 real values over 600 and 20,000 rows (`K-S3-64`'s stated shapes),
  names and addresses owned by CODES-2's allowlist, birth dates by
  CODES-1 part C.
- **Dates published as plain numbers when a declared date count is
  declined: CLOSED by lane HX2** (plan P4-D406, contract NF127): such a
  column is held on every table and named in the screen, the summary
  and the questions file's `held` section.
- **A record-number key written beside `-1` gets a twin that misses its
  published forms** (validate exit 3), declared or held until answered:
  on 68dae22f a declared key of 1,200 rows wrote fewer than 11 of its
  1,176 six-figure forms, and lane HX's hold reaches such a key (plan
  P4-D401). So does a telephone number opening `+` (its `+` layout) and
  a key exported as `100001.0` (the twin writes a figure after the
  point). Lane CODES-1 part C owns them.
- **A second record number beside a declared person column is held**
  (plan P4-D406): each of its values is one person's, so the column is
  described as record numbers counted in people and publishes none
  (`K-S3-64`, 0 at 600 and 20,000 rows).
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

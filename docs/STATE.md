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
| suite | 12,521 collected (lane AQ at its second repair round, on lane HX's close: the gate of the questions file keeping every answer across rounds and `K-S3-66`'s test, 59 more). One process took about 66 minutes when the suite held 9,138 cases (ledger `K-P0-10` carries the seconds); at 12,178, on `3d893032` (batch 4a), the five shards took 20.7 to 30.5 minutes each, 124.6 minutes summed and 30.5 end to end, beside other lanes' runs. In CI it runs as **five shards**, the heaviest about 20 minutes. Re-measure here whenever the count moves |
| KPIs | `tests/kpi/ledger.json`: 217 KPIs over phases 0-4, stages 1, 2, 2b, 3, 3b and 4 and the terminal, 32 of them headlines under a cap of 32 (raised from 30 by the orchestrator at 3b.K, plan P4-D364, for `K-S3-38`, time of day, which landed with 3b.2-H; and from 31 by the orchestrator's recorded call D15 of the December plan, plan P4-D397, for the terminal's `K-S8-01`, the owner may veto it); 187 green, 14 open, 16 limits the owner accepted. Of the 14 open, as each one's `target_stage` reads: 8 have the stage or lane that owns the whole (`K-P4-06` and `K-S6-01` stage 6, `K-P4-22` stage 3, `K-P4-23` the carried reference vectors, `K-S1-06` and `K-S4-04` stage 4, `K-S3-44` lane S4b, `K-S8-01` the terminal's lanes TT and TS); 1 is owned in part (`K-2B-47`: stage 3 owns the carried fidelity items, its residue of 2026-09-19, the identifier-layout misses, has no stage set); 5 have none set (`K-2B-28`, `K-2B-49`, `K-S3-12`, `K-S3-22`, `K-S3-50`). Stage 3's are `K-S3-01` to `K-S3-25`, one of them a headline (`K-S3-11`, the tail leak); stage 3b's `K-S3-30` to `K-S3-32` and `K-S3-34` to `K-S3-62` (`K-S3-33` retired with the weekday certificate), `K-S3-31` (the weekday) a headline in `K-2B-22b`'s place and `K-S3-38` (time of day) a headline; stage 4's `K-S4-02` to `K-S4-08` and `K-S4-15` (`K-S4-09` to `K-S4-14` reserved by the December plan), `K-S4-03` a headline in `K-2B-14`'s place; the terminal's (stage 8's ids, lane TI) `K-S8-01`, a headline, and `K-S8-04`. **One command re-measures them all:** `.venv/bin/python tools/measurements/kpi_run.py` (add `--slow` for timings and scale). Run it at every stage close: **a KPI that drops is a regression even when every test is green** |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request, five Pythons across Ubuntu, Windows and macOS. **It saw stages 1, 2 and 2b for the first time on 2026-09-20 (PR #6, run 35508922164): every static check green, every test cell red on three defects, all three repaired.** Its **second** run (35541541720) was red again on a deeper layer, all of it in the tests: two that asserted the answer for the machine they ran on, a `Path.read_text(newline=)` that exists only on 3.13 while the floor is 3.10, seventeen Windows failures caused by a temporary path containing `AppData` (which contains a sheet name the test forbade), and about 25 workbook cases that failed instead of skipping where openpyxl is absent. All repaired, each with a guard that now fails HERE rather than in CI. The suite is sharded five ways since, so a cell should cost about 13 minutes rather than up to three hours. **Its third run (35670708722, on `eaff15f`, 2026-09-22) passed 69 of 69 jobs, and run 36743015674 on `82b1f1a`, stages 3 and 3b, passed 69 of 69 on 2026-09-30.** A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
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
| 3 | **DONE 2026-09-23. The extremes, and the population floor.** Its review round closed 2026-09-24. Built as FIVE landings on five branches from one base — 3.1 the default floor of 11 and the floor holes, 3.2 the population floor and the person rule, 3.3 the numeric tail, 3.4 the date and clock tails, 3.5 the sentences — and integrated last. No numeric, date or clock column publishes either end now; a table under 100 is refused and one under 1,000 carries a notice it cannot turn off; no sentence carries a count a key withholds | MET: `tests/test_stage3_gate.py` (`K-S3-13`) and `K-S3-01` to `K-S3-15`, and `K-P3-03` and `K-2B-05` reached their targets on the way | done |
| 3b | **Dates keep their calendar shape.** Weekday, time of day, heaps and schedules, each a new published fact that must meet stage 3's floor. **3b.0 landed 2026-09-28**: on the gate's 11 filled ranges of days, seconds and moments the twin comes back with as many different ones -- the same ones where each tail's derived end is the real end, and where one stands a unit past it that unit in place of a real one inside (4 of the 11, plan P4-D358); over small filled columns about three in ten come back with fewer, MISSED (known limits) -- and every rank of a merged run stays inside its gap except where no placement inside the gaps meets the published count of different values (plan P4-D354, `K-S3-30`, `K-S3-39`). **3b.1 landed 2026-09-27**: a column of whole dates publishes its weekday census (plan P4-D355), and its twin meets it -- admissions' weekend share 14.7 per cent real against 14.8 twin where it was 28.5; since 3b.D1 the full-fill certificate is gone and a census is withheld only where a group holds fewer than three different dates, fewer than seven and a half a group on average, or no room beside a published hole (plan P4-D365, `K-S3-35`). **In on the integration branch since 2026-10-02:** 3b.K, the base every landing builds on (P4-D364); 3b.D1; 3b.G1, every tail publishes its pair and a date or clock tail ends at its pair's reach (P4-D375); 3b.T1, Excel's hour and the 12-hour clock read and written back (P4-D370); 3b.R0, numbers written in full (P4-D380); 3b.R1, the day-or-month and date-code questions (P4-D381); 3b.R3, workbook cells read as stored (P4-D382); D0, one weekday pass for every census of bins (P4-D366); T2 (3b.2-H), the hour census on moments (P4-D371); C1 (3b.5), clock columns with their census, heaps, step and codes (P4-D373); G3, the count pass's paid merge keeping its book (P4-D376); G2, the tail pair's wider cell (P4-D377); R2a, dates no member reads written back as written (P4-D383); R2K, the second key cut (P4-D386); D1b, the weekday census withheld where the count leaves too little room (P4-D388); G4, the subtraction guard dropped (P4-D390); the route-2 correction (P4-D390, P4-D373); D2, the weekday census on timestamp columns (P4-D367); R4, numbers that are dates, read as dates and written back as the same counts (P4-D384); R5, a trailing delimiter on one side read as the table's (P4-D387); J, the weekday and the hour of a moment met together (P4-D379); D3, the day-of-month census (P4-D368); R2b and R2c, the clock half and partial dates of the layout reader with Q6 (P4-D383); D4s, the count pass splitting the two tails' ranks first (P4-D369 part one); D4 (3b.6), dates that stand out, each listed date at its exact count (P4-D369, `K-S3-45` to `K-S3-47`); 3b.7, the shared clock and the joint member, each census counted on the clock a value is written on (P4-D378, `K-S3-53`); L1, codes and tables written as the source wrote them (P4-D390, P4-D384, `K-S3-61`); T3 (3b.4), the minutes and seconds of a timestamp counted and met with the hour (P4-D372, `K-S3-41`, `K-S3-42`), merged through lane J2, which meets them beside the weekday census on moments (P4-D391, `K-S3-62`); C2 (3b.5's second step), the minute of the hour on clock-only columns (P4-D374, `K-S3-48`, `K-S3-49`); merged 2026-10-15 (batch 4a), J3, repeated grids of timestamps meeting their counts (P4-D391), R6, a trailing delimiter closed `""` read and written back as the source closed it (P4-D387), and L2, a clock's form holding the one space before its marker (P4-D392); and, merged 2026-10-16 (batch 4b), L3, a stamp's form holding the space between its date and its clock (P4-D393). **The gate is met for the weekday on date columns** (`tests/test_stage3b_gate.py`, `K-S3-31`, `K-S3-32`): weekend share and weekday come back and no weekday count stands below the floor; time of day has landed on moments (3b.2-H) and on clock columns with their heaps (C1), its minutes and seconds on moments (T3 through J2) and its minute on clock columns (C2), and the dates that stand out on date columns (D4); the 3b finish test is met at 254f6419 (both gate files green; `K-S3-31`, `K-S3-38` and `K-S3-42` PASS, `K-S3-41` accepted-held); schedules remain | weekend share, hour of day and heaps come back; no calendar count below the floor | 6 |
| 4 | **The numeric path per stratum, not per row.** The ladder work happens once per distinct value. **Under way.** Before batch 4a: a large table's reading memory, three paths grown with the rows, the packing walk bounded and G5.5's sign repairs (P4-D387, P4-D389; `K-S4-02` to `K-S4-05`). **Lane S4b-num, merged 2026-10-15 (batch 4a):** the dense tail's push, the identity walk, G4's decimal codes and a register's quality report grow with the rows, every twin the same bytes (494 s to 13.7 s generating 100,000 dense-tail rows; 803 s to 32.6 s for 1,000,000 rows of decimal codes; P4-D377, P4-D387, P4-D390). **Lane S4c, merged 2026-10-15 (batch 4a):** `validate` prints and writes its report in pieces (798 MB at 997,770 register rows where it held 1,317; `K-S4-06`), and a dense tail's twin meets its published mean distance (G6.6.8 rule 4, `K-S4-07`; P4-D390, P4-D377). **Lane S4d, merged 2026-10-16 (batch 4b):** `describe` holds one answer per spelling, every description the same bytes (the 2,990,700-row register in 780 MB where it took 2,389; `K-S4-08`; P4-D390); lane S4b-num's work counts have their own KPI since then (`K-S4-15`, the orchestrator's decision; `K-S4-09` to `K-S4-14` are reserved by the December plan). Open: `K-S1-06`, `K-S4-04`, lane S4b's calendar half, `validate` describing the file again (lane SV) and G2's dense tail at 1,000,000 rows (lane G2T) | two million rows by fifty columns, end to end, under an hour (`K-S1-06`) | 8 |
| 5 | **The seam the interface needs.** Results become data with a rank decided once, before any sentence exists; a callable entry point returns results instead of printing them | a caller distinguishes a good run from a bad one without reading prose; reports byte-identical | 13 |
| 6 | **Cross-column, pairwise.** Rank correlation over cut indicators, applied as a reordering of values already generated. **Inherits:** today a rank correlation of 0.747 comes back 0.027 (`K-S6-01`), and the pairing walk of three- and four-number cells (`K-P4-06`) | every marginal unchanged; a known odds ratio comes back; the report names what it carries per relationship | 21 |
| 7 | **Higher-order structure.** Design pending measurement (four prototypes scored as this page was written) | a known three-way interaction comes back with the right sign, or the limit declared per relationship | 25 |
| 7b | **Higher-order structure, chosen.** A declared model plus one cross-tabulation for the outcome; the cross-column floor is ABOVE one, which is what lifts the reviewer's veto | a known three-way comes back at the real table's own estimate; no published cell names one subject | 25 |
| 8 | **The screen.** The bundled toolkit with its scripting engine STRIPPED at startup — seventeen commands deleted, proven unrebuildable, mutation-tested one per command. The strip is the deliverable, not the toolkit. **The terminal takes stage 8's ids (the orchestrator's recorded call D15 of the December plan; the owner may veto it). Lane TI, merged 2026-10-16 (batch 4b):** one install command per system keeping the hash-checked offline install, `python -m synthtwin`, `synthtwin doctor`, and `profile` naming the next command (P4-D397; `K-S8-01`, a headline, open toward lanes TT and TS; `K-S8-04`) | `tk.call`/`tk.eval` banned by the scanner; a table whose column name is an injection string has no effect | 33 |

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

- ~~**The description still names individuals.**~~ **CLOSED by landing
  3, 2026-09-23.** No numeric, date or clock column publishes either
  end, and the default smallest group is 11, so nothing a floor of one
  used to name is named: `K-P4-22` reads 147 published levels of one row
  AT A FLOOR OF ONE and 0 at the default, and `K-S3-11` walks 105 cases
  of the tail battery without one published value, summary line or
  report line equal to an outermost value of the real column. Its one
  stated residual, `edge_pinned`, which plan P4-D346 closed, is open
  again by choice since plan P4-D375 publishes every pair: `K-S3-11`
  records 14 edge-pinned and 8 pinned tails of its 105 cases, whose
  pairs give a reader back that tail's own outer values -- accepted
  under the owner's principle of 2026-10-01, never another column, and
  never which row except on a table sorted by that column, whose
  description publishes the order (`row_order`). A floor lowered to one
  still names what it always named, which is what lowering it asks for.
- ~~**Spread too wide on normal-shaped columns.**~~ **CLOSED by landing
  3, 2026-09-23.** There is no published extreme to draw a straight line
  to: the outer rows are read through the shape fitted to their two
  published moments. `K-P3-03` is GREEN — nothing missed at 5,000 or at
  20,000 rows and the twin's spread 0.04 to 0.22 per cent from the
  published one, against 1.1 to 3.8 per cent before and 10 of 20
  columns missing their own spread check at 20,000 rows.
- **Relationships between columns are not carried.** Landing 6.
- **Time of day inside timestamps:** a column of moments on its own
  clock publishes its hour census and its twin meets it (P4-D371,
  `K-S3-38`); moments in the joint member, wholly at midnight, without
  both tails or with a middle half under four days still spread over
  the day.
- **Cells of three or four numbers** sit at 579 of 2,160 pair
  agreements outside their window and 3 above-counts missed, against a
  target of 550 and 0 (`K-P4-06`). Stage 3 moved it twice: the numeric
  tail took it to 556 and 1, and the listing rule of P4-D346 put it at
  579 and 3, because a position whose tail may no longer name its values
  says its shape instead and every pair agreement of that position moves.
  The pairing walk is the open cause. Landing 6.
- **A short list of carried edge cases** fails the twin's own check on
  one shape each: two date-width allocations, one identifier layout, a
  sign band given more slots than it has numbers. The known-miss entry
  of the ledger names them. And one that fails no check, as no end is
  published: a date or clock tail's derived end can stand past the real
  column's first or last value, so the twin writes a unit the real
  column never reached and holds a real one fewer inside -- 12 of 36
  cases of twelve filled-range shapes at every seed, one unit out there,
  one or more elsewhere (P4-D354); of 316 twins of 158 small filled ISO
  columns, 224 hold as many days as the real column, 61 the same days,
  and 90 fewer, both distinct counts MISSED (P4-D358); a range filled
  in every day or month but a declared-missing one comes back a unit
  short the same way, 6 of 600 twins of a seeded battery. And a tail rank
  whose stratum is one declared-missing day, month or quarter writes an
  absent cell, 5 to 13 checks missed, at a rate that rises with the
  floor: about 1 twin in 40 whose missing unit is published at a floor
  of 11, 1 in 5 to 1 in 3 at 36 -- or, where the twin writes that day in
  another width than the absent spelling, a present day one more than
  published, both distinct counts MISSED (4 of 596 day-first twins of a
  seeded battery, all at 36); a moment counted in minutes on a member
  with one mark is written with an absent spelling it lands on, 8 to 11
  checks missed on 9 of 25 twins; and
  where the count pass's splits break a tail's summed window it moves
  nothing, so a count G12.5 holds exactly is MISSED, 6 of 1,200 twins of
  a floor-50 family holding 1.5 to 2.4 times it -- each held by
  `tests/test_stage3b_gate.py` (P4-D358). And one more that fails no
  check, accepted as a stated limit (P4-D377): a twin can write a far
  cell one figure wider than every real cell, as 110cb46's twin of the
  same seed does -- a padded far cell's leading zero where the width walk
  does not stand, on 382 of 1,080 padded twins, ten of them twins the
  width rule moves, or a far value past the real end, on 25 more it moves
  on its batteries; none is wider than 110cb46's (`K-S3-22` holds that at
  nought on its own battery) -- so code reading such a column at a fixed
  width may meet one wider far cell.
- **ISO moments at midnight can come back a day short where the count
  pass merges, and validate cannot report it** (plans P4-D367 and P4-D369
  part one). Since the count pass splits the two tails' ranks first, 5 of
  2,360 twins with one mark (from 81) and 2 of 549 with both (from 21)
  hold a day fewer while G7.9 makes up the count of texts with a mark, so
  no check is MISSED; each is where the twin draws past the rules'
  expectation and the pass merges (strict xfail in
  tests/test_stage3b_split_order.py).
- **Moments at a million rows can come back short of their hours**
  (plan P4-D379, lane J, merged 2026-10-13). Beside a weekday census,
  G7.3g step 3's escape paid back now meets both censuses on every
  measured column at floors 11 and 36, seeds 0 to 9 (P4-D367's limit;
  its two strict xfails pass). At a million rows a group the hour census
  still needs can hold no free written unit on any day of a rank's gap,
  and G7.3g asks free places only: a clinic comes back 767 ranks of
  1,000,000 off its hours (2,070 before), noon stamps over 118 days 2,344
  (2,908 with the weekday census withdrawn), and ward rounds give the
  round back and miss their hour census alone. Each miss is said by a
  deviation; the remedy is owned by lane S4b (the orchestrator,
  2026-10-13).
- **Stated limits added 2026-10-07 to 09, each with its owner.**
  A published weekday census on logs just above one row an open day cost
  its twin one to four different values at 2 to 7 seeds in ten on 21 of
  313 censuses (ruled 2026-10-08, P4-D388, `K-S3-59`); since lane D4s
  split the two tails' ranks first (P4-D369 part one) 1 of them still
  does, beside the fresh Tuesday-to-Thursday clinic at 11, both where the
  body draws past the rules' expectation and the pass merges. Seven-day
  logs holding every day stay one to three values short (a rebuilt tail
  ending inside the real one) and fifteen Mondays at 36 stay long (each
  tail rebuilt on at least 15 days), each a strict xfail naming its
  cause; the workbook date system moves the rules only where a column's
  first value is the system's first day, not built. A date whose other
  spelling is declared missing, alone in a tail's stratum, now trades
  that spelling (step 8; P4-D369's integration paragraph): the 30 of 90
  battery twins that missed presence, holes, the tail and the ladder
  miss nothing.
  A clock column's cells of the other hour width on
  an absent place nothing present stands on are written in the column's
  width, owed to lane C2 (P4-D373, strict xfail), as are route 1's 198
  blank cells over 2 columns, to be removed under the corrected route-2
  ruling (no cell blank that the source never left blank), and the label
  twins' hour-of-day distance at small tables (P4-D390). A stamp
  beside rare words is written in its source's shape (`2024-01-05 9:15
  AM`, P4-D393) but, as every held-back stand-in of a text column, reads
  as no date (`7000-00-01 26:23`), a `T` stamp whose marker alone is
  lower case (`2024-01-05T9:15 am`) is written `AM`, a stamp with a
  month word, a compact date, an offset after a space, more than 32
  characters or a comma after the date (`1/5/2024, 9:15 AM`) keeps no
  form (a year-first stamp's `Z` or offset keeps its `T` and `Z`), a
  zone after a year-last date keeps no stamp form (spaced, no form at
  all; parted by a letter and of 24 characters or fewer, the form it had
  before L3, its letters filled by the step), and free text of zoned
  stamps can miss `length.mean` at a floor of eleven, by G9.5's length
  pin, not the forms (a stated limit owned by the forms lane FM, the
  orchestrator's ruling of 2026-10-16: `T` stamps written straight on
  beside short rare words at floors 2 and 11 miss `length.mean` only);
  no lane owns the others yet; R1's codes
  question follows the classifier on a clock column (P4-D383's Codex
  paragraph), and on the merged classifier the 10,000-row `HH:MM` column
  with 203 `UNK` is read as clock times under the answer `missing` and
  asked at floors 11 and 36; at a floor of 36 at 300 and 1,000 rows
  `UNK` stands on 11 and 25 cells, under the census line its question
  would print, and it is not put (strict xfail; ACCEPTED by the
  orchestrator, 2026-10-13); and dates mixing offsets that missed
  `n_at_midnight` (4 of 600) hold it since landing 3b.7 (P4-D378).
- **Stated limits added 2026-10-13 (the fifth push's critic), each with
  its owner** (the orchestrator's rulings of that day). D3's two strict
  xfails, quarter ends and six Mays at 10,000 rows (P4-D368), pass since
  lane D4 merged with batch 3b part 1 and are xfails no longer. The day
  pass at 67 per cent of generating against a budget of half at 40,000
  rows (`K-S3-44`) is lane S4b's. An all-different column mixing 800 ISO
  datetimes with 200 ISO dates, which came back 881 of 1,000 different
  (95,463 of 100,000) while `validate` exited 0, comes back 1,000 of
  1,000 since landing 3b.7 (P4-D378) at seeds 0 to 2 and floors 11 and
  36 (measured at batch 3b part 2c); the same mix with a bare date on
  every day of its span comes back 999 of 1,000 at floor 11 and 998 at
  floor 36, seeds 0 to 2, inside G12.5's envelope, every check met and
  the shortfall said in the twin's report, ACCEPTED (the orchestrator's
  rulings of 2026-10-15 on the sixth push's critic, the owner may
  reverse any); a 12-hour dial column read at UTC whose offsets carry
  the drawn instant past local noon or midnight (exit 3; offsets to be
  allocated before the instants are drawn, P4-D383) is lane 3b-REST's,
  the calendar remainders beside 3b's schedules (P4-D378; landing 3b.7
  has closed). R4's whole counts written with a needless exponent
  (`1704067200e+0`) come back written in full, lane L1's (P4-D384). D2's
  older fault (b), the leap-second columns' count of different values
  and count at midnight (P4-D379), and a local dial column just after
  midnight (00:00 to 00:08, written 12:mm) missing `n_distinct`, are
  lane J2's. Fixed on this push's repair (P4-D383): R2c's stepped
  partial cells left the column's range silently (years 1984 to 2063 for
  a source's 1900 to 1979 beside dates of 2024) and now step inside the
  full dates' span first, then before it (1945 to 2024; where the
  source's partial dates lay is published nowhere); and Q6 answered
  `keep` is no longer put again.
- **The calendar on the shared clock and the joint member** (landing
  3b.7, P4-D378, 2026-10-13). The weekday, day-of-month and hour
  censuses stand on columns of two offsets and of dates beside moments,
  each cell counted on its own clock. Stated: the count of different
  values there stays in G12.5's envelope, an all-different joint
  column's too, its shortfall said (consecutive-minute stamps beside
  bare dates: 754 to 805 of 1,000, strict xfail); a daylight-saving
  column's twin writes the offset not in force on its date for 50 to 52
  per cent of its rows (35 to 39 before the landing: G7.4's spread meets
  the censuses at the cost of season; publishing each key's first and
  last day is lane D5's, daylight-saving offsets on the shared clock);
  `z_plus` withholds its weekday census at 1,000 rows and at 10,000 at
  the floor of 36; where the hour census caps the body at hour 0 and the
  tails' gaps hold too few midnight days, bare dates are written as
  moments (98 of 100 at 400 rows, 2,498 of 2,500 at 10,000;
  `resolution_mix` missed and named, strict xfail); where dates and
  stamps share days the twin spreads the dates evenly over the span (20
  per cent in every fifth where the source held 10 to 57); C1's c0 and
  c551 hold 99 to 177 different values for 63 and 83, inside the
  envelope; and the minute and second censuses (MC3, SE3) stand on the
  shared clock too since batch 3b part 2d's integration, each cell
  counted on its own clock, once lane J2 had met T3's fields beside D2's
  weekday census on moments (P4-D378, P4-D391). The consecutive-minute
  shortfall, `z_plus`'s census, the bare dates written as moments and
  their even spread over the span are lane 3b-REST's (the orchestrator's
  rulings of 2026-10-15 on the sixth push's critic, the owner may
  reverse any).
- **Stated limits measured at lane J2 (2026-10-13), each older than
  it.** Beside a weekday census the hour pass leaves a small bursty
  table's count of different values long: 85 of 105 twins of T3's bursty
  tables on 45191fa, 83 since the minute and second passes pay their
  count steps back (P4-D391); owner lane 3b-REST (G7.3g step 6; was lane
  J's family, closed). A column nine in ten at midnight, its count there
  withheld for its size, beside a heap at minute 0, wrote 989 and 983
  cells at midnight of 990 -- found by lane T3 (P4-D372); such a column,
  fewer cells than the line off 00:00:00, now withholds its minute and
  second facts with their own reason (NF123, NF124; NF118 and NF119 say
  the counted midnight's), as 45191fa published none: of a battery of
  dates written as datetimes, 1,000 to 5,000 rows with 5 to 30 timed,
  every column 45191fa met is met at floors 11 and 36, seeds 0 to 2;
  R4's `%.15g` column writes 990 at midnight, its `repr` sibling 10,
  passing as on 45191fa only because the check of a count withheld for
  its size reads either side (the orchestrator's). Regular stamps
  crowding the lattice their clock facts pin -- every series measured
  one to sixty minutes apart, 1,000 to 100,000 rows, short of its count
  and from 3,800 rows off the second's heap -- now withhold those facts
  (NF121, NF122) and miss nothing; dense grids of random times -- on the
  hour, on 5-, 15- and 30-minute slots, written to the minute with `:00`
  seconds -- fill their lattice no more than a uniform draw would and
  keep them (26 of 28 twins miss nothing; the half-hour grid misses
  `second_heaps.counts` in 2, lane 3b-REST's, was lane T3's own). A
  repeated grid publishes its minute and second facts under the looser
  fifth only where no value is written once, no count at midnight is
  published, it holds at most 1,000 different values and its lattice
  stands on midnight (J2's Codex review, item 2, its two verifications
  and the orchestrator's ruling; lane J3, P4-D391):
  80 % of 1,250, the smallest count at which a swept grid missed; the 93
  grid-and-floor pairs of 1,001 to 2,500 values that met with it now
  withhold. A grid off midnight that fills its lattice to the share and
  above a uniform draw with no value written once (or passes the
  twentieth with some written once), or one written four times beside a
  count at midnight above 1,000 values, now withholds them (lane J3: 254
  published pairs of a 512-grid sweep, every lattice slot filled, that
  missed now meet, and 372 that met lose them -- drawing such grids at
  their own phase could keep them, untested, not built). Still so, as
  before J3 (the orchestrator's ruling of 2026-10-15, owner lane
  3b-REST): a daytime grid with a few night stamps (25 to 60, 2.4 to
  5.7 % of its values) at floor 11 publishes and misses its count of
  different values (982 to 1,046 written of 1,024 to 1,057), the hour
  census pooling the night into one group; the J3 verifier's weighted
  draw is that lane's starting point. Carried (lane RT1, 3b-REST's
  clock half: the orchestrator confirmed batch 4a's provisional record
  on 2026-10-16): 500
  stamps five minutes apart, every one different, at floor 36, still come
  back 496 to 500 values, and 1,000 stamps half an hour apart from 07:13
  with 60 % of the slots empty, written two to four times, at floor 36,
  not crowded (0.41 of their lattice), publish and wrote 1,001 values in
  1 twin of 8, as on d3712a1. The payers' walk finds each
  payer by halving and its paid searches grow with the rows (2.04 to
  2.16 times a doubling behind a wall of payers that keep nothing), but
  a wall of more than 1,024 such payers still ends a search
  (`_CLOCK_PAYER_REACH`), the count one value short, ACCEPTED (bounded
  work at a million rows, the orchestrator, 2026-10-15); a state probe
  with payers on both sides of the run, not a twin, ends one value short
  at a wall of 40, as before J2's repair (lane 3b-REST); the payers'
  exclusions hold before 1970. NF74's unit-room rule, measured before
  3b.4, withholds a noon census the twins now meet (lane 3b-REST). A
  clock-only column's minute census is asked over the fine table too, as
  a timestamp's (P4-D374; Codex I3b2d, item 1: one census over every
  hour bent the minutes inside a ten-minute bin, a morning's even
  minutes 0.66 against 0.50, silently); its cost, the fine table reading
  a few hundred cells an hour as dependent: the clinic column at 1,000
  rows is withheld, and at floor 36 comes back 0.515 on `:00`/`:30`
  against 0.706 (0.673 published), its minute distance 0.43 to 0.45
  against 0.29: ACCEPTED (the orchestrator, 2026-10-15: the silent
  distortion ruled worse).
- **Open items found at batch 3b's integration, owner lane 3b-REST**
  (the orchestrator's rulings of 2026-10-15 on the sixth push's critic,
  the owner may reverse any). `wide_three_mid`, 1,500 stamps at -10:00,
  +00:00 and +12:00, three in seven at midnight, comes back 647 against
  644 at the floor of 36, `n_at_midnight` named as a deviation (648 at
  bb9e6d4): no matching of its tail ranks to the held places keeps the
  count, G7.3h's frame (P4-D378). A declared-missing spelling withheld
  below the floor (20 cells of `2/1/2022` at 36) is still written on 109
  of 400 tail ranks at front 400 and 23 of 60 at front 60, read as
  absent by a reader declaring it missing (P4-D369).
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
  Landing 4. Lane S4b-num (2026-10-14) brought four of lane S4b's
  costs, on the shapes named here, to work that grows with the rows,
  every twin the same bytes: the dense tail's push (494 s to 13.7 s at
  100,000 rows, 207 s at 1,000,000), the identity walk (501,501
  spellings asked to 1,001 at 100,000 rows of the Codex column), G4's
  decimal codes (803 s to 32.6 s at 1,000,000 rows) and a register's
  quality report (50,000 consecutive codes validate in 59.5 s, 997,770
  rows in 123.5 s) (P4-D377, P4-D387, P4-D390). Lane S4c
  (2026-10-14): `validate` prints and writes its report in pieces,
  798 MB at 997,770 rows of a register where it held 1,317 and
  2,000 MB at 2,990,700 (P4-D390), and a dense tail's twin meets its
  published mean distance (G6.6.8 rule 4, P4-D377). Lane S4d
  (2026-10-15): `describe` holds one answer per spelling (past 65,536
  different texts, from a text's second sighting within 8,192 new
  ones), every description the same bytes -- those 2,990,700 rows in 780 MB where it
  took 2,389, 4,983,120 in 1,270 MB, and `validate` of them in 1,662 MB
  (P4-D390). Left: a column whose values never repeat still holds a
  record a row (G2's dense tail: 2,287 MB at 3,000,000 rows, past the
  2 GB rule), reading holds the file's bytes and decoded text beside
  the table, and `validate` took 493 s of CPU at 2,990,700 rows, since
  it describes the file again (2,000 MB and 585 s there before lane
  S4d; owner lane SV, the orchestrator's ruling of 2026-10-16); at 1,000,000 rows of
  G2's dense tail the twin still misses the column's mean, skew and
  kurtosis, whose G12.3 windows do not reach the published values
  (owner lane G2T, the orchestrator's ruling of 2026-10-16).
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
  and `K-S3-44` (P4-D376).
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
- **The floor counts ROWS, not people** (owner, 2026-09-23). The table's
  own size is counted in people where a declared identifier repeats, but
  a value held by twelve visits of ONE patient is still published with
  its count: 68 such values over three repeated-measures shapes, 66 of
  them on a table of 12 patients over 1,196 visits (`K-S3-14`, an
  accepted limit, plan P4-D348). The design for counting people per
  value is written and shelved.
- **A long table publishes a patient's name, street address or birth
  date while nobody has answered the person question.** No identity
  question flags them, and no general rule reaches them without hiding
  columns that identify nobody: 214 real values in the description over
  600 and 20,000 rows (`K-S3-64`, plan P4-D401). Lane HX2 owns them.
- **A record-number key written beside `-1` gets a twin that misses its
  published forms** (validate exit 3), declared or held until answered:
  on 68dae22f a declared key of 1,200 rows wrote fewer than 11 of its
  1,176 six-figure forms, and lane HX's hold reaches such a key (plan
  P4-D401). So does a telephone number opening `+` (its `+` layout) and
  a key exported as `100001.0` (the twin writes a figure after the
  point). Lane CODES-1 part C owns them.
- **A second record number beside a declared person column is
  published.** A health plan or account number written with letters
  and figures is read as a number with an affix or as labels and asked
  nothing, since the declaration answers the person question: 71 of 132
  values at 600 rows, 139 of 150 at 20,000 (`K-S3-64`'s stated shapes,
  plan P4-D401). Lane HX2's rule, widened to a declared person column,
  owns it.
- **A pool's spread is no longer verified.** The owner chose on
  2026-09-21 to publish a pooled column's mean and not its spread,
  because publishing both solved for the held-back values. The twin's
  pooled mean is now exact and its spread is unchecked, about 2 out
  (`K-2B-50`, green on the mean). Stated, not hidden.

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

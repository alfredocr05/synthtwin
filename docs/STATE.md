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
| suite | 7,429 collected. **The seconds here are STALE**: the last single-process measurement was 3,085.8 s (51 min 25 s) at 7,109 collected, and stage 3's landings have raised about eighty files' tables to the population floor since. Five-shard sums suggest the suite grew about a quarter; ledger `K-P0-10` carries that arithmetic and the next quiet-machine run re-stamps it. In CI it runs as **five shards**, the heaviest about 20 minutes. Re-measure here whenever the count moves |
| KPIs | `tests/kpi/ledger.json`: 163 KPIs over phases 0-4 and stages 1, 2, 2b and 3, 30 of them headlines — which is the cap, so the next landing demotes one or raises it deliberately; 149 green, 10 open with the stage that owns each, 4 limits the owner accepted. Stage 3's five landings each allocated from `K-S3-01` and their integration renumbered them `K-S3-01` to `K-S3-12`, keeping ONE of them a headline (`K-S3-11`, the tail leak) and demoting the rest. **One command re-measures them all:** `.venv/bin/python tools/measurements/kpi_run.py` (add `--slow` for timings and scale). Run it at every stage close: **a KPI that drops is a regression even when every test is green** |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request, five Pythons across Ubuntu, Windows and macOS. **It saw stages 1, 2 and 2b for the first time on 2026-09-20 (PR #6, run 35508922164): every static check green, every test cell red on three defects, all three repaired.** Its **second** run (35541541720) was red again on a deeper layer, all of it in the tests: two that asserted the answer for the machine they ran on, a `Path.read_text(newline=)` that exists only on 3.13 while the floor is 3.10, seventeen Windows failures caused by a temporary path containing `AppData` (which contains a sheet name the test forbade), and about 25 workbook cases that failed instead of skipping where openpyxl is absent. All repaired, each with a guard that now fails HERE rather than in CI. The suite is sharded five ways since, so a cell should cost about 13 minutes rather than up to three hours. A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
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
| 3 | **DONE 2026-09-23. The extremes, and the population floor.** Built as FIVE landings on five branches from one base — 3.1 the default floor of 11 and the floor holes, 3.2 the population floor and the person rule, 3.3 the numeric tail, 3.4 the date and clock tails, 3.5 the sentences — and integrated last. No numeric, date or clock column publishes either end now; a table under 100 is refused and one under 1,000 carries a notice it cannot turn off; no sentence carries a count a key withholds | MET: `K-S3-01` to `K-S3-12`, and `K-P3-03` and `K-2B-05` reached their targets on the way | done |
| 3b | **Dates keep their calendar shape.** Weekday, time of day, heaps and schedules, each a new published fact that must meet stage 3's floor | weekend share, hour of day and heaps come back; no calendar count below the floor | 6 |
| 4 | **The numeric path per stratum, not per row.** The ladder work happens once per distinct value | two million rows by fifty columns, end to end, under an hour (`K-S1-06`) | 8 |
| 5 | **The seam the interface needs.** Results become data with a rank decided once, before any sentence exists; a callable entry point returns results instead of printing them | a caller distinguishes a good run from a bad one without reading prose; reports byte-identical | 13 |
| 6 | **Cross-column, pairwise.** Rank correlation over cut indicators, applied as a reordering of values already generated. **Inherits:** today a rank correlation of 0.747 comes back 0.027 (`K-S6-01`), and the pairing walk of three- and four-number cells (`K-P4-06`) | every marginal unchanged; a known odds ratio comes back; the report names what it carries per relationship | 21 |
| 7 | **Higher-order structure.** Design pending measurement (four prototypes scored as this page was written) | a known three-way interaction comes back with the right sign, or the limit declared per relationship | 25 |
| 7b | **Higher-order structure, chosen.** A declared model plus one cross-tabulation for the outcome; the cross-column floor is ABOVE one, which is what lifts the reviewer's veto | a known three-way comes back at the real table's own estimate; no published cell names one subject | 25 |
| 8 | **The screen.** The bundled toolkit with its scripting engine STRIPPED at startup — seventeen commands deleted, proven unrebuildable, mutation-tested one per command. The strip is the deliverable, not the toolkit | `tk.call`/`tk.eval` banned by the scanner; a table whose column name is an injection string has no effect | 33 |

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
  floor count as absent; a label row recoverable by subtraction counts
  as missing; a spelling below the floor counts into the commonest; an
  ambiguous first row gets placeholder names and a question, and no
  record's text is ever published.
- **Accepted limits, 2026-09-18** (plan: "Owner decisions of
  2026-09-18"): real record numbers can reach the twin when a declared
  identifier has little spare room; held-back rare values can be rebuilt
  (63 of 251 cells, `K-2B-19`, accepted again on 2026-09-22: "just
  showing that the value exists is not an issue; what matters is not
  showing the relation in a descriptive file"); an autofilter can still make an ambiguous first row the header; a
  workbook date cell naming no day is read; free text's "one cell is a
  number" and a pooled label's one missing cell stay published.
  **Judge any such question by its effect on the owner's code and
  results; if there is none, do not spend time on it.**
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
  report line equal to an outermost value of the real column. A floor
  lowered to one still names what it always named, which is what
  lowering it asks for.
- ~~**Spread too wide on normal-shaped columns.**~~ **CLOSED by landing
  3, 2026-09-23.** There is no published extreme to draw a straight line
  to: the outer rows are read through the shape fitted to their two
  published moments. `K-P3-03` is GREEN — nothing missed at 5,000 or at
  20,000 rows and the twin's spread 0.04 to 0.22 per cent from the
  published one, against 1.1 to 3.8 per cent before and 10 of 20
  columns missing their own spread check at 20,000 rows.
- **Relationships between columns are not carried.** Landing 6.
- **Time of day inside timestamps** is spread over the whole day.
  Landing 3b.
- **Cells of three or four numbers** sit at 556 of 2,160 pair
  agreements outside their window and 1 above-count missed, against a
  target of 550 and 0 (`K-P4-06`); stage 3's numeric tail brought both
  down from 609 and 4. The pairing walk is the open cause. Landing 6.
- **A short list of carried edge cases** fails the twin's own check on
  one shape each: two date-width allocations, one identifier layout, a
  sign band given more slots than it has numbers. The known-miss entry
  of the ledger names them.
- **The largest tables** are measured only to 100,000 rows. Landing 4.
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

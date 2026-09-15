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
| branch | `phase-5-relationships`, cut from `main`. `main` is pull-request only |
| phase | **Phase 4 REOPENED 2026-09-12** — it closed on 2026-09-11 with silent within-column defects live inside its own charter. Phase 5 does not start until the ordered list below reaches it |
| plan | This page is the plan of record. `docs/plans/phase-5-relationships.md` is a DRAFT whose scope is superseded: it deferred correlation, and correlation is now mandatory |
| suite | 4,544 collected. The run that closed landing 1 is recorded in `CHANGELOG.md`; re-measure here whenever the count moves |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — all clean |
| CI | runs on every pull request, five Pythons across Ubuntu and Windows. A green local suite is not a green CI. Check `gh pr checks` before believing a branch is done |
| review | **ONE round per landing** (owner, 2026-09-12), `codex exec -m gpt-6-astra -c model_reasoning_effort="ultra" -s read-only`. `ultra` is valid and verified; do not substitute `high` |

## What is being built, in order

Each line is a landing: one commit, one review round, scope frozen at
this page. Nothing starts until the line above has passed its gate.
Weeks are elapsed from 2026-09-12 and assume one builder.

| # | landing | gate | wk |
|---|---|---|---|
| 1 | **DONE 2026-09-13. The list idiom and the heap merge.** `x = x + [item]` at 661 sites became `x += [item]`; the merge loop became `_merge_down`, a heap over a linked list. Generate at 20,000 rows x 20 numeric: 1,113 s to 19 s. Describe at 200,000 rows: 390 s to 10 s. Both linear now | MET: 9 output files byte-identical, 4,200 randomised cases agree with `_merge_nearest`, suite green at 4,406, and `tests/test_growth_is_linear.py` turns red on either defect | done |
| 2 | **DONE 2026-09-14, closed after an independent audit. The three silent defects.** A grouped number keeps its mark: a comma, including whole numbers such as `12,345`, or a point on a declared decimal-comma column; a moment keeps the mark between its day and its clock at each mark's count; a date stored at midnight stays at midnight. Landed in three commits: the comma, the moment and midnight, and the repairs the audit found | MET: `tests/test_stage2_round_trip.py` describes the twin again for 19 shapes and finds every stage-2 fact returned with nothing missed; the four shapes designed not to return are pinned beside it | done |
| 3 | **The extremes, and the population floor.** Stop publishing exact minima and maxima — publish the tail's shape. Then: refuse under 100, notice 100–999, counted in SUBJECTS where an identifier is declared | no published number is held by fewer than the floor; a one-row table is refused | 5 |
| 4 | **The numeric path per stratum, not per row.** The ladder work happens once per distinct value | two million rows by fifty columns, end to end, under an hour | 8 |
| 5 | **The seam the interface needs.** Results become data with a rank decided once, before any sentence exists; a callable entry point returns results instead of printing them | a caller distinguishes a good run from a bad one without reading prose; reports byte-identical | 13 |
| 6 | **Cross-column, pairwise.** Rank correlation over cut indicators, applied as a reordering of values already generated | every marginal unchanged; a known odds ratio comes back; the report names what it carries per relationship | 21 |
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
- **Asking the person is part of the product** (A-P4-56, A-P4-58).
- **Being synthetic is not an answer to an obligation.** The screen may
  not present the twin as settling a privacy rule. What it MAY say: your rows never leave this
  machine, nothing is sent anywhere, no model sees your data, and the
  files produced are yours to govern like any other export. Guarded by
  the seventh family of `tests/test_claim_inventory.py`.
- **The documentation regime is LEAN** (A-P4-40), and tightened on
  2026-09-12: stop producing text that describes the project. What is
  NOT cut: the tests, the reference vectors, the claim inventory, the
  decontamination scan.
- **Version 6 is extended in place** until the first release (A-P4-41).
- **The release is parked** until the tool has been used on real tables.

## What is broken right now

- ~~Both commands are quadratic.~~ **Repaired 2026-09-13, landing 1.**
  What remains is only the largest tables: a million rows by twenty
  columns is about 35 minutes, two million by fifty is about three
  hours. Landing 4 closes that by doing the ladder work once per
  distinct value rather than once per row.
- **Spellings stage 2 did not reach.** A number grouped with a space or
  an apostrophe is read as free text; an accounting bracket or a plus
  sign on a decimal is not a published style, so the twin writes a
  minus and drops the plus; a column mixing bare dates with midnight
  moments is written wholly as moments; a column only partly at
  midnight, or at midnight on the shared clock, still gets invented
  times. Carried in `CHANGELOG.md`.
- **Twins of date columns spread their values across days too
  evenly**: on 400 rows the day-to-day variance was about a third of
  the real table's. It predates stage 2 and bears on the second goal.
- **The description names individuals.** On a 1,200-row table the
  published maximum of two columns was held by exactly one subject.
  A population floor cannot fix this; the extremes must stop being
  published exactly. Landing 3.
- **R-P4-61** — the generator and the validator print moment windows
  differing in their last two digits. Carried.

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
   second is quadratic and it is currently in 661 places. The scanner
   forbids `.append`; `+=` is allowed and is 3,000 times faster at
   100,000 items.
7. **Run the guards AFTER `git add`**, then the seal LAST, then ONE full
   suite. Breaking that order costs another nineteen minutes.

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
- **A repair that prints ambiguous numbers is worse than the silence it
  replaced.**
- **Measure a ruling against the suite BEFORE building it.** The tests
  are the record of decisions already taken.
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
| the project in plain language | `STATUS.md` |

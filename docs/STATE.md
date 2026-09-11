# STATE — read this first

**One page, kept current, for whoever picks this up next — a person
returning after a week, or an assistant starting a conversation with no
memory of the last one.** Everything here is a fact about *right now*.
Nothing in it is history; history lives in `CHANGELOG.md`, the phase
plans and `git log`.

**The rule that keeps it true: this file moves in the same commit as
the work it describes.** A landing that does not update it is not
finished.

**And the rule that keeps it SHORT, which is new and is the point of
landing L22.** This page reached 3,814 lines by growing a section per
landing — narrative that belongs in `CHANGELOG.md` and the plan. At
that size no session read it, so every session re-measured the project
from scratch, which is the failure the page exists to prevent. **A
landing adds nothing to this page except by changing a fact already
stated here.** If you want to write what a landing did, write it in the
changelog.

**One fact, one place.** Every count in this file that also exists
somewhere else has gone stale here at least once — the suite size, the
lint state, the review protocol, the page's own length. State a fact
where it is measured and point at it from everywhere else.

---

## Where the work is

| | |
|---|---|
| branch | `l14-affix-set` (never merged; `main` is pull-request only) |
| phase | **Phase 4 — CLOSED by owner decision 2026-09-11**, sixty-six register entries carried by name. **Phase 5 — relationships — is CURRENT; its plan is drafted and NOT ratified.** |
| plan | `docs/plans/phase-5-relationships.md` (revision 1, DRAFT, unreviewed). Phase 4's is `docs/plans/phase-4-columns.md` and its closure section is the register Phase 5 inherits |
| suite | 4,457 collected; `4406 passed, 51 skipped in 1160.11s (0:19:20)` verbatim, fully green. Four new tests: `tests/test_p5r1_the_grain_clause_is_true.py` |
| checks | `ruff check .`, `mypy --strict src/`, the offline import scan, the provenance check, the decontamination scan, the signed attestation and the disposition seal — **all clean**, re-measured at the closing commit |
| CI | **runs on every pull request, on five Pythons across Ubuntu and Windows.** A green local suite is not a green CI: the close's last defect was a test that asserted the POSIX outcome on every platform and failed every Windows cell three runs running. Check `gh pr checks` before believing a branch is done |
| review | **ONE round per landing** (A-P4-59), `codex exec -m gpt-6-astra -c model_reasoning_effort="high" -s read-only`, launched without checking in. A crash or a silent wrongness in what THAT landing built is repaired; every other item is recorded as a residual and carried |

The suite size is enforced: `test_the_state_page_states_the_suite_size_
it_was_written_against` compares the number above against what a whole
run collects. **That guard was inert until 2026-09-10** — it compared
`config.args` with `testpaths` as strings, so `pytest tests/` looked
like a filtered run and it skipped on every whole-suite run this
project has ever done. Paths are compared as paths now.

## What is being built right now

**Phase 5 — relationships.** Phase 4 closed on 2026-09-11. The phase 5
plan is DRAFTED and NOT RATIFIED: `docs/plans/phase-5-relationships.md`,
revision 1. Nothing may be built from it until it has been through
adversarial plan review and the owner has taken the four P5-D0
decisions it names.

**What it proposes:** three of the eight reserved slots, in this order
— `temporal` (two event columns keep their order), `deterministic` (a
derived column agrees with what it is derived from), `grain` (what one
row is). The other five stay `null`. Correlation is deliberately NOT
first, and the plan says why in terms the owner can overturn.

**Measured on an event table of 300 rows, at seed 7, the day the
plan was written** — this is the phase in three numbers:

| what a person would check | real | twin |
|---|---|---|
| rows where the end date precedes the start date | 0 | **137** |
| rows where the duration column disagrees with the dates | 0 | **299** |
| rows where a derived column disagrees with its two sources | 0 | **299** |

**None of it is dishonest today** — the twin's report says every column
and every row was built on its own, first and unmissably. Phase 5 lifts
a declared bound; it does not repair a lie.

Phase 5 inherits **sixty-six carried register entries** from Phase 4,
grouped in that plan's closure section by what a reader would do about
them. The estimate in A-P4-59 was "about forty"; the count is
sixty-six, and the closure section says so rather than leaving the
forecast standing.

**R-P5-1 is opened and closed** in the same commit as the plan: the
report's limit 2 said the twin holds no several-rows-per-person, and it
holds exactly the real distribution of them — the identifier role
publishes `n_distinct_by_occurrences` and the generator reproduces it.
The error ran in the safe direction and was repaired before any
relationship content was designed.

| | landing | state |
|---|---|---|
| 1 | L16 — the arbitration, and codes asked about | done |
| 2 | L18 — the shapes a European table meets | done |
| 3 | L17a — the asking becomes one object | done |
| 4 | L17b — the questions file and `--answers` | done |
| 5 | L19 — the twin's report stops contradicting itself | done |
| 6 | L22 — the record: this page, the changelog, STATUS, SECURITY | done |
| 7 | L23 — the closure section, the phase statements, the merge | **this commit** |

**The close finished in seven days, on 2026-09-11.** What made the
difference is worth carrying into Phase 5: one review round per
landing instead of eight, a frozen scope, and a remainder CARRIED by
name rather than built. The ten days before it produced 95 commits of
which 44 were review-round repairs, and opened 32 residuals against 19
closed.

What each landing did is in `CHANGELOG.md` under `[Unreleased]`, and
the reasoning is in the plan at the amendment each names.

## What the owner has decided, and must not be re-asked

These are settled. A new conversation that re-opens one is wasting the
owner's time; the reasoning is in the plan at the amendment named.

- **The small-cell floor defaults to 1** (A-P4-37). Nothing is pooled
  away unless the person asks with `--smallest-group`, so a rare
  finding reaches the twin. It does NOT follow that every column names
  its values: the nothing-publishing roles name none at any floor.
- **A rare value REACHING the twin matters more than the disclosure of
  its presence.** The owner has answered this family the same way three
  times (A-P4-36, the ruling of 2026-08-24, and A-P4-47's per-level
  form census). Do not re-ask it. What still needs asking is anything
  that would publish the CONTENT of a held-back value, which no ruling
  covers.
- **Asking the person is part of the product, and a chance of a wrong
  guess is itself the trigger** (A-P4-56, A-P4-58). "It's better to ask
  the user than make wrong guesses."
- **No column is routed by its SHAPE.** Review item P1-R6-F7 deleted a
  rule that guessed codes from width and the leading zero; A-P4-59
  clause 3 reopened it and **A-P4-60 withdrew it again on
  measurement** — see "What is waiting on the owner".
- **Being synthetic is not an answer to an obligation.** The twin means
  the rows never have to travel; it decides nothing about a privacy
  rule, an institution's own rules or an approval. Guarded by the
  seventh family of `tests/test_claim_inventory.py`.
- **The documentation regime is LEAN** (A-P4-40): an amendment is a
  table row, review records are item lists, a written method clause is
  owed only for branches that do arithmetic. What is NOT cut: the
  tests, the reference vectors, the claim inventory, the
  decontamination scan.
- **Version 6 is extended in place** until the first release rather
  than bumped per key (A-P4-41, contract 1.7a).
- **The release is parked** until Phase 4 is finished and the tool has
  been used on real tables. The release workflow was never built.

## What is waiting on the owner

**Nothing blocks the close.** One decision is open and is theirs alone:

- **Whether to take the padded-column routing after all.** A-P4-59
  clause 3 ruled that an unanswered column of digits reads as CODES. It
  was built, narrowed to the padded signal, given contract NF56 so it
  could never be silent, and covered by thirteen green tests — and the
  suite then returned 46 failures and 19 errors. **A-P4-60 is the
  measurement and the withdrawal.** Taking it anyway is one commit; the
  amendment says what it costs (review item P1-R6-F7's settled policy,
  plan decision P4-D14's field widths, and the distribution of every
  padded measurement).

## What is broken right now

- **Nothing is known broken in the product.** Every scanner, the seal
  and the suite are green as recorded above.
- **R-P4-61 — the generator and the validator print moment windows
  differing in their last two digits**, because they are independent
  implementations by charter and were never written alike at that
  precision. Carried, not closed: it needs the arithmetic stated
  operation by operation in G12.3 and both implementations rewritten to
  it. No verdict has been seen to differ, and R-P4-61 owes that
  measurement too.
- **R-P4-165 — keeping a padded column's WIDTH is not keeping its code
  DOMAIN.** P4-D14 makes the twin of a five-character code five
  characters wide; it does not make it a code of the register. Measured
  by review: 120 five-digit codes gave 115 twin cells outside the source
  set. The fix is a declaration — `--code` — which the questions file
  now asks for.
- **R-P4-168 — AF-R reads its fragments in order and never the text
  between them**, so a required remark saying "do NOT run the command
  again with `--code`" is accepted.

The full register is in the plan. These four are the ones a reader
would otherwise trip over.

## The rules an assistant breaks first here

1. **Never change the decontamination scanner to make text pass** —
   change the text. Some ordinary words are denied. Probe before you
   write rather than guessing, and remember **a file you have not
   staged is not scanned**, because the scanner walks the TRACKED tree.
2. **The generator never reads a table.** Only the profiler and the
   validator open a CSV. No test helper crosses that line.
3. **Every published sentence is an enumerated form**, not a string
   written at the call site. Check `taxonomy.NOTE_ARITY`.
4. **A closed enumeration is stated in up to eight places.** Adding a
   role or a settings key means finding all of them; the guards will
   tell you, but only after they turn red.
5. **Never close a residual on a reading.** Build the column it
   describes and run it.
6. **Grow a list with `+= [item]`, never `x = x + [item]`.** The second
   is quadratic and this project has shipped it more than once.
7. **Run the guards AFTER `git add`**, then the seal LAST, then ONE
   full suite. Breaking that order costs another nineteen minutes.

## Already tried here, and it does not work

Kept short on purpose. Each of these cost at least half a day.

- **A pronoun cannot be resolved by a regular expression.** A rule that
  needs reference resolution must instead demand that the prose NAME
  the thing.
- **Widening a ban's noun list reports honest prose.** Name the SHAPE
  of the claim, never broaden the noun.
- **A guard that passes is not a guard.** Mutation-verify every new one
  before believing it.
- **Where a review names one site, there are usually two or three.**
  Search for siblings rather than repairing the site named.
- **A count restated in several places will disagree.** Compute it from
  one source and check every site that states it.
- **A GIT WORKTREE HAS NO `.venv`, AND BORROWING THE SHARED ONE TESTS
  THE WRONG SOURCE.** The checkout's venv installs this package
  EDITABLE from its own `src`, so a worktree reaching for
  `../../.venv/bin/python` imports the SHARED checkout's product code
  while its tests and documents come from the worktree. Nothing
  announces it. Set `PYTHONPATH=<worktree>/src` or give the worktree a
  venv of its own.
- **A repair that prints ambiguous numbers is worse than the silence it
  replaced.** Withdraw it and record the defect instead.
- **Measure a ruling against the suite BEFORE building it.** The tests
  here are the record of decisions already taken, with the reasoning in
  the docstring. A-P4-59 clause 3 was built in full before the suite
  showed that the owner had settled the same question the other way and
  that the harm it addressed had been fixed nine days earlier.

## How a new conversation gets its bearings

**Four things carry this project, and none of them is the contract.**
The contract is over eight thousand lines and the phase plan over five
thousand: no session reads either, which is why freezing them (A-P4-46)
costs almost no context.

| what | how it reaches you |
|---|---|
| `CLAUDE.md` | loaded automatically in every conversation here |
| **this page** | `CLAUDE.md`'s first instruction is to read it |
| the assistant's own memory | loaded at session start, outside the repository |
| **the docstrings** | read whenever the code is read, which is when it matters |

**The docstrings ARE the specification now.** Every public function's
docstring states what it promises — accepted inputs, determinism,
errors, and any boundary it upholds. With the contract frozen they stop
being a second copy and become the first one. **And the tests are the
other half:** when you would have written a contract clause, write a
test instead.

## Where the detail lives

| you want | read |
|---|---|
| the principles and the honest limits | `CLAUDE.md` |
| what the reviewer holds this to | `AGENTS.md` |
| the current phase, its decisions, its open register | `docs/plans/phase-4-columns.md` |
| what a description may contain | `docs/spec/profile-contract-v6.md` |
| what changed, in order | `CHANGELOG.md` |
| the project in plain language, for an outside reader | `STATUS.md` |
| what each landing did and why | `CHANGELOG.md`, then `git log` |

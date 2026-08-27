# STATE — read this first

**One page, kept current, for whoever picks this up next — a person
returning after a week, or an assistant starting a conversation with no
memory of the last one.** Everything here is a fact about *right now*.
Nothing in it is history; history lives in `CHANGELOG.md`, the phase
plans and `git log`.

**The rule that keeps it true: this file moves in the same commit as the
work it describes.** A landing that does not update it is not finished.
`STATUS.md` went stale exactly once by being updated separately, and its
Phase 4 section then described a phase four roles out of date.

**Part of that rule is enforced rather than promised.** The suite size
below is compared against the tests a whole-suite run actually
collects, so a landing that adds a test and leaves this page alone
turns the suite red (`test_the_state_page_states_the_suite_size_it_was_
written_against`). The rest of the page -- what is decided, what is
broken -- no test can check, and is kept current by the same rule
without the same help.

---

## Where the work is

| | |
|---|---|
| branch | `phase-4-plan` (never merged; `main` is pull-request only) |
| phase | **Phase 4 — comprehensive column handling.** Current. |
| plan | `docs/plans/phase-4-columns.md` |
| suite | 3,936 collected / 48 skipped |
| lint | clean (`ruff check .`), under the rule set pinned in `pyproject.toml` |

## What is being built right now

**THE PHASE 4 GAP RUN**, under the owner's standing authorization of
2026-08-26 ("feel free to move through all the gaps without my
consent", review aimed at machinery only). Gaps 1, 2 and 3 have
landed; gaps 4 to 7, the richer number family and the worked examples
are still ahead. The gap list itself is at the foot of this page.

* **Gap 1 — the address rule.** An affixed-number column no longer
  reads an e-mail address as a number wrapped in affixes.
* **Gap 2 — the fold-collision partner walk.** The walk prefers a
  parent that keeps the folded level under the long-tail line, and
  where a crossing happens anyway the report NAMES it. Four adversarial
  rounds; the preference was deleted once as inert on 190 homogeneous
  columns and restored when a reviewer produced a MIXED-family column
  where it decides the role a reader sees.
* **Gap 3 — the two width facts, closing residual R-P2-1.** The
  unrepresentable role publishes `min_length` and `max_length`, and the
  twin carries both ends instead of writing every such column at one
  made-up 400-figure width. Measured across 93 randomly built
  unrepresentable columns: both published widths held exactly on all
  93, every one reads back as `numeric_unrepresentable`, and no width
  miss anywhere in that trial was silent. This moved the method spec
  (G10.5 revision 4), the independent reference oracle, and the frozen
  `unrepresentable_joint` vector with it.

  **Two things found in this gap are worth carrying forward as habits,
  not as facts.**

  *A constant is a measurement in disguise.* Tightening the fraction
  spelling to its asked width looked safe and was not: the underflow
  floor of 325 had been calibrated against the two-character error
  being corrected, so the correction alone wrote REPRESENTABLE values
  into a column described as holding none. It was caught by probing
  every kind at every index rather than by reading the diff. When a
  number here looks like a constant, check what it was measured against
  before moving anything it touches.

  *A randomised trial shows a defect present and never shows one
  absent.* Having found that defect, I ran 300 built columns, saw the
  state was never reached, and wrote in a landed commit that it was
  unreachable. It is reachable: a reviewer supplied a column of 271
  distinct fractions -- more than seven times the distinct values any
  of my columns held -- whose twin holds 48 representable cells against
  a published zero. The trial was not wrong; the conclusion drawn from
  it was. Say what a trial covered, not what it implies.

**L0 of the close sequence** — the owner said "Go. Lean 15" on
2026-08-26. Landed here: the note-grammar guard (contract 4.5.1 against
`taxonomy.NOTE_ARITY`, both directions), the four clauses NF45-NF48 the
contract had never written for Phase 4's roles, the corrected censuses,
amendments A-P4-40 and A-P4-41, and the obligations landing with two
adversarial rounds behind it.

**R-P4-25 is HALF closed, and the half that was safety-critical is the
one that landed.** Version 6 is now in the sealed governing set, so the
1,987 distinct passages of the contract that governs every description this tree
writes are under the seal — they were outside it, carried as a "draft
under adversarial review", while `PROFILE_VERSION` had been 6 in the
producer and the loader for days. A disposition quietly lowered in it
moved nothing red. Found at the third adversarial read.

**What is still owed of R-P4-25:** the disposition-registry MATRIX
still reads version 4's section 9 plus version 5's deltas. Repointing
it at version 6 means remapping three sub-table headings that changed
when the new roles landed, and it is its own commit. The seal no longer
depends on it.

## What the owner has decided, and must not be re-asked

These are settled. A new conversation that re-opens one is wasting the
owner's time; the reasoning is in the plan at the amendment named.

- **The small-cell floor defaults to 1** (A-P4-37). The floor pools
  nothing away unless the person asks with `--smallest-group`, so a
  rare finding reaches the twin. It does NOT follow that every column
  names its values: the nothing-publishing roles name none at any
  floor.
- **A column that publishes nothing today may begin to publish more**
  (A-P4-36) — answered yes to all five disclosure questions.
- **The release is parked** until Phase 4 is finished and the tool has
  been used on real tables. The release workflow was never built.
- **Adversarial review runs up to FIVE rounds per landing**, launched
  automatically and without checking in (owner ruling 2026-08-26,
  which withdraws A-P4-30's cut to three). Stop early when the items
  turn into wording rather than control gaps — not before. Reviews are
  codex `gpt-5.6-sol` at high effort, read-only. The full suite runs
  once before a commit rather than after every edit.
- **The documentation regime is LEAN** (A-P4-40): an amendment is a
  table row, review records are item lists, the contract is not
  hand-maintained beside the code, and a written method clause is owed
  only for branches that do arithmetic. What is NOT cut: the tests, the
  reference vectors for the number machinery, the claim inventory, the
  decontamination scan.
- **Version 6 is extended in place** until the first release, rather
  than bumped each time a key is added (A-P4-41, contract 1.7a). Residual R-P4-23
  named a version bump as the proper repair and left the choice to the
  owner; that choice is now taken and the residual closes BY RULING,
  which the register says in as many words rather than claiming a
  measurement.
- **Being synthetic is not an answer to an obligation.** The twin means
  your rows never have to travel; it decides nothing about a privacy
  rule, an institution's own rules or an approval. Guarded by the
  seventh family of `tests/test_claim_inventory.py`.

## What is waiting on the owner

**Nothing blocks the close sequence.** The go decision was given on
2026-08-26 ("Go. Lean 15") together with standing authorization to work
the landings without checking in between them, and the two small
rulings stand at the recommendations the owner accepted as defaults:
`numeric_unrepresentable` GAINS `min_length` and `max_length` (L4), and
the recoverable-distribution advice is TIGHTENED rather than softened
(L1).

What is owed to the owner rather than from them is a decision about the
183 lint errors below — whether to pin a rule set or edit — and that
does not stop any landing.

## The joined role's own gaps, all opened by review and all owed

`joined_numbers` (P4-D21, P4-D23, P4-D25) carries four recorded gaps.
None was caused by the landing that found them; all are **Phase 4
close blockers** rather than acceptable release residuals, on the
reviewer's ruling of 2026-08-26.

| # | gap | goes to |
|---|---|---|
| **R-P4-42** | the rank-agreement window is in the plan and in NEITHER method specification | L10 |
| **R-P4-43** | the validator checks a position's endpoints and whole-number test, not its styles or fraction census | L7 |
| **R-P4-44** | the twin's report names NO approximation of this role, so it says the twin gave nothing up while every position's ladder is approximated. A repair was built and WITHDRAWN — it printed per-position counts the profile publishes for no position, both positions as one unnamed column, and a stand-in measured into position two | L7 |
| (unnumbered) | a THREE-part column cannot honour its (1,2) pair — the repair walk permutes only the last position. Two-part columns are unaffected, which is why five reads did not meet it | L7 |

## What is broken right now

- **Lint is clean and CI is running again.** Both were broken and both
  were fixed in this gap run: `pyproject.toml` now pins the ruff rule
  set (the 183 errors were 120 quoted type annotations, a deliberate
  style here, plus tooling import order), and CI had not run for 86
  commits. When it did, all three of its failures were checks that had
  outlived their rules -- a column count, a suppressed-level count and
  an inverted membership test -- and not product defects. The lesson
  worth keeping: **no commit message may claim "every check clean"
  unless the checks actually ran on the STAGED tree**, because the
  scanners walk the tracked tree and will silently skip a file you have
  not added yet.
- The open defects of Phase 4 are the residual register at the foot of
  `docs/plans/phase-4-columns.md`. The 2026-08-26 triage sorted them:
  15 deliberate scope declines, 11 real landings, 7 owner questions.

## The rules an assistant breaks first here

1. **Never change the decontamination scanner to make text pass** —
   change the text. Some ordinary words are denied, including ones
   that look entirely ordinary: the three-letter abbreviation for a
   review board is one, so spell that phrase out. PROBE BEFORE YOU
   WRITE rather than guessing — `tools/decontamination` holds the
   hashed manifest and `check.tokenize` plus the magic prefixes turn
   the question into a lookup. **A file you have not committed yet is
   not scanned**, because the scanner walks the TRACKED tree; that is
   how a denied token reached this very line and survived a green
   run.
2. **The generator never reads a table.** Only the profiler and the
   validator open a CSV. No test helper crosses that line.
3. **Every published sentence is an enumerated form**, not a string
   written at the call site. Check `taxonomy.NOTE_ARITY`.
4. **A closed enumeration is stated in up to eight places.** Adding a
   role or a settings key means finding all of them; the guards will
   tell you, but only after they turn red.
5. **Never close a residual on a reading.** Build the column it
   describes and run it. Two of two closure claims in the 2026-08-26
   triage were wrong, and one hid a live misdescription.

## How a new conversation gets its bearings — READ THIS IF YOU ARE NEW

**Four things carry this project, and none of them is the contract.**
The contract is 8,553 lines and the phase plan 5,730: no session reads
either, which is exactly why freezing them (A-P4-46) costs almost no
context. What a session can actually hold is about 1,900 lines, and it
is these:

| what | size | how it reaches you |
|---|---|---|
| `CLAUDE.md` | 316 lines | loaded automatically in every conversation here |
| **this page** | ~200 lines | `CLAUDE.md`'s first instruction is to read it |
| the assistant's own memory | ~1,300 lines | loaded at session start, outside the repository |
| **docstrings — 1,204 of them, 15,088 lines** | | read whenever the code is read, which is when it matters |

**The docstrings ARE the specification now.** Every public function's
docstring states what it promises — accepted inputs, determinism,
errors, and any boundary it upholds — because the charter has always
required that. With the contract frozen, they stop being a second copy
and become the first one. Write them that way: a rule that lives only
in a frozen document is a rule nobody will meet.

**And the tests are the other half.** A test says what must be true in
a form that cannot drift. When you would have written a contract
clause, write a test instead.

## Already tried here, and it does not work

Kept short on purpose. Each of these cost at least half a day.

- **A pronoun cannot be resolved by a regular expression.** Three
  rounds went into `it`, then number agreement; both broke in both
  directions. A rule that needs reference resolution must instead
  demand that the prose NAME the thing.
- **Widening a ban's noun list reports honest prose.** Name the SHAPE
  of the claim, never broaden the noun.
- **A guard that passes is not a guard.** Mutation-verify every new
  one before believing it; this project has repeatedly produced tests
  that passed for the wrong reason.
- **Where a review names one site, there are usually two or three.**
  Search for siblings rather than repairing the site named.
- **A count restated in several places will disagree.** Compute it
  from one source and check every site that states it.
- **Run the guards AFTER `git add`.** The decontamination scanner
  walks the TRACKED tree, so an uncommitted file is not scanned.
- **A repair that prints ambiguous numbers is worse than the silence
  it replaced.** Withdraw it and record the defect instead.

## Where the detail lives

| you want | read |
|---|---|
| the principles and the honest limits | `CLAUDE.md` |
| what the reviewer holds this to | `AGENTS.md` |
| the current phase, its decisions and its open items | `docs/plans/phase-4-columns.md` |
| what a description may contain | `docs/spec/profile-contract-v6.md` |
| what changed, in order | `CHANGELOG.md` |
| the project in plain language, for an outside reader | `STATUS.md` |

## Owed before the phase closes, by owner instruction (2026-08-26)

**Richer numeric statistics — RULED, five facts.** `skew` and `std`
already exist and the ladder is eleven rungs. The owner ruled the whole
list in on 2026-08-26:

1. **A histogram**, and it matters more than the extra rungs: moments
   and percentiles cannot show two peaks, so a bimodal column yields a
   smooth twin with every published number correct.
2. **All 100 percentiles.**
3. **Kurtosis**, which pairs with skew.
4. **The count of different numbers** (already planned, R-P4-20).
5. **The mode**, for columns where one value dominates.

Design notes — bin edges must be chosen by a reproducible RULE since
the generator has only the description; bin counts fall under the
small-cell floor while percentiles are exact real values and do not;
and the generator must MEET the histogram rather than draw from the
ladder and hope. Fuller notes in the assistant's memory under
`numeric-depth-revisit`. Build beside the distinct-count and width
work, which touch the same machinery.

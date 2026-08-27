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
| suite | 3,968 collected / 48 skipped |
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
* **THE FIRST FROZEN VECTOR FOR A PHASE 4 ROLE EXISTS (residual
  R-P4-17, partly closed).** Before it, every case in either frozen
  file exercised a role Phase 1 to 3 built, so all four Phase 4 roles
  were checked against the implementation alone — a defect written into
  the generator would have been written into its own proof.
  `long_tail_levels` is written from contract 6.6 and method G8.1 to
  G8.4 in the oracle that never imports synthtwin, and the shipped
  generator reproduces its cells.

  **Writing it independently is what found the mistakes**, which is the
  argument that residual makes, demonstrated: five drafts refused by
  the loader and one by the vacuity check, each for a fact about the
  role the implementation knew and I did not — the axis pair, a key
  the role may not carry, what folded distinctness counts, what the
  floor does to a published level, and finally that the first four
  drafts were categorical columns wearing the name.

  **Three roles remain**: `affixed_number`, `time_of_day`,
  `joined_numbers`. This one was cheapest because a long tail carries
  the label roles' keys and no key of its own, so the oracle's existing
  label machinery reached it.

  **Adversarial review then rejected the committed vector, and the
  HIGH item was right.** It published a form census of
  `{"@@@@-@@": 29, "(withheld)": 11}` — a census no profiler can
  write, because the eleven published cells are spelled `Note Alpha`
  and a cell holding a SPACE has no form at all, while `(withheld)`
  means a group too small to name, which eleven cells at a floor of
  eleven are not. The true census was measured against the profiler on
  a table of that exact shape and reads `{"@@@@-@@": 29}`. Correcting
  it left **every frozen cell unchanged**: what was wrong was the
  description's producibility, not the transform. Two stale figures in
  the case's own prose, left from an earlier draft, were corrected in
  the same pass, and the reviewer's fair point that the case pins
  admission and routing rather than a generator branch of the role's
  own is now stated in G14.3 at that width.

* **A JOINED COLUMN OF THREE OR MORE POSITIONS REPRODUCES ONLY THE
  PAIRS ITS LAST POSITION IS IN (residual R-P4-51, opened
  2026-08-27).** The pairing walk moves only the last position and
  scores only the pairs whose later member is that position. At two
  positions there is exactly one pair and it is that one, so nothing
  showed. At three, the pairs among the earlier positions are neither
  moved nor scored, and they come out at `+1` whatever was published.
  Measured on a three-position column whose first two positions are
  perfectly anti-correlated: published −1.0, twin **+1.0** — the exact
  opposite — with the other two pairs also missed.

  **A person is still told.** The twin's own report names none of them
  (that is R-P4-44's split, not this), but `synthtwin validate` on that
  twin returns all three `part_agreements` and `part_above[0]` MISSED.
  So the shortfall reaches the command that exists to report it, and
  the documents no longer claim the walk reproduces every published
  pairing fact — method G6B states the bound and prints the table.

  It is a residual and not a defect: moving more than one position is a
  different search whose objective would have to arbitrate between
  pairs that pull against each other, which is design work priced with
  L7's joined-role items.

* **A last-resort straggler could be spelled the way a hole is
  spelled.** Where every candidate wears the affix pair, the affixed
  role's straggler walk exhausts its ceiling and falls through to
  cells of the package's own — and that branch kept two of the walk's
  three refusals, missing the one that forbids a spelling the column
  publishes as a HOLE. A present cell spelled that way is read as
  absent by the twin's own description. Fixed, with the branch pinned
  directly; reaching it from the profiler was not achieved while the
  refusal was added, so it is recorded as a guard rather than as a
  demonstrated repair.

* **A SECOND PHASE 4 ROLE NOW HAS A FROZEN VECTOR: `time_of_day`.**
  `clock_ladder` is written from method section G7A alone, in the
  oracle that never imports synthtwin, and the shipped generator
  reproduces its twelve cells exactly. It is a column with no slack —
  ends eleven seconds apart, eleven parsed cells, every value published
  different — so the all-different repair, which is EXACT for this
  role, must place each interior rank on the one ordinal left for it.
  Its mutant withdraws the step-up and the same column then writes two
  times twice, in the oracle and in the shipped generator alike.

  Two roles remain: `affixed_number` and `joined_numbers`. Both now
  have a method section, so neither is blocked on anything but work.

* **THE THREE REMAINING ROLES HAD NO METHOD SECTION AT ALL — found
  2026-08-27, and now written.** The oracle's whole value is that it
  implements `docs/spec/generation-method-v1.md` and imports nothing
  from `src/`. In that document `time_of_day` appeared zero times,
  `joined_numbers` zero times, and `affixed_number` once in a sentence
  about a different key; all fifteen `clock` mentions belonged to the
  datetime role's timezone clock. There was nothing to build a vector
  from. Two neighbouring gaps compounded it: **G4.3's draw budget
  omitted all four Phase 4 roles** — and because one stream feeds every
  column in order, a wrong budget shifts every later column at the same
  seed, which is the failure that document names as the one thing it
  exists to prevent — and **G11's all-different table omitted the same
  four** while its list of instances ran one short.

  Now written and each one measured, not transcribed: **G7A**, a full
  section for `time_of_day`; **four rows in G4.3**, the clock rule
  checked on eight described columns, the affixed rule on three and the
  joined rule on five at two and three positions; and **G11's four rows
  plus a fourth instance** — joined-number columns, where the pairing
  cannot reach the published count, measured at 375–385 of 378–388
  across six columns with every shortfall reported.

  **The limit of this, stated:** these sections were written by reading
  the shipped generator, which is the inverse of the order this
  repository requires. A specification transcribed from an
  implementation, and an oracle later written from it by the same
  author, share whatever the implementation got wrong. What it buys is
  that the behaviour is written down and reviewable and that the next
  three vectors have a document to be built from. It does not buy
  independence.

  Writing G7A also removed an overclaim from the generator: the
  capacity refusal `_clock_room` does not "guarantee a place for every
  one of them" — it tests the FORM's capacity, not the span between the
  published ends. A hand-written description with ends eleven minutes
  apart asking for a hundred different values passes it, and the twin
  then holds 11 different times and reports the shortfall. On a
  profiler-written description the claim does hold, and G7A.3 now
  carries the proof instead of the assertion.

* **TWO JOINED-ROLE DEFECTS, FOUND AND FIXED 2026-08-27.** Both came
  out of writing that role's missing method section, not out of the
  suite, which was green throughout.

  **The tool wrote a profile it could not read.** A POSITION of a
  joined column describes only the cells that split, so the profiler
  writes `n_joined` as that block's row count; invariant Q1 compared it
  against the TABLE's row count. Those agree exactly when no cell
  failed to split, so **every joined column carrying even one unparsed
  cell was refused by the loader that had just been handed the
  profiler's own output** — and the refusal told the user their
  description "has been changed since it was written" and to make it
  again, which produces the same file. Measured at 200 rows:
  `n_unparsed` of 1 or 2 refused, 0 accepted, 3 or more leaves the role
  entirely, which is why the window is narrow and why it survived the
  phase. A block of numbers now echoes the row count of whatever it
  describes.

  **A column that met its published count was told it missed.** Cells
  that did not split are replaced, after the pairing, by stand-ins that
  are all one spelling, so they add exactly one to the number of
  different cells however many there are. The pairing was handed the
  whole column's `n_distinct` anyway and compared against it: a
  120-cell column whose twin held 120 different cells reported "120
  published, 119 achieved", while the recount in the same report said
  120. The pairing is now asked for the count the pairs can carry.

  Each fix has a test that turns red when that fix alone is reverted.

* **THE FINER PERCENTILE LADDER IS DESIGNED AND NOT BUILT (plan
  P4-D4.10), and the measurement behind it is the useful part.** The
  owner asked for "every p value (1 to 100)". Reconstructing R-P4-30's
  own dental-code column from its rungs alone: from eleven rungs, 79
  cells below 1000 against a true 97 — which IS that residual's defect,
  measured independently — and from a hundred and one rungs, 97, an
  error of zero. The owner's ask and R-P4-30 are one piece of work.

  **It must land as ONE key, not as 101.** Every published rung owes a
  registered red case: a perturbation shown to make THAT subcheck
  report MISSED. The entry table carries 99 of them for eleven rungs;
  at 101 that is about nine hundred, which cannot be done honestly.
  And it will work where the histogram did not, because a ladder asks
  the twin to PLACE VALUES and interpolating a ladder is what
  `_stratum_values` already does — no new mechanism, only a longer
  list in the one it uses.

  **One thing for the owner before the key is written:** a rung is an
  exact value of a real cell. 101 rungs name up to 101 of them; on a
  400-row column that is a quarter of the column named. Their 2026-08-24
  ruling covers disclosure of this kind, but this is a step change in
  degree rather than a repeat of that question.

* **THE COUNT OF DIFFERENT NUMBERS IS PUBLISHED (plan P4-D4.9),
  closing residual R-P4-20.** `n_distinct` counts SPELLINGS on every
  role -- `1` and `01` are two of them and one number -- so nothing
  bound the number count at all, and a twin could meet every
  distinctness fact it was given while holding fewer numbers than the
  real column. Measured: a 200-row column of tightly clustered values
  held all 166 published spellings and 163 numbers with NO deviation
  anywhere; the demonstration report now names the same gap on its own
  `reading` column, 178 published against 165 held.

  It is REPORT-ONLY, and that is R-P4-20's own framing: what was
  missing is a PUBLISHED count. The twin is not held to it -- the
  kept-sentinel fixture publishes 49 and holds 44 -- and the generator
  NAMES the shortfall, which is precisely what nobody was told before.
  Narrowing the shortfall is the snap's business (P4-D4.5).

* **THE KURTOSIS IS PUBLISHED AND CHECKED (plan P4-D4.8).** The owner's
  second ask of 2026-08-26, and it cost what they said it would: one
  number. It rides the exact integer totals Phase 1 already computes --
  one more power added to the same sums -- and it is APPROXIMATED under
  a window that is the skewness window one moment along, checked by the
  generator's report and by the validator, with red cases registered so
  the check can be shown to fail.

  Three things worth not rediscovering. It is the MOMENT RATIO and not
  the excess, so a normal curve reads 3 here (the same convention
  `skew` beside it uses). It needs FOUR values, as the skewness needs
  three. And it needs **no overflow guard**, unlike the spread: a
  moment ratio lies between 1 and `n - 2 + 1/(n - 1)` for any n values,
  so the row count bounds it -- verified against the extreme
  configuration at four, five, eight and twenty values, where the
  computed value equals that bound exactly.

* **THE VALUE HISTOGRAM IS PUBLISHED (plan P4-D4.7), and the twin does
  not yet hold it.** The owner asked for it first, ahead of the extra
  percentile rungs, because moments and percentiles cannot show two
  peaks: measured on a 300-row column of two populations, the source
  leaves fifteen of the thirty-two bins empty and the twin fills every
  one of them while meeting the ladder, the mean, the spread and the
  skew exactly and raising no deviation, because none of those facts
  can tell.

  What landed is the FACT: produced, published, carried through the
  loader under invariant Q15, in the contract's key tables and
  forbidden-key matrix, disposed REPORT-ONLY, listed by the validator,
  and said in words when a column cannot publish it. The twin's cells
  are byte-identical and the report gained exactly two lines, both of
  them the new note.

  **Consuming it is R-P4-49 and starts at the ALLOTMENT, not the
  values.** A version that bent the value walk toward the shape was
  built and withdrawn: it helped a great deal (the bimodal column's
  empty stretch fell from about a hundred twin values to sixteen) and
  it broke the rungs, then method G12.2's window, then the style map,
  and still missed the bin counts -- because a bin count says how many
  cells hold each value, and cells are allotted by G5.2's even share.
  The withdrawal is written up in the plan under R-P4-49.

* **Gap 3 is DONE, through six adversarial rounds.** Round 5 found six
  things and round 6 found four more, all reproduced and repaired here.

  **A NOTE ON THE REVIEWER'S FAILURE MODE, because it cost real time
  and it will happen again.** `codex exec -o FILE` writes the verdict
  file LATE -- after the process has already exited and after the task
  notification says it completed. Six runs looked like the stall the
  owner described; every one of them had in fact written its verdict,
  and I relaunched over the top of four of them. One landed commit
  claimed "round 6 could not be obtained", which was false. **Check for
  the verdict file again a few minutes after the run reports done,
  before concluding anything about a stall**, and never relaunch on the
  strength of an immediate check alone.
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

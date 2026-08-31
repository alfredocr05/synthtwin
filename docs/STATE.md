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
| branch | `phase-4-allotment` (never merged; `main` is pull-request only) |
| phase | **Phase 4 — comprehensive column handling.** Current. |
| plan | `docs/plans/phase-4-columns.md` |
| suite | 4,152 collected / 51 skipped |
| lint | **10 pre-existing errors** (`ruff check .`) under the rule set pinned in `pyproject.toml`, measured 2026-08-31 at `c10f5f6`; every file this landing touched is clean |

## What is being built right now

**THE PHASE 4 GAP RUN**, under the owner's standing authorization of
2026-08-26 ("feel free to move through all the gaps without my
consent", review aimed at machinery only). Gaps 1, 2 and 3 have
landed; gaps 4 to 7, the richer number family and the worked examples
are still ahead. The gap list itself is at the foot of this page.

* **Gap 1 — the address rule.** An affixed-number column no longer
  reads an e-mail address as a number wrapped in affixes.

  **AND SINCE 2026-08-31 THE DECLINE SPEAKS.** The rule was right and
  is untouched; what was wrong is that it was SILENT. A person whose
  column stopped being described as numbers — losing its average, its
  spread, its ends and its ladder — was told nothing, because
  `taxonomy.NOTE_ARITY` carried no address form at all and every
  surface builds its sentences from that table. Principle 5 does not
  say a column is either handled or declined; it says handled or
  **declined with a plain-language explanation**.

  It is contract **NF50**, `remark_an_address_is_not_a_quantity`,
  arity 0. It names the SHAPE — an at sign, a host, a dot label — so a
  person recognizes their own column, and it names all THREE
  declarations where the free-text remark beside it offered only
  `--identifier`, each with what it does and each outcome measured on
  that column rather than read off the flag's help: `--identifier`
  gives `identifier` and publishes no value, `--code` gives
  `long_tail_labels` and publishes each spelling with its count,
  `--measurement` restores `affixed_number` and its distribution.

  **It routes nothing, measured rather than asserted:** with the
  decline's own question answered False the block is identical key for
  key and role for role, and only the sentence is gone. Arity 0 is
  deliberate — a count of the cells that wore the pair is a count of a
  reading this column does not publish, and the pair itself is the
  fourth argument class, admitted only where the same block publishes
  the spelling.

  **AND LOOKING AT THE DECLINE'S SIBLINGS FOUND A SILENT STATISTICAL
  DEFECT**, which is this project's standing lesson paying again.
  `_cores_judged` — the pass that judges stand-ins over an affixed
  column's CORES (C6-5) — re-derived the affix reading WITHOUT the
  person's declarations, while its own caller decided the role WITH
  them. The two therefore disagreed on every column that is affixed
  only BECAUSE of a declaration, and there is exactly one such shape:
  an address column carried past the decline by `--measurement`. The
  caller saw the role, the pass saw the decline, and every cell went
  unjudged. Measured on 200 cells of `user<core>@example.org`, 189
  cores between 50 and 70 beside eleven spelled `-999`: **no verdict
  published, `-999` standing as the column's smallest reading, and the
  mean 1.785 where the same column wearing an ordinary pair reads
  60.03**. Fixed by handing the pass the declaration its caller used;
  the two now agree cell for cell, and a test turns red when that
  alone is reverted.

  **AND ONE CONTROL GAP IS OPENED RATHER THAN CLOSED: R-P4-67.**
  Adding a form meant reading the guard that holds the note grammar
  together, and every one of its three directions is about a NAME or a
  COUNT. The contract also writes each form's rendering out character
  for character — it says so in as many words — and **nothing compares
  those blockquotes against what `taxonomy.rendered` writes**, which
  is the one thing a second implementer would build from. Measured
  over the twenty arity-0 forms, where the comparison is exact:
  seventeen identical, **two really drifted** (an em dash for `--`,
  and `numbers:` for `numbers;`), and the other thirty forms take
  arguments and are not compared at all. NF50's own rendering was
  checked against that measurement and is identical.
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

  **A person is told by BOTH pages, and that took two review rounds.**
  The twin's own report names them and so does `synthtwin validate`,
  and the two agree about which pair is which: the pairs the walk moves
  are approximated against G12.9's window, and the pair it never moves
  is a plain MISS on both -- a deviation in the twin's report and an
  exact check with no citation in the quality report. It named none of
  them until R-P4-44 closed; then the two pages disagreed until
  P4-G3-R2-F3, one calling a pair unscored while the other handed it
  the window of the section that excludes it; and then a round briefly
  EXCUSED it as an AUTHORIZED-DEVIATION, which P4-G3-R3-F2 withdrew
  because G12.9 withholds the window and not the obligation. So the
  shortfall reaches the command that
  exists to report it, and
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

  **And a third the same day: `affixed_number`.** `affixed_brackets`
  pins the rule that role exists for — its universal class counts
  answer for the CELLS, its quantitative block for the CORES, and only
  the second set reaches the numeric rules. The mutant hands over the
  cell counts and the oracle stops at the word budget, which G4.3 reads
  over the cores too. Writing it independently found a role fact the
  documents alone did not carry, for the third time: a block of this
  role must carry its own REMARK, and the loader refused the case until
  it was there.

  Its adversarial read also found a rule the oracle had wrong for every
  case carrying `n_distinct_values`: that fact is about the SOURCE
  column, and the oracle was overwriting it with a count of the twin's
  own cells — so no frozen case could exercise a miss of it, which is
  the one thing it being REPORT-ONLY is for. A case may now publish its
  own; this one publishes twelve, its twin holds eleven, and the
  generator reports the miss. No other case's cells moved.

  **And the fourth, which closes the residual: `joined_numbers`.**
  `joined_readings` pins the pairing walk — the only search in the
  method. It was designed against the vacuity check: the first draft
  published an agreement of 0.9983, which a rank-for-rank start already
  meets, so removing the walk changed nothing and the case would have
  proved nothing. The committed column publishes 0.4323 and with the
  walk withdrawn six of its twelve cells move. Withdrawing each of the
  walk's rules in turn shows it pins six of them — the walk itself, the
  cursor restart, the threshold's value, accept-on-equal, that a try
  ceiling exists, and the `part_above` term — and not five others,
  which are named in the section rather than left implied.

  Measuring that corrected a false claim in the method: G6B.4 said the
  zero-based rank origin writes different cells. It does not — rank
  agreement is translation-invariant, so one-based ranks with their own
  middle write identical bytes. What had been measured was ranks moved
  with the middle left behind, which is a defect rather than the other
  convention.

  Writing it validated the section: the walk is 237 lines in the
  generator, the oracle's is written from G6B.4's text alone, and the
  two write the same bytes.

  **R-P4-17 is CLOSED** — all four roles Phase 4 added have a frozen
  case with a failing mutant. The stated limit stands: three of the
  four method sections were written from the shipped implementation, so
  they buy reviewability rather than independence.

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

* **THE MODE IS PUBLISHED (the owner's fifth numeric ask), and it is
  REPORT-ONLY.** `mode` is the number a column held most often and
  `mode_count` is how many cells held it, governed by the small-cell
  floor and by a two-cell minimum, tied by the smallest, and identified
  by the exact number so two spellings of one number are one value.
  Invariant Q18 refuses a half-published pair.

  **It was measured before it was built**, because the histogram taught
  that a fact nothing consumes does not improve a twin. On five 300-row
  columns the twin was 17 to 28 per cent short of the real count of a
  dominant value — the gap the owner named. And the mechanism to close
  it already exists and is proven: G5.2's ZERO STRATUM meets one value
  at one published count exactly, measured at counts of 0, 30 and 120.

  **But it is not EXACT yet, and the first draft said it was.** Written
  as a CHECK, it turned sixty-three tests red — "a twin of its own
  description misses nothing" among them, the product's headline claim
  — because a check is an obligation and the generator carves no
  stratum for the mode. That is the fourth fact this phase to walk into
  the trap, and the rule from the first three applies: REPORT-ONLY, and
  the quality report LISTS it rather than holding a file to it. Adding
  it moved no twin byte, which is what REPORT-ONLY should mean.

  The stratum that would make it exact is designed in P4-D4.11, with
  both its feasibility questions already settled: the count can never
  exceed what the strata leave room for on a profiler-written
  description (proved, 40 columns measured), and the mode sits at a
  published endpoint one time in four, so that is a named rule rather
  than a case to discover later.

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

**R-P4-25 IS CLOSED (2026-08-31, landing A1). The disposition
machinery reads the contract that GOVERNS.** The safety-critical half
landed earlier: version 6 joined the sealed governing set, so the
contract that governs every description this tree writes is under the
seal -- it had been outside it, carried as a "draft under adversarial
review", while `PROFILE_VERSION` was already 6 in the producer and the
loader.

The rest landed now. BOTH matrix readers took version 4's section 9
merged with version 5's delta -- the record of what two superseded
versions required -- so the agreement they asserted was luck rather
than design. **The second reader was not named in the residual and was
found by looking for the first one's siblings**, which is this
project's standing lesson paying again: `_matrix` in
`tests/test_p2c4f1_disposition_registry.py`, and `_matrix_rows` /
`_matrix_sections` in `tests/test_p2c1f4_approximation_bounds.py`.

**What the migration DELETED is the measure of it.** Every one of these
existed only because a reader was asking a document about roles it
predates:

* `GROUPS_OUTSIDE_THE_VERSION_4_MATRIX` -- `affixed` and `clock` stood
  outside a matrix entirely. Version 6 gives each a sub-table, so both
  bind, and every registered group is in `CONTRACT_SECTIONS` now with
  no exemption left in the totality assertion.
* the carve-out list, **13 rows to 6**. What remains is exactly the
  family that landed AFTER amendment A-P4-46 froze the contract -- the
  histogram, the kurtosis, the value count, the mode pair and the finer
  ladder -- each held to the Phase 4 plan.
* `FACTS_A_LATER_VERSION_REDISPOSES`, the `missing_by_source` class
  exception; six families of exemption in the second reader; and the
  version 5 delta reader.
* **the clock role's approximated inventory stopped being written out
  by hand.** It is read from version 6's own table -- and what version
  6 produces is character for character the list that had been written
  there, which is what says the migration kept the obligation rather
  than moving it.

**ONE CONTRACT EDIT, under a counted diff read before re-sealing.**
Version 6's 9.6 row for the clock ladder ends names
`clock_percentiles.min` and `.max` now instead of describing them in
prose, as the datetime table beside it already did. One passage out,
one in, 2,016 both sides, class unchanged.

**ROUND P4-A1-R1 REJECTED IT WITH FOUR ITEMS AND EVERY ONE WAS REAL.**
Two were HIGH:

* **The affixed sub-table's RESTATED rows were checked by name and not
  by class.** Version 6 restates the numeric dispositions over the
  cores, and those keys stay registered under `numeric`, so the
  key-by-key walk looked up `("affixed", "mean")`, found nothing and
  skipped the row. Lowering the restated `mean`, `std`, `skew` to
  REPORT-ONLY left both readers GREEN -- reproduced -- and only the
  SEAL went red. **A seal is not the net for a lowering**, because a
  seal is re-written whenever an edit is intended. The restatement is
  held to the numeric table in both directions now, with the two
  delegating rows ("as on `count` and `continuous` above") resolved
  mechanically. Three mutations verify it.
* **Section 9.4a was newly PARSED and claimed by nothing.** The joined
  role's table is read and visited by no group, so deleting or
  lowering `part_agreements` moves no guard. Before the migration it
  was not parsed at all, so the hole was equally open -- what changed
  is that it now LOOKS covered, which is worse. It is named, with the
  residual that owes it, and a totality guard fails if another orphan
  appears or if the excuse outlives R-P4-62. **That residual is the
  next landing's whole subject.**

**ROUND 3 REJECTED IT AGAIN with three HIGH items, and the first one
is the most useful thing on this page.** THREE CHECKS DIED TRYING TO
COMPARE A RESTATEMENT AGAINST WHAT IT RESTATED, each beaten by a
subtler lowering than the last:

1. round 1 checked the extra NAMES were numeric keys -- lowering the
   restated `mean`, `std`, `skew` row passed;
2. round 2 compared the class each row HEADS with -- appending
   "REPORT-ONLY in this corner" passed;
3. round 3 compared the whole ordered SEQUENCE of classes -- writing
   "EXACT-OBSERVABLE (the class named by the numeric citation);
   APPROXIMATED for every affixed column" passed, because it is the
   same sequence with the CONDITION inverted, from "only where
   spellings cannot supply the count" to "always".

**The answer was to stop having two statements to compare.** Version
6's affixed sub-table DELEGATES every key it shares with the numeric
roles -- "as on `count` and `continuous` above" -- and states no class
of its own for any of them. Only the seven keys the role ADDS carry a
class, because those are disposed there and nowhere else. The guard
now checks the delegation is TOTAL and PURE: every shared numeric key
is delegated, no delegated row smuggles a class word back, and none
goes missing. Five mutations verify it, including all three rounds'
own attacks. This is the project's standing lesson arriving one level
up: **a fact written twice will drift, and the fix is to stop writing
it twice rather than to compare the copies harder.**

**ROUND 4 REJECTED IT AGAIN with four items, ALL CONTROL GAPS, and the
first says the delegation was not yet pure.** A delegated cell held
the phrase and no class WORD, and free prose beside it could still say
the opposite: "as on `count` and `continuous` above; for affixed cores
this value need only be mentioned in the report" passed. So would a
lower-case `report-only`, a Markdown-split `REPORT-**ONLY**`, or a
Unicode hyphen -- hunting the vocabulary restarts the contest one
spelling at a time. **The cell is now EXACTLY the delegation phrase
and nothing else**, so there is no room in it for a second statement
whatever words it would have used. Everything the rows used to say
moved into the sub-table's head paragraph, where it is the scope of
the table rather than a per-key rule -- AF6's "never inferred from the
role name" included. Five mutations verify it, the synonym and
formatting family among them.

**That is FOUR checks beaten in four rounds on one surface**, each by
a subtler lowering: names, then the head class word, then the ordered
class sequence, then prose carrying no class at all. The lesson is
worth more than the fix: **when a control keeps being beaten by a
cleverer sentence, stop parsing sentences.** A closed syntax -- this
cell equals this string -- ends what a vocabulary check cannot.

**A POSITIVE guard still named version 5 as "the contract that governs
the format".** `KEPT_BEARING` in `tests/test_claim_inventory.py` lists
the six surfaces that must SAY the person's own word travels, and its
contract member was a literal: deleting the disclosure from version 6
left the guard green because it was reading version 5. It derives from
`fixtures.GOVERNING_CONTRACT` now, and the deletion turns it red --
measured. This is R-P4-25's own shape in the one place the inventory
makes a positive assertion rather than a negative scan.

**And the import-time assertion was unsound in a context this
repository itself ships.** The source distribution includes `tests`
and `tools` and does NOT include `docs`, and several measurement tools
import `fixtures` without ever opening the contract -- so `import
fixtures` would raise in an unpacked distribution over a document that
tool had no use for. The check is LAZY now, in
`fixtures.governing_contract_text()`, where the document is actually
wanted.

**The residual guard needed a fourth version.** Scanning the whole
plan let an open-looking bullet written anywhere answer for a register
entry that had been closed; capturing one physical line let a heading
split across two lines hide its own closure word; and the name
boundary let `R-P4-62a` answer for `R-P4-62`. It reads the **P4-D13
register region only**, takes each entry's whole bold HEADING across
line breaks, and requires an exact name boundary and exactly one
canonical entry. Four mutations verify it. Reading the whole entry
BODY was wrong in the other direction and was tried first: an entry
legitimately says that OTHER residuals are closed.

**Round 3's other two were siblings I had already been warned about.**
FOUR more current-contract readers were still pinned to a literal
`profile-contract-v6.md` -- the producer-membership guard, the role
topology guard, the note-grammar guard and the loader-message
comparison -- so a version bump that edited the producer and the
loader would have left them certifying a document that no longer
governs, which is R-P4-25 itself. There is now ONE derivation,
`fixtures.GOVERNING_CONTRACT`, taken from `contract.PROFILE_VERSION`,
and every current-contract reader uses it; only deliberately
historical readers name a version. And the open-residual guard
accepted any heading merely lacking the word CLOSED, so "RESOLVED"
would have defeated it, as would the register's real duplicate
headings, where a closed historical entry sits beside an open one. It
requires exactly ONE canonical entry per cited name now, whose heading
carries none of this register's closure words. Three mutations verify
it.

The other two of round 2: the landing had not moved this page or the plan (both
done here), and **R-P4-63** -- the loader's own docstring said version
5 was normative with `PROFILE_VERSION` at 6, which is fixed here, plus
two specification-text guards still reading version 4, which are NOT
fixed and are priced in the register with the measurement behind the
price.

**AND THE ENVIRONMENT ATE THIS LANDING ONCE, which is worth more than
the landing.** Mid-way through a full suite run, the eight files this
work had modified were restored to their committed state -- measured:
exactly the modified set and their caches, at one timestamp, with no
`git` reflog entry, which is what an external restore or a
`git checkout --` leaves. **This repository lives inside a
cloud-synced folder.** The work was recoverable only because a diff
had been written outside that folder minutes earlier. **Commit early,
and keep a copy of uncommitted work outside the synced tree**; a green
suite is not durable here until it is committed.

**R-P4-62 IS CLOSED (2026-08-31, landing A2). Every completeness guard
reaches the joined role.** It was the role that carries a blood
pressure and the one role no surface looked at: three guards each
proved their own completeness against a table that does not contain
it, so each passed by never looking. Six repairs, and three of them
were not in the residual when it was opened.

* **The registry has a `joined` group** -- ten facts where there were
  none -- written from contract 9.4a. `parts` is STRUCTURAL, on the
  precedent `length` and `words` set on `free_text`.
* **The completeness walk reaches the role**, through a document of
  its own; it used to close with `reached == set(ROLE_SECTIONS)`,
  which a fixture that never built the role satisfies.
* **The red battery has a joined fixture with NINETY-NINE registered
  red cases, every one MEASURED** -- each perturbation run against the
  fixture, and the one that turns each site red is the one named.
* **`validation._group_of` had no `JoinedFacts` branch**, so a joined
  column fell through to `return "empty"` and its distinctness was
  reported as `empty.n_distinct`, under the identity of a role that
  publishes both counts as 0 and exactly observable. **Found by
  measuring a blood-pressure column through the real pipeline, not by
  any guard**, which is this residual's own point made once more.
* **The contract disposed neither of those counts for this role.**
  9.2 sets them "per role group" and 9.4a set neither, which is why
  the mis-filing could not be noticed: the fact was filed under a
  group that DOES dispose them. They are REPORT-ONLY now (plan
  P4-D29).
* **A joined position's report-only facts are LISTED.**
  `_quantitative_of` returns no block for this role, so per-position
  `n_distinct_values` and `percentiles_between` were neither checked
  nor listed. That was review item P4-A1-R2-F2, and it means residual
  R-P4-58 closed only the half of its own scope that said "nothing
  checks".

**THE DISPOSITION WAS DECIDED TWICE, AND THE SECOND TIME WAS RIGHT.**
It was made REPORT-ONLY on two measurements: every joined column whose
cells REPEAT overshoots its published count (80 published, 210 held),
and even an all-different column reaches it at one seed and misses by
one at another -- so an exact obligation looked like one met or missed
BY THE SEED. And the twin's own report already prints "the description
says 120 / the twin holds 119", so nothing seemed hidden.

**Adversarial round P4-A2-R1 refuted both halves and built the
counter-example.** `synthtwin validate` measures ANY file a person
names, not the twin this run happened to make. A 240-row source of 120
`100/60` and 120 `101/61` publishes two different cells; hand it a file
that keeps each position's multiset and re-pairs the numbers and it
holds FOUR, with every endpoint, moment, width, style, count and
above-count identical and the agreement inside G12.9's window.
**Measured: with the counts report-only that file passed with 74 HELD
and NOT ONE MISS. It now reports two.** So report-only did not decline
to hold a file to a fact; it removed the only verdict-bearing check
that fact had, and the generation report cannot stand in, because it
passes no verdict at all and the charter says so.

**The seed-dependence is a fact about the GENERATOR, not about
observability** -- that is R-P4-40, and it is not a reason to stop
checking files. The lesson is sharper than the fix: **"the twin cannot
always meet it" and "no file can be held to it" are different claims,
and I ran the first into the second.**

**THE FIXTURE IS ITS OWN, and the register assumed otherwise.** The
role REQUIRES a `--measurement` declaration, so it cannot be a
fourteenth column of `every_role_table`: all forty-nine call sites
would have to pass one and any that missed it would give the column
another role in silence. The entry table already answers this for
`numeric_unrepresentable` with a dedicated fixture. Its shape is
measured -- two positions (three cannot honour their (1,2) pair,
R-P4-51), all different, non-overlapping bands, and a companion column
without which `axes.quality_state` would be a site no edit could turn
red.

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

What is owed to the owner rather than from them is a decision about
the TEN lint errors this tree carries — whether to fix them or record
them — and that does not stop any landing. (The 183 that stood here
were a different matter and were closed by pinning the rule set; the
ten are what remains under that pinned set. See "What is broken right
now".)

## The joined role's own gaps, all opened by review and all owed

`joined_numbers` (P4-D21, P4-D23, P4-D25) carries four recorded gaps.
None was caused by the landing that found them; all are **Phase 4
close blockers** rather than acceptable release residuals, on the
reviewer's ruling of 2026-08-26.

| # | gap | goes to |
|---|---|---|
| **R-P4-42 — CLOSED 2026-08-27** | the window was cited as `docs/plans/phase-4-columns.md P4-D25` while every other envelope of the method cites a section of it, so an implementer working from the specification could not find it and a reader could not find the rule a verdict rests on. It is now **G12.9** of the generation method — the two-sided 0.02 window, why it is a window and not an exactness, and what it does NOT excuse — and the report cites that | closed |
| **R-P4-43 — CLOSED 2026-08-27** | it checked a position's endpoints, average and whole-number test and not its styles or either width census. Each position now carries the style identity read over its own numbers, named per position. The residual's own example had gone stale — `200` rewritten as `200.0` is already caught — so the red case is half a position zero-padded, which moves the census and leaves the widths held | closed |
| **R-P4-44 — CLOSED 2026-08-27** | the report now names every approximated fact of every position — nine rungs and four moments each — and the rank agreement beside them, against G12.9's window. All four faults that withdrew the first attempt are answered by name: no per-position count the profile publishes for no position (distinctness is suppressed for a position and a test pins that), every record names its position in the identifier AND in the sentence, a cell counts for a position only where it splits into exactly the published pieces AND every piece reads as a number (the hyphen-separator trap, with its own red case), and `part_agreements` is measured. Twenty-seven records where the role named none | closed |
| **R-P4-51 — OPEN, and now VISIBLE** | a THREE-part column cannot honour its (1,2) pair — the pairing walk moves only the last position. Two-part columns are unaffected, which is why five reads did not meet it. It is not closed, but it no longer hides: G12.9 states that its window does not reach such a pair, and the twin's report names an unscored pair that missed as a DEVIATION with no closeness claimed for it, instead of dressing it as an approximation inside a window the method denies applying | L7 |

**THE REVIEW OF THE LANDING THAT CLOSED THREE OF THESE RETURNED A
REJECT (round P4-G3-R1, 2026-08-27), and every finding it made was
real.** Six were code and are fixed here; the two remaining were the
public documents saying the old state, corrected with them. What they
were is worth keeping, because four of the six were the same shape —
**two places computing one quantity, and only one of them changed**:

* the twin's report and the profiler each implemented the rank-
  agreement convention. They agreed on every column whose positions
  both varied and disagreed where one did not: the profiler answers
  `0.0`, the report answered "no number at all", so a twin that met the
  fact EXACTLY was told it had missed. The report now delegates;
* the validator's style check counted a cell into a position on its
  piece count alone, where the profiler requires every piece to read as
  a number. A real 2,000-row source with twenty `1.00/` cells profiles
  soundly and was then told it MISSED three style facts of its own
  description — the outcome R-P4-43's vacuity rule exists to prevent;
* the window `0.02` and the rounding of a published agreement were each
  written twice, and the two sides measured at different precisions, so
  `0.020018` was outside for one command and inside for the other. Both
  now come from one place, `parsing`, which is the module both sides
  may import;
* **two bounds cited method sections that did not exist.** The clock
  role's rung and distinctness envelopes cited `G12.9` from the day the
  role landed, when the method stopped at G12.8; once G12.9 was written
  for the JOINED role they began to resolve — to the wrong rule, which
  is worse than dangling, and ten lines of the demonstration quality
  report were sending readers to it. The kurtosis bound cited a
  `G12.3a` that was never written. All three sections now exist
  (G12.3a, G12.10, G12.11), and
  `tests/test_method_citations_resolve.py` refuses any citation naming
  a section the method does not define. **That guard immediately found
  a third one the reviewer had missed**: a comment claiming the
  histogram shapes the interpolated value, citing a `G5.4a` that does
  not exist, in code that reads no histogram at all.

**TWO ADVERSARIAL ROUNDS ON THIS WORK, BOTH REJECT, SEVENTEEN ITEMS,
ALL REAL.** Round 1's four-of-six pattern was one fact written in two
places. Round 2 found the SAME pattern four more times, three of them
in the repairs themselves:

* the decimal-comma swap ran before the measuring, so a correct twin's
  own report said it held 0 numeric cells against a published 200 and
  named 2 approximated facts where the same column undeclared names 15;
* the scored/unscored pair rule was fixed in the generator and not the
  validator, so the twin's report called a pair unscored while the
  quality report handed that same pair the window of the section that
  excludes it;
* the role test was written twice, said `NumericFacts` in both, and so
  dropped `numeric_unrepresentable` from a feature about how a number
  is spelled;
* a missed `part_above` reached the quality report and nothing else --
  measured, 12 of 12 three-position twins missed one and the twin's own
  report was silent on all 12.

**The rule that came out of it, and it is sharper than "put it in one
place".** Where an architectural boundary separates the two readers --
the validator may not import the generator -- the shared thing has to
move to a module BELOW both: `parsing.RANK_AGREEMENT_WINDOW`,
`contract.scored_pairs`, `contract.a_decimal_comma_reaches`. It feels
like putting a generation concern in the wrong file. Do it anyway.

**And a test shape worth reusing:** generate, validate, then assert the
two pages name the same facts. Every item above showed up as those two
disagreeing, and no single-page test saw any of them.

**Round 2 also caught a process fault worth keeping.** The new test
files were UNTRACKED, so the decontamination scanner -- which walks the
TRACKED tree -- had never read them, and the "clean" result could not
be credited. Adding them found a denied word in two. *Never report a
scanner clean on files the scanner does not walk.*

**ROUND 3 REJECTED THE REPAIRS AGAIN, and its sharpest item was that I
had WEAKENED A VERDICT.** To keep a three-position twin from missing
facts nothing aims at, I made the unscored pair's agreement and its
above-count AUTHORIZED-DEVIATIONs citing G12.9. That was wrong twice
over: G12.9 withholds the WINDOW, not the obligation, and
AUTHORIZED-DEVIATION is drawn from a registry of corners a ratified
plan or the owner authorizes, reached through `corners_of` -- emitting
it straight from the check bypassed that classifier. The reviewer's
witness settles it: describe 120 cells `r/r/1000` and check
`r/(121-r)/1000` against it, and every marginal value, width, style and
moment holds while the early pair is turned inside out. Under the
excusing rule that file passed every verdict-bearing obligation. It is
withdrawn: both are exact checks again, a three-position twin MISSES
them, and that is residual R-P4-51 appearing in the report, which is
where an open residual belongs.

**Round 3 also found that the swap had moved the defect onto the
HOLES.** A column whose missing spelling is `.` had its twenty absent
cells written as `,` -- 200 present cells against a published 180, the
role re-describing as `long_tail_labels`, seven obligations missed, and
the twin's own report silent because it recounts before the swap. The
swap now leaves every published `missing_by_source` spelling alone.

**And three of the tests written for round 2 could not go red.** Each
is rebuilt to call the thing it claims to protect: the role-name list
is held to the fact-type predicate column by column over a description
carrying every role; the walk's starting rule is pinned by REPLACING
`contract.scored_pairs` and watching the twin's cells move (on a forged
description, because sixty ordinary three-position columns were
measured and none put the two averaging rules on opposite sides of the
threshold); and the citation census is now derived by PARSING the
module with `ast` rather than by the same regex that reads the
citations. All three mutations the reviewer named now turn them red.

**ROUNDS 4 AND 5 REJECTED IT AGAIN; twenty-eight items across five
rounds and every one of them a real defect.** The two that matter most
to a reader of this page:

* **A generated value could be turned into a hole.** A column whose
  published "no value" word is `7,5`, values 7.0-7.9, generates present
  cells spelled `7.5`; the comma swap makes the two one spelling. The
  twin held 60 cells spelled `7,5` against a published 42 and its own
  report, recounting the cells from BEFORE the swap, called it correct.
  The generator now RECOUNTS the cells as written and MEASURES them as
  described -- the same split the profiler and the validator make --
  and `_recount_notes`, which had never covered presence at all, names
  the shortfall.
* **A declared missing value was read under the wrong grammar.**
  `--decimal-comma amount --missing-value 1,234` read the cells with
  the comma (1.234) and the declaration ordinarily (1234). The matching
  rule matches a number-shaped declaration BY NUMBER only, so every
  cell the person had explicitly called "no value" was counted as a
  measurement, and presence, ladder, moments and role all moved with
  them in silence.

**AND THE ROLE BOUNDARY IN R-P4-52 WAS FALSE.** The profiler swaps a
declared column's cells BEFORE it chooses a role, so `constant` and
`binary` -- chosen before the numeric roles -- are read with the comma
too. The tool was telling those columns' owners their numbers were
"NOT read" that way, about a description whose profiler had read
exactly that way, while the twin's own report claimed 0 numeric cells
against a published 60. There are two questions here and they now have
two names: `DECIMAL_COMMA_HONOURED_ROLES` (where the DESCRIPTION
differs) and `a_decimal_comma_reaches` (where the GENERATOR must spell
the numbers itself). A test asserts the second is inside the first.

**A repair of my own was caught by a golden digest**, and the sentence
that caught it is worth keeping: *a report that says less than it did
is a defect even when nothing crashed*. Narrowing the new presence
notes to unconditional holes, I returned early and took the
distinctness notes with me -- the demonstration report silently lost
two lines it had always carried.

**ROUND 6: EIGHT MORE, ALL REAL, AND THE FEATURE'S REAL SHAPE FINALLY
SHOWED.** Four of the eight were one thing said four ways: **a
per-column reading has to reach every place that reads a DECLARATION
as a number, and the value declarations are table-wide.**

* `--decimal-comma amount --keep-value -999,0` read the cells as the
  stand-in and the KEPT declaration under the ordinary grammar, where
  it is no number at all — so the outlier pass carried off forty cells
  the person had explicitly said to keep. The tally now carries the
  reading, as `_Cell` carries `numeric_text`, and the stand-in
  judgement and the calendar-placeholder pass both ask it.
* `--keep-value 1,234 --missing-value 1,2340` is one number on a
  declared column and two everywhere else. Tested under one grammar the
  pair looked innocent and was accepted, and the missing declaration
  then quietly defeated the keep declaration. The contradiction check
  now tests under both readings where either is in play.
* the described-domain view translated HOLES too, so a hole spelled
  `-9,99` became `-999`, read as a number, and the twin's own report
  claimed 200 numeric cells against a published 180 with eleven false
  deviations after it — moments and rungs computed over twenty values
  the column does not have. Its CELLS were right the whole time.
* the presence guard was column-wide, so one judged `-999` silenced a
  genuine collision on an unconditional `7,5` in the same column. It is
  per SPELLING now, because the two cases point the same way and only
  the spelling tells them apart.

**R-P4-54 IS CLOSED BY A REFUSAL, and the paragraph that stood here
claiming it could be left open was refuted in the next round.** I had
written that the consequence was conservative — obligations withheld,
never a wrong verdict. That covered one direction only. Declare `1,234`
and `1234` as missing beside a declared column: the ordinary grammar
folds them into one and the comma grammar keeps them apart, the
table-wide recovery looks complete, the column stays checkable, and the
SOURCE FILE is then told it missed presence, role and its numbers
against a description correct about all three. So a declared value
whose number depends on the grammar is now REFUSED beside
`--decimal-comma`. The loader cannot restate that refusal in full: the
SETTINGS BLOCK carries no spelling of the person's own, only how many
values were declared and which of this package's own words were among
them (C5-16). A spelling the person typed does reach the description
where a column publishes it among its absent cells and the floor
allows — so a partial check is possible and is NOT built, because it
would have to tell a declared hole from a judged one and a wrong
refusal there costs more than the gap. The command line is the gate; a
comment sits where the invariant would.

**Two documents had also outgrown the code** and are corrected: the
plan and the contract still named three honoured roles when the
profiler honours five, and the method said an unscored pair was "held
to nothing at all" three lines before calling its difference a plain
MISS — one reads as no obligation, the other as an obligation, and an
implementer following the first would recreate the verdict weakening
round 3 withdrew.

**ROUND 8, THE LAST AUTHORIZED ONE: three items, all real.**

* **`_recounted` was still asking the old question.** A comment beside
  `_wears_this_hole` claimed three callers shared one identity and only
  two of them did — I wrote the claim without checking the third. On a
  declared column publishing the hole `-999`, a present cell written
  `-999,0` was counted PRESENT by the recount and ABSENT by a
  re-description; the collision was detected, the recount was
  unchanged, and the presence lines — which need both — stayed silent.
* **The R-P4-54 refusal was CLI-only.** `build_document` is a public
  entry point and accepted the pair, so the wrong verdicts were one
  call away for anybody not going through the command line. The
  refusal now sits at the producer.
* **The refusal's own test could not detect the refusal's removal** —
  it called only the message formatter. The same non-red shape earlier
  rounds rejected, written by me again.

**THREE THINGS ABOUT MY OWN WORK IN THIS ROUND, kept because they are
the useful part.** I built the loader invariant S8b, and my own test
for something else then refused a CORRECT description with it: a SAFE
declaration (`--missing-value -999`) matches a cell spelled `-999,0` by
NUMBER on a declared column, so an ambiguous hole spelling has a third
source I had not thought of, and the document cannot tell the three
apart. S8b is withdrawn with that witness written where it stood. I
also added a built-in-missing-word shortcut to the shared hole
identity, which broke a `--keep-value` rescue — the helper beside it
warns against exactly that in its own docstring, and I wrote past it;
an existing test caught it. And my first witness for the recount fix
did not discriminate, because the colliding cell had the SAME TEXT as
the hole: both identities match there. The fixture now makes the two
spellings differ while the numbers agree, and the mutation turns it
red.

**Where this landing stands.** Eight adversarial rounds, forty-five
items, every one a real defect. What ended the structural problem was
not another repair but NARROWING what the feature accepts: a declared
value whose number depends on the grammar is refused beside
`--decimal-comma`. The reviewer had been pointing at that for two
rounds before I took it.

## THE FINER LADDER AND ITS ALLOTMENT — LANDED, AND GREEN

**The suite is GREEN. 4063 passed, 51 skipped, nothing red.** The five
goldens were held red for the whole landing and are re-recorded, after
the whole golden run was built at the commit BEFORE this branch and
again at its head and the two censuses compared obligation by
obligation: 407 checks both, none lost; 129 listings against 138, NONE
LOST and nine gained; and two facts moved WITHIN-BOUND to HELD, which
is the twin landing exactly on a published rung where it used to land
only inside the rung's bound.

**Eight adversarial rounds, every item of all eight real, not one a
wording item.** What they found and what closed it is below; the
register at the foot of `docs/plans/phase-4-columns.md` carries each
one with its reproduction.

**WHAT IS STILL OPEN, and none of it is from this branch:** R-P4-56,
R-P4-58, R-P4-59, R-P4-60 and R-P4-61. The eighth round was asked which
matters most of everything it had seen and named **R-P4-56** -- a twin
writing fixed-width cells wider than any source cell, which breaks
analysis code developed against it. Start there.

## THE FINER LADDER AND ITS ALLOTMENT — HOW IT WENT

**Branch `phase-4-allotment`. The suite is RED on purpose, and the red
is the point.** The owner ruled on 2026-08-28 that statistical fidelity
is the priority, which answers R-P4-49: the hundred-and-one-rung ladder
goes in, and `numeric_styles` may become approximate to pay for it.

The ladder is merged onto the decimal-comma landing and the merge's own
fallout is repaired — the frozen vectors outgrew the fixture-size cap
(raised, with the reason written where the number is), the two new
facts had no plain-language name in the not-checkable census, three red
cases named perturbations that no longer make their check miss, and an
internal check raised a built-in the offline audit cannot trace.

**FOUR TESTS FAILED WHEN THE LADDER WENT IN ALONE, and every one was
the symptom R-P4-49 names.** The plan predicted it in as many words:
the finer ladder helps a column whose values are SPREAD and hurts one
whose values are heavily REPEATED, because it places the twin on the
column's real plateaus while `G5.2` still shared the cells out by an
EVEN SPLIT.

**THE ALLOTMENT IS NOW BUILT AND SPECIFIED**, as method **G5.2a** (how
a band's cells divide) and **G5.2b** (how many strata each band gets).
The sizes are the lengths of the ladder's plateaus at the band's ranks;
the share of strata between the sign bands follows how many VALUES the
ladder gives each band rather than how many CELLS. Measured on the
witnesses that drove it:

* a long-tail code column: **211 of 230** cells correctly shaped under
  the even split, **229** under this;
* the crowded family: every named style count now written, where one
  column wrote 28 point-free cells against a published 38;
* a flat-ladder column: the twin comes out **exact** — 4×30, 9.5×10,
  12.5×8, the real column cell for cell.

`test_p2c5f3_style_reach` and `test_p3v7f2_corner_parity` pass.
`test_p4d18_shape_forms` is at 239 of 240 — one cell wears a
manufactured spelling. The fourteen frozen vectors all bind
again, `numeric_decimal_styles` included, after R-P4-55 below.

**THE MERGE RULE TOOK FOUR TRIES AND EACH WAS MEASURED**, which is why
G5.2a states all three parts of its key and what each one costs when
dropped. Merging by smallest PAIR joins two interpolation artifacts and
loses a real value; by nearest VALUE walks a whole number into the
fraction below it and leaves a published `plain` count unwritable;
absorbing the smallest run alone merged a plateau of thirteen cells
into one of four.

**AND THE ORACLE HAS ALREADY EARNED ITS KEEP: R-P4-55.** The vector
`numeric_decimal_styles` disagreed after the allotment landed, and the
disagreement was ten cells that differed only in the CASE of their
exponent — same values, same places, same style counts, same folded
identities. It was not a wobble. `_style_strata`, the exception that
packs styles over whole strata where the cell walk would overspend the
column's spellings, counted the RAW supply and compared it against the
FOLDED ceiling. Those are two quantities: `1e+15` and `1E+15` are two
raw spellings of one folded identity, and G6.5 names that pair as the
only way a numeric column can hold a raw count above a folded one. So
the guard fired on exactly the columns the pair exists for and packed
it away, leaving the twin one raw spelling short of a published
`n_distinct` it could have met — one published count bought with
another, which is what that exception exists to prevent.

Measured end to end over 140 built columns and 420 column-seeds, with
the two guards side by side
(`tools/measurements/r_p4_55_case_pair.py` -- every measured number on
this page now has a driver in that directory): they disagree on 9, the new one is closer
to the published counts on 9, and further on none. 29 of the 140 columns
publish a raw count above their folded one; 3 of those tripped the
defect. The reach is narrow and the direction is one-way. It needs a
source column that wrote one number with both an upper-case and a
lower-case exponent, which is why no check over published facts alone
would have caught it — both twins met every count the description
names. **Only a second implementation of the same text could separate
them**, and that is the whole argument for the oracle.

The defect is older than the allotment; the allotment is what reached
it. This column now has 21 distinct values where the even split gave
20, which took the raw supply from 23 past a ceiling of 23 that was
never the right ceiling.

**WHAT IS STILL OWED HERE.** The independent oracle is being rebuilt
FROM THE SPECIFICATION ALONE — the charter asks for the spec before the
implementation and this went the other way round, so the oracle is the
only thing that can still catch a method text that says something
different from what the code does. The five goldens are untouched
and must stay so until the above settles.

**THE FIRST ADVERSARIAL ROUND ON THIS LANDING RETURNED REJECT WITH
FOUR ITEMS, AND ALL FOUR WERE REAL** (P4-G6-R1, in the register). Two
were overflows in arithmetic I had already written a paragraph about,
and in one case the paragraph was written by the repair that MOVED the
overflow instead of removing it: G5.2a divides before it subtracts so
the numerator cannot overflow, and its DIVISOR then overflowed on two
large rungs of one sign, tying every gap at zero and handing the choice
back to iteration order. The other put an infinity inside the validator
on a description holding nothing but finite numbers, because
`_ladder_at` said "the convex form" and computed the difference form
the generator's own docstring rules out. Both are repaired with a red
case each; the third item corrected an overstatement in R-P4-55's own
comment and the fourth corrected this page. The rule that keeps
earning: a claim about floating point is worth what it was RUN on, not
what was argued for it.

**EIGHT REVIEW ROUNDS, EVERY ITEM OF ALL EIGHT REAL, AND NOT ONE
WORDING ITEM.** The eighth was the last under the cap a machinery
correction gets, and it was asked three questions besides its items,
because seven rounds had each found something written confidently and
wrongly and this page is what a new reader will trust.

**IT AUDITED THE REGISTER AND FOUND TWO CLAIMS THAT OUTRAN THE CODE,
both mine.** The double step round 7 said it had caught was caught in
ONE of the two places it lived. And the `math.nextafter` coverage cited
there -- 400024 steps -- came from a console run and not from the
committed test, which held 20018 values. The test holds 200018 now and
ASSERTS ITS OWN SIZE, so the figure is one the file can be made to
produce: 800072 comparisons across both module copies. **A coverage
claim is worth what the committed code does, not what was measured
once at a prompt.**

**WHAT THE ROUND SAYS IS LEFT, recorded because it is not my judgement
alone.** It says this landing is NOT safe to stop on while R-P4-58 and
R-P4-59 omit published facts from a report and R-P4-60 can pass a file
that misses an exact obligation. All three are deliberately opened
rather than fixed, each being a different role's landing. And it names
**R-P4-56 as the highest-value work left of everything it saw across
eight rounds**, on the ground that a twin writing fixed-width cells
wider than any source cell breaks analysis code developed against it --
worse than two reports disagreeing in their last digits. That is the
same conclusion this page reached independently, from the other side.

**SEVEN ROUNDS BEFORE THAT, EVERY ITEM REAL.** Round 7 found that the outward step round 6 introduced
was not a step to the ADJACENT number -- and I had written it while
fixing round 6's own bound. The gap below a value on the edge of its
binade is HALF the gap above it, so it stepped two places there; the
gap it computed for a subnormal underflows, so no subnormal moved at
all, which is exactly the case a one-place widening exists for; and the
largest number the format holds raised `OverflowError`. It is checked
against `math.nextafter` over 400024 steps now, in `tests/`, which is
where a hand-rolled stand-in for a call the offline audit forbids
belongs.

Round 7 also found the joined agreement window rounding inward the same
way, and that the ratified METHOD had not been amended for any of the
widening -- blocking on its own under the reviewer brief. Both closed.

**AND ITS FOURTH ITEM WAS MEASURED RATHER THAN GUESSED AT.** The
generator and the validator print different moment windows for one
column, so one run of `generate` beside `validate` states two numerical
versions of
one method. Nine windows built at the commit BEFORE this branch and
again at its head: 8 of 9 differed before, 7 of 9 differ now. It is
pre-existing, this landing improved it slightly, and closing it means
stating the window's arithmetic operation by operation in the method
and making both implementations follow that text. Opened as R-P4-61.

**SIX ROUNDS BEFORE THAT, EVERY ITEM REAL.** Round 6 found the worst report defect of the landing: a bound
stated as a limit that did not ADMIT the limit. The largest skew a
sample of three values can take is one over the square root of two,
whose correctly rounded value is 0.7071067811865476; computed as
written it comes out one place INSIDE, so a column whose skew IS the
maximum fell outside a bound it exactly meets. On the three cells
`-1e20`, `0` and `1` the description publishes -0.7071067811865476, the
twin holds -0.7071067811865476, and the report said OUTSIDE and told
the reader to treat an exactly reproduced fact as not reproduced.
**Every other round closed a report that said less than it should; this
one said something FALSE about a correct twin.** The exact moments of
round 5 are what exposed it -- the recount they replaced never produced
a value that landed on the limit.

Every universal limit is widened one place OUTWARD now, in both
modules. Outward and NOT away from zero: the tail weight's two ends are
both positive, and the first attempt moved its low end away from zero,
which moved it UP past the value the window was drawn to admit. An
existing kurtosis test caught that inside a minute.

Round 6's other item was about a measurement driver committed so that a
claim could be re-derived: its header said it counted the two verdicts
the report shows a reader and its loop read neither, and its comparator
was a paraphrase of the predecessor rather than the predecessor. Both
corrected; 600 verdicts compared, none flips. **A tool that exists to
make claims checkable is held to the standard it was built to
enforce.**

**FIVE ROUNDS BEFORE THAT, EVERY ITEM REAL.** Round 5 found that the round-4 repair answered two column
shapes and not the third and fourth: the scaled root UNDERFLOWS on four
zeroes beside one `5e-324`, and `value - mean` OVERFLOWS before the
scaling can reach it on one value at the bottom of the range beside a
hundred and nineteen near the top.

**Four rounds of chasing that expression is what was wrong.**
`generation._moments_of` now asks `taxonomy.moments_of`, the same exact
whole-number computation the description's own numbers come from. It
forms neither the square nor the difference, so there is no column
shape left for it to be wrong on -- and the number printed beside the
published one is the correctly rounded value of the SAME statistic
rather than a second approximation of it, which is what a report
putting two numbers side by side was always claiming.

The profile/generator boundary was CHECKED rather than assumed: what
the charter forbids is a module that opens a table being in the
generator's import graph, and `taxonomy` imports `math` and `parsing`
and reads no file.

**AND ROUND 5 FOUND THREE PRE-EXISTING GAPS OF THE SAME SHAPE IN OTHER
ROLES**, opened as R-P4-58, R-P4-59 and R-P4-60 and NOT fixed here
because each is a different role's landing: a joined column's positions
carry a full quantitative block nothing checks and nothing lists; a
`numeric_unrepresentable` column publishes two widths that are neither
checked nor listed; and `missing_by_source` is filed report-only by the
validator while the disposition registry calls it EXACT-OBSERVABLE, so
a file that drops a required missing spelling passes with no miss. Read
the register before starting any of them.

**FOUR REVIEW ROUNDS BEFORE THAT, TWELVE SITES.** Rounds
1, 2, 3 and 4 each returned REJECT and every item of all four was real.

**Round 4 corrected a conclusion round 3 let me record, and that is the
single most useful thing on this page.** I reported that a site round 3
named in the GENERATOR did not reproduce, having tried seven column
shapes and searched both reports for a word that is not a number. It
does reproduce, and its symptom is SILENCE: `_moments_of` multiplied
before it divided, the variance of a column whose deviation is an
ordinary 8.5e307 is 7.2e615, and the function returned None for the
spread, the shape and the tails. The twin report files an approximation
only where the value is not None, so three published obligations were
simply ABSENT. Nothing printed, so nothing for the scanner to find.
Repairing it then UNMASKED the infinity round 3 had predicted in the
same function. **A defect can be hidden behind another defect, and "I
could not reproduce it" is only as good as the rest of the system.**

Then the assertion added for that item -- every moment the description
publishes is named somewhere -- went red on a SUBNORMAL column, which
no round had found: a deviation near the smallest number this format
holds, squared, IS zero. Three rounds looked at a square with nowhere
to go and this is the same expression at the other end of the range.

**AND THE LESSON ABOUT WHERE A GUARD BELONGS.** Rounds 1, 2 and 3 each returned REJECT and every item
was real. Rounds 1 and 2 each guarded the INPUTS to a computation and
round 3 found the overflow one step further along -- in the widening
factor, after the scaled displacement had come out finite. The guard is
now at the point a window is FILED, not at its inputs: one function
that records a window where both ends are numbers and withholds it
otherwise. A guard on the products of an expression covers one
expression; a guard where the result is recorded covers every product,
including the ones nobody has written yet. Two of the ten sites were
found by searching for the siblings of a named one, and one was a
composition I had written myself -- `_filled_rungs(_merged_rungs(...))`,
two functions that both document returning None, joined without a guard,
which took `synthtwin generate` down with a `TypeError` on a
description the loader accepts.

Round 3 also found the kurtosis missing from the census a SECOND time,
on a different path, because both listings were built from a typed-out
list of field names. They read the moments off what the description
PUBLISHES now, so a fact cannot go missing by not being typed.

And it found that round 2's withholding filed those facts under a
sentence that is FALSE -- "describing this file would not publish what
this check measures", of a file whose description publishes all four
moments. What is missing is the window, not the fact. They are
not-checkable census lines now, with a reason that is true.

**One claim of round 3 did NOT reproduce and is recorded as such**: the
same multiplication in the GENERATOR, tried against seven column
shapes, never printed an infinity, because its reach is bounded by the
ladder's rank windows rather than by the column's range. No unwitnessed
guard was added there -- silently dropping a fact from a report is the
very defect class two of these rounds found. A DETECTOR was added
instead, over both reports.

**AND SEARCHING FOR AN EARLIER ROUND'S SIBLINGS FOUND THE WORST DEFECT
OF THE DAY: `synthtwin validate` CRASHED** (R-P4-57 -- and round 2 then
found that the first repair for it had MOVED the crash rather than
removed it, which is P4-G6-R2 in the register and the reason the
repair is now an eight-shape BATTERY and not another guard). Sixty ordinary
readings between 1e280 and 1e300 in one column. `synthtwin profile`
wrote a description with a finite spread; `synthtwin generate` wrote a
twin; `synthtwin validate` came out as an `OverflowError` traceback
naming internal functions. `_sample_deviation` is described as "the
standard deviation the profiler's own formula computes" and computed
`sum((x - mean) ** 2)` in binary64 instead -- a second implementation
of a published statistic, on a table nothing was wrong with.

Under the crash was a quieter one: the spread the moment windows are
drawn from came out an infinity, so the standard-deviation window was
`(0, inf)` -- a bound every twin ever written satisfies, reported HELD
with no word about having gone quiet. That is a FALSE PASS and not a
conservative one, and the three windows are now withheld in words
where the spread cannot be held.

**Four sites, one family, and its first member was fixed months ago.**
The tail-weight window already carries the rule -- divide each
deviation by the spread BEFORE raising it -- with the item number that
found it. The rule was applied where that round pointed and at none of
its siblings. **Where a review names a site, search for the siblings**
is the standing lesson of this project and it paid again: the round
named four items and the fifth, found by looking, was the only one
that took a shipped command down.

**AND THE THREE VACUOUS MUTATION TESTS ARE ANSWERED — ALL THREE
REPAIRS ARE ALIVE.** They looked dead because each was redundant on
its own witness after the allotment moved the strata. "Redundant on
its witness" is not "dead everywhere", so each was measured before
anything was touched, and nothing was deleted:

* `_whole_inside`'s share walk. On the old fixture it was called ZERO
  times across 19 seeds. Its new witness — `1.5`×6, `8.5`×7, `9`×15 —
  calls it 18 times across those seeds, and every call returns `8.0`
  with the walk and nothing without it. The twin writes its published
  15 plain cells at all 19 seeds; mutated it writes 14 at 18 of them.
* `_carrier_bands`' band step. The old 58-cell column gave its
  negatives two strata outright under the new share, so the step had
  nothing to fetch. Its new witness is 33 cells whose ladder reads the
  negative band as 3 plateaus against the positive band's 8, so the
  share rounds that side down to ONE stratum — the pinned `min` of
  `-20.5`, which carries a point and can wear no point-free form. The
  step is entered at (1, 4) and returns (2, 3). Unmutated the twin
  writes its published 12 `leading_zero` and 20 `plain` exactly;
  neutralised it writes 7 and 15.
* `_held_later`'s bar. The strongest of the three, and the one that
  shows why none of them could be deleted on a single witness: over
  600 producer columns at six seeds the bar is consulted 399 times and
  decides the answer 247 times, across 58 different columns — about
  one column in ten. The old fixture reached it not once, because the
  allotment made the contended whole number land INSIDE the earlier
  stratum's own share, where the stratum has the older claim and the
  bar is never asked. The whole 20-case battery had drifted the same
  way: one call, no decision.

The lesson is the one already written above the measurement rules: a
test that stops failing when its repair is removed has told you
something about the TEST, and only a measurement over many columns can
say which.

## What is broken right now

- **LINT IS NOT CLEAN: ten errors stand** (`ruff check .` under the
  pinned rule set, measured 2026-08-31 at `c10f5f6` with a throwaway
  stash, so the count is the tree's and not this landing's). Two are
  in `src/` -- a mid-file import in `generation.py`, and in
  `validation.py` a mid-file import plus a dead `mine =
  _position_cells(...)` at line 7438 that residual R-P4-58's drafting
  left behind. Seven are in `tools/measurements/`. **The dead recount
  is measured BENIGN rather than a wrong population**: the joined
  ladder and moment checks read the profiler's re-description, not a
  recount there. It goes with the joined role's own landing.

  This page said lint was CLEAN until 2026-08-31, which is the same
  defect as the commit messages below: a green claim about a check
  that was not run on the tree being described.
- **CI ran again after 86 commits.** `pyproject.toml` pins the ruff
  rule set (the 183 errors that stood before it were 120 quoted type
  annotations, a deliberate style here, plus tooling import order). When it did, all three of its failures were checks that had
  outlived their rules -- a column count, a suppressed-level count and
  an inverted membership test -- and not product defects. The lesson
  worth keeping: **no commit message may claim "every check clean"
  unless the checks actually ran on the STAGED tree**, because the
  scanners walk the tracked tree and will silently skip a file you have
  not added yet.
- **R-P4-56 — CLOSED for a fixed-width column, 2026-08-30, and
  NARROWED to columns whose width census names several widths.** It was
  the most serious thing open here and it is built: where two strata
  would be written as one cell at the column's published width, the
  later moves to the nearest free point of that width's own grid,
  inside its own share of the ladder. Measured over 90 fixed-width
  columns: cells wider before the point than any source cell go from
  200 to 0, deviations the twin files against itself from 53 to 1, and
  the count of different numbers is closer to the published one on 45
  columns and further on none. The original defect, restated for the
  next reader:
  A numeric column with a PINNED fraction width -- a code column, a
  rounded measurement -- can get two strata that hold different
  numbers but round onto one spelling. The count of different values
  then comes out short, which the twin's report NAMES, and the
  leading-zero raise supplies the missing spelling by writing one
  number a second way, which nothing reports. Measured over two
  families of 80 columns: 13 of 80 grid-spaced columns collide and 12
  of those write an integer field wider than any source cell's, the
  worst being seven figures where the source had four; 0 of 80
  ordinary full-precision columns do. A person parsing a fixed-width
  code column against the twin gets a cell their code cannot read, and
  is not told. The repair is written down in the register: step a
  colliding stratum to the next free point on the published width's
  own grid, inside its own share. Not built during the allotment
  landing because it is the same surface.
- The open defects of Phase 4 are the residual register at the foot of
  `docs/plans/phase-4-columns.md`. The 2026-08-26 triage sorted them:
  15 deliberate scope declines, 11 real landings, 7 owner questions.

**ROUND 5, THE LAST AUTHORIZED ONE, RETURNED SIX CONTROL GAPS AND NO
WORDING ITEMS -- AND SAID THE NARROW DEFECT IS HONESTLY CLOSED.** Both
matrix readers derive the governing contract from
`contract.PROFILE_VERSION`, and so does the claim inventory's positive
guard, so R-P4-25 itself is shut. What the round found was the
STRENGTH of the guards around it. Three were surfaces this landing
wrote and are fixed here; three are older controls and are recorded as
R-P4-64, R-P4-65 and R-P4-66 rather than done in passing.

* **The closed syntax protected the CELLS and left the PROSE open.** A
  sentence in the sub-table's head paragraph reaches every row below
  it -- "For affixed cores, `mean` need only be mentioned in the
  report" -- and it names no class, so neither the disposition guard
  nor the lowering scan could see it. That is round 4's attack moved
  one paragraph up, which is the fifth time this one surface has been
  beaten. **The region is pinned WHOLE by its digest now**, prose and
  table together, so changing it is a deliberate act with a counted
  difference. Two mutations verify it.
* **Residual state was inferred from a blacklist, and "FIXED" is not a
  word anybody had listed.** The heading must now SAY `— OPEN`; a
  positive token cannot be defeated by reaching for another word.
* **The name and region tests were not exact.** `R-P4-62-a`,
  `R-P4-62.1` and `R-P4-62_extra` all answered for `R-P4-62`, and an
  earlier duplicate `## P4-D13. Residuals` section would have shadowed
  the real register. The identifier grammar is declared, and exactly
  one anchored register heading is required. Five mutations verify
  both.

**FIVE ROUNDS, TWENTY-THREE ITEMS, EVERY ONE A CONTROL GAP AND NOT ONE
A WORDING ITEM.** The cap is five for governance machinery, so this
landing stops here with three residuals carried by name rather than by
omission. The pattern is the thing to carry forward: **one surface was
beaten five times, each time by a subtler sentence, and every repair
that tried to read the sentence more cleverly was beaten by the next
one.** What finally held was refusing to parse: a cell that must equal
a fixed string, a state that must be asserted rather than inferred, a
region pinned by digest.

**AND THE SUITE-SIZE GUARD CAUGHT ME DELETING A TEST.** Repairing
round 3's residual check, I cut a region of a test file by index
arithmetic -- find the start, find a marker, jump past it, cut to the
next newline -- and the jump swallowed the whole of
`test_the_phase_cannot_close_while_the_seal_is_paused`, the control
that stops this phase closing while the disposition seal is paused. No
test failed, because the deleted test was the one that would have.
Only `test_the_state_page_states_the_suite_size_it_was_written_against`
noticed, by counting: 4,133 written on this page, 4,132 collected.

It is restored, and the lesson is not "be careful with slicing". It is
that **the only control that can see a deleted control is one that
counts them**, and this repository has exactly one. Prefer replacing a
NAMED, ANCHORED block over cutting between computed offsets, and read
the collected count after any edit that removes lines.

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
- **A GIT WORKTREE HAS NO `.venv`, AND BORROWING THE SHARED ONE TESTS
  THE WRONG SOURCE.** The checkout's venv installs this package
  EDITABLE from its own `src`, so a worktree that reaches for
  `../../.venv/bin/python` imports the product code of the SHARED
  checkout while the tests, the contract and the plan come from the
  worktree. Nothing announces it. Measured on 2026-08-31: a landing
  that adds a note form ran green for its author and the note-grammar
  guard then reported `clause 0, appendix 0, producer None` for
  somebody else -- the guard was reading the worktree's contract and
  comparing it against the shared checkout's `NOTE_ARITY`, and the
  same seventy tests went 60/10 for one runner and 70/0 for the other.
  Give the worktree a `.venv` of its own whose `bin/python` exports
  `PYTHONPATH=<this worktree>/src` -- not an env var remembered at the
  call site, because the next person will not know to set it.
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
5. **The mode**, for columns where one value dominates. **PUBLISHED
   2026-08-27 (plan P4-D4.11), REPORT-ONLY until the generator carves
   its stratum.**

Design notes — bin edges must be chosen by a reproducible RULE since
the generator has only the description; bin counts fall under the
small-cell floor while percentiles are exact real values and do not;
and the generator must MEET the histogram rather than draw from the
ladder and hope. Fuller notes in the assistant's memory under
`numeric-depth-revisit`. Build beside the distinct-count and width
work, which touch the same machinery.

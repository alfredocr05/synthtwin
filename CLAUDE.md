# CLAUDE.md - synthtwin implementer brief

This is the canonical brief for the implementing agent. It lives in the
repository and replaces the earlier private parent-folder brief.
Historical note: the project's working name changed to `synthtwin` before
the first commit, after the original name was found taken on PyPI; older
private planning documents may use the previous name.

## The goal

Researchers who hold sensitive tabular data cannot paste it into an AI
assistant, and often cannot move it off a compliant machine at all.
synthtwin gives them a synthetic twin of their table: the same columns,
the same types, and the same published behaviour of each column on its
own - the same distributions, the same counts, the same amount of
missing data column by column - built from a description of that table
rather than from its rows. They develop their analysis with AI
assistance on the twin, freely and quickly, then run the finished code
on the real data inside their compliant environment.

**What the twin carries today, stated before any other sentence claims
more.** The twin reproduces the facts the profile publishes about each
column ON ITS OWN. It carries no cross-column structure at all: no
correlation between two columns, no formula tying one column to
another, no shared pattern of which cells are empty, and no ordering
between two event columns. Rows are treated as independent and the
grain is undescribed - the profile never says what one row of the real
table is - so the twin of a repeated-measures table misdescribes the
subject-level truth even where every column of it is right on its own.
Cross-column structure arrives in a later phase (Phase 5). Until it
does, no sentence in this repository may say or imply that the twin
preserves it.

What the goal sentence may and may not claim about rows is fixed under
"Honest limits" below: it is a claim about where the twin's values come
from, not a promise that no twin row can equal a real one.

## The six principles

1. **Open source by commitment; open by default in the code.** There is
   no private core: every line of the product lives in this repository,
   and nothing here depends on anything a contributor cannot see. The
   repository goes public at Phase 3's visibility flip - the owner
   decision recorded in the Phase 3 plan, executed the moment that plan
   landed - so every line IS read by strangers; write it that way. The
   controls that required a public repository are applied at the flip
   and recorded in SECURITY.md's activation record.
2. **Zero-code UX.** A researcher who has never programmed can run the
   whole workflow. No configuration files to hand-write, no flags that
   require reading source, and every message written for a human.
3. **Secure by architecture, fully offline.** The product code contains
   no construct that initiates network I/O, no subprocess execution, no
   native-code calls, no dynamic code loading; it accepts only local
   filesystem paths and is fully functional air-gapped. This is enforced
   by the layered checks in the Phase 0 plan (D6), not merely promised.
4. **Decontaminated.** No trace of the private prototype study's
   vocabulary, enforced by the hashed decontamination manifest in
   `tools/decontamination` and the process in the Phase 0 plan. Do not
   enumerate, hint at, or paraphrase the private vocabulary anywhere -
   in code, comments, tests, docs, commit messages, or branch names. If
   the scanner flags text you wrote, change the text; never change the
   scanner to make it pass.
5. **Comprehensive column handling.** Every column in the user's table
   is either handled correctly by an appropriate type path or declined
   with a plain-language explanation. Columns are never silently
   dropped, silently miscast, or silently approximated.
6. **Statistical fidelity is the product, and so is an honest account
   of its bounds.** The twin is only worth using if code developed
   against it runs unchanged and meaningfully on the real table. A twin
   that misstates what it carries fails the product's one job even when
   nothing crashes - and a sentence claiming more than the built phase
   carries fails it the same way, because the reader acts on the
   sentence. What each phase carries is stated plainly, and what it
   does not carry is stated beside it.

## The outputs, and which of them exist today

Built now, by the three commands that exist:

1. **The synthetic twin table** - same shape and the same published
   behaviour column by column, every cell derived from the profile and
   the seed rather than taken from the table. Written by
   `synthtwin generate`.
2. **The schema description** - columns, detected types, and how each
   was handled: the profile document itself and the plain-language
   summary beside it. Written by `synthtwin profile`.
3. **The generation report** - written beside every twin, saying which
   published facts the twin holds exactly, which it holds only
   approximately with the achieved value printed beside the published
   one, and which it does not hold at all. It passes no verdict of its
   own and says so, and it ends by teaching the command that produces
   one.
4. **The plain-language quality report** - written by `synthtwin
   validate`, which reads the profile and one CSV file, describes that
   file again with the profiler's own producer, and reports which of
   the profile's obligations the file meets, which it misses, and which
   nothing written in a CSV can evidence either way. A passing report
   means exactly one thing - no checkable obligation was missed - with
   the within-window, authorized-deviation, withheld and not-checkable
   counts standing beside it and never folded into it. It is not a
   fitness verdict for any analysis, it validates nothing the profile
   does not publish, and it cannot tell a synthetic file from a real
   one.

Not built. This is named here as roadmap and is never written about as
though it existed:

5. **The relationship summary** - which columns move together, and what
   a twin would then have to do about it. None of it exists: the
   profile's relationship manifest is eight reserved slots, every one
   empty, and the loader refuses a profile that fills any of them. It
   arrives with Phase 5. Nothing the quality report checks is a
   cross-column fact, because the profile publishes none.

## Honest limits

- Numbers computed on the twin are not scientific results. The twin is
  for developing code; conclusions come from running that code on the
  real data.
- Fidelity is bounded, and today the bound is one column wide. What is
  preserved is what the profile publishes about each column on its own.
  No cross-column structure is preserved at all - not a correlation,
  not a formula between two columns, not a shared pattern of empty
  cells, not the order of two event dates - and rows are treated as
  independent while the grain is undescribed, so a table holding
  several rows per subject yields a twin that misdescribes the
  subject-level truth. Cross-column structure arrives in a later phase
  (Phase 5). Structure that was never modeled is never guaranteed.
- **The record claim is a claim about provenance, and it is qualified**
  (plan P2-D11). Generation reads no source table and samples or copies
  no row of one: every twin cell is derived from the profile and the
  seed. That says where the twin's values come from. It does not say
  that no twin row can equal a real one, and any wording that says so is
  a defect in this repository, not a nuance. Allocating published counts
  exactly can force a twin row to match a real one: an 11-row
  single-column table whose one label clears the disclosure floor
  publishes that label with the count 11, so the twin holds it in all 11
  rows, and each of those rows is a row the real table has. Nothing was
  copied; the arithmetic left no other answer. The categorical form of
  this claim is retired everywhere, and a test asserts its absence on
  every public surface.
- synthtwin is not a formal privacy mechanism, claims no
  differential-privacy property, and offers no formal privacy guarantee.
  All five files a full run leaves behind - the profile, the
  plain-language summary beside it, the twin, the twin's report and the
  quality report - carry facts computed from real data, so the
  institution's rules for real-derived material apply to all five, never
  to the profile alone. The summary is counted in as a file of its own
  (plan amendment A-P3-8) because that is how a person meets it: it is
  printed on the screen and written beside the profile, it repeats the
  real labels the profile publishes, and a rule that named four files
  told a reader by omission that the fifth was free to travel.
- The offline guarantee is a property of the code, verified by source
  audit and scans - it is not an OS-level sandbox. Institutions that
  require enforcement run the tool inside their own network-isolated
  environment.
- **What the quality report withholds is a rule about ONE report, and
  it is not a barrier against somebody who re-runs the check** (owner
  ruling 2026-08-14, plan amendment A-P3-13, validation method V5-A1).
  A number `synthtwin validate` withholds is a number it does not
  print - not in the report, not on the screen, not in a message that
  stops the command - so one report can be handed to a person holding
  no file at all, and that is what the rule buys. It is not a defence
  against a person who HAS the checked file and runs the check again
  and again with descriptions of their own, watching which verdicts
  move: such a person can narrow a number one report withholds, and
  synthtwin does not try to stop them, because running this check on a
  file requires holding that file. Claiming the wider guarantee - in
  any wording, on any surface here, including a comment that gives it
  as a reason for a rule that has another one - is a defect and not a
  nuance, and the claim inventory in `tests/test_claim_inventory.py`
  turns the suite red on it.

## Rules of the road

- **The profile/generator boundary.** The generator never reads a
  table at all - it consumes only the profile file, and the module that
  opens a CSV is not in its import graph at any instant. Two code paths
  DO open a CSV, and stating it at that width is owner decision 6 of
  the Phase 3 plan: the profiler reads the user's real table, and the
  validator reads the one file it was asked to check, because measuring
  a file means describing it with the profiler's own producer. The
  validator in turn never imports the generator, so its verdicts cannot
  inherit the planner's own defects and synthtwin's own random number
  generator is out of its reach. It does NOT follow that no random
  source is in the process, and this brief said otherwise for a while
  and was wrong: the validator reads a file, so it loads pandas, so it
  loads `numpy.random`. What is enforced is that no synthtwin module on
  the validate path imports a random source and that a validate run
  draws from none (plan amendment A-P3-4). No debugging convenience,
  test helper, or one-time exception crosses any of those lines, ever.
- **Determinism.** One RNG, created once from the user's seed, threaded
  explicitly through every consumer. No module-level randomness; sorted
  iteration wherever randomness is consumed; output column order a
  fixed function of the schema. Same profile, seed, version, and locked
  environment produce the same bytes on the same platform (plan D12).
- **Built-in validation.** The tool measures its own output and reports
  the result plainly. A check that cannot fail is a defect; a passing
  report must mean what it says.
- **Docstrings state guarantees.** Every public function's docstring
  says what it promises: accepted inputs, determinism behavior, errors
  raised, and any boundary it upholds. Review holds code to its stated
  word.
- **Errors speak human.** Every user-facing error names what went wrong
  and what to do next, in words a non-programmer can act on. "Invalid
  input" is a bug report against us, not an error message.
- **Open-source hygiene.** Small pushed increments; CI green before
  merge; GitHub is the source of truth; actions pinned by commit SHA;
  changelog kept current; nothing enters the tree that the
  decontamination, provenance, or offline scans would flag. Test
  fixtures are built by seeded neutral scripts at runtime - committed
  data-format files are forbidden outside the fixture manifest.

## The phase process

Plan first, always: every phase begins with a written plan in
`docs/plans/`, reviewed adversarially before any code. Code is then
reviewed against the ratified plan; deviations amend the plan, they do
not silently outgrow it. A freeze gate named in a plan (for example the
Phase 0 Class-A freeze) is blocking. Numeric machinery ports from the
private prototype only behind a ratified public method specification
with frozen neutral reference vectors, checked by the reviewer before
the implementation they anchor exists.

**The current phase is Phase 4.** Each entry below carries its own
state, so no reader has to work out from a date which of them is
running.

- **Phase 0 - public skeleton and security baseline:** repository, MIT
  license, CI, decontamination system, provenance guard, offline
  guarantee. *Complete*; see `docs/plans/phase-0-public-skeleton.md`.
- **Phase 1 - the profiler:** read a local table, emit the profile;
  first runtime dependencies enter under the reviewed dependency
  protocol. *Complete*; see `docs/plans/phase-1-profiler.md`.
- **Phase 2 - the generator:** build the twin from the profile alone;
  the public method specification and frozen reference vectors were a
  blocking deliverable here. *Complete - closed by owner decision
  2026-08-12, with its review record standing exactly as written*; see
  `docs/plans/phase-2-generator.md`. Closure is an owner act, not a
  review verdict, and nothing describes Phase 2 as review-ratified.
- **Phase 3 - the end-to-end product:** profile, generate, and validate
  through one zero-code CLI; earliest possible first PyPI release.
  *Product work complete; closed by owner decision 2026-08-19 with its
  release NOT executed*; the ratified plan is
  `docs/plans/phase-3-product.md`. Closure is an owner act, not a
  review verdict, and nothing describes Phase 3 as review-ratified.
  What closed is the product: the three commands, the quality report,
  and the repository's move to public. What did not happen is the
  release this phase's charter named - there is no tag and nothing is
  published - so the acceptance criteria resting on release evidence
  are unmet, Phase 1's residual R3 stays open with them, and the plan's
  own register says so rather than counting them done.
- **Phase 4 - comprehensive column handling:** the full range of column
  types, rare categories, and missing-data patterns. *Current*; the
  ratified plan is `docs/plans/phase-4-columns.md`.
- **Phase 5 - relationships and fidelity depth:** cross-column
  structure and the quality report at full strength. *Not started* -
  this is the phase the twin's one-column-wide bound waits on.
- **Phase 6 - standalone build:** hardened, fully offline distribution
  for institutional machines. *Not started.*
- **Phase 7 - the interface:** a screen a researcher can use without
  typing a command - choose a table, run the workflow, read the report.
  *Not started* (owner decision 2026-08-18). Principle 2 has always
  promised that somebody who has never programmed can run the whole
  workflow, and until this phase that promise is kept by a command line
  with no configuration files and messages written for a person. This
  phase is where it stops depending on a terminal at all.

  Three constraints it inherits rather than chooses. It must be LOCAL:
  principle 3 forbids network I/O, subprocess execution and dynamic code
  loading in the product, so a hosted page is out - the whole point is
  data that cannot leave the machine. It must not become a second way to
  say things, so every sentence it shows comes from the same place the
  reports and refusals come from, under the same claim guards. And it
  wraps the three commands rather than reimplementing them, so a
  defect can never be true of one surface and false of the other.

  Its ordering against Phase 6 is deliberate and reversible: if both are
  built, the standalone build should carry the interface rather than the
  interface being bolted onto a shipped build. Whoever starts them
  decides which comes first, and says so.

  What it does NOT do: it makes no analysis easier to trust. A screen
  makes the twin easier to reach, which makes the one-column-wide bound
  easier to walk into - so it must state that bound where a person
  meets the twin, not only in a document they may never open.

# Validation method v1 — measuring a written table against a description

**Status:** revision 0, written before any validator code exists, under
the Phase 3 plan (`docs/plans/phase-3-product.md`), which governs on
every conflict. **Not ratified.** This is the third of the phase's
artifacts and the fifth governing document under the disposition seal.

**What this document fixes, and what revision 1 owes.** Revision 0
fixes the MEASUREMENT and the OBLIGATIONS: where a verdict comes from,
which facts are checked and at what grain, which are not checkable and
why, what a report may say out loud about a file nobody promised was a
twin, and what makes a check non-vacuous. Where the Phase 2 contract
says what a published fact MEANS and the Phase 2 method says how the
twin WRITES it, this says how a reader checks that the writing met the
meaning.

**It does not yet carry the two artifacts that make it an oracle**
(review item P3-C1-F5), and it says so rather than implying otherwise:
the COMPLETED entry table — every (fact, predicate, subcheck) row with
its kind and its named red case — and the report's normative byte
layout. Without those, two conforming validators could differ, and each
could then register its own fixtures as its own oracle, which is the
failure this project names by name. Both land in revision 1, written
beside the implementation and reviewed before the implementation is
ratified; the shipped tables are checked against this document, never
the other way round.

**What it does not fix.** No envelope of its own: every bound an
APPROXIMATED fact is checked against lives in
`docs/spec/generation-method-v1.md` G12 and is CITED here, never
restated, so the two can never drift apart. No cross-column check of any
kind: this version carries none, because the profile publishes none.

---

## V1. The boundary, the inputs, and what validation may touch

**V1.1 Two inputs, and nothing else.** The profile document, through the
same strict loader the generator uses (`contract.load_profile`, no
second loader and no relaxed mode), and one measured CSV. The generation
report is NEVER read: every fact about what the twin was allowed to do
is recomputed from the profile alone (V4), so no prose is an input to a
verdict.

**V1.2 The measured file may be anything.** Nothing distinguishes a
twin's path from a real table's, and a person will one day point this
command at the wrong file, or at the very table the profile describes.
The method is written for that: every rule below holds whatever the file
turns out to be, and V5 is the rule that keeps it safe to exist.

**V1.3 What validation writes.** One file, the quality report, through
the write transaction in its one-target form. Validation never writes,
moves, truncates or re-encodes the measured file or the profile, and the
report may not resolve onto either of them by path, by resolved path, by
link, by alias, or by a substitution between the check and the write.

**V1.4 What validation never imports.** The generation module. The
corner classifier of V4 is independent code written from this document,
and a validator that called `plan_generation` would share every planner
defect with the generator it is checking — which is the one thing a
second opinion may not do. No random number generator is constructed or
consumed anywhere in the validate path.

**V1.5 The reading is derived from the profile, never guessed.**

- The header is present exactly when `source.header_source` says the
  names came from the file. A twin whose names were generated is read
  first-row-as-data. The profiler's automatic header detection is never
  invoked here.
- The expected column count, and the expected names where a header
  exists, are known before the first byte is read.
- A profile publishing `n_rows: 0` leads to the degenerate forms of V6.4,
  which the profiler's own reader refuses and this one accepts.
- Every other reading refusal the profiler catalogues is reachable here,
  in the parameterized form of V9.

**V1.5-A1 Two questions are settled before the reader is called, and the
walk that settles them is bound to the reader it stands in for**
(2026-08-14, review item P3-V3-F6; the plan's amendment A-P3-6 clause 3
is the ruling and this follows it). Whether the file's first row can
name a table's columns, and whether the file holds any rows at all, are
settled ahead of the reader so that a structural mismatch stays a
reported MISS rather than becoming a refusal that quotes what it found
(V9). That makes the walk a SECOND READING of the same bytes, and a
second reading that disagrees with the first is a defect wherever they
can differ — not only where they were caught differing:

- it reads under the shipped reader's own limits, taken from the
  reader's own published names rather than copied. The reader raises
  the `csv` module's field size limit for the length of its pass; a walk
  running under the interpreter's default parsed a conforming twin's
  header and stopped, and the twin was reported as a file with no rows;
- it reads the file's characters without translating line endings,
  because the reader translates none;
- and where it cannot finish, it says so rather than handing back what
  it reached. A file neither reading can parse is a catalogued refusal,
  and a report built on a partial walk is a report about a file nobody
  read;
- and both questions are asked of the text the reader SETTLED ON, not
  of the UTF-8 reading alone (2026-08-14, review item P3-V3-F3; plan
  amendment A-P3-7 clause 4). Asking the second one of the UTF-8
  reading and answering "this file has rows" where there was none sent
  a header-only file whose bytes are not UTF-8 on to the reader, which
  refused it, while the same file written in UTF-8 got a full report.
  The producer refuses both and publishes nothing about either, so
  which of the two answers came back was that file's own encoding, told
  by the shape of the reply.

The suite drives both readings over the same files, crossing the
boundaries at which they can differ, rather than testing either rule
twice.

---

## V2. The measurement: re-describe, then compare

**V2.1 The measurement is the profiler's own.** The validator builds a
description of the measured file with the SHIPPED producer — the same
role rules, the same fold, the same parsers, the same exact-fraction
quantiles — and compares that description to the one it was given. This
is what the contract's EXACT-OBSERVABLE means in as many words:
"recounted from the written twin CSV, independently of the generator's
own bookkeeping". Re-implementing seventy-two recounts beside the
producer's would be a second implementation of the profiler and would
drift from it; running the producer is the only way the recount is the
same measurement the description was made with.

**V2.2 The settings it re-describes under** are the profile's own,
field by field, exactly as the Phase 3 plan's P3-D3 table fixes them.
Every classifier and publication threshold is read from the profile's
`settings`; the two declaration tuples are EMPTY, because the contract
deliberately does not record declared spellings; `forced_identifiers`
is applied, so a declared identifier is described as one; and the read
mode comes from `source.header_source` rather than from any settings
key. A sixteenth key, or a key skipped, is a defect in the validator.

**V2.3 The kept set, derived from the profile** (Phase 3 plan owner
decision 8, as amended). A twin can validly hold a spelling the
profiler would otherwise read as an absence, by three published routes,
and all three are recovered:

- every key of every published level's `variants`, as an exact
  spelling;
- every `sentinel_verdicts` candidate whose `reason` is exactly
  `kept_by_you`, matched at the profiler's own declaration-matching
  identity — numeric identity for a numeric candidate, never a byte
  comparison;
- every published `levels[].label`, at the FOLDED identity: a measured
  cell counts as data when its trimmed, case-folded form equals a
  published label's, which is the producer's own pooling rule.

**V2.4 And the kept set governs only what PRINTS, never a verdict.** On
the check side an absence is BLANKNESS, by the contract's own rule for
twins: every absent cell is written as an empty field, so `n_present`,
`n_missing` and every count that depends on them are measured from
blank and non-blank cells alone, with no sentinel or declaration
machinery anywhere in the verdict path. No gap in the reconstruction
can move a verdict; the worst it can do is withhold a measurement that
could have been printed, which is the safe direction.

**Which of V2.1 and V2.4 governs where they disagree, stated because
they can** (review item P3-C1-F4). The producer reads a cell equal to a
built-in missing marker as an absence, and residual R-P2-13 records
that a generated numeric value can BE such a text — so a conforming
twin's re-description can show an absence where the twin holds a
present cell. **V2.4 governs the verdict: present and missing are
counted from blank and non-blank cells, and the re-description's own
absence classification is not consulted for them.** Every count that
depends on presence is taken the same way. **And presence is not two counts alone** (review item P3-C2-F2): which
cells are present decides which cells a style map, a ladder or a
distinctness count is taken over, so EVERY measurement whose input is
the set of present cells is taken over the blank/non-blank split too,
and the re-description's own absence classification is consulted for
none of them. V2.1's re-description governs what does not depend on that
split — which role a column reads as, which label a value folds to, how
a cell is spelled — and it governs the disclosure gate of V5, where a
collision can only move a column toward MORE withholding, never toward
printing more. The two rules therefore never decide the same number: one
owns which cells are counted, the other owns how they read.

**How the split measurement is TAKEN, added because leaving it unsaid
cost a verdict** (amendment V2.4-A1, 2026-08-13, review item P3-V2-A1).
This clause said which cells a measurement is counted over and did not
say how a validator that may not re-implement a recount (V2.1) is to
count them. The first implementation read that gap as permission to
WITHHOLD every presence-dependent obligation of a column wherever the
two readings of presence disagreed — so one cell spelling a built-in
missing marker turned every level, distinctness and suppression
obligation of that column from a potential MISS into a withholding, a
file carrying none of its published labels exited 0 under "no checkable
obligation was missed", and any registered red case of V8 could be
defeated by adding one such cell to the column it targets. That is a gap
in the reconstruction moving a verdict, which the paragraph above
forbids in terms.

**So the measured file is described TWICE, by the same producer, over
the same cells.** The first description is the file's own — the
settings of V2.2 exactly — and it governs V2.1's side: how the cells
read, which role the column is, and the disclosure gate of V5. The
second is taken with absence pinned to BLANKNESS, by naming as kept data
every non-blank spelling the producer's own built-in tables would read
as an absence, and every measurement whose input is the set of present
cells is read off it. Running the shipped producer over a derived input
is not a second implementation of a recount, so V2.1 is met exactly as
before; and the second description governs no gate, because a
description built under it would say more about the file than describing
that file on its own would publish, which V5 forbids. Where the gate is
open and the split description carries no measurement of that kind at
all — the column, counted with every non-blank cell as a value, is not a
column of that kind — the verdict is MISSED, with no measurement shown.

**This amendment RAISES the obligation and lowers nothing.** Every
subcheck it moves, it moves from WITHHELD to a verdict; no bar is
weakened, no published fact stops being checked, and the only new
withholding it can produce is none. A property test over the shipped
fixtures and the whole registered red battery asserts the bound the
first implementation broke: no edit to a measured file can make it stop
missing everything, and no obligation goes silent unless the same run
also reports MISSED a check of that column which decides whether the
file's own description publishes such a measurement at all.

**Which check that is, and why naming only the role was false**
(amendment V2.4-A2, 2026-08-13, review item P3-V2-B-F5). A2 states the
last clause of A1; A1 stated it as "the same run also reports that
column's ROLE MISSED", and the widened red battery of P3-V2-B-F5 found a
conforming file the narrow form calls a defect. A column whose written
values reach both ends of what a number can hold is a column of numbers
and reads back as one, so its role is HELD and its role is RIGHT; and
the producer publishes about that column that its spread CANNOT be
held, and publishes no spread. V5.1 then forbids the report to state a
spread for it, so `moments.std` is withheld while the role stands. The
run is not silent about the reason: `type.std_unrepresentable` is a
published fact of its own and MISSES in the same report, which is the
sentence a reader acts on. **So A2 WIDENS which published fact may
explain a silence, from one to those that decide whether the
measurement exists at all, and it lowers no obligation:** no check
stops being made, no verdict changes, and every silence still stands
beside a MISSED check of the same column that says why. The narrow form
could not be made true of a correct validator, and stating it was the
defect.

**Where the split may be REPORTED, because A1 said which number to take
and not whether it may be shown** (amendment V2.4-A3, 2026-08-14, review
item P3-V3-F1; the plan's amendment A-P3-5 is the ruling and this
follows it). A1 gave every presence-dependent obligation its number from
the second description. It did not ask whether stating that number is
inside V5.1, and it is not always: the producer counts presence by its
own absence rules, the split counts it by blankness, and the two differ
exactly on the cells that are non-blank and read as holes. **How many
such cells a column has is a FLOORED fact**, published per spelling in
`missing_by_source` and pooled into one unnamed total below
`small_cell_floor`, because a count of two cells sharing a rare spelling
is a count the floor exists to hide. So two files the producer describes
BYTE FOR BYTE ALIKE — fifty-nine labels and one empty cell, fifty-nine
labels and one `n/a` — received different verdicts, different censuses
and different exit statuses.

**So the split's number is taken where the file's own description names
the source of every missing cell, and the file's OWN description
supplies the verdict where it pools any of them.** Where every source is
named, the exact multiset of spellings the holes wear is published, so
the split is derivable from what describing the file publishes and
stating it says nothing new. Where sources are pooled it is not
derivable, and the description itself is the only reading inside the
envelope — it IS the description.

**The two presence COUNTS are settled on a weaker publication, because
they need a weaker fact.** They need only how many holes are non-blank;
every other presence-dependent measurement needs what those holes spell.
`missing_by_class` counts holes under this package's own five words, so
it is published for every role including the three that publish no value
of the table, and where its pooled remainder is empty the two counts are
inside the envelope even where the spellings are not.

**It is not a withholding, deliberately.** A silence here is one any
file could buy by writing a single marker cell, which is the defect A1
exists to close; answering this conflict by withholding would trade a
confidentiality defect for the vacuity V3.4 refuses by name. Every
obligation still lands on a verdict taken from one description or the
other, and zero new withholdings are produced on any file. **This
amendment LOWERS one bound and no obligation:** residual R-P2-13's
missing-marker collision can now cost a verdict rather than only report
detail, in a column whose own description pools its missing sources, and
that is stated in the plan rather than discovered. Every measurement
whose input is the set of present cells is settled this way, the style
clauses included: they recount the written cells, so where the split is
not published they recount the cells that description reads.

---

## V3. The entry table: what is checked, at what grain, in three kinds

**V3.1 An entry's identity is the triple (registry fact, profile
predicate, subcheck).** The registry fact is the (group, field) the
disposition registry carries, and the registry stays the authority on
its class. The profile predicate is the condition on the loaded profile
under which the entry applies — `always` for most; the named ones are
`header-written`, `zero-rows-headerless`, `zero-rows-headered`, and the
four corner predicates of V4. The subcheck is one obligation at the
finest grain the contract governs.

**V3.2 The subcheck grain, stated so it cannot be quietly coarsened.**
Each of the eleven percentile rungs separately, the two ends exact and
the nine interior rungs each against its own window. Each published
style key. Each published level with its count, its `variants` map and
its `variants_withheld` multiplicity map. Each offset key and each of
the two endpoint offsets. Each length and word extreme. Each
absent-cell obligation. Each byte-level rule of V6.

**V3.3 Three kinds, and the partition is total over OBLIGATIONS.**

- an **executable subcheck** produces a verdict, and V8 binds it: it
  must carry a registered, named way to fail;
- a **listing entry** is an obligation the matrix itself says cannot be
  checked from a CSV — every REPORT-ONLY fact, the EXACT-CONTROL
  remainder that a CSV cannot evidence, and the structural facts of the
  zero-byte form. It produces no verdict, appears in the report's
  NOT-CHECKABLE census, and its failure mode is that census: removing
  its line is red against the report's exact-shape and golden tests;
- an **input-side entry** is a fact whose whole obligation lives on the
  profile — every LOADER-ONLY fact, and the profile-side membership
  rules of the STRUCTURAL containers. The contract says these impose no
  output obligation, so they may neither carry a verdict nor be listed
  as an unverified twin fact; the strict loader the validator already
  runs is what settles them, and the projection test asserts each is
  bound to a loader refusal or a structural loader rule rather than
  silently absent.

Totality is over obligations, not over facts: one fact may contribute
entries of more than one kind. `columns` contributes its profile-side
membership rule as an input-side entry AND its twin-side order rule —
that the list order IS the CSV's column order — as an executable
subcheck, which is the contract's own split. No obligation may be
unbound, double-bound, or bound to the wrong kind.

**V3.4 No vacuity, in either direction.** No executable subcheck may be
unable to fail, and no listing or input-side entry may be presented as
a check. Those are the two ways vacuity enters and both are refused by
name.

**V3.4-A1 And a THIRD way, which the first implementation found: a
verdict withheld because the VALIDATOR cannot take the measurement**
(2026-08-14, review item P3-V3-F4; the plan's amendment A-P3-6 clause 1
is the ruling and this follows it). WITHHELD says one thing and one
thing only: describing this file on its own would not publish what this
check measures (V5.3). It does not say that this code could not read the
value, and using it for that turns a gap in the validator into a silence
the reader cannot tell from a confidentiality rule. A column of quarters
reached the shipped validator that way — the generation method defines a
quarter's ordinal and applies both the ladder bound and the distinctness
bound to quarters, so eleven obligations were set, and every one of them
was WITHHELD on every file because the reading was written for the two
resolutions that name an instant.

**So every measurement this method takes in the ordinal space is taken
in the space the generation method fixes for the resolution the
description publishes, and that space is TOTAL over the resolutions the
producer can publish.** A published instant that names no point in its
own resolution's space is a contradiction between the strict loader and
this reading, not a fact about the measured file, and it is raised
rather than withheld. The suite walks the producer's own list of
resolutions, so a resolution added there without a reading here is red
on the commit that adds it.

**V3.4-A2 And the measurement taken in that space is the CONSTRUCTION's
own, written from the method and compared with the generator's writing
of it** (2026-08-14, review items P3-V4-F4 and P3-V4-F5; the plan's
amendment A-P3-9 clauses 2 and 3 are the ruling and this follows it).
A1 fixed the space every published instant is read into and said
nothing about the arithmetic done in it, and three readings then
diverged from the G12 construction they check: the rank windows of
G12.4 were drawn without the pinning that fixes the first and last
ranks at the published `earliest` and `latest`, the reading allowance
`u` was one step of the published PRECISION rather than one unit of the
ordinal SPACE, and the ladder was read with the floating-point reader
the numeric ladder uses rather than with the whole-number interpolation
G7.3 builds cells with. Each produced a verdict the generator
contradicts, in both directions: a file passing a distinctness bound its
own construction forbids, and a conforming twin missing a rung by less
than one ordinal unit.

**So a window this method cites is written out from the cited clause,
in the whole-number arithmetic that clause fixes, and the two writings
are compared in the suite where both may be imported** — exactly as
V4.2 compares the two corner classifiers and V6.4-A1 the two canonical
writings. The comparison is over every resolution AND every precision
the producer can publish, walked from the producer's own lists, and
over a spread of column heights: comparing the two ORDINAL SPACES and
reasoning that the windows follow is what let the third divergence
stand, because a scale factor cancels out of a subtraction and does not
cancel out of a floor.

**V3.5 The kind of an entry is decided by the DESCRIPTION, and four
entries are decided that way** (2026-08-13, review items P3-V2-C-F1,
F2, F3 and F7; the plan's amendment A-P3-2 is the ruling and this
follows it). V3.4 forbids an executable subcheck that cannot fail, and
whether one can fail is sometimes a property of the description rather
than of the subcheck: the same name against a published count of zero
and against a published count of two hundred and forty is not the same
obligation, and one of the two can be falsifiable while the other is
not. So the three-way partition of V3.3 is taken per entry, and an
entry whose failure set the description empties is a LISTING with one
sentence saying why nothing in a CSV settles it. Four are decided this
way, and the plan amendment states each as a lowering:

- `universal.structural_role`, on every column, because the axis states
  a declaration made when the description was written and the file is
  re-described under that same declaration (V2.2);
- `universal.position`, on the FIRST column of a description whose
  names were generated, because no file that reaches a verdict carries
  fewer than one column;
- `numeric.skew`, where the cited G12.3 envelope is that statistic's
  whole attainable range. This document may not draw a narrower one:
  every APPROXIMATED bound lives in the generation method and is CITED
  here, never restated, so a tighter envelope is that document's change
  to make;
- `styles.canonical.<form>`, where the published count of the form is
  not below the description's own row count, so the ceiling licenses
  every cell a file of that length can carry.

**And the partition is total the other way too**: an entry the
description leaves falsifiable stays an executable subcheck, and the
same fact is a check on one column and a listing on another where the
descriptions of the two columns differ. Which it is may never depend on
what the measured file turned out to hold.

**V3.6 A check may not be defeated by a compensating edit** (review
item P3-V2-C-F8). A subcheck whose verdict is a conjunction is only as
strong as the conjunct an edit can pay off separately, and a conjunct
that is another subcheck's whole obligation is one such: the headerless
form of `header.presence` asked for the published names on the first
line AND a row count above the published one, so writing the header and
dropping one record left the row count where it was and the check
reported the opposite of the truth about the bytes it governs. Each
subcheck answers for the obligation it names, on its own; a fact another
subcheck already checks is that subcheck's to miss.

---

## V4. The corners: an independent classifier

**V4.1 What a corner is.** A condition on the profile alone under which
the ratified plan names a lesser outcome for some fact — so a twin that
does not carry that fact is conforming, and a validator that called it
MISSED would be wrong. There are exactly four corners, and each is a
predicate over published numbers (this count is the CORNERS' own and is
unrelated to the number of G12 refusals, which method G12 fixes):

- **identifier-infeasible** (owner decision 6): a declared identifier
  whose published length range cannot supply `n_present` distinct
  values. Then `n_distinct`, `n_distinct_folded` and
  `n_distinct_by_occurrences` are REPORT-ONLY for that column, and
  nothing else is.
- **datetime-offsets-withheld** (P2-D9): a datetime column whose
  `utc_offsets` map is the single `(withheld)` key. Then `utc_offsets`,
  both endpoint offsets and `datetimes_read_at` are REPORT-ONLY, and
  the two ends are not.
- **label-variants-short** (P2-D6): a label column whose published
  variants and withheld-variant multiset together cannot supply the
  published raw `n_distinct`. Then raw `n_distinct` falls to the G12.7
  envelope.
- **numeric-spellings-short** (P2-D6): a numeric column whose permitted
  spellings cannot reach the published raw or folded distinctness. Then
  those fall to the G12.8 envelope.

**V4.2 The classifier is written from this document, not imported.**
The generator decides the same question from its own text; the two are
compared in the suite, over every producer-battery description and every
frozen conflict case, and any disagreement is red. A shared design error
now needs the same mistake written twice from two texts.

**V4.3 The G12 refusals are NOT corners.** They refuse GENERATION,
so no conforming twin exists for such a profile at all. A validate run
on one is a catalogued REFUSAL (V9), never a verdict and never a pass —
treating them as corners would launder an impossible obligation into a
passing report.

---

## V5. The disclosure gate: what a report may say about the measured file

**V5.1 The rule.** The quality report may state about the measured file
only what `synthtwin profile`, run on THAT FILE under the profile's own
settings, would publish about it.

**V5.1-A1 Where the producer REFUSES the file, the envelope is the
refusal** (2026-08-14, review item P3-V3-F3; the plan's amendment A-P3-7
is the ruling and this follows it). Two questions are settled ahead of
the reader (V1.5-A1) and both of them are settled about files the
profiler's own reader refuses: a file with no data rows, and one whose
first row leaves a name blank or uses a name twice. Validation reports
on those rather than refusing, because V9 makes a structural mismatch a
verdict; and reporting on them, it stated four structural obligations
and every column's position against a header line that no run of
`synthtwin profile` on that file publishes a word of. Two header-only
files under one name were five verdicts apart.

**So on such a path the report states what that refusal states and
nothing else.** The no-data refusal says the file holds no rows, so the
row count is measured and missed and every obligation of every column
is missed with it — a column with no cells carries none of them — and
what only its header line could answer, the width, the presence, the
names, the order and each column's position, is WITHHELD under a
sentence of its own. The unusable-header refusal says which fault the
first row carries, so the header's presence, its names and its order
are missed with that fault on the line, while the width and the record
count — two numbers that refusal stops before reaching — are withheld.

**V5.1-A1.1 The report is chosen by the refusal the reader RAISES, and
the two faults are not the same size** (2026-08-14, review item
P3-V4-F3; the plan's amendment A-P3-10 clauses 2 and 3 are the ruling
and this follows them). Which of these two reports a file gets was
settled by a walk of the file taken before the reader was called, and
that walk and the reader had a precedence to agree about — a zero-byte
check and a ragged check stand between the reader's own two questions.
They did not agree, on four routes, and on each of them two files the
producer refuses identically got different reports. So the walk is gone
and the branch is the reader's own refusal: two files the producer
refuses with one sentence cannot reach two reports, because the same
refusal chooses the report.

**And what that refusal names differs between the two faults.** The
profiler's refusal for a BLANK name names the column NUMBER, so the
report states it. Its refusal for a REPEATED name quotes the NAME and
names no position, so `dup,a,dup` and `a,dup,dup` are one file to it;
naming the positions is therefore not "less than the name" but a fact
of its own, and the report states the fault alone. V5.4's rule that no
string of the measured file is ever printed is untouched: the name is
not printed either. On both paths the encoding rule is withheld too, because
which reading a file was read under is a fact the producer publishes
about the files it describes. Nothing is lost by any of it: neither
path is reachable by a conforming twin of the description that reaches
it, so every one of those obligations still answers on the file the
description calls right, and the file that reaches these paths misses
whatever its header holds.

**The degenerate zero-row forms are the one place this stops, and it
stops for V3.4's reason.** There the conforming twin ITSELF is a file
the producer refuses — V1.5 says the profiler's reader refuses these
forms and this one accepts them — so withholding would leave V6.4's
byte form unable to HOLD on any file at all and would take V6.4-A1's
repair with it. The residual that leaves open is stated at its size in
the plan's amendment rather than left to be found.

**V5.2 Why the submitted profile's floor is not the envelope.** The
producer routes a two-valued numeric-looking column to a label role
BEFORE it reaches the numeric path, and withholds both labels when they
sit below the floor. A crafted numeric profile would walk a naive
validator straight past that routing and print the measured mean of a
column whose every published fact the producer would have withheld. So
the gate consults the FILE's own description, which V2.1 already builds.

**V5.3 What the gate governs: the verdict as well as the value.** A
within-bound or missed line stated against a candidate value is itself a
measurement-derived statement, and repeated candidate profiles would
binary-search a number the file's own description withholds. So where
the gate closes over a subcheck, its verdict is WITHHELD: neither the
measurement nor its outcome is shown, one fixed sentence says the file's
own description would not publish what this check measures, and the
count of withheld subchecks appears in the census. That the column
classifies differently than the submitted profile expects is itself a
fact the producer publishes about any file — the role axis — so the
signal stays inside the envelope.

**V5.3-A1 What the envelope is drawn round, and the test that settles a
disputed fact** (2026-08-14, review item P3-V3-F2; the plan's amendment
A-P3-5 clause 3 is the ruling and this follows it). The plan's A-P3-3
clause 6 settled `bytes.line-endings` and `bytes.terminal-newline`
outside this envelope on the ground that V5.1 is drawn round facts about
the TABLE a file holds. That ground needs a test, or every awkward fact
gets called a file fact. The test is **whether the producer publishes
the fact about ANY file at ANY count**:

- where it publishes it above a floor and pools it below one, the fact
  is inside the envelope and the floor governs it — because the floor is
  how the producer says the count is small enough to identify somebody.
  The blank/non-blank split of a column's missing cells is such a fact:
  `missing_by_source` names the exact spelling at or above the floor and
  pools it below, so V2.4-A3 above governs it and no ruling may excuse
  it;
- where it publishes it about no file at any count, there is no floor to
  appeal to and no window to draw, withholding it withholds it forever,
  and V3.4 refuses a subcheck that can never verdict. That is the case
  the ruling is for, and it is a ruling rather than a derivation: it
  says the fact is one about the file's own form. Whether a numeric
  cell's TEXT is a spelling its own value licenses is such a fact —
  the producer's form ladder discards it by design, reading `1.5` and
  `01.5` as one form — so `styles.spelled` and `styles.canonical.<form>`
  state their verdicts.

**A ruling of the second kind carries its bound with it.** A spelling
can carry a person's own data where a line ending cannot, so what
escapes is bounded rather than waved away: neither subcheck prints a
measured count, and `styles.spelled` takes no number from the submitted
description at all, so no sequence of candidate descriptions can
binary-search anything through it. Which of the six FORMS a cell wears
is published and floored, and stays gated.

**V5.3-A2 The bound is a property, so it is measured; and one of the
two did not have it** (2026-08-14, review item P3-V4-F2; the plan's
amendment A-P3-10 clause 1 is the ruling and this follows it).
`styles.canonical.<form>` compares its recount of non-canonical cells
against a count the SUBMITTED description names, so the verdict flipped
at exactly that recount and eleven candidate descriptions read the
hidden number off it — the attack this section exists to stop, through
the subcheck a ruling had exempted. **So a recount that a ruling has put
outside the envelope enters a verdict only at the publication floor's
own resolution**: rounded DOWN to a whole number of `small_cell_floor`,
which is the resolution below which the producer names no count at all,
and downward so that a MISSED is never a file the ceiling has not
actually been exceeded by. What a sweep can then locate is the
floor-wide block and not the count. The plan's amendment states the
residual at its size, prices the teeth this costs — a file less than one
floor over its licence is no longer missed there — and shows why teeth
at one cell and a bound better than the exact count cannot both be had.

**V5.4 What may be printed, exactly.**

- No string from the measured file, ever — not in the report, not on
  screen, not in a refusal. Every label named in the report is the
  profile's own published label.
- Whole-column counts print exactly: rows, present, missing,
  distinctness. The producer publishes these for a column of any role.
- A numeric summary prints exactly only for a column the FILE's own
  description sends down a numeric path.
- A per-label, per-style or per-offset measured count prints exactly
  when it clears the floor. Below the floor the line states only what
  omission from the file's own description already publishes: not held
  at its published count, the measured count below the publication
  floor and possibly zero, withheld. The exact sub-floor number never
  appears beside a name. What may print namelessly is exactly what the
  producer publishes namelessly, which differs by kind: the suppressed
  count list for labels, and only the single pooled total for styles
  and offsets.
- An unpublished-content line says the file holds values the
  description does not publish, in N rows, with N floor-governed the
  same way, and never says what they are.

**V5.5 On the ordinary case the gate does not close.** When the measured
file IS the twin built from this profile, Phase 2's owner decisions 5, 8
and 10 give it back the same types, the two descriptions agree on every
role, and everything prints. The withholding bites on a mismatched
file, which is where it must. **The one exception is named rather than
claimed away**: residual R-P2-13's missing-marker collision can move a
column's re-described role, and there the gate may withhold on a twin
that is otherwise conforming. It costs detail in the report and never a
verdict (V2.4), and the green battery of V8.4 asserts zero withheld
verdicts over fixtures built clear of that corner, with the corner
itself pinned by its own case.

---

## V6. Verdicts, byte rules, and exit status

**V6.1 The five verdicts.** HELD (the exact obligation was met);
WITHIN-BOUND (an APPROXIMATED fact inside both ends of its cited G12
envelope); AUTHORIZED-DEVIATION (a lesser outcome the ratified plan
names for this profile's corner, shown with the exact plan passage or
owner decision that authorizes it, taken from the registry's own
citations); WITHHELD (V5.3); MISSED (an obligation the ratified matrix
sets that the file does not meet). Listing entries carry no verdict and
appear only in the NOT-CHECKABLE census.

**V6.2 Byte rules, each an executable subcheck.** UTF-8; no byte-order
mark; LF line endings; a terminal newline; the row count; the column
count and order; the header present exactly when
`source.header_source` says so and its names read back byte for byte,
including the quoted U+FEFF exception.

**V6.3 The numeric-style identity** is contract 7.5.7's, clause by
clause, with each published count a floor.

**V6.4 The degenerate zero-row forms** (Phase 3 plan owner decision 7).
A zero-row profile whose names were generated expects exactly zero
bytes; one whose names came from the file expects the header line and
its terminal newline and nothing more. The expected byte form IS the
executable subcheck, and the structural facts that zero bytes cannot
evidence — how many columns the schema has, their order, their
positions — are listing entries for exactly that predicate, with one
plain sentence in the census.
**"That predicate" is the ZERO-BYTE one, and the headed form is not
it** (2026-08-13, review item P3-V2-E-F5): a headed zero-row file
carries its header line, and that line evidences the column count, the
names and the order, so each of those is an executable subcheck there.
Reading this clause across both forms had put all three inside the byte
check's conjunction, which V3.6 forbids, and left two registry facts
bound by no entry at all while the census called itself every
obligation the description sets. The headerless form keeps the listings
and gains one check: that no header line was written, which a file of
no bytes evidences exactly.

**V6.4-A1 What the zero-row byte check answers for, now that three
facts have been taken out of it** (2026-08-14, review item P3-V3-F5;
the plan's amendment A-P3-6 clause 2 is the ruling and this follows
it). The clause above says the expected byte form IS the executable
subcheck and then takes the column count, the names and the order out of
it, and it did not say what was left. The first implementation read
"the expected byte form" as ONE PHYSICAL LINE ending in a line feed,
which is neither the bytes nor a record: `"reading"` quoted passed for a
description whose renderer writes `reading`, because how a name is
SPELLED was nobody's obligation once reading it back became
`universal.name`'s; and a published name holding a line feed is written
as one record over two physical lines, so the conforming file the
renderer writes was reported MISSED.

**What is left to this subcheck is the WRITING and the STOP**: the file
holds exactly one record, that record is written the way the generation
method's own writing rule writes it — minimal quoting, a doubled quote
inside a quoted field, the byte-order-mark exception — and nothing
follows it. The record's line ending is taken off before the comparison,
because which characters end a line is the two byte rules' obligation
and V3.6 forbids a subcheck to answer for another's. The canonical
writing is derived from the METHOD, never imported from the renderer
(V1.4), and the two writings are compared in the suite where both may be
imported, exactly as V4.2 compares the two corner classifiers.

**And a byte rule is about the file's RECORDS, not about a byte**
(same amendment). `bytes.line-endings` asks whether a carriage return
ends one of the file's lines. A carriage return inside a quoted field is
data the method writes on purpose, and asking whether one is present
anywhere in the file told a conforming twin it had broken a rule it
kept. For the same reason the measured file is read WITHOUT translating
line endings: the reader translates none, and a validator whose text
differs from the reader's is not standing in for the reader at all.

**V6.5 Exit status.** 0 when validation ran to completion and no
subcheck MISSED; 3 when it ran to completion and at least one did; 1 on
a catalogued refusal, which is validation that could not run at all; 2
on a usage error. Automation therefore tells a bad twin from a file it
never evaluated without reading prose.

---

## V7. The quality report

**V7.1 Order.** The verdict summary first, then the honest bounds, then
the fact-by-fact detail, then the analyst-expectations section, then the
handling rule. Every interpolated string passes the display boundary
once, label variants included. The report's normative byte layout and
its golden hashes are revision 1's, with the completed entry table; this
revision fixes the order and the obligations, not the bytes.

**V7.1-A1 The report names the file it is about, before anything else**
(2026-08-14, review item P3-V2-G; plan amendment A-P3-4). The first
thing under the title is the NAME of the measured file, as the person
spelled it on the command line — the last component of the path, never
a folder and never a whole path. The report says it is a report about
ONE file, so it says WHICH before a reader reaches that sentence.

The name is the only string in the report that came neither from the
description nor from this method's own words, and it is safe to be
there for a reason V5 does not have to reach: it is not a fact about
the table the file holds, and it was typed by the person reading the
report. It passes the display boundary exactly as a published label
does. Nothing about where the file SITS is recorded, so a report says
the same thing wherever it is kept, and the same check on the same
bytes writes the same report in every folder (V10).

The output file's own name is derived from the measured file too. One
profile can be measured against any number of files; a report name
derived from the profile therefore named one file and described
another, refused a second candidate for a collision that had nothing to
do with what was measured, and under `--replace` overwrote the first
file's report with a report about a different file under the first
file's name.

**V7.2 The summary is generated from the census alone.** It states how
many subchecks HELD, how many landed WITHIN their stated windows, how
many were AUTHORIZED-DEVIATIONS with their citations, how many were
WITHHELD, how many MISSED, and how many obligations were NOT CHECKABLE
and why. There is no sentence of the form "every published fact was
found": on a profile with corners or approximated facts it would be
false by construction, and it cannot be written from these verdicts at
all. A pass means **no checkable obligation was missed**, with the other
counts standing beside it and never folded into it.

**V7.3 The limits it carries, every run.** No cross-column structure was
validated because none is carried; rows independent and the grain
undescribed; numbers computed on the twin are not research results; and
the verdict-scope sentence — a passing report is not a fitness verdict
for any analysis, it validates nothing the profile does not publish, and
it cannot tell a synthetic file from a real one, because nothing in a
CSV proves provenance.

**V7.4 The analyst-expectations section** names what this version checks
(single-column shares of published labels, distribution ladder positions within
stated windows, spread and shape summaries within stated windows,
missing-value counts, value-format read-back) and what it does not (any
target tying two columns, and any target about row grouping), saying
that those need cross-column structure this version deliberately does
not carry, and that carrying them is later work with its own plan and
its own contract change. It promises no version, no slot and no date.

**V7.5 The fourth artifact.** The report states measured facts about a
real-derived file, so it is real-derived material exactly as the
profile, the twin and the generation report are, and it says so.

**V7.5-A2 — and it names every file a full run leaves behind, which is
FIVE** (plan amendment A-P3-8 clause 2, 2026-08-14). The handling rule
this report carries enumerates the description, the plain-language
summary beside it, the twin, the twin's report and this quality report.
The summary is on that list because the profiler writes its description
twice — once for a program and once in words — and the half a person
reads repeats the published labels; a rule that named four files told a
reader by omission that the fifth was free to travel. Nothing about
what this report MEASURES changes; what changes is what it says about
keeping the files.

---

## V8. Non-vacuity

**V8.1 Every executable subcheck carries a registered red case**: a
perturbation of a valid twin that must produce MISSED — per rung, per
style, per level, per variant map, per offset, per extreme, per
structural rule. Wrong count, moved cell, re-cased label, re-spelled
number, shifted date, truncated file, re-encoded bytes, reordered
columns, edited header, injected byte-order mark, nonempty bytes in the
zero-row form.

**V8.2 A red case NAMES the subcheck it must fail**, and the battery
asserts that THAT subcheck reports MISSED. Other subchecks failing
alongside is fine; a perturbation caught only by a neighbour — the mean
tripping while a hard-coded rung check sleeps — is a red battery,
because the named subcheck did not do its job.

**V8.3 The coverage identity** walks the shipped executable-subcheck
table and asserts every entry has at least one registered, named,
passing red case.

**V8.4 The green direction.** Producer → generator → validator over the
every-role fixture and every frozen conflict case: zero MISSED and zero
WITHHELD, and on the conflict cases the AUTHORIZED-DEVIATION verdicts
must APPEAR with their citations.

**V8.5 The vacuity floor.** A counted floor of distinct red-case classes
per disposition class, so the battery cannot rot into one shared
perturbation.

---

## V9. Refusals

Validation refuses, rather than returning a verdict, when it cannot run:
the measured file missing, unreadable, a folder, or not readable as CSV;
the profile failing the strict loader; the profile meeting any G12 refusal
(method G12 fixes their number and their names, and this document
follows it rather than restating a count), whose message mirrors the
generation refusal and adds
that whatever the file is, it cannot be that profile's twin; the quality
target already present without `--replace`; the target resolving onto
either input; and memory exhaustion.

**Every refusal reachable from validation names positions, never
values** — which column, which row — wherever the profiler's own form
would quote measured content. On this path the file may not be the
person's own table, and refusal text travels as freely as a report does.

A structural mismatch is NOT a refusal: a wrong column count or a wrong
name is a MISSED verdict with a plain explanation, because the report is
the product even when the news is bad.

---

## V10. Determinism

The quality report's bytes are a fixed function of (the profile bytes,
the measured file's NAME, the measured file's bytes, the synthtwin
version) on one platform under the locked dependency set — the same
scope D12 gives the twin. The name joined that list with V7.1-A1
(2026-08-14): the report says which file it is about, so the same bytes
under a different name give a different report, deliberately.
Cross-platform agreement is verified empirically by golden report hashes
on every CI cell, exactly as the twin's are.

**Validation consumes no randomness, and this clause says at what level
that is enforced** (2026-08-14, review item P3-V2-F-F2; plan amendment
A-P3-4). It used to say that the offline scanner's policy asserts the
validate closure cannot reach a random source. That was false, and
measurably so: a fresh interpreter running only `validate` gains
`numpy.random`, `numpy.random.mtrand`, `random`, `secrets` and `uuid`,
because validation must read a CSV, reading a CSV means pandas, and
pandas imports numpy. What is enforced, at three levels, is:

- no module of the synthtwin package on the validate path imports a
  random source — the offline scanner's policy over the source tree,
  plus a static walk of the closure;
- the validate path never reaches the generation module, where this
  package's own random number generator lives — asserted in a FRESH
  INTERPRETER against `sys.modules`, because inside a test process the
  module cache answers for whatever an earlier test imported;
- a validate run DRAWS from no random source — every reachable source
  in the process is trapped and the whole command is run at them.

The third is the property the determinism clause above needs. A random
source being present in the process is not a defect; drawing from one
would be.

# Validation method v1 — measuring a written table against a description

**Status:** revision 0, written before any validator code existed, under
the Phase 3 plan (`docs/plans/phase-3-product.md`), which governs on
every conflict. **Not ratified.** This is the third of the phase's
artifacts and the fifth governing document under the disposition seal.

**The validator SHIPPED, and this status line is not a claim that it did
not** (plan amendment A-P3-30). The clause above read "written before any
validator code exists", in the present tense, for as long as the
validator has existed — which is the stale-claim shape this repository
has now caught in five rounds. What is unchanged is everything the line
was for: this is still revision 0, it is still not ratified, the two
artifacts revision 1 owes are still owed, and the shipped tables are
still checked against this document rather than the other way round.
Amendments made since are numbered in place, each saying what it raises
or lowers.

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
`settings`; both declaration tuples are DERIVED from the profile's own
published text, because the SETTINGS BLOCK deliberately records no
declared spelling and the column blocks publish them anyway (V2.3);
`forced_identifiers` is applied, so a declared identifier is described
as one; and the read mode comes from `source.header_source` rather than
from any settings key. A sixteenth key, or a key skipped, is a defect in
the validator.

**V2.2-A1 The missing tuple was EMPTY, and the reason it gave was true
of a twin and false of a table** (2026-08-14, review item P3-V4-F1; the
plan's amendment A-P3-15 clause 1 is the ruling and this follows it).
This clause read "the two declaration tuples are EMPTY, because the
contract deliberately does not record declared spellings", and the plan
gave `declared_missing_values` the reason "genuinely absent from every
twin, whose absent cells are written empty". The twin is not the only
file this command is pointed at (V1.2): the OTHER one is the table the
description was written from, and that table is exactly where a
`--missing-value` spelling still stands in the cells. Twelve `XX` cells
in such a table were read back as data, the column re-read as free
text, and seven obligations came back MISSED against the table's own
profile; declared as the number `-777` instead, seventeen did.

**V2.3 The kept set, derived from the profile** (Phase 3 plan owner
decision 8, as amended). A twin can validly hold a spelling the
profiler would otherwise read as an absence, by three published routes,
~~and all three are recovered~~ **— and all three are WITHDRAWN by
V2.3-A4 below, which reads the kept set out of the settings block
instead. They stand here as the record of what version 4 forced**:

- every key of every published level's `variants`, as an exact
  spelling;
- every `sentinel_verdicts` candidate whose `reason` is exactly
  `kept_by_you`, matched at the profiler's own declaration-matching
  identity — numeric identity for a numeric candidate, never a byte
  comparison;
- every published `levels[].label`, at the FOLDED identity: a measured
  cell counts as data when its trimmed, case-folded form equals a
  published label's, which is the producer's own pooling rule.

**V2.3-A1 And a FOURTH published route, for the other declaration**
(2026-08-14, review item P3-V4-F1; the plan's amendment A-P3-15 clause 1
is the ruling and this follows it). What the person named as "no value"
is published too, and by a route of nearly the same kind: a column's
`missing_by_source` carries the spelling of every hole whose count
reaches `small_cell_floor` ~~exactly~~ **— as a report SHOWS it, which
is not the same thing and is corrected by V2.3-A2 below**. So

- every key of every published `missing_by_source` that is not one of
  this package's own placeholder names, not a spelling the built-in
  table already reads as an absence, not a spelling that reads as
  one of the three numeric stand-ins, **and not one the display
  boundary could have altered (V2.3-A2)**, is recovered into
  `declared_missing_values`, at the producer's own declaration-matching
  identity.

**Which keys those are is DERIVED, not guessed.** The producer has four
ways to make a cell a hole and no fifth: the person's declaration, by
spelling or by number; a blank; one of the built-in missing texts; and
a numeric stand-in the column's own verdict turned down. The three
exclusions above are the other three, each recognisable from the
description alone, so what is left can only be a declaration.

**V2.3-A2 The field is DISPLAY-ESCAPED and REPORT-ONLY, so the fourth
route reaches only what the boundary cannot alter** (2026-08-15, review
item P3-V7-F1; the plan's amendment A-P3-19 is the ruling and this
follows it). V2.3-A1 called `missing_by_source` the exact spelling. The
profile contract says the opposite in terms — section 5.4 makes its keys
the spelling "after passing through the display boundary that escapes
line, control and bidirectional formatting characters", and decision
13.5 draws the difference from `variants` deliberately, because a
variant is written back into a cell and a missing source is only ever
read.

**That boundary is not one-to-one, and the consequence is not a matter
of detail.** Seventy-two rows whose holes are spelled `X`, U+0001, `Y`
publish the key `X\x01Y`; so do seventy-two rows whose holes are spelled
with those six printable characters. The two whole descriptions come out
BYTE FOR BYTE ALIKE, so nothing this method may read tells them apart.
Reading the key as exact cost a verdict in both directions: the
control-character table missed seven obligations against its own
profile, and a file wearing the printable spelling PASSED against the
control-character table's description, with a census of zero missed,
although `synthtwin profile` under that description's own declaration
reads that file as free text with 72 present cells and no holes.

**So a key is recovered only where the boundary provably left it
alone.** The test is decidable from the key: no substring of it is a
form the boundary itself writes. Every text holding a display control
shows as a key containing such a form, so a key holding none has exactly
one reading, which is the key. A key holding one has at least two, and
this method does not guess between them.

**And matching the DISPLAYED form instead is refused, at the reason.**
Such a rule passes both tables above, and it is exactly what produces
the passing report: it re-describes the other file as the one the
description asks for. Any rule that passes the first passes the second —
V2.4-A4 clause 3's own reasoning about the kept-`n/a` gap, reached again
from the other declaration — and a report that hides a miss is worse
than one that states a miss it should not.

**What this route does NOT reach, stated at its size.** A declaration
whose cells sit below the publication floor in every column is pooled
into `(withheld)` and published nowhere; a declared value that IS one of
the three stand-ins cannot be told from the sentinel rule's own
judgment; ~~and a declaration whose spelling holds a character the
display boundary shows is published only in its shown form and is not
recovered~~ **— that third one is withdrawn by V2.3-A3 below, because
the format changed under it**. All three are named in V2.4-A4 below with
what they cost.

**V2.3-A3 The field is the EXACT spelling from contract version 5, so
the fourth route reaches every key. THIS RAISES** (2026-08-17, owner
ruling of that date; the plan's amendments A-P3-27 and A-P3-28 are the
ruling and this follows them; `docs/spec/profile-contract-v5.md` C5-1
and C5-N5 are the format).

V2.3-A2 above rested on two facts about version 4 of the profile
contract, and version 5 changes both of them.

- **The key crossed the display boundary before it was stored.** From
  version 5 it does not: `missing_by_source` stores the source spelling
  character for character and the boundary is applied where a key is
  SHOWN, which is the rule `variants` next door has always had. So the
  map is one-to-one again, the two tables of V2.3-A2's witness produce
  two different descriptions, and the exclusion that read "recover a key
  only where the boundary provably left it alone" has nothing left to
  exclude. It is withdrawn. `parsing.shows_only_itself` remains the
  property its own docstring claims and remains what makes the SHOWN
  surfaces safe; it is no longer consulted here.
- **The map mixed two key spaces.** Version 4 put `(blank)` and
  `(withheld)` into it beside the person's spellings, so a key had to be
  tested against this package's own class words before it could be
  trusted. Version 5 gives the map one key space and moves those two
  counts to `n_missing_blank` and `n_missing_withheld`, so a key reading
  `(withheld)` means cells of the table held exactly that text. That
  exclusion is withdrawn too, and withdrawing it is not merely a
  simplification: keeping it would walk past a spelling the table wore.

**Which exclusions remain, in full.** A key is recovered unless the
built-in table already reads it as an absence, or it reads as one of the
three numeric stand-ins. Both are recognisable from the description
alone and both are other producer routes rather than declarations.

**What it costs, and it costs nothing on this side.** Every subcheck it
moves, it moves off a false MISS or off a not-checkable line: the
control-character table's seven come back as checks and hold, and the
file that PASSED against the other table's description with a census of
zero missed now misses the seven it always owed. No file loses a check
and no new withholding appears.

**What it does NOT reach, and neither does any version of the format.**
A declaration whose cells sit below the publication floor in every
column is still pooled and named nowhere, unless the word is one of this
package's own, which version 5's settings block records for a different
reason. And a column whose publication class permits no value of the
table publishes no marker word whatever made its cells absent. Both are
stated as limits in contract 5 section 7 and both stay in V2.4-A4's list
below.

~~**What this clause does NOT change.** The reconstruction of the kept
side is untouched: contract version 5 records which of this package's
own words a `--keep-value` named, and this method does not yet read
them, so the head count of V2.4-A4 still asks its kept-side question the
version 4 way and still over-fires on every column of a description that
names a kept value. That is the safe direction and it is a stated limit
of this document until the clause that narrows it is written.~~
**THAT CLAUSE IS NOW WRITTEN. It is V2.3-A4 below, and this paragraph
is struck rather than deleted because it is the record of the limit
between the two stages.**

**V2.3-A4 The declarations are READ from the settings block, and the
three inferred routes of V2.3 are withdrawn. THIS RAISES** (2026-08-17,
owner ruling of that date; the plan's amendment A-P3-29 is the ruling
and this follows it; `docs/spec/profile-contract-v5.md` section 6 and
its C5-19, C5-20 and C5-K1 to C5-K5 are the format).

V2.3 recovered the kept set by INFERENCE from three facts a description
publishes for other reasons, because the settings block recorded a
declaration as a count and never as text. Contract version 5 records
which members of this package's own closed vocabulary — the ten
spellings and the three stand-in numbers of its section 14.1 — each
declaration named, from the command line and from no cell. So:

- **the kept set is `settings.kept_values.built_in_texts` and
  `settings.kept_values.built_in_numbers`, and nothing else.** The
  three routes of V2.3 are withdrawn. Contract 5 section 6.4 proves
  those two lists are the WHOLE of the kept side's effect on the
  reading rule: a rescue can only matter for a cell that would
  otherwise have been absent, and every way a cell becomes absent is
  reached only by naming a member of that vocabulary. The routes
  answered a question about a description's LEVELS, and a label is a
  spelling of a cell the producer read as a VALUE, so naming it as kept
  changed no cell's reading;
- **the fourth route gains a second half.** V2.3-A1's walk over
  `missing_by_source` stands unchanged, and beside it
  `settings.declared_missing_values`'s two lists are read the same way.
  A built-in word named as "no value" moves its cells from class
  `(text-code)` to class `(declared-missing)` (contract 5 C5-20); a
  stand-in number named as "no value" takes its cells out before the
  column's own sentinel rule judges them. Both were unrecoverable under
  version 4 and both were recorded as residuals; neither is now.

**What it costs, and it costs nothing.** Every obligation it moves, it
moves off a not-checkable line and onto a check. No file loses a check,
no new withholding appears, and no verdict that HELD stops holding.

**What it does NOT reach.** The two limits of contract 5 section 7, and
they are the same two V2.3-A3 leaves: a word of the PERSON'S own pooled
below `small_cell_floor`, and a word of the person's own on a column
whose publication class permits no value of the table. A word of this
package's own is now recovered in both of those cases, because the
settings block carries it whatever the floor and the publication class
did with its cells.

**The exclusions that remain, in full.** A key of `missing_by_source`
is recovered unless the built-in table already reads it as an absence,
or it reads as one of the three stand-ins. Both are still skipped there
— and both are now ANSWERED from the settings block instead of being
lost, which is what makes them exclusions rather than residuals.

**V2.3-A5 A recovered spelling is compared RAW, because the display
boundary is for a screen. THIS RAISES; it lowers nothing** (2026-08-17,
owner ruling of that date; the plan's amendment A-P3-33 is the ruling
and this follows it; review item P3-V9-F3).

V2.3-A3 above withdrew the exclusion that existed because version 4
escaped a key before storing it. It did not say what else that fact had
been holding up, and one thing was: the rule that decides whether a CELL
wears a recovered declaration put the cell through the display boundary
first, so that both sides of the comparison would be in the published
form. From version 5 the published form IS the raw form, so escaping one
side compared a text that had crossed the boundary with one that had
not.

**What that cost, measured.** Sixty numbers, twelve holes spelled `X`
U+0001 `Y`, five blank cells pooled below the publication floor: the
rule recognised none of the twelve, the column's cells were recounted as
though its own description read all of them as values, and SEVEN style
obligations came back WITHHELD on the table the description was written
from. A check that cannot fail is a defect by this project's own
charter, and on a file that really did violate two of the seven, those
two were withheld rather than MISSED.

**The rule, stated so it cannot come back.** Escaping is applied where a
spelling is SHOWN and nowhere else. No comparison in this method runs on
escaped text, on either side; the module that states verdicts calls the
display boundary nowhere at all, and the module that renders a report is
where a spelling meets a screen. The suite reads this off the parsed
source rather than off a promise.

**The rule is wider than this method, and the sweep for it found a
second site.** The profiler's summary asked "is this word one of
synthtwin's own?" of an escaped key and answered with escaped text. It
printed the same characters either way, because the page crosses the
boundary once and crossing it twice changes nothing — so the cost was
not a moved byte but a question asked about text no description holds.
Any surface that DECIDES something about a spelling decides it on the
spelling the description stores.

**V2.4 And the kept set governs only what PRINTS, never a verdict.** On
the check side an absence is BLANKNESS, by the contract's own rule for
twins: every absent cell is written as an empty field, so `n_present`,
`n_missing` and every count that depends on them are measured from
blank and non-blank cells alone, with no sentinel machinery anywhere in
the verdict path. ~~No gap in the reconstruction can move a verdict;
the worst it can do is withhold a measurement that could have been
printed, which is the safe direction.~~ **Those two clauses are false
as written and are withdrawn by V2.4-A4 below, which states what is
true in their place. No rule in this document may be re-derived from
them.**

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
`small_cell_floor` — which from contract version 5 is the field
`n_missing_withheld` rather than a key of that map, the same number
under a name of its own (V2.3-A3) — because a count of two cells sharing
a rare spelling is a count the floor exists to hide. So two files the producer describes
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

**What "no gap in the reconstruction can move a verdict" is worth, said
at its size instead of as an absolute** (amendment V2.4-A4, 2026-08-14,
review items P3-V4-F1 and P3-V5-F2; the plan's amendment A-P3-15 is the
ruling and this follows it). V2.4 promised that a gap in the
reconstruction can only cost detail. It cannot: A3 above takes the
split's number only where the FILE'S OWN description publishes the
split, that description is built under the reconstructed settings, and
a declaration the reconstruction misses is a spelling that description
reads as a hole. The gap therefore decides whether the gate is open,
and a gate that closes wrongly puts the file's own — wrong — count on a
verdict. Three clauses, and each says which way it moves.

**Clause 1 — the fourth route. THIS RAISES.** V2.3-A1 reads back the
person's `--missing-value` spellings from `missing_by_source`. Every
subcheck it moves, it moves off a false MISS: seven on a table declared
with a text marker, seventeen with a numeric one, and zero new
withholdings on any file. Nothing stops being checked.

**Clause 2 — the two presence counts come off the split DESCRIPTION,
not off a blank recount beside it. THIS RAISES, and it narrows
blankness.** V2.4 reads every presence-dependent obligation off the
split description; these two were recounted separately, and while both
declaration tuples were empty the two answers were the same number. They
are not once a declaration is recovered, and a report carrying both
disagreed with itself — 211 present beside a distinctness count of 199
taken over the cells that number claims. So blankness is narrowed to
what its own reason reaches: a cell is absent when it is empty, OR when
it wears a spelling the description ITSELF publishes as the source of
its holes. The reason V2.4 pinned absence to blankness is residual
R-P2-13 — a generated value can legitimately BE the text of a built-in
marker, and no file may be failed for colliding with synthtwin's OWN
vocabulary. ~~Nothing of synthtwin's own vocabulary is in the recovered
set, by construction (V2.3-A1's three exclusions).~~ **That sentence was
true of version 4 and is false from V2.3-A4, and the correction is
below.** **What it costs:** a
non-blank cell can now be absent to these two counts, so a generated
value that collides with a spelling the DESCRIPTION declares — not one
of the built-in table — is counted as a hole. That is R-P2-13's shape on
a declared spelling, it is bounded by the cells wearing it, and it is
recorded here rather than found.

**And the bound on that cost is WIDER from V2.3-A4, stated at its size
rather than left inside a withdrawn sentence** (2026-08-17, the plan's
amendment A-P3-29). The recovered set can now hold a member of this
package's own vocabulary, because the settings block says the person
named it as "no value". So a generated cell colliding with THAT word is
counted as a hole here, where version 4 counted it as data. Three things
bound it and none of them is an assumption:

- it reaches only a word the description ITSELF declares as "no value",
  never the built-in table at large — a description that declares
  nothing is untouched, and `_KEPT_OVER_THE_SPLIT` still names every
  built-in marker as data on it;
- it is the reading the description was written under. The producer
  read every cell wearing that word as a hole in every column of the
  table it described, so counting one as data here would measure the
  file under a rule its description was not written under, which is the
  error V2.4-A4 clause 1 repaired for a word of the person's own;
- and it is exactly residual R-P2-13's own shape — a generated value
  that equals a marker and re-reads as absent — on the one word class
  it did not previously reach. It is bounded by the cells wearing it,
  and under version 4 it was not smaller but hidden: such a description
  had that column's cell-counted obligations moved to NOT CHECKABLE
  wholesale (V2.4-A5), so no verdict could be wrong because no verdict
  was given.

**Clause 3 — what is still open, and why it does not close here. THIS
CLOSES NOTHING AND CLAIMS NOTHING.** ~~Two~~ **Three** gaps remain and
all of them are unrecoverable from what the contract publishes:

- ~~a `--keep-value` spelling that is one of the built-in missing texts,
  on a column that publishes no level carrying it — a column of numbers,
  of datetimes, of identifiers, of free text. Nothing in the document
  carries that spelling. The table it was written from reports
  `presence.n_present`, `presence.n_missing`, `counts.n_not_numeric`,
  `counts.n_left_out_of_statistics` and `counts.numeric_share` MISSED~~
  **CLOSED 2026-08-17, by the same decision the third entry asked for:
  contract version 5 records which members of this package's own
  vocabulary a `--keep-value` named, its section 6.4 proves those are
  the whole of what a rescue can change, and V2.3-A4 reads them. The
  five obligations above, and the two that joined them under the plan's
  A-P3-20 clause 3, are checked and every one of them HOLDS. The entry
  stands struck rather than deleted, because it is the record of what
  the format change was bought with;**
- a declaration of either kind whose cells sit below `small_cell_floor`
  in every column, pooled into `(withheld)` and named nowhere —
  **unless the word is one of this package's own, which version 5's
  settings block records for a different reason (V2.3-A4)**;
- ~~**a `--missing-value` spelling holding a character the display
  boundary shows** (added 2026-08-15, review item P3-V7-F1; the plan's
  amendment A-P3-19 is the ruling). `missing_by_source` publishes it in
  its shown form, two different spellings can share that form, and the
  two whole descriptions come out byte for byte alike. The table it was
  written from reports `presence.n_present`, `presence.n_missing`,
  `axes.role`, `axes.statistical_type`, `counts.n_not_numeric` and both
  distinctness counts MISSED — seven, the same seven V2.3-A1 took off
  the plain-marker table, given back on this class alone. What closing
  it needs is the same kind of decision the other two need: a change to
  what the profile publishes, not an edit to this module.~~ **CLOSED
  2026-08-17 by the decision this entry asked for: contract version 5
  stores the spelling exactly, the two descriptions differ, and all
  seven are checked and held (V2.3-A3). The entry stands struck rather
  than deleted, because it is the record of what the format change was
  bought with.**

**And reading the split anyway is not the answer, which is why this is
a ruling and not a repair.** Two hundred readings and one `n/a`, beside
two hundred readings and one `NULL`: the producer describes them BYTE
FOR BYTE ALIKE under the settings this method can build, the first meets
every fact a `--keep-value n/a` description publishes and the second does
not. Any rule that passes the first passes the second, and stating 201
present about the second states a count `synthtwin profile` run on that
file would not publish — V5.1. What closes it is a decision about what
the profile publishes, taken in the open; until then no sentence in this
document may say the bound of V2.4 is met.

**V2.4-A5 Where the reconstruction cannot be completed, the obligations
counted over that column's cells are NOT CHECKABLE and the report says
which and why — instead of printing a failure it cannot support**
(amendment V2.4-A5, 2026-08-16, owner ruling of that date; the plan's
amendment A-P3-26 is the ruling and this follows it). A4 clause 3 leaves
three gaps standing and records what each one costs: a table that is its
own description's perfect match is told it MISSED five, six, seven or
eleven obligations, with the numbers the incomplete reading produced
printed beside them. **That is the mirror of the rule this project holds
a passing report to.** A report that says a good file is bad, with
numbers, is a specific, plausible falsehood, and a reader who cannot see
the description's own limits has no way to disbelieve it.

**The description can always tell that the rule cannot be rebuilt, even
where it cannot rebuild it.** Two questions are asked of the description
alone and the UNION of them is taken, because neither alone is both
sound and complete:

- **per column**: are there cells the description says a declaration
  made absent that no brought-back spelling accounts for? Its inputs are
  `missing_by_class.declared_missing` and the published counts, in
  `missing_by_source`, of the spellings V2.3-A1's fourth route brings
  back;
- **per document**: does the settings block name more words, in either
  of the two ways, than the description carries? On the absence side
  this is asked only of a column whose `missing_by_class` publishes a
  declared hole or a pooled remainder — the producer counts every
  absent cell into one of five classes and pools any class below the
  floor into the fifth, so zero in both is a column no declared word
  appeared in. On the kept side no such count exists, because a rescued
  cell is PRESENT and no published number says how many present cells
  were rescued, so it is asked of every column.

**What it costs, at its size, and both directions are stated.** THIS
LOWERS what is checked on an affected column: every obligation of that
column whose measurement is counted over its cells becomes a listing,
and only `position.at` — measured from the file's names and column
count, never from a cell — stays a check. On the free-text witness that
is twenty-one of thirty-one checkable obligations moved, ten checks
left, where eleven used to MISS; on the numeric witnesses forty-three of
fifty-three, ten left, where seven used to miss. **The width is
deliberate and it is wider than the misses:** which obligations the
unattributable cells reach depends on the spelling nobody recorded, so a
rule that moved only the ones that missed on one marker would keep
printing false failures for another. THIS RAISES the report's
truthfulness in the same act: nothing is stated about the measured file
that the description does not support stating.

**And a report may not buy this back by looking at the file.** The split
between what is checked and what is listed is a function of the
description alone (V3.3), so the twin of an affected description carries
the same limit as the table — its holes are written empty and no marker
survives into it, but no reading of the description can know that. Two
files this description cannot tell apart therefore still get one report,
which is V5.1, and that is why the limit cannot be narrowed here.

**What is left open, named rather than found.** A file that really does
violate one of the moved obligations now returns exit code 0 with those
obligations named, because a not-checkable line is not a failure (V6).
The construction is the one V2.3-A2 records: one description, two files
it cannot tell apart, one of them conforming and one not. Both come back
at exit 0. What the report no longer does is claim to have measured
them. Narrowing this needs either a distinct exit status for a run whose
census is short, or a bound on each moved obligation drawn from the
count of unattributable cells — both are owner decisions and neither is
taken here.

**V2.4-A6 The question is asked of far fewer columns, and the two tests
it is asked with are narrowed to what version 5 makes decidable. THIS
RAISES; it lowers nothing** (2026-08-17, owner ruling of that date; the
plan's amendment A-P3-29 is the ruling and this follows it). A5's
routing is not withdrawn and not weakened. What changes is how often
the answer is "the rule cannot be rebuilt", and it changes in four
places:

- **The kept-side head count is deleted, not narrowed.** A5 asks it of
  EVERY column, "because a rescued cell is PRESENT and no published
  number says how many present cells were rescued", and the plan's
  A-P3-26 calls that the wider of its two costs. Contract 5 section 6.4
  proves the settings block carries the whole of the kept side
  (V2.3-A4), so there is no shortfall left for a head count to find.
- **The absence-side head count asks only about words of the PERSON'S
  own.** `n_declared` counts every value named; the two vocabulary
  lists name the ones that were this package's; the difference is how
  many were the person's, and the per-column walk of V2.3-A1 is what
  came back of those. A word of this package's own is written down
  whatever the floor did, so counting it in the shortfall would report
  a deficit that is not one. *(The words "every value named" were true
  of the field and made the subtraction an upper bound, which this
  clause read as exact; `n_declared` counts every DIFFERENT value named
  from 2026-08-17, and V2.4-A9 below is the correction. The walk
  returns keys, which is V2.4-A7's correction.)*
- **The per-column structural test is not asked where the publication
  class empties the source accounting.** On a nothing-publishing column
  `missing_by_source` is empty, `n_missing_blank` is zero and
  `n_missing_withheld` is zero because of the CLASS and not because of
  the cells, and contract 5's C5-N6 makes the two cases tellable apart
  from `role` and `structural_role`. A count-against-count test has
  nothing to read there; asking it anyway called every declared hole of
  such a column unattributable even where the word is in the settings
  block. The head count answers for that column instead.
- **And where it IS asked, a published key is matched to a recovered
  declaration at `settings.declaration_matching`'s own identity** — the
  exact number where both read as one, else the trimmed and folded
  spelling — rather than by exact key lookup. Exact lookup asked a
  narrower question than the producer asked and answered it wrongly
  twice: a declared stand-in comes back from the settings block written
  `-999` while the file wrote `-999.0`, and a word typed `" N/A "`
  comes back as the member `n/a` while the file wrote `N/A`.

~~**The union is still a union, and that is a soundness bound rather than
caution.** The head count counts WORDS and the structural test counts
CELLS. A declaration is matched by its folded spelling, so one declared
word can be worn by several published keys — ` XX ` and `XX` are two
keys of one word — and a head count of keys against a head count of
words can come out level while a second declared word is pooled and
lost. The structural test sees those cells and fires.~~ **The last
sentence is FALSE and is corrected by V2.4-A7 below. The structural test
is not asked at all on a column whose publication class empties its
source accounting, which is the third bullet of this same amendment, so
on exactly the description this paragraph describes NEITHER half fires.
The union is still a union and both halves are still needed; what was
wrong was the claim that one covers the other here.**

**What it costs, measured on the same witnesses A5 was measured on.**

| witness | A5's checks / moved | now |
|---|---|---|
| a rescued word on a column of numbers (route 1) | 10 / 43 | **53 / 0** |
| a rescued word on a label column (route 1) | 10 / 27 | **37 / 0** |
| an invisible character in a named word (route 2) | 53 / 0 | 53 / 0 |
| a cell spelling one of this package's class words (route 5) | 53 / 0 | 53 / 0 |
| a named stand-in number | 10 / 43 | **53 / 0** |
| a built-in word named on a free-text column | 10 / 21 | **31 / 0** |
| the person's own word on a free-text column (route 4) | 10 / 21 | 10 / 21 |
| the person's own word below the floor (route 3) | 10 / 43 | 10 / 43 |
| one word published, one pooled (route 3) | 10 / 43 | 10 / 43 |
| a word of the person's own that the table never held | 10 / 43 | 10 / 43 |

**The arithmetic of that table, written out so that no reader has to do
it and no later sentence can drift from it** (added 2026-08-17 by the
plan's amendment A-P3-38 clause 2, on review item P3-V9-F9). Ten rows:
FOUR reverse — the two rescued words, the named stand-in number and the
built-in word on a free-text column; FOUR stand — route 4's one, route
3's two, and the head count's own over-fire; and TWO never retreated at
all, reading `53 / 0` on both sides, because the format change closed
them a commit earlier. The plan's own table is these ten rows plus the
rescued stand-in number and the two controls, all three of which also
read alike on both sides, so its count is four, four and five. The
plan's prose said the retreat reversed on FIVE rows and is corrected
there.

**The over-fire that stays, and it is the last line of that table.** A
description naming two words of the person's own, of which the table
holds one, reports a gap that is not there. It is the safe direction —
obligations become not-checkable on a file that would have passed — and
closing it needs the description to say which named words the table
held, which is a fact about the table and not about the command line.

**Both of A5's residual risks stand on what is left**, at exactly A5's
wording: a file that really does violate a moved obligation comes back
at exit 0, and the TWIN of an affected description carries the same
limit as the table. They stand on the two limits of contract 5 section
7 and on nothing else, because those are the only descriptions left
that cannot be read back.

**V2.4-A7 The head count counts WORDS on BOTH sides. THIS RAISES the
report's truthfulness and lowers what is checked on one more shape of
description, in the safe direction** (2026-08-17, owner ruling of that
date; the plan's amendment A-P3-34 is the ruling and this follows it;
review item P3-V9-F4).

A6 narrowed the absence-side head count to words of the person's own and
said the difference is "how many were the person's, and the per-column
walk of V2.3-A1 is what came back of those". That walk returns KEYS. One
declared word can be worn by several keys — the same ` XX ` and `XX`
this amendment's own soundness paragraph names — so the comparison put a
count of keys against a count of words.

**The witness the struck paragraph got wrong.** Declare `XX` and `YY`. A
column of numbers publishes twelve `XX` holes and twelve ` XX ` ones; a
free-text column holds twelve `YY` holes and publishes no spelling of
anything, because its publication class permits none. Two keys back
against two words named is no shortfall, and the structural test is not
asked on that column at all — so `unrebuildable_columns` named nothing
and the free-text column reported ELEVEN obligations MISSED against the
table its own description was written from. A6's table row for the
person's own word on a free-text column (route 4), which records ten
checks and twenty-one moved, is true of the witness it was measured on
and was defeated by adding a second declared word to that witness.

**So the recovered side counts DECLARATIONS**, at
`settings.declaration_matching`'s own identity — the exact number where
the spelling reads as one, else the trimmed and folded spelling. It is
the sound direction and counting keys is not: what comes back is a
subset of what was named, so equality means every named word came back,
while a count of keys can exceed the number of words and mask a loss.

~~**The over-fire that stays is now TWO shapes, and the second is this
amendment's own cost.** Beside a description naming two words of which
the table holds one, a description naming two SPELLINGS of one word —
`XX` and `xx`, which the producer folds into one declaration while
`n_declared` counts the two somebody typed — now routes a column whose
reading rule IS rebuildable, measured at 43 obligations moved on a file
that passes every one of them.~~ **The second shape is CLOSED as of
2026-08-17 by V2.4-A9 below, on the condition this paragraph itself
named.** Both were the safe direction in A6's own sense, and both were
to close the day the description says how many DECLARATIONS were named
rather than how many values were typed; that day came, so one over-fire
stays and it is A6's.

**V2.4-A8 A stand-in number the description's own verdict reads as a
hole is not pinned to data. THIS RAISES; it lowers no obligation**
(2026-08-17, owner ruling of that date; the plan's amendment A-P3-35 is
the ruling and this follows it; review item P3-V9-F5).

V2.4 pins the measurement side to blankness, and V2.4-A4 clause 2
narrowed the pin once already: a cell is absent when it is empty, or
when it wears a spelling the description ITSELF publishes as the source
of its holes. The reason given there is the reason here. The producer
read every such cell as a hole in every column of the table it
described, so counting one as data measures the file under a rule its
description was not written under.

**That reason reaches the third way a cell becomes absent, and the pin
did not follow it.** Contract 5 section 3.2 way 3 publishes, per column,
a stand-in candidate with its verdict, its reason and its occurrences.
A 180-row column of 168 ordinary decimals and twelve `-999` cells, whose
description records `-999` as `read_as_missing`, reported SEVENTEEN
obligations MISSED against the table it was written from — both presence
counts, both distinctness counts, three other counts, seven ladder rungs
and all three moments — with the numbers the wrong reading produced
printed beside them.

**Nothing is CONSULTED, which is why this is a repair and not a
relaxation.** The pin is not applied to a stand-in number some column of
the description reads as a hole; the producer's own per-column sentinel
rule then answers, under the settings the description was written with.
Same rule, same cells, so the file the description came from agrees
exactly, and V2.1 is met as it is for every other measurement: no
recount is re-implemented here and `sentinel_verdicts` is not read a
second time.

**Where pinning to blankness is still required, and why.** Residual
R-P2-13 is the whole of the reason the pin exists: a generated value can
legitimately BE the text of one of synthtwin's own markers, and no file
may be failed for colliding with this package's vocabulary. That reason
reaches every cell the description passes no verdict on, and those stay
pinned: every non-blank built-in missing TEXT on every description, and
every stand-in NUMBER on a description no column of which reads it as a
hole. The blank spelling stays unpinned, because a blank is absent under
both readings.

**What it costs.** R-P2-13's own shape on the third class of marker: a
twin whose generated numbers include a stand-in the description settles
as a hole can have those cells counted as holes here. It is bounded by
the cells wearing that number, it needs the producer's outlier and share
rules to fire on the twin's own values, and it is the exposure the
GATE side has always carried, because the file's own description was
never pinned.

**V2.4-A9 The head count's second over-fire is closed at the producer,
and one of the two over-fires A6 and A7 recorded is gone. THIS RAISES
what is checked on a class of description that was being routed away; it
lowers nothing** (2026-08-17, owner ruling of that date; the plan's
amendment A-P3-37 is the ruling and this follows it; review item
P3-V9-F7).

A6 reads the shortfall as "`n_declared` counts every value named; the
two vocabulary lists name the ones that were this package's; the
difference is how many were the person's". That subtraction was an UPPER
BOUND and this method read it as exact. `n_declared` counted keystrokes:
`--missing-value n/a --missing-value " N/A "` names one value twice, the
producer folds the two spellings into one declaration on the way into
`built_in_texts` and did not fold them on the way into the count, so the
document said two named and one member — and the shortfall read as one
word of the person's own that nobody typed. **Measured: ten checks left
of fifty-three and forty-three obligations moved to NOT CHECKABLE, on a
file that passes every one of them and whose reading rule is recovered
exactly.**

**Nothing on this side could have repaired it.** From the description
alone, `n_declared: 2` beside one vocabulary member is the same
description as one written by `--missing-value n/a --missing-value
WOMBAT`. The count and the lists were answering two different questions,
so the repair is the producer's: contract 5 C5-18 is amended to count
DIFFERENT values, at `settings.declaration_matching`'s own identity —
the same identity A7 made this method's recovered side count at. The
subtraction above is now exact rather than a bound, which is what this
clause always assumed of it.

**So A7's "TWO shapes" is one shape.** The over-fire that stays is A6's:
a description naming two DIFFERENT words of the person's own, of which
the table holds one. Whether the second was ever in a cell is a fact
about the table and no count taken off the command line settles it. The
one that goes is A7's own cost — two SPELLINGS of one word — and A7's
closing sentence named this as the condition for it: "both close the day
the description says how many DECLARATIONS were named rather than how
many values were typed."

**V2.4-A10 A built-in missing word a column publishes as the source of
its holes is not pinned to data either, and this corrects A4's own
sentence rather than adding to it. THIS RAISES; it lowers no
obligation** (2026-08-17, owner ruling of that date; the plan's
amendment A-P3-39 is the ruling and this follows it; review item
P3-V10-F4).

**THE CLAUSE CONTRADICTED ITSELF AND ONE HALF IS WRONG.** A4 clause 2
says a cell is absent to the measurement side when it is empty "OR when
it wears a spelling the description ITSELF publishes as the source of
its holes", and gives the reason in terms: the producer read every such
cell as a hole in every column of the table it described, so counting
one as data measures the file under a rule its description was not
written under. A8 repeats that reason and then names, among what stays
pinned, "every non-blank built-in missing TEXT on every description".
Both cannot stand. `missing_by_source` is where a column publishes the
spelling its holes wore, and a built-in word can be a key of it like any
other. **The first half is the one that stands.**

**MEASURED, on the plainest run this product has.** One column of sixty
numbers and twelve literal `n/a` cells, profiled with NO options at all.
The description publishes `n_present: 60`, `n_missing: 12` and
`missing_by_source: {"n/a": 12}`. Validating that exact CSV against that
exact description re-described it with `n/a` pinned to data, measured
seventy-two present and zero missing, and reported TWENTY-EIGHT
obligations MISSED at exit 3 — both presence counts, both distinctness
counts, `n_not_numeric`, eleven ladder rungs, three moments and the
rest. It now reports none, and both presence counts are HELD rather than
merely unreported.

**THIS IS NOT R-P2-13's CORNER, and the finding's own words are why.**
It happens on the SOURCE table, on the DEFAULT command, with nothing
typed and nothing generated. A generated value colliding with this
package's vocabulary is the residual the pin exists for; a spelling the
description names as the source of twelve of its own holes is the
description speaking.

**WHERE THE PIN IS STILL REQUIRED, and this is the narrower boundary
proved rather than asserted.** A built-in text stays pinned on a
description no column of which publishes it as a hole source. On such a
description the pin cannot move a verdict on the file the description
was written from, and the argument is structural rather than empirical.
For the pin to reach a verdict on a column, that column's own
description must publish its split (V2.4-A3): every absent cell of it is
blank, or is named by a key of `missing_by_source`. A cell the built-in
table made absent is not blank, so it has to be named by a key — and a
named key is exactly the publication this clause reads. So the two cases
are exhaustive: either the spelling is published, and it is unpinned,
or the column pools it and V2.4-A3 takes that column's verdicts from
the file's own description instead. What is still pinned, and asserted
to stay pinned: every built-in missing TEXT on a description no column
of which names it, every stand-in NUMBER on a description no column of
which settles it, and the blank spelling on every description, because a
blank is absent under both readings.

**WHAT IT COSTS, and it is R-P2-13's own shape on the first class of
marker.** A twin holding a generated value that collides with a built-in
word the description publishes as a hole source can have those cells
counted as holes here. It needs the description to publish that word, so
the table it was written from wore it at or above the publication floor,
and it needs the twin's own invention to land on that spelling in some
other column whose split is published. It is bounded by the cells
wearing that word, and it is the same exposure A-P3-29 took for a
built-in word the person declared and A8 took for a stand-in number,
said now about the one route those two left standing.

**WHAT IS NOT CLOSED, at its size.** The two presence COUNTS are read
over the weaker publication of V2.4-A3's second half — `missing_by_class`
says how many holes are non-blank without saying what they spell — so a
column whose non-blank holes are pooled below the floor still has those
two counts measured by blankness. Sixty numbers with six `n/a` cells and
six `N/A` cells at the default floor is that column: neither spelling
reaches eleven, the class map still names twelve non-blank holes, and
the two presence counts MISS while every obligation that needs the
spellings falls back to the file's own description. Two obligations,
never more; the plan carries it as residual R-P3-11 and the suite pins
its size. Closing it would reverse A-P3-5 clause 1, which bought the
weaker question deliberately, and that is an owner decision and not a
repair.

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

**V3.5-A1 Two more are decided that way, and the count above is now
six** (2026-08-15, review item P3-V7-F4; the plan's amendment A-P3-18
clauses 3 and 4 are the ruling and this follows it). Both were found by
the corner comparison V4.2-A1 builds, and each is the same shape as the
four above — an obligation the description itself empties:

- `distinct.n_distinct` and `distinct.n_distinct_folded`, where the
  spelling envelope V4.1 draws reaches from ONE value up to every
  present cell. Forced integers under a single `plain` key are the
  case: all the plain cells together supply one identity, so a column
  that has collapsed onto one repeated value lands inside the bar and
  so does every count above it;
- `offsets.earliest` and `offsets.latest`, where the publication floor
  held that END's own offset back and the description publishes the
  withheld label in its place. The description then names no offset for
  that end, and the comparison that stood asked whether the measured
  file's OWN floor had suppressed the same end — a fact about how many
  rows shared an offset rather than about the file's dates.

**V3.5-A2 And a count the description names only PART of is a window,
not a point** (2026-08-15, review item P3-V7-F2's battery; the plan's
amendment A-P3-18 clause 4 is the ruling and this follows it). The
publication floor pools every numeric form fewer cells wear than the
floor into one withheld key and publishes no count for any of them, so
a cell in that pool has no published form at all and a twin of that
description may give it any form the description permits — `plain`
among them. `styles.published.<form>` therefore owes AT LEAST the
published count and AT MOST that count plus the pool, wherever the pool
is not empty. The exact comparison that stood here refused the shipped
generator's own twin — eleven plain cells published, forty-five written
— on every description of the corner battery whose style map the floor
had pooled. Where the pool IS empty the count is exact, which is the
ordinary case and unchanged, and the window keeps its teeth in the
direction that matters: the published cells are owed, so a file writing
fewer of the named form than the description names still MISSES.

**V3.5-A3 And a SEVENTH way, which is a route rather than a named
entry** (2026-08-16, owner ruling of that date; the plan's amendment
A-P3-26 is the ruling and this follows it). The six above are each one
fact whose failure set the description empties. This one empties no
failure set: the obligation could be falsified by a file, and what the
description does not carry is the RULE for reading that file back the
way it was read when the description was written (V2.4-A5). The entries
it decides are therefore named by a walk and not by a list — every
obligation of an affected column that is counted over its cells — and
`position.at` is the only one of that column's entries left standing,
because it is measured from the file's names and column count. The
condition is a condition on the loaded profile, exactly as V3.1 requires
of a predicate, and the walk that names the listings is the same walk
that would have named the checks, so the two halves of the split cannot
drift apart.

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
  whose published facts cannot supply as many different spellings as
  its `n_distinct_by_occurrences` names groups. Then `n_distinct`,
  `n_distinct_folded` and `n_distinct_by_occurrences` are REPORT-ONLY
  for that column, and nothing else is.

  **The supply is method G9.4's, band by band and all three at once**
  (review item P3-V6-F1, plan amendment A-P3-14). The published cells
  divide between the three alphabet bands by the column's own two
  counts (G9.5 step 4): `n_all_digits` in the figures,
  `n_code_alphabet - n_all_digits` in the code alphabet, and the rest
  outside it. Every cell of one group carries the same spelling, so a
  band can hold no more groups than its own cells have room for and no
  more than its domain can spell over `[min_length, max_length]` —
  where the domain is the band's own alphabet under G9.1's positional
  rules, or, where `all_whole_numbers` is published and every present
  cell reads as a number the format holds, the narrower whole-number
  family G9.6 fixes for that band. The corner is the three bands
  falling short TOGETHER, not one of them falling short alone.

  **Every number in it is taken in the direction that keeps checks**:
  supply is an upper bound on what the construction writes and demand a
  lower bound on what it is asked for, so the corner is claimed only
  where no packing of any kind answers the description. That direction
  is stated because it was once taken the other way: the arithmetic
  this replaced summed `alphabet ** L` with the alphabet read off one
  published count, which is a domain this product never writes from,
  and the three checks it took off a column let a file whose
  identifiers had collapsed to one repeated value receive a passing
  report.

  **The domain is the FAMILY's above one character too, and a band is
  asked whether it can cover its own cells** (review item P3-V7-F2,
  plan amendment A-P3-18 clause 1). The rule above was written for the
  one-character families and left the wider ones counted as strings of
  the band's alphabet under G9.1's positional rules alone — 8,460
  two-character values in the widest band against the 2,538 its own
  family holds — so a producer-derived column of 2,539 such values was
  called feasible while the construction necessarily repeated. What is
  counted is the families G9.6 actually writes those cells from: the
  band's ordinary-text walk, and the ordinary-number family of G9.5
  step 3 where the description gives the numbers class a cell. A class
  the description gives no cell to writes nothing; a column publishing
  cells too large to hold or notations that conflict with themselves is
  given a supply nothing can exceed, since this document does not count
  those widths and keeping its three checks is the cheaper error.
  **And the three bands falling short TOGETHER is not the only way to
  fall short**: a band answering for `cells` of them needs at least
  `ceil(cells / widest group)` different spellings, which is G9.4's own
  sentence and the same one the free-text refusal reads, and where its
  own domain cannot supply that many no packing of the other two
  repairs it. The summed reach can miss that, because it lets the
  smallest published groups answer for every band at once.
- **datetime-offsets-withheld** (P2-D9): a datetime column whose
  `utc_offsets` map is the single `(withheld)` key. Then `utc_offsets`,
  both endpoint offsets and `datetimes_read_at` are REPORT-ONLY, and
  the two ends are not. **A map naming real offsets whose own earliest
  or latest END is withheld is a different shape and not this corner**:
  it is V3.5-A1's listing for that one endpoint, and every offset the
  description does name is still checked.
- **label-variants-short** (P2-D6): a label column whose published
  variants and withheld-variant multiset do not settle the published raw
  `n_distinct`. Then raw `n_distinct` falls to the G12.7 envelope.

  **AND THE FOLDED COUNT IS NOT ITS, WHICH IS WHY A CORNER IS ASKED PER
  FACT** (review item P3-V8-F3, plan amendment A-P3-25 clause 2). A
  corner authorizes the facts its own passage names, and these three do
  not name the same ones: the identifier corner names both counts and
  the multiset, G12.8 names the raw count and says "the same over the
  folded identities", and this one names raw `n_distinct` and nothing
  else. Folding is not a spelling question — however few spellings the
  published variants supply, a label column's folded identities are
  settled by its published levels and the construction meets that count
  exactly — so a validator asking one field-blind question for both
  counts hands this envelope to a fact it does not govern. It did: a
  description publishing folded 2 against a supply of 3 printed the bar
  `2 (between 2.0 and 3.0)`, and a file holding three folded identities
  where the description publishes two was reported an AUTHORIZED
  DEVIATION instead of a MISS.

  **A withheld-variant KEY is an occurrence count and its VALUE is how
  many spellings covered that many rows each** (review item P3-V7-F3,
  plan amendment A-P3-18 clause 2), so the rows such an entry covers are
  `key x value`, exactly as G12.7 writes it. Adding the value alone
  makes a level its withheld variants covered exactly look short, which
  invents one more spelling for it and puts the EXACT bar on a count the
  construction cannot reach. `S` is settled by the published level
  blocks alone, so both writings compute the same number and the suite
  compares them directly.
- **numeric-spellings-short** (P2-D6): a numeric column whose permitted
  spellings do not settle the published raw or folded distinctness. Then
  those fall to the G12.8 envelope.

  **The envelope is two-sided and the corner is asked in both
  directions** (review item P3-V7-F4, plan amendment A-P3-18 clause 2).
  G12.8 fixes `min(supply, n_distinct) <= n_distinct(twin) <=
  max(supply, n_distinct)`, so a column whose own permitted spellings
  force MORE identities than it publishes owes the envelope exactly as
  one that falls short does. Asking only whether the supply fell short
  put the exact bar on a floored style map naming fifteen leading-zero
  cells against nine published values, and reported the shipped
  generator's own twin MISSED.

  **And the supply this document can compute is a PAIR, not a number**
  (A-P3-18 clause 5 as corrected by A-P3-25 clause 3). G12.8's supply
  has TWO summands and both are read here. The first is the numbers
  class: each (value, style) group of it supplies one spelling where the
  style is `plain` and its own cell count otherwise. The second is every
  OTHER class — `min(its cell count, its share of the budget in G6.5)`,
  where the budget is allocated from the published count over the four
  class counts in G6.5's fixed order, one spelling to each non-empty
  class and the remainder offered in that order. That second summand is
  arithmetic on published numbers and needs nothing V1.4 keeps out, and
  it is counted at BOTH ends. **Leaving it out is what made the bar
  vacuous**: twenty whole numbers written one way beside two cells that
  are not numbers read a floor of ONE, so the envelope reached from one
  value to every cell of the column, both distinctness obligations
  became listings under the rule below, and a file one different value
  short of the published count was told nothing was missed.

  The published style map fixes the style half of the first summand
  exactly and says nothing about the other half — how many different
  VALUES the plain cells carry is decided by the value construction of
  G5 and G7, which V1.4 keeps out of this module and which this document
  does not rewrite. That is the whole of what is unknowable here. So a
  FLOOR is taken, where all the plain cells carry one
  value between them, and a CEILING, where each carries its own and no
  more of them than the published count of different values; a withheld
  style count is not a style and is counted with the plain cells at the
  floor and at its own cell count at the ceiling. **The envelope this
  method draws therefore HOLDS the generation report's and does not
  equal it**, and no sentence here may say otherwise until that
  construction is written out. **How far it fails to equal it is stated
  rather than left open**: a file one different value short of a count
  the generation report pins is inside this envelope, so it is an
  AUTHORIZED DEVIATION here and not a MISS.

**And a corner's envelope that admits every count is a LISTING** (V3.4,
V3.5, and A-P3-18 clause 3). Where the floor above reaches one value and
the ceiling reaches every present cell — forced integers under a single
`plain` key are the case — the bar licenses a column that has collapsed
onto one repeated value and every count between that and the whole
column. Such an entry is not a check that happens to be generous; it is
a check that cannot fail, which V3.4 forbids by name, so it is a listing
with one sentence saying why and the census counts it where it counts
every obligation nothing in a CSV settles.

**V4.2 The classifier is written from this document, not imported.**
The generator decides the same question from its own text, and the two
writings are compared in the suite by BUILDING THE TWIN: a description
whose twin misses a fact the classifier claims no corner for turns the
green direction red, and — for `identifier-infeasible` — a description
whose twin holds every published value while the classifier calls it a
corner turns a battery red. A shared design error needs the same
mistake written twice from two texts.

**What that comparison does and does not reach, stated at its real
width** (review item P3-V6-F1, plan amendment A-P3-14 clause 3). This
paragraph said the two were compared "over every producer-battery
description and every frozen conflict case, and any disagreement is
red", and that was wider than what any test did. What the green
direction catches is ONE side: a corner the generator needs and the
classifier withholds shows up as a MISSED verdict on a conforming twin.
The other side — a corner claimed where the generator needs none — is
SILENT there, because the twin passes either way while three checks
disappear from the report, and that silence is how a false identifier
corner survived a green suite. It is now asserted directly for
`identifier-infeasible` against the shipped generator's own cells, over
a battery reaching all three bands, both whole-number readings and four
capacity boundaries taken from both sides. **For the other three
corners the reverse direction was still unasserted when this paragraph
was written**, and V4.2-A1 below is what closed it; nothing above may be
read as having claimed it earlier.

**V4.2-A1 The comparison is now BUILT, over every corner, and here is
what it asks and what it reaches** (2026-08-15, review items P3-V7-F2,
F3 and F4; the plan's amendment A-P3-18 is the ruling and this follows
it). Patching the corners one at a time is what failed: the repair the
paragraph above records introduced two of the three round 7 recorded,
all three of one shape — the validator's independent arithmetic disagrees
with the generator's, and the validator rejects or mis-classifies files
THE SHIPPED GENERATOR ITSELF WRITES. So the comparison is built, in
`tests/test_p3v7f2_corner_parity.py`, over a producer-built space of 219
descriptions reaching all four corners, and it asks four questions:

- **the shipped generator's own twin is measured by the shipped
  validator**, and no fact a corner governs may be MISSED where the
  GENERATION REPORT's own account says the twin holds it — exactly, or
  inside the envelope the ratified plan authorizes. An approximation
  OVERRIDES a deviation in that reading, because the generator files
  both for a fact it could not meet exactly but whose authorized bound
  its own cells landed inside, and such a twin is conforming;
- **where no corner is claimed, the two writings must agree that the
  description PINS the count**: this method puts the exact bar there,
  and the generation report says the same thing in the only words it
  has — the two ends of the bound it prints for that fact meet on the
  published number;
- **the identifier supply is compared family by family**, by walking
  the shipped generator's own index map and counting the spellings it
  actually writes, at every band and both whole-number readings;
- **and every distinctness bar the space prints must be one some file
  can miss**, shown by BUILDING those files rather than by argument.

**What it does not reach, at its real width.** The first question is
only as strong as the generation report is honest: a fact the generator
neither meets nor mentions is invisible to it. **A fact that report is
SILENT about is no longer skipped, though** (review item P3-V8-F3, plan
amendment A-P3-25 clause 2): the report names every fact its
construction could not meet exactly, so silence means the generator
PINNED that fact, and the second question now asks whether this method
pinned it too. Skipping it is what let G12.7's raw-only envelope sit on
a label column's folded count while the comparison walked past the entry
where the bar had been lowered. The third walks each
family's index map, which is affordable at one and two characters and
truncated above that, so wider families are compared at their published
arithmetic and not by enumeration. And on a column of NUMBERS the two
envelopes are compared by CONTAINMENT rather than equality, for the
reason V4.1 gives: this method can bound G12.8's supply from both sides
and cannot compute it without the value construction of G5 and G7.
**That containment is narrower than it was** (A-P3-25 clause 3): every
class but the numbers class is settled exactly at both ends now, and
what remains is measured — a file one different value short of a pinned
count is an AUTHORIZED DEVIATION here, and the battery asserts exactly
that rather than describing it.

**V4.2-A2 A number the description states in FIGURES is read as
figures** (2026-08-15, review item P3-V8-F5; the plan's amendment
A-P3-25 clause 1 is the ruling and this follows it). The keys of a
multiplicity map are row counts written in base ten, and the profile
contract admits them as digits and reads them with whole-number
arithmetic. This method reads them the same way. A reader that answers
in binary64 is exact only below nine quadrillion, and a key one row
short is one group MORE when a band's cells are divided by it: ten
groups of `9007199254740993` rows, which ten one-character figures cover
exactly, came back needing eleven, and the refusal of V9 stopped the run
on a description a twin exists for. This is the fourth site of that
class, so the guard for it follows the KEY rather than any one rule —
every field the contract annotates as a text-keyed mapping, from where
its keys are read out through every call that carries them, refusing
`parse_number`, `float`, `round` and `complex` and permitting `int`,
which on decimal text is exact at every size.

**V4.3 The G12 refusals are NOT corners.** They refuse GENERATION,
so no conforming twin exists for such a profile at all. A validate run
on one is a catalogued REFUSAL (V9), never a verdict and never a pass —
treating them as corners would launder an impossible obligation into a
passing report.

---

## V5. The disclosure gate: what a report may say about the measured file

**V5-A1 The one thing this section stops promising, and it is named
before any rule below is read** (2026-08-14, owner ruling; the plan's
amendment A-P3-13 is the ruling and this follows it). Every rule in this
section was written to hold against two different readers, and only one
of them is still in scope.

- **The reader of ONE report, who may not hold the measured file.** A
  quality report travels: it is written to a file, printed on a screen,
  and sent to whoever is deciding whether to trust a twin. Everything
  below is about that reader and **binds exactly as written**. What the
  report states, on any surface, stays inside what `synthtwin profile`
  run on the measured file would publish; no measured value, no string
  of that file, and no count its own description pools ever appears, in
  the report, on the screen, or in a refusal (V5.4, V9).
- **The person who submits DESCRIPTIONS OF THEIR OWN and runs the check
  again, watching which verdicts change. THIS SECTION NO LONGER
  DEFENDS AGAINST THAT PERSON.** Such a sequence of runs can narrow a
  number one report withholds — the count of a sub-floor group, the
  count of cells a form is written in, the header of a file the
  producer refuses — and no rule below is written to stop it.

**On whose authority, and on what reasoning.** The owner's, ruled
2026-08-14, with the consequence stated and accepted; no review verdict
and no implementer's judgment stands behind it. The reasoning is that
running this check on a file requires holding that file: `validate`
answers questions about a file whoever runs it already has in hand,
and a question they could settle by reading the file is not a question
this method has to refuse. **What that reasoning does NOT reach, so it
is not extended past it:** the report is a separate artifact that
leaves the person's hands, and one report is read by people who hold
nothing. That is why the first reader above keeps every rule.

**What this costs, said as a cost.** A number a single report withholds
is no longer a number this method claims cannot be found; it is a
number this method does not print. Anyone who could run the check
already had the file, so nothing is disclosed that was not already
held — but the guarantee is narrower than the words this document used
to carry, and a reader who took those words for a bound on what the
tool can be made to reveal was reading more than is now promised.

**Where this changes a rule below, it says so at that rule**, and every
clause that was written to defeat the second reader alone is corrected
in place rather than left to be reconciled: V5.3's second sentence and
V5.3-A2 are the two, and V5.3-A2's rule is withdrawn. Nothing else in
this section moves, and no rule here may be re-derived from the
withdrawn promise.

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

**V5.1-A1.2 And that stopping place is reached THROUGH the reader, not
around it** (2026-08-15, review item P3-V4-F3 carried; the plan's
amendment A-P3-20 is the ruling and this follows it). V5.1-A1.1 made the
reader's own refusal choose the report so that two files the producer
refuses with one sentence cannot reach two reports. A zero-row
description reached none of that: the branch on the published row count
RETURNED before the reader was called, and the report was built on a
walk of the file's characters. Against a headed zero-row description,
`column_1` over `1,2` and `other` over `1,2` are one ragged refusal to
the producer and drew 8 HELD / 1 MISSED against 5 HELD / 4 MISSED, and
`header.names` reported HELD about a file no reading of which finishes.

**So the degenerate report has exactly two routes and the reader has
spoken on both.** Its own NO-DATA refusal, which is what the conforming
file draws, and a reading that finished, which is a file holding rows
against a description asking for none. Every other refusal reaches the
report or the refusal that word chooses, exactly as it does against a
description publishing rows. The header line is still read out of the
file's own characters on the no-data route, because the reader refuses
before it hands any name back and there is nowhere else to get one —
but that reading no longer chooses anything, and the residual it leaves
is the one the plan's amendment A-P3-7 clause 3 already rules on, at the
size stated there.

**V5.2 Why the submitted profile's floor is not the envelope.** The
producer routes a two-valued numeric-looking column to a label role
BEFORE it reaches the numeric path, and withholds both labels when they
sit below the floor. A crafted numeric profile would walk a naive
validator straight past that routing and print the measured mean of a
column whose every published fact the producer would have withheld. So
the gate consults the FILE's own description, which V2.1 already builds.

**V5.3 What the gate governs: the verdict as well as the value.** A
within-bound or missed line stated against a candidate value is itself a
measurement-derived statement, ~~and repeated candidate profiles would
binary-search a number the file's own description withholds~~ — **that
second reason is withdrawn by V5-A1 above and this clause stands on the
first, which is enough on its own: a verdict printed in one report is
something that report says about the measured file, and one report is
read by people who hold nothing.** So where
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
  the pool below it is counted in `n_missing_withheld` (V2.3-A3), so
  V2.4-A3 above governs it and no ruling may excuse it;
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
description at all — **which is no longer a bound this document owes,
and is written here as a fact rather than as a promise, for the reason
the next paragraph gives.**

**WHAT SUCH A BOUND OWES IS NARROWER FROM 2026-08-14, AND V5-A1 IS THE
RULING.** The half of it that mattered — neither subcheck prints a
measured count — stands unchanged and is what a reader of one report is
protected by. The half that was about somebody submitting one
description after another is no longer an obligation any ruling here
owes, because no rule in this section defends against that person any
more. What the clause above used to conclude from `styles.spelled`
taking no number — that such a person could get nothing through it — is
therefore struck as a promise and left standing only as the fact it
rests on, so that nothing here can be read as a guarantee about that
person and no future ruling has to establish one. Which of the six
FORMS a cell wears is published and floored, and stays gated.

**V5.3-A2 The bound is a property, so it is measured; and one of the
two did not have it** (2026-08-14, review item P3-V4-F2; the plan's
amendment A-P3-10 clause 1 is the ruling and this follows it).
`styles.canonical.<form>` compares its recount of non-canonical cells
against a count the SUBMITTED description names, so the verdict flipped
at exactly that recount and eleven candidate descriptions read the
hidden number off it — which this section was written to stop when it
was written, and no longer is (V5-A1 above withdrew that reader in
2026-08-14, after this clause was made) — through the subcheck a ruling
had exempted. **So a recount that a ruling has put
outside the envelope enters a verdict only at the publication floor's
own resolution**: rounded DOWN to a whole number of `small_cell_floor`,
which is the resolution below which the producer names no count at all,
and downward so that a MISSED is never a file the ceiling has not
actually been exceeded by. What a sweep can then locate is the
floor-wide block and not the count. The plan's amendment states the
residual at its size, prices the teeth this costs — a file less than one
floor over its licence is no longer missed there — and shows why teeth
at one cell and a bound better than the exact count cannot both be had.

**THIS CLAUSE'S RULE IS WITHDRAWN, AND V5-A1 ABOVE IS THE RULING**
(2026-08-14, owner ruling; the plan's amendment A-P3-13 clause 2). The
whole of A2 is a defence against the second reader V5-A1 puts out of
scope: the recount is read exactly again, `_at_the_floors_resolution` is
deleted rather than left unused, and a file ONE cell over its licence
MISSES again. **This RAISES the subcheck by the exact amount A2 priced
and lowers nothing**: the only files whose verdict moves are files
between one cell and one floor over a licence, and every one of them
moves from HELD to MISSED, which is the direction that cannot excuse a
file. Round 5 measured that A2 did not even buy what it cost — the
publication floor is itself a number the submitted description chooses,
so sweeping `small_cell_floor` from 11 upwards read the exact count back
off the rounded comparison — and that is recorded here as fact rather
than as the reason: the reason is the ruling. **What is still true of
this subcheck** is the half V5.3-A1's bound rested on: it prints no
measured count on any file, so one report carries the licence and the
verdict and never the recount. **To reverse**, restore the rounding
function and the one call, which costs teeth at every count inside a
floor-wide block and buys the block-resolution bound back against a
person who holds the file anyway.

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

**V6.1-A1 Where the first two definitions both fit, HELD is the one
taken: a file holding the description's own value has met the exact
obligation, whatever its window says. THIS RAISES; nothing moves to a
worse verdict** (2026-08-17, owner ruling of that date; the plan's
amendment A-P3-40 is the ruling and this follows it; review item
P3-V10-F5).

**THE TWO DEFINITIONS OVERLAP AND NOTHING SAID WHICH WINS.** HELD is
"the exact obligation was met" and WITHIN-BOUND is "an APPROXIMATED fact
inside both ends of its cited G12 envelope". A file can satisfy the
first and fail the second, because none of these windows is a margin
around the published value: each is worked out from the description and
the size of the column, so a window can lie wholly to one side of the
value it is printed beside, and G12.4 ordinarily does at the top of a
date ladder. The implementation read the verdict off window membership
alone.

**MEASURED, on the shipped source table against its own description.**
`date-ladder.p99` printed "the description asks for: 2024-12-24 / the
file was found to hold: that same value" with MISSED above it, because
that rung's window ends a day earlier. Four rungs of that one table said
it — `recorded_on.p99` and `seen_on.p90`, `p95` and `p99` — and the
cardinality envelope of a column of dates said the same thing in
numbers on two more: "asks for 84 (between 106.0 and 240.0) ... found
84.0: MISSED". Six of the seven obligations that table missed against
its own description were this one line, printed six ways.

**THE VERDICT IS WHAT IS REPAIRED, NOT THE WORDING.** A page that says a
file holds the value and has missed the obligation to hold it is not
strict; it is a page no reader can act on, and the earlier repair of
2026-08-15 made it legible without making it true. So exact equality is
tested first on every envelope this method draws — the numeric ladder,
the moments, the date rungs, the two datetime cardinality counts and the
text-shape facts alike — and where the measured value equals the
published one the verdict is HELD.

**WHAT THE WINDOW STILL SAYS.** Where the window does not reach the
published value the line still says so, in the same words and under the
same verdict line, so that a reader holding the twin's report and this
one sees the same fact about the same window on both pages. What
changes is what the window DECIDED, not what it is.

**WHAT DOES NOT MOVE.** A file holding anything other than the published
value is settled by its window exactly as before, inside it and outside
it. Nothing moves to a worse verdict, no obligation leaves the census,
and the counts that shift are HELD upward and WITHIN-BOUND downward by
the same number.

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

**V8.3-A1 The walk is TOTAL OVER THE PREDICATES, not over the ordinary
one** (plan amendment A-P3-17 clause 3). V3.1 makes an entry's identity
a profile predicate, a column and a subcheck, and owner decision 7 ships
four predicates: a headed description, a headerless one, and the two
degenerate zero-row forms. A walk over ordinary fixtures alone is total
over ONE of the four, and calling it total over the shipped table is the
claim this specification exists to refuse. So both halves of V3.1's
identity proof — which registry fact each site binds, and that each site
can be made to MISS — run over every predicate the validator ships. The
two zero-row forms file fifteen executable subchecks between them, every
one of them carries an edit that names it, and the walk asserts that the
predicates reach a subcheck the ordinary fixtures do not, so that
widening it is measured rather than asserted.

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

**And every one of them is a catalog entry** (plan amendment A-P3-23,
review item P3-V7-F7). The G12 message was built privately inside the
validator, so the catalog's rules about what a sentence a person reads
must contain did not reach it and no test pinned its shape. It is
`errors.no_twin_of_this_description_exists` now, held to the same rules
as every other refusal, pinned clause by clause for each of the four
names method G12 fixes, and reached by running `synthtwin validate` on
a description the shipped producer wrote.

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

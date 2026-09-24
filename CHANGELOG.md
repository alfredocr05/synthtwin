# Changelog

All notable changes to synthtwin are documented here. The format follows
Keep a Changelog; versions follow SemVer (0.x until the end-to-end product
exists).

## [Unreleased]

### The answer paths, and the population census (stage 3's review, floor items 1-4, 2026-09-23)

**Stage 3's one review round returned REJECT on all four passes. These
are the four items of the floor pass that are routes by which the command
did something the person did not ask for, or counted a population it did
not have.** Each has the reviewer's own reproduction as a test and a
mutation that puts the old behaviour back.

**1. AN IDENTIFIER ANSWER LANDED ON THE WRONG COLUMN.** The column names
in a questions file are the names of the reading that WROTE it, and an
answer that changes the reading gives those names to different columns.
Measured: a header of `column_2,column_1` over 360 records whose first
field held twelve repeating subject codes, with `names` answered for the
first row and `identifier` for `column_1` -- the FIRST field under the
reading in force -- reached all three writers with the declaration on the
SECOND field, counted 350 people and published the twelve real subject
codes with counts of thirty, where declaring the field the person meant
refuses the table as thirteen people. **Refused rather than mapped**
(`cli._answers_that_change_the_reading`,
`errors.answers_change_the_reading_and_name_columns`): `column_1` is a
column name under both readings of that file, so nothing can tell which
was meant. Two of the three file questions move a column name -- which
row holds the names, and which character separates the columns -- and
either beside a `code`, `identifier`, `measurement` or `decimal-comma`
answer is refused, with the question named, the columns named, and two
runs to do it in. An answer that AGREES with the option typed is the
reading already in force and is not a change. The delimiter half is not
in the review: it is the same defect one question along.

**2. AN EXPLICIT `first-record` ANSWER WAS IGNORED.** It was called "the
reading that already stands", which it is only while nothing else moves.
Measured: a first record of `12,HEADER|LABEL` over 360 records of
`i,code{i}|other{i}`, answered `first-record` and `vertical-bar`,
described 360 records and published `12,HEADER` and `LABEL` as two column
names, where `--first-row data --delimiter '|'` keeps all 361 records and
names the columns `column_1` and `column_2`. Both answers are applied
now, in both directions: a typed `--first-row names` answered
`first-record` gives the record reading, because the file is the newer
statement.

**3. THE POPULATION CENSUS READ AN UNFINISHED COLUMN.** It asked
`taxonomy.split_missing`, the FIRST of five passes that decide what a
column holds, and stopped there. Measured on five paddings of twenty
readings to a hundred lines, one per pass: `-999` declared with
`--missing-value=-999`, `-999.0` declared the same way, `-999` with
nothing declared, `9999-12-31` in a column of dates and `-999 mg` in a
column of amounts. Every one cleared the hundred-row floor as a hundred
rows, and every one produced a description recording twenty present cells
and eighty missing. **One reading, in one place:** `profile_column`'s own
prologue is now `taxonomy._read_the_column`, the census asks it through
`taxonomy.present_spellings_after_the_rules`, `taxonomy.Declarations`
carries the four column declarations down to it because each of them
changes what a column holds, and a test holds the census's surviving
spellings equal to the description's `n_present` on all five paddings. All
five files are refused now with nothing written, and the refusal says what
"holds no value" covers instead of naming blanks alone.

**4. AN IDENTIFIER DECLARATION SILENCED THE PERSON QUESTION.** A
declaration is only an answer to "who are the rows about" when it settles
that, and an identifier different on every row settles nothing: it names
a ROW. Measured: 1,196 visits over twelve people with a unique-per-row
`visit_id` declared left `person_columns` correctly EMPTY -- the
population was counted in rows -- while the declaration silenced the
question, so the run published the twelve subject codes, asked nothing,
and printed neither the population notice nor the notice that it had
counted rows. The gate is `settings.person_columns` now, so the question
is asked exactly where the count is still in rows. **And one
single-visit subject silenced it by the other route:** route two of
`asking._names_people` asked "every different value on two rows or more",
which one row of 1,196 made false, and the limit had been recorded beside
the rule rather than repaired. Both routes now share route one's average,
counted and never divided, and a per-row key still fails it by a factor
of two whether or not one value of it repeats. The sentence the questions
file says was SEEN moves with the rule: "so each one stands on more than
one row" is now "on average", and both notices that say the population
was counted in ROWS stop opening "Nothing was named with --identifier",
which is false the moment a unique-per-row key is declared and the count
stays in rows.

Plan P4-D232, P4-D340 and P4-D341 carry the four amendments; ledger
`K-S3-02` keeps its 4 false positives of the same 33 columns, with the
amendment and the re-measurement in its `status_note`, two nodes added to
its pin and one renamed where its expectation reversed.

### Stage 3's gate, asked of a whole description in its own words (2026-09-23)

**A STAGE IS NOT DONE UNTIL A TEST LITERALLY IMPLEMENTS THE GATE ITS
PLAN NAMES.** Stage 3's gate is "no published number is held by fewer
than the floor, and a one-row table is refused". Pieces of it were held
in three places -- the tail rule's own guard, the sentence-argument
guard and the population floor's tests -- and nothing walked a whole
description and asked the gate's own question, so a landing that
published something NEW would have landed outside all three.
`tests/test_stage3_gate.py` is that walk.

**THE CLASSIFICATION IS CLOSED, and that is what makes the gate
survive a landing nobody foresaw.** 323 of `profile.PUBLICATION_RULES`'
669 stated paths can carry a number, and every one of them is in
exactly one of ten classes -- GROUP, POOLED, SETTLED, DISTINCT,
WRITTEN_FORM, VALUE, STRUCTURAL, WORD_BY_COUNT, SENTENCE, INDEX --
resolved through the three mirrors the rules table is built with, so
one decision is written once. **A path with no class fails the test.**

| the class | what the gate asks of it |
|---|---|
| GROUP | nought or at the line, and so is every complement against a population `GATE_POPULATIONS` names; a census asked whole, through `parsing.census_nameable` |
| VALUE | names no outer cell the tail rule withholds, unless `parsing.tail_may_list` admits it -- asked of the column, never of a list of paths |
| SENTENCE | every whole-number argument obeys `taxonomy.ARGUMENT_BINDINGS` |
| WORD_BY_COUNT | a non-default word stands only where the census line of the column's own cells wear it |
| SETTLED, WRITTEN_FORM | exempt BY NAME, each with the entry that settled it |
| POOLED, DISTINCT, STRUCTURAL, INDEX | exempt, with the reason written beside the class |

At a floor of eleven the walk puts **12,724 published numbers** of the
battery into those classes: VALUE 4,817, INDEX 1,997, SETTLED 1,895,
GROUP 1,706, STRUCTURAL 1,616, POOLED 310, DISTINCT 294, WRITTEN_FORM
89, beside the sentence arguments and the two words a count moves. The
battery is sixty-seven tables at each of floors 1, 5 and 11: the forty-six
seeded shapes of `tests/stage3_battery.py`, every role with its joined
column, the four realistic families as delimited text AND as workbooks,
three bounded clinical scales, two heavy tails, a sparse block, a
repeated-measures table with a declared identifier, a blank-line-heavy
file, and tables at 99, 100, 999 and 1,000 rows. **0 breaches**, and
the refusal half beside it: a one-row table, a 99-row table and 500
rows of 99 people refused through `cli.main` with nothing written; 100
and 999 rows carrying the notice on every written page; 1,000 carrying
none. Ledger `K-S3-13`.

**FIVE MUTATIONS, EACH A TEST OF ITS OWN**, because a guard that passes
is not a guard: a level count re-published at 1; a sentence argument one
greater than the key it restates; the column's exact minimum put back
into `percentiles.min`; a tail listing three values one row holds
apiece; and `parsing.POPULATION_FLOOR` halved. Each turns the gate red.

**WHAT THE GATE FOUND WHILE IT WAS BEING BUILT**, each recorded where it
belongs rather than worked around: a band read by VALUE rather than by
position called a boundary rung a leak on `two_readings_fit`, where five
rows hold 3.2 at the sorted positions 9 to 13 and the ladder publishes
the thirteenth; a second back-solve written here reported
`boundary + mean_distance` over a TWELVE-row tail as a disclosure when
the mean of twelve unequal distances names no row, so the gate asks the
tail-leak driver's own walk instead; reading a census's complement off
`n_present` called the withheld `thousands_marks` of 1,199 grouped
prices a breach of a word rule W holds at 1,199 cells; and splitting a
table's text on its delimiter turned `"1,234.56"` into two cells.

**THE LIMIT THE OWNER ACCEPTED TODAY (plan P4-D348): the disclosure
floor counts ROWS, not people.** On a repeated-measures table a value
held by twelve visits of ONE patient clears a floor of eleven and is
published with its count. It is not changed here; it is MEASURED, and
held at a ceiling by `K-S3-14`: over three seeded repeated-measures
shapes, **177** published values are held by fewer than eleven of the
table's PEOPLE and **68** of those stand on eleven rows or more -- the
rest being ordinary ladder rungs a handful of rows hold either way. It
concentrates where plan P4-D340 said it would: 12 patients over 1,196
visits leave 66 of the 68, the worst a rung of 65.0 on 11 rows of 5
people. The POPULATION floor beside it does count people, so the two
halves of stage 3 count different units on purpose.

**The KPI ledger's cap is 300,000 bytes, from 275,000**, authorized by
the orchestrator. The ledger stood at 274,933 with 67 to spare, and
what spent the last raise is stage 3's twelve entries `K-S3-01` to
`K-S3-12`. No measurement was trimmed to fit.

### Stage 3's close: one listing rule, and six sentences that were not true (2026-09-23)

**ONE RULE DECIDES WHICH TAIL MAY LIST ITS VALUES, and every role asks
it** (plan P4-D346). `parsing.tail_may_list` is the whole statement of
the owner's ruling of 2026-09-22 and of its premise: a tail lists only
where every value it would name stands on at least two of that tail's
cells AND the column's values are a small fixed set -- at most 256
different ones, standing under at least two cells apiece on average --
or where every listed value is held by a whole smallest group. The date
and clock role had carried that premise since P4-D342 and the numeric
role had carried none, so the two drifted: a continuous column of 599
rows on a tenth-unit grid published `88.0`, its own maximum held by ONE
row, in the same block that withheld `percentiles.max`, and a second of
609 rows listed five values whose counts in the column were 1, 1, 1, 1
and 9. Both are closed. A tail the rule does not admit may still list
where its own published rows and two distances SETTLE what it would
name -- at most two different values, which the pair leaves one
arithmetic for -- because the description names those either way.

| at a floor of eleven | before | after |
|---|---|---|
| six bounded scales at 1,800 rows: tail sides listing | 12 of 12 | 12 of 12 |
| the same six at 900 rows, where a scale's top step is one cell | 12 of 12 | 7 of 12 |
| whole-year ages at 2,000 and 5,000 rows | both sides | both sides |
| continuous columns, 600 to 640 rows | none | none |
| 609-row column listing `87.54, 87.8, 89.21, 90.68, 99.99` | listed | says its shape |
| 640 readings on a hundredth grid, every tail value shared | listed | says its shape |
| twin cells outside a Glasgow coma scale, 900 rows | 0 | 13 of 900 |
| twin cells outside an age column, 600 rows | 0 to 2 | 7 to 9 of 600 |
| a count of children at 900 rows: the twin's mean | -0.82% | +2.71% |

The cost is stated rather than argued away, and it is paid only where a
scale's own outer step stands on ONE cell: at 1,800 rows and above every
one of these scales lists both sides, writes no cell outside itself and
keeps its mean within 0.52 per cent. Every twin still writes the
column's own smallest and largest value, and nothing of the battery
misses a checkable obligation.

**THE COUNTS OF A LISTED TAIL ARE RECOVERABLE, and six places said they
were not.** This package SHIPS the arithmetic that works them out --
`contract._listed_counts`, which the generator needs -- and over the
ordinal battery it recovered 22 of 22 exactly. `README.md`,
`SECURITY.md`, this file, the contract's 6.7a, `summary.py` and
`quality.py` said "without how many rows hold each" and "never with a
count beside them"; they say what is true now: a listed tail names WHICH
values it holds and writes no count, and how many rows hold each follows
from those values and the distances beside them -- which is what the
owner accepted for bounded scales, and why the rule asks first whether
the column is one.

**`synthtwin validate` no longer prints the checked file's own tail
values.** A missed `tails.<side>.values` printed the file's list beside
the description's -- values a row may hold alone, the outermost of them
the file's own end -- which is the one thing the report's own note
promises never happens under any verdict. The comparison is made in full
and the measured side is kept back, as the date and clock role has
always done it. The reason is a fourth constant of `validation.py`, and
`tests/test_p3v12f2_a_miss_says_what_it_found.py` holds every one of the
four to the same bar.

**NF49 WAS A LIVE FALSE SENTENCE.** A tail block publishes its histogram
as `bin_groups` and leaves `value_histogram` empty on purpose, and the
note "the shape of this column's numbers is not published" asked only
the empty key -- so the demonstration's `visits`, `reading` and `amount`
each published 9 to 14 bin groups AND said their shape was not
published. The note asks both keys now, and a test fails on any block
that publishes groups and says otherwise.

**THE GUARD AND THE HEADLINE KPI COULD NOT SEE EITHER.** Both exempted a
listed value because the tail had listed it, so neither could fail on a
listing rule that had moved; the exemption is the rule's own conditions
now, asked from the column's own cells. `tests/test_stage3_tail_rule.py`
no longer skips `tails.*.values` by its path, and where it reads a
page it tells a VALUE from a distance and from a construction window,
each with the reason written beside it.

**`K-S3-11`'s `edge_pinned` IS CLOSED, not accepted** (plan P4-D346). On
an all-different clock column the two published distances, the day's
edge and the column's own "every value different" remark left ONE
multiset -- naming all eleven outermost times including the column's
minimum. The boundary now moves inward while the pair still settles the
tail, which DT2 allows, and the walk that decides it must PROVE the
tail settled inside its budget. Four sides of the battery moved, 11 rows
withheld per side becoming 15 or 17 of 900, and `edge_pinned` is **4 to
0** with `literal`, `pinned` and `missed` still nought.

**A WARNING WHOSE COUNT IS WITHHELD KEEPS THE WARNING** (owner,
2026-09-23; plan P4-D347). P4-D334 withdrew such a remark whole, and
1,199 comma-grouped prices beside one bare cell lost the decimal-comma
warning entirely. The warning is back with no number in it -- NF61,
which carries no argument at all -- and no sentence is withdrawn any
more. At a census line of two, where "fewer than 2" is the count of one
in other words, NF61 stands in NF60's place.

**The time-band remark says what it reads.** It rendered "this column
runs from X to Y" off the two tail boundaries, which understates the
span now that the ends are withheld; it says "with the outermost values
at each end set aside, this column reaches from X to Y". Its arity,
its seven argument classes and every other clause are unchanged.

**K-2B-47's refusal is a key now.** Two of its keys were nought by
construction whenever `build_document` refused the low-floor read, with
nothing structured saying so, so neither could ever fail again.
`read_floor_refused` says which of the two states the nought means.


### Merged: stage 3's five landings in one tree (2026-09-23)

**Nothing new is built here.** Stage 3 was built as five landings on
five branches cut from one base, each with its own skeptic and repair
pass, and this is the last of the five merged into the other four. What
it adds is the answer to every question a branch could not answer on its
own, because each branch could only see itself.

**Four names were claimed twice, and each landing's own text is kept.**
Two plan decision numbers (`P4-D321`, `P4-D332`), one published sentence
form (NF59), all twelve stage-3 KPI ids, and the loader's tail
invariants. In every case but the last the landing that arrived LAST
takes a new number and the rule it states does not change: landing 3.3's
"The numeric tail" is `P4-D344`, landing 3.4's "An advisory remark may
not outlive the facts it quotes" is `P4-D345`, the two fragments the
sentence landing added are NF60 and NF61 while the small-table note
keeps NF59, and stage 3's KPIs are `K-S3-01` to `K-S3-12` in landing
order. The exception is the loader's invariants, where landing 3.4 named
the date and clock tail's TL1 to TL4 and landing 3.3 the numeric tail's
TL1 to TL6 in ONE dictionary -- so every date-tail refusal quoted the
numeric rule's words. The date and clock family is **DT1 to DT4** now,
because `tails` and section 6.7a make TL the numeric family's name
everywhere else in the code.

**TWO KPIs HAD BEEN LOST, not renumbered.** Landing 3.2's population
battery and landing 3.4's tail-leak battery were dropped by earlier
merges of this stage: their tests and their driver stayed in the tree
with nothing naming them. Both are back, and the board's 30-headline cap
is kept by making ONE of stage 3's twelve a headline -- `K-S3-11`, the
tail leak -- and demoting the rest.

**The two tail rules now stand in one tree, and the second one binds the
first.** The time-band remark (NF51) quoted a `count` column's smallest
and largest values a second way, as two calendar days. The numeric tail
rule withdraws those values, so the remark now reads the two ends the
block PUBLISHES -- a heaped end where a group of eleven rows holds one,
and the side's boundary rung otherwise -- and a block that publishes
neither an end nor a boundary carries no remark at all (plan P4-D345).
The loader refuses a description whose ends are gone and whose remark
still names them.

**Nine definitions had silently shadowed one another.** Both landings
added a `TailFacts`, a `TAIL_KEYS`, a `_tail_strata`, a
`_tail_checks`, a `_tail_approximations` and a `_tail_fields`, and
because the two branches touched different lines the merge took both and
the later one won every time. Each pair is two different things with one
name now separated. The oracle also carried a second
`TWO_FIGURE_MEMBERS` that shadowed the real one, naming a format member
this contract does not have and dropping one it does; there is one list
again, and it is the shipped `parsing.TWO_FIGURE_MEMBERS`.

**The reference vectors are regenerated from the merged oracle**, all
eleven files, and the tenth carries six cases and the eleventh three.
The contract's note-grammar census is recomputed from the code: 61
forms, 99 argument positions, and the small-table note's two arguments
are bound where they had never been bound at all.

**A landing cut before the default floor moved brought eleven literal
floor defaults back in with it.** Landing 3.1 had taken them out (plan
P4-D317): a parameter named for a floor defaults to
`parsing.DEFAULT_SMALL_CELL_FLOOR` or to nothing, because a default of 1
reads a file at a floor nobody has chosen since the default became 11.
The date and clock tail landing was cut from the base before that
repair, so eleven of its functions arrived carrying `floor: int = 1` --
`generation._clock_approximations` and ten in `validation`, among them
`_universal_checks`, `_clock_checks`, `_rank_windows` and
`_pin_bounds_of` -- and landing 3.1's two AST guards were red on the
branch this merge lands on as well as after it. THE SITES ARE REPAIRED,
NOT THE GUARDS: the default is gone where the signature allows it and
names `parsing.DEFAULT_SMALL_CELL_FLOOR` where an earlier parameter's
own default keeps one. Four helpers in the tests and the tools were
reading a table at the default beside a floor of their own, which the
same landing's second guard names; each passes its own floor now.

**Two tests were written against a table a later landing refuses, and
five more asserted a rule as though its sibling did not exist.** Each is
repaired from the rule rather than from the new output. The numeric
tail's moment-window witness was twenty rows, which the population floor
refuses, so it asks the same question at a hundred rows with the floor
raised to fifty -- the size the command will take, and the floor at
which no percent clears two tails; landing 3.1's counted double-spaced
file was seventy records, and it takes the plain tail its own sibling
case already took (plan P4-D341), which leaves its seventy-one blank
places exactly where they stood. The empty-bin
witness asserted a per-bin census at a floor of one, where a tail block
publishes none at any floor; it now asserts the GROUPS, thirty-two at a
floor of one and eight at eleven. The twin's obligation census asserted
that only `numeric.tails` files the tail subchecks; both roles file
them, under their own field names, and it now says so and checks that
all three roles do. And the three time-band tests read the column's own
smallest and largest value; they read the block's two published edges
now, worked out through `tests/tail_rule.py`.

**Five golden digests are re-recorded, and THREE OF THEM WERE ALREADY
STALE** before this merge: the date and clock tail landing re-recorded
the twin and the quality report and left the demonstration profile, the
description the twin is built from, and the twin's own report behind, so
the branch this merge lands on was red on all three. Each is re-recorded
against a read of the artifact and not of the hash: the description
gains 329 leaves and loses 10, the twin moves 212 of 3,360 cells and
every one of them is in a numeric column, the report's count of
approximated facts rises from 122 to 134 and NAMES one new miss, and the
quality report's census grows from 533 checkable obligations to 541 with
33 more listed as not checkable and none lost.

### Changed: the numeric tail (stage 3, landing 3.3, 2026-09-22)

**A numeric column no longer publishes a number that one row holds.**
Until now every numeric block published its smallest and largest values
exactly, and the rungs beside them read the rows next to those. A
description now WITHHOLDS every rung whose type-7 reading touches one of
the outermost max(`--smallest-group`, 3) values, on each side, and
publishes what those rows look like as a GROUP instead: how many there
are, how far from the last published rung they lie on average, the
root-mean-square of that distance, and -- on a column whose values stand
on a grid, whose tail the listing rule admits and which holds a handful
of them -- the tail's own values, with no count written beside them
(contract 6.7a, method G5.3b to G5.3e; plans P4-D322 to P4-D327,
P4-D344 and P4-D346). An end is still published where a group of at
least that many rows holds it.

| on sixteen shapes at a floor of eleven                    | before | after |
|-----------------------------------------------------------|--------|-------|
| published numbers equal to a value fewer than 11 rows hold | 13-46 per shape | 0 |
| a 2,000-row age column: the twin's mean                    | +1.31% | +0.01% |
| a 500-row Pareto charges column: the twin's spread         | +9.72% | -1.13% |
| a pain score of 0-10: cells written outside the scale      | 50     | 0     |
| the same column's twin mean                                | +25%   | +0.2% |
| a 20,000-row normal column: real cells outside the twin's range | 16 | 0 |
| twenty gauss columns at 5,000 rows: the twin's spread       | +1.07% to +3.11% | +0.04% to +0.20% |

**Every consumer reads one ladder.** The rungs a tail withholds are
filled by that tail's own reading, and the two ends the twin pins are
DERIVED from the published facts alone (`contract.tail_ladder`), so the
generator, the validator, both reports and the summary all read the same
hundred and one rungs. A block too thin for two tails publishes its
moments alone and is read as the uniform with that mean and spread; one
below the floor publishes neither and is read as a ramp of one grid step
a value.

**What a reader is told instead.** The summary prints, per side, how
many values are not published, how far from the boundary rung they lie
and what that rung is; the twin's report and the quality report name the
two distances as approximated facts with their windows; and `validate`
checks a published (heaped) end ONE-SIDED and silently, so a check never
prints a file's own extreme.

**Found and repaired while building it**: a count column of small whole
numbers beside a heap of zeros published the value 1 in 317 cells and
its twin wrote 4 (the ranks of a band are now read at that band's own
sign, method G5.2a step 1a); a derived end held to a single published
field width pulled the low end of `0`-to-`59` from 0 up to 10; a tail's
smooth reading rounded onto a grid put two of its rows on one value,
which cost a 500-row column five of its thirty-one numbers; a derived
end above what a PADDED column can write -- 1006 on 1,200 offsets
written `+0123` and `0123` -- cost the twin's own description its
padded census, 482 cells of 1,200 against its source's 1,200 (method
G5.3b step 4); a joined position whose end is heaped had that one value
named twice, as `ends.number 2 max` and again by the ladder walk; and a
band whose every run lay inside a listed tail had no run left to
divide, which raised an error out of an empty list on twenty-four
offsets over eight values (method G5.3e).

**And one more found by the ledger itself.** A tail's innermost listed
value is commonly the column's value just inside the boundary as well,
and the ladder then reads one number across the edge. Such a run lay
wholly inside nothing, so the rule that keeps a listed tail's runs
whole passed over it, the layout joined it to its neighbours and the
stratum that swallowed it read its own share instead: on the 240
clinical codes of `K-P4-11`'s ClinVar column the twin wrote five cells
at `920759` where the table holds `920760`, `tails.high.values` MISSED,
and one of eighteen coding systems stopped validating clean. A run that
REACHES INTO a tail's rows is now one of the runs kept whole, where the
band's runs must be joined at all, and the band is still levelled after
it (method G5.3e). Each qualification was measured: cutting the run at
the edge instead spends one of the band's strata on the tail's own part
and took that stratum off a published MODE, 210 cells written nowhere
on 1,140 readings; protecting such a run on a band that had a stratum
for every run already split fifty published pluses across two values,
so a twin wrote four spellings of three numbers; and holding the
protected run STILL, rather than letting the levelling even the band,
gave 49, 53 and 48 cells where the source holds fifty of each. It costs
a seed of one battery one number: on a 4,000-row column of halves the
twin holds 16 of its 17 different values at seed 1 where it held all
17, because the run kept whole is one stratum where the walk could have
divided it.

**And a pooled census may not cross a checked fact.** A census of
widths and a census of marks count a group of fewer cells than the
smallest group into the commonest, so a column of 1 to 30 publishes the
one field width two although nine of its cells wear one. Read as a
ceiling, that census moved a derived low end from under 1 up to 10: on
the 30-row reading column of a macro workbook the twin wrote five cells
at 10 and none below it, its mean stood 5.3 above the published 15.5,
and `validate` MISSED `ladder.p50` and `moments.mean`. Neither spelling
clamp now pulls an end inside the tail's own published mean distance,
which no set of rows can meet from nearer than that (method G5.3b step
4).

**A withheld end is listed under its own name.** The rungs the tail
rule withholds are LISTED rather than checked, and an end is listed
under the field its check bound before -- `percentiles.min` and
`percentiles.max` -- so the same obligation goes quiet under its own
name and no subcheck binds two registry facts. Ten lines of the
demonstration's quality report say so and nothing else in it moved.

**One obligation goes quiet for a new reason, and the report still says
why** (validation amendment V2.4-A11). A file holding a different
number of values describes ITSELF with its ladder and its tails at a
different percent, so it publishes nothing at the percent the
description names, and the rungs and tail facts there are withheld --
beside `counts.n_used_in_statistics` MISSING in the same report, which
is the published fact that decides it. And a coarser description
widens G12.3's windows: on a blood-pressure column of 120 rows
`moments.skew` now reaches the range every sample of that size lies in,
so it is a census line rather than a pass -- which is what a skew of
that shape already was on the second position.

**Not repaired, with the number**: nine twins of a forty-twin battery of
one-place readings still hold one or two numbers fewer than their
description publishes, each named in the twin's own report. The tail's
rows are described by two moments rather than named, so a tail of seven
different values on a grid cannot always be given seven.

**The KPI ledger.** Eight new entries, `K-S3-03` to `K-S3-10`: no
published page names a value too few rows hold (the headline), the
published facts do not solve for a withheld end, a bounded scale keeps
its own values and ends, every twin and table of the battery is checked
clean, the real cells outside the twin's range, a listed tail's solved
counts, a count column beside a heap of zeros, and the histogram that
survives a raised floor in groups. Two targets are MET and their entries
are GREEN at their own measurements: `K-P3-03` (nothing missed at 5,000
or 20,000 rows, the twin's spread 0.04 to 0.22 per cent from the
published one against 1.07 to 3.83) and `K-2B-05` (0 verdicts flip of
1,058). `K-2B-47` improves on every key -- the heavy tail misses nothing
where it missed two checks, the band split is short of no value where it
was short of four, a record layout misses none where it missed three.
`K-P4-06`'s ceiling comes DOWN, from 609 agreements outside the window
and 3 missed above-counts to 556 and 1. `K-P4-07` keeps its exact 0 with
its rule restated. Two entries read worse and are recorded so:
`K-2B-49`'s point-free style misses rise from 30 to 33 -- one grid at
three seeds, whose listed tail's values the strata sizes cannot meet --
while its distinct-count misses fall from 12 to 3; and `K-S1-01` and
`K-P3-12` were taken on a LOADED machine, so their seconds are recorded
and not judged (31.2 s to generate 20,000 by 20 against 23.3, 126.2 s to
validate against 70.2) while their machine-free ratios are judged and
hold at 3.40 and 3.89, against 3.47 and 3.97 before, on a bound of 8.

**The independent oracle was re-written where it had drifted.** The
frozen vectors are built by an oracle written from the method's own
statements, and `K-2B-42` measures how close its functions sit to the
shipped code: the tail cases took it from 176 functions at or above
0.60 similarity to 190, every one of the fourteen a tail function. Each
was re-written from the clause it implements -- the shape's
coefficients read as one tuple, the staircase as a walk over its own
rows, the grid text as exact arithmetic on a fraction rather than a
format string -- and every vector file comes back byte for byte
identical through the provenance guard. The measure is back at 176 over
443 scored functions, where it was over 409.
### Fixed: a table with blank lines in more places than a description can name passes its own description (stage 3, 2026-09-22)

**`synthtwin validate` reported a real table as missing an obligation it
meets.** Where a file holds blank lines in more than 64 places, the
description stops naming the places and records how many blank lines
there are instead. That count was taken AFTER the rule that writes a
rare kind of blank line as the common kind -- a rule that exists to keep
a rare kind from pointing at the one record it stands beside -- so it
could be a number the file does not hold, while `validate` counts the
checked file's own blank lines. Past that cap the description names no
place and no kind, so there is nothing there for that rule to protect:
the count is now the file's own. Both sides of the check ask one
question at every smallest group size, and it is also the count a twin
writes back.

| blank-line-heavy files past the cap on places | before | after |
|---|---|---|
| the real table missing its own description, 300 seeded files | 16 | 0 |
| 70 records each followed by a blank line, one of them preceded by a line of spaces: `profile` / `generate` / `validate` against the real table | 0 / 0 / 3 | 0 / 0 / 0 |
| that file's 71 blank lines, as the description records them | 70 | 71 |

Counting the checked file after that same rule instead -- the other
obvious repair -- cleared those 16 and made 2 of the 300 TWINS miss: a
count spread evenly over its places writes runs of one line beside runs
of two, and the rarer run length is absorbed back, so 87 lines were read
back as 81. A count of the file's own blank lines is the one number both
a real table and its twin give back.

**A description of such a file also keeps its line endings where they
are.** The record of the line endings collapses to a single run wherever
a description keeps fewer lines than the file holds, because the runs'
positions would otherwise say where the missing line stood. Past the cap
the description now keeps every blank line, so nothing collapses: a
70-record file whose first 30 lines end with a carriage return and a
newline records `[{crlf: 30}, {lf: 112}]` where it recorded one run of
141.

**The seeded blank-line fuzz now checks the real table as well as the
twin**, and never writes fewer records than the cap, so the counted path
is covered: 18 of its 40 files take it, and all 18 failed on the real
table before this. The entry below records 27 of 40 descriptions refused
by their own reader before plan P4-D319; that was measured on the
narrower recipe (15 to 120 records) this pass replaced, and the same
measurement on the new recipe is 16 of 40.

### Fixed: the population floor counts the rows that hold a value, and the person question reaches the case it was built for (stage 3, landing 3.2's repair pass, 2026-09-23)

**A table padded with empty rows no longer walks past the floor.** The
population was counted on the rows the reader returned, so twenty real
records followed by eighty `,,` lines -- or eighty `NA,NA,NA` lines --
read as a hundred-row table, cleared the floor and were described. The
description that came out published the mean, the spread and every
percentile over the twenty; three numbers padded to a hundred printed
all three back verbatim. **A row whose every cell is blank, or is one
of this format's spellings for "no value", is now counted nowhere** --
neither as a row of the population, nor as part of the one unknown
person where an identifier is declared. The refusal says which rows it
counted, and the published notice then names the population the
description's counts actually rest on.

**The person question now reaches a subject column read as a set of
categories.** Its rule asked for more different values than a set of
categories could hold -- which is the exact complement of the rule that
makes a column `categorical`, so it could fire only on a column that
publishes no labels, and never on the case plan P4-D340 cites as its
reason for existing: 12 subjects over 1,196 rows, with every subject's
identifier published beside its visit count. A second route asks where
every value stands on two rows or more AND every cell is written as a
code -- inside the code alphabet, carrying both a letter and a figure.
The letter is what keeps a two-value `0`/`1` column, a group coded
1/2/3 and an ordinal scale out; the figure is what keeps `site`, `arm`
and `yes`/`no` out. `K-S3-02`'s battery gained the four label shapes
the rule mis-fires on and now reads 4 false positives over 33 columns,
accepted with the measurement in its `status_note`: route one alone
read 2 of those 4, and the battery simply did not hold them.

**Corrected, in three places: a description written before landing 3.2
does NOT still load.** The settings block gained a required key, and
contract rule C6-20 makes all twenty-three required, so the loader
refuses an earlier build's v6 description and names the entry that is
missing. The break is sanctioned by A-P4-41; the sentence saying it had
not happened was not. What IS still true, and stays: the floor is the
command's, `build_document` still describes a five-row table and
`synthtwin validate` still checks a 50-row file.

**And four smaller repairs.** `K-P0-10`'s `status_note` records that
this landing raised the suite's tables, that the seconds were not
re-taken and that the sharded sums suggest the suite grew by about a
quarter, so the next quiet-machine run re-stamps it. The subject counts
in `tests/test_p4d341_population_floor.py` and in the KPI test are
derived from the floor and the categories ceiling instead of stated, as
is the cell count in `tests/test_extra_round_numbers.py`.
`describe_with_the_producer` raises on a flag it does not implement
rather than dropping it. A stray `.;` left the ledger's measurement
note.

**What it cost the suite.** A one-column shape padded with absent cells
is now a population of its present cells, which is the repair working;
the harnesses that padded that way add a keeper column holding a value
on every row, exactly where the shape's own present cells fall short.
Twenty-three cases across six files moved that way, each still driving
the command.

### Recorded: landing 3.2's two KPIs against its own commit (stage 3, 2026-09-22)

`K-S3-01` and `K-S3-02` are re-measured on `52b9eee`, the commit that
built them: the population floor's thirteen-case battery reads 4
refused, 6 noticed, 3 silent and 0 files written after a refusal, and
the person question reads 0 false positives over 25 columns with the
one `subject_id` column asked about. The measurement note names both
beside the twelve entries already standing off `caf3079`, so
`tests/test_kpi_ledger_integrity.py` holds the note and that set equal.

### Added: synthtwin will not describe a table of fewer than 100, and says so from 100 to 999 (stage 3, 2026-09-22)

**`synthtwin profile` now refuses a table that is too small to describe
as a population.** Under 100 it writes nothing at all and tells you the
count, the line and what to do. From 100 to 999 it describes the table
and says so, in one plain sentence that cannot be turned off: on the
screen, in the description, in the plain-language summary, in the
questions file, in the twin's report and in the quality report. The
sentence says what it means, and it does not say that a small table is
excused anything -- the same rules produced the description, the same
smallest group size applies, and every obligation it states is the same
obligation. **The twin's own table carries no trace of it**, so code
you write against the twin runs exactly as it ran before (plan
P4-D341).

**The count is taken in PEOPLE where you have said who the rows are.**
Name a column with `--identifier` and, if its values repeat, rows
sharing a value of it are one person; rows holding no value of it count
as one person between them. An identifier that is different on every
row names a row rather than a person and is never counted by -- which
is what stops a table of 150 subjects being refused because a sparse
sample number sat beside the subject number. Where you have named
nothing and a column looks like it names people -- its values repeat,
and there are more of them than a set of categories could have -- the
questions file asks you about it, and the screen says the count was
taken in rows (plan P4-D340). The choice is written into the
description under a new settings key, `person_columns`.

| a table of                                    | before                     | after                              |
|-----------------------------------------------|----------------------------|------------------------------------|
| 1 row                                         | described, 3 files written | refused, nothing written           |
| 99 rows                                       | described, 3 files written | refused, nothing written           |
| 100 rows                                      | described, silently        | described, with the notice on all 5 pages |
| 999 rows                                      | described, silently        | described, with the notice         |
| 1,000 rows                                    | described, silently        | described, silently (unchanged)    |
| 500 visits by 99 subjects, `--identifier` given | described, silently      | refused, nothing written           |
| 500 visits by 100 subjects, `--identifier` given | described, silently     | described, with the notice, counted in people |

**What has NOT changed.** The floor is the command's and not the
format's: `build_document` still describes a five-row table, a
description of a small table still loads, and `synthtwin validate`
still checks a 50-row file against one. New KPIs `K-S3-01` and
`K-S3-02` hold the bands over a battery of thirteen sizes and person
shapes, and hold the person question to no false positive on the
realistic shapes.

**The worked example moved with the floor.** Every page that explained
how meeting a published count exactly can force a twin row to match a
real one used an 11-row table -- a table synthtwin now refuses. It is
stated at 100 rows.

### Changed: no sentence of a description carries a count its keys withhold (stage 3, 2026-09-22)

**A count in a key was held to the smallest group size; the same count
in a sentence was held to nothing.** A column with one grouped cell in
four hundred read "1 of this column's values are written with a comma
inside the number" -- a count of one, naming one row, in the plain
prose part of the description. Over 56 descriptions at a smallest group
size of eleven there were 252 sentences and 145 of them carried
numbers: 9 printed a count no key of the block beside them published at
all, and 38 more restated a count the key itself published below that
line.

Every argument of every sentence is now bound to what it is. Most of
them restate a count the block already publishes, and those are checked
against it, so the key's own rule covers the sentence. Thirteen do not
restate anything: they are the sentence's own count -- how far a
reading got, how many cells wore a mark -- and those now say "fewer
than 11" where the group is too small to name. The description is
refused before it is written if any sentence breaks either rule.

Three more changes came with it. The words a count moves -- how the
negatives were written, the mark between thousands, whether wide runs
of figures are their own values' text -- are held to the same line as
the counts, so one cell can no longer move a word about a whole column.
The commonest number and its count are withheld where the cells that
are NOT the commonest number are too few to name: 395 zeros among 400
values used to publish 395 beside 400, which names the other five.
And the counts this release deliberately leaves published -- how many
cells were not numbers, out of range, contradictory, unparsed, zero or
negative -- are now held at a ceiling in the KPI ledger, so they cannot
quietly grow.

Why those last ones stay: flooring them made code developed on the twin
run clean where the real table raises, in 7 of 7 shapes measured, and
the count could still be worked out from the published count of missing
cells. This is a reversible call and goes to the owner.

| a column of 400 values | before | after |
|---|---|---|
| one grouped cell, in the remark | "1 of this column's values..." | "fewer than 11 of this column's values..." |
| a reading that reached 4 cells, in the remark | "4 of its values are numbers wearing..." | "Fewer than 11 of its values are numbers wearing..." |
| 395 zeros: commonest number | `mode 0.0`, `mode_count 395` | both withheld |
| one bracketed negative, `--smallest-group 1` | `negative_form: brackets` | `negative_form: minus` |
| one grouped cell, `--smallest-group 1` | `group_separator: ","` | `group_separator: ""` |
| cells that were not numbers | published | published (unchanged, and held at a ceiling) |

**And a sentence may not hand back the cells it does NOT count.** A
count is a disclosure from either end. A column of 1,200 prices with
1,199 of them written `1,795` and one written plain said "1199 of this
column's values are written with a comma inside the number" beside a
published row count of 1,200 -- and 1,200 less 1,199 is the one cell,
named exactly as a key holding 1 would name it. This is the shape the
tool already refuses in its key censuses, in prose. Four sentence
counts are counts of cells bearing one spelling, and each of those is
now held to the cells it leaves over as well as to itself: below the
line either way, the sentence is not written. Where the sentence is one
a column cannot lose -- the line that says how the column was read --
it is written without the number at all.

| a column whose small group is on the OTHER side | before | after |
|---|---|---|
| 1,199 grouped prices, 1 written plain | "1199 of this column's values are written with a comma..." | the remark is not written |
| 390 dates, 10 cells no reading fits | "390 read as dates written as 2024-03-17" | "some but not all read as dates written as 2024-03-17" |
| 59 cells wearing ` mg`, 1 wearing ` MG` | "59 of its values are numbers wearing one shared piece of text" | the remark is not written |

**What the first row costs, said plainly:** that column loses its
decimal-comma warning, which is a warning about 1,199 cells that may
each be a thousand times their real size. One ungrouped cell withdraws
it. The warning is worth keeping and the subtraction is not acceptable,
so whether such a remark should be kept with no count in it -- the way
the read-as line now is -- goes to the owner rather than being decided
here.

### Fixed: files with blank lines of two kinds describe and build again at the default (stage 3, 2026-09-22)

**A description `profile` wrote could be refused by `generate` and
`validate` as "changed since it was written".** It happened where a
record was followed by a line holding only spaces and then an empty
line. The default floor of 11 writes a rare kind of blank line as the
common kind, and that left two identical blank-line entries after the
same record, which the reader of descriptions refuses. The two are now
one entry, as a file written that way reads, and the same order rule is
checked before a description is written as when it is read (plan
P4-D319).

| blank-line-heavy test files                           | before     | after   |
|-------------------------------------------------------|------------|---------|
| refused by their own reader, 40 seeded files          | 27         | 0       |
| a record followed by spaces, then an empty line: `profile` / `generate` / `validate` exit codes | 0 / 1 / 1 | 0 / 0 / 0 |

**What the default of 11 costs elsewhere, now held by name** (plan
P4-D320). The joined-number battery misses 4 above-counts at the
default against 3 at a floor of one, because the default publishes less
about each position; the ledger's ceiling moves to 4 in its own commit
and stays with stage 6. A declared record-number column of 49 rows still
fails its own check at the default, and one column of the fold-repair
battery still takes minutes to generate; both are pinned so a repair
shows. Two carried misses -- a heavy-tailed column's average and one
record-number layout -- disappear at the default only because it
withholds more, so they are measured at a floor of one as well.

**Every test and tool that names a floor now reads the table at that
floor** (plan P4-D321), and a check keeps it so. The `--code` help no
longer promises every code's count, since the default pools the rare
ones.

**The KPI ledger.** `K-P4-06`, `K-2B-05`, `K-2B-47`, `K-2B-49`,
`K-2B-50` and `K-2B-51` are re-measured on f521955, the repair's own
commit, and written in. `K-2B-47` gains three keys -- the declared
identifier's miss at the default, and the heavy tail and the record
layout at a floor of one -- and holds the read-floor hole closed at
nought. `K-2B-05` reaches its target of no flipped verdicts only
because the default withholds more, so it stays open, and its note says
so.

### Changed: a column of dates or clock times publishes tails, not ends (stage 3, 2026-09-22)

**No date or time a description publishes is one of the column's
outermost cells any more.** `earliest`, `latest`, `earliest_utc_offset`
and `latest_utc_offset` are gone from the `datetime` role, `earliest`
and `latest` from `time_of_day`, and each ladder publishes `null` at
`min` and `max` and at every rung whose rank falls inside a tail. Each
side of such a column publishes a TAIL instead: the boundary -- the
smallest value with at least a smallest group's worth of cells strictly
below it, mirrored above -- the count of rows beyond it, and how far
those rows stand, as a mean and a root-mean-square distance in the
column's own `tail_unit`. A tail holding few different values, or one
whose two distances would settle a count below the floor, publishes
those values instead, with no count written beside them -- but only
where EVERY value it would list is shared by at least two of its cells
and the column's own values come from a small fixed set rather than a
fine grid, or where every listed value is held by the floor's own
number of cells. A column of all-different clock times lists nothing
and publishes its shape (plans P4-D328 to P4-D331, P4-D342, P4-D343 and P4-D345). A
column too small or too tied for a boundary on each side publishes no
value of the table at all, and its twin is a made-up ramp from
1970-01-01.

MEASURED ON ONE NAMED SHAPE, so that the rows can be re-run: the tail
battery's `uniform` column, 400 days drawn over three years at seed 0,
described at a floor of eleven on `13fa831` and on this tree.

| `uniform`, 400 rows, seed 0, floor eleven            | before | after |
|------------------------------------------------------|--------|-------|
| different date values published                      | 11     | 9     |
| of those, held by exactly one row                    | 8      | 6     |
| of those, naming one of the 11 outermost cells        | 4      | 0     |
| rungs published between the two boundaries           | 9      | 7     |
| checkable obligations the twin misses                | 0      | 0     |

The six that a single row still holds are interior ladder rungs and the
two boundaries: this landing's half is the EXTREMES, and a rung read
from the middle of a column of all-different dates is one row's date
whatever else changes. The numeric sibling landing owns the rest.

**And the twin's own spread is repaired by the same change**, measured
on the battery's `lone_far` column -- a column with one value a long
way out -- over both sizes and every seed, as the population standard
deviation of the twin's dates against the real column's: +7.92% to
+40.47% before, -0.96% to +0.18% after.

**What it costs.** The ladder loses both of its ends on every column,
and every interior rung whose rank falls inside a tail. MEASURED on
all-different day-resolution columns at a floor of eleven: a column of
fewer than twenty-three rows publishes no date at all; from
twenty-three it publishes one rung (`p50`), from forty-two a second
(`p75`), from forty-five a third (`p25`), seven at four hundred rows,
and all nine from one thousand one hundred and one -- the row count at
which `p01`'s own rank, `floor((P - 1) / 100)`, first reaches the low
tail's eleven cells. It also costs the lone-far-value column its listed
dates: those were nine dates one row each held, which the rule of
P4-D342 now refuses, so that column is described by its shape like any
other. What it buys is that a column's rarest dates -- a date of death,
a date of birth at the edge of a cohort -- are no longer written down in
a file that travels.

**And one window was drawn tighter than its own construction.** The
checker built a date column's tail window with "every value different"
hard coded FALSE, while the generator reads the column's own
distinctness and lays the tail out accordingly -- a validator that
rejects conforming twins, which is the failure that whole class of
windows exists to avoid. It went unseen while such a column published
its tail's VALUES instead of its shape; with the rule above closing
that road, a column of 120 different months missed both of its low
tail's distances, its twin standing at a mean of 7.0 months against a
window of 5.64 to 6.45 whose own construction reaches 7.0. The checker
now reads distinctness exactly as the generator does.

**What is measured, and where it stays measured.** The KPI ledger's new
`K-S3-11` walks twenty-one shapes at two sizes and up to three seeds --
105 columns, each described, generated and checked -- and holds three
numbers at nought: values named, values settled by back-solve, and
obligations missed by the twin or by the real table. It records four
more as bounds that may not slip. How much room the battery's tightest
tail leaves a reader trying to back-solve it: 2 different multisets of
distances, on a column of quarters. How many tails still LIST their
values rather than publish a shape: 12, all of them quarters, months or
the forty-cell `0001-01-01` heap. How many of the real table's own
published distances the checker's window does not reach: 2, on a
quarters column at 400 rows and a months column at 1,500, and those are
the two places where the real table meets an obligation by holding the
published value exactly and the window around it is no help. And how many tails the published pair settles to ONE arithmetic
once a reader also uses the column's own all-different remark and the
tail's own edge: 4 when this was written, every one of them a side of
an all-different clock column of 900 rows whose tail is pressed against
the end of the day. **That number is 0 since plan P4-D346**, which
moves such a boundary inward until the pair no longer settles the tail;
what stands here is what it was, so that the entry above can be read
against it. A
fifth, `unsearched`, says where the measurement itself could not
finish: 35 tails counted in SECONDS, whose sums run past what an
exhaustive walk can enumerate, so their room is not measured rather
than measured and found roomy.

### Changed: the default smallest group is 11 (stage 3, 2026-09-22)

**A description made without `--smallest-group` no longer names a group
of fewer than eleven rows.** The owner returned the default to 11, the
value it had before 25 August and the same number as the line under
which every page says a description names small groups. A smaller
number is still accepted and still alarms the screen and every page.
The number is written once, in `parsing`, and every module reads it
from there (plan P4-D316).

| on the every-role table (240 rows, 14 columns)   | floor 1, the old default | floor 11, the default now |
|--------------------------------------------------|--------------------------|---------------------------|
| labels published                                 | 192                      | 9                         |
| labels held by one row                           | 147                      | 0                         |
| labels held by fewer than eleven rows            | 183                      | 0 (183 pooled, 224 rows)  |
| numeric columns publishing a histogram           | 4                        | 1                         |
| description size                                 | 100,210 bytes            | 50,517 bytes              |
| facts the twin's own report names as unmet       | 4                        | 4                         |
| subchecks the twin misses                        | 0                        | 0                         |

The histogram is all or nothing, so a bell-shaped column with thin
outer bins loses it until the tail landing re-anchors it. Exact minima
and maxima are still published; that is the tail landing's too.

**Three places read a file at the wrong floor, and one rule lived in
the producer alone** (plan P4-D317). The survey's second walk after a
broken trailing-delimiter guess, the quality check of a zero-row
description, and the test suite's shape describer each read a file at
the default whatever floor was asked. Blank lines, blank lines counted
past the cap and counts of empty records were held to the disclosure
rule by the producer alone. A hand-edited description that names one of them below
the line is now refused by the loader and by the guard that runs before
a description is written.

**Found and not repaired, with the numbers** (plan P4-D316): at the new
default the twin of the 49-row declared-identifier column of plan
P4-D182 fails its own check, because the made-up spellings of its
pooled groups read as hexadecimal; one column of the fold-repair battery
takes 269 seconds to generate against under one second at a floor of
one; and a whole-number column whose rarer width is pooled names
`field_widths` in its twin's report. The tests that measure those
mechanisms now ask for a floor of one and say why.

**The KPI ledger.** `K-P4-20` pins the default at 11 and is re-measured
on `3f6cd9f`, the landing's own commit. The fast tier of the runner
reads no drop there (120 green, 9 open and 4 accepted limits held). The
joined-number battery's driver, measured at the new default on the same
commit, reads `K-P4-06` WORSE: 609 agreements outside the window, as
recorded, and 4 rows-above counts missed against a ceiling of 3. The
in-suite pin of that battery is measured at a floor of one, where its
ceilings were taken.

### Changed: the owner accepted the twin rebuilding 63 held-back cells, not 55 (2026-09-22)

The mean-only landing of 21 September moved `K-2B-19` from 55 to 63 of
251 held-back cells that the twin writes exactly as the table held them,
with one column of nineteen still rebuilt whole. The owner accepted the
new ceiling: "just showing that the value exists is not an issue; what
matters is not showing the relation in a descriptive file." Nothing in
the code moved. The ledger entry records the decision, and the state
page no longer lists it as waiting.

### Changed: stage 2 is closed, and the twin writes each column the way the source wrote it (2026-09-15 to 2026-09-18)

**Until this stage, code that ran on the twin could still fail on the
real table because the twin spelled things its own way.** Dates came
back in ISO form, a declared record number came back as
`A----------------------------------J`, a European price came back as
punctuation, and a workbook could not be read at all. On 2026-09-15 the
owner ruled that the twin writes everything as the source wrote it. The
entries below are grouped by what a researcher now gets. The eighteen
landings of stage 2b were built on separate branches, merged into one,
reviewed three times, and closed under the owner's rulings of
2026-09-17 and 2026-09-18.

| suite, at each close                        | collected | failed |
|---------------------------------------------|-----------|--------|
| first review round's fixes, merged and repaired | 6,056 | 3      |
| stage 2 closed, before the extra round      | 6,397     | 1      |
| extra round merged and landed               | 6,626     | 57     |
| stage 2b closed                             | 7,083     | 0          |

At every close, one of the failures was the state page's own record of
the suite size. That page is written separately.

**The closing run.** On the merged tree at `fd93100`: 7,083 collected,
7,033 passed, 49 skipped, and one failure — this page's companion, the
state page's own record of the suite size, which moves in the commit
that carries this entry. Four review rounds reached this point, and the
last of them is below.

### Fixed: a twin's numbers stay much closer to the column's own distribution (stage 2b, 2026-09-15 to 2026-09-18)

**A twin could hold one number far more often than the real column ever
did, move a column's published mode, or place held-back values
nowhere near the table's own.** Some of these failed the twin's own
validation and some passed every check while wrong; the table gives
both.

| case                                                    | before           | after                  |
|---------------------------------------------------------|------------------|------------------------|
| 4,000 rows, published mode count 62: most copies of one number | 760       | at most 62             |
| 2,000 tenths publishing 517 numbers: numbers held       | 479              | 517                    |
| the same: cells at full binary precision                | 227              | none                   |
| 96 twins of spreadsheet decimals: checked with nothing missed | 4          | 70                     |
| the same: leading zeros invented                        | 736              | 16                     |
| floor of 11: most copies of one number, 30 twins        | 45 (4,000 amounts) | 10 or fewer          |
| two reports on 44 columns: windows printed differently  | 923 of 985       | none                   |
| readings beside labels (skeptic's case): twin spread / table | 1.9 (up to 4.9) | 0.99               |
| six narrow-width shapes: twins failing, of 48           | 19               | none                   |
| readings written both `4` and `4.0`: misses, of 240     | 61               | 1                      |
| signed grouped twins: marks census misses, of 80        | 36               | 0                      |
| published mode `-0.6` over 210 rows: twin holds it      | 0 times          | 210 times              |
| held-back number shapes: twins failing, of 30           | 17               | 0                      |

- **Numbers beside labels keep their numbers.** A column of one-decimal
  readings beside two labels published 853 numbers at 1,200 rows and a
  floor of twenty, and its twin held 359. Over 242 runs every twin now
  meets its class counts and validates. Where the column published a
  number (222 runs), the twin's mean stays within 0.42 of the table's
  standard deviation, and the spread is within a fifth of the table's
  in 217 runs.
- **A column of a few levels keeps its levels.** 2,000 quantities of
  eleven levels, and 1,423 discounts of six, wrote a whole level at a
  number the source never held in six twins of eight (`7.4` 225 times,
  `1.3` 199 times). The twin now uses the published levels. A level too
  rare to be named on the published ladder can still move.
- **A held-back number stays inside the numbers the column has.** An
  exponent-written column's made-up cells came back `9.6E6`. The twin's
  mean was 2,450,000 against the table's 1,173,077, its spread was 43
  times the table's, and validation passed. A made-up number now lies
  between the smallest and largest published values. On an amounts
  column published from 1,100,000 to 8,800,000, the twin's mean is
  4,957,692 against the table's 5,034,615, where it had been 4,188,462.
- **Grouped and bare amounts are spread across the column.** The bare
  cells had always been the largest amounts. The twin's grouped and
  bare means are now 486k and 485k against the real 493k and 476k,
  where they had been 289k and 795k.
- **The twin's report and the quality report print the same window.**
  A twin scaled by 1.03 or 1.05 is still reported MISSED, so the check
  lost none of its power.

**Cost, stated rather than hidden.** Where a held-back level lies outside
the published span, the census is met at the statistics' expense. On
one measured column the twin's mean was 17.9% high and its spread 34.0%
low, and the twin's report says the placement is synthtwin's own.

**Measured and left open, each held at a ceiling in the KPI ledger.**

- **On columns shaped like a bell curve, the twin's spread is 1.4 to
  3.7% too wide.** Measured on potassium, sodium, systolic pressure,
  haemoglobin, body mass and saturation from 5,000 rows. At 20,000 rows
  by 20 columns, 19 of 1,021 checks miss on the standard deviation; at
  5,000 rows none do. The cause is how the twin fills the outermost 1% of
  a column: a straight line out to the exact published minimum and
  maximum, where the real column reaches those ends only with its last
  few cells. The repair is known and needs only published facts. It is
  left for stage 3, which replaces the exact extremes with a published
  tail shape and so rewrites this same step. Until then a test holds
  four bell-shaped columns at 5,000 rows within 2.2% of their published
  spread, and the ledger records the rest: +1.07 to +3.11% at 5,000
  rows and +1.74 to +3.83% at 20,000 across its twenty columns.
- **Cells holding three or four numbers.** 597 of 2,160 pair agreements
  fall outside their window, and 7 counts of rows where one number
  exceeds another are missed. When recorded, the figures were 550 and 0.
  The cause is the walk that pairs the numbers. A repair was tried and
  withdrawn, because it moved length of stay's mean 12% further off.
  After the merge the figures are 609 and 3: the repair of a nearly full
  band (below) trades 12 agreements for 4 exact counts, and the
  orchestrator accepted that trade.

### Fixed: the common ways a number is spelled come back (stage 2b, 2026-09-15 to 2026-09-18)

**Four spellings of a number were lost with no error.** A charge grouped
with a space, an apostrophe or a thin space was read as free text. An
accounting negative `(1,234.56)` came back as `-1,234.56`, and the real
table then failed its own description. A plus on a decimal was dropped.
`1,483.65-` and `−6.09` were published with no negatives. A bare copy
of a grouped twin also validated at exit 0.

- **Seven thousands marks, four negative notations and the signed
  decimal are read, published and written back.** A mixed column is
  written as a mix. 600 charges, 480 written with a minus and 120 in
  brackets, had come back as 600 minuses. 200 cells grouped with a space
  beside 100 grouped with a narrow no-break space had come back as 300
  ordinary spaces. Both now come back exact at three seeds.
- **A German count column is asked whether its point is a thousands
  mark.** It is asked on 6 of 6 runs, where 3 of 3 seeds had asked
  nothing, and the answered mean equals the true mean. The signed
  decimal is exact on 6 of 6 seeds.
- **A declared European price is read as money.** `795,64 EUR` had been
  read as free text, with a twin of `)!!!!! !!!!!` and both files
  passing. It now comes back as `624,60 EUR`. `92.959,11 EUR` had lost
  its grouping point on 800 of 800 twin cells, and now keeps it on 800
  of 800.
- **A real export meets its own description.** Excel, SAS, Stata, SPSS
  and Fortran exports (`4.60E+03`, `6E9`, `.05`, seventeen-figure
  numbers) had failed their own description on 14 runs of 14, and now
  pass. A Fortran column written with a `D` exponent still comes back as
  stand-ins. A ledger of signed seventeen-figure keys had 398 of 800 cells
  refused, and now passes at both seeds.
- **Wide keys say how they were written.** 800 seventeen-figure keys,
  790 of them respelled into neighbours a computer cannot tell apart,
  had checked out at exit 0. The description now records whether the
  column wrote its numbers the way the numbers write themselves, and a
  respelled file is caught. Zero-padded keys are included: 786 of 800
  respelled had passed, and they are now reported at exit 3.
- **A whole-number column written `44.0` stays whole.** 23 cells of 800
  had moved to values such as `25.6`. None move now.
- **An undeclared blood pressure is read as two numbers.** `128/79` had
  been free text without `--measurement`. Near the long-tail line, 22 of
  80 round trips had been reported MISSED, and none are now.
- Offsets written both `+0123` and `0123` keep their spellings: 917 of
  917, where there had been 776. A zero-filled code no longer gains a
  sixth figure in a five-figure field (`099613`).

**Not yet fixed.** A column mixing notations can write `101.88` beside
`0101.88` and hold one different number fewer than published. The twin
fails at exit 3 and its report names it.

### Fixed: timestamps and dates are written as the source wrote them (stage 2b, 2026-09-15 to 2026-09-18)

**The twin wrote every date in ISO form.** `strptime('%m/%d/%Y')` parsed
400 of 400 real cells of a month-first export and none of its twin's.
`'%d-%b-%Y'` failed the same way on a SAS export. `2024-q1` came back as
`2024-Q4`. A compact `YYYYMMDD` column's twin failed synthtwin's own
validation. On eighteen export shapes at three seeds, 240 of 240 twin
cells now parse under the export's own format, none is written as ISO,
and the twin and the real table both validate.

| case                                                | before                  | after              |
|-----------------------------------------------------|-------------------------|--------------------|
| per-day count variance, twin / real (54 runs)       | 0.057 to 0.514          | 0.52 to 1.41       |
| interior percentile dates exact (54 runs)           | none (one day early)    | 54 of 54           |
| 2,000 rows, 1,900 bare dates beside moments at midnight       | written as moments      | written bare       |
| partly-midnight columns: midnight cells kept        | 2 of 361; 1 of 1,429    | 361; 1,429         |
| CET/CEST export at local midnight                   | 2 of 900, a day early   | exact              |
| midnight under three offsets: invented times        | 11 of 120 cells         | none               |
| exact distinct-date counts                          | 4 came back as 7; 3 as 6 | 4; 3              |
| 400 `05-Mar-2021` dates over 250 days               | 246 different dates     | 250                |
| export of 1,077 distinct dates                      | 1,065 or 1,107          | 1,077              |

- **Each spelling detail is kept:** field order, delimiter, field widths,
  month-name case and length, quarter and zulu case, and the mark
  between day and clock. A mark written by fewer rows than the floor is
  the exception: under ruling 6 it is counted into the commonest mark, so
  a rare lower-case `t` beside many `T` comes back as `T`.
- **A twin's dates spread across days as real dates do.** The first
  review round found a shape the table above missed: 3,000 dates over
  60 days piled onto the published percentile days, and the twin's
  day-to-day variance was 4.8 to 6.6 times the table's. It is now 0.61
  to 1.02 times. The first attempt at that fix made a week of thinning
  dates come back 0.32 standard deviations late; its repair returned
  them to +0.06 to +0.10, where they had been.
- **A declared day-first column is judged in its own order.** Twenty
  January dates had been removed as placeholders, leaving 380 of 400
  values. All 400 are now kept.
- **A table no longer fails its own description on a placeholder day.**
  20 judged `1900-01-01 00:00:00` beside 30 declared placeholders had
  left the real table missing thirteen obligations. Five kept
  `01/01/1900` cells below the floor had left it missing fourteen. Both
  now validate.

**Accepted as a limit (2026-09-18).** Fractions of a second are written
as nought. 240 of 240 source cells held a thousandth and the twin held
none, while both files validated. The twin's report now says so.
Generating at the millisecond is a landing of its own.

**Deferred.** The time of day inside a timestamp is not reproduced. On a
clinical table, 932 of 2,000 twin discharges fell outside the real 07:00
to 19:00 range. This is stage 3b.

**A slowdown this stage caused, found by the KPI ledger and fixed.** One
of the extra round's date repairs added a search that stepped one second
at a time. Generating a 2,000-row date-time column took 28.5 s where it
had taken 0.16 s. The search now sorts the column once and walks that
order. Medians of three on a shared machine:

| column | before | after |
|---|---|---|
| 400 date-times, partly at midnight | 55.3 s | 0.12 s |
| 2,000 date-times, partly at midnight | 63.5 s | 0.52 s |
| 20,000 US-style dates | 2.7 s | 1.3 s |

The twins are byte-identical to the slow ones. A test counts the
search's steps, so the suite fails if the one-second walk comes back.

### Fixed: labels, free text and missing values keep their own spellings (stage 2b, 2026-09-15 to 2026-09-18)

**A cell holding only a space was published and written as an empty
cell.** A 500-row readings column published 315 blanks when 177 of them
held a space, two spaces or a no-break space. `pandas.to_numeric` then
ran on the twin and raised on the real table. Each whitespace spelling
is now published at its own count, and the twin writes it back.

- **Free text names the missing-value words it used.** A 500-row note
  column with 101 blanks and 174 `NA` or `N/A` had its twin write 275
  empty cells. The real table also failed its own description. The twin
  now writes `N/A` 95 times and `NA` 79 times, and both files validate.
  The real table of a declared identifier with 59 `NA` cells now meets
  its own description, where it had exited 3.
- **Codes wear their own shapes.** 800 rows whose description names
  forty forms came back wearing none of them, 405 cells short. They now
  meet every form at three seeds. A notes column mixing codes and prose
  went from 320, 310, 138, 117 and 114 cells short to none. A
  two-convention telephone column had worn its form on 531 of 532 cells
  that owed it, and now wears it on all 532.
- **Lower-case codes stay lower case**: 800 of 800, where none had been.
  Held-back codes wear their column's shape instead of `group-N`: the
  mean length is 7.204 against the table's 7.204, where it had been
  9.907.
- **Missing words pooled below a raised floor count as absent (ruling
  4).** 280 record numbers beside ten `NA` and ten `N/A` at a floor of
  twenty now validate, where the real table had exited 3.

**A `-999` that synthtwin judges to mean "no value" is written as the
source wrote it.** It used to be written blank, so pandas read the twin's
column as decimals (`float64`) where the real column is whole numbers
(`int64`). On the twin, `df.reading == -999` found nothing; on the table
it found 13 rows. The twin now writes the judged spelling at its
published count. The column reads `int64` on both files at every seed
and floor tried. Of 16 judged shapes, none now gives a column a
different type in pandas, where 9 did before. A judged spelling below
the floor is still absorbed, like any spelling below the floor, and that
column still reads as decimals. This supersedes the Phase 4 decision
that wrote judged placeholders blank.

### Fixed: record numbers and codes keep their layout (stage 2b, 2026-09-16 to 2026-09-18)

**A declared record number came back as a row of hyphens.** A UUID
column matched its own pattern on 800 real rows and 0 twin rows. A site
code `NYC-2033` came back as `A------J`. A zero-filled `02254257` came
back as `10000020`. A column mixing two numbering systems had its length
mix `{10: 573, 7: 227}` collapse to `{7: 799, 10: 1}`. Both files
validated at exit 0.

The description now publishes each record number's layout: what kind of
character stood at each position, never which one, apart from a prefix
every record shares (ruling 1). The twin writes to that layout.

| twin cells matching the source's pattern, 800 rows | before | after |
|----------------------------------------------------|--------|-------|
| UUID, braced GUID, site code                        | 0      | 800   |
| `%08d` zero fill opening `00`                       | 78     | 800   |
| `^P\d{5}$`                                          | 30     | 800   |
| `^REC\d{7}$`                                        | 0      | 800   |
| `^ABC-\d{4}$`                                       | 0      | 800   |
| two systems `^(REC\d{7}|E\d{6})$`                   | 9      | 800   |
| hexadecimal `DE-[0-9a-f]{6}`                        | 0      | 800   |

- **A shared prefix is published and written (ruling 1), per system on a
  two-system column (ruling 7).**
- Made-up identifiers no longer lean on the figure nought: 11% noughts
  on a 13-figure code, where there had been 45%. On the identifier test
  battery, the runs short of a layout fell from 488 to 200 of 800.
- **One exact rebuild of real record numbers is closed; one is not.**
  `REC000` to `REC999` published a prefix and a layout with one
  solution, and the twin held all 1,000 original rows. The prefix is now
  withheld there, and the twin holds none of them. 900 record numbers
  from `100` to `999` no longer publish their layout, but the lengths
  and counts that remain still pin the set, and the twin still holds all
  900 real numbers (see the limit below).
- **The twin's report no longer says its made-up values "are not your
  data".** 40 of 2,000 made-up subject numbers matched real ones, which
  is the chance rate, and the report now says this can happen.

**Accepted as a limit (2026-09-18).** When a column's layout has little
room to spare, real record numbers still reach the twin. At 1,000 rows,
`REC` plus four figures leaves 100 real record numbers in the twin,
plus five leaves 10, plus six leaves 1, and plus seven leaves none.
Withholding the layout does not help: `100` to `999` leaves all 900,
and 989 numbers from `000` to `988` leave 978.

### Fixed: the file itself, and Excel workbooks (stage 2b, 2026-09-15 to 2026-09-18)

**synthtwin now reads Excel workbooks and writes each twin in the same
form as its source file.** Following the owner's ruling of 2026-09-15,
it reads Excel and delimited text only. Workbooks are read and written
with Python's standard library. openpyxl is used only by the tests, as
an independent check.

- **The delimited form is kept:** the delimiter (including Excel's
  `sep=` line), line endings, encoding and byte-order mark, quoting,
  blank lines, preamble lines, index columns, padding and row order. A
  line ending or blank line too rare to publish is not reproduced. When
  the file form landed, five ordinary UTF-8 comma files with LF endings
  gave twins byte-identical to before; the number, date and label fixes
  above change twin cells where they apply.
- **Three ordinary spreadsheets now make usable twins:** a table behind
  a hidden notes sheet, a sheet named like "Cohort extract", and a
  macro-enabled workbook. None of the three had worked before. Numbers
  stored as text are read. Format codes are written as the source wrote
  them where they use only the format language's own tokens. The twin's
  report names the sheet it writes.
- **A workbook twin can always be opened.** A column stored as dates
  had its twin hold `2006-06-32` and `8204-84-03`. openpyxl could not
  open the twin at all, while validation passed on both files. Every
  date cell now names a real day, and openpyxl reads 118 dates and 2
  strings. *Cost:* those made-up cells pile up at the top of each
  field's range, and 108 of 118 fall in December.
- **A file that reads two ways is asked about.** `id,measure|low|high`
  had silently been read with the bar, and code splitting on the comma
  read `029` where the column holds 100 to 103. The competing reading is
  now recorded and asked about, and `--delimiter` declares it. The
  twin's cells are made up under the reading taken, so code splitting
  the twin by the other character can still find ragged rows.
- **Other fixes.** A quoted title line, a regression of this stage
  caught before it merged, had left a twin failing about 120
  obligations that synthtwin could not read back. Two number formats
  of one kind (`0%` beside `0.0`) had collapsed into one, and are now
  refused by name. ISO dates stored as text had come back as `45315`.
  Empty strings had become blank cells. A hostile cell reference had
  taken 2.592 s to refuse, and now takes 0.000 s. A spreadsheet packing
  a million cells into 5 MB had been read in 4 s and 630 MB, and is now
  refused in 3 s at a peak of 539 MB, under the 600 MB the ledger holds
  it to.

**Accepted as a limit (2026-09-18).** The reader still accepts a workbook
date cell that names no day, when another program wrote it.

### Fixed: far fewer published counts can single out one row (stage 2b, 2026-09-16 to 2026-09-18)

**Many published counts could single out one row, either directly or
by subtraction.** In one example, 400 five-figure numbers, 399 codes
and one `hello` published counts from which 800 − 400 − 399 = 1. The
rule that no count, remainder or difference may name a row had been
written out four separate times. It is now stated once and applied to
every census of how the table was written, and since the extra review
round to the file's own lines. A lone CRLF at record 57 had been
published as runs of 57, 1 and 63 lines, and no longer is. It does not
yet reach everything: the exact smallest and largest values are still
published, and one row can hold them (stage 3), and the counts of one
accepted as limits below still stand.

**The owner's eight rulings of 2026-09-17, all built:**

1. **A record number's shared prefix is published.** Results are in the
   table above.
2. **Held-back label levels publish a pooled total only.** On 2,000
   Zipf codes at a floor of 11, the held-back single-row levels fell
   from 215 to 151 and the largest held-back level from 10 to 4. The
   distinct count of 414 was unchanged.
3. **A workbook with a second table stays refused**, and the message now
   asks which sheet is the table.
4. **Missing words pooled below a raised floor count as absent.**
5. **A label row recoverable by subtraction counts as missing.**
   `F` 480, `M` 519 and one `U` at a floor of eleven now publish two
   levels and one missing cell. Work at the close and in the extra
   review round closed four more shapes that forced a count of one. These were a clinical site column with
   three one-patient sites, one lower-case `f` beside 490 `F`, 201 − 100
   − 100 = 1 across sibling totals, and 120 site codes written once each
   beside `NORTH` and `SOUTH`.
6. **A spelling below the floor counts into the commonest.** 400 stamps
   with one `t` publish `{"upper_t": 400}`. The first repair pooled the
   rare spellings instead, and made one `T` among 5,000 space-separated
   stamps turn 4,998 of the twin's stamps into `T`. It was replaced.
7. **The prefix is published per system.**
8. **An ambiguous first row gets placeholder names and a question.** A
   headerless export whose first record was `CASE-ZEBRA-471,Northfield
   Clinic 3,<0.10` had published that record as the column names,
   described 239 rows where the file holds 240, and written the record
   into the twin. It now describes 240 rows under `column_1` to
   `column_3` and asks the question. The same holds for `R001,North
   Unit,<0.10` with no title above it.

**Costs.** A file with fewer than the floor's number of respelled cells
describes, and validates, as the file without them. A column name such
as `2019_total` over numbers now gets placeholder names and a question.
A spelling common enough to publish can be held back to hide a single
stray cell beside it.

### Fixed: what three review rounds found, and how each was closed (2026-09-16 to 2026-09-18)

**Every round found real defects, and some fixes had to be repaired
again after a second look.** Each fix was reproduced before it was made,
pinned by a test built from that reproduction, and checked by
withdrawing it to confirm a test turns red.

- **The final Codex round of stage 2b (2026-09-16): 52 items.** These
  were 7 on dates, 8 on numbers, 10 on labels, 19 on files and 8 on the
  merge. They were fixed on four branches and merged. An independent
  check re-ran all 52: 50 fixed, one partly (row order kept, but 119
  distinct numbers of 120, closed in the repair that followed), and one
  waiting on the owner, which became ruling 4. The check of the merge
  found one blocker, six major and five minor items. The blocker, three
  of the majors and two of the minors were repaired; the time of day,
  heavy tails, a repeated count of one and three minor workbook and
  date items were measured and carried. The round's verdict files were
  lost in a restart. The round was not re-run, under the rule of one
  round per landing.
- **The independent review of the close (2026-09-18): nine items,
  four of them blockers.** Rulings 5 and 8 held only on their sharpest
  cases, and each broke on a common shape. Both were widened, and the
  extra round then broke each once more on another shape; both were
  closed again there, apart from the autofilter limit accepted below. A
  spelling written by one row, a comma in a made-up value, and the "not
  your data" sentence were also fixed. A separator census at a raised
  floor was only partly fixed, and a percent column that writes two
  fraction widths still misses both (carried). One finding stays with
  the owner: a
  timestamp column whose rare mark is absorbed can publish a description
  no file satisfies. Its twin fails and describes itself again as a
  two-value column, and the quality report names all three missed
  obligations.
- **The extra Codex round (2026-09-18): 39 items, nine of them
  blockers.** These were 10 on dates, 10 on numbers, 10 on files and 9 on
  disclosure, and all four passes rejected the tree. Each area was fixed
  on its own branch, and each fix was checked by a second reader, which
  found more on every branch. The four were then merged. A final check
  re-ran all 39: 35 closed with numbers on their own reproductions, and
  the 4 that still reproduced were confirmed as never closed rather than
  lost in the merge. Of
  those four, one is now fixed and the loss of fractions of a second is
  now named in the twin's report. The other two went to the owner: the
  identifier room ratio, since accepted as a limit, and the scale of a
  pooled population of numbers. The same check then spent an hour on
  realistic tables of its own and found one blocker, five major and two
  minor problems. Four are fixed above: the headerless first record,
  month-name dates, a count of one in the census of missing values, and
  workbook date cells no reader could open. The notation mix and the
  delimiter residue are not, and the red tests are the placeholder
  below.

**The four fix branches of the extra round had each run only their own
area's tests.** Together they left 56 tests failing elsewhere, and each
one was resolved on its own. A skeptic then worked out every changed
number again from its rule, without looking at the fixer's number:

| resolution | tests |
|---|---|
| a real defect, fixed in the code | 14 |
| a number a ruling deliberately moved, re-derived from the rule | 18 |
| a guard that had stopped catching its defect, re-armed and mutation-checked | 39 |

The counts include neighbouring tests the repairs reached. No assertion
was loosened, and no expected value was copied from the tool's output.
The merged suite came to 6,763 collected, with one failure: the state
page's own count.

**Paid back.** Two frozen reference cases for the date merge rules had
stopped reaching the rules they were written for. The rules were not
dead: a census naming one width word over fewer cells than the column
holds reaches both. Two new frozen cases reach them, each with a mutant
that moves its cells.

### Fixed: what the owner asked for on 21 September, and what the second CI run found (2026-09-21)

**A pooled column of numbers beside labels now publishes its MEAN and not its spread** (owner, 2026-09-21). The first attempt at this published both, and that was worse than the defect: on the owner's own shape the published spread was exactly the smallest a pool of ten different whole numbers can have, which forces them to be ten consecutive numbers, and the mean then says which ten. The description gave away the ten values the floor was holding back. Publishing the mean alone is one equation over as many unknowns as the pool has levels.

| | before | after |
|---|---|---|
| the twin's numeric mean, where the table's is 187.08 | 100 | 187.08 |
| the reader's smallest number of surviving arrangements, over 72 shapes | 1 | 1,224 |
| what the validator checks | the mean and the spread | the mean alone |

Four earlier refusals gave way to one counted rule: the published mean must leave the values room to move, counted exactly — how many sets of the pool's own different numbers, on the grid its values stand on, inside the width the column shows, add up to what the mean and the count say. The bound is a thousand. It catches a shape the old rules never saw: six one-figure numbers beside a published one-figure number passed all four and the mean pinned them to sixteen answers. **The cost, stated:** a pool's spread is no longer verified, so a twin whose pooled numbers are too tightly or too widely spread is no longer caught by that check. The twin's pooled spread runs about 2 out on the owner's shape.

**A twin no longer fails a description its own absorbed mark produced.** Ruling 6 counts a mark worn by five rows into the commonest, which is right; what was wrong is that the description then promised three distinct values the twin could not hold, so the tool called the twin wrong for obeying it. A new rule, G7.9, buys back the distinct count within the floor's own budget. The first attempt overshot — a twin that had been clean came back holding six values where five were published and missing two checks — and the repair lands it exactly: five held, nothing missed, the real file clean throughout. One narrower shape, a census mixing upper and lower `t`, still misses one check where it used to miss three.

**The suite costs less, and CI costs far less.** Nothing was deleted, skipped or weakened: the collected set is identical. Three files stopped rebuilding the same corpus for every case — one battery of three walks went from 129 + 119 + 115 seconds to 131 + 0.06 + 0.06 — and the suite is now split five ways in CI with a job that proves the shards are exactly the collected set, no file twice and none missing. One process: 50 min 47 s for 7,174 tests. Heaviest shard: about 13 minutes, against cells that had been costing 1 h 20 m to 3 h.

**The second CI run was red again, on a layer under the first.** Every one of these is a test that could only pass in the arrangement it was written in:

| what CI saw | the cause |
|---|---|
| two failures on every cell, including the ones where nothing else failed | two tests asserted the answer for the machine they ran on rather than testing the rule; on a runner the policy answered before their patched answers were read |
| `TypeError: read_text() got an unexpected keyword 'newline'` on 3.10, 3.11 and 3.12 | that keyword arrived in 3.13 and the floor is 3.10 |
| seventeen Windows-only failures | the refusal message legitimately names the file, and a Windows temporary path contains `AppData`, which contains `Data` — the sheet name the test was checking had NOT leaked |
| about 25 failures in the `minimums` cell | openpyxl is not installed there, and the tests failed instead of skipping |

Each carries a guard against the next one: a reader that scans the tree for standard-library spellings newer than the floor, beside the one that already scans for platform-gated calls, and one named skip for the cross-check reader. That skip lands at the point of use — 59 of the 62 cases run synthtwin's whole half first and skip only the second reader, so a regression still turns them red where openpyxl is absent.

**And the oracle was caught copying the code it checks, twice.** `K-2B-42` allows no more than 176 of its functions to score 0.60 or above against their closest shipped function. A landing added one at 0.67 — same name, same shape — and the bound was not moved: the function was rewritten from the method's statement of its rule, which had to be COMPLETED first, because three of its clauses existed only in the shipped code and one frozen case. Its skeptic then found those newly written clauses were witnessed by nothing, and added seven mutants that are now red.

### Fixed: the first CI run of stages 1, 2 and 2b, and the three defects it found (2026-09-20)

**Every static check passed and every test cell failed** — lint, types,
the offline scan, provenance, decontamination, sensitive paths and build
all green; five Pythons across Ubuntu, Windows and macOS all red (pull
request #6, run 35508922164). None of the three was a defect in the
product: each was a test that could only pass in the arrangement it was
written in, and `src/synthtwin` is untouched by this landing.

| what CI saw | the cause | what the suite does now |
|---|---|---|
| `a network operation was attempted` | the readings battery ran its twelve columns over a process pool, whose machinery takes a socket, in a suite that is network-dead by design | three columns, serially — 25 s of the battery's 95 — holding all three of its missed counts and the two columns the accepted trade moved; the whole battery stays with the driver the ledger already names |
| `peak_mb=703 vs at_most 600` (539 here) | peak memory was judged in the ordinary suite, and it moves with the platform, the Python and the allocator | the refusal, and the cap that produced it, are judged everywhere, word for word against the sentence the cap builds; peak memory is recorded everywhere and judged only on the quiet reference machine, never on a runner |
| `SystemExit: 2` from the KPI guard | CI installs the wheel built from the commit and tests THAT, on purpose, so the package does not sit under `src/` | the guard asks whether the imported package IS this tree's code, byte for byte, rather than where it sits — and still refuses a worktree that imports another checkout's source, which is the mistake it exists to catch |

**The suite costs 54 minutes here and up to three hours on a two-core
runner**, and one cell ended at 3 h 00 m 06 s. That is measured and left
for the owner to decide: the twenty slowest cases are 54% of the run and
the top three are 33.5%, two of them fixture setup shared by many tests,
so the lever is sharing a fixture rather than deleting a test.

### Fixed: what a fourth review round found, and an oracle that copied the code it checks (2026-09-20)

**A missing value reopened the worst defect of the stage.** One `NA`
anywhere in a numeric column defeated the rule that stops a headerless
file publishing its first real record as the column names: 240 records
described as 239, the record's own text published as the header, and no
question asked. Two independent passes found it, in delimited text and
in Excel. The rule now drops recognised spellings of no value from its
evidence and reads a censored reading as a reading, and both formats are
pinned by the reviewer's own reproduction.

**The round raised 28 items across five passes, all rejected, all
closed.** The rest of the disclosure pass: a judged placeholder's
occurrences, less its named spellings, gave a count of one; label form
censuses bypassed the ruling that a level recoverable by subtraction is
missing; a mixed date and timestamp census exposed a singleton; a
plus-sign census omitted a population you could subtract; formula counts
revealed a lone literal cell. Numbers and dates: the mode repair
accepted the wrong frequency; absorbed identifier counts changed a
column's usable type; exponent spelling stayed broken; the calendar
repair corrupted published text labels.

**Five of the items were measurements that did not measure.** The
decontamination driver counted the files it listed rather than the files
it scanned, so an empty scan read PASS; the KPI runner printed a failed
driver's exit status and then discarded it, so a broken driver could
produce a complete PASS; one KPI survived the removal of UTF-16 support
outright. A measure that cannot fail is worse than none, because it is
believed.

**And the merge caught what no branch could see.** The oracle exists to
check the generator without being it, and `K-2B-42` measures that: no
more than 176 of its functions may score 0.60 or above against their
closest shipped function. One of the round's new rules was a
line-by-line transcription of the code it checks — the same three early
returns in the same order, the same names, the same final expression —
and the count crossed to 177. It was rewritten from the method's own
statement of the rule, not by moving the bound. All ten vector files
rebuild byte-identical, so no frozen cell moved, and 324,576 measured
pairs disagree nowhere with the transcription it replaced.

### Added: a ledger of measured outcomes, with a one-command runner (2026-09-19)

**Six thousand tests passing do not tell you that a UUID column still
comes back 800 of 800, or that a 20,000-row twin still builds in
seconds.** Every phase and stage now has its outcomes recorded as
measured numbers, and one command re-measures all of them:

    .venv/bin/python tools/measurements/kpi_run.py          # about 2 minutes
    .venv/bin/python tools/measurements/kpi_run.py --slow   # timings and scale

`tests/kpi/ledger.json` holds 147 KPIs across phases 0 to 4
and stages 1, 2 and 2b, 29 of them headlines. Each has its
value, the commit it was measured on, and a fixed rule for passing.
132 are green, 11 are open with the stage that owns
them, and 4 are limits the owner accepted. The runner prints
every KPI against its rule and exits non-zero if any drops, even when
every test passes. It is run at every stage close.

| a few headlines | before | now |
|---|---|---|
| generate 20,000 rows x 20 numeric columns | 1,113 s | 23 s |
| most copies of one number, where the real mode is 62 | 760 | 62 |
| US dates parsed by the source's own format | 0 twin cells | every cell |
| `^REC\d{7}$` on a prefixed record number | 0 of 800 | 800 of 800 |
| eight realistic shapes: real tables and twins passing | twins 6 of 8 | 8 of 8 each, floors 1 and 11 |
| twin columns whose pandas type differs from the real one | 1 | 0 |
| cases where the generator matches the independent oracle | 95 | 107 |

An open KPI asserts a ceiling rather than its target. The suite stays
green while the ledger shows the KPI open, and fails if it gets worse.
The ledger checks itself: every test it names must exist and be
collected, a skipped test counts as a failure, and a mutation shows that
each of those checks can fail.

**Building it found five things the tests had missed.** Four are above:
the speed regression, the judged `-999`, the spread, and the readings.
The fifth concerns privacy. The headline "no twin row is a real row"
passed only because its table's made-up record number made every row
differ. On two of four realistic shapes, 1 twin row in 400 equals a
real row, record number included. That happens when a made-up number
coincides with a real one, which the owner accepted, and the rest of the
row coincides with that record's own values. This is open, and it is
one question for the owner.

### The owner's decisions recorded in this stage

- **2026-09-15.** The twin writes everything as the source wrote it,
  which reverses the earlier decision to write dates in ISO form.
  synthtwin reads Excel and delimited text only, and openpyxl is a test
  dependency only.
- **2026-09-17.** Rulings 1 to 8, as listed above.
- **2026-09-18.** Seven limits accepted, plus fractions of a second
  written as nought (below).

**Accepted by the owner (2026-09-18), in the owner's words:**

- real record numbers can reach the twin when a declared identifier has
  little spare room: 100 of 1,000 at `REC` plus four figures, and all
  900 when `100` to `999` are declared ("Identifier room: no worries.
  Fine");
- the twin can rebuild a held-back rare value: 55 of 251 held-back cells
  on a fresh sweep, 1 of 19 columns rebuilt exactly ("Rare values: ok.
  Fine");
- an autofilter can still make an ambiguous first row the header ("I
  wouldn't care");
- the count of unreadable cells can be one, which subtraction gives
  anyway ("If makes no difference, don't loose your time");
- the reader accepts a workbook date cell that names no day ("wouldn't
  be worried about").

**Left as they are after the owner asked what they change.** Free text
publishes that one cell is numeric. The missing count that ruling 5
sends a pooled label to can be one. Neither changes the owner's code or
results. Closing the first would move every numeric column's
description. Closing the second would withhold missing counts on every
column.

**The orchestrator's calls under the owner's rule, each open to
reversal:**

- fractions of a second are written as nought;
- the spread fix waits for stage 3;
- the readings trade is accepted;
- descriptions written by hand that no producer writes are left as they
  are;
- a record number's class counts can show that one record below the
  line exists, but not its value;
- the column-wide fill keeps its trade on grids of whole numbers.

**Still with the owner:**

- whether a made-up record number that coincides with a real one may
  carry that real row whole;
- a pooled population of numbers beside labels loses its scale: a mean
  and standard deviation of 187.08 and 39.03 came back as 100 and 3.03,
  and the twin's report says the placement is not a fact about the
  table;
- the timestamp column whose absorbed mark leaves a description no file
  satisfies.

### What later stages inherit

- **Stage 3:** the exact smallest and largest values that one row can
  hold, and the disclosure floor. At the shipped floor of 1, the
  every-role table publishes 147 labels held by one row. Stage 3 also
  inherits the spread of bell-shaped columns, and the mean and spread of
  heavy-tailed columns: on one 5,000-row column the twin's mean was 41%
  high and its spread 161% high.
- **Stage 3b:** the time of day inside timestamps.
- **Stage 4:** the largest tables. 100,000 rows by 20 columns runs in
  264 s; 1 million and 2 million rows have not been measured.
- **Stage 6:** relationships between columns (a rank correlation of
  0.747 comes back as 0.027), and the walk that pairs the numbers of a
  three- or four-number cell.
- **Also carried, named one by one in the ledger's known-miss entry and
  held there at a ceiling:**
  - two date-width allocations;
  - one record-number layout, `(-%)`;
  - a sign band given more slots than it has numbers;
  - the read floor of hand-built descriptions;
  - two generator passes the oracle does not yet mirror;
  - a column that mixes notations can lose one distinct number;
  - a Fortran `D` exponent written as stand-ins;
  - a percent column with two fraction widths.

### Fixed: what a confirmation review found after stage 2 closed (2026-09-15)

**An independent review of the committed stage 2 answered "not fixed",
and six verifiers reproduced every finding.** Five are fixed here; two
older ones are carried.

- **A column of dates could still read back as a column of two values.**
  The census repair guarded literal spellings, so it handed the last copy
  of a day a `t` beside that day's `T`, and ten cells of three values,
  case ignored, came back binary with nothing said, on every seed. The
  repair now never leaves a column one value fewer once case is ignored,
  the oracle mirrors it, and a twin whose values fall to two where the
  description counts three or more is named.
- **Decimal-comma recounts mixed two readings.** The generator's own
  report and the validator read absence and class in the ordinary
  grammar, so labels beside decimal-comma numbers were counted as numbers
  and a grouped `-999.000` as the absent `-999,000`: the report listed
  false deviations, and the real table failed its own description. Both
  now read a declared column in its own grammar and translate only what
  is left. This predates stage 2.
- **A lost thousands mark on a currency, unit or labelled column was
  silent.** The warning now covers the cores of every wrapper of an
  affixed column and the numeric half of a column of numbers and labels.
- **The round-trip tests could not see a failed check.** `cli.main()`
  returns its exit code, and the helpers dropped it, so a validation that
  missed an obligation passed. They read it now, and a test fails if any
  test drops a command's result again. That is how the decimal-comma
  failure above came to light.
- **A day declared absent in every spelling still received values.** A
  whole-unit rank that lands on such a day now steps to the nearest
  present day inside its own window, and the oracle mirrors it.

Each fix is pinned by a test built from the review's reproduction and
mutation-checked by withdrawing it.

**Carried, confirmed older than stage 2:**

- the validator estimates the widest stratum of a numeric column from the
  description while the generator uses the real one, so it can call a
  faithful twin's percentile rung MISSED -- on a 2,000-row column, 6 seeds
  of 8; this bears on the reliability of statistics and belongs to a
  later stage;
- a small column of numbers and labels that falls to a free-text or
  long-tail role writes stand-ins that cannot reproduce its numeric forms.

### Fixed: stage 2 closed after an independent audit (2026-09-14)

**The audit found stage 2 was not done.** Five probes and a verifier who
re-ran every reproduction measured that grouped whole numbers below a
million, such as `12,345`, `$12,345` or `+1,234`, still came back bare:
400 cells of 400. The rule counted a lone group as settling nothing,
although the statistics already read it as thousands. And the stage's
own gate, "a round-trip test per shape", had no test behind it: the
comma witness passed with one grouped cell in six hundred.

**What changed:**

- a lone group now proves the comma, so whole numbers keep it;
- the mark is published where the proving cells reach the smallest
  group and outnumber the bare ones, so five bare cells no longer strip
  it from 395 grouped cells; one grouped cell among many still
  publishes nothing;
- an accounting bracket such as `(123.45)` is no longer counted as a
  figure, which had stripped the mark from a column of grouped charges;
- a declared decimal-comma column grouped with points, `42.037,34`,
  publishes `.` and its twin writes it, where the points were dropped
  although the help promised the twin writes numbers as the table did;
  the loader refuses a point anywhere else and a comma there (GS1);
- the checker offers grouped spellings whatever the published mark, so
  a real table is never missed for commas the description could not
  prove;
- the absent-spelling exception offers the marks the column's own
  census names first, so a column of spaces and `t` never gains a `T`;
- the census repair allows a repeated spelling, which it had refused on
  every column of midnight dates, and runs in linear time (80,000 rows
  had taken 18.9 s against 2.9 s);
- a value left wearing a spelling the table declares absent is named in
  the twin's report, and so is a column of moments whose absent cells
  were pooled below the group size, where no spelling can be avoided;
- report sentences that overstated are corrected: the marks each
  written "as often as the description records it" on a column with a
  pooled or mixed census, and dates reading "the same" on a column that
  mixes bare dates with moments;
- the describe-time summary names the mark, the census and the midnight
  statement, and the claim guard catches contractions and near-synonyms
  of the exemption it bans.

**One review round then rejected the closure, and was right four times.**
Allowing a repeated spelling in the census repair could erase the last
copy of one, and five cells of three spellings came back as a column of
two values; the repair now never leaves a column one spelling fewer.
The decimal-comma exchange decided from the text which cells were
numbers, so a label such as `1,234,567` beside the numbers became a
measurement and a grouped end matching an absent spelling was left
unexchanged and lost; the exchange now touches exactly the cells the
numeric machinery wrote. A small column at a raised floor could lose
the mark in its twin with nothing said; that is now a named deviation.
And the warning about pooled absent cells fired on an ordinary blank; it
is now a remark, raised only where missing values were declared. The
oracle trims absent spellings as the reader does, a departure test that
never departed now does, the claim guard lets "does not necessarily
satisfy" stand, and the contract's GS1 scope matches the loader.

**Measured.** `tests/test_stage2_round_trip.py` describes the twin again
for 19 shapes -- whole, currency, signed, decimal, straggling, bracketed
and decimal-comma numbers, millions, the three marks and their mix,
midnight at three precisions, with a `T` and with an offset -- and finds
every stage-2 fact returned, the twin checked with nothing missed and,
where its spelling is a published one, the real table too. The shapes
designed not to return -- a pooled mark, dates mixed with moments, a day
declared absent -- are pinned beside it with what they do instead. Each
new rule is mutation-checked: put back, it turns a test red.

**Carried, not fixed:**

- a number grouped with a space or an apostrophe is read as free text;
- an accounting bracket or a plus sign on a decimal is not a published
  number style, so the twin writes a minus and drops the plus, and a
  real table with brackets misses its own spelling check;
- a column mixing bare dates with midnight moments is written wholly as
  moments, and a slashed format is written in ISO form;
- a column only partly at midnight, or at midnight on the shared clock,
  still gets invented times;
- at a raised floor, a withheld mark can be attributed by elimination
  when only one mark is left unnamed;
- twins of date columns spread values across days more evenly than real
  tables (predates stage 2);
- continuous integration has not run on this branch.

### Fixed: a moment keeps its own separator, and a date held at midnight stays a date (stage 2, part two, 2026-09-14)

**A stamp written `2025-09-04 06:16:00` came back from the twin as
`2025-09-04T06:16:00`**, so code that split or searched on the space
worked on the twin and silently did nothing on the real table. **A date stored as the date
plus `00:00:00` came back with invented times of day**: 800 of 800 real
rows at midnight became 2 of 800.

Every datetime block now publishes two more facts (plan P4-D39), both
REPORT-ONLY and listed in the quality report:

- **`datetime_separators`**, the census of marks between day and clock
  (`upper_t`, `space`, `lower_t`), floored like `utc_offsets` with a
  `(withheld)` pool. The generator spends it by an evenly spread
  rotation that draws no random word, so each mark is written its
  published number of times and no link is invented between how early a
  moment is and how it was spelled. A withheld pool is written with the
  commonest mark and named in the twin's report.
- **`all_at_midnight`**, true only for a local column whose every parsed
  moment stands exactly at midnight, fraction included, and whose parsed
  cells reach the smallest group size. Such a column is generated and
  checked in whole days and written back with a midnight clock. The
  twin's report recounts the midnight cells it wrote and names any miss,
  because the checker's day-counted windows could not see one.

**Measured on five 400-row shapes.** A space column comes back 400 of
400 with a space. A column mixing 300 spaces, 50 `T` and 50 `t` comes
back with exactly those counts, about 75 spaces in every quarter of its
dates. A date column at midnight keeps 400 of 400 cells at midnight. The
twin and the real table both pass the checker with nothing missed.

**The loader** refuses a census name outside the vocabulary, a named
count below the floor (D12), a census whose total is not the cells that
write a clock or that gives a slashed format a mark other than a space
(D13), and a midnight statement on the shared clock, below the floor, or
beside a published moment that is not at midnight (D14).

**The oracle mirrors both rules** in the same commit (A-P4-59), written
from the statement rather than the implementation, and two frozen branch
cases pin them: `midnight_days` and `mixed_marks`, each with a mutant
that moves its cells. A new test holds the two writings to agreeing over
6,000 censuses and 9,000 cells, and each of three in-memory mutants
turns it red. Every earlier frozen cell is unchanged; both vector files
gained the two keys on their datetime cases.

**One review round rejected the first build, and was right twice.** A
generated moment could equal a spelling ANOTHER column declares absent,
so a present value read back as missing; the writer now checks every
column's absent spellings. And where a cell's mark had to change to step
around an absent spelling, the census was left one short in one name
and one over in another with nothing said; another rank now takes the
owed mark back, the finished marks are recounted, and a shortfall no
rank can absorb is named. The loader also refuses a withheld pool larger
than the unnamed marks could hold, the claim guard catches clearance
said with a preposition, and the oracle mirrors the absent-spelling
exception and its repair, held to the generator over 4,000 columns.

**Also in this landing.** The claim guard's seventh family now names
regimes by their acronyms and catches an exemption claimed by clearing a
regime, not only by lifting it. The sentence saying analysis code
developed on the twin runs is qualified on all four surfaces that
shipped it: running unchanged is the aim, and nothing guarantees it.

**Carried, not fixed:**

- a column grouped with a space or an apostrophe is read as free text,
  so its twin writes stand-in text; a strict expected failure pins it;
- a column only partly at midnight, or at midnight on the shared clock,
  still gets invented times;
- neither new fact is an obligation a file can miss;
- at a floor of one, a census name can stand for one row's spelling, the
  same posture as `utc_offsets`, until landing 3 raises the floor;
- the two published ends take their marks from the rotation, not from
  the real ends' own cells;
- on a midnight column, a calendar placeholder day inside the range is
  now hit by whole-day ranks far more often than before;
- the assembled contract gains two more keys its build folder does not
  hold (residual R-P4-113).
- no frozen case declares an absent spelling, so the exception and its
  census repair are pinned by the agreement test, not by committed
  cells.

### Fixed: a thousands comma is written back (stage 2, part one, 2026-09-14)

**A column written `2,198.92` came back from the twin as `2198.92`.**
Code built on the twin then met the comma for the first time on the
real table and silently dropped every value above a thousand. The
profile now publishes `group_separator` on every numeric block (`""`
or `","`), and the generator writes the comma back.

**The evidence rule** (`taxonomy._group_separator`). The mark is `","`
only when all of these hold:

- no decimal comma is declared for the column;
- every `plain`, `leading_plus` or `decimal` cell with four or more
  whole figures carries a comma;
- no padded or exponent cell carries one;
- the cells proving the grouping reach `small_cell_floor`.

Otherwise it is `""`. The generator groups `plain` cells always, and
`leading_plus` and `decimal` cells only where no leading zeros were
written. The validator accepts grouped spellings of each permitted
form, and the independent oracle carries the same rule. The quality
report lists the mark on every numeric-family column as a fact no file
is held to.

**Measured.** A naive parser gives a mean of 409.97 on the twin against
412.11 on the real table, where the true mean is 917.93. The defect now
shows up on the twin, where it can be fixed. The twin and the real
table both validate with nothing missed. A declared decimal-comma
column, a column mixing grouped and bare cells, and a padded column
all publish `""`. Three independent groupers agree on 30,000 spellings.

**One review round** found nine defects, all corrected here:

- the comma leaked into decimal-comma columns;
- one grouped cell grouped a whole column;
- padded and exponent cells were grouped;
- the generator grouped spent zeros (`+0,001,234`);
- the loader accepted values other than `""` and `","`;
- the reference profiles, including the joined case's two parts,
  lacked the key;
- the contract's key counts and role matrix were stale.

A moment-separator and midnight census built in the same pass broke
profiling and was backed out whole; it returns as part two.

**Frozen artefacts moved, by one key only.** The profile golden and
the twin golden's description hash were re-recorded after a diff showed
`group_separator: ""` as the only addition. Both reference vector
files gained the empty key and no cell moved. Contract v6 gained its
table rows, a matrix row, and a place in the post-freeze list, all
under plan P4-D38.

**Carried, not fixed:**

- the validator accepts a grouped spelling but does not require one, so
  a twin written bare still passes;
- no frozen reference case publishes `","`;
- at a floor of one, a single grouped cell is enough to publish the
  mark;
- a column grouped with a space or an apostrophe is read as free text
  (measured after this entry was written; it said "the wrong number");
- a moment's own separator and a date held at midnight: part two.

### Fixed: describing and generating were quadratic, and it was one idiom (stage 1, 2026-09-13)

**Describing a table and building a twin both grew with the SQUARE of
the row count**, and no guard in the suite looked at growth at all.
Measured on the tree this landed on:

| case                                | before  | after |
|-------------------------------------|---------|-------|
| build a twin, 20,000 rows x 20 numeric | 1,113 s | 19 s |
| describe, 200,000 rows x 2 labels      |   390 s | 10 s |
| describe, 100,000 rows x 20 numeric    | (hours) | 96 s |

A 100,000-row table now runs end to end in about three and a half
minutes. Before this it could not be done at all.

**Two causes, in two places.** Every list in the package was grown with
`x = x + [item]`, which rebuilds the whole list on each pass, in 669
places -- 661 with a plain name as the target and 8 more where the list
sits in a slot of another container. `tools/offline_scan` refuses
`list.append`, so that quadratic form was what the rules left standing;
`x += [item]` is accepted and is amortised constant. And
`generation._shape_sizes` reduced runs by calling `_merge_nearest` once
per merge, which rescans every adjacent pair and rebuilds both lists; it
now calls `_merge_down`, a binary heap over a linked list, written
without a new import because `heapq` is not on the allowlist.

**Nothing the tool produces changed.** The profile, the twin and the
twin's report were hashed for three tables before and after: identical.
`_merge_down` was checked against `_merge_nearest` on 4,200 randomised
cases over six adversarial families -- all-equal values, whole and
fractional mixes, the 1e308 and 1e-320 magnitudes that exercise the
overflow rescale, signed zeros, and the ladder's own
plateau-and-transition shape -- agreeing on every length and on the
`repr` of every value. Review independently reproduced this over
267,330 exhaustive small cases and 6,000 seeded ones.

**A new guard, `tests/test_no_quadratic_list_growth.py`.** It reads the
source and names any list grown by copying, file and line. It is static
rather than timed because the first version was timed and review killed
it: with the defect restored the wall-clock ratios were 2.5 and 2.2,
under the threshold, so the guard accepted a quadratic tree, while a
single 0.6-second pause made repaired code fail. Counting the defect
beats timing its symptom.

**Review found three blocking items and all three were repaired**: the
eight container-slot sites above, the timing guard, and a recorded test
count that guaranteed a gate failure.

Suite: 4,407 passed, 51 skipped. Lint, strict types, the offline import
scan, provenance, decontamination and the signed attestation all clean.


### Phase 4 is closed (2026-09-11)

**Every column type a real table holds is read, or declined with an
explanation you can act on.** Fourteen column roles instead of six:
numbers wearing a unit or a currency mark, two numbers in one cell,
clock times, dates written with dots or a two-figure year or day
first, and long tails of labels where a handful repeat and the rest do
not. Your own word for "no value" reaches the twin at its count.
Leading zeros survive at their field width. The twin says which of its
cells synthtwin made up. And where the values cannot settle what a
column IS, synthtwin asks you in a file instead of guessing.

**What closing does NOT mean.** Sixty-six entries of the phase's own
register are **carried to Phase 5 by name rather than built**, grouped
in the plan's closure section by what a reader would do about them.
Eight of the ten acceptance criteria are met; one is met on a rule
whose own report was false until this phase repaired it; and **one is
unmet and named** — the reference vectors for two generation branches
were not written, so those branches are pinned by tests rather than by
a frozen case with a mutant.

**And closing is an owner decision, not a review verdict.** Nothing in
this repository describes Phase 4 as review-ratified.

**Phase 5 is next, and it is the one that matters most for
statistics:** the twin still carries no structure that crosses two
columns — no correlation, no formula between two columns, no shared
pattern of empty cells, no ordering between two event dates.

### Changed: the documents say what is true today

- **`docs/STATE.md` is one page again.** It is the file a person or an
  assistant reads first to find out where the project stands, and it
  had reached 3,814 lines by gaining a section per landing --
  narrative that belongs in this changelog. At that size nobody read
  it, so every session measured the project from scratch, which is the
  exact failure the page exists to prevent. It is 223 lines now, and it
  carries a rule of its own: **a landing adds nothing to that page
  except by changing a fact already stated there.**

- **Three facts on it had gone stale and are corrected.** It said
  review ran up to five rounds with a model that is no longer used; it
  said ten lint errors stood after the commit that repaired them; and
  it stated its own length as "~200 lines" while running to thousands.
  Each was a fact written in more than one place with one copy updated,
  which is now stated as the page's own rule: state a fact where it is
  measured and point at it from everywhere else.

- **`SECURITY.md` records what profile version 6 publishes.** That
  document tells an institution, version by version, what a description
  carries off the machine, and its entries stopped at version 5 --
  understating what travels, by omission rather than by a wrong
  sentence. Version 6's additions are now written out and priced by
  family: the censuses of written form, the per-label form count, the
  empty stretches of a numeric range, the distribution additions, and
  the two column types Phase 4 added whose affix pair and separator are
  text of your table. The questions file has an entry of its own.

- **`STATUS.md` describes the tool that exists.** It said the new
  column types, the long-tail categories and the missing-value
  reproduction were "planned and ratified but not built"; all of them
  are built. It now lists what Phase 4 actually gives you, names the
  sixth file, and documents `--code` and `--answers` beside the other
  options.

### Fixed: the twin's report told you your 'no value' spelling stayed behind

- **It did not.** For every column with an empty cell, the report said
  "the twin writes every one of them as an empty cell, so how your
  table wrote them is here rather than in the twin", and the heading
  above listed those spellings among the things "no twin can carry".
  Both were true once. They stopped being true when the twin started
  writing your own `NA`, `-9.99` or `Not recorded` into its cells at
  the published count -- and the sentences did not move with it.
  Measured on four twins: a declared `-9.99` column came out with 0
  blank cells and 20 wearing `-9.99`, and printed the sentence anyway.

- **Now it says which, spelling by spelling.** Each published spelling
  carries its own mark -- `-9.99: 20 cell(s) -- the twin writes this
  spelling in all of them`, or `the twin leaves these cells empty` --
  and the paragraph above says how many of the cells travel and what
  that buys you: code that filters on your own word for "no value" does
  the same thing on the twin as on your table. This matters for where
  the files may go, because the twin is carrying that word out of the
  run with it.

### Fixed: one number is no longer both 'not met' and 'inside its range'

- **The same page said both.** A column's `n_distinct` appeared among
  the facts the twin could not meet and, a few lines later, among the
  approximate facts with "inside the range" beside it. A fact that
  lands inside the range the method promises is a fact the twin held,
  so it is not listed as missed any more. It is still printed, with
  the published value, the achieved value and both ends of the bound.

- **And a fact whose range does not cover the published value is still
  listed.** Not every range is a margin around the number printed
  beside it: one column of the demonstration table publishes 84
  different values, its twin holds 224, and the range runs 106 to 240.
  The twin landed where the method said it would and nowhere near your
  table, so that stays in the list of facts it could not meet.

### Fixed: the advice for a column of codes wearing a unit named the wrong option

- **It said `--identifier` where it meant `--code`.** A column of
  values like `12 mg` carries a note saying synthtwin described the
  numbers as quantities, and offering a way out if they are really
  codes. It named `--identifier`, which publishes no value of the
  column at all -- so following it exactly threw away the distribution
  of codes you were trying to keep. It names `--code` first now, with
  what that publishes, and `--identifier` after it for a column that
  really is a record number.

### Added: the questions come back in a file you can fill in

- **Every `synthtwin profile` run now writes a third file beside your
  description**, named for your table and ending `-questions.json`. It
  lists the columns synthtwin could read more than one way, says what
  it SAW in each one -- how many figures, how many padded, what
  separates them -- and what it read each one as, and offers you the
  answers you can give with what each one would publish. It carries no
  value of your table. It is written on every run, whether there were
  questions or not, so a rule about where synthtwin's files may go
  never has to say "and sometimes a sixth".

- **`--answers FILE` hands it back.** Write an answer beside
  `your_answer` for the columns you want to correct, save the file, and
  run `synthtwin profile` on the same table naming that file. Your
  answers become the declarations -- exactly as if you had typed
  `--code`, `--identifier` or `--measurement` for each -- and the
  description records them as such, so it says who decided. Columns you
  leave blank keep the reading synthtwin made. It is the way to answer
  the questions when nobody is at the keyboard, which is most runs.

- **An answer that was not offered is refused rather than ignored.** If
  you write `codes` where the question offers `code`, synthtwin stops,
  names the column, shows you what you wrote and lists what you can
  write instead. Dropping a word nobody could read would have described
  your table the old way while your file said otherwise.

### Changed: synthtwin asks about your codes without showing your data

- **The list of columns to check now appears whoever is running the
  command.** It was printed only in a scripted run, and only when some
  other column had already raised a question of its own -- so a table
  whose only finding was this list showed you nothing at all. It is
  shown once, every run.

- **Every answer now says what it would really publish for YOUR
  column.** A column of numbers too large for the file format to hold
  publishes no average at all, and the "measurements" answer used to
  promise one anyway. If you have asked for groups of eleven, the
  "codes" answer no longer promises that every value is kept, because
  values held by fewer than eleven rows are not. Both sentences are
  worked out from your column and your settings now.

- **A column of two numbers in one cell says what pressing Enter
  actually does.** It said Enter would keep it read as two readings; it
  would not, because reading it that way is a change you have to ask
  for. Enter keeps it as text, and the question says so.

- **And a count of cells is never named below your smallest-group
  size.** A column with a single leading-zero value used to say "1 of
  them", which is a count of one on a surface that names no group
  smaller than you allowed. It says "some of them" now, and the count
  itself once it is at or above your floor.

- **Every column read as a number is now listed for you, under one
  question.** synthtwin has always asked about a column whose values
  gave it a signal -- figures with a leading zero, or every value the
  same width. It could never ask about the rest, because there is
  nothing to see: a register of drug concept identifiers six and seven
  figures wide is written exactly the way a column of ages is written,
  and a rule that guessed between them was removed from this tool years
  of work ago for guessing wrongly. So they are not guessed at and not
  singled out either. They are listed, once, with one question over
  them: which of these hold codes or record numbers? A person who holds
  the table answers it in a minute; nothing else can answer it at all.

- **The questions no longer print your values.** They used to show four
  real cells from the column, on the reasoning that you cannot answer a
  question about a column without seeing it. You can: what you need is
  what synthtwin saw, and it now says that instead -- "every value is
  written in figures alone, all 5 characters wide", or "and 167 of them
  carry a leading zero". That describes the column exactly as well and
  carries none of it, which matters because these questions are about
  to become a file you can save, hand to a colleague and send back.

- **Each answer says what it would publish.** "Codes" and
  "measurements" are labels; the choice is really between "an average,
  a spread, a smallest and a largest" and "every value exactly as
  written, with the number of rows that carried it". The questions say
  that now, and the reading that stands if you answer nothing is named
  and listed first.


### Fixed: a European date is read as a date, not as a quantity

- **A column of dates written `19.08.24` was described as a
  measurement.** It was read as the number 19.08 wearing the text
  `.24`, so the description published an average and a ladder over
  day-and-month numbers, and nothing said so. Measured on 300 rows:
  the profile's smallest and largest came out 1.01 and 28.12, and
  **151 of the 300 cells in the twin were not dates at all** -- months
  74, 85 and 62 among them. Analysis code that read your real column
  could not read its twin, which is the one thing the twin exists to
  allow.

- **It is a date column now.** The same 300 rows describe as dates
  running 2024-01-01 to 2024-12-28, the twin holds 300 real dates, and
  `synthtwin validate` on that twin misses nothing. Which field is the
  day is decided the way it already was for slashed dates: your own
  values first, then `--day-first`, then the stated default; and
  because the year has two figures, the column says out loud which
  century it was read in.

- **`--day-first` now reaches what its help text always promised.** The
  option said it reaches dates "written with dots, and written with a
  two-figure year". Until this release the two together were the one
  shape it did not reach.

- **A column of version numbers is still a column of version numbers.**
  `1.2.24` is how a version is written and, character for character,
  how an unpadded dotted date would be. Only the padded spelling is
  read as a date, which is the same rule the four-figure dotted dates
  have always used. The cost is written down rather than left to be
  met: a padded column whose every value is also a real date IS read as
  dates, exactly as `01/02/24` already was.

- **Your own values now decide which field is the day, even when you
  have not said.** A column of 300 dates where 299 could be read either
  way and ONE can only be a day-first date was read month first, and
  that one cell was reported as unreadable. The column had answered the
  question and the tool overruled it with a default. This was true of
  every shape whose day and month are both numbers, not only the new
  one. Where your values point one way, that way is used; where they do
  not, `--day-first` decides and the stated default stands.

- **A firmware version column stays a version column.** Values like
  `01.02.24`, `01.03.24` and one `01.00.24` were read as dates once the
  dotted two-figure shape had a reader: there is no zeroth month, but
  one odd cell in three hundred slipped under the tolerance for stray
  cells. A dotted value naming a zeroth month or day is now taken as
  the column telling you it holds versions. An ordinary stray cell, or
  a typo like `32.08.24`, is still tolerated exactly as before.

### Fixed: `--day-first` was quadratic, and nobody could see it

- **Describing a column under `--day-first` did work that grew as the
  SQUARE of the column's length.** The helper that counts how many
  cells each reading accepts built its answer by copying everything it
  had accumulated so far, one cell at a time -- the exact defect that
  was found and fixed for numeric columns long ago, and written into
  this module's own rules. It survived here because this helper only
  ran when you passed `--day-first`, and no growth test passes that
  option, so the walk sat unmeasured.

- **It was found by making the tool better at something else.** Once
  your own values decide the day-first question whether or not you
  declare anything, that helper runs on every column that could be
  dates -- and the growth guard that has watched numeric columns for
  months turned red immediately, measuring 14.4 times the work for four
  times the values where proportional growth is about 4. The list is
  extended in place now, and that guard is what pins it from here.

### Fixed: the decimal-comma message names the option that exists

- **A person whose file writes `1,795` for one and three-quarters was
  told to rewrite their own file.** The message said to write the
  column with a decimal point and run the command again. It said that
  for a fortnight after `--decimal-comma` shipped, and never named it.

- **Both messages name the declaration first now**, and the rewrite
  second, because rewriting still works and changes your file where the
  declaration does not.


### Fixed: a column of codes is no longer averaged in silence

- **A register of procedure codes, most of them bare figures and a few
  ending in a letter, was described as a quantity and said nothing
  about it.** Measured on 300 rows -- 280 five-digit codes beside
  fifteen `3074F` and five `3075F` -- the description published an
  average of 54,239 over the codes, a smallest, a largest and nine
  points between, every one of them a real code, and the profile
  carried no remark at all. Nothing on the screen, in the description
  or in the plain-language summary said a choice had been made.

- **The tool asks about that column now, instead of guessing.** Where
  a column can be read as a measurement carrying markers, as numbers
  beside labels, or as a coding system whose codes end in a letter,
  the description says so and names both of the options that settle
  it: `--measurement NAME` describes every number, and `--code NAME`
  keeps every value exactly as written and publishes no average at all.
  The sentence used to name only the first of those, which is the one
  that publishes MORE of your codes.

- **A column whose letter is written hard against the digits is
  declined out loud.** `13.5H` is a flagged laboratory result and
  `1234F` is a category of procedure code, and nothing in the values
  tells them apart, so the tool does not read such a column as a
  quantity unless you say so. Until now it simply fell to free text,
  and the message you met told you to rewrite your column as plain
  numbers -- while both options that read it correctly already
  existed and neither was named.

- **Two messages that were plainly wrong are fixed.** A column of
  hyphenated laboratory codes, which publishes no average at all, was
  told on screen that it was "being described with an average, a
  smallest and a largest"; that text now depends on what was actually
  read. And a column of zero-padded numbers was told in one place to
  use `--code` and in another to use `--identifier`, which are opposite
  things: `--code` keeps every code with the rows that carried it,
  `--identifier` publishes nothing at all. One answer per page now.

- **A question that should never have been asked is not asked.** 280
  readings beside twenty `<0.5` cells raised the question and pointed
  at `--measurement`, which would then have published a distribution
  over the detection limit itself. A mark that is no letter -- `<`,
  `$`, `%` -- is not this ambiguity, and raises nothing.

- **A marker written in another alphabet asks the same question.** The
  first version of this repair tested for English letters, which would
  have taken the warning away from a column of readings marked with a
  Greek letter -- a warning that column already had. The test is a
  closed list of symbols now, so a mark nobody listed is treated as a
  word and asks.

- **The counts in those sentences are the counts they name.** "How many
  of this column's values are a number with a word beside it" now
  counts exactly that: a cell whose marker is `<` is a comparison and
  not a word, and a cell reading `many H` holds no number, and neither
  is counted any more.

- **And the advice no longer promises more than your settings allow.**
  Both sentences said `--code` keeps every value exactly as written.
  That is true at the default, where nothing is held back, and not true
  when you ask for a larger smallest-group size, which pools rare codes
  away. They now say what is published under the size in force.

- **What is still true and is written down:** which of the two
  readings a flagged laboratory column reaches still depends on how
  often its flagged values repeat, so one column can be described two
  ways. Neither description is wrong -- both are now said out loud --
  but the choice is not predictable, and it is recorded rather than
  quietly left (residual R-P4-157, narrowed). A column that reaches a
  set-of-categories reading before the number rules is not reached by
  the new decline sentence at all, which is recorded too (R-P4-158).
  And the message on a column wearing a unit still points at
  `--identifier` where it should point at `--code`, for the same reason
  the padded-number message did; it moves with the next piece of this
  work, and is recorded rather than left to be found (R-P4-72).

### Added: a lab column of readings and markers is now described as both

- **A column that holds numbers AND words -- `4.2`, `7.8`,
  `NOT DETECTED` -- is no longer read as words alone** (closing
  residual R-P4-13). Until now a lab result with even a handful of
  `NOT DETECTED` cells fell to the free-text role or the long-tail
  role: the readings were counted but never described, so the twin
  carried no range, no middle, no ladder for them, and analysis code
  written against the twin met a column of text where the real one
  held a quantity.

- **The description now states both halves and the split between
  them.** A compound column publishes how many cells read as numbers
  and how many do not, and then a full quantitative description of the
  numeric half beside a full label description of the other -- the same
  two blocks the numeric and label roles have always written, each read
  over its own cells. The two counts add up to the number of present
  cells, so the description never speaks about part of a column
  without saying what the rest is.

- **The twin holds both.** Measured on a three-hundred-row column of
  295 readings and 5 markers: the twin writes 295 cells across the
  real range and 5 marker cells, and re-describing the twin re-detects
  the role with the same split. The count of different cells was
  measured on four shapes and four seeds each -- readings that almost
  never repeat, a numeric half of forty values over 280 cells, a coarse
  half of twenty-five, and markers differing only in case -- and was
  reached exactly every time.

- **A column of free comments is still free text, and a code column is
  still codes.** The rule asks whether the numeric half is a real
  quantity rather than a set of codes, and whether the words repeat
  like a vocabulary rather than reading like prose; a column that fails
  either question keeps the role it had. No column that already read
  well moved.

- **And if your table uses a comma for the decimal point, this works
  too.** A column declared `--decimal-comma` whose cells read `1,5`
  beside a marker used to end the run with an internal error; it is
  described, built and checked now, its numbers written with commas
  and its markers left exactly as they are -- a marker spelled `E11.9`
  keeps its dot.

- **What this role cannot do is written down rather than left to be
  found.** A number too large for the format is described as a word
  (R-P4-149); a set of a dozen numeric CODES just above the size where
  a set of categories stops being one is read as a quantity, and
  `--code` is how you say otherwise (R-P4-150); and a column whose
  numbers hold exactly the smallest publishable number of different
  values has a twin that may be described as a different kind of
  column -- the twin still holds the numbers (R-P4-151).

### Fixed: your twin no longer puts values where your column had none

- **A column with two clusters and a gap between them now gets a twin
  that keeps out of the gap** (closing residual R-P4-136). If your
  readings sit around 20 and around 80 with nothing in between, the
  middle value of that column is about 50 -- a number none of your
  cells holds -- and the twin honoured it, writing four to six cells of
  three hundred into the empty middle. Anybody plotting the twin met a
  third group of readings that is not in your table. The description
  now records which stretches of a column's range held no value at all,
  and the twin reads it: measured over forty seeds on three such
  columns, cells in a stretch your column left empty went from four to
  six, two to three, and three to six, to NONE at every seed.

- **And that fact survives a raised smallest-group size.** The shape
  record beside it is all or nothing, so it disappears entirely on
  exactly these columns as soon as you ask for groups larger than one.
  The new record says only where NOBODY is, so no group size hides it,
  and it names no value, no count and no cell.

- Where the twin cannot get out of a stretch -- a column of whole
  numbers whose steps are barely wider than one, or a value whose sign
  leaves it nowhere to go -- it stays, and the report beside the twin
  names the stretch and the value rather than saying nothing.

### Fixed: two numbers in one cell now repeat the way your own readings did

- **A column of readings like `120/80` now holds as many different
  readings as your table did** (closing residuals R-P4-40, R-P4-51 and
  R-P4-112). Each number of such a cell is built by the same machinery
  a plain column of numbers uses -- and it was told how many different
  values to make from the count of different whole CELLS, not from a
  count of its own numbers. So a 400-row blood pressure whose first
  numbers take thirteen different values got a twin whose first numbers
  took thirty-four to forty-one, and the column held a hundred and
  fifty-seven to a hundred and sixty-nine different readings where the
  description says a hundred and ten. Somebody grouping rows by the
  first number found three times as many groups as their real table
  had, and the quality report said so on every run.

  Measured end to end through all three commands over ten seeds, that
  column now holds exactly thirteen first numbers, nine second numbers
  and a hundred and ten different readings at all forty seeds sampled,
  and
  `synthtwin validate` reports nothing missed at all.

- **And a cell holding THREE or more numbers now reproduces how every
  pair of them moves together, not just the last one's.** The step that
  decides which numbers meet in a row moved the last number of a cell
  and no other, so on a column like `1/4/10` the relationship between
  the first two numbers was never aimed at: a column whose first two
  move in exact opposition -- published as -1.0 -- got a twin holding
  +1.0, the exact opposite. Every number but the first moves now.
  Measured over a battery of twelve three- and four-number columns at
  ten seeds, 540 pairs in all: of the 240 pairs between two earlier
  numbers, every one used to land outside the range this tool promises
  and ninety-one do now, and the count of rows holding one above the
  other went from 236 missed to none.

  **And measured again at forty seeds, because ten is not a scope for
  this claim**: of 2,160 pairs, 550 land outside the promised range,
  367 of the 960 between two earlier numbers -- and the count of rows
  holding one above the other is met at every pair of every seed. Ten
  seeds is not a scope for that last one in particular: it is met at
  all ten under a build where forty finds a column that misses it.

  Holding the first number still loses no arrangement at all, and it
  is why a column of exactly two numbers -- every blood pressure, every
  ratio -- still has exactly one number moved, by the same rule as
  before. Such a column's cells DO change in this release, for the
  first reason above rather than this one.

- **What is still short is reported and named.** A column of three or
  four numbers sets three or six relationships that pull against each
  other inside one bounded search, and a hundred and thirty-six of
  those 540 pairs still land outside the promised range -- 550 of 2,160
  at forty seeds -- reported as misses by both the twin's own report
  and `synthtwin validate`, with the achieved value beside the
  published one.

- **And the count of rows holding one number above another is no
  longer given up to buy a relationship.** The step that chooses which
  numbers meet in a row weighed every count it had to meet in ONE
  total, and a total cannot tell one count being lost from another
  being gained at the same price: a four-number column came out having
  traded a count it held for a hundredth of a relationship it did not,
  and `synthtwin validate` reported the count as missed. Each count is
  weighed by its own name now, and a count the twin already holds is
  never given up. The same step also aims at an outstanding count
  directly, every other attempt, which is what a two-number column
  needed: a 400-row blood pressure of 379 different readings missed its
  count at four seeds of six and misses it at none. Measured over the
  same battery of twelve columns at forty seeds, all 2,160 counts are
  met where one was missed before.

  **Which twins change.** A column whose every such count the walk had
  already met writes the same cells it wrote before, to the byte -- a
  repeating blood pressure, a correlated one and a 240-row column of
  all-different readings are unchanged here. A column where a count was
  still outstanding gets a different twin, and that includes columns of
  exactly two numbers.

- **And that direct attempt reaches every number of the cell, not half
  of them.** "Every other attempt" was counted on the search's own
  attempt number -- and the search takes the numbers of a cell in turn
  from that same counter, so on a cell holding an ODD number of values
  the two counters locked: half the numbers were aimed at on every turn
  they got and half on none of theirs. The first number, the one paired
  with the number that never moves, was among the starved half on such
  a cell, so that pair could not reach its count at all. The attempt is
  counted per number now. Measured over forty described columns of two
  to five numbers at forty seeds, 9,640 pairs: 44 counts land short of
  their published value, where counting the attempts on the search's
  own clock leaves 120 and counting them on the opposite turns leaves
  153. On eight five-number columns, 3,200 pairs: 12, against 71 and
  96.

  **Which twins change.** A column holding an even number of values in
  a cell -- every blood pressure, every ratio, every four-number
  reading -- writes exactly the cells the previous build wrote, to the
  byte, at all forty seeds measured. A column holding three or five
  gets a different twin, and a better one.

### Fixed: a column of very large or very small numbers keeps its width

- **A column whose numbers are written compactly -- `1e400`, `-1e400`,
  `2e400` -- now gets a twin written the same width** (closing
  residuals R-P4-68 and R-P4-48; generation method G10.5 revision 5).
  Values too large or too small for a computer's ordinary number format
  to hold are described with the width of the narrowest and the widest
  cell in your table, and the twin could write them only as long runs
  of figures. So a column whose cells were five and six characters wide
  got a twin whose cells were three hundred and ten and three hundred
  and eleven characters wide: the description was right and the report
  said the two widths were missed, but anybody who had written
  `len(x) == 5`, a fixed-width read or a slice against the twin met a
  value sixty times wider than anything their real column held.

  The twin can write these values in scientific notation now, which
  says the same magnitude in five characters. Measured on the column
  above, end to end through all three commands: five and six characters
  published, five and six written, and no fact of that column missed at
  all where two were missed before. A column of thirty very small
  fractions all three hundred and twenty-seven characters wide is now
  written at that width throughout, where its widest cells used to come
  out one character over.

  Nothing about a column already written as long runs of figures moves:
  the twin still writes those the way it did, and the frozen reference
  cells for that shape are unchanged byte for byte.

- **And a column of many such values no longer stops the command.**
  While this was being built, the first version wrote every one of
  these numbers with the same exponent, which left it nine different
  five-character values to spend -- and a real column of sixteen made
  `synthtwin generate` refuse to build a twin at all, saying the
  description asked for more different values than it could write.
  A column that had generated before, wrongly wide, would have stopped
  instead. The exponent moves now, so what the twin can write at a
  width is what a real column of that width can hold: six thousand two
  hundred and twenty-seven different five-character values rather than
  nine.

- **And it stopped eight values short of that, which stopped the
  command on a bigger column.** The walk gave up at the first spelling
  it worked out was a number this format CAN hold -- and for a value
  too large, the ones just past that point are exactly the ones it
  cannot. So a real column holding six thousand two hundred and twenty
  different such values, every one of them five characters wide, made
  `synthtwin generate` refuse again. The walk steps past such a
  spelling now and carries on, and that column gets a twin with all six
  thousand two hundred and twenty values at the published width and
  nothing missed.

### Fixed: a twin no longer writes a value you told it means "no value"

- **A value named with `--missing-value` is left alone by every column
  of the table, including the columns that publish nothing.** A column
  of numbers too large or too small for the format to hold publishes no
  value of your table anywhere -- that is what its role means -- so it
  had no way to know which spellings you had declared, and it was never
  given the list the rest of the run uses. Measured on a two-column
  table where `1e400` was declared missing: the second column's twin
  was handed `1e400` as a real value, its own report said nothing about
  it, and `synthtwin validate` reported eight of that column's counts
  missed. It leaves those spellings alone now, on both of the ways it
  writes such numbers, and counts them out when it works out how many
  different values it can write.

### Fixed: a column of one width whose values repeat keeps that width

- **Where a column of very large or very small numbers is all one width
  and two of its cells are the same value written differently, the twin
  now holds both at that width** (closing residual R-P4-47). Two cells
  spelled with a space -- one at the end, one at the front -- are the
  same value to a spreadsheet and to this tool, and they are the same
  number of characters long. The twin used to write the first at the
  published width and the second one character longer, and its report
  said the widest cell was missed. It writes the value with room for
  the space now, exactly as your own two cells did, so both come out at
  the published width and nothing is missed. Measured end to end on
  eight such columns: five that missed the width now hold it, and the
  three that already held it are written exactly as before.


### Fixed: a twin's invented codes now wear the shape the real ones wore

- **Every published label of a category column records how many of its
  rows were written in that label's own SHAPE** (`shape_form_cells`;
  owner ruling of 2026-08-31, plan amendment A-P4-47, closing residual
  R-P4-34). A column of clinical codes publishes how many of its cells
  were written in each shape -- a letter, two figures, a point and a
  figure -- so that the values the disclosure floor holds back get
  stand-ins of the right shape rather than `group-14`. Where the floor
  held back more than one spelling of a published label, the
  description did not say which of them wore the label's shape, and the
  twin had to guess: measured over 120 built columns, 57 met the
  published census, 31 wrote too few cells in the shape and 32 wrote
  too many. It is a single number per label, because every spelling of
  a label that has a shape wears exactly that label's shape. Given it,
  the generator writes the shape onto exactly the held-back groups that
  add up to the number, and the census is met exactly. The
  reproduction that could not be told apart before now publishes 25
  against 23, produces two different twins, and both hold their own
  census.

  What this means for a person reading a description: a category
  column's entries carry one more whole number each. It publishes no
  spelling and no shape KEY -- the shape it counts is the shape of the
  label already printed beside it -- and the floor still decides which
  values are named. What a reader can take from it is that one of a
  label's held-back spellings was written in the label's own shape,
  which is presence and shape and not content.

  The twin's cells for the demonstration table are byte-identical, and
  its quality report carries nine obligations more than it did and not
  one fewer.

- **A description asking for more than the spelling supply can write is
  told so.** A label of one letter has one alternative spelling that
  keeps its shape. Where a description asks more of its held-back
  groups to keep the shape than that, the twin writes what it can and
  the report beside it names the shortfall with both numbers.

### Fixed: the contract said a rule narrowed a shortfall that it also widens

- **The census of written forms misses in BOTH directions, and two
  passages of the format contract said it misses in one** (residual
  R-P4-34, measured). A column of codes publishes how many of its cells
  were written in each shape. Where the disclosure floor holds back
  more than one spelling of a published label, the description does not
  say which of them wore that shape -- so the twin has to guess.
  Measured over 120 built columns of that family: 57 met the published
  census, 31 wrote too few cells in the shape and 32 wrote too many.
  What that trial covers is that family and nothing else. The contract
  named the rule that offers a label's own spelling to its largest
  held-back group as one of two things that
  "narrow" the shortfall; measurement says that rule is what produces
  the overshoot, so it narrows in one direction and widens in the
  other, and both passages now say so. No published number moves, no
  twin cell is different and no obligation changes: what changes is
  that the document states the bound the tool already had.

### Added: the shortfall was a witness, and the witnesses have gone

- **Both directions were pinned at their exact counts**
  (`tests/test_p4r34_form_census_per_level.py`), and the repair above
  turned all four of those tests red, which is when a witness should
  go. The file is rewritten to the repaired behaviour and keeps every
  measured number -- the same two columns, the same 206 and 204 -- so
  it reads as a repair of what was reported rather than as a fresh case
  built to pass. The fifth test stands unchanged: every spelling of a
  label that has a shape wears exactly that label's shape, which was a
  property rather than a defect and is what the repair rests on.

### Added: four columns that were described correctly and silently now speak

Each of these adds a SENTENCE and nothing else. No role changes, no
published number moves, and no cell of any twin is different -- which
is measured, block for block, and not promised.

- **A column of whole numbers that are all moments in time is told so**
  (residual R-P4-9). A column of `1600000000` is a column of counts
  and stays one; what was missing was anybody saying that read as
  seconds since the 1st of January 1970 it runs from one calendar day
  to another. The remark says which unit the numbers are counted in --
  seconds or milliseconds, which matters by a factor of a thousand --
  and says the twin is unaffected, because reading them as plain
  numbers keeps the range and the spacing, so converting the twin
  gives the same span. It names no flag, because there is none: nothing
  in synthtwin reads a number as a time.
- **A declined column says how far a CLOCK reading got.** The sentence
  that says why no reading fitted named the numeric reading, the
  date reading and the affix reading, and was silent about the fourth
  -- so a column of clock times in a shape synthtwin does not describe
  was told nothing fitted it and never told which reading came
  closest.
- **A declined column whose gaps are a few repeated words is told one
  declaration would recover its distribution.** It is written only
  where it is TRUE: synthtwin reads the column again over what is left
  and writes the sentence only when that reading really publishes a
  distribution. Where the survivors are numbers too large to hold, or
  collapse to two values, nothing is said -- those columns publish no
  distribution and a promise of one would be false.
- **A column of dates that also read as numbers states both counts.**
  Eight digits are a date and a whole number at once; a sentence
  saying only which reading won left no way to see how close the other
  came.
- **A label column publishing `-999` as one of its values is told
  `--missing-value` exists for it.** synthtwin reads that number as
  "no value" on a column of numbers and cannot on a column of labels,
  so it was published as an ordinary value with an ordinary count and
  nothing said so. All three of the built-in stand-in numbers are
  covered, and a column publishing two of them is told about both.

### Fixed: a column that stops being read as numbers is told why

- **The address decline was silent** (residual R-P4-39, contract
  NF50). synthtwin refuses to read a column of `user12345@example.org`
  as a number wrapped in text, and that refusal is right: the average
  of a column of real addresses is the average of whatever numbers
  those addresses were given. But it said NOTHING. The column simply
  stopped carrying an average, a spread, its ends and its ladder, and
  no sentence in the profile, in the summary beside it or in the
  twin's report told its owner why. It carries one now, naming the
  shape it declined for -- an at sign, a host, a dot label -- so a
  person recognizes their own column.
- **And it names all three declarations, not one.** The remark beside
  it offered `--identifier`, which publishes no value at all and is
  the wrong answer for somebody who wants the column's distribution.
  All three are named with what each publishes: `--identifier` no
  value, `--code` each spelling with how many rows carried it,
  `--measurement` the distribution over the numbers inside. **It
  decides nothing** -- no role, no published fact and no cell of the
  twin moves because of it, which is measured rather than promised.
- **A declared measurement wearing an address had its stand-ins
  ignored.** The pass that judges "no value" numbers inside an affixed
  column's cells re-derived that column's reading WITHOUT the person's
  declaration, while the role had been decided WITH it -- so on a
  column carried past the address rule by `--measurement`, not one
  cell was judged. Measured on 200 readings between 50 and 70 with
  eleven cells spelled `-999`: no verdict was published, `-999` stood
  as the column's smallest reading, and the average came out 1.785
  where the same column written any other way reads 60.03.

### Fixed: a blood-pressure column's own facts are checked and named

- **The role that carries a blood pressure was the one role no
  completeness surface reached** (residual R-P4-62). Three guards each
  proved their own completeness against a table that does not contain
  it, so each passed by never looking. The disposition registry now
  carries the role's ten facts, the completeness walk reaches it, and
  the red battery has a fixture for it with ninety-nine registered
  cases, every one measured.
- **A joined column's distinctness was reported under the wrong
  name.** The validator had no branch for this role, so it fell
  through to the one for empty columns and a blood-pressure column's
  count of different readings was reported as an empty column's. It is
  named correctly now, and the contract disposes it -- which nothing
  did before.
- **Each position's report-only facts are named in the report.** A
  two-number column published a count of different numbers and a
  finer ladder per position, and the quality report carried neither a
  check nor a line saying it could not check them.

### Changed: the governance checks read the contract that governs

- **The disposition machinery reads profile contract version 6.** Both
  matrix readers took version 4's tables merged with version 5's
  delta -- the record of what two superseded versions required -- while
  the version every description is written to has been 6. Nothing was
  wrong in what they compared; a governance surface pointed at a
  document that governs nothing shipped is one whose agreement is luck
  rather than design (residual R-P4-25).
- Two role groups and seven facts that had to stand outside a matrix
  are read from the contract's own tables now, and the clock role's
  approximated inventory is read rather than written out by hand.
- The loader's own module documentation said version 5 was normative
  and that a description must carry version 5, with the code requiring
  6. A contributor following it would have prepared a file the shipped
  loader refuses (residual R-P4-63).

### Added: two more ways a reading can be written

- **`120 / 80`, with spaces around the mark**, is now read as the same
  reading as `120/80`. It used to be treated as free text, which
  publishes nothing. The twin writes the spacing your table used.
- **`1:1.5`, with a decimal in one of the numbers** -- an I:E ratio --
  is now read. A number in a cell could only be whole before.
- **A signed number is still not read this way**, deliberately: a
  leading minus cannot be told from the mark the cell might be split
  on, so `-3/-4` is left alone rather than split on its own signs.

### Changed: the two numbers of a reading now move together

- **A blood pressure's two numbers were drawn separately**, so the twin
  held cells like `111/105` -- a diastolic above its systolic -- and the
  two numbers had no relationship at all. Measured on 400 readings whose
  real numbers moved together at 0.83, the twin's moved together at
  -0.01.
- **The description now records how the numbers move together** and in
  how many rows the first sits above the second, and the twin is built
  to both. On the same 400 readings: 0.8342 against a real 0.8343, 400
  of 400 rows with the systolic on top, and **no impossible readings**.
- **Every number in the column is unchanged.** Only which numbers share
  a cell moves, so each position's smallest, largest, average, spread
  and widths are exactly what they were.
- **One thing it can cost, and the twin says so.** The count of
  different readings was always exact before and is not always exact
  now, because a twin's numbers repeat more evenly than real ones do and
  fewer different pairs can be made from them. Where that happens the
  twin's own report names it.

### Changed: a column you name with `--code` now always publishes its codes

- **A code column with many different codes, none repeated much, used to
  publish nothing at all.** A laboratory-code column of 228 different
  codes over 400 rows was read as free text -- too many codes to be a
  set of categories, none repeated often enough to be a long tail -- so
  the description named none of them and the twin held none of them.
- **Named with `--code`, it now publishes every code with its row
  count**, and the twin holds the same codes in the same proportions.
  On the demonstration table: 228 of 228 laboratory codes and 221 of 221
  drug codes, at exactly the right counts, where both were zero before.
- **Why that is worth having: every rollup then comes out right.**
  Because the twin holds the same codes the same number of times, any
  grouping of them reproduces exactly -- the leading letters of a
  diagnosis code, the segment before a dash, the code length. synthtwin
  knows no coding system and models no hierarchy; it does not have to.
- **What it discloses.** The twin holds the REAL codes, redistributed
  across rows, and the description names them. That follows the ruling
  that nothing is held back for being rare. If you need the old
  behaviour for a column, do not name it with `--code`.
- **Nothing changes for a column you do not name.** A column of prose is
  still read as free text at every setting.

### Added: blood pressures, and anything else written as two numbers in one cell

- **`--measurement COLUMN` tells synthtwin that a column holds readings
  written as two or more numbers joined by a mark** -- `120/80`.
  It reads each number separately and publishes a range and an average
  for each, so the twin's cells hold believable readings.
- **What it fixes.** Such a column was described as text, which
  publishes no value at all, so its twin held cells like `632/20`: the
  right shape and an impossible reading. Measured on 400 rows, the twin
  now reproduces systolic 95 / 133.5 / 175 against a real 95 / 133.5 /
  175, diastolic 55 / 80 / 105 against 55 / 80 / 105, and the same
  number of different readings the real column held.
- **synthtwin asks about these columns too**, with one more answer
  offered. The same question that separates a code column from a
  measurement separates a blood pressure from a lab code.
- **Why you have to say so.** `120/80` and a lab code `1923-1` are
  written identically, so nothing in the values can tell them apart. A
  rule that guessed would have claimed lab codes and drug codes and
  published fragments of them as numeric ranges.
- **One limit, stated plainly:** the two numbers are drawn
  independently, so a twin cell is believable one number at a time. The
  description publishes no link between them, and this version invents
  none.

### Changed: nothing is held back for being rare, unless you ask for it

- **The smallest group size now defaults to 1 instead of 11** (owner
  ruling 2026-08-25). Every value your table holds is named in the
  profile, together with how many rows shared it, so a rare finding
  reaches your twin instead of being pooled away. The reason is that
  synthtwin publishes nothing that crosses two columns -- so a named
  rare value says that somebody in your table had it, and nothing else
  about them.
- **`--smallest-group 11` restores the old behaviour in full**, and
  every rule about what the floor protects still binds at whatever
  number your description carries. If a review board or a data-use
  agreement needs groups kept above a size, that is the option.
- **What to check if you relied on the old default:** a profile made
  before this release is unaffected -- the floor lives in the document,
  and every command runs on the number it finds there.

### Added: `--code`, for coding systems written in digits

- **`--code COLUMN` tells synthtwin that a column holds codes rather
  than measurements.** Vaccine codes, procedure codes, revenue codes,
  provider numbers, risk-group codes. Its values are still published,
  because which codes are common is the point of the column; what
  changes is that synthtwin stops reading them as numbers.
- **What it fixes.** A column of `08`, `20`, `213` was read as a
  quantity: the profile published an average, a smallest and a largest
  -- meaningless for a code, and real codes besides -- and the twin
  wrote `8` where your table wrote `08`, so code that splits on width
  broke. Declared, every spelling is kept exactly and counted.
- **You need it only for a column written in digits alone.** One
  written with a letter or a dash -- `E11.9`, `0002-8215-01`,
  `HGNC:5`, `NM_000546.6:c.215C>G` -- is already read as codes.
- **Measured across eighteen coding systems** -- NDC, CVX, MVX, UDI,
  MS-DRG, APC, UB-04, NPI, the clinical grouper codes, Elixhauser, Charlson, CMS-HCC, CDPS,
  HGNC ID, HGVS, OMIM, ClinVar, GA4GH -- all eighteen now survive
  profile, generate and validate with their written shapes intact. Two
  of them, CVX and UB-04, lost their leading zeros before this release.

### Added: synthtwin asks you about columns it cannot read

- **A column of digits is a coding system or it is measurements, and
  the two are written identically.** synthtwin does not guess. When it
  meets a column of digits that could be codes -- some value padded
  with a leading zero, or every value the same width -- it stops and
  asks you, showing you a few of the values.
- **Your answers are recorded in the profile**, and the exact options
  to repeat the run without the questions are printed at the end.
- **It never stops a script.** Where nobody is at the keyboard, it
  names those columns on screen, says what it assumed, and prints the
  `--code` line that corrects it. A run whose output is piped to a
  file counts as scripted even from a terminal.
- **What it does not reach**, said so silence is not read as
  clearance: a column of one-to-three digits with no padding, like
  the clinical grouper codes, are written exactly like a count and raises no question --
  `--code` still describes it correctly when you say the word.

### Changed: Phase 3 is closed, without the release it asked for

- **Phase 3 was closed by owner decision on 2026-08-19, and the release
  it named as its own earliest-possible deliverable did not happen.**
  The product it set out to build is done and in your hands -- the
  three commands, the quality report, the repository going public. The
  release is not: there is no tag and nothing is published. Everything
  that rests on release evidence stays unmet and is named as unmet,
  including Phase 1's residual about verifying the wheel's own digest,
  which this project had recorded as closed "on the first release's
  evidence" before that evidence existed. That line is struck rather
  than deleted, in the plan, where a reader of the register meets it.
- **What changes for you: nothing about the tool, and one thing about
  what it says of itself.** The project now describes itself as being
  in Phase 4, because it is. It does not describe itself as released,
  because it is not, and no wording anywhere says otherwise.
- **The order this was done in is recorded rather than tidied away**
  (plan amendment A-P4-4). Phase 4's first piece was built on a branch
  before Phase 3's closing state was settled, which is not the order
  the plan required. Nothing was merged and nothing was published in
  that window, so the contradiction reached no reader outside the
  branch -- but it was real, an adversarial review raised it at every
  round, and the amendment authorizes that one interval, prices it, and
  leaves the rule at full strength for every stage that follows.

### Added in Phase 4: a twin of a column of codes now holds things shaped like codes

- **A column whose rare values the disclosure floor holds back used to
  put `group-1`, `group-2`, `group-3` in the twin.** On a column of
  clinical codes that stand-in is wrong every way a stand-in can be: it
  is the wrong length, it is lower-case where the codes are not, and on
  a hyphenated scheme it carries a hyphen of its own -- so it passes a
  "looks segmented" check, crashes a split into a fixed number of
  parts, and, the word being exactly five characters, makes a width
  check on the leading segment answer plausibly and wrongly. You found
  all three at once against the real file.
- **A long-tail column and a free-text column now publish the WRITTEN
  FORMS their cells were written in, and the twin wears them** (plan
  P4-D18, contract 7.9, on the owner's ruling A-P4-36). A form is the
  cell with every figure replaced by `9` and every letter by `A`, the
  marks standing as themselves: `E11.9` has the form `A99.9`, a
  laboratory code `4548-4` has `9999-9`, a dispensed-drug code
  `0002-8215-01` has `9999-9999-99`. Your twin's cells are written in
  those forms, so a split, a width check and a pattern match all answer
  the way they will on the real table.
- **A form says the shape and nothing else, and that is CHECKED rather
  than promised.** A key holds two placeholder characters -- `%` for a
  figure, `@` for a letter -- and thirteen marks synthtwin names, and
  nothing else, whatever wrote it, including a file edited by hand.
  `E11.9` is `@%%.%`, and `E11.9` and `Z99.1` are one key that tells
  them apart from nothing.
- **The placeholders are characters no code of yours can contain, and
  that is the whole reason they are those two.** They were `9` and
  `A`, which read far better and were WRONG: a form built from
  figures and letters is a string a cell can also be spelled with, so
  a form could BE one of your values. `A99` is a real diagnosis code.
  On a column with three patients coded `A99` -- held back by the
  small-cell floor, exactly as it should be -- the shape census
  published `A99` straight back into the description file. That is
  fixed: no cell that has a shape can ever be spelled the same as any
  shape, and synthtwin refuses a description whose key breaks it.
- **A shape is read over `0`-`9` and `a`-`z` only, and a cell holding
  anything else has none.** Reading letters the way Python reads them
  made the answer depend on which version of Python you ran: the same
  table gave a different description, a different twin, and a quality
  report that called a good twin BROKEN, purely from where it ran.
- **A column of prose publishes nothing here.** A cell holding a space
  has no form, and neither does one longer than twenty-four
  characters, or one holding any mark outside the thirteen. So a note,
  an address or a typed comment puts nothing in the census -- and
  neither does a short sentence written to a template, which was a
  real hole: two hundred and forty of those share one form, and that
  form would have named every word's length and where the punctuation
  fell.
- **A form that says nothing new is not published.** Four region names
  would say `AAAA` and `AAAAA`, and the description already publishes
  their lengths exactly and which alphabet they came from. A cell has
  a form only where at least two of the three kinds -- figure, letter,
  mark -- appear in it, so `J1200` keeps `A9999` and `north` publishes
  nothing.
- **No rule anywhere decides which of your columns are codes.** The
  same small-cell floor that governs everything else does, together
  with those three limits, so there is no code detector here that can
  get it wrong.
- **Measured across the ten clinical coding schemes the owner named**,
  each written twice: as a column of all-different codes and as a long
  tail. Every one of the twenty twins is shaped like its own scheme and
  splits into the number of parts that scheme has. A blood-pressure
  column reaches `152/90`-shaped cells the same way.
- **What this LOWERS is said plainly**: two roles that published
  nothing about their values' writing now publish the forms those
  values were written in. What it buys is the thing the owner asked
  for: a rare finding represented in the twin, at its real count, in
  the shape of the thing it stands for -- and code developed against
  the twin that runs on the real table.

### Fixed in Phase 4: a number written two ways is written two ways again

- **A column that wrote the same number with both `1e+15` and `1E+15`
  lost one of the two in its twin.** The count of different spellings
  your file publishes then came out one short, every time, and your
  twin's report named the miss. Everything else about the column was
  right, which is why it took a second implementation of the written
  method to find at all: both columns met every other published count.
- **What it needs to have happened to you**: a numeric column whose
  cells carry exponents, where your file spelled one value's exponent
  in upper case somewhere and lower case somewhere else. If your file
  is consistent about the case -- almost all are -- nothing here
  changes for you.
- Measured over 140 built columns at three seeds each: the twin is now
  closer to your published counts on every column that moved, and
  further on none.

### Fixed in Phase 4: your twin's report no longer accuses a twin that is fine

- **A column whose empty cells were written with a word -- `-999`,
  `N/A`, anything you named with `--missing-value` -- had those cells
  counted as values by the report written beside the twin.** On a
  column of ages with twenty `-999` holes, the report said the twin's
  average was -40.4 where your table's is 39.5, its spread 277 where
  yours is 11.6, and its smallest percentile -999. **Thirteen
  complaints about a twin that `synthtwin validate` calls correct.**
- **The check was always right; only the report was wrong.** Nine
  places in the generator asked "is this cell blank" where they meant
  "is this cell a value". A twin writes your absent cells the way your
  file wrote them, so a hole spelled `-999` looks like a number. They
  all ask the same question now, and it is the question
  `synthtwin validate` was already asking.
- **What this changes for you:** if you saw a twin report full of
  alarming numbers on a column with coded missing values, it was the
  report and not the twin. Real shortfalls are still named -- the
  twin holding fewer different values than your table does is still
  reported, because that one is true.

### Fixed in Phase 4: two older defects the form census turned up

- **A held-back spelling of a published label could be written in a
  form the column never had.** The twin makes up spellings for the
  spellings below the floor, by flipping case and then by appending
  spaces -- and a trailing space is a different written form. Where a
  label had few letters and its flips were already published, the twin
  wrote `E11.9 ` and `E11.9  ` for cells the real column wrote `e11.9`.
  The label's own spelling is now offered where nothing else of the
  level needs it, and it is offered to the largest held-back group.
- **The order of a multiplicity map's keys read the figures as text**,
  so a spelling covering ten rows was written before one covering two.
  The method says ascending numeric order and now the code does too. It
  changes nothing until a spelling covers ten rows or more.

### Added in Phase 4: the twin now tells you which of its cells synthtwin made up

- **Every column whose cells synthtwin invented says so, in its own
  block, on every run** (plan P4-D2, the loud decline). Until now the
  only place the report called a cell invented was the spreadsheet
  warning, and only when such a cell happened to begin with `=`, `+`,
  `-` or `@`. So a column synthtwin could not read -- a column of
  prices, of clock times, of anything it has no reading for -- became
  free text, the twin filled it with made-up characters, and you could
  read the whole report without meeting one sentence saying so. Now the
  sentence is a property of the column, not of what its cells happen to
  look like. Three of them, because one would be false somewhere:
  a column that publishes no value of your table is told that **every**
  present value in its twin is invented; a column of categories is told
  how many of its cells are neutral stand-ins for the labels the
  smallest-group floor held back; and a column whose description counts
  cells it carries no value for -- the ones that were not numbers, or
  did not read as dates -- is told how many stand-ins it holds. A
  column that invented nothing is told nothing, and a column with no
  values at all is not told its zero values were invented.
- **The count is on the screen and at the foot of the report**, whatever
  it is: how many columns hold nothing but made-up values, and how many
  more hold some beside values your description publishes. Both halves
  are counted, because a line counting only the first would have read
  "0 of 1" over a twin whose one column carries invented labels.
- **The description's own summary now says it too**: if a description
  publishes no value of a column, a twin built from it will hold
  invented values there. You see that before you generate anything.
- **What did not move:** no wire format, no generation rule, no twin
  byte, and no exit code. A declined column is not a failure and
  `synthtwin generate` still exits 0 on it -- the loudness is in what
  you read, not in what a script checks. The report's golden hash was
  re-recorded in the same commit, with the four blocks that moved named
  in the comment beside it.

### Fixed in Phase 3: a failed check now tells you what your file holds, or why it cannot

- **A missed obligation could print your description's request and
  nothing else** (plan amendment A-P3-45). Where the thing your file
  was found to hold is something the report may not print -- a
  spelling written in the file, or a count these checks are never
  reported with -- the line said what the description asked for and
  stopped. So `synthtwin validate` could tell you that your file failed
  a check and not tell you a single thing about your file. Every missed
  check now prints either what was found or a sentence saying which
  rule keeps it back, what that rule buys you -- the report can be
  handed to somebody who does not hold your file -- and what to do
  instead, which is to open the file, or to describe it with `synthtwin
  profile` and read the count that comes back. Nothing measured is
  printed that was not printed before.
- **The report promised something it did not deliver, twice on the same
  page** (plan amendment A-P3-45 clause 5). The verdict section said
  every missed obligation was named with what the description asks for
  "and what the file was found to hold", and the detail section's
  heading said the same, above lines that printed one of the two. Both
  sentences now say what the page actually carries.
- **A check written in future that forgets to say why cannot print a
  blank line** (plan amendment A-P3-45 clause 4). Every report goes
  through one floor: a missed check naming neither what was found nor
  why gets a sentence saying so, and naming itself a defect in
  synthtwin rather than a fact about your file.

### Known, open, and waiting on a decision: numbers written to a fixed two or more decimal places

- **Checking a real table against its own description reports one
  obligation missed, and exits 3, when a numeric column is written to a
  fixed two or more decimal places** (plan amendment A-P3-46, residual
  R-P3-12). `1.20` and `3.00` are not the shortest text that reads back
  as those values, and one check asks every numeric cell to be written
  as one of the six published forms of its own value. Nothing is wrong
  with your table, and nothing is wrong with the description; the
  column is formatted, which is what a currency column, an instrument
  export and a spreadsheet all do. One decimal place, whole numbers
  written `12.0`, plain whole numbers and shortest-form numbers are all
  unaffected. The check is not idle: a file whose every decimal cell
  has been re-spelled with a trailing zero is caught by this check and
  by nothing else -- measured on a sixty-row column, where it is the
  one obligation of fifty-two that moves -- so what to do about it is
  a decision with a real cost either way, and it is recorded, measured
  and put to the owner rather than taken quietly.

### Fixed in Phase 3: saying where your word stands is now checked against what stands there

- **The check that reads where a sentence puts your word accepted a
  sentence that named the wrong place, or the right place and the wrong
  fact** (plan amendment A-P3-44 clauses 1 and 2). It asked whether a
  sentence about a value you typed NAMED a place in the description,
  and stopped there. So a sentence could name the very place your
  spelling is written into, character for character, and say a count
  stands there instead; or bound what the description keeps of your
  value in one breath and name an unrelated block in the next. The
  check now reads the claim and the place together, against what
  synthtwin's own table of what-goes-where says stands in that place: a
  sentence that puts your value in the column's own description has to
  say your spelling itself is what stands there, a sentence that puts
  it nowhere is refused, and a sentence that bounds what is kept has to
  say which place the bound holds in.
- **The refusals a description's reader prints are now checked too**
  (plan amendment A-P3-44 clause 3). A refusal is built while the
  command runs, out of a rule and two clauses written down in the
  source, so no whole sentence of one was ever checked. All 130 of them
  are now assembled from those pieces and read, which means a sentence
  written into a clause is held to the same rule as every other
  sentence the product shows you.
- **Three sentences the product shows now say your word itself is what
  stands there** (plan amendment A-P3-44 clause 4). The rule about the
  block that records your declarations, the help for `--keep-value`,
  and the refusal about a word that is not one of synthtwin's each
  named a place and left what stands in it to a pronoun or to a path
  filled in while the command runs. Each now says it in words. No rule
  changed and no file synthtwin writes changed.

### Fixed in Phase 3: a description was said to keep a count where it keeps your word

- **Two sentences the product shows said a description records how
  MANY values you named, and denied the values** (plan amendment
  A-P3-43 clauses 1 and 2). The rule the loader prints when it refuses
  a description said the description records how many values were
  declared and then denied your own text, naming no place; the refusal
  that prints that rule said a version 5 description holds the count
  and denied the identity, naming none either. Neither is true of the
  description: a word you name with `--missing-value` is written
  into the column's own description, character for character, wherever
  at least the smallest group size of rows share it and that column
  publishes values at all. Both sentences now say which block they are
  about, and say where your own spelling does stand. The two option
  helps on `--keep-value` and `--missing-value` said the same thing the
  same way and now name the settings block as the place they are
  talking about.
- **The check that forbids those sentences could not see this one**
  (plan amendment A-P3-43 clauses 1 to 3). It read a denial as "the
  thing is not somewhere" and this is the other shape -- what is kept
  is a REDUCTION of what was given -- so the sentence carried no denial
  for it to find. Half of that shape can be read and now is. The other
  half carries no negative word at all, cannot be read by any rule that
  reads words, and is said so in as many words rather than implied: it
  is refused instead by a rule that reads no verb, no negation and no
  limiter and asks only whether a sentence about a value you typed says
  WHERE.
- **A refusal about a malformed description still printed a spelling
  out of your table** (plan amendment A-P3-43 clause 5). The earlier
  repair sent such a file to the refusal that fits it and left that
  refusal naming the entry by its own key -- and in the two places the
  format lets your table decide a key, the key is a spelling some cell
  held. The entry is now named by what its keys are. No description
  synthtwin writes was ever affected, and none is accepted that was
  refused before.
- **The version check now reads a claim whose number arrives after
  "is"** (plan amendment A-P3-43 clause 4). A sentence of the shape
  *the profile version synthtwin writes IS <an old number>* used the
  ban's own version word, its own
  subject and its own verb, and walked through because both
  arrangements it read needed the version word and the number side by
  side. What it still cannot read is written down and measured.

### Fixed in Phase 3: four guards and one message that covered part of what they named

- **A malformed description was refused for the wrong reason, in a
  sentence quoting your own table** (plan amendment A-P3-42 clause 2).
  A description whose spellings map held a block where a count belongs
  was turned away with "this file has been changed since it was
  written", and the sentence printed the spelling out of your table
  that it had walked past to get there. That rule is about a floor and
  says nothing about the kind of value an entry holds. Such a file now
  meets the refusal that fits it -- this entry holds a block and it has
  to hold a whole number -- which names the kind of value and quotes
  none. No description synthtwin writes was ever affected, and none is
  accepted that was refused before.
- **The pre-write warning said you had typed words your table had
  spelled** (plan amendment A-P3-42 clause 5). One
  `--missing-value XX` over a table that writes `XX` in some cells and
  ` xx ` in others puts two spellings in the description, and both the
  screen and the summary page counted those two as two words you named:
  "Words you typed after --missing-value are written into the
  description", and then told you to run again "without naming them".
  Both spellings were disclosed and still are; what changes is that
  the sentence counts what you typed, and says outright where the other
  line came from.
- **The check that forbids saying synthtwin speaks a version it does
  not now reads the sentence written the other way round** (plan
  amendment A-P3-42 clause 3). `Version 4 profiles are what synthtwin
  writes.` used the ban's own subject, its own verb and its own way of
  naming a version, and walked through, because the ban was written as
  an order rather than as a claim. It now reads the two arrangements
  English fronts a sentence with as well, and it stops at a clause
  boundary so that two statements in one sentence are not read as one
  claim. What it still cannot read is written down and measured rather
  than left to be found.
- **Two tests that named a thing and proved a smaller one** (plan
  amendment A-P3-42 clause 4, and clause 1). The witness for the
  validator's per-column routing had stopped exercising that route at
  all -- another rule was doing the work, and removing the one under
  test changed nothing a person would see. It is replaced by a witness
  where only the route under test can fire, and the whole measurement
  is compared with and without it. And the refusal that turns away an
  older description is now held to naming AND pricing every option, by
  the same list read from the shipped command line.

### Fixed in Phase 3: the description contract stopped saying that a word it keeps is absent

- **The document that governs the format told you the wrong thing about
  your own word** (owner ruling 2026-08-17, plan amendment A-P3-41).
  Name a marker of your own with `--missing-value` and the description
  writes that marker down, character for character, in the block for
  the column whose cells wore it -- which is what the previous release
  note says and what the screen now warns you about before either file
  exists. The worked example inside the contract said the opposite: it
  denied, naming no place the denial held in, that the document had your
  word at all. It is the last copy of a false assurance corrected
  everywhere else one commit earlier, and it was in the one document an
  institution's reviewer reads first. It now says what is true, and says where a word of yours
  does travel.
- **And the check that was supposed to stop that sentence was reading
  for verbs.** It knew "written nowhere" and "never stored"; it did not
  know "holds it nowhere", which is the same claim with the words in the
  ordinary order, nor "omitted", "excluded", "discarded" or "left out".
  It now reads a denial by the PLACE it names -- so any verb at all,
  including ones nobody has written yet, is caught when the sentence
  says the word is nowhere, in none of the files, or outside the
  description. Denials that name no place are still recognised by a list
  of verbs, that list is a list, and the size of what it misses is
  written down and measured rather than left to be found.
- **One more sentence of the contract now names its own subject.** The
  line saying that a spelling of yours is never carried said "it" where
  it meant the settings block, which reads as the whole document as soon
  as the line is quoted on its own.

### Fixed in Phase 3: two ways the first check you run reported failures that were not there

- **A table holding `n/a` -- or any of synthtwin's own words for
  nothing -- no longer fails against its own description** (owner ruling
  2026-08-17, plan amendment A-P3-39, validation method V2.4-A10). Take
  one column of sixty numbers and twelve cells reading `n/a`, describe
  it with no options at all, and check that same file: the description
  says sixty values and twelve holes, the check counted seventy-two
  values and no holes, and **twenty-eight obligations came back as
  missed** with the wrong numbers printed beside them. When the check
  measures a file it has to decide which cells are values, and it
  treated every one of synthtwin's own words for nothing as a value --
  even where the description says, in as many words, that twelve of its
  holes were spelled that way. Where your description names the spelling
  its holes wore, the check now reads it the way your description does.
  It reports none, and both counts are held rather than merely
  unreported.
  - **What that costs, said plainly.** Where a description names one of
    synthtwin's own words as the source of some column's holes, a twin
    that happens to invent that same word in another column can have
    those cells counted as absent when it is checked. It is the same
    collision synthtwin already discloses for a word you named yourself
    and for a stand-in number, on the one kind of cell those two did
    not reach.
  - **And one case is stated rather than closed** (plan residual
    R-P3-11). If a column's holes wear one word under two spellings --
    six `n/a` and six `N/A` -- and neither spelling is shared by enough
    rows to be named under your `--smallest-group`, the description
    names no spelling at all, and the two counts of values and holes on
    that column are still reported against a count that reads both
    spellings as values. Exactly two obligations, on that column only;
    everything else on it falls back to your own description and holds.
- **A file holding exactly the value your description asks for is no
  longer reported as missing it** (owner ruling 2026-08-17, plan
  amendment A-P3-40, validation method V6.1-A1). Some facts are checked
  against a range rather than a single number, and that range is not a
  margin around the published value: it is worked out from the
  description and the size of the column, so it can sit wholly to one
  side of the value it is printed beside. The verdict was read off the
  range alone, so a line could say **"the description asks for:
  2024-12-24 / the file was found to hold: that same value"** and call
  it missed. On one ordinary table checked against its own description
  that happened on four dates and two counts. A file that holds the
  value your description asks for now holds the obligation, and the
  range is still printed beneath, with the sentence saying what it is.
  Nothing else moved: a file holding anything else is judged by its
  range exactly as before, and no check moved to a worse outcome.
  - **One report's counts moved with it.** The quality report of the
    demonstration twin now reads 262 held and 36 within-range where it
    read 249 and 49, over the same 300 checks, with nothing missed
    before or after. Thirteen lines whose two values were already the
    same number say so.

### Changed in Phase 3: the description format is version 5

**A description written by an earlier synthtwin is refused, and there is
no upgrade path.** Run `synthtwin profile` on your table again, giving it
**every** option you gave the first time -- `--keep-value`,
`--missing-value`, `--identifier`, `--smallest-group` and `--first-row`
-- and use the file it writes exactly as it writes it. **Every one of
those five changes what the description publishes about your table, so
leaving any one out can publish something your first description held
back**: without the `--smallest-group` you gave, a value that fewer rows
share can be named; without the `--identifier` you gave, a column of
record numbers is described like any other column; without the
`--missing-value` you gave, a stand-in is read as a real reading and can
be published as the column's smallest value; without the `--keep-value`
you gave, a word you had counted as an ordinary value becomes a gap,
which can change what kind of column synthtwin sees and publish both
that word and the column's own numbers; and without the `--first-row`
you gave, the first line of your file is read as the column names and
published as them. The refusal says all of that on its own face (owner
rulings 2026-08-17, plan amendments A-P3-36 and A-P3-42: it named two
options and left three out until the first ruling, and until the second
it named five and priced only two of them, which told a hurried reader
which three were safe to forget). There is no release before this one,
so every description in existence belongs to somebody who still holds
the table it describes -- which is why the change was taken now rather
than after a release, when the same change would cost strangers a
migration (owner ruling 2026-08-17, plan amendments A-P3-27 and
A-P3-28; the format is `docs/spec/profile-contract-v5.md`).

**Why it changed.** A description has to carry how each cell of your
table became "no value" -- the blanks, synthtwin's own words for
nothing, the stand-in numbers, and the words you named yourself --
because `synthtwin validate` rebuilds that rule from the description and
has nothing else. A version 4 description did not carry it, and the
consequence was not a missing feature but a wrong answer: a table
checked against its own genuine description came back with obligations
reported as missed, with numbers beside them.

- **A declared spelling is stored exactly and escaped only when it is
  printed.** Version 4 rewrote a spelling into its printable form before
  storing it, so a word holding an invisible character and a word
  holding the printable characters that stand for it produced
  byte-identical descriptions. Every page prints the same characters it
  printed before; what moved is the file.
- **The blank count and the pooled count left the spellings map.** Each
  column now carries `n_missing_blank` and `n_missing_withheld`, so
  `missing_by_source` holds one key space -- the spellings your table
  wrote -- and a table whose cells literally read `(withheld)` can be
  described. **After this there is no field of the format in which a
  value of somebody's table and one of synthtwin's own words can land in
  the same slot.** Both counts are the numbers version 4 published under
  those two keys, computed by the same rules under the same floor.
- **The settings block names which of synthtwin's own thirteen published
  words you typed** -- ten spellings it reads as "no value" and three
  stand-in numbers. That block still carries no spelling of your own:
  the member's spelling is written and never yours, no count, column or
  row goes with it, and it is written identically whether or not the
  word occurs in your table. `SECURITY.md` states the delta and its
  bound, and the plain-language summary says it on every run where you
  named a value.
- **A word of your own that you name with `--missing-value` IS written
  into the description, and synthtwin used to tell you it was not**
  (owner ruling 2026-08-17, plan amendment A-P3-31). The column that
  counted those cells names the spelling exactly as your table wrote
  it, wherever at least `--smallest-group` rows share it and the column
  publishes any values at all. That is how a description says how each
  cell was read, it has been true of every version 5 description from
  the day the format landed, and version 4 published the same spelling
  in its rewritten form -- so nothing about your files changed here.
  What changed is what synthtwin tells you: the rule about the settings
  block was written on four pages without saying it was about the
  settings block, so the summary printed your word under `counted as
  missing:` and then told you, four screens lower, that it kept no such
  word. **If you decided a description could travel on the strength of
  that sentence, check the description.** From this release
  `--missing-value`'s help says it before you type; a `profile` run that
  writes one of your words prints a warning naming the word, its column
  and its count before either file exists; the summary lists every word
  of yours the description carries; and `SECURITY.md` states it as a
  named risk with its bounds. No output file moved a byte.
- **`synthtwin validate` reads all of that, so it stops declining to
  check what the description now records** (plan amendment A-P3-29). If
  you kept one of synthtwin's own words as real data -- two hundred
  readings and one `n/a` under `--keep-value n/a` -- checking your own
  table against its own description used to leave fifty-three
  obligations unchecked and ten measured. All fifty-three are measured
  now and every one of them holds. The same is true where you named one
  of synthtwin's words, or a stand-in number, as "no value": the check
  no longer stands down on those columns, whatever the publication floor
  did with the cells, and it no longer stands down on every column of a
  description merely because you kept a value somewhere.
- **Four descriptions synthtwin could not read back correctly, and now
  can** (plan amendments A-P3-32 to A-P3-35). Each was found by review,
  each is repaired here, and none of them changes a byte of any file
  synthtwin writes.
  - **A table whose cells say one of synthtwin's own field names can be
    described.** At `--smallest-group 1`, a table with cells reading
    `n_missing_withheld` -- or a category labelled `(withheld)` -- was
    either refused by the reader as a file "changed since it was
    written", or stopped the `profile` run outright. Nothing was wrong
    with the table or the description; two walks over the file read a
    key your table decided as a name synthtwin decided.
  - **A word you named with `--missing-value` that holds an invisible
    character is recognised again when your table is checked.** It was
    stored correctly and compared in its printed form, so none of those
    cells was recognised, and seven of the checks on that column were
    reported as "not shown" on a file that met every one of them.
  - **A free-text column that holds a word of yours the description
    could not record is now listed as one this description cannot
    support checking**, instead of reporting eleven misses against your
    own table. The limit itself is unchanged and stated as before; what
    was wrong is that it was not being noticed when a second declared
    word had two spellings elsewhere in the table.
  - **A column whose absent cells hold a stand-in number like `-999` no
    longer fails against its own description.** The description records
    that verdict in full, and the check now uses it: a 180-row column
    with twelve such cells reported seventeen missed obligations, with
    numbers beside them, and reports none. **One consequence worth
    knowing:** where a description says a stand-in number means "no
    value" in some column, a twin that happens to generate that number
    often enough can now have those cells counted as absent when it is
    checked. That is the same collision synthtwin has always disclosed
    for its own missing words, on one more kind of cell.
- **Two limits are stated rather than closed.** On a column that
  publishes no value of your table -- free text, record numbers,
  numbers no format can hold -- the source accounting stays empty
  whatever made the cells absent, because publishing the marker word
  there would publish text out of a column that exists to publish none.
  And a spelling fewer than `--smallest-group` cells share is still
  pooled and unnamed. **Both now reach only a word of YOUR own**: one of
  synthtwin's thirteen published words is recorded whatever the floor
  and the column class did with its cells. Where either applies,
  `synthtwin validate` lists the affected obligations as ones this
  description cannot support asking, with a printed reason, instead of
  reporting them as missed.
- **No cell of any twin changed.** No generation rule reads any field
  that moved, and the twin still writes every absent cell as an empty
  field, so the frozen twin bytes are untouched.
- **The four artifacts that DID move, diffed line by line before the
  hashes of the three that have one were re-recorded.** The description
  gained `profile_version: 5`,
  two counts on every column block and two vocabulary lists in each
  declaration record, and nothing else -- one `(blank)` entry left the
  spellings map on each column that had one, and became the count
  beside it. The generation report changed in one line per such column,
  from a blank count dressed as a spelling to a count that says it is
  cells with nothing written in them. The quality report's checked
  census did not move at all; its not-checkable census grew by exactly
  two lines per column, one for each new REPORT-ONLY count, each naming
  itself in words. No verdict changed and no obligation left any report.
  **And the plain-language summary beside the description moved most of
  all**, which an earlier draft of this entry left out although it is
  the file a person actually reads: it now says which of synthtwin's own
  thirteen words you named, it scopes its no-spelling-is-kept sentence
  to the settings block where that sentence is true, and it closes with
  a block naming every word of YOUR own the description carries, the
  column that carries it and how many cells wore it. It has no frozen
  hash of its own, which is why it was the one file the byte-for-byte
  diffing did not force anybody to look at.
- **The frozen reference vectors were regenerated, which this project
  treats as a changelogged event** (determinism rule D12). What moved
  in them is the profile fragments they carry as INPUT, and only where
  contract version 5 moved a key: `(withheld)` left `missing_by_source`
  and became `n_missing_withheld`, and every column block gained the
  two counts, because the loader refuses a block without them. **Not
  one expected twin cell in either file changed**, which is the fact
  that says the oracle still disagrees with nothing. The oracle is an
  independent implementation written from the generation method and
  imports no part of synthtwin; `tools/provenance/check_provenance.py`
  re-runs it and compares the bytes on every guard run.

### Added in Phase 3: `synthtwin validate`, and the fourth artifact
- **The third command.** `synthtwin validate <description>` reads the
  description and one CSV file -- by default the twin beside it, or
  whatever `--twin` names -- describes that file again with the
  profiler's own producer, and writes a quality report: which of the
  description's obligations the file meets, which it misses, and which
  nothing written in a CSV can evidence either way. The report is named
  after the file it measured (`<measured stem>-quality.txt`, so the
  ordinary run writes `<stem>-twin-quality.txt`) and names that file in
  its own first lines, so two candidate files never collide on one
  report and no report can be read as being about a file it is not.
  `--out-dir` and `--replace` work as they do on `generate`.
- **The exit code is the machine channel** (validation method V6.5): 0
  when the check ran and nothing was missed, 3 when it ran and something
  was, 1 when it could not run at all, 2 when the command line could not
  be used. A tool reading exit codes can tell a file that failed its
  check from a file that was never evaluated without parsing prose.
- **The quality report** states its verdict from the census alone. There
  is no sentence saying that every published fact was found, and none
  can be written from these counts: a pass means no checkable obligation
  was missed, with the within-window, authorized-deviation, withheld and
  not-checkable counts standing beside it and never folded into it. It
  carries the same limits every run -- no cross-column structure was
  validated because none is carried, rows independent and the grain
  undescribed, numbers on a twin are not research results -- plus the
  verdict-scope sentence: it is not a fitness verdict for any analysis,
  it validates nothing the description does not publish, and it cannot
  tell a synthetic file from a real one.
- **The write transaction gained a one-target form.** The quality report
  is one file, so two-files-or-neither is not a rule it can keep; every
  other rule is kept, and one is widened. The file a run may not write
  over is now a SET, because `validate` is handed two files and neither
  the description nor the file being measured may be landed on -- by
  lexical path, resolved path, link, alias, or a substitution made
  between the check and the write. A third `ArtifactWords` set gives the
  refusals the validator's own nouns.
- **The teaching chain runs end to end** (plan P3-D6): `profile` teaches
  `generate`, `generate` ends by printing the `validate` command line
  with this twin's own paths in it, and `validate` says what its verdict
  means, what it does not, and which exit code automation saw.
- **The handling rule now names every file a run leaves behind** on
  every claim-bearing surface: the profile, the plain-language summary
  beside it, the twin, the twin's report and the quality report. The
  quality report states measurements taken from the file it checked, so
  a verdict travels under the same rules as the thing it measured. The
  summary joined the list at the same time (plan amendment A-P3-8): it
  was never named, in this phase or the last, although it is the half of
  the description a person actually reads and it repeats the real labels
  the profile publishes. The generation report's bytes moved with it and
  its golden hash was re-recorded; the sentence that called a fidelity
  verdict later work is gone, because it is not later work any more.
- **The claim inventory counts instead of remembering.** The guard that
  was supposed to catch a stale claim accepted the retired wording, so
  six surfaces still counted the commands and the run's files the way
  they were counted before the validator shipped, while every test
  passed. It now takes both totals from the
  product itself -- the commands from the shipped parser, the files from
  the output names the modules carry -- and holds every surface to them,
  bans a built capability from being described as a later phase's work,
  and refuses a walkthrough that runs two of the three commands and
  stops.

### Changed in Phase 3: the quality report says what WITHHELD does not protect you from
- **The validator stops promising a defence it was paying for every
  round, and says so instead** (owner ruling 2026-08-14; plan amendment
  A-P3-13, validation method V5-A1). The rule that the report may say
  about the file it checked only what `synthtwin profile` run on that
  file would publish is unchanged, and so is everything about what may
  be PRINTED: no measured value, no string of the checked file, no count
  its own description pools -- not in the report, not on the screen, not
  in a refusal. What is withdrawn is the second half the rule used to
  claim: that somebody who writes their own descriptions and runs the
  check again and again cannot narrow a withheld number by watching
  which verdicts change.
- **THIS LOWERS a confidentiality guarantee, on the owner's authority,
  and the amendment prices it.** A sweep of hand-written descriptions
  can recover the count of oddly written cells in a numeric column
  exactly, can pin a style count the publication floor hides, and can
  read the header of a file the profiler refuses to describe, one guess
  at a time. In every one of those the person doing it is holding the
  file the number is about: running the check on a file requires having
  the file, and someone who has it can read it.
- **What it buys back, measured.** One subcheck was blunted for this
  defence and nothing else. `styles.canonical.<form>` had its recount
  rounded down to a whole number of publication floors before the
  comparison, so a file between one cell and one whole floor over its
  licence stopped being reported. The rounding is deleted rather than
  left unused, and the teeth are back at ONE cell: on the suite's own
  sixty-row fixture, a column licensed for 24 oddly written decimal
  cells and holding 25 now MISSES, and so does every one of the eleven
  counts inside that block, where all eleven held. No verdict moves the
  other way -- the comparison it replaces was never more than the count
  -- and a twin the shipped generator writes still holds every ceiling.
  The defence was no longer working anyway: the publication floor is
  itself a number the submitted description chooses, so sweeping it read
  the exact count straight back off the rounded comparison.
- **Nothing else is handed back, and the amendment says why for each.**
  Every other withholding this project records has a witness in which
  ONE report told two files apart -- the pooled style windows, the
  verdicts taken off a pooling column's own description, the seven
  withholdings on a file the producer refuses. A report travels to
  people who hold no file, so those stand exactly as they were.
- **The limit is written where a reader meets it.** The quality report
  carries it on every run, at the foot of the part that says what
  WITHHELD means; `SECURITY.md` carries it as a named residual risk; the
  README's limits table carries a row for it; and the charter's honest
  limits carry it for whoever writes the next sentence about
  validation. This moves the bytes of every quality report, and
  `GOLDEN_QUALITY_SHA256` is re-recorded with the reports diffed line by
  line before each re-record, the census identical entry for entry
  throughout.
- **The report says what the withholding PROTECTS before it says what
  it does not, and says it is not permission to move the page.** The
  paragraph used to open on the limit alone, which reads as though
  withholding bought nothing; it now says first that every question the
  report answers is about the one file it was given, that a number it
  withholds is a number it does not print anywhere, and that this is
  what lets the page be read by somebody holding no copy of the file.
  **And it stops there rather than at "so this page can be handed to
  somebody who has no copy of the file", which is what stood there
  first**: on a description made with `--smallest-group 3` that sentence
  sat under a section saying this same page now carries counts down to
  three rows and should not move without approval. Found by reading the
  page, not by a test.
- **No surface may state the withdrawn guarantee, and the suite goes
  red on any that does** (amendment A-P3-13 clause 3). The claim
  inventory in `tests/test_claim_inventory.py` gained a fourth family,
  and it is not a list of sentences: the guarantee was written five
  different ways in five different places, so a ban on any one shape
  would catch that shape only. A statement trips it when it NAMES the
  reader the ruling put out of scope -- a word for choosing what the
  description says, or for running the check more than once, attached
  to the word for a description -- and in the same breath PROMISES
  something about them, either by saying they cannot or by giving them
  as the reason a rule exists. A withdrawal standing near it is what
  tells the honest paragraph from the claim. Measured rather than
  asserted: the withdrawn promise was put back in eight wordings across
  eight files -- the front page, the security document, the charter, the
  validation method and four modules -- and every one of the eight
  turned the suite red.
- **The validation method is a surface of the claim inventory now, and
  had never been one.** It is the normative statement of what a quality
  report may say about a file that was measured -- the document an
  institution's reviewer reads before deciding whether a report may
  leave the building -- and it was the one specification no ban in that
  file covered. Adding it cost nothing: every check there was already
  true of it, and the fourth family then found two passages of it
  asserting the withdrawn promise as a live bound. Both are corrected
  in place, as are two in the plan that still said what V5.3 "says".

### Changed in Phase 3: `--smallest-group` works below eleven, and every file says so
- **A documented option no longer produces an unusable file** (owner
  ruling 2026-08-14; plan amendment A-P3-11). `synthtwin profile
  --smallest-group 2` wrote a description that `generate` and `validate`
  then refused, because the contract required `small_cell_floor >= 11` --
  and the refusal told the person to make the description again with
  `synthtwin profile` and use it exactly as written, which is what they
  had done. The contract's minimum is now 1, under a counted re-seal of
  `docs/spec/profile-contract-v4.md` section 4.4, and the whole workflow
  runs on any floor of 1 or more.
- **THIS LOWERS a confidentiality bound, and the amendment prices it.**
  The floor is what keeps a published group too large to point at one
  person. At a floor of `f`, no group named in a description covers
  fewer than `f` rows; at 1, every group is named exactly, a group of one
  row included. Where one row of a table is one person, a low floor
  publishes that a value exists together with how many people have it --
  the count is the disclosure, not a route to one.
- **Nothing else is relaxed.** Every floor-governed invariant still binds
  at the value the document carries (B5, D3, N2, N4, P2, V1, W5); at a
  floor of 1 nothing may be held back at all, and a description that
  fills a held-back field is refused under contract invariant S13. A
  floor of zero or below is still refused, and a hand-edited description
  is still refused for every other reason it was refused before. (This
  entry first said the refusal was "for breaking the invariant it always
  broke", which was true of three fields and false of five; amendment
  A-P3-16 below is the repair.)
- **The consequence is made visible rather than softened.** A `profile`
  run at a lowered number prints an unmissable warning before either
  file exists -- what a group that small can reveal about a person, in
  those words, and where those counts travel next. The plain-language
  summary, the generation report and the quality report each state on
  their own face that the description was made that way, so a reader
  handed one of those files alone can tell. The twin CSV carries no
  sentence because a CSV has nowhere to put one; its report is written
  beside it.
- **The quality report now names the floor it is running at, on every
  run.** Its withholding rule read "never named in any description",
  which was written when every description had one floor and now invites
  a reader to supply eleven and be wrong about what the report is showing
  them. This is the only change to the bytes of an artifact made at the
  default floor.
- **`_multiplicity`'s refusal at a floor of one reads as a sentence.** It
  composed "a number of rows from 1 to 0"; it now says the block must be
  empty, and why.

### Fixed in Phase 3: a floor of one really holds nothing back, and the report says only that
- **The floor-of-one invariant is enforced, not just written down**
  (plan amendment A-P3-16; contract invariant S13). The rule above said
  a description that holds something back at a floor of one is refused.
  Three fields were refused and five were not: a description written by
  the profiler itself stayed accepted after `(withheld)` was put into
  `missing_by_class`, `missing_by_source`, `utc_offsets` or
  `numeric_styles`, and after `n_sentinel_candidates_unpublished` was
  made nonzero. The reason is that four of those are rules holding a
  PUBLISHED count to the floor and EXEMPTING the pooled remainder -- an
  exemption does not become a rule at the bottom of the range by
  itself -- and the fifth, the count of stand-in numbers too rare to
  name, no rule of the contract bounded at any floor. The loader now
  checks the whole description against S13
  before it reads a column, and finds a pooled remainder by looking for
  the format's one word for "held back" wherever it stands rather than
  by a list of field names -- so a field added later is covered when it
  is added.
- **The profiler will not WRITE one either.** Its publication guard
  checks the finished description before a byte reaches a disk, and its
  rule for a pooled entry ignored the floor entirely. It now has
  vocabulary for the floor's other half. No description the profiler
  writes at any floor changes.
- **The quality report stops saying "At 1 nothing is withheld at all".**
  Two rules put WITHHELD on an obligation line and only one of them is
  the floor's; the other asks whether describing the CHECKED FILE
  publishes a measurement of that kind at all. A floor-one report
  printed that sentence and then eighty-three WITHHELD lines, with the
  count of them in its own verdict summary. It now says what is true --
  nothing is held back for being a small group -- and names the other
  rule. No artifact made at the default floor changes.

### Fixed in Phase 3: a table whose times are stamped in UTC can be described
- **`synthtwin profile` refused every UTC-stamped table** (plan
  amendment A-P3-16 clause 4). The profiler writes `Z` as the offset of
  a cell ending in one, and the strict loader accepts `Z` wherever an
  offset may stand -- but the profiler's own publication guard did not
  know the string, so a column of `2024-03-17T09:00:00Z` stopped the
  run with the message that says this is a fault in synthtwin itself
  and there is nothing to fix in your file. The two writings of what a
  UTC offset is now accept the same strings, checked against each other
  string by string, and that comparison closed a second disagreement in
  the other direction: the guard accepted offsets out of range that the
  loader refuses.

### Fixed in Phase 3: checking your own table no longer reports failures that are not there
- **If you named a word with `--missing-value` or `--keep-value`, the
  description does not always record the word -- and the check now says
  so instead of failing your table** (owner ruling 2026-08-16, plan
  amendment A-P3-26, validation method V2.4-A5 and V3.5-A3). To measure
  a file, `synthtwin validate` first works out how the description read
  its cells, from the description alone. There are five ways a word you
  named does not survive into it: it is never written into the settings
  block; it holds an invisible character and is rewritten before it is
  stored; too few rows share it, so it is pooled away unnamed; the
  column publishes no values at all, as a free-text column does on
  purpose; or your own text happens to spell one of synthtwin's own
  words. On every one of those, checking your table against its OWN
  description reported obligations MISSED -- seven, or eleven on a
  free-text column -- with numbers beside them, on a file that matched
  its description perfectly. **The description can always tell that it
  cannot rebuild the rule, even when it cannot rebuild it**, so those
  obligations are now listed as ones this description does not support
  checking, each with a sentence saying what it does not record. They
  are counted on their own line and never folded into a pass.
- **What that costs, said plainly** (plan residual R-P3-8). It is a real
  lowering on an affected column: every obligation counted over that
  column's cells moves, so a free-text column keeps ten checks where it
  had thirty-one, and a numeric one ten where it had fifty-three. The
  same limit applies to the twin of such a description -- the twin holds
  no marker word and passes, and the check has no way to know that
  without reading something the description cannot see. And a file that
  really does miss one of the moved obligations now ends at exit code 0
  with them named rather than at exit code 3. Closing the routes behind
  this needs a change to what a description records, which is a decision
  taken in the open; one of the five -- a marker word in a free-text
  column -- cannot be closed at all without publishing text out of a
  column that exists to publish none.

### Fixed in Phase 3: a description ten spellings answer is no longer refused
- **A repetition count is read as the figures it is written in** (plan
  amendment A-P3-25 clause 1, validation method V4.2-A2). A description
  says how many rows each repeated value covers, written in figures. The
  check read those figures through the same reader it uses for a
  measurement, which is exact only up to about nine quadrillion -- so a
  description saying that ten values cover 9,007,199,254,740,993 rows
  each was read as saying one row less, the division that follows came
  out needing ELEVEN different spellings where ten are asked for and ten
  are available, and `synthtwin validate` stopped and said that no file
  could be that description's twin. It builds one. On a column you
  declared to hold record numbers the same arithmetic quietly took three
  checks off the report instead of stopping the run. The count is read
  as a whole number now, at any size, by the same reader that admitted
  it -- and a new guard follows every such key of the description
  through the code and refuses any reader that would round it, wherever
  somebody adds one.
- **A lesser bar is only ever given to the fact it was granted for**
  (plan amendment A-P3-25 clause 2). Where a column of labels holds back
  spellings that are too rare to publish, the ratified plan lets the
  twin fall short on how many different SPELLINGS it writes. That
  permission was being handed to a second count as well -- how many
  different values the column holds once upper and lower case are
  ignored -- which the description states exactly and the twin meets
  exactly. A file holding three such values where the description
  publishes two was called an authorized difference instead of a miss.
  Each count is now asked about on its own, and the check that compares
  this validator against the tool's own generator no longer skips a fact
  the generator met exactly, which is how the hole survived beside a
  green test.
- **A check that could not fail is a check again** (plan amendment
  A-P3-25 clause 3). How many different spellings a column of numbers
  can carry is worked out from two things: the numbers themselves, and
  every cell of that column that is NOT a number. The second was left
  out entirely, so a column of twenty whole numbers beside two cells of
  text was told a twin might hold as few as ONE different value -- a
  range from one value to every cell in the column, which no file can
  fall outside. Both distinctness obligations were dropped from the
  checks for that reason, and a file one value short of what the
  description publishes was told that nothing was missed. Those cells
  are counted now, at both ends of the range, and the obligations are
  checks again. **What is still open is written down**: how many
  different values the plainly-written numbers carry is decided by a
  construction this check may not read, so a file one value short of a
  count the twin's own report pins is reported as an authorized
  difference rather than a miss, and a test holds that gap at exactly
  that size.

### Fixed in Phase 3: four guards that reached less far than they read
- **A refusal a person can act on, held to that by the catalog like
  every other refusal** (plan amendment A-P3-23, validation method V9).
  When a description asks for a table that cannot exist, `synthtwin
  validate` stops and says so. That message was built inside the
  validator rather than in the file every other refusal lives in, so
  none of the rules that keep those messages readable -- open as a
  sentence, end as one, no programmer's language, and always tell the
  reader what to do next -- reached it, and nothing had ever pinned what
  it says. It is a catalog entry now. Its exact wording is pinned for
  each of the four things that can be wrong with such a description:
  which two published facts collide, that the description itself is
  valid, that no file can be its twin, which file was being checked, and
  both of the two instructions -- describe the table again, and, for
  somebody who was handed the description and holds no table, ask
  whoever wrote it. And it is now produced by running the command: a
  table is written, `synthtwin profile` describes it, and `synthtwin
  validate` on that description has to stop with this refusal.
- **The profiler will not WRITE a floor-one description that holds
  something back** (plan amendment A-P3-22). At a floor of one nothing
  is held back, and the strict reader has refused a description that
  says otherwise since the previous round. The half that WRITES
  descriptions was taught the same rule field by field, and one field
  was not on the list -- so the two halves of the product disagreed
  about what a floor of one means, on a real map the profiler builds.
  The writing half now looks for the format's own word for "held back"
  wherever it stands, which is the reach the reading half already had.
  What found this is the other half of the repair: the check that
  derives the rule from two descriptions of one table now puts every
  case it derives to BOTH halves instead of only to the reader.
- **Two guards that read less than they said they did** (plan amendment
  A-P3-24). The first walks the code that decides which cells of a
  checked file its own description reads, and refuses any reader in
  there that answers in the machine's own approximate arithmetic --
  because the same defect had come back three times. It read a call
  written as a name or as a dotted name, and dropped every other way of
  writing one, so a reader reached out of a list was invisible to it. It
  is now total over the ways a call can be spelled, with a probe for
  each, and it refuses a reader NAMED where a value belongs even where
  nothing calls it here. The second is the guard over the guarantee the
  owner withdrew on 2026-08-14, which no page here may make again in any
  wording: that somebody who re-runs the check with descriptions of
  their own is kept from narrowing a withheld number. It read one
  statement at a time, so the same promise written across two statements
  walked past. It now carries a promise forward to a
  following statement that is about the withheld number, which was
  measured against every surface here before it was written and reports
  none of them.

### Fixed in Phase 3: a check that passed a file its own description rejects
- **A "no value" spelling is read back out of the description only where
  reading it back is safe** (plan amendment A-P3-19, validation method
  V2.3-A2). The description publishes the spellings that made a column's
  cells empty, and the previous round read them back so that a person
  who profiles their own table with `--missing-value` and then checks
  that same table is not told its declared holes are data. But that
  field is written for a REPORT: a character that would command a
  terminal is replaced by text showing what it was, and two different
  spellings can come out the same. Both directions cost a verdict. A
  table whose holes hold such a character was told seven of its
  obligations were missed against its own description; and a DIFFERENT
  file, wearing the printable spelling, passed that description with
  nothing reported at all, although describing that file under the same
  declaration reads it as free text with every cell present. A report
  that passes a file its own description rejects is the one failure this
  project will not ship, so the read-back now covers only the spellings
  the report-writing cannot have altered. What that leaves is stated:
  where the spelling holds such a character, the table it was written
  from reads those cells back as data, and closing that needs a change
  to what the description publishes rather than a change to the checker.
- **The report on a description of NO rows is chosen by the reader, like
  every other report** (plan amendment A-P3-20, validation method
  V5.1-A1.2). An earlier round made the reader's own refusal decide
  which report a file gets, so two files `synthtwin profile` refuses
  with one sentence cannot draw two different reports. One branch never
  reached that rule: a description publishing no rows was answered
  before the file was ever read. Two files with a ragged row under
  differently-spelled headers -- one refusal to the profiler -- drew
  eight met obligations and one missed against five and four, and the
  check said the header names were correct about a file no reading of
  which finishes. The reader is asked first there too now, and a file it
  refuses for anything but "this file has no rows" comes back as that
  refusal, which is the more useful answer and the one the profiler
  gives for the same file.

### Fixed in Phase 3: the check now agrees with the twin the tool itself writes
- **`synthtwin validate` no longer reports the product's own output as
  missing an obligation** (plan amendment A-P3-18, validation method
  V4.2-A1). The validator decides four "corner" questions from the
  description alone, written from its own specification so its verdicts
  cannot inherit the generator's defects. That independence is only
  worth having if the two writings agree, and until now nothing
  compared them: `tests/test_p3v7f2_corner_parity.py` builds 219
  descriptions with the real profiler, asks the shipped generator for a
  twin of each, measures each twin with the shipped validator, and puts
  the two accounts of each governed fact beside one another. The two
  writings parted company in five places, and at each of them the twin
  met its description while the report said it had not.
- **A column of record numbers is measured against the values the tool
  can actually write** (A-P3-18 clause 1). Above one character the
  check counted every string the alphabet allows rather than the
  values the construction writes -- 8,460 two-character values where
  2,538 exist -- so a column of 2,539 of them was told it should hold
  them all and its twin was reported wrong three times over. A second
  gap of the same kind: a group of cells that has to be covered by
  values of its own alphabet needs at least as many different values as
  the widest repeated group leaves room for, which the earlier
  arithmetic could miss.
- **Two counts of different values are measured against the range the
  method allows, in both directions** (A-P3-18 clause 2). A column of
  labels whose held-back spellings covered it exactly was read as
  needing one more than it does, so the check demanded a count the tool
  cannot write; and a column of numbers whose own spellings force MORE
  different values than it publishes was held to the published number
  exactly, so its twin was reported wrong for holding what its
  description obliged it to hold. A file that now holds more different
  values than published, on a column whose spellings can carry them, is
  reported as an authorized deviation rather than a miss.
- **A check that could not fail is no longer printed as a check**
  (A-P3-18 clause 3). Where a column's own spellings leave the count of
  different values anywhere between one and every cell -- two hundred
  forced whole numbers written one way are the case -- the comparison
  admitted every file and proved nothing. It is now one line in the
  not-checkable part of the census, with the sentence saying why.
- **Two more obligations no CSV can evidence** (A-P3-18 clause 4). A
  datetime column whose earliest or latest offset was itself held back
  by the publication floor names no offset for that end, so nothing in
  a file can carry it; and a numeric column whose style map the floor
  has partly pooled owes at least the published count of a named form
  and at most that count plus the pool, rather than the published
  number exactly.
- **What is still open, said plainly** (A-P3-18 clause 5). How many
  different values a column's plainly-written cells carry is decided by
  the value construction, which the checker may not import and does not
  yet rewrite, so for a column of numbers it draws a range that HOLDS
  the generation report's rather than one equal to it. The suite
  asserts containment and says so.

### Fixed in Phase 3: three ceilings that did not mean what they said
- **A search allowed two hundred and fifty-six tries spent two thirds of
  them re-asking a question it had already answered** (plan amendment
  A-P3-17 clause 2, method G9.3 step 5). The rule that repairs a twin's
  count of different record numbers once case and edge spacing are
  ignored may try a stated number of layouts before it gives up. It was
  counting the tries and not the questions, and on a column found by
  review the same question came round ten times over: **2,466 tries
  carrying 246 different questions**, and the ceiling ran out having
  answered 82 of them -- before the first layout that would have
  worked. A question is now asked once and remembered. Measured on a battery of 1,174 columns the profiler wrote
  from real values, at four seeds: **12 of 4,696 twins missed that
  count before and 4 miss it now**, every one of the twins whose bytes
  moved is one that was wrong before, and the count of cells opening
  with a character a spreadsheet reads as a formula is unchanged.
- **The four that remain are one column, and the changelog says so
  rather than rounding to none.** Its cause is neither the ceiling nor
  the search: with every ceiling removed, 2,097 layouts are offered for
  that column and not one of them can build every collision it owes.
  The twin names the deviation in its report, as it always did.
- **A repaired layout is now held to what it WROTE, not to what its
  arithmetic promised.** A layout can name a family that has no spelling
  at the length its slot is pinned to; the twin then falls back to
  another alphabet and loses a count -- how many cells read as numbers,
  how many are figures alone -- that the layout met on paper. Every
  published count is recounted off the finished cells, and a repaired
  layout that gives up any count the first layout held is refused.
  **On the two batteries measured this check never fires**, and that is
  said here rather than left to be assumed: it is kept for the witness
  that reaches such a layout and for the property the amendment states,
  not for a number it moves.
- **The proof that every check the quality report ships can fail was
  walking one of the four kinds of description it ships for** (plan
  amendment A-P3-17 clause 3, validation method V8.3-A1). The two
  degenerate zero-row forms file fifteen checks between them and not one
  had a test showing it could fail, or binding it to the obligation it
  answers for. All fifteen now do.
- **The guard that keeps a withdrawn promise out of this repository was
  not reading the governing plans** (plan amendment A-P3-17 clause 1).
  It named a passage of one of them as a place the 2026-08-14 ruling had
  to correct, and never opened it. It reads them now, and found one
  stale claim on the first run: a paragraph still describing a bound
  that was deleted the same day, now marked superseded where a reader
  meets it. Three sentences that walked past the guard -- a promise made
  as an outcome rather than as a barrier, a word for a description it
  did not carry, and a withdrawal standing in front of the promise it
  was read as curing -- are kept as its own tests. **What a list of
  words cannot do is stated beside the list**: no finite list bounds an
  infinite set of paraphrases, so this is a guard and not a proof, and
  what would be a proof is written down in the amendment for the owner
  to weigh.

### Fixed in Phase 3: a twin of a column of record numbers holds its folded count
- **A published count the twin got wrong on 3.7 per cent of a battery
  of real producer descriptions is right on all of them** (owner
  ruling of 2026-08-14, plan amendment A-P3-12, method G9.3 step 5).
  **Corrected 2026-08-14**: "all of them" is all of the two batteries
  measured below. A third battery, built later to a different shape,
  found the miss again on 12 of 4,696 runs; that is repaired and
  measured under A-P3-17 clause 2 above, where the four runs that still
  miss it are counted rather than rounded away.
  Where a description of a column of record numbers records two
  spellings that come down to one value once upper and lower case and
  spaces at the ends are ignored, the twin owes that collision. Which
  values carried the collisions was settled before any of them was
  spelled, and whether a family of values can carry one depends on the
  spellings: a value already at the longest published length cannot be
  lengthened by a space, and a value with no letter cannot change case.
  So the twin could ask one family for more collisions than it had room
  for while another family stood idle, and wrote a fresh value instead
  -- missing the description's own count of how many different values
  it holds ignoring case. Measured on two independently built batteries
  of descriptions the profiler wrote from real columns, every one of
  which its own column answers exactly: **44 of 1,200 and 68 of 918
  were wrong before; none is wrong now**, at four seeds.
- **A twin that already met every published count does not move by one
  byte.** The layout that shipped is tried first and kept the moment it
  works, so the repair can only reach a column that was already wrong.
  Measured: on this project's own 200-description identifier battery at
  four seeds, 800 twins, not one byte changed and the count of cells
  that open with a character a spreadsheet reads as a formula is the
  same before and after. Across both hazard batteries, every run whose
  bytes moved is a run that was missing a published count.
- **What it costs, stated rather than left to be found.** Two of the
  1,200 repaired columns now write 9 and 12 cells opening with such a
  character where they wrote none; no column writes more of them than
  it did in order to gain nothing, and every one is named in the
  generation report as before. Generation is seven to fifteen per cent
  slower across a battery in which every failing column is included,
  and unchanged on a column whose first layout works.
- **And where such a count still cannot be held, the report now says
  something TRUE about a column of record numbers.** The line carried
  the sentence written for a column of dates -- that how often a value
  repeats is not a fact the column's rule holds on to -- which is false
  of this one role, whose rule meets the repetition pattern in the same
  run. It now says what actually happened: the description asks for two
  spellings that come down to one value, and the published length range
  left no second way to spell one of them.

### Fixed in Phase 3: the Windows half of the matrix could not run the suite
- **One line in one test stopped every governed Windows cell** (review
  item P3-V4-F10, round 5 item 10). The proof added last round drives
  the "this file could not be opened" refusal through the shipped
  command at a real condition, and it decided whether to skip by
  calling `os.geteuid()` -- a function Windows does not have. All ten
  `windows-latest` cells of the CI matrix therefore ended in an
  AttributeError before proving anything, and CI green is a merge
  requirement, so one test's convenience blocked the branch outright.
- **The condition is now built in the mechanism each platform HAS, and
  the mechanism is checked before the command is run.** POSIX takes
  every read permission off the file. Windows locks the file's whole
  length against every other handle -- locks there are mandatory, and
  "the file is open in another program" is how a Windows user actually
  meets this refusal -- with a share-nothing handle as a second try.
  Whichever mechanism ran, the file must be present and must refuse to
  open before the case proceeds, so a mechanism that quietly does
  nothing (`chmod` on Windows moves the read-only attribute and
  nothing else) makes the case fail rather than pass. Guarding the old
  call with the platform name instead would have swapped an error for
  a skip on the one platform this refusal matters most on.
- **Two further proofs that were skipping on Windows now run there.**
  The refusal that stops `generate` writing a twin over the
  description through a link is asserted on every platform, each in
  the sentence its own rule produces -- the stricter Windows rule had
  nothing asserted about it at all for this command. And the fixture
  guard's process-helper mutation no longer carries a POSIX-only mark:
  the guard refuses an import by NAME, before the interpreter goes
  looking for the module, so the case is driven on every platform.
- **The fixture guard learned what Windows uses to create a process.**
  Asking that question is what the skip above had been hiding:
  `_posixsubprocess` was in the blocked-import list and `_winapi` --
  the module that creates a process on Windows, emitting no
  `subprocess.*` audit event of its own -- was not. Both are blocked
  now, as is every `_winapi.*` audit event.
- **Where a condition genuinely cannot be built on a platform, the
  test says so by name.** A folder that refuses to be written cannot be
  made from the standard library on Windows, and a POSIX superuser
  reads a file whose mode bits forbid everybody; both skips now name
  the host and the reason rather than reading as though the check had
  held there.
- **And the suite now asks this question of itself.** A new guard reads
  every test module and refuses two things: a call to an `os` member
  Windows lacks that nothing has guarded, and a module-level import of
  a module only one platform has -- which would fail collection for a
  whole file rather than one test. On the state before this repair it
  names `os.geteuid` at the line that broke the matrix.

### Fixed in Phase 3: six proofs that proved less than they claimed, and two stale sentences
- **The non-vacuity proof no longer reads its answer off the thing it
  is testing** (review item P3-V4-F6). An entry of the shipped
  validator's table is the triple (registry fact, profile predicate,
  subcheck), and five hundred and nineteen of the five hundred and
  eighty-eight registered red cases named only two of the three: the
  registry FACT was taken off the validator's own output at test time.
  Rebinding a subcheck to another fact of the same disposition
  therefore moved the expectation with it, and coverage, membership and
  uniqueness all stayed green over a table whose facts were wrong. The
  binding is now written out in the test file and compared with the
  shipped table in both directions: the roles the fixtures are
  described with are stated and checked against the DESCRIPTION, the
  fact each subcheck answers for is stated and checked against the
  REGISTRY, and no site may bind a fact other than the one stated. Two
  hundred and thirty-eight lines of stated expectation replace five
  hundred and nineteen derived ones.
- **And that proof walked half the table** (plan amendment A-P3-21,
  carrying the same review item). An entry of the shipped table is
  either a verdict or a line saying no CSV can evidence this
  obligation, and the binding proof read the first kind only. So the
  nine entries that exist ONLY where a corner sends a fact to the
  second kind -- four about a datetime column's offsets, three about a
  record-number column's counts of different values, two about a
  numeric column's -- were bound by nothing: rebinding one of them to
  another fact of the same column left the whole suite green while the
  report named one fact twice and another not at all. The walk now
  collects both kinds, over the six ordinary fixtures, the four
  description shapes, and three descriptions built here by the real
  profiler for the express purpose of reaching a corner, each held to
  the corner it is for.
- **The claim guard can no longer be evaded by how a constant is
  spelled** (review item P3-V4-F7). The reading that counts what a full
  run leaves behind recognized one spelling of an output name, so a
  sixth output declared as a typed constant, in single quotes, under
  any other name, or built by a call left every "five files" sentence
  in the repository green beside a run that wrote six. The reading is
  now of the package's own syntax rather than of one line shape, and
  beside it a test RUNS the three commands and counts the files on the
  disk, which no spelling can hide from. It found a live stale claim on
  the way: `quality.py`'s handling helper said "four files" while
  printing the five-file rule.
- **A private docstring stopped claiming a necessity the report does
  not.** The generation report says an invented sign-leading cell
  proves the real column held such values only WHERE the description's
  counts leave no other spelling, and says synthtwin does not always
  reach for the fewest it could. The helper that composes those lines
  still said it flatly, of every such cell.
- **The randomness trap reaches the engines** (review item P3-V4-F8).
  It enumerated four modules written out by hand and their public
  attributes, so `numpy.random._mt19937.MT19937(1).random_raw()`
  returned values with the whole claimed trap installed. Every module
  reachable by attribute from `numpy.random`, `random` or `secrets` is
  now walked, private submodules included; classes are trapped where
  their methods cannot be; and the two module-level generator instances
  are replaced by stand-ins that refuse to be read.
- **The line-ending guard has no route around it any more** (review
  item P3-V4-F9). It followed a written path by the name of the
  variable, so a helper that returned an extensionless path, stored in
  a list and handed over as `paths[0]`, was outside it. Every
  text-mode write in the suite now pins its line ending -- sixty-six
  writes gained the argument -- and so does every handle opened for
  writing, so no classification decides what the rule covers.
- **The failure catalog's reachability is driven, not searched**
  (review item P3-V4-F10). Its reachability test looks for the
  builder's name in the source, which a refusal whose raise site had
  been refactored away would still pass -- measured: taking both
  handlers for an unreadable measured file out and leaving the token
  behind kept that test green while a `PermissionError` reached the
  person as a traceback. The refusals plan P3-D6 names for the validate
  path are now produced by running the shipped command at the real
  condition, with the exit code and the printed sentence both asserted.
- **A stopped `validate` run says which file it did not write** (review
  item P3-V4-F11). It said "No new description was published" about a
  command that writes no description, and a stopped `generate` run said
  its own twin file held "the new description this run produced". The
  words a command carries now reach both sentences and the clause
  saying what a working file holds; the profiler's messages are
  unchanged to the byte.

### Fixed in Phase 3: two guarantees the documents claimed and the code did not have
- **A verdict about a spelling no longer counts out loud.** Whether a
  numeric cell's text is a spelling its own value licenses is a fact
  `synthtwin profile` publishes about no file at any count, so the plan
  rules it outside the disclosure envelope -- and a ruling like that is
  worth exactly the bound it carries. The bound written down was one
  bit per column; the ceiling on non-canonical cells compared its exact
  recount against a number the submitted description names, so eleven
  candidate descriptions read that recount off the report exactly, and
  two files whose own descriptions are the same bytes came back HELD and
  MISSED. The recount now reaches the verdict only at the publication
  floor's own resolution -- the resolution below which a description
  names no count at all -- so a sweep locates the floor-wide block and
  never the number. It costs teeth, and the plan prices them: a file
  less than one floor over its licence is no longer missed there, and
  no arrangement can have both, because the licence is the submitted
  description's own number. **This entry is superseded: the owner ruled
  the candidate sweep out of scope on 2026-08-14, the rounding is gone
  and the teeth are back at one cell.** See the entry above, "the
  quality report says what WITHHELD does not protect you from".
- **A report about a file the producer refuses says what that refusal
  says, and now it cannot say anything else.** Two of the reader's
  refusals are reported on rather than passed along, and which report a
  file got was decided by a walk `synthtwin validate` did before the
  reader was called. That walk and the reader had a precedence to agree
  about, and did not: moving a repeated name's columns moved the report,
  adding one row under a header holding a zero byte turned a report into
  a refusal, and a ragged file changed which refusal it drew as soon as
  a name was repeated in it. The walk is gone. The reader is called
  first and the report is chosen by the refusal it raises, so two files
  the producer refuses with one sentence get one report by construction.
  The repeated-name refusal and report also stop naming which columns
  repeat: the profiler's own refusal quotes the name and names no place,
  so the place was never a fact a report about that file could state.

### Fixed in Phase 3: three readings the validator's own generator contradicts
- **A reading you keep is a reading, not a hole.** A researcher who
  keeps `-999` as real data profiles with `--keep-value -999`, and the
  description publishes that candidate as kept. `synthtwin validate`
  deleted those cells from its recount anyway -- every built-in missing
  spelling and every built-in numeric stand-in, whatever the description
  said about them -- so the twin `synthtwin generate` writes from that
  very description came back with style obligations MISSED and exit 3.
  A cell is now dropped only where describing the measured file reads it
  as a hole: the description's own kept set first, the built-in table of
  missing spellings next, and a stand-in's fate taken from the column's
  own published verdict on that candidate. The same defect rejected a
  person's own table where the producer keeps a stand-in because the
  column's spread makes it no outlier -- a route with no declaration in
  it at all, which the twin cannot even reach.
- **A column of dates is measured against the construction that writes
  it.** The generator pins the first and last cells of a datetime column
  to the published earliest and latest instants; the validator's window
  did not, so a file holding six different quarters passed a bound its
  own construction puts at seven. The allowance for reading a cell back
  was a step of the published precision plus fifty-nine seconds instead
  of one unit of the ordinal space plus fifty-nine, so a rung sitting a
  whole minute below its window was reported inside it. And the ladder
  was read with floating-point arithmetic where the method fixes whole
  numbers, in seconds where the method counts a whole date in days,
  which drew windows ending in the middle of a day -- part of a day
  narrower than the construction, so a conforming twin could be called
  wrong at a rung. All three are one repair: the window is written out
  from the method, and the suite compares that writing with the
  generator's own at every resolution, every precision and eight column
  lengths, so the next drift is red on the commit that writes it.

### Fixed in Phase 3: the sign a table already had, and the check that had gone quiet
- **Owner decision 9 (2026-08-13).** A record number synthtwin invents
  may open with a sign where the published counts leave no other
  spelling of that width -- which is also the proof the real column held
  such values, so the twin inherits a hazard the table had rather than
  making one up. The refusal that stood here for a day is withdrawn.
  Where it is needed is decided by the packing, which runs first with
  that family closed and reaches for it only when no assignment of whole
  groups meets every published count without it.
- The generation report's spreadsheet paragraph told every reader that a
  hazardous cell was a value their description published. For a column
  that publishes no values at all that was false. It now names the
  columns whose cells were invented, says why the counts left no other
  spelling, and says that the same cells behave the same way in the real
  table -- which is where it points the reader to settle it.
- **Owner decision 11 (2026-08-13).** The frozen reference oracle still
  implemented the retired pooled-plain rule on a branch no frozen case
  exercised, so the independent check on pooled spelling was not in
  force there and every vector stayed green regardless. The oracle now
  carries the amended rule, a sixth branch case reaches the branch, and
  that case carries a mutant which must change its cells.

### Fixed in Phase 3: a whole number keeps its shape at any width
- **Owner decision 10 (2026-08-13).** A column whose source wrote very
  wide whole numbers in figures -- more than sixteen of them -- was
  published `plain` and came back from the twin as
  `100000000000000000000.0`, which a reader takes for a decimal column.
  That is exactly the type change the published spelling map exists to
  prevent. The sixteen-figure ceiling that caused it belongs to the
  canonical spelling of a number in the profile DOCUMENT, and was being
  applied to the twin's plain cells, where it does not govern: such a
  cell owes only that it reads back as the same number and classifies
  as plain, and a whole value's full digit expansion does both however
  wide it is. No frozen case reached the branch, so no golden hash and
  no reference vector moved; a column that does reach it now writes its
  digits.

### Fixed in Phase 3: the two open defects the registry carried
- **The pooled numeric spelling (P2-C5-F3).** A description holds back
  the forms used by fewer rows than the smallest group size, and the
  contract wrote every one of those cells plainly -- which a column
  whose published smallest or largest value carries a decimal point can
  never do, because such a value has no point-free spelling at all. The
  twin was therefore required to miss a total no generator could reach,
  on 8 of the producer battery's 240 columns. A held-back cell names no
  form, so it is now spelled by its own value: plainly where the value
  has a point-free spelling, and in the value's own canonical text where
  it has none. Contract 7.5.7 and method G6.4 carry the amended rule and
  a recount identity whose every clause is checked separately, with each
  published count a floor so no form can be substituted away. The
  ordinary case moves no byte.
- **The two-character record number (P2-C5-F4).** Its first shape was
  already closed by the joint packing that settles length and band
  together; only the contract's prose still said otherwise. Its second
  shape was a genuine breach: for a two-character whole number in the
  code alphabet the generator wrote `-0` through `-9`, meeting the
  published count by breaking the rule that no invented value may open
  with a character a spreadsheet reads as the start of a formula -- and
  leaving the report's own formula paragraph telling the reader that an
  invented cell was a value their description published. The family is
  withdrawn, the code band starts at three characters, and a description
  that leaves no spelling at all now meets a named refusal instead:
  `generation-whole-numbers-need-code-room`, the fifth of method G12,
  landed there as an amendment rather than as an unannounced branch.
- The disposition registry's `OPEN` mapping is empty for the first time
  since it was created.
- Two defects the repairs and their reviews found are recorded rather
  than fixed quietly, each with its measurement and its two possible
  outcomes, in the Phase 3 plan's P3-D8.1: the same two-character code
  family reached by a column whose values are not all whole numbers,
  and a column of very wide whole numbers, which a source writes in
  figures and the twin writes with a decimal point. Both need an owner
  decision. A third record sits beside them: the frozen reference
  oracle still implements the retired pooled-plain rule on a branch no
  frozen case exercises, so its independent check on pooled spelling is
  not in force until that decision lands and the oracle moves with it.

### Added in Phase 3: the ratified plan, and the repository goes public
- The Phase 3 plan (`docs/plans/phase-3-product.md`): the validate
  command and its plain-language quality report, the repair of the two
  open registry defects, the visibility flip, and the first release --
  ratified at plan review round 5 after four rejecting rounds whose
  every item is trailed in the plan's own review record; the five
  reviews are in `docs/plans/reviews/`. The plan joined the governing
  set under the disposition seal in the same change, so `GOVERNING`
  now holds four documents and the guard's exact lists moved with it.
- Phase 2 closed by owner decision (2026-08-12), its review record
  standing exactly as written; the charter's phase ledger now says so,
  and Phase 3 is current.
- Stage 1 of the plan's claim migration: every sentence describing the
  repository as private, on every live surface including the CI
  workflow and the tools, is retired in favor of the visibility-flip
  story, enforced by a new whole-tree test
  (`tests/test_p3_flip_migration.py`) because the claim inventory's
  surface list deliberately excludes `.github/` and `tools/`. The
  historical records -- the changelog and the plans -- keep their own
  dates' truth.

### Added
- Phase 1, the profiler: `synthtwin profile <table>` reads a local CSV
  table and writes two files -- the machine-readable profile the twin
  will be built from, and a plain-language summary that is also printed
  on the screen. Every column is given exactly one role (record number,
  whole numbers, measured numbers, dates, categories, two-value, free
  text, constant, empty) with the evidence for that reading recorded in
  words; missing values are counted by the spelling they were written
  in; numeric stand-ins for "no value" are recognized only when they are
  both outliers and frequent, with the verdict reported either way.
- Suppression by role (plan P1-D6): a column read as record numbers, as
  free text, or as numbers no format can hold publishes no value of
  itself anywhere, and a label shared by fewer than eleven rows is
  pooled into a counted remainder. The summary states, every run,
  exactly what of the real table the profile carries.
- The table is read twice -- by the standard library's CSV reader for
  structure and by pandas for the values -- and the two results must
  agree. This is what turns a short row into a refusal naming the row
  instead of a row silently padded out with invented missing values.
- The first runtime dependency, `pandas`, with a written justification,
  a declared floor that a new `minimums` CI job installs and tests, a
  hash-pinned runtime closure (`requirements-install.lock`) exercised by
  the offline fresh-venv smoke test, and an enumeration in the offline
  scanner that reduces the library to the exact function this code calls
  (`read_csv`, and nothing else). It was the only *direct* dependency
  of Phase 1; `python-dateutil` and the others in the lock arrive inside
  pandas's own requirements and are imported nowhere in `src/`.

- The generator, `synthtwin.generation`: the twin's cells built from the
  profile and a seed and from nothing else -- one random stream, made
  once from the seed, threaded through by hand, with every value derived
  from full-width whole-number draws in first-party arithmetic. It never
  reads the real table, reads no file at all, and hands back the cells
  together with a record of what the twin ACHIEVED beside what the
  profile PUBLISHED, so the report names every difference rather than
  implying there was none.
- The second direct runtime dependency, `numpy`, under the same protocol
  as the first: a written justification (plan P2-D8), a declared floor
  the `minimums` CI job installs and tests, and the hash-pinned closure
  regenerated. The generator uses exactly one name from it,
  `numpy.random.default_rng`, and exactly one call on what that returns.
  The profiler still computes its own statistics and imports numpy
  nowhere.
- **The frozen generation reference vectors** (plan P2-D7, method
  section G14): `tests/reference/generation-reference-vectors.json`,
  built by `tools/reference/make_generation_reference_vectors.py` and
  bound in the provenance manifest, so CI rebuilds it from the generator
  and byte-compares it on every run. The tool implements the published
  method specification from that document alone and imports neither this
  package nor numpy nor pandas -- it could not import numpy in any case,
  because the fixture guard refuses `ctypes` and numpy imports `ctypes`.
  It therefore states its vectors as a pure function of GIVEN uint64
  words, which the file carries as inputs, and derives every uniform,
  bounded range, arrangement and cell from them in exact standard-library
  whole-number arithmetic. Fourteen cases are covered, across two
  committed files that are one oracle -- one transform, one proof layer,
  split only because each file must stay under the manifest's byte cap.
  The first nine: a date-only column, a quarter column, an offset-bearing
  column on the utc clock, a column mixing parsed cells with counted
  stand-ins, a whole-number column whose rounding direction decides four
  of its cells, a column that writes the shortest round-trip digits at
  both boundaries of the fixed-point window, a label column with
  published and invented spelling variants, an identifier column that
  must fold two spellings onto a partner, and one publishing whole
  numbers across all three alphabet bands. The five in
  `tests/reference/generation-branch-vectors.json`, added under review
  items P2-C3-F3 and P2-C4-C3 for branches the nine leave unexercised: an
  unrepresentable column whose three published families are packed
  together, free text whose class and alphabet counts are one packing,
  an identifier whose fold collisions no case change can build, a
  column carrying the literal decimal, leading-zero and leading-plus
  spelling styles, and a published end whose seconds field is 60, which
  the whole-second ordinal space has no place for and the endpoint route
  writes exactly. **Every one of the fourteen carries a committed mutant
  that reverts the branch it exists for and must fail**, held in one
  table whose keys are asserted equal to the case set, so a case cannot
  be added without one (review item P2-C4-C2).
  Every binary64 the file publishes is proved correctly rounded -- or
  proved exact, which is the stronger claim the transform's exact steps
  make -- by whole-number comparison against the midpoints to its two
  neighbours, and the run refuses a full-generator mutant before it
  writes a byte.
- **Golden twin and report hashes** (plan P2 acceptance criterion 6,
  method conformance items 10 and 11): `tests/test_twin_golden.py` pins
  three digests for one fixed description -- the description the
  generator is handed, the twin's bytes and the report's bytes -- built
  by the real producer from the seeded neutral table, so nothing is
  committed for it. Three rather than two, so a moved twin digest says
  for itself whether the producer or the generator moved it. Each is a
  change detector and none is an oracle: the oracle for the cells stays
  the frozen reference vectors, and the oracle for the counts stays the
  recounting from the twin's own cells. They run in the plain pytest
  run, so every cell of the matrix runs them, and a difference between
  two platforms, interpreter versions or library versions turns red
  there instead of shipping as a quietly different twin.
- **The rung window proved able to fail** (method conformance item 5).
  The two-sided acceptance bound on the nine interior ladder rungs is
  now put through four columns of a materially bent ladder, laid out by
  hand: the faithful one, which it must accept, and three it must
  refuse -- one built from the two published ends alone, one with the
  nine interior rungs each read one place along the ladder, and one with
  two interior rungs exchanged. All four hold the published minimum and
  maximum exactly and nothing outside them, so every other numeric check
  passes on all four and the window is the only thing that separates
  them. The assertion the mutants meet is the one in force, not a copy.
- The built-artifact smoke test now runs `synthtwin generate` and not
  `synthtwin profile` alone. In the same fresh venv, from the same
  installed wheel and under the same socket guard, it profiles the
  seeded neutral table, hands the description that run wrote back to the
  same command, and checks that the twin and the report are both there
  and that the twin is 240 rows by 10 columns with the published column
  names and no byte-order mark. A generation path broken only in a
  packaged wheel now turns CI red instead of shipping.

### Changed
- The offline import policy gained four reviewed extensions (plan
  P1-D10): the enumerated `pandas`, `csv` and `math` surfaces; a ban on
  calling any method on the objects `pandas` returns, because a data
  frame carries writers that reach a database or a URL on their own; and
  text-origin tracking that follows an accepted string through its own
  data methods, slices and f-strings so that ordinary text handling does
  not need a helper function per method call. The `math` enumeration
  replaced a numpy one: review round 1 showed that numpy's reductions
  made published statistics depend on the order of the rows, so the
  profiler computes them itself and numpy was withdrawn as a declared
  dependency.
- The offline import policy gained three more reviewed extensions for
  Phase 2 (plan P2-D13). `numpy` is readmitted as one name and one name
  only, `numpy.random.default_rng`; every other numpy name, and `import
  numpy` itself, stays refused. What that name RETURNS is enumerated
  too, because a library object is not covered by the enumeration that
  produced it: the generator answers to `integers` alone, and each of
  that call's five arguments must be a value this package built itself;
  the array it returns answers to no method and no attribute; and a word
  taken out of that array, by index or by iteration, is still a library
  scalar carrying `dump` and `tofile` until `int()` turns it into a
  plain whole number, which is the one operation permitted on it. `csv`
  gains `writer`, with the file handle enumerated to this run's own
  validated output target, the rows to sequences built under the
  audit's eyes, and the dialect parameter added to the callback-slot
  table in both its argument forms. Each capability has a mutation test
  that must stay red.

### Added in Phase 2: the profile contract is version 4

Phase 2 builds the generator, which reads the profile and never the
table. Five facts the profile did not carry are what a twin cannot be
built without, so `profile_version` is **4**. Nothing was removed and no
key changed shape: every version 3 key keeps its name, its type and its
meaning, and `docs/spec/profile-contract-v4.md` states all of it
normatively.

- **Three axes beside the role.** Every column now carries
  `statistical_type`, `quality_state` and `structural_role`, derived by
  a fixed rule, and a consumer dispatches on those rather than on the
  role name. The third is not derived from the role at all: it says
  whether the person named the column with `--identifier`, which is
  true even of a declared column whose cells all mean "no value" and
  which therefore ends up described as an empty column.
- **How often values repeat, on every column that publishes none.**
  `n_distinct_by_occurrences` -- a declared identifier's key since round
  8 -- is now carried by free-text columns and by columns of numbers no
  format can hold, in the identical shape. Without it, sixty notes each
  written twice and sixty notes with one written thirty-one times were
  the same description.
- **A reserved cross-column block.** One top-level `relationships` with
  eight names, every one empty, because this version preserves no
  structure between columns and a consumer should read that stated
  rather than infer it from an absence.
- **How each published label was written.** A label is published in one
  settled form -- trimmed, upper and lower case folded together -- so a
  column holding `A`, `a`, `B`, `b` published two labels and nothing
  about the four values it holds. Each published label now carries
  `variants`, the exact spellings of it, and `variants_withheld`, an
  anonymous count of the ones held back. **Every spelling is governed by
  the small-cell floor exactly as a whole label is**: below it, it is
  counted and never named, and a label the floor held back carries no
  spellings at all. This publishes something version 3 did not, and the
  summary now says so where a person deciding whether the profile may
  leave their machine will read it.
- **How the numbers were written.** Columns of counts and of measured
  numbers carry `numeric_styles`: how many cells used each of six
  spelling forms -- plain, leading zero, leading plus, decimal, and the
  two exponent cases -- under the floor, with rarer forms pooled into a
  counted remainder. It carries no value and no magnitude, only form.
  Three columns reading `0`, `0.0` and `0e0` produced byte-for-byte
  identical descriptions before it, and a reader infers a different type
  from each.

### Changed in Phase 2

- **The canonical serializer and the write transaction moved out of
  `profile.py`**, into `canonical.py` and `writing.py`, which import
  neither the table reader nor the taxonomy. Both are code the generator
  has to reach, and `profile.py` imports the reader's own table type, so
  a module importing it would inherit that reach whether or not it ever
  called it. Nothing about either changed but where it lives; both are
  re-exported under the names they had.
- **The write transaction's refusals name the files of whichever command
  is running.** The transaction is no longer the profiler's alone, and
  four of the
  messages it composes named the profiler's files in plain words: "The
  profile could not be written to ...", "... next to your table", "...
  replaced your own table", and "a profile and a summary from two
  different runs do not describe the same table". A stopped `generate`
  run would have told somebody that their profile could not be written
  -- the one file that command never writes to -- and sent them to check
  a table the command never opened. The words are now an argument, the
  two sets live in `errors.py` beside every other message, and every
  message the `profile` command produces is the same byte for byte as
  before.

### Fixed in Phase 2: the two obligations of the invented alphabets

The frozen reference vectors carry an identifier column the generator
disagreed with, and the specification supported the vectors on both
counts. The case was held as a strict expected failure while the
GENERATOR was repaired to the oracle; the vectors were never adjusted
to match the code they exist to check.

- **Fold collisions are now built rather than named.** Where a column
  publishes fewer folded identities than raw spellings, method section
  G9.3 requires the difference to be constructed: the identities that
  will be varied are drawn from the part of the domain that holds a
  letter, and each carries a case flip. The generator instead recorded
  the shortfall as a deviation. Method section G12 grants that fallback
  to columns of numbers alone, and the contract makes both distinctness
  counts exactly recountable on all three roles that invent their
  values. The cause was one record of what a column had already
  written, holding both "this spelling is taken" and "something folds
  onto this" under one mark: the partner of a fold collision is by
  definition new only in the first sense, so it was refused every time
  and no collision could ever be placed. The two senses are now
  recorded apart, the letter is asked for on the identities the
  collisions are actually taken from, and a case flip is only ever
  taken from a value of its own alphabet and numeric class, so meeting
  the folded count cannot quietly cost a different published count.
- **A column of record numbers no longer writes figures where the
  description publishes none.** Method section G9.5 step 3, which G9.6
  imports for record numbers, gives a value counted in the code
  alphabet a leading character that is not a figure, so it cannot read
  as figures alone; the generator wrote plain figures and named
  nothing at all, which is the worse of the two failures, because a
  reader of the report never learned of it. Each band now leads with a
  character that keeps its own alphabet count, and a column whose
  description records that every value is a whole number leads with a
  figure other than zero, so a value's length is its count of figures.
- **Both alphabet counts are recounted from the written twin and named
  when missed.** One made-up value covers a whole group of rows, so a
  published count of cells that falls part-way inside a group cannot
  always be met; where it cannot, the report now names the fact, the
  published number and the number the twin holds, instead of leaving
  the difference for someone to find.
- The same repairs apply to columns of free text, which invent their
  values under the same rules. On columns of numbers too large or too
  small to hold, the collision path is in place, but that role's values
  are written at one canonical width in figures alone, and figures have
  no case: where such a column publishes fewer folded identities than
  spellings and has no cells of ordinary text to carry the collision,
  the shortfall is reported rather than built.

### Corrected in Phase 2: what synthtwin is allowed to claim

Two sentences this project repeated everywhere were stronger than the
product. Both are withdrawn, on every surface at once rather than where
someone happened to notice them, and `tests/test_claim_inventory.py`
refuses to let either come back: it reads the charter, the readme, the
security document, the changelog, the packaging metadata, the two
specification documents and every module under `src/`, and it fails both
ways -- if a retired form reappears anywhere, and if a surface that has
to state the true claim stops stating it (plan P2-D11). The third entry
below records the two new `SECURITY.md` disclosures that version 4's own
new facts require.

- **The categorical record claim is withdrawn, and a qualified one
  replaces it.** The old wording -- the flat assertion that a twin holds
  nothing of yours -- appeared in the charter, in `README.md`, in the
  package docstring, in the installable package's own description, in
  the command's help and in the profiler's own summary, and it promised
  something no tool that reproduces
  published counts exactly can promise. What is true, and what the
  product says now: the generator is handed the profile and a seed and
  nothing else -- it reads no source table, is never given a path to one,
  and samples or copies no row of it. That is a claim about where the
  twin's values come from. It is not a claim that no twin row can equal a
  real row, because meeting the published counts exactly can force the
  match with nothing copied anywhere: a table of eleven rows and one
  column, whose single label all eleven rows share, publishes that label
  with the count eleven, so the twin writes it in all eleven of its rows
  and each of those rows is a row the real table has. synthtwin offers no
  formal privacy guarantee, and now says so where a person will read it
  rather than only in the plans.
- **Institutional handling covers the twin and the report too, not the
  profile alone.** The profiler's summary, `README.md`, the charter and
  `SECURITY.md` each said the profile is real-derived material and left
  the twin and the report unmentioned, which reads as permission for the
  other two. It is not: the twin reproduces published counts exactly and
  the report quotes published facts back. The profile, the twin and the
  report all carry facts computed from real data, and every surface now
  says the institution's rules reach each of them. (Phase 3 widened the
  rule again, to every file a run leaves behind; see above.)
- **`SECURITY.md` gained an entry for each of version 4's two new
  published facts**, so a reader weighing whether a profile may leave the
  machine can see the delta rather than infer it. The label-spelling
  entry states the delta at its true width: the fold the producer applies
  is a Unicode case fold after trimming, not a capitals-to-lowercase map,
  so publishing the variants publishes every difference that fold used to
  absorb -- edge spacing and capitals, and also the equivalences Unicode
  defines, such as `ß` and `SS`. The `numeric_styles` entry states that
  the fact is about form only: counts per spelling style, floor-governed,
  carrying no value, no magnitude and no spelling.

### Repaired in Phase 2 code review round 1: the counts a twin has to hit

Nothing above has been released, so these are corrections to the Phase 2
work in the same unreleased entry. They change the cells a run produces
and what a person is told about them.

- **A published count of cells is now met exactly wherever whole groups
  can meet it** (review item P2-C1-F1). One made-up value covers a whole
  group of rows, so a count like "four of these cells are figures alone"
  has to be met by choosing which GROUPS answer for it. The old rule
  offered the largest group first and stopped: on groups of two, two and
  three with a published count of four it wrote five, although putting
  the two groups of two on that count meets it to the cell. The packing
  is now exact wherever an exact one exists, on all three paths that
  invent values -- record numbers, free text and numbers no format can
  hold -- and it carries the rules one published fact places on another,
  so a cell written in accounting parentheses is never counted among the
  cells written in figures alone.
- **Every one of those counts is now RECOUNTED from the finished cells
  and named where it was missed**, under the profile's own field name.
  The old code named some misses under names it had invented, filed
  others under the wrong field, and left the sign counts of a column of
  unrepresentable numbers silent even in the report.
- **A whole number is not the same as a value written in figures**
  (P2-C1-F1). A column of `+1` and `+2` publishes that every value is a
  whole number and that NO value is written in figures or in the code
  alphabet, and the twin now holds all three facts; the old rule read
  the first as implying the second and missed the other two.
- **A run always ends** (review item P2-C1-F2). A genuine profile -- a
  column of twenty-six different one-character values outside the code
  alphabet -- used to make `generate` consume the processor without end
  and without a message, because the walk that invents values came back
  to spellings it had already written. Every walk now stops at the end
  of the family it is walking, and where a column asks for more
  different values than can be written that way the run refuses before
  anything is written, names the two facts that cannot both hold, and
  says the profile is valid.
- **The capacity a refusal quotes is the number of values that could
  actually have been written** (P2-C1-F2), not the number of strings the
  alphabet holds. The two differ by a lot: the wide alphabet has 95
  one-character members and the ordinary-text construction can write 25
  of them.
- **The leading-zero family has no ceiling again** (review item
  P2-C1-F5). Owner decision 8 chose that family precisely because `0`,
  `00`, `000` supply as many spellings of one value as a profile can ask
  for; the implementation stopped at 4,096 and then repeated a spelling.
  A column of 4,098 differently written zeros now reproduces every one
  of them. A related diagnostic fault is gone with it: a column of
  nothing but zeros no longer builds value strata holding no cell, so
  the report no longer names an endpoint the twin never wrote.
- **Temporal facts the loader accepts are preserved by the generator**
  (review item P2-C1-F6). The contract permitted a column of dates AND
  times whose finest detail is a whole date, which no cell can hold and
  the profiler cannot produce; it is refused where it is decided. A
  published instant now carries calendar and clock RANGES, not only a
  shape, so `2024-99-99` is refused instead of being normalized into a
  real date somewhere else; a UTC offset carries its range the same way;
  and an offset is accepted only on a column that publishes a time of
  day for it to move. A description whose own recorded detail and clock
  cannot show its own first or last value is refused in the same place
  and for the same reason (see round 3 below); every description that
  loads has both of those values written back exactly.

- **Every approximated fact now has a stated two-sided bound, is
  measured on the twin, and is printed in the report beside the value
  the description publishes** (review item P2-C1-F4). The contract marks
  a handful of facts APPROXIMATED -- a column's average, spread and
  shape, the nine steps between its smallest and largest value, the same
  nine steps for a column of dates, how many different dates it holds,
  and the length and word summaries of free text -- and each of them
  owes a bound that both sides are checked against. `mean`, `std` and
  `skew` had no bound at all: the method left that job to a test
  battery, which is not something an independent implementation can
  conform to. Every one of them is now fixed in the method
  specification (G12.1 to G12.8), derived from the rule that builds the
  cells rather than measured on an output, and finite on both sides --
  including the skewness, whose bound falls back to the range every
  sample of its size lies in where its own derivation reaches zero.
- **The generator measures each of them on the finished cells** and
  hands back the published value, the achieved value, both ends of the
  bound and the answer, per column and for the run. A fact that lands
  outside its bound is ALSO named as a fact the twin could not meet, so
  the two lists a reader is given cannot disagree.
- **The report gained the section that says how close they came.** It
  used to say that measuring how close the twin came was a later
  version's work, which left a user told that the report distinguishes
  exact facts from approximate ones while it printed nothing about the
  approximate ones at all.
- **Each of those bounds is proved able to fail**, by putting a
  deliberately broken column through the same shipped measurement: one
  that collapsed the interior rungs onto the two ends, one that shrank
  the spread, one that mirrored the shape, one that wrote every date the
  same, one that wrote a date per row where the published range holds
  twelve days, one that mislaid a character, one that dropped the
  spaces, and one that invented a spelling.
- **The disposition matrix now has a completeness assertion**, promised
  by the plan and previously absent: every key the producer emits, for
  every role and at the top level, is looked up in the contract's own
  section 9 as it is written, and a key nobody disposed fails the suite.
  It found two: `length` and `words`, the two containers a free-text
  column publishes, which the matrix named only through their leaves.
- **Every sentence a profile publishes is now written from an
  enumerated grammar, and the finished description is checked before it
  is written** (review item P2-C1-F3, plan P2-D2). A description carries
  two kinds of text: a value the publication rules allow -- a column's
  name, a label many rows share, a date -- and a sentence synthtwin
  wrote about the column. Both are text at a key the description has
  always had, so a check that reads the key and the type cannot tell
  them apart, and a sentence that one day spelled a rare value into
  itself would have been published with every test still green. Notes,
  evidence, remarks and the header verdict are therefore no longer
  free text: each is built by name from one of an enumerated set of
  forms, filled only with counts and words of this package's own
  vocabulary, so a sentence about a value of the table cannot be built
  at all. The finished description -- including the notes lifted to the
  top level after each column block is complete, which an earlier check
  over the columns alone could never have seen -- is then walked to its
  last leaf: every sentence is written again from the form it carries
  and refused unless the words come out identical, every value stands
  at a place the rules authorize and clears the small-cell floor, and
  anything else at all stops the run before a byte is written. The
  refusal names the PLACE and never the text, because the text is what
  it is refusing to publish. Nothing a person sees changed: every
  sentence is the same sentence, byte for byte.
- **Every surface now says what the twin actually carries, and what is
  actually built** (review item P2-C1-F7, plan P2-D11). The record
  claim had been repaired everywhere and the claim inventory was green
  while four other material claims on the same pages were false. The
  package docstring listed fidelity between columns among the things
  the twin keeps, and the charter promised a relationship summary among
  the outputs, in a phase that generates every column on its own and
  publishes eight EMPTY relationship slots -- measured rather than
  argued: a table of two
  identical columns, every real row holding the same value twice, gave
  a twin in which zero rows of two hundred did. The front page said
  Phase 1, tagged the installed `generate` command as planned, called
  the profile/generator separation future architecture, and denied that
  numpy was a dependency at all; the security document's allowlist
  paragraph still counted a single function of a single third-party
  library, after numpy had returned with its own enumerated scanner
  surface. What every surface says now, in the same
  words: the twin reproduces the published facts of each column ON ITS
  OWN, carries no cross-column structure at all -- no correlation, no
  formula between two columns, no shared pattern of empty cells, no
  ordering between two event dates -- treats rows as independent while
  the grain is undescribed, so the twin of a repeated-measures table
  misdescribes the subject-level truth, and gains cross-column
  structure only in a later phase. The claim inventory was widened to
  hold all of it: relationship fidelity, phase status, command
  availability and dependency count each have a banned list of the
  false forms and a required list of the true marks, with the front
  page's built and planned sections pinned by name, and every ban
  carries a floor test proving it still catches the sentence this
  repository used to carry.

### Repaired in Phase 2 code review round 2: allocation and numeric form

Round 2 read round 1's repairs and refused four of them on the surface
where the twin decides which cells answer for which published count.
These change the cells a run produces and what a person is told about
them.

- **No ceiling counts the SHAPE of a description any more** (review item
  P2-C2-F1). Round 1's repair bounded the exact packing with two
  constants, and a column of record numbers the profiler actually emits
  reached one of them: 132 different group sizes made the depth
  expression 402 against a ceiling of 400, so the packing an exact one
  exists for was never looked for and three published counts came out
  wrong. Both constants are gone. The walk now prunes with two
  whole-number tests -- can the sizes still undecided reach a total this
  count accepts, and can every count still owed be made at all from what
  is unplaced -- answers the smallest counts first so the largest
  absorbs what is left, and never enters the same state twice. This
  repair left one ceiling standing, on undone WORK rather than on the
  size of a description, with the headroom measured rather than
  asserted (96 units, against 200,000). **Round 3 found a description
  that reaches it and it too is now withdrawn** -- see the round-3
  entry below, which is the current state of this surface.
- **Two coupled families are decided in ONE packing** (P2-C2-F1). A
  piece of free text answers for a numeric class and an alphabet at the
  same time, and a number too large to hold answers for a magnitude
  class and a sign; deciding each pair one after the other threw away
  answers that exist. A five-row column of free text lost an alphabet
  count that way, and forty shapes of a wide battery lost a sign count.
  All of them now come out exactly.
- **A published numeric form that CAN be written is written** (review
  item P2-C2-F2). A column holding eleven fractions beside forty whole
  numbers publishes forty cells written plainly, and the twin wrote none
  of them: the canonical spelling of a whole value on such a column
  carries `.0`, which reads back as the decimal form. Both misses were
  named, which is not the same as writing the form. The twin now writes
  a whole value with no point where the published map asks for one, puts
  whole values on as many strata as the map needs -- never at the cost
  of the counts of negative or zero values, or of the count of different
  values -- and looks ahead so a form is not spent on a cell that could
  not have worn it. A form with nowhere to go is still named.
- **The spellings that reach a published count of different values are
  available inside every form but one** (review item P2-C2-F3). Owner
  decision 8's leading-zero family was reached for only where the form
  was itself `leading_zero`, so a column reproducing a decimal or an
  exponent form held one spelling of a value and no way to make a
  second: an input of twelve copies each of three decimal spellings of
  zero came back with one. Zeros written after the sign leave the form
  and the value exactly where they were for five of the six forms, and
  the twin now reaches all three. `plain` is the one form with no such
  family, and the count it cannot reach is named and bounded rather than
  passed over.
- **Both counts of different values on a column of numbers now carry a
  measured range** (review item P2-C2-F4). The contract and the method
  both send them to a two-sided range where the permitted spellings
  cannot supply the published count, and neither end was measured
  anywhere: a run on a column holding nought through four named the
  shortfall and printed no range, while the report's closing sentence
  said every approximate fact had been measured. Both are now measured
  on every column of numbers against the supply the twin's own cells
  carry, both ends are printed, and the test inventory that says which
  facts are approximate is read out of the contract's matrix rather than
  transcribed, so a row whose disposition is conditional cannot be left
  out of it again.
- **A value that comes down onto another one through edge spacing is
  now BUILT, not named** (review item P2-C2-F6). Two spellings are the
  same identity once the ends are trimmed and the case is turned over,
  and only the second half of that was ever used to build one. So a
  value one character wide holding a single letter offered exactly one
  such partner, and a value written in figures offered none: a column
  holding `a`, ` a`, `a ` and ` a ` -- four spellings, one identity, one
  to three characters wide, every one of those a fact a person can
  recount on the twin -- was written as four identities and the miss was
  named. Naming it was honest and wrong, because the real column is
  itself the proof that all of those facts hold together, and owner
  decision 6 permits a lost count only where they cannot. A partner may
  now differ from the value it comes down onto in case, in edge spacing,
  or in both. Nothing else a person recounts moves when it does: the two
  alphabet counts and the whole-number reading are taken after trimming,
  words are counted between spaces, and the one fact spacing does move
  -- the length -- is held inside the published range, with the two
  published ends held to their own single length. The twin writer leaves
  the spacing alone and the reader hands it back, so a twin describing
  itself again finds every published count where it was.
- **The independent oracle no longer carries a rule the method withdrew**
  (review item P2-C2-F7). The vector tool chose the figures alphabet
  whenever a declared record column published every value as a whole
  number, and consulted the published alphabet counts only when it did
  not. That is the rule round 1 withdrew: a column of `+1` and `+2`
  publishes every value whole with BOTH alphabet counts at nought,
  because `+` is in neither alphabet. No frozen vector reached the
  branch, so rebuilding the file byte for byte never tested it, and an
  oracle carrying a withdrawn rule can reject a conforming
  implementation as easily as it can certify a wrong one. The tool's own
  owner reconciled it from the method specification alone: the bands
  come from the two published counts and from nothing else, and what
  the whole-number fact decides is what each band WRITES -- digits with
  a non-zero leading one in the figures, `<digits>e0` in the code
  alphabet, `<digits>.` outside it. A ninth frozen case,
  `identifier_whole_numbers`, reaches all three bands, so the branch is
  covered rather than merely corrected; the other eight cases rebuild
  byte for byte unchanged. The tool now also recounts every one of that
  role's exactly-observable facts from the cells it just built and
  refuses its own answer where one is missed, and it states no expected
  cells at all for the two corners it freezes no case for.
- **A false limit on how far the made-up-value walk may step is retired
  from the method specification** (review item P2-C2-F8). Beside its
  true proof that the walk stops at a family's own size, the document
  claimed the walk visits at most one index more than the number of
  values the column has already written. It does not, and a second
  reader building from that sentence would refuse a family the shipped
  walk draws from: a candidate is also stepped past when it reads back
  as the wrong kind of value, when it is one of the spellings that mean
  "no value", and when it reads as a date -- none of which consults what
  the column has written. Asked for the first value of an empty column
  of numbers too large to hold, the walk steps past one candidate and
  takes the next; asked for an eight-figure number, it steps past
  thirty-one in a row that read as dates. All five reasons a candidate
  can be stepped past are now listed, three worked cases are printed
  beside them, and the limit that is stated is the true one. The pass
  that asks for a value with a case to turn over now hands back "no
  more" when it gives up, so the walk is put back where that pass began
  -- it used to carry on instead, and every candidate it had stepped
  over was then spent for good.

### Repaired in Phase 2 code review round 4: the fourth lowering, and the registry that ends the pattern

- **The last exception to the two ends of a column of dates is refused,
  in both directions** (review item P2-C4-F1). The repair before this
  one refused the two pairs it had been given and left a third standing:
  a column whose values are published on the shared clock, whose first
  or last value sits within one offset's distance of the ends of the
  calendar this format can spell, so that moving that value onto the
  clock its own offset names asks for a cell no reader reads back as a
  date at all. The method called that the calendar's own end rather than
  an exception, the twin wrote the cell and named the end in the report,
  a test required that outcome, and the new wording guard listed the
  passage as a decided one -- so the guard was green about the sentence
  it existed to catch. The loader holds the value, its offset and the
  clock, so the contract's D10 now settles the pair where it is decided,
  at both ends of the calendar, and the method and the generator carry
  no case for it. The last second of a leap minute is unaffected: it is
  still written back unchanged on the ordinary clock.
- **The read-back check on the two ends stays, as a defect detector**,
  and a test proves it can still fail: the writing rule is reverted to
  the arithmetic route that produced the round-1 defect, and the run has
  to catch its own changed end, name it under the contract's own field
  name and print both values. No description a loader accepts can reach
  it, so the report line it writes is a fault notice rather than an
  outcome any description asked for, and it says so in those words.
- **Every published fact now has a machine-checked bar**
  (`tests/dispositions.py`, `tests/test_p2c4f1_disposition_registry.py`).
  Four separate repairs closed a review item by writing a quieter
  sentence into a normative document instead of meeting the bar the
  sentence had, and each was found only by the next adversarial review.
  The registry states the disposition the ratified plan gives every fact
  of every role, together with the plan's own words for it, and a test
  reads the plan, the contract and the method and fails when any of the
  three states a weaker outcome for a fact, omits a fact, or names one
  the plan does not. The plan is read, not trusted: softening P2-D6
  itself turns the same test red. A lesser outcome may be authorized
  only by quoting the plan's own sentence for it, so lowering a bar now
  means amending the ratified plan in the open. The proof that the guard
  reaches is part of it: each of the four lowerings is written back into
  a scratch copy of the document it belonged to, at three places, and
  every one has to come back red, as do four lowerings of obligations
  nobody has ever touched.
- **A lowering an adversarial review has already named can be carried,
  by its item number and no other way.** The registry's open list ties
  each remaining lesser statement to the review item that requires its
  removal, and a test requires that number to appear in the newest
  review record -- so an implementer cannot open one, and every entry
  goes stale the moment a new record lands unless somebody re-argues it.
- **That guard read prose for known wording, and code review round 5
  defeated it six ways out of eight, so the mechanism was replaced**
  (review item P2-C5-F1). A phrase list loses to rewording by
  construction: the six that survived were a lowering said in other
  words, a lowering stood beyond the attribution distance, a lowering
  captured by a nearer field name, a field name whose class depends on
  the role, an authorization added to the registry and propped up with a
  genuine but unrelated plan sentence, and an entry added to the escape
  hatch citing an item the newest record merely mentioned. Four
  comparisons carry the guarantee now, and not one of them asks what a
  sentence means. **The plan and both specifications are sealed passage
  by passage** (`tests/disposition_seal.py`, written by
  `tools/dispositions/seal.py`): a passage that is not in the seal is
  refused whatever it says, so writing or rewording one turns the suite
  red before anybody argues about it, and re-sealing is a separate,
  counted, self-describing edit -- one line per passage -- to a file
  that states what signing it asserts. **The registry's own judgment is
  sealed the same way**, in four surfaces, so the two attacks that
  edited it now need a countersignature. **An authorization declares the
  fact it belongs to, the plan region that has to carry its words, and
  the lesser class it grants**, and the registry's class may never be
  weaker than any class the plan's own region writes beside that name --
  so a quoted sentence no longer bypasses the parse of the plan.
  **The escape hatch is bound four ways**: the item must belong to the
  newest record's own round, stand as one of its item headings and be
  named in its verdict; the prose it excuses must already be sealed; the
  lowering must still be there; and the list must be empty by the time a
  review stops rejecting the phase. All eight of round 5's mutations are
  run against the new design in scratch copies, in the suite itself, and
  each has to go red.
- **And the dispositions became executable, so a quieter sentence buys
  nothing on its own.** A producer battery runs the shipped generator
  across every role and requires each line of its report to be one the
  ratified plan allows -- an approximated or report-only fact, an exact
  fact the plan authorizes a lesser outcome for, an exact fact a
  reviewer has left open, or one of two lines that carry the published
  value on both sides and disclose something else. Softening a document
  does not move that assertion by one character; weakening it is a code
  change a reviewer reads in the diff.
- **What this does not do, stated because the previous guard's claim to
  be binding is exactly what failed.** No check can decide whether new
  English prose lowers an obligation. Somebody who edits a document AND
  re-seals passes everything; what the design guarantees is that the
  edit cannot be silent -- it fails a check until a separate, explicit,
  counted signature is added beside it. Deleting a whole passage that
  RAISES a bar is caught only where that sentence is one of the
  anchors listed in `tests/dispositions.py`, and the anchor list is
  judgment rather than proof.
- **Two descriptions the ratified plan says to REFUSE were being
  generated instead, and are refused now** (review item P2-C5-F4). Plan
  P2-D6 reserves a refusal for a description no rule can satisfy, and
  the report line for a fact a rule CAN meet. A declared column of
  one-character record numbers published as whole numbers with fewer
  than all of them written in figures alone, and a column of free text
  publishing a word count its own published length cannot hold, are
  both descriptions no table can hold -- proved from the published
  numbers themselves, since one character that reads as a whole number
  IS a figure and a value of `L` characters holds at most `(L + 1) // 2`
  words. Both were being built anyway, with the exact fact recounted as
  missed and named in the report: the person received a twin the plan
  says the run should have stopped for, and nothing told them the
  description was one no table can produce. The generation-feasibility
  stage now refuses both before a cell is built, in the words the plan
  fixes -- the profile is VALID, the two facts that cannot both hold are
  named, and the remediation is an edit to the description file, which
  is what the person is holding, rather than anything that needs the
  table back. Two further shapes of the same proof are refused with
  them: a shortest published length of one character with nothing
  written in figures alone, and a word floor the shortest published
  length cannot reach. The contract's section-9 head no longer says a
  document whose facts cannot all hold is met as far as it can be; the
  method's G12 list carries four refusals instead of two; and a battery
  of eleven producer descriptions at three seeds still produces
  thirty-three twins, so nothing a real table describes was refused.
- **What that repair leaves open, said plainly** (review item
  P2-C5-F4). `all_whole_numbers` on a declared identifier is still
  missed on two shapes a real table DOES produce, and the run names it
  each time: a two-character value in the code alphabet, whose only
  whole-number spellings begin with a sign the artifact rules keep a
  made-up value from starting with, and a published length end pinned
  onto a group whose band cannot spell a whole number at that one
  length -- which the source's own values prove another pairing would
  have held. The first needs an owner decision, the second needs the
  length ends and the bands packed together as free text already does,
  and neither is a refusal: the description is one a rule could meet.
  Both are recorded in the registry's open list under this item rather
  than written as a quieter sentence anywhere.
- **The shape of a column of free text is decided WITH its published
  counts and no longer before them** (review item P2-C4-F2). The method
  gave the two published length ends and the two published word ends to
  the description's first two values, settled every other length by the
  walk that approaches the published average, and only then asked the
  grid of classes and alphabets for a packing inside that shape. A
  description the producer emits can have an exact answer that this
  shape forbids -- a twelve-cell column whose five-row value has to be
  counted in the code alphabet, while the shape gives that value the
  longest length and the largest word count, which no code-alphabet
  cell can carry. The ends, the lengths, the classes and the alphabets
  are now one allocation: the shapes are offered in a fixed order whose
  first member is the old rule, and the first whose grid meets every
  published count exactly is taken, so a description the old rule
  already answered is answered byte for byte as before and the frozen
  reference vectors are unmoved. Where no shape at the walk's own
  lengths answers, a value carrying no end may be written at any
  published length, because an exact count outranks an approximated
  average.
- **A number two characters long can be written in the code alphabet.**
  The only numeric shape that alphabet had was an exponent, which needs
  three characters, so a real column holding values like `-3` beside
  ordinary words lost both alphabet counts. A leading minus sign is a
  character the figures do not hold and what follows it still reads as
  a number, so that family now begins at two characters.
- **The four ends of a column of free text are recounted from the
  finished cells.** The shortest and longest value and the fewest and
  most words in one value are EXACT-OBSERVABLE, were pinned onto values
  by construction, and were measured nowhere -- so when a value pinned
  to the largest published word count was given a class that writes one
  unbroken run of characters, it wrote one word and no line of the
  report said so. The rule about several words is now stated over every
  family rather than over the code alphabet alone, and the four ends are
  recounted beside the alphabet and class counts, so a miss no rule
  foresees is named with both values.
- **How many cells hold each different number is the twin's own choice,
  and a published count now outranks it** (review item P2-C4-F3). Owner
  decision 10 says the twin writes every numeric spelling style in its
  published count, because the form is what a reader's type inference
  reads. A column of eleven `1.5`, twenty `100` and twenty `200.5`
  publishes twenty cells written plainly and thirty-one with a point;
  its own values prove that map; and the twin wrote twelve and
  thirty-nine on every seed and named both counts as missed. The reason
  was that the twin divides a numeric column into one stratum per
  different value and had been splitting the cells EVENLY between them,
  which gave the one stratum that could hold a whole number seventeen of
  the fifty-one cells. Nothing in a numeric block publishes those sizes
  -- there is no multiplicity map on a column of numbers -- so the even
  split is a default, while the style map is a published exact fact.
  The default now gives way: cells move into the strata that can hold a
  whole number, always within one sign band so the counts of negative
  and zero values are untouched, never emptying a stratum so the count
  of different values is untouched, and only as far as the published
  counts need. The rung window widens by exactly what that spends,
  because the window is derived from the widest stratum and is measured
  on every run.
- **Three more places where a published form went unwritten**, each
  found by generating a battery of descriptions through the real
  profiler rather than by reading the rule. A sign band left with one
  stratum -- the published `min` or `max`, carrying a point -- could
  carry no plainly-written cell at all, and every cell of that band was
  stuck on it, so a band may now take one stratum from the other side.
  A stratum whose nearest whole number was already another stratum's,
  which is what a FLAT ladder produces when a column's commonest value
  is its own published minimum, gave up rather than stepping to the next
  whole number inside its own share of the ladder. And where the counts
  could not all be placed, cells that could have been written plainly
  were spent on forms any cell could have worn, making the shortfall
  larger than the column's own values force.
- **The held-back remainder yields before a count the description
  names.** A form used by too few rows to name is pooled and written
  plainly, so it competes for the same cells as a form the description
  does name. It now loses that competition rather than sharing the
  shortfall, and the report says which part of a plain count the
  description names and which part it held back, because the total
  appears nowhere in the profile and a reader must be able to check the
  report against it.
- **What is left, and it is not nothing.** Where a column's published
  `min` or `max` carries a point, one cell must hold it and cannot be
  written plainly, so a pooled remainder can come out one or two cells
  short; and where a published ladder crowds several different values
  inside one unit, those strata have no whole number of their own and
  their cells cannot be written plainly at all. Both are recounted and
  named with both values, both are stated in the method, and the second
  can still cost a count the description names. What the repair does
  close in every case is the other half: the cells written plainly are
  exactly the cells whose value can be, so the shortfall is the size of
  the values and never of the placement. The registry carries this as
  the open item it belongs to rather than as a quieter sentence.
- **The fold-collision family says which member a slot takes, and not
  only what order the members stand in** (review item P2-C4-F4). A
  column of four spellings written in figures, folding onto one
  identity, has to build its three partners out of edge spacing alone.
  The method fixed the order those partners stand in and left the choice
  between them to be worked out from it, and two implementations worked
  it out differently: one wrote the one-space partners before any
  two-space one, the other stepped over a one-space partner nothing had
  written. Both columns satisfied every published fact, so nothing was
  lost except the property the frozen vectors exist to provide -- that
  an independent implementer working from the text alone writes the same
  bytes. G9.3 step 2 now states the rule: every slot walks its parent's
  family from that family's own start and takes the first member the
  column has not written whose length its own slot admits; a member one
  slot's window turns down is not spent; and the count of partners a
  parent has already supplied decides which parent comes next, never
  which member is taken. This ADDS a requirement and takes none away.
  The vectors were not adjusted to either implementation -- they already
  wrote what the stated rule produces -- and the comparison that had
  been carried as an expected failure now binds like the other thirteen.
- **Every one of the frozen cases now carries the mutant that reverts
  its own branch** (review item P2-C4-C2). Four of them did and nine did
  not, which is the same gap in a quieter form: a case whose own rule can
  be withdrawn while every committed byte stays put holds nothing up.
  The mutants are one table whose keys are asserted equal to the whole
  case set, so a case cannot be added without one; each either moves its
  case's cells or stops the oracle from building it; and each builds its
  case unmutated first, so none can pass by refusing for a reason of its
  own.
- **The leap-second end has a frozen vector rather than only an
  argument** (review item P2-C4-C3). The obligation had been lowered
  twice and argued over across three rounds while not one committed case
  carried a seconds field of 60 -- so an implementation that sent the two
  ends back through the whole-second ordinal space left every frozen byte
  where it was. The fourteenth case is twelve cells on the local clock
  published from `23:00:00` to `23:59:60`, its two ends written from the
  endpoint's own fields, and its committed mutant is the ordinal route
  put back. The pair no cell can show on the shared clock stays a loader
  refusal and not a vector case, because a description no loader accepts
  has no twin bytes to freeze.
- **The branch fixture's provenance sentence states its generator's
  imports literally** (review item P2-C4-C4). The registered generator
  there is the second entry point, which imports `os`, `runpy` and `sys`
  and executes the oracle beside it by one fixed sibling path; the
  narrower seven-module list belongs to that oracle. The manifest now
  says both, so a reviewer reading the "imports only" line as the
  complete inventory is reading a true one.

### Repaired in Phase 2 code review round 3: the two ends of a column of dates

- **The first and last value of a column of dates are exact on every
  description that loads, with no exception left anywhere** (review item
  P2-C3-F2). The repair before this one restored that rule where it had
  been lowered -- the contract's disposition row and the method's own
  construction -- and wrote the exception back into the paragraph
  after it: a description publishing an end no cell of its own recorded
  detail can show would have that end met as far as it could be,
  recounted and named in the report. The generator did exactly that,
  declining to write a published sixtieth second whenever the column's
  values were published on the shared clock, and the strict loader
  accepted such a description -- so a document this repository itself
  let through came back with its last value moved to the following
  minute, beside a row of the contract that says there is no exception.
  There are two descriptions of that kind, the producer writes neither,
  and both are now REFUSED where they are decided, by a new contract
  rule (D10), exactly as the whole-date-beside-date-and-time pair is
  refused. The generator has no case that declines: both ends are
  written from the published end's own fields on either clock, so the
  last second of a leap minute is carried by every column that can show
  one.
- **The two ends of a column's ladder of dates are that column's own
  two ends** (D11, found beside the item above). Nothing tied
  `date_percentiles.min` to `earliest` although the contract called them
  the same two instants, and the generator pins its first cell to
  `earliest` while placing the rest inside the ladder -- so a ladder
  beginning earlier than `earliest` produced a twin holding instants
  before its own published first value, and the report said nothing at
  all about it. The pair is now tied, which also makes the refusal above
  cover all four texts.
- **The guard against this class of drift now reads every passage of
  both specifications**, not one cell of one table. Every passage that
  speaks of an end being met with something other than what was
  published has to be one the test file decides on by name and with a
  reason, and the test proves it by adding exceptions -- including the
  two that were really written -- at three places in each document and
  requiring every one of them to be caught. Beside it, a battery walks
  every shape of temporal column and every end a reader can publish, and
  allows exactly two outcomes: refused, or described again with the same
  two instants.
- **A column of numbers no format can hold is packed over the counts it
  actually publishes, and over nothing else** (review item P2-C3-F1).
  Such a column publishes three separate divisions of the same cells --
  what the notation reads as, whether the value is a whole number, and
  what sign it settles -- and publishes nothing about how those
  divisions cross. The twin used to pick one crossing itself, sending
  as many out-of-range cells to "whole" as the whole count allowed, and
  then look for a packing of that. On a six-row table of two whole
  numbers written negatively, three cells written inside accounting
  parentheses and one fraction far too small to hold, that choice has
  no answer while the other choice of the very same published counts
  has one, so the twin came out with one numeric cell against two, no
  fraction against one, two negative cells against three and three more
  counts wrong -- all named in the report, and all avoidable. The
  packing now takes the three published divisions as three sides of one
  question and answers them together, so a crossing the description
  never fixed is never assumed.
- **Nothing counts the packing walk's work and stops it** (P2-C3-F1).
  The repair before this one left one ceiling standing -- 200,000 units
  of undone work, after which the twin decided the coupled counts one
  after another instead -- on the measured belief that no description a
  real table produced could reach it. One does: a 2,710-row column of
  numbers too large to hold, with 38 different repeat counts, needed
  more than five million units of that work before the walk it stopped
  would have answered. A ceiling a genuine description reaches is not a
  bound on cost, it is a published count traded away, so it is gone.
  What ends the walk is what always did: it never enters the same state
  twice and there are finitely many. The cost of that is stated rather
  than hidden -- this kind of question has no known quick answer, so a
  valid document nobody produced could take a long time -- and it is
  the same trade this project already made when it refused to cap the
  size of a description. Both repairs together answer that 2,710-row
  column in a fifth of a second, where the ceiling used to stop it.

### Repaired in adversarial review rounds 6 and 7

Nothing above has been released, so these are corrections to the Phase 1
work in the same unreleased entry rather than to any published version.
They are recorded because they change the profile a run produces and
what a person is told about it.

- **Record numbers are declared, never inferred.** Three rules that read
  a column's values and concluded "record numbers" are withdrawn: a
  column of measurements can be shaped exactly like a column of codes,
  and when the guess was wrong it destroyed a distribution the twin
  exists to reproduce. `--identifier` is now the only route to that
  reading, it beats every other rule, and it accepts any named column
  whatever that column holds. What is left of the old rules is a
  sentence: a column whose values almost never repeat is told so, and
  pointed at the option.
- **One taxonomy policy, and the code and the plan state the same
  thresholds.** A single line -- 99% of a column's present values, tested
  as a count so that no rounded division decides a role -- governs both
  the numeric roles and the date role; a second line at half the values
  is deleted, having published a mean over sixty numbers while dropping
  forty notes out of the distribution. A column below that line
  continues through the remaining rules rather than being sent straight
  to free text. The most different values a set of categories may hold
  is a tenth of the **table's rows**, capped at 1,000 and never below 2;
  measuring that share over present values instead punished a sparse
  column for being sparse. The earlier average-repetition rule and the
  separate twelve-value cap on mostly numeric columns are gone.
- **`--keep-value` and `--missing-value`.** A value your table means as
  real data even though the rules read it as "no value", and the
  reverse. A declared value that reads as a number is compared as a
  number -- as the exact number its spelling denotes, not as the binary64
  value that number rounds to, so two distinct integers can no longer
  collapse onto one declaration and remove cells nobody named. Anything
  else is compared by spelling after trimming and case folding. Naming
  one value both ways is refused rather than resolved by a precedence
  nobody can see.
- **A declaration is recorded as a count, never as a spelling.** The
  settings block carries how many values were named each way and the
  rule that matched them. It used to carry the spellings themselves,
  which republished a value out of every column at once -- including
  columns that publish nothing at all, and labels held back for being
  shared by too few rows.
- **A column that publishes no values publishes none anywhere in its
  block.** The rule is applied once, to the whole block, instead of per
  field: a declared identifier whose cells all read as "no value" used
  to reach the empty-column reading and publish the person's own
  spelling hundreds of times while the same run's summary promised the
  opposite.
- **The write transaction survives any failure the run can observe.**
  Both files are written under working names of synthtwin's own making
  and only then renamed into place. When the run raises -- with any
  exception, not only the ones this code composed -- each output name
  holds what it held before, or the person is told by name every file
  that is on disk and what each one holds, checked by looking rather
  than assumed from what was attempted. A path refusal on the second
  working file used to escape the whole transaction and leave a complete
  real-derived description in a hidden neighbor after a message that
  discussed only the path.
- **`profile_version` is 2**, because the settings block changed shape:
  where it held a list of declared spellings it now holds a record of
  how many were declared. The version exists so that a change of this
  kind is explicit rather than something a consumer of the file has to
  detect, so it moved with the change rather than after it.
- **The first row is taken by convention when nothing settles it, and
  said so.** No rule can tell a header row from a first record in a file
  where nothing distinguishes them, so synthtwin follows the CSV
  convention, records in the profile that the names were taken by
  convention, states it in plain words near the top of the summary, and
  offers `--first-row data` to take it back with every record kept. A
  file that shows its first row is a record stops and asks instead.
- **The numeric reference vectors are proved, not merely regenerated.**
  Every number the reference document publishes is re-derived from the
  exact value it stands for and its two neighboring float64 values. Four
  things stop the run instead of being certified: a number with no exact
  value recorded for it; an exact value that no published number spent;
  an integer sitting under a `float64` key where a binary64 value
  belongs, which JSON writes identically and an earlier proof walked
  straight past; and a whole number in a place the document did not say
  in advance that it publishes one.

### Repaired in adversarial review round 8

Still the same unreleased entry, and for the same reason: nothing above
has been released. Three of the four change what a run produces or what
a person is told about it; the fourth changes what the numeric
reference document's proof is allowed to certify.

- **A value you asked to keep is kept, on the numeric stand-in path
  too.** The ordinary declaration path already compared the exact
  number a spelling denotes. The stand-in path did not: it identified,
  counted, and removed cells through the binary64 value each number
  rounds to, so a neighbouring value that rounds onto `-999` was
  treated as `-999` however it was declared. A table of ordinary counts
  with fifteen copies of such a neighbour, that neighbour named with
  `--keep-value`, had those fifteen values deleted from the described
  population and its published minimum moved, with the summary
  reporting them as absent. The exact value is now carried through
  candidate identity, the occurrence count, the population the outlier
  test is measured against, and the removal, so no later rule may merge
  two numbers the declaration path had told apart.
- **The write transaction is one function with one handler.** The
  renaming step used to be a function of its own with a handler of its
  own, so the call between them ran unguarded, and several of the
  names the inner handler read were bound inside the block it guarded
  -- a stop at one of those lines raised UnboundLocalError out of the
  cleanup and cost the person both the account of the files and the
  reason the run stopped. Everything the handler needs is now bound
  before it opens, which is the one place it can be done, because
  nothing of synthtwin's making is on disk yet; each working name is
  recorded before it is reached for, since the file appears a moment
  before the call that makes it returns; and the type of an exception
  is no longer read as proof that a cleanup has run, so an unexpected
  refusal from a rename no longer leaves with two data-bearing working
  files behind it. Failures injected one at a time, at every bytecode
  boundary of every frame the transaction executes, across four
  scenarios, report no case where a surviving working file goes unnamed
  or a person's failure is replaced. Two residuals are stated in the
  plan rather than claimed closed: a second stop arriving during the
  cleanup costs the report, and one statement boundary after the last
  rename is described in worse words than the facts deserve.
- **Every number the reference document publishes is proved, at any
  depth and in every container its writer can use.** The proof walked
  dictionaries and lists, and Python writes tuples as JSON arrays as
  well, so a tuple-valued field could reach the file with nothing proved
  about it while the tool reported that every published number had been
  proved.
  The walk now covers the containers the writer accepts, and a mutation
  that hides numbers in tuples has to fail the proof before anything is
  written.
- **A declared identifier column records how often its values repeat,
  and `profile_version` is 3.** Two tables alike in every published
  count but different in their repetition pattern -- three codes over
  six rows, four/one/one against two/two/two -- produced identical
  profiles and identical summaries, so a twin built from the profile
  alone had to invent one of the two patterns and any grouped analysis
  told them apart at once. The block now carries an anonymous count
  multiset -- `n_distinct_by_occurrences`, keyed on a number of rows
  and holding how many different values cover that many: how often
  things repeat, never which things, no spelling and no length. The
  version moves with the shape, as it did at round 7.

### Repaired after the first hosted run of the Phase 1 suite

Four checks passed on the machine they were written on and could not
pass anywhere else -- and one of them, on Windows, passed by asserting
nothing whatever. Every one is a defect in the checking, not in the
product: the hosted matrix is the first place the declared floor
(Python 3.10) and Windows were ever run, and it caught them at once.
No product code changed for any of them, and on Windows the two rules
in question turned out to be STRICTER than the ones the tests had been
written against.

- **Two scanner mutations were written in Python 3.12 syntax and the
  declared floor is 3.10.** `def name[T](...)` and `type X = ...` do
  not parse before 3.12, so on 3.10 and 3.11 the probe module was not
  Python and the scanner never reached the rule the two tests pin. The
  scanner FAILS CLOSED -- a file it cannot parse comes back as one
  violation of its own, so the module is refused rather than passed --
  and that is now what those versions assert, while 3.12 and above
  still assert the specific message. The choice is made from
  `sys.version_info` and the choice itself is checked against `ast`, so
  the two can never drift apart. A separate test pins the fail-closed
  behaviour on every supported version with source no Python parses,
  and a companion pins the same rule for bytes that are not UTF-8, so
  neither route can become a silent pass.
- **A test built a folder whose name carried a terminal escape
  sequence, which Windows filenames cannot hold.** The property is
  real -- a path or value carrying display controls must be shown,
  never obeyed -- and it is kept on both sides. Where a filesystem
  allows such a name the whole route still runs, from the folder on
  disk through the command to the error stream. Where it does not, the
  control arrives as what it really is, text, through the same caution
  sentence and the same emitter; that half runs on every platform,
  Windows included, whose terminals obey these sequences too.
- **Three tests about a link at an output name asserted the POSIX rule
  as though it were the only one.** A link left where synthtwin is
  about to write is stopped by two different rules. On POSIX a link
  resolves to an ordinary local path, so the locality check passes it
  and the run is stopped later, by the comparison that finds the
  output name and the user's table are one file. On Windows the
  locality check refuses the link first -- any link, symbolic link,
  junction or mount point, because one there can quietly lead to a
  network location -- so that comparison is never reached and the run
  publishes nothing at all. The protection held on both; only the
  sentence differed, and two of the three tests stopped at an
  unexpected refusal before reaching any check of their own. Each test
  now asserts on EVERY platform what it was written for -- the table
  byte-for-byte unchanged, every link left exactly as it was found, no
  file published through one, no working file of synthtwin's own left
  behind, and the reason arriving as a sentence rather than a
  traceback -- and then pins the platform's own wording on the side
  that produced it. The Windows half is asserted rather than skipped:
  it is where the rule is strictest and where nothing had ever
  exercised it.
- **The write transaction's boundary injector traced nothing on
  Windows, so that whole check was vacuous there.** The injector
  recognizes the frames to interrupt by comparing each frame's
  filename against the transaction module's own, and the comparison
  string was rebuilt by resolving the module's path. On Windows the
  interpreter had imported the package through one spelling of that
  path while resolving it hands back the spelling the disk keeps, so
  the comparison matched no frame, no failure was ever injected, and
  every question the check asks went unasked. The floor each half
  carries -- a minimum number of boundaries that must have been
  injected into -- is what turned a silent pass into a red test, which
  is the reason those floors exist. The comparison string is now read
  off one of the module's own code objects, which is by construction
  what the frames carry, on every platform and every interpreter; and
  a new test states that fact directly, so the next reader of a
  failure here gets a diagnosis instead of a count of zero.

### Repaired after the hosted run of the Phase 2 suite: the bytes a test writes

Every Windows job failed while every macOS and Linux job passed, on one
refusal: a description was not in the exact form synthtwin writes. No
product code changed, and none should have. The writer fixes the line
ending rather than leaving it to the platform (plan D12), so a
description synthtwin produces is the same bytes everywhere, and the
loader -- which writes the parsed document out again and compares the
bytes -- was right to refuse a file synthtwin had not written. The
defect was in the tests: they wrote the description themselves, in text
mode with no line-ending argument, so Python translated every line
ending to the platform's own and left a file that only Windows produces
and that the loader must then turn away.

- **The bytes of a description a test writes are now decided in one
  place.** `write_profile` in `tests/fixtures.py` serializes through the
  product's own canonical serializer and fixes the line ending, so the
  file it leaves is byte for byte the file `synthtwin profile` writes;
  a test asserts that equality against the product's writer for the same
  document. Twenty-three test modules that each wrote that file
  themselves now ask for it instead. One of the twenty-three, the
  loader's refusal battery, still composes bytes of its own for the
  cases whose whole subject is a file synthtwin would never write --
  which it says in as many words, and writes with an explicit line
  ending so that what it composed is what reaches the disk on every
  platform.
- **A guard reads the suite's own source so the next one cannot arrive
  unnoticed.** `tests/test_description_line_endings.py` turns red when
  any test writes a description -- or a file named like one -- with the
  line ending left to the platform, and it is put through the original
  defect in source form, so a rule that has stopped recognizing a
  description cannot pass in silence. A companion test writes a
  description with Windows line endings on any platform and asserts the
  loader refuses it with the message the Windows jobs printed, which is
  the property the whole arrangement exists to keep from reaching a
  person.

### Earlier
- Phase 0 public skeleton: package scaffold, `synthtwin` CLI stub, the
  offline guarantee's layered checks, the decontamination scanner and
  manifest, the data-provenance guard, and CI with a single aggregate
  gate job (not yet a mechanically required context: the branch ruleset
  is deferred while the repository is private). No data functionality yet - profiling and generation
  arrive in later phases per the project plan.

# Phase 4 — comprehensive column handling: every column read well, or declined loudly

**Status:** revision 5, 2026-08-19 — **RATIFIED at plan review round
5**, after rounds 1 (REJECT, twelve items, seven blocking), 2 (REJECT,
eleven, seven blocking), 3 (REJECT, seven, four blocking) and 4
(REJECT, nine, five blocking), every item repaired and its repair
verified by the round that followed; round 5, the final abbreviated
verification, replayed the round-4 counterexamples against the
repaired rules, verified all nine closed, and returned RATIFY with no
review items and no conditions. Before external review began, revision
0 was put through a maintainer-internal adversarial pass of six
independent reviewers, which returned seventy-five items, eight
blocking; revision 1 was that repair. The closure tables sit in the
review record at the end, which governs. This is the ratified design
Phase 4 is built from. The plan joins the disposition seal, the
`GOVERNING` set, and the claim-inventory surface list at the commit
that lands this ratification, exactly as the Phase 3 plan and the two
later specifications landed; from that commit its own prose is walked
by the claim-inventory guard families like every other governing
surface.

**Charter (CLAUDE.md):** "Phase 4 — comprehensive column handling: the
full range of column types, rare categories, and missing-data
patterns." The phase is governed by principle 5: every column in the
user's table is either handled correctly by an appropriate type path or
declined with a plain-language explanation; columns are never silently
dropped, silently miscast, or silently approximated. Both prior plans
reserved this phase's lever by name: "no new roles or subtypes
(Phase 4)" is a ratified non-goal of the Phase 2 plan and again of the
Phase 3 plan. This plan lifts that reservation and nothing else
reserved to another phase.

**The problem, stated the way the owner stated it.** A column matching
no detection rule becomes free text, which publishes no values at all —
so it returns as meaningless filler in the twin, and nothing on any
OUTCOME surface complains: `profile`, `generate` and `validate` all
exit 0, the quality report certifies the filler as meeting every
published obligation, `quality_state` reads `ok`, and the one sentence
in the twin report that says values were invented prints only inside
the spreadsheet-formula section, only when a formula-leader cell
exists. The profile-side prose does complain — the evidence sentence,
the competing-readings remark and the withheld note all exist and are
reprinted — so the letter of principle 5's "declined with a
plain-language explanation" is met while its purpose is not: the
product's two goals are that code developed against the twin runs
unchanged on the real table and that per-column statistics are
reliable, and a silently-filled column defeats both while every test
stays green. Phase 4 closes that twice over: fewer real column shapes
fall through, and the fall-through that remains is loud on every
surface where a person meets the twin.

**The one rule that shapes everything below — no regression by
reclassification.** Every new reading this plan adds claims only
columns that today land in free text. The three new roles are tested
AFTER the categorical rule, so no column that any value-publishing or
label-publishing rule handles today changes its role under this plan;
the only movement is out of the publishes-nothing fallback. The one
place existing rules widen — the date-format table — widens inside the
datetime rule at its ratified position, so a column newly read there
behaves exactly as an ISO-date column behaves today, under the same
ratified endpoint policy. ONE deliberate exception, named here because
the rule would otherwise forbid a deliverable: decision 7 changes the
READING layer, not the rule tree — cells wearing the added
spreadsheet-error literals become holes before any rule runs — and
re-reading a cell can move a column between EXISTING roles (a
two-valued column half-full of error literals is binary today and
constant once they read as holes; a numeric column they polluted past
the parse line climbs back to numeric). Those transitions are the
decision's stated consequence, authorized with it, and bounded by it:
they can arise only on columns holding the named literals, and only in
the direction re-reading produces. This rule is an acceptance
criterion with a two-part battery: with the decision-7 literals held
out of the fixtures (or read as data), the shipped tree and the
Phase 4 tree agree on every column except free_text into a new role or
into a newly-read datetime format; and a second fixture set that DOES
hold the literals asserts that every transition it shows is exactly a
re-reading consequence, each direction exercised.

**Scope.** Five deliverables: (1) the loud decline — every surface that
hands a person invented content says so, unconditionally, per column;
(2) new type paths — a number-with-affix role, a time-of-day role, a
month resolution, mixed-resolution ISO columns, and one added date
format **(AMENDED by A-P4-1: plus the two slashed datetime members and
the four-family unpadded widening)**; (3) rare categories — a long-tail label role that gives an
over-ceiling column the same floor-governed level machinery a
categorical column has, instead of nothing; (4) missing-data patterns,
per column — the twin reproduces the recorded hole spellings the
description already publishes, closing the reproduction half that
Phase 2 declined and no phase ever took; (5) settlement of the
column-shaped owner flags this phase inherits: width facts for
unrepresentable numbers (R-P2-1), the fixed-fraction spelling fact (the
durable close of R-P3-12's route), and the Excel-artifact missing
spellings. Deliverable 1's twin-report and screen surfaces land early
and change no governed document's obligations; its quality-report
surface lands with the validation-method amendment. Deliverables 2
through 5 all change either the profile wire or sentences of the
version 5 contract, so every one of them rides the single version 6
landing — including deliverable 4, whose twin-side rule is forbidden by
a sealed sentence of the version 5 contract (C5-9: no absent-value
spelling is reproduced in any twin) and therefore lands only where a
version 6 clause supersedes that sentence in the open.

**Non-goals.** No cross-column structure of any kind — no correlation,
no shared absence, no shared pattern of which cells are empty, no
grain, no keys; the eight `relationships` slots stay null and
`missing_data_process` stays Phase 5's (this plan's missing-data work
is per-column only, and P4-D6 draws that line in the open). No
value-based identifier inference — withdrawn three times under review
item P1-R6-F8 and not reopened here. No routing by the width of text
and no majority-numeric publication — both deleted under review item
P1-R6-F7 and not reopened. No fuzzy or guessing date parser — the
format table stays explicit and auditable. No change to the declaration
matching rule: `--keep-value` and `--missing-value` match whole cells
under the recorded rule, never fragments of them. No new input or
output formats (Excel, parquet, databases stay deferred); no streaming
read; no row-count override; no machine-readable verdict file; no
chaining command; no standalone build (Phase 6); no screen (Phase 7).
No source language ever reaches the twin through an invention path:
free text and every other invention stays invented, and carrying source
text into an invented cell remains a charter change requiring an owner
decision and a privacy review (published labels, variants and hole
spellings are not inventions — they are the label path's ratified
publications, and P4-D5 and P4-D6 price where this plan widens that
path). No new numeric stand-in sentinels (the judged set stays exactly
three; the declaration path covers the rest). No decimal-comma reading
— deferred with reasons in P4-D13. No change to the disclosure gate's
scope: what the quality report withholds remains a rule about one
report, and nothing in this plan claims more for it.

## Sequencing — artifacts, in order

1. **This plan**, ratified through adversarial review before anything
   below it exists. At ratification it lands with its seal entry, the
   `GOVERNING` addition, the guard's updated lists, and the
   claim-inventory surface addition — same-commit landing is procedure,
   as it was for the Phase 3 plan and the version 5 contract.
2. **The loud decline, part one** (P4-D2 items 1, 2 and 4): the twin
   report's unconditional invention lines, the generate-time screen
   line, and the profiler summary's forward sentence. These surfaces
   are plan-governed (their content authority is P2-D10 and this plan;
   no sealed method fixes their sentences), report bytes move, and the
   golden hashes are re-recorded in the same commit with cause-naming
   comments. The quality report is NOT touched here.
3. **`docs/spec/profile-contract-v6.md`** (P4-D7), ratified before any
   version 6 code: the complete normative shape of every new role and
   fact, carrying version 5 by reference exactly as version 5 carries
   version 4, including the clause that supersedes C5-9 for the
   reproduction rule and the dispositions table for every moved fact.
4. **Generation-method amendments** (P4-D8) under counted re-seal, with
   frozen reference vectors and committed failing mutants for every new
   branch, reviewed before the implementation they anchor exists.
5. **Validation-method work** (P4-D9): first its own revision 1 — the
   completed entry table and the report's normative byte layout, the
   document's recorded debt — then the Phase 4 additions, including the
   quality report's loud-decline sentences (P4-D2 item 3), so this
   phase extends a completed table rather than widening an incomplete
   one.
6. **The version 6 implementation**: producer, loader, generator,
   validator, the reproduction rule, and every naming surface flip in
   one landing, because the loader reads exactly one version and the
   format keeps its no-optional-keys rule — a partial landing would
   emit documents the flipped loader refuses. Built in sub-stages on a
   branch; landed whole; the claim-migration table of P4-D7.9 names
   every surface sentence that moves with it.
7. **Phase close**: residual register settled, batteries green, the
   phase-close audit confirming each governing document's introducing
   commit carried its seal.

**Two preconditions, stated rather than discovered.** First: Phase 4
implementation (stage 2 onward) begins only after the owner settles
Phase 3's closing state — the release executed, or closure recorded as
an owner act on the Phase 0 and Phase 2 precedent — because the phase
ledger, the README status line and the claim inventory's pinned phase
statements move in stage 2's first commit and must write a true
sentence about Phase 3 when they do. **(AMENDED by A-P4-4 for stage 2
ALONE, after the fact and on the owner's authority: stage 2 was built
on a branch before Phase 3's closing state was settled, the settlement
and the statement moves land together in the commit carrying that
amendment, and the amendment prices what the interval cost. This
precondition keeps its full force for stages 3 through 7.)** Second: every owner decision of
P4-D0 is taken before the ARTIFACT that encodes it is ratified — and
the stage 3 contract encodes ALL EIGHT (decision 8's `day_first` is one
of its seventeen settings keys), so all eight decisions precede
stage 3, never merely the implementation that follows.

## P4-D0. Owner decisions this phase needs

The standing convention: the decision, its cost stated plainly, and
what it buys. Eight decisions govern this phase, each proposed by this
plan with a recommendation, and the sequencing preconditions above make
every artifact wait on the decisions it encodes. **All eight were TAKEN
on 2026-08-19 and are recorded in place below, decision 7 with an owner
modification** — the sentence that stood here saying none was yet an
owner ruling moved with them (amendment A-P4-1's pricing note). A
decision taken is recorded here, in place, with its date, exactly as
the Phase 3 plan records its eleven; had one been declined, its
sections would have been struck by amendment with a residual entry
recording what remained undone.

1. **Long-tail labels publish floor-cleared levels from columns that
   publish nothing today** (P4-D5; recommended: yes). A column past the
   categorical ceiling, holding at least one level that covers
   `max(small_cell_floor, 11)` rows, moves from free text to the new
   long-tail role and publishes exactly what a categorical column
   publishes: levels at or above the floor, and counted anonymous
   remainders below it. Cost: THIS LOWERS a publication stance —
   repeated spellings publish from columns that publish no value today
   — priced in full in P4-D5, including the lowered-floor widening and
   its endpoint, the repeated-prose case, the undescribed-grain caveat,
   and the folded-grouping fact the suppressed multiset carries beyond
   today's raw repetition map. What it buys: the rare-categories half of the phase — region
   lists, code lists and status columns in mid-sized tables stop
   vanishing into filler. **TAKEN 2026-08-19: yes.** The owner's
   ground, recorded: fidelity — the closer the twin reads to the real
   table, the more reliable the code developed against it and the
   per-column statistics. The pricing above stands exactly as written:
   the floor governs every published label, and all five output files
   remain real-derived material under the charter's honest limits.
2. **The twin reproduces recorded hole spellings** (P4-D6; recommended:
   yes). Lifts the Phase 2 non-goal "no reproduction of absent-value
   spellings", which no phase ever took, by superseding contract
   sentence C5-9 in the version 6 document. Cost: twin bytes move at
   fixed (profile, seed) — a changelogged regeneration event; the
   moved dispositions are enumerated in the version 6 matrix; the twin
   becomes a surface that carries a person's published hole spellings
   (it already carries published labels and variants — the same
   publication class — and SECURITY.md and the summary say so); the
   generator gains a rejection rule so no present cell wears a
   published hole spelling. What it buys: code that names its own
   missing markers — reading the twin with the same na-word list it
   will use on the real table — runs unchanged. **TAKEN 2026-08-19:
   yes.** The owner's ground, recorded: the closer the twin is to the
   real table, the more reliable the developed code first and the
   statistics second — the owner's two stated goals, in that order.
3. **The affixed-number role** (P4-D4.1; recommended: yes). Cost: two
   published affix spellings per affected column (floor-governed,
   under one named exception to the ranges class's no-spelling rule),
   plus the whole numeric block — distribution, moments, sign and zero
   counts, styles and widths — published from columns that publish
   nothing today, enumerated as a grouped row of the disclosure delta,
   one more role through every enumeration, a new plain-number
   straggler construction in the method, a standing per-column remark,
   and a new misroute surface — prefixed code columns can read as
   quantities, remarked on every column the role claims because no
   shape test can single out the code-shaped ones — priced and guarded
   in P4-D4.1. What it buys: prices, percentages and unit-bearing
   measurements that today land in free text get real distributions
   and twin cells that parse the same way the source cells do.
   **TAKEN 2026-08-19: yes.** The owner's ground, recorded: reproduce
   the source's columns in the twin as closely as the published facts
   allow.
4. **The time-of-day role, the month resolution, one added date format,
   and mixed-resolution ISO columns** (P4-D4.2, P4-D4.3; recommended:
   yes). Cost: one more role and one more resolution through every
   enumeration, including the sibling precision vocabulary and three
   new members of the closed datetime format vocabulary **(AMENDED by
   A-P4-1: five, the two slashed datetime members joining)** with their
   resolution bindings; recorded exact form-mix counts on ISO datetime
   columns (REPORT-ONLY — the twin writes the finest form and the
   report says so, the recorded-not-kept precedent of the format fact
   itself); endpoint publication from
   columns that publish nothing today, under the ratified floor-free
   endpoint policy for range-class roles — named in the disclosure
   delta, not slipped in; and a read-time consequence: the widened
   format table reaches the first-row evidence rules, so which
   headerless files are stopped-and-asked changes, re-calibrated and
   re-tested. What it buys: clock-time and month columns stop falling
   through, and the single most common export shape — one ISO column
   mixing dates and datetimes — is read. **TAKEN 2026-08-19: yes.**
5. **Width facts for unrepresentable numbers** (P4-D4.4; recommended:
   yes). Settles R-P2-1, flagged for the owner since Phase 2. Cost: two
   published length facts on a role that publishes no value of the
   table — and for decimal numerals length IS magnitude, so
   `max_length` states the largest withheld value's order of magnitude,
   a one-cell, floor-free fact; the invented 400-figure width retires;
   the fold-partner rule gains a width-pinned clause so the change
   cannot make a real column's twin refuse. What it buys: the one
   taxonomy fact both prior plans left explicitly open is settled, and
   the twin of such a column stops writing 400-figure stand-ins for
   4-figure sources. **TAKEN 2026-08-19: yes.**
6. **The fixed-fraction spelling fact** (P4-D4.5; recommended: yes). A
   numeric column's styles block records how many decimal cells share
   each fraction width. Cost: one fact through the styles machinery and
   its recount identity; the generator writes fixed-width decimals
   where the counts say so. What it buys: the durable close of
   R-P3-12's route — a two-decimal price column checks clean against
   its own description because the description finally records what the
   file does — superseding whichever interim option amendment A-P3-46's
   ruling took, and strengthening rather than trading away the
   obligation review item P3-V2-C-F1 restored. **TAKEN 2026-08-19:
   yes.** The owner's ground, recorded: the same fidelity ground as
   decisions 1 through 3 — reproduce the source so code and statistics
   carry over.
7. **Excel-artifact missing spellings** (P4-D6.2; recommended: yes,
   exactly as enumerated there — the seven Excel error literals, and
   deliberately NOT the pandas absent-time literal, which case-folds
   onto a person's name). Cost: a closed-vocabulary extension — a wire
   event riding the version 6 bump — and a behavior change: cells
   wearing those artifacts read as holes everywhere, including tables
   where somebody meant them as data (the `--keep-value` route remains
   for that person), and re-reading can move an affected column between
   EXISTING roles — the named exception to the no-regression rule,
   bounded and battery-tested where that rule is stated; every surface
   that states the vocabulary's count,
   including the Phase 3 plan's residual R-P3-8 entry, moves by counted
   re-seal in the same landing. What it buys: the most common
   machine-written hole spellings stop counting as data and stop
   pushing numeric columns over the parse line into free text.
   **TAKEN 2026-08-19: yes, WITH ONE OWNER MODIFICATION.** The pandas
   absent-time literal joins the list after all, as the vocabulary's
   one EXACT-SPELLING member: it reads as a hole only on raw
   byte-for-byte equality with the cell — no trimming and no case
   folding, one operation, applied identically in missing recognition,
   declaration recording, the published-vocabulary tests and the
   validator's reconstruction — so the review's concern, a person's
   name folding onto it, cannot arise.
   The matching rule gains that one stated exception; P4-D6.2 carries
   the amended enumeration with this ruling's date. The owner's
   ground, recorded: for statistical work the pandas absent-time
   literal means "no value" and nothing else, and the priority is code
   developed on the twin behaving as it will on the real table.
8. **The day-first declaration** (P4-D4.6; recommended: yes). A
   `--day-first` option that breaks the month/day tie in the declared
   direction, under an evidence-first rule: where the cells themselves
   settle the direction, the evidence wins and a remark says so; the
   declaration decides only what evidence cannot. Cost: one option
   through the option machinery, including the version-refusal
   message's priced list, plus one new remark for the
   evidence-overrides-declaration case. What it buys: the silent
   month/day swap on fully-ambiguous day-first tables — today guarded
   only by a remark — becomes declarable by the person who knows,
   without handing them a lever that can reverse a column against its
   own evidence. **TAKEN 2026-08-19: yes.**

**On whose authority each will stand:** the owner's, on the date
recorded beside it when taken. No review verdict and no implementer's
judgment stands behind an owner decision.

## P4-D1. The measured inventory: what falls through, what misroutes

This section is the evidence the rest of the plan answers. Every entry
was verified against the shipped taxonomy, the parsing rules, and the
generation and validation methods at the commit this plan was drafted
from (`4de1519`).

**Route one into filler: no reading fits.** A column reaches free text
exactly when it is not declared, not empty, below the numeric parse
line (99% of present values, applied as a count), matches no single
date format at that same line, holds three or more folded-distinct
values, and exceeds the categorical ceiling
`max(min(1000, floor(0.10 × rows)), 2)`. Concrete shapes that land
there today:

- clock times (`14:05`, `09:30:00`) — no time reading exists;
- month columns (`2024-03`) — no month resolution exists;
- one ISO column mixing `2024-03-17` and `2024-03-17 14:05:00` cells —
  each format alone fails the 99% line once the mix passes 1%;
- prices, percentages and unit-bearing measurements (`$1,234.50`,
  `45%`, `5 mg`, `170cm`) — an affix makes the cell not-a-number, and
  the whole distribution is withheld (the number reading itself already
  accepts group separators, surrounding whitespace, a leading plus and
  accounting parentheses; it is the affix that defeats it);
- censored or bounded readings (`<5`, `>=10`) past the slack of a
  numeric column;
- region lists, code lists, and any label set whose distinct count
  exceeds a tenth of the rows — forty labels in a hundred rows;
- every label set of three or more in a table under thirty rows, where
  the ceiling formula bottoms out at two;
- formatted record numbers with punctuation, and multi-valued cells.

**Route two: misroutes that publish wrong facts quietly.** Numeric-
looking codes (postal codes, account numbers) read as quantities with a
published mean — remarked only when nearly all-different; an all-digit
column of valid `YYYYMMDD` values reads as dates ahead of numbers;
slashed day-first dates read month-first, remarked once; two-valued
numeric columns publish labels rather than a distribution (a documented
trade this plan keeps); and stand-in numbers inside label columns are
never judged, because sentinel judging runs only above the numeric
parse line — a label column can publish `-999` as an ordinary level
with nothing said (answered by the new remark of P4-D4.7).

**The silence, precisely.** For a fall-through column the profile
carries an evidence sentence and remarks; the summary prints them; the
twin report reprints them. But: every command exits 0; `quality_state`
is `ok`; the generation report's deviations section reads "nothing was
given up" because shape facts are met by construction; the quality
report passes; and the only "synthtwin MADE UP" sentence is conditional
on formula-leader cells. No machine-readable field and no unconditional
sentence tells a person that a column's twin content is invention.

**What this plan deliberately keeps.** The deleted rules stay deleted:
no width routing, no majority-numeric publication, no identifier guess.
Free text remains the last resort rather than a refusal — "unsupported
column type" still does not exist as an outcome, because a refusal
would let one odd column block a whole table. The 99% parse line stays
one line, applied as a count. The binary-before-numbers trade stays,
with its remark. The categorical ceiling stays as the boundary of the
categorical role itself; what changes is what lies beyond it (P4-D5).

## P4-D2. The loud decline: every surface says what is invented

The rule this section implements: **wherever a person meets twin
content that synthtwin invented, the surface says so, per column, in
plain language, unconditionally for the class the column is in.** Three
classes, each with its own sentence, because one sentence would be
false at the edges:

- **Fully invented**: a column whose role publishes no value of the
  table AND whose `n_present` is not zero — free text, declared
  identifiers, unrepresentable numbers. Every present twin cell is
  synthtwin's own construction. (An `empty` column is excluded: its
  twin holds no present values, so an invention sentence about it would
  be false.) **(AMENDED by A-P4-2: a column of either class below whose
  invented cells are ALL of its present cells is in this class too —
  the role opens a class and the cells settle it.)**
- **Partially invented labels**: a label-class column with suppressed
  levels or withheld variants — the twin carries its published
  spellings byte-for-byte plus counted neutral stand-ins (`group-N`,
  invented variant spellings) for the withheld remainder.
- **Counted stand-in cells**: any column whose construction writes
  counted stand-ins for cells the description could not carry —
  unparsed datetime cells, out-of-range, contradictory and non-numeric
  stragglers. The counts are the plan's own bookkeeping; the surface
  states how many.

The class of a column is computed from what this plan already has: the
role and `structural_role` decide the first class; the published
suppression facts decide the second; the construction's own counted
stand-ins decide the third. No new wire fact is needed.

1. **The twin report** (stage 2) gains, per affected column, one
   unconditional line stating — by class — that every present value, or
   N named cells, in the twin's column is synthtwin's own construction,
   that only the published facts were matched, and that numbers
   computed on invented content mean nothing about the real table. The
   existing conditional sentence inside the formula-hazard section
   stays for its own purpose; it stops being the only place.
2. **The generation screen and report closing** (stage 2) count both
   kinds, because a line that counted only the fully-invented columns
   would read "0 of 1" over a twin holding invented labels: the one
   `_warn` line at generate time, and the report's closing count, say
   how many columns hold ONLY invented values and how many more hold
   SOME — each half in words that say exactly what it counts.
   Per-column detail prints in the report body.
3. **The quality report** (stage 5, inside the validation-method
   amendment, because that method is the normative authority on what a
   quality report says) speaks about the DESCRIPTION, never about the
   measured file's provenance — the checker cannot tell a twin from a
   real file and its sentences may not pretend to. Per class: for a
   fully-invented column, that the description publishes no value of
   this column, so these checks measure published shape facts only and
   a pass certifies nothing about what the cells mean — in a generated
   twin, every one of them is invented; for a label column with
   suppression, that the description withholds N levels covering M
   rows, that a twin built from it invents stand-ins for them, and
   that these checks cannot tell such stand-ins from real cells; and
   for a column whose description leaves N cells uncarryable — the
   unparsed, out-of-range, contradictory and non-numeric counts — that
   a conforming twin writes N counted stand-in cells there, which these
   checks likewise cannot tell from real ones. The
   analyst-facing expectations section names the invention classes it
   does not cover. Phrased inside the report's existing vocabulary — a
   pass already means only "no checkable obligation was missed".
4. **The profiler summary** (stage 2) states, in the disclosure
   section's own words, that the twin of a fully-invented column will
   hold invented values — a sentence already true of the shipped
   generator, so it lands with no code change and the claim inventory
   verifies it against what generate does.
5. **Exit codes do not move.** 0/3/1/2 keep their meanings; a decline
   is not a failure, and a warning exit would break every script that
   checks for success. The loudness is in the artifacts and the one
   screen line.

Every new sentence passes the display boundary and lands with
exact-shape tests. **(AMENDED by A-P4-3: this paragraph also required
every new sentence to be built through the profile's enumerated note
grammar. That rule governs sentences of the PROFILE DOCUMENT, where it
already governed; the report, screen, summary and quality-report
sentences are governed by the four controls the amendment names, and
its residual R-P4-14 carries what the scoping costs.)** Report and quality-report bytes move at their stages, so the
golden hashes are re-recorded in the same commits with cause-naming
comments. THIS RAISES reporting obligations and lowers nothing.

## P4-D3. The taxonomy after Phase 4

The rule order, first match wins, with the three inserted rules marked:

0. empty (unchanged — and it settles BEFORE the declaration, the
   ratified exception: an all-absent declared column takes role
   `empty` with `structural_role` `identifier`, exactly as the
   contract's axis rules and the shipped producer already have it);
1. declared identifier (unchanged — declaration is the only route);
2. numeric_unrepresentable (unchanged);
3. constant (unchanged);
4. binary (unchanged, trade documented);
5. datetime — widened inside its ratified position: one added format,
   the month resolution, and the mixed-resolution ISO rule (P4-D4.3);
6. count / continuous (unchanged);
7. categorical (unchanged, ceiling and all);
8. **time_of_day** (new, P4-D4.2);
9. **affixed_number** (new, P4-D4.1);
10. **long_tail_labels** (new, P4-D5);
11. free_text — everything else, exactly as today, now loud (P4-D2).

Rules 8 through 10 sit AFTER categorical by design — the no-regression
rule of the header: a column any earlier rule claims today is claimed
by the same rule tomorrow, so the new roles reach only columns that
today publish nothing. Their internal order is: time before affix
(clock text rarely splits as an affixed number, but the time reading is
the more specific claim), affix before long-tail (a distribution
beats labels where both could fire), long-tail last before the
fallback.

Consequences the enumerations must absorb, stated once here and owed by
every section below: three new roles enter `ROLES` in rule order; the
role-to-statistical_type bijection gains three rows, each new role
naming itself — which is a stated cost, not an oversight: for these
roles the shape axis buys nothing over the role name, and the axes'
value is the totality discipline, not extra information; every new role
carries `quality_state` `ok` and `structural_role` `data` (declaration
still forces `identifier`, winning right after the empty rule settles,
exactly as today), so the full axis triple
of every new role is written in this sentence; `ROLE_AXES` stays total
with its completeness test; the contract's axes table, the
forbidden-key matrix, the disposition registry's role groups and
contract sections, the note grammar, the report and summary word
tables, the fixture builders, the loader's role enumeration, AND the
first-row evidence rules in the reader — which share the format table
and the number classifier with the taxonomy, so widened readings change
which headerless files are stopped-and-asked — all move at stage 6,
with the reader's three calibration shapes and measured slack re-run.
The record-evidence rule itself extends to the two new readings by the
same POSITIVE membership shape it has for numbers and dates today — a
number among numbers, a date among dates, is evidence the first row is
a RECORD, and the reader stops and asks. Two new membership tests: a
first-row cell that is an affixed number wearing the same pair as the
affixed numbers below it, and a first-row cell that is a clock time in
the same form as the clock times below it, are each evidence of a
record, under the same comparison discipline the number and date tests
use. So a headerless column of one-of-a-kind prices or clock times is
stopped-and-asked instead of having its first record eaten as a
presumed header — the exact loss the reader's own rules exist to
prevent.

Publication classes — every role in exactly one, the invariant kept:
`time_of_day` joins the ranges class. `long_tail_labels` joins the
labels class — its published spellings are whole values of the table
under the same floor as every label. `affixed_number` joins the RANGES
class, whose "no spelling appears" sentence gains ONE named,
matrix-confined exception: this role's two affix keys carry
floor-governed shared affix text, and no other key of any ranges-class
role may ever carry a spelling. The exception is written into the
class doctrine by name, priced in the disclosure delta, and enforced
where the classes are enforced — the exact-one-class invariant and the
forbidden-key matrix — so the labels class is untouched and the
nothing class's "no value, no spelling, no fragment of one" sentence
is untouched.

Detection thresholds stay decisions, not diagnostics: every new line
this plan draws is a named `Settings` constant recorded in every
profile, applied as a count, with a borderline remark within the
standing slack. Two of the new rules consult a floor at DETECTION time,
deliberately: for the affix pair and the long-tail level, publishing a
floor-clearing spelling is constitutive of the role, so a column that
cannot publish one under the recorded settings takes the next rule
instead. Because the floor can also be RAISED without limit (the option
accepts any whole number from one up, silently above the default), the
plan states the direction plainly: a raised floor or a tiny table
withholds the new roles; a lowered floor widens what the long-tail role
publishes, priced in P4-D5. The same table under the same settings
always takes the same role, on the producer and on the validator's
re-description alike.

The settings block grows from fifteen keys to the exact count P4-D7
enumerates, and the validator's settings-consumption table moves with
it in the same landing — a key skipped or invented is red against the
contract's own enumeration.

## P4-D4. The full range of column types

### P4-D4.1 The affixed-number role

**What it reads.** A cell is an affixed number when its trimmed text
splits as `prefix + core + suffix`, where the core is a substring the
shipped number classifier reads as a number this format can hold —
the ONE classifier, unchanged, with its existing acceptance of group
separators, a leading plus, and accounting parentheses — and at least
one of prefix and suffix is non-empty. Where more than one substring
parses, the core is the LONGEST, and of equal-length candidates the
LEFTMOST — a stated total order, so the split is a function of the
cell. A column takes the role when, after every earlier rule has
declined it, at least the parse-line count of its present cells are
affixed numbers wearing the column's ONE affix pair — the exact
(prefix, suffix) text of the trimmed cell, no case folding, no inner
trimming — and that pair's count is at least the small-cell floor. One
pair per column, exact-spelling identity, deliberately: a column mixing
`$` cells and `EUR` cells, or `mg` and `MG` cells, past the line's
slack declines to the later rules exactly as today, with the
competing-readings remark extended to say how far the affix reading
got. Mixed-affix and case-varying-affix columns are named residuals
(P4-D13), not partial publications — publishing a distribution over
some cells while dropping others is the outcome principle 5 forbids and
review item P1-R6-F7 deleted.

**Stand-in numbers are judged before the role tests that can see
them — and never on a column an earlier rule claims.** The shipped
sentinel pass is UNTOUCHED: numeric-eligibility judging runs exactly
as today, before everything. The new, affix-based eligibility runs at
a stated later point: only after rules 0 through 7 have all declined
the un-removed column — so a column that constant, binary, datetime,
the numeric rules or categorical would claim today is claimed by the
same rule on the same cells tomorrow, and the no-regression rule
holds by construction (a two-valued column whose cells share an affix
pair stays binary; the new pass never sees it). Where rules 0–7
decline, the affix split — computed at cell-classification time as
part of the one cell record — makes the column eligible when its
affixed reading reaches the parse line; judged candidates (matched
over cores by the existing outlier-and-share rule) are removed and the
column re-tallied exactly as on a plain numeric column today, and only
THEN do rules 8 through 11 run over what remains.
So a marker core inside an affixed column (`-999 mg`) is read as a
hole, never averaged in — and the order question has one answer: a
column whose pair count survives sentinel removal at or above the floor
takes the role, and one whose pair count is eaten below the floor or
below the line by removal declines, by one fixed rule — the same
post-removal fall-through a plain numeric column can take today when
removal thins its population. That fall-through is LOUD where it
lands: the competing-readings remark, already extended to say how far
the affix reading got, additionally states how many cells stand-in
judging removed whenever removal moved the column across a line, so a
column that fell to a later rule because a marker was read out of it
says so in its own evidence — and the sentinel verdicts themselves
stay published under the landing role's publication class, exactly as
today. Declared values keep their ratified whole-cell matching;
nothing about declarations changes.

**What it publishes.** The affix pair, exact spellings, floor-governed
(the detection rule above makes the pair's count clear the floor or the
role decline, so a published pair is always a floor-cleared fact).
Beside the pair: the complete numeric details block of a
count/continuous column, computed over the cores — the eleven-rung
percentile ladder, mean, standard deviation, skewness, the sign and
zero counts, the styles block including P4-D4.5's fraction-width fact —
plus the count of affixed cells. Count-like or continuous-like is the
existing verdict applied to the cores and published as the existing
`integer_valued` fact, never inferred from the role name. The ladder's
two ends are exact values of cores, published floor-free — the ratified
endpoint policy of every ranges-class role, and since this column was
free text yesterday, that is a new disclosure the delta section names.

**What the twin writes.** `prefix + core + suffix` per cell, cores
generated by the existing numeric machinery over the published core
facts, affixes byte-for-byte. The up-to-one-percent of present cells
that did not wear the pair are reproduced by class through the
straggler constructions, including a NEW plain-number straggler
construction the method amendment defines (a conforming plain-number
spelling that reads back as a number, collides with no published hole
spelling and no date form) — named here because the existing straggler
set covers only out-of-range, contradictory and text cells.
Re-profiling the twin re-detects the role with the same facts — the
green battery bar.

**The misroute this creates, priced — and remarked without a
condition.** A prefixed code column (`A-101`, `A-102`, …) that today
lands in free text now reads as quantities with a published
distribution over the numeric parts, and no shape test can separate an
opaque token family from a measurement — repeating decimal-cored
tokens defeat every conditional remark anyone drafts, which is exactly
how three identifier inferences were defeated before withdrawal. So
the remark is STANDING, not conditional: EVERY affixed-number column
carries a remark naming its pair, saying its numeric parts were
described as quantities, and naming `--identifier` as the route if
these are codes rather than measurements — the same
tell-the-person-both-ways posture the all-different text remark
already takes, firing on every column the role claims rather than on a
guessable subset. The all-different remark additionally extends to
this role verbatim. What this misroute can NOT do, by the
no-regression rule: it cannot take a column away from any rule that
handles it today — `V1`/`V2`/`V3` visit labels stay categorical,
because categorical runs first.

### P4-D4.2 The time-of-day role

**What it reads.** Cells matching exactly `HH:MM` or `HH:MM:SS` —
two-digit fields, hours 00–23, minutes 00–59, seconds 00–59 — with ONE
of the two forms at the parse-line count, exactly as one date format
must clear the line today: cells of the other form, like any other
unreadable cell inside the line's slack, are counted in `n_unparsed`
and become counted stand-ins in the twin, loud under P4-D2's third
class. What does NOT exist is a JOINT clock reading: a column where
neither form alone clears the line declines to the later rules — the
mixed-ISO rule of P4-D4.3 exists because that mix is the dominant
export shape, clock-precision mixes are not, and this plan takes the
narrow reading first (the named candidate for a later widening on the
resolution-mix precedent). The shape is deliberately narrow, each
exclusion stated: no fractional seconds (a clock reading that silently
dropped them would approximate every cell); no leap second (the
seconds-of-day ordinal space has no faithful point for it — the
datetime role's endpoint-fields construction exists precisely because
ordinals cannot carry it, and this role does not import that
machinery); no single-digit hours. Each exclusion declines to the
later rules with the competing-readings remark extended, and each is a
named residual.

**What it publishes.** The datetime pattern transposed to the clock:
earliest, latest, an eleven-rung ordinal ladder (order statistics of
real cells — selection, no interpolation, like the date ladder), the
one form the column wears, and the unparsed count. One honest limit
stated at the fact that carries it: the ladder reads the day as a LINE
from 00:00 to 23:59:59, as every ladder reads its axis, so a column
whose values cluster across midnight is described as two edge clusters
with an empty middle, and the twin's interior interpolation fills that
middle — the clock face's circular reading is not modeled, exactly as
a two-humped numeric column's valley is filled by the same ladder
model today. The rungs stay exact real cells either way; P4-D12
restates this beside the model's other bounds. Two invariants
restated from the datetime precedent because the generation rule rests
on them: the ladder's two ends ARE the endpoints, and every rung lies
between them — the contract states both as loader-checked invariants,
the analogue of the datetime rules that pin its ladder.

**What the twin writes.** Rank 0 and rank last pinned to the endpoints;
interior ranks by the same floor-division interpolation the date rule
uses, in the ordinal unit THE PUBLISHED FORM ITSELF SETS — minutes of
day for `HH:MM`, seconds of day for `HH:MM:SS` — exactly as the
datetime rule's resolution sets its unit, so every interpolated ordinal
has a canonical spelling in the column's one form and no generated
value is ever truncated or widened to fit its cell. The PROFILER's
ladder is selection, the GENERATOR interpolates within the pinned ends,
and the interpolation is always satisfiable because the ends are real
cells of a closed finite space and every interior value floor-divides
between them in that same unit. All cells written in the column's one
published form. The all-different obligation binds through
the ordinal mechanism, with its capacity stated: the space holds 1,440
or 86,400 distinct spellings by form, and the unparsed cells are
stand-ins from an unbounded text family that supply distinctness of
their own, so the infeasible shape is a description whose distinct
demand NET of its unparsed cells exceeds the form's space —
`n_distinct − n_unparsed` past the form capacity — and only that shape
joins the refusal catalogue by name (P4-D8). A description whose own
source met every count, unparsed cells included, is never refused by
this rule.

### P4-D4.3 The widened date readings

Three widenings, each an explicit table entry — no guessing — all
inside the datetime rule at its ratified position, so a column newly
read here behaves as ISO-date columns behave today **(AMENDED by
A-P4-1, which adds two more by owner ruling: unpadded slashed fields,
and the two slashed datetime members — the amendment carries them in
full)**:

1. **One added format:** `YYYY/MM/DD` (slashed ISO order, unambiguous —
   the year leads). Dotted forms, textual months and two-digit years
   are named residuals with their reasons (P4-D13).
2. **The month resolution:** `YYYY-MM` joins the format table with
   resolution `month`, canonical form `YYYY-MM` (sorts as text), ladder
   and endpoints in month ordinals. The resolution enumeration AND its
   sibling `time_precision` enumeration each gain the member `month` —
   the quarter precedent shows the two move together — and every
   consumer of both vocabularies moves in the stage 6 landing, honoring
   the standing rule that a resolution added to the producer without a
   reading in the validator is red on the commit that adds it.
3. **Mixed-resolution ISO columns.** The single-format pass runs first,
   exactly as today, and its verdict stands wherever it clears — a
   column of 99 ISO dates and one datetime cell is an iso-date column
   with one unparsed cell today and stays one, the unparsed cell now
   counted by P4-D2's stand-in class. Only where NO single format
   clears the line does the new joint test run: where `iso-date` and
   `iso-datetime` cells TOGETHER reach the parse-line count, the column
   is one datetime column at the family's finest resolution. Such a
   column publishes `resolution_mix` — how many cells wore each form,
   keyed by the two existing format members' exact strings. The fact is
   a REQUIRED key on every datetime block (no optional keys;
   single-format columns publish it with one named form), published at
   EXACT counts with no floor, justified in the open: with a two-member
   form space beside the published parsed total, a pooled remainder is
   recoverable by subtraction, so a floor would withhold nothing — the
   fact is priced as what it is, a form-shape count that carries no
   value of the table, on the repetition-map precedent. And it is
   REPORT-ONLY, deliberately, on the exact precedent of the `format`
   fact itself (residual R-P2-7: the lexical date family is recorded,
   not kept): the twin writes every parsed cell at the column's finest
   recorded precision, exactly as the ratified datetime rule writes
   every column today, because a date-form cell cannot spell a
   datetime-resolution interior value and a construction that split the
   generated ordinals into two per-form lanes would need its own
   packing, feasibility rule and window family for one reading — cost
   out of proportion to a fact the reader still receives. The twin
   report names the mix as recorded-not-reproduced, per column, every
   run. Only the ISO family mixes; slashed and compact forms do not,
   because their mixes are ambiguous with one another; a month-with-day
   mix (`2024-03` beside `2024-03-17`) stays unread and is a named
   residual.

### P4-D4.4 Width facts for unrepresentable numbers (settles R-P2-1)

The role publishes `min_length` and `max_length` over its
NUMERIC-LOOKING cells — not over the whole present population, because
the role tolerates a slack of non-numeric stragglers whose lengths are
facts about text, not about the numbers this role exists for — the
same class of no-value fact the identifier role already publishes,
whitelisted the same way, with one honest difference stated: for
decimal numerals, length bounds magnitude, so `max_length` states the
largest withheld numeral's order of magnitude, one cell's worth of
floor-free fact; that is the disclosure decision 5 weighs. The
generator retires the invented 400-figure canonical width and writes
within the published range, end carriers pinned, capacity per the
existing family rule with the existing named refusal — and the
fold-partner rule gains a width-pinned clause: where the published ends
pin every cell's length, a fold partner may shorten its digit body to
make room for edge spacing inside the pinned length, so any source
whose own cells matched the published pattern remains expressible, and
the refusal stays reserved for descriptions no source could satisfy.
The always-printed width deviation retires with the invention. THIS
RAISES fidelity for these columns and closes residual R-P2-1.

### P4-D4.5 The fixed-fraction spelling fact (closes R-P3-12's route)

The numeric styles machinery gains one fact: among a column's `decimal`
cells, the count sharing each fraction width (digits after the point),
floor-governed with a pooled remainder like every styles fact. How the
twin meets it is fixed here at the level the method needs, because a
width is a property of the VALUE as well as the spelling: a value can
always be padded to a wider fraction, never narrowed below the digits
it needs, so width quotas are met the way the `integer_valued` fact is
met — by a published-fact-driven value adjustment. The construction,
with its place in the pipeline and its guards stated because a snap
that ran late or blind could break exact facts: width assignment and
snapping run INSIDE the value-construction stage, before any spelling
is chosen, under four rules. Pinned values — the endpoints and the
zero stratum, which are exact-observable — are NEVER snapped: a pinned
cell counts toward a width only when its value already fits it, and
where a pinned value fits SEVERAL published widths, which quota claims
it is itself fixed — pinned cells are walked in a stated order
(minimum, maximum, zero) and each takes the largest still-unfilled
width its value fits, a rule the method amendment carries so no byte
is left to an implementer's taste; the quotas are otherwise met from
unpinned cells. Each unpinned
decimal-destined cell is assigned a published width by the same
largest-remaining-quota walk that assigns styles, widths taken largest
first against the cells whose drawn values need the most fraction
digits, in the method's stated tie order; each assigned value is then
rounded half-even to its width — the integer rule's own class of
adjustment, justified the same way (the source's cells carried exactly
these widths), bounded by half a unit in the last published digit. A
snap may never change a cell's sign class or zero-ness: where rounding
would cross zero or erase a sign, the construction takes the nearest
same-class value at that width inside the cell's segment. And where
snapping would merge two strata onto one value, the distinctness
consequence routes through the numeric distinctness envelope the
method already carries — amended for the snap, never silently
absorbed. All of it lands where integer rounding lands today, in the
same G12 envelopes. The
pooled remainder's cells are unsnapped and written at their own value's
canonical decimal spelling, the remainder-by-its-own-value rule G6.4
already fixes for pooled styles. The validator checks each named width
with the pooled-fact window shape the method fixes and this plan
requires: recounted cells at a named width number at least the
published count and at most the published count plus the pool, the
arithmetic written in the generation method and cited, never restated —
exact where nothing pooled, windowed where something did. A two-decimal
price column's description then records what every cell does, the twin
writes `1.20` where the source did, and checking the source against its
own description stops missing on present cells nothing is wrong with —
the durable close of the route residual R-P3-12 records, superseding
whichever interim option amendment A-P3-46's ruling took. The
trailing-zero re-spelling attack that `styles.spelled` alone catches
stays caught: the new fact makes the re-spelled file miss its published
widths too, so the obligation P3-V2-C-F1 restored is strengthened, not
traded away.

### P4-D4.6 The day-first declaration

`--day-first` tells the profiler that slashed dates in this table are
day-first. Its mechanics are NOT a bare order swap, because a swap can
silently reverse a column against its own evidence: with ninety-nine
ambiguous slashed cells and one cell only the month-first reading can
parse, a swapped table lets the day-first reading clear the line first
and reads the whole column backwards, counting the one contrary cell —
the column's only evidence — as unparsed. The rule is therefore
evidence-first: when the option is given and a column's slashed cells
are in play, BOTH slashed readings are counted, and the reading that
parses strictly more cells wins whatever the declaration said; the
declaration decides only a count tie. And because a tie is NOT always
full ambiguity — a column can hold one cell only the day-first reading
parses AND one cell only the month-first reading parses, evidence in
both directions at equal counts — the remark rule is written over the
evidence, not over the winner: every slashed column read under the
option carries exactly one remark, built from four counts the format
pass already yields (cells each reading parses, cells ONLY each
reading parses) plus the reading used. The remark carries two
INDEPENDENT clauses, because how the winner was chosen and whether the
column contradicts itself are different questions that combine freely:
the first clause says which reading was used and why — strictly more
cells parsed, or the declaration broke a count tie; the second clause
appears whenever BOTH only-one-reading counts are nonzero, at any
count, tie or no tie, and says the column carries evidence in both
directions with both counts named — so a column that is
evidence-decided AND internally inconsistent is reported as both,
never presented as settled. The person is never silently overruled, never
silently obeyed against evidence, and never silently obeyed into free
text. It is a reading
declaration in the `--first-row` family: recorded in the settings block
as `day_first`, joined to the version-refusal message's owed-and-priced
option list in the commit that adds it (the suite derives that list
from the shipped parser, so forgetting is red).

### P4-D4.7 Misroute remarks (advisory, routing nothing)

Three remark widenings close the quiet half of route two: the
code-shaped remark (all-whole, nearly-never-repeating, or fixed-width
leading-zero digit strings) fires on repeating code columns too, not
only all-different ones, naming `--identifier` and routing nothing; the
compact-date-versus-number remark states both readings' counts; and a
NEW remark fires when a label-class column publishes a level whose
spelling is one of the three built-in stand-in numbers — the label
column's `-999` — naming `--missing-value` as the route if it means "no
value", routing nothing. **(AMENDED by A-P4-1: a fourth widening — the
recoverable-distribution advice on declined columns — joins by owner
ruling; the amendment carries its trigger.)** Remarks are enumerated
grammar forms with exact-shape tests, like every other sentence.

## P4-D5. Rare categories: the long-tail label role

**The rule.** Past the categorical ceiling, a column whose folded
levels include at least one covering `max(small_cell_floor, 11)` rows
takes the new `long_tail_labels` role. The `11` is a named constant
(the default publication floor, fixed here as the detection line's
lower bound), and the max is deliberate: LOWERING the publication floor
must not widen which columns become label-publishing — an all-different
or nearly-all-different column (names, addresses, free comments) has no
eleven-row level and stays free text at EVERY floor, so the free-text
role remains reachable and its promise stays floor-invariant. Raising
the floor raises the detection line with it.

**What it publishes.** The four shared label keys, under the shared
label invariants (B1 through B8), verbatim: `levels` (each at or above
the recorded floor, with exact variants and withheld-variant counts),
`suppressed_levels`, `suppressed_rows`, and `suppressed_level_counts` —
the anonymous ascending sizes of every below-floor level. NOT
`level_ceiling`, stated so no ambiguity survives into the contract:
that key is categorical's own, its invariant (folded distinctness at or
under the ceiling) is exactly what a long-tail column violates by
definition, and the format has no optional keys — the ceiling the
column passed is recorded in its evidence sentence, where the ratified
free-text remark records it today. The sizes
multiset is NEARLY the fact free text already publishes as its
repetition map, with one stated difference the delta prices: the
repetition map groups raw spellings while the suppressed multiset
groups FOLDED identities, so the new fact additionally reveals which
unnamed spellings share a trim-and-case identity — counts only, no
spelling, but a fact about below-floor cells the free-text map does not
carry, and owner decision 1 is priced with it. The floor-cleared LABELS
remain the delta's main body. A column past the ceiling with NO
qualifying level stays free text and publishes exactly what it
publishes today.

**What the twin writes.** The categorical generation rule verbatim:
published variants byte-for-byte at their counts, invented neutral
labels at the exact suppressed sizes, fold collisions reproduced by the
existing machinery. The twin of a long-tail column carries its real
repeated labels and a counted invented tail — against today's filler
that carries neither. Label columns draw no content words, and their
placement permutation is seeded like every column's, so bytes are fixed
by (profile, seed) exactly as for categorical columns today.

**THIS LOWERS a publication stance, priced, owner-gated (decision 1).**
Columns that today publish no value will publish their floor-clearing
spellings. The price, in full:

- At the default floor: nothing below eleven rows is ever named — the
  same bound as every label today. New is WHICH columns publish: a
  genuine prose column with eleven identical cells names that repeated
  sentence as a level. Two widenings of that sentence's own price are
  stated rather than discovered: the eleven rows are rows, not people —
  the grain is undescribed, so eleven repeated cells can belong to one
  person's repeated records, a caveat the charter already states for
  every floor-guarded fact and which now guards sentences, said in
  SECURITY.md where the floor's row arithmetic is stated; and the
  summary lists every column whose labels will be visible BEFORE
  anything is written, long-tail columns included.
- At a lowered floor: the published set widens with the floor for
  columns the detection line admits — at floor one, such a column
  publishes every level, exactly as a categorical column does at floor
  one today, and the existing lowered-floor alarm and warning cover the
  new role. What a lowered floor can NOT do, by the detection rule, is
  make a new column label-publishing: the eleven-row line does not
  move downward.
- The free-text promise — "publishes no values at all" — keeps its
  exact truth for every column that remains free text, and every
  surface that states that promise is checked against the new boundary
  in the claim-migration table's stage 6 rows.

**Document size, stated.** `suppressed_level_counts` holds one integer
per below-floor level; the bound is `n_rows`; no cap is added, honoring
the standing rule against contracting the promised domain, and the cost
is stated here rather than found later.

## P4-D6. Missing-data patterns, per column

The line against Phase 5 first, in the open: everything in this section
is a fact about ONE column's absent cells. Which cells are absent
TOGETHER across columns, and every other cross-column absence
structure, is the `missing_data_process` slot's work, reserved to
Phase 5; this plan neither fills nor reads that slot.

### P4-D6.1 The twin reproduces recorded hole spellings (decision 2)

Contract version 5 already records, per column: the exact hole
spellings at or above the floor (`missing_by_source`), the blank count
(`n_missing_blank`), and the pooled remainder (`n_missing_withheld`).
The generator today writes every absent cell empty — and a sealed
sentence of the version 5 contract (C5-9) says exactly that, so this
rule is a VERSION 6 rule, landed only at stage 6 where the version 6
contract supersedes C5-9 in the open, never as a quiet early change.

Under this decision the generator writes, per column, ONE rule:

- each `missing_by_source` spelling at exactly its count — EXCEPT a
  spelling that reads as one of the three built-in stand-in numbers,
  which stays blank (stated in the next paragraph);
- every other absent cell — the blank count, the withheld remainder,
  and any stand-in-sourced cells — empty;
- placed by the same single permutation that places everything (one
  mechanism, no new draws, placement budget unchanged), spellings
  assigned to absent slots in a fixed sorted order before the
  permutation, so bytes stay a pure function of profile and seed.

**Why stand-in-sourced cells stay blank.** The validator's absence
chain reads a reproduced TEXT hole spelling as absent by a fixed rule
of the description alone — that extension was made in Phase 3 and is
the mechanism this rule rests on. A stand-in NUMBER is that chain's
named exclusion: its absence reading runs through the producer's
outlier-and-share rule over the measured file's own values, which a
twin's generated distribution is not guaranteed to re-fire. Reproducing
stand-in numbers would therefore make the green battery contingent on a
re-judgment; leaving those cells blank keeps every reproduced cell's
absence reading deterministic. The verdict facts themselves are
already published and are not harmed: the twin report names, per
column, the stand-in cells and below-floor spellings that were NOT
reproduced and why. There is no separate sentinel-reproduction rule —
one write rule, one exception, stated once.

**The collision rule, raised with the reproduction — with no escape,
because an EXACT-OBSERVABLE fact may not carry one.** No PRESENT cell
of the twin may wear a spelling the description publishes as a hole
source for its column, and the method amendment proves this corner
EMPTY rather than naming a runtime deviation, by four arguments this
plan fixes: pinned values (endpoints, the zero stratum) are
values the source itself held, and a published hole number was absent from the
source's present cells by the declaration rule itself, so no pinned
value can collide; an interior numeric selection sits in a segment
between rungs the source itself held, so the segment is
never the single collision point and the construction steps to the
adjacent conforming value inside it (the whole-number rule steps by
one, inside a segment whose whole ends flank the collision point);
every INVENTED spelling — free-text and record-number filler,
unrepresentable numerals, AND a label role's invented variant
spellings and neutral stand-in labels for withheld levels — comes from
an unbounded family (case flips extend by trailing spaces, neutral
labels by their counter) whose candidate-rejection rule extends from
the built-in no-value list to the column's published hole set, so a
conforming alternative always exists; and a label role's PUBLISHED
spellings — its variants, written byte-for-byte — cannot equal its own
column's hole spellings, because one cell cannot have been counted
both present and absent. A shape outside these four
arguments is a defect in the method amendment, found at review, never a
deviation printed at run time. R-P2-13's
built-in-marker collision keeps its own residual entry, re-priced where
the twin now also carries deliberate marker text: deliberate and
accidental hole spellings are counted together by any re-reader, which
is what the description says they should be.

**Consequences, each landed at stage 6 with the rule:** the generation
method's absent-cell rule and the version 6 matrix move together under
counted re-seals; `missing_by_source` strengthens from REPORT-ONLY to
EXACT-OBSERVABLE with a per-spelling recount (stand-in-spelled keys
excepted, their exception stated in the matrix row); the blank and
withheld counts take a stated SUM identity — the twin's recounted blank
absent cells equal `n_missing_blank` plus `n_missing_withheld` plus the
stand-in-sourced count — because the construction writes all three
pools blank and a per-field equality would be false by construction;
`missing_by_class` stays REPORT-ONLY (its classes are not recoverable
from bytes); frozen vectors gain cases with mutants; the twin-byte
change is a changelogged D12 regeneration event with goldens
re-recorded in the same commit. The green battery proves the whole:
producer, generator, validator, zero MISSED and zero WITHHELD on
fixtures that carry reproduced spellings, pooled remainders, and
stand-in-sourced cells.

What this does NOT close, restated from where it stands: the two
permanently-open routes of R-P3-8 (a person's own word pooled below the
floor everywhere, and a person's own word on a nothing-publishing
column) are limits on what the DESCRIPTION records and remain exactly
as written; the reproduction rule can only reproduce what is recorded.

### P4-D6.2 Excel-artifact spellings join the missing table (decision 7)

The built-in missing-text table grows by the closed set of seven Excel
error literals — `#DIV/0!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`,
`#REF!`, `#VALUE!` — each a machine artifact whose folded form collides
with no human word. The pandas absent-time literal was deliberately NOT
in the ratified enumeration, because the vocabulary matches after
trimming and case folding and that literal's folded form is a person's
name, so adding it under the folded rule would silently hollow name
columns. **AMENDED by owner ruling 2026-08-19 (decision 7's TAKEN
note): the literal joins as the vocabulary's one EXACT-SPELLING
member** — it reads as a hole only on raw byte-for-byte equality with
the cell, no trimming and no case folding, one operation applied
identically wherever the vocabulary is consulted — so
the name collision the ratified text guarded against cannot arise, and
the matching rule carries exactly one stated exception, named in the
version 6 contract beside the folded rule it excepts. The criterion
that keeps `unknown` and `missing` out — a human word carries meaning
somewhere — stands unweakened for every folded member. This is a wire event: the published vocabulary is normative from
version 5, so the extension rides the version 6 bump; the
declaration-record machinery and its counts move with it; every surface
that states the vocabulary's size — including the Phase 3 plan's
residual R-P3-8 entry, a sealed governing sentence that counts thirteen
words — moves by counted re-seal in the same landing, enumerated in the
claim-migration table. `--keep-value` remains the stated route for the
table where an artifact really is data. THIS CHANGES how affected cells
read — a column of numbers with a few artifact cells stops losing its
distribution to the parse line — and the cost is one more closed list a
consumer must know, priced in the contract's disclosure-delta section.

### P4-D6.3 What missing-data patterns do NOT include here

No per-column absence-run or ordering facts (rows are unordered in the
profile's model), no dependence of a column's absent cells on values (a
relationship, Phase 5's), no reproduction of below-floor or
stand-in-sourced spellings, and no change to the five-class absence
taxonomy beyond P4-D6.2's list **(AMENDED by A-P4-1: the two built-in
date stand-ins join the judged candidates and the class map gains
their key, by owner ruling — the amendment carries the rule in
full)**. Each is either Phase 5's or priced in
P4-D13.

## P4-D7. Profile contract version 6

One version bump carries every wire change of this phase, landed whole
at stage 6. `docs/spec/profile-contract-v6.md` is written and ratified
at stage 3, before any version 6 code, carrying version 5 by reference
under the same rules version 5 carries version 4: a superseding clause
names the rule it replaces, the older documents are never edited to
change what they require, `C6-` prefixes, and a profile is governed by
exactly one version's documents.

**The delta, complete** (the contract document states each normatively;
this plan fixes the set):

1. Three new roles — `affixed_number`, `time_of_day`,
   `long_tail_labels` — through every closed enumeration: the role
   tuple, the axes table (three new rows, each role naming its own
   statistical type, `ok`, and `data`), the statistical-type
   vocabulary, the publication classes with the one named ranges-class
   exception of P4-D3 (the labels class untouched), the forbidden-key
   matrix, and
   per-role sections fixing every key with invariants and exactly one
   disposition per fact — including the time-of-day analogue of the
   datetime rules that tie the ladder's ends to the endpoints. No
   optional keys anywhere in the format, restated for the new material.
2. New facts on existing roles: `resolution_mix` as a REQUIRED key on
   every datetime block (single-form columns carry one named form);
   `month` in both the resolution and `time_precision` enumerations;
   exactly three new members of the datetime `format` enumeration —
   the closed vocabulary naming which parser family read the file, six
   members inherited and NINE after these additions **(AMENDED by
   A-P4-1: ELEVEN — the two slashed datetime members join by owner
   ruling)**, which no existing
   member may falsely cover — with their
   exact wire spellings fixed here so two implementations cannot
   diverge on a string: `slashed-iso-date` (resolution `date`),
   `iso-month` (resolution `month`), and `iso-mixed` (resolution
   `datetime`), each resolution binding stated so the
   format-to-resolution invariant stays total, and `resolution_mix`
   keyed by format-member strings with its permitted key sets closed:
   on a single-format column, exactly one key — the column's own
   `format` member — carrying the full parsed count; on an `iso-mixed`
   column, exactly the two members `iso-date` and `iso-datetime`; no
   other key set conforms; `min_length` and
   `max_length` on `numeric_unrepresentable`; and the fraction-width
   fact inside the numeric styles block.
3. The missing-text vocabulary extension of P4-D6.2, with the
   declaration-record consequences enumerated and every
   vocabulary-count surface moved.
4. The reproduction rule of P4-D6.1: the clause that supersedes C5-9,
   the one write rule with its stand-in exception, the collision rule,
   and the moved dispositions — `missing_by_source` per-spelling
   recount, the blank/withheld SUM identity stated as the identity it
   is, `missing_by_class` unchanged.
5. Settings: the block grows from fifteen keys to EXACTLY seventeen,
   and the two new keys are named here so the contract, the loader, the
   validator's consumption table and the refusal message can all be
   written and tested from this plan: `day_first` (a yes/no, default
   no) and `long_tail_minimum_level` (whose ONLY permitted value in
   version 6 is eleven, on the `declaration_matching` only-value
   precedent — the loader refuses any other, so no settings
   combination, the publication floor included, can move the detection
   line's lower bound of P4-D5 downward; the key exists so the line is
   recorded on the document's own face and a later phase can move it
   only in the open, by a contract change). No other key is added:
   the affix rule and the time-of-day rule deliberately reuse
   `minimum_parse_rate` and `small_cell_floor` and need no constant of
   their own. A sixteenth-or-eighteenth key, or a key skipped, is red
   against the contract's own enumeration in both directions.
6. Dispositions: every new fact carries exactly one class; every moved
   fact is listed with its old and new class and its recount or window;
   the completeness assertion (every emitted key has a disposition in
   the documents read together) holds with no exceptions acquired
   during implementation.
7. The disclosure-delta section states in one place everything
   version 6 publishes that version 5 withheld, each row priced:
   long-tail levels (floor-cleared spellings from columns that publish
   nothing today); the affix pair (shared cell fragments, floor-
   governed, under the named ranges-class exception); the WHOLE
   affixed-core numeric block as one grouped delta row, every fact
   named — mean, standard deviation, skewness, the sign and zero
   counts, the whole-number fact, the styles block with its fraction
   widths, and the affixed-cell count — each under the ranges-class
   treatment the same fact has on a plain numeric column today, all of
   it new for columns that were free text yesterday; core endpoints
   and
   ladder rungs of affixed columns, and clock endpoints and rungs of
   time-of-day columns — exact values, floor-free, the ratified
   ranges-class endpoint policy newly reaching columns that were free
   text; month and mixed-ISO endpoints likewise; the two
   unrepresentable lengths with the order-of-magnitude reading stated;
   the exact resolution-mix counts with the subtraction argument that
   makes a floor pointless there; the fraction widths; and the twin as
   a carrier of published hole spellings. Each row names its floor
   treatment or its justification, its SECURITY.md sentence and its
   summary sentence.
8. The version machinery: the producer and the fail-closed loader move
   together to the new version at stage 6 — one version read, no
   upgrade path, no dual support, an older document refused rather than
   converted. The older-version refusal message is rewritten for the
   new version naming and pricing EVERY option that changes what a
   description publishes, including `--day-first`, and the standing
   re-examination duty is met in the open: the "describe the table
   again" advice was declared safe only before the first release, so
   the new message is drafted against the release state at the flip
   commit — if the first release has shipped, the message stops
   assuming every reader holds the table and says plainly that a newer
   description can only come from the table's holder; the contract
   section that carries the message records that analysis either way.
9. **The claim-migration table**, stage-keyed, one row per moving
   surface sentence, on the Phase 3 precedent (its round-1 review made
   the absence of such a table a blocking item): the free-text
   "publishes no values" boundary sentences (checked, unchanged in
   truth, at stage 6); the twin-writes-absent-cells-empty sentences in
   the renderer, the summary, SECURITY.md and the changelog (retired at
   stage 6 with C5-9's supersession); the thirteen-word vocabulary
   counts on every surface plus the R-P3-8 re-seal (stage 6); the
   R-P2-1 and R-P2-2 residual ledger entries (closed/retired at stage
   6 if decisions 5 and 2 are taken); the phase statements in
   CLAUDE.md, README.md and the claim inventory (stage 2's first
   commit, after the Phase 3 closing precondition); STATUS.md's phase
   table (same commit); and the loud-decline sentences (stages 2 and
   5). A surface sentence not in the table does not move; a table row
   without its stage's commit is red by the migration battery.

**Timing against the first release, stated rather than assumed.** At
this plan's drafting no release exists (no tag, no package-index
record), so the bump's migration price is currently a changelog line.
The release is Phase 3's deliverable and may land first — the
sequencing precondition requires Phase 3's closing state to be settled
before stage 2. This plan therefore prices both orderings: before the
release, the flip costs nothing external; after it, the flip costs
strangers regenerated descriptions, and the refusal message carries the
post-release analysis of item 8. Neither ordering changes the design;
only the message and the changelog entry differ, and the implementation
takes whichever is true at stage 6.

## P4-D8. Generation method changes

Amended in place under counted re-seal at stage 4, revision advanced,
each change citing this plan:

1. **New role sections** for the three roles: affixed cells as
   `prefix + core + suffix` with cores under the existing numeric rules
   re-based on the published core facts, plus the NEW plain-number
   straggler construction for in-slack plain cells; time-of-day under
   the ordinal machinery with endpoints pinned and interior ranks by
   floor-division interpolation between them; long-tail labels under
   the label rules verbatim. The draw-budget table gains three rows
   (long-tail: zero content words like every label role; time-of-day:
   the datetime budget shape; affixed: the numeric budget shape over
   cores plus zero-word stragglers). The G11 all-different table gains
   three rows — long-tail through the label mechanism, affixed through
   the numeric mechanism over cores, time-of-day through ordinals with
   its finite-space bound — and the approximated-fields table gains the
   new roles' windowed facts, because both lists are closed and a row
   not added is a contradiction, not an omission.
2. **The absent-cell rule** (P4-D6.1): the one write rule with its
   stand-in exception, sorted-order assignment, the same single
   permutation, recounts extended to the reproduced spellings, the
   collision-rejection extension to published hole sets, and the
   written four-argument proof that no construction is ever forced onto
   a published hole spelling (P4-D6.1) — a proof obligation of the
   amendment, not a runtime deviation.
3. **Retirements:** the 400-figure invented width and its
   always-printed deviation (P4-D4.4), with the width-pinned
   fold-partner clause added in the same amendment.
4. **New facts through existing rules:** fraction widths join the value
   construction (the width-snapping rule of P4-D4.5, the
   integer-rule's shape), the style walk's quotas and the recount
   identity; `resolution_mix` changes NO generation rule — it is
   REPORT-ONLY, the twin writes every parsed cell of a mixed column at
   the finest recorded precision exactly as the ratified rule writes
   every datetime column today, and the report names the recorded mix
   as not reproduced, per column, every run.
5. **Refusal catalogue:** the closed list of four grows by exactly one
   named refusal — a time-of-day description whose distinct demand net
   of its unparsed stand-ins (`n_distinct − n_unparsed`) exceeds its
   form's finite space — with the standing
   message obligations (the profile is valid, the two facts that cannot
   both hold are named, remediation does not assume the table). The
   affixed role inherits the numeric refusals over its cores unchanged;
   long-tail inherits the label rules' non-refusing posture; the
   reproduction rule needs no refusal (its cells cannot exceed
   `n_missing` — the write rule consumes exactly the published counts,
   whose sum the contract already bounds). Any further genuinely-
   unsatisfiable shape found in implementation comes back to this
   document by amendment, not as an exception.
6. **Vectors:** every new branch lands with frozen reference cases and
   committed failing mutants, the case set and mutant table asserted
   equal, files under the fixture byte cap with the split rule, the
   oracle extended in the same stdlib-only discipline. The two recorded
   oracle debts in the identifier area (the parent-walk narrowing and
   the collision-order gap) are settled by whoever first touches that
   machinery; this plan's long-tail role reuses the label machinery
   without touching those two rules, and if implementation finds it
   must touch them, the debts land with it.

## P4-D9. Validation method changes

At stage 5: first the document's own revision 1 (the completed entry
table and the report's normative byte layout — its recorded debt), then
the Phase 4 additions, each under the standing rules:

1. Every new fact binds into the entry table's identity scheme —
   (registry fact, profile predicate, subcheck) — as executable check,
   listing, or input-side entry, total over obligations, no entry
   unbound, double-bound, or wrong-kind; every executable subcheck
   lands with a registered red case that makes exactly it miss, and
   fixtures reach every new role in both header modes so the totality
   assertions are not vacuous for them.
2. The new roles' checks mirror their generation rules: affixed columns
   re-described and compared over the core distribution, the affix
   pair, and the styles identity; time-of-day over endpoints (exact),
   interior rungs (windowed, the window arithmetic written from the
   method clause and compared with the generator's writing in the
   suite), and the one form; long-tail over the label checks verbatim.
   Windows for any new approximated fact live in the generation method
   and are cited, never restated.
3. The reproduced-hole facts take their stage-6 shape: the per-spelling
   recount subchecks for `missing_by_source` (stand-in keys excepted as
   the matrix states), the blank/withheld SUM identity as ONE subcheck
   of the stated sum, and `resolution_mix` as a REPORT-ONLY listing in
   the not-checkable census, never a subcheck. The
   absence chain itself is unchanged — it already reads published hole
   spellings as absence, which is what makes the reproducing twin's
   green provable rather than hoped.
4. The quality report's loud-decline sentences (P4-D2 item 3) enter
   this document as report-content clauses, per class, with exact-shape
   tests — the method is the normative authority on what the report
   says, so the sentences land here, not beside it.
5. The disclosure gate's envelope extends mechanically: every new
   measurement passes the membership test (published-above-a-floor
   facts gated by the floor; a fact published about no file needs an
   explicit ruling); every MISSED line carries the found value or a
   fixed keep-back sentence; no string of the measured file is ever
   printed. Nothing in this plan widens what the gate claims: it
   remains a rule about one report.
6. The corner machinery: this plan names no new plan-authorized lesser
   outcome — the affixed role reuses the numeric corners over its
   cores, and the new refusal is a refusal, never a corner. If
   implementation surfaces one, it enters as a predicate over published
   numbers with the independent classifier and the parity battery
   extended, by amendment.
7. Exit codes, verdict vocabulary, and the refusal/verdict split do not
   move.

## P4-D10. CLI, UX, and errors that speak human

One new option (`--day-first`), no new commands, no configuration
files. The option follows the established pattern in full: a
plan-ratified reason, parser vocabulary constants suite-compared to
owning modules, help text held as a testable constant, output through
the display boundary, and membership in the version-refusal message's
derived-and-priced option list in the same commit. Every new decline,
remark and refusal is a catalogued builder in the errors module with
exact-shape and reachability tests: what happened, then what to do
next, in words a person who has never programmed can act on; positions
never values on the validate path; counts never spellings in the
settings story; the affix remark and the long-tail summary lines name
columns and counts, never cell text beyond what the publication rules
authorize (a published affix or level is authorized by its floor). The
summary's pre-write listing of label-visible columns extends to the
long-tail role, so the person sees what will be named before anything
is written.

## P4-D11. Testing strategy

The standing machinery, extended — nothing bespoke:

1. **Fixtures:** the every-role table and every-withholding table gain
   columns for each new role and each new withholding path (long-tail
   suppressions, fraction-width pools, reproduced-spelling columns,
   stand-in-sourced columns, pooled-remainder columns). Goldens move
   and are re-recorded with cause comments.
2. **The no-regression battery** (the header rule, executable, in two
   parts): over the fixture corpus with the decision-7 literals absent
   or read as data, every column's role under the Phase 4 tree equals
   its role under the shipped tree, except transitions out of
   free_text into the new roles and newly-read datetime formats — each
   authorized transition asserted present so the battery cannot pass
   vacuously; and over a second fixture set holding the decision-7
   literals, every observed transition is exactly a re-reading
   consequence of those literals, each direction (label role narrowed,
   numeric role recovered) exercised by name.
3. **Loader battery:** every new invariant ships with a mutation
   refused in its own words; the battery's completeness test (every
   named rule has a mutation) holds.
4. **Reference vectors:** new cases and mutants per P4-D8.6, manifest
   entries per file, byte cap honored.
5. **Batteries:** the producer battery's permitted-line lookup extends
   to the new role groups; the disclosure battery's assertion is
   DIRECTIONAL and stated: every spelling the description publishes for
   a surface is present exactly where authorized (reproduced hole
   spellings in the twin at their counts, published levels and affixes
   at theirs), and every declared or withheld spelling is ABSENT from
   every surface not authorized to carry it — below-floor spellings,
   stand-in-sourced reproductions, settings-block text — under hostile
   fixtures; the green battery holds zero MISSED and zero WITHHELD on
   the every-role fixture through profile → generate → validate at the
   new version.
6. **Claim inventory:** the phase statements, command counts, and
   what-the-twin-carries sentences move per the claim-migration table,
   each with the commit that makes it true, never before; the
   loud-decline sentences land with exact-shape tests.
7. **Determinism:** one stream, sorted iteration on every new path, the
   conformance checklist re-run, byte-identical twins at fixed inputs
   on every CI cell including Windows. Seed-invariance claims are made
   only where the method makes them — a fully-determined column of
   identical cells — and no new-role test asserts more.
8. **Scanner and seals:** every artifact scans clean as a tracked file;
   the offline scanner's policy is unchanged (no new imports, no
   regular expressions, no locale parsers — every new reading is
   spelled out in the shared parsing module); the seal is current at
   every landing.

## P4-D12. Honest limits of this phase

- The twin's fidelity bound is still one column wide. Nothing here
  carries correlation, shared absence, grain, or any cross-column fact;
  Phase 5 exists because this phase does not do that.
- Free text remains, smaller and louder: a column no reading fits still
  yields invented filler, now labeled as such on every surface. The
  filler is still meaningless; the label is the deliverable, not a
  cure.
- Detection reads values, and values do not carry meaning. A prefixed
  code column that was free text can read as affixed quantities; a
  numeric code column can still read as counts; declarations remain the
  person's tool, and the remarks name it. No inference added here
  changes that boundary.
- The ladder model reads every axis as a line. A clock column whose
  values cluster across midnight, like a numeric column with two humps,
  is described by exact rungs whose interior the twin fills — the
  valley, or the empty middle of the night, receives generated values
  the source never held. The rungs are real; the model between them is
  the model.
- The long-tail role publishes only what clears the floor, and its
  detection line never drops below eleven rows; at the default floor, a
  mostly-unique column still publishes nothing of its values. At a
  deliberately lowered floor the role publishes more, exactly as label
  roles always have, and the alarm says so.
- Reproduced hole spellings cover only what the description records:
  below-floor spellings, stand-in-sourced cells, and the two
  permanently-open declaration routes of R-P3-8 remain exactly as
  written, and the twin report names each column's unreproduced
  remainder.
- The quality report's pass still means one thing — no checkable
  obligation was missed — and its scope statements do not widen here.

## P4-D13. Residuals

Opened by this plan, each a limit accepted rather than work forgotten:

- **R-P4-1.** Mixed-affix and case-varying-affix columns decline to
  today's paths; the one-exact-pair rule is deliberate, and the remark
  says how far the affix reading got. Censoring markers mixed among
  plain numbers (`<5` beside `12`) are this residual's second face.
- **R-P4-2.** Durations do not parse; a duration column declines with
  the extended remark. Reason: `1:30` has two readings and no floor of
  evidence settles them.
- **R-P4-3.** Decimal-comma numbers are not read: `1,23` under one
  convention is a grouping error under the other, and a silent wrong
  guess is the failure class this project deletes rules over. (Grouped
  thousands under the shipped convention ARE read, today and after this
  plan.) A declaration-based route is left for a later phase to price.
- **R-P4-4.** Dotted, textual-month, and two-digit-year date forms are
  not added: the first is day/month-ambiguous, the second is locale-
  and case-variant, the third loses the century. Each declines with the
  competing-readings remark.
- **R-P4-5.** Clock cells with fractional seconds, a leap second, or
  single-digit hours do not parse, and no JOINT clock reading exists:
  a column where neither clock form alone clears the line declines
  (an in-slack minority form rides as counted unparsed stand-ins, per
  P4-D4.2 — that is the line's ordinary arithmetic, not a decline).
  The shape is closed on purpose, and the joint reading is the named
  candidate for a later widening.
- **R-P4-6.** A column mixing month cells with full-date cells
  (`2024-03` beside `2024-03-17`) is not read; only the ISO
  date/datetime family mixes. Named here so the partial-date
  convention is a recorded decline, not a surprise.
- **R-P4-7.** Multi-valued cells (delimiter-joined lists) are read as
  the single spellings they are; splitting them is analysis, not
  description.
- **R-P4-8.** Non-ASCII digits and alternate numeric notations stay
  unread; the classifier stays single and closed.
- **R-P4-9.** Epoch-second integer columns read as counts; a remark
  names the alternative reading when the range is epoch-shaped, routing
  nothing.
- **R-P4-10.** The below-floor tail of every reproduced or published
  fact — hole spellings, sentinel candidates, long-tail levels — stays
  unwritten in the twin and unnamed everywhere, by the floor's own
  rule; stand-in-sourced absent cells stay blank in the twin by
  P4-D6.1's stated exception.
- **R-P4-11.** Free text that remains is invention, labeled; making it
  linguistically plausible is out of scope and gated by the charter's
  privacy line on source language.
- **R-P4-12.** The ISO form mix is recorded, not reproduced: a mixed
  column's twin writes every parsed cell at the finest recorded
  precision, on the R-P2-7 precedent (the lexical family is recorded,
  not kept), and the twin report names the recorded mix as not
  reproduced. Reproducing it would need a per-form construction with
  its own packing, feasibility rule and window family, priced out of
  proportion in P4-D4.3.
- **R-P4-14** (opened by amendment A-P4-3, restated at its real size on
  review item P4-C2-F2). Sentences of the twin report, the generation
  screen, the profiler summary and the quality report are held by the
  display boundary, exact-shape tests, the claim inventory and the
  golden hashes — four controls, where the profile document has a
  fifth: an enumerated grammar whose guard rebuilds every published
  sentence from parts and refuses one it cannot. A future edit to those
  surfaces can therefore add a sentence nobody enumerated, and **the
  four do not between them guarantee such a sentence is true**: a novel
  false claim in plain words, or one carrying a published label into
  prose, passes the display boundary (which makes it safe, not
  refused), passes the claim inventory (a list of known-bad shapes,
  not a reader), and moves no golden where no golden pins the surface —
  the screen and the summary have none. What narrows it in practice is
  clause 2: every sentence THIS phase adds is pinned whole, screen line
  included. Priced and accepted in A-P4-3 rather than closed, because
  closing it means moving several hundred lines of existing prose
  behind an enumeration that buys them nothing.
- **R-P4-13** (opened by amendment A-P4-1's audit). A column mixing
  numeric results with qualitative text in ONE cell space — the
  long-format panel export, where `7.2` sits beside `POSITIVE` in the
  same column — still declines to a label or free-text landing, and
  its numeric mass is not described. Serving it well needs a COMPOUND
  description: the numeric subpopulation's distribution AND the
  floor-clearing text levels AND both counts, publishing every cell's
  class so nothing is dropped — a design that must answer the review
  history that deleted majority-numeric publication (P1-R6-F7) rather
  than walk around it. That is its own future owner decision with its
  own review, named here so the terms are written before anyone needs
  them. Until then the decline is loud, and item 4 of A-P4-1 names the
  `--missing-value` route where the blocking text is a hole word.

Carried, restated at their own registers: R1, R2 (Phase 1); R-P2-1
closes under decision 5 and R-P2-2 under decision 2, each ledger entry
moving at stage 6 per the claim-migration table, else both carry;
R-P2-5, R-P2-6, R-P2-7 (the lexical date family is still not kept —
P4-D4.3 widens what is read, not what is remembered; a month-first
source still yields ISO twin dates), R-P2-8, R-P2-9, R-P2-13 (re-priced
under P4-D6.1 where taken), R-P2-14 carry; R-P3-1 through R-P3-8 carry
as written, except R-P3-8's vocabulary count, which moves by counted
re-seal with decision 7; R-P3-11 remains the owner's pending decision,
unmoved by this plan; R-P3-12 closes durably under decision 6, its
ledger entry recording which interim option A-P3-46's ruling took. The
one Phase 3 bookkeeping discrepancy this drafting found is recorded for
the owner rather than resolved here: STATUS.md states R-P3-12's ruling
as taken ("leave as is") while the Phase 3 plan, the changelog and the
pinned test record it as pending.

## Amendment A-P4-1 — the coverage-audit widenings (owner ruling 2026-08-19)

**THIS RAISES what the phase reads and lowers nothing.** After
ratification, a seven-slice audit traced one hundred seventy-five
column shapes common in health-science tables through the ratified rule
order: one hundred five read well, thirty decline loudly, thirty-five
carry the known code-as-quantity remark-and-declare risk, and five are
gaps. The owner ruled: fold the four bounded gaps into this phase now,
while the version 6 bump is already being paid and before the first
release makes vocabulary changes cost strangers a migration; record the
fifth, which needs its own design, as residual R-P4-13. The four, each
priced:

1. **Unpadded slashed dates.** Exactly four families accept one- or
   two-digit month and day fields, named by wire member so no third
   reading exists: `month-first-date`, `day-first-date`, and item 2's
   `month-first-datetime` and `day-first-datetime` — the grammar is a
   one- or two-digit month and day, a four-digit year, and the slash
   delimiter. `slashed-iso-date` stays fully padded (four-digit year
   leading, two-digit fields), and the compact family stays exactly
   eight digits, so no family overlaps another. No new format member
   for the widening itself: the family is the same parser, and the
   ten-character length rule retires for the four named families.
   Ambiguity handling is untouched: month-first tried first, the
   standing remark, and the evidence-first `--day-first` rule of
   P4-D4.6 all apply exactly as written. Cost: the calibration
   consequences P4-D3 already prices for widened readings.
2. **Slashed datetime stamps.** Two new format members with their exact
   wire spellings fixed here — `month-first-datetime` and
   `day-first-datetime`, each resolution `datetime` — reading a slashed
   date (padded or not, per item 1), one space, then a clock in the
   time-of-day rule's two forms, with `time_precision` and the
   endpoint machinery exactly as the ISO datetime member has them. The
   version 6 format vocabulary counts ELEVEN members, and P4-D7 item
   2's nine moves accordingly by this amendment's note there. Both
   members join the first-row evidence rules, the vectors, and the
   red-case tables like every widened reading.
3. **Date stand-ins, judged like the numeric ones.** Exactly two
   built-in candidate dates — `1900-01-01` and `9999-12-31` — with
   their identity fixed at the WRITTEN calendar day: a cell matches a
   candidate when its own written fields, under the column's own
   format, denote that day — no shared-clock normalization and no
   offset arithmetic enters the question, because the placeholder is a
   writing convention and the writer typed that day. Judged by the
   standing outlier-and-share rule transposed to day ordinals over the
   written days, reusing the two recorded sentinel settings; no new
   settings key. Ordering, tighter than the affix pass because a
   removal here could otherwise demote an existing datetime column:
   the pass runs only after rules 0 through 4 decline the un-removed
   column, and it ENTERS only when the non-candidate remainder itself
   clears the datetime rule's line — otherwise no cell is judged, no
   cell is removed, and the column lands exactly where today's rules
   put it. So constant and binary columns keep today's claims, an
   existing datetime column can never fall out of the role by this
   pass, and the no-regression battery's first part stays green by
   construction — two fixtures join it: the two-valued column whose
   one value is a candidate date, and the mixed column whose remainder
   misses the line. The wire, fixed here so the stage-3 contract can
   be written from this text: the absence-class map gains the one key
   `(date-sentinel)`, present on every column block like the other
   five, with the membership, sum and floor invariants restated over
   six; verdict entries carry the candidate as its canonical ISO day
   spelling, ordered with mixed candidates sorted as text, reusing the
   standing verdict and reason enumerations and the standing
   nothing-publishing withholding; both declaration records gain the
   third list `built_in_dates`, same shape and identity rules as the
   numeric list, with the declared-count identity extended over three
   lists; `--keep-value` wins exactly as today. Every consequence
   rides the version 6 bump, and the stage-3 contract, the stage-4
   method sections, the stage-5 validation readings and the affected
   shipped surfaces are enumerated in those artifacts from this
   paragraph. What this buys: a column whose
   open-ended rows are filled with a placeholder date stops publishing
   that placeholder as its exact endpoint, stops dragging its ladder,
   and stops seeding the twin with decades the source never held — the
   one audited shape where the ratified plan published wrong numbers
   with no warning.
4. **The recoverable-distribution advice.** The competing-readings
   remark of a declined column gains one clause, and its trigger is
   the arithmetic that makes the advice TRUE rather than hopeful: the
   remark names `--missing-value` exactly when removing the
   floor-clearing non-numeric folded spellings from the present cells
   would lift the surviving column to the recorded parse line —
   whole-number arithmetic over the numeric-looking count the remark
   already carries, the same count its existing sentences call written
   as numbers. Where the arithmetic does not hold, no advice fires and
   nothing implies one declaration would suffice. Advisory, routing
   nothing, built from counts the remark already carries plus the
   floor, no new settings key.

**The pricing this amendment adds, where the plan's conventions carry
it.** The disclosure delta of P4-D7 item 7 gains two rows: columns the
widened slashed families newly read publish datetime endpoints and
rungs under the standing floor-free ranges policy — the same grouped
treatment the ISO widenings already carry there — and the settings
block's `built_in_dates` lists join the vocabulary-record rows. The
claim-migration table of P4-D7 item 9 gains the surfaces that count
the built-in vocabulary or enumerate the format members, which move at
stage 6 with everything else. And three sentences of the ratified text
that this ruling makes stale move by this amendment's notes where they
stand: the Scope's "one added date format", decision 4's "three new
members", and the P4-D0 preamble's "none is an owner ruling yet".

The deliverables of items 1 through 3 land inside the stages that own
their machinery — the contract additions at stage 3, the method
sections and vectors at stage 4, validation readings at stage 5, the
flip at stage 6 — and their batteries join the acceptance criteria of
those stages as if written there. Item 4 is a remark and lands with
P4-D4.7's. On whose authority: the owner's, ruled 2026-08-19 with the
costs above stated and accepted; no review verdict and no implementer's
judgment stands behind it. A focused external verification of this
amendment's text was run the same day and returned
STANDS-WITH-CORRECTIONS; its six corrections — the remainder-clears
entry condition, the completed stand-in wire, the four-family
unpadded enumeration, this pricing paragraph, the raw-exact matching
of decision 7's member, and the truth-preserving advice trigger — are
applied in this text, and the record is
`docs/plans/reviews/phase-4-amendment-a-p4-1-verification.md`.

## Amendment A-P4-2 — the invention class is settled by cells, not by the role alone

**THIS RAISES the accuracy of a sentence and lowers nothing** (stage 2
code review round 1, item P4-C1-F3). P4-D2 draws its three classes by
role and by published suppression facts, and at one edge that reading
prints a falsehood: a label column every level of which the floor held
back publishes no spelling at all, so every present cell of its twin is
a neutral stand-in — yet the role-based reading files it under
partly-invented, and item 2's count then tells the reader that some of
that column's cells are values their description publishes. There are
none. The same edge is reachable a second way, with no suppressed level
at all: a published label whose every spelling sits below the floor
carries `variants` empty and `variants_withheld` covering its rows, and
the generator invents every spelling of it.

The class is therefore settled in two steps, and this is the ratified
rule: the ROLE opens a class — publishing-nothing roles and declared
columns open the everything class, label roles open the held-back
class, and the counted-stand-in roles open the uncarried class — and
the CELLS settle it, because item 2's count is a count of cells: where
the invented cells of a column are all of its present cells, the column
is in the everything class however its role publishes; where there are
none, it is in no class. The empty-column carve-out is unchanged and
still tested first. Cost: one comparison per column and one more shape
in the batteries. What it buys: the count means what it says on every
description a producer can write, not only on the ones whose edges
nobody reached.

## Amendment A-P4-3 — the enumerated-sentence rule is the profile document's

**THIS LOWERS an obligation this plan wrote wider than it can hold, on
the owner's authority, and prices it** (stage 2 code review round 1,
item P4-C1-F5). P4-D2's closing paragraph says every new sentence is
"built through the enumerated grammar (a new note form plus a rendered
branch per sentence — no free-form text can be published)". Read
literally that governs the twin report, the screen and the profiler
summary as well as the profile, and stage 2's sentences are ordinary
first-party prose assembled where the surrounding prose is assembled.
The reviewer is right that the sentence as written does not
distinguish them.

**What the grammar is for, which is why it does not reach here.** The
note grammar exists so that no VALUE of somebody's table can be
interpolated into a sentence of the PROFILE — a document that travels,
whose every leaf the publication guard rebuilds from enumerated parts
and refuses if it cannot. Its arguments are whole numbers and this
package's own words for exactly that reason. The twin report and the
summary are not that document: they already print column names,
counts, labels and recorded sentences by design, each through the
display boundary, and the guard that rebuilds a profile leaf has
nothing to rebuild here. Putting report prose through the grammar
would not close a leak — there is none to close — and would move
several hundred lines of existing sentences behind an enumeration that
buys them nothing.

**So the rule is scoped, and the scoping is the lowering.** The
enumerated-sentence obligation governs sentences of the PROFILE
DOCUMENT, where it already governed before this plan. Sentences of the
twin report, the generation screen, the profiler summary and the
quality report are governed instead by four controls, named here with
what each one actually does — **stated at their real strength, because
the first draft of this amendment claimed they catch "an overclaiming
or value-bearing sentence" and they do not** (review item P4-C2-F2):

1. **The display boundary** makes every value on those surfaces safe to
   print. It does not decide whether a value belongs there: a published
   label interpolated into a new sentence would be rendered safely, not
   refused.
2. **Exact-shape tests** pin the sentences that have them, whole. Every
   sentence this phase adds is pinned that way, the screen line
   included; a sentence a later phase adds is pinned only if its author
   writes the test.
3. **The claim inventory** walks those files as running text and reds
   on the claim shapes it enumerates — the retired provenance forms,
   the stale wire version, the unscoped retention denial, the phase
   promises. It is a list of known-bad shapes, not a reader: a novel
   false sentence in plain words is not on any list.
4. **The golden hashes** move on any change to the report, description
   or quality-report bytes, which forces a person to re-record and say
   why. No golden pins the screen or the summary.

**What it costs, stated rather than left to be found:** a future edit
to these surfaces can introduce a sentence nobody enumerated, and the
four controls do not between them guarantee it is true. A novel false
claim in plain words, or one carrying a published label into prose,
passes every one of them unless it happens to match an inventory shape
or move a pinned byte. That is a real gap and it is wider than the
"merely useless sentence" the first draft admitted to. It is residual
R-P4-14. What it buys: the plan stops requiring an architecture the
product does not have and would not benefit from, and says instead
what actually holds these sentences — and what does not.

## Amendment A-P4-4 — the branch-first history, authorized and priced

**THIS LOWERS a sequencing obligation, on the owner's authority, and
prices what it cost** (owner ruling 2026-08-19; stage 2 code review
items P4-C1-F7, P4-C2-F3, P4-C3-F3, raised at every round and correctly
declined by the implementer because closure is an owner act).

**What the plan required.** The sequencing preconditions say Phase 4
implementation begins only after the owner settles Phase 3's closing
state, and that the phase ledger, the README status line and the
pinned claim statements move in stage 2's FIRST commit — so that the
ledger writes something true about Phase 3 at the moment it writes
Phase 4 into the present tense.

**What happened instead.** Stage 2 was built and committed first, on
the branch `phase-4-plan`, while every phase-status surface still said
Phase 3 was current and Phase 4 had not started. Phase 3's closing
state was settled afterwards, on 2026-08-19, by the owner act recorded
in that plan's own closure section. The reviewer's point stands and is
why this amendment exists rather than a quiet correction: a closure
taken today cannot make a commit already written have carried the
statements, so the history cannot be brought into line with the
sentence — the sentence has to be amended, in the open, or the phase
proceeds on a rule it visibly broke.

**What is authorized.** The build-then-settle order for stage 2 only,
as it actually happened, with the phase statements moving in the
commit that lands this amendment rather than in stage 2's first. The
precondition stands unchanged for every later stage: stages 3 through
7 begin only with the phase state already true on every surface.

**What it cost, stated rather than left to be found.** For the length
of one branch — from stage 2's first commit to this one — the
repository's own surfaces misdescribed which phase it was in, while
its changelog described Phase 4 work as done. The exposure is bounded
by three facts, each checkable: nothing was merged to the default
branch in that window, so no reader outside this branch could meet the
contradiction; nothing was released, so no user could; and the
contradiction was found by review rather than by a person relying on
it. What it would have cost had any of those three been false is
exactly what the precondition exists to prevent, and the precondition
keeps its full force for every remaining stage.

**What this amendment does NOT do.** It does not close Phase 3's
release, reassign it to this phase, or license any surface to say
synthtwin has been released. It does not weaken the requirement that
the four phase-status surfaces agree — they are moved into agreement
by the same commit that carries this text. And it does not make stage
2 review-ratified by owner act: stage 2 earned its own RATIFY from the
implementation review at round 5, and this amendment settles only the
process gate that stood beside it.

## Acceptance criteria

1. Every owner decision of P4-D0 is recorded in this plan — taken or
   declined, dated — before stage 3's contract, which encodes all
   eight, is ratified; a declined decision's sections are struck by
   amendment with their residual entries written before any artifact
   encoding them is ratified.
2. The artifacts of the sequencing section are ratified in order; the
   contract v6 and method amendments land under counted re-seals; the
   governing set and every guard list grew by this plan at its
   ratification; the phase-close audit confirms each introducing commit
   carried its seal; the Phase 3 closing precondition was met before
   stage 2 and the phase statements moved with it.
3. The loud decline is total over its three classes: every
   fully-invented column, every label column with invented cells, and
   every column with counted stand-in cells carries its class's
   sentence on the twin report; the two-part count — columns holding
   only invented values, and columns holding some — prints at generate
   time; the quality report carries its per-class sentences for all
   three classes from the amended validation method; each with
   exact-shape tests, and
   no surface anywhere still implies such content is measured beyond
   its published facts.
4. The no-regression battery of P4-D11.2 is green in both parts: at
   fixed readings, no fixture column changes role except free_text
   into a new role or a newly-read datetime format; and under the
   decision-7 literals, every transition is a named re-reading
   consequence, both directions exercised.
5. The taxonomy after P4-D3 is total and ordered: three new roles
   through every closed enumeration with the completeness tests green;
   every threshold a recorded setting; the settings table and the
   validator's consumption of it equal in both directions; the
   first-row evidence consequences re-calibrated and tested.
6. Producer → generator → validator at the new version: zero MISSED and
   zero WITHHELD on the extended every-role fixture in both header
   modes; every new executable subcheck has a registered red case that
   fails exactly it; the directional disclosure battery of P4-D11.5
   holds under hostile fixtures.
7. The reproduction rule holds exactly as stated: per-spelling recounts
   equal the published `missing_by_source` (stand-in keys excepted and
   blank), the blank/withheld SUM identity holds, no present twin cell
   wears a published hole spelling — the corner proven empty by the
   method amendment's four arguments, with no runtime escape — and the
   twin report names each column's unreproduced remainder.
8. Every new generation branch has frozen reference cases with
   committed mutants, case set and mutant table equal; goldens
   re-recorded with cause comments in the same commits that move bytes;
   regeneration events changelogged under D12.
9. The version-refusal messages are exact-shape tested, name and price
   every publication-changing option including `--day-first`, and carry
   the release-state analysis of P4-D7 item 8 as of the flip commit;
   the claim-migration table of P4-D7 item 9 is fully executed, each
   row in the commit its stage names.
10. Every artifact scans clean as a tracked file; the seal is current;
    CI green on every cell including Windows; the claim inventory green
    at every stage.

## Review protocol for this phase

Plan and specification reviews before the artifacts they anchor; code
review against the ratified texts after implementation. Every review
ends with an explicit verdict — ratify, ratify-with-conditions with
each condition bounded and verifiable, or reject with the blocking
items named — and a list of what was checked. Up to five rounds per
artifact, stopping early when remaining items are wording rather than
control gaps.

## Review record

- **Internal adversarial pass (maintainer-internal, 2026-08-19):** six
  independent reviewers attacked revision 0 along six lenses — contract
  coherence, generation method and determinism, validation method,
  privacy and disclosure, taxonomy and detection, process and guard
  compliance — returning seventy-five items, eight blocking. Revision 1
  is the repair; the structural changes: the reproduction rule moved
  from an early no-wire-change stage into the version 6 landing behind
  a C5-9-superseding clause; the three new roles moved AFTER the
  categorical rule under an executable no-regression invariant; the
  long-tail detection line was decoupled from a lowered floor; the
  affixed split rule was made a total function with an exact-pair
  identity, sentinel judging over cores, and named straggler
  constructions; the sentinel-reproduction rule was replaced by one
  write rule with a stated stand-in exception and a collision-rejection
  extension; the blank-count strengthening became a stated SUM
  identity; the time-of-day shape was closed against the leap second
  and fractional seconds with the ladder-ends invariant stated; the
  pandas absent-time literal was dropped from the vocabulary extension
  for its folded name collision; the claim-migration table, the
  quality-report sentences' method routing, the phase-ledger
  precondition, artifact-level decision gating, and the disclosure
  delta's endpoint rows were added. The pass is maintainer-internal
  working material; this plan is self-contained and the public record.
- **Plan reviews (this document):** recorded here round by round; the
  full reviews are `docs/plans/reviews/phase-4-plan-review-round-N.md`.
  - **Round 1** (2026-08-19) — **REJECT**, twelve items P4-P1-F1 to
    P4-P1-F12, seven blocking. Revision 2 applies repairs for all
    twelve, **verification pending**:

    | item | answered in |
    |---|---|
    | P4-P1-F1 an order-swapped day-first reading silently reverses a column against its one contrary cell | P4-D4.6 rewritten evidence-first: the reading that parses strictly more cells wins, the declaration decides only the tie, and the override direction carries a new remark |
    | P4-P1-F2 the new date readings had no value in the closed datetime format vocabulary | P4-D7 item 2: exactly three new format members with their resolution bindings, the format-to-resolution invariant kept total |
    | P4-P1-F3 the time-of-day refusal rejected a description its own source satisfies | P4-D4.2 and P4-D8.5: the infeasible shape is distinct demand NET of unparsed stand-ins past the form capacity |
    | P4-P1-F4 sentinel judging and affix detection had no coherent order | P4-D4.1: the ratified order kept — eligibility widened to the affixed reading, judged cores removed and the column re-tallied BEFORE any role test; the below-floor consequence stated |
    | P4-P1-F5 repeating decimal-cored token columns dodged every conditional code remark | P4-D4.1: the remark is standing on every affixed column, naming the pair and the `--identifier` route, because no shape test separates codes from measurements |
    | P4-P1-F6 the suppressed multiset's folded grouping was priced as "the same information" | P4-D5 and decision 1: the folded-vs-raw difference stated and priced as its own delta row |
    | P4-P1-F7 width facts over all present cells could publish a text straggler's length as "magnitude" | P4-D4.4: the two lengths range over numeric-looking cells only |
    | P4-P1-F8 the pooled fraction-width remainder had no writing or window rule | P4-D4.5: pooled cells written at their own value's canonical spelling on the G6.4 precedent; per-width at-least/at-most-plus-pool window fixed in the method and cited |
    | P4-P1-F9 the settings enumeration was open-ended | P4-D7 item 5: exactly seventeen keys, the two new ones named, no affix constant exists |
    | P4-P1-F10 the quality-report invention sentence asserted provenance the checker cannot know | P4-D2 item 3 rewritten provenance-neutral: sentences about the description and what a generated twin would hold |
    | P4-P1-F11 mixed clock forms both took and had to decline the role | P4-D4.2: one form must clear the line, other-form cells are counted unparsed stand-ins within the slack, no joint clock reading exists |
    | P4-P1-F12 affixed_number had no single publication class | P4-D3: ranges class, with one named matrix-confined exception for its two affix keys; the exact-one-class invariant kept |

  - **Round 2** (2026-08-19) — **REJECT**, eleven items P4-P2-F1 to
    P4-P2-F11, seven blocking. It verified eight round-1 repairs
    closed (F3–F7, F9, F10 and, in substance, F1/F2 as narrowings) and
    reopened F11 and F12 where revision 2 left stale sentences.
    Revision 3 applies these repairs, **verification pending**:

    | item | answered in |
    |---|---|
    | P4-P2-F1 an equal-count tie with evidence in both directions was silently called ambiguous | P4-D4.6: the remark is written over the evidence — four counts, three stated shapes, the self-contradicting column reported as one |
    | P4-P2-F2 the three format members had no exact wire spellings | P4-D7 item 2 fixes the literal strings and the resolution_mix key vocabulary |
    | P4-P2-F3 clock interpolation ran in an ordinal space the published form cannot spell | P4-D4.2: the ordinal unit is the form's own — minutes for the minute form, seconds for the second form — the datetime resolution-sets-the-unit rule transposed |
    | P4-P2-F4 mixed-ISO form quotas were incompatible with datetime-resolution ordinals | P4-D4.3: resolution_mix is REPORT-ONLY on the format-fact precedent; the twin writes the finest form; the report names the mix as not reproduced; residual R-P4-12 |
    | P4-P2-F5 fraction-width quotas had no deterministic value-preserving allocation | P4-D4.5: width snapping as a published-fact-driven value adjustment on the integer-rule precedent, largest-first assignment by the styles walk, pooled cells unsnapped |
    | P4-P2-F6 sentinel removal could drop a column out of the affixed role silently | P4-D4.1: the fall-through mirrors the shipped numeric behavior and is loud — the extended remark states the removal count whenever removal moved the column across a line |
    | P4-P2-F7 P4-D7 still carried the labels-widening sentences P4-D3 retired | P4-D7 items 1 and 7 now name the ranges-class exception; the labels class is untouched everywhere |
    | P4-P2-F8 the mixed-clock residual contradicted P4-D4.2 | R-P4-5 rewritten: an in-slack minority form is the line's ordinary arithmetic; only a column neither form clears declines |
    | P4-P2-F9 an EXACT-OBSERVABLE hole fact carried a named-deviation escape | P4-D6.1: the collision corner is proven empty by four written arguments; the escape is deleted from the rule, P4-D8.2 and acceptance criterion 7 |
    | P4-P2-F10 decision 8 was allowed after the contract that encodes it | the sequencing precondition and acceptance criterion 1: all eight decisions precede stage 3 |
    | P4-P2-F11 the long-tail detection key had no closed permitted range | P4-D7 item 5: its only permitted value in version 6 is eleven, on the only-value precedent; the loader refuses any other |

  - **Round 3** (2026-08-19) — **REJECT**, seven items P4-P3-F1 to
    P4-P3-F7, four blocking. It verified seven round-2 repairs closed
    (F3, F4, F6–F8, F10, F11), narrowed F1, F2 and F5, and kept F9
    open through the label-invention gap. Revision 4 applies these
    repairs, **verification pending**:

    | item | answered in |
    |---|---|
    | P4-P3-F1 the clock ladder reads a circular day as a line | stated as the ladder model's own bound, at the fact (P4-D4.2) and in P4-D12 beside the bimodal-numeric case it equals; rungs stay exact |
    | P4-P3-F2 width snapping ran after the exact-fact safeguards | P4-D4.5: snapping runs inside value construction with four rules — pinned values never snapped, sign class and zero-ness preserved, stratum merges routed through the amended distinctness envelope |
    | P4-P3-F3 affix-based sentinel eligibility could re-role a binary column | P4-D4.1: the new eligibility runs only after rules 0–7 decline the un-removed column; the shipped numeric pass is untouched; no-regression holds by construction |
    | P4-P3-F4 the collision proof forgot invented variants and neutral labels | P4-D6.1: every invented spelling, label inventions included, comes from an unbounded family under the extended rejection rule; the published-variant argument stands separately |
    | P4-P3-F5 resolution_mix had no conforming keys outside the ISO family | P4-D7 item 2: closed key sets — the column's own format member on single-format columns, exactly the two ISO members on iso-mixed |
    | P4-P3-F6 the remark shapes did not partition unequal-but-contradictory evidence | P4-D4.6: two independent clauses — how the winner was chosen, and the both-directions conflict whenever both only-counts are nonzero |
    | P4-P3-F7 first-row evidence was unstated for the new readings | P4-D3: the record-evidence rule extends to affixed numbers and clock times by the same shape it has for numbers and dates, calibration re-run |

  - **Round 4** (2026-08-19) — **REJECT**, nine items P4-P4-F1 to
    P4-P4-F9, five blocking. It verified five round-3 repairs closed
    (F1, F3–F6), narrowed F2, and kept F7 open through the
    negative-evidence wording. Revision 5 applies these repairs,
    **verification pending**:

    | item | answered in |
    |---|---|
    | P4-P4-F1 the rule order put declared identifiers ahead of the ratified empty exception | P4-D3: empty settles first, the declaration wins right after, exactly as the contract's axis rules and the shipped producer have it |
    | P4-P4-F2 decision 7's re-reading transitions broke the universal no-regression rule | the header rule and P4-D11.2: a named, bounded reading-layer exception with its own two-part battery; decision 7's cost line and acceptance criterion 4 carry it |
    | P4-P4-F3 the record-evidence repair was a negative test that protected nothing | P4-D3: two POSITIVE membership tests — an affixed number wearing the column's pair, a clock time in the column's form — each evidence of a record, stop-and-ask |
    | P4-P4-F4 level_ceiling on the long-tail role was left ambiguous | P4-D5: the four shared label keys under B1–B8, explicitly WITHOUT level_ceiling, whose invariant a long-tail column violates by definition; the passed ceiling lives in the evidence sentence |
    | P4-P4-F5 the affixed-core numeric block was missing from the priced delta | P4-D7 item 7: one grouped delta row naming every fact of the block; decision 3's cost line carries it |
    | P4-P4-F6 pinned values had no deterministic width-quota selection | P4-D4.5: pinned cells walked minimum, maximum, zero, each taking the largest still-unfilled width it fits, fixed in the method |
    | P4-P4-F7 the third invention class had no quality-report sentence | P4-D2 item 3: the uncarryable-cells sentence, per column, with its counts |
    | P4-P4-F8 the screen count read "0 of 1" over a twin holding invented labels | P4-D2 item 2: a two-part count — columns holding only invented values, and columns holding some — each half saying what it counts |
    | P4-P4-F9 "six-value vocabulary" contradicted the three additions | P4-D7 item 2: six inherited, nine after the additions |

  - **Round 5** (2026-08-19), the final abbreviated verification —
    **RATIFY revision 5.** All nine round-4 repairs verified closed by
    replaying the round's own counterexamples against the repaired
    rules: the all-absent declared column settles empty first; the
    error-literal transitions are the named, battery-tested
    reading-layer exception; the headerless price and clock files are
    stopped-and-asked under the positive membership tests; the
    long-tail block carries the four shared label keys without the
    ceiling key; the affixed-core block is a grouped, priced delta
    row; the endpoint width tie has one answer; the stand-in class has
    its quality-report sentence; the screen count is two-part; the
    format vocabulary counts nine. No review items, no conditions.

  The five plan reviews are in `docs/plans/reviews/` as
  `phase-4-plan-review-round-1.md` through `-round-5.md`.

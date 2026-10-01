# Phase 5 — relationships: what the twin carries across two columns

**Status:** revision 3, 2026-09-11 — **DRAFT, not ratified.**
Revision 1 was written the day Phase 4 closed. Revision 2 recorded the
owner's ruling on P5-D0.2 (**DECLARED**). **Revision 3 is the repair of
plan review round 1, which returned REJECT with thirteen items, six of
them blocking, and which was right about all six.** The record is
`planning-notes/reviews-p5-plan/verdict-round-1.md`. Nothing may be
built from this document until a further round ratifies it.

**THREE THINGS THIS PLAN ASSERTED AND HAD WRONG**, named here rather
than quietly corrected below, because a plan that hides its own repairs
teaches the next reader nothing:

1. **That an order constraint could be imposed on top of placements
   that already hold.** It cannot. A pairing satisfying
   `ended_on ≥ started_on` exists *exactly* when the two columns'
   SORTED values satisfy it at every rank, and no permutation of rows
   repairs a rank violation. Revision 3 replaces the assertion with a
   constructive method (section 3.6) and states its bound.
2. **That correlation was deferred because it is mechanically hard.**
   The opposite is true: permuting whole column cells preserves every
   marginal fact EXACTLY and changes the correlation, so correlation is
   the mechanically cheap one. Formulas are the expensive ones, because
   they move values rather than order. The deferral stands on the
   owner's priority — code runs unchanged first — and section 1 now
   says only that.
3. **That the owner's standing disclosure position covered a
   cross-column fact.** It does not, and contract version 6 says so in
   as many words: the floor ruling "is a ruling about MARGINAL
   publication… were a later version to publish anything that crosses
   two columns, the argument above would not carry to it, and the
   default would have to be decided again on its own facts." It was
   decided again, on 2026-09-11 (P5-D0.3 below).

**Charter (CLAUDE.md):** cross-column structure and the quality report
at full strength. This is the phase the twin's one-column-wide bound
waits on.

**Inherited:** sixty-six register entries carried by name from Phase 4,
grouped in that plan's closure section. They are not this phase's scope
and are not silently folded into it; each is taken up, deferred again,
or closed, by name, in the landing that touches its area.

---

## 0. What is broken today, measured rather than argued

Measured on 2026-09-11, on an event table of 300 rows — 100
subjects, three events each, with `started_on`, `ended_on`,
`days_open`, `units`, `rate` and `total` — profiled with
`--identifier subject_id` and generated at seed 7.

| what a person would check | real table | twin |
|---|---|---|
| rows where the end date precedes the start date | 0 | **137 of 300** |
| rows where `days_open` disagrees with the two dates | 0 | **299 of 300** |
| rows where `total` disagrees with `units × rate` | 0 | **299 of 300** |

**That is the phase in three numbers.** Nearly half the twin's rows
hold a span that ends before it starts. Any elapsed-time computation
returns negative numbers; code that filters `days_open > 0` silently
drops half the twin; a mean duration is meaningless. Both derived
columns disagree with what they are derived from, in every row but one.

**None of this is dishonest today**, and that matters for how the phase
is sold. The twin's own report says it, first and unmissably: "EVERY
COLUMN WAS BUILT ON ITS OWN … not a later date costing more", and
"EVERY ROW WAS BUILT ON ITS OWN". The tool declares the bound it is
inside. Phase 5 lifts the bound; it does not repair a lie.

### 0.1 One thing already works, and the report says otherwise

**The distribution of rows-per-subject is reproduced exactly.**
Measured on a second table of 335 rows and 100 subjects with uneven
event counts:

| events per subject | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| real | 32 | 17 | 20 | 13 | 18 |
| twin | 32 | 17 | 20 | 13 | 18 |

This is not luck. The identifier role publishes
`n_distinct_by_occurrences` — the multiset of how often each identity
repeats — and the generator reproduces it. It is a per-column fact and
therefore inside Phase 4's bound.

**So the twin's report carries a FALSE clause.** It says: "If your
table holds several rows per person, per visit or per site, **the twin
does not**: its rows are independent of each other." The twin does. The
group SIZES are exact; what carries nothing is WHICH rows share a
subject — a subject's rows hold unrelated dates, scores and outcomes,
and which identity gets the eight-visit group is arbitrary.

The direction of the error is the safe one — it understates what the
twin carries — but it is still a sentence a reader acts on, and a
researcher with a repeated-measures design could discard the twin as
useless on it when the group-size distribution they need is exact.
**Opened as R-P5-1 and repaired in landing L24, before any relationship
content is designed**, because a phase that begins by adding facts to a
page that misstates the facts it already has begins wrongly.

---

## 1. The shape of the phase

Eight slots are reserved in the profile's `relationships` manifest —
`deterministic`, `grain`, `hierarchy`, `keys`, `missing_data_process`,
`statistical`, `temporal`, `validation_targets` — each `null` today,
each refused non-null by the loader (invariant S12). Filling any one
advances `profile_version` to 7.

**This phase does not fill all eight, and says so at the top rather
than discovering it at the end.** Phase 4's own lesson, bought at the
cost of a fourteen-day estimate that took twenty-four: a phase that
opens work faster than it closes it does not end. **Phase 5 fills TWO
slots** and reserves the rest:

| # | slot | what it buys the person |
|---|---|---|
| 1 | `temporal` | two event columns keep their order: no span ends before it starts |
| 2 | `deterministic` | a column derived from others agrees with them |

**`grain` LEFT THIS PHASE at revision 3**, on review round 1 item 7,
and the reason is worth keeping: the identifier role already reproduces
the multiset of group sizes (measured, R-P5-1), so a `grain` slot that
only said "one row is one event" would add **no measurable obligation
to anything** — a label with no check behind it. Making it measurable
means naming within-group structure, which is its own design and its
own phase. Reserved, not abandoned.

**Not in this phase, and reserved:** `statistical`, `grain`,
`hierarchy`, `keys`, `missing_data_process`, `validation_targets`. Each
stays `null`, each keeps its loader refusal, and the quality report
continues to check no cross-column fact it is not handed. **A later
phase fills them; this plan neither fills nor reads them.**

**Why correlation is NOT first**, since it is the word a statistician
reaches for — and the mechanical argument this plan first gave was
WRONG, so only one reason survives.

*The withdrawn argument*: that reproducing a correlation moves every
value of both columns while an order constraint can be imposed on
placements that already hold. Both halves are false. **Permuting whole
column cells preserves every marginal fact exactly and changes the
correlation**, so correlation is the mechanically CHEAP one; and an
order constraint cannot be imposed on independent placements at all
(section 3.6).

*What stands*: the owner's first goal is that **code developed on the
twin RUNS UNCHANGED on the real table**. A span that ends before it
starts and a derived column that disagrees with its sources break
running code — negative durations, silent row drops, failed
assertions. A weakened correlation weakens a RESULT, and the twin
already says in its first limit that a number computed from two of its
columns means nothing about the real table. **That is a priority
argument, not a difficulty argument, and the owner may overturn it.**

---

## 2. Owner decisions (P5-D0)

None of these is an implementation detail; each changes what the tool
does to a person's data.

**P5-D0.2 — DECLARED. Taken by the owner on 2026-09-11.** A
relationship reaches a description because a person said so, and by no
other route. **Synthtwin never decides from the values that
`ended_on ≥ started_on` always holds.** That would be a guess of
exactly the kind review item P1-R6-F7 deleted for columns, and the
failure mode is not hypothetical: a constraint that holds in three
hundred rows by chance becomes a constraint the twin enforces for ever,
and a person who never asked for it cannot see that it was applied.

*One half of this is the assistant's reading and is flagged as such*:
the owner answered the word "declared", and the plan takes that to
permit synthtwin PROPOSING a candidate in the questions file, because a
proposal is asking rather than guessing and the owner's standing
position is "it's better to ask the user than make wrong guesses" and
"we can make question to the user everytime we need to". **A proposal
is never applied unanswered.** If the owner meant that synthtwin should
not even propose, this paragraph is the one to strike and section 3.5
loses its second half.

**The other three are TAKEN AT THE PLAN'S RECOMMENDATION and are
reversible.** They are written as decisions rather than questions so
the phase can move; each names what would overturn it.

1. **The three slots and their order** — `temporal`, then
   `deterministic`, then `grain` (section 1). Taken on the measurement
   of section 0. **Overturned by**: the owner preferring correlation
   first, which is the obvious alternative and which section 1 argues
   against in terms that can be disagreed with.
2. *(taken by the owner, above)*
3. **What a relationship costs in disclosure** — a published constraint
   is a fact about the real table and joins the disclosure inventory
   with its own row and its own price (section 4). Taken on the owner's
   standing position, answered the same way three times in Phase 4:
   a fact that identifies nobody and names no value is worth the
   fidelity it buys. A constraint names no cell, no value and no group.
   **Overturned by**: an institution that treats "this never happens in
   my data" as disclosive.
4. **The twin MAY fail to meet a declared relationship, and says so.**
   A constraint and a per-column distribution can be jointly
   unsatisfiable. **The per-column facts win**, the twin's report names
   the constraint and counts the rows that violate it, and the quality
   report does the same. The reverse — bending a published distribution
   to satisfy a constraint, silently — is refused. **Overturned by**:
   the owner preferring the constraint to win, which would mean a twin
   whose published counts are wrong in a way the report would then have
   to name instead.

---

## 3. The landings, in order

Each ends in a commit, with ONE adversarial review round, the scope
frozen at this document, and anything the round finds beyond the
landing recorded as a residual and carried. That is the Phase 4 close's
protocol and it is adopted here from the start rather than after a
fortnight.

| # | landing | what it is |
|---|---|---|
| L24 | **the false clause** | R-P5-1: the report says the twin holds no several-rows-per-person when it holds exactly the real distribution. Repaired before anything is designed. No slot, no version bump. |
| L25 | **the plan's own review** | this document through adversarial review, the P5-D0 decisions taken, revision 2 ratified |
| L26 | **the method, written and reviewed FIRST** | the public method clause for the rank construction of 3.6.2 and the recomputation of 3.6.3 — the repair window, the search bound, the arithmetic, the composition refusals — with frozen reference cases. **No arithmetic is implemented before this round ratifies it** (round 1 item 9) |
| L26a | **version 7 and the seam** | the contract's version bump, the `temporal` slot's shape, the compatibility matrix of acceptance criterion 2, and the generator's one dispatch seam opened. Producer, generator and validator move together for each slot, so no tree ever loads a relationship it neither enforces nor checks |
| L27 | **`temporal`, declared** | two date columns keep their order in every row of the twin; the report entry of criterion 6 |
| L28 | **`deterministic`, declared** | a target recomputed from its sources, its own moved facts named |
| L30 | **the quality report** | `validate` checks the filled slots, with red cases, and says plainly which cross-column facts it cannot check |
| L31 | **the record and the close** | CHANGELOG, STATE, the closure section. SECURITY's version-7 entry lands at L26a, not here |

---

## 3.5 How a relationship is declared, since it is only ever declared

**Two routes, and they are the two Phase 4 already built for columns.**
Nothing new is invented here; a relationship is declared the way a code
column is declared, because a person who has learnt one has learnt the
other.

**Route 1 — on the command line.** One option per slot, named for what
a person would say out loud rather than for the slot:

```
synthtwin profile visits.csv --in-order started_on,ended_on
synthtwin profile sales.csv  --derived "total = units * rate"
synthtwin profile visits.csv --one-row-per subject_id
```

* `--in-order A,B` — B is never before A, in any row. Repeatable.
* `--derived "C = A <op> B"` — C is computed from A and B, with a
  closed set of operators fixed by the contract and no expression
  language. **An expression language is refused outright**: it is the
  dynamic-code seam principle 3 forbids, and a grammar a person can
  write is a grammar synthtwin has to evaluate.
* `--one-row-per COLUMN` — the grain: one row of this table is one of
  whatever that column identifies.

**A DECLARATION PERSISTS THE WAY A COLUMN DECLARATION DOES** (round 1
item 12). It is recorded in the settings block, it is printed in the
"to repeat this run" line beside `--code` and `--identifier`, it is
named in the version-refusal message that lists every
publication-changing option, and it survives answering the questions
file, re-profiling, generating and validating — with `--out-dir` and
`--replace`. Where a command-line declaration and an answers-file
answer name the same target, **the answers file wins**, on the rule
Phase 4 already settled for columns: the file is the newer statement.
Source compliance is re-measured on every profiling run, never carried
forward from an earlier one.

**Route 2 — in the questions file, which the person fills in.** The
file Phase 4 ships already names the columns synthtwin could not
settle. It gains a section for relationships it can PROPOSE:

* two date columns where one is never before the other **in the real
  table** — proposed, with the count of rows the observation rests on;
* a numeric column whose values equal a closed-set operation on two
  others in every row — proposed, with the operator named;
* a declared identifier column whose repeats make the table look like
  several rows per subject — proposed as a grain.

**A proposal is a QUESTION and never an answer.** It is written into
the file with `your_answer` blank, exactly as a column question is, and
`--answers` turns a filled-in answer into the declaration. An
unanswered proposal changes nothing: the slot stays `null` and the twin
is built as it is today. That is what P5-D0.2 rules and it is the whole
difference between this and detection.

**AND A PROPOSAL MAY NOT CLAIM TO HAVE FOUND A RELATIONSHIP** (round 1
item 6, which is right that the person controlling application does not
make the semantics true). Two unrelated date columns can satisfy an
order in three hundred rows by chance; confirming that observation does
not establish what the columns MEAN. So a proposal states what was
OBSERVED and never what is true: how many eligible rows behaved that
way, that synthtwin cannot tell a rule from a coincidence, and that
observed agreement guarantees nothing outside the described table. It
offers an explicit "no" as an answer, so declining is a recorded act
rather than an empty field. And **the selection itself is published
information** — proposing a pair says that pair behaved that way — so
it is made under the floor of P5-D0.3.

**What the proposal may show, and may not.** It may name the two
columns, the operator, and HOW MANY rows the observation covers —
counts and column names, which every question already carries. It may
NOT show a cell. A proposal that printed "rows 4, 19 and 200 break
this" would be publishing the person's data into a file whose one
promise is that it carries none.

**Three refusals, stated now so they are not discovered later.**

1. **A declaration naming a column that is not in the table** stops the
   run before anything is written, exactly as `--code` does.
2. **A declaration the real table does not satisfy** stops the run and
   says how many eligible rows break it. A person who declares
   `--in-order started_on,ended_on` on a table where forty rows run the
   other way has told synthtwin something false about their data, and
   describing it under that constraint would publish a fact that is not
   true. It is a refusal, not a warning: the description is the thing
   every later file is built from.

   **AN EXCEPTION-BEARING MODE IS NOT SUPPORTED IN THIS PHASE, and
   that is a real cost** (round 1 item 4). One reversed pair in a
   hundred thousand rows leaves a person with no route to the
   relationship at all, and real tables have data-entry errors. The
   honest alternative exists — "the intended rule is this; 99,960
   eligible rows satisfy it; 40 do not" is a different and equally true
   statement — and it needs its own design: whether the twin reproduces
   the exception count, enforces the rule with a declared deviation, or
   only describes compliance; and a price for every count it publishes.
   **Named unsupported rather than left to be discovered**, and the
   first candidate for the phase that follows.
3. **A declaration whose columns are not both readable** — a date
   constraint on a free-text column, a formula on a column of labels —
   stops the run and names the role each column actually took.

   **AND A DECLARED IDENTIFIER IS NOT AN OPERAND** (round 1 item 8).
   `--identifier rate --derived "total = units * rate"` names a column
   whose role publishes no value domain at all: reading its cells to
   enforce arithmetic would cross the publication boundary that
   declaration exists to draw. Refused, naming both declarations, and
   **the identifier's role is never silently changed to accommodate the
   formula.**

   **A column name that holds a space, an operator or a comma** is
   referenced the way `--code` already references one, and the
   `--derived` text is parsed by the contract's closed grammar rather
   than split on characters. The grammar is fixed in the method clause
   of L26, with its refusals.

---

## 3.6 How a relationship is MET, which revision 2 asserted and did not have

**Review round 1, items 1, 2 and 9.** This section exists because the
plan claimed a constraint could be imposed on placements that already
hold, and it cannot.

### 3.6.1 The rank theorem, and what it forces

For two columns of equal length whose cells are all readable, **a
pairing of their values satisfying `A ≤ B` in every row exists exactly
when their SORTED values satisfy `A(i) ≤ B(i)` at every rank `i`.** No
permutation of rows repairs a rank violation, and this is the whole of
the feasibility question.

Round 1's case: 101 rows, both columns holding every published anchor,
both endpoints exact, 101 distinct values each, both inside their rank
windows — and one value differing by a single day at rank 9 makes every
one of the 101! pairings fail.

**THREE FAILURES THAT MUST NOT BE CONFLATED**, and the plan's silence
on this was the defect:

| failure | what it means | what synthtwin does |
|---|---|---|
| the published facts CONTRADICT the relationship | no table could satisfy both | **cannot arise from a truthful source.** A real table that satisfies the declaration is itself a witness that its own published facts and the relationship coexist. It can only arise from a hand-edited description, and the loader refuses it |
| the GENERATED contents are incompatible | each column holds its own facts, but their sorted values cross at some rank | repaired by 3.6.2, or reported |
| the SEARCH was exhausted | a bounded construction gave up | reported as a search limit, **never as impossibility** |

### 3.6.2 The construction: pair by rank, then permute once

1. Generate each column's cells exactly as today, independently. Every
   per-column fact holds, because every per-column fact this format
   publishes is a function of the column's MULTISET of values and not
   of their order.
2. Sort both. Compare rank by rank.
3. **Where every rank satisfies the constraint**, pair sorted-to-sorted
   and apply **ONE shared permutation to the pairs**. Both multisets are
   untouched, so every per-column fact still holds exactly, and the
   constraint holds in every row.
4. **Where a rank crosses**, attempt a bounded repair within the window
   that rank's value was already free to move in — the same window
   method G12.4 already bounds it by. A repair that would take a value
   outside its window is not made.
5. **Where the repair does not close every crossing**, the per-column
   facts WIN (P5-D0.4), the twin is written without the constraint, and
   the report names the constraint, the number of crossing ranks and
   which of the three failures above it was.

**Why step 3 is the whole method and not a heuristic.** Step 1 gives
each column the right multiset; the rank theorem says a valid pairing
exists iff the sorted orders agree; step 3 constructs one; the shared
permutation preserves both multisets. Nothing else in the description
depends on row order — which is a property of THIS format and is
asserted as an acceptance criterion rather than assumed.

**What is still open and is the method specification's to settle**
(L26a below): how wide the repair window is, how many attempts bound
the search, and whether step 1 should draw the two columns jointly in
rank space rather than independently and repair. **No arithmetic is
implemented before that specification is written and reviewed**, which
is round 1 item 9 and which Phase 4 already carries two residuals for
(R-P4-18, R-P4-115).

### 3.6.3 A derived column is RECOMPUTED, and its own facts give way

The same construction does not work for `total = units × rate`, and
round 1 proved it: with `units` and `rate` each forced to the support
`1..101`, a generated `total` holding all its own published facts can
contain 103 — prime and above 101 — which no pairing of the allowed
inputs produces.

**So the trade is named rather than hidden. The SOURCES win and the
TARGET is recomputed.**

- `units` and `rate` are generated as today and hold every published
  fact exactly.
- `total` is **computed from them, row by row**, and is not generated.
- **Its own published facts therefore become approximated**, and every
  one that moves is named in the twin's report with the published value
  beside the achieved one, exactly as an approximated fact is today.
- A person who would rather have `total`'s distribution than the
  identity does not declare the formula. **That is the choice, and the
  plan states it rather than pretending both are available.**

**Operators are a closed set fixed by the contract** — `+`, `-`, `*`,
`/` over two operands, and date difference in whole days — with **no
expression language**, for the reason principle 3 gives: a grammar a
person can write is a grammar synthtwin has to evaluate.

**Arithmetic is specified, not left to the language** (round 1 item 8).
The contract fixes the representation, the rounding, the result type
and the behaviour on overflow and on division by zero, and `0.1 × 0.2`
is settled there rather than by whichever binary64 comparison a reader
happens to write.

### 3.6.4 Composition, and the refusal that removes the hard cases

Round 1 item 9: two formulas sharing a target, cycles, and a formula
input that is also a temporal operand each make a sequence of
individually correct repairs into a wrong joint answer.

**This phase refuses those sets rather than solving them:**

1. **One formula per target column.** A second declaration naming the
   same target is refused, naming both.
2. **A formula target may not be an operand of any other declaration**,
   temporal or derived. This makes the dependency graph a set of
   depth-one trees, so there is no cycle, no ordering question and no
   repair that invalidates an earlier one.
3. **Temporal constraints are applied before formulas**, and because of
   rule 2 no formula can move a column a temporal constraint touched.

**That is a real restriction and it is stated as one.** A table whose
columns chain — `b = a + 1`, `c = b + 1` — gets one declaration
accepted and the second refused, with the message naming the chain. A
later phase lifts it; this one does not pretend to.

---

## 3.7 Which rows a relationship is ABOUT, and what comparison means

**Review round 1 item 5**, which the plan was silent on, and the
silence was the defect: a checker that skips absent cells reports "0
violations" for a table with zero comparable pairs and for one with a
hundred valid ones, and those are not the same page.

**ELIGIBILITY.** A row is eligible for a relationship when **every
column the relationship names holds a present, readable cell in that
row**. A row where either cell is absent is not a violation and not a
satisfaction: it is **ineligible**, counted on its own, and named.

**ZERO ELIGIBLE ROWS REFUSES THE DECLARATION at profile time.** Two
date columns of a hundred rows each, present on disjoint rows, have no
comparable pair at all — and a declaration resting on no evidence is a
declaration nothing supports. The refusal says so and names the count.

**COMPARISON HAS A DOMAIN, and mixed resolutions are refused.** A
date, a date-and-time, a month and a quarter are not the same kind of
value: G7.1 reads a month as a SPAN, and comparing it to a day means
choosing an end of it. **Both columns of a temporal declaration must
share a resolution family**; a mixed pair is refused with both
resolutions named.

**Time zones are compared as INSTANTS**, and where the two columns
carry different offsets the description records that the comparison was
made that way — because `2030-01-01 10:00+02:00` precedes
`2030-01-01 09:30+00:00` as an instant and follows it on a wall clock,
and a reader who assumed the other reading would be wrong about their
own data.

**Missing cells are NOT aligned by this phase.** Which rows are empty
together is `missing_data_process`, a reserved slot, and it stays
reserved: the twin's ineligible rows are wherever its own absent cells
fell. Said here because a reader of section 3.6 would otherwise assume
the construction handles it.

---

## 4. What a relationship publishes, and what it costs

**Stated before anything is built, because it is the question an
institution asks.** A published relationship is a fact computed from
real data, exactly as every per-column fact is, and it joins the
disclosure inventory of contract section 12 with its own row and its
own price.

- **A temporal constraint** — "`ended_on` is never before
  `started_on`" — says that of every row of the real table. It names no
  cell, no value and no group. Its price is one bit about the whole
  column pair.
- **A deterministic formula** — "`total` = `units` × `rate`" —
  says the real table's rows satisfy it. It names no value; it names a
  RULE, and a rule a person already knows if they made the column.
- **The grain** — "one row is one event; `subject_id` identifies the
  subject" — says what the table is about. The identifier's repetition
  multiset already publishes the group sizes today, under no floor.

**THE FLOOR APPLIES, AND THAT IS AN OWNER RULING OF ITS OWN**
(P5-D0.3, taken 2026-09-11, and it had to be taken again rather than
inherited — contract version 6 says the marginal ruling "is a ruling
about MARGINAL publication… the default would have to be decided again
on its own facts").

**A relationship is published only where it cannot narrow which values
met in a row below the smallest-group size.** Round 1 item 3 gives the
case the rule exists for: two fully present columns each publishing the
same two distinct dates, with `ended_on ≥ started_on` declared, force
the equal-date pairing and reveal both pairs. The constraint names no
value and still discloses which values shared a row — the one thing the
marginal floor ruling rests on a description never doing.

**What that governs, and every surface of it is priced:**

| what | treatment |
|---|---|
| the constraint itself | published only where the joint deduction it permits cannot single out a group below the floor |
| the eligible-row count, the satisfied count, the violation count | floor-governed as any count is |
| a PROPOSAL in the questions file | the selection itself is information — synthtwin proposing a pair says the pair behaved that way — so a proposal is made under the same floor, and none is made where the deduction would be below it |
| a REFUSAL's exception count | printed on the SCREEN to the person running the command about their own table, and written into no file. Stated because it is the one count that escapes the floor, and the reason it may |

**Where the floor blocks publication, the slot stays `null`** and the
twin's report says the declaration was given and not published, with
the reason. A person who wants it anyway raises nothing and lowers
nothing: the answer is a bigger table, which is the honest answer.

---

## 5. Acceptance criteria

Written now, so the phase can be held to them rather than to a memory
of them. Each is either met or named unmet at the close, as Phase 4's
were.

1. The P5-D0 decisions are recorded — taken or declined, dated —
   before the contract that encodes any of them is ratified.
2. **A COMPATIBILITY MATRIX is written and tested**, not a version
   number changed (round 1 item 10). It states, for each of: a version
   6 description with null slots; a version 7 description whose filled
   slots this tree reads; a version 7 description carrying a slot this
   tree does NOT read; a malformed slot; and a version above 7 — what
   the loader does, what the generator does, and what the validator
   does. **A version 6 description still loads, still generates and
   still validates**, and a test asserts each. The version is dispatched
   on, never mutated.
3. **THE MOTIVATING FAILURES ARE FIXED, on a stated domain, across
   several seeds** (round 1 item 13). The section 0 table is
   re-measured with the declarations given: **137 reversed rows become
   0**, and the derived column's 299 mismatching rows become 0. A phase
   that printed those counts and left them standing would have met
   revision 2's criteria and is refused by this one. Outside the stated
   domain the limitation is REPORTED, never silently accepted.
4. No per-column fact Phase 4 publishes is lost to a temporal
   relationship. Measured: the every-role fixture reports zero MISSED
   before and after, **and the shared-permutation property of section
   3.6.2 — that no published fact of this format depends on row order —
   is asserted by a test rather than assumed.**
5. **A derived column's approximated facts are named, every one.** The
   trade of 3.6.3 is only honest if the report states which of
   `total`'s published facts moved and by how much.
6. **Every relationship carries a report entry** with its definition,
   its eligible population, its satisfied count, its violation count,
   its ineligible count and its outcome — and **the outcome
   distinguishes met, not met, not checkable and search-limited**
   (round 1 item 11). "0 violations" may never stand for "no comparable
   pairs".
7. The questions file proposes under the floor of P5-D0.3, never
   applies a proposal unanswered, and **a proposal states the count its
   observation rests on and that observed agreement guarantees nothing
   outside the described table** (round 1 item 6).
8. **A declaration survives the whole workflow** — answer the questions
   file, re-profile, generate, validate, with `--out-dir` and
   `--replace` — and command-line and answers-file declarations that
   conflict resolve by a stated precedence, tested (round 1 item 12).
9. Every surface that states the twin's bound moves in the commit that
   changes it — the claim inventory's seventh family and the phase
   statements included.
10. SECURITY.md carries a version-7 disclosure entry, priced by family
    and by the floor of P5-D0.3, **in the landing that fills the first
    slot** — not at the close, which is where Phase 4 left it and had
    to repair it (R-P4-90).
11. **The public method is written and reviewed BEFORE the arithmetic
    that implements it**, with frozen reference cases and committed
    mutants for every new branch (round 1 item 9). Phase 4 closed with
    acceptance criterion 8 unmet for exactly this reason; this phase
    does not repeat it.

---

## 6. What this phase does NOT do

- It does not make numbers computed on the twin scientific results.
  That sentence in CLAUDE.md does not soften, at any point of this
  phase, for any slot.
- It does not fill `statistical`, `hierarchy`, `keys`,
  `missing_data_process` or `validation_targets`.
- It does not make the twin safe to move under a rule it was not safe
  to move under before. A relationship is one more real-derived fact.
- It does not touch the offline guarantee, the decontamination model,
  or the profile/generator boundary. The generator still never reads a
  table.

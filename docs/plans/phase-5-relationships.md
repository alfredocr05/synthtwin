# Phase 5 — relationships: what the twin carries across two columns

**Status:** revision 2, 2026-09-11 — **DRAFT, not ratified.** Revision
1 was written the day Phase 4 closed; revision 2 records the owner's
ruling on P5-D0.2 (**DECLARED**, taken 2026-09-11) and takes the other
three decisions at this plan's own recommendation, each marked
reversible and each naming what would overturn it. Nothing may be built
from it until it has been through adversarial plan review. The phase
process is not suspended for it.

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
opens work faster than it closes it does not end. Phase 5 fills THREE
slots and reserves the rest, in this order:

| # | slot | what it buys the person | why this order |
|---|---|---|---|
| 1 | `temporal` | two event columns keep their order: no span ends before it starts | the largest measured breakage, and the one that makes analysis code return nonsense rather than fail |
| 2 | `deterministic` | a column derived from others agrees with them | the second largest, and the one a person is most likely to check first |
| 3 | `grain` | what one row IS, said in the description rather than left to be inferred | it is what makes `temporal` and `deterministic` meaningful within a subject, and R-P5-1 shows the page already needs it |

**Not in this phase, and reserved:** `statistical` (correlation between
two numeric columns), `hierarchy`, `keys`, `missing_data_process`,
`validation_targets`. Each stays `null`, each keeps its loader refusal,
and the quality report continues to check no cross-column fact it is
not handed. **A later phase fills them; this plan neither fills nor
reads them.** Naming them here is not a promise of when.

**Why correlation is NOT first**, since it is the word a statistician
reaches for. Three reasons, and the owner may overturn any of them.
A wrong correlation is invisible in a way a backwards date is not — a
reader sees `ended_on < started_on` immediately and cannot see that
`r = 0.3` should have been `0.7`. Reproducing a correlation means
changing how every value of both columns is placed, which puts every
per-column fact Phase 4 built at risk, while an order constraint and a
formula can be imposed on top of placements that already hold. And the
owner's first goal is that code RUNS UNCHANGED: negative durations and
disagreeing derived columns break running code, where a weakened
correlation weakens a result.

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
| L26 | **version 7 and the seam** | the contract's version bump, the `temporal` slot's shape, the loader's refusal narrowed from "any non-null" to "any slot this version does not read", and the generator's one dispatch seam opened |
| L27 | **`temporal`, declared** | two date columns keep their order in every row of the twin; the report says which constraint held and which did not |
| L28 | **`deterministic`, declared** | a column stated as a formula of others agrees with them; the same reporting |
| L29 | **`grain`** | the description says what one row is; the twin's rows group the way the real table's do |
| L30 | **the quality report** | `validate` checks the filled slots, with red cases, and says plainly which cross-column facts it cannot check |
| L31 | **the record and the close** | CHANGELOG, STATE, SECURITY's version-7 disclosure entry, the closure section |

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
   says how many rows break it. A person who declares
   `--in-order started_on,ended_on` on a table where forty rows run the
   other way has told synthtwin something false about their data, and
   describing it under that constraint would publish a fact that is not
   true. It is a refusal, not a warning: the description is the thing
   every later file is built from.
3. **A declaration whose columns are not both readable** — a date
   constraint on a free-text column, a formula on a column of labels —
   stops the run and names the role each column actually took.

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

**The floor question the owner must rule on:** a constraint that holds
in every row but one is a statement about that one row. The plan's
position is that a relationship is published only where it holds
WITHOUT exception, and a near-miss publishes nothing and says so — but
that is a rule with a cost, and it is P5-D0 decision 3.

---

## 5. Acceptance criteria

Written now, so the phase can be held to them rather than to a memory
of them. Each is either met or named unmet at the close, as Phase 4's
were.

1. The P5-D0 decisions are recorded — taken or declined, dated —
   before the contract that encodes any of them is ratified.
2. `profile_version` advances to 7 in the commit that first fills a
   slot; the loader's refusal is narrowed rather than deleted, and a
   version 6 description still loads and still generates.
3. Every filled slot publishes a constraint the twin MEETS, or the
   twin's report names it as not met with the count of rows that
   violate it. No slot is filled whose satisfaction is not measured on
   the twin's own cells.
4. No per-column fact Phase 4 publishes is lost to a relationship.
   Measured: the full every-role fixture reports zero MISSED before and
   after each landing.
5. The measured breakage of section 0 is re-measured at the close, on
   the same two tables at the same seed, and the numbers are published
   in the closure section whatever they are.
6. The questions file asks about a relationship it could propose, and
   never applies one unanswered.
7. Every surface that states the twin's bound moves in the commit that
   changes it — the claim inventory's seventh family and the phase
   statements included.
8. SECURITY.md carries a version-7 disclosure entry, priced by family,
   in the landing that fills the first slot — not at the close, which
   is where Phase 4 left it and had to repair it (R-P4-90).

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

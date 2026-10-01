# Phase 5 plan review — round 1 (2026-09-11)

**Verdict: REJECT.** Thirteen items, six blocking. `gpt-6-astra` at
high reasoning effort, read-only, against revision 2. The full text is
maintainer-private at
`planning-notes/reviews-p5-plan/verdict-round-1.md`; this is the
repository's record of what it found and what revision 3 did.

**It was right about all six blocking items, and three of them were
things the plan ASSERTED rather than overlooked.** That is the
difference between a plan review and a code review, and it is why this
one ran before any code: each of these would otherwise have been found
weeks in, with an implementation built on it.

| # | severity | what it found | revision 3 |
|---|---|---|---|
| 1 | blocking | **the feasibility claim was false.** A pairing satisfying `A ≤ B` exists exactly when the SORTED values satisfy it at every rank; no permutation repairs a rank violation. Counterexample: 101 rows, every anchor held, endpoints exact, one value differing by a day at rank 9 — every one of 101! pairings fails | §3.6: the rank theorem, the three failures that must not be conflated, and a construction — pair sorted-to-sorted, then apply ONE shared permutation, which preserves both multisets and therefore every published fact |
| 2 | blocking | **a derived column needs joint generation.** With `units` and `rate` forced to support `1..101`, a `total` holding all its own facts can contain 103 — prime, above 101 — which no pairing produces | §3.6.3: the sources win, the target is RECOMPUTED, and its own facts become approximated and are named one by one. The trade is stated instead of both being promised |
| 3 | blocking | **the disclosure decision exceeded the standing ruling**, which contract 6 explicitly limits to marginal publication and says must be decided again for anything crossing two columns. And a constraint can force a pairing: two columns publishing the same two dates reveal both pairs | P5-D0.3 taken by the owner 2026-09-11: **the same floor as everything else**, with every surface priced — the constraint, the counts, the proposal selection, and the one count that escapes (a refusal printed on screen about the person's own table) |
| 5 | blocking | **eligibility and comparison were undefined.** Zero comparable pairs reports "0 violations" exactly as a hundred valid pairs does; time zones and month spans have no stated reading | §3.7: eligibility per row, ineligible counted on its own, zero eligible REFUSES the declaration, mixed resolutions refused, instants compared as instants and the description saying so |
| 7 | blocking | **`--one-row-per subject_id` contradicted the plan's own example** — 300 rows and 100 subjects is not one row per subject — and `grain` added no measurable obligation beyond the repetition multiset that already ships | `grain` LEFT the phase. Two slots, not three. Reserved with the reason |
| 9 | blocking | **no composition method.** Two formulas sharing a target, cycles, a formula input that is also a temporal operand: individually correct repairs, wrong jointly. And the arithmetic had no reviewed method or frozen cases before implementation | §3.6.4 refuses those sets — one formula per target, a target may not be an operand elsewhere — which makes the graph depth-one trees. L26 writes and reviews the method BEFORE any arithmetic |
| 4 | high | strict refusal strands ordinary imperfect tables: one reversed pair in a hundred thousand rows leaves no route | named UNSUPPORTED with its cost and its design sketched, as the first candidate for the next phase |
| 6 | high | an answered proposal can still promote coincidence into a rule | a proposal states what was OBSERVED, never what is true, carries its support count, offers an explicit "no", and is itself made under the floor |
| 8 | high | formula arithmetic, operand roles and name syntax undesigned | the contract fixes representation, rounding, result type, overflow and division by zero; a declared identifier may not be an operand and its role is never silently changed |
| 10 | high | the version transition as written rejects existing version 6 files | acceptance criterion 2 is a compatibility MATRIX, tested, with the version dispatched on and never mutated |
| 11 | high | reporting could not support an honest verdict | criterion 6: every relationship reports definition, eligible population, satisfied, violated, ineligible, and an outcome distinguishing met / not met / not checkable / search-limited |
| 12 | high | declaration persistence and precedence unspecified | a declaration persists as a column declaration does; the answers file wins over the command line; compliance re-measured every run |
| 13 | high | **the acceptance criteria could be met by a phase that fixed nothing** — keep all 137 reversed rows, print the counts, pass. And the correlation-deferral argument was mechanically wrong | criterion 3 requires 137 → 0 and 299 → 0 across several seeds on a stated domain. The mechanical argument is WITHDRAWN in the status block; the deferral now stands only on the owner's priority |

**The correction worth carrying out of this round.** Permuting whole
column cells preserves every marginal fact exactly and changes the
correlation — so correlation is the mechanically CHEAP relationship and
a formula is the expensive one. The plan had it backwards. Deferring
correlation is still defensible on the owner's first goal, that code
runs unchanged; it is not defensible on difficulty.

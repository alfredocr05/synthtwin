# Phase 4 — contract v6 adversarial review, round 5

**Reviewer:** codex `gpt-5.6-sol`, reasoning effort high, read-only,
`< /dev/null`, background with a stall watchdog. Target: revision 4 at
commit `8531be6`, complete diff `e23ffaa..8531be6`.

**Verdict: REJECT.** Ten items, all ten blocking, and the side count
is the part that matters: **10 control gaps, 0 wording items.** The
protocol's early-stop condition — remaining items are wording rather
than control gaps — was therefore not met, and this was the fifth and
final round the protocol allows.

Six of round 4's thirteen items came back FIXED, which had not
happened in any earlier round: P4-X4-F4 (C6-D1), F6 (C6-V4), F10
(producer rows), F11 (the refusal), F12 (citations) and F13 (heading,
range, settings). Seven came back narrowed-still-open.

## The item this record exists for

**P4-X5-F3 found a third invented enumeration, and this one was
harmful.** Round 4's repair of P4-X4-F1 put `empty` into the nothing
publication class. The reasoning was clean — a column with no values
discloses none — and the conclusion broke a shipped fact. The three
publication tuples in `taxonomy.py` and `contract.py` are exactly
`numeric_unrepresentable`, `identifier` and `free_text`; `empty` is
deliberately absent from all three, so an `empty` column is NOT a
nothing-publishing column and C5-N3's source accounting applies to it.
Its `missing_by_source` carries the absent SPELLINGS its cells wore,
under the floor, with counts — and C6-37 reproduces those spellings in
the twin.

Eleven cells all holding one built-in absent word publish that word
with the count 11, and the twin writes it in eleven rows. Under
revision 4's table the class would have forced `missing_by_source`
empty and both absence counts to zero, the published fact would have
vanished with no rule saying it had, and the twin would have written
eleven blanks. That is section 6's reproduction deliverable failing
silently, caused by one wrong table row.

The repair separates two things revision 4 collapsed: `empty` is in no
VALUE-PUBLISHING class (C6-PUB-A) because it has no value to publish,
which is not the same as being NOTHING-PUBLISHING. Round 4's original
finding — that a declared all-absent column had two answers — is
settled by C6-PUB-B, which carries version 4's own rule that a
`--identifier` column is nothing-publishing whatever its role. Declared,
its `missing_by_source` is empty; undeclared, it is published under the
floor. The difference is exactly what the person bought by typing the
option.

**Three invented enumerations in two rounds, all mine.** A format
member and a resolution that do not exist; fifteen settings spellings
none of which were right; and a publication membership contradicting
the shipped tuples. The first two I caught, the third I did not. What
they have in common is that each was written from reasoning about what
the enumeration SHOULD contain instead of from the artifact that fixes
it. The mechanical check I added after round 4 verified the roles
appeared exactly once across the classes — internally consistent, and
consistent with the wrong answer, because it never compared against
`taxonomy.py`. A consistency check that does not reach the source of
truth confirms whatever it is given.

## Items and dispositions

| item | disposition |
|---|---|
| P4-X5-F1 | REPAIRED. Three inherited restrictions made `affixed_number` unsatisfiable — Q1 forbids the `n_rows` echo outside two roles, §7.5.2 forbids `numeric_styles` outside the same two, and §5.5 admits no calendar `candidate`. The producer had to write keys the loader had to refuse. New **C6-Q1**, **C6-NS** and **C6-CAND** supersede each by name and restate it whole; **C6-ARG** supersedes version 4 §4.5's note grammar, which revision 4 added three forms to without naming. Four rows added to 2.2.2A. |
| P4-X5-F2 | REPAIRED. **C6-S13** restates C5-S13's exhaustive floor-one list ENTIRE and adds one position: the `(withheld)` ENTRY of `fraction_widths`, not the field. At a floor of one a named-width census is correct and must not be refused — the same treatment `numeric_styles` already has. `missing_by_source`, `n_missing_blank` and floor-free `resolution_mix` are named as NOT joining. |
| P4-X5-F3 | REPAIRED — see above. |
| P4-X5-F4 | REPAIRED, needing plan amendment **A-P4-8** (THIS RAISES). A-P4-6's three bounds still admitted an impossible document. A fourth condition comes from the pool's finite capacity: with six styles, at most five share the pool with decimal, so *F* ≥ *W* − 5 × (floor − 1). |
| P4-X5-F5 | REPAIRED. C6-48's claim that ways 1–5 were unchanged was false for way 2: version 6 puts a member in the vocabulary matched differently from every other, so the way quantifying over members cannot be inherited. Way 2 is re-proved, and C6-32 now names the rescue test explicitly as one of the places the vocabulary's own matching operation applies. `declaration_matching` does not move. |
| P4-X5-F6 | REPAIRED. The slashed-date form gains the both-readings identity *D* − *X* = *M* − *Y* and a bound to the column's `n_present`. Without it, D=90, M=80, X=10, Y=20 passed every check while requiring one quantity to be both 80 and 60. |
| P4-X5-F7 | REPAIRED. The affix remark said "every value in this column" while C6-5 permits stragglers up to the parse line, so it was false of the hundredth cell of a ninety-nine-affixed column. Arity goes 2 → 3 and the rendering speaks of the `n_affixed` counted cells. |
| P4-X5-F8 | REPAIRED. "Character-for-character the `affix_prefix` OR `affix_suffix`" admitted the pair SWAPPED — a `$`/`kg` block accepting `("kg", "$")` and rendering a sentence that misdescribes the column. The binding is POSITIONAL now, and R-P4-15 is restated: it had described a future fifth argument class while the form that exists was already incompletely bound. |
| P4-X5-F9 | REPAIRED. §12 priced only the DECLARED route to the eight new text members and missed the automatic one, which is the larger. From the flip those spellings read as absent by default: ninety numbers and ten error literals stop being free text, and what newly appears is the spelling, its count, the whole numeric distribution and the role transition — with nobody typing anything. |
| P4-X5-F10 | REPAIRED. C6-MIG-B is specified rather than described: exact search paths, exclusions named with reasons (the older contracts, the plans and the changelog record what was true when written), the literal word, three exact phrases, an eighty-character window, and an expected-hit manifest of twelve lines across nine files — computed by running the search, not by listing from memory. |

## The round budget, and amendment A-P4-9

This was round 5, the last the protocol allows, and it rejected with
ten control gaps. Neither protocol exit was available. **A-P4-9**
raises the limit for this artifact alone, until a round returns a
stopping verdict or its remaining items are wording; it bounds the
raise at three further rounds, after which the artifact is reported to
the owner as not converging.

The amendment records what argues for continuing. Item counts across
five rounds are flat — 17, 13, 10, 13, 10 — but the KIND has fallen
sharply. Rounds 1 and 2 found whole enumerations superseded and lost
and a role with no publication class. Round 5 found a missing
arithmetic identity, a binding that permitted a swap, and a bound
derivable from a partition's capacity. Those are the defects of a
document that is nearly right, and they are exactly the ones that
become wrong twin bytes if nobody looks.

## State

Revision 5. Suite green at 3,359 passed / 48 skipped. Scans clean.
Seal current. The plan now carries nine amendments, seven of them
raised by this document's review.

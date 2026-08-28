# Phase 4 — contract v6 adversarial review, round 4

**Reviewer:** codex `gpt-5.6-sol`, reasoning effort high, read-only
sandbox over the parent folder, `< /dev/null`, background with a
ten-minute stall watchdog. Target: revision 3 at commit `e23ffaa` on
branch `phase-4-plan`, with the complete `f50fcce..e23ffaa` diff.

**Verdict: REJECT.** Thirteen items, ten blocking. Every one of round
3's ten items came back NARROWED, STILL OPEN or STILL OPEN — none was
re-reported as fixed. Verdict text at
`scratchpad/codex/verdict-v6-round-4.md`.

## The lesson of this round, written first because the rest follows from it

Round 3's repairs were too literal. Each fixed the instance the
reviewer named and left the class of defect alive, so the same defect
returned at a different clause. The class is this: **when this
document supersedes a rule ENTIRE, it must restate everything that
rule did which still applies — not only the part version 6 changes.**
A partial replacement of a total rule leaves the untouched part bound
by nothing at all, because the enumeration it quantified over is gone.

Four of this round's blocking items are that one defect: D1 replaced
for five new formats and lost for six old ones; V4 replaced for mixed
candidates and lost for calendar-only ones; §6.10 replaced for three
new roles with `empty` left in no class; C5-19 replaced by a pointer
to an unrelated clause. Revision 4 repairs the class, not the four
instances: every superseding clause named below now restates its
predecessor TOTAL, and says in its own text that this is why.

## Items, and what each cost

| item | severity | disposition |
|---|---|---|
| P4-X4-F1 | blocking | REPAIRED. `empty` is now IN the nothing class rather than in none, and C6-PUB-B states the structural-identifier override as a rule instead of a fourth table row, so the exactly-one-class property survives a column that is both. |
| P4-X4-F2 | blocking | REPAIRED, and it needed a PLAN amendment: **A-P4-7**. Two ratified sentences conflicted — P4-D4.1 requires the affix remark to name the pair, A-P4-3 says arguments are whole numbers and package words. The plan now rules that P4-D4.1 governs, the argument class widens by one, and the widening is bound by character-for-character identity to the block named by the note's own sibling `column` field. Revision 3's "the block the sentence sits in" was unresolvable: notes live in the top-level `publication_notes` array and sit in no block at all. |
| P4-X4-F3 | blocking | REPAIRED, and it needed a PLAN amendment: **A-P4-6**. A-P4-5 concluded the pooled fraction sum "binds nothing", which would have admitted a fraction census ten times larger than the column. C6-30 is now stated by three exhaustive cases, and the pooled case binds three real bounds. |
| P4-X4-F4 | blocking | REPAIRED. New **C6-D1** restates the format-to-resolution binding TOTAL over all eleven members and keeps D1's letter as 2.2.2 requires. Self-caught while writing it: the first draft invented a `clock-only` member and dropped `year-quarter`. |
| P4-X4-F5 | blocking | REPAIRED. **C6-48** supersedes C5-19 properly and re-walks its completeness proof over SIX absence ways instead of five; **C6-K4** now has one answer instead of three (§5.4 said C5-K4 stood, §9 said it was superseded, the table listed neither). Both rows added to 2.2.2A. |
| P4-X4-F6 | blocking | REPAIRED. **C6-V4** is total over three candidate groups — numeric, calendar, withheld — restating version 4's two sentences unchanged and adding the third. |
| P4-X4-F7 | blocking | REPAIRED. The slashed-date form goes to FIVE arguments (the reading used joins the four counts), gains a THIRD first-clause rendering for the tie the plan requires reported as a tie, states the exact one-space composition of the two clauses, and gains argument-consistency checks. |
| P4-X4-F8 | blocking | REPAIRED. §12 gains four rows: below-floor folded identity sizes, the eight new text vocabulary members, the two time-of-day form facts, and the calendar-placeholder verdicts. The inventory now claims completeness over sections 3 through 6 and makes a missing row red. Row 11 was corrected a second time, by me: my first wording said the folded-size multiset was published nowhere in version 5, which overstates it — P4-D5 prices the difference narrowly, as folded rather than raw grouping, and the plan governs. |
| P4-X4-F9 | blocking | REPAIRED. **C6-MIG-B** replaces the claim that a hand-written table is exhaustive with a SEARCH of the tracked tree. The reviewer named five surfaces the table missed; the repository in fact states the vocabulary count in eight, which is the argument for a search rather than a longer list. |
| P4-X4-F10 | serious | REPAIRED. `resolution_mix`, `fraction_widths` and `n_unparsed` gain producer rows in §9, and the preamble names them as the three measured facts whose loader-checkable invariants do not reach the measurement. |
| P4-X4-F11 | blocking | REPAIRED. **C6-46** now carries the refusal WORD FOR WORD as C5-26 did, with only the version numbers, the reason clause, the `--day-first` priced clause and the not-holding-the-table sentence moved. C6-47's source-checkout inference is STRUCK: a maintainer can hand somebody an unreleased wheel, so the conclusion was false while its premise was true. |
| P4-X4-F12 | serious | REPAIRED. Four citations corrected: the vocabulary successor to C6-31, the length rule to C6-26, the fraction residual to C6-27 through C6-30, and `C6-DF` — which never existed — to the `day_first` setting of C6-20. |
| P4-X4-F13 | minor | REPAIRED. Amendment range extended to A-P4-7, the §7B heading says three sentences, and §14 enumerates the seventeen settings keys. The fifteen inherited spellings were verified MECHANICALLY against the shipped `SETTINGS_KEYS`, after a first draft invented all fifteen from memory. |

## Two defects I introduced this round and caught myself

Recorded because a review record that only lists the reviewer's finds
understates how the document is actually kept honest.

1. **The C6-D1 table invented a format member.** The first draft
   listed `clock-only` bound to a `time` resolution and omitted
   `year-quarter`. Neither the member nor the resolution exists.
   Caught by reading §14's own enumeration back against the new table.
2. **The §14 settings list invented all fifteen inherited spellings.**
   Every one was plausible and every one was wrong. Caught by
   comparing against `src/synthtwin/contract.py`, then verified with a
   mechanical set comparison rather than by eye.

Both were the same mistake: writing a closed enumeration from memory
instead of from the artifact that fixes it. Every enumeration this
revision states is now checked against its source.

## State after the repairs

Revision 4. Suite green at 3,359 passed / 48 skipped. Decontamination
clean — two denied tokens found and reworded, never manifested away.
Seal current. Two plan amendments emitted, A-P4-6 (THIS RAISES) and
A-P4-7 (THIS LOWERS, with its compensating binding and residual
R-P4-15), because both moved a ratified obligation and neither could
be a quiet contract-side repair.

Round 5 follows, as the last round the protocol allows.

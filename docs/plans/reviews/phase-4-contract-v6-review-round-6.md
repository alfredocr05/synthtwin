# Phase 4 — contract v6 adversarial review, round 6

**Reviewer:** codex `gpt-5.6-sol`, high effort, read-only. Target:
revision 5 at commit `5ce4944`, diff `8531be6..5ce4944`. This round
runs under plan amendment **A-P4-9**, which raised the five-round
limit for this artifact alone and bounded the raise at three rounds.
This was the first of the three.

**Verdict: REJECT.** Eight control gaps, two wording items.

The repair rate improved sharply: **eleven of round 4's thirteen items
are now FIXED** (six at round 5), and four of round 5's ten. What
remains, and what a maintainer-internal sweep then found beside it, is
the subject of this record.

## The reviewer's closing recommendation, recorded because it is
## addressed to the owner and not to me

> Revision 5 nevertheless repeats both root failure classes — partial
> replacement of a total rule and incomplete arithmetic over a
> partition. Together with the flat historical item counts, this
> round's evidence says the artifact is not converging through local
> repairs. Because this is the requested final round, the next owner
> action should be to split or reduce the contract before
> implementation, rather than consume the remaining nominal rounds
> unchanged.

I did not spend the second budgeted round. Instead I ran a
maintainer-internal sweep to find out WHY the class keeps recurring,
on the reasoning that the reviewer's operative word was "unchanged"
and that another local-repair round would earn it. The sweep's result
is that the reviewer is right, for a reason neither of us had named.

## What the sweep found, and why it settles the question

Six agents derived, from the artifacts rather than from reasoning, the
material revision 6 would need; a second agent adversarially checked
each derivation against source. The verifiers found **83 errors across
the six derived answers**, which is the first thing worth recording: the
derive-then-verify shape was not ceremony.

The sweep then judged **every one of the twenty-five registered
supersession rows** of §2.2.2A, and searched for supersessions that
have no row at all. Result:

- **8 of 25 registered rows are PARTIAL** — the successor does not
  state the whole of what it replaced. Four were unknown before this
  sweep, and one of them, row 19, is a clause round 5 marked REPAIRED.
- **12 unregistered supersessions or orphaned rules**, including four
  version 4 invariants that quantify over enumerations version 6
  destroyed and that are now in force over vocabularies that no longer
  exist.
- **Four classes of uncited SITE** — enumerations version 4 states a
  second and third time, in its universal-key table and in its
  appendix, which no supersession row names.

**The most serious single finding (C1-a).** Version 4 §5.1's
universal-key table fixes `role` at "one of the ten role names", lists
`statistical_type`'s ten values, and fixes `missing_by_class` at
"exactly five keys". No row of §2.2.2A cites it, and C6-FKM
affirmatively re-imports "version 4's universal keys, unchanged, on
every role". By version 6's own carrying rule those three lines are in
force at their own wording. **Three of the thirteen roles, three of
the thirteen statistical types and one of the six absence classes are
therefore unwritable today** — the entire point of the version is
blocked by a table nobody named.

**The second (row 2).** `statistical_type` occurs on exactly three
lines of the whole contract and not one of them writes out a member.
The ten inherited values are never stated; four of the ten map to a
name that is not their role. Version 4's invariant A4 — the rule a
loader actually enforces on the axes — is orphaned, and version 6's
own A5 quantifies over a table holding three rows. **Round 3 cleared
this item as "Correct."**

**The third (row 16).** C6-44 restates two of C5-24's three components
and drops the one binding the refusal catalogue. With C5-24 superseded
entire, a version 4 document trips no refusal row at all — so the
word-for-word message of C6-46, which C6-47 spends forty lines
defending, has nothing that fires it.

**The fourth (row 24).** The note grammar is fixed by version 4 as the
closed shipped table `taxonomy.NOTE_ARITY`, which holds **38 forms**.
§7B's table lists three. Version 6's grammar is 41 forms and no
surface says so. This is inside the clause round 5 repaired.

## Why this is structural rather than a run of bad luck

Version 6 is written as a DELTA against a base that requires TOTAL
restatement. Each superseded rule is stated in two to four places — a
defining section, the universal-key table, the appendix, and a shipped
constant — and each round finds another site. The carrying rule
("total except superseded by name") makes every missed site a live
contradiction rather than a stale sentence. That is a property of the
document's design, not of any round's thoroughness, and no number of
review rounds converges on it: a reviewer who reads what the contract
SAYS cannot see a site the contract never mentions.

Nine amendments have come out of this artifact's review. Three of them
touch a single key. The sweep is what makes the pattern legible.

## Items from round 6

| item | side | disposition |
|---|---|---|
| P4-X5-F11 | control | The note-form supersession. Confirmed far larger than reported: 38 inherited forms, not "some". Held for the structural decision. |
| P4-X5-F12 | control | The EMPTY fraction-census branch escapes the bound. Derived correctly by the sweep; a fifth condition is owed. |
| P4-X5-F13 | control | The slashed-date union `D+Y = M+X ≤ n_present`. Derived. |
| P4-X5-F14 | control | The recoverable-distribution form's two counts are bound by nothing. Derived — and the sweep found the plan rules this a CLAUSE ON AN EXISTING FORM, not a new form, so C6-GRAMMAR is defective against the plan in a way round 6 did not see. |
| P4-X5-F15 | control | The migration search misses `contract.py:2514` and the changelog's unreleased entries. Derived, with real manifests. |
| P4-X5-F16 | control | The other two searches are deferred with no phrases. Derived. |
| P4-X5-F17 | control | §12 omits the datetime shape facts. Derived. |
| P4-X5-F18 | control | **REPAIRED NOW, by plan amendment A-P4-10.** The plan's "every role in exactly one class" was never true of the shipped code: the battery has stated it over FOUR buckets since Phase 1, `empty` being the fourth. Plan review round 1 supplied that exact form and the repaired sentence dropped it. Verified by running the shipped profiler: an undeclared all-absent column publishes `missing_by_source: {"NA": 20}` under the floor, and moving `empty` into the nothing class would force it empty, break C5-N3's closing sum and write blanks where the twin should write the recorded spelling. |
| P4-X5-F19 | wording | Subsumed: the "three tuples list exactly" claim was a symptom of the same misreading A-P4-10 settles. |
| P4-X5-F20 | wording | C6-GRAMMAR announces three sentences and numbers two. Confirmed, and it is one instance of row 24. |

## Where this leaves stage 3

The version 6 contract is NOT ratified and I am not treating it as
convergeable by a seventh round of the same kind. A-P4-9 budgeted
three rounds past the limit and required that the artifact be brought
to the owner if it did not converge; the sweep is the evidence that it
will not, and it arrived one round early. The structural options and a
recommendation go to the owner with this record.

Applied in this commit regardless of which option is chosen: amendment
**A-P4-10**, because the plan states something false about the shipped
code and that is wrong under every option.

Suite green at 3,359 passed / 48 skipped. Scans clean. Seal current.
The derivation material — the 38-form table, the datetime fact set,
the three search specifications with real manifests, the partition
arithmetic, and the full supersession judgement — is kept for whichever
option the owner takes.

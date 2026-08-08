# Phase 1 — response to review round 5

**What changed since round 5:** not a patch set. The owner directed a
redesign of everything still open, and six areas were rebuilt rather
than repaired: the statistics core, the reference-vector oracle, the
column taxonomy, the reader, the two-file write, and the accuracy
contract. The plan is now revision 2. Where a round-5 item was really a
symptom of a design that could not hold, this response says so and names
the replacement instead of claiming the symptom is gone.

Suite: 741 tests green (was 600). ruff, mypy strict, the offline import
scan, the decontamination scan, the provenance guard and the lock
validator are all clean on the tracked tree.

---

## The three round-5 items

### P1-R5-F1 — exclusivity is sound only over the incomplete origin set it receives

**Accepted as stated; fixed at the rule, not the call site.** The review
was right that `_resolve_exclusively` is only as good as the origin set
handed to it, and that a name bound in more than one way could still
arrive carrying one origin. The repair separates two questions the old
code answered with one function:

- **"must this be checked?"** — origins accumulate. Any binding that
  could have produced the value contributes, so a name bound by both an
  import and a definition carries both, and the check fires.
- **"may this be trusted?"** — every origin must independently be the
  allowed API. One unknown origin in the set is enough to refuse.

Class scopes and `match` captures now bind through the same path as
every other binding, so they no longer arrive with an empty set. The
runnable examples from round 4 (a module that both imports and defines
`Path`/`cast`) are in the suite and are refused.

### P1-R5-F2 — the combined numeric population is not carried through sentinel, sign and integer decisions

**Accepted, and it went deeper than the item said.** Tracing it showed
the classification was being recomputed at three points that could
disagree, which is the actual defect — the sentinel, sign and
integer-valued decisions were three readings of the same column rather
than three uses of one reading. Each cell is now classified exactly
once into number / out-of-range / self-contradictory / text, and every
later decision consumes that one population. `n_out_of_range` and
`n_contradictory` appear on every column block, and a column that loses
too many values to the representable range is now described by its own
role, `numeric_unrepresentable`, rather than being pushed into text.

### P1-R5-F3 — output identity does not cover every admitted alias or metadata failure

**Accepted; the identity test now fails closed.** Resolved-path equality
is compared first and regardless of whether either file exists, so a
dangling alias is caught; the filesystem's own identity is consulted
when both exist, which catches hard links; a case-blind comparison
catches case-equivalent aliases on case-insensitive filesystems; and
**any** metadata error is treated as "these are the same file". The
failure mode is now a refusal to write, never an overwrite of the
user's own table.

---

## The redesign, area by area

### The oracle (P1-R2-F5) — fixed first, because it graded everything else

The reference-vector generator could report a negative standard
deviation and mishandled half-even rounding. An oracle defect is worse
than a code defect: it can certify a wrong implementation as right. The
generator no longer uses decimal arithmetic at all. It works in exact
rationals, and every value it publishes is *proved* correctly rounded —
each result is checked against both adjacent floats, with ties resolved
to even significand, and the proof is what fails if the arithmetic is
wrong. The square root is computed by integer methods (`math.isqrt` on
a scaled numerator) and separately proved, so `sqrt` is not trusted to
grade itself.

### The statistics core (P1-R2-F4) — and a limit the plan should never have recorded

Revision 1 recorded a "conditioning limit": for {1e16, 1, -1e16} the
third central moment cancels by 1e32 and no binary64 algorithm could
return the correctly rounded skewness, so only an absolute accuracy
contract was possible. **That was wrong, and it is retired.** It was a
property of the two-pass floating-point reduction revision 1 used, not
of binary64. Every float is an integer times a power of two. The column
is now converted to exactly that — one shared power of two, one integer
significand per value — the power sums are accumulated as
arbitrary-precision integers, which cancel without error because Python
integers do not round, and the result is rounded **once**, at the end.

Measured, on the sample the plan used to argue the limit was
unavoidable:

| case | revision 1 | now | exact |
|---|---|---|---|
| skew {1e16, 1, -1e16} | wrong sign / noise | `-1.224744871391589e-16` | correctly rounded |
| mean [-MAX, 1, MAX] | inexact | `0.3333333333333333` | correctly rounded |
| mean [-MAX, 1e-16, MAX] | inexact | `3.3333333333333335e-17` | correctly rounded |

The accuracy contract in the plan is tightened from absolute to
correctly-rounded-or-adjacent accordingly.

One test change is worth flagging explicitly rather than leaving to be
discovered: `tests/test_numeric_reference.py` had a `SMALLEST_STEP`
floor added to its ladder tolerance. That floor was hiding a real miss
in the subnormal range. It is removed, the miss is fixed, and the
subnormal ladder is correct without it.

### The reader (round-1 F4/F5/F7-F9)

Revision 1 refused a file whose first row looked like data. That is the
wrong verb — it tells a researcher their ordinary file is broken. The
reader now reaches an explicit verdict, states the evidence, and where
the evidence is not conclusive it stops and asks, offering
`--first-row names` and `--first-row data`. The verdict is published as
`source.header_source`.

The two-pass read now compares **values**, not only shapes. A file that
the stdlib reader and pandas parse into different cells is refused,
because a file two parsers read differently has no single correct
reading for us to publish. `c0,c1\n\r,B\nz,w\n` is the case that found
this; it is in the suite. Byte-order marks are detected at the byte
level rather than inferred.

### The two-file write (P1-R2-F11)

Both files appear or neither does. Each document is written to a
working neighbour in the destination folder — same filesystem, so the
commit is a rename — and only when both are complete on disk are they
renamed into place. A failed first rename removes the working files; a
failed second rename rolls the first back from the copy taken before it
was replaced. `rollback_failed` names every file left on disk rather
than reporting a clean failure it cannot vouch for.

Demonstrated under a file-size limit that fails the write midway: exit
1, the pre-existing profile **byte-intact**, no partial file, and the
message names the working file rather than the user's file.

### The taxonomy (round-1 F5)

`identifier` moved from third in the role order to second-to-last.
Round 1 added three guards to it; tracing round 5 showed each guard was
a patch on an ordering mistake — a rule that fires on uniqueness alone
was being tested *before* the rules that would have described the
column properly. Uniqueness is now what is left when no positive
description fits, which is what "identifier" means. The guards remain
as a check, not as the load-bearing part, and `--identifier` still
settles the irreducible case.

---

## Not done, stated plainly

- **The failure-catalog CLI tests and the case-variant header warning.**
  Built, but against the pre-redesign tree, and they do not merge onto
  the rebuilt reader without changes I could not verify in this round.
  They are withheld rather than merged unverified. The underlying
  catalog contract is still tested (`tests/test_failure_catalog.py`,
  one case per message builder); what is missing is the end-to-end
  CLI-driven variant and the collision warning.
- **P1-R3-F6** — the project wheel's own digest in the documented
  install. Cannot close before a release exists to have a digest.

`tests/test_failure_catalog.py` now marks `nothing_was_written` and
`rollback_failed` as clauses rather than standalone messages: they are
appended to a refusal that already says what to do, so the
actionable-wording rule is checked on the sentence they join. They are
still covered — they name files left on disk — and a separate rule
keeps them safe to append.

## The three owner decisions, unchanged and still open

1. Does Amendment A3's best-effort scope cover the pandas `read_csv`
   fence, or must Phase 1 keep chasing static closure?
2. numpy's withdrawal as a direct dependency — the round-1 numerics
   repair left it imported nowhere, which partly reverses the owner's
   "pandas + numpy as drafted" call. pandas is unaffected.
3. Whether the institutional install waits for a release to supply a
   governed wheel digest.

None is a code question, and none blocks the rest.

# Phase 1 review round 4 — implementer response

**Verdict received:** reject; 3 blockers, 2 majors.

**The ruling on the round-3 argument is accepted, and it went against
me.** I argued that the run-time re-validation in `_read_columns` meant
every route in P1-R3-F1 and F2 ended at a refusal rather than at real
harm, and that the remaining gap was the one Amendment A3 already
accepts. Round 4 answered with two runnable examples that reach real
harm, and both are correct:

* a module that imports `Path` and also defines a function called
  `Path` — the real validator accepted one file and the reader opened
  another through a web address;
* a module that imports `cast` and also defines one — the real
  validator ran, the real table was read, and then the user's own file
  was overwritten.

My argument had a false premise. I claimed the value handed to the
reader is the value the validator checked; in both examples something
between the two changed it. The run-time check is necessary and it is
not sufficient, and P1-D2.1 will say so.

The important part is that this is not the unbounded problem I took it
for. Both examples share one root cause, and it is closable: **a name
that is both imported and defined in the same module binds the
definition, and this audit went on trusting the import.**

## Repaired

**P1-R4-F1.** The audit now distinguishes two questions it had been
answering with one rule:

* *must this be checked?* — a name keeps every origin it has ever had,
  so a name that might still hold a dangerous module is still flagged.
  That is Phase 0's flow-insensitive union rule and it is unchanged;
* *may this be trusted?* — a name is the API only when EVERY origin it
  carries is that API. Provenance, value-preserving calls and fenced
  call targets ask this question.

Both of round 4's examples now fail the scan, the real source still
scans clean, and Phase 0's own dead-branch rebinding mutation still goes
red with its original message. Both examples are permanent red tests.

**P1-R4-F2**, all three parts:

* the sentinel share is taken over present values, as the plan always
  said, not over the representable numbers. The reviewer's case — 199
  values, one `-999`, one out-of-range number — now keeps `-999` as
  data: role continuous, minimum -999;
* every population is recomputed after a sentinel removal, so the
  summary no longer reports a negative number of values;
* a minus sign on an out-of-range number now rules out the count role.
  `1..99` plus `-1e999` is continuous, not a non-negative count. The
  value stays out of the statistics; its sign does not stay out of the
  routing.

**P1-R4-F3.** Identity now also compares resolved paths case-blind, and
fails closed. On a case-sensitive filesystem this can refuse a pair that
really is two files; that costs a re-run, while missing the pair costs
one of the two outputs.

**P1-R4-F5.** A test now asserts that the institutional install requires
exactly the runtime dependencies the package declares, so nothing —
numpy or anything else — can return as a root without the test failing.

## Open

**P1-R4-F4** — escaping still misses some format controls, and some
path-bearing refusals do not pass through it. Bounded and understood;
not in this round.

**The role for "numeric intent, nothing representable"** (the third part
of F2, and F4 from round 3). A column whose every value is a number too
large to hold is still called free text with the counts attached. The
counts make it honest; the role name is still thin. This needs a role,
which is a contract change.

**Still open from earlier rounds:** P1-R3-F6 (the project wheel's own
digest — needs an artifact that does not exist before a release),
P1-R2-F4 and P1-R2-F5 (the reference generator's own half-even and
zero-boundary defects — the top remaining priority), P1-R2-F11,
P1-R2-F13, and the round-1 items F4, F5, F7, F8, F9, F10 remainder,
F13's format-spec half, F15, F16, F17, F18, R1-X3.

## For the record, on the process

Round 4 was worth more than the three rounds before it, because it
tested a claim rather than a line of code. The claim was mine and it was
wrong, and the counterexamples are the reason the repair is a rule about
name binding rather than another patch. That is the review working as
intended.

## Standing state

598 tests pass; offline scan, decontamination, attestation, provenance
and all three lock pairs clean; ruff and mypy clean.

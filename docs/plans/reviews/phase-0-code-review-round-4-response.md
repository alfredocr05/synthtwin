# Response to Phase 0 code review — round 4

Implementer's answers to `phase-0-code-review-round-4.md` (three carried
residues, two new blockers, two minors). Every item is answered with a
class-closing fix; nothing is rebutted.

**R2-B2 (final residue) — fixed at the class level.** Module-level trust
is gone everywhere: every allowed module is attribute-enumerated (sys is
seven data attributes; typing is exactly the names src uses, with
targeted messages for the annotation evaluators), and the callback-slot
table is a stated complete audit of the closed surface across CPython
3.10-3.14 — the review's three named misses plus one more found in the
audit are all slots or bans now. The untraced-receiver data-method
exception is REMOVED; in its place, the isinstance type-gate upgrade
makes string methods exact call targets only on proven strings, and
shadowing the gate's built-ins is itself a violation. `src/` gained the
matching plain-language type guards. Seven new red mutations, each shown
green under the prior scanner.

**R4-B2 — fixed.** `typing.get_type_hints`, `ForwardRef`, and the
evaluator family are red with a message explaining they turn annotation
text into running code; the runtime demonstration is recorded in the
test.

**R2-B7 (final residue) — fixed.** The exemption is an explicit reviewed
file list — exactly the one workflow file that exists — and a NEW file
under the workflows directory is a violation until a maintainer lists
its exact path in a reviewed change; the directory-shaped route is
pinned out by test.

**R2-B11 (final residue) — fixed.** The last stale confinement claim (the
fixture-manifest schema note) now states the ratified truth: a
best-effort in-process guard; source review and CI are the operative
controls. The residual wording in the checker and test comments was
aligned too.

**R4-B1 — fixed in this refresh.** The evidence chain is now tree-exact:
the pre-refresh battery note names the exact tree it ran on and lists
the attestation-dependent tests it excludes (they can only pass at the
refresh commit); the post-commit record then attests the full suite at
the refresh head. No signed claim attributes a result to a tree that
cannot produce it.

**R4-m1 — fixed.** Scanner output is encoding-safe under a strict-ASCII
console while staying value-silent; the exit-code contract holds with a
non-ASCII filename present, proven under a forced ASCII writer.

**R4-m2 — fixed.** Amendment A2's heading and status line both state its
round-3 ratification.

**Request to round 5 (final):** verify the class closures, the tree-exact
chain, and the hosted CI result (the previous state's run is green on
all nine jobs; this state's run will exist by review time). Enumerate
the exact residue for Phase 0 acceptance behind the owner's
visibility/governance decision.

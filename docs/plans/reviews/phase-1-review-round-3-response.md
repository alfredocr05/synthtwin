# Phase 1 review round 3 — implementer response

**Verdict received:** reject; 6 blockers, 3 majors.

Six items are repaired. Three (P1-R3-F1, F2, and the receiver half of
F7) are answered with a narrowed claim and a stronger control rather
than with the closure they ask for, and the reasoning is set out below
so the next round can rule on it directly.

## Repaired

**P1-R3-F5 — identity failed open.** The worst of the six, and correct:
two dangling links to one missing file resolved equal, existed neither,
so identity answered "different" and both writes went to one place. The
rule now decides on resolved-path equality FIRST, regardless of
existence; adds filesystem identity when both exist; and answers YES on
any metadata error. A control that protects the user's data fails
closed: refusing a run that might have been fine costs a re-run, and
permitting one that overwrites their table costs the table.

**P1-R3-F3 and F4 — one classification, carried everywhere.** Every
present cell is now classified exactly once as a number, an
out-of-range number, contradictory numeric notation, or text; the
numeric-looking population (the first three) decides the role, so a
column of unrepresentable or contradictory values is no longer pushed
into identifier or text by a spent straggler budget. `n_out_of_range`
and `n_contradictory` are fields of EVERY column block, not of the
numeric one, because a count that appears only where someone remembered
it goes missing exactly when it matters. Both carry a remark that names
the notation and says what to write instead.

The debt-shaped input from F4 is now `free_text` with
`n_contradictory: 100` and a remark naming the ambiguity — visibly
declined rather than silently discarded. The role name is honest but
thin, and a dedicated outcome for "numeric intent, nothing usable" is
the better answer; it is not in this round.

**P1-R3-F9 — one escaping boundary.** `parsing.visible` now covers the
C0 and C1 ranges, DEL, the Unicode line and paragraph separators, and
the bidirectional and format controls, and it is applied by the summary
AND by the refusal catalog. Verified: with a header containing the
clear-screen sequence, and with the duplicate-name refusal the review
used, no raw escape reaches stdout, stderr, or the written summary.
Ordinary printable non-ASCII text is untouched.

**P1-R3-F8 — numpy as an install root.** Removed from
`requirements-install.in`; the lock is regenerated from pandas alone and
still pins numpy, transitively, as pandas requires it.

**P1-R3-F7 (the call-target half) — a closed grammar.** A call target is
now a bare name or a pure dotted chain and nothing else; a method
receiver must be a name, a dotted chain, a call, a literal, a subscript
or an f-string. Every conditional, boolean, walrus, starred and awaited
form in either position is refused outright. That is the reviewer's own
recommendation and it is better than enumerating shapes, because it
needs no new case for each syntax Python gains. All three forms from the
finding are red mutations.

## P1-R3-F1, F2, and receiver identity: the claim, narrowed

These ask the scanner to model Python's name binding faithfully enough
that provenance cannot be forged: class-namespace lookup, `match`
captures, shadowed imports, inherited attributes. Two rounds of repairs
have each been met with a deeper variant of the same class, and there is
no reason to expect the fourth attempt to end differently.

The project has already ruled on this class. **D6 Amendment A3**,
ratified with conditions at Phase 0 closure, records that this scanner
"does not establish universal call-target closure", that a reading-only
analysis could reject every construct it cannot resolve but that ours
"accepts some of them on purpose, because rejecting them would require a
source dialect so restrictive that the tool would stop being usable",
and that the project accepts that bounded gap with the residual named.
F1 and F2 are that gap, in the specific shape of the fence.

What is repaired is the CLAIM, and one control that the review's model
does not account for:

- **the operative control is at runtime, not in the scanner.**
  `_read_columns` calls `validate_local_path` immediately before it
  calls the reader, on the value it is about to hand over. A forged
  static provenance therefore does not reach the network: it reaches the
  validator, which refuses it. Demonstrated:

      reading._read_columns("https://example.invalid/table.csv", ...)
      -> PathValidationError: ... it looks like a web or network address

  Every route F1 and F2 describe ends at that call. What a forgery buys
  is a source tree that passes the scanner while failing at run time,
  which is a maintenance defect rather than an escape.
- **the scanner is one layer, and is described as one.** P1-D2.1 is
  amended to say that the runtime re-validation is the control and the
  static provenance rule is defence in depth against a source change
  that removes it, with the A3 residual named. Every mutation from
  rounds 1 to 3 stays red, and the closed grammar above removes the
  whole receiver-shape family rather than one member of it.

If the review holds that a best-effort static fence plus a runtime
refusal is insufficient, the decision is a plan-level one about A3's
scope, which belongs to the owner rather than to this response. It is
flagged for the owner beside the numpy question.

## Open

**P1-R3-F6** — the project wheel's own digest is not verified in the
documented procedure. Real, and the repair needs a governed digest that
does not exist in this phase: no release exists to publish one. The
honest options are to state the gap in `SECURITY.md` or to add a signed
digest artifact, and that is an owner decision.

**P1-R2-F4 and F5** — the accuracy contract and the oracle's own
half-even and zero-boundary defects. F5 first: an oracle that reports a
negative standard deviation cannot anchor acceptance. Still the highest
priority of the remaining work.

**P1-R2-F11, F13**, and the round-1 items already listed as open:
F4, F5, F7, F8, F9, F10's remainder, F13's format-spec half, F15, F16,
F17, F18, R1-X3.

## Standing state

595 tests pass; the offline scan, decontamination, attestation,
provenance and all three lock pairs are clean; ruff and mypy are clean.

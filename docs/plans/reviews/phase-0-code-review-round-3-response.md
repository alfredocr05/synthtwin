# Response to Phase 0 code review — round 3

Implementer's answers to `phase-0-code-review-round-3.md` (five blockers,
one major, two minors, plus the ratified D14 Amendment A2 and the noted
external push). Every item is answered with a fix. The history is repaired
forward, never rewritten, per the round-3 instruction.

**On the push:** the repository was created and pushed by the project
owner before the round-3 verdict, as the review detected. It was created
PRIVATE; branch/tag rulesets are unavailable on that tier, so the D14
settings that could be applied now (read-only workflow tokens) are
applied, and the rest are queued behind the owner's visibility decision.
No tag, release, or Phase 1 work has begun.

**R3-B1 (invalid workflow YAML) — fixed first and pushed immediately.**
The colon-space plain-scalar defect was repaired to a block scalar, the
full document validated with a YAML parser, and the fix pushed so hosted
CI could instantiate. The first real run then exposed four
environment-parity defects, all fixed: the universal lock lacked a 3.10
floor (tomli/exceptiongroup markers now present); the test-suite socket
guard is now a subclassable class (stdlib ssl subclasses it at import);
a `.gitattributes` disables all end-of-line conversion so signed digests
survive Windows checkouts byte-exactly (a real D12 canonicality gap);
and scanner output plus non-ASCII test writes are explicit about
encoding. The network-none container build passed on the real runner at
first attempt.

**R2-B2 — fixed.** Call-position-aware callback rejection over the closed
allowlisted world: every callable-accepting slot of every allowed API is
enumerated, and any unknown, parameter-derived, or first-party value in
such a slot is a violation, as is star-expansion into a slot-bearing API.
The untraced data-method exception now requires every argument to be a
literal or fully resolved known-safe origin. Red mutations cover the
review's three named routes and more; data arguments stay green.

**R2-B4 — fixed.** The verifier parses with a duplicate-rejecting hook at
every nesting depth; a validly signed graph carrying a duplicated member
is schema-invalid with the member named. Both demanded temp-key re-signed
mutations are red against the prior verifier and pass now.

**R2-B7 — fixed.** The YAML exemption is exactly `.github/workflows/`
single-level `*.yml`/`*.yaml`; a data file elsewhere under `.github/` is
a violation with a red test.

**R2-B11 — fixed.** The guard now blocks IMPORTS of the dangerous module
families at the import audit event (socket, ssl, ctypes, cffi,
subprocess, multiprocessing, pty, fcntl and their underscore twins) in
addition to a widened event list, and the claim is narrowed in both
files to what it is: a best-effort in-process guard aligned with the
project's documented posture, with CI as the enforced boundary. The
review's low-level process and native routes are red tests now.

**R3-M1 — fixed.** The battery records each mode's scanner exit status
and stderr and fails unless the status is exactly match-only; a
match-plus-violation self-test proves the discipline.

**R3-m1 — fixed.** The installer resolves the active hook path through
git itself (honoring custom hook paths and linked worktrees), with tests.

**R3-m2 — fixed.** The public magic table now labels itself as the public
attestation-bound copy.

**Evidence chain.** As scheduled by both signed records, this refresh
binds the existing post-commit verification artifact; after the new
attestation commit, a new post-commit record is produced and signed for
that head without any self-binding claim. The verifier schema gains the
corresponding binding key in the same change.

**Request to round 4:** verify the resolutions and the first green hosted
CI run; rule on any residue. Governance items stay
pending-public-verification behind the owner's visibility decision.

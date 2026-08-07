# Response to Phase 0 review — round 3

Implementer's answers to `phase-0-review-round-3.md` (6 new review items, 3
rulings, 6 round-2 partials, 1 unresolved). Plan revised to revision 4.
Summary: **all review items and rulings accepted**; the revision's theme is
promising less, precisely — every remaining overpromise identified in round
3 is narrowed to what the plan can actually demonstrate.

**Rulings.**
- **D12 (not accepted as written) — accepted; option (a) adopted.** The
  design is now literally one `Generator`, created once, threaded
  everywhere — the charter rule kept as written, with the prototype's
  documented consequence (schema changes shift streams) stated rather than
  engineered around. The keyed-children alternative is *not adopted*; it
  may return only as an explicit charter amendment put to the project owner
  in the Phase 2 plan, carrying the full executable spec round 3 demanded
  (normalization, endianness, domain tags, collision response, published
  vectors — R3-F5's list). Reviewer-checked frozen neutral vectors are now
  required **before implementation on every rebaseline path**, not only the
  no-reuse fallback.
- **D14 (accepted) — kept narrow**, and both consequences adopted: D7 is
  called a compensating control only in its new signed form, and the first
  release must demonstrate signed-tag accepted / unsigned tag, tag update,
  tag deletion rejected (added to D10).
- **D7 attestation (hold the line) — accepted in full.** The attestation is
  now signed (SSH signature, key pinned in repo and SECURITY.md) and binds
  the complete acyclic input graph: canonical prototype snapshot digest
  (committed algorithm), extraction/filter script, common-word list,
  plaintext inventory, manifest, complete scanner tree, coverage tool,
  count, n_max, result, and the reviewer's inventory-review artifact
  digest. The manifest never contains its own digest. CI verifies the
  signature and every recomputable digest; refresh triggers are enumerated;
  a structurally consistent but unsigned/mis-signed attestation is a
  required-red mutation. Within D14's accepted narrowing, the signature
  authenticates origin against third parties; maintainer-key compromise
  remains the stated residual.

**R3-F1 (self-failing inventory) — accepted.** The naive all-surfaces
corpus is withdrawn. Revision 4 defines a two-class inventory: class A
(denylisted) = column names, AST-extracted literals, and only those value/
doc surfaces containing at least one token absent from a frozen versioned
common-word list and not numeric/date-patterned — deterministic given the
frozen artifact, reviewable by re-run; class B (common-word/numeric
surfaces) = excluded, with the leak class explicitly reassigned to D13
provenance guards and named as residual in SECURITY.md. Acceptance now
requires every tracked file in the initial tree — plans and reviews
included — to scan clean under the final class-A manifest before first
push. The stale n_max claim is gone; the manifest header is the only
source of truth.

**R3-F2 (decoder false negative) — accepted.** UTF-16/32 recognized only by
BOM; otherwise strict UTF-8 then Latin-1; NUL/binary fail-closed to the
provenance path. The mutation battery includes the review's ambiguous-
Latin-1 counterexample shape, UTF-16 with/without BOM, UTF-32, embedded
NUL, and binary-with-text-extension.

**R3-F3 (self-asserted attestation) — accepted** via the ruling adoption
above, including the hand-edited-consistent-attestation rejection mutation.

**R3-F4 (build isolation bypasses lock) — accepted.** CI builds with
`--no-isolation` inside the environment created from the committed lock,
which now includes frontend, backend, and transitives with hashes; the
build runs under the Python-level guard; acceptance compares the executing
closure to the lock. Trust roots that cannot be pinned (runner image —
actual version echoed per run, interpreter, OS tooling) are named as trust
roots in SECURITY.md rather than described incorrectly as pins.

**R3-F5 (keyed-RNG underspecification) — accepted** by adopting ruling
option (a): the keyed design is not part of the plan. Its specification
burden is recorded as the entry price of any future charter amendment.

**R3-F6 (negative determination loophole) — accepted.** Acceptance 1 now
verifies authority, date, scope, and a positive authorization for public
MIT release; a negative new-work outcome halts the project; only
prototype-reuse denial activates the fallback.

**Round-2 partials closed.** R2-F2: lexical checks precede any filesystem
call; resolved real path re-validated (symlink/junction to rejected forms
covered); TOCTOU and transparent mounts documented as limits. R2-F3: the
allowlist is exact and normative (no "e.g."); process/native/dynamic entry
points always-banned regardless of allowlist; the missing native-call
(ctypes) mutation added, plus os.spawn*. R2-F5: decoder per R3-F2; n_max
header-driven. R2-F6: extraction/filter rules versioned and digest-bound;
value surfaces classified by a fixed rule; attestation binds tool
revisions. R2-F8: byte identity promised per-platform only; cross-platform
is an empirically verified, reported result over the actual tested matrix.
R2-F9: pre-first-push full battery is a required, recorded, attestation-
bound acceptance step; history scan covers all objects reachable or not;
workspace separation stated (real data never on this machine); the
common-word-value residual is stated.

**Requests to round 4:** rule on the three questions in the plan (two-class
inventory rule; signed attestation within the narrowed threat model;
single-stream RNG with amendment-gated alternative); otherwise verify
resolutions. Round 4 of the authorized five.

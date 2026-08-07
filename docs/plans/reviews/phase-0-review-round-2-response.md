# Response to Phase 0 review — round 2

Implementer's answers to `phase-0-review-round-2.md` (13 new review items; 8
round-1 partials; 1 unresolved; 3 rulings). Plan revised to revision 3.
Summary: **all 13 new review items accepted** — two of them (R2-F10, R2-F12) via
the narrowing/deferral options the review itself offered; all three rulings
adopted, including the two where the reviewer held the line. Nothing
rebutted.

**Rulings.**
- **D6 scope (convinced on scope, controls blocked):** controls rebuilt —
  see R2-F2/R2-F3 below.
- **D2 (hold the line) — adopted in full.** The plan now blocks any public
  commit on a dated written determination from the institutional IP
  authority; the reviewer verifies the document exists (privately) as
  acceptance criterion 1; the repo records date/outcome only. The clean-room
  claim is withdrawn; the fallback is deferred to the phase that would need
  it, with an authorized public contract + independently checked reference
  vectors as that phase's deliverable (also resolves R2-F12 and the F10/F11
  partials).
- **D7 (hold the line) — adopted in full.** Machine-verifiable attestation
  binding prototype-snapshot, inventory, manifest, and scanner digests plus
  entry count, n_max, and result; committed publicly (digests only); CI
  fails on manifest/scanner drift without a fresh matching attestation;
  initial inventory independently reviewed by the adversarial reviewer, who
  has read access to the private notes; review named in the attestation.

**R2-F1 (hash-pinned user install) — accepted.** D5/D10: the first
dependency-bearing release ships a generated `--require-hashes` install file
as a release artifact, CI installs from it offline and smokes it, and
SECURITY.md names it the supported institutional path.

**R2-F2 (path locality) — accepted.** D6.1 now specifies canonicalization,
URL-scheme rejection, Windows UNC/device-form rejection **before any
filesystem call** (the review's SMB-on-existence-check scenario), coverage
of output and temp paths, per-platform tests, and an explicit documented
limit for OS-transparent network mounts.

**R2-F3 (capability enforcement) — accepted.** The denylist is replaced by a
**positive import allowlist** for `src/` (Phase 0: minimal stdlib only);
dynamic loading (`__import__`, `importlib.import_module`, `exec`, `eval`,
`compile`) is banned outright, closing the dynamic-import route; process and
native entry points are enumerated; D6.5 adds one mutation demo per bypass
class; the test wrapper is renamed a "Python-level guard" everywhere —
never "network disabled".

**R2-F4 (private-notes path resolves inside repo) — accepted.** Path
corrected to three levels up (sibling of the repo root); `planning-notes/`
also ignored in-repo as defense in depth; acceptance tests that the
documented path resolves outside the repo root.

**R2-F5 (matcher self-inconsistency) — accepted.** Order corrected: tokenize
on case transitions and letter/digit boundaries **before** NFKC/casefold;
the n-gram cap is gone — candidates run to the **n_max recorded in the
manifest header** (measured max 14); decoding BOM-sniffs UTF-8/16/32 with
Latin-1 byte fallback and fails closed on undecodable input; archives/
binaries route to the D13 violation path; cross-form equivalence tests are
parameterized over every promised form.

**R2-F6 (inventory completeness + binding) — accepted.** Corpus is the
complete prototype snapshot (all files, including the example scripts, the
shell script, and both example artifacts), with deterministic versioned
extraction rules per surface class — explicitly including the displayed
category-label and relationship-group value surfaces the review measured
(262/117 values). The commit-message count is replaced by the bound
attestation above.

**R2-F7 (RNG contract) — accepted.** Revision 2 implied prototype
compatibility it did not deliver; revision 3 makes the **rebaselining
decision explicit**: rules and statistical contract preserved, byte streams
not, put to round 3 as charter-interpretation question 1. The positional
`spawn(n)` scheme is replaced by **stable keying**: per-column entropy =
(master seed, SHA-256 of column name); duplicate names are a load-time input
error, so keys cannot collide; insertion/reordering provably cannot shift
other columns' streams.

**R2-F8 (byte-identity overpromise) — accepted.** Two honest tiers:
guaranteed byte identity only for the exact locked closure, enforced by
golden hashes on every CI platform; across numpy versions the guarantee is
the statistical contract, stated in SECURITY.md/README, with golden
regeneration an explicit changelogged event. Date/time canonicalization
(ISO 8601, explicit offset, fixed precision) added.

**R2-F9 (provenance guard depth) — accepted.** Fixture manifest binds path →
script → seed → digest; CI **rebuilds and byte-compares** every committed
fixture; substitution mutation added; pre-push hook gives a pre-public
check (honestly labeled advisory); initial acceptance runs a full-history
object scan; a purge/notification incident procedure is documented.

**R2-F10 (sole-maintainer tamper limit) — accepted via the review's own
narrowing.** Cheap hardening adopted: `gate` context bound to the GitHub
Actions app, signed release tags, tag create/update/delete protection,
workflow/tools-path change surfacing. The residual compromised-maintainer
risk is **stated, not papered over**, in SECURITY.md, with the compensating
controls users can verify. Question 2 to round 3 asks whether the narrowed
claim is acceptable.

**R2-F11 (required-check identity) — accepted.** A single `always()`
aggregate `gate` job fails unless every upstream job succeeded; the ruleset
requires exactly that context, app-bound.

**R2-F12 (fallback lacks a public oracle) — accepted via deferral.** Phase 0
no longer claims public specifications/vectors exist; the fallback is a blocking
deliverable of the phase that ports numerics, prepared and independently
checked before implementation (folded into D2/D3).

**R2-F13 (count correction) — accepted.** Normative counting is the
executable AST extraction rule; prose counts dropped.

**Round-1 partials:** F2 → installer/build-frontend/twine/runner rows added
(D5). F3 → R2-F2/R2-F3. F4 → R2-F4. F5 → R2-F5. F6 → R2-F9. F8 → R2-F10/
R2-F11. F10/F11 → D2/D3 + rulings. F9 (unresolved) → R2-F7/R2-F8.

**Requests to round 3:** rule on the three questions in the plan (D12
rebaselining, D14 narrowed claim, D7 attestation design); otherwise verify
resolutions.

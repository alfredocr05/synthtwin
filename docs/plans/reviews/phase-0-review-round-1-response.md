# Response to Phase 0 review — round 1

Implementer's answers to `phase-0-review-round-1.md` (15 review items). Plan
revised to revision 2 in place (`../phase-0-public-skeleton.md`). Per the
process, every finding gets a fix or a written rebuttal. Summary: **13
accepted in full, 2 accepted with a scoped position stated** (F3, F11 — both
adopt an option the review itself offered). Nothing is rebutted outright.

This document, like the revised plan, avoids reproducing denied vocabulary.

---

**F1 (blocker, deps/pinning) — accepted.** Phase 0 now ships **zero** runtime
dependencies (D5). The dependency-introduction protocol separates tested
minimums from the frozen-mode lock; CI tests both resolutions. The plan no
longer implies a lockfile governs `pip` consumers; hash-pinned installs are
assigned to the standalone build and a shipped hashed requirements file.

**F2 (blocker, supply-chain language) — accepted.** D5 adds the by-role
inventory (runtime direct/transitive, build, dev, CI, release) maintained in
`SECURITY.md`, with per-row "executes on user machine?" and SBOM + closure
hashes from the first release. All audit claims rephrased to "direct runtime
dependencies" with the closure enumerated beside them.

**F3 (blocker, offline boundary) — accepted, adopting the review's offered
narrowing.** D6 now defines the production boundary first: pure-Python code
with no network/subprocess/native constructs, local-file input validation as
a *runtime product rule* (URL-schemed inputs rejected — closing the
data-frame-reader URL hole the review identified), and full functionality
air-gapped. Scoped position: OS-level syscall enforcement is not promised —
a cross-platform pure-Python tool cannot deliver it without privileged
dependencies that violate D5; the review's own alternative ("narrow the
guarantee explicitly rather than silently") is taken, and `SECURITY.md`
directs institutions that need enforcement to network-isolated deployment.
Concrete fixes adopted: guard installed at conftest **import time** (active
during collection and module import), subprocess/os.exec/ctypes added to the
static denylist, and a built-artifact offline install + CLI smoke test added
(with D9's build job).

**F4 (blocker, plaintext + exemptions) — accepted in full; round-1 design
withdrawn.** D7 is now a hashes-only manifest with **zero content
exemptions**; the briefs and all plans (including the plan itself, which the
review correctly noted contained denied literals) are sanitized; the
plaintext inventory lives only in the maintainer-private planning notes
outside the repository. The review's answer to question 1 is adopted as
written.

**F5 (blocker, coverage undefined) — accepted.** D7 now specifies the
normalization/matching contract (NFKC, casefold, identifier splitting on
case/underscore/hyphen/digit boundaries, word n-grams ≤ 5, path scanning,
Latin-1 byte fallback, fail-closed reads), enumerated surface variants
instead of algorithmic stemming, and inventory regeneration from the
prototype covering **all 288 profile column names** plus every study string
constant — closing the 42-of-288 gap the review measured. Verification is
two-tier because public tests cannot hold plaintext: public machinery
self-tests with shaped neutral canaries; maintainer-side full-inventory
parameterized coverage run, required and recorded. Every newly discovered
escaping form adds an inventory entry + a public canary of the same shape.
Whether this two-tier split is acceptable is explicitly put to round 2
(question 3).

**F6 (blocker, real-derived artifacts) — accepted.** New D13: day-one
prohibition on real and real-derived artifacts (explicitly including the
prototype's example profile files), generated-fixture provenance rule,
root `.gitignore` defaults, and a CI provenance job with an
allowlist-with-justification and an inserted-file mutation demo. The build
job's sdist/wheel content allowlist (D9) closes the same class at the
artifact level.

**F7 (blocker, release before integrity controls) — accepted.** The
placeholder release is withdrawn entirely (D10): no PyPI publication until
the first genuine capability, and that release must satisfy Trusted
Publishing, attestations, protected release environment, reproducibility
comparison, hashes + SBOM — requirements fixed now, mechanics in the
releasing phase's plan.

**F8 (blocker, unenforced governance) — accepted.** New D14 specifies the
ruleset (PR-only, named required checks, no force-push/deletion, no bypass),
protected `v*` tags, read-only default workflow permissions, no
`pull_request_target`, fork-workflow approval, 2FA. Acceptance criterion 2
verifies **settings via the API**, not green runs.

**F9 (blocker, determinism truncated) — accepted.** D12 restates all five
prototype obligations (including no-replacement identifier draws,
schema-driven output order, deterministic special-element selection), fixes
the RNG API decision (`numpy.random.Generator`/PCG64 with per-column spawned
children), defines the byte-identity scope (profile + seed + version, across
supported OS/Python, numpy within locked range), and mandates canonical
serialization — UTF-8, explicit `\n` (the OS-default-newline hazard the
review cited), documented float formatting, sorted-key JSON — with
golden-hash tests from the first file-writing phase.

**F10 (major, sibling-path dependence) — accepted.** D3: briefs are
sanitized, renamed, and honest that the prototype is maintainer-private;
the public verification path is the repo's specifications, neutral seeded golden
vectors, and CI; prototype-diff review is labeled maintainer/reviewer-only.
No real-derived examples are copied in (per D13).

**F11 (major, license provenance) — accepted with one scoped position.** D2
names the copyright holder, requires maintainer confirmation against
institutional IP policy *before the first public commit*, records the
outcome in the README license section, states inbound=outbound contribution
licensing, and adopts the review's clean-room fallback for any prototype
line whose authority cannot be documented. Scoped position: written
institutional confirmation is a maintainer action outside the repo; the plan
makes it a precondition rather than blocking the plan's approval on it —
whether that suffices is explicitly put to round 2 (question 1).

**F12 (major, artifacts untested / entry point undecided) — accepted.** With
the release withdrawn, the artifact pipeline still exists and is tested: D9
adds a required **build** job (clean-checkout wheel + sdist, `twine check`,
content allowlist, fresh-venv offline install, CLI smoke). D4 decides the
console entry point (`synthtwin = synthtwin.cli:main`) and the single
version source (`pyproject.toml` via `importlib.metadata`).

**F13 (major, name reservation) — accepted.** D1 treats availability as
unverified until an authorized upload succeeds; no reservation mechanism is
claimed; the rename risk is accepted and documented. (Release withdrawal per
F7 removes the squat-risk vehicle entirely.)

**F14 (minor, stale name in briefs) — accepted.** D3: the canonical in-repo
briefs are renamed to `synthtwin` with a short historical note; parent
copies retired at repo creation.

**F15 (minor, Python version policy) — accepted.** D4/D9: CI matrix now
includes 3.14; policy recorded — the floor tracks security-supported
CPython, 3.10 dropped in the first minor release after its 2026-10 EOL, new
stable versions enter CI within one release.

---

## Requests to round 2

Confirm or contest the three scoped positions now embedded in the plan
(D2 provenance precondition, D6 explicit narrowing, D7 two-tier
verification) — they are restated as the plan's "Questions explicitly put to
round-2 review".

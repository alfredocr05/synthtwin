# Phase 0 plan review — round 3

**Reviewed:** `docs/plans/phase-0-public-skeleton.md` (revision 3), the
round-2 response, the prior reviews/responses, the charter, and the read-only
prototype  
**Verdict:** **request changes**  
**New finding count:** 6 — 5 blockers, 1 major

Revision 3 closes several concrete gaps: the private-notes path is now outside
the repository, the first dependency-bearing release gets a hash-pinned user
install, the CI matrix has one aggregate required gate, and the sole-maintainer
tamper claim is materially more honest. It is still not implementable as
ratified. The expanded decontamination inventory makes the plan and response
fail their own zero-exemption scanner; the attestation is a self-asserted JSON
that does not prove the private run happened; default build isolation bypasses
the frozen project lock; and D12 still replaces the charter's one-RNG rule with
multiple generators while saying that rule was preserved.

## Resolution of every round-2 finding

| Round-2 finding | Status | One-line evidence from revision 3 |
|---|---|---|
| **R2-F1 — hash-pinned user install** | **Resolved** | D5 lines 92–99 and D10 lines 247–251 put a fully hash-pinned install file, its guarded smoke test, and its user-facing consumption command at the first dependency-bearing release. |
| **R2-F2 — path locality** | **Partially resolved** | D6.1 lines 124–136 covers input/output/temp paths, direct UNC forms, and the remote-mount limit, but orders `Path.resolve()` beside a promise to reject before filesystem access and never decides how symlinks, junctions, or post-resolution remote targets are handled. |
| **R2-F3 — capability enforcement** | **Partially resolved** | D6.2–D6.5 lines 137–160 improves to an import allowlist, but the allowlist is only an `e.g.` list and allowed `os` APIs still include process-launch routes not named by the scanner; there is also no native-call mutation despite the response's claim. |
| **R2-F4 — private-notes path** | **Resolved** | Lines 12–18 use the correct three-level relative path, add an in-repo ignore as defense in depth, and acceptance verifies that the resolved target is outside the repository root. |
| **R2-F5 — matcher contract** | **Partially resolved** | Lines 171–186 correct identifier-splitting order and make `n_max` manifest-driven, but the decoder selection can silently choose the wrong successful codec; the stated measured maximum of 14 is also stale for the newly expanded corpus. |
| **R2-F6 — inventory completeness and proof** | **Partially resolved** | Lines 187–210 enumerate more source surfaces and attestation fields, but the document-term extraction rule is still deferred, the unfiltered value surfaces make the scanner self-fail, and the attestation neither authenticates the private run nor binds the extraction/filter and coverage-tool revisions. |
| **R2-F7 — RNG contract** | **Unresolved** | D12 lines 263–286 admits stream rebaselining but replaces “one RNG, passed everywhere” with multiple per-column generators; the keyed derivation is also underspecified and the required independent vectors are guaranteed before implementation only in D2's no-reuse fallback. |
| **R2-F8 — byte-identity scope** | **Partially resolved** | Lines 287–302 add honest cross-version language and date/time serialization, but still promise every supported OS/Python combination while D9 tests all Python versions only on Ubuntu and only 3.14 on macOS/Windows; NumPy limits stream compatibility to much stricter same-build/environment conditions. |
| **R2-F9 — provenance depth** | **Partially resolved** | D13 lines 309–325 adds regeneration, a substitution mutation, and incident handling, but the hook remains advisory and is not required before the first push, the “full” scan covers reachable commits only, workspace separation is absent, and ordinary source literals remain outside fixture provenance. |
| **R2-F10 — sole-maintainer tamper limit** | **Resolved** | D14 lines 327–353 expressly excludes compromised-maintainer and insider resistance and states the remaining controls as verifiable compensations, which is the narrowing round 2 offered. |
| **R2-F11 — required-check identity** | **Resolved** | D9 lines 238–243 defines one `if: always()` aggregate gate over every upstream job, and D14 binds that exact context to the GitHub Actions app. |
| **R2-F12 — public fallback oracle** | **Resolved** | D2/D3 lines 41–46 and 57–63 withdraw the Phase 0 oracle claim and make an authorized public contract plus independently checked vectors blocking work for the future phase that needs the port. |
| **R2-F13 — inaccurate count** | **Resolved** | D7 lines 217–219 removes the prose count and makes executable AST extraction normative. |

Result: **6 resolved, 6 partially resolved, 1 unresolved.** The remaining
partials are substantive; R2-F2, R2-F3, R2-F5, R2-F6, R2-F8, and R2-F9 still
leave a promised security, decontamination, determinism, or provenance route
unproved.

## Resolution of the round-1 carryovers

The requested eight round-1 partials are all included below. I also include
round 2's unresolved F9 so the determinism carryover is not hidden.

| Round-1 carryover | Status | One-line evidence from revision 3 |
|---|---|---|
| **F2 — full supply-chain accounting** | **Partially resolved** | D5 lines 100–110 names the missing roles, but lines 103–104 explicitly let an isolated build resolve and execute a backend outside the frozen project lock; the interpreter and actual mutable runner image are not a pinned build closure. |
| **F3 — offline boundary** | **Partially resolved** | The scope narrowing remains acceptable, but the path-indirection and allowed-API gaps in R2-F2/R2-F3 remain. |
| **F4 — plaintext/exemptions** | **Resolved** | The public design is hashes-only with zero content exemptions, and the plaintext source path now resolves outside the repository. |
| **F5 — inventory and matching coverage** | **Partially resolved** | Matching mechanics improved, but the expanded corpus contradicts the clean-tree acceptance test and the decoder admits a false-negative route. |
| **F6 — real/real-derived artifacts** | **Partially resolved** | Fixture regeneration is real progress, but the pre-public sequence, unreachable objects, workspace separation, and values embedded in ordinary source remain uncovered. |
| **F8 — repository governance** | **Resolved** | Enforceable branch/tag/check controls are planned and the unavailable insider guarantee is withdrawn; this ruling does not validate the separate D7 attestation. |
| **F10 — public self-containment** | **Resolved** | Phase 0 now honestly says the numerical public oracle does not exist yet and assigns it as a blocking future-phase deliverable before port implementation. |
| **F11 — license provenance** | **Partially resolved** | D2 requires independent written institutional authority, but acceptance checks only that a dated document exists and records its outcome, not that the outcome affirmatively permits the MIT release; see R3-F6. |
| **F9 — determinism (round-2 unresolved)** | **Unresolved** | Serialization is better specified, but D12 still contradicts the charter and prototype rule requiring one RNG used everywhere. |

## Rulings on the three round-3 questions

### 1. D12 rebaselining — **not accepted as written**

Rebaselining the new product's exact draw bytes is acceptable **in principle**;
round 2 explicitly allowed an ratified rebaseline backed by independent
vectors. That does not make the current text a valid charter interpretation.
`CLAUDE.md` lines 120–122 says “one RNG, passed everywhere,” and the prototype's
first determinism rule says one RNG object is used for everything. D12 instead
creates one generator per column and more for internal structures. One entropy
source is not one RNG.

Exact resolution: either (a) use one `Generator` threaded everywhere while
retaining the openly declared stream rebaseline, or (b) obtain an explicit
charter amendment before plan approval. In either case, the independent neutral
vectors must be reviewer-checked and frozen **before** implementation on every
rebaseline path, not only when prototype reuse is denied. Newly generated
goldens may not be their own oracle.

### 2. D14 narrowed tamper-resistance claim — **accepted**

For a one-person project, it is honest to claim resistance to unauthorized
third-party changes while disclosing that a compromised maintainer account and
insider action are residual risks. The plan no longer pretends self-review is
separation of duty. Keep that narrow wording.

Two consistency consequences follow from promises already in the plan: D7 may
be called a compensating control only after its attestation is made genuine,
and the first release's acceptance must demonstrate that a signed release tag
is accepted while an unsigned tag and tag update/deletion are rejected. Neither
consequence expands the tamper claim.

### 3. D7 attestation design — **not accepted; hold the line**

The JSON described at lines 199–210 is internally consistent, not an
attestation of origin. Public CI can recompute only the public manifest and
scanner digests. Anyone able to edit the branch can write those current
digests, set `result` to `pass`, and type the reviewer's name without running
the private coverage tool or obtaining the review. The attestation also omits
the extraction/filter script, complete scanner/tool tree, coverage tool, and
review artifact digests.

Exact resolution: define an acyclic binding graph; bind the canonical prototype
snapshot algorithm and digest, extraction/filter revision, plaintext inventory,
manifest, complete scanner tree, coverage tool, count, `n_max`, result, and the
review artifact; authenticate the issuer/reviewer approval with a signature or
immutable external approval record; and enumerate every refresh trigger. The
manifest must not contain its own digest.

## New defects introduced or exposed by revision 3

### R3-F1 — blocker — D7 inventory and acceptance (`phase-0-public-skeleton.md:166–219, 369–374`; response lines 52–66)

**Defect:** Unfiltered inclusion of every displayed label and relationship
group value makes the zero-exemption denylist reject the revised plan and its
response, so the response's claims of a complete corpus and a clean design
cannot both be true.

**Concrete failure scenario:** The implementer faithfully generates the
manifest from the 475 promised raw value surfaces. After the specified
normalization there are 374 unique entries, 148 of them one token. The plan
contains 17 distinct matches across 121 lines, and the response contains 15
across 37 lines. CI scans those tracked documents, finds the hashes, and the
required `decontam` job can never turn green without either omitting promised
entries or adding the forbidden exemption. The strict corpus also has
`n_max = 28`, not the claimed measured maximum of 14.

**Required change:** Separate objectively source-specific lexical entries from
ubiquitous/numeric value surfaces using a deterministic, reviewable rule. Cover
the excluded common-value leak class through the provenance/artifact guard
rather than a global token denylist. Freeze and review the exact resulting
inventory, then prove every tracked revision-3 file scans clean before the
first public commit.

### R3-F2 — blocker — D7 decoding (`phase-0-public-skeleton.md:171–186`; acceptance 5)

**Defect:** “Try UTF-8, then UTF-16, then UTF-32, then Latin-1” is not a valid
encoding detector: an earlier wrong codec can decode successfully, preventing
the scanner from reaching the encoding that preserves the denied tokens.

**Concrete failure scenario:** A tracked text file begins with a non-UTF-8
Latin-1 byte and then contains a denied multi-token entry. UTF-8 raises, but
UTF-16 accepts the even-length byte sequence as unrelated characters; the
scanner records no match and CI stays green even though Latin-1 decoding would
have exposed it. A neutral local proof reproduced exactly that control flow.

**Required change:** Recognize UTF-16/32 only from a BOM (or a separately
specified validated detector); absent a BOM, use strict UTF-8 then Latin-1,
with explicit NUL/binary detection routed fail-closed. Add neutral mutations
for ambiguous Latin-1, UTF-16/32 with and without BOM, embedded NULs, and a
binary file disguised with a text extension.

### R3-F3 — blocker — D7 attestation (`phase-0-public-skeleton.md:166–210, 369–374`; response lines 21–26)

**Defect:** The proposed unsigned, same-repository JSON is self-asserted and
incompletely bound, so it cannot prove either a fresh private full-inventory run
or the claimed independent review.

**Concrete failure scenario:** A filter-rule change drops a rare private
inventory entry. A contributor updates the public manifest, copies its new
digest and the scanner digest into the JSON, leaves an arbitrary private-input
digest, sets `result` to `pass`, and preserves the reviewer's name. Public CI
can recompute every value available to it and passes, although neither the
coverage run nor the review occurred.

**Required change:** Apply the binding/authentication design in the D7 ruling,
and add a mutation that hand-edits a structurally consistent but unauthenticated
attestation and proves CI rejects it.

### R3-F4 — blocker — D5/D9 build closure (`phase-0-public-skeleton.md:89–110, 231–251, 365–368`)

**Defect:** The frozen project lock does not constrain the backend installed by
default `python -m build` isolation; D5 explicitly says that backend resolves at
build time, leaving an executing supply-chain node mutable.

**Concrete failure scenario:** CI consumes the project lock frozen, then the
isolated builder downloads a newly compromised backend transitive. That backend
injects dormant code into an allowlisted wheel path. Filename inspection and a
stub smoke path pass, and later hashes/SBOM/provenance faithfully bless the
malicious artifact. PyPA documents that an isolated build creates a temporary
environment and installs its own build requirements there
([PyPA build isolation](https://build.pypa.io/en/latest/explanation/how-it-works.html)).

**Required change:** Hash-lock and prefetch the complete build-frontend,
backend, and transitive closure; build with network unavailable using that
closure (`--no-isolation` with a verified environment is one valid design);
compare the executed closure to the lock in acceptance. Inventory the exact
interpreter and actual runner-image identity as executing trust roots rather
than treating a mutable `-latest` label as a pin.

### R3-F5 — blocker — D12 keyed RNG architecture (`phase-0-public-skeleton.md:272–286`)

**Defect:** Even if multiple child generators were charter-authorized, the
“master seed plus SHA-256” key is not an executable collision-safe
specification: name encoding, digest-to-integer mapping, byte order, namespace
separation, and collisions with fixed internal keys are undefined.

**Concrete failure scenario:** A user column has the same name as a fixed
internal structure key. Duplicate-column rejection passes, both keys derive the
same child state, and the column draw becomes spuriously associated with the
structure draw while all determinism goldens for other columns remain green.
Separately, one implementation converts the digest to one big integer while
another splits it into words; both satisfy the prose but generate different
streams. NumPy accepts an integer or sequence of non-negative integers as
`SeedSequence` entropy, not an abstract digest
([NumPy `SeedSequence`](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.html)).

**Required change:** If child streams survive the D12 ruling, specify exact
UTF-8/name normalization, a fixed-endian digest-to-word conversion, length-
delimited domain tags separating user columns from every internal-key class,
and an explicit collision response; publish neutral vectors for the derivation.

### R3-F6 — major — D2/acceptance 1 (`phase-0-public-skeleton.md:33–46, 359–361`)

**Defect:** Acceptance requires only that a dated institutional determination
exists and that its outcome is recorded, not that the outcome affirmatively
authorizes public MIT release of the new work.

**Concrete failure scenario:** The authority issues a dated determination that
addresses both requested subjects but denies public MIT release. Acceptance 1
verifies the document exists, records its negative outcome, and—read literally—
allows repository creation to continue; the prototype-reuse fallback cannot
cure lack of authority to release the new project.

**Required change:** State that acceptance verifies the authority, date, scope,
and a **positive authorization for public MIT release**. Prototype reuse may be
negative only if D2's fallback activates; a negative new-work release outcome
halts the project.

## Decontamination verification

Revision 3 and the round-2 response are **not clean under revision 3's own
promised corpus**. I parsed the displayed-label field and relationship-group
field without printing their values, applied the specified identifier-boundary
tokenization before NFKC/casefold, and searched full normalized entries as
candidate n-grams. Results:

- 475 raw promised surfaces;
- 374 normalized-unique entries, 148 one-token;
- revision 3: 17 distinct matches across 121 lines;
- round-2 response: 15 distinct matches across 37 lines;
- actual strict-corpus `n_max`: 28.

Both files do have zero matches against the complete 288-name source-column
roster and the explicit roots/abbreviations in the reviewer brief. The older
155-entry draft plaintext inventory is not present as a standalone artifact in
the current private planning notes, so I do not claim a fresh independent scan
against that unavailable draft. That qualification does not change the
verdict: the newly promised and reproducibly extractable surfaces already prove
both files fail.

File digests at review time:

- revised plan: `cefb383e4749eeb630d5b759a4a675e2f18552bc2159984df34bf7765a92c18b`
- response: `9721a047d47d14820c0a2bff18701adadfe97e7db0930c895cc1c0d19f7f92d6`

No matched source value is reproduced in this review.

## What I checked

- Read `AGENTS.md`, `CLAUDE.md`, the round-2 review, round-2 response, and
  revision 3 in the requested order; then read the round-1 review/response to
  trace every carryover.
- Read all four required prototype documents and rechecked the five
  determinism obligations, generator/profile boundary, source-artifact warning,
  and the documented failure modes relevant to this Phase 0 security baseline.
- Inspected every revision-3 decision and acceptance criterion, with focused
  blast-radius checks across D2, D5–D7, D9–D10, and D12–D14.
- Resolved `../../../planning-notes/` from the plan directory and confirmed it
  lands in the private sibling outside `synthtwin`; inspected the current
  private-notes file inventory without reproducing its source-study content.
- Re-extracted the promised label/group surfaces: 475 raw, 374 normalized
  unique, 148 single-token; scanned both requested files and independently
  computed `n_max = 28`.
- Scanned both requested files against all 288 source-column names and the
  reviewer-brief roots/abbreviations; both were zero-match on those narrower
  sets.
- Executed a neutral decoder ambiguity proof: UTF-8 failed, UTF-16 succeeded on
  the wrong interpretation, and Latin-1 contained the canary the sequential
  algorithm would never inspect.
- Checked the current official documentation for Python path resolution and
  process-launch APIs, PyPA build isolation, NumPy random compatibility and
  `SeedSequence`, and GitHub ruleset behavior.
- No project tests were run: this remains a plan-only tree with no
  implementation. The path, inventory, hash, codec, and contract diagnostics
  above were run independently.

## Verdict

**Request changes.** D14's narrowed one-person claim is accepted, but D12 and
D7 are not. Before Phase 0 implementation, close the remaining R2 blockers and
the five new blockers: make path/capability checks match the offline promise;
make the inventory both discriminative and self-clean; use a deterministic,
fail-closed decoder; authenticate and fully bind the attestation; freeze the
executing build closure; and either honor the one-RNG charter or amend it before
approving a precisely keyed alternative. Acceptance must also require a
positive institutional MIT-release outcome, and D13 must sequence a real
pre-first-push check rather than relying on after-public CI.

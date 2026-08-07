# Phase 0 plan review — round 2

**Reviewed:** `docs/plans/phase-0-public-skeleton.md` (revision 2), the
round-1 response, and the read-only prototype  
**Verdict:** **request changes**  
**Round-2 finding count:** 13 — 10 blockers, 2 majors, 1 minor

Revision 2 makes meaningful progress: the Phase 0 runtime is dependency-free,
the placeholder release is gone, the artifact entry point and version source
are decided, and the plan now addresses repository governance and real-derived
fixtures. It is not approvable yet. The new decontamination matcher cannot
recognize a substantial part of its own promised inventory, D12 deliberately
changes the prototype RNG while claiming to preserve its determinism contract,
and the repository controls still let one compromised maintainer replace the
checks and approve the release.

## Resolution of the 15 round-1 review items

| Round-1 finding | Status | Evidence from revision 2 |
|---|---|---|
| **F1 — Phase 0 dependencies/pinning** | **Resolved** | D5 lines 117–128 removes all Phase 0 runtime dependencies, separates the frozen CI resolution from tested lower bounds, and no longer claims that a lock controls ordinary `pip`. |
| **F2 — complete supply-chain accounting** | **Partially resolved** | D5 lines 129–143 adds runtime, transitive, build, development, CI, and release roles plus the user-machine flag and first-release SBOM, but the installer/build-isolation node requested in round 1 is still absent; `twine`, the Python/pip toolchain, and the hosted-runner image closure are not assigned explicitly. |
| **F3 — offline boundary** | **Partially resolved** | D6 lines 149–193 explicitly narrows the guarantee and adds locality, import-time socket, static, and built-wheel layers, but lines 165–168 do not distinguish local storage from UNC/network-mounted paths and lines 180–188 do not enforce all capabilities prohibited at lines 149–152. |
| **F4 — plaintext denylist/exemptions** | **Partially resolved** | D7 lines 200–203 correctly chooses hashes and zero content exemptions, and the revised plan/response are clean in the audit below; however, the supposedly external path at lines 18–21 resolves inside the future repository. |
| **F5 — inventory and matching coverage** | **Partially resolved** | D7 lines 204–235 now states normalization, source categories, and two test tiers, but its operation order erases case boundaries, its five-token cap cannot represent many promised entries, and the private run proves only coverage of whatever list it is given—not completeness of that list. |
| **F6 — real/real-derived artifacts** | **Partially resolved** | D13 lines 317–333 adds the policy, ignore rules, allowlist, and an inserted CSV failure, but it does not regenerate and compare allowlisted fixtures, cannot detect real values embedded in ordinary source files, and runs only after a push has already exposed an object in public history. |
| **F7 — premature release integrity** | **Resolved** | D10 lines 261–276 withdraws every Phase 0 publication and fixes minimum integrity requirements for the first functional release. |
| **F8 — enforceable repository governance** | **Partially resolved** | D14 lines 337–350 adds a ruleset, API verification, read-only workflow permissions, tag/environment controls, and 2FA, but self-merge plus mutable workflows and self-approvable release controls leave the round-1 workflow-replacement scenario open. |
| **F9 — determinism contract** | **Unresolved** | D12 lines 290–313 repeats five headings but lines 293–297 replace the prototype's single legacy RNG with a different algorithm and multiple child generators; the claimed cross-platform/version byte identity also exceeds NumPy's compatibility contract. |
| **F10 — public self-containment** | **Partially resolved** | D3 lines 69–78 honestly labels prototype diffing private and promises public specifications/vectors, but neither the D4 layout nor acceptance criteria require those artifacts, while D2 lines 53–56 already depend on them as the fallback implementation source. |
| **F11 — license provenance** | **Partially resolved** | D2 lines 45–58 names a proposed holder, records inbound licensing, and adds a fallback, but a maintainer's own policy reading is not the verified institutional authorization requested in round 1, and reimplementation by the same source-exposed author is not a credible clean-room separation. |
| **F12 — artifact/entry-point/version testing** | **Resolved** | D4 lines 103–108 fixes the console entry point and single version source; D9 lines 250–255 and acceptance criterion 3 build, inspect, install, and smoke-test the wheel while checking both artifact manifests. |
| **F13 — placeholder name reservation** | **Resolved** | D1 lines 32–36 treats availability as unverified and makes no reservation claim; D10 removes the placeholder upload. |
| **F14 — stale product name in briefs** | **Resolved** | D3 lines 69–78 requires the canonical in-repo briefs to be renamed/sanitized and retires the parent copies; acceptance criterion 9 checks that result. |
| **F15 — Python support policy** | **Resolved** | D4 lines 109–112 adds a security-support/EOL policy, and D9 lines 250–253 tests 3.10 through 3.14, including macOS and Windows. |

Result: **6 resolved, 8 partially resolved, 1 unresolved.** A partial resolution
does not clear the original finding where a blocker scenario remains.

## Rulings on the scoped positions and questions

### Response position F3 / plan question D6 — **convinced on scope; controls still blocked**

I am convinced that the charter does not require synthtwin itself to be a
privileged OS syscall sandbox. A source-auditable application that makes no
egress-capable calls, works unchanged in an air gap, accurately discloses the
limit, and recommends an institution-controlled network boundary is an
acceptable interpretation. I am not convinced that the listed checks establish
even that narrower promise: R2-F2 and R2-F3 below identify filesystem and
capability routes that remain inside the stated boundary but outside its tests.

### Response position F11 / plan question D2 — **hold the line**

Phase 0 must be blocked from any public commit until a dated written
determination or authorization from the appropriate institutional IP authority
exists; a README statement that the maintainer read the policy is not
independent evidence. The University's official policy makes ownership of
software fact-dependent—among other things, agreements, assigned duties,
funding, and significant institutional resources can change the result—and
provides a disclosure/determination process where the institution may have an
interest ([University of Iowa Intellectual Property Policy](https://policy.uiowa.edu/administrative-financial-and-facilities-policies/university-iowa-intellectual-property-policy)).
The plan may record only a non-sensitive date/outcome publicly, but acceptance
must let the reviewer verify that documentary authority exists. If it does not,
the fallback needs an actually independent implementer working only from an
authorized public specification; the same author who wrote and reviewed the
private source cannot create clean-room separation by changing files.

### Plan question D7 — **hold the line**

A private plaintext source paired with a public hashed manifest can be
acceptable in principle. This two-tier proposal is not: the matcher is
internally inconsistent, the source corpus is incomplete, and a count in a
commit message is neither an enforced check nor evidence bound to the manifest.
The private run must emit a machine-verifiable attestation tied to the prototype
snapshot digest, plaintext-inventory digest, public-manifest digest, scanner
revision, entry count, and result; the initial inventory also needs an
independent review. Public CI should require that attestation whenever any bound
input changes.

## New defects introduced or exposed by revision 2

### R2-F1 — blocker — D5/D10 (`phase-0-public-skeleton.md:120–143, 266–274`)

**Defect:** The plan permits the first functional PyPI release in Phase 3 but
does not require that release to provide a hash-pinned user install; the only
timed exact-install mechanism is the Phase 6 standalone build, while D10's
SBOM/hashes describe the build closure rather than controlling a later `pip`
resolution.

**Concrete failure scenario:** A Phase 3 wheel declares lower bounds; six
months later an institution installs the same synthtwin version and `pip`
selects a newer compromised runtime artifact. The synthtwin wheel's attestation
and original SBOM remain valid, but the executing closure is not the reviewed
closure.

**Required change:** Make a generated, fully hash-pinned install file and its
offline installation test requirements of the **first** dependency-bearing
release, not merely the Phase 6 standalone build, and state how users consume
it.

### R2-F2 — blocker — D6.1 (`phase-0-public-skeleton.md:149–172`)

**Defect:** “Exists” plus absence of `scheme://` does not establish that a path
is local, and the rule does not define locality for outputs, symlinks, Windows
UNC/device paths, mapped drives, or network-mounted filesystems.

**Concrete failure scenario:** On Windows a UNC source path has no URL scheme;
the existence check itself initiates SMB traffic and the reader accepts it,
while every planned test and static scan remains green. An output directory on
the same kind of path can transmit generated artifacts without importing a
network module.

**Required change:** Define the supported path types and canonicalization for
every input/output/temp path, reject UNC/device forms where the OS exposes them,
state that undetectable remote mounts are outside the audit guarantee, and test
the platform-specific cases before delegating to a capable library.

### R2-F3 — blocker — D6.2–D6.4 / acceptance 6–7 (`phase-0-public-skeleton.md:173–192, 371–374`)

**Defect:** The two patched socket attributes and named import denylist cannot
enforce the stated bans on network, subprocess, native, and dynamic-code
capabilities, while D6.4 inaccurately calls the `sitecustomize` monkeypatch
“network disabled.”

**Concrete failure scenario:** Runtime code imports the low-level socket module
directly, calls an unlisted process-launching API, or dynamically imports a
forbidden module. The listed scanner patterns do not fire, the branch need not
execute in the stub smoke test, and the high-level socket replacements are
irrelevant; all acceptance checks can pass while the installed command has an
egress path.

**Required change:** Prefer a positive runtime import/capability policy, cover
all dynamic-loading and process/native entry points promised by the boundary,
add one mutation for every bypass class, and describe the test wrapper as a
Python-level guard rather than network disablement.

### R2-F4 — blocker — decontamination-note path (`phase-0-public-skeleton.md:18–21`)

**Defect:** From `synthtwin/docs/plans/`, the documented
`../../planning-notes/` path resolves to `synthtwin/planning-notes/`—inside the
future public repository—not to the existing private sibling directory.

**Concrete failure scenario:** An implementer follows the plan literally and
places the plaintext inventory under the repository root; it is then either
committed publicly or makes the zero-exemption scanner fail, despite the plan
claiming that the source is outside the repository.

**Required change:** Correct the path (the present workspace's sibling is
reached one level farther up), explicitly ignore the private location as
defense in depth, and acceptance-test that the resolved path is outside the
repository root.

### R2-F5 — blocker — D7 normalization/matching (`phase-0-public-skeleton.md:200–214`)

**Defect:** D7 case-folds before splitting case transitions, which destroys the
information needed to equate identifier styles, and it hashes candidate
n-grams only through five tokens even though many promised full-name hashes are
longer.

**Concrete failure scenario:** A denied two-token name stored in separated form
is written in lower-Camel form: the manifest normalizes it to two tokens, the
candidate becomes one, and their hashes differ. Independently, using a
conservative tokenizer that preserves digit runs, **179 of the 288** source
column names exceed five tokens (maximum 14), as do 14 entries in the existing
155-entry draft inventory; their full hashes can never be emitted by the
specified candidate generator. A UTF-16 text file is also treated as
NUL-interleaved UTF-8 or Latin-1 bytes rather than decoded into the intended
tokens.

**Required change:** Split identifier boundaries before case-folding, remove or
derive the n-gram cap from the manifest's actual maximum, define handling for
UTF-16/binary/archive inputs, and parameterize neutral cross-form tests for
every promised normalization equivalence.

### R2-F6 — blocker — D7 inventory provenance/two-tier proof (`phase-0-public-skeleton.md:215–235, 366–370`)

**Defect:** The stated corpus and private proof cannot establish inventory
completeness: the corpus omits prototype example executables and real-derived
label surfaces, “study-specific” has no deterministic selection rule, and the
recorded count is not cryptographically bound to any input or enforced by CI.

**Concrete failure scenario:** A source-specific label that occurs only in an
example/profile artifact is pasted into a Python test. The prototype contains a
fourth Python example and a shell executable beyond the “three scripts” in
D7; the profile has 262 case-folded-unique displayed category labels (245
absent from the draft inventory), and the relationship artifact has 117 unique
group values (111 absent). D13 does not flag a `.py` file, the missing hash is
not noticed by neutral canaries, and the private report can retain the same
count by replacing or padding another hash.

**Required change:** Enumerate the exact source snapshot and files/fields,
define reproducible extraction and review rules for every surface class, cover
the profile/relationship value leak class or prove an equivalent guard, and
replace the commit-message assertion with the bound attestation described in
the D7 ruling.

### R2-F7 — blocker — D12 RNG contract (`phase-0-public-skeleton.md:290–304`)

**Defect:** D12 says it restates the prototype contract but replaces its one
`RandomState` stream with `Generator(PCG64)` and multiple child streams,
contradicting both the prototype's first rule and the charter's “one RNG,
passed everywhere” requirement without a fidelity decision or compatibility
demonstration.

**Concrete failure scenario:** A neutral reference profile and seed produce a
different draw sequence immediately after the port, but newly generated golden
files merely bless the drift. Moreover, ordinary `SeedSequence.spawn(n)`
children are identified by their position in the spawn tree, so assigning them
to columns by enumeration makes an inserted/reordered column shift which child
every later column receives; no stable column-to-child mapping or duplicate-name
rule is specified. NumPy documents that spawned children incorporate their
tree position ([NumPy `SeedSequence.spawn`](https://numpy.org/doc/stable/reference/random/bit_generators/generated/numpy.random.SeedSequence.spawn.html)).

**Required change:** Preserve the prototype-compatible RNG for ported numeric
machinery, or obtain an explicit charter/phase decision to rebaseline it with
independent numeric vectors. Do not claim reorder independence unless a stable,
collision-defined keying algorithm is fixed and tested.

### R2-F8 — blocker — D12 byte-identity scope (`phase-0-public-skeleton.md:306–313`)

**Defect:** Canonical serialization cannot make different upstream numeric
results identical, yet the plan promises byte identity across supported
OS/Python versions and a NumPy range that NumPy itself does not guarantee.

**Concrete failure scenario:** The same synthtwin version, profile, and seed
runs against two allowed NumPy builds or linear-algebra backends and produces a
different numeric array; `repr` faithfully serializes the different values and
the golden hash diverges. NumPy limits `Generator` stream compatibility to
strict same-build/environment conditions and permits version changes to its
distribution algorithms ([NumPy random compatibility policy](https://numpy.org/doc/stable/reference/random/compatibility.html)).

**Required change:** Either narrow byte identity to an exact dependency/build
closure or implement platform-stable numeric primitives/quantization that can
support the broader promise. Golden hashes must run on every claimed platform
and dependency boundary; date/time formatting, still omitted from the round-1
request, must also be canonicalized.

### R2-F9 — blocker — D13 provenance guard (`phase-0-public-skeleton.md:317–333, 375`)

**Defect:** An extension allowlist plus a prose header is neither content
provenance nor pre-public leak prevention, and the only mutation proves merely
that an unallowlisted CSV filename is rejected.

**Concrete failure scenario:** An allowlisted tiny generated fixture is
replaced with real-derived rows while retaining its claimed script/seed header;
the provenance and artifact allowlists pass because neither rebuilds the
file. Conversely, a nonallowlisted real file pushed to the public repository
does make CI red, but its blob is already downloadable and remains in history
after a deletion commit, contradicting “ever enters the repository.”

**Required change:** Maintain a complete fixture manifest bound to generator,
seed, and digest; regenerate every committed fixture and byte-compare it in CI;
include an allowlisted-content substitution mutation; add a staged/pre-public
check, full object/history scan at initial acceptance, workspace separation,
and an explicit purge/incident procedure.

### R2-F10 — blocker — D14 tamper resistance (`phase-0-public-skeleton.md:337–350`)

**Defect:** PR-only self-merge does not protect mutable workflows or security
tools, and a manual release approval by the same sole maintainer supplies no
independent authorization.

**Concrete failure scenario:** A compromised maintainer account opens a PR that
turns all seven workflows into no-ops, lets those altered workflows report
success, self-merges, creates the permitted release tag, and approves its own
environment deployment. Every D14 setting is obeyed. GitHub supports binding a
required check to its expected app and environments can prevent self-review,
but neither is selected here ([GitHub status-check guidance](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks),
[GitHub deployment protection](https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments)).

**Required change:** Protect workflow/security-tool paths with an independent
reviewer or immutable external required workflow, bind required contexts to
their expected app, disallow release self-review/admin bypass, protect tag
creation/update/deletion, require signed release tags, and specify account
recovery controls. If a one-person project cannot provide separation of duty,
narrow the tamper-resistance claim explicitly.

### R2-F11 — major — D9/D14 required-check identity (`phase-0-public-skeleton.md:250–258, 340–343`)

**Defect:** “Seven named jobs” is not an implementable required-check list
because `tests` expands into seven matrix job runs and no exact per-variant
contexts or aggregate gate is defined.

**Concrete failure scenario:** A platform/version matrix member fails, is
cancelled, or is skipped while the one context selected in the ruleset reports
success—or the ruleset waits forever for a non-existent bare `tests` context.
GitHub defines a matrix as multiple job runs and recommends an `always()`
dependent job when a single required gate must observe upstream failures
([GitHub matrix workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax),
[GitHub required-check troubleshooting](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)).

**Required change:** Name every exact required context, or create one uniquely
named `always()` aggregate gate that fails unless every lint/type/test/build/
security dependency succeeded, and pin that immutable gate in D14.

### R2-F12 — major — D2/D3 public fallback (`phase-0-public-skeleton.md:53–56, 69–78, 81–99, 354–380`)

**Defect:** The plan relies on public contract documents and neutral numeric
vectors for external verification and its licensing fallback but does not make
either one a Phase 0 deliverable or acceptance item.

**Concrete failure scenario:** Prototype reuse is not authorized, so a future
contributor follows D2's fallback; only plans and self-generated goldens exist,
so the contributor implements a subtly different tail/RNG behavior and
rebuilds the expected files from that same code. CI is green, but there is
no independent public oracle against which to detect the numeric change.

**Required change:** Add a sanitized public method contract and fixed neutral
input/output reference vectors—prepared and independently checked before port
implementation—to the layout and acceptance criteria, or defer the fallback
claim until the phase that creates and approves them.

### R2-F13 — minor — D7 prototype count (`phase-0-public-skeleton.md:217–223`)

**Defect:** The repeated “31 hard-coded names” description is not an accurate
count of source-column string literals in the generator.

**Concrete failure scenario:** An AST intersection against the 288-name profile
finds 39 source names in generator string constants; the prototype document's
31-entry roster contains only 30 source names plus one derived name and omits
nine source names. The proposed all-288 union would mask this mistake if
implemented, but a maintainer using the narrower documented roster for a port
or regression list would silently omit those nine.

**Required change:** Correct the planning statement and record the executable
counting rule. This also corrects my round-1 statement that the documented count
was accurate.

## Decontamination verification

The two files specifically requested for round 2 are **clean against every
currently auditable source**:

- the private round-1 inventory: 155 entries, 151 NFKC/case-folded unique;
- all 288 exact and case-folded-unique source-column names from the prototype
  profile;
- the explicit denied roots/abbreviations in the reviewer brief.

The scan found zero normalized full-term matches in either file. File digests
at review time:

- revised plan: `579287b910f4f317771c735e3490978ef7169c5db79659078026258fe973ffd0`
- response: `2f5eb5e70fd23fd48a1e235b4e3e0e0f8d3107750810c73ec9fb2d8519a02445`

This verification is necessarily qualified: the promised regenerated 288+
plaintext inventory, hashed manifest, and scanner do not exist yet, so a claim
against that future corpus is **unverified**, not assumed. This review itself
does not reproduce denied vocabulary.

## What I checked

- Read `AGENTS.md`, `CLAUDE.md`, the round-1 review, the complete response, and
  revision 2 in the required order.
- Read all four required prototype documents and checked the relevant
  generator/profile boundary, schema roster, real-artifact warning, supply
  imports, and determinism rules against the plan.
- Resolved the plan's private-notes path from the document directory and
  verified that it points inside `synthtwin`; verified the actual private notes
  are one level farther out.
- Parsed the prototype profile independently: 288 rows and 288 exact/case-fold
  unique column names; under a conservative correct identifier split, 179 have
  more than five tokens and the maximum is 14.
- Parsed the draft private inventory: 155 entries, with 14 exceeding the
  proposed five-token cap under the same conservative split.
- Parsed profile category surfaces and relationship groups without reproducing
  them; checked their intersection with the draft inventory.
- Used Python AST, rather than the prototype prose list, to count generator
  string literals intersecting the full source-column roster.
- Checked the revised plan and response against the auditable inventory,
  complete column roster, and reviewer-brief deny roots; recorded both file
  hashes above.
- Checked current primary documentation for the University's IP ownership and
  determination process, NumPy RNG/spawn compatibility, and GitHub required-
  check/environment behavior.
- Inspected every revised decision and acceptance criterion, with fresh focus
  on D5, D6, D7, D10, D12, D13, and D14.
- No project tests were run: this is still a plan-only repository and the plan
  states that no implementation exists. The diagnostic counts/path/hash checks
  above were run independently.

## Verdict

**Request changes.** Resolve every blocker in the written plan before Phase 0
implementation. The D6 no-syscall-sandbox scope is acceptable, but its controls
must prove the narrower boundary; D2 needs documentary institutional authority;
and D7 needs a technically coherent matcher plus a machine-verifiable,
complete-inventory attestation.

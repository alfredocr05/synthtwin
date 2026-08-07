# Phase 0 plan review — round 1

**Reviewed:** `docs/plans/phase-0-public-skeleton.md` (draft dated 2026-08-06)  
**Verdict:** **request changes**  
**Finding count:** 15 total — 9 blockers, 4 majors, 2 minors

The skeleton's scope is appropriate, and several prototype descriptions are
accurate, but the plan does not yet establish the security and decontamination
baseline it claims. In particular, checks can remain green while released code
uses the network, the proposed public install is not pinned, the repository
would intentionally retain prohibited source-study material, and Phase 0 would
publish before its release-integrity controls exist.

## Review items

### F1 — blocker — D5/D10 (lines 82–100, 176–184) and acceptance criterion 3

**Defect:** The Phase 0 package gives a nonfunctional status command two unused
runtime dependencies and exposes ordinary `pip` users to lower-bounded rather
than pinned dependency resolution, contrary to the minimal-and-pinned supply-
chain requirement.

**Concrete failure scenario:** An institution installs the same `0.0.1` release
six months after CI ran; `pip` ignores `uv.lock`, resolves different dependency
artifacts, and installs a compromised or incompatible release even though the
stub needs neither dependency.

**Required plan change:** Give the Phase 0 skeleton zero runtime dependencies.
When a dependency is first used, decide its tested minimum separately from the
exact, hashed application/install resolution; require CI to consume the lock in
frozen mode and test both the supported minimums and the shipped resolution.
`uv.lock` can reproduce a uv-managed project environment, but it does not govern
a normal PyPI consumer's `pip install` ([uv project documentation](https://docs.astral.sh/uv/concepts/projects/layout/)).

### F2 — blocker — D4/D5/D11 (lines 55–100, 186–194)

**Defect:** The statement that an IT reviewer audits “two packages and nothing
else” counts only direct runtime requirements and omits transitive runtime,
build-backend, installer, CI-action, and release-tooling nodes that can execute
code.

**Concrete failure scenario:** An auditor approves the two named direct
requirements, but an sdist build executes the unreviewed build backend and the
data-frame dependency installs additional packages; a compromised omitted node
can alter the installed program while every stated audit step passes.

**Required plan change:** Inventory the complete supply chain by role (runtime,
transitive, build, development, CI, and release), state which artifacts execute
on a research machine, commit hashes/SBOM material for the shipped closure, and
make `README.md` and `SECURITY.md` say “two direct dependencies” only when that
is what is meant. The prototype verifies only the narrow claim that its three
scripts directly import NumPy and pandas plus the standard library.

### F3 — blocker — D6 (lines 102–122) and acceptance criteria 5–6

**Defect:** A pytest-time socket monkeypatch plus a source import denylist is
defense in depth, not a fail-closed network boundary for the installed product,
and the plan overstates it as proof of the offline guarantee.

**Concrete failure scenario:** Phase 1 passes a user-supplied URL to the
allowlisted data-frame reader; tests use local paths and the static scan sees
only an allowed import, but the released CLI performs an HTTP request. The
library explicitly accepts URL inputs ([pandas `read_csv`](https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html)).
Likewise, module-import activity during pytest collection occurs before an
autouse fixture, and child-process/native routes bypass a Python socket stub.

**Required plan change:** Define the production egress boundary and its threat
model before implementation. Add an end-to-end test that observes or blocks
network syscalls from process start (including import/collection and child
processes), test allowed-library URL paths and bypass classes, validate all user
paths as local before handing them to capable libraries, and describe the
static scan as a supplemental control. If an enforceable runtime boundary is
not intended, the charter-level guarantee must be narrowed explicitly rather
than silently.

### F4 — blocker — D7 (lines 124–153) and acceptance criteria 4 and 8

**Defect:** The plaintext rule file and path exemptions deliberately retain the
very source-study vocabulary that the charter says must occur nowhere, while
this tracked plan itself contains denied literals but is not exempted.

**Concrete failure scenario:** The first faithful CI implementation fails on
this plan; adding another exception makes CI green while repository search and
the source distribution still expose prohibited material, so the check certifies
the opposite of the stated invariant.

**Required plan change:** Store only normalized hashes in the public tree,
sanitize this plan and the canonical briefs, and remove content exemptions.
Keep any plaintext source used to audit the hashes outside the repository. Do
not solve the self-failure by exempting plans or reviews.

### F5 — blocker — D7 (lines 126–153)

**Defect:** The denied-vocabulary inventory and “word-ish boundary” algorithm do
not define or demonstrate complete coverage of the prototype's vocabulary and
full source-column roster.

**Concrete failure scenario:** A non-hard-coded source column or a denied root
embedded in a CamelCase, underscore, hyphenated, plural, filename, or differently
encoded form is copied into a test; the one simple canary passes while the new
form evades the scanner and ships.

**Evidence:** The planning inventory does contain 155 entries, so that raw count
is verified, but only 151 are unique after case-folding. Only 42 of the
prototype profile's 288 column names occur as exact case-folded entries; the
plan gives no executable rule proving coverage of the remainder. The
prototype's documented count of 31 names hard-coded into the generator is
accurate, but “hard-coded” is narrower than the charter's “literal column
names.”

**Required plan change:** Approve the exact hashed inventory and provenance in
the plan; specify Unicode normalization, case-folding, identifier/separator and
plural/stem behavior, content and path scanning, binary/non-UTF-8 handling, and
fail-closed read errors. Parameterize tests across every inventory entry and
matching mode, and require every newly discovered term to add a regression.

### F6 — blocker — D3/D7/D12 (lines 36–53, 124–153, 196–203)

**Defect:** No policy or automated guard forbids real or real-derived profile
artifacts and values from entering the public repository; “no large/generated
fixtures” and a study-vocabulary scanner do not cover that leak class.

**Concrete failure scenario:** A later phase copies the prototype's small schema
CSV into `tests/fixtures`; it contains real-derived ranges and top text/category
values, remains small enough to satisfy D3, and contains arbitrary values the
vocabulary scanner cannot recognize, so it is committed publicly.

**Required plan change:** Add a day-one prohibition on real and real-derived
data, an explicit generated-neutral-fixture provenance rule, safe `.gitignore`
defaults, and an artifact/fixture allowlist or equivalent guard. The need is not
hypothetical: the prototype calls its schema examples real artifacts
(`synthetic_data_toolkit/README.md`, lines 83–100) and warns that profiles can
publish identifier/text values (`docs/ADAPTING_TO_A_NEW_PROJECT.md`, lines
77–81).

### F7 — blocker — D8/D10 (lines 155–164, 176–184)

**Defect:** Phase 0 publishes a release while deferring signing/attestation and
reproducible-build decisions to Phase 6, contradicting the charter's first-build
tamper-resistance requirements.

**Concrete failure scenario:** A local long-lived upload credential or dirty
working tree publishes a wheel different from the reviewed commit; users can
verify PyPI's file checksum but cannot tie the artifact to the protected source
or reproduce it.

**Required plan change:** Either remove the Phase 0 release or bring its whole
release design into Phase 0: clean tagged builds, frozen tools, two independent
builds with an explicit reproducibility comparison, artifact hashes and
contents, protected approval, Trusted Publishing, and attached provenance.
PyPI's official publishing action can produce attestations automatically
([PyPI attestation documentation](https://docs.pypi.org/attestations/producing-attestations/)).

### F8 — blocker — D3/D9 (lines 36–53, 166–174) and acceptance criterion 1

**Defect:** Calling CI jobs “required” does not make repository or release
changes tamper-resistant because the plan never chooses enforceable repository
rules, workflow permissions, or release authorization.

**Concrete failure scenario:** A maintainer credential pushes an exfiltrating
change directly to the default branch, edits the workflow that would have
checked it, or publishes from an unprotected environment; all five checks still
exist and can be green on the previous commit.

**Required plan change:** Specify and accept-test the GitHub ruleset/branch
protection (pull requests and named required checks, force-push/deletion and
bypass policy), least-privilege default workflow permissions, protected tags
and release environment, trusted-publisher identity, account recovery/2FA
expectations, and untrusted-PR treatment. Verify settings, not merely a green
run.

### F9 — blocker — D12 (lines 196–203)

**Defect:** D12 truncates the prototype's five determinism rules and leaves the
scope and canonical serialization of “same seed, same bytes” undecided.

**Concrete failure scenario:** An implementer uses a different NumPy generator
that still satisfies “one seeded RNG,” changing the port's numeric stream; or
the same profile and seed serialize on Ubuntu and Windows with different CSV
newlines while every listed D12 rule is obeyed. Pandas defaults CSV line endings
to the host OS ([pandas `to_csv`](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html)).

**Required plan change:** Restate all five prototype §9 obligations, including
the compatible RNG API, identifiers without replacement, schema-defined output
order, and deterministic special-category choice. Define whether byte identity
is cross-process, cross-Python, cross-dependency, and cross-OS; then mandate
canonical encoding, newline, float/date/null and JSON ordering and the later
golden-hash tests needed for that chosen scope.

### F10 — major — D3/D4/D12 (lines 49–70, 196–203)

**Defect:** The public governance files depend on sibling prototype and paper
directories that exist only in this maintainer's OneDrive layout, contradicting
the statement that GitHub is the source of truth for the public process.

**Concrete failure scenario:** An external contributor clones `synthtwin` and
is required by `AGENTS.md` to diff a port against `../synthetic_data_toolkit`,
but that directory and the cited papers do not exist, so the mandated review is
impossible outside the maintainer's machine.

**Required plan change:** Provide public citations/URLs and a self-contained,
decontaminated technical contract with numeric reference vectors, or clearly
label the private comparison as maintainer-only and replace it with an
equivalent public verification path. Do not copy the prototype's real-derived
examples into this repository to fix the path.

### F11 — major — D2/D5 (lines 27–34, 84–92)

**Defect:** The MIT decision does not identify the copyright holder or establish
authority to relicense prototype code that the reference documentation directs
future phases to retain verbatim.

**Concrete failure scenario:** Phase 2 ports the documented transferable block
under a personal MIT notice, but an institution or another contributor owns the
prototype copyright and challenges the public release.

**Required plan change:** Record the exact copyright notice and verified
provenance/authorization for both new work and any ported lines, plus the
contribution-licensing mechanism. I found no license file in the supplied
prototype snapshot, so permission to relicense it is **unverified**; use a
clean-room reimplementation if authority cannot be documented.

### F12 — major — D4/D9/D10 (lines 55–80, 166–184) and acceptance criteria 1–7

**Defect:** The acceptance suite never builds, inventories, scans, installs, or
executes the wheel/sdist and does not decide the console entry point or single
version source required by D10.

**Concrete failure scenario:** Editable installation and source tests pass, but
the published wheel omits the `synthtwin` command, reports a version different
from package metadata, or the sdist includes an unintended local file; every
listed acceptance criterion still passes.

**Required plan change:** If a release remains, define its entry-point module
and authoritative version, build wheel and sdist from a clean checkout, inspect
an explicit file allowlist and metadata, scan extracted artifacts, install the
wheel in fresh network-dead environments, and test the exact command/output on
all supported operating systems. Editable install is not a release test.

### F13 — major — D1/D10 (lines 17–25, 176–184)

**Defect:** The plan treats a final, deliberately nonfunctional PyPI upload as a
safe name-reservation mechanism even though a JSON 404 does not prove the name
is claimable and PyPI treats no-functionality name squats as invalid.

**Concrete failure scenario:** The repository publicly commits to the name, but
the upload is rejected because the unseen name is registered, prohibited, or
confusable; alternatively, the status-only project is removed or transferred
as an invalid squat, defeating the reservation.

**Required plan change:** Treat current availability as **unverified** until an
authorized upload succeeds, and delay PyPI until there is a genuine useful
capability. PyPI documents both hidden reasons a 404 name may be unavailable
([PyPI Help](https://pypi.org/help/#project-name)) and removal of projects with
no functionality ([PyPI Name Retention](https://docs.pypi.org/project-management/name-retention/)).
Whether maintainers would apply the latter rule to this exact stub is
unverified, but D10's stated purpose puts it squarely at risk.

### F14 — minor — D1/D3/D7 (lines 17–25, 49–53, 141–149)

**Defect:** D1 promises one product name everywhere while D3/D7 copy and exempt
governing briefs whose title and body still use the retired working name.

**Concrete failure scenario:** A contributor sees `synthtwin` in package and CLI
metadata but follows a canonical brief that names a different product, creating
wrong paths, issue text, or future metadata.

**Required plan change:** During the move, update the one canonical pair of
briefs to `synthtwin` and retain at most a short historical rename note. The
rename creates no substantive inconsistency with the charter's goal or six
principles; the inconsistency is the plan to publish stale names unchanged.

### F15 — minor — D4/D9 (lines 78–80, 166–174)

**Defect:** `requires-python >=3.10` declares Python 3.14 and later supported,
but CI stops at 3.13 and gives no policy for 3.10 reaching end of life in October
2026.

**Concrete failure scenario:** A Python 3.14 user legally installs the release
and encounters an untested compatibility failure; shortly afterward, a
researcher follows the advertised floor on an interpreter no longer receiving
security fixes.

**Required plan change:** Add 3.14 to CI now and decide a supported-version/EOL
policy (or cap metadata to what is tested). The official status table lists 3.14
as stable bugfix and 3.10 EOL as 2026-10
([Python Developer's Guide](https://devguide.python.org/versions/)).

## Answers to the questions put to review

1. **D7 plaintext versus hashes:** Plaintext is not acceptable under the
   charter as written. Use a hashed public manifest with a precisely specified
   normalization/matching contract, exhaustive test vectors, and a locally
   auditable generation procedure whose plaintext source remains outside the
   public tree. Hashing is not needed for secrecy; it is needed so the
   enforcement mechanism does not violate the literal no-trace invariant.

2. **D7 brief exemptions:** The exemptions do not honor principle §2.4.
   Sanitize and rename the canonical briefs (and this plan) instead. Because D3
   retires the parent copies, the sanitized files can become the sole governing
   versions rather than creating permanent divergence.

3. **D10 placeholder release:** I object to it as written. It adds no user
   capability, adds unnecessary supply-chain surface, precedes signing and
   reproducibility controls, is not artifact-tested, and carries explicit PyPI
   name-retention risk. The clean decision is to wait for the first functional,
   securely published release; if an earlier release remains, it must first
   satisfy every release-integrity and artifact criterion above and provide a
   genuine capability.

## Six-principle assessment

- **Open source:** The public-repo intent is correct, but inaccessible sibling
  references and unresolved licensing provenance prevent a self-contained
  public development/review process.
- **Zero-code:** Deferral of the real user flow is honest for a skeleton, and
  README status labeling is appropriate; a nonfunctional default PyPI install
  should not masquerade as that flow.
- **Secure by architecture:** Not satisfied because the installed dependency
  closure is not pinned/minimal, runtime egress is not bounded, repository
  controls are not enforceable, and the first release precedes integrity
  controls.
- **Decontaminated:** Not satisfied because the design intentionally embeds and
  exempts prohibited material, incompletely specifies coverage, and lacks a
  real-derived-artifact rule.
- **Comprehensive:** Correctly deferred to Phase 1; nothing in Phase 0 may narrow
  the required taxonomy. Neutral fixture provenance must be established now so
  later ugly-case tests do not reuse real profiles.
- **Statistical fidelity:** Correctly deferred to Phase 2. The narrow prototype
  machinery/dependency descriptions are accurate, but dependency policy must
  remain revisitable and the full determinism contract must be preserved.

## What I checked

- Read `AGENTS.md`, `CLAUDE.md`, the complete Phase 0 plan, and all four required
  prototype documents.
- Compared every plan decision and acceptance criterion with all six charter
  principles and the Phase 0 boundary.
- Verified the rename in the plan, charter, reviewer brief, proposed repo/package
  names, and copied-governance-file path behavior.
- Verified the prototype's imports and the cited percentile ladder, tail solve,
  iterative margin calibration, lognormal moment conversion, sampling-error
  tolerance, generator/profile boundary, and five determinism rules. The claim
  that these mechanisms have only NumPy/pandas as direct third-party imports is
  accurate; the claim that this is the whole auditable supply chain is not.
- Verified the prototype's 31 hard-coded-name count, 288-column roster, real-
  artifact warning, regenerate-don't-commit scope, and named-exemption pattern.
- Located and counted the planning inventory: 155 raw entries, 151 unique after
  case-folding, with 42 exact case-folded matches to the 288 source columns. I
  did not reproduce its prohibited plaintext in this review.
- Checked current primary documentation for uv lockfile scope, pandas URL I/O
  and OS-dependent CSV newlines, PyPI name retention/attestations/name
  availability, and supported Python versions.
- Inspected the planned release path, CI jobs, acceptance criteria, repository
  governance, package layout, and license provenance.
- No tests were run: this is a plan-only review and no implementation exists.

## Verdict

**Request changes.** All blocker review items must be resolved in the written plan
before Phase 0 implementation begins; the revised plan should also close the
major decisions rather than leaving them to implementation.

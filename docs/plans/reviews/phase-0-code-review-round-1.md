# Phase 0 code review — round 1

**Reviewed:** the 11-commit Phase 0 implementation at
`001474781de5350c63cc02743c3046c9984d8197`, the canonical in-repo briefs,
the conditioned Phase 0 plan, the public implementation and tests, the
maintainer-private binding records without reproducing protected vocabulary,
and the pre-first-push record  
**Verdict:** **request changes**  
**Finding count:** 25 — 17 blockers, 6 majors, 2 minors  
**Public-host items:** separately classified as pending-public-verification

The current `src/` is small and manually clean: I found no construct in the
three shipped modules that initiates network I/O, starts a process, calls
native code, or dynamically loads code. The tracked tree and the full current
Git object set also scan clean. Those facts do not ratify the implementation.
Several controls accept real bypasses, the build job necessarily rejects its own
artifacts, the signed decontamination chain is not reproducible from its bound
inputs, and required mutation and history controls are absent. A green run of
the present suite therefore overstates what has been enforced.

## Blockers

### F1 — Blocker — the positive source scanner trusts forbidden capabilities re-exported by allowed modules

**Location:** `tools/offline_scan/scan_imports.py:47-58`, `:163-164`,
`:181-182`, `:197-201`, and `:426-435`

**Defect:** `_policy_for` permits every attribute below several allowed module
roots and every `synthtwin.*` chain, rather than resolving each access to an
exact allowed API as D6.2 requires.

**Concrete failure scenario:** add either of these to product source:
`import os; os.path.os.system("noop")` or
`import synthtwin.paths; synthtwin.paths.os.system("noop")`. On the reviewed
interpreter both paths reach `os.system`, but `scan_source` reports zero
violations. A process can therefore be launched while `offline-static` stays
green. A registry lookup through an allowed module's exported interpreter
module also scans clean, defeating the reflective mutation class by changing
only the route to the registry.

**Deviation status:** undocumented and not defensible. It contradicts D6.2's
central positive-policy decision rather than selecting an equivalent
implementation.

### F2 — Blocker — the source scanner's name binding is control-flow-unsound and unresolved call targets are accepted

**Location:** `tools/offline_scan/scan_imports.py:261-291`, `:479-481`,
`:509-518`, and `:533-539`

**Defect:** one sequential binding map forgets an imported origin after any
store, even a store on a branch that cannot run, while calls through unknown
names or attributes are not rejected.

**Concrete failure scenario:** this module scans clean:

```python
import os as capability

if False:
    capability = 0

capability.system("noop")
```

At runtime the original module remains bound and starts a process. Likewise,
`def invoke(callback): callback("payload")` is accepted even though the call
target cannot be resolved statically. Both outcomes contradict the scanner's
claim that indirect or dynamically manufactured call targets are rejected.

**Deviation status:** undocumented; the existing alias tests exercise only
straight-line assignments and do not expose this data-flow failure.

### F3 — Blocker — the path gate accepts valid URL-scheme syntax containing punctuation

**Location:** `src/synthtwin/paths.py:57-74` and `tests/test_paths.py:20-28`

**Defect:** `_url_scheme` permits only letters and digits after the first
letter, although URL scheme syntax also permits `+`, `-`, and `.`.

**Concrete failure scenario:** `git+ssh://host/item`, `a-b://host/item`, and
`a.b://host/item` were each accepted and passed to `Path.resolve()`, which
turned them into misleading local-looking paths. A later reader that
recognizes one of those schemes receives remote-address syntax even though
D6.1 and `SECURITY.md` say every `scheme://` form is rejected before any
filesystem call.

**Deviation status:** undocumented and contrary to D6.1.

### F4 — Blocker — Windows metadata failures are treated as proof that a component does not exist

**Location:** `src/synthtwin/paths.py:149-168`

**Defect:** the Windows walk catches every `OSError`, not just a missing path,
and then proceeds to resolution without having examined that component.

**Concrete failure scenario:** when `os.lstat` raises `PermissionError` or a
sharing error for an existing junction, the code continues and invokes
`Path.resolve()`. A targeted probe produced exactly that outcome. Resolution
can then follow or touch the unexamined target, contradicting D6.1's guarantee
that resolution occurs only after every existing component is shown not to be
a reparse point.

**Deviation status:** undocumented and fail-open.

### F5 — Blocker — the mandatory Windows link mutation can turn into a skip

**Location:** `tests/test_paths.py:195-245`

**Defect:** `_make_windows_dir_link` calls `pytest.skip` when the runner cannot
create a symbolic link, causing the rejection test and the no-resolution spy
to disappear together.

**Concrete failure scenario:** a Windows runner lacks link-creation privilege;
all three link tests skip, and a regression that resolves a junction before
checking it can still produce a green matrix. D6.1 and acceptance criterion 6
require the mutation to execute in every Windows cell. A deterministic mocked
reparse test is needed even when an integration link cannot be created.

**Deviation status:** undocumented; four such tests skipped on this non-Windows
review host, and the workflow contains no non-skippable fallback.

### F6 — Blocker — project build hooks execute on networked runners before the network-none boundary

**Location:** `.github/workflows/ci.yml:107-108`, `:533-534`, and `:566-567`;
`SECURITY.md:131-141`

**Defect:** the tests, offline-static, and provenance jobs each run
`pip install .` on the hosted runner, invoking the project PEP 517 backend
outside the D5 container even though the plan and security document say no
build hook executes before the network-none boundary.

**Concrete failure scenario:** a pull request sets `backend-path` to a local
backend whose metadata hook makes an HTTP request. The tests job executes that
hook with host networking before either the static scanner or the isolated
build can fail the change. The later red gate cannot undo the pre-boundary
execution or an egress that already happened.

**Deviation status:** undocumented and security-relevant.

### F7 — Blocker — the lock does not independently reject source inputs and the required acquisition mutation is absent

**Location:** `requirements-dev.lock:1-70` and
`.github/workflows/ci.yml:136-190`

**Defect:** the universal lock carries source-archive hashes and no
binary-only directive or lexical rejection of VCS, editable, and local/path
requirements; only the current command-line `--only-binary` option supplies
that boundary, and the required malicious-source metadata/sentinel mutation
does not exist.

**Concrete failure scenario:** a later edit drops or misplaces
`--only-binary`, or introduces a local source requirement. Its metadata hook
runs during networked acquisition and writes the sentinel, but every current
test remains green because no mutation constructs that input and proves both
rejection and sentinel absence. D5 explicitly requires the lock and prefetch,
not just one option in the happy path, to reject this class.

**Deviation status:** undocumented and contrary to D5.

### F8 — Blocker — two required container-image red mutations do not exist

**Location:** `.github/workflows/ci.yml:192-220`

**Defect:** the production branches reject a tag-only reference and a
nonmatching observed digest, but CI never deliberately supplies either bad
state and proves that the job turns red.

**Concrete failure scenario:** a refactor weakens the shell pattern or compares
the observed digest to itself. The normal pinned value still passes and no
test fails, although D5 requires tag-only and wrong-observed-digest mutations.
The separate build-egress mutation is present; these two are not.

**Deviation status:** undocumented acceptance-criterion omissions.

### F9 — Blocker — the built-artifact allowlist rejects files that the current build necessarily emits

**Location:** `pyproject.toml:34-46` and
`.github/workflows/ci.yml:327-353`

**Defect:** the wheel allowlist omits `synthtwin/paths.py`; the sdist rules omit
`ROOT/src/synthtwin/paths.py`, the extensionless signer file, and the signature
file included under `tools/`.

**Concrete failure scenario:** a local no-isolation build emitted all four
members. The CI content checker classifies them as unexpected, exits 1, and
forces both `build` and `gate` red on the first public run. This is statically
decidable and is not deferred to public-runner verification.

**Deviation status:** undocumented ordinary breakage of D6.4, D9, and
acceptance criterion 3.

### F10 — Blocker — extractor and public scanner do not share the ratified surface implementation

**Location:** `tools/decontamination/check.py:47-144` and the bound private
`surfaces_v2.py` and `tokenizer_v2.py`

**Defect:** the public checker reimplements tokenization, decoding, and text
surface construction instead of using the single shared module required by
D7 Amendment A1.

**Concrete failure scenario:** a decoder-order repair is made in the public
checker but not in the private extractor. The public tree scan and private
inventory then operate on different candidate sets, recreating the exact drift
the shared-module ruling was intended to prevent. The reviewed versions are
substantially aligned today, but they are not identical by construction and
there is already no bound repeatable equivalence harness (F12/F13).

**Deviation status:** undocumented and directly contrary to the ratified
architecture.

### F11 — Blocker — the bound extraction pipeline cannot regenerate the committed manifest

**Location:** bound private `extract_inventory_v2.py:119-133`, the bound final
freeze record, `tools/decontamination/manifest.txt:5-9`, and
`tools/decontamination/attestation.json:3-21`

**Defect:** the extractor reads `freeze["artifacts"]`, but the bound final
freeze record contains `final_artifacts`; in addition, all five artifact
digests in the public manifest header disagree with the final bound artifacts
and signed attestation.

**Concrete failure scenario:** a refresh trigger occurs and the maintainer
runs the attested extractor. It raises `KeyError` before regeneration. An
auditor meanwhile sees obsolete header bindings while
`verify_attestation.py` reports that all public digests match because it never
checks those fields. This breaks D7's reproducibility and binding contract even
though the current 2,065 manifest entries match the current private inventory.

**Deviation status:** undocumented; the attestation note mentions a later
file-enumeration repair, not this inconsistent final graph.

### F12 — Blocker — the signed attestation does not bind or recompute its complete trust graph

**Location:** `tools/decontamination/attestation.json:3-27`,
`tools/decontamination/verify_attestation.py:25-33` and `:59-75`, and
`SECURITY.md:195-205`

**Defect:** `coverage_tool` is prose rather than a tool digest; no versioned
7,639-form coverage harness is present; `SCANNER_TREE` omits the verifier and
signer file; the separately asserted public magic-table binding and actual
manifest-entry count are not recomputed; and `SECURITY.md` does not record the
promised key or fingerprint.

**Concrete failure scenario:** replace `allowed_signers`, sign with the
replacement key, and weaken the unbound verifier. The listed scanner-tree
digest is unchanged and the modified verifier accepts the new chain. A signed
manifest whose header count does not equal its actual entry count also passes,
because the verifier compares two declared numbers rather than counting hash
entries. This does not provide D7's third-party origin or complete-drift
guarantee.

**Deviation status:** undocumented and security-critical.

### F13 — Blocker — the decontam CI job does not perform its claimed verification, and the required D7 battery is incomplete

**Location:** `.github/workflows/ci.yml:494-515` and
`tests/test_decontamination.py:50-150`

**Defect:** the named job invokes only `check.py`, which neither verifies the
attestation nor runs mutations, while the generic test job supplies only a
partial battery.

**Concrete failure scenario:** break malformed-BOM rejection, a BOM-less wide
encoding route, a surviving unknown-magic route, an enclosed compatibility
form, a shell-only surface, missing-signature rejection, or wrong-key
rejection. No current mutation isolates those required cases, so the suite can
remain green. Valid BOM-tagged clean inputs are also never shown green, and
only one listed magic signature is tested. The comment at CI lines 501-505 is
therefore false.

**Deviation status:** undocumented and contrary to D7, D9, and acceptance
criterion 5.

### F14 — Blocker — the provenance extension policy allows common real-derived artifact formats

**Location:** `tools/provenance/check_provenance.py:59-101`

**Defect:** the data-format gate recognizes a narrow suffix set and treats
JSON, JSON Lines, Arrow-family files, columnar and array stores, common
statistical-package files, and several database/spreadsheet forms as ordinary
source.

**Concrete failure scenario:** commit a numeric profile as `profile.json` or a
table as `rows.jsonl`, containing only common words and short numbers. Direct
probes returned `False` from `is_data_format` for both. The provenance checker
accepts the file without a fixture entry, while the declared decontamination
residual can also accept its contents. D13's no-real-derived-artifact policy
then fails silently.

**Deviation status:** undocumented; the existing CSV mutation proves only one
suffix.

### F15 — Blocker — D13's pre-first-push and history evidence chain is incomplete

**Location:** `tools/decontamination/attestation.json:3-21`, the signed private
pre-first-push note, repository Git objects, and the absence of a public hook
installer

**Defect:** the signed note's digest is absent from the first attestation; its
all-object result records only 44 blobs although this repository has 11 commit
and 31 tree objects as well; and the required one-command advisory pre-push
hook does not exist.

**Concrete failure scenario:** protected content exists only in a commit
message or historical filename. A blob-only battery reports clean, the
unbound note cannot prove the required run, and no installed advisory hook
stops the push before public CI. I independently scanned the present 44 blobs,
11 commit representations, and 31 tree name sets with zero matches or decode
violations; the finding is about the promised repeatable control and evidence,
not a current match.

**Deviation status:** undocumented and contrary to D13 and acceptance
criterion 7.

### F16 — Blocker — the history omits every required source-literal provenance checklist line

**Location:** commits `c979e85`, `fafaee6`, `790d2b7`, `afe2769`, and
`590d5ca`; `CONTRIBUTING.md:33-38`

**Defect:** each listed commit adds literal string or numeric constants under
`src/` or `tests/`, but none contains the exact D13 checklist line and no pull
request description exists for this local history.

**Concrete failure scenario:** a common real-derived literal is copied into a
test and falls within the explicitly named machine-scan residual. All automated
checks stay green, and the only human control assigned to that residual has no
auditable record. The commit messages need repair before the first push.

**Deviation status:** undocumented process failure in the scoped Git history.

### F17 — Blocker — D14's sensitive-path labeling control is claimed but not implemented

**Location:** `.github/workflows/ci.yml:23-27` and `:39-625`;
`SECURITY.md:228-232`

**Defect:** no job detects changes under `.github/workflows/**` or `tools/**`,
no labeling step exists, and the workflow has no permission capable of applying
a pull-request label.

**Concrete failure scenario:** a pull request changes a checker together with
the workflow that invokes it. CI applies no required security-sensitive label,
despite `SECURITY.md` describing that control as in force, so the planned
review signal is absent.

**Deviation status:** undocumented and statically false; it is not a
pending-settings item.

## Major review items

### F18 — Major — fixture manifest paths and generators are not contained to reviewed repository code

**Location:** `tools/provenance/check_provenance.py:202-246`, `:251-308`, and
`:337-375`

**Defect:** the checker accepts absolute and `..` paths, does not require the
fixture or generator to be tracked, and executes the generator in a new Python
process without the socket guard despite its own no-network rule.

**Concrete failure scenario:** a manifest points `generator` at a sibling file
on the maintainer machine. The checker executes out-of-repository code with
host networking and can copy its last 500 stderr bytes into CI output while
claiming the entry follows the repository-relative generator contract.

### F19 — Major — the build-closure comparison is one-way but reports equality

**Location:** `.github/workflows/ci.yml:260-311`

**Defect:** the comparator checks that every frozen installed package has the
right locked version, but never checks that every lock entry applicable to the
container is present.

**Concrete failure scenario:** remove an applicable locked package line from
`build-freeze.txt`. The loop has no reverse-set comparison and still prints
`build closure matches the lock`, so a truncated executing environment can be
reported as exact. Marker evaluation is needed before comparing both sets.

### F20 — Major — decontamination output is not value-silent for a protected filename

**Location:** `tools/decontamination/check.py:190-213` and
`tests/test_decontamination.py:38-70`

**Defect:** every match prints `f.relative_to(root)`, so when the matched
surface is a path component the output repeats the protected path text; tests
assert only exit codes and never assert absence of the canary from output.

**Concrete failure scenario:** place a protected token only in a filename. The
scanner correctly returns red but writes that token into local or CI logs,
contradicting its `locations and digest prefixes only, never matched text`
claim.

### F21 — Major — the lexical-order test observes only resolution, not every filesystem call

**Location:** `tests/test_paths.py:170-187`

**Defect:** the test message claims to prove lexical rejection before any
filesystem call, but its spy watches only `Path.resolve` and not `os.getcwd`,
`os.lstat`, or other filesystem operations.

**Concrete failure scenario:** move `os.getcwd()` or `os.lstat()` above the
raw-string rejection. The test still passes although D6.1's security-relevant
ordering has regressed.

### F22 — Major — socket-guard timing is implemented correctly but is not regression-tested

**Location:** `tests/conftest.py:26-33` and
`tests/test_socket_guard.py:8-23`

**Defect:** all self-tests execute after collection, so moving the monkeypatch
into an autouse fixture would leave them green even though package imports and
test collection would then happen before the guard.

**Concrete failure scenario:** a refactor installs `_blocked` in a fixture.
The three current assertions run after fixture setup and pass; a connection
attempt in an imported test module occurs earlier and escapes. A collection-
time sentinel module is needed to prove D6.3 timing.

### F23 — Major — `SECURITY.md` omits concrete supply-chain trust records required by D5

**Location:** `SECURITY.md:110-141`

**Defect:** the document does not record the actual build-image digest or name
the container runtime and git/OS tooling as trust roots, and its role table
describes several hash-locked tools only as versions recorded in logs.

**Concrete failure scenario:** an institutional auditor follows
`SECURITY.md` without opening the workflow and cannot compare the selected
image or identify all unpinned execution roots, despite D5 requiring those
facts in this document. A later workflow digest change can also drift from the
security record because no concrete value is present there.

## Minor review items

### F24 — Minor — public status documentation is internally stale

**Location:** `README.md:3-7`, `:44-46`, and `:91-100`;
`SECURITY.md:202-205`; `docs/plans/phase-0-public-skeleton.md:562-629`

**Defect:** the future determinism guarantee lacks a `[planned]` tag despite
the README's every-capability promise; “no data files ... ever” is followed by
a fixture exception; `SECURITY.md` says the signer key was added in the first
commit although it entered in commit six; and Amendment A1 still says pending
even though the implementation and attestation say the private inventory cycle
ratified it.

**Concrete failure scenario:** an auditor reads the current public documents
and classifies future byte determinism and the signer's history incorrectly,
or cannot tell which D7 text is normative without consulting private records.

### F25 — Minor — the CLI version contract is weakly tested and its public entry function lacks the required guarantee docstring

**Location:** `src/synthtwin/cli.py:28-57` and `tests/test_cli.py:16-19`

**Defect:** `main` has no public-function docstring covering inputs, return
behavior, and errors, while the version test accepts any nonempty output rather
than checking the metadata-backed version.

**Concrete failure scenario:** `--version` is changed to a stale constant or
the full status block. Both the unit test and artifact smoke test remain green,
despite D4's single-version-source rule.

## Test-honesty accounting

The following required controls do have meaningful red demonstrations:

- direct disallowed import, direct dynamic import, entry-point reference,
  direct process APIs, and a direct native-call API;
- direct `sys.modules`, function-global-state, and reflection references;
- ordinary URL, UNC, and device forms;
- the runtime socket guard's two patched APIs;
- an unlisted CSV and an allowlisted fixture whose manifest hash matches the
  substituted bytes, so only regeneration detects the substitution;
- the build-container HTTP attempt exists statically; execution remains
  pending-public-verification.

Those tests do not rescue the missing or bypassed classes in F1-F8 and
F10-F15. In particular, the direct scanner mutations are not representative of
allowed-module proxies or control-flow rebinding, the Windows link proof can
skip, and the decontamination tests do not constitute the ratified full
battery.

## Acceptance-criterion status

| Criterion | Status | Evidence |
| --- | --- | --- |
| 1 — owner waiver and README license record | **satisfied** | The dated owner waiver is in D2 and `README.md:116-123` records the requested basis. |
| 2 — public governance settings | **pending-public-verification** | Requires the GitHub rulesets/settings API and account evidence. F17 is a separate static workflow defect. |
| 3 — install, isolated build, artifacts, smoke, egress | **failed pre-push** | Tests import the installed package, but F9 makes the build gate necessarily red and F6 violates the build-hook boundary. Actual container execution remains pending. |
| 4 — no runtime dependencies and frozen complete lock | **partially satisfied; not accepted** | `dependencies = []` and a hash lock exists, but F7 violates the lock-level acquisition rule and F19 makes the closure comparison non-exact. |
| 5 — decontamination and signed attestation | **failed** | Current tree scan and signature pass; F10-F13 and F20 break the ratified implementation, binding, and mutation contract. The private-notes path does resolve outside the repository. |
| 6 — offline policy and nine mutation classes | **failed** | Current source is manually clean, but F1-F5 expose accepted bypasses or missing mandatory evidence; two D5 image mutations are absent. |
| 7 — provenance, all objects, and bound pre-push run | **failed** | The two existing fixture mutations are honest and the current full object set is clean, but F14-F16 and F18 leave the policy and evidence incomplete. |
| 8 — consistent documentation and named residuals | **partially satisfied; not accepted** | Canonical briefs and named residuals are present, but F17, F23, and F24 make material claims incomplete or false. |

## Pending-public-verification, not review items

- creation and availability of the public repository;
- the default-branch ruleset: PR-only, app-bound `gate`, force-push and
  deletion blocks, and no bypass actors;
- tag restrictions, signing enforcement, fork-workflow approval, repository
  workflow permissions, 2FA, recovery-code handling, and private vulnerability
  reporting;
- real GitHub-hosted execution of the Ubuntu/macOS/Windows Python matrix,
  especially non-skipped Windows reparse behavior;
- pull and observed-digest verification of the pinned container image, the
  real `--network none` namespace, artifact smoke behavior, and the aggregate
  status context on GitHub infrastructure.

The workflow's action references are full commit SHAs, default token permission
is `contents: read`, no privileged trigger or secret reference is present, and
the two action SHAs were checked against their documented upstream releases.
Those static positives do not substitute for a public run.

## Deviation accounting

The task says six builder components recorded deviation lists in a workflow
record. No such record was available as a repository file, Git note, commit
body, planning-notes index entry, or other searchable workspace artifact, so I
could not map assertions to those six lists. That makes their documentation
status **unverified**. More importantly, the canonical brief says a builder
handoff does not amend the plan: a semantic deviation must be fixed or placed
in a ratified plan amendment.

Against repository evidence, the deviations in F1-F18 are undocumented. The
attestation note does disclose one scanner file-enumeration repair and a
coverage rerun; that disclosure is credible for that narrow edit but does not
cover the broken extractor, stale header, missing coverage-tool binding, or
other deviations above.

## What I checked and ran

- Read the canonical `AGENTS.md` and `CLAUDE.md`, all 629 lines of the
  conditioned plan, the relevant closed review rulings, the complete scoped
  source/tests/tools/docs/workflow, and all 11 commit bodies and trees.
- Inspected D5 acquisition, wheelhouse hashing, image pinning, container
  command, closure comparison, artifact member rules, fresh-venv smoke, egress
  mutation, and aggregate gate logic.
- Audited D6.1 lexical ordering and Windows component walking; D6.2 import,
  alias, module-state, attribute, subscript, and call handling; and D6.3 guard
  installation timing.
- Compared the D7 public tokenizer/decoder/surfaces with their bound private
  counterparts without printing inventory entries; recomputed direct binding
  digests, confirmed all 2,065 manifest hashes match the current private
  inventory, confirmed `n_max = 578`, and confirmed the current snapshot tree
  digest. The failure is the inconsistent/re-unrunnable chain described in
  F10-F12, not an unverified claim that the current entries differ.
- Verified the private-notes path resolves outside the repository and checked
  that no protected vocabulary was reproduced in this review.
- Inspected all 43 tracked paths; ran `git fsck --full --no-reflogs`; confirmed
  a linear 11-commit history with no reported corrupt or unreachable objects;
  and independently scanned 44 blobs, 11 commit representations, and 31 tree
  name sets with zero matches and zero decode violations.
- Built the wheel and sdist locally with `python -m build --no-isolation` into
  a temporary directory and confirmed the four F9 members are emitted.
- Ran targeted non-executing probes for allowed-module process paths,
  control-flow alias loss, unknown callback calls, punctuated URL schemes,
  simulated Windows `PermissionError`, provenance suffix classification,
  manifest/attestation header consistency, extractor/freeze schema
  consistency, and pre-push-note binding.

Commands run from the repository root:

```text
.venv/bin/python -m pytest
  68 passed, 4 skipped in 1.63s

.venv/bin/python -m ruff check .
  All checks passed!

.venv/bin/python -m mypy src
  Success: no issues found in 3 source files

.venv/bin/python tools/decontamination/check.py
  decontamination: clean

.venv/bin/python tools/decontamination/verify_attestation.py
  attestation: verified (signature valid, implemented public checks match)

.venv/bin/python tools/offline_scan/scan_imports.py src
  3 Python files, 0 reported violations

.venv/bin/python tools/provenance/check_provenance.py
  current tracked tree reported clean

direct file-level decontamination scan of this review through check.py's
decoder, surface builder, tokenizer, and manifest matcher
  0 matches, 0 violations
```

Docker is unavailable on this review host, so I did not claim local execution
of the container step. The static workflow defects above are independently
decidable; actual image and namespace behavior remains in the pending list.

## Verdict

**Request changes.** No bounded ratification conditions are offered in this
round: the blockers require implementation, test, signed-binding, history, and
workflow changes, not a small set of text-only edits. Preserve the current
positive facts — manually offline-safe `src/`, a clean tracked/object set,
honest D13 substitution test, SHA-pinned actions, and read-only workflow token
— but do not push this history or begin Phase 1 until every blocker is fixed or
the behavior is explicitly taken back through a ratified plan amendment. Each
finding requires a fix or an evidence-backed rebuttal in the round-1 response.

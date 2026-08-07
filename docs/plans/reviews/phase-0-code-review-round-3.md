# Phase 0 code review — round 3

**Reviewed:** the 15-commit Phase 0 history at
`30ca7a13ffcc0356151cff76e2fe4c9327fb2975`, the canonical briefs, the
conditioned Phase 0 plan including D14 Amendment A2, the round-2 review and
implementer response, the complete changed public tree, the Git object graph,
and the maintainer-private evidence chain without reproducing protected values

**Verdict:** **request changes**

**D14 Amendment A2:** **ratified**

**Public push authorization:** **not granted**

**Public-host items:** remain **pending-public-verification**

The round-2 response closes many real defects: first-party import laundering,
the textual lock gate, the filed manifest contradictions, full magic-table
parameterization, the named format suffixes, fail-closed historical-blob
handling, the missing post-commit evidence, destructive hook replacement, and
the three documentation defects all behave as claimed in their filed probes.
The refreshed current evidence chain is internally consistent.

Ratification still fails. The offline scanner accepts unknown callbacks handed
to allowed higher-order APIs; the attestation verifier accepts contradictory
duplicate JSON members after a valid fresh signature; the YAML provenance
exception admits arbitrary non-workflow data files; and the audit-hook runner
is bypassable through process and native-call routes below its selected event
names. In addition, the committed CI workflow is syntactically invalid YAML,
so no hosted job can instantiate from these bytes. These have concrete failure
scenarios against claims the code and conditioned plan make.

During this review, the checkout gained an `origin` and the remote-tracking
reflog recorded `origin/main` moving to the reviewed 15-commit head. The push
therefore appears to have occurred before this verdict. That external action
does not ratify the history. Do not tag, release, or begin Phase 1 on this
state; repair forward rather than rewriting otherwise clean public history.

## Round-2 finding disposition

| Item | Round-3 status | Independently verified evidence |
| --- | --- | --- |
| **R2-B1** | **resolved** | The scanner builds top-level defined/imported sets at `tools/offline_scan/scan_imports.py:358-395`, checks first-party `from` imports at `:999-1038`, and constructs the export map tree-wide at `:1381-1422`. Sibling-present laundering, sibling-absent fallback, and legitimate-export probes all passed; the laundering cases were red for the intended reason. |
| **R2-B2** | **partially resolved — blocker remains** | The explicit unknown origin now survives unions, a callback invoked directly is red, and an unknown receiver's non-enumerated method is red. However, unknown callback parameters passed to `sorted`, `json.loads`, or `ArgumentParser.add_argument` each produced **zero violations**. `_check_callable_arguments` at `scan_imports.py:1211-1232` recognizes only a direct lambda or a name already classified as a local definition; it ignores an unknown parameter. The fixed untraced-method exception at `:162-167,1160-1175` also still accepts `.find` without resolving the receiver to an exact API. |
| **R2-B3** | **resolved** | `tools/supply_chain/validate_lock.py:80-128,131-216` rejects paths, archives, VCS, editable, URL, direct-reference, malformed-pin, and missing-hash forms lexically. All 34 validator tests passed. A real local PEP 517 source archive named with its correct SHA-256 was rejected with exit 1 for the archive/path reason, and both execution sentinels remained absent. CI places the validator before prefetch at `.github/workflows/ci.yml:169-192`; the self-contained archive mutation is at `:235-330`. |
| **R2-B4** | **partially resolved — blocker remains** | The shared parser at `tools/decontamination/check.py:59-113` now rejects duplicate control headers and malformed body lines. The verifier's filed missing-binding, direct-public-digest, snapshot/header, duplicate-header, duplicate-body, and isolated-count mutations all went red under fresh temporary signatures. But plain `json.loads` at `tools/decontamination/verify_attestation.py:187` discards duplicate member names before `schema_problems` at `:123-155` sees them. Freshly pinned and re-signed graphs with contradictory duplicate top-level and nested binding members both returned 0 and claimed an exact v2 graph. |
| **R2-B5** | **partially resolved — major residual** | The bound private battery now drives committed `check.py` in line, UTF-16, CSV-cell, syntax-tree-string, and filename modes. The normal run detected every applicable entry, and temporary layouts missing the checker/surface module or manifest returned 1. However, `planning-notes/decontamination/coverage_battery.py:45-50` discards every scanner return code and `:111-124` decides success only from parsed match prefixes. A copied decoder deliberately made the simple filename-mode payload a fail-closed violation while its protected filename still matched; the scanner returned match-plus-violation, but the battery returned 0 with zero misses. |
| **R2-B6** | **resolved** | `tests/test_decontamination.py:213-232` loads the committed table at collection time. The table had 22 unique offset/signature pairs; all 22 parameterized mutations passed. The nonempty-table sentinel passed as well. |
| **R2-B7** | **partially resolved — blocker remains** | XML, SQL dump, DuckDB-family, DBF, transport, and YAML outside `.github/` now route through `tools/provenance/check_provenance.py:73-181,484-534`; the 27-suffix battery and the focused named probes passed. The blanket `relative.startswith(".github/")` exemption at `:494-508` is broader than workflow configuration: an independently created `.github/nonworkflow.yaml` carrying a table passed with no manifest entry. |
| **R2-B8** | **resolved** | `planning-notes/decontamination/all_objects_scan.py:63-78,97-103` increments violations for every non-text blob and includes them in the exit status. A scratch repository with an unreachable malformed blob returned 2 and reported one violation. The current graph returned 0 with 92 blobs, 15 commits, 66 trees, zero matches, and zero violations. |
| **R2-B9** | **resolved** | The pre-first-push note is signed, its digest equals the current attestation binding, and its recorded head equals current `HEAD^`. The only following commit changes `attestation.json` and its signature. A pruned reconstruction of the recorded head reproduced 90 blobs, 14 commits, 63 trees, and a clean scan. The new post-commit artifact and signature exist, validate under the pinned identity/namespace, name exact current `HEAD`, and its 92/15/66 clean result reproduced. Its digest is truthfully scheduled for the next attestation refresh rather than falsely claimed as already bound. |
| **R2-B10** | **resolved by this review's A2 ratification** | The replacement mechanism at `.github/workflows/ci.yml:891-954` records comparison status, exits 1 on comparison failure, and emits a warning plus step-summary path list on success; `gate` depends on the job at `:956-1007`. `SECURITY.md:248-259` states the same mechanism and token tradeoff. The global workflow parse failure is a separate new blocker below. |
| **R2-B11** | **unresolved — blocker** | The named low-level socket and ordinary `subprocess` tests pass, but `tools/provenance/guard_runner.py:43-86` blocks only selected audit-event names. Through the actual runner, a standard low-level process primitive started a benign external program, created its sentinel, and exited 0; a native-call route created a socket descriptor and also exited 0. Both contradict the absolute claims at `guard_runner.py:11-27` and `tools/provenance/check_provenance.py:394-403`. |
| **R2-M1** | **resolved** | `tests/test_decontamination.py:559-575` removes one body line, refreshes the outer manifest binding, re-signs, and asserts the specific inner count failure without manifest-digest drift. The isolated test passed. |
| **R2-M2** | **resolved as filed** | `tools/hooks/install.sh:32-48` compares an existing hook and refuses before replacement. The foreign-hook bytes remained identical, and an identical reinstall remained quiet; both focused tests passed. A different active-hook-path defect is listed below. |
| **R2-m1** | **resolved** | The D7 A1 heading and terminal status both say ratified at `docs/plans/phase-0-public-skeleton.md:564,627-631`. |
| **R2-m2** | **resolved** | `src/synthtwin/cli.py:38-62` now states the narrow boundary: no user-data path read, installed metadata consulted on disk, and ordinary output errors propagate. |
| **R2-m3** | **resolved** | `.github/workflows/ci.yml:774-804` accurately distinguishes the scanner, verifier, and test-battery steps. |

## D14 Amendment A2 ruling

**Ratified.** The replacement makes the better security tradeoff for a
one-maintainer repository:

- the workflow retains the global `contents: read` token and adds no mutable
  issue/label authority;
- a valid base comparison lists the sensitive paths in both an annotation and
  the job summary;
- a failed comparison is enforcing rather than advisory: it exits 1 and the
  aggregate gate depends on it;
- release-note collection can reconstruct the same path set from immutable Git
  history, so a mutable label is not required as the durable record.

A valid local comparison listed both sensitive files changed by the final
commit and returned 0; an invalid base returned 128, which the workflow maps to
job failure. Hosted annotations, branch rules, and the first release-time
history collection remain pending-public-verification.

Apply two lifecycle text edits with the next corrective commit: change the A2
heading/status at `docs/plans/phase-0-public-skeleton.md:633-646` from pending
to ratified with this review/date, and change the pending-cycle parenthetical
at `SECURITY.md:258-259` to ratified wording. These are consequences of this
ruling, not pre-ratification defects.

## Blocking review items

### R2-B2 — Blocker — unknown callbacks still cross the static boundary

**Location:** `tools/offline_scan/scan_imports.py:1211-1232`; conditioned plan
`docs/plans/phase-0-public-skeleton.md:216-220`

**Defect:** the callback-argument checker rejects only syntactically known
functions/lambdas, not an unknown parameter placed in a callback-taking slot,
so the promised rule that every call target resolves statically to an exact
enumerated API is still false.

**Concrete failure scenario:** product source accepts a `callback` parameter
and supplies it as `sorted(..., key=callback)`, a JSON object hook, or an
argument-parser conversion callback. All three forms scanned clean in direct
probes. At runtime the allowed helper invokes caller-controlled code that can
open a connection or start a process, while offline-static remains green.

The fixed tests prove that direct callback invocation and unknown-origin union
handling improved; they do not cover the original higher-order unknown route.
The policy needs call-position-aware callback rejection or another analysis
that proves the callable's origin. A list of locally defined functions is not
sufficient.

### R2-B4 — Blocker — signed duplicate JSON members bypass exact-v2 checking

**Location:** `tools/decontamination/verify_attestation.py:123-155,187`

**Defect:** the verifier authenticates raw bytes, then parses them with a
last-member-wins JSON loader. Duplicate keys vanish before exact-schema
checking, so a signed ambiguous graph is reported as exact.

**Concrete failure scenario:** an attestation refresh/template merge emits a
stale binding followed by the current binding under the same member name. A
fresh trusted signature is applied. The current verifier selects the latter
and exits 0, while a first-member-wins consumer can select the stale value.
Independent top-level and nested-binding mutations both verified.

Reject duplicate member names at every object depth during parsing and add
fresh-key tests for at least one top-level duplicate and one duplicate inside
`bindings`. Because this changes the bound verifier, refresh the chain.

### R2-B7 — Blocker — the YAML exception is a provenance laundering directory

**Location:** `tools/provenance/check_provenance.py:120-127,484-508`

**Defect:** every YAML path anywhere below `.github/` is treated as workflow
configuration, although GitHub interprets only specific paths and the
conditioned policy permits no unexplained real-derived artifact.

**Concrete failure scenario:** a derived schema/table is saved as
`.github/nonworkflow.yaml`; its cells contain only residual-class words and
short numbers. The file is not a workflow, is absent from the fixture
manifest, and the direct checker returned 0. It can therefore enter history
without either provenance or decontamination going red.

Limit the exception to explicit, reviewed configuration paths that exist for
this repository; every other YAML file must use the fixture manifest.

### R2-B11 — Blocker — the Python audit hook is not the claimed confinement

**Location:** `tools/provenance/guard_runner.py:11-27,43-86`;
`tools/provenance/check_provenance.py:394-403`;
`tools/provenance/fixture-manifest.json:2`

**Defect:** a Python audit hook sees only events CPython or an extension elects
to emit. The runner blocks selected names, not every process/native/network
operation, and the installed Python callback remains mutable state. Calling it
“irremovable” does not make its policy tamper-resistant.

**Concrete failure scenario:** a manifest-listed generator uses a lower-level
process primitive that emits none of the blocked prefixes, starts an external
client, and then writes the exact committed fixture bytes. In a controlled
probe the actual runner exited 0 and the external sentinel existed. A separate
native-call probe created a socket descriptor and also exited 0. The provenance
checker would accept the byte-identical fixture despite the documented “never”
guarantee.

This is not closed by appending two more event strings: an in-process Python
hook is not an OS sandbox and native calls need not emit Python audit events.
Implement a control that actually matches D13, or amend the plan and every
public claim to a defensible reviewed-source guarantee before adding any
fixture generator.

### R3-B1 — Blocker — the committed CI workflow is invalid YAML

**Location:** `.github/workflows/ci.yml:802`

**Defect:** the new one-line `run:` scalar contains an unquoted `:all:` token
followed by a space, which terminates a YAML plain scalar illegally.

**Concrete failure scenario:** GitHub reads the pushed workflow and rejects it
during YAML parsing before job creation. No lint, type, test, build,
decontamination, offline-static, provenance, sensitive-path, or aggregate gate
job exists for the commit; if `gate` is required, all PRs are stuck, and if it
is not required, none of the claimed checks protects the branch.

Ruby/Psych stopped at line 802, column 71. Replacing that one command with a
block scalar in memory made the complete workflow parse. Repair the scalar and
run a GitHub-compatible workflow syntax check before the next review.

## Major finding

### R3-M1 — Major — the bound coverage battery ignores scanner failure status

**Location:** `planning-notes/decontamination/coverage_battery.py:45-50,111-124`

**Defect:** `scan_tree` returns only parsed digest prefixes and drops the child
exit status/stderr, so coverage can be declared passing while the public
scanner reports a fail-closed violation.

**Concrete failure scenario:** a decoder regression classifies the filename
mode's simple text payload as invalid. The path component still produces every
expected match, while `check.py` exits with match-plus-violation. The copied
battery returned 0 and reported every filename form detected. A signed “pass”
would therefore hide a broken scanner route even though the actual scanner was
red.

Require the expected match-only exit for every mode and treat execution error,
stderr, or any other status as battery failure. Add this exact match-plus-
violation mutation. This private-tool change is attestation-bound and requires
a fresh coverage run and signature.

## New minor review items

### R3-m1 — Minor — the hook installer can install to an inactive hook path

**Location:** `tools/hooks/install.sh:11-14`

**Defect:** the installer hard-codes `$REPO_ROOT/.git/hooks/pre-push` instead
of asking Git for the active hook path.

**Concrete failure scenario:** a repository configures `core.hooksPath` and a
contributor runs the advertised installer. The probe exited 0 and announced
success, but the active hook path stayed empty while an unused file appeared
under `.git/hooks`. Linked worktrees also use a `.git` file rather than this
directory shape.

Resolve the path through Git and add custom-hook-path plus linked-worktree
tests. This stays minor because the hook is explicitly advisory and CI is the
enforced control.

### R3-m2 — Minor — the public magic table labels itself as private

**Location:** `tools/decontamination/magic.txt:1-3`

**Defect:** the public scanner's committed table says it is the
maintainer-private copy and that a separate public copy exists.

**Concrete failure scenario:** an auditor follows the header literally and
concludes the public scanner is loading the wrong side of the handoff, even
though byte comparison and attestation binding show this is the public copy.
Change only the role label; the table bytes are bound, so include the edit in
the required refresh.

## Attestation and evidence-chain verification

The committed graph is internally consistent apart from the verifier/parser
and battery defects above:

- the current attestation signature validates against the pinned signer and
  namespace;
- all 18 attestation digest bindings independently recomputed; all 12 final
  freeze-record artifacts matched;
- the canonical private snapshot digest and complete seven-file public scanner
  tree digest matched their bindings;
- the private inventory and public manifest each contain 2,065 sorted unique
  entries/hashes; hashing every inventory entry reproduced the public body;
  the recorded maximum token length is 578;
- the public and private frozen magic tables are byte-identical;
- the normal private coverage run found every applicable entry in all five
  modes and zero misses;
- the pre-first-push note signature validates, its digest is bound, its head is
  exact current `HEAD^`, and a history reconstructed at that head reproduced
  its 90-blob/14-commit/63-tree clean result;
- the attestation-only final commit changes exactly the attestation JSON and
  signature;
- the post-commit verification artifact signature validates, its recorded
  final head equals current `HEAD`, and its 92-blob/15-commit/66-tree clean
  all-object result plus 196-pass/4-skip test result reproduced.

The post-commit artifact is not yet a current attestation binding. That is not
the former false-evidence defect: both signed records explicitly schedule its
digest for the **next** refresh. This round's required verifier/battery/table
changes will trigger that refresh, so the next schema and attestation must bind
the existing post-commit artifact as promised. After the new attestation
commit, produce and sign a new post-commit verification record for that head;
do not claim self-binding in the same commit.

## Required commands and results

Run from the public repository root unless stated otherwise:

```text
.venv/bin/python -m pytest -q
  196 passed, 4 skipped in 4.46s
  (the skips are host-inapplicable real-Windows integration tests)

.venv/bin/python -m ruff check .
  All checks passed

.venv/bin/python -m mypy src
  Success: no issues found in 3 source files

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/decontamination/verify_attestation.py
  current committed graph verified

.venv/bin/python tools/offline_scan/scan_imports.py src
  3 Python files, 0 reported violations

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  both requirement files passed structural validation

private coverage_battery.py
  L 2065/2065; ENC 2065/2065; C 2065/2065;
  A 2065/2065; P 1829/1829; 0 misses

private all_objects_scan.py
  92 blobs; 15 commits; 66 trees; 0 tags;
  0 matches; 0 violations
```

Focused suites also passed: seven filed offline-scanner probes; all 34 lock
validator tests; 22 magic signatures plus the nonempty and isolated-count
checks; seven strict filed attestation mutations; and eight named provenance,
guard, and hook tests.

Additional direct probes covered:

- first-party `from`-import laundering with and without sibling source;
- unknown method, unknown-origin union, unknown higher-order callback, JSON
  callback, and parser callback routes;
- a correctly hash-bound self-contained local source archive with two absent
  execution sentinels;
- fresh-key re-signed semantic contradictions, including duplicate manifest
  headers and duplicate JSON members;
- coverage with scanner/surface files absent and with match-plus-violation
  status;
- all 22 committed magic signatures;
- YAML, XML, SQL, DuckDB-family, DBF, and transport paths, including the broad
  `.github/` exception;
- ordinary and below-wrapper socket/process routes through the actual generator
  runner;
- an unreachable malformed Git blob;
- foreign-hook refusal, idempotent reinstall, and a custom active hook path;
- valid and invalid sensitive-path base comparisons;
- both private evidence signatures and the pre-/post-commit history states;
- full workflow YAML parsing; and
- the current tree and all Git objects with value-silent output.

Docker is unavailable on this host, so the real pinned image, `--network none`
container build, image-digest mutations, cross-platform matrix, and hosted
artifact flow were not executed locally.

## Acceptance-criterion status

| Criterion | Round-3 status |
| --- | --- |
| 1 — owner waiver and README record | **satisfied** |
| 2 — public governance settings | **pending-public-verification**; A2 is ratified, but R3-B1 prevents the committed workflow from loading |
| 3 — build, artifacts, smoke, egress | **not accepted**: hosted/container execution remains pending and the workflow is invalid YAML |
| 4 — empty runtime set and frozen closure | **satisfied locally**: structural validator and lock tests pass; hosted consumption remains pending |
| 5 — decontamination and signed attestation | **not accepted**: current bytes/signatures match, but R2-B4 and R3-M1 leave strict graph and bound-result claims incomplete |
| 6 — offline policy and mutations | **not accepted**: R2-B2 retains an executable higher-order call-target bypass |
| 7 — provenance and all-object evidence | **not accepted**: R2-B7 and R2-B11 retain silent artifact and generator-capability routes, although the current all-object chain is clean |
| 8 — documentation and residuals | **not accepted**: the generator guarantee and public table role label are inaccurate; A2 lifecycle wording now needs the ratification update |

## Pending-public-verification

The local remote-tracking state now shows the reviewed head on `origin/main`,
but that does not verify host controls. Still pending:

- default-branch ruleset details, app-bound `gate`, force-push/deletion blocks,
  bypass actors, tag restrictions, signing enforcement, fork-workflow approval,
  workflow permissions, two-factor account state, recovery-code handling, and
  private vulnerability reporting;
- the real hosted Ubuntu/macOS/Windows Python matrix, including non-skipped
  Windows reparse behavior;
- the pinned container pull/inspection, real network-none build, artifact
  transfer and smoke behavior, image mutations, sensitive-path annotations,
  and aggregate status context; and
- the first release-time sensitive-history collection under ratified A2.

The workflow remains statically positive on full-SHA action references,
read-only default token permission, absence of privileged triggers/secrets,
and complete declared gate dependencies. Those source facts do not overcome
the YAML parse blocker or substitute for hosted execution.

## What was checked

- Read the canonical reviewer/implementer briefs, all 646 lines of the
  conditioned plan including A2, the complete round-2 review and response,
  every changed source/tool/test/document/workflow section, and all 15 commit
  bodies and trees.
- Re-ran every named round-2 probe and chased adjacent same-class routes rather
  than stopping at the new regression examples.
- Recomputed the public/private attestation graph without printing any private
  inventory entry; verified current, pre-refresh, and post-commit history
  states and signatures independently.
- Ran the complete requested test, lint, type, public-tool, private coverage,
  and all-object matrix, then parsed the workflow separately.
- Inspected security, offline, provenance, decontamination, determinism-relevant
  source structure, zero-code hook behavior, documentation truthfulness, and
  public-history state. Phase 0 contains no statistical generator, so no
  numeric-fidelity behavior is claimed or reviewable yet.
- Scanned this review itself against the committed decontamination manifest
  before finalizing it.

## Verdict

**Request changes.** D14 Amendment A2 is ratified, but the Phase 0 code is not.
R2-B2, R2-B4, R2-B7, R2-B11, and R3-B1 are blockers; R3-M1 is a bound-evidence
major. The 15-commit history was **not authorized for public push** by this
review and, although it now appears on `origin/main`, must not be treated as
ratified. Fix forward, rerun and refresh the complete evidence chain in the
promised order, and return for round 4 of the authorized five.

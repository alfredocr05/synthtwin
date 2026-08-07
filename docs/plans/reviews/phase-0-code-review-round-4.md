# Phase 0 code review — round 4

**Reviewed:** the 18-commit Phase 0 history at
`83c9a4c03d018a189eccf0f97cd736f13e2ad0ec`, the canonical briefs, all
646 lines of the conditioned Phase 0 plan and its ratified amendments, the
round-3 review and response, the three forward repair commits, the complete
changed public tree, the Git object graph, and the maintainer-private evidence
chain without reproducing protected values.

**Verdict:** **request changes**

**D14 Amendment A2:** remains **ratified** by round 3; its two required
lifecycle text edits are still outstanding.

**Hosted CI:** **pending independent verification**. The local `gh` profile
reported its active token invalid and the API request could not connect, so no
run ID, job graph, or failed log was available to this review. Static and local
environment-parity checks are reported below; they do not substitute for the
hosted jobs.

The response closes the duplicate-JSON defect, the invalid workflow syntax,
the coverage-battery status defect, and both round-3 minor implementation
defects. It also makes the named callback, YAML, low-level process, and native
mutations red. That is real progress, but it is not the whole promised
boundary.

Three round-3 blockers retain narrower residues: the callback inventory is not
complete and the untraced-method exception still dispatches unknown code; the
YAML exemption still covers unreviewed new workflow-directory files instead
of explicit existing configuration paths; and one public provenance artifact
still makes the withdrawn absolute guard claim. Two new blockers were found:
an allowlisted typing API can evaluate dynamic annotation code while the
offline scan stays green, and the signed evidence chain attributes a green
suite to a commit whose exact tree is red. Hosted success and repository
governance would not cure those defects.

## Round-3 finding disposition

| Item | Round-4 status | Independently verified evidence |
| --- | --- | --- |
| **R2-B2** | **partially resolved — blocker remains** | The filed `sorted` key, JSON hook, `add_argument(type=...)`, positional-star, keyword-star, and unknown data-method-argument probes are red. However, direct scanner probes reported zero violations for `sys.call_tracing(callback, ...)`, `Path.walk(on_error=callback)`, and Python 3.14's `make_dataclass(decorator=callback)`; harmless runtime probes confirmed the first two invoke the supplied callback. A parameter's `.find("marker")` also remains green and dispatched a custom object's method at runtime, contrary to the plan's exact-call-target rule. |
| **R2-B4** | **resolved** | `verify_attestation.py:115-130,208-227` uses an object-pairs hook for every JSON object depth. The focused tests generated fresh temporary keys, pinned those keys, re-signed contradictory top-level and nested-member graphs, and both returned schema-invalid status 2 naming the duplicate member. |
| **R2-B7** | **partially resolved — blocker remains** | `.github/nonworkflow.yaml` and nested YAML below the workflow directory are now red. But `check_provenance.py:193-208,524-526` exempts every single-level `.github/workflows/*.yml` or `*.yaml`, while the round-3 ruling required explicit reviewed configuration paths that exist. A direct probe showed an arbitrary new file at `.github/workflows/nonworkflow.yaml` is exempt, and `tests/test_provenance.py:553-565` codifies that broad pass. |
| **R2-B11** | **partially resolved — blocker remains** | The ordinary and low-level socket/process probes, the native-call probe, and the low-level process-helper probe all went red. `guard_runner.py:27-33` and `check_provenance.py:421-434` now accurately call the hook best-effort rather than confinement. But `fixture-manifest.json:2`, a location named in round 3, still says the obsolete name-replacement design makes network use impossible. An actual-runner probe also demonstrated why that claim is indefensible: after reaching and mutating the hook's Python globals through a live frame, a generator created and closed a native socket descriptor and exited 0. Source review, not this hook, is the operative control. |
| **R3-B1** | **resolved locally; hosted result pending** | `.github/workflows/ci.yml:802-803` is now a block scalar. Ruby/Psych parsed the complete document as a mapping with all nine jobs. The absence of hosted evidence is recorded separately and does not reopen the syntax defect. |
| **R3-M1** | **resolved** | The bound private battery records each scanner return code and stderr, requires exact match-only status, and contains the demanded match-plus-violation self-test. All five modes detected every applicable entry with zero misses/status failures; the self-test returned status 3 and the battery rejected that status as required. Its digest matches the current attestation binding. |
| **R3-m1** | **resolved** | `tools/hooks/install.sh:11-22` resolves the active path through `git rev-parse --git-path`. Custom `core.hooksPath` and linked-worktree tests passed. A direct scratch-repository probe installed and executed the active hook while the inactive `.git/hooks/pre-push` remained absent. |
| **R3-m2** | **resolved** | `tools/decontamination/magic.txt:1-4` now identifies itself as the public attestation-bound copy. The semantic table rows match the private source, and the refreshed public digest verifies. |

## Blocking review items

### R2-B2 — Blocker remains — the exact call-target boundary still has open callback routes

**Location:** `tools/offline_scan/scan_imports.py:195-290,1330-1359,1417-1517`;
conditioned plan `docs/plans/phase-0-public-skeleton.md:216-220`

**Defect:** the callback-slot table is described as complete but omits
callable-taking APIs available in the supported standard library, and the
enumerated data-method exception still allows a method call whose receiver is
not resolved to an exact API.

**Concrete failure scenario:** product source accepts `callback` and calls
`sys.call_tracing(callback, ())`, or passes it as `Path.walk(on_error=callback)`.
Both forms scanned with zero violations; harmless probes showed the library
invoked the callback. On Python 3.14 the same happens statically for
`make_dataclass(..., decorator=callback)`, whose newly supported decorator
argument is a callable. Separately, `value.find("marker")` scans clean for an
unknown parameter and runs an arbitrary caller-defined `find` method. Such a
method or callback can start a process or connection while offline-static is
green.

The filed three callback tests and both star-expansion forms are now good, as
are the new argument checks on the data-method exception. They prove the named
slots, not the claimed closed world. Replace the hand-maintained incomplete
surface with a reviewed exhaustive policy for every supported interpreter, or
narrow the allowed APIs to the exact calls product source needs. Remove the
unratified unknown-receiver exception or amend the plan before relying on it.

### R2-B7 — Blocker remains — the YAML exception is still directory-shaped rather than file-shaped

**Location:** `tools/provenance/check_provenance.py:193-208,514-541`;
`tests/test_provenance.py:477-498,553-565`

**Defect:** the repair distinguishes the GitHub workflow directory from the
rest of `.github`, but it still automatically exempts any new YAML filename in
that directory instead of the explicit reviewed configuration paths ordered
in round 3.

**Concrete failure scenario:** an unmanifested derived table or schema is
stored at `.github/workflows/nonworkflow.yaml`. The direct predicate returned
true and the checker accepts it solely because of its directory and suffix;
the only currently tracked workflow is `ci.yml`. GitHub parsing is separate
from the D13 provenance decision.

Use an explicit allowlist containing the actual workflow configuration path or
otherwise bind additions to review. Keep the now-correct red behavior for YAML
elsewhere under `.github` and below nested workflow directories.

### R2-B11 — Blocker remains — one public artifact still promises confinement the implementation disclaims

**Location:** `tools/provenance/fixture-manifest.json:2`;
`tools/provenance/guard_runner.py:27-33`;
`tools/provenance/check_provenance.py:42-52,421-434`

**Defect:** the runner and checker now state a defensible best-effort,
reviewed-source posture, but the manifest schema note still describes the old
socket-stub mechanism and says a rebuild can never reach the network.

**Concrete failure scenario:** an auditor reads the manifest as the generator
contract and treats its absolute statement as enforced. A generator reaches
the runner's mutable Python state, clears the hook policy, loads a native
interface, and creates a socket descriptor; the actual runner returned 0 in a
controlled no-connect probe. The code's narrowed text admits this residual,
but the manifest tells the opposite story.

Do not add more event names and do not restore the confinement claim. Apply
the reviewed-source/best-effort wording consistently to the manifest and any
remaining `no-network guard` labels, retaining the now-red ordinary,
low-level, process, and native regression mutations.

### R4-B1 — Blocker — the signed battery note does not identify the tree that produced its claimed green result

**Location:**
`planning-notes/decontamination/out/pre-first-push-note.json:4,7`;
`planning-notes/decontamination/out/post-commit-verification-r3.json:6`;
`tools/decontamination/verify_attestation.py:83`

**Defect:** the attestation-bound pre-refresh record names commit `a01c13e` as
the battery head and records a green 215-pass/4-skip suite, while the signed
round-3 post-commit record says that same full result occurred at the parent
commit; an exact isolated checkout of that commit is red.

**Concrete failure scenario:** a maintainer runs the battery against dirty
prospective attestation bytes, records only the older Git head, and later
commits different bytes. The signature authenticates the note, but an auditor
cannot reconstruct the tested state. Here, the named commit's verifier already
requires the new post-commit binding while its committed attestation lacks it:
the independently reconstructed suite produced 8 failures, 207 passes, and 4
skips, all from that schema contradiction. Current head produces the recorded
green count, but it is not the state the note claims.

Replace or supersede the false statement with signed evidence that binds an
exact reconstructible Git tree (and clean/staged state when relevant), then
refresh the attestation in the declared order. A signature over an ambiguous
or contradicted run record is not valid acceptance evidence.

### R4-B2 — Blocker — an allowlisted typing API dynamically evaluates code while offline-static stays green

**Location:** `tools/offline_scan/scan_imports.py:146-158,931-1028`;
conditioned plan `docs/plans/phase-0-public-skeleton.md:205-220`

**Defect:** `typing` is treated as unrestricted at one attribute step, so
`typing.get_type_hints` is accepted even though it evaluates forward-reference
annotations and can execute annotation code.

**Concrete failure scenario:** a scanned function calls
`typing.get_type_hints(obj)` on an object carrying a string annotation that
invokes a function. The scanner returned zero violations, and a harmless
marker probe confirmed the annotation function ran. Replacing the marker with
a process or network action violates the no-dynamic-code boundary without
making offline-static red.

The current product source needs only `typing.Protocol` and `typing.cast`.
Make the typing surface API-granular and add an executable-annotation mutation;
audit the other wholesale module surfaces for equivalent evaluators and
loaders rather than treating module membership as a capability proof.

## New minor review items

### R4-m1 — Minor — a non-ASCII violation path breaks the scanner's exit-code contract

**Location:** `tools/decontamination/check.py:18-22,188-207`

**Defect:** match text is ASCII-safe, but the scanner interpolates an
unescaped ordinary path into stdout, so a terminal encoding that cannot
represent the filename raises `UnicodeEncodeError` before status 2 is returned.

**Concrete failure scenario:** under forced ASCII stdout, a temporary tree
contained a neutral non-ASCII filename with a recognized binary signature.
The scanner raised, wrote a traceback, and exited 1 instead of reporting the
value-silent violation and returning 2. CI remains red, but automation sees the
wrong class and a non-coder receives no actionable scanner message.

Render every untrusted path safely for the output encoding and add this exact
locale/path mutation. The explicit UTF-8 writes in the existing compatibility
tests are otherwise correct.

### R4-m2 — Minor — the ratified A2 lifecycle text still says pending

**Location:** `docs/plans/phase-0-public-skeleton.md:633-646`;
`SECURITY.md:258-259`

**Defect:** round 3 ratified D14 Amendment A2 and explicitly ordered two
lifecycle edits, but both files still say the mechanism is pending the current
code-review cycle.

**Concrete failure scenario:** a contributor reads the conditioned plan or
security policy after round 3 and cannot tell whether the warning/step-summary
mechanism has normative force, even though the review record says it does.

Apply the two text edits ordered in round 3 with the next repair.

## Attestation and evidence-chain verification

The cryptographic and digest mechanics verify; the run-record semantics do
not:

- the current public attestation and all three private JSON records validate
  under the pinned identity and their declared namespaces;
- all current public/private bindings, the complete public scanner tree, the
  canonical private snapshot tree, and every freeze-record artifact
  independently match;
- the private inventory and public manifest are sorted, unique, agree under
  per-entry hashing, and match the signed count/length metadata;
- the semantic public/private magic table rows agree; the public header's new
  role label is intentionally different and correctly rebound;
- the newly bound round-2 post-commit artifact matches its binding, names the
  correct historical head, and its historical suite, decontamination,
  attestation, and all-object results reproduced;
- the private coverage battery detects every applicable entry in all five
  modes, has zero misses/status failures, and rejects match-plus-violation
  status 3;
- the current all-object scan reports 112 blobs, 18 commits, 82 trees, zero
  tags, zero matches, and zero violations;
- the new round-3 post-commit record is signed, names exact current head, is
  correctly not self-bound, and schedules its digest for the next refresh;
  however, its statement about the full suite at its parent is contradicted by
  the isolated checkout described in R4-B1; and
- `git fsck --full --no-reflogs` is clean, the worktree was clean before this
  review artifact, and `HEAD`, `origin/main`, and `origin/HEAD` all named the
  reviewed 18-commit head.

R4-B1 is therefore an evidence-honesty failure, not a signature or hash
failure. The chain proves who signed the bytes and that current bindings match;
it does not make a false run attribution true.

## Hosted CI and environment parity

Hosted runs could not be inspected. `gh auth status` reported the active token
invalid, and `gh run list --json ...` failed before returning any run. No run
ID existed locally to pass to `gh run view --json jobs` or `--log-failed`.
Accordingly, the claimed green run, the matrix cells, artifact transfers,
network-none build, and aggregate `gate` context remain unverified rather than
accepted.

The four parity repairs have good local/static evidence:

- **Python 3.10 floor:** the workflow includes Ubuntu and Windows 3.10 cells;
  the lock records universal compilation at the 3.10 floor and now includes
  the missing conditional packages; the structural validator passes. Actual
  resolution and execution under 3.10 remain hosted-pending.
- **Subclassable socket guard:** `tests/conftest.py:36-45` leaves a real class
  for stdlib subclassing but blocks its initialization; importing `ssl`, the
  base and subclass guard self-tests, and the collection-timing sentinel pass.
- **Byte-exact checkout:** `.gitattributes` applies `* -text`; every tracked
  path currently has LF index/worktree bytes with `attr/-text`, and a scratch
  checkout configured with automatic conversion had no blob/worktree byte
  mismatch.
- **Encoding:** the compatibility tests explicitly write UTF-8, and the live
  scanner plus full suite pass under a forced ASCII locale. R4-m1 is an
  adjacent output-path case the repair missed.

Docker and a local Python 3.10 interpreter are unavailable on this host, so
the real pinned image, empty network namespace, cross-platform matrix, and
3.10 installation cannot be substituted locally.

## Local battery and direct probes

Run from the repository root unless stated otherwise:

```text
.venv/bin/python -m pytest -q
  215 passed, 4 skipped in 6.70s

.venv/bin/python -m ruff check .
  All checks passed

.venv/bin/python -m mypy src
  Success: no issues found in 3 source files

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/decontamination/verify_attestation.py
  signature, exact shape, scanner tree, manifest, headers, and counts verified

.venv/bin/python tools/offline_scan/scan_imports.py src
  3 Python files, 0 reported violations

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  both requirement files passed structural validation

private coverage_battery.py
  all five modes complete; 0 misses; 0 status failures;
  match-plus-violation status 3

private all_objects_scan.py
  112 blobs; 18 commits; 82 trees; 0 tags;
  0 matches; 0 violations

focused callback/duplicate/YAML/process/native/hook suite
  14 passed

full workflow parse
  valid mapping; 9 jobs
```

Additional direct probes covered both star-expansion forms, unknown
data-method arguments, unknown data-method receivers, three omitted callback
APIs, dynamic annotation evaluation, explicit versus directory-shaped YAML
exceptions, mutable-hook reachability through the actual runner, custom active
hook execution, forced-ASCII output, and exact historical reconstruction of
the signed run attribution.

## Acceptance-criterion status

| Criterion | Round-4 status |
| --- | --- |
| 1 — owner waiver and README record | **satisfied** |
| 2 — public governance settings | **pending owner visibility decision and hosted settings verification** |
| 3 — build, artifacts, smoke, egress | **pending hosted verification**; Docker is unavailable locally |
| 4 — empty runtime set and frozen closure | **satisfied structurally; hosted 3.10/build consumption pending** |
| 5 — decontamination and signed attestation | **not accepted**: cryptographic graph is consistent, but R4-B1 makes the bound run evidence non-reconstructible and contradicted |
| 6 — offline policy and mutations | **not accepted**: R2-B2 and R4-B2 leave callable and dynamic-evaluation routes green |
| 7 — provenance and all-object evidence | **not accepted**: R2-B7, R2-B11, and R4-B1 retain an artifact route, a false guard claim, and false/incomplete run attribution |
| 8 — documentation and residuals | **not accepted**: the manifest guard statement and A2 lifecycle wording are stale |

## What remains if hosted CI is green and the owner applies visibility and governance

**Phase 0 still cannot close on those two external conditions alone.** Even if
the latest hosted `gate` and every required settings/API check become green,
acceptance still requires exactly these repository/evidence repairs:

1. close R2-B2 across every supported Python version: complete or narrow the
   callback-capable API surface and remove or ratify the unknown-receiver
   method exception, with the direct missed-route and star regressions red;
2. close R4-B2 by rejecting dynamic annotation evaluation and auditing the
   other wholesale allowed-module APIs for equivalent capability;
3. close R2-B7 with explicit reviewed YAML configuration paths rather than a
   workflow-directory wildcard;
4. close R2-B11 by removing the last absolute guard claim and stating the
   reviewed-source/best-effort boundary consistently;
5. correct R4-B1 with signed, reconstructible run evidence, refresh every
   affected binding/signature in order, and produce the next non-self-bound
   post-commit record;
6. fix the R4-m1 ASCII-path diagnostic and the R4-m2 A2 lifecycle text;
7. rerun the full local/private battery, current-tree scan, all-object scan,
   strict attestation mutations, and this review-file scan on the final bytes;
   and
8. obtain the authorized round-5 code-review verdict over those repairs and
   the independently visible hosted/governance evidence before any tag,
   release, or Phase 1 work.

For the external side, the owner must make the visibility decision and, if
proceeding to public acceptance, apply and verify the D14 default-branch and
tag rulesets, exact app-bound `gate`, no bypass actors, force-push/deletion
blocks, workflow/fork permissions, two-factor/recovery controls, and private
reporting path. The latest repair head must then show a fully successful
hosted matrix, network-none build/egress mutation, artifacts and smoke, all
security jobs, sensitive-path job, and aggregate `gate`.

## What was checked

- Read the canonical reviewer/implementer briefs, the complete conditioned
  plan including both amendments, the round-3 review/response, all three new
  commits, and every changed implementation/test/document surface.
- Replayed every probe named by the round-4 protocol and chased adjacent APIs
  rather than stopping at the filed examples.
- Recomputed and signature-checked the public/private attestation graph,
  round-2 and round-3 post-commit records, freeze artifacts, scanner/snapshot
  trees, coverage behavior, current Git objects, and historical named heads.
- Inspected the hook under custom `core.hooksPath` and linked-worktree state,
  including actual active-hook execution.
- Parsed the workflow; checked action pins, gate dependencies, 3.10 lock
  markers, socket-guard subclassability, byte-exact attributes, encoding
  behavior, and the unavailable hosted/CLI state.
- Ran the complete test, lint, type, public-tool, private-coverage, all-object,
  focused mutation, Git-integrity, and review-artifact scan matrix. Phase 0
  contains no statistical generator, so numeric fidelity is not yet claimed
  or reviewable.

## Verdict

**Request changes.** R2-B2, R2-B7, and R2-B11 remain blockers in narrower
forms; R4-B1 and R4-B2 are new blockers. R2-B4, R3-B1's local syntax defect,
R3-M1, R3-m1, and R3-m2 are resolved. Hosted CI and governance remain pending
independent verification. Repair forward, rebuild the evidence chain around an
exact reproducible tree, and return for round 5, the final authorized code
review round.

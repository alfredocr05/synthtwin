# Phase 0 code review — round 5 (final authorized round)

**Reviewed:** the 21-commit Phase 0 history at
`0438ef8956f848e75e0f5f1dafa9653ad3300309`, the canonical briefs, all
646 lines of the conditioned plan and its ratified amendments, the round-4
review and response, the three repair commits, every changed public surface,
the current Git object graph, and the maintainer-private evidence chain
without reproducing protected values.

**Verdict:** **request changes** (option **c** in the round-5 protocol).

R2-B2 still has a blocker that is not expressible as a bounded edit. The new
scanner closes the filed spellings, but its claimed closed exact-dispatch
model is false at several distinct Python invocation boundaries, including a
route exercised by the current product. Adding another callback-table row
cannot close decorators, class construction, protocol dispatch, type
subclasses, and allowed-library calls that invoke methods on their arguments.
The policy needs a new, reviewable design or a materially narrower contract;
that is not an edit the implementer can apply mechanically without another
review.

R4-B1 also remains blocking acceptance evidence, although its repair *is*
bounded. The implementer handled the newly caught run-count error properly in
one respect: the corrected signed artifact carries the prior artifact's
digest, and the change is explicitly disclosed.
But the corrected note names an unavailable commit, and the separately bound
round-3 record still contains the earlier contradicted result. The new signed
round-4 record is sound evidence for the current head but does not supersede
those two defects.

**Hosted CI:** **not independently verified**. Repeated `gh` attempts failed:
the active CLI credential was reported invalid and run enumeration could not
connect to the API. The authenticated GitHub connector confirmed the private
remote, its 21-commit sequence, and the current head, but its available run
enumerator filters to pull-request events and therefore returned no push runs
for the requested commits. I could not recover run IDs for `83c9a4c`,
`f71d657`, or `0438ef8`. The supplied success claim is not treated as false,
but it remains unverified acceptance evidence. Static workflow inspection and
local checks do not substitute for the hosted jobs.

## Round-4 finding disposition

| Item | Round-5 status | Independently verified evidence |
| --- | --- | --- |
| **R2-B2** | **partially resolved — blocker remains** | The filed `sys.call_tracing`, assigned-variable `Path.walk(on_error=...)`, `make_dataclass(decorator=...)`, ungated parameter `.find`, scanned custom-object dispatch, and ordinary built-in-shadow mutations are red; the intended gated `.find` is green. But `Path(...).walk(on_error=callback)` in one expression is green and invokes the callback. A `str` subclass overriding `find` passes the new `isinstance` gate, scans green, and runs its override in current product code. A pattern capture can shadow `str` without being recorded, after which a gated custom-object dispatch is green. `json.load(reader)` and an unknown decorator also scan green and invoke caller-controlled methods/functions. |
| **R2-B7** | **resolved** | `KNOWN_CONFIG_YAML` contains exactly `.github/workflows/ci.yml`; direct predicates returned false for `.github/workflows/added-later.yaml`, a nested workflow path, and YAML elsewhere under `.github`. The focused new-file mutation is red, and the provenance checker passes the current tree. |
| **R2-B11** | **partially resolved — minor wording residue** | The manifest, checker, and runner now consistently describe a best-effort in-process guard, source review, and CI rather than confinement. The stale absolute claim is gone. However, the runner diagnostic and six test assertions still call it a `no-network fixture guard`, despite round 4's explicit instruction to align the remaining labels. |
| **R4-B1** | **partially resolved — blocker remains** | All relevant signatures and current digest bindings verify. The corrected pre-push note transparently supersedes the immediately prior note by its exact digest, and the digest equals the note binding committed at `f71d657`. Its `head_at_battery`, however, cannot be resolved locally or by the authenticated GitHub API. The attestation also binds the signed round-3 record whose 215-pass claim at `a01c13e` is contradicted by an isolated exact-tree run: 8 failed, 207 passed, 4 skipped. The signed round-4 record names reachable current head `0438ef8`, and its 224-pass/4-skip claim reproduced, but it neither cures the unavailable pre-push tree nor explicitly supersedes the false round-3 result. |
| **R4-B2** | **resolved** | `typing` is enumerated to `Protocol` and `cast`; `get_type_hints`, `ForwardRef`, `evaluate_forward_ref`, private evaluator access, and aliases are red. A harmless runtime probe reconfirmed that `get_type_hints` evaluates annotation text, while the repaired scanner rejects the source. |
| **R4-m1** | **resolved** | Every scanner diagnostic passes through an ASCII-safe emitter. The exact strict-ASCII writer plus non-ASCII violation-path mutation returns status 2, prints a value-silent `VIOLATION`, and escapes the path instead of raising. The full suite also passed under forced ASCII I/O. |
| **R4-m2** | **partially resolved — minor wording residue** | The A2 plan heading and status now say ratified and in effect. `SECURITY.md:258-259` still says the mechanism is being put to the current code-review cycle, so the second lifecycle edit ordered in rounds 3 and 4 was missed. |

## Blocking review items

### R2-B2 — Blocker remains — the exact-call-target policy is not a closed model

**Location:** `tools/offline_scan/scan_imports.py:73-200,376-466,1124-1148,`
`1528-1767,1826-1967`; `src/synthtwin/paths.py:74-93,238-243`;
conditioned plan `docs/plans/phase-0-public-skeleton.md:206-230`

**Defect:** the scanner calls its surface exhaustive, but it proves neither
exact receiver types nor every implicit call target, and several independent
source shapes execute caller-controlled code while reporting zero violations.

The named repairs themselves work in their filed shapes:

- `sys.call_tracing(callback, ())` is red;
- `base = Path(raw); base.walk(on_error=callback)` is red;
- `make_dataclass(..., decorator=callback)` is red even on an interpreter
  where that 3.14 parameter is not yet available at runtime;
- `typing.get_type_hints`, ungated `.find`, a scanned custom-object `.find`,
  and direct assignment shadowing are red; and
- a leading `isinstance(value, str)` gate makes the intended `.find` green.

Those controls have four independently reproduced defeats:

1. `isinstance(value, str)` admits subclasses. A neutral `str` subclass that
   overrides `find` scanned with zero violations and ran the override. The
   shipped `validate_local_path` accepted that subclass at line 238, reached
   `_url_scheme`, and dispatched the override at line 93 while the complete
   `src` scan remained green.
2. The built-in-shadow inventory omits structural-pattern binders. Capturing
   the built-in `object` under the name `str`, followed by the documented
   gate in a nested function, scanned with zero violations; the gate then
   accepted an arbitrary object and its custom `find` ran. The scanner has no
   binding treatment for `MatchAs`, `MatchStar`, or a mapping rest capture.
3. Callback checking depends on the receiver having a dotted name.
   `base = Path(raw); base.walk(on_error=callback)` is red, but the equivalent
   `Path(raw).walk(on_error=callback)` scanned with zero violations. A harmless
   missing-directory run invoked `on_error`.
4. The asserted external-API audit treats protocol-bearing arguments as data.
   `json.load(reader)` scanned with zero violations and invoked
   `reader.read`. A function parameter used as a decorator likewise scanned
   with zero violations and ran when the nested function was defined. Adjacent
   probes found the same class at path conversion, formatting, length,
   operator, class-base, and metaclass boundaries.

**Concrete failure scenario:** a caller passes a `str` subclass whose `find`
method starts a process or connection to `validate_local_path`. Both type
checks accept it; synthtwin calls the override; `scan_imports.py src` reports
zero violations. Separately, future allowed source can call `json.load` on a
caller-provided reader or apply a caller-provided decorator and receive the
same green result while the supplied object/function performs the forbidden
action.

This is not another missing slot. Python invokes user code through explicit
calls, decorators and class construction, descriptors, operators, iteration,
formatting, conversion protocols, and library methods on supplied objects.
The current checker models only selected `ast.Call` shapes and selected named
slots. A bounded patch for `Path.walk`, exact `type(value) is str`, and pattern
captures would leave the other demonstrated classes green.

Before Phase 0 can be ratified, replace this premise with one of two
reviewable designs: (1) a fail-closed invocation/type-provenance model that
enumerates and tests every source construct and allowed-library boundary that
can dispatch user code on all supported interpreters; or (2) a materially
narrower, ratified Phase 0 policy that permits only the exact source shapes and
proven-safe value origins the three current product modules need, rejecting
everything else. The choice, completeness argument, and mutations require a
new authorized review; they cannot be supplied as mechanical round-5
conditions.

### R4-B1 — Blocker remains — the signed chain still contains unreconstructible and contradicted run attribution

**Location:** maintainer-private
`out/pre-first-push-note.json:3-10`,
`out/post-commit-verification-r3.json:4-7`, and
`out/post-commit-verification-r4.json:4-11`;
`tools/decontamination/attestation.json:3-25`

**Defect:** the repair-forward disclosure is authentic, but it does not bind a
reconstructible pre-push tree or correct the older false record that the
current attestation deliberately binds.

The handling of the newly discovered error was appropriate as far as it went.
The current pre-push note is signed, its digest matches the current
attestation, and its `supersedes.note_sha256` exactly matches the pre-push-note
binding in the `f71d657` attestation. Its reason states what was mis-attributed,
what the actual run showed, and that the error was caught before review. This
is a transparent repair-forward record, not silent history rewriting.

It still fails the round-4 reconstructibility requirement. The named
`head_at_battery` object is absent from the local object database, `git fsck`
finds no recoverable copy, and the authenticated GitHub commit endpoint
returns `No commit found` for that SHA. None of the three reachable repair
trees proves what bytes that run used.

The current attestation's `post_commit_verification_sha256` also exactly binds
the signed round-3 record. That record says the full 215-pass/4-skip suite ran
at its parent `a01c13e`. An isolated archive of that exact commit reproduced
8 failures, 207 passes, and 4 skips: every failure came from the new verifier
requiring a binding absent from that commit's attestation. The newer correction
does not name this record or its digest as superseded.

The round-4 post-commit record is the sound part of the repair. Its signature
verifies, it names reachable current head `0438ef8`, the worktree bytes match
that head, and the recorded full-suite result reproduced. It is correctly not
self-bound; the declared protocol schedules it for the next refresh. But a
new good record does not silently null an older signed and currently bound
false one.

**Concrete failure scenario:** an auditor follows the attestation bindings to
the authoritative pre-push and round-3 records. One named tree cannot be
obtained; the other can be obtained but produces a red suite. The signatures
prove who signed the claims, not that the claims are reproducible, so the
auditor cannot accept criterion 5 or 7.

The bounded evidence repair for the next code state is: run the complete
battery in an isolated checkout at an exact reachable commit; replace and
sign the pre-push record with that SHA and actual outputs; explicitly
preserve the existing supersession and supersede by digest both the current
unreconstructible note and the contradicted round-3 result; refresh the
attestation and all affected bindings/signature in the declared order; then
issue the normal signed, non-self-bound post-commit record for the refresh
head. Do not relabel an old run as a different commit.

## Remaining bounded review items

### R2-B11 — Minor — one diagnostic still uses the withdrawn label

**Location:** `tools/provenance/guard_runner.py:44-46`;
`tests/test_provenance.py:751,945,973,1004,1036,1070`

**Defect:** the normative prose now says best-effort guard and not sandbox,
but the runtime diagnostic and its tests retain the exact `no-network fixture
guard` label round 4 ordered removed or aligned.

**Concrete failure scenario:** a maintainer sees only a rejected-generator
diagnostic in a CI excerpt and reads the name as a confinement property, even
though a deliberately hostile generator can bypass the in-process hook under
the documented residual.

Rename the diagnostic to `best-effort fixture guard` (or equally explicit
non-confinement wording) and update the six assertions. No implementation or
threat-model change is required.

### R4-m2 — Minor — SECURITY.md still presents ratified A2 as pending

**Location:** `SECURITY.md:250-260`

**Defect:** the plan now records A2's ratification, but the security policy
still says the sensitive-path mechanism is being put to the current review
cycle.

**Concrete failure scenario:** a contributor reads the security policy after
this final round and concludes that the warning/step-summary lifecycle is only
a proposal, while the ratified plan says it is operative.

Replace the parenthetical at lines 258-259 with: `This mechanism was ratified
by code-review round 3 as plan amendment A2 and is in effect.` Then rerun the
decontamination scan.

## Evidence-chain verification

The cryptographic mechanics are sound; the run semantics above are not:

- the public attestation and all four current private JSON records verify
  under the pinned identity and namespace;
- every publicly recomputable binding verifies; the private input digests,
  current pre-push note, bound round-3 record, and independently recomputed
  12-file snapshot tree match their attestation bindings;
- the private inventory and public manifest each contain 2,065 sorted unique
  entries and agree under per-entry hashing; their counts and matching
  parameters agree with the attestation;
- the public/private magic tables have the same 22 semantic rows; the public
  role header is intentionally different and is the byte artifact bound by
  the public verifier;
- the corrected pre-push note's supersession digest matches the prior binding
  at `f71d657`, and its new digest matches the current binding;
- the bound round-3 post-commit record's signature and digest match, but its
  historical suite claim fails exact reconstruction as described in R4-B1;
- the new round-4 post-commit record is signed, names current head, and its
  suite/tree/attestation claims reproduced; its digest is correctly scheduled
  for a later refresh rather than self-bound;
- the private coverage battery detected all 2,065 entries in every applicable
  mode, with zero misses and zero status failures, and rejected combined
  match-plus-violation status 3 as required; and
- the current all-object scan reports 127 blobs, 21 commits, 99 trees, zero
  tags, zero matches, and zero violations. `git fsck --full --no-reflogs` is
  clean, and local `HEAD`, `origin/main`, and `origin/HEAD` all name `0438ef8`.

## Hosted CI and environment evidence

Three independent routes were attempted:

1. `gh auth status` repeatedly reported the active credential invalid;
   `gh run list` then failed to reach `api.github.com`.
2. The authenticated GitHub connector confirmed repository metadata, private
   visibility, admin access, the exact 21-commit remote sequence, and remote
   head `0438ef8`. Its workflow-run wrapper explicitly filters to
   pull-request-triggered runs, so it returned empty sets for the push commits.
3. The only recoverable local run cache belongs to older commit `63f6c30`. Its
   container build and egress mutation were green, but the overall run and
   gate were red. It is not evidence for any requested head and was not used
   as such.

Static parsing found exactly nine workflow jobs — `lint`, `types`, `tests`,
`build`, `decontam`, `offline-static`, `provenance`, `sensitive-paths`, and
`gate` — and `gate` needs all other eight. The build definition uses a pinned
container with `--network none` and a separate egress mutation. Those facts
verify workflow bytes, not execution. The claimed successful runs for
`83c9a4c` and the two newer commits remain hosted-pending until their run IDs,
job graphs, conclusions, and relevant build logs are independently visible.

## Local battery and direct probes

Run from the repository root unless stated otherwise:

```text
.venv/bin/python -m pytest -q
  224 passed, 4 skipped in 6.99s

LC_ALL=C PYTHONIOENCODING=ascii .venv/bin/python -m pytest -q
  224 passed, 4 skipped in 7.02s

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
  match-plus-violation status 3 rejected

private all_objects_scan.py
  127 blobs; 21 commits; 99 trees; 0 tags;
  0 matches; 0 violations

named round-4 focused mutations
  10 passed

full workflow parse
  valid mapping; 9 jobs; gate needs all other 8

git fsck --full --no-reflogs
  clean
```

Direct scanner/runtime probes additionally covered the named callbacks,
dynamic annotation evaluation, assigned versus chained `Path.walk`, ungated
and gated `.find`, subclass dispatch, direct and pattern-capture shadowing,
custom-object dispatch, `json.load` reader dispatch, decorators, explicit YAML
paths, strict-ASCII output, current-product path handling, and exact historical
suite reconstruction. Harmless markers, never network or process actions,
demonstrated which runtime call targets executed.

## Acceptance status and closure conditions

| Criterion | Round-5 status |
| --- | --- |
| 1 — owner waiver and README record | **satisfied** |
| 2 — public governance settings | **pending owner action and API verification** |
| 3 — build, artifacts, smoke, egress | **not independently hosted-verified**; local smoke passes and workflow bytes are structurally valid |
| 4 — empty runtime set and frozen closure | **satisfied structurally**; final hosted consumption remains pending |
| 5 — decontamination and signed attestation | **not accepted** because R4-B1 leaves unreconstructible/contradicted run evidence |
| 6 — offline policy and mutations | **not accepted** because R2-B2 disproves the claimed closed exact-dispatch policy |
| 7 — provenance and all-object evidence | **not accepted** because R4-B1 remains; R2-B7 is resolved and the operative R2-B11 wording is honest |
| 8 — documentation and residuals | **not accepted** until the two bounded R2-B11/R4-m2 labels are corrected |

Because this verdict is **request changes**, Phase 0 does not close through
owner actions alone. A newly authorized review must first ratify a replacement
or narrowed offline-call policy and verify its implementation, the evidence
repair, the two bounded wording edits, and the complete final battery.

The exact Phase 0 items that remain behind the owner are:

1. change repository visibility from the currently verified **private** state
   to public and verify it through the repository API;
2. apply and API-verify the default-branch ruleset: PR-only, required context
   exactly `gate` bound to the GitHub Actions app, force-push and deletion
   blocked, no bypass actors, and self-merge only after that gate is green;
3. apply and API-verify the `v*` tag ruleset restricting creation, update, and
   deletion, with signed release tags and the signing-key record when releases
   begin;
4. API-verify repository Actions governance: default workflow token
   `contents: read` and the required fork-run approval setting (the absence of
   `pull_request_target` is already verified statically); and
5. confirm account 2FA, offline recovery-code custody, and no shared
   credentials.

After the code/evidence review is ratified and those owner items are verified,
Phase 0 closes only when a hosted run on the **exact final head** is
independently shown green for all nine jobs, including every test matrix cell,
the network-none build and egress mutation, artifact transfer/content checks,
fresh-venv smoke, every security job, sensitive-path surfacing, and aggregate
`gate`.

## What was checked

- Read the canonical reviewer and implementer briefs, complete conditioned
  plan with both amendments, round-4 review/response, three repair commits,
  and every changed source, test, document, attestation, and workflow surface.
- Replayed every probe named by the round-5 protocol and varied receiver and
  binding shapes instead of stopping at the new regression tests.
- Recomputed signatures, public and private bindings, snapshot digest,
  inventory/manifest correspondence, semantic magic rows, coverage behavior,
  current Git objects, and both reachable historical run claims.
- Checked explicit YAML routing, best-effort-guard wording, strict-ASCII path
  diagnostics, A2 lifecycle text, workflow structure, gate dependencies,
  action pins, repository synchronization, and Git integrity.
- Ran the full test, forced-ASCII, lint, type, public-tool, private-coverage,
  all-object, focused mutation, CLI smoke, workflow-parse, and review-artifact
  scan batteries. Phase 0 contains no statistical generator, so numeric
  fidelity is not yet claimed or reviewable.

## Final verdict

**Request changes.** R2-B2 remains a systemic exact-dispatch blocker whose
repair is not an exact bounded edit, so option (c) is required. R4-B1 also
remains blocking evidence acceptance; R2-B11 and R4-m2 retain two bounded text
residues. R2-B7, R4-B2, and R4-m1 are resolved. This final authorized cycle
ends without Phase 0 ratification.

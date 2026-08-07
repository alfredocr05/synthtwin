# Phase 0 closure review — round 2

**Reviewed baseline:** pushed 27-commit head
`f84404b1fa815b0d5b13a1a19986544831c725c4`, with local `main`,
`origin/main`, and the authenticated remote commit all agreeing; the complete
Phase 0 plan and acceptance criteria; closure-review round 1; the public tree;
and the maintainer-private evidence records, inspected value-silently.

**Verdict: request changes. Phase 0 remains open.** C1, C2, C5, and C6 are
resolved. C3 and C4 are partially resolved. The substantive implementation,
mutation batteries, and signed evidence chain pass, but two bounded closure
conditions remain: current text still describes a deferred branch ruleset as
active in two places, and the repository-level Actions settings assertion is
not independently auditable through the available interfaces or a durable
response artifact. Acceptance criteria 2 and 8 are therefore unsatisfied.

Phase 1 planning is not authorized by this verdict. The existing Phase 1 draft
is correctly double-gated and remains inert pending Phase 0 closure and its own
review cycle.

## Round-1 conditions C1–C6

| Item | Status | Independently verified basis |
| --- | --- | --- |
| C1 — A3 text propagation | **Resolved** | The plan now states what A3 supersedes, uses a scanner-specific premise, and carries the caller-supplied-code residual through D8 and criterion 8 (`phase-0-public-skeleton.md:361-379,677-744`). `SECURITY.md:31-45,66-78,105-116,201-208`, `README.md:47-51,69-83`, scanner prose, path-validator prose, diagnostics, and tests use the narrower best-effort contract. Executable-AST comparison against `61d9943` found no enforcement or mutation change after prose strings were normalized; all policy collections and mutation outcomes remain unchanged. |
| C2 — evidence-chain order | **Resolved** | All six retained private record signatures and the current public attestation signature verify under the pinned identity and namespace. A value-silent reconstruction passed all 28 digest/order checks: seven pre-push states, four post-commit states, the restored order-4 to order-5 link, the corrected round-3 supersession, the late round-4 binding, and the signed non-self-bound record for exact head `f84404b`. The records plus committed attestation history form the complete order without review prose. |
| C3 — private-mode governance claims | **Partially resolved** | README, SECURITY, and both canonical briefs now state the temporary private-mode exception; the authenticated repository metadata independently reports private visibility. `SECURITY.md:276-376` correctly separates active and deferred controls. However, the plan at `phase-0-public-skeleton.md:395-396` and workflow header at `.github/workflows/ci.yml:3-4` still say in present tense that the branch ruleset requires `gate`, contradicting `SECURITY.md:288-294` and the canonical reviewer brief's instruction that deferred controls must never be described as active. |
| C4 — settings/account evidence | **Partially resolved** | The plan and SECURITY now enumerate the eight branch/tag controls, defer fork approval with its recorded HTTP 422 reason, limit the dated account claim to 2FA, and expressly mark recovery-code and shared-credential practices unattested (`phase-0-public-skeleton.md:755-802`; `SECURITY.md:295-302,326-366`). The workflow itself declares `contents: read` and has no `pull_request_target`. But I could not independently read the repository-level `default_workflow_permissions` and `can_approve_pull_request_reviews` values: local `gh` has an invalid credential, the authenticated connector exposes repository visibility and jobs but not Actions settings, no browser session is available, and no durable settings-response artifact exists. |
| C5 — A2 lifecycle sentence | **Resolved** | `SECURITY.md:316-325` states in order that the mechanism was ratified by code-review round 3 as A2 and is in effect; the plan's A2 status is likewise ordered at `phase-0-public-skeleton.md:662-675`. The tree scan is clean. |
| C6 — parent briefs | **Resolved** | Both parent briefs are short, explicit non-instruction pointer stubs to `synthtwin/AGENTS.md` and `synthtwin/CLAUDE.md`. Both originals exist structurally under `planning-notes/retired-briefs/`, outside the repository. The private-notes path independently resolves outside the repository root. |

## Remaining review items

### R2-C1 — Major — two active-voice ruleset claims survived the private-mode repair

**Location:** `docs/plans/phase-0-public-skeleton.md:381-398` and
`.github/workflows/ci.yml:1-4`; contradictory authoritative status at
`SECURITY.md:278-294` and the owner-decision record at
`docs/plans/phase-0-public-skeleton.md:748-782`.

**Defect:** both locations say the branch ruleset “requires” the `gate`
context. No branch ruleset is applied while the repository is private. This is
not merely a future design statement: the present-tense wording describes the
deferred mechanical protection as being in force today.

**Concrete failure scenario:** a contributor reads the workflow header or D9,
believes a failing push cannot land on `main`, and relies on that protection.
The maintainer can in fact push directly, and a red commit is not mechanically
blocked after it lands.

**Bounded repair:** change both statements to future/deferred wording, with an
explicit pointer to the visibility-flip record, then rerun the tracked-tree
scan. No workflow behavior changes.

### R2-C2 — Major — current repository-level Actions settings are asserted but not independently evidenced

**Location:** `docs/plans/phase-0-public-skeleton.md:538-548,783-793` and
`SECURITY.md:295-302`.

**Defect:** the documents record a dated API readback of the two required
settings, but the response is not retained in a durable evidence artifact and
none of the currently working read-only interfaces exposes those fields. The
workflow's own `contents: read` declaration and a hosted log's effective
`Contents: read` output do not prove the repository default that a later
workflow would inherit.

**Concrete failure scenario:** a later workflow omits its permission block. If
the repository default is not actually read-only, the new workflow receives
broader authority even though the security policy tells an auditor the
repository default prevents that outcome.

**Bounded repair:** supply a reproducible read-only settings-API readback, or a
durable dated response artifact whose provenance and exact repository are
verifiable, establishing both required values. Re-read them again at the
visibility flip as already required. The dated owner 2FA confirmation remains
acceptable as owner evidence and needs no expansion.

## Enforcement and mutation verification

The round-2 text and evidence changes did not weaken the security controls.

```text
.venv/bin/python -m pytest -q
  224 passed, 4 skipped

LC_ALL=C PYTHONIOENCODING=ascii .venv/bin/python -m pytest -q
  224 passed, 4 skipped

.venv/bin/python -m ruff check .
  clean

.venv/bin/python -m mypy src
  clean (3 source files)

decontamination tree scan
  clean

signed-attestation verifier
  signature, exact schema, scanner tree, manifest, headers, and counts verified

offline source scanner
  3 files, 0 violations

provenance checker
  clean; manifest fixtures reproduce

supply-chain lock validator
  input and lock structurally valid
```

Focused batteries independently reproduced:

- decontamination and attestation: 72 passed;
- offline scanner, provenance, path, and socket suites: 114 passed, 4 Windows
  skips on this host;
- the private coverage battery detected every applicable entry in line,
  encoded-text, structured-cell, code-literal, and path modes, with zero misses
  or status failures;
- the all-object scan covered 147 blobs, 27 commits, 127 trees, and zero tags,
  with zero matches or violations;
- wrong signature identity, wrong namespace, and content tampering were red;
- git integrity was clean.

Direct scanner replay kept the four accepted A3 residual shapes green and
confirmed their harmless runtime markers dispatched. Disallowed import,
dynamic import, entry-point access, process launch, native access, reflective
lookup, untraced method dispatch, and unknown callback-slot probes remained
red. The committed 45-test offline scanner battery includes the two
split-string reflective mutations. URL, UNC, device-form, and mocked Windows
link tests remain red; the hosted Windows cells reported below cover the real
platform path.

An AST comparison from closure baseline `61d9943` to `f84404b` found the
product path validator and offline tests executable-structure identical after
normalizing documentation strings. The scanner likewise retained its policy
collections and decisions; only documentation and diagnostic strings changed.
The one later verifier change adds the reconciliation digest to the mandatory
attestation schema, which tightens rather than weakens verification.

## Signed evidence chain

The chain reads as one complete sequence from signed records and committed
attestation history alone:

1. The signed reconciliation lists six predecessor pre-push states in exact
   order. Every listed prefix resolves uniquely to the corresponding full
   binding in the named committed attestation.
2. Its fifth state explicitly supersedes the fourth, preserving the link that
   the prior current note omitted; its sixth explicitly supersedes the fifth.
3. The current signed pre-push note is the seventh state, supersedes the sixth
   by its full binding, and names the reconciliation record.
4. The reconciliation separately lists four post-commit states. The corrected
   third state explicitly supersedes the contradicted second state. The fourth
   is the true round-4 record whose promised next binding had been missed.
5. The current signed public attestation binds the seventh pre-push note, the
   reconciliation record, and that fourth post-commit record, and declares
   that order.
6. The new signed closure post-commit record names exact head `f84404b`, is not
   present in the attestation it follows, and declares binding at the next
   refresh. It therefore supplies the required non-self-bound terminal record.

All six retained private signatures verify under the pinned signer and
namespace. The current attestation's three relevant digests equal the exact
bytes of the records they name. The closure record's digest is absent from the
current binding set, as required. No private vocabulary or record value is
reproduced here.

## Hosted CI

The authenticated GitHub connector confirms exact head `f84404b` exists in the
private remote. It cannot establish an Actions result for that commit: its
commit-to-runs operation currently returns only pull-request-triggered runs and
there is none for this push; combined legacy statuses are empty. Local `gh`
still reports an invalid credential and then fails to reach the API, and no
authenticated browser session is available. **No green hosted-CI claim is made
for `f84404b`.** If a run exists, its status is unavailable through the current
interfaces.

The most recent run whose ID is independently retrievable remains run
`31215033942` at exact head
`61d99436658041062a3f6e8e39fa16aabbb0736e`. The job API returns all 19 jobs
completed successfully, including all eleven platform/version test cells,
build, four guard jobs, and aggregate `gate`. The fetched build log establishes
the exact checkout; read-only effective token; wheel-only hashed prefetch;
pinned-image verification and red image mutations; build with no network;
two-way executing-closure comparison; wheel/sdist allowlists; fresh guarded
install and CLI smoke; and both required failed egress attempts.

No workflow, build, packaging, lock, path, provenance, or decontamination
scanner surface changed between that hosted baseline and `f84404b`. The current
local battery covers the changed prose and the tightened attestation verifier.
Those unchanged surfaces support criterion 3, but the older run is not
presented as an exact-head hosted run.

## Acceptance-criteria walk

| Criterion | Status | Basis |
| --- | --- | --- |
| 1 — D2 waiver and README license record | **Satisfied** | The dated owner waiver remains in D2 and README records release on the owner's authority as non-commercial research tooling. |
| 2 — governance/settings/2FA | **Unsatisfied overall; nine controls deferred behind the visibility flip** | The repository is independently confirmed private; the exact eight branch/tag controls and fork approval are correctly enumerated as deferred with their recorded reasons; dated 2FA confirmation is correctly scoped. R2-C1 leaves two false active-voice claims, and R2-C2 leaves the two current repository settings without independently auditable evidence. |
| 3 — install, artifacts, smoke, closure, egress | **Satisfied** | Local import/CLI and the unchanged implementation pass. The independently fetched 19-job hosted baseline proves the network-unavailable build, checked artifacts, fresh guarded smoke, locked closure, and red egress mutations; no criterion-3 surface changed afterward. Exact-head hosted status is reported as unavailable, not inferred. |
| 4 — empty runtime set and frozen complete build lock | **Satisfied** | `dependencies = []`; structural lock validation passes; the unchanged hosted build consumed the lock and matched the executing closure in both directions. |
| 5 — decontamination and signed attestation | **Satisfied** | Current tree scan, full mutation battery, signature/schema/digest verification, private coverage, key-negative probes, and private-notes locality pass. C2's complete signed reconciliation is now bound. |
| 6 — offline policy and mutations | **Satisfied under A3's ratified narrower contract** | Current source scan is clean; retained red mutations, socket tests, local path tests, prior hosted Windows cells, and build egress all pass. AST and outcome comparison show no enforcement weakening. |
| 7 — provenance and pre-push/history evidence | **Satisfied** | Fixture regeneration and both required mutations pass; the all-object scan is clean; the signed seven-state pre-push sequence and four-state post-commit sequence are complete. |
| 8 — documents/residuals/canonical briefs | **Unsatisfied** | A3 scope/residual propagation, A2 wording, private-status text, named residuals, canonical briefs, and parent retirement are correct. R2-C1 leaves two current public statements inconsistent with the private-mode owner record and canonical brief. |

## Phase 1 draft boundary check

`docs/plans/phase-1-profiler.md:3-5` explicitly requires both Phase 0 closure
and its own adversarial ratification before any Phase 1 code. Commit `99c67c3`
added only that draft file; it changed no Phase 0 implementation, workflow,
contract, or documentation surface. This review makes no finding on the
draft's substance.

## What was checked

- Read both canonical briefs, all 802 lines of the current Phase 0 plan,
  closure-review round 1, every post-baseline public change, and the relevant
  current source, tests, workflow, and documents.
- Diffed executable scanner/product/test structure and policy collections;
  replayed accepted residuals and red mutation classes; ran the full normal and
  strict-ASCII local batteries.
- Signature-verified and digest-reconstructed the current and historical
  attestation/evidence sequence; ran negative signature probes, the private
  coverage battery, and the all-object scan value-silently.
- Parsed workflow topology, pins, permissions declaration, triggers, and secret
  references; checked the empty runtime dependency set, lock, import, CLI,
  repository synchronization, and git integrity.
- Queried authenticated remote repository metadata, current-head run/status
  interfaces, the most recent retrievable hosted job graph, and its build log;
  did not substitute an older run for the unavailable exact-head status.
- Checked README, SECURITY, owner records, canonical and parent brief topology,
  and only the double lock plus file boundary of the Phase 1 draft.

## Exact bounded work remaining

1. Reword the two active-voice ruleset assertions in D9 and the workflow header
   as deferred-until-public statements; rerun the tree scan.
2. Provide independently auditable evidence for the two current repository
   Actions settings, through a reproducible read-only query or a durable dated
   response artifact tied to this repository.
3. Push the bounded repair, provide the exact run ID if the connector still
   cannot discover push runs, and verify all 19 hosted jobs including `gate` on
   that exact head. Scan the new closure review and changed public files before
   finishing.

## Final verdict

**Request changes. Phase 0 is not closed.** The code, mutations, decontamination
controls, provenance controls, and signed evidence chain are closure-ready.
The remaining work is limited to two governance wording lines, durable/readable
settings evidence, and exact repaired-head hosted confirmation. Once those
bounded conditions verify, Phase 0 may close; until then Phase 1 planning and
implementation remain gated.

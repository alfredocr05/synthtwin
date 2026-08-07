# Phase 0 closure review — round 1 of the new authorized cycle

**Reviewed baseline:** the requested 24-commit pushed tree at
`61d99436658041062a3f6e8e39fa16aabbb0736e`; D6 Amendment A3 and the
owner-decision records; the complete Phase 0 plan and code-review round-5
ruling; the public implementation, tests, workflow, and documentation; and the
maintainer-private, value-silent evidence chain.

While this review was running, `main` and `origin/main` advanced to a 25th
commit, `99c67c38a4df683082c9543bf91a1c326def8dd5`, containing only a
double-gated Phase 1 draft. That commit is outside the requested closure
baseline, changes no Phase 0 implementation or contract surface, and does not
repair any review item below. It does expand the tracked corpus and Git object
graph and becomes the new pushed head; the separate post-move scans are
reported below.

**Verdict: request changes. Phase 0 remains open.** A3's substantive narrower
contract receives **ratify-with-conditions**: it is materially narrower
than the contract rejected in round 5, and the scanner itself was not weakened.
That resolves R2-B2 as a systemic implementation-design blocker. It does not
close Phase 0 because the narrower contract has not been propagated honestly
through the plan, security policy, scanner documentation, product documentation,
and tests; the signed evidence repair is incomplete; and private-mode governance
claims and evidence remain inconsistent. The requested authorization for Phase
1 planning is therefore not issued by this review.

## Rulings sought

| Requested ruling | Ruling |
| --- | --- |
| D6 Amendment A3 | **Ratify-with-conditions.** The best-effort, mutation-tested static layer plus the exactly named caller-supplied-code residual is a materially narrower contract. Every scanner rule and mutation remains. The public text-alignment conditions in C1 are mandatory before closure. |
| Round-5 bounded repairs | **Partly verified, not complete.** The resolvable-head battery, corrected round-3 record, and guard-label repair are sound. The post-refresh record/order is incomplete, and the prescribed A2 sentence was not applied. |
| Hosted CI | **Independently verified green for the requested head.** `gh` remains unusable, but the authenticated GitHub job API and build logs independently establish all 19 job cells green on the two cited runs and on exact baseline head `61d9943`. |
| Owner decisions | **Accepted in substance, incompletely propagated/evidenced.** The private-visibility override and dated 2FA confirmation are honestly scoped. Branch/tag rulesets may be deferred behind the visibility flip; other settings and account claims are not covered by that deferral. |
| Phase 0 acceptance | **Not closed.** Criteria 2, 5, 7, and 8 retain the bounded items listed below. |

## Review items

### C1 — Blocker — A3 narrows the contract, but the public contract still makes the disproved universal claim

**Location:** `docs/plans/phase-0-public-skeleton.md:206-220,354-372,548-551,648-679`;
`README.md:56-65,129-130`; `SECURITY.md:29-108`;
`tools/offline_scan/scan_imports.py:66-152,773-782`;
`src/synthtwin/paths.py:74-80,224-238`;
`tests/test_offline_scan.py:613-617,750-753,807-812`

**Defect:** A3 correctly calls the scanner best-effort and names
caller-supplied code as a residual, but (a) it says that residual is disclosed
in `SECURITY.md` when it is absent; (b) it does not expressly supersede D6.2's
still-normative statement that every call target resolves to an exact API; and
(c) scanner, product, diagnostic, and test prose still says directly or by
implication that an `isinstance` gate proves a plain built-in string and exact
method dispatch. A3's premise is
also overstated: the current scanner does not establish universal closure, but
a reading-only analysis can reject unresolved constructs, so universal
impossibility is not the accurate reason for choosing the narrower contract.

**Concrete failure scenario:** a caller passes a string subclass whose method
has a side effect to `validate_local_path`. The type gate accepts it, current
product code invokes the override, and the source scanner reports zero
violations. An auditor who follows README to `SECURITY.md` never sees the
accepted residual, while a contributor who reads the scanner, product, or test
documentation is still told that only the built-in method can run.

**Bounded repair:** keep every scanner rule and mutation unchanged; state in A3
which D6.2 universal sentences it supersedes; replace the overbroad
impossibility premise with a statement about what this scanner does not prove;
add the exact caller-supplied-code residual and best-effort/non-universal scope
to D8, acceptance criterion 8, and `SECURITY.md`; and align README's
offline-architecture text plus the cited scanner, product, diagnostic, and
test prose with that contract. Update A3's heading and status lines to record
this closure review's ratify-with-conditions ruling and, after these
mechanical conditions are applied, its operative status.

### C2 — Blocker — the round-5 evidence repair does not complete its declared signed order

**Location:** maintainer-private
`decontamination/out/pre-first-push-note.json:1-20`,
`post-commit-verification-r3.json:1-9`,
`post-commit-verification-r4.json:1-11`, and the `out/` record set;
public `tools/decontamination/attestation.json:1-29`;
`docs/plans/reviews/phase-0-code-review-round-5.md:168-175`

**Defect:** the new pre-push note is signed, bound, and reproducible at reachable
head `ac696ab`, and the corrected round-3 record is signed, bound, and explicitly
supersedes the contradicted record. The chain nevertheless omits three steps
required by round 5: the new note records only its immediate predecessor and
does not preserve that predecessor's earlier supersession; the signed round-4
post-commit record promised that its digest would be bound at the next refresh,
but refresh `f5bad96` instead binds the corrected round-3 record and neither
binds nor explicitly supersedes the round-4 record; and no signed,
non-self-bound post-commit record exists for the round-5 refresh head.

**Concrete failure scenario:** an auditor follows the current signed records
without relying on historical review prose. The trail drops an earlier
supersession, reaches a true record whose promised next binding never occurred,
and finds no post-commit verification record for the refresh that claims to
complete the repair. Signatures authenticate the fragments but do not form the
declared complete sequence.

**Bounded repair:** create a signed reconciliation record that preserves both
pre-push supersession links, binds or explicitly supersedes the round-4 record
by digest, and retains the corrected round-3 supersession; refresh the public
attestation and signature over that record and the corrected pre-push note in
the declared order; then issue the normal signed, non-self-bound post-commit
record naming and verifying the refresh commit. Do not relabel an earlier run.

### C3 — Blocker — private-mode governance is recorded in the plan but contradicted by current public status claims

**Location:** `docs/plans/phase-0-public-skeleton.md:683-691`;
`SECURITY.md:236-261`; `README.md:3-5,41-49,106-114`

**Defect:** the owner record honestly says the repository remains private and
the branch/tag rulesets are deferred until the visibility flip, while
`SECURITY.md` labels those same rulesets “Controls in force” and README calls
the current repository/project public and gives an unauthenticated clone flow.

**Concrete failure scenario:** a reader relies on PR-only changes,
force-push/deletion protection, and tag protection because the security policy
says they are active, although the owner record says they are not yet applied;
an unauthenticated reader following README cannot access the private repository.

**Bounded repair:** split `SECURITY.md` governance into controls active now and
controls deferred behind the visibility flip; make README and the canonical
briefs describe the temporary private-mode exception without weakening the
long-term open-source commitment; and keep the exact deferred controls listed
in the owner record and closure checklist.

### C4 — Major — the visibility deferral does not cover all unverified governance settings and account claims

**Location:** `docs/plans/phase-0-public-skeleton.md:500-510,521-522,683-695`;
`SECURITY.md:248-261`

**Defect:** the private-mode decision properly defers branch/tag rulesets and
their API verification, and the dated owner statement is acceptable owner
evidence for 2FA alone. It does not defer or verify the repository Actions
default-token setting or fork-run approval setting, and it does not attest the
separate recovery-code and no-shared-credential claims that `SECURITY.md`
presents as active.

**Concrete failure scenario:** the checked-in workflow itself requests only
`contents: read`, but a later workflow that omits the declaration inherits an
unverified repository default; separately, an auditor treats all three account
controls as owner-confirmed when the dated record confirms only one.

**Bounded repair:** provide settings/API evidence for the Actions default and
fork-run approval settings, or add an explicit owner deferral for them with an
exact activation point; separately record dated owner confirmation for the two
remaining account controls or narrow the current policy claim. Re-verify all
settings at the visibility flip.

The branch/tag items properly deferred behind the flip are exactly:

1. repository visibility and API confirmation;
2. default-branch PR-only enforcement;
3. required context exactly `gate`, bound to the GitHub Actions app;
4. force-push and deletion blocks;
5. no bypass actors;
6. self-merge only after a green gate;
7. `v*` creation, update, and deletion restrictions; and
8. signed release tags and the signing-key record when releases begin.

### C5 — Minor — the prescribed A2 lifecycle sentence was not applied

**Location:** `SECURITY.md:248-259`;
`docs/plans/reviews/phase-0-code-review-round-5.md:197-211`

**Defect:** the active guard label and all six active assertions now use the
honest best-effort label, but the A2 sentence says the mechanism “is put and
ratified” instead of the ordered statement that it was ratified by code-review
round 3 as A2 and is in effect.

**Concrete failure scenario:** a contributor reading the sentence cannot tell
whether “put” means proposed, submitted, or operative, preserving the lifecycle
ambiguity the bounded edit was meant to remove.

**Bounded repair:** apply the exact lifecycle sentence ordered at round 5 and
rerun the tree scan.

### C6 — Major — the parent-folder agent briefs are still operational, not retired

**Location:** parent-folder `AGENTS.md` and `CLAUDE.md`;
in-repo `AGENTS.md:3-7`, `CLAUDE.md:3-7`;
`docs/plans/phase-0-public-skeleton.md:67-73,548-551`

**Defect:** the in-repo briefs call themselves canonical and acceptance requires
the parent copies to be retired, but both parent files remain complete, live
instruction documents with legacy project context. They are still discovered
when an agent starts from the shared workspace root.

**Concrete failure scenario:** an agent launched one directory above the
repository follows the legacy name, phase structure, and private-reference
instructions instead of the canonical synthtwin rules, producing a review or
implementation against the wrong contract.

**Bounded repair:** replace each parent brief with a short retired pointer to
the corresponding in-repo canonical file, or otherwise make the parent files
non-governing while retaining any desired historical copy in private notes.

## Bounded round-5 repair verification

| Repair | Verification | Status |
| --- | --- | --- |
| Resolvable-head battery note | Signature verifies under the pinned identity and namespace; its digest equals the current attestation binding; `ac696ab` is reachable; an isolated exact-tree run reproduced 224 passed/4 skipped, clean lint/types/decontamination/offline/provenance/lock results; reachable-object counts reproduce 131 blobs, 22 commits, and 106 trees; the private coverage battery reports zero misses/status failures. | **Verified**, except the earlier supersession link was not preserved (C2). |
| Corrected round-3 record | Signature and current binding verify; its superseded digest equals the prior attestation binding. Exact historical reconstruction reproduced the stated pre-refresh failures and the green refresh-head suite, and hosted CI for `83c9a4c` is independently green. | **Verified.** |
| Round-5 post-commit record | No signed record naming the round-5 refresh exists; the round-4 forward-binding promise is also unfulfilled. | **Missing / unsatisfied** (C2). |
| Guard-label alignment | Active runner diagnostic and all six active assertions use `best-effort fixture guard`; obsolete wording remains only as historical review evidence. | **Verified.** |
| `SECURITY.md` A2 lifecycle line | Ratification is mentioned, but the exact ordered lifecycle statement is not present. | **Unsatisfied** (C5). |

## Hosted CI

`gh auth status` still reports the active credential invalid. The requested
`gh run list` and both requested `gh run view` calls each exited 1 while trying
to reach `api.github.com`; therefore no success claim is attributed to `gh`.

The authenticated GitHub connector independently supplied the missing hosted
evidence:

- run `31199671768` checked out exact head `f5bad966fa3a5fb98a53696dd3b43638b609e7ca`;
  all 19 jobs completed successfully, including build and aggregate gate;
- run `31193509891` checked out exact head `83c9a4c03d018a189eccf0f97cd736f13e2ad0ec`;
  all 19 jobs completed successfully, including build and aggregate gate; and
- run `31215033942` checked out exact requested closure head
  `61d99436658041062a3f6e8e39fa16aabbb0736e`; all 19 jobs completed
  successfully.

For the exact closure head, the connector job graph establishes every
platform/version test cell and the successful `gate`. The fetched build log
separately demonstrates the SHA-pinned checkout, pinned image verification,
wheel-only hash-checked prefetch, build inside `--network none`, both required
failed egress attempts, two-way executing-closure comparison, wheel/sdist
checks, fresh-venv install, and CLI smoke.

`planning-notes/ci-evidence-2026-08-07.json` matches the independently fetched
job names, conclusions, run IDs, and commit identities for both requested runs.
It is a JSON text sequence containing three top-level values rather than one
strict JSON document; stream-aware parsing succeeds. Its blank conclusion for
run `31215033942` records that run while it was still pending and is not a
contradiction of the subsequently fetched successful result.

**Hosted-CI status:** independently verified green for the exact requested
24-commit head. The later Phase 1 draft commit is outside this closure baseline.

## Owner-decision records

- **Private visibility:** accepted as an explicit owner override by the same
  audit mechanism as the earlier owner waiver. It is honest about the
  principle being deferred and is correctly limited to the branch/tag ruleset
  controls enumerated above. It does not silently defer unrelated settings.
- **2FA:** accepted as a dated owner attestation. The automation token does not
  expose the account setting, so this is not described as independent API
  verification; re-verification remains due at the visibility flip.
- **Limits:** the owner records do not make the false public-document claims or
  the unverified settings in C3-C4 acceptable. Those are separate bounded
  propagation/evidence repairs.

## Phase 0 acceptance — private-mode form

| Criterion | Status | Basis |
| --- | --- | --- |
| 1 — D2 waiver and README license record | **Satisfied** | The dated owner waiver is in the plan and README records release on the owner's authority as non-commercial research tooling. |
| 2 — governance/settings/2FA | **Unsatisfied overall; branch/tag subset deferred behind the flip** | Exact branch/tag controls are properly deferred; dated owner 2FA attestation is accepted. Actions/fork settings and the remaining account claims are neither verified nor deferred, and current security prose falsely calls deferred controls active. |
| 3 — install, artifacts, smoke, closure, egress | **Satisfied for the requested head** | Local import/CLI pass; connector-fetched run `31215033942` proves the exact `61d9943` build, artifacts, fresh-venv smoke, locked closure, network-none build, and red egress mutations. |
| 4 — empty runtime set and frozen complete build lock | **Satisfied** | Project metadata has no runtime dependencies; structural lock validation, hosted frozen installs, and closure comparison pass. |
| 5 — decontamination and signed attestation | **Unsatisfied for closure** | Scanner, full mutation battery, zero-exemption tree scan, signature, public/private digest bindings, inventory review binding, and private-notes locality pass. The declared signed post-refresh ordering remains incomplete under C2. |
| 6 — offline policy and mutations | **Satisfied behaviorally under A3's narrower contract** | Current source scan is clean; all mutation classes and socket/path tests pass across hosted cells; the scanner was not weakened. C1's public-contract alignment remains an acceptance-8 documentation blocker. |
| 7 — provenance and pre-push/history evidence | **Unsatisfied for closure** | Fixture/provenance mutations, reachable-head pre-push run, current all-object scan, and binding pass. C2 leaves the mandated repair-forward chain incomplete. |
| 8 — documents/residuals/canonical briefs | **Unsatisfied** | A3's residual is absent from `SECURITY.md`; private-mode governance/public-status text is false; A2 wording is not the ordered lifecycle text; and the parent briefs are not retired. |

## Local and private battery

Run against the requested 24-commit baseline unless noted:

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

attestation verification
  signature, exact schema, scanner tree, manifest, headers, and counts verified

offline-static source scan
  3 files, 0 violations

provenance checker
  clean

supply-chain lock validator
  input and lock structurally valid

private coverage battery
  2,065 entries; all applicable modes detected; 0 misses; 0 status failures;
  match-plus-violation status 3 correctly rejected

private all-object scan
  134 blobs; 24 commits; 112 trees; 0 tags; 0 matches; 0 violations

this review artifact in an isolated tracked-file scan tree
  clean

workflow parse
  9 job definitions; gate needs all other 8; global contents: read;
  no pull_request_target; all action references full-SHA pinned; no secret refs

git fsck --full --no-reflogs
  clean
```

After the concurrent 25th documentation-only commit, the tracked-tree scan,
provenance check, and all-object scan were repeated: all remained clean (135
blobs, 25 commits, 115 trees, zero tags/matches/violations).

Targeted A3 probes reconfirmed that four accepted residual shapes remain green:
a built-in subclass override, a caller-provided decorator, a protocol-bearing
reader passed to an allowed library API, and a callback passed through a call
chained onto a constructor. Harmless markers confirmed runtime dispatch, and
the shipped path validator exercised the subclass override. The focused
offline-scan suite passed all 45 tests. These results support A3's narrower
contract and disprove the stale exact-dispatch prose in C1.

## Exact bounded work remaining

1. Apply C1's A3 lifecycle/D6.2/D8/criterion-8, README, `SECURITY.md`, scanner,
   product, diagnostic, and test wording alignment without changing scanner
   behavior or removing mutations.
2. Repair the signed evidence chain in C2, refresh the attestation in declared
   order, and issue the missing signed post-refresh record.
3. Propagate the private-mode decision through README, `SECURITY.md`, and the
   canonical briefs, separating current controls from deferred controls.
4. Supply or explicitly defer the Actions/fork settings evidence; confirm or
   narrow the remaining account-control claims.
5. Apply the exact A2 lifecycle sentence ordered in round 5.
6. Retire the two parent-folder briefs operationally.
7. Re-run the full local/private battery, scan this review and every changed
   public file value-silently, push the bounded repair head, and independently
   verify all 19 hosted cells on that exact head.

## What was checked

- Read the canonical reviewer/implementer briefs, all 695 lines of the Phase 0
  plan, A1-A3, owner records, code-review round 5, and every post-round-5 public
  change.
- Diffed the scanner/tests from the round-5 head, replayed the four accepted A3
  residual classes, exercised current product dispatch, and checked adjacent
  plan/source/test claims.
- Recomputed and signature-verified the current attestation and all current
  private JSON records, their current/prior bindings, exact reachable heads,
  supersession links, inventory/manifest correspondence, and history counts.
- Reproduced the complete current battery and the repaired note's exact tree;
  checked workflow structure, action pins, token declaration, triggers,
  secrets, repository synchronization, and Git integrity.
- Retried `gh` as requested; independently fetched hosted job graphs and build
  logs through the authenticated GitHub connector; cross-checked the supplied
  evidence stream against those results.
- Checked the owner decisions against D3, D14, acceptance criterion 2, README,
  `SECURITY.md`, and the parent/canonical agent-brief topology.
- Phase 0 contains no statistical generation machinery, so no numeric-fidelity
  claim exists to diff against the private prototype in this review.

## Final verdict

**Request changes.** A3's core narrower contract receives
ratify-with-conditions, and R2-B2 no longer requires a scanner redesign. The
remaining work is bounded
to honest contract propagation, signed-chain completion, governance evidence
or explicit deferral, current-status documentation, the exact A2 sentence, and
parent-brief retirement. Phase 0 is **not closed** on this state.

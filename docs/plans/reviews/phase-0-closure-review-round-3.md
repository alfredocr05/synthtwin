# Phase 0 closure review — round 3

**Reviewed baseline:** pushed 29-commit head
`bdfac7d672f1bc2c51af0f86ffa8f2a20253c71c`, with `HEAD`, local `main`,
`origin/main`, and the authenticated remote commit agreeing; the complete
Phase 0 plan and acceptance criteria; closure-review round 2; every tracked
change after `f84404b`; the current public tree; and the relevant signed
maintainer-private evidence, inspected value-silently.

**Verdict: request changes. Phase 0 remains open.** R2-C2's requested
settings evidence is substantively supplied, and the two R2-C1 sentences
named in round 2 are repaired. The full sweep nevertheless found four other
current statements that still call the deferred gate required or enforced.
The evidence-chain replay also found that the newly bound predecessor record
was overwritten rather than retained, and the settings artifact retains an
unneeded temporary repository credential. Acceptance criteria 2, 5, and 8
are therefore unsatisfied. The remaining repairs are bounded and require no
product or workflow-behavior redesign.

Phase 1 planning may not begin under this verdict. The existing Phase 1
draft remains blocked by its recorded Phase 0-closure and independent-review
conditions.

## Rulings on R2-C1 and R2-C2

### R2-C1 — not resolved — four other active gate claims remain

The two named edits are correct:

- `docs/plans/phase-0-public-skeleton.md:393-400` says the future ruleset
  will require `gate` only once applied and is not in force while the
  repository is private.
- `.github/workflows/ci.yml:1-6` says the same and explicitly says that
  nothing currently blocks a push mechanically.

The D14 specification bullets at
`docs/plans/phase-0-public-skeleton.md:502-517` also retain their explicit
scope: they specify what will be applied, not what is active today. No
unqualified active fork-approval claim survives outside historical review
records.

The exhaustive tracked-tree sweep, however, found these operative claims:

- `CONTRIBUTING.md:82-86` calls `gate` an “aggregate required check”;
- `CHANGELOG.md:10-14` calls it an “aggregate required gate”;
- `tools/hooks/install.sh:26-29` says the public CI gate “remains the
  enforced check”; and
- `.github/workflows/ci.yml:959-962` calls it “the one required status
  context.” The file-header disclaimer mitigates this last instance, but
  the local statement still fails the requested no-active-claim sweep.

**R3-C1 — Major.** A contributor can read any of the first three files,
reasonably conclude that GitHub mechanically refuses a red change, and rely
on that protection. In private mode the maintainer can direct-push; a failed
run occurs only after the commit is already on `main`.

**Bounded repair:** call `gate` the aggregate job or context in all four
places. Where enforcement is discussed, say that the public-mode ruleset
will require it after the visibility flip and that no private-mode push is
mechanically blocked. Historical review records need no rewrite. Rerun the
tracked-tree scan.

### R2-C2 — evidence requirement satisfied; live re-read unavailable

The signed private settings artifact satisfies round 2's core requirement
for a durable, dated response record tied to the exact repository:

- its signature verifies under the pinned signer identity and namespace;
- its byte digest equals the new mandatory
  `settings_readback_sha256` binding at
  `tools/decontamination/attestation.json:22`;
- the exact endpoint URLs and five per-call sets of HTTP status, GitHub
  `Date`, `Server`, and request-identifier headers are retained;
- the repository identity records the expected full name, stable repository
  identifiers, private visibility, and default branch;
- the workflow-permission response retains
  `default_workflow_permissions = read` and
  `can_approve_pull_request_reviews = false`; and
- the fork-approval and ruleset responses retain the expected private-tier
  refusal status and body. Four exact read-only `gh api ... --include`
  commands reproduce the settings calls.

The authenticated repository connector independently corroborated the exact
repository, numeric repository identity, private visibility, default branch,
and pushed head. It does not expose the settings endpoints. Local `gh`
authentication is invalid, and no signed-in browser is available, so I could
not independently re-read the two settings values live. No live-corroboration
claim is made. That access limitation does not defeat the signed durable
artifact within D14's stated dishonest-maintainer residual.

There are two new artifact-hygiene issues, recorded separately as R3-C3
below. They do not negate the provenance evidence above, but the artifact
must not remain in its present over-retentive form.

## New closure items

### R3-C2 — Major — the bound predecessor record is dangling

The valid current attestation declares this order: current pre-push note,
evidence reconciliation, settings readback, then previous post-commit
record. The first three digests exactly match retained signed private files.
The fourth does not: the bound `post_commit_verification_sha256` digest at
`tools/decontamination/attestation.json:15` matches none of the four retained
post-commit JSON records and appears nowhere in the workspace except the
public attestation.

The cause is bounded and concrete. The round-2 terminal record for exact head
`f84404b` used `out/post-commit-verification-closure.json`; that path and its
signature were then overwritten by the new terminal record for `bdfac7d`.
The current file is validly signed and names exact head `bdfac7d`, but it is a
different byte sequence. The predecessor's bytes and original signature are
no longer available for independent verification.

**Failure scenario:** an auditor starts with the current repository and
private evidence bundle, computes every declared digest, and reaches the
post-commit binding. No retained file opens that commitment, so the auditor
cannot verify the predecessor's covered head, recorded results, or signature
without relying on review prose. The round-2 standard — records plus committed
attestation history reconstruct the sequence — has regressed.

The rest of the chain is sound:

- all relevant historical committed attestations verify under their pinned
  signer and namespace;
- the reconciliation's six earlier pre-push prefixes and four earlier
  post-commit prefixes resolve in exact declared order against committed
  attestation bindings, including the preserved order-4 to order-5 link and
  the corrected round-3 link;
- the current signed pre-push note covers exact parent `1971bd5`, supersedes
  the note bound at `f84404b` by its full digest, and is bound at `bdfac7d`;
- the new signed terminal record covers exact head `bdfac7d`; its digest is
  absent from the current attestation as required; and
- no retained private JSON and no committed attestation contains its own
  digest. No self-binding was found.

**Bounded repair:** restore the exact `f84404b` terminal bytes and original
signature under an immutable, head-qualified filename. If recovery is
impossible, create and ratify an honest signed loss/reconciliation replacement
that independently re-verifies that exact head, then bind it in a fresh
attestation. Retain the `bdfac7d` record under its own immutable filename
before the refresh, and add a maintainer-side check that every bound private
digest resolves to exactly one retained artifact. The next refresh again
ends with a new signed, non-self-bound terminal record.

### R3-C3 — Major — the private settings artifact over-retains a credential

The repository-identity response was retained wholesale even though R2-C2
needs only stable identity fields. It includes a non-null temporary clone
credential unrelated to the evidence claim, in a long-lived synced artifact
with ordinary read permissions. This review does not reproduce that value.
The artifact also contains five API readbacks but records exact commands for
only four; the omitted command is the base repository-identity call. Thus the
plan and `SECURITY.md` overstate that every retained call is reproduced by a
command recorded inside the artifact.

**Failure scenario:** the private evidence folder is read or synchronized to
an unintended local account while the temporary credential is valid. The
reader can potentially clone the still-private repository even though the
evidence requirement never needed that credential. Separately, an auditor
following only the recorded commands cannot reproduce the stable node
identity call exactly.

**Bounded repair:** revoke the credential if it can still be active; replace
the record with a minimized, signed readback that retains only the required
repository identity fields, response provenance, and the verbatim governance
endpoint bodies; record the exact identity command as well. Bind the sanitized
record during the same fresh attestation cycle as R3-C2 and retain only a
digest plus an honest sanitization/loss note for the credential-bearing
version.

## Enforcement and mutation verification

No enforcement weakened between `f84404b` and `bdfac7d`. The changed tracked
surfaces are governance prose/comments, the signed attestation, and one
attestation-verifier schema tuple. The verifier change only adds
`settings_readback_sha256` to the mandatory binding set. It removes no check.
After comments and blank lines are removed, the workflow is byte-identical to
the closure baseline. Executable AST comparison also leaves the product path
validator, offline scanner, and mutation tests unchanged.

The complete local battery passed:

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

Focused batteries independently reproduced 72 decontamination/attestation
passes; 115 offline, provenance, path, and socket passes with four genuine
Windows-only skips on this host; and 34 supply-chain-validator passes. The
private coverage battery detected every applicable entry in line, encoded
text, structured-cell, code-literal, and path modes with zero misses or status
failures. The all-object scan covered 154 blobs, 29 commits, 136 trees, and
zero tags with zero matches and zero violations. Git integrity and diff
whitespace checks were clean.

Accordingly, disallowed imports, dynamic loading, entry-point access, process
launch, native access, reflective lookups, URL/UNC/device inputs, mocked
Windows link traversal, signature and schema tampering, unlisted/substituted
fixtures, forbidden lock inputs, and the private match-plus-violation probe
remain red for the intended reasons. The earlier hosted Windows cells remain
the real-platform complement to the four local skips.

## Hosted CI

The authenticated connector confirms the exact private remote head
`bdfac7d`. Its commit-to-runs operation exposes pull-request-triggered runs
only and returns none for this push; combined legacy statuses are empty.
Local `gh` has an invalid credential, and the browser runtime has no available
signed-in browser. **No exact-head hosted-green claim is made.**

The most recent run independently retrievable through the working interface
remains Actions run `31215033942`, at exact checkout
`61d99436658041062a3f6e8e39fa16aabbb0736e`. Its job API reports all 19 jobs
completed successfully: build, lint, types, four guard/surfacing jobs, all 11
platform/version test cells, and aggregate `gate`. The fetched build log
confirms the exact checkout, effective read-only token, wheel-only hashed
prefetch, red source/image mutations, pinned-image check, network-none build,
two-way executing-closure comparison, artifact allowlists, guarded fresh
install and CLI smoke, and both failed egress attempts.

No workflow behavior, build, packaging, lock, path, provenance, or
decontamination-scanner surface changed after that hosted baseline. The
current local battery covers the changed prose and tighter attestation schema.
The older run is evidence for those unchanged surfaces, not an exact-head run.
Under the round-3 instruction to report the most recent *available* run
honestly, interface unavailability adds no separate closure condition.

## Acceptance-criteria walk

| Criterion | Status | Independently verified basis |
| --- | --- | --- |
| 1 — D2 waiver and README license record | **Satisfied** | The dated owner waiver remains at `phase-0-public-skeleton.md:41-63`; README records release on the owner's authority at `README.md:141-148`. |
| 2 — governance/settings/2FA | **Unsatisfied overall; nine controls properly deferred behind the visibility flip** | The two active settings have signed durable evidence and the 2FA claim is correctly limited to owner confirmation. `SECURITY.md:340-370` and the plan owner record enumerate exactly the eight ruleset controls plus fork approval as deferred. R3-C1 leaves four contradictory required/enforced-gate claims. |
| 3 — install, artifacts, smoke, closure, egress | **Satisfied** | Current local import/CLI tests pass. The unchanged 19-job hosted baseline proves the no-network build, checked wheel/sdist, guarded fresh smoke, locked executing closure, image/source mutations, and failed egress attempts. Exact-head hosted status is reported unavailable, not inferred. |
| 4 — empty runtime set and frozen complete build lock | **Satisfied** | `pyproject.toml:17-19` has an empty runtime set; structural lock validation passes; frozen CI consumption and the hosted executing-closure comparison pass. |
| 5 — decontamination and signed attestation | **Unsatisfied overall** | Scanner, manifest, decoder, coverage battery, current public signature/schema, public digests, and key-negative mutations all pass. R3-C2 leaves one private attestation binding without its committed bytes/signature, so the reviewer-accessible binding graph is not end-to-end recomputable. R3-C3 requires a sanitized settings binding. |
| 6 — offline policy and mutations | **Satisfied under A3's narrower contract** | Source scan is clean; exact allowlist, retained red mutations, socket timing/self-test, local path tests, prior hosted Windows cells, and build egress evidence pass. No enforcement changed. |
| 7 — provenance and pre-push/history evidence | **Satisfied as written** | Fixture regeneration and both mutations pass; the 29-commit all-object scan and git integrity pass; the pre-first-push lineage reconstructs from signed committed attestations. R3-C2 is the later closure-record regression and is accounted for under criterion 5. |
| 8 — documents/residuals/canonical briefs | **Unsatisfied** | Named residuals, A3 scope, A2 lifecycle, private-status sections, canonical briefs, parent retirement, and notes locality are correct. R3-C1 leaves four current governance overclaims; R3-C3 leaves the reproduction-command claim too broad. |

## What was checked

- Read both canonical briefs, all 811 lines of the current Phase 0 plan,
  closure-review round 2, the complete repair diff, and every acceptance
  criterion.
- Swept all tracked current text for branch, tag, fork, gate, required-check,
  and enforcement claims; separated operative documents from historical
  review items and future specifications.
- Signature-verified the current attestation and every relevant committed
  attestation state; verified all seven retained private signatures; rebuilt
  reconciliation prefixes/order and every current private digest binding;
  searched the workspace for the dangling predecessor; checked self-binding
  negatively.
- Inspected the settings record's exact repository identity, endpoint/body
  structure, response provenance, command list, file permissions, signature,
  digest binding, and credential-bearing fields without reproducing private
  values.
- Ran both full test modes, lint, strict types, all public guards, lock check,
  focused mutation groups, private coverage, all-object history scan, git
  integrity, and whitespace checks; compared executable policy surfaces to
  the earlier closure baseline.
- Queried authenticated remote metadata, exact-head run/status interfaces,
  the most recent retrievable hosted job graph, and its build log; did not
  substitute an older run for unavailable exact-head status.
- Walked acceptance criteria 1–8 and checked the Phase 1 draft boundary only;
  this review makes no finding on that draft's substance.

## Exact bounded work remaining

1. Normalize the four remaining required/enforced-gate descriptions to the
   private-mode truth and rerun the tracked-tree scan (R3-C1).
2. Restore or honestly replace the missing `f84404b` terminal record, retain
   head-qualified immutable evidence filenames, and add a bound-artifact
   existence/uniqueness check (R3-C2).
3. Revoke or confirm expiry of the unnecessarily retained temporary
   credential; create a minimized settings record with all five exact
   reproduction commands; sign and bind it, recording the sanitization
   without retaining credential bytes (R3-C3).
4. Refresh the pre-push note, reconciliation as needed, private coverage,
   public attestation, and signatures in declared order; then create a new
   signed exact-head terminal record whose digest is absent from that
   attestation. Scan every changed public file and the next review.

## Final verdict

**Request changes. Phase 0 is not closed.** R2-C2's evidentiary requirement
is met and enforcement remains intact, but R3-C1, R3-C2, and R3-C3 are bounded
closure blockers. Phase 1 planning may not begin until they are repaired and
independently verified.

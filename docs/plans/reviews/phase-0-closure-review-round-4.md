# Phase 0 closure review — round 4

**Reviewed baseline:** pushed 31-commit head
`078abf8ea8dd657c1f4e24fd284c4d9a0205087f`, with `HEAD`, local `main`,
`origin/main`, `origin/HEAD`, and the authenticated remote commit agreeing;
the complete conditioned Phase 0 plan and all eight acceptance criteria;
closure-review round 3; both commits after `bdfac7d`; the current tracked
tree; and the relevant signed maintainer-private evidence, inspected
value-silently.

**Verdict: request changes. Phase 0 remains open.** The credential-bearing
record is gone, its minimized replacement is sound, and the signed disclosure
closes the irrecoverable predecessor loss without fabricating bytes. The
current attestation graph has no missing binding, and all enforcement and
mutation batteries remain green/red as intended. The fresh tracked-tree sweep,
however, found the same active-enforcement overclaim three more times in tool
documentation. Round 3's promised maintainer-side binding resolver is absent
and the predecessor payload still has two retained path aliases. The canonical
plan also points to the deleted settings artifact and calls the evidence a full
rather than minimized readback. Acceptance criteria 2, 5, and 8 are therefore
not closed.

Phase 1 planning may not begin under this verdict. The three repairs below are
bounded text/evidence-hygiene work; no product or CI-behavior redesign is
required.

## Rulings on the requested items

### R2-C1 / R3-C1 — not fully resolved — three operative survivors

The four named repairs are correct:

- `CONTRIBUTING.md:82-90` calls `gate` the aggregate check and standing
  rule, expressly not a mechanically enforced context until the visibility
  flip.
- `CHANGELOG.md:10-15` says it is not yet a mechanically required context.
- `tools/hooks/install.sh:25-30` calls the hook advisory and the private-mode
  gate a standing rather than mechanically enforced rule.
- `.github/workflows/ci.yml:959-964` calls `gate` the aggregate context and
  scopes required-context status to the future ruleset.

The other obvious governance surfaces are also accurate. The workflow header
says nothing currently blocks a push mechanically; `SECURITY.md:276-294`
states that direct pushes reach the default branch; `SECURITY.md:340-370`
puts all eight branch/tag controls and fork approval outside current force;
and README, both canonical briefs, D9, D14, acceptance criterion 2, and the
owner-decision record distinguish the standing rule from future enforcement.
Internal workflow references to “required” upstream jobs describe the
aggregate job's own `needs`, not a required GitHub status context.

A wider tracked-current-tree sweep nevertheless found this statement three
times:

- `tools/provenance/check_provenance.py:53`;
- `tools/provenance/check_provenance.py:439-440`; and
- `tools/provenance/guard_runner.py:31-33`.

Each says that CI is the enforced boundary. The surrounding prose presents it
as a repository control that actually holds, not merely as a checker that
returns nonzero once invoked. That contradicts the accurate private-mode
description in `SECURITY.md`.

**R4-C1 — Major. Failure scenario:** the maintainer directly pushes a change
containing a prohibited fixture generator. The commit reaches `main`; the
provenance job reports red only afterward. A contributor reading either tool
module can instead conclude that CI mechanically stopped the change at the
repository boundary, the same mistaken reliance R3-C1 was meant to remove.

**Bounded repair:** in all three occurrences, call CI the authoritative check
or standing rule and say that a private-mode push is not mechanically blocked.
Repeat the sweep across all tracked current text, including tool docstrings,
not only governance and contributor documents. Historical review records need
no rewrite.

### R3-C2 — the disclosed loss is closed; the promised resolver is not

The signed hygiene record handles the irrecoverable record honestly:

- its signature verifies under the pinned principal and namespace, and its
  digest equals the current mandatory `evidence_hygiene_sha256` binding;
- the disclosed lost digest is the authoritative digest committed in the
  predecessor attestation, not the padded value from the discarded draft;
- it names the overwrite cause, the information class the lost record carried,
  why its exact duration-bearing bytes cannot be reconstructed, and the
  immutable `post-commit-<head12>.json` rule;
- the missing payload has zero retained byte matches, exactly as disclosed;
  no reconstruction is presented as original evidence; and
- the current predecessor payload covers exact head `bdfac7d` and is retained
  under the correct immutable head-qualified name with a valid signature.

The digest-correction disclosure is acceptable. The current signed record uses
the authoritative committed digest, the incorrect draft is neither current nor
bound, and the correction is not hidden. Under the requested proportionality
rule, the historical loss itself is a closed, honestly bounded item.

The complete replay also establishes that no **current** binding dangles:

- all ten committed attestation versions verify under the pinned signer;
  replaying the verifier from each archived commit tree passed;
- all ten retained private signature/file pairs verify, representing nine
  unique payloads because one predecessor pair is duplicated byte-for-byte;
- all 20 current file-backed binding keys match their designated retained
  files, while the public scanner-tree digest and the 12-file private snapshot
  tree recompute exactly;
- reconciliation prefixes resolve in order and without collision against the
  committed attestation history;
- the current pre-push note covers exact parent `41982f7`, supersedes the prior
  bound note by full digest, and is itself bound at `078abf8`;
- the new terminal record is
  `out/post-commit-078abf8ea8dd.json`, covers exact `HEAD`, has a valid
  signature, and its digest is absent from the attestation it follows; and
- none of the 21 retained private JSON payloads contains its own digest.

There is one necessary historical exception to the phrase “every bound digest
matches a retained file”: the predecessor attestation still contains the
irrecoverable digest it committed. The signed hygiene record cannot make those
bytes reappear; it makes the exception explicit and is now itself retained and
bound. Thus there is no unexplained or current dangling commitment, but this
review does not falsely claim that the historical commitment can be opened.

One part of R3-C2's bounded repair was not implemented. Round 3 required a
maintainer-side check that each bound private digest resolves to exactly one
retained artifact. No such checker exists; the public verifier cannot inspect
private evidence. In addition, the currently bound predecessor payload and
signature remain at both the immutable path
`post-commit-bdfac7d672f1.json` and the reusable legacy path
`post-commit-verification-closure.json`. The two pairs are byte-identical and
both signatures verify, so this creates no present content ambiguity, but the
literal uniqueness invariant is false.

**R4-C2 — Major. Failure scenario:** a future refresh again overwrites or omits
the intended predecessor file. The signed naming rule says that should not
happen, but no executable maintainer-side check proves existence, canonical
path, uniqueness, and signature before the new attestation is signed. The next
auditor can rediscover another missing predecessor only after it has entered the
committed chain.

**Bounded repair:** add and run the promised private binding resolver. It must
map each private evidence binding to one declared retained path, verify bytes
and signature where applicable, and reject a missing or ambiguous current
record. Either remove the redundant legacy alias or explicitly ratify and
enforce one canonical immutable path while proving any archival alias is
byte/signature-identical and ineligible for resolution; do not leave the
exception implicit.

### R3-C3 — credential removal resolved; the canonical evidence path is stale

The sensitive artifact repair is substantively correct:

- the credential-bearing JSON and its signature are absent from the workspace
  and were never tracked;
- `settings-readback-v2.json` and its signature verify, and the exact byte
  digest equals the current `settings_readback_sha256` binding;
- the repository identity appears only as the six permitted fields: full name,
  stable numeric and node identifiers, visibility, private flag, and default
  branch;
- five endpoint readbacks each retain status/date/server/request provenance;
  the governance bodies are retained while the identity body is minimized;
- the record contains five distinct reproduction commands, exactly equal to
  the five per-readback commands, including the repository-identity call; and
- field-name, authorization-header, URL-userinfo, and recognizable-token
  probes found no retained credential or credential value.

The hygiene record's superseded digest equals the authoritative
`settings_readback_sha256` value in the committed `bdfac7d` attestation. It
also records deletion, minimization, the non-public/non-committed short-lived
credential residual, and the offered but unperformed host-credential refresh.
That is a named, bounded, control-assigned residual rather than an undisclosed
credential defect. The invented-digest correction is accepted for the same
reason as above: the current record is correct and the mistake is disclosed
rather than allowed to stand.

The operative plan is now wrong at
`docs/plans/phase-0-public-skeleton.md:795-802`. It promises a “full API
readback” at `decontamination/out/settings-readback.json`; that path was
deliberately deleted, and the retained evidence is the minimized
`decontamination/out/settings-readback-v2.json`. `SECURITY.md` uses a generic
description and remains accurate.

**R4-C3 — Minor, but closure-blocking under acceptance criterion 8. Failure
scenario:** an auditor follows the canonical plan to reproduce the active
settings evidence and lands on a nonexistent path, then reasonably concludes
that the promised durable record was lost or that the credential-bearing full
response still exists elsewhere.

**Bounded repair:** change the plan's owner-decision record to name the v2 path
and describe the evidence as minimized: six repository-identity fields,
per-call provenance, and verbatim governance bodies. Keep the five-command
claim.

## Enforcement, local battery, and mutations

No enforcement weakened from either `f84404b` or `bdfac7d` to `078abf8`.
Product source, tests, the offline scanner, provenance behavior, lock
validator, requirements, and packaging are unchanged. After comments and
blank lines are removed, the workflow is byte-identical to `bdfac7d`; the
hook's executable text is unchanged. The only verifier behavior change adds
`evidence_hygiene_sha256` to the mandatory exact schema. It removes no check.
All 15 action steps remain pinned to full 40-hex commit IDs, the workflow keeps
top-level `contents: read`, and it has neither `pull_request_target` nor a
secret reference.

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

Focused batteries reproduced 72 decontamination/attestation passes; 115
offline, provenance, path, socket, and timing passes with four genuine
Windows-only reparse skips; and 34 supply-chain-validator passes. The private
coverage battery detected every applicable entry in line, encoded-text,
structured-cell, code-literal, and path modes with zero misses or status
failures. The all-object scan covered 162 blobs, 31 commits, 147 trees, and
zero tags with zero matches or violations. `git fsck --full --strict`, diff
whitespace, and the pre-review worktree state were clean.

Accordingly, disallowed imports, dynamic loading, entry-point access, process
and native calls, reflective lookups, URL/UNC/device inputs, mocked Windows
link traversal, signature/schema tampering, fixture substitution, forbidden
lock inputs, and the private match-plus-violation probe remain red for the
intended reasons. The earlier hosted Windows cells remain the real-platform
complement to the four local skips.

## Hosted CI

The authenticated repository interface confirms the exact private remote and
pushed head `078abf8`. Its commit-to-runs operation exposes pull-request runs
and returns none for this push; combined legacy statuses are empty. Local `gh`
authentication is invalid and cannot query Actions, and browser discovery
found no signed-in session. **No exact-head hosted-green claim is made, and the
available interfaces cannot prove that no newer push run exists.**

The most recent run independently retrievable through a working interface
remains Actions run `31215033942`, at exact checkout
`61d99436658041062a3f6e8e39fa16aabbb0736e`. Its current job response reports
all 19 jobs successful: build, lint, types, four guard/surfacing jobs, all 11
platform/version test cells, and aggregate `gate`. Its build log confirms the
exact checkout, read-only token, wheel-only hashed acquisition, source/image
mutations, pinned image, network-none build, executing-closure comparison,
artifact allowlists, guarded fresh install and smoke, and both failed egress
attempts.

No workflow, build, packaging, lock, product path, provenance, or scanner
behavior changed after that hosted baseline. The old run is evidence for those
unchanged surfaces, not an exact-head result.

## Acceptance-criteria walk

| Criterion | Status | Independently verified basis |
| --- | --- | --- |
| 1 — D2 waiver and README license record | **Satisfied** | The dated owner waiver remains in D2; README records release on the owner's authority as non-commercial research tooling. |
| 2 — governance/settings/2FA | **Unsatisfied overall; nine controls properly deferred behind the visibility flip** | The signed minimized evidence establishes both active Actions values; the 2FA claim remains correctly limited to dated owner confirmation; the eight branch/tag controls and fork approval are explicitly deferred with their API reasons. R4-C1 leaves three contrary active-enforcement claims, and R4-C3 leaves the canonical evidence locator false. |
| 3 — install, artifacts, smoke, closure, egress | **Satisfied** | Current local import/CLI tests pass. The unchanged 19-job hosted baseline proves the network-unavailable build, checked wheel/sdist, guarded fresh smoke, locked executing closure, image/source mutations, and failed egress attempts. Exact-head hosted status is reported unavailable, not inferred. |
| 4 — empty runtime set and frozen complete build lock | **Satisfied** | `dependencies = []`; lock structure and mutations pass; frozen consumption and executing-closure comparison remain unchanged from the hosted baseline. |
| 5 — decontamination and signed attestation | **Unsatisfied overall** | Scanner, manifest, decoder, private coverage, signatures, current binding values, tree digests, inventory-review binding, and key/schema-negative mutations pass. The disclosed historical loss is closed and no current binding is missing, but R4-C2 leaves Round 3's required private existence/uniqueness resolver absent and the current predecessor at two paths. |
| 6 — offline policy and mutations | **Satisfied under A3's narrower contract** | Source scan is clean; exact allowlist, retained red mutations, socket timing/self-test, local path tests, prior hosted Windows cells, and build egress evidence pass. No enforcement changed. |
| 7 — provenance and pre-push/history evidence | **Satisfied as written** | Fixture regeneration and both required mutations pass; the 31-commit all-object scan is clean; signed pre-push lineage reconstructs; the later irrecoverable terminal-record loss is honestly disclosed rather than fabricated. |
| 8 — documents/residuals/canonical briefs | **Unsatisfied** | Named residuals, A3 scope, A2 lifecycle, private-status sections, canonical briefs, parent retirement, and notes locality are correct. R4-C1 leaves three enforcement overclaims and R4-C3 leaves the settings evidence path/minimization description stale. |

## What was checked

- Read both canonical briefs, all 811 lines of the conditioned Phase 0 plan,
  closure-review round 3, both repair commits, and every acceptance criterion.
- Swept all tracked current text for required/enforced check, context, gate,
  branch, tag, fork, ruleset, mechanical-block, authoritative-control, and
  enforcement-boundary claims; separated operative text from historical
  reviews and future specifications.
- Verified all ten committed attestation signatures and archived verifier
  states; verified all retained private signatures; recomputed the 20 current
  file-backed bindings and both tree bindings; replayed reconciliation order,
  supersession, exact-head coverage, terminal non-self-binding, and historical
  loss exceptions.
- Inspected the minimized settings record's schema, commands, provenance,
  signatures, digest history, and credential-oriented fields/value shapes
  without reproducing private values.
- Ran both full test modes, lint, strict types, all public guards, lock checks,
  focused mutation groups, private coverage, all-object history scan, git
  integrity, and whitespace checks; compared executable enforcement surfaces
  to both prior closure heads.
- Queried authenticated remote metadata, exact-head run/status interfaces, the
  most recent retrievable hosted job graph and build log, local CLI access, and
  browser-session availability; did not substitute an older run for an
  unavailable exact-head result.

## Exact bounded work remaining

1. Correct the three “CI is the enforced boundary” tool docstrings and rerun
   the full tracked-tree control-claim sweep (R4-C1).
2. Add and run the promised private binding existence/canonical-path/
   uniqueness checker, and resolve or formally govern the duplicate legacy
   predecessor alias (R4-C2).
3. Correct the canonical plan's settings-evidence filename and full/minimized
   description (R4-C3).
4. Run the full public and private batteries, refresh and sign every binding
   changed by those repairs in declared order, create the next immutable
   exact-head terminal record, and scan the next review value-silently.

## Final verdict

**Request changes. Phase 0 is not closed.** R3-C2's irrecoverable loss and
R3-C3's credential deletion are honestly resolved, the current signed graph is
complete, and enforcement remains intact. R4-C1, R4-C2, and R4-C3 are bounded
closure blockers. Phase 1 planning may not begin until they are repaired and
independently verified.

# Phase 0 code review — round 2

**Reviewed:** the 13-commit Phase 0 implementation at
`6a951e995de81a9f0880015a1f4105e21634a397`, the canonical briefs, the
conditioned Phase 0 plan, the round-1 review and response, the complete public
tree and Git object graph, and the maintainer-private evidence chain without
reproducing protected values

**Verdict:** **request changes**

**Public push:** **not authorized**

**Public-host items:** remain separately classified as
**pending-public-verification**

The response fixed a substantial part of round 1: the path-ordering defects,
project-build placement, artifact allowlists, extractor reproducibility,
history rewrite, CLI version assertion, trust-root records, and several
mutation gaps now behave as claimed. The full public suite is green, and the
current tracked tree and current Git objects are clean.

That is not enough to ratify. The exact round-1 examples now fail, but several
controls still accept same-class bypasses. In particular, the offline source
scanner accepts a first-party re-export route and unresolved method/callback
routes; the acquisition gate executes a hash-bound local source archive before
the network-none boundary; the attestation verifier accepts signed graphs whose
semantic bindings disagree; the bound coverage and all-object tools do not
perform the checks their records claim; and the sensitive-path implementation
still contradicts the conditioned plan. These are genuine blockers, not edits
that can be safely prescribed as a finite wording-only condition.

## F1–F25 disposition

| Item | Round-2 status | Evidence independently verified |
| --- | --- | --- |
| **F1** | **partially resolved — blocker remains** | The two original chained re-export probes now produce one violation each, and `tests/test_offline_scan.py:333-366` covers them. However, importing the re-exported capability with a first-party `from` import produces zero violations; runtime identity inspection confirmed it is the forbidden standard-library module. `tools/offline_scan/scan_imports.py:685-716` registers every first-party imported attribute as a module prefix without checking what the defining module exports. |
| **F2** | **partially resolved — blocker remains** | The exact dead-branch module rebinding and bare callback probes now produce one violation each (`tests/test_offline_scan.py:385-414`). An unknown parameter method call, a callback retaining an unknown branch possibility, and a callback passed to an allowed higher-order helper still produce zero violations. Empty unknown-origin sets are discarded at `scan_imports.py:420-423,462-472`; unresolved attribute call targets are accepted at `:770-815`; and any one recognized origin makes a bare call acceptable at `:817-838`. |
| **F3** | **resolved** | `src/synthtwin/paths.py:74-100` implements the complete scheme character set. The three punctuated probes are in `tests/test_paths.py:23-35`; the targeted lexical test rejected all of them with zero calls to resolution, metadata, working-directory, or file-opening touchpoints. |
| **F4** | **resolved** | Only missing/non-directory results continue the Windows walk; other `OSError` values reject at `src/synthtwin/paths.py:174-193`. A direct `PermissionError` simulation raised `PathValidationError` and made zero resolution calls (`tests/test_paths.py:265-286`). |
| **F5** | **resolved** | The Windows walk is drivable with an explicit platform at `src/synthtwin/paths.py:138-175`. The always-running mocked reparse mutation at `tests/test_paths.py:243-262` rejected with zero resolution calls. The four host-inapplicable real-Windows integrations still skip locally, but the mandatory fallback did not skip. |
| **F6** | **resolved** | The test matrix consumes the wheel produced by `build` and installs it with `--no-index --no-deps` (`.github/workflows/ci.yml:80-122`). The project build itself occurs only inside `docker run --network none` at `:456-491`; offline-static and provenance no longer install the project (`:718-787`). |
| **F7** | **partially resolved — blocker remains** | Binary-only mode is embedded in `requirements-dev.in:1-4` and `requirements-dev.lock:1-3`, and a mutation exists at `.github/workflows/ci.yml:204-250`. A hash-bound local PEP 517 source archive in a requirements file was nevertheless accepted by the production `pip download --require-hashes --only-binary=:all:` shape: both metadata hooks ran, a sentinel was written, the archive was saved, and pip exited 0. The current mutation appends an unhashed directory, so hash-required mode can reject it before testing the dangerous state. |
| **F8** | **resolved statically; hosted execution pending** | The production image verifier is shared by the normal path and both mutations at `.github/workflows/ci.yml:251-325`. With a deterministic fake inspection result, the correct digest returned 0, while the tag-only and wrong-digest cases each returned 1. Docker is unavailable on this host, so the real pull and observed-digest behavior remains pending-public-verification. |
| **F9** | **resolved** | The allowlist includes the previously omitted package module, signer file, and signature at `.github/workflows/ci.yml:507-537`. A fresh local no-isolation build returned 0; the exact extracted workflow checker returned 0 and reported an eight-file wheel and 31-file sdist with no missing or unexpected members. |
| **F10** | **resolved** | The public scanner imports `tools/decontamination/tokenizer.py` and `surfaces.py` at `check.py:32-36`. A clean-process origin probe confirmed `extract_inventory_v3.py:28-35` imported those exact public files, not private copies. |
| **F11** | **resolved** | `extract_inventory_v3.py:111-129` reads `final_artifacts` and emits current header bindings. All 12 freeze-record artifact digests matched. The rerun left the inventory and manifest byte-identical; the regenerated manifest body also matched the committed public body. |
| **F12** | **partially resolved — blockers remain** | Both signatures validate; every current digest binding recomputes; the seven-file scanner-tree digest includes the verifier and pinned signer; and current header, count, uniqueness, and parameter values agree. The verifier nevertheless accepts freshly signed incomplete/inconsistent v2 graphs and duplicate control headers, and the bound coverage tool does not run against the public scanner. Details appear in R2-B4 and R2-B5 below. |
| **F13** | **partially resolved — blocker remains** | CI now runs the scanner, verifier, and public test file (`.github/workflows/ci.yml:687-716`), and all 38 public decontamination tests pass. The permanent table mutation still covers only four of 22 committed signatures (`tests/test_decontamination.py:193-199`), and the private all-entry run does not exercise scanner surface/decoder modes. The current decoder handled all independently probed entries, but the ratified mutation harness is still absent. |
| **F14** | **partially resolved — blocker remains** | The original JSON, JSON Lines, Arrow-family, array, database, spreadsheet, and statistical-file probes now route to the format gate, and all 17 provenance tests pass. The same suffix blocklist at `tools/provenance/check_provenance.py:68-150` still treats common YAML, XML, SQL-dump, DuckDB, DBF, and transport-file paths as ordinary source. |
| **F15** | **partially resolved — blockers remain** | The attestation binds the all-objects tool, coverage tool, and signed pre-push note; the note signature is valid; the current run enumerates 73 blobs, 13 commits, and 48 trees; and `tools/hooks/install.sh` exists. The all-objects tool fails open on non-text blobs, the bound note cites a follow-up evidence artifact that does not exist, and the installer overwrites an existing hook. Details are R2-B8, R2-B9, and R2-M2 below. |
| **F16** | **resolved** | The history is linear with 13 commits. Exactly six commits touch `src/` or `tests/`, and every one contains the required checklist sentence. The six old identifiers named in round 1 are absent, `git fsck --full --no-reflogs` reports no unreachable objects, the reflog contains one unique head, and no remote is configured. |
| **F17** | **partially resolved — blocker remains** | `.github/workflows/ci.yml:789-847` detects sensitive paths and emits a warning/summary. It explicitly never fails and never applies the label required by `docs/plans/phase-0-public-skeleton.md:500-502`; `SECURITY.md:248-252` still claims labeling occurs. The response is not a ratified plan amendment. |
| **F18** | **partially resolved — blocker remains** | Absolute, parent-traversal, out-of-tree, and untracked paths are rejected at `tools/provenance/check_provenance.py:312-360`, and their mutations pass. The wrapper at `tools/provenance/guard_runner.py:39-42` replaces only two high-level socket names. A generator run through it created a raw socket through the lower-level module and exited 0, contradicting the no-network claim at `check_provenance.py:39-41,363-370`. |
| **F19** | **resolved** | `.github/workflows/ci.yml:335-454` evaluates markers and compares the applicable lock and installed environment in both directions. Extracted-script probes returned 0 for an exact closure and 1 for both a missing applicable package and an extra installed package. |
| **F20** | **resolved** | Redaction at `tools/decontamination/check.py:81-91,109-134` replaces matched path components with digest tags. The focused protected-filename mutation returned red while neither output stream contained the neutral canary (`tests/test_decontamination.py:92-102`). |
| **F21** | **resolved** | Lexical rejection occurs before `_resolve_local` at `src/synthtwin/paths.py:226-238`. The repository spy covers resolution, `lstat`, `stat`, working-directory lookup, and opening at `tests/test_paths.py:178-208`; an expanded local spy also observed zero calls. |
| **F22** | **resolved** | The socket replacements occur during `tests/conftest.py` import (`:25-36`), and `tests/test_guard_timing_sentinel.py:19-42` records the exception during collection and requires the guard's exact exception class. |
| **F23** | **resolved for the original omission** | `SECURITY.md:110-156` records the same image digest as the workflow and names the hosted runner, interpreter, container runtime, and Git/OS tooling as trust roots. The documented signer fingerprint independently matches the pinned key. The claim that local source inputs are rejected remains false under F7. |
| **F24** | **partially resolved — minor remains** | README determinism is marked planned, the fixture exception is co-located with the rule, and signer history is corrected. The plan heading at `docs/plans/phase-0-public-skeleton.md:564` still says Amendment A1 is pending while `:627-631` says it was ratified. |
| **F25** | **partially resolved — minor remains** | `tests/test_cli.py:18-31` now pins exact metadata-backed version output, the bad-flag contract is tested, and `main` has a guarantee docstring. The new boundary sentence at `src/synthtwin/cli.py:53-58` says the function performs no filesystem operation, but a fresh audit of `main(["--version"])` observed 33 file/listing events from the required metadata lookup. |

## Remaining blockers

### R2-B1 — Blocker — F1's first-party re-export bypass remains

**Location:** `tools/offline_scan/scan_imports.py:685-716`

**Defect:** every attribute named by a first-party `from` import is blindly
registered as a module prefix, so importing a capability that a sibling module
itself imported launders that capability through the one-step rule.

**Concrete failure scenario:** product source imports the standard-library
process-capable module from `synthtwin.paths` and invokes its process API. The
import resolves to the live standard-library module, but `scan_source` reports
zero violations and offline-static stays green while a process launches.

### R2-B2 — Blocker — F2's unresolved call-target policy remains unsound

**Location:** `tools/offline_scan/scan_imports.py:55-60,420-423,462-472,770-838`

**Defect:** unknown bindings are represented by an empty set that is lost when
another possible origin appears, unresolved attribute calls are allowed, and
allowed higher-order helpers may receive unknown callables even though the
conditioned plan requires every call target to resolve statically.

**Concrete failure scenario:** a public function receives a caller-supplied
object and invokes one of its methods, or passes a caller-supplied callable to
an allowed higher-order helper. The supplied implementation performs a
forbidden operation, yet the scanner reports zero violations. A dead branch
that rebinds the unknown callable to an allowed API can also make a later bare
call appear safe.

This is not safely closed by adding more example strings to the blocklist. The
binding lattice must retain an explicit unknown possibility, and method and
higher-order call targets need a sound, documented policy consistent with D6.2.

### R2-B3 — Blocker — F7's acquisition boundary executes hash-bound local sources

**Location:** `requirements-dev.in:1-4`, `requirements-dev.lock:1-3`, and
`.github/workflows/ci.yml:148-250`

**Defect:** pip's binary-only option does not reject an explicitly named,
hash-bound local source archive, while the mutation tests only an unhashed
directory that hash-required mode can reject for an unrelated reason.

**Concrete failure scenario:** a future compiled lock contains a direct local
source archive with its correct hash. The networked prefetch accepts it,
executes its metadata hooks, and stores it before the network-none container
starts; the existing sentinel mutation remains green because its unhashed
fixture fails earlier.

The production gate needs a non-executing lexical/structural validator for
every lock input before pip runs, with red cases for source archives, direct
file references, VCS, editable, and path requirements. Its mutation must use a
self-contained PEP 517 backend with no unavailable build prerequisite so
sentinel absence proves the intended rejection.

### R2-B4 — Blocker — F12's verifier accepts signed semantic contradictions

**Location:** `tools/decontamination/verify_attestation.py:31-47,89-134` and
`tools/decontamination/check.py:39-47`

**Defect:** the verifier checks selected values but does not enforce the exact
attestation-v2 schema, does not recompute the named public surface digest, does
not bind the snapshot header to the snapshot field, and accepts duplicate
manifest headers under parser precedence different from the scanner.

**Concrete failure scenarios:**

- In a temporary trust tree, six required private binding fields were removed,
  the named public-surface digest was made incorrect, and the snapshot binding
  was made inconsistent with the manifest header. After recomputing the outer
  scanner-tree digest and signing with the temporary pinned key, the verifier
  returned 0.
- A manifest with the normal `n_max` line followed by a second `n_max: 1` line
  also verified after a valid temporary signature. The verifier used the first
  value while the scanner used the last, reducing the effective matching limit
  to one token without making verification red.

Require the exact v2 keys, types, and digest formats; exactly one instance of
every mandatory header; strict body-line validation; direct recomputation of
every named public-file binding; and one shared or demonstrably identical
manifest parser. The semantic mutation tests must re-sign consistent outer
bindings so each inner check is proven independently.

### R2-B5 — Blocker — F12's bound coverage tool never runs the public scanner

**Location:** `planning-notes/decontamination/coverage_battery.py:18-73`

**Defect:** the bound tool imports only the tokenizer and independently
reimplements n-gram matching; it never imports or calls the public scanner,
surface producer, or decoder, so it is not the ratified inventory-entry ×
matching-mode run.

**Concrete failure scenario:** in a temporary layout, both public `check.py`
and `surfaces.py` were absent. The bound battery still exited 0 with 2,065
entries, 9,704 applicable forms, and zero reported misses. An entry-specific
regression in filename, line, CSV-cell, syntax-tree-string, encoding, or binary
handling can therefore escape while the signed result remains “pass.”

### R2-B6 — Blocker — F13's permanent mutation battery is still narrower than the frozen table

**Location:** `tests/test_decontamination.py:193-199,267-275` and
`.github/workflows/ci.yml:695-716`

**Defect:** the magic mutation hard-codes four of 22 committed signatures, and
the entry-count mutation changes the outer manifest digest, so it stays red
even if the count check itself is deleted.

**Concrete failure scenario:** a refresh accidentally drops or mishandles one
of the 18 unparameterized signatures and is correctly re-signed. The four-case
test remains green. Separately, deleting the verifier's real count comparison
does not make the existing count test green because manifest-digest drift
already fails it.

The current implementation handled all 22 signatures in an independent probe;
the defect is that the required mutation harness does not preserve that fact.

### R2-B7 — Blocker — F14 remains a negative suffix list with obvious data routes

**Location:** `tools/provenance/check_provenance.py:68-150`

**Defect:** the expanded list still omits common structured, database, and
exchange formats, so the guard's “no real-derived artifact” claim remains
strictly weaker than its accepted inputs.

**Concrete failure scenario:** a generic derived schema is committed as YAML,
an XML export, an SQL dump, or a DuckDB file. Its text contains only residual-
class words and short numbers. `is_data_format` returns false, the fixture
manifest is never consulted, the decontamination scan can remain green, and
the artifact enters history silently.

### R2-B8 — Blocker — F15's all-objects tool ignores fail-closed decoder outcomes

**Location:** `planning-notes/decontamination/all_objects_scan.py:58,63-76,95-101`

**Defect:** `violations` is initialized and reported but never incremented;
every non-text blob is merely searched for printable runs, and the exit code
depends only on matches.

**Concrete failure scenario:** a scratch repository containing a malformed
historical blob produced exit 0 with one blob, zero matches, and zero
violations. An unreachable non-text artifact can therefore evade the current
tree scanners and still receive a clean all-objects record.

Every non-text blob must add a value-silent violation (printable runs may still
be searched), the exit status must include violations, and a red mutation must
place such a blob in an unreachable object. Repairing this bound tool forces a
fresh all-object run, signed note, attestation binding, and signature.

### R2-B9 — Blocker — F15's signed ordering claim cites absent evidence

**Location:**
`planning-notes/decontamination/out/pre-first-push-note.json:4-5`

**Defect:** the signed note correctly records the parent of current HEAD and
says one attestation-only commit follows, but it claims post-commit
re-verification is recorded in a remediation addendum; no such artifact exists
anywhere in the workspace.

**Concrete failure scenario:** the final attestation commit introduces a
protected commit-message or filename surface. The bound note predates that
commit, the cited follow-up evidence is absent, and public verification still
accepts the note digest. The current final commit was independently rescanned
clean; the defect is the false and incomplete evidence chain.

### R2-B10 — Blocker — F17 still contradicts the conditioned governance plan

**Location:** `.github/workflows/ci.yml:789-847`,
`docs/plans/phase-0-public-skeleton.md:500-502`, and `SECURITY.md:248-252`

**Defect:** CI reports this condition without enforcing it or applying the label
required by the plan, while the public security document continues
to claim the label exists.

**Concrete failure scenario:** a pull request changes a checker and its
workflow. The reporting job succeeds whether comparison succeeds or fails,
applies no label, and supplies no durable label for release-note collection;
the repository nevertheless tells auditors that this control is in force.

Either implement the ratified label safely or take the changed mechanism back
through a plan amendment. A code-review response cannot amend the conditioned
plan.

### R2-B11 — Blocker — F18's generator guard is bypassable below `socket`

**Location:** `tools/provenance/guard_runner.py:39-42`,
`tools/provenance/check_provenance.py:39-41,363-370`, and
`tests/test_provenance.py:447-471`

**Defect:** the wrapper replaces two names in the high-level module but leaves
the lower-level constructor, subprocess routes, and native routes available,
while the checker and manifest contract say a rebuild can never touch the
network.

**Concrete failure scenario:** a tracked fixture generator creates a socket
through the lower-level module or launches an external client. The generator
runs on the networked provenance runner—or on the maintainer machine that also
holds private sibling material—while the guard stays green. The direct raw-
constructor probe exited 0; the existing mutation exercises only the patched
high-level helper.

## Major and minor issues introduced or left by the fixes

### R2-M1 — Major — F12's count test does not isolate the claimed check

**Location:** `tests/test_decontamination.py:267-275`

**Defect:** deleting a manifest body line changes the already-bound manifest
digest, so the test passes even if actual entry counting is removed.

**Concrete failure scenario:** a refactor deletes `len(body_hashes) != count`.
The mutation still returns red on outer digest drift and falsely certifies the
missing semantic check. Use a temporary signer and refresh all outer public
bindings before asserting the inner count mismatch fails.

### R2-M2 — Major — the advisory hook installer destroys an existing hook

**Location:** `tools/hooks/install.sh:5-25`

**Defect:** the installer unconditionally truncates `.git/hooks/pre-push`
without checking, refusing, backing up, or chaining an existing executable.

**Concrete failure scenario:** a contributor already has an organizational or
security pre-push hook, runs the advertised one-command installer, and silently
loses the earlier control. Refuse installation when a non-identical hook
exists, or install through a non-destructive chaining mechanism.

### R2-m1 — Minor — F24's amendment heading still says “pending”

**Location:** `docs/plans/phase-0-public-skeleton.md:564,627-631`

**Defect:** the section heading and terminal status state opposite lifecycle
states.

**Concrete failure scenario:** an auditor reads the heading or links directly
to the section and treats the operative classifier as unratified, even though
the section footer and bound private review say it is ratified.

### R2-m2 — Minor — F25's new CLI docstring overclaims filesystem behavior

**Location:** `src/synthtwin/cli.py:38-58`

**Defect:** the docstring says `main` performs no filesystem operation even
though the plan-required metadata version lookup performs installed-metadata
filesystem reads; its “only exception” statement also omits ordinary output
stream failures.

**Concrete failure scenario:** an auditor treats the docstring as the promised
boundary and concludes version output is memory-only, or a caller relies on
the stated exception set while a closed output stream raises an I/O error.
State the narrow truth: no user data path is read; installed package metadata
is consulted; ordinary output/metadata errors follow the implemented handling.

### R2-m3 — Minor — the decontam workflow comment names the wrong component

**Location:** `.github/workflows/ci.yml:694-716`

**Defect:** the comment says signature verification and the mutation battery
live inside the checker, while the workflow correctly runs them as separate
steps.

**Concrete failure scenario:** a maintainer consolidates the job based on the
comment, retains only `check.py`, and silently removes the verifier and test
steps that actually supply those controls.

## Attestation-v2 and private extraction verification

The current bytes are internally consistent even though the verifier and bound
tools have the defects above:

- `attestation.json` validates against the pinned signer and namespace.
- The signed pre-push note validates against the same pinned signer and its
  digest equals the attestation binding.
- The complete seven-file scanner-tree digest independently matches and covers
  `allowed_signers`, `check.py`, `magic.txt`, `manifest.txt`, `surfaces.py`,
  `tokenizer.py`, and `verify_attestation.py`.
- All 18 digest bindings independently recompute, including both inventory
  reviews, the freeze record, extractor, inventory, coverage tool, all-objects
  tool, pre-push note, public modules, manifest, and snapshot tree.
- All 12 artifacts named by the final freeze record match their recorded
  digests. The public and private frozen magic tables are byte-identical.
- The manifest has 2,065 actual body lines, 2,065 unique body lines, valid
  lowercase hash syntax, and a header/attestation count of 2,065. Its
  `n_max`, header bindings, private inventory hashes, and snapshot digest all
  agree.
- The v3 extractor imported the public canonical tokenizer and surface module.
  A rerun reproduced the inventory and manifest byte-for-byte and reproduced
  the committed public manifest body.
- The current Git graph contains 73 blobs, 13 commits, 48 trees, and no tags.
  An independent decoder pass found zero non-text current blobs. This current
  clean fact does not repair the all-objects tool's fail-open branch.

## Required commands and probe results

Run from the public repository root unless noted:

```text
.venv/bin/python -m pytest
  112 passed, 4 skipped in 2.79s
  (the skips are host-inapplicable real-Windows integration tests)

.venv/bin/python -m ruff check .
  All checks passed!

.venv/bin/python -m mypy src
  Success: no issues found in 3 source files

.venv/bin/python tools/decontamination/check.py
  decontamination: clean

.venv/bin/python tools/decontamination/verify_attestation.py
  signature, scanner tree, current manifest, header bindings, and counts verified

.venv/bin/python tools/offline_scan/scan_imports.py src
  3 Python files, 0 reported violations

.venv/bin/python tools/provenance/check_provenance.py
  passed

private coverage_battery.py
  2,065 entries; 9,704 applicable forms; 621 skipped; 0 reported misses

private all_objects_scan.py
  73 blobs; 13 commits; 48 trees; 0 tags; 0 reported matches/violations

local python -m build --no-isolation + exact workflow allowlist checker
  build exit 0; checker exit 0; wheel 8 files; sdist 31 files
```

Targeted probes additionally covered:

- both original allowed-module re-export routes and the remaining first-party
  `from`-import route;
- the exact conditional rebinding module, the exact bare callback, an unknown
  method target, an unknown union, and a higher-order callback;
- all three punctuated schemes with a filesystem-touchpoint spy;
- Windows reparse and `PermissionError` simulations with resolution forbidden;
- the collection-time guard sentinel;
- a hash-bound local source archive under the production acquisition options;
- correct, tag-only, and wrong image-reference verification branches;
- exact, missing, and extra closure comparisons;
- the original and newly omitted format suffixes;
- local artifact members against the workflow's own allowlist;
- current and mutation all-object graphs, including an unreachable malformed
  blob;
- current attestation signatures, all binding digests, header/body counts,
  duplicate headers, missing bindings, and named-binding mismatches under fresh
  temporary signatures;
- protected-filename value-silent output;
- all six source/test-changing commit-message checklist lines and absence of
  the six purged round-1 object identifiers;
- direct low-level-socket construction through the fixture guard; and
- exact CLI version output plus filesystem audit events.

Docker is unavailable on this review host. I did not claim execution of the
real container image, network namespace, or hosted matrix.

## Acceptance-criterion status

| Criterion | Round-2 status |
| --- | --- |
| 1 — owner waiver and README record | **satisfied** |
| 2 — public governance settings | **pending-public-verification**; F17 is a separate static plan contradiction |
| 3 — build, artifacts, smoke, egress | **not accepted**: local artifacts pass, but F7 violates the pre-boundary rule and real container execution is pending |
| 4 — empty runtime set and frozen closure | **not accepted**: current entries are pinned, but F7 leaves prohibited lock/input forms executable |
| 5 — decontamination and signed attestation | **not accepted**: current bytes match, but F12/F13 and the bound-tool defects make the verification and mutation claims incomplete |
| 6 — offline policy and mutations | **not accepted**: F1 and F2 retain executable scanner bypasses |
| 7 — provenance and all-object evidence | **not accepted**: F14, F15, and F18 remain open |
| 8 — documentation and residuals | **not accepted**: F17, F24, and F25 leave public claims inconsistent or false |

## Pending-public-verification

- creation and availability of the public repository;
- default-branch ruleset details, app-bound `gate`, force-push/deletion blocks,
  bypass actors, tag restrictions, signing enforcement, fork-workflow approval,
  workflow permissions, two-factor account state, recovery-code handling, and
  private vulnerability reporting;
- the real hosted Ubuntu/macOS/Windows Python matrix, including non-skipped
  Windows reparse behavior;
- pulling and inspecting the pinned container image, the real
  `--network none` build, artifact transfer/smoke behavior, both image
  mutations on the hosted engine, and the aggregate status context.

The workflow remains statically positive on full-SHA action references,
read-only default token permission, absence of privileged triggers/secrets,
and complete gate dependencies. Those facts do not substitute for the first
hosted run.

## What was checked

- Read the canonical `AGENTS.md`, `CLAUDE.md`, all 631 lines of the conditioned
  plan, the complete round-1 review and response, every changed public source,
  test, tool, document, workflow section, and all 13 commit bodies/trees.
- Re-ran every probe named in the round-2 request and chased each repair's
  adjacent policy surface rather than stopping at the exact regression string.
- Recomputed the complete current attestation and extraction graph without
  printing private inventory entries, then tested the verifier with fresh
  temporary signatures so inner checks were isolated from outer signature
  drift.
- Inspected all tracked paths and all reachable/unreachable Git objects;
  verified the repaired history is linear and the named old objects are gone.
- Built and inspected both distribution artifacts locally and extracted the
  workflow's own comparison scripts for direct green/red probes.
- Scanned this review itself against the committed decontamination manifest
  before finalizing it.

## Verdict

**Request changes.** The history **may not be pushed publicly**. F1, F2, F7,
F12–F15, F17, and F18 include genuine security, fail-closed, evidence-chain,
and conditioned-plan blockers. In particular, sound handling of unresolved
call targets and the sensitive-path plan contradiction require design or plan
work beyond exact bounded edits applicable without another review round.

After the fixes, refresh every affected private binding in dependency order:
coverage/all-object tools and mutations, full private runs, signed pre-push
record (including truthful final-commit ordering evidence), attestation,
signature, then a complete current-tree and all-object rescan. Do not begin
Phase 1 or make the first public push until a further code-review round clears
that chain.

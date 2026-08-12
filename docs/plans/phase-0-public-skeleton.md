# Phase 0 — Public skeleton & security baseline

**Status:** revision 6 — the **conditioned plan**. Round-5 verdict (final
authorized round): **approve-with-conditions**, seven bounded text edits
(C1–C7 in `reviews/phase-0-review-round-5.md`) applied verbatim below; per
that verdict, implementation may begin under this plan without a further
plan-review round, gated first by the D2 precondition and the C1 Class-A
freeze gate. Fully self-contained: no decision is incorporated by reference
to an earlier revision; earlier revisions are superseded drafts with no
normative force. Reviews and responses live in `reviews/`. No code exists
yet.

**Scope:** public repository, license (blocking IP precondition), CI,
decontamination system, data-provenance guard, repository governance, offline
guarantee. **Non-goals:** no profiling/generation/validation code; no PyPI
publication; no feature work.

**Accepted-and-closed decisions** (round-4: "do not reopen absent new
evidence"): D12's single-stream RNG with declared rebaseline; D7's signed
fully-bound attestation within D14's narrowed threat model; D14's narrowed
tamper-resistance claim; the two-class inventory *architecture* (its
implementation rule is revised below per the round-4 ruling).

**Decontamination note:** this plan reproduces no source-study vocabulary.
The plaintext inventory lives only in the maintainer-private planning notes
at `../../../planning-notes/` relative to this file — the sibling of the
repository root, outside the repository; `planning-notes/` is additionally
ignored in-repo; acceptance verifies the documented path resolves outside
the repo root.

---

## D1. Product name: `synthtwin`

Chosen 2026-08-06 over three free alternatives after the charter's working
name was found taken on PyPI. Repo `synthtwin`, import `synthtwin`, command
`synthtwin`. PyPI availability is treated as **unverified** until an
authorized upload succeeds; no reservation mechanism is used or claimed;
rename risk before first release is accepted.

## D2. License, copyright, and code provenance

- **MIT.** Notice: `Copyright (c) 2026 Alfredo Camargo Rodrigues`.
- **Blocking precondition:** no public commit until a dated written
  determination from the appropriate University of Iowa IP authority
  exists. Acceptance verifies authority, date, scope, and an
  **affirmative authorization for public MIT release of this work**.
  **Owner decision, 2026-08-07:** the project owner **waived this
  precondition**, on the rationale that this is non-commercial research
  tooling, and directed the project to proceed; the owner accepts the
  associated risk. This is an owner override of a reviewer-held
  condition, recorded here for the audit trail; the implementer's noted
  caveat (institutional IP policies can attach to employee-created
  software regardless of commercial intent) was given and acknowledged.
  Acceptance criterion 1 is amended accordingly: it verifies this
  recorded waiver instead of the determination document. A
  negative determination on releasing the new work, if one were ever
  issued, **halts the project**;
  a negative determination on prototype reuse activates the fallback:
  ported-machinery work is blocked until the phase that needs it delivers
  an authorized sanitized public method contract plus fixed neutral
  reference vectors, reviewer-checked and frozen before implementation.
  Phase 0 relies on no prototype line.
- Contribution licensing: inbound = outbound (MIT); no CLA.

## D3. Hosting, repo location, public self-containment

- Public GitHub repository from the first commit (after the D2
  precondition), under the maintainer's account; governance in D14.
- Local working copy at `Research/0- Synthetic dataset/synthtwin/` (owner's
  decision), inside OneDrive. Recorded mitigations: GitHub is source of
  truth; small pushed increments; repo stays lean; first `.git` corruption
  moves the working copy out of OneDrive.
- The in-repo agent briefs are renamed to `synthtwin`, sanitized of all
  inventory vocabulary, and canonical (the parent-folder copies are retired
  at repo creation; one short historical rename note remains). The
  prototype is described as maintainer-private; prototype-diff review is a
  maintainer/reviewer-only step; Phase 0 claims no public numeric oracle —
  that oracle (contract + frozen vectors) is a blocking deliverable of the
  first phase that ports numeric machinery.

## D4. Layout, build backend, entry point, versioning

```
synthtwin/
├── pyproject.toml          # hatchling; [project.scripts] synthtwin = synthtwin.cli:main
├── LICENSE  README.md  CHANGELOG.md  SECURITY.md  CONTRIBUTING.md
├── CLAUDE.md / AGENTS.md   # sanitized canonical briefs
├── src/synthtwin/          # src layout; __init__ + cli.py (version/status stub)
├── tests/
├── tools/                  # decontamination/, offline_scan/, provenance/
├── docs/plans/             # plans + reviews/
└── .github/workflows/
```

- Build backend hatchling; src layout (tests run against the installed
  package).
- Console entry point `synthtwin = synthtwin.cli:main`; Phase 0 CLI prints
  version, status, and repo URL only.
- Single version source: `[project] version` in `pyproject.toml`, read at
  runtime via `importlib.metadata.version("synthtwin")` (see D6.2 for the
  exact allowed API).
- Python ≥ 3.10; CI matrix in D9; the floor tracks security-supported
  CPython (3.10 dropped in the first minor release after 2026-10; new
  stable CPython enters CI within one release). SemVer, `0.x` until the
  Phase 3 product exists.

## D5. Dependency and supply-chain policy

- **Phase 0 ships zero runtime dependencies.** `numpy`/`pandas` enter in
  Phase 1, each with written justification reviewed adversarially.
- **Introduction protocol (from Phase 1):** honest tested lower bounds in
  `pyproject.toml`; a committed lockfile covering the dev/CI environment
  **and the complete build closure** (frontend, backend, transitives) with
  hashes, consumed **frozen** (CI fails on drift); a minimum-versions CI
  job tests the declared floors.
- **Hash-pinned user install:** the first dependency-bearing release ships
  a generated `--require-hashes` requirements file as a release artifact;
  CI installs from it into a fresh offline-guarded venv and runs the smoke
  suite; `SECURITY.md` names it the supported institutional install path.
  Ordinary `pip install synthtwin` is bounds-governed and documented as
  such.
- **Non-executing acquisition gate:** the networked prefetch accepts
  wheels only: `pip download --require-hashes --only-binary=:all:`
  against the complete lock. The lock and prefetch reject source
  distributions, VCS requirements, editable requirements, and local/path
  requirements; no PEP 517 or legacy setup hook may execute before the
  network-none boundary. Every downloaded wheel is hash-verified
  immediately before the wheelhouse is mounted read-only into the build
  container. A malicious-source-distribution fixture whose metadata hook
  writes a sentinel is required to be rejected with the sentinel absent;
  this mutation runs at the prefetch boundary, not inside the later
  build.
- **Network-unavailable build (round-4 carried R3-F4 closed):** the build
  job (Ubuntu) first verifies and populates a local wheelhouse from the
  lock (per the acquisition gate above), then runs the entire build
  **inside a container started with `--network none`**: environment
  created `--no-index --find-links wheelhouse/`, build invoked
  `python -m build --no-isolation`. No proxy, no DNS, no egress of any
  kind is available to build code — process- or native-level included,
  because the network namespace is empty. Acceptance compares the
  packages present in the executing build environment to the lock
  (`pip freeze` + hash check) and records the wheel/sdist digests.
  **Egress mutation:** a deliberate HTTP fetch attempted inside the same
  container must fail; demonstrated in CI self-test.
- **Pinned build image:** the Ubuntu build uses the official CPython 3.14
  slim Linux image referenced only as `repository@sha256:digest`, never
  by a mutable tag alone. The OCI digest is a committed lock input; CI
  verifies the observed image digest before execution and records it
  together with the in-container OS identity and exact Python and pip
  versions. The image digest and in-container interpreter/toolchain are
  included in `SECURITY.md`, the executing-closure comparison, build
  record, and release SBOM. A tag-only reference and a wrong observed
  digest are required red mutations. The container image is a named
  trust root at the pinned digest; changing it follows the
  dependency-update review path.
- **Trust roots named honestly** in `SECURITY.md`: the GitHub-hosted
  runner (actual image version echoed into logs from the runner context
  each run; a `-latest` label is never called a pin), the CPython
  interpreter (exact version installed by the SHA-pinned setup action and
  recorded), the container runtime, git/OS tooling. Everything pinnable is
  pinned (actions by SHA; closures by hash); everything else is a named
  trust root.
- Supply-chain inventory by role in `SECURITY.md`: runtime direct; runtime
  transitive; build frontend/backend; installer toolchain (pip/uv versions
  used in CI); artifact checker (twine); dev tools; CI platform; release
  tooling (none until first release). Each row: executes on a user
  machine? pinned by what? SBOM + exact closure hashes accompany every
  release from the first one.

## D6. The offline guarantee

**Boundary (accepted round 2; wording final):** synthtwin's own code
contains no construct that initiates network I/O, no subprocess execution,
no native-code calls, no dynamic code loading; it accepts only local
filesystem paths; it is fully functional air-gapped. Verification is
source audit plus the layered checks below — explicitly not an OS-level
sandbox; institutions requiring enforcement run it inside their own
network-isolated environment.

1. **Path locality rule** (product code, applies to input, output, and
   temp paths; standing rule for all phases):
   - (i) lexical checks on the raw string **before any filesystem call**:
     reject URL schemes (`scheme://`), Windows UNC (`\\server`,
     `//server`) and device/namespace forms (`\\.\`, `\\?\`);
   - (ii) **Windows: reject links without following them (round-4 carried
     R2-F2 closed).** Each existing component is examined with `os.lstat`;
     any reparse point (symlink/junction/mount point) causes rejection
     with a plain-language error. The link node's metadata is local; the
     rule never reads or resolves the target, so no remote traversal can
     occur. Full-path resolution (`Path.resolve()`) is invoked **only
     after** the component walk finds no reparse points. Links are
     legitimately rare in the tool's audience workflows; the restriction
     and its rationale are documented.
   - (iii) POSIX: symlinks are permitted; the resolved real path is
     re-validated against the lexical rules (UNC/device forms do not
     exist on POSIX; network mounts are the named residual below).
   - Tests: per-platform units for every rejected form; the Windows link
     test **asserts resolution is never invoked** on link-containing input
     (mock/spy on the resolution call), not merely that rejection is the
     eventual result.
   - Named residuals in `SECURITY.md`: OS-transparent network mounts are
     portably undetectable; local-actor TOCTOU between check and use is
     outside the threat model (the tool defends data from itself, not
     from a hostile local OS).
2. **Positive runtime import policy — exact and API-granular (round-4 F2
   closed).** Phase 0 `src/` may use exactly:
   `argparse`; `dataclasses`; `json`; `pathlib`; `sys` (excluding writes
   to `sys.modules` and `sys.path`, which the scanner bans); `typing`;
   from `os`: only `os.path` functions, `os.fspath`, `os.getcwd`,
   `os.lstat`, and read-only `os.environ`; from `importlib.metadata`:
   **only the `version()` function** — `EntryPoint`, `entry_points`, and
   any `.load(` reference are banned tokens in the scanner, because
   `EntryPoint.load()` is a dynamic loader reachable through an otherwise
   allowed module (round-4's finding). No other module, no third-party.
   The source policy is enforced as an AST/name-binding positive policy,
   not as substring bans alone. Every import binding, module-rooted
   attribute read or write, subscript into module/function state, and
   call target must resolve statically to an exact enumerated API;
   indirect or dynamically manufactured call/attribute targets are
   rejected. All reads and writes of `sys.modules` and `sys.path`, all
   dunder-state traversal, and the reflection primitives `getattr`,
   `setattr`, `delattr`, `hasattr`, `vars`, `globals`, `locals`, and
   `dir` are forbidden in `src/`; aliases are traced to their origin. The
   existing direct mutations remain, and two reflective mutations are
   added: a split-string lookup through a preloaded module registry and a
   split-string lookup through an allowed function's global state, each
   attempting a forbidden process call; both must be red. Allowlist
   changes are plan-level decisions with a capability audit of the added
   API surface.
3. **Python-level socket guard** in the test suite, installed at
   `tests/conftest.py` module import time (active through collection and
   package import); described everywhere as a guard, never as "network
   disabled"; its self-test asserts it fires on a deliberate connection.
4. **Built-artifact smoke test:** the D5 network-unavailable build's wheel
   installs into a fresh venv with the guard applied via `sitecustomize`;
   `synthtwin --version` and the stub CLI run; sdist/wheel contents match
   an explicit file allowlist.
5. **Mutation demos, one per promised bypass class, each demonstrated
   red:** disallowed import; dynamic import (`importlib.import_module`);
   entry-point loading (`EntryPoint` reference); process launch
   (`subprocess` and `os.spawn*`); native call (`ctypes`); URL input; UNC
   input; Windows link-component input (asserting no resolution call);
   build-container egress attempt (D5).

## D7. The decontamination system

Architecture (two classes, hashed manifest, signed attestation) accepted in
rounds 3–4; the implementation rule revised per the round-4 ruling and
R4-F1.

- **Corpus:** the complete prototype snapshot — every file (docs, all
  Python scripts including examples, the shell script, both example
  profile artifacts) — processed by a versioned maintainer-only
  extraction script in the private notes.
- **Pre-code Class-A freeze:** before the authoritative Phase 0
  extraction is run, before either the conditioned plan or the round-4
  response is scanned, and before extractor/scanner/manifest code is
  written, materialize the exact common-word list and exact
  numeric/date/quarter grammar as versioned artifacts. Each artifact
  header records its neutral source identifier and digest, deterministic
  derivation/cutoff and normalization; no manual additions or removals
  are permitted. The artifacts must be source-independent: they are not
  derived from the prototype, the public tree, or scan results, and a
  match is fixed by editing public text, never by expanding the
  classifier. Their paths and SHA-256 digests, full contents, and
  derivation records are included in the initial adversarial inventory-review
  artifact. Any later change is a plan-level decision and forces
  attestation refresh plus a full private/public rescan. The conditioned
  plan and the round-4 response must each produce zero Class-A matches
  under these exact artifacts before code work proceeds beyond this
  freeze gate.
- **One discriminative rule for every candidate surface (round-4 R3-F1
  fix: code literals included).** Candidate surfaces are every normalized
  path component; every decoded line of every textual snapshot file
  (including Python identifiers, attributes, and comments, shell and
  other non-Python source, and documentation); every cell of every
  structured text/profile artifact; and every AST string constant from
  every Python script. Structured extractors may add surfaces but never
  replace raw-text extraction. Coverage mutations place a neutral canary
  only in a Python identifier, only in a Python comment, only in a shell
  token/comment, and only in a path; every mutation must enter Class A
  and make the public scanner red. **Every** candidate — code literals
  not excepted — passes the same deterministic distinctiveness test: it
  enters **Class A** iff it contains at least one token that (a) is absent
  from the frozen, versioned common-word list artifact and (b) is not
  purely numeric/date/quarter-patterned under the frozen pattern grammar
  (both artifacts digest-bound in the attestation). Everything else is
  **Class B** — not denylisted; its leak class is governed by D13 with the
  residual stated in `SECURITY.md`. Column names are expected to be
  overwhelmingly Class A by this test; generic code literals (error
  messages, format fragments made of common words) fall to Class B, which
  is what makes a zero-match tree achievable *without exemptions*.
- **Emitted units (round-4 F1 fix):** for each Class-A surface the
  manifest contains: the full normalized entry, **and each distinctive
  token as its own entry**, and any explicitly protected multi-token
  subphrases the extraction rule designates. A distinctive token escaping
  into a new context is therefore caught by its own hash. Mutations
  transplant a neutral canary token into fresh left/right contexts,
  filenames, and identifier positions, and must go red.
- **Matching contract (order per round-2 ratification R2-C1):**
  NFKC-normalize the complete input string first; then find maximal
  Unicode-alphanumeric chunks in the normalized string; then split chunks
  at case transitions and letter/digit boundaries; then casefold each
  subtoken — so compatibility spellings (fullwidth, enclosed
  alphanumerics) yield the same token stream as ASCII. Candidate n-grams
  up to the `n_max` recorded in the manifest header (the header is the
  sole source of truth); file paths scanned as content.
- **Deterministic decoder/classifier order and bounded residual:** first
  recognize text BOMs longest-first (UTF-32 BE/LE, then UTF-8, then
  UTF-16 BE/LE),
  decode strictly, reject malformed input, apply the forbidden-control
  test to decoded Unicode scalar values, and scan the decoded text. With
  no recognized BOM, check the committed `magic-v1` offset/hex-signature
  table, then attempt strict UTF-8; valid UTF-8 is control-checked as
  decoded text and scanned. If strict UTF-8 fails, reject raw C0 bytes
  outside TAB/LF/CR and DEL/C1 bytes 0x7F–0x9F, otherwise decode as
  Latin-1 and scan. Before decoder/scanner code is written, `magic-v1`
  is materialized with every offset and exact hex signature,
  independently reviewed, SHA-256-frozen, and attestation-bound; its
  initial scope is archive, image, executable, compound-document,
  database, and columnar-storage signatures, and it makes no
  completeness claim. Named residual: every non-magic byte stream that
  survives these rules is treated and scanned as text regardless of
  whether a human would call it binary; no format-classification
  guarantee is made for that set. Required outcomes are explicit: valid
  BOM-tagged UTF-8/16/32 is green and token-scanned; malformed BOM text,
  BOM-less UTF-16/32 with forbidden controls, embedded forbidden
  controls, and listed magic are red; an unknown-magic surviving stream
  follows the named residual and a placed Class-A token in it is
  detected.
- **Signed, fully bound attestation (accepted in round 4; restated
  self-containedly):** the maintainer-side coverage tool emits an
  attestation binding by SHA-256: the canonical prototype snapshot digest
  (sorted path list + per-file digests → tree digest; algorithm committed
  inside a named bound tool, per the round-4 ruling note), the
  extraction/filter script, the common-word list, the pattern grammar,
  the plaintext inventory, the public manifest, the complete scanner tree
  (`tools/decontamination/`), the coverage tool itself, entry count,
  `n_max`, result, and the digest of the reviewer's inventory-review
  artifact (stored in the private notes). The manifest never contains its
  own digest. The attestation is signed (SSH signature; public key pinned
  in the repo and `SECURITY.md`). Public CI verifies the signature
  against the pinned key and recomputes every publicly computable digest;
  any drift, missing signature, or wrong key is red. Refresh triggers:
  any change to the manifest, scanner tree, pinned key, or any bound
  input. Mutations: structurally consistent but unsigned attestation
  red; wrong-key signature red. Within D14, the signature authenticates
  origin against third parties; maintainer-key compromise is the stated
  residual.
- **Private coverage run:** parameterizes every inventory entry × every
  matching mode against the public scanner before any push that touches
  bound inputs and before every release; result bound in the attestation.
  The **initial inventory is independently reviewed by the adversarial
  reviewer** (read access to private notes); the review artifact digest is
  bound.
- **Acceptance:** every tracked file in the initial tree — all plans and
  reviews included — **scans clean (zero matches) under the final Class-A
  manifest** before the first public push. No content exemptions exist.

## D8. `SECURITY.md`

Contents: plain-language threat model (theft and tampering, not statistical
disclosure); the D6 boundary statement with the path rules and the named
residuals (network mounts, TOCTOU, printable-binary, and the D6
Amendment A3 caller-supplied-code residual - a booby-trapped object or
callable handed to synthtwin's public functions runs in the caller's own
process under the caller's own authority, and the boundary governs what
synthtwin's own code initiates), stated together with A3's scope
sentence that the static scanner is a best-effort, mutation-tested layer
inside that boundary rather than a proof of universal call-target
closure; the supply-chain
inventory and trust roots (D5); the network-unavailable build design; the
hash-pinned institutional install path; the decontamination model — hashed
manifest, signed attestation, pinned key, verification procedure, Class-B
residual; the D13 provenance controls and the source-exposed-maintainer
residual; the D14 governance controls and narrowed claim; release-integrity
requirements (D10); vulnerability reporting. Phase 0 commits only to what
Phase 0 can demonstrate.

## D9. CI (GitHub Actions) — fully enumerated

Jobs: **lint** (ruff); **types** (mypy strict on `src/`); **tests**
(Ubuntu × {3.10, 3.11, 3.12, 3.13, 3.14}; macOS-latest × 3.14;
Windows-latest × {3.10, 3.11, 3.12, 3.13, 3.14}, with the complete
Windows path-locality/reparse suite running in every cell); **build**
(the D5 wheelhouse + `--network none`
container build, twine check, content allowlist, offline fresh-venv
install + CLI smoke, closure-vs-lock comparison, egress mutation);
**decontam** (D7 scanner over all tracked files and paths; signature +
digest verification; full neutral mutation battery); **offline-static**
(D6.2 allowlist scan; all D6.5 mutation classes); **provenance** (D13
checks + mutations). **Gate:** one additional job named `gate` with
`if: always()`, listing every job above in `needs`, failing unless every
one succeeded. The branch ruleset WILL require exactly the `gate`
context, bound to the GitHub Actions app, once it is applied: while the
repository is private that ruleset is deferred and NOT in force (see the
owner-decision records and SECURITY.md). All actions pinned by commit SHA; default
token permissions `contents: read`; no secrets exist in Phase 0. CI green
before any Phase 1 work.

## D10. PyPI publication: none in Phase 0

First publication only with a genuine user capability (earliest: end of
Phase 3). Fixed requirements for that first release, whichever phase makes
it: Trusted Publishing (OIDC, no long-lived tokens); PyPI attestations;
clean tagged builds from a protected release environment; two independent
builds compared for reproducibility; artifact hashes + SBOM published;
the D5 hash-pinned install file if any runtime dependency exists; and a
demonstration that a **signed tag is accepted while an unsigned tag, a tag
update, and a tag deletion are rejected** by the configured protections.
Name-loss risk in the interim is accepted (D1).

## D11. README v0 — fully enumerated

Written for the world: what synthtwin will do (synthetic twin + schema +
relationships + plain-language quality report); who it is for; the security
architecture in plain language (offline boundary as stated in D6,
profile/generator separation as the future architecture, dependency policy
with direct-vs-closure phrasing); the honest-limits section from the
charter; the D2 license section with the recorded determination
date/outcome; the tested-platform determinism statement from D12; a status
banner — what exists today (skeleton only), current phase, **not yet on
PyPI**; every capability tagged built/planned. No overclaiming.

## D12. Determinism and serialization policy (accepted in round 4; restated)

- **Rebaseline:** synthtwin does not reproduce the prototype's draw
  streams; it preserves the prototype's determinism rules and statistical
  contract. On every rebaseline path, neutral reference vectors are
  reviewer-checked and frozen **before** the implementation they anchor
  exists; newly generated goldens are never their own oracle.
- **One RNG, literally:** a single `numpy.random.Generator` instance,
  created once from the seed, threaded explicitly through every consumer.
  No module-level randomness; no unordered iteration on
  randomness-consuming paths (sorted first); identifiers drawn without
  replacement; output column order a deterministic function of the schema
  with derived columns appended in documented order; internally selected
  special elements chosen by deterministic rule, never an extra draw.
  Documented consequence: schema changes shift subsequent streams at the
  same seed; byte-stability is promised only across identical inputs. A
  keyed-per-column design may be proposed only as an explicit charter
  amendment to the project owner in a future phase plan, carrying full
  executable derivation details (name normalization, fixed-endian
  digest-to-integer mapping, length-delimited domain tags, collision
  response) plus published derivation vectors; absent that, single-stream
  stands.
- **Byte-identity scope:** guaranteed = same (profile, seed, synthtwin
  version, exact locked closure) **on the same platform**. Cross-platform
  equality is an empirically verified result of golden-hash tests on every
  CI matrix cell, reported as tested — never promised beyond the tested
  matrix. A divergence is release-blocking until fixed or converted to
  per-platform goldens with a changelog entry. Across numpy versions:
  statistical contract only; golden regeneration on a numpy bump is an
  explicit changelogged event.
- **Canonical serialization:** UTF-8; explicit `\n`; documented
  shortest-round-trip float format; JSON with sorted keys and fixed
  separators; documented null convention; dates/times ISO 8601 with
  explicit offset and fixed precision. Golden-hash tests from the first
  phase that writes files.

### D12 Amendment A-2026-08-11 — three scoped exceptions for twin CSV cells

**Recorded 2026-08-11 by owner decision, on the Phase 2 plan review
round-4 item P2-R4-F7.** The paragraphs above remain the canonical rule
and their historical text is unchanged. This amendment records three
exceptions the owner settled while planning Phase 2. **Every exception
below is scoped to CELLS OF THE SYNTHETIC TWIN CSV. The profile
document's own serialization is unchanged and remains canonical in every
respect** — sorted keys, fixed separators, one shortest-round-trip
spelling per number, and ISO 8601 with explicit offset and fixed
precision.

1. **Twin datetime cells are written at the precision the profile
   records, not always with an explicit offset.** The profiler
   legitimately publishes offsetless dates and quarter values, recording
   their offset as `(none)`, so a twin obeying the unconditional rule
   could not reproduce them: a date-only column would gain a time and a
   zone it never had, and a quarter column could not be written at all.
   A twin datetime cell is therefore written in the ISO form matching
   the recorded precision — a date-only column writes `2024-03-15`, a
   quarter column writes `2024-Q1` — and an offset is written only where
   the profile records a real one. Rationale: the twin re-profiles to
   the same precision and offset state, so date-handling code developed
   against it behaves the same on the real table.
2. **Twin numeric cells may carry more than one spelling of the same
   value, from a bounded family.** A real table that wrote some cells
   `0` and others `00` publishes a raw distinct count that one canonical
   spelling cannot reproduce. The permitted family is the canonical
   spelling plus leading-zero and leading-plus forms of the same value,
   which measurement confirms ordinary readers parse to the same number
   while keeping a whole-number column whole-number. Where a profile
   also records fold-collapsing spellings, case-varied exponent forms
   are permitted for that purpose alone. No other form is permitted, and
   an alternate spelling is used ONLY where the published counts require
   it.
3. **Identifier values are drawn without replacement except in one
   named infeasible corner.** The bullet above requires identifiers
   drawn without replacement. Where a declared identifier's published
   length range and its all-different fact cannot both be satisfied, the
   owner directed that the published length wins and the necessary
   minimum of values repeat, with the loss named in the generation
   report. This exception applies to no other role and to no feasible
   case.

The Phase 2 plan carries each exception's consequences, disclosures and
tests. A future phase that finds an exception unnecessary retires it by
a further dated amendment here, never by silence.

## D13. Data-provenance guard — fully enumerated

- **Policy:** no real data and no real-derived artifact (profiles, schema
  files, category inventories, statistics computed from real data) ever
  enters the repository. Test fixtures are generated by seeded neutral
  scripts committed as code; a committed fixture is allowed only if tiny
  and listed in the **fixture manifest** binding path → generating script
  → seed → SHA-256.
- **CI provenance job:** re-runs the generator for every committed fixture and
  **byte-compares** it; fails on any tracked data-format file (`.csv`,
  `.parquet`, `.xlsx`, archives, etc.) absent from the allowlist; every
  allowlist entry carries a written justification. Mutations: an inserted
  non-allowlisted data file red; **allowlisted-fixture content
  substitution** (forged header, changed bytes) red.
- **Pre-first-push sequencing (required acceptance step):** before the
  first public push the maintainer runs the full battery — decontamination
  scan over the whole tree **and all git objects reachable or not**
  (`git cat-file --batch-all-objects`), provenance scan, offline-static
  scan — and the run is recorded in a signed note whose digest is bound
  into the first attestation. The ongoing pre-push hook (one-command
  install) remains and is honestly labeled advisory.
- **All-objects history scan** repeats at every release.
- **Source-exposed-maintainer residual (round-4 F3 fix — the false
  machine-separation premise is withdrawn):** the maintainer's machine
  hosts the private prototype snapshot and its real-derived example
  artifacts in sibling folders; a common-word real value could be copied
  into ordinary source, and no machine-detectable control catches that
  class. Controls that actually exist: the D7 hashes-only handoff (no
  plaintext crosses into the repo tree); a standing `CONTRIBUTING.md`
  review rule — any commit adding literal string or numeric constants to
  `src/` or `tests/` carries an explicit checklist line "no value copied
  from private artifacts", checked in adversarial review; the fixture
  regeneration guard for data files; and the D2/D13 policy that real data
  itself never exists on this machine (only the compliant environment).
  The residual is stated in `SECURITY.md` in exactly these terms.
- **Incident procedure** (in `SECURITY.md`): if real-derived content
  reaches public history — history rewrite + force push + provider cache/
  PR-ref purge request; institutional notification per policy; CHANGELOG
  record; the leaked surface's shape added to D7/D13 checks.

## D14. Repository governance (accepted in round 3; restated)

- Default branch ruleset: PR-only; required context = exactly the `gate`
  check, bound to the GitHub Actions app; force-push and deletion blocked;
  no bypass actors; self-merge after green gate permitted (one human).
- Tags `v*`: creation, update, deletion restricted; release tags signed;
  signing key recorded in `SECURITY.md`.
- Status of the two ruleset bullets above: they specify what is applied,
  not what is in force today. Both are deferred behind the visibility
  flip as items 1-8 of the owner-decision records at the end of this
  plan, and neither is active while the repository is private.
- Workflows: default token `contents: read` (verified active at the
  repository level on 2026-08-07, see the owner-decision records at the
  end of this plan); no `pull_request_target`; fork workflows require
  approval (unavailable while the repository is private; deferred as
  item 9 of those records); any PR touching `.github/workflows/**`
  or `tools/**` is CI-labeled and listed in the next release's notes.
- Account: 2FA enforced (owner-confirmed 2026-08-07, dated attestation,
  not API-verified); offline recovery codes and no shared credentials
  remain the intended practice but carry no owner attestation yet, so
  they are not claimed as confirmed controls (see the owner-decision
  records at the end of this plan).
- **Narrowed claim (accepted):** these controls resist third-party
  tampering. A compromised maintainer account or dishonest maintainer is
  a residual risk a one-person project cannot eliminate; compensating,
  user-verifiable controls: signed tags, SHA-pinned actions, the signed
  attestation chain, and — once releases exist — Trusted Publishing
  provenance binding artifacts to source commits. No insider-resistance
  is claimed.

---

## Acceptance criteria

1. **D2:** the owner's recorded waiver of the institutional-determination
   precondition (D2, 2026-08-07) is present in this plan; the repo's
   README license section records that the work is released on the
   owner's authority as non-commercial research tooling.
2. Governance in the private-mode form recorded in the owner-decision
   records at the end of this plan: the repository workflow-permission
   settings are verified through the settings API and read back as
   `read` with pull-request-review approval disabled; two-factor
   authentication rests on the owner's dated confirmation, since the
   setting is not exposed to the automation token; and the nine
   deferred items - the eight branch and tag ruleset controls
   (app-bound `gate` and tag protections among them) plus fork
   pull-request run approval - are applied and verified through the
   rulesets and settings API at the visibility flip, each with its
   recorded API reason for deferral.
3. Editable install, import, `synthtwin --version` run under the guard;
   the containerized network-unavailable build produces wheel + sdist
   whose contents match the allowlist; the wheel installs and smokes in a
   fresh offline-guarded venv; the executing build closure matches the
   lock; the build-egress mutation is red.
4. Runtime dependency set empty; lockfile (incl. build closure) present
   and consumed frozen.
5. Decontamination: Class-A manifest (full entries + distinctive tokens +
   protected subphrases) with header (count, `n_max`); the discriminative
   rule demonstrably applied to **all** surfaces including code literals;
   deterministic decoder + binary classifier with the full mutation
   battery red/green as specified (including no-NUL control-byte binary
   and transplanted-token mutations); **every tracked file in the initial
   tree scans clean with zero exemptions**; signed attestation valid
   against the pinned key with all recomputable digests matching and the
   reviewer's inventory-review digest bound; unsigned and wrong-key
   attestation mutations red; private-notes path resolves outside the
   repo root.
6. Offline: exact API-granular allowlist enforced; all nine D6.5 mutation
   classes red; socket-guard self-test red; per-platform path tests pass —
   UNC, device forms, and the Windows link test asserting resolution is
   never invoked.
7. Provenance: fixture manifest + regeneration byte-compare; both
   mutations red; all-objects scan clean; pre-first-push battery run
   recorded and bound into the first attestation.
8. Docs present and consistent with this revision, including every named
   residual (Class B, network mounts, TOCTOU, printable-binary,
   source-exposed maintainer, compromised maintainer, and
   caller-supplied code per D6 Amendment A3) stated where D8
   places it, with A3's best-effort, non-universal scope sentence
   accompanying the caller-supplied-code residual; sanitized canonical
   briefs in place; parent copies retired.

## Review record

Five review rounds (the full authorized cycle) are recorded in `reviews/`.
Round-5 final verdict: **approve-with-conditions**; conditions C1–C7 are
applied verbatim in this revision. Per that verdict, implementation may
begin under this conditioned plan without a further plan-review round.
Gate sequence before any code: (1) the D2 institutional authorization;
(2) the C1 Class-A freeze gate, including zero-match scans of this plan
and the round-4 response under the frozen artifacts; then implementation,
with the reviewer's remaining role being code review against this plan.

## D7 Amendment A1 — classifier v2 (ratified by inventory-review round 2, conditions applied)

The independent inventory review required by D7 (round 1, recorded in the
maintainer-private notes) **rejected classifier v1**: a neutral-source
common-word list alone cleared expressly denied vocabulary whose tokens
collide with ordinary English or arbitrary code identifiers, an
institution-identifying comment line, short roster literals, and
real-derived value fingerprints; the tokenizer dropped Unicode
compatibility forms instead of normalizing them; the decoder predated and
omitted the C3 byte pipeline; the scanner constructed fewer candidate
surfaces than the extractor; and digests were location-dependent. This
amendment is the plan-level decision replacing D7's single
distinctiveness rule with a **three-layer classifier**:

- **L1 — curated denial seed** (maintainer-private artifact, digest
  attestation-bound): the charter's expressly enumerated denial terms,
  the study's exposure vocabulary, and source-institution identifiers.
  Seed entries enter the manifest unconditionally and a surface
  containing one is Class A regardless of the other layers. Per the
  round-2 seed audit (R2-C4), L1 explicitly covers the full reviewed
  exposure and pharmaceutical-class policy set and the one reviewed
  prototype-derived column exception; the reviewer authorized exactly
  five additions by hash and rejected one candidate. Unlike the word
  list, this artifact is curated *by policy*, independently reviewed,
  and frozen; any change is a plan-level decision.
- **L2 — structural protections** (final rule ratified by round 2,
  R2-C3): every data-row first-field value of every snapshot structured
  artifact (the full roster, any token length); every other cell with a
  distinctive token; and every other cell of three or more tokens, with
  no further condition. **Named residuals, stated exactly** (ratified):
  bare one-to-five digit numeric fragments, and one- or two-token cells
  composed entirely of L3-nondistinctive tokens (word-list members
  and/or pattern-rule tokens) — explicitly including two-token numeric
  decimal/statistic sequences and mixed common/pattern pairs. Denying
  those would collide with every version number and decimal in any
  public file; they are assigned to the D13 contributor-review controls
  and disclosed in D8.
- **L3 — the word-list rule** as before, with two corrections: the
  tokenizer is Unicode-correct (compatibility forms normalize before
  matching), and numeric tokens of six or more digits are eligible for
  distinctiveness (seeds, date anchors, and long identifiers are denied;
  short numerics remain an L2 residual). The pattern rules are reframed
  as **policy residuals**, not safety proofs.

Further v2 corrections, all per the round-1 review: the extraction corpus
is every snapshot file with no exclusions (binary files contribute
printable-run surfaces); extractor and scanner share one surface module
so their **text-surface** candidate sets are identical by construction,
while binary files deliberately differ — printable-run extraction on the
private side, fail-closed violation on the public scan side; the C3
decoder
pipeline and the frozen magic table are implemented and were frozen
before the v2 extraction code was written; all tree digests use
root-relative, length-delimited serialization; and every remediation edit
made to pass a scan is recorded in a value-silent ledger with pre- and
post-edit digests. The review-history files in `reviews/` retain their
original bytes; their generic-token matches await reviewer-controlled
wording normalization after v2 ratification, per the round-1 ruling. One
extraction-rule revision (the L2 cell rule stated above) was made after
tree-scan results exposed the short-numeric false-positive class and is
disclosed as such in the extractor and the remediation record; the frozen
artifacts themselves were not touched.

This amendment takes effect only on ratification by inventory-review
round 2, which also rules on the wording-normalization step for the
review history. Status: ratified by inventory-review round 2 on
2026-08-07 with conditions R2-C1..R2-C7, which are applied; the private
review record binds this ratification.

## D14 Amendment A2 — sensitive-path surfacing (ratified by code-review round 3)

D14 as ratified requires that any pull request touching
`.github/workflows/**` or `tools/**` is CI-labeled and listed in the
next release's notes. This amendment replaces the label with a
different surfacing mechanism: on pull requests, CI emits a non-failing
warning annotation and writes the changed sensitive paths to the step
summary; an error while computing the path comparison fails the job;
and at release time, sensitive-path changes are collected from the git
history for the release notes. The reason is deliberate: applying a
label requires widening the workflow token beyond `contents: read`,
and D14 values the read-only token higher than the label. Status:
ratified by code-review round 3 on 2026-08-07; the replacement
mechanism is in effect and described in SECURITY.md.

## D6 Amendment A3 — the static scanner's honest contract (ratified with conditions by the Phase 0 closure review)

Code-review round 5 demonstrated, with runnable probes, four construct
classes that this scanner does not resolve to an exact enumerated API:
a subclass of a built-in type passes an isinstance gate and overrides
its methods; a call chained onto a constructor in one expression evades
name tracking; an allowed library API invokes methods on
caller-supplied objects; and decorators and class construction dispatch
code the scanner does not follow. The accurate premise of this
amendment is therefore about this scanner, not about static analysis in
general: this scanner does not establish universal call-target closure
for those four classes. A reading-only analysis could in principle
reject every construct it cannot resolve; ours accepts some of them on
purpose, because rejecting them would require a source dialect so
restrictive that the tool would stop being usable. The project accepts
that bounded gap, with the residual named below, instead of adopting
that dialect. The reviewer's round-5 ruling required a new reviewable
design or a materially narrower contract.

**What this supersedes in D6.2.** D6.2 says, in its positive runtime
import policy: "Every import binding, module-rooted attribute read or
write, subscript into module/function state, and call target must
resolve statically to an exact enumerated API; indirect or dynamically
manufactured call/attribute targets are rejected." A3 supersedes the
universal reach of that sentence - the claim that *every* call target
resolves statically to an exact enumerated API - for the four construct
classes named above, and it supersedes the same universal reading
wherever D6.2's exactness language is quoted as a closure proof.
Nothing D6.2 enforces is withdrawn: the exact API-granular allowlist,
the `importlib.metadata.version()`-only rule and the banned
`EntryPoint`/`entry_points`/`.load(` tokens, the bans on reads and
writes of `sys.modules` and `sys.path`, the ban on dunder-state
traversal and on the listed reflection primitives, alias tracing to
origin, and every listed mutation including the two reflective ones all
remain in force and unweakened. A3 changes the claim, not the
enforcement.

**This amendment adopts the narrower contract.** The offline static
scanner is a best-effort static analysis layer: a strong,
mutation-tested automatic check over a fully attribute-enumerated
allowlist, with the audited callback-slot table, union-set origin
tracking, and the type-gate rule — one defensive layer inside the D6
boundary (source audit + layered checks + network-isolated deployment),
not a proof of universal call-target closure. Nothing in the scanner is
weakened by this amendment; every mutation and rule stays. What changes
is the claim.

**Named residual, stated exactly:** code supplied BY THE CALLER (a
booby-trapped object or callable handed to synthtwin's public
functions) runs in the caller's own process under the caller's own
authority. The boundary governs what synthtwin's own code initiates; it
does not govern the caller against themselves. This is the same
residual family as the two limits the ratified D6 already accepts:
local-actor races between check and use, and transparent network
mounts. This amendment requires that residual, and the best-effort
non-universal scope of the scanner, to be recorded in D8's contents
list, in acceptance criterion 8, and in `SECURITY.md` beside those two
residuals, in these terms.

Status: authorized by the project owner on 2026-08-07; **ratified with
conditions** by the Phase 0 closure review on 2026-08-07. The
conditions are that review's C1 text-alignment items: the explicit
D6.2 supersession above, the corrected premise above, the residual
recorded in D8, in acceptance criterion 8, and in `SECURITY.md`, and
the matching wording in the scanner, product, diagnostic, and test
prose. With those conditions applied, this amendment is in effect and
governs the public claim; the scanner's rules and mutations are
unchanged by it.

## Owner decisions recorded at Phase 0 closure

- **Repository visibility (2026-08-07):** the repository remains
  private until the owner judges the application readier for public
  release; the public-from-first-build principle is deferred by owner
  authority, by the same mechanism as the D2 waiver. Phase 0 acceptance
  closes in private-mode form, with the items enumerated below as
  deferred behind the visibility flip and applied at the moment of that
  flip. CI runs on metered private-tier minutes meanwhile.
- **Deferred behind the visibility flip - nine items, exactly.** Items
  1-8 are the D14 branch and tag ruleset controls. On this account tier
  a branch or tag ruleset cannot be created on a private repository:
  the rulesets API answers HTTP 403, "Upgrade to GitHub Pro or make
  this repository public". That API reason is the recorded evidence for
  their deferral.
  1. repository visibility and API confirmation;
  2. default-branch PR-only enforcement;
  3. required context exactly `gate`, bound to the GitHub Actions app;
  4. force-push and deletion blocks;
  5. no bypass actors;
  6. self-merge only after a green gate;
  7. `v*` creation, update, and deletion restrictions; and
  8. signed release tags and the signing-key record when releases
     begin.

  The ninth item is added by this closure review:

  9. fork pull-request run approval (D14's "fork workflows require
     approval"). Setting it through the Actions permissions API answers
     HTTP 422, "Fork PR approval is not allowed for private
     repositories", so the control is structurally unavailable while
     the repository is private. That API reason is the recorded
     evidence for its deferral.

  Every one of the nine is re-verified through the settings and
  rulesets API at the visibility flip, and none of them may be
  described as active in any public document before then.
- **Settings verified active now (2026-08-07, GitHub settings API):**
  the repository Actions default workflow permissions read back as
  `default_workflow_permissions = "read"`, and workflow runs may not
  approve pull request reviews
  (`can_approve_pull_request_reviews = false`). The API response of
  that date is the evidence for both. They hold at the repository
  level, independently of the `contents: read` declaration the
  checked-in workflow makes for itself, so a later workflow that omits
  its own declaration inherits the read-only default. These two are not
  deferred; they are re-read at the visibility flip with the nine items
  above. Durable evidence: the full API readback -- endpoint URL, GitHub's own
  `Date` and `x-github-request-id` response headers, the repository's
  `node_id` and `full_name`, and the verbatim bodies for the Actions
  permissions, fork-approval (HTTP 422), and rulesets (HTTP 403)
  endpoints -- is retained MINIMIZED as a signed maintainer-private artifact
  (six repository-identity fields, the per-call provenance headers, and the
  verbatim governance bodies; the full repository body is deliberately NOT
  retained because for a private repository it carries a short-lived clone
  credential -- see the evidence-hygiene record),
  `decontamination/out/settings-readback-v2.json`, bound by digest in the
  public attestation. Any account with read access reproduces it with
  the `gh api ... --include` commands recorded inside it.
- **Account controls (2026-08-07):** the owner confirmed two-factor
  authentication is enabled on the hosting account. That setting is not
  exposed to the automation token, so this is a dated owner
  attestation, not API verification. The owner's dated confirmation
  covers two-factor authentication only. D14's offline recovery codes
  and its no-shared-credentials statement are not attested by the
  owner, so neither is claimed as confirmed in this plan or in any
  public document until a dated owner statement covers it.
  Re-verification of all three is due at the visibility flip.

## Phase 0 closure — owner decision, 2026-08-07

The adversarial review cycles for Phase 0 are **ended by owner decision**.
Their record is complete and public: five plan-review rounds, two
decontamination-inventory rounds, five code-review rounds, and four closure
rounds, with every response document retained.

**What the cycles delivered, substantively:** the ratified plan and
classifier; a scanner, provenance guard, path validator and network tripwire
each with red mutation tests; a CI gate set that runs green on three
operating systems and five Python versions including a network-disabled
container build; a signed evidence chain; and a series of genuine defects
found and fixed - a workflow that could not parse at all, checkout settings
that silently broke signed digests on one platform, several scanner bypasses
demonstrated with runnable probes, and a short-lived repository credential
that an evidence artifact had over-retained.

**What remained when the cycle was stopped:** documentation-wording
consistency of one kind - places where a control that is deferred until the
repository becomes public could still be read as active. The last rounds
repaired these in the plan, the security policy, the contributor guide, the
changelog, the workflow, the hook installer and the provenance tooling; any
survivor is a labeling defect in prose, not a gap in a control, and is
corrected on sight.

**Standing rules that outlive the cycle.** The deferred controls listed in
the owner-decision records and SECURITY.md are applied and verified through
the settings API at the visibility flip. The binding resolver
(`decontamination/resolve_bindings.py`) runs with every evidence refresh and
fails if any signed binding does not resolve to exactly one retained,
correctly signed file - the control that makes a dangling record impossible
to miss. Post-commit records use immutable per-head filenames and are never
overwritten. Evidence artifacts retain only the fields their claim needs.

**Phase 0 is closed on this basis.** Phase 1 planning proceeds under the
same plan-first discipline: its draft plan is reviewed before any Phase 1
code is written.

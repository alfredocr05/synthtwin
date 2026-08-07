# Security

This document states what synthtwin defends against, how each defense is
built, what it deliberately does not defend against, and how an outside
auditor can check every claim. Phase 0 commits only to what Phase 0 can
demonstrate; anything that arrives in a later phase is tagged
**[planned]**.

## Threat model, in plain language

synthtwin exists for people whose records must never leak. Two threats
are in scope:

- **Theft** - real data, or values computed from real data, leaving the
  user's machine, or entering this public repository through the
  development process.
- **Tampering** - a third party altering the code or artifacts that a
  user downloads and runs.

Explicitly **out of scope**: statistical disclosure. synthtwin does not
claim differential privacy and makes no promise about inference attacks
on a synthetic output you choose to share. The defense against exposure
is architectural: the real data never has to move, and nothing from any
real dataset is permitted to exist in this project's code, tests, or
history. Also out of scope: a hostile local operating system - the tool
defends data from itself, not from an attacker who already controls the
machine it runs on.

## The offline guarantee

The boundary statement: synthtwin's own code contains no construct that
initiates network I/O, no subprocess execution, no native-code calls, and
no dynamic code loading; it accepts only local filesystem paths; it is
fully functional air-gapped. Verification is source audit plus the
layered checks below - explicitly **not** an OS-level sandbox.
Institutions requiring enforcement rather than assurance run synthtwin
inside their own network-isolated environment.

The layers:

1. **Path locality rule.** Every input, output, and temp path is checked
   lexically *before any filesystem call*: URL schemes (`scheme://`),
   Windows UNC forms (`\\server`, `//server`), and Windows device or
   namespace forms (`\\.\`, `\\?\`) are rejected with a plain-language
   error. On Windows, every existing path component is examined without
   following it; any link (symlink, junction, mount point) causes
   rejection, and the target is never read or resolved, so no remote
   traversal can occur. On POSIX, symlinks are permitted and the resolved
   real path is re-checked against the lexical rules.
2. **Positive import allowlist.** Source under `src/` may use only an
   exact, enumerated list of standard-library APIs - no third-party
   imports exist in Phase 0. An AST-level scanner (`tools/offline_scan`)
   enforces the list and additionally bans dynamic import, entry-point
   loading, reflection primitives, and writes to interpreter state.
   Adding an API to the list is a plan-level decision with a capability
   audit.
3. **Socket guard.** The test suite installs a Python-level guard at
   collection time that makes any attempted network connection fail
   loudly. It is described everywhere as a guard - never as "network
   disabled" - and its self-test proves it fires on a deliberate
   connection attempt.
4. **Packaged-artifact smoke test.** The wheel produced by the
   network-unavailable build (below) is installed into a fresh virtual
   environment with the guard active; the CLI runs; the wheel and sdist
   contents must match an explicit file allowlist.
5. **Red mutation demos.** For every bypass class the guarantee promises
   to close - disallowed import, dynamic import, entry-point loading,
   process launch, native call, URL input, UNC input, Windows
   link-component input, build-container egress - CI demonstrates that a
   deliberate violation turns red.

## Named residual risks

Stated here so that no reader has to discover them independently:

- **OS-transparent network mounts.** If the operating system presents a
  network share as an ordinary local path, no portable program can
  detect that. Mount configuration is part of your environment, not
  something synthtwin can see.
- **Check-to-use races.** A hostile local process swapping a path between
  validation and use is outside the threat model, per the scope statement
  above.
- **Printable-only streams scanned as text.** The decontamination
  scanner's decoder treats any byte stream that survives its strict
  decoding rules as text, even if a human would call the file binary. No
  format-classification guarantee is made for that set; a protected token
  inside such a stream is still detected as text.
- **Short numeric fragments.** Bare numeric fragments of one to five
  digits cannot be denylisted without matching every version number and
  decimal in ordinary public files. They are handled by the
  contributor-review controls below, not by the scanner.
- **One- or two-token common cells.** Cells composed entirely of common
  words and/or pattern-rule tokens (for example a two-token decimal
  sequence) fall below the distinctiveness threshold for the same reason
  and are likewise assigned to the contributor-review controls.
- **Source-exposed maintainer.** The maintainer's machine hosts the
  private prototype snapshot and its example artifacts in sibling
  folders; a common-word real value could be copied into ordinary source,
  and no machine-detectable control catches that class. The controls that
  actually exist: the hashes-only handoff (no plaintext from the private
  side ever crosses into the repo tree); the standing review rule that
  any commit adding literal string or numeric constants to `src/` or
  `tests/` carries the checklist line "no value copied from private
  artifacts"; the fixture rebuild guard for data files; and the policy
  that real data itself never exists on this machine - only in the
  compliant environment.
- **Compromised maintainer account.** See the narrowed tamper claim under
  Governance below.

## Supply chain

Phase 0 ships **zero runtime dependencies**. The inventory by role, with
the question an auditor actually cares about answered per row:

| Role | Phase 0 contents | Executes on a user machine? | Pinned by |
| --- | --- | --- | --- |
| Runtime, direct | none | nothing to execute | - |
| Runtime, transitive | none | nothing to execute | - |
| Build frontend | `pip` / `python -m build` in CI | no | `build` is hash-locked in `requirements-dev.lock`, consumed frozen (CI fails on drift); `pip` ships with the runner interpreter, its exact version recorded in CI logs every run |
| Build backend | `hatchling` | only if you build from source yourself; never when installing a prebuilt wheel | hash-locked in `requirements-dev.lock`, which covers the complete build closure, consumed frozen (CI fails on drift) |
| Installer toolchain | the user's own `pip` | yes - it is your tool and a trust root you already hold | your environment |
| Artifact checker | `twine` (CI only) | no | hash-locked in `requirements-dev.lock`, consumed frozen (CI fails on drift) |
| Dev tools | `pytest`, `ruff`, `mypy` | no - contributor and CI machines only | hash-locked in `requirements-dev.lock` (floors declared in `requirements-dev.in`), consumed frozen (CI fails on drift) |
| CI platform | GitHub-hosted runner image; CPython installed by the SHA-pinned setup action; the runner's container runtime and git/OS tooling | no | **trust roots, not pins**: named concretely below the table; versions are echoed into the logs where the platform exposes them; a `-latest` label is never called a pin |
| Release tooling | none until the first release | - | - |

Everything pinnable is pinned (GitHub Actions by full commit SHA;
closures by hash); everything that cannot be pinned is named here as a
trust root rather than papered over. The unpinned trust roots, named
concretely:

- the GitHub-hosted runner image (its actual version is echoed into the
  logs from the runner context every run);
- the CPython interpreter installed by the SHA-pinned setup action (the
  exact interpreter and `pip` versions are recorded in the logs);
- the container runtime - the Docker engine the runner image provides -
  which starts the build container and enforces its `--network none`
  namespace;
- the git and OS tooling on the runner (checkout, shell, coreutils),
  which handle the repository before any hash-locked tool runs.

**The network-unavailable build [built].** The build job first verifies
and populates a local wheelhouse (wheels only, hash-required; source
distributions, VCS, editable, and local-path requirements are rejected,
so no build hook can execute before the boundary), then runs the entire
build inside a container started with `--network none` - an empty network
namespace, so no proxy, DNS, or egress of any kind exists for build code
at any level. The container image is the official CPython slim image,
pinned in `.github/workflows/ci.yml` as
`python:3.14-slim@sha256:a7fb1e634c4a578f9e0bd6327f11a3cde11b7a9395f48e24360c0988bcc5c2bc`
(the tag before `@` is human context only; the digest is the pin,
resolved from Docker Hub on 2026-08-07) - never a mutable tag alone; the
observed digest, in-container OS identity, and exact Python and pip
versions are verified and recorded. If the workflow's pinned digest ever
changes, this recorded value must change in the same commit. A deliberate HTTP fetch attempted
inside the same container must fail, demonstrated in a CI self-test.

**The supported institutional install path [planned].** The first
dependency-bearing release ships a generated `--require-hashes`
requirements file as a release artifact; CI installs from it into a fresh
offline-guarded environment and runs the smoke suite. That file is the
supported institutional install path. An ordinary `pip install synthtwin`
is governed by version bounds only and is documented as such.

## How an IT auditor verifies each layer

1. **Offline claim.** Read `src/` - in Phase 0 it is a handful of small
   files. Run the scanner in `tools/offline_scan` against `src/` and
   confirm it passes; make it fail by adding a disallowed import to a
   scratch copy. Run the test suite and confirm the socket-guard
   self-test fires on a deliberate connection.
2. **Zero runtime dependencies.** Open `pyproject.toml`; confirm
   `dependencies = []`.
3. **Path rules.** Run the test suite on your platform; the Windows cells
   run the complete path and link-rejection suite, including the
   assertion that resolution is never invoked on link-containing input.
4. **Decontamination.** Run the scanner in `tools/decontamination` over
   the whole tree and confirm zero matches; verify the attestation
   signature against the pinned public key; recompute every publicly
   computable digest the attestation binds and confirm they match.
5. **Provenance.** Run the checks in `tools/provenance`; confirm no
   data-format file is tracked outside the fixture manifest and that any
   committed fixture rebuilds byte-identically from its committed
   generating script and seed.
6. **Build integrity.** In the CI logs, compare the recorded container
   image digest, interpreter versions, and the executing-environment
   package listing against the committed lock; confirm the egress
   self-test failed as required.
7. **Governance.** Query the repository ruleset via the GitHub API:
   required status check exactly `gate`, bound to the GitHub Actions app;
   force-push and deletion blocked; no bypass actors. Read
   `.github/workflows/` and confirm every action is pinned by full commit
   SHA and the default token permission is `contents: read`.

## The decontamination model

synthtwin's development is informed by a maintainer-private prototype
built around a restricted study environment. Nothing from that
environment may appear in this public repository: no values, no column
vocabulary, no identifiers. The mechanism:

- **Hashed manifest.** The private inventory of protected terms never
  enters the repository. Only SHA-256 hashes of normalized entries - full
  entries, each distinctive token on its own, and designated protected
  subphrases - are committed. The public scanner
  (`tools/decontamination`) normalizes and tokenizes every tracked file,
  every path, and every code literal by one fixed rule and compares
  hashes; any match turns CI red. There are no content exemptions: every
  tracked file, plans and reviews included, must scan clean.
- **Signed attestation.** A maintainer-side coverage tool emits an
  attestation binding, by SHA-256: the private snapshot digest, the
  extraction script, the frozen common-word list and pattern grammar, the
  private inventory, the public manifest, the complete scanner tree, the
  coverage tool itself, the entry count and matching parameters, the
  result, and the digest of the independent inventory review. The
  attestation is signed with the maintainer's SSH key.
- **Pinned key.** The verifying public key is pinned in this repository
  at `tools/decontamination/allowed_signers` (recorded in the
  repository's initial history) and recorded here:
  `ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIAO6FlktnDKn0LNiJ+e6bnRTtWAj8nlTKoY7oFo2SWXD`,
  SHA256 fingerprint
  `SHA256:rR6ITL4F2JAdAnBaIocCCf1N8cY5NmPrIx7ZjyXCsPM`. Public CI
  verifies the signature against the pinned key and recomputes every
  publicly computable digest; any drift, missing signature, or wrong
  key is red.
- **What the signature means.** Within the narrowed claim below, the
  signature authenticates origin against third parties.
  Maintainer-key compromise is the stated residual.
- **Class-B residual.** Generic text made only of common words, short
  numerics, and pattern-shaped tokens (dates, decimals, version numbers)
  is *not* denylisted - denying it would match every ordinary public
  file. That class is governed by the contributor-review controls in
  `CONTRIBUTING.md` and by the incident procedure below, and it is the
  reason a zero-match public tree is achievable without exemptions.

## Governance and the narrowed tamper claim

Controls in force:

- Default branch: pull requests only; required status check exactly
  `gate` (an aggregate job that fails unless every CI job succeeded),
  bound to the GitHub Actions app; force-push and deletion blocked; no
  bypass actors; self-merge after a green gate is permitted - this is a
  one-human project.
- Tags matching `v*`: creation, update, and deletion restricted; release
  tags signed; the signing key will be recorded here when the first
  release exists.
- Workflows: default token permission `contents: read`; no
  `pull_request_target`; workflow runs from forks start only after the
  maintainer allows them; any pull request touching
  `.github/workflows/**` or `tools/**` is labeled in CI and listed in the
  next release's notes.
- Account: two-factor authentication enforced; recovery codes stored
  offline; no shared credentials.

**The narrowed claim, stated honestly:** these controls resist
*third-party* tampering. A compromised maintainer account, or a
dishonest maintainer, is a residual risk a one-person project cannot
eliminate. The compensating controls are the ones a user can verify
independently: signed tags, SHA-pinned actions, the signed attestation
chain, and - once releases exist - Trusted Publishing provenance binding
artifacts to source commits. No insider-resistance is claimed.

## Release integrity [planned]

No PyPI publication exists in Phase 0. The first release, whichever phase
makes it, requires: Trusted Publishing (OIDC, no long-lived tokens); PyPI
attestations; clean tagged builds from a protected release environment;
two independent builds compared for reproducibility; published artifact
hashes and SBOM; the hash-pinned install file if any runtime dependency
exists; and a demonstration that a signed tag is accepted while an
unsigned tag, a tag update, and a tag deletion are rejected.

## Incident procedure

If real-derived content ever reaches public history:

1. Rewrite history to remove it, force-push the cleaned history, and
   request cache and pull-request-reference purges from the hosting
   provider.
2. Notify the institution per its policy.
3. Record the incident in `CHANGELOG.md`.
4. Add the leaked surface's shape to the decontamination and provenance
   checks so the same class cannot recur undetected.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting: the **Security** tab of
<https://github.com/alfredocr05/synthtwin>, then **Report a
vulnerability**. Please do not open a public issue for a suspected
vulnerability. This is a one-person project; reports are acknowledged as
fast as one person can, normally within a few days.

# Security

This document states what synthtwin defends against, how each defense is
built, what it deliberately does not defend against, and how an outside
auditor can check every claim. It commits only to what the built phases
can demonstrate - Phase 0's security baseline, Phase 1's profiler and
Phase 2's generator; anything that arrives in a later phase is tagged
**[planned]**.

## Threat model, in plain language

synthtwin exists for people whose records must never leak. Two threats
are in scope:

- **Theft** - real data, or values computed from real data, leaving the
  user's machine, or entering this repository through the development
  process.
- **Tampering** - a third party altering the code or artifacts that a
  user downloads and runs.

Explicitly **out of scope**: statistical disclosure. synthtwin does not
claim differential privacy and makes no promise about inference attacks
on a synthetic output you choose to share. The defense against exposure
is architectural: the real data never has to move, and nothing from any
real dataset is permitted to exist in this project's code, tests, or
history. Read the first entry under "Named residual risks" below before
relying on that sentence - the twin is built without reading the table,
but that is a claim about provenance and not a claim that no twin row
equals a real row. Also out of scope: a hostile local operating system -
the tool defends data from itself, not from an attacker who already
controls the machine it runs on.

## The offline guarantee

The boundary statement: synthtwin's own code contains no construct that
initiates network I/O, no subprocess execution, no native-code calls, and
no dynamic code loading; it accepts only local filesystem paths; it is
fully functional air-gapped. Verification is source audit plus the
layered checks below - explicitly **not** an OS-level sandbox.
Institutions requiring enforcement rather than assurance run synthtwin
inside their own network-isolated environment.

What the boundary covers, said once and then relied on below: it governs
what synthtwin's **own** code initiates. It does not govern code that a
caller hands to synthtwin - that code runs in the caller's process under
the caller's own authority, and it is named as a residual risk below.
The automatic checks in layers 2 and 3 are best-effort layers inside this
boundary; the source audit, not any one scanner, is what carries the
boundary claim.

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
   exact, enumerated list of standard-library APIs, plus a named surface
   of exactly two third-party libraries: `pandas.read_csv`, which is
   additionally fenced by the rule described under the reader residual
   below, and `numpy.random.default_rng` together with the single
   drawing method `integers` on the stream it returns, which is the
   whole of what the generator uses and reaches no file, path or
   network. An AST-level scanner (`tools/offline_scan`) enforces the list
   and additionally bans dynamic import, entry-point loading, reflection
   primitives, and writes to interpreter state. Adding an API to the
   list is a plan-level decision with a capability audit.

   **The scope of this scanner, stated exactly.** It is a best-effort
   automatic layer inside the boundary above. It is *not* a proof that
   every call target in the program resolves to an exact allowed API. A
   reading-only analysis could in principle refuse every construct whose
   target it cannot resolve; this one deliberately does not, so that
   ordinary code stays writable. What it accepts, named rather than
   summarized: an object supplied by the caller that satisfies a type
   check; a call chained onto a constructor in one expression; and, on a
   value whose origin the audit cannot trace to an allowed API, the whole
   of **implicit protocol dispatch** - attribute and property reads,
   subscription, operators and comparisons, truth and length checks,
   iteration and conversion through accepted built-ins, formatting, and
   class or metaclass construction. Every one of those can run code
   belonging to the object, with no method-call expression anywhere in
   the source. What it refuses on such a value is the written method
   call; and the attributes of a value one of the enumerated libraries
   returned are themselves an enumerated list. So what this scanner does
   not prove is universal call-target closure, and it is not what holds
   the CSV reader to local files either - that is the run-time
   `validate_local_path` re-applied immediately before the reader is
   handed a path. Its strength is measured rather than asserted: every
   rule it holds is exercised by a deliberate red mutation in CI, and no
   rule was relaxed to make this scope statement true. (Plan D6
   Amendment A3, ratified with conditions by the Phase 0 closure review;
   the surface named above is the correction that Phase 1 review round 7
   required of the earlier, narrower statement.)
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

- **The record claim is a claim about provenance, and it is not a claim
  that no twin row equals a real row** (plan P2-D11). The generator is
  handed the profile and a seed and nothing else: it reads no source
  table, is never given a path to one, and samples or copies no row of
  one. That says where the twin's values come from. It is deliberately
  weaker than the categorical wording this project used to carry - a
  flat assertion that a twin holds nothing of yours - which was
  withdrawn everywhere in Phase 2, because reproducing published counts
  exactly can force a twin row to match a real one with nothing copied
  anywhere. The shortest true example: an
  11-row single-column table whose one label clears the small-cell floor
  publishes that label with the count 11, so the twin writes it in all
  11 rows, and each of those rows is a row the real table has. The same
  applies to any column whose published facts pin it completely. Two
  consequences follow and are stated rather than left to be worked out.
  synthtwin offers **no formal privacy guarantee** and claims no
  differential-privacy property; statistical disclosure is out of scope,
  as the threat model above says. And all three artifacts a full run
  produces - the profile, the twin and the report - carry facts computed
  from real data, so the institution's rules for real-derived material
  apply to all three, never to the profile alone.
- **What the twin carries, stated so that neither its risk nor its
  usefulness is overstated.** The twin reproduces the facts the profile
  publishes about each column ON ITS OWN. It carries no cross-column
  structure at all - no correlation between two columns, no formula
  tying one to another, no shared pattern of which cells are empty, no
  ordering between two event columns - and rows are treated as
  independent while the grain is undescribed: the profile never says
  what one row of the real table is. That is stated here for two
  reasons. It bounds what an attacker can reconstruct from a twin to
  the per-column facts the profile already published, which is the
  security-relevant half; and it bounds what a researcher may conclude
  from one, which is why the twin's own report repeats it on every run.
  Cross-column structure arrives in a later phase (Phase 5), and no
  surface of this project may describe it as present before it is.
- **The profile is computed from real data.** It holds no row of the
  table, but it is not anonymous: it publishes labels that at least
  `small_cell_floor` rows share (11 by default), the smallest and
  largest values of numeric columns and the points between them, and
  counts about groups nobody is named in. Handle it under your
  institution's rules for real-derived material - together with the twin
  and the report, per the entry above. Profile version 4 widened what it
  carries in exactly two ways, and each gets its own entry below rather
  than a clause here.
- **Version 4 publishes the exact spellings of the labels the profile
  already names** (plan P2-D0 owner decisions 9 and 11). Through version
  3 a label left the machine in one settled form only: the producer
  trims the ends and applies a Unicode case fold before pooling, so
  `A`, ` a ` and `a` were one published label and the file's own
  spellings stayed behind. From version 4 each PUBLISHED label
  additionally carries `variants` - a map from each exact spelling to
  how many rows wrote it that way - and `variants_withheld`, an
  anonymous map from an occurrence count to how many distinct spellings
  occurred that often. The generator cannot do without it: with the
  settled form alone, a column holding `A`, `a`, `B`, `b` comes back as
  `a, a, b, b` - four rows where the real column held four different
  values.

  **The delta is wider than "capitalization", and calling it that would
  understate it.** The fold is Python's `str.casefold()` applied after
  trimming, not an upper-to-lower mapping. So what version 4 publishes
  is every difference between two spellings BEFORE that fold: leading
  and trailing spacing, capitals, and the case-folding equivalences
  Unicode defines - which include pairs a reader would not predict, such
  as German `ß` and `SS`, which fold to the same identity and were
  therefore one published label in version 3 and are two named spellings
  in version 4 whenever both clear the floor.

  **What bounds it.** Every variant is governed by the same
  `small_cell_floor` as a whole label: a spelling fewer rows than the
  floor wrote is withheld and counted into `variants_withheld`, which
  names no spelling at all. Variants are forbidden on a label the floor
  itself withheld, and forbidden on every role that publishes no values
  - record numbers, free text, and numbers no format can hold. So no
  spelling crosses a line its own parent label had not already crossed,
  and the addition is bounded to labels the profile already publishes.
  It is still a real widening of the source text that leaves the
  machine. Text elsewhere in this repository saying that case and edge
  spacing are not preserved was true of version 3 and is wrong from
  version 4 on. The profiler's own summary states this on every run.
- **Version 4 publishes how a numeric column's values were written**
  (plan P2-D0 owner decision 10). Every column of counts and of measured
  numbers carries `numeric_styles`: a map from a spelling style to how
  many cells were written that way, over exactly six enumerated styles -
  `plain`, `leading_zero`, `leading_plus`, `decimal`, `exponent_lower`
  and `exponent_upper`. **The fact is about form, and carries no value.**
  It records that seventeen cells were written with a leading zero; it
  records neither which cells nor what any of them held, and no
  magnitude and no spelling appear in it. The small-cell floor governs
  it exactly as it governs a label: a style fewer rows than the floor
  used is withheld and pooled into a counted remainder, so a single
  oddly written cell cannot be singled out. It is published because
  without it three columns reading `0`, `0.0` and `0e0` produce
  byte-identical descriptions, while an ordinary reader infers a
  whole-number column from the first and a decimal column from the other
  two - so a generator working from the description alone would silently
  change the type of a column that code developed against the twin will
  meet on the real table.
- **OS-transparent network mounts.** If the operating system presents a
  network share as an ordinary local path, no portable program can
  detect that. Mount configuration is part of your environment, not
  something synthtwin can see.
- **Check-to-use races.** A hostile local process swapping a path between
  validation and use is outside the threat model, per the scope statement
  above.
- **A network-capable reader, fenced rather than unable.** The CSV
  reader synthtwin calls (`pandas.read_csv`) would open a URL or a
  remote storage location if it were handed one: the library is capable
  of network access even though synthtwin never asks it for any. Three
  controls hold that line, and they are what the offline claim rests on
  for this call. Two of them run at run time and they are the operative
  ones: every path reaching the reader has just passed
  `validate_local_path`, which refuses URL forms lexically before any
  file is opened, and the reader is handed the resulting path object
  rather than text the user typed. The third is the import scanner, a
  best-effort layer over those two: it enumerates `read_csv` and no
  other name from the library, so **no other pandas name can be written**
  in `src/`. That is narrower than "no other pandas API runs", and the
  difference is deliberate: reading an attribute of a value the library
  returned, subscripting it, or handing it to a built-in dispatches the
  library's own code without naming it, and `reading.py` does exactly
  that on every run (the frame's length, its `columns`, and a column by
  key). Attribute reads on returned values are held to an enumerated
  list and written method calls on them are refused; implicit dispatch
  is accepted on purpose and is the residual named above. The scanner
  also requires **every `read_csv` call site to carry,
  on its own, provenance the scanner recognizes** - the argument must
  trace, inside that same function, to `validate_local_path`. Be exact
  about what that does and does not mean: a second, correctly fenced
  call site scans clean and needs no plan-level change, while an
  unfenced one is refused wherever it is written. This is a fencing
  arrangement, not an inability. An
  institution that wants the inability rather than the fence runs
  synthtwin inside its own network-isolated environment, where the
  question does not arise. The same enumeration bans calling any method
  on the objects the library returns -- a data frame carries writers that
  reach a database or a URL on their own -- so those objects are read
  from and passed back to enumerated functions, never called through.
- **Code supplied by the caller.** A booby-trapped object or callable
  handed to one of synthtwin's public functions runs in the caller's own
  process under the caller's own authority. The boundary controls what
  synthtwin's own code initiates; it does not and cannot police the
  caller against themselves. Concretely: a subclass of a built-in type
  passes a type check and can override the very methods that check
  accepts, and the import-allowlist scanner reports no violation for
  that shape, because the overriding code is the caller's, not this
  project's. This is the same residual family as the two above - a
  property of the machine and the process the caller already controls,
  not a hole in synthtwin's code - and it is accepted on the same terms
  (plan D6 Amendment A3).
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

synthtwin has **two runtime dependencies**. pandas is justified in
writing in `docs/plans/phase-1-profiler.md` (P1-D2) and reduced by the
import scanner to exactly one function, `read_csv`, which may be called
only with a path the validator produced. numpy is justified in
`docs/plans/phase-2-generator.md` (P2-D8) and reduced to
`numpy.random.default_rng` and the one `integers` call on the stream it
returns; it is reachable only from the generator, which opens no file at
all. The inventory by role, with the question an auditor actually cares
about answered per row:

| Role | Contents | Executes on a user machine? | Pinned by |
| --- | --- | --- | --- |
| Runtime, direct | `pandas`, `numpy` | yes | bounds in `pyproject.toml` for an ordinary `pip install` (floors installed and tested by the `minimums` CI job); by hash in `requirements-install.lock` for the supported institutional install |
| Runtime, transitive | `python-dateutil`, `six`, `tzdata`, and (below Python 3.11) `pytz` - the closure pandas brings. numpy is in that closure too and is a declared direct dependency again as of Phase 2: it was withdrawn at Phase 1 review round 1 because its REDUCTIONS made published statistics depend on row order, and the profiler still computes those statistics itself in exact whole-number arithmetic, rounding once at the end. What returns is the generator's one random stream, reduced by the scanner to `default_rng` and one `integers` call | yes | by hash in `requirements-install.lock`; the complete closure is also in `requirements-dev.lock`, consumed frozen in CI |
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

**The supported institutional install path [built].**
`requirements-install.lock` pins the complete runtime closure by hash.
CI installs from it -- with `--require-hashes`, from a local wheelhouse,
with no index -- into a fresh virtual environment that has the socket
guard active, then installs the built WHEEL with `--no-index --no-deps`,
runs the command, and profiles a table built on the spot by a seeded
script. The wheel matters: installing from a source folder would make
pip fetch and execute a build backend that this lock does not pin, so
the documented procedure names the wheel and CI exercises exactly it. That
path is exercised on every run rather than described and never tried. An
ordinary `pip install synthtwin` is governed by version bounds only and
is documented as such. The bounds are not guesses: the `minimums` job
installs exactly the declared floors on the oldest supported interpreter
and runs the whole test suite against them.

## How an IT auditor verifies each layer

1. **Offline claim.** Read `src/` - it is still a small number of plain
   Python files. Run the scanner in `tools/offline_scan` against `src/`
   and confirm it passes; make it fail by adding a disallowed import to
   a scratch copy. Run the test suite and confirm the socket-guard
   self-test fires on a deliberate connection. Read the clean scan for
   what it is: the best-effort layer scoped above, so the source read is
   what carries the boundary claim, and the caller-supplied-code
   residual stays open either way. For the one network-capable API in
   the allowlist, read each `pandas.read_csv` call site in `src/` and
   confirm that the argument comes from `validate_local_path` in that
   same function; that run-time check, not the scan, is what holds the
   reader to local files.
2. **Two direct runtime dependencies.** Open `pyproject.toml`; confirm
   `dependencies` names pandas and numpy and nothing else.
   `python-dateutil` and the rest of the transitive row in the table
   above arrive inside pandas's own requirements, and
   `requirements-install.lock` pins the whole closure by hash. Then
   `grep -rn numpy src/`: every hit is in the generator, and every one
   of them is `numpy.random.default_rng` or the single `integers` call
   the method specification fixes -- the profiler, which is the half
   that reads the real table, imports numpy nowhere.
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
7. **Governance.** Read `.github/workflows/` and confirm every action is
   pinned by full commit SHA and that the workflow declares
   `contents: read` at the top level. Query the repository's Actions
   permissions through the GitHub API and confirm
   `default_workflow_permissions` is `read` and
   `can_approve_pull_request_reviews` is false. Do not expect a branch or
   tag ruleset to come back: those could not exist on the private
   repository, and the Governance section below records them as applied
   at the visibility flip
   with the exact API reason.

## The decontamination model

synthtwin's development is informed by a maintainer-private prototype
built around a restricted study environment. Nothing from that
environment may appear in this repository: no values, no column
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
  `SHA256:rR6ITL4F2JAdAnBaIocCCf1N8cY5NmPrIx7ZjyXCsPM`. CI verifies the
  signature against the pinned key and recomputes every publicly
  computable digest; any drift, missing signature, or wrong key is red.
- **What the signature means.** Within the narrowed claim below, the
  signature authenticates origin against third parties.
  Maintainer-key compromise is the stated residual.
- **Class-B residual.** Generic text made only of common words, short
  numerics, and pattern-shaped tokens (dates, decimals, version numbers)
  is *not* denylisted - denying it would match every ordinary public
  file. That class is governed by the contributor-review controls in
  `CONTRIBUTING.md` and by the incident procedure below, and it is the
  reason a zero-match tracked tree is achievable without exemptions.

## Governance and the narrowed tamper claim

The repository **goes public at Phase 3's visibility flip** - the owner
decision recorded in the Phase 3 plan, superseding the 2026-08-07
private-mode decision and executed the moment that plan landed on the
default branch (the open-source commitment itself is unchanged).
Private mode decided which governance controls could exist at all, so
this section separates what has been running all along from what the
flip applies. Nothing in the flip-applied list is in force until the
activation record below carries its API confirmation. Do not rely on
any of it before that.

### Controls active now

- **How changes reach the default branch.** Until the flip this was a
  one-maintainer private repository with no branch ruleset applied -
  direct pushes to the default branch by the maintainer, no pull
  request required - and the plan-landing commit itself travelled that
  way. From the flip, the ruleset in the activation record governs:
  pull requests only, the aggregate gate required, self-merge only
  after green. Every push runs the
  full CI gate and no change is treated as done until that gate is
  green, but nothing mechanically blocks a push whose gate later turns
  red. The pull-request-only enforcement is in the deferred list below.
- **Read-only Actions token (verified active).** The repository's
  Actions permissions were read back from the GitHub API on 2026-08-07:
  `default_workflow_permissions` is `read`, and
  `can_approve_pull_request_reviews` is false. That is the
  repository-wide default, so a workflow added later that omits its own
  permission block still receives a read-only token. The checked-in
  workflow additionally declares `permissions: contents: read` at its top
  level and uses no `pull_request_target` trigger. The readback is
  retained as a signed, digest-bound evidence artifact (endpoint URLs,
  GitHub's own response headers, and the repository's node identifier),
  and the exact commands to reproduce it are recorded inside that
  artifact; an auditor with read access can re-run them at any time.
- **SHA-pinned actions.** Every action reference under
  `.github/workflows/` is pinned by full commit SHA, and the build
  container image is pinned by digest, as recorded in the supply-chain
  section above.
- **Signed attestation chain.** The decontamination attestation is
  signed with the maintainer's SSH key and verified in CI against the
  key pinned in this repository; any drift, missing signature, or wrong
  key is red. See the decontamination section above.
- **The four guard jobs behind the aggregate gate.** `decontam`,
  `offline-static`, `provenance`, and `sensitive-paths` each run on
  every push and pull request, and the aggregate `gate` job goes green
  only when all eight jobs it depends on succeeded - a skipped or
  cancelled job counts there as a failure, not as a pass.
- **Sensitive-path surfacing.** For any pull request touching
  `.github/workflows/**` or `tools/**`, CI emits a non-failing warning
  annotation and writes the changed sensitive paths to the job's step
  summary; an error while computing that path comparison fails the job.
  At release time, sensitive-path changes are collected from the git
  history for the release notes. No label is applied, deliberately:
  applying a label would require widening the workflow token beyond
  `contents: read`, so no label-writing permission exists, and the
  read-only token is the control valued higher. This mechanism was
  ratified by code-review round 3 as plan amendment A2 and is in effect.
- **Account.** The owner confirmed on 2026-08-07 that two-factor
  authentication is enabled on the hosting account. That dated owner
  statement is the whole of the account claim: the automation token does
  not expose account settings, so this is not an independent API
  verification, and it is re-checked at the visibility flip. Two further
  account practices that an earlier version of this document listed -
  offline storage of recovery codes, and the absence of shared
  credentials - are **not yet attested by the owner** and are therefore
  not claimed here as active controls.

### Controls applied at the visibility flip

None of the following is in force until the activation record carries
its API confirmation. This account tier cannot create
branch or tag rulesets on a private repository at all: the rulesets API
refuses with HTTP 403, "Upgrade to GitHub Pro or make this repository
public." Each item below is applied and then confirmed through the API
at the moment of the visibility flip, and every setting in the active
list above is re-verified at that same moment.

The deferred branch and tag controls are exactly these eight:

1. repository visibility itself, and its confirmation through the API;
2. default-branch pull-requests-only enforcement;
3. a required status check that is exactly `gate` (the aggregate job
   that fails unless every other CI job succeeded), bound to the GitHub
   Actions app;
4. force-push and deletion blocks on the default branch;
5. no bypass actors on that ruleset;
6. self-merge permitted only after a green gate - this is a one-human
   project, so self-merge stays allowed, but only behind that condition;
7. `v*` tag creation, update, and deletion restrictions; and
8. signed release tags, with the signing key recorded in this document,
   once releases begin.

One further setting is deferred for its own recorded reason:

- **Fork pull-request run approval.** It cannot be set on a
  private repository: the API refuses the change with HTTP 422,
  "Fork PR approval is not allowed for private repositories." It is
  structurally unavailable rather than merely unset, and it is applied
  and verified at the visibility flip along with the eight items above.

**The narrowed claim, stated honestly:** the controls listed as active
resist *third-party* tampering. A compromised maintainer account, or a
dishonest maintainer, is a residual risk a one-person project cannot
eliminate. The compensating controls a user can verify independently
today are the SHA-pinned actions, the read-only workflow token, and the
signed attestation chain; signed release tags and - once releases exist -
Trusted Publishing provenance binding artifacts to source commits join
that list when the deferred items above are applied. No
insider-resistance is claimed.

## Release integrity [planned]

No PyPI publication exists in Phase 0. The first release, whichever phase
makes it, requires: Trusted Publishing (OIDC, no long-lived tokens); PyPI
attestations; clean tagged builds from a protected release environment;
two independent builds compared for reproducibility; published artifact
hashes and SBOM; the hash-pinned install file if any runtime dependency
exists; and a demonstration that a signed tag is accepted while an
unsigned tag, a tag update, and a tag deletion are rejected.

## Incident procedure

If real-derived content ever reaches the repository's pushed history:

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

That page opens to everyone at the visibility flip; before the flip it
was reachable only by accounts the owner had granted access.

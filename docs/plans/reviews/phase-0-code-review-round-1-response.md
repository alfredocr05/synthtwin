# Response to Phase 0 code review — round 1

Implementer's answers to `phase-0-code-review-round-1.md` (25 review items:
17 blockers, 6 majors, 2 minors). Every item is answered with a fix; none
is rebutted. The history was NOT pushed; the five commit messages the
review flagged were repaired in place before first publication.

**F1 (capability re-exports) — fixed.** The scanner now resolves every
module-rooted chain to an exact enumerated API: one attribute step past a
known module path, a module-name attribute block list (os.path.os and
friends), an underscore-attribute ban, a documented one-step rule for
intra-package modules, and rejection of module objects passed as bare
values. Red mutations added for the review's exact routes, including
`os.path.os.system` and the intra-package chain.

**F2 (flow-unsound binding) — fixed.** Bindings are flow-insensitive union
sets built by a scope pre-pass; a store never erases a module origin, so
conditional rebinding cannot clear suspicion. Bare-name call targets must
trace to defined code, an allowlisted origin, or an enumerated builtin;
callback parameters are banned in Phase 0 `src/` (documented). The
review's verbatim `if False` module and the unknown-callback case are red
mutations now.

**F3 (URL scheme charset) — fixed.** Scheme parsing accepts `+`, `-`,
and `.` per RFC 3986; `git+ssh://`, `a-b://`, and `a.b://` are red tests
covered by the no-filesystem-call spy.

**F4 (fail-open Windows walk) — fixed.** Only a missing component
continues the walk; every other OSError (permission, sharing) rejects
with a plain-language error. Red test simulates PermissionError and
asserts resolution never ran.

**F5 (skippable link mutation) — fixed.** The reparse walk is drivable
with an explicit platform argument; a never-skipping test runs the win32
walk on every OS with a mocked reparse attribute and asserts rejection
with zero resolution calls. Real-symlink integration tests remain
additionally.

**F6 (build hooks outside the boundary) — fixed.** The wheel is built
only inside the network-none container and travels to the test matrix as a
pinned-action artifact installed with `--no-index --no-deps`; the
offline-static and provenance jobs no longer install the project at all.
No project PEP 517 hook executes on a networked runner.

**F7 (lock-level source rejection + missing mutation) — fixed.**
`--only-binary :all:` is embedded in the requirements input and the
regenerated lock; a prefetch-boundary mutation builds a local source tree
whose metadata hook writes a sentinel and proves the download is refused
with the sentinel absent.

**F8 (missing image-pin mutations) — fixed.** Two inverted self-test
steps prove the tag-only-reference and wrong-observed-digest checks each
go red.

**F9 (allowlist rejects own artifacts) — fixed.** The wheel and sdist
allowlists now match the actual build output (paths module, signer file,
signature file); verified locally by building and running the workflow's
own checker: zero unexpected, zero missing.

**F10 (no shared surface implementation) — fixed.** `tokenizer.py` and
`surfaces.py` are now canonical public modules; the scanner imports them
and the private extraction pipeline imports THE SAME FILES from the
repository. The rebuilt private pipeline reproduced the ratified
2,065-entry inventory byte-for-byte, proving no semantic drift.

**F11 (unreproducible extraction chain) — fixed.** The private extractor
reads the final freeze record's actual schema and reruns cleanly; the
manifest header now carries the current digests, and header, freeze
record, and attestation agree (the verifier now cross-checks them).

**F12 (incomplete attestation graph) — fixed.** The scanner-tree digest
now covers all seven public files including the verifier and the pinned
signer file; the coverage battery and all-objects scan are permanent
digest-bound tools; the verifier recomputes the magic binding, counts the
actual manifest hash lines against the header and attestation, checks
header digest lines against attestation bindings, and rejects
duplicates. SECURITY.md records the public key and fingerprint. New red
tests: missing signature, wrong-key signature, forged header count.

**F13 (decontam job under-verifies; battery incomplete) — fixed.** The CI
decontam job now runs the scanner, the attestation verifier, and the full
self-test battery. The battery adds: malformed BOM, BOM-less wide
encodings, UTF-8-BOM Python AST recovery, enclosed compatibility
spellings, shell-line surfaces, unknown-magic printable survivors, four
magic signatures, and valid-BOM green paths.

**F14 (format gap) — fixed.** Nineteen further real-derived formats are
gated; `.json`/`.jsonl` are data formats permitted only for the two known
configuration files or manifest-listed fixtures, with red tests.

**F15 (history evidence chain) — fixed.** The permanent all-objects scan
covers blobs, commit messages, and tree entry names; the signed
pre-first-push note's digest is bound into the attestation; the
one-command advisory hook installer exists (`tools/hooks/install.sh`).

**F16 (missing checklist lines) — fixed.** The unpushed history was
rewritten in place: every commit adding literal constants under `src/` or
`tests/` now carries the required checklist line.

**F17 (unimplemented sensitive-path control) — fixed within the read-only
token.** A job now surfaces changes under `.github/workflows/**` or
`tools/**` as a prominent annotation and step-summary section; the
security document describes exactly that mechanism.

**F18 (fixture execution containment) — fixed.** Fixture and generator
paths must be repository-relative, tracked, and inside the tree; the
generator runs through a guard runner that stubs socket entry points
before the script executes; red tests cover absolute paths, `..` paths,
and a network-attempting generator.

**F19 (one-way closure comparison) — fixed.** The in-container comparison
now evaluates environment markers and compares both directions, reporting
exact differences.

**F20 (output not value-silent for filenames) — fixed.** Matched path
components are redacted with digest tags in every printed location; a
test asserts the canary never appears in scanner output.

**F21 (narrow spy) — fixed.** The lexical-order spy patches resolution,
lstat, getcwd, stat, and open, asserting none is touched on lexical
rejection.

**F22 (untested guard timing) — fixed.** A sentinel module records at
collection time what a connection attempt raises; moving the guard into a
fixture turns the sentinel test red.

**F23 (abstract supply-chain records) — fixed.** SECURITY.md records the
digest-pinned image reference, the named unpinned trust roots, the
hash-locked tool descriptions, and the attestation key with fingerprint.

**F24 (stale documentation) — fixed.** The determinism statement is tagged
as planned; the fixture exception is stated in the same sentence as the
no-data-files rule; the signer-history wording is corrected; the plan
amendment carries its ratification status line.

**F25 (weak CLI contract) — fixed.** `main` has a guarantee docstring;
the version test compares the exact metadata-backed version; a bad-flag
test pins the SystemExit contract.

**Deviation accounting.** The review noted the builder deviation lists
were not repository artifacts. The substantive deviations that survive
this round are now either implemented plan-conformant behavior or stated
in code/document comments where they live; the response and review files
are the repository record.

**Request to round 2:** verify the resolutions and the re-signed
attestation chain; the public-host items remain pending until the first
push, which waits for this cycle's clearance.

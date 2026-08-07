# Response to Phase 0 review — round 4

Implementer's answers to `phase-0-review-round-4.md` (4 new blockers, 4
carried blockers, 3 rulings). Plan revised to **revision 5 — fully
self-contained**: no decision is incorporated by reference to a superseded
draft (round-4 F4). Every finding accepted; the closed decisions (D12
single-stream, D7 signed attestation, D14 narrowing) are restated without
substantive change and not reopened.

**R3-F1 carried (Class A rejects the plan's own text) — accepted.** The
round-4 ruling's exact fix is adopted: the **same deterministic
distinctiveness rule now applies to every candidate surface, code literals
included** — a surface enters Class A only if it contains a token absent
from the frozen common-word list and not matching the frozen
numeric/date/quarter grammar. Generic code literals fall to Class B, whose
leak class is assigned to D13's real controls. Acceptance requires a
demonstrated zero-match initial tree with zero exemptions.

**R4-F1 (distinctive token not an emitted unit) — accepted.** The manifest
now emits, per Class-A surface: the full normalized entry, **each
distinctive token as its own entry**, and designated protected subphrases.
Transplanted-token mutations (new contexts, filenames, identifier
positions) are required red.

**R3-F2 carried (no binary classifier) — accepted.** A deterministic
classifier is specified: C0 control bytes outside {TAB, LF, CR} or a fixed
magic-number list ⇒ fail-closed to the provenance path. The genuinely
undecidable case — a "binary" made solely of printable bytes — is a
**named residual**: it is scanned as Latin-1 text, which still applies the
full matcher to its bytes. The battery adds the no-NUL control-byte binary
and magic-number archive disguised with text extensions.

**R3-F4 carried (build network not actually unavailable) — accepted.** The
build now runs inside a `--network none` container after a hash-verified
wheelhouse prefetch (`--no-index --find-links`), so process- and
native-level egress is closed by an empty network namespace, not by the
Python guard. Closure-vs-lock comparison and a build-egress mutation
(in-container fetch must fail) are acceptance items.

**R2-F2 carried (resolution-time remote traversal) — accepted.** Windows
paths are now checked component-wise with `os.lstat` and **any reparse
point is rejected without reading or following its target**; resolution is
invoked only after the walk finds none. The test asserts the resolution
call never occurs on link-containing input, not merely eventual rejection.
POSIX symlinks remain permitted with post-resolution revalidation (no
UNC/device forms exist there; mounts stay the named residual).

**R4-F2 (EntryPoint.load via allowed module) — accepted.** The allowlist is
now API-granular: from `importlib.metadata` only `version()`;
`EntryPoint`, `entry_points`, and `.load(` are banned scanner tokens; `sys`
is allowed excluding `sys.modules`/`sys.path` mutation, which the scanner
bans; `os` is limited to the named path/query functions. An entry-point
mutation joins the battery. Allowlist changes now require a capability
audit of the added API surface, not just a module name.

**R4-F3 (false machine-separation premise) — accepted; premise withdrawn.**
D13 now states the **source-exposed-maintainer residual** in plain terms:
the private prototype and its real-derived example artifacts live in
sibling folders on this machine, and no machine-detectable control catches
a common-word value hand-copied into ordinary source. The controls claimed
are only those that exist: hashes-only handoff into the repo tree, a
standing review-checklist rule for commits adding literal constants,
fixture regeneration for data files, and the fact that real data itself
exists only in the compliant environment. No separation is claimed that
the workspace does not have.

**R4-F4 (self-containment) — accepted.** Revision 5 restates every
normative decision in full — D3, D4, D9 (all eight jobs and the gate
enumerated), D10, D11, D12, D13, D14 — with no "as revision N" references.
Superseded drafts have no normative force.

**Rulings acknowledged:** D7 signed attestation — accepted within D14;
the snapshot-algorithm-inside-a-named-bound-tool note is incorporated.
D12 single-stream — accepted; restated verbatim in substance. Two-class
architecture — accepted; its implementation rule now matches the ruling's
three-point fix (rule applied to code literals; distinctive units emitted;
excluded surfaces assigned to controls that exist).

**Request to round 5 (final authorized round):** the plan asks one
question — whether the eight specified resolutions make revision 5
implementable and honest as written. Per the brief, approve or
approve-with-conditions (exact text edits) if so; request changes with the
specific failing text if not.

# Phase 0 plan review — round 4

**Reviewed:** `docs/plans/phase-0-public-skeleton.md` (revision 4), the
round-3 response, every requested carryover, the charter, and the relevant
read-only prototype surfaces  
**Verdict:** **request changes**  
**New finding count:** 4 — 4 blockers

Revision 4 makes two decisions cleanly: D12 now honors the literal one-RNG
charter, and D7's signed attestation is acceptable inside D14's already accepted
narrow threat model. It does not close the plan. The wordlist exception applies
only to documentation/value surfaces while every prototype code literal remains
unconditionally Class A; that mandatory subset alone rejects both revision 4
and its response. The prior path, binary-decoder, and offline-build gaps also
remain, and revision 4 introduces four additional concrete defects.

## Resolution of every round-3 finding

| Round-3 finding | Status | One-line evidence from revision 4 |
|---|---|---|
| **R3-F1 — self-failing inventory** | **Unresolved** | D7 lines 126–134 filters only documentation/value surfaces; all AST string literals remain Class A, producing 41 distinct mandatory-Class-A matches in the plan and 24 in the response despite acceptance lines 142–144 and 297–303 requiring a clean tree. |
| **R3-F2 — decoder false negative** | **Partially-resolved** | Lines 145–151 correctly make UTF-16/32 BOM-only and otherwise choose strict UTF-8 then Latin-1, but merely assert that every binary/archive is recognized; no classifier distinguishes a no-NUL binary from Latin-1 text. |
| **R3-F3 — self-asserted attestation** | **Resolved** | Lines 157–179 sign the attestation, bind the complete listed input/tool/review graph without a self-digest, enumerate refresh triggers, and make missing/wrong-key signatures fail; this is sufficient under D14's accepted maintainer-key-compromise residual. |
| **R3-F4 — build-isolation bypass** | **Partially-resolved** | Lines 59–67 lock the frontend/backend closure and use `--no-isolation`, but omit the required prefetch plus network-unavailable build; a Python socket guard and absent proxy variables do not close process/native egress from build code. |
| **R3-F5 — keyed RNG underspecification** | **Resolved** | Lines 219–232 remove keyed child generators, require one threaded `Generator`, and allow a keyed design only after an owner-ratified charter amendment carrying every previously missing executable detail and vectors. |
| **R3-F6 — negative authorization loophole** | **Resolved** | D2 lines 28–34 and acceptance lines 286–289 require affirmative authority for public MIT release and halt the project on a negative new-work determination. |

Result: **3 resolved, 2 partially-resolved, 1 unresolved.**

## Resolution of every requested carried partial

| Carried finding | Status | One-line evidence from revision 4 |
|---|---|---|
| **R2-F2 — path locality** | **Partially-resolved** | Lines 87–98 fix direct lexical checks and name mount/TOCTOU limits, but `Path.resolve()` can follow a local Windows link/junction into a UNC target before the post-resolution rejection; acceptance checks rejection, not absence of the network attempt. |
| **R2-F3 — capability enforcement** | **Partially-resolved** | Lines 99–117 give a normative module list and named mutations, but the allowlisted `importlib.metadata` module exposes `EntryPoint.load()`, an unlisted dynamic-loader route. |
| **R2-F5 — matcher contract** | **Partially-resolved** | Lines 145–156 fix codec precedence, identifier-splitting order, and manifest-driven `n_max`; binary/archive detection and distinctive-token emission remain undefined. |
| **R2-F6 — inventory completeness/proof** | **Partially-resolved** | Lines 123–179 bind a complete-snapshot workflow and signed proof, but the mandatory corpus is not self-clean and a distinctive token inside a longer surface is not itself required in the manifest. |
| **R2-F8 — byte-identity scope** | **Resolved** | Lines 233–245 limit guaranteed bytes to identical inputs/version/exact closure on the same platform, describe cross-platform equality only as a tested matrix result, and retain only the statistical contract across NumPy changes. |
| **R2-F9 — provenance depth** | **Partially-resolved** | Lines 253–270 add required pre-first-push/all-object checks and regeneration, but assign the Class-B leak residual to a workspace premise contradicted by the adjacent real-derived prototype artifacts already on this machine. |
| **R2-F7 / carried round-1 F9 — determinism** | **Resolved** | Lines 208–245 adopt literal single-stream use, ordered/schema-driven consumption, pre-implementation independent vectors for every rebaseline, scoped byte identity, and canonical serialization. |

## Rulings on the three round-4 questions

### 1. Two-class inventory — **not accepted as written**

The architectural split is acceptable: common-word/numeric-only surfaces are
not disqualifying merely because they came from a displayed value, and a named,
bounded residual can be assigned to provenance controls. The implementation
rule is not acceptable yet for three independent reasons:

1. D7 lines 126–134 makes every code literal Class A without applying the
   distinctiveness filter, so the promised initial tree cannot pass its own
   acceptance test.
2. A whole surface enters Class A when it contains one distinctive token, but
   lines 152–155 require only full-entry matching; the distinctive token is not
   itself required to be emitted.
3. The Class-B control at lines 263–270 relies partly on no real-derived material
   being present on this machine, while the audited workspace already contains
   adjacent prototype profile artifacts of that kind.

The exact fix is to apply an executable discriminative rule to code literals as
well, emit each distinctive token (or explicitly defined distinctive subphrase)
that the invariant intends to prohibit, freeze the actual wordlist and exact
numeric/date/quarter grammar, and assign every excluded surface to an honest
control that actually exists in this workspace. Then regenerate and rescan the
entire initial tree.

### 2. Signed fully-bound attestation — **accepted within D14**

Lines 157–179 satisfy the round-3 binding and authentication ruling: the signed
bytes bind the snapshot result, extraction/filter, wordlist, plaintext inventory,
manifest, complete scanner tree, coverage tool, count, `n_max`, result, and the
review artifact; CI recomputes the public side and rejects unsigned/wrong-key
substitutions. This authenticates the maintainer-side issuer against a third
party. It does not protect against a dishonest or compromised holder of the
pinned key, and D14 lines 274–280 expressly excludes that threat. I do not reopen
the accepted D14 narrowing by demanding separation of duty from a one-person
project. At implementation review, the committed snapshot algorithm must be
inside a named bound tool as the phrase “fully bound” requires.

### 3. Single-stream RNG and amendment-gated alternative — **accepted**

D12 lines 211–232 adopts the exact option round 3 allowed: independent neutral
vectors are reviewed and frozen before every rebaseline implementation; one
`numpy.random.Generator` is created once and threaded through every consumer;
schema-order stream shifting is disclosed; and keyed children cannot return
without an explicit owner-ratified charter amendment plus a complete derivation
specification and vectors. This resolves R2-F7, carried determinism F9, and
R3-F5.

## Carried blockers still open

### R3-F1 — blocker — D7 inventory/acceptance (`phase-0-public-skeleton.md:123–144, 297–303`)

**Defect:** The distinctiveness rule does not filter prototype code literals, so
the mandatory Class-A corpus still rejects the plan's own tracked documents.

**Concrete failure scenario:** The implementer extracts all AST string constants
as lines 126–129 require and creates the manifest. Before the first push, the
scanner finds 41 distinct entries across 129 plan lines and 24 across 42 response
lines; acceptance cannot pass without omitting promised entries or creating an
undeclared exemption.

**Required change:** Apply a deterministic source-specific/distinctiveness rule
to code literals too, assign excluded generic literals to the stated residual,
freeze the inventory, and demonstrate a zero-match initial tree.

### R3-F2 — blocker — D7 decoder (`phase-0-public-skeleton.md:145–151, 297–303`)

**Defect:** Latin-1 decodes every byte sequence, while the plan specifies no
binary/archive classifier capable of enforcing its claimed fail-closed route.

**Concrete failure scenario:** A no-NUL binary payload is saved with an allowed
text suffix. UTF-8 fails, Latin-1 succeeds, the decoded bytes contain no denied
n-gram, and the file ships even though lines 147–151 promise that a disguised
binary is rejected; a mutation containing NUL would exercise only the NUL rule.

**Required change:** Specify deterministic magic/type/control-byte rules and add
a no-NUL binary-with-text-extension mutation, or narrow the claim and document
the bounded format-classification residual.

### R3-F4 — blocker — D5 build closure (`phase-0-public-skeleton.md:59–78, 292–296`)

**Defect:** The build dependency set is locked, but the build is not prefetched
and executed with network unavailable as round 3 required.

**Concrete failure scenario:** A build hook in the executing closure launches a
native/process network client, retrieves a mutable second stage, and alters an
allowlisted wheel module. The Python socket guard and proxy cleanup do not fire,
`pip freeze` is unchanged, and a dormant smoke path passes.

**Required change:** Prefetch the complete hash-locked closure, install only from
that local set, run the build under an actual egress-denying boundary, compare
the executed artifact origins/hashes to the lock, and add a build-time egress
mutation.

### R2-F2 — blocker — D6 path locality (`phase-0-public-skeleton.md:87–98, 304–306`)

**Defect:** Revalidating after `Path.resolve()` is too late to prevent the
resolution operation itself from contacting a remote link/junction target.

**Concrete failure scenario:** A lexically local Windows path contains a link to
a UNC share. The raw string passes; Windows real-path resolution attempts the
remote target; only afterward does the resolved string fail. SMB/DNS activity
has already occurred although the eventual-rejection test is green.

**Required change:** Inspect link/reparse components without following them and
validate each target before traversal (or reject links), and make the mutation
assert no network attempt rather than only a rejected return value.

## New defects introduced or exposed by revision 4

### R4-F1 — blocker — D7 distinctiveness/matching (`phase-0-public-skeleton.md:129–155`)

**Defect:** Classification promotes an entire documentation/value surface when
one token is distinctive, but the matcher never requires that distinctive token
or a defined subphrase to be included as its own manifest entry.

**Concrete failure scenario:** A two-token prototype label contains one ordinary
word plus a neutral canary absent from the frozen wordlist. The two-token entry
is hashed. A contributor later writes the canary alone with different context;
no full-entry hash matches, CI stays green, and a source-specific token ships
despite the decontamination invariant.

**Required change:** Define the emitted unit: at minimum hash every normalized
distinctive token, plus any explicitly protected phrase forms, and parameterize
mutations that transplant the token into new left/right contexts.

### R4-F2 — blocker — D6 capability policy (`phase-0-public-skeleton.md:99–117, 304–306`)

**Defect:** The positive policy is module-granular, and the allowlisted
`importlib.metadata` module itself exposes an unbanned dynamic loader.

**Concrete failure scenario:** Source constructs an
`importlib.metadata.EntryPoint` and calls `.load()` for a forbidden module.
`EntryPoint.load()` calls `import_module` inside the standard library, so project
source contains only an allowed import and none of the banned references; the
named direct-import mutation remains red while a dormant smoke path stays green.

**Required change:** Restrict `importlib.metadata` to the exact version-query API
the skeleton needs, explicitly ban/test entry-point loading, and audit the other
allowed modules at API/capability rather than module-name granularity.

### R4-F3 — blocker — D7/D13 Class-B control (`phase-0-public-skeleton.md:138–141, 247–270`)

**Defect:** D13 assigns the machine-undetectable common-value leak to a claim
that no real-derived material exists on this machine, but the read-only prototype
and its profile artifacts are present beside this repository and D7 requires
private processing of that snapshot.

**Concrete failure scenario:** A common-word real-derived value is copied from an
adjacent profile artifact into ordinary source. Class A intentionally excludes
it, the fixture-regeneration guard does not govern ordinary source, and the
provenance scan passes; the only prevention claimed at lines 267–270 is a
workspace premise that is already false.

**Required change:** Either perform public-tree work in a genuinely clean
workspace/machine and run private extraction elsewhere with a hashes-only
handoff, or state the source-exposed-maintainer residual and add a concrete
review/control for ordinary source. Do not describe the present sibling-folder
layout as machine separation.

### R4-F4 — blocker — cross-cutting plan self-containment (`phase-0-public-skeleton.md:22, 44–52, 76–78, 180–204, 243–280`)

**Defect:** Revision 4 incorporates security-critical requirements by saying
“as/unchanged from revision 3,” but no revision-3 plan snapshot or repository
history exists, leaving the normative specification unavailable.

**Concrete failure scenario:** D9 tells the implementer only “seven jobs +
`gate` as revision 3.” A security job is omitted from the gate dependency graph;
that job fails while the app-bound gate succeeds, and the protected branch
accepts the commit—the exact outcome D9/D14 claim to prevent. D11, which consists
only of “As revision 3,” is even less reconstructible.

**Required change:** Consolidate every inherited normative decision into revision
4, or reference an immutable available artifact by path and digest. Review and
implementation conformance cannot depend on an overwritten draft.

## CLASS-A decontamination verification

Revision 4 and the round-3 response are **not clean** under the stable,
wordlist-independent portion of their own Class-A rule.

I extracted only:

- all 288 prototype profile column names; and
- every AST string constant from the four prototype Python scripts (1,288 raw
  literals).

I deliberately excluded every documentation term, displayed value surface, and
shell-script surface, so no choice of common-word list can weaken this result.
Using the plan's boundary order (non-alphanumeric, case, and letter/digit splits
before NFKC/casefold), the mandatory union has 756 normalized-unique entries,
113 of them one token, with `n_max = 578` when docstrings are included.
Line-local full-entry matching found:

- revision-4 plan: **41 distinct matches across 129 lines** (36 are one-token);
- round-3 response: **24 distinct matches across 42 lines** (21 are one-token).

Column-name-only matches were zero; every match came from the unconditionally
Class-A code-literal surface. Excluding docstrings still produces exactly the
same matches (721-entry mandatory union, `n_max = 48`). The not-yet-created
frozen wordlist and distinctive documentation/value portion are unverified, but
that cannot rescue a failure in a mandatory subset.

File digests at review time:

- revised plan: `25bf128c5926abb9b3011c62fbd26e750536cee0378c63d704b9362678e0166c`
- response: `bf5e75d1a2369cf703d3fb7afced27b3f82130878428b56246d00661e2195f20`

No matched entry or source value is enumerated or quoted in this review.

## What I checked

- Read `AGENTS.md`, `CLAUDE.md`, the round-3 review, the complete round-3
  response, and revision 4 in the requested order; traced every requested
  carryover through the round-1/round-2 records.
- Rechecked D12 against the charter's literal one-RNG rule and the prototype's
  determinism obligations, including ordered consumption, schema-order stream
  shifting, and pre-implementation independent vectors.
- Parsed all four prototype Python scripts with `ast` and the complete 288-name
  profile roster without printing any source token; independently ran both
  inclusive and docstring-excluding Class-A lower-bound scans.
- Recomputed the plan/response SHA-256 digests and confirmed the private-notes
  path resolves outside `synthtwin`.
- Confirmed the prototype and two profile artifacts are nevertheless on the same
  parent workspace/machine, contradicting D13's stronger machine-separation
  premise.
- Inspected the allowed `importlib.metadata.EntryPoint.load()` implementation
  and verified that it delegates to dynamic import internally.
- Inspected CPython's Windows real-path implementation: it invokes final-path
  resolution before handling bad-network-path/access errors, so post-resolution
  lexical rejection does not prove absence of a network attempt.
- Audited D5–D7 and D9–D14 plus all acceptance criteria for blast radius and
  checked whether each residual was named, bounded, and assigned to a real
  control. I did not count common-word/numeric surfaces merely for being Class B.
- Confirmed there is no implementation or test suite and no accessible revision-3
  plan/VCS snapshot. No project tests were run; the AST, hash, path, API-source,
  and corpus diagnostics above were run independently.

## Verdict

**Request changes.** D12's single-stream design and D7's signed attestation are
ratified within their stated scopes; do not reopen them absent new evidence.
Before implementation, make Class A discriminative and actually self-clean,
emit the distinctive units the matcher promises to prohibit, define a real
binary detector or narrow that claim, prevent resolution-time remote traversal,
close allowed-module capability routes, perform the build with network truly
unavailable, replace the false machine-separation premise with a real control,
and make revision 4 self-contained. These are concrete failures of controls the
plan claims will prevent, not objections to the named Class-B, remote-mount,
TOCTOU, or compromised-maintainer residuals.

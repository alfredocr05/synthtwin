# Phase 0 plan review — round 5

**Reviewed:** `docs/plans/phase-0-public-skeleton.md` (revision 5), the
round-4 review and complete response, the charter and reviewer brief, the
relevant read-only prototype surfaces, and the private audit notes  
**Verdict:** **approve-with-conditions**  
**Resolution count:** 4 resolved, 4 partially resolved  
**Round-5 finding count:** 7 — 6 blockers, 1 major  
**Condition count:** 7 bounded plan-text edits

Revision 5 is materially better and is now self-contained. It preserves the
three closed decisions, withdraws the false workspace-separation premise, and
closes the link-traversal and distinctive-token-emission failures. It is not
ready exactly as written: the Class-A rule cannot yet be reproduced, its stated
candidate surfaces omit parts of the complete corpus, build code can still run
before the network boundary, the container execution root is unpinned, the
positive API policy has a reflective escape, and the binary route remains
internally ambiguous. Every gap has a bounded edit below; no further plan-review
round is required after those edits are applied verbatim.

## Resolution of every round-4 blocker

| Round-4 blocker | Status | One-line evidence from revision 5 |
|---|---|---|
| **R3-F1 carried — self-failing inventory** | **Partially resolved** | D7 lines 212–225 now applies one distinctiveness rule to code literals and all other named candidates, and lines 277–279 require zero exemptions, but lines 217–220 refer only to future frozen list/grammar artifacts whose contents, deterministic construction recipes, and digests do not yet exist, so the rule and claimed clean result are not reproducible. |
| **R3-F2 carried — decoder false negative** | **Partially resolved** | Lines 237–251 add C0/magic routing and a residual, but do not order BOM decoding against raw-byte C0 detection, do not instantiate the magic table, and bound the residual to printable bytes even though an unknown-magic DEL/C1 stream also reaches the Latin-1 path. |
| **R3-F4 carried — build-isolation bypass** | **Partially resolved** | Lines 110–121 add a hash-locked wheelhouse and `--network none` build, but the preceding networked `pip download --require-hashes` may execute a locked source distribution's metadata hook, and lines 122–128 omit the pinnable container image and in-container interpreter from the closure/trust inventory. |
| **R2-F2 carried — path locality** | **Resolved** | Lines 148–166 perform lexical rejection first, inspect Windows components with `os.lstat`, reject a reparse component without reading its target, delay resolution until that walk succeeds, and require a spy assertion that resolution was never invoked. |
| **R4-F1 — distinctive unit not emitted** | **Resolved** | Lines 226–232 emit the full normalized entry and every distinctive token, then require transplanted-token mutations across contexts, filenames, and identifiers. |
| **R4-F2 — allowlisted dynamic-loader route** | **Partially resolved** | Lines 171–180 close the direct `EntryPoint.load()` route, but lines 173–185 prohibit only mutation of `sys.modules`/`sys.path`; a permitted registry read plus reflection can recover a forbidden preloaded capability without any listed banned token. |
| **R4-F3 — false Class-B machine-separation control** | **Resolved** | Lines 393–405 expressly withdraw machine separation, name the source-exposed-maintainer residual, bound it to common-value hand copying, and assign only controls that actually exist. |
| **R4-F4 — non-self-contained plan** | **Resolved** | Lines 3–7 deny normative force to superseded drafts, and revision 5 restates D1–D14 and acceptance in full; no operative “as revision N” reference remains. |

## Previously ratified decisions — no weakening

| Closed decision | Verification in revision 5 | Ruling |
|---|---|---|
| **D12 single-stream RNG** | Lines 337–341 retain independently reviewed, pre-implementation reference vectors; lines 342–356 retain one explicitly threaded `numpy.random.Generator`, ordered consumption, declared stream shifting, and an owner-ratified charter amendment plus full vectors for any keyed alternative; lines 357–369 retain the ratified byte-scope and canonical serialization. | **Restated without substantive weakening.** |
| **D7 signed attestation within D14** | Lines 252–270 bind the snapshot algorithm/tool, extraction/filter inputs, list/grammar, plaintext inventory, public manifest, complete scanner tree, coverage tool/result, counts, `n_max`, and reviewer artifact; preserve no self-digest, pinned-key signature verification, refresh triggers, negative mutations, and the accepted key-compromise residual. | **Restated without substantive weakening.** |
| **D14 narrowed tamper claim** | Lines 411–429 retain the app-bound gate, tag/account/workflow controls, third-party-tampering-only claim, explicit compromised/dishonest-maintainer residual, and user-verifiable compensating controls; lines 319–320 retain negative tag tests. | **Restated without substantive weakening.** |

These rulings remain closed. The conditions below repair adjacent enforcement
details; they do not reopen the ratified architecture or threat-model boundary.

## Revised Class-A scan

**Formal result: not yet certifiable under the exact promised rule.** Neither the
frozen common-word artifact nor the exact numeric/date/quarter grammar (or their
digests) exists in the repository or private notes. Consequently there is no
single executable Class-A membership function under which I can honestly claim
that revision 5 and the round-4 response have zero matches. Calling them clean
now would repeat the round-4 error in a different form.

I nevertheless ran a conservative, value-silent audit of the revised surfaces:

- Inputs were all 12 prototype files, including paths and every decodable text
  surface, not merely AST literals. Tokenization followed the stated boundary
  order before NFKC + casefold. No source token or displayed value was printed.
- The conservative prototype set contained 4,280 normalized unique tokens
  (including numeric tokens, which the final grammar may demote).
  Revision 5 intersected it in 576 tokens (intersection-set digest
  `1e5205db0b8bf1c9944bf8a11a896b85180e7f81b6e3e04fea60f98c21fa5ce1`);
  the response intersected it in 229 tokens (digest
  `0ff573b80fb6db71a6e218450e9bafc7603487225ea25266c86dbc60766b1a9e`).
- Manual/heuristic classification found no apparent source-distinctive match;
  the intersections were generic project, programming, security, statistical,
  or common-language tokens. A direct check against the charter's explicitly
  enumerated denied-token subset was zero in both targets.
- The target file digests were revision 5
  `7b2c2034ac3418f24012770f6624a50fd5acea448c2243e426b3f4b4113ec31f`
  and response
  `207be65274ad2723f390926cfcaa2e04bad5bbf7f4dbc6644f96628ac6b38dea`.

That is strong provisional evidence that both targets are clean under the
*intended* distinctive-token filter, but it is not a substitute for running the
actual frozen rule. C1 makes that proof a pre-code gate. The audit also exposed
the independent surface-completeness defect in R5-F2: merely listing a file in
the corpus does not cause its identifiers, comments, or non-Python source to
enter the candidate set.

## Round-5 review items

### R5-F1 — blocker — D7 classifier freeze (`phase-0-public-skeleton.md:212–225, 252–279`)

**Defect:** The plan calls the common-word list and pattern grammar frozen while
neither artifact, deterministic source/derivation, digest, nor freeze-before-scan
sequence exists, so Class-A membership can be adjusted after matches are known.

**Concrete failure scenario:** The initial scan finds a source-specific token in
the plan; the still-unfixed list is expanded to contain it, the surface becomes
Class B, the zero-exemption scan and signed attestation pass, and the control
certifies the very token it was meant to reject.

**Required condition:** C1.

### R5-F2 — blocker — D7 inventory completeness (`phase-0-public-skeleton.md:208–215, 271–279`)

**Defect:** “Complete snapshot” is not matched by the candidate taxonomy, which
names Python AST strings but not Python identifiers/attributes/comments or raw
shell and other non-Python source surfaces.

**Concrete failure scenario:** A distinctive source token occurs only in a
Python function name or a shell comment; extraction never offers it to the
distinctiveness filter, private coverage tests only the resulting incomplete
inventory, and a later copy of that token into public code passes the manifest.

The conservative audit found hundreds of identifier tokens outside the named
AST-string surfaces and multiple tokens unique to the shell source. Their values
are not reproduced here; the nonzero sets prove there are real unexamined
surfaces, not merely hypothetical parser categories.

**Required condition:** C2.

### R5-F3 — blocker — D7 decoder/classifier (`phase-0-public-skeleton.md:237–251`)

**Defect:** The byte pipeline is internally unordered and its named residual is
narrower than the streams the stated classifier actually accepts.

**Concrete failure scenario:** If the C0 test runs on raw bytes first, valid
BOM-tagged UTF-16/32 text is routed as binary because its encoding contains NUL;
if decoding runs first without an explicit rule, implementations can diverge.
Separately, an unknown-magic stream containing DEL/C1 but no listed C0 byte fails
UTF-8, decodes as Latin-1, and is neither rejected nor covered by the
printable-only residual.

**Required condition:** C3.

### R5-F4 — blocker — D5 networked prefetch (`phase-0-public-skeleton.md:110–121, 294–300`)

**Defect:** The egress-denying boundary starts after a `pip download` operation
that can execute source-distribution build/metadata code.

**Concrete failure scenario:** The hash-locked closure contains a source
distribution whose PEP 517 metadata hook runs during download on the networked
runner, fetches a mutable second stage, and changes the checkout or wheelhouse;
the later in-container fetch mutation still fails and the package/version freeze
still matches.

This behavior was verified in the installed pip source: requirement preparation
invokes distribution metadata preparation during `pip download`; hashes
authenticate the source archive but do not make its hook non-executing.

**Required condition:** C4.

### R5-F5 — blocker — D5 container trust root (`phase-0-public-skeleton.md:110–128, 294–300`)

**Defect:** The plan introduces a build container but neither selects nor
digest-pins its image or binds the in-container interpreter/toolchain, despite
claiming every pinnable input is pinned.

**Concrete failure scenario:** A mutable image tag resolves to an altered base
containing a startup hook or modified interpreter; `--network none`, wheel
hashes, `pip freeze`, content allowlisting, and a dormant CLI smoke test all pass
while the build artifact is changed.

**Required condition:** C5.

### R5-F6 — blocker — D6 positive capability policy (`phase-0-public-skeleton.md:171–200`)

**Defect:** Token bans plus import/API names do not enforce the claimed positive
capability boundary because reads from module registries and reflective object
state remain permitted.

**Concrete failure scenario:** Dormant source reads a preloaded allowed module
from `sys.modules`, constructs a forbidden callable's name from string pieces,
and invokes a process client; it contains only an allowed `sys` import and none
of the listed direct forbidden references, so every named mutation stays red
while this bypass stays green.

**Required condition:** C6.

### R5-F7 — major — supported Windows matrix (`phase-0-public-skeleton.md:90–93, 151–166, 296–300, 459–462`)

**Defect:** The security-critical Windows reparse implementation is tested only
on Python 3.14 even though Windows users are promised Python 3.10–3.14 support.

**Concrete failure scenario:** A version-conditional or standard-library
behavior difference causes the 3.10 branch to call resolution on a junction;
all Ubuntu floor-version cells and the sole Windows 3.14 cell pass, but a
supported Windows 3.10 installation attempts the remote traversal.

**Required condition:** C7.

## Conditions — exact bounded plan-text edits

These are the complete conditions of approval. Apply the quoted text verbatim;
they require no sixth review round. C1 is the first pre-code gate, after which
implementation proceeds under the conditioned plan.

### C1 — insert after the D7 corpus bullet

```markdown
- **Pre-code Class-A freeze:** before the authoritative Phase 0 extraction is run, before either the conditioned plan or the round-4 response is scanned, and before extractor/scanner/manifest code is written, materialize the exact common-word list and exact numeric/date/quarter grammar as versioned artifacts. Each artifact header records its neutral source identifier and digest, deterministic derivation/cutoff and normalization; no manual additions or removals are permitted. The artifacts must be source-independent: they are not derived from the prototype, the public tree, or scan results, and a match is fixed by editing public text, never by expanding the classifier. Their paths and SHA-256 digests, full contents, and construction recipes are included in the initial adversarial inventory-review artifact. Any later change is a plan-level decision and forces attestation refresh plus a full private/public rescan. The conditioned plan and the round-4 response must each produce zero Class-A matches under these exact artifacts before code work proceeds beyond this freeze gate.
```

### C2 — replace the D7 candidate-surfaces sentence at lines 213–215

```markdown
Candidate surfaces are every normalized path component; every decoded line of every textual snapshot file (including Python identifiers, attributes, and comments, shell and other non-Python source, and documentation); every cell of every structured text/profile artifact; and every AST string constant from every Python script. Structured extractors may add surfaces but never replace raw-text extraction. Coverage mutations place a neutral canary only in a Python identifier, only in a Python comment, only in a shell token/comment, and only in a path; every mutation must enter Class A and make the public scanner red.
```

### C3 — replace the D7 decoder/classifier bullet at lines 237–251

```markdown
- **Deterministic decoder/classifier order and bounded residual:** first recognize text BOMs longest-first (UTF-32 BE/LE before UTF-16 BE/LE), decode strictly, reject malformed input, apply the forbidden-control test to decoded Unicode scalar values, and scan the decoded text. With no recognized BOM, check the committed `magic-v1` offset/hex-signature table, then attempt strict UTF-8; valid UTF-8 is control-checked as decoded text and scanned. If strict UTF-8 fails, reject raw C0 bytes outside TAB/LF/CR and DEL/C1 bytes 0x7F–0x9F, otherwise decode as Latin-1 and scan. Before decoder/scanner code is written, `magic-v1` is materialized with every offset and exact hex signature, independently reviewed, SHA-256-frozen, and attestation-bound; its initial scope is archive, image, executable, compound-document, database, and columnar-storage signatures, and it makes no completeness claim. Named residual: every non-magic byte stream that survives these rules is treated and scanned as text regardless of whether a human would call it binary; no format-classification guarantee is made for that set. Required outcomes are explicit: valid BOM-tagged UTF-16/32 is green and token-scanned; malformed BOM text, BOM-less UTF-16/32 with forbidden controls, embedded forbidden controls, and listed magic are red; an unknown-magic surviving stream follows the named residual and an inserted Class-A token in it is detected.
```

### C4 — insert in D5 immediately before the network-unavailable build paragraph

```markdown
- **Non-executing acquisition gate:** the networked prefetch accepts wheels only: `pip download --require-hashes --only-binary=:all:` against the complete lock. The lock and prefetch reject source distributions, VCS requirements, editable requirements, and local/path requirements; no PEP 517 or legacy setup hook may execute before the network-none boundary. Every downloaded wheel is hash-verified immediately before the wheelhouse is mounted read-only into the build container. A malicious-source-distribution fixture whose metadata hook writes a sentinel is required to be rejected with the sentinel absent; this mutation runs at the prefetch boundary, not inside the later build.
```

### C5 — insert in D5 after the network-unavailable build paragraph

```markdown
- **Pinned build image:** the Ubuntu build uses the official CPython 3.14 slim Linux image referenced only as `repository@sha256:digest`, never by a mutable tag alone. The OCI digest is a committed lock input; CI verifies the observed image digest before execution and records it together with the in-container OS identity and exact Python and pip versions. The image digest and in-container interpreter/toolchain are included in `SECURITY.md`, the executing-closure comparison, build record, and release SBOM. A tag-only reference and a wrong observed digest are required red mutations. The container image is a named trust root at the pinned digest; changing it follows the dependency-update review path.
```

### C6 — replace D6.2's scanner-enforcement sentences after the API list

```markdown
The source policy is enforced as an AST/name-binding positive policy, not as substring bans alone. Every import binding, module-rooted attribute read or write, subscript into module/function state, and call target must resolve statically to an exact enumerated API; indirect or dynamically manufactured call/attribute targets are rejected. All reads and writes of `sys.modules` and `sys.path`, all dunder-state traversal, and the reflection primitives `getattr`, `setattr`, `delattr`, `hasattr`, `vars`, `globals`, `locals`, and `dir` are forbidden in `src/`; aliases are traced to their origin. The existing direct mutations remain, and two reflective mutations are added: a split-string lookup through a preloaded module registry and a split-string lookup through an allowed function's global state, each attempting a forbidden process call; both must be red.
```

### C7 — replace the Windows cell in D9's `tests` matrix

```markdown
Windows-latest × {3.10, 3.11, 3.12, 3.13, 3.14}, with the complete Windows path-locality/reparse suite running in every cell
```

## What I checked

- Read `AGENTS.md`, `CLAUDE.md`, the complete round-4 review, the complete
  round-4 response, and revision 5 in the requested order; checked every row
  above against the cited revision-5 lines rather than accepting the response's
  assertions.
- Audited every normative D1–D14 section and all acceptance criteria for
  self-containment, cross-section consistency, security boundaries, honest
  residuals, dependency closure, governance, and zero-code/public-skeleton
  scope.
- Compared D12, the signed D7 attestation, and D14 line by line with the precise
  round-4 approval rulings; found no substantive weakening.
- Parsed/scanned all 12 prototype files without printing candidate values; ran
  the conservative raw-text/path token audit and a separate explicit denied-set
  check against both requested targets; recomputed both target SHA-256 digests.
- Verified that the exact common-word and pattern artifacts do not exist in the
  current nine-file `synthtwin` tree or the two private-note files, so the formal
  scan qualification is evidence-based rather than assumed.
- Inspected pip's installed download/preparation path and confirmed that source
  distribution metadata preparation can execute before `pip download`
  completes; separately traced the reflective `sys.modules` bypass against the
  exact D6 allow/banned surface.
- Rechecked the Windows `lstat(..., follow_symlinks=False)` behavior against the
  [official CPython documentation](https://docs.python.org/3.12/library/os.html)
  and accepted the named network-mount/TOCTOU residuals rather than demanding an
  impossible portable mount detector.
- Confirmed there is still no implementation, package, workflow, or test suite.
  No project tests were available to run; the hash, corpus, decoder, pip-source,
  API-reachability, and self-containment diagnostics above were run independently.
- Did not verify the future D2 institutional authorization, GitHub settings, 2FA,
  signatures, or CI executions because none is present yet; those remain
  implementation acceptance evidence, not facts silently credited in this plan
  review.

## Final verdict

**approve-with-conditions**

Apply C1–C7 verbatim. The plan is then implementable and honest within its named
residuals, and implementation may begin without another plan-review round.

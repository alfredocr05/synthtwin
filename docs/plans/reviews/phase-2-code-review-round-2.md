# Phase 2 code review, round 2

**Date:** 2026-08-11  
**Reviewer role:** adversarial reviewer under `AGENTS.md`  
**Artifacts reviewed:** the ratified Phase 2 plan; both normative
specifications; the repaired profile-v4 producer and loader; generator,
renderer and CLI; the independent generation oracle and frozen vectors;
tests; security, disclosure and public-claim surfaces.

## Result

**REJECT.** The repairs close four round-1 items, partly close four, and
remove the silent part of the most serious allocation failure. They do not
carry the ratified exactness obligations completely. Eight current blocking
items are listed below as P2-C2-F1 through P2-C2-F8.

Severity in this review means:

- **HIGH** — release-blocking violation of a ratified owner decision,
  normative contract, independent-oracle obligation, or material fidelity
  claim.
- **MEDIUM** — incorrect or incomplete behavior that must be repaired but is
  not demonstrated here to expose source content or silently corrupt an
  ordinary generated column.

## Round-1 closure verification

I did not treat the repair tests as closure evidence. Each row below records
an independent execution of the original failure class against the current
tree.

| item | judgment | remaining severity | independent closure check |
|---|---|---:|---|
| P2-C1-F1, whole-group allocation | **partly closed** | **HIGH** | I exercised all three producer paths. A 5-row free-text column with three singleton numeric groups and one doubled text group has an exact joint class/alphabet assignment; seed 0 instead wrote five code-alphabet cells against four, and named `n_code_alphabet`. A producer-valid declared identifier with 132 group sizes reached the stated depth ceiling; generation returned in 0.0282 s, wrote `n_numeric` 5 versus 4, `n_not_numeric` 21,387 versus 21,388, and `n_all_digits` 5 versus 4, and named all three misses. A 5-row unrepresentable column with groups 1,1,1,2 has an exact class/sign assignment; generation wrote two negative and no positive cells against one each and named both sign misses. Thus all three paths now recount honestly, but none solves the joint or ceiling case completely. |
| P2-C1-F2, invention non-termination | **closed** | none | Under a 5-second subprocess deadline, the producer-valid 25-value, one-character wide-text boundary generated in 0.0015 s; the corresponding 26-value profile refused in 0.0014 s with both capacities and the requested count in the message, before writing. I also traced every accepted family to the finite `_family_room` bound: `_walked_cell` advances its state monotonically and stops at that precomputed size (`src/synthtwin/generation.py:3473-3503`); the optional letter pass rewinds once and the ordinary pass then consumes the same finite family. I could construct no loader-accepted cyclic state. P2-C2-F8 records a different, false *tighter* bound in the specification. |
| P2-C1-F3, finished-document publication guard | **closed** | none | I built a genuine profile and confirmed it passes. I then replaced the completed document's `source.header_evidence` with a plain source-derived string. The guard refused the path before serialization and its error did not echo the neutral marker. The current guard requires an origin-bearing `Note`, enumerated arguments and an exact re-render (`src/synthtwin/profile.py:753-781`), walks the closed finished shape (`profile.py:863-925`), and is called after lifted notes are installed (`profile.py:1071-1077`). |
| P2-C1-F4, approximation evidence | **partly closed** | **HIGH** | I generated a producer-valid numeric column containing 0 through 4. Its profile publishes `n_distinct = n_distinct_folded = 5`; seed 0 wrote four of each and named both as deviations, but `Twin.approximations` contained neither fact, no two-sided bounds, and therefore no corresponding approximation-report entries. The contract marks both numeric fallbacks APPROXIMATED (`docs/spec/profile-contract-v4.md:1841-1852`) and the method lists them explicitly (`docs/spec/generation-method-v1.md:1771-1790`). The new ledger covers the other families but is not complete. |
| P2-C1-F5, 4,096 numeric-spelling ceiling | **closed** | none | I profiled 4,098 spellings of zero, from one figure through 4,098 figures. Seed 0 completed in 9.2045 s with 4,098 raw and folded spellings; every spelling parsed to zero and no distinctness deviation appeared. The current walk increases the leading-zero order until an unused identity is found and imposes no fixed ceiling (`src/synthtwin/generation.py:1855-1906`). |
| P2-C1-F6, temporal round trip | **partly closed** | **HIGH** | I mutated genuine profiles through all resolution/precision combinations and invalid calendar, clock and offset boundaries. The loader now refuses the undefined datetime/date pair and impossible fields. It still accepts a producer-generated second value ending in `60`; for a 40-row genuine datetime column whose latest instant was that value, seed 3 wrote the following minute and named the endpoint miss. The new specification calls that endpoint REPORT-ONLY (`docs/spec/profile-contract-v4.md:1886-1911`), but the ratified plan still makes both endpoints exact without that corner (`docs/plans/phase-2-generator.md:607-612`). |
| P2-C1-F7, public claims | **closed** | none | I ran the installed command with no arguments and with `--help`, read all inventory surfaces, and ran the claim-inventory tests. The built `profile` and `generate` commands, pandas/numpy dependency set, three-artifact handling rule, qualified row-provenance statement, and absence of cross-column structure are current. The relationship wording in `CLAUDE.md` is in an explicitly not-built section. |
| P2-C1-F8, specification reconciliation | **partly closed** | **HIGH** | Direct serialization preserved `2.0`; a genuine 36-row decimal-style profile regenerated all 36 cells as decimal; and the false implication from `all_whole_numbers` to figures-only is gone from the normative documents and implementation. The current specifications nevertheless disagree with the ratified plan on allocation and leap-second exactness, omit numeric fallback measurements in code despite requiring them, and state a false invention-walk bound. The independent oracle also retains the retracted whole-number rule (P2-C2-F7). |

## Current blocking items

### P2-C2-F1 — Exact multi-constraint allocation still stops on producer-valid profiles

**Severity: HIGH.**

The repaired allocator searches at most 20,000 states and refuses a search
shape deeper than 400 (`src/synthtwin/generation.py:707-730`). The depth test
returns no exact allocation when `len(quotas) * (len(keys) + 2) > 400`
(`generation.py:763-785`), after which a deterministic greedy allocator takes
over (`generation.py:873-944`). Those constants bound runtime, but they are
not a proof of exact allocation. The ratified plan contains no ceiling and
makes the relevant facts exact (`docs/plans/phase-2-generator.md:639-661`).

The normative method is internally inconsistent. It first says every quota
MUST be met exactly whenever an assignment exists
(`docs/spec/generation-method-v1.md:1432-1444`), then permits any deterministic
fallback after a stated search ceiling (`generation-method-v1.md:1446-1455`).
The producer-valid identifier probe in the closure table has 132 distinct
`(group size, permission)` keys, so three quotas make the depth expression
402. The source table itself proves an exact assignment exists. `_allotted`
returned `None`; the fallback wrote five numeric and 21,387 nonnumeric cells
against four and 21,388, with five figures-only cells against four. The
finished recount named all three affected facts. Therefore the ceiling is
reachable by a profile the producer actually emits, and the fallback is
honest but nonconforming.

The problem is not restricted to the ceiling. Free text allocates numeric
class first and alphabet second (`generation.py:2855-2883`), while
unrepresentable text allocates magnitude class and sign in separate searches
(`generation.py:3530-3543`, `:3599-3629`). The small producer probes in the
closure table have feasible *joint* assignments that these sequential
allocations discard. Identifier allocation also uses the same bounded search
(`generation.py:2712-2739`). All three paths are now followed by independent
recounts (`generation.py:3955-3973`), and rendering prints every deviation
without filtering (`src/synthtwin/rendering.py:464-501`). That repairs the
round-1 silence, not the published facts.

**Concrete failure scenario.** A researcher profiles the five-row free-text
source from the closure table. The real column and an available assignment
have four code-alphabet cells. The twin has five. A pattern check that is
true on exactly four source rows is true on every twin row. The report names
the miss, but owner decision 4 promises the exact feasible fact rather than a
warning that it was lost.

**Required repair.** Specify and implement one joint, complete allocator for
each coupled set of exact facts, or obtain an explicit owner amendment that
defines the ceiling and changes the affected dispositions. Keep the finished
recount in either case. Add a producer-generated ceiling case and joint
free-text and unrepresentable cases that require exact output rather than
merely a deviation.

### P2-C2-F2 — Feasible numeric-style quotas are knowingly left unplaced

**Severity: HIGH.**

Owner decision 10 requires each numeric style in its published count
(`docs/plans/phase-2-generator.md:207-253`). The method correctly says a
named miss is not permission to omit a style when suitable cells exist
(`docs/spec/generation-method-v1.md:780-810`). The implementation chooses a
style using only remaining quota and whether the value is negative
(`src/synthtwin/generation.py:1235-1260`). It does not ask whether the
finished spelling will classify back into that style. Its own later comment
acknowledges that a planned plain cell can recount as decimal
(`generation.py:1907-1917`).

**Concrete failure scenario.** A genuine producer input with eleven
non-whole values `1.5` through `11.5` and forty whole values `100` through
`139` publishes 40 plain and 11 decimal cells. Seed 0 writes 0 plain and 51
decimal cells. Both deviations are reported, but the source values themselves
prove that the exact map is feasible: put plain style on the forty whole
values and decimal style on the eleven fractional values. A type- or
pattern-sensitive consumer therefore sees a completely different form mix
despite an exact owner decision.

**Required repair.** Allocate styles jointly with value feasibility, and
assert exact finished-text recounts for every producer-feasible style map.

### P2-C2-F3 — Numeric distinctness invention is unavailable inside reproduced styles

**Severity: HIGH.**

Owner decision 8 supplies an unbounded spelling family for distinctness, and
decision 10 says the published style takes precedence when reproducing form
(`docs/plans/phase-2-generator.md:143-181`, `:234-253`). The generator varies
leading-zero order only when the assigned style is literally
`leading_zero` (`src/synthtwin/generation.py:1881-1905`). Decimal and exponent
renderers have no corresponding order parameter (`generation.py:1208-1215`).
That leaves usable, style-preserving spellings such as additional zeros
before a decimal point outside the invention family.

**Concrete failure scenario.** A producer input containing twelve copies
each of three different decimal spellings of zero publishes 36 decimal
cells, three raw identities and three folded identities. Seed 0 preserves the
36-cell decimal style but writes one identity; the report names both
distinctness misses. The three source spellings, and the wider family they
demonstrate, prove the style and distinctness facts are jointly feasible.
Code that tests whether differently written zero values were normalized sees
one group in the twin and three in the real table.

**Required repair.** Define a no-ceiling invention family within every
published numeric style that can preserve the value and reader type, or
obtain an owner disposition for the lost distinctness. Freeze producer cases
that require more than one identity inside decimal and exponent styles.

### P2-C2-F4 — The numeric fallback approximation ledger omits both cardinalities

**Severity: HIGH.**

The method's complete list includes numeric `n_distinct` and
`n_distinct_folded` in their fallback
(`docs/spec/generation-method-v1.md:1771-1790`) and G12.8 supplies its stated
envelope
(`generation-method-v1.md:2084-2103`). The contract assigns the same
disposition (`docs/spec/profile-contract-v4.md:1841-1852`). Yet the code's
claimed complete list includes only numeric rungs and moments
(`src/synthtwin/generation.py:4374-4399`), and
`_numeric_approximations` returns only those fields
(`generation.py:4574-4706`). The role dispatcher has no second
numeric-cardinality path
(`generation.py:5241-5270`).

The test intended to prove matrix completeness transcribes the numeric roles
without the two fallback fields
(`tests/test_p2c1f4_approximation_bounds.py:187-215`). It therefore agrees
with the implementation while disagreeing with both normative tables.

**Concrete failure scenario.** On the 0-through-4 producer input from the
closure table, a user reads the report's approximation section to learn the
allowed cardinality range. Neither cardinality appears, although both missed
their exact value. The deviation section says four versus five, but it does
not print or check the two-sided bounds required for the fallback. The report
therefore claims every approximation was measured
(`src/synthtwin/rendering.py:493-501`) when two were not.

**Required repair.** Add finished-cell measurements, both bounds and report
entries for the two numeric fallback facts, and derive the test inventory
from all disposition clauses rather than a hand transcription that can omit
a conditional field.

### P2-C2-F5 — The specifications silently weaken exact temporal endpoints

**Severity: HIGH.**

The loader's strict calendar and offset checks repair the malformed-input
part of P2-C1-F6 (`src/synthtwin/contract.py:1932-2032`). It deliberately
accepts second 60 because the producer can emit it (`contract.py:1953-1956`,
`:2024-2032`). The reconciled contract then creates a new REPORT-ONLY leap
endpoint corner (`docs/spec/profile-contract-v4.md:1886-1911`). No owner
decision authorizes that exception. The ratified plan requires earliest and
latest to be exact in owner decision 5's representation
(`docs/plans/phase-2-generator.md:607-612`).

**Concrete failure scenario.** A 40-row source has a genuine latest instant
whose seconds field is 60. The producer publishes that exact latest value,
the loader accepts it, and seed 3 writes the next minute. A boundary filter
written against the twin can include a row at the following minute that is
not a source endpoint. The report names the mismatch, but the specification
has silently converted a ratified exact fact into a report-only one.

**Required repair.** Obtain an owner disposition for the producible corner,
or define an exact representational path that preserves it. The plan and both
specifications must state the same result before implementation is ratified.

### P2-C2-F6 — Feasible edge-spacing fold collisions are not constructed

**Severity: HIGH.**

The contract makes both invention-role distinctness counts exact outside the
single identifier width-capacity corner and explicitly binds fold collisions
(`docs/spec/profile-contract-v4.md:1926-1949`). Owner decision 6 permits
distinctness loss only when width and capacity are jointly infeasible
(`docs/plans/phase-2-generator.md:119-138`, `:639-657`). The implementation
uses case variation for partners and refuses to partner the first two pinned
length values (`src/synthtwin/generation.py:2633-2681`). It does not use edge
spacing even though folding trims it and it can preserve both pinned lengths.

**Concrete failure scenario.** A genuine declared identifier column contains
four distinct spellings that fold to one identity, with lengths 1, 2, 2 and
3. The producer publishes raw distinctness 4, folded distinctness 1 and the
feasible 1-to-3 length range. Seed 0 writes four raw and four folded
identities and names the folded miss. Adding edge spacing to one-character
content supplies the source's exact collision pattern within the same length
range, so this is not owner decision 6's infeasible corner. A case-insensitive
join tested on the twin sees four keys where the real table has one.

**Required repair.** Extend the collision construction to the full folding
operation the contract defines—case folding after trimming—while preserving
the other exact family constraints. Add a genuine edge-spacing collision
case whose length range remains feasible.

### P2-C2-F7 — The independent oracle retains a retracted identifier rule

**Severity: HIGH.**

The oracle remains mechanically independent: it imports only Python standard
library modules, imports neither synthtwin nor numpy, and the provenance guard
runs it under a policy that also blocks ctypes. Its exact `Fraction`
midpoint proofs, half-even tie decision, overflow boundary and signed-zero
handling are sound under the exercised mutants. The proof walk rejects
unproved numeric leaves, unknown container shapes and unused claims. All 76
oracle tests passed. Regeneration proved 210 published numbers across eight
cases plus 247 named counts; the 77,907-byte output had SHA-256
`376d9288eaf51f2569c4c254c8199f491a42ef49864c8ce1c3f2378416cc6375` and
byte-compared equal to the committed vector.

However, `_identifier_content` still chooses the figures-only alphabet
whenever `all_whole_numbers` is true and consults `n_all_digits == 0` only
when it is false
(`tools/reference/make_generation_reference_vectors.py:1525-1556`). That is
the rule P2-C1-F1 retracted. No frozen vector reaches the branch, so byte
equality does not test it.

**Concrete failure scenario.** I changed only an independent in-memory
identifier case to publish `all_whole_numbers: true`, `n_all_digits: 0` and
`n_code_alphabet: 0`. The oracle built 14 figures-only cells against the
published zero. If a future vector freezes that branch, the supposed oracle
will bless the withdrawn rule and can reject a conforming implementation—or
certify a nonconforming one.

**Required repair.** The repairing implementer's restraint was correct:
editing the independent
artifact to match implementation work would weaken its provenance. Restraint
does not make the stale branch acceptable. Its independently authorized
owner must reconcile it from the specification before any such vector is
added, then regenerate and review the affected proof and bytes.

### P2-C2-F8 — The specification's per-value invention bound is false

**Severity: HIGH.**

G9.2 correctly gives the implementation-wide termination proof: a walk is
monotone and stops at a finite family size
(`docs/spec/generation-method-v1.md:1226-1246`). It then additionally claims
that one value is produced after at most one more visited index than the
number of previously written values (`generation-method-v1.md:1248-1251`).
That does not account for candidates rejected because they classify into the
wrong numeric class, are missing-value spellings, or read as dates—the three
rejections the same section names. The code applies all of those predicates
(`src/synthtwin/generation.py:3483-3501`).

**Concrete failure scenario.** With an empty `used` set, I invoked the
current walk for an out-of-range code-alphabet value of length 5 and one word.
Index 0 produced a candidate of the wrong class and was rejected; index 1
produced the first value. The walk therefore visited two indices when the
stated bound was one. An independent implementation that uses the normative
`used + 1` sentence as its refusal threshold rejects a valid family even
though the shipped implementation returns a value.

**Required repair.** Retain the finite-family termination proof and remove
the false tighter sentence, or derive a true class-specific rejection bound
from the enumerator. Add a direct adversarial case for every post-enumeration
rejection predicate.

## Installed-entry boundary and security

I executed the installed `.venv/bin/synthtwin` entry from before its import of
`synthtwin.cli`, using an audit hook to record imports, file opens, sockets,
process creation and native loads. The profile was first produced through the
installed command; generation then exited 0 and wrote the twin and report.

- Generation did not import `synthtwin.reading`, `synthtwin.profile`,
  `synthtwin.taxonomy` or pandas.
- It did not open the real CSV. It opened the profile exactly once for
  reading and opened only its output paths for writing.
- It made no socket, network, subprocess or dynamic-code event.
- The only native-load event was numpy's locked, explicitly permitted
  runtime. No product call escaped the scanner's enumerated random API.

I found no transitive path from the installed generation entry to a real
table path, handle, table object or source-cell collection. The generator
boundary is closed in the executed entry-point closure, not only in source
imports.

I also inspected offline scanner E7-E9, origin preservation through aliases
and elements, writer provenance, path-locality handoff, native/dynamic-load
restrictions and mutation coverage. The offline scan and its suite passed.
No new security finding resulted.

## Independent-oracle assessment

In addition to P2-C2-F7, I checked:

- imports and call closure for implementation, numpy, pandas, ctypes and
  native interfaces;
- exact binary64 midpoint comparisons, half-even parity, overflow adjacency,
  subnormal and signed-zero behavior;
- recursive proof consumption through mappings, lists and tuples;
- rejection of unknown containers, unproved numbers and unspent claims;
- deterministic word inputs, case order, count proofs, serialization and
  committed-byte binding.

The arithmetic proof layer is sound for the branches exercised, and the
committed vectors still bind byte-for-byte. The stale identifier branch is a
coverage and conformance defect, not evidence that the checked binary64 proof
is wrong.

## Owner-decision trace

| P2-D0 decision | current result and disclosed cost |
|---|---|
| 1. additive axes | **Carried.** Producer, contract, loader, dispatch and report retain quality, statistical and structural axes independently; role is not used as a substitute for them. |
| 2. multiplicity parity | **Carried in the wire and each invention path, but exact interaction is incomplete.** Anonymous maps load and drive whole groups. Sequential and bounded allocations can still lose other exact facts (P2-C2-F1). |
| 3. eight reserved relationship slots | **Carried.** All eight are explicit nulls, the loader refuses filled slots, generation is independent by column, and current public surfaces disclose the absence of relationship fidelity. |
| 4. exact allocation and fact dispositions | **Not carried.** The state/depth ceiling and sequential allocations lose feasible exact facts (P2-C2-F1); two numeric fallback facts have no approximation records (P2-C2-F4). Honest recounting is now carried. |
| 5. datetime shape | **Partly carried.** Date, quarter, minute, second, subsecond, offset and invalid-range cases are explicit; source lexical family loss is disclosed as R-P2-7 (`docs/spec/generation-method-v1.md:2105-2117`). The new leap-endpoint loss lacks an owner decision (P2-C2-F5). |
| 6. identifier length wins only in the infeasible corner | **Not carried outside its scope.** The true width-capacity corner keeps width and reports raw, folded and multiplicity loss with the join/de-duplication consequence (`src/synthtwin/generation.py:2782-2808`). A feasible edge-spacing collision also loses folded identity (P2-C2-F6). This remains opposite the implementer's earlier recommendation to accept repeats generally. |
| 7. alternate numeric spellings | **Partly carried.** Multiple spellings are available, subject to decisions 8 and 10. They are not available within every reproduced style (P2-C2-F3). |
| 8. leading-zero, no-ceiling invention family | **Carried for the literal leading-zero style.** The 4,098-spelling probe passes, and the less-tidy output/type cost is disclosed as R-P2-9. The family is not generalized where decision 10 fixes another style (P2-C2-F3). |
| 9. floor-governed label variants | **Carried.** Published variants reproduce, below-floor variants are pooled anonymously, and the profile, summary, twin and report exclude the withheld spelling. This follows the owner's direction against the earlier recommendation to accept repetitions. |
| 10. floor-governed numeric writing styles | **Producer and disclosure carried; generation not complete.** The wire carries form counts without values or magnitudes, rare styles are pooled, and reports recount misses. Feasible style quotas and style-preserving distinctness are still missed (P2-C2-F2, F3). |
| 11. complete Unicode-fold variant contract | **Carried.** Exact spelling maps, anonymous occurrence multisets, parent/count invariants, Unicode-fold scope, SECURITY disclosure and four-surface scanning are present. The finished-document guard now covers the profile after note lifting. |

The implementation therefore does not completely carry decisions 4, 5, 6,
7, 8 and 10. The recorded costs for relationship absence, datetime lexical
family, identifier width precedence, less-tidy numeric spellings and widened
variant disclosure are honest. The allocation ceiling and leap endpoint are
new costs that are not owner decisions.

## Disclosure verification

I built one genuine 70-row table containing three unique neutral canaries:
a label variant below the small-cell floor, a complete label below the floor,
and a numeric spelling style below the floor. The profile published two
above-floor variants by exact spelling and count, represented the rare
variant only as `variants_withheld = {"1": 1}`, represented the rare parent
only by its anonymous occurrence bucket, and represented the rare numeric
style only as `(withheld): 3` beside `plain: 67`.

I searched the canonical profile, profile summary, generated twin and report
for each unique canary. All twelve searches were negative. Thus the floor
genuinely governs the new exact variant map, the anonymous withheld-variant
multiset and the numeric-style map; no withheld source value reached any of
the four artifacts. I also checked that wholly withheld parents carry no
variant keys, and that numeric style facts contain only form counts—not a
value, magnitude or spelling.

## Required verification run

All local commands used the repository `.venv` on macOS with Python 3.13.14.
Pytest's cache provider, Ruff's cache and mypy's incremental state were
disabled. I ran the content gate once on the existing staged index, and again
after adding this review to a copied temporary index; the second result is
the one that validates this public artifact.

| check | exact local result |
|---|---|
| full suite: `.venv/bin/python -m pytest -p no:cacheprovider` | **2,156 passed, 30 skipped** in 59.37 s; 2,186 collected. |
| offline scanner: `.venv/bin/python tools/offline_scan/scan_imports.py src/` | `scan_imports: checked 14 Python file(s) under 'src': 0 violation(s).` |
| decontamination, existing staged index | `decontamination: clean` |
| decontamination attestation | **verified**: signature, exact v2 shape, scanner tree, manifest, header bindings and counts matched. |
| provenance guard | **passed**: no unlisted data-format files; every manifest fixture matched regenerated bytes. |
| development lock validation | **passed** for `requirements-dev.in` and `requirements-dev.lock`. |
| install lock validation | **passed** for `requirements-install.in` and `requirements-install.lock`. |
| minimum lock validation | **passed** for `requirements-min.in` and `requirements-min.lock`. |
| Ruff: `.venv/bin/python -m ruff check --no-cache .` | `All checks passed!` |
| mypy: `.venv/bin/python -m mypy --no-incremental src` | `Success: no issues found in 14 source files` |
| this review through the no-argument staged-file content gate, using a copied index and temporary object database | `decontamination: clean` |

Passing tests do not resolve the review items. The approximation inventory
omits the two conditional numeric fields; style tests accept a named miss
where the owner requires feasible exact placement; and allocation tests do
not cover a producer-reachable ceiling or the two joint-constraint examples.

## Auditable coverage

### Surfaces examined

- `AGENTS.md`; ratified Phase 2 plan, owner decisions 1-11, sequencing
  override, disposition matrix, residuals and artifact-status record.
- Both normative specifications: canonical grammar, loader invariants,
  dispositions, allocation, numeric spelling, temporal representation,
  invention capacity, termination and approximation/report obligations.
- Current Phase 2 diffs in producer, taxonomy, publication guard, contract
  loader, generator, parser, renderer, CLI and transaction path.
- All three invention paths, allocation search/fallback, capacity arithmetic,
  spelling enumeration, collision construction, RNG consumption, recounts,
  approximation ledger and final report rendering.
- Installed generation entry and its transitive import/file/event closure.
- Independent oracle, proof ledger, provenance runner, committed vectors and
  the 76 oracle tests.
- Offline scanner E7-E9 and mutations; decontamination scanner and
  attestation; dependency declarations and three lock pairs.
- README, SECURITY, CLAUDE, package text, installed help/status, profile
  summary, generation report and public-claim inventory.
- New disclosure facts across canonical profile, summary, twin and report.

### Properties and attack classes examined

- Network I/O, sockets, subprocesses, dynamic loading, native calls,
  restricted-library escape, path locality and writer/callback provenance.
- Generator/profile boundary, reader-bearing initialization, aliases and
  attempts to recover a source path, handle, table or source cell.
- Silent statistical wrongness: exact class, alphabet, sign, whole/fraction,
  style, distinctness, folding, multiplicity, endpoint and relationship
  facts; approximation measurements and both bounds.
- Type misrouting through role plus the three independent axes, decimal/plain
  spelling, numeric-looking text, declared identifiers and unrepresentable
  numerics.
- Determinism: sorted iteration, one random stream, draw width and ordering,
  fixed enumeration, timeout/refusal behavior, same-input bytes and frozen
  vector binding.
- Validator honesty: finished-cell recounts, capable-of-failing bounds,
  matrix completeness, report inclusion, public claims and green-test
  vacuity.
- Decontamination and disclosure: floor boundaries, exact and pooled variants,
  Unicode folding, rare numeric styles, lifted notes and four-artifact
  propagation.
- Zero-code UX: installed help/status, bounded refusal, pre-write failures,
  report language, replacement behavior and two-file publication.
- Ordinary correctness: canonical JSON, CSV round trip, temporal ranges,
  formula-hazard reporting, lock structure and documentation/specification
  drift.

### Limits

I did not reproduce the full CI operating-system/interpreter matrix, the
network-disabled container build, or Windows reparse behavior locally. The 30
skipped cases were not executed on this host. Repository-public governance
controls remain deferred while the repository is private, exactly as
SECURITY.md records; I did not count a deferred control as active.

## Verdict

**REJECT.** The blocking items are **P2-C2-F1 through P2-C2-F8**: producer-
reachable and sequential allocation paths still lose feasible exact facts;
numeric style placement and style-preserving distinctness are incomplete;
the approximation report omits both numeric fallback cardinalities; a
ratified exact temporal endpoint was weakened without an owner decision;
feasible fold collisions are lost outside the authorized corner; the
independent oracle retains a retracted branch; and the normative invention
bound is false. Phase 2 code and both specifications are not ratified.

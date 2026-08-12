# Phase 2 code review, round 5 — final round

Date: 2026-08-12

Reviewer role: adversarial reviewer under repository `AGENTS.md`

Scope: the current staged Phase 2 tree, reviewed against the ratified
`docs/plans/phase-2-generator.md`, `docs/spec/profile-contract-v4.md`, and
`docs/spec/generation-method-v1.md`. All citations and results below were
re-derived from this tree; earlier-round citations were not trusted.

## Result

**REJECT.** Phase 2 is not safe to ship as ratified. Four items must block
ratification outright:

1. **P2-C5-F1:** the new structural disposition guard can be defeated by
   rephrasing a lesser outcome, separating it from a fact name, exploiting
   nearest-name attribution, changing the registry's class or authorization,
   or adding an `OPEN` entry. Seven independent mutations survived all 19
   guard tests.
2. **P2-C5-F2:** declared identifiers do not allocate the four published
   parser classes jointly with their alphabet counts. Genuine producer
   profiles miss `n_numeric`, `n_not_numeric`, `n_out_of_range`, and
   `n_contradictory` even when the source itself proves an exact assignment.
3. **P2-C5-F3:** the numeric-style repair contains a genuine producer case
   that it expressly expects to miss a named published style count. This is
   the still-open P2-C4-F3, not closure of it.
4. **P2-C5-F4:** P2-C4-C1 remains a ratified-plan deviation. Two valid
   hand-authored descriptions that the plan says generation must refuse are
   instead generated with exact obligations missed and reported.

One bounded documentation condition, **P2-C5-C1**, may be carried while the
four blockers are repaired. It is not permission to ship the product
failures above.

This phase is not fundamentally unsound. The installed boundary remains
offline and profile-only; no silent exact-fact miss survived the producer
batteries; the two-direction temporal refusal is sound; the free-text shape
repair holds over its producer battery; and the independent oracle is now
determinate, normally bound, proof-checked, byte-bound, and branch-mutant
complete. Those safe results are bounded precisely below.

Severity meanings:

- **HIGH:** blocks Phase 2 code ratification because a ratified exact fact,
  refusal rule, or structural protection is violated.
- **LOW:** an inaccurate audit record with no demonstrated generator-output
  consequence; it may be carried only with the stated closure check and gate.

## Commands and exact results

| check | result |
|---|---|
| full suite, `.venv/bin/python -m pytest -p no:cacheprovider` | **2,412 collected; 2,382 passed, 30 skipped** in 83.07 s; no xfails |
| focused oracle, proof and provenance tests | **240 passed** |
| offline scan, `.venv/bin/python tools/offline_scan/scan_imports.py src/` | `scan_imports: checked 14 Python file(s) under 'src': 0 violation(s).` |
| provenance, `.venv/bin/python tools/provenance/check_provenance.py` | passed; no unlisted data-format files and every fixture matched its registered generator |
| development lock | structural validation passed for `requirements-dev.in` and `requirements-dev.lock` |
| install lock | structural validation passed for `requirements-install.in` and `requirements-install.lock` |
| minimum lock | structural validation passed for `requirements-min.in` and `requirements-min.lock` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 14 source files` |
| signed attestation, `.venv/bin/python tools/decontamination/verify_attestation.py` | signature valid; exact v2 shape, scanner tree, manifest, header bindings, and counts match |
| decontamination | run after this review was staged; result recorded in the final verification section below |

A green suite does not resolve the verdict. The style-capacity test at
`tests/test_p2c4f3_style_capacity.py:389-449` affirmatively requires the
named exact miss, and the disposition guard's weaknesses are false
negatives rather than failing baseline tests.

## Round-4 closure table

| round-4 item | judgment | remaining severity | independent check |
|---|---|---:|---|
| P2-C4-F1, temporal calendar boundary | **Closed.** | none | I exercised both D10 directions: an early shared-clock endpoint moved below year 0001 by its negative offset, and a late shared-clock endpoint moved above year 9999 by its positive offset. The installed loader refused both and named D10. The same check accepts an ordinary endpoint and a local-clock seconds field of 60. The code loops over both ends and compares the moved minute to both bounds (`src/synthtwin/contract.py:3478-3565`); the contract states both directions (`docs/spec/profile-contract-v4.md:960-999`). |
| P2-C4-F2, free-text shape preassignment | **The named free-text failure is closed, but the general exact-allocation claim is reopened on declared identifiers.** | **HIGH, P2-C5-F2** | The 12-row producer witness now meets all four class/alphabet margins over seeds 0 through 63, and more than 900 producer-emitted short free-text profiles used no fallback. I then generated 360 producer-emitted declared-identifier profiles at seeds 0 and 63: 676 exact class-count misses resulted, all named. The source rows themselves supply the missing joint assignment. |
| P2-C4-F3, numeric style map | **Not closed.** | **HIGH, P2-C5-F3** | The original 51-row witness closes, but I independently described the 82-row source now present at `tests/test_p2c4f3_style_capacity.py:407-421`. It publishes `plain: 34` and `decimal: 48`; seeds 0, 1, and 63 write `20/62`, while seeds 17 and 113 write `30/52`. The test says in its own executable assertion that the named `plain` count is missed (`:389-449`). The source spellings themselves prove exact feasibility. |
| P2-C4-F4, strict-xfail oracle disagreement | **Closed by a genuine tightening.** | none | G9.3 now fixes which family member each slot takes: every slot starts at its parent's family start and selects the first unused spelling its own length window admits (`docs/spec/generation-method-v1.md:1703-1725`). That adds the missing selection rule; it does not weaken any published fact. The committed bytes did not change, all 14 implementation comparisons bind normally, `identifier_edge_spacing` now equals the oracle, and the focused oracle/proof run passed 240 tests with no xfail. |
| P2-C4-C1, blanket jointly-satisfiable qualification | **Not closed.** | **HIGH, P2-C5-F4** | No owner amendment exists. A producer profile edited to declare an 11+11 row, one-character identifier `all_whole_numbers: true` is accepted and generated with that exact fact missed. A 12-row, three-character free-text profile edited to publish `words.max: 3` is likewise accepted and generated with `words.max` missed. Plan P2-D6 says descriptions no rule can satisfy are refused (`docs/plans/phase-2-generator.md:668-687`); the contract instead says to generate, recount, and report (`docs/spec/profile-contract-v4.md:1845-1859`). |
| P2-C4-C2, own-branch mutants | **Closed.** | none | `CASE_MUTANTS` has exactly the 14 vector case keys; the equality assertion is executable (`tests/test_generation_reference.py:1160-1169`). Each parametrized case builds unmutated, then its own branch reversion must change cells or stop for the branch-specific reason (`:1172-1199`). All cases passed. |
| P2-C4-C3, leap-second vector | **Closed.** | none | `leap_second_endpoint` is the fourteenth normal case, contains the local-clock end `2016-12-31T23:59:60`, and carries a mutant that restores the ordinal route (`tests/test_generation_reference.py:1090-1097`; `docs/spec/generation-method-v1.md:3207-3222`). The implementation comparison and its own mutant both pass. |
| P2-C4-C4, provenance import statement | **Closed.** | none | The branch-vector manifest now states literally that the wrapper imports only `os`, `runpy`, and `sys`, then executes the fixed sibling core, whose imports are `argparse`, `datetime`, `fractions`, `json`, `math`, `struct`, and `sys`. The wrapper and core match that statement; neither imports synthtwin, numpy, or pandas. Provenance and attestation both pass. |

### Rounds 1–3 reopening spot-check

I reran the full suite and inspected every earlier repair file. The temporal
round-trip, transaction, disclosure, profile-version, approximation,
fold-collision, invention-domain, leading-zero, bounded-walk, and oracle
coverage repairs remain closed on their named witnesses. Two general claims
did reopen:

- P2-C1-F1/P2-C2-F1's exact allocation claim is violated by the declared
  identifier cases in P2-C5-F2.
- P2-C2-F2's numeric-style exactness remains violated by P2-C5-F3.

The six-row and 2,710-row round-3 allocator witnesses still close, as do the
round-3 temporal and oracle witnesses. I found no other reopened item.

## Structural disposition guard audit

### Baseline inventory and what the guard does protect

The current registry contains **110 unique facts**: 72 EXACT-OBSERVABLE, 6
EXACT-CONTROL, 10 APPROXIMATED, 11 REPORT-ONLY, 7 LOADER-ONLY, and 4
STRUCTURAL. The contract section-9 parser compares keys in both directions
and verifies the leading disposition. Its existing mutations catch a known
lesser phrase inserted at the beginning, middle, or end; catch a recognized
lowering moved between documents; catch a missing or invented contract row;
and catch the plan's parsed class being changed where the fact uses a parsed
binding. The four endpoint facts have empty authorization tuples. These are
useful protections.

They are not the claimed semantic protection. The prose scan depends on the
finite `LESSER` phrase tuple (`tests/dispositions.py:636-671`), attributes a
phrase to registered names only inside a 600-character window and to names
within 100 characters of the nearest (`tests/test_p2c4f1_disposition_registry.py:451-495`),
and skips prose scanning for exact facts whose field name has different
classes in different roles (`:184-200`, `:513-520`). A `plan_words` entry is
accepted by substring presence and bypasses parsed disposition checking
(`:206-237`). Authorization separately proves that some phrase and some plan
text exist; it does not bind their meanings (`:240-255`).

### Independent scratch attacks

Each mutation below was made in a fresh scratch copy outside the repository.
I ran the entire `tests/test_p2c4f1_disposition_registry.py` file after each
one. “Survived” means **19 passed** and the guard accepted the lowered tree.

| attack | mutation | result |
|---|---|---|
| rephrasing rather than keyword | Added a sentence beside `latest` saying the generated value is permitted to differ and then governs, without using a `LESSER` tuple phrase. | **Survived: 19 passed.** |
| moving between documents | Moved a recognized historical lowering into the plan. | **Caught: 18 passed, 1 failed.** This is a real strength, but only for recognized wording. |
| distance | Put `latest` more than 600 characters from a recognized `may miss` sentence. | **Survived: 19 passed.** |
| nearest-name attribution | Put a real lowering of `latest` beyond the 100-character together range and a closer `format may miss` phrase. The phrase was assigned to the report-only name. | **Survived: 19 passed.** |
| role-ambiguous name | Added “For numeric roles, `n_distinct` is REPORT-ONLY when the ladder is crowded.” | **Survived: 19 passed.** The prose scan excludes all three ambiguous field names: `n_rows`, `n_distinct`, and `n_distinct_folded`. |
| edit registry authorization | Authorized `n_missing` with the phrase `may miss` and quoted an unrelated exact sentence that already exists in the plan, then added `n_missing may miss`. | **Survived: 19 passed.** |
| edit registry disposition | Changed `n_missing` to REPORT-ONLY, supplied unrelated existing `plan_words`, and changed its contract row accordingly. | **Survived: 19 passed.** |
| open escape hatch | Added an `n_missing` lowering and `OPEN[("universal", "n_missing")] = "P2-C4-F1"`. The lexicographically newest review already mentioned that old item. | **Survived: 19 passed.** |

The last attack will also survive after this record lands: this review must
mention P2-C4-F1 to verify closure, and the escape test requires only that the
item text occur anywhere in the newest file
(`tests/test_p2c4f1_disposition_registry.py:544-557`). It does not parse an
open-item heading, status, fact key, or current-round ownership. Thus the
claim that an entry cannot outlive the round that named it is false.

### `OPEN` audit

The reported limit is inaccurate. `tests/dispositions.py:599-633` contains
**11**, not six, open facts:

- six class/alphabet facts under P2-C4-F2;
- `numeric_styles` under P2-C4-F3; and
- `words.min`, `words.max`, `all_whole_numbers`, and the section-head proxy
  `n_present` under P2-C4-C1.

Each current entry corresponds to a lesser statement the scanner presently
finds, so none is a fabricated permission in the baseline tree. They are
genuinely open defects: P2-C5-F2, P2-C5-F3, and P2-C5-F4 demonstrate their
families. The list is nevertheless a laundering route because an implementer
can add another entry carrying any old review identifier that this closure
record necessarily mentions. The separate “still a lowering” check
(`tests/test_p2c4f1_disposition_registry.py:560-571`) does not bind the
lowering to the cited review item.

The three dual-class field names are a real syntactic ambiguity, but excluding
them from prose checking is not safe. The role was explicit in the scratch
`n_distinct` lowering and the guard still ignored it.

## Items that must block ratification outright

### P2-C5-F1 — The structural guard is machine-checked but not structurally binding

**Severity: HIGH. Blocking.**

The guard proves several lexical and table invariants, but its main public
claim is semantic: no governing document may state a weaker outcome. The
scratch attacks prove that claim false across every defeat class the owner
asked this review to try except moving already-recognized wording. Editing
the registry is especially consequential because the plan check trusts an
unrelated `plan_words` substring, while the contract matrix then trusts the
edited registry. The proposed source of truth can therefore be changed on
both sides of its comparison without consulting the ratified disposition.

**Concrete failure scenario.** A future repair changes numeric
`numeric_styles` in the method to say “the resulting form may differ when
the ladder is crowded,” adds no phrase from `LESSER`, and leaves the matrix
row exact. All 19 guard tests pass. A genuine 82-row profile then ships with
34 plain cells promised and 20 written; the report names the miss, but the
contract still tells a consumer the count is exact. Alternatively, the
repair changes the registry and matrix to REPORT-ONLY and uses an unrelated
plan sentence as `plan_words`; the same suite still passes and now the
lowering looks structurally ratified.

**Required closure and owning gate.** The **Phase 2 disposition/claim CI
gate** must bind a stable fact identifier to a structurally parsed plan
disposition, not a free-form substring. Governing lesser outcomes must use a
bounded normative form keyed to that identifier, and any authorization must
bind the same fact, exact plan region, lesser class, and authorizing decision.
The newest-review exception must parse a current open-item record containing
the exact fact key and status; merely mentioning an old identifier must fail.
No `OPEN` entry may remain when Phase 2 is ratified. Executable closure is the
eight-mutation table above: all eight mutations must make the focused guard
test fail, the 110-key two-way matrix test must still pass unmutated, and a
test must assert `OPEN == {}` for a ratified phase.

### P2-C5-F2 — Declared identifiers miss producer-feasible exact class counts

**Severity: HIGH. Blocking.**

Plan P2-D6 makes all four parser classes exact by class-preserving
construction (`docs/plans/phase-2-generator.md:582-589`). Contract section
9.2 says the same (`docs/spec/profile-contract-v4.md:1888-1897`). But the
identifier method says its band allocation reads only the two alphabet
counts (`docs/spec/generation-method-v1.md:2213-2238`), and the implementation
passes only those three band quotas to `_allocation`
(`src/synthtwin/generation.py:4181-4208`). It then spells values without a
class margin and merely recounts any class miss afterward
(`src/synthtwin/generation.py:6226-6274`). Naming an exact miss makes the
report honest; it does not satisfy the exact obligation.

**Concrete failure scenario 1.** Describe a 49-row declared identifier with
source groups `N_7`×13, `no!!`×5, `x-y`×8, `913`×12, and `-3`×11. The genuine
profile publishes `n_numeric: 23`, `n_not_numeric: 26`, `n_all_digits: 12`,
`n_code_alphabet: 44`, occurrence counts 5/8/11/12/13, and length 2–4. Seeds
0 and 63 write `n_numeric: 12` and `n_not_numeric: 37`; both deviations are
named. The five source values themselves are a joint exact allocation.

**Concrete failure scenario 2.** Describe the 36-row declared identifier
`7`×5, `ab`×7, `(-5)`×11, and `1e999`×13. The producer publishes 5 normal
numbers, 7 text values, 11 contradictory values, and 13 out-of-range values,
plus exact alphabet, length, and occurrence facts. Seeds 0, 1, and 63 write
5 normal numbers and 31 text values, with zero contradictory and zero
out-of-range values. The report names all three misses. A user testing a
pipeline's treatment of oversized or internally conflicting numeric-looking
identifiers sees no such row in the twin even though the exact public profile
promised both classes.

Across 360 producer-emitted identifier profiles at two seeds I counted 676
exact class misses, all named and none silent. This is a general producer
path, not a contrived single case.

**Required closure and owning gate.** The **Phase 2 producer-feasibility and
exact-recount gate** must solve the four class quotas and two alphabet quotas
in one whole-group allocation before spelling identifiers. It must run both
producer scenarios above plus a seeded role battery, reclassify every written
cell through the shipped parser, assert every exact count with no deviation,
and include a mutant restoring the alphabet-only band walk that fails. The
lesser G9.6/G12 prose and corresponding `OPEN` entries must be removed or an
owner must amend the ratified plan before code changes are accepted.

### P2-C5-F3 — A producer-feasible numeric style map is still deliberately missed

**Severity: HIGH. Blocking.**

Owner decision 10 says the twin writes each style in its published count
(`docs/plans/phase-2-generator.md:207-253`), and the contract makes
`numeric_styles` EXACT-OBSERVABLE (`docs/spec/profile-contract-v4.md:1912-1923`).
Plan feasibility rule 4 gives published counts precedence over ladder
conformance (`docs/plans/phase-2-generator.md:677-682`). The method instead
lists a point-free shortfall (`docs/spec/generation-method-v1.md:2525-2534`),
the registry leaves the fact open (`tests/dispositions.py:609-623`), and the
new test explicitly asserts the miss.

**Concrete failure scenario.** Profile 82 numeric rows:
`0.125`, `0.25`, `0.375`, and `0.625` ten times each; `1` twenty times;
`-32` fourteen times; and `-59.5`, `52.75` four times each. The producer
publishes `plain: 34` and `decimal: 48`. Seed 0 writes 20 plain and 62 decimal
cells; seed 17 writes 30 and 52. The source is itself a satisfying witness.
A user checking that a downstream reader preserves a mixed whole/decimal
input distribution receives a twin with materially fewer point-free forms
than the exact public map promises.

**Required closure and owning gate.** The **numeric-style producer battery
and oracle branch gate** must choose strata, multiplicities, and endpoint
carriers jointly so this 82-row producer profile reproduces 34/48 at every
declared test seed without a style deviation. It must add an own-branch mutant
that restores the current crowded-ladder choice and fails. Remove the
style-miss method/contract commentary, affirmative miss test, and `OPEN`
entry. An alternative needs an explicit owner amendment to decision 10 and
the plan before implementation.

### P2-C5-F4 — The feasibility stage generates two cases the ratified plan says to refuse

**Severity: HIGH. Blocking.**

P2-D6 says generation refusal is reserved for descriptions no governing rule
can satisfy and fixes the refusal message (`docs/plans/phase-2-generator.md:668-687`).
The method claims it has exactly two refusals (`docs/spec/generation-method-v1.md:2500-2523`).
The contract instead creates a blanket qualification and instructs the
generator to meet, recount, and report what it can on inconsistent
hand-authored inputs (`docs/spec/profile-contract-v4.md:1845-1859`). Its
free-text and identifier rows apply that lesser outcome directly
(`:2028-2044`). This is the unamended P2-C4-C1 plan deviation.

**Concrete failure scenario 1.** Take a producer profile for 22 one-character
declared identifiers in two groups and edit only `all_whole_numbers` to true
while leaving an alphabet quota that requires a non-figure value. The strict
loader accepts it; generation writes a non-whole value and reports the exact
fact as missed. A user relying on every generated identifier being readable
as a whole number encounters text despite an exact true flag.

**Concrete failure scenario 2.** Take 12 distinct three-character, two-word
free-text values and edit only `words.max` from 2 to 3. Three characters can
hold at most two nonempty space-separated words. The loader accepts it;
generation writes at most two and reports `words.max` as missed instead of
refusing before output.

**Required closure and owning gate.** The **Phase 2 generation-feasibility
gate** must refuse both inputs before writing a twin, say that the profile is
valid, name the conflicting facts, and give profile-only remediation; tests
must assert no output is committed. The contract, method G12 list, and
registry must agree with that behavior. The only alternative is an explicit
owner amendment to the ratified plan followed by specification review; the
current code review cannot supply that authority.

## Condition that may be carried

### P2-C5-C1 — The Phase 2 status paragraph stops at code review round 1

**Severity: LOW. Carryable only while the four blockers are repaired.**

The plan's artifact status says the implementation was reviewed and rejected
in round 1 and will remain unratified until a later round says otherwise
(`docs/plans/phase-2-generator.md:1200-1221`). The unratified conclusion is
still correct, but the audit history omits rounds 2 through 5.

**Concrete failure scenario.** The owner reads the canonical status block
during the release decision, sees only eight round-1 blockers, and fails to
follow the final review record containing the current four. The product
remains blocked elsewhere, but the canonical plan gives a materially
incomplete account of why.

**Executable closure check and owning gate.** Before Phase 2 ratification,
the **documentation claim-inventory/provenance gate** must assert that the
status paragraph names code review rounds 1 through 5 and reproduces this
review's final verdict without claiming deferred controls are active. The
existing claim-inventory suite and decontamination scan must then pass. This
condition does not authorize carrying P2-C5-F1 through P2-C5-F4 into a ship.

## Standing-scope audits

### Installed boundary, offline guarantee, and profile/generator separation

I invoked the installed `.venv/bin/synthtwin` entry point, not an internal
helper. I profiled a 40-row, two-column CSV, declared its identifier role,
moved the source CSV away, then generated seed 17 under import tracing. The
twin and report were written with 40 data rows. The generator import trace
contained `cli`, `contract`, `generation`, `parsing`, `rendering`, and
`writing`; it contained neither `reading`, `profile`, nor pandas. Generation
succeeded with the real table absent. The report named its authorized numeric
distinctness fallback.

I searched product code for network I/O, subprocesses, native calls, dynamic
loading, unsafe path resolution, and imports outside the allowlist, then ran
the offline scanner. It checked all 14 source files and reported zero
violations. I found no generation path by which product code can read the
real table rather than the loaded profile.

### Silent-wrongness producer audit

I built producer-emitted profiles covering identifier, categorical, count,
continuous, datetime, binary, free text, empty, constant, and
numeric-unrepresentable roles. For seeds 0, 17, and 63 I generated, described
the twins again, and recounted every exact fact. I separately exercised the
free-text shape battery, declared-identifier fuzz battery, numeric-style
battery, label disclosure source, and both temporal bounds.

- Every exact miss found was represented by a report deviation under the
  public fact's own name; no silent miss survived.
- The identifier class misses in P2-C5-F2 were all named.
- The numeric-style misses in P2-C5-F3 were all named.
- Authorized numeric distinctness and datetime-cardinality deviations stayed
  inside their published two-sided envelopes and were named.
- Empty-cell counts, parser classes, temporal endpoints, label counts and
  variants, free-text shape facts, and unrepresentable margins had no
  unreported exact mismatch in the exercised profiles.

This is evidence that validator/report honesty is sound on the observed
failures. It is not permission to replace an exact obligation with a named
miss.

### Disclosure floor

I described a 63-row label/numeric table containing two visible label
variants, one below-floor label variant, one suppressed label, 60 visible
plain numeric cells, and three below-floor exponent-form cells. The profile
published the visible variant counts, recorded the hidden variant as the
anonymous multiset `{3: 1}`, recorded the suppressed label only through its
count and row total, and recorded the numeric style remainder as
`(withheld): 3`. The exact below-floor spellings were absent from all four
required surfaces: profile JSON, profiler summary, twin CSV, and generator
report. This covers label variants, withheld-variant multiplicities, and
numeric styles rather than only the twin artifact.

### Oracle independence, proof soundness, and byte binding

The selection text added at G9.3 is a tightening: the old family order did
not determine which admissible member a slot received; the new text chooses
the first unused admissible member from the family's start
(`docs/spec/generation-method-v1.md:1703-1738`). It neither weakens a
disposition nor changes the frozen vector bytes.

There are 14 required cases in two committed files, including the five branch
cases and the leap-second case (`docs/spec/generation-method-v1.md:3113-3137`).
Every case has an own-branch mutant, and the mutant key set equals the case
set. All implementation cell and CSV-byte comparisons bind normally. No
pytest xfail marker remains; the only `xfail` wording is historical
explanation. The oracle core imports only the stated standard-library
modules, never synthtwin, numpy, or pandas; the wrapper contains no transform
or proof logic. The exact-integer rounding proofs, uint64 input binding,
mutant-before-write refusal, fixture regeneration, provenance, and signed
attestation checks all passed.

### Eleven owner decisions and disclosed costs

| decision | judgment |
|---|---|
| 1, additive axes | carried completely; dispatch and exact-control checks pass |
| 2, multiplicity parity | carried for free text and numeric-unrepresentable roles; identifier's separately authorized capacity corner names all three lost distinctness facts |
| 3, relationships reserved | carried as eight null slots and loader-only structure |
| 4, exact-count allocation | **not carried completely: P2-C5-F2** |
| 5, datetime shape | carried for resolution, precision, offsets, endpoints, and local seconds 60; loss of the source parser-family spelling is honestly disclosed as R-P2-7 |
| 6, identifier length wins only in the declared capacity corner | carried in that corner with duplicate, join, and de-duplication costs; it does not authorize the ordinary class misses in P2-C5-F2 |
| 7, alternate numeric spellings | carried only where counts require them; distinctness fallback is bounded and named |
| 8, leading-zero family | carried with an unbounded spelling supply; decimal forms appear only when the published style map requires them |
| 9, label variants | carried with the floor on each exact variant spelling |
| 10, numeric style map | **not carried completely: P2-C5-F3** |
| 11, complete label-variant contract | carried with wire invariants, anonymous withheld multiplicities, full four-surface disclosure testing, and the broader fold disclosure |

The material costs are stated honestly where the decision authorizes them:
identifier duplicates and join behavior, datetime lexical-family loss,
numeric distinctness envelopes, withheld label spellings, and inferred-type
effects of published numeric forms. I found no cost disclosure that silently
claims a deferred public-repository control is active.

## What is safe in this phase

Within the exercised scope, I judge these parts safe and independently
supported:

- **Security and offline operation:** the installed generator consumes the
  profile with the source absent; the product import and capability scan is
  clean; no profile/generator boundary bypass was found.
- **No silent statistical miss found:** every observed exact-count failure is
  named in the report with published and achieved values. The remaining
  blockers are explicit contract violations, not hidden report omissions.
- **Temporal endpoints:** D10 rejects both calendar-overflow directions at
  load time while preserving ordinary and local leap-second cases.
- **Free-text shape repair:** the round-4 producer witness and a broad seeded
  short-profile battery meet the jointly feasible class/alphabet facts without
  fallback.
- **Oracle:** it is independent of product code and numpy, proves its numeric
  outputs, binds all 14 cases normally at cells and CSV bytes, and gives each
  case a non-vacuous own-branch mutant.
- **Disclosure floor:** visible label variants, anonymous withheld-variant
  multiplicities, suppressed labels, and numeric style remainders respect the
  floor across profile, summary, twin, and report.
- **Determinism and output integrity:** repeated seeds reproduced bytes in the
  spot checks; differing seeds followed the declared seed path; transaction,
  quoting, row-count, header, and path-locality tests remain green.
- **Type routing outside the named identifier defect:** declared roles, numeric
  integer/decimal form, datetime resolution, label roles, empty, and
  numeric-unrepresentable paths followed their published axes in the role
  battery.

These results distinguish a phase with four identifiable blockers from a
phase whose entire security, oracle, or reporting model is unsound. They do
not make the four blockers carryable.

## Coverage and gaps

Surfaces examined: ratified plan, profile contract, generation method,
registry and its parser, all round-4 repair tests, product loader and
generator, installed CLI entry point, profile/summary/twin/report artifacts,
both vector files, oracle core and wrapper, provenance manifest, lock files,
release checks, security claims, and all earlier Phase 2 review records.

Properties examined: two-way disposition completeness, semantic lowering,
authorization provenance, open-item freshness, exact recounts across roles,
producer feasibility, type routing, deterministic bytes, temporal endpoint
representation, numeric style capacity, text shape allocation, oracle
independence and proof coverage, disclosure floors, report honesty,
profile-only generation, and all eleven owner decisions.

Attack classes examined: rephrasing, document movement, lexical distance,
nearest-name capture, role ambiguity, registry authorization tampering,
registry disposition tampering, escape-hatch laundering, matrix omission and
invention, network/process/native/dynamic-loading routes, source-table access,
unordered/randomness drift, branch-removal mutants, below-floor disclosure,
and producer-feasible silent wrongness.

Limits: the producer battery is broad but finite; it is not an exhaustive
proof over every valid profile. I did not compare against the private
prototype or disclose its inventory. The public method, frozen neutral
vectors, independent recounts, and release checks were the numeric oracle available
for this phase. No network was used during the review.

## Final verification of this review artifact

The workspace permission profile makes the repository's `.git/index`
read-only, so `git add` could not alter the real index. I copied the current
index to a temporary directory, configured a temporary writable Git object
store with the repository objects as read-only alternates, and added exactly
this review there. Under that staged index:

- `git ls-files --error-unmatch` named this review, proving it was part of the
  scanner's tracked-file set;
- the no-argument `.venv/bin/python tools/decontamination/check.py` reported
  **`decontamination: clean`**;
- `git diff --cached --check -- docs/plans/reviews/phase-2-code-review-round-5.md`
  reported no problem; and
- the newest-review guard reported **19 passed**.

No repository file other than this review was modified by this review turn.
The actual index remains unchanged because its write was denied; the owner
must stage this file outside that sandbox before committing.

## Verdict

**REJECT.** The blocking items are **P2-C5-F1, P2-C5-F2, P2-C5-F3, and
P2-C5-F4**. Phase 2 must not be ratified or shipped until each item satisfies
its executable closure check at its named gate. **P2-C5-C1** alone may be
carried, bounded to the documentation status repair and its claim-inventory,
provenance, and content-gate checks. The safe results above remain valid
within their stated evidence and do not reduce any blocker.

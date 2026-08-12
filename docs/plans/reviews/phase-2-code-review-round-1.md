# Phase 2 code review, round 1

**Date:** 2026-08-11
**Reviewer role:** adversarial reviewer under `AGENTS.md`
**Artifacts reviewed:** the ratified Phase 2 plan; the two previously
unreviewed specifications; the profile-v4 producer and loader; generator,
renderer, transaction and CLI changes; scanner extensions E7-E9; the
independent generation vectors and their proof layer; tests; disclosure and
claim surfaces.

## Sequencing basis

The owner override in `docs/plans/phase-2-generator.md` authorizes the code to
have been built before the specifications were reviewed. I applied that
override as written. It does not waive review of either specification. This
review therefore treats a defect in either normative document as a defect in
the Phase 2 artifacts, not merely as documentation drift around otherwise
acceptable code.

Severity in this review has the following meaning:

- **CRITICAL** — release-blocking security, non-termination, or silent
  fidelity failure on an accepted or producer-generated input.
- **HIGH** — release-blocking violation of a ratified owner decision,
  normative contract, security control, or material public claim.
- **MEDIUM** — incorrect or incomplete behavior that must be repaired but is
  not itself demonstrated to expose source content or silently corrupt a
  common generated column.

## Review items

### P2-C1-F1 — Whole-group allocation violates exact published facts on identifier, free-text and unrepresentable paths

**Severity: CRITICAL.**

`generation._share_out` is a largest-group-first greedy heuristic
(`src/synthtwin/generation.py:606`), not an exact allocation procedure. The
same heuristic drives free-text class and alphabet allocation
(`generation.py:2295`) and unrepresentable class allocation
(`generation.py:2693`). Identifier allocation adds a second error:
`_identifier_bands` writes every group from `DIGITS` whenever
`all_whole_numbers` is true (`generation.py:2192-2201`), without regard to the
independent published `n_all_digits` or `n_code_alphabet` facts.

This contradicts owner decisions 2, 4 and 6 and the ratified plan's matrix at
`docs/plans/phase-2-generator.md:599-625`. Only three identifier distinctness
facts become report-only, and only in the length-infeasible corner.
`n_all_digits`, `n_code_alphabet`, the universal four-class partition, and all
unrepresentable sign/whole facts remain exact.

The following probes all used genuine profiles made by the shipped producer
and then loaded by the shipped v4 loader:

| path and source values | published fact | achieved fact | report result |
|---|---:|---:|---|
| declared identifier: `11` twice, `22` twice, `AB` three times | `n_all_digits = 4` | 5 | names the miss, although it is not a permitted report-only fact |
| declared identifier: `+1` twice, `+2` twice | `n_all_digits = 0`, `n_code_alphabet = 0` | 4 and 4 | names both misses |
| free text: two numeric groups of two, one text group of three, eighteen text groups of two | `n_numeric = 4`, `n_all_digits = 4`, `n_code_alphabet = 4` | 5, 5 and 5 | class misses are filed under non-contract names `number` and `text`; alphabet misses are named |
| unrepresentable: `1e999` twice, `2e999` twice, `1e-999` three times | `n_whole = 4` | 5 | does not name `n_whole` or `n_fraction`; emits two misleading `n_out_of_range` entries instead |
| unrepresentable: `-1e999` three times and two positive values twice each | `n_negative = 3` | 2 | no sign deviation at all; only the unconditional invented-width note appears |

**Concrete failure scenario.** A researcher profiles the first declared
identifier column and develops a rule that digits-only codes take one branch
and lettered codes another. The real column has four digits-only cells. The
twin has five, despite the exact fact being feasible: assign the two groups of
size two to the digits bucket and the group of size three to the code bucket.
The test at `tests/test_generation.py:1404-1446` asserts the wrong result as
expected behavior and says no assignment reaches four. That statement is
arithmetically false. On the unrepresentable negative example, the wrong
two-versus-three result is silent even in the report.

The generation specification contains the same defect class. G9.5 says
`n_all_digits` **groups**, although the contract defines it as a count of
cells (`docs/spec/generation-method-v1.md:1189-1193`). G9.6 then asserts that
`all_whole_numbers` forces `n_all_digits == n_present`
(`generation-method-v1.md:1236-1246`). The profile contract has no such
invariant, and the producer-generated `+1`, `+2` example disproves it.

The independent oracle correctly caught its singleton identifier case, but
that case has no non-trivial group packing. Its repair is therefore real for
the eight frozen vectors and incomplete for the defect class the oracle
exposed.

**Required repair.** Replace greedy allocation with a specified exact
multi-constraint allocation over whole groups, or obtain a new owner
disposition for any fact that is mathematically infeasible. Remove the false
all-whole implication. Recount every exact class, alphabet, sign and
whole/fraction fact independently from the finished cells, using the
contract's exact field names. Replace the current identifier regression with
one that requires the feasible 2+2 allocation, and add the free-text and both
unrepresentable probes above.

### P2-C1-F2 — The stated invention capacity is not the generated domain, and a producer-valid profile does not terminate

**Severity: CRITICAL.**

G9.4 defines capacity as `sum(|A|**L)`, while G9.1 maps several raw strings to
the same fixed-end string and G9.5 further restricts the leading character by
class and alphabet. The code repeats the over-count in `_domain_size`
(`generation.py:475`) and applies the many-to-one transform afterwards in
`_spelling_at` (`generation.py:521`). For `WIDE` at length one, the planner
reports 95 spellings, but the stated positional transform produces only 90
different strings. The free-text, wide-band, ordinary-text construction has
only 25 valid one-character outputs.

The method explicitly promises that no rejection loop exists
(`docs/spec/generation-method-v1.md:1074`). The implementation contains
bounded searches at 4,096 and 1,000,000 steps and unbounded `while True`
searches. In the failing path, `_plain_text` loops forever
(`generation.py:2619`) over a finite cycle created by `_worded`'s modulo-4096
state (`generation.py:2682`).

**Concrete failure scenario.** A genuine CSV with 26 different one-character
ordinary-text values outside the code alphabet profiles as `free_text` with
`n_distinct = 26`, `length.min = length.max = 1`, and both alphabet counts
zero. The loader accepts it and `plan_generation` claims capacity 95. In a
fresh subprocess, `generation.generate(profile, 0)` did not return within two
seconds. Source inspection closes the inference: after 25 accepted values the
candidate walk is periodic and every candidate is already in `used`, so the
loop has no return path. The promised pre-generation
`generation-domain-too-small` refusal never occurs.

This is both a zero-code UX failure and an availability failure: the accepted
command consumes CPU indefinitely instead of naming the incompatible facts
before writing.

**Required repair.** Define capacity over the actual injective, class- and
position-constrained enumeration; make the enumeration a direct mixed-radix
mapping with no search; and prove that every accepted free-text and
unrepresentable plan terminates. Add the 26-value producer regression and
capacity boundary mutations for every class/band combination.

### P2-C1-F3 — The required finished-document publication guard is absent

**Severity: HIGH.**

P2-D2 requires origin-tagged, enumerated note constructors and a recursive
guard over the finished document, including notes lifted to the top level
(`docs/plans/phase-2-generator.md:384-411`). The profile specification repeats
the obligation at `docs/spec/profile-contract-v4.md:284-292`.

No origin type, enumerated note grammar, or finished-document recursive guard
exists in `src/`. `taxonomy.ColumnProfile.publication_notes` remains
`list[str]`; `profile.build_document` copies those strings directly into the
finished top-level array (`src/synthtwin/profile.py:361-445`). No required
same-path, concatenation, nested-container, or lifted-note mutation exists in
the suite.

**Concrete failure scenario.** I replaced the existing note-producing seam in
memory so it appended the first source cell to the existing
`publication_notes` list without changing the path or type. With a source
value `source-note-marker-271`, `profile.build_document` returned a finished
document containing exactly that value under the lifted top-level note. No
guard failed. A future maintenance edit that interpolates a rare source
spelling into an existing explanatory note would therefore publish it while
the disposition and schema tests remain green.

The current constructors appear not to perform that interpolation. That is
not the ratified control: the plan deliberately rejected reliance on current
constructor care.

**Required repair.** Implement the specified closed note-constructor type and
grammar, tag every authorized string origin, recursively validate the final
document after top-level lifting, and add all four required mutations. The
guard must fail during construction, before serialization.

### P2-C1-F4 — Approximation obligations have neither complete bounds nor an honest report

**Severity: HIGH.**

The profile contract defines `APPROXIMATED` as a fact measured from the
written CSV, checked against a stated two-sided finite-sample bound, and named
in the generation report with published and achieved values
(`docs/spec/profile-contract-v4.md:74-89`). Its matrix assigns that class to
numeric moments, interior numeric and datetime rungs, datetime cardinality,
label cardinality in its fallback, and free-text length/word summaries
(`profile-contract-v4.md:1649-1701`). The plan requires the same completeness
and a test that fails when any emitted field lacks a disposition.

The generation specification defines a rung window, but explicitly fixes no
bound for `mean`, `std`, or `skew` and delegates that normative job to a test
battery (`docs/spec/generation-method-v1.md:585-587`). No such derived moment
bound exists. There is likewise no complete bound/report implementation for
the other approximated families.

At runtime, `ColumnOutcome` carries only presence and raw/folded distinctness
counts (`src/synthtwin/generation.py:198-220`), and `_recounted` computes only
those four counts (`generation.py:659`). The report can therefore render only
generator-created deviations and those few recounts. It does not independently
reprofile the twin or print achieved moments, rungs, datetime cardinality, or
text summaries. I found no promised disposition-completeness assertion.

**Concrete failure scenario.** For the genuine 200-row square-number fixture,
the profile publishes mean `13433.5`, standard deviation
`12011.485753228033`, and skew `0.6361376847074723`. At seed 7 the twin has
mean `13654.57`, standard deviation `11907.104235770657`, and skew
`0.6017428700017496`. `twin.deviations` is empty, and the report contains no
achieved standard deviation or skew and no testable moment bound. A user is
told that the report is the place that distinguishes exact, approximate and
unmet facts, but cannot tell whether these differences passed any rule.

The rung mutation tests are useful and capable of failing, but they are test
helpers over one numeric family; they do not make the shipped report honest
or complete the disposition matrix.

**Required repair.** Fix a formula and finite two-sided bound for every
approximated field in the normative method. Build an independent recount or
reprofile result from the finished CSV cells, put every published/achieved
pair and bound outcome in the report, add the promised matrix-completeness
assertion, and add base-plus-mutant batteries for each approximation family.

### P2-C1-F5 — Owner decision 8's unbounded numeric spelling family is capped at 4,096

**Severity: HIGH.**

Owner decision 8 says the leading-zero family has no ceiling
(`docs/plans/phase-2-generator.md:144-169`), and G6.3 calls its supply
unbounded (`docs/spec/generation-method-v1.md:650-654`). `_number_cells`
stops looking for a new leading-zero order at 4,096
(`src/synthtwin/generation.py:1540-1574`). On collision at that point it emits
the already-used spelling.

**Concrete failure scenario.** A genuine numeric column containing the 4,098
spellings `0`, `00`, and so on profiles as `count` with
`n_distinct = n_distinct_folded = 4098` and
`numeric_styles = {"(withheld)": 1, "leading_zero": 4097}`. Generation at
seed 0 produces only 4,097 different spellings. The report names the two
distinctness misses, but owner decision 8 says this capacity failure cannot
arise; it is not an authorized report-only corner. The run also emits an
unrelated endpoint deviation for a zero-size constructed stratum, which makes
the diagnostic less honest still.

**Required repair.** Remove the arbitrary ceiling and compute the requested
leading-zero order directly. Add a regression beyond 4,096 and a test that an
all-zero ladder creates no zero-size-stratum endpoint deviation.

### P2-C1-F6 — Loader-accepted temporal facts are not preserved by the generator

**Severity: HIGH.**

The profile contract explicitly permits `time_precision == "date"` when
`resolution == "datetime"` (invariant D6 at
`docs/spec/profile-contract-v4.md:814-818`), and the loader implements that
rule (`src/synthtwin/contract.py:3157-3218`). `_cell_of_ordinal` has no date
branch for datetime resolution: anything other than minute or subsecond is
written with seconds (`src/synthtwin/generation.py:984-1015`).

The loader also treats canonical date/time and signed-offset text as a shape
only. `_canonical_datetime` explicitly accepts calendar-impossible month,
day, hour, minute and second fields (`contract.py:1924-1976`), and the offset
checker accepts out-of-range hour/minute components. Generation then performs
calendar and offset arithmetic on those unchecked fields.

**Concrete failure scenario.** Starting with a genuine datetime profile, I
set only `time_precision` to `date` and left `resolution` as `datetime`. The
canonical document loaded successfully. Generation emitted values such as
`2024-01-01T00:00:00`, reprofiling at second rather than date precision, and
recorded no deviation. Separately, a contract-shaped profile whose endpoints
and rungs are `2024-99-99` loads and is normalized by generation to
`2032-06-23`, so its exact endpoint text is not preserved.

**Required repair.** Reconcile D6 with the rendering grammar: either forbid
the combination in the normative contract and loader, or define and implement
its exact output. State and enforce valid calendar, clock and offset ranges,
or specify a non-calendar interpretation that round-trips. Add loader-valid
generation tests for every permitted resolution/precision pair and boundary
mutations for calendar and offset ranges.

### P2-C1-F7 — Public relationship and current-capability claims contradict the implemented phase

**Severity: CRITICAL.**

The Phase 2 profile deliberately publishes eight null relationship slots and
the report says columns and rows are generated independently. Nevertheless,
the package docstring promises “same relationships”
(`src/synthtwin/__init__.py:3-5`), and the canonical implementer brief promises
the same relationships and a relationship summary
(`CLAUDE.md:10-16`, `CLAUDE.md:59-68`). These are present-tense product claims,
not a future roadmap qualification.

The checked claim inventory is too narrow to catch them. It correctly bans
the retired categorical row claim and requires the qualified provenance and
three-artifact handling statements, but it does not inventory relationship
fidelity, current phase, current dependencies, or current command
availability. Consequently it is green while `README.md` still says Phase 1,
marks generation and its report as planned (`README.md:1-10`,
`README.md:150-164`), calls generator separation future architecture, and
says numpy is not a dependency (`README.md:188-201`). `SECURITY.md:61-66`
still describes the source allowlist as one function of one third-party
library even though E7/E8 and `pyproject.toml` now admit numpy's random
generator.

**Concrete failure scenario.** I profiled a table with two identical columns,
each containing the same 200 square numbers. Every source row had
`left == right`. At seed 19 the generated columns were not identical and zero
of 200 twin rows had `left == right`, as Phase 2's independent-column method
allows. A user relying on the package's “same relationships” claim can develop
and accept code on the twin that behaves oppositely on every real row. A
separate zero-code user following the README is told the already-installed
`generate` command does not exist.

The requested row-provenance correction itself is present and qualified in
CLAUDE.md, README.md, SECURITY.md, the package docstring, command status/help,
profile summary and generation report. All three artifacts are named in the
institutional-handling text. The defect is that other material claims on the
same surfaces remain false, and the inventory's green result overstates its
coverage.

**Required repair.** Remove present-tense relationship fidelity from every
current product surface and state plainly that Phase 2 carries no cross-column
structure. Update current-phase, command, output and dependency descriptions.
Expand the claim inventory so relationship fidelity, phase status,
dependency count and command availability have both positive and negative
checks, with current and planned sections distinguished.

### P2-C1-F8 — The two normative specifications contain incompatible serialization and spelling rules

**Severity: HIGH.**

The profile contract defines canonical serialization by Python
`json.dumps` and then says numbers use a shortest form with no redundant
fraction (`docs/spec/profile-contract-v4.md:112-134`). Its loader table says a
trailing `.0` on an integer is changed by reserialization
(`profile-contract-v4.md:1851-1860`). The same document later correctly says
`2.0` survives the canonical round trip unchanged
(`profile-contract-v4.md:1870-1875`). The implementation follows Python:
`canonical.serialize({"x": 2.0})` writes `2.0`
(`src/synthtwin/canonical.py:35-51`).

The profile contract's `numeric_styles` disposition also says the styles the
twin may write are exactly the canonical, leading-zero and leading-plus
family, with exponent case only for fold collisions
(`profile-contract-v4.md:1436-1444`). That list omits the required `decimal`
style, while the same contract requires and classifies it and the generation
method correctly includes it. The generation method's false all-whole
identifier invariant and cell/group confusion are recorded in P2-C1-F1.

The plan's own closing sentence still says no Phase 2 code exists and no part
of the plan is ratified (`docs/plans/phase-2-generator.md:1147-1153`), in
direct conflict with its current status and the recorded sequencing override.
Two earlier plan passages still say four parser bounds where the ratified
decision and profile contract say exactly two.

**Concrete failure scenario.** An independent loader follows the profile
contract's shortest-number prose and rejects a shipped profile containing a
number-valued `mean: 2.0` as non-canonical, while the shipped loader accepts
it. An independent generator follows the profile contract's closing style
list for a profile with eleven `decimal` cells and emits plain cells; one
following the generation method emits decimal cells. Both cannot conform to
the current normative text, defeating the specifications' stated purpose of
supporting an independent implementation.

**Required repair.** Make the canonical-number grammar agree with the actual
serializer or replace the serializer with the stated grammar; make the
numeric-style family identical in both specifications and the plan; remove
the false identifier invariant and group/cell wording; and correct the plan's
status and parser-bound record. Add direct cross-document consistency tests
for these rules.

## Owner-decision trace

| P2-D0 decision | review result |
|---|---|
| 1. additive axes | Carried in producer, contract, loader, dispatch and report; role/axis tests pass. |
| 2. multiplicity parity | Wire shape and loader are carried; generation violates class/sign allocation and can fail to terminate (P2-C1-F1, F2). |
| 3. reserved relationship manifest | Eight null slots and loader refusal are carried; public relationship-fidelity claims contradict them (P2-C1-F7). |
| 4. exact-count allocation and disposition | Not carried completely; exact facts fail, approximation obligations are incomplete, and the promised matrix-completeness assertion is absent (P2-C1-F1, F4). |
| 5. datetime shape | Ordinary date, quarter, minute, second, subsecond and offset fixtures pass; the contract-allowed datetime/date combination and unchecked canonical ranges do not (P2-C1-F6). |
| 6. identifier length wins | Length-infeasible distinctness reporting exists, but exact alphabet facts fail outside that corner and the specification invents a false invariant (P2-C1-F1). |
| 7. alternate numeric spellings | Implemented through the six recorded styles; its corrected scope is governed by decisions 8 and 10 below. |
| 8. leading-zero family | Ordinary fixtures pass; the implementation imposes a forbidden 4,096 ceiling (P2-C1-F5). |
| 9. published label variants | Carried. Named variants reproduce exact counts and below-floor spellings are not named. |
| 10. numeric writing styles | Producer, loader and ordinary generation cases carry six styles under the floor; the cross-spec list is inconsistent and high-cardinality distinctness fails (P2-C1-F5, F8). |
| 11. complete label-variant contract | Carried in wire shape, loader invariants, generation and disclosure text; the finished-document publication guard that protects all publication routes is still absent (P2-C1-F3). |

## Boundary, security and oracle assessment

### Installed-entry transitive boundary

I executed the installed `.venv/bin/synthtwin` entry point in a fresh process
on a genuine profile and watched imports and file-open events from before the
entry script imported `synthtwin.cli`.

- Profiling exited 0 and produced the profile used by the probe.
- Generation exited 0 and wrote only `source-twin.csv` and
  `source-twin-report.txt`.
- Product modules imported by the generation process were `canonical`,
  `cli`, `contract`, `errors`, `generation`, `parsing`, `paths`, `rendering`
  and `writing`.
- No `reading`, `profile`, `taxonomy`, or pandas import occurred.
- No CSV file was opened for reading during generation.
- A second run with Python import-time tracing reached both outputs and also
  showed no forbidden reader-bearing import.

The lazy branch boundary is therefore real for the installed entry point, not
just for a unit-test import state. I found no generator route to a table path,
table handle, table object or source cell collection.

### Offline and scanner surface

I inspected E7-E9's restricted origins, element-origin preservation,
`int(...)` origin termination, first-party argument slots, writer handle and
row provenance, and the red mutation coverage in `tests/test_offline_scan.py`.
The product uses only `numpy.random.default_rng` and `Generator.integers` in
the enumerated form; the CSV rendering path is first-party text construction,
so E9 does not enlarge a product call site today. The standalone scanner and
its mutation suite passed. I found no network-I/O, subprocess, dynamic-load,
or direct native-call path in product source.

### Independent oracle

`tools/reference/make_generation_reference_vectors.py` imports only
`argparse`, `datetime`, `fractions`, `json`, `math`, `struct` and `sys`; it
imports neither synthtwin nor numpy/pandas. The frozen words are inputs, not
drawn by the tool. Provenance rebuilt the vectors under the guard and
byte-compared them successfully.

The binary64 layer uses exact `Fraction` arithmetic, compares against exact
neighbour midpoints in `prove_nearest_float`, handles overflow and signed zero,
and recursively refuses unproved numeric leaves or unknown container shapes
before serialization (`make_generation_reference_vectors.py:236-352`,
`:517-626`, `:2457-2500`). Its proof and full-generator mutants pass. I found
no arithmetic error in that layer.

Mechanical source independence is established; historical authorship
independence cannot be proved from repository bytes. More importantly, eight
correct examples are not a completeness proof. The oracle's identifier case
caught the original singleton collision/alphabet defect, but contains no
non-singleton allocation, no domain-exhaustion case, and no leading-zero order
beyond 4,096. P2-C1-F1, F2 and F5 pass outside its coverage.

## Disclosure and claim checks

The new disclosure facts are implemented at the producer boundary:

- each exact label variant is named only when its own count reaches
  `small_cell_floor`;
- below-floor variants are represented only by the anonymous occurrence
  multiset in `variants_withheld`;
- a wholly withheld parent has no `variants` or `variants_withheld` entry to
  expose spellings;
- each numeric style is named only at the floor and rare styles are pooled;
  the map contains form counts, not numeric values or spellings.

I generated a profile with a below-floor label, a below-floor exact variant,
and a below-floor numeric style. The two source spellings were absent from the
machine profile, profile summary, twin CSV and generation report. The profile
contained only `variants_withheld = {"3": 1}` for the rare variant and
`numeric_styles = {"plain": 72, "(withheld)": 3}` for the rare style.

`SECURITY.md` describes the Unicode case-fold width of the variant delta, its
anonymous multiset and floor, and all six numeric forms with the floor and the
fact that no value/magnitude/spelling is carried. The profile summary names
the widened disclosure. The CLI status, summary and generation report each
state the qualified provenance claim, the forced-match counterexample, the
lack of a formal privacy guarantee, and institutional handling for the
profile, twin and report. P2-C1-F7 records the other false claims that the
current inventory misses.

## Verification run

All commands used the repository's `.venv` on macOS with Python 3.13.14. I
set `PYTHONDONTWRITEBYTECODE=1`; pytest's cache provider and Ruff's cache were
disabled, and mypy ran without incremental state.

| check | exact local result |
|---|---|
| full suite: `python -m pytest -p no:cacheprovider` | **1942 passed, 4 skipped** in 37.18 s; 1,946 collected. The four skips are Windows-only path checks on this macOS host. |
| offline scanner: `python tools/offline_scan/scan_imports.py src/` | **14 Python files checked, 0 violations**. |
| decontamination content scan | **clean**. |
| decontamination attestation | **verified**: signature, exact v2 shape, scanner tree, manifest, header bindings and counts matched. |
| provenance guard | **passed**: no unlisted data-format files; every manifest fixture matched regenerated bytes. |
| development lock validation | **passed** for `requirements-dev.in` and `requirements-dev.lock`. |
| install lock validation | **passed** for `requirements-install.in` and `requirements-install.lock`. |
| Ruff: `python -m ruff check --no-cache .` | **All checks passed.** |
| mypy: `python -m mypy --no-incremental src` | **Success: no issues found in 14 source files.** |

Observed coverage gaps remain: the suite treats the feasible identifier miss
as expected behavior, has no
finished-document publication-guard mutation, has no moment/report
conformance battery, and has no termination boundary for the actual
one-character free-text domain.

## Auditable coverage

### Surfaces examined

- Ratified Phase 2 plan, owner decisions 1-11, closure table and sequencing
  override.
- Both unreviewed specifications, including wire grammar, invariants,
  dispositions, draw method, numeric/date/text generation, feasibility,
  report obligations and oracle requirements.
- All new or heavily changed product modules named in the review request and
  their transitive import closure from the installed command.
- Profile-v4 producer changes for axes, multiplicity, relationships, variants
  and numeric styles; strict loader; canonical serializer.
- Generator dispatch, allocation, capacity, RNG draw budgets, each role path,
  recount/deviation construction and output rendering.
- Two-file transaction and its fault-injection tests; CLI grammar, help,
  status, replacement behavior and display boundary.
- Offline scanner E7-E9 and mutations; provenance manifest/generator;
  generation vector proof layer and conformance tests; golden twin/report
  digests.
- CLAUDE.md, README.md, SECURITY.md, package and module docstrings, command
  help/status, profile summary, generation report and claim-inventory tests.

### Properties and attack classes examined

- Network, subprocess, native-interface and dynamic-load reachability;
  restricted-library object escape; writer-handle and callback/protocol
  provenance; path-locality handoff.
- Reader-bearing module initialization, aliases/re-exports and pre/post
  dispatch generation closure; attempts to pass or recover a real-table
  path, handle, object or cell collection.
- Silent statistical wrongness: class partitions, signs, whole/fraction
  counts, alphabet counts, distinctness/folding, repetition, numeric styles,
  rungs/moments, temporal precision and relationships.
- Type misrouting through the three axes, integer/decimal spelling, numeric
  stragglers and declared identifiers.
- Determinism: one stream, full-width words, draw counts/order, sorted
  iteration, same-input repeat, golden bytes and independent transform
  vectors.
- Validator honesty: independent recounts, complete dispositions, bounds,
  capable-of-failing mutants, achieved-versus-published report text and
  green-test vacuity.
- Disclosure: below-floor label, variant and style publication; nested and
  lifted note routes; source spelling propagation across profile, summary,
  twin and report.
- Zero-code UX: installed help/status, actionable refusals, pre-write
  feasibility, non-termination and two-file transaction state reporting.
- Ordinary correctness: canonical JSON, loader rejection order, temporal
  shapes, CSV quoting/round trip, formula-hazard reporting and documentation
  drift.

### Limits of this local review

I did not reproduce the CI operating-system/interpreter matrix, the
network-disabled container build, or Windows reparse behavior locally. The
four platform-specific tests were skipped on macOS, and the checked golden
tests establish only this host's agreement with the committed bytes; CI is
still required for cross-platform evidence. Repository-public governance
controls remain deferred while the repository is private, as SECURITY.md
states; I did not treat them as active.

## Verdict

**REJECT.** The blocking items are **P2-C1-F1 through P2-C1-F8**: exact facts
are violated across all three group-invention paths; a producer-valid profile
does not terminate; the ratified publication guard is absent; approximation
bounds and report evidence are incomplete; owner decision 8 has an arbitrary
ceiling; loader-accepted temporal facts are silently changed; public
relationship/current-capability claims are false; and the two unreviewed
specifications are internally incompatible. Phase 2 code and both
specifications must be revised and reviewed again before ratification.

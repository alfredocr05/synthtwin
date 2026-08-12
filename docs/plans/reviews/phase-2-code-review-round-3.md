# Phase 2 code review, round 3

**Date:** 2026-08-11  
**Reviewer role:** adversarial reviewer under `AGENTS.md`  
**Reviewed revision:** `246d265399cdb39c71bac4380cbcde7dda817095`  
**Artifacts reviewed:** the ratified Phase 2 plan; both normative
specifications; the current profile-v4 producer and loader; generator,
renderer and installed CLI; the independent generation oracle and committed
vectors; security, supply-chain, disclosure and public-claim surfaces; the
complete test tree; and both earlier Phase 2 code reviews.

## Result

**REJECT.** Six of the eight round-2 items are closed. P2-C2-F1 and
P2-C2-F5 are only partly closed and remain **HIGH-severity blockers**:

1. **P2-C3-F1 / P2-C2-F1:** the joint allocator's pruning and failure
   memoisation are sound, but the claimed unreachable 200,000-work ceiling is
   reached by a genuine producer profile, and the unrepresentable path still
   manufactures a class cross-tabulation for which no joint answer exists
   even though every published marginal came from a real table.
2. **P2-C3-F2 / P2-C2-F5:** both specifications display the ratified exact
   endpoint sentence, then create an exception elsewhere; the loader accepts
   that description and the code deliberately changes the endpoint.

P2-C3-F3, the independent oracle's uncovered branches, is **MEDIUM** and is
bounded enough to carry to round 4. It is not a reason for this rejection;
the two HIGH items above are the named blockers. Its checkpoint is stated
under that item.

Severity in this review means:

- **HIGH** — release-blocking violation of a ratified owner decision,
  normative exactness obligation, boundary, or material fidelity claim.
- **MEDIUM** — a real verification gap with a concrete escaping mutant, but
  not a newly demonstrated source-content leak or product-output defect
  beyond a separately blocking item.

## Required checks, run on this tree

I ran the commands rather than accepting the reported baseline.

| gate | exact result |
|---|---|
| full suite: `python -m pytest -p no:cacheprovider` | **2,260 passed, 30 skipped**, 2,290 collected, in 63.91 s |
| focused oracle suite | **103 passed** in 0.89 s |
| round-1 boundary spot checks | **12 passed** in 14.76 s |
| offline scan | `scan_imports: checked 14 Python file(s) under 'src': 0 violation(s).` |
| provenance | `Provenance check passed: no unlisted data-format files; every manifest fixture matches its generator output.` |
| decontamination, staged index | `decontamination: clean` |
| signed attestation | signature valid, exact v2 shape, scanner tree, manifest, header bindings and counts all matched |
| development lock | structural check passed for `requirements-dev.in` and `requirements-dev.lock` |
| install lock | structural check passed for `requirements-install.in` and `requirements-install.lock` |
| minimum lock | structural check passed for `requirements-min.in` and `requirements-min.lock` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 14 source files` |

The live Git index was read-only in this review environment. I copied that
index to a temporary location, staged this review into the copy, confirmed
that `git ls-files` included this path, and ran the scanner's no-argument
command with that index. This file was therefore one of the scanner's actual
inputs even though the live index could not be changed. No commit was made.

## Round-2 closure verification

I did not treat a repair test as independent closure evidence. Each row
records a separate current-tree execution of the failure class.

| item | judgment | remaining severity | independent closure check |
|---|---|---:|---|
| P2-C2-F1, complete joint allocation | **partly closed** | **HIGH** | I cross-checked 6,000 random small grids against brute-force enumeration: no disagreement, with a peak of 249 loop iterations. I proved the subset-sum and margin prunes are necessary-only and that the failure key contains the complete future state. I then built two genuine profiles. A 6-row unrepresentable source produced an invented joint grid with no answer and lost six exact facts. A 2,710-row producer profile exhausted the default budget after 200,001 loop iterations; the same walk found an answer after 218,216 iterations when given a larger budget. Details are P2-C3-F1. |
| P2-C2-F2, numeric-style placement | **closed** | none | A genuine column of eleven fractional values followed by forty whole values published `plain: 40, decimal: 11`. Seed 0 wrote exactly 40 and 11, and no `numeric_styles` deviation. Reversing whole and fractional values in direct `_style_places` probes also kept the only point-free carrier for `plain`; the look-ahead, not iteration order, decided it. |
| P2-C2-F3, style-preserving invention | **closed** | none | I independently profiled three 36-row columns with three spellings of one value: decimal, lower-case exponent and upper-case exponent. Each twin retained its one published style in all 36 cells, retained three raw and folded identities, and named no style or distinctness miss. Direct spelling probes confirmed that inserting zeros after the sign preserves value and style for every non-plain family. |
| P2-C2-F4, numeric-cardinality bounds | **closed** | none | On producer values 0 through 4, both cardinalities were measured as published 5, achieved 4, bounds 4..5, inside. I then passed the shipped measurement a broken 36-cell decimal column using only one spelling where its cells supplied at least three. Both cardinality records returned `inside: false`; the bounds can fail and are not restated achievements. |
| P2-C2-F5, exact temporal endpoints | **partly closed** | **HIGH** | The local-clock source scenario now writes the seconds field of 60 unchanged. I then edited a genuine offset-bearing profile to the loader-valid `datetimes_read_at: utc` form with the same seconds field. Seed 3 wrote the following minute and reported `latest` as missed. The contract row says “No corner, no exception,” while later contract and method paragraphs permit exactly this miss; the new guard passes that contradiction and one test positively requires it. Details are P2-C3-F2. |
| P2-C2-F6, fold collisions by edge spacing | **closed** | none | For each of seeds 0, 1, 3 and 17, I generated declared identifiers from the four lengths 1, 2, 2 and 3. Both a letter-bearing source and a figures-only source came out with four raw identities and one folded identity, exact length ends, and no deviation. The figures-only run proves edge spacing, not a wider case search, supplied the collision. |
| P2-C2-F7, stale independent identifier rule | **closed** | none | The independently reconciled `identifier_whole_numbers` case now covers 12 cells, eight groups, all three alphabet bands and `all_whole_numbers: true`. Its oracle result and implementation result agree byte for byte. I also confirmed mechanically that the oracle imports only `argparse`, `datetime`, `fractions`, `json`, `math`, `struct` and `sys`. P2-C3-F3 addresses branches the nine cases still do not reach. |
| P2-C2-F8, false per-value walk bound | **closed** | none | With empty history, the shipped walk stepped past a wrong-class candidate to cursor 2, two missing-value candidates to cursor 13, and 31 compact-date candidates to cursor 10,133. A letter-only ask over a figures family stopped at the normative 4,096 steps and returned no value. The method now states the family-size bound and these history-independent rejection classes, not the retired `used + 1` claim. |

## Blocking review items

### P2-C3-F1 — The exact allocator is bounded on a producer-reachable case, and its unrepresentable grid is not guaranteed to represent the source margins

**Severity: HIGH.** This is the remaining substance of P2-C2-F1 and
reopens the exact-allocation part of P2-C1-F1.

#### What is sound

The new search is a material improvement. `_reach_bits` computes the exact
bounded subset sums of the copies permitted in the current cell
(`src/synthtwin/generation.py:991-1028`). `_margins_left` tests each still
owed margin against the union of its remaining cells
(`generation.py:1062-1101`). Ignoring competition between margins makes that
test weaker, not unsafe: failure is necessary, while success is not treated
as sufficient. `_cell_room` imposes only the remaining row/column capacity
and the forced last-cell equality (`generation.py:968-988`). None of those
prunes can remove an answer.

The failure memoisation key is also sound. It is
`(cell, left, rows_left, columns_left)` (`generation.py:1247-1255`). Group
identities have already been compressed by identical `(size, permission)`
keys (`generation.py:920-930`), and the fixed cell order leaves no other
history capable of changing a future answer. My 6,000-case brute-force
comparison found no counterexample to the unbounded walk.

#### The completeness claim still fails in two independent ways

First, the public solver is not that unbounded walk. It installs a 200,000
budget (`generation.py:784`, `:931-937`) and decrements it on every trip
through the main loop (`generation.py:1241-1246`). That is not the claimed
number of distinct states entered: retries of another fill under an existing
state consume the budget too. The nearby explanation even says that the
ordering keeps a producer profile quick “now that no ceiling stops the
walk” (`generation.py:891-901`), although the ceiling remains.

I constructed a 2,710-row `numeric_unrepresentable` source through the real
producer. Its 38 anonymous groups produce class margins
`[592, 879, 0, 424, 815, 0]` and sign margins `[1578, 540, 592]`. With the
shipped budget, `_allotted_pairs` returned no answer after 200,001 loop
iterations. With the same groups, margins, permissions and order, but a
1,000,000 budget, it returned a valid joint answer after 218,216 iterations.
The method permits a work ceiling only if no producer description can reach
it, and says the implementation must demonstrate that headroom
(`docs/spec/generation-method-v1.md:1801-1815`). The two existing producer
batteries' observed maximum of 96 is a sample, not that proof; this producer
profile refutes it directly.

Second, the claim that the real source is always a packing of the grid is
false for `numeric_unrepresentable`. The profile publishes overlapping
marginals, not their cross-tabulation. The generator assigns out-of-range
rows to “whole” first with `min(...)`, then to “fraction,” and derives six
class quotas from that invented split (`src/synthtwin/generation.py:4552-4561`).
It then asks the joint class/sign allocator to solve those invented cells
(`generation.py:4649-4669`) and falls back to two sequential allocations
when it cannot (`generation.py:4670-4680`). The source table proves only that
*some* cross-tabulation of the published marginals exists, not that this
particular unpublished cross-tabulation exists.

The smallest counterexample is a genuine six-row source with four raw groups
of sizes 2, 2, 1 and 1. Its profile publishes:

- `n_numeric = 2`, `n_out_of_range = 1`, `n_contradictory = 3`;
- `n_whole = 2`, `n_fraction = 1`, `n_whole_unknown = 3`;
- `n_negative = 3`, `n_positive = 0`, `n_sign_unknown = 3`.

The implementation invents class quotas `[3, 1, 0, 1, 1, 0]`; there is no
whole-group joint assignment of those cells and the sign margins. Seed 0
therefore wrote and named these misses:

| exact fact | published | achieved |
|---|---:|---:|
| `n_numeric` | 2 | 1 |
| `n_contradictory` | 3 | 4 |
| `n_fraction` | 1 | 0 |
| `n_whole_unknown` | 3 | 4 |
| `n_negative` | 3 | 2 |
| `n_sign_unknown` | 3 | 4 |

The finished recount at `generation.py:5057-5075` makes this loss honest;
it does not make it conforming. The contract keeps all six facts exact for
this role (`docs/spec/profile-contract-v4.md:1962-1968`), and the ratified
plan does the same (`docs/plans/phase-2-generator.md:659-661`).

**Concrete failure scenario.** A researcher profiles that six-row source
and develops one filter for fractional values and another for negative
values. The real table has one fractional row and three negative rows; the
twin has zero and two. The report names both differences, but owner decision
4 promises exact feasible counts, not a warning that the generator selected
an infeasible unpublished cross-tabulation.

**Required repair.** Preserve the safe prunes and the complete state key,
but do all of the following:

1. redesign this allocation so it uses only relationships present in the
   profile, and require the six-row producer case to
   finish with no exact-fact deviation;
2. remove the reachable work fallback, or provide a proof that the retained
   limit is unreachable over the entire producer output domain rather than
   two measured batteries; and
3. count what the specification calls states if the normative ceiling still
   uses that word. A counter incremented on every loop iteration is not that
   quantity.

Add the six-row case and the 2,710-row work case as genuine
producer-to-loader-to-generator regressions. The large case must assert that
the joint route found the answer, not merely that the eventual recount happened
to match after fallback.

### P2-C3-F2 — The exact temporal obligation is displayed, then weakened elsewhere and violated by code

**Severity: HIGH.** This is the remaining substance of P2-C2-F5 and the
temporal part of P2-C1-F6/P2-C1-F8.

The ratified plan says `earliest` and `latest` are exact in owner decision
5's representation (`docs/plans/phase-2-generator.md:607-612`). The contract
matrix now repeats that and says “No corner, no exception”
(`docs/spec/profile-contract-v4.md:1869-1875`). The method likewise says
there is no leap-second exception (`docs/spec/generation-method-v1.md:1169-1179`).

The agreement stops there. Later contract text permits a synthetic
shared-clock description with a seconds field of 60 to miss and be reported
(`profile-contract-v4.md:1924-1937`), and the method gives the same exception
(`generation-method-v1.md:1181-1206`). Code implements it directly:
`_endpoint_cell` returns `None` for `datetimes_read_at == "utc"` with
seconds 60 (`src/synthtwin/generation.py:1962-1967`), the caller writes the
ordinal fallback (`generation.py:2732-2745`), and the finished cell is
recounted and reported (`generation.py:2750-2757`, `:2807-2835`).

The strict loader accepts this canonical profile. My edited genuine profile
loaded with `latest = 2024-11-02 09:55:60`; seed 3 achieved
`2024-11-02 09:56:00`, and the report named the miss. Saying the producer
does not emit the pair does not restore an exact obligation on every
loader-valid description. The contract cannot simultaneously say “no
exception” and specify what the exception reports.

The new guard is not semantically capable of preventing this recurrence. It
asserts the exact phrase in the matrix cell and counts one numbered datetime
corner (`tests/test_p2c2f5_temporal_endpoints.py:253-297`), but it ignores the
unnumbered exception after that corner. Another test positively constructs
the UTC profile and requires the endpoint miss
(`test_p2c2f5_temporal_endpoints.py:210-247`). Thus the suite is green while
the obligation is already softened again.

**Concrete failure scenario.** A consumer accepts any profile that the v4
loader accepts and relies on the exact latest instant for a closed upper-bound
filter. On the UTC profile above, the consumer develops the filter against a
twin whose latest instant is the following minute. The report is honest, but
the exact contract the consumer relied on is false.

**Required repair.** Choose one result at the ratified boundary and make all
four surfaces agree: plan, contract, method and code. If no cell can represent
this accepted combination, either make the strict loader reject the
internally incompatible pair under a reviewed invariant, or obtain an owner
amendment changing the disposition. Do not retain exact wording beside an
exception. Replace the phrase-shape guard with a semantic mutation that adds
an exception anywhere in either specification and must fail.

This audit looked for the same lowering pattern elsewhere. The other instance
found is P2-C3-F1: G9.5 permits a work-ceiling fallback while retaining the
“exact whenever an answer exists” rule, on the assertion that no producer can
reach it. The producer-reachable case above disproves the asserted scope. I
found no third lowered obligation outside the already explicit and
owner-authorized identifier length corner, withheld-offset corner, numeric
cardinality envelopes and label-cardinality envelope.

## Carryable condition

### P2-C3-F3 — The independent oracle is sound where it runs, but it has nine cases and leaves important new branches unexercised

**Severity: MEDIUM. Nonblocking carry to round 4.**

The oracle remains mechanically independent. Its AST imports are exactly
`argparse`, `datetime`, `fractions`, `json`, `math`, `struct` and `sys`; it
imports neither the implementation nor numpy, pandas or ctypes. The
provenance guard still blocks ctypes, which is why adding numpy would fail
before writing a vector. I independently exercised the arithmetic proof:

- an exact midpoint between 1.0 and its next neighbour rounded to the even
  1.0, while the odd-neighbour mutant was refused;
- a negative rational below the smallest subnormal rounded to signed zero,
  while positive zero was refused; and
- a value beyond the finite binary64 range was refused rather than certified.

Regeneration reported **210 proved published numbers across 9 cases, beside
270 named whole-number counts**. The rebuilt file was byte-for-byte equal to
the committed 83,723 bytes, whose SHA-256 is
`cf85c2a0345042a2f2df9bab21e368c01153194c1dd37aa4ff09829d0a14bde3`.

The user's stated count of ten is not the current artifact's count. There are
nine cases, and G14.3 itself calls the repaired identifier case the ninth
(`docs/spec/generation-method-v1.md:2629-2657`). The nine cover integer
rounding, point-free look-ahead inside an exponent-heavy style map, date,
quarter, offset, parsed/unparsed mixing, label variants, case-based identifier
collisions and all three whole-number identifier bands.

They do not cover `numeric_unrepresentable` at all, do not cover the
free-text joint class/alphabet grid, do not force the edge-spacing collision
route, and do not assign a cell the literal `decimal`, `leading_zero` or
`leading_plus` styles. The implementation bug in P2-C3-F1 therefore leaves
all committed vector bytes unchanged. So would a mutant that removed edge
spacing while retaining case flips. This is the same failure mode P2-C2-F7
identified: an unreached branch can carry a withdrawn or defective rule
without disturbing byte equality.

**Concrete failure scenario.** A future repair changes
`_unrepresentable_families` back to sequential class and sign allocation.
Every one of the nine committed vectors and all 210 numeric proofs still
binds byte for byte, while the six-row producer case in P2-C3-F1 again loses
six exact facts. A reviewer treating vector equality as branch coverage would
certify the regression.

**Round-4 checkpoint.** Before the round-4 code review, add
implementation-independent, provenance-bound reference cases that force:

1. joint class/sign allocation for `numeric_unrepresentable` and joint
   class/alphabet allocation for free text;
2. an identifier fold collision that case changes alone cannot build; and
3. literal decimal, leading-zero and leading-plus placements.

Each must compare the independent expected cells with implementation bytes
and must be shown to fail when its named branch is removed or reverted. The
cases may live in a second small fixture if the existing fixture's 100,000-byte
limit would otherwise be exceeded.

## Owner-decision audit

All eleven P2-D0 decisions were traced from the plan through producer, loader,
generation and report. “Carried” below means both behavior and the stated cost
were found; it does not mean every neighboring Phase 2 obligation passed.

| owner decision | current judgment | independent evidence and cost disclosure |
|---:|---|---|
| 1. additive axes | **carried** | Producer and loader round-tripped all three axes. Generation dispatches on `quality_state`, `statistical_type` and `structural_role`, not `role` (`src/synthtwin/generation.py:4943-4969`). The misrouting and empty-declared-identifier tests passed. |
| 2. multiplicity parity | **carried** | Genuine free-text and unrepresentable profiles carried anonymous occurrence maps; generated groups retained those sizes. The absence of an unrepresentable width fact and the invented 400-figure width are named in every such report (`generation.py:4531-4549`). P2-C3-F1 concerns other exact marginals, not loss of the multiplicity map. |
| 3. eight-slot relationship manifest | **carried** | The loader required all eight keys and null values; generation checked the empty seam; report/help continued to state no cross-column or row structure. Non-null and missing-slot mutations passed as refusals. |
| 4. exact-count allocation | **not carried** | The forced-row-equality/privacy cost is disclosed honestly in CLI, report, README and SECURITY. Exact feasible counts nevertheless fail in P2-C3-F1. |
| 5. temporal shape | **not carried completely** | Date, quarter, minute, second, subsecond and ordinary offset-bearing shapes reprofiled correctly. The source-format loss is disclosed as report-only. The accepted UTC endpoint exception in P2-C3-F2 violates the decision's exact endpoint consequence. |
| 6. identifier length wins | **carried** | In the infeasible one-character case, lengths stayed exact, all three distinctness facts were named, and the report stated the join/de-duplication consequence (`generation.py:3692-3720`, `:5112-5177`). Outside that corner, the edge-spacing probes retained both distinctness counts. |
| 7. multiple numeric spellings | **carried** | Alternate spellings were used only to satisfy published cardinality and style needs; a column already meeting its cardinality remained byte-plain. The report measured both cardinalities. |
| 8. leading-zero invention family | **carried** | The 4,098-spelling boundary remained closed in the focused round-1 check. Decimal and both exponent probes showed the family now works inside every non-plain style without changing value or inferred form. No fixed invention ceiling was found. |
| 9. published label variants | **carried** | The producer named only variants at or above the floor and placed smaller ones in an anonymous occurrence multiset (`src/synthtwin/taxonomy.py:2769-2816`). The twin retained published counts and invented replacement spellings for the anonymous part. |
| 10. numeric writing styles | **carried** | Producer pooling at the floor is explicit (`taxonomy.py:2987-3028`), the loader enforces both the floor and total (`src/synthtwin/contract.py:3642-3680`), and the independent F2/F3 probes reproduced exact finished-text counts. The profile publishes form counts only, not magnitudes or spellings, and SECURITY says so. |
| 11. complete Unicode-fold variant contract | **carried** | The exact Unicode case-fold variant in my disclosure probe was withheld anonymously; the complete-profile guard and loader enforced parent binding and multiset totals (`contract.py:3111-3166`). SECURITY accurately says the delta is Unicode folding after trimming, not capitalization alone. |

The decisions taken against the implementer's recommendation — identifier
length, label-variant preservation and the corrected numeric spelling family
— retain their recorded cost statements. I found no cost described more
narrowly in public text than in P2-D0. Decisions 4 and 5 fail because the
code does not meet them, not because their costs are hidden.

## Boundary, disclosure, determinism and silent-wrongness checks

### Installed-entry boundary

I exercised the installed `.venv/bin/synthtwin` entry rather than importing
`generation.generate` alone:

1. the installed profiler made a genuine profile;
2. I moved the source table away from the path recorded for it;
3. the installed `generate` command ran at seed 17 and wrote both expected
   artifacts; and
4. Python's import trace from process start showed only
   `synthtwin.canonical`, `cli`, `contract`, `errors`, `generation`,
   `parsing`, `paths`, `rendering` and `writing` in the first-party closure.

`synthtwin.reading`, `synthtwin.profile` and pandas were never reached. The
authorized `numpy.random` dependency was reached; its normal initialization
loads compiled internals and ctypes inside numpy, but no synthtwin source
imports or calls ctypes or any other native interface. The static closure
scan then checked all 14 product modules and found zero network, subprocess,
dynamic-loader, native-interface or unapproved-import violations. I found no
path, handle, table object or raw-cell collection entering a generation
signature.

### Disclosure floor and withheld content

I built a 63-row, two-column source with one published folded label, two
published exact variants (30 and 20 rows), one exact variant used by 3 rows,
one separate label used by 10 rows, 60 plain numeric cells and one exact
exponent spelling used by 3 rows. With the default floor of 11, the profile
contained:

- the two 30/20 exact variants;
- `variants_withheld: {"3": 1}` for the third variant;
- `suppressed_level_counts: [10]` for the withheld whole label; and
- `numeric_styles: {"(withheld)": 3, "plain": 60}`.

I byte-searched the complete profile, profiler summary, twin CSV and twin
report for the exact withheld variant, whole label and numeric spelling. All
three appeared only in the source and in none of the four artifacts. This is
an information-flow check, not a promise of mathematical non-equality: the
repository correctly states that a profile-derived invention can happen to
equal a real value with nothing copied.

### Determinism

I generated the 240-row every-role profile at seed
`18446744073709551615` in two fresh installed processes with
`PYTHONHASHSEED=1` and `PYTHONHASHSEED=999`. The twin SHA-256 was
`9a9c3e3598cba249daba34469b5467557b3635233bbc445eb815361d97ae6f1f`
in both runs; the report SHA-256 was
`534d30cfaf7a5c612605b413a5aadcfcab03f633f0fb25a92840200eeef690fd`
in both. The explicit allocation stack, bitsets, dictionaries and sets did
not introduce hash-order-dependent bytes in this cross-process probe.

### Silent wrongness

I recounted the finished outputs in every independent closure probe. The six
misses in P2-C3-F1 were all present under their exact contract field names;
the UTC endpoint miss in P2-C3-F2 was also present with published and
achieved values. Numeric cardinality bounds that I forced outside their
envelope became deviations. Edge collision, style, sign, whole/fraction,
class, alphabet and endpoint successes produced no false miss.

I found **no current published fact that the exercised generator misses
without naming**. That does not downgrade P2-C3-F1 or P2-C3-F2: both violate
exact obligations, but neither remains silent.

## Round-1 reopening spot check

The round-2 repairs rewrote the same allocation, temporal and invention
surfaces, so I reran one capable probe from every non-allocation round-1
class. The 25/26-value domain boundary returned/refused within its deadline;
the finished-document guard rejected a source spelling at an existing note
path; the approximation inventory and a rung-collapse mutant failed in the
intended directions; 4,098 zero spellings completed; ordinary temporal
shapes reprofiled; and decimal form serialization remained exact. Those
twelve focused tests all passed.

P2-C1-F2, F3, F4, F5 and F7 did not reopen. P2-C1-F1's exact-allocation
part remains open through P2-C3-F1. P2-C1-F6 and the corresponding
specification-reconciliation part of P2-C1-F8 remain open through P2-C3-F2.

## Coverage statement

Surfaces examined:

- installed entry point, command prologue and generation-only import closure;
- profile-v4 producer, canonical serializer, strict loader and publication
  guard;
- joint and single-axis allocation, bitset reachability, necessary-condition
  pruning, explicit-stack backtracking, failure memoisation and fallback;
- numeric value/style placement, style-preserving invention, raw/folded
  supply envelopes and finished-cell recounts;
- label variants, anonymous withheld-variant multiset, suppressed labels and
  Unicode trim/case-fold behavior;
- identifier and unrepresentable invention, edge-spacing collisions,
  multiplicity, alphabet, class, sign and whole/fraction paths;
- every temporal resolution/precision route relevant to the repaired
  endpoints, including local and shared-clock seconds-field boundaries;
- independent oracle imports, proof arithmetic, case list, regeneration,
  provenance binding and branch coverage;
- all eleven owner decisions and their public cost disclosures;
- twin/report disclosure, public claims, zero-code commands, locks,
  attestation and all required checks.

Properties and attack classes checked:

- source-table reachability, path locality, network/process/native-interface
  and dynamic-loading surfaces;
- silent statistical wrongness and validator/report honesty;
- type misrouting through role versus the three axes and through numeric form;
- exact versus approximated disposition drift, especially obligation
  lowering in normative prose;
- completeness of allocation prunes, search termination, reachable work
  ceilings and unsound memo keys;
- hidden randomness, hash iteration, extra draws and cross-process byte
  determinism;
- small-cell-floor bypass through labels, variants and numeric forms;
- withheld-content flow into profile, summary, twin or report;
- independent-oracle contamination, unproved rounding, unbound bytes and
  unreached specification branches;
- ordinary boundary, capacity, calendar, clock, collision and report edge
  cases.

Not proved by this review: universal performance over every loader-valid
hand-made profile; byte identity across operating systems or numpy versions;
or non-equality between invented and real values. The project does not claim
the last of those.

## Explicit verdict

**REJECT, blocked on P2-C3-F1 and P2-C3-F2.** P2-C3-F3 may carry only to
the round-4 checkpoint stated under that item. No other condition is being
carried.

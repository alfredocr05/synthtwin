# Phase 2 code review, round 4

Date: 2026-08-12  
Reviewer role: adversarial reviewer under repository `AGENTS.md`  
Scope: the current staged Phase 2 tree, reviewed against the current
ratified plan, profile contract and generation method. All citations below
were re-derived from this tree.

## Result

**REJECT.** The fourth occurrence of obligation-lowering is present. The
repair restored the exact temporal sentence at the places round 3 named,
but expressly permits the same endpoint loss at a calendar boundary, and
the new guard allowlists that exception. Two other producer-reachable exact
obligations are also stated as misses the implementation may report:
free-text alphabet counts and numeric writing styles. The implementation
does miss both. Finally, the independent oracle and implementation still
write different bytes for `identifier_edge_spacing`; marking that required
comparison strict xfail does not bind an implementation to the oracle.

The blocking items are **P2-C4-F1 through P2-C4-F4**. The bounded items that
may be checked in the fifth and final round are **P2-C4-C1 through
P2-C4-C4**. The successful command results do not alter this verdict: the sole xfail is one
of the blockers, and two affirmative tests require exact-count losses.

Severity meanings in this review:

- **HIGH**: blocks Phase 2 code ratification because a ratified exact fact,
  owner decision, or independent byte oracle is violated.
- **MEDIUM**: a bounded proof or specification gap that does not add a
  second blocking product failure beyond a named HIGH item, but must close
  at the final checkpoint.
- **LOW**: an inaccurate audit statement with no demonstrated product
  consequence; still bounded for correction because provenance text must
  be literal.

## Commands and exact results

| check | result |
|---|---|
| full suite, `.venv/bin/python -m pytest -p no:cacheprovider` | 2,343 collected; **2,312 passed, 30 skipped, 1 xfailed** in 72.64 s |
| focused closure run over the round-3 allocator, temporal and oracle files | **140 passed, 1 xfailed** in 3.27 s |
| round-1/round-2 repair-file spot-check | **301 passed, 26 skipped** in 21.56 s |
| offline scan, `.venv/bin/python tools/offline_scan/scan_imports.py src/` | `scan_imports: checked 14 Python file(s) under 'src': 0 violation(s).` |
| provenance | `Provenance check passed: no unlisted data-format files; every manifest fixture matches its generator output.` |
| development lock | structural check passed for `requirements-dev.in` and `requirements-dev.lock` |
| install lock | structural check passed for `requirements-install.in` and `requirements-install.lock` |
| minimum lock | structural check passed for `requirements-min.in` and `requirements-min.lock` |
| ruff | `All checks passed!` |
| mypy | `Success: no issues found in 14 source files` |
| signed attestation | signature valid; exact v2 shape, scanner tree, manifest, header bindings and counts all match |
| decontamination, review staged in a copied index | `decontamination: clean` |

The full suite exits zero only because the failed oracle comparison is
marked expected. The comparison itself is not passing.

## Round-3 closure table

| item | judgment | remaining severity | independent closure check |
|---|---|---:|---|
| P2-C3-F1, unpublished split and reachable work ceiling | **Closed on both reported inputs; the general exact-allocation claim is reopened on a different producer path.** | **HIGH**, P2-C4-F2 | I described the six-row source again through the real producer and generated it with the greedy fallback made to raise: none of its ten exact class, whole-status or sign counts missed. I independently rebuilt the 2,710-row, 38-group source, instrumented the walk, observed **261,805 states**, obtained an answer, disabled the fallback and observed no exact-count miss. I then described a default-settings 12-row free-text source with occurrence groups 1, 5 and 6. Its own values realize `n_code_alphabet = 5`; every seed 0 through 63 generated only 1 and named the miss. P2-C3-F1's two witnesses close, but the method's claim that a producer's own values always remain representable in the grid does not. |
| P2-C3-F2, exact temporal endpoints | **Not closed.** The local leap endpoint and the two D10/D11 cases named in round 3 close, but the same exact obligation is lowered at the calendar boundary. | **HIGH**, P2-C4-F1 | I edited a genuine 40-row, two-offset description to publish earliest `0001-01-01 00:00:00` at endpoint offset `-05:00` on the shared clock. The loader accepted it; seed 3 wrote a cell that reads as no date and reported `earliest` as missed. Separately, a local-clock endpoint with seconds field 60 wrote one cell with that field unchanged and named no endpoint deviation, and the loader refused the shared-clock/60 pair under D10. This exercises both the repaired branch and the exception left behind. |
| P2-C3-F3, oracle branch coverage | **Not closed as a byte-binding checkpoint.** The four required branch cases and their four branch-removal mutants are real, but one of the four implementation comparisons fails. | **HIGH**, P2-C4-F4 | I loaded all 13 cases from both files, gave the implementation each recorded seed, and compared cells. `identifier_edge_spacing` differed in the second and third one-based slots; the implementation length sequence was 3, 2, 3, 1 where the oracle's was 3, 2, 2, 1. I also ran the four branch-removal tests directly: all four passed by changing the case or stopping its construction. |

## Exhaustive exact-obligation audit

I took the field inventory from the ratified matrix
(`docs/plans/phase-2-generator.md:494-666`) and searched **all three**
governing documents for every exact field, its aliases, its role-specific
paragraphs, and the vocabulary used for a lesser outcome: approximation,
report-only treatment, fallback, recount, miss, clamp, exception and
refusal. I then read every hit in context rather than treating grep as a
verdict. This included all EXACT-CONTROL fields, not only observable
counts.

| matrix family audited | result of the three-document audit |
|---|---|
| document shape and controls: document `n_rows`, `n_columns`, header decision, name, position, role and three axes | **One bar.** I found no statement making an EXACT-CONTROL field advisory or substituting a CSV recount for dispatch evidence. The installed no-header/header routes and column-order tests pass. |
| universal and empty fields: presence, absence, four parse classes, empty distinctness | **Not one bar for free text.** The matrix makes all four class counts exact (`phase-2-generator.md:575-589`), but G9.5 allows the packing fallback and report path (`generation-method-v1.md:1859-1867`). P2-C4-F2 proves a producer reaches it for an alphabet count after the implementation invents length/word-to-group associations. |
| numeric endpoints, sign/count facts, integer fact, distinctness and styles | The numeric sign-repair endpoint movement is expressly authorized by plan feasibility rule 4 (`phase-2-generator.md:677-682`), and the two-sided distinctness fallback is in the matrix. **Numeric styles are softer:** owner decision 10 says each published count is written (`phase-2-generator.md:207-253`), the contract says EXACT-OBSERVABLE (`profile-contract-v4.md:1621-1628`, `1900-1907`), but the method permits an unplaceable map to miss (`generation-method-v1.md:876-885`). P2-C4-F3 proves a producer reaches that passage. |
| labels: levels, visible variants, withheld-variant multiplicities, suppressed counts and folded distinctness | **One bar.** The only softer raw-distinctness outcome is the matrix's own bounded case where published and withheld variant facts do not supply enough spellings. No additional exception was found. |
| datetime endpoints, ladder endpoints, precision, offsets, clock and unparsed count | **Not one bar.** The matrix says endpoint exactness has “No corner, no exception” (`profile-contract-v4.md:1924-1935`), while G7.5 permits and reports the calendar-boundary miss (`generation-method-v1.md:1207-1224`) and G12 repeats it (`generation-method-v1.md:2208-2218`). This is P2-C4-F1. The withheld-offset loss is the owner-authorized matrix corner and was not counted as drift. |
| free-text ends, alphabet counts, multiplicity and distinctness | **Not one bar.** Besides the producer-reachable alphabet loss in P2-C4-F2, the contract and method allow an exact word extreme to be clamped and reported on a hand-authored inconsistent description (`profile-contract-v4.md:2010-2018`; `generation-method-v1.md:1890-1897`). This is part of P2-C4-C1. |
| identifier length, whole-number fact, alphabet counts, multiplicity and distinctness | The three distinctness losses inside owner decision 6's length-capacity corner match the plan. **A different exception does not:** the contract and method let `all_whole_numbers` miss on a one-character, outside-the-figures description (`profile-contract-v4.md:2020-2026`; `generation-method-v1.md:1907-1932`). This is part of P2-C4-C1. |
| unrepresentable whole/fraction/sign/multiplicity/distinctness | **One bar on producer descriptions and on both round-3 witnesses.** The generalized three-margin path now meets the published counts without a work ceiling. The blanket no-packing fallback still inherits P2-C4-C1's normative conflict for inconsistent hand-authored descriptions. |

Thus the repair's exhaustive-temporal-wording claim is false, and the
same failure mode has recurred for a fourth time. The guard is not merely
missing the calendar passage accidentally. Lines 696-724 of the temporal
endpoint test put that passage in the method allowlist and describe the
calendar outcome as legitimate. That check does not establish uniform
endpoint exactness.

## Blocking review items

### P2-C4-F1 — The exact temporal obligation was lowered a fourth time

**Severity: HIGH. Blocking.**

The contract matrix says `earliest`, `latest` and both ladder ends are
EXACT-OBSERVABLE with no corner and no exception
(`docs/spec/profile-contract-v4.md:1924-1935`). Its repair history also
says an exact endpoint may not become a report line
(`docs/spec/profile-contract-v4.md:1979-2003`). G7.5 nevertheless says a
loader-accepted endpoint near year 0001 or 9999 may read back as no date and
be named in the report (`docs/spec/generation-method-v1.md:1207-1224`). G12
lists the same permitted deviation (`docs/spec/generation-method-v1.md:2208-2218`).
The implementation performs it (`src/synthtwin/generation.py:2899-2942`),
and an affirmative test requires it (`tests/test_p2c2f5_temporal_endpoints.py:449-482`).

**Concrete failure scenario.** Start from the producer's 40-row
offset-bearing datetime profile, retain `datetimes_read_at: utc`, set the
first instant and ladder minimum to the first second of year 0001, and set
the first endpoint offset to five hours behind the shared clock. The loader
accepts the profile. Seed 3 writes an endpoint cell outside the supported
calendar, its read-back is not a date, and the report names `earliest` as
missed. A consumer relying on the public exact endpoint row can construct a
closed lower-bound filter that the twin does not exercise.

The scenario is not producer-reachable, but that does not authorize a
contract contradiction. The existing D10 pattern shows the bounded repair:
the loader has the clock, endpoint text and endpoint offset needed to refuse
the pair before generation.

**Required closure.** Extend D10 to reject both lower- and upper-calendar
offset overflow pairs; remove the calendar exception from G7.5, G12,
generation and its affirmative test; and make the wording guard require
zero endpoint-loss passages rather than allowlisting this one. The closure
check is the exact edited profile above refusing under D10, the local
seconds-60 profile still loading and round-tripping exactly, and an
exhaustive three-document search finding no lesser endpoint outcome.

### P2-C4-F2 — Pre-assigning text shape makes a producer-feasible exact margin disappear

**Severity: HIGH. Blocking. Reopens P2-C1-F1 and the general claim behind
P2-C3-F1.**

The plan makes free-text length ends, word ends, alphabet counts and the
multiplicity map exact (`docs/plans/phase-2-generator.md:634-637`). The
method says a producer profile always has a packing because the source
values are one and says the walk receives only published relationships
(`docs/spec/generation-method-v1.md:1844-1867`). The code first assigns
lengths and word counts to anonymous occurrence groups independently
(`src/synthtwin/generation.py:4121-4180`), then asks the generalized packing
walk to place class and alphabet margins only inside that invented shape
(`src/synthtwin/generation.py:3929-4000`). It can thereby manufacture an
infeasible grid from feasible published margins.

**Concrete failure scenario.** With default settings, describe a one-column
source containing one two-word, three-character value, five copies of a
one-character code-alphabet value, and six copies of a two-character value
outside that alphabet. The producer emits `free_text`, groups 1, 5 and 6,
and `n_code_alphabet = 5`; the source itself is the exact assignment. The
shape walk pins the longest length and largest word count to the five-row
group, making that group ineligible for the code alphabet. Seed 0 writes
one code-alphabet cell and reports 1 against 5. I repeated seeds 0 through
63; all 64 missed.

The miss is named, so this is not silent reporting. It is still forbidden
statistical wrongness: a reader of code-shaped text sees a different count,
and owner decision 4 did not authorize trading it for an arbitrary
length-to-multiplicity association the profile never published.

**Required closure.** Put every exact relationship that constrains these
anonymous groups into one complete allocation, including the length and
word extreme carriers, or otherwise prove that the shape chosen before the
grid preserves every feasible exact assignment. Add the producer scenario
above end to end, forbid the fallback for it, and add a mutant that restores
the current pre-assignment and must fail. Re-run the earlier six-row and
2,710-row cases to ensure the generalized repair does not regress them.

### P2-C4-F3 — A producer's exact numeric-style map is knowingly missed

**Severity: HIGH. Blocking. Reopens P2-C2-F2 and violates owner decision
10.**

Owner decision 10 says the twin writes every numeric style in its published
count because the form controls the type a reader infers
(`docs/plans/phase-2-generator.md:207-253`). The contract repeats the exact
bar (`docs/spec/profile-contract-v4.md:1621-1628`, `1900-1907`). The method
instead says a ladder with point-bearing ends and too few intervening
carriers may miss a point-free quota and report it
(`docs/spec/generation-method-v1.md:852-885`). The implementation changes
only whole strata while refusing to move endpoints, cross zero or reuse a
stratum value (`src/synthtwin/generation.py:2607-2670`); its own affirmative
test requires the producer miss (`tests/test_p2c2f2_style_placement.py:200-226`).

**Concrete failure scenario.** Describe 51 numeric cells: 11 copies of
`1.5`, 20 copies of `100`, and 20 copies of `200.5`. The producer publishes
20 `plain` and 31 `decimal` cells. Its own values prove that exact map is
compatible with every published fact. Seed 0 writes only 12 plain cells and
39 decimal cells; all seeds 0 through 63 did the same. The report names both
counts, but code that infers or validates a column's lexical type is trained
on the wrong mix.

**Required closure.** Remove the producer-reachable miss from G6.4 and the
affirmative test, and make exact style capacity take precedence over the
approximated ladder degrees of freedom as the owner decision requires. The
closure check is the 51-row producer profile matching 20/31 for seeds 0,
1, 63 and the vector seeds, plus a style-removal mutant failing. Search all
three governing documents again for every style-miss passage.

### P2-C4-F4 — A strict xfail is not independent byte binding

**Severity: HIGH. Blocking. P2-C3-F3 remains open.**

The method calls the partners of one parent one family and orders that
family by ascending total edge spacing, trailing first within one total
(`docs/spec/generation-method-v1.md:1517-1533`). Each slot then filters that
family by its permitted length window (`docs/spec/generation-method-v1.md:1538-1544`).
That supports the oracle. After the length-three partner consumes the first
member permitted by its pinned window, the next unrestricted slot's first
unused one-space member is the trailing-space form. The implementation
instead derives a new ordinal from the destination slot and restarts the
slot-local lookup at the second member (`src/synthtwin/generation.py:3518-3589`,
`3637-3655`).

**Concrete failure scenario.** Load `identifier_edge_spacing` and generate
with seed 113. Oracle and implementation both satisfy four raw spellings,
one folded identity, length range 1 through 3 and the alphabet facts. They
still differ in the second and third one-based output slots: the oracle uses
the two one-space placements before any two-space mixed placement, while
the implementation skips one one-space member and writes a three-character
member. Cell and CSV-byte comparison fails. The test converts that failure
to a strict xfail (`tests/test_generation_reference.py:413-469`).

The loss is method determinism, not column fidelity. That is precisely what
the independent artifact exists to detect; two conforming implementers may
not write different bytes and call both conforming.

**Required closure.** Change the implementation to follow the oracle and
G9.3 family order, remove `DISAGREES_WITH_THE_IMPLEMENTATION` and the xfail
branch, and require all 13 implementation comparisons to pass normally.
Do not change the oracle bytes to match the implementation. The closure
check is zero xfails, exact cell and CSV-byte equality for seed 113, and the
case-flip-only branch mutant still failing.

## Bounded conditions for the final round

### P2-C4-C1 — The blanket “only jointly satisfiable” qualification exceeds the plan's named exceptions

**Severity: MEDIUM. Nonblocking only because the demonstrated cases require
hand-authored inconsistent profiles and every miss is reported.**

The contract qualifies every exact obligation by joint satisfiability and
allows a best-effort generated twin (`docs/spec/profile-contract-v4.md:1829-1851`).
That creates specific lesser outcomes for exact word extremes and
`all_whole_numbers` (`docs/spec/profile-contract-v4.md:2010-2026`), which
the method implements (`docs/spec/generation-method-v1.md:1859-1867`,
`1890-1897`, `1907-1932`). The ratified plan instead says refusal is the
generation outcome reserved for descriptions no preceding rule can satisfy
(`docs/plans/phase-2-generator.md:668-687`) and names only owner decision
6's length-versus-distinctness loss, numeric sign precedence, numeric and
label distinctness fallbacks, and withheld offsets as softer outcomes.

**Concrete failure scenario.** Hand-edit a loader-valid, one-character
identifier description to require every value to be a whole number while
placing some cells outside both published alphabets. No one-character text
can meet that combination. The current generator writes non-whole cells and
reports `all_whole_numbers`; a reader following the plan expects generation
to refuse before output. The same divergence occurs when a free-text
description requires more words than its exact maximum length can contain.

**Closure condition.** Before the final round, either remove these added
fallbacks and refuse the two concrete profiles before writing, or obtain and
record an owner amendment to the plan that names each lesser disposition.
The verification is an executable test for both profiles plus an exhaustive
exact-field prose audit with no unnamed exception.

### P2-C4-C2 — Only four of thirteen cases have the required own-branch mutant

**Severity: MEDIUM.**

G14.3 says **every** case must fail when its own branch is removed or
reverted (`docs/spec/generation-method-v1.md:2747-2776`), and the conformance
list repeats that obligation (`docs/spec/generation-method-v1.md:2899-2903`).
The test file explicitly applies that rule to “each of the four” new cases
and contains four such mutants (`tests/test_generation_reference.py:867-875`,
`878-1009`). There is no one-to-one mutant for the nine original cases.

**Concrete failure scenario.** Revert the oracle's quarter-specific ordinal
or precision branch and rebuild the oracle fixture and manifest digest.
There is no quarter-own-branch mutation test that must stop construction;
the claimed 13-of-13 proof can regress to an ordinary regenerated golden.

**Closure condition.** Add a named case-to-mutant table covering all 13 and
an assertion that its keys equal the case set; each mutant must change its
own case or stop its construction, and a vacuity assertion must show the
unmutated case builds. The four existing mutants may populate four rows.

### P2-C4-C3 — The repeatedly disputed leap endpoint is absent from the independent vectors

**Severity: MEDIUM.**

None of the 13 committed cases contains a seconds field of 60. The case list
names ordinary date, quarter and offset-bearing datetime shapes but no leap
endpoint (`docs/spec/generation-method-v1.md:2747-2768`). The method even
records that the endpoint repair changes no frozen vector for ordinary
seconds (`docs/spec/generation-method-v1.md:1160-1177`). Product tests now
exercise the local endpoint and shared-clock refusal, but an independent
implementation of the new endpoint-fields route has no byte oracle.

**Concrete failure scenario.** Restore ordinal conversion for a local-clock
latest endpoint whose seconds field is 60. The product writes the following
minute again. Every committed oracle byte remains unchanged, exactly the
coverage gap under which this obligation was lowered twice.

**Closure condition.** Add an independent local-clock seconds-60 endpoint
case, in a third file if the 100,000-byte cap requires one, plus its own
branch-reversion mutant and implementation byte comparison. The
shared-clock pair should remain a loader-refusal product test, not a vector
case.

The other unreached branches I inspected—minute/subsecond lexical shapes,
withheld-offset reporting, infeasible-domain refusals and report-only
corners—are covered by product or refusal tests and do not have the same
repeated independent-implementation dispute. I do not make them blocking
vector requirements in this round.

### P2-C4-C4 — The branch fixture's provenance import sentence is not literal

**Severity: LOW.**

The split itself is sound. The primary oracle is 190,664 bytes of source;
the branch entry point is only 2,505 bytes and executes that exact file by a
fixed sibling path. The committed fixtures are disjoint sets of 9 and 4
cases, 87,322 and 29,172 bytes respectively, each beneath the cap; both are
manifest-bound and rebuild byte-for-byte. There is one transform and one
proof layer (`docs/spec/generation-method-v1.md:2667-2690`).

The branch manifest entry nevertheless says its registered generator
imports only seven named standard-library modules
(`tools/provenance/fixture-manifest.json:5-9`). The registered entry point
also imports `os` and `runpy` (`tools/reference/make_generation_branch_vectors.py:37-55`).
The forbidden-import claim remains true, but the exhaustive positive list
does not.

**Concrete failure scenario.** A reviewer uses the manifest's “imports
only” list as the complete source-review inventory and does not inspect the
dynamic path execution performed by `runpy`; the review records a narrower
capability surface than the registered generator actually has.

**Closure condition.** State the wrapper's imports literally and say that
the executed core has the narrower seven-module list. Provenance must still
rebuild both files and the wrapper path must remain fixed inside
`tools/reference/`.

## Oracle judgment

The two-file split **preserves independence and proof discipline**. I checked
the following rather than accepting the header claims:

- both case sets are disjoint and their union is exactly 13;
- the wrapper contains no transform or proof copy and calls the core by one
  fixed sibling path;
- neither source imports `synthtwin`, numpy or pandas; the provenance guard
  would refuse numpy through its native-capability import;
- the words are committed inputs and agree with the opening words of the
  locked numpy stream in all 13 cases;
- both files' every numeric leaf is either a named whole number or has an
  exact/rational proof claim; the overflow, signed-zero, unproved-number,
  tuple and full-generator proof mutants all fail;
- both fixtures rebuild to their committed bytes and both manifest hashes
  match;
- all four new branch-removal mutants fail as intended.

Those checks support the split. They do not excuse P2-C4-F4's byte mismatch,
P2-C4-C2's missing nine mutants or P2-C4-C3's material endpoint gap.

## Installed boundary and offline guarantee

I executed `.venv/bin/synthtwin`, not an imported helper. I profiled a
40-row, two-column temporary CSV, moved the source CSV away, and invoked
`generate` from the installed entry point with seed 17. It wrote the twin
and report from the profile alone. An import-time trace from process start
contained `synthtwin.cli`, `contract`, `generation`, `parsing`, `rendering`
and `writing`, but not `synthtwin.reading`, `synthtwin.profile` or pandas.
The static offline scan then checked all 14 product modules and reported
zero violations; the mutation suite was part of the full 2,343-test run.

I also reviewed local-path validation, URL rejection, dynamic-code,
subprocess, socket and native-call scan classes, and the generate transaction
surface. I found no fresh product route to network I/O, subprocess
execution, dynamic loading, or a read of the source table. The `runpy` use
in P2-C4-C4 is tooling, not product code, and is exercised under the
provenance guard.

## Owner decisions and disclosed costs

| P2-D0 decision | judgment |
|---:|---|
| 1, additive axes | **Carried.** Required on every block, loader-checked and used at dispatch; exact-control/order tests pass. |
| 2, multiplicity parity | **Carried.** All three invention roles carry anonymous occurrence maps and ordinary paths reproduce them. |
| 3, reserved relationship manifest | **Carried.** Eight required nulls, refusal of non-null content, and public text says no cross-column structure. |
| 4, exact-count allocation | **Not carried: see P2-C4-F2.** The documented costs remain accurate. |
| 5, datetime shape | **Not carried completely.** Ordinary date, quarter, minute, second, subsecond and offset routes pass, and source lexical-family loss is disclosed; P2-C4-F1 leaves an endpoint the matrix calls exact outside the twin. |
| 6, identifier length wins only in its infeasible corner | **Carried on its owner-authorized corner and ordinary exact paths.** Duplicate, join and de-duplication consequences are printed. P2-C4-C1 is a different whole-number conflict and needs a plan disposition. |
| 7, alternate numeric spellings | **Carried.** Multiple spellings are used only to meet published counts. |
| 8, unbounded leading-zero invention family | **Carried.** The old ceiling and tighter false walk bound remain absent; type/appearance cost is disclosed. |
| 9, visible label variants | **Carried.** Visible variants reproduce exact spellings and counts; the floor applies to each. |
| 10, numeric writing styles | **Not carried.** P2-C4-F3 misses a producer's exact style map. The deviation text honestly states the achieved counts, but the public exact claim is false for that input. |
| 11, complete label-variant contract and disclosure | **Carried.** Exact wire shape, withheld multiplicity, Unicode-fold scope and the broader disclosure delta are present and tested. |

For the disclosure floor, I independently profiled and generated a neutral
63-row, two-column source. The visible label carried count 53; its two
visible variants carried counts 30 and 20; the held-back variant multiset
was `{3: 1}`; a ten-row whole label was suppressed; and numeric styles were
60 published plain plus a held-back remainder of 3. I searched the complete
profile JSON, profiler summary, twin CSV and generation report. The exact
three held-back source spellings—variant, whole label and numeric form—were
absent from all four artifacts. This covers label variants, withheld-variant
multiplicities, whole-level suppression and numeric styles rather than only
the twin/report pair.

## Silent-wrongness judgment

I found no exercised published miss that was absent from the deviation
ledger: the calendar, text-alphabet and style misses are all named with
published and achieved values, and recounting—not writer intention—finds
them. That is materially better than a silent miss, but it does not turn an
EXACT-OBSERVABLE fact into an approximation. The most important statistical
failures here are exact facts knowingly lost on producer profiles while the
plan and contract tell an independent implementer to preserve them.

Type routing received separate checks: numeric-looking declared identifiers,
point-free versus decimal numeric forms, datetime precision/clock routes,
empty columns and ordinary free text. The taxonomy and dispatch tests pass;
the style failure changes downstream inferred type despite taking the
correct numeric route, and is therefore recorded under fidelity rather than
misrouting.

## Coverage and attack classes examined

Surfaces and properties checked:

- all three governing documents, every EXACT-OBSERVABLE and EXACT-CONTROL
  field, authorized corners, feasibility outcomes and acceptance criteria;
- current code and tests for the generalized packing grid, pruning,
  termination, fallback, text shape, style capacity and endpoint read-back;
- installed-entry-point closure from process start, source removal, allowed
  reads, import closure and transaction output;
- all 13 oracle cases across both fixtures, case-set union, cell/CSV byte
  equality, RNG-word binding, word budgets, proof coverage, proof mutants,
  case-specific mutants, no-numpy rule, fixture sizes, hashes and rebuilds;
- all eleven owner decisions, including their public costs and the boundary
  between invention and reproduction;
- disclosure-floor behavior in the full profile, profiler summary, twin and
  report, including variant spellings, anonymous held-back multiplicities,
  suppressed levels and numeric forms;
- determinism over repeated seeds, unordered-iteration risk on
  randomness-consuming paths, and exact byte disagreement;
- profile/generator separation, real-table access, network, subprocess,
  dynamic-code and native-call attack classes;
- validator honesty: positive tests for misses, strict xfail handling,
  branch-removal vacuity, proof-layer mutations and wording-guard allowlists;
- decontamination, provenance, supply-chain locks, lint, typing, public
  capability claims, zero-code output instructions and failure messages;
- round-1 and round-2 repair surfaces. Their focused files pass, but
  P2-C1-F1 and P2-C2-F2 are substantively reopened by P2-C4-F2 and F3;
  P2-C1-F6's endpoint principle is reopened by P2-C4-F1. I found no reopening
  of the invention-domain termination, publication guard, approximation
  bounds, leading-zero ceiling, relationship claims, specification spelling,
  numeric distinctness ledger, fold-collision availability, legacy oracle
  identifier bands, or invention-walk-bound repairs.

Review gaps: I did not run another operating system or rebuild the wheel in
the CI network-none container. I relied on the repository's platform tests
for those two surfaces. I did execute the installed local entry point and
all repository commands requested for this round.

## Final verdict

**REJECT, blocked on P2-C4-F1, P2-C4-F2, P2-C4-F3 and P2-C4-F4.** The final
round must independently close those four HIGH items. P2-C4-C1 through
P2-C4-C4 may carry only as the bounded, executable conditions stated above;
none authorizes lowering an exact obligation or blessing an oracle
disagreement.

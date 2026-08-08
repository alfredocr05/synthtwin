# Phase 1 combined plan-and-code review — round 5

**Reviewed baseline:** the staged Phase 1 tree above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`, including the round-4
response, the amended Phase 1 plan, all product and test code, the offline
scanner, dependency inputs and all three locks, workflow, and public
documentation.

**New item count:** 3 blockers. Previously admitted-open items are assessed
below and are not counted again.

This final cycle round does not support closure. The bounded dependency-root
repair holds, and meaningful pieces of the scanner, numeric-population, and
path-identity repairs hold. The latter three do not implement their complete
rules. Two scanner binding forms already established in round 3 still report
clean; numeric sign, integer, and sentinel evidence is still split between
populations; and output identity still misses one supported filesystem
equivalence and one metadata-error path.

## Review items

### [BLOCKER] P1-R5-F1 — exclusivity is sound only over the incomplete origin set it receives

**Carries forward:** P1-R4-F1 and the unresolved P1-R3-F1/F2 binding
families.

**Location:** `tools/offline_scan/scan_imports.py:1255-1327, 1424-1510,
1545-1569, 1979-1992, 2373-2404, 2503-2518`;
`tests/test_offline_scan.py:1532-1585`;
`docs/plans/phase-1-profiler.md:124-147`; `SECURITY.md:105-134`.

The new distinction is useful and correctly applied when the origin set is
accurate. `_resolve_exclusively` refuses any set containing a definition,
instance, result, string, literal, local-path, or unknown origin. Its three
trust-sensitive callers then impose the necessary identity: `typing.cast`
must be the only resolved name; the validator and `pathlib.Path` wrapper must
be canonical; and every candidate for a fenced call is inspected. Both
round-4 examples are now red, the shipped source is clean, and the Phase 0
dead-branch module mutation remains red.

The defect is one layer earlier: `_lookup` can return the wrong set or a set
that never received a binding.

**Concrete failure scenario 1 — class namespace:** put a module-global
function called `Path` in the file; it returns a file URL. Inside a class,
import the genuine `pathlib.Path`, and inside a method pass `Path(validated)`
to `pandas.read_csv` after calling the genuine validator. A scanner-only
fixture reported zero violations. The scanner keeps the class namespace on
its scope stack while visiting the method and therefore trusts the class's
`pathlib.Path`. Python method bodies do not close over the surrounding class
namespace: the unqualified name resolves to the module-global function. The
validated path is replaced with the URL before the reader sees it. This is
project-owned source behavior, not the A3 residual for code supplied by a
caller.

**Concrete failure scenario 2 — pattern capture:** read a frame through the
fenced reader, bind `path` to a genuine `pathlib.Path`, then use `case path:`
to capture the frame and call `path.to_csv(raw_path)`. The scanner-only case
again reported zero violations. `MatchAs.name` is a string field rather than
an `ast.Name`, and the checker has no conservative match-binding visitor, so
it retains the earlier Path origin. Python replaces `path` with the frame;
the writer can replace the input table. This is the same writer route already
executed and recorded in round 3; this round did not execute it.

The specific plan and security claims remain too strong. P1-D2.1 says the
scanner holds the line, and `SECURITY.md` says another reader call site cannot
appear and returned pandas objects are never called through. The general A3
best-effort language elsewhere does not make those specific statements true.

**Required closure:** either make method-body lookup skip class scopes, bind
every pattern capture conservatively, and retain both cases as permanent red
tests; or record the owner's A3 choice that human source review carries these
forms, make the scanner explicitly defense in depth, and remove the absolute
plan/security claims. The current state does neither.

### [BLOCKER] P1-R5-F2 — the combined numeric population is still not carried through sentinel, sign, and integer decisions

**Carries forward:** the incomplete P1-R4-F2 repair and the admitted contract
for numeric intent with no representable value.

**Location:** `src/synthtwin/parsing.py:311-442`;
`src/synthtwin/taxonomy.py:368-428, 518-532, 565-625, 704-708,
897-960`; `docs/plans/phase-1-profiler.md:232-250, 543-569`.

Three narrow repairs are real. Sentinel frequency now divides by every
present value; populations and thresholds are recomputed after an actual
removal; and a leading minus sign on an out-of-range spelling prevents the
count role. The round-4 cases now produce continuous with minimum `-999`, no
negative summary count, and continuous rather than count, respectively.

The complete rule still fails in neighboring states.

**Concrete failure scenario 1 — sentinel gate:** profile `1` through `196`,
one `-999`, and `1e999`, `2e999`, `3e999`. All 200 cells are numeric-looking.
The candidate is exactly 0.5% of present values and is an outlier, so the
documented rule says it is missing. The code starts sentinel decisions only
when the *representable* numbers meet the 99% threshold: 197 is below the 198
needed. It emits no candidate verdict, keeps `-999`, and publishes it as the
minimum. The denominator was repaired, but the combined population still
does not gate normalization.

**Concrete failure scenario 2 — decidable sign:** profile `1` through `99`
plus `(1e999)`. Parentheses are the supported accounting form for a negative
number, and the parser classifies the cell as numeric but out of range. The
profile nevertheless says `role: count`, `integer_valued: true`,
`n_out_of_range: 1`, and `n_negative: 0`, because the routing checks only
whether the text begins with `-`. The leading-minus neighbor is called
continuous now, but it still publishes `n_negative: 0`; the sign affected the
role and then disappeared from the structured count.

**Concrete failure scenario 3 — decidable integer status:** `1` through `99`
plus `1e-999` is called a whole-number count. The last spelling is a positive
fraction too small for binary64, so its integer status was not established.
`all_whole` considers only the representable values and silently treats the
missing evidence as true.

The admitted contract gap is still visible: a column of distinct
out-of-range numbers becomes free text; repeated spellings can become a
constant or category and publish the spellings as labels. The counts say the
cells were intended as numbers while the role dispatch says otherwise. The
owner must choose a refusal, a limited numeric role, or an explicit fidelity
loss; more routing patches cannot make that contract decision.

None of the round-4 sentinel-denominator, post-removal, or out-of-range-sign
examples was added as a profiler/CLI regression. Reverting those repairs
leaves the relevant current tests green, despite the acceptance criterion
requiring every sentinel branch to have a red/green fixture.

**Required closure:** represent each cell's numeric class plus any decidable
sign/integer evidence once; use that record for normalization, routing,
structured counts, and remarks; implement the owner-selected no-representable
role; and add the scenarios above and the original round-4 cases as
end-to-end regressions.

### [BLOCKER] P1-R5-F3 — output identity still does not cover every admitted alias or metadata failure

**Carries forward:** P1-R4-F3. It remains coupled to the admitted
P1-R2-F11 transaction defect.

**Location:** `src/synthtwin/profile.py:188-253, 307-351`;
`src/synthtwin/parsing.py:162-173`; `src/synthtwin/cli.py:290-309`;
`tests/test_profile_document.py:245-279`;
`tests/test_cli_profile.py:172-181`.

Exact resolved aliases, existing hard links, and absent paths that differ
only in case are now refused. Exceptions from `resolve()` and `samefile()`
also return the conservative answer.

**Concrete failure scenario 1 — normalization-equivalent absent names:** on
a supported normalization-insensitive macOS volume, make the two dangling
output links point to spellings that differ only as U+00E9 versus U+0065
U+0301. `resolve()` returns distinct strings, and `parsing.folded` performs
only trim plus case folding, not Unicode normalization. A read-only helper
check returned `False`. The first write creates the shared destination and
the second write opens the same file, replacing the JSON with summary text;
there is no identity recheck after the first target exists. This is the same
machine-profile loss as round 4's case-only example.

**Concrete failure scenario 2 — metadata query:** make either `Path.exists()`
query raise `OSError`. Those calls remain outside both exception handlers.
The helper propagates the raw exception, and `cli.main` does not catch it, so
the command produces a traceback instead of a fail-closed plain-language
refusal. On a runtime/filesystem combination that suppresses the query error
as `False`, the helper instead answers that the paths differ.

There is no direct identity test in `test_profile_document.py`, and the CLI
suite covers only a link from one output to the input. The exact, dangling,
hard-link, case/normalization, metadata-failure, and after-first-write states
required by round 4 are not a permanent regression set.

**Required closure:** complete identity and transaction work together. Use
filesystem-appropriate case/normalization comparison or recheck identity
after the first destination exists; catch every metadata query; write and
flush same-directory temporary regular files before either commit; define
rollback for existing targets; and add every state above as a regression.

## Disposition of the round-4 response

| Repair | Final-cycle disposition |
| --- | --- |
| P1-R4-F1 | **Incomplete.** The new exclusive resolver closes its two new tests and its callers use it correctly, but wrong class lookup and missing pattern bindings still supply trusted origins and scan clean (P1-R5-F1). |
| P1-R4-F2 | **Partly holds.** Present-value denominator, post-removal recomputation, and the literal leading-minus role change work. Sentinel gating, accounting-negative/integer evidence, structured negative counts, the no-representable role, and regressions remain open (P1-R5-F2). |
| P1-R4-F3 | **Partly holds.** Exact and case-only aliases are conservative; normalization aliases and `exists()` errors remain outside the rule, with no regression battery (P1-R5-F3). |
| P1-R4-F4 | **Admitted open, Major.** Format controls and path-bearing refusal sinks still bypass the one display boundary. |
| P1-R4-F5 | **Holds for its bounded claim.** `requirements-install.in` is read and its direct roots must equal `AUTHORIZED = {"pandas"}`; package metadata has the same sole runtime root. Adding numpy or another root makes the test fail. This does not close the separate project-wheel/bundle item P1-R3-F6. |

## What is genuinely solid now

- The shipped profiler's direct reader call revalidates the raw input
  immediately before `pandas.read_csv`, and the current nine source modules
  pass the enumerated scanner. The same-scope import-plus-definition cases
  from round 4 are now rejected.
- The current dependency surface is coherent: pandas is the sole declared and
  institutional-input root; numpy is transitive; all three input/lock pairs
  satisfy the structural validator; the install-root equality guard is real.
- The profile/generator boundary is structurally clean in Phase 1. Only the
  reader opens the table, no generator exists yet, and the profile contains no
  source path, clock, RNG, or machine identity. Serialization is canonical
  and the tested outputs are repeatable.
- Ordinary headed UTF-8/Latin-1 CSVs, ragged rows, exact duplicate headers,
  basic taxonomy paths, suppression on the exercised categorical/text cases,
  and actionable common refusals have useful end-to-end coverage.
- The narrow round-4 numeric and case-alias behaviors listed above work. That
  is meaningful progress even though the rules around them remain incomplete.
- Every prescribed check passed. That establishes consistency for the cases
  those checks exercise; it does not answer counterexamples outside them or
  establish that the numeric reference generator is correct.

## Remaining admitted work, in shortest-path order

The rows below retain their established severities and give the concrete
consequence that still makes each item real.

| Order | Severity and item | Concrete remaining consequence | Closure kind |
| --- | --- | --- | --- |
| 1 | [MAJOR] P1-R2-F11 | If an existing JSON is replaced and the summary write then fails, the prior file is not restored; partial first or second files can also remain. Pair this with P1-R5-F3. | Code plus failure/rollback tests. |
| 2 | [BLOCKER] P1-R2-F5 | The reference generator rounds the subnormal tie for `[0, 0, 2m, 3m]` down instead of half-even, can return a negative spread at the zero boundary, truncates terminating decimals while labeling them exact, and measures tolerance without true representable-step distance. | Correct and independently re-review the oracle before changing implementation or vectors. |
| 3 | [BLOCKER] P1-R2-F4 | `[-max, 1, max]` still publishes a mean five representable steps from exact rounding; replacing `1` with `1e-16` erases it; the subnormal median misses half-even. | Numeric implementation after P1-R2-F5. |
| 4 | [BLOCKER] P1-R1-F4 and R1-X3 | Equal dimensions still admit a same-shaped edit between passes and a parser disagreement that moves a value between columns, yielding plausible profiles of different data. | Reader design and value-level end-to-end comparisons. |
| 5 | [BLOCKER] P1-R1-F5 | A headerless `P001,34`-style file consumes and publishes the first record as schema while profiling one fewer row. | Owner-selected ambiguous-header contract, then code/tests. |
| 6 | [BLOCKER] P1-R1-F7 | The fixed sentinel rule still removes a legitimate extreme, retains a rarer genuine missing code, treats a legitimate text code as missing, and lets multiple candidates mask one another. | Owner-selected ambiguity/override policy, then code/tests. |
| 7 | [BLOCKER] P1-R1-F8 | A 98%-numeric column can become an identifier; padded codes become quantities; a category just over the ceiling becomes free text; the sole override corrects only one direction. | Taxonomy/override redesign and realistic neighbor tests. |
| 8 | [BLOCKER] P1-R1-F10 remainder | Eleven identical values forced as an identifier still take the constant branch and publish the value; raw normalized spellings can still appear in `missing_by_source` for otherwise suppressed roles. | Output-wide noninterference and override precedence. |
| 9 | [BLOCKER] P1-R1-F9 | Different datetime shapes and different suppressed-level distributions can still serialize to the same profile, so a profile-only generator cannot preserve both. | Owner-selected v1 fidelity contract, collision tests, then implementation. |
| 10 | [BLOCKER] P1-R3-F6 | Replacing the project wheel leaves every dependency hash valid; the acquisition instructions are host-specific and do not transfer a governed target-complete bundle. | Owner chooses a governed release artifact now or marks the institutional path planned rather than built. |
| 11 | [MAJOR] P1-R4-F4 | U+061C and other format controls can still reach a human-facing output, and a path containing a terminal control can reach several refusal messages raw. | Complete one escaping boundary and byte-level sink tests. |
| 12 | [MAJOR] P1-R2-F13 | `Age,age` is accepted with no promised warning; a later case-insensitive consumer can collapse or select the wrong column. | Define normalization and add structured warning/CLI tests. |
| 13 | [MAJOR] P1-R1-F13 format-spec half | A dynamic f-string format specification is not recursively checked and can invoke caller-controlled formatting behavior while the scanner accepts the resulting text. | Scanner code, capability text, red mutation. |
| 14 | [MAJOR] P1-R1-F15 | The structural pass still materializes all rows while the plan says it holds one row; the true peak-memory model remains larger than documented. The CLI-wide `MemoryError` catch and sampling advice have improved, but do not make the streaming claim true. | Code or honest plan amendment plus large-table failure tests. |
| 15 | [MAJOR] P1-R1-F16 | Catalog reachability is still source-text membership, so a dead builder can pass; builder-only tests can miss the real library/argparse wording a user sees. | Real CLI trigger per catalog entry. |
| 16 | [MAJOR] P1-R1-F17 | `NA`, `na`, padded variants, empty cells, and whitespace-only cells are merged into canonical keys although the plan promises source spellings. | Owner chooses exact spelling versus canonical classes under the privacy rule. |
| 17 | [MINOR] P1-R1-F18 | A valid Latin-1 header beginning with `0xFF` or `0xFE` can be mistaken for a wide-encoding marker and refused. | Byte-signature repair and controls. |

## Decisions for the project owner

These are not usefully resolved by another narrow implementation patch:

1. Whether D6 Amendment A3 means mandatory human source review plus a
   best-effort scanner, explicitly accepting the known clean-scan binding
   forms, or whether product source must obey a fail-closed dialect/stronger
   checker.
2. What role or refusal represents numeric intent when no value is
   representable, and whether the accuracy/platform contract remains literal
   or is narrowed before the oracle is repaired.
3. Whether an ambiguous first row and an ambiguous sentinel require user
   confirmation, an explicit override, or unconditional refusal.
4. Which distributional facts profile v1 must carry for Phase 2, versus which
   collisions become explicit fidelity limits.
5. Whether numpy's direct-dependency authorization is formally withdrawn for
   Phase 1.
6. Whether Phase 1 must deliver the governed project-wheel digest and
   target-complete offline bundle, or must describe that procedure as planned
   until a release exists.
7. Whether missing-source reporting preserves exact spelling or reports named
   canonical classes, and how that choice interacts with suppression.

## What a sixth round would need to see

A sixth round is useful only after one response maps every blocking item to a
recorded plan decision, implementation, and permanent regression. At minimum:

- the owner decisions above recorded before dependent code is changed;
- the class-lookup and pattern-capture scanner cases red, or the scanner and
  security claims narrowed exactly to the accepted source-review model;
- normalization aliases, metadata failures, partial writes, existing-output
  rollback, and after-first-write identity covered together;
- the reference generator corrected and independently reviewed, with new
  boundary vectors frozen before the numeric implementation is judged;
- the combined numeric record and chosen no-representable role exercised
  through profile and CLI tests;
- both readers compared on values, an explicit header-ambiguity outcome, and
  full-output suppression/type-routing collision tests; and
- either a governed, target-specific install bundle exercised across its
  transfer boundary or every built-institutional-path claim withdrawn.

Submitting only another subset while the remaining blockers stay admitted
would make a sixth round repeat this inventory rather than decide closure.

## Verification and attack coverage

The staged baseline before this report was written passed:

```text
.venv/bin/python -m pytest -q
  598 passed, 4 skipped

.venv/bin/python -m pytest tests/test_offline_scan.py -q
  80 passed

.venv/bin/python tools/offline_scan/scan_imports.py src
  9 files, 0 violations

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  dev input/lock passed

explicit install and minimum input/lock checks
  both passed

.venv/bin/python -m pytest tests/test_dependencies.py tests/test_validate_lock.py -q
  43 passed

.venv/bin/python -m ruff check .
  passed

.venv/bin/python -m mypy src
  9 source files passed
```

Scanner-only static cases were evaluated from source strings and never
executed. Both the class-namespace reader case and the pattern-capture writer
case returned an empty violation list. No URL was opened and no file-writing
behavior was run. Pure profiler calls checked the original and neighboring
sentinel/sign/integer populations. Read-only identity calls checked the
case/normalization comparison and an injected `exists()` exception.

The examined properties were trust versus suspicion in every
`_resolve_exclusively` caller; Python module/function/class and match binding;
fenced reader provenance; restricted-object origin preservation; direct
dependency-root equality; representable, out-of-range, contradictory,
sentinel-removed, and no-representable populations; sign/integer evidence;
output identity before and between writes; metadata failure; transaction and
rollback; numeric-oracle independence and stated bounds; reader agreement;
header ambiguity; type routing; output-wide suppression; profile sufficiency;
canonical determinism; profile/generator separation; display escaping;
failure reachability; and plan/security/code consistency.

The review surveyed all files under `src/synthtwin/` and the full test set,
then re-read the repair paths and their focused tests in detail. It also
covered `tools/offline_scan/scan_imports.py`, the reference generator and
numeric fixture, the supply-chain validator, `pyproject.toml`, all dependency
inputs and locks, workflow consumers, the Phase 1 plan, all four prior Phase 1
review/response pairs, README, SECURITY, and CHANGELOG.

This host is macOS. Unicode normalization alias behavior was checked without
creating or writing through aliases; Windows reparse behavior was not run
outside the suite's platform simulations/skips. No second air-gapped target
or release artifact exists, so P1-R3-F6 could not be exercised end to end.

## Cosmetic observations

The stale “two runtime dependencies/pins” sentences in README, CHANGELOG, and
`requirements-min.in`, plus SECURITY's instruction to confirm an empty
dependency list, are cosmetic in this review: authoritative metadata, the
actual inputs, and the new root guard agree on pandas. Correct them after the
owner confirms the numpy decision, but they do not change this result.

## Verdict

**Verdict: reject.** Blocking round-5 items are P1-R5-F1, P1-R5-F2, and
P1-R5-F3. They join P1-R3-F6, P1-R2-F4, P1-R2-F5, P1-R1-F4,
P1-R1-F5, P1-R1-F7, P1-R1-F8, P1-R1-F9, and the remainder of
P1-R1-F10; R1-X3 remains a blocking member of P1-R1-F4.

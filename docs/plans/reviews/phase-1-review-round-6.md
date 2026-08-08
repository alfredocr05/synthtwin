# Phase 1 combined plan-and-code review — round 6

**Reviewed baseline:** the staged Phase 1 tree above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`, including the round-5
response, revision 2 of the Phase 1 plan, the six redesigned areas, all
product and test code, the offline scanner, dependency inputs and locks,
workflow, and public documentation.

**New item count:** 8 blockers and 4 majors. The explicitly withheld work
and owner decisions are recorded separately and are not counted again.

**Ruling on the question posed for this round: (c).** The exact-integer
reformulation is mathematically sound, the retired conditioning limit was an
artifact of the old two-pass reduction, and I found no statistic that violates
the correctly-rounded-or-adjacent contract. The current reference numbers are
also right. The worse finding is in the apparatus that certifies them: its
proof routines accept false results, some published values bypass proof, and
the grading tests still enforce revision-1 tolerances that accept non-adjacent
answers.

This is nevertheless real movement toward ratification, not merely a move of
every problem. Exact moments, value-level reader agreement, the bounded
numeric-population repairs, and several former scanner binding cases now hold.
The oracle, first-row decision, transactional write, remaining origin
tracking, and taxonomy contract do not yet support closure.

## Review items

### [BLOCKER] P1-R6-F1 — the oracle's proof layer accepts false overflow and signed-zero results, and does not prove the ladder

**Location:** `tools/reference/make_numeric_reference_vectors.py:170-200,
323-354, 565-580, 750-801`; `docs/plans/phase-1-profiler.md:619-626`.

The exact constructors are sound, but the independent checks around them are
not. These two calls return normally:

```python
prove_nearest_float(F(1 << 1024), sys.float_info.max)
prove_correctly_rounded_sqrt(F(1 << 2048), sys.float_info.max)
```

Both exact results are beyond the round-to-nearest overflow boundary and must
be refused. At the maximum finite float, each proof routine sees an infinite
upper neighbour and makes the upper comparison unconditionally pass instead
of comparing with the finite/overflow midpoint.

Zero has a second blind spot. `prove_nearest_float(F(-1, 1 << 2000), +0.0)`
accepts positive zero even though the correctly rounded result is negative
zero. `prove_correctly_rounded_sqrt(F(0), -0.0)` also accepts a negative-zero
square root. Numeric comparison erases the sign of zero, and the explicit sign
guards use `< 0`/`> 0`, which do not distinguish the two encodings.

Finally, every ladder rung at lines 565-580 is sent directly through
`round_rational_to_float`; none is passed to `prove_nearest_float`. The
generator's statement that every published float is proved against both
neighbours is therefore false even apart from the bad proofs.

This is a certification defect, not evidence that a current vector is wrong:
an independent rational audit found all 222 authoritative mean/std/skew and
exact-ladder results correct, as well as all 90 diagnostic binary-p ladder
results. A future constructor regression at overflow, zero sign, or in a
ladder rung could nevertheless be certified and frozen.

**Required closure:** prove the finite/overflow midpoint explicitly; compare
zero signs by bits where the mathematical operation fixes a sign; run a
construction-independent neighbour check on each emitted float, including
all ladder rungs; add negative tests that make each proof reject the exact
counterexamples above; and regenerate and byte-compare the fixture.

### [BLOCKER] P1-R6-F2 — the tests still accept revision-1 errors rather than correctly-rounded-or-adjacent results

**Location:** `tests/test_numeric_reference.py:55-140`;
`tools/reference/make_numeric_reference_vectors.py:779-801`;
`docs/plans/phase-1-profiler.md:582-607`.

`_ulp_distance` is not a representable-float distance. It divides by
`abs(expected) * eps`, and at zero by `eps**2`. Standard deviation is allowed
two of those rough units, and skew still uses the retired absolute tolerance.
Directly substituting wrong results into the real assertions gives:

| case | correctly rounded reference | wrong result accepted by the test | why this violates revision 2 |
| --- | ---: | ---: | --- |
| skew of `{1e16, 1, -1e16}` | `-1.224744871391589e-16` | `0.0` | zero is not either adjacent float; it is about 4.97 quadrillion representable steps away |
| sample std of `[1, 2]` | `0.7071067811865476` | `0.7071067811865478` | the mutant is two floats above the correct result |
| sample std of `[5, 5, 5]` | `0.0` | `1e-100` | the nearest nonzero float to zero is about `4.94e-324`, not `1e-100` |

All three pass the checked-in test expressions. Removing the earlier named
subnormal floor did not remove the underlying zero-boundary hole.

The generated fixture also still describes the old sorted/`fsum` reduction,
old one/two-unit and absolute skew tolerances, and the supposedly retired
`known_conditioning_limit`. The plan itself retains the old contract at lines
582-588 immediately before tightening it at lines 604-605. Thus a green suite
does not grade the redesign's stated contract.

**Required closure:** compare ordered binary64 encodings, including signed
zeros and the subnormal/normal boundary, and accept only the reference result
or a genuine immediate neighbour for mean, standard deviation, and skew.
Retain the separately stated bracket-scale ladder rule only if that remains
the intended contract. Regenerate metadata that describes the exact-integer
algorithm and remove the retired limit and tolerances. Keep each mutant above
as a test that must fail.

### [MAJOR] P1-R6-F3 — an exact out-of-range spread can be published as an ordinary finite maximum

**Location:** `src/synthtwin/taxonomy.py:703-739`;
`docs/plans/phase-1-profiler.md:609-617`.

Profile these three distinct values:

```text
-1.5568479229996504e+308
 1.5568479229996504e+308
 1.5568479229996502e+308
```

The column is continuous and publishes
`std: 1.7976931348623157e+308`, with no `std_unrepresentable` flag. In units
`U = 2**970`, let `A = 15600926743107924` and `d = 2`. Its exact sample
variance is

```text
(4*A*A - 2*A*d + d*d) / 3 * U**2
```

Exact integer comparison gives
`MAX**2 < variance < (MAX + U)**2`. The exact standard deviation is larger
than the largest finite binary64 number but below the overflow midpoint, so
rounding it to `MAX` is correct. That is why the rounding audit did not find
an arithmetic error. The semantic contract is different: revision 2 says
that any exact spread larger than the format can hold is `null` plus
`std_unrepresentable: true`. The code sets the flag only when rounding itself
raises for overflow. A consumer cannot distinguish a saturated spread from a
genuinely representable maximum.

**Required closure:** compare the exact squared spread with `MAX**2` before
rounding, publish null plus the flag on the exact boundary promised by the
plan, and retain this three-value continuous-column case as a profile and CLI
regression.

### [BLOCKER] P1-R6-F4 — origin sets still omit bindings at the point where trust is granted

**Location:** `tools/offline_scan/scan_imports.py:1213-1344, 1555-1586,
2368-2442`; `docs/plans/phase-1-profiler.md:124-147`; `SECURITY.md:105-134`.

The new accumulated-origin/exclusive-trust distinction is correct only after
all possible origins have entered the set. This runnable module reports zero
violations:

```python
import pandas
from pathlib import Path
from synthtwin.paths import validate_local_path

def substitute_path(raw):
    return "https://example.invalid/table.csv"

def fetch(raw_path):
    validated = validate_local_path(raw_path, purpose="input")
    return pandas.read_csv(Path(validated))

Path = substitute_path
```

At runtime the final assignment runs during import, before an external caller
can call `fetch`; a recorder substituted for `pandas.read_csv` received
`https://example.invalid/table.csv`. The scanner pre-collects imports,
functions, and classes, but not assignments. It visits the deferred function
body while `Path` still has only the trusted import origin, grants local-path
provenance, and never revisits that call after seeing the assignment.

A second clean mutation demonstrates the inverse temporal error in a class
body: a module-global fake `Path` is called in a class statement before a
later `from pathlib import Path` inside the class. Pre-collection trusts the
later import even though Python executes the earlier class statement first
and falls back to the fake global. This can send a URL into the fenced reader
without a scanner finding.

The round-5 method-body class-scope and `match`-capture examples are now red,
and `_resolve_exclusively` behaves correctly when given a complete set. The
remaining defect is precisely the completeness and timing of that set.

**Required closure:** model all store forms conservatively before analysing
deferred bodies, preserve execution order for statements executed while a
class is being built, and add both examples above as permanent red mutations;
or take the owner's A3 path and narrow the scanner and security claims to a
documented best-effort/source-review boundary. The present absolute fence
claim and a clean scan cannot coexist.

### [BLOCKER] P1-R6-F5 — deterministic staging names can destroy the input and the rollback messages do not describe the disk

**Location:** `src/synthtwin/profile.py:250-277, 332-507`;
`src/synthtwin/errors.py:332-350`; `src/synthtwin/cli.py:275-329`.

The same-folder staging idea is reasonable, but the fixed `.synthtwin-part`
and `.synthtwin-kept` names are neither created exclusively nor included in
the identity and ownership checks. Executed `/tmp` probes left these states:

| failure or pre-existing state | what the user is left holding |
| --- | --- |
| `table-profile.json.synthtwin-part` is a symlink to `table.csv` | staging follows the link and overwrites the source table with profile text; commit moves the symlink to the final profile name, and the operation can report success |
| no old profile exists and the second rename fails | the new JSON remains at the final profile name, while the message says “Nothing was written: both files are as they were before” |
| unrelated regular `.synthtwin-part` or `.synthtwin-kept` neighbours already exist | they are overwritten and then deleted without refusal or disclosure |
| the first staging write completed, the second failed, and cleanup of the first part failed | the named residue contains a real-data-derived description, while the message says working files “hold no description of your table” |

On successful commit, failure to delete an old-profile `.synthtwin-kept` file
is also ignored. Metadata is not fully fail-closed: `exists()` at lines 272
and 396 remains outside an exception handler and can escape the CLI as a raw
traceback. On this normalization-insensitive host, two dangling output aliases
using composed and decomposed spellings of the same name also passed the
identity check; the later collision left summary text at the shared target
while claiming both files were restored.

The strongest failure is not merely two-file non-atomicity: a working-name
symlink can destroy the table that the command exists to protect, outside the
two output names the CLI says it writes.

**Required closure:** create unique same-directory regular staging and backup
files with exclusive ownership; refuse or preserve every pre-existing
neighbour; validate every stage/backup identity against the input and both
final targets; remove a newly installed first target when there was no backup;
verify and report cleanup; catch every metadata error; and add a failure test
for each row above, including exact assertions on every surviving byte and on
the message's file list.

### [BLOCKER] P1-R6-F6 — automatic first-row handling still treats no evidence as evidence for names

**Location:** `src/synthtwin/reading.py:473-511, 698-720, 744-771`;
`docs/plans/phase-1-profiler.md:198-215`.

For this headerless table:

```csv
alpha note,red apple
beta observation,green pear
gamma record,blue berry
```

automatic reading returns `header_source: file`, column names
`["alpha note", "red apple"]`, and two rows. The first record has been
silently consumed as schema. Every column receives `_SAYS_NOTHING` from the
shape rule; `_first_row_is_ambiguous` returns false as soon as it sees that
state, so absence of evidence selects names. The public `read_table` docstring
explicitly admits this free-text-over-free-text loss, while revision 2 says
inconclusive evidence stops and asks.

The consequence is both analytic and disclosure-related: one real record is
missing from every count, and its raw values are published as column names
outside role suppression. `--first-row data` correctly keeps all three rows
and generates neutral names, but the default never asks the user to choose.

Value-level two-reader agreement is sound: the readers compare every header
and cell, same-shaped rewrites are refused, and the explicit data mode works.
Those bounded repairs need not be revisited after this remaining decision rule
is fixed.

**Required closure:** make `_SAYS_NOTHING` produce the documented inconclusive
outcome unless positive names evidence exists, exercise all-numeric,
shape-contradicting, positive-name, mixed, and no-evidence cases through the
CLI, and assert row counts and absence of first-record text from schema.

### [BLOCKER] P1-R6-F7 — revision 2 and the implemented taxonomy describe different products

**Location:** `src/synthtwin/taxonomy.py:158-200, 1441-1765`;
`docs/plans/phase-1-profiler.md:220-288`.

Revision 2 freezes numeric routing at 99% and categorical routing at
`distinct <= min(1000, 10% of rows)`. The implementation instead adds an
undocumented 50% numeric-majority path, defines categories by average
repetition of two, uses 1000 only as a publication cap, caps mostly numeric
categories at 12, and inserts a fixed-width-code rule before dates and
numbers. These are design choices, not implementation details, and the
serialized settings do not amend the governing plan.

Two concrete dispatch changes show why this is not a wording item:

- Sixty distinct strings `"0"` through `"59"` plus forty distinct two-word
  notes are published as `role: count`, with `min: 0`, `max: 59`, and
  `mean: 29.5`; forty cells are omitted from the distribution. Revision 2's
  99% numeric rule declines, its categorical and identifier rules decline,
  and free text publishes no values.
- Sixty-one `"common"` values plus thirty-nine unique labels in 100 rows are
  categorical and publish `common: 61`. Revision 2 has 40 distinct values,
  above its ceiling of 10, and routes the column to nonpublishing free text.

The divergence changes Phase 2 dispatch and what real-data-derived facts
cross the boundary. Either policy could be argued, but only the owner can
choose it; a reviewer cannot ratify both.

**Required closure:** record one ordered taxonomy and one set of thresholds in
revision 2, make code and serialized settings implement exactly that policy,
and add neighbour tests at 49/50/98/99% numeric, repetition and 10%-of-row
category boundaries, the 12/1000 caps, and fixed-width codes.

### [BLOCKER] P1-R6-F8 — moving `identifier` later still turns unsupported measurements into record IDs

**Location:** `src/synthtwin/taxonomy.py:1827-1919`;
`docs/plans/phase-1-profiler.md:272-288`.

Use 30 rows whose values run from `1mg` through `30mg` without repetition.
The number and date parsers decline these tokens, and they do not repeat
enough to form a category. Each is one code-alphabet token, so the column is
classified confidently as `identifier`. No value or distribution is
published, and Phase 2 is instructed to generate neutral placeholder
identifiers rather than measurements.

The reordered implementation and its positive code rule fix the former
98%-numeric, date, sentence, T/F, and padded-code neighbours. They do not make
uniqueness positive evidence that the leftovers are identifiers. Unit-bearing
measurements, accession-like codes, and other unique alphanumeric domains
remain irreducibly ambiguous, and the only override (`--identifier`) works in
the direction already chosen automatically.

**Required closure:** provide a reverse measurement/text decision or stop and
ask on the ambiguous unique-code shape; at minimum, do not claim code-alphabet
uniqueness alone establishes an identifier. Add unit-bearing measurements and
true record IDs with the same lexical shape as paired end-to-end cases.

### [BLOCKER] P1-R6-F9 — the promised sentinel override is absent from the CLI and fails on equivalent numeric spellings

**Location:** `src/synthtwin/cli.py:123-169`;
`src/synthtwin/taxonomy.py:203-208, 881-914, 976-1054, 2043-2073`.

The settings and docstrings promise `--keep-value` and `--missing-value`, with
the user's choice authoritative in both directions. The CLI exposes neither.
A region column with forty `north`, forty `south`, and forty legitimate `NA`
values therefore loses all `NA` rows as missing and becomes binary; the person
who knows that `NA` is data has no command-line way to keep it.

Even direct settings do not make the numeric override authoritative. Profile
`1` through `199` plus fifteen `-999.0` values with
`Settings(kept_values=("-999.0",))`. The result records fifteen missing
values and publishes a minimum of `1`. `_sentinel_verdicts` converts the
candidate to the spelling `-999` before checking the user's tuple, misses the
declared spelling, and later removes every value whose parsed float equals
`-999.0`.

The redesigned combined population correctly fixes the former
out-of-range-neighbour sentinel, sign, and integer decisions. It cannot settle
the policy ambiguity on its own; the implemented override must be reachable
and must actually have the last word.

**Required closure:** expose both options, carry them into the serialized
settings, define whether numeric declarations compare source spellings or
exact numeric values, honor that definition consistently before removal, and
test legitimate `NA`, alternative `-999` spellings, conflicting declarations,
and more than one candidate through the real CLI.

### [MAJOR] P1-R6-F10 — the “classify once” record reclassifies cells and builds numeric columns quadratically

**Location:** `src/synthtwin/taxonomy.py:757-868, 2043-2073`;
`src/synthtwin/parsing.py:311-442, 780-844`.

`_analyse` calls `classify_number`, then `numeric_sign` and `numeric_whole`;
both helpers call `classify_number` again and may call `parse_number` again.
Sentinel removal reparses every value and invokes `_analyse` a second time.
The promised one classification is therefore not the implemented invariant,
although the current pure string helpers agree on the ordinary cases tested.

There is an immediate performance consequence: each numeric value uses
`numbers = numbers + [parsed]`, copying the entire accumulated list. On this
host, a direct `_analyse` benchmark took 0.11 seconds for 10,000 distinct
numbers, 0.41 for 20,000, 1.63 for 40,000, and 6.52 for 80,000. Doubling the
column quadrupled the time. This work happens before exact statistics and can
make a moderately large numeric column spend most of its run repeatedly
copying prior values.

**Required closure:** make one immutable per-cell classification carry parsed
value, sign, and whole-number evidence; make all downstream decisions consume
it without reparsing; collect lists in linear time; and add a scale test that
would fail the observed quadratic growth.

### [MAJOR] P1-R6-F11 — human-facing controls still bypass the display boundary

**Carries forward:** P1-R4-F4.

**Location:** `src/synthtwin/parsing.py:99-148`; path-bearing message builders
and `src/synthtwin/cli.py:275-329`.

Running the CLI on a missing path containing the bytes for
`/tmp/r6-\x1b[2J.csv` returned code 1 with the raw ESC `[` `2` `J` sequence
in stderr. A terminal can execute that sequence and clear the display instead
of showing the path. The `visible` helper would escape C0 controls, but the
path reaches this refusal without going through it. The helper's Unicode list
also still omits format controls such as U+061C, U+200B, U+2060, and
U+206A-U+206F.

**Required closure:** apply one complete escaping boundary to every
user-controlled value and path at every human-facing sink, define the Unicode
format-control set systematically, and add byte-level CLI tests for ESC,
newlines, bidi/format controls, and ordinary non-English text.

### [MAJOR] P1-R6-F12 — a dynamic f-string format specification still launders an unknown value into trusted text

**Carries forward:** the format-specification half of P1-R1-F13.

**Location:** `tools/offline_scan/scan_imports.py:1416-1429`;
`docs/plans/phase-1-profiler.md:477-500`.

This scanner mutation reports zero violations:

```python
def reveal(spec):
    return f"{'x':{spec}}".strip()
```

The `JoinedStr` visitor checks only each `FormattedValue.value`; it never
walks `FormattedValue.format_spec`. Evaluating the nested specification can
invoke formatting on the caller-supplied `spec`, yet the outer result is
marked as trusted text and `.strip()` is accepted. This contradicts the E4
claim that every interpolated part is resolved and the explicit rule that an
unknown value never becomes text.

**Required closure:** recursively apply the same origin rule to conversion and
format-specification subtrees, retain the example as a red mutation, or place
this form explicitly inside the owner-selected A3 residual and narrow the E4
claim.

## Conditioning question and oracle coverage

The arithmetic part of the redesign is sound enough to stop re-examining its
central premise once the certification blockers above are fixed:

- every finite binary64 input is decomposed exactly as an integer times a
  shared power of two;
- first, second, and third power sums and the cleared central-moment formulas
  remain exact Python integers until the final rational or square-root
  rounding;
- sample variance and moment skew use the correct factors, including the
  `n - 1` sample denominator;
- rational half-even construction and the integer-square-root construction
  produced the nearest binary64 result across zero, subnormals, the
  max-subnormal/min-normal boundary, binade boundaries, and overflow; and
- reversing or shuffling a sample left its outputs bit-identical.

The independent `/tmp` audits covered 100,000-plus rational/root rounding
cases, 30,000 adjacent-float midpoints, 24,000 square-root midpoint ties,
2,000 exact power-sum comparisons, and more than 8,000 complete finite
samples generated from random bit patterns. A further 5,000 quantile cases,
cancellation extremes, and every current vector output were checked.
`{1e16, 1, -1e16}` produced
`-1.224744871391589e-16`; `[-MAX, 1, MAX]` produced `1/3` rounded once; and no
numeric mismatch or row-order dependence was found.

A fresh generator run was byte-identical to the committed fixture, SHA-256
`477ff6a0932cf03d57ffa4cc507dd303daf3a71b358133f74ee2d11b8ee64ad`.
That establishes that today's fixture values are correct by an independent
method. It does not make a proof routine that accepts false candidates or a
test that accepts distant values safe.

## Disposition of the redesign

| area | disposition this round |
| --- | --- |
| Exact statistics and conditioning-limit retirement | **Holds for numeric rounding.** No counterexample to correctly-rounded-or-adjacent was found. The exact out-of-domain spread flag is a separate semantic miss (P1-R6-F3). |
| Independent reference numbers | **Current values hold.** All authoritative and diagnostic outputs checked independently; certification does not hold (P1-R6-F1/F2). |
| Reader agreement and explicit first-row modes | **Agreement and `--first-row data` hold.** The automatic no-evidence state still consumes a record (P1-R6-F6). |
| Two-file write | **Does not hold.** Staging ownership, source identity, rollback, cleanup, and messages fail together (P1-R6-F5). |
| Taxonomy order and numeric-unrepresentable role | **Partly holds.** The old numeric-neighbour cases, all-unrepresentable withholding, and forced-identifier precedence are repaired. Governing thresholds, residual identifier ambiguity, and sentinel overrides are not (P1-R6-F7-F9). |
| Origin tracking | **Partly holds.** Accumulation/exclusive trust and the round-5 class-method/match cases work for complete origin sets; deferred and class-body timing still supplies incomplete or premature sets (P1-R6-F4). |
| One cell population | **The former semantic neighbours hold.** The literal once-only and linear-work claims do not (P1-R6-F10). |
| Profile/generator boundary and deterministic bytes | **Holds in Phase 1.** The profile carries no source path, clock, RNG, or machine identity; canonical serialization and regenerated fixtures are repeatable. |
| Dependency roots and locks | **Holds for the checked tree.** pandas is the sole direct runtime root, all input/lock pairs validate, and numpy remains transitive. The release-artifact boundary remains separately open. |

## Explicitly known open work

- **P1-R1-F16:** end-to-end failure-catalog CLI triggers are withheld; builder-level coverage is not a substitute and the Major remains open.
- **P1-R2-F13:** the case-variant header warning is withheld; `Age,age` can still reach a later case-insensitive consumer without the promised warning.
- **P1-R3-F6:** no released project artifact exists to hash or transfer, so the governed release/bundle boundary remains blocking and could not be exercised.
- **Reserved questions:** the three choices enumerated at the end of the
  round-5 response are outside this code ruling.

## Verification and attack coverage

The staged baseline before this report was written passed:

```text
.venv/bin/python -m pytest -q
  741 passed, 4 skipped

.venv/bin/python tools/offline_scan/scan_imports.py src
  9 files, 0 violations

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  dev input/lock passed

.venv/bin/python -m ruff check .
  passed

.venv/bin/python -m mypy src
  9 source files passed
```

All destructive demonstrations used isolated paths under `/tmp`. They covered
reference construction and proof independently; every current vector;
correct-rounding midpoints, ties, signs, subnormal/normal and overflow
boundaries; exact moment formulas and row order; true representable adjacency
in the grader; first-row positive, contradictory, and no-evidence states;
stdlib/pandas name and value agreement; explicit names/data modes; staging
symlinks and pre-existing neighbours; first/second write and rename failures;
rollback with and without an old target; cleanup failure and message truth;
case/normalization aliases and metadata errors; taxonomy thresholds,
unit-bearing values, sentinel spellings, out-of-range and contradictory cells,
sign and integer evidence, suppression and forced roles; deferred module and
class-body bindings; match captures and method lookup; f-string origins;
display-control bytes; deterministic serialization; dependency roots; and
profile/generator separation.

The review surveyed the complete staged diff and all `src/synthtwin` modules,
then read the redesigned reader, writer, taxonomy, arithmetic, reference
generator, scanner and their tests in detail. It also covered revision 2, all
five earlier reviews and responses, the numeric fixture and provenance entry,
dependency inputs and locks, workflow consumers, README, SECURITY, CHANGELOG,
and the failure catalog. This host is macOS; platform-specific behavior not
exercised by the project's simulations/skips remains outside direct host
coverage.

## Cosmetic observations

`git diff --cached --check` reports `src/synthtwin/reading.py:146` as a
leftover conflict marker. Inspection shows that it is the all-equals
underline below an `IMPORTS` heading inside the module docstring, not an
unresolved merge. This is cosmetic, but it makes that standard sanity check
noisy. Other stale prose is included above only where it changes the graded
accuracy contract, taxonomy dispatch, or a user-visible guarantee.

## Verdict

**Verdict: reject.** Blocking round-6 items are P1-R6-F1, P1-R6-F2,
P1-R6-F4, P1-R6-F5, P1-R6-F6, P1-R6-F7, P1-R6-F8, and P1-R6-F9;
P1-R3-F6 remains an independently blocking release-boundary item.

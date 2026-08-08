# Phase 1 combined plan-and-code review — round 1

**Reviewed baseline:** the uncommitted Phase 1 working tree above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`, including revision 1 of the
Phase 1 plan, the canonical reviewer and implementer briefs, the complete
ratified Phase 0 plan with Amendments A1–A3, all new and modified product,
test, workflow, dependency, and documentation files, and the owner-recorded
combined-review sequencing decision.

**Item count:** 18 — 12 blockers, 5 majors, 1 minor.

The ordinary suite and every standing local gate are green. That result does
not establish the properties Phase 1 claims. New scanner mutations reach real
pandas and NumPy writers while `offline-static` remains green; the declared
`read_csv` fence is not a scanner-enforced fence; and generated output targets
bypass the mandatory locality gate. On the product side, the two readers can
accept different values, numerical summaries can be materially wrong, common
columns are routed into information-destroying roles, distinct source
distributions can produce identical profiles, and values promised to be
suppressed reach both output files. The new dependency jobs and documented
hash-pinned installation path also do not execute as claimed.

These are control and behavior defects. Two cosmetic inconsistencies are
listed separately only so they are not mistaken for the basis of this review.

## Blocking items

### P1-R1-F1 — Blocker — the scanner does not enforce the `pandas.read_csv` fence

**Location:** `docs/plans/phase-1-profiler.md:102-120, 370-384`;
`tools/offline_scan/scan_imports.py:630-646, 1974-1992`.

P1-D2.1 says enumeration prevents a second `read_csv` call site without a
policy change. Enumeration actually permits any number of call sites and
places no constraint on the first argument's origin.

**Concrete failure scenario:** each of these new product-source mutations
scanned with zero violations:

```python
return pandas.read_csv("https://example.invalid/table.csv")
```

```python
return list(map(pandas.read_csv, ["https://example.invalid/table.csv"]))
```

The second route also shows that `_callback_slot_ok` treats any directly named
allowlisted API as a safe callback, even when the callback is the
network-capable reader and its input is URL text. A future source change can
therefore initiate network I/O while the required scanner stays green, with no
allowlist or plan change.

The current ordinary CLI route did pass this part of review: `read_table`
validates its input and hands the sole current `read_csv` call a `Path`. That
does not make the advertised preventive control true.

**Required repair:** enforce an exact fenced context or validated-local-path
provenance for every `read_csv` call, reject it as a callback, and permanently
add both mutations as red tests.

### P1-R1-F2 — Blocker — E5 loses pandas/NumPy origins and admits real writers

**Location:** `docs/plans/phase-1-profiler.md:434-449`;
`tools/offline_scan/scan_imports.py:514-537, 1160-1202, 1314-1354,
1837-1871`.

E5 checks the library recorded on an api-instance origin. The origin analysis
can replace or hide that library before the method check.

**Concrete failure scenario 1:** this mutation scanned with zero violations:

```python
frame = pandas.read_csv(pathlib.Path("/tmp/input.csv"))
disguised = typing.cast("object", frame)
disguised.to_sql("table_name", "postgresql://host/database")
```

`typing.cast` returns the same value, but `_call_result_origins` retags its
result as a `typing.cast` instance. E5 therefore no longer sees pandas. The
same bypass followed by `DataFrame.to_csv` wrote a file at runtime, and the
NumPy form followed by `array.tofile` wrote 16 bytes. This is not a theoretical
false negative: methods E5 exists to exclude execute.

**Concrete failure scenario 2:** a module-level frame followed by a function
with `global frame`, a conditional local-looking reassignment, and
`frame.to_csv(...)` also scanned green and wrote a CSV when the branch was
false. A class attribute with the same name similarly hid a module-level
frame, because the scanner treats class namespaces as lexical parents of
methods even though Python does not.

An uncalled property access such as `frame.style` is also green and reaches an
unenumerated pandas capability, so the audit cannot treat arbitrary returned-
object attributes as closed merely because direct method syntax is checked.

**Required repair:** preserve origins through value-preserving APIs such as
`typing.cast`; model `global`, `nonlocal`, and class lookup correctly; audit
capability-bearing properties; and retain cast, global, class-scope,
`to_sql`/`to_csv`, and `tofile` red mutations.

### P1-R1-F3 — Blocker — output files bypass the mandatory path-locality gate

**Location:** `src/synthtwin/profile.py:198-238`;
`src/synthtwin/cli.py:189-193`; `src/synthtwin/paths.py:1-31`.

Only an explicitly supplied output folder is validated. The two final target
paths are never passed through `validate_local_path`, and the public
`write_text_file` function writes any `Path` directly.

**Concrete failure scenario:** on Windows, put an existing reparse-point file
named `table-profile.json` in an otherwise local output folder and point it to
`\\server\share\profile.json`. Run `synthtwin profile table.csv`. The folder
walk does not examine that file and `Path.write_text` follows it, placing the
real-derived profile on a UNC share despite the standing rule that every
input, output, and temporary path passes the one locality gate. A POSIX probe
confirmed that the writer follows an existing target symlink; the security
violation is the Windows reparse path that Phase 0 expressly requires the gate
to reject.

This is not the named local-actor TOCTOU residual: the hostile output target
can exist before the command starts and is never checked.

**Required repair:** validate each exact output target immediately before the
write, including generated defaults, while retaining the ratified platform
link behavior; add a non-skippable Windows reparse mutation and a direct-writer
test.

### P1-R1-F4 — Blocker — the two-pass control compares dimensions, not values

**Location:** `src/synthtwin/reading.py:72-74, 125-142, 193-200, 321-380`;
`docs/plans/phase-1-profiler.md:122-152`.

The agreement check compares only row and column counts. It cannot establish
that the two readers saw the same bytes, header, or values.

**Concrete failure scenario 1:** after the structural pass read
`old_name,value\nold_a,1\nold_b,2`, a probe rewrote the file to the same shape
with header `new_name,value` and values `new_a,8` and `new_b,9`. `read_table`
accepted the result with the old column names and the new values. The plan and
README claim that an edit between passes fails; this one does not.

**Concrete failure scenario 2:** a fixed CSV placed `alpha\0omega` in data row
6. The stdlib reader retained the complete value while pandas' C reader
returned `alpha`. Both found six rows and two columns, so the truncated value
was silently accepted. The NUL defense examines only the first five rows.

Quoted newlines, blank physical lines, CRLF versus LF, a final row with and
without a trailing newline, and quoted empty fields agreed in the probes. The
failure is specifically the claim that equal dimensions imply equal reads.

**Required repair:** bind both passes to identical file content and compare
the interpreted header and values, or replace the split with a design that has
one authoritative parse plus an independently verified structural invariant.
Check NULs throughout any supported text input. Add both reproductions.

### P1-R1-F5 — Blocker — a headerless mixed table loses and publishes its first record

**Location:** `src/synthtwin/reading.py:214-236`;
`docs/plans/phase-1-profiler.md:166-170`.

The header check refuses the first row as data only when every cell looks
numeric. One text-like identifier beside one measurement defeats it.

**Concrete failure scenario:** this realistic headerless file was accepted:

```text
P001,34
P002,35
P003,36
P004,37
P005,38
P006,39
```

The resulting table had five rows and column names `P001` and `34`; the first
retained value was `P002`. The CLI exited zero, omitted the first person's row
from every statistic, and published `P001` as schema text outside all
identifier suppression.

This is a plan-design gap, not just an implementation deviation: P1-D3's
first-row rule itself covers only all-numeric or empty headers.

**Required repair:** define and implement a non-lossy header contract. An
ambiguous first row must be refused or explicitly resolved by the user; it
must never silently become schema. Add mixed identifier/measurement, small,
wide, and one-row headerless fixtures.

### P1-R1-F6 — Blocker — float conversion and 12-digit quantization publish contradictory or wrong statistics

**Location:** `src/synthtwin/parsing.py:243-279`;
`src/synthtwin/taxonomy.py:126-138, 182-223, 404-418`;
`docs/plans/phase-1-profiler.md:213-223, 460-487`.

The formulas match the stated linear quantile, sample-standard-deviation, and
moment-skew definitions on well-scaled inputs. Their float64 implementation
and the unconditional significant-digit rule are not numerically sound over
the accepted input domain.

**Concrete failure scenario:** profile the ten exactly written integers
`1000000000000000` through `1000000000000009`. Independent exact arithmetic
gives mean `1000000000000004.5`, sample standard deviation approximately
`3.02765035409749`, and skewness zero. The reviewed code published every
percentile, including minimum and maximum, as `1000000000000000.0`, standard
deviation `3.03051609099`, and skewness `0.130270403551`. The profile says both
that the range is zero and that its spread is nonzero.

The defect is not limited to one rounding boundary. The same multiset ordered
as `[1e16, 1, -1e16]` versus `[1e16, -1e16, 1]` produced means of `0` and of
a twelve-digit rounding of one third; values around `1e-300` produced zero
spread; values around
`1e308` overflowed reductions and published null moments; and decimal inputs
below binary64 range parsed as zero. These are plausible outputs, not
refusals.

The charter requires an independently ratified public method specification
and frozen neutral reference vectors before numeric machinery becomes its own
oracle. The current golden was generated from this implementation, and the
only hand test does not independently exercise skewness or difficult scales.

**Required repair:** choose a numerically stable, scale-aware representation
and reduction method; preserve meaningful source resolution; specify behavior
for overflow, underflow, and non-finite reductions; and add independent
high-precision reference vectors covering translated, scaled, permuted,
extreme, undefined, and rounding-boundary cases before accepting new goldens.

### P1-R1-F7 — Blocker — automatic missing/sentinel decisions irreversibly delete real data and retain real sentinels

**Location:** `src/synthtwin/parsing.py:43-59`;
`src/synthtwin/taxonomy.py:226-305, 451-483`;
`docs/plans/phase-1-profiler.md:233-243`.

The fixed rule cannot distinguish an extreme real value from a missing-value
code, and Phase 1 provides no override or ambiguity state. There are also
implementation errors around the fixed rule.

**Concrete failure scenarios:**

- One legitimate `9999` among 199 ordinary measurements is exactly 0.5% and
  far outside their IQR, so it is removed and the published maximum is false.
- One genuine `9999` missing-value code among 1,000 ordinary measurements is
  below 0.5%, so it remains data and distorts the maximum.
- A categorical region column containing the legitimate code `NA` is
  unconditionally treated as missing. A three-region column can become
  binary after all `NA` rows disappear.
- With 199 numeric values, one candidate, and one unparseable present value,
  the plan's share is below 0.5% of present values. The implementation divides
  by parsed numeric values only and removes the candidate at 0.5%.
- With 60 zeros, 20 `-999` values, and 20 `9999` values, the candidates mask
  one another's IQR test. Only one is removed and the other becomes a
  plausible binary level, although both may be one missing convention.
- With 90 numeric values, ten nonnumeric values, and one candidate, the
  initial numeric threshold fails and no candidate verdict is produced,
  contradicting “before every role” and “every candidate.”

**Required repair:** add an explicit per-column way to confirm, reject, or
declare missing conventions; do not silently decide ambiguous candidates.
Make the denominator and multi-candidate algorithm match the ratified rule,
run verdicts independently of eventual role, and add all false-positive,
false-negative, denominator, masking, and text-code fixtures.

### P1-R1-F8 — Blocker — the identifier guard still swallows realistic measurements and categories

**Location:** `src/synthtwin/taxonomy.py:536-619, 621-862`;
`docs/plans/phase-1-profiler.md:175-250`.

“Not 99% numeric, not 99% dates, single word” does not establish that a
high-uniqueness column is an identifier. Because identifier precedes every
remaining role, an unsupported measurement syntax loses its distribution
instead of taking a conservative, reviewable path.

**Concrete failure scenarios:**

- Values `0` through `97` plus the word `trace` are 98/99 numeric, just below
  the numeric threshold. All 99 are distinct single words, so the column is
  called an identifier and its almost-entirely numeric distribution vanishes.
- A two-row `T`/`F` column is called an identifier before the documented
  binary equivalence rule can run.
- Unique currency amounts, percentages, and time-of-day values without dates
  are single words unsupported by the parsers and become identifiers.
- Repeated zero-padded codes such as `00501`, `02139`, and `52242` become
  numeric counts, dropping their padding and discrete labels. There is no
  categorical override.
- 1,001 categorical labels repeated 20 times each all clear the privacy floor
  but exceed the hard ceiling by one, so the entire distribution is reduced
  to free-text lengths.

These cases cover small, mixed-convention, zero-padded, time, currency,
percentage, and high-cardinality inputs requested by the brief. The sole
`--identifier` override only moves a column into suppression; it cannot repair
any of these opposite-direction errors.

**Required repair:** redesign the order and ambiguity policy so unsupported
high-uniqueness syntax does not imply identifier, provide explicit role
corrections in both directions, preserve formatted discrete codes, and add
realistic neighboring fixtures rather than only synthetic happy paths.

### P1-R1-F9 — Blocker — the profile contract is not sufficient for a table-independent generator

**Location:** `src/synthtwin/taxonomy.py:313-373, 668-775`;
`src/synthtwin/parsing.py:319-467`;
`docs/plans/phase-1-profiler.md:39-53, 264-293`.

The file boundary itself is structurally respected: only `reading.py` opens
the user's table, and the profile carries no source path, timestamp, or
machine identity. The document nevertheless discards facts a generator needs
to preserve the source distribution.

**Concrete failure scenario 1:** two 100-row date columns had the same minimum,
maximum, and row count. One put 49 rows at each endpoint and two in the middle;
the other put 98 in the middle and one at each endpoint. Their complete
`ColumnProfile` objects were equal. A profile-only generator must emit the
same distribution for both and therefore cannot match both source tables.

**Concrete failure scenario 2:** with the default floor, binary counts of 1/9
and 5/5 both suppress both labels and serialize to equal profiles: two
suppressed levels and ten suppressed rows. Privacy does not require deleting
the anonymous count multiset; the current pooling loses the probability.
Categorical rare-level splits have the same collision.

**Concrete failure scenario 3:** fractional ISO datetimes at `.001`, `.500`,
and `.999` seconds all produced the same second-level earliest/latest value.
For mixed offsets, the code sorts local wall-clock strings, discards which
offset belongs to which value, and emits only `mixed`. For example,
`2024-01-01T00:30:00+14:00` is chronologically earlier than
`2023-12-31T23:45:00-12:00`, but the profile reports the opposite local-text
ordering. Offsets `+99:99` and `+24:60` are accepted as valid. This also
contradicts P1-D5's explicit-offset/fixed-precision serialization statement.

Numeric stragglers create a related structured-contract gap: their count is
only embedded in prose while `n_present` includes them and the numeric
statistics do not. A generator should not have to parse an English remark to
know part of a column was excluded from its distribution.

**Required repair:** define a distribution-bearing v1 contract for every
generatable role, including datetime shape and precision, anonymous counts for
suppressed levels, and structured unparsed counts. Add collision tests proving
that inputs whose generator-relevant distributions differ cannot serialize to
the same machine profile unless the loss is an explicit, ratified fidelity
limit.

### P1-R1-F10 — Blocker — suppression is porous across role order, remarks, and missing-source keys

**Location:** `src/synthtwin/taxonomy.py:226-247, 250-305, 421-479,
507-534, 572-665`; `src/synthtwin/cli.py:143-151, 181-218`;
`docs/plans/phase-1-profiler.md:295-317`.

The direct `levels` filtering works in its tested categorical and binary
cases. It is not an output-wide noninterference control.

**Concrete failure scenarios:**

- Eleven repetitions of the neutral canary `amber-id`, with that column
  passed as `--identifier`, take the earlier constant branch. The role is
  `constant` and both JSON and summary publish the canary because its count
  meets the floor. The forced-identifier branch is never reached.
- Two hundred zeros plus one `-999` become binary. The one-row label is absent
  from `levels`, while a remark prints `-999` and its sentinel decision in
  both files. The publication note simultaneously says the label is not
  published.
- Values `1` through `98`, the raw spelling `-9.99e2`, and one narrative value
  normalize the numeric sentinel and then route to free text. The profile
  still contains `missing_by_source: {"-9.99e2": 1}` although the free-text
  note promises no value appears. The same channel leaks from a forced
  identifier.
- If a user misspells a numeric ID column in `--identifier`, the CLI builds and
  writes the profile with numeric extrema and percentiles first, then merely
  warns that the named column was absent. The intended suppression failure is
  not refused before output.

These are the exact constant, binary, identifier, free-text, remark, missing-
source, and option-error channels the acceptance criterion needs to cover.

**Required repair:** make a forced role take precedence over every automatic
role, refuse unknown override names before building or writing, and enforce
suppression across the complete serialized JSON and summary rather than only
`levels`. Resolve the privacy conflict with per-spelling reporting explicitly;
for suppressed roles, a neutral sentinel category can retain counts without
publishing a raw value. Add full-output canary tests for every field.

### P1-R1-F11 — Blocker — the minimum-version job is red by construction and reopens the build-hook boundary

**Location:** `.github/workflows/ci.yml:1079-1109`;
`pyproject.toml:1-3`; `tests/test_dependencies.py:26-69`.

The job installs the minimum runtime/test lock, which does not contain
Hatchling, and then invokes a source build with `--no-build-isolation`.

**Concrete failure scenario 1:** in a clean temporary virtual environment,
the workflow's exact local-install command failed with exit 2:

```text
BackendUnavailable: Cannot import 'hatchling.build'
```

Thus `minimums` and the aggregate gate cannot reliably pass. If a hosted image
happens to supply Hatchling, the job silently trusts an ambient, unpinned
backend instead.

**Concrete failure scenario 2:** a pull request changes `build-backend` or
`backend-path` to a local metadata hook that performs network I/O. The
minimums job executes that hook on a networked hosted runner, outside the
Phase 0 `--network none` build container and before the test socket guard.
The later gate cannot undo the egress.

The claimed floor-drift control also reads `requirements-dev.in`, while this
job installs `requirements-min.lock`. Changing and regenerating the minimum
input can therefore stop testing the declared floor while all current drift
tests and structural lock checks remain green.

**Required repair:** install and execute the project only from the already
network-none-built, content-checked wheel, or put the source build behind the
same boundary with a fully pinned build closure. Make the drift test compare
the actual minimum input/lock, and prove the exact floor environment in a
clean mutation.

### P1-R1-F12 — Blocker — the advertised hash-pinned institutional install executes an unhashed build closure

**Location:** `README.md:135-147, 175-193`;
`.github/workflows/ci.yml:748-762`; `pyproject.toml:1-3`.

The documented locked-machine procedure installs the hashed runtime closure
and then runs `pip install --no-deps .`. `--no-deps` does not disable PEP 517
build isolation.

**Concrete failure scenario:** an institution follows the published commands
on a fresh connected machine. Pip resolves and executes Hatchling and its
build dependencies from an index without the hashes in
`requirements-install.lock`. On a genuinely air-gapped machine the same step
fails unless those unlisted build packages happen to be cached. The path
therefore provides neither property it advertises.

CI does not exercise these commands: its fresh-venv smoke installs the already
built wheel with `--no-index --no-deps`. That path is sounder, but it cannot be
evidence for the different source-install instructions.

**Required repair:** document and test one exact wheel-based, no-index,
hash-bound institutional procedure, or include and consume a separately
governed build closure behind the ratified build boundary. Do not call the
runtime-only lock a complete build closure.

## Major items

### P1-R1-F13 — Major — E2/E4 understate caller-code execution surfaces

**Location:** `tools/offline_scan/scan_imports.py:547-658, 1289-1302,
1974-2049`; `docs/plans/phase-1-profiler.md:385-433`.

**Concrete failure scenario 1:** `f"{'x':{spec}}".strip()` scanned clean when
`spec` was an untraced parameter. At runtime a supplied object's `__format__`
wrote a marker. The f-string analysis checks the main formatted value but does
not recursively inspect its dynamic `format_spec`, laundering the result into
the text origin.

**Concrete failure scenario 2:** supported NumPy 2.5.1 exposes
`errstate(*, call=...)`. A mutation entered
`numpy.errstate(all="call", call=callback)` and divided by zero; the callback
ran, while the scanner reported zero violations. P1-D10 says `errstate` takes
only string keywords and no E2 API takes a callable; the callback table has no
entry for it.

These remain Major rather than Blocker because execution is caller-supplied
code under the authority already named by Amendment A3. The claimed residual
is still inaccurately bounded: E4 reaches any format-spec object, not only a
`str` subclass, and E2 omits a documented callable slot.

The explicit `read_csv` callable-parameter names were complete across the
reviewed pandas 2.1 and 3.0 signatures (with `date_parser` removed in 3.0), and
E6's `ArgumentParser.formatter_class` position remains correct. The scanner's
`read_csv` failure is F1's universal acceptance of an allowlisted API as a
callback, not a missing documented pandas slot.

**Required repair:** recursively analyze dynamic format specifications, add
the supported `errstate.call` slot, update the capability audit, and add both
red mutations. Audit other protocol-bearing parameters such as array-like
dispatch under the same A3 accounting.

### P1-R1-F14 — Major — a failed second write leaves an undisclosed first artifact

**Location:** `src/synthtwin/cli.py:181-218`;
`src/synthtwin/profile.py:222-238`;
`docs/plans/phase-1-profiler.md:295-308`.

The CLI writes JSON, writes the text summary, and only then prints the summary,
real-derived-material disclosure, missing-identifier notice, and lowered-floor
warning. P1-D6 says disclosure happens before files are written.

**Concrete failure scenario:** make `table-profile.txt` an existing directory
and run with `--smallest-group 1`. The JSON write succeeds, the summary write
fails, and the command returns 1. The JSON containing one-row labels remains
on disk, while none of the disclosure or lowered-floor warning is printed.

**Required repair:** validate/preflight both targets, present disclosure and
warnings before persistence, and make the two-file outcome transactional or
recoverably clean up the first artifact on second-write failure. Add a test
that inspects the filesystem and both streams after each possible failure.

### P1-R1-F15 — Major — the claimed streaming/memory failure path can instead crash or bias the profile

**Location:** `src/synthtwin/reading.py:125-142, 177-205, 321-380`;
`src/synthtwin/errors.py:203-213`; `src/synthtwin/cli.py:256-268`.

The structural pass materializes every CSV row, then slices another list of
all data rows. Later pandas-to-column conversion, taxonomy allocations,
document building, summary rendering, and serialization allocate further
copies outside the two local `MemoryError` catches. This contradicts P1-D3's
repeated statement that the structural pass holds one row at a time.

**Concrete failure scenario:** a table completes `pandas.read_csv` but exhausts
remaining memory during column conversion or `build_document`. A probe
injecting `MemoryError` at document building escaped `main`; the console entry
point emits a traceback rather than the catalog's size-aware refusal. The
README promise that oversized tables are explained instead of crashing is
therefore false.

The catalog's recovery advice compounds the statistical risk: it recommends
the first 100,000 rows as generally equivalent. For a table sorted by date,
cohort, site, or severity, following that instruction produces a plausible but
systematically biased profile.

**Required repair:** make the structural pass genuinely bounded-memory or
state the real peak-memory model; convert all expected allocation failures at
the CLI boundary into one actionable refusal; and recommend a representative
extract, never the first rows as a general substitute.

### P1-R1-F16 — Major — the failure-catalog tests do not exercise real failures or prove reachability

**Location:** `src/synthtwin/reading.py:125-176, 349-357`;
`src/synthtwin/errors.py:182-213`;
`tests/test_failure_catalog.py:1-134`;
`docs/plans/phase-1-profiler.md:319-334`.

**Concrete failure scenario 1:** an unclosed quoted field reaches pandas and
prints raw library text including “Error tokenizing data” and “C error,” then
advises quoting commas rather than closing the missing quote. The no-jargon
test passes because it calls the message builder with a sanitized invented
detail instead of the real exception. Likewise `--smallest-group bananas`
uses argparse's “invalid int value” rather than the catalog's plain-language
builder.

**Concrete failure scenario 2:** the “reachability” test only searches source
text for `errors.<name>(`. A comment or dead branch satisfies it. The
`not_utf8_or_latin1` entry is in fact behind Latin-1 raising
`UnicodeDecodeError`, which cannot happen for arbitrary bytes, yet the test is
green. The plan's exact-shape claim is also not implemented: tests check broad
length, punctuation, and keyword properties rather than exact messages from
each runtime trigger.

**Required repair:** drive every catalog item through the public CLI using the
actual triggering state, assert exit code/stream/actionable message, and prove
coverage structurally rather than by substring. Normalize third-party and
argparse errors into catalog-owned language. Remove or make reachable any dead
entry.

### P1-R1-F17 — Major — “per-spelling” missing counts merge distinct source representations

**Location:** `src/synthtwin/taxonomy.py:226-247`;
`src/synthtwin/parsing.py:110-133`;
`docs/plans/phase-1-profiler.md:233-243`.

**Concrete failure scenario:** values `NA`, `na`, padded `Na`, an empty cell,
and a whitespace-only cell yield correct totals (`n_present=0`,
`n_missing=5`) but only `{"na": 3, "(blank)": 2}`. Case and surrounding
whitespace are normalized before counting, so the profile cannot tell the user
how the values were actually written or let a generator reproduce those
representations.

**Required repair:** either preserve exact source spellings where privacy
permits or amend every plan/document claim to a named canonical missing class.
Define the interaction with F10 explicitly so an exact rare spelling in an
identifier or free-text column is never exposed.

## Minor finding

### P1-R1-F18 — Minor — a valid Latin-1 header can be falsely refused as UTF-16

**Location:** `src/synthtwin/reading.py:112-123, 197-200`.

**Concrete failure scenario:** a valid supported Latin-1 CSV whose first
header begins with byte `0xFF` is decoded to a legitimate U+00FF character.
The BOM heuristic checks that lone character rather than a complete UTF-16 BOM
sequence and refuses the file as UTF-16/binary, falsely saying the first row
contains zero bytes.

**Required repair:** recognize complete byte-order signatures before text
decoding, not isolated legitimate Latin-1 characters; add both endian BOMs and
valid leading `0xFF`/`0xFE` controls.

## Checks, properties, and attack classes examined

The complete local baseline passed before this artifact was added:

```text
.venv/bin/python -m pytest -q
  478 passed, 4 skipped

LC_ALL=C PYTHONIOENCODING=ascii .venv/bin/python -m pytest -q
  478 passed, 4 skipped

.venv/bin/python -m pytest -q tests/test_offline_scan.py
  61 passed

.venv/bin/python tools/offline_scan/scan_imports.py src
  9 files, 0 violations

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/decontamination/verify_attestation.py
  verified

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  passed

explicit dev, install, and minimum input/lock validations
  passed

.venv/bin/python -m ruff check .
  passed

.venv/bin/python -m mypy src
  passed (9 source files)

git diff --check
  passed
```

After this public artifact was written, the full decontamination scan was run
again and remained clean. The attestation verifier, provenance checker,
offline source scan, lock validator, ruff, mypy, the 478-test suite, and diff
whitespace check were also rerun and remained green.

Scanner attacks under `/tmp` covered direct and aliased imports; unlisted
pandas/NumPy APIs; direct frame/array methods; value-preserving casts; global,
nonlocal, branch, and class-scope name resolution; properties, attributes,
subscripts, operators, comparisons, dunders, iterators, and bound methods;
direct and callback-mediated `read_csv`; f-string values and nested format
specifications; string slices and chained methods; callable slots; and the
supported pandas/csv/argparse signature tables. Direct unlisted APIs and
direct frame/array writers were red as intended. Cast/scope writers, direct
URL reads, `read_csv` as `map` callback, nested format specs, and
`errstate(call=...)` were unexpectedly green.

Reader probes covered UTF-8/BOM/Latin-1 decisions, blank physical lines,
quoted newlines, quoted empty cells, CRLF/LF, trailing/no trailing newline,
ragged rows, a late NUL, a same-shape rewrite, mixed headerless input, and
output symlink/reparse behavior. The ordinary newline and quoted-field cases
agreed; F4 and F5 identify the corrupting cases.

Statistical checks used independent exact/high-precision calculations for the
ladder, mean, sample standard deviation, and moment skewness; exercised
undefined one-value/two-value/zero-spread cases; translation, scaling,
permutation, underflow, overflow, and large-offset inputs; and attacked every
sentinel decision branch, multiple simultaneous candidates, parse-rate
interaction, and denominator choice. The stated formulas were correct on
well-scaled values; the accepted numeric domain and publication machinery were
not.

Taxonomy probes covered empty, constant, identifier, binary, datetime,
numeric, categorical, and free-text neighbors; small, wide, one-row, and
mixed-convention tables; zero-padded codes; times, negative counts,
percentages, currency, T/F, and more than 1,000 levels. The output search
covered names, evidence, remarks, publication notes, role details,
missing-source keys, sentinel spellings, constant/binary/categorical labels,
identifier/free-text length blocks, both serialized files, stdout, stderr,
and partial-write state.

Boundary review traced every product table read and output write, checked that
only `reading.py` opens the table, checked that path/time/machine identity do
not enter the document, and constructed generator-relevant profile collisions.
Determinism review checked sorted mapping/set consumers, stable level ordering,
JSON canonicalization, locale-independent parsing, line endings, and repeated
normalized hashes under hash seeds 1, 2, 999, and random. No hash-order or
locale divergence was found. P1-D11 is honest that quantization is not a proof
of cross-platform equality; F6 is instead the more serious finding that the
control destroys or contradicts statistically meaningful values. This host
used Python 3.13.14, pandas 3.0.5, and NumPy 2.5.1; no claim is made that one
local environment proves every universal-lock resolution.

Supply-chain review covered all three lock/input pairs, declared floors,
marker parsing, workflow consumers, the minimums job in a clean temporary
environment, the network-none build boundary, the fresh-wheel smoke, and the
published institutional commands. Failure UX review exercised all ordinary
catalog categories, real parser details, argparse failures, output failures,
and injected memory exhaustion. No validator exists in Phase 1 by plan; the
honesty check here targeted profile/suppression assertions and tests that
cannot establish what their names claim.

## Cosmetic observations not counted as items

`SECURITY.md` still tells an auditor to expect `dependencies = []`, and the
changelog calls E1–E6 “four” extensions. These should be corrected when the
behavioral repairs touch those documents, but they neither change execution
nor contribute to the decision above.

## Verdict

**Verdict: reject.** Blocking items: P1-R1-F1 through P1-R1-F12.

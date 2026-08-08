# Phase 1 combined plan-and-code review — round 2

**Reviewed baseline:** the staged Phase 1 tree above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`, including the amended Phase 1
plan, the round-1 review and response, all product and test code, both numeric
reference artifacts, the scanner changes, workflows, requirement inputs and
locks, and public documentation.

**Item count:** 14 — 9 blockers and 5 majors.

**Verdict: reject.** Blocking items: P1-R2-F1 through P1-R2-F9.

The staged-tree claim in R1-X2 is true. `tools/decontamination/check.py` obtains
its scope from `git ls-files`; the Phase 1 source, tests, vectors, scanner, and
round-1 artifacts are now present in the index, and the scanner examined that
tree. That does not rescue the repaired claims. The fenced reader can still be
used as a callback or reached with forged provenance, pandas/NumPy capabilities
still escape the origin analysis, accepted finite columns violate the frozen
accuracy contract, the oracle's claimed rounding proof is false, hard links can
still destroy the input, the two writes are not one outcome, and the published
institutional procedure still takes routes CI deliberately avoids.

These are control and behavior defects, not wording consistency. Two
non-behavioral observations are isolated at the end and do not contribute to
the verdict.

## Disposition of the claimed repairs

| Round-1 item | Round-2 disposition |
| --- | --- |
| P1-R1-F1 | **Fails.** The intended module-qualified direct call is fenced, but bare-name references and false/cross-scope `localpath` origins bypass it (P1-R2-F1). |
| P1-R1-F2 | **Fails.** Positional `typing.cast` and direct pandas attributes are caught, but valid keyword casts and other origin-shedding expressions reach real writers (P1-R2-F2); the new origin also weakens callback-slot checking (P1-R2-F10). |
| P1-R1-F3, P1-R1-F14, R1-X1 | **Fail.** Directories and POSIX symlinks to the source are refused, but hard-link aliases defeat target identity and write failures leave or replace artifacts (P1-R2-F7 and P1-R2-F11). |
| P1-R1-F6/F6f | **Fail.** Sorting, `math.fsum`, recentering, the NumPy ban, and fixture regeneration hold, but range accounting is unwired, accepted values breach the contract, and the oracle/test logic has boundary errors (P1-R2-F3 through P1-R2-F5). |
| P1-R1-F10, absent-column part | **Holds.** An absent named identifier exits 2 before document construction or writes, and the message names actual columns. The response's declared remainder stays open. |
| P1-R1-F11 | **Partly holds, overall fails.** The minimums job consumes the network-none-built wheel, but nothing binds the lock it installs to the input the drift test checks (P1-R2-F8). |
| P1-R1-F12 | **Fails.** The wheel is named, but the runtime command still consults an index and the recommended self-build still resolves an unpinned backend (P1-R2-F9). |

## Blocking items

### P1-R2-F1 — Blocker — the `read_csv` fence still has direct bypasses

**Location:** `docs/plans/reviews/phase-1-review-round-1-response.md:103-115`;
`tools/offline_scan/scan_imports.py:1255-1259, 1427-1451, 1817-1881,
1915-1928, 2125-2143, 2389-2404`.

The fenced-reference check exists in `visit_Attribute`, not `visit_Name`.
`_callback_slot_ok` then treats the bare imported API as an acceptable
callback. Separately, `_localpath_call_result` accepts a resolved validator
name while `_resolve` discards simultaneous def/unknown origins, and the
marker carries no producing-function identity. The promised “direct target,
same function, produced only by the real validator” rule is therefore not the
implemented rule.

**Concrete failure scenario 1:** this product-source mutation scanned with
zero violations:

```python
from pandas import read_csv

def fetch(paths):
    return list(map(read_csv, paths))
```

Give `fetch` a URL string. Pandas receives that string through the callback
and enters its URL-opening path while the required scanner remains green.
Storing the bare imported name first is green as well.

**Concrete failure scenario 2:** import `validate_local_path`, redefine that
same name in the scanned module as a pass-through returning its argument, and
then pass the result to `pandas.read_csv`. The mutation scanned green because
the import origin survives in the scanner's union while the def origin is
discarded during dotted resolution; Python runs the later pass-through and
pandas receives the original URL. A separate class-scope probe also scanned
green: the scanner read a class attribute carrying a real local-path marker,
while Python's method lookup read a module global containing a URL. This is
the class-namespace defect P1-R1-F2 already demonstrated, now manufacturing
the new fence token.

**Required repair:** apply fenced-reference enforcement to every reference
shape, not just attributes; reject a fenced API in every callback/stored-value
route; make the provenance token carry and require the current function's
identity; and treat any shadowed, ambiguous, class-inherited, outer-scope, or
unknown validator binding as non-provenance. Keep all three mutations as red
tests and make them execute far enough to prove the URL-opening branch is not
reached.

### P1-R2-F2 — Blocker — F2 still loses library origins and reaches writers

**Location:** `tools/offline_scan/scan_imports.py:1294-1369, 1387-1397,
1856-1870, 1936-1952, 1981-2015, 2217-2240, 2389-2404`;
`tests/test_offline_scan.py:1320-1340`.

The cast repair recognizes exactly two positional arguments. The Python API
also accepts `typing.cast(typ=..., val=...)`; that form is tagged as an
instance produced by `typing.cast`, so the original pandas origin disappears.
The scanner also deliberately turns a subscript of a pandas value into
unknown, then accepts conditional, Boolean, and assignment-expression call
targets without applying the computed-call rejection used for a subscript or
call target. Class names and pattern captures remain incorrectly modelled.

**Concrete failure scenario 1:** load a frame through the fenced reader, run
`typing.cast(typ="object", val=frame)`, and call `to_csv` on the result. The
source scanned with zero violations and wrote the requested CSV. The only
regression test uses positional syntax.

**Concrete failure scenario 2:** select a Series with `frame["secret"]`, put
its `to_csv` method on one branch of a conditional call target, and call the
result. The mutation scanned green and wrote a CSV. Replacing that path with
`frame["secret"].values.tofile` reached a NumPy object and wrote bytes even
though NumPy cannot be imported from `src/`. Class-shadow and `match`-capture
variants likewise scanned green and wrote frames.

**Required repair:** preserve restricted origins through every
value-preserving construct and through restricted-object subscripts; reject
every call-target AST form unless it is in a closed, explicitly audited
grammar; implement Python's class and pattern-binding semantics conservatively;
and handle every supported call form of value-preserving APIs. Add runtime red
mutations for keyword cast, Series/array derivation, conditional/Boolean/walrus
targets, class lookup, and pattern capture.

### P1-R2-F3 — Blocker — out-of-range accounting is dead code

**Location:** `docs/plans/phase-1-profiler.md:521-529`;
`src/synthtwin/parsing.py:259-331`;
`src/synthtwin/taxonomy.py:420-422, 559-587, 827-879`.

`parse_number` does refuse both overflow and nonzero underflow, and
`number_out_of_range` identifies them. Nothing calls the latter: the taxonomy
sees only `None`, spends the ordinary non-number allowance, publishes no
`n_out_of_range`, and can change the role.

**Concrete failure scenario:** profile a 202-row measurement containing the
distinct strings `1` through `199` plus `1e999`, `2e999`, and `3e999` (the
same result occurs with `e-999`). `number_out_of_range` returns true for the
three cells, but `profile_column` routes the column as `identifier` with no
range count. With 200 valid values and two such cells it stays numeric, but
the remarks call them ordinary values that are “not numbers” and the details
still omit `n_out_of_range`. Both outcomes contradict P1-D11 and reproduce the
response's claimed mirror-case repair.

**Required repair:** classify parse outcomes once as valid, malformed, or
out-of-range; exclude the third category from the straggler budget while
carrying its count into every applicable profile; define behavior when every
numeric-looking value is out of range; and add role-boundary tests for high and
low range failures.

### P1-R2-F4 — Blocker — accepted finite columns violate P1-D11

**Location:** `docs/plans/phase-1-profiler.md:460-529`;
`src/synthtwin/taxonomy.py:18-46, 212-237, 249-335`;
`tests/test_numeric_reference.py:34-63, 72-100, 120-140`.

Scaling every value by the exponent of the largest one is not exact across
the accepted binary64 domain. A small normal operand can become subnormal or
zero before `math.fsum` sees it. The interpolation formula also rounds the
weighted gap before adding it to the lower bracket. The frozen tests hide the
latter failure behind a tolerance not present in the plan.

**Concrete failure scenario 1:** the three accepted values

```text
-1.7976931348623157e308
1
1.7976931348623157e308
```

have exact float-input sum 1 and correctly rounded exact mean
`0.3333333333333333`. `_moments` publishes `0.33333333333333304`, five actual
representable steps away from the one-step contract. All six row orders give
the same wrong answer. Replace the middle value by `1e-16` and scaling erases
it entirely: the published mean is `0.0`, not
`3.3333333333333335e-17`.

**Concrete failure scenario 2:** the committed `subnormal` vector contains
the ten values `m, 2m, ..., 10m`, where `m = 2^-1074`. Its exact p50 is
`5.5m`, which rounds half-even to `6m = 3e-323`; `_quantiles` returns
`5m = 2.5e-323`. The written bracket-relative bound is about `2.63e-338`,
while the error is one full minimum step, about `4.94e-324`. The test adds a
`5e-324` floor and passes exactly at that floor while claiming P1-D11 records
it; P1-D11 does not.

Sorting did make every examined result row-order invariant. The stronger
machine-independence claim still exceeds both D12's tested-matrix scope and
Python's guarantee: Python documents that `math.fsum` can occasionally
double-round an intermediate on some non-Windows extended-precision builds.
Serializing the unrounded bit means those supported builds can differ by a
last bit even after the two local scenarios are fixed.

**Required repair:** use a summation/scaling method that does not discard any
accepted finite operand, make interpolation safe at subnormal and extreme
brackets, and either meet the literal frozen bounds or amend them before code
is accepted. Test actual representable-step distance with cancellation plus
near-overflow, subnormal ties, every permutation, and the declared platform
scope.

### P1-R2-F5 — Blocker — the new numeric oracle is not a valid oracle

**Location:** `docs/plans/phase-1-profiler.md:506-540`;
`tools/reference/make_numeric_reference_vectors.py:108-178, 184-257`;
`tests/test_numeric_reference.py:1-18, 34-63, 72-140`.

The reference generator says its square-root result is proved correctly
rounded by exact midpoint comparisons. Its loop uses strict comparisons and
does not apply half-even parity when the exact value is on a midpoint. Its
walk around zero is invalid as well. The test's `_ulp_distance` is a relative
error divided by `abs(expected) * eps`, not distance between representable
numbers, and the undocumented percentile floor masks a current contract miss.

**Concrete failure scenario:** let `m = 2^-1074`. For the exact sample
`[0, 0, 2m, 3m]`, sample standard deviation is `1.5m`, exactly halfway
between `m` and `2m`; half-even must choose `2m = 1e-323`. The generator's
`stats` reports `m = 5e-324`. For `[0, 0, 0, 0, m]`, it reports a negative
standard deviation (`-4m`) where the correctly rounded result is zero. An
oracle that can produce a negative spread and mishandles the exact boundary
it claims to prove cannot anchor implementation acceptance.

The current sixteen cases happen not to exercise that defect: independent
integer midpoint checking, including tie parity, found all 218 committed
mean/std/skew/ladder float candidates correctly rounded. The surrounding
oracle metadata is still false. `exact_decimal` caps terminating expansions at
200 significant digits and labels the truncation exact; 96 of 778 rendered
rationals disagree with their exact values. For example, the minimum
subnormal expansion needs 751 significant digits. `_ulp_distance` can also
call a three-representable-step error only `1.5` and therefore admit it under
the two-step standard-deviation limit.

**Required repair:** implement exact lower/upper-neighbour selection with
half-even parity and a correct zero boundary; render terminating rationals in
full or label approximations honestly; use bit/`math.ulp`-based distances;
remove any tolerance absent from P1-D11; and add generator boundary vectors
that fail the current code. Re-review and freeze the resulting vectors before
using them as the implementation oracle.

### P1-R2-F6 — Blocker — accounting notation can reverse an explicit sign

**Location:** `docs/plans/phase-1-profiler.md:211-220`;
`src/synthtwin/parsing.py:225-301`;
`src/synthtwin/taxonomy.py:827-879`.

After removing accounting parentheses, `parse_number` accepts an inner sign
and then blindly negates the parsed value. A visibly negative value can become
positive, and a visibly positive value can become negative, without a refusal
or remark.

**Concrete failure scenario:** a real CLI run over one column named `debt`
with rows `(-1)` through `(-100)` exits 0. The profile says the role is
`count`, minimum `1.0`, maximum `100.0`, mean `50.5`, and `n_negative` zero.
The source explicitly contains minus signs; preserving the sign would give a
mean of `-50.5`, while treating the notation as contradictory should refuse
it. `(-1,234.50)` similarly becomes positive `1234.5`, and `(+5)` becomes
negative `-5`.

**Required repair:** reject an explicit inner sign under accounting
parentheses, or specify a non-sign-reversing interpretation that cannot turn
visible minus into plus. Add direct parser and end-to-end role/statistic tests
for parenthesized unsigned, plus-signed, minus-signed, grouped, exponent, zero,
and out-of-range forms.

### P1-R2-F7 — Blocker — hard links defeat input and output identity

**Location:** `src/synthtwin/cli.py:211-225`;
`src/synthtwin/profile.py:183-187, 205-281, 284-301`;
`tests/test_cli_profile.py:158-193`.

The input-protection check compares resolved path strings. Hard links have
different path strings and the same underlying file, so resolution does not
expose the alias. The two output paths are never compared by file identity,
and target preflight rejects only directories.

**Concrete failure scenario 1:** create `table.csv`, then create
`table-profile.json` as a hard link to it before running the default CLI.
The command exits 0 and `write_text` truncates the shared inode, replacing the
input CSV with JSON. The alias exists before execution and requires no
timing-dependent substitution.

**Concrete failure scenario 2:** hard-link `table-profile.json` and
`table-profile.txt` to each other. The command exits 0; the second write
replaces the first through the shared inode, so both names contain only the
human summary and the machine-readable profile is gone. A FIFO at the JSON
name is also accepted: with a reader the CLI exits 0 and sends the full JSON
through the pipe while leaving no regular profile; without a reader it blocks
indefinitely.

**Required repair:** require each existing target to be a regular file,
reject other node types, and compare stable file identity for input versus
both outputs and output versus output before any write. Cover hard links on
every supporting platform and FIFOs/devices on POSIX, alongside the existing
symlink and directory tests.

### P1-R2-F8 — Blocker — the minimum lock is not bound to the declared floors

**Location:** `docs/plans/phase-1-profiler.md:85-100`;
`.github/workflows/ci.yml:1079-1119`;
`tests/test_dependencies.py:37-64`;
`tools/supply_chain/validate_lock.py:250-275`.

The repaired test parses `requirements-min.in`; the job installs
`requirements-min.lock`. The structural validator validates both files
independently and never proves that the lock's direct pins equal the input's
pins. `pip freeze` is printed but not asserted.

**Concrete failure scenario:** keep `requirements-min.in` at pandas 2.1.0 and
NumPy 1.24.0, then regenerate or replace the lock with valid hashes for newer
compatible versions. The dependency test still sees the declared floors in
the input, the structural validator accepts the well-formed lock, and the job
installs and tests the newer versions. A regression against the advertised
floors can merge while the “minimums” job is green. A scratch stale-lock
mutation passed both current controls.

The network-none wheel handoff itself holds: this job no longer executes a
project build hook on the hosted runner.

**Required repair:** compare the direct pins and relevant markers in the
installed lock to `requirements-min.in`, or assert the installed distribution
versions before tests (preferably both), and add a mutation that changes only
the lock. The job must fail before pytest when either direct floor differs.

### P1-R2-F9 — Blocker — the supported institutional procedure is still not closed

**Location:** `README.md:186-200`; `SECURITY.md:213-226`;
`.github/workflows/ci.yml:571-592, 748-762`.

README calls the procedure no-index, but its runtime-closure command is only
`pip install --require-hashes -r requirements-install.lock`; it supplies
neither `--no-index` nor the local wheelhouse that CI uses. It then tells the
reader they may build the project with plain `python -m build`. That command
uses an isolated PEP 517 environment and resolves the backend outside the
runtime lock. SECURITY says CI exercises exactly the documented procedure,
but CI uses a pre-populated wheelhouse, `--no-index --find-links`, a separately
hash-locked build environment, `--no-isolation`, and a network-none container.

**Concrete failure scenario:** follow README in a fresh institutional
environment. The first command announces and consults an index; with no
network and no pre-positioned wheelhouse it cannot install NumPy. Follow the
offered self-build route under `PIP_NO_INDEX=1`: an actual probe attempted to
install Hatchling into the isolated build environment and failed. On a
connected machine the same route downloads and executes that backend without
the hashes in `requirements-install.lock`. Thus the path is neither the
air-gapped procedure described nor the one CI proves.

**Required repair:** publish one complete, copyable wheelhouse-plus-wheel
procedure using the same `--no-index --find-links --require-hashes` and
`--no-deps` boundaries as CI, including how the governed artifacts arrive in
the environment. Remove plain self-build from that supported path, or specify
and exercise the separately locked, network-none build closure. Make CI invoke
the documented commands from a shared script or otherwise compare them
mechanically.

## Major items

### P1-R2-F10 — Major — the new `localpath` origin bypasses callback-slot checks

**Location:** `tools/offline_scan/scan_imports.py:549-558, 657,
2002-2015, 2100-2123`.

Method checking accepts `localpath` as a safe API-like receiver, but
`_callee_slot_identities` creates `pathlib.Path.<method>` identities only for
an `instance` origin. The new origin therefore loses the Path callback table.

**Concrete failure scenario:** validate a path, then call
`validated.walk(on_error=callback)` where `callback` is a function parameter.
The mutation scans with zero violations. On Python 3.12+ a walk error invokes
the caller-supplied callback, despite the scanner's standing rule and explicit
`pathlib.Path.walk.on_error` slot. The boundary impact remains within the
documented caller-code residual, so this is Major rather than Blocker, but it
is a repair-induced control regression.

**Required repair:** preserve the `pathlib.Path` callee identity alongside
locality provenance, or teach callback-slot resolution that `localpath` is a
Path receiver. Add keyword and positional red tests on 3.12+ and prove the
callback is not invoked after a green scan.

### P1-R2-F11 — Major — the two writes are still not one outcome

**Location:** `src/synthtwin/profile.py:241-301`;
`tests/test_cli_profile.py:158-193`.

The first write has no cleanup path when it fails after creating/truncating a
target. When the second write fails, only a newly created first target is
removed; the partial second target is never removed, and an existing first
target has already been irreversibly replaced. The directory test exercises
preflight, not a mid-write failure.

**Concrete failure scenario 1:** under a 256-byte file-size limit, make the
first JSON write fail. The CLI exits 1 and leaves a new 256-byte partial JSON
file. Under a 2100-byte limit, the full JSON succeeds and the summary fails;
the cleanup removes JSON but leaves a 2100-byte partial summary. The error
mentions cleanup of the first path, not the surviving second artifact.

**Concrete failure scenario 2:** start with an existing profile, then make the
summary write fail. The old profile is replaced by the new one and left in
place; there is no rollback to the pre-run state. Therefore neither “leave
neither” nor “one outcome” is true.

**Required repair:** fully write and flush validated same-directory temporary
regular files before committing either target; define rollback for failures
during both commits, including restoration of existing files; and report every
leftover if rollback itself fails. Exercise real partial first/second writes,
existing targets, cleanup failure, and output aliases.

### P1-R2-F12 — Major — the plan and security record still authorize the old surface

**Location:** `docs/plans/phase-1-profiler.md:55-120, 370-449, 460-512,
542-555`; `tools/offline_scan/scan_imports.py:235-276`;
`src/synthtwin/reading.py:38-45`; `README.md:135-145`;
`SECURITY.md:105-122, 162-175`.

The response says the NumPy owner decision is partially superseded and awaits
confirmation, and says the Path-object fence claim was withdrawn. The amended
plan still directs pandas and NumPy, says the scanner enumerates NumPy,
authorizes `numpy.errstate` as accepting only string keywords, and treats the
Path wrapping as a fence layer. The actual scanner instead bans NumPy and
adds `math.fsum`, `frexp`, `isfinite`, `ldexp`, and `sqrt`; that math surface
has no amended plan-level capability decision. P1-D11 additionally promises
machine-independence beyond D12's same-platform/tested-matrix scope.

**Concrete failure scenario:** a maintainer follows still-current P1-D10 E2
and restores the enumerated NumPy surface, including
`numpy.errstate(call=...)`, believing the already-ratified capability audit
says it takes no callable. That reopens caller-code execution without a new
plan decision. Conversely, the current math API surface can change under code
review without the D6.2 plan-level authorization the project requires. This is
not cosmetic drift: the contradictory plan is the authorization boundary for
future scanner changes.

**Required repair:** obtain and record the owner decision; amend P1-D2,
P1-D2.1, P1-D8, P1-D10, P1-D11, acceptance criteria, README, SECURITY, and
scanner/reader audit text to one capability inventory and one D12-compatible
determinism scope. The plan must name the actual fenced provenance rule after
P1-R2-F1 is fixed and enumerate/audit the exact math surface before code is
accepted.

### P1-R2-F13 — Major — the required case-variant header warning is absent

**Location:** `docs/plans/phase-1-profiler.md:166-171`;
`src/synthtwin/reading.py:214-236`; `src/synthtwin/profile.py:57-139`;
`src/synthtwin/summary.py:238-284`.

P1-D3 accepts case-variant column names only with a summary warning.
`_check_header` detects exact duplicates and no later layer records a folded
collision.

**Concrete failure scenario:** profile a real CSV headed `Age,age` with 19
data rows. The CLI exits 0, JSON carries two fields, and the summary contains
neither a collision nor ambiguity warning. A later case-insensitive consumer
can collapse the two names or select the wrong field without the promised
notice.

**Required repair:** define the exact normalization used for this warning,
carry collisions as structured profile evidence, render them visibly in the
summary, and test the real CLI with case-only and Unicode variants. Exact
duplicates must remain refusals.

### P1-R2-F14 — Major — table-controlled terminal instructions reach the disclosure

**Location:** `src/synthtwin/reading.py:184-236`;
`src/synthtwin/summary.py:95-122, 175-284`;
`src/synthtwin/cli.py:227-247`.

Header names and published labels are interpolated into the human summary
without refusing or visibly escaping control characters. JSON escaping is
safe, but the same summary is printed before writes and saved as text.

**Concrete failure scenario:** a CSV headed with the bytes
`lab\x1b[2Jname` followed by eleven identical values is accepted and the CLI
exits 0. The raw `ESC [ 2 J` sequence appears in both captured stdout and the
written summary. On a normal ANSI terminal it clears the screen after the
mandatory disclosure has been printed, hiding the very notice that must
precede creation of the files. A quoted header containing a newline can
similarly inject a fake section or `Written:` line.

**Required repair:** reject control characters in schema names and published
labels, or render them with an unambiguous visible escaping function at every
human-facing sink, including errors and disclosure. Add byte-level stdout and
summary tests for C0/C1 controls, escape, carriage return, newline, bidi
controls, and ordinary non-ASCII text.

## Round-1 items intentionally left open

P1-R1-F4, F5, F7, F8, F9, the remainder of F10, the format-spec half of
F13, F15, F16, F17, F18, and R1-X3 remain open exactly as the response says.
I did not reproduce or count them in this round. P1-R2-F12 covers the
conflicting NumPy authorization that also touches the other half of
P1-R1-F13.

## What held under attack

- The Phase 1 tree is staged and therefore inside the tracked-file
  decontamination scope. The clean result is no longer a Phase 0-only result.
- The current `_read_columns` call revalidates immediately before the direct
  reader call. Module-qualified direct URL, module-qualified callback, stored
  attribute, and bare-Path mutations go red; the intended direct call goes
  green.
- Two-positional-argument `typing.cast`, direct pandas methods, and direct
  unenumerated pandas attributes go red. `global` and `nonlocal` nodes are
  refused. NumPy is absent from `src/`, is rejected as an import, and the
  listed math surface is closed against unlisted math names.
- Independent checking found all current reference float candidates correct;
  rebuilding produced identical bytes, and the examined statistics stayed
  unchanged when rows were reordered. The host also produced the intended
  flag for an unrepresentable spread. These limited passes do not establish
  correctness beyond the frozen cases.
- Exact output targets re-enter the locality validator, a directory at either
  target is refused before writes, a POSIX symlink to the source is refused,
  and the normal disclosure text is emitted before file creation.
- The absent-column override is refused before construction/writes. The
  minimums job uses the network-none-built wheel rather than running a source
  build hook on its networked runner.

## Verification and attack coverage

The complete baseline check set passed before this review file existed and
again with the review staged in the index:

- `pytest -q`: 582 passed, 4 skipped;
- offline source scan: 9 files, 0 violations;
- decontamination: clean over the staged/tracked Phase 1 tree, including this
  artifact;
- signed attestation: signature, shape, scanner tree, manifest, bindings, and
  counts verified;
- provenance: the committed fixtures regenerated and byte-compared;
- supply-chain validation: the development, minimum, and institutional
  lock/input pairs passed their structural rules;
- Ruff: passed;
- mypy: 9 source files passed;
- staged diff whitespace check: passed.

Targeted checks added to the review work, all outside the repository:

- Scanner: import styles/aliases, direct/stored/callback references,
  cross-function/module/class provenance, validator shadowing, positional and
  keyword casts, class and pattern scopes, containers/destructuring,
  subscripts, conditional/Boolean/walrus targets, pandas-derived and
  NumPy-derived capabilities, Path callbacks, and math/NumPy allowlist
  mutations. The repository's 70 scanner tests pass; five independent green
  mutations above reached their prohibited runtime behavior.
- Numeric: exact rational checking of all 218 committed float candidates;
  regeneration digest and byte equality; high/low range refusal; n=1/n=2,
  zero and subnormal spread, near-overflow, unrepresentable spread,
  cancellation, every permutation of the three-value counterexample, and
  random translated/scaled/dynamic-range stress for mean, standard deviation,
  skewness, and quantiles. The 205 targeted repository tests pass.
- I/O: default and explicit output paths; directories, POSIX symlinks, hard
  links, FIFOs, existing/new targets; first- and second-write partial failure;
  cleanup, replacement, disclosure/error order, and absent overrides. The 46
  targeted tests pass despite the independent failures above.
- Supply chain: all requirement inputs/locks, declared floors, lock/input
  drift, minimum-job artifact flow, network-none build, fresh-wheel smoke, and
  README commands in clean temporary environments with/without an index.
- Untouched product surfaces: direct numeric parsing and full CLI runs for
  signed accounting notation, case-variant headers, and terminal controls;
  profile JSON and summary bytes were inspected separately.

The checked properties were: the offline/no-capability boundary; scanner
soundness for the newly claimed fence and origin lattice; numeric accuracy,
range honesty, row-order and platform scope; independent-oracle validity;
input/output locality, identity, non-destruction, disclosure, and transaction
behavior; exact minimum-version testing; and equality between the documented
and exercised institutional install. Attack classes included aliasing,
shadowing, scope mismatch, value-preserving syntax, computed calls, derived
objects, boundary floats, cancellation, subnormals, midpoint ties, special
filesystem nodes, partial writes, stale but valid locks, isolated builds, and
data-controlled terminal text.

## Cosmetic observations not counted as items

The numeric prose calls `x*x` and `math.sqrt` “exact to the last bit”; the
useful term is correctly rounded. That wording does not create a separate
finding because the actual accuracy failures are P1-R2-F4.

The generator's `ladder_binary_p` branch models exact multiplication by the
binary rational for `p`, not the separately rounded Python multiplication it
says it compares. At `n=101`, Python computes `100 * 0.99` as `99.0` while
the branch records the exact product just below 99. The authoritative
exact-probability ladder and current final float happen to agree, so this is a
stale comparison branch, not another blocker.

## Verdict

**Verdict: reject.** Blocking items: P1-R2-F1 through P1-R2-F9. Repair those,
then re-run the still-open round-1 work and all round-2 red mutations before
asking for ratification.

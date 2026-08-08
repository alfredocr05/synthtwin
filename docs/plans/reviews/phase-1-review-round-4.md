# Phase 1 combined plan-and-code review — round 4

**Reviewed baseline:** the staged Phase 1 tree above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`, including the round-3
response, the amended Phase 1 plan, product and test code, the offline
scanner, public documentation, workflow, dependency inputs, and all three
locks.

**New item count:** 5 — 3 blockers and 2 majors. Previously admitted-open
items are listed separately and are not counted again.

The direct production call in `reading._read_columns` does revalidate its
raw path, and a direct web address is refused. That useful fact does not
settle the disputed question. The two examples below pass the checker but
continue beyond the real validator and either read a different resource or overwrite
the input table. The requested ruling is therefore **option (b)**.

Three of the five repair groups fail under neighboring states. Numeric
classification is still split across incompatible populations, absent output
aliases still merge on a case-insensitive filesystem, and display controls
still reach both summaries and refusals. The call-target grammar and the
current removal of numpy as an installation root hold. The latter lacks the
regression guard its own input file says exists.

## Review items

### [BLOCKER] P1-R4-F1 — runtime path revalidation does not resolve the origin-tracking items

**Location:** `src/synthtwin/reading.py:321-355`;
`tools/offline_scan/scan_imports.py:1389-1481, 1950-1963, 2034-2108`;
`docs/plans/phase-1-profiler.md:112-147`; `SECURITY.md:105-122`.

The response is right about the current ordinary path: `_read_columns`
calls the real `validate_local_path` at line 335 and then calls
`pandas.read_csv`. The test using a direct web address raises
`PathValidationError`.

It is wrong that every route in P1-R3-F1 and P1-R3-F2 ends at that control.
The following two mutations both scanned with zero violations and then ran:

```python
# F1: the validator checks selected.csv; the reader opens other.csv by URL.
import pandas
from pathlib import Path
from synthtwin.paths import validate_local_path

def Path(raw):
    return "file:///tmp/other.csv"

def fetch(raw_path):
    validated = validate_local_path(raw_path, purpose="input")
    return pandas.read_csv(Path(validated))
```

The real validator accepted `/tmp/selected.csv`; pandas returned the rows of
`/tmp/other.csv`. The shadowed wrapper changes the value after validation and
before the fenced call. This is an actual read through a URL-form argument,
not only a quiet scan.

```python
# F2: the real input is validated and read, then a shadowed cast launders
# the frame to the writer that replaces the input.
import pathlib
import pandas
from typing import cast
from synthtwin.paths import validate_local_path

def cast(typ, val):
    return typ

def damage(raw_path):
    validated = validate_local_path(raw_path, purpose="input")
    frame = pandas.read_csv(pathlib.Path(validated))
    disguised = cast(frame, pathlib.Path(validated))
    disguised.to_csv(raw_path)
```

The scanner again reported zero violations. At run time the real validator
ran, but `damage.csv` changed from:

```text
secret_value
3
4
```

to:

```text
,secret_value
0,3
1,4
```

Its SHA-256 changed from
`8aa8e75b86a0ad9c3d346ea3d53338d9b256fd4fd1f22f252e01c6d59b50c328`
to
`dfa28ef46d2a4033029e8a0c346e03541311b344cb050467db8879b522f00260`.
That is the user's input being damaged after the runtime locality check has
succeeded. Runtime locality cannot constrain a pandas writer.

This does not imply that the scanner must become a proof of all Python name
binding. It does mean the owner must choose the control honestly. One option
is the already documented A3 model: source review carries the boundary and
the scanner is a best-effort second layer, accepting that a clean scan alone
does not prevent either mutation. The other is a fail-closed source dialect
or a stronger machine check. The runtime recheck is not a substitute for
that choice.

The current plan and security text also overstate the chosen model. The plan
says, “What holds the line now is enforced by the scanner,” then promises
canonical validator identity, same-function provenance, direct fenced calls,
and shadow rejection. `SECURITY.md` says enumeration means a second call site
“cannot appear” and that returned pandas objects are “never called through.”
Replace those claims with: runtime revalidation controls the current direct
reader call; scanner provenance is defense in depth under A3; source review
is responsible for binding forms the scanner does not resolve and for
preventing new writer paths. This is a security-boundary correction, not
cosmetic wording.

The receiver-identity half of P1-R3-F7 is separable. Its effect is invocation
of caller-supplied code, which A3 already names. It may be downgraded to that
accepted residual if the owner records that decision and removes the stronger
slot-identity claim; the runtime path check does not answer it.

### [BLOCKER] P1-R4-F2 — the combined numeric population still splits at sentinel and role boundaries

**Location:** `src/synthtwin/taxonomy.py:368-428, 565-607, 686-721,
879-933`; `src/synthtwin/parsing.py:364-442`;
`docs/plans/phase-1-profiler.md:543-569`.

The new four-way cell classification exists, and both new counts are present
on every column block. The population is not carried through every later
decision.

**Concrete failure scenario 1:** profile `1` through `199`, one `-999`, and
one `1e999`. There are 201 present cells, so the sentinel appears in less
than the plan's 0.5% of present values and must remain data. Sentinel code
uses only the 200 representable numbers as its denominator, removes `-999`,
and publishes a count column with minimum 1 and mean 100. The conservative
outcome would retain the negative value: continuous, minimum -999, mean
94.505 over the representable values. Because `numeric_looking` is not
updated after removal, the summary also says `-1 value(s)` are not numbers.

**Concrete failure scenario 2:** `1` through `99` plus `-1e999` is still
called a nonnegative count and reports `n_negative: 0`. The lexical sign of
the out-of-range number was discarded even though it is sufficient to rule
out the count role.

**Concrete failure scenario 3:** one hundred distinct out-of-range numbers
become `free_text`; three repeated out-of-range spellings become categorical
and are published as labels. The summary can say both that none of the values
read as numbers and that every value is a number counted in deciding the
role. The final numeric branch still requires at least one representable
number, so the combined population did not decide the role.

The narrow P1-R3-F4 repair holds for distinct `(-1)` through `(-100)`: no sign
is reversed, `n_contradictory` is 100, and the remark is actionable. Repeated
contradictory spellings can still take constant, binary, or categorical roles
instead of a defined declined-numeric outcome.

**Required repair:** carry one structured record per cell through sentinel
normalization; use all present cells for the specified sentinel denominator;
gate on the combined numeric-looking population; recompute every population
after normalization; preserve decidable sign and integer evidence; and add
the cases above as profile/CLI regressions. The owner must choose an explicit
refusal, a limited numeric role, or an amended contract for a numeric-intent
column with no representable values.

### [BLOCKER] P1-R4-F3 — absent output identity still fails on filesystem-equivalent names

**Location:** `src/synthtwin/profile.py:188-244, 298-342`;
`src/synthtwin/cli.py:211-230`.

Resolved-path equality catches exact absent aliases, and `samefile` catches
existing hard links. It cannot decide filesystem equivalence for two absent
names.

**Concrete failure scenario:** on this supported, case-insensitive macOS
filesystem, create these dangling links before running the CLI:

```text
clinic-profile.json -> FutureTarget
clinic-profile.txt  -> futuretarget
```

Both targets are absent. Their resolved path strings differ by case, each
`exists()` call is false, and `is_the_same_file` returns false. The CLI exits
zero. The first write creates the target; the second spelling then identifies
the same inode and overwrites the JSON with the human summary. Both advertised
output names contain summary text and there is no machine-readable profile.
No timing window or separate local actor is involved.

The “any metadata error” claim is also incomplete. `resolve()` and
`samefile()` errors fail closed, but an `OSError` from either `exists()` call
escapes the helper and then the CLI as a traceback.

**Required repair:** handle case- and normalization-equivalent absent names
according to the destination filesystem, or recheck identity after the first
target exists and before the second commit as part of a transactional write.
Catch every metadata-query failure and turn it into a fail-closed,
plain-language refusal. Keep exact dangling aliases, case/normalization
aliases, hard links, and injected failures as regressions.

### [MAJOR] P1-R4-F4 — display escaping still omits controls and bypasses some refusal sinks

**Location:** `src/synthtwin/parsing.py:99-148`;
`src/synthtwin/errors.py:46-75, 87-142, 196-309`;
`src/synthtwin/summary.py:54-56, 95-172, 175-235`.

The C0/C1/DEL, U+2028/U+2029, and listed directional controls are escaped,
and ordinary printable non-ASCII text is preserved. The claimed control set
is not complete.

**Concrete failure scenario 1:** U+061C ARABIC LETTER MARK is a Unicode bidi
control but `visible()` returns it unchanged. A header containing it reached
CLI stdout, the written summary, and the duplicate-header refusal raw.
U+200B ZERO WIDTH SPACE, U+2060 WORD JOINER, and U+206A INHIBIT SYMMETRIC
SWAPPING also survive unchanged as format controls.

**Concrete failure scenario 2:** refusal builders pass paths directly rather
than through `_shown`. A missing local filename containing raw ESC followed by
`[2J` reached stderr unchanged, so it can clear the terminal even though
`visible()` knows how to escape ESC.

**Required repair:** define the complete promised bidi/format-control set and
test it mechanically; pass every untrusted string headed to stdout, stderr,
or the written summary through the same boundary, including paths and library
details. Add end-to-end bytes tests for ordinary non-ASCII text and for every
control class.

### [MAJOR] P1-R4-F5 — numpy is no longer an install root, but the promised root guard is absent

**Location:** `requirements-install.in:1-11`;
`tests/test_dependencies.py:14-19, 102-167`;
`tools/supply_chain/validate_lock.py:250-295`.

The current F8 artifact is correct: `requirements-install.in` has pandas as
its sole root, and the lock records numpy only through pandas. The repair's
behavior therefore holds today.

The input file says `tests/test_dependencies.py` fails if its roots drift.
That test never reads `requirements-install.in`; it compares project metadata
with the development input and only checks that the install lock contains the
runtime closure. The structural validator checks syntax, not root equality.

**Concrete failure scenario:** add numpy back to `requirements-install.in`
and regenerate the lock. The install continues to name numpy as a direct
root, even if a future pandas no longer requires it, while the current
dependency tests and all three structural lock checks remain green.

**Required repair:** parse the direct roots of every runtime input and assert
they equal the authorized project-metadata roots, with a mutation that adds
only an extra install root. This is a bounded missing control, not a current
dependency-behavior failure.

## Disposition of the round-3 repair groups

| Repair group | Round-4 disposition |
| --- | --- |
| P1-R3-F1/F2 and receiver identity | **Option (b).** The current direct read is revalidated, but scan-clean mutations read a different URL-form resource and damage the input after that validation. F1/F2 do not close on the response's rationale. Receiver identity may be accepted only as the explicitly documented A3 caller-code residual, not as runtime-fence coverage. |
| P1-R3-F3/F4 | **Fails overall.** Counts are universal and the original sign reversal is gone, but sentinel populations, sign evidence, and no-representable role routing remain contradictory (P1-R4-F2). |
| P1-R3-F5 | **Fails.** Exact aliases and existing hard links hold; absent case-equivalent aliases merge after the check and destroy one output (P1-R4-F3). |
| P1-R3-F9 | **Fails.** Several controls and path-bearing refusal sinks remain raw (P1-R4-F4). |
| P1-R3-F8 | **Current artifact holds.** Numpy is transitive, not a root. The advertised regression guard is missing (P1-R4-F5). |
| P1-R3-F7 call-target half | **Holds under the examined shapes.** Function targets are name/attribute only; conditional, Boolean, walrus, subscript, call-result, awaited, and comparison targets are refused. Accepted method-receiver syntax matches the documented name/attribute/call/literal/subscript/f-string grammar; origin and callback-slot checks still apply afterward. |

## Previously admitted-open items

These remain open; the user requested only a one-line standing record for
each. P1-R2-F4/F5 were rerun in this round; the others were checked for
obvious accidental closure but not re-derived from scratch.

| Item | Standing state and concrete consequence |
| --- | --- |
| P1-R3-F6 — Blocker | Replacing the project wheel leaves every dependency hash valid and installs substituted project code; the documented cross-machine bundle also omits a governed project digest and target-complete acquisition. |
| P1-R2-F4 — Blocker | `[-max, 1, max]` still publishes a mean five representable steps from the exact-rounded result, `1e-16` is erased in the corresponding cancellation case, and the subnormal median misses half-even rounding. |
| P1-R2-F5 — Blocker | The generator still rounds a subnormal tie downward, can return a negative standard deviation at zero, and labels truncated decimals exact, so it cannot be frozen as the numeric oracle. |
| P1-R2-F11 — Major | A partial first or second write can leave incomplete output or replace an existing profile without rollback; the two files are not one transaction. |
| P1-R2-F13 — Major | `Age,age` is accepted with no promised warning, so a later case-insensitive consumer can collapse or select the wrong column. |
| P1-R1-F4 and R1-X3 — Blocker | Equal row/column counts still allow the two readers to accept different values or move a value between columns while the profile looks ordinary. |
| P1-R1-F5 — Blocker | A headerless `P001,34`-style table still consumes its first record as schema and publishes it as a column name. |
| P1-R1-F7 — Blocker | Automatic sentinel rules still delete legitimate extremes or retain real missing codes without an ambiguity state or user override. |
| P1-R1-F8 — Blocker | Realistic measurements, formatted codes, and high-cardinality categories can still take information-destroying roles with no correction in both directions. |
| P1-R1-F9 — Blocker | Different datetime or suppressed-level distributions can still serialize to the same profile, so a profile-only generator cannot preserve both. |
| P1-R1-F10 remainder — Blocker | Forced-role precedence and raw values in remarks or missing-source keys can still defeat the promised suppression boundary. |
| P1-R1-F13 format-spec half — Major | A dynamic f-string format specification can invoke caller-controlled formatting code while the scanner accepts the result as text. |
| P1-R1-F15 — Major | Peak-memory behavior and recovery advice remain inconsistent with the plan; allocation failure can still diverge from the promised bounded-memory/user-message path. |
| P1-R1-F16 — Major | Catalog “reachability” is still source-text membership rather than a real CLI trigger, so dead or jargon-bearing refusal paths can pass. |
| P1-R1-F17 — Major | `NA`, `na`, padded variants, empty cells, and whitespace-only cells are merged into canonical keys despite the promise of counts by source spelling. |
| P1-R1-F18 — Minor | A valid Latin-1 header beginning with byte `0xFF` or `0xFE` can still be mistaken for a wide-encoding marker and refused. |

## Cosmetic observations

These sentences are stale but do not affect this round's decision:

- `README.md` and `CHANGELOG.md` call pandas and numpy the first/exactly two
  runtime dependencies and say both are scanner APIs. Pandas is the only
  direct dependency; numpy is transitive and source imports it nowhere.
- `requirements-min.in` says “two runtime pins” although it has one runtime
  pin plus pytest.
- `SECURITY.md` still tells an auditor to confirm `dependencies = []`.

They should be corrected, but they are cosmetic. The scanner/runtime claims
in P1-R4-F1 are not cosmetic because they assign responsibility to the wrong
security control.

## Verification and attack coverage

The staged baseline before this report was written passed:

```text
.venv/bin/python -m pytest -q
  595 passed, 4 skipped

.venv/bin/python tools/offline_scan/scan_imports.py src
  9 files, 0 violations

.venv/bin/python tools/decontamination/check.py
  clean

.venv/bin/python tools/decontamination/verify_attestation.py
  verified

.venv/bin/python tools/provenance/check_provenance.py
  passed

.venv/bin/python tools/supply_chain/validate_lock.py
  dev input/lock passed

explicit dev, install, and minimum input/lock checks
  all passed

.venv/bin/python -m ruff check .
  passed

.venv/bin/python -m mypy src
  9 source files passed

focused scanner, parsing, taxonomy, numeric-reference, profile, CLI,
summary/property, and dependency tests
  341 passed
```

The reference generator rebuilt the committed vector file byte-for-byte.
That proves provenance and reproducibility, not the mathematical validity
that P1-R2-F5 disputes.

Targeted work covered direct and shadowed validator/wrapper/cast bindings;
actual URL-form reading and writer execution; accepted and refused call-target
and receiver shapes; representable, out-of-range, contradictory, signed, and
text populations; sentinel denominator and gate neighbors; post-normalization
counts; exact/dangling/hard-link/case-equivalent output identity; metadata
failure; C0/C1/DEL, Unicode line, bidi and format controls; stdout, stderr,
written-summary and refusal sinks; direct dependency roots, transitive lock
annotations, markers and all lock consumers; oracle midpoint, zero, maximum
neighbor, decimal-rendering and bit-distance behavior.

The examined properties were runtime locality at the actual value handed to
the reader, non-destruction of the input, scanner-claim honesty, single-outcome
type routing, numeric accuracy/oracle independence, output identity and
recoverability, safe human display, dependency-root authorization,
determinism, profile/generator separation, refusal reachability, and plan/code
consistency. The source surfaces reviewed were all files under
`src/synthtwin/`, the relevant tests, `tools/offline_scan/scan_imports.py`,
the reference and lock validators, the Phase 1 plan, README, SECURITY,
CHANGELOG, project metadata, workflow, inputs, and locks.

This host is macOS on a case-insensitive filesystem. The case-alias failure
was exercised end to end. Windows reparse behavior was not independently run
outside the repository's platform-mocked/skipped tests. No actual second
air-gapped host or published release artifact exists to test P1-R3-F6.

## Ordered path to ratification

1. **Stop current loss/corruption paths.** Repair P1-R4-F3 together with the
   transactional work in P1-R2-F11; retain the exact, hard-link,
   case/normalization, metadata-failure, partial-write, and rollback cases.
2. **Make the numeric oracle valid before changing numeric implementation.**
   Repair P1-R2-F5's half-even, zero, maximum-neighbor, full-decimal and
   bit-distance logic; independently review and freeze the new vectors. Then
   repair P1-R2-F4 and P1-R4-F2 against that oracle.
3. **Close the remaining silent type/profile blockers.** Resolve P1-R1-F4/F5,
   P1-R1-F7/F8/F9, P1-R1-F10 and R1-X3 with end-to-end collision, ambiguity,
   suppression, and reader-agreement tests.
4. **Finish the security and display controls.** Record the owner's A3 choice
   described below, align the plan/SECURITY/scanner claims, close P1-R4-F4,
   and add the bounded install-root assertion in P1-R4-F5.
5. **Close the remaining majors and minor.** P1-R2-F13, P1-R1-F13's
   format-spec half, P1-R1-F15/F16/F17, and P1-R1-F18 need their already
   specified runtime regressions or explicit plan amendments.
6. **Resolve the release-install claim.** Before calling the institutional
   path built, publish and verify a governed project-wheel digest and a
   target-complete transferable bundle, or mark that path planned until a
   release exists.

The decisions that belong to the project owner, rather than another narrow
patch, are:

- whether A3 means mandatory human source review plus a best-effort scanner,
  explicitly accepting that a clean scan alone misses the two runnable
  mutations above, or whether product source must obey a fail-closed dialect;
- whether numeric intent with no usable number is a refusal, a limited numeric
  schema role, or a documented fidelity loss, and whether the subnormal
  tolerance/machine-independence claims are narrowed;
- confirmation that numpy's direct-dependency authorization is withdrawn for
  Phase 1; and
- whether the institutional install remains planned until a release supplies
  the governed wheel digest, or Phase 1 must produce that artifact now.

## Verdict

**Verdict: reject.** Blocking round-4 items are P1-R4-F1, P1-R4-F2, and
P1-R4-F3. They join P1-R3-F6, P1-R2-F4, P1-R2-F5, P1-R1-F4,
P1-R1-F5, P1-R1-F7, P1-R1-F8, P1-R1-F9, and the remainder of
P1-R1-F10; R1-X3 remains a blocking member of P1-R1-F4.

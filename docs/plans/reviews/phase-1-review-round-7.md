# Phase 1 combined plan-and-code review — round 7

**Reviewed baseline:** `a5e1b4562812760108197bcb8a56b4643f6fd422`,
the three Phase 1 commits above
`002bca35ce1562e1afe39b4d9987fa617a04ee38`. I reviewed revision 3 of
the plan, the round-1 through round-6 record, all changed product and test
code, the offline scanner, the numeric reference generator and grader, the
dependency and provenance controls, and the public documentation.

**New item count:** 4 blockers and 2 minors. The minors are explicitly
documentation-only. They belong in the residual record under the owner's
instruction; they are not named as reasons for rejection.

The twelve round-6 answers made substantial progress. The named overflow,
signed-zero, ladder, grading, staging-name, cleanup-report, first-row,
taxonomy, identifier, and declaration cases now behave as described. The
current numeric fixture is unchanged and independently survived the revised
grading checks. Four adjacent cases nevertheless still cross the project's
substantive lines: a failed write can leave an undisclosed data-derived
working file, suppressed source text is serialized in settings, distinct
numeric declarations collapse onto one binary64 value, and an integer-valued
`float64` field bypasses the finished-document proof.

## Explicit ruling on residual R2: (b)

**The residual understates the limit.** Attribute reads are not the one
remaining implicit-dispatch class. This scanner also accepts these operations
on a value it cannot trace:

```python
def probe(value):
    value[0]          # __getitem__
    value + 1         # __add__ / reflected arithmetic
    value == 1        # __eq__
    bool(value)       # __bool__ or __len__
    list(value)       # __iter__ / __next__
    f"{value}"         # __format__

    class Made(value):
        pass          # __mro_entries__ and class/metaclass construction
```

That complete file produced zero scanner violations. These forms can execute
code belonging to a caller-supplied object without a method-call expression,
just as a property read can. The scanner's own statement at
`tools/offline_scan/scan_imports.py:477-482` that every other accepted built-in
“takes data ... and never invokes an argument it is handed” is therefore
false: iteration, conversion, length/truth, formatting, comparison, hashing,
and similar protocol operations are calls in everything but syntax.

**Does that let the current reader read a non-local path at run time, within
synthtwin's own-code boundary and absent caller/same-process mutation? No.**
There is one `pandas.read_csv` call, at `src/synthtwin/reading.py:1062-1083`.
Its argument is the `pathlib.Path` wrapping of the value returned by
`validate_local_path` immediately above it. The position-blind origin claim
itself held: direct URL, UNC, device-path, unproved-path, late module
rebinding, and class-timing mutations were refused, and the URL/UNC run-time
probes reached no pandas call. Caller-supplied protocol hooks can themselves
perform network I/O or mutate the reader, but that is the caller/process
authority A3 expressly excludes; the admitted syntax does not provide an
in-tree route around the reader's immediate validator. As Phase 0 A3 says, a
reading-only analysis could refuse all unresolved forms; this scanner
deliberately does not. The run-time validator, not a claim of static closure,
is the operative non-local-read control.

This is a documentation-only ruling. P1-R7-F5 below gives exact replacement
scope for the residual and the neighboring overclaims.

## Group 1 — substantive behavior

These items leave or publish real-derived material, silently misclassify
values, or let an unproved number be certified. None is a wording-only item.

### [BLOCKER] P1-R7-F1 — a second-write path refusal escapes the transaction and leaves the data-derived first part undisclosed

**Location:** `src/synthtwin/profile.py:437-459, 823-864, 883-943`;
`src/synthtwin/cli.py:549-560`; `docs/plans/phase-1-profiler.md:402-416`.

`write_text_file` re-runs `validate_local_path` immediately before each
working-file write. That validator raises `PathValidationError`, but the two
write handlers catch only `ProfileError`. A probe allowed the two exclusive
claims and the first immediate validation, then made the second working
file's immediate validation report a refusal. This is the resulting disk
state:

```text
exception: PathValidationError: injected refusal on second working write
final outputs: neither exists
table-profile.json.synthtwin-part-1: "PROFILE-DERIVED\n"
table-profile.txt.synthtwin-part-1:  empty
```

The cleanup/state-report path never ran. The CLI caught the path error but
named neither survivor, so a complete real-derived profile was left in a
hidden neighbor after a message that discussed only the path refusal. On
Windows, this exception has a non-hostile production route: a component
metadata check can fail because permission is refused or another program is
holding the component (`paths.py:164-211`). The transaction contract promises
honest state after every error the code can see, not only write-system-call
errors.

There is a neighboring ownership loss in the same state machine.
`_create_empty` can create a working file successfully and then receive an
uncertain answer from `_what_is_there`. It returns `("refused", ...)` without
returning the path it now owns; the caller cleans an empty inventory and can
say that nothing is left while that empty working file remains. This second
case exposes no table content by itself, but it proves that exclusive creation
and cleanup ownership are split at the wrong point.

The ordinary injected `OSError` on the second content write now behaves
correctly: working files are removed and old outputs remain. The same is true
for a second rename failure and for cleanup failures the state reporter is
actually given. Those repairs should be retained.

**Required closure:** route both `ProfileError` and `PathValidationError`
from either working-file write through the same disk-state inspection and
cleanup; preserve ownership as soon as exclusive creation succeeds, even if a
later metadata check is uncertain; and assert final-output bytes, every
working neighbor, and every named leftover for both cases above. No caught
failure may leave a data-bearing part unnamed.

### [BLOCKER] P1-R7-F2 — raw declarations in `settings` bypass value suppression

**Location:** `src/synthtwin/profile.py:72-89`;
`tests/test_p1r6f9_declared_values.py:413-431`;
`docs/plans/phase-1-profiler.md:418-431, 754-757`.

The new options are recorded verbatim in the serialized settings. That
conflicts with the still-normative rules for identifier, free-text, and
below-floor source spellings.

In an end-to-end profile of a high-cardinality narrative column, the rare
source value `withheld-token-417` was supplied as
`--missing-value withheld-token-417`. The column was correctly classified
`free_text`; its role block omitted the value and counted one declared
missing cell. Nevertheless the JSON contained:

```json
"declared_missing_values": [
  "withheld-token-417"
]
```

The summary did not disclose that this source value would be emitted. The
same path can expose a value from a column explicitly declared as an
identifier. It also defeats small-cell suppression: with 99 `common` cells
and one `rare-label`, `--missing-value rare-label` withholds the spelling from
`missing_by_source` but republishes it in `settings`. The existing regression
checks that the file spelling
`-9.99e2` is absent while the setting records the equivalent declaration
`-999`; it therefore does not inspect the raw setting that crossed the
boundary.

This is not resolved by saying that the operator typed the value. The test
suite itself correctly states that a declaration is still a real table value
and must obey the publication rule. The round-6/current requirement to carry
the raw declaration and D6's suppression claims cannot both hold.

**Required closure:** make the disclosure battery cover the complete
serialized document, including `settings`, using the exact declared spelling.
Do not serialize a declaration spelling that occurs in any source cell whose
spelling is otherwise suppressed, including identifier, free-text, and
below-floor values; retain auditable non-value metadata such as the option
count and matching rule instead. If the owner instead chooses raw declaration
publication, the privacy contract and pre-write disclosure would need an
explicit owner amendment; the current guarantees cannot remain.

### [BLOCKER] P1-R7-F3 — declaration matching uses rounded binary64 equality instead of exact numeric equality

**Location:** `src/synthtwin/taxonomy.py:1208-1252, 1307-1315,
1362-1400`; `tests/test_p1r6f9_declared_values.py:135-218, 297-377`.

`_Declaration.value` is a `float`, and both contradiction detection and cell
matching compare that rounded value. Distinct decimal integers can therefore
be treated as the same exact number. These two declarations are falsely
reported as contradictory:

```text
--keep-value 9007199254740992
--missing-value 9007199254740993
```

Both source spellings round to the same binary64 value. In the more damaging
direction, a 40-row column containing twenty copies of each integer, profiled
with only `--missing-value 9007199254740992`, became:

```text
role = empty
n_present = 0
n_missing = 40
missing_by_class["(declared-missing)"] = 40
```

The other twenty real values were silently removed. The same class appears
with two distinct decimal fractions that round to one float. Conversely,
mathematically equal exponent spellings outside binary64 range fall back to
text comparison and need not match. Common alternative sentinel spellings
such as `-999`, `-999.00`, `-9.99e2`, and `(999)` do match as intended; the
defect is at the precision and range boundaries the ordinary cases do not
exercise.

**Required closure:** parse a declaration and each numeric source spelling
to a normalized exact numeric representation for declaration comparison,
before binary64 conversion loses information. Use that same relation for
keep/missing contradiction checks and cell removal, and add distinct-neighbor,
equivalent exponent/decimal, parenthesized-negative, and out-of-range cases.
The property to assert is mathematical equality of the source numbers, not
equality of their rounded profile values.

### [BLOCKER] P1-R7-F4 — the finished-document proof silently skips integer-valued `float64` fields

**Location:** `tools/reference/make_numeric_reference_vectors.py:484-563`;
`tests/test_oracle_proof_layer.py`; `tests/test_numeric_reference.py`.

The finished-document walker yields only objects for which
`isinstance(node, float)` is true. JSON also serializes Python integers as
numbers, so a future field or a document assignment after a local field proof
can put an integer under the explicit `float64` wrapper and bypass both the
finished-document proof and the missing-claim check. The existing
mean/std/skew/ladder constructors retain local proofs and are not this bypass.
This false field passed normally and reported that zero numbers were proved:

```python
published = {"new_statistic": {"float64": 7}}
exact = {("new_statistic",): (NEAREST, Fraction(1, 3))}
assert prove_every_published_float(published, exact) == 0
```

Changing `7` to `7.0` correctly raises because it is not nearest to `1/3`.
Thus the exact claim can itself remain unused while the generator says every
published number was proved. This is an adjacent finished-document coverage
gap, not a wrong current fixture: regeneration was byte-identical, with
SHA-256
`49807e54670e4988f485df7ef197aafd902b599814d4d928e7ff19bcf78e9e7a`,
and the named overflow, signed-zero, ladder, and adjacency mutants are now
refused.

**Required closure:** inspect every JSON numeric value (excluding booleans),
require a value below a `float64` key to have the intended Python/binary64
type, reject floating-point values outside such a field, and allow only the
explicitly enumerated integer metadata elsewhere. Also require a one-to-one
match between visited `float64` fields and exact claims, so an unused claim
cannot mask a skipped field. Keep the integer `7`/exact `1/3` document as a
mutant that must fail.

## Group 2 — documentation-only residuals

Both items in this section are wording, naming, or documentation consistency.
I found no additional data loss, publication, numeric error, or current
network path behind them. They should be logged as residuals under the
owner's instruction rather than treated as implementation repairs.

### [MINOR] P1-R7-F5 — R2 names only property dispatch while the scanner admits a broader implicit-protocol surface

**Location:** `docs/plans/phase-1-profiler.md:137-155, 503-523`;
`tools/offline_scan/scan_imports.py:11-66, 372-399, 477-482`;
`SECURITY.md:105-134`; `docs/plans/phase-0-public-skeleton.md:679-696`.

The clean constructs and run-time consequence are set out in the explicit
R2 ruling above. The residual should name unresolved **implicit protocol
dispatch**, including attribute/property access, subscription, operators and
comparisons, truth/length checks, iteration and conversion by accepted
built-ins, formatting, and class/metaclass construction. It may then state
that written method calls on unresolved receivers remain refused. Calling
attribute reads the one construct left “precisely” is too narrow.

Three neighboring sentences should be corrected at the same time:

- P1-D8.1 says Phase 0 proved “a fully closed static call-target model is
  not possible in Python.” Phase 0 expressly rejected that premise. It should
  say that **this scanner does not establish universal closure and a
  reading-only scanner could refuse all unresolved constructs; this project
  deliberately accepts the bounded caller/process residual**.
- P1-D2.1 says “What holds the line now is enforced by the scanner.” R2's
  later statement is the accurate one: the immediate run-time
  `validate_local_path` is the operative reader control and the scanner is a
  best-effort second layer.
- SECURITY.md says enumeration means “a second call site cannot appear
  without a plan-level change.” A second correctly fenced `read_csv` call
  scans clean. The accurate statement is that **no other pandas API can
  appear, and every `read_csv` call site must independently carry
  scanner-recognized provenance from `validate_local_path`**.

The concrete consequence of leaving the current wording is audit error: a
reviewer can add `list(value)` or `f"{value}"`, receive a clean scan, and
reason incorrectly that no caller code is dispatched. It does not change the
current reader-path result stated above.

### [MINOR] P1-R7-F6 — revision 3 still describes several deleted policies as current

**Location:** `docs/plans/phase-1-profiler.md:206-221, 232-238,
647-667, 729-736`; `src/synthtwin/cli.py:314-320`;
`src/synthtwin/taxonomy.py:32-53, 285-304, 1940-1956`;
`README.md:58-82, 135-143`; `SECURITY.md:238-239`; `CHANGELOG.md:10-32`.

These inconsistencies did not defeat the implementation probes, but they are
all live text rather than clearly marked history:

| area | current text | implemented revision-3 truth |
| --- | --- | --- |
| header policy | older prose promises a refusal followed by an explicit rerun choice | R1 selects the CSV default, records its decision code, and permits an operator override |
| identifier | README says the profiler “decides” record numbers and describes `--identifier` as only for a column of numbers; the D4 introduction retains an inference ordering | no value-based path reaches `identifier`; the option declares any named column |
| numeric routing | the taxonomy module says every column below 0.99 becomes free text | routing continues through the remaining ordered rules; 98 repeated numeric spellings plus two words produced `categorical` and one above-floor label |
| category ceiling | taxonomy comments and `_categorical_ceiling` say the tenth is over present values | code and revision 3 use all table rows; the 100-row/30-present/6-label case correctly received ceiling 10 |
| dependencies | README and CHANGELOG call pandas and numpy the two runtime dependencies; SECURITY's audit step says there are zero | pandas is the one direct dependency; numpy is in pandas's transitive closure and is imported nowhere in `src` |
| numeric method | P1-D11 calls sorted/`math.fsum`/power-of-two floating reduction the current algorithm and says the oracle uses `decimal` | moment statistics use exact integer power sums, the ladder uses exact rational interpolation, and the oracle explicitly removed `decimal` |

The first-row and identifier text is user-facing and should point to R1 and
the explicit-only role. The taxonomy comments should use rows and say that
role selection continues rather than promising free text below the numeric
line. The dependency and numeric-method passages should be collapsed to one
current account rather than leaving retired designs phrased as operative.

## Areas and properties examined

- **Round-6 proof repairs:** exact finite/overflow midpoint behavior on both
  signs; rational, square-root, signed-root, and zero-sign cases; every current
  ladder path; actual ordered-encoding adjacency at zero, subnormal/normal,
  and finite-range boundaries; current fixture regeneration and byte identity.
- **Write transaction:** pre-existing staging names and symlinks; input/output
  identity; first- and second-content-write failure; both rename failures;
  old-output restoration; cleanup refusal and caller propagation; immediate
  path revalidation; post-create metadata uncertainty; exact survivor bytes
  and messages.
- **Declarations:** option parsing and help; ordinary numeric alternative
  spellings; source-spelling matching for non-numbers; contradictory keep and
  missing declarations; declarations before sentinel routing; binary64
  collisions; out-of-range exponent forms; serialization and suppression.
- **Taxonomy:** the categorical ceiling over total rows on a sparse column;
  the floor and the 1,000 cap (`1,000` labels at the ceiling remained
  categorical, `1,001` became free text); exact 99/100 numeric routing;
  98/100 and 98/99 below-line routing; high-cardinality below-line free text;
  low-cardinality below-line categorical publication; removal of the
  majority, repetition, 12-value, and fixed-width-code paths.
- **Identifier:** source search and adversarial columns of unique integers,
  padded codes, unit-bearing values, and prose; only `forced_identifier`
  reaches the role, and forcing beats every publishing role.
- **First row:** ordinary named files with positive header evidence; ordinary
  text-headed files taken by disclosed convention; headerless numeric and
  text files; positive data evidence that stops and asks; explicit names/data
  overrides; row/count recovery with `--first-row data`; and forced
  structural/pandas disagreement before publication.
- **Offline/security boundary:** complete source scan; position-blind module
  and class binding mutations; fenced-reader provenance; URL, UNC, device,
  link, and unproved-path refusals; the single run-time reader call; callback,
  property, subscript, operator, conversion, formatting, and dynamic-class
  surfaces; Phase 0 A3 and public security claims.
- **Profile boundary and determinism:** free-text and identifier suppression,
  below-floor labels, settings, publication notes, source-path absence,
  canonical JSON, stable row order, and no RNG in profiling.
- **Dependency and repository controls:** direct/transitive inventory, frozen
  lock structure, provenance regeneration, decontamination, lint, typing, and
  repository state. No review probe or script was placed in the repository.

Host-specific live filesystem checks ran on macOS. The complete Windows path
and reparse-point behavior was examined through the project's platform fakes
and tests, not on a Windows host.

## Commands and results

All requested commands were run from `synthtwin`:

```text
.venv/bin/python -m pytest -q
1174 passed, 4 skipped

.venv/bin/python tools/offline_scan/scan_imports.py src
9 Python files checked, 0 violations

.venv/bin/python tools/decontamination/check.py
clean

.venv/bin/python tools/provenance/check_provenance.py
passed

.venv/bin/python tools/supply_chain/validate_lock.py
passed

.venv/bin/python -m ruff check .
passed

.venv/bin/python -m mypy src
9 source files checked, no issues
```

Focused policy, first-row, scanner, oracle, and transaction selections also
passed. Separate adversarial scripts under `/tmp` produced the concrete
failures reported above. The report was written only after the tree was
staged and the unchanged decontamination check was run, as required.

## Verdict

**Verdict: reject.** The blocking items are P1-R7-F1 (transaction cleanup and
state disclosure), P1-R7-F2 (suppressed values serialized in settings),
P1-R7-F3 (non-exact numeric declarations), and P1-R7-F4 (integer-valued
`float64` fields bypass the oracle sweep). P1-R7-F5 and P1-R7-F6 are
documentation-only residuals and are not blocking items.

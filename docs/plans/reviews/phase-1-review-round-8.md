# Phase 1 combined plan-and-code review — round 8 (final round)

**Reviewed baseline:** `c416eaa49b75ca04b309c21bbed60dfaaddd7ea5`.
I reviewed revision 4 of the Phase 1 plan, the round-1 through round-7
record and available response files, the round-7 repairs and their adjacent
cases, the public security claims, the profile-v2 producer contract, and the
repository controls named in the reviewer brief.

**New item count:** 4 blockers, 1 major, and 2 minors. P1-R8-F1 through
P1-R8-F4 are substantive: they leave data-derived files undisclosed, remove
values the user explicitly kept, allow an unproved number to be certified, or
discard generator-relevant multiplicity. P1-R8-F5 through P1-R8-F7 are
wording/specification residuals; no current data loss, value disclosure,
wrong published number, or network route was demonstrated behind them.

The repaired paths do hold in important ways. All current nonpublishing roles
kept table values out of both outputs in full-document canary and paired
noninterference probes. Ordinary exact declaration comparison distinguishes
decimal literals that round to the same binary64 value, and equivalent
spellings declared both ways are refused. The committed numeric fixture is
byte-stable, and an independent parsed-JSON traversal accounted for every
number it currently contains. The reader still revalidates immediately before
its sole `pandas.read_csv` call, and no current in-tree path around that fence
appeared in the review. Those passing cases do not cover the four failures
reported below.

## Explicit ruling on residual R2: (b)

The corrected Phase 0 premise is accurate: a reading-only scanner could
refuse every unresolved construct, and this scanner deliberately accepts a
caller/process residual so ordinary first-party code remains writable. The
narrower statement in `SECURITY.md:130-138` that no other pandas **name** may
be referenced, while pandas code still runs through implicit dispatch, is
also accurate for the current source. Immediate `validate_local_path` at
`src/synthtwin/reading.py:1053-1067` remains the operative reader control.

The combined R2 and `SECURITY.md` wording is nevertheless not accurate as
written, so the ruling is **(b)** rather than (a) or (c):

- `SECURITY.md:72-83` says the accepted surface is “named rather than
  summarized” and then names the “whole” implicit-protocol surface. A
  reading-only probe added attribute and subscription writes/deletes,
  containment and hashing, synchronous and asynchronous context management,
  awaiting, asynchronous iteration, mapping-pattern matching, generator
  delegation, and decorator application. The scanner reported zero
  violations. Most are additional data-model dispatch; decorator application
  is an additional implicit call site, not an item in the stated list. The
  accurate boundary is that permitted ordinary syntax may invoke every
  applicable Python data-model hook on an untraced value, and may contain
  other explicitly admitted implicit-call forms; any examples must be marked
  non-exhaustive.
- `SECURITY.md:81-83` says attributes of values returned by the enumerated
  libraries are themselves enumerated. Only libraries in the restricted
  instance maps receive that treatment, currently pandas. Both
  `pathlib.Path(value).open()` and a later `place.open()` scanned clean. The
  true statement is that pandas result attributes/methods are restricted;
  standard-library API instances retain the scanner's broader policy.
- `SECURITY.md:122-129` calls the validated value and its wrapping in a Path
  two operative run-time controls. The plan at P1-D2.1 and the reader's own
  docstring correctly say the Path wrapping is not an independent locality
  control. There is one operative run-time control here — immediate path
  validation — plus the best-effort source scanner.
- `docs/plans/phase-1-profiler.md:189-193` still says “no OTHER pandas API can
  appear at all.” The true claim is the repaired SECURITY wording: no other
  pandas **name** can appear in executable source, while pandas APIs may run
  through accepted implicit dispatch.
- `tools/offline_scan/scan_imports.py:29-49,477-482` still describes unknown
  attribute reads as the admitted construct and claims most accepted
  built-ins never invoke an argument. Length, truth, iteration, conversion,
  formatting, and hashing directly disprove that sentence.

These are claim-boundary errors, not a demonstrated current network path. The
single pandas call, its per-call provenance, URL/UNC/device refusals, and the
pandas result method/attribute restriction all held under inspection.

## Group 1 — substantive behavior

### [BLOCKER] P1-R8-F1 — `_commit` starts and partly builds its failure handler after data-bearing working files already exist

**Location:** `src/synthtwin/profile.py:1102-1201,1398-1619`;
`docs/plans/phase-1-profiler.md:505-537`.

The plan says `_commit` opens its guard on its first line and accepts one
bytecode boundary between the caller's handler and that guard. It does not.
`progress = _Progress()` at line 1139 executes before the `try`. A single
injected `MemoryError` there left both complete working files on disk and left
`DiskState.sentence` empty:

```text
exception=MemoryError: injected at _commit entry
clinic-profile.json.synthtwin-part-1: PROFILE-DERIVED
clinic-profile.txt.synthtwin-part-1:  SUMMARY-DERIVED
state=''
```

The next setup lines are inside the `try`, but the handler uses `target`,
`summary_target`, `new_profile`, `new_summary`, and `both` before each is
guaranteed to have been assigned. Stops at lines 1141-1147 therefore replaced
the injected failure with `UnboundLocalError`, left both parts, and still
reported no disk state. This loses the original exception and leaves complete
real-derived artifacts unnamed.

The claimed residual is not the only adjacent gap. `except ProfileError:
raise` treats the exception's type as proof that cleanup was already composed;
an unexpected package `ProfileError` from the first rename left both parts and
empty state, while eleven other injected exception classes reached cleanup.
A second interruption during cleanup can replace the original and leave parts
unnamed. Opcode injection also found post-commit return boundaries where the
new pair is already installed but an interrupt reports failure with no state.
Those nested and post-commit cases must either be covered or named as
residuals; they are not the stated caller-to-handler boundary.

**Required closure:** activate the handler before `_Progress()` and make its
cleanup inventory derive safely from already-bound arguments, not partially
initialized locals. Distinguish a transaction-composed `ProfileError` from an
unexpected one. Regression-test `MemoryError`, `KeyboardInterrupt`, and
`SystemExit` at the prologue and every setup assignment, preserving the
original exception and proving that every surviving working file is named.
Then state the actual bounds for nested cleanup failure and post-commit
interruption rather than retaining “one bytecode boundary” as the whole
residual.

### [BLOCKER] P1-R8-F2 — exact declaration matching is lost again inside numeric-sentinel detection and removal

**Location:** `src/synthtwin/taxonomy.py:1753-1820,3090-3143`;
`tests/test_p1r7f3_exact_declarations.py:350-373`.

The ordinary declaration path now compares exact decimal values. The
sentinel path still identifies, counts, excludes, and removes cells through
their rounded `float` value. Consider rows `1` through `199` plus fifteen
copies of `-999.00000000000001`, with that exact value supplied through
`--keep-value`. The spelling denotes a number distinct from `-999`, although
both round to the same binary64 value. The produced column nevertheless had:

```text
role=count
n_present=199
n_missing=15
(numeric-sentinel)=15
sentinel candidate=-999, verdict=read_as_missing
minimum=1.0
```

The user's exact keep instruction was ignored, fifteen real values were
silently deleted from the profiled population, and the published distribution
changed. Neighbours around all three numeric sentinels behave the same way.
Declaring the exact same value both ways is correctly refused, and a plain
same-binary64 declaration pair is correctly treated as two numbers; the loss
happens later when sentinel logic conflates them again.

**Required closure:** carry `_Cell.exact` through candidate identity,
occurrence counts, reference-population exclusion, and removal. Add all three
sentinels' same-binary64/different-exact neighbours, keep and missing
directions, and distinct-versus-equivalent “both ways” declarations. The
assertion is not merely that declaration comparison is exact; no later rule
may merge the values again.

### [BLOCKER] P1-R8-F3 — the finished-document oracle sweep skips JSON-serializable tuples

**Location:** `tools/reference/make_numeric_reference_vectors.py:521-555,
572-660`.

`_published_numbers` descends through dictionaries and lists, but Python's
JSON encoder also serializes tuples as arrays. This complete mutant reports
zero proved numbers and then writes the number successfully:

```python
published = {"new_statistic": (7.0,)}
prove_every_published_float(published, {})  # 0
json.dumps(published, allow_nan=False)      # {"new_statistic": [7.0]}
```

A full generator mutation added one such tuple-valued field per case; the
tool wrote all sixteen unproved values while still reporting that every
published number had been proved. Tuple and tuple subclasses are the missing
built-in JSON container family. The committed fixture itself remains clean:
regeneration was byte-identical, and an independent traversal found the 312
proved float fields plus the 32 enumerated integer metadata fields.

**Required closure:** traverse both lists and tuples, or sweep the normalized
JSON tree that will actually be written. Keep a full-generator tuple mutant
that must fail before serialization; checking only the current fixture after
regeneration does not test the generator's generic certification claim.

### [BLOCKER] P1-R8-F4 — profile v2 loses the anonymous multiplicity distribution of repeated identifiers

**Location:** `src/synthtwin/taxonomy.py:2754-2788,3223-3224`;
`src/synthtwin/profile.py:211-247`; `docs/plans/phase-1-profiler.md:405-423`.

Two forced-identifier tables used the same three equal-length neutral codes
and six rows. Their frequency multisets were `[4, 1, 1]` and `[2, 2, 2]`.
Their complete profile bytes and complete summaries were identical: each
records `n_present=6`, `n_distinct=3`, the same folded cardinality and the same
length facts, but no anonymous frequencies. A profile-only generator must
choose one repetition pattern for both inputs; grouped analyses immediately
distinguish the two synthetic outputs.

This is the same contract class as the suppressed-level collision repaired
after P1-R1-F9: values need not be published to retain an anonymous count
multiset. The plan explicitly makes `n_distinct` generator-relevant and says
the generator will create neutral identifiers, but it does not state that
their multiplicities are intentionally approximated.

**Required closure:** before generator code consumes this shape, either add a
privacy-reviewed anonymous multiplicity representation and advance
`profile_version`, or obtain an explicit owner decision defining the
deterministic approximation and recording the lost fidelity as a contract
residual. Profile v2 is not sufficient for faithful identifier generation as
currently claimed.

## Group 2 — specification and documentation residuals

Items in this group do not produce a current wrong profile or network route.
They should be recorded under the owner's last-round instruction rather than
confused with the four behavioral repairs above.

### [MINOR] P1-R8-F5 — revision 4 did not propagate the corrected R2 boundary consistently

**Location:** `SECURITY.md:67-92,119-150`;
`docs/plans/phase-1-profiler.md:156-200,668-725`;
`tools/offline_scan/scan_imports.py:11-80,713-744,3250-3284`.

The exact contradictory sentences and clean-scan examples are in the R2
ruling above. A reviewer who relies on the purported exhaustive list can add
`@value`, `with value`, or `hash(value)`, receive a clean scan, and incorrectly
conclude that no caller code was dispatched. A reviewer who relies on the
generic library-result sentence can add `pathlib.Path(value).open()` and
incorrectly expect the scanner to reject it. The documents must describe
examples as non-exhaustive, distinguish restricted pandas instances from
standard-library API instances, and count only immediate path validation as
a run-time reader control.

### [MINOR] P1-R8-F6 — the claimed whole-column publication whitelist filters only three substructures

**Location:** `src/synthtwin/taxonomy.py:262-277,2943-3037,3195-3227`;
`src/synthtwin/profile.py:211-247,250-325`.

The comments promise that the publication class is applied to the whole
column block and that the next field added anywhere is withheld until
whitelisted. `_publication_class_applied` actually receives only `details`,
`missing_by_source`, and `sentinel_verdicts`. `_column_block` separately emits
`detection_evidence` and `remarks`, and `build_document` separately emits
`publication_notes`. The `length` and `words` containers are also admitted as
whole shallow containers rather than recursively checked facts.

Current builders place only counts and static prose in those adjacent routes;
full profile and summary probes found no current value leak for identifier,
forced-identifier-then-empty, free-text, or numeric-unrepresentable columns.
The false part is the fail-closed structural claim: a future evidence or note
field containing a source spelling would bypass this function. State the
current manually bounded property, or move the check to the finished column
document and enforce a recursive whitelist.

### [MAJOR] P1-R8-F7 — profile v2 is not yet a complete normative consumer contract

**Location:** `docs/plans/phase-1-profiler.md:71-78,459-490,731-737`;
`src/synthtwin/profile.py:34-48,211-325`; `tests/test_profile_document.py`.

The plan still calls the contract “v1” in three current passages although the
producer emits version 2. It says each column contains “exactly one
role-specific block,” while the implementation flattens role-specific keys
into the column mapping. It says case variants are recorded distinctly, while
the implementation and tests case-fold and pool them. There is no exhaustive
normative schema for per-role required and forbidden keys, types, enum values,
null meanings, count/sum invariants, unknown or duplicate keys, supported
versions, or fail-closed loading.

The missing generation semantics are concrete. A 100-row column with 99
numbers and one word records the straggler count but not that value; without a
rule, reasonable consumers can emit 100 numbers, 99 numbers plus a missing
cell, a neutral text stand-in, or refuse the profile. The same choice exists
for datetime stragglers, unrepresentable numeric columns, free text, withheld
missing spellings, and suppressed labels. Those consumers would all accept
the same v2 document and create observably different twins.

This is a Phase 2 plan gate rather than evidence that the current producer
wrote a wrong field. Before generator implementation, define the complete
schema and strict loader behavior, then specify the neutral-generation and
fidelity rule for every present-but-unmodelled class. Align the plan's version,
shape, and casing text with that schema.

## Ordered profile-contract judgment for Phase 2

1. **Not sound enough unchanged.** P1-R8-F4 is a real profile collision and
   would require a breaking field addition unless the owner explicitly
   accepts the multiplicity approximation. Resolve it before a consumer fixes
   itself to version 2.
2. **Sound foundations, incomplete grammar.** Source independence,
   deterministic order, explicit row/cardinality counts, numeric and datetime
   distributions, anonymous suppressed-level counts, settings, and the
   version discriminator are useful generator inputs. P1-R8-F7 must turn the
   observed shape into an exhaustive, validated schema and compatibility
   policy before code.
3. **Generation policy is still under-specified.** Decide how every counted
   but unmodelled cell class is emitted and graded. Most of these decisions
   need prose and loader validation rather than new source facts; identifier
   multiplicity is the demonstrated exception.
4. **Relationships are an expected later break.** The plan expressly excludes
   cross-column structure. Adding it will require another profile version;
   that evolution is already disclosed and is not a new Phase 1 defect.

## Areas and properties examined

- **Transaction:** exclusive working-name claims; occupied files and links;
  first and second writes; both renames; prior-output restoration; input and
  output identity; permission/path/metadata failures; cleanup failures;
  `OSError`, ordinary exceptions and `BaseException` subclasses; prologue,
  setup, commit-return and caller-return injection; survivor bytes, ownership,
  original-exception identity, and disk-state wording. Sixty-six shipped
  transaction tests passed; separate line/opcode probes stayed under `/tmp`.
- **Publication boundary:** settings declarations, missing-source maps,
  sentinel verdicts, role details, evidence, remarks, publication notes, JSON,
  and summary text; identifier, forced identifier that ends empty, free text,
  numeric-unrepresentable, below-floor labels, and declared values; canary
  absence and paired noninterference with equal permitted aggregates.
- **Declarations and routing:** exact canonical numeric triples; whole and
  fractional decimal pairs sharing a binary64 value; equivalent decimal,
  exponent and accounting spellings; contradictory declarations; keep and
  missing precedence; all three numeric sentinels; candidate population,
  counts, removal, role, and published minima. An independent 117,644-spelling
  comparison found no ordinary canonicalization mismatch.
- **Numeric proof:** finished-document traversal; integer-valued `float64`
  refusal; exact-claim consumption; list, tuple and scalar shapes; finite,
  subnormal, overflow and signed-zero cases; fixture regeneration and an
  independent traversal of the serialized document.
- **Profile/generator contract:** every top-level and column field, every role
  shape, null/count invariants represented in tests, profile versioning,
  deterministic bytes, identifier and suppressed-label collisions, numeric
  and datetime stragglers, nonpublishing roles, and the deliberate absence of
  relationships.
- **Offline/security boundary:** Phase 0 Amendment A3, revision-4 R2,
  `SECURITY.md`, scanner binding and instance policies, implicit data-model
  protocols, decorators, callback slots, the single pandas call, immediate
  locality validation, and URL/UNC/device/unproved path cases. The probes ran
  the scanner only; they did not execute the constructs.
- **Repository controls:** full source tests, static scan, decontamination,
  provenance regeneration, frozen-lock structure, lint, typing, dependency
  inventory, and current repository state. No probe or test script was added
  to the repository.

This host was macOS. Windows path and reparse behavior was covered through the
project's platform fakes/tests rather than a live Windows host. Power loss was
not simulated; it remains the explicitly stated durability residual.

## Commands and results

All required commands were run from `synthtwin` at the reviewed baseline:

```text
.venv/bin/python -m pytest -q
1387 passed, 4 skipped

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

Focused declaration/publication/oracle selections also passed, which is why
the neighbours required separate `/tmp` probes. Before this report was
written, `git add -A` followed by the decontamination check was clean. The
report itself was then staged and scanned again; it was also clean.

## Verdict

**Verdict: reject.** The blocking items are P1-R8-F1 (the transaction guard
does not cover its own setup and does not preserve every original failure),
P1-R8-F2 (exactly kept decimal neighbours are removed as rounded sentinels),
P1-R8-F3 (JSON-serializable tuple numbers bypass the oracle proof), and
P1-R8-F4 (identifier multiplicity collides in the profile-v2 contract).
P1-R8-F5 and P1-R8-F6 are documentation-only residuals. P1-R8-F7 is a
bounded Phase 2 specification gate and is not an additional reason for this
rejection.

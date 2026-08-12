# Phase 2 plan review, round 1

**Reviewed:** 2026-08-10  
**Plan:** `docs/plans/phase-2-generator.md`, revision 0  
**Review type:** plan-only ratification gate; no Phase 2 implementation exists

## Review basis and method

I read the complete required baseline: `CLAUDE.md`, `AGENTS.md`,
`SECURITY.md`, the ratified Phase 0 plan, the Phase 1 plan at revision 5,
and the Phase 1 round-8 review. I then read revision 0 in full and checked
its producer claims against `profile.py`, `taxonomy.py`, and `parsing.py`.
I also inspected the offline scanner, transaction writer, command path,
dependency floor, and the relevant Phase 1 tests.

This review does not revisit the owner's settled choices to add three
classification fields, extend multiplicity parity, reserve an all-null
relationship block, or allocate counts exactly. It tests whether revision 0
states those choices completely and carries their consequences into a
coherent, implementable contract.

I ran neutral, in-memory producer probes for raw-versus-parsed numeric
distinctness, negative whole-number columns, very large numeric spellings,
folded labels, identifier invention capacity, and structured free text. I
also ran the existing profile-document and offline-scanner tests and the
current source scan. Those checks passed; the review items below concern the
proposed Phase 2 contract, not a nonexistent implementation.

## Review items

### P2-R1-F1 — Revision 0 does not pass the repository's content gate

**Severity: BLOCKER.**

**Location:** revision 0 lines 65-68 and 569-570; repository content scanner.

An independent value-silent scan of the untracked plan found six matches:
line 146 against manifest hash prefix `37852d1c963b`, and lines 223, 238,
283, 393, and 501 against manifest hash prefix `0cfa4a919f59`. No matched
text is reproduced here. The ordinary no-argument command currently obtains
its file list from `git ls-files`, so its clean result does not cover this
untracked plan.

**Failure scenario:** revision 0 is committed unchanged. The mandatory
repository scan then includes it and turns the blocking gate red, despite the
plan's claim that this plan scans clean. If review relies only on the current
untracked no-argument run, the defect remains hidden until the file enters
the index.

**Required closure:** rewrite the six plan locations using neutral language,
without changing the scanner or its manifest; then scan the tracked plan and
record a clean result.

### P2-R1-F2 — The v4 wire contract is still deferred past this ratification gate

**Severity: BLOCKER.**

**Location:** revision 0 lines 31-41, 70-95, 118-132, and 614-615;
`profile.py` lines 241-277 and 280-355; `taxonomy.py` lines 1915-1969;
Phase 1 review P1-R8-F6 and P1-R8-F7.

Revision 0 says this plan fixes every decision and closes the ordered
consumer-contract judgment, but it expressly leaves the flat-versus-nested
role shape, case behavior, and the F6 enforcement mechanism to later
implementation choice. The proposed profile contract is not itself in the
listed sequence of separately ratified artifacts. The shipped producer
flattens role details and publishes trimmed, case-folded label identities;
those are observable wire semantics, not editorial details.

**Failure scenario:** implementer A writes the v4 contract around the shipped
flat, folded producer. Implementer B follows the older prose, nests a role
block, and preserves raw case variants. Both can claim conformance to
"whichever way," yet their strict loaders reject each other's documents and
their generated category values differ. The first consumer has again been
designed before its contract is fixed.

**Required closure:** make `docs/spec/profile-contract-v4.md` a separately
reviewed, blocking artifact before the generation method or code; decide the
wire shape, label identity, every key's semantics, and one F6 enforcement
mechanism in revision 1. The loader, producer, report, and generator must all
bind to that same ratified contract.

### P2-R1-F3 — The required duplicate-key parser is forbidden by the current offline policy

**Severity: BLOCKER.**

**Location:** revision 0 lines 96-108; `tools/offline_scan/scan_imports.py`
callback-slot table and checks around lines 799-863 and 3351-3450.

The plan requires a first-party function in `json.load` or `json.loads`'
`object_pairs_hook` slot. The current scanner explicitly classifies that as
a callback slot and rejects a scanned function placed there. Revision 0 does
not request or audit a policy change for it.

**Failure scenario:** the loader calls
`json.loads(text, object_pairs_hook=reject_duplicates)`. The loader correctly
refuses `{"n_rows": 1, "n_rows": 100}`, but the offline gate fails. If the
hook is omitted to keep CI green, Python silently retains 100 and generation
uses a row count the first spelling contradicted. If the callback policy is
quietly relaxed, unreviewed external invocation enters the allowlist.

**Required closure:** specify a duplicate-detecting parse construction that
passes the existing scanner, or add an exact D6.2 amendment with callback
identity, invocation, origin, and red-mutation analysis. The plan cannot
promise both the present hook and the present policy.

### P2-R1-F4 — The profile/generator boundary is tested only at the first import edge

**Severity: BLOCKER.**

**Location:** revision 0 lines 45-63, 456-465, and 563-568;
`profile.py` line 32 and its transaction implementation; `cli.py` line 50.

The promised red mutation catches a generation module importing `reading`
or `pandas` directly. The scanner accepts ordinary first-party imports and
does not enforce a forbidden transitive dependency graph. This matters
immediately because the transaction code the plan says to generalize lives
in `profile.py`, which imports the real-table type, while the command module
imports the real-table reader.

**Failure scenario:** `study-profile.json` sits beside `study.csv`. A new
first-party workflow facade imports and re-exports `read_table`; generation
imports that facade and derives the sibling name by stripping
`-profile.json` for a diagnostic preview. No generation file directly
imports `reading` or `pandas`, so the stated mutations pass, but generation
reads `study.csv` and its output is no longer a function of profile plus
seed. Importing transaction code from `profile.py` does not itself read a
table, but it defeats the claimed module separation and leaves the reader
dependency reachable.

**Required closure:** define and test a transitive forbidden-import graph and
forbidden reachable-call graph for all generation modules, including
re-exports and aliases; add API-signature mutations that refuse table paths,
file handles, and raw cell collections at every reachable layer. Move the
transaction primitive to a neutral module before generation uses it, and
rerun its statement/opcode injection measurement after that refactor rather
than inheriting the old count by assertion.

### P2-R1-F5 — Per-column child generators contradict ratified D12

**Severity: BLOCKER.**

**Location:** Phase 0 D12 lines 428-447; revision 0 lines 305-307, 355-367,
551-555, and 583-587.

Ratified D12 requires one `numpy.random.Generator`, created once and threaded
through the whole operation. It says a keyed or per-column design needs an
explicit charter amendment with the derivation and vectors. Revision 0
instead spawns child generators and requires an unrelated column to remain
unchanged when another column consumes different draws, while claiming D12
is honored.

**Failure scenario:** a two-column profile is generated with seed 7.
Revision 0 creates one parent and two child `Generator` objects and produces
child-stream bytes. An implementation that creates one literal generator
instead produces sequential-stream bytes and fails the required
column-local test; an implementation that spawns the children fails D12's
one-object rule. No implementation or determinism test can satisfy both
records.

**Required closure:** retain D12's single sequential stream and remove the
column-local invariant, or obtain and record the exact charter amendment D12
requires before ratification, including seed derivation, stream identity,
draw order, and frozen vectors.

### P2-R1-F6 — The twin byte contract contradicts D12 and can be impossible to encode

**Severity: BLOCKER.**

**Location:** Phase 0 D12 lines 448-460; revision 0 lines 317-319, 357-359,
and 469-476; `parsing.py` lines 283-294; `taxonomy.py` label construction.

D12 fixes canonical text artifacts to UTF-8 with explicit LF and fixes
dates/times to ISO 8601 with explicit offset and precision. Revision 0
instead fixes CSV to the source encoding with CRLF and writes datetimes in
the matched source format. Its claim that every published label re-encodes
is also false because the producer publishes Unicode case-folded identities,
not necessarily the decoded source code points. Revision 0 also silently
strengthens D12's same-platform byte promise and empirical cross-platform
check into unconditional cross-platform byte identity, removing D12's
documented per-platform-golden fallback.

**Failure scenario A:** a Latin-1 table contains an above-floor label made from
U+00B5. The shipped producer publishes its folded identity U+03BC. That code
point cannot be encoded as Latin-1, so a conforming generator raises an
uncatalogued `UnicodeEncodeError`. Independently, any source encoding other
than UTF-8 and any CRLF output violates D12 even when generation succeeds.

**Failure scenario B:** a valid date column matched as `MM/DD/YYYY` must be
written with slashes under revision 0 and in ISO 8601 form under D12; no CSV
cell satisfies both. Separately, a one-bit platform divergence is
release-blocking under revision 0 but may use D12's disclosed per-platform
goldens, so the two records prescribe different release outcomes.

**Required closure:** conform twin and report bytes to D12, or ratify an
explicit D12 amendment that fixes both artifacts' exact encoding and newline
rules, datetime representation, and cross-platform fallback. Define whether
twin labels are normalized, prove or validate their encodability, and
specify a human-actionable refusal for every impossible case.

### P2-R1-F7 — “Every published count” is not carried through the allocation rules

**Severity: BLOCKER.**

**Location:** revision 0 lines 250-288, 392-402, 543-550, 623-626, and
667-669; `profile.py` lines 249-274; `taxonomy.py` lines 1680-1735 and
3378-3397.

The settled exact-allocation choice is stated globally, but the normative
list omits common published counts. In particular, converting every absent
cell to empty cannot reproduce `missing_by_source` or `missing_by_class`, and
distribution roles have no rule that preserves ordinary `n_distinct`. This
is an internal contradiction between the global owner-decision summary and
the detailed empty-cell exception, not a reason to reopen exact allocation.

**Failure scenario A:** a 1,100-row numeric column has 11 recognized coded
absent cells. The profile publishes 11 for that source spelling and class;
the twin writes 11 empty cells. Reprofiling preserves `n_missing` but changes
both published maps.

**Failure scenario B:** a 100-row continuous column cycles among 11 distinct
fractional quantities. It publishes `n_distinct = 11`. Piecewise
interpolation can emit almost 100 different quantities, so grouping code
sees about 100 groups in the twin and 11 in the real table although the plan
says every published count is exact.

**Required closure:** add a field-by-field table for every v4 count and carry
the settled exact-count decision through all of them, including independent
CSV recounts. If the empty-cell rule or any other exception is retained,
obtain and record an explicit owner amendment that bounds the exception;
implementation judgment cannot silently narrow the decision. Define an
exact, feasible rule for `n_distinct` under the reconciled decision.

### P2-R1-F8 — The universal all-different rule is undefined and infeasible for valid profiles

**Severity: BLOCKER.**

**Location:** revision 0 lines 258-269, 308-313, 323-329, 426-439, and
543-550; `taxonomy.py` raw distinctness and numeric-statistic paths around
lines 1387-1467 and 1998-2023.

`n_distinct` counts raw source strings, while numeric statistics describe
parsed values and category facts use folded identity. Revision 0 never says
whether equality means CSV spelling, folded text, numeric value, or datetime
instant. Collision repair cannot create capacity that the other exact facts
forbid.

**Failure scenario A:** the 100 raw cells `0`, `0.0`, `1`, `1.0`, through
`49`, `49.0` form a valid count profile with `n_present = n_distinct = 100`,
integer-valued data, minimum 0, maximum 49, and two zeros. One hundred
different integer values cannot fit in the inclusive range of 50 integers;
the exact two-zero count already requires a numeric duplicate.

**Failure scenario B:** 200 distinct one-character Unicode values declared
as an identifier publish a one-character length range and an all-singleton
multiplicity map. An ASCII invention domain has at most 128 one-character
values and fewer safe printable values, so it cannot satisfy length,
multiplicity, and all-different simultaneously.

**Required closure:** define equality separately for each statistical path;
add cross-field feasibility constraints and capacity checks; and widen the
invention domain enough to preserve the settled exact invariants. Relaxing
length, ASCII, multiplicity, or another exact invariant requires an explicit
owner amendment and report disclosure. A refusal is coherent only if the v4
producer/schema domain is narrowed so the producer cannot emit the refused
profile, with that compatibility and privacy consequence recorded. Freeze
genuine producer regression profiles for both scenarios.

### P2-R1-F9 — The unrepresentable-number method assumes facts v4 does not publish

**Severity: BLOCKER.**

**Location:** revision 0 lines 170-198 and 409-413; `taxonomy.py` lines
2415-2422.

The proposed v4 additions provide an anonymous multiplicity map but no
length facts for `numeric_unrepresentable`. The shipped block instead records
sign and whole-versus-fraction count marginals. The proposed digit-string rule
both depends on absent length information and fails to say how the facts that
do exist are preserved.

**Failure scenario:** 100 distinct positive whole-number strings of roughly
400 characters and 100 of roughly 4,000 characters produce identical shipped
details; the proposed new fields are identical as well. A profile-only
generator must make the same output for both and therefore gives incorrect
field width to at least one. A negative overflow case also publishes a
negative and whole-number count that the unspecified invention rule can
erase.

**Required closure:** either add explicitly privacy-classified length/shape
facts to the reviewed v4 contract, or withdraw length fidelity and specify a
deterministic approximation and its report wording. In either case, define
exact generation or an honest disposition for every sign and whole/fraction
count already published.

### P2-R1-F10 — Numeric stragglers and integer-valued continuous columns remain misrouted

**Severity: BLOCKER.**

**Location:** revision 0 lines 263-267, 308-313, 403-413, and 543-550;
`profile.py` lines 249-270; `taxonomy.py` lines 1998-2019 and 3011-3035.

The producer distinguishes representable numeric cells, out-of-range numeric
spellings, contradictory spellings, ordinary nonnumeric cells, and negative
unrepresentable cells. Revision 0 maps numeric stragglers to one neutral text
scheme. It also limits the integer generation rule to the `count` role even
though `integer_valued` is published for continuous columns.

**Failure scenario A:** cells `0` through `98` plus `-1e999` produce a
continuous profile with one out-of-range cell, no ordinary nonnumeric cell,
one negative cell, one negative-unrepresentable cell, and minimum 0. A word
stand-in changes the first two class counts and erases both negative facts;
an ordinary negative numeric value violates the exact minimum.

**Failure scenario B:** integers `-50` through `49` profile as continuous
with `integer_valued = true`. Piecewise interpolation under the plan may emit
fractions because the integer rule is role-gated, so integer-only application
code succeeds on the real table and fails on the twin.

**Required closure:** normatively partition every left-out numeric class and
their sign intersections, provide class-preserving neutral constructions, and
recount them independently from the CSV. Route integer construction by the
published fact, not by role alone, and add genuine producer fixtures.

### P2-R1-F11 — Other counted classes still have no generation disposition

**Severity: BLOCKER.**

**Location:** revision 0 lines 300-331, 385-447, and 543-550;
`taxonomy.py` lines 1975-1995 and 2105-2187.

P1-R8-F7 required a normative policy for every class the producer counts but
does not model. Role-level prose still omits fields such as free-text
`n_all_digits` and `n_code_alphabet`, and datetime offset counts and
precision facts. This is a contract gap even if a future method author can
invent reasonable behavior.

**Failure scenario:** 1,000 distinct four-character text cells contain 980
digit-only strings and 20 alphabetic strings. The shipped profile records
`n_all_digits = 980`, `n_code_alphabet = 1000`, fixed length four, and
one-word shape; proposed v4 additionally records singleton multiplicity. One
implementation emits only alphabetic neutral words; another emits 980 digit
strings. Both satisfy revision 0's listed text rules, but `.isdigit()`
returns 0 in one twin and 980 in the other, while the real table returns 980.

**Required closure:** put every required v4 field in an exhaustive generation
and validation matrix before the method specification is written. For each
field, state its exact construction, approximation and bound, report-only
treatment, or intentional refusal. Include datetime resolution, format,
offset, precision, and straggler intersections in the same audit.

### P2-R1-F12 — The proposed ladder property test cannot detect loss of interior rungs

**Severity: BLOCKER.**

**Location:** revision 0 lines 274-279, 308-316, 514-516, and 543-550.

Containment plus monotonic empirical quantiles does not compare generated
quantiles with the profile's ladder. Empirical quantiles are monotonic by
definition. The remaining moment check is called generous, but revision 0
fixes neither its formula nor its bound.

**Failure scenario:** a valid continuous profile comes from 1,010 cells:
`0.5` through `100.5`, each repeated ten times, with no absent, zero, or
negative cells. A mutant emits one minimum and 1,009 maxima. It preserves the
stated exact present, sign, and zero counts and both endpoint values; every
value is contained; its empirical quantiles are monotonic; and the
all-different trigger is off. The stated property battery therefore passes
unless the later author chooses a sufficiently small moment tolerance, while
the nine interior rungs and the center are silently lost.

**Required closure:** require the method specification to define a
finite-sample expected value or envelope at every rung and a fixed,
nonvacuous moment formula and bound. Add mutants that ignore, permute, and
swap interior rungs and require each to fail outside the frozen-vector tests.

### P2-R1-F13 — The record claim does not exclude exact row-value matches

**Severity: BLOCKER.**

**Location:** revision 0 lines 13-17, 443-447, 466-467, and 522-527.

The unqualified record claim can reasonably be read as excluding any exact
row-value match. Exact allocation of published labels can force such a match
even though the generator never reads or samples a row. That is a consequence
of the settled allocation decision, not a reason to revisit it.

**Failure scenario:** an 11-row, one-column table contains one above-floor
constant label. Its profile publishes that label and count 11. The required
twin contains that label in all 11 rows, so every twin row equals a real row.
The same is forced for a table composed only of published constant columns.

**Required closure:** replace the categorical claim with a provenance claim:
generation reads no source table and does not sample or copy source rows, but
row equality can occur by coincidence or can be forced by published facts in
low-dimensional tables. Put the same qualification in command help, README,
and every report.

### P2-R1-F14 — The twin and report are misclassified for disclosure handling

**Severity: BLOCKER.**

**Location:** revision 0 lines 184-198, 456-483, and 494-527; `SECURITY.md`
threat-model and institutional-handling sections.

Calling the twin merely adjacent to real-derived output while saying the
profile remains the governed artifact understates the output. The twin and
report reproduce real-derived published labels, extrema, ladder values,
counts, column names, and published absent-value spellings. `SECURITY.md`
excludes formal statistical disclosure control from the threat model; it
does not establish that these outputs contain no real-derived facts.

**Failure scenario:** a user assumes the twin needs fewer institutional
controls because the report treats it differently from the profile, and
moves it beyond the authorized environment. A rare-but-above-floor category
label and exact numeric extreme then leave that environment even though
institutional policy would have required review of any real-derived artifact.

**Required closure:** classify the twin and report explicitly as artifacts
containing real-derived published facts; state that synthtwin provides no
formal privacy guarantee; and apply the institutional handling and approval
warning to all three outputs. Preserve the useful distinction that no source
row is read or sampled, but do not turn that provenance property into a
disclosure classification.

### P2-R1-F15 — Default output identities and collision behavior are unspecified

**Severity: BLOCKER.**

**Location:** revision 0 lines 449-465; shipped `profile.default_output_paths`
and transaction collision checks; shipped command option `--out-dir`.

The plan names a destination-folder option but not the two exact file names,
the default folder, suffix derivation, existing-target ownership rule, or how
the generate option relates to the shipped `--out-dir` convention. Those are
part of both zero-code UX and the transaction safety contract.

**Failure scenario:** `study-profile.json` sits beside the original
`study.csv`. An implementation that strips the profile suffix and chooses
`study.csv` as the twin target designates the original as an output. The
current writer sets aside and replaces an existing designated target; because
generation is intentionally not given the real-table path, its identity guard
cannot recognize `study.csv` as the source. A successful zero-option run can
therefore replace the real table. Another implementer can choose
`study-twin.csv`, making behavior and data-loss risk differ under the same
ratified plan.

**Required closure:** fix safe, noncolliding twin and report suffixes, exact
default placement, the option name and semantics, existing-target ownership
and replacement behavior, and input/output identity checks. Add ordinary
adjacent-layout, alias, link, preexisting-target, and two-target collision
cases to the transaction acceptance criteria.

### P2-R1-F16 — Published category identities are normalized, not source spellings

**Severity: MAJOR.**

**Location:** revision 0 lines 443-447, 478-483, and 522-527;
`taxonomy.py` lines 1915-1969; `parsing.py` lines 283-294.

The plan repeatedly describes published labels as real labels. The shipped
producer trims and Unicode-case-folds before pooling and publishing them.
That may remain the v4 contract, but then the twin is reproducing a normalized
identity that may never have appeared byte-for-byte in the source.

**Failure scenario:** a column contains 11 `TAG_A` and 11 `TAG_B` cells. The
profile publishes normalized lower-case identities, and the twin writes
those. A case-sensitive filter for `TAG_A` returns 11 on the real table and 0
on the twin even though the report calls the emitted value the real label.

**Required closure:** decide the label identity in the v4 contract. If folded
identity remains, call it normalized everywhere and disclose case/edge-space
loss. Preserving raw variants would be a new disclosure rule and requires its
own floor and privacy review; it cannot be chosen during implementation.

### P2-R1-F17 — E7-E9 are not yet the exact, API-granular D6.2 extension

**Severity: BLOCKER.**

**Location:** Phase 0 D6.2; revision 0 lines 572-602 and 640-647; current
`requirements-min.lock` line 19.

E8 permits unspecified “draw methods” and defers the exact list to the later
method review. E9 names the writer constructor but not the returned writer
methods the code must invoke, their accepted argument origins, or the
result-instance propagation rule. That is not the plan-level exact capability
audit D6.2 requires. There is also a concrete floor conflict if spawning
survives F5: the current minimum lock has NumPy 1.24.0, while the installed
API documentation marks `Generator.spawn` as added in 1.25.0.

**Failure scenario:** the minimums job installs the current floor and a
generator calls `spawn`; generation fails with `AttributeError`. Separately,
one scanner implementation permits only `random`, while another permits
`choice`, `permutation`, and `shuffle` under the phrase “draw methods.” Both
claim plan conformance, and one may admit an unreviewed return type or method
chain.

**Required closure:** in the ratified plan, enumerate every constructor,
instance method, returned type, allowed argument form, callback-capable slot,
output handle, and result-origin propagation rule for E7-E9, with one red
mutation per capability. Set and test the true NumPy floor for the retained
API; if F5 removes spawning, remove that API rather than auditing dead power.

### P2-R1-F18 — Report text has no display or byte-serialization boundary

**Severity: MAJOR.**

**Location:** revision 0 lines 456-483 and 556-562; shipped
`parsing.visible` and `parsing.visible_lines` boundaries.

The report interpolates source-derived column names, normalized labels, and
published absent-value spellings, but the plan does not require display
escaping for controls or bidirectional formatting characters. It also does
not fix the report's encoding, newline form, terminal newline, or include
report bytes in the golden contract.

**Failure scenario:** an above-floor label contains embedded U+000A followed
by a neutral sentence that looks like a report conclusion. If the report
writes the label directly, the value creates a new apparent report line and
the user attributes the sentence to synthtwin. On two platforms, default
newline handling can also produce different report hashes while the twin
golden remains green.

**Required closure:** require one finished-report display boundary equivalent
to the shipped safe-display functions; specify handling of line, control, and
bidirectional characters; fix UTF-8/LF/terminal-newline bytes under D12; and
golden-test the complete report with adversarial names and published values.

### P2-R1-F19 — Spreadsheet formula handling conflicts with exact label fidelity

**Severity: BLOCKER.**

**Location:** revision 0 lines 443-476 and 478-483; exact published headers
and category identities; spreadsheet-oriented CSV output.

Source-derived headers and above-floor labels are inert strings in JSON but
can be interpreted as formulas when the advertised CSV is opened in common
spreadsheet software. Minimal CSV quoting does not neutralize that
interpretation. Prefixing or otherwise altering the cell may make it safe in
one spreadsheet, but then the CSV value no longer equals the published label
the settled exact-allocation rule requires.

**Failure scenario:** an above-floor category label is `=1+1` in 11 rows.
The profile safely records that text. The twin writes it exactly and a
spreadsheet displays the computed value 2 rather than the category; more
capable formula forms can initiate external activity when a user opens the
file. If generation prefixes the value to prevent evaluation, ordinary CSV
readers see a changed category and exact label fidelity fails.

**Required closure:** decide and document the formula-context policy before
ratification. Specify which headers/cells are hazardous, whether the product
refuses them, changes them under an explicit owner amendment, or emits an
additional safe-view artifact, and give zero-code users an unavoidable
warning. Test both literal CSV readers and supported spreadsheet behavior;
ordinary CSV quoting must not be presented as a mitigation.

### P2-R1-F20 — Version-skew and seed advice is not directionally correct

**Severity: MINOR.**

**Location:** revision 0 lines 100-103, 371-373, and 485-491.

The same advice is prescribed for both older and newer profile versions, and
the seed is only described as an integer. NumPy's seeded constructor does not
accept every Python integer.

**Failure scenario:** a machine with a v4 generator receives a valid v5
profile but not the real table. The error tells the user to re-run the
profiler with the older tool, which is impossible on that machine and would
discard newer semantics; the correct action is to update the generator. In a
separate ordinary run, `--seed -1` passes integer parsing and produces a raw
library exception absent from the failure catalog.

**Required closure:** distinguish older-profile advice from newer-profile
advice, never assume the generation machine has the source table, define the
accepted nonnegative seed range, and wrap range/type failures in tested
plain-language guidance.

### P2-R1-F21 — The P1-R8-F5 documentation repair remains incomplete

**Severity: MINOR.**

**Location:** revision 0 lines 118-126 and 604-615; Phase 1 review
P1-R8-F5; scanner documentation and decorator handling.

Revision 0 corrects the enumeration of data-model hooks but does not carry
round 8's broader point that other explicitly admitted implicit call forms,
including decorator application, also execute code without an ordinary call
expression at the use site.

**Failure scenario:** a reviewer reads the repaired security text, audits
only data-model hooks on untraced values, and treats an untraced decorator
applied through an admitted implicit-call form as outside the residual. Code
executes at definition time while the public description again makes the
best-effort scanner sound narrower and more complete than it is.

**Required closure:** describe data-model hooks as examples and state the
full residual as all explicitly admitted implicit-call forms, including
decorators. Add a documentation assertion or scanner test that prevents the
wording from becoming exhaustive again.

### P2-R1-F22 — The position-base migration is silent

**Severity: MINOR.**

**Location:** revision 0 lines 83-94; `profile.py` line 311;
`taxonomy.profile_column` lines 3202-3217.

Revision 0 requires positions `0..n_columns-1`, while the shipped producer
and its public function contract use one-based positions. A v4 bump may carry
that change, but it is not one of the stated v4 migrations and has no
conversion or user-facing explanation.

**Failure scenario:** producer and loader are both changed to zero-based
positions, but an existing integration still maps a profile column with
`columns[position - 1]`. The first v4 column has position 0 and is therefore
silently mapped to the last column rather than the first. The version refusal
does not protect code that upgrades the library and consumes newly produced
v4 documents.

**Required closure:** explicitly retain one-based positions or explicitly
migrate producer, API contract, fixtures, documentation, and loader together;
add a producer-to-loader round trip that fixes the chosen base.

## What was checked

### Surfaces

- Every Phase 2 decision P2-D1 through P2-D14, the acceptance criteria,
  planning decisions, and claimed closures of P1-R8-F4 through F7.
- The complete top-level profile document and every common column field
  emitted by `profile.build_document` and `_column_block`.
- All shipped role paths, raw and normalized distinctness, label pooling,
  absent-cell source/class maps, numeric classification, datetime metadata,
  text details, identifier declarations, and multiplicity serialization.
- Command arguments, default paths, path validation, two-file transaction,
  report display boundary, dependency minimums, and the D6.2 scanner policy.
- Phase 0 D12, the profile-only boundary, offline guarantee, institutional
  handling language, deferred governance wording, oracle ordering, and
  provenance/change-detector distinctions.

### Properties and attack classes

- Schema completeness, unknown/duplicate keys, type/range/count invariants,
  producer/loader self-compatibility, version migration, and consumer
  ambiguity.
- Direct and transitive table access, first-party re-exports, callback
  execution, native/dependency capability growth, result-instance methods,
  local-path enforcement, and output alias/collision behavior.
- Silent statistical divergence from type misrouting, raw-versus-parsed
  equality, exact count interactions, absent-cell rewriting, straggler class
  loss, invention-domain exhaustion, integer routing, ladder-test vacuity,
  and unmodeled published fields.
- RNG topology, draw-order coupling, sorted randomness-consuming iteration,
  seed domain, encoding/newline determinism, report escaping, and platform
  byte identity.
- New real-derived facts, label normalization, low-dimensional row equality,
  disclosure classification, below-floor withholding, and public-text
  content scanning.

### Checks that did not produce review items

- The three additive classification fields are deterministic restatements of
  existing role/settings facts and add no new disclosure by themselves.
- The multiplicity map's key padding and two sum invariants match the shipped
  identifier helper; its count-only publication class is stated consistently.
- The reserved all-null relationship block adds no real-derived content, and
  fail-closing every slot to null is sound for this phase.
- A single v3-to-v4 version increment is appropriate for one coordinated
  schema change, once the complete v4 contract is fixed.
- Exact allocation is a strong, independently recountable choice for the
  fields to which the contract actually applies.
- The exact-rational oracle discipline, separation from `src/`, tuple-aware
  serialized-tree sweep, and treatment of goldens as change detectors rather
  than oracles are sound plan elements.
- The plan does not overstate the repository's deferred public-hosting
  controls, and no Phase 2 code is falsely presented as shipped.

### Verification performed and limits

- `.venv/bin/python -m pytest -q tests/test_profile_document.py
  tests/test_offline_scan.py`:
  122 passed.
- `.venv/bin/python tools/offline_scan/scan_imports.py src`: 9 Python files,
  0 violations.
- Producer probes used only neutral values and performed no file or network
  I/O.
- This was a paper review. The v4 contract, generation method, frozen vectors,
  and implementation do not yet exist, so they could not be reviewed. The
  live host was macOS; Windows behavior was checked only against the stated
  Phase 0 requirements and current CI descriptions.

## Verdict

**REJECT.** The blocking items are **P2-R1-F1 through P2-R1-F15,
P2-R1-F17, and P2-R1-F19**. Revision 0 may not be ratified and no generator
implementation may begin until those items are closed in a revised plan.
P2-R1-F16, P2-R1-F18, and P2-R1-F20 through P2-R1-F22 are also required plan
repairs; they are not permission to defer defects into the method
specification or implementation.

# Phase 2 plan review, round 2

**Reviewed:** 2026-08-10  
**Plan:** `docs/plans/phase-2-generator.md`, revision 1  
**Review type:** plan-only ratification gate; no Phase 2 implementation exists

## Outcome

Revision 1 makes material repairs. It fixes the flat role shape, retains
one-based positions, defines normalized label identity, replaces the forbidden
duplicate-key callback with canonical round-trip, returns to D12's single
stream, fixes UTF-8/LF output, ties header presence to `header_source`, records
the forced-row-equality consequence, reclassifies all three artifacts, and
takes a formula-context decision.

Those repairs do not yet form one implementable contract. Eight round-1 items
close fully; eleven close only in part; three only appear closed because their
decisive mechanism is still deferred or their original failure route remains.
Nine blocking defects remain in revision 1, including contradictions inside
the new disposition, feasibility, datetime, output, boundary, scanner, and
validation surfaces.

## Review basis and method

I read the complete required baseline: `CLAUDE.md`, `AGENTS.md`,
`SECURITY.md`, the ratified Phase 0 plan, the Phase 1 plan at revision 5, the
Phase 1 round-8 review, and the Phase 2 round-1 review. Round 1 was used as the
finding record, not as a line map. Every citation below was re-derived from
revision 1.

I checked revision 1's producer and scanner claims against the shipped code,
including `profile.py`, `taxonomy.py`, `parsing.py`, `reading.py`, `cli.py`,
the transaction writer, and `tools/offline_scan/scan_imports.py`. I also ran
neutral producer/reader probes for raw-versus-folded identity and a leading
U+FEFF header, checked NumPy's accepted integer behavior, ran the relevant
existing tests, and scanned the current source.

The four decisions in "Decisions taken at planning" and the inherited owner
decisions are treated as settled. This review tests whether their consequences
are specified and carried consistently; it does not reopen the choices.

## Closure of every round-1 item

The last column gives either the concrete surviving failure scenario or the
test that established closure. “None” means the old item is no longer a live
review item.

| Round-1 item | Judgment | Remaining severity | Independent closure check |
|---|---|---:|---|
| P2-R1-F1 | **Closed.** Revision 1 records the index-only limitation and requires a tracked-file check at lines 16-18, 90-91, and 774-776. | None | I scanned an exact byte-copy of revision 1 from a non-Git temporary root and verified the copy with `cmp`; the scanner read it and returned clean. |
| P2-R1-F2 | **Partly closed.** The contract is now a separate blocking artifact and the three wire decisions are fixed at lines 37-56 and 95-162. The required P1-R8-F6 enforcement choice remains deferred between two mechanisms at lines 170-173. | MAJOR; P2-R2-F12 | A future source spelling placed in `remarks` can bypass a partial manual check, while a recursive finished-document check would refuse it. Both implementations still fit revision 1 because this plan chooses neither. |
| P2-R1-F3 | **Closed.** Plain parsing followed by canonical serialization and exact byte comparison is specified at lines 141-153, with duplicate/reordered mutations at lines 655-656. | None | A duplicated key collapses during plain parsing and therefore cannot reproduce the input bytes. No callback slot is needed. |
| P2-R1-F4 | **Partly closed.** Transitive imports, a neutral transaction module, and signature mutations are added at lines 74-88, but the actual command root and call-graph semantics remain undefined. | BLOCKER; P2-R2-F1 | Rooting the check at the installed `cli.main` reaches `reading`; rooting it below the command permits pre-call table access in the command facade. |
| P2-R1-F5 | **Closed.** Lines 418-451 withdraw child streams and require one explicitly threaded `Generator`, schema-order consumption, fixed special-element placement, and D12's version policy. | None | The proposed topology now matches Phase 0 D12; revision 1 no longer requires unrelated-column invariance. |
| P2-R1-F6 | **Partly closed.** Lines 553-564 correctly fix UTF-8, LF, no marker, terminal newline, and report bytes. The datetime rule still contradicts D12, and the leading-header case makes the byte and name promises jointly false. | BLOCKER; P2-R2-F2 and P2-R2-F9 | A month-first datetime cannot be both source-formatted and ISO 8601. Separately, an exact leading U+FEFF name becomes the byte sequence that the same reader consumes as an encoding marker. |
| P2-R1-F7 | **Partly closed.** The blanket count claim is replaced by a useful four-way matrix at lines 263-350, but the matrix omits shipped fields, contains a raw/folded contradiction, and gives numeric distinctness only a one-sided ceiling. | BLOCKER; P2-R2-F3 | A profile with 50 raw numeric spellings for two parsed endpoint values can yield only those endpoints and still meet “at most” 50; two raw category spellings that fold together cannot preserve both exact raw distinctness and exact normalized levels. |
| P2-R1-F8 | **Only appears closed.** Equality notions and capacity checks are named, but lines 352-366 defer each actual outcome to a later choice between relaxation and refusal. | BLOCKER; P2-R2-F4 | A valid 200-distinct, one-character identifier either violates an EXACT length/count row or is refused despite being valid producer output. The plan has not chosen which contract applies. |
| P2-R1-F9 | **Closed.** Lines 212-223, 344-350, and 732-736 explicitly withdraw width fidelity, preserve the fields that exist, and disclose one canonical invented width as a residual. | None | Two profiles with different hidden widths may intentionally yield the same invented shape, and revision 1 now says so rather than claiming otherwise. |
| P2-R1-F10 | **Partly closed.** Lines 303-308 and 472-484 route integer construction by fact and partition numeric leftovers. The required frozen, genuine producer profiles are absent; lines 666-669 require only constructed documents. | MAJOR; P2-R2-F4 | A hand-built fixture can omit or normalize a producer field involved in the conflict, so both the loader and generator pass while the same document emitted by Phase 1 follows a different path. |
| P2-R1-F11 | **Partly closed.** The matrix adds the named text and datetime facts, but it is not exhaustive. | BLOCKER; P2-R2-F3 | Shipped `n_distinct_folded` and `datetimes_read_at` have no disposition, allowing implementations to change folded grouping or datetime interpretation while every listed matrix check passes. |
| P2-R1-F12 | **Closed.** Lines 303, 390-392, and 664-665 require a rung-by-rung finite-sample envelope, fixed moment bounds, and ignore/permute/swap mutants. | None | A generator collapsing the nine interior rungs is now required to fail outside the frozen-vector tests. |
| P2-R1-F13 | **Partly closed.** Lines 618-628 state the right provenance qualification and its exact-allocation consequence, but the required repository-wide propagation omits canonical public surfaces. | BLOCKER; P2-R2-F7 | A one-column constant twin can equal every source row while `CLAUDE.md` and the package docstring retain categorical zero-record wording. |
| P2-R1-F14 | **Partly closed.** Lines 629-636 correctly classify twin and report as carrying real-derived published facts, but the approval consequence and all canonical documentation surfaces are not carried through. | BLOCKER; P2-R2-F7 | A user following the implementer brief sees only the profile singled out for governed handling and moves a twin containing a published label outside the authorized environment. |
| P2-R1-F15 | **Only appears closed.** Lines 516-533 fix names, placement, and input/output identity, but inherit replacement of any ordinary pre-existing target without proving ownership. | BLOCKER; P2-R2-F5 | A renamed valid profile can derive the name of an unrelated existing CSV, which the inherited transaction replaces and then discards after success. |
| P2-R1-F16 | **Partly closed.** Lines 108-117 correctly choose normalized identity and disclose case/edge-space loss, but the raw/folded count consequences are not carried into P2-D6. | BLOCKER; P2-R2-F3 | Two raw spellings that normalize to one published level cannot produce both the exact raw distinct count and literal normalized-label allocation under the stated rules. |
| P2-R1-F17 | **Only appears closed.** Removing `spawn` closes the dependency-floor conflict, but lines 688-717 still defer the exact Generator/writer method surface and contain a false account of bare from-import calls. | BLOCKER; P2-R2-F6 | Two scanner implementations can admit different randomness-consuming methods and both claim conformance, changing bytes and capability without a plan amendment. |
| P2-R1-F18 | **Closed.** Lines 559-606, 659, and 680-681 fix report bytes, one safe-display boundary, full-report goldens, and hostile-display fixtures. | None | The shipped display boundary covers line, control, and bidirectional formatting characters, and revision 1 requires its use on every interpolated source-derived value. |
| P2-R1-F19 | **Partly closed.** Lines 572-599 choose unchanged CSV cells, reject quoting as protection, require counting and unavoidable warnings, and lines 748-752 disclose the residual. The promised supported-spreadsheet behavior is not tested. | MAJOR; P2-R2-F13 | A spreadsheet import behavior can change while the ordinary CSV-reader tests stay green, leaving the hazard classification or warning claim unverified. |
| P2-R1-F20 | **Partly closed.** Lines 135-140 give direction-correct version advice, but lines 454-457 merely say the seed range is stated; no accepted set appears anywhere. | MAJOR; P2-R2-F11 | `--seed -1` can pass command parsing and reach a raw NumPy refusal because the plan never fixes the range the CLI must enforce. |
| P2-R1-F21 | **Closed, narrowly.** Lines 164-170 make the data-model examples non-exhaustive and include decorator application. | None | The specific implicit-call wording defect is closed. Revision 1's broader claim that all of P1-R8-F5 is repaired is separately false; see P2-R2-F14. |
| P2-R1-F22 | **Closed.** Lines 103-107 retain one-based positions and require producer-to-loader round trip. | None | This matches shipped `enumerate(..., start=1)` and removes the silent base migration. |

## Review items

### P2-R2-F1 — The boundary proof has no viable root for the real command

**Severity: BLOCKER.**

**Location:** revision 1 lines 60-91 and 673-675; `pyproject.toml` lines
33-34; `src/synthtwin/cli.py` lines 42-50; `src/synthtwin/profile.py` line 32.

The installed entry point is `synthtwin.cli:main`. That module imports the
table reader because the existing `profile` branch legitimately needs it.
Revision 1 instead says “generation entry point” without naming a root,
defining branch sensitivity, or specifying how calls through first-party
helpers are resolved. Its signature mutations do not cover work performed
before the checked function is called. The current profile serializer also
lives in a module that imports the table type, so the neutral move must cover
every helper generation needs, not only the transaction writer.

**Failure scenario:** the command validates `study-profile.json`, derives a
sibling table path, and calls `read_table` for a preview before invoking a
clean `generate(profile, seed)` function. A graph rooted at that lower
function and every stated signature mutation pass, yet real cells influence
the twin. A graph rooted at `cli.main` fails permanently because the separate
`profile` command's legitimate reader import is reachable. The plan therefore
offers no test that both accepts the product and enforces the boundary.

**Required closure:** name the installed command's generation dispatch as the
root; define a branch-sensitive import and call closure from argument parsing
through completed output; enumerate the allowed profile read and forbidden
table-reader targets; and require red mutations before, within, and after the
loader call, including aliases and re-exports. Identify every neutral helper
move needed to make that graph pass. The test must fail if any generate-path
layer accepts or constructs a table path, table handle, table object, or raw
cell collection.

### P2-R2-F2 — The datetime contract still contradicts D12

**Severity: BLOCKER.**

**Location:** Phase 0 D12 lines 448-460; revision 1 lines 318-326 and
393-395.

D12 fixes date/time output to ISO 8601 with explicit offset and fixed
precision. Revision 1 instead marks the recorded source `format` EXACT and
requires values to be written back in that format. UTF-8 and LF repair only
the surrounding bytes; they do not reconcile the cell representation. The
Line 324's universal quantifier also applies the format promise to the
`n_unparsed` construction on line 326, which cannot meet it.

**Failure scenario:** a valid profile records a month-first date format. A
conforming D12 implementation emits ISO values; a conforming P2-D6/P2-D7
implementation emits slash-separated month-first values. No output satisfies
both ratified requirements, so different implementers produce different
bytes and one contract always fails. With 99 parsed dates and one unparsed
cell, a neutral stand-in also cannot be a value in the recorded date format
while remaining counted as unparsed.

**Required closure:** either require D12's ISO representation and make source
format REPORT-ONLY, or ratify an explicit D12 amendment before this plan.
Define offset and precision serialization in the chosen representation and
state that unparsed stand-ins are outside the parsed-value format obligation.
Freeze both a non-ISO source-format vector and a mixed parsed/unparsed vector.

### P2-R2-F3 — The disposition matrix is incomplete and internally inconsistent

**Severity: BLOCKER.**

**Location:** revision 1 lines 263-350, 660-663, and 763-766;
`src/synthtwin/profile.py` lines 249-277 and 323-355;
`src/synthtwin/taxonomy.py` lines 2168-2187.

The matrix claims field-by-field coverage but omits the shipped universal
`n_distinct_folded` and datetime `datetimes_read_at`. It also does not give a
disposition to the top-level source evidence, settings, counts, publication
notes, or relationship block, nor define which of those are loader-only. The
omission matters: `header_by_convention` and `header_evidence` carry the
Phase 0 R1 uncertainty, but P2-D10 reports only whether a header was written.

The rows that are present conflict. Raw `n_distinct` is EXACT for
non-distribution roles, while normalized `levels` and their counts are EXACT
and raw variants are intentionally unavailable. For distribution roles, “at
most the profile target” is not the stated non-vacuous bound: it supplies no
lower bound and permits collapse to the endpoints.

**Failure scenario A:** a neutral column has eleven `North` values and eleven
`north` values. The shipped producer reports raw distinctness 2, folded
distinctness 1, and one normalized level with count 22. Literal normalized
emission has raw distinctness 1. Adding a second spelling preserves the
raw count but violates the decision not to preserve or invent raw variants.
Either result violates an EXACT row while looking plausible.

**Failure scenario B:** a numeric profile publishes 50 raw spellings that
parse to two endpoint values, with ladder and moments consistent with those
endpoints. A mutant emits only the two canonical endpoint spellings. Two is
“at most” 50, so the matrix and report accept a twin whose raw grouping
behavior has collapsed by a factor of 25.

**Failure scenario C:** a source's first row is taken as names only by
convention. Generation writes those strings as the header and reports merely
that a header was written. The user is not told that the strings may instead
be the first data row, despite the profile carrying that warning explicitly.

**Required closure:** derive an exhaustive matrix from every v4 key, including
top-level and per-role fields, and label metadata that is loader-only. Give
`n_distinct_folded`, `datetimes_read_at`, and the header evidence explicit
dispositions. Resolve raw-versus-normalized cardinality without adding
unpublished variants, and give approximate numeric distinctness a fixed,
two-sided, finite-sample bound. Add a schema-to-matrix completeness assertion
so a future field cannot arrive undisposed.

### P2-R2-F4 — Feasibility is deferred and valid producer output can become unusable

**Severity: BLOCKER.**

**Location:** revision 1 lines 352-366 and 666-669; sequencing lines 43-55.

Revision 1 correctly recognizes incompatible facts, but leaves the decisive
outcome of every check to the later method specification. “Relaxation” is not
one of the four dispositions. It can contradict a field already marked EXACT;
refusal can make a document accepted by the v4 contract unusable by its first
consumer. Placing generation capacity checks in “the loader” also conflates
schema validity with method feasibility: a contract-valid document should not
become syntactically unloadable because one generation method lacks capacity.

**Failure scenario:** Phase 1 emits a valid profile for 200 distinct,
one-character identifier values with singleton multiplicities. A later method
chooses a smaller neutral invention domain. Relaxing length violates the EXACT
length row; relaxing distinctness violates exact allocation; refusing leaves
a zero-code user with a valid profile and no action that can make it generate,
especially when the generation machine has no source table. Every outcome is
currently permitted, so artifact 3 can silently decide product scope.

**Required closure:** in this plan, enumerate each capacity/conflict check and
fix its outcome. If valid v4 documents may be generation-refused, define a
separate generation-feasibility stage, its compatibility promise, its plain
remediation, and its report/disclosure consequences; do not call the profile
invalid. Otherwise expand the deterministic invention domains to cover the
producer's full domain. Freeze genuine Phase 1 producer outputs for both
round-1 conflict cases and require producer-to-loader-to-generator tests.

### P2-R2-F5 — Output ownership still permits replacement of unrelated files

**Severity: BLOCKER.**

**Location:** revision 1 lines 516-533; `src/synthtwin/profile.py` lines
1209-1264, 1305-1307, and 1334-1342.

The new suffixes avoid the profiler's normal pair, and profile/output alias
checks protect the input profile. They do not establish ownership of an
existing twin or report target. The “shipped conservative rule” accepts any
ordinary file: the transaction moves the first aside, installs both outputs,
then removes the saved predecessor after success. The second target is
replaced directly. That rule is transactional, not an ownership proof.

**Failure scenario:** a canonical profile is renamed to
`study-profile.json` in a directory already containing an unrelated
`study-twin.csv`. A default generate run derives that exact CSV path, treats
the unrelated file as a previous product artifact, replaces it, and removes
the saved predecessor after success. The profile path remains untouched, so
all identity and two-target checks in revision 1 pass while unrelated data is
lost.

**Required closure:** refuse every pre-existing output unless positive,
verifiable synthtwin ownership is established, or require an explicit
overwrite action that names both exact targets and warns what will be
replaced. Define first- and second-target behavior symmetrically. Add a test
with a valid renamed profile and unrelated ordinary files at each derived
target; the default run must leave every byte unchanged.

### P2-R2-F6 — E7-E9 remain deferred and one scanner premise is false

**Severity: BLOCKER.**

**Location:** Phase 0 D6.2; revision 1 lines 688-717;
`tools/offline_scan/scan_imports.py` lines 510-591, 713-744, 2891-2912,
and 3245-3248.

Revision 1 says the exact enumeration is “settled” in later contract and
method specifications, then leaves the Generator methods and writer methods
unnamed. That is the same plan-level deferral round 1 rejected. The current
scanner has no NumPy or writer capability to inherit. Revision 1 also says a
bare from-imported allowed API remains refused by the callback rule. The
scanner actually binds an allowed from-import as kind `api`, and a bare call
to an `api` binding is accepted. Callback-slot handling is a separate check.

**Failure scenario:** one implementation permits only `Generator.random`;
another adds `choice`, `permutation`, and `shuffle`, with arrays flowing
through different operations before conversion. Both satisfy “enumerated in
the method specification,” yet consume different draw counts and expose
different native-backed capabilities. A red mutation based on the asserted
bare-call refusal passes or fails for the wrong reason, so the reviewed policy
does not match the enforced one.

**Required closure:** enumerate in this ratified plan every E7-E9
constructor, returned type, instance method, argument origin/form, callback
slot, output handle, array operation, and result-origin propagation rule.
Name the writer's callable methods and the allowed row value origins. Correct
the from-import account and require red mutations for dotted and bare forms,
stored aliases, methods, arrays, callbacks, and unlisted output handles.

### P2-R2-F7 — Provenance and handling repairs omit canonical surfaces and the approval consequence

**Severity: BLOCKER.**

**Location:** revision 1 lines 618-636 and 777-779; `CLAUDE.md` lines
13-16, 55-58, and 74-77; `src/synthtwin/__init__.py` lines 1-4.

P2-D11 contains the right facts, but acceptance requires updates only to
README, SECURITY.md, command help, and reports. The canonical implementer
brief and the package's public docstring retain categorical record claims;
the brief also applies institutional handling only to the profile. Revision 1
says all three artifacts carry the institutional rule but never carries
round 1's explicit approval warning into an acceptance assertion.

**Failure scenario:** an 11-row, one-column constant profile forces all 11
twin rows to equal the source rows. An implementer follows `CLAUDE.md`, leaves
the categorical claim in package documentation, and a user treats the twin
as outside the institution's approval process because only the profile is
called governed material there. The exact published value leaves the authorized
environment even though P2-D11 knew the consequence.

**Required closure:** require a repository-wide claim and handling inventory,
including `CLAUDE.md`, package/module docstrings, README, SECURITY.md, command
status/help, reports, and any generated metadata. State for all three
artifacts that institutional handling and approval requirements apply and
that synthtwin supplies no formal privacy guarantee. Add exact assertions
that reject the old categorical wording and profile-only handling wording on
every public surface.

### P2-R2-F8 — EXACT validation asks CSV bytes to prove metadata they do not contain

**Severity: BLOCKER.**

**Location:** revision 1 lines 271-277, 290-297, 566-570, 660-663, and
763-766.

EXACT is defined as independently recounted from the twin, and acceptance
requires every EXACT field to be recounted from written CSV. Yet `role`, the
three axes, and sometimes `name` are not facts encoded in CSV cells. A
headerless output has no field names at all. Position is a mapping convention,
not a statistic that can be independently inferred from bytes. Copying these
values from the input profile is not an independent recount and cannot detect
misrouting.

**Failure scenario:** a headerless declared identifier profile is routed
through the free-text method, but the output happens to match its row and
distinct counts. A validator that copies `role`, axes, name, and position from
the profile reports every EXACT field passed; a validator that truly reads
only the CSV cannot recover those fields and rejects correct output. The
acceptance criterion is either tautological or impossible.

**Required closure:** split EXACT into output-observable quantities and exact
metadata/control decisions. Define the independent evidence source and a
failing mutant for each: CSV recount for observable statistics, serialized
header bytes only when present, schema-order assertions for positions, and
dispatch/typed-object assertions for role and axes. Rewrite acceptance so it
never claims CSV proves absent metadata.

### P2-R2-F9 — A valid leading U+FEFF header breaks the exact-name/no-marker contract

**Severity: BLOCKER.**

**Location:** revision 1 lines 296 and 553-570;
`src/synthtwin/reading.py` lines 388-401, 626-640, and 758-762.

Phase 1 can validly publish a first column name whose first character is
U+FEFF when that character occurs inside a quoted first field: the source
bytes begin with the quote, so the character is content rather than a file
marker. The reader's explicit marker check runs only on its Latin-1 byte view.
Revision 1 requires the name EXACT, no byte-order marker, and minimal CSV
quoting. Minimal quoting does not quote this otherwise ordinary name.

**Failure scenario:** a UTF-8 source begins with a quoted header whose content
is U+FEFF followed by `measure`, then contains two numeric rows. Phase 1
accepts it and publishes the full name with `header_source` from the file.
Generation writes that exact unquoted name first. The twin now begins with
the UTF-8 marker byte sequence, violating the no-marker rule; reopening it
through the same `utf-8-sig` path consumes U+FEFF and silently changes the
column name to `measure`.

**Required closure:** define a canonical exception that forces quoting for a
leading U+FEFF first header, or explicitly refuse that valid producer case and
record the compatibility cost. Test exact bytes and a full
profile-to-twin-to-reader round trip. The test must prove both that the stream
has no leading marker and that the recovered name is byte-for-byte the
published name.

### P2-R2-F10 — Canonical loading has uncatalogued exceptions and no resource bounds

**Severity: MAJOR.**

**Location:** revision 1 lines 132-162 and 608-614.

Plain `json.loads` plus canonical reserialization is a sound duplicate-key
construction, but the plan specifies only its success logic. Invalid UTF-8,
escaped lone surrogates, non-finite numbers accepted by the parser, excessive
nesting, and oversized arrays/maps can fail during decoding, serialization,
or allocation rather than at the listed parse/schema boundary. The catalog's
memory message names `n_rows`, which is unavailable if allocation fails before
the document is validated.

**Failure scenario:** a local document contains `1e999` for a numeric key.
Python parses it as a non-finite float; canonical serialization with
`allow_nan=False` raises `ValueError` before the schema check. A conforming
implementation that follows only the listed catches exposes a traceback
instead of the promised plain non-canonical/schema refusal. A deeply nested
document can similarly exhaust parser resources before a trustworthy row
count exists.

**Required closure:** fix maximum input bytes, nesting depth, container size,
and string size before implementation; define strict UTF-8 decoding; and map
every decode, parse, canonical-encode, recursion, and allocation failure to a
tested plain-language error that does not rely on unvalidated fields. Add one
mutation for each boundary and a near-limit valid document.

### P2-R2-F11 — The seed contract is unstated and the sensitivity test is overbroad

**Severity: MAJOR.**

**Location:** revision 1 lines 438-457, 512-514, and 670-672.

The plan promises an accepted range but supplies no endpoints or predicate.
The installed NumPy accepts nonnegative integers, including integers much
larger than 64 bits, and rejects negative integers. Implementers can therefore
adopt different CLI acceptance rules without violating this text.
The determinism battery also requires every different seed to change interior
values, but some valid profiles have no random degree of freedom.

**Failure scenario A:** `--seed -1` reaches `default_rng` on one implementation
and exposes its raw exception; another refuses it cleanly; a third wraps it
modulo 64 bits. Revision 1 does not distinguish the three.

**Failure scenario B:** an all-absent one-column profile or a one-column exact
constant profile has no interior values that may change. The correct output
is identical at seeds 0 and 1. The stated battery either rejects a correct
generator or encourages a spurious draw/value change that violates exact
allocation.

**Required closure:** state one exact seed domain and parsing rule, with lower
and upper bounds if any, and freeze boundary tests. Qualify seed sensitivity
to fixtures with at least one genuinely random interior degree of freedom;
also require seed invariance for fully determined fixtures.

### P2-R2-F12 — The P1-R8-F6 publication guard is still an implementation choice

**Severity: MAJOR.**

**Location:** revision 1 lines 164-173 and 727-728; Phase 1 round-8 review
P1-R8-F6.

Revision 1 claims P1-R8-F6 is repaired, but says the existing comments are
corrected to a manually bounded property “or” the check becomes a recursive
finished-document whitelist. Those mechanisms make materially different
future-change guarantees. Deferring the choice to artifact 2 does not close a
plan item whose required closure expressly demanded one mechanism in this
revision.

**Failure scenario:** a future producer field places a source spelling in
`publication_notes`. The manual guard still inspects only the existing three
substructures and the document ships; the recursive guard refuses it. Both
implementations conform to the unresolved “or,” so a claimed fail-closed
publication boundary depends on an unratified later choice.

**Required closure:** choose one mechanism now. If manual, enumerate every
covered and uncovered route and correct the fail-closed claim; if recursive,
define the finished-tree traversal, allowed leaf classes, nested-container
behavior, and a mutation in each currently adjacent route. Artifact 2 may
specify details but may not choose the security property.

### P2-R2-F13 — The formula-context battery does not test the supported spreadsheet behavior

**Severity: MAJOR.**

**Location:** revision 1 lines 572-599 and 682-686; round-1
P2-R1-F19 required closure.

The unchanged-cell decision, warning, count, and residual are explicit.
However, revision 1 says its tests cover both reader classes from round 1 and
then names only an ordinary CSV parser, the internal counter, and warning
goldens. It names no supported spreadsheet, version, import path, or expected
cell behavior. The policy's claim about spreadsheet interpretation is
therefore not tested by the battery that purports to close it.

**Failure scenario:** a supported spreadsheet release changes how a quoted
cell beginning with one listed character is imported. The ordinary CSV parser
still returns the literal text, the counter still fires, and every stated test
passes, but the product's warning and hazard count no longer describe what
that supported spreadsheet does. A zero-code user cannot tell which behavior
was actually verified.

**Required closure:** name the supported spreadsheet reader(s), version or
version policy, import settings, and a reproducible verification for each
listed leading character in both header and data positions. If such behavior
cannot be tested in CI, narrow the claim to unverified risk and make that
limitation explicit; do not say both reader classes are covered.

### P2-R2-F14 — The plan overclaims closure of P1-R8-F5

**Severity: MINOR.**

**Location:** revision 1 lines 164-170 and 727-728; `SECURITY.md` lines
70-92 and 119-139; `docs/plans/phase-1-profiler.md` lines 200-213.

The implicit-call wording is repaired, but other contradictions named by
P1-R8-F5 remain outside the plan's required edits. `SECURITY.md` still states
generically that attributes on enumerated-library results are enumerated,
although standard-library `Path` instances have a broader data-only surface;
it also counts two run-time controls where round 8 required counting only
immediate validation. The Phase 1 plan still says no other pandas API can
appear, a stronger statement than the name-level scanner property.

**Failure scenario:** a reviewer adds an allowed `Path` instance operation
and expects the scanner to refuse it because the security text describes the
restricted pandas rule as generic. The scan stays green, and the reviewer
mistakenly concludes the enforcement regressed or that the documented audit
surface was complete.

**Required closure:** enumerate every text location named by P1-R8-F5 in this
plan's documentation gate, distinguish standard-library and restricted
third-party instances, count only immediate validation as the run-time reader
control, and assert the corrected sentences.

### P2-R2-F15 — The review record and internal references are inaccurate

**Severity: MINOR.**

**Location:** revision 1 lines 3-4, 106, 136, 165, 222, 455, and 826-829.

Round 1 named seventeen blockers: P2-R1-F1 through F15, F17, and F19.
Revision 1 twice says fifteen. Several body references shifted after the late
item was inserted: position is F22 rather than F21; version advice is F20
rather than F19; implicit forms are F21 rather than F20; the seed reference is
F20 rather than F19. The width residual is P2-D14/R-P2-1, not P2-D13. The
mapping table at lines 799-824 is correct, which makes the conflicting body
references more likely to mislead a later audit.

**Failure scenario:** a later reviewer follows the body cross-reference for
the seed repair, reads the formula-context item instead, and marks F20 closed
without checking the missing seed domain. The closure ledger then reports two
fewer original blockers and an unresolved contract enters implementation.

**Required closure:** change both blocker counts to seventeen and reconcile
every body citation with the final mapping table. Add a simple review-ID
reference check or a manual acceptance checklist covering all 22 identifiers.

## What was checked

### Surfaces

- Every revision-1 decision P2-D1 through P2-D14, sequencing, acceptance
  criteria, owner-decision record, residual, and the claimed F1-F22 mapping.
- The complete shipped v3 profile shape: top-level, source/settings,
  universal fields, role-specific fields, axes proposed for v4,
  multiplicities, and the reserved relationship block.
- The shipped producer's flat keys, one-based positions, canonical JSON,
  normalized labels, raw/folded counts, datetime clock metadata, header
  evidence, and publication routes.
- The real command entry point, imports, reader boundary, path inputs,
  neutral-helper proposal, output naming, pre-existing-target behavior,
  aliases/links, two-file transaction, and error catalog.
- D12 serialization and RNG rules, NumPy construction, seed behavior,
  draw-order promises, special-element placement, CSV dialect, report bytes,
  and the new formula-context policy.
- E7-E9 against the shipped scanner's module/API bindings, callback slots,
  restricted instances, result propagation, writer absence, and bare versus
  dotted calls.
- Public provenance, disclosure, handling, approval, first-row uncertainty,
  formal-privacy, and deferred-governance claims across the required baseline
  and package documentation.

### Properties and attack classes

- Producer/loader compatibility, unknown and duplicate keys, canonical form,
  malformed encoding/numbers, range/count/sum invariants, resource bounds,
  and schema-to-disposition completeness.
- Silent statistical wrongness from raw/folded identity, numeric equality,
  approximate-distinct collapse, datetime clock/format drift, integer
  misrouting, unparsed stand-ins, absent-class loss, and infeasible exact
  allocations.
- Direct and transitive table access, pre-dispatch reads, first-party aliases
  and re-exports, callback and implicit execution, native-backed capability
  growth, returned-object methods, and output-handle provenance.
- Single-stream determinism, draw-count coupling, sorted iteration, seed
  domain, fully determined profiles, platform/version boundaries, UTF-8/LF,
  terminal newline, marker handling, and exact header recovery.
- Destructive replacement, path/link/alias collision, input/output identity,
  first/second-target asymmetry, rollback inheritance, and actionable
  zero-code failures.
- Forced row equality, real-derived published values, normalized identities,
  handling/approval propagation, report display integrity, spreadsheet
  interpretation, and actual-file content-gate coverage.

### Checks that did not produce review items

- Flat role keys and one-based positions match the shipped producer.
- Canonical parse/serialize/byte-compare is a viable duplicate-key defense and
  is stronger than duplicate detection alone, once its error/resource
  boundary is specified.
- The single sequential stream, schema-order draw consumption, and fixed
  placement of special elements now conform to D12.
- The three additive axes are deterministic restatements of existing facts;
  the dispatch decision is carried consistently.
- The two new anonymous multiplicity maps retain the intended count-only
  publication class and their two sum invariants are stated.
- The all-null relationship shape is closed to premature content and adds no
  real-derived facts in this phase.
- Width fidelity for unrepresentable numbers is now honestly withdrawn, with
  the existing sign and whole/fraction fields retained and a named residual.
- The rung envelope and required mutants are non-vacuous plan requirements.
- Header presence correctly follows `source.header_source`; the remaining
  defects concern uncertainty disclosure and exact leading-name bytes.
- The report's UTF-8/LF/display boundary and complete-report golden contract
  are specified coherently.
- The formula-context choice itself is explicit and honestly says unchanged
  cells remain hazardous; the item above concerns the missing verification
  surface, not a reopening of that choice.
- Revision 1 preserves the repository's temporarily-private/deferred-control
  distinction and does not claim Phase 2 code already exists.

### Verification performed and limits

- `.venv/bin/python -m pytest -q tests/test_profile_document.py
  tests/test_offline_scan.py tests/test_decontamination.py`: 194 passed.
- `.venv/bin/python tools/offline_scan/scan_imports.py src`: 9 Python files,
  0 violations.
- A producer probe with eleven instances of each of two case variants
  confirmed `n_distinct = 2`, `n_distinct_folded = 1`, and one normalized
  published level of size 22.
- A valid quoted-header probe confirmed that Phase 1 accepts a leading U+FEFF
  as name content and that minimal UTF-8 CSV output moves its bytes to the
  start of the file, where `utf-8-sig` consumes them on re-read.
- NumPy 2.5.1 refused `-1`, accepted `0`, and accepted nonnegative integers
  much larger than 64 bits as seeds.
- Revision 1 was copied byte-for-byte to a non-Git temporary root, verified
  with `cmp`, and scanned clean. This made the scanner read the plan instead
  of relying on the real repository index, where the plan is untracked.
- This review file was checked the same way: exact byte-copy, `cmp`, then a
  clean scan over the non-Git root. No staging claim is made.
- This remains a paper review. The v4 contract, method specification,
  vectors, and implementation do not exist and could not be reviewed. The
  live host was macOS; other-platform behavior was checked against the
  ratified requirements rather than executed locally.

## Verdict

**REJECT.** The blocking items are **P2-R2-F1 through P2-R2-F9**. Revision 1
may not be ratified, and no Phase 2 method or implementation may begin, until
those items are closed in a revised plan. P2-R2-F10 through P2-R2-F15 are
also required repairs; they do not authorize deferral of loader safety, seed
semantics, publication enforcement, spreadsheet verification, documentation
accuracy, or review traceability into implementation.

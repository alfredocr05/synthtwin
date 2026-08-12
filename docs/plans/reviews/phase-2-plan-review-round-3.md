# Phase 2 plan review, round 3

**Reviewed:** 2026-08-10

**Plan:** `docs/plans/phase-2-generator.md`, revision 2

**Review type:** plan-only ratification gate; no Phase 2 implementation exists

## Outcome

Revision 2 makes several real decisions. It closes output ownership, the
repository-wide claim inventory, the observable/control evidence split, the
leading-U+FEFF header case, and the overstated spreadsheet test claim. It also
preserves all eight round-1 closures that round 2 accepted.

It does not decide every mechanism it says it decides. Five of the fifteen
round-2 items close fully; ten remain partly or wholly open. Six defects still
block ratification: the boundary excludes module initialization, the scanner
extension lacks returned-object and output-handle provenance, the datetime
contract is impossible for genuine offsetless and quarter profiles, the
disposition matrix contradicts real producer shapes, the numeric conflict has
no fixed feasibility outcome, and the identifier-length fidelity relaxation
lacks the owner authorization the prior review required.

## Review basis and method

I read the complete required baseline: `CLAUDE.md`, `AGENTS.md`,
`SECURITY.md`, the Phase 0 public-skeleton plan (including D6.2 and D12), the
Phase 1 profiler plan at revision 5, the Phase 1 round-8 review, and both prior
Phase 2 plan reviews. The mapping table at the end of revision 2 was treated as
a set of claims; every closure judgment below was re-derived from the plan and
the repository.

Producer, writer, reader, and scanner claims were checked against
`src/synthtwin/profile.py`, `taxonomy.py`, `reading.py`, `parsing.py`,
`cli.py`, and `tools/offline_scan/scan_imports.py`. I ran neutral producer
probes for empty, constant, numeric-conflict, date-only, and quarter columns;
a quoted leading-U+FEFF reader and neutral CSV-serialization probe; direct
scanner probes; the focused regression suite; the shipped offline scan; and an
exact-copy content scan of revision 2.

The four decisions in “Decisions taken at planning” and the inherited owner
decisions are treated as settled. This review tests whether their consequences
are carried consistently. It does not reopen those choices.

## Closure of every round-2 item

The last column records the independent closure check. For an open item it
also gives a specific surviving failure scenario. “None” means the round-2
item is no longer live.

| Round-2 item | Judgment | Remaining severity | Independent closure check |
|---|---|---:|---|
| P2-R2-F1 | **Partly closed.** Lines 64-88 now name the generate dispatch, branch sensitivity, allowed and forbidden sets, neutral helper moves, and before/within/after mutations. The checked extent still starts only after argument parsing selects `generate`; module initialization is outside it. | BLOCKER; P2-R3-F1 | The installed entry point imports `reading` and `read_table` unconditionally at `cli.py:42-50` before `main` reaches dispatch. A module-level mutation that reads `preview.csv` and caches a count runs before both named regions; the post-dispatch closure and parser-prologue check can remain green while that count changes the twin. |
| P2-R2-F2 | **Partly closed.** Source `format` is now REPORT-ONLY and the non-ISO and mixed parsed/unparsed vectors are real repairs. Explicit-offset output is still incompatible with valid producer output. | BLOCKER; P2-R3-F4 | A genuine 33-row date-only profile emitted date precision and `utc_offsets: {"(none)": 33}`; a quarter profile did the same at quarter precision. Adding an offset changes the exact offset and precision facts; omitting it violates lines 529-543 and D12. |
| P2-R2-F3 | **Partly closed.** Revision 2 adds the five dispositions, header evidence, raw/folded label and invention rules, two-sided numeric language, and a completeness assertion. The written matrix still does not match all real shapes. | BLOCKER; P2-R3-F5 | Real empty, constant, and datetime blocks omit per-column `n_rows` although lines 275-280 call it universal; every empty block still emits both distinctness fields, but “empty” belongs to none of the three role groups at lines 284-285. A matrix-derived validator must reject genuine output or invent an unratified exception. |
| P2-R2-F4 | **Partly closed.** A separate post-load feasibility stage, valid-profile wording, fixed length-first rule, and genuine producer fixtures are substantive repairs. The original numeric conflict still has no named result, and the length relaxation lacks its required owner decision. | BLOCKER; P2-R3-F6 and P2-R3-F7 | The genuine values `0, 0.0, ... 49, 49.0` publish 100 present and raw-distinct cells, whole-number status, endpoints 0 and 49, and two zeros. Lines 354-390 choose neither canonical single-spelling output, invented raw spelling variants, relaxation, nor generation refusal, yet acceptance says this fixture receives the outcome the plan names. |
| P2-R2-F5 | **Closed.** A default run refuses either existing target, names both paths, and only `--replace` authorizes replacement; the rule and test are symmetric. | None | Inspection of `profile.py:1209-1264,1305-1337` confirmed why the repair is needed: the current transaction replaces ordinary targets. Lines 505-516 now put the ownership decision before that transaction and require unrelated bytes to remain unchanged. |
| P2-R2-F6 | **Partly closed.** The bare-import premise is corrected and the names `default_rng`, `integers`, `csv.writer`, `writerow`, and `writerows` are fixed. Required result-origin, returned-type, argument-form, attribute, and output-handle rules are still missing. | BLOCKER; P2-R3-F2 | The real scanner accepted a bare `dumps(...)` call after `from json import dumps`. After adding only the proposed NumPy and writer names in memory, it also accepted an `integers` result followed by `draws.ctypes` and accepted `csv.writer(handle).writerows(rows)` where both arguments were caller-derived. The listed red mutations do not reach either route. |
| P2-R2-F7 | **Closed.** Lines 604-621 and 751-754 cover `CLAUDE.md`, package and module docstrings, README, SECURITY, help/status, reports, and generated metadata; they apply handling and approval to all three artifacts and reject categorical record and profile-only handling wording. | None | The current stale statements at `CLAUDE.md:13-16,74-77` and `src/synthtwin/__init__.py:1-6` are both inside the named gate. The `CLAUDE.md` change is correctly identified as charter text. |
| P2-R2-F8 | **Closed.** EXACT-OBSERVABLE and EXACT-CONTROL now have different evidence sources and mutation obligations. | None | Lines 226-239, 279-320, and 738-741 require CSV recount for observable facts and typed/schema-order dispatch evidence for controls. The declared-identifier misrouting mutant can fail without pretending a headerless CSV encodes role, name, or position. |
| P2-R2-F9 | **Closed.** The plan fixes a canonical forced-quoting rule and exact-byte/no-marker/reader-round-trip tests. | None | The shipped reader preserved a first name beginning U+FEFF from a real quoted source. Neutral CSV serialization showed that minimal bytes began with the marker sequence and lost the character through the same reader, while forced-quoted bytes began with a quote and preserved the exact name. Lines 546-557 now require the latter properties. |
| P2-R2-F10 | **Partly closed.** Decode, parse, canonicalization, recursion, and allocation failures are catalogued without relying on unvalidated `n_rows`. The actual resource contract remains deferred and incomplete. | MAJOR; P2-R3-F8 | Lines 128-135 fix no byte or depth number and no container or string limit. A prospective v4 document for a table within the shipped producer's accepted domain can be accepted under one later cap and refused under another, so revision 2 still does not define producer/loader compatibility. |
| P2-R2-F11 | **Partly closed.** The numeric set `0..2**64-1` is fixed and sensitivity is correctly scoped to a fixture with random freedom. The parsing grammar, boundary battery, and fully determined invariance check remain absent. | MAJOR; P2-R3-F9 | `--seed 1_0` can be accepted as ten by Python-style parsing and refused by an ASCII-decimal parser. Both fit “integers” in lines 437-442. A seed-dependent quoting mutant on an all-absent twin also escapes the one scoped sensitivity check. |
| P2-R2-F12 | **Not closed.** Revision 2 chooses recursion, but applies it to the same incomplete structural scope. | MAJOR; P2-R3-F3 | The shipped producer builds `publication_notes` separately at top level after `_column_block`. A future note containing a source spelling bypasses a recursive check over only the finished column mapping and is serialized without adding a key that the matrix-completeness test could notice. |
| P2-R2-F13 | **Closed.** The plan now says no spreadsheet is executed and limits the battery to exact ordinary-reader recovery, hazard counts, and warnings. | None | Lines 576-589 no longer make a product/version-specific spreadsheet claim that the named tests cannot verify. |
| P2-R2-F14 | **Partly closed.** The SECURITY and Phase 1 plan corrections are named, but the scanner docstring's false accepted-built-in sentence and an assertion over its correction are absent. | MINOR; P2-R3-F10 | Implementing lines 153-163 can leave `scan_imports.py:477-482` saying most accepted built-ins never invoke an argument. `hash(value)` scans clean but invokes the value's protocol, so a reviewer can incorrectly conclude enforcement regressed. |
| P2-R2-F15 | **Partly closed.** The blocker counts are corrected. The required all-22 round-1 reference checklist is absent, and the body's P2-R2-F6 citation on the datetime/byte heading is ambiguous because that paragraph does not answer the scanner item. | MINOR; P2-R3-F11 | A later reviewer following the F6 citation at line 529 can inspect datetime bytes rather than E7-E9 and mark the scanner repair closed. The table at lines 780-796 covers only the fifteen round-2 identifiers and cannot catch that drift. |

## Recheck of round-1 items previously judged closed

Revision 2 did not reopen any of the eight round-1 items that round 2 judged
closed. Adjacent new defects are kept under their round-3 identifiers rather
than being used to rewrite the prior record.

| Round-1 item | Judgment | Remaining severity | Independent closure check |
|---|---|---:|---|
| P2-R1-F1 | **Closed; not reopened.** Lines 755-757 retain the index-only limitation and tracked-file requirement. | None | An exact byte-copy of revision 2 was verified with `cmp` in a non-Git temporary root and scanned clean there. The repository plan is currently untracked, so I did not claim the no-argument gate reads it. |
| P2-R1-F3 | **Closed; not reopened.** Plain JSON parsing, canonical serialization, and exact byte comparison remain fixed at lines 121-127. | None | A duplicated key collapses during plain parsing and cannot reproduce its input bytes; no callback slot is required. |
| P2-R1-F5 | **Closed; not reopened.** Lines 420-448 retain one Generator, explicit threading, schema-order consumption, fixed special placement, and no child streams. | None | The topology matches D12 at `phase-0-public-skeleton.md:433-447` and does not restore unrelated-column invariance. |
| P2-R1-F9 | **Closed; not reopened.** Width fidelity for numeric-unrepresentable values remains withdrawn and disclosed at lines 188-197 and 714-715. | None | The plan makes no attempt to recover an unpublished width and flags any future width publication for owner review; two profiles differing only in hidden width may intentionally generate the same canonical shape. |
| P2-R1-F12 | **Closed; not reopened.** Rung-specific envelopes and ignore/permute/swap mutants remain required. | None | Lines 294, 395-405, and 650-652 still make an endpoints-only or reordered-rung implementation fail independently of golden hashes. |
| P2-R1-F18 | **Closed; not reopened.** Complete report bytes, one display boundary, hostile fixtures, and report goldens remain fixed. | None | Lines 529-574, 647-649, and 662-667 point to the shipped `parsing.visible` boundary; focused display/profile tests passed. |
| P2-R1-F21 | **Closed narrowly; not reopened.** The implicit-call examples remain non-exhaustive and decorator application remains named. | None | Lines 153-163 distinguish this narrow repair from the still-open P1-R8-F5 documentation propagation item. |
| P2-R1-F22 | **Closed; not reopened.** One-based positions and a producer/loader round trip remain fixed. | None | Lines 92-96 match the shipped `enumerate(..., start=1)` at `profile.py:311`. |

## Review items

### P2-R3-F1 — The branch-sensitive boundary omits process-start module initialization

**Severity: BLOCKER.**

**Location:** revision 2 lines 55-88 and 656-659;
`src/synthtwin/cli.py:42-50,605-625`.

The plan starts its checked region where parsing selects `generate` and checks
the shared parser prologue separately. Importing `synthtwin.cli` happens before
both regions. The current module unconditionally imports the table reader
because the profile command needs it.

If top-level imports and their initialization are included, the current graph
reaches the expressly forbidden `reading` module and cannot pass. If they are
excluded because they precede dispatch, module-level work is outside the
boundary. Naming “imports” reachable from the selected branch does not resolve
that fork: Python executes the unconditional import before any branch exists.

**Failure scenario:** a module initializer validates a local
`preview.csv`, reaches `read_table` through a re-export, and caches its row
count. The later generate dispatch uses that global as a default allocation
size. All before/within/after-loader mutations inside `main` and every
generation-layer signature test pass, but changing real table cells changes
the twin.

**Required closure:** include module initialization from installed-entry-point
startup in the checked extent, or split/lazily import commands under a rule
that proves the generate invocation initializes no reader-bearing module. Add
a module-initializer red mutation in addition to the command-prologue mutation.

### P2-R3-F2 — E7-E9 still omit capability-bearing provenance rules

**Severity: BLOCKER.**

**Location:** revision 2 lines 669-704; Phase 0 D6.2;
`tools/offline_scan/scan_imports.py:510-591,713-744,799-899,2137-2197,
3250-3284,3351-3373`.

The enumeration now fixes method names, but D6.2 granularity includes the
constructor's returned type, method result, argument origins, attributes,
callback slots, and output handle. Revision 2 states desired behavior for some
of those without fixing a scanner rule that enforces it.

The current scanner records a direct allowed API call as an instance. It does
not propagate an instance-method result as a restricted-library value.
Restricted methods and restricted attributes are also separate, library-keyed
tables. Consequently, adding only the names revision 2 gives does not establish
that an `integers` array has no attribute surface. For the writer, no rule
requires the constructor's handle to be the transaction-owned, locally
validated target, and no origin rule proves that `writerows` receives an
iterable of first-party text rows. Revision 2 says the dialect slot is governed
by the existing callback rule, but the current callback table enumerates
`csv.reader`, not `csv.writer`. The generic callable-argument check rejects
direct functions and lambdas, not caller-derived data objects.

**Failure scenario:** a generate helper accepts `handle` from its caller and
passes it to `csv.writer`. The constructor invokes the object's write protocol,
so output can go somewhere other than the transaction target. In the same
minimal policy extension, `draws = rng.integers(..., size=3)` followed by
`draws.ctypes` scans clean because the result origin is lost. None of the
listed unrecognized-method, array-method, module-attribute, writer-method, or
dialect-slot mutations targets either route; a caller-derived dialect also
scans clean under only the named E9 additions.

**Required closure:** enumerate distinct Generator, scalar, array, and writer
result origins; their allowed attributes (including an empty set where that is
the policy); every `integers` and row argument form; conversion to first-party
integers; the transaction-owned output-handle origin; and propagation at each
call. Add red mutations for a lost array origin, an unlisted attribute, a
caller-derived row source, and an unlisted/caller-derived handle. Also withdraw
the existing-rule claim unless a `csv.writer` callback-slot entry and its
positional and keyword forms are explicitly added. Also withdraw
the claim at lines 687-688 that use of `integers` makes vectors independent of
NumPy distribution behavior: `integers` is itself the retained random-number
operation; first-party post-processing removes only the additional surfaces.

### P2-R3-F3 — The recursive publication guard still misses a shipped route

**Severity: MAJOR.**

**Location:** revision 2 lines 143-151 and 263-265;
`src/synthtwin/profile.py:241-277,309-355`.

The chosen recursion covers the completed column mapping. The shipped producer
does not place every column-originating publication route in that mapping:
`build_document` lifts `described.publication_notes` into a separate top-level
list after `_column_block` returns. Calling that key LOADER-ONLY in the
generator disposition does not make the producer-side publication guard cover
it.

**Failure scenario:** a future no-value-publication role adds a diagnostic note
that interpolates one source spelling. The completed column mapping passes the
recursive whitelist, then `build_document` copies the note to top-level
`publication_notes`. No new key is added, so the matrix completeness assertion
also stays green while the spelling is serialized.

**Required closure:** apply the recursive whitelist to the finished document
tree, including top-level notes, or define an equally fail-closed separate
guard for that route. Fix allowed leaf classes, path-sensitive classes,
nested-container behavior, and one mutation for each adjacent route named by
P1-R8-F6.

### P2-R3-F4 — Explicit-offset datetime output cannot preserve genuine profiles

**Severity: BLOCKER.**

**Location:** Phase 0 D12 at `phase-0-public-skeleton.md:456-460`;
revision 2 lines 310-320, 392-406, 529-544, and 723-725;
`src/synthtwin/taxonomy.py:2026-2051,2105-2187`.

Demoting source `format` correctly removes the old slash-versus-ISO
contradiction. Revision 2 then marks resolution, precision, endpoints, offset
counts, and endpoint offsets EXACT-OBSERVABLE while requiring every parsed
datetime cell to carry an explicit offset. The producer legitimately emits
offsetless date, datetime, and quarter facts: `_offset_counts` publishes their
empty offset as `(none)`.

The probe over 33 date-only cells emitted `resolution: date`,
`time_precision: date`, both endpoint offsets `(none)`, and
`utc_offsets: {"(none)": 33}`. Forty quarter cells emitted quarter precision,
`2024-Q1`/`2024-Q4` endpoints, and the same offset map. A quarter is not an
offset-bearing instant in the representation the plan names.

**Failure scenario:** writing `2024-01-01T00:00:00+00:00` satisfies the
explicit-offset sentence but re-profiles as offset-bearing datetime precision,
not an offsetless date. Writing `2024-01-01` preserves the published facts but
violates D12 and P2-D10. No output satisfies both sets of exact obligations.

**Required closure:** define a representation for every producer precision and
offset state, including `(none)` and quarter, then reconcile it with D12 before
ratification. If D12 literally requires offsets on date-only and quarter
values, an owner amendment is required. Expand R-P2-7: the current statement
understates the cost as only a source-format argument change, while the present
rule also changes naive/aware behavior and cannot represent quarter precision.

### P2-R3-F5 — The exhaustive disposition matrix contradicts the producer

**Severity: BLOCKER.**

**Location:** revision 2 lines 101-111, 241-352, and 634-652;
`src/synthtwin/profile.py:241-277,323-355`;
`src/synthtwin/taxonomy.py:1998-2023,2105-2187`.

Revision 2 correctly records at lines 110-111 that per-column `n_rows` appears
only in numeric blocks, then declares it universal at lines 275-280. Real
empty, constant, and datetime probes had no per-column `n_rows`; the count
block did.

The role partition for `n_distinct` and `n_distinct_folded` also omits
`empty`, although `_column_block` emits both fields on every role. Datetime
cardinality is ambiguous: line 261 sends “distribution roles” to a row below,
but that distinctness envelope sits under the heading “Numeric roles (count,
continuous).” One implementation can apply the bound to datetime while
another excludes it.

**Failure scenario:** the v4 producer retains the shipped empty block with
`n_distinct = n_distinct_folded = 0` and no per-column `n_rows`. A validator
generated from the universal row refuses that genuine profile for a missing
key; one that silently exempts the role has implemented a rule absent from the
ratified matrix. Separately, a 50-date profile can collapse to a few dates
without any datetime cardinality bound to test.

**Required closure:** derive and print the matrix from each genuine per-role
producer shape, distinguish document row count from the numeric detail echo,
and add explicit empty and datetime cardinality dispositions and bounds. The
completeness test must first pass against the ratified matrix itself, not add
exceptions while being implemented.

### P2-R3-F6 — The original numeric feasibility conflict still has no fixed outcome

**Severity: BLOCKER.**

**Location:** Phase 0 D12 at `phase-0-public-skeleton.md:456-460`; revision 2
lines 354-390, 392-406, and 653-655.

“Counts take precedence over ladder conformance where a numeric conflict is
resolvable” does not decide a conflict among exact counts, distinctness,
integer status, endpoints, and canonical representation. Nor does the generic
generation-refusal paragraph enumerate this check, choose refusal, or state a
remediation usable without the source table.

The original genuine producer fixture remains decisive: the 100 raw cells
`0, 0.0, 1, 1.0, ... 49, 49.0` publish `n_present = n_distinct = 100`,
`integer_valued: true`, endpoints 0 and 49, and `n_zero = 2`. There are only 50
whole-number values in the inclusive range, and two zero cells already require
a parsed duplicate. Under D12's one canonical shortest-round-trip numeric
serialization, those parsed integers do not supply 100 output spellings. If
that D12 rule is not intended to govern twin numeric cells, the plan instead
needs to authorize and specify invented lexical variants; revision 2 does
neither.

**Failure scenario:** one implementation relaxes exact all-different
distinctness, another moves an endpoint, a third invents exponent or spacing
variants for the same parsed integers, and a fourth generation-refuses the
valid producer profile. All can cite lines 375-383 because the plan neither
classifies the conflict as resolvable nor names the winning facts or permitted
numeric spellings. Acceptance line 655 nevertheless claims a fixed named
outcome.

**Required closure:** enumerate this conflict and choose its exact outcome in
the plan, including whether D12 permits more than one spelling per parsed
number. If it is generation refusal, give an actionable no-table remediation
and record the producer/consumer compatibility loss; if it is relaxation,
identify each changed disposition and obtain any owner amendment required for
an exact fact.

### P2-R3-F7 — Identifier length is relaxed without the required owner decision

**Severity: BLOCKER.**

**Location:** revision 2 lines 331-336, 354-379, 726-728, and 759-776;
round-1 review P2-R1-F8 at lines 260-267.

Revision 2 now chooses a real mechanism: length expands before distinctness.
That is an improvement over deferral, but it is also an active fidelity
amendment. The matrix otherwise calls `min_length` and `max_length`
EXACT-OBSERVABLE. Round 1 expressly required an owner amendment before relaxing
length or any other exact invariant. The settled exact-count choice determines
that counts must win; it does not by itself choose which separate exact
observable may be made false.

**Failure scenario:** a declared identifier has 200 distinct one-code-point
values, all singleton. Phase 1 validly publishes
`min_length = max_length = 1`. Revision 2 emits some multi-character values.
Validation code developed against the twin accepts variable-width identifiers,
while the real table contains only one-character identifiers. The report names
the difference, but the owner has not authorized that fidelity trade.

**Required closure:** obtain and record owner authorization for R-P2-8, or
change the v4 domain/method so the exact length and exact count facts are
jointly feasible. Do not present the relaxation as implementer-level conflict
resolution.

### P2-R3-F8 — Loader resource limits remain a later artifact's product decision

**Severity: MAJOR.**

**Location:** revision 2 lines 128-141 and 591-600;
`src/synthtwin/reading.py:239-246,716-745`.

Revision 2 says maximum document size and depth will be stated in the contract
specification, but gives neither value here. The round-2 requirement also
included maximum container and string sizes; those remain only generic
“oversized structures.” A depth bound “checked before parsing” needs a
defined structural pre-scan or bounded parser construction, which is not
chosen.

Producer compatibility is unresolved. The shipped reader permits one field up
to 10,000,000 characters and has no total profile-byte or column-count bound.
Any finite loader cap can therefore reject a profile produced within the
producer's stated domain unless v4 adds a matching producer bound.

**Failure scenario:** a valid wide table produces a canonical v4 profile just
above the later implementer's chosen 8 MiB document cap. Phase 1 writes it;
Phase 2 refuses it before parsing. Another conforming implementation chooses
16 MiB and generates successfully, so revision 2 has not fixed product
behavior or disclosed its compatibility cost.

**Required closure:** fix numeric byte, depth, container, and string limits;
define the pre-parse enforcement construction; align the v4 producer domain
with those limits or record the intentional incompatibility; and require
near-limit valid and one-over-limit tests for every bound.

### P2-R3-F9 — The seed set is fixed but its CLI grammar and invariance are not

**Severity: MAJOR.**

**Location:** revision 2 lines 437-447 and 664; round-2 review lines 411-414.

The mathematical range and scoped sensitivity fixture are now correct.
“Integers,” however, is not a lexical CLI grammar. Common parsers disagree on
leading signs, underscores, leading zeros, whitespace, and non-ASCII decimal
digits. The required boundary tests are not named. The determinism battery
also omits the round-2 requirement that fully determined twin bytes be
seed-invariant.

**Failure scenario:** one implementation parses `--seed 1_0` as ten and
another refuses it; both enforce `0..2**64-1` after parsing. Separately, a
mutant uses the seed to choose minimal or extra quoting for an all-absent
column. Default-seed goldens, identical-input checks, and sensitivity on a
random-freedom fixture all pass, while a seed changes bytes for a profile with
no random degree of freedom.

**Required closure:** state one accepted character grammar and normalization
rule, freeze lower/upper and adjacent boundary spellings, and add twin-byte
seed invariance for fully determined profiles.

### P2-R3-F10 — P1-R8-F5's accepted-built-in correction is still omitted

**Severity: MINOR.**

**Location:** revision 2 lines 153-163 and 710-712; Phase 1 round-8 review
lines 27-70 and 217-231; `tools/offline_scan/scan_imports.py:477-482`.

Revision 2 names the SECURITY and Phase 1 plan corrections but calls them the
remaining edits. Its non-exhaustive-example and decorator wording repairs part
of the implicit-call description, but P1-R8-F5 also named the scanner's own
accepted-built-in audit. That sentence still says every other accepted built-in
takes data and never invokes an argument. Length, truth, iteration, conversion,
formatting, and hashing contradict it.

**Failure scenario:** implementation edits only the two named documents. A
reviewer adds `hash(value)`, sees a clean scan, and concludes the scanner has
regressed because its own audit record says that built-in cannot invoke the
value it receives.

**Required closure:** add the scanner's accepted-built-in paragraph to the
documentation gate, correct the false sentence, and assert it together with
the SECURITY, Phase 1, and non-exhaustive-example sentences.

### P2-R3-F11 — The repair map cannot catch its own remaining reference drift

**Severity: MINOR.**

**Location:** revision 2 lines 529, 778-796, and 798-805; round-2 review lines
495-516.

The blocker counts are now accurate. The demanded simple reference check or
manual checklist for all 22 round-1 identifiers is still absent; the new table
checks only the fifteen round-2 items. Line 529 also cites P2-R2-F6 in the
datetime/byte heading without explaining that cross-reference, while the
mapping identifies F6 as the scanner enumeration and gives its actual answer
only in P2-D13. Because F6 includes the writer surface, that citation could be
intentional, but in its present form it is ambiguous rather than a usable
closure trail.

**Failure scenario:** a later reviewer follows line 529 for P2-R2-F6, checks
datetime serialization, and records closure without inspecting returned-array
or writer-handle provenance. The fifteen-row mapping does not expose that the
original 22-item audit trail remains unchecked.

**Required closure:** reconcile every body citation and add the previously
required all-22 round-1 identifier checklist or an equivalent mechanical
reference check.

## Owner decisions and fidelity costs

The settled additive axes, anonymous multiplicity additions, and empty
relationship manifest are carried consistently. Header evidence is restored,
the additive axes are controls rather than falsely CSV-observable facts, and
the relationship block remains loader-only and empty.

The exact-count decision is not fully carried: P2-R3-F6 leaves the genuine
numeric conflict undecided. It also motivates but does not authorize the
separate length-fidelity amendment in P2-R3-F7.

Of the two choices revision 2 explicitly leaves with the owner:

- **Source datetime formatting:** correctly recognized as a D12 amendment and
  correctly not assumed. The plan's chosen ISO path is nevertheless
  incoherent for offsetless/date/quarter profiles, and its recorded cost is
  incomplete; P2-R3-F4 must be settled before the owner can evaluate the true
  alternative.
- **Publishing numeric-unrepresentable width facts:** correctly recognized as
  a new real-derived disclosure and correctly not assumed. R-P2-1 honestly
  records the fidelity loss while the plan proceeds without new disclosure.

R-P2-8 is a third owner-level fidelity choice, not merely an implementer
choice. The plan accurately states that some identifier lengths will change,
but it must not ratify that change without the owner record required by
round 1. The still-unknown loader caps may create another product-domain cost;
their mechanism must be fixed before deciding whether owner approval is also
needed.

The other stated costs are substantially honest: absent-value spellings and
classes are not reproduced; columns and row grain are not modeled; source
encoding is not retained; and formula-context text remains unchanged and
warned. R-P2-4 currently overstates matrix-wide boundedness because datetime
cardinality has no unambiguous bound in the written matrix.

## What was checked

### Surfaces

- Every revision-2 decision P2-D1 through P2-D14, sequencing gate, residual,
  acceptance criterion, owner record, and claimed round-2 mapping.
- Every P2-R2-F1 through F15 closure claim and all eight round-1 items that
  round 2 judged closed.
- Shipped top-level, source, settings, universal, empty, constant, count,
  continuous, categorical, binary, datetime, text, identifier, and
  numeric-unrepresentable profile shapes.
- Producer flat keys, one-based positions, normalized label pooling,
  raw/folded counts, numeric echoes, datetime resolutions and offsets,
  header evidence, publication notes, canonical JSON, and display functions.
- Installed command initialization and dispatch, transitive/re-export/alias
  boundary routes, loader read set, output naming, input/output identity,
  existing targets, and both sides of the transaction.
- D12 byte and RNG rules, seed domain, draw topology, canonical CSV/report
  bytes, leading-U+FEFF handling, and the narrowed formula-context claim.
- Scanner imports, bare and dotted bindings, restricted instance methods and
  attributes, method-result origins, callback slots, writer handle/row
  origins, and current source scan.
- Public record, handling, approval, privacy, temporary-private, and
  deferred-governance claims across the required baseline and package text.

### Properties and attack classes

- Offline and profile-only generation under process startup, pre-dispatch,
  before/within/after-loader, alias, re-export, raw-cell, and unexpected-output
  routes.
- Native-backed capability expansion through constructor returns, array
  attributes/methods, callback arguments, writer protocols, and lost origin
  propagation.
- Silent statistical wrongness through raw/folded identity, cardinality
  collapse, numeric equality, infeasible exact allocation, datetime
  offset/precision changes, unparsed stand-ins, and type misrouting.
- Matrix completeness, loader/producer compatibility, duplicate and unknown
  keys, non-canonical numbers, malformed encoding, recursion/allocation
  failures, and resource-bound behavior.
- Single-stream determinism, draw ordering, seed parsing, fully determined
  profiles, locked-version changes, UTF-8/LF/terminal-newline bytes, and exact
  reader round trips.
- Destructive replacement, first/second-target symmetry, aliases/links,
  rollback inheritance, source-derived publication routes, report display
  integrity, zero-code remediation, and content-gate coverage of the actual
  file.

### Checks that did not produce additional items

- Flat role keys, one-based positions, canonical duplicate-key rejection, and
  the one-stream topology remain coherent.
- The output-observable/control split has non-tautological evidence and a
  useful type-misrouting mutant.
- Label-role raw/folded resolution no longer requires invented unpublished
  spelling variants; the remaining matrix item concerns uncovered roles and
  shapes.
- Header-source and header-evidence dispositions carry the first-row
  uncertainty into the report.
- Default refusal plus explicit symmetric `--replace` closes unrelated-file
  replacement at plan level.
- The forced-quoting leading-U+FEFF rule closes the exact-name/no-marker
  contradiction and is testable with exact bytes.
- The repository-wide record/handling inventory and the no-formal-privacy
  statement cover the canonical surfaces round 2 named.
- The formula-context battery now claims only what it executes.
- Revision 2 preserves the repository's temporarily-private/deferred-control
  distinction and does not claim that Phase 2 code exists.

### Verification performed and limits

- `.venv/bin/python -m pytest -q -p no:cacheprovider
  tests/test_profile_document.py tests/test_offline_scan.py
  tests/test_decontamination.py tests/test_r6f5_write_transaction.py`:
  **222 passed**.
- `.venv/bin/python -m pytest -q -p no:cacheprovider
  tests/test_p1r6f11_display_boundary.py
  tests/test_p1r8f4_repetition_multiset.py`: **46 passed**.
- `.venv/bin/python tools/offline_scan/scan_imports.py src`: **9 Python
  files, 0 violations**.
- Empty/constant/date/quarter/count producer probes confirmed the role shapes,
  numeric-only `n_rows` echo, universal distinctness fields, offsetless date
  metadata, quarter precision, and the genuine numeric conflict.
- A quoted leading-U+FEFF source round-tripped exactly; minimal output moved
  the marker bytes to byte zero and lost the character on re-read; quoted
  output retained it.
- Direct scanner probes confirmed a bare allowed from-import scans clean.
  In-memory additions limited to revision 2's named NumPy/writer surface
  demonstrated the lost array origin and caller-derived writer-handle,
  row-source, and dialect routes.
- Revision 2 was copied byte-for-byte to a non-Git temporary root, checked with
  `cmp`, and the content scanner read that copy and returned clean. This does
  not claim the current untracked plan is covered by the repository's
  no-argument scan.
- The review environment refused a write to the repository's working index
  while creating `.git/index.lock`. To make the no-argument gate actually read
  this file, I copied the real index to a temporary Git index, added only this
  review there, and set `GIT_INDEX_FILE` for both
  `git ls-files --error-unmatch` and the unchanged no-argument content command.
  The exact review path resolved from that index and the command returned
  clean. The working index remains unchanged, so this review still needs to be
  staged by the maintainer.
- This remains a paper review. The v4 contract, method specification,
  reference vectors, and Phase 2 implementation do not exist and were not
  reviewed.

## Verdict

**REJECT.** The blocking items are **P2-R3-F1, P2-R3-F2, and P2-R3-F4
through P2-R3-F7**. Revision 2 may not be ratified, and no Phase 2 method or
implementation may begin, until those items are closed in a revised plan.
P2-R3-F3 and P2-R3-F8 through P2-R3-F11 are also required repairs; they do not
authorize deferral of publication enforcement, loader bounds, seed semantics,
documentation accuracy, or review traceability into implementation.

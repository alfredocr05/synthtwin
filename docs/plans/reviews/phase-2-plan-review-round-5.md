# Phase 2 plan review, round 5

**Reviewed:** 2026-08-11

**Plan:** `docs/plans/phase-2-generator.md`, revision 4

**Review type:** final authorized plan-only ratification gate; no Phase 2
implementation exists

## Outcome

Revision 4 makes three important repairs. The two datetime dispositions are
now correct, the identifier infeasible corner demotes all three facts that
cannot survive the owner's length-first decision, and the numeric-token route
has its own pre-parse bound. The antecedent amendments are also additive: they
preserve the historical Phase 0 and Phase 1 text rather than silently rewriting
it.

The revision is nevertheless not ratifiable. The new numeric family cannot
represent the shipped producer's raw/folded domain, and the current profile
cannot identify the ordinary-reader type the plan promises to preserve. The
new label-variant decision is not carried into the wire shape, invariants,
matrix, generation semantics, or a boundary-sensitive disclosure battery.
The universal all-different rule remains infeasible for genuine datetime,
free-text, and numeric-unrepresentable profiles. The publication guard and
the `columns` container still leave contract mechanisms open, while the
remaining container limit still rejects genuine Phase 1 output. Those defects
would be baked into the profile-contract specification if it were built now.

The other withdrawals are also incomplete. Downstream text still refers to
the abandoned ownership proof and to four producer bounds. E8 now names the
three NumPy origins, but it still delegates the exact accepted call form and
does not close implicit-protocol origin laundering. These latter items remain
blocking for their eventual implementation surfaces, but they need not alter
the profile v4 wire contract if recorded as bounded conditions at the next
review gate.

## Review basis and method

I read the complete required baseline: `CLAUDE.md`, `AGENTS.md`,
`SECURITY.md`, the Phase 0 public-skeleton plan (D6.2, D12, and its dated
amendment), the Phase 1 profiler plan at revision 5 and its dated amendment,
the Phase 1 round-8 review, and all four prior Phase 2 reviews. Every plan
citation below was re-derived against revision 4.

Measured producer, reader, normalization, and scanner claims were checked
against `src/synthtwin/parsing.py`, `taxonomy.py`, `reading.py`,
`profile.py`, `tools/offline_scan/scan_imports.py`, and the locked current
environment. The five small pandas examples in decision 8 reproduce under
default pandas 3.0.5. They are measurements of default pandas inference, not
of synthtwin's shipped checking pass, which expressly uses `dtype=str`
(`reading.py:1066-1083`). Producer roles and facts come from synthtwin's own
parser and taxonomy instead.

I treated owner decisions 8 and 9 as settled choices, not as invitations to
choose different policy. The review asks whether the mechanisms stated for
those choices actually implement them over the producer's domain, whether
the disclosure delta is complete and floor-governed, and whether a further
owner choice is required before the contract can be written.

## Closure of every round-4 item

The final column is an independent closure check. For every live item it gives
a specific state or input and the wrong outcome. A repair that closes the
original issue but exposes a separate defect is credited narrowly and points
to the round-5 item that records the new defect.

| Round-4 item | Judgment | Remaining severity | Independent closure check |
|---|---|---:|---|
| P2-R4-F1 | **Partly closed.** The operative rule now refuses whenever either target exists unless `--replace` is explicit, and it preserves P2-D1's profile-only read boundary (`phase-2-generator.md:631-656`). The withdrawal is not complete: the failure catalog still conditions refusal on absence of “proof of ownership,” and the closure trail still says proof plus `--replace` (`:705-714,930-941`). | **BLOCKER; P2-R5-F9.** | Leave a genuine old report beside a substituted valuable CSV. The rule at `:648-656` refuses, but an implementer following `:711` or `:936` can reinstate the withdrawn marker/name proof and replace the CSV on a default run. The generic “ownership battery” at `:774` does not resolve which rule is normative. |
| P2-R4-F2 | **Partly closed.** Revision 4 names Generator, array, and scalar origins, requires type-sensitive lookup, preserves origin through indexing/iteration, and identifies the argument slots (`:795-824`). It still merely says “the exact” positional and keyword form will be enumerated rather than stating either form, and its red list omits implicit-protocol routes. | **BLOCKER; P2-R5-F8.** | A traced scalar passed to `bool`, `format`, `hash`, an operator, or `list`/iteration can execute a library protocol or lose its origin under the shipped scanner, while the named attribute mutations at `:839-846` remain red. A caller-derived `size` can likewise enter whichever positional form the later specification chooses because this plan never fixes that form. |
| P2-R4-F3 | **Closed narrowly.** `format` is REPORT-ONLY, `datetimes_read_at` is EXACT-OBSERVABLE, and the lexical-format residual is restored (`:429-454,865-870`). | None for the two dispositions. **Fresh BLOCKER P2-R5-F3** applies to all-different; its broad behavior rationale is a carried MAJOR condition. | Genuine compact-date, month-first-date, and mixed-offset producer probes confirm the two revised dispositions. The remaining contradiction is no longer in those rows: it is the universal all-different rule and the claim at `:83-85` that date-handling code behaves the same despite `:865-870`. |
| P2-R4-F4 | **Closed substantively.** In the identifier infeasible corner, raw distinctness, folded distinctness, and the anonymous repetition multiset are all REPORT-ONLY, with published and achieved values named (`:461-479,871-875`). The Phase 1 amendment records the same three losses (`phase-1-profiler.md:449-468`). | None for the original missing demotions. **Fresh BLOCKER P2-R5-F4** applies to other invention roles; the identifier alphabet arithmetic is a MAJOR method condition. | The arithmetic 95 raw printable ASCII code points and 69 folded identities is correct for the entire printable set. It is not the usable present-value domain: space, `-`, `.`, and `?` normalize as absent, leaving at most 91 raw and 65 folded one-character values. A method using 95/69 can write four cells that reprofile as missing. The text is otherwise honest that the multiset can no longer be honored. |
| P2-R4-F5 | **Not closed.** Decision 8 replaces the spelling family, but exact raw/folded capacity and ordinary-reader typing still fail over genuine producer output. The old approximate fallback and repeated references to superseded decision 7 remain (`:378-423,499-527,666-669`). | **BLOCKER; P2-R5-F1.** | `0`, `00`, `000` and `0.0`, `00.0`, `000.0` produce identical shipped column blocks, but default locked pandas infers whole-number and decimal columns respectively. A profile-only generator must choose the same output for both and mistype at least one. A separate 75-row exponent/edge-spacing profile requests three raw spellings per folded identity, while the permitted exponent case pair supplies only two. |
| P2-R4-F6 | **Not closed.** Decision 9 exists at `:142-164`, but normalized-only contract and generation text still contradict it (`:213-219,369-379,425-427,608-616`). The datetime half of the original all-different finding is untouched, and other invention roles have the same finite-domain defect. | **BLOCKER; P2-R5-F2 through P2-R5-F4.** | With floor 11, three published normalized labels can each contain eleven one-off spelling variants. The plan has no per-parent suppressed-variant shape that tells generation to invent eleven distinct safe forms. Independently, twelve raw-unique spellings of four dates publish `n_distinct == n_present`, but canonical date output between the exact endpoints has only four parsed dates. |
| P2-R4-F7 | **Partly closed.** Both amendment records are append-only and preserve historical text. The identifier scope and all three demotions are accurate. The records inherit the unresolved numeric and label claims, Phase 1 says there are only two all-different exceptions, and the broad datetime rationale conflicts with the reinstated residual. | **BLOCKER through P2-R5-F1 through P2-R5-F3; MAJOR wording condition.** | Phase 1 lines 451-468 enumerate identifier and label only. Feed the genuine datetime profile described under P2-R5-F3: the third infeasible case contradicts that amendment. Phase 0 lines 486-496 also promise the numeric type behavior disproved by two profile-equivalent sources, while Phase 0 lines 483-485 promise unchanged date-handling behavior for a month-first parser that the ISO twin breaks. |
| P2-R4-F8 | **Not closed.** The finished-document traversal remains, but allowed leaf classes, path-sensitive classes, and nested-container behavior are again delegated to the profile contract (`phase-2-generator.md:275-284`). | **MAJOR and next-artifact blocking; P2-R5-F5.** | Interpolate a source-derived spelling into the existing string-valued `publication_notes[*].note` path. A path-and-type whitelist sees the same path and type as permitted prose and serializes it; every matrix key remains known. Artifact 2 would have to invent origin or grammar enforcement that sequencing `:55-56` says it may not introduce. |
| P2-R4-F9 | **Partly closed.** A sixth STRUCTURAL class is introduced for `columns` and `source`, and leaf completeness is required (`:381-395,485-488`). Container membership and ordering remain unstated; the section still says five dispositions, and the disposition battery and acceptance criterion enumerate only the old five (`:332-341,748-761,893-905`). | **BLOCKER for the profile contract; P2-R5-F6.** | A two-column profile whose list holds position 2 before position 1 still has positions forming exactly `1..n_columns` and every leaf disposed. One conforming generator preserves list order; another sorts by position. They write different schema and consume the RNG in different orders. |
| P2-R4-F10 | **Closed narrowly.** A JSON numeric token has a 64-character limit, checked by the structural pre-scan with near/over tests (`:245-263`). | None for the numeric-token route. | Producer counts and positions are far shorter than 64 characters, and the pre-scan occurs before `json.loads`. References to “four” limits are part of the failed cap withdrawal under F11, not an absence of this numeric-token route. |
| P2-R4-F11 | **Not closed.** Removing the document-byte and producer limits leaves a maximum of 10,000,000 members per container, which narrows Phase 1's domain for inputs that fit in memory. Several later sections still say there are four limits or refer to producer limits (`:245-268,705-708,748-753,881-900,930-941`). | **BLOCKER; P2-R5-F7.** | Assume Phase 1 has enough memory to create a profile from a CSV containing 10,000,001 named fields. The resulting `columns` list is one member past the loader maximum, so Phase 2 refuses it. |
| P2-R4-F12 | **Not closed.** The trail still begins with round 2 and repeats the transitive prose assurance rejected in round 4; there is no R1-F1 through R1-F22 checklist or mechanical equivalent (`:922-969`). | **MINOR; P2-R5-F10.** | If one round-1 item was mapped to the wrong round-2 successor, the table has no row against which a reviewer can detect the omission; the claim at `:924-928` stays green by assertion alone. |

## Review items

### P2-R5-F1 — Decision 8 cannot preserve numeric identity and type from the current profile

**Severity: BLOCKER. Must block the profile-contract artifact.**

**Location:** revision 4 lines 110-140, 378-423, 490-527, 666-669,
750-769, and 876-880; `src/synthtwin/parsing.py:432-482`;
`src/synthtwin/taxonomy.py:3390-3395`;
`src/synthtwin/reading.py:239-246,1066-1083`.

The five measurements in decision 8 reproduce under default pandas 3.0.5:
leading zeros and a leading plus keep the three small integer cases as
`int64`, while a decimal point or exponent produces `float64`. That local
measurement does not establish the plan's general claim. It is also not a
measurement of the shipped synthtwin checker, whose pandas pass deliberately
reads every cell as text.

The current profile loses exactly the lexical fact needed to preserve default
reader typing. These three source families produce byte-for-byte identical
shipped column blocks: `0`, `00`, `000`; `0.0`, `00.0`, `000.0`; and `0e0`,
`00e0`, `000e0`. Each is role `count`, with three present, three raw and
folded identities, all numeric, all zero, and `integer_valued: true`. Default
pandas reads the first family as `int64` and the other two as `float64`.
Because the profile is identical, no deterministic profile-only generator can
preserve the source's inferred type for all three. Decision 8 permits exponent
case only when folded identity is below raw identity, so it specifically
chooses integer-looking leading-zero output for all three of these equal-count
profiles.

The new family also does not cover raw/fold capacity. For each integer 1
through 25, take lower-case exponent, upper-case exponent, and an edge-spaced
lower-case exponent. The shipped producer records 75 raw identities, 25
folded identities, whole-number parsed values, and role `count`. Exponent case
supplies only two raw strings per folded identity. A leading zero or plus
creates another folded identity, so the permitted family cannot supply the
required 75/25 pair. Lines 421-423 and 499-501 still silently fall back to an
approximation even though decision 8 says the ceiling was removed and no
owner authorized that loss.

The claimed unbounded safe capacity also fails for fractional values. A
genuine 100-row continuous source using `1.5`, `1.50`, and successively longer
trailing-zero spellings is read by default pandas as 1.5 in every row. The
producer publishes 100 raw and folded identities. Supplying 100 leading-zero
and plus forms forces long prefixes; under the locked reader, the first wrong
value appears with 16 added leading zeros, and longer forms read as 1.0 or
0.0. A generated column can therefore reprofile cleanly through synthtwin
while default analysis reports a mean of 0.5 rather than 1.5. Independently,
the shipped CSV reader's 10,000,000-character field limit makes any
single-value spelling family finite.

**Failure scenario:** profile the decimal zero family above, then generate
under decision 8. The loader and reprofile checks see the expected count,
raw/folded counts, zero count, and integer-valued fact. Default pandas receives
an integer column instead of the source's decimal column, so downstream type
dispatch changes with no error or validation miss.

**Required closure:** obtain an owner disposition. Either publish a precisely
defined, floor-reviewed lexical/type fact sufficient to distinguish the
colliding producer profiles, or explicitly withdraw ordinary-reader type
fidelity and record its consequence. Separately define a family and capacity
rule that realizes every permitted raw/folded pair, or authorize a named
refusal/loss. Remove the unauthorized fallback and every superseded
decision-7 reference. Freeze genuine whole, decimal, exponent, edge-space,
fractional-prefix, and capacity-boundary profiles, and test both reprofiled
facts and the named ordinary-reader configuration.

### P2-R5-F2 — Decision 9 is neither a complete contract nor an honest disclosure delta

**Severity: BLOCKER. Must block the profile-contract artifact.**

**Location:** revision 4 lines 142-164, 213-229, 369-379, 425-427,
608-616, 767-781, and 885-888; `src/synthtwin/parsing.py:283-294`;
`SECURITY.md:20-27`.

The floor logic is sound only at its narrowest level: if a variant is nested
under an already-published normalized label, its count cannot exceed its
parent count, so a visible variant cannot make a withheld parent visible.
Revision 4 does not define the structure or invariants that enforce that
narrow claim. It provides no variant keys, per-parent association, sum rules,
anonymous remainder shape, forbidden-key rule for non-label roles, or
generation semantics. Its existing contract text says case and spacing are
not preserved; its matrix leaves raw label distinctness REPORT-ONLY; and D9
still writes normalized labels only. The new disclosure could therefore ship
without the fidelity benefit for which the owner authorized it.

The suppression case needs more than a pooled row count. With floor 11, make
three normalized labels of eleven rows each, each row using a different
edge-spacing variant. The shipped producer publishes the three parent labels,
`n_present = n_distinct = 33`, and `n_distinct_folded = 3`; every raw variant
is below the floor. A per-parent pool saying only “11 rows withheld” cannot
distinguish eleven singletons from two hidden variants occurring ten and one
times. The first requires eleven invented spellings to keep all-different
output; the second requires two spellings with different multiplicities. The
contract currently states neither fact. Decision 9's four-row example also
needs an explicit floor at most two: under the shipped default floor 11 its
two normalized labels are themselves withheld.

The disclosure description is too narrow. The shipped fold is Unicode
`strip().casefold()`, not capitalization plus ASCII edge spaces. At floor 2,
two occurrences of U+00DF and two occurrences of ASCII `SS` fold to the same
normalized identity, while variant publication exposes both exact forms and
their counts. That is a broader raw-spelling disclosure than lines 159-160
state. The plan says the change is already named in `SECURITY.md`, but that
file contains no variant-disclosure entry. The battery at line 781 scans only
the twin and report, not the real-derived profile and profiler summary where
the new fact first appears.

**Failure scenario:** build the 33-row floor-11 profile above. A contract that
implements only a per-parent withheld-row total cannot tell the generator how
many distinct spellings to invent. It either emits repeats and violates the
published all-different fact, or emits singletons for a profile whose hidden
variant was repeated, while all named floor and disclosure checks remain
green.

**Required closure:** define the exact label-only wire keys and publication
classes; bind every variant or anonymous pool to one already-visible parent;
state per-parent count, raw-distinct, folded-identity, and reconciliation
invariants; forbid these keys for withheld parents and every non-label role;
and update the matrix, loader, generation semantics, report, summary, and
residual. Describe the delta as exact raw variants under trim plus Unicode
case-folding, including anonymous suppressed counts. The battery must cover
floor-minus-one, floor, and floor-plus-one variants beneath a visible parent,
a withheld parent, identifier and free-text blocks, and must scan the complete
profile, profiler summary, twin, and generator report. Add the promised
planned entry to `SECURITY.md`.

### P2-R5-F3 — The universal all-different rule still fails for datetime, and the antecedent record omits it

**Severity: BLOCKER. Must be settled before the profile contract.**

**Location:** revision 4 lines 73-105, 429-454, 608-613, and 865-870;
`docs/plans/phase-0-public-skeleton.md:462-508`;
`docs/plans/phase-1-profiler.md:449-468`.

Decision 5 canonicalizes datetime cells at recorded precision. The equality
rule measures datetime facts as parsed instants at that precision, while D9
still requires all-different present values on every role whenever raw
`n_distinct == n_present`. Lexically distinct source values can collapse to
far fewer parsed instants after canonicalization.

A genuine example uses four consecutive dates, each written in three distinct
edge-space forms. The producer reports twelve present and twelve raw-distinct
cells, four folded identities, date precision, and exact endpoints four days
apart. Decision 5 permits canonical date-only ISO output. There are only four
parsed dates inside those exact endpoints, so twelve all-different output
values are impossible. The same issue occurs with multiple fractional-zero
spellings of one timestamp. Owner decision 9 is label-only and owner decision
6 is declared-identifier-only, so neither supplies a disposition.

The new Phase 1 amendment says the inherited obligation is infeasible in
exactly two cases, identifier and label (`phase-1-profiler.md:451-468`). This
datetime profile is a third. The Phase 0 amendment and P2-D0 also state that
date-handling code behaves the same (`phase-0-public-skeleton.md:483-485`;
`phase-2-generator.md:83-85`), while the correctly reinstated residual says a
source-format-specific parser must change (`phase-2-generator.md:865-870`).
Those are not compatible descriptions of the cost.

**Failure scenario:** profile twelve raw-unique spellings of the four dates,
then generate canonical date cells. Reusing dates violates D9's all-different
rule; choosing a calendar day earlier than the first or later than the last
violates endpoint equality.
Either output looks valid, but at least one exact promise is false.

**Required closure:** obtain an owner disposition for datetime lexical
distinctness: publish floor-reviewed lexical facts sufficient to preserve it,
or demote/refuse the infeasible fact with published-versus-achieved reporting.
State the equality and capacity rule per datetime resolution, add genuine
date/time boundary profiles, and amend Phase 1 to enumerate the actual cases.
Narrow both “behaves the same” rationales to the reprofiled precision and
offset facts; retain the explicit source-format loss.

### P2-R5-F4 — The finite invention domain leaves genuine all-different profiles infeasible outside identifiers

**Severity: BLOCKER for the plan; bounded and carryable to the method-specification gate without changing the profile contract.**

**Location:** revision 4 lines 369-379, 456-459, 481-483, 490-516,
595-613, and 767-769; `src/synthtwin/parsing.py:283-306`.

The identifier repair is complete about its three lost facts, but its domain
calculation counts spellings the producer treats as absent. Full printable
ASCII contains 95 characters and 69 case-folded identities; after removing
space, `-`, `.`, and `?`, only 91 raw and 65 folded one-character present
values remain. A generator that follows the stated 95/69 capacity can turn
four present identifier cells into missing cells. The plan also never locally
repeats in D9 that the exception is declared-identifier-only.

More importantly, the same capacity conflict exists where the owner expressly
did not authorize repeats. A genuine undeclared column containing 96 distinct
one-code-point neutral Unicode values profiles as free text with 96 present,
96 raw/folded identities, exact one-character length, and an all-singleton
multiplicity map. P2-D6 widens generation only to printable ASCII, which has
at most 95 raw one-character forms before absent and alphabet constraints.
D9 nevertheless requires all-different output. No identifier exception
applies to an undeclared free-text key.

`numeric_unrepresentable` has an analogous folded-capacity case. For each of
three positive whole values, use lower-case exponent, upper-case exponent,
and an edge-spaced lower-case exponent large enough to be outside binary64.
The producer records nine raw identities and three folded identities plus an
all-singleton repetition map. Canonical invented digit strings and a two-case
exponent pair cannot reproduce all three exact facts, and the feasibility
battery names neither role.

**Failure scenario:** generate from the 96-value free-text profile. Emitting
only the fixed printable-ASCII domain forces a duplicate or a missing value,
so raw distinctness, presence, or the exact singleton map fails even though
the report has no authorized exception to disclose.

**Required closure:** before ratifying the generation method, freeze a
present-safe neutral invention alphabet and prove capacity jointly over
length, folded identity, `n_all_digits`, `n_code_alphabet`, word count, and
multiplicity for every invention role. Otherwise obtain an owner disposition
for each infeasible role. Add genuine boundary profiles and one-over-capacity
mutations. Correct the identifier figures and repeat its declared-only scope
at the local D9 rule. This condition may be carried through profile-contract
review only if that review records that no approximate output is authorized
and that closure is mandatory before artifact 3.

### P2-R5-F5 — The publication guard still delegates its acceptance mechanism

**Severity: MAJOR. Must block the profile-contract artifact.**

**Location:** revision 4 lines 43-56 and 275-284.

Revision 4 correctly moves traversal to the finished document. It does not
choose what that traversal accepts. “Allowed leaf classes, path-sensitive
classes and nested-container behaviour fixed in the spec” is the same
deferral round 4 rejected. A path-and-type whitelist cannot distinguish a
fixed first-party note from source-derived text interpolated into the same
note path. Artifact 2 cannot repair this by introducing origin tags, a fixed
note grammar, or another mechanism, because sequencing says later artifacts
may carry out decisions but may not make them.

**Failure scenario:** a future producer formats one source spelling into
`publication_notes[0].note`. It remains a string at a permitted path, every
schema key and disposition is unchanged, and finished-document recursion
passes while the profile publishes a real value outside the authorized
matrix.

**Required closure:** choose the plan-level mechanism now. For example,
require origin-tagged fixed-note constructors plus an exact enumerated note
grammar, or define an equally enforceable alternative. Enumerate every
allowed leaf origin/path/container combination and add same-path/same-type,
nested-container, concatenation, formatting, and top-level-lift mutations.
Artifact 2 may encode that choice, not invent it.

### P2-R5-F6 — STRUCTURAL leaves schema order and membership unconstrained

**Severity: BLOCKER. Must block the profile-contract artifact.**

**Location:** revision 4 lines 221-229, 332-341, 381-395, 485-488,
545-552, 748-761, and 893-905.

STRUCTURAL closes the missing-disposition accounting hole for leaves, but it
expressly gives the container's own key no obligation. The only position
invariant requires the set `1..n_columns`; it does not bind position to list
index. D8 then consumes columns in “schema order” without saying whether that
means list order or sorted position. Membership, output order, and randomness
order therefore remain ambiguous. The testing and acceptance text also still
enumerates only the original five dispositions.

**Failure scenario:** a canonical two-column profile serializes the block at
position 2 before the block at position 1. All keys, ranges, set invariants,
and leaf dispositions pass. One implementation preserves the array and writes
the second column first; another sorts positions and writes the first column
first. Both claim conformance, but names, type paths, values, and downstream
RNG bytes are routed differently.

**Required closure:** state that `len(columns) == n_columns`, that
`columns[i].position == i + 1`, and that list order is the schema, output, and
RNG-consumption order. Define exact membership for every STRUCTURAL object,
include STRUCTURAL in the disposition battery and acceptance criterion, and
add swapped, duplicate, omitted, and extra column-block mutations.

### P2-R5-F7 — The size-cap withdrawal retains a producer-domain cap

**Severity: BLOCKER. Must block the profile-contract artifact.**

**Location:** revision 4 lines 245-268, 705-708, 748-753, 881-900,
and 930-941; `docs/plans/phase-1-profiler.md:311-318,945-952`.

Removing the document-byte and producer-side limits is a real correction.
Keeping a ten-million-entry limit on every container is still a column-count
cap because every produced column contributes one entry to `columns`. Phase 1
promises wide tables subject to available memory, not ten million columns.
The statement that no producible profile approaches the limit is therefore
false. Revision 4 also leaves five separate references to four limits or
producer bounds after saying exactly three parser bounds remain.

**Failure scenario:** on a machine with enough memory, Phase 1 profiles a CSV
with 10,000,001 short columns. No cell exceeds the reader field limit and
Phase 1 succeeds. Phase 2's pre-scan rejects the genuine `columns` array before
schema validation, contradicting the claim that the phases accept the same
domain.

**Required closure:** either remove the container-entry limit and choose a
parser-protection strategy that does not cap genuine column count, or obtain
an owner-authorized domain contraction and amend Phase 1 explicitly. Then
replace every “four bounds” and “producer bounds” dependency with the final
enumeration and add a genuine producer-to-loader boundary test.

### P2-R5-F8 — E8 names three origins but does not enforce the promised scalar-only operation

**Severity: BLOCKER for the scanner extension; bounded and carryable past the profile-contract gate.**

**Location:** revision 4 lines 545-560 and 783-846;
`tools/offline_scan/scan_imports.py:978-1009,2026-2095,3030-3053,3250-3284`.

The three-origin and type-sensitive-lookup repair is correct. Its enforcement
surface remains incomplete. P2-D8 describes a semantic full-width word, while
E8 says the later specification will enumerate the exact positional and
keyword forms and values. The plan therefore still does not say which
`low`, `high`, `size`, `dtype`, and `endpoint` arguments are accepted in
which syntax.

More fundamentally, empty scalar attribute and method sets do not enforce
“`int` is the only permitted operation.” The current scanner accepts built-ins
including `bool`, `format`, `hash`, `iter`, `list`, and `next`, and preserves
restricted origin through subscripting but not every implicit protocol.
Read-only scanner probes rejected a direct unenumerated attribute yet accepted
operators, comparison, truth, formatting, hashing, integer conversion, and
collection conversion on a traced restricted instance. Converting an iterable
to `list` also allowed a later element attribute to lose the original origin.
The red list covers attributes and caller-derived explicit arguments, not
these routes.

**Failure scenario:** convert a traced returned array with `list`, take its
first scalar, and read an otherwise forbidden scalar attribute. The current
analysis loses the scalar origin through collection conversion, so the source
scans clean even though E8 says the scalar has an empty attribute set. All
listed array and direct-scalar mutations still fail.

**Required closure:** fix the one accepted `integers` call syntactically,
including exact values, positional/keyword forms, and first-party origin for
every slot. Propagate or refuse restricted origin through operators,
comparison, truth, formatting, hashing, iteration, `next`, and collection
conversion; allow only the exact checked `int(scalar)` terminal. Add one red
mutation per implicit protocol, an iteration-laundering chain, and every
accepted argument form. This can be carried as a condition through artifact 2
because no NumPy object appears in the profile contract, but it must close
before the method specification using E8 is ratified.

### P2-R5-F9 — The ownership-proof withdrawal is contradicted downstream

**Severity: BLOCKER for output safety; bounded and carryable past the profile-contract gate.**

**Location:** revision 4 lines 631-656, 705-714, 748-781, 893-910,
and 930-969.

P2-D10's operative replacement rule is now safe and complete: existence of
either target refuses unless the person explicitly supplies `--replace`.
The failure catalog still says “without proof of ownership and without
`--replace`,” and R2-F5 still closes through “proof of ownership plus
`--replace`.” Those are not harmless historical descriptions; both are
downstream implementation and audit instructions, and the generic ownership
battery never says that no proof route exists.

**Failure scenario:** following both the failure catalog and closure row, a
developer restores the old report marker/name proof as an alternative
to `--replace`. A stale genuine report beside a substituted CSV then
authorizes default replacement of unrelated data, recreating P2-R4-F1 while
the safe-path test at lines 653-656 can still pass if it uses an invalid
report.

**Required closure:** delete every proof-of-ownership dependency and state in
the failure catalog, closure row, testing strategy, and acceptance criterion
that either existing target always refuses without explicit `--replace`.
Require stale-report, valid-report-plus-substituted-CSV, both target sides,
link/alias, and between-check-and-write cases. This does not change profile v4
and may be recorded as a condition due before implementation review.

### P2-R5-F10 — The closure and decision records remain internally inconsistent

**Severity: MINOR.**

**Location:** revision 4 lines 60-64 and 922-980.

P2-D0 says four decisions were taken on 2026-08-10 and three on 2026-08-11,
and says the latter were required by round 3. The list and review record
correctly show four on the first date and five on the second, of which three
came from round 3 and two from round 4 (`:66-164,973-978`). The closure trail
also still lacks the requested 22-row round-1 mapping, and several rows assert
closure through mechanisms revision 4 withdrew or superseded.

**Failure scenario:** a later audit trusts the D0 count and reviews only
decisions 5 through 7 as the 2026-08-11 set, omitting the numeric and variant
owner decisions. Separately, a mis-mapped round-1 item remains invisible
because no row names it.

**Required closure:** correct the date/count/provenance sentence, enumerate
R1-F1 through R1-F22 or provide a mechanically checkable one-to-one mapping,
and update every stale closure row after the substantive mechanisms settle.

## Final-gate separation for the owner

The verdict below remains a rejection, so revision 4 does not itself authorize
artifact 2. If the owner chooses how to continue after this final authorized
round, the following separation identifies what can and cannot safely be
carried into the profile-contract review.

### Must block the profile-contract artifact

| Item | Why artifact 2 cannot safely proceed | Bounded proof of closure |
|---|---|---|
| P2-R5-F1 | A new numeric lexical/type fact, or an owner-authorized loss, changes what profile v4 promises and may change its wire shape. | Two profile-collision fixtures no longer require incompatible ordinary-reader types; every permitted raw/fold pair has a proved capacity/outcome; no unauthorized fallback remains. |
| P2-R5-F2 | Variant keys, per-parent pools, publication classes, invariants, forbidden-role rules, and disclosure boundaries are the profile contract itself. | Ratified wire rows and reconciliation rules cover visible/withheld parents and floor-minus-one/floor/floor-plus-one across full profile and summary artifacts. |
| P2-R5-F3 | The contract cannot claim universal all-different fidelity while canonical datetime output makes it impossible; the owner must choose a lexical fact or a named loss first. | A genuine raw-unique/fold-colliding datetime fixture has one explicit, owner-authorized outcome and both antecedent records agree. |
| P2-R5-F5 | Artifact 2 is forbidden to invent the origin/grammar mechanism that decides which real-derived leaves may be published. | The plan fixes an enforceable completed-document acceptance rule, with same-path/same-type and nested-source mutations. |
| P2-R5-F6 | Ordering and membership are normative JSON structure and determine schema routing and deterministic byte order. | `columns[i].position == i + 1`, exact membership, and swapped/duplicate/extra/omitted mutations are fixed. |
| P2-R5-F7 | The proposed loader would reject genuine output from the producer whose contract it claims to accept. | Every retained parser bound is proved non-contracting over producer output, or an owner-authorized Phase 1 amendment records the contraction. |

### May be carried as recorded, bounded conditions

These conditions do not require profile v4 fields or weaken any exact profile
fact. They may be recorded in the profile-contract review without baking in
silent wrongness, provided their latest checkpoints are enforced.

| Condition | Latest permissible gate | Verifiable closure condition |
|---|---|---|
| P2-R5-F4 invention-domain capacity and the corrected 91/65 identifier domain | Before generation-method artifact 3 is ratified | A frozen present-safe alphabet and capacity proof covers every invention role and every exact constraint; one-over-capacity genuine profiles receive an owner-authorized outcome. |
| P2-R5-F8 exact E8 call and implicit-protocol provenance | Before artifact 3 is ratified and before any scanner/code change | Exact call syntax/values are normative; all named protocol and iteration-laundering mutations refuse; only checked `int(scalar)` ends scalar origin. |
| P2-R5-F9 ownership withdrawal residues | Before implementation review | Every existing target refuses without `--replace`; no proof mechanism remains in plan, tests, acceptance, or closure text. |
| P2-R5-F3 broad datetime behavior wording and P2-R5-F2 Unicode-disclosure wording/`SECURITY.md` entry | During documentation portions of the profile-contract review | Public text names source-format loss and exact trim-plus-Unicode-fold variant disclosure without claiming behavioral equivalence. |
| P2-R5-F10 decision metadata and all-22 closure mapping | Before the plan record is declared closed | Correct 4/5 decision count and a mechanically complete R1-R4 mapping with no superseded mechanism cited. |

## Coverage

### Surfaces checked

- Revision 4 status, owner decisions, sequencing, boundary, profile-contract
  gate, additive axes, multiplicity, relationships, disposition matrix,
  feasibility stage, method obligations, RNG, per-role generation, outputs,
  honest limits, tests, scanner extensions, residuals, acceptance criteria,
  closure trail, and review record.
- Every P2-R4-F1 through P2-R4-F12 claim and its downstream references in
  decisions, matrix rows, batteries, residuals, acceptance, and closure.
- Phase 0 D12 and amendment A-2026-08-11; Phase 1 D4, its amendment,
  within-memory promises, disclosure obligations, and Phase 1 round-8
  ratification record.
- Shipped numeric parsing and taxonomy, raw and folded counting, label
  normalization and pooling, datetime parsing and equality, missing-value
  normalization, CSV field limits, pandas checking-reader configuration, and
  current scanner origin/call enforcement.
- Public `SECURITY.md` claims, planned-control status, and the asserted new
  label-variant disclosure entry.

### Properties and attack classes checked

- Offline and profile-only generation from process start; library-origin
  propagation; native-backed attributes and methods; callback and implicit
  protocols; argument-origin injection; iteration and collection laundering.
- Silent statistical wrongness through profile-equivalent numeric lexical
  families, ordinary-reader type changes, changed fractional values, raw/fold
  capacity, normalized-label duplication, datetime lexical collapse,
  invention-domain exhaustion, and exact checks with unauthorized fallbacks.
- Type misrouting across whole-number/decimal inference, label roles,
  datetime equality, undeclared free-text keys, numeric-unrepresentable
  values, and schema order.
- Determinism through list/position ambiguity, column consumption order,
  one-stream draw shape, scalar conversion, spelling allocation, and
  fully-determined profiles.
- Profile/generator separation, permitted reads, existing-target replacement,
  stale proof, target symmetry, aliases, and check-to-write changes.
- Validator honesty: observable versus control facts, matrix completeness,
  STRUCTURAL containers, non-vacuous bounds, published-versus-achieved facts,
  and batteries that omit the artifact where disclosure occurs.
- Disclosure through exact variants, Unicode folding, per-parent pools,
  withheld parents, role misplacement, publication notes, nested containers,
  same-path/same-type interpolation, profile/summary/report surfaces, and
  floor boundaries.
- Zero-code behavior through refusal messages, exact affected paths,
  no-table remediation, owner-decision consequences, and residual wording.

### Checks that did not produce additional items

- P2-D1's installed-entry-point boundary, lazy reader-bearing imports,
  profile-only read set, signature bans, and neutral transaction move remain
  coherent after the ownership mechanism is removed.
- Decision 9's narrow mathematical statement that no visible child variant
  can make a withheld parent visible is correct when child nesting and the
  per-variant floor are enforced. The defect is that no contract mechanism or
  battery enforces those premises.
- The corrected datetime `format` and `datetimes_read_at` dispositions match
  genuine shipped producer behavior; their original round-4 defect is closed.
- The identifier section now names the raw count, folded count, and repetition
  multiset together, accurately states that the real repetition pattern can no
  longer be honored, and requires achieved values in the report.
- The 64-character JSON numeric-token bound is a distinct parser-protection
  route and is compatible with current producer-emitted numeric literals.
- The default existing-target rule at P2-D10 is safe as written, the seed
  grammar remains precise, and the leading-U+FEFF, display, formula-context,
  transaction, and determined-profile requirements remain coherent.
- The antecedent amendments preserve historical text and correctly scope
  D12 exceptions to twin CSV cells rather than profile JSON serialization.
- The plan does not claim that deferred public-repository controls are in
  force, does not claim Phase 2 implementation exists, and does not treat new
  generated goldens as their own oracle.

## Verification performed and limits

- `.venv/bin/python -m pytest -q -p no:cacheprovider
  tests/test_profile_document.py tests/test_offline_scan.py
  tests/test_decontamination.py tests/test_r6f5_write_transaction.py`:
  **222 passed**.
- `.venv/bin/python -m pytest -q -p no:cacheprovider
  tests/test_p1r6f11_display_boundary.py
  tests/test_p1r8f4_repetition_multiset.py`: **46 passed**.
- `.venv/bin/python tools/offline_scan/scan_imports.py src`: **9 Python
  files, 0 violations**.
- Default pandas 3.0.5 reproduced all five decision-8 measurement rows; the
  shipped checker configuration was independently confirmed to use
  `dtype=str`.
- Genuine producer probes confirmed the identical numeric profile blocks,
  exponent/edge-spacing fold ratios, label floor behavior, Unicode folding,
  raw-unique datetime collapse, identifier present-value exclusions,
  free-text capacity case, and numeric-unrepresentable fold collision used
  above.
- Ordinary-reader probes confirmed the whole-number/decimal type collision
  and the long-leading-zero fractional value change under the locked current
  environment.
- Source inspection confirmed the 10,000,000-character CSV field limit, the
  library-keyed restricted-instance tables, current accepted built-ins,
  subscript origin propagation, and absent implicit-protocol mutations.
- The review file was added only to a copied temporary Git index, with new
  objects directed outside the repository. `git ls-files --error-unmatch`
  resolved this exact path from that index, and the unchanged no-argument
  content gate read the index and returned clean. The repository index was not
  modified; the review remains unstaged for the maintainer.
- This remains a paper review. The profile v4 specification, generation
  method, reference vectors, and Phase 2 code do not exist and were not
  reviewed.

## Verdict

**REJECT.** Revision 4 is not ratifiable as written. The blocking items for
plan ratification are **P2-R5-F1 through P2-R5-F4 and P2-R5-F6 through
P2-R5-F9**. **P2-R5-F5** is a major but mandatory next-artifact blocker, and
**P2-R5-F10** is a required audit repair. Under the plan's own sequencing, no
profile contract may begin from this revision. If the owner authorizes a path
forward after this final review, the six items in “Must block the
profile-contract artifact” must be settled before artifact 2; the remaining
conditions may be carried only at the bounded checkpoints and with the
closure tests listed above.

# Phase 2 plan review, round 4

**Reviewed:** 2026-08-11

**Plan:** `docs/plans/phase-2-generator.md`, revision 3

**Review type:** plan-only ratification gate; no Phase 2 implementation exists

## Outcome

Revision 3 makes several real repairs. The process-start boundary, genuine
per-role producer shapes, four named structural loader limits, seed grammar,
fully determined seed invariance, and the third scanner-documentation
correction are now stated at plan level. Owner decisions 5, 6, and 7 are
settled and are not reopened here.

Their consequences are not carried consistently. The datetime matrix requires
source syntax that decision 5 forbids; decision 6 leaves an impossible exact
multiplicity obligation; and decision 7 silently falls back from exact numeric
facts outside the one example it names. The inherited all-different rule also
conflicts with normalized label and datetime output independently of the
declared-identifier exception. The new existing-target rule neither proves
ownership of the current CSV nor fits the plan's own permitted-read boundary,
and the NumPy scalar route still loses the provenance round 3 required.

Four of the eleven round-3 items close fully. Five still carry blocking
defects, one retains a major defect, and the traceability item remains minor.
Fresh review of the rewritten surfaces found additional blocking and major
items below.

## Review basis and method

I read the complete required baseline: `CLAUDE.md`, `AGENTS.md`,
`SECURITY.md`, the Phase 0 public-skeleton plan (especially D6.2 and D12), the
Phase 1 profiler plan at revision 5, the Phase 1 round-8 review, and all three
prior Phase 2 plan reviews. Every citation below was re-derived against
revision 3 rather than carried forward from revision 2.

Claims about producer shape, datetime parsing, raw and folded identity,
existing-target replacement, command initialization, reader limits, and
scanner origin propagation were checked against `src/synthtwin/profile.py`,
`taxonomy.py`, `parsing.py`, `reading.py`, `cli.py`, `errors.py`,
`tools/offline_scan/scan_imports.py`, and
`tools/decontamination/check.py`. I also ran neutral producer, ordinary-reader,
JSON-parser, NumPy-result, transaction, scanner, and content-gate checks.

The seven owner decisions in P2-D0 are treated as settled choices. This review
asks whether revision 3 implements their stated scope and costs, whether it
silently adds another owner-level choice, and whether the ratified antecedent
plans record the amendments.

## Closure of every round-3 item

The final column is an independent closure check. For a live item it includes
a concrete surviving failure scenario. An adjacent defect introduced by a
revision-3 change is assigned a round-4 identifier rather than used to rewrite
the historical round-3 finding.

| Round-3 item | Judgment | Remaining severity | Independent closure check |
|---|---|---:|---|
| P2-R3-F1 | **Closed narrowly.** P2-D1 now begins at installed-entry-point process start, requires lazy reader-bearing command imports, covers initialization/prologue/body/post-write, names the neutral helper moves, and adds an initializer mutation (`phase-2-generator.md:124-158`). | None for the original pre-dispatch hole. Fresh P2-R4-F1 applies. | The installed entry remains `synthtwin.cli:main` (`pyproject.toml:33-34`), and the current `cli.py:42-50` imports `profile`, `reading`, and `read_table` before dispatch. Revision 3 now requires exactly the split needed to remove that route. Its new permitted-read rule conflicts with ownership verification, but that is a fresh cross-section defect rather than the old missing-startup extent. |
| P2-R3-F2 | **Partly closed.** Array-result, writer, handle, row, and dialect origins are now named, and the false NumPy-independence claim is withdrawn. Derived NumPy scalars are expressly stripped of origin, and the exact `integers` argument forms and origins remain unspecified. | **BLOCKER; P2-R4-F2.** | `draws[0]` from the required uint64 array is a `numpy.uint64`, not a Python integer, and exposes native attributes and methods before `int(...)`. Revision 3 says that value has no library origin (`phase-2-generator.md:693-702`) and has no scalar mutation (`:717-721`). An implementation following that rule can accept `word.data` through the shipped scanner's untraced-attribute route while the array-origin mutations remain green. |
| P2-R3-F3 | **Partly closed.** The recursion now reaches the finished document and top-level notes, but the acceptance policy it applies is still deferred to the later contract. | **MAJOR; P2-R4-F8.** | P2-D2 says leaf classes, path-sensitive classes, and nested-container behavior will be fixed in artifact 2 (`phase-2-generator.md:217-226`), although sequencing forbids later artifacts from choosing an open mechanism (`:35-48`). A future source-derived string at the already-allowed `publication_notes[*].note` path remains indistinguishable from current prose under a path-and-type whitelist. |
| P2-R3-F4 | **Partly closed.** Owner decision 5 resolves the offsetless date and quarter choice, scopes it to twin CSV cells, and carries it into bytes and datetime vectors. The matrix reverses the earlier correct disposition for source `format`, and the Phase 0 record remains unamended. | **BLOCKER; P2-R4-F3 and P2-R4-F7.** | A genuine compact-date profile publishes `format: compact-date`; a slash-date profile publishes `format: month-first-date`. Decision 5 requires their twin cells to be ISO dates (`phase-2-generator.md:65-77`), while the matrix calls `format` EXACT-OBSERVABLE (`:365-375`). Reprofiling necessarily returns `iso-date`, so no output satisfies both rules. |
| P2-R3-F5 | **Partly closed.** The three cited producer-shape errors are repaired: document versus numeric-echo `n_rows`, the empty role, and datetime cardinality now have separate rows (`phase-2-generator.md:290-309`). The claimed exhaustive matrix is still not ratifiable because the datetime, identifier, numeric, and all-different consequences below are contradictory, and two emitted structural keys have no written disposition. | **BLOCKER through P2-R4-F3 through P2-R4-F6; MAJOR P2-R4-F9.** | Per-role probes agree that only count and continuous blocks carry the numeric `n_rows` echo and that empty blocks carry both zero distinctness fields. But a validator generated from the complete written matrix still cannot satisfy the exact `format`, identifier multiplicity, and numeric folded-count rows for genuine profiles. |
| P2-R3-F6 | **Partly closed.** Owner decision 7 fixes the original `0`/`0.0` fixture, the method and byte path name the permitted forms, and the local twin-CSV/profile-document scope is precise. The bounded pair does not cover the producer's valid numeric domain, and the fallback relaxes exact facts without owner authorization. | **BLOCKER; P2-R4-F5 and P2-R4-F7.** | A genuine three-row count column containing three different zero spellings publishes three present and three raw/folded distinct values, all parsed as whole-number zero. Decision 7 permits only two output spellings. Lines 356-359 and 407-409 approximate the miss, while lines 516-521 still require all-different output on every role. |
| P2-R3-F7 | **Partly closed.** Owner decision 6 authorizes repeats, demotes raw distinctness, and reaches the report, honest-limits section, genuine fixture, and general all-different statement. Anonymous multiplicity remains exact, folded distinctness has no infeasible-corner disposition, and the local D9 wording does not repeat the declared-identifier-only scope. | **BLOCKER; P2-R4-F4 and P2-R4-F7.** | The named all-singleton profile has `n_distinct_by_occurrences = {"1": 200}`. Any authorized repeated output changes that map, but the identifier row still calls it EXACT-OBSERVABLE (`phase-2-generator.md:382-387`) and generation still promises to honor it (`:513-521`). |
| P2-R3-F8 | **Closed narrowly.** The four specifically required limits, numeric values, pre-parse structural scan, matching producer bounds, producer-time refusal, and near/over tests are fixed (`phase-2-generator.md:194-205`). | None for the four requested limits. Fresh P2-R4-F10 and P2-R4-F11 apply. | The 10,000,000-character string limit matches the shipped reader constant at `reading.py:239-246`. A separate numeric-token route and the authority to contract the Phase 1 producer domain were not the four missing values in round 3 and are recorded as fresh items. |
| P2-R3-F9 | **Closed.** The ASCII-decimal grammar, normalization, range, accepted/refused boundary spellings, scoped sensitivity, and fully determined seed invariance are fixed (`phase-2-generator.md:473-489,675-676`). | None. | `0` and the uint64 maximum have explicit accepted spellings; adjacent overflow, sign, underscore, whitespace, and non-ASCII forms are refused. Leading zeros preserve the numeric seed, and a determined twin may not change bytes with the seed. |
| P2-R3-F10 | **Closed.** The scanner's accepted-built-in paragraph is the third named correction and is asserted with the other documentation fixes (`phase-2-generator.md:228-236`). | None. | The named correction directly reaches the still-false shipped paragraph and includes length, truth, iteration, conversion, formatting, and hashing, so implementation cannot claim closure after editing only SECURITY and the Phase 1 plan. |
| P2-R3-F11 | **Not closed.** The ambiguous body citation is gone, but the requested all-22 round-1 checklist or mechanical equivalent is still absent. | **MINOR; P2-R4-F12.** | The closure trail enumerates round-2 and round-3 identifiers only (`phase-2-generator.md:782-817`). Its prose assertion that round 2 carried every live round-1 item cannot reveal a dropped or incorrectly mapped identifier. |

## Review items

### P2-R4-F1 — The ownership proof is stale, and reading it violates the boundary

**Severity: BLOCKER.**

**Location:** revision 3 lines 143-146, 539-554, 672, and 768-770;
`src/synthtwin/profile.py:1209-1264,1305-1337`.

The current transaction really does replace ordinary files at both targets.
Revision 3 attempts to authorize default replacement from a report marker and
the twin file name recorded in that report. Those facts prove only that the
report once referred to a file with that name. They do not prove that the
current CSV at that path is the same artifact. Calling this “positive proof”
overstates what was verified.

The mechanism is also forbidden by P2-D1 as written. That section permits the
generate process to read “the profile document through the loader, and
nothing else.” Recognizing the marker and recorded name necessarily reads the
existing report. Binding the report to the current twin bytes would also
require reading the twin. A normal repeat run therefore cannot satisfy both
sections.

**Failure scenario:** a successful run leaves `sample-twin-report.txt` in
place. The user moves the accompanying twin elsewhere and puts an unrelated,
valuable CSV at `sample-twin.csv`. A default rerun reads the genuine stale
report, sees the expected name, calls the inherited transaction, and replaces
the unrelated CSV without `--replace`.

**Required closure:** either return to refusal whenever either target exists
unless `--replace` is explicit, or bind the report to the exact current twin
bytes with a digest or equivalent. If binding is chosen, P2-D1 must enumerate
narrow, bounded reads of the exact validated report and twin targets solely
for ownership verification. Add stale-report, copied-report, substituted-CSV,
other-path, oversized-target, link/alias, and between-check-and-write
mutations. Marker plus file name alone is not proof.

### P2-R4-F2 — E8 still launders scalar and argument origins

**Severity: BLOCKER.**

**Location:** revision 3 lines 458-468 and 690-721;
`tools/offline_scan/scan_imports.py:38-49,733-744,2026-2095,2140-2197`.

The array-result repair is real, but its next sentence removes the origin from
values derived from that array. A uint64 element remains a NumPy scalar until
an explicit conversion. A direct probe under the locked environment found
`data`, `dtype`, `flags`, `dump`, `dumps`, and `tofile` on that scalar. The
shipped scanner intentionally accepts attribute reads on untraced values and
already demonstrates the correct security shape by preserving restricted
origin across a subscript. Revision 3 would undo that property for the new
scalar route.

The shipped restricted-instance tables are keyed only by the first module
component (`scan_imports.py:3030-3052,3250-3283`). Adding `integers` to one
`numpy` method set would therefore grant the same method policy to Generator,
array, and scalar origins, although revision 3 requires three different
surfaces. The plan names distinct returned types without choosing the type-
sensitive origin and lookup change needed to enforce them.

The “one draw form” is also not executable policy. P2-D8 specifies a
full-width uint64 draw conceptually but never fixes the positional/keyword
forms or the origins of `low`, `high`, `size`, `dtype`, and `endpoint`. The red
list contains no caller-derived draw-argument mutation. D6.2 requires that
granularity because these arguments can invoke object protocols while the
method name remains the permitted `integers`.

**Failure scenario:** generation indexes the permitted array and reads
`word.data` before converting `word`. Because the plan declares the scalar
originless, the unenumerated native attribute passes through the scanner's
documented untraced-attribute residual; all array-attribute mutations still
fail as intended because they test `draws`, not `word`. Separately, a helper
can forward a caller-derived `size` object to the permitted method without a
named argument-origin mutation failing.

**Required closure:** add distinct Generator, array, and NumPy-scalar origins;
propagate scalar origin through indexing and iteration; give the scalar empty
attribute and method sets until an explicitly checked `int(...)` conversion;
add a type-sensitive restricted-instance lookup; and add scalar lost-origin
mutations. Fix the exact `integers` signature and first-party origin rule for
every slot and every accepted argument form. The claim at lines 701-702 should
also be narrowed or corrected: pandas already occupies a non-empty restricted-
instance attribute table.

### P2-R4-F3 — Decision 5 is contradicted by the datetime matrix

**Severity: BLOCKER.**

**Location:** revision 3 lines 65-77, 365-375, 426-451, 564-566,
660-662, and 740-742; `src/synthtwin/parsing.py:61-71`;
`src/synthtwin/taxonomy.py:2054-2072,2168-2208`.

Decision 5 chooses ISO twin syntax at the recorded precision and offset state.
It does not choose the real file's parser-family spelling. The producer emits
that parser family as `format`; genuine compact and slash-date probes produced
`compact-date` and `month-first-date`. An ISO date twin reprofiles as
`iso-date`. Calling `format` EXACT-OBSERVABLE is therefore impossible under
the settled decision. Withdrawing R-P2-7 entirely also hides the remaining
source-lexical-format loss.

`datetimes_read_at` has the opposite classification error. It is marked
EXACT-CONTROL, but `_datetime_reading` derives it entirely from the offset
diversity in the CSV. A four-row, two-offset genuine profile produced
`datetimes_read_at: utc`, a pooled `(withheld): 4` offset map, and withheld
endpoint offsets. One invented rare offset can preserve the pooled map and
endpoints while reprofiling as `local`; a dispatch assertion cannot detect
that byte-level miss.

**Failure scenario:** a 28-row column of month-first slash dates publishes
`format: month-first-date`, date precision, and no offset. The generator writes
the required ISO date cells. Reprofiling returns `format: iso-date`, so the
EXACT-OBSERVABLE check fails. If validation instead trusts the source field,
the report falsely says the written CSV reproduced a fact it did not.

**Required closure:** restore source `format` to REPORT-ONLY and disclose that
lexical format is not preserved. Make `datetimes_read_at` EXACT-OBSERVABLE and
recount it from the twin. The method specification must fix how one versus
multiple invented offsets represent a withheld offset state. Retain a scoped
residual for source-format loss rather than withdrawing R-P2-7 wholesale.

### P2-R4-F4 — Decision 6 leaves multiplicity exact after authorizing repeats

**Severity: BLOCKER.**

**Location:** revision 3 lines 78-97, 170-178, 249-254, 311-321,
382-424, 513-521, 631-634, and 743-745; Phase 1 plan lines 433-447 and
516-566.

Revision 3 correctly carries the owner choice into raw distinctness, the
report, honest limits, and the named conflict fixture. It does not carry the
choice into the anonymous repetition multiset. The loader invariant requires
that map's entries and weighted keys reconcile with distinct and present
counts, the identifier row calls it EXACT-OBSERVABLE, and generation promises
to honor it. Once an invented value repeats where every source value was a
singleton, exact reproduction is mathematically impossible.

The infeasible-corner disposition is also stated only for raw distinctness.
The general invention rule still calls folded distinctness exact, although the
named one-character fixture publishes 122 folded identities and the only
concrete widened one-character domain in the plan is printable ASCII. At a
minimum the plan must state and prove the folded capacity or give that field
an explicit corner disposition. The D9 sentence “where the facts are jointly
infeasible” should locally repeat that decision 6 applies only to a declared
identifier; D0's scope is precise, but D9's is not.

**Failure scenario:** the genuine named profile publishes 200 present, 200 raw
distinct, and `{"1": 200}` at length one. Decision 6 makes at least one
invented value repeat to keep the length. The reprofiled map then contains an
occurrence key above one and fewer singleton groups. Raw distinctness is
allowed to miss, but the exact multiplicity validator must reject the owner-
required output.

**Required closure:** define dispositions for raw distinctness, folded
distinctness, and `n_distinct_by_occurrences` together in the infeasible
corner; report every published and achieved miss, not only a duplicate count;
and add independent recounts and mutations for all three. Repeat the
declared-identifier-only scope in P2-D9. Amend the antecedent Phase 1
multiplicity promise as required by P2-R4-F7.

### P2-R4-F5 — Decision 7 covers one fixture, not the numeric producer domain

**Severity: BLOCKER.**

**Location:** revision 3 lines 98-113, 311-321, 349-359, 398-424,
428-450, 516-521, 564-566, 660-667, and 746-748;
`src/synthtwin/taxonomy.py:1334-1344,1412-1467,3390-3395`.

The canonical/one-decimal pair can reproduce the original 100-cell fixture,
and revision 3 carries that covered case into the method, deterministic bytes,
goldens, and report. It is not enough for every genuine profile. The producer
counts exact raw spellings and separately folded spellings, without limiting
either count to two forms per parsed number.

Revision 3 responds by applying a two-sided envelope when the two spellings
cannot supply the count. That is a new fidelity decision, not a consequence
authorized by owner decision 7, whose text says the published raw count is
reproduced. It also conflicts with D9's unchanged all-different rule. A second
genuine shape shows that raw capacity is not the only problem: case-paired
exponent spellings can publish 50 raw but 25 folded identities; canonical and
one-decimal output can supply 50 raw strings but they remain 50 folded
identities.

The reader rationale is factually wrong for the shipped ordinary reader.
Pandas reads `0`, `+0`, and `00` as `int64`, not text. Replacing those cells
with a mix containing `0.0` yields `float64`. R-P2-9's “less tidy” sentence
does not disclose that type dispatch can change.

**Failure scenario:** a genuine three-row count column contains `0`, `+0`, and
`00`. It publishes three present, three raw and folded distinct values,
whole-number status, three zeros, and equal endpoints. The permitted output
set has only `0` and `0.0`. An implementation follows the fallback and repeats
one spelling; the exact distinctness and all-different obligations fail, and
ordinary pandas code takes a floating-point path on the twin after taking an
integer path on the real file.

**Required closure:** obtain an owner disposition for valid profiles that need
more than the permitted pair or need fold collisions the pair cannot express.
The owner must choose which of raw distinctness, folded distinctness,
all-different behavior, bounded spelling vocabulary, or generation
compatibility yields. Carry that result into the matrix, method, feasibility
battery, report, honest limits, and residuals. Correct the ordinary-reader
claim and name the possible dtype change. This does not reopen the settled
two-spelling choice for the case it actually covers.

### P2-R4-F6 — The universal all-different rule is impossible for normalized roles

**Severity: BLOCKER.**

**Location:** revision 3 lines 62-64, 285-321, 361-375, 495-524, and
655-667; Phase 1 plan lines 442-447.

Decision 6 is the only stated exception to the inherited rule that a column
publishing `n_distinct == n_present` produces all-different output on every
role. But label roles intentionally write normalized identities and refuse to
invent unpublished spelling variants. A valid label column can be raw-unique
and folded-nonunique. The exact level allocation then necessarily writes
duplicates. Date normalization creates the same conflict when many raw-unique
spellings parse to a smaller set of dates.

Calling label raw distinctness REPORT-ONLY does not resolve the separate D9
obligation, and owner decision 6 is expressly limited to declared
identifiers. If owner decision 4 was intended to authorize this additional
loss, the plan does not say so or carry its join/de-duplication cost.

**Failure scenario:** with valid `small_cell_floor = 1`, a genuine binary
column contains `A`, `a`, `B`, and `b`. The producer emits four present, four
raw distinct, two folded distinct, and normalized levels `a: 2` and `b: 2`.
The specified twin writes `a, a, b, b` to meet the exact level counts. A join
or duplicate check developed on the twin sees repeated keys although every raw
source cell was different, directly violating lines 516-521.

**Required closure:** reconcile the trigger and equality notion for every
role, not only identifiers. Either make all-different binding and choose an
output representation that can satisfy it, or obtain and record the owner-
level exceptions for normalized label, datetime, and numeric shapes. Give
every exception an explicit matrix disposition, report sentence, honest-limit
consequence, and per-role mutation. A generic “facts are infeasible” sentence
is not authorization.

### P2-R4-F7 — The ratified antecedent plans still state the superseded rules

**Severity: BLOCKER.**

**Location:** Phase 0 D12 at `phase-0-public-skeleton.md:426-460`;
Phase 1 plan lines 433-447 and 516-566; revision 3 lines 65-113 and
782-825.

Revision 3 scopes decisions 5 and 7 precisely enough inside this plan: both
say twin CSV cells only and expressly preserve profile-document canonical
serialization. That wording does not invite a future reader to apply the
exception to profile JSON. The older canonical record nevertheless remains
unconditional: Phase 0 still requires explicit datetime offsets and one
canonical numeric spelling. It also still requires identifiers to be drawn
without replacement, which decision 6 overrides in its one infeasible corner.
Phase 1 still says the anonymous multiset lets Phase 2 reproduce the
repetition pattern.

Under the repository's plans-before-code protocol, a later plan saying that
an earlier rule was amended does not make two conflicting normative texts safe
to implement. The earlier text needs a dated, scoped amendment record. This is
recording settled decisions, not reopening them.

**Failure scenario:** one implementer follows Phase 0 D12 and refuses an
offsetless date, emits only one spelling per numeric value, and expands an
identifier's width to avoid replacement. Another follows revision 3 and does
the opposite in all three cases. Both can cite a ratified plan, so code review
cannot identify deviation from the canonical rule.

**Required closure:** add recorded amendments to Phase 0 D12 for (1) twin CSV
datetime cells at the published precision/offset state, (2) the bounded twin
CSV numeric spelling exception, and (3) replacement only in decision 6's
declared-identifier infeasible corner. State in that record that profile JSON
remains canonical. Add the corresponding scoped amendment to Phase 1's
all-different and multiplicity promises. Preserve the historical text and
date the amendment rather than silently rewriting the record.

### P2-R4-F8 — The finished-document traversal still has no ratified acceptance rule

**Severity: MAJOR.**

**Location:** revision 3 lines 35-48 and 217-226;
`src/synthtwin/profile.py:241-277,309-355`.

Moving recursion from a column block to the finished document closes the
specific structural bypass. It does not decide what that recursion accepts.
The plan leaves leaf classes, path-sensitive classes, and nested behavior to
the later contract even though that contract may only carry out decisions
already made here.

A type-and-path whitelist alone cannot distinguish current neutral note prose
from a future note built by interpolating a source spelling: both are strings
at `publication_notes[*].note`. The shipped producer confirms that notes are
lifted after `_column_block`, so this is a real route rather than a hypothetical
key.

**Failure scenario:** a future no-value-publication role adds a note at the
existing allowed path and inserts one source cell into the sentence. The
finished-tree recursion sees an allowed string at an allowed path; matrix
completeness sees no new key; the source spelling is serialized.

**Required closure:** choose the enforcement mechanism in this plan. For
example, require origin-tagged publication values with a closed constructor
set, or a fixed value-free note grammar whose producer cannot populate from a
cell. Enumerate allowed leaves, path rules, nesting, provenance propagation,
and a same-path/same-type source-interpolation mutation before artifact 2.

### P2-R4-F9 — The written matrix omits emitted structural keys

**Severity: MAJOR.**

**Location:** revision 3 lines 323-331, 393-396, 652-659, and 761-765;
`src/synthtwin/profile.py:323-355`.

The top-level disposition paragraph omits `columns` and the `source`
container, although `build_document` emits both and the completeness assertion
promises every top-level key with no exceptions. Dispositions for the leaves
inside `source` do not give the container key a disposition, and no general
structural-container class is defined.

**Failure scenario:** the v4 producer retains the shipped top-level document
shape. The required completeness test encounters `columns`, finds no matrix
row, and fails before generation. If implementation silently exempts
structural containers, it passes only by adding the implementation-time
exception lines 393-396 prohibit.

**Required closure:** enumerate both keys or define and ratify a structural-
container disposition that covers them and says what output evidence, if any,
their ordering and membership impose. Run completeness over full key paths so
container and leaf coverage cannot be conflated.

### P2-R4-F10 — The pre-parse limits omit JSON numeric-token length

**Severity: MAJOR.**

**Location:** revision 3 lines 188-212, 603-612, and 646-651.

The byte, depth, container, and string limits do not bound a JSON number token.
A document well below 64 MiB, with shallow nesting, one small container, and
no long string can still carry a multi-thousand-digit integer. The structural
pre-scan passes it to plain `json.loads` before schema range checks.

Under the locked Python 3.13 environment, a direct 5,000-digit integer probe
raised a raw `ValueError` at the interpreter's 4,300-digit conversion limit.
That limit can differ by runtime or configuration. The input is syntactically
JSON, but it receives neither the promised parse-position message nor a stable
schema-range refusal.

**Failure scenario:** `n_rows` is written as one 5,000-digit canonical decimal
token in an otherwise small v4-shaped document. The four pre-parse bounds all
pass. One supported runtime raises an uncatalogued conversion exception;
another with a higher limit parses it and reaches the plain-language range
check. User-visible behavior and resource work now depend on interpreter
configuration.

**Required closure:** set and enforce a numeric-token digit bound in the
first-party pre-scan before `json.loads`, including integer, fraction, and
exponent components as applicable. Give the refusal its own plain-language
shape and add near/over, very long integer, and runtime-limit mutations.

### P2-R4-F11 — Producer-side caps are an unratified product-domain contraction

**Severity: BLOCKER.**

**Location:** revision 3 lines 194-205 and 749-751; Phase 1 plan lines
311-318 and 924-930.

Fixing the loader limits is an implementer-level security mechanism. Giving
the already shipped profiler those limits and refusing tables whose profile
would exceed them is a separate product-support decision. Phase 1 says wide
and multi-gigabyte tables are supported within available memory and lists
memory exhaustion, not profile-byte or container-count caps. Revision 3 now
withdraws part of that accepted domain with only a residual, not an owner
record.

**Failure scenario:** on a machine with enough memory, a very wide valid table
would produce a canonical v4 document just over 64 MiB. The Phase 1 contract
says the table is supported within memory, but the revised profiler refuses it
before writing. A user upgrading solely to obtain the generator loses a
previously promised profiling path.

**Required closure:** obtain and record the owner's acceptance of the 64 MiB,
depth, container, and producer-side domain contraction, or record explicit
delegated authority for resource caps and amend Phase 1's support statement.
Keep R-P2-10, but do not treat disclosure as authorization. The exact numeric
cap choices can remain implementation-level only after the product-domain
decision is owned.

### P2-R4-F12 — The closure trail still cannot audit all round-1 items

**Severity: MINOR.**

**Location:** revision 3 lines 782-817; round-3 review P2-R3-F11.

The trail asserts that round 2 checked every one of the 22 round-1 items,
then prints only round-2 and round-3 rows. This is the same transitive assurance
round 3 rejected, not the requested checklist or mechanical equivalent.

**Failure scenario:** a later revision maps one round-1 finding to the wrong
round-2 item or drops it while preserving the prose assertion. The printed
table remains complete by its own reduced key set, so the omission is not
detectable from revision 3.

**Required closure:** enumerate P2-R1-F1 through P2-R1-F22 with current status
and successor, or add a mechanical reference check that fails when any one is
missing or multiply/incorrectly mapped.

## Owner decisions, authority, and residual R-P2-1

### Decision 5

The twin-CSV-only scope is precise, and the plan carries the decision into the
method, byte contract, datetime vectors, and golden hashes. It does not carry
the remaining source-format loss or the output-derived clock field correctly.
P2-R4-F3 gives the required matrix and disclosure repairs. Phase 0 needs the
scoped amendment record in P2-R4-F7; that record does not reopen the choice or
change profile JSON.

### Decision 6

The plan correctly keeps published length, permits the minimum necessary
repetition, demotes raw distinctness, names duplicate/join behavior in the
report, and preserves the general obligation where feasible. It fails to
disposition the anonymous multiplicity map and folded distinctness, and D9's
local exception is broader in wording than D0. Phase 0's no-replacement rule
and Phase 1's multiplicity promise also remain unamended. P2-R4-F4 and
P2-R4-F7 are consequence repairs, not attempts to revisit length winning.

### Decision 7

The local scope protects profile serialization, and the covered two-spelling
case reaches method determinism, report/twin bytes, reference work, and CI
goldens. The plan does not define a settled result when two
spellings cannot preserve raw or folded facts, and it understates the ordinary-
reader dtype consequence. P2-R4-F5 requires a further owner disposition for
that uncovered domain. It does not reopen the settled pair where the pair is
sufficient.

### Decisions treated as implementer-level

Most remaining repairs are properly implementer-level: scanner origin
propagation, datetime field dispositions, a sound ownership-binding mechanism,
publication-guard mechanics, structural matrix rows, and numeric-token bounds.
Two choices are not:

1. The fallback that relaxes numeric raw/folded distinctness and all-different
   behavior is an owner-level fidelity choice (P2-R4-F5).
2. Retrofitting finite document/container caps into the shipped Phase 1
   producer withdraws a supported input domain and needs owner assent or an
   explicit delegation record (P2-R4-F11).

The cross-role all-different exceptions in P2-R4-F6 are likewise owner-level
unless the record shows that owner decision 4 already and explicitly
authorized them. The current one-line summary does not.

### Residual R-P2-1

R-P2-1 is correctly left open. The shipped numeric-unrepresentable block
publishes whole/fraction and sign marginals but no digit width
(`taxonomy.py:2415-2422`). Revision 3 does not infer or publish a real width;
it invents one disclosed canonical width and flags any new real-derived width
fact for the owner. That is the honest non-assumption required at this gate.

## What was checked

### Surfaces

- Every revision-3 decision P2-D0 through P2-D14, sequencing rule, residual,
  acceptance criterion, and closure-trail claim.
- Every P2-R3-F1 through P2-R3-F11 closure claim, plus the round-1/round-2
  record needed to test transitive closure and regressions.
- Shipped top-level, source, settings, note, empty, label, count, continuous,
  datetime, free-text, identifier, and numeric-unrepresentable producer
  shapes, including new v4 axes and multiplicity additions on paper.
- Raw versus folded identity, numeric parsing versus spelling, label
  normalization, datetime parser family, precision, offset pooling, clock,
  document versus numeric row counts, and repetition maps.
- Installed command startup, lazy-import target graph, process-start extent,
  permitted reads, loader-only data flow, serializer/writer moves, output
  naming, target identity, existing-target proof, and both transaction sides.
- Strict JSON loading, canonical round-trip, duplicate keys, malformed text,
  byte/depth/container/string limits, numeric tokens, producer compatibility,
  and failure-message reachability.
- One-stream determinism, uint64 draw shape, seed lexical forms, determined
  profiles, numeric/datetime cell spellings, exact report/twin bytes, and
  golden/reference-vector obligations.
- Scanner module names, bare/dotted bindings, Generator/array/scalar/writer
  origins, restricted attributes and methods, `integers` arguments, output
  handles, row sources, callback slots, and lost-origin routes.
- Publication recursion over the finished document, top-level notes, leaf and
  container classes, path sensitivity, origin tracking, and same-path leaks.
- Public handling, privacy, temporary-private/deferred-control, D12 amendment,
  and Phase 1 support claims across the required baseline.

### Properties and attack classes

- Offline and profile-only generation from process start, including module
  initialization, aliases, re-exports, unexpected reads, caller objects,
  native-backed values, callback protocols, and dynamic output handles.
- Silent statistical wrongness through raw/folded collapse, repeated keys,
  exact multiplicity, numeric lexical aliases, ordinary-reader dtype changes,
  datetime syntax/clock changes, and validator evidence that cannot observe
  the claimed fact.
- Type misrouting across integer/floating readers, normalized labels, declared
  identifiers, header controls, and new axis-based dispatch.
- Determinism under argument grammar, draw order/count, scalar conversion,
  spelling allocation, fixed special placement, platform/lock scope, and
  fully determined profiles.
- Destructive replacement through stale or copied proof, swapped target
  contents, path aliases, first/second-target symmetry, transaction rollback,
  and check-to-write changes.
- Contract fail-closed behavior for unknown/missing keys, structural
  containers, non-canonical and oversized tokens, runtime-dependent parsing,
  producer/loader domain mismatch, and implementation-time exceptions.
- Source-derived publication through notes, nested containers, same-key
  interpolation, display boundaries, formula-context warnings, and report
  claims.
- Zero-code usability through stable refusal shapes, exact path naming,
  no-table remediation, achieved-versus-published reporting, and honest
  limitations.

### Checks that did not produce additional items

- The process-start diagnosis and named lazy-import/neutral-helper repair match
  the installed entry point and current reader-bearing imports.
- Flat role keys, one-based positions, numeric-only per-column `n_rows`, the
  empty-role shape, and the finished-document note route match shipped code.
- The four named structural limits are fixed and have matching producer-side
  values; the additional resource items concern a different token class
  and authority for the compatibility change.
- The seed grammar and determined-profile invariance are sufficiently precise
  at plan level.
- The third documentation correction reaches the actual accepted-built-in
  prose, and the false NumPy-independence claim is withdrawn.
- Header-source behavior, the leading-U+FEFF quoting exception, display
  boundary, narrowed formula-context battery, and complete-artifact handling
  inventory remain coherent.
- Decision 5 and decision 7 are locally scoped tightly enough that their text
  does not amend profile-document serialization. The defect is the unchanged
  Phase 0 record, not local scope ambiguity.
- The plan does not claim public-repository controls currently deferred by
  `SECURITY.md`, and it does not claim Phase 2 code or numeric oracles exist.
- R-P2-1 remains an honest open owner question rather than an assumed width
  fact.

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
- In-memory producer probes confirmed compact and month-first source `format`,
  withheld mixed-offset clock state, numeric raw/folded spelling conflicts,
  numeric-only row echoes, empty-role fields, normalized label collisions,
  and the declared-identifier singleton multiset.
- Under the locked environment, a uint64 draw element remained
  `numpy.uint64` with the native attributes named in P2-R4-F2.
- Ordinary pandas probes read the three integer-looking zero forms as `int64`
  and a canonical/one-decimal mix as `float64`.
- Plain `json.loads` under Python 3.13.14 raised `ValueError` for a 5,000-digit
  integer before schema validation.
- Inspection of the current writer confirmed replacement of ordinary targets
  on both transaction sides; inspection of the scanner confirmed restricted
  subscript propagation, the untraced-attribute residual, and the current
  `csv.reader`-only dialect callback entry.
- The review file was added only to a copied temporary Git index, with objects
  directed outside the repository. `git ls-files --error-unmatch` resolved
  this exact path from that index, and the unchanged no-argument content gate
  read the index and returned clean. The repository index was not modified;
  the review still needs to be staged by the maintainer.
- This remains a paper review. The v4 contract, generation-method
  specification, reference vectors, and Phase 2 implementation do not exist
  and were not reviewed.

## Verdict

**REJECT.** The blocking items are **P2-R4-F1 through P2-R4-F7 and
P2-R4-F11**. Revision 3 may not be ratified, and no Phase 2 contract, method,
reference vector, or implementation may begin, until those items are closed
in a revised plan and the settled amendments are recorded in their antecedent
plans. **P2-R4-F8 through P2-R4-F10 and P2-R4-F12** are also required repairs;
they do not authorize deferring publication enforcement, complete matrix
coverage, parser bounds, or auditable closure into implementation.

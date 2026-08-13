# Phase 1 — The profiler: reading and automatic type analysis

**Status:** revision 5 — the implemented plan, after review rounds 1-8.
Revision 5 records what the round-8 repairs changed and the owner
decision taken with them; it describes no behaviour those repairs did
not make true. What changed in the text: the transaction section
(P1-D5) described machinery the rebuild removed — a renaming step that
opened a handler of its own, and a remaining window called one
bytecode boundary wide that had never been measured — so it is
rewritten around one function with one handler, the measurement that
replaces that claim, the two residuals that actually remain, and the
third bound that has always been in the command rather than in the
transaction (P1-R8-F1); P1-D8 gains the transaction battery those
residuals are stated against. P1-D5 also states the number
`profile_version` carries and records the owner decision of 2026-08-10
that a declared-identifier column publishes an anonymous count
multiset, advancing that number to 3 (P1-R8-F4), with P1-D4 item 8,
P1-D6 and the list of decisions taken during implementation carrying
the same decision where they describe the role, what the profile
publishes, and the record of what was settled when. No other section
changed. Earlier revisions are recorded below, newest first.

**Status:** revision 4 — the implemented plan, after review rounds 1-7.
Revision 4 changes no behaviour. It corrects sentences that described
retired designs as though they were operative, and one claim that
overstated a safety property. What changed in the text: the R2 residual
now names unresolved implicit protocol dispatch as a CLASS rather than
naming attribute reads as the one construct left, and it corrects the
premise this document had attributed to Phase 0 (P1-D8.1); P1-D2.1 now
says that the run-time `validate_local_path` is the operative reader
control and the scanner a best-effort second layer; the first-row
paragraph states the four outcomes the reader actually has, ending in
the convention of residual R1 (P1-D3); the P1-D4 introduction no longer
carries an inference ordering for `identifier`; P1-D11 states the exact
integer method as the current one and marks the floating-point
reduction as history; the dependency text says pandas is the one direct
runtime dependency; and P1-D5, P1-D6 and P1-D8 record the declared-value
publication rule, the settings-block rule, the transaction's coverage,
and the scope of the disclosure battery. Earlier revisions are recorded
below, newest first.

**Status:** revision 3 — the implemented plan, after review rounds 1-6.
Revision 3 records the round-6 outcome: identifier inference WITHDRAWN
(P1-D4 item 8), one taxonomy policy replacing two contradictory ones
(P1-D4), the first-row convention confirmed by the owner on 2026-08-09,
the sentinel options exposed on the command line (P1-D6), and three
residuals stated as accepted limits (P1-D8.1). Revision 2 recorded the
round-5 redesign, described below.

**Status:** revision 2 — the implemented plan, after review rounds 1-5.
Revision 2 records the round-5 redesign: the retired conditioning limit
(P1-D11), the reordered taxonomy with `numeric_unrepresentable` and
`identifier` as a last resort (P1-D4), the explicit first-row verdict
and the two-reader value agreement rule (P1-D3), and the transactional
two-file write (P1-D5). Revision 1 was the plan as first implemented. Revision 0 was the draft
prepared while the Phase 0 closure review completed; this revision fixes
every decision the draft left open, records the owner decisions taken
since, and states exactly what the implementation does. The changes from
the draft are listed at the end, so the reviewer never has to diff two
documents to find them.

**Sequencing — owner decision, 2026-08-07.** The standing process is
plan first: a phase plan is reviewed and ratified before its code exists.
The project owner directed that Phase 1 be implemented first and reviewed
once, as a single combined plan-and-code review, rather than in two
separate rounds. This is an owner override of a reviewer-held condition,
recorded here for the audit trail by the same mechanism as the Phase 0 D2
waiver. The implementer's noted caveat was given and acknowledged: a plan
reviewed only after its code exists loses the cheapest place to catch a
design error, so any design item this review rejects is repaired in code,
not merely in prose. Nothing else about the process changes — the
reviewer's verdict governs, the plan is amended by whatever that verdict
requires, and no Phase 1 claim rests on this document being pre-ratified.

**Scope:** one new command path — `synthtwin profile <table>` — that reads
a local CSV table and produces the profile: the machine-readable schema
description and a plain-language summary of what was detected and what
will be published. **Non-goals:** no generation, no relationships (Phase 2
decides how cross-column structure is profiled), no validator, no
Excel/parquet/database input (later phases), no PyPI release.

The profile is computed FROM real data and is therefore real-derived
material: it is written only to a user-chosen output location through the
path validator, is never committed (the provenance guard and gitignore
already refuse it), and the user is told in plain language that the
profile file is the one artifact that crosses from their compliant
environment to wherever the twin is generated.

---

## P1-D1. The deliverable and its boundary role

**Amended 2026-08-13, at the validator's landing (Phase 3 plan P3-D7,
stage 2; owner decision 6).** The sentence below that everything
downstream consumes the profile AND NOTHING ELSE was written before
`synthtwin validate` existed and is superseded for that command alone.
The validator reads TWO files, the profile and the CSV it was asked to
measure, because measuring a written file against a description means
describing that file with the profiler's own producer; a validator that
recounted beside the producer would be a second implementation of the
profiler and would drift from it. The boundary this plan draws is
unchanged where it matters and is now stated at its true width: the
GENERATOR reads the profile and nothing else, and the module that opens
a CSV is not in its import graph at any instant. The validator in turn
never imports the generator. Nothing else in this section is affected,
and the record of what was written here is left standing rather than
rewritten.

The profiler is the ONLY code path that will ever read real data (charter
rule). Its output contract is therefore the project's central interface:
everything downstream — generator, validator, quality report — consumes
the profile and nothing else. This phase fixes the profile's v1 contract
(P1-D5) with an explicit `profile_version` field so later phases can
evolve it without ambiguity.

The boundary is architectural, not advisory: reading lives in
`src/synthtwin/reading.py`, which is the only module that opens the user's
table, and every other module takes already-read values as arguments. A
generator module added in Phase 2 that imported `reading` would be visible
in one grep, and the offline scanner's first-party import verification
records who imports whom.

## P1-D2. Dependency introduction: pandas, and pandas alone

**What is true today, stated before the history so no paragraph below
can be read as operative:** pandas is the ONE direct runtime dependency
of this project. numpy is present only inside pandas' own transitive
closure — pinned there in the frozen lock because pandas requires it —
and `src/` imports it nowhere; the offline scanner refuses an import of
numpy from `src/` outright (E2 in P1-D10). The owner decision and the
withdrawal that produced that state are recorded next, as the record of
how the phase arrived here.

**Owner decision, 2026-08-07 (partly superseded at review round 1 by
the numpy withdrawal below).** The implementer proposed a zero-runtime-
dependency profiler (standard-library `csv` only) on three grounds: the
code path that touches real data would carry no third-party surface at
all; `pandas.read_csv` is network-capable (it accepts URLs and remote
storage schemes) and so introduces a construct whose fencing depends on
our path validator rather than on its own inability to reach the network;
and published statistics computed in exactly-rounded Python arithmetic are
bit-identical across CPU architectures, where numpy reductions are only
empirically equal. The owner considered that and **directed pandas and
numpy as drafted**, accepting the trade. The controls that answer the
three concerns are P1-D2.1 (the fencing), P1-D11 (the determinism rule),
and the disclosure lines in `SECURITY.md`.

Per the D5 protocol, each runtime dependency needs written justification:

- **pandas** — reading real-world CSVs is the hard part of this phase:
  encodings, quoting, embedded newlines, ragged rows, large files, and a
  mature typed columnar representation. Options considered: the stdlib
  `csv` module (correct, and now used for exactly one job, P1-D3, but it
  leaves the bulk parse to Python-level code); `polars` (strong, but a
  younger audit surface and a Rust binary dependency that weakens the
  pure-Python audit story). **Choice: pandas.**
- **numpy — withdrawn as a direct dependency at review round 1.** The
  draft justified it for the percentile ladder and the moment
  statistics. Round 1 showed those were exactly what it must not do
  here: its reductions made the published mean depend on the order the
  rows arrived in, and overflowed or underflowed at the ends of the
  accepted range. The profiler now computes its statistics itself under
  the rules in P1-D11, using only `math`, and imports numpy nowhere.
  numpy remains in the closure as a dependency OF pandas and is
  recorded that way in `SECURITY.md`; it becomes a direct dependency
  again in Phase 2, where D12's single seeded `numpy.random.Generator`
  genuinely requires it. **This partially supersedes the owner's
  dependency decision above and is flagged for the owner's
  confirmation.** pandas is unaffected: it still does the parsing.

**Declared floor** (an honest tested lower bound, D5): `pandas>=2.1.0`,
tested by the `minimums` CI job, which installs exactly that version on
the oldest supported interpreter, PROVES it is the version installed
before the suite runs, and then runs the whole suite. The floor appears
in `requirements-dev.in` and in `requirements-min.in`, and tests assert
that those files and the compiled `requirements-min.lock` all carry the
same version -- round 2 found that the lock the job installs could be
regenerated at newer versions with every other check still green.

Mechanics (all specified by Phase 0 D5): tested lower bounds in
`pyproject.toml`; the frozen lock regenerated with the 3.10 floor; the
minimum-versions CI job added; the offline static scanner's allowlist
gains an API-granular enumeration of exactly the pandas APIs the
profiler uses — one name, `read_csv` — while numpy receives no
enumeration at all and is simply not importable from `src/` (P1-D10 —
module-level trust stays banned); a hash-pinned
runtime install file (`requirements-install.lock`) is generated and used
by the build job's fresh-venv smoke, so the D5 institutional install path
is exercised from the first dependency-bearing commit rather than promised
for a later release; the sensitive-path job already surfaces lock changes.

### P1-D2.1 The pandas fencing rule (rewritten at review round 1)

`pandas.read_csv` accepts URLs and remote-storage schemes and will open a
network connection when handed one.

**The draft's second control was false and is withdrawn.** It claimed
that handing the reader a `pathlib.Path` rather than user text prevented
a scheme string surviving. It does not: the library turns the object
back into text before it decides whether it has a URL, so
`pathlib.Path("https://host/f.csv")` reaches the network just as the
string would. Nothing rested on that sentence except the claim itself.

**What holds the line, and in which order.** The operative control is a
run-time one: `validate_local_path` runs immediately before the reader
is handed a path and rejects URL and remote-storage forms lexically,
before any filesystem call (D6.1). Every path that reaches the reader
has passed it on that same run. The static scanner is a best-effort
SECOND LAYER over that control, in exactly the terms Phase 0 Amendment
A3 sets and P1-D8.1 R2 restates — a clean scan is not a proof that the
reader cannot be reached another way. What that second layer adds is:

1. the scanner tracks a provenance origin produced ONLY by a call to
   `validate_local_path` and by one wrapping of such a result in
   `pathlib.Path`. A fenced API's first argument must carry that origin,
   established inside the same function as the call, so the reader
   re-validates immediately before it reads;
2. a fenced API may appear only as the direct target of a call. It may
   not be stored in a variable, imported as a bare name and called,
   passed to another function, or placed in a callback slot -- each of
   which was a live bypass at round 1 or round 2 and each of which is
   now a red mutation;
3. a name that shadows the validator does not mint the provenance.

What the second layer does NOT establish is that only one such call
site can ever exist: a second, independently fenced `read_csv` call
would scan clean. What the enumeration does establish is that no OTHER
pandas API can appear at all, and that every `read_csv` call site must
carry that scanner-recognized provenance for itself.

This is a fencing arrangement, not an inability. `SECURITY.md` states it
in exactly those terms next to the existing named residuals: the D6
boundary claim ("synthtwin's own code contains no construct that initiates
network I/O") is preserved by what synthtwin's code does with the API, and
a reader who wants the inability rather than the fencing runs the tool in
their own network-isolated environment, as D6 has always said.

## P1-D3. Input format v1 — and the two-pass read

CSV only, from a local path through `validate_local_path`. The file is
read **twice, by two different readers, and the two results must agree**:

1. **Structural pass** — the standard library's `csv.reader`, streamed,
   holding one row at a time. It establishes: the encoding actually used,
   the true header (unmangled), the number of fields in every data row,
   the count of data rows, and the first three rows whose field count
   differs from the header's.
2. **Checking pass** — `pandas.read_csv`, all columns as text
   (`dtype=str`, `keep_default_na=False`, `na_filter=False`), every
   dialect parameter written out explicitly so both readers provably use
   the same dialect, and **the names read BACK from the file rather than
   handed to the library**. The draft handed them over; review round 1
   showed that this is what made the check blind, because a reader told
   what the columns are called cannot disagree about them, and a file
   rewritten between the passes was accepted with the old header and the
   new values (P1-R1-F4). The library is asked for the names, not told.
3. **Agreement check — every VALUE, not the counts** (rewritten at review
   round 1). The two passes must agree about the column names, the shape,
   AND every single cell; the first difference is a refusal naming the
   row and the column. The draft compared only the row and column counts,
   which round 1 showed was worth nothing: for the bytes
   `c0,c1\n\r,B\nz,w\n` the two readers put different values in
   different columns with both counts equal, so two columns were profiled
   wrongly and nothing looked unusual. Equal counts are NOT accepted as
   agreement.

**Why two passes.** pandas silently pads a short row to the header width:
`a,b,c` followed by the row `4,5` yields `4`, `5`, and an empty third
value that is indistinguishable from a genuinely empty cell. A malformed
file would therefore become a plausible-looking table with invented
missing values — precisely the silent statistical wrongness this project
refuses to ship. Nothing in pandas' interface reports it without handing
the library a callback, which the offline policy forbids. The stdlib
reader reports field counts exactly, so it does the structural job and
pandas does the bulk parse. The cost is one extra sequential pass over the
file, stated in the README next to the size limits.

**Encoding.** UTF-8 first (`utf-8-sig`, so a UTF-8 byte-order mark is
consumed rather than glued to the first column name), then one documented
fallback: Latin-1. Latin-1 decodes any byte sequence, so "undecodable" is
not a state this fallback can reach; instead, after a Latin-1 fallback the
header row is inspected for the two tell-tale signs of a mis-decoded
UTF-16/UTF-32 file — a leading byte-order-mark character, or a NUL
character anywhere in a header name — and such a file is refused with a
message naming UTF-16 and telling the user to save as UTF-8. The same NUL
test also refuses binary files handed over by mistake. Both the encoding
that was chosen and any fallback are reported in the summary; the encoding
is never guessed beyond these two documented attempts.

**The first row is settled in four outcomes, and where nothing settles
it the CSV convention is taken and disclosed (residual R1).** Revision 1
refused a file whose first row looked like data. That was the wrong
verb: refusing a headerless table tells a researcher their perfectly
ordinary file is broken. Revision 2's replacement — stop and ask
wherever the evidence is not conclusive — was wrong the other way, and
is also retired: it questions ordinary files. What the reader does now,
in this order:

1. **`--first-row names` or `--first-row data` was given** — it wins in
   both directions, and nothing below is consulted.
2. **The file shows positively that the first row is a RECORD** — its
   value in some column belongs among the values written below it (a
   number inside their range, a date in their format, or a label the
   column repeats). The run stops and asks, naming the column by
   POSITION, quoting nothing from the row, and offering both options.
   A first row whose EVERY value reads as a number is stopped by its
   own message on the same reasoning.
3. **The file shows positively that the first row is NOT a record** —
   some column holds numbers below a first-row value that is not one.
   The row is read as names and nothing is assumed.
4. **Nothing in the file settles it** — the first row is taken as the
   column names BY CONVENTION, because that is what a CSV file
   normally holds. Nothing is proved, and nothing is silent: the
   decision is recorded as `source.header_by_convention`, its wording
   as `source.header_evidence`, and one plain-language paragraph near
   the top of the summary says the row was taken as names because
   nothing contradicted it and that `--first-row data` re-reads it as a
   record. The cost of the convention is stated in R1 (P1-D8.1).

Where the names came from either way is published as
`source.header_source`, so a later reader of the profile can see
whether they came from the file or were generated. Two readers parse
the table and their disagreement about any NAME or any VALUE is itself
a refusal, because a file that two parsers read differently has no
single correct reading for us to publish.

**Refusals** (message shapes in P1-D7): empty file; header-only file with
no data rows; a first row the file shows could be a record, where
`--first-row` did not say which it is; duplicate column names
(exact duplicates are an input error by the D12 uniqueness rule;
case-variant names are accepted and flagged in the summary); ragged rows;
a field longer than the reader's limit; memory exhaustion. Size is bounded
by available memory with a clear failure message; a streaming/chunked path
is future work, stated honestly in the README.

## P1-D4. The type taxonomy — every column gets exactly one role

Detected roles, in the order they are tested (first match wins; the
profile records which rule fired as `detection_evidence`, in words).
`numeric_unrepresentable` was added at review round 5.

**One role is not in that order at all.** `identifier` is settled
before any rule reads a value and comes from `--identifier` alone
(review round 6, revision 3): a named column takes the role whatever
its values look like, and no ordering of the value rules can reach it.
It is listed below as item 8 only because it is a role, and the item
numbers are left as they are so that references to them elsewhere
still point at the same text. Two earlier attempts to place it IN the
order — third, then second-to-last — are described under that item as
the history they now are; neither survives in the code, and no
sentence anywhere should be read as saying that uniqueness, or
anything else a column contains, selects the role. What uniqueness
still does is decide whether the summary SAYS a column never repeats
and points at the option; that sentence changes no role.

1. **empty** — no present values after sentinel normalization.
2. **numeric_unrepresentable** — the values read as numbers, but enough
   of them fall outside what a 64-bit float can hold that publishing
   statistics would misdescribe the column. It is named rather than
   folded into text, because "these are numbers we cannot carry" and
   "these are words" call for different handling in Phase 2.
3. **constant** — exactly one distinct present value.
4. **binary** — exactly two distinct present values after case folding,
   whether or not they come from the documented equivalence table
   (`0/1`, `true/false`, `t/f`, `y/n`, `yes/no`, `m/f`); the profile
   records both raw labels and their counts, subject to the small-cell
   floor.
5. **datetime** — values parse under an EXPLICIT ordered format table
   (ISO 8601 date, ISO 8601 datetime with optional offset, `YYYYMMDD`,
   `MM/DD/YYYY`, `DD/MM/YYYY`, `YYYY-Qn`) at a parse rate `>= 0.99` of
   present values. Fuzzy parsing is deliberately excluded: a
   deterministic format table is auditable, a guesser is not.
   **Ambiguity rule, stated:** `MM/DD/YYYY` is tried before
   `DD/MM/YYYY`, so a column whose every value is ambiguous (no day
   above 12) is read as month-first; the profile records the matched
   format and the summary says, in words, that the reading was ambiguous
   and which one was taken. The profile records min, max, resolution
   (date vs datetime), the matched format, and the count of unparseable
   stragglers.
6. **numeric (count or continuous)** — values parse as numbers at a rate
   `>= 0.99` of present values, INCLUDING numbers written with
   surrounding whitespace, thousands separators, a leading `+`, or
   parentheses for negatives. Distinction: every present value
   integer-valued and none negative = **count**; otherwise
   **continuous**. The profile records the 11-point percentile ladder
   (min, p01, p05, p10, p25, p50, p75, p90, p95, p99, max — the
   shape-carrying summary the research phase identified), mean, standard
   deviation, skewness, and `n_zero` / `n_negative` as COUNTS against the
   real row count (the counts-not-shares lesson), plus the real row count
   as a first-class field.
7. **categorical** — distinct present values (after trimming and
   Unicode case folding) `<= max(2, min(1000, a tenth of the table's
   ROWS))`. The profile records value counts with the small-cell floor
   applied (P1-D6); case-variant labels are recorded as distinct and
   flagged in the summary. Above the ceiling the column is free text,
   which publishes nothing, and its remark names the distinct count and
   the ceiling that declined it.

   **The share is over rows, not over the values the column holds**
   (settled at review round 6). Measuring it over present values would
   punish a column for being sparse: a 100-row table whose coded field
   is filled in 30 times with 6 labels would get a ceiling of 3 and
   publish nothing, though 6 labels in 100 rows is an ordinary shape and
   the small-cell floor already governs which of them may be shown.

   **The floor of 2 almost never binds, and the earlier claim that it
   "gives tiny tables a categorical path" was wrong.** Where the floor
   is the ceiling, at most two distinct values are allowed — and one
   distinct value is already `constant` and two are already `binary`,
   both tested earlier. So the floor changes no outcome except to keep
   the ceiling a positive number. It is kept for that reason and for no
   other. Small tables are protected by the small-cell floor instead: in
   a 20-row table every label is shared by too few rows to be published
   whichever role the column lands on.
8. **identifier** — **never inferred. Reached only through
   `--identifier` (revision 3, review round 6).** No rule reads the
   values and concludes that a column holds record numbers. The
   declaration is settled before any rule that reads a value and beats
   every one of them, including the ones that publish; the position in
   this list is the numbering's, not the code's. One rule still runs
   ahead of it: a column with no present value at all is `empty`
   (item 1) whether or not it was named, which costs nothing, because
   an empty column has no value to publish either way. A named column
   publishes no value whatever role it ends with.

   Three designs tried and failed, and all three are HISTORY —
   uniqueness plus three guards
   (revision 1), demotion to second-to-last so uniqueness is only a last
   resort (revision 2), and requiring every value to carry a letter
   (round 6). The third was defeated in one line — `1mg` contains
   letters, so a column of measured amounts written with their unit was
   still read as record numbers and lost its distribution. The reason none of them can work is not that
   the rule was not clever enough: `1mg` and `code1` are the same string
   structurally, and what separates a measurement from a label is what
   the column MEANS, which only the person who owns the table knows.

   The guess also had no upside. Guessed right, the identifier role
   publishes nothing useful; guessed wrong, it destroys a distribution.
   So it is withdrawn, and the cost is one option on the command line.

   A column that would once have been inferred now falls to whatever
   positive rule accepts it, and to free text if none does. Free text
   publishes NO values, so the conservative outcome is also the safe
   one, and the column carries a remark saying its values are all
   different, that synthtwin did not assume they are record numbers,
   that nothing from it is published either way, and that
   `--identifier NAME` declares it.

   When declared, identifier VALUES are never published: the profile
   records the role, the counts, the min/max length, whether the
   values are whole numbers, and — by the owner decision of 2026-08-10
   recorded in P1-D5 — an anonymous count multiset saying how many
   distinct values repeat how often, never which ones. The twin will
   generate neutral placeholder identifiers (Phase 2's job), and that
   multiset is what lets it reproduce the repetition pattern rather
   than making one up.

   **Obligation this moves to Phase 2, recorded here so it is not
   discovered later:** an undeclared key column now arrives as free text
   rather than as identifier, so Phase 2 must generate all-different
   values from `n_distinct == n_present` — published on every role —
   rather than from the role name. Without that, twins of key columns
   silently contain duplicates.

   **Amendment A-2026-08-11, recorded on Phase 2 plan review item
   P2-R4-F7.** The obligation above stands and its text is unchanged.
   Phase 2 planning established that it cannot be met in two cases,
   and the owner settled each; both are recorded here so the two plans
   do not state conflicting rules. (a) **A declared identifier whose
   published length range cannot supply as many distinct values as it
   has rows:** the published length wins and the minimum necessary
   number of values repeat, and the generation report names the loss.
   In that corner the identifier column's raw distinct count, its
   folded distinct count, and the anonymous repetition multiset added
   by the owner decision of 2026-08-10 are all reported rather than
   reproduced — so the sentence above, that the multiset lets the twin
   reproduce the repetition pattern rather than making one up, holds
   everywhere except there. (b) **A label column whose values differ
   only by case or edge spacing:** rather than let the twin repeat
   where the real column did not, the owner directed that the profile
   RECORD the spelling variants of an already-published label, under
   the same small-cell floor as any other published label, so the twin
   can keep them distinct. That is a new published fact and is
   described in the Phase 2 plan with its disclosure consequences; the
   obligation therefore HOLDS for label columns wherever the variants
   are visible, and falls back only beneath the floor. (c) **A datetime
   column whose UTC offsets are withheld.** Two spellings can name the
   same instant through different offsets, so a column can be
   raw-distinct while holding fewer distinct instants. Where every
   offset is shared by too few rows to publish, the offset map
   collapses to a withheld pool and the profile no longer says which
   offsets made the spellings distinct; the twin cannot then reproduce
   the raw distinctness without making up unpublished facts, so it is
   reported instead.

   **The general form, which is what governs:** the obligation binds
   only on facts the profile actually publishes. Wherever raw
   distinctness was produced by something the disclosure rules withheld,
   it is reported rather than reproduced. The three cases above are
   instances of that one rule, not a closed list of exceptions.
9. **free text** — everything else. Values are NEVER published: the
   profile records length statistics and token-count statistics only,
   and the summary says so in plain language.

**Sentinel-null normalization runs before every role test**, from a
documented table: empty string, whitespace-only, `NA`, `N/A`, `NULL`,
`None`, `NaN`, `.`, `-`, `--`, `?` (compared after trimming and case
folding), and the numeric sentinels `-999`, `-9999`, `9999` WHEN they are
distribution outliers: the value lies more than 4 interquartile ranges
outside the quartiles of the other numeric values AND accounts for
`>= 0.5%` of present values. Otherwise the candidate is data, and the
summary says which way each candidate went, for every candidate that
appeared. Every normalization is counted and reported per column, by
source, so a reader can see exactly how many missing values came from
which spelling.

Mixed-type columns that fail every threshold fall to free text — which
publishes nothing — and the summary tells the user why, naming the
competing interpretations and their parse rates. "Unsupported column
type" does not exist as an outcome, honoring the charter: every column is
either profiled under a role or safely absorbed as unpublishable text with
an explanation.

**Thresholds are decisions, not diagnostics** (question 1 to the review).
They are fixed here, defined as named constants in one module, recorded
inside every profile under `settings`, and applied as COUNTS rather than
compared shares, so that no rounding of a division decides a column's
role. A column is reported as borderline when one more value of a
different kind would have changed its reading — a rule stated in values,
not in percentages, because a percentage margin calls a column where
everything parses "close to the line" and says nothing useful. Phase 2 may
revisit any of them under the fidelity framework; `profile_version` and
the recorded `settings` are what make that revision explicit rather than
silent.

## P1-D5. The profile contract v1

One JSON document plus a human-readable `.txt` summary generated from it.
Options considered: the prototype's two-CSV shape (workable but
stringly-typed, and its consumer needed a bespoke parser); JSON is chosen
for canonical bytes, explicit typing, and a single artifact crossing the
boundary (question 2 to the review: the answer is one document, not a
stats/metadata split, because a split invites the two halves to disagree
and doubles the number of files a user must carry).

Top-level fields: `profile_version`, `created_with`, `settings` (the
thresholds that produced the roles, plus the two records described
under P1-D6), `source` (the encoding that was used and whether it was
the fallback — the twin has to be written in a form the same tools can
open, and it is fixed by the input bytes, so it does not make two runs
differ, together with where the column names came from), `n_rows`,
`n_columns`, `columns` (ordered list, order = source order), and
`publication_notes` (what was suppressed and why, so the summary and the
machine record can never disagree). `n_rows` is explicit — the prototype
smuggled it through an ID column, a reviewed defect class.

Each column entry carries: `name`, `position`, `role`,
`detection_evidence`, `n_present`, `n_missing`, `missing_by_source`, and
exactly one role-specific block. No RNG is involved anywhere in profiling.

**The number on the wire, and what moves it.** `profile_version`
started at 1. It became 2 at review round 7, when the settings block
stopped carrying declared spellings and began carrying a record of how
many values were declared each way. It becomes 3 with the owner
decision below. The number exists so that a change of shape is
explicit rather than something a consumer of the file has to detect,
which is why it moves with the change and not after it.

**Owner decision, 2026-08-10: a declared-identifier column publishes an
anonymous count multiset, and the contract version advances to 3
(review item P1-R8-F4).** Two six-row tables, each with a declared
identifier column holding the same three neutral codes — one where the
codes appear four times, once and once, one where each appears twice —
produced identical profile bytes and identical summaries. Both recorded
six present, three distinct, and the same length facts, and neither
recorded anything about how the repeats were distributed. A generator
that reads the profile and nothing else must pick one repetition
pattern for both, so a grouped analysis developed against the twin
behaves differently from the same analysis on the real table, with
nothing crashing and nothing said. That is the silent statistical
wrongness this project ranks above ordinary bugs, and it is why the
owner directed the field rather than a recorded approximation.

The shape is a frequency of frequencies: how many distinct values occur
once, how many occur twice, and so on — a map from a repetition count
to the number of distinct values that repeat that often. It never
records WHICH values, never a spelling, never a length paired with a
count, and nothing that can be joined back to a row. That makes it the
same CLASS of fact as the withheld categorical levels published after
review item P1-R1-F9, which is the precedent the decision rests on,
though the two are written differently: the withheld levels are
published as the list of their sizes, this one as a map from a size to
how many groups have it. The publication rule for this role is therefore
unchanged: a declared identifier column publishes counts and lengths
and no value of itself anywhere, and this field is counts about
counts. It is still real-derived material — the repetition pattern is
a fact about the real table, in the same class as the published minima
and the sizes of the withheld levels — so it is covered by the same
institutional handling rule as the rest of the profile. No small-cell
floor is applied to it, and that is deliberate rather than overlooked:
the floor governs whether a LABEL may be shown, and there is no label
here to withhold, only the size of a group nothing names. It is
serialized under the canonical rules below, so its bytes do not depend
on the order anything was iterated in.

**The field.** The implementation landed in `taxonomy.py` in this same
round as `n_distinct_by_occurrences` on the declared-identifier block,
and this document takes that name from the code rather than proposing
one of its own: what the decision fixes is the shape and the rule, and
a plan that invents a second name for the same thing only gives a
reader two answers to reconcile. Its keys are row counts and its
entries are how many different values cover that many rows. Because
JSON object keys are text and the document is serialized with sorted
keys, each key is written in base ten and left-padded with zeros to the
width of the largest key in the same map, so that the sorted-key order
is a numeric order; a consumer reads a key as a number, and the leading
zeros do not change it. The entries sum to `n_distinct`, and the keys
weighted by their entries sum to `n_present`, which is what makes the
field checkable against counts the profile already carried.

**Canonical serialization** (D12): UTF-8 without a byte-order mark; `\n`
line endings; JSON with sorted keys, two-space indent, fixed separators;
datetimes as ISO 8601 with explicit offset and fixed precision; nulls
written as JSON `null`; every published floating-point number written in
its shortest form that reads back as the same number (P1-D11). No timestamp, no source path, and no machine identity
appears anywhere in the profile: identical input bytes produce identical
profile bytes, which is what makes the golden-hash tests meaningful.

**Both files appear, or neither does — as a transaction (added at review
round 5).** A run writes two files, and revision 1 wrote them in
sequence: a failure on the second left the first behind, so a researcher
could be holding a profile with no summary, or a fresh profile beside
last week's summary, with nothing saying so. Writing is now staged.
Each document is written to a working neighbour in the destination
folder — same filesystem, so the final step is a rename rather than a
copy — and only when BOTH working files are complete on disk are they
renamed into place. If either write fails, the working files are
removed and the previous files are untouched. If the first rename
succeeds and the second fails, the first is rolled back from the copy
taken before it was replaced.

**The cleanup and the state report cover EVERY failure the code can
observe, not only write errors (review round 7).** A refused
permission, a full disk, a vanished folder, a working name already
taken, a path refusal raised inside the transaction, memory exhausted
in the middle of a write, a person pressing Ctrl-C, and a defect in
this package are all one case here: the working files are cleared away
and the person is told, by name, what is at each of the two output
names and at every working name this run reached for — checked by
looking rather than assumed from what was attempted. Catching the
exception types someone had thought of is what let the next type
escape with a data-bearing working file behind it, so nothing is
caught by type on that path. The telling takes one of two forms and
the difference is only where the sentence travels: a refusal the
transaction composed itself carries it in its own message
(`nothing_was_written`, `rollback_failed` where even the rollback could
not complete, `working_name_unavailable`), while a failure the
transaction did not compose keeps its own type and message for the
caller — which has its own advice for it — and the sentence is handed
back separately for the caller to print beside it.

**The transaction was rebuilt, and the window it used to claim was
measured (review round 8, item P1-R8-F1).** Through revision 4 this
section said that the renaming step opened a handler "on its own first
line" and that what remained uncovered was one bytecode boundary. Both
sentences described machinery that no longer exists, and neither was
true of the machinery it described. The renaming lived in a
function of its own with a handler of its own, so the call that
reached it sat between two handlers; that handler was not on the first
line; and several of the names it read were bound inside the block it
was meant to guard, so a stop at one of those lines raised
UnboundLocalError out of the cleanup and the person lost their own
failure as well as the account of the files. An opcode-level probe of
that code found 24 boundaries out of policy across two scenarios,
seven of them of that UnboundLocalError kind. "One bytecode boundary"
was not a slight overstatement of a nearly closed window; it was a
figure for a window nobody had measured.

The transaction is now one function with one handler. Everything the
handler reads is bound BEFORE the handler opens, which is possible
only there: at that moment nothing of synthtwin's making is on disk —
no file created, no name reached for — so a stop in those lines leaves
the folder exactly as the run found it and there is nothing to clear
away or to name. Everything after them, the claim of each working
name, both writes and the renaming alike, happens inside that one
handler. A working name is recorded before it is reached for rather
than when the call that creates it hands the name back, because the
file appears on disk a moment earlier than that. And the type of an
exception is no longer read as proof that a cleanup has run: only the
narrower refusal the transaction composes for itself — built in
exactly two places, each after its own cleanup and with the state of
every name already in its message — is passed straight out. Everything
else goes through the full cleanup and then leaves with its own type
and its own message, an unexpected `ProfileError` included, because
the type says which words a refusal uses and never that anything was
tidied up.

What that is worth is a measurement rather than a reading of the
source. 36,832 injections — MemoryError, KeyboardInterrupt,
SystemExit, an unexpected `ProfileError`, and OSError, one at a time,
at every bytecode boundary of every frame the transaction executes,
across four scenarios including one where files the user owns are
already sitting at the working names — report not one violation of the
three questions asked after each stop: did the person's own failure
reach them unchanged, is every working file that survived named to
them, and does each output name hold either what it held before or
what this run wrote? The same probe against the pre-repair code
reports 9,962 violations, which is what says the probe is not vacuous.
The transaction battery in the suite (P1-D8) asks the same three
questions at every STATEMENT boundary; the bytecode-level probe is
independent verification and is not part of the suite. The claim those
numbers support has the scope the code claims and no more: ONE
failure, of any kind, at any statement of the writes, the renames, or
the creation of a working name.

**Two residuals, stated rather than closed.**

1. **A second failure arriving while the first is being described.**
   The cleanup can itself be stopped — a person pressing Ctrl-C again
   while the first stop is being written up. The second failure is
   dropped so the first survives to the caller, which has advice for
   the first and none for the second. What the person loses is the
   report: it is composed and stored in one step, so it goes whole
   rather than in half, but the naming of the working files goes with
   it, and a working file can therefore survive on disk unnamed in
   this case. This is outside the probe above, which injects one
   failure per run.
2. **One statement boundary between the second rename returning and
   the recording of that return.** Both files are in place the moment
   the rename returns, and the record that says so is set on the next
   line. A stop in between is reported as a run caught mid-move. Every
   name is still looked at and named and no file is lost — which is
   why the probe counts it as no violation — but the message opens
   "synthtwin could not put things back as they were" when nothing
   needed putting back, and it calls both outputs unattributable when
   the move had landed. It sends a reader to inspect files that are in
   fact correct; it claims no safety that is not there. There is
   nowhere to put a record that would close it, because a rename
   returning and the recording of that return cannot be one operation.

**A third bound, in the command rather than in the transaction.** Once
the transaction has returned normally, the two lines that report the
run — the caution naming a working file that could not be cleared away
afterwards, and the confirmation naming the two files written — are
ordinary prints outside any handler, so a stop between them can cost
one of them. The caution is printed first for that reason: if only one
of the two reaches the person, it must be the one naming a file that
may hold text taken from their table, not the one confirming what
already went well.

**What is not promised.** The two renames are two steps: a machine
that loses power between them can leave a new profile beside an old
summary, and a stopped MACHINE leaves no sentence anywhere because
nothing runs afterwards to write one. An interrupted PROGRAM is
covered; durability against a power cut is not claimed, and the call
that would force a write to the disk is outside the import allowlist
in any case.

## P1-D6. Privacy defaults — automatic, not advisory

The prototype required the operator to hand-exclude identifier and text
columns and to read the output by eye; the reviews called the manual step
a foot-gun. Phase 1 makes suppression AUTOMATIC by role: identifier and
free-text values never appear in any output; a categorical, binary, or
constant label appears only when its count is at least the small-cell
floor (default 11), and suppressed levels are pooled into a counted
remainder that says how many levels and how many rows it covers. The
summary lists, before the files are written, exactly which columns will
have visible labels — the "read it by eye" step becomes a printed,
explicit disclosure. The floor is configurable only through a documented
advanced flag, off the zero-code path, and lowering it below the default
prints a warning naming the disclosure risk.

**What the profile does publish, stated plainly** (because privacy
defaults that hide their own leaks are worse than none): numeric minima
and maxima are real values from the table, and so are datetime minima and
maxima; the percentile ladder is a distributional summary of real values.
That is inherent to the product — a twin cannot match a distribution
nobody described — and it is why the profile is real-derived material
governed by the user's institutional rules. The summary says this in one
sentence, every run, and README and SECURITY.md say it too.

A column that publishes no value of itself can still publish counts
ABOUT its values, and that is a distinction worth writing down rather
than leaving a reader to infer. The sizes of the withheld levels in a
categorical column and the identifier multiplicity map added by the
owner decision of 2026-08-10 (P1-D5) are both counts about unnamed
groups: they say how often things repeat without saying what repeated,
they carry no spelling and no length, and neither weakens the rule
that identifier and free-text values never appear in any output. What
they do disclose is the sizes themselves — a group of one says that
some single row holds a value no other row holds, without saying which
row or which value — and that is one of the reasons the profile is
described as real-derived material rather than as anonymous.

**Declared values: `--keep-value` and `--missing-value` (exposed on the
command line at revision 3; the settings rule corrected at review round
7).** A person can name a value that means "no value" in their table
and a value that is real data despite looking like one. A declaration
that reads as a number this format can hold is compared with the NUMBER
each cell holds, so naming `-999` also covers a file that writes
`-999.00`; anything else is compared with the spelling, after trimming
and case folding. Naming one value BOTH ways is refused rather than
resolved, on both paths that can reach it.

Two consequences, and they pull in opposite directions, so both are
stated:

- **In its own column, a declared value obeys the publication rules
  like any other value.** Declaring a value withdraws nothing. One
  named with `--keep-value` is data from that point on and is
  described wherever its column publishes values — as one of that
  column's labels above the small-cell floor, or as its smallest
  number. One named with `--missing-value` is counted absent, and its
  spelling reaches `missing_by_source` under the same floor and the
  same role rule as any other missing spelling: withheld in a column
  that publishes no values, withheld below the floor, shown otherwise.
- **In the settings block, no spelling ever appears.** A declaration is
  compared against every cell of every column, so writing the spelling
  there would publish a source value out of all of them at once —
  including the columns that publish nothing and the labels held back
  for being shared by too few rows, which is exactly how a rare value
  supplied as `--missing-value` was serialized while its own column
  published nothing. The block records the COUNT named each way, the
  rule that matched them, and the rule that governs their publication,
  and never the values. No per-column exemption is made: an exemption
  would have to be re-derived for every role and every publication
  rule added later, and that is a rule that will one day be missed.
  The two keys carry a record rather than a list, so a consumer can
  tell a profile written under this rule from one written before it.

## P1-D7. Errors speak human — the failure catalog

Every refusal names what happened and what to do next: path rejections
(already built), a file that is not there or not readable, a folder given
where a file was expected, encoding refusals, empty files, header-only
files, a first row that is not column names, duplicate column names,
ragged rows (the count, plus the first three offending data-row numbers),
over-long fields, the two-pass disagreement, memory exhaustion (with the
file's size in the message), an unwritable output location, and a
small-cell floor that is not a positive whole number. Row positions are
reported as DATA-ROW numbers, counted after the header and skipping blank
lines, not as file line numbers: a quoted value may contain newlines, so a
file line number can point at the middle of a row and mislead. The
catalog is a test fixture: every message has a test asserting its exact
shape, and a test asserts that every catalog entry is reachable from the
code path that raises it.

## P1-D8. Testing strategy

- Neutral seeded fixture GENERATORS (committed as code, provenance-
  compliant, no committed data files) build nasty-case tables at test
  time: every taxonomy rule, every sentinel decision branch, every
  refusal.
- Golden-hash tests pin profile bytes; the same test runs on every CI
  matrix cell, so cross-platform equality is verified empirically and a
  divergence is release-blocking (D12).
- A property battery: for seeded neutral tables, counts in the profile
  agree with counts computed independently from the same input, the
  published percentiles are non-decreasing, `n_present + n_missing`
  equals `n_rows` for every column, and no suppressed value appears
  anywhere in either output file.
- A disclosure battery: for tables built to contain rare labels,
  identifiers, free text, and values named with `--keep-value` or
  `--missing-value`, the search runs over the COMPLETE serialized
  document — the settings block included, not the role block alone —
  and over the complete summary text, and it uses the EXACT spelling
  the person typed rather than the file's own spelling of the same
  number. Searching a role block, or searching for a rounded spelling,
  is what let a rare value cross through settings while its column
  published nothing (review round 7).
- A transaction battery, and it is a battery rather than a reading of
  the source because the property is about instants (review round 8).
  A failure is injected at every statement boundary the write
  transaction executes — in the two frames that hold the guard, and
  again across every function of the module the transaction calls —
  with and without an earlier profile in place, and the same three
  questions are asked after each stop: the person's own failure reached
  them unchanged, every working file that survived is named to them,
  and each output name holds either what it held before or what this
  run wrote. The battery carries a floor on itself, because a tracer
  that quietly stopped tracing would make every assertion in it
  vacuous. P1-D5 records the bytecode-level probe run alongside it and
  the two residuals neither of them closes.
- The offline scanner's new pandas and csv enumerations get red
  mutations: an unlisted pandas attribute, a callable in a `read_csv`
  callback slot, and a method call on a value whose text origin was not
  established must each fail the scan. numpy has no enumeration to
  mutate — an import of it from `src/` is itself a violation — and that
  refusal is held by its own red test.
- The decontamination scanner runs unchanged; profiler fixtures use
  neutral vocabulary by construction.

## P1-D8.1 Residuals: limits accepted, not work outstanding

Three things below are settled decisions with a stated cost, recorded so
that a reader is never told more than the code delivers. They are not a
backlog.

**R1. The first row is taken by convention when nothing settles it, and
this is disclosed.** Owner decision, 2026-08-09. A file where nothing
distinguishes a header row from a first record has no reading that is
provably right — every rule strict enough to catch such a file also
interrogates ordinary files, and every rule quiet enough for ordinary
files also consumes that record. Two repairs proved this by failing in
opposite directions. synthtwin therefore follows the CSV convention and
says so: `header_by_convention` in the profile, a plain-language
paragraph near the top of the summary, and `--first-row data` to take it
back. **The cost, stated plainly:** a headerless file's first record is
described as column names and is missing from every count, unless the
person says otherwise. The alternative — asking on every ordinary file —
was judged the worse product.

**R2. The offline import scanner is one best-effort layer, and
unresolved IMPLICIT PROTOCOL DISPATCH is accepted on purpose.** This is
Phase 0 Amendment A3 applied to Phase 1, not a new concession. Five
repairs at the same class each closed the demonstrated statement and
were defeated one construct over.

**The premise, corrected at review round 7.** This plan said, through
revision 3, that the Phase 0 review had proved a fully closed static
call-target model is not possible in Python. Phase 0 says the opposite,
in the amendment's own words: the accurate premise "is therefore about
this scanner, not about static analysis in general: this scanner does
not establish universal call-target closure", and "a reading-only
analysis could in principle reject every construct it cannot resolve;
ours accepts some of them on purpose, because rejecting them would
require a source dialect so restrictive that the tool would stop being
usable." So the true statement is a choice, not an impossibility: a
reading-only scanner COULD refuse every construct it cannot resolve,
and this project deliberately accepts a bounded caller/process residual
instead, because refusing everything unresolved would refuse ordinary
first-party code. Nothing the scanner enforces changed with that
correction; the claim did.

Trust decisions are **position-blind** — the origin set of a name is
every binding it takes anywhere in the enclosing scopes, and trust
requires all of them to be the allowed API — which over-refuses some
safe programs on purpose, because a refusal costs a contributor one
edit and a wrongly granted trust costs a user their data silently.

**What is accepted, stated as a class rather than as one construct.**
Naming attribute reads as "precisely" the one thing left was too
narrow, and the narrowness invites an audit error: a reviewer who adds
`list(value)` or an f-string of an untraced value gets a clean scan and
concludes that no caller code is dispatched. What the scanner accepts
is unresolved implicit protocol dispatch generally — on a value the
audit cannot trace, every one of these scans clean:

- attribute and property access, and any chain built on one;
- subscription;
- arithmetic and other operators, including the reflected forms;
- comparisons;
- truth and length checks;
- iteration, and conversion by the accepted built-ins;
- formatting, including f-strings;
- class and metaclass construction from such a value.

Each of those runs code belonging to a caller-supplied object without a
call expression appearing anywhere in the source, exactly as a property
read does. Written method CALLS on unresolved receivers do remain
refused, and the restricted library's attributes remain an enumerated
list checked position-blind.

This reaches the caller-supplied-code residual already accepted in
SECURITY.md, and it reaches it WITHOUT A CALL. **The control that
actually holds the reader is not this scanner:** it is the run-time
`validate_local_path` applied immediately before the reader is handed a
path (P1-D2.1). A clean scan is evidence about the source, not a proof
that the reader cannot be reached another way, and no document may
present it as one.

**R3. The project wheel's own digest is not verified in the documented
institutional install.** It cannot be, before a release exists to have a
digest. This closes when Phase 3 publishes one.

## P1-D9. What Phase 1 honestly does not do

No cross-column structure of any kind is detected (Phase 2 decides how
relationships are profiled and represented), so the profile describes each
column alone. The profile v1 may evolve before the Phase 3 end-to-end
freeze; `profile_version` exists so that evolution is explicit. Very wide
tables and multi-gigabyte files are supported only within memory limits.
Nothing is generated, nothing is validated, and no number in the profile
is a scientific result.

## P1-D10. Offline-scanner policy extensions (D6.2 allowlist changes)

D6.2 makes allowlist changes plan-level decisions requiring a capability
audit of the added surface. Phase 1 adds exactly six things, each
enumerated by name in the scanner, with module-level trust still banned:

- **E1 — `pandas.read_csv`, and nothing else from pandas.** Capability
  audit: `read_csv` opens its first argument, which may be a path, a
  file-like object, or a URL; it is network-capable and fenced by
  P1-D2.1. Its callable-accepting parameters are enumerated as callback
  slots (`converters`, `dtype`, `date_format`, `date_parser`,
  `on_bad_lines`, `skiprows`, `usecols`, `dialect`, `engine`,
  `storage_options`), so a caller-supplied or computed callable cannot
  reach the library. Values returned by `read_csv` are api-instances
  under the existing policy case (b).
- **E2 — a fixed set of `math` functions** (this replaced the numpy
  enumeration at review round 1): `fsum`, `frexp`, `isfinite`, `ldexp`,
  `sqrt`. Capability audit: each is a pure numeric function of numbers;
  none takes a callable, none performs I/O, and each is either a
  correctly rounded IEEE-754 operation or an exact manipulation of a
  power of two. Nothing else from `math` is allowed: `prod` and
  `sumprod` are reductions with their own ordering behaviour, and the
  trigonometric and special functions are not correctly rounded. numpy
  is no longer importable from `src/` at all, which is stricter than the
  enumeration it replaces and closes `numpy.errstate(call=...)` -- a
  callable slot the withdrawn audit text wrongly described as taking
  only strings.
- **E3 — `csv.reader`, `csv.Error`, `csv.field_size_limit`.** Capability
  audit: `reader` consumes an iterable of text and yields lists of text;
  its `dialect` parameter is enumerated as a callback slot because a
  dialect class is instantiated by the library; `field_size_limit` reads
  and writes one integer of module state and is used to raise, then
  restore, the per-field cap; `Error` is an exception type. None of the
  three performs I/O or invokes a value it is handed.
- **E4 — text-origin propagation, with its residual restated.** Phase 0
  accepted method calls on a value read as text (a literal, or a
  parameter behind the exact `isinstance` gate) for an enumerated set of
  string data methods. That rule stopped at one step: the RESULT of an
  accepted call was untraced, so `text.strip().casefold()` was rejected
  and any real text processing had to be split into a chain of
  single-method helper functions. E4 tracks the result of an enumerated
  text method on an accepted text receiver as text as well, and adds the
  same treatment for `str(...)`, `repr(...)`, and f-strings built from
  parts this audit already resolved. The enumerated method set is
  extended to the data methods the profiler uses, every one of which is
  audited here as a pure text transform that performs no I/O and invokes
  nothing it is handed except the formatting protocol governed by the
  existing safe-argument rule (`casefold`, `count`, `endswith`, `find`,
  `format`, `isascii`, `isdigit`, `join`, `lower`, `lstrip`,
  `removeprefix`, `removesuffix`, `replace`, `rsplit`, `rstrip`, `split`,
  `startswith`, `strip`, `upper`, `zfill`).
  **Residual, restated exactly:** the `isinstance` gate does not settle
  that a receiver is a built-in `str`; a `str` subclass passes it and may
  override these methods, so a value this audit calls text may be the
  subclass's own return value. That is the same caller-supplied-code
  residual D6 Amendment A3 already names — the caller's object runs in
  the caller's process under the caller's authority — and E4 does not
  widen the class of thing that can happen, because the only operations
  the policy permits on a text value are another enumerated data method
  or use as data. What E4 changes is how far that accepted reading
  propagates, and the propagation is bounded: text originates only at a
  literal, a gated parameter, or an enumerated text call, never at an
  untraced value. Required red mutations: a method outside the
  enumeration called on a text value; a method call on a value from an
  untraced source; an unresolved value passed to `format`; a method
  called on the result of `split`, which returns a list and therefore
  does not carry the text origin forward.
- **E5 — no method calls at all on pandas objects (and none on numpy
  objects, which `src/` cannot hold).** Policy
  case (b) accepts any method name on a value an allowlisted API
  produced, on the reasoning that the producing API was itself checked.
  That reasoning does not survive contact with these two libraries: a
  data frame carries `to_sql`, `to_gbq` and a whole family of `to_*`
  writers that accept URLs, and an array carries `tofile` and `dump`.
  Admitting pandas under E1 while leaving case (b) untouched would have
  reopened, through the returned object, everything E1's single-name
  enumeration closes. The scanner therefore holds a table of libraries
  whose instances may not be called through, with the exact method
  names nonetheless permitted on them — currently none. Since the numpy
  withdrawal that table holds pandas alone, because no numpy object can
  exist in `src/` for the rule to govern: the import that would produce
  one is itself refused. synthtwin's source reads pandas objects with
  an attribute, a subscript or an operator and passes them back to the
  enumerated module-level functions. Required red mutations:
  `frame.to_sql(...)` must fail the scan, `array.tofile(...)` must fail
  it too (at the numpy import, which is where it is now stopped), and a
  clean read (`list(frame[name])`, `len(frame.columns)`) must stay
  green.
- **E6 — `argparse.RawDescriptionHelpFormatter`.** Capability audit: a
  help-text formatter that argparse instantiates and calls to lay out
  the help screen; it formats strings, performs no I/O, and invokes
  nothing it is handed. It is named directly in `ArgumentParser`'s
  `formatter_class` slot, which is exactly the shape the callback-slot
  rule permits — a literal or a directly named allowlisted API, never a
  computed value. It exists so that the worked examples in the help
  screen keep their line breaks, which is a zero-code-UX requirement,
  not a convenience.

## P1-D11. Determinism of the profile bytes (revised at review round 1)

D12 governs. Phase 1 adds no RNG and reads no clock, so the only
determinism risk is floating-point arithmetic.

**Revision 0's rule was wrong and is withdrawn.** It rounded every
published number to twelve significant digits, on the reasoning that
this was far beyond any statistically meaningful precision and would
absorb the last-bit differences a reduction can produce between
processors. Review round 1 showed it destroys real data: ten values
around 1e15 all collapse onto one number, so the profile states that the
range is zero and, in the next field, that the spread is 3.03. A control
that makes the output self-contradictory is worse than the divergence it
was hiding.

**The rule now is that the computation itself is machine-independent**,
so nothing has to be hidden. **Nothing is accumulated in floating point
at all** (revision 2, review round 5), which is what makes that exact
rather than nearly true. Four properties, each load-bearing, and each
stated so a reviewer can check the code against it:

1. every finite binary64 value IS a whole number times a power of two,
   and the module splits each value into exactly that. A column becomes
   one shared power of two and one whole significand per value;
2. the significands, their squares and their cubes are added as
   ARBITRARY-PRECISION WHOLE NUMBERS. Whole-number addition neither
   rounds nor depends on the order it is done in, so the three power
   sums are exact and the row order cannot reach them;
3. the mean, the sample variance and the moment skewness are then exact
   fractions of those whole numbers, and each is rounded to binary64
   exactly ONCE, at the end. The last digit is settled by comparing
   whole numbers — a quotient against the midpoint between its two
   candidates, a square root against the SQUARE of that midpoint — so
   the rounding is the correct one on every platform, ties to even;
4. a ladder rung is the same shape of computation: its position is
   located in whole numbers (`(n-1) * num` split by `den`, because 0.99
   has no exact binary spelling and the nearest one can move a rung
   onto the wrong pair of neighbours), and the interpolation between
   its two neighbours is one exact fraction rounded once.

`**` is used nowhere in the numeric path: it calls the platform's
`pow`, which no standard requires to be correctly rounded. Every square
is `x * x` on whole numbers and every square root is Newton's method on
whole numbers, so both are exact by construction rather than by
trusting a library to round well.

**The floating-point reduction described here in revision 1 is retired
(review round 5) and is recorded only as history.** It sorted the
values, summed them with `math.fsum`, divided by a power of two taken
from the largest magnitude before every sum to keep `math.fsum`'s own
overflow path unreachable, reapplied the scale once after the square
root with `math.ldexp`, and recentred the deviations once before the
second and third moments. None of that is the algorithm now, and
neither `math.fsum` nor `math.sqrt` is called anywhere in the
statistics module — `math` is still on the scanner's enumerated list
with those names on it (E2), which is a statement about the allowlist
and not about what the code calls. Two `math` functions are still
called, for a different job than the retired one: `frexp` splits a
value into its whole significand and its power of two on the way in,
and `ldexp` builds the single rounded result on the way out.

**The accuracy contract (revision 2; the revision-1 tolerances below it
are retired).** Frozen here and tested against the reference vectors:
the mean, the sample standard deviation and the moment skewness are each
**correctly rounded, or the float immediately adjacent to it** -- stated
as a count of representable numbers between the published value and the
exact one, not as a relative error, because a relative error degenerates
at zero. Every ladder rung is likewise correctly rounded or adjacent.

Revision 1 instead allowed the mean 1 unit in the last place, the
standard deviation 2, and the skewness an absolute `8 * eps * (1 +
|skew|)`. Those were the tolerances the retired conditioning limit
required, and review round 6 recorded that leaving them in place would
have accepted answers many representable numbers from the truth while
the plan claimed exactness. They bind nothing now.

Each ladder rung is **additionally** held within `4 * eps *
max(|x_k|, |x_k+1|)` of its bracketing order statistics. That bound
survives not as a conditioning allowance but because an interpolated
quantile is defined in terms of its two neighbours, so the bracket is
part of what the rung means. Both readings are checked, and every rung
in the committed vectors is in fact exactly the reference value.

**The conditioning limit recorded in revision 1 is retired (review round
5).** That paragraph said that for a sample like {1e16, 1, -1e16} the
third central moment cancels past what a 64-bit float can carry, so only
an absolute accuracy contract was achievable. That was true of the
*two-pass floating-point reduction* revision 1 used, and the revision
mistook a property of that algorithm for a property of binary64. It is
not one: cancellation of 1e32 costs nothing to the whole numbers the
four properties above accumulate, because nothing was approximated on
the way in. The sample now yields -1.224744871391589e-16, the correctly
rounded exact skewness. The contract is therefore tightened from
absolute to correctly-rounded-or-adjacent for every statistic the
reference vectors cover, and the ladder bracket above stays only
because interpolated quantiles are defined in terms of two neighbours,
not because of conditioning.

**Values outside the representable range are refused, not approximated.**
A number too large becomes an infinity and one too small collapses to
zero; zero is the more dangerous of the two because it is a plausible
reading. Both are refused by the parser and counted in a structured
`n_out_of_range` field, so such a column is still described as numbers
rather than being pushed into another role by a spent straggler budget.
When a spread is larger than the format can hold, `std` is null AND
`std_unrepresentable` is true, because "undefined" and "out of range"
are different facts a generator must be able to tell apart.

**The oracle.** The charter requires that numeric machinery not be its
own oracle. `tools/reference/make_numeric_reference_vectors.py` computes
the reference values from the exact rational values of the inputs, using
`fractions` and importing none of the code it checks — not synthtwin,
not pandas, not numpy. **It no longer imports `decimal` at all**
(review item P1-R2-F5): a high-precision decimal seed was how a square
root came out negative, so every published value is built from whole
numbers and the one rounding step is all-integer too. Every float64 it reports
is *proved* correctly rounded by exact integer comparison against the
midpoints to its neighbours. Its output is
committed as a fixture, bound in the provenance manifest by generator,
seed and digest, so CI rebuilds it and byte-compares it on every run.
The golden profile hash remains, demoted to what it always was: a change
detector, not an oracle.

## Acceptance criteria

1. `synthtwin profile` exists behind the path validator; the four Phase 0
   guards (offline static scan, decontamination + signed attestation,
   provenance, lock validation) all pass with the new code and
   dependencies, and the socket guard stays green with pandas imported,
   and with the numpy that pandas loads for itself.
2. Every taxonomy rule and every sentinel decision branch has a red/green
   fixture test; the failure catalog is fully tested, message by message.
3. Golden profile hashes verified on every CI platform; the dependency
   introduction satisfies every D5 item — declared floors, floors tested
   by the `minimums` job, frozen lock regenerated, hash-pinned runtime
   install file present and exercised by the fresh-venv smoke, scanner
   enumeration in place with its red mutations.
4. A profile of a neutral demonstration table is generated end-to-end in
   CI and its `publication_notes` match the suppression rules.
5. The disclosure battery passes: searching the COMPLETE serialized
   document, settings block included, and the complete summary text,
   using the exact spelling that was declared, finds no identifier
   value, no free-text value, no below-floor label, and no spelling
   named with `--keep-value` or `--missing-value` where its column's
   own publication rules withhold it.
6. Docs updated and consistent: README states what the profiler does, the
   two-pass read, the memory bound, and what the profile publishes;
   SECURITY.md carries the pandas fencing statement (P1-D2.1) and the
   updated supply-chain inventory; CHANGELOG records the phase.

## The three questions the draft put to review — answered

1. **Are the taxonomy thresholds the right decisions to fix now?** Yes,
   fixed now (P1-D4), with three controls that make the decision
   reviewable rather than buried: the constants live in one module, every
   profile records them under `settings`, and any column that landed
   within 10% of a threshold is named in the summary. A profile-time
   diagnostic that deferred the decision would leave Phase 2 unable to
   generate anything, because a role is what the generator dispatches on.
2. **Single JSON profile, or a stats/metadata split?** Single document
   (P1-D5). A split doubles the artifacts a user must carry across the
   boundary and creates a state where the two halves disagree; the
   `publication_notes` block already separates "what was suppressed" from
   the statistics inside one file.
3. **Is the API-enumeration approach for the scanner proportionate under
   A3?** Yes, and P1-D10 states the capability audit for each addition.
   The alternative — trusting pandas at module level — is exactly what
   D6.2 bans, and the enumeration is what keeps a future
   `pandas.read_sql` from entering without a plan change. numpy needs
   no enumeration for this: it is not importable from `src/` at all, so
   `numpy.load` is refused with the import that would reach it.

## Changes from the draft (revision 0)

- The two-pass read (P1-D3) is new: the draft assumed pandas alone could
  report ragged rows. It cannot without a callback, and it silently pads
  short rows, so the stdlib `csv` structural pass and the agreement check
  were added, together with the E3 scanner entries they require.
- Row positions in errors are DATA-ROW numbers, not file line numbers
  (P1-D7), because quoted newlines make file line numbers wrong.
- The determinism rule (P1-D11) is new; the draft named no control for
  cross-architecture float divergence. Its first form was withdrawn at
  review round 1 and replaced, as that section records.
- `settings` is added to the profile's top-level fields (P1-D5) so the
  thresholds that produced the roles travel with the profile.
- The taxonomy gains the explicit `MM/DD/YYYY` ambiguity rule, the
  categorical ceiling's floor of 2, the extended sentinel table, and the
  near-threshold reporting rule (P1-D4).
- P1-D6 gains the paragraph stating what the profile DOES publish
  (minima, maxima, the ladder), because a privacy section that lists only
  suppressions overstates itself.
- The scanner extension E4 (text-origin propagation) is new; the draft
  did not notice that the Phase 0 policy stopped text tracking after one
  method call.
- The dependency justification records the owner decision and the
  zero-dependency alternative that was considered and rejected, and adds
  the fencing rule P1-D2.1.
- The hash-pinned runtime install file is delivered in this phase rather
  than deferred to the first release, so the D5 institutional install
  path is exercised as soon as a dependency exists.

## Decisions taken during implementation (all recorded here, none silent)

- **The identifier rule gained three guards, and was then withdrawn
  altogether** (P1-D4). Written as the draft had it — uniqueness alone —
  it swallowed every all-different numeric column, every date column,
  and every column of sentences, each of which would have cost the twin
  a whole distribution. The guards did not save it: review round 6
  removed value-based inference entirely, so THE GUARDS ARE HISTORY
  TOO. `--identifier` is now the only route to the role, and the remark
  that names it is what a column of all-different values gets instead
  of a guess.
- **E5 (no method calls on pandas objects) is new** (P1-D10).
  It closes a hole the dependency introduction would otherwise have
  opened in the Phase 0 policy, and it was found by writing the code
  rather than by reading the plan.
- **E6 (the help formatter) is new** (P1-D10), for the worked examples
  in the help screen.
- **The command line is flat** — `synthtwin profile <table>` is a
  positional word, not an argparse subcommand. One help screen serves a
  reader who has never used a command line, and the parser object stays
  inside the function that makes it, which is what the offline policy
  accepts.
- **Borderline reporting counts values instead of comparing shares**
  (P1-D4), because a percentage margin marks a column where everything
  parses as "close to the line".
- **Zero bytes are refused wherever they appear in the first rows**, not
  only in the header, and Python 3.10's own refusal of a zero byte in
  the CSV reader is mapped to the same message, so the advice a reader
  gets does not depend on their interpreter version.
- **`source` was added to the profile's top-level fields** (P1-D5).
- **A declared-identifier column publishes an anonymous count multiset,
  and `profile_version` advances to 3** — owner decision, 2026-08-10,
  recorded in full in P1-D5 and in P1-D6. Two tables that differ only
  in how a declared identifier's values repeat used to serialize to the
  same bytes, which left a generator to invent the repetition pattern.

## Review record

Revision 0 (draft) was written before Phase 0 closed and was never
reviewed. Revision 1 is the document the implementation was first
written against, submitted for the combined plan-and-code review
described in the sequencing note at the top; revisions 2, 3, 4 and 5
record what the reviews of rounds 5, 6, 7 and 8 changed. Round 8
returned a verdict of reject, and its repairs are the work this
revision records. No part of Phase 1 is claimed as ratified.

# Phase 1 — The profiler: reading and automatic type analysis

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

## P1-D2. Dependency introduction: pandas and numpy

**Owner decision, 2026-08-07.** The implementer proposed a zero-runtime-
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
gains an API-granular enumeration of exactly the pandas/numpy APIs the
profiler uses (P1-D10 — module-level trust stays banned); a hash-pinned
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

What holds the line now is enforced by the scanner rather than asserted
in prose:

1. every path reaching the reader has passed `validate_local_path`,
   which rejects URL schemes lexically, before any filesystem call
   (D6.1);
2. the scanner tracks a provenance origin produced ONLY by a call to
   `validate_local_path` and by one wrapping of such a result in
   `pathlib.Path`. A fenced API's first argument must carry that origin,
   established inside the same function as the call, so the reader
   re-validates immediately before it reads;
3. a fenced API may appear only as the direct target of a call. It may
   not be stored in a variable, imported as a bare name and called,
   passed to another function, or placed in a callback slot -- each of
   which was a live bypass at round 1 or round 2 and each of which is
   now a red mutation;
4. a name that shadows the validator does not mint the provenance.

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
2. **Data pass** — `pandas.read_csv`, all columns as text
   (`dtype=str`, `keep_default_na=False`, `na_filter=False`), with the
   header names supplied from the structural pass and every dialect
   parameter written out explicitly so both readers provably use the same
   dialect.
3. **Agreement check** — the row count and the column count from the two
   passes must match, or the read is refused with a plain-language
   message. This check can fail (a file edited between the passes fails
   it), and it is the control that makes the pass division meaningful
   rather than decorative.

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

**The first row is decided explicitly, not assumed (revised at review
round 5).** Revision 1 refused a file whose first row looked like data.
That was the wrong verb: refusing a headerless table tells a researcher
their perfectly ordinary file is broken. The reader now reaches a
verdict — names, or data — states which it took and on what evidence,
and where the evidence is not conclusive it stops and asks, offering
`--first-row names` and `--first-row data`. The verdict is published as
`source.header_source` so a later reader of the profile can see whether
the column names came from the file or were supplied. Two readers parse
the table and their disagreement about any NAME or any VALUE is itself a
refusal, because a file that two parsers read differently has no single
correct reading for us to publish.

**Refusals** (message shapes in P1-D7): empty file; header-only file with
no data rows; a first row whose reading cannot be settled and was not
supplied with `--first-row`; duplicate column names
(exact duplicates are an input error by the D12 uniqueness rule;
case-variant names are accepted and flagged in the summary); ragged rows;
a field longer than the reader's limit; memory exhaustion. Size is bounded
by available memory with a clear failure message; a streaming/chunked path
is future work, stated honestly in the README.

## P1-D4. The type taxonomy — every column gets exactly one role

Detected roles, in the order they are tested (first match wins; the
profile records which rule fired as `detection_evidence`, in words).
**Revised at review round 5**: `numeric_unrepresentable` is new, and
`identifier` moved from third place to second-to-last. Round 1 showed
why the old position was wrong — a rule that fires on uniqueness alone,
however many guards hang off it, is tested *before* the rules that would
have described the column properly, so every guard added was a patch on
an ordering mistake. Uniqueness is now what is left when no positive
description fits, which is what "identifier" actually means.

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
7. **categorical** — distinct count `<= min(1000, 10% of rows)`, with a
   floor of 2 so that tiny tables still have a categorical path. The
   profile records value counts with the small-cell floor applied
   (P1-D6); case-variant labels are recorded as distinct and flagged in
   the summary.
8. **identifier** — reached only when every rule above declined the
   column: it does not read as numbers or dates, it is not constant,
   binary or categorical, and `distinct >= ceil(0.95 * present)` with
   every value a single word. Testing it here rather than third means
   the all-different measurement column, the column of event dates and
   the column of sentences have each already been described properly
   before uniqueness is ever consulted. The irreducible case (a record
   number written as digits) is still settled by the person who knows
   the table, through `--identifier`, and a numeric column whose values
   are all different still carries that option in its remarks.
   Identifier VALUES are never published: the profile records the role,
   the counts, the min/max length, and whether the values are whole
   numbers; the twin will generate neutral placeholder identifiers
   (Phase 2's job).
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

Top-level fields: `profile_version`, `created_with`, `settings`,
`source` (the encoding that was used and whether it was the fallback —
the twin has to be written in a form the same tools can open, and it is
fixed by the input bytes, so it does not make two runs differ), `n_rows`,
`n_columns`, `columns` (ordered list, order = source order), and
`publication_notes` (what was suppressed and why, so the summary and the
machine record can never disagree). `n_rows` is explicit — the prototype
smuggled it through an ID column, a reviewed defect class.

Each column entry carries: `name`, `position`, `role`,
`detection_evidence`, `n_present`, `n_missing`, `missing_by_source`, and
exactly one role-specific block. No RNG is involved anywhere in profiling.

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
taken before it was replaced. Two message shapes cover what the user
must then be told: `nothing_was_written`, and `rollback_failed` for the
case where even the rollback could not complete, which names every file
left on disk rather than reporting a clean failure it cannot vouch for.

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
  identifiers, and free text, the emitted bytes are searched for those
  values and must not contain them.
- The offline scanner's new pandas/numpy/csv enumerations get red
  mutations: an unlisted pandas attribute, an unlisted numpy attribute, a
  callable in a `read_csv` callback slot, and a method call on a value
  whose text origin was not established must each fail the scan.
- The decontamination scanner runs unchanged; profiler fixtures use
  neutral vocabulary by construction.

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
- **E5 — no method calls at all on pandas or numpy objects.** Policy
  case (b) accepts any method name on a value an allowlisted API
  produced, on the reasoning that the producing API was itself checked.
  That reasoning does not survive contact with these two libraries: a
  data frame carries `to_sql`, `to_gbq` and a whole family of `to_*`
  writers that accept URLs, and an array carries `tofile` and `dump`.
  Admitting pandas under E1 while leaving case (b) untouched would have
  reopened, through the returned object, everything E1's single-name
  enumeration closes. The scanner therefore holds a table of libraries
  whose instances may not be called through, with the exact method
  names nonetheless permitted on them — currently none for either.
  synthtwin's source reads those objects with an attribute, a subscript
  or an operator and passes them back to the enumerated module-level
  functions. Required red mutations: `frame.to_sql(...)` and
  `array.tofile(...)` must each fail the scan, and a clean read
  (`list(frame[name])`, `len(frame.columns)`) must stay green.
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
so nothing has to be hidden. Four properties, each load-bearing, and
each stated so a reviewer can check the code against it:

1. every reduction starts from the sorted values, and every sum is
   `math.fsum`, which computes the exact sum and rounds once. The result
   therefore cannot depend on the order the rows arrived in;
2. before any sum, the values are divided by a power of two taken from
   the largest magnitude present. That division is exact, so it costs
   nothing, and it puts every operand in [-1, 1] -- which is what makes
   `math.fsum`'s own intermediate-overflow path unreachable. On raw
   values `math.fsum` can raise, and *whether* it raises depends on the
   order, so sorting alone would have made that worse rather than
   better;
3. the scale is reapplied once, after the square root, with
   `math.ldexp`. Squaring the scale would reintroduce exactly the
   overflow and underflow that the scaling exists to prevent;
4. the deviations are recentred once before the second and third
   moments. The mean carries up to half a unit in the last place of
   error; every deviation inherits it as a common shift, and the
   moments are quadratic and cubic in that shift.

`**` is used nowhere in the numeric path. It calls the platform's
`pow`, which no standard requires to be correctly rounded and which
disagrees with `x*x` and `math.sqrt` on real inputs; those two are
IEEE-754 operations and are exact to the last bit on every conforming
platform. The percentile rungs are located by whole-number arithmetic
(`(n-1) * num` split by `den`), because 0.99 has no exact binary
spelling and the nearest one can move a rung onto the wrong pair of
neighbours.

**The accuracy contract**, frozen here and tested against the reference
vectors: the mean is within 1 unit in the last place of the correctly
rounded exact mean; the sample standard deviation within 2; each ladder
rung within `4 * eps * max(|x_k|, |x_k+1|)` -- bounded by its bracketing
order statistics rather than by its own value, because a rung falling
near zero between two large neighbours is intrinsically ill-conditioned;
and the moment skewness within `8 * eps * (1 + |skew|)`.

**The conditioning limit recorded in revision 1 is retired (review round
5).** That paragraph said that for a sample like {1e16, 1, -1e16} the
third central moment cancels past what a 64-bit float can carry, so only
an absolute accuracy contract was achievable. That was true of the
*two-pass floating-point reduction* revision 1 used, and the revision
mistook a property of that algorithm for a property of binary64. It is
not one. Every value a `float` holds is an integer times a power of two.
The statistics module now converts the column to exactly that form -- a
shared power of two and one integer significand per value -- accumulates
the power sums as **arbitrary-precision integers**, which cancel without
error because Python integers do not round, and rounds **once**, at the
end, to the nearest float. Cancellation of 1e32 costs nothing when
nothing was approximated on the way in. The sample above now yields
-1.224744871391589e-16, the correctly rounded exact skewness. The
contract is therefore tightened from absolute to correctly-rounded-or-
adjacent for every statistic the reference vectors cover, and the ladder
bracket above stays only because interpolated quantiles are defined in
terms of two neighbours, not because of conditioning.

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
`fractions` and `decimal` and importing none of the code it checks;
every float64 it reports is *proved* correctly rounded by exact integer
comparison against the midpoints to its neighbours. Its output is
committed as a fixture, bound in the provenance manifest by generator,
seed and digest, so CI rebuilds it and byte-compares it on every run.
The golden profile hash remains, demoted to what it always was: a change
detector, not an oracle.

## Acceptance criteria

1. `synthtwin profile` exists behind the path validator; the four Phase 0
   guards (offline static scan, decontamination + signed attestation,
   provenance, lock validation) all pass with the new code and
   dependencies, and the socket guard stays green with pandas and numpy
   imported.
2. Every taxonomy rule and every sentinel decision branch has a red/green
   fixture test; the failure catalog is fully tested, message by message.
3. Golden profile hashes verified on every CI platform; the dependency
   introduction satisfies every D5 item — declared floors, floors tested
   by the `minimums` job, frozen lock regenerated, hash-pinned runtime
   install file present and exercised by the fresh-venv smoke, scanner
   enumeration in place with its red mutations.
4. A profile of a neutral demonstration table is generated end-to-end in
   CI and its `publication_notes` match the suppression rules.
5. The disclosure battery passes: no identifier value, no free-text
   value, and no below-floor label appears in either output file.
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
   The alternative — trusting pandas or numpy at module level — is
   exactly what D6.2 bans, and the enumeration is what keeps a future
   `pandas.read_sql` or `numpy.load` from entering without a plan change.

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

- **The identifier rule gained three guards** (P1-D4). Written as the
  draft had it — uniqueness alone — it swallowed every all-different
  numeric column, every date column, and every column of sentences. Each
  of those would have cost the twin a whole distribution. The
  `--identifier` option and the remark that names it are the answer to
  the one case no rule can settle.
- **E5 (no method calls on pandas or numpy objects) is new** (P1-D10).
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

## Review record

Revision 0 (draft) was written before Phase 0 closed and was never
reviewed. This revision 1 is the document the implementation was written
against, submitted for the combined plan-and-code review described in the
sequencing note at the top. No part of Phase 1 is claimed as ratified.

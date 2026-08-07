# Phase 1 — The profiler: reading and automatic type analysis

**Status:** DRAFT — prepared while the Phase 0 closure review completes.
This plan is gated twice: Phase 0 must close, and this document must be
adversarially reviewed and ratified before any Phase 1 code exists.

**Scope:** one new command path — `synthtwin profile <table>` — that reads
a local CSV table and produces the profile: the machine-readable schema
description and a plain-language console summary of what was detected and
what will be published. **Non-goals:** no generation, no relationships
(Phase 2 decides how cross-column structure is profiled), no validator, no
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
(P1-D6) with an explicit `profile_version` field so later phases can
evolve it without ambiguity.

## P1-D2. Dependency introduction: pandas and numpy

Per the D5 protocol, each runtime dependency needs written justification:

- **pandas** — reading real-world CSVs is the hard part of this phase:
  encodings, quoting, embedded newlines, ragged rows, large files, and
  a mature typed columnar representation. Options considered: the stdlib
  `csv` module (correct but leaves every hard case to us: no typed
  columns, no memory-efficient large-file path; rebuilding pandas'
  twenty years of CSV hardening is worse security than importing it);
  `polars` (strong, but younger audit surface and a Rust binary
  dependency that weakens the pure-Python audit story). **Choice:
  pandas**, consistent with the audit claim already in `SECURITY.md`.
- **numpy** — percentile/quantile computation, vectorized statistics,
  and the numeric representation pandas is built on. It arrives with
  pandas regardless; declaring it directly makes the audit surface
  explicit and lets the profiler use its statistics functions under our
  own determinism rules.

Mechanics (all already specified by Phase 0): tested lower bounds in
`pyproject.toml`; the frozen lock regenerated with the 3.10 floor; the
minimum-versions CI job becomes meaningful and is added; the offline
static scanner's allowlist gains an API-GRANULAR enumeration of exactly
the pandas/numpy APIs the profiler uses (a bounded list stated in the
scanner, per the A3 contract — module-level trust stays banned); the
sensitive-path job already surfaces the lock change.

## P1-D3. Input format v1

CSV only, from a local path through `validate_local_path`. Encoding:
UTF-8 first, then the documented single fallback (Latin-1), reusing the
Phase 0 decoder's BOM handling; undecodable input is a plain-language
refusal, never a guess. A file that is empty, headerless, or has
duplicate column names is refused with a message saying exactly what to
fix (duplicate names are an input error by the D12 uniqueness rule).
Size: bounded by available memory with a clear failure message; a
streaming/chunked path is future work, stated honestly in the README.

## P1-D4. The type taxonomy — every column gets exactly one role

Detected roles, in the order they are tested (first match wins, and the
profile records WHICH rule fired as `detection_evidence`):

1. **empty** — all values missing after sentinel normalization.
2. **constant** — exactly one distinct present value.
3. **identifier** — values are unique or near-unique (rule: distinct
   count / present count >= 0.95) AND the column is not numeric-
   continuous by parse (integer-like or string forms). Identifier
   VALUES are never published: the profile records only the role, the
   count, and the min/max length; the twin will generate neutral
   placeholder identifiers (Phase 2's job).
4. **binary** — exactly two distinct present values after case folding,
   from a documented equivalence table (0/1, true/false, t/f, y/n,
   yes/no, m/f) or any other two-value set; the profile records both
   raw labels and their counts.
5. **datetime** — values parse under an EXPLICIT ordered format table
   (ISO 8601 date and datetime, YYYYMMDD, MM/DD/YYYY, DD/MM/YYYY with
   the ambiguity rule stated, YYYY-Qn quarters) at a parse rate >= 0.99
   of present values; fuzzy parsing is deliberately excluded — a
   deterministic format table is auditable, a guesser is not. The
   profile records min, max, resolution (date vs datetime), and the
   matched format; unparseable stragglers are counted and reported.
6. **numeric (count or continuous)** — values parse as numbers at a
   rate >= 0.99 of present values, INCLUDING numbers stored as strings
   with thousands separators or surrounding whitespace (the parse rule
   is written out). Distinction: integer-valued and non-negative =
   **count**; otherwise **continuous**. The profile records the
   11-point percentile ladder (min, p01, p05, p10, p25, p50, p75, p90,
   p95, p99, max — the quantile function the research phase identified
   as the shape-carrying summary), mean, std, skew, and `n_zero` /
   `n_negative` as COUNTS against the real row count (the prototype's
   documented counts-not-shares lesson), plus the real row count itself
   as a first-class field.
7. **categorical** — distinct count <= the categorical ceiling (rule:
   min(1000, 10% of rows)); the profile records value counts with the
   small-cell floor applied (P1-D7) and case-variant labels reported
   as distinct but flagged in the summary.
8. **free-text** — everything else. Values are NEVER published: the
   profile records length statistics and token-count statistics only;
   the summary says so in plain language.

Sentinel-null normalization runs before all role tests, from a documented
table: empty string, whitespace-only, `NA`, `N/A`, `NULL`, `null`,
`None`, `.`, `-`, and the numeric sentinels `-999`, `-9999`, `9999`
WHEN they are distribution outliers (rule: the sentinel is more than 4
IQRs outside the quartiles AND accounts for >= 0.5% of values;
otherwise it is treated as data and the summary says which way each
candidate went). Every normalization is counted and reported per column.

Mixed-type columns that fail every threshold above fall to free-text —
which publishes nothing — and the summary tells the user why, naming the
competing interpretations. "Unsupported column type" does not exist as
an outcome, honoring the charter: every column is either profiled under
a role or safely absorbed as unpublishable text with an explanation.

## P1-D5. The profile contract v1

One JSON document (canonical serialization per D12: UTF-8, LF, sorted
keys, documented float format, ISO 8601 datetimes) plus a human-readable
`.txt` summary generated from it. Options considered: the prototype's
two-CSV shape (proved workable but stringly-typed, and its consumer
needed a bespoke parser); JSON chosen for canonical bytes, explicit
typing, and a single artifact crossing the boundary. Top-level fields:
`profile_version`, `created_with` (synthtwin version), `n_rows`
(explicit — the prototype smuggled it through an ID column, a reviewed
defect class), `n_columns`, `columns` (ordered list, order = source
order), and `publication_notes` (what was suppressed and why, so the
summary and the machine record can never disagree). No RNG is involved
anywhere in profiling; identical input bytes produce identical profile
bytes on a platform (golden-hash tested; cross-platform equality
verified empirically in CI per D12's tested-matrix rule).

## P1-D6. Privacy defaults — automatic, not advisory

The prototype required the operator to hand-exclude identifier and text
columns and to read the output by eye; the reviews called the manual
step a foot-gun. Phase 1 makes suppression AUTOMATIC by role:
identifier and free-text values never appear in any output; categorical
value labels appear only with count >= the small-cell floor (default
11), with suppressed levels pooled into a counted remainder. The
console summary lists, before the file is written, exactly which
columns will have visible labels — the "read it by eye" step becomes a
printed, explicit disclosure. The floor is configurable only through
the documented advanced flag, off the zero-code path.

## P1-D7. Errors speak human — the failure catalog

Every refusal has a message naming what happened and what to do next:
path rejections (already built), unreadable encodings, empty/headerless
files, duplicate column names, ragged rows (count reported, refusal
with the first three offending line numbers), memory exhaustion (told
plainly with the file size), and zero-row tables. The catalog is a test
fixture: every message has a test asserting its exact shape.

## P1-D8. Testing strategy

- Neutral seeded fixture GENERATORS (committed as code, provenance-
  compliant) build nasty-case tables at test time: every taxonomy rule,
  every sentinel decision branch, every refusal.
- Golden-hash tests pin profile bytes per platform (D12).
- A property battery: for random-but-seeded neutral tables, the profile
  round-trips (parse → describe → counts agree with pandas' own).
- The offline scanner's new pandas/numpy API enumeration gets red
  mutations (an unlisted pandas API reference must fail the scan).
- The decontamination scanner runs unchanged; profiler fixtures use
  neutral vocabulary by construction.

## P1-D9. What Phase 1 honestly does not do

No cross-column structure of any kind is detected (Phase 2 decides how
relationships are profiled and represented). The profile v1 may evolve
before the Phase 3 end-to-end freeze; `profile_version` exists so that
evolution is explicit. Very wide tables (thousands of columns) and
multi-gigabyte files are supported only within memory limits, stated in
the README.

## Acceptance criteria (sketch — finalized at review)

1. `synthtwin profile` exists behind the path validator; the four
   Phase 0 guards all pass with the new code and dependencies.
2. Every taxonomy rule and sentinel branch has a red/green fixture
   test; the failure catalog is fully tested.
3. Golden profile hashes verified per CI platform; the dependency
   introduction satisfies every D5 item (bounds, frozen lock, minimums
   job, scanner enumeration, hash-pinned install file updated).
4. A profile of a neutral demonstration table is generated end-to-end
   in CI and its `publication_notes` match the suppression rules.

## Questions put to review

1. Are the taxonomy thresholds (0.95 identifier uniqueness, 0.99 parse
   rates, the categorical ceiling, the sentinel outlier rule) the right
   DECISIONS to fix now, or should any be profile-time diagnostics that
   Phase 2 revisits with the fidelity framework?
2. Is the single-JSON profile contract acceptable as the boundary
   artifact, or should the review require a split (stats vs metadata)?
3. Is the pandas/numpy API-enumeration approach for the scanner
   proportionate under Amendment A3?

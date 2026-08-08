# Changelog

All notable changes to synthtwin are documented here. The format follows
Keep a Changelog; versions follow SemVer (0.x until the end-to-end product
exists).

## [Unreleased]

### Added
- Phase 1, the profiler: `synthtwin profile <table>` reads a local CSV
  table and writes two files -- the machine-readable profile the twin
  will be built from, and a plain-language summary that is also printed
  on the screen. Every column is given exactly one role (record number,
  whole numbers, measured numbers, dates, categories, two-value, free
  text, constant, empty) with the evidence for that reading recorded in
  words; missing values are counted by the spelling they were written
  in; numeric stand-ins for "no value" are recognized only when they are
  both outliers and frequent, with the verdict reported either way.
- Automatic suppression by role (plan P1-D6): record-number and
  free-text values are never published, and a label shared by fewer than
  eleven rows is pooled into a counted remainder. The summary states,
  every run, exactly what of the real table the profile carries.
- The table is read twice -- by the standard library's CSV reader for
  structure and by pandas for the values -- and the two results must
  agree. This is what turns a short row into a refusal naming the row
  instead of a row silently padded out with invented missing values.
- The first two runtime dependencies, `pandas` and `numpy`, each with a
  written justification, declared floors that a new `minimums` CI job
  installs and tests, a hash-pinned runtime closure
  (`requirements-install.lock`) exercised by the offline fresh-venv
  smoke test, and an enumeration in the offline scanner that reduces
  each library to the exact functions this code calls.

### Changed
- The offline import policy gained four reviewed extensions (plan
  P1-D10): the enumerated pandas, numpy and `csv` surfaces; a ban on
  calling any method on the objects those two libraries return, because
  a data frame carries writers that reach a database or a URL on their
  own; and text-origin tracking that follows an accepted string through
  its own data methods, slices and f-strings so that ordinary text
  handling does not need a helper function per method call.

### Earlier
- Phase 0 public skeleton: package scaffold, `synthtwin` CLI stub, the
  offline guarantee's layered checks, the decontamination scanner and
  manifest, the data-provenance guard, and CI with a single aggregate
  gate job (not yet a mechanically required context: the branch ruleset
  is deferred while the repository is private). No data functionality yet - profiling and generation
  arrive in later phases per the project plan.

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
- Suppression by role (plan P1-D6): a column read as record numbers, as
  free text, or as numbers no format can hold publishes no value of
  itself anywhere, and a label shared by fewer than eleven rows is
  pooled into a counted remainder. The summary states, every run,
  exactly what of the real table the profile carries.
- The table is read twice -- by the standard library's CSV reader for
  structure and by pandas for the values -- and the two results must
  agree. This is what turns a short row into a refusal naming the row
  instead of a row silently padded out with invented missing values.
- The first runtime dependency, `pandas`, with a written justification,
  a declared floor that a new `minimums` CI job installs and tests, a
  hash-pinned runtime closure (`requirements-install.lock`) exercised by
  the offline fresh-venv smoke test, and an enumeration in the offline
  scanner that reduces the library to the exact function this code calls
  (`read_csv`, and nothing else). It is the only *direct* dependency:
  numpy, `python-dateutil` and the others in the lock arrive inside
  pandas's own requirements and are imported nowhere in `src/`.

### Changed
- The offline import policy gained four reviewed extensions (plan
  P1-D10): the enumerated `pandas`, `csv` and `math` surfaces; a ban on
  calling any method on the objects `pandas` returns, because a data
  frame carries writers that reach a database or a URL on their own; and
  text-origin tracking that follows an accepted string through its own
  data methods, slices and f-strings so that ordinary text handling does
  not need a helper function per method call. The `math` enumeration
  replaced a numpy one: review round 1 showed that numpy's reductions
  made published statistics depend on the order of the rows, so the
  profiler computes them itself and numpy was withdrawn as a declared
  dependency.

### Repaired in adversarial review rounds 6 and 7

Nothing above has been released, so these are corrections to the Phase 1
work in the same unreleased entry rather than to any published version.
They are recorded because they change the profile a run produces and
what a person is told about it.

- **Record numbers are declared, never inferred.** Three rules that read
  a column's values and concluded "record numbers" are withdrawn: a
  column of measurements can be shaped exactly like a column of codes,
  and when the guess was wrong it destroyed a distribution the twin
  exists to reproduce. `--identifier` is now the only route to that
  reading, it beats every other rule, and it accepts any named column
  whatever that column holds. What is left of the old rules is a
  sentence: a column whose values almost never repeat is told so, and
  pointed at the option.
- **One taxonomy policy, and the code and the plan state the same
  thresholds.** A single line -- 99% of a column's present values, tested
  as a count so that no rounded division decides a role -- governs both
  the numeric roles and the date role; a second line at half the values
  is deleted, having published a mean over sixty numbers while dropping
  forty notes out of the distribution. A column below that line
  continues through the remaining rules rather than being sent straight
  to free text. The most different values a set of categories may hold
  is a tenth of the **table's rows**, capped at 1,000 and never below 2;
  measuring that share over present values instead punished a sparse
  column for being sparse. The earlier average-repetition rule and the
  separate twelve-value cap on mostly numeric columns are gone.
- **`--keep-value` and `--missing-value`.** A value your table means as
  real data even though the rules read it as "no value", and the
  reverse. A declared value that reads as a number is compared as a
  number -- as the exact number its spelling denotes, not as the binary64
  value that number rounds to, so two distinct integers can no longer
  collapse onto one declaration and remove cells nobody named. Anything
  else is compared by spelling after trimming and case folding. Naming
  one value both ways is refused rather than resolved by a precedence
  nobody can see.
- **A declaration is recorded as a count, never as a spelling.** The
  settings block carries how many values were named each way and the
  rule that matched them. It used to carry the spellings themselves,
  which republished a value out of every column at once -- including
  columns that publish nothing at all, and labels held back for being
  shared by too few rows.
- **A column that publishes no values publishes none anywhere in its
  block.** The rule is applied once, to the whole block, instead of per
  field: a declared identifier whose cells all read as "no value" used
  to reach the empty-column reading and publish the person's own
  spelling hundreds of times while the same run's summary promised the
  opposite.
- **The write transaction survives any failure the run can observe.**
  Both files are written under working names of synthtwin's own making
  and only then renamed into place. When the run raises -- with any
  exception, not only the ones this code composed -- each output name
  holds what it held before, or the person is told by name every file
  that is on disk and what each one holds, checked by looking rather
  than assumed from what was attempted. A path refusal on the second
  working file used to escape the whole transaction and leave a complete
  real-derived description in a hidden neighbor after a message that
  discussed only the path.
- **`profile_version` is 2**, because the settings block changed shape:
  where it held a list of declared spellings it now holds a record of
  how many were declared. The version exists so that a change of this
  kind is explicit rather than something a consumer of the file has to
  detect, so it moved with the change rather than after it.
- **The first row is taken by convention when nothing settles it, and
  said so.** No rule can tell a header row from a first record in a file
  where nothing distinguishes them, so synthtwin follows the CSV
  convention, records in the profile that the names were taken by
  convention, states it in plain words near the top of the summary, and
  offers `--first-row data` to take it back with every record kept. A
  file that shows its first row is a record stops and asks instead.
- **The numeric reference vectors are proved, not merely regenerated.**
  Every number the reference document publishes is re-derived from the
  exact value it stands for and its two neighboring float64 values. Four
  things stop the run instead of being certified: a number with no exact
  value recorded for it; an exact value that no published number spent;
  an integer sitting under a `float64` key where a binary64 value
  belongs, which JSON writes identically and an earlier proof walked
  straight past; and a whole number in a place the document did not say
  in advance that it publishes one.

### Earlier
- Phase 0 public skeleton: package scaffold, `synthtwin` CLI stub, the
  offline guarantee's layered checks, the decontamination scanner and
  manifest, the data-provenance guard, and CI with a single aggregate
  gate job (not yet a mechanically required context: the branch ruleset
  is deferred while the repository is private). No data functionality yet - profiling and generation
  arrive in later phases per the project plan.

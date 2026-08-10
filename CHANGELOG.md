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

### Repaired in adversarial review round 8

Still the same unreleased entry, and for the same reason: nothing above
has been released. Three of the four change what a run produces or what
a person is told about it; the fourth changes what the numeric
reference document's proof is allowed to certify.

- **A value you asked to keep is kept, on the numeric stand-in path
  too.** The ordinary declaration path already compared the exact
  number a spelling denotes. The stand-in path did not: it identified,
  counted, and removed cells through the binary64 value each number
  rounds to, so a neighbouring value that rounds onto `-999` was
  treated as `-999` however it was declared. A table of ordinary counts
  with fifteen copies of such a neighbour, that neighbour named with
  `--keep-value`, had those fifteen values deleted from the described
  population and its published minimum moved, with the summary
  reporting them as absent. The exact value is now carried through
  candidate identity, the occurrence count, the population the outlier
  test is measured against, and the removal, so no later rule may merge
  two numbers the declaration path had told apart.
- **The write transaction is one function with one handler.** The
  renaming step used to be a function of its own with a handler of its
  own, so the call between them ran unguarded, and several of the
  names the inner handler read were bound inside the block it guarded
  -- a stop at one of those lines raised UnboundLocalError out of the
  cleanup and cost the person both the account of the files and the
  reason the run stopped. Everything the handler needs is now bound
  before it opens, which is the one place it can be done, because
  nothing of synthtwin's making is on disk yet; each working name is
  recorded before it is reached for, since the file appears a moment
  before the call that makes it returns; and the type of an exception
  is no longer read as proof that a cleanup has run, so an unexpected
  refusal from a rename no longer leaves with two data-bearing working
  files behind it. Failures injected one at a time, at every bytecode
  boundary of every frame the transaction executes, across four
  scenarios, report no case where a surviving working file goes unnamed
  or a person's failure is replaced. Two residuals are stated in the
  plan rather than claimed closed: a second stop arriving during the
  cleanup costs the report, and one statement boundary after the last
  rename is described in worse words than the facts deserve.
- **Every number the reference document publishes is proved, at any
  depth and in every container its writer can use.** The proof walked
  dictionaries and lists, and Python writes tuples as JSON arrays as
  well, so a tuple-valued field could reach the file with nothing proved
  about it while the tool reported that every published number had been
  proved.
  The walk now covers the containers the writer accepts, and a mutation
  that hides numbers in tuples has to fail the proof before anything is
  written.
- **A declared identifier column records how often its values repeat,
  and `profile_version` is 3.** Two tables alike in every published
  count but different in their repetition pattern -- three codes over
  six rows, four/one/one against two/two/two -- produced identical
  profiles and identical summaries, so a twin built from the profile
  alone had to invent one of the two patterns and any grouped analysis
  told them apart at once. The block now carries an anonymous count
  multiset -- `n_distinct_by_occurrences`, keyed on a number of rows
  and holding how many different values cover that many: how often
  things repeat, never which things, no spelling and no length. The
  version moves with the shape, as it did at round 7.

### Repaired after the first hosted run of the Phase 1 suite

Four checks passed on the machine they were written on and could not
pass anywhere else -- and one of them, on Windows, passed by asserting
nothing whatever. Every one is a defect in the checking, not in the
product: the hosted matrix is the first place the declared floor
(Python 3.10) and Windows were ever run, and it caught them at once.
No product code changed for any of them, and on Windows the two rules
in question turned out to be STRICTER than the ones the tests had been
written against.

- **Two scanner mutations were written in Python 3.12 syntax and the
  declared floor is 3.10.** `def name[T](...)` and `type X = ...` do
  not parse before 3.12, so on 3.10 and 3.11 the probe module was not
  Python and the scanner never reached the rule the two tests pin. The
  scanner FAILS CLOSED -- a file it cannot parse comes back as one
  violation of its own, so the module is refused rather than passed --
  and that is now what those versions assert, while 3.12 and above
  still assert the specific message. The choice is made from
  `sys.version_info` and the choice itself is checked against `ast`, so
  the two can never drift apart. A separate test pins the fail-closed
  behaviour on every supported version with source no Python parses,
  and a companion pins the same rule for bytes that are not UTF-8, so
  neither route can become a silent pass.
- **A test built a folder whose name carried a terminal escape
  sequence, which Windows filenames cannot hold.** The property is
  real -- a path or value carrying display controls must be shown,
  never obeyed -- and it is kept on both sides. Where a filesystem
  allows such a name the whole route still runs, from the folder on
  disk through the command to the error stream. Where it does not, the
  control arrives as what it really is, text, through the same caution
  sentence and the same emitter; that half runs on every platform,
  Windows included, whose terminals obey these sequences too.
- **Three tests about a link at an output name asserted the POSIX rule
  as though it were the only one.** A link left where synthtwin is
  about to write is stopped by two different rules. On POSIX a link
  resolves to an ordinary local path, so the locality check passes it
  and the run is stopped later, by the comparison that finds the
  output name and the user's table are one file. On Windows the
  locality check refuses the link first -- any link, symbolic link,
  junction or mount point, because one there can quietly lead to a
  network location -- so that comparison is never reached and the run
  publishes nothing at all. The protection held on both; only the
  sentence differed, and two of the three tests stopped at an
  unexpected refusal before reaching any check of their own. Each test
  now asserts on EVERY platform what it was written for -- the table
  byte-for-byte unchanged, every link left exactly as it was found, no
  file published through one, no working file of synthtwin's own left
  behind, and the reason arriving as a sentence rather than a
  traceback -- and then pins the platform's own wording on the side
  that produced it. The Windows half is asserted rather than skipped:
  it is where the rule is strictest and where nothing had ever
  exercised it.
- **The write transaction's boundary injector traced nothing on
  Windows, so that whole check was vacuous there.** The injector
  recognizes the frames to interrupt by comparing each frame's
  filename against the transaction module's own, and the comparison
  string was rebuilt by resolving the module's path. On Windows the
  interpreter had imported the package through one spelling of that
  path while resolving it hands back the spelling the disk keeps, so
  the comparison matched no frame, no failure was ever injected, and
  every question the check asks went unasked. The floor each half
  carries -- a minimum number of boundaries that must have been
  injected into -- is what turned a silent pass into a red test, which
  is the reason those floors exist. The comparison string is now read
  off one of the module's own code objects, which is by construction
  what the frames carry, on every platform and every interpreter; and
  a new test states that fact directly, so the next reader of a
  failure here gets a diagnosis instead of a count of zero.

### Earlier
- Phase 0 public skeleton: package scaffold, `synthtwin` CLI stub, the
  offline guarantee's layered checks, the decontamination scanner and
  manifest, the data-provenance guard, and CI with a single aggregate
  gate job (not yet a mechanically required context: the branch ruleset
  is deferred while the repository is private). No data functionality yet - profiling and generation
  arrive in later phases per the project plan.

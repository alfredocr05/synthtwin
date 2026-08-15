# Changelog

All notable changes to synthtwin are documented here. The format follows
Keep a Changelog; versions follow SemVer (0.x until the end-to-end product
exists).

## [Unreleased]

### Added in Phase 3: `synthtwin validate`, and the fourth artifact
- **The third command.** `synthtwin validate <description>` reads the
  description and one CSV file -- by default the twin beside it, or
  whatever `--twin` names -- describes that file again with the
  profiler's own producer, and writes a quality report: which of the
  description's obligations the file meets, which it misses, and which
  nothing written in a CSV can evidence either way. The report is named
  after the file it measured (`<measured stem>-quality.txt`, so the
  ordinary run writes `<stem>-twin-quality.txt`) and names that file in
  its own first lines, so two candidate files never collide on one
  report and no report can be read as being about a file it is not.
  `--out-dir` and `--replace` work as they do on `generate`.
- **The exit code is the machine channel** (validation method V6.5): 0
  when the check ran and nothing was missed, 3 when it ran and something
  was, 1 when it could not run at all, 2 when the command line could not
  be used. A tool reading exit codes can tell a file that failed its
  check from a file that was never evaluated without parsing prose.
- **The quality report** states its verdict from the census alone. There
  is no sentence saying that every published fact was found, and none
  can be written from these counts: a pass means no checkable obligation
  was missed, with the within-window, authorized-deviation, withheld and
  not-checkable counts standing beside it and never folded into it. It
  carries the same limits every run -- no cross-column structure was
  validated because none is carried, rows independent and the grain
  undescribed, numbers on a twin are not research results -- plus the
  verdict-scope sentence: it is not a fitness verdict for any analysis,
  it validates nothing the description does not publish, and it cannot
  tell a synthetic file from a real one.
- **The write transaction gained a one-target form.** The quality report
  is one file, so two-files-or-neither is not a rule it can keep; every
  other rule is kept, and one is widened. The file a run may not write
  over is now a SET, because `validate` is handed two files and neither
  the description nor the file being measured may be landed on -- by
  lexical path, resolved path, link, alias, or a substitution made
  between the check and the write. A third `ArtifactWords` set gives the
  refusals the validator's own nouns.
- **The teaching chain runs end to end** (plan P3-D6): `profile` teaches
  `generate`, `generate` ends by printing the `validate` command line
  with this twin's own paths in it, and `validate` says what its verdict
  means, what it does not, and which exit code automation saw.
- **The handling rule now names every file a run leaves behind** on
  every claim-bearing surface: the profile, the plain-language summary
  beside it, the twin, the twin's report and the quality report. The
  quality report states measurements taken from the file it checked, so
  a verdict travels under the same rules as the thing it measured. The
  summary joined the list at the same time (plan amendment A-P3-8): it
  was never named, in this phase or the last, although it is the half of
  the description a person actually reads and it repeats the real labels
  the profile publishes. The generation report's bytes moved with it and
  its golden hash was re-recorded; the sentence that called a fidelity
  verdict later work is gone, because it is not later work any more.
- **The claim inventory counts instead of remembering.** The guard that
  was supposed to catch a stale claim accepted the retired wording, so
  six surfaces still counted the commands and the run's files the way
  they were counted before the validator shipped, while every test
  passed. It now takes both totals from the
  product itself -- the commands from the shipped parser, the files from
  the output names the modules carry -- and holds every surface to them,
  bans a built capability from being described as a later phase's work,
  and refuses a walkthrough that runs two of the three commands and
  stops.

### Changed in Phase 3: the quality report says what WITHHELD does not protect you from
- **The validator stops promising a defence it was paying for every
  round, and says so instead** (owner ruling 2026-08-14; plan amendment
  A-P3-13, validation method V5-A1). The rule that the report may say
  about the file it checked only what `synthtwin profile` run on that
  file would publish is unchanged, and so is everything about what may
  be PRINTED: no measured value, no string of the checked file, no count
  its own description pools -- not in the report, not on the screen, not
  in a refusal. What is withdrawn is the second half the rule used to
  claim: that somebody who writes their own descriptions and runs the
  check again and again cannot narrow a withheld number by watching
  which verdicts change.
- **THIS LOWERS a confidentiality guarantee, on the owner's authority,
  and the amendment prices it.** A sweep of hand-written descriptions
  can recover the count of oddly written cells in a numeric column
  exactly, can pin a style count the publication floor hides, and can
  read the header of a file the profiler refuses to describe, one guess
  at a time. In every one of those the person doing it is holding the
  file the number is about: running the check on a file requires having
  the file, and someone who has it can read it.
- **What it buys back, measured.** One subcheck was blunted for this
  defence and nothing else. `styles.canonical.<form>` had its recount
  rounded down to a whole number of publication floors before the
  comparison, so a file between one cell and one whole floor over its
  licence stopped being reported. The rounding is deleted rather than
  left unused, and the teeth are back at ONE cell: on the suite's own
  sixty-row fixture, a column licensed for 24 oddly written decimal
  cells and holding 25 now MISSES, and so does every one of the eleven
  counts inside that block, where all eleven held. No verdict moves the
  other way -- the comparison it replaces was never more than the count
  -- and a twin the shipped generator writes still holds every ceiling.
  The defence was no longer working anyway: the publication floor is
  itself a number the submitted description chooses, so sweeping it read
  the exact count straight back off the rounded comparison.
- **Nothing else is handed back, and the amendment says why for each.**
  Every other withholding this project records has a witness in which
  ONE report told two files apart -- the pooled style windows, the
  verdicts taken off a pooling column's own description, the seven
  withholdings on a file the producer refuses. A report travels to
  people who hold no file, so those stand exactly as they were.
- **The limit is written where a reader meets it.** The quality report
  carries it on every run, at the foot of the part that says what
  WITHHELD means; `SECURITY.md` carries it as a named residual risk; the
  README's limits table carries a row for it; and the charter's honest
  limits carry it for whoever writes the next sentence about
  validation. This moves the bytes of every quality report, and
  `GOLDEN_QUALITY_SHA256` is re-recorded with the reports diffed line by
  line before each re-record, the census identical entry for entry
  throughout.
- **The report says what the withholding PROTECTS before it says what
  it does not, and says it is not permission to move the page.** The
  paragraph used to open on the limit alone, which reads as though
  withholding bought nothing; it now says first that every question the
  report answers is about the one file it was given, that a number it
  withholds is a number it does not print anywhere, and that this is
  what lets the page be read by somebody holding no copy of the file.
  **And it stops there rather than at "so this page can be handed to
  somebody who has no copy of the file", which is what stood there
  first**: on a description made with `--smallest-group 3` that sentence
  sat under a section saying this same page now carries counts down to
  three rows and should not move without approval. Found by reading the
  page, not by a test.
- **No surface may state the withdrawn guarantee, and the suite goes
  red on any that does** (amendment A-P3-13 clause 3). The claim
  inventory in `tests/test_claim_inventory.py` gained a fourth family,
  and it is not a list of sentences: the guarantee was written five
  different ways in five different places, so a ban on any one shape
  would catch that shape only. A statement trips it when it NAMES the
  reader the ruling put out of scope -- a word for choosing what the
  description says, or for running the check more than once, attached
  to the word for a description -- and in the same breath PROMISES
  something about them, either by saying they cannot or by giving them
  as the reason a rule exists. A withdrawal standing near it is what
  tells the honest paragraph from the claim. Measured rather than
  asserted: the withdrawn promise was put back in eight wordings across
  eight files -- the front page, the security document, the charter, the
  validation method and four modules -- and every one of the eight
  turned the suite red.
- **The validation method is a surface of the claim inventory now, and
  had never been one.** It is the normative statement of what a quality
  report may say about a file that was measured -- the document an
  institution's reviewer reads before deciding whether a report may
  leave the building -- and it was the one specification no ban in that
  file covered. Adding it cost nothing: every check there was already
  true of it, and the fourth family then found two passages of it
  asserting the withdrawn promise as a live bound. Both are corrected
  in place, as are two in the plan that still said what V5.3 "says".

### Changed in Phase 3: `--smallest-group` works below eleven, and every file says so
- **A documented option no longer produces an unusable file** (owner
  ruling 2026-08-14; plan amendment A-P3-11). `synthtwin profile
  --smallest-group 2` wrote a description that `generate` and `validate`
  then refused, because the contract required `small_cell_floor >= 11` --
  and the refusal told the person to make the description again with
  `synthtwin profile` and use it exactly as written, which is what they
  had done. The contract's minimum is now 1, under a counted re-seal of
  `docs/spec/profile-contract-v4.md` section 4.4, and the whole workflow
  runs on any floor of 1 or more.
- **THIS LOWERS a confidentiality bound, and the amendment prices it.**
  The floor is what keeps a published group too large to point at one
  person. At a floor of `f`, no group named in a description covers
  fewer than `f` rows; at 1, every group is named exactly, a group of one
  row included. Where one row of a table is one person, a low floor
  publishes that a value exists together with how many people have it --
  the count is the disclosure, not a route to one.
- **Nothing else is relaxed.** Every floor-governed invariant still binds
  at the value the document carries (B5, D3, N2, N4, P2, V1, W5); at a
  floor of 1 nothing may be held back at all, and a description that
  fills a held-back field is refused under contract invariant S13. A
  floor of zero or below is still refused, and a hand-edited description
  is still refused for every other reason it was refused before. (This
  entry first said the refusal was "for breaking the invariant it always
  broke", which was true of three fields and false of five; amendment
  A-P3-16 below is the repair.)
- **The consequence is made visible rather than softened.** A `profile`
  run at a lowered number prints an unmissable warning before either
  file exists -- what a group that small can reveal about a person, in
  those words, and where those counts travel next. The plain-language
  summary, the generation report and the quality report each state on
  their own face that the description was made that way, so a reader
  handed one of those files alone can tell. The twin CSV carries no
  sentence because a CSV has nowhere to put one; its report is written
  beside it.
- **The quality report now names the floor it is running at, on every
  run.** Its withholding rule read "never named in any description",
  which was written when every description had one floor and now invites
  a reader to supply eleven and be wrong about what the report is showing
  them. This is the only change to the bytes of an artifact made at the
  default floor.
- **`_multiplicity`'s refusal at a floor of one reads as a sentence.** It
  composed "a number of rows from 1 to 0"; it now says the block must be
  empty, and why.

### Fixed in Phase 3: a floor of one really holds nothing back, and the report says only that
- **The floor-of-one invariant is enforced, not just written down**
  (plan amendment A-P3-16; contract invariant S13). The rule above said
  a description that holds something back at a floor of one is refused.
  Three fields were refused and five were not: a description written by
  the profiler itself stayed accepted after `(withheld)` was put into
  `missing_by_class`, `missing_by_source`, `utc_offsets` or
  `numeric_styles`, and after `n_sentinel_candidates_unpublished` was
  made nonzero. The reason is that four of those are rules holding a
  PUBLISHED count to the floor and EXEMPTING the pooled remainder -- an
  exemption does not become a rule at the bottom of the range by
  itself -- and the fifth, the count of stand-in numbers too rare to
  name, no rule of the contract bounded at any floor. The loader now
  checks the whole description against S13
  before it reads a column, and finds a pooled remainder by looking for
  the format's one word for "held back" wherever it stands rather than
  by a list of field names -- so a field added later is covered when it
  is added.
- **The profiler will not WRITE one either.** Its publication guard
  checks the finished description before a byte reaches a disk, and its
  rule for a pooled entry ignored the floor entirely. It now has
  vocabulary for the floor's other half. No description the profiler
  writes at any floor changes.
- **The quality report stops saying "At 1 nothing is withheld at all".**
  Two rules put WITHHELD on an obligation line and only one of them is
  the floor's; the other asks whether describing the CHECKED FILE
  publishes a measurement of that kind at all. A floor-one report
  printed that sentence and then eighty-three WITHHELD lines, with the
  count of them in its own verdict summary. It now says what is true --
  nothing is held back for being a small group -- and names the other
  rule. No artifact made at the default floor changes.

### Fixed in Phase 3: a table whose times are stamped in UTC can be described
- **`synthtwin profile` refused every UTC-stamped table** (plan
  amendment A-P3-16 clause 4). The profiler writes `Z` as the offset of
  a cell ending in one, and the strict loader accepts `Z` wherever an
  offset may stand -- but the profiler's own publication guard did not
  know the string, so a column of `2024-03-17T09:00:00Z` stopped the
  run with the message that says this is a fault in synthtwin itself
  and there is nothing to fix in your file. The two writings of what a
  UTC offset is now accept the same strings, checked against each other
  string by string, and that comparison closed a second disagreement in
  the other direction: the guard accepted offsets out of range that the
  loader refuses.

### Fixed in Phase 3: a description ten spellings answer is no longer refused
- **A repetition count is read as the figures it is written in** (plan
  amendment A-P3-25 clause 1, validation method V4.2-A2). A description
  says how many rows each repeated value covers, written in figures. The
  check read those figures through the same reader it uses for a
  measurement, which is exact only up to about nine quadrillion -- so a
  description saying that ten values cover 9,007,199,254,740,993 rows
  each was read as saying one row less, the division that follows came
  out needing ELEVEN different spellings where ten are asked for and ten
  are available, and `synthtwin validate` stopped and said that no file
  could be that description's twin. It builds one. On a column you
  declared to hold record numbers the same arithmetic quietly took three
  checks off the report instead of stopping the run. The count is read
  as a whole number now, at any size, by the same reader that admitted
  it -- and a new guard follows every such key of the description
  through the code and refuses any reader that would round it, wherever
  somebody adds one.
- **A lesser bar is only ever given to the fact it was granted for**
  (plan amendment A-P3-25 clause 2). Where a column of labels holds back
  spellings that are too rare to publish, the ratified plan lets the
  twin fall short on how many different SPELLINGS it writes. That
  permission was being handed to a second count as well -- how many
  different values the column holds once upper and lower case are
  ignored -- which the description states exactly and the twin meets
  exactly. A file holding three such values where the description
  publishes two was called an authorized difference instead of a miss.
  Each count is now asked about on its own, and the check that compares
  this validator against the tool's own generator no longer skips a fact
  the generator met exactly, which is how the hole survived beside a
  green test.
- **A check that could not fail is a check again** (plan amendment
  A-P3-25 clause 3). How many different spellings a column of numbers
  can carry is worked out from two things: the numbers themselves, and
  every cell of that column that is NOT a number. The second was left
  out entirely, so a column of twenty whole numbers beside two cells of
  text was told a twin might hold as few as ONE different value -- a
  range from one value to every cell in the column, which no file can
  fall outside. Both distinctness obligations were dropped from the
  checks for that reason, and a file one value short of what the
  description publishes was told that nothing was missed. Those cells
  are counted now, at both ends of the range, and the obligations are
  checks again. **What is still open is written down**: how many
  different values the plainly-written numbers carry is decided by a
  construction this check may not read, so a file one value short of a
  count the twin's own report pins is reported as an authorized
  difference rather than a miss, and a test holds that gap at exactly
  that size.

### Fixed in Phase 3: four guards that reached less far than they read
- **A refusal a person can act on, held to that by the catalog like
  every other refusal** (plan amendment A-P3-23, validation method V9).
  When a description asks for a table that cannot exist, `synthtwin
  validate` stops and says so. That message was built inside the
  validator rather than in the file every other refusal lives in, so
  none of the rules that keep those messages readable -- open as a
  sentence, end as one, no programmer's language, and always tell the
  reader what to do next -- reached it, and nothing had ever pinned what
  it says. It is a catalog entry now. Its exact wording is pinned for
  each of the four things that can be wrong with such a description:
  which two published facts collide, that the description itself is
  valid, that no file can be its twin, which file was being checked, and
  both of the two instructions -- describe the table again, and, for
  somebody who was handed the description and holds no table, ask
  whoever wrote it. And it is now produced by running the command: a
  table is written, `synthtwin profile` describes it, and `synthtwin
  validate` on that description has to stop with this refusal.
- **The profiler will not WRITE a floor-one description that holds
  something back** (plan amendment A-P3-22). At a floor of one nothing
  is held back, and the strict reader has refused a description that
  says otherwise since the previous round. The half that WRITES
  descriptions was taught the same rule field by field, and one field
  was not on the list -- so the two halves of the product disagreed
  about what a floor of one means, on a real map the profiler builds.
  The writing half now looks for the format's own word for "held back"
  wherever it stands, which is the reach the reading half already had.
  What found this is the other half of the repair: the check that
  derives the rule from two descriptions of one table now puts every
  case it derives to BOTH halves instead of only to the reader.
- **Two guards that read less than they said they did** (plan amendment
  A-P3-24). The first walks the code that decides which cells of a
  checked file its own description reads, and refuses any reader in
  there that answers in the machine's own approximate arithmetic --
  because the same defect had come back three times. It read a call
  written as a name or as a dotted name, and dropped every other way of
  writing one, so a reader reached out of a list was invisible to it. It
  is now total over the ways a call can be spelled, with a probe for
  each, and it refuses a reader NAMED where a value belongs even where
  nothing calls it here. The second is the guard over the guarantee the
  owner withdrew on 2026-08-14, which no page here may make again in any
  wording: that somebody who re-runs the check with descriptions of
  their own is kept from narrowing a withheld number. It read one
  statement at a time, so the same promise written across two statements
  walked past. It now carries a promise forward to a
  following statement that is about the withheld number, which was
  measured against every surface here before it was written and reports
  none of them.

### Fixed in Phase 3: a check that passed a file its own description rejects
- **A "no value" spelling is read back out of the description only where
  reading it back is safe** (plan amendment A-P3-19, validation method
  V2.3-A2). The description publishes the spellings that made a column's
  cells empty, and the previous round read them back so that a person
  who profiles their own table with `--missing-value` and then checks
  that same table is not told its declared holes are data. But that
  field is written for a REPORT: a character that would command a
  terminal is replaced by text showing what it was, and two different
  spellings can come out the same. Both directions cost a verdict. A
  table whose holes hold such a character was told seven of its
  obligations were missed against its own description; and a DIFFERENT
  file, wearing the printable spelling, passed that description with
  nothing reported at all, although describing that file under the same
  declaration reads it as free text with every cell present. A report
  that passes a file its own description rejects is the one failure this
  project will not ship, so the read-back now covers only the spellings
  the report-writing cannot have altered. What that leaves is stated:
  where the spelling holds such a character, the table it was written
  from reads those cells back as data, and closing that needs a change
  to what the description publishes rather than a change to the checker.
- **The report on a description of NO rows is chosen by the reader, like
  every other report** (plan amendment A-P3-20, validation method
  V5.1-A1.2). An earlier round made the reader's own refusal decide
  which report a file gets, so two files `synthtwin profile` refuses
  with one sentence cannot draw two different reports. One branch never
  reached that rule: a description publishing no rows was answered
  before the file was ever read. Two files with a ragged row under
  differently-spelled headers -- one refusal to the profiler -- drew
  eight met obligations and one missed against five and four, and the
  check said the header names were correct about a file no reading of
  which finishes. The reader is asked first there too now, and a file it
  refuses for anything but "this file has no rows" comes back as that
  refusal, which is the more useful answer and the one the profiler
  gives for the same file.

### Fixed in Phase 3: the check now agrees with the twin the tool itself writes
- **`synthtwin validate` no longer reports the product's own output as
  missing an obligation** (plan amendment A-P3-18, validation method
  V4.2-A1). The validator decides four "corner" questions from the
  description alone, written from its own specification so its verdicts
  cannot inherit the generator's defects. That independence is only
  worth having if the two writings agree, and until now nothing
  compared them: `tests/test_p3v7f2_corner_parity.py` builds 219
  descriptions with the real profiler, asks the shipped generator for a
  twin of each, measures each twin with the shipped validator, and puts
  the two accounts of each governed fact beside one another. The two
  writings parted company in five places, and at each of them the twin
  met its description while the report said it had not.
- **A column of record numbers is measured against the values the tool
  can actually write** (A-P3-18 clause 1). Above one character the
  check counted every string the alphabet allows rather than the
  values the construction writes -- 8,460 two-character values where
  2,538 exist -- so a column of 2,539 of them was told it should hold
  them all and its twin was reported wrong three times over. A second
  gap of the same kind: a group of cells that has to be covered by
  values of its own alphabet needs at least as many different values as
  the widest repeated group leaves room for, which the earlier
  arithmetic could miss.
- **Two counts of different values are measured against the range the
  method allows, in both directions** (A-P3-18 clause 2). A column of
  labels whose held-back spellings covered it exactly was read as
  needing one more than it does, so the check demanded a count the tool
  cannot write; and a column of numbers whose own spellings force MORE
  different values than it publishes was held to the published number
  exactly, so its twin was reported wrong for holding what its
  description obliged it to hold. A file that now holds more different
  values than published, on a column whose spellings can carry them, is
  reported as an authorized deviation rather than a miss.
- **A check that could not fail is no longer printed as a check**
  (A-P3-18 clause 3). Where a column's own spellings leave the count of
  different values anywhere between one and every cell -- two hundred
  forced whole numbers written one way are the case -- the comparison
  admitted every file and proved nothing. It is now one line in the
  not-checkable part of the census, with the sentence saying why.
- **Two more obligations no CSV can evidence** (A-P3-18 clause 4). A
  datetime column whose earliest or latest offset was itself held back
  by the publication floor names no offset for that end, so nothing in
  a file can carry it; and a numeric column whose style map the floor
  has partly pooled owes at least the published count of a named form
  and at most that count plus the pool, rather than the published
  number exactly.
- **What is still open, said plainly** (A-P3-18 clause 5). How many
  different values a column's plainly-written cells carry is decided by
  the value construction, which the checker may not import and does not
  yet rewrite, so for a column of numbers it draws a range that HOLDS
  the generation report's rather than one equal to it. The suite
  asserts containment and says so.

### Fixed in Phase 3: three ceilings that did not mean what they said
- **A search allowed two hundred and fifty-six tries spent two thirds of
  them re-asking a question it had already answered** (plan amendment
  A-P3-17 clause 2, method G9.3 step 5). The rule that repairs a twin's
  count of different record numbers once case and edge spacing are
  ignored may try a stated number of layouts before it gives up. It was
  counting the tries and not the questions, and on a column found by
  review the same question came round ten times over: **2,466 tries
  carrying 246 different questions**, and the ceiling ran out having
  answered 82 of them -- before the first layout that would have
  worked. A question is now asked once and remembered. Measured on a battery of 1,174 columns the profiler wrote
  from real values, at four seeds: **12 of 4,696 twins missed that
  count before and 4 miss it now**, every one of the twins whose bytes
  moved is one that was wrong before, and the count of cells opening
  with a character a spreadsheet reads as a formula is unchanged.
- **The four that remain are one column, and the changelog says so
  rather than rounding to none.** Its cause is neither the ceiling nor
  the search: with every ceiling removed, 2,097 layouts are offered for
  that column and not one of them can build every collision it owes.
  The twin names the deviation in its report, as it always did.
- **A repaired layout is now held to what it WROTE, not to what its
  arithmetic promised.** A layout can name a family that has no spelling
  at the length its slot is pinned to; the twin then falls back to
  another alphabet and loses a count -- how many cells read as numbers,
  how many are figures alone -- that the layout met on paper. Every
  published count is recounted off the finished cells, and a repaired
  layout that gives up any count the first layout held is refused.
  **On the two batteries measured this check never fires**, and that is
  said here rather than left to be assumed: it is kept for the witness
  that reaches such a layout and for the property the amendment states,
  not for a number it moves.
- **The proof that every check the quality report ships can fail was
  walking one of the four kinds of description it ships for** (plan
  amendment A-P3-17 clause 3, validation method V8.3-A1). The two
  degenerate zero-row forms file fifteen checks between them and not one
  had a test showing it could fail, or binding it to the obligation it
  answers for. All fifteen now do.
- **The guard that keeps a withdrawn promise out of this repository was
  not reading the governing plans** (plan amendment A-P3-17 clause 1).
  It named a passage of one of them as a place the 2026-08-14 ruling had
  to correct, and never opened it. It reads them now, and found one
  stale claim on the first run: a paragraph still describing a bound
  that was deleted the same day, now marked superseded where a reader
  meets it. Three sentences that walked past the guard -- a promise made
  as an outcome rather than as a barrier, a word for a description it
  did not carry, and a withdrawal standing in front of the promise it
  was read as curing -- are kept as its own tests. **What a list of
  words cannot do is stated beside the list**: no finite list bounds an
  infinite set of paraphrases, so this is a guard and not a proof, and
  what would be a proof is written down in the amendment for the owner
  to weigh.

### Fixed in Phase 3: a twin of a column of record numbers holds its folded count
- **A published count the twin got wrong on 3.7 per cent of a battery
  of real producer descriptions is right on all of them** (owner
  ruling of 2026-08-14, plan amendment A-P3-12, method G9.3 step 5).
  **Corrected 2026-08-14**: "all of them" is all of the two batteries
  measured below. A third battery, built later to a different shape,
  found the miss again on 12 of 4,696 runs; that is repaired and
  measured under A-P3-17 clause 2 above, where the four runs that still
  miss it are counted rather than rounded away.
  Where a description of a column of record numbers records two
  spellings that come down to one value once upper and lower case and
  spaces at the ends are ignored, the twin owes that collision. Which
  values carried the collisions was settled before any of them was
  spelled, and whether a family of values can carry one depends on the
  spellings: a value already at the longest published length cannot be
  lengthened by a space, and a value with no letter cannot change case.
  So the twin could ask one family for more collisions than it had room
  for while another family stood idle, and wrote a fresh value instead
  -- missing the description's own count of how many different values
  it holds ignoring case. Measured on two independently built batteries
  of descriptions the profiler wrote from real columns, every one of
  which its own column answers exactly: **44 of 1,200 and 68 of 918
  were wrong before; none is wrong now**, at four seeds.
- **A twin that already met every published count does not move by one
  byte.** The layout that shipped is tried first and kept the moment it
  works, so the repair can only reach a column that was already wrong.
  Measured: on this project's own 200-description identifier battery at
  four seeds, 800 twins, not one byte changed and the count of cells
  that open with a character a spreadsheet reads as a formula is the
  same before and after. Across both hazard batteries, every run whose
  bytes moved is a run that was missing a published count.
- **What it costs, stated rather than left to be found.** Two of the
  1,200 repaired columns now write 9 and 12 cells opening with such a
  character where they wrote none; no column writes more of them than
  it did in order to gain nothing, and every one is named in the
  generation report as before. Generation is seven to fifteen per cent
  slower across a battery in which every failing column is included,
  and unchanged on a column whose first layout works.
- **And where such a count still cannot be held, the report now says
  something TRUE about a column of record numbers.** The line carried
  the sentence written for a column of dates -- that how often a value
  repeats is not a fact the column's rule holds on to -- which is false
  of this one role, whose rule meets the repetition pattern in the same
  run. It now says what actually happened: the description asks for two
  spellings that come down to one value, and the published length range
  left no second way to spell one of them.

### Fixed in Phase 3: the Windows half of the matrix could not run the suite
- **One line in one test stopped every governed Windows cell** (review
  item P3-V4-F10, round 5 item 10). The proof added last round drives
  the "this file could not be opened" refusal through the shipped
  command at a real condition, and it decided whether to skip by
  calling `os.geteuid()` -- a function Windows does not have. All ten
  `windows-latest` cells of the CI matrix therefore ended in an
  AttributeError before proving anything, and CI green is a merge
  requirement, so one test's convenience blocked the branch outright.
- **The condition is now built in the mechanism each platform HAS, and
  the mechanism is checked before the command is run.** POSIX takes
  every read permission off the file. Windows locks the file's whole
  length against every other handle -- locks there are mandatory, and
  "the file is open in another program" is how a Windows user actually
  meets this refusal -- with a share-nothing handle as a second try.
  Whichever mechanism ran, the file must be present and must refuse to
  open before the case proceeds, so a mechanism that quietly does
  nothing (`chmod` on Windows moves the read-only attribute and
  nothing else) makes the case fail rather than pass. Guarding the old
  call with the platform name instead would have swapped an error for
  a skip on the one platform this refusal matters most on.
- **Two further proofs that were skipping on Windows now run there.**
  The refusal that stops `generate` writing a twin over the
  description through a link is asserted on every platform, each in
  the sentence its own rule produces -- the stricter Windows rule had
  nothing asserted about it at all for this command. And the fixture
  guard's process-helper mutation no longer carries a POSIX-only mark:
  the guard refuses an import by NAME, before the interpreter goes
  looking for the module, so the case is driven on every platform.
- **The fixture guard learned what Windows uses to create a process.**
  Asking that question is what the skip above had been hiding:
  `_posixsubprocess` was in the blocked-import list and `_winapi` --
  the module that creates a process on Windows, emitting no
  `subprocess.*` audit event of its own -- was not. Both are blocked
  now, as is every `_winapi.*` audit event.
- **Where a condition genuinely cannot be built on a platform, the
  test says so by name.** A folder that refuses to be written cannot be
  made from the standard library on Windows, and a POSIX superuser
  reads a file whose mode bits forbid everybody; both skips now name
  the host and the reason rather than reading as though the check had
  held there.
- **And the suite now asks this question of itself.** A new guard reads
  every test module and refuses two things: a call to an `os` member
  Windows lacks that nothing has guarded, and a module-level import of
  a module only one platform has -- which would fail collection for a
  whole file rather than one test. On the state before this repair it
  names `os.geteuid` at the line that broke the matrix.

### Fixed in Phase 3: six proofs that proved less than they claimed, and two stale sentences
- **The non-vacuity proof no longer reads its answer off the thing it
  is testing** (review item P3-V4-F6). An entry of the shipped
  validator's table is the triple (registry fact, profile predicate,
  subcheck), and five hundred and nineteen of the five hundred and
  eighty-eight registered red cases named only two of the three: the
  registry FACT was taken off the validator's own output at test time.
  Rebinding a subcheck to another fact of the same disposition
  therefore moved the expectation with it, and coverage, membership and
  uniqueness all stayed green over a table whose facts were wrong. The
  binding is now written out in the test file and compared with the
  shipped table in both directions: the roles the fixtures are
  described with are stated and checked against the DESCRIPTION, the
  fact each subcheck answers for is stated and checked against the
  REGISTRY, and no site may bind a fact other than the one stated. Two
  hundred and thirty-eight lines of stated expectation replace five
  hundred and nineteen derived ones.
- **And that proof walked half the table** (plan amendment A-P3-21,
  carrying the same review item). An entry of the shipped table is
  either a verdict or a line saying no CSV can evidence this
  obligation, and the binding proof read the first kind only. So the
  nine entries that exist ONLY where a corner sends a fact to the
  second kind -- four about a datetime column's offsets, three about a
  record-number column's counts of different values, two about a
  numeric column's -- were bound by nothing: rebinding one of them to
  another fact of the same column left the whole suite green while the
  report named one fact twice and another not at all. The walk now
  collects both kinds, over the six ordinary fixtures, the four
  description shapes, and three descriptions built here by the real
  profiler for the express purpose of reaching a corner, each held to
  the corner it is for.
- **The claim guard can no longer be evaded by how a constant is
  spelled** (review item P3-V4-F7). The reading that counts what a full
  run leaves behind recognized one spelling of an output name, so a
  sixth output declared as a typed constant, in single quotes, under
  any other name, or built by a call left every "five files" sentence
  in the repository green beside a run that wrote six. The reading is
  now of the package's own syntax rather than of one line shape, and
  beside it a test RUNS the three commands and counts the files on the
  disk, which no spelling can hide from. It found a live stale claim on
  the way: `quality.py`'s handling helper said "four files" while
  printing the five-file rule.
- **A private docstring stopped claiming a necessity the report does
  not.** The generation report says an invented sign-leading cell
  proves the real column held such values only WHERE the description's
  counts leave no other spelling, and says synthtwin does not always
  reach for the fewest it could. The helper that composes those lines
  still said it flatly, of every such cell.
- **The randomness trap reaches the engines** (review item P3-V4-F8).
  It enumerated four modules written out by hand and their public
  attributes, so `numpy.random._mt19937.MT19937(1).random_raw()`
  returned values with the whole claimed trap installed. Every module
  reachable by attribute from `numpy.random`, `random` or `secrets` is
  now walked, private submodules included; classes are trapped where
  their methods cannot be; and the two module-level generator instances
  are replaced by stand-ins that refuse to be read.
- **The line-ending guard has no route around it any more** (review
  item P3-V4-F9). It followed a written path by the name of the
  variable, so a helper that returned an extensionless path, stored in
  a list and handed over as `paths[0]`, was outside it. Every
  text-mode write in the suite now pins its line ending -- sixty-six
  writes gained the argument -- and so does every handle opened for
  writing, so no classification decides what the rule covers.
- **The failure catalog's reachability is driven, not searched**
  (review item P3-V4-F10). Its reachability test looks for the
  builder's name in the source, which a refusal whose raise site had
  been refactored away would still pass -- measured: taking both
  handlers for an unreadable measured file out and leaving the token
  behind kept that test green while a `PermissionError` reached the
  person as a traceback. The refusals plan P3-D6 names for the validate
  path are now produced by running the shipped command at the real
  condition, with the exit code and the printed sentence both asserted.
- **A stopped `validate` run says which file it did not write** (review
  item P3-V4-F11). It said "No new description was published" about a
  command that writes no description, and a stopped `generate` run said
  its own twin file held "the new description this run produced". The
  words a command carries now reach both sentences and the clause
  saying what a working file holds; the profiler's messages are
  unchanged to the byte.

### Fixed in Phase 3: two guarantees the documents claimed and the code did not have
- **A verdict about a spelling no longer counts out loud.** Whether a
  numeric cell's text is a spelling its own value licenses is a fact
  `synthtwin profile` publishes about no file at any count, so the plan
  rules it outside the disclosure envelope -- and a ruling like that is
  worth exactly the bound it carries. The bound written down was one
  bit per column; the ceiling on non-canonical cells compared its exact
  recount against a number the submitted description names, so eleven
  candidate descriptions read that recount off the report exactly, and
  two files whose own descriptions are the same bytes came back HELD and
  MISSED. The recount now reaches the verdict only at the publication
  floor's own resolution -- the resolution below which a description
  names no count at all -- so a sweep locates the floor-wide block and
  never the number. It costs teeth, and the plan prices them: a file
  less than one floor over its licence is no longer missed there, and
  no arrangement can have both, because the licence is the submitted
  description's own number. **This entry is superseded: the owner ruled
  the candidate sweep out of scope on 2026-08-14, the rounding is gone
  and the teeth are back at one cell.** See the entry above, "the
  quality report says what WITHHELD does not protect you from".
- **A report about a file the producer refuses says what that refusal
  says, and now it cannot say anything else.** Two of the reader's
  refusals are reported on rather than passed along, and which report a
  file got was decided by a walk `synthtwin validate` did before the
  reader was called. That walk and the reader had a precedence to agree
  about, and did not: moving a repeated name's columns moved the report,
  adding one row under a header holding a zero byte turned a report into
  a refusal, and a ragged file changed which refusal it drew as soon as
  a name was repeated in it. The walk is gone. The reader is called
  first and the report is chosen by the refusal it raises, so two files
  the producer refuses with one sentence get one report by construction.
  The repeated-name refusal and report also stop naming which columns
  repeat: the profiler's own refusal quotes the name and names no place,
  so the place was never a fact a report about that file could state.

### Fixed in Phase 3: three readings the validator's own generator contradicts
- **A reading you keep is a reading, not a hole.** A researcher who
  keeps `-999` as real data profiles with `--keep-value -999`, and the
  description publishes that candidate as kept. `synthtwin validate`
  deleted those cells from its recount anyway -- every built-in missing
  spelling and every built-in numeric stand-in, whatever the description
  said about them -- so the twin `synthtwin generate` writes from that
  very description came back with style obligations MISSED and exit 3.
  A cell is now dropped only where describing the measured file reads it
  as a hole: the description's own kept set first, the built-in table of
  missing spellings next, and a stand-in's fate taken from the column's
  own published verdict on that candidate. The same defect rejected a
  person's own table where the producer keeps a stand-in because the
  column's spread makes it no outlier -- a route with no declaration in
  it at all, which the twin cannot even reach.
- **A column of dates is measured against the construction that writes
  it.** The generator pins the first and last cells of a datetime column
  to the published earliest and latest instants; the validator's window
  did not, so a file holding six different quarters passed a bound its
  own construction puts at seven. The allowance for reading a cell back
  was a step of the published precision plus fifty-nine seconds instead
  of one unit of the ordinal space plus fifty-nine, so a rung sitting a
  whole minute below its window was reported inside it. And the ladder
  was read with floating-point arithmetic where the method fixes whole
  numbers, in seconds where the method counts a whole date in days,
  which drew windows ending in the middle of a day -- part of a day
  narrower than the construction, so a conforming twin could be called
  wrong at a rung. All three are one repair: the window is written out
  from the method, and the suite compares that writing with the
  generator's own at every resolution, every precision and eight column
  lengths, so the next drift is red on the commit that writes it.

### Fixed in Phase 3: the sign a table already had, and the check that had gone quiet
- **Owner decision 9 (2026-08-13).** A record number synthtwin invents
  may open with a sign where the published counts leave no other
  spelling of that width -- which is also the proof the real column held
  such values, so the twin inherits a hazard the table had rather than
  making one up. The refusal that stood here for a day is withdrawn.
  Where it is needed is decided by the packing, which runs first with
  that family closed and reaches for it only when no assignment of whole
  groups meets every published count without it.
- The generation report's spreadsheet paragraph told every reader that a
  hazardous cell was a value their description published. For a column
  that publishes no values at all that was false. It now names the
  columns whose cells were invented, says why the counts left no other
  spelling, and says that the same cells behave the same way in the real
  table -- which is where it points the reader to settle it.
- **Owner decision 11 (2026-08-13).** The frozen reference oracle still
  implemented the retired pooled-plain rule on a branch no frozen case
  exercised, so the independent check on pooled spelling was not in
  force there and every vector stayed green regardless. The oracle now
  carries the amended rule, a sixth branch case reaches the branch, and
  that case carries a mutant which must change its cells.

### Fixed in Phase 3: a whole number keeps its shape at any width
- **Owner decision 10 (2026-08-13).** A column whose source wrote very
  wide whole numbers in figures -- more than sixteen of them -- was
  published `plain` and came back from the twin as
  `100000000000000000000.0`, which a reader takes for a decimal column.
  That is exactly the type change the published spelling map exists to
  prevent. The sixteen-figure ceiling that caused it belongs to the
  canonical spelling of a number in the profile DOCUMENT, and was being
  applied to the twin's plain cells, where it does not govern: such a
  cell owes only that it reads back as the same number and classifies
  as plain, and a whole value's full digit expansion does both however
  wide it is. No frozen case reached the branch, so no golden hash and
  no reference vector moved; a column that does reach it now writes its
  digits.

### Fixed in Phase 3: the two open defects the registry carried
- **The pooled numeric spelling (P2-C5-F3).** A description holds back
  the forms used by fewer rows than the smallest group size, and the
  contract wrote every one of those cells plainly -- which a column
  whose published smallest or largest value carries a decimal point can
  never do, because such a value has no point-free spelling at all. The
  twin was therefore required to miss a total no generator could reach,
  on 8 of the producer battery's 240 columns. A held-back cell names no
  form, so it is now spelled by its own value: plainly where the value
  has a point-free spelling, and in the value's own canonical text where
  it has none. Contract 7.5.7 and method G6.4 carry the amended rule and
  a recount identity whose every clause is checked separately, with each
  published count a floor so no form can be substituted away. The
  ordinary case moves no byte.
- **The two-character record number (P2-C5-F4).** Its first shape was
  already closed by the joint packing that settles length and band
  together; only the contract's prose still said otherwise. Its second
  shape was a genuine breach: for a two-character whole number in the
  code alphabet the generator wrote `-0` through `-9`, meeting the
  published count by breaking the rule that no invented value may open
  with a character a spreadsheet reads as the start of a formula -- and
  leaving the report's own formula paragraph telling the reader that an
  invented cell was a value their description published. The family is
  withdrawn, the code band starts at three characters, and a description
  that leaves no spelling at all now meets a named refusal instead:
  `generation-whole-numbers-need-code-room`, the fifth of method G12,
  landed there as an amendment rather than as an unannounced branch.
- The disposition registry's `OPEN` mapping is empty for the first time
  since it was created.
- Two defects the repairs and their reviews found are recorded rather
  than fixed quietly, each with its measurement and its two possible
  outcomes, in the Phase 3 plan's P3-D8.1: the same two-character code
  family reached by a column whose values are not all whole numbers,
  and a column of very wide whole numbers, which a source writes in
  figures and the twin writes with a decimal point. Both need an owner
  decision. A third record sits beside them: the frozen reference
  oracle still implements the retired pooled-plain rule on a branch no
  frozen case exercises, so its independent check on pooled spelling is
  not in force until that decision lands and the oracle moves with it.

### Added in Phase 3: the ratified plan, and the repository goes public
- The Phase 3 plan (`docs/plans/phase-3-product.md`): the validate
  command and its plain-language quality report, the repair of the two
  open registry defects, the visibility flip, and the first release --
  ratified at plan review round 5 after four rejecting rounds whose
  every item is trailed in the plan's own review record; the five
  reviews are in `docs/plans/reviews/`. The plan joined the governing
  set under the disposition seal in the same change, so `GOVERNING`
  now holds four documents and the guard's exact lists moved with it.
- Phase 2 closed by owner decision (2026-08-12), its review record
  standing exactly as written; the charter's phase ledger now says so,
  and Phase 3 is current.
- Stage 1 of the plan's claim migration: every sentence describing the
  repository as private, on every live surface including the CI
  workflow and the tools, is retired in favor of the visibility-flip
  story, enforced by a new whole-tree test
  (`tests/test_p3_flip_migration.py`) because the claim inventory's
  surface list deliberately excludes `.github/` and `tools/`. The
  historical records -- the changelog and the plans -- keep their own
  dates' truth.

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
  (`read_csv`, and nothing else). It was the only *direct* dependency
  of Phase 1; `python-dateutil` and the others in the lock arrive inside
  pandas's own requirements and are imported nowhere in `src/`.

- The generator, `synthtwin.generation`: the twin's cells built from the
  profile and a seed and from nothing else -- one random stream, made
  once from the seed, threaded through by hand, with every value derived
  from full-width whole-number draws in first-party arithmetic. It never
  reads the real table, reads no file at all, and hands back the cells
  together with a record of what the twin ACHIEVED beside what the
  profile PUBLISHED, so the report names every difference rather than
  implying there was none.
- The second direct runtime dependency, `numpy`, under the same protocol
  as the first: a written justification (plan P2-D8), a declared floor
  the `minimums` CI job installs and tests, and the hash-pinned closure
  regenerated. The generator uses exactly one name from it,
  `numpy.random.default_rng`, and exactly one call on what that returns.
  The profiler still computes its own statistics and imports numpy
  nowhere.
- **The frozen generation reference vectors** (plan P2-D7, method
  section G14): `tests/reference/generation-reference-vectors.json`,
  built by `tools/reference/make_generation_reference_vectors.py` and
  bound in the provenance manifest, so CI rebuilds it from the generator
  and byte-compares it on every run. The tool implements the published
  method specification from that document alone and imports neither this
  package nor numpy nor pandas -- it could not import numpy in any case,
  because the fixture guard refuses `ctypes` and numpy imports `ctypes`.
  It therefore states its vectors as a pure function of GIVEN uint64
  words, which the file carries as inputs, and derives every uniform,
  bounded range, arrangement and cell from them in exact standard-library
  whole-number arithmetic. Fourteen cases are covered, across two
  committed files that are one oracle -- one transform, one proof layer,
  split only because each file must stay under the manifest's byte cap.
  The first nine: a date-only column, a quarter column, an offset-bearing
  column on the utc clock, a column mixing parsed cells with counted
  stand-ins, a whole-number column whose rounding direction decides four
  of its cells, a column that writes the shortest round-trip digits at
  both boundaries of the fixed-point window, a label column with
  published and invented spelling variants, an identifier column that
  must fold two spellings onto a partner, and one publishing whole
  numbers across all three alphabet bands. The five in
  `tests/reference/generation-branch-vectors.json`, added under review
  items P2-C3-F3 and P2-C4-C3 for branches the nine leave unexercised: an
  unrepresentable column whose three published families are packed
  together, free text whose class and alphabet counts are one packing,
  an identifier whose fold collisions no case change can build, a
  column carrying the literal decimal, leading-zero and leading-plus
  spelling styles, and a published end whose seconds field is 60, which
  the whole-second ordinal space has no place for and the endpoint route
  writes exactly. **Every one of the fourteen carries a committed mutant
  that reverts the branch it exists for and must fail**, held in one
  table whose keys are asserted equal to the case set, so a case cannot
  be added without one (review item P2-C4-C2).
  Every binary64 the file publishes is proved correctly rounded -- or
  proved exact, which is the stronger claim the transform's exact steps
  make -- by whole-number comparison against the midpoints to its two
  neighbours, and the run refuses a full-generator mutant before it
  writes a byte.
- **Golden twin and report hashes** (plan P2 acceptance criterion 6,
  method conformance items 10 and 11): `tests/test_twin_golden.py` pins
  three digests for one fixed description -- the description the
  generator is handed, the twin's bytes and the report's bytes -- built
  by the real producer from the seeded neutral table, so nothing is
  committed for it. Three rather than two, so a moved twin digest says
  for itself whether the producer or the generator moved it. Each is a
  change detector and none is an oracle: the oracle for the cells stays
  the frozen reference vectors, and the oracle for the counts stays the
  recounting from the twin's own cells. They run in the plain pytest
  run, so every cell of the matrix runs them, and a difference between
  two platforms, interpreter versions or library versions turns red
  there instead of shipping as a quietly different twin.
- **The rung window proved able to fail** (method conformance item 5).
  The two-sided acceptance bound on the nine interior ladder rungs is
  now put through four columns of a materially bent ladder, laid out by
  hand: the faithful one, which it must accept, and three it must
  refuse -- one built from the two published ends alone, one with the
  nine interior rungs each read one place along the ladder, and one with
  two interior rungs exchanged. All four hold the published minimum and
  maximum exactly and nothing outside them, so every other numeric check
  passes on all four and the window is the only thing that separates
  them. The assertion the mutants meet is the one in force, not a copy.
- The built-artifact smoke test now runs `synthtwin generate` and not
  `synthtwin profile` alone. In the same fresh venv, from the same
  installed wheel and under the same socket guard, it profiles the
  seeded neutral table, hands the description that run wrote back to the
  same command, and checks that the twin and the report are both there
  and that the twin is 240 rows by 10 columns with the published column
  names and no byte-order mark. A generation path broken only in a
  packaged wheel now turns CI red instead of shipping.

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
- The offline import policy gained three more reviewed extensions for
  Phase 2 (plan P2-D13). `numpy` is readmitted as one name and one name
  only, `numpy.random.default_rng`; every other numpy name, and `import
  numpy` itself, stays refused. What that name RETURNS is enumerated
  too, because a library object is not covered by the enumeration that
  produced it: the generator answers to `integers` alone, and each of
  that call's five arguments must be a value this package built itself;
  the array it returns answers to no method and no attribute; and a word
  taken out of that array, by index or by iteration, is still a library
  scalar carrying `dump` and `tofile` until `int()` turns it into a
  plain whole number, which is the one operation permitted on it. `csv`
  gains `writer`, with the file handle enumerated to this run's own
  validated output target, the rows to sequences built under the
  audit's eyes, and the dialect parameter added to the callback-slot
  table in both its argument forms. Each capability has a mutation test
  that must stay red.

### Added in Phase 2: the profile contract is version 4

Phase 2 builds the generator, which reads the profile and never the
table. Five facts the profile did not carry are what a twin cannot be
built without, so `profile_version` is **4**. Nothing was removed and no
key changed shape: every version 3 key keeps its name, its type and its
meaning, and `docs/spec/profile-contract-v4.md` states all of it
normatively.

- **Three axes beside the role.** Every column now carries
  `statistical_type`, `quality_state` and `structural_role`, derived by
  a fixed rule, and a consumer dispatches on those rather than on the
  role name. The third is not derived from the role at all: it says
  whether the person named the column with `--identifier`, which is
  true even of a declared column whose cells all mean "no value" and
  which therefore ends up described as an empty column.
- **How often values repeat, on every column that publishes none.**
  `n_distinct_by_occurrences` -- a declared identifier's key since round
  8 -- is now carried by free-text columns and by columns of numbers no
  format can hold, in the identical shape. Without it, sixty notes each
  written twice and sixty notes with one written thirty-one times were
  the same description.
- **A reserved cross-column block.** One top-level `relationships` with
  eight names, every one empty, because this version preserves no
  structure between columns and a consumer should read that stated
  rather than infer it from an absence.
- **How each published label was written.** A label is published in one
  settled form -- trimmed, upper and lower case folded together -- so a
  column holding `A`, `a`, `B`, `b` published two labels and nothing
  about the four values it holds. Each published label now carries
  `variants`, the exact spellings of it, and `variants_withheld`, an
  anonymous count of the ones held back. **Every spelling is governed by
  the small-cell floor exactly as a whole label is**: below it, it is
  counted and never named, and a label the floor held back carries no
  spellings at all. This publishes something version 3 did not, and the
  summary now says so where a person deciding whether the profile may
  leave their machine will read it.
- **How the numbers were written.** Columns of counts and of measured
  numbers carry `numeric_styles`: how many cells used each of six
  spelling forms -- plain, leading zero, leading plus, decimal, and the
  two exponent cases -- under the floor, with rarer forms pooled into a
  counted remainder. It carries no value and no magnitude, only form.
  Three columns reading `0`, `0.0` and `0e0` produced byte-for-byte
  identical descriptions before it, and a reader infers a different type
  from each.

### Changed in Phase 2

- **The canonical serializer and the write transaction moved out of
  `profile.py`**, into `canonical.py` and `writing.py`, which import
  neither the table reader nor the taxonomy. Both are code the generator
  has to reach, and `profile.py` imports the reader's own table type, so
  a module importing it would inherit that reach whether or not it ever
  called it. Nothing about either changed but where it lives; both are
  re-exported under the names they had.
- **The write transaction's refusals name the files of whichever command
  is running.** The transaction is no longer the profiler's alone, and
  four of the
  messages it composes named the profiler's files in plain words: "The
  profile could not be written to ...", "... next to your table", "...
  replaced your own table", and "a profile and a summary from two
  different runs do not describe the same table". A stopped `generate`
  run would have told somebody that their profile could not be written
  -- the one file that command never writes to -- and sent them to check
  a table the command never opened. The words are now an argument, the
  two sets live in `errors.py` beside every other message, and every
  message the `profile` command produces is the same byte for byte as
  before.

### Fixed in Phase 2: the two obligations of the invented alphabets

The frozen reference vectors carry an identifier column the generator
disagreed with, and the specification supported the vectors on both
counts. The case was held as a strict expected failure while the
GENERATOR was repaired to the oracle; the vectors were never adjusted
to match the code they exist to check.

- **Fold collisions are now built rather than named.** Where a column
  publishes fewer folded identities than raw spellings, method section
  G9.3 requires the difference to be constructed: the identities that
  will be varied are drawn from the part of the domain that holds a
  letter, and each carries a case flip. The generator instead recorded
  the shortfall as a deviation. Method section G12 grants that fallback
  to columns of numbers alone, and the contract makes both distinctness
  counts exactly recountable on all three roles that invent their
  values. The cause was one record of what a column had already
  written, holding both "this spelling is taken" and "something folds
  onto this" under one mark: the partner of a fold collision is by
  definition new only in the first sense, so it was refused every time
  and no collision could ever be placed. The two senses are now
  recorded apart, the letter is asked for on the identities the
  collisions are actually taken from, and a case flip is only ever
  taken from a value of its own alphabet and numeric class, so meeting
  the folded count cannot quietly cost a different published count.
- **A column of record numbers no longer writes figures where the
  description publishes none.** Method section G9.5 step 3, which G9.6
  imports for record numbers, gives a value counted in the code
  alphabet a leading character that is not a figure, so it cannot read
  as figures alone; the generator wrote plain figures and named
  nothing at all, which is the worse of the two failures, because a
  reader of the report never learned of it. Each band now leads with a
  character that keeps its own alphabet count, and a column whose
  description records that every value is a whole number leads with a
  figure other than zero, so a value's length is its count of figures.
- **Both alphabet counts are recounted from the written twin and named
  when missed.** One made-up value covers a whole group of rows, so a
  published count of cells that falls part-way inside a group cannot
  always be met; where it cannot, the report now names the fact, the
  published number and the number the twin holds, instead of leaving
  the difference for someone to find.
- The same repairs apply to columns of free text, which invent their
  values under the same rules. On columns of numbers too large or too
  small to hold, the collision path is in place, but that role's values
  are written at one canonical width in figures alone, and figures have
  no case: where such a column publishes fewer folded identities than
  spellings and has no cells of ordinary text to carry the collision,
  the shortfall is reported rather than built.

### Corrected in Phase 2: what synthtwin is allowed to claim

Two sentences this project repeated everywhere were stronger than the
product. Both are withdrawn, on every surface at once rather than where
someone happened to notice them, and `tests/test_claim_inventory.py`
refuses to let either come back: it reads the charter, the readme, the
security document, the changelog, the packaging metadata, the two
specification documents and every module under `src/`, and it fails both
ways -- if a retired form reappears anywhere, and if a surface that has
to state the true claim stops stating it (plan P2-D11). The third entry
below records the two new `SECURITY.md` disclosures that version 4's own
new facts require.

- **The categorical record claim is withdrawn, and a qualified one
  replaces it.** The old wording -- the flat assertion that a twin holds
  nothing of yours -- appeared in the charter, in `README.md`, in the
  package docstring, in the installable package's own description, in
  the command's help and in the profiler's own summary, and it promised
  something no tool that reproduces
  published counts exactly can promise. What is true, and what the
  product says now: the generator is handed the profile and a seed and
  nothing else -- it reads no source table, is never given a path to one,
  and samples or copies no row of it. That is a claim about where the
  twin's values come from. It is not a claim that no twin row can equal a
  real row, because meeting the published counts exactly can force the
  match with nothing copied anywhere: a table of eleven rows and one
  column, whose single label all eleven rows share, publishes that label
  with the count eleven, so the twin writes it in all eleven of its rows
  and each of those rows is a row the real table has. synthtwin offers no
  formal privacy guarantee, and now says so where a person will read it
  rather than only in the plans.
- **Institutional handling covers the twin and the report too, not the
  profile alone.** The profiler's summary, `README.md`, the charter and
  `SECURITY.md` each said the profile is real-derived material and left
  the twin and the report unmentioned, which reads as permission for the
  other two. It is not: the twin reproduces published counts exactly and
  the report quotes published facts back. The profile, the twin and the
  report all carry facts computed from real data, and every surface now
  says the institution's rules reach each of them. (Phase 3 widened the
  rule again, to every file a run leaves behind; see above.)
- **`SECURITY.md` gained an entry for each of version 4's two new
  published facts**, so a reader weighing whether a profile may leave the
  machine can see the delta rather than infer it. The label-spelling
  entry states the delta at its true width: the fold the producer applies
  is a Unicode case fold after trimming, not a capitals-to-lowercase map,
  so publishing the variants publishes every difference that fold used to
  absorb -- edge spacing and capitals, and also the equivalences Unicode
  defines, such as `ß` and `SS`. The `numeric_styles` entry states that
  the fact is about form only: counts per spelling style, floor-governed,
  carrying no value, no magnitude and no spelling.

### Repaired in Phase 2 code review round 1: the counts a twin has to hit

Nothing above has been released, so these are corrections to the Phase 2
work in the same unreleased entry. They change the cells a run produces
and what a person is told about them.

- **A published count of cells is now met exactly wherever whole groups
  can meet it** (review item P2-C1-F1). One made-up value covers a whole
  group of rows, so a count like "four of these cells are figures alone"
  has to be met by choosing which GROUPS answer for it. The old rule
  offered the largest group first and stopped: on groups of two, two and
  three with a published count of four it wrote five, although putting
  the two groups of two on that count meets it to the cell. The packing
  is now exact wherever an exact one exists, on all three paths that
  invent values -- record numbers, free text and numbers no format can
  hold -- and it carries the rules one published fact places on another,
  so a cell written in accounting parentheses is never counted among the
  cells written in figures alone.
- **Every one of those counts is now RECOUNTED from the finished cells
  and named where it was missed**, under the profile's own field name.
  The old code named some misses under names it had invented, filed
  others under the wrong field, and left the sign counts of a column of
  unrepresentable numbers silent even in the report.
- **A whole number is not the same as a value written in figures**
  (P2-C1-F1). A column of `+1` and `+2` publishes that every value is a
  whole number and that NO value is written in figures or in the code
  alphabet, and the twin now holds all three facts; the old rule read
  the first as implying the second and missed the other two.
- **A run always ends** (review item P2-C1-F2). A genuine profile -- a
  column of twenty-six different one-character values outside the code
  alphabet -- used to make `generate` consume the processor without end
  and without a message, because the walk that invents values came back
  to spellings it had already written. Every walk now stops at the end
  of the family it is walking, and where a column asks for more
  different values than can be written that way the run refuses before
  anything is written, names the two facts that cannot both hold, and
  says the profile is valid.
- **The capacity a refusal quotes is the number of values that could
  actually have been written** (P2-C1-F2), not the number of strings the
  alphabet holds. The two differ by a lot: the wide alphabet has 95
  one-character members and the ordinary-text construction can write 25
  of them.
- **The leading-zero family has no ceiling again** (review item
  P2-C1-F5). Owner decision 8 chose that family precisely because `0`,
  `00`, `000` supply as many spellings of one value as a profile can ask
  for; the implementation stopped at 4,096 and then repeated a spelling.
  A column of 4,098 differently written zeros now reproduces every one
  of them. A related diagnostic fault is gone with it: a column of
  nothing but zeros no longer builds value strata holding no cell, so
  the report no longer names an endpoint the twin never wrote.
- **Temporal facts the loader accepts are preserved by the generator**
  (review item P2-C1-F6). The contract permitted a column of dates AND
  times whose finest detail is a whole date, which no cell can hold and
  the profiler cannot produce; it is refused where it is decided. A
  published instant now carries calendar and clock RANGES, not only a
  shape, so `2024-99-99` is refused instead of being normalized into a
  real date somewhere else; a UTC offset carries its range the same way;
  and an offset is accepted only on a column that publishes a time of
  day for it to move. A description whose own recorded detail and clock
  cannot show its own first or last value is refused in the same place
  and for the same reason (see round 3 below); every description that
  loads has both of those values written back exactly.

- **Every approximated fact now has a stated two-sided bound, is
  measured on the twin, and is printed in the report beside the value
  the description publishes** (review item P2-C1-F4). The contract marks
  a handful of facts APPROXIMATED -- a column's average, spread and
  shape, the nine steps between its smallest and largest value, the same
  nine steps for a column of dates, how many different dates it holds,
  and the length and word summaries of free text -- and each of them
  owes a bound that both sides are checked against. `mean`, `std` and
  `skew` had no bound at all: the method left that job to a test
  battery, which is not something an independent implementation can
  conform to. Every one of them is now fixed in the method
  specification (G12.1 to G12.8), derived from the rule that builds the
  cells rather than measured on an output, and finite on both sides --
  including the skewness, whose bound falls back to the range every
  sample of its size lies in where its own derivation reaches zero.
- **The generator measures each of them on the finished cells** and
  hands back the published value, the achieved value, both ends of the
  bound and the answer, per column and for the run. A fact that lands
  outside its bound is ALSO named as a fact the twin could not meet, so
  the two lists a reader is given cannot disagree.
- **The report gained the section that says how close they came.** It
  used to say that measuring how close the twin came was a later
  version's work, which left a user told that the report distinguishes
  exact facts from approximate ones while it printed nothing about the
  approximate ones at all.
- **Each of those bounds is proved able to fail**, by putting a
  deliberately broken column through the same shipped measurement: one
  that collapsed the interior rungs onto the two ends, one that shrank
  the spread, one that mirrored the shape, one that wrote every date the
  same, one that wrote a date per row where the published range holds
  twelve days, one that mislaid a character, one that dropped the
  spaces, and one that invented a spelling.
- **The disposition matrix now has a completeness assertion**, promised
  by the plan and previously absent: every key the producer emits, for
  every role and at the top level, is looked up in the contract's own
  section 9 as it is written, and a key nobody disposed fails the suite.
  It found two: `length` and `words`, the two containers a free-text
  column publishes, which the matrix named only through their leaves.
- **Every sentence a profile publishes is now written from an
  enumerated grammar, and the finished description is checked before it
  is written** (review item P2-C1-F3, plan P2-D2). A description carries
  two kinds of text: a value the publication rules allow -- a column's
  name, a label many rows share, a date -- and a sentence synthtwin
  wrote about the column. Both are text at a key the description has
  always had, so a check that reads the key and the type cannot tell
  them apart, and a sentence that one day spelled a rare value into
  itself would have been published with every test still green. Notes,
  evidence, remarks and the header verdict are therefore no longer
  free text: each is built by name from one of an enumerated set of
  forms, filled only with counts and words of this package's own
  vocabulary, so a sentence about a value of the table cannot be built
  at all. The finished description -- including the notes lifted to the
  top level after each column block is complete, which an earlier check
  over the columns alone could never have seen -- is then walked to its
  last leaf: every sentence is written again from the form it carries
  and refused unless the words come out identical, every value stands
  at a place the rules authorize and clears the small-cell floor, and
  anything else at all stops the run before a byte is written. The
  refusal names the PLACE and never the text, because the text is what
  it is refusing to publish. Nothing a person sees changed: every
  sentence is the same sentence, byte for byte.
- **Every surface now says what the twin actually carries, and what is
  actually built** (review item P2-C1-F7, plan P2-D11). The record
  claim had been repaired everywhere and the claim inventory was green
  while four other material claims on the same pages were false. The
  package docstring listed fidelity between columns among the things
  the twin keeps, and the charter promised a relationship summary among
  the outputs, in a phase that generates every column on its own and
  publishes eight EMPTY relationship slots -- measured rather than
  argued: a table of two
  identical columns, every real row holding the same value twice, gave
  a twin in which zero rows of two hundred did. The front page said
  Phase 1, tagged the installed `generate` command as planned, called
  the profile/generator separation future architecture, and denied that
  numpy was a dependency at all; the security document's allowlist
  paragraph still counted a single function of a single third-party
  library, after numpy had returned with its own enumerated scanner
  surface. What every surface says now, in the same
  words: the twin reproduces the published facts of each column ON ITS
  OWN, carries no cross-column structure at all -- no correlation, no
  formula between two columns, no shared pattern of empty cells, no
  ordering between two event dates -- treats rows as independent while
  the grain is undescribed, so the twin of a repeated-measures table
  misdescribes the subject-level truth, and gains cross-column
  structure only in a later phase. The claim inventory was widened to
  hold all of it: relationship fidelity, phase status, command
  availability and dependency count each have a banned list of the
  false forms and a required list of the true marks, with the front
  page's built and planned sections pinned by name, and every ban
  carries a floor test proving it still catches the sentence this
  repository used to carry.

### Repaired in Phase 2 code review round 2: allocation and numeric form

Round 2 read round 1's repairs and refused four of them on the surface
where the twin decides which cells answer for which published count.
These change the cells a run produces and what a person is told about
them.

- **No ceiling counts the SHAPE of a description any more** (review item
  P2-C2-F1). Round 1's repair bounded the exact packing with two
  constants, and a column of record numbers the profiler actually emits
  reached one of them: 132 different group sizes made the depth
  expression 402 against a ceiling of 400, so the packing an exact one
  exists for was never looked for and three published counts came out
  wrong. Both constants are gone. The walk now prunes with two
  whole-number tests -- can the sizes still undecided reach a total this
  count accepts, and can every count still owed be made at all from what
  is unplaced -- answers the smallest counts first so the largest
  absorbs what is left, and never enters the same state twice. This
  repair left one ceiling standing, on undone WORK rather than on the
  size of a description, with the headroom measured rather than
  asserted (96 units, against 200,000). **Round 3 found a description
  that reaches it and it too is now withdrawn** -- see the round-3
  entry below, which is the current state of this surface.
- **Two coupled families are decided in ONE packing** (P2-C2-F1). A
  piece of free text answers for a numeric class and an alphabet at the
  same time, and a number too large to hold answers for a magnitude
  class and a sign; deciding each pair one after the other threw away
  answers that exist. A five-row column of free text lost an alphabet
  count that way, and forty shapes of a wide battery lost a sign count.
  All of them now come out exactly.
- **A published numeric form that CAN be written is written** (review
  item P2-C2-F2). A column holding eleven fractions beside forty whole
  numbers publishes forty cells written plainly, and the twin wrote none
  of them: the canonical spelling of a whole value on such a column
  carries `.0`, which reads back as the decimal form. Both misses were
  named, which is not the same as writing the form. The twin now writes
  a whole value with no point where the published map asks for one, puts
  whole values on as many strata as the map needs -- never at the cost
  of the counts of negative or zero values, or of the count of different
  values -- and looks ahead so a form is not spent on a cell that could
  not have worn it. A form with nowhere to go is still named.
- **The spellings that reach a published count of different values are
  available inside every form but one** (review item P2-C2-F3). Owner
  decision 8's leading-zero family was reached for only where the form
  was itself `leading_zero`, so a column reproducing a decimal or an
  exponent form held one spelling of a value and no way to make a
  second: an input of twelve copies each of three decimal spellings of
  zero came back with one. Zeros written after the sign leave the form
  and the value exactly where they were for five of the six forms, and
  the twin now reaches all three. `plain` is the one form with no such
  family, and the count it cannot reach is named and bounded rather than
  passed over.
- **Both counts of different values on a column of numbers now carry a
  measured range** (review item P2-C2-F4). The contract and the method
  both send them to a two-sided range where the permitted spellings
  cannot supply the published count, and neither end was measured
  anywhere: a run on a column holding nought through four named the
  shortfall and printed no range, while the report's closing sentence
  said every approximate fact had been measured. Both are now measured
  on every column of numbers against the supply the twin's own cells
  carry, both ends are printed, and the test inventory that says which
  facts are approximate is read out of the contract's matrix rather than
  transcribed, so a row whose disposition is conditional cannot be left
  out of it again.
- **A value that comes down onto another one through edge spacing is
  now BUILT, not named** (review item P2-C2-F6). Two spellings are the
  same identity once the ends are trimmed and the case is turned over,
  and only the second half of that was ever used to build one. So a
  value one character wide holding a single letter offered exactly one
  such partner, and a value written in figures offered none: a column
  holding `a`, ` a`, `a ` and ` a ` -- four spellings, one identity, one
  to three characters wide, every one of those a fact a person can
  recount on the twin -- was written as four identities and the miss was
  named. Naming it was honest and wrong, because the real column is
  itself the proof that all of those facts hold together, and owner
  decision 6 permits a lost count only where they cannot. A partner may
  now differ from the value it comes down onto in case, in edge spacing,
  or in both. Nothing else a person recounts moves when it does: the two
  alphabet counts and the whole-number reading are taken after trimming,
  words are counted between spaces, and the one fact spacing does move
  -- the length -- is held inside the published range, with the two
  published ends held to their own single length. The twin writer leaves
  the spacing alone and the reader hands it back, so a twin describing
  itself again finds every published count where it was.
- **The independent oracle no longer carries a rule the method withdrew**
  (review item P2-C2-F7). The vector tool chose the figures alphabet
  whenever a declared record column published every value as a whole
  number, and consulted the published alphabet counts only when it did
  not. That is the rule round 1 withdrew: a column of `+1` and `+2`
  publishes every value whole with BOTH alphabet counts at nought,
  because `+` is in neither alphabet. No frozen vector reached the
  branch, so rebuilding the file byte for byte never tested it, and an
  oracle carrying a withdrawn rule can reject a conforming
  implementation as easily as it can certify a wrong one. The tool's own
  owner reconciled it from the method specification alone: the bands
  come from the two published counts and from nothing else, and what
  the whole-number fact decides is what each band WRITES -- digits with
  a non-zero leading one in the figures, `<digits>e0` in the code
  alphabet, `<digits>.` outside it. A ninth frozen case,
  `identifier_whole_numbers`, reaches all three bands, so the branch is
  covered rather than merely corrected; the other eight cases rebuild
  byte for byte unchanged. The tool now also recounts every one of that
  role's exactly-observable facts from the cells it just built and
  refuses its own answer where one is missed, and it states no expected
  cells at all for the two corners it freezes no case for.
- **A false limit on how far the made-up-value walk may step is retired
  from the method specification** (review item P2-C2-F8). Beside its
  true proof that the walk stops at a family's own size, the document
  claimed the walk visits at most one index more than the number of
  values the column has already written. It does not, and a second
  reader building from that sentence would refuse a family the shipped
  walk draws from: a candidate is also stepped past when it reads back
  as the wrong kind of value, when it is one of the spellings that mean
  "no value", and when it reads as a date -- none of which consults what
  the column has written. Asked for the first value of an empty column
  of numbers too large to hold, the walk steps past one candidate and
  takes the next; asked for an eight-figure number, it steps past
  thirty-one in a row that read as dates. All five reasons a candidate
  can be stepped past are now listed, three worked cases are printed
  beside them, and the limit that is stated is the true one. The pass
  that asks for a value with a case to turn over now hands back "no
  more" when it gives up, so the walk is put back where that pass began
  -- it used to carry on instead, and every candidate it had stepped
  over was then spent for good.

### Repaired in Phase 2 code review round 4: the fourth lowering, and the registry that ends the pattern

- **The last exception to the two ends of a column of dates is refused,
  in both directions** (review item P2-C4-F1). The repair before this
  one refused the two pairs it had been given and left a third standing:
  a column whose values are published on the shared clock, whose first
  or last value sits within one offset's distance of the ends of the
  calendar this format can spell, so that moving that value onto the
  clock its own offset names asks for a cell no reader reads back as a
  date at all. The method called that the calendar's own end rather than
  an exception, the twin wrote the cell and named the end in the report,
  a test required that outcome, and the new wording guard listed the
  passage as a decided one -- so the guard was green about the sentence
  it existed to catch. The loader holds the value, its offset and the
  clock, so the contract's D10 now settles the pair where it is decided,
  at both ends of the calendar, and the method and the generator carry
  no case for it. The last second of a leap minute is unaffected: it is
  still written back unchanged on the ordinary clock.
- **The read-back check on the two ends stays, as a defect detector**,
  and a test proves it can still fail: the writing rule is reverted to
  the arithmetic route that produced the round-1 defect, and the run has
  to catch its own changed end, name it under the contract's own field
  name and print both values. No description a loader accepts can reach
  it, so the report line it writes is a fault notice rather than an
  outcome any description asked for, and it says so in those words.
- **Every published fact now has a machine-checked bar**
  (`tests/dispositions.py`, `tests/test_p2c4f1_disposition_registry.py`).
  Four separate repairs closed a review item by writing a quieter
  sentence into a normative document instead of meeting the bar the
  sentence had, and each was found only by the next adversarial review.
  The registry states the disposition the ratified plan gives every fact
  of every role, together with the plan's own words for it, and a test
  reads the plan, the contract and the method and fails when any of the
  three states a weaker outcome for a fact, omits a fact, or names one
  the plan does not. The plan is read, not trusted: softening P2-D6
  itself turns the same test red. A lesser outcome may be authorized
  only by quoting the plan's own sentence for it, so lowering a bar now
  means amending the ratified plan in the open. The proof that the guard
  reaches is part of it: each of the four lowerings is written back into
  a scratch copy of the document it belonged to, at three places, and
  every one has to come back red, as do four lowerings of obligations
  nobody has ever touched.
- **A lowering an adversarial review has already named can be carried,
  by its item number and no other way.** The registry's open list ties
  each remaining lesser statement to the review item that requires its
  removal, and a test requires that number to appear in the newest
  review record -- so an implementer cannot open one, and every entry
  goes stale the moment a new record lands unless somebody re-argues it.
- **That guard read prose for known wording, and code review round 5
  defeated it six ways out of eight, so the mechanism was replaced**
  (review item P2-C5-F1). A phrase list loses to rewording by
  construction: the six that survived were a lowering said in other
  words, a lowering stood beyond the attribution distance, a lowering
  captured by a nearer field name, a field name whose class depends on
  the role, an authorization added to the registry and propped up with a
  genuine but unrelated plan sentence, and an entry added to the escape
  hatch citing an item the newest record merely mentioned. Four
  comparisons carry the guarantee now, and not one of them asks what a
  sentence means. **The plan and both specifications are sealed passage
  by passage** (`tests/disposition_seal.py`, written by
  `tools/dispositions/seal.py`): a passage that is not in the seal is
  refused whatever it says, so writing or rewording one turns the suite
  red before anybody argues about it, and re-sealing is a separate,
  counted, self-describing edit -- one line per passage -- to a file
  that states what signing it asserts. **The registry's own judgment is
  sealed the same way**, in four surfaces, so the two attacks that
  edited it now need a countersignature. **An authorization declares the
  fact it belongs to, the plan region that has to carry its words, and
  the lesser class it grants**, and the registry's class may never be
  weaker than any class the plan's own region writes beside that name --
  so a quoted sentence no longer bypasses the parse of the plan.
  **The escape hatch is bound four ways**: the item must belong to the
  newest record's own round, stand as one of its item headings and be
  named in its verdict; the prose it excuses must already be sealed; the
  lowering must still be there; and the list must be empty by the time a
  review stops rejecting the phase. All eight of round 5's mutations are
  run against the new design in scratch copies, in the suite itself, and
  each has to go red.
- **And the dispositions became executable, so a quieter sentence buys
  nothing on its own.** A producer battery runs the shipped generator
  across every role and requires each line of its report to be one the
  ratified plan allows -- an approximated or report-only fact, an exact
  fact the plan authorizes a lesser outcome for, an exact fact a
  reviewer has left open, or one of two lines that carry the published
  value on both sides and disclose something else. Softening a document
  does not move that assertion by one character; weakening it is a code
  change a reviewer reads in the diff.
- **What this does not do, stated because the previous guard's claim to
  be binding is exactly what failed.** No check can decide whether new
  English prose lowers an obligation. Somebody who edits a document AND
  re-seals passes everything; what the design guarantees is that the
  edit cannot be silent -- it fails a check until a separate, explicit,
  counted signature is added beside it. Deleting a whole passage that
  RAISES a bar is caught only where that sentence is one of the
  anchors listed in `tests/dispositions.py`, and the anchor list is
  judgment rather than proof.
- **Two descriptions the ratified plan says to REFUSE were being
  generated instead, and are refused now** (review item P2-C5-F4). Plan
  P2-D6 reserves a refusal for a description no rule can satisfy, and
  the report line for a fact a rule CAN meet. A declared column of
  one-character record numbers published as whole numbers with fewer
  than all of them written in figures alone, and a column of free text
  publishing a word count its own published length cannot hold, are
  both descriptions no table can hold -- proved from the published
  numbers themselves, since one character that reads as a whole number
  IS a figure and a value of `L` characters holds at most `(L + 1) // 2`
  words. Both were being built anyway, with the exact fact recounted as
  missed and named in the report: the person received a twin the plan
  says the run should have stopped for, and nothing told them the
  description was one no table can produce. The generation-feasibility
  stage now refuses both before a cell is built, in the words the plan
  fixes -- the profile is VALID, the two facts that cannot both hold are
  named, and the remediation is an edit to the description file, which
  is what the person is holding, rather than anything that needs the
  table back. Two further shapes of the same proof are refused with
  them: a shortest published length of one character with nothing
  written in figures alone, and a word floor the shortest published
  length cannot reach. The contract's section-9 head no longer says a
  document whose facts cannot all hold is met as far as it can be; the
  method's G12 list carries four refusals instead of two; and a battery
  of eleven producer descriptions at three seeds still produces
  thirty-three twins, so nothing a real table describes was refused.
- **What that repair leaves open, said plainly** (review item
  P2-C5-F4). `all_whole_numbers` on a declared identifier is still
  missed on two shapes a real table DOES produce, and the run names it
  each time: a two-character value in the code alphabet, whose only
  whole-number spellings begin with a sign the artifact rules keep a
  made-up value from starting with, and a published length end pinned
  onto a group whose band cannot spell a whole number at that one
  length -- which the source's own values prove another pairing would
  have held. The first needs an owner decision, the second needs the
  length ends and the bands packed together as free text already does,
  and neither is a refusal: the description is one a rule could meet.
  Both are recorded in the registry's open list under this item rather
  than written as a quieter sentence anywhere.
- **The shape of a column of free text is decided WITH its published
  counts and no longer before them** (review item P2-C4-F2). The method
  gave the two published length ends and the two published word ends to
  the description's first two values, settled every other length by the
  walk that approaches the published average, and only then asked the
  grid of classes and alphabets for a packing inside that shape. A
  description the producer emits can have an exact answer that this
  shape forbids -- a twelve-cell column whose five-row value has to be
  counted in the code alphabet, while the shape gives that value the
  longest length and the largest word count, which no code-alphabet
  cell can carry. The ends, the lengths, the classes and the alphabets
  are now one allocation: the shapes are offered in a fixed order whose
  first member is the old rule, and the first whose grid meets every
  published count exactly is taken, so a description the old rule
  already answered is answered byte for byte as before and the frozen
  reference vectors are unmoved. Where no shape at the walk's own
  lengths answers, a value carrying no end may be written at any
  published length, because an exact count outranks an approximated
  average.
- **A number two characters long can be written in the code alphabet.**
  The only numeric shape that alphabet had was an exponent, which needs
  three characters, so a real column holding values like `-3` beside
  ordinary words lost both alphabet counts. A leading minus sign is a
  character the figures do not hold and what follows it still reads as
  a number, so that family now begins at two characters.
- **The four ends of a column of free text are recounted from the
  finished cells.** The shortest and longest value and the fewest and
  most words in one value are EXACT-OBSERVABLE, were pinned onto values
  by construction, and were measured nowhere -- so when a value pinned
  to the largest published word count was given a class that writes one
  unbroken run of characters, it wrote one word and no line of the
  report said so. The rule about several words is now stated over every
  family rather than over the code alphabet alone, and the four ends are
  recounted beside the alphabet and class counts, so a miss no rule
  foresees is named with both values.
- **How many cells hold each different number is the twin's own choice,
  and a published count now outranks it** (review item P2-C4-F3). Owner
  decision 10 says the twin writes every numeric spelling style in its
  published count, because the form is what a reader's type inference
  reads. A column of eleven `1.5`, twenty `100` and twenty `200.5`
  publishes twenty cells written plainly and thirty-one with a point;
  its own values prove that map; and the twin wrote twelve and
  thirty-nine on every seed and named both counts as missed. The reason
  was that the twin divides a numeric column into one stratum per
  different value and had been splitting the cells EVENLY between them,
  which gave the one stratum that could hold a whole number seventeen of
  the fifty-one cells. Nothing in a numeric block publishes those sizes
  -- there is no multiplicity map on a column of numbers -- so the even
  split is a default, while the style map is a published exact fact.
  The default now gives way: cells move into the strata that can hold a
  whole number, always within one sign band so the counts of negative
  and zero values are untouched, never emptying a stratum so the count
  of different values is untouched, and only as far as the published
  counts need. The rung window widens by exactly what that spends,
  because the window is derived from the widest stratum and is measured
  on every run.
- **Three more places where a published form went unwritten**, each
  found by generating a battery of descriptions through the real
  profiler rather than by reading the rule. A sign band left with one
  stratum -- the published `min` or `max`, carrying a point -- could
  carry no plainly-written cell at all, and every cell of that band was
  stuck on it, so a band may now take one stratum from the other side.
  A stratum whose nearest whole number was already another stratum's,
  which is what a FLAT ladder produces when a column's commonest value
  is its own published minimum, gave up rather than stepping to the next
  whole number inside its own share of the ladder. And where the counts
  could not all be placed, cells that could have been written plainly
  were spent on forms any cell could have worn, making the shortfall
  larger than the column's own values force.
- **The held-back remainder yields before a count the description
  names.** A form used by too few rows to name is pooled and written
  plainly, so it competes for the same cells as a form the description
  does name. It now loses that competition rather than sharing the
  shortfall, and the report says which part of a plain count the
  description names and which part it held back, because the total
  appears nowhere in the profile and a reader must be able to check the
  report against it.
- **What is left, and it is not nothing.** Where a column's published
  `min` or `max` carries a point, one cell must hold it and cannot be
  written plainly, so a pooled remainder can come out one or two cells
  short; and where a published ladder crowds several different values
  inside one unit, those strata have no whole number of their own and
  their cells cannot be written plainly at all. Both are recounted and
  named with both values, both are stated in the method, and the second
  can still cost a count the description names. What the repair does
  close in every case is the other half: the cells written plainly are
  exactly the cells whose value can be, so the shortfall is the size of
  the values and never of the placement. The registry carries this as
  the open item it belongs to rather than as a quieter sentence.
- **The fold-collision family says which member a slot takes, and not
  only what order the members stand in** (review item P2-C4-F4). A
  column of four spellings written in figures, folding onto one
  identity, has to build its three partners out of edge spacing alone.
  The method fixed the order those partners stand in and left the choice
  between them to be worked out from it, and two implementations worked
  it out differently: one wrote the one-space partners before any
  two-space one, the other stepped over a one-space partner nothing had
  written. Both columns satisfied every published fact, so nothing was
  lost except the property the frozen vectors exist to provide -- that
  an independent implementer working from the text alone writes the same
  bytes. G9.3 step 2 now states the rule: every slot walks its parent's
  family from that family's own start and takes the first member the
  column has not written whose length its own slot admits; a member one
  slot's window turns down is not spent; and the count of partners a
  parent has already supplied decides which parent comes next, never
  which member is taken. This ADDS a requirement and takes none away.
  The vectors were not adjusted to either implementation -- they already
  wrote what the stated rule produces -- and the comparison that had
  been carried as an expected failure now binds like the other thirteen.
- **Every one of the frozen cases now carries the mutant that reverts
  its own branch** (review item P2-C4-C2). Four of them did and nine did
  not, which is the same gap in a quieter form: a case whose own rule can
  be withdrawn while every committed byte stays put holds nothing up.
  The mutants are one table whose keys are asserted equal to the whole
  case set, so a case cannot be added without one; each either moves its
  case's cells or stops the oracle from building it; and each builds its
  case unmutated first, so none can pass by refusing for a reason of its
  own.
- **The leap-second end has a frozen vector rather than only an
  argument** (review item P2-C4-C3). The obligation had been lowered
  twice and argued over across three rounds while not one committed case
  carried a seconds field of 60 -- so an implementation that sent the two
  ends back through the whole-second ordinal space left every frozen byte
  where it was. The fourteenth case is twelve cells on the local clock
  published from `23:00:00` to `23:59:60`, its two ends written from the
  endpoint's own fields, and its committed mutant is the ordinal route
  put back. The pair no cell can show on the shared clock stays a loader
  refusal and not a vector case, because a description no loader accepts
  has no twin bytes to freeze.
- **The branch fixture's provenance sentence states its generator's
  imports literally** (review item P2-C4-C4). The registered generator
  there is the second entry point, which imports `os`, `runpy` and `sys`
  and executes the oracle beside it by one fixed sibling path; the
  narrower seven-module list belongs to that oracle. The manifest now
  says both, so a reviewer reading the "imports only" line as the
  complete inventory is reading a true one.

### Repaired in Phase 2 code review round 3: the two ends of a column of dates

- **The first and last value of a column of dates are exact on every
  description that loads, with no exception left anywhere** (review item
  P2-C3-F2). The repair before this one restored that rule where it had
  been lowered -- the contract's disposition row and the method's own
  construction -- and wrote the exception back into the paragraph
  after it: a description publishing an end no cell of its own recorded
  detail can show would have that end met as far as it could be,
  recounted and named in the report. The generator did exactly that,
  declining to write a published sixtieth second whenever the column's
  values were published on the shared clock, and the strict loader
  accepted such a description -- so a document this repository itself
  let through came back with its last value moved to the following
  minute, beside a row of the contract that says there is no exception.
  There are two descriptions of that kind, the producer writes neither,
  and both are now REFUSED where they are decided, by a new contract
  rule (D10), exactly as the whole-date-beside-date-and-time pair is
  refused. The generator has no case that declines: both ends are
  written from the published end's own fields on either clock, so the
  last second of a leap minute is carried by every column that can show
  one.
- **The two ends of a column's ladder of dates are that column's own
  two ends** (D11, found beside the item above). Nothing tied
  `date_percentiles.min` to `earliest` although the contract called them
  the same two instants, and the generator pins its first cell to
  `earliest` while placing the rest inside the ladder -- so a ladder
  beginning earlier than `earliest` produced a twin holding instants
  before its own published first value, and the report said nothing at
  all about it. The pair is now tied, which also makes the refusal above
  cover all four texts.
- **The guard against this class of drift now reads every passage of
  both specifications**, not one cell of one table. Every passage that
  speaks of an end being met with something other than what was
  published has to be one the test file decides on by name and with a
  reason, and the test proves it by adding exceptions -- including the
  two that were really written -- at three places in each document and
  requiring every one of them to be caught. Beside it, a battery walks
  every shape of temporal column and every end a reader can publish, and
  allows exactly two outcomes: refused, or described again with the same
  two instants.
- **A column of numbers no format can hold is packed over the counts it
  actually publishes, and over nothing else** (review item P2-C3-F1).
  Such a column publishes three separate divisions of the same cells --
  what the notation reads as, whether the value is a whole number, and
  what sign it settles -- and publishes nothing about how those
  divisions cross. The twin used to pick one crossing itself, sending
  as many out-of-range cells to "whole" as the whole count allowed, and
  then look for a packing of that. On a six-row table of two whole
  numbers written negatively, three cells written inside accounting
  parentheses and one fraction far too small to hold, that choice has
  no answer while the other choice of the very same published counts
  has one, so the twin came out with one numeric cell against two, no
  fraction against one, two negative cells against three and three more
  counts wrong -- all named in the report, and all avoidable. The
  packing now takes the three published divisions as three sides of one
  question and answers them together, so a crossing the description
  never fixed is never assumed.
- **Nothing counts the packing walk's work and stops it** (P2-C3-F1).
  The repair before this one left one ceiling standing -- 200,000 units
  of undone work, after which the twin decided the coupled counts one
  after another instead -- on the measured belief that no description a
  real table produced could reach it. One does: a 2,710-row column of
  numbers too large to hold, with 38 different repeat counts, needed
  more than five million units of that work before the walk it stopped
  would have answered. A ceiling a genuine description reaches is not a
  bound on cost, it is a published count traded away, so it is gone.
  What ends the walk is what always did: it never enters the same state
  twice and there are finitely many. The cost of that is stated rather
  than hidden -- this kind of question has no known quick answer, so a
  valid document nobody produced could take a long time -- and it is
  the same trade this project already made when it refused to cap the
  size of a description. Both repairs together answer that 2,710-row
  column in a fifth of a second, where the ceiling used to stop it.

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

### Repaired after the hosted run of the Phase 2 suite: the bytes a test writes

Every Windows job failed while every macOS and Linux job passed, on one
refusal: a description was not in the exact form synthtwin writes. No
product code changed, and none should have. The writer fixes the line
ending rather than leaving it to the platform (plan D12), so a
description synthtwin produces is the same bytes everywhere, and the
loader -- which writes the parsed document out again and compares the
bytes -- was right to refuse a file synthtwin had not written. The
defect was in the tests: they wrote the description themselves, in text
mode with no line-ending argument, so Python translated every line
ending to the platform's own and left a file that only Windows produces
and that the loader must then turn away.

- **The bytes of a description a test writes are now decided in one
  place.** `write_profile` in `tests/fixtures.py` serializes through the
  product's own canonical serializer and fixes the line ending, so the
  file it leaves is byte for byte the file `synthtwin profile` writes;
  a test asserts that equality against the product's writer for the same
  document. Twenty-three test modules that each wrote that file
  themselves now ask for it instead. One of the twenty-three, the
  loader's refusal battery, still composes bytes of its own for the
  cases whose whole subject is a file synthtwin would never write --
  which it says in as many words, and writes with an explicit line
  ending so that what it composed is what reaches the disk on every
  platform.
- **A guard reads the suite's own source so the next one cannot arrive
  unnoticed.** `tests/test_description_line_endings.py` turns red when
  any test writes a description -- or a file named like one -- with the
  line ending left to the platform, and it is put through the original
  defect in source form, so a rule that has stopped recognizing a
  description cannot pass in silence. A companion test writes a
  description with Windows line endings on any platform and asserts the
  loader refuses it with the message the Windows jobs printed, which is
  the property the whole arrangement exists to keep from reaching a
  person.

### Earlier
- Phase 0 public skeleton: package scaffold, `synthtwin` CLI stub, the
  offline guarantee's layered checks, the decontamination scanner and
  manifest, the data-provenance guard, and CI with a single aggregate
  gate job (not yet a mechanically required context: the branch ruleset
  is deferred while the repository is private). No data functionality yet - profiling and generation
  arrive in later phases per the project plan.

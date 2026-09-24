# Generation method v1 — the exact transform from (profile, seed) to twin bytes

**Status:** written before any Phase 2 code existed, under the owner
sequencing override recorded in `docs/plans/phase-2-generator.md`
(revision 5), and revised repeatedly since — clauses below cite their
own revisions 2, 4 and 5, each raised by a code-review round or an
owner ruling against the implementation this document anchors. This
header said "revision 1, written before any Phase 2 code exists" until
2026-08-20, which had stopped being true at the first of those
revisions and was plainly false once the generator shipped. It carries
no revision number now rather than a guessed one; the next amendment
to this document sets one and states what it counts.

**Not ratified, and that is a statement about process rather than a
doubt about the text.** No review round returned a ratifying verdict
on this document. Phase 2 was closed by owner act on 2026-08-12 with
its review record standing exactly as written, and nothing in this
repository describes Phase 2 or its artifacts as review-ratified. This
document is sealed and governing regardless: it is one of the
documents `tools/dispositions/seal.py` counts, and the generator is
held to it.

This is artifact 3 of that plan's four, and it carries out decisions
the plan makes; it introduces no mechanism the plan left open, except
the one the plan explicitly delegated here — the invention domain and
its capacity rule, with a named refusal (P2-R5-F4), which section G9
fixes.

**Who this is for.** Two readers, and the document fails if either is
left guessing. The first is the implementer of `synthtwin generate`. The
second is an INDEPENDENT implementer, working from this text alone, in
another language, who must produce the same twin bytes from the same
profile and the same seed. Every place where two conforming programs
could differ is therefore closed here by a stated rule, including the
ones that look too small to matter: the order of a loop, the direction
of a rounding, which end of a list a tie goes to.

**What it does not cover.** The profile's wire shape, key by key, is
`docs/spec/profile-contract-v5.md` together with
`docs/spec/profile-contract-v4.md`, which version 5 carries by reference
(version 5 section 2.2): a rule version 5 does not supersede is a rule
of version 5 at its version 4 wording and is cited below by its version
4 number. This document names published fields and assumes the
meanings the two of them fix. **This pointer is amended rather than original**
(plan amendments A-P3-28 and A-P3-30): it named the version 4 document
alone, which was true until the producer and the loader moved to
version 5 and false afterwards — and the reader it misdirected is the
one this document is written for, the independent implementer working
from this text alone. Nothing else here moves, because no generation
rule reads any field version 5 changed; the twin's bytes at a fixed
profile and seed are what they were, and the frozen reference vectors
prove it. The command line, the output file
names, the write transaction, the refusal catalogue's wording and the
generation report's own bytes are P2-D10's business. Fidelity
measurement and the quality report are `synthtwin validate`'s, and the
rules it measures against are `docs/spec/validation-method-v1.md`.

**This amends the sentence that called fidelity measurement later work**
(Phase 3 plan P3-D7 stage 2, amendment A-P3-8, 2026-08-14). The
validator ships, so a reader of this document — including the
independent implementer it is written for — is now told where the
measuring rules live rather than which phase would eventually write
them. Nothing this document obliges a generator to do moves: the
validator measures a written file against the PROFILE, and it is a
consumer of this method's output rather than a rule upon it.

**Vocabulary.** "Word" always means one full-width unsigned 64-bit draw
from the single stream of section G3. "Cell" means one value in one row
of one column of the written twin. "Published" means present in the
profile document; a fact that is not published is not available to any
rule here, and a rule that would need one is a defect in this document.

---

## G1. The boundary this method upholds

The transform below reads the profile document and the seed. It reads
nothing else. It has no access to the real table, no access to the file
the profile was made from, and no access to anything the profile does
not carry. That is not an aspiration of the implementation: it is a
property of this method, and it can be checked against this text —
**every input to every rule below is either a published profile field, a
word from the single stream, or a constant fixed in this document.**

Two consequences worth stating, because they are the ones an
implementer is tempted to breach:

- **No rule may read a twin cell it has already written back out of the
  written file** to decide the next one. Every decision is made from the
  in-memory construction described here, so the method never depends on
  the file system or on a reader.
- **No rule may consult the profiler's code.** Where this document has
  to agree with the profiler — the fold, the number parser, the date
  parser, the ladder positions — it states the rule in full and names
  the shipped function that must agree with it, so the agreement is
  testable in both directions rather than assumed.

## G2. The output bytes

The twin is one delimited text file, written the way the description
records its source file was (owner ruling 2026-09-15, plan P4-D86;
`source.encoding` and `source.dialect`, contract 4.3 and 4.3a). The
exact byte-level rules, because "CSV" is not one format. For an
ordinary source — UTF-8, comma, line feeds, minimal quoting, a final
line ending — every row below reads as it did before P4-D86:

| property | value |
|---|---|
| encoding | `source.encoding`, with a byte-order mark exactly when `source.dialect.byte_order_mark` |
| line ending | each line takes the next ending of `line_endings`, in file order, or, where `line_endings_spread` counts them instead, the ending `dialect.spread_endings` gives it (the commonest ending, the earlier in the listed order on a tie, ends every line no rarer ending takes; each rarer ending, in that same order, places its `c` lines one at a time, and its k-th line, counting k from nought, is offered the line `((2k + 1) * total) // (2c)` — the middle of the k-th of `c` equal stretches of the file — or, where that stands higher, the line just below the one this same ending took last; where the offered line is already taken the next free line below it is used, and where the file ends before a free line is found, the first free line from the top. STATED IN FULL at landing 2b.17's repair pass, for the reason G2.1's placement is: "spread evenly" does not decide which lines, a committed case freezes them, and two conforming programs would otherwise both answer to the sentence); the last line has none unless `final_line_ending`; an end-of-file mark follows where `end_of_file_mark` |
| field separator | `delimiter`, followed by one space where `initial_space` |
| quote character | `"` (U+0022) |
| doubling | an embedded `"` is written twice inside a quoted field, or after a backslash where `escape` is `backslash` (and a backslash is then written after one too) |
| escape character | none, or the backslash where `escape` is `backslash` |
| quoting | per column and per cell class (`absent`, `empty`, `number`, `text`) — a cell holding no character is `empty`; one whose text is a spelling of absence in contract 5.4.1's vocabulary (seventeen matched after trimming and a case fold, `NaT` byte for byte) is `absent`; one the profiler's number grammar reads as a number is `number`; every other cell is `text` (plan P4-D173): `needed` — quoted when and only when the field contains the delimiter, a quote character, a carriage return or a line feed (a backslash too under backslash escaping, a leading space under `initial_space`); `bare` — quoted only where it could not be read back otherwise; `always`; `mixed` is written `needed`. The header and the metadata rows take `header_quoting` and `header_rows_quoting` — **plus the two canonical exceptions below** |
| lines that are not records | the `sep=` line, the `preamble` lines, the header, the `header_rows`, and `blank_lines` standing after `after` data records, in that order; where `blank_lines_spread` counts them instead, its `lines` blank lines stand evenly from after `first` records to after `last` (`dialect.spread_places`) |
| a record's width | a trailing delimiter where `trailing_delimiter` says so; trailing empty cells left out where `short_rows`; a padded column's cells padded with spaces to its width where shorter |
| header row | written when `source.header_source` is `file`; not written when it is `generated` |
| column order | the `columns` list order of the profile, which the contract fixes as the schema order (P2-D6, STRUCTURAL) |
| row count | exactly the document-level `n_rows` data rows, not counting the header row when one is written |

**Canonical quoting exception 1 — a leading U+FEFF in a column name.**
A first column name beginning U+FEFF is always quoted (P2-D10). Written
unquoted it would begin the file with the byte-order-mark sequence,
which the reader then consumes, silently renaming the column.

**Canonical quoting exception 2 — a row that would otherwise be
empty.** When the table has exactly one column and that row's single
cell is absent, the cell is written as `""` — two quote characters —
rather than as nothing. Written as nothing, the line is empty, and the
shipped reader refuses a one-column file with an empty line (it cannot
tell a record whose only value is missing from a blank line left in the
file) while the second reader would drop it. The `""` spelling is the
one the reader's own refusal message teaches, it reads back as an empty
cell, and an empty cell is what an absent value is. This exception
cannot arise with two or more columns, because a row of absent cells is
then written as one or more commas, which is not an empty line.

**A line before the table is written as a stand-in, and the stand-in is
one record** (plan P4-D80, P4-D83). For each `preamble` run the twin
writes `dialect.preamble_line`: a blank line stays blank and keeps its
spaces, a comment keeps its mark and reads `# withheld line`, a line of
text reads `withheld line`. No word of the line itself is in the
description to write. The mark a run carries holds no quote character
and not the delimiter (contract FD11), so every line written here is
one field or one comment to the file's own reader -- a twin whose first
line was `"withheld line` was a file no reader could finish.

**Every other cell is written as its exact text.** No trimming, no
padding but a padded column's, no normalization, no locale, no
alteration of a published label — including a label a spreadsheet would
treat as a formula (P2-D10 and R-P2-6: counted and warned, never
altered).

### G2.1 Where the rows stand (plan P4-D86)

Three steps after every column is generated, drawing no word.

1. **The row sequence.** A column whose `sequence_start` is not `null`
   is written `start, start + 1, ...` in row order. It is written in
   place of the column's generated cells before the column is measured,
   so the report states what the file holds, and the words its plan drew
   are still drawn.
2. **The records holding nothing.** In a table of two or more columns
   with no row order, or with a row order and published records holding
   nothing, cells move only within one column so that exactly the
   published number of rows hold nothing in every cell (below).
3. **The sort.** Where `row_order` names a column, whole rows are
   permuted by that column's cells under the collation — a number read
   by the method's number reader, a cell with none last; or, under the
   `decimal_comma` collation, that same reader applied to the cell with
   its declared decimal comma and thousands point exchanged, because the
   twin writes this column's numbers with a comma and reading its own
   cells by the ordinary grammar would put `10,0` before `9,9` and hand
   back a column the description calls ascending and is not (review item
   CODEX-9); or the cell's
   code points — ascending or descending, stably, so rows the key cannot
   tell apart keep their generated order. The rows placed as holding
   nothing in step 2 stay where they stand, and the other rows are
   sorted into the places around them (repair of landing 2b.9: a sorted
   Excel table with formatted-empty rows below it is sorted).

   How step 2 places them: `leading` at the
   top, `trailing` at the bottom, `interior` spread evenly between.

   THIS PARAGRAPH STATES THE PLACEMENT IN FULL, and it was written at
   landing 2b.17's repair pass because it did not. "Spread evenly
   between" is not a rule an independent implementer can write: two
   conforming programs would put the interior records in different
   rows and both would answer to the sentence. A committed case now
   freezes these rows (G14.3, `row_arrangement`), so the rule they
   freeze has to be readable here — the way contract 4.3a states the
   comparable spread of blank lines, as arithmetic and not as an
   adverb. Counting rows from nought, with the published counts capped
   in this order — `leading` at the table's rows, `trailing` at what is
   left below the leading block, `middle` the rows between them and
   `interior` at `middle`:

   - the leading block is the first `leading` rows and the trailing
     block the last `trailing` rows;
   - the k-th interior record, counting k from one, is placed at row
     `leading + k * middle // (interior + 1)`. Where that row is
     already taken the next row down is taken instead, and that walk
     down stops at the last row above the trailing block, which is
     then used whether or not an earlier interior record took it (so
     where the interior records crowd the bottom of the middle, fewer
     rows are targets than `interior` counts).

   The cells are then exchanged, one column at a time and never
   between columns, in two walks taking the rows in order:

   - **the target rows are emptied.** In each column, a target row
     whose cell holds something is exchanged with the cell of the
     first row that is not a target and holds nothing in that column
     (a row that has received a cell holds something and is not asked
     again), and where the column has no such row left, that column's
     walk stops.
   - **no other row is left holding nothing.** A row that is not a
     target and holds nothing in every column takes one cell back: in
     the first column, in column order, that has a giver, the giver's
     cell is exchanged into it, and the row is done. A giver is the
     first row, in row order, that is not a target, holds something in
     that column, and holds something in two or more columns at that
     moment, so that it still holds something after it gives.

   A row-sequence column is written in place again last.

Whole rows moving, and cells moving within one column, change no
column's cells as a multiset, so no published fact of any column moves,
and the twin carries no structure between columns for either to break.

### G2.2 The twin of a workbook (plan P4-D79, P4-D82)

Where `source.workbook` is not `null` the twin is a spreadsheet
workbook and not delimited text (contract 4.3b). G2 above states the
bytes of a delimited file and does not reach here: a workbook cell is
TYPED, so what each cell IS in the file is a fact of its own, decided
from the description's census and never from the characters the column
generator wrote. That seam is what keeps the generator table-blind —
it produces each column's cells as text, knowing nothing about
workbooks — and it is why a column of text whose every cell looks like
a number is written as TEXT.

THIS SECTION WAS WRITTEN AT LANDING 2b.17 AND STATES RULES THAT WERE
ALREADY SHIPPING. They lived in plan P4-D79, in contract 4.3b and in
the writer's own docstrings, and this document said nothing about any
of them — so the second implementation this method requires of every
generator rule (G14) could not be written for the workbook writer at
all, because there was no statement to write it from. Nothing here is
new behaviour; what is new is that the behaviour is stated where the
oracle can be built from it.

**The package, and the one fixed order.** The twin is a zip package
whose members are written in exactly this order, which is part of the
determinism rather than a convenience:

1. `[Content_Types].xml`
2. `_rels/.rels`
3. `docProps/app.xml`
4. `docProps/core.xml`
5. `xl/workbook.xml`
6. `xl/_rels/workbook.xml.rels`
7. `xl/styles.xml`
8. `xl/sharedStrings.xml`
9. `xl/worksheets/sheet1.xml` … one per sheet, in workbook order
10. where the description publishes a defined table, and then only:
    `xl/worksheets/_rels/sheet<chosen>.xml.rels` and
    `xl/tables/table1.xml`

**Every member carries one fixed moment**, 1980-01-01 00:00:00, which
is the earliest a zip can store. A member ordinarily records when it
was written, and that would make the same description and the same seed
different bytes on every run. Across platforms the deflate stream
itself may differ between zlib builds; this method states that as a
limit rather than claiming past it, and what it freezes is the TEXT of
each member.

**Step 1 — the class of each cell** (`cell_classes`). One column's
generated cells, its published `cell_classes` census and its published
`value_class` go in; one class per cell comes out. A count the smallest
group held back (`null`) counts as NONE ASKED FOR BY NUMBER, and a
count published as `0` is a FACT that no cell has that class; the two
are never read the same way.

A class FITS a cell's text where the cell can be written as that class
(plan P4-D166): `text` fits every text; `error` fits one of the error
kinds (`#DIV/0!`, `#N/A`, `#NAME?`, `#NULL!`, `#NUM!`, `#REF!`,
`#VALUE!`, `#GETTING_DATA`, `#SPILL!`, `#CALC!`); `boolean` fits `TRUE`
and `FALSE`; `date` fits ISO text that NAMES A DAY OF THE CALENDAR —
the shape is `YYYY-MM-DD`, optionally followed by `T` and a clock, or a
clock alone, the clock being `hh:mm`, `hh:mm:ss` or `hh:mm:ss` with a
point and figures, and the fields of that shape must be a month among
the twelve, a day the month has in that year (G7.1's calendar, whose
leap rule is the Gregorian one), an hour of at most 23 and minutes and
seconds of at most 59 (plan P4-D291: the shape alone let `2006-06-32`
fit, and a `t="d"` cell holding it is a file no reader can open at
all). **A CELL HOLDING A SPELLING THE COLUMN'S OWN DESCRIPTION PRINTS IS
NOT BROUGHT ONTO THE CALENDAR** (item 1 of the dates pass of the second
Codex round, 2026-09-19). The correction is for the date candidates the
twin FABRICATES from a published shape; a published label, and a
published variant of one, is the source's own text and is owed
character for character. MEASURED at a floor of five, seed 0, on a
workbook column of 60 `2024-03-01` cells stored as dates beside 60
`2024-02-30` cells stored as TEXT, both published as labels over 60 rows
each: generation kept both and the serialization rewrote all 60 text
cells as `2024-02-29`, the source missing nothing and the serialized
twin missing six label obligations. A cell the source stored as legal
text is not an invalid date cell, and since `date` fits only a spelling
that names a day, holding the published spellings back also sends the
cells that DO name days to the date class first, so nothing stored as a
date names a day the calendar does not have. And `number` fits the text a
workbook stores as a number (an optional sign, figures, an optional
point with figures on one side or both, and an optional exponent whose
mark is followed by an optional sign and at least one figure — never a
grouped number, a decimal comma, a bracketed negative, a percent or a
currency mark, which in a workbook are a FORMAT worn by a plain number
and not the stored value).

- The cells holding no text take the three classes that hold nothing —
  `absent`, `blank`, `empty`, in that order — each handed out in row
  order to as many of those cells as its published count names. What
  is left takes the first of those three whose count was WITHHELD, and
  where none was, the group's LEADING class (below).
- The cells holding text take the five that hold a value. First
  `error`, `boolean`, `date` and `number`, in that order: each class
  whose count is published is handed out to as many cells, not yet
  given a class, that it FITS as its count names -- every such cell, in
  row order, where no more fit than the count; where more fit, the count
  is SPREAD over them by the smooth rotation, each fitting cell in row
  order adding the count to a credit and taken where the credit reaches
  the number of fitting cells, which is then taken back (plan P4-D187:
  thirty text cells of a column of numbers stored partly as text stood
  in its last thirty rows). Then
  `text`, by its published count, in row order: first to the cells no
  class still wanting cells fits — a class wants cells where its count
  was withheld or is not yet spent — and then to any cell left.
- Every text cell still without a class takes, in this order of
  candidates — the published `value_class` where there is one, then
  `error`, `boolean`, `date`, `number`, `text` — the first candidate
  whose count was withheld and which fits the cell; where none, the
  group's LEADING class if it fits; and `text` otherwise.
- A group's LEADING class is the one the column holds most of by its
  published counts, ties going to the earlier of the order above,
  **except that a class published as nought is never the leading one**.
  A withheld count is not a licence to write none, and a published
  nought is not a count to fall back on.

WHY A CLASS GOES ONLY TO A CELL IT FITS (plan P4-D166). The first
writing handed the error, boolean and text counts out in row order to
whatever the cells held, so a column of forty `#N/A` errors, forty
`North` and forty `South` got a twin marking twenty-six labels as
errors, and pandas read 27, 27 and 66 missing against 40, 40 and 40.
WHY `value_class` DECIDES WHERE A COUNT WAS WITHHELD (plan P4-D164): a
census held back whole because one cell was unlike the rest leaves the
twin nothing else to tell a column of digit texts from a column of
numbers by.

**Step 0 — a date is written back as the day count it was read as**
(repair of the stage-2b integration). The reader hands the column
machinery a number cell wearing a date or datetime format as its date
(contract 4.3b), so the generator writes dates. Where a column
publishes a positive `date` or `datetime` FORMAT-KIND count, or a
`format_code` of either kind, each cell holding `YYYY-MM-DD` or
`YYYY-MM-DD HH:MM:SS` (with an optional `.fff`) is replaced, before
step 1, by the day count a workbook stores for it in the published date
system — a whole day in
figures, a moment as the shortest spelling of its double — and the kind
of date it was is carried beside the cell through step 6's exchanges.
The 1900 system counts 1900-01-01 as day 1 and carries a 29 February
1900 that never was, so a date before 1900-03-01 stands one day nearer
its epoch; a date no day count of the system can hold stays text.

**EXCEPT A CELL THE CENSUS STORES AS A DATE** (plan P4-D284). A day
count is a NUMBER's spelling, and a workbook may instead store a date
as its ISO text (`t="d"`, cell class `date`, contract 4.3b). So step 1
is run FIRST, on the cells as the column generator wrote them, to
settle which cells are to be stored as dates; each of those keeps its
ISO text, every other date becomes its day count, and step 1 is then
run again over the cells as they will be written. **And the census has
to say so, not merely fail to deny it:** the first allocation is
trusted only where the column publishes a `date` CELL-CLASS count above
nought, or — where that census was withheld — a `value_class` of
`date`. A withheld census lets a cell no count claims take the first
withheld class its spelling fits, and a date's own spelling fits
`date`, so a column of ordinary day counts wearing a date format would
otherwise be given date storage it never had. Asked the other way
round, 120 `t="d"` cells lost their ISO spelling before anything could
fit the `date` class, the whole column fell through to `text`, and
every reader handed back strings such as `"45315"`; asked without the
census guard, 59 day counts of the study's titled book at a floor of
eleven turned into `t="d"` cells and the twin missed
`workbook.value-class`.

**Step 0a — a column stored as dates is written as dates** (plan
P4-D291). Step 1 hands the `date` class only to a cell that names a day
of the calendar, and that narrowing on its own would write a column the
description stores as dates as a column of TEXT: the cells of a column
whose ROLE publishes no value of it — free text, a long tail — are made
up from the column's published SHAPE, so a column of `2024-03-17` cells
read as free text is written `7001-26-23`, which wears a date's shape
and names no day. So, before step 0 and before step 1, in a column the
description says stores dates — a published `date` cell-class count
above nought, or a `value_class` of `date` where that census was
withheld, the same question step 0 asks — every cell wearing the ISO
shape above and naming no day of the calendar has each of its fields
brought to the NEAREST value the calendar allows, at the width it was
written with: the year to at least `0001` and at most `9999`, the month
into the twelve, the day into the days that month has in that year, the
hour to at most 23 and the minutes and the seconds to at most 59. A
cell that is not of the ISO shape, and one that already names a day, is
left exactly as it came — so a column whose dates ARE published, being
generated from instants, is not touched here at all, and neither is a
column of day counts.

WHAT THIS COSTS, STATED RATHER THAN CLAIMED PAST. The cells this
touches are cells of a column about whose values the description
publishes nothing but their shape, and the shape does not move — every
one keeps its length and its figures-and-marks form, so the form census
and the length facts the description does publish are met exactly as
before. What moves is the figures themselves, and they pile up at the
top of each field's range: measured at a smallest group of eleven on
118 made-up cells of the shape `%%%%-%%-%%`, 105 of the 118 months
stood above twelve, and 108 of the twin's cells are written in
December. How many DIFFERENT values the column holds does not move —
83 before and 83 after — because a made-up cell's year is four figures
and carries the differences. A reader who groups the twin's column by
month sees one bucket where the real table has twelve —
which is a fact about a column whose dates the description publishes
NOTHING about, and is why it is written here. The alternative measured
beside it was to write those cells as text, which opens in a reader and
then misses `workbook.value-class` at exit 3, describing the twin as
holding text where the description says date.

**Step 2 — the kind of format each cell wears** (`cell_format_kinds`).
A mixture is reproduced as its COUNTS and never collapsed to the
majority: the census publishes a count per kind and the twin owes a
cell per count. An ABSENT cell is always `plain`, because nothing is
written for it and every reader sees the general format there — so the
kinds that are not plain are handed out, in the order `date`,
`datetime`, `time`, `elapsed`, `text`, each by its published count,
among the cells that ARE written and not yet given a kind. **A date
format goes to a date first:** the `date` and `datetime` counts are each
offered to the cells holding a date of their own kind, then to the cells
holding a date of the other kind. Every count is then offered in three
passes in row order: a `text` format first to `text` and `empty` cells
and any other kind first to `number` and `date` cells, then to `blank`
cells, then to any cell. **A date left over keeps its own kind** where
the census held that kind's count back: a count the smallest group held
back is not a licence to write none, and a date wearing the general
format reads back as a bare day count; a published count is never
exceeded. The written cells left then take `plain` up to
the published `plain` count less the absent cells; where `plain` was
withheld, or its count is spent, each remaining cell takes the kind of
the column's published `format_code` where that kind's count was
withheld, else `plain` where plain was withheld, else the first kind in
the order `plain`, `date`, `datetime`, `time`, `elapsed`, `text` whose
count was withheld, else `plain` (plan P4-D166: twenty date cells at a
floor of eleven, their counts withheld and `plain` published as nought,
were written `plain 20`). The two orders -- the date's own kind, and
the class tiers -- were composed at the merge of the files review's
repair into the integration, which had each rewritten this step.

**Step 3 — the code each cell is written with.** The column's own
published `format_code` is used for the kind it IS; a cell of any other
kind takes the canonical code of its own kind. Every code written is
one the description may publish: Excel's built-in vocabulary, a
canonical code, or a code built of the number format language's own
tokens alone, written as the source wrote it (plan P4-D189,
`dialect.sheet_format_code_publishable`) -- never a code carrying a
quoted word, a currency or a locale.

A code's KIND is read off the code (`dialect.sheet_format_kind`), since
a code written as the source wrote it is in no closed list: `General`
and the empty code are `plain` and `@` is `text`; otherwise the first
section alone is read left to right -- a square bracket outside a
quoted run is read to its close, one never closed ending the reading,
and counts only where it holds one of `h`, `m` or `s` repeated, which
makes the code `elapsed`; the character after a backslash, an
underscore or an asterisk is skipped, inside a quoted run too; a
quotation mark opens or closes a quoted run, whose characters are not
read. Of the characters read, in either case, a `d` or `y` beside an
`h` or `s` is `datetime`; a `d` or `y`, or an `m` with no `h` or `s`,
is `date`; an `h` or `s` is `time`; anything else is `plain`.

**Step 4 — the style table.** One style per distinct code, the general
format standing first so an unstyled cell is still right, and the codes
collected in column order and then row order. The header's style is
written LAST in the table, and is the bold font with the general
format.

**Step 5 — the rows above the header.** The twin writes as many rows
above its header as `rows_above_header` names, and puts NOTHING of the
person's in them: each is one cell holding the empty string, which is
content to every reader — so the count comes back when the twin is
described again — and carries no character of anybody's table. A title
or a banner is free text somebody typed, and the disclosure rule names
it outright. A ONE-COLUMN TABLE CANNOT CARRY THEM and writes none: the
header is found as the first row reaching the table's width, so on a
table one column wide a one-cell row above the header IS the width and
would be read back as the header.

**Step 6 — the records holding nothing.** `empty_rows_inside` is a
fact about the WHOLE ROW and the column generator cannot produce one:
it fills each column's missing cells independently, so on a table of
any width no row comes out empty in every column at once. Two steps
repair that, and neither adds, removes or changes a cell:

- each column's cells are exchanged AMONG ITS OWN ROWS so that the
  cells holding nothing come to rest on the same leading rows in every
  column, as many rows as the published count asks for, capped by the
  fewest cells holding nothing any column has;
- a row is then written as a record holding nothing only where every
  column's class already holds nothing, taken in row order until the
  published count is met.

Each column keeps its exact multiset of cells, so every published fact
about that column still holds. Where fewer rows qualify than the source
had, the twin writes fewer and that is a stated limit rather than a
value quietly thrown away.

**Step 7 — the sheet the table was read from.** Its worksheet part
carries, in order: the dimension, which reaches the last row the twin
writes (the rows above, the header where one is written, the records,
and the rows of formatted blanks below) and the last column (the
table's own, and the columns of formatted blanks beyond it), each
floored at one; a frozen pane where `frozen_rows` is not nought; then
the rows —

- the rows above the header, one empty-string cell apiece;
- the header, where `source.header_source` is `file`, one shared-string
  cell per column in the header's own style — except that a column named
  `Unnamed: N`, N its place counted from nought, is written with NO
  cell, because that is the name a blank header cell is given and a
  reader names it so again (plan P4-D165) — followed by one blank cell
  for each column of formatted blanks beyond the table;
- each record: an `absent` cell is written as NO CELL AT ALL, a `blank`
  as a cell holding nothing in its style, an `empty` as the empty
  string, an `error` and a `boolean` and a `number` as their own kinds
  where the text can carry them and as shared text where it cannot, a
  `date` as an ISO date cell (`t="d"`) holding its text where the text
  is ISO text NAMING A DAY OF THE CALENDAR (plan P4-D168, narrowed by
  plan P4-D291), and anything else as shared text. A row placed as a record holding
  nothing is written with no cells at all, and so is a row every one of
  whose cells turned out to be absent;
- the rows of formatted blanks below the table, one blank cell apiece.

Then the filter, where the description publishes one and a header is
written, over the header row down to the last row; and the reference to
the defined table where the description publishes one.

**Step 8 — every other sheet.** A sheet that is not the table's is
written with AS MANY CELLS AS IT HELD, each carrying one word of
synthtwin's own, and a sheet that held nothing is written holding
nothing. It was written EMPTY once and a reader then met a different
workbook: measured with pandas, the default sheet of a book whose first
sheet is a notes page reads back as one column and no rows on the real
file and as nothing whatever on the twin. Writing the person's own text
is what the disclosure rule forbids, and cells holding the empty string
change nothing at all, because every reader folds those into a missing
value and trims the frame away again — measured, the same nothing. A
sheet holding a TABLE never reaches here: contract WB7 refuses that
description and the reader asks which sheet the table is on.

**Step 9 — the names, and which sheets are hidden.** Each sheet is
written under the name the description publishes for it, and a sheet
whose name was withheld under a neutral one — the published names
claimed first, and a placeholder walking up until it finds a number no
published name has taken, a name being TAKEN whatever its case, because
a spreadsheet holds no two sheets whose names differ in case alone
(plan P4-D171). Every sheet BEFORE the chosen one is hidden,
so the chosen sheet is the first visible one and a reader that opens
the workbook without naming a sheet lands on the table; the chosen
sheet keeps the hidden state the description publishes, and the sheets
after it stay visible. Where that would leave nothing visible at all —
a workbook no spreadsheet application can open — one sheet that is not
the table's is shown instead, and the table's own where there is no
other.

**Step 10 — the shared strings.** Every piece of text is written once
and pointed at, which is how a spreadsheet application's own save
writes it. The table is built IN THE ORDER THE SHEETS ARE WRITTEN, one
sheet at a time in workbook order, and within the chosen sheet in the
order above: the empty string first, then the header's names, then each
record's cells in row and column order. Edge spaces are preserved.

**Step 11 — how text is written inside the markup.** In element text
`&`, `<`, `>` and `"` are written `&amp;`, `&lt;`, `&gt;` and `&quot;`,
and a carriage return is written `&#13;`; in an attribute's value a line
feed is written `&#10;` and a tab `&#9;` as well. A reader turns a
literal carriage return into a line feed before any text reaches it, so
a header `line`, carriage return, `name` came back from the twin as
`line`, line feed, `name` and the twin missed its own header (plan
P4-D167).

**What a twin workbook NEVER carries**, each one a way a spreadsheet
file can act on the person who opens it: no formula, whatever a cell's
text begins with; no macro project; no external link, hyperlink or
connection; no cache of any kind; and no document author or company —
the study behind this landing measured one writer recording the
operating-system user name as the file's creator and another writing
the signed-in user's name into `lastModifiedBy`, and both name a
person. A defined table's own NAME is text somebody typed, so the twin
writes a neutral one and publishes none; what is written back is that a
table is there and that it covers the twin's own rows, because that is
what a structured reference and a query read.

## G3. The single stream: one generator, one draw shape, integer primitives

### G3.1 The generator

Exactly one random generator exists in a run:

```
generator = numpy.random.default_rng(seed)
```

`seed` is a Python integer in `0 .. 2**64 - 1`, parsed from the command
line under the grammar P2-D8 fixes (one or more ASCII decimal digits and
nothing else; leading zeros accepted; no sign, no underscores, no
whitespace, no non-ASCII digits). `default_rng` is the only name this
method uses from numpy (scanner policy E7). There is no `spawn`, no
second generator, no module-level generator, and no other source of
randomness anywhere in the run — not a hash seed, not a clock, not a set
iteration order.

### G3.2 The one draw shape

Every random quantity in this method comes from **full-width unsigned
64-bit words**, drawn in exactly this form and no other:

```
generator.integers(0, 18446744073709551615, size=count, dtype="uint64",
                   endpoint=True)
```

- `low` is the literal `0`; `high` is the literal `18446744073709551615`
  (that is `2**64 - 1`); `endpoint` is the literal `True`. So the drawn
  range is the whole of `0 .. 2**64 - 1`, inclusive at both ends.
- `size` is a first-party Python integer computed by the rules of this
  document. It is never derived from anything the caller supplies.
- `dtype` is the **string** `"uint64"`, never `numpy.uint64`: E7 permits
  no numpy attribute but `default_rng`, so the type is named by text.
- Each element is converted to a first-party Python integer by `int(...)`
  before any other use. That conversion is the point where the library
  scalar's origin ends (E8); nothing else is ever done to an element, an
  array or a scalar.

**Why this shape and no other.** The plan measured (numpy 1.24.0 and
2.5.1, seed 12345) that power-of-two, non-power-of-two and full-width
uint64 draws agree exactly today, so nothing diverges now; fixing one
shape narrows what the twin's bytes can ever depend on to a single
library operation. The claim that this makes the vectors independent of
numpy is NOT made here and was withdrawn in the plan (P2-R3-F2):
`integers` is itself the retained random operation. What first-party
post-processing removes is the additional surfaces, nothing more.

### G3.3 Calls, blocks and the word sequence

The **word sequence** of a run is the concatenation, in order, of every
word the run draws. Section G4 fixes that order exactly.

The implementation makes **one `integers` call per stage** (the stages
are named in G4) with `size` equal to that stage's exact word count, and
makes no call at all for a stage whose count is zero. That is stated as
a rule rather than left free, so no implementation detail can move a
byte.

It is nevertheless a property of this draw shape that the word sequence
does not depend on how the calls are cut: drawing `n` words in one call,
in `n` calls of one, or as `n` scalar draws yields the same words, because
the full-width range needs no rejection and no buffering. Verified on
numpy 2.5.1; the conformance battery re-checks it on every supported
numpy version, so a library change that broke it would turn a test red
rather than move a twin.

For orientation only — no reference vector depends on it — the first
four words for `--seed 0` are:

```
11749869230777074271
4976686463289251617
755828109848996024
304881062738325533
```

### G3.4 The three derived primitives, in first-party integer code

Nothing below ever forms a binary64 uniform. Every use of a word is
exact integer arithmetic on Python integers, so no rounding mode, no
extended precision and no platform difference can reach it.

**(a) The unit value.** `unit(w)` is the exact rational `w / 2**64`,
in `[0, 1)`. It is never materialized as a float: it always appears as
the pair (numerator `w`, denominator `2**64`) inside a larger exact
integer expression. Section G5.4 and G7.3 are the only users.

**(b) A bounded range.** For an integer `m >= 1`:

```
bounded(w, m) = (w * m) >> 64
```

which is the integer part of `unit(w) * m`, a value in `0 .. m - 1`.

This is the multiply-high rule, and it is chosen over a rejection loop
for one reason that matters more than its bias: **it consumes exactly
one word for every call, so the word count of a run is a fixed function
of the published facts and can be stated in advance.** A rejection loop
would make the count depend on the words themselves, and every draw
budget in this document would become unstatable.

Its cost is stated rather than hidden: the outcomes are not exactly
uniform. Of the `2**64` words, each outcome receives either
`floor(2**64 / m)` or `ceil(2**64 / m)` of them, so the largest
deviation from `1/m` is below `m / 2**64`. For every `m` this method
uses — `m` is at most a table's row count — that is below `2**-32` for
tables under four thousand million rows, which is far below any
distributional effect the twin is measured for. It is not a
cryptographic construction and is not offered as one.

**(c) An arrangement.** `permutation(n)` consumes exactly `max(n - 1, 0)`
words and produces an arrangement `a` of `0 .. n - 1`:

```
a = [0, 1, ..., n - 1]
for i = n - 1 down to 1:
    w = the next word
    j = bounded(w, i + 1)
    swap a[i] and a[j]
```

The loop runs downward, the drawn index is inclusive of `i` itself, and
the swap happens even when `j == i`. All three are stated because all
three change the bytes.

## G4. Order and count of draws

### G4.1 Column order

Columns are generated in the profile's `columns` **list order**. The
contract fixes that this is the schema order, the twin's output column
order, and the order in which the single stream is consumed (P2-D6,
P2-R5-F6). No column is generated before an earlier one, no column is
generated lazily, and no column's words are drawn out of turn. Nothing
is drawn before the first column: the first word of the run is the first
word the first column's first stage asks for.

### G4.2 Stages within a column

Every column is generated in exactly two stages, in this order:

1. **Content.** Build `content`, a list of exactly `n_present` cell
   texts, by the role's own rule (G5–G10). The order of `content` is
   fixed by that rule; it is not the output order.
2. **Placement.** Extend `content` with `n_missing` copies of the empty
   text, giving a list of exactly `n_rows` entries, then draw
   `a = permutation(n_rows)` and write

   ```
   written[t] = content[a[t]]      for t = 0 .. n_rows - 1
   ```

The absent cells are therefore placed by the same arrangement that
places everything else, which is what makes their positions
seeded-random (P2-D9) without a second mechanism and without a second
draw budget.

### G4.3 The draw budget, as a function of published content

| role | content words | placement words |
|---|---|---|
| `empty` | 0 | `max(n_rows - 1, 0)` |
| `constant`, `binary`, `categorical`, `long_tail_labels` | 0 | `max(n_rows - 1, 0)` |
| `count`, `continuous` | `S - pinned - zeroed` (G5.3) | `max(n_rows - 1, 0)` |
| `datetime` | `max(P - 2, 0)` where `P = n_present - n_unparsed` (G7) | `max(n_rows - 1, 0)` |
| `identifier` | 0 | `max(n_rows - 1, 0)` |
| `free_text` | 0 | `max(n_rows - 1, 0)` |
| `numeric_unrepresentable` | 0 | `max(n_rows - 1, 0)` |
| `time_of_day` | `max(P - 2, 0)` where `P = n_present - n_unparsed` (G7A) | `max(n_rows - 1, 0)` |
| `affixed_number` | `S - pinned - zeroed` (G5.3), read over the CORES | `max(n_rows - 1, 0)` |
| `joined_numbers` | the sum over positions of `S - pinned - zeroed` (G5.3) read over that position's numbers, PLUS `max(n_joined - 1, 0)` for every position after the first | `max(n_rows - 1, 0)` |

Where, for the numeric roles, `S` is the number of value strata
(G5.2), `pinned` is the number of strata pinned to an endpoint (2 when
`S >= 2`, 1 when `S == 1`, 0 when `S == 0`), and `zeroed` is 1 when a
zero stratum exists and is not itself one of the pinned strata, else 0.

**The two quantities the Phase 4 roles add.** On `affixed_number` the
strata are counted over the CORES and not over the written cells: the
prefix and the suffix are fixed text that costs no word, so this role's
budget is the numeric budget of the numbers inside it. On
`joined_numbers` each position is budgeted as its own numeric column,
and the budget then RESERVES a further `max(n_joined - 1, 0)` words for
every position after the first.

Those reserved words are not spent inside any position. Each position
draws exactly its own numeric budget and no more, and the reserve is
handed afterwards, once, to the walk that chooses WHICH NUMBER OF ONE
POSITION MEETS WHICH NUMBER OF THE NEXT in a row.

**"Reserved" is the exact word and "spent" would not be.** The words
are DRAWN from the stream either way -- which is what fixes the budget,
and therefore where the next column starts -- but the walk may consume
none of them: it begins from a sorted, rank-for-rank pairing, and where
that already meets the published targets it stops without looking at a
single reserved word. An implementer must draw them regardless, or
every later column moves. The reserve exists because
`_numeric_content` places its values by rule rather than by chance --
the words decide arrangement, not which numbers come out -- so two
positions built from it emerge in the same order and would pair up in
lockstep. The measured effect of leaving them paired that way: a
400-row column whose real cells held 387 different readings came out
with 117, in runs of near-neighbours, while each position's own
published distribution was right to the digit.

**AND THE PAIRING IS ASKED FOR, which makes this role the one place in
synthtwin today where structure BETWEEN two quantities is published and
reproduced.** `part_agreements` gives, for each pair of positions, how
strongly they rise and fall together BY RANK, and `part_above` gives
how often the earlier position stands above the later one. Both are
published facts of the real column, and the repair walks toward them by
swapping two rows' numbers within ONE position at a time -- which keeps
that position's multiset to the last cell, so its ladder, mean, spread,
styles and widths are all untouched and only the pairing moves. Drawn
independently and left alone, two positions of a reading agreed at
-0.02 where the real column agreed at 0.83, and a twin cell could hold
a second number above a first that no real cell ever did.

This is an exception to the one-column-wide bound stated elsewhere in
this repository, and it is a narrow one: the structure lives INSIDE a
cell, between the positions of one column, and says nothing about any
other column. `part_agreements` is APPROXIMATED against the fixed window
of G12.9 on EVERY pair. Until landing L7 the walk moved the last
position alone and a pair between two earlier positions was scored by
nothing: no window was promised for it, which is not the same as no
obligation, and it could come out at `+1` against a published `-1` --
a plain MISS named as such by both reports (residual R-P4-51, review
item P4-G3-R6-F7). The walk now moves every position but the first, so
every pair is aimed at and every pair takes the window; a pair that
lands outside it is still a MISS, named by both reports with the
achieved value beside the published one. Measured on a 400-row
two-position column published at 0.9613, the twin reached 0.8994 while
`part_above` came out exact. BOTH reports name these facts and measure
them (R-P4-42 and R-P4-44, closed 2026-08-27). The count of
different CELLS is a separate fact a pairing of these numbers may be
unable to meet, and the twin's report DOES say so (residual R-P4-40).


**Everything else is placed by fixed rule and costs no word** (P2-D8):
the endpoints of a numeric or datetime column, the zeros, the class
stand-ins, every invented identifier, every invented text, every label
and every label variant. Where this document says a value is pinned,
that means no word is drawn for it — never that a word is drawn and
discarded.

**The consequence D12 already carries** is restated here so nobody is
surprised by it: a schema change, or any change to this method that
alters a column's word count, shifts every later column at the same
seed. Regeneration after a method change is a changelogged event.

## G5. Numeric columns (`count`, `continuous`)

### G5.1 What the profile supplies, and what each fact obliges

Published: the 11-rung `percentiles` ladder; `n_zero`; `n_negative`;
`n_negative_unrepresentable`; `integer_valued`; `n_used_in_statistics`;
`n_left_out_of_statistics`; `numeric_share`; `mean`, `std`, `skew`,
`std_unrepresentable`; the universal class counts `n_numeric`,
`n_out_of_range`, `n_contradictory`, `n_not_numeric`; `n_distinct` and
`n_distinct_folded`; and (owner decision 10) `numeric_styles` with its
withheld remainder, TOGETHER WITH ITS TWO SIBLING CENSUSES:
`fraction_widths`, how many `decimal`-styled cells wrote each number of
figures after the point (plan P4-D4.5), and `pad_widths`, how many
`leading_zero`-styled cells wrote each FIELD WIDTH (plan P4-D14). Both
are floor-governed with a `(withheld)` remainder, both are read over
the CORES on `affixed_number`, and both were absent from this list
while the profile published them -- an omission that left an
independent implementer writing a column the shipped tool would not
write, which is the one thing this document exists to prevent.

Fixed quantities used throughout:

```
K = n_numeric                     cells that parse as ordinary numbers
O = n_out_of_range                cells that are numbers out of range
C = n_contradictory               cells with self-contradicting notation
N = n_not_numeric                 cells that are ordinary text
K + O + C + N = n_present         (contract invariant)

G = n_negative - n_negative_unrepresentable    negatives among the K
Z = n_zero                                     zeros among the K
P = K - G - Z                                  positives among the K
```

`P < 0` is a jointly infeasible document and is a generation refusal
(G12). The ladder rungs are named `L[0] .. L[10]` for
`min, p01, p05, p10, p25, p50, p75, p90, p95, p99, max`, with
probabilities in hundredths

```
PCT = (0, 1, 5, 10, 25, 50, 75, 90, 95, 99, 100)
```

held as integers, never as decimal fractions, for the same reason the
profiler holds them that way: `0.99` has no exact binary spelling and
the nearest one moves a rung onto the wrong pair of neighbours in a
large column. The contract requires the ladder to be non-decreasing, so
a descending pair is a loader refusal and not something this method
repairs.

**A null rung is NOT a refusal, and this is the rule for one**
(P2-C1-F8). Revision 1 of this document said the contract required every
rung to be a finite number and that a null rung was a loader refusal.
The contract says the opposite in its rule L3 — a rung may be null, it
carries no obligation of its own, and a loader accepts it rather than
refusing a document over a case it cannot rule out — and the shipped
loader accepts one. A method that expects a refusal that never comes
leaves the generator to decide the rule for itself, which is what
happened. The rule is fixed here:

- **The filled ladder.** Before anything in G5.2 or G5.3 reads a rung,
  every null rung takes the value of the NEAREST rung BELOW it that
  holds a number; where no rung below it holds one, it takes the FIRST
  rung of the ladder that holds a number. The filled ladder is what
  every later rule reads, and it is still non-decreasing, because each
  filled rung repeats a number already standing at or before its own
  place.
- **A ladder that holds no number anywhere** has no filled form. The
  column's values are then placed on the sign counts alone (G5.5), no
  ladder-derived bound is measured for it, and the empty ladder is named
  in the report on every run (G12.3).
- **A filled rung owes nothing.** `min` and `max` are EXACT-OBSERVABLE
  only where they hold a number; where either was null the report names
  it as a published fact the description did not carry, rather than as
  an endpoint the twin missed.

No producible profile is known to reach any of this — every interpolated
rung lies between two finite neighbours — but "not known to be
reachable" is not a rule, and the loader accepts the document, so the
method states what happens rather than leaving two implementations to
answer differently.

### G5.1a The tail block (stage 3, plans P4-D322 to P4-D327 and P4-D344)

A numeric block that carries the key `tails` is a TAIL BLOCK (contract
6.7, invariants TL1 to TL6); one without it was written before stage 3
and every clause of G5 reads it exactly as before, so no description
already written moves. On a tail block every rung outside the two
boundary percents `P_lo = tails.low.percent` and
`P_hi = tails.high.percent` is null by rule, except an end the
description publishes because at least `max(small_cell_floor, 3)` rows
held it (a HEAPED end). **G5.1's fill applies inside `[P_lo, P_hi]`
only**; outside it the ladder is each tail's own reading, G5.3b or, for a
listed tail, G5.3e. `L[0]` and `L[100]` of the ladder every later rule
reads are the two DERIVED ENDS of G5.3b, and the pinned strata of G5.3
hold them exactly as they held `min` and `max`, so the draw schedule of
G3 and G4 does not move.

**Every consumer reads that one ladder**: G5.2a's rank values and
G5.2b's shares, G5.2a's cap, G5.3's values, G5.6's windows and the snap
bounds that read them, G6.7's scale, and both reports' windows. It is
built once from the published facts, by the rules below, and written
once in the shipped code (`contract.tail_ladder`), where the generator
and the validator both read it.

A tail block whose `tails` is null publishes no rung and no moment (the
block floor, TL2), and its ladder is G5.3d's ramp; one whose two sides
are null publishes the moments alone (TL3), and its ladder is G5.3c's.

### G5.2 Strata: how many different values, and how the cells divide

The K numeric cells are divided into **strata**. One stratum holds one
value; a stratum of size `g` puts that one value in `g` cells. Strata
exist because raw distinctness is a published fact and a numeric column
may hold far fewer different values than cells.

Let `F_num` be the folded-spelling budget this column's numbers may use
(G6.5 computes it; where the column has no other class of cell it is
just `n_distinct_folded`). Then

```
M = min(K, F_num)          the number of different VALUES
```

`M` is the largest value count the distinctness facts allow, and largest
is deliberate: every value the ladder is allowed to distinguish is a
value the twin keeps.

**A GRAIN INSIDE A ROLE TAKES ITS OWN COUNT, AND THIS SECTION SAID
NOTHING ABOUT IT UNTIL LANDING L7** (residual R-P4-112). One position
of a joined column (G6B.2) and the cores of an affixed one (G6A.2) are
handed to G5 and G6 as columns in their own right, and the universal
counts they arrive with answer for the CELLS AROUND them. A 36-row
column of `N/M` publishes 36 different cells while its first position
holds 11 different numbers, so that position was divided into 36
strata where a plain column carrying the same numeric facts gets 11 —
and a stratum holds a VALUE, not a cell. So for such a grain, and only
for such a grain,

```
F_num = n_distinct_values of the grain's own quantitative block
```

**for the division here AND FOR NOTHING ELSE.** The spelling budgets of
G6.5 keep the counts the block arrives with, which are the counts of
whole CELLS.

**AND THIS SENTENCE SAID THE OPPOSITE FOR ONE REVISION.** A count of
NUMBERS is not a count of spellings, and a spelling budget is precisely
what buys the SECOND way of writing one number: an affixed cell's
spelling is its core's spelling with fixed text around it, so the
cells' count IS the cores' count, and a joined position's variants are
the cell's spellings just as much. Measured on 300 cells holding sixty
values, each written plainly and again with a leading zero — 120
different spellings over 60 different numbers — at forty seeds through
the real path: with the budget at the grain's 60 the twin held 55 to 60
of the 120 published spellings, and with it on the cells' 120 it holds
81 to 97. On the joined role, where both counts are exactly observable,
the shortfall is a reported MISS at forty seeds of forty either way.
An affixed core has no pairing stage that could recover the variants at
all.

A plain numeric column is unaffected: there the count on the block IS
the column's own, and `n_distinct_folded` divides it exactly as it
always has.

The strata are laid out in one fixed order — **negatives ascending, then
the zero stratum, then positives ascending** — because that is the
sorted order of the column's own values, and the ladder is a statement
about sorted order.

```
M_zero = 1 if Z > 0 else 0
M_rest = min(M - M_zero, G + P)           (refuse if M - M_zero < 0)
```

**A stratum with no cell in it is not a value** (P2-C1-F5). Only the
negatives and the positives are divided into strata, so at most `G + P`
of them can hold a cell, and `M_rest` is capped at that. Without the cap
a column of nothing but zeros whose published spelling count is large --
which owner decision 8's leading-zero family makes ordinary, since one
value has as many spellings as a description asks for -- built one
empty stratum per spelling. Each of those still took an end of the
ladder in G5.3 and still had its sign repaired in G5.5, so the run named
an endpoint deviation about a value the twin never wrote. A published
count of different SPELLINGS is not a count of different VALUES: G6.5 is
where the spellings come from.

If `G > 0` and `P > 0`:

```
M_neg  = the integer nearest to M_rest * G / (G + P), ties upward,
         computed exactly in integers as
         M_neg = (2 * M_rest * G + (G + P)) // (2 * (G + P))
then clamp M_neg into [1, M_rest - 1]
M_pos  = M_rest - M_neg
```

If `G == 0`, `M_neg = 0` and `M_pos = M_rest`. If `P == 0`, `M_pos = 0`
and `M_neg = M_rest`. A clamp that cannot be satisfied (`M_rest < 2`
with both `G > 0` and `P > 0`) means fewer different values are
permitted than the sign facts require; the sign facts win (P2-D6
feasibility rule 4), `M` is raised to the smallest value that satisfies
them, and the report names the raised distinct count beside the
published one.

#### G5.2a How a band's cells divide between its strata

The zero stratum, when it exists, has size `Z`. Each of the other two
bands divides its own cells among its own strata by the rule below.
Write `C` for the band's cell count (`G` for the negatives, `P` for the
positives), `M` for its stratum count (`M_neg` or `M_pos`), and `lo`
for the rank its first cell stands at in the sorted column — `0` for
the negatives and `G + Z` for the positives.

**THE EVEN SPLIT IS THE FALLBACK AND NO LONGER THE RULE.** Where there
is no ladder, or where `M >= C`, the cells divide evenly:

```
size of stratum i = floor((i + 1) * C / M) - floor(i * C / M)
```

for `i = 0 .. M - 1`. That is what this clause said for every column
until 2026-08-28, and residual R-P4-49 is what it cost: an even split
gives every value the same number of cells, so a column of 230 cells
holding 27 numbers — five of them about forty cells each, the other
twenty-two about one — became 27 strata of eight or nine, a shape that
can represent neither. The ladder decides WHICH values a twin holds and
the split decides HOW MANY CELLS each of them gets, and no ladder,
however fine, can repair the second.

**OTHERWISE THE SIZES FOLLOW THE LADDER'S OWN SHAPE**, which is what
the hundred-and-one-rung ladder of G5.1 knows and the eleven named
rungs do not: a value standing at seventeen of the rungs stands at
seventeen per cent of the column, because the rungs stand at the
percentiles.

**THE ORDER OF THE WHOLE LAYOUT, stated once so it cannot be read
three ways.** The steps run: (1) read the ladder at every rank of both
bands and take their runs, which is steps 1 and 2 below; (2) the band
share of G5.2b, which turns those run counts into `M_neg` and `M_pos`;
(3) the carrier band step of G5.2, which may move one stratum from one
band to the other; (4) steps 3 and 4 below, which join or divide each
band's runs to its final `M` and take the sizes; (5) the carrier cell
step; (6) the reach step. Steps 1 and 2 are computed ONCE, before the
band share, and are not re-taken when step 3 moves a stratum — only
step 4 is redone, against the moved counts.

**1. Read the ladder at every rank of the band.** THE LADDER IS THE
HUNDRED-AND-ONE-RUNG ONE that G5.3 merges from `percentiles` and
`percentiles_between`, and every other reader of a ladder in this
section reads the same one. For `i = 0 .. C - 1`,

```
v[i] = Interpolate(Ladder, (lo + i) * 2**64, K * 2**64)
```

by the convex form of G5.3 — its segment rule, its four floating-point
operations and its clamp — with the integer rule of G5.4 applied
afterwards where `integer_valued` is published true. `K` is the
column's numeric cell count and `2**64` is the scale G5.3 itself uses,
so nothing rounds here that does not round there. G5.5's sign repair is
NOT applied: the operations named here are the whole of it.

**1a. The band's own sign** (plan P4-D327). With the values `v[i]` of
step 1 read for one band: in the POSITIVE band every value that is not
above nought is replaced by the FIRST value of the band that is above
nought; in the NEGATIVE band every value that is not below nought is
replaced by the LAST value of the band that is below nought. A band none
of whose ranks reads a value of its own sign keeps what it read, and
G5.5 answers for it. Both steps 2 to 4 and G5.2b's run counts read the
replaced values.

Why. The positive band starts at rank `G + Z`, where the zero stratum
ends, and the ladder does not know that: it crosses from the last rung
reading nought to the first reading one by a straight line, so the
first ranks of the band read a fraction under a half, the integer rule
takes them to nought, and the band opens with a run of noughts. G5.5
then repairs that run to one, BESIDE the real plateau of one, two strata
hold one number, G6.5a's separation moves the larger up to two, and
every stratum above it moves up in turn. **Measured** on 2,000 counts
drawn `int(expovariate(0.2))` beside a constant column (seed 7, twin
seed 4): the twin wrote the value one in 4 cells against the table's
317, two in 320 against 236, and its mean was 19.3 per cent high at
floors 1 and 11, with nothing missed; with this step, one in 324 cells
and the mean 1.3 per cent above the table's. The frozen case `mode_held`
moved with it (G14.3). **NO FROZEN CASE WAS ADDED FOR THIS STEP**, which
is recorded here rather than left to be noticed: what pins it is the
round trip
`tests/test_stage3_tail_rule.py::test_a_count_column_beside_a_zero_heap_keeps_its_ones`,
which withdraws the step and reads the two counts and the mean above off
the twin. That is a gap in G14.3's own terms and it is named as one.

**AND ON A COLUMN WRITTEN AT ONE FRACTION WIDTH, THE NUMBER THE WRITER
WOULD WRITE THERE** (landing 2b.1, 2026-09-15). Where `integer_valued`
is false and the column is on a WRITTEN GRID of `f > 0` figures, `v[i]`
is replaced by the number its GRID TEXT reads back as: the text G6.6's
writer gives `v[i]` at `f` figures. A run is then a run of one WRITTEN
number, and `GridValue(x)` below names this reading. A column is on a
written grid of `f` figures where `fraction_widths` names the one width
`f` and either that width covers every numeric cell — G6.5a's WHICH GRID
clause — or its count and the NAMED point-free style counts (`plain`,
`leading_zero` and `leading_plus`, the `(withheld)` share EXCLUDED) add
up to every numeric cell (landing 2b.1, repair, 2026-09-16; the
withheld share excluded by landing 2b.7, 2026-09-15). That pool is not
read here even though G6.4 WRITES it in the plain style: a pooled count
says how many cells it covered and never which form they took, so it
cannot prove its cells carry no point. Counting it proved a grid that
does not exist — 490 cells at one decimal place beside ten `-1e-2`
cells publish the width `1` for 490 and pool the other ten, and 490 + 10
read as full coverage of the grid of tenths, which `-0.01` is not on.
Its twin held 28 different numbers against a published 31 at seeds 1, 7
and 23, and holds 30 with the pool excluded.

**A census naming SEVERAL widths is on the grid of its commonest one**
(repair of the stage-2b integration). Where `fraction_widths` names two
widths or more, none of them pooled, every named width is positive, and
the named widths and the NAMED point-free style counts together cover
every numeric cell, the column is on the written grid of the width the
most cells are written at, ties going to the wider. A census that pools
a width is read as no grid: the pool may hold a width finer than the
commonest, and snapping it moved a published minimum of 2.11. A
narrower width is a grid value whose last figures are zero and a wider
one is a grid value written with zeros after it, so every cell the
census counts can be written from a value on that grid. Such a column
used to be read as on no grid: 400 one-place readings with one cell
written `4.20` published `{1: 399, 2: 1}` at a floor of one, and the twin wrote
`5.020207149207973` six times and held 26 different numbers against 27,
exit 3 at every floor; money written by the shortest round trip
(`{1: 213, 2: 1787}`) missed both widths and the count of different
numbers. On 96 twins of six multi-width shapes, twins exiting 3 went
from 72 to 44, and none that passed before missed after.

**AND A NARROWER WIDTH HAS THE VALUES IT NEEDS** (plan P4-D179). Where
`fraction_widths` names two widths or more, none pooled, and the named
widths and named point-free counts cover every numeric cell, then after
G6.7, for each named width `w` but the largest, in ascending order, with
`u` the next named width up and `b` the next one down (or none): let the
TARGET be the named point-free count plus every named count at a width
of `w` or less, and HELD the cells of every stratum whose value needs
`w` figures or fewer after the point. Where held is below the target,
and only then — a surplus is written at a wider width with zeros after
it, as a column of tenths writing `55.40` beside `55.4` does — the
shortfall is closed in two steps. First, NEIGHBOURING strata `i` and
`i + 1` exchange values, where neither is pinned, in the zero band,
whole, or holding the `mode`, both are in one sign band, and one needs
more than `b` and at most `w` figures while the other needs more than
`w` and at most `u`; the exchange adds the difference of their sizes,
and pairs are chosen disjoint so their gains add to the shortfall
exactly — by reachable sums over the pairs in stratum order, the pair
at the latest place completing a sum, where strata times shortfall is at
most 400,000, and otherwise the largest gain that still fits first,
walked from the bottom. Second, what remains is closed by MOVES over
the strata in ascending order of value, never two neighbours in value:
a stratum needing more than `w` and at most `u` figures, not pinned, not
in the zero band, not holding the `mode`, not whole, not sharing its
number, and not already exchanged or moved, takes the nearest number of
the grid of `w` figures — walked outward one unit, the lower first, at
most 64 units — that needs more than `b` and at most `w` figures, lies
strictly between the next smaller and the next larger number any
stratum holds, has no point-free spelling, keeps the sign, and stands in
the same histogram bin; moves are chosen by the same sum rule over their
sizes. MEASURED before this clause: 2,000 two-place readings written by
the shortest round trip (`1.1` beside `1.23`) held 168 to 178 one-place
cells against a published 182 at every seed, in a CSV and in a
workbook; on a battery of six shortest-round-trip shapes at two floors
and four seeds the twins exiting 3 went from 19 of 48 to none.

**THE WIDTH A CELL IS WRITTEN AT, three rules the shortfall rule needs**
(plan P4-D179). A pinned value takes the width its own value needs where
the census names that width and it holds the value's cells, and
otherwise the largest still-unfilled width it fits, as before; a value
that already fits a width is written at it without its stretch being
asked, since nothing is snapped; and a value whose own width is a named
one is never snapped to a width at which it reads as a number another
value holds or a snap has already written -- where its own width is not
named, refusing the snap would write the cell at that width, a number no
source wrote at a width the census does not have, so the snap is taken.
The second is how a spreadsheet writes tenths, `37` beside `37.4`, and
how a zero-inflated column writes `0` beside `2.5`: a point-free cell is
the grid point whose last `f` figures are zero, so every number of such
a column is a point of the grid. Read as no grid, its strata did not
line up with the numbers: at 53bb012 a 2,000-row column of weights
written this way held 238 cells at full binary precision and 51 leading
zeros, and a 4,000-row column of temperatures held one number 601 times
against a `mode_count` of 308. On 96 twins of eight such shapes at 500
to 4,000 rows the count of twins checked with nothing missed went from 4
to 70, of cells at full precision from 6,971 to 21, and of leading zeros
from 736 to 16.

Without it a ladder read at every rank gives nearly every rank a value
of its own on a column whose values move continuously, the join of
step 3 has only one-rank transitions to work with, and the strata it
builds bear no relation to the numbers the column is written as. G6.6's
snap then refuses every stratum narrower than half a grid unit and the
cell is written at full binary precision. Measured on 2,000 cells of a
one-figure column publishing 517 different numbers: 227 cells written
like `55.44657068472738`, 38 leading-zero spellings such as `053.6`
bought to make up the spelling count, and 479 numbers held; with this
reading and G5.3's grid value, none, none and 517, at every seed tried.

**2. Take the runs.** A RUN is a maximal block of consecutive ranks
whose values are equal, compared as binary64 numbers. Write the runs in
rank order as lengths `L[0..R-1]` and values `H[0..R-1]`. A run is a
PLATEAU of the ladder: the cells that hold one value.

**3. Make the run count equal `M`.** Interpolating a ladder over a
column's ranks puts a one-rank TRANSITION between each pair of real
plateaus — a value the column does not hold, standing between two it
does — so `R` is usually larger than `M` and never exactly it by
accident.

While `R > M`, join one adjacent pair `(j, j+1)` into a single run of
length `L[j] + L[j+1]` keeping the value `H[j]`. The pair is chosen by
the SMALLEST of this key, and the leftmost pair wins a tie:

```
( Over(j),  min(L[j], L[j+1]),  0 if Whole(H[j]) == Whole(H[j+1]) else 1,  Gap(j) )

Over(j) = max(0, L[j] + L[j+1] - Cap_band)     and 0 wherever Cap is 0

span   = |H[j]| + |H[j+1]|
Gap(j) = 0                              where span is 0
       = | H[j+1]/span - H[j]/span |    where span is finite

                                        and where span is NOT finite,
scale  = max(|H[j]|, |H[j+1]|)          scale is finite and non-zero
a      = H[j]/scale,  b = H[j+1]/scale  whenever span is not, so
Gap(j) = | b/(|a|+|b|) - a/(|a|+|b|) |  this branch always answers
```

in binary64, and **DIVIDED BEFORE IT IS SUBTRACTED, which is the whole
of the guard.** Taking `|H[j+1] - H[j]|` first overflows to an infinity
where the two rungs sit at opposite ends of the representable range —
the same hazard G5.3 spends two paragraphs on — and `inf / inf` is a
NaN, which makes every comparison against it false and hands the choice
to iteration order instead of to the key.

**AND THE SECOND BRANCH IS WHY THE FIRST IS NOT ENOUGH** (review item
P4-G6-R1-F1). Dividing first moves the overflow out of the numerator
and into `span`, where it is still an overflow: two LARGE rungs of the
SAME sign make `|H[j]| + |H[j+1]|` an infinity, both quotients zero,
every `Gap` tied at zero, and the leftmost pair wins a comparison it
should have lost. On the three cells `1e308`, `1.1e308`, `1.1e308` the
true gaps are about 0.032 and 0.015, so the right pair is the nearer
one and the left pair was taken. A column of very large numbers is not
an exotic case. Scaling both rungs by the LARGER MAGNITUDE first cannot
overflow, because that divisor is one of the two numbers themselves.

The two branches compute one quantity in real arithmetic and not one
binary64: over 400000 random pairs whose `span` was finite they agree
on 97.8 per cent and part by one unit in the last place on the rest,
which would move the choice on about 7 merges in every 10000 — always
between two gaps already equal to within representation. So the second
branch is taken ONLY where the first has no answer at all, and every
column the first form could represent keeps exactly the bytes it had. `Whole(x)` is true
where `x` is a whole number, by the test of G5.4. The key is recomputed
after every join, not once for the whole walk.

**THE CAP, AND WHY THE KEY BEGINS WITH IT** (landing 2b.1,
2026-09-15). No stratum may hold more cells than one number of the real
column held. Write

```
Cap      = mode_count                              where the mode pair is published
         = min(K - n_distinct_values + 1,
               floor((r + 1) * (K - 1) / 100) + 2,
               F - 1)                              where it is withheld
Cap_band = max(Cap, ceil(C / M))                   where Cap > 0
```

where `r` is the length of the longest run of equal rungs in the
hundred-and-one-rung ladder, filled by G5.1's rule. Both halves of the
second line are bounds the description proves. Every other number holds
a cell, so one number holds at most `K - n_distinct_values + 1` — one
exactly where every number is different. And the ladder proves the
other: a number held by `c` cells stands at sorted positions
`a .. a + c - 1`, and every rung whose type-7 position `(K - 1) p`
falls in `[a, a + c - 2]` reads exactly that number, which is at least
`floor((c - 2) * 100 / (K - 1))` rungs, so no run of equal rungs can be
shorter than that. `ceil(C / M)` stands in only where a band has too few
strata to fit its cells under the cap at all.

`F` is the description's `small_cell_floor`, and its term stands only
where `F >= 3` and the description does not itself prove a number held
by `F` cells or more — `ceil(K / n_distinct_values)` does not reach `F`;
everywhere else the term is absent (landing 2b.1, repair, 2026-09-16;
narrowed by landing 2b.7, 2026-09-15). The profiler withholds the
pair exactly where the commonest number is held by fewer than `F` cells
or by one, so under a floor of 3 or more the pair's absence proves no
number was held by more than `F - 1`; under a lower floor it proves only
that every number is different, which the first term already says. The
ONE exception is a description that contradicts that reading: every
number of a column holds at least `ceil(K / n_distinct_values)` cells
on average, so a withheld pair under the floor was not withheld by it
there.

**A RUN OF EQUAL RUNGS IS NOT THE SECOND EXCEPTION, AND WAS** (landing
2b.7, 2026-09-15, withdrawing the `floor((r - 1) * (K - 1) / 100)` term
of the clause above). The argument for it was that the rungs at the two
ends of a run of `r` equal rungs stand `(K - 1)(r - 1) / 100` type-7
positions apart with every sorted position between them reading that
number — which is true of the ladder and false of the column, because
RUNGS ARE COMPARED AS BINARY64. Equal rungs prove that many equal
ROUNDED values and say nothing about how often one exact value was held.
A hundred exact decimals `1.0000000000000001` upward at four cells each
is the column that separates the two: every number is different, none is
held more than four times, the profiler withholds the mode pair because
four is under a floor of 11 — and 101 rungs carry 46 different binary64
values with a longest equal run of 4, so the withdrawn term read
`floor(3 * 399 / 100) = 11` and stood the floor aside. All three
writings then capped a stratum at 21 where the withheld pair proves 10.
The count term is unaffected: it reads `ceil(400 / 100) = 4`, which does
not reach the floor, so the floor binds. One frozen case moves with this
withdrawal and only one — `numeric_point_free_styles`, whose 33 cells
are all the number 5 and whose hand-written description withholds its
mode pair while its own flat ladder said a number was held 33 times. Without the
term, 4,000 amounts described under `--smallest-group 11` came back
holding one number 45 times and 2,500 thousandths 27 times, where the
withheld pair proved no real number was held more than 10 times, and
the twin described again at that floor published a mode pair the real
column had withheld; with it, 30 twins of five such shapes at 1,000 to
4,000 rows held none more than 10 times.

**G5.2a-2. THE FLOOR TERM STANDS ONLY WHERE THE HEAP READING IS
CLOSED** (stage 3 landing 3.5, 2026-09-22; profile contract Q18). The
profiler withholds the mode pair on TWO grounds since that landing. The
first is the one above: the commonest number is held by fewer than `F`
cells, or by one. The second is that its count leaves a GROUP below the
line on the other side -- `census_nameable([mode_count],
[n_used_in_statistics])` fails because `K - mode_count` is between one
and `L - 1`, with `L` the census line, the larger of two and `F`. A
heap is exactly that shape: 395 zeros among 400 numbers published
`mode_count: 395` beside `n_used_in_statistics: 400`, and the five
cells that are not the heap are a group no key of the block would be
allowed to name.

So a withheld pair proves "fewer than `F` cells" only where the rest of
the description already rules the heap out, and it rules it out exactly
when the other terms put the cap at or below `K - L`:

```
Cap = min(K - n_distinct_values + 1,
          floor((r + 1) * (K - 1) / 100) + 2)     where the pair is withheld
    = min(Cap, F - 1)   only where F >= 3, ceil(K / n_distinct_values) < F
                        AND Cap <= K - L
```

Nought still means no bound, and a `Cap` of nought is not lowered to
`F - 1` either: nothing else bounds the column, so nothing rules the
heap out. Without this clause the generator would cap a heap column's
widest stratum at `F - 1` and write a column that is not a heap,
because the very fact that withheld the pair is the fact the old
reading took for its opposite. The validator's own reading of a
withheld pair is the same clause, written from it (validation method
V6.2's stratum window).

The three parts that follow `Over` never stop a run growing: a run
beside a one-rank transition always has a smaller side of one, so on a
ladder that moves continuously the same run takes neighbour after
neighbour. Measured on 4,000 cells of a two-figure lognormal column
publishing a `mode_count` of 62: strata of 760, 720 and 240 cells, one
number written 760 times, and `p25` recomputed at 0.64 against a
published 0.79 — while the twin's own report said every rung was inside
its window, because that window is drawn from the same inflated
stratum (G5.6). With `Over` first the join takes every pair that stays
under the cap before any that does not, and where every pair overshoots
it takes the one that overshoots least.

`Whole(x)` is true where `x` is a whole number. **The three parts after
`Over` earn their place, and each was measured against a witness that
the other two get wrong:**

- **the smaller side smallest** — absorb the least. A transition is one
  rank wide and a plateau is many, so this takes the artifact into the
  real value beside it and never the reverse. Choosing instead the pair
  of fewest cells joins two transitions, which are two different values
  and neither spurious, and loses a value the column holds.
- **both whole or both fractional next** — which cells can be written
  without a point is `numeric_styles`, an EXACT-OBSERVABLE fact, and a
  whole value's nearest neighbour is very often the fraction just below
  it: `4` and `3.875` are closer than `4` and `5`. Choosing by distance
  alone walked a column's whole-number plateaus into fractional ones
  and left a published `plain` count of 38 written as 28.
- **nearest in value last**, measured RELATIVELY against the pair's own
  size, so a column of thousands and a column of thousandths are judged
  the same way.

While `R < M`, divide the longest run in two — leftmost on a tie — into
lengths `floor(L/2)` and `L - floor(L/2)`, both keeping its value. The
two strata then hold the same value, and the leading-zero family of
G6.5 is what gives the second of them a spelling of its own.

**Then no run stands above the cap.** Visit the runs in rank order;
while one holds more than `Cap_band` cells, the NEAREST other run still
under it — the lower where two are equally near — takes as many of its
cells as it has room for and the overflow still owes. Cells move by
moving the boundaries between strata, so no band's total, no stratum
count and no rank order changes. A run of step 2 can stand above the
cap on its own, because interpolation rounds a plateau's edges onto it:
345 cells of a five-point score against a published `mode_count` of
333. Nothing moves where `Cap` is 0, or where the band's strata could
not hold it under `Cap_band`.

The carrier and reach steps of G5.2b run after this and may move cells
past the cap: `numeric_styles` is EXACT-OBSERVABLE and `mode_count` is
REPORT-ONLY, so by plan P2-D6's feasibility rule 4 the published style
count wins, exactly as it wins over the even split. That is the one
exception G5.6 names to the promise its window rests on.

**4. The sizes are the run lengths**, in rank order. Each is at least
one and they sum to `C`, because every run is at least one rank long
and the joins and divisions above preserve the total.

A stratum whose SHARE `[c/K, (c+g)/K]` lies inside one plateau takes
that plateau's value for every word, because both rungs of every
segment its share meets hold that value and G5.3's clamp returns it
exactly. That is what makes a repeated value's count exact rather than
approximate.

**THE SHARE AND NOT THE RANK RANGE, and this clause said the rank range
until 2026-08-28.** A stratum's share runs one rank PAST its last cell,
so a stratum whose every rank sits inside a plateau can still draw from
the segment above it: measured, a ladder flat at `7.0` over ranks 10 to
20 with the next rung at `20.0`, a stratum at `c = 10, g = 11`, and the
word `2**64 - 1` gives **19.999999999999996** and not `7.0`. The reach
step of G5.2b already states the criterion correctly — "a stratum whose
share does not move at all" — so the two were adjacent and disagreed.

#### G5.2b How many strata each band gets

`M_neg` and `M_pos` are fixed in G5.2 above, and the share between them
follows the ladder rather than the cells wherever there is one. Where
`G > 0` and `P > 0`, write `A_neg` and `A_pos` for the number of RUNS
step 2 above finds in each band — how many different values the ladder
gives that band — and replace the cell counts in G5.2's formula with
them:

```
M_neg = (2 * M_rest * A_neg + (A_neg + A_pos)) // (2 * (A_neg + A_pos))
then clamp M_neg into [ max(1, M_rest - P),  min(G, M_rest - 1) ]
then, where Cap > 0 and N_neg + N_pos <= M_rest,
     clamp M_neg into [ N_neg,  M_rest - N_pos ]
     with N_neg = ceil(G / Cap) and N_pos = ceil(P / Cap)
```

falling back to `G` and `P` where there is no ladder or where
`A_neg + A_pos` is zero. `Cap` is G5.2a's.

**AND THE CAP DECIDES EACH BAND'S FLOOR** (landing 2b.1, part 2,
2026-09-15). Every number of a band holds at most `Cap` cells, so a band
of `G` cells holds at least `ceil(G / Cap)` different numbers, and a band
handed fewer strata than that holds more cells in one of them than any
number of the real column held — which G5.2a's levelling cannot repair,
because a band's strata cannot hold its cells under a cap they are too
few for. The rounded share of runs does exactly that on a short column:
twelve whole numbers, seven cells of `-29` and one of `-28` beside a
zero and three positive cells, publish a `mode_count` of 7, and the
share gave the negatives ONE stratum, which then held eight cells. The
floor gives them two. `N_neg + N_pos <= M_rest` holds whenever `M_rest`
is at least the column's count of different non-zero numbers, since the
real bands hold at least `N_neg` and `N_pos` of them; where a budget
leaves `M_rest` below that, the floor is not applied. With it, no band's
even share rises above `Cap`, so `Cap_band` is `Cap` itself and no
stratum holds more than `Cap` cells wherever the carrier and reach steps
below move none — the promise G5.6's window is drawn from. Measured over
4,500 randomised columns of mixed signs and very uneven counts, whole
and one- and two-figure, at floors of 1, 5 and 11, that the carrier and
reach steps do not touch: every layout at or under `Cap`, where one of
the 1,500 of the first search had not been.

**THE LADDER DECIDES THE SHARE AND THE CELLS DECIDE THE CEILING**, and
the clamp above says so because the formula alone does not. G5.2's
cell-ratio version could never ask a band for more strata than it has
cells: `M_rest <= G + P` makes `M_rest * G / (G + P) <= G` an identity,
so the bound came free. A RUN count has nothing to do with a cell
count, and the bound does not. Measured before the clamp was added: a
102-cell column with two negative cells over two plateaus and a hundred
positive cells over four asked SEVENTEEN strata of the two-cell band,
and the sizes came back as fifteen strata of no cells — which G5.2
forbids by name, because a stratum with no cell in it is not a value
(P2-C1-F5), and each of those would still take an end of the ladder in
G5.3 and still have its sign repaired in G5.5.

**CELLS ARE THE WRONG THING TO FOLLOW HERE, and this clause followed
them until 2026-08-28.** Two bands holding the same number of cells
need not hold the same number of values, and a stratum count is about
values. Measured on one column: thirteen negative cells holding TWO
values, forty-eight positive cells holding five, and seven strata
between them — the cell share gave the negatives one, so ten cells of
`-30` and three of `-55.5` collapsed into a single value and took ten
of the eighteen point-free cells the style map publishes with them.
Following the ladder gives the negatives two, which is what the column
holds.

**The carrier step: the cells a published point-free count needs**
(P2-C4-F3). Three of the six styles of G6.1 — `plain`, `leading_zero`
and `leading_plus` — can be worn only by a cell whose value has a
point-free spelling (G6.2), so how many such cells a column HAS is
settled here, by the split, before any style is chosen. Let

```
W      = plain + leading_zero + leading_plus in the published
         `numeric_styles` map, with the `(withheld)` remainder added
         to `plain` (G6.4), capped at K
W_plus = the published `leading_plus` count, capped at Z + P
```

A stratum **can carry** a point-free value exactly when it is the zero
stratum, whose value is exactly `0`; or a pinned end whose published
rung has a point-free spelling; or any other stratum, because the
values step of G6.4 may take it to a whole number.

Write `Room(reachable)` for the most cells the strata that can carry
could ever cover inside a set of sign bands: a band with no stratum
that can carry offers nothing, because cells never cross a sign band,
and a band that has one offers every cell it holds except the one each
of its other strata must keep. `Room` is taken over every band for `W`,
and over the zero and positive bands alone for `W_plus`.

**The band step, taken first.** How the different values divide between
the negative and the positive side is no more published than how many
cells each holds. A band left with ONE stratum, where that stratum is a
pinned end whose rung carries a point, can carry no point-free cell at
all, and every cell of that band is stuck on it. So where `Room` falls
below its demand, ONE stratum moves into such a band from the other
divided band — `W_plus` considered before `W`, and the negative side
before the positive — provided the other band keeps at least one and
the move raises `Room`. Each band gains at most one stratum. `S`,
`M_zero`, the sign counts and the draw budget of G4.3 are all
unchanged: both bands keep a stratum, so the zero stratum keeps its
place in the order, and G4.3 counts strata rather than cells. A 58-cell
column publishing forty-one `leading_zero` cells, ten negative cells
and a `min` of `-45.5` had `M_neg = 1`: without this step its ten
negative cells were stuck on `-45.5` and TWO NAMED counts came out
short.

**The cell step, taken second.** Where the strata that can carry cover
fewer than `W` cells, cells move into them until they do, or until no
more can move:

- `W_plus` is settled first, and only over the zero and positive bands,
  because there is no leading-plus spelling of a negative value;
- cells move only WITHIN a sign band, so `G`, `Z` and `P` are exactly
  what they were;
- no stratum is emptied, so `S` is exactly what it was;
- the fewest cells the demand needs are moved: taken from the strata of
  that band that cannot carry, in ascending `s`, each down to size 1,
  and shared out over the strata of that band that can carry by the
  same even split above;
- **except on a column on a written grid (G5.2a step 1)**, where the
  shares are the same even split but each carrying stratum, in ascending
  `s`, takes its share from the strata that cannot carry NEAREST to it
  in `s` — the lower of two equally near — each still down to size 1
  (landing 2b.1, repair, 2026-09-16). G5.2a lined every stratum of such
  a column up with the numbers its grid holds, and taking the cells from
  the lowest strata slid every boundary between those strata and the
  takers: on 4,000 temperatures written `37` beside `37.4`, 34 cells
  taken from the bottom left four strata on `35.3`, every stratum up to
  `38.0` straddling two written numbers, and the twin four numbers
  short. Taken from the nearest, only the boundaries beside a taker
  move, and the same column came back with all 34 numbers at every
  size and seed measured.

**The reach step, taken third** (P2-C5-F3). "Can carry" above is a
PLAN, not a certainty: every stratum that is neither a pinned end nor
the zero stratum is counted because the values step of G6.4 MAY take it
to a whole number. On a ladder that crowds several different values
inside one unit that plan does not come true — four values between
`0.125` and `1` leave their strata one whole number between them — and
the cell step then moves nothing, because by its own count nothing
needed moving. A genuine 82-cell producer column published 34
point-free cells and the twin wrote 20 on three seeds and 30 on two.

So the question is put to the LADDER and the answer is taken to a fixed
point:

- a stratum **really carries** exactly when its own share of the
  published ladder — the closed interval from `Ladder(c[s]/K)` to
  `Ladder((c[s]+g[s])/K)`, read by G5.6's own rule — holds a whole
  number that is inside its sign band, inside the published `min` and
  `max`, has a point-free spelling (G6.2), and is not one another
  stratum holds. Strata are offered their candidates in ascending `s`,
  each from the middle of its own share outward, which is where a drawn
  value sits on average and therefore which number `_whole_inside`
  takes;
- a stratum whose share does not move at all — the ladder is flat
  across it — is CERTAIN to hold that one value, so it claims it before
  the walk begins. Deciding in stratum order instead gave the number to
  an earlier stratum whose share merely touched the flat rung, and at
  run time the flat one took it anyway and the earlier one came back
  with nothing;
- the two sign fallbacks of G5.5 are treated as spoken for wherever a
  stratum's share crosses its own band's sign, because which side a
  drawn value falls on is a function of the seed and the split may not
  be;
- where the strata that really carry cover fewer than `W` cells, the
  cell step above runs again on this answer;
- and where a band's strata ALL sit on fractions, so that no cell can
  move anywhere useful, ONE stratum's window moves instead: the band's
  last stratum that may take a value at all is given the narrowest
  window of the ladder that reaches a free whole number, widened to the
  cells the demand still needs with its start moving first, and the
  band's other strata divide what is left by the same even split, each
  keeping one cell. `G`, `Z`, `P`, `S` and the draw budget are
  untouched;
- the two steps repeat until both demands are met or a round changes
  nothing, which is bounded by the strata themselves.

A column publishing `integer_valued: true` skips this step: G5.4 makes
every value whole, so every stratum carries already.

**Why the split gives way and the count does not.** A numeric block
publishes no multiplicity map — nothing in it says how many cells hold
each different value — so the even split is this method's own default,
not a published fact. `numeric_styles` IS published, and
EXACT-OBSERVABLE (contract 7.5.7, 9.4). Plan P2-D6's feasibility rule 4
fixes the order: published counts take precedence over ladder
conformance where the conflict is otherwise resolvable. The cost is
paid in the open rather than absorbed, because the twin's own report
reads `g_max` as no less than the widest stratum this step produces, so
its rung envelope widens by exactly what the step spent and by nothing
else. The quality report cannot read this layout, and reads `Cap`; so
wherever this step moves a stratum past `Cap` the two reports print
different windows for one fact, which is the one exception G5.6 names. Revision 1 had no such
step and left a producer's own style map unreachable: a 51-cell column
holding eleven `1.5`, twenty `100` and twenty `200.5` publishes twenty
`plain` cells, its own values prove the map, and an even three-way
split gave the one stratum that could hold a whole number seventeen
cells and named the other three as missed.

Number the strata `s = 0 .. S - 1` in the fixed order above, where
`S = M_neg + M_zero + M_pos`. Let `c[s]` be the number of cells in all
strata before `s` (so `c[0] = 0`) and `g[s]` the size of stratum `s`.
Then `c[S - 1] + g[S - 1] = K`.

### G5.3 The value of each stratum: pinned ends, stratified inverse transform, no word for a zero

**REVISION 2 (2026-08-27, plan P4-D4.10): the ladder a column of
numbers interpolates over is a HUNDRED AND ONE rungs, not eleven.**

The measurement that forced it. An eleven-rung ladder says nothing
about how many cells lie INSIDE a gap between two rungs, so a twin
drawn from it puts too few values where the real column crowded them.
Four hundred rows, a threshold at 1000, and the share of the column
below that threshold varied — the error in the twin's count of cells
below it:

| share below the threshold | eleven rungs | hundred and one |
|---|---|---|
| 11% | −2 | **0** |
| 24% | −9 | **0** |
| 37% | −31 | **0** |
| 62% | −39 | **0** |
| 85% | −37 | **0** |

The eleven-rung error grows with the distance from a named rung and
reaches thirty-nine cells, a tenth of the column; the finer ladder is
EXACT at every one of them. That is residual R-P4-30's defect, and this
is its repair.

**The first measurement of this table read `+2` in the right-hand
column at every share, and that was not the method — it was a defect in
this landing.** Eight places reached for `L[10]` meaning the top of the
ladder, which on a hundred-and-one-rung ladder is `p10`; with them
fixed the column reads nought. A constant error across five very
different shapes should have been read as a structural fault rather
than as a property, and it is written down here because the next person
to see a suspiciously flat residual should look for one.

**WHY THIS WORKED WHERE THE HISTOGRAM DID NOT** (G13, R-P4-49). The
histogram asked the twin to hold a COUNT per bin, and counts come from
the allotment, which never saw it. A ladder asks the twin to PLACE a
value, and placing values by interpolating a ladder is what this
section already does. No new mechanism was added: the list got longer.

**THE WHOLE LAYOUT READS THIS LADDER, and this paragraph said the
opposite until 2026-08-28.** It said the layout — how many strata a
band gets and which can carry a point-free spelling — still read the
eleven NAMED rungs, on a measurement taken before R-P4-49: handing the
finer ladder to the carrier-band decision was found to change the
strata counts, so a column came out a different shape rather than the
same shape more finely placed.

That measurement no longer holds, and it was RE-TAKEN rather than
trusted. Over 120 columns of six shapes — gaussian, heavily repeated,
bimodal, whole numbers, a narrow band around zero, and mostly zeros —
the layout is identical either way, 0 of 120 differing. What changed is
that G5.2a's sizes and G5.2b's band share now read this ladder
themselves, so the carrier steps are no longer the only thing standing
between the two.

**It is unified because one fact read from two different ladder
lengths is one fact written twice.** While the paragraph above stood, the shipped generator read
the eleven at the carrier steps and the independent reference oracle
read the hundred and one, and the frozen vectors agreed only because no
committed case separates them. Everything in G5.2, G5.2a, G5.2b and
G6.4 that reads a ladder reads THIS one.

For each stratum `s`, in ascending `s`:

- **`s == 0`**: the value is `L[0]` — the published `min`, used exactly
  as published. No word.
- **`s == S - 1` and `S >= 2`**: the value is `L[-1]` — the published
  `max`, exactly. No word. (The LAST rung, named by its position and
  not by the number ten: the ladder a column of numbers interpolates
  over has a hundred and one rungs, and code that reached for `L[10]`
  as the top of it read `p10` instead — see the revision note below.)
- **the zero stratum** (when it exists and is neither of the above): the
  value is exactly `0`. No word.
- **any other stratum**: one word `w` is drawn, and the value is

  ```
  N_s = c[s] * 2**64 + g[s] * w              (exact integer)
  D   = K * 2**64                            (exact integer)
  ```

  which places the stratum's uniform inside the stratum's own share of
  the distribution: `N_s / D` lies in `[c[s]/K, (c[s]+g[s])/K)`.

  Find the ladder segment `j` — the unique `j` with

  ```
  PCT[j] * D  <=  100 * N_s  <  PCT[j+1] * D
  ```

  scanning `j` upward from 0 and stopping at the first that holds. Where
  two adjacent rungs share a probability this cannot happen (the
  probabilities are strictly increasing), so the segment is unique.

  **`PCT` HERE IS THE HUNDRED AND ONE PERCENTS `0 .. 100`, AND `L` IS
  THE HUNDRED AND ONE RUNGS** — the eleven the description names and
  the ninety of `percentiles_between` beside them, merged in percent
  order and filled by G5.1's rule over the whole of it (revision 2,
  plan P4-D4.10). A DATE or CLOCK column keeps the eleven of G7.3 and
  G7A.4: each of those is a selection ladder over values that cannot be
  averaged, and the finer ladder is a fact about numbers.

  Which percents a ladder stands at follows from HOW MANY RUNGS IT
  HAS, so an implementation cannot pair a ladder with the wrong
  percents; doing so reads `L[j]` for a `j` chosen against the other
  scale, which on a hundred-and-one-rung ladder means never reading
  above the tenth percentile. Then

  ```
  A = 100 * N_s - PCT[j] * D                 (exact, 0 <= A < B)
  B = (PCT[j+1] - PCT[j]) * D                (exact)
  T = (A << 53) // B                         (exact, 0 <= T <= 2**53 - 1)
  t = ldexp(T, -53)                          (exact: a power-of-two scale)
  ```

  and the value is the **convex form**, in exactly this operation order,
  with exactly these four IEEE-754 binary64 operations and no others:

  ```
  u  = 1 - t                  (one IEEE subtraction)
  x1 = u * L[j]               (one IEEE multiplication)
  x2 = t * L[j+1]             (one IEEE multiplication)
  v  = x1 + x2                (one IEEE addition)
  ```

  followed by the **clamp**, in this order:

  ```
  if v < L[j]:    v = L[j]
  if v > L[j+1]:  v = L[j+1]
  ```

- **any other stratum of a column on a written grid** — the grid of
  G5.2a step 1, which includes a column whose other cells are written
  with no point: the word `w` is drawn exactly as above, and
  the stratum takes the grid value of the ladder at ONE OF ITS OWN
  RANKS rather than at a share between ranks:

  ```
  rank  = c[s] + ((w * g[s]) >> 64)           (exact integer, c[s] <= rank < c[s] + g[s])
  value = GridValue(Interpolate(Ladder, rank * 2**64, K * 2**64))
  ```

  G5.4 does not apply, the column not being whole-valued, and G5.5
  applies as to every stratum (landing 2b.1, 2026-09-15). **Why a rank
  and not a share.** G5.2a sized this stratum by the ranks whose grid
  value is its own; a share `[c[s]/K, (c[s]+g[s])/K)` runs one rank past
  them, so a one-rank stratum drew a position half a rank above its own
  number and snapped onto its neighbour's half the time. Measured on
  2,000 cells of a one-figure column publishing 598 different numbers:
  529 strata held a number of their own after the draw, and G6.5a's
  walk could bring that back only to 592.

**Why the convex form and not `L[j] + t * (L[j+1] - L[j])`.** The
difference form overflows to an infinity when the two rungs sit at
opposite ends of the representable range, and it loses the interpolation
entirely between neighbouring subnormal values — the two failures review
item P1-R2-F4 found in the profiler's own arithmetic. The convex form
cannot overflow on either multiplication, because each product is
bounded by its own rung.

**Why the clamp is not decoration.** `1 - t` rounds, so `u + t` can
exceed 1 by one unit in the last place, and two rungs of the same large
magnitude can then sum to an infinity. More importantly the published
`min` and `max` are EXACT-OBSERVABLE: an interior value one unit in the
last place above `max` would change the twin's own recomputed maximum
and break a fact the profile publishes. The clamp bounds every value
inside its own segment, so every value is inside `[min, max]`, exactly.

`t < 1` always (`A < B` gives `T <= 2**53 - 1`), so `t = 1` is never
reached and the top of a segment is only ever produced by the clamp or
by the `max` pin.

### G5.3b The tail reading (stage 3, plans P4-D344, P4-D322)

**A TAIL THAT PUBLISHES NEITHER DISTANCE IS READ FIRST, AND IT IS NOT
READ THROUGH A SHAPE** (plan P4-D349, contract TL5 and DT1). There is no
`d1` and no `rms` to fit `a(s)` to, so the side's rows stand on even
shares of the room between its boundary rung and its end, snapped to the
grid of step 4, one grid point apart at the least, and a row landing
where the row before it stands taking the next grid point outward. Its
END is `m` GRID STEPS beyond the boundary, held to the sign counts by
G5.5a -- the narrowest tail the description still asks for, since its
rows lie strictly beyond the boundary and the column's own count of
different values asks them to differ. Two wider readings were measured
against it and neither ships: the ends of the uniform stretch with the
column's own two published moments, and Cauchy-Schwarz's bound on the
mean of `m` of `K` cells. Plan P4-D349 records what each does, on which
shape, and what none of the three can do -- average to a mean a single
withheld cell carries, which is held at ledger entry `K-S3-15`.

For one side that publishes its pair -- boundary percent `P`, boundary
rung `b` (the published rung at `P`), rows `m`, mean distance `d1` and
root-mean-square
distance `rms` -- the rows beyond `b` are read through a shape `a(s)` on
`s` in `[0, 1]` -- the distance from `b` at the share `s` of the way out
-- that has `a(0) = 0`, whose mean over a uniform `s` is `d1` and whose
mean square is `rms * rms`: a MIXTURE OF TWO ADJACENT WHOLE POWERS,

```
a(s) = E * (s**j * (lam + (1 - lam) * s))
```

built with `+ - * /` and `sqrt` alone, each correctly rounded by IEEE
754, in this order and no other:

```
if d1 == 0 (or is not above nought): the tail is FLAT; a(s) = 0, E = 0
r   = (rms / d1) * (rms / d1)        one division, one multiplication
r   = 1 where r < 1; 1e15 where it is larger than that or not a number
j   = the whole number with R(j) <= r < R(j + 1), R(j) = (j + 1)**2 / (2j + 1)
a2  = 1 / (j + 2)        de = 1 / ((j + 1) * (j + 2))   the product in whole numbers
b1  = 1 / (2j + 1)       c  = 1 / (j + 1)               b2 = 1 / (2j + 3)
qa  = (b1 - c + b2) - (r * de) * de
qb  = (c - 2 * b2) - ((2 * r) * a2) * de
qc  = b2 - (r * a2) * a2
lam = 0 where qc <= 0; otherwise disc = qb * qb - (4 * qa) * qc, held at 0
      or more; q = -0.5 * (qb + sqrt(disc)) where qb >= 0, else
      -0.5 * (qb - sqrt(disc)); the candidates q / qa (where qa != 0) and
      qc / q (where q != 0) that lie in [-1e-12, 1 + 1e-12]; the smaller,
      clamped into [0, 1]; 1 where there is none
E   = d1 / (a2 + lam * de)     held at the largest finite binary64
```

`j` is decided by EXACT rational comparison: `r` is a binary64, hence a
whole significand over a power of two, and `(j + 1)**2 * den <= num *
(2j + 1)` is whole-number arithmetic. The search starts at the whole part
of `(r - 1) + sqrt(r * (r - 1))`, steps down while `R(j) > r` and up while
`R(j + 1) <= r`, so no rounding of the square root decides the power.
`s**j` is formed by squaring and multiplying over the bits of `j`, most
significant first, starting from 1; then `(1 - lam) * s`, `lam + that`,
`s**j * that` and `E * that`, in that order. No `pow`, `exp` or `log`
is used, so the reading is the same binary64 on every platform.

`R(0) = 1` is the jump (every row at one distance), `R(1) = 4/3` the
straight line, and a mixture of `s**j` and `s**(j+1)` reaches exactly
the ratios between `R(j)` and `R(j + 1)`, so every `r` of one or more has
one shape.

**The share, and THE TAIL IS ITS OWN ROWS.** A stratum reads the ladder
at the exact share `N / D` (G5.3), which stands at the rank position
`t = N K / D` of the `K` numbers. The LOW tail holds the ranks below
`m_lo` and the HIGH tail the ranks from `K - m_hi` up -- the rows the
description counts, and not the percent, which stands between two of
them. (Reading the tail by its percent instead leaves the first rank of
a tail outside it where `K P / 100` is whole: measured on a 2,000-row
column of ages, the twin then wrote its top value 19 times against the
20 rows published, and its listed tail missed.)

`N = 0` reads the low end exactly and `N = D` the high end, which is
what the two pinned strata hold. Otherwise the rank stands at the MIDDLE
of its own row's share of the tail, counting from the boundary outward
-- row `i` of `m` at `s = (2 i + 1) / (2 m)`, so the mean of `a(s)` over
a tail's rows is the mean of `a` over a uniform `s`, which is the
published mean distance, on both sides alike:

```
low:   A = 2 m_lo D - 2 N K - D                B = 2 m_lo D
high:  A = 2 N K - 2 (K - m_hi) D + D          B = 2 m_hi D
s      = ldexp((max(0, min(B, A)) << 53) // B, -53)
value  = b - a(s) held into [end_lo, b]   (low)
       = b + a(s) held into [b, end_hi]   (high)
```

Between the two tails nothing changes: G5.3's convex form over the
published rungs. The rungs `L[p]` of the ladder at a whole percent `p`
outside `[P_lo, P_hi]` are this reading at `N / D = p / 100`, and the
boundary rung itself where that percent falls between the two tails.

**The derived end** of one side, which the pinned stratum holds:

1. a published (heaped) end IS the end, and binds the reading (the
   clamp above holds every tail value at or inside it);
2. a LISTED tail's end is its outermost listed value (G5.3e);
2a. a tail publishing NEITHER distance takes the end above (P4-D349);
3. a FLAT tail's end is `b`;
4. otherwise the fitted shape read at the OUTERMOST ROW'S OWN SHARE,
   `a((2 m - 1) / (2 m))` -- where that row stands, and not where the
   distribution stops. Reading the fitted end `E` there instead, which
   is the shape's own supremum and which no row of `m` rows is expected
   to reach, put a 500-row column of charges 13 per cent past its own
   largest value and its twin's spread 9.7 per cent above the table's,
   where the row's own share leaves it 1.1 per cent under. That reading
   is moved OUTWARD, whatever the fitted power,
   to the larger of it and `d1 * H(m)`, `H(m) = 1 + 1/2 + ... + 1/m`
   summed in that order, which is where the largest of `m` draws of an
   exponential tail of mean `d1` is expected (plan P4-D326); held at or
   inside the tail's own BOUND `d1 + sqrt((m - 1) * max(0, rms * rms -
   d1 * d1))`, the furthest one row of `m` can stand with that mean and
   root-mean-square -- TAKEN AS `rms` TIMES A FRACTION,
   `d1 + rms * sqrt((m - 1) * max(0, 1 - (d1 / rms)**2))` where `rms`
   is above nought, which is the same number and is the only form this
   format holds at both ends of its range, `rms * rms` underflowing to
   nought below about 1e-162 and overflowing above about 1e154;
   then `b - that` on the low side and `b + that` on
   the high; then placed on the column's grid -- G5.4's rule where
   `integer_valued` is true OR the forms map names a cell it can only
   write WHOLE -- a `plain` or `leading_plus` count, whose cells wear
   the canonical spelling and so carry a point exactly where the value
   does; `leading_zero` is not one of them, because `01.5` wears that
   form with a point in it, and the anonymous pool names no form at all
   (counting either of them cost a column publishing
   `{"leading_zero": 35}` thirteen of its twenty-five named cells): a derived end is a construction and not a value of
   the table, `numeric_styles` is EXACT-OBSERVABLE, and G6.4's walk may
   not move a pinned stratum to find a whole number for it; measured on
   forty whole values beside twenty halves, the end stood at 0.9 and the
   twin wrote 21 decimal cells against a published 20), otherwise the
   text at the WIDEST width `fraction_widths` names, rounded half to
   even on the shortest round-trip figures and read back (unrounded
   where it does not read back; and where the census names NO width at
   all AND the BOUNDARY RUNG itself carries a point, the places that
   rung's own shortest round-trip text writes, so that a derived end
   never writes more figures than the description's own numbers do (a
   whole boundary rung leaves the end alone: placing it on the whole
   numbers there moved the strata beside it off the values the forms
   census asks for and cost a named count of twenty-five thirteen
   cells; and a rung whose own step would be no SMALLER than the rung
   leaves the end alone too, because a grid of that step is no grid for
   this column: the places of a shortest round-trip text are counted to
   seventeen and no further, so the rung 5.34e-322 of 120 subnormal
   numbers reads as seventeen places while one of them is larger than
   the whole column, and placing an end there rounds it to nought) --
   without it a column of tenths whose
   census is empty took an end of seventeen significant figures and its
   twin wrote `-27.17407492967617` beside cells of `-20.5`) -- and
   moved one grid step toward
   `b` where the grid placed it further from `b` than the bound times
   `1 + 1e-12`; then held to the ONE FIELD WIDTH the block's census
   names, where `integer_valued` is true, `field_widths` names one
   width covering every numeric cell, the block publishes no padded
   width and no cell of it is written with leading zeros or under a
   withheld form (a PADDED cell's width is not its value's: forty codes
   written `00000` to `00039` publish the width five while their values
   need one or two figures, plan P4-D14; and a block publishing a ZERO
   is left alone unless that width is one, because a width group below
   the floor is counted into the commonest width by plan P4-D222 -- the
   sixty whole numbers 0 to 59 publish `{"2": 60}` while ten of them
   wear one figure, and holding their derived end to two figures moved
   it from 0 to 10 while `n_zero` still asked the twin for a zero) -- a whole number of fewer or more
   figures is a value those published facts rule out, exactly as a
   negative end is on a column with no negative number (measured: sixty
   whole numbers from 10000 to 69000 derived an end of 9820 and the twin
   wrote 59 of the published 60 cells at five figures). The width `w` is
   held that way for `1 <= w <= 15`: the end's MAGNITUDE is held into
   `[10**(w - 1), 10**w - 1]`, signed again, placed on the whole numbers
   by G5.4 and then held on its own side of `b`. A PADDED BLOCK IS HELD
   TO THE ONE CEILING ITS OWN CENSUS DOES STATE: where `integer_valued`
   is true and `pad_widths` names ONE width `w`, of `2 <= w <= 15`,
   whose count is every numeric cell and which `field_widths` names at
   that same width for every numeric cell too, every cell of the column
   wrote at least one pad figure, so no value of it reaches `w` figures
   -- the end's magnitude is held at `10**(w - 1) - 1`, signed again,
   placed on the whole numbers and held on its own side of `b`
   (measured on 1,200 offsets written `+0123` and `0123`, plan
   P4-D145's own case: the derived end stood at 1006, ten cells took
   it, `+1006` wears no pad, and the twin's own description published
   `pad_widths {"4": 482}` against its source's `{"4": 1200}`, because
   P4-D148's plus route withholds the plus-signed padded cells
   altogether once ten of them are unpadded).

   THE ORDER OF THE LAST THREE IS: G5.5a's SIGN RULE, then the two
   width clamps above, then the MARK BETWEEN THOUSANDS -- where
   `thousands_marks` counts a mark on every numeric cell, every value
   of the column reaches a thousand in size (G6.5a's last value pass
   puts a mark exactly there), so the end's magnitude is held at a
   thousand or beyond and then on its own side of `b`. The two
   spelling clamps run AFTER the sign rule because that rule's own
   clamp can land an end the published spellings cannot write -- on a
   column with no negative number an end reaching past nought is held
   at one step, which is 1 on sixty whole numbers from 1000 to 60000,
   where the census names one width of five figures and the twin wrote
   9 of its 60 cells at a width the census does not name, and 0.01 on
   240 prices written `92,959.11`, a cell with no mark in it that the
   twin's own census then counted one short -- and neither clamp
   crosses nought, each moving a MAGNITUDE, so the sign rule is not
   undone by running before them.

   AND NEITHER SPELLING CLAMP PULLS THE END INSIDE THE TAIL'S OWN MEAN
   DISTANCE `d1`. Both censuses are POOLED at the floor -- a group of
   fewer cells than the smallest group is counted into the commonest
   (plan P4-D222) -- so a census naming ONE width does not say that no
   cell of the column is narrower, only that fewer than the floor's
   worth are. No set of `m` rows has mean distance `d1` when its
   furthest row stands nearer than `d1`, so an end the clamp puts
   inside `b -/+ d1` makes a CHECKED fact (G12.13) unreachable to hold
   a report-only census, and the clamp stands aside there: the end is
   the one G5.5a's sign rule left. Measured on the 30-row reading
   column of a macro workbook, whose thirty whole numbers 1 to 30
   publish `field_widths {"2": 30}` because the nine cells of one
   figure are fewer than the floor: the clamp moved the derived low end
   from under 1 up to 10, the twin wrote five cells at 10 and none
   below it, its mean stood 5.3 above the published 15.5, and
   `validate` MISSED `ladder.p50` and `moments.mean`.

**Why each step** (measured on the 16-shape battery of plan P4-D344 at
floors 1 and 11). The two moments are what the rows beyond the boundary
publish, and no published number is one of their values: before stage
3 a description published 13 to 46 numbers per shape equal to a value
fewer than eleven rows held; with it, none. The ends of step 4 are a
function of published facts alone, so the twin's range tells a reader
nothing the description does not. The outward move is there for code
developed on the twin: the fitted end of a light tail stands inside the
real extreme, and 16 real cells of a 20,000-row normal column fell
outside the twin's range without it (the skeptic's B6).

### G5.3c The moment ladder (stage 3)

A tail block publishing its moments and no rung (`tails` with two null
sides, TL3) is read as the straight stretch from `lo = mean - sqrt(3) *
std` to `hi = mean + sqrt(3) * std` -- the uniform with that mean and that
spread -- each placed on the grid of G5.3b step 4 and held to the sign
counts by G5.5a, the mean standing for `b` -- and every rung
`L[p] = (1 - t) * lo + t * hi`, `t = p / 100`,
held into `[lo, hi]`, with `L[0] = lo` and `L[100] = hi`. Where the mean
or the spread is withheld the ramp of G5.3d stands in. Measured on a
15-value block at floor 11: the twin's mean 1.9 per cent from the
table's and its spread 6 per cent, nothing missed on the twin or the
table.

### G5.3d The made-up ramp (stage 3)

A tail block below its floor (`tails: null`, TL2) publishes no rung and
no moment. Its ladder is a RAMP: `L[p] = (1 - t) * lo + t * hi` with
`t = p / 100`, `lo = -G u` and `hi = (K - G - 1) u`, each rung held into
`[lo, hi]` and placed on the grid, `u` one step of the grid step 4 of
G5.3b names (one where no width is named). The strata then take points
about one step apart on their own sign bands, so the twin keeps the
block's type, its sign counts and its count of different numbers and
claims nothing else. Measured on an 8-value block at floor 11: before
the ramp the sign fallback wrote `1.0` eight times and the twin was
re-described as another role; with it, 0 to 7 and nothing missed.

### G5.3e The listed tail (stage 3, plan P4-D324)

A tail whose `values` list is not empty -- on a block with a grid, a
tail of at most six different values, or one whose published facts
would otherwise solve for its end (contract 6.7, TL6) -- is read as a
STAIRCASE over its own rows. The listed values are taken OUTERMOST FIRST
(ascending on the low side, descending on the high side), each holds at
least one row, and the `R = m - L` rows over (`L` values) are placed by
this rule:

- every binary64 of the tail -- `b`, the values, `d1`, `rms` -- is
  written as a whole number of one shared power of two, exactly, so a
  value's distance `A_i = |b - v_i|` and its square are whole numbers,
  and so are the targets `S1 = m * d1` and `S2 = m * rms * rms`;
- the candidates are the count vectors `c_i = 1 + e_i` whose extras
  `e_i >= 0` sum to `R` and are nonzero on at most THREE values;
- the chosen one makes `|sum c_i A_i - S1|` least, then
  `|sum c_i A_i**2 - S2|` least, then is the smallest vector of extras in
  lexicographic order, outermost first.

On a grid the summed distance of the real tail is what the published
`d1` rounds from, so the twin's `d1` is met exactly and its
root-mean-square as closely as whole counts on three values allow. The
share `N / D` inside a listed tail reads, counting the rank position
`t = N K / D` from the tail's outer end (`t` on the low side, `K - t` on
the high), the first listed value whose running count exceeds that
position on the low side and reaches it on the high side, and the
innermost listed value past the tail's rows. The layout of G5.2a
neither joins nor divides a band's leading or trailing runs that lie
wholly inside a listed tail's rows: each is one listed value at the
count solved for it -- UNLESS those runs are the whole band and it is
owed more strata still, where they are left to the ordinary walk,
because there is no other run to divide and the twin would otherwise
hold fewer values than the description names (twenty-four offsets
written `+0100` and `0100` over eight values: both tails list four
each, those eight runs are the band, and sixteen different SPELLINGS
ask for sixteen strata). The pinned end is the outermost listed value.

**A RUN THAT REACHES ACROSS A TAIL'S EDGE IS ONE OF THOSE RUNS**, whole,
WHERE THE BAND'S RUNS MUST BE JOINED to reach its stratum count: the
protection reads a run as the tail's where any of its ranks is the
tail's, and not only where all of them are, on a band with more runs
than strata. Two qualifications, each measured. Only where the runs
must be joined, because that is the only case a run can be joined away
in and the protection is not free: on 150 cells over three values
written `+100.25`, `200.25` and `300.25`, whose three runs already had
three strata, protecting the two that reach into a tail split the fifty
published pluses across two values and the twin wrote four spellings of
three numbers. And the band is still LEVELLED after it, because the
runs a listed tail names are the ladder's and the ladder's own boundary
can stand a rank from the column's: what the tail needs is that the run
not be joined away, not that it be held still, and holding it still
gave that same band 49, 53 and 48 cells where the source holds fifty of
each. A tail's innermost listed value
is commonly the column's value just inside the boundary as well, so the
ladder reads one number across the edge, and counting only the runs
lying WHOLLY inside left that one to the ordinary walk. Measured on 240
rows of clinical codes at a floor of one, whose high tail lists two
values and whose inner one stood at eleven ranks, the outer two of them
the tail's own: the walk joined that run to its neighbours, the stratum
that swallowed it read its own share instead, and the twin wrote five
cells at `920759` where the table holds `920760` -- so `validate`
MISSED `tails.high.values`. The run is kept WHOLE rather than cut at the
edge, which was the first repair and cost more than it bought: a cut
spends one of the band's strata on the tail's own part, and on 1,140
readings over eleven values it took that stratum off the published
MODE -- 210 cells written nowhere, `-1.4` written in 307 cells against
170, and the median moved with them.

Why. On a bounded scale the tail holds a handful of values each held by
several rows, and G5.3b's smooth reading rounded onto that grid wrote
values the scale does not have and never wrote its real end: a pain
score of 0 to 10 at floor 11 wrote 50 cells at 11 and none at 10, and its
twin's mean was 25 per cent high with nothing missed (the skeptic's B1).
The owner's ruling of 2026-09-22 settles what may be said: "many people
will be there and there is no big deal in knowing that it's there".
With the listed tail, 13 columns of pain, GCS, a surgical risk grade,
Apgar, children and Likert scales at two seeds write no off-scale cell
and every real value.

### G5.4 The integer rule

When `integer_valued` is published **true**, every value of the K
numeric cells is a whole number. The rule is applied to each stratum
value after G5.3 and before G5.5, and it is applied by the FACT and not
by the role (P2-D6): a `continuous` column publishing
`integer_valued: true` gets it, and a `count` column publishing false
does not.

```
b = int(v)                  exact truncation toward zero
r = v - float(b)            exact; |r| < 1, sign follows v
if r >  0.5:  n = b + 1
elif r == 0.5: n = b + 1                  ties go toward +infinity
elif r < -0.5: n = b - 1
elif r == -0.5: n = b                     ties go toward +infinity
else:          n = b
```

**Rounding direction, stated once:** to nearest, and **ties toward
positive infinity**. Not banker's rounding, and not toward zero: two
implementations that disagree here disagree on bytes, and half-even
would make a twin's rounding depend on the parity of a neighbour.

**AND THE ONE PLACE THAT RULE DOES NOT GOVERN, named here so that
"stated once" stays true.** The integer rule above places ONE value at
a time and a bias in it moves that value. Phase 4's fixed-fraction
snap — the rule that writes a `decimal`-styled cell at a width the
column's own census publishes (plan P4-D4.5, with amendments A-P4-5,
A-P4-6, A-P4-8 and A-P4-15) — places a whole column of them at once,
and a bias toward positive infinity applied to every tie there walks
the column's own mean up with it. That snap rounds **half to even**,
which the plan fixes in those words. Nothing else in this method does.

**WHAT THE SNAP ROUNDS, which half to even alone does not settle.**
The operand is the value's SHORTEST ROUND-TRIP DECIMAL FIGURES — the
shortest decimal string that reads back as exactly this binary64,
which is what `repr` produces and what G6.2 already builds every
spelling from — and NOT the binary64 itself. The two give different
answers and a second implementer has to be told which: `2.675` is held
as a double a shade BELOW two and sixty-seven and a half hundredths,
so rounding the double at two figures gives `2.67`, while rounding its
shortest figures `2675` at two gives the tie, and the tie goes to even,
so `2.68`. Both are defensible half-to-even; only one is this method's.
Review round 2 of the integer-grid landing found this document silent
on it while two implementations agreed on `2.68` for no stated reason.

**AND THE SIGN SURVIVES A MAGNITUDE THAT SNAPS TO NOTHING.** Where the
figures round away entirely the sign is still written: `-0.004` at two
figures is `-0.00`, not `0.00`. This is NOT the "never `-0`" rule of
G6.2, which governs the canonical spelling of zero itself; here the
value is not zero and the width is what hides it. A second implementer
who dropped the sign would write a different cell, and the twin would
carry a positive-looking cell where the column held a negative value.

**THE REST OF THE SNAP IS NOT WRITTEN HERE YET, and that is a recorded
debt, not an omission this sentence closes.** **R-P4-146** owes this
document the width assignment, the pinned-cell order, and the
same-class and endpoint guards. It is named here because review round 3
of the integer-grid landing found this paragraph assigning that debt to
R-P4-17, which is CLOSED — so the unwritten half of the snap had no
live owner at all. R-P4-18 owes a vector in which a value is actually
rounded, and now owes it twice over, because no frozen case reaches the
operand rule above either. Both
are named in the Phase 4 plan's register. What the paragraph above
settles is only the contradiction: a second implementer reading this
section used to find a global tie rule the shipped snap violates by
name, with nothing saying an exception existed.

Both subtractions are exact. For `|v| >= 2**52` the value is already
integral and `r` is zero; below that, `b` is exactly representable and
`v - float(b)` needs no more than 53 bits, so no rounding occurs.

`min` and `max` are themselves whole numbers whenever `integer_valued`
is true (every value was whole, so the extremes are), and rounding a
value inside `[min, max]` to a nearest integer cannot leave that
interval. The pinned strata are not rounded — they already carry the
published rungs — which is what keeps the endpoints exact.

### G5.5 Placing `n_zero` and `n_negative` exactly

The strata of G5.2 give the exact counts by construction: `G` cells sit
in negative strata, `Z` cells in the zero stratum, `P` in positive
strata. Two repairs make that construction true of the VALUES as well,
because the ladder and the sign counts are separate published facts and
nothing forces them to agree:

```
negative_fallback = the larger of L[0] and -1
positive_fallback = the smaller of L[10] and 1
```

Applied to every stratum after the integer rule, including the pinned
ones:

- a stratum in the negative band whose value is `>= 0` takes
  `negative_fallback`;
- a stratum in the positive band whose value is `<= 0` takes
  `positive_fallback`;
- the zero stratum's value is exactly `0` and needs no repair, because
  it was never drawn.

Both fallbacks are inside `[min, max]` whenever they are reachable: a
column with `G > 0` has a negative value, so `min < 0`, so
`max(min, -1) < 0`; symmetrically for the positive side. Both are whole
numbers when `integer_valued` is true, because a whole `min < 0` is at
most `-1`.

**On a column written at one width `f > 0`** (the grid of G5.2a step 1
and G5.3; integration repair of landing 2b.1) a stratum that is not
pinned takes instead the nearest point of that grid on its own side of
zero that no other stratum holds -- `-0.01`, then `-0.02`, and so on at
`f = 2`, never past `L[0]` on the negative side or `L[10]` on the
positive -- and the first such step where every one within reach is
held. The strata are repaired in stratum order, and "held" is the value
every other stratum has at that moment. The grid value of G5.3 puts a
negative stratum whose rank lies within half a step of zero on `0.00` or
`0.01`, so the plain fallback made such strata `-1`: on a 2,000-row
column of changes rounded to two places two of them landed on `-1.0`
beside a third that held it, one number spent the count of different
values, and its six cells were written `-1.0` against a published width
of two. The pinned strata keep the plain fallbacks.

**The precedence is stated, not implied:** where the ladder and the sign
counts disagree, **the counts win** (P2-D6 feasibility rule 4). The
repair moves at most one value per conflicting stratum onto a fallback,
the deviation is measured against the published rungs, and the report
names it. Where a repair changes a PINNED stratum — which can happen
only for a profile whose `min`/`max` contradict its own sign counts —
the endpoint stops being EXACT-OBSERVABLE for that column and the report
names the achieved endpoint beside the published one.

### G5.5a The sign rule on a derived end (stage 3)

A derived end (G5.3b step 4, G5.3c) is held to the sign counts after it
is placed on the grid: where the block has no negative number the low
end is at least nought -- nought where `n_zero > 0`, otherwise the
smaller of `b` and one grid step where it would be nought or less --
and symmetrically the high end where the block has no positive number;
ONE STEP HERE IS THE SMALLEST POSITIVE NUMBER THE FORMAT HOLDS where
the block names no width, its boundary rung gives no places, and the
step that leaves is not smaller than that rung: `min(b, one)` hands
back `b` itself there and the tail's rows have nowhere to stand (120
subnormal numbers, `5e-324` times 1 to 120, whose whole column is
smaller than one);
then the low end is at or below `b` and the high end at or above it. A
published heaped end is never moved. The pinned strata keep G5.5's plain
fallbacks for anything this leaves (a profile whose ends contradict its
sign counts).

### G5.6 The two-sided rung envelope

This is the acceptance bound the disposition battery applies to a
numeric column, and it is stated here because the method is what makes
it true.

Let `Ladder(p)` be the published ladder read as a piecewise-linear
function of a probability `p` in `[0, 1]`, using the same segment rule
and the same convex form as G5.3. Let `g_max` be G5.2a's `Cap`, read off
the numeric block the numbers are described by — a column's own block,
or the block of one joined position, one affixed wrapper or a compound
column's numeric half — and the count of numeric cells that block
describes where `Cap` is 0 (landing 2b.1, part 2, 2026-09-15). It is a
function of the description alone, so the twin's own report and the
quality report read one number without either rebuilding the layout
(validation method V1.4), and

```
d = (g_max + 2) / K
```

Then, for each of the nine INTERIOR rungs `i = 1 .. 9`, the rung `T[i]`
recomputed from the twin's own written numeric cells (by the profiler's
own type-7 quantile, over the parsed values) must satisfy

```
Ladder(max(0, PCT[i]/100 - d))  <=  T[i]  <=  Ladder(min(1, PCT[i]/100 + d))
```

and the two extreme rungs must be met EXACTLY:

```
T[0] == L[0]        and        T[10] == L[10]
```

**Why that window.** The cell that lands at recomputed rank `k` comes
from the stratum covering rank `k`, whose share of the distribution is
at most `g_max / K` wide, and a recomputed rung interpolates two
adjacent order statistics, which adds one more rank. So `d` is the
widest ladder displacement the construction can produce, and the bound
is a statement about the method rather than a tolerance somebody
measured and rounded up.

**Why no stratum is wider than `g_max`.** G5.2b's band floor gives every
band enough strata to hold its cells under `Cap`, and G5.2a's levelling
holds every stratum under it. **The one exception is named, not
absorbed.** On a column publishing `integer_valued: false` beside a
point-free style count, G5.2b's carrier and reach steps may move cells
past `Cap`, because the published style count wins (plan P2-D6, rule 4).
The twin's own report, which built the layout, then reads `g_max` as the
widest stratum built, so its bound still holds of the construction. The
quality report cannot read that layout (validation method V1.4) and reads
`Cap`, so there the two reports print different windows for one fact and
the quality report's is the narrower: it can call a rung MISSED that the
twin report calls inside. Closing that needs a second writing of the
carrier and reach steps outside the generator. Measured: of 11,134
layouts the generation test files build, 305 stood above `Cap`, every
one of that shape; on a 4,000-row column of halves written without
their trailing zero one stratum held 315 cells beside a `Cap` of 268,
and no rung left the narrower window at the seeds tried.

**What it must reject.** A mutant that ignores the nine interior rungs
and interpolates only between `min` and `max` produces
`T[i] ≈ min + (PCT[i]/100) * (max - min)`, which leaves this window on
any column whose ladder is materially non-linear. The battery is
therefore required to include at least one fixture whose interior ladder
is far from a straight line and whose `K` is large enough that `d` is
small — a fixture where the collapse mutant misses the window by more
than one rung — and to assert this bound on it. Rung mutants that
permute or swap the interior rungs are rejected by the same window.

**The same window holds rank by rank, not only at the nine rungs.** The
argument above never uses the fact that `i` is one of the eleven ladder
positions: it bounds the value at ANY recomputed rank. Writing `p_k =
k / (K - 1)` for the share the profiler's own quantile rule attaches to
sorted position `k`, every value `V[k]` of the twin's own sorted numeric
cells satisfies

```
Ladder(max(0, p_k - d))  <=  V[k]  <=  Ladder(min(1, p_k + d))
```

with the same `d`. On a column publishing `integer_valued: true` both
ends widen by the one half unit the whole-number rule of G5.4 can add;
on a column written at one fraction width, by half a unit of its last
place, which is how far G5.3's grid value stands from the ladder at its
own rank; and by nothing else. G12.3 derives the moment bounds from this rank
form, so the moments and the rungs rest on one statement about the
construction rather than on two.

Moments (`mean`, `std`, `skew`) are APPROXIMATED, and **G12.3 fixes a
formula and a finite two-sided bound for each of them**, derived from
the rank form above. Revision 1 of this document left that bound to a
test battery; review item P2-C1-F4 ruled that delegating a normative
bound to a battery leaves an approximated fact with no bound at all,
since a battery is not a document an independent implementer can
conform to.

### G5.6a The envelope on a tail block (stage 3)

On a tail block the ends are DERIVED and not EXACT-OBSERVABLE: `min`
and `max` are checked only where published (a heaped end), and then
ONE-SIDED and silently -- no cell of the file beyond the end, and the
file's own extreme never printed (validation method V5). The rank form
and its `d = (g_max + 2) / K` stand unchanged over the tail ladder of
G5.1a, so G12.2's and G12.3's windows are drawn through it. A rung the
tail rule withholds carries no window and is LISTED.

## G6. Numeric spelling

### G6.1 The permitted family

Owner decisions 7, 8 and 10 fix the family. A numeric cell is written in
exactly one of six **styles**, and in no other form:

| style | what it writes | changes the type a reader infers? |
|---|---|---|
| `plain` | the canonical spelling (G6.2) | no |
| `leading_zero` | canonical, with one or more `0` characters inserted immediately after the sign | no |
| `leading_plus` | canonical, with a `+` written before a non-negative canonical spelling | no |
| `decimal` | the value in fixed-point notation with at least one digit after the point | yes — a whole-number column reads as a decimal one |
| `exponent_lower` | the value in exponent notation with a lower-case `e` | yes |
| `exponent_upper` | the value in exponent notation with an upper-case `E` | yes |

**A thousands separator only where the column publishes one** (`group_separator`, contract 6 numeric block; stage 2, 2026-09-14). The ruling that stood here — that a separator is never written because the comma breaks the CSV row itself — was false: a cell holding a comma is quoted by the CSV writer and read back unchanged. It was the whole cause of a defect in which a grouped charge column came back ungrouped and code developed on the twin silently discarded every charge over a thousand from the real table. Where `group_separator` is `,` or `.`, every `plain` cell, and every `leading_plus` or `decimal` cell at leading-zero order zero, is grouped with a comma, so a column whose proving cells were the majority is written wholly grouped; a `leading_zero` cell, an exponent form and a cell at a raised order are never grouped (the stage 2 audit, 2026-09-14). A column declared to write its decimals with a comma publishes `.`: it is grouped with a comma like any other and then has its points and commas exchanged, so `42,037.34` is written `42.037,34`.

**Every mark a column may publish, and every notation of a negative, and a plus on a decimal** (landing 2b.2, 2026-09-15; plan P4-D41). A column publishing a space, an apostrophe, U+2019, U+00A0, U+202F or U+2009 is grouped with that mark itself, under the same rule of forms and order; no exchange touches it, so a declared decimal-comma column grouped with a space is written `1 234,56`. Where `decimal_plus` names a count, the cells allocated `decimal` whose value is not negative are taken in cell order, P being the lesser of the named count and their number E, and the plus is placed on WHOLE VALUES (integration repair of landing 2b.2: placed cell by cell, three values written fifty times each, one with a plus, came back as six spellings, and 900 signed changes publishing 690 spellings as 780). Those cells form runs of one value, in cell order; a run from cell `a` to cell `b - 1` is offered `floor(b·P/E) - floor(a·P/E)` pluses and takes one on every cell where that offer is at least half its length. While the cells taken exceed P, the taken run with the smallest offer per cell no longer than the excess is given up; while they fall short, the untaken run with the largest offer per cell no longer than the shortfall is taken, the earlier run first on a tie. What whole runs still cannot meet is spread inside one run -- the last taken run where the total is over, keeping its length less the excess, or the first untaken run at least as long as the shortfall -- and a run of length m holding k pluses gives its j-th cell, counting from nought, a plus exactly where `floor((j+1)·k/m)` exceeds `floor(j·k/m)`; so a column whose decimal cells all hold one value is spread one in every `E/P` exactly as before; a pooled count names no form and adds no plus; the plus stands in front of any zeros the cell spends. Before any fraction width is assigned (G6.6), where fewer cells are allocated `decimal` on a value not negative than the named count, cells exchange forms: each cell allocated `plain` or `leading_zero` whose value is not negative, from the first cell upward, takes the first cell, from the last cell downward, allocated `decimal` whose value is negative, has a point-free spelling, is not yet taken, and -- where the giver is `leading_zero` -- writes no more figures than the giver does, so the field width the padded exchange fitted it to is still reachable; each pair swaps its two forms, for as many pairs as the shortfall allows; no form count moves (integration repair of landing 2b.2: only `plain` gave, and a column of `-001` beside `+2.00` and `+3.00` came back with none of its hundred pluses). Where E is still below `decimal_plus` every eligible cell carries one and the report names a deviation of `decimal_plus`. Every negative cell is then written in the column's `negative_form`: the figures after the hyphen-minus, zeros and mark included, inside brackets, after the minus sign U+2212, or followed by a hyphen-minus -- the last only where those figures carry a decimal point, because neither `12-` nor `1,234-` is read as a number, so such a cell keeps its hyphen-minus in front. So `(001234.5)` and `(1,234.5)` are written and `(0,001.00)` never is.

**A mixture of conventions is written as a mixture** (landing 2b.7, 2026-09-15; plan P4-D65.2). `negative_form` and `group_separator` publish the column's MAJORITY, and writing every cell that way threw the minority away: 480 negatives with a minus beside 120 in accounting brackets came back as 600 minuses, and 200 cells grouped with a space beside 100 grouped with a narrow no-break space came back as 300 ordinary spaces, each with no deviation reported and no check missed. Where `negative_notations` names a notation, each named notation takes its count in turn from the cells holding a negative value that no earlier notation took; where `thousands_marks` names a mark, the cells that CAN be grouped are taken the same way. **EACH COUNT IS SPREAD ACROSS THE VALUES, NOT TAKEN FROM THE FIRST CELL UPWARD** (plan P4-D149, the repair pass of the final Codex review). The cells stand in stratum order, ascending, so the first version's walk put the last convention on the largest values: 1,500 amounts at a floor of eleven, 915 grouped and 585 bare with means of 489,137 and 483,357, came back with a grouped mean of 289,169, a bare mean of 795,007 and every bare cell larger than every grouped one, with every check passing. A count is placed over the cells still untaken, in cell order, by the whole-value spread rule the plus sign uses below — runs of one value offered their share, given up or taken whole to make the count exact — except that a run the count must split keeps its share on its FIRST cells, so a notation and a mark spent over one run of a negative value split it at the same cell and write the value two ways rather than four. A column whose eligible cells hold one value is therefore written exactly as before. Where `negative_notations` names no notation, or `thousands_marks` no mark, every cell wears the column's published majority — so a column publishing no mixture is written exactly as it was before this rule existed. **WHERE `thousands_marks` NAMES A MARK, THE CENSUS IS THE WHOLE OF THE GROUPED CELLS** (plan P4-D142, the final Codex review's item 3). Measured before this sentence, at a floor of eleven and seed 4: 800 prices grouped with a comma beside 400 bare published `{",": 800}` and the twin grouped all 1,200; 800 commas, 200 spaces and 200 bare came back as 1,000 commas and 200 spaces; and 600 commas beside 600 spaces, which publish no majority, came back with no grouped cell at all. So the groupable cells are spent in three parts, each by the spread just stated: each named mark takes its count, in the contract's own order of marks; a `(withheld)` remainder takes its count next, written with the first of a space, an apostrophe, U+2019, U+00A0, U+202F and U+2009 that the census does not name — never a named mark, which would add the pool to that mark's count, and neither decimal mark; and the cells still left are written with NO mark wherever they number at least the census floor max(2, `small_cell_floor`), because the census is published only beside a bare remainder of nought or at least that floor (contract C6-88), while a smaller remainder is the twin's own ladder reaching a few more values past a thousand and wears the published majority as before. A cell CAN be grouped exactly where writing it with a mark puts a mark in it, which is this section's own rule about forms, leading-zero order and four whole figures, asked of the writer rather than restated; the mark asked with is the published majority, or where the column publishes none the first mark its census names, so a column with no majority is not left with no groupable cell. A trailing minus is offered only to a cell allocated `decimal`, because the notation is written only where the figures carry a decimal point, so a cell without one would keep its minus in front and miss the census silently. Where a named count has more cells than the twin can offer, every cell it can reach takes the convention and the report names the shortfall as a deviation of that census.

**AS MANY CELLS REACH A THOUSAND AS THE CENSUS OF MARKS COUNTS** (plan P4-D185). A cell carries a mark between thousands exactly where its number reaches a thousand, and the ladder places the strata near a thousand by interpolation, a rank or two either side: 2,000 lognormal amounts written `1.234,56` published `{".": 418}` and the twin wrote 416 at every seed, and over twelve such columns sixteen twins of twenty-four wrote one or two fewer and two wrote one more, the surplus named nowhere. So, as the last of the value passes of G6.5a and G6.6, on a column whose every numeric cell is on ONE grid (G6.5a's first two clauses), naming no field width and no form but `decimal` and `plain`: let `C` be the census's cells, named and pooled, and `K` the cells whose values reach a thousand in size, of either sign. Where `K < C`, the run of strata just below a thousand, from the highest down while their cells do not pass `C - K`, takes the lowest free grid points of a thousand or more, in order, the last below the value of the stratum above the run. Where `C < K < C + max(2, small_cell_floor)` -- a surplus the table cannot have held as bare cells, since the census is published only beside a bare remainder of nought or at least that floor -- the run from a thousand up, from the lowest while their cells do not pass `K - C`, takes the highest free grid points below a thousand, in order, the first above the value of the stratum below it. A free grid point is one whose text no stratum holds and whose text survives being read and written again, looked for at most sixty-four units past the run's own length. A stratum moves only where its text is its own and never the first or last stratum; the run moves whole or not at all, so the count of different values, the sign counts and the order of the strata stay where they were. Only strata in the positive band are in a run. **AND ON THE NEGATIVE SIDE** (plan P4-D194, the final skeptic of stage 2's close): the rule first stood aside on any column holding a negative value, and 1,500 amounts one in ten negated published `{",": 396}` while the twin wrote 397 at seeds 4 and 11 with nothing named -- over forty such columns, 36 twins of 80 missed by one to three. So on a column holding a negative value, once the run above has moved or not, `K` is counted again and the same rule is taken among the strata of the negative band read by size: "a thousand or more" is "minus a thousand or less", the run below a thousand is the run of negative strata just above minus a thousand, from the lowest up, taking the highest free grid points of minus a thousand or less, each above the value of the stratum below the run, and the run from a thousand up is the run from minus a thousand down, taking the lowest free grid points above minus a thousand. **A SURPLUS UNDER THE LINE IS NAMED**: where the cells the census's marks leave over number more than nought and fewer than the census line, and so wear the published mark, the twin's report names `thousands_marks` with the census's count and the count the twin holds.

**THE PUBLISHED MODE IS A NUMBER THE TWIN HOLDS** (plan P4-D267, the extra review round of 2026-09-18; stated here and mirrored in the oracle by the carried numbers pass of the same day). After the census of marks, as the LAST of the value passes, where the column publishes a `mode` and a `mode_count` of one or more and has at least three strata: where some stratum already holds the `mode`, nothing moves, and the twin's report names `mode_count` with that stratum's SIZE against the published count wherever the two differ (item 1 of the numbers pass of the second Codex round, 2026-09-19). The published pair is a pair, and this pass declared success on the VALUE alone: measured at a floor of eleven on one-place values -1.8, -0.9, -0.6, 0.8, 1.8, 3.3 and 3.5 at the counts 9, 18, 28, 23, 8, 30 and 23, at seeds 4, 0, 1, 7 and 13 alike, the description publishes the mode 3.3 at a count of 30, the ladder gives 3.3 a stratum of one cell and no stratum at all is 30 cells, so the twin wrote 3.3 once, its commonest numbers were -0.6 and 3.4 at 28 each, its mean moved 1.17338 to 1.06619 and its spread 1.92529 to 2.08471, and NOTHING was named. The cells do not move for it -- a stratum's size comes from the runs of the published ladder and not from `mode_count`, which is why the pair is LISTED and not checked (G11, and the same measurement the validator records) -- and what is owed is that the difference be said. Otherwise the stratum taken is the one, among all but the first and the last, whose size is exactly `mode_count`, standing nearest the `mode` by absolute difference, the earliest on a tie; where none is that size nothing moves. It takes the `mode` as its value only where every guarantee the passes before it established survives the move: the `mode` lies strictly between the values of the strata on either side of it; the stratum's sign band holds it (the zero band nought alone, and no other band nought); on a column whose styles map asks for a point-free cell, whether the stratum's value has a point-free spelling does not change; on a column written on ONE grid (G6.5a's first two clauses) the `mode` is a point of it -- a whole number on the integer grid, and on a grid of `f > 0` figures a value whose grid text reads back as itself; and, where the column publishes `empty_bins`, the `mode`'s bin under contract C6-31f's division of the published `min` to `max` is not one of them. Where the move is not made, the twin's report names `mode` with the published number beside "a number of its own". Measured before the rule, on eleven one-place values from -1.7 to 6.9 at a floor of eleven: the published mode -0.6 over 210 rows was written nowhere, and the twin's median moved from -0.6 to -0.2 with nothing named.

**Accounting brackets never hold a sign.** The rule that stood here -- never write accounting parentheses, because they are reserved for the contradictory-notation stand-in of G10.3 -- is withdrawn by landing 2b.2: that stand-in is brackets around a SIGNED number, `(-5)`, and a written negative in the `brackets` notation holds the unsigned figures, so the two constructions stay distinct and a cell keeps its class.

**Which decision governs which question** (P2-C1-F8). Decision 8 fixed
the family the twin may INVENT from — the leading-zero forms, which have
no ceiling and change no inferred type — for the spellings a published
distinctness count needs beyond the ones the style map already accounts
for (G6.5). Decision 10 then made the FORM of every cell a published
fact, and a published form is written because it is published: a
`decimal` cell carries a point because the real column's cell did, which
is the fidelity decision 10 was taken to protect. The profile contract
states the same division in its section 7.5.7, and the two documents are
checked against each other by a test.

**An alternate spelling is used only where the published counts require
it.** A column whose `numeric_styles` says every cell is `plain` is
written entirely in canonical spellings and is byte-plain, and is read
by an ordinary reader as exactly the kind of column the real one was.

### G6.2 The canonical spelling

For a finite binary64 `v`:

- **When the column publishes `integer_valued: true`** (so `v` is
  whole): the base-ten digits of the exact integer `int(v)`, with a
  leading `-` when negative, no decimal point and no exponent. `0` is
  written `0`, never `-0`.
- **Otherwise**: the shortest decimal digit string `D` and decimal
  exponent that read back as exactly `v` (shortest first, then nearest,
  ties to even significand), formatted by this rule, where `decpt` is
  the position of the decimal point relative to `D` — that is,
  `v = 0.D × 10**decpt`:
  - `-4 < decpt <= 16`: fixed-point notation, with `.0` appended when no
    fractional digit would otherwise be written;
  - otherwise: exponent notation `d[.ddd]e±XX`, lower-case `e`, sign
    always written, exponent at least two digits.

  This is exactly what Python's `repr` of a float produces, which is
  what the implementation uses; the rule is stated in full so an
  independent implementer in another language does not have to
  reverse-engineer it. Examples that pin the boundaries: `1e+16`,
  `1000000000000000.0`, `0.0001`, `1e-05`, `5.0`, `-2.5`.

**The POINT-FREE spelling of a value, and why it is not always the
canonical one** (P2-C2-F2). Three of the six styles — `plain`,
`leading_zero` and `leading_plus` — write a text carrying neither a
decimal point nor an exponent, because that is what the contract's
first-match ladder (contract 7.5.4) counts them by. On a column
publishing `integer_valued: false` the canonical spelling of the whole
value `100` is `100.0`, which that ladder counts as `decimal`, so a
generator writing canonical spellings can place none of those three
styles on such a column at all. That is not what the profile says
happened: a real column holding `1.5` beside `100` publishes eleven
`decimal` cells and forty `plain` ones, and the forty were written
`100`, `101` and so on.

So the point-free spelling of a value `v` is defined for its own sake:
let `D` and `decpt` be the shortest round-trip digits and decimal point
of G6.2. Where `decpt >= len(D)` — that is, `v` is a whole number — the
point-free spelling is the sign, `D`, and `decpt - len(D)` trailing
zeros, and it reads back through `parsing.parse_number` as exactly `v`.
Zero is written `0`, never `-0`. **There is no width ceiling** (owner
decision 10, 2026-08-13): an earlier revision stopped at
`-4 < decpt <= 16`, which is the fixed-point window of the CANONICAL
spelling, and that window governs the numbers inside a profile document
rather than the spelling of a cell in the twin. A plain cell owes that
it reads back as the same number and that it classifies as plain, and
the digits of a whole value do both however many there are; while the
ceiling stood, a column whose source wrote `100000000000000000000` in
figures was published `plain` and written back with a point. Where `v`
is not whole, no point-free spelling of it exists; the canonical spelling stands in its
place and G6.4 does not offer the three styles to such a cell unless
every other quota is already spent.

Every canonical spelling reads back through the shipped
`parsing.parse_number` as exactly the same binary64 and classifies as
`NUMBER` through `parsing.classify_number`. That is a property a test
asserts over the reference vectors, not an assumption.

### G6.3 The five alternate spellings

Let `sign` be the leading `-` of the canonical spelling (possibly
empty), and `body` the rest.

- **`leading_zero`, order k (k >= 1)**: `sign` + `k` copies of `0` +
  the POINT-FREE spelling's body. `00`, `000`, `0005` are this style.
  The supply is unbounded — one value has as many leading-zero spellings
  as a profile can ask for — which is why decision 8 chose this family
  and why capacity never binds a numeric column's raw distinctness.
- **`leading_plus`**: `+` + `body`, permitted only when `sign` is empty.
  There is no leading-plus spelling of a negative value; G6.4 says what
  happens when the counts ask for one anyway.
- **`decimal`**: the shortest round-trip digits written in fixed-point
  notation whatever `decpt` is, with `.0` appended when there would
  otherwise be no fractional digit. `5` becomes `5.0`; `1e+16` becomes
  `10000000000000000.0`.
- **`exponent_lower`**: the shortest round-trip digits written as
  `d[.ddd]e±XX` whatever `decpt` is, lower-case `e`, sign always
  written, exponent at least two digits. `5` becomes `5e+00`.
- **`exponent_upper`**: the same with `E`. `5E+00`.

The exponent pair is the ONLY place a numeric spelling carries case, so
it is the only construction that can make a numeric column's folded
count fall below its raw count (G6.5).

**The leading-zero family is available INSIDE every style but `plain`**
(P2-C2-F3). Owner decision 8 chose that family because it has no
ceiling and changes no type a reader infers, and decision 10 then made
the form of each cell a published fact. Revision 1 reached for the
family only where the assigned style was literally `leading_zero`,
which left a column reproducing a `decimal` or an exponent form with
one spelling of a value and no way to make a second: a profile
publishing thirty-six `decimal` cells, three raw identities and three
folded identities held one identity in the twin and named the loss.
Zeros written straight after the sign leave the contract's ladder
exactly where it was for the other four styles — a point keeps a cell
`decimal`, an `e` or an `E` keeps it in its exponent case, a leading
plus keeps it `leading_plus` — and the value each reads back as is
unchanged. So each of the five carries an **order k >= 0**, where order
zero is the style's own base spelling and each step writes one more
zero after the sign: `0.0`, `00.0`, `000.0`; `+5`, `+05`, `+005`;
`1e+05`, `01e+05`, `001e+05`. `plain` is the one style with no family,
because a zero in front of a plain spelling is what makes it
`leading_zero`, and a column whose whole map is `plain` therefore
reaches its published distinctness only as far as its different values
carry it (G12.8).

**A NAMED FIELD WIDTH SPENDS THE FAMILY, and this is the one bound the
family has** (plan P4-D14). Where `pad_widths` names a width, the cells
it counts are written AT that width: the order is not one, and not
whatever an identity walk asks for, but exactly the number of zeros
that makes the field the published width. Every further order writes
one more figure, so a value has exactly ONE leading-zero spelling at a
named width and the supply that "has no ceiling" above has, for those
cells, a ceiling of one. Two rules follow and both are normative:

1. **A width narrower than a value is never assigned.** A padded cell
   writes at least one zero in front of at least one figure, so a value
   needing `k` figures can wear only a field STRICTLY wider than `k`.
   Assigning it a field of `k` or less would lose figures the value
   needs, and padding must never move a value.
2. **The style is placed on values the widths can hold.** Where the
   style walk of G6.4 would give `leading_zero` to a value no published
   width can hold while a value that fits wears another style, the two
   cells EXCHANGE styles. The exchange is between two cells, so every
   published style count is unchanged. A PINNED CELL IS NOT SPECIAL
   HERE, either way round: what pins a cell is its value, a style
   carries no value, and `1` and `01` read back as the same number, so
   a published endpoint may give the padded style up and may equally
   receive it. The two guards that DO bind are the ones the styles
   themselves impose: there is no leading-plus spelling of a negative
   value, and no point-free spelling of a value that has none.

   **AND THE EXCHANGE RUNS IN BOTH DIRECTIONS** (landing 2b.7,
   2026-09-15; plan P4-D66.4). The sentence above moves the padded
   style ONTO a value a published field can hold; it must equally move
   it OFF a value no published field can hold. A cell left wearing the
   style is handed no width — a field narrower than the value is never
   assigned, by rule 1 — and the writer then writes one zero in front
   of a value that already fills the field. Measured: a column of month
   codes `01` to `12`, every real cell two characters and the census
   naming the one field `{2: 598}`, came back holding `012`, three
   characters in a two-character field, with `pads.published.2` MISSED.
   So after the widths are served, each cell still wearing the padded
   style whose value no published width can hold exchanges styles with
   the first cell, in ascending position, that is not wearing it, can
   wear it, and holds a value a published width CAN hold; the giver
   must be able to wear what it receives, as in the exchange above.
   **AND WHERE NO PARTNER EXISTS THE CELL GIVES THE STYLE UP ANYWAY**
   (landing 2b.16, 2026-09-16; plan P4-D105). That is the case where
   the twin drew fewer values narrow enough for the field than the
   census counts cells, so no exchange can mend it and the census
   cannot be met; a revision of this sentence left the cell wearing the
   style, and the writer then put one zero in front of a value that
   already filled the field. Measured: eight hundred five-figure postal
   codes at floor eleven, seed 7, publish `pad_widths {5: 85}`; the
   twin drew 84 values narrow enough, wrote `099613` — six characters
   in a five-character field — and missed `pads.published.5` at 84 all
   the same. **The census is missed in both writings; what differs is
   the cell.** Reaching for the value instead is closed off by the
   contract in as many words: a named field width is honoured by
   padding and never by adjusting a value, because `000123` and `123`
   read back as the same number and no rung, endpoint or statistic may
   be spent to reach one.

   **AND A PLUS DOES NOT HIDE THE PAD** (plan P4-D145, the final Codex
   review's item 6). The census counts a `leading_plus` cell whose
   figures begin with a redundant zero (contract C6-28b), so the widths
   are served in TWO TIERS: first every cell styled `leading_zero`,
   exactly as above, and then, from what each width still owes, the
   cells styled `leading_plus` whose value is whole and not negative,
   by the same narrowest-first, whole-value-first walk -- and the second
   tier pads no more cells in all than the census counts past the
   published `leading_zero` count (past the cells styled `leading_zero`
   where that form is not named), which is how many plus-signed padded
   cells the census holds: where the padded form falls short of its own
   share, a plus padded to make up the count would wear a spelling, `+01`,
   no cell of the source wore. A plus cell given a width is written with
   its zeros after the plus, `+` and then the field, and wears no mark; a
   plus cell given none is written as before. The fallback that hands an unplaced cell the narrowest
   published width it can wear reaches `leading_zero` cells alone,
   because only they are padded by their form. Measured before the
   second tier: 800 keys written `+` and twenty figures, at a floor of
   eleven and seed 1, published `field_widths {"20": 800}` and the twin
   wrote every one of them as `+` and eighteen figures.

   So the cell takes, instead of the padded style, the point-free form
   the published map carries MOST OF — `plain` before `leading_plus`
   where both are worn the same number of times, which is the
   enumeration order every other tie here is broken by — and a form no
   cell of the column wears is never offered, because writing one would
   invent a spelling the description does not publish. Where the map
   carries no other point-free form at all, every cell of the column
   being padded, there is nothing to give the style up to and the cell
   keeps it.

   **WHAT THIS COSTS IS A FORM COUNT, AND G13's RECOUNT NAMES IT.** The
   exchange above moves no count; this gives one cell from
   `leading_zero` to `plain`, so the styles map — which is
   EXACT-OBSERVABLE against the identity of contract 7.5.7 — is missed
   in the clauses that identity states, beside the width census that
   was already missed. Measured on the same column: one obligation
   missed before this rule and five after it, every one of the five
   naming the same single cell, and no cell of the twin wider than the
   field its description publishes.

Placing the counted cells into the published widths is a packing
problem and this method fixes a WALK rather than an optimum. The walk
is stated to the byte, because two implementations agreeing on the
census and differing on the order write different files:

- the published widths are served in ASCENDING order, narrow fields
  first, a value that fits a narrow field fitting every wider one;
- within one width, the cells are taken in ASCENDING CELL POSITION,
  each cell taken if its value needs strictly fewer figures than the
  field and the width's count is not yet spent;
- THE UNIT IS THE CELL AND NOT THE VALUE. One value may wear several
  published widths, and must be able to: a column publishing widths
  two, three and four over the single value 1 is a column whose source
  wrote `01`, `001` and `0001`, and whose three different spellings are
  published because of it. Holding such a value to one width collapses
  the census and the spelling count together;
- a cell no count can hold takes the NARROWEST published width its
  value can still wear, over that width's count. Only where no
  published width can hold the value at all is the cell written at its
  own value's width;
- and in the exchange of rule 2 above, the published widths are walked
  ascending, the cells that may receive the padded style are walked in
  ascending position, and the cell that gives it up is the first in
  ascending position whose value the width in hand cannot hold.

A width the walk cannot fill is reported by G13's recount rather than
passed over.

### G6.4 Which cell gets which style

`numeric_styles` publishes a count per style, plus a withheld remainder
(a style used by fewer rows than the small-cell floor is pooled, exactly
as a rare label is). **A pooled cell is written by its own value**: in
the `plain` style where the value has a point-free spelling, because
that is the style that changes nothing a reader infers, and in the
value's own canonical text (contract 3.2.1) where it has none. The
report names how many cells the remainder covered and how many of them
had no point-free spelling.

**AND CELLS ARE HELD BACK FROM THE POINT-FREE WALK SO THAT BOTH THE
COLUMN'S TYPE AND ITS `plain` FLOOR SURVIVE** (residual R-P4-69). Two
duties, and they are not the same one:

- **the type.** A column publishing `integer_valued: false` whose twin
  holds a whole number in every cell re-describes as `count`, and every
  downstream reading of it is then a reading of a different kind of
  column. ONE cell is owed a value with a point in it whatever the style
  census says. The pooled count is only one road to losing it: a
  description with no pool at all may name a `decimal` quota whose cells
  the twin then writes `1.0`, whole-valued in every cell with the form
  map still met exactly.
- **the `plain` floor.** Where `plain` is a NAMED count, every cell that
  can be written point-free is written `plain` by the rule above, so the
  cells carrying a point number exactly the pool: `r(plain) = p(plain) +
  R - D`, where `R` is the pooled count and `D` the cells carrying a
  point. G13's recount asks that `r(plain)` lie between `p(plain)` and
  `p(plain) + R`, so `D` must not exceed `R`. Where `plain` is NOT a
  named count the arithmetic is a different one — a pooled cell may
  perfectly well be point-free, as `060` and `11` are in a column whose
  only named style is `leading_plus` — and only the type is owed.

The cells are held back on the NARROWEST strata the ladder has, after
the step that pulls two strata apart, and a stratum wider than the count
still wanted is passed over rather than overshot: a cell written with a
point that the description did not pool is a `plain` floor missed just
as surely as one written without. The one exception is the type, which
is not a count and is not traded for an exact fit: where no stratum
fits, the narrowest there is NARROWED TO A SINGLE CELL, the neighbour
it already touches taking the rest, and that one cell carries the value.
Taking the stratum whole instead spends a `plain` floor that was
reachable — a 200-row column of two `0`, one `0.5` and 197 `2` is
allotted strata of 2, 2 and 196 and its pool is one cell, so the whole
two-cell stratum missed an achievable `plain: 199` by one. Dividing the
stratum in place and keeping both its values would buy the floor with
the count of different values instead, which is published too; moving
the spare cells to a neighbour writes a value the twin was writing
anyway and moves neither. A pinned end may TAKE those cells — what is
pinned is its value, not how many cells hold it — and on a column of
three strata the ends are the only neighbours there are. The value it takes
is chosen by the rule of G6.4's exchange above, so it stays inside its
own share and on its own side of zero.

**A SHORTFALL IS G13's TO NAME.** Where the walk cannot bring the cells
carrying a point down to the pool — the search is cheapest at each step,
which is not cheapest over the column — the recount names `plain` short
of its floor, and no separate note is written beside it.

**This amends the rule that wrote every pooled cell plainly** (Phase 3
plan P3-D8.1, 2026-08-12, closing the registry's open P2-C5-F3). A
published `min` or `max` carrying a decimal point has no point-free
spelling, and both ends are EXACT-OBSERVABLE, so a column whose
remainder covered such a cell owed a form no conforming generator could
write. Nothing published moves: the amendment gives the anonymous
remainder — which names no form at all, that being what pooling MEANS —
a spelling its own cells can carry.

**The recount is therefore the identity contract 7.5.7 states**, whose
clauses are these, with `r(s)` the recount, `p(s)` the published count,
`R` the remainder and `NW` the written numeric cells with no point-free
spelling: `leading_zero`, `leading_plus` and `exponent_upper` exact;
`plain`, `decimal` and `exponent_lower` never below their published
counts; the spill `D = max(0, NW - p(decimal) - p(exponent_lower) -
p(exponent_upper))`; `r(decimal) + r(exponent_lower) = p(decimal) +
p(exponent_lower) + D`; `r(plain) = p(plain) + R - D`; and, in each of
`decimal` and `exponent_lower`, at most `p` of its cells carry a text
that is not the canonical text of their own value, so a pooled cell can
never be re-spelled into a form the description never named. `NW` is
read off the VALUES and never off the spellings — the count of written
numeric cells whose value has no point-free spelling — because counting
the cells WRITTEN with a point would let a twin inflate its own `D` and
balance the arithmetic against itself. No cell text falls outside the
six styles, so there is no "outside the published styles" bucket for the
remainder to be counted in.

Styles are assigned over the K numeric cells in the fixed **stratum
order** of G5.2 (which is the sorted order of the values), by
**largest-remaining-quota**:

```
remaining[style] = the published count of that style,
                   plus the withheld remainder added to `plain`
pool         = the withheld remainder still standing inside
               remaining[plain], capped at it
carriers[i]  = how many cells from i onward can wear a point-free
               style; plus_carriers[i], how many of those are not
               negative
for each cell, in stratum order, and within a stratum in ascending
cell index:
    consider only the styles this cell's value can wear (below) whose
        remaining count is above zero -- and, where the point-free
        claims still standing outnumber carriers[i + 1], `plain` is
        offered to a cell that can wear no point-free style too,
        while the pool is still standing, spending one pooled cell
        and writing it in the value's own canonical text.  Among
        the styles offered, consider only those whose
        choice leaves
            remaining[leading_plus]        <=  plus_carriers[i + 1]
        after the choice is taken.  Write
            owed = remaining[plain] + remaining[leading_zero]
                     + remaining[leading_plus], after the choice
            named = owed  minus the pool still standing after the
                     choice
        and take the FIRST of these four that offers a style:
        1. the largest remaining count among the styles whose choice
           leaves  owed <= carriers[i + 1];
        2. the largest remaining count among the styles whose choice
           leaves  named <= carriers[i + 1];
        3. the largest remaining count among the POINT-FREE styles
           this cell can wear, and G12 names the miss;
        4. the largest remaining count this cell can wear at all,
           and G12 names the miss;
    ties are broken by the enumeration order
        plain, leading_zero, leading_plus, decimal,
        exponent_lower, exponent_upper;
    decrement its remaining count, and where the style taken is
        `plain` and the pool is still standing, decrement the pool
        first.
```

**Why the second answer exists** (P2-C4-F3). The pool is the count of
cells whose form the description WITHHELD: it says how many there were
and never which of the six they were, so a pooled cell is written
plainly wherever its value has a point-free spelling, because plain
changes nothing a reader infers, and in the value's own canonical text
where it has none (P3-D8.1). Where the point-free cells cannot carry
every quota, something has to give, and it is the anonymous claim that
gives — never a count the description names. A column publishing
twenty-five `leading_zero` cells and a pooled remainder of ten, on a
ladder whose two ends carry points, has thirty-three point-free cells
for thirty-five claims: it writes all twenty-five named `leading_zero`
cells, eight pooled cells plainly, and the remaining two in their own
values' canonical text — every cell has a spelling and no named count
moves. Answer 1 alone spent the shortfall on both claims at once and
missed the named count by one.

**Why the third answer exists.** Reaching it means the point-free
counts cannot all be placed however the rest of the column goes. Every
cell that can wear a point-free style must then wear one, because a
carrier spent on a form any cell could have worn makes the shortfall one
cell worse than the column's own values force — and the shortfall is a
published count. So answer 3 offers only the point-free styles, and
answer 4 is reached only by a cell that can wear none of them. **This is
what makes the miss the values' own size and not the placement's**: on
every description this method's battery reaches, the cells written
point-free are exactly the cells whose value HAS a point-free spelling.

**What "this cell's value can wear" means, in full** (P2-C1-F8,
P2-C2-F2). Revision 1 gave one example — a leading plus on a negative
value — and called it the only one. It is not. A cell's style is not a
label the generator keeps beside the cell: it is what the contract's own
first-match ladder (contract 7.5.4) makes of the text the twin finally
writes, because that ladder is what the recount from the CSV runs. So a
style can be given to a cell only where the finished text would classify
back as that style:

- **`leading_plus`** needs a value that is not negative.
- **`plain`, `leading_zero` and `leading_plus`** need a value with a
  POINT-FREE spelling (G6.2) — a WHOLE value, at any width (owner
  decision 10; the fixed-point window this clause used to name governs
  the canonical spelling and not this one). `12.5` has none; inserting
  zeros or a plus in front of it leaves the point exactly where it was,
  so `012.5` classifies as `decimal`, not as `leading_zero`. `1e+16` and
  `1e+20` DO have one — their digits — which is what keeps a column of
  wide whole numbers reading as whole numbers.
- **`decimal`, `exponent_lower` and `exponent_upper`** can spell any
  finite value.

**The look-ahead is part of the rule, not an optimisation** (P2-C2-F2).
Largest-remaining alone spends a cell that could have worn a point-free
style on a form any cell could have worn, and the quota then arrives at
the end of the column with nothing left to carry it. The two conditions
above are exactly what stops that, and together with the values step
below they make **every producer-feasible style map come out exactly**.

**The VALUES step, taken before the styles** (P2-C2-F2). The map and
the values are one question: a `plain` quota needs cells whose values
are whole, and on a column publishing `integer_valued: false` the
ladder hands back values that mostly are not. So, before styles are
assigned, take `W` and `W_plus` from G5.2's carrier step — they are the
same two numbers the split was made to serve. The walk is taken twice,
in the order the carrier step uses and for the same reason: first over
the strata that are not negative until the cells they cover reach
`W_plus`, because a plus needs a value that is not negative as well as
one with no point, and then over every stratum until the cells they
cover reach `W`. Where `decimal_plus` names a count D above nought, a walk over the negative strata alone comes between the two, until the negative cells carrying a point-free spelling reach `W - max(0, F - D)`, F being the cells that are not negative: at most `F - D` of those may be point-free once D of them keep a point, so the rest of `W` must stand on negative values (the verification of landing 2b.2). Without the first pass a walk could cover `W` entirely
out of the negative band and leave a published `leading_plus` count
with nowhere to go. Each pass counts the cells whose stratum value
already has a point-free spelling and, while that count is below its
demand, walks the strata in ascending order and gives the FEWEST of
them whole values that the shortfall needs, taking each stratum's value
to the nearest whole number by the rule of G5.4. Two strata are never taken: the two pinned
ends, which hold the published ends of the ladder. Three further rules
bound which whole number a stratum may take, and none of the three may
be traded for a style: it never crosses zero, so `n_zero` and
`n_negative` are untouched; it is never a whole number another stratum
already holds, so the count of different values does not fall; and it
is never outside the published `min` and `max`. **That third rule is
not decoration** (P2-C4-F3): G5.4 rounds a tie toward positive
infinity, so a stratum whose value interpolated to `88.5` rounds to
`89`, and on a column whose published `max` IS `88.5` that puts a value
above an EXACT-OBSERVABLE end of the ladder. The step below takes `88`
instead. Where a stratum can take no whole number under all three, it
takes none, and the point-free demand is short by that stratum's cells.

**Where the nearest whole number is another stratum's already**
(P2-C4-F3), the stratum does not give up the published form: the walk
steps one unit at a time, `+1`, `-1`, `+2`, `-2`, and takes the first
whole number that meets all three rules above and lies within HALF A
UNIT of the stratum's own share of the ladder — the closed interval
from `Ladder(c[s]/K)` to `Ladder((c[s]+g[s])/K)`, read by G5.6's own
piecewise-linear rule, widened by `0.5` at each end. The walk is
bounded at `S + 1` steps, because at most `S` values are already held.
Revision 1 skipped such a stratum, which lost a published count on the
commonest shape there is: a column whose most frequent value IS its
published `min` gives the ladder a flat lower half, so the interior
stratum rounds onto the pinned end's own number. A value inside the
stratum's own share costs G5.6's window nothing at all, because that
window already bounds a rank by the width of the stratum covering it;
half a unit outside it is exactly what the NEAREST candidate can
already cost, and G12.2 widens for that half unit and no more. Revision
2 held the stepped candidates to the share ITSELF, which bought that
window nothing and lost a form: a 39-cell producer column whose ladder
is flat at `18` gives the flat stratum that number, and the stratum
just below it — whose share stops AT `18`, and whose own `17` sits a
fraction below the share — was left with no candidate at all on the
seeds where its value rounded up.

**A candidate outside the stratum's own share is refused where a LATER
stratum's share holds it** (P2-C5-F3). Two neighbouring strata can
reach one whole number, the earlier from outside its share and the
later from inside its own, and which of them got it then turned on a
drawn value rather than on anything the description publishes: a
54-cell producer column publishing 26 point-free cells wrote 26 on some
seeds and 20 on others. The refusal costs the earlier stratum nothing
it was owed — every whole number of its own share, and every one within
the half unit that no later stratum's share holds, is still open to it
— and it leaves the later stratum the only number it has.

**REVISION 3: A NUMBER ANOTHER STRATUM HOLDS IS ASKED FOR RATHER THAN
PASSED OVER** (residual R-P4-69). Only so many whole numbers lie between
a column's published ends, so where the ladder asks for more strata than
there are whole numbers to give them, some stratum keeps a value with a
point in it whatever the walk does. WHICH stratum is a choice, and the
rules above left it to arrival order: a 36-cell column holding 34 whole
numbers and two halves, publishing `plain: 34` and a pool of 2, gave its
two single-cell strata `2` and `8` before the four-cell strata either
side of them could, so the twin wrote 28 point-free cells against a
published floor of 34 — or, where the walk was given every cell, 36 of
them, losing both halves so completely that the twin re-described as a
column of COUNTS.

Where a stratum can take no whole number under the three rules above,
the walk asks each stratum that is HOLDING one, in ascending order:

- a number two strata are both holding is never asked for, because
  moving one of them frees nothing;
- the holder is asked to find a whole number of ITS OWN, under exactly
  the three rules and the share rule above, with the number being asked
  for still counted as held. That question is the same one, so it
  repeats, and a stratum already visited on the chain is not revisited;
- a holder that can find none gives the number up only if it covers
  FEWER cells than the stratum asking, and takes in exchange a value
  with a point in it drawn from its OWN share, by the rule below;
- of every answer the holders give, the walk takes the one leaving the
  fewest CELLS carrying a point, ties going to the lower stratum. This
  is not decoration: taking the first workable answer ended a chain at a
  three-cell stratum where a single-cell one stood two steps further
  along, on 85 seeds in 200 of the column above.

A stratum that has given a number up is not asked again in this
column's walk, so a later stratum cannot undo the exchange. The walk
over the strata REPEATS until a pass moves nothing, because giving one
stratum a whole number frees the one it was holding, and the number of
passes is bounded by the strata.

**THE CHAIN IS BOUNDED IN DEPTH AND IN WORK, AND THE WORK IS BOUNDED
OVER THE WHOLE COLUMN.** A conforming implementation must cap both: the
chain's length, because a column may be allotted more strata than an
implementation can nest that question for, and the strata examined,
because asking every holder for its cheapest answer explores every
simple chain and that count is not linear in the strata. The work cap
is spent ACROSS the column and not renewed for each question, because
the walk asks one question per stranded stratum per pass and a
per-question cap therefore bounds no total at all: measured on a
482-cell column of 242 strata, a per-question cap cost 15.8 seconds
against 5.2 with the chain withdrawn, and shared it costs 5.4. A search that reaches either cap
gives back the best answer it has found, which is a stratum keeping a
value with a point in it — a cost G13's recount names — and never a
different answer. The caps are an implementation's own, and two
implementations that both reach them may differ; a description whose
walk reaches them is one whose twin the report already says is
approximate.

**A GRAIN INSIDE A ROLE IS LAID OUT BY ITS OWN COUNT OF DIFFERENT
NUMBERS** (residual R-P4-112, closed; G5.2's grain rule). An affixed
core and a joined position are handed to this method as columns of
their own, and the division of cells into strata reads
`n_distinct_values` from the grain's OWN quantitative block. The
counts the block arrives with answer a different question for those
roles: a 36-row column of `N/M` holds 36 different CELLS while its
first position holds 11 different numbers, so reading the column's
count divided that position into 36 strata where a plain column
carrying the same numeric facts is divided into 11.

**THE SPELLING BUDGETS OF G6.5 DO NOT MOVE WITH IT**, and they took the
grain's count for one revision before review found what that costs. A
budget bounds how many different SPELLINGS the twin may write, and a
count of NUMBERS cannot buy the second way of writing one number: a
column of `01/5` and `1/5` publishes two different cells whose first
position holds one number. Measured on 300 cells holding sixty values
each written plainly and again with a leading zero — 120 spellings over
60 numbers — at forty seeds, the twin held 55 to 60 of the 120 with the
budget at the grain's count and holds 81 to 97 with it on the block's.

**THIS PARAGRAPH SAID THE OPPOSITE OF BOTH UNTIL 2026-09-01**, naming
the grain rule a recorded LIMIT and the repaired behaviour
nonconforming. It is superseded: a conforming implementation divides by
the grain's count and budgets by the block's.

**THE VALUE A STRATUM TAKES IN EXCHANGE** is chosen from its own share
of the ladder, so the stratum stays where the ladder put it, and is
never a value another stratum holds. The share is first cut back to the
stratum's own side of zero — the rung above a column's last negative
value is a positive number, so the share of the stratum just under zero
STRADDLES zero, and a column of four `-4.5` cells whose negative stratum
was handed `2.097` came out holding one negative cell against a
published four. The middle of the cut share is taken where it has no
point-free spelling; where the middle IS whole, the value is the middle
plus a step of at most half a unit, which cannot be whole WHEREVER THAT
STEP IS REPRESENTABLE, the step halving again only to move around a
value another stratum holds — and
each step is tried BOTH above the middle and below it. **Halving alone
is not enough, and neither is halving upward**: eight halvings of a
share `(1, 257)` are `129, 65, 33, 17, 9, 5, 3, 2`, every one whole, and
`(1, 2)` with the middle and every upper step already held leaves `1.25`
free below. An implementation that gave up in either case passed the
stratum over in silence.

**AND ABOVE ABOUT TWO TO THE FIFTY-THIRD THERE IS NOTHING TO FIND.**
The gap between one representable number and the next is more than a
whole unit there — at two to the fifty-fifth it is eight — so every
number a share up there can hold is whole, and a column of such numbers
publishing `integer_valued: false` has nowhere to put a value with a
point in it. The twin then writes whole numbers throughout and
re-describes as a column of COUNTS.

**THE OWNER'S RULING BOUNDS THAT OUTCOME, AND THE BOUND IS
ARITHMETIC** (amendment A-P4-48, closing residual R-P4-117).
`integer_valued` is EXACT-OBSERVABLE and stays so; it falls back to
REPORT-ONLY — not APPROXIMATED, because a boolean has no window to
approximate INSIDE, only a fact the twin either holds or names — where
no stratum that MAY take a value has a share holding a number a double
can represent with anything after the point.

**THE CONDITION IS OVER THE SHARES AND NOT THE PUBLISHED ENDS** (round
5, item 2). A column may run from `1` to two to the fifty-fifth, holding
countless fractions between those ends, while every stratum that may
take a value sits high above them: the ends bound the ladder, the shares
bound what a value may BE. The arithmetic edge is exact — the gap
between one representable number and the next reaches a WHOLE UNIT at
two to the fifty-SECOND, about four and a half quadrillion — and the
search walks in from both ends of a share rather than probing its
middle, because on a wide share the values with a point in them live at
the LOW end and the middle is the worst place to look. Round 5 built a
column whose middle stratum ran from about 3.6 to 7.2 thousand million
million: the middle of it is whole in every direction, and
`4053239664633446.5` sits inside it. The twin keeps its type there now
and names nothing.

This method does not grant that outcome by writing it down — an earlier
revision said the outcome was "permitted", which a sentence cannot do.
The plan grants it, the registry carries the authorization, and the
twin still NAMES `integer_valued` as a fact it could not meet, so a
reader meets the changed type in the report rather than by measuring
the twin.

**A quota that cannot be placed is a MISS, and naming it is not a
licence to leave it unplaced.** Where a quota's own cells exist, an
implementation that fails to put them there is defective, not
approximate. G5.2's carrier step and the two answers above are what
make the cells exist: the split gives way before a published count
does, and the anonymous pool gives way before a named count does.
**The remainder leaves no shape a producer writes** (Phase 3 plan
P3-D8.1): what a producer could once cost THROUGH THE POOL is placed
exactly now, because a remainder names no form and is spelled by its own
cells' values. **That sentence was too strong, and residual R-P4-69 is
the producer-written shape it missed**: a 36-cell column of 34 whole
numbers and two halves publishes `plain: 34` with a pool of 2, and the
pool is exactly the two halves. Its twin lost them — every cell whole,
the column re-describing as `count` — because the point-free walk was
asked for the plain count AND the pool, a pooled cell being written
plainly wherever it can be. The hold-back above is what places it, and
what remains is bounded rather than absent: measured on that column over
200 seeds, 182 write the published count exactly and 18 run over it and
are named by the recount (residual R-P4-111). **One producer-reachable shape survives, and it is not
the pool's** (review item P3-C2-F1): a column whose values are whole but
lie outside the fixed-point window of G6.2 is published `plain` by a
source that wrote it in figures, while the twin writes it with a
decimal point, so the plain count is missed and the spelling is named
beside it. That is the
window's own cost, it predates this repair, and the Phase 3 plan carries
it as a defect for the owner rather than as a disposition this method
grants. This method grants
`numeric_styles` no lesser outcome anywhere, and the shapes listed
below are reached only by a hand-written description whose own facts
contradict each other — the same class of document G12's refusals
settle, listed here because the walk answers them rather than stopping:

- a `leading_plus` quota larger than the column's own count of
  non-negative cells. No producer emits one — a cell it read as
  `leading_plus` was not negative — so this shape needs a hand-edited
  description whose own facts disagree.
- a NAMED point-free demand larger than `K` minus the cells the
  published ends force to carry a point. At least one cell must read
  back as `min` and one as `max`, both EXACT-OBSERVABLE, so an end that
  has no point-free spelling costs one cell of the demand. **No producer
  reaches this shape**: the named counts alone can never exceed that
  ceiling, because the source's own end cells were not written
  point-free either, so it takes a hand-written description whose facts
  disagree with each other. The twin writes the largest number of
  point-free cells the published ends leave, which is the most any
  conforming generator can write, and names the miss.

  **The producer-reachable half of this shape is CLOSED** (Phase 3 plan
  P3-D8.1, closing the registry's open P2-C5-F3). A producer reached it
  only through the anonymous pool, where it was the conflict between
  `min`/`max` exactness and the withdrawn rule that every pooled cell is
  written `plain`. A pooled cell names no form, so it is now spelled by
  its own value and there is nothing left to miss: measured over the
  producer battery of 240 descriptions at eight seeds, the eight columns
  that filed such a line file none.
The third shape revision 2 listed here — a stratum whose own share
holds no whole number free for it — **is no longer one of them**
(P2-C5-F3). Where a band's strata all sit on fractions the strata
themselves move: G5.2's reach step gives one of them a window of the
ladder that reaches a free whole number. The 82-cell producer column
that shape was written for reproduces its published `34` and `48`
exactly, on every seed.

Largest-remaining rather than a block per style, and the reason is
fidelity: a block assignment would put every exponent-styled cell at one
end of the distribution, so a reader of the twin would find style
correlated with magnitude where the real column had no such pattern.

**Except where one form per stratum is what the spelling count leaves
room for** (P2-C5-F3). Two styles inside one stratum write one value
two ways, so they cost a spelling, and a column with as many strata as
it has published spellings — which is the ordinary case, since `M` is
`min(K, F_num)` — has no room for that at all. The cell walk above then
meets `numeric_styles` by missing `n_distinct` and `n_distinct_folded`,
which is one published count bought with another. So where the walk's
own answer would spend more spellings than the column has, the styles
are packed over whole STRATA instead, by the same complete rule G9.5
states: every style quota is met exactly whenever any assignment of
whole strata meets them all, and each stratum keeps one form. It is
reached for only there, and where no such assignment exists the walk's
answer stands.

**AND A VALUE NO NAMED FORM CAN WRITE IS OWED FROM THE FORM THE RECOUNT
COUNTS IT INTO** (plan P4-D235). Since P4-D222 a form fewer cells than
`parsing.census_floor` wrote has no key of its own and its cells are
counted into the commonest named form, so a column whose published
forms are ALL point-free may still hold a value with no point-free
spelling — a published minimum of `-20.5` beside padded and plain whole
numbers. The twin writes that cell in its own canonical text, and when
the twin is described again the cell is counted into the commonest
named form. The packing therefore lets such a stratum wear THAT ONE
form, and no other, and gives the packing up where more cells would be
owed from it than `parsing.absorbed_room` says it can take in. The rule
is asked only where the published map names NO point-carrying form: a
map that names one must have those cells wear it, and a cell more would
move that form's own printed count. Without it, thirty-three point-free
cells claimed over thirty-two carriers made the placement give up a
NAMED count instead: a 33-cell column of one `-20.5`, ten `-20`, twelve
`00`, four `1`, three `6` and three `9` at a floor of eleven publishes
`{"leading_zero": 12, "plain": 21}` and its twin wrote ELEVEN padded
cells, missing `leading_zero`, `plain`, the remainder and
`pads.published.2` at exit 3.

**Which supply, against which ceiling** (R-P4-55). "More spellings than
the column has" is TWO tests and not one, because a split does not
always cost both published counts. Take the distinct pairs of VALUE and
STYLE the cell walk leaves standing: how many there are is the column's
RAW supply, and it may not exceed `R_num`. Fold `exponent_upper` onto
`exponent_lower` and count the distinct pairs again: that is the FOLDED
supply, and it may not exceed `F_num`. The strata are packed only where
one of the two ceilings is passed.

Charged the other way round -- the raw supply against the folded
ceiling -- this exception refuses the one construction G6.5 names for
reaching a raw count above a folded one. The exponent case pair is two
raw spellings of one folded identity, so it costs `R_num` a spelling
and costs `F_num` nothing; one form per stratum makes the pair
impossible. A column publishing `n_distinct` one above
`n_distinct_folded` therefore had the pair packed away and came out one
raw spelling short of a count it could have met exactly. That column is
`numeric_decimal_styles`, and it is a committed vector, which is how
the disagreement was caught: the reference implementation of this
section wrote the pair and the shipped one did not.

### G6.5 Reaching `n_distinct` and `n_distinct_folded`

Raw `n_distinct` counts different SPELLINGS over all present cells;
`n_distinct_folded` counts different folded identities, where folding is
trimming then Unicode `casefold`, as the shipped `parsing.folded` does.
A numeric column's present cells come from four classes, and different
classes never share a spelling (G10 constructs them so).

**Budget allocation across classes**, in this fixed order:

```
classes, in order:  numbers (K cells), out_of_range (O),
                    contradictory (C), not_numeric (N)
```

1. Every non-empty class receives one spelling. If `n_distinct` is
   smaller than the number of non-empty classes, the published facts
   cannot hold together: raw distinctness becomes REPORT-ONLY for the
   column, the twin uses one spelling per class, and the report names
   both counts.
2. The remainder of `n_distinct` is offered to the classes in the order
   above, each taking as much as it can use (never more than its own
   cell count), until the remainder is spent. The same allocation is
   made for `n_distinct_folded`. Call the numbers class's two shares
   `R_num` and `F_num`.

**Inside the numbers class**, with `M = min(K, F_num)` different values
already fixed by G5.2:

- The `M` stratum values each contribute their own spelling.
- `F_num - M` further FOLDED spellings are needed. Each is supplied by
  raising the leading-zero ORDER of a cell whose base spelling repeats
  an identity already written — inside whatever style G6.4 gave that
  cell, since every style but `plain` carries the family (G6.3). A
  stratum of size `g` can carry `g - 1` alternate spellings, and the
  total capacity `K - M` is always at least `F_num - M`, because
  `F_num <= K`.

  **How many zeros are spent is decided over the WHOLE column first**,
  not cell by cell. Count the identities the column's base spellings
  already hold; the shortfall against `F_num` is how many cells raise
  their order, and no more. A cell cannot tell from where it stands
  whether the identities still to come will cover the count on their
  own, and spending a zero that was not needed carries the count PAST
  the published one — a miss in the other direction, and just as
  visible to somebody grouping rows by the column. Cells are visited in
  the order of G6.4, and each that raises its order takes the lowest
  order whose folded identity is new.

  **A cell at a named field width does not raise its order** — every
  order writes one more figure (G6.3) — **so before any zero is spent,
  padded cells TRADE THE PLUS** (plan P4-D145 as amended by the repair
  pass of the final Codex review). Measured before this paragraph:
  1,200 offsets written `+0123` or `0123` at a floor of eleven publish
  917 spellings of 706 values at one width of four figures, and the
  twin, whose styles left most values in ONE of the two padded forms,
  held 776 and 768 spellings at seeds 1 and 4. A cell may trade where it
  is allocated `leading_plus` or `leading_zero`, stands at a named field
  width, wears no mark and no signed-decimal plus, and holds a whole
  value that is not negative. At one width a value's such cells are
  counted by form, and a trade turns one `leading_plus` cell of one
  value into `leading_zero` and one `leading_zero` cell of another value
  into `leading_plus`, the value's first such cell in cell order in each
  case — so no form count and neither width census moves. Three walks,
  each over the widths ascending and, within a width, the values in the
  order of their first cell: (1) while at least two identities are
  owed, the k-th value written only with a plus by at least two cells
  trades with the k-th value written only with a zero by at least two
  cells, both lists taken before the walk, adding two; (2) while at
  least one is owed, each value written only with a plus by at least two
  cells trades, in order, with the first value in a list taken before
  the walk that has a plus cell and still has at least two zero cells —
  a value that no longer has two is passed over for good — adding one;
  (3) the same with the two forms the other way round. No trade takes
  from a value the only cell of a form, so no spelling is lost.
  **Measured after:** 917 spellings at both seeds, every width kept.
- `R_num - F_num` further RAW spellings are needed, and each must fold
  onto a spelling already used. The only construction that does this in
  a numeric column is the exponent case pair: a value written
  `exponent_lower` and the same value written `exponent_upper` are two
  raw spellings of one folded identity. Each such pair therefore
  consumes one `exponent_lower` cell and one `exponent_upper` cell out
  of the quotas of G6.4.
- Where the published style counts do not supply enough exponent cells
  to make `R_num - F_num` pairs, the twin's folded count comes out equal
  to its raw count for those spellings; raw and folded distinctness then
  fall inside the two-sided envelope rather than being exact, and the
  report names the profile's counts beside the twin's (P2-D6).

**Precedence, stated:** the published style counts are met first, and
distinctness is met within them. That is the order P2-D6 already
implies — `n_distinct` is EXACT-OBSERVABLE "using the spellings owner
decision 7 permits, falling back to the two-sided envelope only where
even those cannot supply the count" — and it is stated here so two
implementations cannot resolve the conflict in opposite directions.

### G6.5a Reaching `n_distinct_values`, the count of different NUMBERS

G6.5 above reaches the two counts of different SPELLINGS. This section
reaches the count of different numbers, which is a separate published
fact and is not met by spelling one number two ways. **The method
referenced this pass twice — G6.4's held-back pool and G6.6.5 both
order themselves against "the step that pulls two strata apart" — and
never stated it. Written here at review of the distinct-count landing.**

**Why a pass is needed at all.** G5.2 divides a grain into as many
strata as the block publishes different numbers and G5.3 gives each
stratum a value from its own share of the ladder. Two of those values
can be written as one cell: on a fixed-shape code column of 240 cells
at `NNN.N`, the ladder hands back `252.96704532913995` and
`253.02741326459255`, six hundredths apart, and at the published one
figure both are `253.0`. The carrier walk of G6.4 can cause it too, by
moving a stratum onto a whole number another stratum already holds.

**WHEN IT RUNS.** After G6.4's point-free carrier walk — which can
itself land two strata on one text — and before the held-back pool.

**WHICH GRID, and this is the clause the landing corrected.** The pass
acts only where every numeric cell of the column is written on ONE
grid, because only then does a value know what text it will wear:

- **where the column is `integer_valued`, the grid is the INTEGERS,
  whatever `fraction_widths` says** (landing 2b.7, 2026-09-15; plan
  P4-D66.3). The two facts answer different questions: `integer_valued`
  says every VALUE of the column is whole, and `fraction_widths` says
  how many figures each CELL writes after its point. A column a
  spreadsheet exported as `44.0` publishes both — every value whole,
  every cell one figure wide — and this clause used to reach the
  integers only for an EMPTY census, so such a column was read as
  being on the grid of TENTHS and this pass moved a stratum onto a
  value no whole-number column holds. Measured through the real reader,
  producer, loader, generator and validator on 800 whole counts written
  at one figure: 23 non-whole twin cells at seed 1 and 19 at seed 7,
  `25.6` and `30.6` among them, and the twin described itself again as
  a `continuous` column where the source was a `count` — `axes.role`,
  `axes.statistical_type` and `type.integer_valued` all MISSED. Whole
  amounts written at two figures were worse, 68 cells of 800. Which
  cell is written at which width is not lost by answering the other
  question: that is settled after the styles by G6.6, and what is
  settled here is the grid the VALUES sit on, which for a whole-valued
  column is the one G5.4's own rule already put them on;
- where `fraction_widths` names exactly one width and that width covers
  every numeric cell, the grid is that width — tenths, hundredths. A
  whole-number column carries no figure after the point, so it has no
  width to count and its census is empty — which an implementation may
  read as "no grid" and skip the pass entirely, which is why the clause
  above does not depend on the census at all;
- otherwise, where the census names widths at all, the grid is the
  FINEST of them (amendment A-P4-55): which cell gets which width is
  settled after the styles by G6.6, so a value cannot know here what it
  will be written at, but two values that read alike at the finest width
  ARE one number, so every collision seen there is real. A census that is
  empty on a column that is not whole-valued, or that holds a key that is
  not a run of figures, gives no grid and the pass does not run.

**A COLUMN THAT WRITES SOME CELLS WITH NO POINT KEEPS ITS WHOLE VALUES
WHOLE** (amendment A-P4-55): where the census counts fewer cells than the
column has numeric cells, a stratum whose value is whole moves only onto a
whole grid point, and one whose value is not only onto a point that is not
whole, so the plain cells keep the whole values they need.

**WHICH STRATA MAY MOVE.** Only a stratum whose text is held by more
than one stratum — moving a stratum that collides with nothing frees
nothing. Never the first or last stratum, whose values are the
published `min` and `max`. Never the zero stratum, whose value is a
published count's whole reason for being there.

**A GRID WITH NO SPARE POINT IS FILLED, NOT WALKED** (plan P4-D147,
the final Codex review of the merge, item 6). Where the grid is the
INTEGERS, the column has exactly as many strata as the different values
it publishes, and the integers from the published `min` to the published
`max` number exactly that count, the strata are given those integers in
ascending stratum order, each once, and the walk below does not run. It
is the only assignment meeting the count, and it keeps both ends and the
order the ladder put the strata in. Where the stratum at some position
stands in a sign band its integer is not in — the zero stratum holding
anything but nought, a negative stratum a value of nought or more, a
positive stratum a value of nought or less — the fill is not taken and
the walk runs as it always did. Measured before this clause on 400 rows
of `+1.0` to `+400.0` beside a column of labels: every stratum that
walked landed on a point another stratum still needed, and the twin wrote
400 different spellings of 395, 392 and 391 numbers at seeds 4, 1 and 7
while the real table held 400.

**AND ON EVERY WRITTEN GRID, NOT ONLY THE INTEGERS** (plan P4-D176, the
final skeptic of the merged repairs). Where the grid is `f > 0` figures,
both published ends are points of it — each end's grid text at `f`
reads back as that end — and the points from `min` to `max`, counted in
whole grid units off the two grid texts, number exactly the count of
different values, the strata take those points in ascending order, each
once, under the same sign-band condition. Measured before this clause:
120 amounts `0.1` to `12.0`, with or without a decimal comma, held 119
numbers at seeds 4, 0 and 1.

**A COLUMN WHOSE PUBLISHED LEVELS ARE ITS STRATA TAKES THEM** (plan
P4-D178), where the fill above does not answer. Let `R` be the different
numbers the hundred and one rungs and the published `mode` name. Where
`R` holds more numbers than the count of different values, let `R` be
instead the numbers two rungs or more name, together with the two ends
and the `mode`: a rung on the boundary of two levels is interpolated and
names a number no cell holds, once. Where the column has exactly as many
strata as the count of different values, `R` holds exactly that many,
and every member is a point of the grid (a whole number on the integer
grid), the strata take the members of `R` in ascending order, each once,
and the walk below does not run — unless a sign band would not hold its
member, a stratum outside the zero band would take nought, or, on a
column whose styles map asks for any point-free cell (the withheld
remainder counting as `plain`), a stratum would change whether its value
has a point-free spelling. Measured before this clause over eight seeds
on 2,000 quantities of eleven levels and 1,423 discounts of six: six
twins of eight wrote a whole level at a number the source never held —
`7.4` 225 times, `1.3` 199 times — and lost a published rung, with
validation at exit 0.

**A SIGN BAND WHOSE OWN GRID HAS NO SPARE POINT IS FILLED IN ORDER**
(the carried numbers pass of 2026-09-18, amending plan P4-D147), where
neither fill above answers, and before the walk. It is asked only on a
column written on ONE grid — `integer_valued`, or one fraction width
covering every numeric cell — that has exactly as many strata as the
different numbers it publishes, and whose published `min` and `max` are
both points of that grid. For each of the two signed bands in turn,
negative and then positive, the band's POINTS are the points of the grid
from `min` to `max`, of the band's own sign, that lie strictly inside no
published `empty_edges` pair (a point on a pair's edge is outside it).
Where those points number exactly the band's strata, the band's strata
take them in ascending order, each once; a band with a spare point is
left as it is. The zero stratum never moves. On a column whose styles
map asks for any point-free cell, the whole rule stands aside where any
stratum it would fill would change whether its value has a point-free
spelling. The walk below then runs over the result as it would have run
over the strata. It is the only assignment that gives every stratum of
the band a number of its own standing in no stretch the description
calls empty, and a band can be full where the column is not: measured
before this clause on 388 positive amounts `100.00` to `103.87` beside
eleven accounting brackets and one `-12.25` at a floor of eleven, the
ladder's third percentile fell inside the published pair
`(-1.25, 100.00)`, three positive strata stood below 100, two of the
rest shared `101.88` with no free point within the walk's reach, G6.5
spelled the second one `0101.88`, and the twin held 400 spellings of 399
numbers at every seed tried while the real table held 400.

**IN WHAT ORDER.** The strata are visited in ascending index, ONCE
each in a walk, and a stratum a walk could not move is not returned to in
that walk. Which stratum is repaired first decides which grid points the
later ones find occupied, so the order is part of the answer and not an
implementation detail.

**HOW MANY WALKS, AND HOW FAR EACH REACHES** (amendment A-P4-55, plan
P4-D183). A walk has a REACH. At reach 0 a stratum is moved as the
paragraphs below state, inside its own share. At reach 1, where that finds
nothing, it is asked again with its share widened by the share's own width
on either side -- its neighbours' ground. At reach 2, where that too finds
nothing, it is asked a third time with no share at all and at most as many
grid steps as its share is wide, one more than the whole number of grid
units that width holds and never more than sixty-four, still inside the
published ends. A ROUND is a walk at reach 0, then a walk at reach 1, then
a walk at reach 2, the count asked after each; at most three rounds are
taken, and a round that adds no different value ends the pass. **Every
stratum is walked inside its own share before any is walked on wider
ground.** The three reaches were first tried stratum by stratum, and an
early stratum took a point beyond its share that a later stratum held
inside its own: on eleven whole numbers from 100 to 110 written three
times each, twenty-two strata publishing eleven values, the tenth stratum
walked from 104 onto 105, above the 104 of the stratum after it, while the
thirteenth stratum's own share held 105 -- and the reference oracle,
reading this section, wrote the other.

**THE MOVE.** The nearest free point of the grid inside the stratum's
own share of the ladder, walked outward one grid step at a time — the
step being one unit of the last place the width holds, so `1` on the
integer grid and `0.01` at two figures — and the LOWER of two equally
distant candidates taken first, so that two implementations reading
this text choose the same point.

**FROM WHERE, EXACTLY.** Not from the stratum's value, but from that
value's OWN GRID TEXT read back as a number. The two differ: a stratum
holding `1.25` on a grid of one figure is written `1.2`, and the
candidates are `1.1` and `1.3` rather than `1.15` and `1.35`. This
paragraph named the value until review round 1 of the integer-grid
landing, which is the wrong anchor and a byte-determining one.

**HOW FAR, AND THE STEPS ARE COUNTED ON THE GRID.** At most SIXTY-FOUR
grid steps out, where a step is ONE UNIT of the last place the width
holds and the count is of units, not of additions. A share wider than
that is not searched to its ends; the walk answers with nothing and the
stratum stays where it is.

**The distinction is not pedantry.** Adding `10 ** -figures` to a
double sixty-four times does not move sixty-four grid units: the
addition accumulates, and at eleven figures a candidate this rule
bounds at sixty-four units came back SEVENTY units from its anchor and
was taken. So the anchor is read as a whole number of grid units and
the step is added to THAT — by whatever arithmetic an implementation
likes, so long as sixty-four means sixty-four.

**AND A GRID POINT NO DOUBLE HOLDS IS PASSED OVER.** The stratum
carries a number, not a text, and the run re-spells that number when it
books the text the stratum took. Where a grid point's text does not
survive being read back and written again — which begins where the grid
is finer than the numbers near it, at eleven figures on a value in the
millions — the walk passes it by rather than recording one text and
writing another.

**WHAT IS TESTED AND TAKEN IS THE GRID POINT, not the sum that reached
it.** Stepping outward accumulates in binary: a tenth added to `0.2`
is `0.30000000000000004`, which is greater than `0.3`. Ask the bounds
about THAT and a candidate whose grid text is exactly the share's
inclusive upper end is refused by the end it sits on — which is how
this pass came to leave two strata written as one cell on a column it
was built for. So each step is snapped to its grid text first, that
text is what the written-text refusal reads, the number that text
reads back as is what the share, the ends and the sign band are asked
about, and it is what the stratum takes.

**WHAT IS REFUSED.** A candidate that is not a finite number; a
candidate whose text is already written by another stratum; a candidate
outside the stratum's share, whose two ends are INCLUSIVE; a candidate
outside the published `min` and `max`, inclusive likewise; and a
candidate that would cross into another sign band — the counts of negative, zero and positive cells are published
facts and no repair may move one. A stratum in the ZERO band answers
with nothing at once, without walking. So does a grid whose step is not
a finite number greater than nought, and a value whose grid text does
not read back as a number.

**WHERE THERE IS NO LADDER** — a column published without one — there
is no share and no published ends, so those two refusals do not apply.
The other three do: a candidate must still be finite, must still not
wear a text another stratum has written, and must still stay in its
sign band.

**WHEN IT STOPS.** As soon as the count of different texts reaches the
published `n_distinct_values`, and otherwise at the end of the rounds
above. A stratum for which every candidate was refused keeps
its value, and the push below is asked; what it leaves is G13's to name.

**A COLLISION THE WALKS LEAVE IS PUSHED ALONG ITS BAND TO THE NEAREST FREE
POINT** (the carried numbers repair pass of 2026-09-19, the repair
skeptic's first MAJOR finding). The walks move one stratum at a time and
at most as far as its share reaches, so a band with a free point is not
yet a band whose strata find it: where the band's strata stand on every
point of a long run but one, and two share a point far from the free
one, no single move reaches it. Measured before this clause on 300
negative amounts `-5.00` to `-7.99` beside 120 positive amounts drawn
between 10 and 900, at a floor of eleven: the description publishes 420
different numbers and no empty pair, the ladder puts the negative band's
last stratum at `-0.01`, and two of the rest shared `-5.90` eighty-nine
points from the free `-5.01` and `-5.00`. G6.5 then spelled the second
one `-05.90`, and the twin held 420 spellings of 419 numbers at every one
of ten seeds while the real table held 420; `validate` exited 3 on the
twin and 0 on the real table. Over 312 twins of 52 dense and skewed
columns, at two floors and three seeds each, 88 held fewer numbers than
published before this clause and 30 were MISSED by `validate`; with it,
none.

So, after the walks, on a column with a grid (WHICH GRID above) and a
published ladder, with exactly as many strata as the different numbers it
publishes, while the strata hold fewer different texts than that: a
band's POINTS are the grid points from the published `min` to the
published `max`, of the band's own sign, lying strictly inside no
published `empty_edges` pair, and a pair is stepped over to the first
point past its far edge. Take the LOWEST grid text two strata or more
hold, in a signed band, not yet found immovable. Its holders outside the
zero band, other than the first and last stratum, are the candidate
MOVERS, asked in turn: for a push downward the one of lowest position
first, for a push upward the one of highest position first. For a mover,
walk the band's points from the collision that way to the first point no
stratum holds -- on a column that writes some cells with no point, only
the points of the mover's own KIND, whole where its value is whole and
not whole where it is not, so that a free whole point is no destination
for a value that is not whole. Every stratum on a point passed on the
way moves one point of that kind toward the free one, and the mover
takes the first point past the collision. The push is refused for that
mover where the walk leaves the band first or reaches a point no double
holds, or where a stratum it would move is the first or last stratum, or
would change whether its value is whole (on a column that writes some
cells with no point) or has a point-free spelling (on a column whose
styles map asks for a point-free cell); the next mover is then asked. Of
the two ways, each with its first mover not refused, the one moving
fewer strata is taken, the DOWNWARD one on a tie. A collision with no way
is found immovable and the next is taken; the push ends when the count is
reached or no collision is left to take. Each push gives the column one
more different number and moves every stratum it touches by exactly one
point of its kind, so the sign counts, the pinned ends and every
published empty stretch stay as they were. What it cannot mend is a band
given more strata than it has points -- G5.2 divides the strata between
the bands by their cells, not by their different numbers, which the
description does not publish per band -- and that shortfall is named.

**WHICH OF THE THREE REFUSALS CAN DECIDE A PUSH, measured** (the skeptic
of the oracle's independence repair, 2026-09-19). Two of them never
decide a push the walk builds, and they are stated above only so that
the rule reads whole. The WHOLE refusal: on a column that writes some
cells with no point the walk visits only points of the mover's kind, so
every stratum it moves goes from a point of that kind to the next one,
and the refusal could fire only on a stratum whose value is not the
number its grid text reads back as, which no walk leaves. The END
refusal: the first and last strata stand on the published ends, and the
walk would have to pass an end to move one, so it could fire only where
they do not. The POINT-FREE refusal is the one that decides, and only on
a column whose styles map asks for a point-free cell while every numeric
cell has a published width, which is a map pooling a share below the
floor that G6.4 writes plain; there the walk takes points of either kind.
Measured on the oracle's push over 40,000 random draws of strata in
order with the two ends pinned and every value on its own text (28,723
of them asked the push): without the whole refusal and without the end
refusal no value moved, and without the point-free refusal values moved
in 482, every one of that shape. No frozen case is of that shape: the
one push a frozen case asks (`pushed_along_band`) makes five checks and
none refuses, in the oracle and in the generator alike. So the push
refusals are witnessed one call at a time in
`tests/test_oracle_rule_witnesses.py`, against the oracle's push and the
generator's alike: the point-free refusal holding a collision immovable,
the end refusal holding one whose first stratum stands above the
published `min` -- an input no published column produces, and the only
way that refusal can be reached -- and a push each allows, with four
registered mutants (each of those two refusals removed, every move
allowed, every move refused) each turning that witness red. The same
file holds the two refusals that cannot decide to moving nothing over
3,000 seeded draws of that shape.

**A WHOLE NUMBER THE COLUMN WRITES TWO WAYS IS HELD BY TWO STRATA** (plan
P4-D193, the final pass over the close of stage 2). A column whose numeric
cells are written at ONE fraction width `f` of one figure or more beside
cells written with no point, in the `decimal` and `plain` forms only, with
no field width, no mark between thousands and no negative notation, whose
strata are its spellings (`n_distinct` of them) and no fewer than its
numbers, spells a number that is not whole one way and a whole number at
most two ways (`4` and `4.0`); so `S`, the strata less the published count
of numbers, is how many whole numbers it writes both ways. On such a
column, straight after the walk above, where the strata's texts at `f` are
not SETTLED -- as many texts as the published count of numbers, every text
held by more than one stratum held by exactly two and naming a whole
number -- two steps are taken, in order:

1. **The fill.** Let `P` be the grid points from the published `min` to
   the published `max`, both ends points of the grid, less every point
   strictly inside a published `empty_edges` pair. Where `P` holds exactly
   the published count of numbers, the strata take `P` in ascending order,
   `S` whole points of it each taken by two neighbouring strata and no
   point by three. Of every such assignment keeping each stratum inside its
   sign band, the one taken moves the strata the fewest grid units in all,
   each stratum counted from its own grid text, and of those the one taking
   the lower point at the first stratum where two differ. It is not taken
   where the strata whose numbers have a point-free spelling hold fewer
   cells than the styles map asks to be written point-free.
2. **The merge.** Where the texts still number more than the published
   count, a stratum holding a number that is not whole, beside a stratum
   holding a whole number, each text held by its stratum alone, takes its
   neighbour's number -- never the first or last stratum, and only where
   its sign band holds that number. Pairs are taken fewest grid units apart
   first, then the lower pair, then the lower stratum moving, no stratum in
   two pairs, until the texts number the published count.

Measured before this clause: 500 readings at one place whose whole ones
were written `4` in most cells and `4.0` in a few -- a workbook with some
figures stored as text reads exactly so -- published 33 spellings of 31
numbers and the twin held 30 at seeds 4, 11 and 1, with the table at exit
0; over 120 such columns 61 twins of 240 missed `n_distinct_values`, and
after it one of 240 does, a column writing no whole number twice whose walk
lands two whole strata on one point.

**MEASURED, through the real reader, producer, loader and generator at
twelve seeds, published against held, before this clause and after.**
300 ages between 18 and 89 publishing 70 different numbers: **56 to 66
before, 67 to 70 after**. A tight 200-row column publishing 74: **61 to
68 before, 69 to 71 after**. A wide one publishing 194: **193 to 194
before, 194 at every seed after**. A column of seven repeated numbers
over 200 rows publishes 7 and holds 7 either way, so the clause costs
nothing where there was nothing to win. Columns at one fixed fraction
width were already on a grid, so THIS CLAUSE moves none of them --
the pass itself moves them, which is what it was built for.

**WHAT IT STILL DOES NOT DO, AND WHY THAT IS THE WALK AND NOT THE
FACTS.** A tight column's strata have narrow shares and a share can
hold no free grid point at all — on the 200-row column above the walk
was asked 14 times and answered 6. The count stays REPORT-ONLY and the
twin's own report names the shortfall.

**But that is this walk falling short, not the count being
unreachable**, and an earlier writing of this paragraph said otherwise.
The walk is greedy and ascending, and it moves only a
stratum that has COLLIDED. Take pinned ends `0` and `5` with interior
values `1`, `1`, `2` and shares `[0,1]`, `[1,2]`, `[2,4]`: neither `1`
can move, because `2` is taken and their shares reach nothing else, and
the unique `2` is never asked because it collided with nothing. Yet
moving that `2` to `3`, inside its own share, and then a `1` to `2`,
inside its own, gives `0,1,2,3,5` — every value distinct, no stratum
off its share, no sign changed, no end moved. A walk that could move an
uncollided stratum to make room would reach the count here. That walk
has not been built or measured, so what is stated is what this one
does; the shortfall it leaves is not evidence that the ladder and the
count are in conflict.

### G6.6 The published field widths reach the VALUES

**THE CENSUS THIS SECTION SERVES IS `field_widths`** (contract 7.10,
plan P4-D30), and it is served here rather than among the spelling
walks for one reason: an unpadded cell is exactly as wide as its value.
`pad_widths` is bought with a zero and `fraction_widths` by adjusting a
value inside its own stretch, so both are the writing stage's business.
A cell written `199` can be made three figures wide only by holding a
value between 100 and 999, which is the VALUE stage's business and
nothing else's.

Until this section existed the value stage ran first and read neither
census. That is residual R-P4-27 in one sentence, and R-P4-30 and
R-P4-35 are what it produced: a dental-code column of `D0120`, `D1110`
and `D2740`, every core four figures, published `pad_widths {4: 97}`
and a twin that drew 78 values below a thousand where 97 were needed.
No assignment of 78 small values fills 97 narrow fields, and the
padding walk was not at fault.

**G6.6.1 The two censuses become demands on the values.** Let *P* be
`pad_widths` and *X* be `field_widths`, each read over its NAMED keys
alone; the pooled remainder of either names no width and asks for
nothing. Then:

- for every width *w* named by *P*: **P(w)** cells must hold a value of
  AT MOST *w* − 1 figures, the leading zero being a figure of the field
  and not of the value. A width of 1 asks for nothing and is skipped,
  no value having fewer than one figure;
- for every width *w* named by *X*: **X(w) − P(w)** cells must hold a
  value of EXACTLY *w* figures, there being nothing else to make up the
  difference. Where *P* does not name *w*, *P(w)* is nought.

The figure count of a value is the count of figures in its own
point-free spelling, the sign not counted — the reading
`pad_widths` is taken with, applied to the twin's own text.

**G6.6.2 The demands are served from the values already drawn, and the
order is fixed.** The EXACT demands are served first, because only one
figure count can serve one of them while a ceiling demand accepts every
count at or under its own. The ceiling demands are then served in
ASCENDING order of width, each from the NARROWEST values still
unclaimed: a value that fits a narrow ceiling fits every wider one, so
spending it on a wide one is what leaves the narrow one unfillable.
Within a demand, WHOLE STRATA are taken first and one stratum is split
only to finish a count nothing else can — the rule G6.4's padded walk
keeps over the cells, kept here over the values, and for a second
reason of its own: a stratum holds ONE value, so a stratum that is only
partly spare cannot move without breaking the demand it is half
serving. **And WHICH strata a demand takes decides where the surplus is
left, which is the only thing G6.6.3 has to spend** (stage 3, landing
3.3): the two PINNED strata are served first, because G6.6.3 may move
neither, so a spare cell there serves nothing at all; and the rest are
served from the widest values DOWN, so what is left over is the
smallest stratum of its width — the one whose own stretch reaches the
narrower field. It is the demand order's own reasoning, read over the
strata: a value that fits a narrow ceiling fits every wider one, so it
is the last thing a wide demand should take. Measured on 120 record
codes `S00042` at a floor of eleven, where stage 3's derived high end
held the surplus: 110 cells of five figures against a published 109,
one four-figure cell short, and nowhere to take it from.

**G6.6.3 One stratum moves, and the rules it may not break.** Where a
demand is short, one stratum takes a value of the figure count that
demand wants. The stratum must be

1. not one of the two PINNED strata, which hold the published ends of
   the ladder;
2. not in the ZERO band, so the count of zero values does not move;
3. holding a value that can be written point-free, so that the pass
   moves nothing the point-free count, the strata-apart rule or the
   held-back pool has just settled;
4. no wider than the cells the short demand is still owed, a wider
   stratum overshooting the width it moves to — which is the same miss
   in the other direction;
5. covered, cell for cell, by cells of its OWN figure count that no
   demand claimed. A stratum wholly spare satisfies this trivially; a
   stratum half claimed satisfies it when the surplus can take its
   place, which is sound because a cell serves a demand by its figure
   count and by nothing else.

The value it takes is the one nearest the value it holds, among the
whole numbers of the wanted figure count this stratum could have been
GIVEN. **Which whole numbers those are is not "the ones strictly inside
its share", and writing it that way first left a floor-one column two
cells short of a width it could reach.** G5.3 draws a position inside
the stratum's share and G5.4 rounds it to the nearest whole number, so
every whole number within HALF A UNIT of the share is one an ordinary
run could have produced for this stratum: a share of `(9.18, 11.55)`
yields 9, 10, 11 and 12, not 10 and 11 alone.

**A STRATUM HOLDING ONE OF A TAIL'S ROWS TAKES THE ROOM BETWEEN ITS
TWO NEIGHBOURS INSTEAD OF ITS SHARE** (stage 3, landing 3.3; contract
6.7a). A-P4-18 bounds the move by the stratum's stretch because the
ladder's rungs are published values and a stratum leaving its own
stretch is a twin disagreeing with a fact somebody can read. Beyond a
boundary percent no rung is published: what the description states
about those rows is their count and their two distances, both
approximated facts with windows of their own (G12.13), and the
staircase step they stand on is a choice G5.3b makes rather than a
value the source held. So the room for such a stratum is the order
itself — strictly between the value the stratum below holds and the
value the stratum above holds, so the order of the values and the
count of different ones both stand — and, the walk taking the NEAREST
candidate inside it, what the move spends of the two distances is the
least it can. Measured on the 120 record codes above: eleven cells are
published padded at five figures, the twin's staircase put ten of its
rows under ten thousand and the eleventh at 10009, no other stratum
could reach four figures, and with the room that stratum takes 9999 —
ten units of a mean distance of 6593.3 — and the twin writes the
eleven padded cells it owes.

That half unit is G5.4's own, the one G12.2 already widens the rung
window by, so this rule grants nothing the method had not granted
already. **It is not a widening of amendment A-P4-18**, which bounds a
move's REACH by the stratum's stretch: the reach here is half a unit,
and a stratum whose stretch is narrower than that gets the two whole
numbers its own rounding could have reached and no others. A share of
`(99.23, 99.79)` holds no whole number at all and yields exactly 99 and
100 — which is the case the ladder itself does not settle, a decade
crossing falling between two rungs, and the census is what settles it.

It never crosses zero, for the reason G6.4's searches do not.

**It may not take a value another stratum holds, EXCEPT where the value
it gives up is one another stratum also holds.** Then the count of
different values cannot fall: what it vacates stays behind and what it
lands on was there or is new. Drawn values ARE shared — two strata
either side of a rung can round onto one whole number — so this is a
case that arises rather than one imagined for it.

**G6.6.4 What the half unit buys, measured rather than argued.** The
rule above was written twice. The first version took only the whole
numbers strictly inside the share, and the second takes every one the
stratum's own rounding could reach; the difference is not a nicety.

Measured on a 230-row vaccine-code column running `000` to `199`
(residual R-P4-35), where the rung above the crossing is interpolated
across a jump and the ladder puts 128 cells below a hundred against the
source's 127: over forty seeds, 20 wrote a cell at a width the source
never used before this section and 2 after it — and the 2 are named by
`synthtwin validate` where before nothing said anything at all.

**G6.6.5 The pass runs LAST among the value passes**, after G6.4's
point-free carrier walk, after the step that pulls two strata apart and
after the held-back pool. It moves a whole value onto another whole
value no stratum holds alone, so every guarantee those three
established comes through it untouched and none has to be re-argued
against a value this pass chose.

**G6.6.6 What it does NOT do, stated so no reader assumes it.** It does
not move a value outside its stretch except by G6.6.4's single
neighbour. It does not change how many cells a stratum holds — the
allotment is G5.2's and is not read here — so a census whose widths
disagree with the allotment by a whole stratum is reported rather than
met. And its search over the whole numbers of a share stops at 4096
candidates and at fifteen figures, fifteen being the widest field every
value of which is exact in binary64; beyond either, the width is given
up and named rather than met with a value that is not the value it
looks like.

**G6.6.7 Where the width is given up.** `field_widths` is
REPORT-ONLY — plan P4-D30 and contract 7.10 and 9.4 all say so, on the
measurement 7.10 carries — so a width the pass cannot reach is
RECOUNTED off the finished cells and NAMED in the twin's own report as
a deviation carrying the published count and the achieved one, while
`synthtwin validate` LISTS `numeric.field_widths` with a sentence
saying the twin follows the census without being held to it. **This
paragraph said EXACT-OBSERVABLE and named a subcheck
`fields.published.<width>` that exists nowhere in the product or the
suite**; nothing read it, so nothing turned red, and it is repaired
here rather than left as a fourth document saying a fifth thing (the
sibling search of landing L12). The report reads the census with the
producer's own reader, so a width the writer intended and a width a
cell actually wears cannot come apart between them.

### G6.7 No value stands where the description says there is none

**THE FACTS THIS SECTION SERVES ARE `empty_bins` AND `empty_edges`**
(contract 7.11 and 7.11a, plan P4-D32), and they are served at the
value stage because each is a statement about VALUES and about nothing
else. A cell cannot be written out of a stretch it stands in; only the
value can be moved. The first says WHICH stretches there are and the
second says where each one really begins and ends.

**G6.7.1 What was wrong.** A column with two clusters and nothing
between them publishes a middle rung BETWEEN the clusters — the median
of a hundred and fifty values around twenty and a hundred and fifty
around eighty is 49.65, a number no cell of that column holds — and
G5.3 interpolates the rungs and honours it. Measured through the real
reader, producer, loader, generator and validator at FORTY seeds and
at the default floor, the twins of three such columns put 4–6, 2–3 and
3–6 of their 300 cells in a stretch the real column left completely
empty. Nothing crashed and nothing was named. Anybody plotting the
twin met a third cluster that is not there.

**AND WHAT THE FIRST REPAIR LEFT.** Moving a cell to the nearest
occupied BIN emptied the named stretches but not the source's own gap,
because the bins lie strictly inside it. Publishing the real edges
(`empty_edges`, residual R-P4-138, owner's ruling of 2026-09-04) and
then asking those edges which stretch a stratum stands in took it to
nothing. **THE LEDGER, and it is the only one: ** three stages, measured the same way each time -- forty seeds on each
of the three two-cluster witnesses, counting cells inside the SOURCE's
own widest gap rather than inside a bin:

* moved to the nearest occupied BIN: one cell per column per seed,
  15.7 to 23.0 units from the nearest real value;
* walking from the published EDGES, with the queue still gathered from
  the bins: **8, 4 and 27** of 12,000;
* asking the published PAIRS which stretch a stratum stands in:
  **0, 0 and 0** of 12,000, which is where the shipped pass is.

**G6.7.2 The bins, and where they come from.** The scale is the one
G6.6's sibling census is counted on: `HISTOGRAM_BINS` equal bins
between the block's published `min` and `max`, divided by contract
C6-31f's rule -- which fixes, among other things, that a value on a
shared edge belongs to the UPPER bin, the one that starts there. The
generator reads the two ends from the LADDER rather than recomputing
them, which is what makes a bin number mean one thing in the producer,
the loader and here. A block whose ends this format
cannot hold, or whose ends are finite and whose WIDTH is not, has no
scale, publishes an empty list, and this section does nothing.
**THE ARITHMETIC OF ONE BIN, stated so that a second reader computes
the same number** (the oracle's independence repair of 2026-09-19).
The division is done in the format's own binary64 arithmetic, because
contract C6-31f's case with no scale is two ends whose DIFFERENCE the
format cannot hold, so the division it states is a binary64 one: the width is
`max - min`; a scale with no width -- the two ends equal, or `max`
below `min`, or an end or the width not finite -- puts the value in bin
0, as C6-31f's two cases with no division say. Otherwise the clamp is
taken FIRST, before any arithmetic, so that no step of it can overflow:
a value at or above `max` is in the last bin, one at or below `min` in
bin 0; and a value strictly between the ends is in bin
`floor((v - min) / width * 32)`, each operation rounded to binary64 in
that order, the difference, the quotient, then the product, and the
result held to at most the last bin, since the quotient of a value just
below `max` may round to one. In binary64 `0.125` on the scale `0` to
`0.2` is in bin 20, where exact rationals over the two doubles would
give 19.

**A VALUE THAT IS NOT FINITE IS OUTSIDE C6-31F, and what this method
answers for it was completed from the shipped code, not read from the
contract** (the skeptic of the independence repair, 2026-09-19). The
contract's formula takes no floor of a quotient that is not a number,
and its clamp read literally would put `+inf` in the last bin; this
method puts every value that is not finite in bin 0, which is what the
shipped division answers (the one the producer, the loader and the
generator share), so that the rule is total. The
clause decides nothing any description reaches: the loader refuses a
description holding an infinity or a not-a-number (measured
2026-09-19: a `mode` and a `max` written as `Infinity`, as `NaN` and as
`1e999` were each refused), so every end and every mode the generator
bins is finite, and no witness pins the clause.

**WHERE THE DIVISION IS WITNESSED.** The oracle bins a value in one
place, G6.1's mode pass (plan P4-D267), and there only on a column
publishing an empty bin, to ask whether the mode stands in one. A
description a producer writes never puts its mode there, since the
mode is one of the values the statistics used and C6-122 names only the
bins holding none of them; the loader does accept one that does
(measured 2026-09-19: a mode of 25.0 standing in bin 15, bin 15 named
empty with its edges, loaded). So no frozen case reaches the division:
rebuilding every vectors file with the oracle instrumented calls it no
times. Its clauses are witnessed one call at a time instead, in
`tests/test_oracle_rule_witnesses.py`: thirteen values with the answers
worked out from this statement, asked of the oracle and of the shipped
division, and seven registered mutants of the oracle's division -- a
shared edge to the lower bin, one bin up, no cap at the last bin, the
top clamped to bin 0, the clamp after the arithmetic, exact rationals,
and bin 0 always -- each of which turns that witness red. The empty-bin
PASS itself (G6.7.3 onward) is not mirrored by the oracle, and ledger
K-P4-23 counts it.

**G6.7.3 The stretches.** Consecutive named bins are taken as one
STRETCH, and the move is out of the whole stretch rather than out of
the bin a value happens to stand in: a value in the middle of nineteen
empty bins has to reach the occupied bin below the first of them or
the one above the last, and the bin it stands in says nothing about
how far that is. Both of those bins always exist, because the smallest
value of a block is in the first bin of the scale and the largest is
in the last, so neither end bin is ever empty (contract Q20).

**AND THE STRETCH'S REAL EDGES ARE PUBLISHED, one pair per stretch, in
the same order** (`empty_edges`, contract 7.11a; residual R-P4-138,
closed by the owner's ruling of 2026-09-04). The pair is the largest
value the block holds below the stretch and the smallest above it. It
matters because a bin is a thirty-second of the block's reach, so the
bins a column leaves empty lie strictly INSIDE the stretch it really
leaves empty: a cell moved to a bin edge was still in the source's own
gap. Contract Q21 holds a description to one pair per stretch, in
order, and to each pair standing either side of its OWN run of bins,
so the generator indexes the pairs by the stretch's position and needs
no search.

**WHICH STRETCH A STRATUM IS IN IS ASKED OF THE PAIRS, and of the bins
only where the pairs say nothing.** A bin is a thirty-second of the
block's reach and a pair is the gap itself, so a value can stand
INSIDE the gap and still be in a bin that holds plenty. A pass that
gathered its queue from the bins alone never saw those values: it is
what left 8, 4 and 27 cells of 12,000 inside the source's own gap
after the edges were published, and asking the pairs first took all
three to nought. A stratum is in the FIRST pair that holds it, read by
the value and by every spelling of it, in the width order
`_census_widths` fixes.

**AND A CANDIDATE IS REFUSED IF IT READS INSIDE ANY PUBLISHED PAIR,
not only inside a barred bin.** A column with two stretches sharing
the one value between them let the further-edge walk step past that
value into the FIRST stretch's real gap — outside every barred bin,
because a bin is coarser than a gap, and so accepted with nothing
naming it. The pairs are OPEN intervals: an edge is a value the source
really holds, so landing ON one is not landing in the gap.

**AND WHERE NOTHING CLEAN IS FREE, A SLOT INSIDE SOME STRETCH BUT
OUTSIDE EVERY BARRED BIN IS TAKEN RATHER THAN NONE** (residual
R-P4-156, closed 2026-09-04). The walk is four walks in order of how
much they ask for: the nearer edge and then the further one refusing
every published stretch, and then the same two refusing only the
barred bins. STAYING IS NEVER BETTER THAN MOVING — a stratum that
stays is inside its own stretch AND inside the barred bin it stood in,
while the looser slot is better on one count and no worse on the
other. Measured on the committed battery, forty columns at forty
seeds: refusing every stretch and stopping there raised the count of
runs leaving a cell in a named bin to 240; walking the loose pass
after it gives **130 runs in a named bin and 213 inside a stretch the
source really leaves empty**, against 135 and 1058 on the tree before
the stretch edges landed.

**G6.7.4 Which stratum moves, and the rules it may not break.**

**ELIGIBILITY, STATED EXACTLY, because the enumerated rule below used
to say "falls in a named bin" and the shipped pass moves more than
that.** A stratum is IN a stretch when its value, or any spelling of
it at any width the fraction census could reach that cell at, reads
strictly inside one of the published `empty_edges` pairs — the FIRST
such pair, taking the pairs in ascending order and the spellings in
the width order G6.4's census fixes. Where no pair holds it, and only
then, the BINS are asked: a stratum whose value or spelling falls in a
named bin belongs to the stretch that bin is part of. A generator that
asked the bins alone recreates the residual this pass exists to remove
— measured, 8, 4 and 27 cells of 12,000 on the three witnesses — since
a gap is finer than a bin and a value can sit inside the gap while
standing in a bin that holds plenty.

**AND THE FACT A FAILED MOVE NAMES FOLLOWS FROM WHICH ROUTE QUEUED
IT.** A stratum queued because it stands in a named BIN that cannot be
moved names `empty_bins`; one queued only because its value is inside
a published PAIR names `empty_edges`. Naming the bins for the second
would send a reader to a fact the twin did not break.

Every stratum so identified moves, subject to:

1. not one of the two PINNED strata, which hold the published ends of
   the ladder — and which are never in a named stretch anyway, being
   the two values the end bins are defined by;
2. not in the ZERO band, so the count of zero values does not move;
3. never across zero, so the sign counts do not move;
4. keeping its WRITTEN FORM — a value that carries no point moves to a
   value that carries no point, and one that carries a point moves to
   one that carries a point — so the point-free count G6.4 met and the
   held-back pool are untouched. This rule is asked only of a column
   whose styles map asks for a point-free cell, the withheld remainder
   counting as `plain` (plan P4-D177): on any other column every cell is
   written with a point whatever its value, so `10` is written `10.0`
   and a move onto it changes no form. Measured before: a stratum at
   8.5 inside the published stretch 7.5 to 10.0 of a column of six
   discounts could not take the free edge 10.0 and went to 7.4, and the
   twin held 225 cells of 7.4 and no 10.0 while validation passed;
5. landing on no value another stratum holds, AND on no value that
   would be WRITTEN the way another stratum's value can be written, at
   any width the fraction census could reach either of them at. The
   second half of that is not caution: two values a thousandth apart
   are two values and ONE cell, so a rule that compared only the
   numbers handed the column two identical cells and took back the
   count of different values;
6. holding its value ALONE. A move costs nothing only when the stratum
   VACATES what it leaves: one value goes, one arrives, and the count
   stands. A stratum sharing its value vacates nothing, so whatever it
   does ADDS — a fresh value adds a number, and joining another
   stratum's value adds a spelling, because the writing stage then has
   two strata on one number and the leading-zero family splits them;
7. keeping its FIGURE COUNT, where its value carries no point. A
   point-free cell is exactly as wide as its value, so moving a
   stratum from one figure to two takes a carrier away from the padded
   -width census: 9 can be written `09` at a published width of two
   and 10 cannot.
8. landing on a POINT OF THE COLUMN'S WRITTEN GRID, where the column
   is on one — G5.2a step 1's grid of `f` figures (landing 2b.7,
   2026-09-15). A whole-valued column is on the INTEGER grid and rule
   G6.7.6 already rounds every candidate onto it; a column written at
   a fixed width is the same kind of fact and had no such step, so
   this walk — which steps in sixty-fourths of a BIN, and a bin is not
   a grid — handed a stratum a value lying between two grid points.
   G6.6's writer then wrote that cell at the width its own value
   needed rather than at a published one, which is a published width
   count missed. MEASURED through the real reader, producer, loader,
   generator and validator on halves written as a spreadsheet writes
   them — `37` beside `37.5` — at 400 and 4,000 rows, seeds 1, 7 and
   23, at both floors: ONE cell of each twin came out
   `38.55126953125` and `39.05078125`, the twin wrote 207 cells at the
   one published width against 208 and 2,000 against 2,001, and
   `widths.published.1` missed at every one of the twelve runs.
   The rule only NARROWS the candidate set: rules 1 to 7 are applied
   to the snapped candidate exactly as before, so a snapped value that
   would change the written form, the figure count or the sign band,
   or that reads as a value another stratum holds, is passed over as
   it always was. Where the grid holds no free point within the reach
   of G6.7.5, the answer is nothing, the value stays, and G6.7.8's
   recount names the stretch — the same outcome this walk has always
   had where it can find nowhere to go.

**RULES 6 AND 7 EXIST BECAUSE THE SUITE FOUND THEM, and both were
measured on the floored witness of review item P3-V7-F4** — a column
of nine different spellings at a floor of eleven, the case where this
fact is published and the census beside it is not. Without either rule
the twin wrote TEN spellings against a published nine and
`distinct.n_distinct` fell from HELD to an authorized deviation. With
both, it writes nine and the count is met outright. `n_distinct` and
`pad_widths` are EXACT-OBSERVABLE and this fact is REPORT-ONLY, so
where they meet this one gives way and G6.7.8's deviation names the
stretch instead. **Measured cost of the two rules on the corpus of
G6.7.8: none.** The three two-cluster columns still write no cell in a
named stretch at any of forty seeds at either floor, and the forty
described columns leak on the same 119 runs of 1600 — 130 after this
landing, against 1058 to 213 on the stretches the bins stand in for.

**G6.7.5 Where it goes, and the bound.** To the published EDGE nearer
to it — measured from the value to each of the stretch's two edges —
and no further past that edge than one BIN'S WIDTH. **That is this
move's whole reach, and it is written in the published fact's own
terms**: a value moves out of the stretch the description says holds
nothing, to the real value the description says stands beside it, and
stops within a bin's width of it.

**THE REACH IS A DISTANCE AND NOT A COUNT OF BINS**, and the two are
not the same once the walk starts from a published EDGE. An edge is a
VALUE standing somewhere inside its bin, so a candidate a bin's width
below it can fall in the bin beyond the stretch's neighbour — on a
whole-numbered column whose bin is narrower than a unit, the rounding
puts it there. That candidate violates no published fact: it is
outside every named bin and outside every published stretch. Reading
the bound as "the adjacent bin" instead was measured on the committed
battery and refuses those slots: runs leaving a cell in a named bin go
from 130 of 1600 to 190, and runs leaving one inside a stretch the
source really leaves empty from 213 to 285. The distance is the
bound.

**THE FURTHER EDGE IS WALKED AFTER THE NEARER ONE**, and only where
the nearer one has nothing free. Both edges are edges of the SAME
stretch, so a value reaching either has left it; the nearer is tried
first because that is the smaller move. This is what a published edge
made necessary rather than a preference: a BIN edge has a whole
occupied bin behind it, while a published edge may have a single value
— a column whose two clusters sit close together publishes a stretch
whose lower edge is one value alone in its bin with ANOTHER stretch
below it, so the downward walk had a twelfth of a bin to work in and
gave up. Walking the other edge afterwards moved that cell and cost
the near-side answers nothing.

**IT IS NOT A-P4-18's BOUND, and it cannot be.** That amendment bounds
the width snap by the stretch of the ladder a stratum covers. Measured
on all three columns above, most of the strata that land in the empty
middle have a share lying WHOLLY inside it — four of six on the first,
one of three on the second, four of six on the third — so a move
bounded by the share reaches nothing at all. Plan amendment A-P4-50
records the choice and its ground: between the rungs the ladder says
nothing and the method fills the silence by interpolating, which is an
INFERENCE, while "no cell of the real column lies between these two
edges" is a MEASUREMENT. Where the two meet, the measurement wins.

**G6.7.6 The walk inside the bin.** From the published edge outward,
in sixty-fourths of a bin, taking the first position that breaks none
of G6.7.4's rules. The edge ITSELF is the first candidate on both
sides, because each published edge is a value the source really holds
and so a target in its own right; the bin edges this walk took before
were the edges of the EMPTY bin, so the downward one had to start a
step past it.

**THE ORDER THE STRATA ARE WALKED IN IS WHAT KEEPS THE LADDER'S
ORDER**, and it is stated here in the terms the walk really uses. Each
stretch's strata are split by which edge is nearer to them; each group
is then walked **furthest from its own destination edge FIRST**. The
group going DOWN is walked from its largest value downward and the
group going UP from its smallest value upward, and since the walk
hands out positions from the edge inward, that gives the largest of
the down group the position nearest the lower edge and the smallest of
the up group the position nearest the upper one. The moved values
therefore come out in the order the ladder gave them.

This section said "the strata standing nearest the edge are walked
FIRST" until 2026-09-04, which is the opposite of both groups: a
generator following it would reverse the moved values against the
shipped one and write different bytes for the same description. On a
whole-numbered column each position is rounded to a whole number
before it is tested, and a position that then reads back inside a
named bin is passed over. **AND ON A COLUMN ON A WRITTEN GRID each
position is moved onto that grid before it is tested** (G6.7.4 clause
8, landing 2b.7): the two are one rule, the integers being the grid a
whole-valued column is written on, and the snap is taken BEFORE the
reach of G6.7.5 is measured for the same reason the rounding is —
the candidate that is tested must be the candidate that is written.
A grid point whose text does not read back as itself is passed over,
which is the rule G6.5a states for its own walk.

**AND THE TEST IS APPLIED TO THE SPELLING, not to the value.** A
column written to one figure after the point has its values rounded
when they are written, and a value placed a thousandth of the reach
outside a stretch comes back inside it: the value 71.625, placed in
the first occupied bin above a stretch, was written `71.6`, which is
in the last bin OF it — one cell of three hundred, at every seed, and
the only sign of it was the recount. So each candidate is written at
every width the fraction census could reach the cell at, with this
method's own writer, and every one of those readings must fall outside
every named bin.

**G6.7.7 The pass runs LAST among the value passes**, and takes that
place from G6.6. The reason is a difference in kind between the two
obligations: a width the values cannot wear is a SHORTFALL the report
names, while a cell in a stretch the real column left empty is the
twin SHOWING A CLUSTER NOBODY HAS. What this pass can take back from
the four before it is bounded by G6.7.4 to exactly one thing — a field
width — and that census is REPORT-ONLY with its shortfalls named.

**G6.7.8 What the report says, and when.** The report names every
FINISHED CELL that reads inside a published stretch, RECOUNTED from
the twin's own text after the cells are written — one note per stretch
and per fact, carrying the stretch's two PUBLISHED edges, the number
of cells standing in it and the values they read as. A cell in a bin
the description names as empty misses `empty_bins`; one standing only
inside the published pair misses `empty_edges`; a stretch holding both
kinds gets a note for each.

**IT IS A RECOUNT AND NOT A PREDICTION**, and three things were wrong
while it was written at the value stage. The edges it carried were the
BIN boundaries, so on a real gap of 26.6 to 72.7 it read "no value
from 26.7 to 71.3" — a narrower range than the description states. The
count was a STRATUM's size, and a stratum stands for several cells
whose widths are chosen later, so it could report two cells where one
was inside the stretch and one outside. And a stratum that MOVED, to a
slot the looser walk of G6.7.6 found inside a stretch other than its
own, left no note at all. Measured over forty described columns
at forty seeds each, the runs writing a cell into a named stretch went
from 1049 of 1600 to 119 — and, re-measured on the same committed
battery after this landing on 2026-09-04, to 130 of 1600 in a named
BIN while runs putting a cell inside a stretch the SOURCE really
leaves empty fell from 1058 to 213 and the worst run of either from
twelve cells to four. Every one of them is a column whose
other published facts leave no room beside the stretch: a
whole-numbered column whose bins are barely wider than a unit and
whose neighbouring bin holds no free whole number, or a stratum whose
sign band ends at the edge it would have to cross. `empty_bins` is
REPORT-ONLY on that measurement (contract 7.11), so `synthtwin
validate` LISTS the fact rather than holding a file to it.

### G6.7a The scale of a tail block (stage 3, plan P4-D325)

On a tail block the thirty-two bins divide `[b_lo, b_hi]`, the two
boundary rungs, by contract C6-31f's arithmetic, and **a value outside
that stretch is in no bin**: G6.7 never moves a tail value. The
description publishes the real edges only of a run of empty bins with an
occupied bin on BOTH sides -- two interior values, the owner's principle
("just showing that the value exists is not an issue") -- and withdraws
the edges of a run touching an end bin, whose outer neighbour would be a
tail value; G6.7 walks a run with published edges to them as before and
a run touching an end bin to the edges of its own bins. `value_histogram`
is `{}` on a tail block, and `bin_groups` (contract BG1) carries the
census in groups of at least `max(small_cell_floor, 3)` rows.

Why "no bin" is load-bearing: with the clamp of `histogram_bin` a tail
value below `b_lo` reads as bin 0, and on a 40-value block whose bin 0
was empty G6.7 dragged twelve of its low ranks onto the boundary. The
price of withdrawing the tail edges is measured on the three two-cluster
witnesses of `r_p4_136_l8_empty_bins.py` and recorded against K-P4-07,
whose rule is restated to interior stretches (plan P4-D325).

### G6.8 A count column that publishes every spelling is written as them

**THE FACT THIS SECTION SERVES IS `number_spellings`** (contract 7.13,
plan P4-D123, landing 2b.18 part 2), which a `count` block names only
where one number was written more than one way — `7`, `07`, `007` — and
every spelling cleared the floor and two cells. It then names every cell
read as a number with its own spelling.

**THE RULE.** Where the census names anything, the numbers of the
column's content list are that census and nothing else: each spelling
written as many times as it counts, ordered by the whole number it
writes and then by the spelling itself, so `0`, `7`, `07`, `007`. G5's
strata and G6.1 to G6.7 are not taken for those cells, and the
stragglers of G10.3 follow them exactly as they follow the numbers G5
and G6 would have written. The words G4.3 budgets for the column are
still drawn, so the stream every later column reads does not move.

**WHY THIS IS NOT A SHORTCUT.** Every statistic the block publishes beside
the census — the ladder, the moments, the styles, the pad and field
widths, `n_zero`, `n_distinct_values` — was computed from exactly the
cells the census names, so writing the census writes a column holding
every one of them. Measured on a 500-row column of `0`, `7`, `07` and
`007` at three source and generate seeds: before, the twin held six or
eight spellings for four, two to four of them spellings the table
never wrote; after, the four spellings at their published counts on
every run, with both files passing their description.

## G6A. Affixed-number columns (`affixed_number`)

Added by Phase 4; like G7A this section was written after the
implementation shipped, which is the wrong order and is recorded in
G13.

### G6A.1 Two populations, and which facts answer for which

An affixed column holds cells such as `$1200` or `450 mg`: a NUMBER
with a fixed prefix, a fixed suffix, or both. The role's whole
difficulty is that it has TWO populations and the profile publishes
facts about both, so an implementer who reads one set of counts as the
other builds the wrong column.

- **The CELLS.** The universal class counts — `n_present`, `n_numeric`,
  `n_out_of_range`, `n_contradictory`, `n_not_numeric` — answer for the
  cells, like every other role. A cell reading `$1200` is not itself a
  number, so a column of prices publishes `n_numeric` of 0 and
  `n_not_numeric` equal to its present count.
- **The CORES.** The quantitative block `numbers` — the ladder, the
  moments, `numeric_styles` and its two sibling censuses, everything
  G5 and G6 consume — answers for the cores, the text left when the
  pair is taken off. Beside it stand `n_affixed`, how many cells wore
  the pair, and the four CORE class counts `n_core_numeric`,
  `n_core_out_of_range`, `n_core_contradictory`, `n_core_not_numeric`.

Also published: `affix_prefix` and `affix_suffix`, either of which may
be empty, but not both.

### G6A.2 The core view: G5 and G6 apply unchanged

The construction does not reimplement any numeric rule. It builds a
COLUMN VIEW of the cores and hands it to the numeric machinery:

```
statistical_type  <- continuous
n_present         <- n_affixed
n_numeric         <- n_core_numeric
n_not_numeric     <- n_core_not_numeric
n_out_of_range    <- n_core_out_of_range
n_contradictory   <- n_core_contradictory
facts             <- numbers
```

Every rule of G5 and G6 then applies to that view WORD FOR WORD,
including the stratification of G5.2, the endpoint pins of G5.3, the
spelling family of G6.1 and the style walk of G6.4. This is also why
G4.3 budgets this role as `S - pinned - zeroed` read over the cores,
and why G5.1 says `fraction_widths` and `pad_widths` are read over the
cores here: there is one numeric implementation and the affixed role
is a caller of it, never a copy.

The pair goes on afterwards, character for character as published:

```
cell = affix_prefix + core + affix_suffix
```

No trimming, no case change, no normalization of either side.

**AND ON A DECLARED COLUMN THE EXCHANGE OF P4-D26 RUNS OVER THE CORE
ALONE** (landing 2b.16, plan P4-D106). Where the column is named in
`settings.forced_decimal_commas`, its cores are written by the rules
above and then have every point and comma exchanged, exactly as a plain
numeric column's cells are — and the WRAPPER is not touched, because it
is published text rather than a number this method spelled. So a
declared column publishing the suffix ` EUR` writes `624,60 EUR`, and
one publishing the prefix `U.S.$ ` writes `U.S.$ 825,81` with the two
points of its own wrapper still in it. Exchanging the whole cell
instead rewrites the wrapper into a pair the description does not
publish: measured, 800 cells of `U.S.$ 129,58` had every twin cell
written correctly and both the twin and the real table reported at exit
3, because the reading turned each into `U,S,$ 129.58` and counted it a
straggler wearing no published pair. The order is the one the numeric
roles use: the cell is finished first and exchanged last, so the rules
above see the point form they were written in.

### G6A.3 The stragglers, and the overlap that must not be assumed away

`n_present - n_affixed` cells wore no pair. The detection rule requires
one side of an affixed cell to carry text, so a cell that IS a plain
number wears no pair and is a straggler. The description says HOW MANY
there were and, through the universal counts, what CLASSES they fell
in — and nothing else about them, so they are invented.

**The two populations OVERLAP, and this is the trap.** A cell wearing
the pair is still a cell, so it lands in one of the four universal
classes like any other cell. A column whose prefix is `1` holds cells
such as `12` that wear the pair AND read as ordinary numbers. An
implementation that subtracts `n_affixed` from the text class alone,
clamps at zero and then writes the number class again on top produces
a hundred-and-one-cell twin for a hundred-row column.

So the classes the affixed cells ALREADY fill are RECOUNTED from the
finished text, with the same classifier the description was built with,
and only the shortfall is written:

```
worn[k]  = how many of the written affixed cells classify as k
short[k] = max(published[k] - worn[k], 0), then capped at the room left
```

taken in the order `n_numeric`, `n_out_of_range`, `n_contradictory`,
each capped by the stragglers not yet spent. **Whatever the three named
classes do not claim is ordinary text**, which is the class the contract
gives every cell no other class names. The cells are then appended in
that same order: numbers first, then out-of-range, contradictory and
text.

**Three spellings are refused for every straggler**, and each refusal
was learned from a defect: a spelling already written would repeat a
cell; a spelling that WEARS the pair would be counted affixed when the
twin is described again; and a spelling this column publishes as a HOLE
would be read back as no value at all — a column of prices beside
eleven cells spelled `1`, declared missing, published
`missing_by_source {"1": 11}`, and a twin that wrote a present `1` had
five exact counts move against the description it was built from.

The plain-number stragglers are written as WHOLE NUMBERS counting up
from 1, skipping every refused spelling, because nothing else about
them is published: the ladder and every moment belong to the cores.

**The walk for the other three classes is BOUNDED, and what happens
past the bound is part of the method.** It asks the class builder for
progressively larger batches and keeps the survivors, and it stops
after `count * 8 + 64` steps. A column can exhaust it — one whose every
candidate wears the pair, such as a prefix of `text-` against text
stand-ins spelled `text-1`, `text-2` — and past that point the cells
are written from a last resort of this method's own: `(no pair 0)`,
`(no pair 1)`, and so on by their place.

That last resort **owes the same hole refusal the walk owes**. A
spelling this column publishes as a hole is read back as no value at
all, so writing one as a PRESENT cell moves the twin's own missing
counts against the description it was built from. It also refuses a
spelling already written. It PREFERS not to wear the pair rather than
refusing to, and that is deliberate: a pair can be any text — a column
of `(1)` and `(2)` wears `(` and `)` — so a rule that refused every
spelling wearing the pair would refuse every spelling this branch can
make and never finish. Past a bound of `count * 4 + 64` the pair alone
is conceded, because a repeated cell and a cell read as absent are both
worse than a cell counted in the wrong class.

This branch kept only two of the three refusals until 2026-08-27, and
no column reaching it was built from the profiler while the third was
added, so it is recorded as a guard rather than as a demonstrated
repair.

## G6B. Joined-number columns (`joined_numbers`)

Added by Phase 4; like G6A and G7A this section was written after the
implementation shipped, which is the wrong order and is recorded in
G13. It is the longest of the three because this role's pairing walk is
byte-determining and nothing outside it fixes the answer.

### G6B.1 What the profile supplies

A joined column holds cells such as `120/80`: two or more NUMBERS
written in one cell with a fixed separator between them. Published:

| key | what it holds |
|---|---|
| `parts` | one full numeric block per POSITION — the same block G5 and G6 consume, measured over the cells that split |
| `separator` | the exact text between two positions |
| `n_parts` | how many positions |
| `n_joined` | how many cells split that way |
| `n_unparsed` | how many present cells did not |
| `part_min_widths` | the smallest written width of each position |
| `part_agreements` | one number per PAIR of positions, each −1 to 1, in the order (1,2), (1,3), … (2,3), … — how strongly the two rise and fall together BY RANK |
| `part_above` | one count per pair — how often the earlier position stands above the later |

**`part_agreements` and `part_above` make this the one role in
synthtwin today that publishes structure between two quantities and
reproduces it.** The structure lives INSIDE a cell, between the
positions of one column; it says nothing about any other column, so the
one-column-wide bound stated elsewhere is unaffected.

Each position's block describes only the `n_joined` cells that split,
so it echoes `n_joined` as its own `n_rows` — NOT the table's. A
reader checking that block against the table's row count refuses every
column with an unparsed cell; the two coincide only when `n_unparsed`
is zero, which is why that defect survived a whole phase.

### G6B.2 Each position is a numeric column

Each position is built by G5 and G6 unchanged, over a view of the
column carrying that position's block and `n_joined` as its present
count. **G5.2's grain rule applies**: the STRATA take that
position's own `n_distinct_values` and not the column's counts, which
are counts of whole CELLS. The spelling budgets do NOT — they keep the
counts the block arrives with, because a joined position is a
projection of whole joined cells and the cell count is a safe ceiling
on the spellings one position can wear, while a count of numbers cannot
buy a second spelling of one number. Its word budget is
G5.3's, and G4.3 states the whole: the sum over positions, plus a
RESERVE of `max(n_joined - 1, 0)` for every position after the first,
drawn after all the positional words.

A finished cell is then

```
cell = pad(v[0], part_min_widths[0]) + separator
     + pad(v[1], part_min_widths[1]) + separator + …
```

where `pad` adds leading zeros until the text is that many characters
wide and never truncates.

### G6B.3 Why a pairing step exists at all

`_numeric_content` places its values by RULE and not by chance — the
words decide arrangement, not which numbers come out — so two positions
built from it emerge in the same order and pair up in lockstep.
Measured: a 400-row column whose real cells held 387 different readings
came out with 117, in runs of near-neighbours, while each position's
own published distribution was right to the digit. Drawn independently
and left alone, two positions of a reading agreed at −0.02 where the
real column agreed at 0.83, and a twin cell could hold a second number
above a first that no real cell ever did.

Every step below swaps two rows' numbers within ONE position, so each
position keeps its multiset to the last cell and every number published
about it — ladder, mean, spread, styles, widths — is untouched. Only
the pairing moves.

### G6B.4 The pairing walk, step by step

Write `T` for `n_joined` and `last` for `n_parts - 1`.

**1. Sort.** Each position's spellings are ordered by `(value,
spelling)` ascending, value being the spelling read as a number. This
is the rank-for-rank start: largest with largest.

**2. Choose each position's start.** Position `0` is the ANCHOR and is
never moved, here or below. A pairing is only ever relative — permuting
every position the same way writes the same cells in a different order
— so one position may be held still without losing a single
arrangement, and holding the FIRST one still is what leaves a
two-position column the same walk it was: the same position moves under
the same start rule, so nothing about such a column changes on account
of the anchor.

For each position `p` from `1` to `n_parts - 1`, let `A` be the
published `part_agreements` entry of the pair `(0, p)` — seat `p - 1`,
since the seats run `(0,1), (0,2), … (1,2), …` — or `0.0` where the key
is shorter than that. Then

- `A < -0.4`: position `p` is reversed, seat `i` taking seat
  `T - 1 - i`;
- `-0.4 <= A < 0.4` and at least `max(T - 1, 0)` words remain in the
  reserve from `(p - 1) * max(T - 1, 0)` onward: position `p` is
  permuted by `permutation(T)` of G3.4c, drawn from the reserve
  STARTING AT THAT OFFSET — each shuffling position takes its own
  slice, which is exactly what G4.3 sets `T - 1` words aside per
  position after the first for;
- otherwise: it is left rank for rank.

A low target starts from a shuffle because it is already near it, and
a strongly negative one from the REVERSED order — seat `i` taking seat
`T - 1 - i`, as the first rule above says — because the walk cannot
travel the whole way from rank against rank inside its try ceiling.
This paragraph said "from rank against rank" until review round 8 of
L7, which is the opposite of the rule it stands under: at `A = -0.5`
an
unchanged rank order starts near `+1` and the reversal starts near
`-1`.

**IT IS THE PAIR WITH THE ANCHOR AND NOT A MEAN, AND IT WAS A MEAN
UNTIL LANDING L7.** While step 3 moved the last position and nothing
else, one choice served every pair the walk could reach, and the mean
of the scored entries was that choice — computed as a binary64 running
sum in published order and divided once, because a mathematical mean of
`-0.4, -0.4, -0.4` is exactly `-0.4` and takes the permutation branch
while the sequential sum gives `-0.4000000000000001` and takes the
reversal, and the two write different cells. Now every position moves
and every position has a target of its own, so a mean would let a fact
one position owns decide another position's start. Three positions
publishing `-0.68, 0.4, 0.4` average `0.04` over every entry and
`0.4` over the two the old walk scored; the rule here reads `-0.68`
for position two and reverses it, and `0.4` for position three and
leaves it rank for rank. For a two-position column all three rules are
the same rule, because its only pair is the pair with the anchor.

**3. Every position but the anchor moves,** taken in turn — try number
`t`, counting from zero, moves position `1 + (t mod (n_parts - 1))` —
and **every pair is scored**, because a pair has two different
positions and at most one of them can be the anchor. Choosing the
position by turn costs no reserve word; drawing it would consume the
reserve at a different rate and rewrite every two-position column's
cells for a choice that has only one answer there.

**THIS WAS A REAL BOUND ON WHAT THE ROLE REPRODUCED, AND IT IS THE
RESIDUAL LANDING L7 CLOSED.** The walk moved the LAST position alone
and scored only the pairs whose later member was that position. With
`n_parts` of 2 there is one pair and it is that pair, so nothing
showed. With THREE OR MORE, every pair among the earlier positions was
neither moved nor scored: those positions kept the ascending order
step 1 sorted them into, so their agreement came out at `+1` whatever
the description published, and no term of the distance ever noticed.

Measured on a 100-row three-position column built from 25 copies each
of `1/4/10`, `2/3/20`, `3/2/30` and `4/1/40` — whose first two
positions are perfectly anti-correlated, published `-1.0`:

| pair | published | before | now |
|---|---|---|---|
| (1,2) | −1.0 | **+1.0** | −0.9922 |
| (1,3) | +1.0 | −0.144 | +1.0 |
| (2,3) | −1.0 | −0.144 | −0.9922 |

and over a wider battery — twelve columns of three and four positions,
FORTY seeds, 2,160 pairs of which 960 are between two EARLIER
positions:

| | before | now |
|---|---|---|
| agreements outside G12.9's window | 1,560 of 2,160 | 665 of 2,160 |
| above-counts missed | 1,038 of 2,160 | **1 of 2,160** |
| early pairs outside the window | **960 of 960** | 407 of 960 |
| early pairs' above-counts missed | 945 of 960 | 1 of 960 |
| widest agreement gap | 1.0546 | 0.2433 |

**What is still bounded, stated rather than implied.** Aiming at a pair
is not reaching it: 188 of those 540 agreements still land outside
G12.9's window, because a column of three or four positions sets three
or six agreement targets that pull against each other inside one
bounded search. Those are MISSES and are reported as misses on both
pages, exactly as a two-position column's miss is. What is gone is the
class of pair that no term of the distance looked at.

**4. The distance.** Ranks here are ZERO-BASED — the smallest value of
a position takes rank `0` and the largest `T - 1`, with tied values
sharing the average of the ranks they span — and the middle is
`m = (T - 1) / 2`, the mean of those ranks. The divisors
`spread[p] = Σ_rows (rank[p][r] − m)²` are computed once and never
move, because no swap changes a position's multiset of ranks.

**The ORIGIN is a convention and not a byte-determining rule, and an
earlier revision of this passage claimed otherwise.** Every use of a
rank here is a deviation from the middle, and the whole expression is
translation-invariant: an implementation using one-based ranks WITH
their own middle `(T + 1) / 2` computes the same deviations, the same
spreads, the same numerators, the same distance, and writes the same
cells. What must not be done is to move the ranks and leave the middle
where it was — that is not the other convention, it is a defect, and
measuring it was how the false claim got in. Either convention is
conforming provided its middle matches it. Then:

```
room = 0.02 − 0.00005            G12.9's window, less half a unit at
                                 the precision an agreement is
                                 published to (4 decimal places)
tip  = 1 / (T * (pairs + 1))     0 when there are no pairs
gap[pair] = |agreement[pair] − part_agreements[pair]|

away =  |distinct_cells − wanted| / T
      + Σ_pairs |above[pair] − part_above[pair]|
      + Σ_pairs (gap[pair] − room  if gap[pair] > room  else 0)
      + Σ_pairs (min(gap[pair], room) / room) * tip
```

where `agreement[pair] = (Σ_rows (rank[a][r] − m)(rank[b][r] − m))
/ sqrt(spread[a] * spread[b])` over the pair's two positions `a` and
`b`, taken as 0 when the divisor is 0.

**The terms are scaled differently on purpose, and each scale is a
measurement.** `part_above` is an exact count a pairing can meet
whenever the twin's own numbers admit it — which is not always, and
R-P4-144 measures where they do not — and one row out of it is one
cell holding a reading that cannot happen
— at equal weight the walk sold a row of it for a thousandth of
agreement and produced an impossible cell — so it carries FULL WEIGHT
PER ROW. The count of different cells is divided by `T`: weighting it
per row instead was built and was worse at everything — the agreement
fell from 0.834 to 0.559, two impossible cells appeared, and the count
it was chasing still stopped at 317 of 324 — so it competes fairly and
yields where it cannot win, and any shortfall is REPORTED (G11,
instance 4).

**AN AGREEMENT IS SCORED BY HOW FAR IT LIES OUTSIDE ITS OWN WINDOW,
AND IT WAS SCORED AS AN EXACTNESS UNTIL LANDING L7.** The three facts
are not held to the same standard by the tool that checks them:
`part_above` and the count of different cells are EXACT-OBSERVABLE,
checked value for value by `synthtwin validate`, while an agreement is
APPROXIMATED inside G12.9's window. Scored as an exactness, an
agreement already four ten-thousandths from its target outbid every
remaining different cell on a 240-row column — each of those is worth a
240th — and the twin held 185 to 231 of 240 published readings while
overpaying a fact it is never held to exactly. `room` is HALF the
published window, because the published agreement is rounded to four
places and the walk's own is not, so a bound met exactly is a bound a
rounding can cross.

**`room` IS THE WHOLE WINDOW, AND IT WAS HALF OF IT FOR ONE
REVISION.** Half was chosen for a rounding, and the rounding is far
smaller than half a window: an agreement published to four decimal
places carries at most `0.00005` of uncertainty, not `0.01`. Any margin
the walk keeps BELOW the published window is margin it will buy with an
exactly-checked fact — a swap moving a gap from 0.019 to 0.015 cut the
half-window term by 0.004, where one different cell on a 400-row column
is worth 0.0025, and both of those agreements are already inside the
range the validator accepts.

**`away` IS THE SCORE AND IT IS NOT THE ACCEPTANCE RULE.** The Σ over
pairs is a sum, and a sum cannot carry identity: it cannot tell one
above-count going from held to MISSED while another improves by one
from nothing happening at all. Full weight per row is exactly
what the sum already delivers, so the weights above are not what
forbids that trade — the per-pair refusal of step 5 is, and it runs
before this score is consulted. The scales themselves stay as they
are: re-weighting them was built and measured and was worse at
everything.

**The raw gap is kept as a TIE-BREAK and nothing more, SCALED TO THE
WINDOW.** Inside the window the walk still prefers the closer
agreement, because near-exactness is free where nothing is bought with
it. Each pair contributes at most `tip`, so every pair together
contributes less than `pairs / (T * (pairs + 1))`, which is strictly
less than the `1 / T` one different cell is worth: the preference can
never be spent on a cell. **That guarantee had no counterpart for
`part_above` and now has one**, but not from a weight — from step 5's
first refusal, which forbids a held above-count being sold whatever
the tie-break says. It had to be a rule rather than a scale, because
the trade the tie-break bought was one above-count against ANOTHER,
and no choice of weight tells those two apart. It is scaled to `room`
rather than to the whole range an agreement can take, because a tie-break spread from −1
to 1 is a hundred times too shallow to steer inside a window two
hundredths wide.

**`wanted` is not the column's `n_distinct`.** Cells that did not split
are replaced after the walk by stand-ins that are all ONE spelling,
which no joined cell wears, so they add exactly one to the number of
different cells however many there are. The walk is therefore asked for
`n_distinct - 1` where any such cell exists and `n_distinct` where none
does. Comparing the walk's result against the whole column's figure
instead made a 120-cell column holding 120 different cells report "120
published, 119 achieved" while the recount in the same report said 120.

**5. The walk.** While anything is still OWED, fewer than
`max(200 * T, n_parts − 1)` tries have been made, and at least two
reserve words exist:

Something is owed when the count of different cells is not the wanted
one, or any `above[pair]` is not its published value, or any pair's
`gap` exceeds `0.00005` — half a unit at the precision the agreement is
published to.

**THE STOPPING RULE IS THE OBLIGATIONS THEMSELVES, and it was a fixed
distance of `0.0005` for one revision.** A distance cannot serve: one
different cell is worth `1 / T`, so above about two thousand rows a
whole missed cell costs less than that threshold and the walk stops
with an exactly-checked fact still missed — at four thousand rows it
can stop before its first try. And the agreement half of the test is
the PUBLISHED PRECISION rather than the window, because stopping at the
window leaves the walk idle while it could still be improving a fact a
reader reads: measured on a correlated 300-row blood pressure, stopping
at the window left the twin agreeing at 0.8174 against a published
0.8343, where continuing reaches 0.8343. Continuing is not a trade —
what could trade a cell for margin is the SCORE, and it cannot.

**THE CEILING IS AT LEAST THE NUMBER OF MOVABLE POSITIONS.** `n_parts`
may reach `n_present + 2`, so a column admitted at a lowered parse rate
can hold many present cells of which few SPLIT — and `200 * T` tries
could then be fewer than the positions taken in turn, leaving a tail
position no try at all while its pairs are still counted in the score.
Measured: 602 present cells of which two split into 402 positions gives
401 movers against 400 tries. "Every pair is aimed at" is only true if
every position is reached.

- let `p` be the position this try moves, `1 + (t mod (n_parts - 1))`
  for try number `t` counting from zero, per step 3;
- take the next two reserve words, **counting from reserve word ZERO
  even when the permutations of step 2 already consumed some** — the
  walk does not continue after them, it starts again at the beginning
  of the reserve and reads the same words a second time. **Each restart
  begins one word further along than the last**: the `r`-th restart
  begins at reserve word `r mod max(len(reserve) - 1, 1)`, so a second
  pass over the reserve does not draw the pairs the first one drew;
- `i = bounded(w1, T)`, `j = bounded(w2, T)` by G3.4b;
- **the proposal step (G6B.4a) may move `i` and `j` to two other rows**
  — when the count of different cells is not yet the published one,
  AND ALSO when it already is and an above-count is still unmet, which
  is that section's `d == 0` bullet. This line named only the first
  case until review round 7 of L7; an implementer who read the summary
  and stopped would omit the second branch entirely and never repair
  an above-count once the distinct count was right;
- if `i == j`, or position `p` holds the same spelling at both, the try
  is spent and nothing moves;
- otherwise swap position `p`'s seats `i` and `j`, recompute `away`,
  and **accept when the new distance is less than OR EQUAL to the old
  AND the swap is allowed**. A swap is allowed unless one of three
  refusals applies, in this order, every one of them evaluated on
  EVERY try:
  1. it takes any pair's above-count from HELD to missed;
  2. it takes any above-count further from its published value, while
     the moved pairs' above-counts do not fall as a whole and no other
     above-count reaches its published value in the same swap;
  3. it takes any pair out of its window, while neither exact fact
     comes closer — neither the moved above-counts as a whole nor the
     count of different cells.

  Otherwise restore every carried quantity exactly.

**THE ABOVE-COUNTS ARE CARRIED BY IDENTITY, ONE ENTRY PER MOVED
PAIR**, in a fixed order, so entry `k` names the same pair on both
sides of the swap. A SUM cannot express these refusals: an above-count
can go from held to MISSED while another improves by one, the total
says nothing happened, and the agreement tie-break is the only reason
left to take the swap. Measured on a 150-row four-position column at
one seed, four accepted swaps did exactly that — at the fifty-seventh
the per-pair gaps went `(0, 3, 0, 0, 0, 0)` to `(0, 2, 0, 1, 0, 0)`
while `away` fell by 2.4e-5, and no pair had left its window, so the
refusal was never even reached — and the twin came out holding
`(65, 120, 32, 118, 31, 0)` against a published
`(65, 122, 32, 118, 31, 0)`. An independent transcription of this
section reproduced the same trade on its own columns, which is why the
refusals are numbered here rather than described.

**THE COUNT OF DIFFERENT CELLS IS A SEPARATE READING AND IS NOT ADDED
TO THEM.** It belongs to no pair, and it is the one exact fact
deliberately licensed to yield (step 4); added into the same number, a
gained cell could buy a lost row of `part_above` and no rule could see
the trade. It enters refusal 3 alone, as its own term beside the rows,
and refusal 3 asks the two facts SEPARATELY — "an exactly-checked
fact" is singular, and netting rows against cells is the arithmetic
these refusals exist to stop.

**REFUSAL 2's ESCAPE AND REFUSAL 3's SEPARATION EACH COST ONE
AGREEMENT AND ARE TAKEN ANYWAY, and saying so is the honest form of
the record.** Measured over twelve columns of three and four positions
at forty seeds, 2,160 pairs: the rules as written leave 550 agreements
outside their window; refusal 2 without its escape leaves 549 and
refusal 3 written as one combined total leaves 549. Neither variant
misses an above-count either, so neither costs a fact a reader is
told about — the difference is one pair's agreement in each case, and
both are kept for a reason a battery cannot show. Refusing a swap that
takes a pair ONTO its published count is refusing progress towards the
fact refusal 1 protects, and refusal 1 is absolute: without the escape,
a column whose remaining debt needs one seat to dip has no route to it
at all. And netting rows against cells is the collapse this revision
removes, so refusal 3 may not be written as the arithmetic being
repaired.

**REFUSAL 2 COSTS NOTHING WHERE THE ABOVE-COUNTS WERE NEVER AT RISK.**
On a correlated 400-row blood pressure at six seeds the twin holds all
324 different cells, all 400 above-rows and a worst agreement gap of
0.009948 with these refusals and without them alike.

**WHAT REFUSAL 1 GUARANTEES ACROSS A WALK**, and it is the guarantee
G12.9's "either holds it or has missed it" rests on: the set of pairs
holding their published `part_above` never shrinks. A pair the swap
cannot touch keeps its count, a refused swap is put back exactly, and a
moved pair cannot go from held to missed. Measured on the column above,
that count fell four times over 149 accepted swaps before these
refusals and falls at none of the 146 after them. Over the whole
battery — twelve columns, forty seeds, 2,160 pairs — the above-counts
missed go from one to none and the agreements outside their window
from 643 to 550.

**WHY THE WINDOW IS GUARDED SEPARATELY FROM THE SCORE.** Scoring an
agreement only beyond the window is what stops the walk buying margin
with an exactly-checked cell, but it leaves the inside of that window
flat, and a walk indifferent there lets a pair drift across the edge
and out. Measured on a forged three-position column at forty seeds, 120
pair measurements: flattening the interior took the pairs landing
OUTSIDE the window from 87 to 110, while the count of different cells
it was meant to protect was already met at every seed both ways — so
the trade bought nothing and cost 23. Refusing the drift directly
brings it to 73, better than either. The exception for an exact fact is
not optional: without it the same column lost ten above-counts of forty
where none had been missed.

**THE RESTART STEPS ALONG, AND IT RETURNED TO ZERO UNTIL LANDING L7.**
The reserve holds `T - 1` words for each position after the first and
the ceiling is `200 * T` tries, so a cursor returning to zero drew the
same `T / 2` pairs of rows two hundred times over: measured on a
240-row column publishing 240 different readings, the walk spent 48,000
tries on 119 distinct draws. Stepping the restart walks the reserve
against itself and costs no word and no draw.

**An equal swap is taken, and that is not a detail.** Three facts are
being met at once and they pull against each other: a swap that breaks
a repeated cell often costs a little agreement and gains it back two
swaps later. Taking only strict improvements stops on the first ridge —
measured, it left a column of 324 different readings at 276 while the
agreement was already right. Equal moves let the walk cross the ridge,
and the try ceiling is what stops it wandering.

**The reserve is DRAWN whether or not it is used.** The walk may
consume none of its words — it can begin already inside 0.0005 of every
target and stop — but the words are drawn from the stream regardless,
because that is what fixes the budget and therefore where the next
column starts.

#### G6B.4a Which two rows a try really swaps

`away` scales a row of `part_above` at a whole unit and one different
cell at `1 / T`, so a walk drawing its two rows at random spends its
ceiling on swaps that move the count of different cells by nothing at
all. **The objective is not re-weighted for this** — weighting that
count per row was built and measured and was worse at everything, per
step 4 — what changes is which swaps are put to it.

Write `seen` for how many rows hold each cell, `d = distinct_cells −
wanted`, and `R = 16` for how far either scan looks. Both scans run
forward cyclically from the drawn row and both fall back to the row as
drawn, so a try always has something to propose.

**EXACTLY WHICH ROWS EITHER SCAN VISITS, because an implementer who
counts from one instead of zero writes a different twin.** The scan
for `i` visits `(i + k) mod T` and the scan for `j` visits
`(j + k) mod T`, for `k = 0, 1, …, R − 1` in that order, where `i` and
`j` are the rows AS DRAWN. So `k = 0` is the drawn row itself: each
scan tests its own drawn row first, and the two scans count from
DIFFERENT origins. A scan that finds no qualifying row inside its `R`
candidates yields its own drawn row unchanged.

**And "a different spelling at `p`" is measured against the row the
FIRST scan settled on, not against the row `j` was drawn at**: the
partner scan takes the first candidate row that is neither the row `i`
ended at nor holds the spelling that row holds at `p`. Comparing
against the drawn `j` instead CAN select a different partner and so
write a different twin — the two agree only when the settled `i` row
and the drawn `j` hold the same spelling at `p`, which is why the rule
has to be stated rather than left to chance.

- `d == 0`, the count of different cells already met — TWO sub-cases,
  written as one bullet because an implementer reading in order must
  not take the first and stop. Write `s` for **how many turns position
  `p` has already had in this walk**: step 5 takes its positions in
  turn, so a try index `t` gives `p = 1 + (t mod (P − 1))` and
  `s = ⌊t / (P − 1)⌋`, the remainder and the quotient of one division,
  and `s` is read BEFORE the try index is stepped:
  - every `above[pair]` is its published value, or `s + p` is ODD: the
    two rows as drawn;
  - some `above[pair]` is not its published value and `s + p` is EVEN.
    **WHICH pair is named here, because two programs that chose
    differently would scan different rows and write different twins.**
    The pair is the EARLIEST, in `part_above`'s own published order,
    among those that BOTH contain position `p` and whose count is
    unmet. Position `p` may sit in several unmet pairs — at the
    `battery-11` start it sits in three, short by 14, 1 and 4 — and
    only the earliest is aimed at on this turn. If `p` sits in NO
    unmet pair, this turn proposes the two rows as drawn, exactly as
    the first bullet does.

    **"Unmet" means the count differs from its published value, and
    NOTHING ELSE.** In particular a program must NOT screen out a pair
    whose published count its own drawn numbers cannot express under
    any arrangement, even though such a pair stays unmet forever and
    is therefore aimed at on every ABOVE-COUNT-AIMING turn — the
    `(s + p)` EVEN ones — of every position it contains. On the odd
    turns nothing is pair-directed at all, so it is half of those
    positions' turns and not all of them.
    Screening it would be defensible and would write a different twin,
    which is why the rule is stated rather than left to judgement.
    R-P4-144 measures how many such pairs there are and records that
    the turns they consume, and the pairs behind them in the order
    that consequently get none, are an unmeasured contributor to the
    shortfall it reports. Then: `i` becomes the first row within `R`
    steps that holds that pair's earlier position above its later one
    where the count is too high, or does not where it is too low; `j`
    becomes the first row within `R` steps holding a different
    spelling at `p`. The
    acceptance rule refuses to trade one above-count for another, so
    the walk cannot reach the repair sideways and has to aim at it. On
    ALTERNATE TURNS OF THAT POSITION because aiming on every turn
    starves the agreement, which is the other fact still being
    improved: measured on a 300-row blood pressure, aiming every try
    left the twin agreeing at 0.8232 against a published 0.8343 where
    alternating reaches it exactly.
    **This branch is not optional beside the acceptance rule**: with
    the refusals in place and this proposal withdrawn, the battery
    leaves seven above-counts of 2,160 short of their published value,
    where the walk that could still trade them sideways left one. The
    wording here avoids one word on purpose — this bullet also carries
    the word `earliest`, and the guard of `docs/spec` that reads for a
    temporal end met with something else would take the pair for one of
    those.
- `d < 0`, the walk short of the count:
  - `i` becomes the first row within `R` steps whose cell more than one
    row holds;
  - `j` becomes the first row within `R` steps, other than `i` and
    holding a different spelling at `p`, for which the swap would give
    row `i` a cell no row holds AND would either give row `j` a cell no
    row holds or take from row `j` a cell another row also holds. The
    second half is not optional: the partner's own cell changes too and
    can go from unique to repeated, leaving the count where it was.
- `d > 0`, the walk over the count:
  - `i` becomes the row within `R` steps whose cell the FEWEST rows
    hold, the earliest where several tie. The mirror image of the rule
    above — "a row whose cell is unique" — finds nothing on a column
    holding six different cells over a hundred rows, and it is the
    rarest cell whose last few rows the count comes down by;
  - `j` becomes the first row within `R` steps, on the same terms, for
    which the swap would give row `i` a cell some row already holds AND
    would give row `j` one some row already holds or the same cell as
    row `i`.

**THE TURN IS THE POSITION'S OWN AND NOT THE WALK'S, and the `d == 0`
bullet above read "the try number" until amendment A-P4-52.** Step 5
reaches position `p` at try indices `p − 1`, `p − 1 + (P − 1)`,
`p − 1 + 2(P − 1)`, … which all carry ONE parity whenever `P − 1` is
even. A gate on the try number is therefore not alternating at all on
a column with an odd number of positions: it answers the same thing at
every turn a given position ever gets, so half the positions aim at an
above-count on all of their turns and the other half on none of
theirs. Position 1 is the ONLY mover of the pair it makes with the
anchor, so where position 1 is the starved half that pair has no route
to its published `part_above` at all. `s + p` alternates on each
position's own turns for every `P`, and wherever `P − 1` is odd it is
the SAME schedule the try number gave, so a column with an even number
of positions writes the same cells under either wording. Measured
through the reader, producer, loader and generator over forty
described columns of two to five positions at forty seeds each, 9,640
pairs: the pairs whose `part_above` the twin did not reach run 120 on
the try number, 153 on its phase flip and 44 on `s + p`, with the
agreements outside G12.9's window 3,665, 3,668 and 3,638. On eight
five-position columns, 3,200 pairs: 71, 96 and 12. The driver is
`tools/measurements/a_p4_52_l7_parity.py`.

**THE `p` IN `s + p` IS NOT LOAD-BEARING, and this method implied
otherwise until review round 4 of L7.** It staggers neighbouring
positions onto opposite turns, which reads as a reason, and it was
kept because dropping it moved bytes an earlier commit had set — a
circular argument, since that commit is the one that carried the
lockout this amendment repairs. Measured across THREE families built
three different ways, 15,560 pairs at forty seeds, the four phases
`s + p`, `s + p + 1`, `s` and `s + 1` miss 716, 709, 709 and 717
above-counts. `s + p + 1` has fewer misses than `s + p` in every one
of the three families, and `s + p` has fewer agreement excursions in
aggregate, 5,513 against 5,527: **no phase dominates across BOTH
reported metrics**, and the differences are not zero either — 716
against 709 is seven above-counts one phase reaches and another does
not.

**THE PHASE IS THEREFORE FIXED HERE, and `s + p` is the one.** An
implementation MUST gate on `(s + p) mod 2`, aiming when it is zero.
This is a reproduction rule, not a fidelity one: two programs that
chose different phases would both be defensible statistically and
would still write different twins from the same profile and seed,
which this document exists to forbid. All `p` amounts to is a stagger
of neighbouring positions onto opposite turns, and the measurement
says only that dropping it costs nothing consistent — not that a
conforming program may drop it.

Gating on the TRY NUMBER is refused for a second and stronger reason,
by a published fact rather than by a byte: it starves a parity, and
restoring it leaves seat 0 of the witness column reaching 49 against a
published 64.

`R` is a fixed small number and not the whole column because the scan
runs inside a walk whose ceiling is already `200 * T`, so an unbounded
scan makes the walk quadratic in the rows. **Sixteen is a
measurement**: over four columns at forty seeds each, counting different
cells held against published, a 36-row witness goes 30–35 at `R = 1`,
32–35 at 4, 32–36 at 8 and 33–36 from 16 upward, and a 240-row
all-different column goes 176–211, 192–231, 196–236 and 197–236 from
16 upward — flat from sixteen, at more than twice the running time by
sixty-four. A 400-row blood pressure reaches its published count at
every value of `R` and separates none of them. (Forty seeds; a
ten-seed reading of the same sweep put the witness at 33–36 from
sixteen, which forty does not support.)

### G6B.5 The cells that did not split

`n_present - n_joined` cells wore no such shape. The description says
HOW MANY and nothing else, so they are invented as ordinary text at a
budget of one distinct spelling, stepped past every cell already
written and every spelling this column publishes as a hole, and the
invention is REPORTED as a deviation of `n_unparsed`.

## G7. Datetime columns

### G7.1 The ordinal space

All datetime arithmetic in this method is **exact integer arithmetic in
ordinal space**. No float is formed anywhere in G7. The ordinal unit is
fixed by the published `resolution`, and on a `datetime` column by
`all_at_midnight` as well:

| `resolution` | canonical form | ordinal unit | ordinal of a value |
|---|---|---|---|
| `date` | `YYYY-MM-DD` | one day | days from 1970-01-01, proleptic Gregorian |
| `datetime` | `YYYY-MM-DD HH:MM:SS` | one second | `86400 * days + 3600*HH + 60*MM + SS` |
| `quarter` | `YYYY-Qn` | one quarter | `4 * (year - 1970) + (n - 1)` |
| `month` | `YYYY-MM` | one month | `12 * (year - 1970) + (MM - 1)` |

**A `datetime` column on the `local` clock whose `all_at_midnight` is
`true` takes the `date` row** (stage 2, 2026-09-14, plan P4-D39; on its
own clock only since landing 2b.3, 2026-09-15 — a column wholly at
local midnight values on the `utc` clock publishes instants that are not
values at midnight of that clock, and keeps the `datetime` row, G7.5). Its unit is one day,
and its ladder, its two ends and every interior rank are day
ordinals, exactly as for a column of dates; its cells still write a
clock, at midnight (G7.5). The ruling that stood here — one second on
every `datetime` column — handed a date stored as the date plus
`00:00:00` back with invented times of day: 800 of 800 real rows at
midnight became 2 of 800.

**THE TWO SPAN ROWS ARE SPANS, AND THAT IS WHY THEY HAVE SPACES OF
THEIR OWN** (plan P4-D4.3 item 2, amendment A-P4-24). A quarter and a
month each name a stretch of days rather than one instant, so neither
has a place in the day or second space: turning `2024-03` into a day
would put a value in the column that no cell of it holds. Both count
from the same origin, both are exact whole-number arithmetic on the
written figures, and for both the canonical form IS the cell text, so
their endpoints and their ladder rungs sort as text and come back out
of a file unchanged.

The day count is the proleptic Gregorian civil-to-days function the
shipped `parsing._days_from_civil` computes, and its inverse is
`parsing._civil_from_days`; this method requires exactly those two, and
the leap rule they use (a year divisible by four is a leap year, except
a century not divisible by four hundred).

**Some cells do not travel through this space**: the pinned cells of
G7.3 carrying a published moment whose seconds field is `60`, which are
built from that moment's own fields by
G7.5. The whole-second row above has one place for `HH:MM:59` and the
next for `HH:MM+1:00`, and none for the `SS` of `60` the profile
contract's canonical form admits — so a boundary carrying one is
built from the published moment's own fields, not from its ordinal, and
the space below is left to the ranks it is exact for.

### G7.2 What is generated, and what is a stand-in

```
P = n_present - n_unparsed     cells that parsed as dates
n_unparsed                      cells that did not
```

The `n_unparsed` cells are class-preserving neutral stand-ins (G10.4);
they are explicitly OUTSIDE the parsed-value representation obligation
(P2-D6) and are counted, not reproduced.

The `P` parsed cells are generated from the published
`date_percentiles` ladder, `earliest`, `latest`, `earliest_utc_offset`,
`latest_utc_offset`, `utc_offsets`, `datetimes_read_at`,
`datetime_separators`, `all_at_midnight`, `n_at_midnight` and, on an
`iso-mixed` column, `resolution_mix` (landing 2b.3).

### G7.3 Values: the same stratified inverse transform, in integers

The ladder `date_percentiles` is a SELECTION ladder — the profiler
picks the value at the rung rather than interpolating, because there is
no half-way point between two dates a calendar would recognize. The
generator interpolates in ORDINAL space, which a calendar does
recognize, and rounds down.

Convert the eleven rungs to ordinals `Lo[0] .. Lo[10]`. The cells are
ranks `r = 0 .. P - 1` (one cell per rank; datetime columns are not
stratified by value, because no datetime multiplicity map is
published). Then:

**The published tail PINS a rank to a published value** (landing 2b.6;
stage 3, plan P4-D328). The pinned ranks are the two TAIL BOUNDARY ranks
-- `m_lo = low_tail.rows` and `m_hi = P - 1 - high_tail.rows` -- and the
rank each PUBLISHED interior rung is selected from,
`k_j = floor((P - 1) * PCT[j] / 100)` for `j = 1 .. 9`, which by the
contract's D11 lies between the two boundary ranks, both included. Two
rungs selecting off one rank keep the LOWER rung's value, and a rung
whose rank is a boundary rank is left to that boundary, so the pins are
non-decreasing for any ladder a description can carry. **No end is
pinned, because no end is published**: rank `0` and rank `P - 1` belong
to the two tails, and a column publishing no tails at all is G7.3d's
ramp.

- `r < m_lo`, or `r > m_hi`: the rank belongs to a TAIL and is placed by
  G7.3b, or by G7.3c where that tail publishes which values it holds.
- `r == m_lo`: the instant is `low_tail.boundary`; `r == m_hi`: it is
  `high_tail.boundary`, each used exactly as published. "Exactly as
  published" means the boundary's OWN fields and not its ordinal
  wherever its seconds field is `60` (G7.5), because the space of G7.1
  has no place for a leap second.
- `r == k_j` for some PUBLISHED interior rung: the instant is `Lo[j]`,
  the rung's own published ordinal. A rung the tail rule withholds is
  null, pins nothing, and is never written anywhere.
- otherwise: `r` lies strictly between two pinned ranks `a < r < b`. Let
  `Lo_a` and `Lo_b` be their pinned ordinals and `X_a` and `X_b` their
  PLACES, below. The rank takes one word `w` and

  ```
  step    = X_a + (w * (X_b - X_a)) // 2**64       (X_a where X_b <= X_a)
  ordinal = step // 2**20,  kept inside [Lo_a, Lo_b]
  ```

  **A PIN'S PLACE INSIDE ITS OWN UNIT (plans P4-D130 and P4-D138).** One
  unit of the ordinal space is a stretch of time and not a point, split
  here into `2**20` steps. Take the distinct pinned ranks in order,
  `k_0 = 0 < k_1 < ... < k_m = P - 1`, with ordinals `Lo_i`. TWO SETS OF
  PLACES are built, and in both the first stands at
  `X_0 = Lo_0 * 2**20`, the start of its unit, and the last at
  `X_m = Lo_m * 2**20 + 2**20`, the end of its own.

  - THE MIDDLES: every other pin at `X_i = Lo_i * 2**20 + 2**19`, its
    unit's middle.
  - THE STRAIGHTEST: a HEAP — two or more pins on one unit that holds
    neither `k_0` nor `k_m` — stands at its unit's middle and does not
    move. Every other pin starts at its unit's middle; then 128 times
    over, for `i = 1 .. m - 1` in order, skipping the heaps,

    ```
    line = X_(i-1) + ((k_i - k_(i-1)) * (X_(i+1) - X_(i-1))) // (k_(i+1) - k_(i-1))
    X_i  = line, kept inside [Lo_i * 2**20, Lo_i * 2**20 + 2**20 - 1]
    ```

  With fewer than three distinct pins the straightest is taken. Otherwise
  each set is scored by how sharply it bends the count from unit to unit.
  A set puts a count `c(u)` on each unit `u`, in parts of `2**32` to a
  rank: `2**32` for each pin on `u`, and for each two neighbouring pins
  with `b` ranks strictly between them, `b * 2**32` on the first pin's
  unit where the two share a unit or `X_(i+1) <= X_i`, and otherwise
  `b * o * 2**32 // (X_(i+1) - X_i)` on each unit, `o` the steps of
  `[X_i, X_(i+1))` inside it. Over each unit `u` strictly between the
  first and last pinned units that holds a pin or stands next to one,
  with `C(u) = c(u) + 2**32`,

  ```
  r    = C(u - 1) * C(u + 1) * 2**32 // (C(u) * C(u))
  bend = the sum of (r - 2**32) ** 2
  ```

  and THE MIDDLES ARE TAKEN ONLY WHERE THEIR BEND IS STRICTLY LESS. Two
  pins on one value share a unit, so every rank between them stays on
  it.

  *Amended by the skeptic of the review of 158c811 (plan P4-D138).* The
  rule above P4-D138 was the straightest set alone, with no heap held,
  which is the cumulative count with the fewest changes of slope that
  puts every pinned rank in its unit. On a column that thins out or peaks
  that count is the flattest the pins allow, and it starves the heavy
  days: 500 dates over a week, drawn thinning from the first day, came
  back with the first day at 0.57 of its real count and a mean 0.32
  standard deviations late on every seed, and 1,500 dates peaking in a
  fortnight had the peak day at 0.74 and a mean 0.151 early, where the
  inclusive draw of 158c811 had held 0.79 to 0.89 and 0.06 to 0.11, and
  1.28 to 1.34 and 0.04 to 0.06. The middles alone give those back but
  not the flat column: 1.37 to 7.34 times the real per-day variance over
  a week to a fortnight. With both sets and the bend choosing, the
  thinning week measures +0.057 to +0.104 and 0.79 to 0.89, the peaked
  fortnight -0.059 to -0.037 and 1.28 to 1.34, and every flat short span
  of the gate below exactly as the straightest alone did.

  *Amended by the review of 158c811.* This rule drew over `[Lo_a, Lo_b]`
  inclusive, `ordinal = Lo_a + (w * (Lo_b - Lo_a + 1)) // 2**64`, so a
  pinned unit took a whole unit's share from the gap on each side of it
  and the pin on top. Measured on 3,000 dates drawn uniformly over sixty
  days at seed 4: the twin's per-day variance was 301.33 against the real
  column's 45.47, 6.63 times, with 31 January at 91 values against 44 and
  15 February at 105 against 42 -- a spike at every rung -- and both files
  validated with nothing missed. Taking each pin to its unit's middle
  alone left 1.47 to 1.83 times there and 6.40 times on 500 dates over a
  week, because a gap a day wide is then given half a day too much or too
  little. With the places above: 0.61 to 1.02 times the real column's
  variance on the sixty-day column over seeds 0, 4 and 11, and on spans of
  a week to two months at most 0.95 of what such a column varies by in
  expectation, against 3.37 to 23.8 before.

  and the ordinals drawn for the ranks strictly between `a` and `b` are
  SORTED among themselves before they are written back, so `O` is still
  ascending. The draw is in the ordinal space of G7.1 — whole days for a
  column of dates, of months, of quarters and for one whose every moment
  stands at midnight; seconds otherwise.

**Each rank that is NOT pinned spends exactly one word; a pinned rank
spends none.** The words are drawn in rank order, so the ranks inside
one gap take consecutive words and the next gap continues where the
last one stopped.

**The budget is unchanged: `P - 2` content words** (`_plan_column`), of
which the pins leave up to nine unread. That is what keeps the shared
stream in step — a column is HANDED its budget before it is built, and a
word it does not read is not a word another column takes — so a column
of dates consumes exactly the allocation it always consumed and no
column generated after it moves. Of 24 twins of unrelated shapes, 18 are
byte-identical across this rewrite and the 6 that moved are the two date
shapes; an independent set of 30 unrelated twins was byte-identical at
30 of 30.

*Amended by the repair pass of landing 2b.6.* This paragraph said that a
pinned rank draws its word and discards it. It does not: the
construction takes a word only for the ranks strictly between two pins,
which a probe of the shipped code measured as 389 words read of the 398
a 400-row column is handed. The rule above is what the code does, in the
generator and in the oracle alike; writing the other rule here left an
implementer who followed the document handing different words to
different ranks, and every committed date vector would have moved for
nothing.

*Amended again by the repair pass of landing 2b.14, which measured the
number this paragraph had just been corrected to carry.* It said the
pins leave up to ELEVEN of the handed words unread. The ceiling is
NINE. The tail pins at most eleven RANKS -- the two ends and the nine
interior rungs -- and neither end is ever drawn for, so the surplus a
column leaves unread is the number of DISTINCT pinned ranks less two.
Measured over fourteen column sizes from two rows to ten thousand, the
surplus runs 0, 1, 3, 5, 6, 6, 6, 8 and then 9 from a hundred and one
rows upward, and reaches ten at no size. The ceiling is pinned as a
number in `tests/test_date_spread.py`, together with the eleven it
comes from, so a later ladder that grows a rung cannot leave the
sentence standing.

WHY THE STRATIFIED PLACEMENT WAS WITHDRAWN. Each rank used to be its own
stratum, interpolated inside the band from `r / P` to `(r + 1) / P`, so
each day received almost exactly its expected count — a below-Poisson
spread, where a real table's per-day counts vary at least Poisson.
Measured over 54 runs of uniform, seasonal and admissions-style columns,
date-only and at midnight, at 400, 1,500 and 3,000 rows: the twin's
per-day count variance was **0.057 to 0.514 of the real column's**, and
it got worse as the column grew, because stratifying ever more finely is
ever further from sampling. The same floor also put **every one of the
nine interior rungs below its published value in all 54 runs** — one day
early on a 400-row admissions column, so a rung published as a Monday was
written as a Sunday. After this rule: every rung exact in 54 of 54, and
the ratio 0.52 to 1.41 **on columns whose shape eleven rungs can
carry** -- and, once each pin was given its place inside its unit (plan
P4-D130), 0.516 to 1.284 over seeds 4, 7, 11 and 23 at 400 and 1,500
rows, the shaped columns lower because part of what the ratio measured
before was the spike at each rung. That qualification is measured, not hedged (repair pass of
landing 2b.6): on a column whose values burst around three onset dates,
eleven pins over a year leave gaps weeks wide, the gap is filled evenly
as everywhere else, and the ratio stays at 0.34 to 0.47 at 400 rows and
0.15 to 0.18 at 1,500 — which is where the withdrawn construction
already was, so this rule neither helps nor harms that shape.

WHAT IT DOES NOT CARRY, and G12.4's window is drawn to match. A gap is
filled EVENLY, so structure the description does not publish does not
come back: the weekday composition, the time of day, days the real
column heaps values on, and a column whose values sit on a few scheduled
dates. On a seasonal or admissions-style column at 3,000 rows that
structure is most of the day-to-day variance and the ratio stays near
0.55. Each would need a fact no datetime block carries — a weekday
census, a time-of-day ladder, a value-count map over days — and each of
those publishes counts over small groups, so what may be published waits
on the stage that sets the disclosure floor. The twin's report says so
in its own enumerated sentence rather than printing "inside the range"
alone.

  The floor division is the stated rounding direction: **toward the
  earlier instant**, always, including for ordinals before the epoch
  (Python's `//` floors toward negative infinity, and that is the
  intended behaviour — a rule that truncated toward zero would round in
  opposite directions on either side of 1970). On an `all_at_midnight`
  column `Lo[]` and `ordinal` are day ordinals (G7.1), so the rounding
  is toward the earlier DAY.

  `ordinal` is inside `[Lo[j], Lo[j+1]]` by construction, so it is
  inside `[Lo[0], Lo[10]]`, which is `[earliest, latest]` because the
  profile contract's D11 makes the ladder's two ends those two instants.
  So no interior cell can fall outside the published range and the
  endpoints stay exact. The step from one to the other was an unstated
  assumption until D11: with the pair untied, a hand-made ladder end
  below `earliest` put interior cells before the published earliest
  instant, and describing the twin again gave back an `earliest` the
  report had said nothing about.

**The count passes, after every rank's instant and before any cell is
spelled** (plans P4-D191 and P4-D192). Each rank drawn between two
pinned ranks may move anywhere inside that gap: the gap's ranks are a
multiset, sorted again afterwards, and every pinned rank still reads off
its published value. Three counts the published facts fix are reached
that way.

- **A count at midnight withheld for its size** (P4-D191,
  `contract.midnight_withheld_for_its_size`: a column of moments, not
  wholly at midnight, not read on the shared clock with its offsets
  pooled, and not the joint ISO reading -- a joint column withholds
  that count for a reason of its own since review round 2's disclosure
  item 4, and no consumer can tell the two silences apart, so nothing
  is owed there). On a column counted in seconds, each rank asked on its own
  wall clock -- its offset applied on the shared clock -- with the line
  two or the floor: where the eleven published instants
  stand at midnight no more than half the time, every unpinned rank
  that is not a bare date and is written at midnight at the column's
  precision is moved one precision step later, or earlier where later
  leaves its gap, in rank order until fewer than the line stand there;
  otherwise every unpinned rank off midnight takes the nearest midnight
  inside its gap, in rank order, until fewer than the line stand off it
  and never all. Nothing moves where fewer than the line already stand
  on either side.
- **The widths** (P4-D192), on a column read on its own clock, writing
  no bare date, counted in days or in seconds, whose member shows
  widths and whose census names exactly ONE convention: every cell
  showing a width wears it, so the ranks whose day COUNTS INTO the
  census's word must number that count. A day counts into the word when
  it shows that width -- a numeric field below ten, or a textual
  member's day below ten -- or when it shows NO width at all, since the
  producer and the checker both absorb a showing-nothing cell into the
  column's one convention (P4-D278). **A DAY'S KIND IS THAT ONE
  QUESTION AND NOT THE NARROWER ONE** (P4-D294, the merge-close of
  2026-09-18): every rule below that speaks of a day's "width kind"
  means whether it counts into the word, which is the quantity these
  passes count, and not whether it shows a width, which is a different
  question wherever the census is an absorbed one. While they do not, each unpinned rank of the kind
  in surplus is offered the nearest instant a whole number of days away
  inside its gap whose day is of the other kind, earlier first at one
  distance, and the offers are taken nearest first, ties to the lower
  rank, until the count holds.
- **The different values** (P4-D192), on the same columns, where one
  instant is written one way (`contract.datetime_counts_reachable`: at
  most one offset KEY and none pooled, one mark at most and none pooled,
  each written-form census naming at most one form, no bare date beside
  moments) and the two published counts agree: the different
  written units -- a day, a month or a quarter, or minutes or seconds at
  the column's precision -- must number `n_distinct` less the stand-ins.

  *Amended by the dates pass of the stage-3 review (items 4).* Two
  narrowings of this clause were narrower than its own reason, and
  neither was written down as a decision.

  1. **A MONTH AND A QUARTER ARE UNITS OF ONE**, stepped by the layout
     exactly as a day is, and the pass ran on `date` and `datetime`
     alone. Measured at a floor of eleven, seed 4: 100 unique months
     from `2000-01` came back holding 74 different values and 100
     consecutive quarters the same, with no deviation reported, because
     the pass never ran and G12.5's envelope then admitted whatever the
     draw held. Such a column carries no width census and no midnight
     standing, so only the different-values pass has anything to do on
     it. After the amendment both come back at 100 of 100 at seeds 0, 1
     and 4.
  2. **ONE PUBLISHED OFFSET IS ONE WAY OF WRITING AN INSTANT.** The
     clause asked for no offset at all; a column every cell of which
     wears `+02:00` writes that offset after every moment, so one
     instant still has exactly one spelling. Measured: 200 timestamps
     seven minutes apart, all different, publishing `{"+02:00": 200}` in
     full, fell to the envelope -- and a file holding 29 of those 200
     values met every obligation the description states. What the clause
     refuses is more than one KEY, and a pool, because either lets one
     instant be written more than one way.

  Too many:
  each unpinned run sorted, a run of ranks on one unit holding no pinned
  rank moves whole onto the instant of the rank just below or just
  above it, where that lies inside its gap and is of the same width kind
  and midnight standing -- nearest first, then the shorter run, then the
  lower rank; and, where no such instant exists, onto the nearest
  instant any rank holds inside its gap of that same standing, earlier
  before later at one distance (plan P4-D258). **AND WHERE NO UNIT OF
  THE RUN'S OWN STANDING LIES IN ITS GAP AT ALL, THE MERGE IS MADE WITH
  A PAYMENT** (plan P4-D258 for the width kind; extended to midnight by
  item 2 of the dates pass of the second Codex round, 2026-09-19). The
  run moves whole onto the nearest instant ranks hold inside its gap of
  the OTHER standing in one respect, and exactly as many ranks elsewhere
  move BETWEEN HELD UNITS the other way -- each leaving a unit other
  ranks still hold, each landing on a unit ranks already hold, each
  flipping that one respect, and neither of the trade's own two units
  touched. Neither half changes how many different units are held, the
  two together leave that standing's count exactly where it stood, and
  no pinned rank moves; a payment that cannot be made in full is put
  back cell for cell. The width kind is traded first, at the single
  nearest offer, and the midnight standing after it, where the nearest
  four offers of each run are tried in turn -- because whether a merge
  can be PAID FOR is a fact about the ranks elsewhere, and the nearest
  target is often the one whose own block the payment would have had to
  draw on. MEASURED at a floor of eleven, seed 4, on 40 each of
  `2024-03-01T00:00:00`, `2024-03-02T00:00:00` and
  `2024-03-03T12:00:00`: with the width trade alone the twin held those
  three values 41, 39 and 35 times beside FIVE invented
  `2024-03-01T16:13:10` cells -- a non-midnight run stranded between
  midnight pins, with no unit of its own standing anywhere in its gap --
  missing both distinct counts, four against three, while the source
  passed and the twin kept all eleven rungs and the 80 cells the census
  puts at midnight. Too few: each unpinned rank sharing its unit is offered
  the nearest unit no rank holds inside its gap, of the same width kind
  and midnight standing, earlier first, nearest first, ties to the lower
  rank.

The two passes of P4-D192 run with the different values FIRST and the
widths second, again while either moved, at most four times, and each
unpinned run is then sorted. Where the different values are held too,
the widths pass offers each rank the nearest day of the other kind on a
unit no rank holds, and one already held only where none is free; a
split whose unit an earlier split took is offered the nearest unit still
free when its turn comes. And where the splits leave the count short, a
TRADE: in rank order, an unpinned rank sharing its unit takes the nearest
free unit of another standing -- width kind and midnight -- inside its
gap, where the first unpinned rank of that standing alone on its unit
can take the nearest free unit of the first rank's standing inside its
own gap (a midnight is sought one day at a time, from the one starting
its own day outward); both move, every standing's count holds, and one
more unit is held. A count the passes leave unmet is measured on the
finished cells and reported as a deviation under its own name. Measured on the final skeptic's clinical export of
2,000 rows at seeds 4 and 11: `n_distinct` 1077, `date_field_widths
{"unpadded": 1635}` and a withheld discharge count at midnight all come
back exactly, where the twins held 1065 and 1107, 1657 and 1667, and two.

`n_distinct` and `n_distinct_folded` on a datetime column are
APPROXIMATED under **the envelope of G12.5**, and held EXACTLY where the
published count lies inside that envelope and the pass above applies,
which it reaches (plan P4-D192); which is the one the
profile contract's matrix names for them (contract 9.6) and the one this
document derives from the rank windows of G12.4. An earlier revision
sent them to G5.6's numeric rung envelope with `g_max = 1`, which is a
bound on where a VALUE sits and not on how many different values a
column holds; two rules for one question is one too many, and G5.6 is
not the one either document's matrix points at. No repair is made for
these two counts (P2-D6, datetime cardinality); the recount of G12 names
them where the published count was missed.

#### G7.3b The tails: one shape, a derived end, and a stratum for every rank

*Stage 3, plan P4-D328. It replaces the two published ends, which are
gone from the format.* Each side of a column of dates publishes
`{boundary, rows, mean_distance, rms_distance, values}` and the tail unit
they are counted in (contract DT1 to DT4). Where `values` is null the
`m = rows` ranks beyond the boundary are drawn through ONE SHAPE whose
mean and mean square over a uniform share are the two published
distances. Everything below is binary64 arithmetic in `+ - * /` and
`sqrt` alone, each operation correctly rounded by IEEE 754 on every
platform, in the order written; no library power, exponential or
logarithm is used anywhere, and the one integer decision is made by
exact whole-number comparison.

Write `d1 = mean_distance` and `rho = rms_distance`, both at least one
unit by DT3.

1. **The shape.** `t = rho / d1`; `r = t * t`; where `r < 1`, `r = 1`.
   The POWER `n` is the largest whole number with
   `(n + 1)**2 <= r * (2n + 1)`, decided on the exact rational `r` is:
   with `r = top / bottom` in whole numbers (its significand and its
   exponent), `n` is the largest `n` with
   `(n + 1)**2 * bottom <= top * (2n + 1)`, found by counting up from
   nought. Then with

   ```
   a2 = 1.0 / (n + 2)                 de = 1.0 / ((n + 1) * (n + 2))
   b1 = 1.0 / (2n + 1)                c  = 1.0 / (n + 1)
   b2 = 1.0 / (2n + 3)
   qa = ((b1 - c) + b2) - ((r * de) * de)
   qb = (c - (2.0 * b2)) - (((2.0 * r) * a2) * de)
   qc = b2 - ((r * a2) * a2)
   ```

   the WEIGHT `w` is nought where `qc <= 0`; otherwise, with
   `disc = max((qb * qb) - ((4.0 * qa) * qc), 0.0)`,
   `q = -0.5 * (qb + sqrt(disc))` where `qb >= 0` and
   `q = -0.5 * (qb - sqrt(disc))` otherwise, the candidates are `q / qa`
   (where `qa` is not nought) and `qc / q` (where `q` is not nought),
   and `w` is the SMALLEST of those that lie in
   `[-1e-12, 1 + 1e-12]`, kept inside `[0, 1]`; where neither lies
   there, `w = 1`. The SCALE is
   `E = d1 / (a2 + (w * de))`, and the shape is

   ```
   a(s) = E * (s**n * (w + ((1.0 - w) * s)))
   ```

   with `s**n` by squaring and multiplying over the bits of `n`, the
   most significant first (`result = result * result`, then
   `result = result * s` where that bit is set). Its mean over
   `s` uniform on `[0, 1]` is `d1` and its mean square is `rho**2`,
   which is what makes the two published numbers the shape's own. It is
   the same family the numeric tail is read through, so the method has
   one tail shape and not two.

   The two integrals it is read with are

   ```
   A(s)  = E * (((w * s**(n+1)) / (n + 1))
                + (((1.0 - w) * (s**(n+1) * s)) / (n + 2)))
   B(s)  = (E * E) * ((((w * w) * s**(2n+1)) / (2n + 1)
                       + (((2.0 * w) * (1.0 - w)) * (s**(2n+1) * s))
                         / (2n + 2))
                      + ((((1.0 - w) * (1.0 - w)) * ((s**(2n+1) * s) * s))
                         / (2n + 3)))
   ```

   -- the integral of `a` and of `a**2` from nought to `s`, each power
   taken by the same squaring rule.

2. **The strata.** Rank `i` counted from the OUTSIDE (`i = 0` the
   outermost, `i = m - 1` the innermost) owns the share
   `s in [(m - 1 - i) / m, (m - i) / m]`. A drawn rank reads one word
   `u` and stands at
   `s = ((m - 1 - i) * 2**64 + u) / (m * 2**64)`, one whole-number
   quotient rounded once. **The words are read in RANK order**, which
   is ascending outer index on the low tail and DESCENDING on the high
   one, so the words run through the column exactly as its ranks do:
   the low tail's drawn ranks first, then each gap of the body, then
   the high tail's.

3. **The derived end, matched on both moments.** With
   `T = m * d1`, `S = m * (rho * rho)`, `inner = (m - 1) / m`,
   `P1 = m * A(inner)`, `Q1 = m * B(inner)` and
   `reach = a(inner)`, the STRETCH `k` on ranks `1 .. m - 1` and the
   outermost rank's distance `D` solve

   ```
   k**2 * (P1**2 + Q1) - 2 * k * T * P1 + (T**2 - S) = 0,  D = T - k * P1
   ```

   so that the expected sum of the `m` distances is `T` and the expected
   sum of their squares is `S`. Of the two roots
   `((-qb2 -/+ sqrt(disc2)) / (2 * qa2))` with
   `qa2 = (P1 * P1) + Q1`, `qb2 = -2.0 * (T * P1)` and
   `qc2 = (T * T) - S`, taken in that order, a root counts only where
   `k > 0` and `D >= k * reach` -- the outermost rank is never inside
   rank 1's own reach -- and the one nearest `1` is taken, the first on
   a tie. Where neither counts, `k = 1` and
   `D = sqrt(max(m * (B(1) - B(inner)), 0.0))`, the root-mean-square of
   the shape over the outermost stratum.

   *Why the moments and not the stratum mean (measured, design
   `date-clock-tails` section 6.2).* On a lone far value the stratum
   mean misses the published mean square by 14 to 22 per cent and the
   stratum root-mean-square misses the mean by 13 to 24 per cent, where
   this end misses by 0.1 to 3.9 per cent.

4. **The readable window.** `edge` is G7.3e's furthest distance. Where
   `D > edge`, `D = edge` and `k = (T - D) / P1` where `P1 > 0`: the end
   stands at the edge and the rest of the tail is stretched to keep the
   published mean, which is the point mass at the edge a column heaped
   on a sentinel really has.

5. **Whole distances.** Every distance is rounded to the nearest whole
   unit, halves UP, on the value itself -- its significand and exponent,
   never `value + 0.5` in binary64 -- and is at least one unit and at
   most `edge`:

   - rank `0` takes `D`;
   - a tail holding more cells than the smallest group size `F` puts its
     innermost ranks on ONE distance (the TIE GROUP): ranks `F - 1` to
     `m - 1` take
     `k * (m * A((m - (F - 1)) / m)) / (m - (F - 1))`, the mean of the
     shape over their strata together, and draw no word. The real tail
     held them on one value -- that is why `rows` exceeded the floor --
     and a twin that split them would describe a boundary further out
     (measured: `heap` seed 7, boundary 2022-03-17 against 2022-03-15
     and `rows` 40 against 39);
   - every other rank `i` takes `k * a(s)` at its own `s`.

   Then each distance is raised to at least the distance of the rank
   inside it, from the innermost outward, so the tail never folds; a
   column whose values are ALL DIFFERENT (G11) runs the two-pass step of
   G7A.4 instead; and each is finally kept at `edge` or less.

   **ALL DIFFERENT REACHES BOTH ROLES**, a column of dates exactly as a
   column of clock times, and a tail of such a column takes NO TIE
   GROUP: two ranks on one distance are two cells on one value, which a
   column whose cells all differ does not have. Measured: 400 dates, all
   different, whose high tail was drawn without this held 398 of them --
   three ranks on one day -- and missed both distinctness counts on a
   file whose own source met them.

6. **Where the rank stands.** On the low side the rank's ordinal is
   `anchor - distance * unit`, on the high side `anchor + distance *
   unit`, with `unit` the tail unit in the ordinal space of G7.1 -- one
   for days, months and quarters, sixty for a column written to the
   minute, one second otherwise, and 86400 for a column counted in days
   of the shared clock -- and `anchor` the boundary's own ordinal,
   except on the shared clock counted in days, where it is the UTC
   midnight of the boundary's own day.

7. **A rank standing at ONE PLACE steps off a hole and onto a midnight.**
   The outermost rank and the tie group draw no word, so each stands at
   one place and two rules apply to them, in this order:

   - a tail group of a column whose count at midnight is published and
     whose unit is a minute or a second stands at the midnight NEAREST
     its own distance inside the strata it covers -- the local midnight of a
     named offset's wall clock, the inner taken on a tie, its own
     distance where none lies in reach. Its strata reach
     `k * a((m - (F - 1)) / m)`, rounded as above;
   - a rank whose unit is named by one of the column's own published
     absent spellings, read under the column's own member, steps one
     unit INWARD until it is not, never below one unit. A derived end
     that is a declared missing value would be written as a cell the
     twin's own description reads as absent (the skeptic of the tail
     design, B8).

   The end is then raised to the group's distance where the group is
   further out, so the two stay in rank order.

8. **The gap of a tail rank IS its stratum** (G12.4): the two distances
   its own construction gives it at a word of nought and at the largest
   word, widened to the whole DAY it may be moved inside where one unit
   is a day of the shared clock -- half a day below and one second less
   than half a day above, so the room is exactly one day wide and two
   neighbouring ranks' rooms never name one instant twice -- inside
   which the move onto a local midnight may take it anywhere. Every later pass -- the step off a hole, the counts of
   different values and of widths, and the moves onto and off midnight
   -- moves a rank only inside its gap, which is what keeps every
   published tail fact inside the window of G12.14.

#### G7.3c A tail that publishes which values it holds

*Stage 3, plan P4-D329 (the owner's ruling of 2026-09-22).* Where a tail
holds few different values, or where its two distances would settle the
outermost value or a count below the floor, the description publishes
the tail's sorted distinct `values` instead of its root-mean-square
distance, and its mean distance beside them only where that settles no
count below the floor (contract DT1, DT3). It publishes them only where
each of its DISTANCES carries one canonical text; where a distance
carries two -- which a day of the shared clock does, holding a bare
date's midnight and a moment's two hours before it -- the tail
publishes its two distances instead, and the ranks it holds are drawn
through the shape below like any other.

The twin then writes the tail ON THOSE VALUES AND NOWHERE ELSE. With the
values in distance order, outermost first, and `m = rows`:

- every value takes at least one rank;
- with the mean published, `T = round(m * mean_distance)` halves up is
  the whole sum the counts must reach exactly. Each value from the
  outermost inward takes the FEWEST ranks that still leave the values
  inside it able to reach `T` exactly -- asked by a table over how many
  ranks are left and what they must still add, in whole numbers -- and
  the innermost takes the rest;
- with no mean published, or where no count can reach `T`, rank `i` of
  the tail takes value number `floor(i * v / m)` of the `v` values, so
  the ranks are shared as evenly as the values allow, the outer values
  first;
- **except that a column publishing `n_at_midnight` shares them by that
  count instead** (stage 3). With the mean withheld the description says
  only that each value is held at least once, so every other rank is the
  construction's to place, and it places them where the column's other
  EXACT facts need them: each value takes one rank, and the rest go to
  the first value, outermost first, that stands at a local midnight
  where the column publishes more cells at midnight than not, or that
  does not where it publishes fewer. Where no value answers, the even
  share above stands. Measured: 1,000 moments over five days under two
  offsets, 980 at local midnight, whose high tail lists a midnight and a
  noon and withholds its mean because three rows held the noon -- the
  even share wrote 102 noon cells for those three and the twin missed
  `n_at_midnight` by 84 and `all_at_midnight` with it.

Each of those ranks stands at its value's own ordinal and draws no word.
Its gap is that one place, so no later pass moves it.

#### G7.3d A column with no tails: the made-up ramp

*Stage 3, plan P4-D330.* A column too small for a boundary on each side,
or one so tied at an end that the two boundaries cross (contract DT2),
publishes no tail, no rung and no value of the table at all. Its cells
are still counted, so the twin writes a RAMP that meets the counts and
claims nothing: rank `0` stands at 1970-01-01 -- ordinal nought in every
space of G7.1 -- and rank `P - 1` at `(D - 1)` steps later, where `D` is
the column's published count of different values less the cells that
read as no date, capped at `P` and at least one, and the step is one
unit of the space, a whole DAY for a column counted in seconds so that
the passes onto and off midnight have a midnight of each day to reach. Every rank
between the two is drawn in the gap between them exactly as a body rank
is, and every later pass runs unchanged, so the published counts of
different values, of values at midnight, of resolutions and of written
forms are reached where the construction can reach them. The quality
report lists every value-bearing obligation of such a column as
withheld (validation method V3.5).

#### G7.3e The readable window a tail is kept inside

*Stage 3, plan P4-D331 (the skeptic of the tail design, B2 and B3).* A
twin cell must read back as the value the twin holds, so no rank of a
tail is placed where the column's own spelling cannot spell it:

- the calendar itself, the years 0001 to 9999, for every member;
- 1969-01-01 to 2068-12-31 for a member that writes a TWO-FIGURE YEAR,
  whose century the reader settles at `parsing.TWO_DIGIT_YEAR_PIVOT`:
  a twin that writes 1968 as `68` is read back as 2068 (measured:
  8 of 16 twins of a `dd/mm/yy` column wrote 1 to 3 such cells, each
  missing 4 to 7 of the tail's own checks);
- from the first day the workbook's date system can store, where the
  twin's cells are stored as workbook days: 1900-01-01 for the 1900
  system and 1904-01-01 for the 1904 one;
- on the SHARED clock, those edges come in by the widest offset the
  census names, because each cell is written on its own offset's wall
  clock -- and by one whole day where the unit is a day of that clock.

The edge is then the furthest distance from the boundary inside that
window, at least one unit. **The calendar is not inset on the local
clock**: a column holding a heap of `0001-01-01 00:00:00` -- the "no
date" value of two common systems -- is floor-safe, and its twin writes
that day exactly (measured: 40 cells of 40, against 0 under a one-day
inset).

### G7.4 Offsets: only where recorded

`utc_offsets` maps an offset text to a count, under the small-cell
floor, with a `(withheld)` key pooling everything below it and a
`(none)` key counting offsetless cells.

Allocation, over the `P` parsed cells in ascending rank:

0. A rank G7.5 writes as a bare date is settled first, with no
   offset: it consumes one from `(none)`, or from `(withheld)` where
   `(none)` has no count left (landing 2b.3).
1. **NO END TAKES AN OFFSET OF ITS OWN** (stage 3, plan P4-D328): the
   description names no offset for the two end rows, because it
   describes no end row at all, so both ends join the allocation of step
   2 like every other rank and the two keys are gone from the format.
   What remains of this step is the midnight rule. On a column G7.5
   moves onto a midnight -- wholly at midnight on the `utc` clock, or
   only partly at midnight on either clock
   (integration repair of landing 2b.3: 1,000 moments over five days
   under `+01:00` and `+02:00`, 980 of them at local midnight, stood
   mostly between pinned ranks of one instant, took their offsets in
   sorted order, and 82 were written an hour off midnight) -- each rank
   whose instant the layout of G7.3 fixes at ONE PLACE: a boundary rank,
   a published rung's rank, and a tail's derived end or group where it
   stands at one instant, with each rank standing between two pinned
   ranks of one instant -- takes the first offset,
   the real offsets in sorted order and then `(none)`, under which that
   instant stands at midnight and whose key has a count left (repair pass
   of landing 2b.3: a rung at a midnight of the shared clock whose `Z` was
   spent takes `(none)`, and ranks between p90 and the end on one such
   midnight were written `T02:00:00+02:00`).
2. The remaining counts are spent over the remaining ranks, taking the
   offset keys in the profile's own sorted key order, `(none)` and
   `(withheld)` last. The ranks are visited in ascending rank order,
   except on a column moved onto a midnight, where they are visited
   **SCARCEST FIRST** (stage 3, repairing plan P4-D254): each remaining
   rank is counted for how many keys both have a count left AND put a
   midnight inside that rank's own gap (the bounds of G12.4), and the
   ranks are taken in ascending order of that count, ties in ascending
   rank order. Measured on 1,000 moments over five days under `+01:00`
   and `+02:00`, 980 of them at local midnight: spending in rank order
   gave a key feasible for nearly every rank to ranks that had another,
   and the 84 ranks in the twelve-hour gap between the last rung and the
   high boundary -- where only `+02:00` puts a midnight inside the gap --
   found it gone, so the twin held 896 and missed both midnight
   obligations. Counting first and spending the scarcest first writes
   all 980. Where every key is feasible for every rank the count is the
   same for all of them and the order is ascending rank order again, so
   no column outside this rule moves a byte.
3. A cell allocated `(none)` is written with **no offset**.
4. A cell allocated `(withheld)` is written with **no offset** as well,
   and this is a loss, named as one: the profile does not say which
   offsets those cells carried, so the twin has no published way to
   spell them apart. See G11 instance 3.

**The clock conversion, which is not optional.** `datetimes_read_at`
says which clock the two tail boundaries, the values a tail lists and
the ladder are written on:

- `local` — one offset wrote the whole column, so the published text IS
  the local wall clock. The cell text is the canonical form of the
  ordinal, and the offset is appended as published.
- `utc` — two or more offsets appeared, so the published text is the
  INSTANT. A cell that carries an offset must be written on that
  offset's own wall clock, or the twin would re-profile to a different
  instant. So:

  ```
  local_ordinal = ordinal + offset_in_seconds     (resolution `datetime`)
  local_ordinal = ordinal                          (resolution `date`,
                                                    `month`, `quarter`:
                                                    no clock to shift)
  ```

  where `offset_in_seconds` is `+/- (3600 * HH + 60 * MM)` read from the
  offset text, and `Z` is zero. The cell text is the canonical form of
  `local_ordinal` followed by the offset.

`datetimes_read_at` is EXACT-OBSERVABLE (P2-R4-F3) and is met by this
construction whenever the published offset map holds two or more keys,
because the twin then writes two or more offset kinds. Where the map's
only key is `(withheld)` and the published reading is `utc`, the twin
writes one kind, re-profiles as `local`, and the report names it. That
corner is bounded: it needs two or more distinct offsets each used by
fewer rows than the small-cell floor.

**THE TWO KINDS ARE COUNTED OVER WHAT THE CELLS WEAR, AND NONE IS A
KIND** (*corrected by the dates pass of the stage-3 review, item 8*).
There are two kinds a cell can wear: a NAMED offset, written out after
the moment, and NO offset at all -- the census's own `(none)` member,
which is also what a rank spent from a withheld pool is written with.
The report counted the named ones alone, dropping the offsetless member
before measuring the diversity, so a column publishing
`{"(none)": 50, "+01:00": 50}` -- a census that withholds nothing --
was told that every offset it carried had been held back as too rare to
publish, on a twin that wrote both published members exactly. Measured
on 100 successive noon timestamps alternating no offset and `+01:00`,
at every seed.

### G7.5 Writing the cell IN ITS SOURCE'S OWN FORM, at the published precision

**Owner decision 5 is REVERSED** (owner ruling 2026-09-15, plan P4-D61,
landing 2b.6). The history is kept because it is the record of what this
rule cost while it stood. D12 fixed ISO 8601 with an explicit offset;
owner decision 5 amended it for twin CSV cells, because the producer
legitimately publishes offsetless dates and quarters and no output could
satisfy both D12 and the published facts, and it chose the ISO form at
the recorded precision for EVERY member. Residual R-P2-7 disclosed the
price: a month-first table yielded ISO twin dates, so a person's own
parsing call needed a different format argument on the twin than on
their table. Measured: `strptime('%m/%d/%Y')` parsed 400 of 400 real
cells and none of the twin's; a compact `YYYYMMDD` column's ISO twin
FAILED this tool's own validation, because the real cells are also
numbers and the ISO cells are not.

**So a twin datetime cell is written in the MEMBER that read the real
column — the document's `format` — at the precision the profile records,
and an offset is written only where the profile records a real one.**
The date half is written by the member; the clock half, the mark before
it and the offset after it are unchanged by the reversal. The member
fixes the field order, the delimiter and the year's width; what it does
not fix is carried by four censuses the description publishes, each
allocated to the ranks that can show it by the same smooth weighted
rotation the marks use, which draws no word:

| written by | census | the words |
|---|---|---|
| how wide the month and day fields were | `date_field_widths` | `padded`, `unpadded`, `first-padded`, `second-padded` for a cell whose two fields are both below ten; `first-field-padded`, `first-field-unpadded`, `second-field-padded`, `second-field-unpadded` for a cell where one alone is — ONE word per CELL |
| how a month NAME was written | `month_name_styles` | one joint `<case>-<length>-<mark>-<comma>` word, the length `either` on a cell of May |
| the case of a quarter's marker | `quarter_marker_case` | `upper`, `lower` |
| the case of a zulu offset marker | `zulu_case` | `upper`, `lower` |

**The joint words are joint on purpose, and that is a rule and not a
convenience.** On a column half written `%m/%d/%Y` and half `m/d/yyyy`
not one real cell mixes the two, so two independent censuses would have
written about half the eligible cells `03/5/2024` — a style no row of
that table uses. The same holds of a hand-entered column mixing
`17-MAR-2024` with `17 Mar 2024`, which carries its case and its mark
together. A rank that cannot show a convention — a day above the ninth,
a cell carrying no zulu marker — takes the column's commonest form and
is counted against no census.

**Each census is spent over its own classes of rank, and a named form
keeps its least (plans P4-D131 to P4-D133).** No census of written forms
carries a pool (contract D17 to D20), so what each owes is its named
counts and nothing else.

1. WIDTHS. A rank whose two numeric fields are both below ten takes a
   joint word; one whose FIRST field alone is, a first-field word,
   written with that field padded or not; one whose SECOND alone is, a
   second-field word likewise -- first and second in the member's own
   field order, and on a textual member the day is its one field. A
   class the census counts no word for takes the joint words' padding of
   that field, summed (`padded` and `first-padded` pad the first field),
   and one with none of those either takes that field padded. A rank
   whose two fields both show, where the census counts no joint word,
   takes the joint word built field by field from the convention the
   commonest named one-field word of that field does NOT wear, a field
   the census names no one-field word for being padded: a census naming a
   one-field word says that no cell of its table showing both fields
   wore that word's convention in that field, because
   `folded_width_tally` would have joined the named count to such a
   cell's joint word and the census would name the joint word instead
   (plan P4-D294, amended by the repair pass of the carried date items of
   2026-09-18). A rank that shows no width takes the commonest joint
   word, or the joint word the commonest first-field and second-field
   words make.
2. NAMES. A rank whose month is May takes the census's `either` words; a
   rank of any other month the words that name a length. A class the
   census counts no word for takes the other class's words with the
   length set aside: `either` read as `abbreviated`, a named length read
   as `either`.
3. MARKERS AND ZULU CASES are spent over every quarter rank and over the
   ranks carrying `Z`.
4. THE RESERVATION. Every class is spent by the smooth rotation; where
   that leaves a named form fewer places than the smaller of its count
   and the floor (never below two), and those leasts come to no more
   than the class's places, the leasts are reserved first, the places
   left are shared by the rotation over what each form is owed beyond
   its least (over the leasts where nobody is owed more), and the
   finished counts are spread by the rotation once more. A twin's column
   has its own number of cells in each class, and a proportional share
   of a smaller class fell under the floor: at a smallest group size of
   fifty, `second-padded: 97` came back under it and the twin missed an
   obligation the real table met.

*Amended by the review of 158c811.* This section spent a withheld pool
evenly over the forms a census left unnamed, spent the joint width words
over every rank showing a width and `padded`/`unpadded` over every rank
showing one field, gave a rank of May the commonest style, and reserved
nothing.

**The date half, per member:**

| `format` | the cell's date half | example |
|---|---|---|
| `iso-date`, `iso-datetime`, `iso-mixed` | `YYYY-MM-DD` | `2024-03-17` |
| `slashed-iso-date`, `slashed-iso-datetime` | `YYYY/MM/DD`, both fields padded | `2024/03/17` |
| `compact-date` | `YYYYMMDD` | `20240317` |
| `month-first-date`, `month-first-datetime` | month, day, four-figure year, slashed, each field at its allocated width | `03/17/2024`, `3/17/2024` |
| `day-first-date`, `day-first-datetime` | day, month, four-figure year, slashed, at its allocated width | `17/03/2024` |
| `two-digit-month-first-date` | month, day, `YY`, slashed, at its allocated width | `03/17/24` |
| `two-digit-day-first-date` | day, month, `YY`, slashed, at its allocated width | `17/03/24` |
| `dotted-month-first-date`, `dotted-day-first-date` | dotted, both fields PADDED (contract C6-22) | `17.03.2024` |
| `dotted-two-digit-month-first-date`, `dotted-two-digit-day-first-date` | dotted, both fields padded, `YY` | `17.03.24` |
| `textual-day-first-date` | day at its allocated width, the month NAME in its allocated case and length, four-figure year, on the allocated mark | `17-MAR-2024`, `7 September 2024` |
| `textual-month-first-date` | the month NAME, the day at its allocated width with the allocated comma, four-figure year, on the allocated mark | `Mar 17, 2024`, `Mar 17 2024` |
| `iso-month` | `YYYY-MM` | `2024-03` |
| `year-quarter` | `YYYY-` then `Q` or `q` as allocated, then the quarter | `2024-Q1`, `2024-q1` |

A month NAME is built by `month_spelling`, the one inverse of the
reader's own `month_of_name`, so a producer counting names and a
generator writing them cannot spell one month two ways — as
`clock_spelling` is the one inverse of `clock_ordinal`. The whole date
half is `written_date`, the one inverse of `parse_datetime`, and the
generator reaches it through `_cell_of_ordinal` and nowhere else.

**What the reversal does NOT change.** The figures after a second are
still zeros: the description says how MANY the finest cell carried and
nothing about their values, so any other figure would be a made-up fact.
The precision, the mark and the offset state are decision 5's own gains
and are untouched. And the members the reader does not reach — a
12-hour clock, `08APR2024`, Excel's unpadded hour — still fall to free
text; the reversal is about writing what was read, not about reading
more.

Then the clock half, exactly:

| `resolution` | `time_precision` | cell text |
|---|---|---|
| `quarter` | `quarter` | `YYYY-Qn` |
| `month` | `month` | `YYYY-MM` |
| `date` | `date` | `YYYY-MM-DD` |
| `datetime` | `minute` | `YYYY-MM-DD` + mark + `HH:MM` |
| `datetime` | `second` | `YYYY-MM-DD` + mark + `HH:MM:SS` |
| `datetime` | `subsecond` | `YYYY-MM-DD` + mark + `HH:MM:SS.` + `subsecond_digits` digits |

then the offset suffix, when one was allocated: `Z`, or `+HH:MM`, or
`-HH:MM`, exactly as the offset key spells it.

**The table is COMPLETE, and that is now true of the contract as well**
(P2-C1-F6). Revision 1 of the profile contract permitted a sixth pair —
`resolution: datetime` with `time_precision: date` — for which no cell
text exists: written `YYYY-MM-DD` the column re-profiles with
`resolution: date`, and written with seconds it re-profiles with
`time_precision: second`, and both fields are EXACT-OBSERVABLE. The
producer cannot make that pair, because a value carrying no time of day
does not read as a date AND time at all, so the contract's invariant D6
now refuses it and its loader enforces that. Every pair a description
can carry has a row above.

**An offset is written only where `resolution` is `datetime`** (contract
invariant D9). A whole date, a month and a quarter have no time of day
for an offset to move, and a cell written `2024-03-15+02:00` reads back
as no date at all.

**THE TWO ENDPOINT CELLS ARE BUILT FROM THE PUBLISHED ENDPOINT'S OWN
FIELDS, NOT FROM ITS ORDINAL** (review item P2-C2-F5). G7.3 pins ranks
`0` and `P - 1` to `earliest` and `latest` "used exactly as published",
and this paragraph is what makes that sentence literal. For the two
SPAN resolutions the two routes cannot differ at all: a month and a
quarter ARE their canonical text, so the fields route and the ordinal
route write the same characters, and the pin is literal either way. The ordinal
space of G7.1 round-trips every instant a whole-second count can hold,
and there is one a real reader can still hand a description that it
cannot: the last second of a leap minute, `SS` of `60`, which the
profile contract's canonical form admits at 6.6.2 because the shipped
reader accepts one. *Stage 3 (plan P4-D328): the values this rule is stated over are the two
TAIL BOUNDARIES and the values a few-valued tail lists, which are the
published values of a date column now; no end is published.* Read the
published moment as its four fields —
the date, `HH`, `MM` and `SS` — and build the cell as:

1. `resolution` `date`, `month` or `quarter`: the published text itself, which is
   already the cell text the table above asks for.
2. `resolution` `datetime`: take the published date with `HH:MM` and
   `SS` of `00`, move THAT to the clock G7.4 allocates for this cell —
   unchanged where `datetimes_read_at` is `local`, shifted by
   `offset_in_seconds` where it is `utc` — and then write the published
   `SS` back into the seconds field unchanged. Every offset is a whole
   number of minutes (contract 6.6.2 bounds the minute field), so the
   move never touches the seconds field and a `60` survives it.

The result is then cut to the recorded `time_precision` by the table
above, and the offset suffix follows as usual. The cut can drop no
published detail: `minute` is the only precision with no seconds field,
and the contract's D10 admits it only where every published moment's
`SS` is `00`. For every instant whose `SS` is `00` through `59` this produces
exactly the same bytes the ordinal route produces, which is why it moved
no case of G14.3's first nine when it was written; for `SS` of `60` it
produces the endpoint the description published, and G14.3's
`leap_second_endpoint` case freezes those bytes beside a committed
mutant that puts the ordinal route back.

**Both tail boundaries are therefore EXACT-OBSERVABLE, with no
leap-second exception**, which is what the ratified plan requires in its
own words —
both tail boundaries EXACT-OBSERVABLE in the representation owner
decision 5 fixes (`docs/plans/phase-2-generator.md` revision 5, P2-D6,
the datetime paragraph), the obligation stage 3 moved from the two ends
to the two boundaries without lowering it — and what the profile
contract's 9.6 now states in the same words. An earlier
revision of this section instead declared the endpoint REPORT-ONLY
because the ordinal space has no room for the value. That was a true
statement about the ordinal space used to lower a bar the owner set;
the bar is restored and the ordinal space is no longer the endpoints'
route.

**The rule above has no case that declines** (review items P2-C3-F2 and
P2-C4-F1). Step 2 writes the published `SS` back on BOTH clocks, at
every instant the canonical form can spell. An earlier revision of this
paragraph named two descriptions on which the endpoint would instead be
met as far as it could be, recounted and named — a `time_precision` of
`minute` whose endpoint carries seconds, and an `SS` of `60` while
`datetimes_read_at` is `utc` — and an implementation followed it,
sending the second of those back through the ordinal space. The revision
that withdrew those two named a third in the paragraph below: a
shared-clock endpoint whose own offset moves its cell off the end of the
calendar. Each was an exception written beside a sentence that says
there is none, and the previous paragraph's own words apply to all
three: a true statement about what a cell can show, used to lower a bar
the owner set. The first two pairs are refused by the profile contract's
**D10**, on the same terms as its D6 refusal of the
`date`-beside-`datetime` pair, and its **D11** ties
`date_percentiles.min` and `.max` to the tail rule -- both are `null`,
and every published rung stands between the two boundaries. The third
pair no longer exists to refuse: stage 3 publishes no end and no end's
offset, and the calendar's edge is G7.3e's obligation on every rank of a
tail, which is where the cell it was about is now derived. No pair
reaches a generator, so this method needs no rule for them, and it
states none.

**The tails are still checked on the written cells, not assumed from
the rule.** After the cells are built, each is
read back with the shipped date reader, put on the clock
`datetimes_read_at` names and counted in the published `tail_unit`: a
cell must stand on each published boundary, and exactly `rows` cells
must lie strictly beyond it. Silence there was the defect: a fact the loader accepted
was quietly changed on output. The check is not a formality now that D10
and D11 stand, and it is not vacuous either: it fails on any
implementation that stops writing the ends from their own fields, which
is the regression this whole section exists to prevent, and a conforming
repository owes a case that puts that regression in and watches the
check catch it. What it is NOT is a route by which a
description gets a lesser tail. Every description this contract's loader
accepts has tails this method writes exactly; a disagreement here is a
defect in the implementation, and the run says so in as many words
rather than passing it off as an outcome the description asked for.

- **The mark between the day and the clock is the one allocated from
  `datetime_separators`** (stage 2, 2026-09-14, plan P4-D39). The ruling
  that stood here — `T` on every `datetime` cell, because the parser
  accepts `T`, `t` and a space and one choice had to be made for the
  bytes to be fixed — fixed the bytes at the cost of the source's own
  spelling: a stamp written with a space came back with a `T`, so code
  splitting on the space worked on every twin row and failed on every
  row of the real table. The bytes stay a fixed function of the
  description:

  1. Take the names of `datetime_separators` other than `(withheld)`,
     sorted: `lower_t`, `space`, `upper_t`, each weighted by its count.
     Where none is named and nothing is pooled, every cell is written
     with `T` and the steps below do not run.
  2. A `(withheld)` pool is split EVENLY over the PERMITTED marks the
     census leaves unnamed (landing 2b.3) — the three names, or `space`
     alone on a `month-first-datetime`, `day-first-datetime` or
     `slashed-iso-datetime` column — each taking the pool divided by
     their number, and the remainder one each in the order `upper_t`,
     `space`, `lower_t`; a mark given nothing is left out. Where no
     permitted mark is unnamed, the pool is not split. **Amended by plan
     P4-D220 and restored by plan P4-D222 (stage 2 closed by the owner
     rulings of 2026-09-17).** Contract D12 admits a pool only as the
     whole census and only over values a pool names no one in -- fewer
     than the line, or no more than two marks hold below it -- so each
     third of it is below the line and the twin described again pools the
     same count. Plan P4-D220 gave each rarer mark one value and the
     commonest the rest, which on a pool of thirty at a floor of twenty
     wrote twenty-eight `T` and the twin described again named them;
     writing the whole pool with one mark, the rule landing 2b.3 replaced,
     erased the spellings the pool stood for.
  3. The ranks this allocation covers are the ones that write a clock:
     on an `iso-mixed` column whose `all_at_midnight` is `true`, the
     ranks the form census gives `iso-date` write none and take no mark.
     Those ranks less the weights so far — the whole-date cells of any
     other `iso-mixed` column — are added to the commonest named count,
     the first name in sorted order winning a tie, or where nothing is
     named to `upper_t`, or to `space` on a slashed stamp.
  4. Every mark starts with a credit of zero. For the covered ranks in
     order, every mark's credit grows by its weight, the rank takes the
     mark with the most credit, the first in sorted order winning a tie,
     and that mark's credit falls by the weights' total. `upper_t`
     writes `T`, `space` a space, `lower_t` a `t`.

  The walk draws no word, and it spreads each mark across the date
  range, so the twin invents no link between a moment's date and its
  spelling. The published instants stay in the contract's canonical
  form, space-separated, whatever mark the cells carry.

  A `(withheld)` pool is not a deviation: described again at the same
  floor the twin pools the same count (landing 2b.3).

- **A column read jointly whose every value stands at midnight writes
  its whole dates as whole dates** (landing 2b.3, narrowing owner
  decision 4 and residual R-P4-12). Such a column is generated in whole
  days, so a bare date spells every rank exactly. Its `resolution_mix`
  is spent over the ranks by the smooth rotation of step 4 over the two
  forms, `iso-date` before `iso-datetime` on a tie, after the ranks whose
  instant the published tail fixes are settled in rank order: rank `0`
  and rank `P - 1` with their published offsets and, on a column the
  move onto a midnight below reaches, each rung rank and each rank
  standing between two pinned ranks of one instant, with every offset
  that instant stands at midnight under. A settled rank none of whose
  offsets is `(none)` or `(withheld)` is a moment; on the `utc` clock a
  settled rank that may carry no offset is a bare date while `iso-date`
  has a count left; each takes one from its form's count (repair pass
  of landing 2b.3: bare dates beside `T00:00:00+02:00` moments publish
  rungs at 22:00, rung ranks the rotation made bare dates were written
  22 hours early, and every twin of that shape missed). A rank given
  `iso-date` is written `YYYY-MM-DD`, with no mark, clock or offset. No
  other column writes a bare date.

- **A column counted in seconds that publishes `n_at_midnight` above
  nought has that many values moved onto a midnight** (landing 2b.3):
  one partly at midnight on either clock, or one wholly at local
  values at midnight on the `utc` clock. After G7.3's instants exist:

  1. The ranks the published tail pins never move: rank `0`, rank
     `P - 1`, and each interior rung's rank `floor((P - 1) * c / 100)`,
     which takes its published rung (the first rung wins a shared rank).
     Every other rank interpolated past a pinned value below or above it
     is brought back to that value.
  2. A pinned rank, or one standing between two pinned ranks of one
     value, whose cell is written at midnight counts toward
     `n_at_midnight`; midnight is asked of the WRITTEN cell, on the
     rank's own wall clock and cut to the column's precision.
  3. What is still owed is spread over the other ranks: each adds the
     count owed to a credit, and a rank is chosen where the credit
     reaches the number of those ranks, which is then taken back.
  4. A chosen rank moves to the local midnight nearest its instant, the
     earlier on a tie, brought inside the pinned values either side; a
     rank with no local midnight inside them is left. An unchosen rank
     written at midnight moves one precision step later, or earlier where
     later would pass its upper bound.
  5. A second pass over the unchosen ranks, in rank order, moves as many
     more as are still owed, by step 4.

  The set of step 1 is stated once in the implementation, so a change to
  what the tail publishes changes that set and not the construction. A
  count the two passes cannot reach is a deviation of `n_at_midnight`.

- **A column publishing no count of values at midnight is moved
  nowhere** (landing 2b.6). The repair pass of landing 2b.3 moved an
  accidental value at midnight off a column publishing `n_at_midnight`
  of nought, and the integration repair moved each dense run of such
  ranks out together; both are WITHDRAWN, because the nought they served
  is withdrawn. A nought a reader can tell from a suppressed count of
  one is that count: 400 moments a day apart at noon, and the same 400
  with a single row moved to midnight, published `0` and `1` and were
  otherwise identical documents. So the field is absent on both, the
  construction owes such a column nothing, and its twin may hold a value
  at midnight that the real column did not — a fidelity cost named here
  rather than paid in silence, and the one clause 3 of the owner's twin
  definition requires.

  The two endpoint cells carry the marks of ranks `0` and `P - 1`, like
  any other rank.

  **WITH ONE EXCEPTION, AND IT KEEPS AN EXACT FACT RATHER THAN
  RELAXING ONE** (review item P4-DATE-F2). Where the cell this rule
  produces is one of the spellings the column publishes among its
  absent cells — the keys of any column's `missing_by_source`, since a
  declaration reaches the whole table — another mark is offered, in
  order: each mark the census names, in sorted order, then the other
  common form, a space for `T` or `t` and `T` for a space; since
  landing 2b.3 the marks offered first are every mark step 2 writes,
  the pooled ones included. The first whose spelling is not absent is
  written (the stage 2 audit, 2026-09-14). A spelling a column's own
  calendar placeholder or stand-in pass judged absent is not a
  declaration and is not offered to other columns (landing 2b.3).
  **WHICH SPELLINGS THOSE ARE IS READ OUT OF THE DESCRIPTION** (repair
  pass of landing 2b.6): each decision published in `sentinel_verdicts`
  names the spellings its own pass took out (contract V5), and a key no
  decision names was made absent by something that reaches the whole
  table. The version this replaces counted — the keys denoting the
  judged candidate, with the column's pooled hole spellings added,
  against the verdict's `n_occurrences` — and a count cannot separate
  two keys writing ONE candidate day: twenty judged
  `1900-01-01 00:00:00` beside thirty `1900-01-01T00:00:00` a person
  declared put 50 cells against a verdict of 20, so the judged key was
  offered to every column and a second column's ordinary values were
  read as absent, which made the REAL table miss thirteen obligations
  of its own description. Any two of them spell the same instant at the same
  precision on the same clock, so nothing published moves; what moves is whether
  the twin's OWN description still counts the cell. A real column can
  hold a present cell at midnight written `2024-01-01` and, beside it,
  cells a declaration made absent as `2024-01-01T00:00:00`; the twin
  writes every parsed cell at the finest precision, reaches the second
  spelling, and hands back a cell its own reader calls absent — so
  `n_present` falls and, where the cell was an endpoint, an
  EXACT-OBSERVABLE end walks out of the twin over a separator nobody
  chose. The exception is asked ONLY at that collision, so no other
  cell and no frozen vector moves. Where EVERY offer is absent too, an
  interior rank of a column counted in whole units -- dates, months,
  quarters, and a column whose every moment stands at midnight -- is
  stepped to the nearest unit whose spelling is not absent, earlier
  before later, first inside its own G12.4 window and then inside
  `[earliest, latest]` (stage 2 confirmation review, 2026-09-15: a day
  declared absent in all three of its spellings otherwise received eight
  values, which read back as absent cells). A rank inside its window
  stays inside every rung's bound, because the window never falls below
  the unit before the rank's own. Only where no unit qualifies, or on a
  column written to the second, does the allocated form stand, G12's
  endpoint entry name a lost end, and the report name every value left
  in an absent spelling as a deviation of `n_present`: this rule
  declines to invent a spelling the description does not make possible.

  **And the census is given back** (stage 2 review, 2026-09-14; the
  stage 2 audit, 2026-09-14). Each cell whose mark that exception
  changed hands the mark it owed to the first other rank, in rank
  order, that was allocated the mark the changed cell now wears, still
  wears it, was neither changed nor given a mark before, and whose new
  spelling is not absent. A repeated spelling is allowed, but no change
  may leave the column one spelling fewer, nor one value fewer once
  upper and lower case are ignored: a rank whose spelling is the last
  copy of its kind, literally or folded, is passed over while the
  spelling it would take is already written (stage 2 closure review:
  five cells of three spellings came back as two values; stage 2
  confirmation review: a `t` given to the last copy of a day beside that
  day's `T` folded ten cells of three values into two, which is binary). The walk is linear: each
  pair of marks keeps its own place in its list of ranks.
  The finished marks are then counted against the allocation, and a
  shortfall no rank could take is a deviation of `datetime_separators`.
  A spelling is matched as absent whatever the case of its letters, as
  the reader matches it.

  **A column of moments whose absent cells were pooled** below the
  group size (`missing_by_class` `(withheld)` above zero), in a table
  that declared missing values, carries a REMARK in the report (the
  stage 2 audit, 2026-09-14; a remark since the closure review, which
  measured it filed as a failed fact beside an ordinary pooled blank):
  those spellings are not published, so the twin cannot avoid one, and
  a value written in it reads back as absent.
- **The fractional digits are zeros.** The profile publishes how MANY
  subsecond digits the finest cell carried and nothing about their
  values — the parser reads and discards the fraction — so any other
  digits would be an invented fact, and drawing them would cost words
  for a quantity no published fact constrains.
- **Every parsed cell is written at the same precision**, which is the
  finest the column recorded. That is what makes `time_precision`
  EXACT-OBSERVABLE: it is the finest precision any value writes, so at
  least one value must write it, and writing them all at that precision
  is the rule that needs no further fact. On an `all_at_midnight` column
  every cell is its day with a midnight clock at that precision —
  `00:00`, `00:00:00`, or `00:00:00.` and `subsecond_digits` zeros —
  carrying its allocated mark (stage 2, 2026-09-14), and the report
  recounts the midnight cells it wrote and names any that are not.
- `format` is EXACT-OBSERVABLE and IS reproduced (landing 2b.6, plan
  P4-D61): the cell is written through the member that read the real
  column, so a month-first source column yields month-first twin dates
  and re-profiles as `month-first-date`. It was not reproduced at all
  under owner decision 5 (P2-R4-F3), when such a column yielded ISO
  twin dates and
  a person's own parsing call needed a different format argument on the
  twin than on their table, so the field could not be reproduced at
  all; the owner reversed that decision and residual R-P2-7 is retired
  with it. The one column whose member its
  own twin cannot show is an `iso-mixed` column not wholly at midnight,
  which is written wholly as moments (R-P4-12).

### G7.9 Reaching a distinct count a mark census absorbed out of reach

**The defect this closes** (plan P4-D245, ledger K-2B-51; the owner on
2026-09-21, 'I think we need to fix'). Ruling 6 of the owner's rulings
of 2026-09-17 counts a written spelling below the census line into the
COMMONEST spelling, and that ruling stands: it is what keeps a census
from naming a handful of rows. So a column of 125 moments at midnight
on two days, 120 of them written with a space between day and clock and
5 with a `T`, publishes `datetime_separators` of `{"space": 125}` at a
floor of eleven — beside `n_distinct_folded` of THREE, because the
column really did hold three different spellings.

A construction that reads that census as an instruction about the CELLS
writes 125 spaces over two days. That is two different values where the
description publishes three, and a column of two values is read back as
BINARY (the taxonomy decides the kind on the count of values before it
asks whether they are dates). `synthtwin validate` then reported the
twin missing `axes.role`, `axes.statistical_type` and `midnight.count`
while the REAL table missed none — the tool telling the person their
twin was wrong for doing exactly what the description said.

**The rule.** After the marks are allocated (G7.5 step 2) and the
absent-spelling repair has run, the parsed cells are counted by folded
spelling. Where a column of dates holds FEWER folded spellings than
`n_distinct_folded` publishes, the construction may spend ranks on the
permitted marks (contract D12) the census leaves UNNAMED, in the order
`upper_t`, `space`, `lower_t`:

1. The number of ranks spent is bounded by the SHORTFALL the
   description itself publishes — `n_distinct_folded` less the folded
   spellings the cells hold AND less the `n_unparsed` stand-ins still
   to be written — and by a budget of `census_floor(floor)` less one
   ranks in all, whichever binds first. The stand-ins are counted
   though this pass never sees them: the datetime content builder
   appends exactly `n_unparsed` of them (G7.2, G10.4) after this pass
   runs, each a spelling no other cell of the
   column holds, so the finished column holds that many folded
   spellings more than the cells in hand. Counting only the cells in
   hand made the shortfall too large by exactly that many and the pass
   OVERSHOT — measured on 303 midnight moments over two days beside two
   cells no date reader accepts, where the twin wrote six different
   values against a published five, so `synthtwin validate` named
   `distinct.n_distinct` and `distinct.n_distinct_folded` on a column
   that had named nothing before this pass existed (the review of
   2026-09-21, item 1).
2. A rank is spent when its cell is at least eleven characters long, it
   wears the commonest NAMED mark, its respelling is not a spelling the
   table declares absent, its respelling is a folded spelling the cells
   do not already hold, its own folded spelling is still worn by
   another rank, and it is NEITHER OF THE TWO END RANKS, which are
   written as the description publishes `earliest` and `latest`. So no
   spend ever leaves the column one spelling fewer, none buys a
   spelling twice, and neither published end is respelled.

   **AND THE MARK IT IS TAKEN FROM IS LEFT AT OR ABOVE
   `census_floor(floor)`** (*added by the dates pass of the stage-3
   review, item 6*). The budget of item 1 keeps the mark this pass
   INVENTS below the census line, so that describing the twin counts it
   back into the commonest one and publishes the census exactly as it
   stands -- and that absorption only happens while the commonest one is
   itself still a count the census may print. On a SPARSE column it need
   not be: 22 dates in 2,000 rows, alternating a `T` separator and a
   bare date, publish `{"upper_t": 11}` at a floor of eleven, which is
   exactly the line. Seed 4 spent one of those eleven, leaving ten `T`
   beside one space; no count of that census then reached the line, so
   describing the twin pooled the whole census under `(withheld)` and
   `synthtwin validate` named `marks.upper_t` and `marks.unnamed` on a
   twin whose own generation reported nothing. The spend stops while the
   count it would take from is at the line.
3. The pass RUNS ON THE TWO ISO DATETIME MEMBERS ALONE — `iso-datetime`
   and `iso-mixed`, the members contract D12 permits all three marks —
   and is skipped on every other member, and on a census holding a
   withheld pool, which G7.5 already splits over every permitted mark.
   THE SKIP IS BY MEMBER AND NOT BY CHARACTER. A slashed stamp writes
   its date in fields of no fixed width, so its mark sits at no fixed
   index: `3/03/2020 13:37` carries it at index nine and
   `2024/06/20 13:37` — the frozen `slashed_pool` case — at index TEN,
   where it is the MARK and not a digit. The date members carry no mark
   at all. Until the independence repair of 2026-09-21 this item read
   'a member whose eleventh character is a digit of the date rather
   than the mark', which that frozen cell contradicts; a second
   implementer reading it literally would not skip
   `slashed-iso-datetime`. No byte moved when the reason was corrected,
   because D12 permits a slashed stamp the SPACE ALONE, so a census
   naming anything leaves it no mark unnamed to buy in any case —
   which is why the skip could be misstated for a landing without a
   committed file saying so.

**STATED IN FULL, because the three clauses above do not decide the
pass.** They say which ranks MAY be spent and how many; they leave four
things a second implementer has to invent, and two conforming programs
that invented them differently would write different bytes. The
independence repair of 2026-09-21 completed the statement rather than
letting the shipped code be the answer, for the reason G2.1's placement
is stated at that width:

4. **Where the mark sits, and what a respelling is.** On the members
   this pass runs on, the cell's eleventh character — index ten,
   counting from nought — is the mark between the day and the clock.
   A rank's respelling is that cell with that ONE character replaced by
   the spare mark and every other character of it untouched, which is
   why a cell shorter than eleven characters is passed over: it carries
   no mark to replace.
5. **Which rank takes a spare mark.** Each spare mark in turn, in the
   order `upper_t`, `space`, `lower_t` stated above, is offered the
   ranks between the two end ranks in rank order, lowest first, and
   each rank that meets every clause of item 2 takes it as offered. When a mark's offer reaches the last of
   those ranks, the next spare mark is offered the same ranks again
   from the lowest. The pass stops the moment the ranks spent reach the
   SMALLER of item 1's two bounds — the published shortfall and the
   budget of `census_floor(floor)` less one — and no further rank is
   offered anything.
6. **The clauses of item 2 are asked of the column as it now stands.**
   A spend changes which folded spellings the cells hold, so the rank
   offered a mark after it is judged against the column that spend
   left: a folded spelling one rank has just bought is a spelling the
   cells already hold, and a rank whose own folded spelling another
   rank has just left is no longer worn by another rank.
7. **The commonest NAMED mark on a tie, and a census that names
   nothing.** Where two names of the census carry the same count, the
   commonest is the first of them in sorted order — the same tie G7.5
   steps 3 and 4 settle the same way, on the same census. Where the
   census names no mark at all, no cell wears the commonest named mark
   and no rank is ever spent, so the pass leaves such a column exactly
   as it found it without being told to skip it.

**Why the budget is one below the line.** The twin is held to its
description by being DESCRIBED AGAIN, and the description of a column
wearing fewer than `census_floor` cells of a mark counts that mark back
into the commonest name by ruling 6 — the same absorption that created
the shortfall. So the published census is met exactly. A spend that
REACHED the line would publish a count the real column's census
withheld, and the twin would miss its own mark census instead: measured
on the shape above, eleven ranks and twelve alike miss `marks.space`
and `marks.unnamed`, while one through ten miss nothing at all.

**Where the spent ranks come from, and why they name no row.** The
count spent is a function of the PUBLISHED numbers alone. The count the
real column held — five, in the shape above — is not published, is not
read and is not reproduced: the twin writes ONE. So the twin carries no
number the description does not already carry, and a reader of the
twin's own description cannot see the mark at all.

**What it does not do.** It buys values; it does not excuse their loss.
A shortfall the budget cannot close leaves the column exactly where
G12.5's published envelope and `_kind_notes`' deviation already put it,
and a twin that holds fewer values than the census can supply is
reported missing its role as before.

**The stand-in term is witnessed one call at a time**, in
`tests/test_oracle_rule_witnesses.py`. The one frozen case that reaches
this rule (`date_absorbed_mark`) publishes `n_unparsed` of nought, so no
committed vectors file parts the stand-in road from the fallback, and
plan P4-D295 routes a new case into an existing file, where it would
move bytes. TWELVE columns with the answers worked by hand instead —
eleven midnight moments over two days, every one written with a space,
asked at shortfalls of nought and one, at budgets of one and two ranks,
on a slashed stamp, on a date member, on a census holding a withheld
pool, on a census naming nothing but the mark the cells do NOT wear, on
a census whose two names tie, and on a table declaring the respelling
of the first day absent — asked of the oracle's
`marks_bought_for_the_shortfall` and of the shipped
`_spellings_short_of_the_count` alike, with seven mutants (the stand-ins
left uncounted, the budget raised to the census line, both END ranks
opened, item 7's tie stated backwards, item 2's commonest NAMED mark
dropped, item 2's declared-absent spelling dropped, item 3's member skip
dropped) each turning that witness red. THE LAST FOUR ARE THIS
DOCUMENT'S OWN DEBT: the repair's skeptic measured sixteen one-clause
mutants of the rewritten function against every frozen case and the
eight rows then standing, and those four moved cells while moving
nothing any file or row could see — item 7's tie worst of all, since
nothing but the shipped code had ever pinned it, which is the one source
an oracle may not be written from. A clause this document states in full
and no row parts is a clause the oracle and the generator may both have
wrong. THE TWO NAMES DIFFER ON PURPOSE:
the oracle's is what it hands back and the shipped one's is the
shortfall it closes, so the pairing a reader checks is not asserted by a
shared name (the independence repair of 2026-09-21, ledger K-2B-42).

**It reasons about the FOLDED count alone**, and on one shape that
leaves the unfolded count further from its published value than it
found it. A census naming both `upper_t` and `lower_t` writes two
spellings of every instant that fold to one, so a column of 125
midnight moments over two days beside five spaces publishes
`n_distinct` and `n_distinct_folded` of three while the construction
already writes four different texts for two folded ones. This pass
sees the folded shortfall of one, spends a rank, and reaches the
published folded count exactly — taking the unfolded count from four to
five. Measured on that column: the twin missed `axes.role`,
`axes.statistical_type` and `midnight.count` before this pass and
misses `distinct.n_distinct` alone after it, three checks traded for
one. Holding the unfolded count instead was measured too — a guard that
spends only where the unfolded count is short as well returns that
column to its three misses and moves no other shape — so the trade is
recorded here rather than taken back. The entry K-2B-51 carries the
same measurement, so its rule is not read as a claim about every column
of dates.

## G7A. Clock columns (`time_of_day`)

This role was added by Phase 4 and this section was written after its
implementation shipped, which is the wrong order and is recorded as
such in G13. It is written from the behaviour the shipped tool has, so
that an independent implementer can reproduce it; it is not evidence
that the behaviour was reviewed before it existed.

### G7A.1 The ordinal space

A clock column holds TIMES OF DAY and nothing else: no date, no zone,
no offset. Each cell is a place in one day, and the role counts in
**integer ordinals** of the form's own unit. No float is formed
anywhere in G7A.

| form | unit | capacity | spelling |
|---|---|---|---|
| `hh-mm` | minutes of day | 1,440 | `HH:MM` |
| `hh-mm-ss` | seconds of day | 86,400 | `HH:MM:SS` |

The ordinal of a cell is `hours * 60 + minutes` for `hh-mm` and
`hours * 3600 + minutes * 60 + seconds` for `hh-mm-ss`. The spelling of
an ordinal is that map inverted and zero-padded to two digits per
field. Because the unit is the form's own, every ordinal in
`[0, capacity)` has exactly one spelling in that form, and no value the
generator interpolates is ever truncated or widened to fit a cell.

**What the reader accepts is EXACTLY these two shapes**, and the word
exactly is the rule rather than a summary of it: two ASCII digits in
every field, hours at most 23, minutes and seconds at most 59, nothing
before the digits and nothing after. Four shapes a reader might expect
are refused on purpose — a fractional part (a reading that dropped it
would describe such a cell approximately while publishing an exact
ladder), the leap second `23:59:60` (the ordinal space has no faithful
point for it, and making one up would write into the twin a time that
no clock face reaches), an hour written with one digit such as `9:30`
(the published spellings are fixed width), and anything else — a
date, an offset, a name.

**Nothing is trimmed before the reader looks**, and that is a fifth
refusal rather than an oversight. What this role publishes are the
CELLS THEMSELVES: the two endpoints and the eleven ladder rungs are
values some row wore, character for character. A cell wearing the form
the column did NOT publish is counted unparsed rather than silently
re-read, so a column of `hh-mm` cells with one `hh-mm-ss` cell among
them publishes `n_unparsed` of 1.

### G7A.2 What the profile supplies

Published: `clock_form`; the 11-rung `clock_percentiles` ladder;
`earliest`; `latest`; `n_unparsed`; together with the universal class
counts and `n_distinct` / `n_distinct_folded`. **This role publishes no
sixth key.** It has NO OFFSET MACHINERY AND MAY NOT INVENT ANY: the
datetime role's ten offset and resolution keys are absent here, so
there is no zone to carry, no reading to convert and no endpoint field
surgery. A clock time is a place in the day and nothing else.

The loader holds the published values to four rules before the
generator sees them: every published time wears the column's own form
(T1); the ladder begins at `earliest` and ends at `latest` (T2); the
ladder never goes backwards (T3); and at least one cell parsed (T4). A
fifth (T5) is the detection line — enough of the column's cells are
clock times for it to be read this way.

Fixed quantity used below:

```
P = n_present - n_unparsed        cells that parsed as clock times
```

### G7A.3 The one refusal this role adds

A day holds 1,440 different minutes and 86,400 different seconds, and
nothing else can be written in the column's form. So where

```
n_distinct - n_unparsed  >  capacity(clock_form)
```

the description asks for more different times than its form has, and
generation REFUSES before a single cell exists, naming the description
valid and the table impossible. The test is the FORM'S CAPACITY and not
the span between the two endpoints: a description whose own source met
every count is never refused here, which is the difference between a
description nothing can satisfy and one this method finds hard.

**The span is a separate matter and is not a refusal.** Where the
endpoints are close together and the column asks for many different
values, the form has room but the RANGE does not, and G7A.4's repair
runs out of places. Nothing is silently dropped: the twin holds fewer
different times than published and the generation report names the
shortfall as a deviation of `n_distinct`, alongside every ladder rung
the clamp moved. Measured on a forged 100-cell `hh-mm` column whose
ends were `08:00` and `08:10` -- eleven minutes for a hundred different
values -- the twin held 11 different times, reported a deviation of
`n_distinct` reading 11, and reported 8 of the 11 rungs moved.

**A description the PROFILER wrote can never have that shape**, and the
reason is worth stating because it tells an implementer exactly when
the clamp can bite. Write `lo` and `hi` for the ordinals of `earliest`
and `latest`. Every parsed cell is a clock time between those two
endpoints, so the number of DIFFERENT parsed cells is at most
`hi - lo + 1`. And `n_unparsed` counts unparsed CELLS while `n_distinct`
counts each unparsed spelling once, so `n_unparsed` is at least the
number of different unparsed spellings, and therefore

```
n_distinct - n_unparsed  <=  (different parsed cells)  <=  hi - lo + 1
```

on every description measured from a real column. The repair always has
a place to step into there.

The inequality is necessary and, on its own, not quite sufficient: it
bounds how many different times are wanted, and the repair also needs
the interpolation not to jump past them. That second half comes from
the ladder being a SELECTION ladder over the column's own values
(G7A.2, invariants T2 and T3), so its rungs are real cells in order and
the interpolation between two rungs stays between two values the column
held. With both halves the conclusion holds, and no profiler path was
found that breaks either. The clamp is reachable only from a
HAND-WRITTEN description, which this method accepts and must therefore
say what it does with -- and what it does is degrade and report, never
refuse and never quietly hold fewer. Sixty profiler-built clock columns
were checked against the inequality and none came within reach of it;
the inequality is the reason, and the check is only corroboration.

This is why G7A.3's first paragraph does not say the capacity test
guarantees a place for every value. It does not: it guarantees the FORM
has room, not that the RANGE does. Only the report closes that gap.

### G7A.4 Values: the tails, and the body between their boundaries

*Amended at stage 3 (plan P4-D328): a column of clock times publishes no
earliest and no latest value either, so its two ends belong to its two
tails and its body runs between the two published boundaries.*

The cells are ranks `r = 0 .. P - 1`, one cell per rank; clock columns
are not stratified by value, because no clock multiplicity map is
published. With `m_lo = low_tail.rows` and `m_hi = P - 1 -
high_tail.rows`, in the form's own unit -- minutes of the day for
`hh-mm`, seconds for `hh-mm-ss`:

- `r < m_lo` or `r > m_hi`: a TAIL rank, placed by G7.3b in this unit
  (or by G7.3c where the tail publishes its values), against the day's
  own ends: nothing beyond `00:00` below and nothing beyond the last
  minute or second above (G7.3e in this space).
- `r == m_lo`: the cell is `low_tail.boundary`; `r == m_hi`:
  `high_tail.boundary`, each the published TEXT, not a re-spelling of
  its ordinal.
- otherwise: the body, interpolated between the KNOTS -- the low
  boundary at position `m_lo`, each PUBLISHED rung `j` at position
  `P * PCT[j] / 100`, and the high boundary at position `m_hi + 1`,
  every position counted in hundredths of a rank times `2**64` so that a
  rank reading one word `w` stands at `100 * (r * 2**64 + w)`. A rung
  the tail rule withholds is not a knot. Let `(p0, v0)` and `(p1, v1)`
  be the two knots the rank's own position falls between, the last pair
  where it passes the end:

  ```
  share   = min(max(position - p0, 0), p1 - p0)
  ordinal = v0 + (share * (v1 - v0)) // (p1 - p0)        (v1 where p1 <= p0)
  ```

  identical in shape to G7.3's segment reading. The floor division
  rounds toward the EARLIER time, and `ordinal` lies between the two
  boundaries by construction, so no body cell falls into either tail.

**EVERY INTERIOR RANK READS ONE WORD, AS IT ALWAYS HAS.** A clock
column is handed `P - 2` content words and spends them in rank order;
rank `0` and rank `P - 1` draw none. A boundary rank and a tail's group
READ their word and set it aside, so every body rank keeps the word it
read before stage 3 and no column generated after this one moves
(G3, G4). A column with no tails at all spreads its ranks evenly over
its count of different values from `00:00` (the ramp of G7.3d), each
interior rank still reading and discarding its word.

**The all-different obligation is EXACT for this role**, and it is the
one shape where it is. Everywhere else a column's count of different
values falls to an envelope; here a closed finite space of times has a
place for each of them and the construction can take the next one. The
obligation applies where

```
n_distinct - n_unparsed  >=  P
```

and the repair is: in the BODY, keep the ordinal of the previous rank;
if this rank's ordinal is not above it, step to the previous ordinal
plus one; then clamp to one unit below the high boundary. In a TAIL it
is the two-pass step of G7.3b step 5: from the innermost rank outward,
a distance not above the one inside it is raised to that distance plus
one and then kept at the edge; then, from the outermost rank inward,
a distance not below the one outside it is lowered to that distance less
one, never below one unit. **The clamp runs inside BOTH passes**: with
the clamp applied only after the first, the ranks piled up at `00:00`
and `23:59` and 7 of 20 twins of an all-different column repeated a
value its description publishes as different (the skeptic of the tail
design, B5). The real column fits, because its own `m` values stood
between the day's edge and the boundary.

**AND NO PARSED CELL WEARS A SPELLING THE TABLE CALLS ABSENT.** The
ranks come out of the layout, which knows nothing about the spellings
this document's columns publish among their absent cells, so a rank can
land on one -- and the twin then writes a cell its own reader counts as
no value at all, one more absent cell and one fewer present one. After
the ranks are placed and before any cell is spelled, each BODY rank --
one strictly between the two tail boundaries -- whose spelling is one of
those is moved to the NEAREST unit of the window it was built in
(G12.10 above) that is not one of them, earlier before later at one
distance, and -- on a column whose values were all different -- one no
other rank stands on, so G11 survives the step. A boundary rank and a
tail rank do not move: the first stands at a value the description
prints and the second at a distance the published shape fixes, and a
twin that moved either would miss a published fact to keep a count. Nor
does a body rank whose window is one unit, which is a body with no slack
left in it. The search passes at most one unit per absent spelling and,
where the ranks must differ, one per rank.

*Added by the dates pass of the stage-3 review, item 5.* The stand-ins
of G7A.5 were stepped past the absent spellings from the day the role
landed and the clock VALUES were checked against nothing. Measured at a
floor of eleven: 99 minutes two apart from `07:00` with `08:00` declared
missing and held by eleven cells wrote TWELVE `08:00` cells at seed 0,
leaving 98 present against a published 99 and 12 absent against 11, at
seeds 0, 3 and 7. There are enough free minutes to keep both the
absent count and the uniqueness, and the step above takes one.

### G7A.5 The stand-ins

The `n_unparsed` cells are outside the obligation to reproduce a clock
value: they are COUNTED rather than described, exactly as the datetime
role's stand-ins are (G10.4). Each is stepped past four things — a
spelling this column has already written, a word this format reads as
"no value", a spelling that would read as a clock time in EITHER form,
and a spelling this column publishes as a hole.

The third of those is the one specific to this role. A stand-in that
reads as a clock time under the form the column did NOT publish is
still a cell the twin's own description would count differently from
the description the twin was built from, so it would quietly move
`n_unparsed` — and a twin that re-describes to a different profile is
the failure this whole document exists to prevent.

## G8. Label columns (`constant`, `binary`, `categorical`, `long_tail_labels`)

A label column consumes no content words. Everything is fixed by
published counts, which is why a fully determined label column produces
seed-invariant bytes.

### G8.1 Published levels and their variants

For each entry of `levels`, in the profile's own list order (the
producer sorts by descending count then by label), the entry's `count`
cells are filled as follows:

1. **`variants`** (owner decisions 9 and 11) maps an exact spelling to
   its count. Each key contributes exactly its count of cells, written
   byte-for-byte as the key spells it. Keys are taken in the profile's
   sorted key order.
2. **`variants_withheld`** maps an occurrence count to how many distinct
   spellings occurred that often. For each key in ascending numeric
   order — the key is a whole number written in figures, and the order
   is over the NUMBER, so `2` comes before `10` — and for each of its
   distinct spellings, one invented variant spelling is produced (G8.2)
   and used exactly that many times. **Which form each of those
   spellings must wear is fixed first, by G8.1a.**

   **Where step 3 is not reached, the label's OWN spelling is one of
   the spellings available to G8.2**, and it is offered to the LARGEST
   group whose target form the label's own spelling wears — which is
   the largest FORM-KEEPING group where the label has a written form of
   its own, and the largest group of all where it has none, because
   then every group's target is "no form" and so is the label's. Where
   the label HAS a form and G8.1a gives it to no group, the label's own
   spelling is not spent at all. It is available only where step 3 is
   not reached: a level whose published and withheld spellings do not
   cover its `count` is finished by step 3 writing the label itself, so
   that spelling is spoken for. It is worth offering because it is the
   one further spelling that folds onto the label while KEEPING ITS
   WRITTEN FORM, where a trailing space does not (P4-D18, amended by
   A-P4-47).
3. If the entry publishes neither key, or both are empty, all `count`
   cells are written with the normalized label itself.

The contract's invariant — each variant's count is at most its parent's,
and the variant counts plus the withheld pool sum exactly to the
parent's count — means no remainder can exist. A document that breaks it
is a loader refusal, not something this method repairs.

**Why the variants are written rather than the normalized identity
alone:** the producer folds case and trims spacing before publishing a
label, so a column holding `A`, `a`, `B`, `b` publishes two labels of
two rows each. A twin built from the normalized identities alone would
write `a, a, b, b` and repeat where the real column never did, breaking
the all-different obligation for every label role. Owner decision 9
directed that the variants be published so the twin can keep the values
distinct; this section is where that is spent.

### G8.1a Which held-back groups keep the label's written form

**Input: the level's `shape_form_cells`** (contract 7.4.8), how many of
the level's rows wrote the label in the label's own written form. Owner
ruling of 2026-08-31, plan amendment A-P4-47; before it the description
did not carry the fact and the walk guessed, missing in both directions
(residual R-P4-34).

**Step 1 — what the published spellings already cover.** Walk
`variants` and add up the counts of the keys whose spelling has a form
under contract 7.9. Those cells are written byte for byte by G8.1 step
1, so what they wear is read rather than reasoned about. Call the total
`covered`.

**Step 2 — the debt.** `debt = shape_form_cells - covered`. Where it is
nought or less, no held-back group keeps the form and this section is
finished.

**Step 3 — the plain walk.** Take the `variants_withheld` keys in
DESCENDING numeric order. For each key, take as many of its groups as
fit under what is still owed — `min(multiplicity, owed // key)` of them
— and subtract what they cover. Where nothing is left owed, those
groups are the answer.

**Step 4 — the reachability walk, where step 3 leaves a remainder.**
Taking the largest size that fits at each step misses arrangements that
exist: a debt of 6 against groups of 4, 3 and 3 takes the 4 and is left
with a 2 no group covers, while 3 and 3 settle it exactly. So walk
every total from 0 up to the debt and record, for each, the FIRST size
that reaches it, offering the sizes in the same descending order and
never using a size along one chain more often than the entry holds
groups of it. Where the debt is reached, follow the record back from it
to nought and count the sizes taken; that is the answer.

**A SUB-MULTISET SUMMING TO THE DEBT ALWAYS EXISTS ON A DESCRIPTION THE
PRODUCER WROTE**, because the debt is a sum of those very sizes there,
by construction: the source's own form-bearing held-back spellings are
whole groups. So the closure is EXACT and not approximate.

**THE WALK IS BOUNDED**, because its cost is the product of the debt
and the number of different group sizes and neither is bounded by the
document. Where the product exceeds the bound, or where the debt is not
reachable at all, step 3's own partial answer stands and the twin's
report NAMES what it left unsettled — the same treatment every other
bounded search in this method gets.

**Each group of a size is then asked in walk order**, and the first
however-many groups of each size the answer names are the form-keeping
ones. Which group of one size is which does not matter and cannot: the
description publishes group SIZES and names no spelling, so two groups
of one size are indistinguishable in it.

### G8.2 Invented variant spellings

An invented variant must fold to its parent label, differ from every
spelling already used in the column, WEAR THE FORM G8.1a ALLOTTED IT
(G8.2a), and be produced by a rule that has an unbounded supply. In
this order:

1. **Case flips.** Let the parent's alphabetic positions be
   `q[0] .. q[L-1]`, left to right. For `k = 1, 2, 3, ...` write `k` in
   binary and flip the case of position `q[i]` for every set bit `i`,
   with bit 0 the LEFTMOST alphabetic position. Skip any candidate equal
   to a spelling already used in this column, raw or after folding
   against a DIFFERENT parent. This supplies `2**L - 1` spellings.
2. **Trailing spaces.** When the case flips are exhausted (a parent with
   no letters exhausts them immediately), append `m = 1, 2, 3, ...`
   space characters to the parent's spelling. Folding trims, so every
   one of these folds to the parent; the reader preserves them
   (`skipinitialspace=False`, and minimal quoting does not quote for a
   trailing space); and the supply has no end.

A spelling that is only spaces cannot arise, because a published label
is not empty — an empty cell is an absent value, not a label.

### G8.2a The form a made-up spelling must wear

**Each held-back group carries a TARGET FORM**: the label's own form
where G8.1a gives that group the form, and "no form" otherwise. A
candidate of G8.2 whose form is not the target is stepped past, exactly
as one already used in the column is.

**The two halves of the supply are the two answers, which is why one
rule settles it.** A case flip of the label wears the label's own form
— such a spelling holds no space, so trimming changes nothing, and
folding an ASCII letter leaves an ASCII letter in the same place. A
trailing space wears no form at all, since a space is not one of the
thirteen marks. So a form-keeping group takes a case flip (or the
label's own spelling, G8.1 step 2), and a form-losing group takes a
trailing space, or a case flip where the label itself has no form.

**Where the case flips run out with the form still wanted**, the
trailing space is written and the level falls short of its published
`shape_form_cells`. A label of one letter has one case flip, so a
description asking two of its held-back groups to keep the form is
asking for a spelling that does not exist. No producer writes such a
description — a source that spelled those groups had the spellings to
do it — and the loader cannot see it, because the count is inside W8's
two bounds. The twin's own report names the shortfall.

### G8.3 Withheld levels

`suppressed_levels` says how many levels were withheld and
`suppressed_rows` how many rows they covered together. No size of any
one of them is published (owner ruling of 2026-09-17, item 2, option A;
plan P4-D201), so the sizes are a fixed rule of those two, the floor,
and the DEBTS the published facts leave the held-back cells to pay.
With `cap` one less than the floor:

1. **The debts, in order.** For each numeric class in the order G8.3a
   settles them, what each census form reading as that class still
   owes, by the form's spelling and never past the class's own debt,
   then what the class owes beyond its forms; then what each census form
   reading as no number owes, by its spelling; then the cells left over.
   The first group are NUMBER debts and the rest WORD debts.
2. **The fewest labels.** Each debt takes its cells over `cap`, rounded
   up. Where the debts do not come to `suppressed_rows`, or need more
   labels than `suppressed_levels`, the pool is one word debt.
3. **The labels left over** go one at a time to the debt whose labels
   are then the largest on average, the earlier debt on a tie, in four
   rounds: a number debt while its average exceeds `(cap + 2) / 3`, the
   average of the sizes step 4 writes; then the debt of each census form
   reading as no number, up to one label per cell; then the cells left
   over, likewise; then any debt, one label per cell at most. A form's
   debt comes before the cells owing no form because a column holding
   more held-back labels than the form walk searches is settled by its
   one-pass rule, which overshoots a debt it cannot finish in single
   rows.
4. **The rows of each debt** are shared over its labels: one row each,
   the rest in proportion to the square of each label's place counted
   from one, whole rows going to the largest remainders (the later place
   on a tie), and a label past `cap` passing what it holds past it to
   the label before it, from the last one down.

So every invented label stays below the floor -- contract invariant B4
refuses a pool too large for that -- every debt is paid by a set of the
sizes that exists, and the sizes rise, in the order this section reads
them. Five labels on twenty-one rows at a floor of eleven, all owed to
one form, are `1, 2, 4, 6, 8`; frozen case `pooled_level_sizes` pins it.
One invented label is produced for each size and used exactly that many
times.

**WHICH SIZE TAKES WHICH FORM IS SETTLED BEFORE ANY LABEL IS BUILT,
and it is not the list's own order** (contract 7.9.1, review round 3
finding 9). Where the column publishes a census, the sizes are
considered LARGEST FIRST and each published form's outstanding debt is
settled by an exact subset of them, read off the reachable sums rather
than hunted for; a size no debt needs is left NEUTRAL. Where no
arrangement settles every debt exactly, the largest debt is taken
first and the report names what went unmet.

Ascending order and neediest-form-first were what this said, and they
do not reach an arrangement the source itself exhibits: twelve levels
whose debts of 31 and 74 are met exactly by `14+17` and
`6+13+13+14+14+14` are reached by no one-pass rule over the ascending
list. The published counts are exact facts and the order of a list is
not, so the order yields.

**Where the column's census NAMES NO FORM** the invented
labels are `group-1`, `group-2`, `group-3`, … in order. Each candidate
is skipped and the number advanced when it collides, raw or folded,
with any spelling already used in the column. They are neutral by
construction: they carry no fragment of any real value, they are not
one of the spellings that mean "no value", they do not read as a number
or a date, they contain no comma or quote so they need no quoting, and
they do not begin with a character that a spreadsheet reads as a
formula.

**Where it DOES — which is any of the four label roles, since all four
carry the census (contract 6.11, C6-31b) — the invented label is
written in one of the published forms**
(contract C6-D18, plan P4-D18). `group-14` is not a code: it is the
wrong length, it is lower-case where the codes are not, and on a
hyphenated scheme it carries a hyphen of its own, so it passes a "looks
segmented" check, crashes a split into a fixed number of parts, and,
the word being exactly five characters, makes a width check on the
leading segment answer plausibly and wrongly.

- **The debt is over CELLS ALREADY WRITTEN.** The census counts every
  present cell of the column, and the published spellings and the
  invented variants of G8.1 and G8.2 are already on the page wearing
  their forms. What the invented labels owe is the published count
  minus what those cells paid, counted over the twin's own cells. A
  walk taking its debt from the census alone writes every form twice
  over and misses every count it was built to meet.
- **Each invented label covers its level's size**, which the rule
  above reads off the pooled total, so the walk chooses only WHERE to
  pay: the form owing the most cells, ties broken by the form's own
  spelling ascending.
- **The form is filled from a counter**, never from a reading. Every
  `%` takes a figure and every `@` a letter, the step taken apart into
  those positions by mixed-radix arithmetic after being multiplied by a
  stride sharing no factor with the form's own supply — so consecutive
  labels differ in every fillable position, and no two steps below that
  supply collide. Every other character of the form stands as itself.
- **The four neutrality properties are ASKED rather than had.** A
  spelling built to look like a code no longer has them by
  construction, so each candidate is tested against all four and
  stepped past where it fails, exactly as a collision is.
- **"Does not read as a number" is the property of a stand-in owing
  ORDINARY TEXT, and only of one** (landing 2b.4). A held-back level the
  class debt of G8.3a gives a numeric class must read as that class, so
  for it the number property turns round and G8.3a states the rest.
- **And it is NO NUMERIC CLASS AT ALL, not merely no finite number**
  (landing 2b.8, plan P4-D72). The property was asked as "does this read
  as a NUMBER", which is one of the four classes of G10.2, so the other
  two walked through it: a spelling of the census form `%%@%%%` that is
  a well-formed number too large for binary64, `47E807`, was accepted
  for a level owing ordinary text, and a sign inside accounting
  parentheses, `(-1)`, was accepted the same way. A column of
  `12e400`-style values beside four text levels came back with
  twenty-seven out-of-range cells against a published twenty-five and
  eighteen text against twenty, three checks missed and the table
  passing its own description. The class partition is the whole point of
  G10.2, so the question asked of a text stand-in is the partition's
  own: it must read as ordinary text under the column's grammar AND
  under the other one, exactly as the number property is already asked
  twice.

**THE LOWER-CASE KEY** (contract C6-31a, plan P4-D121). A census key
carrying `&` names the cells of one form whose every letter was lower
case, and a stand-in written in it fills each `&` from the lower-case
alphabet at the position and by the arithmetic a `@` is filled: the
step taken apart leftmost first, twenty-six to a letter place. Every
cell already written settles the census under the key the census counts
it under — its lower-case key where every letter of it is lower case
and the census names that key, and the form as `@` writes it
otherwise — which is the recount's own reading, so a debt is never
paid by a cell the validator files elsewhere. The probe of G8.3a that
asks whether a form's spellings read as numbers fills `&` with `e` as it
fills `@` with `E`, so `1.1e6` written in lower case keeps its number
reading under the key `%.%&%`.

### G8.3b The shape a stand-in the census owes no form takes

**THE RULE THE NEUTRAL SPELLING GAVE WAY TO** (plan P4-D122, landing
2b.18 part 2, the carried item of landing 2b.12). A stand-in the census
owes no form was `group-N`, and on a long tail that is most of them: a
code column of 2,000 rows at a floor of twenty, `4-F` beside `12-AB` and
longer, published three forms and none for its commonest shape `%-@`,
whose few spellings the small-supply rule of contract C6-31 withholds,
and its twin's mean cell length was 9.907 against the real 7.204, with
both files passing.

1. **The shape.** The spellings a label column publishes — each level's
   variants, or its label where it lists none — are tallied by the shape
   each wears and the rows that wrote it: the written form, with `&` in
   every letter place where every letter of the spelling is lower case.
   A shape reading as a number (G8.3a's reading) is passed over, and so
   is a shape the census names in either case. The shape covering the
   most rows is taken, ties to its own spelling ascending; none left
   means no shape, and every stand-in owed no form is `group-N` as
   before.
2. **Its supply**, counted as G8.3 counts any form's.
3. **The places it covers.** The places owed no form are ranked largest
   first and then by place, and the first `supply` of them are covered;
   the rows of the rest are the rows missed.
4. **The trade.** While any row is missed, each place paying a named
   form is offered once, largest first and then by place: for an offer
   of `k` rows, two or more, places owed no form are taken from the END
   of that ranking — smallest first — each smaller than `k` and no
   larger than what is still to be matched, until they sum to `k` with
   two or more of them. The trade stands where they do, where the named
   form has spellings for the extra places, and where the rows missed
   then FALL; the named form is paid exactly the rows it was paid
   before. Each offer costs twice the number of places against a budget
   of `2^22`, and the offers stop when it is spent.
5. **The walk.** Each covered place takes the shape's next spelling
   under the same cursor, collision skips and neutrality tests a named
   form's walk uses; a place past the supply, or one whose shape is
   spent, takes `group-N`.

**WHY THE LARGEST PLACES.** The published labels are the column's
commonest values, so the held-back values most like them are the most
repeated ones, and a shape of 260 spellings covers a thousand rows only
if it is spent on the groups that write many rows each. Measured on the
carried column at two source seeds: the length mix of the twin equals
the real column's exactly, `{3: 988, 5: 306, 9: 350, 19: 356}`, mean and
spread identical to three decimals. Without the trade the shape's 257
spellings covered 257 of the 919 rows owed no form, all of them single
rows, and the other 662 were `group-N`.

### G8.3a The classes the held-back levels owe

**A held-back level that was a number is written as a number** (landing
2b.4). The published spellings of G8.1 and G8.2 are on the page first,
and each reads as one of the four classes of G10.2; what is left of
`n_numeric`, `n_out_of_range` and `n_contradictory` after them is OWED
by the held-back levels, counted over the twin's own cells exactly as
G8.3's form debt is. Before this section every held-back level was
written as a word, which broke G10.2 on the column a real table most
often has: a column of readings beside two labels, 1,200 rows at a
floor of twenty, published 853 numbers and its twin held 359, so code
converting that column's non-label cells to numbers crashed on the twin
and the twin failed its own validation. A column is read with its own
grammar throughout: on a column declared `--decimal-comma` a cell is a
number when it is one under that reading.

1. **Which levels pay which class, BEFORE any form.** The class decides
   how every cell parses, so it is settled first. The sizes are taken
   largest first and each class debt is settled by an exact subset of
   them, read off the reachable sums, the larger debt first and then the
   smaller first, exactly as G8.3 settles a form debt. Where neither
   order settles every class debt, or the sizes times the largest debt
   pass 2^24, one pass gives each size, largest first, to the class
   owing the most that the size does not overpay and that can still
   supply a spelling. A number's supply is how many numbers step 3 can
   still give.

   **AN ARRANGEMENT THAT STRANDS A FORM DEBT IS NOT TAKEN** (landing
   2b.13, Codex item 5 of landing 2b.4). The split settles CELLS and
   step 2 settles the forms INSIDE it, so an arrangement paying every
   class exactly can still make a form debt impossible. Readings `5.1`
   and `5.3` on eleven rows each beside `ab-cd` on twenty, with `5.2`
   on four rows, `8` on one and two words held back: five cells must be
   numbers and four of them must wear `%.%`, and the held-back sizes 4,
   1, 3 and 2 were split 3+2 — which makes five exactly and four not at
   all — so the twin wrote TWENTY-SEVEN cells of `%.%` against a
   published twenty-six and `synthtwin validate` exited 3 while the
   table passed. The source's own 4+1 meets both.

   So an exact arrangement is accepted only where, inside each class,
   the forms reading as that class can themselves be settled exactly
   over that class's sizes by the same reachable-sums arithmetic, both
   debt orders, each form's supply taken as the number of sizes. Where
   they cannot, another exact arrangement is tried — each pass
   forbidding one more of the places the refused arrangement spent, so
   the passes reach genuinely different subsets — up to eight passes,
   and the FIRST exact arrangement stands where none of them can. A
   form owing more cells than the whole class covers is unpayable under
   every split and is not asked, so an arrangement is never refused for
   failing to do the impossible. The supply is COUNTED rather than
   walked because this asks only whether the arithmetic exists; the
   walk of step 3 still reports whatever the supply then refuses, so
   preferring an arithmetically possible arrangement can never be worse
   than taking the first one blind.
2. **Which form each paying level wears.** The census forms whose
   spellings read as a class are settled over that class's levels
   ALONE, by G8.3's arrangement, with each form's supply counted by the
   walk of step 3 for numbers and by G8.3's own walk for the other two
   classes.

   **WHICH CLASS A FORM READS AS is its first filling (`_filled_form`
   at step zero) — and, where that reads as no numeric class, its
   EXPONENT filling as well** (landing 2b.13, Codex item 7 of landing
   2b.4). `_filled_form` puts `A` in the first letter place, so
   `%.%@%`, the form of `1.1e6`, fills to `0.0A0` and read as TEXT: the
   form went to the word debt and never to the number debt, and the
   four held-back cells of a column publishing `1.1e6` and `1.2e6` on
   twenty-two rows were written `1`, with the census naming `%.%@%`
   twenty-six times, the twin wearing it twenty-two, and `synthtwin
   validate` exiting 3 while the table passed. The exponent filling
   puts `0` in every figure place and `E` in every letter place; where
   it reads as a NUMBER the form reads as a number. Only NUMBER is
   answered this way — the other two classes are constructed outright
   by G10.3 — and a form whose letter places would have to DIFFER is
   answered exactly as before, which is the stated limit of the rule.

   **A NUMBER FORM HAS TWO SUPPLIES, and the walk takes the second
   where the first is empty** (same landing). Step 3 spells a PLAIN
   decimal, whose form is `%.%` and never `%.%@%`, so a form the ladder
   cannot spell has ladder supply nought and would be settled over no
   level at all. Its supply is therefore the LARGER of the ladder's and
   its own filling's, and a level owing such a form that step 3 cannot
   spell takes the form's own walk instead, which wears the form and
   reads as a number, so it meets the census and the class count
   together. The number's LOCATION is still nothing the
   description places, and the report says so in those words.

   **AND THAT WALK IS HELD TO THE PUBLISHED NUMBERS' OWN ENDS**
   (landing 2b.13 repair, plan P4-D92). Step 3's ladder is BUILT from
   the published numbers and steps from them, so what it writes sits in
   or beside the span the column is known to hold. The form's own walk
   is no ladder: it fills the form's figure places by plain counting
   and lands wherever the counting lands. Unbounded it wrote `9.6E6`
   for every held-back cell of a column holding `1.1e6` to `1.3e6`, at
   seven generate seeds — the census met exactly, twenty-six of
   twenty-six, while the twin's numbers took mean 2,450,000 and
   greatest 9,600,000 against the table's 1,173,077 and 1,300,000, a
   spread 42.9 times the table's, and `synthtwin validate` fell from 3
   to 0. That column publishes no ladder, least or greatest of its own,
   so NO obligation could ever catch it.

   So a spelling of the form's own walk is refused where its VALUE lies
   outside the ends, and the supply is counted under the same bound it
   is spent under — counted loosely, the form is settled over a level
   the walk then cannot cover, and the shortfall is reported as a
   missing spelling rather than as the bound really refusing it.

   **THE ENDS ARE THE PUBLISHED VALUES, NOT THE LADDER'S RUNGS**
   (landing 2b.15, plan P4-D100). The ends are the smallest and the
   largest VALUE the column published, read by the same grammar the
   column is read with, whether or not step 3 can step from the
   spelling that carries it. Asking the LADDER for them — which is
   built from plain decimals alone — left a column whose every
   published number wears an exponent, a grouping mark or a leading
   plus with no ends at all, so every spelling of its form was refused
   and four cells of a census of twenty-six went unpaid, at twin
   validate 3 against the table's 0 and at seven generate seeds, on all
   three of those spellings alike. Such a column DOES publish numbers —
   1,100,000 to 1,300,000, stated in its own description — and what it
   lacks is a rung to step FROM, which settles the walk of step 3 and
   says nothing about how large a made-up number may be. Nothing here
   places that number: the ladder still cannot step, and the report
   still tells the reader the location is invented and that a statistic
   computed over it means nothing about the table. The bound only holds
   it inside the magnitudes the column is known to hold. Where the
   column published NO number at all there are no ends of any kind, so
   every spelling is refused, the debt stands, and the report line and
   the exit code announcing it stand with it.

   A shortfall a reader can see is not exchanged for a larger one
   nothing can check WHERE THIS VERSION CAN TELL THE TWO APART, which
   is where the CANDIDATE leaves the published ends. It cannot tell
   them apart where the HELD-BACK LEVEL lies outside those ends
   (landing 2b.15 repair, plan P4-D101). Nothing below the floor
   reaches this walk, so a level smaller or larger than every number
   the column published is indistinguishable here from one inside the
   span, and the stand-in is written from inside the span either way.
   Measured at three generate seeds on a column publishing 5,000,000
   and 8,800,000 with 1,100,000 held back on four rows: the census is
   met twenty-six of twenty-six and validate exits 0 where the unpaid
   twin exited 3, and the twin's mean moves from 2.8 per cent low to
   17.9 per cent high while its spread moves from 11.6 per cent high to
   34.0 per cent low. That cost is NAMED here rather than claimed away;
   it is not paid by choosing a different spelling, which was measured
   and refused; and the report says over those cells that where between
   the published ends they fall is this version's own choice. Only
   NUMBER is bounded this way; the
   other two classes are constructed outright by G10.3 and mean
   magnitudes no envelope covers. The rule above is not withdrawn by
   this — a column publishing the same census beside PLAIN spellings
   has ends, and its form debt is met in full from inside them.

   A level given no form
   wears none the census names, because a spelling of a named form counts
   toward that form and a level settled without it would overpay it. A form
   whose spellings read as a numeric class is then taken out of the
   word debt: it is paid inside its class or not at all.

   **The levels given no form have a supply too** (landing 2b.4,
   repair). Where the number levels left without a form outnumber the
   numbers step 3 can give a level wearing no named form, the forms are
   settled again by the same arrangement with those numbers as a debt of
   their own -- every cell of the number class the forms do not owe --
   beside the forms, with that supply. The second answer is taken only
   where it settles every form exactly and leaves no more levels without a
   form than the supply; otherwise the first stands. One-decimal
   readings from 3.5 to 10.2 whose census names `%%.%` have thirty-nine
   such numbers, and the largest-first settlement of `%%.%` left
   forty-one levels to them.
3. **What a number is.** The walk starts from the PUBLISHED numbers: the
   published spellings reading as numbers that are plain decimals -- an
   optional minus, figures, and at most one point followed by figures.
   **EVERY PUBLISHED NUMBER ANCHORS IT, not only the plain ones** (plan
   P4-D268; stated here in full by the oracle's independence repair of
   2026-09-19, the passage below on spellings this walk cannot step from
   being the rule that P4-D268 replaced). Each published number is taken
   as a whole count of UNITS of its last place and the count of PLACES
   after its point, and is read in the first of three ways that reaches
   it. (a) Its spelling, trimmed of surrounding white space, read as a
   plain decimal: the figures with the point taken out are the units,
   negative where a minus leads, and the figures after the point are the
   places. (b) Its spelling rewritten and then read as (a): a spelling
   wrapped whole in round brackets is negative and is read inside them;
   then a leading plus is dropped, or else a leading minus is dropped and
   makes it negative, or else, where neither leads, a trailing minus is
   dropped and makes it negative -- one of the three at most, and a
   leading sign with a trailing minus reaches nothing; every mark contract
   GS1 lets stand between thousands (a comma, a space, an apostrophe,
   U+2019, U+00A0, U+202F, U+2009) is taken out wherever it stands; and
   what is left, with a minus in front where it is negative, must be a
   plain decimal. (c) Its VALUE, for a spelling no rewriting reaches, an
   exponent above all: a whole value below two to the fifty-third in
   magnitude is its own units at no places; any other value is read as
   (a) reads the shortest decimal spelling that parses back to the same
   binary64, written the way that spelling is conventionally printed --
   positionally from 10^-4 up to below 10^16, with a single nought after
   the point where the value is whole, and with an exponent outside that
   range, which is READ THROUGH THAT EXPONENT (item 3 of the numbers
   pass of the second Codex round, 2026-09-19): the part before the
   exponent mark is read as (a), and the exponent moves the count of
   places it was read at -- down by the exponent where it is
   positive, up by its size where it is negative, and where that
   leaves fewer than no places the units carry the difference
   instead. Before this a column published at 1.1e-7 had NO ANCHOR,
   its walk counted from nought, and its made-up cells came back
   near a thousandth: four orders of magnitude above every number
   the column is known to hold. A value that is not finite
   gives no anchor. That window is the way Python's own `repr` prints
   a binary64, which the generator's own reading calls: it was COMPLETED
   FROM THE SHIPPED CODE'S BEHAVIOUR at the independence repair, since
   P4-D268 named no window, and the skeptic of that repair recorded it
   so. **No frozen case tells the three readings apart** (measured by
   that skeptic: each of six mutants changing one reading alone left
   every vectors file unchanged, and removing (b)'s leading plus
   together with (c) moved cells), because the held-back anchors frozen cases publish are
   whole spellings with a leading plus, which (c) reads as (b) does. They
   are witnessed one call at a time in
   `tests/test_oracle_rule_witnesses.py`: eighteen spellings with the
   answers worked out from this step, asked of the oracle and of the
   generator, and eight registered mutants -- the leading plus, the
   leading minus, the brackets, the trailing minus and the marks each
   left unread, the value not read, a whole value read at one place, and
   the value's own minus not written -- each of which turns that
   witness red. TWO OF THOSE EIGHT WERE ADDED BY THE ROUND-2 LEDGER PASS
   (item 6), and with them two negative spellings: the NEGATIVE clauses
   of (b) and (c) had a case that touched them and no case that parted
   their two roads. Measured on that pass, each mutant rebuilding all
   nine vectors files byte for byte: with (b)'s leading-minus frame
   removed `-0.05` still answers `(-5, 2)`, falling through to (c) whose
   shortest spelling writes the same two places, while `-12.50` drops
   from `(-1250, 2)` to `(-125, 1)`; and with the minus taken out of the
   characters (c) lets a shortest spelling hold, every positive spelling
   is unmoved while `-1.5e-3` drops from `(-15, 4)` to no anchor at all.
   Both spellings are in that file's table now.
   Their finest count of figures after the point is `P`, and the
   smallest and the largest of them are the two ENDS. A level is
   written at `P` places, or, where it wears a form, at that form's own
   count of figures after its point, the ends rounded outward to it. A
   level wearing no named form may be written at EVERY count of places
   a published number was written with, the finest first, a coarser
   count taken up only once the walk at the finer one has ended (landing
   2b.4, repair): a column of amounts given publishing `0.5` and `1` whose
   census names `%.%` writes its other held-back amounts as whole numbers,
   which wear no form, and not as `10.0`.
   The walk has two parts, and the GAPS come first:
   - the values strictly between the two ends that no published number
     holds, nearest an end first, and the low end before the high end
     at each distance -- because a held-back reading is as often inside
     the published span as beyond it: at a floor of twenty that
     1,200-row column held nineteen of its sixty held-back numbers
     inside it;
   - then OUTWARD, one step below the smaller end, one above the
     larger, two below, and so on.

   The paying levels take their numbers LARGEST FIRST, ties by the
   list's order, each debt walking the ladder with a cursor of its own
   so a value one debt refuses is still there for another. A number is
   written with a minus where negative, its whole part as the figures
   it has -- no leading zero invented -- and exactly its places after
   the point, with the column's own decimal mark.

   **THE DRESSING, and an exponent form's own SCALE** (plan P4-D268;
   the scale added by item 3 of the numbers pass of the second Codex
   round, 2026-09-19). A step of the walk is written as a plain decimal,
   and a census form may be a plain decimal WITH A DECORATION -- a
   leading plus, a thousands mark, accounting brackets -- or an
   EXPONENT, which is a form carrying exactly one letter place. So the
   step is written into the form and the result verified: the form's
   figure places take figures in order, a letter place takes `e` for a
   lower-case key and `E` for a case-blind one, every other character of
   the form stands as itself, and the answer is kept only where it reads
   as a number, wears exactly that form under the published census and
   parses to the step's own value. A form with more figure places than
   the step has figures is filled from the left and then, where it
   carries a letter place, from the right; those two placements are
   tried in that order.

   An exponent form spells `mantissa` times ten to the `exponent`, and
   its two halves are read SEPARATELY. The mantissa is the figure places
   before the letter, split by the decimal mark into `lead` before it
   and `after` it; the exponent is the figure places following the
   letter, written as a size, negative where the form writes a minus
   after its letter and positive otherwise. A THIRD fitting is offered,
   after the two above: the exponent that leaves the mantissa exactly
   `lead + after` figures, and the one either side of it, each giving
   the mantissa the step's own value divided by that power of ten --
   exactly, or not at all -- and each still held to the verification.
   Those exponent fittings are offered ONLY on the walk below, and never
   on the ladder's plain places, so no column the dressing already
   answered moves.

   And the ladder is walked a second time for such a form, at `after`
   less that exponent -- which may be fewer than no places at all and
   then means units larger than one. That walk is the LAST of three and
   is taken only where the other two have both come back empty: the
   ladder at the form's plain places, then the form's OWN filling of
   step 2, which is held to the published ends, and then this. Measured
   on landing 2b.15's own columns, a column publishing both notations
   still writes `5.0e6` and an unanchored one still writes `5.0e6`,
   because the form's own filling answers them first; what moves is the
   column whose published span holds no spelling of its form at all,
   whose four held-back cells were written `1100001` and are now written
   `1.0e6` -- one ladder step below the published minimum, exactly as
   P4-D268's own frozen case writes `+14` one step below a published
   `+15` -- and whose spread now reproduces the table's exactly, 72,430.3
   against 72,430.3 where the unpaid twin gave 50,383. What P4-D92 and
   P4-D100 bound is the form's OWN walk of step 2, which is not a ladder
   at all; the ladder has always stepped outside the published ends.
   MEASURED at a floor of
   eleven, seed 4, on a hundred `alpha` beside twenty `1.10e+7`, ten
   `1.11e+7` and ten `1.12e+7`: the census requires `%.%%&+%` on forty
   cells and the source passes all 45 executable checks, while the twin
   wore the form TWENTY times and spelled the other twenty `10999999`
   and `11000001` -- a walk in hundredths where the form spells hundreds
   of thousands, and a dressing with no room for eight figures in four
   figure places. The same column at `1.10e-7` failed the same way.

   A PUBLISHED MAGNITUDE OF NOUGHT IS AN EXPONENT OF NOUGHT (the
   skeptic's finding 3 on that item, the repair pass of 2026-09-19).
   Nought has no magnitude to read an exponent off, and reading its one
   written figure as a figure before the mark would give the scaled walk
   a place the ladder's own places contradict. But a column that
   publishes nought alone publishes it AS its form spells it, and the
   mantissa's own lead figures spell nought at an exponent of nought, so
   the scaled place is the mantissa's `after`. MEASURED at a floor of
   eleven, seeds 4 and 13 alike, on a hundred `alpha` beside twenty
   `0.00e+0` and two held-back levels of ten: before this the rule stood
   aside and answered the plain places, which sends the walk back at its
   first line, and the twin wore the form TWENTY times and wrote the
   other twenty as the bare figures `1` and `2`, missing the form count
   at exit 3 against the table's 0. After it the twin writes `0.01e+0`
   and `0.02e+0`, forty of forty wearing the form, both files at exit 0.
   The same column with `1.10e+0` published instead -- a magnitude that
   is not nought -- is byte-identical either way.

   **The sign rule.** A negative needs a published negative. A positive
   needs a published positive, or a published zero and no published
   negative, which is a column of counts whose only published number is
   zero. Zero needs a published zero, or published numbers on both
   sides of it. A value breaking the rule is stepped past; once both
   outward sides break it the walk has ended.

   **The refusals.** A candidate is stepped past where it is already
   written in the column, raw or folded; where its value is `-9999`,
   `-999` or `9999`, the three the profiler can read as a missing-value
   sentinel; where it is a spelling this column or the vocabulary reads
   as absent; where it reads as a date; where it carries a quote, or a
   comma on a column not read with one; and where it opens with `=`,
   `+` or `@`. A minus is how a negative is written, not a formula.

   **What the census could hold** (landing 2b.4, repair). A level
   wearing no named form must still wear a form the census could have
   held. The census counts a form only where the form has room for at
   least the column's `n_distinct` plus its smallest group size
   (contract 7.9); a counted form it does not name was pooled under the
   withheld key. So a candidate's form is stepped past where it is
   NAMED; is written where it is too small to be counted, or where the
   candidate has no form at all -- a whole number has none; and, where
   it is COUNTED BUT NOT NAMED, is written only where the census pooled
   at least one cell. The pool is not spent cell by cell: spent that way
   it ended the walk of a column of negative integers pooling ten cells
   after ten of them, and `n_numeric`, which the quality report checks,
   was missed to keep a pooled count, which it does not. Every step
   further out on a side, a larger positive or a smaller negative, is
   wider and its form counted too, so where such a form is refused that
   side of the walk has ENDED; a side of a form's own walk likewise ends
   once its steps are wider than the form. The gaps are never ended
   this way. Without this rule one-decimal readings from 3.5 to 10.2,
   whose census names `%%.%` and pools nothing, stepped past every
   `%%.%` value and wrote `100.0`, and the twin's standard deviation of
   its numbers was up to four times the table's with every check
   passing; with it, readings whose census names `%.%` and pools
   eighteen cells still write `10.0`.

   **The narrow walk comes first** (integration repair of landing 2b.4).
   The pool proves only that some cell below the floor wore a counted
   form, and a pooled WORD proves nothing about numbers. So steps 2 and
   3 are first taken with every counted form the census does not name
   refused -- pool or no pool -- wherever the candidate has more figures
   before its mark than the widest of the smallest published number, the
   largest, and every plain decimal form the census names. That answer
   stands wherever every level paying a class debt found a spelling;
   only where one did not are steps 2 and 3 taken again under the pool
   rule above. Without it one pooled `ab-cd` beside one-decimal readings
   from 0.8 to 13.4 at a floor of eleven let the walk write `100.0` to
   `100.3`, and the twin's numbers had a standard deviation of 4.91
   against the table's 2.01 with every check passing; the narrow walk
   writes the twin the same column has without that cell, 2.02. Where
   the table did hold the wider numbers -- readings under ten whose
   census pools the few `%%.%` above them, and `label_numbers` below --
   the narrow walk runs short and the pool rule writes them as before.

   **A whole-number tier where the published places cannot pay**
   (landing 2b.8, plan P4-D70). The tiers above are the counts of places
   a PUBLISHED number was written with. Where every published number
   carried a decimal AND the census NAMES the form those places write,
   every candidate of the only tier there is is stepped past for wearing
   a named form, so the tier is empty and a class debt goes unpaid:
   readings published `5.1` and `5.3`, whose census names `%.%` and
   pools nothing, beside a held-back `7`, wrote two cells the table
   holds as numbers as words instead -- twenty-five numeric against a
   published twenty-seven, two checks missed, and the table passing its
   own description. So where the finished walk has left the number debt
   unpaid, steps 2 and 3 are taken AGAIN with a last tier of no places
   at all, and that answer is kept only where it covers more of the debt
   than the published places did. A whole number wears no form (a cell
   of figures alone carries one kind and has no form at all), so it can
   never overpay the census; and because the tier is last and a tier is
   taken up only once the one before it has ended, a column whose own
   places still pay never reaches it. That is what keeps a column of
   `d.d` readings writing `d.d` -- an integer there passes the census
   and breaks a check written against the table's own spelling, which is
   the first goal -- and it is why the tier is asked for by the DEBT and
   not by the supply: a supply counted before the walk says how many
   numbers exist, not how many this column may wear.

   A level whose form has no number left keeps its class without the
   form. A level that finds no number at all is written as G8.3's
   neutral label, and the report names the shortfall with the reason
   that the supply ran out -- not the reason that a count fell part-way
   inside a group, which is the other one and which is given only
   where no exact split was found. **Where the column published no
   number at all**, nothing places them: the walk starts at zero, holds
   only positive numbers, takes its places from the number-reading
   forms the census still owes, and so counts upward from the smallest
   step those forms write; a level wearing no named form takes those
   places first and whole numbers after them; the report says that
   nothing published places them.

   **And where it published a number this walk cannot step from**
   (landing 2b.8, plan P4-D71). The ladder is built from the PLAIN
   decimals among the published spellings, so a column publishing
   `1.1e6` and `1.2e6`, or a grouped `12,345`, or a leading-plus `+5`,
   has an unanchored ladder although it published numbers. The report
   said of such a column that it "published no number at all", which is
   false on its face: the reader checks the description, finds the
   numbers, and stops believing the report. The two cases are told apart
   and the second says what is true -- every number this column
   published is written in a way this version cannot step from -- with
   the location invented either way. **WHAT THE REPORT SAYS OF THOSE
   NUMBERS MOVED WITH THE RULE** (landing 2b.15 repair, plan P4-D101).
   Step 2's bound now holds them between the smallest and the largest
   number the column published, so the sentence saying they count
   upward from the smallest step this column's forms write is true only
   where that span spells none of them; it states both cases, and it
   carries the clause the placed sentence carries -- a made-up number
   can equal one the table held back and is worked out from the
   published numbers alone. Placing those numbers is not done
   here: building the anchors from the exponent, grouped and
   leading-plus spellings was measured at landing 2b.4's integration and
   withdrawn, because the leading-plus column then lost `n_numeric` and
   `n_not_numeric` to a counted-but-unnamed empty pool, and trading a
   class count for a location is the wrong direction under the first
   goal. What this section now forbids is the false sentence, not the
   invented location.
4. **Out of range and contradictory** levels take G10.3's
   constructions, `ke999` and `(-k)` with `k` advancing on every
   refusal, or their form's own spellings, held to the same refusals.

**What a made-up number carries.** It is worked out from the published
numbers alone, EXCEPT WHERE G8.3c BELOW PLACES IT, which is wherever
the description publishes the pool's own scale. A gap value or an
outward step can equal a value the real column held back, and nothing
here prevents that; but no fact below the floor reaches it, and which
held-back level is written as a number is this method's own choice by
exact subset over the published sizes.

**The label half of a compound column owes no class.** The contract's
view of that half publishes `n_numeric` 0 and every cell a label, so
its debt is nought and none of its stand-ins is a number; a test holds
the view to that.

**What it was measured to hold** (landing 2b.4's repair; the first
writing of this paragraph was measured only on readings whose tail never
reached `10.0`, where the census names no wider form, and it overstated
what the rule holds). Two hundred and forty-two runs of a column of
labels -- one-decimal readings whose tail does and does not cross
`10.0`, at 60 to 5,000 rows and floors of eleven to fifty, potassium,
ages, answers, amounts given, coded amounts, negative and two-decimal readings,
years, room numbers, a column read with a decimal comma and negative
integers beside comments, over two to three seeds each -- met
`n_numeric` and `n_not_numeric`, kept the table's role when the twin
was described again, and validated with nothing missed for the twin and
the table, in every run. **Where the column published a number** (222
runs) the mean of the twin's numbers stayed within 0.42 of the table's
standard deviation of them in every run, and that standard deviation
within a fifth in 217. The five outside it are named: amounts given beside one
to five published numbers, whose rare `10` carries the table's spread
and whose twin keeps the held-back amounts nearest the published ones --
0.64 to 0.77 of the spread -- and coded amounts beside two published
numbers, 1.26. **Where the column published none** (20 runs) nothing
places the numbers, the report says so, and the location is invented:
at a floor of fifty a column of readings near seven came back with a
mean near 3.4 and whole numbers up to seventy-eight.

### G8.3c The pool's own scale

**WHERE THE COLUMN PUBLISHES A MEAN FOR ITS HELD-BACK NUMBERS, the
made-up numbers are placed on it** (contract section 6.3.3, invariant
B4d; plan P4-D302). The block gives two numbers over the pool: how many
of the held-back cells read as numbers, and their mean `mu`. This
section says what the twin writes from them.

**Why it exists.** Without it the walk of G8.3a has only the numbers
the column PUBLISHED to step outward from, and a column whose rare
values are its numbers publishes few of them or one. 100 `alpha`,
twenty `100` and ten each of 200 to 209 at a floor of eleven publishes
`100` alone; its twin wrote 95 to 105, so the numeric mean came back
100 against 187.083333 — and both files passed every check, because no
published fact spoke of the pool.

**What it does NOT get, and this is the whole shape of the section.**
The block used to carry the pool's POPULATION SPREAD as well, and the
owner's decision of 2026-09-21 withdrew it: a mean and a spread are two
equations and solve a tightly spaced pool outright. So HOW FAR APART
THE HELD-BACK NUMBERS STOOD IS A FACT THE TWIN DOES NOT HAVE. The
generator has to write something, so step 2 below chooses a spacing of
its own and the report says in words that the spread of this column's
made-up numbers is not a fact about the reader's table.

**What is placed.** Every group the class split of G8.3a step 1 gave to
the number class, in the order that step hands them out, which is
descending size. The form each group owes is settled first by G8.3a
step 2 and is not changed here: this section decides the VALUE and the
census decides how it is WRITTEN.

1. **The positions.** With `m` such groups, the `i`-th in that order
   stands at position `p_i`: nought, then one above, one below, two
   above, two below, and on outward. The largest group of a pool is
   therefore nearest the pool's own mean, which is where the most cells
   of the table sit.
2. **The centre and the spacing.** With the groups covering
   `c_1..c_m` rows and `N = c_1 + ... + c_m` between them, the weighted
   centre is `C = sum(c_i * p_i) / N`. Group `i` is asked for the value
   `mu + h * (p_i - C)`. That puts the mean of the cells written at
   `mu` for ANY spacing `h`, because the offsets cancel by
   construction — which is what lets `h` be this method's own choice.

   **`h` IS FIVE PLACES OF THE FINEST GRID THE LADDER WRITES AT, held
   inside the room the column's own published numbers leave, and then
   down to an ODD whole number of places.** Each of those three is
   measured.

   * **Five, and not one.** At one place the groups stand as closely as
     the grid allows, which is the arrangement a pool of consecutive
     whole numbers already has — so the twin's pool comes back AS the
     table's: measured on the shape ledger K-2B-50 names, all ten
     held-back values and every one of their hundred cells. Ledger
     K-2B-19 counts exactly that and is an accepted limit whose rule is
     that it may not get worse. At five, twenty of those hundred cells
     come back.
   * **Odd.** The offsets from the weighted centre are half-integers
     wherever the pool has an even number of equal groups, so an even
     multiple lands every value half a place off the grid and the
     rounding of step 3 pushes the written mean off `mu`: measured on
     that same shape, a pooled mean of 205.0 against a published 204.5
     at two places, against 204.5 exactly at one, three, five and seven.
   * **Held inside the room.** The room is the span of the numbers the
     column publishes, or how far `mu` stands outside that span,
     whichever is wider; `h` is the largest odd whole number of places
     that keeps the outermost group inside it, and one place where
     nothing fits. A column that publishes NO number bounds nothing and
     the five places stand. Without this, a pool of many levels five
     places apart reaches a long way — eighty groups on a column of
     integers around 120 spanned four hundred — and the twin's numeric
     spread came back 77.6 against the table's 20.4; held inside the
     room it comes back within 2.61 of it.

   `C` is the weighted centre whatever the sizes, and a single group
   stands at it and takes `mu` itself. Step 4 below moves the value
   each group is actually asked for, and the offsets of this step are
   what it moves them around.
3. **The spelling.** The value asked for is rounded to the nearest
   whole number of the tier's last place and written plainly there,
   then dressed in the group's form where it owes one, by the same
   dressing G8.3a step 3 uses — and a spelling that already WEARS that
   form is not dressed again. The TIERS are the ladder's own, the
   finest count of places first and the whole numbers last, exactly the
   tiers G8.3a step 3 walks for a number wearing no named form, and a
   tier is taken up only once the one before it has ended; a group that
   owes a form has the single tier that form writes at, because the
   dressing writes a plain spelling's figures into the form's figure
   places in order and a spelling written at another count of places is
   dressed into a different number. Where a rule refuses a spelling —
   it wears a form the census names while the group was asked for none,
   the census pooled nothing for a counted form it does not name, it is
   a spelling the column already uses, it fails the neutrality tests of
   G8.3a, it carries a sign no published number has, or it is too wide
   under the rule below — the offer steps one place outward, below then
   above, and on outward until one is accepted. One place is the
   smallest move there is, so a short walk keeps the group at the scale
   it was asked for; a LONG one does not, which is why step 4 exists.
4. **The offers, and which one is written.** Steps 1 to 3 ask each
   group for its own value and let the written mean fall where it may,
   and where a rule of step 3 refuses every spelling near a group's
   value the offer steps outward until one is accepted — HOWEVER FAR
   THAT IS. Measured on a column of 200 `alpha`, thirty `48.0` and five
   held-back one-decimal levels whose census names `%%.%`: the one
   group that owed no form was refused every two-figure one-place
   spelling there is, because each of them wears the form the census
   names, and the offer walked four hundred and twenty-eight places to
   `9.9`. Its pool came back at 45.14 against a published 53.72 — a
   sixth of the published mean out, on a twin that broke no other rule;
   over a hundred and fifty randomised pools the worst such twin stood
   A FIFTH of its published mean away. That is the defect this step
   closes, and it is what made G12.12's window impossible to draw from
   anything but a magnitude.

   **So the pool is offered several ways, on copies, and the offer
   whose own cells average closest to `mu` is the one written.**

   1. **The plain offer** of steps 1 to 3, at `mu` itself.
   2. **Up to three moved offers.** Each stands where the one before it
      would have had to stand for its own cells to average `mu` — a
      plain fixed-point step. A moved offer keeps the pool's
      arrangement exactly and only slides it, so it is asked for before
      the offer that does not. Three is measured: over 551 pools that
      publish a scale and whose twin publishes one back, no fourth
      offer came closer than the best of the first four.
   3. **The carried offer**, asked last because it rearranges the pool
      rather than sliding it. In it the groups CARRY EACH OTHER'S
      ARREARS: with `A` still owed — `mu * N` less what has been
      written — over `R` cells still to be written, the next group is
      asked for `A / R + h * (p_i - C_rest)`, where `C_rest` is the
      weighted centre of the positions still to be written. Those
      offsets cancel against `C_rest` exactly as the first ones cancel
      against `C`, so if every group were written where it was asked the
      pool would land on `mu` whatever order they were asked in. The
      group the census pushes FURTHEST goes first, because only the
      groups after it can carry it: every group is offered its step 2
      value once, writing nothing, and the distance between what it was
      offered and what was accepted is the order, the furthest first, a
      group nothing was accepted for before them all, ties in the
      walk's own order. A group nothing is accepted for does not lay
      its shortfall on the groups after it, because what the ordinary
      walk writes for it is not known here.

   **THIS STEP IS A REPAIR AND NOT A PREFERENCE.** It does not run at
   all where the plain offer already meets the window of G12.12, and it
   stops at the first offer that meets it. Moving a pool that was
   already inside the window buys nothing on the one obligation there
   is and MOVES THE TWIN'S NUMBERS: measured on 2,500 one-decimal
   readings at a floor of eleven, a moved offer took the pooled mean's
   error from 0.056 to 0.000 and the twin's whole numeric population
   spread from within a fifth of the table's to a quarter past it.

   **AND THE PLAIN OFFER IS AMONG THEM**, so a pool this step cannot
   improve is placed exactly where steps 1 to 3 place it: step 4 cannot
   make a twin worse. Ties go to the earliest offer.

   **BOTH KINDS OF OFFER EARN THEIR PLACE, measured.** With the carried
   offer withdrawn, four to five of about 115 randomised pools per draw
   came back outside the window — a dense one-decimal pool at 16 places
   out — because no slide of the whole pool helps when the column's
   unused spellings near the mean are spent. With the moved offers
   withdrawn, a dense pool of many levels ran the arrears away instead
   of closing them: 2,500 one-decimal readings at a floor of twenty,
   whose 43 held-back levels leave almost no unused tenth, asked its
   last group for 44.92 on a column whose numbers run from 5.1 to 9.3
   and came back at 4.17 against a published 6.79.

5. **Where nothing is accepted**, the group is left to the ordinary
   walk of G8.3a step 3, unchanged, and it is counted in no offer's own
   mean, because what that walk writes is not known here.

**WHAT THE REPORT SAYS, AND THE SENTENCE THIS SECTION CHANGES.** The
held-back note of a column whose made-up values are numbers used to end
by telling the person that an average or a spread over this column's
numbers is not a fact about their table, because the LOCATION of those
numbers was the version's own choice. Where this section placed EVERY
one of them the AVERAGE part of that sentence is false, and a report
that went on saying it would send a person away from the one number
this section exists to make reliable; so the note says instead that the
description publishes the held-back numbers' average as a group, that
the twin places them on it, and that what is still not a fact about the
table is HOW FAR APART they lie and which made-up number stands for
which label. Where the placement ran short of even one group the older
sentence is the true one and stands.

**The width rule, in the two cases this section distinguishes.** Two
different bounds are called a width here and only one of them is
evidence about magnitude.

**WHERE THE COLUMN PUBLISHED A NUMBER OF ITS OWN** — where the ladder
of G8.3a step 3 is anchored — those numbers' own width says what this
column's numbers look like, and no made-up number is a whole figure
wider, wherever the mean's own reach would fall outside it. A mean is
met as far as that width allows and no further. Measured: 1,200 ages at
a floor of twenty, whose held-back numbers are the tails, asked for
values past 99 and took the widest two-figure ones instead.

**WHERE IT PUBLISHED NONE**, the only width there is comes from the
form census, which says how the cells that WORE those forms were
written and nothing at all about the held-back ones. There the
published mean is the better evidence — it states the held-back
numbers' magnitude outright — so the value the mean asks for carries
its own width and the stepping is held to that.

**What this section does NOT publish.** It reads the two aggregates of
contract 6.3.3 and the column's own published numbers, and nothing
else. It does not learn which held-back level covered which rows, what
any one of them was worth, or how the pool's cells split between them,
and the values it writes are a construction over two numbers and a
spacing this method chose.

### G8.4 The order of `content`

Published levels first, in profile order, each level's variants in the
order of G8.1; then the withheld levels in the order of G8.3. The
placement arrangement of G4.2 is what makes the rows random; the content
order is fixed so that two implementations build the same list.

## G9. Invention: alphabets, the enumeration, fold collisions, capacity

This section fixes what P2-R5-F4 carried to this gate: the invention
domain and its capacity rule, with a named refusal.

### G9.1 The three alphabets

Each alphabet is an ordered tuple of characters. The ORDER is part of
the specification, because it decides which spellings are produced
first.

| name | characters | size |
|---|---|---|
| `DIGITS` | `0`–`9` in ASCII order | 10 |
| `CODE` | `-`, `0`–`9`, `A`–`Z`, `_`, `a`–`z` — ASCII code-point order | 64 |
| `WIDE` | every printable ASCII character, U+0020 through U+007E, in code-point order | 95 |

`CODE` is exactly the alphabet the shipped `parsing.is_code_text`
accepts, which is what makes `n_code_alphabet` reproducible. `DIGITS` is
a subset of `CODE`, which is why an all-digit value counts toward
`n_code_alphabet` as well, and the constructions below rely on that.

**Positional constraints, which apply to every spelling the ENUMERATION
of G9.2 produces:**

- the first and last character is never a space, so no enumerated value
  can be changed by trimming or read as blank;
- the first character is never `=`, `+`, `-` or `@`, so no invented
  value creates a spreadsheet formula hazard the report would have to
  count — **with one carve-out, bounded by the packing** (owner
  decision 9): a two-character value of the code alphabet that is not
  figures alone and reads back as a whole number has no other spelling,
  and a description publishing those counts proves the real column held
  one, so the twin reproduces the character rather than refusing to
  build. It is reached only where no assignment of whole groups meets
  every published count without it, and the report counts it and names
  its column (published labels are a different matter: they are written
  unchanged, counted and warned);
- a COMMA inside an invented value is permitted; the writer quotes the
  field and the reader reads it back unchanged, and a test asserts that
  round trip. **The stand-in rule refused one until plan P4-D243, which
  is this clause's own words contradicted by the code that was supposed
  to hold them**: a free-text column publishing
  `shape_forms {"@%%%,%%@": 2000}` was offered the form, refused every
  candidate wearing it, and wrote 2,000 wide-band cells matching none of
  them, with validate at exit 3 on the twin; the comma was the only mark
  of `parsing.SHAPE_MARKS` no twin could write. A QUOTE character is a
  different matter and the stand-in rule refuses one: it is the
  delimiter's own escape, a value holding one is written doubled, and
  that round trip has not been measured through the readers this package
  ships. The `group-N` labels carry neither by construction.

When a positional constraint rejects a character, the enumeration puts
the first character of the same alphabet that meets that constraint in
its place, in the alphabet's own order.

**THE LEADING NOUGHT OF A PUBLISHED LAYOUT, and why it is not a
constraint this list has to bend** (contract 7.12, landing 2b.18, plan
P4-D120). A record number written to a published layout may open with
the figure nought where that layout's leading mark says the source's
own cell did — the zero fill of a `%08d` record number. The
constraints above are about the space and the four characters a
spreadsheet reads as the start of a formula, and the nought is neither,
so nothing here is lowered: what changes is that G9.6's figures band no
longer forbids a leading nought where the census published one. A
layout whose own leading mark IS one of those four characters is given
up rather than written, since every one of its spellings would open
with it.

**The ONE construction outside the first constraint, and why it is
outside it** (P2-C2-F6). A fold-collision partner built by G9.3 may
carry a space at one or both ends. The first constraint exists so that
an enumerated value cannot be *changed* by trimming; a partner's whole
purpose is to come down onto a value already written once the ends are
trimmed, which is the same sentence with the sign turned over. The
constraint's other half is kept in full: a partner is built from a
parent that is not empty and holds no space at either end, so no partner
can be read as blank, and the character a spreadsheet would act on is
still never at the front. Every OTHER value of every column obeys the
constraint as written.

### G9.2 The enumeration, and why there is no search

The spellings of one alphabet `A` and one length `L` are enumerated as
plain base-`|A|` counting with `A[0]` as the zero digit and the leftmost
character most significant: index `k` in `0 .. |A|**L - 1` maps to the
string whose character at position `i` from the RIGHT is
`A[(k // |A|**i) mod |A|]`.

The **domain** of a column is enumerated by ascending length from
`min_length` to `max_length`, and within a length by ascending `k`.

The spellings a column needs are the first ones of that enumeration,
with the two extreme lengths pinned:

- the FIRST invented spelling of a column has length `min_length`;
- the SECOND has length `max_length` (when `max_length > min_length`);
- the rest follow the enumeration in order, skipping any spelling
  already used in this column.

The pins are what make `min_length` and `max_length` EXACT-OBSERVABLE.
They cost no word, exactly like the numeric endpoints.

**A BAND'S LEFTMOST CHARACTER IS A FAMILY OF ITS OWN, NOT A CONSTRAINT
APPLIED AFTERWARDS** (plan P4-D234). G9.1's substitution sentence above
governs G9.1's OWN constraints — the space at either end and the four
formula leaders — and nothing else. G9.5 step 4's band rule is not one
of them: it says which characters a cell of that band may LEAD with, and
that set, the family's **head**, is where the leftmost position counts.
So a word of one band at length `L` is enumerated as

```
index k  ->  head[k mod |head|]  followed by  the base-|A| spelling of
             k // |head| at length L - 1
```

with G9.1's own rules then applied to the result. The heads are fixed
here and nowhere else: the figures band has none (every one of its
characters keeps the cell in it); the code band's head is the LETTERS of
`CODE`, so no cell of it reads as a number; the wide band's head is the
characters of `WIDE` that are outside `CODE`, less the space and the
four formula leaders, so no cell of it counts as code-alphabet. This is
the family whose size G9.5's capacity paragraph already states —
`|head| * |A|**(L-1)` — and it is a BIJECTION on its own indices, where
substituting after the counting would put every index whose leading
character the band refuses onto one spelling: the code band's `A-` would
answer for eleven indices of sixty-four, and the wide band's `!!` for
sixty-eight of ninety-five. **Two implementations parted company here
and that is why it is written down**: the generator counted `A-`, `B-`,
`C-` and the reference oracle `A-`, `A0`, `A1`, agreeing only at length
one, where every index of the head is one spelling.

**The index-to-spelling map is a mixed-radix decomposition and holds no
search of any kind.** The `n`-th spelling is computed in a fixed number
of steps from `n`, so two implementations cannot diverge by searching in
different orders.

**The WALK over that map does step past spellings, and its bound is
stated here** (P2-C1-F2). Revision 1 said no rejection loop existed
anywhere in the invention path. That was not true of the implementation
and cannot be true of any implementation of this document. **Five rules
reject a candidate after it is computed**, and every one of them is
listed here because an implementer who plans for fewer plans a walk that
is too short:

1. the spelling is one this column has already written, or one this
   column already folds onto;
2. the spelling reads back as some other numeric class than the one its
   group has to answer for (G10.2);
3. the spelling means "no value" (G10.3's list) -- and on a column of
   free text or of record numbers, it is one ANY column of the document
   publishes as the spelling of its absent cells, because a
   `--missing-value` declaration reaches the whole table (plan P4-D158:
   a declared `FPQ7317879` in one column was written into a column of
   record numbers beside it, and the twin missed eight obligations with
   nothing named);
4. the spelling reads as a date under `parsing.DATE_FORMATS`;
5. only while a fold collision is being asked for (G9.3 step 1), the
   spelling holds no character with a case.

What is required, and is sufficient, is that the walk is BOUNDED:

- the walk over one family visits the indices `0, 1, 2, …` of that
  family in order and **stops at the family's own size** (G9.4), which
  is a number computed before the walk begins;
- a family that is spent returns "no more" rather than beginning again,
  so the walk cannot return to a spelling it has already written;
- the fold-collision ask of G9.3 is an ASK: a pass that insists on a
  letter-bearing candidate and finds none puts the walk back exactly
  where that pass began and takes it again without the ask, so the ask
  can never spend a family the ordinary rule could still have used. The
  pass gives up after **4,096** rule-5 rejections, and that number is
  NORMATIVE rather than an implementation's own choice: two programs
  giving up at different points would part company on the first family
  holding a letter-bearing spelling between their two ceilings, and the
  twin's bytes would stop being a function of the profile and the seed.
  Giving up MUST mean handing back "no more" so the rewind happens —
  carrying on inside the same pass would spend the very indices the
  rewind exists to protect (P2-C2-F8);
- the caller's response to "no more" is fixed by role in G9.4: a
  refusal for `free_text` and `numeric_unrepresentable`, and repetition
  under owner decision 6 for a declared identifier.

**The bound, stated truly** (P2-C2-F8). Revision 4 added a tighter
sentence: that the walk visits at most one more index than the number of
pieces of text the column has already written. **That sentence was
false, and a false normative bound is worse than a missing one, because
an implementer trusts it** — an implementation refusing at `used + 1`
rejects a family from which the walk does return a value. It is retired.
What is true:

- **Termination.** Let `room` be the family's capacity (G9.4) and `s`
  the index the family's cursor stands at when a value is asked for. The
  ordinary pass visits `s, s + 1, …` and stops at `room`; the cursor
  never moves backwards except for the one rewind the ask performs. So
  each index is visited at most once by the ordinary rule, at most
  `room` ordinary visits exist over a whole column, and a column asking
  `v` values of one family costs at most `room + A·v` index visits,
  where `A` is the ask ceiling. Every term is finite and computed before
  the walk begins.
- **Per value.** Producing one value visits at most `room − s` indices
  in the ordinary pass, plus at most `A` in the ask pass that may
  precede it, and **no bound smaller than that can be stated in terms of
  what the column has already written.** Rules 2 to 5 do not consult the
  column's history at all, so each can reject a run of consecutive
  indices with nothing yet written. Three witnesses in this document's
  own enumeration, each reachable with an empty history:

  | family | index | rejected because |
  |---|---:|---|
  | `out_of_range`, `CODE`, length 5, 1 word | 0 | `0e999` reads as an ordinary number, not an out-of-range one (rule 2) |
  | text, `WIDE`, length 1 | 11, 17 | `.` and `?` mean "no value" (rule 3) |
  | `number`, `DIGITS`, length 8 | 10101 – 10131 | `00010101` … `00010131` read as compact dates (rule 4) — thirty-one consecutive rejections |

  The first of those three settles the question on its own: one index is
  rejected and the second produces the first value of the column, so a
  walk that stopped after `0 + 1` indices would refuse a family that
  holds one.

### G9.3 Fold collisions when folded is below raw

When a column publishes `n_distinct_folded < n_distinct`, exactly
`n_distinct - n_distinct_folded` invented spellings must fold onto a
spelling already used. This obligation is binding and non-trivial: a
real 200-row single-character identifier profile publishes 200 raw and
122 folded, so 78 values must fold onto a partner.

**The fold this section has to reproduce is the SHIPPED fold, and the
shipped fold trims before it turns the case over** (P2-C2-F6). Revision
4 built partners by case flip alone, which is half of that operation, so
two whole classes of feasible collision could not be built at all: a
one-character parent holding a single letter offers exactly one case
variant, and a parent written in figures alone offers none. A column of
`a`, ` a`, `a ` and ` a `, which a producer describes as four raw
spellings, one folded identity and the length range 1 to 3, was written
as four folded identities and the miss was named. Naming it was honest
and wrong: owner decision 6 authorizes a lost distinctness count only
where width and capacity are jointly infeasible, and this column's own
source proves the pattern fits inside its own published length range. A
partner is therefore **a case flip, edge spacing, or both**.

The construction, in this order:

1. **Plan the budget first.** Let `X = n_distinct - n_distinct_folded`
   be the number of collision partners needed, and let `Y =
   n_distinct_folded` be the number of different folded identities. The
   first `X` folded identities are PREFERRED from the enumeration
   restricted to spellings holding at least one ASCII letter (in the
   `CODE` and `WIDE` alphabets this restriction removes only the
   all-digit and all-punctuation spellings; in `DIGITS` there are no
   letters at all). The preference exists because a case flip is the
   partner that leaves the length exactly where it was; it is a
   preference and not a condition, because step 2's second construction
   needs no letter. A pass that insists on a letter and finds none is
   put back where it began (G9.2), and the ordinary rule then takes the
   same spellings it would have taken anyway.
2. **Produce the partners.** The partners of one parent are one family,
   enumerated in this fixed order so that two implementations build the
   same ones:

   - the **edge spacing** is taken by ascending TOTAL number of spaces,
     starting at whatever total the parent needs to reach this partner's
     shortest permitted length and starting at none where the parent is
     already long enough; within one total the LEADING share ascends, so
     the spaces go to the end first, then are moved leftward one at a
     time. A total of `t` therefore supplies `t + 1` placements;
   - within one placement, the **case flips** of G8.2 are taken in
     ascending binary-counter order — for `k = 0, 1, 2, ...` flip the
     case of the alphabetic positions named by the set bits of `k`, bit
     0 the leftmost — with `k = 0` the parent's own case. A parent with
     `L` such positions supplies `2**L` of them;
   - the parent itself, which is no spacing and `k = 0`, is not one of
     its own partners and is stepped over.

   Case flips of the unspaced parent are therefore the first `2**L - 1`
   partners, in exactly the order revision 4 gave them, so a column whose
   collisions case alone could carry writes what it wrote before.

   **THE FAMILY IS THE PARENT'S FOLDED IDENTITY RESPELT, WHICH IS ITS
   TRIMMED TEXT** (residual R-P4-47). The three rules above are stated
   over the parent, and for every parent an invention role produced
   before this those are the same thing: a parent carrying no edge
   spacing of its own IS its own trimmed text, its own placement is the
   no-spacing one, and the walk starts and steps exactly where revision
   5 said it did. Where a parent DOES carry edge spacing the total is
   counted over the whole cell rather than added to what the parent
   already has, so a parent written `N ` inside a window pinned at
   `len(N) + 1` has ` N` as its next partner AT THAT SAME WIDTH, and
   not ` N ` one character past it. The placement stepped over is the
   parent's own — its own total, its own leading share, and `k = 0`.

   **AND A PARENT THAT WILL BE ASKED FOR PARTNERS AT A PINNED WIDTH IS
   WRITTEN WITH ROOM FOR THEM** (residual R-P4-47; section 9.7 of the
   profile contract says this in its own words about the partner, and
   this is the same sentence applied to the parent). Spacing only
   LENGTHENS, so a parent already filling a pinned width has no partner
   at that width at all: `N + " "` beside `" " + N` is ONE published
   width and one folded identity, and the walk kept the fold, fell back
   to the open window, and missed the ceiling by one character. The
   source column shows the answer its own cells took, which is that the
   PARENT carries a space too. So the parent of such a slot is written
   with that many fewer figures and that many spaces, and both cells
   land where the description says a cell of that column sits.

   **THE ROOM IS NOT FORECAST, IT IS MEASURED IN A FIRST PASS.** Which
   parent a slot takes is settled by step 4's preferences, so a rule
   that predicted the assignment would be a second implementation of
   it, free to disagree with the first. Instead the column is built
   once exactly as it was built before, the parents whose partners fell
   back to the open window are counted, and ONLY such a column is built
   again with that many spaces reserved in each of those parents. A
   column whose widths were already held has no fallback, so it is
   never built twice and none of its bytes move — which includes every
   column whose parent holds a letter, since a case flip keeps the
   length exactly where it was. Where the reserved room would take a
   parent below its own shape's floor the reservation is not made, the
   fallback stands, and the recount names the width as before.

   **WHICH MEMBER OF THAT ORDER A SLOT TAKES** (review item P2-C4-F4).
   The three rules above say what the family IS; this says which member
   of it a slot gets, and the twin's bytes are fixed only by the two
   together. A slot takes the **first** member of its parent's family —
   read in the order above, from that family's own start — that meets
   both of the following and is turned down for no other cause:

   - the column has not already written that exact spelling, raw text
     against raw text;
   - its length is one the slot's own window admits (step 3).

   **Every slot walks the family from that family's start.** The one
   place the start moves is the first rule above: a slot whose shortest
   permitted length is longer than the parent begins at the total that
   reaches it, since no smaller total can produce a member that slot
   could hold at all. A member some other slot's window turned down is
   NOT spent — a later slot with a wider window may still take it — and
   **the number of partners a parent has already supplied decides which
   parent comes next (step 4), never which member of a family is
   taken.** A slot that began at the second member of the family, or at
   the member whose position matches its own ordinal among the partners,
   would step over a member the column has not written and no window has
   turned down; this rule forbids that.

   Worked on the four-spelling column above, written in figures so that
   the case flips supply nothing at all. The parent is `1` and the
   published length range is 1 to 3, so the family is `1 `, ` 1`, `1  `,
   ` 1 `, `  1` — each backtick pair holds one digit and one or two
   single spaces. The slot pinned to the longest published length starts
   at the two spaces that length needs and takes `1  `. The next slot's
   window is the whole published range, so its walk starts where every
   walk starts, steps over the parent, and takes `1 ` — the member the
   pinned slot walked past. The slot after it takes ` 1`. The three
   partners of that column are therefore `1  `, `1 ` and ` 1`, in that
   order, and `tests/reference/generation-branch-vectors.json` freezes
   them.

   Revision 5 fixed the order and left this choice to be worked out from
   it. Two implementations worked it out differently on exactly that
   column: one wrote the three partners above, the other wrote `1  `,
   ` 1` and ` 1 ` and left `1 ` unwritten. Both columns satisfy every
   published fact of that description, which is what made the difference
   easy to walk past and is precisely why it is settled here — the
   frozen vectors exist to fix the bytes, and an order two careful
   readers can complete two ways fixes none. This paragraph adds a
   requirement to G9.3 and takes none away.
3. **The length a partner may take is the length its own slot may
   take.** Spacing lengthens a value, and both published length ends are
   EXACT-OBSERVABLE, so each slot carries a window:

   - the slot holding the SHORTEST published length, and the slot
     holding the LONGEST, may take only that one length;
   - every other slot may take any length in the published range;
   - a role publishing no longest length at all —
     `numeric_unrepresentable`, whose width is not published (R-P2-1) —
     puts no end on the spacing.

   Step 1 fills the first `Y` slots with the folded identities and the
   `X` slots after them with partners, so the first slot is never a
   partner — nothing has been written for it to fold onto — and the
   SECOND is a partner exactly when `Y == 1`, which is to say when the
   whole column comes down to one identity. **In that case the second
   slot may be a partner**: spacing lengthens, so a partner CAN carry
   the longest published length while folding onto the shortest, which
   is exactly what the four-spelling column above asks for. Revision 4
   barred both of the first two slots on the reasoning that a partner
   copies its parent's length, and that reasoning is retired with the
   construction that made it true. Nothing else the second slot carries
   is put at risk by this, because `Y == 1` means every present cell has
   the same trimmed, case-folded text and therefore the same word count:
   the published word range is a single number there.
4. Partners are assigned to identities in ascending identity order, one
   each, then a second each, and so on, so that the collisions are
   spread rather than piled on one identity. A partner is only ever
   taken from a parent of its own FAMILY — its band, and on free text
   its numeric class as well — because neither construction moves the
   trimmed characters, so a partner reads back in its parent's alphabet
   counts and its parent's numeric class, and taking one from another
   family would meet the folded count by missing a different published
   one.
5. **The layout is CHECKED against what the families actually supplied,
   and repaired where a collision could not be built. THIS RAISES: a
   published `n_distinct_folded` that revision 5 missed on descriptions
   whose own values meet it is now met** (plan amendment A-P3-12).
   Steps 1 to 4 settle which slots carry the collisions before any
   spelling exists, and what a family can SUPPLY is a fact about
   spellings: its identities' own case positions, and whatever edge
   spacing their lengths leave inside the taking slot's window. Spacing
   only lengthens, so an identity pinned to the LONGEST published
   length supplies no spaced partner at all, and a family whose flips
   are spent supplies no further one. A layout can therefore ask one
   family for more collisions than it holds while another family of the
   same column has room to spare. Measured over 1,200 descriptions a
   real producer wrote, every one of whose own values is an exact
   assignment of every count it publishes: 44 of them, 3.7 per cent,
   lost the published folded count that way, and the feasibility check
   of G12 never fired on one of them, because that check counts a whole
   alphabet and knows nothing about families, slots or windows.

   So the column is laid out AGAIN. The layouts are offered in the
   fixed order below, and the FIRST one that supplies every collision
   it owes is the answer:

   1. **the layout of steps 1 to 4, unchanged and offered first.** A
      description that layout answers is answered by it, so this step
      can reach no column the earlier rule already met, and no twin
      that met every published count changes by one byte;
   2. **the same layout with every family that fell short asked for no
      more collisions than that layout showed it supplies**, the
      surplus passing to the next family G9.6's choice rule admits.
      Where the repeat falls short again the ceiling is lowered again,
      at most once per group;
   3. **layouts 1 and 2 with the slots carrying the two published
      length ENDS taking a collision before any other slot their family
      admits.** The pinned slot is the one place in a family where
      being an identity costs the family its whole spacing supply and
      being a partner costs it nothing: pinned to the longest published
      length an identity can be lengthened by nothing, while a PARTNER
      pinned there is built by spacing its own family's shorter
      identity out to that length;
   4. **all of the above over each further packing of G9.6**, in that
      section's own order, and then over the packings that section's
      search reaches by holding ONE group to ONE family. A description
      can have several exact packings; one that gives every group a
      family of its own leaves no slot a same-family sibling, so no
      collision can be built at all, where another packing of the very
      same counts puts two groups together.

   **A repair may not give up a count the first layout held.** The one
   count a different layout of the same packing can lose is the one
   this walk names for itself: a layout that ran out of spellings and
   had to write one twice gives up the raw distinctness count and the
   repetition pattern with it (owner decision 6). So a layout is
   accepted only when it repeats no more than the first layout did.
   Trading raw distinctness for the folded count is the trade this
   section refuses, and this refuses it by construction rather than by
   measurement.

   **The walk ends in a stated number of steps.** At most two hundred
   and fifty-six candidate packings are examined on one column, counted
   across both of G9.6's tiers; the per-family ceiling is lowered at
   most once per group; and every layout is a fixed function of the
   description, so two implementations that follow this order write the
   same bytes. Where every offered layout falls short the column KEEPS
   THE FIRST, and the folded count it missed is recounted from the
   finished cells and named as a deviation — which is what happened to
   every one of them before this step existed.

   **This step moves no other published fact, and the reason is
   structural rather than measured.** Every layout it offers assigns
   the same group sizes to the same class-and-alphabet families as some
   exact packing of G9.6, so all four class counts and both alphabet
   counts are met by construction; the collision choice is a
   permutation of the groups, and the occurrence multiset pairs a size
   with a made-up value and never with a position, so it is
   permutation-invariant; both published length ends travel with their
   carriers. What the step CAN move is which spelling a slot writes,
   and so how many cells open with a character a spreadsheet reads as a
   formula. Measured over the same 1,200 descriptions: 42 of the 44
   repaired columns write the same number of such cells as before and
   two write nine and twelve where they wrote none. Writing fewer of
   them conforms, here as in G9.6.

**Why edge spacing costs no other published fact.** `n_all_digits` and
`n_code_alphabet` are read from the TRIMMED value, so a space at either
end moves neither. Word counts are read as whitespace-separated words,
so a space at either end adds none. The numeric class a cell reads back
as is read after trimming, so a whole number stays a whole number. The
length is read from the raw cell, which is why step 3's window exists
and is the ONLY fact spacing can move. The twin writer quotes a field
for a comma, a quote character or a line ending and for nothing else,
and the reader reads with `skipinitialspace=False`, so the spacing
reaches the file and comes back unchanged.

**The bound on the walk over one parent's family.** Two different orders
of one parent's family build two different spellings — a different
spacing gives a different string, and a different flip set gives a
different string. A candidate is refused only when the column has
already written that exact spelling, so at most one order per piece of
text the column has recorded can be refused and the walk ends by the
time it has tried one more than that. This is a true bound of the shape
G9.2 says the ENUMERATION's walk does not have, and it is true here for
the reason it is false there: this family has no class check, no
"no value" check and no date check on it, because a partner inherits all
three answers from a parent that already passed them.

### G9.4 The capacity rule

Capacity is decided **before any cell of the run is generated**, in the
generation-feasibility stage, so a shortfall never produces a partial
file.

**Capacity is a property of a FAMILY, not of an alphabet** (P2-C1-F2).
Revision 1 defined it as

```
capacity = sum over L in [min_length, max_length] of |A|**L
```

and that number is not the domain any construction of this document
generates. Three rules narrow it, and all three were already in this
document when that formula was written: G9.1 fixes the first and last
character positionally, G9.5 step 4 fixes what the leftmost character
may be so that the value falls in its own alphabet band, and G10.2
requires every cell to read back as its own numeric class. The `WIDE`
alphabet at length one has 95 members; the ordinary-text construction at
length one in the wide band produces **25** different values, because
the space is refused at both ends, the four characters a spreadsheet
reads as the start of a formula are refused at the front, and two of the
remainder are spellings that mean "no value". A planner quoting 95 there
promises a column it cannot write.

**The definition.** A **family** is one (class, band, length, word
count) combination. Its capacity is the number of indices its
mixed-radix map (G9.2) has:

```
capacity(class, band, L, w) = the number of indices of that family's map
```

computed with a **saturating rule** — every power stops accumulating
once it passes `2**62`, which is far above any row count a table can
hold, so every comparison this decision makes is exact and the
arithmetic costs a few dozen multiplications whatever `max_length` says.

The capacity is an **upper bound on what the walk produces**, never a
lower one: the positional rules of G9.1 can put two indices onto one
spelling, and the three rejection rules of G9.2 remove candidates. That
direction is the safe one — a run can only ever write fewer values than
the capacity claims, never more — and the number a refusal quotes is the
number the WALK produced, counted by the same walk that would have
written the cells, so the message states a fact rather than a bound.

**Where the demand is settled.** The class of every group, its band and
its length are settled in the feasibility stage (G9.5 steps 1 to 5)
before any capacity question is asked, so every group belongs to exactly
one family and each family's demand is the number of groups in it. A
family whose walk runs out before its demand is met is what triggers the
outcome table below.

Where fold collisions are required, the same rule is applied to the
sub-domain a partner can be built FROM, and that sub-domain has two
halves because G9.3 has two constructions (P2-C2-F6): the spellings
holding a character with a case, which a case flip varies, and the
spellings shorter than the longest published length, which edge spacing
lengthens. Counting only the first is what refuses a column whose
collisions the second can build, so both are counted and their counts
add — two different parents never build the same partner. Only where
BOTH halves are empty are the collisions genuinely unbuildable: that is
a column whose one permitted length holds no character with a case,
which is the corner owner decision 6 governs on a declared identifier
and the `generation-domain-too-small` refusal on the other two roles.

**When capacity cannot be met**, the outcome depends on the role, and
each outcome is fixed here:

| role | outcome |
|---|---|
| `identifier` (declared) | **No refusal.** Owner decision 6 governs: LENGTH WINS and invented identifiers repeat. The fewest necessary values repeat, and the report names the column, the number of duplicates and the join consequence. Raw `n_distinct`, `n_distinct_folded` and `n_distinct_by_occurrences` all become REPORT-ONLY for that column, each achieved value named beside its published one (P2-R4-F4). |
| `constant`, `binary`, `categorical` | **Cannot arise.** The withheld-level and variant alphabets of G8 have no end. |
| `count`, `continuous` | **Cannot arise.** The leading-zero family has no ceiling (owner decision 8): order `k` is computed directly for whatever `k` the published counts ask for, and no implementation may impose a ceiling of its own (P2-C1-F5). |
| `datetime` | **No refusal.** Cardinality is APPROXIMATED under the envelope. |
| `free_text`, `numeric_unrepresentable` | **REFUSAL — `generation-domain-too-small`.** |

**This table settles CAPACITY, and capacity alone.** Two of the four
refusals G12 lists are raised for a different reason — published facts
that contradict one another outright rather than a domain that ran out —
and one of those reaches a declared identifier, whose row above says
only that a domain too small for its multiplicity map does not stop the
run. G12 carries the closed list of all four.

**The named refusal, and why it is these two roles.** Both publish
`n_distinct_by_occurrences` under multiplicity parity (owner decision
2): an exact repetition pattern, group size by group size. The map
exists precisely so that a generator never invents a repetition pattern.
Where the domain cannot supply the distinct spellings that map requires,
the only ways forward are to invent a different repetition pattern —
which the map forbids — or to write a value longer than `max_length`,
which contradicts a published length fact. No owner decision authorizes
either for these two roles, so generation refuses. The refusal:

- is a refusal of GENERATION and says so — **the profile is valid**;
- names the column, the length and the alphabet band of the family that
  ran out, what that family's values have to read back as, the number of
  different values the profile requires of it and the number the walk
  produced;
- names the two facts that cannot both hold, in the person's words;
- gives remediation that does not assume the person still holds the
  table.

It is raised in the feasibility stage, before any output file is
created, so a refused run leaves the folder exactly as it found it.

### G9.5 Free text

Free text is INVENTED language. The generator never samples, quotes,
templates from, or paraphrases source text, and no source text is
available to it in any case (G1). Any future change carrying source
language into the profile or the twin is a charter change requiring an
owner decision and a privacy review (P2-D9).

The construction, and its precedence order — each later constraint is
met only within the freedom the earlier ones leave, and the report names
any that could not be met:

1. **The repetition pattern.** `n_distinct_by_occurrences` fixes the
   groups: for each key (a row count, read as a number in base ten;
   leading zeros are padding and do not change it) in ascending order,
   and for each of that key's distinct values, one spelling is invented
   and used exactly that many times. The groups' sizes sum to
   `n_present` and their number sums to `n_distinct`, by the contract's
   own invariant. **Every published count below is a count of CELLS and
   every group covers a whole number of cells**, so meeting a count
   means choosing which GROUPS answer for it — see "the packing rule"
   after step 4.
2. **The lengths, and WHICH group carries each published end.** Step 5
   assigns a length and a word count to every group. **It is not settled
   before steps 3 and 4 and it may not be** (P2-C4-F2). Revision 5 said
   the lengths came first and depended on nothing the other steps
   decide, which is false in the direction that costs published counts:
   a length decides which class-and-alphabet pairs a group can stand in
   at all, so a shape fixed in advance can make a count unreachable that
   another shape reaches. Steps 2, 3 and 4 are therefore ONE allocation
   — see "the packing rule" after step 4.
3. **Numeric class.** The `n_numeric`, `n_out_of_range`,
   `n_contradictory` and `n_not_numeric` counts are met by the
   class-preserving constructions of G10, exactly as for a numeric
   column. A free-text column publishes these counts too, and they are
   EXACT-OBSERVABLE by construction on every role. A group may answer
   for a class only where some band can write that class at that group's
   length.

   **How a number is spelled, and how many spellings a family holds**
   (landing 2b.4). In figures alone a number of `L` figures is written
   with NO INVENTED LEADING ZERO FIRST: `0` to `9` at one figure, and at
   two or more the spellings that do not open with a zero, `10` to
   `99`, before those that do, `00` to `09`, so the family still holds
   `10^L`. In the code band a number of two characters is a minus and a
   figure; of `L >= 3` it is `L - 2` figures spelled the same way, an
   `e`, and one last figure taken in the order `0 1 2 3 4 5 6 7 8 9`. In
   the wide band a number of two characters is a figure and a point; of
   `L >= 3` it is `L - 2` figures, a point, and one last figure in the
   order `5 0 1 2 3 4 6 7 8 9`. Those two bands hold ten at two
   characters; the wide band holds `10^(L - 1)` at `L >= 3`, and the code
   band only its spellings whose exponent's figure is nought and whose
   figures before the `e` open with no zero -- ten at three characters,
   `9 · 10^(L - 3)` above -- because an exponent's figure that varies
   multiplies the number by a power of ten (integration repair of
   landing 2b.4: sixty integers from -10 to -69 beside three-letter
   words came back as `0e0` to `9e5`, mean 83,333 against -39.5, with
   every check passing). A column needing more of them than that is
   refused by G9.4, as it was before landing 2b.4. **Every run of figures before
   the mark with no leading zero is taken under all ten last figures
   before any run that opens with a zero** (landing 2b.4, repair): the
   walk used to take a block of `10^(L - 2)` runs per last figure, which
   ends with the runs opening with a zero, so from four characters up
   the ninety-first number of each block was `00.5` and a column needing
   two hundred such numbers wrote twenty with an invented zero. **The
   exponent's figure is nought first** (landing 2b.4, repair), so a number
   of the code band is as large as its figures for the first
   `10^(L - 2)` of its length; it was `1` first, and a column of integers
   near minus forty needing more than that came back as `9e5` and `7e6`. The last figure used to be
   a constant -- `e1` and `.5` -- which spent a character on nothing
   and left ten spellings where a hundred exist: a column of readings
   written `7.2` beside comments, with twenty-five different
   three-character numbers, was refused. And the first number of every
   width used to be all zeros, so integers beside comments came back
   spelled `000...0001` across forty-four characters.

   **3a. A number's length is its own** (landing 2b.4). A column of
   text publishes no length for its numbers, only for its cells, and
   the average of those is set by the words. So once the packing below
   has settled every group's class and band, each group that reads as a
   number and carries NO published end takes a length of its own,
   largest group first, ties by group order, inside the published ends:
   the length of the census form step 7 settles it to wear, where it is
   given one; otherwise the SHORTEST length at or above its band's
   shortest -- one figure, a minus and a figure, a figure, a point and a
   figure -- at which its band still has a number with no leading zero
   to give AND WHOSE FORM THE CENSUS DOES NOT NAME (landing 2b.8, plan
   P4-D73: step 7 settles a named form over the number groups EXACTLY,
   so its cells are spoken for, and every number of the wide band four
   characters long is written `%%.%` -- a column publishing that form on
   199 cells settled those 199 and then gave forty-eight groups the
   census owed nothing a length of four, so the twin wore it on 247
   cells and failed its own description while the table passed. Where no
   length inside the published ends escapes the named forms the first
   length with room stands, the census is missed, and the report names
   it, exactly as step 3b already states); in
   the code band only the numbers whose exponent is nought
   count as given, so a column needing more of them lengthens them
   instead of raising them by a power of ten (landing 2b.4, repair). A
   number group carrying an end spends one spelling of its own band and
   length before the others are placed: uncounted, a hundred numbers of
   three characters were given to the code band beside the one carrying
   the shortest length, and the family of a hundred refused the column. Every other group is then walked toward the published
   average and word count by step 5, with those lengths held and each
   of those groups holding one word. A group carrying an end keeps it.
   **The report says what this cannot do**: a column of text publishes
   how many of its cells are numbers and nothing about what those
   numbers are, so a twin holding any names that nothing published
   places them -- a mean or a range computed over them means nothing
   about the table. Integers near a hundred and twenty beside comments
   came back with a mean near fifty and every check passing; the line
   is what stops that being silent, and no validation obligation is
   raised for it, because the description carries no fact to check.

   **3b. A number stands in the band its forms are written in**
   (landing 2b.4). The packing meets the class and alphabet counts and
   knows no form, and filling the number row's code cell before its
   wide cell can put numbers written `7.2` in the code band, where no
   spelling is `%.%`. So where a census form that reads as a number
   still owes cells in one band, a group of ordinary text carrying no
   end in that band is EXCHANGED with number groups carrying no end in a
   band holding more numbers than its own forms owe, whose sizes make
   the text group's size exactly -- read off the reachable sums -- and
   which can each stand in the other's band at their lengths. Cells
   leave and enter each band in equal numbers and each class keeps its
   own, so every class count and every alphabet count stays exactly
   where the packing put it. The text groups are offered smallest first,
   and no exchange passes what the forms owe. Where none exists the
   census is missed and the report names it: on a column whose only
   single-cell text group carries an end, one cell of a number form can
   stay unpaid.

   **Numbers leave the code band where text can take their place**
   (landing 2b.4, repair). A number of the code band is written with an
   exponent, and the packing prefers no band, so a column of readings
   written `7.2` beside one-word notes -- whose code-alphabet cells were
   all notes -- had a hundred and seventy-eight of its readings written
   `175e0`. So BEFORE the exchange above, and only where no census form
   reading as a number is written in the code band, a group of ordinary
   text carrying no end in the wide band that can stand in the code band
   at its length is exchanged with number groups carrying no end in the
   code band that can stand in the wide band, whose sizes make its size
   exactly, the smallest text groups first, until no number is left in
   the code band or no exchange is. Every class and alphabet count stays
   where the packing put it. The report names every number still written
   with an exponent, as a fixed remark: a check written against the
   table's own integers can fail on `54e0`.

   **3c. The text keeps a tenth of its cells in values written once**
   (landing 2b.4, repair). A column holding numbers is free text only
   while its other cells are not a vocabulary: the profiler reads a
   column whose non-number cells wear repeating spellings in more than
   nine tenths of them as numbers beside labels (its rule 7b). The
   packing knows no role and can give every value written once to the
   numbers: a column of readings beside notes, a thousand rows at a floor
   of fifty, was described again as numbers beside labels and failed its
   own validation. So after the exchanges above, where the number groups
   and their cells both reach the long-tail line and the text's values
   written once hold fewer than a tenth of its cells, a text group of
   several cells carrying no end is exchanged with that many number
   groups of one cell carrying no end in the same band, each able to
   stand in the other's class at its length, the smallest text groups
   first, until a tenth is reached or none is left. Cells leave and
   enter each class in equal numbers inside one band, so every class and
   alphabet count stays exact.
4. **The alphabets.** `n_all_digits` cells are written from `DIGITS`;
   a further `n_code_alphabet - n_all_digits` cells from `CODE`, each
   carrying at least one non-digit character at its leftmost position so
   it does not count as all-digits; the remaining cells from `WIDE`,
   each carrying at least one character outside `CODE` at its leftmost
   permitted position so it does not count as code-alphabet.

   **The bands a group may take depend on the class it took in step 3**,
   and that dependency is part of the rule rather than something an
   implementation may leave to chance (P2-C1-F1). A cell whose notation
   conflicts with itself is written inside accounting parentheses, which
   the code alphabet does not hold, so such a group can answer for
   neither alphabet count. A cell of ordinary text cannot be written in
   figures alone, because figures alone read as a number. Packing the
   two alphabet counts without those rules lets a count the description
   publishes be missed while a construction that could have met it goes
   unused.

   **A cell counted in the code alphabet holds ONE word**, because the
   words of step 6 are separated by a space and a space is not one of
   that alphabet's characters. **And so does a cell of any of the three
   numeric classes**, for a plainer reason that was left unsaid and cost
   an exact fact (P2-C4-F2): every numeric construction of step 3 writes
   one unbroken run of characters — a number, a number too large to
   hold, a notation inside accounting parentheses — and none of them has
   a space anywhere in it. The rule is therefore stated over FAMILIES
   and not over one band: a family that cannot hold a group's word count
   is not a family that group may be given.

   Every group but the two that carry the published word extremes may
   therefore have its word count brought down to one wherever the family
   it is given needs that: `n_code_alphabet` and the class counts are
   EXACT-OBSERVABLE and `words.mean` is APPROXIMATED, so the exact fact
   wins and the change is measured and named. The two groups carrying
   the ends keep their published word counts, and take only families
   that can hold them — and WHICH two groups those are is decided by the
   packing below, not before it. Reading this rule as being about the
   code alphabet alone let a word-extreme carrier be given a numeric
   class, write one word, and miss `words.max` with nothing said, which
   is why G12 now recounts all four ends from the finished cells.

   **TWO CHARACTERS ARE ENOUGH FOR A NUMBER IN THE CODE BAND**
   (P2-C4-F2). A number written in that band needs a character the
   figures do not hold, and a leading minus sign is one: `-3` reads back
   as a number, holds a character outside `DIGITS`, and is two
   characters long. Requiring three — which an exponent form needs —
   loses published counts a real table reaches, because a source of one
   one-character number, five two-letter words and six copies of `-3`
   publishes twelve code-alphabet cells of which six read as numbers,
   and its own values are an exact assignment. So this family begins at
   length two. At length one it is genuinely empty: one character that
   reads as a number is a figure, and a figure is all-digits.

**The packing rule, stated once for steps 2, 3 and 4** (P2-C1-F1,
P2-C2-F1, P2-C4-F2). Steps 3 and 4 are **ONE packing, not two**, and
step 2's choice of which groups carry the published ends is **part of
that same packing, not an input to it**. Every group
answers for one class count and one alphabet count at the same time,
and which PAIRS it may stand in depends on its own length, so deciding
the classes in one walk and the alphabets in a second throws away joint
assignments that exist. Round 2 built a five-row column with three
singleton numeric groups and one doubled text group whose joint
class-and-alphabet assignment is exact and which two separate walks
missed by one code-alphabet cell.

The packing is therefore stated over a GRID of cells carrying MARGINS.
A margin is one published family of counts that divides the cells
between them: here the rows are the four class quotas of step 3 and the
columns are the three alphabet quotas of step 4, and each group takes
exactly one cell of that grid out of the set its length permits. Given
the groups, every margin and each group's permitted cells, an
implementation MUST produce an assignment in which **every quota of
every margin is met exactly, whenever such an assignment exists**. A
largest-group-first greedy rule does not satisfy this and is not
conforming: on groups of 2, 2 and 3 with a digits quota of 4 it
writes 5.

**THE SHAPE IS PART OF THE ANSWER, NOT PART OF THE QUESTION**
(P2-C4-F2). "The set its length permits" is not a set the description
publishes: the description publishes only that SOME group's values are
`length.min` characters long, that SOME group's are `length.max`, and
the same for the two word extremes. Which group that is, and what
length every other group takes, is the implementation's own choice, so
an implementation that makes it before the packing has narrowed the
packing with a fact the profile never carried. Revision 5 did exactly
that — first group takes the shortest, second takes the longest — and a
producer profile loses a published count to it. Take a source of twelve
cells: one of
them holds two words in three characters; five hold one character that
the code alphabet has; six hold two characters it does not. The
description publishes `n_code_alphabet = 5`, and the source's own
twelve cells are an exact assignment of it. But pinning the longest
length and the largest word count onto the group of five bars that
group from the code alphabet, and no other group covers five cells, so
every seed wrote one code-alphabet cell against the five published.

So the completeness sentence above is read over the shape as well:
**every quota of every margin is met exactly whenever SOME shape the
description leaves open admits such an assignment**. The shapes are
offered in this fixed order, and the FIRST whose grid packs every quota
exactly is the one taken:

- the pairs of groups that may carry the two ends, in ascending order of
  the pair — the group taking the shortest length first, then the group
  taking the longest — so the description's own first two groups are
  tried first and a description the earlier rule already answered is
  answered identically, byte for byte;
- under each pair, first the reading that holds every other group to the
  length step 5's walk gave it, and then the reading that holds only the
  two end-carrying groups to their lengths and lets every other group be
  written at any published length. The first reading is preferred
  because it keeps the approximated average where the walk put it; the
  second is reached only where no pair's first reading packs every
  count, because `length.mean` and `length.p50` are APPROXIMATED and the
  counts are EXACT, and an exact fact outranks an approximated one. A
  group lengthened under the second reading takes the shortest permitted
  length at or above the walk's, so the average moves as little as the
  exact counts require, and where the middle length then lands outside
  the bound of G12.6 the report names it like any other approximated
  fact that could not be held.

**Two groups of the same size are the same question**, and that is what
keeps this bounded. No published count tells two groups covering the
same number of cells apart: the grid ranks a group by its size and by
nothing else, and step 5's walk gives the groups carrying no end the
same lengths in the same amounts whichever of two equal-sized groups
took an end. So a pair whose two SIZES an earlier pair already offered
can only fail the same way and is skipped, and the number of pairs
actually walked is the square of the number of different group sizes
rather than of the number of groups. A shape whose group sizes and
permitted cells repeat a shape already tried is skipped for the same
reason, since whether a grid packs depends on nothing else.

Where NO pair and no reading packs every count — which a description a
real table produced does not reach, because that table's own values are
one such shape — the description's own first two groups carry the ends
and the fallback below applies.

**AN ABSORBED ALPHABET COUNT IS PACKED AS THE PRODUCER PUBLISHES IT**
(plan P4-D298). `n_all_digits` and `n_code_alphabet` are published
through the disclosure rule (profile contract, "the two alphabet counts
ask the disclosure rule"): where a side of either census is below
max(2, `small_cell_floor`) the smaller is counted into the larger, so
the block publishes nought or every present cell where the table's own
count sat just short of that end. **Stated as arithmetic** (the
oracle's independence repair of 2026-09-19), with `L` = max(2,
`small_cell_floor`): a count `c` of `n` present cells splits them into
the `c` inside and the `n - c` outside, and each side that is not
nought is a group. Where no group is below `L`, `c` is published as it
is. Otherwise the smaller side is counted into the larger, and an even
split goes INSIDE: `c` is published as `n` where `c` is at least half
of `n`, and as nought where it is less. A twin meets such a count wherever
describing it again publishes the same number — which is how
`synthtwin validate` holds a twin to it — and the table itself meets it
in exactly that sense: eleven figures beside one `ab` publish
`n_all_digits 12` beside `n_numeric 11`, twelve cells in figures alone
are twelve numbers, and no assignment of whole groups meets both. So the
margins are READ, in this order, and the whole search above — every
pair, both readings of a free group's length — is asked of each reading
until one packs:

1. the published counts;
2. every other pair of a figures count and a code-alphabet count, each
   either equal to its published count or a count the rule publishes as
   it, the figures never more than the code alphabet, in ascending
   order of the two differences summed, ties by the figures count and
   then the code count, each the smaller first.

**No frozen case witnesses the even split, the census line or the
filter above** (measured by the skeptic of the independence repair,
2026-09-19: an even split sent outside, a side on the line counted as
below it, and the figures let exceed the code alphabet each left every
vectors file unchanged). They are witnessed one call at a time in
`tests/test_oracle_rule_witnesses.py`, asked of the oracle and of the
shipped rules alike (the producer's `absorbed_total` and the generator's
readings): fifteen counts with the answers worked out
from the arithmetic above (five of ten at a floor of eleven is published
as ten; eleven of thirty is published as eleven, a side on the line not
being below it), and the whole ordered list of readings of twelve cells
publishing nought and nought (twenty-one pairs, 0 to 5 each, the figures
never more than the code alphabet), with four registered mutants of
the count and three of the readings each turning its witness red.

A description that packs as published is answered exactly as before,
byte for byte; the four class counts are free text's own and are not
read (the contract protects them on a declared record number alone). A
reading is a statement about the published description and never about
the table: every count it packs is published the same way. At most 256
readings are asked, and the fallback below applies where none packs.
**Measured** at e53d5f4 on the battery of review item P2-C4-F2: 158 of
3,186 producer columns reached the fallback, and none reaches it with
this rule. Every recount of the two counts reads a count equal to the
published one as it stands and any other through the same rule, so a
twin holding the table's own eleven figures is not named for them.

**A grid may carry more than two margins, and where the description
publishes more than two families over the same cells it MUST**
(P2-C3-F1). Two margins is this step's shape, not the rule's: an
unrepresentable column publishes three families over one set of cells
(G10.5), and the completeness sentence above governs all of them
together. An implementation that picks two of the published families,
derives the rest by a choice of its own, and packs that instead has
answered a question the description never asked — which is what lost
six exact counts on a genuine six-row column, in G10.5's own words.

The order is fixed so that two implementations pack the same way. Each
margin ranks its own counts in ascending order of their published
values, ties by the order the contract states them in; a cell then
carries one rank per margin and the cells are filled in ascending order
of those ranks read margin by margin, ties by the cell's own number,
which over two margins is exactly row-major order over ranked rows and
ranked columns. Within a cell the different group SIZES are offered in
ascending order and each size offers as many copies as the cell can
still hold, falling back to fewer; a fill that leaves a later cell
unable to finish is undone and the next is tried; and groups are handed
to their cells in group order, so the first cell takes the earliest
groups. A cell is the last of one of its counts exactly when nothing
after it can answer for that count, and then it takes what that count
still owes rather than choosing. A grid one cell wide is the
single-axis rule, which is how the same statement governs the alphabet
packing of a declared identifier (G9.6), and a grid of three margins is
how it governs the unrepresentable column of G10.5.

**The smallest quota is answered for first**, and the largest last:
inside every margin the counts are taken in ascending order of their
own published values, ties by the contract's own order, so the count
that absorbs whatever is left over is filled at the end. That is a
statement about the ORDER and not about the answer — the completeness
above is unchanged either way — and it is written down because it is
what keeps a genuine description answered at once. Filling the largest
count first spends the small group sizes on it and leaves the small
counts to be made out of the large sizes, which is the shape a packing
walk can spend an unbounded amount of time undoing.

**ONE thing bounds the walk, and it is not a bound on the SHAPE of a
description, on its size, or on the work the walk spends** (P2-C2-F1,
P2-C3-F1). Revision 1 carried two structural ceilings — one refusing
any profile publishing more than a stated number of different group
sizes, the other stopping after a stated number of steps in a walk with
no pruning — and round 2 showed a description the PRODUCER emits
reaching the first, losing three published counts an exact packing
reaches. The repair replaced them with a ceiling on WORK, permitted on
the assertion that no producer description could reach it, and round 3
disproved that assertion: a 2,710-row unrepresentable column with 38
groups, class counts 592, 879 and 1,239 and sign counts 1,578, 540 and
592 needs more work than the ceiling allowed. **All three ceilings are
withdrawn, and no implementation may carry one.** What is left is the
pruning, which costs no exactness at all:

Before the walk descends past one group size it asks, in one
whole-number test, whether the sizes it has not yet decided can still
reach a total the cell accepts; and on entering a cell it asks whether
every count still owed, on every margin, can be made at all from what
is unplaced. Both are necessary conditions, so a branch either of them
cuts held no answer. A state the walk has already found no answer for —
which cell is being filled, which sizes are unplaced, what every count
of every margin still owes — is never entered twice, and the number of
different states is finite and fixed by the description before the walk
begins, so **the walk ends on every input the loader accepts and no
count is traded to make it end**.

**What that costs, stated rather than hidden.** The packing question is
the classic partition one and has no known quick answer, so a
contract-valid document nobody produced could take a long time. That
cost is accepted for the same reason plan P2-D2 accepts a document too
large for the machine failing on the memory-exhaustion path rather than
being refused by a cap: a bound that keeps the run short by writing a
number the description did not publish is the worse of the two, and it
is the exact shape of failure the section-9 head of the contract names
— "the published facts cannot all hold" must mean no assignment
satisfies them, PROVED, not that the search was stopped. What keeps
genuine descriptions quick is that their own values are an answer and
that the walk is handed only the relationships the description
publishes, so it is never asked to settle a cross-tabulation the real
column never fixed.

**The packing is COMPLETE, and that is the whole of what steps 3 and 4
owe.** Every count of both margins is met exactly whenever any
assignment of whole groups meets them all, on every description, and
the walk finds such an assignment whenever one exists. A description
for which none exists is one whose own published facts cannot all hold
at once — no profile a real table produced is one, because that table's
own values are such an assignment — and it is the section-9 shape of
the contract's head, proved rather than assumed. G12 states what a run
does there and what its report says; nothing in this section grants an
implementation a lesser outcome on a description an assignment exists
for.

5. **The lengths.** `length.min` and `length.max` are EXACT-OBSERVABLE
   and are pinned: one group takes `length.min` and one takes
   `length.max` — **the two the packing rule above settled on, not the
   description's first two** (P2-C4-F2). The remaining groups start at
   `base`, the published
   `length.p50` rounded to a whole number by the rule of G5.4 and
   clamped into `[min, max]`. Let `n = n_present`, and let `S` be the
   nearest whole number to the exact product `length.mean * n`, ties
   upward, computed on the exact rational value of the published
   binary64 rather than in floating point. The residual

   ```
   R = S - (sum over groups of occurrences * assigned length)
   ```

   is spent one character at a time: while `R > 0`, add one to the
   length of the group with the largest occurrence count that is below
   `max` (ties by group order), subtracting its occurrence count from
   `R`; while `R < 0`, subtract one from the group with the largest
   occurrence count that is above `min`, adding its occurrence count to
   `R`. Stop when `R` reaches zero, changes sign, or no group can move.
   `length.mean` and `length.p50` are APPROXIMATED; this is the fixed
   rule their bound is measured against.

   **Where no group can move and `R` is not zero, the numbers carry it**
   (plan P4-D190). The groups this walk moves are the ones no rule
   holds: a number holds its own length (step 3a) and a group wearing a
   form its form's length (step 7), so a column whose remaining groups
   all carry the two ends -- or all stand at the end `R` points toward
   -- left `R` unspent, and its twin missed `length.mean` on every seed:
   sixty numbers, thirty-eight codes and two `TRUE` cells published 2.99
   and the twin wrote 2.95. So where no group the walk may move can move
   toward `R`, the number groups carrying no end whose length's form the
   census does not name are walked the same way, largest occurrence
   count first, ties by group order, one character at a time: a group
   grows while below `max`, and shrinks while above both `min` and its
   band's shortest, in each case only to a length at which its band
   still has a number with no leading zero to give -- counting every
   number group's length, the two carrying ends included -- and whose
   form the census does not name. Stop when `R` reaches zero, changes
   sign, or no number can move. A number holds one word at any length,
   so no word count moves. Where `R` changes sign the walk above had
   room and is left as it stood, so no column it already served moves.
6. **The words.** `words.min` and `words.max` are EXACT-OBSERVABLE and
   pinned onto the same two groups the lengths pinned — whichever two
   the packing rule settled on; `words.mean` is APPROXIMATED
   and is approached by the same residual walk. A group of length `L`
   can hold at most `(L + 1) // 2` words (each word at least one
   character, each separator one space). **A description whose
   `words.max` is more than `length.max` carries, or whose `words.min`
   is more than `length.min` carries, publishes facts that cannot all
   hold**, and G12 refuses generation for it before any cell is built
   rather than writing a twin and naming the miss (review item
   P2-C5-F4). Lengths and word counts are paired by ascending order —
   the longest cells take the most words.

   What is left for the ceiling above to bite is a group carrying
   NEITHER published extreme, whose count is the walk's own step toward
   the APPROXIMATED `words.mean` rather than a number the description
   publishes: that count comes down to what its own length carries, and
   the change is measured and named like any other. The two carrying
   groups are never brought down this way — their lengths are the two
   published ends, and a description in which those ends cannot hold
   their own published word counts never reaches this step.
7. **The text itself.** A group of length `L` and word count `w` is
   written as `w` words separated by single spaces, whose lengths differ
   by at most one and sum to `L - (w - 1)`, longer words first. Each
   word is the next spelling of the group's alphabet enumeration
   (G9.2) at that word's length, so the whole cell is distinct from
   every other group's cell.

   **Where the column publishes a census of written forms and one of
   them fits this group, the group is written in that form instead**
   (contract 7.9.1, plan P4-D18). A form FIXES a length — every cell
   that wore one was exactly as long as the form — so which lengths a
   group may be offered is the whole question here.

   **A GROUP CARRYING A PUBLISHED LENGTH END keeps its length exactly**,
   because `length.min` and `length.max` are EXACT-OBSERVABLE. **EVERY
   OTHER GROUP may take a form of another length, but only while the
   published AVERAGE can still afford it** — the total length may move
   by ONE CHARACTER in each direction and no further, measured against
   what the packing's own lengths already spend (review round 3 finding
   10; the rule stated here was "the assigned length", which met one
   form of a blood-pressure column and missed the two beside it).

   That budget is the precedence rule of this section made arithmetic:
   an exact count outranks an approximated average, and it spends the
   average's own slack to the last character and no further. Swept
   against two real columns at four budgets — half the rows, a
   fiftieth, a hundredth and one character — only one character keeps
   BOTH a blood-pressure column's four forms and a column whose census
   asks for lengths its average does not want.

   **THE FORM IS SETTLED BEFORE THE LENGTHS ARE WALKED, AND THE GROUP
   THAT WEARS ONE HOLDS ITS FORM'S LENGTH** (landing 2b.8, plan
   P4-D75). The budget above is kept exactly as it is, and the order it
   is asked in is what changes. Step 5's walk toward the published
   average parks nearly every group on the middle length; the offer
   then ran against that budget, so a form of any OTHER length was
   refused for all but a handful of groups, and the budget — a rule
   written to spend the average's slack on the census — was spending
   the census on the average instead. So which form each group would
   wear is settled FIRST, by this same offer asked with a budget no
   column can spend, and that group's length and word count are then
   HELD through step 5 exactly as a number's own length is held by step
   3a. The published average is carried by the groups no form spoke
   for. The walk's own offer then costs the budget nothing, because the
   group already stands at the form's length and a swap of no
   characters is always afforded — which is why the sentences above
   still govern it and a test still pins them.

   **AND A FORM IS OFFERED ONLY TO A GROUP OF THE BAND IT IS WRITTEN
   IN** (landing 2b.8, plan P4-D75), on exactly the ground that a form
   is offered only to a group of the class it reads as. A form's band
   is the band its own first filling recounts into: `%%%-@` fills to
   `000-A`, which the code alphabet holds, and `%%/@` fills to `00/A`,
   which it does not, because the slash is not one of that alphabet's
   characters. The walk already refuses such a candidate and misses the
   census instead, so asking for it spent the form's debt on a cell
   that could never be written.

   **What the two together were measured to do.** On 800 rows of
   `%%%-@@@`-style codes at the default floor, whose census publishes
   FORTY forms of four lengths across both bands: before, the walk put
   777 of 791 groups at length five and the twin missed ALL FORTY
   forms, 405 cells short, writing `?!!!#` and `R---3` out of the
   fallback alphabet while `synthtwin validate` exited 3 and the table
   itself passed. With the lengths held, the asks covered all 715 cells
   the census owes, but 350 of them went to groups whose band their
   form could not be written in — 354 cells, which was the whole
   remaining shortfall. With both rules the twin wears every one of the
   forty forms at its published count and validates with nothing
   missed, on three seeds, and so does a column of REDCap `arm-record`
   identifiers, which missed its largest form before.

   A space survives into a form unchanged, so the form's own word count
   is fixed by the form, and a group can only wear one by being written
   with that many words. **THE SETTLING ASK EXCHANGES THE PACKED WORD
   COUNT THE SAME WAY IT EXCHANGES THE PACKED LENGTH** (landing 2b.8
   repair), and the walk's own ask does not. At the settling ask a
   group's word count is no more fixed than its length, so a form of
   another word count is offered -- but ONLY where the group can still
   stand in the class and alphabet cell the packing gave it while
   holding that many words, because those two counts are EXACT and the
   census may not be paid with them. A GROUP CARRYING A PUBLISHED END
   IS NEVER REWORDED: `words.min` and `words.max` are EXACT-OBSERVABLE
   and those two groups are what make them facts a recount confirms.
   The group is then held to the form's word count through step 5, so
   the walk's later ask agrees with the settling one.

   **Why the order alone was not enough** (review of landing 2b.8,
   finding 1). Holding the form's LENGTH freed one of the two packed
   numbers the census was being refused for, and the packed WORD COUNT
   was still holding the other. Measured on 800 rows of one-word codes
   mixed with multi-word prose, whose census publishes `@%%`, `@%%%`
   and `@%%%%`: the packing gives those code groups TWO words, because
   it spends `words.mean` exactly as it spends the average length, and
   every published form of the column holds ONE. The settling ask made
   626 asks and won 1; the twin missed ALL THREE published forms, 320
   of 800 cells short, and `synthtwin validate` exited 3 while the
   table passed. With the count exchanged as well, that column meets
   every published form at four draws of the shape, and a column of
   sentences beside one-word tags stops missing its census, its word
   clamp and `words.mean` together.

   The debt is over cells and a
   group covers its own number of them, so the walk settles the form
   owing the most cells, ties broken by the form's own spelling.

   **THE FORM IS AN ASK AND NOT A PROMISE**, exactly as the fold
   collision of G9.3 is. The candidate is still checked against the
   class the group has to read back as, against what the column has
   already written, and against the four neutrality tests; where the
   form's spellings cannot satisfy those, the walk is put back where it
   started and taken again WITHOUT the form, so a form can cost the
   column no value the ordinary rule could still have written. A column
   of prose publishes an empty census, so no group of it is offered a
   form and this paragraph is vacuous there — which is every free-text
   column the free-text promise was written for.

   **A FORM IS OFFERED ONLY TO A GROUP OF THE CLASS IT READS AS**
   (landing 2b.4). A form's class HERE is the class its FIRST filling
   reads as, and that is deliberately narrower than G8.3a's, which since
   landing 2b.13 asks the exponent filling as well. The asymmetry is
   named rather than left to be found: G8.3a settles the held-back
   levels of a column of LABELS, where a form the census names is owed
   by a known number of cells and the walk can be told to wear it,
   while this step packs a free-text column's groups against the class
   and alphabet counts at the same time, and widening which forms count
   as numbers here moves that packing. Widening it was not measured, so
   it was not done. An ask a group could never meet still spent the
   form's debt and
   the length budget, so a column of readings beside comments owing
   forty-four cells of `%.%` gave that form to one group. Ordinary text
   is offered the text forms by the walk above. **A number's form is
   SETTLED, not asked**: inside each band, the number-reading forms that
   band's spellings wear are settled over that band's number groups by
   an exact subset of their sizes, as G8.3 settles a label column's
   forms — a group carrying a published end first, and only for a form
   of exactly its length — and a group no form needs wears none. Asked
   group by group, the form owing most overpaid: eleven cells of `%%.%`
   were handed groups of seven and six. A form's spelling that reads as
   a number is refused where it opens with a zero before another figure,
   as the family's own numbers are, and a number whose settled form has
   already been paid is written without one rather than asked for
   another.

   **The stride matters and is part of the rule.** Two hundred and
   forty values taken in counting order out of a form holding a hundred
   thousand leave every position but the lowest at zero, so every cell
   ends alike — and a column whose cells all end in the same characters
   is not free text to the describer, it is a column of numbers wearing
   an affix. The twin then reprofiles into a role the source never had.
   The step is therefore multiplied by a stride sharing no factor with
   the form's supply, which is a one-to-one map onto it.

**A WORKBOOK COLUMN'S TRUTH VALUES ARE WRITTEN AS THEM** (plan P4-D198,
the final skeptic of stage 2's close). The workbook census publishes how
many cells of a column were truth values, and G2.2's writer gives the
boolean class only to a cell spelled `TRUE` or `FALSE`, which no made-up
word is: a column of 160 whole numbers, 138 codes `noteNN` and two `TRUE`
cells published `boolean 2` and its twin wrote none, missing
`workbook.cell-classes` at the default floor on every seed. So where the
table's workbook census publishes a boolean count `B` above nought for a
free-text column, after the classes and alphabets are packed and the
numbers' and the forms' lengths held (steps 3a and 7): among the groups
packed as TEXT in the CODE alphabet and held to no length by a number or
a form, in group order, the first covering exactly `B` cells is spelled
`TRUE`; failing that, the first two, in order, covering `B` between them
are spelled `TRUE` and `FALSE`. A group carrying a published end is taken
only where the length and the one word it is pinned to are the spelling's
own. Those groups' lengths are held with the others before step 5's walk
spends the average, and the walk of shapes in the packing rule takes a
shape only where such groups exist, keeping the first packing where no
shape offers them. At most two groups can be spelled so, since a value
written twice is one group: measured over sixteen twins of eight columns
of one to six truth values, two met the census before this rule and eight
after, and the rest still miss it, named by the quality report.

### G9.6 Identifiers

`min_length`, `max_length`, `all_whole_numbers`, `n_all_digits` and
`n_code_alphabet` are EXACT-OBSERVABLE in every case, since owner
decision 6 keeps the length, and so are the four class counts
`n_numeric`, `n_out_of_range`, `n_contradictory` and `n_not_numeric`,
which P2-D6 makes exact by class-preserving construction on every role.
The construction is G9.5 steps 1, 3, 4, 5 and 7, with that section's
packing rule applying here IN FULL — both margins and the shape search
— and four changes:

- **the four class counts are packed WITH the two alphabet counts, in
  one allocation, and which two groups carry the published length ends
  is part of that same packing** (P2-C5-F2). Revision 2 said the bands
  came from the two published alphabet counts and from nothing else,
  and that the shape search of G9.5 could not reach here because no
  group's length was an input to it. Both halves were false in the
  direction that costs published counts. A group written from an
  alphabet reads back as whatever the contract's classifier makes of
  it, so packing the alphabets alone READS a published class count off
  a construction instead of meeting it: a declared column of `N_7`,
  `no!!`, `x-y`, `913` and `-3` publishes 23 cells that read as numbers
  and 26 that do not, its own five values are an exact assignment, and
  the twin wrote 12 and 37. And once the classes are packed a group's
  LENGTH is an input, because one character cannot be a number and
  stand outside the figures at the same time — so pinning an end onto a
  group chosen in advance can make a count unreachable that another
  pinning meets. A column of `-48562`, `14618`, `3`, `37e999`, `^slX`
  and `tA` publishes an exact assignment in its own values, and pinning
  the shortest published length onto its two-row group, whose value is
  six characters long and reads as a number outside the figures, puts
  that group where no exact assignment has it. The candidate shapes are
  offered in the fixed order of G9.5's own shape rule, so the
  description's own first two groups are tried first and a column the
  earlier rule already answered is answered the same way, byte for
  byte. **This search can be asked for MORE than its first answer**
  (G9.3 step 5, plan amendment A-P3-12), because a description can have
  several exact packings and the first can be one no fold collision can
  be built inside. The further answers are this same walk continued in
  this same order, and then this same walk again with ONE group held to
  ONE family — which is a narrowing of the permissions handed to the
  packer, never a change to the packer's own fill order, so the first
  answer stays the first answer and the rule four roles share is
  untouched. **THE WALK ENDS IN A STATED NUMBER OF STEPS, AND THE
  NUMBER IS COUNTED IN QUESTIONS ANSWERED** (plan amendment A-P3-17
  clause 2): the second half of it walks a candidate end-carrier pair, a
  group and a family, and hands the packer a permission vector that
  depends on the end-carriers only through the two places carrying them,
  so the same question recurs many times over. A question is put to the
  packer ONCE and remembered, at most a stated number of DIFFERENT
  questions are put at all, and at most a second stated number of
  positions are looked at, so a walk that only ever re-asks still ends.
  Where either number is reached the column keeps the layout it already
  had and the shortfall is measured off the finished cells and named.
  **A named layout the first answer leaves short is a reason to look
  further too** (plan P4-D163): a candidate meeting every count and every
  collision the first one met is returned at once only where every named
  layout holds its published count; otherwise the walk goes on, with no
  collision ask, at most sixteen questions and at most six further
  layouts built, taking only a candidate that misses exactly the counts
  the first one missed and reaches for no sign the first one did without,
  and the candidate leaving the fewest named layouts short is kept, the
  first on a tie — so 400 `-10000` beside 400 `20000` no longer packs the end
  pinned to six characters into the figures band;
- **each of the four class families is class-preserving by
  construction, and the walk CHECKS it.** A cell that reads as an
  ordinary number, one holding a well-formed number too large or too
  small to hold, and one whose notation conflicts with itself inside
  accounting parentheses are the constructions of G9.5 step 3 and
  G10.3; a cell of ordinary text is the band's own alphabet walk of
  G9.2, led by a character that holds the value inside its band. A
  candidate the contract's own classifier does not read back as its
  family's class is stepped over, so the class a cell is counted in is
  the class it was packed for. Revision 1 said that when
  `all_whole_numbers` is true every group is written from `DIGITS` and
  `n_all_digits` then equals `n_present`, "as the contract's own
  invariant requires". **The contract has no such invariant and the
  statement is false** (P2-C1-F1): a column of `+1` and `+2` publishes
  `all_whole_numbers: true` with `n_all_digits = 0` AND
  `n_code_alphabet = 0`, because `+` is in neither alphabet, and the
  shipped producer writes exactly that. The false implication is
  withdrawn;
- **which slots carry the fold collisions is settled after the packing,
  not before it** (P2-C5-F2). A partner carries its parent's family
  (G9.3), so a slot that owes a collision and whose class-and-alphabet
  family no earlier slot has can carry none at all. The collision slots
  are therefore chosen rather than taken: each in turn is the LAST group
  whose family can carry a collision — one whose spellings hold a
  character with a case, or any family at all where the published length
  range leaves room for edge spacing — and which still has another
  member among the groups not yet chosen, then the last group whose
  family merely has another member, and otherwise the last remaining
  group, which is the ascending occurrence order this rule replaces.
  Groups keep their relative order otherwise, so a column whose groups
  all share one family is laid out exactly as it was. Nothing published
  moves: the occurrence multiset pairs a size with a made-up value and
  never with a position, and every group keeps its own class, alphabet
  and size wherever it sits. The ask of G9.3 step 1 stays an ASK here as
  everywhere: a family whose spellings hold no character with a case —
  a notation inside accounting parentheses never does — gives the pass
  up after the ceiling G9.2 fixes, the walk is put back where that pass
  began, and the ordinary rule takes the value it would have taken
  anyway. **AND THE CHOICE IS CHECKED ONCE THE SPELLINGS EXIST** (G9.3
  step 5, plan amendment A-P3-12): whether a family can SUPPLY the
  collisions this choice asks it for depends on spellings that do not
  exist while the choice is being made, so a layout that could not
  build one is laid out again — the short family asked for no more than
  it was shown to supply, a slot carrying a published length end
  offered a collision before any other slot of its family, and where
  neither helps, the further exact packings of this section, including
  the ones its own search reaches by holding one group to one family.
  The choice above is offered FIRST and unchanged, so a description it
  answers is answered by it, byte for byte. **AND A LAYOUT REACHED THIS
  WAY IS ACCEPTED ONLY WHERE IT GIVES UP NOTHING THE FIRST LAYOUT HELD,
  RECOUNTED FROM THE FINISHED CELLS** (plan amendment A-P3-17 clause 2).
  A packing meets the four class counts and the three alphabet counts as
  arithmetic over whole groups; whether the family it names holds a
  spelling AT THE LENGTH the slot is pinned to is a separate question,
  and where the answer is none the walk falls back to the band's own
  alphabet and a count met in the arithmetic is missed on the page. So
  the four class counts, both alphabet counts, both published length
  ends and both distinctness counts are recounted off the cells a
  candidate layout wrote, and a candidate missing a count the first
  layout held is refused whatever else it repairs;
- **when `all_whole_numbers` is true, every band writes whole numbers.**
  In the figures band the first character is a non-zero digit wherever
  the spelling is longer than one figure, so the spelling's length is
  its digit count, and **the lone figure `0` is one of the ten
  one-figure spellings** (plan P4-D155): it is a whole number one figure
  long, and refusing it left one figure nine spellings where it has ten,
  so a declared identifier holding 0 to 119 wrote twenty-one
  three-figure cells against a published `{"%%%": 20}` and failed its
  own layout census. **It is the LAST of the ten, after `1` to `9`, and
  where the published lengths run from one figure to two or more the
  walk takes it after every number shorter than the shortest named
  layout of figures alone two or more figures long — or after every
  published length where none is named** (plan P4-D162): taken first, a
  column of `1` to `800` came back holding `0` and one two-figure number
  fewer, and taken late it is written only where the column holds more
  short numbers than the numbers from `1` supply. In the code band the value is
  written `<digits>e0`, which reads back as a whole number and holds a
  character the figures do not. Outside the code alphabet it is written
  `<digits>.`, which reads back as a whole number and holds a character
  the code alphabet does not. **Where the published length range leaves
  a value that must stand outside the figures no whole-number spelling
  at ANY length — one character cannot be both a whole number and
  outside the figures — the facts cannot all hold and G12 refuses
  generation before any cell is built** (review item P2-C5-F4);
- **each cell is written to its PUBLISHED LAYOUT where the column
  publishes one** (contract 7.12, landing 2b.18, plan P4-D120). The
  census of layouts says what KIND of character stood at each position
  of a record number, and until this rule existed the construction
  above did not read it: a column of UUIDs published its layout and its
  twin still wrote `A----------------------------------J`, matching 0
  of its own 800 rows while both files passed their own description at
  exit 0. The rule is this. The census counts CELLS and this walk
  spends GROUPS, and every cell of a group carries the same spelling,
  so taking a layout lowers that layout's remaining count by the whole
  group. **Before any cell is spelled, the census is SPREAD over the
  identities by the smooth weighted rotation** that spends a datetime
  column's separator census (plan P4-D39). The identities are visited
  with the ones carrying a published length END first, then by the
  number of cells they cover, LARGEST FIRST, then in walk order. Each
  visit considers the layouts that still have at least as many cells
  left as the group covers, whose length the group's own window holds,
  and which the group's class and band can wear at all -- read off the
  layout's own first 64 fillings (or all of them where it has fewer)
  with every guard below but freeness. Every layout the group's family
  can wear has its published count times the group's size added to
  that family's running credit, the candidate with the most credit is
  preferred -- the first in sorted order on a tie -- and the
  family's total times the group's size is taken back from it. Credit
  is kept per family (class and band), so a layout one family cannot
  wear is never poured into another. LARGEST FIRST is what keeps the
  census payable: a group covering three cells needs a layout with
  three left, and the singletons visited last can pay whatever a
  larger group left behind. The walk then offers each group its
  preferred layout first and every other published layout in sorted
  order after it, each only where its remaining count covers the group
  and its length fits the slot, and at most 4,096 fillings of one
  layout are read for one offer. **A GROUP THE OFFER CANNOT SERVE IS
  OFFERED A MIX OF THE COLUMN'S OWN KINDS** (plan P4-D128) -- a pooled
  cell, a cell of a layout too few to name, a cell of a layout the
  census took back. The KINDS are the placeholders `%`, `@` and `&` the
  named layouts use between them, in that order; with fewer than two,
  or on a census carrying a hexadecimal mark, nothing is mixed. The
  BASES are the named layouts holding no `!`, in sorted order, each read
  only where the group's window holds its length. The `j`-th MIX of a
  base puts one kind in each of its figure and letter places, read off
  `j` spread over the number of mixes (the kinds' count to the power of
  the places) by the stepping below and taken apart leftmost first; its
  marks and spaces are the base's own. Sixteen mixes are read in all for
  one group, each base's `j` counted on from where that base's reading
  stopped: a mix the census NAMES is stepped over, because its cell would
  be counted into a published layout the column owes exactly; a mix no
  slot of this class and band can wear, by the 64-filling test above, is
  stepped over; and the first mix with a free filling that passes every
  guard below is taken. Only a group no mix serves keeps the walk above,
  unchanged, so a column publishing no layout is written exactly as it
  was, byte for byte. **Why, measured:** 800 random eight-character codes
  of capitals and figures at a floor of eleven pooled 448 cells, the
  walk wrote them `A-----2S`, and `[A-Z0-9]{8}` matched 800 real cells
  and 352 twin cells; with the mixes it matches 800 of 800. **Why the spread, measured:** the
  walk reaches the values written once before the values written more
  often, and taking the first layout with room left gave a two-system
  key -- `REC` and seven figures beside `E` and six, 800 rows,
  identities recurring one to three times -- a one-letter layout of
  217 singletons and nothing else against the real column's 71
  singletons, 34 doubles and 26 triples; with the rotation it is 67,
  27 and 32, so code counting visits per record system meets both
  systems recurring.
  **A layout is filled from a COUNTER and never from a reading**, by
  the mixed-radix arithmetic of G8.3's own form fill, leftmost first,
  so consecutive spellings differ in their leading characters rather
  than their trailing ones — which is what stops a column of record
  numbers coming out as the near-consecutive walk `10000020`,
  `10000021`, … that landing 2b.18 measured. **The step is spread
  around the layout's room by a stride coprime to it, the exact golden
  section of the room in whole numbers** — `(isqrt(5 * room * room) -
  room) // 2`, walked up to the first value sharing no factor with the
  room (plan P4-D128). G8.3's stride is the room times 61803 over
  100000, which on a room that is a power of ten ends in noughts, and
  the fill reads the low figures of the product first: measured on 800
  thirteen-figure codes, 44.8 per cent of the twin's figures were
  noughts against 11.4 per cent of the table's; a section taken to
  sixty-four bits does the same on a hexadecimal room, 57 per cent on
  800 UUIDs. **Each layout's walk starts at its own step**: the k-th
  named layout in sorted order at `1 + k * 4096`, and a mix, when first
  read, at `1 + m * 4096` where `m` counts the walks already started.
  Not at nought, which is the all-nought, all-`A` filling; and not all
  at one step, because a filling's trailing characters follow the step
  whatever the room, so two layouts walked from one step end alike. **AND A CELL IS WRITTEN
  TO A LAYOUT ONLY WHERE IT RECOUNTS INTO THAT LAYOUT**, asked of the
  census's own reader: `%%%%` filled at a step whose leading figure is
  nought spells `0123`, whose layout is `!%%%` and not `%%%%`, so such
  a filling is stepped over rather than written. Without that guard a
  column publishing `!%%%%%%%` 480 and `%%%%` 320 wrote 33 four-figure
  cells with a leading nought — a zero-filled spelling its source never
  wrote. The length ends need no separate rule: a layout is one mark
  per character, so the shortest cell's layout is `min_length` marks
  long and the longest cell's is `max_length`, and the slot pinned to
  an end has a layout of exactly its length to take. **The four class
  counts and the two alphabet counts are kept across this rule and not
  traded for it**: a candidate the shipped classifier does not read
  back as its slot's class, or the shipped alphabet readers do not
  recount into its slot's band, a candidate that reads as a date
  under `parsing.DATE_FORMATS`, and a candidate a reader reads as absent
  -- G10.3's list, the column's own published hole spellings and every
  spelling the document declares absent (plan P4-D158) -- is stepped
  over. **A LAYOUT WHOSE LEADING MARK OPENS A FORMULA IS GIVEN UP AT
  ONCE, SAVE ONE**: a sign, `-` or `+`, followed by figures with at most
  one point among them (plan P4-D156). Such a layout is worn by signed
  numbers alone, so a census publishing it PROVES the table held them,
  which is owner decision 9's own distinction: the twin inherits the
  hazard rather than manufacturing it, and the cells are counted in the
  report's formula paragraph. Refusing it wrote `000020e0` for 800
  cells of `-1000000` upward, 0 of 800 kept the layout, and nothing
  named it. A signed layout is not given to an identity owed a
  fold-collision partner, in the rotation or in the offer, because that
  partner can only be edge-spaced and would open with the sign too. **`!` IS THE ONE
  PLACE A MADE-UP WHOLE NUMBER MAY OPEN WITH A NOUGHT**, and it is the
  zero fill of NC-9 — the `%08d` a reader loses when a spreadsheet or
  a statistics package reads `01586982` as 1586982. Every `!` is
  written a nought, and a filling whose next figure is also a nought is
  stepped over by the recount guard, because that cell is one nought
  deeper (plan P4-D126). The mark stands only where the whole cell is
  figures, so it can name no text anybody chose. **A LITERAL RUN IS
  WRITTEN BACK ONLY AS A PUBLISHED PREFIX** — a record prefix, or `ABC-`
  in front of a study number — by the owner's ruling of 2026-09-17, item
  1, which settled clause 3 for that case and amended contract invariants
  I3 and F3 for it alone; G9.6a states how. Any other literal run is a
  fragment the description does not carry, and the twin writes the
  layout's own alphabet in its place;
- **a fold-collision partner wears the layout its identity reserved**
  (plan P4-D157). A partner is its parent's spelling with a case turned
  over or an edge space added (G9.3), so a case flip wears a layout --
  `g0000` beside `G0000` is `&%%%%` -- and an edge space wears none.
  Before the rotation, each partner slot is handed, as G9.3 hands
  partners out, to the first identity of its own family counted on
  cyclically from the slot's ordinal among the partners. The layouts a
  cell of layout `L` hands its partners are read off `L`'s first filling:
  its partner family in G9.3's order, at most 64 members, inside the
  published length range, and the members wearing a NAMED layout taken
  one per partner in that order, a partner past them wearing none. Where
  any partner of any named layout wears a named layout, the rotation
  visits the identities owed partners after the two end carriers and
  before every other identity, and a layout is a candidate for such an
  identity only where its own remaining count covers the identity and
  every named layout its partners wear has their cells left, the layout
  itself counting both where they coincide; all of them are debited
  together. **A partner wearing no named layout is debited too** (plan
  P4-D196), from the present cells the census names no layout for, so an
  identity is not given a layout whose partner can wear none where no such
  cell is left: 300 record numbers `S1000` upward, a tenth of them written
  again in lower case, beside `S-12-A`, published every cell under a named
  layout, and two partners turned `S-12-A` into `s-12-A` and left `@%%%%`
  two short at every seed. The walk debits an identity's partners off the layout it
  actually took, remembered by partner; at a partner slot that debit is
  given back and the member taken is the first unwritten one wearing a
  named layout with the partner's cells left, else the first wearing no
  named layout, else the first, and its layout is debited. Measured
  before this rule: `G` and four figures on 600 rows beside `g` and four
  on 200 published `{"@%%%%": 600, "&%%%%": 200}` and the twin wrote 500
  and 300; `AB` beside `ab` wrote the partners `aB`. **And every named
  layout is RECOUNTED into the twin's own report**, off the present
  cells by the census's own per-layout rules and against the window the
  pool leaves, so a layout the twin does not hold is named: before this
  recount a signed column wrote 0 of 800 cells to its layout, and a
  battery of 800 small mixed columns missed a layout on 488 runs, and
  the report named none of them;
- **a named layout the first answer leaves short is PACKED with the
  families** (plan P4-D182). The class-and-alphabet packing settles each
  group's class and band before any layout is offered, and a layout is a
  fact about a cell's length, class and band at once, so that packing can
  put a group where no layout it owes can be worn: a declared column of
  49 rows publishing `{"%%%": 12, "&-&": 8, "@_%": 10, "@_%%": 3}` wrote
  `&-&` and `@_%%` nought times on every seed while its own values meet
  every count. So where the first answer meets every count and every
  collision and leaves a named layout short, and NO group owes a
  fold-collision partner, the census is packed as a THIRD MARGIN of the
  same grid by the same allocator and fill order: a cell is a class, a
  band and either one named layout or none, the named layouts' quotas are
  their published counts in sorted order and the last quota is the
  present cells the census names no layout for. A group may take a named
  layout only where it covers no more cells than that layout counts, the
  layout's length is one its window holds -- exactly the end it carries,
  where it carries one -- and a slot of that class and band can wear it by
  the 64-filling test above; "none" is open to every class and band the
  group may stand in. The grid is packed FIRST WITH NO END PINNED, the
  sign family closed and then open, and the two groups carrying the
  published ends are read off the answer: the first group, in group
  order, that can be written at the shortest length -- packed to a named
  layout of that length, or packed to none in a class and band holding a
  spelling that long -- and the first OTHER group that can be written at
  the longest, or the first two groups where the two lengths are one. Only
  where that finds no answer, or no such pair, are the ends pinned shape
  by shape in the order of the first tier of the search above (measured:
  on 760 rows whose first groups are singletons, pinning first asked
  sixteen questions with no answer and took eighty seconds; unpinned, the
  column takes under one). At most sixteen different questions are asked
  and at most four layouts built, and each group is then offered
  its packed layout ALONE, a group packed to none being offered no named
  layout at all. A layout built this way is kept only where it builds
  every collision, files no more notes than the first answer, recounts
  missed exactly the counts the first answer missed, reaches for no sign
  the first answer did without -- save where a named layout is a sign in
  front of a number, which proves the table held sign-leading cells (plan
  P4-D196, as P4-D156 reads that proof): 200 record numbers `P###` beside
  `+###` and `-##` published `{"+%%%": 38, "@%%%": 121}`, only the sign
  family open packed it, and the twin wrote 37 -- and leaves fewer named
  layouts short;
  one leaving none is returned at once, before the wider search. **What
  it does not reach, measured on the battery of 800 small mixed columns,
  where it names a layout short on 200 runs against 376 before:** a
  column owing a partner, whose layout its parent's spelling decides; a
  column whose made-up cells, all of whose letters are `a` to `f` and
  trade places with figures, read as HEXADECIMAL where the census is
  plain, or the reverse; a layout opening with a character a spreadsheet
  reads as a formula that no proven sign covers; and a group packed to no
  named layout whose family writes a named one anyway. Every one of them
  is recounted and named;
- no word statistics exist, so G9.5 step 6 does not apply and no space
  is ever written into an identifier.

**What the length ends and the bands cost, and how both were settled**
(review items P2-C5-F4 and P2-C5-F2; closed by Phase 3 plan P3-D8.1,
owner decision 1, 2026-08-12). A whole number standing outside the
figures needs two characters in the wide band and three in the code
band, so once `all_whole_numbers` is true a band's permitted LENGTHS
are part of the question. The first bullet above settles length and
band together, which closed the shape a length end pinned onto a group
whose band has no whole-number spelling at that one length used to
leave — a source of `1.`, `2e0` and `3` is its own proof that an answer
exists, and the packing finds it.

The other shape was a published longest length of two characters
carrying a value that must stand in the code alphabet. Its only
two-character whole numbers begin with a sign, which G9.1 keeps a
made-up value from beginning with, and the implementation wrote one
anyway — meeting the count by breaking the bar, and leaving the
report's formula paragraph telling the reader that an invented cell was
a value the description published.

**The owner settled it as a bounded carve-out, not a refusal** (owner
decision 9, 2026-08-13). A description carrying those counts PROVES the
real column held sign-leading values, since no other spelling of that
width exists, so the twin inherits a hazard the table already had
rather than manufacturing one — which is the distinction G9.1's bar was
written to draw. Refusing instead would deny a person a twin over a
character their own file used. The family is written where it is
needed, and the report's formula paragraph names those columns, says
the cells were invented, and says why.

**"Where it is needed" is decided by the packing and by nothing else.**
The class-and-alphabet search above runs first with the two-character
code family CLOSED, and reaches for it only when no assignment of whole
groups meets every published count without it — so a column with room
for three characters writes `1e0` and no sign at all.
`all_whole_numbers` stays EXACT-OBSERVABLE in every case this method
builds, and an invented record number opens with such a character only
where the published counts leave no other way to spell a value of that
width for its own group.

**The COUNT of such cells is not minimal, and this document said
otherwise until now** (Phase 3 plan P3-C7-F1 and its amendment A-P3-8
clause 4, 2026-08-14). A fold-collision PARTNER carries its parent's
spelling, and `_partner_of` searches only the family the packing
already gave the slot, so it cannot move a collision to a family where
it would cost nothing: the plan's measured column — `-3` twelve times,
`-34023` twice, `8e999` three times and `8E999` twice — writes fourteen
such cells where an allocation putting the collision on the
out-of-range pair would write two. Every published count is met either
way, so what is missing is a MINIMISATION rather than an obligation;
the plan records the three passes that designed it, measured it and did
not take it, and the generation report says the same thing to the
person holding the twin. An independent implementer is bound by the
counts, not by this shortfall: writing fewer such cells while meeting
every published count conforms.

**A RECORD NUMBER IS BUILT AGAINST A READING OF ITS ABSORBED COUNTS
WHERE THE PUBLISHED ONES HAVE NO ANSWER** (plan P4-D298). On a declared
record number the four class counts are published under invariant X2 —
a part below max(2, `small_cell_floor`) counted into the largest — and
the two alphabet counts as G9.5 says, so fifteen `-463`, eight `-4`, one
`bLMQsN` and one `5e999` publish `n_numeric 25` and nothing else beside
`all_whole_numbers: false`, which twenty-five whole numbers cannot hold.
So the column is built first against the published counts, and where
those cells miss a count as published — the four classes read through
X2, the two alphabets through the disclosure rule, and
`all_whole_numbers` — the readings are built in order, each only where a
packing of whole groups meets it, at most eight of them:

1. every partition of `n_present` that X2 publishes as the published
   one (the published largest part gives up what the others take, each
   of which may measure anything below the line), with
2. every pair of alphabet counts G9.5's reading offers,

in ascending order of the six counts' differences summed, ties by the
partition's own difference, then the partition, then the pair, each
ascending. **A READING WHOLE GROUPS CANNOT MEET IS NOT OFFERED** (item 2
of the numbers pass of the second Codex round, 2026-09-19): every count
of a reading is filled by whole repetition groups, so a reading is
passed over at once where any of its four class counts, or any of its
three alphabet bands -- the cells in figures alone, the rest of the code
alphabet, and the cells outside both -- is a total no choice of whole
groups adds up to. The first 256 readings that survive that sift are
offered and no more, at most 131,072 are looked at, and of those offered
at most eight are built. MEASURED at a floor of eleven, seed 4, on a
declared record number holding `12` on 230 rows and `Z` on ten, whose
counts absorb to `n_numeric 240`, `n_all_digits 240`, `n_code_alphabet
240` and `all_whole_numbers: false`: 87,845 readings exist and exactly
FOUR of them any packing can meet, the unsifted first 256 held one of
those four, the reading the column's own values make stood at position
17,773, and the twin came back `16` on 230 rows and `0` on ten -- every
cell a whole number against a description that says not every value is
one, `validate` exiting 3 on the twin and 0 on the real table, and
`pandas` reading the source as text and that twin as whole numbers. The
sift leaves eleven readings of the 87,845, at a cost of 0.01 seconds
against the 46 seconds packing all of them would take. A shortfall this
search leaves is reported as a search that found no way and NOT as a
proof that none exists. The first reading whose cells hold every count as published,
file no more deviations, miss no other count the published build held
and leave no more named layouts short is the column; where none does,
the published build stands and every miss is named. **Measured** at
e53d5f4 on the battery of review item P2-C5-F2: six of 200 producer
columns missed a class count, an alphabet count or the whole-number fact
on every seed, and none does with this rule.

### G9.6a The literal prefix (owner ruling of 2026-09-17, item 1)

Contract section 7.12a publishes `layout_prefixes`: `(column)` mapped to
the text every present cell opens with, or each named layout mapped to
the text its own cells open with (plan P4-D202). Before the ruling the
twin of `REC1234567` was `FPQ7317879`: measured at 800 rows, `^REC\d{7}$`
matched 800 real cells and 0 twin cells, and `^P\d{5}$` 800 and 30.

1. **A prefixed layout is written as its TEMPLATE.** The template is the
   layout with its opening marks replaced by the prefix — `@@@%%%%%%%`
   under `REC` is `REC%%%%%%%`; under `(column)` every named layout takes
   the column's prefix. Every walk of G9.6 above reads the template in
   place of the layout: the fill leaves every character that is not a
   placeholder standing, so the prefix stands where every real cell
   holds it and only the placeholders after it are filled; the room of a
   template is the room of its placeholders, which is what keeps the
   made-up values different; the rotation, the offer, the packing and
   the partner layouts spread the census over the templates exactly as
   they spread the layouts. Templates are offered in sorted order, as
   layouts are.
2. **A cell is counted into a template only where it wears it**: its own
   layout, read by the census's reader, is the template's layout read
   under the COLUMN'S OWN CONVENTION — every letter marked by its case in
   a plain column, by the column's hexadecimal mark in a hexadecimal one
   (`parsing.prefix_layout`, plan P4-D233) — and every letter of the
   template stands in the cell at its place. On a template holding no
   letter this is the layout test and nothing more, so a column
   publishing no prefix is written byte for byte as before. A
   hexadecimal template is `DE-~~~~~~` under the prefix `DE-`, and its
   layout is `~~-~~~~~~`.
3. **The mixes are made over templates**, whose letters are not kinds,
   and a mix whose own layout is a named one is stepped over, prefix or
   no prefix.
4. **A cell of the band walk (G9.2) owes a prefix** where the column
   publishes one for the whole column, or for the layout the walk's cell
   wears. Its opening is overwritten with the prefix, and the result is
   taken only where it is unwritten, reads as the slot's class and band,
   is no spelling read as absent and no date, and wears no named layout
   the walk's cell did not; otherwise the walk's cell stands.
5. **A fold-collision partner not opening with a prefix it owes** is
   taken only where no member of its family does: a case flip of
   `REC1234567` is `rEC1234567`, and the edge-spaced `REC1234567 ` is
   taken before it.
6. **And a PARENT whose partner wears a named layout is asked before
   one whose partner wears none** (plan P4-D230). G9.3 step 4 hands the
   partners out in ascending identity order and walks the parents of the
   asking slot's own family in its cyclic order, taking the first that
   supplies a partner at all; the member preference of G9.3 step 2
   chooses inside ONE parent's family. That order was fixed where every
   parent of a family could supply a partner of any layout the census
   names, and a published prefix narrows it: every cell of a prefixed
   layout opens with the same characters, so one parent's family reaches
   one layout and no other. On a column publishing a prefix the ask is
   therefore offered to every parent of the family FIRST, with the step 2
   preference held to a named layout that has cells left, and only then
   walked again as G9.3 step 4 walks it. The two walks are the same walk
   in the same order, so a column publishing no prefix asks nothing new
   and writes the bytes it wrote. MEASURED: 300 record numbers `S1000`,
   a tenth of them written again in lower case, beside `S-12-A`,
   publishing `{"%%%%%": 28, "&%%%%": 26, "@%%%%": 214, "@-%%-@": 32}`
   and a prefix for each of the three lettered layouts -- the first
   parent of each partner's family was a hyphenated one, whose flip
   `s-12-A` wears a layout the census names no cell for, so the twin
   wrote 20 of those, `&%%%%` came back 7 of 26 and `validate` exited 3
   naming both misses; with this step the twin writes the census exactly
   at seeds 1 and 4.

The cells a prefix governs are recounted beside the layout census, and
the report names a prefix some such cell does not open with. **What this
does not reach**, measured: pooled cells the band walk writes keep its
shapes, so 790 `P` and five figures beside ten `P` and six at a floor of
eleven write all 800 twin cells opening with `P` while `^P\d{5,6}$`
matches 790; and a partner pinned to a length only a case flip reaches
writes one flipped prefix, which the report names. Frozen cases
`identifier_column_prefix` and `identifier_layout_prefixes` pin steps 1
and 2; the oracle states steps 3 to 6 from this text and no frozen case
reaches them, neither publishing a folded count below its raw one.

In the infeasible corner of owner decision 6 the identifier repeats:
the groups are filled from the domain in order and, when it is
exhausted, the enumeration restarts, so the fewest necessary values
repeat. Three distinctness facts are then REPORT-ONLY, not one — raw
`n_distinct`, `n_distinct_folded` AND `n_distinct_by_occurrences` — and
the report names all three achieved values beside the published ones,
with the join and de-duplication consequence in the person's own words.

## G10. Absent cells, straggler stand-ins, unrepresentable values

### G10.1 Absent cells

Exactly `n_missing` cells per column, placed by the arrangement of
G4.2. Each published `missing_by_source` spelling is written at exactly
its published count, character for character — a spelling a judged
pass put there included — and every other absent cell — the blank
count and the withheld remainder — is written as the EMPTY text
(contract C6-115 and C6-116, plans P4-D6.1 and P4-D6.4).
`missing_by_class` is REPORT-ONLY.

**A JUDGED PASS'S KEY WAS WRITTEN EMPTY UNTIL PLAN P4-D6.4.** The
stand-in number and calendar placeholder passes decide absence by an
outlier-and-share rule over the real column's values, and this
paragraph kept their cells blank so that a twin's own values would not
have to fire that rule again. The owner's ruling of 2026-09-15 has the
twin write everything as the source wrote it, and a blank where the
table wrote `-999` turned pandas' reading of a whole-number column from
`int64` to `float64`. The validator now reads a candidate the
description judged missing as absent in that column without asking the
rule again, so the cells are written back and read back the
same way on every run.

**THIS PARAGRAPH SAID THE OPPOSITE UNTIL LANDING 2b.8, AND THE CODE
HAD BEEN RIGHT FOR A VERSION.** It read "each written as the EMPTY
text — no space, no marker, no spelling of any kind", citing residual
R-P2-2, which plan P4-D6.1 closed when version 6 began reproducing the
spellings. A method sentence that describes a rule the product retired
is a defect of this document, so it is corrected here rather than
footnoted.

**A SPELLING OF NOTHING BUT SPACE IS WRITTEN LIKE ANY OTHER** (plan
P4-D74, contract C6-125). One space, two spaces, a tab and a no-break
space are keys of that map since C6-125, and the twin writes each at
its count. No construction can collide with one: every walk that
INVENTS a spelling refuses anything the reader's own vocabulary calls
absent, and the empty spelling is a member of it, so a whitespace-only
candidate is refused before it is claimed (G9.4, G10.4). An empty cell
re-profiles as `(blank)`, which is what makes `n_present` and
`n_missing` EXACT-OBSERVABLE.

The one-column canonical quoting exception of G2 applies here.

### G10.2 The class partition

Every present cell of every role belongs to exactly one of four classes,
and the four counts are published on every role:

```
n_numeric + n_out_of_range + n_contradictory + n_not_numeric = n_present
```

They are EXACT-OBSERVABLE **by class-preserving construction**: each
class has its own construction below, each construction's output
classifies back into its own class through the shipped
`parsing.classify_number`, and a test asserts exactly that over every
constructed spelling.

**The label roles construct their classes too** (landing 2b.4). Their
published spellings carry their own classes, and the held-back levels
pay what is left of the three numeric counts by G8.3a. Until that
section existed every held-back level was written as a word, so this
partition was held on every role but the four that most often hold
numbers beside words, and a twin's own validation said so.

### G10.3 The three straggler constructions

Distinctness inside a class is supplied by advancing `k` from 1; the
budget allocation of G6.5 says how many different spellings each class
may use, and a class that has spent its budget repeats its last
spelling.

- **Out of range (`n_out_of_range`).** A well-formed number too large or
  too small for binary64. Too large, spelling `k`: `1e999`, `2e999`,
  `3e999`, … (`ke999`, with `k` written in base ten). Too small,
  spelling `k`: `1e-999`, `2e-999`, …. A negative one carries a leading
  `-`. The published `n_negative_unrepresentable` says how many of these
  are negative; on the numeric roles the too-large/too-small split is
  not published for this class and every out-of-range cell is written
  too LARGE, which the report names.
- **Contradictory (`n_contradictory`).** A sign inside accounting
  parentheses, which is numeric notation whose meaning conflicts with
  itself: `(-1)`, `(-2)`, `(-3)`, … for spelling `k`. These carry
  neither sign nor whole-number status — the shipped parser answers
  "unknown" for both, and never guesses — so they can answer only for
  `n_sign_unknown` and `n_whole_unknown` wherever those are published.
  They are not the only class that can: a cell of ordinary text is left
  unsettled by the same parser in the same way, so the two together are
  what those counts are made of, and G10.5 step 1 states that tie for
  the one role that publishes them.
- **Ordinary text (`n_not_numeric`).** `text-1`, `text-2`, `text-3`, …
  for spelling `k`. Each is checked against the spellings that mean "no
  value" (`""`, `-`, `--`, `.`, `?`, `n/a`, `na`, `nan`, `none`,
  `null`, compared after trimming and case folding) and against every
  spelling already used in the column, and `k` is advanced on a
  collision. It parses as no number and as no date, so it stays in its
  own class.

**The interaction with the numeric-sentinel rule, stated rather than
left to chance.** The profiler reads `-9999`, `-999` and `9999` as
"no value" when they are also distribution outliers and cover at least
`sentinel_minimum_share` of the column. A twin cell that lands on one of
those numbers can therefore be read as missing when the twin is
re-profiled, exactly as the real column's own cells were. The method
does not steer values away from those three numbers — doing so would
distort a distribution to protect a re-profiling artifact — and the
report names `sentinel_verdicts` as REPORT-ONLY. This is a residual, not
a defect, and it is named as one in G13.

**The one construction that DOES step past them is G8.3a's**: a
held-back number of a column of labels is chosen from a walk rather
than placed on a distribution, so refusing `-9999`, `-999` and `9999`
there costs a step of the walk and moves no published fact.

### G10.4 Unparsed datetime stand-ins

`n_unparsed` is EXACT-OBSERVABLE as counted neutral stand-ins,
explicitly outside the parsed-value obligation. The spellings are
`text-1`, `text-2`, … from the same construction as G10.3, checked
additionally against every date format the shipped `parsing.DATE_FORMATS`
names so that a stand-in cannot accidentally parse as a date and change
`n_unparsed`.

### G10.5 The `numeric_unrepresentable` role

The column publishes `n_whole`, `n_fraction`, `n_whole_unknown`,
`n_positive`, `n_negative`, `n_sign_unknown`, `n_out_of_range`,
`n_distinct_by_occurrences` and — since revision 4 — the two widths
`min_length` and `max_length`, the character counts of the narrowest
and the widest value the real column holds. It publishes no magnitude
fact of any other kind.

**REVISION 4 RETIRES THE CANONICAL INVENTED WIDTH** (residual R-P2-1,
closed). Revisions 1 to 3 published no width at all for this role and
wrote every such column at one invented width of 400 significant
digits, the same for every column and disclosed in the report as
invented. That was measurably wrong for the product's one job: two
columns of overflowing values, one about 400 characters wide and one
about 4,000, described identically, and a twin built from either
description held cells of a width neither table had. Code that measures
how wide the written values are — a column width, a fixed-width read, a
check on the length of a field — reads a different answer on the twin
from the one it reads on the real table, and nothing in the description
let the generator do better.

**REVISION 5 GIVES THE WIDE-VALUE WALK A SECOND SPELLING FAMILY**
(residuals R-P4-48 and R-P4-68, both closed). Revision 4 published the
two widths and then could not write them on a column spelled compactly,
because the only spelling either out-of-range shape had was a digit
string and a digit string cannot say `1e400` in five characters. The
family, its floors, its capacity and its recount are the clauses marked
revision 5 below.

**The two published widths are the width window, and both ends are
carried where the column's own shapes can carry them.** The rule has
three parts and they apply in this order.

* **Every group is asked for a width.** By default a group is asked for
  `max_length`. One group is asked for `min_length` instead: the FIRST
  group, in the packing order of step 3, whose shape can be written at
  that width. Choosing the floor carrier by shape rather than by
  position matters — a column whose one narrow-capable group comes
  first would otherwise carry no floor at all. A column of a single
  group, or one whose two published widths are equal, asks every group
  for `max_length` and there is nothing to choose.
* **A shape may have a floor of its own, and the floor wins.** A whole
  number is out of binary64's range only past about 1.8e308, and a
  fraction is below its smallest subnormal only past about 5e-324, so
  a value narrow enough for the format to hold is a value of a
  different kind from the one the description publishes. The shape's
  floor therefore takes precedence over the asked width and the report
  names the widening in those words. **What that floor IS depends on
  the spelling family, and revision 5 is the clause that says so:**
  spelled as a digit string the too-large shape needs **310
  characters** of room and the too-small shape **327** (a leading
  `0.` and 325 decimal places); spelled in exponent notation the two
  need **five** and **six**. The floor that binds is the narrower of
  the two, so it is five for the too-large shape and six for the
  too-small one. The other four shapes have no floor: contradictory
  notation, ordinary text and the two in-range shapes are written at
  exactly the width they are asked for.
* **EXPONENT NOTATION IS A SPELLING FAMILY OF ITS OWN, AND IT IS WHAT
  CARRIES A NARROW COLUMN OF WIDE VALUES** (revision 5, closing
  residuals R-P4-48 and R-P4-68). Revision 4 spelled the two
  out-of-range shapes as DIGIT STRINGS and nothing else, so their
  floors above were the narrowest cell either could be written at at
  all — and a real column whose cells are `1e400`, `-1e400`, `2e400`,
  five and six characters, publishing `min_length` 5 and `max_length`
  6 exactly right, got a twin of 310- and 311-character numerals.
  Somebody who develops `len(x) == 5`, a fixed-width read or a slice
  against that twin meets a value sixty times wider than anything
  their real column held.

  A value too large or too small for the format has a second spelling:
  a mantissa, the letter `e`, and a signed exponent. Both families
  write the same two shapes and answer for the same published counts —
  the table of step 1 is untouched, because what a cell answers for is
  what the shipped parser says of it and the parser says the same of
  both. What separates the families is the width each can be written
  at and how many distinct values each supplies there.

  **Which family writes a group is settled by the ASKED WIDTH and then
  by capacity, in that order.** The digit-string family is asked
  first, and it writes the group where the asked width is at or above
  ITS OWN floor and the spelling it would write lands at exactly that
  width. Where it cannot — the asked width is below its floor, or the
  candidate it would write is wider than the width asked for, or its
  spellings at that width are already spent — the exponent family
  writes instead. Asking the digit-string family first is what keeps
  every column revision 4 wrote byte-identical: at 310 characters and
  above nothing moves.

  **THE EXPONENT FAMILY'S SPELLINGS ARE ONE CONSTRUCTION FOR BOTH
  SHAPES.** A cell of this family is the value's sign, a mantissa of
  decimal figures, the letter `e`, and a THREE-FIGURE exponent, which
  carries a minus for the too-small shape. The exponent field is
  therefore four characters wide for the too-large shape and five for
  the too-small one, whatever exponent it holds, and the mantissa
  fills whatever that field leaves of the asked width. **What
  separates one spelling from the next is the mantissa read as a
  number** — 1, 2, 3 and so on — written at the right of that room
  behind a run of leading zeros. That is step 4's own rule (the zeros
  are the width and the figures are the difference) applied to this
  family, and it is why a group asked for a width writes exactly that
  width. So at a room of five the too-large shape writes `1e400`
  through `9e400`, and at a room of 327 the too-small shape writes
  `0…01e-400`, `0…02e-400` and onward, which is the family a real
  column reaches twenty-five distinct values with where the
  digit-string family reaches nine.

  **THE MANTISSA IS SPENT BEFORE THE EXPONENT MOVES, AND THE EXPONENT
  MOVES.** When the mantissas at one exponent are gone the exponent
  steps OUTWARD from 400 — up to 999, then down from 399 — and the
  mantissa starts again. Both move, so the family's capacity at a
  width is the SHAPE's own count of spellings there rather than one
  exponent's.

  **That is a repair of the first build of this family and the
  measurement is the reason it is written here rather than left as a
  detail.** With the exponent fixed at 400 the family had nine
  spellings at five characters, and a real column has thousands
  (`1e309` through `9e999`). A 160-row column of sixteen distinct
  five-character values then made `synthtwin generate` REFUSE — the
  domain-too-small refusal of G9.4 — on a description the profiler had
  just written from a real table, where the same column before this
  family existed generated at 310 characters with both widths missed.
  A repair that met the width had turned a reported miss into a stopped
  command; **a repair can move a hazard, and a capacity rule is where
  this one moved to.**

  400 is where the walk STARTS and not a bound: it is deep inside both
  shapes' ranges at every width this method writes, and starting there
  is what lets two implementations agree on the first cell rather than
  on a search.

  **AND EACH CANDIDATE IS ASKED THE QUESTION rather than trusted to
  the constant.** A spelling of this family is written only where the
  shipped parser reads it back as out of range AND settles it as the
  shape's own whole-number status — the same two questions step 6's
  recount asks of the finished cell. Where a candidate fails either,
  it is STEPPED PAST and the walk carries on to the next. That is the
  rule the too-small shape's zero run already follows, and the only
  form two implementations can agree on without sharing a number.

  **A REFUSED CANDIDATE IS NOT THE END OF THE WALK, and revision 5
  read it as one.** Inside one exponent the mantissa ascends, so the
  candidates the question turns down are contiguous at one END of that
  exponent — a SUFFIX for the too-small shape, whose values grow past
  the smallest subnormal as the mantissa grows, and a PREFIX for the
  too-large one, whose values grow past the largest holdable number
  the same way. Stopping at the first refusal is therefore right for
  one shape and wrong for the other, which is exactly what happened:
  at five characters `1e308` is a number this format holds while
  `2e308` through `9e308` are not, so the walk stopped one spelling
  short of eight it could have written.

  **WHAT ENDS THE WALK IS ONE WHOLE EXPONENT TURNED DOWN.** The
  exponent steps outward from 400 and then inward from 399, so it
  moves monotonically away from the shape after it leaves 999; an
  exponent every one of whose mantissas is refused is therefore an
  exponent past which nothing is ever accepted again, and the family
  is spent at that width. This is a rule of the SHAPE and not a step
  budget: no number is written down for it, it cannot stop a family
  that still holds a spelling, and it BOUNDS the walk, which "step
  past it and carry on" does not.

  Measured at each shape's narrowest width, and the two shapes end
  DIFFERENTLY:

  * the too-large shape ends INSIDE an exponent and past a refusal.
    Every mantissa at an exponent of 309 or more overflows and so does
    every mantissa but the first at 308, so the first refused spelling
    is `1e308`, the eight after it are written, and the capacity at
    five characters is **6,227** — nine mantissas at each of 691
    exponents plus those eight, which is the shape's own count of
    five-character spellings;
  * the too-small shape ends PARTWAY THROUGH an exponent and at its
    first refusal. `1e-324` and `2e-324` are below the smallest
    subnormal and `3e-324` rounds up onto it, so every candidate from
    there on is refused and the capacity at six characters is
    **6,077**, two spellings into its 677th exponent.

  A rule that stopped at the exponent boundary would throw the
  too-small shape's two spellings away; a rule that stopped at the
  first refusal throws the too-large shape's eight away; and a rule
  that ASSUMED a boundary would write a value the format holds into a
  column described as holding none. Asking each candidate, stepping
  past the ones turned down, and giving the family up on a whole
  exponent of them is what gets all three right without any of the
  numbers being written down.

  The mantissa has an edge of its own, measured the same way and far
  further out: a too-small spelling stops underflowing at a mantissa of
  seventy-seven figures, which needs a room of 82 characters. So the
  exponent's edge is the one a column can reach and the mantissa's is
  not.
* **NEITHER FAMILY MAY CLAIM A HOLE SPELLING, and the hole spellings
  this role must avoid are the WHOLE DOCUMENT'S.** A `--missing-value`
  declaration is made once and reaches every column of the table, and
  a spelling any column publishes among its absent cells therefore
  means "no value" wherever it is written. This role is the one that
  cannot learn it from its own block: it publishes no value of the
  table at all, so its own `missing_by_source` is empty however many
  of its cells wore a declared spelling, and a walk consulting that
  map alone reserves nothing. A candidate the reader's own rule would
  call absent is stepped past by both families before it is claimed,
  and the capacity a shape supplies at a width is what is left after
  those spellings are taken out — so the refusal of G9.4 counts them
  out too. Measured: a label column publishing `missing_by_source
  {"1e400": 12}` beside a wide column of five-character values gave
  that wide column `1e400` — the exponent family's very first
  spelling — as a PRESENT cell, and `synthtwin validate` reported
  eight of its counts missed against a generation report that named
  nothing.
* **The asked width is the width of the WHOLE CELL.** A minus sign, a
  leading `0.` and a trailing figure are all spent inside it, so a group
  asked for 400 characters writes a cell 400 characters long and not
  401 or 402.
* **THE TOO-SMALL SHAPE'S ZERO RUN GROWS UNTIL ITS VALUE UNDERFLOWS,
  and is not a fixed count.** That shape spends its width on `0.`, a
  run of zeros and a figure body, and the body grows as the walk
  enumerates distinct values — so a run sized as whatever the width
  leaves shrinks as the body grows, and the value climbs back up until
  it is a value binary64 holds. A fixed floor high enough for the worst
  body is safe and writes every better body too wide: behind 323 zeros
  the body `10` underflows and the body `9` does not, and a six-figure
  body needs only 319. The rule is therefore the question itself, asked
  of each candidate spelling, which is also the only form two
  implementations can agree on without sharing a constant.
* **The in-range fraction's narrowest spelling is `.5`, two
  characters.** The leading zero is optional, so a column whose
  narrowest numeric-looking cell is two characters has a shape that can
  carry that floor; at that width the body is the point and one figure,
  which gives nine distinct spellings.
* **A shape may only be asked for a width it can actually write.** Two
  of the six write at a width of their own whatever they are given —
  contradictory notation is the fixed construction of G10.3 and
  ordinary text is a stand-in drawn by the text rule — so neither may
  be chosen to carry either published end. Of the four that may, each
  has a narrowest spelling as well as a magnitude floor: the in-range
  fraction needs three characters (`1.5`) however narrow the ask, and
  the two out-of-range shapes need five and six by the exponent
  family's floors above — which is what lets a column published at 5
  and 6 characters carry BOTH its ends rather than neither.
  **And the floor is only assigned when some OTHER group can still
  carry the ceiling**: a column with exactly one carrying group must
  spend it on the ceiling, because the groups that carry nothing land
  where they land and that is where the floor already is.
* **A FOLD-COLLISION PARTNER IS HELD TO ITS GROUP'S ASKED WIDTH**
  (revision 4). A partner (G9.3) is a respelling of a value already
  written — a case flip, edge spacing, or both — and while this role
  published no length at all its spacing was held to no window and ran
  on as far as the collision needed. Now that both ends are published,
  a partner free of the window consumes the group the ceiling was
  assigned to: two 310-figure values folding together, published as 310
  to 312 characters wide, wrote a parent at 310 and a partner at 311
  and held no 312-character cell anywhere. The window is the group's
  own ask at both ends.

Construction, in this fixed order, so the counts land exactly:

1. **The cells a twin may write, and which published count each
   answers for.** A wide cell is written in one of six shapes: the
   contradictory construction of G10.3; a whole number too large for
   the format; a fraction too small for it; a whole number the format
   holds; a fraction the format holds; and ordinary text. The shipped
   parser's own answers tie those six to the published counts, and this
   tie is the whole of the relationship between them:

   | shape | counted by | whole-number status | sign |
   |---|---|---|---|
   | contradictory | `n_contradictory` | `n_whole_unknown` | `n_sign_unknown` |
   | too large | `n_out_of_range` | `n_whole` | `n_negative` or `n_positive` |
   | too small | `n_out_of_range` | `n_fraction` | `n_negative` or `n_positive` |
   | whole, in range | `n_numeric` | `n_whole` | `n_negative` or `n_positive` |
   | fraction, in range | `n_numeric` | `n_fraction` | `n_negative` or `n_positive` |
   | ordinary text | `n_not_numeric` | `n_whole_unknown` | `n_sign_unknown` |

   **A group whose cells carry no sign can answer only for
   `n_sign_unknown`, and only for `n_whole_unknown`**: notation that
   conflicts with itself and ordinary text are the shapes whose sign
   and whole-number status the shipped parser refuses to guess, and
   that rule is carried into the packing as a permission rather than
   left to chance.
2. **The three published families are THREE MARGINS over those cells,
   and no cross-tabulation of them is assumed** (P2-C3-F1). The
   description publishes how the cells divide by notation class (`X2`:
   `n_numeric`, `n_not_numeric`, `n_out_of_range`, `n_contradictory`),
   how they divide by whole-number status (`U1`: `n_whole`,
   `n_fraction`, `n_whole_unknown`) and how they divide by sign (`U2`:
   `n_negative`, `n_positive`, `n_sign_unknown`). It publishes NOTHING
   about how those three divisions cross. In particular **how
   `n_out_of_range` divides between whole numbers and fractions is not
   a published fact**, and an implementation that fixes it by a rule of
   its own — spending `n_whole` on the too-large cells first, say — has
   invented a description and may then find no packing where the real
   column had one.

   Revision 2 did exactly that and lost six exact counts on a genuine
   six-row column: four groups of 2, 2, 1 and 1 publishing
   `n_numeric = 2`, `n_out_of_range = 1`, `n_contradictory = 3`,
   `n_whole = 2`, `n_fraction = 1`, `n_whole_unknown = 3`,
   `n_negative = 3`, `n_positive = 0` and `n_sign_unknown = 3`. Sending
   the one out-of-range cell to `n_whole` asks for cell quotas no
   packing of those groups meets; sending it to `n_fraction` — equally
   consistent with every published count — is met exactly. The real
   table proves only that SOME cross-tabulation of the published counts
   exists, never which one, so the packing is stated over the three
   margins themselves and the walk chooses among every cross-tabulation
   they permit.
3. **The three margins are ONE packing, not three** (P2-C2-F1,
   P2-C3-F1). Which shape a group takes settles which sign counts and
   which whole-number counts it can answer for, so deciding them one
   after another throws away joint assignments that exist: round 2
   built a five-row column with groups of 1, 1, 1 and 2 whose joint
   class-and-sign assignment is exact and which two separate walks
   missed, writing two negative cells and none positive against one of
   each. All three are therefore packed together by the grid rule of
   G9.5, over the cells and permissions of step 1, with the notation
   counts, the whole-number counts and the sign counts as its three
   margins. Spending the negative count greedily and stopping at the
   first group too large to fit is not conforming — on three negative
   rows in one group beside two positive groups of two it writes two
   negatives (P2-C1-F1).
4. In-range cells are written from the leading-zero family — a run of
   zeros carrying a whole number or a fraction — padded to the width
   the group was asked for, since no ladder and no statistic is
   published for this role. **What separates one spelling of a shape
   from the next is its VALUE and not its width**: the in-range whole
   shape writes `1`, `2`, `3` and so on behind the zeros, and the
   in-range fraction shape writes `1.5`, `2.5`, `3.5`. Distinguishing
   them by adding a zero instead — which revision 3 did, having no
   width to hold to — makes every group after the first one character
   wider than the width it was asked for, so a column published as at
   most 372 characters wide holds a 373-character cell.

   **EACH SHAPE-AND-SIGN PAIR WALKS EACH FAMILY FROM THAT FAMILY'S OWN
   START** (stated in revision 5). This document had left the walk's
   bookkeeping unsaid, so one conforming program could count per shape
   and another per shape and sign, and the two would write different
   cells the first time a column carried a positive and a negative
   group of one shape. No frozen case carried one, which is why it
   took until revision 5 to notice. The rule is the second: the
   positive and the negative groups of a shape each begin at that
   shape's first spelling, and a group refused by one family does not
   move another family's place.
5. The repetition pattern is `n_distinct_by_occurrences`, exactly as in
   G9.5 step 1; the capacity rule and its refusal (G9.4) apply, with the
   digit alphabet over the width each group was asked for.

   **A SHAPE'S CAPACITY IS THE SUM OVER ITS FAMILIES** (revision 5).
   The two out-of-range shapes have two spelling families, so the count
   of distinct values either can supply at one width is what the
   digit-string family supplies there PLUS what the exponent family
   supplies there, and the refusal is raised only when both are spent.
   The two counts are very different and a reader who prices one for
   the other gets a wrong answer: at a room of 327 characters the
   too-small shape's digit-string family runs out at twenty-four
   spellings — the next is a value the format holds unless its zero run
   grows, and a grown run is a character wider than the description
   asks — while its exponent family supplies every mantissa the room
   holds at each exponent it visits. At a room of five the too-large
   shape's digit-string family supplies NOTHING at all, because its own
   floor is 310, and its exponent family supplies **6,227**: nine
   mantissas at each of the 691 three-figure exponents whose every
   mantissa overflows, plus the eight at 308 that overflow while
   `1e308` does not. A rule that fixed the exponent would supply nine,
   and nine is fewer than a real column of that width holds — which is
   how the refusal of G9.4 came to be raised on a description a
   profiler wrote. A rule that stopped at the first refused candidate
   supplies 6,219, and a real 6,220-value column of that width was
   refused for the missing eight. At six characters the too-small
   shape's exponent family supplies **6,077**, and the difference
   between that and 6,084 is the two spellings its edge falls short of
   a whole exponent by.
6. **Every one of `n_whole`, `n_fraction`, `n_whole_unknown`,
   `n_positive`, `n_negative` and `n_sign_unknown` is recounted from the
   finished cells** and named in the report where it was missed, under
   its own field name, with the achieved value beside the published one.
   The recount asks the shipped parser the same three questions the
   profiler asks of a real cell — what the notation classifies as, what
   sign it settles, and whether it is a whole number — and, like the
   profiler, it leaves a cell that reads as ordinary text out of the
   sign and whole tallies altogether. Where the three margins have no
   joint answer at all — which no description a real table produced can
   reach, because that table's own values are such an answer — G9.5's
   fallback rule applies: each published family is packed after the one
   before it, and this recount is what turns whatever it missed into a
   NAMED deviation the report renders. The four notation counts are
   recounted the same way on every role (G10.2). A miss on this path is
   never silent, and a miss the search could have avoided is a defect
   rather than a deviation.

   **THE RECOUNT SPANS BOTH SPELLING FAMILIES** (revision 5), and it is
   worth saying why it needed no clause of its own to do so: it asks
   the shipped parser rather than reading the writer's intention. The
   parser answers of `1e400` exactly what it answers of a 310-figure
   numeral — out of range, whole, and the sign its leading character
   carries — and of `1e-400` exactly what it answers of `0.` behind
   325 zeros and a figure. So a cell of the exponent family recounts
   under the same class as the digit string it stands in for, and the
   twelve counts of this step bind it unchanged. A recount that read
   the class off the FAMILY instead would have had to move; there is no
   such recount on either side of this product, and this sentence is
   what a second implementer should check rather than assume.
7. **AND BOTH PUBLISHED WIDTHS ARE RECOUNTED THE SAME WAY** (revision
   4). Nothing in steps 1 to 5 promises them: the in-range shapes take
   the width they were asked for, the out-of-range shapes take whatever
   keeps them out of range, and a fold-collision partner (G9.3) is
   spelled to fold onto its parent rather than to fit a width. So the
   character counts of the narrowest and the widest finished cell are
   measured and compared to `min_length` and `max_length` **for
   equality, not for containment**. A twin whose narrowest cell is
   WIDER than the narrowest in the real table has not held the
   published fact, and a check written as "no narrower than the floor"
   passes a column published at 250 whose twin starts at 310. Either
   end that does not match is a NAMED deviation carrying the twin's own
   count beside the published one. A miss on this path is never silent.

## G11. The all-different obligation

**The rule, once:** whenever a column publishes
`n_distinct == n_present`, its present values are ALL DIFFERENT in the
twin, on every role, in that column's own notion of equality — because
an undeclared key column arrives as free text or as a numeric role, not
as an identifier (P1-D4 item 8; P2-R5-F3).

The obligation can bind only on facts the profile actually publishes,
and stating it that way is what stops a fourth instance arriving
undetected. Where the raw distinctness of a column was produced by
something the disclosure rules WITHHELD, the twin cannot reproduce it
without making up unpublished facts; raw distinctness is REPORT-ONLY
there, and the report names the achieved count beside the published one.

How each role meets it:

| role | notion of equality | mechanism |
|---|---|---|
| `count`, `continuous` | the raw spelling | G6.5: `M = K` different values, and the leading-zero family for any spelling budget above that |
| `datetime` | the raw spelling | G7.3 with `P` ranks, plus the published offsets of G7.4 |
| `constant`, `binary`, `categorical`, `long_tail_labels` | the raw spelling | G8.1: the published variants |
| `identifier`, `free_text`, `numeric_unrepresentable` | the raw spelling | G9.2: one enumeration element per group |
| `time_of_day` | the raw spelling | G7A.4 with `P` ranks, plus the step-and-clamp repair, which is EXACT on every description a profiler wrote |
| `affixed_number` | the raw spelling | G6.5 read over the CORES; the affix pair is fixed text and separates nothing |
| `joined_numbers` | the raw spelling of the WHOLE cell | the pairing of G4.3 over positions laid out by G5.2's grain rule: each position's numbers are placed by rule and the reserve is spent making the pairs different. This is the fourth instance below |

**The four known instances where it cannot hold**, each of which is
tested:

1. **Declared identifiers** whose published length range cannot supply
   as many distinct values as the column has rows. Owner decision 6:
   length wins, values repeat, and three distinctness facts become
   REPORT-ONLY (G9.6).
2. **Label columns whose values differ only before the fold**, beneath
   the small-cell floor. Owner decisions 9 and 11 publish the variants,
   so the obligation now HOLDS wherever the variants are visible and
   falls back only beneath the floor, where `variants_withheld` says how
   many spellings to invent but not what they were; the invented
   variants of G8.2 are distinct, so the obligation is met in form, and
   the report names that the spellings themselves are invented.
3. **Datetime columns whose offsets are withheld.** A 30-row column of
   ten rare offsets over 15 dates publishes
   `n_present = n_distinct = 30` while `utc_offsets` collapses to
   `{"(withheld)": 30}`: the obligation fires, but the profile never
   says which offsets made those 30 spellings distinct, so the twin
   holds only 15 instants and no published way to spell them apart
   (G7.4). Raw distinctness is REPORT-ONLY for that column. Where the
   same column's offsets ARE published, the obligation holds and the
   twin uses them.

4. **Joined-number columns, where the PAIRING cannot reach the count.**
   This role publishes each position's numbers separately, so the cell
   a row wears is made by pairing one number from each position. Each
   position's multiset is held exactly, but the number of different
   WHOLE CELLS that any pairing of those numbers can produce is bounded
   by the numbers themselves, and the published count is a fact of a
   real column that the bound may sit below. The pairing is not left to
   chance: it is walked toward the published `part_agreements`,
   `part_above` and cell count together (G4.3), which closes most of
   the gap and not all of it, and those targets can pull against
   each other. Measured on six 400-row
   two-position columns whose cells were all different: the twin held
   375 to 385 of 378 to 388, short by three or four every time, and
   every one of the six reported the shortfall as a deviation of
   `n_distinct` and `n_distinct_folded`.

   **WHERE THE BOUND CAME FROM WAS PART OF THE DEFECT UNTIL LANDING
   L7, and the bound is real but was far tighter than it had to be.**
   Each position was laid out in as many strata as the whole CELL had
   different values (G5.2), so a position held far MORE different
   numbers than the real one did and the pairs it could make were the
   wrong pairs — a 400-row blood pressure publishing 110 different
   readings, whose positions hold 13 and 9 different numbers, came out
   with its positions holding 34 to 41 and 23 to 29 and the column
   holding 157 to 169 different cells. G5.2's grain rule and the walk
   of G6B.4 close that one: measured at forty seeds, the same column now
   holds exactly 13 and 9 different numbers and exactly 110 different
   cells at all forty sampled seeds, and `synthtwin validate` misses
   nothing at those. Seed 141 holds 108 of 110, which is the duplicate-
   value mechanism of residual R-P4-120 rather than the pairing.

   **What remains is bounded by the DRAW and not by the pairing, and it
   is measured.** A 240-row column of 240 different readings whose
   positions hold 20 and 12 different numbers — exactly 240 possible
   pairs — reached 173 to 188 before and 195 to 234 now, and the reason
   it is not 240 is that the twin's own positions hold 18 to 20 and 11
   to 12 different numbers rather than 20 and 12: two strata of one
   position can be given the same number by the ladder, which is
   residual R-P4-120 and is the plain numeric roles' business rather
   than this one's.

   **The report vehicle is a DEVIATION and not an approximation**, and
   the difference is not a nicety. This role builds no `Approximation`
   record and carries no window for distinctness: what it writes is a
   named miss, and the recount at the end of generation measures the
   FINISHED cells, so no shortfall on a finished column is silent.
   Calling it APPROXIMATED, as an earlier revision of this passage did,
   would say a window governs it when none does. This is residual
   R-P4-40.

   **Two defects here were found and fixed on 2026-08-27, and the first
   is why the second went unseen.** The LOADER refused every joined
   column carrying an unparsed cell: a position describes only the
   cells that split, so the profiler writes `n_joined` as that block's
   row count, and Q1 compared it against the TABLE's row count -- so
   `synthtwin profile` wrote a file `synthtwin generate` refused,
   telling the user the file had been changed since it was written and
   to make it again, which produces the same file. With no unparsed
   cell the two counts coincide, which is why nothing showed. And the
   PAIRING was asked for the whole column's count rather than the count
   the pairs can carry: cells that did not split are replaced
   afterwards by stand-ins that are all ONE spelling, adding exactly one
   to the number of different cells however many there are, so a
   120-cell column holding 120 different cells was told by its own
   report that it held 119.

A fifth instance is a change to this document, not an exception granted
during implementation.

## G12. Feasibility, refusals, and named deviations

The generation-feasibility stage runs after the loader and before any
generation, and every outcome is fixed (P2-D6):

1. **Domains are widened first** — G9.1's alphabets include upper and
   lower case and the full printable ASCII range, and G9.3's partner
   family adds edge spacing to the case flips, so a fold collision can
   be placed on a value with no case at all.
2. **Identifier length versus distinctness**: owner decision 6 (G9.4,
   G9.6).
3. **Numeric raw distinctness**: owner decisions 7, 8 and 10 (G6.5).
4. **Published counts take precedence over ladder conformance** where a
   numeric conflict is otherwise resolvable (G5.5); the residual
   deviation is measured and named.
5. **Refusal is reserved for documents no rule above can satisfy.** This
   method has exactly four, each of them a refusal of GENERATION rather
   than a claim that the description is invalid, and each says the
   profile is VALID, names the two facts that cannot both hold, and
   gives remediation that does not assume the person still holds the
   table:
   - `generation-domain-too-small` (G9.4) — a free-text or
     unrepresentable column whose published multiplicity map needs more
     different values than its published length range can spell;
   - `generation-counts-contradict` — a numeric column whose
     `n_zero` and `n_negative` together exceed `n_numeric` (`P < 0` in
     G5.1), which no ordering of values can satisfy;
   - `generation-words-exceed-length` (G9.5 step 6, review item
     P2-C5-F4) — a free-text column whose `words.max` is more than its
     `length.max` can hold, or whose `words.min` is more than its
     `length.min` can hold, given that a value of `L` characters holds
     at most `(L + 1) // 2` words;
   - `generation-whole-numbers-need-room` (G9.6, review item P2-C5-F4)
     — a declared identifier published as whole numbers whose length
     range leaves a value that must stand outside the figures no
     whole-number spelling at any length: one character that reads as a
     whole number IS a figure, so a longest length of one character
     with `n_all_digits` below `n_present`, and a shortest length of one
     character with `n_all_digits` of zero, are both descriptions no
     table can hold — **each asked of every figures count G9.5's reading
     offers** (plan P4-D298): `n_all_digits` is absorbed, so nought
     stands for a column whose one figure-only cell fell below the line,
     and `7` beside twenty `-3` is its own witness that the pair can be
     written;
   A FIFTH REFUSAL WAS ADDED HERE ON 2026-08-12 AND WITHDRAWN ON
   2026-08-13, both by amendment, and the round trip is recorded rather
   than erased. `generation-whole-numbers-need-code-room` stopped a
   declared identifier published as whole numbers whose values must
   stand in the code alphabet with no room for a third character. The
   owner withdrew it under decision 9: a description carrying those
   counts proves the real column held sign-leading values, so refusing
   denied a person a twin over a character their own file used. G9.1's
   bar carries the bounded carve-out instead, and the report counts and
   names the cells.

   The last two were written as twins with the exact fact named as
   missed until review item P2-C5-F4; the ratified plan reserves the
   report line for facts a rule CAN meet, and a person who receives a
   twin where the plan says the run stops has no signal that anything
   was wrong. A fifth refusal is a change to this document, not an
   exception granted during implementation.

Every deviation this document permits is **measured against the
published fact and named in the report, every run**, with the achieved
value beside the published one. The complete list, so that a reviewer
can check the report against it: a raised distinct count (G5.2); an
endpoint moved by a sign repair (G5.5); a `leading_plus` quota larger
than the column's own count of non-negative cells, and a point-free
demand larger than `K` minus the cells the published ends force to
carry a point — the only two shapes G6.4 leaves, both narrower than
the entry this replaces, which named any unplaceable point-free quota
before G5.2's carrier step existed (G6.4, P2-C4-F3); a folded count
that could not fall below its raw count
(G6.5); a
datetime reading that fell from `utc` to `local` because every offset
was withheld (G7.4); the invented spellings behind withheld label
variants (G8.2) and withheld levels (G8.3), including the numbers
written for held-back numbers and whether anything published places
them (`suppressed_levels`, G8.3a); identifier duplicates and
the three distinctness facts they cost (G9.6); a word count brought down
to what its own length carries on a group carrying NEITHER published
word extreme, the two carrying groups being settled by a refusal instead
(G9.5 step 6, P2-C5-F4); a published width of an unrepresentable column
that no shape of that column can be written at, which revision 4 names
as a deviation rather than making a width up for (G10.5); the
out-of-range cells all written too large (G10.3); the
form census of a column of dates read under the joint ISO reading,
which the twin does not reproduce (G7.5, contract C6-25, plan
P4-D4.3); a count of the census of written forms
(`shape_forms`, contract 7.9) a twin's finished cells did not reach,
which the same landing's own guard found missing from this list on its
first run; the pooled marks of a datetime separator census, written in
the marks the census leaves unnamed (G7.5, plan P4-D39, since landing
2b.3 not a deviation, because the twin pools the same count); a
shortfall in that census after the absent-spelling exception that no
rank could give back (`datetime_separators`, G7.5); the values of a
column of moments left in a spelling the table declares absent because
every mark offered was absent too (`n_present`, G7.5); a column of
numbers whose own twin cells reach too few four-figure values to prove
the mark it writes, at the published smallest group size -- a column of
numbers, the cores each wrapper of an affixed column wears, or the
numeric half of a column of numbers and labels
(`group_separator`, `affix_variants[<n>].numbers.group_separator`,
`numbers.group_separator`, G6.1; the stage 2 closure and confirmation
reviews, 2026-09-14 and 2026-09-15); a column whose twin put fewer values
that are not negative in the decimal form than the description counts
signed decimals, so fewer of its cells carry a plus (`decimal_plus`,
G6.1; landing 2b.2); a column whose twin values come to
two or fewer once case is ignored where the description counts three
or more, so that describing the twin again reads it as a column of two
values or one (`n_distinct_folded`; the stage 2 confirmation review); a
cell of an `all_at_midnight` column written off midnight, which the
rule says never happens and a run that finds one has found a defect in
itself (`all_at_midnight`, G7.5); a column partly at midnight whose
twin reaches another count of values at midnight, where the pinned
ranks leave too little room (`n_at_midnight`, G7.5, landing 2b.3); and
**a value left inside a stretch the description says
holds nothing** — named `empty_bins` where the stratum stands in a bin
the description names, `empty_edges` where it stands only inside a
published pair, carrying that stretch's two PUBLISHED edges and the
value that stayed inside them (G6.7.8, plan P4-D32 and P4-D35). Those
last two were missing from this list from the landing that authorized
them until 2026-09-04, which is a list that calls itself complete and
was not.

**The census entry, in full, because it is the one entry on this list
that is named on EVERY run of the column it belongs to.**
`resolution_mix` is REPORT-ONLY: it records how many of the real
column's parsed cells were written as a whole date and how many carried
a time of day, and the twin writes every one of them at the column's
finest recorded precision, because a cell spelled as a whole date
cannot carry an interior value of a column published at the second. So
the achieved side is not a shortfall a rule failed to reach; it is what
the rule above says the twin writes, and the entry exists so the reader
is told rather than left to work it out. It is RECOUNTED from the
finished cells like every count below, not predicted: the rule says the
twin writes no whole dates at all, and a run that finds otherwise has
found a defect in itself. A column read under ONE format has no such
line — its census restates that format's own name beside the parsed
total, and `format` is already disclosed as recorded-not-reproduced, so
a second line would tell a reader there were two losses where there is
one.

**THE KEY INDEX, so that "complete" is a claim a machine can check.**
The prose above names each deviation by the SHAPE of what happened,
which is what a reader needs and what a checker cannot read. Every
`fact` name a report may carry is therefore listed here as well, and
`tests/test_p4d32_empty_bins.py` resolves the names the generator can
pass -- through the helpers that forward one -- and holds this index
to them in BOTH directions. Three keys were missing from the prose
list when that guard was first written: `shape_forms`, and the two
gap keys `empty_bins` and `empty_edges`.

**AND TWO MORE WERE MISSING WHEN THE MIXTURE CENSUSES LANDED** (landing
2b.7, 2026-09-15). `negative_notations` and `thousands_marks` are keys
a report may carry the moment a column publishes a mixture of
conventions, and the landing that added them to the generator did not
add them here -- so this index stopped being complete and the guard
above turned red, which is exactly what it is for. They are listed
below. The lesson is the one this repository keeps relearning: a closed
enumeration is stated in up to eight places, and the deviation key
index is one of them.

**AND ONE MORE AT THE EXTRA ROUND OF 2026-09-18** (plan P4-D267):
`mode`, named where the published mode is a number the ladder leaves the
twin no room to write. The round that added `generation._mode_note` did
not add the key here, so the index stopped being complete and the guard
above turned red with every other check green -- which is exactly what it
is for, and it is the same lesson twice: a closed enumeration is stated
in up to eight places and this index is one of them.

**AND ONE MORE AT THE SECOND CODEX ROUND OF 2026-09-19** (item 1 of its
numbers pass): `mode_count`, named where the twin holds the published
mode's VALUE on a stratum the published count does not size. The pass of
P4-D267 declared success wherever some stratum held the mode, whatever
its size, so the count went unmet in silence: measured at a floor of
eleven on one-place values -1.8, -0.9, -0.6, 0.8, 1.8, 3.3 and 3.5 at the
counts 9, 18, 28, 23, 8, 30 and 23, the published mode 3.3 at a count of
30 was written ONCE and nothing was named.

**AND TWO LEFT THE INDEX IN STAGE 3** (plan P4-D328): `earliest` and
`latest`. A column of dates publishes neither instant any more, so no
call can pass either name and an index naming them would be a report
key nothing can produce -- which this guard reads in that direction
too. What stands in their place is two TAILS, and they are named in
the shape list below rather than here: a boundary is exact, written
from the published moment's own fields, so no run can fail to reach
it; the two DISTANCES are approximated inside the construction window
of G12.14, which is what an entry of that list is for.

**AND ONE MORE AT PLAN P4-D192**: `date_field_widths`, named where a
census of one convention is left unmet by the count passes of G7.3. *Widened by plan P4-D195:* a census naming several conventions is
recounted the same way, and each convention whose count the twin does not
hold is named -- those counts are spread over the values and held only at
the floor, so without the note a different count passed unsaid.

* `all_at_midnight`
* `all_whole_numbers`
* `date_field_widths`
* `datetime_separators`
* `datetimes_read_at`
* `decimal_plus`
* `empty_bins`
* `empty_edges`
* `field_widths`
* `fraction_widths`
* `group_separator`
* `integer_valued`
* `n_at_midnight`
* `max_length`
* `min_length`
* `n_all_digits`
* `n_code_alphabet`
* `n_contradictory`
* `n_distinct`
* `n_distinct_by_occurrences`
* `n_distinct_folded`
* `n_distinct_values`
* `n_fraction`
* `n_missing`
* `n_negative`
* `n_not_numeric`
* `n_numeric`
* `n_out_of_range`
* `n_positive`
* `n_present`
* `n_sign_unknown`
* `n_unparsed`
* `n_whole`
* `n_whole_unknown`
* `mode`
* `mode_count`
* `negative_notations`
* `numeric_styles`
* `pad_widths`
* `percentiles`
* `resolution_mix`
* `shape_forms`
* `subsecond_digits`
* `suppressed_levels`
* `thousands_marks`
* `utc_offsets`
* `words`
* `levels -> shape_form_cells`
* `levels -> variants_withheld`

**AND THE FAMILIES WHOSE NAME CARRIES A POSITION, listed as their
shape** (review round 6 item 5; five of them when it was written). A
report builds these from a position, a seat, a rung or a SIDE, so the
index names the SHAPE and the guard holds the shapes to the writing
rules that build them:

* `parts[<n>].<key>` — any key above, carried by one POSITION of a
  `joined_numbers` cell, `<n>` counting from nought
* `affix_variants[<n>].<key>` — one WRAPPER's own key, which is where
  its two counts of different cores sit: they belong beside the block
  rather than inside it, so a record about them takes this path
* `affix_variants[<n>].numbers.<key>` — any key above, carried by one
  WRAPPER of an `affixed_number` column that wears a set of them (plan
  P4-D37), `<n>` counting from nought over the wrappers the description
  states beside the commonest. The commonest wrapper's own block is the
  column's, so its keys are carried bare and appear above rather than
  here: a report naming `affix_variants[0].numbers.mean` says WHICH
  wrapper's mean moved, and a bare `mean` on such a column says it was
  the commonest one's
* `numbers.<key>` — any key above, carried by the NUMERIC HALF of a
  `numbers_with_labels` cell, which is where that role publishes its
  quantitative facts
* `part_agreements[<n>]` — the agreement between two neighbouring
  positions, `<n>` the earlier of the pair
* `part_above[<n>]` — how often the later of two positions is above
  the earlier, `<n>` the earlier of the pair
* `percentiles.p<nn>` — one rung of a NUMBER ladder, `<nn>` the
  percent written to two figures
* `clock_percentiles.p<nn>` — the same for a clock ladder
* `date_percentiles.p<nn>` — the same for a date ladder
* `<n>_tail.mean_distance` — how far, on average, the cells beyond one
  TAIL's boundary lie beyond it, `<n>` the side that tail stands on,
  `low` or `high`, on a column of dates or clock times (stage 3, plan
  P4-D328)
* `<n>_tail.rms_distance` — the same for the root-mean-square distance,
  which such a tail publishes where it publishes no values
* `tails.<key>.<key>` — one distance of one NUMERIC tail (stage 3,
  contract 6.7a): the first `<key>` is `low` or `high` and the second is
  `mean_distance` or `rms_distance`

A name here is a key a report MAY carry, never one it must: every
entry above is a deviation raised only where the twin did not reach
the published fact.

**What this list does not hold, and why the absence is the point.** No
end of a column of dates appears in it, and neither does a tail's
BOUNDARY -- the fact that stands where an end stood. The contract's D10 and D11
settle every description on which one could not be written, so a
generator has an exact answer for the two ends of every column it is
handed; a run that finds otherwise has found a defect in itself, prints
it in the same shape as the entries above, and is not conforming while
it does. A list is the place a lowered obligation hides — four repairs
put one here or in a paragraph like it (contract 13.16) — so a fact
leaving this list is a fact whose bar went back up, and one arriving
needs the ratified plan to name it first.

**And, on every column, every published count the packing rule of G9.5
could not meet.** These are not predicted by a rule; they are RECOUNTED
from the finished cells, which is what lets them catch a shortfall no
rule of this document foresaw (P2-C1-F1). Each is named under the
contract's own field name, never under a name the implementation
invented for it:

- the four class counts `n_numeric`, `n_out_of_range`,
  `n_contradictory` and `n_not_numeric`, on every role (G10.2);
- `n_all_digits` and `n_code_alphabet` on the two roles that publish
  them, and `all_whole_numbers` on a declared identifier (G9.5, G9.6);
- `length.min`, `length.max`, `words.min` and `words.max` on a column of
  free text (G9.5 steps 5 and 6). **These four were pinned and never
  recounted, and one of them was lost in silence** (P2-C4-F2): a group
  pinned to the published largest word count and then given a class
  that writes one unbroken run of characters wrote one word, no rule
  predicted it, and no line of the report said so. A construction that
  believes a fact is exactly the construction that stops measuring it,
  so all four are measured from the finished cells like every count
  above them;
- `n_whole`, `n_fraction`, `n_whole_unknown`, `n_positive`,
  `n_negative` and `n_sign_unknown` on an unrepresentable column
  (G10.5);
- `n_distinct` and `n_distinct_folded` on every column.

### G12.1 What an APPROXIMATED fact owes

The profile contract gives every published field exactly one
disposition, and APPROXIMATED means: reproduced under a stated rule
inside a two-sided finite-sample bound, MEASURED from the written CSV,
checked against BOTH ends of that bound, and named in the generation
report with the achieved value beside the published one
(`docs/spec/profile-contract-v4.md` section 2.2). This subsection and
the six after it fix that rule and both ends for every field the
contract's matrix marks APPROXIMATED. The complete list, by role:

| role | field | where its bound is fixed |
|---|---|---|
| `count`, `continuous` | the nine interior rungs of `percentiles` | G5.6, restated as G12.2 |
| `count`, `continuous` | `mean`, `std`, `skew` | G12.3 |
| `datetime` | the nine interior rungs of `date_percentiles` | G12.4 |
| `datetime` | `n_distinct`, `n_distinct_folded` | G12.5 |
| `free_text` | `length.mean`, `length.p50`, `words.mean` | G12.6 |
| `constant`, `binary`, `categorical` | `n_distinct` in its fallback | G12.7 |
| `count`, `continuous` | `n_distinct`, `n_distinct_folded` in their fallback | G12.8 |

Nothing else is approximated. Every other published field is
EXACT-OBSERVABLE, EXACT-CONTROL, REPORT-ONLY, LOADER-ONLY or
STRUCTURAL, and a field measured under two dispositions would be a
field with two answers.

Four rules hold for all of them.

1. **Measured, never predicted.** The achieved value is recomputed from
   the FINISHED cells — the same characters the twin file carries —
   using the profiler's own formula for that field, so that the two
   numbers the report prints side by side are the same statistic
   computed the same way. A value the generator held in memory on the
   way to the file is not the measurement.
2. **Both ends are checked, and both are finite.** A bound with one end
   is not a bound: a twin can leave a one-sided window in the direction
   nobody looked. Where a derivation below would leave an end at
   infinity, the subsection names the finite value that replaces it and
   why that value is a true bound.
3. **Every one is named in the report, every run**, with the published
   value, the achieved value, both ends of the bound and whether the
   achieved value landed between them — whatever the answer is. A fact
   whose bound was checked but not printed is a fact the reader has to
   take on trust, and this document treats an unshown check as a check
   that was not made.
4. **A measurement outside its bound is ALSO a named deviation.** The
   bound is a statement this method makes about its own construction,
   so a twin that leaves it did not hold what the description asks for,
   and it belongs in the deviation list of G12 beside every other fact
   the twin could not meet.
5. **EXCEPT WHERE THE TWIN HOLDS THE PUBLISHED VALUE ITSELF**
   (*added by the dates pass of the stage-3 review, item 9; the same
   reading the quality report takes under validation method clause
   V6.1-A1 and plan amendment A-P3-40*). None of these bounds is a
   margin around the published value -- each is worked out from the
   description and the size of the column, so a bound can lie wholly to
   one side of the value printed beside it. Where the achieved value
   EQUALS the published one, the published fact was met, whatever the
   window says: the record is marked as having landed inside, and no
   deviation is raised for it. The window is still printed at both ends
   and the report still says where it does not reach the published
   value, so nothing is hidden -- what is removed is a page that said
   "the description says 23:44; the twin holds 23:44 ... OUTSIDE the
   range" and named the rung, four lines above, as a fact the twin had
   not reproduced. That is a line no reader can act on, and it was
   printed on a twin reproducing the real column's whole multiset.

**A bound here is a statement about the CONSTRUCTION**, derived from the
rule that builds the cells, never a tolerance measured on an output and
rounded up. That is what makes each one able to FAIL: a generator that
ignored the published ladder, collapsed the interior rungs, wrote
values at the wrong precision, or made up its own lengths leaves these
windows on an ordinary column. A bound no wrong twin can leave is not a
check.

### G12.2 The bound on the nine interior numeric rungs

G5.6 states it, and it is not restated here. On a tail block it is read
through G5.3b's ladder (G5.1a), and a rung the tail rule withholds has no
window. Its two forms are used
below: the rung form, over the nine published interior rungs, and the
rank form, over every sorted position of the twin's own numeric cells.
Both use the same displacement `d = (g_max + 2) / K`, where `K` is the
number of cells the twin writes that read back as a number and `g_max`
is G5.6's, read off the description. **Both reports read that `g_max`,
and neither rebuilds the layout** (landing 2b.1, part 2), except that the
twin's own report reads it as no less than a stratum G5.2b's carrier and
reach steps moved past `Cap`, which G5.6 names. Before it the
twin's own report read the layout it had just built and the quality
report read an estimate narrower than that layout: on a 2,000-row
rounded-income column the twin report allowed `p75` anywhere from
55673.3 to 63799.2 and called it inside, and the quality report allowed
59624.75 to 60275.25 and called it MISSED.

**Each end is the ladder read at an exact fraction.** Write
`Ladder(N / D)` for G5.3's reading of the hundred and one rungs, filled
by G5.1, at the share `N / D` of two whole numbers: its `A`, `B`, `T`
and `t`, the four convex-form operations in their order, and the clamp.
The rung form reads interior rung `i` at

```
low  = Ladder(max(0, PCT[i] * K - 100 * (g_max + 2)) / (100 * K)) - h
high = Ladder(min(100 * K, PCT[i] * K + 100 * (g_max + 2)) / (100 * K)) + h
```

and the rank form reads rank `k` of `K >= 2` at

```
A[k] = Ladder(max(0, k * K - (g_max + 2) * (K - 1)) / (K * (K - 1))) - h
B[k] = Ladder(min(K * (K - 1), k * K + (g_max + 2) * (K - 1)) / (K * (K - 1))) + h
R[k] = Ladder(k * K / (K * (K - 1)))
```

and a column of one value at `Ladder(0 / 1)`. No share is formed in
binary64. `PCT[i] / 100 - (g_max + 2) / K` formed that way is the same
number in exact arithmetic and not the same reading, and it put one
window into the two reports in two sets of last digits (residual
R-P4-61).

**The half unit, and the two rules that can spend it.** On a column
publishing `integer_valued: true` both ends widen by one half unit, and
by nothing else, because G5.4 rounds each value to a whole number
exactly once. On a column publishing `integer_valued: false` whose
`numeric_styles` map holds a count for `plain`, `leading_zero` or
`leading_plus` -- or a withheld share, which G6.4 writes plain -- the
values step of G6.4 may take a stratum to the
nearest whole number so that the published form can be written at all
(P2-C2-F2), which is the same half unit and no more; both ends widen by
it there too. A column publishing none of those three counts keeps the
tighter window, so the widening is granted to exactly the columns whose
own map can spend it and to no others.

**And the step that spends nothing.** Where that whole number is
another stratum's already, G6.4 takes one inside the stratum's own
share of the ladder instead (P2-C4-F3). That move is not an extra
allowance and no term is added for it: `d` already carries the whole
width of the stratum covering a rank, which is the argument G5.6 makes
in full, so a value anywhere inside that share is inside the window
before the half unit is added.

**And half a grid unit on a column written at one fraction width**
(landing 2b.1, 2026-09-15). G5.3 gives each stratum of such a column
the grid value of the ladder at one of its own ranks, which stands at
most half a unit of the column's last place from the ladder there. Both
ends widen by that half unit on a column publishing neither
`integer_valued: true` nor a point-free style count, and by the whole
half unit above where it does. These two are the only widenings this
document grants.

### G12.3 The bounds on `mean`, `std` and `skew`

On a tail block every `Ladder` below is read through G5.3b's ladder
(G5.1a); a block below its floor publishes no moment and has no window.

Let `V` be the twin's own numeric cells, sorted, read back through
`parsing.parse_number`; `K = len(V)`; `p_k = k / (K - 1)`; and, with
`Ladder` and `d` as in G5.6 and `h` the half unit of G12.2,

```
A[k] = Ladder(max(0, p_k - d)) - h        (the lowest value rank k can hold)
B[k] = Ladder(min(1, p_k + d)) + h        (the highest)
R[k] = Ladder(p_k)                        (the ladder's own value there)
e[k] = max(R[k] - A[k], B[k] - R[k])
E    = sqrt( (1 / K) * sum over k of e[k] * e[k] )
```

`A[k] <= V[k] <= B[k]` is G5.6's rank form, and `A[k] <= R[k] <= B[k]`
because `Ladder` never decreases; so `|V[k] - R[k]| <= e[k]` for every
rank, and `E` is the largest root-mean-square displacement the
construction can produce.

The three formulas are the profiler's own (`taxonomy._moments`): the
arithmetic mean; the SAMPLE standard deviation, divided by `K - 1`; and
the moment skewness, the average cubed deviation over the cube of the
POPULATION standard deviation. `std` is undefined for `K < 2` and
`skew` for `K < 3` or a column whose values are all identical, matching
the contract's Q4 and Q5; where the published field is null the twin
owes nothing and the fact is not measured.

**`mean`.** The mean rises with every value, so its two ends are the
mean of the two windows:

```
(1/K) * sum A[k]   <=   mean(V)   <=   (1/K) * sum B[k]
```

**`std`.** The sample standard deviation is
`||V - mean(V)|| / sqrt(K - 1)` for the ordinary Euclidean length,
which is a seminorm of `V`, so it moves by at most the length of the
displacement:

```
| std(V) - std(R) |  <=  ||V - R|| / sqrt(K - 1)  <=  E * sqrt(K / (K - 1))
```

giving `max(0, std(R) - E*sqrt(K/(K-1)))  <=  std(V)  <=  std(R) +
E*sqrt(K/(K-1))`, where `std(R)` is the same statistic of the ladder's
own values `R`.

**`skew`.** The skewness is a ratio, so each part is bounded and the
two are divided. With `meanA = (1/K) sum A[k]` and
`meanB = (1/K) sum B[k]`, every deviation `V[k] - mean(V)` lies between
`A[k] - meanB` and `B[k] - meanA`; cubing keeps that order, so the
average cubed deviation lies between `(1/K) sum (A[k] - meanB)^3` and
`(1/K) sum (B[k] - meanA)^3`. The population standard deviation obeys
the same seminorm argument as `std`, so it lies between
`max(0, s(R) - E)` and `s(R) + E`, and the denominator lies between the
cubes of those two. The skewness lies in the quotient of the two
intervals, taken with the sign rule division needs: a negative
numerator end is divided by the SMALLEST denominator and a positive one
by the largest, and the reverse for the upper end.

**The one column with no bound at all.** A description whose ladder is
null at EVERY rung publishes no shape for the values to take: G5.3 puts
them on the sign counts alone, and there is no `Ladder` for any of the
three bounds above to be drawn from. Such a column's moments are not
measured and not bounded, and the empty ladder is named in the report as
a deviation on every run — which tells a reader more than a bound would,
because it says the column's values follow no published shape at all. A
rung that is null while OTHER rungs hold numbers is a different case:
contract rule L3 admits one, G5.1 fixes exactly which number fills it,
and the filled ladder bounds it like any other.

**And the finite fallback.** Where `s(R) <= E` the denominator's lower
end is zero and that quotient has no finite upper end. It is replaced
by the range every sample of `K` values lies in whatever its values
are:

```
-(K - 2) / sqrt(K - 1)   <=   skew   <=   +(K - 2) / sqrt(K - 1)
```

**THE OPERATION ORDER, WHICH BOTH REPORTS FOLLOW** (residual R-P4-61,
closed by landing 2b.1, part 2, 2026-09-15). The bounds above are exact
statements, and binary64 reaches them in more than one way; the twin's
own report and the quality report reached them in different ways and
printed one window in two sets of last digits. So the computation is
fixed, step by step, and both follow it. `fsum` is the correctly
rounded sum of a list, `mean` is the profiler's exact mean correctly
rounded once, and `std` is the profiler's exact sample deviation:

```
meanA  = mean(A)                        meanB = mean(B)
m      = max over k of e[k]
E      = 0                               where m is 0
       = m * sqrt(fsum(q[k] * q[k]) / K) otherwise, with q[k] = e[k] / m
S      = std(R)                          s     = S * sqrt((K - 1) / K)
std    : max(0, S - E * sqrt(K / (K - 1)))  ..  S + E * sqrt(K / (K - 1))
s_low  = max(0, s - E)                   s_high = s + E
Q(X, c, t) = fsum(u[k] * u[k] * u[k]) / K, with u[k] = (X[k] - c) / t
skew   : max(-C, min(Q(A, meanB, s_low), Q(A, meanB, s_high)))
         ..  min(C, max(Q(B, meanA, s_low), Q(B, meanA, s_high)))
```

where `C` is the finite range below, already widened. Taking the lower
of the two readings of `A` and the higher of the two readings of `B` is
the sign rule above: a negative end is lowest over the smaller spread
and a positive one over the larger, and the other two readings are
never the extremes. **Each deviation is divided by the spread before it
is cubed**, so a column around `1e300` has a window at all. The finite
fallback is taken where `s_low` is 0 or any term is not a number. The
quotient's two ends are NOT stepped outward; only the range `C` is, once,
where it is formed — the quality report stepped the clamped ends again
and the twin report did not. Where some `e[k]` is not a number there is
no window to draw: the quality report lists the fact, and the twin
report prints "any value this format can write".

**AND EVERY LIMIT WRITTEN IN THIS SECTION IS WIDENED ONE PLACE OUTWARD
BEFORE ANYTHING IS COMPARED AGAINST IT** (review item P4-G6-R7-F1,
opened by the shape P4-G6-R6-F1 found). A limit stated as a closed form
and computed in binary64 can land one place INSIDE itself: on three
values `(K - 2) / sqrt(K - 1)` is one over the square root of two,
whose correctly rounded value is 0.7071067811865476, and the division
and the square root each round, so the expression gives ...75. A column
whose skew IS the maximum then falls outside a bound it exactly meets,
and the report tells its reader that an exactly reproduced fact was not
reproduced.

So each end of each of these bounds -- the skew range here, the tail
weight's range in G12.3a, and the inclusive agreement window of G12.9
-- is moved to the number this format holds NEXT TO IT, away from the
middle of the bound: the lower end downward, the upper end upward.
Outward, and not away from zero: the tail weight's two ends are both
positive, and moving its lower end away from zero moves it UP, past the
value the bound was drawn to admit. The widening can never turn a real
miss into a pass, because it admits exactly the values the limit itself
admits and no others. A limit already at the edge of the range is left
as it is, there being no number beyond it.

The published bound is the INTERSECTION of the quotient with that
range, so it is finite on both sides for every column, and it narrows
to the quotient exactly when the ladder's own spread exceeds the
displacement — which is the ordinary case for a column whose ladder
describes it at all. A column whose published ladder is so coarse that
`E` reaches its own spread is told so by a wide bound rather than by a
bound that cannot be printed.

### G12.3a The bound on `kurtosis`

`kurtosis` is APPROXIMATED and until this section existed its bound was
written only in code and in a plan. Three places cited "method G12.3a"
and no such section existed, so an implementer working from this
document alone could not know how close a twin has to come, and a
reader of a report that counts this fact among its approximations could
not find the rule its range rests on. That is review item P4-G3-R1-F4,
and this closes it.

The notation is G12.3's: `V`, `K`, `A[k]`, `B[k]`, `R[k]`, the
displacement `E`, the population spread `s` of the ladder's own values
and the operation order all carry the meanings fixed there. The formula
bounded is the profiler's own — the average FOURTH deviation over the
FOURTH power of the POPULATION standard deviation. It is undefined for
`K < 4`, matching the contract's Q16; where the published field is null
the twin owes nothing and the fact is not measured.

**The range every sample lies in.** Whatever `K` values a column holds,

```
1   <=   kurtosis   <=   K - 2 + 1 / (K - 1)
```

the top reached exactly when one value stands apart from `K - 1` equal
ones. The published bound is always intersected with this, so it is
finite on both sides for every column — including one whose spread
window reaches zero, where the quotient alone would not be.

**The quotient.** The spread moves by at most `E`, exactly as in
G12.3, so with `s` the population spread of the ladder's own values
`R`, as there:

```
S_low  = max(0, s - E)          S_high = s + E
```

and, writing `m_low` and `m_high` for the means of `A` and `B`,

```
below[k]    = A[k] - m_high
above[k]    = B[k] - m_low
nearest[k]  = below[k]         if below[k] > 0
              -above[k]        if above[k] < 0
              0                otherwise
furthest[k] = max(-below[k], above[k], 0)
```

```
(1/K) * sum (nearest[k]  / S_high)^4   <=   kurtosis(V)
kurtosis(V)   <=   (1/K) * sum (furthest[k] / S_low )^4
```

in G12.3's order: `m_low` and `m_high` are `mean(A)` and `mean(B)`;
each ratio `r` is raised as `r * r * r * r`; the terms are added by
`fsum` and the sum is divided by `K` after (residual R-P4-61).

**THE FOURTH POWER DOES NOT KEEP THE ORDER, and that is the one place
this differs from the cube of G12.3.** Cubing a window's two ends
leaves them the ends. Raising them to the fourth does not, because a
window that STRADDLES the mean has its smallest fourth power in the
middle and not at either end. So the low end of a rank's contribution
is zero wherever its window straddles the mean, which is what
`nearest[k]` says, and the high end is the further of the two ends.

**Each deviation is divided by the spread BEFORE it is raised**, and
that ordering is part of the method rather than an implementation
detail. Raising first and dividing after is the same number in exact
arithmetic and NOT the same computation in binary64: an ordinary column
of a hundred values around `1e79` has deviations whose fourth power is
not a number the format holds, and an implementation that raised first
could not produce a bound at all.

**The spread enters to the FOURTH power** and not the second — the
skewness divides an average cubed deviation by the spread cubed, and
this divides an average fourth deviation by the spread to the fourth.
Squaring instead puts a gaussian column's window at 107 to 298 around
a published 3, which is a bound that binds nothing.

Where `S_low` is zero, or either end is not finite, the bound is the
sample range above and nothing narrower. The two ends are ORDERED
before they are published: on a four-value column the two clamps can
cross by one unit in the last place, and a window whose low end sits
above its high end excludes the very statistic it was drawn for.

### G12.4 The bound on the nine interior datetime rungs

Let `P = n_present - n_unparsed` be the number of twin cells that read
back as a date, and `Ladder_d` the published `date_percentiles` read in
the ordinal space of G7.1. Since landing 2b.6 rank `k` of G7.3 is NOT
its own stratum, and since stage 3 the ranks the layout pins are the two
TAIL BOUNDARY ranks and the rank each PUBLISHED interior rung is
selected from, each at its published value; a BODY rank is drawn inside
the gap between the two pins either side of it, and a TAIL rank inside
its own stratum (G7.3b step 8), or at the one place its published value
gives it (G7.3c). Writing `P[k]` and `Q[k]` for the two ends of rank
`k`'s gap, the twin's own ordinals `O`, sorted, obey

```
O[m_lo] == low_tail.boundary,   O[m_hi] == high_tail.boundary,
O[k_j]  == Ladder_d rung j for every PUBLISHED rung,
and for every other rank:   P[k] - u   <=   O[k]   <=   Q[k]
```

**A pinned rank's window is a POINT.** Each published interior rung is
held to the value the description publishes rather than to a band
around its slice, which is what makes the rung check of this section
strictly stronger than the one it replaces: under the stratified
placement every interior rung landed BELOW its published value in all 54
runs it was measured over, because the interpolation floors, and the
band was wide enough to admit that. **No end is a rung any more**: both
ends of the ladder are null and the ranks they stood at are the
outermost cells of the two tails, whose window is the stratum their own
construction draws (G12.14).

where `u` is what reading a written cell back can lose: one unit for
the downward rounding of the whole-number interpolation itself, plus
59 seconds where `resolution == "datetime"` and
`time_precision == "minute"`, because such a cell carries no seconds.
A date, a month, a quarter, a second and a subsecond cell each carry
their own unit exactly and lose nothing further. On an `all_at_midnight`
column on the `local` clock `Ladder_d` and `O` are day ordinals, `u` is
one day and no 59-second term applies, whatever `time_precision` is
(G7.1, stage 2, 2026-09-14); the validator reads such a column in day
units of 86400 seconds. One on the `utc` clock is read in seconds, with
no 59-second term (landing 2b.3).

The achieved rung at percent `c` is the profiler's own selection rule
(`taxonomy._ordinal_rung`): the ordinal at sorted position
`k = floor((P - 1) * c / 100)`, SELECTED and not interpolated, because
there is no half-way point between two dates a calendar recognises. Its
two ends are that rank's own two ends above.

### G12.5 The envelope on datetime `n_distinct` and `n_distinct_folded`

**The lower end.** Two ranks whose windows of G12.4 do not overlap
cannot hold the same instant. Let `F` be the largest number of ranks
whose windows are pairwise separate — taken in one walk, since the
windows arrive in non-decreasing order of both ends: keep the first
rank, then keep each later rank whose lower end is strictly above the
last kept rank's upper end. Every cell that did not read as a date is a
counted stand-in spelled differently from every other cell of the
column (G10.4). So

```
F + n_unparsed   <=   n_distinct(twin)
```

**The upper end.** Every cell of the BODY carries an instant between
the two published tail boundaries, written at the published precision,
spelled with one of the offsets `utc_offsets` names by name (G7.4), and
with one of the marks G7.5 allocates; each cell of the two TAILS can be
a value of its own, and stage 3 counts them one by one rather than
through a range no description publishes. With `W` the number of
instants the two boundaries hold between them at that precision — days
on a column counted in days — `M` the number of named offsets, or 1 where
none is named, `S` the number of marks G7.5 writes — the named ones
and, where a pool is split, the unnamed permitted marks given a share of
it — `C` the product over the four censuses of how
a column's dates were written of how many forms each names, 1 for a
census naming none (plan P4-D137: `3/5/2024` and `03/05/2024` are two
cells of one day, and `2024-Q1` and `2024-q1` two of one quarter), `B`
one on an `iso-mixed` column whose
`all_at_midnight` is `true` on the `local` clock and that holds a whole
date, where a day can also be written bare, and nought otherwise, `R`
the two tails' `rows` added, and
`n_present` cells in the column at all:

```
n_distinct(twin)   <=   min(n_present, W * (M * S * C + B) + R + n_unparsed + G)
```

A column publishing no tails at all is its RAMP (G7.3d), and the ramp
bounds itself: it spreads its ranks evenly over `D` steps from
1970-01-01, `D` its published count of different values less its
unparsed cells, capped at `P` and at least one, so the twin's instants
are those `D` and no others. Each of them can be written in the same
`M * S * C + B` ways as a body cell, and each unparsed cell is a
stand-in of its own:

```
n_distinct(twin)   <=   min(n_present, D * (M * S * C + B) + n_unparsed + G)
```

Written as `n_present` instead -- the reading before this clause was
measured -- the envelope admitted 124 on a column whose ramp can hold
six, which is an envelope that checks nothing.

`G` is what G7.9 may buy, and it is bounded at BOTH ends. It is nought
unless the column's census leaves a permitted mark unnamed — nought, that
is, on every census holding a withheld pool, on every census naming all
its member's permitted marks, and on every member whose eleventh
character is a digit of the date. Where it is not nought it is
`census_floor(small_cell_floor) - 1`, the budget of ranks G7.9 may
spend, but the upper end is raised no further than
`n_distinct_folded`, and only where the rest of the product falls short
of that count: G7.9 stops the moment the folded count reaches the
published one, so the window reaches exactly that count and no further.
In symbols, with `P` the product of the four terms above plus
`n_unparsed`, the upper end is `P` where `n_distinct_folded <= P`, and
`min(n_distinct_folded, P + census_floor(small_cell_floor) - 1)`
otherwise. `G` is ADDED and not multiplied, because G7.9 spends RANKS
and each spent rank buys at most one more different spelling;
multiplying would promise the column a spelling of every instant under
the spare mark, which G7.9 never writes. It was added by the
absorbed-mark landing of 2026-09-21 (plan P4-D245, ledger K-2B-51):
without it a twin that met its published count of three exactly was
reported by its own generation report as landing outside a window of 2
to 2, which is the method telling the person a conforming twin
deviated.

**Adding the whole budget without the second bound was measured and is
wrong** (the review of 2026-09-21, finding 2). It widened the promise on
columns G7.9 never touches — a census naming `space` and `upper_t` over
three days went from a window of 3 to 6 to one of 3 to 16 with the
twin's bytes unchanged, so an over-count of up to ten would have been
reported as landing inside the range this method promises — and on a
census mixing `upper_t` with `lower_t` it made the generation report
print `inside` for a count `synthtwin validate` reported MISSED, the two
halves of one run contradicting each other. With the second bound the
report and the checker agree on that column: the window is 2 to 4, the
twin holds 5, and both say so.

**The VALIDATOR's window does not carry `G`** and does not need it: the
validation method's clause V6.1-A1 holds a file that matches the
published count exactly to that count whatever the window says, and
prints the window beside it for the record. A window one term wider
there could only excuse a file holding MORE different values than the
description publishes, which is a check and not a lowering — and a file
G7.9 wrote can hold more, on the case-mixed census named above, where
the pass reaches the published folded count and leaves the unfolded one
at five against a published three. That file is reported missing
`distinct.n_distinct`, which is the outcome this clause is for.

(`S` counting the pooled marks and `B` were added at landing 2b.3, and
`C` by the review of 158c811: without it 300 quarters over twelve years,
a quarter of them written `q`, published 81 different values against an
upper end of 48, and the table and its twin were both called MISSED.)

**The midnight correction to the lower end is WITHDRAWN** (landing
2b.6). A column G7.5 moves onto a midnight used to need one, because a
window of G12.4 was then the rank's own `1 / P` stratum and the move
could carry a rank straight out of it — a CET column of 2,000 values at
midnight over sixty days, faithfully written, held 61 different values
against a lower end of 981 — so `F` was taken over windows widened by a
precision step, reduced by `n_at_midnight + 18`, and floored at a second
set of windows computed from the pinned values. G12.4's window IS the
span between the pinned values now, and the move keeps every rank inside
exactly that span: it clamps each rank between the pinned ranks either
side of it, takes its nearest midnight inside those same bounds, and
steps an unchosen rank one precision unit only where that too stays
inside them. So no rank leaves its window, all three corrections compute
a weaker form of the same `F`, and stating them twice could only let the
two drift apart. `F` is the one walk, for every column.

Folding can only put two of those spellings onto one — `T` and `t`
fold together — so both ends bound `n_distinct_folded` as well. The
factor `S` was added on 2026-09-14 (plan P4-D39), when a column began
to write more than one mark. The lower end is brought down to the upper
where a description's own facts put them the wrong way round.

**This envelope need not contain the published count, and often does
not.** A column of 240 rows over 84 different dates publishes
`n_distinct = 84`, while the method above writes a value per rank and
holds far more; the envelope says what the CONSTRUCTION guarantees, and
the published count is printed beside it. Where the two disagree, the
recount of G12 names `n_distinct` as a deviation, so the reader is told
both that the published count was missed and how many different values
the twin does hold. *Amended by plan P4-D192:* the twin's cardinality is
now made exact wherever the published count lies inside this envelope
on a column G7.3's count pass applies to
(`contract.datetime_counts_reachable`), and a count the pass cannot reach
there is a deviation rather than a measurement inside a range. Outside
the envelope, and on every other column, the count stays approximated
under it.

### G12.6 The bounds on `length.mean`, `length.p50` and `words.mean`

Let `G[0], G[1], ...` be the group sizes of G9.5 step 1, `g_max` the
largest of them, and `N = n_present`. Write `lo` and `hi` for the two
groups the packing rule of G9.5 settled the published ends onto — **the
run's own pair, not group 0 and group 1** (P2-C4-F2), which for a
description the first pair already answers are the same two. G9.5
step 5 pins `G[lo]` to the smallest published value and `G[hi]` to the
largest, leaves every other group free between the two, and walks the
free groups toward the whole target `T = round(a * N)` for the
published average `a`, one character at a time, largest group first,
stopping as soon as the residual changes sign. So it overshoots by less
than the largest group it moved, and the total the column can reach at
all lies between

```
Floor = G[lo]*smallest + G[hi]*largest + (N - G[lo] - G[hi]) * smallest
Ceil  = G[lo]*smallest + G[hi]*largest + (N - G[lo] - G[hi]) * largest
```

Write `clamp(x)` for `x` brought inside `[Floor, Ceil]`.

**`length.mean`.** Nothing clamps a length after the walk, so the twin's
total written length `S` satisfies
`clamp(T - g_max) <= S <= clamp(T + g_max)`, with `Floor` and `Ceil`
formed from `length.min` and `length.max`, and the achieved average is
`S / N`.

**`words.mean`.** The same walk, and then the clamp of G9.5 step 6: a
value of `L` characters holds at most `(L + 1) // 2` words, since every
word needs a character and every gap between two words needs one too.
With `c[i] = max(1, (L[i] + 1) // 2)` over the twin's OWN written
cells, `w_lo = max(words.min, 1)`, `w_hi = max(words.max, 1)`,
`Floor` and `Ceil` formed from those two, and
`Allow = sum over cells of max(0, w_hi - c[i])`:

```
max( sum max(1, min(w_lo, c[i])),  clamp(T - g_max) - Allow )
    <=   S_words   <=
min( sum max(1, min(w_hi, c[i])),  clamp(T + g_max) )
```

The clamp can only REMOVE words, never add them, which is why it widens
the lower end by exactly `Allow` and leaves the upper end alone. Where
the two ends cross — a description whose own facts cannot both hold —
the lower end is brought down to the upper.

**`length.p50`.** Every free group starts at
`start = clamp(round(length.p50), length.min, length.max)` and the walk
moves it in ONE direction only. Its total movement is at most
`M = |T - Built| + g_max`, where
`Built = G[lo]*length.min + G[hi]*length.max + (N - G[lo] - G[hi]) * start`
is the total before the walk; and a group that moved `t` characters
spent `t` of that movement for every row it covers, so at most
`M / floor(N / 2)` characters of movement can reach the middle of the
column. With `W = ceil(M / max(1, floor(N / 2)))`:

```
start - (W where T < Built, else 0)  <=  p50(twin)  <=  start + (W where T > Built, else 0)
```

with two exceptions for the two end-carrying groups, each of which
holds the middle itself when it covers half the column: where
`2*G[lo] >= N` the lower end is `length.min`, and where `2*G[hi] >= N`
the upper end is `length.max`. Both ends are then brought inside
`[length.min, length.max]`, which every written length obeys because
those two facts are EXACT-OBSERVABLE. The achieved value is the
profiler's own `p50` — the interpolated quantile of `taxonomy._quantile`
— over the twin's own written lengths.

**These three bounds are the WALK's reach and are widened by nothing
else** (P2-C4-F2). Where no pair of end-carriers packs every published
count at the walk's own lengths, G9.5's packing rule reaches its wider
reading and lengthens a free group so that an exact count can be met —
an exact count outranks an approximated average, and that precedence is
stated there. A lengthened group can put the achieved middle length, or
the achieved average, outside the ends computed above. **SO CAN A GROUP
WHOSE LENGTH AND WORD COUNT ARE HELD FOR A PUBLISHED FORM** by G9.5
step 7, which is the same case reaching here by the other road: the
census is EXACT and these three averages are APPROXIMATED, so the
census is paid first and the walk carries what is left with the groups
no form spoke for (landing 2b.8 repair). Measured on 1,000 rows of
telephone numbers written in two conventions, whose census names one
form on 532 cells: the twin wears that form on exactly 532 cells, and
its achieved average length is 12.934 against a published 12.936 where
this window is 0.002 wide -- so the census is met to the cell and
`length.mean` is reported MISSED. **The bound is
not widened to swallow that.** The measurement is made against these
ends every run, the miss is reported as an approximated fact the twin
did not hold, and G12.1's rule that a measurement outside its own bound
is also named among the facts the twin could not meet applies unchanged.
A bound that stretched to cover whatever the construction did would
report a pass that means nothing.

### G12.7 The envelope on label `n_distinct`

G8 writes exactly one spelling for each published variant, one for each
variant the floor held back, one for each level whose variants do not
cover its own count, and one for each level held back whole. Call that
number `S`: it is fixed by the description alone, before any cell is
written. Then

```
min(S, n_distinct)   <=   n_distinct(twin)   <=   max(S, n_distinct)
```

Where `S == n_distinct` the two ends coincide, the bound is a single
number and the fact is exact — which is the ordinary case, and what the
contract means by EXACT-OBSERVABLE "where the published variants and
the withheld-variant map supply enough spellings" (contract 9.5). The
envelope is the fallback the same line names. G8.2's supply has no end
— case flips first, then trailing spaces — so a conforming generator
that reaches this fallback at all has been handed a description whose
own counts disagree, and the report prints both numbers.

### G12.8 The fallback on numeric `n_distinct` and `n_distinct_folded`

For `count` and `continuous` both counts are EXACT-OBSERVABLE using the
spellings owner decisions 7, 8 and 10 permit (G6.5), and the contract
sends them to the two-sided envelope only where even those cannot
supply the count. That corner is real: the whole-number rule of G5.4
can round two neighbouring strata onto one value, and where the
published map writes those cells `plain` — the one style with no
leading-zero family (G6.3) — no spelling rule brings the second
identity back.

**Both ends are measured and printed on every run** (P2-C2-F4).
Revision 1 wrote the lower end as "the count the finished cells hold",
which is the achieved value itself: an envelope no twin can leave, and
a fact whose range the report never printed at all. It is replaced by
the column's own SUPPLY — how many different spellings the finished
cells are capable of carrying, which is a statement about the
construction and not a second reading of the output:

```
supply = for each (value, style) group of the numbers class:
             1                      where the style is `plain`
             1                      where the style is `leading_zero`
                                    AND `pad_widths` names that cell's
                                    field width, the family being spent
                                    by the width (G6.3)
             the group's cell count otherwise, since every other style
                                    carries the leading-zero family
       + for each other class:
             min(its cell count, its share of the budget in G6.5)

min(supply, n_distinct)  <=  n_distinct(twin)  <=  max(supply, n_distinct)
```

and the same over the folded identities for `n_distinct_folded`. Where
`supply` reaches the published count the two ends meet on it, the bound
is a single number and the fact is exact — the ordinary case, and what
the contract's EXACT-OBSERVABLE means here. Where it does not, the
printed range says how far the count could fall, and the report names
the published count beside the achieved one under the recount of G12 as
well. The bound is able to fail: a twin that wrote one spelling where
its own cells could have carried two lands outside it.

### G12.9 The envelope on a joined column's rank agreement

`part_agreements` is APPROXIMATED, and until this section existed the
window it is approximated inside was written **only in a plan**
(P4-D25). Every other envelope of this method is stated here and cited
here; that one was cited as `docs/plans/phase-4-columns.md`, so an
implementer working from the specification alone could not know how
close a twin has to come, and a reader of a quality report could not
find the rule the verdict rests on. That is residual R-P4-42, and this
closes it.

**The window.** For EVERY pair of positions -- and until landing L7
this section reached only the pairs the walk moved, which is the last
paragraph's own subject -- the twin's own rank agreement must lie
within **0.02** of the published value, two-sided:

```
|agreement(twin) - part_agreements[pair]|  <=  0.02
```

**THE COMPARISON IS INCLUSIVE AND THE SUBTRACTION ROUNDS**, so both
ends of that window are widened one place outward before anything is
compared against them, exactly as G12.3's limits are (review item
P4-G6-R7-F1). On a published agreement of `0.2487` the lower end
`published - 0.02` comes out `0.22870000000000001` in binary64, so a
file agreeing at exactly `0.2287` -- which this rule admits, the
comparison being `<=` -- was reported MISSED against it. Widening
outward admits exactly what the rule admits and nothing else.


Both sides are measured at the precision the description PUBLISHES the
agreement at, which is four decimal places. A twin measured raw can sit
outside a window that the same twin, re-described, sits inside -- an
agreement of `0.020018` against a published `0.0` is one such -- and a
fact cannot be inside its window for one command and outside it for
another.

`part_above` beside it carries NO window. It is a count of rows and the
walk of G6B.4 weights one row of it above the whole agreement, so a
twin either holds it or has missed it.

**AND THE PRECEDENCE IS HELD UP BY THE ACCEPTANCE RULE, NOT BY THE
WEIGHT.** A weight is a term in a sum, and a sum could not tell one
above-count being sold from another being bought at the same price —
which is how a twin came out having traded one for another with that
weight already at a whole unit per row. G6B.4 step 5's first
refusal is what holds this sentence up: a pair holding its published
count never stops holding it.

**Why a window and not an exactness.** The pairing is chosen by a
bounded search (G6B.4), and published facts pull against each other
inside it: every pair's agreement, every pair's above-count, and how
many different whole CELLS the pairing makes. The search stops at
`0.0005` of its own combined distance or at its try ceiling of
`200 * n_joined`, whichever comes first, and on a column whose targets
conflict it stops at the ceiling with an agreement short. Measured on a
400-row two-position column published at 0.9613, the twin reached
0.8994.

**What the window does NOT promise, and this paragraph replaces the one
that stood here.** Until landing L7 the walk moved only the last
position, so a pair between two EARLIER positions of a three-or-more
position cell was neither moved nor scored, could come out at `+1`
against a published `-1`, and was not an approximation of anything —
this envelope expressly did not reach it (residual R-P4-51). The walk
now moves every position but the first, so every pair is aimed at and
every pair takes this window.

Aiming at a pair is not reaching it. A column of three or four
positions sets three or six agreement targets that pull against each
other inside one bounded search: measured over 2,160 pairs of a
twelve-column battery at forty seeds, **665 landed outside this
window**, against 1,560 before. Those are MISSES, reported as misses on both pages
with the achieved value beside the published one — the same verdict a
two-position column's miss gets, which the second paragraph above
already measured at 0.06 outside. What is gone is the class of pair no
term of the distance ever looked at.

### G12.10 The envelope on a clock column's interior rungs

`clock_percentiles` is APPROXIMATED and its bound was cited as "G12.9"
from the day the clock role landed — a section that did not exist then,
and that when it was later written turned out to be about something
else entirely. So a reader who followed the citation first found
nothing and then found a rule about rank agreement between the
positions of a joined column, with a window of `0.02` that means
nothing for a time of day. That is review item P4-G3-R1-F5, and this
section and G12.11 close it.

**THIS IS A WINDOW ON THE FILE'S OWN RUNG AND NOT A MARGIN AROUND THE
PUBLISHED VALUE.** It is the same shape as G12.4's for dates, in this
role's own space: whole-number arithmetic throughout, in the ordinal
unit the published `clock_form` sets — minutes of the day where the
form is the one without seconds, seconds of the day otherwise. The unit
matters and is not a presentation choice: the construction interpolates
and FLOORS in that unit, and a window drawn in seconds around a
minute-form column lands part way through a minute the construction
cannot write.

Let `P = n_present - n_unparsed` be the number of cells that read back
as clock times, `Ladder` the published eleven rungs converted to
ordinals, and `Ladder(r, P)` its interpolation at rank `r` of `P`. Then
rank `r` of the twin, read back and converted to ordinals, satisfies

```
r < m_lo or r > m_hi :  the rank's own stratum (G12.14), or its one
                        published value (G7.3c)
r = m_lo             :  ordinal = low_tail.boundary
r = m_hi             :  ordinal = high_tail.boundary
otherwise            :  Knots(r) - 1  <=  ordinal  <=  Knots(r + 1)
```

where `Knots` is G7A.4's own reading between the knots, and the upper
end is never above the high boundary. *Amended at stage 3: the two ends
are tail ranks now, and `Ladder` is the knots the two boundaries and
the published rungs make.*

The two ends are then multiplied into seconds, because the measured
side is read in the FILE's own form and the two have to meet in one
space. The first and last ranks are EXACT: the twin writes the
published ends themselves.

The lower end subtracts one whole unit because the interpolation
floors, so a value the construction writes for rank `r` can sit one
unit below the un-floored ladder value there. The upper end is the
ladder at rank `r + 1` because the construction never writes a value
for rank `r` above the value it would write for the rank after it.

**AND ON A COLUMN WHOSE VALUES WERE ALL DIFFERENT, BOTH ENDS GO THROUGH
THE STEP-AND-CLAMP** (*added by the dates pass of the stage-3 review,
item 9*). G7A.4's all-different repair leaves no body rank on the
instant the knots gave it: it keeps the instant of the rank before,
steps to that instant plus one where this rank is not above it, and
clamps to one unit below the high boundary. That walk is monotone in
each rank's own instant, so carrying the two ends of the window above
through the same walk gives the two ends of what the construction can
reach -- no wider and no narrower. Writing `lo(r)` and `hi(r)` for the
two ends above, for the body ranks in ascending order and starting both
at `low_tail.boundary`:

```
lo(r) = min(high_tail.boundary - 1, max(Knots(r) - 1,     lo(r - 1) + 1))
hi(r) = min(high_tail.boundary - 1, max(Knots(r + 1),     hi(r - 1) + 1))
```

Without it the window is the interpolation's alone, which is NARROWER
than the construction: measured on every minute of a day, 1,440 rows at
a floor of eleven, seeds 0 and 1 reproduce the real column's whole
multiset and its p99 rung stands at `23:44`, where the interpolation's
window ends at `23:43`. The twin's report named that rung as a fact the
twin had not held, printing "the description says 23:44; the twin holds
23:44 ... OUTSIDE the range"; on the other side of the wall only the
equality reading of V6.1-A1 kept the quality report from saying the
same. Both reports draw this window, so both carry the walk.

### G12.11 The envelope on a clock column's two distinctness counts

The same two ends the date role's envelope has (G12.5), in this role's
ordinal space, and it carries the same citation defect this section
closes with G12.10.

```
separate  =  how many of the P rank windows of G12.10 pairwise fail to overlap
room      =  latest - earliest + 1        (in the form's own ordinal unit)

lower  =  min(separate + n_unparsed, upper)
upper  =  min(n_present, room + n_unparsed)
```

The LOWER end counts ranks whose windows do not overlap — two ranks
that cannot hold the same time are two identities the twin must
carry — plus every stand-in, each spelled differently from every other
cell. The UPPER end is how many different times the published range
holds at all, plus those stand-ins, and never more than the column has
cells.

**IT NEED NOT CONTAIN THE PUBLISHED COUNT, and on an ordinary column it
does not.** A column of two hundred and forty rows over a hundred and
twenty different times publishes a hundred and twenty, while the
construction writes a value per RANK and so tends to hold more. That is
what an explicit cardinality bound is for, and it is why this role's
two distinctness counts are approximated rather than exact: a bound
that had to contain the published value would be a promise the
construction cannot keep.

### G12.12 The window on the scale of the held-back numbers

The one aggregate contract section 6.3.3 publishes over a column's
pooled numbers — their mean `mu` — is APPROXIMATED, and this is the
window it is met inside. Method G8.3c places the twin's made-up numbers
on it and then rounds each value onto a place the column writes at, so
the twin's own pool comes back NEAR `mu` rather than on it.

```
places  is the FEWEST decimal places any number this column publishes
        was written with, and nought where it publishes none: the
        coarsest grid the ladder of G8.3a can reach, and so the
        coarsest a pooled placement can be rounded onto

window  is  2 * 10 ** -places                (taxonomy.pooled_window)

mean    is met where   |mean(pool of the file) - mu|  <=  window
```

**THERE WERE TWO OBLIGATIONS HERE AND NOW THERE IS ONE.** The pool used
to publish its population spread beside its mean, and this section drew
both windows from that spread. The owner's decision of 2026-09-21
withdrew the spread, for the reason contract 6.3.3 states: a mean and a
spread together solve a tightly spaced pool for its own values. **SO
NOTHING IN THIS METHOD NOW CHECKS HOW FAR APART A FILE'S HELD-BACK
NUMBERS LIE.** A file whose pool sits at the published average and is
spread a tenth as wide as the real column's meets every obligation this
method states, and meets them honestly, because no published fact was
missed. The twin's own pooled spread is the generator's own choice of
spacing (G8.3c step 2) and a fact about no table; the held-back note of
the generation report is where a person is told so.

**THE WIDTH IS COUNTED IN PLACES OF THE COLUMN'S OWN GRID**, because
the grid is what decides how exactly a placement can meet a mean, and
it is MEASURED rather than chosen. G8.3c step 4 makes the pool's groups
carry each other's arrears, so every group but the last is asked for
whatever the cells still to be written must average for the pool to
come out on `mu`, and the only error left over is the LAST group's own
rounding. Over 371 pools that publish a scale and whose twin publishes
one back — the shape ledger K-2B-50 names, its loose cousin, a decimal
pool, an unanchored pool of readings, the ten shapes of this landing's
before-and-after table, and four draws of 150 randomised pools at four
widths, two grids, both signs and mixed grids — the furthest a
conforming twin's own pooled mean stood from the published one was A
THIRD OF ONE PLACE. The window is TWO places, six times the worst
measured. The defect ledger K-2B-50 names stands at a hundred and four
and a half places: the twin without G8.3c's placement puts a pool
published at 204.5 at 100, on a column of whole numbers whose window is
therefore 2.

**IT WAS A SHARE OF A MAGNITUDE AND THAT WAS WORSE THAN NOTHING.** For
one landing this window was a fifth of the largest magnitude the
column's description stated — the largest of its published numbers, or
`|mu|` where it published none. A column's published number has nothing
to do with its pool: measured on 100 `alpha`, twenty `990` and ten each
of 940 to 949 at a floor of eleven, the published `990` drew a window of
198.0 around a pooled mean of 944.5, and the very defect this section
exists to catch — G8.3c's placement withdrawn, the twin's pool back at
990.0, its numeric mean 990.000 against the table's 952.083 — passed
inside it and the file exited clean. It does not now.

**A COLUMN THAT PUBLISHES NO NUMBER is read as whole numbers**, which
is the coarsest grid there is and so the widest this window ever
becomes; an unanchored ladder ends on that same grid. The window is
never nought, so no file is held to a check of no width.

**THE FILE'S OWN POOL IS WHAT IS MEASURED, and a file that publishes
none closes the gate**: the obligation is WITHHELD, as every other
check of this kind reads a re-described block that says nothing.

**THAT GATE USED TO CLOSE ON EVERY TWIN THIS PRODUCT WROTE, and does
not now.** While the pool published a spread, the producer refused any
pool packed as closely as its own values allow — such a pool is NAMED
by its mean and its spread — and G8.3c spaced the twin's groups evenly,
which is exactly that arrangement. So a twin's own description
published no pool, both obligations were withheld on every file, and
this section said so rather than pretending otherwise. A mean names no
arrangement, tight or loose, so the producer's rules let a twin's own
description publish its pool and the comparison happens. Measured on the
shape ledger K-2B-50 names: the twin's own re-described block publishes
a hundred pooled cells at a mean of 204.5, and the twin built without
the placement publishes a hundred at 100 and is MISSED.

### G12.13 The window on the tail facts (stage 3, plan P4-D344)

For one side, with `K` the numbers, `g` the widest stratum both reports
read (`_window_stratum`), `d = (g + 2) / K` and the half unit of G12.2:
every twin cell at rank `i` lies in

```
[lo_i, hi_i] = [Ladder(i / (K - 1) - d) - half, Ladder(i / (K - 1) + d) + half]
```

(G5.6's rank form, read through the tail ladder of G5.1a), and the twin's
own boundary rung -- a type-7 reading at `h = (K - 1) P / 100` -- lies
between `lo` at rank `floor(h)` and `hi` at rank `ceil(h)`. Each tail row's
distance from that boundary is therefore at least the gap between the
nearer two ends (held at nought) and at most the gap between the further
two, so

```
mean_distance' in [ (1/m) sum near_i , (1/m) sum far_i ]
rms_distance'  in [ sqrt((1/m) sum near_i**2) , sqrt((1/m) sum far_i**2) ]
```

summed with `fsum`. It is a statement about the construction, never a
tolerance; HELD where the file's number equals the published one
(V6.1-A1). The file's tail is read AT THE PUBLISHED PERCENT: a file of the
published count has its tail there, and one whose own tail stands
elsewhere has its distances withheld rather than compared at another
percent. Its power is limited exactly as G12.2's and G12.3's are at a
raised floor, because the widest stratum is read off the floor where the
mode is withheld; the skeptic's straight-line mutant (a twin whose tail
reach is 70 per cent too long) is inside it at 5,000 rows, as it is
inside G12.3's spread window.

A LISTED tail's `values` are EXACT: the file's own tail at that percent
lists the same values, or -- where the list is short enough
(`TAIL_VALUES_MOST`, six) that a file holding those values would list
them -- the file misses.

### G12.14 The window on a date or clock tail's two distances

*Stage 3, plan P4-D328.* `mean_distance` and `rms_distance` are
APPROXIMATED facts (contract section 9), and this is the two-sided bound
G12.1 obliges them. It is a statement about the CONSTRUCTION and never a
tolerance around the published number.

Run G7.3b's construction twice over the tail's `m` ranks: once with
every drawn rank's word at NOUGHT and once with every one at
`2**64 - 1`, each pass carried through the rounding, the tie group, the
step off a hole, the move onto a midnight, the monotone fix, the
all-different step and the clamp to the edge. Call the two whole
distances of rank `i` `near[i]` and `far[i]`. Every step of the
construction is monotone in every word, so a twin built by it has each
rank's distance between those two, and

```
sum(near) / m   <=   mean(twin)   <=   sum(far) / m
sqrt(sum(near[i]**2) / m)  <=  rms(twin)  <=  sqrt(sum(far[i]**2) / m)
```

measured over the twin's cells lying strictly beyond the PUBLISHED
boundary, in the published tail unit. The comparison is made in whole
numbers -- the file's own sum against `sum(near)` and `sum(far)` scaled
by the counts -- so no rounding decides a verdict, and the file's value
is HELD where it rounds to the published one (validation method V6.1-A1).
A tail that publishes its values (G7.3c) owes its mean EXACTLY, because
every rank stands at a published value and the counts are solved to
reach it.

**Where the window does not cover the published value.** The window
certifies that the twin was built by the construction, not that it
reproduced the published fact, and on a tail spanning few whole units
the rounding of each rank can carry the whole tail's mean outside it:
measured over the design's battery, all but one of its published values
lie inside their own window, the exception being a tail of quarters
whose mean distance is 2. Such a tail publishes its values instead since
P4-D329, which removes most of that population; what is left is the
V6.1-A1 pattern, where the real table passes by exact equality and the
report says the window does not reach the value.

## G13. Residuals this method carries

- **R-P2-1 — CLOSED in revision 4, and its remaining deviation
  narrowed almost to nothing in revision 5.** Unrepresentable values
  publish `min_length` and `max_length`, and the twin carries both ends
  where the column's own shapes can be written at them (G10.5). The
  invented 400-digit canonical width this residual was opened for is
  gone. What remains is not a residual but a named deviation: where a
  shape's own floor is wider than the published width, the twin writes
  the floor and the report says the published width was not held.
  **Revision 4 measured that floor against the digit-string family
  alone — 310 characters for a value too large to hold, 327 for one
  too small — and revision 5's exponent family brings it down to five
  and six**, so a column of `1e400` is now written at the width it
  publishes instead of sixty times wider. The deviation survives only
  for a published width of four characters or fewer, which no
  out-of-range cell a real table holds can have.
- **R-P2-2** — absent-value spellings and classes are not reproduced.
- **R-P2-7 — RETIRED 2026-09-15** (landing 2b.6). While it stood it
  read: the twin keeps a datetime column's precision and offset state
  but not the source's lexical date family, a month-first table yields
  ISO twin dates, and `format` is not reproduced for that reason. The
  owner reversed decision 5, the cell is written through the member
  that read the real column, and `format` is EXACT-OBSERVABLE. What is
  NOT retired with it is named in its place: the figures after a second
  are still zeros, and a spelling no member of the reader reaches at
  all still falls to free text.
- **R-P2-9** — twin numeric cells may carry several spellings of one
  value from the leading-zero family, so a twin column can look less
  tidy than a table whose numbers were written one way. The inferred
  column type is preserved, which the decimal-point form of decision 7
  would not have done.
- **R-P2-13 (new here)** — a generated numeric value can land on one of
  the three numbers the profiler treats as stand-ins for "no value"
  (`-9999`, `-999`, `9999`) and be read as missing when the twin is
  re-profiled, exactly as the real column's own cells were. The method
  does not steer values away from them, because distorting a
  distribution to protect a re-profiling artifact is the worse trade.
  `sentinel_verdicts` is REPORT-ONLY and the report names the column.
- **R-P2-14 (new here, review item P2-C3-F1)** — the packing of G9.5
  runs to its own end and nothing stops it early, so a contract-valid
  document nobody produced could take a long time to generate. This is
  a cost in TIME and never in exactness: no published count is traded
  to make the walk stop, which is what the withdrawn work ceiling did
  on a description the producer emits. It is the same trade plan P2-D2
  made when it refused a size cap on the description, and it is
  recorded here rather than paid for silently.

## G14. The frozen reference vectors

### G14.1 What the oracle is, and what it may not import

The vectors are computed by a tool under `tools/reference/`, importing
nothing from `src/` — the same rule the Phase 1 numeric vectors follow,
for the same reason: a value recomputed beside the code it checks can
drift with it.

**The oracle computes twin values as a pure function of GIVEN uint64
words.** The words are inputs of the vector file, written out in the
file itself, not drawn by the oracle. The oracle therefore contains no
generator, no seed handling and no library random operation of any kind.

**The oracle may not import numpy**, and the reason is mechanical rather
than stylistic: the data-provenance guard runs every fixture generator
under an audit hook that refuses `ctypes` — and numpy imports `ctypes`,
so a generator that imported numpy would be stopped by the guard before
it wrote a byte. This is stated here because it is the constraint that
shapes the whole vector design: the transform from words to bytes is
what the vectors freeze, and the word stream itself is bound separately
by a golden twin hash computed in CI against the locked numpy.

Exact quantities are computed in integer or rational arithmetic
(`fractions.Fraction` and Python integers), and each published binary64
is proved correctly rounded by midpoint comparison against its two
neighbours, ties to the even significand — the proof shape the Phase 1
vector tool already uses, including its two hand-checked boundaries (the
point where binary64 rounds to an infinity, and the sign of a zero). The
tool walks the exact serialized tree it writes, tuples included
(P1-R8-F3's blind spot), and carries a full-generator mutant that must
fail.

### G14.2 The vector file shape

**Six committed JSON files, and ONE oracle** (review item P2-C3-F3).
How many cases each file holds is counted once, in G14.3, off the files
themselves; the growth list below says which cases went where and when.
`tests/reference/generation-reference-vectors.json` carries the nine
cases G14.3 names first, with the four the review of 158c811 added and
the two its skeptic added (plan P4-D138), and
`tests/reference/generation-branch-vectors.json` carries the twenty it
names after them (five, until owner decision 11 added the
pooled-spelling case; then the month-span case of plan P4-D4.3,
then the long-tail, clock, affixed and joined cases of residual
R-P4-17, then the exponent case of G10.5 revision 5, and then the
midnight-day and mixed-mark cases of plan P4-D39, then the
mixed-convention case of landing 2b.7, and then the five cases of landing
2b.18), and
`tests/reference/generation-branch-vectors-2.json` carries the sixteen
it names last, the cases the carried landings 2b.4, 2b.3 and 2b.2 added,
less the one landing 2b.6 withdrew with the rule it pinned,
and `tests/reference/generation-document-vectors.json` carries the five
landing 2b.17 added for the transforms that produce a WHOLE DOCUMENT
rather than one column's cells, the three the files review of
2026-09-18 and its two repair passes added, and the one the landing
that closed the withheld date census added (plan P4-D291), and
`tests/reference/generation-branch-vectors-3.json` carries the seven the
repair of the final Codex review of the number censuses added (plans
P4-D142, P4-D145 and its amendment, P4-D147 and P4-D149), through the entry point
`tools/reference/make_generation_branch_vectors_3.py`, because the second
and third files each stand within a few kilobytes of the byte cap -- and
beside them the layout packing of plan P4-D182, the one case of the
carried items' repair that fit -- and
`tests/reference/generation-branch-vectors-4.json` carries the four that
repair added for G6.5a and the census of marks (plans P4-D176, P4-D178,
P4-D183 and P4-D185), through the entry point
`tools/reference/make_generation_branch_vectors_4.py`, because the fifth
file then stood within four kilobytes of the cap -- and
`tests/reference/generation-branch-vectors-5.json` carries the cases
the final pass over the close of stage 2 added -- a whole number written
two ways (plan P4-D193), the census of marks on a column with refunds
(plan P4-D194), a declared identifier's partners held to its unnamed
cells (plan P4-D196) and a workbook column's truth values (plan P4-D198)
-- through the entry
point `tools/reference/make_generation_branch_vectors_5.py`, because the
sixth file then stood within a few kilobytes of the cap -- and
`tests/reference/generation-branch-vectors-6.json` carries the seven the
extra review round of 2026-09-18 added, the five of its date pass (plans
P4-D254 to P4-D258) and the two of its number pass, G6.5a's last resort
on the REPRESENTABLE grid (plan P4-D269) and G6.5's visiting order for
the distinct-spelling repair (plan P4-D265), through the entry point
`tools/reference/make_generation_branch_vectors_6.py` -- and
`tests/reference/generation-branch-vectors-7.json` carries the six the
carried numbers pass of 2026-09-18 and its repair pass of 2026-09-19
added, G6.5a's band fill, the published mode's own stratum, G8.3a's
dressing and anchors, G6.5a's push of a collision the walks leave and its
column-wide fill on a column where the band fill and the push both stand
aside, through the entry point
`tools/reference/make_generation_branch_vectors_7.py`, because the eighth
file's output had passed the 200000 bytes plan P4-D295 sets for opening
the next entry point, and beside the carried date items and the readings
of an absorbed count it would have passed the cap. **That eighth file
is where the round's two branches MET.** Each built its own cases into
the seventh, and merged they took it to 276235 bytes against the cap, so
the seven moved together into a file of their own and the seventh kept
the six it held before the round, every cell of them unmoved. No case was
dropped, no proof was shortened and the cap was not raised. This sentence carried the
count `six` while the file held seven, which is the same drift G14.3's
own warning is about, and it is written here as a growth list so the
next case has an obvious place to be recorded. All nine are written by
`tools/reference/make_generation_reference_vectors.py` — the second
through the entry point `tools/reference/make_generation_branch_vectors.py`,
the third through `tools/reference/make_generation_branch_vectors_2.py`,
the fourth through `tools/reference/make_generation_document_vectors.py`,
the fifth through `tools/reference/make_generation_branch_vectors_3.py`,
the sixth through `tools/reference/make_generation_branch_vectors_4.py`,
the seventh through `tools/reference/make_generation_branch_vectors_5.py`,
the eighth through `tools/reference/make_generation_branch_vectors_6.py`
and the ninth through `tools/reference/make_generation_branch_vectors_7.py`,
each of which runs that oracle and asks it for its own case set — so there
is one transform, one proof layer and one set of rules behind every file.
Each is registered in `tools/provenance/fixture-manifest.json` with its
`seed` (`0`, accepted and ignored — these vectors are a fixed transform,
not a random sample), its `sha256`, and a justification, and each is
rebuilt and byte-compared in CI.

**Why two files rather than one.** Each file must stay under the
manifest's 100000-byte fixture limit, and the two case sets together
carry about 123000 bytes. Splitting them is the one thing that must NOT
be done by dropping a case or shortening a proof: the limit is a rule
about a committed file, and the case list of G14.3 is a rule about
coverage. A third file follows the same rule the moment the second
approaches the limit, and a fourth the moment the third does, which
landing 2b.17 reached. Two copies of the oracle would not, and are
forbidden here: a proof layer that exists twice can be repaired once.

**The third file** (the integration of landings 2b.1 to 2b.5,
2026-09-15). The manifest's cap is 250000 bytes today. The second file
held 171111 bytes with its fourteen cases, and the twelve the carried
landings 2b.4, 2b.3 and 2b.2 added would have taken it above 300000, so
it was split as the paragraph above requires: no case was dropped, no
proof was shortened and the cap was not raised. The fourteen stay where
they were, and the twelve are the third file, at 141003 bytes. Five more
cases then froze the marks and notations of a negative landing 2b.2 had
left to round trips for want of room, at eleven rows each, because at
twenty-two rows the five carried the file 873 bytes past the cap. The
third file held 245567 bytes with seventeen cases, which left no room
for another of that size. Landing 2b.6 withdrew `accidental_midnight`
with the nought it pinned, so it holds sixteen cases and — once landing
2b.6 rewrote the one slashed stamp among them in that member's own form
and gave every block of dates its four written-form censuses — 240399
bytes, still under the cap, which was not raised;
that is room bought by a rule going away, not by shortening a proof, and
the next case of the usual size still opens a fourth file.

**The fourth file** (landing 2b.17). It is the one the sentence above
predicted, opened for the reason that sentence gives: the third file
has no room. It carries the five DOCUMENT cases — the written form of a
delimited file, the arrangement of its rows, the twin of a workbook,
the shape a line before the table is published as, and the reading that
settles which delimiter a file is written with. Those five transforms
had reached the twin's bytes with NO second implementation of any kind:
landings 2b.9, 2b.10 and 2b.11 built them, each recorded the gap, and
none could close it — because the workbook writer's rules were stated
in no specification at all, and a rule that is not stated cannot be
implemented a second time FROM ITS STATEMENT. G2.2 was written first,
at this landing, for exactly that reason.

**A document case is a different shape, and the shape is the point.**
It carries no `column`, no `words` and no `word_budget`, because none
of these transforms reads a column's published facts or draws a single
word. What it carries instead is the description's own `source.dialect`
or `source.workbook` block — the input each transform really takes —
and the bytes that come out: the file's lines and its whole text, the
arranged rows, the runs published for the lines before a table beside
the lines the twin writes for them, the reading each candidate
delimiter reaches, or every part of a workbook package. The workbook's
parts are frozen as TEXT and never as the packed bytes, because the
compressed stream differs between library builds, which G2.2 states as
a limit rather than claiming past it.

**WHERE THE SECOND WRITING IS INDEPENDENT, AND WHERE IT IS NOT.** This
section's rule is that each transform is written from the rule's
STATEMENT and not from the code, because a second writing copied from
the implementation agrees with it by construction and cannot disagree
with it, which is the one thing these vectors exist to do. Landing
2b.17's review measured the document transforms against that rule and
found it half kept, so the measurement and its result are recorded
here rather than left for the next reader to rediscover.

Normalise every function of the oracle — docstrings, comments and
annotations dropped — and score it against its closest normalised
function in `src/synthtwin`. The transforms added for the document
cases scored far higher against the shipped code than the oracle's
own earlier work does, and two of them reproduced arithmetic that no
governing document stated at all: the placement of the records holding
nothing (G2.1) and the spread of the rarer line endings (G2). Those
two sentences said only "spread evenly", which does not decide a
single row or line, so the mirror could not have come from them.

Both rules are now STATED — in G2.1 and in G2's line-ending row — and
the two walks were rewritten from those statements, which moved no
committed byte. No committed case publishes counted line endings, so
the second of the two is held by no frozen byte: the review's repair
compared it with the shipped spread over twenty thousand drawn
censuses instead, and the placement over twenty thousand drawn grids,
and both agreed on every one. That comparison is a measurement taken
once and is not a vector; a case publishing counted endings is owed
the day a file has room for it.

What remains close to the shipped code is named here rather than
summed up. Measured after the rewriting, 13 of the 53 added transforms
of six statements or more score 0.60 or above (17 before it), against
a median of 0.41. Nine of the thirteen write the workbook package: the
cell element, the escaping of text, the spelling of a boolean, the
hidden states, the styles part, the defined table, the content types,
the place of a shared string and the class of each cell. The file
format fixes most of those bytes, so an element writer and its mirror
converge however each was written. The other four are short rules
whose statement leaves one natural writing: the joining of fields
with the delimiter, the letters of a column, the share of records at
the commonest width, and whether a sheet's name is one synthtwin's own
vocabulary can rebuild. A reader should take the placement and the
spread as independently written, the delimiter reading, the written
form, the marks of the lines before a table and the arrangement's sort
as written from G2, G2.1 and FD11, and the part-emitting code of G2.2
as written against the shipped writer and stated afterwards. The
frozen cases hold all of them to the same bytes; only the first kinds
can find a defect in the rule they mirror.

Serialization: `json.dumps(document, indent=2, sort_keys=True,
allow_nan=False)` plus a terminal newline — the same canonical form the
Phase 1 vectors use, so a reviewer reads one shape and not two.

```
{
  "what":          one sentence naming this as the generation oracle
  "generated_by":  "tools/reference/make_generation_reference_vectors.py"
  "case_set":      which of the three case sets this file carries, and where
                   the other two live, so neither file can be read as the
                   whole of the oracle
  "never_imports": ["synthtwin", "numpy", "pandas"]
  "method":        "docs/spec/generation-method-v1.md"
  "method_revision": 1
  "word_source":   a sentence saying the words below are INPUTS, that the
                   oracle draws nothing, and that the word stream itself
                   is bound by the golden twin hash and not by this file
  "definitions":   one entry per named transform of this document, each
                   stating the rule and the section that fixes it:
                     bounded, permutation, stratum_layout, ladder_segment,
                     convex_interpolation, integer_rule, class_repair,
                     canonical_spelling, style_allocation,
                     ordinal_transform, precision_form, endpoint_fields,
                     offset_form, grid_packing, partner_family,
                     notation_reading, separator_allocation, and, for the
                     document cases of the fourth file, written_form,
                     row_arrangement, workbook_sheet, writable_mark,
                     best_reading
  "cases": {
     "<case name>": {
        "why":            what this case exists to pin
        "column":         the published facts the case supplies, key by
                          key, in the profile's own wire shape
        "words":          the uint64 words the case is given, as decimal
                          strings, in consumption order
        "word_budget":    {"content": n, "placement": m} — the counts
                          this document's G4.3 predicts, so a mismatch is
                          a failure rather than a silent re-alignment
        "content":        the content list before placement, as exact
                          cell text
        "cells":          the written column, as exact cell text, in row
                          order after placement
        "csv_bytes":      the exact bytes of the column's own field of
                          each row, as a JSON string with the LF endings
                          written out
        "float64":        for every interior numeric value: the exact
                          rational it stands for, its correctly rounded
                          binary64, and the proof shape used
     }
  }
}
```

Every number in the file is either inside a `float64` wrapper carrying
its exact value, or a whole number at a path the tool's own list of
whole-number fields names. A number reaching the document with no exact
value recorded beside it stops the run, so "every published float is
proved" cannot quietly stop being true when a field is added.

### G14.3 The required cases

The four the plan names (P2-D7), five more this method's own mechanisms
need, five more for the branches those nine leave unexercised (four at
review item P2-C4-C3 and one at owner decision 11, review
item P2-C3-F3), and one more for the published end the ordinal space
cannot hold (review item P2-C4-C3), and the pooled remainder written by
its own value beside a whole number wider than the fixed-point window
(owner decision 11), and one for the second SPAN resolution when it was
added (plan P4-D4.3 item 2), and four for the four roles Phase 4 added
(residual R-P4-17, now closed), and one for the second spelling family
of G10.5 when revision 5 added it (residuals R-P4-48 and R-P4-68), and
two for the mark between a moment's day and its clock and the day unit
of a column at midnight (plan P4-D39), and one for the class debt of a
column of labels (G8.3a, landing 2b.4), and one for what the census
could hold beside the places a made-up number may take (G8.3a, landing
2b.4's repair), and five for the withheld pool of marks, a slashed
stamp's one permitted mark, bare dates beside midnight moments, the move
onto midnight and midnight on two offsets (G7.1, G7.4 and G7.5, landing
2b.3), and two for the ranks whose instant the published tail fixes and
the move off an accidental value at midnight (landing 2b.3's repair), and
three for the spellings of a number landing 2b.2 publishes (plan P4-D41),
and five for the marks and notations of a negative those three left
unfrozen (plan P4-D41, frozen at the integration of landings 2b.1 to
2b.5), and one for the two mixed-convention censuses of a column's
negative notations and thousands marks (landing 2b.7, plan P4-D65.2),
and one for the LAYOUT of a record number (contract section
7.12, landing 2b.18), whose three identifier cases all publish an empty
census, so the whole layout rule could have been withdrawn with every
committed byte unchanged, and three for the lower-case key of a form
census, the shape a stand-in owed no form takes, and the census of
spellings of a count column (landing 2b.18 part 2), which no earlier
case reaches, and one for a layout census's zero fill two noughts deep,
its interior space and the mixes that write its pool (landing 2b.18's
repair pass), which `identifier_layout` reaches none of, and four for
the places of G7.3's pins, the classes of width, the `either` length of
a name of May and the reservation of a named form's least (the review of
158c811, plans P4-D130, P4-D132 and P4-D133) -- no case in any file
published a non-empty census of written forms before them, so every
allocation of G7.5 could have been withdrawn with every committed byte
unchanged -- and two for G7.3's choice of the middles and its heaps (the
skeptic of that review, plan P4-D138), which no flat case reaches -- and
five for the transforms that produce a WHOLE DOCUMENT rather than
one column's cells, which landings 2b.9, 2b.10 and 2b.11 left with no
second implementation of any kind (landing 2b.17), and one more for the
rules of G2.2 the files review repaired -- a class handed only to a
cell it fits, a withheld census falling to the published commonest
class and code, a date cell, a blank header cell, a carriage return and
a placeholder taken whatever its case (plan P4-D164 to P4-D171), and
one for G9.6's layout packing (plan P4-D182), and four for G6.5a's walks
taken reach by reach (plan P4-D183), its fills of a saturated grid of
tenths and of a column's published levels (plans P4-D176 and P4-D178),
and the census of marks held at a thousand (plan P4-D185), and one for
the rules of G2.2 part 2 of the carried items changed -- a count spread
over the cells its class fits, and a code published as the source wrote
it and read for its kind off the code (plans P4-D187 and P4-D189), and
one for the numbers of a free-text column carrying what the walk of
G9.5 step 5 could not spend (plan P4-D190), and three for G7.3's count
passes -- a withheld count at midnight kept on its side, and the counts of
widths and of different dates reached (plans P4-D191 and P4-D192), and
two for G6.5a's whole number written two ways, by the fill and by the
merge (plan P4-D193), one for the census of marks held at a thousand on
a column with refunds (plan P4-D194), and one for a declared identifier's
partners held to the cells its layout census names no layout for (plan
P4-D196), and one for a workbook column of free text writing its truth
values as them (plan P4-D198). and ONE for the calendar a date cell is held to and the
cells a column stored as dates is written from (plan P4-D291), which is
the ninth case of the fourth file and the only case of any file that
reaches either branch. **No case was added for the files review
of 2026-09-18, and a COLUMN was**, which is recorded here rather than
left to be noticed: `workbook_as_written` gained a fourth column storing
its dates as their ISO text rather than as day counts (cell class
`date`, plan P4-D284), and a third mutant that converts every date as
the rule it replaced did. No committed case reached that branch of step
0 before it, so every rule telling such a cell from a day count could
have been withdrawn with every committed byte unchanged.

**Landing 2b.6 PART 2 added no case either, and it WITHDREW a frozen
mutant, which is recorded here rather than left to be noticed.** Part 2
rewrote the placement rule of G7.3 — the nine interior rungs pinned to
their published values, every other rank drawn inside its own gap — so
the interior cells of every date case in all three committed files
moved, and `date_only`'s mutant was retargeted from the floor rounding
of the withdrawn interpolation to the placement rule itself. **The
mutant of `midnight_days` could not be kept.** It withdrew P4-D39's
day-unit rule by counting a column wholly at midnight in seconds, and
its interior ranks still land part-way through a day under it —
measured, rank 3 moves from day 19846 to that day plus 25,374 seconds —
but the CELLS no longer move, because counting in seconds also turns the
midnight snap of landing 2b.3 on, and that snap pulls every rank back to
the nearest midnight INSIDE ITS OWN GAP. With the rungs pinned and every
draw confined to a gap, the snap reproduces the day-unit rule exactly,
so withdrawing either rule alone leaves the same twin. A mutant whose
branch has become redundant cannot move a byte, and dressing it up as
one would be the "guard that passes" this section exists to refuse. So
`midnight_days` now holds up the placement rule, which is load-bearing
for it, and **the day-unit rule of P4-D39 no longer has a frozen mutant
of its own** — a gap in this section's own terms, named as one, and the
rule stays pinned by the round trips of
`tests/test_stage2_timestamp_spellings.py`.

**Landing 2b.6 added NO case, and that is recorded here rather than
left to be noticed.** The reversal of owner decision 5 changed the
writing rule of G7.5 for every member, and the case that pins it
already existed: `slashed_pool` describes a column read as
`slashed-iso-datetime`, and its ten cells moved from `2024-06-13 07:55`
to `2024/06/13 07:55` when the rule changed — so a revision that put
the ISO writer back moves committed bytes and is caught. What no
committed case reaches is the ALLOCATION of the two joint censuses,
the widths and the month-name styles, because no case here describes a
column that mixes two conventions; those are pinned by round trips in
`tests/test_stage2_dates_as_written.py` and not by frozen bytes. That
is a gap in this section's own terms and it is named as one.

**The owner's rulings of 2026-09-17 add three more to the sixth file**:
`identifier_column_prefix` and `identifier_layout_prefixes`, G9.6a's
templates for the whole column and per layout (plan P4-D202), and
`pooled_level_sizes`, G8.3's sizing of the invented levels off the
pooled total (plan P4-D201).

**The extra review round of 2026-09-18 adds seven, and they are the
EIGHTH file.** Five come from its date pass (plans P4-D254 to P4-D258):
`date_midnight_feasible`, the feasible spend of an
offset where the column is moved onto midnight;
`date_endpoint_ties`, the offsets a rank standing on an end's own
instant may wear; `date_second_field_class`, the census key carried
into the width pass; and `date_traded_merge` and
`date_nonadjacent_merge`, G7.3's two merges. Two come from its number
pass: `saturated_representable`, G6.5a's last resort on the
representable grid (plan P4-D269), and `unmarked_duplicates_first`,
G6.5's visiting order for the distinct-spelling repair (plan P4-D265).
The two passes were built separately and each put its own cases in the
seventh file; merged, that file stood at 276235 bytes against the
250000-byte cap, so all seven moved into
`tests/reference/generation-branch-vectors-6.json` together. **The
carried date items of 2026-09-18 add two more to the eighth file**,
`date_two_kinds_traded` and `date_two_kinds_nonadjacent`, which reach
G7.3's two merges again after plan P4-D294 left them unreached (see
below the table). **Its repair pass adds one more**,
`date_both_fields_disagree`, which pins G7.5 step 1's joint word for a
rank whose two fields both show under a census naming one-field words
alone, and rebuilds the two before it from the descriptions the producer
writes of their tables.

**The readings of an absorbed count add two more to the eighth file**
(plan P4-D298): `free_text_absorbed_figures`, G9.5's packing against a
reading where the published alphabet counts have none, and
`identifier_absorbed_figure`, G9.6 built against a reading where the
published counts have no whole-number spelling at the shortest length.

**The carried numbers pass of 2026-09-18 added four more to the eighth
file**, where plan P4-D295 routes the next case: `saturated_band`,
G6.5a's fill of a sign band whose own grid has no spare point, which
this pass added; and the two generator rules the extra round landed with
no mirror at all -- `mode_held`, the published mode on the stratum its
count sizes (plan P4-D267), and `held_back_dressed` and
`held_back_anchored`, G8.3a's dressing of a ladder number into its
published form and the anchors every published spelling gives the ladder
(plan P4-D268), one case for each half so either half withdrawn moves
cells. With them the eighth file's output stood at 235440 bytes on that
pass's own branch: it had passed the 200000 bytes P4-D295 set, so the
NEXT case went in a ninth entry point, written the way the eighth was. The band fill is the
column-wide fill of plans P4-D147 and P4-D176 stated band by band, and on
a column of one sign the two are the same fill, so the registered
mutants of `saturated_integers` and `saturated_tenths` withdraw the fill
in both its statements -- withdrawing the column-wide one alone left the
band fill writing the same cells, and those two cases stopped holding the
fill up.

**The carried numbers repair pass of 2026-09-19 adds two, and they are the
NINTH file**, `tests/reference/generation-branch-vectors-7.json`, the
entry point the paragraph above called for: `pushed_along_band`, G6.5a's
push of a collision the walks leave along its band to the nearest free
point, which this pass added; and `saturated_grid_alone`, the column-wide
fill of plans P4-D147 and P4-D176 on a column where the band fill and the
push both stand aside. After the band fill the column-wide fill could be
withdrawn with every committed byte unchanged, because every case that
reached it was a column the band fill filled the same way; the second
case holds it up alone, and its mutant withdraws it and nothing else. The
push reaches the same assignment on a grid of tenths with no spare point,
so the mutant of `saturated_tenths` withdraws it on a written grid too;
each of the three statements of the fill is held up by a case of its own
whose mutant withdraws that statement alone -- `saturated_grid_alone`,
`saturated_band` and `pushed_along_band`.

**WHERE THE CARRIED PASSES MET** (the integration of 2026-09-19). The
carried date items and the readings of an absorbed count put their five
cases in the eighth file as P4-D295 directed, and the numbers pass put
its four there on a branch of its own; merged, the eighth would have held
sixteen cases and stood past the 250000-byte cap. So the numbers pass's
four moved WHOLE into the ninth file beside the two its repair pass put
there, exactly as the eighth file was first formed: the eighth holds
twelve cases under 200000 bytes and takes the next case again, and the
ninth holds six. No case was dropped, no cell of any case moved, no proof
was shortened and the cap was not raised.

**Plan P4-D6.4 adds one, to the eighth file**, where plan P4-D295 says
the next case goes while that file stands under 200000 bytes:
`judged_stand_in_written`, G10.1's write rule with a judged stand-in
among a column's absent cells. No case before it published a
`missing_by_source` key at all, so the whole of G10.1 could have been
withdrawn with every committed byte where it was. Built on a branch of
its own and merged at the integration of the gap passes (2026-09-19), it
takes the eighth file to thirteen cases and 191318 bytes.

**The dates pass of the second Codex round of 2026-09-19 adds one, to the
eighth file**, where plan P4-D295 still sends the next case while that
file stands under 200000 bytes: `date_midnight_traded`, the MIDNIGHT half
of P4-D258's paid merge. Every case frozen for that plan carries two
WIDTH kinds, so the trade's other standing -- whether a unit is written at
midnight -- could have been withdrawn with every committed byte where it
was, and a run of non-midnight ranks stranded between midnight pins had
no merge of any kind. It takes the eighth file to fourteen cases and
212306 bytes.

TWO MORE CAME WITH THE REPAIR PASS OF THAT ROUND (2026-09-19), closing
its skeptic's finding that G8.3a step 3's two new rules were held up by
no committed byte: withdrawn from the oracle, singly or together, they
left 814 reference and oracle-witness tests green and all ten vector
files byte-identical. `exponent_scaled` pins the SCALED walk and
`exponent_fitted` the EXPONENT FITTINGS. They go in the SEVENTH file,
which stands at 162761 bytes, and not in the eighth or the ninth, both
past plan P4-D295's 200000-byte line: the eighth's own entry point
provides for exactly this, saying the fifth takes a case where it
cannot. Opening a tenth entry point would have moved every other
committed file's bytes, because each file's `case_set` account names all
the others. The seventh file now holds eight cases and 176541 bytes.

**THE ABSORBED MARK OF 2026-09-21 ADDS ONE, TO THE SEVENTH FILE** (plan
P4-D245, ledger K-2B-51, the owner: 'I think we need to fix'):
`date_absorbed_mark`, G7.9's spend of a mark the census leaves unnamed
where ruling 6 of 2026-09-17 absorbed the spelling the column's published
distinct count needed. It goes to the seventh for the reason the two
exponent cases did -- the eighth and the ninth stand past plan P4-D295's
200000-byte line and this one does not -- and no earlier case reaches
the rule with the shortfall it is written for, so the whole of G7.9
could have been withdrawn with every committed byte unchanged.

**THE POOLED SCALE OF 2026-09-21 ADDS THE TENTH** (plan P4-D301, ledger
K-2B-50): `pooled_number_scale`, G8.3c's placement of the pool's made-up
numbers on the scale contract 6.3.3 publishes for them. It was cut
against the same file and for the same reason on a branch of its own,
and the two arrived together at the integration of 2026-09-21. **The
seventh file now holds ten cases and 203332 bytes, so it has crossed
plan P4-D295's 200000-byte line and the next case does not come here.**
Both of the sentences above judged that line against the file as their
own branch found it -- 176541 bytes and 197917 bytes -- and neither
could see the other's case; the line is judged against the merged file
from now on. The provenance manifest's 250000-byte cap is unaffected and
the file stands well inside it.

**THE TAIL RULE OF STAGE 3 ADDS FIVE, AND THEY ARE THE TENTH AND
ELEVENTH FILES** (landing 3.3, plans P4-D322 to P4-D327 and P4-D344). Every column
they describe publishes NO rung outside its two boundary percents,
which no case committed before stage 3 does, so the whole of the rule
could have been withdrawn with every committed byte of the other nine
files unchanged. The tenth file,
`tests/reference/generation-branch-vectors-8.json`, holds
`tail_shape_ends` -- G5.3b's reading of a tail's rows and the two
DERIVED ends, on a column whose low tail fits a nearly straight shape
and whose high one fits a power of sixteen -- and `tail_made_up_ramp`,
the ramp of G5.3d on a block of eight rows at a floor of eleven. The
eleventh, `tests/reference/generation-branch-vectors-9.json`, holds
`tail_listed_counts`, the staircase of G5.3e and the counts solved for
it on a grid of whole numbers; `tail_sign_clamped`, G5.5a's hold on a
derived end that reaches past nought on a column with no negative
number; and `tail_moment_ladder`, the uniform of G5.3c on a block too
thin for two tails. The six are cut into two files because a committed
fixture must stay under the provenance manifest's 250000-byte cap and
each case describing a column dense enough to fill its own histogram
costs about seventy kilobytes of proved numbers.

**A PUBLISHED (HEAPED) END HAS NO FROZEN CASE, AND THAT IS A GAP NAMED
AS ONE.** Step 1 of G5.3b's derived end -- a published end IS the end
-- is unreachable by a mutant on a column whose values stand on a
grid: an end is published only where at least max(`small_cell_floor`,
3) rows hold it, twelve rows with eleven of them on one value hold at
most two different values, so the tail is LISTED and G5.3e's step 2
returns the same end. On a column with NO grid the case must publish
several fraction widths or an exponent form, and G6.6's allocation of
those across the cells is a transform this oracle does not state; a
case built that way had the two implementations part company over
which strata wear the exponent form, which is a disagreement about
G6.4 and not about the tail rule. The step is pinned by the round
trips of `tests/test_taxonomy.py` and `tests/test_validation.py`, and
it is named here rather than left to be discovered.

**AND ONE SENTENCE OF THE MIGRATION REFUSAL NOW OVERSTATES WHAT A CODE
COLUMN PUBLISHES, WHICH IS NAMED HERE BECAUSE IT CANNOT BE EDITED.**
The refusal a version 4 description raises says that without the
`--code` given the first time, "its smallest and largest values --
which are real codes -- are published". Under the tail rule they are
published only where a group of at least max(`small_cell_floor`, 3)
rows holds the end; on a column of different codes neither is. The
sentence is fixed word for word by contract version 5, section 10.2
(C5-26), which is a frozen document, so the wording stands and the
overstatement is recorded rather than repaired. What it overstates is
in the safe direction -- it warns of a disclosure larger than the one
that happens -- and the clause beside it, `--missing-value`'s "CAN be
published as the column's smallest value", is exactly right under the
new rule.

**All one hundred and nineteen are required.** The count is taken off the committed
case sets and not carried forward: this sentence said fifty-two and a
split of nine, twenty, sixteen and seven while the six files held
seventy-three, because each repair that added a case added a clause to
the list above and moved no number here. Landing 2b.6 withdrew one of
the cases named above, `accidental_midnight`, with the rule it pinned,
and it is in no file. The first file,
`tests/reference/generation-reference-vectors.json`, holds fifteen; the
second, `tests/reference/generation-branch-vectors.json`, holds
nineteen; the third, `tests/reference/generation-branch-vectors-2.json`,
holds sixteen; the fourth,
`tests/reference/generation-document-vectors.json`, holds nine; the
fifth, `tests/reference/generation-branch-vectors-3.json`, holds eight;
the sixth, `tests/reference/generation-branch-vectors-4.json`, holds
eleven; the seventh, `tests/reference/generation-branch-vectors-5.json`,
holds ten; the eighth,
`tests/reference/generation-branch-vectors-6.json`, holds fourteen; the
ninth, `tests/reference/generation-branch-vectors-7.json`, holds six;
the TENTH, `tests/reference/generation-branch-vectors-8.json`, holds
six; and the ELEVENTH,
`tests/reference/generation-branch-vectors-9.json`, holds five (G14.2),
and a test holds this sentence to those files.

**THE TENTH AND ELEVENTH FILES, AND WHY THEY WERE OPENED** (stage 3,
plans P4-D328 and P4-D322 to P4-D327 and P4-D344). BOTH of stage 3's tail landings
opened a file here, and in one tree the tenth holds both sets. A
column of dates or clock times needs `2F + 1` cells to publish a tail
at all, and a case whose rule lives BETWEEN the two boundaries needs a
body of several ranks besides, so four cases grew at the tail landing:
`clock_ladder`, `partial_midnight`, `midnight_bare_offsets` and
`midnight_days`. Grown in place they carried the third file to 261857
bytes and the second to 258476 against the manifest's 250000-byte cap,
so the four moved into a file of their own and both fell back under it.
The NUMERIC tail rule's five cases (landing 3.3) could go in no earlier
file either -- the seventh, eighth and ninth all stand past the 200000
bytes plan P4-D295 draws the line at -- and five of them do not fit
under the 250000-byte cap in one file beside the date landing's four, so
two stand in the tenth (`tail_shape_ends`, `tail_made_up_ramp`) and
three open the eleventh (`tail_listed_counts`, `tail_sign_clamped`,
`tail_moment_ladder`). No case was dropped and no cap was raised.

**AND THREE BRANCHES LOST THEIR WITNESS AT THAT LANDING**, recorded
here rather than left to be discovered. `date_endpoint_ties` was frozen
for plan P4-D255's hold on the ranks tied at an END, and there are no
ends: the description names no offset for an end row because it
describes no end row. `date_absorbed_mark` was frozen for G7.9's spend
of an absorbed mark, and `date_two_kinds_nonadjacent` for P4-D258's
merge onto a held unit that is no rank neighbour; both columns are
heaped on two or three days, so at a floor of eleven their two
boundaries cross, they publish no tail and no rung (P4-D330), and their
twins are the RAMP -- which reaches the published count of different
values by itself, leaving no shortfall for a mark to buy and no run for
a merge to move. `date_midnight_traded` keeps its column and loses the
midnight half of the same merge, because a tail rank moves only inside
its own stratum. **The round-trip mutant of that same half lost its
outcome too**, and is named here for the same reason:
`tests/test_round2_numbers_dates.py` commits a mutant withdrawing the
midnight trade, and the column of three timestamps whose twin used to
strand a fourth value now holds exactly the three published ones with
the trade withdrawn -- the two tails settle the outer values and G12.4
puts a run whose gap must hold a midnight into a gap that can hold one,
both before a merge is asked for. Measured over nine shapes on
2026-09-22, the mutant matched the unmutated twin in every one; the
test keeps the mutation and asserts the property that replaced it, so a
regression in either rule strands the run again and turns it red. Each
of the four cases now holds up a rule it does reach --
the ramp's step count and its start, G7.3b's moment-matched end, and
the CONDITION on G7A.4's two-pass step -- and the branches they leave
are named here so that a later landing can put a case back rather than
discover the gap. **The table below is the inventory itself, and it was short of
the count above by one row from the day the pooled-spelling case was
added** (review item P4-DATE4-F3): an implementer who built exactly the
rows listed would have left out a required branch while every listed
case passed, which is the failure the count exists to prevent:

| case | pins |
|---|---|
| `date_only` | G7.5's date form; endpoints exact; ordinal floor rounding |
| `quarter` | G7.5's quarter form; the quarter ordinal |
| `offset_bearing` | G7.4's allocation, the `utc` clock conversion, and `earliest_utc_offset`/`latest_utc_offset` |
| `mixed_parsed_unparsed` | G10.4's stand-ins beside parsed cells, and `n_unparsed` |
| `numeric_integer` | G5.3 with `integer_valued: true`, the tie-toward-`+inf` rounding, and both endpoint pins |
| `numeric_decimal_styles` | G6.2's canonical boundaries (`1e+16`, `1e-05`, `.0`), G6.4's largest-remaining allocation over twelve lower-case and thirteen upper-case exponent cells, and a fold-collision family of four spellings of one value (source rewritten by plan P4-D221, citing the owner rulings of 2026-09-17: its three plain cells were a pool below the disclosure line beside two named forms, which the profile contract no longer admits) |
| `label_variants` | G8.1's variant allocation, G8.2's case flips and trailing spaces, G8.3's withheld levels |
| `identifier_fold_collisions` | G9.3 with `n_distinct_folded < n_distinct`, and G9.2's length pins |
| `identifier_whole_numbers` | G9.6 with `all_whole_numbers: true` reaching all three bands, and the whole-group alphabet packing |
| `unrepresentable_joint` | G10.5's three margins packed together, on the six-row column of its step 2 whose out-of-range cell no two of them place |
| `unrepresentable_exponent` | G10.5 revision 5's EXPONENT spelling family, on six cells published at five and six characters — widths no digit string can be written at — and the shape-and-sign walk rule that case forced this section to state |
| `free_text_joint` | G9.5 steps 3 and 4 as ONE packing, on a column two separate walks cannot both land; since landing 2b.4 its doubled number is also written at step 3a's own length, one figure, and the column it describes publishes the average that length gives |
| `identifier_edge_spacing` | G9.3's partner family where case flips supply nothing at all, so every partner is edge spacing |
| `free_text_absorbed_figures` | G9.5's packing against the READINGS of an absorbed count (plan P4-D298): sixteen cells of free text publishing sixteen in figures alone beside fifteen numbers, because the one cell outside the figures is below the floor of eleven and the contract counts it into the larger side. Sixteen figures-only cells are sixteen numbers, so the published counts have no packing; the first reading, fifteen in figures alone, packs, and the single cell is `A`. Its mutant packs the published counts alone and the oracle refuses the column |
| `identifier_absorbed_figure` | G9.6 built against the READINGS of an absorbed count (plan P4-D298): twenty-one record numbers, every one a whole number, publishing no cell in figures alone beside a shortest length of one, because the one figure-only cell is below the floor. A one-character whole number is a figure, so the published counts have no answer; the first reading that holds every count as published writes `1` once and `0e0` twenty times. Its mutant builds the published counts alone and the oracle refuses the column |
| `unmarked_duplicates_first` | G6.5's distinct-spelling repair visited unmarked first (plan P4-D265): forty-four cells of one value written plain, with a leading plus and with a point, whose census of marks names eleven of the twenty-two groupable cells and whose ten published spellings ask four cells to spend a zero, so the duplicates a raised order may be spent on are mixed. Its mutant visits them in index order and four of the eleven marks come off the column |
| `judged_stand_in_written` | G10.1's write rule with a judged stand-in among the absent cells (plan P4-D6.4): `numeric_integer`'s twenty values beside twenty-two absent cells, eleven of which held `-999`, which the column's own stand-in pass judged to mean "no value", and eleven of which held nothing. The twin writes `-999` in eleven cells and leaves eleven empty, placed by G4.2's one arrangement. Its mutant is the rule this replaced, which wrote a judged pass's cells empty, and the eleven `-999` cells move |
| `saturated_representable` | G6.5a's last resort, the REPRESENTABLE grid (plan P4-D269): twelve numbers at the subnormal boundary, one binary64 step apart, whose census names no fraction width, so neither the pinned width nor the finest width gives the separation pass a grid and the two published ends saturate the representable numbers themselves. Its mutant withdraws the fill, the ladder interpolates between rungs one step apart, and several strata land on one number |
| `pushed_along_band` | G6.5a's push of a collision the walks leave along its band to the nearest free point (the carried numbers repair pass of 2026-09-19): fourteen one-place readings from 2.6 to 3.9 beside four far ones, 53.6, 67.1, 134.8 and 135.7, eighteen different numbers each written once and no empty stretch published. Once the walks are done the run's fourteen strata stand on thirteen of its tenths, two of them on 3.4, and the free tenth 3.9 lies past the walk's reach; the push moves the second 3.4 and every stratum above it one tenth up. Its mutant withdraws the push, and the twin writes 3.4 a second way, `03.4`, holding seventeen numbers against eighteen |
| `tail_shape_ends` | G5.3b's reading of a tail's own rows and the two DERIVED ends (stage 3, landing 3.3): sixty one-place readings whose twelve smallest and twelve largest are withheld by the tail rule, the low tail fitting a nearly straight shape and the high one a power of sixteen because one row stands far past the others. Its mutant withdraws the OUTWARD move of plan P4-D326 and the high end falls back inside the rows it stands for |
| `tail_made_up_ramp` | G5.3d's ramp (stage 3): eight whole numbers at a floor of eleven, a block below one tail's own rows, publishing no rung, no moment and no style. Its mutant leaves the ramp flat at nought, which is what the sign fallback wrote before the ramp existed |
| `tail_listed_counts` | G5.3e's staircase and the counts solved for it (stage 3, plan P4-D324): seventy-two whole numbers from 0 to 54 on a grid, four cells each at the three values of either end, so both tails are few-valued and the description publishes the values themselves. Its mutant gives every listed value one row and the rest to the outermost, and the staircase moves |
| `tail_sign_clamped` | G5.5a's sign rule on a derived end (stage 3): sixty two-place readings, every one positive, whose low tail's own reading reaches past nought. Its mutant withdraws the rule and the twin writes a negative cell on a column whose description says it has none |
| `tail_moment_ladder` | G5.3c's moment ladder (stage 3): fifteen two-place readings at a floor of eleven, where no percent leaves eleven rows outside on both sides at once, so the block publishes its moments and not one rung. Its mutant reads the block as the ramp of G5.3d instead |
| `saturated_grid_alone` | G6.5a's column-wide fill of a grid with no spare point (plans P4-D147 and P4-D176) where it alone answers: seventy-eight one-place readings from -2.4 to 0.1, the whole numbers written bare, publishing twenty-six different numbers between ends holding exactly twenty-six tenths and twelve point-free cells, no empty stretch published. The band fill stands aside because a stratum it would fill changes whether its value has a point-free spelling, and the push keeps a whole value on the whole points: the two strata the walks leave on -2.0 find every whole point of their band taken, and the one free tenth, -0.1, is not whole. Its mutant withdraws the column-wide fill and nothing else, and the twin writes -1.9 a second way, `-01.9`, holding twenty-five numbers against twenty-six |
| `saturated_band` | G6.5a's fill of a sign band whose own grid has no spare point (the carried numbers pass of 2026-09-18, amending plan P4-D147): twelve negative readings at one place and fifteen positive ones with the published empty pair (-0.1, 50.0) between them. The finer rungs fall inside the pair, so the ladder puts a positive stratum there; the positive band's points outside the pair are exactly its fifteen strata and take them in order, while the negative band, twelve strata on a hundred points, is left to the walk, and the whole column is not saturated. Its mutant withdraws the band fill and a stratum stays inside the empty pair |
| `mode_held` | G6.1's last value pass (plan P4-D267): eleven one-place readings from -1.7 to 6.9, the commonest -0.6 over twenty-one rows. The ladder sizes one stratum at twenty-one cells and gives it another number; the pass puts -0.6 on it. Its mutant withdraws the pass and the mode is written nowhere |
| `held_back_dressed` | G8.3a's dressing (plan P4-D268): thirty `alpha` beside eleven `+15` and two held-back signed numbers over eleven rows, whose census names `+%%` twenty-two times. The ladder's plainly spelled steps are written through the form and kept where they wear it and hold the same value, `+14` and `+16`. Its mutant withdraws the dressing and the held-back rows are bare numbers |
| `exponent_scaled` | G8.3a step 3's SCALED walk (item 3 of the numbers pass of the second Codex round, 2026-09-19): thirty `alpha` beside eleven `1.10e+3` and two held-back exponent spellings over eleven rows, whose census names `%.%%&+%` twenty-two times. The form writes two figures after its mark, but the value those two figures move by is a hundredth of the EXPONENT'S scale, so a walk at the form's plain places offers steps a thousand times finer than the form can spell and the dressing refuses every one. The exponent is read off the largest published magnitude, written with the mantissa's own count of figures before the mark, and the ladder is walked again at `after` less that exponent — last of three, after the ladder's plain places and after the form's own filling of step 2. The held-back rows take `1.11e+3` and `1.09e+3`. Its mutant answers the plain places and they are written `1101` and `1099`, bare numbers wearing no form |
| `exponent_fitted` | G8.3a step 3's EXPONENT FITTINGS (item 3 of the same pass): thirty `alpha` beside eleven `2.20e+4` and two held-back exponent spellings over eleven rows, under the same census. Step 2's two placements count a candidate's figures into the form's figure places in order, which reaches only a value the mantissa has room for — five figures into four places is no filling at all. An exponent form is filled instead by choosing the exponent that leaves the mantissa exactly its own count of figures, and the one either side, the mantissa being the candidate's value divided by that power of ten exactly or not at all. The held-back rows take `2.21e+4` and `2.19e+4`. Its mutant offers no exponent filling, step 2's placements answer alone, and they are written `22001` and `21999` |
| `held_back_anchored` | G8.3a's anchors (plan P4-D268): thirty `alpha` beside eleven `+25` and two held-back signed numbers over eleven rows. The only published number carries a plus, which the plain reading refuses; read a second way it anchors the ladder at twenty-five, so the held-back rows take `+24` and `+26`. Its mutant reads the plain spelling alone and the ladder counts up from nought |
| `code_band_words` | G9.2's HEADED enumeration of a band's made-up words (plan P4-D234): six one-word cells of the code alphabet at two characters, `A-`, `B-`, `C-`, `D-`, `E-`, `F-`. Its mutant counts the whole word over the alphabet and puts the first permitted character in the leading place afterwards, which is how the reference oracle read the rule until the two implementations were measured against each other, and the cells become `A-`, `A0`, `A1` |
| `count_spellings` | G6.8's census of spellings: a count column writing `7`, `07` and `007` beside `0`, eleven cells each, whose numbers are written as the census and nothing else. Its mutant withdraws the rule, the ladder and style walks write the column, and the cells move |
| `level_shape_stand_ins` | G8.3b's shape and trade: a long tail publishing one level `a-` whose shape no census key names, beside a census owing `@@@@-@@` thirty-four cells over forty-five held-back labels pooled on sixty rows, whose sizes G8.3 reads off the pool and its debts as thirty-seven single rows, four of two, two of three, one of four and one of five (plan P4-D201). The stand-ins owed no form wear `&-` with the case kept, and the group of five paying `@@@@-@@` trades with five single rows so the shape's supply covers every place owed no form. Its mutant withdraws the trade, a place past the supply takes `group-N`, and the oracle refuses the figure that spelling carries |
| `lower_case_stand_ins` | contract C6-31a's lower-case keys: a column of categories whose census names `&&-&&` for its published level `ab-cd` and `&&&&-&&` for twenty-nine held-back cells. The level settles its own key in full under the key the census files it, so the stand-ins owe `&&&&-&&` alone, filled from the lower-case alphabet. Its mutant fills the key in capitals, and every stand-in moves; reading the level blind to case hands `&&-&&` stand-ins it does not owe, and the cells move too |
| `identifier_layout_mixes` | G9.6's zero fill, space and MIXES (plans P4-D126 to P4-D128): a declared identifier of forty-seven nine-character cells publishing `{"!!%%%%%%%": 11, "@%-------": 11, "@@%% %%%%": 11, "(withheld)": 14}`. The eleven fills are written `00` and seven figures, the next figure never a nought; the space stands as a mark; and the fourteen pooled cells are written to mixes of figures and capitals over the two places of `@%-------`, the first base in sorted order, whose mix `@%` is named and stepped over, so they are written `%%`, `%@` and `@@`. Nine characters wide because this oracle reads no date, and no date format is nine figures or four and four around a space. Its mutant withdraws the mixes and the fourteen cells move; withdrawing the fill or the space stops the oracle at the check of 7.12, and reading the named mix moves the cells |
| `identifier_signed_layout` | G9.6's proven sign (plan P4-D156): a declared identifier of twelve signed whole numbers publishing `{"-%%%%": 12}`, every cell a minus and four figures. Its mutant refuses the sign and the check of 7.12 finds the layout worn nought times |
| `identifier_absent_words` | G9.6's refusal of a spelling read as absent (plan P4-D158): a declared identifier publishing `{"@@": 20}`, whose layout walk reaches `NA` at its thirteenth filling and steps over it. Its mutant reads nothing as absent, `NA` is written, and the cells move |
| `identifier_layout_partners` | G9.6's partner layouts (plan P4-D157): twenty-two identities and eleven partners publishing `{"@%%": 22, "&%%": 11}`, the identities owed partners visited first and debited with them. Its mutant predicts no partner wears a layout, and the check of 7.12 finds `&%%` worn fourteen times |
| `identifier_layout_packing` | G9.6's layout packing (plan P4-D182): a declared identifier of four groups of eleven rows and two of twenty-two publishing `{"@@#%%": 11, "@@*%%": 11, "@@-%%": 22, "@@.%%": 11, "@@:%%": 11, "@@_%%": 22}`, two code-alphabet layouts of twenty-two cells and four wide-alphabet layouts of eleven. The class-and-alphabet packing gives the code band the four groups of eleven and the wide band the two of twenty-two, which no layout of eleven can take; packed with the census as a third margin, the wide band takes the groups of eleven and each group is offered its own layout alone. Its mutant finds no layout packing and the check of 7.12 finds `@@#%%` worn nought times |
| `identifier_layout` | G9.6's LAYOUT OFFER (contract 7.12): a declared identifier publishing `layout_forms` `{"@%%%%%": 12, "@@%%%%": 12}` over twelve identities written once and six written twice, whose cells are written to those layouts rather than by the band enumeration; the fill is a counter taken apart LEFTMOST FIRST from step one, spread by the exact golden section of the room — `L30816`, `W60632`, `H01458` — and the census is spread over the identities by the smooth weighted rotation, largest group first. Its mutant withdraws the rotation, every singleton then takes `@%%%%%` and every repeat `@@%%%%`, and the cells move; withdrawing the offer altogether stops the oracle at the check of 7.12 |
| `numeric_point_free_styles` | G6.1's literal `decimal`, `leading_zero` and `leading_plus` placements, G6.4's tie order, and G5.3's clamp |
| `leap_second_endpoint` | G7.5's endpoint-fields route on a `local`-clock end whose seconds field is `60`, which the ordinal space of G7.1 has no place for |
| `month_span` | G7.1's month ordinal and G7.5's `month/month` cell form: the second resolution that names a SPAN rather than an instant, whose canonical form is its own cell text |
| `numeric_pooled_spelling` | owner decision 11's pooled remainder written by its own value, beside a whole number wider than the fixed-point window |
| `long_tail_levels` | G8.1 to G8.4 reached through `long_tail_labels`: the ADMISSION of a folded count above the categorical ceiling, and the G8.3 stand-ins taken as words because a form census covers the held-back rows. It pins admission and routing into the shared label machinery, not a generator branch of the role's own |
| `clock_declared_hole` | G7A.4's HOLE STEP (the dates pass of the stage-3 review, item 5): forty-four clock cells beside eleven absent ones, every absent cell written `08:00` -- a spelling a declaration made mean "no value" for the whole table -- and `08:00` is the column's own middle rung, so the body's interpolation puts ranks squarely on it. Its mutant answers that no spelling reads as absent, which is what this role did: the stand-ins were stepped past the absent spellings and the clock VALUES were asked nothing, and the column then writes thirteen `08:00` cells against the eleven its description publishes absent |
| `clock_ladder` | G7A end to end on a column with NO SLACK: eleven seconds hold its eleven parsed cells, so the all-different repair must place every interior rank on the one ordinal left for it, and a stand-in stands beside them |
| `affixed_brackets` | G6A's core view: the CELL class counts and the CORE class counts are not the same set, and only the second reaches G5 and G6. The pair is two-sided with differing characters, so the order of the wrap is pinned too |
| `joined_readings` | G6B.4's PAIRING WALK, the only search in this method: each position built by the numeric rules over its own view, and the last position then walked, from a rank-for-rank start, toward a published agreement of 0.4323 that it does not reach |
| `midnight_days` | G7.1's day unit and G7.5's midnight clock: twelve `local` moments all at midnight, published with `all_at_midnight: true` and `datetime_separators: {"space": 12}`, whose ladder, ends and interior ranks are counted in whole days and whose every cell is its day with a midnight clock, carrying a space |
| `grouped_charges` | G6.1's mark at leading-zero order nought only, on a column publishing `,`, beside `decimal_plus` of eleven spread one in every two over twenty-two decimal cells; two cells spend a zero and carry the plus in front of it and no mark |
| `grouped_decimal_comma` | P4-D26's exchange on a declared column publishing `.`: `42.037,34`, one spent cell `042037,34` with no mark, and two absent cells the exchange does not touch |
| `spaced_brackets` | a space between thousands and the `brackets` notation: `(12 345.5)`, and a spent cell `(012345.5)` whose brackets close around the zeros with no mark and no sign |
| `apostrophe_minus_sign` | an apostrophe between thousands and the `minus_sign` notation: `−12'345.5`, and a spent cell `−012345.5` with the sign in front of the zeros and no mark |
| `quoted_trailing_minus` | U+2019 between thousands and the `trailing_minus` notation after figures carrying a point: `12’345.5-`, and a spent cell `012345.5-` with no mark |
| `spaced_decimal_comma` | P4-D26's exchange beside a no-break space U+00A0, a mark neither decimal mark: `42 037,34`, one spent cell `042037,34` with no mark, and two absent cells |
| `narrow_spaced` | a narrow no-break space U+202F between thousands: `12 345.5`, and a spent cell `012345.5` with no mark |
| `thin_spaced` | a thin space U+2009 between thousands: `12 345.5`, and a spent cell `012345.5` with no mark |
| `bare_mark_remainder` | G6.1's bare remainder of a census of marks (plan P4-D142): thirty-three cells of twelve thousand three hundred and forty-five and a half published with `group_separator: ","` and `thousands_marks: {",": 22}`, so the first twenty-two are written `12,345.5` and the eleven the census leaves -- the census floor of them -- `12345.5`, with no mark |
| `pooled_mark_cells` | G6.1's pooled remainder of a census of marks (plan P4-D142): forty-four cells published with `thousands_marks: {",": 33, "(withheld)": 11}`, so the first thirty-three are written `12,345.5` and the pooled eleven `12 345.5`, a space being the first pool mark the census does not name |
| `unpublished_majority_marks` | G6.1's groupable cells asked with a mark that writes one (plan P4-D142): twenty-two cells published with no `group_separator` and `thousands_marks: {",": 11, " ": 11}`, so the first eleven are written `12,345.5` and the last eleven `12 345.5` rather than every cell bare |
| `plus_padded_field` | G6.3's second tier of named field widths (plan P4-D145): twenty-two cells of twelve thousand three hundred and forty-five published `leading_plus` with `pad_widths: {"7": 22}`, every one written `+0012345` |
| `saturated_integers` | G6.5a's fill of a saturated integer grid (plan P4-D147): thirty-three whole numbers publishing twenty-two different values between the ends one and twenty-two, so the strata take those integers in order, each once, and all twenty-two are written |
| `spread_conventions` | G6.1's spread of both censuses of conventions (plan P4-D149): the twenty-two whole numbers from minus 1,021 to minus 1,000, published with `thousands_marks: {",": 11}` and `negative_notations: {"brackets": 11, "minus": 11}`, so the brackets, the minus signs, the grouped cells and the bare ones each fall across the whole range of values rather than on its most negative half |
| `grouped_thousands_signed` | G6.1's census of marks held at a thousand on a column with refunds (plan P4-D194): thirty-three amounts at one place between -1080.4 and 1096.6, seventeen negative, twenty-two reaching a thousand in size and written with a comma. The positive run leaves one cell short, the count is taken again, and the negative stratum just above minus a thousand moves below it. Its mutant withdraws the negative side, and twenty-one cells wear a comma |
| `identifier_unnamed_partners` | G9.6's quota of the cells a layout census names no layout for (plan P4-D196): a declared identifier of forty-four cells publishing `{"&%%%": 11, "@%%%": 22, "@-%%": 11}`, thirty-three identities and eleven fold-collision partners. No cell is left unnamed, so an identity owed a partner takes no layout whose partner wears none, and every partner wears `&%%%`. Its mutant withdraws the quota, and the check of 7.12 finds `@%%%` worn twenty-one times |
| `truth_values_written` | G9.5's truth values of a workbook column (plan P4-D198): thirty-two cells of free text, twenty-one one-letter codes and eleven truth values its workbook census counts as `boolean 11`. The group of eleven the packing puts in the code alphabet as text is spelled `TRUE` at its own four characters. Its mutant spells no truth value, and the cells move |
| `twice_written_filled` | G6.5a's whole number written two ways, the fill (plan P4-D193): ninety readings at one place between 3.5 and 4.3, fourteen whole ones written bare, publishing ten spellings of nine numbers; the grid holds exactly nine tenths, so the ten strata take them in order with 4.0 taken twice. Its mutant withdraws the rule, and the walk leaves two strata on a tenth that is not whole |
| `twice_written_merged` | G6.5a's whole number written two ways, the merge (plan P4-D193): a hundred and twenty readings at one place between 3.3 and 4.5, twenty-one whole ones written bare, publishing thirteen spellings of twelve numbers; the walk leaves a number on every stratum, so the stratum beside 4.0 nearest to it takes 4.0. Its mutant withdraws the rule |
| `saturated_tenths` | G6.5a's fill of a saturated written grid (plan P4-D176): thirty-three readings at one place publishing twenty-two different numbers between the ends 0.1 and 2.2, which hold exactly twenty-two tenths, so the strata take those tenths in order, each once. Its mutant keeps the fill on the integers alone -- in the column-wide statement, the band fill and the push, all three of which reach this assignment on a grid with no spare point -- and the cells move |
| `saturated_levels` | G6.5a's fill of a column whose published levels are its strata (plan P4-D178): thirty-three readings at one place of the four levels 2.0, 3.2, 6.5 and 15.0, each named by two rungs or more, the mode 6.5, four different values published; the rungs name more than four numbers, so the levels are the numbers two rungs or more name with the ends and the mode, and the strata take them in order. Its mutant withdraws the fill and the walk writes `4.6` |
| `separated_in_order` | G6.5a's walks taken reach by reach (plan P4-D183): `signed_pads` publishing eleven different values and twenty-two spellings, twenty-two strata over 100 to 110; every stratum is walked inside its own share first, so the thirteenth takes 105 inside its share. Its mutant takes the three reaches stratum by stratum, the tenth stratum walks out of its share onto 105, and the cells move |
| `identifier_column_prefix` | G9.6a's TEMPLATE for the whole column (plan P4-D202, owner ruling of 2026-09-17): a declared identifier publishing `{"@@@%%%%": 24}` and `{"(column)": "REC"}` over twelve identities written once and six twice; every cell is `REC` and four figures filled from the step, `REC1816`, `REC2632`, and the eighteen stay different. Its mutant reads the census as published, the letters are filled from the step, and the recount of 7.12a stops the oracle |
| `identifier_layout_prefixes` | G9.6a's templates per layout (plan P4-D202): `{"@%%%%%": 12, "@@%%%%": 12}` with `{"@%%%%%": "E", "@@%%%%": "ST"}` over twenty-four identities; the rotation spreads `E%%%%%` and `ST%%%%` over them as it spread the layouts, `E30816`, `ST7553`. Its mutant reads the census as published, and the recount of 7.12a stops the oracle |
| `pooled_level_sizes` | G8.3's sizes read off a pooled total and its debts (plan P4-D201, owner ruling of 2026-09-17): a column of categories publishing `alpha` and `beta` beside five held-back labels pooled on twenty-one rows at a floor of eleven, all owed to the one form the census names; the debt takes the three labels that pay it below the floor and then the other two, and its rows are shared one each and the rest by the square of each label's place, so the stand-ins cover 1, 2, 4, 6 and 8 rows. Its mutant shares the pool out evenly, 4, 4, 4, 4 and 5, and the cells move |
| `pooled_number_scale` | G8.3c's placement of the pool's made-up numbers on the mean contract 6.3.3 publishes for them (plan P4-D302, ledger K-2B-50): thirty-one rows at a floor of eleven, one published label `alpha` on eleven and four held-back levels covering twenty rows, every one of which the source wrote as a number. The column publishes no number of its own, so the ladder of G8.3a step 3 is unanchored; the pool's block — twenty numeric cells and a mean of 50, with NO spread since the owner's decision of 2026-09-21 — places them instead. G8.3 reads the four sizes off the pool as 10, 6, 3 and 1, the walk hands them out largest first at positions 0, 1, -1 and 2, and their weighted centre is a quarter, so their offsets are -1/4, 3/4, -5/4 and 7/4. Nothing published says how far apart the held-back numbers stood, so the spacing is this method's own — five places of this column's whole-number grid, unbounded here because the column publishes no number to bound it — and the first value asked for, 48.75, rounds onto 49. The four groups then CARRY EACH OTHER'S ARREARS (step 4): no group is pushed by the census here, so the order is the walk's own, and each group after the first is asked for what the cells still to be written must average for the pool to come out on 50 — 53.5 onto 54, 42.75 onto 43 and 57 onto 57 — against the 54, 44 and 59 the step 2 values alone would have written. The twin's own pool comes back at 50 EXACTLY, inside the window G12.12 draws, which is two places of this column's whole-number grid; the fact stays APPROXIMATED because a mean the last group's rounding cannot carry is met inside that window and not on it. Its mutant withdraws the placement and the unanchored ladder answers instead, so all four cells move |
| `grouped_thousands` | G6.1's census of marks held at a thousand (plan P4-D185): thirty-three different readings at one place between 920.1 and 1096.6 published with `thousands_marks: {",": 20}`; the ladder puts one stratum fewer at a thousand or more, so the highest stratum below a thousand takes the lowest free tenth of a thousand or more and twenty cells wear the comma. Its mutant withdraws the rule and the cells move |
| `signed_pads` | G6.5's padded sign exchange (plan P4-D145, as amended): thirty-three cells of ten whole numbers from 100 to 110 at one named field width of four figures, published `leading_plus: 22` and `leading_zero: 11` with twenty spellings, so cells written with a plus trade forms with cells written with a zero until every value the twin holds is written both ways |
| `mixed_conventions` | G6.1's two MIXED-CONVENTION censuses (landing 2b.7, plan P4-D65.2), and the only case in the three files naming more than one convention — with a single notation or a single mark the census path and the majority path write the same cell, so neither allocator can be pinned. Twenty-two cells of minus twelve thousand three hundred and forty-five and a half, published with `negative_notations: {"minus": 11, "brackets": 11}` and `thousands_marks: {" ": 11, U+202F: 11}`: each census is spent in the contract's own order of conventions, so the first eleven are written `-12 345.5` and the last eleven `(12 345.5)`. Two spellings of one number is the count of different cells published, so no cell spends a leading zero |
| `mixed_marks` | G7.5's rotation of marks: twenty-four `local` moments to the minute, published with `datetime_separators: {"lower_t": 12, "space": 12}`, whose marks are spread evenly over the ranks and whose tie goes to `lower_t`, the earliest name in sorted order. Rebuilt at plan P4-D220 (stage 2 closed by the owner rulings of 2026-09-17): it published eleven and eleven beside a pool of two, which contract D12 now refuses, and the pool is `pooled_marks`' to pin |
| `label_numbers` | G8.3a's class debt: forty-four rows of `ab-cd`, `5.1` and `5.3` with four held-back levels pooled on ten rows owing nine numbers, whose sizes G8.3 reads off the pool and its debts as `1, 2, 2, 5` (plan P4-D201); the class split makes nine `5 + 2 + 2`; `%.%` settled inside the number class as `5 + 2`; the gap `5.2` taken before the first outward step `5.0`; a number wearing no named form walked to `10.0`, which the census's pool of two cells lets it wear; and the word left over written in `@@-@@` |
| `label_number_tiers` | G8.3a's rule on what the census could hold and its tiers of places: fifty-five rows of `ab-cd`, `5.1`, `5.3` and `7`, a census naming `%.%` and `@@-@@` and pooling nothing, and held-back sizes read off the pool as `1, 2, 2, 5` (plan P4-D201); `%.%` settled as `5 + 2` into the gaps `5.2` and `6.9`; the number wearing no named form refused `10.0`, whose form the census would have counted and pooled, so that side ends and the walk takes the published whole numbers' places and writes the gap `6` |
| `pooled_marks` | G7.5 step 2: twenty `local` moments to the minute, published with `datetime_separators: {"(withheld)": 20}`, whose pool is split seven, seven and six over `upper_t`, `space` and `lower_t`. Rebuilt at plan P4-D220 (stage 2 closed by the owner rulings of 2026-09-17), from fourteen `upper_t` beside a pool of ten split five and five, and again at plan P4-D222, from twenty-four moments, a pool contract D12 now refuses because it would say all three marks were written |
| `slashed_pool` | G7.5 step 2's permitted marks and the `slashed-iso-datetime` member: ten year-first slashed stamps whose every mark is pooled, every one written with a space |
| `midnight_mixed_forms` | G7.5's whole dates: twenty-four days at midnight read jointly, published with `resolution_mix: {"iso-date": 13, "iso-datetime": 11}` and `datetime_separators: {"space": 11}`, whose forms are spread by the rotation and whose marks fall on the clock-writing ranks alone |
| `partial_midnight` | G7.5's move onto midnight: twenty-four `local` moments to the second, published with `n_at_midnight: 12`, whose rung ranks take their rungs and whose owed values at midnight are spread over the other ranks |
| `midnight_two_offsets` | G7.1 on the `utc` clock and G7.5's move onto midnight: twenty-four local midnight values at `+01:00` and `+02:00`, published at UTC with `all_at_midnight: true`, counted in seconds, whose rung ranks take their rungs and their offsets |
| `midnight_bare_offsets` | G7.4 and G7.5's whole dates on the `utc` clock: thirteen bare dates and eleven moments at `T00:00:00+02:00`, published with rungs at 22:00 and at 00:00 and two runs of ranks on one instant, whose ranks with a published instant settle their form and offset before the rotation |
| `date_gap_places` | G7.3's places for its pins inside their own units (plan P4-D130): forty dates over ten days, four pins on the first day and three on the last, whose gaps are drawn across the stretch between two places. Its mutant draws each gap over its two pinned days whole and the ranks beside the pinned days move |
| `date_thinning_week` | G7.3's choice between its two sets of places (plan P4-D138): forty dates thinning out over a week, five pins on the first day, where every pin at its unit's middle bends the count less than the straightest count and is taken. Its mutant keeps the straightest count and the ranks beside the first day move |
| `date_peak_heap` | G7.3's heaps (plan P4-D138): forty dates peaking over a week, two pins on each of three days holding neither end, each heap at its day's middle in the straightest count, which is taken. Its mutant moves every heap onto the straight line and the ranks beside the peak's days move |
| `month_first_widths` | G7.5's classes of width (plan P4-D132): eighty month-first dates publishing `padded` and `unpadded` at eleven each and `first-field-padded` at eleven beside `first-field-unpadded` at thirty; a date whose month alone is below ten is written from the first-field words, eleven of them reserved to the padded one. Its mutant writes that class as the joint words pad its field, and those dates take the other padding |
| `mark_spend_at_the_line` | G7.9's spend REFUSED (the dates pass of the stage-3 review, item 6): twenty-two dates in forty-four rows alternating a `T` separator and a bare date, so `datetime_separators` names `upper_t` at eleven -- `census_floor(11)` exactly. The construction is two folded spellings short of the published twenty-two, which is what the spend exists for, and spending a rank here leaves the census ten and one, which no twin's own description may print at all. Its mutant lets the spend run to the budget alone, and the column comes back with ten `T` marks beside one space |
| `may_month_names` | G7.5's `either` length (plan P4-D133): sixty day-first textual dates publishing `upper-abbreviated-hyphen-no-comma` at forty and `title-either-space-no-comma` at twenty; a date of May is written `02 May 2024` and every other `23-JUL-2024`. Its mutant offers May no `either` word and those dates take the hyphens and capitals |
| `reserved_name_floor` | G7.5's reservation (plan P4-D132): sixty day-first textual dates publishing `title-abbreviated-space-no-comma` at eleven -- the floor -- beside thirty `upper-abbreviated-hyphen-no-comma` and nineteen `upper-either-hyphen-no-comma`, whose twin holds fewer dates outside May than the real column, so a proportional share gives the title-case style fewer than eleven. Its mutant spends the class by the rotation alone and the style falls under the floor |

| `written_form_lines` | G2's written form end to end: an `sep=` hint, a byte-order mark, four lines before the table in three runs, an always-quoted header, a left-padded column, a second column taking three DIFFERENT quoting rules over its four cell classes, a trailing delimiter on the records and none on the header, a blank line after the third record, two runs of line endings, no ending on the last line and an end-of-file mark after it |
| `written_form_classes` | G2's quoting per cell class on the two classes `written_form_lines` never reaches (files review MAJOR 19, plan P4-D173): two columns under opposite rules, numbers and absent cells always quoted in one and text bare, text and empty cells always quoted in the other, over `.5`, `2.5e3`, `0012` and `-3`; `-`, `?`, `#N/A`, a cell of spaces and `NaT` read as absent under contract 5.4.1's vocabulary, beside `nat` and `3 kg`, which are text. It carries TWO mutants: every cell under the text rule, and absence read from seven spellings |
| `row_arrangement` | G2.1 in both its halves, which no single file can carry: the sort under the number collation with the row sequence written in place LAST, and the records holding nothing placed one leading, one trailing and one interior by exchanging cells within each column alone. It carries TWO mutants, one for each |
| `withheld_line_marks` | G2 and contract FD11: the shape a line before the table is published as, the narrowing of a mark the twin could not write — a quotation mark, and the table's own delimiter — to a line of TEXT, the run-length encoding of lines of one shape, and the neutral line written for each |
| `delimiter_reading` | review item CODEX-5's own measured file: every setting scored WITH the delimiter, the semicolon reading as two columns only once the space after it is skipped, and the comma reading the whole line as one field because text follows a closing quote |
| `date_distinct_reached` | G7.3's pass on the count of different values (plan P4-D192): sixty ISO dates over thirty days publishing twelve different days, one more than its pins hold, reached by runs of ranks on one day moving whole onto a neighbour's day inside their gaps. Its mutant withdraws the pass and the twin holds more days |
| `date_midnight_feasible` | G7.4's feasible spend of the offsets (plan P4-D254): forty-eight moments on two days at local midnight under `Z`, `+01:00` and `-05:00`, sixteen of each, published on the shared clock, whose gaps hold a midnight under one offset and none under the other two. Its mutant makes every offset look feasible, which is the lexical spend it replaces, and the ranks it leaves off midnight are written with a time of day |
| `date_absorbed_mark` | G7.9's spend of a mark the census leaves unnamed (plan P4-D245, ledger K-2B-51, the owner on 2026-09-21): a hundred and twenty-five moments at midnight on two days at a floor of eleven, a hundred and twenty written with a space and five with a `T`, so ruling 6 of 2026-09-17 counts the five into the commonest mark and the census publishes `{"space": 125}` beside a published three different values. Read as an instruction about the cells that census writes 125 spaces over two days -- two different values, a twin that reads back as binary rather than as a column of dates, and a report saying the twin missed its role, its statistical type and its count at midnight while the real table missed none. The construction gives the SHORTFALL the description publishes, one value here and never the five the table held, to the first permitted mark the census does not name, and spends fewer ranks on it than the census could print, so the twin described again counts the mark back into the commonest name. Its mutant withdraws the spend and the two different values come back |
| `date_endpoint_ties` | G7.4's hold on the ranks tied at an end (plan P4-D255): forty-eight moments on three days at midnight or noon under `+01:00` and `+02:00`, twenty-four of each, published on the shared clock, several ranks standing on the latest instant. Its mutant holds none of them and the larger offset is published for that end |
| `date_second_field_class` | G7.3's census key in the width pass (plan P4-D256): sixty month-first dates whose month is eleven on every one of them, so the census names `second-field-padded` alone. Its mutant asks whether either field is below ten, and the twin's dates fall on days counted under a joint word |
| `date_traded_merge` | The day's width KIND (plan P4-D294): sixty textual dates on three days, five, twelve and forty-three, publishing three different values and a width census of forty-three. Its mutant asks the narrower question -- does the day SHOW the width -- in place of the census's own membership, and the twin's dates move. It was frozen for G7.3's traded merge (plan P4-D258) and no longer reaches it: under a joint word every day counts into the census, so a column of one kind has no gap without a unit of its own kind. See the note below this table |
| `date_midnight_traded` | The MIDNIGHT half of P4-D258's paid merge (item 2 of the dates pass of the second Codex round, 2026-09-19): forty each of `2024-03-01T00:00:00`, `2024-03-02T00:00:00` and `2024-03-03T12:00:00`, eighty of them at midnight, on a column writing no width at all. The count passes strand a run of non-midnight ranks between midnight pins, whose gap holds no unit off midnight anywhere; the run merges onto a midnight unit and as many ranks elsewhere move between held units from midnight to the non-midnight one to pay the count back. Its mutant keeps the width trade and withdraws the midnight one, and the twin holds four different instants against the three the description publishes |
| `date_nonadjacent_merge` | The same three days at other words, pinning the same corrected kind question (plan P4-D294); its mutant is the same narrowing and it moves these cells too. It was frozen for G7.3's merge onto a unit that is no rank neighbour (plan P4-D258) and no longer reaches it, for the reason the row above gives |
| `date_two_kinds_nonadjacent` | G7.3's merge onto a held unit that is no rank neighbour (plan P4-D258), on a column carrying two width kinds: the description the producer writes of ten `08/15/2020`, thirteen `08/22/2020`, seven `10/05/2020` and six `10/5/2020`, publishing four different values and `first-field-padded` on twenty-three cells, the thirteen left standing on the fifth of October, which is of the other kind. A run drawn onto the seventeenth of September, of the named kind, has rank neighbours of the other kind on either side -- the ninth of September, whose two fields both show, and the fifth of October -- and merges onto the twenty-second of August past them. Its mutant offers the rank neighbours alone, the run stays, and the twin holds five different dates against four. Rebuilt by the repair pass of the carried date items of 2026-09-18: first frozen at three different values, which no table of these cells can publish |
| `date_two_kinds_traded` | G7.3's traded merge (plan P4-D258), on a column carrying two width kinds: the description the producer writes of eleven `03/19/2020`, eleven `04/10/2020`, seven `3/3/2020` and seven `3/03/2020`, publishing four different values and `first-field-padded` on twenty-two cells, the fourteen left standing on the third of March. A run of five ranks drawn onto the sixth of April, whose two fields both show, has no unit of its own kind in its gap, so it moves onto the tenth of April and three ranks of the eleventh and the nineteenth of March move onto a day of the other kind to pay for it. Its mutant makes no trade, and the twin's fourth date is the sixth of April on five cells in place of the eleventh of March. Rebuilt by the repair pass of the carried date items of 2026-09-18: first frozen at three different values, which no table of these cells can publish, and with the third of March written `03/03/2020`, the spelling that folded its own census away; G7.5 step 1 now writes it `3/03/2020` |
| `date_both_fields_disagree` | G7.5 step 1's joint word for a rank whose two fields both show, where the census names one-field words alone (plan P4-D294, amended by the repair pass of the carried date items of 2026-09-18): the description the producer writes of thirty-six DAY-first dates, eleven `19/03/2020`, eleven `10/04/2020`, seven `3/3/2020` and seven `03/3/2020`, publishing `second-field-padded` -- the month, on this member -- on twenty-two cells. The twin writes the third of March and the second of April with the month unpadded and the day padded, `03/3/2020` and `02/4/2020`, so no cell of it joins the named count to a joint word. Its mutant writes the joint word that agrees with the census, `03/03/2020`, and the twenty-two named cells fold into `padded` |
| `date_widths_reached` | G7.3's widths pass (plan P4-D192): eighty month-first dates leaning into the last quarter, whose census names `second-field-padded` alone on forty-four cells, reached by ranks moving whole days to the nearest day of the other kind. Its mutant withdraws the pass. The word was `unpadded` until plan P4-D294: a JOINT word absorbs every day, so a column of eighty cells can publish only eighty under it and the pass had nothing left to reach |
| `midnight_withheld_kept` | G7.3's rule for a withheld count at midnight (plan P4-D191): sixty moments to the minute whose pins stand a minute either side of midnight in turn, so about half the ranks between a `23:59` and the next `00:01` land at midnight; the published instants stand off it, so fewer than the line of eleven may, and the ranks at midnight step a minute later. Its mutant leaves them there |
| `numbers_carry_the_average` | G9.5 step 5's walk of the numbers' own lengths (plan P4-D190): ten cells of free text, eight numbers and two words, the words carrying both published length ends so the ordinary walk has no group to move; the numbers at their shortest average six fifths against a published two, and four of them are walked to three figures. Its mutant leaves the numbers at their shortest and the recount refuses the case |
| `workbook_as_written` | G2.2 steps 1 and 3 as part 2 of the carried items left them (plans P4-D187 and P4-D189): twenty-two figures of which eleven are stored as text, the count of numbers spread over the cells it fits so the text cells do not stand in the last rows; numbers wearing `00000` and moments wearing `yyyy-mm-dd hh:mm`, codes of the format language's own tokens written as the source wrote them, the moments' kind read off the code. It carries TWO mutants, one for each rule |
| `workbook_classes_by_spelling` | G2.2 as the files review left it (plan P4-D164 to P4-D171), at a floor of eleven: eleven `#N/A` errors between eleven labels, one of them `TRUE`, handed only to the cells they fit; a column of digit strings with one empty cell whose whole census is withheld, kept TEXT by its published commonest class; ISO dates written back as date cells and wearing the date kind of their published code where the format census is withheld; a column named `Unnamed: 3` given no header cell; a column name holding a carriage return written `&#13;`; and sheets published `Data`, withheld and `sheet2`, so the withheld one's placeholder walks past `Sheet2`. It carries FIVE mutants, one for each rule |
| `workbook_made_up_dates` | G2.2 step 0a and the calendar step 1 asks of the `date` class (plan P4-D291), at a floor of eleven: a column whose census is withheld whole and whose commonest class is `date`, sixteen of whose twenty-two cells wear the ISO shape and name no day, each field brought to the nearest value the calendar allows and the six that DO name a day unmoved; the same asked of a clock, and of a day that moves under one; and a column the description does not store as dates, whose made-up cells the calendar keeps off the `date` class and which are written as shared text. It carries TWO mutants, one for each half of the rule |
| `workbook_sheet` | G2.2 end to end, every part of the package as TEXT: the class of each cell taken from the census and never from the twin's characters, a column of digit strings published as TEXT staying text, the alignment that makes records holding nothing exist at all, a built-in format code beside a canonical one written as a custom format, the table's sheet second of three so the first is hidden, a withheld sheet name written neutrally, and a shared-string table filled in the order the sheets are written |

Each case is small enough to read by hand — at most a few dozen cells —
because a vector nobody can check by hand is a vector nobody checks.

**WHAT PLAN P4-D294 COST THIS TABLE, AND HOW IT WAS PAID BACK.**
Correcting a day's width KIND to the census's own membership question
made the two branches of plan P4-D258 — the traded merge and the merge
onto a unit that is no rank neighbour — unreachable by the two cases
frozen for them. Both are textual columns under a JOINT word, and a
joint word absorbs every day that shows no width at all, so such a
column carries ONE kind and no gap of it can be without a unit of its
own kind. The two cases were re-registered against the rule they DO
pin, which is P4-D294 itself: asking the narrower question moves their
committed cells. The merge-close of 2026-09-18 measured 500 candidate
columns for a replacement and found none. A census naming one word over
EVERY parsed cell leaves the twin nothing of the other kind to hold,
whatever the word; what reaches both branches is a census naming one
word over FEWER cells than that: a ONE-FIELD word whose
unnamed remainder, at least the line and written by words that each
fall below it and fold into no named one, stands on days of the other
kind. Such a column carries two kinds, and both branches are reached on
it. `date_two_kinds_traded` and `date_two_kinds_nonadjacent` are two
such columns, and each mutant withdraws exactly its own merge (the
carried date items of 2026-09-18).

**Every case must also FAIL when the branch it exists for is removed or
reverted**, and that mutant is committed beside it. A case a withdrawn
rule would still write is a case that tests nothing, which is exactly
how the ninth case's branch carried a withdrawn rule for two rounds.

**The mutants are ONE TABLE, and its keys are the case set** (review
item P2-C4-C2). Four of the thirteen carried a mutant of their own and
nine did not, which is the same gap in a quieter form: a case whose own
rule can be reverted with every committed byte unchanged proves nothing,
whether it is named in this list or not. So the mutants are committed as
a single table whose keys are asserted equal to the whole case set — a
case added without one turns that assertion red — and each entry must
either change its own case's cells or stop the oracle from building it.
Each entry also builds its case UNMUTATED first, so a mutant that would
have refused for some unrelated reason cannot pass by refusing.

**Why the ninth case exists** (2026-08-11; review item P2-C2-F7). The
oracle carried revision 1's withdrawn rule — that `all_whole_numbers`
true means every group is written from the figures — and no frozen case
reached it, so byte equality never tested it. A branch no vector reaches
is a branch that can bless a withdrawn rule the day somebody freezes a
case on it. `identifier_whole_numbers` reaches it: twelve cells over
eight groups, `n_all_digits` 4 and `n_code_alphabet` 8, so four cells
fall in the figures, four in the code alphabet and four outside it, and
each band writes the whole-number spelling this section fixes for it.
Two doubled groups answer for each of the two non-figures counts, so the
case also pins that both alphabet counts are counts of CELLS answered
for by whole GROUPS.

**Why the four after them exist** (2026-08-12; review item P2-C3-F3).
The nine above are sound where they run, and between them they reach no
`numeric_unrepresentable` column at all, no joint class-and-alphabet
grid on free text, no fold collision that a case change cannot build,
and no cell wearing the literal `decimal`, `leading_zero` or
`leading_plus` style. So the defect G10.5 step 2 records — a generator
choosing a cross-tabulation the description never published, and losing
six exact counts on a genuine six-row column — left every committed byte
unchanged, and so would a repair that took the edge spacing back out of
G9.3. Each of the four reaches exactly one of those branches:

- **`unrepresentable_joint`** is that six-row column, published fact for
  published fact. Its three margins have one joint answer, the walk
  finds it, and the recount of G10.5 step 6 reads all twelve counts back
  off the finished cells. Withdrawing the too-small shape — which is
  what spending `n_whole` on the too-large cells amounts to — leaves the
  column with no packing at all, and that is the committed mutant.

  **It reaches this role and NOT the second spelling family**, which is
  why revision 5 adds a case rather than widening this one: every cell
  it freezes is a four-hundred-character digit string or the fixed
  contradictory construction, so the exponent family could have been
  withdrawn whole with both committed files byte-identical.
  `unrepresentable_exponent` is six cells published at five and six
  characters, widths no digit string can be written at; its mutant puts
  the too-large shape's floor back to the digit string's own 310 and
  the recount then reads `min_length` as 310 against a published 5.
  Writing it is also what found that this section had never said
  whether the walk counts per shape or per shape and sign — no earlier
  case carried a positive and a negative group of one shape, so two
  conforming programs could differ and agree on every committed byte.
- **`free_text_joint`** is four cells over three groups whose class
  counts and alphabet counts have a joint answer that neither margin
  settles alone: deciding the classes first hands the two singletons to
  the numeric class and leaves one doubled group owing one code-alphabet
  cell and one wide cell, which no whole group can answer for.
- **`identifier_edge_spacing`** is written in figures alone, so its one
  identity holds no character with a case and the case-flip half of
  G9.3's family is empty from the start. All three partners come from
  the edge spacing, and the case-flip-only construction revision 4
  carried cannot build the column at all.
- **`numeric_point_free_styles`** publishes the three styles the floor
  makes expensive — eleven cells each — and pins that a cell named
  `decimal` carries a point, a cell named `leading_plus` a `+` and a
  cell named `leading_zero` a redundant `0`, each recounted by the
  contract's own first-match ladder. Its ladder is flat, which also pins
  that G5.3's clamp is not decoration: the four IEEE-754 operations of
  the convex form can land one unit in the last place away from a value
  both rungs agree on, and the clamp is what brings it back.

**Why the fifteenth exists** (2026-08-13; owner decision 11). The
independent oracle still implemented the pooled-plain rule the Phase 3
repair retired, and no committed case reached the branch, so both files
stayed byte-identical while the check they exist to be proved nothing
there. `numeric_pooled_spelling` reaches it, and reaches owner decision
10's point-free spelling at any width in the same twelve cells: its
published smallest value carries a decimal point, so the cell that must
read back as it can wear no point-free form and the held-back cell is
the one that lands there; its published largest is ten to the twentieth,
whole, and written in figures. **What the case freezes is the CELLS**,
and the pooled rule's own difference is in the recount rather than in
them -- the retired rule wrote the same canonical text for that cell and
differed only in what it then owed -- so the recount identity of 7.5.7
is guarded by the style batteries and the report's golden bytes, and
this case guards the width.

**Why the fourteenth exists** (2026-08-12; review item P2-C4-C3). The
obligation G7.5's endpoint route carries had been lowered twice and
argued over in three rounds, and not one committed case held a seconds
field of `60` — so an implementation that sent the two ends back through
the ordinal space of G7.1 landed on the minute after such an end and
left every frozen byte where it was. `leap_second_endpoint` is twelve
cells on the `local` clock at `time_precision` `second`, published from
`23:00:00` to `23:59:60` on one evening, offsets `(none)` throughout. Its
first and last cells are the two ends written from their own fields, its
ten interior ranks are the ordinal transform this section already
freezes, and its committed mutant is the ordinal route put back: that
mutant writes the following midnight in place of the published end and
must fail. The pair this route cannot show on the SHARED clock is
refused by the profile contract's D10 before generation, so it is a
loader case and not a vector case — a description no loader accepts has
no twin bytes to freeze.

**`numeric_decimal_styles` was rewritten again at plan P4-D221** (stage 2
closed by the owner rulings of 2026-09-17). Its published map of three
pooled plain cells beside eleven cells in each exponent form holds a
pool below `parsing.census_floor` beside named forms, which the profile
contract's P6 now refuses, so no loader reads the case. The source is
now written in the two exponent forms alone, twelve lower-case and
thirteen upper-case, with the ladder and the spelling counts unchanged:
the rebuilt cells write the smallest value `1E-05`, the largest `1e+16`
and `1E+16`, four spellings of `1000000000000000` on the flat top, and
twenty-three folded identities against twenty-five raw spellings. The
cases `numeric_integer`, `numeric_pooled_spelling` and
`saturated_integers` published censuses the same rule no longer admits
-- field-width pools of four and nine beside a named width, and a forms
map pooling one cell beside a named count -- and now publish what the
producer writes for their sources; their cells did not move.

**`numeric_decimal_styles` was regenerated against this revision by the
oracle's own owner** (2026-08-11; review items P2-C2-F2 and P2-C2-F3).
The cells committed before the two repairs above froze the behaviour
both items rejected: they held nought `plain` cells against a published
three and three `decimal` cells against a published nought, and
twenty-one folded identities against a published twenty-three. Derived
again from this revision alone, the same case comes out with `plain` 3,
`exponent_lower` 11 and `exponent_upper` 11 — its published map exactly
— and twenty-three folded identities, its published count exactly, at
the cost of one raw spelling (23 against a published 24), which the
exact map forces because the column holds only one value a point-free
spelling can be written for and all three `plain` cells must therefore
share it. G6.5's stated precedence — the published style counts are met
first and distinctness is met within them — is what decides that trade,
and G12.8's envelope prints the range the raw count fell in.

The vectors are the independent artifact of P2-D7 and are written by a
tool that imports nothing from `src/`. Reconciling that tool to this
revision, regenerating the file and reviewing the affected proof and
bytes belonged to that tool's owner, exactly as review item P2-C2-F7
directed for the identifier branch it found stale; an implementer
editing the independent artifact to agree with implementation work would
weaken the provenance the artifact exists for. The reconciliation was
carried out from this document, the committed bytes were rebuilt and
re-registered, and `tests/test_generation_reference.py` now holds the
implementation to the regenerated case with no exception of any kind.

**Why the seventeenth exists** (2026-08-27; residual R-P4-17). Phase 4
added four roles -- `long_tail_labels`, `time_of_day`, `affixed_number`
and `joined_numbers` -- and for a year of commits not one frozen case
reached any of them, so every rule those roles carry could be changed,
lowered or withdrawn with all sixteen committed cases still passing
byte for byte. `long_tail_levels` is the first to close, and it closes
the cheapest of the four: forty rows, twenty-one folded identities at a
floor of eleven, one published level of eleven rows carrying one
variant, and twenty suppressed levels covering the other twenty-nine.

**What it pins, stated at its real width.** The role has no generator
branch of its own: a long tail is ADMITTED by rules a categorical
column would fail -- its folded count stands above the ceiling, and the
`level_ceiling` key categorical must carry is one this role may not --
and it is then written by the shared G8 machinery. So the case pins
admission and routing plus G8.3's stand-in walk, and it does NOT pin a
transform belonging to the role. An implementation that accepted the
profile and then discarded the role tag, sending every label column
down one path, would still write all forty cells. That is a real limit
of this case and it is written here rather than left for a reader to
discover.

Its mutant starts G8.3's stand-in walk one spelling along, which
changes the stand-ins and nothing else. The case also carries a form
census of `{"@@@@-@@": 29}`, which is what makes those stand-ins words
rather than numbered labels: emptied, the oracle refuses to build the
case at all, because `group-1` carries a figure and could read back as
a number. An earlier draft published `{"@@@@-@@": 29, "(withheld)": 11}`
instead, a census no profiler can write -- the eleven published cells
are spelled with a SPACE and so have no form at all, and `(withheld)`
means a group too small to name, which eleven cells at a floor of
eleven are not. The committed census was measured against the profiler
on a table of this exact shape. Correcting it left every frozen cell
unchanged, which is worth recording: what was wrong was the
DESCRIPTION's producibility, not the transform under it.

**Why the eighteenth exists** (2026-08-27; residual R-P4-17).
`time_of_day` and `joined_numbers` had no section in this document at
all, and `affixed_number` a single passing mention, so no vector for
any of the three could be built from the specification -- there was
nothing to build from. G6A, G6B, G7A and G4.3's rows are that work, and
`clock_ladder` is the first case they make possible.

It is deliberately a column with NO SLACK. Its ends are `08:00:00` and
`08:00:10`; the eleven ordinals between them inclusive are exactly as
many as the cells that parsed; and it publishes every value different.
So G7A.4's all-different repair -- EXACT for this role where every
other shape's distinctness falls to an envelope -- has nowhere to give:
each interior rank must land on the one ordinal left for it. Its mutant
withdraws the STEP-UP and keeps the clamp, and the same column then
comes out holding `08:00:01` and `08:00:06` twice each, so the repair
is doing the work here rather than merely being present. The case also
carries one cell that is not a clock time, which puts a stand-in beside
the parsed cells (G7A.5), and it reads its ladder in SECONDS OF DAY --
the form's own unit -- which is the whole of what separates this role
from the date role whose transform it borrows.

**Why the nineteenth exists** (2026-08-27; residual R-P4-17).
`affixed_brackets` pins the rule its role exists for. A column of this
role publishes TWO SETS of class counts and they are not the same set:
the universal counts answer for the CELLS, and a cell reading `[12]` is
not a number, so such a column publishes `n_numeric` of nought and
twelve cells of ordinary text; the quantitative block answers for the
CORES, where `n_core_numeric` is twelve. Its mutant hands the numeric
machinery the cell counts, and the oracle then stops at the WORD
BUDGET — G4.3 reads that over the cores too, so cell counts ask for no
content words at all and no cell can be built.

Writing it independently found a fact about the role the oracle did not
have: **a block of this role must carry its own REMARK**, the sentence
naming the shared text, saying how many cells wore it, and naming
`--identifier` as the route for a column of codes (contract AF-R). The
loader refused the case until it was there, which is the argument this
residual makes, arriving for the third time.

**It is also the one case in either file where a conforming generator
MISSED a published fact and said so — until the integer-grid landing
took the miss away.** Its source column held twelve different numbers
and it publishes twelve; the twin held eleven, because values drawn to
a published ladder repeat more evenly than real ones did, so `23` came
out twice. G6.5a's pass had been declining every whole-number column,
this case is one, and the twin holds twelve now. `n_distinct_values`
is EXACT-OBSERVABLE since amendment A-P4-55 of 2026-09-04 -- it was
REPORT-ONLY when this paragraph was written, and the owner ruled it an
obligation because analysis code groups by and counts distinct on
numeric columns -- and **no committed case exercises a reported miss of
it any more.** The reporting control itself is not
lost — `tests/test_p2c4f3_style_capacity.py` asserts it seed by seed —
and what R-P4-145 records is narrower and older than this case: the
frozen harness compares cells and CSV bytes and has never read a
deviation or a report line, so no committed case pins what a twin
SAYS. Every other case
carrying that key publishes the figure its OWN TWIN reaches, so none of
them can exercise the miss: an adversarial read found that the oracle
was overwriting the field with a count of the finished cells, which
puts a fact about the twin where a profiler publishes a fact about the
table. A case may now publish its own, and this one does.

**Why the twentieth exists** (2026-08-27; residual R-P4-17, and it
closes it). `joined_readings` pins G6B.4's pairing walk — the only
SEARCH in this method, and the only place synthtwin reproduces
structure between two quantities at all.

**It was designed against a vacuity check rather than assumed to
work.** The first draft published an agreement of 0.9983, and a
rank-for-rank start already agrees at about 1.0, so the walk found
nothing to do: removing step 5 entirely left every committed byte where
it was, and the case would have pinned only the sort and the start
rule. The committed column publishes **0.4323** instead, holds the
earlier position above the later in only seven of twelve rows, and
repeats values in both positions; measured with step 5 withdrawn, six
of its twelve cells move, and that is the mutant.

**And writing it validated the section.** The walk is 237 lines in the
shipped generator; the oracle's is written from G6B.4's text alone —
the sort key, the binary64 sequential mean, the two thresholds, the
last position moving, the three-term distance and its scaling, the
zero-based ranks, the fixed divisors, the `0.0005` stop, the `200 * T`
ceiling, two words a try from a cursor that restarts at zero, the skip
conditions, accept-on-equal and the exact restore — and it writes the
same bytes. A section that could not be reimplemented from its own
words would have shown here.

**WHAT ONE CASE PINS IS NOT THE WHOLE WALK, and the difference is
measured rather than left to be assumed.** The committed column was
chosen against that check: a first draft published an agreement of
0.9983, which a rank-for-rank start already meets, so withdrawing the
walk entirely changed no byte and the case pinned the sort and the
start rule and nothing else. The committed one publishes **0.4323**,
holds the earlier position above the later in only seven of twelve
rows, and repeats values in both positions.

Withdrawn one at a time, these move its cells, and are pinned:

| rule of G6B.4 | cells moved |
|---|---|
| the walk itself (step 5) | 6 |
| the reserve cursor's restart at word zero | 6 |
| the `0.4` threshold's VALUE — moving it to `0.9` pulls this column into the permutation branch | 11 |
| accept-on-equal against strict improvement | 5 |
| that a try ceiling EXISTS (`200 * T` down to `1 * T`) | 5 |
| the `part_above` term of the distance | 5 |

**And these do not move its cells, so they stand on this document's
word alone:** the ceiling's exact VALUE (`100 * T` writes the same
bytes as `200 * T`); the skip when both drawn seats hold one spelling;
the `0.0005` stop (even `0.0` writes the same bytes, because this
column never stops on distance); that a start rule exists AT ALL
(deleting both branches is identical, because an agreement of 0.4323
takes neither); and the scaling of the distinct-cell term.

The rank origin is absent from both lists on purpose: as stated in
G6B.4 step 4 it is not byte-determining in either direction, so no case
can pin it and none should claim to.

Reaching the five unpinned rules needs further columns shaped for them.
Saying so is the rule about silent coverage: a case that claims a whole
search and holds up part of one is the failure the frozen files exist
to prevent.

**All four roles Phase 4 added now have a frozen case**, which is what
residual R-P4-17 asked for.

**Why the twenty-second and twenty-third exist** (2026-09-14; plan
P4-D39). G7.1 and G7.5 changed on that date, and a rule no case
reaches can be withdrawn with every committed byte unchanged.
`midnight_days` pins the day unit: its mutant counts the column in
seconds, the rule withdrawn, and the interior ranks then land part-way
through a day. `mixed_marks` pins the rotation and the tie (and, until
plan P4-D220 moved it to `pooled_marks`, the pool): its mutant spends
the names from the first rank upward, and the marks then cluster by
date.

**Why the twenty-fourth exists** (landing 2b.4). Every label case
before it published no number, so G8.3a -- a held-back number written
as a number -- could be withdrawn with every committed byte unchanged,
and until that landing the method had no such rule at all.
`label_numbers` reaches each of its steps once: the class split, the
forms inside a class, the gap before the outward step, the number that
must wear no named form, and the word left over. Its mutant withdraws
the gaps, so the largest held-back level is written below the smallest
published number instead of beside it. Writing it moved the oracle
too: its stand-in walk was one greedy pass over the neediest form with
one counter for both kinds of spelling, not G8.3's exact settlement
with a cursor per form, and the two label cases already committed
happened to give the same bytes under both. The oracle carries the
settlement now. It still states no reading of G9.5 step 7's forms, and
steps 3a's form lengths and 3b's band exchange act only where a column
of text names a form, so it refuses to freeze such a case rather than
reason around one.

**Why the twenty-fifth exists** (landing 2b.4's repair). `label_numbers`
pools two cells, so its number wearing no named form may write `10.0`
there, and a rule that wrote any form the census does not name gave the
same bytes -- while on a real column of one-decimal readings whose census
named `%%.%` and pooled nothing that rule wrote `100.3` and a standard
deviation 2.4 times the table's. `label_number_tiers` pools nothing, so
the rule ends that side of the walk, and it publishes a whole number, so
the walk's second tier writes `6`. Its mutant withdraws the census rule
and the level of two moves to `10.0`. Writing it moved the oracle again:
it now carries that rule, the tiers, the second settlement of the forms
where the levels given none starve, the code band's numbers held to the
exponent nought, and the two free-text exchanges of G9.5 steps 3b and 3c,
each from the text; no cell of an earlier case moved.

**Why the twenty-sixth to the thirtieth exist** (landing 2b.3,
2026-09-15). G7.1, G7.4 and G7.5 changed on that date. `pooled_marks`
pins the pool's split: its mutant puts the pool back on the commonest
named mark. `slashed_pool` pins the permitted marks and the new format
member: its mutant offers a slashed stamp all three marks.
`midnight_mixed_forms` pins the narrowing of owner decision 4: its
mutant writes every rank as a moment. `partial_midnight` pins the move
onto midnight: its mutant keeps the interpolated instants.
`midnight_two_offsets` pins the reading on the shared clock: its mutant
counts the column in days, which reads a rung at 23:00 as the day
before.

**Why the thirty-first exists** (the repair pass of landing 2b.3,
2026-09-15). Its skeptic found two rules no case reached: regenerated
after the rules changed, both committed files were byte-identical.
`midnight_bare_offsets` pins the settling of the ranks whose instant the
published tail fixes: its mutant settles the two ends alone, and rung
ranks are written as the day before and at `T02:00:00+02:00`.

**And why the thirty-second was WITHDRAWN** (landing 2b.6).
`accidental_midnight` pinned the move off an accidental value at
midnight on a column publishing `n_at_midnight` of nought. No column
publishes that nought any more, so there is no rule left for a case to
pin and the case went with it rather than being left to freeze a branch
nothing reaches. Withdrawing a case is recorded here because a case that
quietly disappears is a branch that quietly stops being checked.

### G14.4 What the vectors do NOT freeze

- **The word stream.** The vectors take words as inputs. The stream from
  a seed is bound by the golden twin and report hashes on every CI cell,
  with the numpy floor proved by the `minimums` job.
- **The report's bytes.** Golden-tested separately (P2-D10).
- **Anything about a real table.** No value in the file comes from any
  real or synthetic table; every published fact in every case is written
  by hand in this document's own neutral vocabulary.

---

## Conformance checklist

An implementation conforms to this document when all of the following
hold, and each has a test:

1. One generator, created once from the seed, threaded explicitly; no
   module-level randomness; no second random source (G3.1).
2. Every random quantity comes from the one draw form of G3.2, with
   `dtype` given as the string `"uint64"` and each element converted by
   `int(...)` before use.
3. The word count per column matches G4.3 exactly, and the reference
   vectors' `word_budget` is asserted against it.
4. Columns are consumed in `columns` list order; the first word of the
   run belongs to the first column (G4.1).
5. Numeric endpoints are exact; the nine interior rungs sit inside the
   two-sided window of G5.6; the rung-ignoring, rung-permuting,
   rung-swapping and endpoints-only mutants each fail it.
6. `n_zero`, `n_negative`, `integer_valued`, the four class counts and
   the published style counts are each recounted from the WRITTEN CSV
   and match exactly, outside the named deviations of G12.
7. Datetime cells carry the published precision and offset state, and a
   profile → twin → profile round trip returns the same `resolution`,
   `time_precision`, `subsecond_digits`, `utc_offsets` and
   `datetimes_read_at` (G7).
8. Label counts, variants and withheld level sizes are recounted from
   the written CSV and match exactly (G8).
9. The capacity rule is decided before any file is created, and the
   named refusal leaves every byte on disk unchanged (G9.4).
10. Twin bytes are identical for identical inputs; a different seed
    changes interior values for a profile that has a random degree of
    freedom; and twin bytes are seed-INVARIANT for a fully determined
    profile — one whose published counts pin every cell (G4.2 makes this
    true: an arrangement of identical entries is identical).
11. EVERY committed vector file rebuilds byte-for-byte in CI; the oracle
    imports neither `synthtwin`, nor numpy, nor pandas (G14); every case
    G14.3 names is present; and each one FAILS when the branch it exists
    for is removed or reverted, because a case a withdrawn rule would
    still write tests nothing (G14.3).
12. The packing of G9.5 meets every quota of EVERY margin exactly
    whenever an assignment of whole groups exists; its margins are the
    families the description publishes and no others, so no
    cross-tabulation of them is chosen by the implementation (G10.5);
    and **nothing counts the walk's work and stops it** — a description
    a producer can emit reached the ceiling that once did (P2-C3-F1),
    so the only end of the walk is the finite state space of G9.5.

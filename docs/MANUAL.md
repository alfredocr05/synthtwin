# synthtwin: the manual

This manual is for the physician who holds the table and makes its
twin: you run synthtwin on the protected computer, answer its questions,
and hand on the twin. It says what to type, what each question means,
what the twin is and is not, and what to do when synthtwin refuses
something. The project's front page, `README.md`, is the long account
for whoever reviews or changes synthtwin; this page is the short one.

## 1. What the twin is, and what it is not

**What it is.** A made-up table with the same columns, the same number
of rows and the same kind of file as yours (a SAS dataset's twin is SAS
transport). Each column behaves like
your column: the same kinds of values, the same spread, the same common
labels and the same share of empty cells. The relations between columns
come from the inside record, a model of your table that synthtwin fits
on the protected computer and keeps there: a twin drawn from it keeps
how a number or a label depends on the columns before it, which cells
are empty together and, where a column says which patient a row
belongs to, each patient's rows in order with their dates as one
timeline. Every date it draws keeps the real month, weekday and time of
day, with the day of the month made up. Record numbers, names, places
and the other identifiers the Safe Harbor rule lists (45 CFR
164.514(b)(2)) are made up.

**What it is for.** Writing and testing your analysis code, with any
help you like, on a table that may leave the protected computer. The
finished code then runs, unchanged, on the real table, back on the
protected computer, and that run gives the results.

**How well it works, measured on invented tables** of 20,000 rows, never
on real data: 405 runs of analysis scripts (comparisons, regressions,
survival, ordinal and multinomial models, prediction, missing-data
methods) all ran unchanged on the twin, and the twin reached the same
statistical conclusion as the real table in 94.4 per cent of runs,
against 89.8 per cent for a second real sample of the same size. On
twelve more advanced analyses: 79.6 against 78.7 per cent. This is a
measurement on invented tables, not a promise about yours.

**What it is not.**

- **Not a result.** Numbers computed on the twin are not research
  results. The relations are approximate, and the twin can show one your
  table does not have: check on your table any effect the twin shows,
  and never read a negative finding from the twin.
- **Not your rows.** synthtwin samples or copies no row of your table:
  every cell is worked out from the description, the inside record and
  a seed. That says where the values come from. It does not say no twin
  row can equal a real one: holding the published counts exactly can
  force a twin row to match a real one, with nothing copied.
- **Not a privacy guarantee.** synthtwin offers no formal privacy
  guarantee. All six files a run leaves in its folder -- the
  description, the plain-language summary beside it, the questions
  file, the twin, the twin's report and the quality report -- carry
  facts computed from your real data, so your institution's rules for
  real-derived material apply to all six.
- **Not a twin of a moved description.** A twin built from the
  description alone, on a computer where the inside record does not
  stand, carries nothing between columns but the tables of counts the
  description publishes. Make the twin on the protected computer.

## 2. Before you start

- **One table**, the final analysis table: synthtwin does not join
  tables. Several rows per patient are fine.
- **At least 20,000 rows**, and at least 1,000 patients where patients
  have several rows. synthtwin refuses anything smaller and writes
  nothing.
- **A file it reads**:

  | Your file | Read | The twin is written as |
  | --- | --- | --- |
  | CSV or other delimited text (comma, semicolon, tab, vertical bar) | yes | the same |
  | Excel workbook | yes | a workbook |
  | Parquet | yes | Parquet, uncompressed |
  | SAS transport (`.xpt`) | yes | SAS transport |
  | SAS dataset (`.sas7bdat`) | yes | SAS transport (`.xpt`) |
  | Stata (`.dta`) | yes | Stata |
  | SPSS (`.sav`) | yes | SPSS, uncompressed |
  | Arrow (Feather), ORC, SPSS portable | refused by name | -- |
  | FHIR or HL7 messages | not read | -- |

  Column types, display formats, labels and value labels are kept
  where they may be published, so code that loads the real file loads
  the twin the same way. A file's own label, notes, author and dates are
  never read. A CSV saved from Excel must not be opened and saved in
  Excel again: Excel rewrites codes such as `0250` and dates.
- **Memory and time.** The whole table is read into memory. Measured on
  an invented table of 2,000,000 rows by 50 columns, the whole run took
  13.05 hours (9.8 without the round of answered questions) and used
  about 4.1 GB of memory at the most, half of an 8 GB computer. Close
  other programs, keep the computer plugged in, and choose a day without
  a planned restart.

## 3. Install

**On a protected Windows computer** use the ready folder: one zip,
checked by its SHA-256, unzipped, started by double-clicking
`START-HERE`. It needs no internet, no administrator and no Python.
`docs/windows-install.md` walks through it step by step.

**On a Mac or Linux computer** use the offline bundle for that computer
and its install script, as the front page's "Installing" says. Each time
you open a new terminal window, switch synthtwin's private environment
on first, in the bundle's folder (`source .venv/bin/activate`).

Then check the computer against your table. It never opens the table;
it asks the computer for the file's size:

```
synthtwin doctor my-table.csv
```

Each line marked PROBLEM says what to do. On Windows the memory line
says `note`, because Windows does not let it read the memory: read it in
Task Manager instead.

## 4. Make the twin: one command

```
synthtwin twin my-table.csv
```

synthtwin reads your table, asks its questions in one round (section
5), and only then writes. Everything goes into one folder beside your
table, `my-table-synthtwin`:

- `my-table-twin.csv` (or a file of your table's kind) -- the twin;
- `my-table-twin-report.txt` -- what the twin carries; it opens by
  naming the columns drawn from the inside record;
- `my-table-profile.json` and `my-table-profile.txt` -- the description,
  and the same in words;
- `my-table-questions.json` -- your answers, kept, so the next run in
  this folder asks nothing;
- `my-table-twin-quality.txt` -- the quality report: which of the
  description's facts the twin meets and which it misses.

The inside record is written in your account's own private folder, not
beside the table; the screen names its place and size and never shows
what it holds.

A large table can keep the screen still for hours: that is normal. Do
not click inside a Windows window while it works (a click pauses it;
press Esc if the title begins with "Select"). To stop, press Ctrl+C.

To make another twin of the same table, with nothing asked again:

```
synthtwin twin my-table.csv --replace --seed 2
```

## 5. The questions, and what Enter does

Some things your values cannot settle: whether a column of numbers is a
measurement or a code, whether a column names a person, whether a
five-figure number is a ZIP code. synthtwin puts every such question on
the screen in one round, before it writes anything, grouped by kind:

1. **Who each row is about.** Where your table may hold several rows a
   patient, it asks whether one person can stand on more than one row.
   Type the name of the column that says which patient a row belongs to,
   exactly as the first row of your table writes it, and press Enter.
   Enter alone means "not sure": the table is described, but nothing
   that links two columns is published, and the twin keeps nothing about
   each patient's rows.
2. **Columns that may name a person, a place or a date**, the
   identifiers of the Safe Harbor rule of 45 CFR 164.514(b)(2).
3. **Ages over 89.**
4. **Numbers that may be dates of people.**
5. **Number columns read as measurements.**

In each list, **Enter alone keeps every column as synthtwin read it**,
which is how a run with nobody at the keyboard reads it. For a column
that may identify a person that is the cautious reading: its values are
held back and the twin writes made-up values there. **Typing a column's
name changes that column's reading**; nothing else does. A last screen
says what the twin will hide, cap, blank and release before anything is
written.

To end your answers early, press Ctrl+Z then Enter on Windows, or
Ctrl+D on a Mac or Linux computer. Your answers stay in
`my-table-questions.json` in the folder; to change one, write another
of the offered answers beside `your_answer` there, save it, and run the
same command again with `--replace`.

## 6. What may leave the protected computer

**Only the twin and its report, and only after your institution's
approval.** Read the report first: it says what the twin carries.

The description, the summary, the questions file, the quality report and
the inside record stay on the protected computer. The table itself, and
any part, sample or copy of it, never leaves.

Before the twin leaves, run the five twin-versus-real checks. They read
the twin against your table, on the protected computer, for copied
rows, rows too close to a real one, copied patients, real identifiers
and rare real dates, and combinations only one real row holds, and print
counts and a verdict, never a value. On a Mac or Linux bundle install,
with its environment switched on:

```
python -m synthtwin.twin_checks my-table.csv my-table-synthtwin/my-table-twin.csv
```

The Windows ready folder has no command word for them yet. That is a
known gap: until it is closed, ask the project before a twin leaves a
Windows computer.

## 7. Write the code on the twin, run it unchanged on the real table

1. Load the twin exactly as you will load the real table: the same
   column names, in the same order, in the same kind of file.
2. Write and test the whole analysis on the twin, with whatever help you
   like.
3. Bring the finished code back to the protected computer, point it at
   the real table, and run it there. That run gives the results.

What can differ between the two runs, and why:

- **The day of the month** of a drawn date is made up, so an analysis
  of the exact calendar day (a holiday, a pattern by day of the month)
  cannot match. Weekday, month and time of day are kept.
- **Identifiers are made up.** Joining the twin to another table by a
  record number finds nothing real; two twins of one study join by the
  patient column only when made with `--linked-to`.
- **Rare values are pooled.** A label fewer than 11 rows hold is not
  named, so the twin writes made-up labels for those rows. Code that
  names a rare label finds it on the real table and not on the twin.
- **A step that depends on more than the twin holds**, such as a cut
  into quartiles of a column whose ends are not published, can succeed
  on the twin and fail on the real table.
- **Effects are approximate.** Check on your table any effect the twin
  shows; never read a negative finding from the twin.

## 8. When something is refused

synthtwin never stops without saying what went wrong and what to do
next, and a refused run writes nothing, so it is safe to correct and run
again. The common ones:

| The screen says | What to do |
| --- | --- |
| "synthtwin makes twins of large tables only" | The table has under 20,000 rows, or under 1,000 patients with several rows each. Describe the whole extract, not a sample; combine sites or years into one table. |
| "something is already at one of the names it would write" | Add `--replace` to the same command, or move the old files away. |
| "was not accepted ... is a link" or "... a network location" | Copy the table into a folder on this computer's own disk (on Windows, `C:\Users\YOU\twin-work`). |
| "The twin will be built from the description alone" | The inside record could not be written where it belongs, and the screen says why. Stop: a twin built this way carries nothing between columns. Ask whoever looks after the computer to make your account's own data folder a plain local folder, then run again. |
| a number under 11 after `--smallest-group` | 11 is the least: the number can be raised, never lowered. |
| an answer the question did not offer | Use one of the answers the message lists. |
| a file kind refused by name (Feather, ORC, SPSS portable) | Save the table as CSV, Parquet, Stata, SAS or SPSS (`.sav`) and run again. |
| the quality report ends "missed" (exit status 3) | The twin missed something its report names. Read the named lines; the twin can still be used for code, but check that what it missed does not touch your analysis. |

## 9. Limits to know

- One table at a time; tables are not joined by their contents.
- Groups of rows other than the patient (per visit, per site) are not
  modelled beyond what the relations carry; where no column names the
  patient, rows are built on their own.
- Free text and structured notes are made up in the layouts at least 11
  different people write: only words that many people write reach the
  twin, and every number in them is drawn anew.
- A SAS dataset's twin is SAS transport; Parquet and SPSS twins are
  written uncompressed (a Parquet twin about 2.4 times larger in the
  measured case); SPSS text value labels, a file's notes and its sort
  order are dropped.
- The quality report checks only what the description publishes. It
  cannot tell a synthetic file from a real one, and it does not check
  the relations the inside record carries.
- The twin changes where your rows go; it does not change which rules
  you are under. Whether an approval or a privacy rule is satisfied is
  for the people who set it to decide, with the account of which real
  facts each file carries.

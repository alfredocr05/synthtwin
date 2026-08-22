# synthtwin

> **Status: early (Phase 4).** synthtwin is **not on PyPI**. What
> exists today is the whole workflow -- the profiler, which reads a CSV
> table on your computer and describes it; the generator, which builds
> the synthetic twin from that description and nothing else; and the
> validator, which measures a written file against the description and
> writes the quality report -- plus the security baseline the whole
> project rests on. Every capability on this page is tagged **[built]**
> or **[planned]** so there is no ambiguity about which is which.
>
> **The one thing to know before you use a twin:** it is faithful one
> column at a time. It carries no cross-column structure at all -- see
> "What the twin does not carry" below, which is the section to read
> before any other.

> **This repository goes public at Phase 3's visibility flip** - the
> owner decision recorded in the Phase 3 plan, executed the moment that
> plan landed on the default branch. The open-source commitment is
> unchanged: there is no private core, every line of the product lives
> here, and nothing here depends on anything a contributor cannot see.
> The governance controls that required a public repository - branch
> and tag rulesets among them - are applied at the flip, and their
> evidence lands in `SECURITY.md`'s activation record; no control is
> claimed before its evidence exists.

synthtwin creates a **synthetic twin** of a tabular dataset: a table
with the same shape as yours, and with each column behaving like the
same column of yours, worked out from a description of your table
rather than from its rows - built entirely on your machine, with no
network access of any kind. What that does and does not promise about
your rows is set out in "The twin's rows, stated exactly" below, and
what it does and does not promise about two columns together is set out
in "What the twin does not carry". Both are worth reading before you
rely on a twin.

## What synthtwin does today [built]

Given one table of real data, three commands produce five files, of
four kinds:

1. **A synthetic twin** - a table of the same shape whose columns each
   behave like the matching column of the original, every cell of it
   worked out from the description rather than taken from your file.
2. **A schema file** - a plain description of every column: its type, its
   range or its categories, and how the twin version of it was built.
   You get it twice, once for a program to read and once in words.
3. **A generation report** - written beside every twin, saying which of
   the description's facts the twin holds exactly, which it holds only
   approximately (with the value the twin actually reached printed
   beside the value the description publishes), and which it does not
   hold at all.
4. **A plain-language quality report** - written by `synthtwin
   validate`, which measures a CSV file against the description and
   says which of its obligations the file meets, which it misses, and
   which nothing written in a CSV could evidence either way. A passing
   report means exactly one thing: no checkable obligation was missed.
   It is not a verdict that the twin is fit for an analysis, and it
   cannot tell a synthetic file from a real one.

## What synthtwin does not do yet [planned]

5. **A relationships file** - the dependencies between columns, so that
   a twin could preserve them. **Nothing of this exists today.** The
   description carries a reserved block for it whose every slot is
   empty, and synthtwin refuses a description that fills one. Until it
   is built, the twin carries no cross-column structure at all. Nothing
   the quality report checks is a cross-column fact, because the
   description publishes none.

## Who it is for

Researchers who work with records that must never go anywhere near AI
tooling, cloud services, or any network - and who are not programmers.
The tool is being designed to run from a single command, and every error
message is required to tell a non-programmer what happened and what to do
next.

## What works today

Three commands, run one after the other. Each one ends by printing the
next.

```
synthtwin profile my-table.csv
synthtwin generate my-table-profile.json
synthtwin validate my-table-profile.json --twin my-table-twin.csv
```

The first reads `my-table.csv` on your computer and writes two files
beside it:

- `my-table-profile.json` - the description the twin will be built from;
- `my-table-profile.txt` - the same description in plain language, which
  is also printed on the screen.

The profiler reads what each column holds -- whole numbers, measured
numbers, dates, a set of categories, two-value columns, free text --
says in words why it read it that way, reports what is missing and how
the missing values were written, and tells you exactly which of your
real values ended up in the profile and which did not.

There is one reading it never makes for you: record numbers. A column of
ID codes and a column of measurements can look identical, and getting
that wrong either publishes identifiers or destroys a distribution the
twin exists to reproduce. So no rule anywhere in synthtwin can reach
that reading from the values in a column -- it comes only from you,
through `--identifier`, and it is described below with the rest of the
options.

**Read that last part before you move the profile anywhere.** The
profile is computed from your real data. It contains no rows of your
table, and it never contains a value from a column you named with
`--identifier`, a line of free text, or a label shared by fewer than
eleven rows -- but it does contain the smallest and largest values of
your numeric and date columns, the points in between that describe their
shape, and, for each label it names, the exact spellings your file used
for that label wherever eleven rows or more wrote it that way. Eleven is
the default and it is the only number in this paragraph you can change:
`--smallest-group` moves it, the whole workflow runs on whatever you set,
and setting it lower publishes smaller groups. What that costs is written
out under the options below. It is
real-derived material, and your institution's rules for such material
apply to it. The same is true of every other file a full run produces:
the profile, the plain-language summary beside it, the twin, the twin's
report and the quality report all carry facts computed from your real
data, so those rules apply to all five, not to the profile alone. The
summary is on that list for the reason that makes it easy to forget --
it is the readable one, so it is the one that gets pasted into an email,
and it repeats the real labels the profile publishes.

The second reads that description -- and nothing else, not your table
again -- and writes two more files beside it:

- `my-table-twin.csv` - the synthetic twin;
- `my-table-twin-report.txt` - what the twin carries, what it only
  approximates and what it does not carry at all, in plain language.
  It is also printed on the screen. Keep it with the twin: it is the
  only place that says which of those three each fact is.

The twin has the same columns in the same order, the same number of
rows, and the same amount of missing data as your table, and each of
its columns behaves like the matching column of yours. Read "What the
twin does not carry" below before you draw anything from two of its
columns at once.

The third reads the description and one CSV file -- by default the twin
beside it, or whatever `--twin` names -- and writes one more file:

- `my-table-twin-quality.txt` - the quality report, which lists every
  obligation the description sets, the outcome of each, and every
  obligation no CSV can evidence either way, with the reason. It is
  also printed on the screen. Its name comes from the file it measured
  and its first lines say which file that was, so checking a second
  candidate writes a second report rather than overwriting the first.

The exit code carries the same answer for a script: `0` when nothing was
missed, `3` when something was, `1` when the check could not run at all,
and `2` when the command line could not be used. A tool reading exit
codes can therefore tell a file that failed its check from a file that
was never evaluated, without parsing prose.

### The options

Six for `profile`, for the things the rules cannot settle on their own:

```
synthtwin profile my-table.csv --out-dir reports
synthtwin profile my-table.csv --identifier participant_number
synthtwin profile my-table.csv --smallest-group 20
synthtwin profile my-table.csv --keep-value -999
synthtwin profile my-table.csv --missing-value NA
synthtwin profile my-table.csv --first-row data
```

`--out-dir` writes the two files into a folder you name instead of into
the folder your table is in. The folder has to exist already.

`--identifier` names a column whose values are record numbers or codes
rather than measurements, so that none of them are published anywhere in
that column's description. It takes a column name -- any column, whatever
that column holds -- and it is the only way a column is ever read that
way. Repeat it to name more than one column. A name that is not in your
table stops the run before anything is written.

**`--smallest-group`, and what lowering it costs.** It changes the
eleven-row rule above, in either direction, and any whole number of 1 or
more is accepted end to end: `profile`, `generate` and `validate` all run
on the file it produces. Raising it publishes less. **Lowering it below
eleven publishes small groups and their counts**, and that is worth
reading slowly, because the count is the disclosure rather than a route
to one. At a smallest group size of two, the profile names values that
two rows shared and says that two rows shared them; at one, it names a
value one row held and says that one row held it. If one row of your
table is one person, somebody who already knows one true thing about
someone in it -- that they are in it at all -- can find the small group
that person must be in and read off everything else the profile says
about that group. Eleven is the number that keeps a published group too
big for that.

The counts do not stop at the profile: the twin is built to hold them
exactly, and the summary, the twin's report and the quality report quote
them back, so all five files of a run carry them. synthtwin does not
refuse the option -- it is your table and your institution's rules -- but
a run at a lowered number prints an unmissable warning before either file
exists, and each of the four readable files says on its own face that it
was made that way, so that a colleague handed one of them alone can tell.

`--keep-value` names a value your table means as real data even though
synthtwin would otherwise read it as "no value" -- a region genuinely
coded `NA`, or `-999` as a real reading. `--missing-value` is the
opposite: a value synthtwin would keep that your table means as "no
value". A value that reads as a number is matched as a number, so `-999`
also covers `-999.00`; anything else is matched as text, ignoring
surrounding spaces and capitals. The profile records how many values you
named each way and the rule that matched them. Where the value you named
is one of synthtwin's own twenty-three published words for "no value" --
the eighteen spellings such as `NA`, `null` and the spreadsheet error
literals like `#N/A`, the three stand-in numbers `-9999`, `-999` and
`9999`, and the two placeholder days `1900-01-01` and `9999-12-31` -- it also records which of those words it
was, because a check of your own table against its own description has
to read those cells the way the description read them. **A word of your
own is written nowhere in the settings**, no count, column or row goes
with the ones that are recorded, and `SECURITY.md` states the delta and
its bound. **That is a rule about the settings, and not about the rest
of the description.** A word you name with `--missing-value` IS written
into the description: the column that counted those cells names the
spelling exactly as your table wrote it, wherever at least
`--smallest-group` rows hold it and that column publishes any values at
all. So do not name a diagnosis, a code or an identifier here without
deciding first that the description may carry it - a `profile` run that
writes one of your words says so on the screen before either file
exists, and the plain-language summary lists every word of yours the
description names. And a value you keep is ordinary data from then on,
so it can appear wherever its column publishes values, for instance as
that column's smallest number.

**`--first-row`, and the assumption it takes back.** When a file settles
the question, synthtwin follows the file. When nothing in the file
settles it, synthtwin reads the first row as the column names, because
that is how a table is normally written -- and taking that reading is not
the same as proving it, so it is written down rather than assumed
silently. The profile records that the names were taken by convention,
and the summary says so in plain words near the top, ahead of everything
the assumption would change. The cost, stated instead of hidden: if your
file has no column names, its first record is described as column names
and is left out of every count. `--first-row data` takes that back --
synthtwin then names the columns `column_1`, `column_2`, and so on, and
keeps every record. `--first-row names` settles it the other way. When
the file itself shows that the first row is a record, synthtwin stops and
asks rather than choosing for you.

Three for `generate`:

```
synthtwin generate my-table-profile.json --out-dir reports
synthtwin generate my-table-profile.json --seed 7
synthtwin generate my-table-profile.json --replace
```

`--out-dir` works as it does above. `--seed` is a whole number from 0 to
18446744073709551615 that decides which twin you get: the same
description, seed and version of synthtwin always give the same twin,
byte for byte, and a different seed gives a different twin that follows
the description just as closely. `--replace` lets a re-run write over
the twin and the report an earlier run left at those names; without it a
run that finds either name taken stops and changes nothing, because
synthtwin has no way of telling an earlier twin of its own from a file
of yours that happens to be there.

Three for `validate`:

```
synthtwin validate my-table-profile.json --twin my-table-twin.csv
synthtwin validate my-table-profile.json --out-dir reports
synthtwin validate my-table-profile.json --replace
```

`--twin` names the CSV file to measure; left out, synthtwin measures the
twin beside the description. It measures whatever file you name: it has
no way of telling a twin of its own from any other CSV, and the report
says so rather than implying otherwise. `--out-dir` works as it does
above, and decides only where the quality report goes -- it says nothing
about where an earlier `generate` run put its twin, which is why the
line the generator prints when it finishes always spells out `--twin`.
`--replace` lets a re-run write over a quality report an earlier run
left at that name, on the same reasoning as above.

## What the twin does not carry

This is the section to read before you trust a number computed from a
twin, and it is not a list of bugs -- it is what this version of
synthtwin models.

**No cross-column structure, of any kind.** Every column of the twin is
built on its own, from the facts the description publishes about that
column alone. Nothing that links two columns of your table is in the
twin: not a taller person weighing more, not a later date costing more,
not a code that only ever appears beside one region, not a column that
is another column times twelve, not two columns that are empty in the
same rows, and not one event date always falling before another.
Analysis code you develop on the twin **runs**, which is what the twin
is for; a number that code computes from two columns of the twin means
nothing about your table.

**Rows are treated as independent, and the grain is undescribed.** The
description never says what one row of your table is. If your table
holds several rows per person, per visit or per site, the twin does not
know that, so anything that groups rows -- an average per person, a
repeated-measures model, a count of visits each -- behaves differently
on the twin than it will on your table. The twin is faithful one row at
a time, and a twin of a repeated-measures table misdescribes the
subject-level truth even where every column of it is right on its own.

Cross-column structure arrives in a later phase (Phase 5, in
`docs/plans/`). Every twin's own report states both limits, on every
run, whether or not anything else went wrong.

## What exists today

- **[built]** `synthtwin profile` - the reading and column analysis
  described above.
- **[built]** `synthtwin generate` - the twin and the report described
  above, built from the description and a seed and from nothing else.
  The generator never opens your table; it is not given a path to one.
- **[built]** `synthtwin validate` - the quality report described
  above, measured by describing the file again with the profiler's own
  producer and comparing. It never reaches the generator, so its
  verdicts are a second opinion rather than the planner marking its own
  work, and it consumes no randomness at all.
- **[built]** The generation report, which names every published fact
  the twin missed, every fact it only approximates with the bound it was
  held to, and the two limits under "What the twin does not carry"
  above. It passes no verdict of its own and says so, and it ends by
  teaching the `validate` command line that produces one.
- **[built]** The `synthtwin` command's version and status output.
- **[built]** The offline guarantee's layered checks: a best-effort
  import-allowlist scanner for the source tree, a socket guard in the
  test suite, and a packaged build that runs with no network available
  at all. `SECURITY.md` states exactly what the scanner does and does
  not prove.
- **[built]** The decontamination system: a scanner, a hashed manifest,
  and a signed attestation that together keep private-environment
  vocabulary out of this repository (see `SECURITY.md`).
- **[built]** The data-provenance guard: no data-format file is tracked
  anywhere in the repository except a test fixture listed in the fixture
  manifest, and every such fixture must be rebuilt from its committed
  generating script and byte-compared in CI.
- **[built]** Continuous integration with a single aggregate gate, and
  the written plans and their review record in `docs/plans/`.
- **[planned]** Relationships between columns. The description
  describes each column on its own, and the twin therefore carries no
  cross-column structure at all; how columns move together arrives in a
  later phase (Phase 5).
- **[planned]** PyPI publication - with signed, reproducible, attested
  releases. Phase 3 named it that phase's earliest-possible deliverable
  and Phase 3 closed on 2026-08-19 without it, so no phase carries it
  now: it is release engineering, waiting on its own checklist in
  `docs/plans/phase-3-product.md` and on the owner's go decision.

## The security architecture, in plain language

**Offline by construction [built].** synthtwin's own code contains
nothing that opens a network connection, launches another program, calls
native code, or loads code dynamically. It accepts only local file paths,
and it is fully functional air-gapped. The claim is about the code this
project ships and the work that code starts: it is verified by source
audit plus layered automatic checks, and it is explicitly *not* an
operating-system sandbox. Those automatic checks - the import-allowlist
scan in particular - are best-effort layers rather than a proof that
every call in the program lands on an exactly known target. `SECURITY.md`
states their scope plainly and names the residual risks that stay open,
among them code that a caller hands to synthtwin: that code runs in the
caller's own process under the caller's own authority, and no check here
governs it. If your institution requires enforcement rather than
assurance, run synthtwin inside your own network-isolated environment; it
will work there unchanged.

**Profile and generator are separate [built].** The architecture keeps
the profiler and the generator apart: the profiler runs where the real
data lives and writes a profile file; the generator needs only that
profile. The real data never has to move. The separation is held by the
import graph rather than by anybody's care -- one module opens a CSV
table, and a `generate` run never reaches it at any instant, from the
moment the command starts. `validate` does reach it, and must: measuring
a file means describing that file with the profiler's own producer. What
`validate` never reaches is the generator, so its verdicts cannot
inherit the planner's own defects and synthtwin's own random number
generator is out of its reach. That is not the same as saying no random
source is in the process, and it would be dishonest to write it that
way: `validate` reads a file, reading a file means pandas, and pandas
imports numpy, which loads `numpy.random`. What is enforced is that no
module of synthtwin on that path imports a random source and that the
run draws from none -- a trap over every source in the process, with the
whole command run at it. The boundary this architecture keeps is that
GENERATION reads a description and nothing else -- not that only one
command opens a file.

**Dependencies are governed [built].** synthtwin has exactly two direct
runtime dependencies. pandas is justified in writing in
`docs/plans/phase-1-profiler.md` and reduced by the import scanner to
exactly one function of it, `read_csv`; numpy is justified in
`docs/plans/phase-2-generator.md` and reduced to
`numpy.random.default_rng` plus the single drawing call on the random
stream it returns -- membership in an allowed library grants nothing on
its own. numpy is used only by the generator's one random stream: the
profiler, which is the half that reads your table, imports it nowhere.
(It was declared directly in Phase 1 too, until review round 1 showed
that its reductions made published statistics depend on the order of the
rows; the profiler computes those statistics itself now, and what
returned in Phase 2 is the random stream alone.) The policy
distinguishes the *direct* dependency (declared with an honest lower
bound that a CI job installs and tests) from the *complete closure*
(every package, including build tooling and everything a dependency
brings in with it, locked by hash and consumed frozen in CI and in the
supported institutional install path). One consequence is stated plainly
in `SECURITY.md`: the CSV reader synthtwin calls is itself capable of
fetching a URL, and what keeps it from doing so is synthtwin's own path
check, which refuses anything that is not a plain local path before any
file is opened and is re-run immediately before the reader is handed
that path.

## The twin's rows, stated exactly

The generator is given the profile and a seed, and nothing else. It is
never handed a path to your table, it does not open one, and it samples
or copies no row of it. Every value in the twin is worked out from the
description.

That is a statement about where the twin's values come from. It is not a
promise that no row of the twin can equal a row of yours, and an earlier
version of this page said otherwise, which was wrong. The profile
publishes exact counts, and meeting them exactly can force a twin row to
match a real one. The plainest case: a table of eleven rows with one
column, whose single label is shared by all eleven rows, publishes that
label with the count eleven -- so the twin writes that label in all
eleven of its rows, and each of those rows is the row you have. Nothing
was copied. The arithmetic left no other answer, and any tool that
reproduces published counts exactly lands in the same place.

So synthtwin offers **no formal privacy guarantee** and claims no
differential-privacy property. All five files a full run produces --
the profile, the plain-language summary beside it, the twin, the twin's
report and the quality report -- carry facts computed from your real
data, and your institution's rules for real-derived material apply to
all five, not to the profile alone. What synthtwin does give you is
an architecture in which the real table never has to move, plus a
written account, in `SECURITY.md` and in the run's own report, of
exactly which real facts each file carries.

## Honest limits

These are design limits, stated up front so nobody discovers them late:

| Limit | What it means for you |
| --- | --- |
| One flat table at a time | synthtwin models a single table. Multi-table databases and cross-file joins are out of scope. |
| One column at a time | The twin reproduces what the description publishes about each column on its own. It carries **no cross-column structure** at all -- no correlation, no formula between two columns, no shared pattern of empty cells, no ordering between two event dates. Cross-column structure arrives in a later phase (Phase 5). See "What the twin does not carry" above. |
| One row at a time | Rows are treated as independent and the grain is undescribed: the description never says what one row of your table is, so a table with several rows per subject yields a twin that misdescribes the subject-level picture. |
| Only what the description publishes is reproduced | A pattern the profiler does not publish is not in the twin, whether or not the profiler could in principle have seen it. |
| No free text | Narrative or note columns are described by their length and word counts only; their values are never published, and the twin will not invent sentences. |
| CSV only, for now | The profiler reads comma-separated files saved as UTF-8 (or, as a fallback, Western European text). Spreadsheets, databases and columnar formats come later. |
| The table has to fit in memory | A table is read into memory whole; reading very large files in pieces is planned but not built. A file of a few hundred megabytes is comfortable on an ordinary machine; several gigabytes is not, and you are told so in words rather than by a crash. |
| The file is read twice | Once to check its shape and once to read its values, by two different readers whose results must agree. That costs a second pass over the file and buys the guarantee that a malformed row is refused rather than quietly turned into missing values. |
| Small tables degrade | With few rows, the statistics the profiler measures are noisy, and the twin's fidelity drops accordingly. Two files say where: the generation report names each approximate fact with the value the twin reached beside the published one, and `synthtwin validate` writes the quality report, which is where a small table shows as missed obligations rather than as a feeling. |
| The quality report protects the report, not the file | `synthtwin validate` may say about the file it checked only what `synthtwin profile` run on that file would publish, and prints WITHHELD where it may not say a number. That protects the **report**, which travels to people who may not hold the file. It is not a defence against somebody who has the checked file and runs the check again and again with descriptions they wrote themselves, watching which lines change: that person can narrow a number one report withholds, and synthtwin does not try to stop them, because they can read the file. The control that matters is who may hold the file. See `SECURITY.md`. |

## Determinism [built]

The guarantee, exactly as scoped: the same profile, the same seed, the
same synthtwin version, and the same locked dependency set produce
byte-identical output **on the same platform**. Cross-platform equality
is verified empirically by golden-hash tests on every cell of the CI
matrix and is reported as a tested result - it is never promised beyond
the tested matrix. One documented consequence of the single-stream design:
changing the schema shifts the random streams that follow it at the same
seed, so byte-stability is promised only across identical inputs.

## Installing

synthtwin is **not on PyPI** yet. To use all three commands from a
clone:

```
git clone https://github.com/alfredocr05/synthtwin
cd synthtwin
pip install -e .
synthtwin profile my-table.csv
synthtwin generate my-table-profile.json
synthtwin validate my-table-profile.json
```

On a machine that must install everything by hash, and that may have no
network at all, the procedure has two parts. The first needs a machine
that does have network access; the second does not.

**On a connected machine**, collect the exact files, verifying every
hash as they arrive, and copy the folder across:

```
pip download --require-hashes --only-binary=:all: \
    --dest wheelhouse -r requirements-install.lock
```

Put the synthtwin wheel (`synthtwin-<version>-py3-none-any.whl`, from a
release) into that same folder.

**On the locked-down machine**, install from the folder and nothing
else:

```
pip install --no-index --find-links wheelhouse \
    --require-hashes -r requirements-install.lock
pip install --no-index --no-deps wheelhouse/synthtwin-<version>-py3-none-any.whl
```

Both pip commands are barred from the network by `--no-index`, and the
first checks every hash. `--no-deps` on the second is what keeps the
verified versions in place.

Do **not** substitute `pip install .` from a source folder for the
second command. It runs a build backend that pip fetches from the
network, `requirements-install.lock` does not pin that backend, and on a
machine with no network it simply fails. CI runs exactly the two pip
commands above on every build, against the wheel produced inside a
container with no network.

From Phase 3's visibility flip onward the repository is public and
these commands work for anyone, with no account and no authentication;
the hash-verified procedure itself is the same either way.

Running `synthtwin` with no arguments prints the version and what the
tool can do today.

## License

MIT License. Copyright (c) 2026 Alfredo Camargo Rodrigues.

This work is released on the project owner's authority as non-commercial
research tooling (owner decision recorded 2026-08-07 in the Phase 0
plan). Contributions are accepted under the same license: inbound =
outbound MIT, no CLA. See `LICENSE` for the full text.

## Learn more

- `SECURITY.md` - the threat model, the offline guarantee and the exact
  scope of its automatic checks, every named residual risk, how an
  auditor verifies each layer, and which governance controls are active
  now, with the activation record of the controls applied at the
  visibility flip.
- `CONTRIBUTING.md` - the plan-first process and the standing rules every
  change must follow.
- `docs/plans/` - the written plans and their adversarial review record.

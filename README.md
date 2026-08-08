# synthtwin

> **Status: early (Phase 1).** synthtwin is **not on PyPI**. What
> exists today is the profiler -- it reads a CSV table on your computer
> and describes it -- plus the security baseline the whole project rests
> on. Generating the twin itself is the next phase. Every capability on
> this page is tagged **[built]** or **[planned]** so there is no
> ambiguity about which is which.

> **This repository is private for now.** It is private by owner
> decision and becomes public when the owner judges the application
> readier for release. The open-source commitment is unchanged: there is
> no private core, every line of the product lives here, and nothing
> here depends on anything a contributor cannot see. The governance
> controls that require a public repository - branch and tag rulesets
> among them - are listed in `SECURITY.md` as deferred until that
> moment, never as active.

synthtwin will create a **synthetic twin** of a tabular dataset: a table
with the same shape and the same statistical behavior as yours, but
containing no real records - built entirely on your machine, with no
network access of any kind.

## What synthtwin will do [planned]

Given one table of real data, synthtwin will produce four outputs:

1. **A synthetic twin** - a table of the same shape whose columns look
   and behave statistically like the original, with zero real rows in it.
2. **A schema file** - a plain description of every column: its type, its
   range or its categories, and how the twin version of it was built.
3. **A relationships file** - the dependencies between columns that the
   profiler detected or that you declared, so the twin preserves them.
4. **A plain-language quality report** - how faithful the twin is,
   written so you can judge it without a statistics background.

## Who it is for

Researchers who work with records that must never go anywhere near AI
tooling, cloud services, or any network - and who are not programmers.
The tool is being designed to run from a single command, and every error
message is required to tell a non-programmer what happened and what to do
next.

## What works today

```
synthtwin profile my-table.csv
```

That reads `my-table.csv` on your computer and writes two files beside
it:

- `my-table-profile.json` - the description the twin will be built from;
- `my-table-profile.txt` - the same description in plain language, which
  is also printed on the screen.

The profiler decides what each column holds -- record numbers, whole
numbers, measured numbers, dates, a set of categories, two-value
columns, free text -- says in words why it decided that, reports what is
missing and how the missing values were written, and tells you exactly
which of your real values ended up in the profile and which did not.

**Read that last part before you move the profile anywhere.** The
profile is computed from your real data. It contains no rows of your
table, and it never contains a record number, a line of free text, or a
label shared by fewer than eleven rows -- but it does contain the
smallest and largest values of your numeric and date columns, and the
points in between that describe their shape. It is real-derived
material, and your institution's rules for such material apply to it.

Two options exist for the situations the rules cannot decide alone:

```
synthtwin profile my-table.csv --out-dir reports
synthtwin profile my-table.csv --identifier participant_number
synthtwin profile my-table.csv --smallest-group 20
```

`--identifier` tells synthtwin that a column of numbers is a record
number rather than a measurement, so that none of its values are
published. `--smallest-group` changes the eleven-row rule above.

## What exists today

- **[built]** `synthtwin profile` - the reading and column analysis
  described above.
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
- **[planned]** Generation, validation, and the quality report - these
  arrive in later phases, each behind its own written plan and
  adversarial review.
- **[planned]** Relationships between columns. The profile describes
  each column on its own; how columns move together is decided in the
  next phase.
- **[planned]** PyPI publication - earliest at the end of Phase 3, with
  signed, reproducible, attested releases.

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

**Profile and generator are separate [planned].** The future architecture
keeps the profiler and the generator apart: the profiler runs where the
real data lives and writes a profile file; the generator needs only that
profile. The real data never has to move.

**Dependencies are governed [built].** synthtwin has exactly two
runtime dependencies, pandas and numpy, each justified in writing in
`docs/plans/phase-1-profiler.md` and each reduced by the import scanner
to the handful of functions this code actually calls -- membership in an
allowed library grants nothing on its own. The policy distinguishes the
*direct* dependencies (declared with honest lower bounds that a CI job
installs and tests) from the *complete closure* (every package,
including build tooling and transitives, locked by hash and consumed
frozen in CI and in the supported institutional install path). One
consequence is stated plainly in `SECURITY.md`: the CSV reader
synthtwin calls is itself capable of fetching a URL, and what keeps it
from doing so is synthtwin's path check, which refuses anything that is
not a plain local path before any file is opened.

## Honest limits

These are design limits, stated up front so nobody discovers them late:

| Limit | What it means for you |
| --- | --- |
| One flat table at a time | synthtwin models a single table. Multi-table databases and cross-file joins are out of scope. |
| Only detected or declared structure is reproduced | The twin preserves what the profiler can see or what you explicitly declare. A pattern the profiler cannot detect, and that you did not declare, will not be in the twin. |
| No free text | Narrative or note columns are described by their length and word counts only; their values are never published, and the twin will not invent sentences. |
| CSV only, for now | The profiler reads comma-separated files saved as UTF-8 (or, as a fallback, Western European text). Spreadsheets, databases and columnar formats come later. |
| The table has to fit in memory | A table is read into memory whole; reading very large files in pieces is planned but not built. A file of a few hundred megabytes is comfortable on an ordinary machine; several gigabytes is not, and you are told so in words rather than by a crash. |
| The file is read twice | Once to check its shape and once to read its values, by two different readers whose results must agree. That costs a second pass over the file and buys the guarantee that a malformed row is refused rather than quietly turned into missing values. |
| Small tables degrade | With few rows, the statistics the profiler measures are noisy, and the twin's fidelity drops accordingly. The quality report will say so plainly. |

## Determinism [planned]

The guarantee that will hold once generation exists, exactly as scoped:
the same profile, the same seed, the same synthtwin version, and the
same locked dependency set produce byte-identical output **on the same
platform**. Cross-platform equality
is verified empirically by golden-hash tests on every cell of the CI
matrix and is reported as a tested result - it is never promised beyond
the tested matrix. One documented consequence of the single-stream design:
changing the schema shifts the random streams that follow it at the same
seed, so byte-stability is promised only across identical inputs.

## Installing

synthtwin is **not on PyPI** yet. To use the profiler from a clone:

```
git clone https://github.com/alfredocr05/synthtwin
cd synthtwin
pip install -e .
synthtwin profile my-table.csv
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

Both commands are barred from the network by `--no-index`, and the
first checks every hash. `--no-deps` on the second is what keeps the
verified versions in place.

Do **not** substitute `pip install .` from a source folder for the
second command. It runs a build backend that pip fetches from the
network, `requirements-install.lock` does not pin that backend, and on a
machine with no network it simply fails. CI runs exactly the two
commands above on every build, against the wheel produced inside a
container with no network.

While the repository is private, that clone works only from an account
the owner has granted access, and Git asks you to authenticate first; an
unauthenticated clone fails. Once the repository becomes public, the same
commands work for anyone, with no account and no authentication.

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
  now versus deferred until the repository becomes public.
- `CONTRIBUTING.md` - the plan-first process and the standing rules every
  change must follow.
- `docs/plans/` - the written plans and their adversarial review record.

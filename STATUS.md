# synthtwin — where the project stands

*Written 2026-08-18, at commit `95136aa` on branch `phase-3-open-defect-repairs`.*
*Version `0.1.0.dev0` — not yet released.*

This is a plain-language status document. It says what synthtwin is, what
each phase built, what you can do with it today, how to try it yourself,
and what is honestly still missing.

---

## What synthtwin is for

You hold a table you cannot paste into an AI assistant, and often cannot
move off a compliant machine at all. synthtwin reads that table and
writes a **description** of it. From the description alone — never from
your rows — it builds a **synthetic twin**: same columns, same types,
each column behaving like yours.

You develop your analysis against the twin, freely and quickly. Then you
run the finished code on the real table, inside your safe environment.

---

## The phases

| phase | what it builds | state |
|---|---|---|
| **0** | the repository, licence, CI, and the security baseline | **done** |
| **1** | the profiler — read a table, write the description | **done** |
| **2** | the generator — build the twin from the description alone | **done** |
| **3** | the whole product through one command, plus the checker | **essentially done**, see below |
| **4** | every column type, rare categories, missing-data patterns | not started |
| **5** | relationships between columns | **not started — this is the one that matters most for statistics** |
| **6** | a hardened offline build for institutional machines | not started |

### Phase 3, in more detail

Phase 3 made the three commands work together and added the **quality
report** — the checker that measures a written file against a
description and says which of its published obligations the file meets.

It also went through **thirteen rounds of adversarial review**. Those
rounds were not cosmetic. Early ones found that the checker would tell
you a file was fine when it held almost none of its published facts.
Later ones found a message telling you the description does not keep
words that it does keep. Every one of those is fixed.

Late in the phase the profile format moved from version 4 to **version 5**,
so the description now records *how each cell was read* — which word you
called "missing", which you rescued as real data. That was done now
because Phase 5 needs it anyway, and changing the format costs nothing
while nobody outside has the tool.

---

## What you have today

Three commands, and a full run leaves **five files**.

```
synthtwin profile   my-table.csv           # writes the description
synthtwin generate  my-table-profile.json  # writes the twin
synthtwin validate  my-table-profile.json  # writes the quality report
```

| file | what it is |
|---|---|
| `my-table-profile.json` | the description — the only thing the generator reads |
| `my-table-profile.txt` | the same description in plain language |
| `my-table-twin.csv` | **the synthetic twin — the file you develop against** |
| `my-table-twin-report.txt` | what the twin holds exactly, approximately, and not at all |
| `my-table-twin-quality.txt` | the checker's report on a file you name |

**All five carry facts computed from your real data.** Your institution's
rules for real-derived material apply to all five, not to the twin alone.

---

## How to try it right now

From the repository folder:

```bash
cd synthtwin
.venv/bin/synthtwin profile  path/to/your-table.csv
.venv/bin/synthtwin generate your-table-profile.json
.venv/bin/synthtwin validate your-table-profile.json
```

Then open `your-table-twin.csv` and develop against it. Read
`your-table-twin-report.txt` — it tells you, per column, what the twin
reproduces exactly and what it only approximates.

Useful options:

- `--seed 7` — same description and seed always give the same twin
- `--missing-value -999` — "in my table, `-999` means missing"
- `--keep-value -999` — "no, `-999` is real data here"
- `--identifier record_id` — "this column is a code, not a measurement"
- `--smallest-group 11` — the privacy floor; groups smaller than this are
  not named in the description

**If you name a word with `--missing-value` or `--keep-value`, that word
is written into the description.** The tool tells you so before it writes
anything. Type a diagnosis or an identifier there and it travels with the
file.

---

## What the twin is good for, and what it is not

**Reliable, column by column:**

- row count, how many values are missing, the fraction missing
- each column's distribution — mean, spread, percentiles
- which categories exist and roughly how often
- date ranges and spacing

So: summary tables, histograms, "describe each variable", and any code
whose correctness depends on shape and type rather than on relationships.

**Not reliable — and this is the wall:**

Anything using **two columns at once**. Correlation. Regression. Group
comparisons. Survival analysis. Any model with more than one predictor.

Each column is built independently, so the relationship between age and
blood pressure in the twin is noise. If your table holds several rows per
subject, the twin gets every column right and describes a subject who
does not exist.

**Your code will run. Numbers from a multi-column analysis mean nothing
about your real data.** That is Phase 5, and it has not started.

**Also true:** the twin is not a formal privacy mechanism and claims no
differential-privacy property. Numbers computed on it are not scientific
results.

---

## Known, open, and written down

- **Two-decimal numbers.** Checking your *own* table against its own
  description reports one missed check, because your file writes `1.20`
  where the description recorded `1.2`. Owner decision: leave as is. Your
  twin is unaffected.
- **Free-text columns** cannot record which word you called "missing", so
  the checker says it cannot check those columns rather than guessing.
- **A guard against future edits** — the test that stops someone later
  writing a false sentence about what the description keeps — can still be
  walked past in two specific wordings. Nothing shipped is wrong today.
- Several smaller items are recorded in `docs/plans/phase-3-product.md`
  and its residual register.

---

## Before this can be released

1. **Push the branch and let CI run.** Seventeen commits have never been
   through CI. The Windows fix in particular was only ever *emulated*
   locally — real Windows is the one thing that cannot be checked here.
2. Merge, once CI is green.
3. The release steps in `docs/plans/phase-3-product.md` (P3-D8.2–8.4).

---

## Where the detail lives

- `CLAUDE.md` — the charter: the principles and the honest limits
- `docs/plans/phase-3-product.md` — the Phase 3 plan and every amendment
- `docs/spec/profile-contract-v5.md` — what a description may contain
- `CHANGELOG.md` — what changed, in order

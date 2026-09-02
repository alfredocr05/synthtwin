# The drivers behind the numbers in the plans

Every measured number the phase plan or the state page states about
this package's behaviour is produced by a script in this directory. It
is here for one reason, and an adversarial round is what put it here:

> The empirical totals are not reproducible from the committed source
> alone. [...] their measurement drivers and outputs are absent.
> The committed cases support the direction of the repairs but not
> those sample sizes or frequencies.
>
> — review item P4-G6-R2, 2026-08-30

A number stated in a governing document with no way to re-derive it is
a number the reader has to take on trust, which is the one thing this
repository's own charter refuses everywhere else: the oracle exists so
that the generator is not its own witness, the vacuity guards exist so
that a green check is not its own witness, and the provenance manifest
exists so that a fixture is not its own witness. A measured claim owes
the same.

## What these are NOT

They are not tests. Nothing here runs in the suite, nothing here is a
pass or a fail, and a number that comes out different from the one the
plan states is not by itself a defect -- the corpora are random and
several of the rates are properties of a draw. What they buy is that
the number can be RE-DERIVED and the corpus INSPECTED, so a reader can
see which family was measured and what the driver could not have
produced.

That last point is the one that matters most. Every rate here is a rate
FOR A FAMILY. `r_p4_56_width_collision.py` measures 13 in 80 on columns
with a pinned decimal width and 0 in 80 on ordinary ones, and it
carries the second family precisely so the first number cannot be read
as a rate for columns in general.

## Running one

    .venv/bin/python tools/measurements/<name>.py

Each prints how many cases it BUILT and how many it REFUSED, before any
rate. A driver that silently swallows its refusals reports a confident
number about nothing, which happened twice while these were being
written.

## What each one answers

| script | the claim it re-derives |
| --- | --- |
| `p4_g6_r1_merge_key.py` | the scaled branch of G5.2a moves no merge the plain divisor could make |
| `r_p4_55_case_pair.py` | how often the raw-against-folded ceiling cost a column its spelling count |
| `r_p4_56_width_collision.py` | how often two strata round onto one spelling, by family |
| `r_p4_57_deviation_drift.py` | what the exact deviation costs a column that already worked |
| `r_p4_61_window_agreement.py` | whether the twin's report and the quality report ever disagree about a verdict |
| `r_p4_56_grid_separation.py` | what separating two strata on the grid costs the twin |
| `p4_g6_r5_exact_moments.py` | what the exact moments cost a column that already worked |
| `r_p4_30_l6_widths.py` | how often a twin writes a cell at a whole-number width the source never used (landing L6) |
| `r_p4_40_l7_joined.py` | how many different numbers a joined column's positions hold against their published counts (landing L7) |
| `r_p4_136_l8_empty_bins.py` | how many twin cells land in a stretch the real column left empty, before and after landing L8, and the two families where the twin still cannot get out |

**This table went stale before landing L8 and is repaired there**: it
listed four of the ten scripts, so six measured claims in the phase
plan had a driver on disk that no index reached. A row here is owed by
every script in this directory.

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
| `a_p4_52_l7_parity.py` | how many of a position's own turns the above-count proposal aims on, and what each variant of that gate costs a twin in above-counts and agreements (amendment A-P4-52) |
| `k_p3_03_spread.py` | why a numeric twin's spread is too wide (ledger K-P3-03): the straight ladder's own spread, the same with the real outer segments put back, the bend the published spread fixes, the twin's, and the `moments.std` window, by rows, by shape and on lab-like columns the verdict does not flag |
| `kpi_run.py` | the KPI ledger (`tests/kpi/ledger.json`): every KPI's value now against its rule, grouped by phase and stage with the headlines first; exits 1 on any drop and 2 on a ledger that fails its own integrity check. It is the one script here that passes or fails, because the ledger states a rule for each number |
| `kpi_decontamination.py` | K-P0-05: the decontamination scan reads at least 400 files and finds nothing, so a scan of no file cannot pass |
| `kpi_windows_20_seeds.py` | K-P2-07: approximated facts outside their windows, and MISSED obligations, on the every-role twin at seeds 0 to 19 |
| `kpi_numeric_20k.py` | K-P3-03, K-P3-12, K-S1-01: twenty numeric columns at 5,000 and 20,000 rows -- MISSED obligations, and the seconds and growth ratios of generate and validate, each a median of three at both sizes |
| `kpi_scale.py` | K-S1-05 and K-S1-06: describing 200,000 rows of labels, and 100,000 x 20 numbers end to end, each against a quarter of the rows as a machine-free growth ratio, medians of three (2,000,000 x 50 on request, the landing-4 gate) |
| `kpi_joined_battery.py` | K-P4-06 and K-P4-08: the joined-number battery's pair agreements and rows-above counts, and the runs whose count of different numbers is not met, read off `r_p4_40_l7_joined.py` |
| `kpi_window_flips.py` | K-2B-05: verdicts the two reports disagree on, read off `r_p4_61_window_agreement.py` |
| `kpi_datetime_speed.py` | K-2B-14: the units `_nearest_held_unit` steps through on two second-precision columns, an operation count, with the seconds beside it |
| `kpi_census_repair_speed.py` | K-S2-06: the census-of-marks repair at 80,000 and 320,000 cells, as a growth ratio |
| `kpi_large_workbooks.py` | K-2B-34: three writers' study workbooks at three sizes, the real book AND its twin validated |
| `kpi_known_misses.py` | K-2B-47: the four carried fidelity misses (percent widths, a two-width dose, a temperature stratum over the mode count, a heavy tail) held still until stage 3, as MISSED verdicts summed over each shape's runs |
| `kpi_oracle_similarity.py` | K-2B-42: oracle functions whose syntax sits at 0.60 or above against their closest shipped function, named |

**This table went stale before landing L8 and is repaired there**: it
listed four of the ten scripts, so six measured claims in the phase
plan had a driver on disk that no index reached. A row here is owed by
every script in this directory.

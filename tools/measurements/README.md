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
| `kpi_decontamination.py` | K-P0-05: the decontamination scan COMPLETES a read of at least 400 files, over at least 100,000 text surfaces, and finds nothing, so neither a scan of no file nor a scan that reads one token out of each can pass -- both counts are instrumented at the surface reader the scan pulls its text through, never taken from the listing, and both are bounds the ledger states |
| `kpi_windows_20_seeds.py` | K-P2-07: approximated facts outside their windows, and MISSED obligations, on the every-role twin at seeds 0 to 19 |
| `kpi_numeric_20k.py` | K-P3-03, K-P3-12, K-S1-01: twenty numeric columns at 5,000 and 20,000 rows -- MISSED obligations, the twin's spread against the published one (widest and narrowest, per cent), and the seconds and growth ratios of generate and validate, each a median of three at both sizes |
| `kpi_scale.py` | K-S1-05 and K-S1-06: describing 200,000 rows of labels, and 100,000 x 20 numbers end to end, each against a quarter of the rows as a machine-free growth ratio, medians of three (2,000,000 x 50 on request, the landing-4 gate) |
| `kpi_joined_battery.py` | K-P4-06 and K-P4-08: the joined-number battery's pair agreements and rows-above counts, and the runs whose count of different numbers is not met, read off `r_p4_40_l7_joined.py` |
| `kpi_window_flips.py` | K-2B-05: verdicts the two reports disagree on, read off `r_p4_61_window_agreement.py` |
| `kpi_datetime_speed.py` | K-2B-14: the questions the two date-time searches ask of the held-unit table on two second-precision columns, an operation count, with the seconds and the distance walked beside it |
| `kpi_census_repair_speed.py` | K-S2-06: the census-of-marks repair at 80,000 and 320,000 cells, as a growth ratio |
| `kpi_large_workbooks.py` | K-2B-34: three writers' study workbooks at three sizes, the real book AND its twin validated |
| `kpi_known_misses.py` | K-2B-47: the four carried fidelity misses (percent widths, a two-width dose, a temperature stratum over the mode count, a heavy tail) and the carried residue of 2026-09-19 (two date-width defects, the `(-%)` layout, the G5.2 band split, the unchecked read floor), held still as MISSED verdicts summed over each shape's runs; K-2B-49: the orchestrator's calls of 2026-09-18 (the point-free grid trade, subsecond digits as nought, a record number's class counts); K-2B-50 and K-2B-51: the two fidelity failures the owner ruled on 2026-09-21 were to be fixed, GREEN since (a pooled population of numbers beside labels losing its scale, and a timestamp column whose absorbed mark leaves a description no file satisfies) |
| `kpi_suite_time.py` | K-P0-10: what the suite itself costs -- one ordinary single-process `pytest -q` from the repository root, timed by the wall clock, with the collected count beside it so seconds can never be bought by running fewer cases |
| `kpi_oracle_similarity.py` | K-2B-42: oracle functions whose syntax sits at 0.60 or above against their closest shipped function, named |
| `kpi_stage3_tail_leak.py` | K-S3-11: published values, summary lines and report lines equal to one of the eleven outermost values of a date or clock column; the tails the published facts settle by back-solve; how much room the tightest of them leaves; and how many of the real table's own tail distances the construction window does not reach, so that the real table passes that obligation only by exact equality -- over the tail design's own battery |
| `kpi_cost_rule.py` | K-S3-17, K-S3-18, K-S3-20, K-S3-21, K-S3-22 and K-S3-50: what the published tail pairs give and cost since plan P4-D375 -- the tail values the exact skew and kurtosis rebuild beside both pairs, the sides a reader names a cell from and the cells, every obligation the twins miss and leave withheld at a floor of 36, the values a reader names by subtraction beside a published pair, the moments no published pair keeps, and how far twins write past the real range |
| `kpi_weekday_census.py` | K-S3-31: over the weekday gate's battery of six date columns at 1,000 and 10,000 rows and seeds 0 to 4, the censuses published, the obligations MISSED on every twin and real table, and the scoped weekend-share and weekday clauses that fail |
| `kpi_clock.py` | K-S3-48: the fourteen clock columns of `tests/clock_census_shapes.py` in one table at 1,000 rows (seeds 0 to 4, floors 11 and 36) and 10,000 rows (seed 0) -- how many are read as clock times, the largest hour-of-day error at the floor of eleven, heaps off their count, twin cells no clock reader takes, and twins or tables MISSED |
| `kpi_counted_dates.py` | K-S3-60: numbers that are dates (landing R4) -- the fourteen shapes of `tests/counted_dates.py` and their writers over events from 1985 and births from 1920, undeclared at 1,000 rows: which question Q3 asks with the writer's system among its answers, clean and under six stray-value scenarios, and the new questions it raises on the chance battery; declared with `--date-count` at 1,000 rows and seeds 0 to 2 and at 10,000 rows and seed 0: columns not read as dates, twin cells off the published `count_form`, source cells not written back as themselves, twins and sources MISSED, and the largest weekday TVD at 10,000 rows |
| `kpi_day_of_month_census.py` | K-S3-44: at 40,000 rows, seven date columns publishing their day-of-month census, the joint day plan's seconds as a per cent of the whole generation's, the censuses published and the obligations MISSED on the twin (landing 3b.3, plan P4-D368) |
| `kpi_heavy_dates.py` | K-S3-46 and K-S3-47: the gate's battery at 40,000 rows and the 26-week two-weekday session family, the listed dates held, the obligations MISSED and the twins whose count gives way; the weekday groups a list narrows and the twin's unlisted dates that stand out at 1,000, 10,000 and 40,000 rows (landing 3b.6, plan P4-D369) |
| `kpi_reader.py` | K-S3-52: the twenty written clocks of landing T1 (`tests/clock_spellings.py`) at 1,000 rows and seeds 0 to 2 and at 10,000 rows and seed 0 -- how many read with no cell left over, twin cells the source's own format refuses, twins MISSED, and twins rewritten on the 24-hour clock that validation does not miss |
| `kpi_full_precision.py` | K-S3-54: computed numbers written in full -- hours between two times, ratios, fractions of a day -- at 1,000 rows and seeds 0 to 19 through `synthtwin profile`, counting every run that ends without both files; then 10,000 and 100,000 rows, counting the pool walk's big-number steps and its placements onto a state wider than half the rows, with the seconds beside them; K-S3-55's slow half: the seconds an unread 10,000-row column takes to describe |
| `kpi_hour_census.py` | K-S3-38: over the hour gate's battery -- eleven columns of moments at 1,000 rows (three spans withheld), four at 10,000 rows, a lab panel of 2,000 results and 3,021 OR starts -- at floor 11 and seeds 0 to 4, the censuses published, the obligations MISSED on every twin and real table, the hour statistics clauses that fail, and the twins whose weekdays or count of different values move against the same seed with the hour pass withdrawn; and a timed node, 100,000 daytime moments of a year at floor 11, seed 0, the hour pass's seconds against a budget judged on the quiet reference machine, and the obligations it misses |
| `kpi_clock_census.py` | K-S3-42: over the minute gate's shapes -- sixteen columns of moments at 1,000 rows and fourteen at 10,000 -- at floor 11 and seeds 0 to 4, the minute and second fields published, the obligations MISSED on every twin and real table, the minute and second statistics clauses and the INDEPENDENCE clause that fail, and the twins at 1,000 rows whose hour or weekday census groups move against the same seed with G7.3h withdrawn; and the design skeptic's node, 40,000 cells written `HH:MM:00` at floor 11, seed 0, G7.3h's seconds against a budget judged on the quiet reference machine, and the obligations it misses |
| `kpi_date_questions.py` | K-S3-56: the columns of `tests/date_question_shapes.py` at their own sizes, floor 11, seed 0 -- the day-or-month and code columns the questions file asks about and the ones whose answer repairs the twin (every cell outside the codes parsed by the person's own format, the codes written back as often, nothing missed, nothing asked again), and the thirty-seven clean spellings of the reach audit and five shapes neither question may reach, how many of them are asked |
| `kpi_reader_memory.py` | K-S4-02: the most memory the reader holds, in kilobytes a row, and its CPU seconds, reading a made-up 50-column mixed table of 200,000 rows (record numbers, codes, labels, numbers in their spellings, dates, stamps, clocks and free text) in a process of its own; and the survey's traced peak at 10,000 rows with lines ended by carriage returns alone and by mixed endings, over its peak with line feeds |
| `kpi_layout.py` | K-S3-58: the thirty-nine date spellings of landing R2a (`tests/layout_spellings.py`) -- the thirty-two of the date half no named member read and the seven its design skeptic added -- at 1,000 rows and seeds 0 to 2 and at 10,000 rows and seed 0 -- how many read under a layout with no cell left over, twin cells off the source's own spelling or refused by its own format, twins MISSED, and twins rewritten in ISO that validation does not miss |
| `kpi_unanswered_identifiers.py` | K-S3-64: ten long tables of `tests/unanswered_identifier_shapes.py` -- 44 patients, one Safe Harbor identifier repeated on each patient's rows -- at 600 and 20,000 rows, profiled with nothing declared or answered and generated at seed 0: real values and fragments in the description, its summary and the questions file, and real values and fragments in the twin, over the six shapes held and the four stated ones |

**This table went stale before landing L8 and is repaired there**: it
listed four of the ten scripts, so six measured claims in the phase
plan had a driver on disk that no index reached. A row here is owed by
every script in this directory.

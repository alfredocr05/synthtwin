"""How long each test file takes, for packing the CI shards.

MEASURED, NOT GUESSED. Every number below is one file's own share of a
run of the whole suite with `--durations=0`: the setup, call and
teardown seconds of its cases, added up. That is the cost a shard
inherits when it takes the file, its module-scoped fixtures included.
Interpreter start and collection are left out: a shard is charged for
those once, however many files it holds.

TO RE-MEASURE, run the five shards through the suite runner with
`PYTEST_ADDOPTS=--durations=0`, as the table below was, and add up, per
file, the seconds each shard's log prints against each case.

WHAT A STALE NUMBER COSTS, AND WHAT IT CANNOT COST. These seconds
decide only the PACKING: which shard a file lands in. A number that has
drifted makes one shard longer than another and never makes a file run
twice or not at all -- `tools/ci/shards.py --prove` is what holds that,
against pytest's own collection. So this table is a convenience that
may be re-measured whenever somebody wants the shards to come out
closer in length, and it is never a thing a test result depends on.

RE-MEASURED WHOLE 2026-11-05, by lane SPD2 (plan P4-D461, the suite's
time part 2). The table below replaced every row of the one before it,
and the dated paragraphs that described those rows, from the re-measure
of 2026-10-01 to the row added on 2026-11-04, are cut: the version
history keeps them (the lane's skeptic 1, item 5). Each row
is one file's setup, call and teardown seconds summed from ONE run of
the lane's head `e45eaecc` through the suite runner with
`PYTEST_ADDOPTS=--durations=0` -- the five shards at once, each one
pytest process, under Python 3.11 -- on a machine other work was loading
(one-minute load average 44 at the run's start and 140 at its end, free
memory 48 and 50 per cent; the shards took 6,457, 4,341, 8,267, 5,972
and 9,114 s). Every collected file has a row, the 49 that had none
included (four of them had taken 934 to 2,327 s each on the base and
weighed 2.0 s here), and a file whose every case fell under the five
milliseconds pytest prints weighs 0.0. The packing is still
`tools/ci/shards.py`'s longest-first: on these seconds it splits the
head's work into five shards within half a second of one another, where
the old rows had projected 3,837 s a shard and the base's run took
4,871 to 10,314 s. One row is
that run's less what the lane moved after it: `tests/test_stage4_describe_memory.py`
weighs its 1,506.31 s less the 371.41 s its six 40,000-row legs took
in the same run, which now run in K-HZ-21's driver. And one is that
run's plus what the lane's repairs kept after it (LANE SPD2 RULINGS 4
and 5): `tests/test_zoo_identifiers.py` weighed its 150.91 s plus the
132.75 s its six kept 20,000-row legs took in base run 1 (`2af926ce`,
the same way: 80.99 s for the five repair 1 kept, 51.76 s for the `ge`
leg repair 2 kept), until it was weighed whole again on 2026-11-08
(below).

THREE ROWS ADDED 2026-11-04, at batch 4o's merge of lanes MR, PL and SH3
(plans P4-D452, P4-D453 and P4-D454): each lane's new file weighed the
default. `tests/test_safe_harbor_ages_and_address_parts.py`, 244.50 s
(lane SH3's gate, 110 cases), `tests/test_levels_few_people_hold.py`,
69.39 s (lane PL's gate, 92 cases), and `tests/test_rules_method_page.py`,
34.39 s (lane MR's rules page, 31 cases), each timed alone by one
`pytest -q --durations=0` process on the merged tree under Python 3.11, on a
machine other work was loading (lane SH3 measured about 130 s on a quiet
machine and 179 to 250 s under load, lane PL's verify 65.4 s).

THREE ROWS ADDED 2026-11-04, at batch 4o's merge of lanes CZ-D, CZ-H and
MPp (plans P4-D447, P4-D446 and P4-D455): each lane's new file weighed the
default. `tests/test_types_and_flags.py`, 85.21 s (lane CZ-D's gate, 68
cases; the orchestrator's AT CZ-D'S MERGE), `tests/test_zoo_dates_in_disguise.py`,
86.52 s (lane CZ-H's gate, 173 cases with the merge's three of its limit
(h)), and `tests/test_moment_rule_b.py`, 60.27 s (lane MPp's gate, 54
cases), each timed alone by one `pytest -q` process on the merged tree
under Python 3.11, on a machine other work was loading.

THREE ROWS ADDED 2026-11-05, at batch 4p's merge of lanes BT2 and CHa2
(plans P4-D448 and P4-D451): each lane's new file weighed the default.
`tests/test_stage6_clock_mirror.py`, 64.23 s (lane BT2's clock mirror in
the quality report, 9 cases), `tests/test_stage6_reader_step.py`, 16.68 s
(lane BT2's reader step, 16 cases), and `tests/test_chain_table_layer.py`,
13.5 s (lane CHa2's gate, 37 cases), each timed alone by one `pytest -q`
process on the merged tree under Python 3.11, on a machine other work was
loading.

THREE ROWS ADDED 2026-11-06, at batch 4p's merge of lanes GRa and MPg
(plans P4-D449 and P4-D456): each lane's new file weighed the default.
`tests/test_stage6_patient_profile.py`, 264.1 s (lane GRa's gate, 83
cases, and the merge's case of the patient table's pooled top category),
`tests/test_moment_polish.py`, 254.43 s (lane MPg's gate, 25 cases), and
`tests/test_moment_polish_sort.py`, 55.07 s (lane MPg's sort, 2 cases),
each timed alone by one `pytest -q` process on the merged tree under
Python 3.11, on a machine other work was loading. RE-TIMED at batch 4p's
fix round: `tests/test_stage6_patient_profile.py`, 354.3 s (its two gate
cases of Codex's item 1 and of its sibling sweep added), timed the same
way on the fix round's tree.

ONE ROW ADDED 2026-11-05, on lane ARR-a's branch (plan P4-D466): the
audited array helper's gate `tests/test_arrays.py`, 12.92 s (49 cases),
timed alone by one `pytest -q --durations=0` process under Python 3.11 on
a machine other work was loading; timed again 2026-11-06 at the lane's
repair 1, 14.74 s (106 cases), the same way, and at its repair 2,
17.46 s (147 cases). Its other new file,
`tests/test_computer.py`, has no row: every case fell under the five
milliseconds pytest prints. The lane's 229 new cases in
`tests/test_offline_scan.py` keep that file's row (most scan a few lines
of source; the lane's report measures the file beside the base).

TWO ROWS ADDED 2026-11-07, at batch 4q's merge of lane ST (plan P4-D458):
`tests/test_stage6_selftest_reports.py`, 158.03 s (the lane's gate, 95
cases, and the merge's two cases of its private report beside lane GRa's
patient layer), and `tests/test_analyst_battery.py`, 159.24 s (31 cases,
the lane's K-BC-11 cases among them), each timed alone by one `pytest -q`
process on the merged tree under Python 3.11, on a machine other work
was loading.

SIX ROWS ADDED 2026-11-07, at batch 4q's merge of lane ID-ROOM2 (plan
P4-D457; the orchestrator's LANE ID-ROOM2 RULINGS 5 (3)): the lane's six
gate files, `tests/test_held_dates_off_the_real.py`, 22.7 s (80 cases),
`tests/test_held_dates_off_the_real_zoo.py`, 40.57 s (4),
`tests/test_held_dates_off_the_real_writers.py`, 266.28 s (2),
`tests/test_held_dates_off_the_real_shapes.py`, 219.91 s (8),
`tests/test_held_dates_off_the_real_widths.py`, 192.55 s (5), and
`tests/test_held_dates_off_the_real_typed.py`, 208.08 s (4), each timed
alone by one `pytest -q` process on the merged tree under Python 3.11, on
a machine other work was loading.

TWO ROWS ADDED 2026-11-07, at batch 4q's merge of lane CZ-A (plan P4-D445;
the lane's report names them the integrator's): its gate,
`tests/test_zoo_safe_harbor_forms.py`, 192.29 s (286 cases), and
`tests/test_zoo_safe_harbor_forms_walk.py`, 42.6 s (21 cases), each timed
alone by one `pytest -q` process on the merged tree under Python 3.11, on
a machine other work was loading.

ONE ROW ADDED 2026-11-07, at batch 4q's merge of lane CHs (plan P4-D462):
`tests/test_stage6_chain_describe_scale.py`, 126.48 s (the lane's gate, 17
cases), timed alone by one `pytest -q` process on the merged tree under
Python 3.11, on a machine other work was loading.

AT BATCH 4q'S MERGE OF LANE SPD2 (2026-11-07; LANE SPD2 RULINGS 2 (3), point 6): this table is the lane's, measured whole on its head, and the rows the lanes merged after its base `2af926ce` added are added beside it, as the 9 dated paragraphs above name them: 23 files the lane's tree did not have, and `tests/test_analyst_battery.py` at lane ST's 159.24 s, timed alone on the merged tree with lane ST's added case, where the lane's run read the base's file at 102.73 s.

NINE ROWS ADDED 2026-11-07, at batch 4q's merge of lane SPD2: the test
files of the merged line that had no row, each timed alone by one
`pytest -q --durations=0` process on the merged tree under Python 3.11,
its setup, call and teardown seconds summed as the table's other rows
are, on a machine other work was loading lightly (one-minute load average 6 to 8):
lane TT's `tests/test_terminal_twin.py`, 71.33 s, and
`tests/test_terminal_twin_held.py`, 136.04 s; lane RO's
`tests/test_stage6_order_rules.py`, 59.29 s; batch 4o's fix rounds'
`tests/test_ages_named_on_held_columns.py`, 23.96 s,
`tests/test_pool_start_keeps_off_keys.py`, 11.29 s,
`tests/test_short_letters_asked.py`, 7.69 s, and
`tests/test_yes_no_letters_one_pair.py`, 4.66 s; batch 4p's fix round's
`tests/test_module_names_once.py`, 1.72 s; and lane ARR-a's
`tests/test_computer.py`, 0.0 s (every case under the five milliseconds
pytest prints). Every collected file now has a row.

FOUR ROWS ADDED AND SIX WEIGHED AGAIN 2026-11-08, at batch 4q's records
round (its two fix rounds' test files; the orchestrator's LANE I4q
RULINGS 17 (4)(d) and 22): each timed alone by one
`pytest -q --durations=0` process over the second fix round's head
`c22837e6` under Python 3.11, its setup, call and teardown seconds
summed as the table's other rows are, on a machine other work was
loading lightly (one-minute load average 4.3 to 7.1): the rounds' new
files, `tests/test_chain_grades_held_dates.py`, 7.0 s (16 cases),
`tests/test_held_dates_field_readings.py`, 73.77 s (37 cases),
`tests/test_held_dates_reader_readings.py`, 86.52 s (34 cases) and
`tests/test_record_numbers_beside_text.py`, 86.55 s (7 cases); and the
six they grew by a case, each weighed whole again,
`tests/test_held_dates_off_the_real.py`, 16.17 s (81 cases; 22.7 s
before), `tests/test_held_dates_off_the_real_typed.py`, 83.54 s (5
cases; 208.08 s before), `tests/test_p4a60_answers_handed_back.py`,
3.74 s (18 cases; 3.12 s before), `tests/test_stage6_band_totals.py`,
70.36 s (109 cases; 192.97 s before), `tests/test_zoo_identifiers.py`,
86.77 s (76 cases; 283.66 s before) and `tests/test_identifier_room.py`,
99.59 s (220 cases; 394.45 s before).

ONE ROW ADDED 2026-11-09, at batch 4q's records round for its third fix
round (the round's new gate file; the orchestrator's LANE I4q RULINGS
22): `tests/test_held_dates_spellings.py`, 91.74 s (29 cases), timed
alone by one `pytest -q --durations=0` process over the records head,
whose src is the third round's head `36023624`'s, under Python 3.11,
its setup, call and teardown seconds summed as the table's other rows
are, on a machine other work was loading lightly (one-minute load
average 4.5).

ONE ROW ADDED AND ONE WEIGHED AGAIN 2026-11-09, at batch 4q's records
round for its fourth fix round (the orchestrator's LANE I4q RULINGS 23
and 24): the round's new gate file `tests/test_held_dates_export_spellings.py`,
93.35 s (57 cases), and `tests/test_held_dates_spellings.py`, which its
enlarged generator of spellings grew, 99.14 s (29 cases; 91.74 s
before), each timed alone by one `pytest -q --durations=0` process over
the records head, whose src is the fourth round's head `15c89b3b`'s,
under Python 3.11, its setup, call and teardown seconds summed as the
table's other rows are, on a machine other work was loading lightly
(one-minute load average 5.5 and 5.3).

ONE ROW ADDED 2026-11-05, on lane SR2a's branch (plan P4-D463), timed again
2026-11-07 at its repair 2: its gate, `tests/test_stage4_describe_peak.py`,
56.86 s, its 76 cases timed alone by one `pytest -q` process on the repair's
code under Python 3.11, on a quiet machine (a one-minute load of about 8;
96.53 s for its first 67 cases at a load of about 120, at repair 1, and
87.72 s for its first 52).

ONE ROW ADDED 2026-11-07, at lane PRT-a (plan P4-D468): the lane's gate
file weighed the default. `tests/test_readers_once_a_spelling.py`, 8.99 s
(39 cases since the lane's repair 2: each reader's answers, the walks
read against their readers asked one by one, the shared memo's cap over
spellings written twice in a row, the whole describe of a 600-row table
with every memo on and off, each check on its mutant), timed alone by
one `pytest -q --durations=0` process on the lane's head under Python
3.11, on a machine other work was loading (6.71 CPU seconds, at a load
of 63; 14.11 s and 6.85 CPU seconds for repair 1's 35 cases, 9.86 s and
5.75 for the build's 32).

ONE ROW ADDED 2026-11-06, at lane BT3a (plan P4-D467): the lane's gate
file weighed the default. `tests/test_stage6_chain_recount.py`, 80.71 s
(10 cases: a clinic table and a long table of 400 visits a patient, each
through the switched command at the owner's table floor), timed alone by
one `pytest -q` process on the lane's head under Python 3.11, on a
machine other work was loading (72.9 CPU seconds). RE-TIMED 2026-11-08
at the lane's repair 1: 95.52 s (16 cases: the long table's three
patient-fixed columns, three year tables of 24,000 rows and a table of
20,000 rows read with its own absent spellings added), the same way on
its final code head at a load near 5 (95.5 CPU seconds; 275.54 s at a
load near 50 the day before). RE-TIMED 2026-11-08 at its repair 2, with
a second file: `tests/test_stage6_chain_recount.py` 148.65 s (17 cases:
two patient-fixed ages and the same long table with the switch off
added, two year tables moved out) and
`tests/test_stage6_chain_recount_settled.py` 66.06 s (5 cases: two year
tables, the table of own absent spellings, a settled comma on 24,000
rows and an age answered in days on 20,000), each timed alone the same
way on the final code head at a load near 9 (149.8 and 66.4 CPU
seconds).

ONE ROW WEIGHED AGAIN 2026-11-09, at batch 4r's merge of lane BT3a (plan
P4-D467): `tests/test_stage6_chain_recount_settled.py`, 49.61 s (6 cases:
the merge's case of the rule steps reading the cells of the reading that
stands, beside the lane's five; 66.06 s before), timed alone by one
`pytest -q --durations=0` process on the merged tree under Python 3.11,
its setup, call and teardown seconds summed as the table's other rows
are, on a machine other work was loading lightly (one-minute load
average about 7). The merged line's other files keep their rows, the
three other new files of lanes SR2a, PRT-a and BT3a at the seconds their
lanes measured above: every file the merged line collects has a row
(399 files, 18,170 cases). Lane TR (plan P4-D473) adds
`tests/test_zoo_time_readers.py`, 216.24 s (45 cases, 12 of them its repair 1's, 10 its repair 2's
and 8 its follow-up's), timed alone by one `pytest -q --durations=50` process on its follow-up's code
head under Python 3.11 beside other lanes' runs, the machine heavily loaded (one-minute load average
about 140; eight settings under 0.005 s unshown; 64.9 CPU s, where repair 2's 37 cases took 53.5 CPU s
in a run of their own at a load average about 40).

ONE ROW ADDED 2026-11-10, by lane LM1 (plan P4-D475), re-timed at its
repair 2: `tests/test_lm1_numbers_as_written.py`, 71.32 s (its gate,
42 cases, two of them at 20,000 rows: 22.03 and 8.63 s;
169.24 s at repair 1 with 63 cases and three such, before the exponent
form's cases left), timed alone by one `pytest -q --durations=0` process
on the repair's head under Python 3.11, its setup, call and teardown
seconds summed, on a machine other work was loading.

ONE ROW ADDED 2026-11-09, at lane DST (plan P4-D474): the lane's gate
file weighed the default. `tests/test_offsets_follow_the_date.py`,
134.34 s at the lane's repair 2 (54 cases: the rule families against a
calendar written from their own words on quarter hours sampled over four
decades -- each year from the family's first admitted one to 2030, the
25 quarter hours beside each change and 300 drawn over the year, not
every quarter hour as this comment first said -- the reading, the one
definition that admits a rule over every quarter-hour pair of offsets,
the product against the oracle on generated cases, the census step, the
dead hour and the read-back at five rungs of four fall-back days, every
bucket of four fall-back days drawn, the take-back, the count at the
rung, a twin's tail before and after its family's years, the zoo's two
tables at 600 rows, the hour-rung tables of three families, one table
of 20,000 rows through the command with the floor
on, the mutants' cases, and the combined zone-word case, skipped until
lane TR's reading stands), timed alone by one `pytest -q --durations=0`
process on the repair's code head under Python 3.11, its setup, call
and teardown seconds summed, at a one-minute load of 80 to 110 (an
earlier run of the same cases: 138.51 s; repair 1's 39 cases: 62.65 s
near 100; the build's 30: 50.41 s near 80).

ONE ROW ADDED 2026-11-10, at lane CODES-2's repair 2 (Codex's item 8 on
the lane's build, the orchestrator's LANE CODES-2 RULINGS 6 (5)): the
lane's gate file `tests/test_zoo_rare_names.py`, 170.37 s (92 cases, its
case at the owner's floor 143.05 s of them), timed alone by one
`pytest -q --durations=0` process over the repair's tree (its src that of
the repair's head) under Python 3.11, its setup, call and teardown seconds
summed as the table's other rows are, on a machine other work was loading
heavily (one-minute load average 72 to 85; 172.2 s wall, 88.1 s of CPU).
Before this row the file weighed the default though the plan records it at
about 145 s wall, so its shard was packed about two minutes light.

THE SAME ROW RE-TIMED 2026-11-11, at lane CODES-2's follow-up (the
orchestrator's LANE CODES-2 RULINGS 8 and 9): 366.91 s (102 cases, ten
added; its first case at the owner's floor 227.56 s and the follow-up's
case at the floor 81.58 s of them), timed alone by one
`pytest -q --durations=0` process over the follow-up's tree under
Python 3.11, setup, call and teardown summed as before, on a machine
other work was loading heavily (one-minute load average 58 to 88;
370.96 s wall, 121.6 s of CPU against repair 2's 88.1 s). RULINGS 9
counts the suite-time rule in CPU seconds on this machine: the file
adds 33.5 CPU s to repair 2's, well inside its three minutes.

THE SAME ROW RE-TIMED AGAIN 2026-11-11, at lane CODES-2's follow-up
micro-step (the orchestrator's LANE CODES-2 RULINGS 10): 410.25 s (106
cases, four added; its first case at the owner's floor 202.17 s, the
follow-up's 75.71 s and the micro-step's 67.88 s of them, the glued
grammar enumerated 13.62 s), timed alone by one `pytest -q
--durations=0` process over the micro-step's third commit (its src and
tests those of the micro-step's head) under Python 3.11, setup, call and
teardown summed as before, on a machine other work was loading heavily
(one-minute load average 57 to 88; 414.01 s wall, 151.1 s of CPU, user
and system, against the follow-up's 121.6 s). In CPU seconds, as
RULINGS 9 counts the suite-time rule on this machine, the file adds 29.5
to the follow-up's and stays inside its three minutes.

ONE ROW ADDED 2026-11-11, at batch 4s's merge of lane CZ-A2 (the
orchestrator's LANE CZ-A2 RULINGS 11 (3)): the lane's gate file
`tests/test_labelled_record_numbers.py`, 144.9 s (61 cases), the lane's
own measurement on its final code `a08efa47`: one `pytest` process over
the file, 144.9 CPU seconds, user and system (313.8 s of wall at the
machine's load), where the other rows sum the setup, call and teardown
seconds `--durations=0` prints. The merge's join adds one case, the
agreement of the file's plain reading with the product's one definition
of a space and a dash over every code point (4.5 s in the merge
step's run).

TWO ROWS ADDED 2026-11-11, at batch 4s's merge of lane HB2 (plan P4-D477):
the lane's two gate files, each timed by one `pytest` process over the
file on the merge step's code, CPU seconds, user and system, at the
machine's load: `tests/test_safe_harbor_age_words.py` 51.5 s (21 cases:
the lane's 17, the scoped verify 2's floor case beside a declared
person and the join's three) and `tests/test_safe_harbor_ends_and_bounds.py` 71.6 s (19
cases: the lane's 17 and the verify's two unit cases), where the other
rows sum the setup, call and teardown seconds `--durations=0` prints.

ONE ROW ADDED 2026-11-12, at batch 4s's merge of lane CZ-E (plan P4-D472):
the lane's gate file `tests/test_zoo_value_readers.py`, 137.1 s (254 cases: the
lane's 243 and the merge's join), one `pytest` process over the file on
the merge step's code, CPU seconds, user and system, at the machine's load
(268 s of wall), where the other rows sum the setup, call
and teardown seconds `--durations=0` prints; the lane measured 62.7 CPU s
for its 243 on its final code `591b48d0`.

ONE ROW ADDED 2026-11-09, on lane SV's branch (plan P4-D476): its gate,
`tests/test_stage4_validate_groups.py`, 96.35 s (40 cases since the
lane's repair 2, 2026-11-11: a generated sweep of the check's rewrites
and of the encoding words, fourteen written forms, seeded refused
files, grains, the chain's switch, one table of 20,000 rows, quoting by
class, a header line written in, a row order broken inside a grain and
a workbook, each read one column a group against one group, and twelve
machine-free cases of K-S4-23's driver), timed alone by one
`pytest -q --durations=0` process on the repair's code under Python
3.11, its setup, call and teardown seconds summed as the table's other
rows are, on a machine other work was loading (one-minute load 46 to
51; the 120.59 s recorded before were repair 1's 33 cases).

ONE ROW MOVED 2026-11-12, at batch 4s's merge of lane SV (plan P4-D476):
`tests/test_stage4_validate_groups.py`, 79.93 s (42 cases: the
lane's 40 and the join's two agreement cases of the line's top-coded and
time shapes, one of them over a table of 20,000 rows), one `pytest`
process over the file on the merge step's code, CPU seconds, user and
system, at the machine's load (164 s of wall), as the rows of
lanes HB2 and CZ-E were measured at their merges; the lane's 96.35 s
were its 40 cases' setup, call and teardown seconds summed.

TEN ROWS WEIGHED AGAIN 2026-11-12, at batch 4s's owed items (the merge
part's checks, on the merged head `4e64baa5`): every gate file the batch's
lanes added, each timed alone by one `pytest -q --durations=0` process
under Python 3.11 over that head, its setup, call and teardown seconds
summed as the table's other rows are, on a machine other work was loading
(one-minute load average about 60 to 110), the process's CPU seconds, user
and system, and its wall beside each:
`tests/test_labelled_record_numbers.py` 400.77 s (62 cases, 178.3 CPU s,
404 s of wall; the row was 144.9); `tests/test_lm1_numbers_as_written.py`
112.12 s (42 cases, 46.9 CPU s, 116 s of wall; the row was 71.32);
`tests/test_offsets_follow_the_date.py` 145.94 s (54 cases, 62.5 CPU s, 149
s of wall; the row was 134.34); `tests/test_safe_harbor_age_words.py`
141.05 s (21 cases, 54.1 CPU s, 145 s of wall; the row was 51.5);
`tests/test_safe_harbor_ends_and_bounds.py` 192.92 s (19 cases, 72.2 CPU s,
195 s of wall; the row was 71.6); `tests/test_stage4_validate_groups.py`
218.82 s (42 cases, 78.6 CPU s, 223 s of wall; the row was 79.93);
`tests/test_zoo_persons_names.py` 90.27 s (300 cases, 37.3 CPU s, 94 s of
wall; no row before); `tests/test_zoo_rare_names.py` 377.02 s (106
cases, 147.8 CPU s, 382 s of wall; the row was 410.25);
`tests/test_zoo_time_readers.py` 163.24 s (45 cases, 68.5 CPU s, 166 s of
wall; the row was 216.24); `tests/test_zoo_value_readers.py` 341.0 s (254
cases, 134.5 CPU s, 345 s of wall; the row was 137.1). The row of lane
CZ-F's gate file was missing, so the file weighed the default; the five
rows the merges of lanes CZ-A2, HB2, CZ-E and SV wrote in CPU seconds now
hold summed durations like the rest.

ONE ROW ADDED 2026-11-13, at batch 4s's seal: the fix round's gate file
`tests/test_merged_line_review_items.py`, 403.77 s (22 cases), its setup,
call and teardown seconds summed from the round's final run of it on the fix
head `85eb6754`, one `pytest -q --durations=0` process under Python 3.11 at
a one-minute load of about 80 to 100 (100.3 CPU s, 407 s of wall).

A FILE WITH NO ROW weighs `DEFAULT_SECONDS`. Only a file added since
the last measurement has none: it is placed like an ordinary small file
and runs in its shard from the commit that adds it. A file every case of
which fell under the five milliseconds pytest prints a duration for has
a row of 0.0, as said above.
"""

# The weight of a test file this table has no measurement for: a little
# over the median file, so a handful of new files cannot all land in one
# shard by looking free.
DEFAULT_SECONDS = 2.0

SECONDS = {
    "tests/test_ages_named_on_held_columns.py": 23.96,
    "tests/test_all_different_numbers_asked.py": 161.92,
    "tests/test_analyst_battery.py": 159.24,
    "tests/test_analyst_kit.py": 13.36,
    "tests/test_analyst_tables.py": 12.18,
    "tests/test_answers_across_rounds.py": 434.87,
    "tests/test_ap311_lowered_floor.py": 22.99,
    "tests/test_ap312_fold_repair.py": 269.94,
    "tests/test_ap313_stated_limit.py": 0.38,
    "tests/test_ap326_unrebuildable_reading_rule.py": 2.42,
    "tests/test_ap329_reading_rule_from_version_5.py": 3.05,
    "tests/test_arrays.py": 17.46,
    "tests/test_bundle.py": 57.73,
    "tests/test_carried_numbers.py": 14.2,
    "tests/test_census_reading_handed_over.py": 1.3,
    "tests/test_chain_grades_held_dates.py": 7.0,
    "tests/test_chain_method_page.py": 2.2,
    "tests/test_chain_oracle.py": 2.87,
    "tests/test_chain_profile.py": 45.82,
    "tests/test_chain_table_layer.py": 13.5,
    "tests/test_ci_demo_steps.py": 30.63,
    "tests/test_ci_shards.py": 0.07,
    "tests/test_claim_inventory.py": 80.12,
    "tests/test_cli.py": 0.04,
    "tests/test_cli_generate.py": 4.04,
    "tests/test_cli_profile.py": 14.31,
    "tests/test_cli_validate.py": 17.76,
    "tests/test_column_analysis.py": 1.51,
    "tests/test_column_analysis_extra.py": 0.19,
    "tests/test_commit_messages.py": 4.53,
    "tests/test_commonest_width_grid.py": 6.65,
    "tests/test_computer.py": 0.0,
    "tests/test_contract_loader.py": 38.72,
    "tests/test_contract_self_check.py": 8.75,
    "tests/test_date_spread.py": 73.14,
    "tests/test_dates_held_by_the_floor.py": 61.7,
    "tests/test_dates_pooled_in_people.py": 338.01,
    "tests/test_dates_written_forms_disclosed.py": 21.23,
    "tests/test_decontamination.py": 2549.59,
    "tests/test_dependencies.py": 13.21,
    "tests/test_description_line_endings.py": 53.75,
    "tests/test_extra_review_dates.py": 7.84,
    "tests/test_extra_round_disclosure.py": 35.61,
    "tests/test_extra_round_numbers.py": 9.98,
    "tests/test_failure_catalog.py": 3.32,
    "tests/test_file_dialect_round_trip.py": 92.56,
    "tests/test_files_review_2026_09_18.py": 9.04,
    "tests/test_files_review_repairs.py": 21.17,
    "tests/test_final_review_labels.py": 44.82,
    "tests/test_final_skeptic_repairs.py": 23.92,
    "tests/test_floor_is_a_minimum.py": 65.5,
    "tests/test_generation.py": 14.3,
    "tests/test_generation_reference.py": 188.32,
    "tests/test_guard_timing_sentinel.py": 0.02,
    "tests/test_health_zoo.py": 185.27,
    "tests/test_health_zoo_leaks.py": 68.47,
    "tests/test_health_zoo_shards.py": 27.87,
    "tests/test_held_dates_export_spellings.py": 93.35,
    "tests/test_held_dates_field_readings.py": 73.77,
    "tests/test_held_dates_off_the_real.py": 16.17,
    "tests/test_held_dates_off_the_real_shapes.py": 219.91,
    "tests/test_held_dates_off_the_real_typed.py": 83.54,
    "tests/test_held_dates_off_the_real_widths.py": 192.55,
    "tests/test_held_dates_off_the_real_writers.py": 266.28,
    "tests/test_held_dates_off_the_real_zoo.py": 40.57,
    "tests/test_held_dates_reader_readings.py": 86.52,
    "tests/test_held_dates_spellings.py": 99.14,
    "tests/test_held_unit_search.py": 48.04,
    "tests/test_identifier_room.py": 99.59,
    "tests/test_joined_battery_readings.py": 413.72,
    "tests/test_joined_pair_round_trip.py": 77.22,
    "tests/test_k_p3_03_outer_tail_spread.py": 64.99,
    "tests/test_kpi_ledger.py": 2473.74,
    "tests/test_kpi_ledger_integrity.py": 21.86,
    "tests/test_l0_method_page.py": 0.28,
    "tests/test_labelled_record_numbers.py": 400.77,
    "tests/test_landing_2b12_identifiers_codes_text.py": 18.4,
    "tests/test_landing_2b13_numbers_beside_labels.py": 10.22,
    "tests/test_landing_2b15_unanchored_numbers.py": 19.24,
    "tests/test_landing_2b16_number_readings.py": 58.19,
    "tests/test_landing_2b18_forms_and_spellings.py": 51.48,
    "tests/test_landing_2b18_identifier_layout.py": 116.36,
    "tests/test_landing_2b18_layout_disclosure.py": 117.09,
    "tests/test_landing_2b2_number_spellings.py": 169.14,
    "tests/test_landing_2b7_mixed_spellings.py": 18.17,
    "tests/test_landing_2b7_source_spellings.py": 37.44,
    "tests/test_landing_2b8_labels_text_missing.py": 64.74,
    "tests/test_lane_l1_codes_as_written.py": 714.35,
    "tests/test_lane_l2_spaced_meridiem.py": 99.06,
    "tests/test_lane_l3_stamp_forms.py": 188.23,
    "tests/test_levels_few_people_hold.py": 69.39,
    "tests/test_lm1_numbers_as_written.py": 112.12,
    "tests/test_lone_figure_nought.py": 0.28,
    "tests/test_lone_pools_every_reader.py": 7.46,
    "tests/test_merge_close_2026_09_18.py": 12.42,
    "tests/test_merged_line_review_items.py": 403.77,
    "tests/test_method_citations_resolve.py": 1.38,
    "tests/test_mixture_reader_bounds.py": 30.15,
    "tests/test_module_names_once.py": 1.72,
    "tests/test_moment_method_page.py": 0.82,
    "tests/test_moment_oracle.py": 21.54,
    "tests/test_moment_polish.py": 254.43,
    "tests/test_moment_polish_sort.py": 55.07,
    "tests/test_moment_rule_b.py": 60.27,
    "tests/test_moment_window_anchor.py": 8.62,
    "tests/test_no_quadratic_list_growth.py": 11.2,
    "tests/test_numba_vectors.py": 1.0,
    "tests/test_number_censuses_name_no_row.py": 28.6,
    "tests/test_numbers_beside_labels.py": 45.38,
    "tests/test_numeric_reference.py": 0.07,
    "tests/test_numeric_strata_round_trip.py": 287.89,
    "tests/test_offline_scan.py": 73.78,
    "tests/test_older_censuses_name_no_row.py": 25.38,
    "tests/test_oracle_proof_layer.py": 1.86,
    "tests/test_oracle_rule_witnesses.py": 153.55,
    "tests/test_p1r6f11_display_boundary.py": 0.94,
    "tests/test_p1r6f4_comprehension_scopes.py": 30.76,
    "tests/test_p1r6f6_first_row_decision.py": 1.71,
    "tests/test_p1r6f7_one_policy.py": 1.51,
    "tests/test_p1r6f8_identifier_evidence.py": 4.27,
    "tests/test_p1r6f9_declared_values.py": 2.53,
    "tests/test_p1r7f1_any_exception.py": 0.13,
    "tests/test_p1r7f1_transaction_disclosure.py": 0.16,
    "tests/test_p1r7f2_declaration_disclosure.py": 1.02,
    "tests/test_p1r7f2_disclosure_is_true.py": 1.98,
    "tests/test_p1r7f2_withholding_block.py": 1.08,
    "tests/test_p1r7f3_exact_declarations.py": 8.32,
    "tests/test_p1r8f1_guard_seam.py": 7.18,
    "tests/test_p1r8f1_working_name_claim.py": 2.67,
    "tests/test_p1r8f2_exact_sentinels.py": 3.32,
    "tests/test_p1r8f4_repetition_multiset.py": 0.25,
    "tests/test_p2c1f2_invention_domain.py": 0.54,
    "tests/test_p2c1f3_publication_guard.py": 9.42,
    "tests/test_p2c1f4_approximation_bounds.py": 4.73,
    "tests/test_p2c1f5_leading_zero_family.py": 110.67,
    "tests/test_p2c1f6_temporal_round_trip.py": 0.68,
    "tests/test_p2c1f8_specification_agreement.py": 0.59,
    "tests/test_p2c2f1_complete_allocation.py": 43.2,
    "tests/test_p2c2f2_style_placement.py": 0.23,
    "tests/test_p2c2f3_style_invention.py": 0.27,
    "tests/test_p2c2f4_numeric_cardinality_bounds.py": 0.26,
    "tests/test_p2c2f5_temporal_endpoints.py": 177.05,
    "tests/test_p2c2f6_fold_collisions.py": 0.43,
    "tests/test_p2c2f7_oracle_identifier_bands.py": 0.03,
    "tests/test_p2c2f8_invention_walk_bound.py": 0.06,
    "tests/test_p2c3f1_published_margins.py": 30.43,
    "tests/test_p2c4f1_disposition_registry.py": 42.51,
    "tests/test_p2c4f2_text_shape.py": 52.77,
    "tests/test_p2c4f3_style_capacity.py": 62.79,
    "tests/test_p2c5f2_identifier_classes.py": 894.21,
    "tests/test_p2c5f3_style_reach.py": 124.15,
    "tests/test_p2c5f4_generation_refusals.py": 3.22,
    "tests/test_p2d10_artifact_words.py": 0.06,
    "tests/test_p3_flip_migration.py": 0.94,
    "tests/test_p3v10f3_the_walk_stops_at_the_tables_keys.py": 0.8,
    "tests/test_p3v10f4_named_markers_are_holes.py": 1.91,
    "tests/test_p3v10f5_exact_equality_wins.py": 15.42,
    "tests/test_p3v11f2_no_refusal_quotes_your_spelling.py": 1.07,
    "tests/test_p3v12f2_a_miss_says_what_it_found.py": 15.92,
    "tests/test_p3v1f12_one_target_transaction.py": 4.35,
    "tests/test_p3v1f2_entry_table.py": 543.87,
    "tests/test_p3v2a1_presence_split.py": 1280.47,
    "tests/test_p3v3f1_description_equivalence.py": 29.33,
    "tests/test_p3v3f3_refused_files.py": 3.06,
    "tests/test_p3v3f4_ordinal_spaces.py": 0.75,
    "tests/test_p3v3f5_written_form.py": 3.34,
    "tests/test_p3v3f6_reader_agreement.py": 3.86,
    "tests/test_p3v4f10_windows_reach.py": 18.43,
    "tests/test_p3v4f1_kept_values.py": 344.33,
    "tests/test_p3v4f2_canonical_ceiling.py": 4.24,
    "tests/test_p3v4f3_refusal_equivalence.py": 1.2,
    "tests/test_p3v4f4_datetime_windows.py": 1.59,
    "tests/test_p3v5f1_floor_one.py": 12.07,
    "tests/test_p3v6f1_identifier_corner.py": 0.83,
    "tests/test_p3v7f1_escaped_declarations.py": 1.5,
    "tests/test_p3v7f2_corner_parity.py": 28.62,
    "tests/test_p3v8f5_published_keys.py": 108.57,
    "tests/test_p3v9f10_changelog_container.py": 0.0,
    "tests/test_p3v9f1_declared_words_disclosed.py": 0.57,
    "tests/test_p3v9f2_one_key_space.py": 0.58,
    "tests/test_p3v9f3_escaping_is_display_only.py": 1.15,
    "tests/test_p3v9f4_declarations_not_keys.py": 1.06,
    "tests/test_p3v9f5_sentinels_settle.py": 1.05,
    "tests/test_p3v9f6_migration_names_every_option.py": 0.26,
    "tests/test_p3v9f7_declarations_not_keystrokes.py": 0.5,
    "tests/test_p4a1_calendar_placeholders.py": 5.53,
    "tests/test_p4a58_asking_shapes.py": 1.72,
    "tests/test_p4a60_answers_handed_back.py": 3.74,
    "tests/test_p4d140_number_censuses.py": 87.74,
    "tests/test_p4d14_pad_widths.py": 2.81,
    "tests/test_p4d15_dotted_and_two_digit_dates.py": 2.52,
    "tests/test_p4d15_textual_dates.py": 0.52,
    "tests/test_p4d16_padded_numbers.py": 0.52,
    "tests/test_p4d17_group_commas.py": 1.35,
    "tests/test_p4d182_layout_packing.py": 4.92,
    "tests/test_p4d184_joined_value_counts.py": 24.76,
    "tests/test_p4d185_grouped_cells.py": 14.38,
    "tests/test_p4d186_title_rows.py": 2.15,
    "tests/test_p4d187_numbers_stored_as_text.py": 2.96,
    "tests/test_p4d188_sheet_names_in_the_report.py": 1.06,
    "tests/test_p4d189_format_codes_as_written.py": 1.58,
    "tests/test_p4d18_role_topology.py": 0.23,
    "tests/test_p4d18_shape_forms.py": 126.87,
    "tests/test_p4d190_numbers_carry_the_average.py": 6.22,
    "tests/test_p4d191_p4d192_date_counts.py": 15.09,
    "tests/test_p4d193_twice_written_wholes.py": 12.73,
    "tests/test_p4d194_signed_marks.py": 21.64,
    "tests/test_p4d195_width_conventions_named.py": 7.84,
    "tests/test_p4d196_identifier_layout_partners_signs.py": 3.61,
    "tests/test_p4d197_stored_as_text_withheld.py": 4.38,
    "tests/test_p4d198_truth_values_written.py": 19.17,
    "tests/test_p4d19_declared_codes.py": 2.35,
    "tests/test_p4d21_joined_numbers.py": 11.87,
    "tests/test_p4d230_prefixed_partners_wear_named_layouts.py": 2.36,
    "tests/test_p4d233_hexadecimal_prefix.py": 8.05,
    "tests/test_p4d239_forced_counts_of_one.py": 11.47,
    "tests/test_p4d241_record_shape_names_no_column.py": 3.93,
    "tests/test_p4d242_commonest_written_name.py": 0.23,
    "tests/test_p4d243_comma_shape_forms.py": 50.04,
    "tests/test_p4d244_made_up_can_coincide.py": 0.85,
    "tests/test_p4d26_contract_describes_the_producer.py": 0.08,
    "tests/test_p4d26_decimal_comma.py": 4.65,
    "tests/test_p4d27_address_remark.py": 2.35,
    "tests/test_p4d27_note_grammar_matches_the_code.py": 0.32,
    "tests/test_p4d27_token_not_quantity.py": 0.22,
    "tests/test_p4d28_free_text_keeps_its_kind.py": 1.07,
    "tests/test_p4d291_dates_a_reader_opens.py": 2.36,
    "tests/test_p4d298_absorbed_readings.py": 1.61,
    "tests/test_p4d2_loud_decline.py": 0.75,
    "tests/test_p4d30_field_widths.py": 2.26,
    "tests/test_p4d32_empty_bins.py": 23.17,
    "tests/test_p4d334_sentence_arguments.py": 55.37,
    "tests/test_p4d341_population_floor.py": 13.78,
    "tests/test_p4d349_tail_reconstruction.py": 8.39,
    "tests/test_p4d353_cost_rule.py": 39.61,
    "tests/test_p4d357_review_of_followup_a.py": 100.31,
    "tests/test_p4d361_compared_reaches.py": 146.08,
    "tests/test_p4d375_earlier_descriptions.py": 0.92,
    "tests/test_p4d375_review_of_g1.py": 0.7,
    "tests/test_p4d382_typed_workbook_cells.py": 56.75,
    "tests/test_p4d390_counts_per_block.py": 269.5,
    "tests/test_p4d411_mode.py": 0.78,
    "tests/test_p4d42_clock_role.py": 5.05,
    "tests/test_p4d43_date_readings.py": 2.22,
    "tests/test_p4d44_unrepresentable_widths.py": 11.65,
    "tests/test_p4d46_day_first.py": 0.32,
    "tests/test_p4d48_kurtosis.py": 0.22,
    "tests/test_p4d4_affixed_role.py": 14.02,
    "tests/test_p4d5_long_tail_labels.py": 2.34,
    "tests/test_p4d61_holes_reproduced.py": 1.23,
    "tests/test_p4d62_machine_artifacts.py": 0.36,
    "tests/test_p4d64_judged_stand_ins_written.py": 57.54,
    "tests/test_p4g3r1_joined_review.py": 68.54,
    "tests/test_p4r13_compound_role.py": 5.36,
    "tests/test_p4r152_one_page_one_answer.py": 0.36,
    "tests/test_p4r1_withdrawn_claims.py": 4.49,
    "tests/test_p4r24_advisory_remarks.py": 2.06,
    "tests/test_p4r34_form_census_per_level.py": 1.86,
    "tests/test_p4r53_recount_population.py": 2.78,
    "tests/test_p4r56_grid_separation.py": 1.29,
    "tests/test_p4r58_joined_numbers.py": 0.89,
    "tests/test_p4r59_unrepresentable_widths.py": 0.09,
    "tests/test_p4r60_hole_spellings.py": 0.38,
    "tests/test_p4r70_the_report_says_what_the_twin_carries.py": 0.47,
    "tests/test_p5r1_the_grain_clause_is_true.py": 0.96,
    "tests/test_packaging_allowlist.py": 0.0,
    "tests/test_parsing.py": 0.01,
    "tests/test_paths.py": 0.01,
    "tests/test_patient_page.py": 0.58,
    "tests/test_pool_alone_marks.py": 92.96,
    "tests/test_pool_start_keeps_off_keys.py": 11.29,
    "tests/test_pooled_number_scale.py": 5.19,
    "tests/test_pooled_scale_refusals.py": 7.19,
    "tests/test_privacy_unanswered_identifiers.py": 1297.86,
    "tests/test_profile_document.py": 4.88,
    "tests/test_profile_version_4.py": 0.49,
    "tests/test_profile_version_5.py": 1.08,
    "tests/test_provenance.py": 107.49,
    "tests/test_r5_trailing_delimiter_reading.py": 19.72,
    "tests/test_r6_quoted_closing_reading.py": 83.07,
    "tests/test_r6_taxonomy_contract.py": 14.24,
    "tests/test_r6f5_write_transaction.py": 0.1,
    "tests/test_readers_once_a_spelling.py": 8.99,
    "tests/test_offsets_follow_the_date.py": 145.94,
    "tests/test_reading.py": 7.51,
    "tests/test_reading_agreement.py": 7.9,
    "tests/test_reading_header_shape.py": 0.02,
    "tests/test_record_numbers_beside_text.py": 86.55,
    "tests/test_round2_disclosure.py": 42.0,
    "tests/test_round2_numbers_dates.py": 14.15,
    "tests/test_rules_method_page.py": 34.39,
    "tests/test_ruling_first_row_not_told.py": 1.99,
    "tests/test_ruling_identifier_prefix.py": 18.2,
    "tests/test_ruling_levels_counted_by_subtraction.py": 6.57,
    "tests/test_ruling_pooled_held_back_levels.py": 6.97,
    "tests/test_safe_harbor_age_words.py": 141.05,
    "tests/test_safe_harbor_ages_and_address_parts.py": 244.5,
    "tests/test_safe_harbor_ends_and_bounds.py": 192.92,
    "tests/test_safe_harbor_numbers.py": 210.24,
    "tests/test_safe_harbor_places_years_devices.py": 279.66,
    "tests/test_shipped_page_review.py": 3.56,
    "tests/test_short_letters_asked.py": 7.69,
    "tests/test_socket_guard.py": 0.0,
    "tests/test_stage2_dates_as_written.py": 30.1,
    "tests/test_stage2_datetime_oracle.py": 8.03,
    "tests/test_stage2_decimal_comma_readings.py": 0.56,
    "tests/test_stage2_grouping_oracle.py": 1.51,
    "tests/test_stage2_judged_provenance.py": 15.86,
    "tests/test_stage2_nested_grouping_loss.py": 2.28,
    "tests/test_stage2_refusals.py": 1.44,
    "tests/test_stage2_round_trip.py": 66.79,
    "tests/test_stage2_spellings_survive.py": 2.38,
    "tests/test_stage2_summary.py": 1.37,
    "tests/test_stage2_timestamp_spellings.py": 141.78,
    "tests/test_stage3_answer_paths.py": 3.02,
    "tests/test_stage3_default_floor.py": 171.4,
    "tests/test_stage3_gate.py": 34.77,
    "tests/test_stage3_review_dates.py": 3.19,
    "tests/test_stage3_review_numeric_robustness.py": 11.32,
    "tests/test_stage3_review_sentences.py": 8.56,
    "tests/test_stage3_tail_rule.py": 55.98,
    "tests/test_stage3b_base.py": 0.54,
    "tests/test_stage3b_clock.py": 120.74,
    "tests/test_stage3b_clock_minutes.py": 93.11,
    "tests/test_stage3b_clock_review.py": 371.01,
    "tests/test_stage3b_count_pass_speed.py": 154.69,
    "tests/test_stage3b_count_room.py": 78.6,
    "tests/test_stage3b_counted.py": 617.61,
    "tests/test_stage3b_counted_codex.py": 196.32,
    "tests/test_stage3b_date_questions.py": 67.47,
    "tests/test_stage3b_day_of_month.py": 158.95,
    "tests/test_stage3b_full_precision.py": 87.79,
    "tests/test_stage3b_gate.py": 202.03,
    "tests/test_stage3b_heavy_dates.py": 181.7,
    "tests/test_stage3b_hour.py": 254.47,
    "tests/test_stage3b_hour_review.py": 25.13,
    "tests/test_stage3b_joint.py": 389.13,
    "tests/test_stage3b_layout.py": 299.16,
    "tests/test_stage3b_minutes.py": 551.79,
    "tests/test_stage3b_reader.py": 37.7,
    "tests/test_stage3b_reader_review.py": 8.64,
    "tests/test_stage3b_route2.py": 84.54,
    "tests/test_stage3b_second_cut_work.py": 2.96,
    "tests/test_stage3b_shared_clock.py": 190.48,
    "tests/test_stage3b_shared_steps.py": 85.19,
    "tests/test_stage3b_split_order.py": 1.36,
    "tests/test_stage3b_weekday_moments.py": 150.51,
    "tests/test_stage3b_weekday_review.py": 189.77,
    "tests/test_stage3b_width.py": 246.43,
    "tests/test_stage4_allocator_walk.py": 609.72,
    "tests/test_stage4_arrow_groups.py": 31.79,
    "tests/test_stage4_counted_in_persons.py": 865.11,
    "tests/test_stage4_counts_together.py": 1.57,
    "tests/test_stage4_describe_groups.py": 119.36,
    "tests/test_stage4_describe_memory.py": 1134.9,
    "tests/test_stage4_describe_peak.py": 56.86,
    "tests/test_stage4_generate_memory.py": 742.66,
    "tests/test_stage4_linear_work.py": 69.73,
    "tests/test_stage4_million_rows.py": 266.07,
    "tests/test_stage4_number_tail.py": 692.06,
    "tests/test_stage4_numbers_and_codes.py": 212.99,
    "tests/test_stage4_padded_swap_scale.py": 158.03,
    "tests/test_stage4_sign_repairs.py": 43.59,
    "tests/test_stage4_tier2a.py": 247.32,
    "tests/test_stage4_validate_groups.py": 218.82,
    "tests/test_stage5_gate.py": 349.56,
    "tests/test_stage6_band_totals.py": 70.36,
    "tests/test_stage6_chain_describe_scale.py": 126.48,
    "tests/test_stage6_chain_generate.py": 338.92,
    "tests/test_stage6_chain_recount.py": 148.65,
    "tests/test_stage6_chain_recount_settled.py": 49.61,
    "tests/test_stage6_clock_mirror.py": 64.23,
    "tests/test_stage6_order_rules.py": 59.29,
    "tests/test_stage6_patient_profile.py": 354.3,
    "tests/test_stage6_reader_step.py": 16.68,
    "tests/test_stage6_selftest_reports.py": 158.03,
    "tests/test_stage6_validate_chain.py": 62.22,
    "tests/test_summary_and_properties.py": 7.22,
    "tests/test_table_floor.py": 85.52,
    "tests/test_tail_back_solve_without_recursion.py": 17.81,
    "tests/test_taxonomy.py": 0.47,
    "tests/test_terminal_install.py": 2.38,
    "tests/test_terminal_twin.py": 71.33,
    "tests/test_terminal_twin_held.py": 136.04,
    "tests/test_twin_golden.py": 5.0,
    "tests/test_types_and_flags.py": 85.21,
    "tests/test_u1u2_count_every_present_cell.py": 0.53,
    "tests/test_validate_lock.py": 1.32,
    "tests/test_validation.py": 43.17,
    "tests/test_version_reach.py": 53.13,
    "tests/test_window_agreement.py": 177.58,
    "tests/test_workbook_dates.py": 13.16,
    "tests/test_workbook_round_trip.py": 296.89,
    "tests/test_workbook_stream_writer.py": 484.99,
    "tests/test_yes_no_letters_one_pair.py": 4.66,
    "tests/test_zoo_codes_in_pattern.py": 210.41,
    "tests/test_zoo_dates_in_disguise.py": 86.52,
    "tests/test_zoo_few_valued_gap.py": 562.84,
    "tests/test_zoo_held_layouts.py": 904.32,
    "tests/test_zoo_identifiers.py": 86.77,
    "tests/test_zoo_persons_names.py": 90.27,
    "tests/test_zoo_rare_names.py": 377.02,
    "tests/test_zoo_reading_page.py": 3.74,
    "tests/test_zoo_safe_harbor_forms.py": 192.29,
    "tests/test_zoo_safe_harbor_forms_walk.py": 42.6,
    "tests/test_zoo_stand_ins_page.py": 145.51,
    "tests/test_zoo_time_readers.py": 163.24,
    "tests/test_zoo_units.py": 52.99,
    "tests/test_zoo_units_order.py": 84.66,
    "tests/test_zoo_value_readers.py": 341.0,
}

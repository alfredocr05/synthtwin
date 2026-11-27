"""K-HZ-39: twin cells equal to a real key or code, per column and mode, at 20,000 rows (plan P4-D489).

Lane ID-ROOM4, part a. Runs the invented tables of `tests/made_up_key_tables.py` -- the code table
(codes written in the made-up figure writer's grammar, ten rows a code or one a row, beside decimals
with stragglers), the person table (2,000 people of ten rows each: a person key, second keys one a
person, an encounter key on two rows a value, plain figures, a key one a row, a weight and a pulse)
and the device table -- in their modes through the commands a person types (profile with nobody at
the keyboard and the owner's table floor on, the answers rounds where the mode answers, generate seed
0, validate), the codes held by few people of `people_code_table`, and the health data zoo's held keys (`identifier_room_shapes.zoo_equal_cells` over the
zoo tables with a person column beside other keys, and the magnitudes column of
`instrument_magnitudes`, which the dry run must not reach). Counts per column the twin cells equal to
a present real cell of it exactly, case-folded or by merged key, with counters linear in the cells.

THE KEYS. `held_twin_cells_real`: over every column A1 or A2 holds in a mode where the hold applies
(every mode for the code table's columns past a double's range, spelled one letter or figure wider by
method G10.5 step 8, the base's questions file answered `code` included; the codes held by few people,
with the person question open and with the person key declared; every key of the person table with
nothing declared, with the person key declared and nothing answered, with every key declared, with the
person question answered as the zoo answers it, or with the people's own question answered identifier;
and the timed runs), the largest of the three counts: 0, exact. `real_in_files_and_screen`: real key or code values in the
description, summary, questions file, report and screen: 0. `zoo_twin_cells_real`: the zoo's
identifier columns' equal and merging cells and the magnitudes column's equal cells: 0.
`runs_not_written`: runs whose profile or generate did not exit 0: 0. `misses_outside_carry_c2`:
validate misses on a column the lane holds that are not the identifier writer's facts on the exponent
layouts (carry C2, lane HB3-b's): 0. RENAMED `misses_outside_the_carries` by repair 2 and read EXACTLY
(Codex's review of lane ID-ROOM4, item 7): a miss is excused only where its mode, column and fact are one
of carry C2's eight (`made_up_key_tables.C2_MISSES`) or carry C2b's three (the identifier writer on keys
written with comma thousands, `C2B_MISSES`); any other miss on a held column, in any mode, counts.
`validate_missed_runs`: runs whose validate ran and named misses (exit 3): REPORTED. A run whose
validate did not run to its end -- exit 1 or 2, or no quality report written -- is NO EVIDENCE (Codex's
item 8): the driver then prints no KPI line, says which run, and exits 1, so `kpi_run` reads FAIL.
`stated_limit_keep_or_measurement`: the second keys answered keep
-- to their own question or with the person declared -- or declared measurement, which the answer
releases (RULING D5: the twin then draws inside the range): REPORTED, not judged.
`wider_generate_cpu_20000`, `_60000`, `_200000` and `codes_generate_cpu_200000`: the generate step's CPU
seconds on one held column of codes one a row and on the whole code table (RULINGS 5 (2)): REPORTED,
the growth read against the rows in the lane's report. `folded_generate_cpu_100000` and `_200000`: the
same for one held column whose every value has a folded partner (codes `1e400` onward written once with
`e` and once with `E`, `made_up_key_tables`' ``codes-folded``; Codex's review of lane ID-ROOM4, item 4:
the timing fixtures held no folded partners): REPORTED, its doubling ratio read in the lane's report;
every timed run's held twin cells are counted in `held_twin_cells_real`. `stated_limit_code_stand_ins`: the long tail of labels a key or code column
answered `code` becomes outside the role A1 holds, its stand-ins equal to real ones by chance (lane
HB3-b-b's, LANE ID-ROOM4 RULINGS 2): REPORTED. `runs`: how many runs were counted.

Each run's line says how long its commands took (wall and CPU seconds). Where
KPI_KEYS_NEVER_REAL_LINES names a file, the lines are written there too. About 20 CPU minutes at
20,000 rows and the timed runs; one process, about 350 MB.

    .venv/bin/python tools/measurements/kpi_keys_never_real.py --kpi
"""

import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import made_up_key_tables as tables  # noqa: E402

from synthtwin import cli  # noqa: E402

ROWS = 20000
# The modes, in their order (`made_up_key_tables.DRIVER_MODES`, which the gate reads against each mode's table).
MODES = tables.DRIVER_MODES
# `--person` (lane EZ-a, plan P4-D479), where this tree has it.
if hasattr(cli, "_people_said_settled"):
    MODES = MODES + ("persons-person",)
# The zoo tables with a person column beside other keys that the lane's people arm may reach, and
# the one table of numbers past a double's range (its magnitudes the dry run must leave as they are).
ZOO_TABLES = ("relatives", "specimen_units", "i2b2_facts", "long_references", "instrument_magnitudes")
# The writer of A1's held columns, its CPU at growing sizes (the statistics check of lane ID-ROOM4, item
# 1; RULINGS 5 (2)): one column of codes one a row at 20,000, 60,000 and 200,000 rows, and the whole code
# table at 200,000 rows; and one held column whose every value has a folded partner at 100,000 and
# 200,000 rows (Codex's item 4).
TIMED = (
    ("codes-one-a-row", 20000), ("codes-one-a-row", 60000), ("codes-one-a-row", 200000), ("codes", 200000),
    ("codes-folded", 100000), ("codes-folded", 200000),
)
TIMED_KEY = {"codes-one-a-row": "wider_generate_cpu", "codes": "codes_generate_cpu", "codes-folded": "folded_generate_cpu"}


# The columns the lane holds in a mode: `made_up_key_tables.held_in`, which reads repair 2's reproductions
# before the code table's prefix (the gate checks every mode's columns against its table).
held_in = tables.held_in


value = {"held_twin_cells_real": 0, "real_in_files_and_screen": 0, "zoo_twin_cells_real": 0, "runs_not_written": 0,
         "misses_outside_the_carries": 0, "validate_missed_runs": 0, "stated_limit_keep_or_measurement": 0,
         "stated_limit_code_stand_ins": 0,
         "wider_generate_cpu_20000": 0.0, "wider_generate_cpu_60000": 0.0, "wider_generate_cpu_200000": 0.0,
         "codes_generate_cpu_200000": 0.0, "folded_generate_cpu_100000": 0.0, "folded_generate_cpu_200000": 0.0,
         "runs": 0}
lines: "list[str]" = []
unfinished: "list[str]" = []
with tempfile.TemporaryDirectory() as scratch:
    for mode in MODES:
        folder = pathlib.Path(scratch) / mode
        seen = tables.run(folder, mode, ROWS)
        value["runs"] += 1
        exits = seen["exits"]
        if any(code != 0 for code in exits[:-1]):
            value["runs_not_written"] += 1
        held = held_in(mode)
        columns = seen["columns"]
        for name in held:
            value["held_twin_cells_real"] += max(columns[name]["equal"], columns[name]["folded"], columns[name]["merged"])
        if mode in ("persons-declared-keep", "persons-declared-measurement", "persons-own-keep"):
            for name in tables.SECOND_KEYS:
                value["stated_limit_keep_or_measurement"] += columns[name]["equal"]
        # ...and the long tail of labels a key or code column answered code becomes, whose stand-ins
        # equal real ones by chance outside the role A1 holds (lane HB3-b-b's, LANE ID-ROOM4 RULINGS 2): reported.
        if mode in ("persons-declared-code", "codes-code", "codes-base-answered-code"):
            for name in columns:
                if columns[name]["role"] == "long_tail_labels" and name in tables.KEY_COLUMNS + tables.CODE_COLUMNS[:10]:
                    value["stated_limit_code_stand_ins"] += max(columns[name]["equal"], columns[name]["merged"])
        value["real_in_files_and_screen"] += int(seen["real_in_files_and_screen"])
        # ...validate's own outcome first: a run it did not finish is no evidence (Codex's item 8).
        if not tables.validation_completed(seen):
            unfinished += [f"{mode}: validate exit {seen['validated']}, "
                           f"{'no quality report' if seen['misses'] is None else 'a quality report'}"]
        value["validate_missed_runs"] += int(seen["validated"] == 3)
        value["misses_outside_the_carries"] += tables.misses_outside_the_carries(mode, held, seen["misses"] or [])
        counted = ", ".join(
            f"{name} {columns[name]['role']} {columns[name]['equal']}/{columns[name]['folded']}/{columns[name]['merged']}"
            for name in columns
        )
        lines += [f"{mode:30s} exits {exits}, {seen['seconds']} s wall, {seen['cpu_seconds']} CPU s, "
                  f"{seen['real_in_files_and_screen']} real in files, misses {seen['misses']}; {counted}"]
        for written in folder.glob("*"):
            if written.is_file():
                written.unlink()
    # THE HELD WRITER'S TIME: the generate step alone, its CPU at each size, every held twin cell counted.
    for which, rows in TIMED:
        timed = tables.generate_cpu(pathlib.Path(scratch) / f"timed-{which}-{rows}", which, rows)
        value["runs"] += 1
        if any(code != 0 for code in timed["exits"]):
            value["runs_not_written"] += 1
        value[f"{TIMED_KEY[which]}_{rows}"] = timed["generate_cpu"]
        for name, counts in timed["columns"].items():
            if name != "e5seven":
                value["held_twin_cells_real"] += max(counts["equal"], counts["folded"], counts["merged"])
        lines += [f"timed {which} at {rows} rows: exits {timed['exits']}, profile {timed['profile_cpu']} CPU s, "
                  f"generate {timed['generate_cpu']} CPU s; "
                  + ", ".join(f"{name} {c['role']} {c['equal']}/{c['folded']}/{c['merged']}" for name, c in timed["columns"].items())]
    import health_zoo
    import identifier_room_shapes as room

    chosen = tuple(table for table in health_zoo.catalogue() if table.name in ZOO_TABLES)
    by_column: "dict[str, tuple[int, int]]" = {}
    zoo = room.zoo_equal_cells(pathlib.Path(scratch) / "zoo", ROWS, tables=chosen, by_column=by_column)
    value["zoo_twin_cells_real"] += int(zoo["equal"]) + int(zoo["merged"])
    value["runs_not_written"] += int(zoo["unwritten"])
    value["runs"] += int(zoo["tables"])
    magnitudes = pathlib.Path(scratch) / "zoo" / "instrument_magnitudes"
    real = tables.columns_of(magnitudes / "instrument_magnitudes.csv")
    twin_path = magnitudes / "instrument_magnitudes-twin.csv"
    twin = tables.columns_of(twin_path) if twin_path.is_file() else {}
    counted_magnitudes = tables.equal_cells(real["magnitude"], twin.get("magnitude", []))
    value["zoo_twin_cells_real"] += counted_magnitudes["equal"]
    lines += [f"the zoo ({zoo['tables']} tables): {zoo['columns']} identifier columns, {zoo['equal']} equal, "
              f"{zoo['merged']} merging, {zoo['unwritten']} not written; magnitudes {counted_magnitudes}"]
    lines += [f"the zoo: {column} {equal} equal, {merged} merging" for column, (equal, merged) in sorted(by_column.items())]
for line in lines:
    print(line)
if os.environ.get("KPI_KEYS_NEVER_REAL_LINES"):
    pathlib.Path(os.environ["KPI_KEYS_NEVER_REAL_LINES"]).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
if unfinished:
    # NO KPI LINE: a validation that did not run to its end measured nothing (Codex's item 8).
    for line in unfinished:
        print(f"K-HZ-39 NOT MEASURED: {line}", file=sys.stderr)
    raise SystemExit(1)
kpi_rules.emit(
    "K-HZ-39", value,
    f"{len(MODES)} modes of four invented tables at {ROWS} rows, {len(TIMED)} timed runs and {len(ZOO_TABLES)} zoo tables",
)

"""K-HZ-06: twin identifier cells spelled as a real identifier of their column (plan P4-D432).

Runs every shape of `tests/identifier_room_shapes.py` -- lane CODES-3's verify 3's table of UIDs,
record numbers of every width and layout (Cerner decimals, sequential, random, zero-filled,
exported as decimals, CSN strides, NPI-like numbers), prefixed ids, rsIDs, keys beside words and
placeholders held until answered, CODES-3's own gate tables -- and the held shapes answered
`identifier`, at 600 and at 20,000 rows, through the real `synthtwin profile` (scripted, whatever
terminal this is started from), `synthtwin generate` (seed 0); and the health data zoo's every
identifier column at the same two sizes through `health_zoo.run_table`. Counts the twin cells of
each identifier column spelled exactly as a present real cell of that column (`equal_cells`).
Target 0 each, exact. And, since the repair of lane ID-ROOM (skeptic 1, item 3), the twin cells
whose MERGED KEY (`parsing.merged_key`, the form `profile.subject_keys` counts a person by) is a
present real cell's -- one person written two ways is one person -- over the same runs and, at
200,000 rows, over the densest shape that measured it on the lane's first head (`p_five`: 1,800
twin cells merging at 200,000 rows there; one leg, as the lane's brief asks, since 2026-10-26). And, since lane
ID-ROOM2's repair 2 (LANE ID-ROOM2 RULINGS 6 (5)), each of the zoo's held date columns' twin cells naming a day a real
cell of it names, either width of year (`zoo_<table>_<column>_same_day`). Also: how many shapes were measured, how many zoo identifier
columns were read and how many were NOT read (each a failure: no column goes uncounted), and how
many profiles or twins failed to be written (the population floor's refusals of the shapes listed
in REFUSED_AT_600 aside), how many zoo tables the command refused for the people floor, counted
apart from those (`refused_by_floor`; LANE I4q RULINGS 15 (3)), and how many of the shapes listed in VALIDATED fail their twin's own
validation at 20,000 rows (the gate's 20,000-row grid moved here on 2026-10-26: the suite keeps one
case a writer). Each line says how long its profile, generate and validate took; the counting
inside that time is linear and small (the real cells and their merged keys in sets, each twin cell
read once).

The tables are written to a temporary folder and removed. About seventy minutes on the
reference machine (61 on 2026-10-26 under a load average of 25, before the validated shapes joined);
one process, under 1 GB. Where KPI_IDENTIFIER_ROOM_LINES names a file, each run's line is written
there too (kpi_run keeps only the KPI line).

    .venv/bin/python tools/measurements/kpi_identifier_room.py --kpi
"""

import contextlib
import csv
import io
import os
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import identifier_room_shapes as room  # noqa: E402
from synthtwin import cli, parsing  # noqa: E402

SIZES = (600, 20000)
# The densest shape whose merged keys a nought after a prefix tied to a real one on the lane's first
# head (1,800 at 200,000 rows), measured once more at 200,000 rows.
LARGE = ("p_five",)

value = {"twin_cells_equal_to_a_real_identifier": 0, "zoo_twin_cells_equal_to_a_real_identifier": 0,
         "twin_cells_merging_with_a_real_identifier": 0,
         "zoo_twin_cells_merging_with_a_real_identifier": 0,
         "shapes": 0, "zoo_identifier_columns": 0, "zoo_identifier_columns_not_read": 0,
         "not_written": 0, "refused_by_floor": 0, "validated_twins_failing": 0}
lines = []
with tempfile.TemporaryDirectory() as scratch:
    for rows in SIZES + (200000,):
        runs = [(name, "") for name in room.every_shape() if rows == 600 or name not in room.AT_600_ALONE]
        runs += [(name, "identifier") for name, sizes in room.ANSWERED if rows in sizes]
        if rows == 200000:
            runs = [(name, "") for name in LARGE]
        for name, answer in runs:
            folder = pathlib.Path(scratch) / f"{name}-{answer or 'asis'}-{rows}"
            validate = rows == 20000 and not answer and name in room.VALIDATED
            started = time.perf_counter()
            seen = room.run_shape(folder, name, rows, answer=answer, validate=validate)
            took = time.perf_counter() - started
            if validate and seen["exits"][2] != 0:
                value["validated_twins_failing"] += 1
            refused = rows == 600 and not answer and name in room.REFUSED_AT_600
            if seen["exits"][:2] != (0, 0) and not refused:
                value["not_written"] += 1
            value["shapes"] += 1
            value["twin_cells_equal_to_a_real_identifier"] += int(seen["equal"])
            value["twin_cells_merging_with_a_real_identifier"] += int(seen["merged"])
            longest = seen["block"].get("max_length") if isinstance(seen["block"], dict) else None
            wider = sum(1 for cell in seen["twin"] if cell.strip() and isinstance(longest, int)
                        and len(cell) > longest)
            lines += [f"{name:40s} {answer or '-':10s} {rows:6d} rows: exits {seen['exits']}, {took:.1f} s, "
                      f"{seen['equal']} twin cells equal to a real one, {seen['merged']} merging, "
                      f"{wider} written wider"]
            for written in folder.glob("*"):
                if written.is_file():
                    written.unlink()
        if rows == 200000:
            continue
        by_column: "dict[str, tuple[int, int]]" = {}
        same_days: "dict[str, int]" = {}
        zoo = room.zoo_equal_cells(pathlib.Path(scratch) / f"zoo-{rows}", rows, by_column=by_column,
                                   same_days=same_days)
        # Per named column (BATCH 4n OWES 1): the five held birth dates apart, every other column
        # into the totals, which read 0; the held dates' twin cells naming a real day too, either
        # width of year (LANE ID-ROOM2 RULINGS 6 (5)).
        room.tally_zoo(value, by_column, same_days)
        lines += [f"the zoo at {rows} rows: {column} {equal} equal, {merged} merging"
                  for column, (equal, merged) in sorted(by_column.items()) if equal or merged]
        lines += [f"the zoo at {rows} rows: {column} {days} naming a real day"
                  for column, days in sorted(same_days.items()) if days]
        value["zoo_identifier_columns"] += zoo["columns"]
        # ...over the whole catalogue (BATCH 4m OWES 2): the tables run, named beside the columns.
        value["zoo_tables"] = value.get("zoo_tables", 0) + zoo["tables"]
        value["zoo_identifier_columns_not_read"] += zoo["unread"]
        value["not_written"] += zoo["unwritten"]
        # ...and apart from them, the tables the command refused for the people floor (LANE I4q RULINGS
        # 15 (3)), recognised by the command's own words and exit (`room.refused_for_the_people_floor`).
        value["refused_by_floor"] += zoo["refused_by_floor"]
        lines += [f"the zoo at {rows} rows ({zoo['tables']} tables): {zoo['columns']} identifier columns read, {zoo['unread']} "
                  f"not, {zoo['equal']} twin cells equal to a real one, {zoo['merged']} merging, "
                  f"{zoo['unwritten']} tables not written, {zoo['refused_by_floor']} refused for the people floor"]
# THE CENSUS WITHHELD WHOLE (K-HZ-06's target key, lane ID-ROOM3, plan P4-D488; LANE ID-ROOM2 RULINGS 7 (1)): the
# verify's five shapes -- F3u, F2u and F3cu beside other companion columns, P3 and P2 at 2,000 people of ten rows --
# and the planning measure's own census-withheld columns at 1,000 patients (one patient's twenty rows of an ISO
# birth and visit column written in another layout), nobody at the keyboard, each twin cell counted where it is
# a real cell of its column, merges with one, or names a day one names (a two-figure year in both centuries), and
# each validated (`census_withheld_validated_failing`).
import dates_never_real_shapes as made  # noqa: E402


def _withheld_days(cell: str, forms: "tuple[str, ...]") -> "set[object]":
    found: "set[object]" = set()
    for form in forms:
        found |= made.text_days(cell, form)
    return found


value["census_withheld_twin_cells_equal_to_a_real_date"] = 0
value["census_withheld_validated_failing"] = 0
with tempfile.TemporaryDirectory() as scratch:
    births, visits, order = made.people()
    rare = order[0][0]
    persons = [person for person, _index in order]
    mixed = {
        "birth": [births[p].strftime("%d-%b-%Y").upper() if p == rare else births[p].strftime("%Y-%m-%d")
                  for p, _i in order],
        "visit": [visits[p][i].strftime("%d-%b-%Y").upper() if p == rare else visits[p][i].strftime("%Y-%m-%d")
                  for p, i in order],
    }
    withheld_runs = [(name, *made.shape_table(name)[:2]) for name in ("F3u", "F2u", "F3cu", "P3", "P2")]
    withheld_runs += [("planning", ["person_ref", "birth_mixlay", "visit_mixlay"],
                       [[p, b, v] for p, b, v in zip(persons, mixed["birth"], mixed["visit"])])]
    for name, header, rows in withheld_runs:
        folder = pathlib.Path(scratch) / name
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "t.csv"
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(header)
            writer.writerows(rows)
        started = time.perf_counter()
        with room.held_shapes.nobody_at_the_keyboard():
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                exits = [cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"])]
                if exits[0] == 0:
                    exits += [cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}",
                                        "--seed", "0", "--replace"])]
                    exits += [cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                        f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}", "--replace"])]
        if exits[:2] != [0, 0]:
            value["not_written"] += 1
            lines += [f"census withheld {name}: exits {exits}, not written"]
            continue
        if exits[2] != 0:
            value["census_withheld_validated_failing"] += 1
        with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
            twin = list(csv.reader(handle))
        forms = ("%Y-%m-%d",) if name == "planning" else ("%d-%b-%y", "%d-%b-%Y", "%d %b %Y")
        for place in range(1, len(header)):
            column = header[place]
            if column not in ("dob", "birth_mixlay", "visit_mixlay"):
                continue
            real = {row[place] for row in rows if row[place].strip()}
            keys = {parsing.merged_key(cell) for cell in real}
            days: "set[object]" = set()
            for cell in real:
                days |= _withheld_days(cell, forms)
            at = twin[0].index(column)
            hits = sum(1 for row in twin[1:] if row[at].strip() and (
                row[at] in real or parsing.merged_key(row[at]) in keys or _withheld_days(row[at], forms) & days))
            value["census_withheld_twin_cells_equal_to_a_real_date"] += hits
            lines += [f"census withheld {name}.{column}: exits {exits}, {hits} twin cells equal to, merging with "
                      f"or on the day of a real date, {time.perf_counter() - started:.1f} s"]
for line in lines:
    print(line)
# kpi_run reads only the KPI line; KPI_IDENTIFIER_ROOM_LINES names a file the lines are copied to.
if os.environ.get("KPI_IDENTIFIER_ROOM_LINES"):
    pathlib.Path(os.environ["KPI_IDENTIFIER_ROOM_LINES"]).write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
kpi_rules.emit("K-HZ-06", value, f"{len(SIZES)} sizes x {len(room.every_shape())} shapes, "
               f"{len(room.ANSWERED)} answered, {len(LARGE)} at 200,000 rows, and the zoo")

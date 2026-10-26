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
200,000 rows, over the three shapes that measured it on the lane's first head (`p_five`,
`abc_dash_four`, `pad_split`). Also: how many shapes were measured, how many zoo identifier
columns were read and how many were NOT read (each a failure: no column goes uncounted), and how
many profiles or twins failed to be written (the population floor's refusals of the shapes listed
in REFUSED_AT_600 aside), and how many of the shapes listed in VALIDATED fail their twin's own
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

SIZES = (600, 20000)
# The shapes whose merged keys a nought after a prefix or a second zero fill tied to a real one on
# the lane's first head, measured once more at 200,000 rows.
LARGE = ("p_five", "abc_dash_four", "pad_split")

value = {"twin_cells_equal_to_a_real_identifier": 0, "zoo_twin_cells_equal_to_a_real_identifier": 0,
         "twin_cells_merging_with_a_real_identifier": 0,
         "zoo_twin_cells_merging_with_a_real_identifier": 0,
         "shapes": 0, "zoo_identifier_columns": 0, "zoo_identifier_columns_not_read": 0,
         "not_written": 0, "validated_twins_failing": 0}
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
        zoo = room.zoo_equal_cells(pathlib.Path(scratch) / f"zoo-{rows}", rows)
        value["zoo_twin_cells_equal_to_a_real_identifier"] += zoo["equal"]
        value["zoo_twin_cells_merging_with_a_real_identifier"] += zoo["merged"]
        value["zoo_identifier_columns"] += zoo["columns"]
        value["zoo_identifier_columns_not_read"] += zoo["unread"]
        value["not_written"] += zoo["unwritten"]
        lines += [f"the zoo at {rows} rows: {zoo['columns']} identifier columns read, {zoo['unread']} "
                  f"not, {zoo['equal']} twin cells equal to a real one, {zoo['merged']} merging, "
                  f"{zoo['unwritten']} tables not written"]
for line in lines:
    print(line)
# kpi_run reads only the KPI line; KPI_IDENTIFIER_ROOM_LINES names a file the lines are copied to.
if os.environ.get("KPI_IDENTIFIER_ROOM_LINES"):
    pathlib.Path(os.environ["KPI_IDENTIFIER_ROOM_LINES"]).write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
kpi_rules.emit("K-HZ-06", value, f"{len(SIZES)} sizes x {len(room.every_shape())} shapes, "
               f"{len(room.ANSWERED)} answered, {len(LARGE)} at 200,000 rows, and the zoo")

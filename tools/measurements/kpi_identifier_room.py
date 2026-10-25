"""K-HZ-06: twin identifier cells spelled as a real identifier of their column (plan P4-D432).

Runs every shape of `tests/identifier_room_shapes.py` -- lane CODES-3's verify 3's table of UIDs,
record numbers of every width and layout (Cerner decimals, sequential, random, zero-filled,
exported as decimals, CSN strides, NPI-like numbers), prefixed ids, rsIDs, keys beside words and
placeholders held until answered, CODES-3's own gate tables -- and the held shapes answered
`identifier`, at 600 and at 20,000 rows, through the real `synthtwin profile` (scripted, whatever
terminal this is started from), `synthtwin generate` (seed 0); and the health data zoo's every
identifier column at the same two sizes through `health_zoo.run_table`. Counts the twin cells of
each identifier column spelled exactly as a present real cell of that column (`equal_cells`).
Target 0 each, exact. Also: how many shapes were measured, how many zoo identifier columns were
read, and how many profiles or twins failed to be written (the population floor's refusals of
the shapes listed in REFUSED_AT_600 aside).

The tables are written to a temporary folder and removed. About forty minutes on the
reference machine; one process, under 600 MB.

    .venv/bin/python tools/measurements/kpi_identifier_room.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import identifier_room_shapes as room  # noqa: E402

SIZES = (600, 20000)

value = {"twin_cells_equal_to_a_real_identifier": 0, "zoo_twin_cells_equal_to_a_real_identifier": 0,
         "shapes": 0, "zoo_identifier_columns": 0, "not_written": 0}
lines = []
with tempfile.TemporaryDirectory() as scratch:
    for rows in SIZES:
        runs = [(name, "") for name in room.every_shape()]
        runs += [(name, "identifier") for name, sizes in room.ANSWERED if rows in sizes]
        for name, answer in runs:
            folder = pathlib.Path(scratch) / f"{name}-{answer or 'asis'}-{rows}"
            seen = room.run_shape(folder, name, rows, answer=answer, validate=False)
            refused = rows == 600 and not answer and name in room.REFUSED_AT_600
            if seen["exits"][:2] != (0, 0) and not refused:
                value["not_written"] += 1
            value["shapes"] += 1
            value["twin_cells_equal_to_a_real_identifier"] += int(seen["equal"])
            lines += [f"{name:40s} {answer or '-':10s} {rows:6d} rows: exits {seen['exits'][:2]}, "
                      f"{seen['equal']} twin cells equal to a real one"]
        zoo = room.zoo_equal_cells(pathlib.Path(scratch) / f"zoo-{rows}", rows)
        value["zoo_twin_cells_equal_to_a_real_identifier"] += zoo["equal"]
        value["zoo_identifier_columns"] += zoo["columns"]
        value["not_written"] += zoo["unwritten"]
        lines += [f"the zoo at {rows} rows: {zoo['columns']} identifier columns, {zoo['equal']} twin "
                  f"cells equal to a real one, {zoo['unwritten']} tables not written"]
for line in lines:
    print(line)
kpi_rules.emit("K-HZ-06", value, f"{len(SIZES)} sizes x {len(room.every_shape())} shapes, "
               f"{len(room.ANSWERED)} answered, and the zoo")

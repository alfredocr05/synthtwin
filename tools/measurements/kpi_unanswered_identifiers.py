"""K-S3-64: real identifier values an unanswered long table publishes (plan P4-D401).

Runs `tests/unanswered_identifier_shapes.py`'s 35 long tables -- 44
patients (150 beside a declared person column), one Safe Harbor
identifier repeated on each patient's rows -- at 600 and at 20,000 rows
through the real `synthtwin profile` (scripted, whatever terminal this is
started from: nothing answered) and `synthtwin generate` (seed 0), and
counts what is real:

- over the 32 shapes a question flags (`HELD` and `BESIDE`): real values
  written whole, or as a number, in the description, its summary, the
  questions file or the screen, fragments of them anywhere there, twin
  cells holding a real value and fragments inside twin cells. Target 0
  each.
- over the three STATED shapes (a name, a street address, a full birth
  date), which no question flags and lane HX2 owns: real values in the
  description and twin cells holding one. Must not get worse.

The tables are written to a temporary folder and removed. About two
minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_unanswered_identifiers.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import unanswered_identifier_shapes as shapes  # noqa: E402

SIZES = (600, 20000)

held = {"description_values": 0, "description_fragments": 0, "twin_cells": 0, "twin_fragments": 0}
stated = {"stated_description_values": 0, "stated_twin_cells": 0}
lines = []
with tempfile.TemporaryDirectory() as scratch:
    for rows in SIZES:
        for kind in shapes.HELD + shapes.BESIDE + shapes.STATED:
            folder = pathlib.Path(scratch) / f"{kind}-{rows}"
            folder.mkdir()
            seen = shapes.run(folder, kind, rows)
            if seen["profile_exit"] != 0 or seen["generate_exit"] != 0:
                raise SystemExit(f"{kind} at {rows} rows: profile {seen['profile_exit']}, "
                                 f"generate {seen['generate_exit']}")
            lines += [f"{kind:8s} {rows:6d} rows: role {seen['role']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"description, {seen['description_fragments']} fragments in its block, "
                      f"{seen['twin_cells']} twin cells real, {seen['twin_fragments']} twin fragments"]
            if kind not in shapes.STATED:
                for key in held:
                    held[key] = held[key] + int(seen[key])
            else:
                stated["stated_description_values"] += int(seen["description_values"])
                stated["stated_twin_cells"] += int(seen["twin_cells"])
for line in lines:
    print(line)
value = dict(held)
value.update(stated)
held_shapes = len(shapes.HELD) + len(shapes.BESIDE)
value["shapes"] = len(SIZES) * (held_shapes + len(shapes.STATED))
kpi_rules.emit("K-S3-64", value, f"{len(SIZES)} sizes x {held_shapes} held and "
               f"{len(shapes.STATED)} stated shapes")

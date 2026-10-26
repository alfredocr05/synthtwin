"""K-S3-64: real identifier values an unanswered long table publishes (plan P4-D401).

Runs `tests/unanswered_identifier_shapes.py`'s long tables -- 44 patients
(150 beside a declared person column), one Safe Harbor identifier repeated
on each patient's rows -- at 600 and at 20,000 rows through the real
`synthtwin profile` (scripted, whatever terminal this is started from:
nothing answered), `synthtwin generate` (seed 0) and `synthtwin validate`,
and counts what is real:

- over the shapes a question flags (`HELD` and `BESIDE`) and the shapes
  lane HX2's count in people holds (`COUNTED`, plan P4-D406: a plan and
  an account number beside a declared person column, and a name, a
  street address and a birth date beside a patient key whose person
  question is open), and the register lists (`LISTED`, plan P4-D424: one
  to three record numbers a cell, six figures, six padded to seven, `R` and
  six figures, and the first beside a declared person column), and the
  columns of a value a row (`ONE_A_ROW`, plan P4-D436: `RPT` and six
  figures counting up, at random, `ACC` and six figures on about four rows
  in three, plain figures counting up across a power of ten, that run with
  one number twice, plain figures at random, and the run beside `-1`): real
  values written whole, or as a number, in the
  description, its summary, the questions file or the screen, fragments
  of them anywhere there, twin cells holding a real value and fragments
  inside twin cells. Target 0 each. And the twins of those shapes that
  fail their own validation, but for the generator's stated limits
  (`VALIDATION_LIMITS`): target 0.
- over the STATED shapes (a name, a street address, a full birth date on
  a long table with no subject column, so no people to count in; plan
  P4-D406 item (a)): real values in the description and twin cells
  holding one. Must not get worse.

The tables are written to a temporary folder and removed. About six
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

held = {"description_values": 0, "description_fragments": 0, "twin_cells": 0, "twin_fragments": 0,
        "twins_failing_validation": 0}
stated = {"stated_description_values": 0, "stated_twin_cells": 0}
# CHANCE IN A FILLED ROOM (lane HX5, plan P4-D436): a held column of a value
# a row publishes nothing, and its twin's made-up record numbers carry the
# figures of a real one where the real values fill the layout's room (20,000
# references counting up among a million six-figure spellings). Counted apart,
# owner lane ID-ROOM (plan P4-D432, held blocks included by its rulings 2):
# twin cells whose figures stand in a real value, and cells equal to one.
chance = {"one_a_row_twin_cells": 0, "one_a_row_twin_fragments": 0, "one_a_row_twin_cells_equal": 0}
lines = []
with tempfile.TemporaryDirectory() as scratch:
    for rows in SIZES:
        for kind in (shapes.HELD + shapes.BESIDE + shapes.COUNTED + shapes.LISTED + shapes.ONE_A_ROW
                     + shapes.STATED):
            folder = pathlib.Path(scratch) / f"{kind}-{rows}"
            folder.mkdir()
            seen = shapes.run(folder, kind, rows)
            if seen["profile_exit"] != 0 or seen["generate_exit"] != 0:
                raise SystemExit(f"{kind} at {rows} rows: profile {seen['profile_exit']}, "
                                 f"generate {seen['generate_exit']}")
            lines += [f"{kind:8s} {rows:6d} rows: role {seen['role']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"description, {seen['description_fragments']} fragments published, "
                      f"{seen['twin_cells']} twin cells real, {seen['twin_fragments']} twin fragments, "
                      f"{seen['twin_cells_equal']} twin cells equal, validate {seen['validate_exit']}"]
            if kind in shapes.ONE_A_ROW:
                held["description_values"] += int(seen["description_values"])
                held["description_fragments"] += int(seen["description_fragments"])
                chance["one_a_row_twin_cells"] += int(seen["twin_cells"])
                chance["one_a_row_twin_fragments"] += int(seen["twin_fragments"])
                chance["one_a_row_twin_cells_equal"] += int(seen["twin_cells_equal"])
                if seen["validate_exit"] != 0 and kind not in shapes.VALIDATION_LIMITS:
                    held["twins_failing_validation"] += 1
            elif kind not in shapes.STATED:
                for key in held:
                    if key != "twins_failing_validation":
                        held[key] = held[key] + int(seen[key])
                if seen["validate_exit"] != 0 and kind not in shapes.VALIDATION_LIMITS:
                    held["twins_failing_validation"] += 1
            else:
                stated["stated_description_values"] += int(seen["description_values"])
                stated["stated_twin_cells"] += int(seen["twin_cells"])
for line in lines:
    print(line)
value = dict(held)
value.update(stated)
value.update(chance)
held_shapes = (len(shapes.HELD) + len(shapes.BESIDE) + len(shapes.COUNTED) + len(shapes.LISTED)
               + len(shapes.ONE_A_ROW))
value["shapes"] = len(SIZES) * (held_shapes + len(shapes.STATED))
kpi_rules.emit("K-S3-64", value, f"{len(SIZES)} sizes x {held_shapes} held and "
               f"{len(shapes.STATED)} stated shapes")

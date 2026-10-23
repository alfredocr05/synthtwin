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
  question is open): real values written whole, or as a number, in the
  description, its summary, the questions file or the screen, fragments
  of them anywhere there, twin cells holding a real value and fragments
  inside twin cells. Target 0 each. And the twins of those shapes that
  fail their own validation, but for the generator's stated limits
  (`VALIDATION_LIMITS`): target 0.
- over lane SH's Safe Harbor number shapes (plan P4-D427,
  `SAFE_HARBOR_NUMBERS`: five-figure ZIP codes beside `UNKNOWN` once or
  `HOMELESS` three times, with and without a leading zero, and ages
  above 89, plain and beside `999` once or twenty times or `-9`), counted
  the same way into the same keys -- an age above 90 counted as published
  where an output of the table carries it more often than the same output
  of the table with every value above 89 written 90, an output that
  differs counted as a fragment, a twin cell above 90 as a real cell --
  and twins failing validation, the real age tables' own validation
  among them, but the held block's named limit at 20,000 rows. Target 0.
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
lines = []
with tempfile.TemporaryDirectory() as scratch:
    for rows in SIZES:
        for kind in shapes.HELD + shapes.BESIDE + shapes.COUNTED + shapes.STATED:
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
                      f"validate {seen['validate_exit']}"]
            if kind not in shapes.STATED:
                for key in held:
                    if key != "twins_failing_validation":
                        held[key] = held[key] + int(seen[key])
                if seen["validate_exit"] != 0 and kind not in shapes.VALIDATION_LIMITS:
                    held["twins_failing_validation"] += 1
            else:
                stated["stated_description_values"] += int(seen["description_values"])
                stated["stated_twin_cells"] += int(seen["twin_cells"])
        # LANE SH'S SAFE HARBOR NUMBER SHAPES (plan P4-D427).
        for kind in shapes.SAFE_HARBOR_NUMBERS:
            folder = pathlib.Path(scratch) / f"{kind}-{rows}"
            folder.mkdir()
            seen = shapes.run_safe_harbor(folder, kind, rows)
            if seen["profile_exit"] != 0 or seen["generate_exit"] != 0:
                raise SystemExit(f"{kind} at {rows} rows: profile {seen['profile_exit']}, "
                                 f"generate {seen['generate_exit']}")
            lines += [f"{kind:8s} {rows:6d} rows: role {seen['role']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"outputs, {seen['description_fragments']} outputs differing, "
                      f"{seen['twin_cells']} twin cells real, validate {seen['validate_exit']}, "
                      f"the real table {seen['validate_real_exit']}"]
            for key in held:
                if key != "twins_failing_validation":
                    held[key] = held[key] + int(seen[key])
            limited = rows >= 20000 and kind in shapes.SAFE_HARBOR_HELD_LIMITS_AT_20000
            if seen["validate_exit"] != 0 and not limited:
                held["twins_failing_validation"] += 1
            if kind in shapes.AGES and seen["validate_real_exit"] != 0:
                held["twins_failing_validation"] += 1
for line in lines:
    print(line)
value = dict(held)
value.update(stated)
held_shapes = (len(shapes.HELD) + len(shapes.BESIDE) + len(shapes.COUNTED)
               + len(shapes.SAFE_HARBOR_NUMBERS))
value["shapes"] = len(SIZES) * (held_shapes + len(shapes.STATED))
kpi_rules.emit("K-S3-64", value, f"{len(SIZES)} sizes x {held_shapes} held and "
               f"{len(shapes.STATED)} stated shapes")

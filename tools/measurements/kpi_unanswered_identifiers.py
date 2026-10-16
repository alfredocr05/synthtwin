"""K-S3-64: real identifier values an unanswered long table publishes (plan P4-D401).

Runs `tests/unanswered_identifier_shapes.py`'s ten long tables -- 44
patients, one Safe Harbor identifier repeated on each patient's rows --
at 600 and at 20,000 rows through the real `synthtwin profile` (nothing
declared, nothing answered) and `synthtwin generate` (seed 0), and counts
what is real:

- over the six shapes a question flags (a record number, a health plan
  number, an e-mail address, an account number, a telephone number and a
  social security number): real values written whole in the description,
  its summary and the questions file, fragments of them in the column's
  own block, twin cells holding a real value and fragments inside twin
  cells. Target 0 each.
- over the four STATED shapes (a name, a street address, a full birth
  date, a study subject code of five figures), owned by lane CODES-2's
  allowlist: real values in the description and twin cells holding one.
  Must not get worse.

The tables are written to a temporary folder and removed. About a minute
on the reference machine.

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
        for kind in shapes.HELD + shapes.STATED:
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
            if kind in shapes.HELD:
                for key in held:
                    held[key] = held[key] + int(seen[key])
            else:
                stated["stated_description_values"] += int(seen["description_values"])
                stated["stated_twin_cells"] += int(seen["twin_cells"])
for line in lines:
    print(line)
value = dict(held)
value.update(stated)
value["shapes"] = len(SIZES) * (len(shapes.HELD) + len(shapes.STATED))
kpi_rules.emit("K-S3-64", value, f"{len(SIZES)} sizes x {len(shapes.HELD)} held and "
               f"{len(shapes.STATED)} stated shapes")

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
  one number twice, plain figures at random, and the run beside `-1`; and,
  from lane HX5's repair 1, `SPECIMEN`, `S24-` and `-A` references, the run
  beside `-9999`, and the run and `RPT` references with one stray cell): real
  values written whole, or as a number, in the
  description, its summary, the questions file or the screen, fragments
  of them anywhere there, twin cells holding a real value and fragments
  inside twin cells. Target 0 each. And the twins of those shapes that
  fail their own validation, but for the generator's stated limits
  (`VALIDATION_LIMITS`): target 0.
- over lane SH's Safe Harbor number shapes (plan P4-D427,
  `SAFE_HARBOR_NUMBERS`: ZIP codes of four or five figures in every role,
  beside words and placeholders of any share, signed or beside ZIP+4
  cells, and ages above 89 in every role, beside an outlier, placeholders
  or words of any share, written with a unit word or a plus sign, or
  beside an open person question), counted the same way into the same
  keys -- an age above 90 counted as published where an output of the
  table carries it more often than the same output of the table with
  every age from 90 to 125 written 90, an output that differs counted as
  a fragment, a twin cell above 90 as a real cell, and a held twin's
  made-up value equal to a real ZIP by chance counted apart (the same
  table with every ZIP written as another twins it too) -- and twins
  failing validation, the real age tables' own validation among them
  (a held block's real table but for the census of repetition every held
  block's real table misses), but the held block's named limit at
  20,000 rows and an age twin missing only what the top-coded table's
  own twin misses. And the same over `SAFE_HARBOR_ANSWERED` (the second
  repair of lane SH): each shape once its column's other question is
  answered -- NAACCR's three-figure ages `measurement` or `code`, ZIP
  codes `measurement`, `keep` or `code` (its third repair, the
  orchestrator's ruling R1 of 2026-10-25) -- where the Safe Harbor
  question is then put; and the zoo's own `patients.zip5` (`ZOO_ZIPS`),
  answered `code` and then `yes` as the zoo's person answers. Target 0.
- over lane SH2's Safe Harbor years, places and devices (plan P4-D434,
  `SH2_SHAPES`: years of birth beside a stray cell, top-coded at the year
  an age of 90 shows against this release's reference year, and held where
  they are ZIP-shaped too; birth dates in two spellings; a city of
  birth; ZIP codes cut to three figures; GS1 device identifiers; and ZIP
  codes answered `excel-1900`), counted the same way into the same keys
  -- a year before the group counted as published where an output of the
  table carries it more often than the same output of the table with
  every such year written as the group's, a twin cell reading as such a
  year or date as a real cell, ZIP codes read as dates by the dates they
  name too -- and twins failing validation, the top-coded years' real
  table and a held block's real table but for the census of repetition
  among them, but the held block's named limits (`SH2_HELD_LIMITS`,
  `SH2_HELD_LIMITS_AT_600`); a shape put any question but the one Safe
  Harbor question stops the run. AND ITS CLOSE ROUND'S: latitudes and
  longitudes, named or a pair by their cells, counted by a counter
  linear in the data (`count_linear`; a held twin's made-up places equal
  to real ones by chance counted apart, as ZIP codes' are); places beside
  their states; DICOM ages answered `keep`, a twin cell above 90 years
  counted real; and ages beside placeholders on few rows or a value past
  125, every fact of the block above 90 counted published and every twin
  cell above 90 real.
  Target 0.
- over the STATED shapes (a name, a street address, a full birth date on
  a long table with no subject column, so no people to count in; plan
  P4-D406 item (a)): real values in the description and twin cells
  holding one. Must not get worse.

The tables are written to a temporary folder and removed. About six
minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_unanswered_identifiers.py --kpi
"""

import pathlib
import re
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
# THE ONE LIST CASE OF CHANCE APART (BATCH 4m OWES 1, Codex's review of
# batch 4l, its first Medium): `shapes.tally_held` counts exactly
# (reglistmixR, 20,000 rows) under keys of its own and a register list's
# members equal to a real key, as written or by the merged key, at every
# shape and size; each bounded in the ledger, every other shape at 0.
held.update({"list_chance_twin_cells": 0, "list_chance_twin_fragments": 0,
             "twin_members_equal": 0, "twin_members_merging": 0})
held.update({"held_limit_twins_failing_validation": 0})
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
                      f"{seen['twin_cells_equal']} twin cells equal, validate {seen['validate_exit']}; "
                      f"profile, generate and validate {seen['product_seconds']} s, counting "
                      f"{seen['counting_seconds']} s"]
            if kind in shapes.ONE_A_ROW:
                held["description_values"] += int(seen["description_values"])
                held["description_fragments"] += int(seen["description_fragments"])
                chance["one_a_row_twin_cells"] += int(seen["twin_cells"])
                chance["one_a_row_twin_fragments"] += int(seen["twin_fragments"])
                chance["one_a_row_twin_cells_equal"] += int(seen["twin_cells_equal"])
                if seen["validate_exit"] != 0 and kind not in shapes.VALIDATION_LIMITS:
                    held["twins_failing_validation"] += 1
            elif kind not in shapes.STATED:
                shapes.tally_held(held, kind, rows, seen)
                if seen["validate_exit"] != 0 and kind not in shapes.VALIDATION_LIMITS:
                    held["twins_failing_validation"] += 1
            else:
                stated["stated_description_values"] += int(seen["description_values"])
                stated["stated_twin_cells"] += int(seen["twin_cells"])
        # LANE SH'S SAFE HARBOR NUMBER SHAPES (plan P4-D427), unanswered and
        # with the column's other question answered (its second repair).
        harbor = [(kind, "") for kind in shapes.SAFE_HARBOR_NUMBERS]
        for kind, answer in harbor + list(shapes.SAFE_HARBOR_ANSWERED):
            folder = pathlib.Path(scratch) / f"{kind}-{rows}-{answer or 'unanswered'}"
            folder.mkdir()
            seen = shapes.run_safe_harbor(folder, kind, rows, answer)
            if seen["profile_exit"] != 0 or seen["generate_exit"] != 0:
                raise SystemExit(f"{kind} at {rows} rows: profile {seen['profile_exit']}, "
                                 f"generate {seen['generate_exit']}")
            lines += [f"{kind:8s} {answer or 'unanswered'} {rows:6d} rows: role {seen['role']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"outputs, {seen['description_fragments']} outputs differing, "
                      f"{seen['twin_cells']} twin cells real, validate {seen['validate_exit']}, "
                      f"the real table {seen['validate_real_exit']}, "
                      f"{seen.get('twin_cells_by_chance', 0)} made-up twin cells equal "
                      f"to a real ZIP by chance"]
            for key in shapes.HELD_KEYS:
                held[key] = held[key] + int(seen[key])
            limited = (rows >= 20000 and kind in shapes.SAFE_HARBOR_HELD_LIMITS_AT_20000) or (
                rows < 20000 and kind in shapes.SAFE_HARBOR_HELD_LIMITS_AT_600)
            if kind not in shapes.ZIP_KINDS and answer:
                # An age twin's limit is the top-coded table's own.
                limited = seen["twin_misses"] == seen["control_twin_misses"]
            elif kind not in shapes.ZIP_KINDS and limited:
                # ...and held, unanswered, a kind of shapes.HELD_LIMIT_MISSES
                # only its measured subchecks (BATCH 4n OWES 2).
                limited = shapes.held_limit_met(kind, seen)
            if seen["validate_exit"] != 0 and not limited:
                held["twins_failing_validation"] += 1
            # ...and the known limits' failing twins reported apart (BATCH 4n
            # OWES 3, Codex's review of batch 4m, its third Medium): naaccr's,
            # owner lane HB2; `twins_failing_validation` keeps no allowance.
            if seen["validate_exit"] != 0 and limited and not answer and kind in shapes.HELD_LIMIT_MISSES:
                held["held_limit_twins_failing_validation"] += 1
            missed = set(re.findall(r"^\s+(\S+) \[[^\]]+\]: MISSED",
                                    f"{seen['real_quality']}", re.M))
            if kind in shapes.AGES and seen["validate_real_exit"] != 0 and not (
                seen["role"] == "identifier"
                and missed <= {"distinct.n_distinct_by_occurrences"}
            ):
                held["twins_failing_validation"] += 1
        # LANE SH2'S SAFE HARBOR YEARS, PLACES AND DEVICES (plan P4-D434).
        for number, kind in enumerate(shapes.SH2_SHAPES):
            # ...each in a folder of its own number: `CITYText` and
            # `cityname` are one folder on a disk that folds case (macOS).
            folder = pathlib.Path(scratch) / f"sh2-{number}-{kind}-{rows}"
            folder.mkdir()
            seen = shapes.run_sh2(folder, kind, rows)
            if seen["profile_exit"] != 0 or seen["generate_exit"] != 0:
                raise SystemExit(f"{kind} at {rows} rows: profile {seen['profile_exit']}, "
                                 f"generate {seen['generate_exit']}")
            # ...ONE QUESTION, lane SH's, never a second: the gate's own
            # check, here at 20,000 rows too (the gate runs 600 rows).
            if seen["asked"] != shapes.sh2_asked(kind):
                raise SystemExit(f"{kind} at {rows} rows: asked {seen['asked']}")
            lines += [f"{kind:8s} {rows:6d} rows: role {seen['role']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"outputs, {seen['description_fragments']} fragments, "
                      f"{seen['twin_cells']} twin cells real, validate {seen['validate_exit']}, "
                      f"the real table {seen['validate_real_exit']}, asked {seen['asked']}, "
                      f"{seen.get('twin_cells_by_chance', 0)} made-up twin cells equal to a real "
                      f"place by chance"]
            # Through the one tally, as every held shape above: a key of its
            # own for the one list case of chance, and `run_sh2` carries no
            # list member's counts (LANE I4m RULINGS 6 (4)).
            shapes.tally_held(held, kind, rows, seen)
            if seen["validate_exit"] != 0 and kind not in shapes.SH2_HELD_LIMITS and not (
                rows < 20000 and kind in shapes.SH2_HELD_LIMITS_AT_600
            ):
                held["twins_failing_validation"] += 1
            missed = set(re.findall(r"^\s+(\S+) \[[^\]]+\]: MISSED",
                                    f"{seen['real_quality']}", re.M))
            if seen["validate_real_exit"] != 0 and not (
                seen["role"] == "identifier"
                and missed <= {"distinct.n_distinct_by_occurrences"}
            ):
                held["twins_failing_validation"] += 1
        # ...and the zoo's own ZIP codes, answered `code` and then `yes`
        # (the third repair of lane SH, ruling R1 of 2026-10-25).
        for kind in shapes.ZOO_ZIPS:
            folder = pathlib.Path(scratch) / f"zoo-{rows}"
            folder.mkdir()
            seen = shapes.run_zoo_zips(folder, rows)
            steps = seen["steps"]
            assert isinstance(steps, dict)
            if steps.get("profile") != 0 or steps.get("answers") != 0 or steps.get("generate") != 0:
                raise SystemExit(f"{kind} at {rows} rows: {steps}")
            lines += [f"{kind} code, then yes {rows:6d} rows: role {seen['roles']}, "
                      f"{seen['description_values']} of {seen['different']} real values in the "
                      f"outputs, {seen['description_fragments']} fragments, "
                      f"{seen['twin_cells']} twin cells real, validate {steps.get('validate')}"]
            for key in shapes.HELD_KEYS:
                held[key] = held[key] + int(seen[key])  # type: ignore[call-overload]
            if steps.get("validate") != 0:
                held["twins_failing_validation"] += 1
for line in lines:
    print(line)
value = dict(held)
value.update(stated)
value.update(chance)
held_shapes = (len(shapes.HELD) + len(shapes.BESIDE) + len(shapes.COUNTED)
               + len(shapes.LISTED)
               + len(shapes.SAFE_HARBOR_NUMBERS) + len(shapes.SAFE_HARBOR_ANSWERED)
               + len(shapes.ZOO_ZIPS) + len(shapes.ONE_A_ROW) + len(shapes.SH2_SHAPES))
value["shapes"] = len(SIZES) * (held_shapes + len(shapes.STATED))
kpi_rules.emit("K-S3-64", value, f"{len(SIZES)} sizes x {held_shapes} held and "
               f"{len(shapes.STATED)} stated shapes")

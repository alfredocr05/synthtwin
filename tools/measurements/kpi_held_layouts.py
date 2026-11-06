"""K-HZ-13: held and unanswered columns written in their own valid layouts (plan P4-D442).

Runs the lane's hunt -- `tests/held_layouts_shapes.py`: record numbers beside `-1` and `-99` and
the same column with those cells blank, keys of 44 patients beside `-1` (2 % and 40 %), a
telephone number opening `+`, a key exported as `100001.0`, UIDs with no root and a held UID, the
walk's persons (zero-filled halves, a number beside its `.0`, a dotted pad, `P` beside `P-`),
birth dates in mixed layouts and beside `UNKNOWN`, a column of two dates, three people's `pending`
and a two-figure `PatientStudyKey` beside `-1` -- and every held and unanswered shape of
`tests/unanswered_identifier_shapes.py` (K-S3-64's `HELD`, `BESIDE` and `COUNTED`) at 20,000 rows,
through the real `synthtwin profile` (scripted, nothing answered), `synthtwin generate` (seed 0) and
`synthtwin validate`; the quoted comma lists of record numbers at 600 rows (the internal smoke);
the record numbers beside `-1` and their blank pair, and the birth dates in two layouts (read as
record numbers there), at 200,000 rows; and the zoo's `tumor_registry` and `labs` at 20,000 rows
(their held `dx_date` and `viral_load`, through the zoo's own truthful answers). Counts, each
target 0:

- `held_twins_failing_validation`: twins whose own validation exits other than 0 (`reglistmixR`'s,
  declared as the person column in place of lane HX4's hold, recorded apart);
- `invalid_date_strings`: twin cells of a date shape -- figures and marks, or one run of three
  letters among them (a month word) -- that no layout of the source reads as a valid date
  (`7949-90-04`, `0000-00-00`, `00-AAA-0000`), the zoo's `dx_date` among them;
- `uids_off_the_grammar`: twin cells of a UID shape off `[012](\\.(0|[1-9]\\d*))+` or past 64
  characters;
- `real_persons_merged`: over the hunt's shapes of record numbers, the real column's different
  merged keys (`parsing.merged_key`) less the twin's, and its different values read as numbers less
  the twin's, where positive;
- `real_keys_in_held_list_cells`: made-up keys inside the list cells of a column of keys between
  commas -- held as record numbers until answered, or declared so -- whose merged key is a real key's
  of the column, at 20,000 rows (HX4's register lists at 600);
- `list_cells_carrying_a_real_key`: twin cells of those list shapes carrying a real key -- a run of
  figures that is a real key's, or a real key holding a letter found inside the cell as text -- lane
  HX4's `reglistmixR` (marks `;`, `,` and `|` cell by cell) among them at seeds 0 and 1 (LANE HB
  RULINGS 3: by construction, on any draw);
- `named_key_twin_cells_real`: twin cells of the key named as a key that equal a real key.

- `slow_beside_a_placeholder`: pairs whose generate beside the placeholder asks more than twice the
  `parsing.layout_form` calls a row of the same column's with those cells blank, at 20,000 and
  200,000 rows -- a machine-free key (lane HB's skeptic 1, item 6);

and `placeholder_time_ratio_most`, the largest ratio of a pair's generate processor seconds beside
the placeholder to the same column's with those cells blank, at 20,000 and 200,000 rows, is bounded
at 2.5 (target 2.0): the brief's "within twice" is met on average and missed at random (lane HB's
statistics skeptic, item 4).

Recorded beside them, never failed: `shapes`; `placeholder_layout_calls_ratio_most` (the largest
ratio in `layout_form` calls a row); `real_dates_written_by_chance` (made-up valid dates of a HELD shape -- read as record
numbers, free text or long-tail labels -- equal to a real date of their column that the
description does not publish: an attribute, never a key, ID-ROOM's ruling 1 (3)); `real_persons_split`
(the twin's different merged keys and numbers less the real column's, where positive: one real
person written two ways, P4-D442's stated limit (j)); `persons_merged_in_the_source_layouts` (persons
merged counted over the twin cells in the source's own layouts alone); `e_notation_the_source_never_wrote`
(numbers written with a power of ten where the source wrote none: stated limit (k));
`non_numbers_in_a_numbers_column` (the zoo's `viral_load`, each cell read past a censoring `<` or `>`: stated limit (h));
`twins_recorded_apart_failing_validation` (the shapes `hunt.RECORDED_APART` names: linked order numbers once
each, whose free text misses its mean length as on the base, stated limit (t)); and `list_cells_written_as_no_list` (the list cells of the random keys between commas, `hunt.KEPT_AS_LISTS`,
the twin writes as no list; judged 0 since rule 22). Since lane HB's repair 2 the hunt also reads keys in free text marked `;` and `|`, alone among
notes and once each between commas (the verify's finding 1: 0 real keys and 0 equal cells by construction).
Since lane HB's close round 2 (LANE HB RULINGS 8) it also reads, under `list_cells_carrying_a_real_key`, the
twin cells no published spelling names that equal a held-back real cell or hold one's run of four figures or more
as written, noughts kept (`hunt.cells_holding_a_real_run`), on the twelve shapes of `hunt.SHAPES` whose kind is
`runs` (counted from the registry by the gate, LANE HB RULINGS 9 (4)): a level of two runs on two rows
in five beside keys once each (`two_runs_published`), padded keys once each among notes in other scripts and at
the table's floor (`pad_notes_cjk`, `pad_notes_cyrillic`, `pad_notes_arabic`, `pad_notes_floor`), runs `1` to
`999` zero-filled to 4 to 9 figures beside the same three figures wider (`padded_inside_4` to `padded_inside_9`),
and keys beside eleven cells of a declared absent spelling (`rebuilt_as_absent`).

Every count is linear in the cells: each real value and each twin cell read once into a set. The
tables are written to a temporary folder and removed. About twenty-five minutes on the reference
machine, one process under 500 MB.

    .venv/bin/python tools/measurements/kpi_held_layouts.py --kpi
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
from synthtwin import parsing  # noqa: E402
import held_layouts_shapes as hunt  # noqa: E402
import unanswered_identifier_shapes as held_shapes  # noqa: E402

ROWS = 20000
LARGE = 200000

value = {"held_twins_failing_validation": 0, "invalid_date_strings": 0, "uids_off_the_grammar": 0,
         "real_persons_merged": 0, "slow_beside_a_placeholder": 0, "real_keys_in_held_list_cells": 0,
         "named_key_twin_cells_real": 0, "shapes": 0, "real_dates_written_by_chance": 0,
         "placeholder_time_ratio_most": 0.0, "placeholder_layout_calls_ratio_most": 0.0,
         "real_persons_split": 0, "persons_merged_in_the_source_layouts": 0,
         "e_notation_the_source_never_wrote": 0, "non_numbers_in_a_numbers_column": 0,
         "list_cells_carrying_a_real_key": 0, "twins_recorded_apart_failing_validation": 0,
         "list_cells_written_as_no_list": 0}
lines = []
seconds: "dict[tuple[str, int], float]" = {}
calls: "dict[tuple[str, int], float]" = {}
_layout_form = parsing.layout_form
_layout_calls = [0]


def _counted_layout_form(*arguments: object) -> str:
    _layout_calls[0] += 1
    return _layout_form(*arguments)  # type: ignore[arg-type]


with tempfile.TemporaryDirectory() as scratch:
    runs = [(name, ROWS) for name in hunt.SHAPES if name not in hunt.AT_600]
    runs += [(name, 600) for name in hunt.AT_600]
    # ...and each shape of more than one seed again at its other seeds (LANE HB RULINGS 3).
    again = [(name, ROWS, seed) for name, seeds in hunt.SEEDS.items() for seed in seeds[1:]]
    # KPI_HELD_LAYOUTS_NO_LARGE leaves the 200,000-row runs out (a base whose search beside a
    # placeholder takes about 9 ms a row would hold the slot for an hour; say so where it is used).
    if not os.environ.get("KPI_HELD_LAYOUTS_NO_LARGE"):
        runs += [(name, LARGE) for pair in hunt.PAIRS.items() for name in pair]
        runs += [("dob_mixed", LARGE)]
        runs += [(name, LARGE) for name in hunt.LARGE_LISTS]
    for name, rows, seed in [(name, rows, 0) for name, rows in runs] + again:
        if (name, rows) in seconds and not seed:
            continue
        folder = pathlib.Path(scratch) / f"{name}-{rows}-{seed}"
        paired = any(name in pair for pair in hunt.PAIRS.items())
        _layout_calls[0] = 0
        if paired:
            parsing.layout_form = _counted_layout_form  # type: ignore[assignment]
        try:
            seen = hunt.run(folder, name, rows, validate=rows != LARGE, seed=seed)
        finally:
            parsing.layout_form = _layout_form  # type: ignore[assignment]
        took = seen["seconds"]
        if not seed:
            seconds[(name, rows)] = float(took.get("generate_cpu", 0.0))
            calls[(name, rows)] = _layout_calls[0] / rows
        value["shapes"] += 1
        # ...HX4's `reglistmixR` stands for HX4's hold (not on this base) DECLARED as the person
        # column, which publishes its prefix: its validation is recorded apart (P4-D442, limit (q)).
        if rows != LARGE and seen["exits"] != (0, 0, 0) and name not in hunt.SEEDS:
            if name in hunt.RECORDED_APART:
                value["twins_recorded_apart_failing_validation"] += 1
            else:
                value["held_twins_failing_validation"] += 1
        if name in hunt.KEPT_AS_LISTS:
            # ...the list cells the real column holds less the twin's: a held list stays one (rule 22).
            listed = sum(1 for cell in seen["real"] if "," in cell)  # type: ignore[union-attr]
            value["list_cells_written_as_no_list"] += max(
                0, listed - sum(1 for cell in seen["twin"] if "," in cell))  # type: ignore[union-attr]
        value["invalid_date_strings"] += int(seen["invalid_dates"])
        value["uids_off_the_grammar"] += int(seen["off_the_grammar"])
        value["real_persons_merged"] += int(seen["persons_merged"])
        value["real_persons_split"] += int(seen["persons_split"])
        value["e_notation_the_source_never_wrote"] += int(seen["e_notation_the_source_never_wrote"])
        if "persons_in_the_source_layouts" in seen:
            before, inside = seen["persons_in_the_source_layouts"]
            value["persons_merged_in_the_source_layouts"] += max(
                0, before["merged_keys"] - inside["merged_keys"]) + max(0, before["numbers"] - inside["numbers"])
        value["real_keys_in_held_list_cells"] += int(seen["real_keys_in_lists"])
        value["list_cells_carrying_a_real_key"] += int(seen.get("list_cells_carrying", 0))
        if hunt.SHAPES[name][3] == "dates":
            value["real_dates_written_by_chance"] += int(seen["dates_by_chance"])
        if hunt.SHAPES[name][3] == "name":
            value["named_key_twin_cells_real"] += int(seen["equal"])
        lines += [f"{name:32s} {rows:6d} rows{f' (seed {seed})' if seed else ''}: role {seen['role']}, "
                  f"exits {seen['exits']}, "
                  f"profile {took.get('profile', 0):.1f} s, generate {took.get('generate', 0):.1f} s, "
                  f"validate {took.get('validate', 0):.1f} s; equal {seen['equal']}, merging "
                  f"{seen['merged']}, invalid dates {seen['invalid_dates']}, off the UID grammar "
                  f"{seen['off_the_grammar']}, persons merged {seen['persons_merged']} (split "
                  f"{seen['persons_split']}), real keys in lists {seen['real_keys_in_lists']}, e-notation "
                  f"{seen['e_notation_the_source_never_wrote']}, list cells carrying "
                  f"{seen.get('list_cells_carrying', 0)}, persons {seen.get('persons')}"]
        for written in folder.glob("*"):
            if written.is_file():
                written.unlink()
    for slow, blank in hunt.PAIRS.items():
        for rows in (ROWS, LARGE):
            if (slow, rows) not in seconds:
                continue
            ratio = seconds[(slow, rows)] / max(seconds[(blank, rows)], 0.001)
            value["placeholder_time_ratio_most"] = max(value["placeholder_time_ratio_most"], round(ratio, 2))
            called = calls[(slow, rows)] / max(calls[(blank, rows)], 0.001)
            value["placeholder_layout_calls_ratio_most"] = max(
                value["placeholder_layout_calls_ratio_most"], round(called, 2))
            if called > 2:
                value["slow_beside_a_placeholder"] += 1
            lines += [f"{slow} beside {blank} at {rows} rows: generate {seconds[(slow, rows)]:.1f} "
                      f"processor seconds against {seconds[(blank, rows)]:.1f}, ratio {ratio:.2f}; layout_form "
                      f"{calls[(slow, rows)]:.2f} calls a row against {calls[(blank, rows)]:.2f}, ratio {called:.2f}"]
    for kind in held_shapes.HELD + held_shapes.BESIDE + held_shapes.COUNTED:
        folder = pathlib.Path(scratch) / f"k-{kind}"
        folder.mkdir()
        seen = held_shapes.run(folder, kind, ROWS)
        value["shapes"] += 1
        if (seen["profile_exit"], seen["generate_exit"], seen["validate_exit"]) != (0, 0, 0):
            value["held_twins_failing_validation"] += 1
        lines += [f"K-S3-64's {kind:20s} {ROWS} rows: role {seen['role']}, validate "
                  f"{seen['validate_exit']}, {seen['twin_cells']} twin cells real"]
        for written in folder.glob("*"):
            if written.is_file():
                written.unlink()
    # THE ZOO'S HELD COLUMNS AT THE FLOOR (the statistics skeptic's item 2; LANE HB RULINGS 1, item
    # (17)): `tumor_registry.dx_date`, read as record numbers, and `labs.viral_load`, every real cell
    # a number, each through the zoo's own truthful answers.
    import csv
    import health_zoo

    for place, table in enumerate(health_zoo.TABLES):
        if table.name not in ("tumor_registry", "labs"):
            continue
        folder = pathlib.Path(scratch) / f"zoo-{table.name}"
        health_zoo.run_table(table, folder, ROWS, 20261016 + place)
        value["shapes"] += 1
        sources = sorted(path for path in folder.glob(f"{table.name}*{table.suffix}") if "twin" not in path.name)
        with open(folder / f"{table.name}-twin{table.suffix}", encoding="utf-8", newline="") as handle:
            twin_rows = list(csv.reader(handle))
        with open(sources[0], encoding="utf-8", newline="") as handle:
            real_rows = list(csv.reader(handle))
        if table.name == "tumor_registry":
            at = twin_rows[0].index("dx_date")
            cells = [row[at] for row in twin_rows[1:] if row[at].strip()]
            bad = sum(1 for cell in cells if hunt._a_date_shape(cell)
                      and not hunt._is_a_date(cell, ("%Y-%m-%d", "%m/%Y", "%Y")))
            value["invalid_date_strings"] += bad
            lines += [f"zoo tumor_registry.dx_date {ROWS} rows: {bad} of {len(cells)} twin cells no valid date"]
        else:
            # ...each cell read past a censoring `<` or `>` (`<5`, `>1000`), as the zoo's analyst reads it.
            at, real_at = twin_rows[0].index("viral_load"), real_rows[0].index("viral_load")
            real = [row[real_at].lstrip("<>") for row in real_rows[1:] if row[real_at].strip()]
            cells = [row[at].lstrip("<>") for row in twin_rows[1:] if row[at].strip()]
            if real and all(hunt.as_a_number(cell) is not None for cell in real):
                bad = sum(1 for cell in cells if hunt.as_a_number(cell) is None)
                value["non_numbers_in_a_numbers_column"] += bad
                lines += [f"zoo labs.viral_load {ROWS} rows: {bad} of {len(cells)} twin cells no number"]
        for written in folder.rglob("*"):
            if written.is_file():
                written.unlink()
for line in lines:
    print(line)
# kpi_run reads only the KPI line; KPI_HELD_LAYOUTS_LINES names a file the lines are copied to.
if os.environ.get("KPI_HELD_LAYOUTS_LINES"):
    pathlib.Path(os.environ["KPI_HELD_LAYOUTS_LINES"]).write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
kpi_rules.emit("K-HZ-13", value, f"{len(hunt.SHAPES)} hunt shapes at {ROWS} rows (lists at 600), "
               f"{len(hunt.PAIRS)} pairs and the mixed birth dates at {LARGE}, K-S3-64's held shapes and "
               f"the zoo's tumor_registry and labs at {ROWS}")

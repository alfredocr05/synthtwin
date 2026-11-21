"""K-HZ-20: ages in other units and parts of an address under the Safe Harbor rule, per form at 600 and 20,000 rows (plan P4-D454).

Every form of lane SH3's shapes (`tests/age_address_shapes.py`: ages with
their unit in the name, in the cells, with decimals, at death and at an
event on a few rows, with no unit anywhere, a top category of 1 to 10
rows; house, apartment, unit and suite numbers, district and county codes,
two address blocks on one row; and the columns named alike, which are
neither) through the command -- `profile`, every round of the questions
file answered as a truthful person answers or left unanswered, `generate`
at seed 0 -- at 600 rows (the library below the table floor) and at
20,000 rows (the shipped floor). Counted by the shapes' linear counters:
each fact of a column's block read once, each twin cell once.

Keys, per size: values of 90 years or more published in any unit
(`ages_published_*`), twin cells past the mark (`ages_written_*`; of a
column an open question holds, read as its cells are written, its cells
that are real values, its made-up cells past the mark recorded apart as
`held_made_up_past_the_mark_*`: LANE I4m RULINGS 21 (1)), top
categories of 1 to 10 rows -- or people, on the long table of ten rows a
patient -- named in the block or the twin at the table
floor (`top_named_20000_rows`; below it the command refuses the table),
record numbers its values alone read as ages published or written once
answered `yes` (`records_released_*`, lane SH3's repair), real address-part values published, unanswered and
answered (`parts_published_*`), age columns answered truthfully and still
held whole where the top-code serves (`ages_held_whole_*`); the price:
Safe Harbor questions put to the columns named alike (`false_alarm_
questions_*`) and those still held once answered (`false_alarms_held_*`); the questions put to
the ages and parts (`questions_put_*`, at least); and over the health data
zoo's catalogue, its column names that the lane's name rules newly read
as ages in another unit or as parts of an address (`zoo_names_reached`);
and, since lane SH3's second repair, the obligations a twin at the table
floor misses against its own description (`twin_misses_20000_rows`, the
misses `validate` names, summed over every form, unanswered and answered).

    .venv/bin/python tools/measurements/kpi_ages_and_address_parts.py --kpi
"""

import pathlib
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import age_address_shapes as shapes  # noqa: E402
import health_zoo  # noqa: E402
from synthtwin import cli, taxonomy  # noqa: E402

SIZES = (600, 20000)
TABLE_FLOOR = 20000


def _asked(one: "dict[str, object]") -> bool:
    asked = [f"{offered}" for offered in one["open"]] + [f"{given}" for given in one["answers"]]  # type: ignore[attr-defined]
    return any(offered.startswith("no/yes") for offered in asked) or any(
        given.split("=")[-1] in ("yes", "years", "months", "weeks", "days") for given in asked
    )


value: "dict[str, int]" = {"columns_measured": 0}
lines: "list[str]" = []
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    for rows in SIZES:
        for key in ("ages_published", "ages_written", "parts_published_unanswered",
                    "parts_published_answered", "ages_held_whole", "false_alarm_questions",
                    "false_alarms_held", "questions_put", "records_released", "held_made_up_past_the_mark"):
            value[f"{key}_{rows}_rows"] = 0
        # ...every form but the gate's own case at the floor, whose columns
        # are `ages_named`'s; the long table at the table floor alone (below
        # it the command refuses a table of so few people).
        for form in sorted(form for form in shapes.FORMS if form != "units_at_the_floor"
                           and (rows >= TABLE_FLOOR or form != "ages_long_table")):
            for answered in (False, True):
                folder = scratch / f"{form}-{rows}-{answered}"
                started = time.monotonic()
                measured = shapes.measure(cli.main, folder, form, rows, 0, answered)
                seconds = time.monotonic() - started
                shutil.rmtree(folder, ignore_errors=True)
                said: "list[str]" = []
                if rows >= TABLE_FLOOR:
                    missed = measured["(table)"]["misses"]
                    value[f"twin_misses_{rows}_rows"] = value.get(f"twin_misses_{rows}_rows", 0) + len(missed)  # type: ignore[arg-type]
                    said += [f"twin misses {missed}"] if missed else []
                for column in shapes.FORMS[form]:
                    one = measured[column.name]
                    value["columns_measured"] += 1
                    asked = _asked(one)
                    if column.kind == shapes.AGE:
                        value[f"ages_published_{rows}_rows"] += int(one["published_over"])  # type: ignore[call-overload]
                        if shapes.held_as_written(one):
                            # ...a column an open question holds, read as its cells
                            # are written (LANE I4m RULINGS 21 (1)): a cell of it is an
                            # age written only where it is a real value; its made-up
                            # values past the mark are recorded apart.
                            value[f"ages_written_{rows}_rows"] += int(one["twin_real"])  # type: ignore[call-overload]
                            value[f"held_made_up_past_the_mark_{rows}_rows"] += int(one["twin_over"])  # type: ignore[call-overload]
                        else:
                            value[f"ages_written_{rows}_rows"] += int(one["twin_over"])  # type: ignore[call-overload]
                        if rows >= TABLE_FLOOR:
                            # ...pooled at the table floor and above (below it
                            # the command refuses the table).
                            value[f"top_named_{rows}_rows"] = value.get(f"top_named_{rows}_rows", 0) + int(one["few_top_named"])  # type: ignore[call-overload]
                        value[f"ages_held_whole_{rows}_rows"] += int(answered and one["role"] == taxonomy.ROLE_IDENTIFIER)
                        value[f"questions_put_{rows}_rows"] += int(asked)
                        said += [f"{column.name} {one['role']} top {one['top_coded']} published {one['published_over']} "
                                 f"twin {one['twin_over']} few-top {one['few_top_named']} asked {asked}"]
                    elif column.kind == shapes.PERSON:
                        said += [f"{column.name} {one['role']}"]
                    elif column.kind == shapes.RECORD:
                        if answered:
                            value[f"records_released_{rows}_rows"] += int(one["published_real"]) + int(one["twin_real"])  # type: ignore[call-overload]
                        said += [f"{column.name} {one['role']} published {one['published_real']} twin {one['twin_real']}"]
                    elif column.kind == shapes.ADDRESS:
                        key = "parts_published_answered" if answered else "parts_published_unanswered"
                        value[f"{key}_{rows}_rows"] += int(one["published_real"])  # type: ignore[call-overload]
                        value[f"questions_put_{rows}_rows"] += int(asked)
                        said += [f"{column.name} {one['role']} published {one['published_real']} asked {asked}"]
                    else:
                        value[f"false_alarm_questions_{rows}_rows"] += int(asked)
                        value[f"false_alarms_held_{rows}_rows"] += int(answered and one["role"] == taxonomy.ROLE_IDENTIFIER)
                        said += [f"{column.name} {one['role']} asked {asked}"]
                lines += [f"{form} at {rows} rows, {'answered' if answered else 'unanswered'} ({seconds:.1f} s): "
                          + "; ".join(said)]
                print(lines[-1], flush=True)
# ...and the zoo's names the lane's rules newly read: ages in a unit other
# than years, and parts of an address.
reached: "list[str]" = []
for table in health_zoo.catalogue():
    header, _rows = table.build(30, 1)
    for name in header:
        mark = taxonomy.age_mark_named(name)
        if (mark and mark != taxonomy.TOP_CODE) or taxonomy.named_as_an_address_part(name):
            reached += [f"{table.name}.{name}"]
value["zoo_names_reached"] = len(reached)
print(f"zoo names reached: {reached}", flush=True)
kpi_rules.emit("K-HZ-20", value, f"{value['columns_measured']} columns over {len(shapes.FORMS) - 1} forms at 600 and 20,000 rows (the long table at 20,000 alone)")

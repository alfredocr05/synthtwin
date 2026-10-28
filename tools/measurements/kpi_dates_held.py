"""K-HZ-07: real dates one to ten people (or rows, where no person column is) hold, published in a description (plan P4-D433).

Every delimited export of the healthcare catalogue (`tests/health_zoo.py`'s
`runnable_tables`) at 20,000 rows, the owner's table floor, and lane PS2's
sweep (`tests/dates_held.py`: birth dates over seventy years, death dates,
sparse event dates and dense admission days on one row a person, several
rows a person and no person column, and lane E0c's two exposures, the
zoo's `patients.csv` and its `phi_registry.csv`) at 20,000 and 200,000
rows, each through the zoo's own path -- profile, the general answers,
profile --answers -- and counted by `dates_held.dates_held_few`, written
apart from the product's count: every date a description publishes,
counted in people where a person column repeats, else in rows by the day
(month, quarter) it names, with the pooled and held records' spans and
buckets (`few`), and every real date one to ten of them hold printed in
its column's block (`printed`). Target 0 of each, exact; and no table the
counter could not read (`not_counted`). Each sweep shape is profiled
under its own options and counted at its own floor (`dates_held.
options_of`: the user's raised floor, a declared count, `--day-first`).
THE DENSE COLUMNS' BYTES (the orchestrator's ruling 2 on lane PS2's build,
2026-10-25: the gate's 200,000-row cases run here, not in the suite):
each column whose day the floor's rows hold keeps the base's block, its
digest equal to `dates_held.DENSE_DIGESTS` at both sizes
(`dense_moved`, target 0). About forty minutes on the reference machine.

    .venv/bin/python tools/measurements/kpi_dates_held.py --kpi
"""

import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import dates_held  # noqa: E402
import health_zoo  # noqa: E402

ZOO_ROWS = 20000
SWEEP_ROWS = (20000, 200000)
# The catalogue's exports the counter reads: the delimited ones.
DELIMITED = (".csv", ".txt", ".tsv")

value: "dict[str, object]" = {"tables": 0, "not_counted": 0, "dense_moved": 0}
lines: "list[str]" = []


def _measured(battery: str, table: health_zoo.Table, rows: int, scratch: pathlib.Path, shape: str = "") -> str:
    """One table counted into `value`; the line that names what was found."""
    folder = scratch / f"{battery}-{shape or table.name}-{rows}"
    folder.mkdir()
    options, floor = dates_held.options_of(shape) if shape else ((), dates_held.FLOOR)
    few_key = f"{battery}_dates_few_{rows}_rows"
    printed_key = f"{battery}_printed_{rows}_rows"
    value.setdefault(few_key, 0)
    value.setdefault(printed_key, 0)
    try:
        source = dates_held.answered(table, folder, rows, options)
        found = dates_held.dates_held_few(source, folder, floor)
        moved = [column for column in dates_held.DENSE.get(shape, ())
                 if (shape, column, rows) in dates_held.DENSE_DIGESTS
                 and dates_held.dense_digest(folder, shape, column) != dates_held.DENSE_DIGESTS[(shape, column, rows)]]
    except Exception as failure:  # noqa: BLE001 -- every failure is named and judged
        value["not_counted"] = int(value["not_counted"]) + 1  # type: ignore[call-overload]
        return f"{battery} {table.name} at {rows}: not counted ({type(failure).__name__}: {failure})"[:300]
    value["tables"] = int(value["tables"]) + 1  # type: ignore[call-overload]
    value[few_key] = int(value[few_key]) + int(found["few"])  # type: ignore[call-overload]
    value[printed_key] = int(value[printed_key]) + len(found["printed"])  # type: ignore[arg-type, call-overload]
    value["dense_moved"] = int(value["dense_moved"]) + len(moved)  # type: ignore[call-overload]
    return (f"{battery} {shape or table.name} at {rows}: {found['counted_in']}, dates {found['dated']}, few "
            f"{found['few']} {list(found['named'])[:3]}, printed {list(found['printed'])[:3]}"
            f"{', dense moved ' + str(moved) if moved else ''}")  # type: ignore[call-overload]


with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    for table in health_zoo.runnable_tables():
        if table.suffix in DELIMITED:
            lines += [_measured("zoo", table, ZOO_ROWS, scratch)]
    for rows in SWEEP_ROWS:
        for shape in sorted(dates_held.SWEEP):
            lines += [_measured("sweep", dates_held.SWEEP[shape], rows, scratch, shape)]
for line in lines:
    print(line)
kpi_rules.emit("K-HZ-07", value, f"{value['tables']} tables")

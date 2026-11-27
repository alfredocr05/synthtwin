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
(`dense_moved`, target 0). 6,270 s under kpi_run at one-minute load 18
falling to 6, 1,025 s of it the moved cases below, which lane SPD added
(plan P4-D444).

THE GATE'S CASES AT 20,000 ROWS (the orchestrator's rule of 2026-10-26 on
the suite's time; batch 4l OWES 1, lane SPD, plan P4-D444): every case of
`tests/test_dates_held_by_the_floor.py` at 20,000 rows but the one it keeps
runs here too, one item a case (`dates_held_checks.moved_cases`), through
the gate's own checks, on the sweep's 20,000-row tables this driver
already writes: each shape's count, lane E0c's exposures, the dense
columns' bytes, the stamp's time of day, the twins valid in their own
layouts and meeting their description, the day-first registry, ten
patients held in people, the words, no question, the raised floors, the
counts and clocks, month-first under `--day-first`, an older description
and the evidence. It prints one line an item, its verdict, its counts and
seconds (`few` and `printed` where the check counts dates,
`description_values` and `twin_cells` for the ten patients; the other
checks read a block's words, a digest or an exit, so their line says they
count nothing), and the driver exits 1 when any item fails, when the
choice of items selects none, or when any target above is missed; the
value it records is the same as before. Every line it prints
is also written to `synthtwin-kpi/kpi_dates_held-items.txt` under the
system's temporary folder (beside kpi_run's report), since kpi_run keeps
only a driver's KPI line. `--moved-only`
(with `--only PATTERN`) runs the items alone, for a mutant's red, and
writes no KPI line; `--only` without it is refused, so the KPI record is
always the whole run; kpi_run never passes either.

    .venv/bin/python tools/measurements/kpi_dates_held.py --kpi
    .venv/bin/python tools/measurements/kpi_dates_held.py --moved-only --only 'no_date_few:*'
"""

import argparse
import fnmatch
import pathlib
import sys
import tempfile
import time
import traceback

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import dates_held  # noqa: E402
import dates_held_checks  # noqa: E402
import health_zoo  # noqa: E402

ZOO_ROWS = 20000
SWEEP_ROWS = (20000, 200000)
# The catalogue's exports the counter reads: the delimited ones.
DELIMITED = (".csv", ".txt", ".tsv")

value: "dict[str, object]" = {"tables": 0, "not_counted": 0, "dense_moved": 0}
lines: "list[str]" = []
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_dates_held-items.txt"
ITEMS.parent.mkdir(parents=True, exist_ok=True)
ITEMS.write_text("", encoding="utf-8")


def said(line: str) -> None:
    """One line printed, and kept beside kpi_run's report."""
    print(line, flush=True)
    with ITEMS.open("a", encoding="utf-8") as written:
        written.write(line + "\n")


# The sweep's tables at 20,000 rows, each written once: the gate's moved
# cases read them as its fixture did (shape and size to table and folder).
made: "dict[tuple[str, int], tuple[pathlib.Path, pathlib.Path]]" = {}


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
        if shape:
            made[(shape, rows)] = (source, folder)
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


def _moved(scratch: pathlib.Path, only: "list[str]") -> "tuple[int, int]":
    """The gate's moved cases, one item each: how many ran, how many failed."""

    def described(shape: str, rows: int) -> "tuple[pathlib.Path, pathlib.Path]":
        if (shape, rows) not in made:
            folder = scratch / f"described-{shape}-{rows}"
            folder.mkdir()
            options, _floor = dates_held.options_of(shape)
            made[(shape, rows)] = (dates_held.answered(dates_held.SWEEP[shape], folder, rows, options), folder)
        return made[(shape, rows)]

    ran = failed = 0
    for name, node, call in dates_held_checks.moved_cases():
        if only and not any(fnmatch.fnmatch(name, one) for one in only):
            continue
        folder = scratch / f"item-{ran}"
        folder.mkdir()
        started = time.monotonic()
        verdict, why = "PASS", ""
        dates_held_checks.COUNTED.clear()
        try:
            call(described, folder)
        except AssertionError as failure:
            verdict, why = "FAIL", f"{failure}" or traceback.format_exc(limit=-1).strip()
        except Exception as failure:  # noqa: BLE001 -- every failure is named and judged
            verdict, why = "FAIL", f"{type(failure).__name__}: {failure}"
        ran += 1
        failed += verdict == "FAIL"
        said(f"moved {name} ({node}): {verdict} {dates_held_checks.counted_words()} {time.monotonic() - started:.1f} s"
             + (f" -- {why[:600]}" if why else ""))
    return ran, failed


chosen = argparse.ArgumentParser(description="K-HZ-07 and the gate's moved cases at 20,000 rows")
chosen.add_argument("--kpi", action="store_true", help="print the KPI line (kpi_run passes it)")
chosen.add_argument("--moved-only", action="store_true", help="run the gate's moved cases alone")
chosen.add_argument("--only", action="append", default=[], help="the moved items whose name matches (repeatable)")
arguments = chosen.parse_args()
if arguments.only and not arguments.moved_only:
    chosen.error("--only runs some of the moved cases, so it needs --moved-only, which writes no KPI line")
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    if not arguments.moved_only:
        for table in health_zoo.runnable_tables():
            if table.suffix in DELIMITED:
                lines += [_measured("zoo", table, ZOO_ROWS, scratch)]
        for shape in sorted(dates_held.SWEEP):
            lines += [_measured("sweep", dates_held.SWEEP[shape], dates_held_checks.ROWS, scratch, shape)]
    ran, failed = _moved(scratch, arguments.only)
    if not arguments.moved_only:
        for rows in SWEEP_ROWS:
            if rows != dates_held_checks.ROWS:
                for shape in sorted(dates_held.SWEEP):
                    lines += [_measured("sweep", dates_held.SWEEP[shape], rows, scratch, shape)]
for line in lines:
    said(line)
said(f"the gate's moved cases at {dates_held_checks.ROWS:,} rows: {ran} run, {failed} failing")
missed = [key for key, number in value.items() if key != "tables" and number]
if not arguments.moved_only:
    kpi_rules.emit("K-HZ-07", value, f"{value['tables']} tables")
if not ran:
    said(f"no moved case matches {arguments.only}: nothing was measured")
sys.exit(1 if failed or missed or not ran else 0)

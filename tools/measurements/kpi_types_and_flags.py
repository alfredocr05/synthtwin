"""K-HZ-17: types, codes and flags, eight invented forms (lane CZ-D, plan P4-D447).

Runs the eight invented forms of `tests/types_flags_zoo.py` -- whole-number
category codes, dense Y/N flags, a wide mart of 180 columns with 70
1-or-blank indicators, near-empty measures beside full columns, frequency
and route words with an as-needed flag, a Windows-1252 file of units, a
table of 60 columns of every role, and codes and flags with a level 1 to
10 people hold on 11 rows or more -- each through `health_zoo.run_table`
the way the zoo runs its catalogue (profile, the general answers round by
round, generate, validate, the analyst's script on both files): at 600
rows BELOW THE OWNER'S TABLE FLOOR with the command's internal switch
off, then at 20,000 rows with the SHIPPED floor on. It prints K-HZ-17
`types_and_flags`, per size: the forms whose run fails a step, the
columns whose twin pandas reads with another dtype, the spellings off (a
code written 3.0, an indicator 1.0, a flag spelled another way, a stamp
off its midnight or whole minute, mojibake or a file rewritten as UTF-8),
the Y/N/blank and empty shares and the ==, isin and str.contains filter
shares more than SHARE_TOLERANCE from the source's, every level 11 or
more people hold of a code column read the same way, the text cells
written in a column of numbers, the group-N stand-ins, the validate
misses, the values of person and record columns published (HIPAA first),
the levels 1 to 10 people hold published in any column's block and the
values of a rare indicator or a near-empty measure published, the present
counts of a column 1 to 10 people fill published (directly or as the rows
less its missing cells), the made-up codes past the description's held
rows or off the column's form and a code's cells on levels 1 to 10 people
hold past those rows, the checks that fail on the source, the faults that
name no column, any other fault, and, recorded apart, the made-up codes
held-back levels are written as (the floor's price) and the twin cells
equal to a source level 1 to 10 people hold; the seconds of each form at
20,000 rows, the wide mart's among them (K-HZ-03's shard bound is 900 s),
and each form's failing columns.

Every count is linear in the cells. Each form is written into a folder of
its own under a temporary folder, removed when the form is done.

    .venv/bin/python tools/measurements/kpi_types_and_flags.py --kpi
"""

import pathlib
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402
import types_flags_zoo  # noqa: E402

kpi_rules.guard_this_tree()

SIZES = (health_zoo.SMOKE_ROWS, health_zoo.KPI_ROWS)
COUNTED = types_flags_zoo.COUNTS


def _timed(spent: "dict[str, float]") -> object:
    """`health_zoo._quietly`, timing each command it runs by the command's name."""
    quietly = health_zoo._quietly

    def run(arguments: "list[str]", small_tables_refused: bool = False) -> "tuple[int, str]":
        started = time.perf_counter()
        try:
            return quietly(arguments, small_tables_refused)
        finally:
            step = "answers" if "--answers" in arguments else arguments[0]
            spent[step] = spent.get(step, 0.0) + time.perf_counter() - started

    return run


def main() -> None:
    value: "dict[str, object]" = {}
    named: "list[str]" = []
    quietly = health_zoo._quietly
    with tempfile.TemporaryDirectory(prefix="synthtwin-types-and-flags-") as scratch:
        root = pathlib.Path(scratch)
        for rows in SIZES:
            totals = {key: 0 for key in COUNTED}
            for table in types_flags_zoo.tables():
                folder = root / f"{table.name}-{rows}"
                spent: "dict[str, float]" = {}
                health_zoo._quietly = _timed(spent)  # type: ignore[assignment]
                started = time.perf_counter()
                try:
                    result = health_zoo.run_table(
                        table, folder, rows, types_flags_zoo.seed_of(table), small_tables_refused=rows >= health_zoo.KPI_ROWS,
                    )
                finally:
                    health_zoo._quietly = quietly  # type: ignore[assignment]
                seconds = time.perf_counter() - started
                found = types_flags_zoo.form_measures(table, result, folder)
                for key in COUNTED:
                    totals[key] = totals[key] + int(found[key])  # type: ignore[call-overload]
                failing = list(found["failing_columns"])  # type: ignore[call-overload]
                if rows == health_zoo.KPI_ROWS:
                    value[f"seconds_20000_rows_{table.name}"] = round(seconds, 1)
                said = {key: found[key] for key in COUNTED if found[key]}
                named += [
                    f"{table.name}@{rows}: {said or 'clean'}"
                    + (f" failing {failing}" if failing else "")
                    + " seconds " + ", ".join(f"{step} {round(took, 1)}" for step, took in spent.items())
                ]
                shutil.rmtree(folder, ignore_errors=True)
            for key in COUNTED:
                value[f"{key}_{rows}_rows"] = totals[key]
    kpi_rules.emit("K-HZ-17", value, "; ".join(named))

if __name__ == "__main__":
    main()

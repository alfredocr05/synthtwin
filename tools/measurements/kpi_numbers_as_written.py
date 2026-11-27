"""K-HZ-28: the zoo's numbers beside a label's bound written differently from their source, at the table floor (lane LM1, plan P4-D475).

The health data zoo's two columns of numbers beside a label that names a
bound -- `bedside_results`' result field `hiv_rna` (`TND`, `<20` and
loads of 20 or more) and `safe_harbor`'s `age_top` (ages beside the
top-code label `90+`) -- are each run end to end at 20,000 rows as a
person runs them (`tests/health_zoo.py`'s run_table: profile with the
owner's table floor on, the answers rounds, generate at seed 0,
validate). A twin cell that holds a figure is WRITTEN DIFFERENTLY where
its form -- every figure a `9`, every capital an `A`, every other letter
an `a`, every other character as written (`health_zoo.form`) -- is no
form a cell of the real column wears (`3` beside loads of 20 or more),
or where it is a number on the far side of the label's bound
(`health_zoo.numbers_written_differently`; repair 1 of lane LM1:
skeptic 1's item 9, the statistics check's item 3): `hiv_rna` a number
under 20 (a twin `12` wears the form of a real `40`), `age_top` a number
of 90 or more (a twin `91` wears the form of a real `89`); a cell
counted either way is counted once. The count is LINEAR in the cells:
the real forms in a set, each twin cell's form and number read once.
Target 0.

The exponent form and census of a column of magnitudes lane LM1 built
were withdrawn (LANE LM1 RULINGS 5), and a count written in exponent
style (`wbc_count`) is plan P4-D475's limit (a), owner lane LM2: neither
is a column of this KPI.

It prints the count over the two columns, the columns measured and those
written as their source wrote them, each column's count in the detail,
and the seconds each run took apart from the counting. Each table is
written into a temporary folder that is removed at the end.

    .venv/bin/python tools/measurements/kpi_numbers_as_written.py --kpi
"""

import csv
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

# The exports and their columns beside a label that names a bound.
COLUMNS = (
    ("bedside_results", ("hiv_rna",)),
    ("safe_harbor", ("age_top",)),
)

# Each column's bound: the lowest number the label leaves the numbers
# (`<20`), or the number they stay below (`90+`).
BOUNDS: "dict[str, tuple[str, float]]" = {
    "hiv_rna": ("at least", 20.0),
    "age_top": ("below", 90.0),
}


def _cells(path: pathlib.Path, column: str) -> "list[str]":
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        header = next(reader)
        place = header.index(column)
        return [row[place] for row in reader if len(row) > place]


def main() -> None:
    total = 0
    clean = 0
    measured = 0
    named: "list[str]" = []
    spent: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-numbers-as-written-") as scratch:
        root = pathlib.Path(scratch)
        for name, columns in COLUMNS:
            table = health_zoo.table_named(name)
            folder = root / name
            started = time.perf_counter()
            result = health_zoo.run_table(
                table, folder, health_zoo.KPI_ROWS, health_zoo.seed_of(table), small_tables_refused=True
            )
            spent += [f"{name} {round(time.perf_counter() - started, 1)}"]
            twin = folder / f"{name}-twin{table.suffix}"
            if not twin.is_file():
                twin = folder / f"{name}-twin.csv"
            for column in columns:
                measured = measured + 1
                if not twin.is_file():
                    named += [f"{name}.{column}: no twin ({result['steps']})"]
                    total = total + health_zoo.KPI_ROWS
                    continue
                found = health_zoo.numbers_written_differently(
                    _cells(folder / f"{name}{table.suffix}", column), _cells(twin, column), BOUNDS[column]
                )
                total = total + found
                clean = clean + (1 if found == 0 else 0)
                named += [f"{name}.{column} {found}"]
    value: "dict[str, object]" = {
        "cells_written_differently": total,
        "columns_measured": measured,
        "columns_as_written": clean,
    }
    kpi_rules.emit("K-HZ-28", value, "; ".join(named) + "; seconds (counting included) " + ", ".join(spent))


if __name__ == "__main__":
    main()

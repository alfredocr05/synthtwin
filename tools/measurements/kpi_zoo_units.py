"""K-HZ-08 and K-HZ-09: the zoo's unit and decimal-comma columns at 20,000 rows (plan P4-D438).

The zoo-fix track's nine columns that hold a number beside a unit or a
decimal comma (wave6 ZOO/PLAN.md section 2.1, lanes UN-1a and UN-1b):
vitals' `temp` (`36,9 °C`), `spo2` (`98%`), `stature` (`172 cm`),
`weight` (`72,5 kg`) and `mass_index` (`25,5`); labs' `result`
(`5.4 mmol/L` beside four other units); the US vitals' `temp_f`
(`98.4 F`) and `weight` (`172 lb`); and an eGFR (`56 mL/min/1.73m2`
beside `>60 mL/min/1.73m2`), which `tests/health_zoo.py` does not hold,
so this driver writes it as a table of its own, built and run the way
the zoo builds and runs its tables.

Each table runs through `tests/health_zoo.py`'s `run_table` at 20,000
rows -- profiled, answered with the zoo's general facts, generated at
seed 0, validated -- and two counts are printed:

- K-HZ-08: how many of the nine columns the answered description reads
  as numbers (`affixed_number`, `continuous` or `count`), a column whose
  every level clears the floor counted as read where rule 7 keeps its
  exact list (`categorical`, no level held back: an exact twin; P4-D419's
  ZR.7);
- K-HZ-09: the twin's bad cells on the nine columns, counted in ONE
  pass over each twin column against the real column's own forms: a
  cell is bad where it is blank and the real column holds no blank,
  where it is not a number (a point or a comma for its decimals) behind
  an optional `<` or `>` and before a text, where that pair of texts
  never stands in the real column, or where its number lies outside the
  real numbers of that pair widened by a tenth of their span on each
  side (the zoo's own range tolerance).

Each table is written into a folder of its own under a temporary folder
that is removed at the end.

    python tools/measurements/kpi_zoo_units.py --kpi [--rows N] [--seed S]
"""

import argparse
import json
import pathlib
import random
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

ROWS = 20_000
# The zoo's own seed for its battery (`run_zoo`), each table at its place.
SEED = 20261016
NUMERIC_READINGS = ("affixed_number", "continuous", "count")
# One number in a cell: an optional `<` or `>`, a sign, figures, and a
# point or a comma before its decimals; what stands before and after it
# is the pair of texts it wears.
CELL = re.compile(r"^(?P<before>[<>]?)(?P<number>-?\d+(?:[.,]\d+)?)(?P<after>.*)$", re.DOTALL)
# (table, column) in the order the plan names them.
COLUMNS = (
    ("vitals", "temp"),
    ("vitals", "spo2"),
    ("vitals", "stature"),
    ("vitals", "weight"),
    ("vitals", "mass_index"),
    ("labs", "result"),
    ("us_vitals", "temp_f"),
    ("us_vitals", "weight"),
    ("egfr_labs", "egfr"),
)
NAMES = {
    ("vitals", "temp"): "temp",
    ("vitals", "spo2"): "spo2",
    ("vitals", "stature"): "stature",
    ("vitals", "weight"): "weight",
    ("vitals", "mass_index"): "mass_index",
    ("labs", "result"): "labs_result",
    ("us_vitals", "temp_f"): "temp_f",
    ("us_vitals", "weight"): "weight_lb",
    ("egfr_labs", "egfr"): "egfr",
}


def egfr_labs(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """An eGFR as a laboratory exports it: `56 mL/min/1.73m2`, and `>60 mL/min/1.73m2` above 60."""
    draw = random.Random(seed)
    header = ["patient_id", "egfr"]
    rows: "list[list[str]]" = []
    for _index in range(n):
        value = round(draw.gauss(52.0, 18.0))
        cell = ">60 mL/min/1.73m2" if value > 60 else f"{max(value, 5)} mL/min/1.73m2"
        rows += [[f"PT{1000000 + draw.randrange(max(n // 3, 1)):07d}", cell]]
    return header, rows


EGFR = health_zoo.Table(
    "egfr_labs", ".csv", egfr_labs,
    lambda header, rows: health_zoo.csv_bytes(header, rows),
    {"egfr_labs": ("patient_id", "egfr")},
    {"patient_id": "identifier", "egfr": "measurement"},
    health_zoo._csv_reader(),
    (),
)


def _table(name: str) -> "health_zoo.Table":
    return EGFR if name == EGFR.name else health_zoo.table_named(name)


def _seed_of(name: str, seed: int) -> int:
    """The seed the zoo's battery gives the table (its place), or the next for the eGFR."""
    tables = health_zoo.TABLES
    for place in range(len(tables)):
        if tables[place].name == name:
            return seed + place
    return seed + len(tables)


def _number(text: str) -> float:
    return float(text.replace(",", "."))


def _cells(table: "health_zoo.Table", path: pathlib.Path, column: str) -> "list[str]":
    frames = table.read(path)
    raw = frames["raw"]
    return [f"{cell}" for cell in raw[column].tolist()]  # type: ignore[index]


def bad_cells(real: "list[str]", twin: "list[str]") -> int:
    """The twin's cells off the real column's forms, numbers and blanks: one pass over each."""
    ranges: "dict[tuple[str, str], list[float]]" = {}
    real_blank = False
    for cell in real:
        if cell.strip() == "":
            real_blank = True
            continue
        found = CELL.match(cell)
        if found is None:
            continue
        key = (found["before"], found["after"])
        number = _number(found["number"])
        if key in ranges:
            span = ranges[key]
            span[0] = min(span[0], number)
            span[1] = max(span[1], number)
        else:
            ranges[key] = [number, number]
    bad = 0
    for cell in twin:
        if cell.strip() == "":
            bad += 0 if real_blank else 1
            continue
        found = CELL.match(cell)
        if found is None or (found["before"], found["after"]) not in ranges:
            bad += 1
            continue
        low, high = ranges[(found["before"], found["after"])]
        slack = (high - low) * 0.1
        number = _number(found["number"])
        if number < low - slack or number > high + slack:
            bad += 1
    return bad


def measure(rows: int, seed: int, folder: pathlib.Path) -> "dict[str, dict[str, object]]":
    """Each of the nine columns: its role in the answered description and its twin's bad cells."""
    found: "dict[str, dict[str, object]]" = {}
    done: "dict[str, dict]" = {}
    for table_name, column in COLUMNS:
        table = _table(table_name)
        if table_name not in done:
            done[table_name] = health_zoo.run_table(table, folder / table_name, rows, _seed_of(table_name, seed))
        result = done[table_name]
        roles = result.get("roles", {})
        source = folder / table_name / f"{table_name}{table.suffix}"
        twin = folder / table_name / f"{table_name}-twin{table.suffix}"
        bad: "int | None" = None
        if _completed(result) and twin.is_file():
            bad = bad_cells(_cells(table, source, column), _cells(table, twin, column))
        found[NAMES[(table_name, column)]] = {
            "role": roles.get(column, "not described"),
            "exact_list": _exact_list(folder / table_name / f"{table_name}-profile.json", column),
            "bad_cells": bad,
        }
    return found


def _completed(result: "dict[str, object]") -> bool:
    """Whether the steps a twin is made by exited 0: profile, the answers where run, generate.

    A twin left behind by a step that failed is no measurement (Codex's
    review of lane UN-1a, item 6): its column is counted as not measured.
    """
    steps = result.get("steps", {})
    if not isinstance(steps, dict):
        return False
    for name in ("profile", "answers", "generate"):
        step = steps.get(name)
        if step is None and name == "answers":
            continue
        if not isinstance(step, dict) or step.get("exit") != 0:
            return False
    return True


def missing_twins(found: "dict[str, dict[str, object]]") -> "list[str]":
    """The columns whose twin was not measured: their bad cells are None.

    A total over fewer than the nine columns is no comparable K-HZ-09
    (Codex's review of lane UN-1a, item 6: labs' generation failing
    returned normally, and its 578 bad cells left the total 2,176 ->
    1,598 with K-HZ-08 unchanged), so `main` refuses to emit one.
    """
    return sorted(name for name, one in found.items() if not isinstance(one["bad_cells"], int))


def _exact_list(profile: pathlib.Path, column: str) -> bool:
    """Whether the answered description keeps the column's exact list: `categorical`, no level held back."""
    try:
        document = json.loads(profile.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return False
    for block in document.get("columns", []):
        if block.get("name") == column:
            return block.get("role") == "categorical" and not block.get("suppressed_levels")
    return False


def _read(one: "dict[str, object]") -> bool:
    return one["role"] in NUMERIC_READINGS or bool(one["exact_list"])


def main() -> None:
    # Asked first, inside `main` so a test may import the helpers above.
    kpi_rules.guard_this_tree()
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--seed", type=int, default=SEED)
    options = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="synthtwin-zoo-units-") as folder:
        found = measure(options.rows, options.seed, pathlib.Path(folder))
    missing = missing_twins(found)
    if missing:
        raise SystemExit(
            f"K-HZ-09 not measured: no completed twin for {', '.join(missing)}; "
            f"a total over fewer than the {len(found)} columns is not emitted"
        )
    read = sorted(name for name, one in found.items() if _read(one))
    unread = sorted(name for name in found if name not in read)
    bad = {name: one["bad_cells"] for name, one in found.items()}
    total = sum(int(count) for count in bad.values() if isinstance(count, int))
    roles = "; ".join(
        f"{name} {one['role']}" + (" (its exact list)" if one["exact_list"] else "") for name, one in found.items()
    )
    kpi_rules.emit(
        "K-HZ-08",
        {"columns_read_as_numbers": len(read), "columns": len(found), "read_named": ", ".join(read) or "none"},
        f"{len(read)} of {len(found)} at {options.rows:,} rows; not read as numbers: {', '.join(unread) or 'none'}; {roles}",
    )
    kpi_rules.emit(
        "K-HZ-09",
        {"bad_cells": total, **{f"bad_cells_{name}": count for name, count in bad.items()}},
        f"{total} bad twin cells over the nine columns at {options.rows:,} rows",
    )


if __name__ == "__main__":
    main()

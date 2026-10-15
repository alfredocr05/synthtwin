"""K-S3-48: clock-only columns keep their time of day (landing 3b.5).

PLAN P4-D373. The fourteen columns of `tests/clock_census_shapes.py`'s
battery read as clock times -- a clinic's slots, walk-ins on a ten-minute
grid, a medication round, a handover heaped at 07:00 and 19:00, shift
starts, emergency triage at the second, night observations across
midnight, lab draws, five rounds, shift starts beside `UNK`, Excel's
one-figure hour, the 12-hour clock with a marker, a five-minute grid and
a dominant time with no tails -- in one table, at 1,000 rows (seeds 0 to
4, floors 11 and 36) and 10,000 rows (seed 0, floor 11), through the real
producer, generator and checker:

* `columns`: how many of the fourteen were read as clock times at every
  size;
* `hour_tvd_1k` and `hour_tvd_10k`: the largest total variation between
  the twin's hour of day and the real one, over the 24 hours, at the
  floor of eleven;
* `heaps_off`: published heaps whose twin count is not the real count;
* `cells_unreadable`: twin cells no clock reader takes, blanks among
  them, beyond the real column's own such cells;
* `missed`: twins, and real tables, of which validation MISSES anything;
* since landing 3b.5's second step (plan P4-D374), `minute_censuses`: the
  minute censuses the tables publish over every size and floor (13: five
  at 1,000 rows at each floor, three at 10,000); `slots_gap_1k`: the
  largest gap, over the columns publishing one at 1,000 rows and the floor
  of eleven, between the twin's share on `:00` or `:30` and the real one;
  and `ten_tvd_1k`, the design's stated cost: the largest total variation
  over the 144 ten-minute stretches between twin and table on those
  columns, beside a noise floor near 0.13 at 1,000 rows.

Before the landing (110cb46, the battery of the design and its skeptic):
clinic, shift starts, rounds and the coded shifts took `categorical` at
1,000 rows, writing 42 to 107 blank cells each; the hour came back 0.18
(med_round), 0.32 (handover) and 0.33 (night_obs) off; handover's heaps
came back 186 of 680 rows; and the dominant time with no tails was a
ramp from 00:00, its hour 1.0 off at 100 rows.

    .venv/bin/python tools/measurements/kpi_clock.py --kpi
"""

import collections
import csv
import io
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import clock_census_shapes as shapes  # noqa: E402
import fixtures  # noqa: E402
import kpi_rules  # noqa: E402

from synthtwin import contract, generation, parsing, profile, reading  # noqa: E402
from synthtwin import rendering, taxonomy, validation  # noqa: E402

RUNS = ((1000, 11, (0, 1, 2, 3, 4)), (1000, 36, (0, 1, 2, 3, 4)), (10000, 11, (0,)))


def _second(text: str) -> "int | None":
    parts = parsing.clock_parts(text)
    if parts is None:
        return None
    return parsing.clock_second(parts, parts[5])


def _tvd(real: "list[str]", twin: "list[str]") -> float:
    def hours(cells: "list[str]") -> "collections.Counter[int]":
        return collections.Counter(
            second // 3600 for second in (_second(cell) for cell in cells) if second is not None
        )

    first, second = hours(real), hours(twin)
    a, b = max(1, sum(first.values())), max(1, sum(second.values()))
    return 0.5 * sum(abs(first[hour] / a - second[hour] / b) for hour in range(24))


def _tvd_ten(real: "list[str]", twin: "list[str]") -> float:
    def stretches(cells: "list[str]") -> "collections.Counter[int]":
        return collections.Counter(
            second // 600 for second in (_second(cell) for cell in cells) if second is not None
        )

    first, second = stretches(real), stretches(twin)
    a, b = max(1, sum(first.values())), max(1, sum(second.values()))
    return 0.5 * sum(abs(first[bin] / a - second[bin] / b) for bin in range(144))


def _on_the_slots(cells: "list[str]") -> float:
    read = [second for second in (_second(cell) for cell in cells) if second is not None]
    return sum(1 for second in read if (second // 60) % 60 in (0, 30)) / max(1, len(read))


def _missed(loaded: contract.Profile, path: pathlib.Path) -> int:
    outcome = validation.measure(loaded, str(path))
    return sum(1 for check in outcome.checks if check.verdict == validation.MISSED)


def _unreadable(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells no clock reader takes, blanks among them, beyond the real column's."""
    def counted(cells: "list[str]") -> int:
        return sum(1 for cell in cells if cell == "" or _second(cell) is None)

    return max(0, counted(twin) - counted(real))


def measure(home: pathlib.Path) -> "tuple[dict[str, object], list[str]]":
    """Every size, floor and seed; the totals and what failed."""
    names = shapes.CLOCKS
    totals: "dict[str, object]" = {
        "columns": 0, "hour_tvd_1k": 0.0, "hour_tvd_10k": 0.0,
        "heaps_off": 0, "cells_unreadable": 0, "missed": 0,
        "minute_censuses": 0, "slots_gap_1k": 0.0, "ten_tvd_1k": 0.0,
    }
    notes: "list[str]" = []
    read = {name: True for name in names}
    for rows, floor, seeds in RUNS:
        folder = home / f"{rows}-{floor}"
        folder.mkdir()
        columns = {name: shapes.cells(name, rows) for name in names}
        lines = [",".join(names)] + [
            ",".join(columns[name][index] for name in names) for index in range(rows)
        ]
        table = fixtures.write(folder, "clocks.csv", "\n".join(lines) + "\n")
        document = profile.build_document(
            reading.read_table(str(table), small_cell_floor=floor),
            taxonomy.Settings(small_cell_floor=floor),
            [],
        )
        blocks = {block["name"]: block for block in document["columns"]}
        loaded = contract.load_profile(str(fixtures.write_profile(folder, "clocks.json", document)))
        if _missed(loaded, table):
            totals["missed"] = int(totals["missed"]) + 1  # type: ignore[call-overload]
            notes += [f"the real table at {rows} rows, floor {floor}: MISSED"]
        minutes = [name for name in names if blocks[name].get("minute_census")]
        totals["minute_censuses"] = int(totals["minute_censuses"]) + len(minutes)  # type: ignore[call-overload]
        for name in names:
            if blocks[name]["role"] != taxonomy.ROLE_CLOCK:
                read[name] = False
                notes += [f"{name} at {rows} rows, floor {floor}: read as {blocks[name]['role']}"]
        for seed in seeds:
            text = rendering.twin_csv(generation.generate(loaded, seed))
            target = fixtures.write(folder, f"twin-{seed}.csv", text)
            if _missed(loaded, target):
                totals["missed"] = int(totals["missed"]) + 1  # type: ignore[call-overload]
                notes += [f"twin at {rows} rows, floor {floor}, seed {seed}: MISSED"]
            body = list(csv.reader(io.StringIO(text)))
            for place, name in enumerate(body[0]):
                twin = [row[place] for row in body[1:] if row]
                real = columns[name]
                if floor == 11:
                    key = "hour_tvd_1k" if rows == 1000 else "hour_tvd_10k"
                    totals[key] = round(max(float(totals[key]), _tvd(real, twin)), 4)  # type: ignore[arg-type]
                if floor == 11 and rows == 1000 and name in minutes:
                    gap = abs(_on_the_slots(twin) - _on_the_slots(real))
                    totals["slots_gap_1k"] = round(max(float(totals["slots_gap_1k"]), gap), 4)  # type: ignore[arg-type]
                    ten = _tvd_ten(real, twin)
                    totals["ten_tvd_1k"] = round(max(float(totals["ten_tvd_1k"]), ten), 4)  # type: ignore[arg-type]
                counted = collections.Counter(twin)
                for heap in blocks[name]["clock_heaps"]:
                    if counted[heap["value"]] != heap["count"]:
                        totals["heaps_off"] = int(totals["heaps_off"]) + 1  # type: ignore[call-overload]
                        notes += [f"{name} at {rows}, floor {floor}, seed {seed}: a heap off"]
                bad = _unreadable(real, twin)
                totals["cells_unreadable"] = int(totals["cells_unreadable"]) + bad  # type: ignore[call-overload]
    totals["columns"] = sum(1 for name in names if read[name])
    return totals, notes


def main() -> int:
    with tempfile.TemporaryDirectory() as folder:
        totals, notes = measure(pathlib.Path(folder))
    kpi_rules.emit(
        "K-S3-48", totals, "; ".join(notes) if notes else "every column read, laid and checked"
    )
    return 0


if __name__ == "__main__":
    if "--kpi" not in sys.argv[1:]:
        print(__doc__)
    sys.exit(main())

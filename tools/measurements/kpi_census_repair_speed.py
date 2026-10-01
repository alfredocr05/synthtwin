"""K-S2-06: the census-of-marks repair of stage 2 grows linearly.

The pinned test (`tests/test_stage2_datetime_oracle.py`) keeps a 10 s
budget at 40,000 cells. Its speed at 40,000 and 80,000 cells was 0.61 s
and 1.27 s, and a ratio of two numbers under a second can be pushed past
any bound by the scheduler alone. So this takes the pinned test's own
shape at 80,000 and 320,000 cells -- four times the cells, the small
size over a second -- with a median of three at each, and prints the
ratio, which is machine-free. About half a minute.

    .venv/bin/python tools/measurements/kpi_census_repair_speed.py --kpi
"""

import pathlib
import statistics
import sys
import time
import types
import typing

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
from synthtwin import contract, generation  # noqa: E402

kpi_rules.guard_this_tree()


def repair_seconds(parsed):
    column = typing.cast(contract.ColumnBlock, types.SimpleNamespace(name="c"))
    wanted = [" " if rank % 4 else "T" for rank in range(parsed)]
    days = [19000 + (rank * 29) // parsed for rank in range(parsed)]
    cells = [
        generation._cell_of_ordinal(day * 86400, "datetime", "second", 0, wanted[rank])
        for rank, day in enumerate(days)
    ]
    holes = (generation._cell_of_ordinal(19014 * 86400, "datetime", "second", 0, " "),)
    named = ("space", "upper_t")
    started = time.perf_counter()
    kept = [generation._kept_datetime_cell(cell, holes, named) for cell in cells]
    fixed, _notes = generation._rebalanced_marks(column, wanted, kept, holes)
    spent = time.perf_counter() - started
    assert sorted(cell[10] for cell in fixed) == sorted(wanted)
    return spent


small = statistics.median(repair_seconds(80_000) for _ in range(3))
large = statistics.median(repair_seconds(320_000) for _ in range(3))
print(f"80,000 cells {small:.2f} s, 320,000 cells {large:.2f} s", flush=True)
kpi_rules.emit("K-S2-06", {"ratio_4x_cells": round(large / small, 2),
                           "seconds_80k": round(small, 2), "seconds_320k": round(large, 2)})

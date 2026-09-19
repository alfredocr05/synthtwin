"""K-2B-14: generating second-precision date-time columns, counted and timed.

The stage-2b regression: `generation._nearest_held_unit` walks outward
from an instant ONE UNIT AT A TIME, so a second-precision column spends time
for every second between an instant and the nearest one a rank holds.
Its cost follows the data, not the row count (1,000 rows 10.5 s, 4,000
rows 1.4 s on the same machine), so seconds alone flap. This counts
the WORK instead, which is machine-free: every call of the walk and the
units it stepped (the distance from the instant to the one it returned,
or to the far bound when it returned nothing), summed over one run.

Two shapes: `_partly(2000, 0.7, 2)` of tests/test_stage2_timestamp_spellings.py
at seed 4, and the 2,000-row extract of tests/test_workbook_dates.py
written as delimited text. The ledger holds the steps as the entry's
must-not-get-worse bound and its target as seconds under 2 on the
reference machine. About a minute before the repair.

    .venv/bin/python tools/measurements/kpi_datetime_speed.py --kpi
"""

import io
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
from synthtwin import generation  # noqa: E402

kpi_rules.guard_this_tree()
import test_stage2_timestamp_spellings as spellings  # noqa: E402
import test_workbook_dates as dates  # noqa: E402

walked = {"calls": 0, "steps": 0}
original = generation._nearest_held_unit


def counted(facts, value, lowest, highest, day, step, unit, *rest, **named):
    found = original(facts, value, lowest, highest, day, step, unit, *rest, **named)
    walked["calls"] += 1
    if found is None:
        walked["steps"] += max(value - lowest, highest - value) // unit + 1
    else:
        walked["steps"] += abs(found // unit - value // unit)
    return found


generation._nearest_held_unit = counted


def run(described):
    walked.update(calls=0, steps=0)
    started = time.perf_counter()
    generation.generate(described.loaded, 4)
    return dict(walked), time.perf_counter() - started


def extract_text(rows):
    import openpyxl

    sheet = openpyxl.load_workbook(io.BytesIO(dates._extract(rows, 9))).worksheets[0]
    lines = ["service_date,paid_at,amount"]
    for day, moment, amount in sheet.iter_rows(min_row=2, values_only=True):
        lines += [f"{day:%Y-%m-%d},{moment:%Y-%m-%d %H:%M:%S},{amount}"]
    return "\n".join(lines) + "\n"


value = {}
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    partly = kpi_shapes.describe(
        home / "partly", "stamps", "stamp\n" + "\n".join(spellings._partly(2000, 0.7, 2)) + "\n"
    )
    work, seconds = run(partly)
    print("partly 2000:", work, f"{seconds:.1f} s", flush=True)
    value.update(steps_partly_2000=work["steps"], calls_partly_2000=work["calls"],
                 seconds_partly_2000=round(seconds, 2))
    extract = kpi_shapes.describe(home / "extract", "extract", extract_text(2000))
    work, seconds = run(extract)
    print("extract 2000:", work, f"{seconds:.1f} s", flush=True)
    value.update(steps_extract_2000=work["steps"], calls_extract_2000=work["calls"],
                 seconds_extract_2000=round(seconds, 2))
kpi_rules.emit("K-2B-14", value)

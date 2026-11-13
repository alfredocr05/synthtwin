"""K-2B-14: generating second-precision date-time columns, counted and timed.

The stage-2b regression: `generation._nearest_held_unit` walked outward
from an instant ONE UNIT AT A TIME, so a second-precision column spent
time for every second between an instant and the nearest one a rank
holds (190,524,866 questions of the held-unit table on `_partly(2000,
0.7)`, about a minute). The g-speed repair (plan K-2B-14, merged
2026-09-19) sorts the held units once and searches them, so the same
column asks 2,444. Seconds alone flap with the machine's load; this
counts the WORK instead, which is machine-free: every call of the two
searches, `_nearest_held_unit` and `_nearest_free_unit`, and every
question each asks of the held-unit table (positional argument 7,
wrapped in a counting dict for the call), summed over one run.

The distance walked -- units between an instant and the one returned,
or the far bound where none was -- is printed beside it as context: it
is the ANSWER's distance, the same before and after the repair, and it
is what the first version of this driver counted.

Two shapes: `_partly(2000, 0.7, 2)` of tests/test_stage2_timestamp_spellings.py
at seed 4, and the 2,000-row extract of tests/test_workbook_dates.py
written as delimited text. The twin each counted run writes is checked
byte for byte against an uncounted run, so the counting cannot move a
twin unseen. The ledger holds the questions as the entry's
must-not-get-worse bound and the seconds of the first shape under 2 on
the quiet reference machine. A few seconds.

    .venv/bin/python tools/measurements/kpi_datetime_speed.py --kpi
"""

import hashlib
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
from synthtwin import generation, rendering  # noqa: E402

kpi_rules.guard_this_tree()
import test_stage2_timestamp_spellings as spellings  # noqa: E402
import test_workbook_dates as dates  # noqa: E402

tally = {"calls": 0, "questions": 0, "steps": 0}


class Counting(dict):
    """The held-unit table, counting every question asked of it."""

    def __contains__(self, key):
        tally["questions"] += 1
        return dict.__contains__(self, key)

    def __getitem__(self, key):
        tally["questions"] += 1
        return dict.__getitem__(self, key)


def counted(search):
    def wrapped(facts, value, lowest, highest, day, step, unit, held, *rest, **named):
        tally["calls"] += 1
        found = search(facts, value, lowest, highest, day, step, unit, Counting(held),
                       *rest, **named)
        if found is None:
            tally["steps"] += max(value - lowest, highest - value) // unit + 1
        else:
            tally["steps"] += abs(found // unit - value // unit)
        return found
    return wrapped


ORIGINALS = {name: getattr(generation, name)
             for name in ("_nearest_held_unit", "_nearest_free_unit")}


def run(described):
    for name, search in ORIGINALS.items():
        setattr(generation, name, search)
    plain = hashlib.sha256(rendering.twin_csv(
        generation.generate(described.loaded, 4)).encode("utf-8")).hexdigest()
    started = time.perf_counter()
    generation.generate(described.loaded, 4)
    seconds = time.perf_counter() - started
    for name, search in ORIGINALS.items():
        setattr(generation, name, counted(search))
    tally.update(calls=0, questions=0, steps=0)
    twin = generation.generate(described.loaded, 4)
    for name, search in ORIGINALS.items():
        setattr(generation, name, search)
    counted_twin = hashlib.sha256(rendering.twin_csv(twin).encode("utf-8")).hexdigest()
    if counted_twin != plain:
        print("REFUSING: the counted run wrote a different twin", flush=True)
        raise SystemExit(kpi_rules.REFUSED_EXIT)
    return dict(tally), seconds


def extract_text(rows):
    # THE ONE PLACE OUTSIDE tests/crosscheck.py THAT NAMES openpyxl, and
    # `tests/test_dependencies.py` records it by name with this reason.
    # openpyxl is TEST-ONLY -- synthtwin imports it nowhere -- and CI's
    # `minimums` cell has none, so a test that needs it SKIPS through
    # `tests/crosscheck.py`. This is not a test: it is a measurement
    # driver run by hand on a quiet machine, no test loads it, and a
    # pytest helper has no business inside `tools/`. On a floors-only
    # environment it cannot run at all, which is the right answer for it.
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
    print("partly 2000:", work, f"{seconds:.2f} s", flush=True)
    value.update(questions_partly_2000=work["questions"], calls_partly_2000=work["calls"],
                 steps_partly_2000=work["steps"], seconds_partly_2000=round(seconds, 2))
    extract = kpi_shapes.describe(home / "extract", "extract", extract_text(2000))
    work, seconds = run(extract)
    print("extract 2000:", work, f"{seconds:.2f} s", flush=True)
    value.update(questions_extract_2000=work["questions"], calls_extract_2000=work["calls"],
                 steps_extract_2000=work["steps"], seconds_extract_2000=round(seconds, 2))
kpi_rules.emit("K-2B-14", value)

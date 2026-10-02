"""K-S3-54 and K-S3-55: computed numbers written in full, and a column nothing reads, through `synthtwin profile`.

K-S3-54 (plan P4-D380). A number a program computes and writes in
full -- hours between two times as seconds over 3,600, a ratio of two
counts, a time as a fraction of a day: Python's `repr`, pandas' default
-- has a different spelling on almost every row, and the walk asking
whether its fraction widths may pool nested once per width and charged
a reading of the free cells one step however long it took. On 668f276
the reach audit's skeptic measured `synthtwin profile` stopping on a
stack trace in 14, 7 and 15 of 20 seeds of the three shapes at 1,000
rows, and the walk alone, made iterative, at 41 s for 3,000 rows and
past twelve CPU minutes at 10,000. This drives the same three
generators at 1,000 rows and seeds 0 to 19 through the command and
counts every run that did not end with both files written; then the
gate's 10,000- and 100,000-row columns, counting the readings'
big-number steps and every placement onto a state of more than half
the rows, with the seconds beside them (judged only on the quiet
reference machine, `kpi_rules.seconds_judged_here`).

K-S3-55 (the same plan entry). A column the earlier rules decline was
split by `taxonomy.affixed_split` sixteen times a cell; it is split once
per different text now. Its count is the FAST test `test_k_s3_55`; this
adds the seconds an unread 10,000-row column takes to describe.

    .venv/bin/python tools/measurements/kpi_full_precision.py --kpi
"""

import contextlib
import io
import pathlib
import random
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
from synthtwin import cli, parsing  # noqa: E402

import test_stage3b_full_precision as gate  # noqa: E402


def frac_of_day(rows, seed):
    draw = random.Random(seed)
    return [repr(draw.randrange(86400) / 86400) for _cell in range(rows)]


def ratio(rows, seed):
    draw = random.Random(seed)
    return [repr(draw.randrange(1, 500) / draw.randrange(1, 500)) for _cell in range(rows)]


SHAPES = {"hours_between": gate.hours_between, "ratio": ratio, "frac_of_day": frac_of_day}

counts = {"spreads": 0, "wide": 0, "rows": 0}
spread = parsing._spread
placements = parsing._placements


def counted_spread(sums, low, high, barred):
    counts["spreads"] += 1
    return spread(sums, low, high, barred)


def counted_placements(state, kinds, index, rows, spellings, budget):
    if sum(len(loads) for loads in state) > counts["rows"] // 2:
        counts["wide"] += 1
    return placements(state, kinds, index, rows, spellings, budget)


def described(folder, name, cells):
    """`synthtwin profile` on one column: whether both files were written, and the seconds."""
    path = gate._table(folder, name, cells)
    started = time.perf_counter()
    heard = io.StringIO()
    code = None
    with contextlib.redirect_stdout(heard), contextlib.redirect_stderr(heard):
        try:
            code = cli.main(["profile", str(path), "--out-dir", str(folder), "--replace"])
        except BaseException as stopped:  # noqa: BLE001 -- a stack trace is what this counts
            code = type(stopped).__name__
    seconds = time.perf_counter() - started
    written = (folder / f"{name}-profile.json").is_file() and (folder / f"{name}-profile.txt").is_file()
    return code == 0 and written, seconds


value = {}
with tempfile.TemporaryDirectory() as home:
    home = pathlib.Path(home)
    columns = crashed = 0
    for shape in sorted(SHAPES):
        for seed in range(20):
            ok, _seconds = described(home / f"{shape}-{seed}", "x", SHAPES[shape](1000, seed))
            columns += 1
            crashed += not ok
            if not ok:
                print(f"{shape} seed {seed}: NOT DESCRIBED", flush=True)
    print(f"{columns} columns at 1,000 rows, {crashed} not described", flush=True)
    parsing._spread = counted_spread
    parsing._placements = counted_placements
    try:
        for rows in (10_000, 100_000):
            counts.update(spreads=0, wide=0, rows=rows)
            ok, seconds = described(home / f"gate-{rows}", "hours", gate.hours_between(rows, gate.GATE_SEED))
            crashed += not ok
            print(f"{rows} rows: described {ok}, {seconds:.1f} s, {counts['spreads']} big-number steps, "
                  f"{counts['wide']} placements wider than half the rows", flush=True)
            if rows == 10_000:
                value.update(spreads_10k=counts["spreads"], seconds_10k=round(seconds, 2))
            else:
                value.update(wide_placements_100k=counts["wide"], seconds_100k=round(seconds, 2))
    finally:
        parsing._spread = spread
        parsing._placements = placements
    value.update(columns=columns, crashed=crashed)
    ok, seconds = described(home / "unread", "stamps", gate.oracle_timestamps(10_000, 7))
    print(f"unread 10,000 rows: described {ok}, {seconds:.1f} s", flush=True)
    unread = {"seconds_unread_10k": round(seconds, 2)}
    if not ok:
        unread.update(described_unread_10k=0)
kpi_rules.emit("K-S3-54", value)
kpi_rules.emit("K-S3-55", unread)

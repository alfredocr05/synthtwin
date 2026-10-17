"""K-S4-19: generating a column of signed changes, timed, over a sweep of sizes and seeds.

Lane H2 (plan P4-D403). A number column of signed changes -- gauss(0, 40)
written `+3.25`, `+12` and `12` for the values at or above nought and
`-1.50` and `-4` for the others, lane H1's shape -- made `synthtwin
generate` stall at 4,000 and 5,000 rows on 36ad3061: the style question
`_style_strata` asks the packing walk has no answer, and the walk tried
every fill of one cell before saying so (24.2 million reserve readings in
300 s, unfinished). Condition 6 of `generation._cell_entry` refuses it on
entering. `K-S4-18` holds that refusal as machine-free counts of work;
this driver records what a person waits for, which is the machine's as
much as the code's, so the ledger judges its seconds only on the quiet
reference machine (`kpi_rules.MACHINE_KINDS`) and records them elsewhere.

Two measures, each table described in process by `kpi_shapes.describe`
at the shipped floor and its twin generated at seed 0:

* the seconds `generation.generate` takes on H1's column at 5,000 rows
  (seed 20261016);
* the sweep: the same shape at 3,000, 4,000, 5,000, 6,000, 8,000 and
  10,000 rows, column seeds 1 to 5, 30 twins, each given at most 30 s by
  this driver's own alarm (the product has no limit, plan P2-C3-F1). It
  records how many finish inside it and the slowest; on 36ad3061, 21 of
  the 30 passed 30 s.

About two minutes. POSIX only (the alarm); on a platform without
SIGALRM each twin runs to its end.

    .venv/bin/python tools/measurements/kpi_packing_sweep.py --kpi
"""

import hashlib
import pathlib
import random
import signal
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

H1_SEED = 20261016
SWEEP_ROWS = (3000, 4000, 5000, 6000, 8000, 10000)
SWEEP_SEEDS = (1, 2, 3, 4, 5)
LIMIT_SECONDS = 30


def signed_changes(rows: int, seed: int) -> str:
    """The column's text: lane H1's signed changes, ``rows`` of them drawn at ``seed``."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(rows):
        value = draw.gauss(0.0, 40.0)
        kind = draw.random()
        if value >= 0:
            if kind < 0.6:
                cells += [f"+{value:.2f}"]
            elif kind < 0.8:
                cells += [f"+{int(value)}"]
            else:
                cells += [f"{int(value)}"]
        elif kind < 0.7:
            cells += [f"{value:.2f}"]
        else:
            cells += [f"{int(value)}"]
    return "change\n" + "\n".join(cells) + "\n"


class OverLimit(Exception):
    """The driver's own alarm: a twin took longer than LIMIT_SECONDS."""


def on_alarm(signum: int, frame: object) -> None:
    raise OverLimit()


ALARM = getattr(signal, "SIGALRM", None)
if ALARM is not None:
    signal.signal(ALARM, on_alarm)


def timed(folder: pathlib.Path, stem: str, text: str) -> "tuple[float | None, str]":
    """Describe ``text`` and generate its twin at seed 0: the seconds, or None past the limit, and the twin's digest."""
    described = kpi_shapes.describe(folder, stem, text)
    started = time.perf_counter()
    if ALARM is not None:
        signal.alarm(LIMIT_SECONDS)
    try:
        twin = generation.generate(described.loaded, 0)
    except OverLimit:
        return None, ""
    finally:
        if ALARM is not None:
            signal.alarm(0)
    seconds = time.perf_counter() - started
    return seconds, hashlib.sha256(rendering.twin_csv(twin).encode("utf-8")).hexdigest()


value: "dict[str, object]" = {}
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    seconds, digest = timed(home / "h1", "h1-5000", signed_changes(5000, H1_SEED))
    print(f"H1's column at 5,000 rows: {seconds} s, twin {digest[:16]}", flush=True)
    value["generate_seconds_5000_rows"] = (
        round(seconds, 2) if seconds is not None else float(LIMIT_SECONDS)
    )
    finished = 0
    slowest = 0.0
    for seed in SWEEP_SEEDS:
        for rows in SWEEP_ROWS:
            took, digest = timed(home / f"s{seed}-{rows}", f"a-{rows}-s{seed}", signed_changes(rows, seed))
            print(f"seed {seed}, {rows} rows: {took} s", flush=True)
            if took is None:
                slowest = float(LIMIT_SECONDS)
            else:
                finished += 1
                slowest = max(slowest, took)
    value["sweep_twins"] = len(SWEEP_SEEDS) * len(SWEEP_ROWS)
    value["sweep_finished_within_30_s"] = finished
    value["sweep_slowest_generate_seconds"] = round(slowest, 2)
kpi_rules.emit("K-S4-19", value)

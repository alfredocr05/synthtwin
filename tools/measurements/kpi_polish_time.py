"""K-S6-13, the implied slope's and the polish's seconds and peak memory (generation method G16.2 and G16.3; lane MPg, plan P4-D456).

On an invented table of 50 columns (an age, 24 measurements in chains
with a few blanks, 10 yes/no columns, 10 labels of three to six levels and
5 small counts, every cell drawn from a fixed seed) at 20,000 and 200,000
rows, each step run in a process of its own so its peak is its own: the
imports alone (`import`, the floor every step stands on), the description
(`profile.build_document`), the chain with rule B's moments
(`chain.describe`, the ledger's fixed test key), and three generates of
the same switched description at twin seed 0: the walk by hidden scores
alone (`walk`), the walk with the implied slope (`implied`) and the
shipped twin, the polish added (`polish`). Beside them, THE POLISH'S OWN
STEP (`column`): one round of one column on synthetic rows (the hidden
sums drawn as the generate draws them, then `_polish_column`, with 45
partners and 4 groupings holding band spreads) at 200,000, 500,000 and
1,000,000 rows, with its frame in ten groups and in ONE (every row in one
group, as a binary whose families cross it with nothing: the step's
largest working set; repair 2).

MEMORY IS THE FOOTPRINT (repair 1, lane MPg's reviews' memory items): each
child's peak is its physical footprint, compressed pages included, never
the child's own `ru_maxrss`, which compression hides. On macOS it is the
child's LIFETIME PEAK, exact, which `time -l` prints when the child ends
(repair 2: the parent's sampling every few seconds missed 16 MB at
200,000 rows); elsewhere the parent samples the resident set every few
seconds, and `footprint_counter` says which was read. Each child reads
the package's compiled code from a cache one discarded import child
fills first, as an installed package does (repair 2: compiling the
generator's source peaked at about 170 MB in every child). Each step's
INCREMENT is its peak less the imports' peak, and it is projected to
2,000,000 rows LINEARLY (`a + b n` through the two sizes; through the
three for the polish's own step, by least squares), the imports added
back. Seconds: each step's, the implied slope's and the polish's own (the
generates' differences), each one's scaling exponent from 20,000 to
200,000 rows and its projection by it; seconds are judged only on a quiet
machine, so a run beside other work records them as load-disturbed.

    PYTHONPATH=src:tests python tools/measurements/kpi_polish_time.py --kpi

About two hours on the reference machine, most of it the 200,000-row
generates; each child process stays under 2 GB.
"""

import json
import math
import os
import pathlib
import random
import resource
import subprocess
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
SIZES = (20000, 200000)
COLUMN_SIZES = (200000, 500000, 1000000)
KEY = bytes(range(32))
FLOOR = 11
STEPS = ("import", "describe", "chain", "walk", "implied", "polish")
SAMPLE_SECONDS = 3.0


def table_text(rows: int, seed: int = 1) -> str:
    """The invented 50-column table: nothing real, every cell drawn from `seed`."""
    draw = random.Random(seed)
    names = ["age"] + [f"m{k:02d}" for k in range(1, 25)] + [f"y{k:02d}" for k in range(1, 11)]
    names += [f"g{k:02d}" for k in range(1, 11)] + [f"c{k}" for k in range(1, 6)]
    lines = [",".join(names)]
    for _row in range(rows):
        age = draw.randint(18, 90)
        cells = [str(age)]
        before = (age - 54) / 21
        values = []
        for k in range(24):
            value = 0.6 * before + 0.8 * draw.gauss(0, 1) if k % 6 else 0.4 * (age - 54) / 21 + draw.gauss(0, 1)
            before = value
            values += [value]
            cells += ["" if draw.random() < 0.03 else f"{50 + 10 * value:.1f}"]
        for k in range(10):
            cells += ["1" if draw.random() < 1 / (1 + math.exp(-values[2 * k])) else "0"]
        for k in range(10):
            levels = 3 + k % 4
            at = min(levels - 1, max(0, int((values[k + 3] + 2) * levels / 4)))
            cells += [f"L{at}" if draw.random() < 0.85 else f"L{draw.randrange(levels)}"]
        for k in range(5):
            cells += [str(sum(1 for _ in range(6) if draw.random() < 0.15 + 0.1 * (values[k] > 0)))]
        lines += [",".join(cells)]
    return "\n".join(lines) + "\n"


def _peak_mb() -> float:
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / 1048576 if sys.platform == "darwin" else peak / 1024, 1)


def _footprint_mb(pid: int) -> float:
    """A process's physical footprint now, compressed pages included (macOS's `top` MEM; elsewhere the resident set)."""
    if sys.platform == "darwin":
        done = subprocess.run(["top", "-l", "1", "-pid", str(pid), "-stats", "pid,mem"], capture_output=True, text=True, check=False)
        for line in reversed(done.stdout.splitlines()):
            parts = line.split()
            if len(parts) == 2 and parts[0] == str(pid):
                text = parts[1].rstrip("+-")
                scale = {"K": 1 / 1024, "M": 1.0, "G": 1024.0, "B": 1 / 1048576}.get(text[-1:], None)
                if scale is not None:
                    return float(text[:-1]) * scale
                return float(text) / 1048576
        return 0.0
    status = pathlib.Path(f"/proc/{pid}/status")
    if status.exists():
        for line in status.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return float(line.split()[1]) / 1024
    return 0.0


# macOS's `time -l` prints the child's LIFETIME PEAK physical footprint
# (the kernel's own maximum, compressed pages included), exact rather than
# sampled (repair 2: a sample every few seconds missed 16 MB at 200,000
# rows, about 190 MB on the line to 2,000,000).
TIME_COMMAND = "/usr/bin/time"


def _exact_peak(err: str) -> "float | None":
    """The `peak memory footprint` line `time -l` writes, in MB, or None."""
    for line in reversed(err.splitlines()):
        parts = line.split()
        if len(parts) == 4 and parts[1:] == ["peak", "memory", "footprint"] and parts[0].isdigit():
            return int(parts[0]) / 1048576
    return None


def _run_child(arguments: "list[str]", env: "dict[str, str] | None" = None) -> "tuple[dict[str, float], float, str]":
    """Runs one step in a child process; returns its report, its peak footprint in MB and how the peak was read.

    On macOS the child runs under `time -l`, which gives its lifetime peak
    footprint (`exact`); elsewhere the parent samples the child's resident
    set every `SAMPLE_SECONDS` (`sampled`).
    """
    exact = sys.platform == "darwin" and os.path.exists(TIME_COMMAND)
    command = ([TIME_COMMAND, "-l"] if exact else []) + [sys.executable, __file__] + arguments
    child = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env if env is not None else dict(os.environ))
    peak = 0.0
    while child.poll() is None:
        if not exact:
            peak = max(peak, _footprint_mb(child.pid))
        time.sleep(SAMPLE_SECONDS if not exact else 0.5)
    out, err = child.communicate()
    lines = [line for line in out.splitlines() if line.startswith("STEP ")]
    if child.returncode or not lines:
        raise SystemExit(f"step {arguments} failed: {err[-2000:]}")
    read = _exact_peak(err) if exact else None
    if read is not None:
        return json.loads(lines[-1][5:]), round(read, 1), "exact"
    return json.loads(lines[-1][5:]), round(peak, 1), "sampled"


def run_column(rows: int, groups: int = 10) -> "dict[str, float]":
    """THE POLISH'S OWN STEP: one round of one column on `rows` synthetic rows, as the generate runs it.

    `groups` chain-level bands, the frame (ten; one, every row in one
    group, as a binary whose families cross it with nothing, the column
    step's largest working set); 45 partner numbers, each with codes, rank codes
    and a reading on four rows of five; 4 grouping columns of eight bands,
    each a `within` target with published band spreads; the hidden sums
    drawn as `generate_held` draws them (blocks of 65,536 rows).
    """
    sys.path.insert(0, str(ROOT / "src"))
    import numpy.random

    from synthtwin import chain_walk, generation
    draw = random.Random(3)
    column = generation._WalkColumn(0, 0, (tuple(range(20)), tuple(b // 2 for b in range(20)), tuple(b // 4 for b in range(20))), (20, 10, 5), ())
    column.index = bytearray(3 * rows)
    column.index_width = 3
    for row in range(rows):
        chain_walk.write_code(column.index, 3, row, row)
    column.codes = bytearray((row * groups) // rows for row in range(rows))
    column.width = 1
    column.slot_l0 = bytearray((row * 20) // rows for row in range(rows))
    column.l0_width = 1
    column.slot_codes = bytearray(min(255, (row * 256) // rows) for row in range(rows))
    column.slot_has = bytearray([1]) * rows
    column.slot_rank = generation._rank_codes([float(row) for row in range(rows)])
    codes = {"x": bytearray(column.slot_codes)}
    has = {"x": bytearray([1]) * rows}
    ranks = {"x": bytearray(column.slot_rank)}
    for j in range(45):
        codes[f"p{j}"] = bytearray(draw.randrange(256) for _row in range(rows))
        has[f"p{j}"] = bytearray(1 if draw.random() > 0.2 else 0 for _row in range(rows))
        ranks[f"p{j}"] = bytearray(draw.randrange(256) for _byte in range(2 * rows))
    bands = {(f"g{j}", 1): bytes(draw.randrange(8) for _row in range(rows)) for j in range(4)}
    spreads = {name: generation._code_spread(codes[name], has[name]) for name in codes}
    targets = [generation._PolishTarget("pair", f"p{j}", 0.3, (), 0.3) for j in range(45)]
    targets += [
        generation._PolishTarget("within", f"g{j}", 0.05, tuple(draw.uniform(-1, 1) for _band in range(8)), 0.05, 1,
                                 tuple(30.0 for _band in range(8)), [1.0 for _band in range(8)])
        for j in range(4)
    ]
    normal = [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS)) for step in range(generation._POLISH_RANK_STEPS)]
    state = generation._PolishState([("x", targets)], rows, codes, has, ranks, bands, spreads, normal, {})
    stream = numpy.random.default_rng(1)
    clock = time.perf_counter()
    sums = chain_walk.packed(rows, chain_walk.SUM_WIDTH)
    for start in range(0, rows, chain_walk.BLOCK_ROWS):
        size = min(chain_walk.BLOCK_ROWS, rows - start)
        block = stream.integers(0, generation._WORD_CEILING, size=int(3 * size), dtype="uint64", endpoint=True)
        for first in range(0, size, generation._SUMMED_ROWS):
            last = min(size, first + generation._SUMMED_ROWS)
            summed = chain_walk.hidden_sums([int(word) for word in block[3 * first:3 * last]])
            for place in range(len(summed)):
                chain_walk.put(sums, start + first + place, summed[place])
    drawn = time.perf_counter() - clock
    clock = time.perf_counter()
    generation._polish_column(column, "x", targets, sums, state, None, True)  # type: ignore[arg-type]
    return {"seconds": round(time.perf_counter() - clock, 1), "draw_seconds": round(drawn, 1), "peak_mb": _peak_mb()}


def run_step(step: str, rows: int, folder: pathlib.Path) -> "dict[str, float]":
    """One step in this process: its seconds and this process's peak memory."""
    sys.path.insert(0, str(ROOT / "src"))
    from synthtwin import canonical, chain, contract, generation, profile, reading, rendering, taxonomy

    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    source = folder / f"table-{rows}.csv"
    document_path = folder / f"document-{rows}.json"
    switched = folder / f"switched-{rows}.json"
    clock = time.perf_counter()
    if step == "import":
        # The imports' footprint is sampled while the child lives: it stays
        # two sampling periods, so the parent reads it at least once.
        time.sleep(2 * SAMPLE_SECONDS)
    elif step == "describe":
        table = reading.read_table(str(source), small_cell_floor=FLOOR)
        document = profile.build_document(table, settings, [], [], [])
        document_path.write_text(canonical.serialize(document), encoding="utf-8", newline="\n")
    elif step == "chain":
        table = reading.read_table(str(source), small_cell_floor=FLOOR)
        document = json.loads(document_path.read_text(encoding="utf-8"))
        clock = time.perf_counter()
        chained = chain.describe(table, document, settings, chain.ChainSwitch(f"time-{rows}", KEY, rows_per_person=chain.ROWS_UNASKED))
        written = dict(document)
        written["relationships"] = dict(written["relationships"], statistical=chained.statistical)
        switched.write_text(canonical.serialize(written), encoding="utf-8", newline="\n")
    else:
        loaded = contract.load_profile(str(switched), chain=True)
        generation._IMPLIED_SLOPE = step != "walk"
        generation._POLISH_ROUNDS = 8 if step == "polish" else 0
        clock = time.perf_counter()
        twin = generation.generate_held(loaded, 0)
        written_bytes = 0
        for piece in rendering.twin_csv_pieces(twin):
            written_bytes += len(piece)
    return {"seconds": round(time.perf_counter() - clock, 1), "peak_mb": _peak_mb()}


def _line(points: "list[tuple[float, float]]") -> "tuple[float, float]":
    """The least-squares line `a + b n` through `(n, y)` points (two points: the line through them)."""
    count = len(points)
    mean_n = sum(n for n, _y in points) / count
    mean_y = sum(y for _n, y in points) / count
    spread = sum((n - mean_n) ** 2 for n, _y in points)
    slope = sum((n - mean_n) * (y - mean_y) for n, y in points) / spread if spread > 0 else 0.0
    return mean_y - slope * mean_n, slope


def measure() -> "dict[str, object]":
    started = time.time()
    load_before = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
    value: "dict[str, object]" = {}
    found: "dict[int, dict[str, dict[str, float]]]" = {}
    with tempfile.TemporaryDirectory() as folder_text:
        folder = pathlib.Path(folder_text)
        for rows in SIZES:
            (folder / f"table-{rows}.csv").write_text(table_text(rows), encoding="utf-8", newline="\n")
            found[rows] = {}
        # BYTECODE (repair 2): each child reads the package's compiled code
        # from a cache of its own that one discarded import child fills
        # first, as an installed package does; compiling the generator's
        # source in a child peaked at about 170 MB, over every step's own
        # peak at 20,000 rows and the walk's at 200,000.
        env = {key: value for key, value in os.environ.items() if key != "PYTHONDONTWRITEBYTECODE"}
        env["PYTHONPYCACHEPREFIX"] = str(folder / "bytecode")
        _run_child(["--step", "import", str(SIZES[0]), str(folder)], env)
        counters: "list[str]" = []
        for step in STEPS:
            for rows in SIZES:
                report, peak, counter = _run_child(["--step", step, str(rows), str(folder)], env)
                found[rows][step] = {"seconds": report["seconds"], "footprint_mb": peak, "rss_mb": report["peak_mb"]}
                counters += [counter]
        column: "dict[int, dict[str, float]]" = {}
        single: "dict[int, dict[str, float]]" = {}
        for rows in COLUMN_SIZES:
            for groups, held in ((10, column), (1, single)):
                report, peak, counter = _run_child(["--column", str(rows), str(groups)], env)
                held[rows] = {"seconds": report["seconds"], "draw_seconds": report["draw_seconds"], "footprint_mb": peak, "rss_mb": report["peak_mb"]}
                counters += [counter]
        floor_report, floor_peak, counter = _run_child(["--step", "import", str(SIZES[0]), str(folder)], env)
        counters += [counter]
    load_after = os.getloadavg()[0] if hasattr(os, "getloadavg") else 0.0
    small, large = SIZES
    value["footprint_counter"] = "exact" if set(counters) == {"exact"} else "sampled"
    value["steps"] = {str(rows): found[rows] for rows in SIZES}
    value["column_step"] = {str(rows): column[rows] for rows in COLUMN_SIZES}
    value["column_step_one_group"] = {str(rows): single[rows] for rows in COLUMN_SIZES}
    # MEMORY: each step's increment over the imports' own footprint, projected
    # linearly to 2,000,000 rows and the imports added back.
    imports = min(peak for peak in [found[rows]["import"]["footprint_mb"] for rows in SIZES] + [floor_peak] if peak > 0)
    value["import_footprint_mb"] = round(imports, 1)
    projected_mb: "dict[str, float]" = {}
    for step in STEPS[1:]:
        start, slope = _line([(float(rows), found[rows][step]["footprint_mb"] - imports) for rows in SIZES])
        projected_mb[step] = round(imports + start + slope * 2000000, 1)
    start, slope = _line([(float(rows), column[rows]["footprint_mb"] - imports) for rows in COLUMN_SIZES])
    projected_mb["column"] = round(imports + start + slope * 2000000, 1)
    value["column_step_bytes_a_row"] = round(slope * 1048576, 1)
    start, slope = _line([(float(rows), single[rows]["footprint_mb"] - imports) for rows in COLUMN_SIZES])
    projected_mb["column_one_group"] = round(imports + start + slope * 2000000, 1)
    value["column_step_one_group_bytes_a_row"] = round(slope * 1048576, 1)
    value["projected_2m_footprint_mb"] = projected_mb
    value["projected_2m_shipped_generate_mb"] = projected_mb["polish"]
    value["projected_2m_footprint_mb_largest"] = max(projected_mb[step] for step in ("describe", "chain", "polish"))
    # SECONDS: the implied slope's and the polish's own, the generates'
    # differences, under names of their own (the shipped generate's step is
    # called `polish`, so its whole seconds once overwrote the polish's own).
    own: "dict[str, dict[int, float]]" = {
        "slope_own_seconds": {rows: found[rows]["implied"]["seconds"] - found[rows]["walk"]["seconds"] for rows in SIZES},
        "polish_own_seconds": {rows: found[rows]["polish"]["seconds"] - found[rows]["implied"]["seconds"] for rows in SIZES},
    }
    for step in STEPS[1:]:
        own[f"{step}_seconds"] = {rows: found[rows][step]["seconds"] for rows in SIZES}
    exponents: "dict[str, float | None]" = {}
    projected: "dict[str, float | None]" = {}
    for name, by_rows in own.items():
        low, high = by_rows[small], by_rows[large]
        if low > 0 and high > 0:
            power = math.log10(high / low) / math.log10(large / small)
            exponents[name] = round(power, 3)
            projected[name] = round(high * (2000000 / large) ** power, 1)
        else:
            exponents[name] = None
            projected[name] = None
    column_low, column_high = column[COLUMN_SIZES[0]]["seconds"], column[COLUMN_SIZES[-1]]["seconds"]
    if column_low > 0 and column_high > 0:
        exponents["column_seconds"] = round(math.log10(column_high / column_low) / math.log10(COLUMN_SIZES[-1] / COLUMN_SIZES[0]), 3)
    value["slope_seconds"] = {str(rows): round(own["slope_own_seconds"][rows], 1) for rows in SIZES}
    value["polish_seconds"] = {str(rows): round(own["polish_own_seconds"][rows], 1) for rows in SIZES}
    value["scaling_exponent"] = exponents
    value["polish_scaling_exponent"] = exponents["polish_own_seconds"]
    value["slope_scaling_exponent"] = exponents["slope_own_seconds"]
    value["projected_2m_seconds"] = projected
    total = sum(projected[f"{step}_seconds"] or 0.0 for step in ("describe", "chain", "polish"))
    value["projected_2m_hours_describe_chain_and_shipped_generate"] = round(total / 3600, 2)
    value["load_average"] = [round(load_before, 1), round(load_after, 1)]
    value["seconds_load_disturbed"] = max(load_before, load_after) > 4.0
    value["columns"] = 50
    value["seconds"] = round(time.time() - started, 1)
    return value


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--column":
        print("STEP " + json.dumps(run_column(int(sys.argv[2]), int(sys.argv[3]) if len(sys.argv) > 3 else 10)), flush=True)
        return 0
    if len(sys.argv) > 1 and sys.argv[1] == "--step":
        found = run_step(sys.argv[2], int(sys.argv[3]), pathlib.Path(sys.argv[4]))
        print("STEP " + json.dumps(found), flush=True)
        return 0
    value = measure()
    if "--kpi" in sys.argv:
        print("KPI " + json.dumps({"id": "K-S6-13", "value": value, "detail": "the implied slope's and the polish's time and memory (lane MPg)"}, sort_keys=True))
    else:
        print(json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

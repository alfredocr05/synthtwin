"""K-S6-15, its describe part: the switched `synthtwin profile` at scale, stage by stage (lane CHs, plan P4-D462).

The owner's big table is 2,000,000 rows by 50 columns, described,
generated and validated in 12 to 18 hours with every process under the
2.5 GB watchdog (guard.sh kills at 1,900 MB). This driver measures the
DESCRIBE of that table with the chain's switch on: the plain description
the switched command builds, then `chain.describe`'s stages, each read at
the stage's end: `describe` calls `chain._probed` there, a function that
does nothing, and this driver puts its own reading in its place.

    kpi_chain_describe_scale.py write SHAPE ROWS PATH
    kpi_chain_describe_scale.py run TABLE OUT_DIR [--group-bytes N] [--walk-bytes N] [--trace]
                                [--cut SECONDS] [--progress FILE] [--lives]
    kpi_chain_describe_scale.py bytes ROWS OUT_DIR NAME... [--whole-only]
    kpi_chain_describe_scale.py --kpi

THE SHAPES, all invented here, none from a real table: `numeric`, K-S1-06's
Gaussian columns at two places (`kpi_scale.write_numeric`, 50 columns);
`mixed`, K-S4-02's 50-column health table (`kpi_reader_memory`, record
numbers, codes, labels, numbers, dates, stamps, clocks and free texts);
`codes`, this driver's own code-heavy table of 50 columns (codes of a
letter, two figures, a point and one figure; numbers zero-padded to a
fixed width; three keys, each once a row; labels and numbers), with
its own round parameters; `wide`, 230 columns (150 numbers, 40 binaries
and 40 labels of four letters, drawn from five shared factors);
`spellings`, this driver's own table of 50 columns of many spellings
(sixteen measurements at two places spread wide, numbers, labels and
binaries), whose kept readings passed the switched describe's first
bounds at 200,000 rows.

`run` describes one table in THIS process with the switch on (a fresh
installation folder holding the fixed key `KEY`) and prints one line of
JSON: the exit, the CPU and wall seconds, the EXACT lifetime peak of the
process's physical footprint (macOS `proc_pid_rusage`, RUSAGE_INFO_V4,
`ri_lifetime_max_phys_footprint`, compressed pages included: the counter
guard.sh kills by; on Linux the resident high-water mark VmHWM, the
closest exact counter there, named in the output; never a sample), and
the stage table: each stage's CPU and wall seconds, the lifetime peak at
its end and its rise over the stage before, and with --trace the most
bytes `tracemalloc` saw held during it and what it left held. It prints
the sha256 of the written description and of the private notes (the
notes, the screen's seeds, the families chosen, the content hash and the
moment layer's inputs), so a build can be held to the same bytes. With
--cut a run stops at the end of the first stage past the CPU seconds
given and says which stage it reached; with --progress each stage's row
is written to that file as it ends, so a run its guard stops still says
where it was, and a run cut short returns its record as any other. The
readings the description kept for the chain are counted (columns,
spellings and the bytes they retain by the product's byte counter,
`retained_bytes`). Each search step's row counts the search's cache, machine-
free: its tables, their cells (the sum of len over `search.tables`) and
the counts above 256 it shares; with --lives each cached table's life
(made, last read, let go) is kept, and the run says how many cells the
cache held at its largest and how many of them no later step read.

`bytes` describes each named table (`zoo:KIND`, `wide:NAME`, `analyst:ST1`
to `analyst:ST6`, `shape:SHAPE`, `file:PATH` for a table already
written; `+unheld` after a name for the cost device) at ROWS rows with
the switch on, read whole and one column a group (whole alone with
--whole-only), and prints both digests each way: the bytes check a build
of this lane is held to.

THE GROUPS. `--group-bytes` and `--walk-bytes` set `reading.GROUP_BYTES`
and `reading.WALK_BYTES`. `--kpi` reads every size with both scaled by
the rows over 2,000,000 (as `kpi_describe_groups` does), so each size is
read in the groups 2,000,000 rows are read in.

`--kpi` (K-S6-15's describe part; about five hours, one heavy process at
a time, run it in a window the orchestrator names): the three shapes of
50 columns at 20,000, 200,000 and 500,000 rows, each size in a process
of its own and the largest size the largest of three hash seeds; one
traced run of each at 200,000 rows; the peak and the CPU seconds
projected LINEARLY to 1,000,000 and 2,000,000 rows through the 200,000-
and 500,000-row runs (the three-size least squares beside them), the
CPU seconds with the screen read at the self-test's sample of the
projected size (`projected_cpu_seconds`; the line's own figure beside
it, `_unadjusted`), every projected value marked so in its key; the
chain phase's own increment
(the peak at its end over the peak the plain description reached); and
the machine-free traced bytes a cell of the chain phase at 200,000 rows.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import time
import tracemalloc
import typing

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))

import kpi_rules  # noqa: E402

COLUMNS = 50
BIG_ROWS = 2_000_000
SIZES = (20_000, 200_000, 500_000)
TRACED_ROWS = 200_000
HASH_SEEDS = ("1", "2", "3")
SHAPES = ("numeric", "mixed", "codes")
# The fixed installation key every measured description is drawn with
# (lane MPg's `kpi_polish_time.KEY`), so two heads' bytes can be compared.
KEY = bytes(range(32))
MEBIBYTE = 1024 * 1024


# -- THE INVENTED SHAPES -------------------------------------------------


def _codes_table(path: pathlib.Path, rows: int) -> None:
    """The code-heavy table: 50 columns of this driver's own round parameters, from one seeded stream."""
    draw = random.Random(20261104)
    letters = "ABCDEFGHJKLMNPRSTVWXYZ"
    vocabularies = []
    for at in range(12):
        size = (40, 100, 200, 400)[at % 4]
        vocabularies += [[f"{draw.choice(letters)}{draw.randrange(100):02d}.{draw.randrange(10)}" for _ in range(size)]]
    weights = [[1.0 / (rank + 1) for rank in range(len(vocabulary))] for vocabulary in vocabularies]
    words = ("north", "south", "east", "west", "inner", "outer", "upper", "lower", "first", "second", "third", "other")
    header = (
        [f"code{at:02d}" for at in range(12)]
        + [f"padded{at:02d}" for at in range(10)]
        + ["record", "order_key", "account"]
        + [f"label{at:02d}" for at in range(10)]
        + [f"value{at:02d}" for at in range(15)]
    )
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(",".join(header) + "\n")
        for row in range(rows):
            cells: "list[str]" = []
            for at in range(12):
                if draw.random() < 0.05:
                    cells += [""]
                else:
                    cells += [draw.choices(vocabularies[at], weights[at])[0]]
            for at in range(10):
                width = 6 if at % 2 == 0 else 7
                # A top of 400 (repair 1): at a top of 120 a declared column's
                # recount disagreed and the chain was off (lane BT3's item).
                top = (3000, 800, 20000, 400)[at % 4]
                cells += [f"{min(int(draw.expovariate(4.0 / top)), top - 1):0{width}d}"]
            # Three keys, each once a row (a key that repeats holds the
            # chain back until its question is answered, OFF_PERSON).
            cells += [f"R{1000000 + row * 7 % 9000000:07d}"]
            cells += [f"{40000000 + row:08d}"]
            cells += [f"AC{(row * 7919) % 10000000:07d}"]
            for at in range(10):
                cells += [words[min(int(draw.expovariate(0.6)), 2 + at)]]
            for at in range(15):
                if at % 5 == 4 and draw.random() < 0.1:
                    cells += [""]
                else:
                    cells += [f"{draw.gauss(40 + 3 * at, 4 + at % 6):.1f}"]
            out.write(",".join(cells) + "\n")


def _spellings_table(path: pathlib.Path, rows: int) -> None:
    """The many-spellings table: 50 columns of this driver's own round parameters, from one seeded stream.

    Four measurements at two places spread wide (about 86,000 different
    spellings each at 200,000 rows) and twelve spread narrower (about
    51,600 each), twenty numbers at one place, eight labels and six
    binaries, all of them read as numbers or labels (three places or six
    would raise the questions that hold a column as an identifier). At the
    switched describe's first bounds on its kept readings (65,536 spellings
    a column, 524,288 a table) the chain read ten of its columns again at
    200,000 rows; under the bounds raised at lane CHs's repair 1 it keeps
    them all there.
    """
    draw = random.Random(20261105)
    words = ("low", "mid", "high", "none", "some", "many", "few", "all")
    header = (
        [f"fine{at:02d}" for at in range(4)]
        + [f"grid{at:02d}" for at in range(12)]
        + [f"value{at:02d}" for at in range(20)]
        + [f"level{at:02d}" for at in range(8)]
        + [f"flag{at:02d}" for at in range(6)]
    )
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(",".join(header) + "\n")
        for _ in range(rows):
            shared = draw.gauss(0, 1)
            cells = [f"{500 + 10 * at + 250 * (0.6 * shared + 0.8 * draw.gauss(0, 1)):.2f}" for at in range(4)]
            cells += [f"{300 + 10 * at + 120 * (0.6 * shared + 0.8 * draw.gauss(0, 1)):.2f}" for at in range(12)]
            cells += [f"{50 + at + (4 + at % 5) * (0.5 * shared + draw.gauss(0, 1)):.1f}" for at in range(20)]
            cells += [words[min(int(draw.expovariate(0.7)), 3 + at % 5)] for at in range(8)]
            cells += ["1" if draw.random() < 0.2 + 0.1 * at + (0.1 if shared > 0 else 0.0) else "0" for at in range(6)]
            out.write(",".join(cells) + "\n")


def _wide_table(path: pathlib.Path, rows: int, numbers: int = 150, binaries: int = 40, labels: int = 40) -> None:
    """The wide table: numbers, binaries and four-letter labels drawn from five shared factors, one seeded stream."""
    draw = random.Random(11)
    loads = [[draw.gauss(0, 1) for _ in range(5)] for _ in range(numbers + binaries)]
    header = [f"x{at}" for at in range(numbers)] + [f"b{at}" for at in range(binaries)] + [f"l{at}" for at in range(labels)]
    with path.open("w", encoding="utf-8", newline="") as out:
        out.write(",".join(header) + "\n")
        for _ in range(rows):
            factors = [draw.gauss(0, 1) for _ in range(5)]
            cells: "list[str]" = []
            for at in range(numbers):
                mean = 300 + 20 * sum(a * b for a, b in zip(loads[at], factors)) / 3
                cells += [f"{mean + draw.gauss(0, 10):.1f}"]
            for at in range(binaries):
                lean = -1.5 + 0.5 * sum(a * c for a, c in zip(loads[numbers + at], factors)) / 3
                cells += ["1" if draw.random() < 1 / (1 + math.exp(-lean)) else "0"]
            for _ in range(labels):
                cells += [draw.choice("abcd")]
            out.write(",".join(cells) + "\n")


def write(shape: str, rows: int, path: pathlib.Path) -> None:
    """Write one invented table of ``rows`` rows."""
    if shape == "numeric":
        import kpi_scale

        kpi_scale.write_numeric(path, rows, COLUMNS)
    elif shape == "mixed":
        import kpi_reader_memory

        kpi_reader_memory.write_table(path, rows)
    elif shape == "codes":
        _codes_table(path, rows)
    elif shape == "spellings":
        _spellings_table(path, rows)
    elif shape == "wide":
        _wide_table(path, rows)
    else:
        raise SystemExit(f"no shape {shape}")


# -- THE EXACT COUNTER ---------------------------------------------------


def counter_name() -> str:
    """Which exact counter `footprint` reads on this platform."""
    if sys.platform == "darwin":
        return "ri_lifetime_max_phys_footprint (proc_pid_rusage, RUSAGE_INFO_V4)"
    if sys.platform.startswith("linux"):
        return "VmHWM (/proc/self/status, the resident high-water mark)"
    return "none"


def footprint() -> "tuple[int, int]":
    """This process's physical footprint now and its lifetime maximum, in bytes; -1 where neither can be read."""
    if sys.platform == "darwin":
        import ctypes

        buffer = (ctypes.c_uint64 * 48)()
        library = ctypes.CDLL("/usr/lib/libproc.dylib")
        if library.proc_pid_rusage(os.getpid(), 4, ctypes.byref(buffer)) != 0:
            return -1, -1
        # After the 16 bytes of ri_uuid: ri_phys_footprint is the eighth
        # field and ri_lifetime_max_phys_footprint the twenty-ninth.
        fields = list(buffer)[2:]
        return int(fields[7]), int(fields[28])
    if sys.platform.startswith("linux"):
        now = most = -1
        for line in pathlib.Path("/proc/self/status").read_text().splitlines():
            if line.startswith("VmRSS:"):
                now = int(line.split()[1]) * 1024
            elif line.startswith("VmHWM:"):
                most = int(line.split()[1]) * 1024
        return now, most
    return -1, -1


# -- ONE RUN, STAGE BY STAGE ---------------------------------------------


class Cut(BaseException):
    """A run stopped at the end of the stage it reached past its cut (a BaseException: no handler of the command takes it)."""


class _Stages:
    """The stage probe: one row at each stage's end, the clocks and counters read here."""

    def __init__(self, trace: bool, cut: float, progress: "pathlib.Path | None") -> None:
        self.trace = trace
        self.cut = cut
        self.progress = progress
        self.began = time.process_time()
        self.cpu = self.began
        self.wall = time.perf_counter()
        self.rows: "list[dict[str, object]]" = []
        self.peak = footprint()[1]
        # The search (`chain._Search`) once `search_chain` is called, and the
        # search step reached: the cache is counted at each step's end.
        self.cache: "dict[str, typing.Any]" = {"search": None, "step": 0}

    def __call__(self, stage: str, counts: "dict[str, int]") -> None:
        cpu = time.process_time()
        wall = time.perf_counter()
        now, most = footprint()
        row: "dict[str, object]" = {
            "stage": "plain description" if stage == "start" else stage,
            "cpu": round(cpu - self.cpu, 4),
            "wall": round(wall - self.wall, 4),
            "footprint_mb": round(now / MEBIBYTE, 1),
            "lifetime_peak_mb": round(most / MEBIBYTE, 1),
            "rise_mb": round(max(most - self.peak, 0) / MEBIBYTE, 1),
            "tables_counted": counts["tables_counted"] if "tables_counted" in counts else 0,
        }
        search = self.cache["search"]
        if stage == "search step" and search is not None:
            # THE SEARCH'S CACHE AT THIS STEP (LANE CHs RULINGS 4 (3)), machine-free:
            # its tables, their cells (the sum of len over `search.tables`)
            # and the counts above 256 it shares (len of `search.shared`).
            tables = getattr(search, "tables")
            row["cache_tables"] = len(tables)
            row["cache_cells"] = sum(len(table) for table in tables.values())
            row["cache_shared"] = len(getattr(search, "shared"))
            self.cache["step"] += 1
        if self.trace:
            held, most_traced = tracemalloc.get_traced_memory()
            tracemalloc.reset_peak()
            row["traced_peak_bytes"] = most_traced
            row["traced_held_bytes"] = held
        self.cpu, self.wall, self.peak = cpu, wall, max(most, self.peak)
        self.rows += [row]
        if self.progress is not None:
            with self.progress.open("a", encoding="utf-8") as out:
                out.write(json.dumps(row) + "\n")
        if self.cut and cpu - self.began > self.cut:
            raise Cut(row["stage"])


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def retained_bytes(text: str) -> int:
    """THE BYTE COUNTER: what one kept spelling retains, as `taxonomy._kept_bytes` counts it (its characters, at most four bytes each, beside 176 of slot)."""
    if text.isascii():
        return 176 + len(text)
    return 176 + 32 + 4 * len(text)


def _private_bytes(chained: object) -> bytes:
    """The private notes and the other unpublished facts `describe` returns, as bytes to hash."""
    record = {
        "notes": list(getattr(chained, "notes")),
        "seeds": [list(seed) for seed in getattr(chained, "seeds")],
        "chosen": [[child, list(parents), list(levels)] for child, parents, levels in getattr(chained, "chosen")],
        "content": getattr(chained, "content"),
        "moments": getattr(chained, "moments"),
    }
    return json.dumps(record, sort_keys=True).encode("utf-8")


def _summed(rows: "list[dict[str, object]]") -> "list[dict[str, object]]":
    """The stage rows summed by stage, in the order each stage first ended."""
    out: "dict[str, dict[str, object]]" = {}
    for row in rows:
        name = f"{row['stage']}"
        if name not in out:
            out[name] = {"stage": name, "calls": 0, "cpu": 0.0, "wall": 0.0, "rise_mb": 0.0, "lifetime_peak_mb": 0.0}
        held = out[name]
        held["calls"] = int(f"{held['calls']}") + 1
        for key in ("cpu", "wall", "rise_mb"):
            held[key] = round(float(f"{held[key]}") + float(f"{row[key]}"), 4)
        held["lifetime_peak_mb"] = row["lifetime_peak_mb"]
        held["tables_counted"] = row["tables_counted"]
        if "traced_peak_bytes" in row:
            held["traced_peak_bytes"] = max(int(f"{held.get('traced_peak_bytes', 0)}"), int(f"{row['traced_peak_bytes']}"))
            held["traced_held_bytes"] = row["traced_held_bytes"]
    return list(out.values())


# What a person who knows each invented table declares before the chain
# can read it: the code-heavy table's codes and zero-padded numbers are
# codes.
# Unanswered, their open question holds them, and a held column that
# repeats turns the chain off (OFF_PERSON). The mixed table keeps its
# truthful holds (its post codes and its authors' names stay held and
# repeat), so the command publishes no chain of it; `--unheld` measures
# the chain phase over its columns as lane MPg's chain step reads it
# (`chain.describe` handed no held column and no column held as an
# identifier), a cost device whose written files are deleted.
DECLARED: "dict[str, tuple[str, ...]]" = {
    "numeric": (),
    "mixed": (),
    "codes": tuple(word for at in range(12) for word in ("--code", f"code{at:02d}"))
    + tuple(word for at in range(10) for word in ("--code", f"padded{at:02d}")),
    "wide": (),
    "spellings": (),
}


def _cache_life(lives: "dict[object, list[int]]", steps: int) -> "dict[str, object]":
    """What the search's cache held at each step, from each table's life: when made, last read and let go, and its cells.

    A table read for the last time before a step and still held there is
    one no later step read (seen after the run, so an upper bound on what
    any rule letting go of tables before they are read again could cut).
    """
    alive = [0] * steps
    unread = [0] * steps
    for born, last, gone, cells in lives.values():
        for step in range(born, gone if gone >= 0 else steps):
            alive[step] += cells
            if last < step:
                unread[step] += cells
    peak = max(range(steps), key=lambda step: alive[step]) if steps else 0
    return {
        "steps": steps,
        "tables_made": len(lives),
        "cells_at_its_largest": alive[peak] if steps else 0,
        "step_at_its_largest": peak,
        "cells_never_read_again_at_its_largest": unread[peak] if steps else 0,
        "cells_by_step": alive,
        "cells_never_read_again_by_step": unread,
    }


def run(table: str, out: pathlib.Path, group_bytes: int, walk_bytes: int, trace: bool, cut: float, progress: str,
        declared: "tuple[str, ...]" = (), unheld: bool = False, lives: bool = False) -> "dict[str, object]":
    """Describe ``table`` with the switch on, in this process; what each stage took. An empty table imports only.

    With ``lives`` each table the search caches is kept with the step it
    was made, the last step that read it, the step it was let go and its
    cells (`_cache_life`): about 200 bytes a table, held beside the run.
    """
    from synthtwin import asking, chain, chain_moments, cli, reading
    import synthtwin

    if not table:
        now, most = footprint()
        return {"exit": 0, "lifetime_peak_mb": round(most / MEBIBYTE, 1), "counter": counter_name(), "synthtwin": synthtwin.__file__}
    if group_bytes > 0:
        reading.GROUP_BYTES = group_bytes
    if walk_bytes > 0:
        reading.WALK_BYTES = walk_bytes
    out.mkdir(parents=True, exist_ok=True)
    data = out / "installation"
    shutil.rmtree(data, ignore_errors=True)
    data.mkdir(mode=0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    key.write_bytes(KEY)
    # What `describe` returns beside the description, and the CPU seconds
    # of the moments' two families of passes and of the search's counting.
    captured: "dict[str, object]" = {}
    spent = {"correlations": 0.0, "within": 0.0, "count_table": 0.0}
    # The levels each table counted over the rows was ASKED at, a member
    # at a time (W3 and NE's base levels): not the levels the walk read,
    # since a table whose members' L0 bands hold at most
    # `chain.L0_TABLE_CELLS` cells is counted at L0 and summed to them
    # (`chain._table_at`; Codex's item 6 on the lane's repair 1).
    levels_asked = [0, 0, 0]
    describe = chain.describe
    table_at = chain._table_at
    search_chain = chain.search_chain
    # A tree before this lane's search cache has no `_release` (the base's).
    release = getattr(chain, "_release", None)
    # Each cached table's life: [made at step, last read at step, let go at
    # step or -1, cells] (`lives`), the step being the probe's.
    life: "dict[object, list[int]]" = {}
    cache: "dict[str, typing.Any]" = {"search": None, "step": 0}

    def leveled(search: object, child: str, parents: "tuple[str, ...]", base: "tuple[int, ...]", levels: "tuple[int, ...]") -> object:
        key = (child, parents, levels)
        fresh = key not in getattr(search, "tables")
        if levels == base and fresh:
            for level in levels:
                levels_asked[level] += 1
        found = table_at(search, child, parents, base, levels)  # type: ignore[arg-type]
        if lives:
            step = int(cache["step"])
            if key in life:
                life[key][1] = step
            else:
                life[key] = [step, step, -1, len(found)]  # type: ignore[arg-type]
        return found

    def searching(search: object, *arguments: object, **keywords: object) -> object:
        cache["search"] = search
        return search_chain(search, *arguments, **keywords)  # type: ignore[arg-type]

    def releasing(search: object, child: str) -> None:
        if lives:
            for key in getattr(search, "tables"):
                if key[0] == child and key in life:
                    life[key][2] = int(cache["step"])
        if release is not None:
            release(search, child)

    def capturing(*arguments: object, **keywords: object) -> object:
        if unheld:
            import dataclasses

            # The cost device: no held column and no column held as an
            # identifier, so the chain reads every column it can (the
            # written description keeps the command's own settings).
            document = dict(arguments[1])  # type: ignore[call-overload]
            settings_block = document.get("settings")
            if isinstance(settings_block, dict):
                document["settings"] = dict(settings_block, forced_identifiers=[])
            arguments = (arguments[0], document, arguments[2], dataclasses.replace(arguments[3], held=())) + arguments[4:]  # type: ignore[type-var]
        # The readings the description kept for the chain, as handed over:
        # how many columns and spellings (`taxonomy.KeptSpellings`), and the
        # bytes they retain by the byte counter (`retained_bytes`), read
        # alike on a tree whose kept readings count none.
        kept = arguments[8] if len(arguments) > 8 else keywords.get("kept")
        if isinstance(kept, dict):
            captured["kept_columns"] = len(kept)
            captured["kept_spellings"] = sum(len(getattr(one, "spellings")) for one in kept.values())
            captured["kept_bytes"] = sum(retained_bytes(text) for one in kept.values() for text in getattr(one, "spellings"))
        found = describe(*arguments, **keywords)  # type: ignore[arg-type]
        captured["chained"] = found
        return found

    def timed(name: str, function: "typing.Callable[..., object]") -> "typing.Callable[..., object]":
        def call(*arguments: object, **keywords: object) -> object:
            began = time.process_time()
            try:
                return function(*arguments, **keywords)
            finally:
                spent[name] += time.process_time() - began

        return call

    patched = ((chain, "describe", capturing), (chain_moments, "pair_moments", timed("correlations", chain_moments.pair_moments)),
               (chain_moments, "within_moments", timed("within", chain_moments.within_moments)),
               (chain, "count_table", timed("count_table", chain.count_table)), (chain, "_table_at", leveled),
               (chain, "search_chain", searching)) + (((chain, "_release", releasing),) if release is not None else ())
    kept = [(module, name, getattr(module, name)) for module, name, _new in patched]
    for module, name, replacement in patched:
        setattr(module, name, replacement)
    target = pathlib.Path(progress) if progress else None
    if target is not None and target.exists():
        target.unlink()
    if trace:
        tracemalloc.start()
    stages = _Stages(trace, cut, target)
    stages.cache = cache
    probed = chain._probed
    chain._probed = stages  # type: ignore[assignment]
    said = io.StringIO()
    reached = ""
    code = -1
    # Every shape here is a table of one row a person, and the run says so:
    # lane GRa's subject question (plan P4-D449) holds the chain while it is
    # open (batch 4q's merge of this lane; a tree before lane GRa has no
    # such answer, and none is given there).
    answered = {"rows_per_person": asking.ANSWER_ONE_ROW_EACH} if hasattr(asking, "ANSWER_ONE_ROW_EACH") else {}
    try:
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(
                ["profile", table, "--out-dir", str(out), "--replace"] + list(declared),
                chain=cli.ChainRun(folder=str(data), **answered),
                small_tables_refused=False,
            )
    except Cut as stopped:
        reached = f"{stopped}"
    finally:
        chain._probed = probed  # type: ignore[assignment]
        for module, name, original in kept:
            setattr(module, name, original)
    # The cut is spent once a stage has reached it: the bookkeeping's own
    # reading below must not raise it again (Codex's item 7 on the lane's
    # repair 1), so a run cut short still returns its record and lets go
    # of its installation.
    stages.cut = 0.0
    stages("written document", {})
    seconds = time.process_time() - stages.began
    wall = time.perf_counter() - stages.wall + sum(float(f"{row['wall']}") for row in stages.rows)
    traced_peak = -1
    if trace:
        traced_peak = max(int(f"{row['traced_peak_bytes']}") for row in stages.rows)
        tracemalloc.stop()
    rows = stages.rows
    start_peak = float(f"{rows[0]['lifetime_peak_mb']}") if rows else 0.0
    end_peak = float(f"{rows[-1]['lifetime_peak_mb']}") if rows else 0.0
    found: "dict[str, object]" = {
        "exit": code,
        "cut_at": reached,
        "cpu_seconds": round(seconds, 1),
        "wall_seconds": round(wall, 1),
        "lifetime_peak_mb": end_peak,
        "plain_peak_mb": start_peak,
        "chain_increment_mb": round(end_peak - start_peak, 1),
        "counter": counter_name(),
        "traced_peak_bytes": traced_peak,
        "group_bytes": reading.GROUP_BYTES,
        "walk_bytes": reading.WALK_BYTES,
        "moments_seconds": {name: round(value, 2) for name, value in spent.items()},
        "members_asked_at_l0_l1_l2": levels_asked,
        "stages": _summed(rows),
        "steps": [[row["cpu"], row["tables_counted"]] for row in rows if row["stage"] == "search step"],
        "cache_cells_at_its_largest": max([int(f"{row['cache_cells']}") for row in rows if "cache_cells" in row] or [0]),
        "cache_tables_at_its_largest": max([int(f"{row['cache_tables']}") for row in rows if "cache_tables" in row] or [0]),
        "cache_shared_at_its_largest": max([int(f"{row['cache_shared']}") for row in rows if "cache_shared" in row] or [0]),
        "synthtwin": synthtwin.__file__,
    }
    if trace and len(rows) > 1:
        chain_rows = rows[1:-1]
        found["chain_traced_peak_bytes"] = max(int(f"{row['traced_peak_bytes']}") for row in chain_rows) if chain_rows else -1
        found["traced_held_at_start_bytes"] = rows[0]["traced_held_bytes"]
    written = sorted(out.glob("*-profile.json"))
    if written:
        found["description_sha256"] = _digest(written[0].read_bytes())
    chained = captured.get("chained")
    if chained is not None:
        found["private_sha256"] = _digest(_private_bytes(chained))
        found["kept_columns"] = captured.get("kept_columns", -1)
        found["kept_spellings"] = captured.get("kept_spellings", -1)
        found["kept_bytes"] = captured.get("kept_bytes", -1)
        found["counts"] = dict(getattr(chained, "counts"))
        statistical = getattr(chained, "statistical")
        found["families"] = len(statistical["chain"]) if isinstance(statistical, dict) else 0
        found["off"] = [note for note in getattr(chained, "notes") if note.startswith("no chain is published")]
    if lives:
        found["cache_life"] = _cache_life(life, int(cache["step"]))
    shutil.rmtree(data, ignore_errors=True)
    return found


# -- THE BYTES: every switched description the same, read whole and one column a group --


def battery_table(name: str, rows: int, folder: pathlib.Path) -> pathlib.Path:
    """Write one named table of the bytes battery: `zoo:KIND`, `wide:NAME`, `analyst:ST1`... or `shape:SHAPE`."""
    family, _, which = name.partition(":")
    folder.mkdir(parents=True, exist_ok=True)
    if family == "zoo":
        import health_zoo

        table = [one for one in health_zoo.TABLES if one.name == which][0]
        return health_zoo.write_table(table, folder, rows, 1)
    if family == "wide":
        import health_zoo
        import health_zoo_wide

        table = [one for one in health_zoo_wide.WIDE_TABLES if one.name == which][0]
        return health_zoo.write_table(table, folder, rows, 1)
    if family == "analyst":
        import analyst_tables

        path = folder / f"{which}.csv"
        analyst_tables.write(path, which, rows, 1)
        return path
    path = folder / f"{which}-{rows}.csv"
    write(which, rows, path)
    return path


def battery(names: "list[str]", rows: int, out: pathlib.Path, whole_only: bool = False) -> "dict[str, object]":
    """Each named table described with the switch on, read whole and one column a group: its two digests each way.

    `file:PATH` names a table already written (its rows are its own; it is
    not removed); `whole_only` reads each table whole alone (a base's run,
    whose reading in groups is lane SR's gate).
    """
    from synthtwin import reading

    whole = (reading.GROUP_BYTES, reading.WALK_BYTES)
    found: "dict[str, object]" = {}
    for name in names:
        table, _, device = name.partition("+")
        path = pathlib.Path(table.partition(":")[2]) if table.startswith("file:") else battery_table(table, rows, out / "tables")
        shape = table.partition(":")[2]
        declared = DECLARED[shape] if table.startswith("shape:") and shape in DECLARED else ()
        ways: "dict[str, object]" = {}
        both = (("whole", whole),) if whole_only else (("whole", whole), ("one column a group", (1, 1)))
        for way, budgets in both:
            reading.GROUP_BYTES, reading.WALK_BYTES = budgets
            done = run(str(path), out / "described", 0, 0, False, 0.0, "", declared, device == "unheld")
            ways[way] = [done.get("description_sha256", ""), done.get("private_sha256", ""), done["exit"],
                         done.get("families", 0), done.get("off", [])]
            shutil.rmtree(out / "described", ignore_errors=True)
        reading.GROUP_BYTES, reading.WALK_BYTES = whole
        if not whole_only:
            ways["alike"] = ways["whole"] == ways["one column a group"]
        found[name] = ways
        if not table.startswith("file:"):
            path.unlink()
    return found


# -- THE KPI -------------------------------------------------------------


def _child(table: str, out: pathlib.Path, rows: int, trace: bool, seed: str = "0") -> "dict[str, object]":
    """`run` in a process of its own (its peak is that run's alone), budgets scaled to ``rows``, under hash seed ``seed``."""
    from synthtwin import reading

    group = reading.GROUP_BYTES * rows // BIG_ROWS if rows else 0
    walk = reading.WALK_BYTES * rows // BIG_ROWS if rows else 0
    shape = pathlib.Path(table).stem.split("-")[0] if table else ""
    argv = [sys.executable, str(pathlib.Path(__file__).resolve()), "run", table or "-", str(out),
            "--group-bytes", str(group), "--walk-bytes", str(walk)] + (["--trace"] if trace else [])
    if shape in DECLARED and DECLARED[shape]:
        argv += ["--declared", shape]
    done = subprocess.run(argv, capture_output=True, text=True, check=True, env=dict(os.environ, PYTHONHASHSEED=seed))
    found = json.loads(done.stdout.strip().splitlines()[-1])
    if found["exit"] != 0:
        raise SystemExit(f"the switched synthtwin profile of {table} exited {found['exit']}")
    return found


def linear(sizes: "list[int]", values: "list[float]", at: int) -> float:
    """The value at ``at`` rows on the line through the last two sizes."""
    slope = (values[-1] - values[-2]) / (sizes[-1] - sizes[-2])
    return values[-1] + slope * (at - sizes[-1])


def least_squares(sizes: "list[int]", values: "list[float]", at: int) -> float:
    """The value at ``at`` rows on the least-squares line through every size."""
    mean_x = sum(sizes) / len(sizes)
    mean_y = sum(values) / len(values)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(sizes, values)) / sum((x - mean_x) ** 2 for x in sizes)
    return mean_y + slope * (at - mean_x)


def projected_cpu_seconds(sizes: "list[int]", totals: "list[float]", screens: "list[float]", at: int) -> "tuple[float, float]":
    """The CPU seconds at ``at`` rows, adjusted for the sample the screen reads there, and the line's own (unadjusted).

    THE SAMPLE'S JUMP (Codex's item 5 on the lane's repair 1, the
    orchestrator's LANE CHs RULINGS 7 (5)): the screen reads the
    self-test's sample, 20,000 rows below 1,000,000 tabled rows and
    200,000 from there (`chain_rules.selftest_size`), so its seconds do
    not follow the rows: every measured size draws 20,000, a table of
    2,000,000 draws 200,000. The adjusted figure takes the screen's own
    line out of the line through the last two sizes and puts back the
    screen's seconds at the largest size times the two samples' ratio.
    The tables measured hold no record holding nothing, so their tabled
    rows are their rows.
    """
    from synthtwin import chain_rules

    plain = linear(sizes, totals, at)
    ratio = chain_rules.selftest_size(at) / chain_rules.selftest_size(sizes[-1])
    return plain - linear(sizes, screens, at) + screens[-1] * ratio, plain


def measure() -> "dict[str, object]":
    """K-S6-15's describe part: every value at 1,000,000 and 2,000,000 rows PROJECTED and marked so."""
    value: "dict[str, object]" = {"sizes": list(SIZES), "hash_seeds_at_the_largest": list(HASH_SEEDS), "counter": counter_name(), "status_of_values": "projected"}
    with tempfile.TemporaryDirectory() as folder:
        work = pathlib.Path(folder)
        imports = float(f"{_child('', work / 'imports', 0, False)['lifetime_peak_mb']}")
        value["imports_mb"] = imports
        for shape in SHAPES:
            table = work / f"{shape}.csv"
            peaks: "list[float]" = []
            cpu: "list[float]" = []
            screen: "list[float]" = []
            chain_rise: "list[float]" = []
            cache_cells: "list[int]" = []
            digests: "list[str]" = []
            for rows in SIZES:
                write(shape, rows, table)
                seeds = HASH_SEEDS if rows == SIZES[-1] else ("1",)
                most = spent = screened = rise = -1.0
                for seed in seeds:
                    found = _child(str(table), work / f"{shape}-{rows}-{seed}", rows, False, seed)
                    most = max(most, float(f"{found['lifetime_peak_mb']}"))
                    spent = max(spent, float(f"{found['cpu_seconds']}"))
                    screened = max(screened, sum(float(f"{row['cpu']}") for row in found["stages"] if row["stage"] == "screen"))
                    rise = max(rise, float(f"{found['chain_increment_mb']}"))
                    if seed == seeds[0]:
                        cache_cells += [int(f"{found['cache_cells_at_its_largest']}")]
                    digests += [f"{found.get('description_sha256', '')}"]
                peaks += [most]
                cpu += [spent]
                screen += [screened]
                chain_rise += [rise]
                if rows == TRACED_ROWS:
                    traced = _child(str(table), work / f"{shape}-traced", rows, True)
                    cells = TRACED_ROWS * COLUMNS
                    value[f"{shape}_traced_bytes_a_cell"] = round(int(f"{traced['traced_peak_bytes']}") / cells, 2)
                    value[f"{shape}_chain_traced_bytes_a_cell"] = round(int(f"{traced['chain_traced_peak_bytes']}") / cells, 2)
            table.unlink()
            value[f"{shape}_peak_mb"] = peaks
            value[f"{shape}_cpu_seconds"] = cpu
            value[f"{shape}_chain_increment_mb"] = chain_rise
            # Machine-free: the search's cached cells at their most, each size.
            value[f"{shape}_search_cache_cells_at_its_largest"] = cache_cells
            value[f"{shape}_descriptions_alike_across_seeds"] = len(set(digests[-len(HASH_SEEDS):])) == 1
            top = list(SIZES[-2:])
            for at, word in ((1_000_000, "1m"), (BIG_ROWS, "2m")):
                value[f"{shape}_peak_mb_{word}_projected"] = round(linear(top, peaks[-2:], at), 1)
                value[f"{shape}_peak_mb_{word}_projected_least_squares"] = round(least_squares(list(SIZES), peaks, at), 1)
                # The key the target judges is the adjusted one (LANE CHs RULINGS 7 (5)).
                adjusted, unadjusted = projected_cpu_seconds(top, cpu[-2:], screen[-2:], at)
                value[f"{shape}_cpu_hours_{word}_projected"] = round(adjusted / 3600, 2)
                value[f"{shape}_cpu_hours_{word}_projected_unadjusted"] = round(unadjusted / 3600, 2)
                value[f"{shape}_chain_increment_mb_{word}_projected"] = round(linear(top, chain_rise[-2:], at), 1)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="")
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--group-bytes", type=int, default=0)
    parser.add_argument("--walk-bytes", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    parser.add_argument("--cut", type=float, default=0.0)
    parser.add_argument("--progress", default="")
    parser.add_argument("--declared", default="", help="a shape whose DECLARED options the run passes")
    parser.add_argument("--unheld", action="store_true", help="the cost device: describe handed no held column")
    parser.add_argument("--lives", action="store_true", help="keep each cached table's life (run)")
    parser.add_argument("--whole-only", action="store_true", help="read each table whole only (bytes; a base's run)")
    arguments = parser.parse_args()
    if arguments.action == "write":
        shape, rows, path = arguments.rest
        write(shape, int(rows), pathlib.Path(path))
        return 0
    if arguments.action == "run":
        table, out = arguments.rest
        found = run("" if table == "-" else table, pathlib.Path(out), arguments.group_bytes, arguments.walk_bytes,
                    arguments.trace, arguments.cut, arguments.progress,
                    DECLARED[arguments.declared] if arguments.declared else (), arguments.unheld, arguments.lives)
        print(json.dumps(found))
        return 0
    if arguments.action == "bytes":
        rows, out, *names = arguments.rest
        print(json.dumps(battery(names, int(rows), pathlib.Path(out), arguments.whole_only), sort_keys=True))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    value = measure()
    detail = ("the switched describe of three invented 50-column shapes, read in the groups 2,000,000 rows are read in; "
              "every 1,000,000- and 2,000,000-row value PROJECTED from 200,000 and 500,000 rows (lane SX measures them)")
    kpi_rules.emit("K-S6-15", value, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""K-S4-23 and K-S4-09's validate part: `synthtwin validate` of the big table's twin, read in groups of columns.

PLAN P4-D476 (lane SV of the December plan). The owner's big table is
2,000,000 rows by 50 columns, and `synthtwin twin TABLE` runs profile,
generate and validate, each in a process the owner's computer can hold
(the 2.5 GB bound of K-S4-09; the owner's 8 GB a process). Read whole,
`synthtwin validate` held the checked twin's bytes, its text and a
Python text object a cell. It now reads the file as `synthtwin profile`
reads a table (`reading.read_table`'s ``in_groups``, lane SR): a file
too large for one group of columns (`reading.GROUP_BYTES`) one group at
a time, every column asked of `reading.column_values`, the check's three
rewrites made of each column as it is asked for.

The two tables are lane B0's, K-S4-09's builders: the made-up 50-column
health table of K-S4-02 (`kpi_reader_memory.write_table`, seed 20261002)
and K-S1-06's Gaussian columns at two places (`kpi_scale.write_numeric`),
at 50 columns (`kpi_describe_groups.write`). No value comes from a real
table. Each size is written, described by `synthtwin profile`, its twin
generated at seed 0, and the twin validated, each step in a process of
its own, one at a time.

    kpi_validate_groups.py run DESCRIPTION TWIN OUT_DIR [--group-bytes N] [--walk-bytes N] [--trace]
    kpi_validate_groups.py imports
    kpi_validate_groups.py --kpi

`run` validates TWIN against DESCRIPTION in THIS process (`cli.main`, the
screen captured) and prints one line of JSON: the exit, the CPU and wall
seconds, the EXACT lifetime peak of the process's physical footprint
(macOS `proc_pid_rusage`, RUSAGE_INFO_V4, compressed pages included --
the counter guard.sh kills by; Linux's VmHWM; `kpi_chain_describe_scale.
footprint`), the instructions the process retired (macOS
`ri_instructions`, the counter `/usr/bin/time -l` prints; they do not
move with the machine's load; none elsewhere), the kernel's
memory-pressure level (macOS `kern.memorystatus_vm_pressure_level`, the
larger of its readings before and after the check: 1 normal, 2 warning,
4 critical; -1 elsewhere), with --trace the most bytes `tracemalloc` saw
held, and the sha256 of every file written and of the screen.
--group-bytes and --walk-bytes set `reading.GROUP_BYTES` and
`reading.WALK_BYTES`. `imports` prints the footprint of a process that
has imported synthtwin and done nothing else.

`run` NEVER CLEARS A FOLDER IT IS HANDED (Codex's review of lane SV,
item 1): it writes only into a folder of its own, OUT_DIR/kpi-validate-run,
which it makes -- refusing where one is there already -- and takes away
once it has read what the check wrote in it, so it removes nothing it
did not make; and it refuses an OUT_DIR that is either input, or is or
holds either input's folder, before it reads or writes anything.

`--kpi` measures, for each table, at 20,000 and 100,000 rows by day, at
20,000, 100,000 and 200,000 rows with `SV_KPI_NIGHT=1`, or at the sizes
`SV_KPI_SIZES` names (whole numbers of rows of at least 20,000,
comma-separated; 20,000 rows always added; a list giving fewer than two
sizes is refused before any work):

* the validate of the twin read in the groups 2,000,000 rows are read in
  (both budgets times the rows over 2,000,000, as K-S4-09 reads them),
  in THREE runs a size at hash seeds 1, 2 and 3: each size's peak
  footprint, CPU seconds and instructions retired the LARGEST of its
  three runs, K-S4-09's rule (one run a size moved by a factor of about
  two between runs of the same check on a loaded machine: the statistics
  skeptic of lane SV), each run's peak, wall seconds and memory-pressure
  level recorded beside it (`*_validate_runs`);
* the peak at 2,000,000 x 50 PROJECTED (`*_validate_peak_mb_2m_projected`,
  the keys the entry is judged by, and K-S4-09's `mixed_validate_peak_mb_2m`
  and `gaussian_validate_peak_mb_2m`) ONLY from three sizes of at least
  100,000 rows, the largest reaching 1,000,000 rows, as lane B0 projects:
  over the three largest of them, a least-squares line through log(rows)
  and log(the peak above the footprint of the imports), read at
  2,000,000 (the 20,000-row point, where fixed costs dominate, is never
  fitted). Otherwise the peak is not projected: the line through each
  two of the sizes, read at 2,000,000 rows (`*_validate_peak_mb_2m_lines`),
  is recorded context, and the entry is held OPEN with its target keys
  not measured;
* CPU seconds and instructions projected LINEARLY through the two
  largest sizes (`*_2m_projected`), recorded;
* at 20,000 rows, the bytes `tracemalloc` sees held a cell at the most,
  read in those groups (`*_validate_traced_bytes_a_cell`, recorded; at
  that size fixed costs dominate, so it does not compare with K-S4-09's
  bound at 200,000 rows: a 200,000-row traced run is `run --trace`);
* at 20,000 rows, the same twin validated again with the shipped budgets
  -- one group, the code a file read whole runs -- and every file either
  run wrote and the screen with the exit compared, sha256 for sha256 (a
  file one run alone wrote is unequal): `files_equal` of
  `files_compared`, `equal_files_ratio` 1.0 (the lane's own cases
  compare the head with the code before it, base for base).

THE EVIDENCE IS WITHHELD, NEVER FAVOURABLE BY ACCIDENT (Codex's review
of lane SV, items 2 to 5; LANE SV RULINGS 3 (2)). A validation that did
not complete -- an exit other than 0 or 3, or no report where the check
writes it -- is never read: the measurement stops at it and neither KPI
is printed. A memory counter that read nothing (`footprint`'s -1:
unsupported or unsuccessful) at any run of a table withholds that
table's peaks, its lines and its projected peak, and one that read
nothing for the imports withholds every projected peak. A size's
description and twin are measured only where the record the driver
writes beside them once it has made and counted them (`inputs.json`:
the table, its rows and columns as read back from both files, the seed,
a digest of the code that made them and the sha256 of each) still
holds; a pair kept by `SV_KPI_KEEP=FOLDER` in FOLDER/<table>-<rows>/
(desc/, twin/) whose record is missing, names another table, size or
code, or whose files no longer give its digests is made again, never
trusted by its folder's name; the digests measured are recorded.

Peaks and seconds are the machine's, judged only on the quiet reference
machine (`kpi_rules.MACHINE_KINDS`); instructions and bytes a cell are
recorded. One run a size took about 7.6 hours at night on a loaded
machine (measured once, 2026-11-09 to 11-10, `SV_KPI_NIGHT=1`); three
runs a size add twice that run's validates (about 2.9 CPU hours at the
night's sizes); by day not measured. Run it in a measurement window, one
heavy process at a time.
"""

from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))

import kpi_rules  # noqa: E402

COLUMNS = 50
BIG_ROWS = 2_000_000
SIZES = (20_000, 100_000)
NIGHT_SIZES = (20_000, 100_000, 200_000)
TRACED_ROWS = 20_000
# Each size's peak is the largest of a run at each seed (K-S4-09's rule).
HASH_SEEDS = ("1", "2", "3")
# The peak is projected to 2,000,000 rows only over three sizes of at
# least FITTED_FROM rows, the largest reaching PROJECTED_FROM.
FITTED_FROM = 100_000
PROJECTED_FROM = 1_000_000
KINDS = ("mixed", "gaussian")
MEBIBYTE = 1024 * 1024
# The seed every twin is generated at.
TWIN_SEED = 0
# The folder of its own `run` writes in, inside the OUT_DIR it is handed.
RUN_FOLDER = "kpi-validate-run"
# The record `prepare` writes beside a size's description and twin.
INPUTS = "inputs.json"
# A validation that completed: it measured the file and reported (0 met, 3 missed).
COMPLETED = (0, 3)
# What validate names its report: the checked file's stem and this (`cli._quality_path`).
QUALITY_SUFFIX = "-quality.txt"


def instructions() -> int:
    """The instructions this process has retired, or -1 where they cannot be read (macOS `proc_pid_rusage`'s `ri_instructions`)."""
    if sys.platform != "darwin":
        return -1
    import ctypes

    buffer = (ctypes.c_uint64 * 48)()
    library = ctypes.CDLL("/usr/lib/libproc.dylib")
    if library.proc_pid_rusage(os.getpid(), 4, ctypes.byref(buffer)) != 0:
        return -1
    # RUSAGE_INFO_V4: after the 16 bytes of ri_uuid, ri_instructions is
    # the thirtieth field (ri_lifetime_max_phys_footprint the twenty-ninth).
    return int(list(buffer)[2:][29])


def pressure_level() -> int:
    """The kernel's memory-pressure level (macOS `kern.memorystatus_vm_pressure_level`: 1 normal, 2 warning, 4 critical), or -1 where it cannot be read."""
    if sys.platform != "darwin":
        return -1
    import ctypes

    level = ctypes.c_int(0)
    size = ctypes.c_size_t(ctypes.sizeof(level))
    library = ctypes.CDLL("/usr/lib/libc.dylib")
    if library.sysctlbyname(b"kern.memorystatus_vm_pressure_level", ctypes.byref(level), ctypes.byref(size), None, 0) != 0:
        return -1
    return int(level.value)


def imports_only() -> "dict[str, object]":
    """The footprint of this process once synthtwin is imported (the base lane B0's projection sets aside)."""
    import kpi_chain_describe_scale as scale
    from synthtwin import cli  # noqa: F401

    _now, most = scale.footprint()
    return {"exit": 0, "peak_footprint_bytes": most}


def refused_folder(description: str, twin: str, out: pathlib.Path) -> str:
    """Why `run` will not write in ``out``, or '' where it may (Codex's review of lane SV, item 1).

    ``out`` may not be either input, lie inside either input, or be or
    hold either input's folder; it may not be a file; and the run's own
    folder inside it may not be there already, so that nothing the run
    did not make is written over or taken away. Guarantees: a function
    of the three paths and what is on disk at them. Reads nothing else.
    """
    held = out.resolve()
    for given in (description, twin):
        place = pathlib.Path(given).resolve()
        if held == place or held in place.parents or place in held.parents:
            return f"OUT_DIR {out} is, holds or lies inside {given} or its folder: name a folder of its own"
    if held.exists() and not held.is_dir():
        return f"OUT_DIR {out} is not a folder"
    if (held / RUN_FOLDER).exists() or (held / RUN_FOLDER).is_symlink():
        return f"{out / RUN_FOLDER} is there already: take it away or name another OUT_DIR"
    return ""


def run(description: str, twin: str, out: pathlib.Path, group_bytes: int, walk_bytes: int, trace: bool) -> "dict[str, object]":
    """Validate ``twin`` against ``description`` in this process, writing in a folder of its own inside ``out``; what it took and what it wrote."""
    refusal = refused_folder(description, twin, out)
    if refusal:
        raise SystemExit(refusal)
    import kpi_chain_describe_scale as scale
    import synthtwin
    from synthtwin import cli, reading

    if group_bytes > 0:
        reading.GROUP_BYTES = group_bytes
    if walk_bytes > 0:
        reading.WALK_BYTES = walk_bytes
    out.mkdir(parents=True, exist_ok=True)
    own = out / RUN_FOLDER
    # Made here, new and empty (never exist_ok): everything in it the check wrote.
    own.mkdir()
    try:
        if trace:
            tracemalloc.start()
        said = io.StringIO()
        level = pressure_level()
        began = time.process_time()
        began_wall = time.perf_counter()
        retired = instructions()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(["validate", description, "--twin", twin, "--out-dir", str(own), "--replace"])
        seconds = time.process_time() - began
        wall = time.perf_counter() - began_wall
        retired_after = instructions()
        level = max(level, pressure_level())
        traced = -1
        if trace:
            traced = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
        _now, most = scale.footprint()
        written = {
            path.name: hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(own.iterdir()) if path.is_file() and not path.is_symlink()
        }
    finally:
        # Only what the check wrote in the folder this run made.
        for path in sorted(own.iterdir()):
            if path.is_file() and not path.is_symlink():
                path.unlink()
        with contextlib.suppress(OSError):
            own.rmdir()
    return {
        "exit": code,
        "cpu_seconds": round(seconds, 1),
        "wall_seconds": round(wall, 1),
        "pressure_level": level,
        "peak_footprint_bytes": most,
        "counter": scale.counter_name(),
        "instructions": retired_after - retired if retired >= 0 and retired_after >= 0 else -1,
        "traced_peak_bytes": traced,
        "written": written,
        "screen": hashlib.sha256(said.getvalue().encode("utf-8")).hexdigest(),
        "group_bytes": reading.GROUP_BYTES,
        "walk_bytes": reading.WALK_BYTES,
        "synthtwin": synthtwin.__file__,
    }


def _child(arguments: "list[str]", seed: str = HASH_SEEDS[0]) -> "dict[str, object]":
    """One step in a process of its own at hash seed ``seed``; the last line of JSON it printed. A step that failed or printed no record stops the measurement."""
    done = subprocess.run(
        [sys.executable, str(pathlib.Path(__file__).resolve())] + arguments,
        capture_output=True, text=True, check=False, env=dict(os.environ, PYTHONHASHSEED=seed),
    )
    printed = done.stdout.strip().splitlines()
    found: object = None
    if done.returncode == 0 and printed:
        with contextlib.suppress(ValueError):
            found = json.loads(printed[-1])
    if not isinstance(found, dict):
        raise SystemExit(f"a step exited {done.returncode} and printed no record: {arguments}: {done.stderr.strip()[-600:]}")
    return found


def sha256_of(path: pathlib.Path) -> str:
    """The sha256 of a file, read a MiB at a time."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(MEBIBYTE), b""):
            digest.update(block)
    return digest.hexdigest()


def code_digest() -> str:
    """A sha256 over what makes a size's description and twin: synthtwin's source, the table builders, this driver and the interpreter's version."""
    measurements = ROOT / "tools" / "measurements"
    places = sorted((ROOT / "src" / "synthtwin").rglob("*.py")) + [
        measurements / "kpi_describe_groups.py",
        measurements / "kpi_reader_memory.py",
        measurements / "kpi_scale.py",
        ROOT / "tests" / "kpi_shapes.py",
        pathlib.Path(__file__).resolve(),
    ]
    digest = hashlib.sha256(sys.version.encode("utf-8"))
    for place in places:
        digest.update(place.resolve().relative_to(ROOT).as_posix().encode("utf-8") + b"\0" + place.read_bytes() + b"\0")
    return digest.hexdigest()


def dimensions(described: pathlib.Path, twin: pathlib.Path) -> "tuple[int, int, int, int]":
    """The rows and columns the description states, and the records and columns of the twin, read back from the two files."""
    document = json.loads(described.read_text(encoding="utf-8"))
    with twin.open(encoding="utf-8", errors="replace", newline="") as handle:
        reader = csv.reader(handle)
        header = next(reader, [])
        records = sum(1 for _record in reader)
    return int(document["n_rows"]), len(document["columns"]), records, len(header)


def kept(kind: str, rows: int, folder: pathlib.Path, described: pathlib.Path, twin: pathlib.Path) -> "dict[str, object] | None":
    """The record of a size's pair already in ``folder``, where it still holds: its table, rows, columns, seed and code are those asked, and both files give its digests; else None."""
    record_place = folder / INPUTS
    if not (record_place.is_file() and described.is_file() and twin.is_file()):
        return None
    try:
        record = json.loads(record_place.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(record, dict):
        return None
    asked = {"table": kind, "rows": rows, "columns": COLUMNS, "seed": TWIN_SEED, "code": code_digest()}
    if any(record.get(key) != value for key, value in asked.items()):
        return None
    if record.get("description_sha256") != sha256_of(described) or record.get("twin_sha256") != sha256_of(twin):
        return None
    return record


def prepare(kind: str, rows: int, folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path, dict[str, object]]":
    """The table of ``kind`` at ``rows`` rows written, described and twinned at seed 0, each in a process of its own, and its record.

    A pair already in ``folder`` is used only where its record holds
    (`kept`); otherwise the pair is made again, read back -- the rows and
    columns the description states and the twin's records and columns
    must be ``rows`` and `COLUMNS` -- and its record written beside it.
    """
    described = folder / "desc" / f"{kind}-profile.json"
    twin = folder / "twin" / f"{kind}-twin.csv"
    record = kept(kind, rows, folder, described, twin)
    if record is not None:
        return described, twin, record
    table = folder / f"{kind}.csv"
    for action in ("write", "describe", "generate"):
        found = _child([action, kind, str(rows), str(folder)])
        if found.get("exit") != 0:
            raise SystemExit(f"{action} of the {kind} table at {rows} rows exited {found.get('exit')}")
    table.unlink()
    read_back = dimensions(described, twin)
    if read_back != (rows, COLUMNS, rows, COLUMNS):
        raise SystemExit(
            f"the {kind} table made at {rows} rows reads back as {read_back[0]} rows and {read_back[1]} columns "
            f"described, {read_back[2]} records and {read_back[3]} columns twinned"
        )
    record = {
        "table": kind, "rows": rows, "columns": COLUMNS, "seed": TWIN_SEED, "code": code_digest(),
        "description_sha256": sha256_of(described), "twin_sha256": sha256_of(twin),
    }
    (folder / INPUTS).write_text(json.dumps(record, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    return described, twin, record


def step(action: str, kind: str, rows: int, folder: pathlib.Path) -> "dict[str, object]":
    """`write`, `describe` or `generate` one size in this process."""
    from synthtwin import cli

    table = folder / f"{kind}.csv"
    if action == "write":
        import kpi_describe_groups

        folder.mkdir(parents=True, exist_ok=True)
        kpi_describe_groups.write(kind, rows, table)
        return {"exit": 0}
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        if action == "describe":
            (folder / "desc").mkdir(exist_ok=True)
            code = cli.main(["profile", str(table), "--out-dir", str(folder / "desc"), "--replace"], small_tables_refused=False)
        else:
            (folder / "twin").mkdir(exist_ok=True)
            code = cli.main(
                ["generate", str(folder / "desc" / f"{kind}-profile.json"), "--seed", str(TWIN_SEED),
                 "--out-dir", str(folder / "twin"), "--replace"],
                small_tables_refused=False,
            )
    return {"exit": code}


def _number(value: object) -> float:
    """A measured number, read back from a run's JSON."""
    return float(f"{value}")


def counted(value: object) -> bool:
    """Whether a memory counter read something: `footprint` gives -1 where it is unsupported or unsuccessful, and no process holds nothing."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


def report_of(twin: pathlib.Path) -> str:
    """The name of the report validate writes of ``twin``."""
    return f"{twin.stem}{QUALITY_SUFFIX}"


def completed(found: "dict[str, object]", report: str) -> bool:
    """Whether a run's validation completed: it exited 0 or 3 and wrote ``report``."""
    written = found.get("written")
    return found.get("exit") in COMPLETED and isinstance(written, dict) and report in written


def _completed_or_stop(found: "dict[str, object]", report: str, what: str) -> "dict[str, object]":
    """``found``, where its validation completed; else the measurement stops and neither KPI is printed."""
    if not completed(found, report):
        written = found.get("written")
        state = "written" if isinstance(written, dict) and report in written else "missing"
        raise SystemExit(f"validate {what} did not complete (exit {found.get('exit')}, its report {state}): neither KPI is printed")
    return found


def projected(sizes: "list[int]", values: "list[float]") -> float:
    """The value at 2,000,000 rows on the line through the two largest sizes (LINEAR: CPU seconds and instructions, recorded)."""
    slope = (values[-1] - values[-2]) / (sizes[-1] - sizes[-2])
    return values[-1] + slope * (BIG_ROWS - sizes[-1])


def lines(sizes: "list[int]", values: "list[float]") -> "dict[str, float]":
    """The value at 2,000,000 rows on the line through each two of the sizes, keyed 'rows-rows': recorded context, never judged."""
    found: "dict[str, float]" = {}
    for first in range(len(sizes)):
        for second in range(first + 1, len(sizes)):
            slope = (values[second] - values[first]) / (sizes[second] - sizes[first])
            found[f"{sizes[first]}-{sizes[second]}"] = round(values[second] + slope * (BIG_ROWS - sizes[second]), 1)
    return found


def fitted_sizes(sizes: "list[int]") -> "list[int]":
    """The sizes the peak may be projected from: those of at least `FITTED_FROM` rows, where three of them reach `PROJECTED_FROM`; else none."""
    fitted = [size for size in sizes if size >= FITTED_FROM]
    return fitted if len(fitted) >= 3 and fitted[-1] >= PROJECTED_FROM else []


def equal_files(scaled: "dict[str, object]", shipped: "dict[str, object]") -> "tuple[int, int]":
    """How many things the two runs were compared on, and on how many they were equal: every file either run wrote, by name and sha256 (a file one run alone wrote is unequal), and the screen with the exit."""
    one: "dict[str, str]" = scaled["written"]  # type: ignore[assignment]
    other: "dict[str, str]" = shipped["written"]  # type: ignore[assignment]
    names = sorted(set(one) | set(other))
    equal = sum(1 for name in names if name in one and name in other and one[name] == other[name])
    equal += 1 if scaled["screen"] == shipped["screen"] and scaled["exit"] == shipped["exit"] else 0
    return len(names) + 1, equal


def sizes_asked() -> "list[int]":
    """The sizes measured, read before any work: `SV_KPI_SIZES` (whole numbers of at least 20,000 rows; 20,000 always among them; two sizes at least), else the night's with `SV_KPI_NIGHT=1`, else the day's."""
    named = os.environ.get("SV_KPI_SIZES", "")
    if not named:
        return list(NIGHT_SIZES if os.environ.get("SV_KPI_NIGHT") == "1" else SIZES)
    parts = [part.strip() for part in named.split(",") if part.strip()]
    if not parts or not all(re.fullmatch("[0-9]+", part) for part in parts):
        raise SystemExit(f"SV_KPI_SIZES={named!r}: name whole numbers of rows, comma-separated")
    sizes = sorted({int(part) for part in parts} | {TRACED_ROWS})
    if sizes[0] < TRACED_ROWS:
        raise SystemExit(f"SV_KPI_SIZES={named!r}: every size is at least {TRACED_ROWS:,} rows, the table floor")
    if len(sizes) < 2:
        raise SystemExit(f"SV_KPI_SIZES={named!r}: name a size above {TRACED_ROWS:,} rows, which is always measured")
    return sizes


def measure(sizes: "list[int]", keep: str) -> "tuple[dict[str, object], dict[str, object]]":
    """K-S4-23's values, and K-S4-09's validate keys where the peak is projected."""
    import kpi_describe_groups
    from synthtwin import reading

    found: "dict[str, object]" = {"sizes": sizes, "hash_seeds": list(HASH_SEEDS)}
    validate_keys: "dict[str, object]" = {}
    compared = equal = 0
    # Lane B0's fit rests on three sizes of 100,000 rows or more, the
    # largest reaching 1,000,000: fewer, or smaller, project nothing.
    fitted = fitted_sizes(sizes)
    imports = 0.0
    imports_counted = True
    if fitted:
        made = _child(["imports"])
        imports_counted = made.get("exit") == 0 and counted(made.get("peak_footprint_bytes"))
        if imports_counted:
            imports = _number(made["peak_footprint_bytes"]) / MEBIBYTE
            found["imports_mb"] = round(imports, 1)
        else:
            found["imports_mb"] = None
    with tempfile.TemporaryDirectory() as temporary:
        work = pathlib.Path(keep) if keep else pathlib.Path(temporary)
        for kind in KINDS:
            peaks: "list[float]" = []
            cpu: "list[float]" = []
            retired: "list[float]" = []
            runs: "list[list[list[float | None]]]" = []
            inputs: "dict[str, list[str]]" = {}
            memory_counted = True
            for rows in sizes:
                folder = work / f"{kind}-{rows}"
                described, twin, record = prepare(kind, rows, folder)
                if record.get("rows") != rows or record.get("columns") != COLUMNS:
                    raise SystemExit(
                        f"the {kind} pair handed for {rows} rows holds {record.get('rows')} rows and "
                        f"{record.get('columns')} columns: neither KPI is printed"
                    )
                inputs[f"{rows}"] = [f"{record.get('description_sha256')}"[:12], f"{record.get('twin_sha256')}"[:12]]
                report = report_of(twin)
                group = reading.GROUP_BYTES * rows // BIG_ROWS
                walk = reading.WALK_BYTES * group // reading.GROUP_BYTES
                arguments = ["run", str(described), str(twin), str(folder / "out"), "--group-bytes", str(group), "--walk-bytes", str(walk)]
                scaled: "list[dict[str, object]]" = []
                for seed in HASH_SEEDS:
                    scaled += [_completed_or_stop(_child(arguments, seed), report, f"of the {kind} table at {rows} rows, hash seed {seed}")]
                found["counter"] = scaled[0]["counter"]
                read = [counted(one.get("peak_footprint_bytes")) for one in scaled]
                memory_counted = memory_counted and all(read)
                peaks += [max(_number(one["peak_footprint_bytes"]) / MEBIBYTE for one in scaled) if all(read) else -1.0]
                cpu += [max(_number(one["cpu_seconds"]) for one in scaled)]
                instructions_read = all(_number(one["instructions"]) >= 0 for one in scaled)
                retired += [max(_number(one["instructions"]) / 1e9 for one in scaled) if instructions_read else -1.0]
                runs += [[
                    [
                        round(_number(one["peak_footprint_bytes"]) / MEBIBYTE, 1) if counted(one.get("peak_footprint_bytes")) else None,
                        _number(one["wall_seconds"]),
                        _number(one["pressure_level"]),
                    ]
                    for one in scaled
                ]]
                if rows == TRACED_ROWS:
                    shipped = _completed_or_stop(
                        _child(["run", str(described), str(twin), str(folder / "out")]), report,
                        f"of the {kind} table at {rows} rows at the shipped budgets",
                    )
                    asked, held = equal_files(scaled[0], shipped)
                    compared += asked
                    equal += held
                    found[f"{kind}_validate_exit_{rows}"] = scaled[0]["exit"]
                    traced = _completed_or_stop(
                        _child(arguments + ["--trace"]), report, f"of the {kind} table at {rows} rows, traced",
                    )
                    if counted(traced.get("traced_peak_bytes")):
                        found[f"{kind}_validate_traced_bytes_a_cell"] = round(_number(traced["traced_peak_bytes"]) / (rows * COLUMNS), 1)
            found[f"{kind}_validate_inputs_sha256"] = inputs
            found[f"{kind}_validate_runs"] = runs
            found[f"{kind}_validate_cpu_seconds"] = cpu
            if len(sizes) >= 2:
                found[f"{kind}_validate_cpu_seconds_2m_projected"] = round(projected(sizes, cpu), 1)
            if min(retired) >= 0:
                found[f"{kind}_validate_g_instructions"] = [round(value, 1) for value in retired]
                if len(sizes) >= 2:
                    found[f"{kind}_validate_g_instructions_2m_projected"] = round(projected(sizes, retired), 1)
            if not memory_counted:
                # A counter that read nothing: no peak of this table is
                # recorded, lined or projected (LANE SV RULINGS 3 (2)(b)).
                found[f"{kind}_validate_peak_withheld"] = "a memory counter read nothing"
                continue
            found[f"{kind}_validate_peak_mb"] = [round(peak, 1) for peak in peaks]
            if fitted and imports_counted:
                at_fitted = [peak for size, peak in zip(sizes, peaks) if size in fitted]
                _growth, at = kpi_describe_groups.projected(fitted[-3:], at_fitted[-3:], imports)
                found[f"{kind}_validate_peak_mb_2m_projected"] = round(at, 1)
                validate_keys[f"{kind}_validate_peak_mb_2m"] = round(at, 1)
            else:
                found[f"{kind}_validate_peak_mb_2m_lines"] = lines(sizes, peaks)
    found["files_compared"] = compared
    found["files_equal"] = equal
    found["equal_files_ratio"] = round(equal / compared, 3) if compared else 0.0
    return found, validate_keys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("action", nargs="?", default="")
    parser.add_argument("rest", nargs="*")
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--group-bytes", type=int, default=0)
    parser.add_argument("--walk-bytes", type=int, default=0)
    parser.add_argument("--trace", action="store_true")
    arguments = parser.parse_args()
    if arguments.action == "run":
        description, twin, out = arguments.rest
        print(json.dumps(run(description, twin, pathlib.Path(out), arguments.group_bytes, arguments.walk_bytes, arguments.trace)))
        return 0
    if arguments.action == "imports":
        print(json.dumps(imports_only()))
        return 0
    if arguments.action in ("write", "describe", "generate"):
        kind, rows, folder = arguments.rest
        print(json.dumps(step(arguments.action, kind, int(rows), pathlib.Path(folder))))
        return 0
    if not arguments.kpi:
        print(__doc__)
        return 0
    kpi_rules.guard_this_tree()
    sizes = sizes_asked()
    found, validate_keys = measure(sizes, os.environ.get("SV_KPI_KEEP", ""))
    detail = (
        "B0's two made-up tables, 50 columns, each size described, twinned at seed 0 and its twin validated in the "
        "groups 2,000,000 rows are read in, each size's peak the largest of three runs; "
        + ("the peak projected as lane B0 projects from the three largest sizes of 100,000 rows or more" if validate_keys else
           "the peak NOT projected (fewer than three sizes of 100,000 rows or more reaching 1,000,000, or a memory "
           "counter that read nothing): the lines through each two sizes recorded where the counter read")
    )
    kpi_rules.emit("K-S4-23", found, detail)
    if validate_keys:
        # K-S4-09's validate keys are measured by K-S4-09's rule only from
        # sizes reaching 1,000,000 rows, each the largest of three runs.
        kpi_rules.emit("K-S4-09", validate_keys, detail)
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""The inside record at scale: `synthtwin profile` and `synthtwin generate` of an invented table, their time, memory and record size.

LANE IN-8 (plan P4-D502). The inside record (plan P4-D495) is written by
`synthtwin profile` once the description is written, and `synthtwin
generate` draws the twin from it. This driver measures both steps on an
invented table of N rows by C columns -- the owner's reference is
2,000,000 rows by 50 columns, in 12 to 18 hours and under the 8 GB a
process the protected computer is given -- and prints, a step a line, the
seconds, the CPU seconds, the process's peak resident memory, the seconds
of the inside record's own parts and the record's size, never a cell.

    kpi_inside_scale.py write SHAPE ROWS COLUMNS PATH
    kpi_inside_scale.py profile SHAPE TABLE WORK [--trace]
    kpi_inside_scale.py generate WORK [--trace]
    kpi_inside_scale.py run --shape SHAPE --rows N [--columns C] --work DIR [--trace STEPS] [--keep] [--layer]
                            [--results FILE]
    kpi_inside_scale.py project FILE [FILE ...]

`run` writes the table, describes it and generates its twin, each step
in a process of its own (so each step's peak is its own), with the
installation's data folder in a folder of the run's own inside DIR: the
record is written only outside a temporary folder (`inside.place_refusal`),
so DIR is a folder of the person's own disk, never a temporary or a
synchronised one. Each step prints one line of JSON starting `RESULT `;
`--results FILE` appends those lines to FILE. `--trace profile,generate`
(either or both) also reads, in the steps named, the most bytes
`tracemalloc` saw held by the inside record's own parts (the profile
hook; the draw, the dates and the trajectories of generate), above what
the process held before each: machine-free, so it is judged anywhere,
and slower (the profile's fit about three times); generate is then run
twice, untraced for its seconds and traced (`generate-traced`).
`--layer` switches the patient layer on in each step's process (it is
off in the shipped command), so the trajectories zone is written and
applied and its own seconds and peak are read too. `--keep` keeps the table, the description and the twin
(deleted otherwise, as soon as the step that reads them ends).

`project` reads such lines and admits only a step that measured the inside
route (`admitted`: a profile that wrote a record, a generate whose twin
was drawn from one; batch 4x's outside review, item 14), saying how many
it refused, and projects each measure of each shape and
step to 2,000,000 rows by a least-squares straight line through the sizes
measured (value = a + b rows: a step's fixed part and its part a row),
and prints beside it the growth a doubling over the largest sizes (as
lane B0 reads it). The relations' fit reads at most
`inside_relations.SAMPLE_CAP` rows, so a profile's seconds are projected
as the fit's seconds at the largest size at or past that cap, held, plus
the line through the rest.

THE SHAPES, invented here, none from a real table:

* `dense`: C columns (12 or more): `pid`, a person's key, about five
  rows a person (one to twenty); `visit_start`, a date and time whose
  weekday and clock carry a pattern (few weekend starts, a 07:30 first
  slot, quarter hours), and `visit_end`, its end a duration after it by
  the first label's level; five yes/no flags (`f0` constant within a
  person); labels of five levels moved by the flags; numbers of one
  decimal, each a curve of the two before it, a flag, a label and their
  interaction, a person's share and noise, about 2 per cent empty; two
  short notes; `code`, a record number of every row.
* `wide302`: the health zoo's wide export (`health_zoo_wide.wide_export`):
  a key a row, a date and 300 items of the same labels, 302 columns.

WHAT IS PRINTED: seconds, peaks, counts of columns and the bytes of the
record and of each of its zones. Nothing of a cell, of the description
or of the record's content: the screen text of each command is read
into memory and dropped, never printed.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import time
import tracemalloc

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

SHAPES = ("dense", "wide302")
BIG_ROWS = 2_000_000
MEBIBYTE = 1024 * 1024
PREFIX = "RESULT "
EPOCH_YEAR = 2031
# The run's own data folder, handed to each step's process: the guard above
# points every process at a temporary one, where no record is written.
DATA_VARIABLE = "KPI_INSIDE_DATA"
if os.environ.get(DATA_VARIABLE):
    for _name in kpi_rules.DATA_FOLDER_NAMES:
        os.environ[_name] = os.environ[DATA_VARIABLE]
LAYER_VARIABLE = "KPI_INSIDE_LAYER"


def _layer() -> None:
    """The patient layer switched on in this process where the run asked for it (`--layer`)."""
    if os.environ.get(LAYER_VARIABLE):
        from synthtwin import cli

        cli._PATIENT_LAYER_SHIPPED = True


# -- the invented tables ---------------------------------------------------------------------------------


def _day_text(day: int) -> str:
    """Day ``day`` after the first of January of `EPOCH_YEAR`, as YYYY-MM-DD."""
    import datetime

    return (datetime.date(EPOCH_YEAR, 1, 1) + datetime.timedelta(days=day)).isoformat()


def _stamp(day: int, minute: int) -> str:
    return f"{_day_text(day + minute // 1440)} {(minute % 1440) // 60:02d}:{minute % 60:02d}"


def _weekday(day: int) -> int:
    """0 Monday to 6 Sunday of day ``day`` after the first of January of `EPOCH_YEAR` (a Wednesday)."""
    return (day + 2) % 7


def dense_names(columns: int) -> "list[str]":
    """The `dense` shape's column names, ``columns`` of them (12 or more)."""
    if columns < 12:
        raise SystemExit("the dense shape holds 12 columns or more")
    labels = (columns - 11) * 2 // 5
    numbers = columns - 11 - labels
    return (["pid", "visit_start", "visit_end"] + [f"f{k}" for k in range(5)]
            + [f"g{k:02d}" for k in range(labels)] + [f"n{k:02d}" for k in range(numbers)]
            + ["note_a", "note_b", "code"])


def write_dense(rows: int, columns: int, path: pathlib.Path) -> None:
    """The `dense` shape, ``rows`` rows by ``columns`` columns, from one seeded stream."""
    names = dense_names(columns)
    labels = sum(1 for name in names if name[0] == "g")
    numbers = sum(1 for name in names if name[0] == "n" and name[1:].isdigit())
    draw = random.Random(f"dense-{rows}-{columns}")
    person, left, day, f0, share = 0, 0, 0, False, 0.0
    with open(path, "w", encoding="utf-8", newline="\n") as out:
        out.write(",".join(names) + "\n")
        for row in range(rows):
            if left == 0:
                person += 1
                left = 1 + min(19, int(draw.expovariate(0.25)))
                day = draw.randrange(1400)
                f0 = draw.random() < 0.45
                share = draw.gauss(0.0, 4.0)
            else:
                day += 7 + int(draw.expovariate(1.0 / 21.0))
            left -= 1
            if _weekday(day) >= 5 and draw.random() < 0.8:
                day += 7 - _weekday(day)
            start = 450 if draw.random() < 0.13 else 480 + 15 * draw.randrange(40)
            f = [f0] + [draw.random() < 0.2 + 0.1 * k for k in range(1, 5)]
            g: "list[str]" = []
            for k in range(labels):
                shift = 0.25 if f[k % 5] else 0.0
                u = draw.random()
                g += ["A" if u < 0.15 + shift else "B" if u < 0.45 + shift / 2 else "C" if u < 0.7 else "D" if u < 0.9 else "E"]
            n: "list[float]" = []
            for k in range(numbers):
                prev = n[k - 1] - 50.0 if k else 0.0
                prev2 = n[k - 2] - 50.0 if k > 1 else 0.0
                n += [50.0 + 0.5 * prev + 4.0 * f[k % 5] + 0.02 * prev2 * prev2 + 3.0 * (g[k % labels] == "A")
                      + 3.0 * (f[k % 5] and g[k % labels] == "B") + (share if k % 3 == 0 else 0.0) + draw.gauss(0.0, 8.0)]
            length = {"A": 35, "B": 60, "C": 90, "D": 120, "E": 240}[g[0]] + int(draw.expovariate(1.0 / 20.0))
            cells = [f"P{1000000 + 7 * person}", _stamp(day, start), _stamp(day, start + length)]
            cells += ["Y" if x else "N" for x in f] + g
            cells += ["" if draw.random() < 0.02 else f"{x:.1f}" for x in n]
            cells += [f"review in {draw.randint(1, 60)} days" if draw.random() < 0.3 else "no change",
                      draw.choice(["stable", "improving", "worse"]), f"C{100000 + 13 * row}"]
            out.write(",".join(cells) + "\n")


def write_wide302(rows: int, path: pathlib.Path) -> None:
    """The `wide302` shape: the health zoo's wide export of ``rows`` rows, 302 columns."""
    import csv

    import health_zoo_wide

    header, body = health_zoo_wide.wide_export(rows, 20261118)
    with open(path, "w", encoding="utf-8", newline="") as out:
        writer = csv.writer(out, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(body)


def write(shape: str, rows: int, columns: int, path: pathlib.Path) -> None:
    if shape == "dense":
        write_dense(rows, columns, path)
    elif shape == "wide302":
        write_wide302(rows, path)
    else:
        raise SystemExit(f"no shape {shape!r}; the shapes are {', '.join(SHAPES)}")


# -- measuring one step in this process ------------------------------------------------------------------


def _peak_rss_mb() -> float:
    """This process's peak resident memory in MiB (-1 where it cannot be read, as on Windows)."""
    try:
        import resource
    except ImportError:
        return -1.0
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round((peak if sys.platform == "darwin" else peak * 1024) / MEBIBYTE, 1)


class Clock:
    """Seconds and, under --trace, the traced peak above the start, for each function wrapped; the outermost traced alone."""

    def __init__(self, trace: bool) -> None:
        self.trace = trace
        self.seconds: "dict[str, float]" = {}
        self.traced_mb: "dict[str, float]" = {}
        self.calls: "dict[str, int]" = {}
        self._depth = 0

    def wrap(self, owner: object, name: str, traced: bool = False) -> None:
        original = getattr(owner, name)
        clock = self

        def timed(*args: object, **kwargs: object) -> object:
            tracing = clock.trace and traced and clock._depth == 0
            if tracing:
                tracemalloc.start()
                clock._depth += 1
            started = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                clock.seconds[name] = round(clock.seconds.get(name, 0.0) + time.perf_counter() - started, 2)
                clock.calls[name] = clock.calls.get(name, 0) + 1
                if tracing:
                    peak = tracemalloc.get_traced_memory()[1]
                    tracemalloc.stop()
                    clock._depth -= 1
                    clock.traced_mb[name] = round(max(clock.traced_mb.get(name, 0.0), peak / MEBIBYTE), 1)

        setattr(owner, name, timed)


def _answered(questions: pathlib.Path) -> int:
    """Writes an answer to every open question of a questions file (the first offered of a fixed list); how many."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    wrote = 0
    entries: "list[object]" = []
    for key in ("about_your_file", "asked"):
        entries += list(document.get(key) or [])
    checklist = document.get("checklist")
    if isinstance(checklist, dict):
        entries += list(checklist.get("columns") or [])
    for entry in entries:
        if isinstance(entry, dict) and "answers_you_can_give" in entry and not entry.get("your_answer"):
            offered = [str(a.get("answer")) for a in entry["answers_you_can_give"] if isinstance(a, dict)]
            for pick in ("keep", "no", "measurement", "code", "label"):
                if pick in offered:
                    entry["your_answer"] = pick
                    wrote += 1
                    break
    between = document.get("between_columns")
    asked = between.get("rows_per_person") if isinstance(between, dict) else None
    if isinstance(asked, dict) and not asked.get("your_answer"):
        asked["your_answer"] = "several rows each"
        wrote += 1
    questions.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return wrote


def _quiet(argv: "list[str]") -> int:
    """`synthtwin` ARGV in this process, its screen read and dropped; the exit code."""
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return int(code)


def _records(data: pathlib.Path) -> "list[pathlib.Path]":
    from synthtwin import inside

    return sorted(pathlib.Path(data, kpi_rules.INSTALLATION_FOLDER, inside.FOLDER).glob(f"*{inside.SUFFIX}"))


def _zone_bytes(path: pathlib.Path) -> "dict[str, int]":
    """Each zone's bytes in the record's own serialisation; nothing of the content."""
    from synthtwin import inside

    record = inside.load_record(path)
    zones = record["zones"]
    out: "dict[str, int]" = {}
    if isinstance(zones, dict):
        for name in sorted(zones):
            body = json.dumps(zones[name], ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
            out[str(name)] = len(body.encode("utf-8"))
    return out


def _declarations(shape: str) -> "list[str]":
    if shape == "dense":
        return ["--person", "pid", "--identifier", "code"]
    return ["--identifier", "patient_ref"]


def profile_step(shape: str, table: pathlib.Path, work: pathlib.Path, trace: bool) -> "dict[str, object]":
    """`synthtwin profile` of ``table`` with its answers' rounds, in this process; what it took."""
    from synthtwin import cli, inside_dates, inside_relations

    _layer()
    clock = Clock(trace)
    clock.wrap(cli, "_inside_record_written", traced=True)
    clock.wrap(cli, "_inside_trajectories", traced=True)
    clock.wrap(inside_relations, "fit_zone")
    for name in ("build_zone", "zone_of", "take_column"):
        if hasattr(inside_dates, name):
            clock.wrap(inside_dates, name)
    out = pathlib.Path(work, "out")
    out.mkdir(exist_ok=True)
    argv = ["profile", str(table), "--out-dir", str(out), "--replace", *_declarations(shape)]
    started, cpu = time.perf_counter(), time.process_time()
    code = _quiet(argv)
    rounds = 1
    questions = pathlib.Path(out, f"{table.stem}-questions.json")
    while code != 0 and rounds < 4 and questions.exists() and _answered(questions):
        code = _quiet(argv + ["--answers", str(questions)])
        rounds += 1
    data = pathlib.Path(os.environ["XDG_DATA_HOME"])
    found = _records(data)
    return {
        "step": "profile", "exit": code, "rounds": rounds,
        "seconds": round(time.perf_counter() - started, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
        "peak_rss_mb": _peak_rss_mb(), "inside_seconds": clock.seconds, "inside_traced_mb": clock.traced_mb,
        "record_bytes": found[0].stat().st_size if found else 0, "records": len(found),
        "zone_bytes": _zone_bytes(found[0]) if found else {},
    }


def generate_step(work: pathlib.Path, trace: bool) -> "dict[str, object]":
    """`synthtwin generate` of the description in WORK/out, in this process; what it took."""
    from synthtwin import generation, inside_dates, inside_relations, inside_trajectories

    _layer()
    clock = Clock(trace)
    clock.wrap(generation, "generate_held")
    clock.wrap(inside_relations, "draw_columns", traced=True)
    for name in ("write_dates", "write_dates_held"):
        if hasattr(inside_dates, name):
            clock.wrap(inside_dates, name, traced=True)
    clock.wrap(inside_trajectories, "twin_with_zone", traced=True)
    out = pathlib.Path(work, "out")
    described = sorted(out.glob("*-profile.json"))
    if not described:
        return {"step": "generate", "exit": -1}
    started, cpu = time.perf_counter(), time.process_time()
    code = _quiet(["generate", str(described[0]), "--out-dir", str(out), "--seed", "1", "--replace"])
    reports = sorted(out.glob("*-twin-report.txt"))
    head = reports[0].read_text(encoding="utf-8").split("\n")[:2] if reports else []
    drawn = 0
    if len(head) == 2 and head[0].startswith("THIS TWIN WAS DRAWN") and head[1].startswith("These "):
        drawn = int(head[1].split(" ")[1])
    return {
        "step": "generate", "exit": code,
        "seconds": round(time.perf_counter() - started, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
        "peak_rss_mb": _peak_rss_mb(), "inside_seconds": clock.seconds, "inside_traced_mb": clock.traced_mb,
        "drawn_columns": drawn,
    }


def baseline_step() -> "dict[str, object]":
    """What the process holds once synthtwin and its readers are imported."""
    from synthtwin import cli, generation, inside_dates, inside_relations, inside_trajectories, reading  # noqa: F401

    return {"step": "baseline", "peak_rss_mb": _peak_rss_mb()}


# -- the run: a process a step ---------------------------------------------------------------------------


def _child(arguments: "list[str]", env: "dict[str, str]") -> "dict[str, object]":
    """One step of this driver in a process of its own; its RESULT line, or what went wrong."""
    done = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), *arguments],
                          env=env, capture_output=True, text=True, check=False)
    for line in done.stdout.splitlines():
        if line.startswith(PREFIX):
            return dict(json.loads(line[len(PREFIX):]))
    return {"step": arguments[0], "exit": done.returncode, "error": "no RESULT line"}


def run(shape: str, rows: int, columns: int, work: pathlib.Path, trace: "tuple[str, ...]", keep: bool,
        results: "pathlib.Path | None", layer: bool = False) -> None:
    if shape == "wide302":
        columns = 302
    work.mkdir(parents=True, exist_ok=True)
    place = kpi_rules.fresh_data_folder(work)
    env = dict(os.environ)
    for name in kpi_rules.DATA_FOLDER_NAMES:
        env[name] = str(place)
    env[DATA_VARIABLE] = str(place)
    if layer:
        env[LAYER_VARIABLE] = "1"
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT / "src"), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    stem = f"{shape}-{rows}x{columns}"
    folder = pathlib.Path(work, stem)
    shutil.rmtree(folder, ignore_errors=True)
    pathlib.Path(folder, "table").mkdir(parents=True)
    table = pathlib.Path(folder, "table", f"{shape}.csv")
    said: "list[dict[str, object]]" = []
    try:
        started = time.perf_counter()
        write(shape, rows, columns, table)
        said += [{"step": "write", "seconds": round(time.perf_counter() - started, 1),
                  "table_bytes": table.stat().st_size}]
        said += [_child(["baseline"], env)]
        said += [_child(["profile", shape, str(table), str(folder)] + (["--trace"] if "profile" in trace else []), env)]
        if not keep:
            table.unlink()
        said += [_child(["generate", str(folder)], env)]
        if "generate" in trace:
            traced = _child(["generate", str(folder), "--trace"], env)
            traced["step"] = "generate-traced"
            said += [traced]
    finally:
        if not keep:
            shutil.rmtree(folder, ignore_errors=True)
            shutil.rmtree(place, ignore_errors=True)
    for line in said:
        line.update({"shape": shape + ("+layer" if layer else ""), "rows": rows, "columns": columns})
        text = PREFIX + json.dumps(line, sort_keys=True)
        print(text, flush=True)
        if results is not None:
            with open(results, "a", encoding="utf-8") as out:
                out.write(text + "\n")


# -- the projection ---------------------------------------------------------------------------------------


def _line(points: "list[tuple[float, float]]") -> "tuple[float, float]":
    """Least squares of value on rows: the intercept and the slope (a step's fixed part and its part a row)."""
    xs = [x for x, _y in points]
    ys = [y for _x, y in points]
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    sxx = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
    return mean_y - slope * mean_x, slope


def projected(points: "list[tuple[float, float]]", rows: int = BIG_ROWS) -> "dict[str, float]":
    """The value at ``rows`` on the straight line through the sizes measured, and the growth a doubling of the two largest."""
    kept = sorted(points)
    if len(kept) < 2:
        return {}
    intercept, slope = _line(kept)
    (x1, y1), (x2, y2) = kept[-2], kept[-1]
    growth = math.exp(math.log(y2 / y1) * math.log(2.0) / math.log(x2 / x1)) if y1 > 0 and y2 > 0 and x2 > x1 else 0.0
    return {"at": round(intercept + slope * rows, 1), "growth_a_doubling": round(growth, 3), "sizes": len(kept)}


def _number_of(line: "dict[str, object]", key: str, part: str = "") -> float:
    value = line.get(key)
    if part:
        value = dict(value or {}).get(part, 0.0) if isinstance(value, dict) else 0.0
    return float(str(value)) if value is not None else 0.0


def admitted(line: "dict[str, object]") -> bool:
    """Whether a step's RESULT line measures the inside route and may enter a projection.

    Batch 4x's outside review, item 14: an exit of 0 alone is no evidence,
    for a run whose data folder the record's guard refuses (a temporary
    one) describes and generates as the description alone, with no record
    written and no column drawn. So a profile line is admitted only where
    it wrote an inside record (`records` and `record_bytes` above nought),
    and a generate line only where its twin's report names columns drawn
    from the record (`drawn_columns` above nought).
    """
    if line.get("exit") != 0:
        return False
    step = line.get("step")
    if step == "profile":
        return _number_of(line, "records") > 0 and _number_of(line, "record_bytes") > 0
    if step in ("generate", "generate-traced"):
        return _number_of(line, "drawn_columns") > 0
    return False


def project(files: "list[pathlib.Path]") -> None:
    from synthtwin import inside_relations

    lines: "list[dict[str, object]]" = []
    for path in files:
        for text in path.read_text(encoding="utf-8").splitlines():
            if text.startswith(PREFIX):
                lines += [dict(json.loads(text[len(PREFIX):]))]
    keys: "dict[tuple[str, int, str], dict[int, dict[str, object]]]" = {}
    refused = 0
    for line in lines:
        if line.get("step") not in ("profile", "generate", "generate-traced"):
            continue
        if not admitted(line):
            refused += 1
            continue
        found = keys.setdefault((str(line["shape"]), int(str(line["columns"])), str(line["step"])), {})
        found[int(str(line["rows"]))] = line
    if refused:
        print(f"REFUSED {refused} step line(s): an exit other than 0, or no inside record written or drawn from "
              "(a data folder the record's guard refuses); they enter no projection.", flush=True)
    for (shape, columns, step), by_rows in sorted(keys.items()):
        found = [by_rows[rows] for rows in sorted(by_rows)]
        sizes = [float(rows) for rows in sorted(by_rows)]
        out: "dict[str, object]" = {"shape": shape, "columns": columns, "step": step, "rows_measured": sorted(by_rows)}
        for measure in ("seconds", "cpu_seconds", "peak_rss_mb"):
            out[measure] = projected([(x, _number_of(line, measure)) for x, line in zip(sizes, found)])
        for kind in ("inside_seconds", "inside_traced_mb"):
            parts: "dict[str, object]" = {}
            for line in found:
                for part in dict(line.get(kind) or {}):
                    parts[part] = projected([(x, _number_of(each, kind, part)) for x, each in zip(sizes, found)])
            out[kind] = parts
        if step == "profile":
            capped = [(x, line) for x, line in zip(sizes, found) if x >= inside_relations.SAMPLE_CAP]
            if capped:
                fit = _number_of(capped[-1][1], "inside_seconds", "fit_zone")
                rest = projected([(x, _number_of(line, "seconds") - _number_of(line, "inside_seconds", "fit_zone"))
                                  for x, line in zip(sizes, found)])
                out["seconds_fit_held"] = {"fit_seconds": fit, "rest_at": rest.get("at", 0.0),
                                           "at": round(fit + float(rest.get("at", 0.0)), 1)}
            out["record_bytes"] = {str(int(x)): line.get("record_bytes") for x, line in zip(sizes, found)}
        print("PROJECTED " + json.dumps(out, sort_keys=True), flush=True)


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(prog="kpi_inside_scale.py")
    steps = parser.add_subparsers(dest="command", required=True)
    one = steps.add_parser("write")
    one.add_argument("shape", choices=SHAPES)
    one.add_argument("rows", type=int)
    one.add_argument("columns", type=int)
    one.add_argument("path")
    one = steps.add_parser("profile")
    one.add_argument("shape", choices=SHAPES)
    one.add_argument("table")
    one.add_argument("work")
    one.add_argument("--trace", action="store_true")
    one = steps.add_parser("generate")
    one.add_argument("work")
    one.add_argument("--trace", action="store_true")
    steps.add_parser("baseline")
    one = steps.add_parser("run")
    one.add_argument("--shape", choices=SHAPES, default="dense")
    one.add_argument("--rows", type=int, required=True)
    one.add_argument("--columns", type=int, default=50)
    one.add_argument("--work", required=True)
    one.add_argument("--trace", default="")
    one.add_argument("--keep", action="store_true")
    one.add_argument("--layer", action="store_true")
    one.add_argument("--results")
    one = steps.add_parser("project")
    one.add_argument("files", nargs="+")
    given = parser.parse_args(argv)
    if given.command == "write":
        write(given.shape, given.rows, given.columns, pathlib.Path(given.path))
    elif given.command == "profile":
        print(PREFIX + json.dumps(profile_step(given.shape, pathlib.Path(given.table), pathlib.Path(given.work),
                                               given.trace), sort_keys=True), flush=True)
    elif given.command == "generate":
        print(PREFIX + json.dumps(generate_step(pathlib.Path(given.work), given.trace), sort_keys=True), flush=True)
    elif given.command == "baseline":
        print(PREFIX + json.dumps(baseline_step(), sort_keys=True), flush=True)
    elif given.command == "run":
        run(given.shape, given.rows, given.columns, pathlib.Path(given.work), tuple(given.trace.split(",")), given.keep,
            pathlib.Path(given.results) if given.results else None, given.layer)
    else:
        project([pathlib.Path(name) for name in given.files])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

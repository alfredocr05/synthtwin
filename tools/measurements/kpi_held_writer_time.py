"""K-HZ-40: the held writer's time (plan P4-D490, lane HB3-b part a).

The tables are `tests/held_writer_tables.py`'s, invented. Each run goes
through the commands a person types (`synthtwin profile`, the person
column answered `identifier`, profile again, `generate` seed 0,
`validate`) in this process, and every second is CPU seconds, user plus
system, of `generate` alone:

- the exam column (120 names, each drawn on about a 120th of the rows,
  held unanswered) at 20,000, 40,000, 80,000, 100,000, 160,000 and 200,000
  rows, the same after `yes` at 20,000, and the equal and long-tailed
  controls at 20,000: `exam_20000_generate_cpu` (bound 60), the largest
  ratio of one doubling's seconds to the size half of it -- 20,000 to
  40,000, 40,000 to 80,000, 80,000 to 160,000 and 100,000 to 200,000
  (`exam_doubling_ratio_most`, bound 2.5: linear within 25 per cent) --
  and `exam_200000_generate_cpu`;
- the rare exam column (`rare_exam_rows`: 150 rare names beside the 120,
  whose exact walk of 6,514 steps sets the meter, LANE HB3-b RULINGS 4
  (1)) and the wide exam column (`wide_exam_rows`: 240 names in 27
  layouts, drawn) at 20,000 rows, held unanswered: their rung, layouts
  filed short and validate's exit (`rare_exam_*`, `wide_exam_*`);
- the held list (one to three of 40 keys a cell, declared `--identifier`)
  at 5,000, 10,000 and 20,000 rows, its seconds and its own doubling
  ratio recorded (`held_list_*`; its growth is part b's, stated in
  P4-D490); and the blocks table (LANE HB3-b RULINGS 2's measured cliff,
  lane CZ-F's table: 5,496 values in 244 layouts at 49,152 rows) at
  20,004 and 49,152 rows, declared `--identifier` (`blocks_*`) and with
  its identifier question left open (`blocks_open_*`, LANE HB3-b RULINGS
  4 (2)), the rung, layouts filed and validate's exit of each at 49,152
  rows recorded;
- on every run: the layout pass's walk steps and work (the most any
  column took, `walk_steps_most` and `walk_work_most`, at most
  `generation._LAYOUT_WALK_STEPS` and `_LAYOUT_WALK_WORK`), the rung each
  held column ended on (1 the walk, 2 the re-packing allocator, and 3 the
  nearest assignment or the first answer, filed), the layouts filed short
  (`layouts_filed_short`), validate's exit, and the twin cells equal to a
  real cell of the column (`real_cells_equal`, target 0);
- the generated checks of the gate file, larger: 6,000 equality questions,
  6,000 re-packing questions, 200 invariant columns of record numbers and
  100 held label columns, each label column profiled with its question
  open or answered `yes` and generated three times, about 8 CPU s a
  column (`generated_failures`, target 0; the re-packing's exact share
  recorded).

`--large` instead runs, in a measurement window and apart from the KPI,
the held list at 30,000 rows, then one held names column (`names_rows`,
20,000 surnames) and the long-tailed exam column at 2,000,000 rows:
generate's CPU seconds and peak, the rung and the layouts filed short (the
fidelity cost of rung 3, P4-D490).

Everything is linear in the cells save the generated checks, which are
fixed counts. About 45 CPU minutes at the floor and 200,000 rows on the
reference machine, one process under 500 MB.

    .venv/bin/python tools/measurements/kpi_held_writer_time.py --kpi
"""

import contextlib
import csv
import io
import json
import pathlib
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
from synthtwin import cli, generation, parsing  # noqa: E402
import held_writer_tables as tables  # noqa: E402

# A fragment of the third rung's cause as the twin's report prints it.
FILED = " ".join(generation._LAYOUT_PASS_STOPPED.split()[:9])


def _cpu() -> float:
    """This process's CPU seconds, user plus system, on every platform."""
    return time.process_time()


def _peak_megabytes() -> "float | None":
    """This process's peak resident memory in MB where the platform reports it (POSIX), else None.

    `resource` is a POSIX module, so it is imported here, where Windows's
    ImportError is answered, and never at module level (Codex's review of
    lane HB3-b, item 3).
    """
    try:
        import resource
    except ImportError:
        return None
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(peak / (1_000_000 if sys.platform == "darwin" else 1000), 1)


def _quietly(arguments: "list[str]") -> int:
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        return cli.main(arguments, small_tables_refused=False)


def run(folder: pathlib.Path, kind: str, rows: int, answer: str = "", **made: object) -> "dict[str, object]":
    """One table through the commands, measured (see the module's text)."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "t.csv"
    if kind == "exam":
        header, body = tables.exam_rows(rows, spread=str(made.get("spread", "drawn")))
        column, declared = "exam", []
    elif kind == "list":
        header, body = tables.held_list_rows(rows)
        column, declared = "registers", ["--identifier", "registers"]
    elif kind == "blocks":
        header, body = tables.blocks_rows(rows)
        column, declared = "label_text", ["--identifier", "label_text"]
    elif kind == "blocks_open":
        header, body = tables.blocks_rows(rows)
        column, declared = "label_text", []
    elif kind == "rare":
        header, body = tables.rare_exam_rows(rows)
        column, declared = "exam", []
    elif kind == "wide":
        header, body = tables.wide_exam_rows(rows, spread=str(made.get("spread", "drawn")))
        column, declared = "exam", []
    else:
        header, body = tables.names_rows(rows, int(str(made.get("values", 20000))))
        column, declared = "surname", []
    tables.write_csv(source, header, body)
    out = ["--out-dir", str(folder), "--replace"]
    assert _quietly(["profile", str(source), *out, *declared]) == 0
    questions = folder / "t-questions.json"
    answers = {"person_id": "identifier", column: answer} if declared == [] else {}
    document = json.loads(questions.read_text(encoding="utf-8"))
    changed = False
    for entry in document.get("asked", []):
        if answers.get(entry.get("column")):
            entry["your_answer"] = answers[entry["column"]]
            changed = True
    if changed:
        questions.write_text(json.dumps(document), encoding="utf-8")
        assert _quietly(["profile", str(source), *out, *declared, "--answers", str(questions)]) == 0
    meters: "list[list[int]]" = []
    making = generation._layout_meter

    def kept(*given: int) -> "list[int]":
        meter = making(*given)
        meters.append(meter)
        return meter

    generation._layout_meter = kept  # type: ignore[assignment]
    started = _cpu()
    try:
        generated = _quietly(["generate", str(folder / "t-profile.json"), *out, "--seed", "0"])
    finally:
        generation._layout_meter = making  # type: ignore[assignment]
    seconds = round(_cpu() - started, 1)
    report = " ".join((folder / "t-twin-report.txt").read_text(encoding="utf-8").split())
    filed = report.count(FILED)
    validated = _quietly(["validate", str(folder / "t-profile.json"), "--twin", str(folder / "t-twin.csv"), *out])
    with open(source, encoding="utf-8", newline="") as handle:
        real = {row[column] for row in csv.DictReader(handle)}
    keys = {str(parsing.merged_key(parsing.trimmed(value))) for value in real}
    folded = {value.casefold() for value in real}
    equal = 0
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            cell = row[column]
            if cell and (cell in real or cell.casefold() in folded
                         or str(parsing.merged_key(parsing.trimmed(cell))) in keys):
                equal += 1
    steps = max([generation._LAYOUT_WALK_STEPS - meter[0] for meter in meters] or [0])
    work = max([generation._LAYOUT_WALK_WORK - meter[2] for meter in meters] or [0])
    stopped = any(meter[1] for meter in meters)
    short = any(meter[4] for meter in meters)
    for written in folder.glob("*"):
        written.unlink()
    return {"kind": kind, "rows": rows, "answer": answer, "spread": str(made.get("spread", "")),
            "generate": generated, "seconds": seconds, "steps": steps, "work": work,
            "rung": 1 if not stopped else (3 if short or filed else 2), "filed": filed,
            "validate": validated, "equal": equal}


def _ratio_most(seconds: "list[float]") -> float:
    """The largest ratio of one size's seconds to the size half of it, over sizes that double."""
    return round(max([seconds[at] / max(seconds[at - 1], 0.1) for at in range(1, len(seconds))] or [0.0]), 2)


def kpi() -> None:
    value: "dict[str, object]" = {"real_cells_equal": 0, "layouts_filed_short": 0, "walk_steps_most": 0,
                                  "walk_work_most": 0, "held_twins_failing_validation_unfiled": 0,
                                  "generated_failures": 0}
    lines: "list[str]" = []
    results: "list[dict[str, object]]" = []
    with tempfile.TemporaryDirectory() as scratch:
        home = pathlib.Path(scratch)
        plan = [("exam", rows, "", "drawn") for rows in (20000, 40000, 80000, 100000, 160000, 200000)]
        plan += [("exam", 20000, "yes", "drawn"), ("exam", 20000, "", "equal"), ("exam", 20000, "", "long-tailed")]
        plan += [("rare", 20000, "", "drawn"), ("wide", 20000, "", "drawn")]
        plan += [("list", rows, "", "") for rows in (5000, 10000, 20000)]
        plan += [("blocks", rows, "", "") for rows in (20004, 49152)]
        plan += [("blocks_open", rows, "", "") for rows in (20004, 49152)]
        for kind, rows, answer, spread in plan:
            began = _cpu()
            seen = run(home / f"{kind}-{rows}-{answer}-{spread}", kind, rows, answer, spread=spread)
            results += [seen]
            lines += [f"{kind} {spread} {rows} rows {answer or 'unanswered'} ({_cpu() - began:.0f} CPU s in all): "
                      f"generate {seen['generate']} "
                      f"{seen['seconds']} CPU s, walk {seen['steps']} steps {seen['work']} work, rung {seen['rung']}, "
                      f"{seen['filed']} layouts filed, validate {seen['validate']}, {seen['equal']} real cells"]
            value["real_cells_equal"] = int(str(value["real_cells_equal"])) + int(str(seen["equal"]))
            value["layouts_filed_short"] = int(str(value["layouts_filed_short"])) + int(str(seen["filed"]))
            value["walk_steps_most"] = max(int(str(value["walk_steps_most"])), int(str(seen["steps"])))
            value["walk_work_most"] = max(int(str(value["walk_work_most"])), int(str(seen["work"])))
            if kind in ("rare", "wide"):
                value[f"{kind}_exam_rung"] = seen["rung"]
                value[f"{kind}_exam_layouts_filed_short"] = seen["filed"]
                value[f"{kind}_exam_validate"] = seen["validate"]
            if kind in ("blocks", "blocks_open") and rows == 49152:
                value[f"{kind}_49152_rung"] = seen["rung"]
                value[f"{kind}_49152_layouts_filed_short"] = seen["filed"]
                value[f"{kind}_49152_validate"] = seen["validate"]
            if seen["validate"] != 0 and not seen["filed"] and kind in ("exam", "rare", "wide"):
                value["held_twins_failing_validation_unfiled"] = int(str(value["held_twins_failing_validation_unfiled"])) + 1

    def seconds_of(kind: str, sizes: "tuple[int, ...]", answer: str = "", spread: str = "drawn") -> "list[float]":
        return [float(str(r["seconds"])) for size in sizes for r in results
                if r["kind"] == kind and r["rows"] == size and r["answer"] == answer
                and (kind != "exam" or r["spread"] == spread)][: len(sizes)]

    exam = seconds_of("exam", (20000, 40000, 80000, 160000))
    value["exam_20000_generate_cpu"] = exam[0]
    value["exam_doubling_ratio_most"] = max(_ratio_most(exam), _ratio_most(seconds_of("exam", (100000, 200000))))
    value["exam_200000_generate_cpu"] = seconds_of("exam", (200000,))[0]
    held = seconds_of("list", (5000, 10000, 20000))
    for size, seconds in zip((5000, 10000, 20000), held):
        value[f"held_list_{size}_generate_cpu"] = seconds
    value["held_list_doubling_ratio_most"] = _ratio_most(held)
    for size, seconds in zip((20004, 49152), seconds_of("blocks", (20004, 49152))):
        value[f"blocks_{size}_generate_cpu"] = seconds
    for size, seconds in zip((20004, 49152), seconds_of("blocks_open", (20004, 49152))):
        value[f"blocks_open_{size}_generate_cpu"] = seconds
    # THE GENERATED CHECKS, larger than the gate file's (`tests/test_held_writer_time.py`).
    import test_held_writer_time as gate
    from _pytest.monkeypatch import MonkeyPatch

    patched = MonkeyPatch()
    began = _cpu()
    try:
        failures, seen = gate._equality_failures(patched, gate.EQUALITY_METER, 6000)
        lines += [f"equality check: {len(failures)} failing of 6,000; {seen}"]
        value["generated_failures"] = int(str(value["generated_failures"])) + len(failures)
        patched.undo()
        failures, seen = gate._repacking_failures(6000)
        lines += [f"re-packing check: {len(failures)} failing of 6,000; {seen}"]
        value["generated_failures"] = int(str(value["generated_failures"])) + len(failures)
        value["repacking_exact_share"] = round(seen["exact"] / max(seen["answered"], 1), 3)
        with tempfile.TemporaryDirectory() as scratch:
            failures, seen = gate._invariant_failures(patched, pathlib.Path(scratch), 200, 100)
        lines += [f"invariant check: {len(failures)} failing of 200 columns and 100 held label columns; {seen}"]
        value["generated_failures"] = int(str(value["generated_failures"])) + len(failures)
    finally:
        patched.undo()
    lines += [f"the generated checks: {_cpu() - began:.0f} CPU s"]
    value["peak_megabytes"] = _peak_megabytes()
    for line in lines:
        print(line, flush=True)
    kpi_rules.emit("K-HZ-40", value, "the exam column at 20,000 to 200,000 rows, its controls, the held list "
                   "at 5,000 to 20,000 rows and the generated checks")


def large() -> None:
    """The 2,000,000-row columns, in a measurement window (see the module's text)."""
    with tempfile.TemporaryDirectory() as scratch:
        # The held list at 30,000 rows first: its growth is part b's (P4-D490 (a), (b)), measured here apart.
        seen = run(pathlib.Path(scratch) / "list", "list", 30000)
        print(f"list 30,000 rows: {json.dumps(seen)}, peak {_peak_megabytes()} MB", flush=True)
        for kind, spread in (("names", ""), ("exam", "long-tailed")):
            seen = run(pathlib.Path(scratch) / kind, kind, 2000000, spread=spread or "drawn")
            print(f"{kind} {spread} 2,000,000 rows: {json.dumps(seen)}, peak {_peak_megabytes()} MB", flush=True)


if __name__ == "__main__":
    if "--large" in sys.argv:
        large()
    else:
        kpi()

"""A table of 302 columns through every shipped step: the seconds, the memory, the questions and the relations found.

LANE W5-302. A health table exported at full width holds a few hundred
columns of every kind (`tests/wide_table.py`: a person's key, a record
number, dates and clock times, letters, codes, series over a person's
visits, measurements in a chain, counts, mostly empty columns, notes and
keys of other kinds, 302 columns). This driver writes that table at N
rows and runs on it every step a person runs inside the protected
computer, each step in a process of its own so each step's peak is its
own:

1. `synthtwin profile` with the person column named, round by round
   with the answers the table's holder gives (`tests/wide_table.holder_answer`), the inside record
   written on the shipped route;
2. `synthtwin generate`, the twin drawn from the record;
3. `synthtwin validate`, the twin measured against the description;
4. the five twin-versus-real checks (`python -m synthtwin.twin_checks`).

It prints, a step a line (`RESULT ` and one line of JSON), the step's
seconds, its CPU seconds, its peak resident memory and its exit code;
for profile also the questions put in each round (the entries that take
an answer, and of them the ones the first round puts), the seconds of the
inside record's own parts and the record's bytes; for the checks their
verdicts; and `relations`: for each relation `tests/wide_table.RELATIONS`
writes into the table, whether the response's fitted terms read its
parent (presence or value), and how many parents each modelled column's
fit took. Nothing of a cell is printed: screens are read into memory and
dropped. `--keyboard` runs the first profile round with a stand-in for a
person at the terminal who presses Enter at every prompt, and counts the
prompts (the questions a physician faces there). `--progress` lines (each
wrapped part's end, each stage of the chain, with the step's CPU seconds
and peak) are written to DIR/progress-N-sS.txt while a step runs.

    kpi_wide_table.py run --rows N --work DIR [--seed S] [--keep] [--results FILE] [--steps LIST] [--keyboard] [--rounds R] [--no-record]
    kpi_wide_table.py write ROWS PATH [--seed S]

DIR must be a folder of the person's own disk, never a temporary or a
synchronised one (`inside.place_refusal`). Every run at 20,000 rows or
more goes through the machine's memory guard.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

import wide_table as W  # noqa: E402

PREFIX = "RESULT "
MEBIBYTE = 1024 * 1024
DATA_VARIABLE = "KPI_WIDE_DATA"
SMALL_VARIABLE = "KPI_WIDE_UNDER_THE_FLOOR"
KEYBOARD_VARIABLE = "KPI_WIDE_KEYBOARD"
ROUNDS_VARIABLE = "KPI_WIDE_ROUNDS"
NO_RECORD_VARIABLE = "KPI_WIDE_NO_RECORD"


def _record_switch() -> None:
    """The inside record's sub-switch set off in this step's process where the run asked (`--no-record`): the
    description route alone, its every step measured where the record's own fit is too long to run here."""
    if os.environ.get(NO_RECORD_VARIABLE):
        from synthtwin import cli

        cli._INSIDE_RECORD_SHIPPED = False  # type: ignore[attr-defined]
# Prompts at most at the keyboard before the stand-in ends its input (a prompt that never takes Enter stops there).
PROMPTS_MOST = 2000
if os.environ.get(DATA_VARIABLE):
    for _name in kpi_rules.DATA_FOLDER_NAMES:
        os.environ[_name] = os.environ[DATA_VARIABLE]
STEPS = ("profile", "generate", "validate", "checks")
# The answered rounds after the first, at most (the reliability battery's `ROUNDS`).
ROUNDS = 4
TABLE = "wide.csv"


def _peak_rss_mb() -> float:
    try:
        import resource
    except ImportError:
        return -1.0
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round((peak if sys.platform == "darwin" else peak * 1024) / MEBIBYTE, 1)


def _quiet(argv: "list[str]") -> int:
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return int(code)


# -- the answers ---------------------------------------------------------------------------------------------


def _entries(document: object) -> "list[dict]":
    import reliability_battery as B

    return B._entries(document)


def answered(questions: pathlib.Path) -> "tuple[int, int, int]":
    """Answers every open question of a questions file; (entries taking an answer, open ones, answers written)."""
    import reliability_battery as B

    document = json.loads(questions.read_text(encoding="utf-8"))
    entries = _entries(document)
    open_ = [entry for entry in entries if not entry.get("your_answer")]
    wrote = 0
    for entry in open_:
        pick = W.holder_answer(str(entry.get("column", "")), B._offered(entry), B._asks_for_people(entry))
        if pick:
            entry["your_answer"] = pick
            wrote += 1
    between = document.get("between_columns") if isinstance(document, dict) else None
    asked = between.get("rows_per_person") if isinstance(between, dict) else None
    if isinstance(asked, dict) and not asked.get("your_answer"):
        asked["your_answer"] = W.PERSON
        wrote += 1
    questions.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    return len(entries), len(open_), wrote


# -- one step in this process --------------------------------------------------------------------------------


PROGRESS_VARIABLE = "KPI_WIDE_PROGRESS"


def progress(what: str) -> None:
    """One line of the step's progress (its seconds so far, what ended, its peak), to the file the run names; no cell."""
    target = os.environ.get(PROGRESS_VARIABLE)
    if target:
        with open(target, "a", encoding="utf-8") as out:
            out.write(f"{time.strftime('%H:%M:%S')} {round(time.process_time(), 1)} cpu-s {what} "
                      f"peak {_peak_rss_mb()} MB\n")


class Clock:
    """Seconds spent in each function wrapped, each call's end written to the progress file."""

    def __init__(self) -> None:
        self.seconds: "dict[str, float]" = {}

    def wrap(self, owner: object, name: str) -> None:
        if not hasattr(owner, name):
            return
        original = getattr(owner, name)
        clock = self

        def timed(*args: object, **kwargs: object) -> object:
            started = time.perf_counter()
            try:
                return original(*args, **kwargs)
            finally:
                spent = time.perf_counter() - started
                clock.seconds[name] = round(clock.seconds.get(name, 0.0) + spent, 2)
                progress(f"{name} {round(spent, 1)} s")

        setattr(owner, name, timed)


def _records(data: pathlib.Path) -> "list[pathlib.Path]":
    from synthtwin import inside

    return sorted(pathlib.Path(data, kpi_rules.INSTALLATION_FOLDER, inside.FOLDER).glob(f"*{inside.SUFFIX}"))


def _reads(terms: object, parent: str) -> bool:
    """Whether a fit's terms read ``parent`` (a term names its column, or a product of terms does)."""
    if isinstance(terms, list):
        return any(_reads(term, parent) for term in terms)
    return terms == parent


def relations_found(record: pathlib.Path) -> "dict[str, object]":
    """For each written relation, whether its response's fit reads its parent; the parents a fit took."""
    from synthtwin import inside

    zones = inside.load_record(record)["zones"]
    zone = zones.get("relations") if isinstance(zones, dict) else None
    columns = zone.get("columns") if isinstance(zone, dict) else None
    fitted: "dict[str, dict]" = {}
    for entry in columns or []:
        if isinstance(entry, dict):
            fitted[str(entry.get("name"))] = entry
    found: "dict[str, list[str]]" = {}
    missed: "dict[str, list[str]]" = {}
    for response, parents in W.RELATIONS.items():
        entry = fitted.get(response)
        for parent in parents:
            terms: "list[object]" = []
            if entry is not None:
                for part in ("value", "presence"):
                    model = entry.get(part)
                    if isinstance(model, dict):
                        terms += [model.get("terms")]
            (found if _reads(terms, parent) else missed).setdefault(response, []).append(parent)
    parents_taken: "list[int]" = []
    for entry in fitted.values():
        named: "set[str]" = set()
        model = entry.get("value")
        for term in (model.get("terms") if isinstance(model, dict) else None) or []:
            for other in fitted:
                if _reads(term, other):
                    named.add(other)
        parents_taken += [len(named)]
    return {
        "modelled": len(fitted),
        "found": sum(len(v) for v in found.values()), "missed": missed,
        "written": sum(len(v) for v in W.RELATIONS.values()),
        "parents_taken_mean": round(sum(parents_taken) / len(parents_taken), 2) if parents_taken else 0.0,
        "parents_taken_most": max(parents_taken) if parents_taken else 0,
    }


def profile_step(table: pathlib.Path, work: pathlib.Path) -> "dict[str, object]":
    from synthtwin import (chain, chain_selftest, cli, inside_dates, inside_keyed, inside_missing, inside_relations,
                           inside_trajectories, patient_layer, profile)

    _record_switch()
    clock = Clock()
    for owner, name in ((cli, "_inside_record_written"), (cli, "_inside_trajectories"), (inside_relations, "fit_zone"),
                        (inside_relations, "encode"), (inside_dates, "take_column"), (inside_dates, "zone_of"),
                        (inside_missing, "fit_zone"), (inside_trajectories, "zone_from_columns"),
                        (inside_keyed, "build_zone"), (inside_keyed, "key_of"), (inside_keyed, "_copies"),
                        (chain, "describe"), (chain_selftest, "run"), (patient_layer, "describe"),
                        (profile, "build_document")):
        clock.wrap(owner, name)
    # The chain's own stage probe (lane CHs, `chain._probed`): each stage's end in the progress file.
    chain._probed = lambda stage, counts: progress(f"chain stage {stage}")  # type: ignore[attr-defined]
    out = pathlib.Path(work, "out")
    out.mkdir(exist_ok=True)
    argv = ["profile", str(table), "--out-dir", str(out), "--replace", "--person", W.PERSON]
    started, cpu = time.perf_counter(), time.process_time()
    # THE FIRST ROUND AT THE KEYBOARD (`--keyboard`): a person at the terminal who presses Enter at every prompt, each
    # prompt counted -- the questions a physician faces there; Enter leaves each open, as a run with nobody at the
    # keyboard does. The answered rounds after it are route S's, through the questions file.
    prompts: "list[str]" = []
    saved = (cli._a_person_at_the_terminal, cli._terminal_ask)
    if os.environ.get(KEYBOARD_VARIABLE):
        def entered(prompt: str) -> "str | None":
            prompts.append(prompt)
            return "" if len(prompts) < PROMPTS_MOST else None

        cli._a_person_at_the_terminal = lambda: True  # type: ignore[assignment]
        cli._terminal_ask = entered  # type: ignore[assignment]
    try:
        code = _quiet(argv)
    finally:
        cli._a_person_at_the_terminal, cli._terminal_ask = saved  # type: ignore[assignment]
    rounds = [{"exit": code, "seconds": round(time.perf_counter() - started, 1)}]
    if os.environ.get(KEYBOARD_VARIABLE):
        rounds[0]["prompts"] = len(prompts)
    progress(f"round 1 exit {code} prompts {len(prompts)}")
    questions = pathlib.Path(out, f"{table.stem}-questions.json")
    # Route S, as the reliability battery runs it (`reliability_battery.make_twins`): after a round that wrote its
    # description, the holder's answers to every open question, and the next round with --answers (with
    # --replace-description where the record of earlier descriptions refuses it), while answers are written.
    most = int(os.environ.get(ROUNDS_VARIABLE, str(ROUNDS)))
    while code == 0 and len(rounds) < 1 + most and questions.exists():
        entries, open_, wrote = answered(questions)
        rounds[-1].update({"entries": entries, "open": open_, "answered": wrote})
        if not wrote:
            break
        began = time.perf_counter()
        again = argv + ["--answers", str(questions)]
        code = _quiet(again)
        if code != 0:
            code = _quiet(again + ["--replace-description"])
        rounds += [{"exit": code, "seconds": round(time.perf_counter() - began, 1)}]
        progress(f"round {len(rounds)} exit {code}")
    if questions.exists():
        import reliability_battery as B

        document = json.loads(questions.read_text(encoding="utf-8"))
        rounds[-1].update({"entries": len(_entries(document)),
                           "open": len([e for e in _entries(document) if not e.get("your_answer")])})
        rounds[-1]["questions_file_bytes"] = questions.stat().st_size
        del B
    data = pathlib.Path(os.environ["XDG_DATA_HOME"])
    found = _records(data)
    return {
        "step": "profile", "exit": code, "rounds": rounds,
        "seconds": round(time.perf_counter() - started, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
        "peak_rss_mb": _peak_rss_mb(), "inside_seconds": clock.seconds,
        "record_bytes": found[0].stat().st_size if found else 0, "records": len(found),
        "relations": relations_found(found[0]) if found else {},
    }


def generate_step(work: pathlib.Path) -> "dict[str, object]":
    from synthtwin import generation, inside_dates, inside_keyed, inside_missing, inside_relations, inside_trajectories
    from synthtwin import patient_walk

    _record_switch()
    clock = Clock()
    for owner, name in ((generation, "generate_held"), (generation, "generate_inside"),
                        (inside_relations, "draw_columns"), (inside_dates, "write_dates_held"),
                        (inside_trajectories, "twin_with_zone"), (patient_walk, "twin"),
                        (inside_keyed, "persons_and_labels"), (inside_keyed, "numbers_and_rules"),
                        (inside_missing, "moved_columns")):
        clock.wrap(owner, name)
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
        "peak_rss_mb": _peak_rss_mb(), "inside_seconds": clock.seconds, "drawn_columns": drawn,
        "report_lines": len(reports[0].read_text(encoding="utf-8").splitlines()) if reports else 0,
    }


def validate_step(work: pathlib.Path) -> "dict[str, object]":
    _record_switch()
    out = pathlib.Path(work, "out")
    described = sorted(out.glob("*-profile.json"))
    if not described:
        return {"step": "validate", "exit": -1}
    started, cpu = time.perf_counter(), time.process_time()
    code = _quiet(["validate", str(described[0]), "--out-dir", str(out), "--replace"])
    reports = sorted(out.glob("*-twin-quality.txt"))
    text = reports[0].read_text(encoding="utf-8") if reports else ""
    lines = text.splitlines()
    # The report's head: what a reader meets before the obligation-by-obligation listing (the summary, the bounds and
    # every missed obligation); and the missed obligations' count, read off the head's own words.
    listing = "EVERY OBLIGATION, IN THE DESCRIPTION'S OWN ORDER."
    head = lines.index(listing) if listing in lines else len(lines)
    return {
        "step": "validate", "exit": code,
        "seconds": round(time.perf_counter() - started, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
        "peak_rss_mb": _peak_rss_mb(), "report_lines": len(lines), "report_bytes": len(text.encode()),
        "report_head_lines": head, "summary": [line for line in lines[:head] if "missed" in line.lower()][:6],
    }


def checks_step(table: pathlib.Path, work: pathlib.Path) -> "dict[str, object]":
    from synthtwin import twin_checks

    out = pathlib.Path(work, "out")
    twin = pathlib.Path(out, f"{table.stem}-twin.csv")
    if not twin.exists():
        return {"step": "checks", "exit": -1}
    started, cpu = time.perf_counter(), time.process_time()
    # The checks' own table floor stays on at the owner's 20,000 rows and more; a first look below it turns it off.
    outcome = twin_checks.run_checks(f"{table}", f"{twin}", person=W.PERSON,
                                     small_tables_refused=not os.environ.get(SMALL_VARIABLE))
    return {
        "step": "checks", "exit": 0 if outcome.passed else 3,
        "seconds": round(time.perf_counter() - started, 1), "cpu_seconds": round(time.process_time() - cpu, 1),
        "peak_rss_mb": _peak_rss_mb(),
        "verdicts": {check.code: bool(check.passed) for check in outcome.checks},
        "failed_lines": [list(check.lines) for check in outcome.checks if not check.passed][:5],
    }


# -- the run: a process a step -------------------------------------------------------------------------------


def _child(arguments: "list[str]", env: "dict[str, str]") -> "dict[str, object]":
    done = subprocess.run([sys.executable, str(pathlib.Path(__file__).resolve()), *arguments],
                          env=env, capture_output=True, text=True, check=False)
    for line in done.stdout.splitlines():
        if line.startswith(PREFIX):
            return dict(json.loads(line[len(PREFIX):]))
    return {"step": arguments[0], "exit": done.returncode, "error": done.stderr[-1500:]}


def run(rows: int, seed: int, work: pathlib.Path, keep: bool, results: "pathlib.Path | None",
        steps: "tuple[str, ...]", keyboard: bool = False, rounds: int = ROUNDS, no_record: bool = False) -> None:
    work.mkdir(parents=True, exist_ok=True)
    place = kpi_rules.fresh_data_folder(work)
    env = dict(os.environ)
    for name in kpi_rules.DATA_FOLDER_NAMES:
        env[name] = str(place)
    env[DATA_VARIABLE] = str(place)
    env[PROGRESS_VARIABLE] = str(pathlib.Path(work, f"progress-{rows}-s{seed}.txt"))
    if rows < 20_000:
        env[SMALL_VARIABLE] = "1"
    if keyboard:
        env[KEYBOARD_VARIABLE] = "1"
    env[ROUNDS_VARIABLE] = str(rounds)
    if no_record:
        env[NO_RECORD_VARIABLE] = "1"
    env["PYTHONPATH"] = os.pathsep.join([str(ROOT / "src"), env.get("PYTHONPATH", "")]).rstrip(os.pathsep)
    folder = pathlib.Path(work, f"wide-{rows}-s{seed}")
    shutil.rmtree(folder, ignore_errors=True)
    pathlib.Path(folder, "table").mkdir(parents=True)
    table = pathlib.Path(folder, "table", TABLE)
    said: "list[dict[str, object]]" = []

    def emit(line: "dict[str, object]") -> None:
        line.update({"rows": rows, "columns": W.COLUMNS, "seed": seed, "route": "description" if no_record else "inside"})
        text = PREFIX + json.dumps(line, sort_keys=True)
        print(text, flush=True)
        if results is not None:
            with open(results, "a", encoding="utf-8") as out:
                out.write(text + "\n")

    try:
        started = time.perf_counter()
        size = W.write(table, rows, seed)
        emit({"step": "write", "seconds": round(time.perf_counter() - started, 1), "table_bytes": size})
        for step in STEPS:
            if step not in steps:
                continue
            arguments = [step, str(table), str(folder)]
            line = _child(arguments, env)
            emit(line)
            said += [line]
            if line.get("exit") not in (0, 3):
                break
    finally:
        if not keep:
            shutil.rmtree(folder, ignore_errors=True)
            shutil.rmtree(place, ignore_errors=True)


def main(argv: "list[str]") -> int:
    parser = argparse.ArgumentParser(prog="kpi_wide_table.py")
    sub = parser.add_subparsers(dest="command", required=True)
    one = sub.add_parser("run")
    one.add_argument("--rows", type=int, required=True)
    one.add_argument("--seed", type=int, default=1)
    one.add_argument("--work", required=True)
    one.add_argument("--keep", action="store_true")
    one.add_argument("--results", default="")
    one.add_argument("--steps", default=",".join(STEPS))
    one.add_argument("--keyboard", action="store_true")
    one.add_argument("--rounds", type=int, default=ROUNDS, help="answered rounds after the first, at most")
    one.add_argument("--no-record", action="store_true", help="the inside record's sub-switch off: the description route")
    writer = sub.add_parser("write")
    writer.add_argument("rows", type=int)
    writer.add_argument("path")
    writer.add_argument("--seed", type=int, default=1)
    for step in STEPS:
        child = sub.add_parser(step)
        child.add_argument("table")
        child.add_argument("work")
    options = parser.parse_args(argv)
    if options.command == "run":
        run(options.rows, options.seed, pathlib.Path(options.work).resolve(), options.keep,
            pathlib.Path(options.results) if options.results else None, tuple(options.steps.split(",")),
            options.keyboard, options.rounds, options.no_record)
        return 0
    if options.command == "write":
        print(W.write(options.path, options.rows, options.seed))
        return 0
    table, work = pathlib.Path(options.table), pathlib.Path(options.work)
    if options.command == "profile":
        line = profile_step(table, work)
    elif options.command == "generate":
        line = generate_step(work)
    elif options.command == "validate":
        line = validate_step(work)
    else:
        line = checks_step(table, work)
    print(PREFIX + json.dumps(line, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

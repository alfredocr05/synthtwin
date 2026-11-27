"""K-HZ-12: few-valued numbers with a gap among them, at the table floor (lane GG, plan P4-D440).

Three tables of 20,000 rows, each profiled through the command, its
questions answered as the zoo answers them (`no` to the Safe Harbor
question of a column the person knows as a measurement), generated at
seed 0 and read back:

- the zoo's own surveys (`tests/health_zoo.py`: `q2_score`, `q3_score`
  and `scale_total`) beside the lane's shapes (`tests/few_valued_shapes.py`:
  a 1-to-5 score, a pain score of 0 to 10, half-step scores and a 1-to-7
  scale, each beside -99, a days' supply with rare values) and two
  gapless controls;
- the sweep's other shapes: codes -9 and -1 below a scale, two codes
  below one, a code 99 above one, and a dispensed quantity;
- lane HX's case: the warehouse export's 60 patient keys beside -1, their question
  left unanswered;
- from the lane's repair 1: three laboratory columns (the statistics
  skeptic's hr61, glu46 and k_dec: 61 heart rates beside -99, 46
  glucoses beside 999, potassium to one decimal beside -99 with values on
  one cell each in its tail), each also generated unanswered -- the
  base's twin, since GG acts only after `no` -- for the share measure;
  and skeptic 1's k60f3m and k60f3mp: sixty patient keys of three
  figures beside -1, alone and beside a declared person column, their
  question left unanswered;
- from its repair 2 (the orchestrator's LANE GG RULINGS 3, its verify's
  items 1 and 2): a days' supply with one 13 and one 83, a Likert score
  beside -98 and -44 with one stray -77, and a potassium beside -99 with
  one -50, each one-cell number an edge of a published empty stretch;
  and the verify's k60f3m99 and k60f3m40, the same sixty keys beside -99
  on 2 % of rows and beside -1 on 40 %, in one table.

It prints, summed over the thirteen gapped columns, the levels lost (real
numbers the twin never writes), the twin cells inside a published empty
stretch, the twin cells off the published value list (or off the real
spellings where no list is published), the published mode pairs the twin
misses and the published rungs its own ladder misses; the gapless
controls that list their values; the real patient keys printed in any
file and the twin cells equal to one; and the scores whose valid mean
(-99 aside) falls outside the real table's own half-split gap. From the
repair: the listed values held by eleven real cells or more, outside the
tails, that the twin writes on fewer than a quarter of them
(`values_starved`); the listed columns whose total variation from the
real column exceeds the unanswered twin's (`listed_tvd_above_base`); the
values on one cell left off a list, which are never printed and so never
written (`singletons_left_off`, recorded, kept out of `levels_lost`);
and the three-figure keys: held, none printed in the column's own facts,
and the twin cells equal to a real key, the held column's made-up keys
drawn from the 900 three-figure numbers, recorded beside chance's
bound. Every
count is LINEAR in the cells (`few_valued_shapes.faults`; the keys in a
set, each token and twin cell looked up once). The seconds each step of
the product took are printed beside them, apart from the counting.

Each table is written into a temporary folder that is removed at the end.

    .venv/bin/python tools/measurements/kpi_few_valued_gap.py --kpi
"""

import collections
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
import few_valued_shapes as shapes  # noqa: E402
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()

from synthtwin import canonical, cli, contract, generation, profile, reading, rendering, taxonomy  # noqa: E402

ROWS = 20_000
SURVEYS = ("q2_score", "q3_score", "scale_total")
GAPPED = SURVEYS + shapes.GAPPED + tuple(shapes.MORE) + tuple(shapes.LABS) + tuple(shapes.EDGES)


def _unanswered_twin(folder: pathlib.Path) -> "dict[str, list[str]]":
    """The twin GG leaves as the base wrote it: the library's, no column answered `no`, seed 0."""
    document = profile.build_document(reading.read_table(str(folder / "t.csv")), taxonomy.Settings(), [])
    written = folder / "t-unanswered.json"
    written.write_text(canonical.serialize(document), encoding="utf-8", newline="")
    text = rendering.twin_csv(generation.generate(contract.load_profile(str(written)), 0))
    rows = list(csv.reader(io.StringIO(text)))
    return {rows[0][place]: [row[place] for row in rows[1:]] for place in range(len(rows[0]))}


def _write(folder: pathlib.Path, header: "list[str]", body: "list[list[str]]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(body)
    return table


def _run(folder: pathlib.Path, header: "list[str]", body: "list[list[str]]", answers: "dict[str, str]") -> "dict[str, float]":
    """Profile, answer every round, generate at seed 0: the seconds of each."""
    table = _write(folder, header, body)
    seconds: "dict[str, float]" = {}
    started = time.perf_counter()
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=True) in (0, 3)
    seconds["profile"] = time.perf_counter() - started
    started = time.perf_counter()
    shapes.answered(cli.main, folder, table, answers)
    seconds["answers"] = time.perf_counter() - started
    started = time.perf_counter()
    assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
    seconds["generate"] = time.perf_counter() - started
    return seconds


def _twin(folder: pathlib.Path) -> "dict[str, list[str]]":
    with (folder / "t-twin.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return {rows[0][place]: [row[place] for row in rows[1:]] for place in range(len(rows[0]))}


def _blocks(folder: pathlib.Path) -> "dict[str, dict[str, object]]":
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    return {f"{block['name']}": block for block in document["columns"]}


def _answered_only(folder: pathlib.Path, table: pathlib.Path, answers: "dict[str, str]", extra: "list[str]") -> None:
    """Every round answered from ``answers`` alone: a question no answer names is left open."""
    questions = folder / "t-questions.json"
    for _round in range(4):
        if not questions.is_file():
            return
        document = json.loads(questions.read_text(encoding="utf-8"))
        entries: "list[dict[str, object]]" = []
        for key in ("about_your_file", "asked"):
            entries += [one for one in (document.get(key) or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        checklist = document.get("checklist") or {}
        entries += [one for one in (checklist.get("columns") or []) if isinstance(one, dict) and "answers_you_can_give" in one]
        changed = False
        for entry in entries:
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]  # type: ignore[union-attr]
            wanted = answers.get(f"{entry.get('column', '')}", "")
            given = wanted if wanted in offered else ""
            if entry.get("your_answer", "") != given:
                changed = True
            entry["your_answer"] = given
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace", "--answers", f"{questions}"] + extra) in (0, 3)
        if not changed:
            return


def main() -> None:
    totals = {"levels_lost": 0, "cells_in_gap": 0, "cells_off_list": 0, "mode_count_missed": 0, "rungs_off": 0}
    named: "list[str]" = []
    spent: "dict[str, float]" = {"profile": 0.0, "answers": 0.0, "generate": 0.0}
    gapless_listed = 0
    mean_outside = 0
    measured = 0
    starved = 0
    above_base = 0
    singletons = 0
    with tempfile.TemporaryDirectory(prefix="synthtwin-few-valued-") as scratch:
        root = pathlib.Path(scratch)
        zoo_header, zoo_body = health_zoo.surveys(ROWS, 20261016)
        kept = [zoo_header.index(name) for name in ("respondent_id",) + SURVEYS]
        lane_header, lane_body = shapes.table(shapes.SHAPES, ROWS)
        more_header, more_body = shapes.table(shapes.MORE, ROWS, 20261017)
        tables = (
            (
                "surveys",
                [zoo_header[place] for place in kept] + lane_header,
                [[row[place] for place in kept] + right for row, right in zip(zoo_body, lane_body)],
            ),
            ("sweep", more_header, more_body),
            ("labs",) + shapes.table(shapes.LABS, ROWS, 4242),
            ("edges",) + shapes.edge_strays(ROWS),
        )
        for name, header, body in tables:
            folder = root / name
            answers = {column: "measurement" for column in header}
            answers["respondent_id"] = "identifier"
            for step, seconds in _run(folder, header, body, answers).items():
                spent[step] = spent[step] + seconds
            twin = _twin(folder)
            blocks = _blocks(folder)
            base = _unanswered_twin(folder)
            for column in header:
                if column in shapes.GAPLESS:
                    gapless_listed = gapless_listed + (1 if "few_values" in blocks[column] else 0)
                if column not in GAPPED:
                    continue
                place = header.index(column)
                real = [row[place] for row in body]
                found = shapes.faults(blocks[column], real, twin[column], taxonomy._quantile)
                # A value on ONE real cell is never printed, so never
                # written: recorded apart, not a level lost.
                alone = {text for text, count in collections.Counter(real).items() if count == 1}
                left_off = sum(1 for text in alone if text not in set(twin[column]))
                singletons = singletons + left_off
                found["levels_lost"] = found["levels_lost"] - left_off
                starving = shapes.starved(blocks[column], real, twin[column])
                starved = starved + len(starving)
                if starving:
                    named += [f"{column} starved {starving}"]
                if "few_values" in blocks[column] and shapes.total_variation(real, twin[column]) > shapes.total_variation(real, base[column]):
                    above_base = above_base + 1
                    named += [f"{column} total variation above the unanswered twin's"]
                measured = measured + 1
                for key, value in found.items():
                    total_key = "mode_count_missed" if key == "mode_missed" else key
                    totals[total_key] = totals[total_key] + value
                if any(found.values()):
                    named += [f"{column} {found}"]
                if column in ("q2_score", "q3_score"):
                    real = [float(row[place]) for row in body if row[place] != "-99"]
                    halves = (real[0::2], real[1::2])
                    gap = abs(sum(halves[0]) / len(halves[0]) - sum(halves[1]) / len(halves[1]))
                    made = [float(cell) for cell in twin[column] if cell != "-99"]
                    if abs(sum(made) / len(made) - sum(real) / len(real)) > gap:
                        mean_outside = mean_outside + 1
        header, body = shapes.keyed_export(ROWS)
        keys = {float(row[1]) for row in body if row[1] != "-1"}
        folder = root / "keyed_export"
        for step, seconds in _run(folder, header, body, {"EncounterKey": "identifier"}).items():
            spent[step] = spent[step] + seconds
        shown = shapes.keys_shown(folder, keys)
        equal = sum(1 for cell in _twin(folder)["patient_key"] if shapes.number(cell) in keys)
        three_held = 0
        three_shown = 0
        three_equal = 0
        for person in (False, True):
            header, body = shapes.keys_in_sequence(ROWS, person=person)
            keys = {float(row[1]) for row in body if row[1] != "-1"}
            folder = root / ("k60f3mp" if person else "k60f3m")
            answers = {"EncounterKey": "identifier"}
            table = _write(folder, header, body)
            extra = ["--identifier", "patient"] if person else []
            started = time.perf_counter()
            assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"] + extra, small_tables_refused=True) in (0, 3)
            spent["profile"] = spent["profile"] + time.perf_counter() - started
            started = time.perf_counter()
            _answered_only(folder, table, answers, extra)
            spent["answers"] = spent["answers"] + time.perf_counter() - started
            started = time.perf_counter()
            assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
            spent["generate"] = spent["generate"] + time.perf_counter() - started
            three_held = three_held + (1 if _blocks(folder)["patient_key"]["role"] == "identifier" else 0)
            three_shown = three_shown + shapes.column_keys_shown(folder, keys, "patient_key")
            three_equal = three_equal + sum(1 for cell in _twin(folder)["patient_key"] if shapes.number(cell) in keys)
        # ...and the verify's k60f3m99 and k60f3m40 (repair 2), a column each.
        header, body = shapes.keys_beside_placeholders(ROWS)
        folder = root / "k60f3m99-k60f3m40"
        table = _write(folder, header, body)
        started = time.perf_counter()
        assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=True) in (0, 3)
        spent["profile"] = spent["profile"] + time.perf_counter() - started
        started = time.perf_counter()
        _answered_only(folder, table, {"EncounterKey": "identifier"}, [])
        spent["answers"] = spent["answers"] + time.perf_counter() - started
        started = time.perf_counter()
        assert shapes.quiet(cli.main, ["generate", f"{folder / 't-profile.json'}", "--replace", "--seed", "0"]) == 0
        spent["generate"] = spent["generate"] + time.perf_counter() - started
        made = _twin(folder)
        for column in ("patient_key", "PatientKeyB"):
            place = header.index(column)
            keys = {float(row[place]) for row in body if not row[place].startswith("-")}
            three_held = three_held + (1 if _blocks(folder)[column]["role"] == "identifier" else 0)
            three_shown = three_shown + shapes.column_keys_shown(folder, keys, column)
            three_equal = three_equal + sum(1 for cell in made[column] if shapes.number(cell) in keys)
    value: "dict[str, object]" = {
        "columns_measured": measured,
        "levels_lost": totals["levels_lost"],
        "cells_in_gap": totals["cells_in_gap"],
        "cells_off_list": totals["cells_off_list"],
        "mode_count_missed": totals["mode_count_missed"],
        "rungs_off": totals["rungs_off"],
        "gapless_columns_listed": gapless_listed,
        "valid_means_outside_half_split": mean_outside,
        "patient_keys_shown": shown,
        "patient_key_twin_cells": equal,
        "values_starved": starved,
        "listed_tvd_above_base": above_base,
        "singletons_left_off": singletons,
        "three_figure_keys_held": three_held,
        "three_figure_keys_shown": three_shown,
        "three_figure_key_twin_cells": three_equal,
    }
    detail = "; ".join(named) or "every gapped column clean"
    detail = detail + "; seconds " + ", ".join(f"{step} {round(seconds, 1)}" for step, seconds in spent.items())
    kpi_rules.emit("K-HZ-12", value, detail)


if __name__ == "__main__":
    main()

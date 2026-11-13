"""K-HZ-26: the zoo's time columns at 20,000 rows that no reader reads, and the bad cells their twins write (plan P4-D473).

Lane TR of the zoo-fix track (the zoo plan's section 2.5): the time
columns of `tests/health_zoo.py` and `tests/health_zoo_wide.py` that the
lane's readers own -- a military time `0742` (`chart_time`), a monitor's
clock with milliseconds (`monitor_clock`), DICOM's TM with a fraction
(`study_time`), Eastern stamps followed by their zone word
(`zoned_word`), a month and year of its own (`onset_month`), the registry
mix of years, months and days (`dx_date`), NAACCR's YYYYMMDD, YYYYMM and
YYYY (`date_of_diagnosis`), slot ends written `24:00` at the day's end
(`slot_end`), and a warehouse date key beside its -1 and -2 members
(`day_key`, lane TR-e's). Each table runs through `run_table` at 20,000
rows with the owner's table floor on -- profiled, answered with the
zoo's general facts, generated at seed 0, validated -- and per column:

- READ: the answered description reads it as dates or clock times
  (`datetime`, `time_of_day`), or keeps its exact list (`categorical`
  with no level held back: rule 7's own exact twin, P4-D419's ZR.7), or
  holds dates it read whole or at a coarser grain beside the people who
  hold them (a `time_grain` record, plan P4-D417), or describes it as
  record numbers though the zoo never answered it so (a hold of dates
  few people hold, plan P4-D406): read, and held by HIPAA's floor,
  named apart as HELD;
- BAD CELLS: the twin's cells, counted in ONE pass, that are blank where
  the real column holds no blank, or that its own written form does not
  read (the zoo's pattern or strptime form for the column).

HELD names only a block that carries a `time_grain` record (the lane's
statistics check, item 2: a record-number block the zoo never answered
so is no reading -- `dx_date` is held by its open questions, and the
base's `chart_time` by its open padded question -- so both count unread).

AND TWO HOLDS AT 20,000 ROWS, each an exact 0 (repair 1 of lane TR):

- HELD BIRTH STAMPS (the lane's skeptic 1, item 1; LANE TR RULINGS 2
  (2)): one birth stamp a patient, 1,000 patients born 1928 to 2005, 20
  rows each, written with an Eastern zone word, with no offset, with
  `-05:00` or `-04:00`, with ` UTC`, and as a date alone (the control),
  each profiled unanswered, with the patient answered `identifier`, and
  with that and the birth stamp's Safe Harbor `yes`, generated at seed 0:
  the twin cells whose calendar date (its year, month and day as
  written) is a real cell's, one pass over each, the real days in a set
  (80 a stamp form at 43732144); K-HZ-06's own same-day counter
  (tests/identifier_room_shapes.py's `same_day_cells`, which names the
  day of a date written alone) beside it; and (repair 2, the verify's
  carry C-B) the same with a Central European word, `CET` or `CEST`, and
  every stamp form's twin cells that are no stamp of the form (an invalid
  date, or a word or offset the form does not write), an exact 0 too
  (11,760 a run at e84b4ff7, where a made-up cell as long as `CEST` kept
  the identifier walk's value); and (the follow-up, LANE TR RULINGS 7
  (2)) the Eastern word after a fraction of a second, which the G1 floor
  did not draw (20,000 cells a run at 7d968bb8, the walk's value kept);
- UNANSWERED FIGURES (the lane's statistics check, item 4): military times
  `0742` beside a reading, and the seven padded key shapes on the clock's
  grid (ZR.1), each profiled with nothing answered and generated: real
  values and their fragments in the description, its summary and the
  questions file, and twin cells holding one, by the counter linear in
  the data (`unanswered_identifier_shapes.count_real`, `linear=True`).
  EVERY real value is searched for (Codex's review of lane TR, item 6);
  only LOCATIONS are set apart (`published_texts`): the clock-figures
  choice's offered text, whose fixed examples `0742` and `074512` are
  constants of the product (LANE TR RULINGS 2 (6)), and the JSON whole
  numbers -- counts, positions and settings -- where the product writes
  its own figures.

It prints K-HZ-26: the columns, those not read, and the bad cells, each
named, the two holds' counts, and each table's seconds beside them.
Every table is written into a folder of its own under a temporary folder
removed at the end.

    python tools/measurements/kpi_zoo_time_readers.py --kpi [--rows N]
"""

import argparse
import datetime
import pathlib
import re
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402

ROWS = 20_000
READ_ROLES = ("datetime", "time_of_day")
# (table, column, how its written form is read, the form): a pattern the
# whole cell matches, a strptime form, or the date key's own rule.
COLUMNS = (
    ("critical_care_charting", "chart_time", "pattern", r"([01]\d|2[0-3])[0-5]\d"),
    ("critical_care_charting", "monitor_clock", "strptime", "%H:%M:%S.%f"),
    ("imaging", "study_time", "strptime", "%H%M%S.%f"),
    ("zoned_stamps", "zoned_word", "pattern", r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d (EDT|EST)"),
    ("time_edges", "onset_month", "strptime", "%m/%Y"),
    ("tumor_registry", "dx_date", "pattern", r"\d{4}|\d\d/\d{4}|\d{4}-\d\d-\d\d"),
    ("registry_naaccr", "date_of_diagnosis", "pattern", r"\d{8}|\d{6}|\d{4}"),
    ("appointments", "slot_end", "pattern", r"([01]\d|2[0-3]):[0-5]\d|24:00"),
    ("warehouse_export", "day_key", "date_key", "%Y%m%d"),
)


def cell_reads(cell: str, how: str, form: str) -> bool:
    """Whether one present twin cell is written in its column's own form."""
    if how == "pattern":
        return re.fullmatch(form, cell) is not None
    if how == "date_key" and cell in ("-1", "-2"):
        return True
    try:
        datetime.datetime.strptime(cell, form)
    except ValueError:
        return False
    return True


def bad_cells(real: "list[str]", twin: "list[str]", how: str, form: str) -> int:
    """The twin's cells off its column's own form, or blank where the real holds no blank: one pass over each."""
    real_blank = any(cell.strip() == "" for cell in real)
    bad = 0
    for cell in twin:
        if cell.strip() == "":
            bad += 0 if real_blank else 1
            continue
        if not cell_reads(cell, how, form):
            bad += 1
    return bad


def _cells(table: "health_zoo.Table", path: pathlib.Path, column: str) -> "list[str]":
    raw = table.read(path)["raw"]
    return [f"{cell}" if f"{cell}" != "nan" else "" for cell in raw[column].tolist()]  # type: ignore[index]


def _exact_list(block: "dict") -> bool:
    return block.get("role") == "categorical" and not block.get("suppressed_levels")


def measure(rows: int, folder: pathlib.Path) -> "dict[str, dict[str, object]]":
    """Each column: its role, whether it is read, its twin's bad cells, and its tables' kinds' failures; each table run once."""
    import json

    found: "dict[str, dict[str, object]]" = {}
    done: "dict[str, dict]" = {}
    seconds: "dict[str, float]" = {}
    for table_name, column, how, form in COLUMNS:
        table = health_zoo.table_named(table_name)
        home = folder / table_name
        if table_name not in done:
            started = time.perf_counter()
            done[table_name] = health_zoo.run_table(
                table, home, rows, health_zoo.seed_of(table), small_tables_refused=rows >= health_zoo.KPI_ROWS,
            )
            seconds[table_name] = round(time.perf_counter() - started, 1)
        result = done[table_name]
        block: "dict" = {}
        try:
            document = json.loads((home / f"{table_name}-profile.json").read_text(encoding="utf-8"))
            block = [one for one in document["columns"] if one["name"] == column][0]
        except (OSError, ValueError, IndexError, KeyError):
            block = {}
        twin = home / f"{table_name}-twin{table.suffix}"
        if not twin.is_file():
            twin = home / f"{table_name}-twin.csv"
        steps = result.get("steps", {})
        made = all(
            isinstance(steps.get(step), dict) and steps[step].get("exit") == 0
            for step in ("profile", "generate")
        ) and twin.is_file()
        bad: "int | None" = None
        if made:
            bad = bad_cells(
                _cells(table, home / f"{table_name}{table.suffix}", column), _cells(table, twin, column), how, form,
            )
        role = f"{block.get('role', 'not described')}"
        held = isinstance(block.get("time_grain"), dict)
        found[column] = {
            "table": table_name,
            "role": role + (" held" if held and role not in READ_ROLES else ""),
            "read": role in READ_ROLES or _exact_list(block) or held,
            "held": held and role not in READ_ROLES,
            "bad_cells": bad,
            "seconds": seconds[table_name],
            # The zoo's own verdict on each kind of the table, as K-HZ-02 counts it.
            "kinds": {
                kind: health_zoo.failure_items(table, result, kind) for kind in table.kinds
            },
        }
    return found


# THE HELD BIRTH STAMPS (repair 1 of lane TR): each spelling of one instant.
STAMP_SPELLINGS = ("zone", "zone-eu", "zone-fraction", "plain", "offset", "utc", "date")
# What each spelling's twin cell is: its strptime form, and what may follow
# it (a word of the family, any offset, ` UTC`, or nothing).
STAMP_SHAPES = {
    "zone": ("%Y-%m-%d %H:%M:%S", r" (EST|EDT)"),
    "zone-eu": ("%Y-%m-%d %H:%M:%S", r" (CET|CEST)"),
    "zone-fraction": ("%Y-%m-%d %H:%M:%S.%f", r" (EST|EDT)"),
    "plain": ("%Y-%m-%d %H:%M:%S", r""),
    "offset": ("%Y-%m-%d %H:%M:%S", r"[+-]\d\d:\d\d"),
    "utc": ("%Y-%m-%d %H:%M:%S", r" UTC"),
    "date": ("%Y-%m-%d", r""),
}
ANSWER_STATES = ("unanswered", "identifier", "identifier and yes")
_CALENDAR = re.compile(r"(\d{4})-(\d\d)-(\d\d)")
KEY_SHAPES = {
    "0001_to_0040": lambda index: f"{1 + index % 40:04d}",
    "0001_to_0059": lambda index: f"{1 + index % 59:04d}",
    "0100_to_0159": lambda index: f"{100 + index % 60:04d}",
    "sites_by_patients_6x40": lambda index: f"{1 + index // 40 % 6:02d}{1 + index % 40:02d}",
    "0001_to_0020": lambda index: f"{1 + index % 20:04d}",
    "0101_to_0140": lambda index: f"{101 + index % 40:04d}",
    "sites_by_patients_4x30": lambda index: f"{1 + index // 30 % 4:02d}{1 + index % 30:02d}",
}


def _spelled(moment: "datetime.datetime", spelling: str) -> str:
    """One birth instant as the spelling writes it: the Eastern word or offset by the month (April to October)."""
    summer = 4 <= moment.month <= 10
    if spelling == "zone":
        return f"{moment:%Y-%m-%d %H:%M:%S} " + ("EDT" if summer else "EST")
    if spelling == "zone-eu":
        return f"{moment:%Y-%m-%d %H:%M:%S} " + ("CEST" if summer else "CET")
    if spelling == "zone-fraction":
        # ...a fraction of three figures from the instant's own minute and
        # second, so the births' draw, and every other spelling's table, stay.
        fraction = (moment.minute * 61 + moment.second * 7) % 1000
        return f"{moment:%Y-%m-%d %H:%M:%S}.{fraction:03d} " + ("EDT" if summer else "EST")
    if spelling == "plain":
        return f"{moment:%Y-%m-%d %H:%M:%S}"
    if spelling == "offset":
        return f"{moment:%Y-%m-%d %H:%M:%S}" + ("-04:00" if summer else "-05:00")
    if spelling == "utc":
        return f"{moment:%Y-%m-%d %H:%M:%S} UTC"
    return f"{moment:%Y-%m-%d}"


def _quiet(arguments: "list[str]", refused: bool) -> int:
    """One synthtwin command in this process with nobody at the keyboard, its screen dropped; its exit."""
    import contextlib
    import io

    import unanswered_identifier_shapes as shapes
    from synthtwin import cli

    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return cli.main(arguments, small_tables_refused=refused)


def _answered(path: pathlib.Path, answers: "dict[str, str]") -> bool:
    """Each answer written where the column's entry offers it; whether any was."""
    import json

    questions = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    entries = list(questions.get("asked") or []) + list((questions.get("checklist") or {}).get("columns") or [])
    for entry in entries:
        if not isinstance(entry, dict) or "answers_you_can_give" not in entry:
            continue
        offered = [choice.get("answer") for choice in entry["answers_you_can_give"]]
        if entry.get("column") in answers and answers[entry["column"]] in offered:
            entry["your_answer"] = answers[entry["column"]]
            changed = True
    path.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    return changed


def _written(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    import csv

    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return path


def _twin_column(folder: pathlib.Path, place: int) -> "list[str]":
    import csv

    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        return [row[place] for row in list(csv.reader(handle))[1:]]


def held_birth_stamps(rows: int, folder: pathlib.Path) -> "dict[str, dict[str, int]]":
    """Each spelling under each answer state: the twin cells on a real calendar date, and K-HZ-06's same-day count."""
    import random

    import identifier_room_shapes as room

    people = max(rows // 20, 1)
    draw = random.Random(206)
    births: "dict[str, datetime.datetime]" = {}
    for person in range(people):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        births[f"P{person + 1:05d}"] = datetime.datetime.combine(
            day, datetime.time(draw.randrange(24), draw.randrange(60), draw.randrange(60)))
    order = [f"P{1 + index % people:05d}" for index in range(rows)]
    draw.shuffle(order)
    grades = [f"{draw.randint(1, 9)}" for _row in range(rows)]
    refused = rows >= health_zoo.KPI_ROWS
    found: "dict[str, dict[str, int]]" = {}
    for spelling in STAMP_SPELLINGS:
        real = [_spelled(births[person], spelling) for person in order]
        days = {match.group(0) for match in (_CALENDAR.match(cell) for cell in set(real)) if match}
        for state in ANSWER_STATES:
            home = folder / f"stamps-{spelling}-{state.replace(' ', '-')}"
            path = _written(home, ["person_ref", "birth_ts", "grade"],
                            [[order[row], real[row], grades[row]] for row in range(rows)])
            base = ["profile", f"{path}", "--out-dir", f"{home}", "--replace"]
            _quiet(base, refused)
            answers = {"person_ref": "identifier"}
            if state == "identifier and yes":
                answers["birth_ts"] = "yes"
            for _round in range(3 if state != "unanswered" else 0):
                if not _answered(home / "t-questions.json", answers):
                    break
                _quiet(base + ["--answers", f"{home / 't-questions.json'}"], refused)
            _quiet(["generate", f"{home / 't-profile.json'}", "--out-dir", f"{home}", "--seed", "0", "--replace"],
                   refused)
            twin = _twin_column(home, 1)
            on_a_real_day = 0
            for cell in twin:
                match = _CALENDAR.match(cell)
                on_a_real_day += 1 if match and match.group(0) in days else 0
            found[f"{spelling} {state}"] = {
                "on_a_real_day": on_a_real_day, "same_day": room.same_day_cells(real, twin), "cells": len(twin),
                "no_stamp": no_stamp_cells(twin, spelling),
            }
    return found


def no_stamp_cells(twin: "list[str]", spelling: str) -> int:
    """The twin's present cells that are no stamp of the spelling's form: an invalid date, or a word or offset it does not write; one pass."""
    form, ending = STAMP_SHAPES[spelling]
    shape = re.compile(r"(.*?)" + ending)
    bad = 0
    for cell in twin:
        if cell == "":
            continue
        match = shape.fullmatch(cell)
        if match is None:
            bad += 1
            continue
        try:
            datetime.datetime.strptime(match.group(1), form)
        except ValueError:
            bad += 1
    return bad


# The answer whose offered text names the fixed examples (asking's Q-CLOCK
# choice): that text, and nothing else, is the constant location set apart.
EXAMPLE_ANSWER = "clock-figures"
EXAMPLE_TEXT_KEY = "means"


def published_texts(document: object, questions: object, summary: str) -> "list[str]":
    """What the figures leg searches for real values: every location but the constant and count ones.

    Codex's review of lane TR, item 6 (LANE TR RULINGS 5 (5)): the leg set
    apart every REAL VALUE equal to a fixed example or to a whole number of
    the description, so a real `0742` or `1000` published or written went
    uncounted. Now only LOCATIONS are set apart: the clock-figures choice's
    offered text in the questions file (`0742` and `074512`, constants of
    the product, LANE TR RULINGS 2 (6)), and every JSON WHOLE NUMBER of the
    two files -- the counts, positions and settings (the settings block's
    ceiling of 1,000 levels, a column's 1,440 cells of one form), where the
    product writes its own figures; a column's values are written as text,
    or as numbers with a point (`2359.0`, a measurement's statistics),
    which are searched. The summary writes the description in words, so
    its count locations are where it writes one of those whole numbers
    (`1440 different values, between 4 and 4 characters long`, the
    column's count of different values, measured at 20,000 rows): each
    such run of figures is set apart there and every other text of the
    summary searched; a value it writes stands in the description too,
    as text or with a point, where it is searched. Every string, key and
    decimal number of either file and the summary so read are returned,
    each as one text. A function of the three. Raises nothing. No I/O.
    """
    found: "list[str]" = []
    whole: "set[str]" = set()
    stack: "list[object]" = [document, questions]
    while stack:
        node = stack.pop()
        if isinstance(node, str):
            found.append(node)
        elif isinstance(node, bool) or node is None:
            continue
        elif isinstance(node, int):
            whole.add(f"{node}")
        elif isinstance(node, float):
            found.append(f"{node}")
        elif isinstance(node, list):
            stack.extend(node)
        elif isinstance(node, dict):
            constant = node.get("answer") == EXAMPLE_ANSWER
            for key, value in node.items():
                found.append(f"{key}")
                if constant and key == EXAMPLE_TEXT_KEY:
                    continue
                stack.append(value)
    found.append(re.sub(r"(?<![0-9.])[0-9]+(?![0-9])", lambda run: "#" if run.group(0) in whole else run.group(0), summary))
    return found


def figures_counted(
    real: "list[str]", document: object, questions: object, summary: str, twin: "list[str]"
) -> "dict[str, int]":
    """Every real value in the leg's published locations and in every twin cell, by the counter linear in the data.

    No real value is set apart (Codex's review of lane TR, item 6): the
    texts are `published_texts`', and every twin cell is searched for
    every real value (`unanswered_identifier_shapes.count_real`,
    `linear=True`). A function of the arguments. Raises nothing. No I/O.
    """
    import unanswered_identifier_shapes as shapes

    counted = shapes.count_real(real, published_texts(document, questions, summary), twin, linear=True)
    return {
        "values": counted["description_values"], "fragments": counted["description_fragments"],
        "twin_cells": counted["twin_cells"],
    }


def unanswered_figures(rows: int, folder: pathlib.Path) -> "dict[str, dict[str, int]]":
    """Military times and the seven key shapes, nothing answered: real values in the texts and the twin, linear counter.

    Every real value is searched for in every twin cell and in every
    location the description, its summary and the questions file publish
    but the constant and count ones (`published_texts`): no value is set
    apart (Codex's review of lane TR, item 6).
    """
    import json
    import random

    refused = rows >= health_zoo.KPI_ROWS
    draw = random.Random(3)
    columns: "dict[str, list[list[str]]]" = {}
    military: "list[list[str]]" = []
    for index in range(rows):
        second = draw.randrange(86400)
        military += [[f"{second // 3600:02d}{second % 3600 // 60:02d}", f"{draw.randint(60, 140)}"]]
    columns["military_time"] = military
    for shape, key in KEY_SHAPES.items():
        columns[shape] = [[key(index), f"{index % 7}"] for index in range(rows)]
    found: "dict[str, dict[str, int]]" = {}
    for name, table in columns.items():
        home = folder / f"figures-{name}"
        path = _written(home, ["chart_time", "visit"], table)
        _quiet(["profile", f"{path}", "--out-dir", f"{home}", "--replace"], refused)
        _quiet(["generate", f"{home / 't-profile.json'}", "--out-dir", f"{home}", "--seed", "0", "--replace"],
               refused)
        texts = [(home / one).read_text(encoding="utf-8") for one in ("t-profile.json", "t-profile.txt", "t-questions.json")]
        found[name] = figures_counted(
            [row[0] for row in table], json.loads(texts[0]), json.loads(texts[2]), texts[1], _twin_column(home, 0),
        )
    return found


def main() -> None:
    kpi_rules.guard_this_tree()
    parser = argparse.ArgumentParser()
    parser.add_argument("--kpi", action="store_true")
    parser.add_argument("--rows", type=int, default=ROWS)
    options = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix="synthtwin-zoo-time-") as folder:
        found = measure(options.rows, pathlib.Path(folder))
        stamps = held_birth_stamps(options.rows, pathlib.Path(folder))
        figures = unanswered_figures(options.rows, pathlib.Path(folder))
    missing = sorted(name for name, one in found.items() if not isinstance(one["bad_cells"], int))
    if missing:
        raise SystemExit(f"K-HZ-26 not measured: no twin for {', '.join(missing)}")
    unread = [name for name, one in found.items() if not one["read"]]
    held = [name for name, one in found.items() if one["held"]]
    bad = {name: int(one["bad_cells"]) for name, one in found.items() if one["bad_cells"]}  # type: ignore[call-overload]
    tables: "dict[str, object]" = {}
    kinds: "dict[str, list[str]]" = {}
    for one in found.values():
        tables[f"{one['table']}"] = one["seconds"]
        kinds.update(one["kinds"])  # type: ignore[arg-type]
    kpi_rules.emit(
        "K-HZ-26",
        {
            "time_columns": len(found),
            "time_columns_unread": len(unread),
            "unread_named": ", ".join(unread) or "none",
            "held_named": ", ".join(held) or "none",
            "bad_cells": sum(bad.values()),
            "bad_named": ", ".join(f"{name} {count}" for name, count in bad.items()) or "none",
            "held_stamp_cells_on_a_real_day": sum(
                one["on_a_real_day"] for name, one in stamps.items() if not name.startswith("date ")
            ),
            "held_date_cells_on_a_real_day": sum(
                one["on_a_real_day"] + one["same_day"] for name, one in stamps.items() if name.startswith("date ")
            ),
            "held_stamp_cells_no_stamp": sum(one["no_stamp"] for one in stamps.values()),
            "unanswered_figures_published": sum(one["values"] + one["fragments"] for one in figures.values()),
            "unanswered_figures_twin_cells": sum(one["twin_cells"] for one in figures.values()),
        },
        f"at {options.rows:,} rows: {len(unread)} of {len(found)} time columns unread, {sum(bad.values())} bad twin "
        "cells; roles " + "; ".join(f"{name} {one['role']}" for name, one in found.items())
        + "; seconds " + ", ".join(f"{name} {value}" for name, value in tables.items())
        + "; kinds failing " + ("; ".join(
            f"{kind} {len(items)} ({', '.join(items)})" for kind, items in kinds.items() if items
        ) or "none")
        + "; held birth stamps " + ", ".join(
            f"{name} {one['on_a_real_day']}/{one['same_day']}/{one['no_stamp']} of {one['cells']}"
            for name, one in stamps.items()
        )
        + "; unanswered figures " + ", ".join(
            f"{name} {one['values']}/{one['fragments']}/{one['twin_cells']}" for name, one in figures.items()
        ),
    )


if __name__ == "__main__":
    main()

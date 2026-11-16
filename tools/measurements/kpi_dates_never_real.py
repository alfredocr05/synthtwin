"""K-HZ-38: held dates written as counts, a census withheld whole and placeholders: twin cells on a real day (plan P4-D488).

Two invented tables of 20,000 rows and 1,000 patients born 1928 to 2005, twenty visits a patient from 2016 on,
each family written in its own form beside a patient column: C, nine counting systems (Excel's 1900 days with and
without a time after the point, its 1904 days, seconds and milliseconds from 1970, SAS's days and seconds from
1960, days from 1970 and from 1840); T, dates written as text (ISO, a day of the year in seven and five
figures, SAS's DATETIME with a four- and a two-figure year, a day of the year with its clock run on, ISO beside
three `99999`, ISO with one patient's twenty rows in another layout, the census withheld). Each in four modes
through the commands a person types (`synthtwin profile`, the answers round by round, `generate` seed 0,
`validate`): U nobody answers anything; A the patient column answered `identifier`, the counted columns typed
`--date-count`, every column answered `dates` where that is offered, the births' Safe Harbor question left open;
N as A, the births answered `no`; H every birth column typed `--identifier` and the patient column answered
`identifier`, one ordinary column beside, on 2,000 patients of ten rows (a birth column typed so is a person
column the table floor counts by, and 1,000 patients' births are fewer than 1,000 different days). And the census-withheld shapes of K-HZ-06's target (F3u, F2u and F3cu beside other
companion columns, P3 and P2 at 2,000 people of ten rows), the placeholder table (19,997 ISO births beside three
`99999`, nobody answering and typed `--identifier`), and the zoo's held day numbers (`day_numbers`, through
`health_zoo.run_table`).

LANE ID-ROOM3'S REPAIR 1 adds, through the same commands: skeptic 1's young births (1973-04 to 2001-08 written
as nine-figure seconds from 1970 and with a comma before three figures, nobody answering: only the open question
offering `identifier` holds them; 1,620 twin cells on 81 real birth days before); the statistics check's stray word
(the nine counting systems' births, one patient's twenty cells `UNK`, in modes U, A and N: 540 and 660 twin cells
on real birth days before, validation exiting 3); the forms that find no room (births written with a month's word,
a two-figure year or a six-figure fraction before EST or EDT, as a day of the year and as SAS's DATETIME of both
year widths, the patient answered `identifier`), whose twin cells holding a figure that are no date of the form
are counted (`no_room_invalid_strings`: 12,859 such cells on the build's head for the day of the year), here and in
table T, for every held column whose grain reads dates or stamps and whose block publishes no run of years (a
column held with no grain writes the walk's record numbers by design, and one with a room its placeholders' and its
pool's stand-ins: each column's line names its count, the key sums the forms that find no room); and
ordinary record numbers no question about dates concerns (a member number of seven figures, case numbers of twelve
to eighteen, claim numbers of sixteen, encounter keys numbered one after another), nobody answering and the
patient answered, whose blocks may publish no room (`record_number_columns_with_a_room`).

LANE ID-ROOM3'S REPAIR 2 adds (the verify of repair 1, LANE ID-ROOM3 RULINGS 7): the stray figures and words
(births as seconds from 1970 beside eleven `00000000`, beside one patient's twenty rows written as ISO dates and
zero-padded; as milliseconds beside one patient's ISO rows; as SAS datetimes beside one patient's rows month first;
as seconds beside two patients' words and beside three patients' `UNK`), nobody answering, declared with the patient
answered `identifier`, and answered `no` (D and N; 380 to 600 twin cells on real birth days with nobody answering
before, validation exiting 3 with two or three patients' words); births of one calendar year, one a patient (1970 as
seconds and milliseconds, 1960 as SAS datetimes, 1971, 1999, 2001 and 2000 as seconds), nobody answering and the
patient answered (4,940 to 5,620 before at the epoch's first year); and births as seconds with five and ten figures
after the point and milliseconds with three, nobody answering (validation exiting 3 on `all_whole_numbers` before).

Counted, for every column the description HOLDS (role `identifier`): twin cells whose calendar day, read in the
column's own system or form (a two-figure year in both centuries), is a day some real cell of the column names
(exact, merged or the same day alike: a day is a day); held columns whose validation missed any fact of theirs
(every MISSED line under the column), and runs whose validation exited other than 0; and real days ten patients or
fewer hold printed in the column's own words -- every scalar of its block, numbers too (its counts, lengths,
positions and room set aside by their keys: facts about the column, never values of it), its entries of the
questions file, and its lines of the summary, the screens, the twin's report and the quality report (firsts of a
month set aside; another column's constants, a bin edge or a count that equals a day count by chance, are not the
column's). Target 0 each, exact. Columns the description PUBLISHES at a rung are the owner's chance class (plan
P4-D488, ruling D1) and are not counted. The counter is linear: the real days in a set, each twin cell read once.

About 2,400 to 2,900 CPU seconds at 20,000 rows (the build's driver measured 1,759 to 1,769, repair 1's tables
added six runs and repair 2's add six); one process, under 1 GB. Where KPI_DATES_NEVER_REAL_LINES names a file, each column's line is written
there too.

    .venv/bin/python tools/measurements/kpi_dates_never_real.py --kpi
"""

import contextlib
import csv
import datetime
import io
import json
import os
import pathlib
import random
import re
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
from synthtwin import cli  # noqa: E402

import unanswered_identifier_shapes as shapes  # noqa: E402
from dates_never_real_shapes import (  # noqa: E402
    COUNTED, EPOCH_COHORTS, FRACTIONS, MODES, NO_ROOM, PEOPLE, ROWS, STRAY_FIGURES, TEXT, ZONED, counted_cell,
    counted_day, epoch_cohort_table, fraction_table, no_room_table, people, record_number_table, shape_table,
    stray_figure_table, stray_word_table, text_days, young_table,
)

TOKEN = re.compile(r"[0-9A-Za-z:.\-/]+")


# The keys whose numbers are facts about a column, never values of it: its counts, lengths, positions and room, and
# the counts a census or a tally maps its spellings to (lane ID-ROOM3's repair 1, the statistics check's item 5).
FACT_KEYS = ("position", "min_length", "max_length", "made_up_years", "rows", "people", "spans", "finest")
TALLIES = ("layout_forms", "missing_by_source", "missing_by_class", "n_distinct_by_occurrences", "layout_prefixes")


def texts_of(value: object, key: str = "") -> "list[str]":
    """Every scalar a JSON value holds, however deep, as text: its strings and its numbers, never its keys; a number
    under a key `FACT_KEYS` or `n_...` names, or a count a census maps a spelling to (`TALLIES`), set aside."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, bool) or value is None:
        return []
    if isinstance(value, (int, float)):
        return [] if key in FACT_KEYS or key.startswith("n_") or key in TALLIES else [f"{value}"]
    found: "list[str]" = []
    if isinstance(value, dict):
        for name, part in value.items():
            found += texts_of(part, key if key in TALLIES else f"{name}")
    if isinstance(value, list):
        for part in value:
            found += texts_of(part, key)
    return found


def quiet(arguments: "list[str]") -> "tuple[int, str]":
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            try:
                code = cli.main(arguments, small_tables_refused=True)
            except SystemExit as stop:
                code = stop.code if isinstance(stop.code, int) else 1
    return code, screen.getvalue()


def answered(path: pathlib.Path, wanted: "dict[str, list[str]]") -> bool:
    questions = json.loads(path.read_text(encoding="utf-8"))
    changed = False
    entries = list(questions.get("asked") or []) + list((questions.get("checklist") or {}).get("columns") or [])
    for entry in entries:
        if not isinstance(entry, dict) or "answers_you_can_give" not in entry:
            continue
        offered = [choice.get("answer") for choice in entry["answers_you_can_give"]]
        for want in wanted.get(f"{entry.get('column', '')}", []):
            if want in offered:
                if entry.get("your_answer") != want:
                    entry["your_answer"] = want
                    changed = True
                break
    if changed:
        path.write_text(json.dumps(questions, indent=2), encoding="utf-8", newline="\n")
    return changed


def pipeline(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]", typed: "list[str]",
             wanted: "dict[str, list[str]]") -> dict:
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "t.csv"
    with open(source, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    base = ["profile", f"{source}", "--out-dir", f"{folder}", "--replace", *typed]
    started = time.process_time()
    code, said = quiet(base)
    screens = [said]
    exits = [code]
    if code == 0 and wanted:
        for _round in range(3):
            if not answered(folder / "t-questions.json", wanted):
                break
            code, said = quiet(base + ["--answers", f"{folder / 't-questions.json'}"])
            screens += [said]
            exits += [code]
    if code != 0:
        return {"exits": exits, "failed": said[-400:]}
    code, _said = quiet(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0",
                         "--replace"])
    exits += [code]
    validated, _said = quiet(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"])
    exits += [validated]
    # ...each MISSED line of the quality report under the column it is about, whatever group its fact is of: the
    # report names the column on the line above it, in quotes, so the line is kept with that name before it.
    missed: "set[str]" = set()
    quality = folder / "t-twin-quality.txt"
    reports: "list[str]" = []
    if quality.exists():
        about = ""
        for line in quality.read_text(encoding="utf-8").splitlines():
            reports += [line]
            if len(line) > 2 and line.startswith("'") and line.endswith("'"):
                about = line[1:-1]
            elif "MISSED" in line and "[" in line:
                missed.add(f"{about}: {line.strip()}")
    if (folder / "t-twin-report.txt").exists():
        reports += (folder / "t-twin-report.txt").read_text(encoding="utf-8").splitlines()
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    blocks = {block["name"]: block for block in document["columns"]}
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    twin = {name: [row[place] for row in table[1:]] for place, name in enumerate(table[0])}
    # ...each held column's own published words: the texts of its block and of its entries of the questions file,
    # and the lines of the summary and of the screens that name it (a real day of it printed there would be its
    # own; another column's constants are not). A number the block publishes as a number -- a count, a length, a
    # year of its room -- is a fact about the column, never a value of it: read as words, the block's year 2028
    # or a whole screen's count of another column matched a day count some patient was born on.
    own: "dict[str, list[str]]" = {}
    summary = (folder / "t-profile.txt").read_text(encoding="utf-8") if (folder / "t-profile.txt").exists() else ""
    asked = json.loads((folder / "t-questions.json").read_text(encoding="utf-8")) if (
        folder / "t-questions.json").exists() else {}
    entries = list(asked.get("asked") or []) + list((asked.get("checklist") or {}).get("columns") or [])
    shown = summary.splitlines() + [line for screen in screens for line in screen.splitlines()] + reports
    for name, block in blocks.items():
        own[name] = texts_of(block)
        for entry in entries:
            if isinstance(entry, dict) and entry.get("column") == name:
                own[name] += texts_of(entry)
        own[name] += [line for line in shown if name in line]
    for written in folder.glob("*"):
        if written.is_file():
            written.unlink()
    value["validations_exiting_nonzero"] = value.get("validations_exiting_nonzero", 0) + (1 if validated != 0 else 0)
    return {"exits": exits, "cpu": round(time.process_time() - started, 1), "blocks": blocks, "twin": twin,
            "own": own, "missed": sorted(missed)}


def measured(run: dict, name: str, real: "list[str]", persons: "list[str]", read) -> "tuple[int, int, int]":
    """(twin cells on a real day, real days ten patients or fewer hold printed, 1 where validation missed a fact of it)."""
    holders: "dict[datetime.date, set[str]]" = {}
    for cell, person in zip(real, persons):
        for day in read(cell):
            holders.setdefault(day, set()).add(person)
    on = 0
    for cell in run["twin"].get(name, []):
        if read(cell) & holders.keys():
            on += 1
    tokens: "set[str]" = set()
    for text in run["own"].get(name, []):
        tokens.update(TOKEN.findall(text))
    rare = {cell for cell in real if any(len(holders[day]) <= 10 and day.day != 1 for day in read(cell))}
    printed = len(rare & tokens)
    missed = 1 if any(line.startswith(f"{name}: ") for line in run["missed"]) else 0
    return on, printed, missed


value: "dict[str, int]" = {f"{table}_{mode}_twin_cells_on_a_real_day": 0 for table in ("counted", "text") for mode in MODES}
value.update({f"{key}_twin_cells_on_a_real_day": 0 for key in ("census_withheld", "placeholder", "zoo_held_day_numbers")})
value.update({"real_days_printed": 0, "held_columns_validation_missed": 0, "held_columns_read": 0, "runs_not_written": 0})
value.update({f"{key}_twin_cells_on_a_real_day": 0 for key in ("unanswered_identity", "stray_U", "stray_A", "stray_N",
                                                                "no_room")})
value.update({"no_room_invalid_strings": 0, "record_number_columns_with_a_room": 0, "validations_exiting_nonzero": 0})
lines: "list[str]" = []


def tally(key: str, on: int, printed: int, missed: int, line: str) -> None:
    value[f"{key}_twin_cells_on_a_real_day"] = value.get(f"{key}_twin_cells_on_a_real_day", 0) + on
    value["real_days_printed"] = value.get("real_days_printed", 0) + printed
    value["held_columns_validation_missed"] = value.get("held_columns_validation_missed", 0) + missed
    value["held_columns_read"] = value.get("held_columns_read", 0) + 1
    lines.append(line)


def planning_table(table: str, births: dict, visits: dict, order: list) -> "tuple[list[str], list[list[str]], dict, list[str]]":
    """(header, rows, each column's reader, the `--date-count` arguments) of planning table C or T."""
    persons = [person for person, _index in order]
    header, cols, readers, typed_counted = ["person_ref"], [persons], {}, []
    if table == "C":
        for family, member, how in COUNTED:
            for kind in ("birth", "visit"):
                name = f"{kind}_{family}"
                moments = [births[p] if kind == "birth" else visits[p][i] for p, i in order]
                header += [name]
                cols += [[counted_cell(moment, member, how) for moment in moments]]
                readers[name] = (lambda m: (lambda c: {d for d in (counted_day(c, m),) if d is not None}))(member)
                typed_counted += ["--date-count", name, member]
    else:
        rare = order[0][0]
        for family, form in TEXT:
            for kind in ("birth", "visit"):
                name = f"{kind}_{family}"
                moments = [births[p] if kind == "birth" else visits[p][i] for p, i in order]
                cells = [moment.strftime(form).upper() for moment in moments]
                if family == "ph9":
                    for place in (5, 5000, 15000):
                        cells[place] = "99999"
                if family == "mixlay":
                    for place, (person, _index) in enumerate(order):
                        if person == rare:
                            cells[place] = moments[place].strftime("%d-%b-%Y").upper()
                header += [name]
                cols += [cells]
                readers[name] = (lambda f: (lambda c: text_days(c, f)))(form)
    return header, [list(row) for row in zip(*cols)], readers, typed_counted


def the_planning_tables(scratch: pathlib.Path) -> None:
    for mode in MODES:
        # ...typed `--identifier`, a birth column is a person column the table floor counts its people by: 1,000
        # patients' births are about 956 different days and the floor refuses the table, so mode H draws 2,000
        # patients of ten rows (still 20,000 rows).
        births, visits, order = people(2000, 10) if mode == "H" else people()
        persons = [person for person, _index in order]
        for table in ("C", "T"):
            header, rows, readers, typed_counted = planning_table(table, births, visits, order)
            forms = {f"{kind}_{family}": form for family, form in TEXT for kind in ("birth", "visit")}
            names = header[1:]
            birth_names = [name for name in names if name.startswith("birth_")]
            typed: "list[str]" = []
            wanted: "dict[str, list[str]]" = {}
            run_header, run_rows = header, rows
            if mode in ("A", "N"):
                typed = list(typed_counted)
                wanted = {"person_ref": ["identifier"], **{name: ["dates"] for name in names}}
                if mode == "N":
                    wanted.update({name: ["no", "dates"] for name in birth_names})
            if mode == "H":
                typed = [x for name in birth_names for x in ("--identifier", name)]
                wanted = {"person_ref": ["identifier"]}
                draw = random.Random(31)
                run_header = header + ["grade"]
                run_rows = [row + [f"{draw.randint(1, 9)}"] for row in rows]
            run = pipeline(scratch / f"{table}-{mode}", run_header, run_rows, typed, wanted)
            if "failed" in run:
                value["runs_not_written"] = value.get("runs_not_written", 0) + 1
                lines.append(f"{table} {mode}: NOT WRITTEN, exits {run['exits']}: {run['failed'][-200:]!r}")
                continue
            for name in names:
                block = run["blocks"].get(name, {})
                if block.get("role") != "identifier":
                    continue
                place = header.index(name)
                real = [row[place] for row in rows]
                on, printed, missed = measured(run, name, real, persons, readers[name])
                grain = block.get("time_grain") if isinstance(block.get("time_grain"), dict) else {}
                bad = invalid_strings(run, name, forms[name]) if table == "T" else 0
                # ...counted in the key only for a FORM THAT FINDS NO ROOM (LANE ID-ROOM3 RULINGS 6 (3)): a held
                # column whose grain reads dates or stamps and whose block publishes no run of years. A column held
                # with no grain -- record numbers while its question is open, or typed `--identifier` -- writes the
                # walk's record numbers by design (NF125), and one with a room keeps its placeholders' and its
                # pool's stand-ins; the line names each column's count all the same.
                if grain.get("kind") in ("date", "stamp") and not block.get("made_up_years"):
                    value["no_room_invalid_strings"] += bad
                tally(f"{'counted' if table == 'C' else 'text'}_{mode}", on, printed, missed,
                      f"{table} {mode} {name}: held, grain {grain.get('kind')}, room {block.get('made_up_years')}, "
                      f"{on} twin cells on a real day, {bad} that are no date, {printed} rare real days printed, "
                      f"validation missed {missed}")
            lines.append(f"{table} {mode}: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")


def the_shapes(scratch: pathlib.Path) -> None:
    for name in ("F3u", "F2u", "F3cu", "P3", "P2", "PHu", "PHi"):
        header, rows, typed, persons = shape_table(name)
        run = pipeline(scratch / name, header, rows, typed, {})
        if "failed" in run:
            value["runs_not_written"] = value.get("runs_not_written", 0) + 1
            lines.append(f"{name}: NOT WRITTEN, exits {run['exits']}")
            continue
        block = run["blocks"].get("dob", {})
        if block.get("role") != "identifier":
            lines.append(f"{name}: dob not held ({block.get('role')})")
            continue
        real = [row[1] for row in rows]
        forms = ("%d-%b-%y", "%d-%b-%Y", "%d %b %Y") if name[0] in "FP" else ("%Y-%m-%d",)

        def read(cell: str, forms: "tuple[str, ...]" = forms) -> "set[datetime.date]":
            found: "set[datetime.date]" = set()
            for form in forms:
                found |= text_days(cell, form)
            return found

        on, printed, missed = measured(run, "dob", real, persons, read)
        key = "census_withheld" if name[0] in "FP" else "placeholder"
        tally(key, on, printed, missed, f"{name}: room {block.get('made_up_years')}, {on} twin cells on a real day, "
              f"{printed} rare real days printed, validation missed {missed}, exits {run['exits']}, {run['missed']}")


def invalid_strings(run: dict, name: str, form: str) -> int:
    """Twin cells of a held text column holding a figure that are no date of its form (its zone word aside)."""
    zoned = form in [one for _family, one in ZONED]
    found = 0
    for cell in run["twin"].get(name, []):
        core = cell.strip()
        if not core or not re.search(r"[0-9]", core):
            continue
        if zoned and " " in core:
            core = core.rsplit(" ", 1)[0]
        if not text_days(core, form) and not (form == "%Y-%m-%d" and text_days(core, "%d-%b-%Y")):
            found += 1
    return found


def held_columns_of(run: dict, header: "list[str]", rows: "list[list[str]]", persons: "list[str]", readers: dict,
                    key: str, label: str, forms: "dict[str, str] | None" = None) -> None:
    """Tally every held column a reader is given for, on the run's twin."""
    for name in readers:
        block = run["blocks"].get(name, {})
        if block.get("role") != "identifier":
            lines.append(f"{label} {name}: not held ({block.get('role')})")
            continue
        place = header.index(name)
        real = [row[place] for row in rows]
        on, printed, missed = measured(run, name, real, persons, readers[name])
        bad = invalid_strings(run, name, forms[name]) if forms and name in forms else 0
        grain = block.get("time_grain") if isinstance(block.get("time_grain"), dict) else {}
        # ...the key sums the forms that find no room, as table T's columns are summed.
        if grain.get("kind") in ("date", "stamp") and not block.get("made_up_years"):
            value["no_room_invalid_strings"] += bad
        tally(key, on, printed, missed, f"{label} {name}: held, grain {grain.get('kind')}, room "
              f"{block.get('made_up_years')}, {on} twin cells on a real day, {bad} that are no date, {printed} rare "
              f"real days printed, validation missed {missed}")


def the_repair_tables(scratch: pathlib.Path) -> None:
    """Lane ID-ROOM3's repair 1: the young births, the stray word, the forms that find no room, the record numbers."""
    def counts_in(member: str):
        return lambda cell: {day for day in (counted_day(cell.replace(",", "."), member),) if day is not None}

    header, rows, persons = young_table()
    run = pipeline(scratch / "young", header, rows, [], {})
    if "failed" in run:
        value["runs_not_written"] += 1
        lines.append(f"young U: NOT WRITTEN, exits {run['exits']}")
    else:
        readers = {"birth_ys": counts_in("seconds-since-1970"), "birth_yc": counts_in("seconds-since-1970")}
        held_columns_of(run, header, rows, persons, readers, "unanswered_identity", "young U")
        lines.append(f"young U: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")
    header, rows, typed_counted, persons = stray_word_table()
    readers = {f"birth_{family}": counts_in(member) for family, member, _how in COUNTED}
    for mode in ("U", "A", "N"):
        typed = list(typed_counted) if mode in ("A", "N") else []
        wanted: "dict[str, list[str]]" = {}
        if mode in ("A", "N"):
            wanted = {"person_ref": ["identifier"], **{name: ["dates"] for name in readers}}
            if mode == "N":
                wanted.update({name: ["no", "dates"] for name in readers})
        run = pipeline(scratch / f"stray-{mode}", header, rows, typed, wanted)
        if "failed" in run:
            value["runs_not_written"] += 1
            lines.append(f"stray {mode}: NOT WRITTEN, exits {run['exits']}")
            continue
        held_columns_of(run, header, rows, persons, readers, f"stray_{mode}", f"stray {mode}")
        lines.append(f"stray {mode}: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")
    header, rows, persons = no_room_table()
    forms = {f"birth_{family}": form for family, form in ZONED + NO_ROOM}
    readers = {name: (lambda f, z: (lambda cell: text_days(cell.rsplit(" ", 1)[0] if z and " " in cell.strip()
                                                           else cell, f)))(form, name[6:] in [x for x, _y in ZONED])
               for name, form in forms.items()}
    run = pipeline(scratch / "no-room", header, rows, [], {"person_ref": ["identifier"],
                                                           **{name: ["dates"] for name in forms}})
    if "failed" in run:
        value["runs_not_written"] += 1
        lines.append(f"no room A: NOT WRITTEN, exits {run['exits']}")
    else:
        held_columns_of(run, header, rows, persons, readers, "no_room", "no room A", forms)
        lines.append(f"no room A: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")
    header, rows, persons = record_number_table()
    for mode in ("U", "A"):
        run = pipeline(scratch / f"records-{mode}", header, rows, [], {} if mode == "U" else {
            "person_ref": ["identifier"], **{name: ["identifier"] for name in header[1:-1]}})
        if "failed" in run:
            value["runs_not_written"] += 1
            lines.append(f"records {mode}: NOT WRITTEN, exits {run['exits']}")
            continue
        for name in header[1:-1]:
            block = run["blocks"].get(name, {})
            roomed = 1 if "made_up_years" in block else 0
            value["record_number_columns_with_a_room"] += roomed
            lines.append(f"records {mode} {name}: role {block.get('role')}, room {block.get('made_up_years')}")
        lines.append(f"records {mode}: exits {run['exits']}, {run['cpu']} CPU s")


def the_repair2_tables(scratch: pathlib.Path) -> None:
    """Lane ID-ROOM3's repair 2 (the verify of repair 1): the stray figures and words, the epoch's cohorts, the long
    fractions."""
    def counts_in(member: str, form: str = ""):
        return lambda cell: ({day for day in (counted_day(cell.replace(",", "."), member),) if day is not None}
                             | (text_days(cell, form) if form else set()))

    header, rows, typed_counted, persons = stray_figure_table()
    readers = {name: counts_in(member, form) for name, member, form in STRAY_FIGURES}
    for mode in ("U", "D", "N"):
        typed = list(typed_counted) if mode in ("D", "N") else []
        wanted: "dict[str, list[str]]" = {}
        if mode in ("D", "N"):
            wanted = {"person_ref": ["identifier"], **{name: ["dates"] for name in readers}}
            if mode == "N":
                wanted.update({name: ["no", "dates"] for name in readers})
        run = pipeline(scratch / f"figures-{mode}", header, rows, typed, wanted)
        if "failed" in run:
            value["runs_not_written"] += 1
            lines.append(f"stray figures {mode}: NOT WRITTEN, exits {run['exits']}")
            continue
        held_columns_of(run, header, rows, persons, readers, f"stray_figure_{mode}", f"stray figures {mode}")
        lines.append(f"stray figures {mode}: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")
    header, rows, persons = epoch_cohort_table()
    readers = {name: counts_in(member) for name, member in EPOCH_COHORTS}
    for mode in ("U", "P"):
        run = pipeline(scratch / f"cohorts-{mode}", header, rows, [], {} if mode == "U" else {
            "person_ref": ["identifier"]})
        if "failed" in run:
            value["runs_not_written"] += 1
            lines.append(f"epoch cohorts {mode}: NOT WRITTEN, exits {run['exits']}")
            continue
        held_columns_of(run, header, rows, persons, readers, f"epoch_cohort_{mode}", f"epoch cohorts {mode}")
        lines.append(f"epoch cohorts {mode}: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")
    header, rows, persons = fraction_table()
    readers = {name: counts_in(member) for name, member in FRACTIONS}
    run = pipeline(scratch / "fractions-U", header, rows, [], {})
    if "failed" in run:
        value["runs_not_written"] += 1
        lines.append(f"long fractions U: NOT WRITTEN, exits {run['exits']}")
    else:
        held_columns_of(run, header, rows, persons, readers, "long_fraction_U", "long fractions U")
        lines.append(f"long fractions U: exits {run['exits']}, {run['cpu']} CPU s, missed {run['missed']}")


def the_zoo(scratch: pathlib.Path) -> None:
    import health_zoo as zoo

    table = zoo.table_named("day_numbers")
    folder = scratch / "zoo"
    header, rows = table.build(ROWS, zoo.seed_of(table))
    result = zoo.run_table(table, folder, ROWS, zoo.seed_of(table), small_tables_refused=True)
    document = json.loads((folder / "day_numbers-profile.json").read_text(encoding="utf-8"))
    blocks = {block["name"]: block for block in document["columns"]}
    with open(folder / "day_numbers-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for name in ("visit_day_number", "birth_day", "admit_day_fixed", "discharge_day_text"):
        if blocks.get(name, {}).get("role") != "identifier":
            continue
        place = header.index(name)
        real = {day for day in (counted_day(row[place], "days-since-1840") for row in rows) if day is not None}
        on = sum(1 for row in twin[1:] if counted_day(row[twin[0].index(name)], "days-since-1840") in real)
        tally("zoo_held_day_numbers", on, 0, 0, f"zoo day_numbers.{name}: {on} twin cells on a real day, "
              f"steps {[(step, entry.get('exit')) for step, entry in result['steps'].items()]}")


with tempfile.TemporaryDirectory() as folder:
    started = time.process_time()
    the_planning_tables(pathlib.Path(folder))
    the_shapes(pathlib.Path(folder))
    the_repair_tables(pathlib.Path(folder))
    the_repair2_tables(pathlib.Path(folder))
    the_zoo(pathlib.Path(folder))
    lines.append(f"{round(time.process_time() - started)} CPU s in all")
for line in lines:
    print(line)
if os.environ.get("KPI_DATES_NEVER_REAL_LINES"):
    pathlib.Path(os.environ["KPI_DATES_NEVER_REAL_LINES"]).write_text(
        "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
value.setdefault("runs_not_written", 0)
kpi_rules.emit("K-HZ-38", value, f"2 tables x {len(MODES)} modes, 7 shapes, repair 1's 4 tables in 7 runs, repair "
               f"2's 3 tables in 6 runs and the zoo's held day numbers at {ROWS:,} rows and {PEOPLE:,} patients")
if "--kpi" not in sys.argv[1:]:
    print(json.dumps(value, indent=1, sort_keys=True))

"""K-HZ-29: Safe Harbor ages read with their words and counted in people, per form and spelling family at 20,000 rows and 1,000 people (plan P4-D477).

Lane HB2's four parts, each through the command a person types --
`profile` with nobody at the keyboard, the questions file answered round
by round where the leg says so, `generate` at seed 0, `validate` -- on
invented tables at the owner's floor, counted by linear counters (a set
of each column's real spellings, each twin cell read once):

- THE AGE WORDS (`taxonomy.AGE_VOCABULARY`): thirteen families of words
  before or around the number (`Age NN`, `age: NN`, `AGE=NN`, `Age - NN`,
  `aged NN`, `Age NN yrs`, `(NN yrs)`, `NN (years)`, `age NNN` to 105, `Age
  NN months` to 1,300 months, and since lane HB2's repair 2 `Age (NN) years`,
  `Age [NN] years` and `Age .NNe2`) and the five read before them (`NN yrs`, `NNy`,
  `NN years old`, `NN-year-old`, `NN y/o`), one a person, 1,000 people of
  20 rows, the column alone under a generic name, unanswered and answered
  `yes` (the truthful answer); `Age NN` beside a declared person column too.
  Keys: ages past 89 shown in any file or on the screen
  (`ages_past_89_shown`), twin cells past 89 (`ages_past_89_written`; a
  held column's made-up cells read as their cells are written, real past-89
  spellings alone), twin cells holding a real past-89 spelling inside a
  wider cell (`real_runs_inside`), families whose question was put
  (`families_asked`, of `families`), and words that are no age (`Stage`,
  `Grade`, `Room`, `Week`, `Score`) put a Safe Harbor question
  (`false_alarm_questions`). And `Age 18` to `Age 105` beside 2,000 `Age
  126` to `Age 225` under five headings (an age, a neutral, a code-like, a
  label and a note heading): the headings whose question was put
  (`headings_asked`, of 5), their ages past 89 counted with the families'.
- THE PEOPLE-COUNTED AGE READING: the visit table `ST2-AGE`
  (`patient_enumeration.st2_rows`, ages about 55 +/- 12 clamped to 25 to
  90, one a patient) at the table floor -- the fewest patients from 3,000
  up, in steps of 10, whose rows reach 20,000 (at 3,000 patients the table
  holds fewer, which the command refuses) -- seeds 21 to 23, through the
  command: the age column held as record numbers (`st2age_held`), classed
  patient-fixed by the patient layer (`st2age_patient_fixed`), its twin
  not valid (`st2age_validate_not_0`), every number the block publishes
  and every bin group 1 to 10 patients hold (`bands_below_floor`), and the
  twin patients the default command writes holding two ages or more
  (`st2age_two_ages_twin_patients`: every row's age is drawn as a number's
  is, the patient walk being lane GRb2's, not on this line); the same
  ages capped at 89, no age past it, four draws through the describe and
  one through the command, held (`st2age_capped89_held`: the ends' reach
  is the top-coded column; owner HB3-a2); and 34 draws at 1,000 people of
  20 rows held (`floor_draws_held`), their published numbers and bin
  groups counted in people into `bands_below_floor`, the bands' price
  printed.
- THE TOP CODE'S BOUND: the zoo's vitals export, unanswered: twin weight
  cells past the top code its description publishes
  (`top_code_cells_past`).
- THE ENDS IN EVERY UNIT (lane HB2's repair 2): ages written in years,
  months, weeks and days and every mixed pair beside a declared person
  column (2,000 people of 10 rows), five people at each end and the top code
  itself: the tables whose ends are not drawn, or pass the top code, or
  whose description does not load, generate and validate with exit 0
  (`units_not_loaded`).
- THE POOL'S START AFTER `no`: a code column whose one rare value is the
  pool's constant start (`8888` beside the key `8889`; `88` and `8888`
  beside levels `1` to `5`), answered `no`; and declared codes `+1` to `+5`
  beside one person's `+88`, and `1.1` to `5.1` beside `88.8`, given `no`
  through the describe (they put no question): the rare value in the
  description and in the twin (`pool_start_rare`), the column held
  (`pools_held`).
- THE COUNTERS SEE: each widened counter on a block made to publish
  what it counts (a value 3 people hold, a figure 95 in a label key, a figure
  95 in a key alone, a bin group of 5 people, a bin group at a tail's edge
  whose interior rows 5 people hold) reads it (`counters_blind`, the
  counters that read none). A bin group's people are counted over the rows
  its count covers, the tails' rows set aside by rank. `ages_past_89_shown` counts the real spellings past 89 in every
  file and on the screen, and every figure past 90 years the column's
  block holds in a key, a label, a text value or a value key.
- THE PRICE BY NAME: over the zoo's catalogue at 20,000 rows, the columns
  the age words newly bring into the age reach, their evidence read as a
  name's (`zoo_columns_newly_reached`, each named in the detail).

    .venv/bin/python tools/measurements/kpi_age_words.py --kpi
"""

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import shutil
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import health_zoo  # noqa: E402
import patient_enumeration  # noqa: E402

from synthtwin import chain, cli, parsing, profile, reading, taxonomy  # noqa: E402

ROWS = 20_000
PEOPLE = 1_000
A_PERSON = ROWS // PEOPLE
COLUMN = "record_label"
DRAW = random.Random(20261110)
AGES = [DRAW.randint(18, 95) for _person in range(PEOPLE)]
AGES_WIDE = [DRAW.randint(18, 105) for _person in range(PEOPLE)]
MONTHS = [DRAW.randint(0, 1300) for _person in range(PEOPLE)]
FAMILIES = {
    "Age NN": (lambda age: f"Age {age}", AGES, 1),
    "age: NN": (lambda age: f"age: {age}", AGES, 1),
    "AGE=NN": (lambda age: f"AGE={age}", AGES, 1),
    "Age - NN": (lambda age: f"Age - {age}", AGES, 1),
    "aged NN": (lambda age: f"aged {age}", AGES, 1),
    "Age NN yrs": (lambda age: f"Age {age} yrs", AGES, 1),
    "(NN yrs)": (lambda age: f"({age} yrs)", AGES, 1),
    "NN (years)": (lambda age: f"{age} (years)", AGES, 1),
    "age NNN": (lambda age: f"age {age}", AGES_WIDE, 1),
    "Age NN months": (lambda age: f"Age {age} months", MONTHS, 12),
    "Age (NN) years": (lambda age: f"Age ({age}) years", AGES, 1),
    "Age [NN] years": (lambda age: f"Age [{age}] years", AGES, 1),
    "Age .NNe2": (lambda age: f"Age .{age}e2", AGES, 1),
    "NN yrs": (lambda age: f"{age} yrs", AGES, 1),
    "NNy": (lambda age: f"{age}y", AGES, 1),
    "NN years old": (lambda age: f"{age} years old", AGES, 1),
    "NN-year-old": (lambda age: f"{age}-year-old", AGES, 1),
    "NN y/o": (lambda age: f"{age} y/o", AGES, 1),
}
NOT_AGES = {
    "Stage N": lambda person: f"Stage {1 + person % 4}",
    "Grade N": lambda person: f"Grade {1 + person % 3}",
    "Room NNN": lambda person: f"Room {100 + person % 30}",
    "Week NN": lambda person: f"Week {1 + person % 96}",
    "Score NN": lambda person: f"Score {person % 101}",
}
NUMBER = re.compile(r"\d+")


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]", delimiter: str = ",") -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter=delimiter, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def _offered(questions: pathlib.Path, column: str) -> "list[list[str]]":
    if not questions.is_file():
        return []
    entries = json.loads(questions.read_text(encoding="utf-8")).get("asked", [])
    return [[f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]
            for entry in entries if entry.get("column") == column]


def _run(folder: pathlib.Path, source: pathlib.Path, column: str, declared: "list[str]", answer: str) -> "dict":
    """profile; with ``answer``, up to three rounds giving it to every question of the column offering it; generate; validate."""
    questions = folder / "t-questions.json"
    screen = io.StringIO()
    exits: "list[int]" = []
    asked: "list[list[str]]" = []
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"] + declared)]
        asked = _offered(questions, column)
        for _round in range(3 if answer else 0):
            document = json.loads(questions.read_text(encoding="utf-8")) if questions.is_file() else {"asked": []}
            given = 0
            for entry in document.get("asked", []):
                offered = [f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]
                if entry.get("column") == column and not f"{entry.get('your_answer') or ''}" and answer in offered:
                    entry["your_answer"] = answer
                    given += 1
            if not given:
                break
            path = folder / "answers.json"
            path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{path}"]
                               + declared)]
        twin_folder = folder / "twin"
        twin_folder.mkdir(exist_ok=True)
        exits += [cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{twin_folder}", "--seed", "0",
                            "--replace"])]
        twin_path = twin_folder / f"{source.stem}-twin.csv"
        exits += [cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{twin_path}", "--out-dir",
                            f"{twin_folder}", "--replace"]) if twin_path.is_file() else -1]
    texts = [screen.getvalue()]
    for name in ("t-profile.json", "t-profile.txt", "t-questions.json"):
        if (folder / name).is_file():
            texts += [(folder / name).read_text(encoding="utf-8")]
    for name in sorted(twin_folder.glob("*.txt")):
        texts += [name.read_text(encoding="utf-8")]
    blocks = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"] if exits[0] == 0 else []
    block = next((one for one in blocks if one["name"] == column), {})
    twin: "list[list[str]]" = []
    if twin_path.is_file():
        with open(twin_path, encoding="utf-8", newline="") as handle:
            twin = list(csv.reader(handle))
    return {"exits": exits, "asked": asked, "texts": texts, "block": block, "twin": twin}


def _years(cell: str, in_months: int) -> float:
    found = NUMBER.search(cell)
    return -1.0 if found is None else int(found.group(0)) / in_months


# THE WIDENED COUNTERS (lane HB2's repair 1; the statistics check's item 4 and
# skeptic 1's item 8): what a block publishes, read whole. A figure is any run
# of figures in a key, a label or a text value of the block, and any number
# under a key that names a value (`_VALUE_KEYS`); counts, sizes and the
# block's sentences (`_SENTENCE_KEYS`) are no value.
_SENTENCE_KEYS = ("detection_evidence", "remarks", "name", "negative_form", "group_separator", "statistical_type",
                  "quality_state", "structural_role", "role", "n_distinct_by_occurrences", "field_widths",
                  "missing_by_class", "missing_by_source", "numeric_styles", "layout_forms", "layout_prefixes",
                  "layout_exclusions", "shape_forms", "figure_openings")
_VALUE_KEYS = ("percentiles", "percentiles_between", "mode", "mean", "top_coded_ends", "boundary", "values", "value")
# A rung's own name (`p95`) is no value.
_RUNG_NAME = re.compile(r"p\d\d")


def _figures_past(block: "dict[str, object]", in_months: int) -> int:
    """How many figures of a block, past 90 years in its unit, a key, a label, a text value or a value key holds (the top code 90 itself aside)."""
    found = 0
    waiting: "list[tuple[str, object, bool]]" = [("", block, False)]
    while waiting:
        key, leaf, valued = waiting.pop()
        if key in _SENTENCE_KEYS:
            continue
        if isinstance(leaf, dict):
            for inner in leaf:
                if not _RUNG_NAME.fullmatch(f"{inner}"):
                    found += sum(1 for run in NUMBER.findall(f"{inner}") if int(run) / in_months > 90)
                waiting += [(f"{inner}", leaf[inner], valued or key in _VALUE_KEYS)]
        elif isinstance(leaf, list):
            waiting += [(key, item, valued) for item in leaf]
        elif isinstance(leaf, str):
            found += sum(1 for run in NUMBER.findall(leaf) if int(run) / in_months > 90)
        elif isinstance(leaf, (int, float)) and not isinstance(leaf, bool) and (valued or key in _VALUE_KEYS):
            found += int(leaf / in_months > 90)
    return found


def _below_floor(block: "dict[str, object]", rows: "list[tuple[int, str]]", floor: int = 11) -> int:
    """How many numbers a block publishes (`profile._published_in`), and how many of its bin groups, 1 to ``floor`` - 1 people hold, ``rows`` each row's whole value as the block reads its cell and its person, in row order.

    A bin group's people are counted over the rows its count covers: the
    interior, the tails' published rows set aside at each end by rank, ties
    in row order (lane HB2's repair 2, the combined verify's item 1).
    """
    people: "dict[int, set[str]]" = {}
    for value, person in rows:
        people.setdefault(value, set()).add(person)
    found = 0
    for number in profile._published_in(block, True).numbers:
        if number == int(number) and 0 < len(people.get(int(number), set())) < floor:
            found += 1
    groups = block.get("bin_groups")
    tails = block.get("tails")
    points = block.get("percentiles") or {}
    if isinstance(groups, list) and groups and isinstance(points, dict):
        lowest = points.get("min")
        highest = points.get("max")
        if isinstance(tails, dict):
            low = (tails.get("low") or {}).get("percent")
            high = (tails.get("high") or {}).get("percent")
            between = {**points, **(block.get("percentiles_between") or {})}
            if isinstance(low, int) and isinstance(high, int):
                lowest = between.get(f"p{low:02d}", lowest)
                highest = between.get(f"p{high:02d}", highest)
        if isinstance(lowest, (int, float)) and isinstance(highest, (int, float)) and highest > lowest:
            low_rows = ((tails or {}).get("low") or {}).get("rows", 0) if isinstance(tails, dict) else 0
            high_rows = ((tails or {}).get("high") or {}).get("rows", 0) if isinstance(tails, dict) else 0
            ranked = sorted((value, place) for place, (value, _person) in enumerate(rows))
            held: "dict[int, set[str]]" = {}
            for value, place in ranked[int(low_rows): len(ranked) - int(high_rows)]:
                held.setdefault(parsing.histogram_bin(value, lowest, highest), set()).add(rows[place][1])
            for group in groups:
                if isinstance(group, dict):
                    union: "set[str]" = set()
                    for at in range(int(group.get("first", 0)), int(group.get("last", -1)) + 1):
                        union |= held.get(at, set())
                    found += int(0 < len(union) < floor)
    return found


def _counters_blind() -> "list[str]":
    """Each widened counter on a block made to publish what it counts: the names of those that read none (lane HB2's repair 1, LANE HB2 RULINGS 4 (5); repair 2, the combined verify's items 1 and 3)."""
    blind: "list[str]" = []
    if _figures_past({"levels": [{"label": "age 95", "count": 20, "variants": {"Age 95": 20}}]}, 1) < 1:
        blind += ["a figure 95 in a label key"]
    if _figures_past({"variants": {"Age 95": 20}}, 1) < 1:
        blind += ["a figure 95 in a key alone"]
    if _figures_past({"percentiles": {"max": 95.0}, "n_present": 20000}, 1) != 1:
        blind += ["a value 95 beside a count"]
    rows = [(age, f"P{age}-{who}") for age in range(30, 71) for who in range(3 if age == 31 else 40)]
    if _below_floor({"role": "count", "percentiles": {"min": 31.0, "p50": 50.0, "max": 70.0}}, rows) < 1:
        blind += ["a published value held by 3 people"]
    rows = [(age, f"P{age}-{who}") for age in range(30, 71) if age != 31 for who in range(5 if age == 30 else 40)]
    block: "dict[str, object]" = {"role": "count", "percentiles": {"min": 30.0, "max": 70.0}, "bin_groups": [
        {"first": 0, "last": 0, "count": 5}, {"first": 1, "last": 31, "count": 1560}]}
    unbinned = {key: block[key] for key in block if key != "bin_groups"}
    if _below_floor(block, rows) - _below_floor(unbinned, rows) < 1:
        blind += ["a bin group of 5 people"]
    # ...a group at a tail's edge: 15 people hold 25, 10 of them inside the
    # 200-row low tail, so its 100 interior rows are 5 people's.
    rows = [(25, f"P25-{who}") for who in range(15) for _row in range(20)]
    rows += [(age, f"P{age}-{who}") for age in range(28, 72) for who in range(15) for _row in range(20)]
    edge: "dict[str, object]" = {"role": "count", "percentiles": {"min": 25.0, "max": 71.0},
                                 "percentiles_between": {"p01": 25.0, "p99": 71.0},
                                 "tails": {"low": {"percent": 1, "rows": 200}, "high": {"percent": 99, "rows": 200}},
                                 "bin_groups": [{"first": 0, "last": 0, "count": 100}, {"first": 1, "last": 31, "count": 12000}]}
    unbinned = {key: edge[key] for key in edge if key != "bin_groups"}
    if _below_floor(edge, rows) - _below_floor(unbinned, rows) < 1:
        blind += ["a bin group at a tail's edge whose interior rows 5 people hold"]
    return blind


def _words(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    legs = [(family, False, "") for family in FAMILIES] + [(family, False, "yes") for family in FAMILIES]
    legs += [("Age NN", True, ""), ("Age NN", True, "yes")]
    asked_families: "dict[str, bool]" = {}
    for family, beside, answer in legs:
        make, ages, in_months = FAMILIES[family]
        cells = [make(ages[row // A_PERSON]) for row in range(ROWS)]
        folder = scratch / f"w{len(lines)}"
        folder.mkdir(parents=True)
        source = folder / "t.csv"
        if beside:
            _write(source, ["patient_key", COLUMN], [[f"{300000 + row // A_PERSON}", cells[row]] for row in range(ROWS)])
            declared = ["--identifier", "patient_key"]
        else:
            _write(source, [COLUMN], [[cell] for cell in cells])
            declared = []
        run = _run(folder, source, COLUMN, declared, answer)
        past = {cell for cell in cells if _years(cell, in_months) > 90}
        # ...each real spelling past 89 in any file or on the screen, and every
        # figure past 90 years the column's block holds (repair 1's counter).
        shown = sum(1 for spelling in past if any(spelling in text for text in run["texts"]))
        shown += _figures_past(run["block"], in_months)
        place = run["twin"][0].index(COLUMN) if run["twin"] else 0
        twin = [row[place] for row in run["twin"][1:]]
        # ...a held column's made-up cells read as written: only a real
        # past-89 spelling is an age written (LANE I4m RULINGS 21 (1)).
        held = run["block"].get("role") == taxonomy.ROLE_IDENTIFIER
        written = (
            sum(1 for cell in twin if cell in past)
            if held
            else sum(1 for cell in twin if _years(cell, in_months) > 90)
        )
        inside = sum(1 for cell in twin if cell not in past and any(spelling in cell for spelling in past))
        put = any("yes" in offered for offered in run["asked"])
        asked_families[family] = asked_families.get(family, False) or put
        for key, count in (("ages_past_89_shown", shown), ("ages_past_89_written", written), ("real_runs_inside", inside)):
            value[key] = int(value[key]) + count  # type: ignore[call-overload]
        value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + sum(  # type: ignore[call-overload]
            1 for code in run["exits"] if code not in (0, 3))
        lines += [f"{family}{' beside a person' if beside else ''} {answer or 'unanswered'}: role "
                  f"{run['block'].get('role')}, top {run['block'].get('top_coded')}, asked {run['asked']}, past 89 shown "
                  f"{shown}, written {written}, inside {inside}, exits {run['exits']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)
    value["families"] = len(FAMILIES)
    value["families_asked"] = sum(1 for family in asked_families if asked_families[family])
    # ...AND THE WORDS UNDER EVERY HEADING (lane HB2's repair 2, Codex's item
    # 2): strays past 125 beside them never take the column out of the reach.
    strayed = [f"Age {18 + row % 88}" for row in range(ROWS - 2000)] + [f"Age {126 + row % 100}" for row in range(2000)]
    past = {cell for cell in strayed if _years(cell, 1) > 90}
    value["headings_asked"] = 0
    for heading in ("age", "value", "item_code", "record_label", "visit_note"):
        folder = scratch / f"h{len(lines)}"
        folder.mkdir(parents=True)
        source = folder / "t.csv"
        _write(source, [heading], [[cell] for cell in strayed])
        run = _run(folder, source, heading, [], "")
        shown = sum(1 for spelling in past if any(spelling in text for text in run["texts"])) + _figures_past(run["block"], 1)
        place = run["twin"][0].index(heading) if run["twin"] else 0
        written = sum(1 for row in run["twin"][1:] if _years(row[place], 1) > 90)
        put = any("yes" in offered for offered in run["asked"])
        value["headings_asked"] = int(value["headings_asked"]) + int(put)  # type: ignore[call-overload]
        value["ages_past_89_shown"] = int(value["ages_past_89_shown"]) + shown  # type: ignore[call-overload]
        value["ages_past_89_written"] = int(value["ages_past_89_written"]) + written  # type: ignore[call-overload]
        value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + sum(  # type: ignore[call-overload]
            1 for code in run["exits"] if code not in (0, 3))
        lines += [f"strayed words under {heading}: role {run['block'].get('role')}, top {run['block'].get('top_coded')}, "
                  f"asked {run['asked']}, past 89 shown {shown}, written {written}, exits {run['exits']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)
    for family, make_word in NOT_AGES.items():
        folder = scratch / f"n{len(lines)}"
        folder.mkdir(parents=True)
        source = folder / "t.csv"
        _write(source, [COLUMN], [[make_word(row // A_PERSON)] for row in range(ROWS)])
        run = _run(folder, source, COLUMN, [], "")
        put = any("yes" in offered for offered in run["asked"])
        value["false_alarm_questions"] = int(value["false_alarm_questions"]) + int(put)  # type: ignore[call-overload]
        lines += [f"{family} (no age): role {run['block'].get('role')}, asked {run['asked']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)


def _people_by_age(rows: "list[list[str]]", ends: "object", subject: int = 0, age: int = 2) -> "list[tuple[int, str]]":
    """Each row's whole age, the ends drawn as the description reads them, and its person, in row order."""
    found: "list[tuple[int, str]]" = []
    for row in rows:
        read = int(row[age])
        if isinstance(ends, list) and len(ends) == 2:
            read = min(max(read, ends[0]), ends[1])
        found += [(read, row[subject])]
    return found


def _st2age(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    import dataclasses

    for seed in (21, 22, 23):
        # ...at the owner's table floor: the fewest patients from 3,000 up, in
        # steps of 10, whose rows reach 20,000 (the command refuses fewer);
        # through the command a person types (repair 1's item 4).
        patients = 3000
        header, rows = patient_enumeration.st2_rows(patients, seed, True)
        while len(rows) < ROWS:
            patients += 10
            header, rows = patient_enumeration.st2_rows(patients, seed, True)
        folder = scratch / f"st2age-{seed}"
        folder.mkdir(parents=True)
        path = folder / "t.csv"
        _write(path, header, rows)
        run = _run(folder, path, "age", ["--identifier", "sid"], "")
        block = run["block"]
        document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
        settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
        table = reading.read_table(str(path), small_cell_floor=11)
        chained = chain.describe(table, document, settings,
                                 chain.ChainSwitch("st2age", bytes(range(32)), rows_per_person=chain.ROWS_PERSON))
        classes = {entry["column"]: entry["class"] for entry in chained.grain["classes"]} if chained.grain else {}  # type: ignore[index]
        ends = block.get("top_coded_ends")
        below = _below_floor(block, _people_by_age(rows, ends))
        # ...and the twin patients holding two ages or more, as the default
        # command writes them (the patient walk is lane GRb's, not on this line).
        twin = run["twin"]
        ages_of: "dict[str, set[str]]" = {}
        if twin:
            place, person = twin[0].index("age"), twin[0].index("sid")
            for row in twin[1:]:
                ages_of.setdefault(row[person], set()).add(row[place])
        two = sum(1 for one in ages_of.values() if len(one) > 1)
        value["st2age_held"] = int(value["st2age_held"]) + int(block.get("role") == taxonomy.ROLE_IDENTIFIER)  # type: ignore[call-overload]
        value["st2age_patient_fixed"] = int(value["st2age_patient_fixed"]) + int(classes.get("age") == "patient_fixed")  # type: ignore[call-overload]
        value["bands_below_floor"] = int(value["bands_below_floor"]) + below  # type: ignore[call-overload]
        value["st2age_two_ages_twin_patients"] = int(value["st2age_two_ages_twin_patients"]) + two  # type: ignore[call-overload]
        value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + sum(  # type: ignore[call-overload]
            1 for code in run["exits"] if code not in (0, 3))
        value["st2age_validate_not_0"] = int(value["st2age_validate_not_0"]) + int(run["exits"][-1] != 0)  # type: ignore[call-overload]
        lines += [f"ST2-AGE seed {seed} ({len(rows)} rows, {patients} patients): role {block.get('role')}, ends {ends}, "
                  f"class {classes.get('age')}, published numbers and bin groups 1 to 10 patients hold {below}, "
                  f"twin patients holding two ages {two} of {len(ages_of)}, exits {run['exits']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)


def _capped(value: "dict[str, object]", lines: "list[str]", scratch: pathlib.Path) -> None:
    """ST2-AGE's ages capped at 89, no age past it (LANE HB2 RULINGS 4 (3)): four draws through the describe, one through the command; the ends' reach is the top-coded column, so such a column is held as before (owner HB3-a2)."""
    import dataclasses

    held = 0
    for seed in (31, 32, 33, 34, 35):
        draw = random.Random(seed)
        rows: "list[list[str]]" = []
        for subject in range(3000):
            age = int(min(89, max(25, draw.gauss(55, 12))))
            rows += [[f"S{subject:05d}", f"{age}"] for _visit in range(7)]
        folder = scratch / f"capped-{seed}"
        folder.mkdir(parents=True)
        path = folder / "t.csv"
        _write(path, ["sid", "age"], rows)
        if seed == 35:
            role = _run(folder, path, "age", ["--identifier", "sid"], "")["block"].get("role")
        else:
            settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
            table = reading.read_table(str(path), small_cell_floor=11)
            document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
            role = next(one for one in document["columns"] if one["name"] == "age")["role"]  # type: ignore[union-attr, index]
        held += int(role == taxonomy.ROLE_IDENTIFIER)
        lines += [f"ages capped at 89, 3,000 patients of 7 rows, draw {seed}"
                  f"{' through the command' if seed == 35 else ''}: role {role}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)
    value["st2age_capped89_held"] = held


def _draws(value: "dict[str, object]", lines: "list[str]", scratch: pathlib.Path) -> None:
    """The statistics check's 34 draws at 1,000 people of 20 rows (ages 55 +/- 12 clamped to 25 to 90): how many stay held, every published number and bin group counted in people, and the bands' price."""
    import dataclasses
    import statistics

    held = 0
    below = 0
    shares: "list[float]" = []
    spreads: "list[float]" = []
    lows: "list[int]" = []
    highs: "list[int]" = []
    for seed in range(1, 35):
        draw = random.Random(seed * 7919)
        ages = [min(90, max(25, int(round(draw.gauss(55, 12))))) for _person in range(PEOPLE)]
        rows = [[f"P{who:06d}", f"{ages[who]}"] for who in range(PEOPLE) for _row in range(A_PERSON)]
        path = scratch / f"draw-{seed}.csv"
        _write(path, ["sid", "age"], rows)
        settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
        table = reading.read_table(str(path), small_cell_floor=11)
        document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
        block = next(one for one in document["columns"] if one["name"] == "age")  # type: ignore[union-attr, index]
        path.unlink()
        if block["role"] == taxonomy.ROLE_IDENTIFIER:
            held += 1
            lines += [f"1,000 people of 20 rows, draw {seed}: held"]
            print(lines[-1], flush=True)
            continue
        ends = block.get("top_coded_ends")
        below += _below_floor(block, _people_by_age(rows, ends, 0, 1))
        if isinstance(ends, list):
            lows += [ends[0]]
            highs += [ends[1]]
            shares += [sum(1 for age in ages if age <= ends[0] or age >= ends[1]) / PEOPLE]
            pooled = [min(max(age, ends[0]), ends[1]) for age in ages]
            spreads += [statistics.pstdev(pooled) / statistics.pstdev(ages)]
    value["floor_draws_held"] = held
    value["bands_below_floor"] = int(value["bands_below_floor"]) + below  # type: ignore[call-overload]
    if shares:
        lines += [f"1,000 people of 20 rows, 34 draws: {held} held; the low band's value {min(lows)} to {max(lows)}, "
                  f"the top band's {min(highs)} to {max(highs)}; the bands hold {100 * min(shares):.1f} to "
                  f"{100 * max(shares):.1f} per cent of people (median {100 * statistics.median(shares):.1f}); "
                  f"the pooled SD {min(spreads):.2f} to {max(spreads):.2f} of the real (median {statistics.median(spreads):.2f}); "
                  f"published numbers and bin groups 1 to 10 people hold {below}"]
        print(lines[-1], flush=True)


def _in_unit(years: int, unit: str) -> str:
    """One whole age of ``years`` in a unit, the fewest whole units it holds: bare, `N months`, `N wk`, `N days`."""
    if unit == "y":
        return f"{years}"
    return f"{-((-years * taxonomy.AGE_MARKS[unit]) // 90)} " + {"m": "months", "w": "wk", "d": "days"}[unit]


def _units(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    """Ages in years, months, weeks and days and every mixed pair beside a declared person column, 2,000 people of 10 rows, five people the youngest and five at the top code, the rest 30 to 79 alike, each age's people written half in each unit of the pair, so the ends' bands, written in each cell's own unit, fall on spellings the floor's people hold: through the command, each description's ends at most its top code, the description loaded, its twin generated and valid (lane HB2's repair 2, Codex's item 1)."""
    value["units_not_loaded"] = 0
    people = 2 * PEOPLE
    for units in (("y",), ("m",), ("w",), ("d",), ("y", "m"), ("y", "w"), ("y", "d"), ("m", "w"), ("m", "d"), ("w", "d")):
        draw = random.Random(len(lines))
        ages = [20] * 5 + [90] * 5 + [30 + who % 50 for who in range(people - 10)]
        written = [_in_unit(ages[who], units[(who if who < 10 else (who - 10) // 50) % len(units)]) for who in range(people)]
        draw.shuffle(written)
        folder = scratch / f"u{len(lines)}"
        folder.mkdir(parents=True)
        source = folder / "t.csv"
        _write(source, ["sid", "age"], [[f"P{who:06d}", written[who]] for who in range(people) for _row in range(ROWS // people)])
        run = _run(folder, source, "age", ["--identifier", "sid"], "")
        top = run["block"].get("top_coded")
        ends = run["block"].get("top_coded_ends")
        bad = any(code != 0 for code in run["exits"]) or not (
            isinstance(ends, list) and isinstance(top, int) and 0 <= ends[0] <= ends[1] <= top)
        value["units_not_loaded"] = int(value["units_not_loaded"]) + int(bad)  # type: ignore[call-overload]
        lines += [f"ages in {'+'.join(units)}: role {run['block'].get('role')}, top {top}, ends {ends}, exits {run['exits']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)


def _vitals(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    table = health_zoo.table_named("vitals")
    header, rows = table.build(ROWS, health_zoo.seed_of(table))
    folder = scratch / "vitals"
    folder.mkdir(parents=True)
    source = folder / "t.csv"
    source.write_bytes(table.write(header, rows))
    run = _run(folder, source, "weight", [], "")
    top = run["block"].get("top_coded")
    past = 0
    twin_path = folder / "twin" / "t-twin.csv"
    if top and twin_path.is_file():
        with open(twin_path, encoding="utf-8", newline="") as handle:
            twin_rows = list(csv.reader(handle, delimiter=";"))
        place = twin_rows[0].index("weight")
        for row in twin_rows[1:]:
            found = re.match(r"\s*(\d+)(,\d+)?", row[place])
            if found and float(found.group(1) + (found.group(2) or "").replace(",", ".")) > top:
                past += 1
    value["top_code_cells_past"] = past
    value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + sum(  # type: ignore[call-overload]
        1 for code in run["exits"] if code not in (0, 3))
    lines += [f"vitals unanswered: weight role {run['block'].get('role')}, top {top}, twin cells past it {past}, "
              f"exits {run['exits']}"]
    print(lines[-1], flush=True)
    shutil.rmtree(folder, ignore_errors=True)


def _pool(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    value["pools_held"] = 0
    for name, key, rare, levels in (("8888 beside the key 8889", "8889", "8888", ("201", "202", "203", "204")),
                                    ("88 beside 1 to 5", "100000", "88", ("1", "2", "3", "4", "5")),
                                    ("8888 beside 1 to 5", "100000", "8888", ("1", "2", "3", "4", "5"))):
        folder = scratch / f"pool{len(lines)}"
        folder.mkdir(parents=True)
        source = folder / "t.csv"
        rows = [[key if who == 0 else f"{100000 + who}", rare if who == 0 else levels[(who * A_PERSON + row) % len(levels)]]
                for who in range(PEOPLE) for row in range(A_PERSON)]
        _write(source, ["patient_key", "kind"], rows)
        run = _run(folder, source, "kind", ["--identifier", "patient_key"], "no")
        in_block = json.dumps(run["block"]).count(f'"{rare}"')
        place = run["twin"][0].index("kind") if run["twin"] else 0
        cells = sum(1 for row in run["twin"][1:] if row[place] == rare)
        value["pool_start_rare"] = int(value["pool_start_rare"]) + in_block + cells  # type: ignore[call-overload]
        value["pools_held"] = int(value["pools_held"]) + int(run["block"].get("role") == taxonomy.ROLE_IDENTIFIER)  # type: ignore[call-overload]
        value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + sum(  # type: ignore[call-overload]
            1 for code in run["exits"] if code not in (0, 3))
        start = (run["block"].get("pool_in_people") or {}).get("number_from")
        lines += [f"pool after no, {name}: role {run['block'].get('role')}, start {start}, the rare value in the "
                  f"description {in_block}, in the twin {cells}, exits {run['exits']}"]
        print(lines[-1], flush=True)
        shutil.rmtree(folder, ignore_errors=True)
    # ...AND THE SIGNED AND DECIMAL CODES (lane HB2's repair 2, Codex's item 4),
    # declared codes that put no question, so `no` is given as the describe
    # takes it; generated from the loaded description.
    import dataclasses

    from synthtwin import canonical, contract, generation

    for name, rare, level in (("+88 beside +1 to +5", "+88", "+{}"), ("88.8 beside 1.1 to 5.1", "88.8", "{}.1")):
        path = scratch / "codes.csv"
        _write(path, ["patient_key", "kind"], [[f"{100000 + who}", rare if who == 0 else level.format(1 + (who * A_PERSON + row) % 5)]
                                               for who in range(PEOPLE) for row in range(A_PERSON)])
        table = reading.read_table(str(path), small_cell_floor=11)
        settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("patient_key",))
        document = profile.build_document(table, settings, ["patient_key"], ["kind"], [], subjects=["patient_key"],
                                          top_code=True, safe_harbor_no=["kind"])
        block = next(one for one in document["columns"] if one["name"] == "kind")  # type: ignore[union-attr, index]
        described = scratch / "codes-profile.json"
        # (the description's own bytes, which its loader writes again and compares)
        described.write_text(canonical.serialize(document), encoding="utf-8", newline="\n")
        twin = generation.generate(contract.load_profile(str(described)), 0)
        in_block = json.dumps(block).count(f'"{rare}"')
        cells = sum(1 for cell in twin.columns[twin.names.index("kind")] if parsing.parse_number(cell) == parsing.parse_number(rare))
        value["pool_start_rare"] = int(value["pool_start_rare"]) + in_block + cells  # type: ignore[call-overload]
        value["pools_held"] = int(value["pools_held"]) + int(block.get("role") == taxonomy.ROLE_IDENTIFIER)  # type: ignore[call-overload, union-attr]
        lines += [f"pool after no, {name} (the describe): role {block.get('role')}, start "  # type: ignore[union-attr]
                  f"{(block.get('pool_in_people') or {}).get('number_from')}, the rare value in the description {in_block}, "  # type: ignore[union-attr]
                  f"in the twin {cells}"]
        print(lines[-1], flush=True)
        path.unlink()
        described.unlink()


def _zoo_price(value: "dict[str, object]", lines: "list[str]") -> None:
    reached: "list[str]" = []
    for table in health_zoo.catalogue():
        header, rows = table.build(ROWS, health_zoo.seed_of(table))
        for place, name in enumerate(header):
            cells = [row[place] if place < len(row) else "" for row in rows]
            # ...the words read, and since lane HB2's repair 2 their evidence fed
            # to the reach as a name's is (Codex's item 2).
            named = taxonomy.ages_written_with_words(cells, False, frozenset({""}))
            if not named and not taxonomy.age_words_written(cells, False, frozenset()):
                continue
            before = taxonomy.safe_harbor_reach(cells, False, frozenset({""}), 11, True, False, taxonomy.TOP_CODE, False, False)
            after = taxonomy.safe_harbor_reach(cells, False, frozenset({""}), 11, True, False, taxonomy.TOP_CODE, named, True)
            if after != before:
                reached += [f"{table.name}.{name}"]
        del rows
    value["zoo_columns_newly_reached"] = len(reached)
    lines += [f"zoo columns the age words newly bring into the reach: {reached}"]
    print(lines[-1], flush=True)


value: "dict[str, object]" = {
    "ages_past_89_shown": 0, "ages_past_89_written": 0, "real_runs_inside": 0, "false_alarm_questions": 0,
    "exits_not_0_or_3": 0, "st2age_held": 0, "st2age_patient_fixed": 0, "bands_below_floor": 0, "pool_start_rare": 0,
    "st2age_two_ages_twin_patients": 0, "st2age_validate_not_0": 0,
}
lines: "list[str]" = []
blind = _counters_blind()
value["counters_blind"] = len(blind)
lines += [f"the widened counters on blocks made to publish what they count: blind {blind}"]
print(lines[-1], flush=True)
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    _words(scratch, value, lines)
    _st2age(scratch, value, lines)
    _capped(value, lines, scratch)
    _draws(value, lines, scratch)
    _units(scratch, value, lines)
    _vitals(scratch, value, lines)
    _pool(scratch, value, lines)
_zoo_price(value, lines)
# ...each leg's line kept beside kpi_run's report, which keeps only the KPI line.
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_age_words-items.txt"
ITEMS.parent.mkdir(parents=True, exist_ok=True)
ITEMS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
kpi_rules.emit("K-HZ-29", value, f"{len(lines)} legs at 20,000 rows and 1,000 people (ST2-AGE at the table floor, the fewest patients from 3,000 up whose rows reach 20,000)")

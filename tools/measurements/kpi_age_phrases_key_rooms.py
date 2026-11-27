"""K-HZ-35: ages inside free-text phrases and the held keys' room, per family and key shape at 20,000 rows and 1,000 people (plan P4-D482).

Lane HB3-a's parts, each leg through the command a person types --
`profile` with nobody at the keyboard, the questions file answered round by
round where the leg says so, `generate` at seed 0, `validate` -- on invented
tables at the owner's floor, counted by linear counters (a set of each
column's real spellings and runs, each twin cell read once):

- THE PHRASES (`taxonomy._phrase_age`): each family alone in its table
  (1,000 made-up people of 20 rows, no other column) and beside a person
  column, unanswered and answered `keep`: the Safe Harbor question put
  (`phrase_columns_not_asked`), real spellings past 89 in any file or on the
  screen (`ages_past_89_shown`, the top code 90 of a top-coded column aside),
  twin cells past 89 that are real spellings (`ages_past_89_written`, the
  same) and made-up ones (`made_up_past_89_written`: a held column's
  stand-ins carrying figures 90 to 99, none real, lane HB3-a2's part S, an
  at-most key), validate exits.
- THE WORDS THAT ARE NO AGE: eleven families alone, unanswered: reached as
  ages or asked the Safe Harbor question (`non_age_families_moved`).
- THE KEY ROOM (`generation._figure_runs_off_the_real`): a label column of
  two key forms (letters and bare numbers), of bare numbers, of numbers of
  six and seven figures, and of lettered keys with one of noughts alone,
  each beside a word on 30 per cent of rows: twin cells equal to a real key
  (`key_cells_equal_real`), equal once each run's noughts are dropped
  (`key_cells_merged_real`: the merged reading reads every run of noughts
  alone as one, the stated residue of limit (af), an at-most key), and twin
  cells holding a real run of four figures or more
  (`key_cells_real_run_inside`); the levels' own-form shape (fl_0x, part C3,
  left to lane HB3-a2 by the size valve) recorded apart
  (`own_form_runs_inside`, `own_form_cells_equal_real`, at-most keys at
  today's counts).
- THE PRICE BY NAME: over the zoo's catalogue at 20,000 rows, the columns
  the phrase reading newly brings into the age reach
  (`zoo_columns_newly_reached`, each named in the detail).

Since lane HB3-a's repair 1 (the orchestrator's LANE HB3-a RULINGS 6 and 7):
eleven families more -- `Age NN G.`, `NN g` beside both small letters, `Onset
age NN, current age NN`, `A NN-year-old man`, `0NN years`, `Age (months):
NNNN`, `NNy/G`, `Pt ageNN` and the characters that print nothing at a cell's
edges and inside the age word (X2, X3) -- each cell's age read on its own as
its largest run of figures over its unit's share of a year
(`tests/age_phrase_counts.py`, which the gate shows reading every file the bar
names, generate's twin report and validate's quality file among them); and the
own-form leg in fl_0x's own layout (levels on one span, held keys once each on
another), so its at-most keys record the class lane HB3-a2 lowers. Since its
repair 2 (the orchestrator's LANE HB3-a RULINGS 9): three families more --
`Age NN m` beside `Age NN girl` and an age word with a line break before the
words after it (`Age<LF>at diagnosis: NN`, `Age<NEL>in<NEL>years:<NEL>NN`) --
and the counter reads each spelling as the text files show a value too.

    .venv/bin/python tools/measurements/kpi_age_phrases_key_rooms.py --kpi
"""

import contextlib
import csv
import io
import json
import pathlib
import random
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import age_phrase_counts  # noqa: E402
import health_zoo  # noqa: E402

from synthtwin import cli, taxonomy  # noqa: E402

ROWS = 20_000
PEOPLE = 1_000
A_PERSON = ROWS // PEOPLE
COLUMN = "entry"
DRAW = random.Random(20261111)
AGES = [DRAW.randint(90, 105) if person % 33 == 0 else max(18, min(105, round(DRAW.gauss(60, 17))))
        for person in range(PEOPLE)]
GENDERS = [DRAW.choice("MF") for _person in range(PEOPLE)]
MONTHS = [DRAW.randint(0, 11) for _person in range(PEOPLE)]
# ...and an earlier age of each person, at most the age above (lane HB3-a's
# repair 1: two ages in one cell).
EARLIER = [max(1, AGES[person] - DRAW.randint(0, 20)) for person in range(PEOPLE)]
# This driver reads a cell's age on its own (`age_phrase_counts.years_of`: its
# largest run of figures over its unit's share of a year), never through the
# product.
FAMILIES = {
    "Age at diagnosis: NN": "Age at diagnosis: {a}",
    "Age (yrs): NN": "Age (yrs): {a}",
    "Pt age: NN": "Pt age: {a}",
    "Age ~NN": "Age ~{a}",
    "NN years N months": "{a} years {m} months",
    "NN y/o G": "{a} y/o {g}",
    "Age NN G": "Age {a} {g}",
    "Age NN, gender word": "Age {a}, {w}",
    "Age 0NN": "Age {a:03d}",
    "Age -NN": "Age -{a}",
    "Age<U+FF1A>NN": "Age：{a}",
    "NN years<U+00A0>old": "{a} years old",
    "Age.NN": "Age.{a}",
    "{{Age NN}}": "{{{{Age {a}}}}}",
    # ...lane HB3-a's repair 1: skeptic 1's items 1 to 4, the statistics
    # check's items 1, 2 and 7, and RULINGS 6's X2 and X3.
    "Age NN G.": "Age {a} {g}.",
    "NN g, both small letters": "{a} {gs}",
    "Onset age NN, current age NN": "Onset age {b}, current age {a}",
    "A NN-year-old man": "A {a}-year-old {mw}",
    "0NN years": "{a:03d} years",
    "Age (months): NNNN": "Age (months): {mo}",
    "NNy/G": "{a}y/{g}",
    "Pt ageNN": "Pt age{a}",
    "<U+200B>NN": "\u200b{a}",
    "NN<U+200B>": "{a}\u200b",
    "Ag<U+200B>e NN": "Ag\u200be {a}",
    # ...lane HB3-a's repair 2: the combined verify's items 1 and 2 (a lone
    # `m` beside the gender word `girl`; a line break before a letter).
    "Age NN m beside Age NN girl": "Age {a} {mg}",
    "Age<LF>at diagnosis: NN": "Age\nat diagnosis: {a}",
    "Age<NEL>in<NEL>years:<NEL>NN": "Age\u0085in\u0085years:\u0085{a}",
}
# The units of a year a family writes its age in, where not years.
SHARES = {"Age (months): NNNN": 12.0}
NOT_AGES = {
    "Stage N": "Stage {s4}", "Grade N": "Grade {s3}", "Room NNN": "Room {room}", "Week NN": "Week {w60}",
    "Score NN": "Score {sc}", "Age group N": "Age group {s6}", "Agent NN": "Agent {w60}", "Ages NN": "Ages {s90}",
    "Age N codes": "Age {s9}", "(NNN) amounts": "({s200})", "Aged care N": "Aged care {s5}",
}
NUMBER = re.compile(r"[0-9]+")


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _write(path: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)


def _run(folder: pathlib.Path, source: pathlib.Path, answer: str) -> "dict":
    """profile; with ``answer``, up to three rounds giving it to every question of the column offering it; generate; validate."""
    questions = folder / "t-questions.json"
    screen = io.StringIO()
    exits: "list[int]" = []
    asked: "list[list[str]]" = []
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace"])]
        for _round in range(3 if answer and exits[0] == 0 else 0):
            document = json.loads(questions.read_text(encoding="utf-8"))
            given = 0
            for entry in document.get("asked", []):
                offered = [f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]
                if entry.get("column") == COLUMN and not f"{entry.get('your_answer') or ''}" and answer in offered:
                    entry["your_answer"] = answer
                    given += 1
            if not given:
                break
            path = folder / "answers.json"
            path.write_text(json.dumps(document), encoding="utf-8", newline="\n")
            exits += [cli.main(["profile", f"{source}", "--out-dir", f"{folder}", "--replace", "--answers", f"{path}"])]
        if questions.is_file():
            asked = [[f"{one['answer']}" for one in entry.get("answers_you_can_give", [])]
                     for entry in json.loads(questions.read_text(encoding="utf-8")).get("asked", [])
                     if entry.get("column") == COLUMN]
        twin_folder = folder / "twin"
        twin_folder.mkdir(exist_ok=True)
        exits += [cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{twin_folder}", "--seed", "0",
                            "--replace"])]
        twin_path = twin_folder / f"{source.stem}-twin.csv"
        exits += [cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{twin_path}", "--out-dir",
                            f"{twin_folder}", "--replace"]) if twin_path.is_file() else -1]
    # ...the screen, the description, its summary and the questions file, and
    # generate's twin report and validate's quality file (skeptic 1's item 8).
    texts = age_phrase_counts.texts_of(folder, twin_folder, source.stem, screen.getvalue())
    blocks = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"] if exits[0] == 0 else []
    block = next((one for one in blocks if one["name"] == COLUMN), {})
    twin: "list[str]" = []
    if twin_path.is_file():
        with open(twin_path, encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        place = rows[0].index(COLUMN) if rows and COLUMN in rows[0] else -1
        twin = [row[place] for row in rows[1:] if 0 <= place < len(row)]
    return {"exits": exits, "asked": asked, "texts": texts, "block": block, "twin": twin}


def _cells(template: str) -> "list[str]":
    rows: "list[str]" = []
    for person in range(PEOPLE):
        cell = template.format(
            a=AGES[person], g=GENDERS[person], w="male" if GENDERS[person] == "M" else "female", m=MONTHS[person],
            s4=1 + person % 4, s3=1 + person % 3, room=100 + person % 60, w60=person % 60, sc=person % 101,
            s6=1 + person % 6, s90=person % 90, s9=1 + person % 9, s200=person % 200, s5=1 + person % 5,
            gs=GENDERS[person].lower(), b=EARLIER[person], mw="man" if GENDERS[person] == "M" else "woman",
            mo=AGES[person] * 12 + MONTHS[person], mg="m" if GENDERS[person] == "M" else "girl",
        )
        rows += [cell] * A_PERSON
    return rows


def _phrases(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    for family, template in FAMILIES.items():
        cells = _cells(template)
        share = SHARES[family] if family in SHARES else 1.0
        past = {cell for cell in cells if age_phrase_counts.years_of(cell, share) >= 90}
        for person_column in (False, True):
            header = ["subject_id", COLUMN] if person_column else [COLUMN]
            rows = [[f"S{100000 + place // A_PERSON}", cell] if person_column else [cell] for place, cell in enumerate(cells)]
            for answer in ("", "keep"):
                folder = scratch / f"p{len(lines)}"
                folder.mkdir()
                source = folder / "t.csv"
                _write(source, header, rows)
                run = _run(folder, source, answer)
                top = run["block"].get("top_coded") in (90, 1080)
                shown = age_phrase_counts.shown(past, run["texts"], top, share)
                real_cells = set(cells)
                past_twin = [cell for cell in run["twin"]
                             if age_phrase_counts.years_of(cell, share) > (90 if top else 89.999)]
                written = sum(1 for cell in past_twin if cell in real_cells)
                made_up = len(past_twin) - written
                asked = any("yes" in one and "no" in one for one in run["asked"])
                value["ages_past_89_shown"] = int(value["ages_past_89_shown"]) + len(shown)  # type: ignore[call-overload]
                value["ages_past_89_written"] = int(value["ages_past_89_written"]) + written  # type: ignore[call-overload]
                value["made_up_past_89_written"] = int(value["made_up_past_89_written"]) + made_up  # type: ignore[call-overload]
                if not answer and not asked and not top:
                    value["phrase_columns_not_asked"] = int(value["phrase_columns_not_asked"]) + 1  # type: ignore[call-overload]
                if run["exits"][-1] not in (0, 3) or run["exits"][0] != 0:
                    value["exits_not_0_or_3"] = int(value["exits_not_0_or_3"]) + 1  # type: ignore[call-overload]
                lines += [f"{family} person={person_column} answer={answer or '-'} role={run['block'].get('role')} "
                          f"top={top} asked={asked} shown={len(shown)} written={written} made_up={made_up} exits={run['exits']}"]
                print(lines[-1], flush=True)
        value["families"] = int(value["families"]) + 1  # type: ignore[call-overload]


def _not_ages(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    for family, template in NOT_AGES.items():
        folder = scratch / f"n{len(lines)}"
        folder.mkdir()
        source = folder / "t.csv"
        _write(source, [COLUMN], [[cell] for cell in _cells(template)])
        run = _run(folder, source, "")
        moved = bool(run["block"].get("top_coded")) or any("yes" in one and "no" in one for one in run["asked"])
        value["non_age_families_moved"] = int(value["non_age_families_moved"]) + int(moved)  # type: ignore[call-overload]
        lines += [f"no age: {family} role={run['block'].get('role')} moved={moved}"]
        print(lines[-1], flush=True)


def _strings(node: object, into: "set[str]") -> None:
    """Every string a description block holds, keys and values, at any depth: what it publishes."""
    if isinstance(node, str):
        into.add(node)
    elif isinstance(node, dict):
        for key, inner in node.items():
            into.add(f"{key}")
            _strings(inner, into)
    elif isinstance(node, list):
        for inner in node:
            _strings(inner, into)


def _merged(cell: str) -> str:
    """A key read with its case folded, its spaces dropped and the noughts before each run of figures dropped."""
    return re.sub(r"(?<![0-9])0+(?=[0-9])", "", "".join(cell.split()).casefold())


def _keys(scratch: pathlib.Path, value: "dict[str, object]", lines: "list[str]") -> None:
    draw = random.Random(4835)
    shapes = {
        "two forms": lambda k: f"R{100000 + k}" if k % 2 else f"{500000 + k}",
        "bare numbers": lambda k: f"{500000 + k}",
        "six and seven figures": lambda k: f"{999000 + k}",
        "lettered with noughts alone": lambda k: f"Q{k:05d}",
        "own-form levels (fl_0x)": lambda k: f"R{600000 + k // 2}X{700000 + k}",
    }
    for shape, key in shapes.items():
        cells: "list[str]" = []
        number = 0
        for _row in range(ROWS):
            if draw.random() < 0.3:
                cells += ["pending"]
            else:
                cells += [key(number)]
                number += 1
        if shape.startswith("own-form"):
            # ...fl_0x's own layout (lane HB3-a's repair 1, skeptic 1's item 9):
            # 400 published levels of two runs on one span, on 10,200 rows, and
            # 9,800 held keys once each in their form on another span.
            cells = [f"R{500000 + row % 400}X{200000 + row % 400}" for row in range(ROWS * 5100 // 10000)]
            cells += [f"R{600000 + held}X{700000 + held}" for held in range(ROWS - len(cells))]
        folder = scratch / f"k{len(lines)}"
        folder.mkdir()
        source = folder / "t.csv"
        _write(source, [COLUMN], [[cell] for cell in cells])
        run = _run(folder, source, "")
        published: "set[str]" = set()
        _strings(run["block"], published)
        real = {cell for cell in cells if cell != "pending" and cell not in published}
        merged = {_merged(cell) for cell in real}
        # ...a run of noughts alone is the merged reading's, counted apart above, never a real run inside.
        runs = {found for cell in real for found in NUMBER.findall(cell) if len(found) >= 4 and found.strip("0")}
        equal = 0
        merged_equal = 0
        inside = 0
        for cell in run["twin"]:
            if cell == "pending" or cell in published:
                continue
            if cell in real:
                equal += 1
                continue
            if _merged(cell) in merged:
                merged_equal += 1
                continue
            for found in NUMBER.findall(cell):
                if any(found[start:start + width] in runs for width in range(4, len(found) + 1)
                       for start in range(len(found) - width + 1)):
                    inside += 1
                    break
        if shape.startswith("own-form"):
            value["own_form_runs_inside"] = inside
            value["own_form_cells_equal_real"] = equal + merged_equal
        else:
            value["key_cells_equal_real"] = int(value["key_cells_equal_real"]) + equal  # type: ignore[call-overload]
            value["key_cells_merged_real"] = int(value["key_cells_merged_real"]) + merged_equal  # type: ignore[call-overload]
            value["key_cells_real_run_inside"] = int(value["key_cells_real_run_inside"]) + inside  # type: ignore[call-overload]
        lines += [f"keys: {shape} role={run['block'].get('role')} equal={equal} merged={merged_equal} inside={inside} "
                  f"noughts={run['block'].get('figure_noughts')} exits={run['exits']}"]
        print(lines[-1], flush=True)


def _zoo_price(value: "dict[str, object]", lines: "list[str]") -> None:
    reached: "list[str]" = []
    for table in health_zoo.catalogue():
        header, rows = table.build(ROWS, health_zoo.seed_of(table))
        for place, name in enumerate(header):
            cells = [row[place] if place < len(row) else "" for row in rows]
            seen: "dict[str, bool]" = {}
            phrased = False
            for cell in cells:
                if cell in seen or len(seen) > 5000:
                    continue
                seen[cell] = True
                read = taxonomy.safe_harbor_number(cell, False, True, True)
                if read is not None and read.phrase:
                    phrased = True
                    break
            if phrased and taxonomy.safe_harbor_reach(cells, False, frozenset({""}), 11) == taxonomy.SAFE_HARBOR_AGES:
                reached += [f"{table.name}.{name}"]
        del rows
    value["zoo_columns_newly_reached"] = len(reached)
    lines += [f"zoo columns the phrase reading brings into the reach: {reached}"]
    print(lines[-1], flush=True)


value: "dict[str, object]" = {
    "ages_past_89_shown": 0, "ages_past_89_written": 0, "made_up_past_89_written": 0, "phrase_columns_not_asked": 0,
    "exits_not_0_or_3": 0,
    "non_age_families_moved": 0, "key_cells_equal_real": 0, "key_cells_merged_real": 0, "key_cells_real_run_inside": 0,
    "own_form_runs_inside": 0, "own_form_cells_equal_real": 0, "families": 0,
}
lines: "list[str]" = []
with tempfile.TemporaryDirectory() as scratch_name:
    scratch = pathlib.Path(scratch_name)
    _phrases(scratch, value, lines)
    _not_ages(scratch, value, lines)
    _keys(scratch, value, lines)
_zoo_price(value, lines)
ITEMS = pathlib.Path(tempfile.gettempdir()) / "synthtwin-kpi" / "kpi_age_phrases_key_rooms-items.txt"
ITEMS.parent.mkdir(parents=True, exist_ok=True)
ITEMS.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
kpi_rules.emit("K-HZ-35", value, f"{len(lines)} legs at 20,000 rows and 1,000 people")

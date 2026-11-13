"""K-HZ-23 and K-HZ-24: rare values of category and code columns written as real vocabulary, at 20,000 rows (lane CODES-2, plan P4-D471).

K-HZ-23, THE CLOSED-LIST ANALYST. The zoo's tables holding the kinds lane
CODES-2's OWNERS lines named (`TARGET_KINDS`, thirty kinds over twenty-seven
tables), each run end to end at 20,000 rows with the shipped table floor on
(`health_zoo.run_table`: profile, the general answers round by round,
generate, validate). For every column of those kinds the twin describes as
labels (a constant, binary, categorical or long-tail column, or the words of
a column of numbers with labels; a long tail only where answered `code`, the
zoo plan's 2.3 naming none other) and no HIPAA rule holds, the twin cells off
the real column's closed list (`isin` over its real spellings) that read as
words or codes -- numbers too where the column is answered `code` -- are
counted (`closed_list_cells_failing_20000_rows`, target 0), named by kind;
recorded beside them, the columns that name their pool and the Safe Harbor
questions the lane's reason put (the price).

A long tail not answered `code` is outside this count (its stand-ins are
other lanes': the key-value answers' long tail, lane CZ-C; the typed values
read by key, lane CZ-H), as are the columns a HIPAA rule holds.

K-HZ-24, HIPAA FIRST (lane CODES-2's repair 1: skeptic 1's item 2, the
statistics skeptic's items 4 and 5, the orchestrator's LANE CODES-2 RULINGS
3 (2) and 4 (4)). THREE INVENTED TABLES of 20,000 rows, one a road, each
holding a column for every class the gate generates -- the 23 Safe Harbor
classes of 45 CFR 164.514(b)(2)(i) (`test_zoo_rare_names.CLASSES`) and, on
roads (ii) and (iii), the 22 families of words a column of numbers with
labels may hold (`WORD_FAMILIES`; repair 2 adds a record in another
script's figures, a note joined by spaces other than ASCII's, an age past
89 in words and a date in words; the follow-up nine more, `FOLLOW_UP_NEVER`:
one character that prints nothing inside a number word, a month's name, a
marked age or a clock, number words glued into one, a month beside a day in
figures, a word of about glued to an age, a decade past 89 and an age whose
marks stand apart, road (i) holding these nine too) -- 160 rare spellings of
the class, one to three rows each: road (i) five common levels beside them,
every column declared a code (`--code`); road (iii) the same columns undeclared; road
(ii) 17,000 or so readings to two places beside `QNS` and `Pending` and the
rare words, about 15 per cent words (at 0.5 per cent a column is read
`continuous`, `count` or `identifier` and the road is not reached: the
statistics skeptic's measurement). Each table runs through the command
three ways: unanswered, every Safe Harbor question answered `yes`, and
answered `no`. WHAT IS READ, exactly: each column's own block of the
description with its published levels set aside (each holds the floor's
rows or more, invariant B5; the age top-code `90` a rare age may be spelled
as is a pooled category), searched for every rare spelling as a JSON
string, and each twin cell of the column. A rare spelling found in the
block unanswered or after `yes` is a rare level published without the
person's `no` (`rare_levels_published_without_no_20000_rows`, ceiling 0),
SAVE the stated limit (a) of P4-D471 on road (ii): words of letters and
marks alone, which no shape tells from a result word (surnames, full names,
cities, counties, names and places written in letters, bare host names),
named by the screen with no question and counted apart with their twin
cells (`limit_a_*`). Also counted into the ceiling: a real value of a
column of the zoo's target tables that the zoo's own scan reads
(`health_zoo.leaked`); the stand-ins page's two carried cases at 20,000
rows (ZS.11 item 5, ten ZIP+4 labels on 1,990 rows each beside `UNKNOWN` on
100; item 7, the held shapes `ziprole`, `zip5word` and `zipwidth`), their
real values published or written in the twin; and the statistics skeptic's
table of words at 12 per cent (dates, records, ages, internet addresses
beside readings), its rare words published unanswered or after `yes`.
Recorded apart: the classes each road names after `no` (the person's
answer governs), and the twin cells meeting a rare spelling where nothing
was published (a made-up value drawn in a class's own form may meet a real
one by chance; the top-code's own spellings among them). Every count is
linear in the cells. The product's own times are printed apart from the
counting.

    .venv/bin/python tools/measurements/kpi_rare_names.py --kpi
"""

import collections
import csv
import json
import pathlib
import random
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import health_zoo  # noqa: E402
import kpi_rules  # noqa: E402
import test_zoo_rare_names as gate  # noqa: E402

from synthtwin import parsing, taxonomy  # noqa: E402

kpi_rules.guard_this_tree()

ROWS = health_zoo.KPI_ROWS
LABEL_ROLES = ("constant", "binary", "categorical", "long_tail_labels", "numbers_with_labels")
# The kinds lane CODES-2's OWNERS lines named on its base a391424c.
TARGET_KINDS = (
    "demographics", "diagnoses", "medication_orders", "imaging", "genomics", "perioperative", "labs",
    "mixed_results", "labelled_results", "pharmacy_dispensing", "social_history", "pediatrics", "cardiology_ecg",
    "organism_long_tail", "naaccr_and_trauma_registry", "remittance_835", "vcf_flattened", "diagnosis_code_forms",
    "procedure_and_drg_forms", "icd10_long_tail", "omop_cdm", "pcornet_cdm", "fhir_flattened", "warehouse_keys",
    "float_keys_export", "key_value_answers", "values_typed_by_key", "dates_as_results", "paired_clocks",
    "phi_columns",
)


def _cells_of(path: pathlib.Path) -> "dict[str, list[str]]":
    """A delimited file's columns, each as its cells, read as written."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.reader(handle))
    return {name: [row[place] for row in rows[1:] if place < len(row)] for place, name in enumerate(rows[0])}


class RunNotComplete(RuntimeError):
    """A run this driver reads did not complete, so no count is taken from it.

    Lane CODES-2's repair 2 (Codex's item 6 on the build, the orchestrator's
    LANE CODES-2 RULINGS 6 (4)): a twin missing a column was read as an
    empty column, so the closed-list check read 0 of its 2,185 offending
    cells, and a generate that exited 1 with no twin was read as no exposure
    at all. Now the driver STOPS: generate must exit 0, the twin must exist,
    and every column the count reads must be in it with every row.
    """


def _generated(exit_code: object, twin_path: pathlib.Path, where: str) -> None:
    """Generate exited 0 and wrote its twin, or the driver stops."""
    if exit_code != 0:
        raise RunNotComplete(f"{where}: generate exited {exit_code}; no count is read from it")
    if not twin_path.is_file():
        raise RunNotComplete(f"{where}: generate wrote no twin at {twin_path.name}")


def _complete_columns(twin: "dict[str, list[str]]", expected: "list[str]", rows: int, where: str) -> None:
    """Every column the count reads is in the twin, each with ``rows`` cells, or the driver stops."""
    missing = [name for name in expected if name not in twin]
    if missing:
        raise RunNotComplete(f"{where}: the twin lacks {missing}; an analyst's access would fail on it")
    short = [f"{name} ({len(twin[name])})" for name in expected if len(twin[name]) != rows]
    if short:
        raise RunNotComplete(f"{where}: the twin's columns {short} do not hold {rows} rows")


def _answered_code(result: "dict", column: str) -> bool:
    return any(entry["column"] == column and entry["given"] == "code" for entry in result.get("asked", []))


def closed_list(folder: pathlib.Path) -> "dict[str, object]":
    """K-HZ-23 over the target tables, each run once at 20,000 rows."""
    failing: "dict[str, int]" = {}
    named: "list[str]" = []
    asked = 0
    harbor_rare: "list[str]" = []
    seconds = 0.0
    for table in health_zoo.catalogue():
        kinds = {kind: cols for kind, cols in table.kinds.items() if kind in TARGET_KINDS}
        if not kinds or table not in health_zoo.runnable_tables((table,)):
            continue
        home = folder / table.name
        started = time.perf_counter()
        result = health_zoo.run_table(table, home, ROWS, health_zoo.seed_of(table), small_tables_refused=True)
        seconds = seconds + time.perf_counter() - started
        header, rows = table.build(ROWS, health_zoo.seed_of(table))
        asked = asked + sum(1 for entry in result.get("asked", []) if sorted(entry["offered"]) == ["no", "yes"])
        profile_path = home / f"{table.name}-profile.json"
        twin_path = home / f"{table.name}-twin{table.suffix}"
        if not twin_path.is_file():
            twin_path = home / f"{table.name}-twin.csv"
        _generated(result.get("steps", {}).get("generate", {}).get("exit"), twin_path, table.name)
        if not profile_path.is_file():
            raise RunNotComplete(f"{table.name}: no description was written")
        described = {block["name"]: block for block in json.loads(profile_path.read_text(encoding="utf-8"))["columns"]}
        frame = table.read(twin_path)["raw"]
        twin = {f"{name}": [f"{cell}" for cell in frame[name].tolist()] for name in frame.columns}  # type: ignore[attr-defined]
        del frame
        # EVERY TARGET COLUMN IS READ WHOLE: a twin lacking one, or holding it
        # short, stops the driver (Codex's item 6), never counts as nothing off.
        _complete_columns(twin, [column for columns in kinds.values() for column in columns], ROWS, table.name)
        # HIPAA FIRST, read by the zoo's own scan (`health_zoo.leaked`, every
        # column answered `identifier` or a Safe Harbor name rule reaches):
        # a real value of one found in a description or the twin.
        for key, found in sorted(result.get("leaks", {}).items()):
            if found["description"] or found["twin"]:
                harbor_rare += [f"{table.name}.{key}: {found['description']} in the description, {found['twin']} in the twin"]
        for kind, columns in kinds.items():
            for column in columns:
                place = header.index(column)
                real = collections.Counter(row[place] for row in rows if row[place] != "")
                if health_zoo.names_a_safe_harbor_element(table, column) or column in health_zoo.SAFE_HARBOR_ELEMENTS:
                    continue
                block = described.get(column, {})
                if block.get("role") not in LABEL_ROLES:
                    continue
                # ...A LONG TAIL NOT ANSWERED `code` is no closed list: the zoo
                # plan's 2.3 names none of it (its stand-ins are other lanes').
                if block.get("role") == "long_tail_labels" and not _answered_code(result, column):
                    continue
                if "held_back_names" in block or "held_back_names" in (block.get("labels") or {}):
                    named += [f"{table.name}.{column}"]
                code = _answered_code(result, column)
                off = 0
                for cell in twin.get(column, []):
                    if cell and cell not in real:
                        if code or parsing.classify_number(cell) == parsing.NOT_A_NUMBER:
                            off = off + 1
                if off:
                    failing[f"{kind}.{column}"] = off
        del rows
    return {
        "failing": failing,
        "named": named,
        "asked": asked,
        "harbor_rare": harbor_rare,
        "seconds": round(seconds, 1),
    }


ROADS = ("i", "ii", "iii")
# Letters and marks alone, which no shape tells from a result word: road (ii)
# names them with no question, P4-D471's stated limit (a), counted apart.
LIMIT_A_CLASSES = gate.UNSHAPED + gate.LIMIT_A
SPELLINGS = 160


def _road_classes(road: str) -> "tuple[str, ...]":
    """The classes a road's table holds: the 23 Safe Harbor classes, on roads (ii) and (iii) the word families, and on
    road (i) the follow-up's families (`gate.FOLLOW_UP_NEVER`: a character that prints nothing inside a refused shape,
    number words glued, the neighbour families), each after the classes so theirs keep their seeds."""
    return gate.CLASSES + gate.FOLLOW_UP_NEVER if road == "i" else gate.CLASSES + gate.WORD_FAMILIES


def _rare_spellings(kind: str, seed: int) -> "list[str]":
    """SPELLINGS different spellings of one class or one family, drawn from ``seed``."""
    if kind in gate.CLASSES:
        counted = collections.Counter(gate._rare_column(kind, seed, SPELLINGS))
        return sorted(value for value, count in counted.items() if count < health_zoo.FLOOR)
    return gate._family(kind, seed, SPELLINGS)


def _road_column(road: str, kind: str, seed: int) -> "tuple[list[str], set[str]]":
    """One column of a road's table at 20,000 rows, and its rare spellings (on road (ii) the words alone)."""
    draw = random.Random(seed)
    rare = _rare_spellings(kind, seed)
    if road == "ii":
        # A spelling read as a number joins the column's numbers, a measurement's
        # values and no word of this road: the words alone are counted.
        rare = [value for value, cell in zip(rare, taxonomy._classify_all(rare)) if cell.kind == "text"]
    cells: "list[str]" = []
    for place, value in enumerate(rare):
        cells += [value] * (1 + place % 3)
    if road == "ii":
        cells += ["QNS"] * 1600 + ["Pending"] * 1000
        while len(cells) < ROWS:
            cells += [f"{draw.uniform(1, 400):.2f}"]
    else:
        common = ("Alpha group", "Beta group", "Gamma group", "Delta group", "Omega group")
        while len(cells) < ROWS:
            cells += [draw.choice(common)]
    draw.shuffle(cells)
    return cells[:ROWS], set(rare)


def _write(source: pathlib.Path, columns: "dict[str, list[str]]", key: bool = True) -> None:
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow((["row_ref"] if key else []) + list(columns))
        for index in range(ROWS):
            writer.writerow(([f"R{5000000 + index}"] if key else []) + [columns[name][index] for name in columns])


def _answer_rounds(source: pathlib.Path, answers: "dict[str, str]", declared: "list[str]") -> None:
    """The gate's rounds (`test_zoo_rare_names._answer_rounds`), the command's declarations typed on every run."""
    folder = source.parent
    assert gate._run(["profile", str(source), "--replace"] + declared, True) == 0
    questions = folder / f"{source.stem}-questions.json"
    for _round in range(5):
        document = json.loads(questions.read_text(encoding="utf-8"))
        fresh = 0
        for entry in gate._entries(document):
            if f"{entry.get('your_answer') or ''}":
                continue
            offered = [f"{choice.get('answer')}" for choice in entry["answers_you_can_give"]]
            column = f"{entry.get('column', '')}"
            wanted = answers.get(column, "")
            if "no" in offered and "yes" in offered:
                wanted = answers.get(f"{column} harbor", "")
            if wanted in offered:
                entry["your_answer"] = wanted
                fresh = fresh + 1
        if not fresh:
            return
        questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert gate._run(["profile", str(source), "--replace", "--answers", str(questions)] + declared, True) == 0


def _blocks(profile_path: pathlib.Path) -> "dict[str, str]":
    """EACH COLUMN'S OWN BLOCK as text, its published levels set aside (each holds the floor's rows or more, B5).

    THE LEVELS SET ASIDE ARE READ TOO (Codex's item 6 on lane CODES-2's
    build): each level's label and each spelling of it it counts is
    returned apart by `_levels_published` with its count, so a rare
    spelling published as a level is counted, never hidden by the setting
    aside.
    """
    blocks: "dict[str, str]" = {}
    if not profile_path.is_file():
        raise RunNotComplete(f"no description at {profile_path.name}")
    for block in json.loads(profile_path.read_text(encoding="utf-8"))["columns"]:
        rest = {key: block[key] for key in block if key != "levels"}
        if isinstance(rest.get("labels"), dict):
            rest["labels"] = {key: rest["labels"][key] for key in rest["labels"] if key != "levels"}
        blocks[f"{block['name']}"] = json.dumps(rest, ensure_ascii=False)
    return blocks


def _levels_published(profile_path: pathlib.Path) -> "dict[str, dict[str, int]]":
    """Each column's published levels: every label and every spelling a level counts, with its count."""
    found: "dict[str, dict[str, int]]" = {}
    for block in json.loads(profile_path.read_text(encoding="utf-8"))["columns"]:
        spelled: "dict[str, int]" = {}
        for holder in (block, block.get("labels") if isinstance(block.get("labels"), dict) else {}):
            for entry in holder.get("levels") or []:
                spelled[f"{entry['label']}"] = int(entry["count"])
                for spelling, count in (entry.get("variants") or {}).items():
                    spelled[f"{spelling}"] = int(count)
        found[f"{block['name']}"] = spelled
    return found


def rare_as_levels(levels: "dict[str, int]", rare: "set[str]", floor: int) -> int:
    """The rare spellings a column's published levels name: a level under the floor, or one holding a rare spelling.

    A level the floor allows (B5) is the published census; a rare spelling
    that is one counts here whatever its count, save the top-code's own
    pooled category -- `90` written in the source's form, `90 years`,
    `90 yrs`, `90+` -- which a rare age may also be spelled as (the first
    reading of this check, on the repair's head, counted those three
    forms on roads (i) and (iii) unanswered and after `yes`, 12 in all).
    """
    named = 0
    for spelling, count in levels.items():
        if count < floor or (spelling in rare and not _the_top_codes_own(spelling, count, floor)):
            named = named + 1
    return named


def _the_top_codes_own(spelling: str, count: int, floor: int) -> bool:
    """Whether a published level is the age top-code's pooled category: on the floor's rows, its one run of figures 90."""
    runs = [run for run in "".join(ch if ch.isdigit() else " " for ch in spelling).split() if run]
    return count >= floor and runs == ["90"]


def battery(folder: pathlib.Path, road: str, how: str) -> "dict[str, object]":
    """K-HZ-24's table of one road, one class a column, run unanswered, answered `yes` or answered `no`."""
    folder.mkdir(parents=True, exist_ok=True)
    columns: "dict[str, list[str]]" = {}
    rare: "dict[str, set[str]]" = {}
    names: "dict[str, str]" = {}
    for place, kind in enumerate(_road_classes(road)):
        cells, spellings = _road_column(road, kind, 700 + place)
        if not spellings:
            continue
        name = f"c{place:02d}"
        columns[name] = cells
        rare[kind] = spellings
        names[kind] = name
    source = folder / "classes.csv"
    _write(source, columns)
    declared = [one for name in columns for one in ("--code", name)] if road == "i" else []
    # UNANSWERED is the Safe Harbor questions left open with the key answered
    # `identifier`: before that answer rule U (c) names nothing on any road (a
    # run nobody answers at all names nothing; the gate pins it).
    answers: "dict[str, str]" = {"row_ref": "identifier"}
    if how in ("yes", "no"):
        for name in columns:
            answers[f"{name} harbor"] = how
    started = time.perf_counter()
    _answer_rounds(source, answers, declared)
    generated = gate._run(["generate", str(folder / "classes-profile.json"), "--replace", "--seed", "0"], True)
    seconds = time.perf_counter() - started
    twin_path = folder / "classes-twin.csv"
    _generated(generated, twin_path, f"road ({road}) {how}")
    blocks = _blocks(folder / "classes-profile.json")
    levels = _levels_published(folder / "classes-profile.json")
    twin = _cells_of(twin_path)
    _complete_columns(twin, list(columns), ROWS, f"road ({road}) {how}")
    found: "dict[str, int]" = {}
    cells_written: "dict[str, int]" = {}
    for kind, name in names.items():
        written = blocks.get(name, "")
        found[kind] = sum(1 for value in rare[kind] if json.dumps(value, ensure_ascii=False) in written)
        found[kind] = found[kind] + rare_as_levels(levels.get(name, {}), rare[kind], health_zoo.FLOOR)
        # ...and the twin cells equal to a rare spelling: the names written where
        # the pool is named, else a made-up value meeting a real one by chance.
        cells_written[kind] = sum(1 for cell in twin.get(name, []) if cell in rare[kind])
    shutil.rmtree(folder, ignore_errors=True)
    return {"found": found, "cells": cells_written, "seconds": round(seconds, 1)}


def _command_table(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]",
                   answers: "dict[str, str] | None" = None) -> "dict[str, object]":
    """One invented table through profile (and the answers' rounds), generate (seed 0) and validate."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "table.csv"
    with source.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(header)
        writer.writerows(rows)
    if answers is None:
        profiled = gate._run(["profile", str(source), "--replace"], True)
    else:
        _answer_rounds(source, answers, [])
        profiled = 0
    described = folder / "table-profile.json"
    generated = gate._run(["generate", str(described), "--replace", "--seed", "0"], True) if profiled == 0 else -1
    validated = gate._run(["validate", str(described), "--replace"], True) if generated == 0 else -1
    text = described.read_text(encoding="utf-8") if described.is_file() else ""
    summary = folder / "table-profile.txt"
    text = text + (summary.read_text(encoding="utf-8") if summary.is_file() else "")
    twin = _cells_of(folder / "table-twin.csv") if (folder / "table-twin.csv").is_file() else {}
    out = {"exits": [profiled, generated, validated], "text": text, "twin": twin, "blocks": _blocks(described)}
    return out


def carried_cases(folder: pathlib.Path) -> "dict[str, object]":
    """The stand-ins page's ZS.11 items 5 and 7 at 20,000 rows, unanswered (the owner's carried conditions, CODES-2's)."""
    plus4 = [f"52240-{1000 + 37 * k:04d}" for k in range(10)]
    shapes = {
        "item 5 zip_plus4": [value for value in plus4 for _ in range(1990)] + ["UNKNOWN"] * 100,
        "item 7 ziprole binary": ["02100"] * 10000 + ["02107"] * 10000,
        "item 7 ziprole constant": ["02100"] * 20000,
        "item 7 ziprole count": ["2100", "2107", "52240", "52247"] * 5000,
        "item 7 zip5word": [f"0{2100 + 7 * (k % 40):04d}" for k in range(13000)] + ["-99"] * 7000,
        "item 7 zipwidth": ["2100", "2107", "52240", "52247"] * 3250 + ["-99"] * 7000,
        "item 7 zipwidth nines": [f"{2100 + 7 * (k % 40)}" for k in range(19000)] + ["99999"] * 1000,
    }
    failing_exits: "list[str]" = []
    exposed: "dict[str, int]" = {}
    for place, (shape, cells) in enumerate(shapes.items()):
        real = {cell for cell in cells if cell not in ("UNKNOWN", "-99")}
        run = _command_table(folder / f"z{place}", ["pid", "zip"], [[f"P{100000 + k}", cell] for k, cell in enumerate(cells)])
        if run["exits"] != [0, 0, 0]:
            failing_exits += [f"{shape}: {run['exits']}"]
        published = sum(1 for value in real if json.dumps(value) in run["text"] or f" {value} " in run["text"])  # type: ignore[operator]
        written = sum(1 for cell in run["twin"].get("zip", []) if cell in real)  # type: ignore[union-attr]
        exposed[shape] = published + written
        shutil.rmtree(folder / f"z{place}", ignore_errors=True)
    return {"failing_exits": failing_exits, "exposed": exposed}


# The statistics skeptic's table of words at 12 per cent (wave6/CODES-2-stat/probe_pathii2.py; the
# orchestrator's LANE CODES-2 RULINGS 4 (1): his red case), its rare words of each Safe Harbor shape.
TWELVE_PER_CENT = {
    "reading_dates": ["2023-07", "2023-07", "2023-07", "2024-02", "2024-02", "11/2022", "2021-W14", "2021-W14", "14-03"],
    "reading_records": ["#RC4821", "#RC4821", "REC-0042", "XXX-XX-6789", "ACCT 0815", "ABC 1234"],
    "reported_age": ["100+", "100+", "age 101", "95+", "95+", "95+"],
    "reading_internet": ["fe80::1", "face_0012.jpg", "face_0012.jpg", "jsmith(at)example.org", "example.org/jsmith",
                         "522**", "522**"],
}


def twelve_per_cent(folder: pathlib.Path, how: str) -> "dict[str, int]":
    """The statistician's table through the command at 20,000 rows: rare words found per column, and twin cells."""
    draw = random.Random(4471)
    columns: "dict[str, list[str]]" = {}
    for name, rare in TWELVE_PER_CENT.items():
        if name == "reported_age":
            cells = [f"{draw.randint(18, 89)}" for _ in range(ROWS - 2400 - len(rare))] + ["Unknown"] * 1400 + ["Refused"] * 1000
        else:
            cells = [f"{draw.uniform(1, 400):.2f}" for _ in range(ROWS - 2400 - len(rare))] + ["QNS"] * 1400 + ["Pending"] * 1000
        cells += rare
        draw.shuffle(cells)
        columns[name] = cells
    answers = None if how == "unanswered" else {f"{name} harbor": how for name in columns}
    run = _command_table(folder, list(columns), [[columns[name][index] for name in columns] for index in range(ROWS)], answers)
    _generated(run["exits"][1], folder / "table-twin.csv", f"twelve per cent {how}")  # type: ignore[index]
    _complete_columns(run["twin"], list(columns), ROWS, f"twelve per cent {how}")  # type: ignore[arg-type]
    found: "dict[str, int]" = {}
    for name, rare in TWELVE_PER_CENT.items():
        block = run["blocks"].get(name, "")  # type: ignore[union-attr]
        found[name] = sum(1 for value in set(rare) if json.dumps(value, ensure_ascii=False) in block)
        found[f"{name} twin"] = sum(1 for cell in run["twin"].get(name, []) if cell in set(rare))  # type: ignore[union-attr]
    shutil.rmtree(folder, ignore_errors=True)
    return found


def main() -> None:
    value: "dict[str, object]" = {}
    said: "list[str]" = []
    with tempfile.TemporaryDirectory(prefix="synthtwin-rare-names-") as scratch:
        listed = closed_list(pathlib.Path(scratch) / "zoo")
        failing = listed["failing"]
        value["closed_list_cells_failing_20000_rows"] = sum(
            count for count in failing.values() if count > 0  # type: ignore[union-attr]
        )
        value["closed_list_columns_failing_20000_rows"] = len(failing)  # type: ignore[arg-type]
        value["closed_list_columns_failing_named"] = ", ".join(
            f"{key}: {count}" for key, count in sorted(failing.items())  # type: ignore[union-attr]
        ) or "none"
        value["columns_naming_their_pool_20000_rows"] = len(listed["named"])  # type: ignore[arg-type]
        value["safe_harbor_questions_put_20000_rows"] = listed["asked"]
        said += [f"zoo target tables: {listed['seconds']} s of the product's runs; named {listed['named']}"]
        without_no = len(listed["harbor_rare"])  # type: ignore[arg-type]
        for road in ROADS:
            limit_names: "dict[str, int]" = {}
            limit_cells: "dict[str, int]" = {}
            for how in ("unanswered", "yes", "no"):
                run = battery(pathlib.Path(scratch) / f"road-{road}-{how}", road, how)
                found = run["found"]
                cells = run["cells"]
                key = f"road_{road}"
                if how == "no":
                    value[f"classes_named_after_no_{key}_20000_rows"] = ", ".join(
                        f"{kind}: {count}" for kind, count in found.items() if count  # type: ignore[union-attr]
                    ) or "none"
                else:
                    counted = 0
                    for kind, count in found.items():  # type: ignore[union-attr]
                        if road == "ii" and kind in LIMIT_A_CLASSES:
                            limit_names[f"{kind} {how}"] = count
                            limit_cells[f"{kind} {how}"] = cells[kind]  # type: ignore[index]
                        else:
                            counted = counted + count
                    without_no = without_no + counted
                    value[f"rare_levels_published_{how}_{key}_20000_rows"] = counted
                    value[f"twin_cells_meeting_a_rare_value_{how}_{key}_20000_rows"] = ", ".join(
                        f"{kind}: {count}" for kind, count in cells.items()  # type: ignore[union-attr]
                        if count and not (road == "ii" and kind in LIMIT_A_CLASSES)
                    ) or "none"
                said += [f"road ({road}) {how}: {run['seconds']} s"]
            if road == "ii":
                value["limit_a_names_published_road_ii_20000_rows"] = ", ".join(
                    f"{kind}: {count}" for kind, count in limit_names.items()) or "none"
                value["limit_a_twin_cells_road_ii_20000_rows"] = ", ".join(
                    f"{kind}: {count}" for kind, count in limit_cells.items()) or "none"
        started = time.perf_counter()
        carried = carried_cases(pathlib.Path(scratch) / "carried")
        value["zs11_carried_cases_failing_exits_20000_rows"] = len(carried["failing_exits"])  # type: ignore[arg-type]
        value["zs11_carried_cases_real_values_published_or_written_20000_rows"] = sum(carried["exposed"].values())  # type: ignore[union-attr]
        said += [f"ZS.11 items 5 and 7: {round(time.perf_counter() - started, 1)} s; {carried}"]
        for how in ("unanswered", "yes", "no"):
            found = twelve_per_cent(pathlib.Path(scratch) / f"twelve-{how}", how)
            words = sum(count for name, count in found.items() if not name.endswith("twin"))
            value[f"twelve_per_cent_words_published_{how}_20000_rows"] = words
            if how != "no":
                without_no = without_no + words
            said += [f"twelve per cent {how}: {found}"]
        value["rare_levels_published_without_no_20000_rows"] = without_no
        value["safe_harbor_zoo_columns_publishing_20000_rows"] = "; ".join(listed["harbor_rare"]) or "none"  # type: ignore[arg-type]
    kpi_rules.emit("K-HZ-23", {key: value[key] for key in value if key.startswith(("closed_list", "columns_naming", "safe_harbor_questions"))}, "; ".join(said))
    kpi_rules.emit("K-HZ-24", {key: value[key] for key in value if key.startswith(
        ("rare_levels", "classes_named", "safe_harbor_zoo", "twin_cells_meeting", "limit_a", "zs11", "twelve_per_cent"))},
        "; ".join(said))


if __name__ == "__main__":
    main()

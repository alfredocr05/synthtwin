"""Gate file of batch 4w's outside review, fix round, worker A (plans P4-D496 and P4-D497): six items, each red on the 4w head.

Every case runs the shipped commands on an invented table of 20,000 rows
(profile, the answers written into the questions file, then generate), the
inside record written in a private folder of the test's own, so the twin is
drawn from the record exactly as on a protected computer. Each is red on the
4w integration head b9165d2d and on a mutant of its fix (the fix round's
report names each mutant).

* ITEM 1. A top-coded age column whose rows past 89 are written as censored
  spellings (`>95`, `>90`): the drawn twin writes no spelling that names an
  age past the top category, whether the spelling is the column's highest
  value held by many rows (a spike) or a censored value inside its range (an
  atom); each is written `>89`, as the description writes it.
* ITEM 10. The dates zone reads each date column as the description does:
  a column of day-first dates read with `--day-first` is written day first
  (no twin cell invalid as day, month, year), and a column of days since
  1970 the person declared with `--date-count` is carried by the zone.
* ITEM 11. A measurement written with an exponent (`1.234e-6`) keeps its
  scale and its spelling: no twin cell is `0`.
* ITEM 12. Two date columns of one table each keep their own weekdays: a
  column of Fridays is never written on Mondays because another column of
  Mondays was written first.
* ITEM 13. Stamps keep their order and their interval as instants: a start
  written either `09:00+02:00` or `07:00Z` and an end 30 minutes later keep
  30 minutes on every row; a start at `.100` and an end at `.200` of the same
  second keep a tenth of a second on every row.
* ITEM 19. The offline audit passes the generate step's dates block and its
  helper (no method call on a value it cannot trace).
"""

from __future__ import annotations

import ast
import csv
import datetime
import importlib.util
import io
import json
import pathlib
import random
import re

import typing

import pytest

import reliability_battery as B
from synthtwin import inside, installation

ROWS = 20000
REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


# -- the route: the shipped commands, the record in the test's own private folder ---------------------------


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _entries(document: object) -> "list[dict[str, object]]":
    found: "list[dict[str, object]]" = []
    if isinstance(document, dict):
        for key in ("asked", "about_your_file", "about_your_table"):
            value = document.get(key)
            if isinstance(value, list):
                found += [entry for entry in value if isinstance(entry, dict)]
    return found


def _answered(questions: pathlib.Path, answers: "dict[str, str]") -> bool:
    """The given answers (column -> answer) written into the questions file, and the subject question answered."""
    if not questions.exists():
        return False
    document = json.loads(questions.read_text(encoding="utf-8"))
    wrote = False
    for entry in _entries(document):
        column = str(entry.get("column", ""))
        if not entry.get("your_answer") and column in answers:
            entry["your_answer"] = answers[column]
            wrote = True
    between = document.get("between_columns") if isinstance(document, dict) else None
    question = between.get("rows_per_person") if isinstance(between, dict) else None
    if isinstance(question, dict) and not question.get("your_answer"):
        question["your_answer"] = "one row each"
        wrote = True
    if wrote:
        questions.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
                             newline="\n")
    return wrote


def _route(folder: pathlib.Path, stem: str, text: str, extra: "tuple[str, ...]" = (),
           answers: "dict[str, str] | None" = None,
           seeds: "tuple[int, ...]" = (0,)) -> "tuple[dict[int, str], dict[str, object], dict[str, object]]":
    """Profile with the answers given, then generate at each seed: the twins, the description and the record."""
    source = folder / "table" / f"{stem}.csv"
    out = folder / "out"
    source.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    source.write_text(text, encoding="utf-8", newline="\n")
    twins: "dict[int, str]" = {}
    with pytest.MonkeyPatch.context() as patch, B.installed(folder):
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = B.command(["profile", str(source), "--out-dir", str(out), "--replace", *extra], False)
        assert code == 0, said
        questions = out / f"{stem}-questions.json"
        for _round in range(3):
            if not _answered(questions, answers or {}):
                break
            again = ["profile", str(source), "--out-dir", str(out), "--answers", str(questions), *extra]
            code, said = B.command(again, False)
            if code != 0:
                code, said = B.command(again + ["--replace-description"], False)
            assert code == 0, said
        description = out / f"{stem}-profile.json"
        for seed in seeds:
            done, words = B.command(["generate", str(description), "--out-dir", str(out), "--seed", str(seed),
                                     "--replace"], False)
            assert done == 0, words
            twins[seed] = (out / f"{stem}-twin.csv").read_text(encoding="utf-8")
    found = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert found, "no inside record was written"
    record = inside.load_record(found[0])
    document = json.loads(description.read_text(encoding="utf-8"))
    return twins, document, record


def _table(header: "tuple[str, ...]", rows: "list[tuple[str, ...]]") -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    return buffer.getvalue()


def _column(text: str, name: str) -> "list[str]":
    return [row[name] for row in csv.DictReader(io.StringIO(text))]


def _dates_zone(record: "dict[str, object]") -> "dict[str, object]":
    zones = record["zones"]
    assert isinstance(zones, dict)
    zone = zones["dates"] if "dates" in zones else {}
    assert isinstance(zone, dict)
    return zone


# -- item 1: censored ages past the top category ----------------------------------------------------------


def test_censored_ages_past_89_are_written_as_the_top_category(tmp_path: pathlib.Path) -> None:
    """Spike `>95` (a fifth of the rows, the column's highest value) and atom `>90` (600 rows inside its range)."""
    r = random.Random(11)
    rows: "list[tuple[str, ...]]" = []
    for _ in range(ROWS):
        u = r.random()
        if u < 0.20:
            age, score = ">95", f"{r.gauss(60, 8):.1f}"
        elif u < 0.23:
            age, score = ">90", f"{r.gauss(58, 8):.1f}"
        else:
            value = 40 + r.random() * 49.99
            age, score = f"{value:.2f}", f"{r.gauss(20 + value * 0.5, 5):.1f}"
        rows += [(age, r.choice(("north", "south", "east")), score)]
    twins, document, record = _route(tmp_path, "ages", _table(("age", "ward", "score"), rows))
    block = [column for column in document["columns"] if column["name"] == "age"][0]  # type: ignore[index,union-attr]
    assert block["top_coded"] == 90  # type: ignore[index]
    drawn = [entry["name"] for entry in record["zones"]["relations"]["columns"]]  # type: ignore[index]
    assert "age" in drawn
    cells = _column(twins[0], "age")
    censored = [cell for cell in cells if cell[:1] in "<>"]
    assert sorted(set(censored)) == [">89"], sorted(set(censored))[:6]
    assert 0.20 <= len(censored) / len(cells) <= 0.26
    for cell in cells:
        if cell and cell[:1] not in "<>":
            assert float(cell) <= 90.0, cell


# -- item 10: the reading the description gave -----------------------------------------------------------


def test_the_dates_zone_reads_day_first_dates_as_the_description_does(tmp_path: pathlib.Path) -> None:
    """Day-first dates, nearly all on days 1 to 12 so month first reads 97 per cent of them, read with --day-first."""
    r = random.Random(10)
    rows: "list[tuple[str, ...]]" = []
    for _ in range(ROWS):
        late = r.random() < 0.03
        day = datetime.date(2024, 1 + r.randrange(12), (13 + r.randrange(15)) if late else (1 + r.randrange(12)))
        rows += [(day.strftime("%d/%m/%Y"), r.choice(("p", "q", "r")))]
    twins, document, record = _route(tmp_path, "dayfirst", _table(("seen_on", "unit"), rows), ("--day-first",),
                                     {"seen_on": "no"})
    block = [column for column in document["columns"] if column["name"] == "seen_on"][0]  # type: ignore[index,union-attr]
    assert block["format"] == "day-first-date"  # type: ignore[index]
    cells = _column(twins[0], "seen_on")
    written = [cell for cell in cells if cell]
    bad = 0
    for cell in written:
        try:
            datetime.datetime.strptime(cell, "%d/%m/%Y")
        except ValueError:
            bad += 1
    assert bad == 0, f"{bad} twin cells are not day, month, year"
    assert len(written) >= 0.99 * len(cells)
    zone = _dates_zone(record)
    assert zone["columns"]["seen_on"]["reading"] == {"kind": "text", "member": "day-first-date"}  # type: ignore[index]


def test_a_declared_count_of_days_is_carried_by_the_dates_zone(tmp_path: pathlib.Path) -> None:
    """Days since 1970 of a clinic open on Tuesdays and Thursdays, declared with --date-count."""
    r = random.Random(14)
    rows: "list[tuple[str, ...]]" = []
    start = datetime.date(2022, 1, 1)
    for _ in range(ROWS):
        day = start + datetime.timedelta(days=r.randrange(730))
        while day.weekday() not in (1, 3):
            day = day + datetime.timedelta(days=1)
        rows += [(f"{(day - datetime.date(1970, 1, 1)).days}", r.choice(("p", "q")))]
    twins, _document, record = _route(tmp_path, "counted", _table(("clinic_day", "unit"), rows),
                                      ("--date-count", "clinic_day", "days-since-1970"), {"clinic_day": "no"})
    zone = _dates_zone(record)
    assert "clinic_day" in zone.get("order", []), "the declared column is not in the dates zone"  # type: ignore[operator]
    assert zone["columns"]["clinic_day"]["reading"] == {"kind": "count",  # type: ignore[index]
                                                        "member": "days-since-1970"}
    cells = [cell for cell in _column(twins[0], "clinic_day") if cell]
    assert len(cells) == ROWS
    weekdays = {(datetime.date(1970, 1, 1) + datetime.timedelta(days=int(cell))).weekday() for cell in cells}
    assert weekdays <= {1, 3}, weekdays


def test_the_dates_zone_reads_no_column_the_description_reads_otherwise(tmp_path: pathlib.Path) -> None:
    """A value column typed by a key, nearly all of its values dates: the description reads it otherwise (its dates
    held under the open question, its numbers continuous), so the zone holds no census of it."""
    r = random.Random(22)
    rows: "list[tuple[str, ...]]" = []
    for _ in range(ROWS):
        if r.random() < 0.96:
            rows += [("seen on", (datetime.date(2023, 1, 1) + datetime.timedelta(days=r.randrange(700))).isoformat())]
        else:
            rows += [("weight", f"{r.gauss(72, 9):.1f}")]
    twins, document, record = _route(tmp_path, "keyed", _table(("item", "value"), rows))
    block = [column for column in document["columns"] if column["name"] == "value"][0]  # type: ignore[index,union-attr]
    assert "format" not in block  # type: ignore[operator]
    zone = _dates_zone(record)
    assert "value" not in (zone["order"] if "order" in zone else []), "the zone read a column the description does not"  # type: ignore[operator]
    cells = _column(twins[0], "value")
    assert not [cell for cell in cells if cell[4:5] == "-"]


# -- item 11: an exponent's scale ----------------------------------------------------------------------------


def test_an_assay_written_with_an_exponent_keeps_its_scale_and_its_spelling(tmp_path: pathlib.Path) -> None:
    """1,000 values from 1.000e-6 to 1.999e-6: the twin's are of that scale, written as the source writes them."""
    r = random.Random(5)
    rows: "list[tuple[str, ...]]" = []
    for _ in range(ROWS):
        level = 1000 + r.randrange(1000)
        rows += [(f"{level // 1000}.{level % 1000:03d}e-6", r.choice(("a", "b")),
                  f"{r.gauss(10 + (level - 1500) / 100, 2):.1f}")]
    twins, _document, record = _route(tmp_path, "assays", _table(("assay", "group", "dose"), rows))
    drawn = [entry["name"] for entry in record["zones"]["relations"]["columns"]]  # type: ignore[index]
    assert "assay" in drawn
    cells = _column(twins[0], "assay")
    assert all(re.fullmatch(r"[12]\.\d{3}e-6", cell) for cell in cells), sorted(set(cells))[:5]
    values = [float(cell) for cell in cells]
    assert min(values) >= 1e-6 and max(values) < 2e-6
    assert len(set(cells)) >= 300


# -- item 12: each date column's own weekdays --------------------------------------------------------------


def test_two_date_columns_keep_their_own_weekdays(tmp_path: pathlib.Path) -> None:
    """Every Monday and every Friday of January 2024, two columns independent of each other."""
    r = random.Random(12)
    mondays = [datetime.date(2024, 1, d).isoformat() for d in (1, 8, 15, 22, 29)]
    fridays = [datetime.date(2024, 1, d).isoformat() for d in (5, 12, 19, 26)]
    rows = [(r.choice(mondays), r.choice(fridays), r.choice(("x", "y"))) for _ in range(ROWS)]
    twins, _document, record = _route(tmp_path, "weekdays", _table(("seen_monday", "seen_friday", "kind"), rows),
                                      seeds=(0, 1))
    zone = _dates_zone(record)
    assert zone["order"] == ["seen_monday", "seen_friday"]
    for seed in (0, 1):
        friday = [datetime.date.fromisoformat(cell).weekday() for cell in _column(twins[seed], "seen_friday") if cell]
        monday = [datetime.date.fromisoformat(cell).weekday() for cell in _column(twins[seed], "seen_monday") if cell]
        assert len(friday) == ROWS and set(friday) == {4}, sorted(set(friday))
        assert len(monday) == ROWS and set(monday) == {0}, sorted(set(monday))


# -- item 13: offsets and fractions of a second ---------------------------------------------------------------


def _instants(cells: "list[str]") -> "list[datetime.datetime | None]":
    out: "list[datetime.datetime | None]" = []
    for cell in cells:
        if not cell:
            out += [None]
            continue
        moment = datetime.datetime.fromisoformat(cell)
        out += [moment if moment.tzinfo is not None else moment.replace(tzinfo=datetime.timezone.utc)]
    return out


def test_an_interval_between_stamps_written_with_offsets_stays_as_written(tmp_path: pathlib.Path) -> None:
    """Starts written `+02:00` or `Z` (one instant either way), each end 30 minutes later in `Z`."""
    r = random.Random(13)
    rows: "list[tuple[str, ...]]" = []
    for k in range(ROWS):
        day = datetime.datetime(2024, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(days=k % 366)
        start = day + datetime.timedelta(minutes=6 * 60 + r.randrange(12 * 60))
        end = start + datetime.timedelta(minutes=30)
        if k % 2:
            written = (start + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M") + "+02:00"
        else:
            written = start.strftime("%Y-%m-%dT%H:%M") + "Z"
        rows += [(written, end.strftime("%Y-%m-%dT%H:%M") + "Z")]
    twins, _document, record = _route(tmp_path, "offsets", _table(("began", "ended"), rows), seeds=(0, 1))
    assert _dates_zone(record)["order"] == ["began", "ended"]
    for seed in (0, 1):
        began = _column(twins[seed], "began")
        intervals = [(b - a).total_seconds() for a, b in zip(_instants(began), _instants(_column(twins[seed], "ended")))
                     if a is not None and b is not None]
        assert len(intervals) == ROWS
        assert {interval for interval in intervals} == {1800.0}, sorted(set(intervals))[:5]
        assert {cell[16:] for cell in began} == {"+02:00", "Z"}


def test_an_interval_of_a_tenth_of_a_second_stays_a_tenth(tmp_path: pathlib.Path) -> None:
    """A message sent at `.100` and received at `.200` of the same second."""
    r = random.Random(13)
    rows: "list[tuple[str, ...]]" = []
    for k in range(ROWS):
        moment = datetime.datetime(2024, 1, 1) + datetime.timedelta(days=k % 366, minutes=6 * 60 + r.randrange(600),
                                                                    seconds=r.randrange(60))
        rows += [(moment.strftime("%Y-%m-%d %H:%M:%S") + ".100", moment.strftime("%Y-%m-%d %H:%M:%S") + ".200")]
    twins, _document, record = _route(tmp_path, "fractions", _table(("sent", "received"), rows), seeds=(0, 1))
    assert _dates_zone(record)["order"] == ["sent", "received"]
    for seed in (0, 1):
        sent = _column(twins[seed], "sent")
        intervals = [round((b - a).total_seconds(), 6) for a, b in zip(_instants(sent),
                                                                        _instants(_column(twins[seed], "received")))
                     if a is not None and b is not None]
        assert len(intervals) == ROWS
        assert set(intervals) == {0.1}, sorted(set(intervals))[:5]
        assert all(re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}", cell) for cell in sent)


# -- item 19: the offline audit over the generate step ------------------------------------------------------------


def _scanner() -> object:
    spec = importlib.util.spec_from_file_location("scan_imports", REPO_ROOT / "tools" / "offline_scan" / "scan_imports.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_offline_audit_passes_the_inside_generate_step() -> None:
    """No violation of the audit inside `generation.generate_inside` or the helpers written beside it."""
    path = REPO_ROOT / "src" / "synthtwin" / "generation.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    spans: "list[tuple[int, int]]" = []
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and (node.name == "generate_inside" or node.name[:7] == "_inside"
                                                  or node.name == "_names_under_by"):
            spans += [(node.lineno, node.end_lineno or node.lineno)]
    assert spans
    violations = _scanner().scan_tree(REPO_ROOT / "src" / "synthtwin")  # type: ignore[attr-defined]
    mine = []
    for line in violations:
        found = re.match(r"(.*generation\.py):(\d+): ", line)
        if found and any(first <= int(found.group(2)) <= last for first, last in spans):
            mine += [line]
    assert mine == [], "\n".join(mine)


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield

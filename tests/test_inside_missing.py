"""Gate file of lane IN-7 (plan P4-D501): the inside record's missing-values zone, and the logistic fit it stands on.

THE PATH. `synthtwin profile` writes, beside the relations zone, a zone
carrying each KEPT column's emptiness (a date, free text, a record
number other than the person's): one logistic response fitted inside on
every modelled column and on the kept columns before it
(`inside_missing.fit_zone`); `synthtwin generate` draws each such
column's latent emptiness (`inside_missing.draw`), hands a date column
the rows that hold a date, and moves any other carried column's own
cells onto the rows its model leaves filled (`inside_missing.dealt`).

WHAT IT HOLDS, each clause red on its mutant (lane IN-7's report):

* Through the commands at the table floor (20,000 rows, an invented
  table, the person's answers in the questions file): the record carries
  the zone; the twin's end day is empty where the status says the stay
  goes on and filled where it says the person went home, as in the real table
  (the description's twin alone spreads its empty cells evenly); a free
  remark is written where the yes/no column says yes, at the real
  shares; IN-1's five checks pass, no identifier equals a real one and
  no age passes 90.
* A kept column's emptiness follows a modelled label, columns empty
  together come out empty together, and an emptiness held once a person
  is drawn once a person.
* `dealt` keeps every cell of the column and puts the filled ones on
  the rows least likely empty.
* The zone is a model: no row, and its size holds as the rows double.
* A logistic fit near separation (a level no row of a parent's level
  holds) settles where the table's shares are, with coefficients of
  ordinary size (the step halved while it raises the deviance).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import math
import pathlib
import random

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, inside_missing, inside_relations, installation, twin_checks

FLOOR_ROWS = 20000
# The person column's name, as the battery names it.
PERSON = T.PERSON["T2"]
COLUMNS = [PERSON, "age", "gender", "body_weight", "complication", "status", "start_day", "end_day", "remark"]
WORDS = ("seen", "reviewed", "plan", "called", "booked", "ward", "team", "clinic", "letter", "result", "follow",
         "up", "advised", "rest", "fluids", "walking", "brace", "dressing", "changed", "stable", "home", "family",
         "informed", "pain", "settled", "review", "week", "month", "nurse", "visit")
ANSWERS = {PERSON: "identifier", "age": "yes", "body_weight": "measurement", "remark": "keep"}


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _table_text(rows: int, seed: int) -> str:
    """An invented table: an end day empty while the stay goes on, a free remark written mostly where a complication is."""
    r = random.Random(f"in7-gate-{seed}")
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(COLUMNS)
    start = datetime.date(2021, 1, 4)
    for i in range(rows):
        age = min(99, max(18, int(r.gauss(60, 16))))
        female = r.random() < 0.5
        weight = max(40.0, r.gauss(80.0 - 6.0 * female + 0.05 * (age - 60), 12.0))
        complication = r.random() < _logistic(-1.8 + 0.03 * (age - 60))
        admitted = r.random() < _logistic(-2.2 + 1.4 * complication)
        admit = start + datetime.timedelta(days=r.randrange(900))
        stay = 1 + int(r.expovariate(1.0 / (3.0 + 4.0 * complication)))
        remark = ""
        if r.random() < (0.7 if complication else 0.08):
            remark = " ".join(r.choice(WORDS) for _k in range(r.randrange(5, 9)))
        writer.writerow([f"P{2000000 + i}", str(age), "F" if female else "M", f"{weight:.1f} kg",
                         "Y" if complication else "N", "staying" if admitted else "home", admit.isoformat(),
                         "" if admitted else (admit + datetime.timedelta(days=stay)).isoformat(), remark])
    return out.getvalue()


def _places(folder: pathlib.Path) -> inside.Places:
    """The run's own installation's private folder, as `reliability_battery.installed` makes it."""
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _run(argv: "list[str]") -> "tuple[int, str]":
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv, small_tables_refused=True)
    return int(code), said.getvalue()


def _answer(questions: pathlib.Path) -> "list[str]":
    """The person's answers: the person key an identifier, the age a Safe Harbor yes, the rest as they are."""
    if not questions.exists():
        return []
    document = json.loads(questions.read_text(encoding="utf-8"))
    written: "list[str]" = []
    for entry in B._entries(document):
        if entry.get("your_answer"):
            continue
        column = str(entry.get("column", ""))
        offered = B._offered(entry)
        pick = ANSWERS.get(column, "")
        if pick not in offered:
            pick = "keep" if "keep" in offered else ("no" if "no" in offered else "")
        if pick:
            entry["your_answer"] = pick
            written += [f"{column}={pick}"]
    between = document.get("between_columns") if isinstance(document, dict) else None
    question = between.get("rows_per_person") if isinstance(between, dict) else None
    if isinstance(question, dict) and not question.get("your_answer"):
        question["your_answer"] = "one row each"
        written += ["the subject question"]
    if written:
        questions.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
    return written


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, str, str, dict[str, object]]":
    folder = tmp_path_factory.mktemp("inside-missing") / "product"
    source = pathlib.Path(folder, "table", "stays.csv")
    out = pathlib.Path(folder, "out")
    source.parent.mkdir(parents=True)
    out.mkdir(parents=True)
    text = _table_text(FLOOR_ROWS, 1)
    source.write_text(text, encoding="utf-8", newline="\n")
    questions = pathlib.Path(out, "stays-questions.json")
    with pytest.MonkeyPatch.context() as patch, B.installed(folder):
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = _run(["profile", f"{source}", "--out-dir", f"{out}", "--replace"])
        for _round in range(4):
            assert code == 0, said[-600:]
            if not _answer(questions):
                break
            code, said = _run(["profile", f"{source}", "--out-dir", f"{out}", "--answers", f"{questions}"])
            if code != 0:
                code, said = _run(["profile", f"{source}", "--out-dir", f"{out}", "--answers", f"{questions}",
                                   "--replace-description"])
        assert code == 0, said[-600:]
        code, said = _run(["generate", f"{pathlib.Path(out, 'stays-profile.json')}", "--out-dir", f"{out}",
                           "--seed", "0", "--replace"])
        assert code == 0, said[-600:]
    records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    twin = pathlib.Path(out, "stays-twin.csv").read_text(encoding="utf-8")
    return folder, text, twin, inside.load_record(records[0])


def _columns(text: str) -> "dict[str, list[str]]":
    reader = csv.reader(io.StringIO(text))
    header = next(reader)
    found: "dict[str, list[str]]" = {name: [] for name in header}
    for row in reader:
        for place, name in enumerate(header):
            found[name] += [row[place] if place < len(row) else ""]
    return found


def _empty_share(cells: "list[str]", keys: "list[str]", key: str) -> float:
    picked = [cell for cell, held in zip(cells, keys) if held == key]
    return sum(1 for cell in picked if not cell.strip()) / max(1, len(picked))


def test_the_record_carries_the_zone_and_the_twin_s_dates_are_empty_where_the_model_puts_them(made) -> None:  # type: ignore[no-untyped-def]
    _folder, text, twin, record = made
    zone = inside_missing.zone_of(record)
    assert zone is not None
    assert set(inside_missing.carried(zone)) >= {"end_day", "remark"}, inside_missing.carried(zone)
    real, drawn = _columns(text), _columns(twin)
    assert _empty_share(real["end_day"], real["status"], "staying") == 1.0
    assert _empty_share(real["end_day"], real["status"], "home") == 0.0
    assert _empty_share(drawn["end_day"], drawn["status"], "staying") >= 0.95
    assert _empty_share(drawn["end_day"], drawn["status"], "home") <= 0.05


def test_a_free_remark_is_written_where_the_yes_no_column_says_yes(made) -> None:  # type: ignore[no-untyped-def]
    _folder, text, twin, _record = made
    real, drawn = _columns(text), _columns(twin)
    for key in ("Y", "N"):
        assert abs(_empty_share(drawn["remark"], drawn["complication"], key)
                   - _empty_share(real["remark"], real["complication"], key)) <= 0.06, key


def test_a_weight_written_with_its_unit_is_drawn_from_the_record_with_its_relation(made) -> None:  # type: ignore[no-untyped-def]
    _folder, text, twin, record = made
    assert "body_weight" in inside_relations.modelled_names(inside_relations.zone_of(record))
    real, drawn = _columns(text), _columns(twin)
    assert all(cell[-3:] == " kg" for cell in drawn["body_weight"] if cell.strip())

    def gap(columns: "dict[str, list[str]]") -> float:
        female = [float(cell[:-3]) for cell, g in zip(columns["body_weight"], columns["gender"]) if g == "F" and cell]
        male = [float(cell[:-3]) for cell, g in zip(columns["body_weight"], columns["gender"]) if g == "M" and cell]
        return sum(male) / len(male) - sum(female) / len(female)

    assert abs(gap(drawn) - gap(real)) <= 1.0, (gap(drawn), gap(real))


def _another_twin(folder: pathlib.Path, seed: int) -> str:
    """The twin of the fixture's description at another seed, through the command."""
    out = pathlib.Path(folder, "out")
    with pytest.MonkeyPatch.context() as patch, B.installed(folder):
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = _run(["generate", f"{pathlib.Path(out, 'stays-profile.json')}", "--out-dir", f"{out}", "--seed",
                           f"{seed}", "--replace"])
    assert code == 0, said[-600:]
    return pathlib.Path(out, "stays-twin.csv").read_text(encoding="utf-8")


def test_the_released_twin_passes_the_five_checks_and_no_draw_shows_an_identifier_a_date_or_an_age_past_ninety(made, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    """The plan's release rule: a twin a check fails is drawn again, at most three times (plan-inside section 2).

    Every draw keeps the copy, identifier, date and age clauses (C1, C3,
    C4: never a real record number, a copied row or patient, a real rare
    date beyond chance, an age past 90); the released draw passes all five.
    """
    folder, text, twin, _record = made
    real_path, twin_path = pathlib.Path(tmp_path, "stays.csv"), pathlib.Path(tmp_path, "stays-twin.csv")
    real_path.write_text(text, encoding="utf-8", newline="\n")
    real = _columns(text)
    released = False
    for attempt in range(4):
        drawn_text = twin if attempt == 0 else _another_twin(folder, attempt)
        twin_path.write_text(drawn_text, encoding="utf-8", newline="\n")
        outcome = twin_checks.run_checks(f"{real_path}", f"{twin_path}", small_tables_refused=True)
        kept = [check for check in outcome.checks if check.code in ("C1", "C3", "C4") and not check.passed]
        assert not kept, [(check.code, check.lines) for check in kept]
        drawn = _columns(drawn_text)
        assert not set(real[PERSON]) & set(drawn[PERSON])
        assert max(int(cell) for cell in drawn["age"] if cell.strip()) <= 90
        if outcome.passed:
            released = True
            break
    assert released


# -- the zone's fit and draw on frames (no command) ---------------------------------------------------


def _frames(codes: "list[int]") -> "dict[str, inside_relations.Frame]":
    return {"group": inside_relations.Frame(inside_relations.LABEL, [], [], codes)}


def _kept(name: str, place: int, flags: "list[int]", persons: "inside_relations.Persons | None" = None) -> inside_missing.Kept:
    spec = inside_relations.ColumnSpec(name, place, "", 0, (), "its kind (datetime) is drawn by the description")
    cells = ["" if flag else "2024-01-01" for flag in flags]
    found = inside_missing.kept_column(spec, {"name": name, "role": "datetime"}, cells,
                                       [row for row in range(len(flags))], persons)
    assert found is not None
    return found


def _invented(rows: int, seed: int) -> "tuple[list[int], list[int], list[int]]":
    r = random.Random(f"in7-frames-{seed}")
    group = [1 if r.random() < 0.3 else 0 for _row in range(rows)]
    first = [1 if r.random() < (0.85 if g else 0.10) else 0 for g in group]
    second = [1 if r.random() < (0.9 if f else 0.05) else 0 for f in first]
    return group, first, second


def test_a_kept_column_s_emptiness_follows_a_modelled_label_and_columns_empty_together_stay_together() -> None:
    rows = 4000
    group, first, second = _invented(rows, 1)
    frames = _frames(group)
    zone = inside_missing.fit_zone([_kept("first", 1, first), _kept("second", 2, second)], frames, set(), rows, rows)
    twin_group, _a, _b = _invented(rows, 2)
    latent = inside_missing.draw(zone, _frames(twin_group), rows, 7)
    one = [0 if keep else 1 for keep in inside_missing.present_rows(latent["first"])]
    two = [0 if keep else 1 for keep in inside_missing.present_rows(latent["second"])]
    for key in (0, 1):
        real = sum(f for f, g in zip(first, group) if g == key) / max(1, group.count(key))
        made_share = sum(f for f, g in zip(one, twin_group) if g == key) / max(1, twin_group.count(key))
        assert abs(made_share - real) <= 0.04, (key, made_share, real)
    real_both = sum(a * b for a, b in zip(first, second)) / rows
    made_both = sum(a * b for a, b in zip(one, two)) / rows
    assert abs(made_both - real_both) <= 0.03, (made_both, real_both)


def test_an_emptiness_held_once_a_person_is_drawn_once_a_person() -> None:
    r = random.Random("in7-persons")
    keys: "list[str]" = []
    flags: "list[int]" = []
    for person in range(800):
        empty = 1 if r.random() < 0.4 else 0
        for _visit in range(r.randrange(2, 6)):
            keys += [f"K{person}"]
            flags += [empty]
    persons = inside_relations.persons_of(keys)
    kept = _kept("visit_day", 1, flags, persons)
    assert kept.level == inside_missing.PATIENT
    owners = [persons.person[row] for row in range(len(keys))]
    zone = inside_missing.fit_zone([kept], {}, set(), len(keys), len(keys), owners)
    latent = inside_missing.draw(zone, {}, len(keys), 3, persons)
    of_person: "dict[int, set[bool]]" = {}
    for row, value in enumerate(latent["visit_day"]):
        of_person.setdefault(persons.person[row], set()).add(value > 0.0)
    assert all(len(held) == 1 for held in of_person.values())
    share = sum(1 for held in of_person.values() if True in held) / len(of_person)
    assert abs(share - 0.4) <= 0.06, share


def test_dealt_keeps_every_cell_and_puts_the_filled_ones_on_the_rows_least_likely_empty() -> None:
    cells = ["a", "", "b", "NA", "c", "", "d", ""]
    latent = [5.0, -3.0, 4.0, -2.0, 3.0, -1.0, 2.0, 1.0]
    moved = inside_missing.dealt(cells, latent)
    assert sorted(moved) == sorted(cells)
    assert [cell for cell in moved if not inside_missing.is_empty(cell)] == ["a", "b", "c", "d"]
    filled_rows = [row for row, cell in enumerate(moved) if not inside_missing.is_empty(cell)]
    assert filled_rows == [1, 3, 5, 7]


def test_the_zone_is_a_model_whose_size_holds_as_the_rows_double() -> None:
    sizes: "list[int]" = []
    for rows in (3000, 6000):
        group, first, second = _invented(rows, 4)
        zone = inside_missing.fit_zone([_kept("first", 1, first), _kept("second", 2, second)], _frames(group),
                                       set(), rows, rows)
        sizes += [len(json.dumps(zone, sort_keys=True))]
    assert sizes[1] <= 1.05 * sizes[0] + 120, sizes


def _remarks(rows: int, seed: int) -> "dict[str, list[str]]":
    """A remark of five phrases written mostly where a complication is, beside thirty codes of falling frequency."""
    r = random.Random(f"in7-remarks-{seed}")
    phrases = ("seen by the team", "plan reviewed", "follow up booked", "note added", "call back")
    found: "dict[str, list[str]]" = {"age": [], "code": [], "complication": [], "status": [], "remark": []}
    for _row in range(rows):
        age = min(99, max(18, int(r.gauss(60, 16))))
        code = f"D{min(29, int(r.expovariate(1 / 8.0))):02d}"
        complication = r.random() < _logistic(-2.0 + 0.03 * (age - 60) + 0.8 * (code < "D05"))
        admitted = r.random() < _logistic(-2.2 + 1.2 * complication)
        found["age"] += [str(age)]
        found["code"] += [code]
        found["complication"] += ["Y" if complication else "N"]
        found["status"] += ["staying" if admitted else "home"]
        found["remark"] += [r.choice(phrases) if r.random() < (0.7 if complication else 0.08) else ""]
    return found


def test_a_logistic_fit_near_separation_settles_where_the_table_s_shares_are() -> None:
    rows = 3000
    cells = _remarks(rows, 1)
    sample = inside_relations.sample_rows(rows)
    encoded: "list[inside_relations.Encoded]" = []
    for place, name in enumerate(cells):
        kind = inside_relations.NUMBER if name == "age" else inside_relations.LABEL
        spellings = tuple(sorted(set(cells[name]))) if kind == inside_relations.LABEL else ()
        found = inside_relations.encode(inside_relations.ColumnSpec(name, place, kind, 0, spellings, ""), cells[name],
                                        sample, None)
        assert found is not None
        encoded += [found]
    frames: "dict[str, inside_relations.Frame]" = {}
    zone = inside_relations.fit_zone(encoded, rows, rows, None, "", frames)
    entry = [each for each in zone["columns"] if each["name"] == "remark"][0]  # type: ignore[union-attr, index]
    model = entry["value"]
    biggest = max(abs(value) for row in model["coefficients"] if row for value in row)
    assert biggest < 60.0, biggest
    count = len(entry["levels"]) + (1 if entry["rest"] else 0)
    columns = [inside_relations.term_values(term, frames, rows) for term in model["terms"]]
    empty = entry["levels"].index("")
    for key in ("Y", "N"):
        picked = [row for row in range(rows) if cells["complication"][row] == key]
        fitted = 0.0
        for row in picked:
            etas = [0.0] + [math.fsum([model["coefficients"][level][k] * columns[k][row] for k in range(len(columns))])
                            for level in range(1, count)]
            top = max(etas)
            lifted = [math.exp(max(-700.0, eta - top)) for eta in etas]
            fitted += lifted[empty] / math.fsum(lifted)
        observed = sum(1 for row in picked if cells["remark"][row] == "") / len(picked)
        assert abs(fitted / len(picked) - observed) <= 0.02, (key, fitted / len(picked), observed)

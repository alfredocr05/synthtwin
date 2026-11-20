"""Gate file of lane IN-2b: the twin drawn from the inside record keeps the description's written forms.

A column the inside record's relations zone draws is WRITTEN WITH ITS OWN CELLS in the description's twin
(`inside_relations.redeal_number`, `redeal_label`): the draw decides only which row holds which cell, so every
spelling, decimal place, sign, censoring mark, missing-value spelling, label spelling and count over rows that twin
holds stands. A column held once a person keeps one value a person, its counts over rows settled by moving whole
persons. A date column of the dates zone holds a date where that twin holds one, and a date column heading its own
chain holds that twin's months exactly, moved by whole weeks (weekday and clock kept).

THE FORMS TABLE (`forms_text`, invented at run time, 20,000 rows of about 3,000 persons): a number written in plain
and decimal spellings, a yes/no label with several spellings a level, a number with signs, zeros, blanks and a
missing-value word, a share written with and without its leading nought, an assay with censoring marks, an age past
89 for some persons, two date columns written month first, a label with blanks and a missing-value word.

WHAT IT HOLDS (each clause red on its mutant, lane IN-2b's report):

* Every drawn column's cells are its own description twin's cells: the same cells, the same counts (mutant: the
  draw's own writer, `draw_number` and `draw_label`, writes the drawn columns).
* `synthtwin validate` finds no miss in the drawn twin that the description's own twin does not show at the same
  seed (outside the calendar counts of a made-up date column), and the relabel of a drawn twin excuses no check of a
  number or a label (mutant: the counts are not settled, `_settled` moves nothing).
* The drawn twin keeps the relations the record carries, which the description's own twin does not (mutant: the
  numbers are dealt in a hashed order, not by the drawn scores).
* A column held once a person holds one value a person, and its counts over rows stand (mutant: such a column dealt
  row by row).
* A top-coded column writes nothing past its top code (mutant: `_capped` reads no top code).
* The settles move the fewest rows or whole persons and hold every count (mutants: each settle moves nothing).
* A date column heading its own chain holds the description's twin's months exactly, its weekdays as the record
  keeps them (mutant: `_held_months` moves nothing).
* Lane IN-1's five checks pass on the drawn twin; no identifier is a real one; no age passes 90.
"""

from __future__ import annotations

import collections
import contextlib
import csv
import datetime
import io
import math
import pathlib
import random
import typing

import numpy.random
import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, contract, generation, inside, inside_relations as R, installation, twin_checks, validation

TABLE = "forms"
FILE = "forms.csv"
PERSON = B.PATIENT
ROWS = 20000
KNOWS = {PERSON: "identifier", "age": "measurement", "reading": "measurement", "amount": "measurement",
         "share": "measurement", "assay": "measurement"}
DATE_FACTS = frozenset(fact for fact in cli._INSIDE_EXCUSED_DATE_FACTS)


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def forms_text(rows: int, seed: int) -> str:
    """The forms table: a header and one line a row, `\\n` line ends; every value invented from the seed."""
    r = random.Random(f"forms-{seed}")
    lines = [f"{PERSON},arm,age,reading,flag,amount,share,assay,visit_day,booked_on,status"]
    used: "set[str]" = set()
    written = 0
    while written < rows:
        pid = f"Q{r.randrange(1_000_000, 10_000_000)}"
        if pid in used:
            continue
        used.add(pid)
        visits = min(rows - written, 1 + int(r.expovariate(1.0 / 5.7)))
        arm_b = r.random() < 0.45
        age = int(min(99.0, max(18.0, r.gauss(61.0, 14.0))))
        own = r.gauss(0.0, 6.0)
        day = datetime.date(2021, 1, 4) + datetime.timedelta(days=r.randrange(900))
        for visit in range(visits):
            if visit:
                day = day + datetime.timedelta(days=28 + r.randint(-3, 3))
            reading = 120.0 + 6.0 * arm_b + 0.4 * (age - 60) + own + r.gauss(0.0, 9.0)
            reading_text = f"{reading:.1f}" if r.random() < 0.4 else f"{round(reading)}"
            yes = r.random() < _logistic(-2.0 + 0.08 * (reading - 125.0))
            flag = r.choice(("Yes",) * 7 + ("yes",) * 2 + ("Y",)) if yes else r.choice(("No",) * 8 + ("no",) * 2)
            draw = r.random()
            if draw < 0.04:
                amount = ""
            elif draw < 0.07:
                amount = "NA"
            elif r.random() < (0.5 if yes else 0.25):
                amount = "0"
            else:
                value = math.exp(r.gauss(1.0, 0.6)) * (1.5 if yes else 1.0)
                amount = f"+{value:.1f}" if r.random() < 0.2 else (f"{value:.2f}" if r.random() < 0.3 else f"{value:.1f}")
            share_value = min(0.99, max(0.01, 0.3 + 0.006 * (age - 60) + r.gauss(0.0, 0.15)))
            share = f"{share_value:.2f}"
            if r.random() < 0.3:
                share = share[1:]
            pick = r.random()
            if pick < 0.06:
                assay = "<0.5"
            elif pick < 0.08:
                assay = ">50"
            else:
                assay = f"{min(49.9, max(0.5, math.exp(r.gauss(1.5, 0.7)))):.1f}"
            booked = datetime.date(2021, 1, 4) + datetime.timedelta(days=r.randrange(1000))
            status_draw = r.random()
            status = ("" if status_draw < 0.10 else "unknown" if status_draw < 0.14
                      else ("open" if r.random() < (0.6 if yes else 0.3) else r.choice(("closed", "pending"))))
            lines += [f"{pid},{'B' if arm_b else 'A'},{age},{reading_text},{flag},{amount},{share},{assay},"
                      f"{day.strftime('%m/%d/%Y')},{booked.strftime('%m/%d/%Y')},{status}"]
            written += 1
    return "\n".join(lines) + "\n"


@contextlib.contextmanager
def forms_known() -> "typing.Iterator[None]":
    """The battery's truthful answers (`reliability_battery.truthful`) for the forms table, for the run's span."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setitem(T.KNOWS, TABLE, KNOWS)
        patch.setitem(T.AGES, TABLE, ("age",))
        patch.setitem(T.PERSON, TABLE, PERSON)
        patch.setitem(T.FILES, TABLE, FILE)
        yield


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def make_twin(folder: pathlib.Path, text: str, twins: "tuple[int, ...]") -> B.Product:
    """Route S on the forms table with the inside record switched on: profile, the truthful answers, generate."""
    with forms_known(), pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: _places(folder))
        return B.make_twins(folder, TABLE, text, twins, False)


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    return {name: [row[at] for row in rows[1:]] for at, name in enumerate(rows[0])}


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, typing.Any]":
    folder = tmp_path_factory.mktemp("inside-forms") / "product"
    text = forms_text(ROWS, 1)
    product = make_twin(folder, text, (0,))
    assert not product.errors, product.errors
    description = folder / "out" / "forms-profile.json"
    records = sorted((folder / "installation" / "synthtwin" / "inside").glob("*"))
    assert records, "no inside record was written"
    record = inside.load_record(records[0])
    profile = contract.load_profile(f"{description}")
    seeds = [int(word) for word in numpy.random.default_rng(0).integers(0, 18446744073709551615, size=2,
                                                                         dtype="uint64", endpoint=True)]
    strict = generation.generate_held(profile, seeds[0])
    return {"folder": folder, "text": text, "twin": product.twins[0], "description": description, "record": record,
            "profile": profile, "strict": strict}


def _strict_cells(made: "dict[str, typing.Any]", name: str) -> "list[str]":
    from synthtwin import twinstore

    names = [column.name for column in made["profile"].columns]
    return twinstore.column_cells(made["strict"].held_columns[names.index(name)])


def _zone_entries(made: "dict[str, typing.Any]") -> "dict[str, dict[str, object]]":
    zone = R.zone_of(made["record"])
    return {str(entry["name"]): entry for entry in zone["columns"]}  # type: ignore[union-attr]


def test_every_drawn_column_is_dealt_inside_its_own_twins_cells(made) -> None:  # type: ignore[no-untyped-def]
    twin = _columns(made["twin"])
    entries = _zone_entries(made)
    assert {"reading", "flag", "amount", "share", "assay", "status"} <= set(entries)
    for name, entry in entries.items():
        if entry.get("level") == R.SEQUENCE:
            continue
        strict = _strict_cells(made, name)
        if entry.get("level") == R.PATIENT and entry["kind"] == R.NUMBER:
            continue
        assert collections.Counter(twin[name]) == collections.Counter(strict), name


def _validated(made: "dict[str, typing.Any]", measured: "pathlib.Path | None") -> "tuple[int, list[tuple[str, str]], list[tuple[str, str]]]":
    """`synthtwin validate` of the drawn twin (or of the file `measured`): its exit code, the MISSED checks before the
    relabel of a drawn twin, and the checks that relabel moved."""
    folder, description = made["folder"], made["description"]
    seen: "dict[str, list[tuple[str, str]]]" = {"missed": [], "moved": []}
    original = cli._outcome_of_a_drawn_twin

    def watched(described, checked, outcome):  # type: ignore[no-untyped-def]
        after = original(described, checked, outcome)
        seen["moved"] = [(a.column, a.fact) for a, b in zip(after.checks, outcome.checks) if a.verdict != b.verdict]
        seen["missed"] = [(b.column, b.fact) for b in outcome.checks if b.verdict == validation.MISSED]
        return after

    named = ["--twin", f"{measured}", "--out-dir", f"{measured.parent}"] if measured is not None else []
    with forms_known(), pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: _places(folder))
        patch.setattr(cli, "_outcome_of_a_drawn_twin", watched)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = int(cli.main(["validate", f"{description}", "--replace"] + named, small_tables_refused=False))
    return code, seen["missed"], seen["moved"]


def test_validate_adds_no_miss_and_excuses_no_number_or_label_check(made) -> None:  # type: ignore[no-untyped-def]
    from synthtwin import rendering

    strict_twin = made["folder"] / "strict" / "forms-twin.csv"
    strict_twin.parent.mkdir(exist_ok=True)
    strict_twin.write_text("".join(rendering.twin_csv_pieces(made["strict"])), encoding="utf-8", newline="")
    _code, own, _none = _validated(made, strict_twin)
    code, missed, moved = _validated(made, None)
    added = [each for each in missed if each[1] not in DATE_FACTS and each not in own]
    assert added == [], added
    assert [each for each in moved if each[1] not in DATE_FACTS] == []
    assert code == (0 if not [each for each in own if each[1] not in DATE_FACTS] else 3)


def _correlation(xs: "list[float]", ys: "list[float]") -> float:
    mean_x, mean_y = sum(xs) / len(xs), sum(ys) / len(ys)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    sxx = sum((x - mean_x) ** 2 for x in xs)
    syy = sum((y - mean_y) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy)


def _pairs(columns: "dict[str, list[str]]", first: str, second: str) -> "tuple[list[float], list[float]]":
    xs: "list[float]" = []
    ys: "list[float]" = []
    for a, b in zip(columns[first], columns[second]):
        try:
            x, y = float(a), float(b)
        except ValueError:
            continue
        xs += [x]
        ys += [y]
    return xs, ys


def test_the_drawn_twin_keeps_the_relations_the_record_carries(made) -> None:  # type: ignore[no-untyped-def]
    real, twin = _columns(made["text"]), _columns(made["twin"])
    real_r = _correlation(*_pairs(real, "age", "reading"))
    twin_r = _correlation(*_pairs(twin, "age", "reading"))
    assert real_r > 0.3 and abs(twin_r - real_r) < 0.08, (real_r, twin_r)
    yes = {"Yes", "yes", "Y"}
    for columns in (real, twin):
        high = [flag in yes for flag, value in zip(columns["flag"], columns["reading"]) if float(value) > 135.0]
        low = [flag in yes for flag, value in zip(columns["flag"], columns["reading"]) if float(value) < 115.0]
        assert sum(high) / len(high) > 2.0 * sum(low) / len(low)


def test_a_column_held_once_a_person_holds_one_value_a_person(made) -> None:  # type: ignore[no-untyped-def]
    twin = _columns(made["twin"])
    entries = _zone_entries(made)
    assert entries["arm"]["level"] == R.PATIENT and entries["age"]["level"] == R.PATIENT
    for name in ("arm", "age"):
        held: "dict[str, set[str]]" = {}
        for person, cell in zip(twin[PERSON], twin[name]):
            held.setdefault(person, set()).add(cell)
        assert all(len(cells) == 1 for cells in held.values()), name
    assert collections.Counter(twin["arm"]) == collections.Counter(_strict_cells(made, "arm"))


def test_the_five_checks_pass_and_no_age_passes_ninety(made, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    real = made["folder"] / "table" / FILE
    twin = tmp_path / "forms-twin.csv"
    twin.write_text(made["twin"], encoding="utf-8", newline="")
    outcome = twin_checks.run_checks(f"{real}", f"{twin}", person=PERSON, small_tables_refused=False)
    assert outcome.passed, twin_checks.report_lines(outcome)
    columns = _columns(made["twin"])
    assert max(float(cell) for cell in columns["age"] if cell) <= 90.0
    assert not set(columns[PERSON]) & set(_columns(made["text"])[PERSON])


def _months(cells: "list[str]") -> "collections.Counter[str]":
    return collections.Counter(f"{cell[6:10]}-{cell[0:2]}" for cell in cells if cell)


def test_a_date_column_heading_its_chain_holds_its_months_and_weekdays(made) -> None:  # type: ignore[no-untyped-def]
    real, twin = _columns(made["text"]), _columns(made["twin"])
    strict = _strict_cells(made, "booked_on")
    assert _months(twin["booked_on"]) == _months(strict)
    assert [cell == "" for cell in twin["visit_day"]].count(True) == [cell == "" for cell in
                                                                        _strict_cells(made, "visit_day")].count(True)

    def weekdays(cells: "list[str]") -> "list[float]":
        counts = collections.Counter(datetime.datetime.strptime(cell, "%m/%d/%Y").weekday() for cell in cells if cell)
        total = sum(counts.values())
        return [counts[day] / total for day in range(7)]

    assert max(abs(a - b) for a, b in zip(weekdays(real["booked_on"]), weekdays(twin["booked_on"]))) < 0.02


def _entry(top: int = 0) -> "dict[str, object]":
    return {"name": "x", "place": 0, "kind": R.NUMBER, "level": R.ROW, "grid": [float(k) for k in range(R.GRID)],
            "decimals": 0, "atoms": [], "spikes": [None, None], "top": top, "states": [900, 100, 0, 0, 0],
            "presence": None,
            "value": {"terms": [["one"]], "coefficients": [0.0], "spread": 1.0,
                      "residuals": [float(k - 20) / 10.0 for k in range(R.RESIDUAL_POINTS)]}}


def _words(count: int, seed: int) -> "list[int]":
    r = random.Random(f"forms-words-{seed}")
    return [r.getrandbits(64) for _ in range(count)]


def test_a_top_coded_column_writes_nothing_past_its_top_code() -> None:
    strict = [f"{40 + (k % 60)}" for k in range(900)] + [""] * 95 + ["95", "97", ">97", ">=95", "90"]
    drawn = R.redeal_number(_entry(90), {}, _words(2000, 1), strict, R.Dealing(1000))
    values = [float(cell) for cell in drawn.cells if cell and cell[0] not in "<>"]
    assert max(values) <= 90.0
    assert set(cell for cell in drawn.cells if cell and cell[0] in "<>") == {">89"}


def test_the_settles_move_the_fewest_and_hold_every_count() -> None:
    codes = [0] * 60 + [1] * 30 + [2] * 10
    moved = R._settled(codes, list(range(100)), [50, 35, 15], None, R._constant_shares([50, 35, 15]), 7)
    assert moved == 10
    assert [codes.count(kind) for kind in range(3)] == [50, 35, 15]
    rows_of = [[3 * k, 3 * k + 1] if k % 2 else [3 * k] for k in range(40)]
    persons = list(range(40))
    marks = [0 for _row in range(120)]
    for person in persons:
        marks[rows_of[person][0]] = 0 if person < 30 else 1
    targets = [0, 0]
    for person in persons:
        targets[0 if person < 20 else 1] += len(rows_of[person])
    R._person_settled(marks, rows_of, persons, targets, 11)
    held = [0, 0]
    for person in persons:
        held[marks[rows_of[person][0]]] += len(rows_of[person])
    assert held == targets


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield

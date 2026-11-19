"""Gate file of Codex's review of batch 4w, items 2, 14, 15 and 16: the trajectories zone of the inside record.

Each item has a case red on the 4w integration head b9165d2d (the
docstring says what it measured there), and every case is red on the
mutant its docstring names.

* Item 2 (the twin's dates): on the patient route the zone timed the visit
  dates again AFTER the dates zone made their day of the month up, setting
  them by rank to the real calendar's quantile points, so a clinic seen only
  on each month's first Monday came back with its real days. The generate
  step now times no date: every date column moves with its rows, and the
  dates zone writes its own columns again over the patients the zone's rows
  then form (one timeline a patient, the day of the month made up).
* Item 14 (whose model): the zone was written and read under the table's
  bare file name, checked against the header and the row count only, so a
  second table of the same name and header replaced the first one's model.
  It now joins the record bound to the description's own place and bytes,
  as the relations zone does.
* Item 15 (the gap model's cost): each patient's mean gap was taken again
  for every one of its gaps (quadratic in a long patient's rows).
* Item 16 (the recut's cost): every patient short of rows copied the whole
  donor list and walked it again from the start (quadratic in donors).

The command cases run the typed commands at 20,000 rows (1,000 people) on
two invented visit tables, in one installation, the patient layer switched
on in this process, the private folder the installation's own.
"""

from __future__ import annotations

import dataclasses
import datetime
import json
import math
import pathlib
import random
import sys
import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, inside_relations, inside_trajectories as I, installation

ROWS = 20000
PERSON = T.PERSON["T2"]
HEADER = [PERSON, "arm", "visit", "visit_date", "sbp"]


def _first_monday(year: int, month: int) -> datetime.date:
    day = datetime.date(year, month, 1)
    return day + datetime.timedelta(days=(7 - day.weekday()) % 7)


def _month_after(year: int, month: int, k: int) -> "tuple[int, int]":
    index = year * 12 + (month - 1) + k
    return index // 12, index % 12 + 1


def _person_rows(person: int, dates: "list[datetime.date]", r: random.Random) -> "list[str]":
    """One invented person's visits: an arm, the visit's number and date, a pressure with its own level and slope."""
    arm_b = r.random() < 0.5
    level = r.gauss(0.0, 12.0)
    slope = r.gauss(0.0, 0.6)
    noise = r.gauss(0.0, 8.0)
    out: "list[str]" = []
    for k in range(len(dates)):
        if k:
            noise = 0.5 * noise + r.gauss(0.0, 8.0 * math.sqrt(0.75))
        sbp = 138.0 + level + (-0.4 - 0.8 * arm_b + slope) * k + noise
        out += [",".join((f"P{1000000 + person}", "B" if arm_b else "A", f"{k + 1}", dates[k].isoformat(),
                          f"{int(round(sbp))}"))]
    return out


def _clinic_table() -> str:
    """Table A: 1,000 people of 20 visits each, every visit on its month's first Monday (consecutive months)."""
    r = random.Random("review-4w-c-A")
    lines = [",".join(HEADER)]
    for person in range(1000):
        year, month = _month_after(2021, 1, r.randrange(36))
        lines += _person_rows(person, [_first_monday(*_month_after(year, month, k)) for k in range(20)], r)
    return "\n".join(lines) + "\n"


def _other_table() -> str:
    """Table B: the same file name, header and rows, another census: 500 people of 10 visits and 500 of 30."""
    r = random.Random("review-4w-c-B")
    lines = [",".join(HEADER)]
    for person in range(1000):
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=r.randrange(700))
        dates: "list[datetime.date]" = []
        for k in range(10 if person % 2 == 0 else 30):
            if k:
                day = day + datetime.timedelta(days=28 + r.randint(-3, 3))
            dates += [day]
        lines += _person_rows(5000 + person, dates, r)
    return "\n".join(lines) + "\n"


def _private(folder: pathlib.Path) -> pathlib.Path:
    return pathlib.Path(folder, "installation", "synthtwin", inside.FOLDER)


def _described(folder: pathlib.Path, text: str) -> pathlib.Path:
    """Route S: the table described, its questions answered truthfully round by round; the description's path."""
    source = folder / "table" / "visits.csv"
    out = folder / "out"
    source.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    source.write_text(text, encoding="utf-8", newline="\n")
    questions = out / "visits-questions.json"
    code, said = B.command(["profile", str(source), "--out-dir", str(out), "--replace"], False)
    for _round in range(B.ROUNDS):
        assert code == 0, said
        written, _left = B.answer_questions(questions, "T2")
        if not written:
            break
        again = ["profile", str(source), "--out-dir", str(out), "--answers", str(questions)]
        code, said = B.command(again, False)
        if code != 0 and B.replace_description_known():
            code, said = B.command(again + ["--replace-description"], False)
    assert code == 0, said
    return out / "visits-profile.json"


def _generated(description: pathlib.Path) -> str:
    out = description.parent
    code, said = B.command(["generate", str(description), "--out-dir", str(out), "--seed", "0", "--replace"], False)
    assert code == 0, said
    return (out / "visits-twin.csv").read_text(encoding="utf-8")


def _column(text: str, name: str) -> "list[str]":
    lines = text.splitlines()
    at = lines[0].split(",").index(name)
    return [line.split(",")[at] for line in lines[1:]]


def _census(text: str) -> "dict[int, int]":
    counts: "dict[str, int]" = {}
    for key in _column(text, PERSON):
        counts[key] = counts[key] + 1 if key in counts else 1
    out: "dict[int, int]" = {}
    for value in counts.values():
        out[value] = out[value] + 1 if value in out else 1
    return out


@dataclasses.dataclass
class Made:
    clinic: str
    other: str
    twin: str
    dates_alone: str
    unhanded: str
    after_other: str
    tables: "dict[str, dict[str, object]]"


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> Made:
    folder = tmp_path_factory.mktemp("review-4w-c")
    clinic = _clinic_table()
    other = _other_table()

    def places() -> inside.Places:
        return inside.Places(pathlib.Path(installation.data_folder(), inside.FOLDER), (), (), installation.system_name())

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
        patch.setattr(inside, "default_places", places)
        with B.installed(folder):
            first = _described(folder / "a", clinic)
            twin = _generated(first)
            with pytest.MonkeyPatch.context() as off:
                # The yardstick: the same description and seed with the zone's application left out, so the dates are
                # the dates zone's alone (its made-up days).
                off.setattr(I, "twin_with_zone", lambda twin_made, *args, **kwargs: twin_made)
                dates_alone = _generated(first)
            with pytest.MonkeyPatch.context() as unhanded_patch:
                # The zone applied with no dates zone handed to it (a twin whose dates the dates zone did not write:
                # a workbook's, or a table past the rows the dates zone reads whole).
                unhanded_patch.setattr(cli, "_dates_drawn", lambda record, drawn: (None, []), raising=False)
                unhanded = _generated(first)
            _described(folder / "b", other)
            after_other = _generated(first)
    tables: "dict[str, dict[str, object]]" = {}
    for path in sorted(_private(folder).glob(f"*{inside.SUFFIX}")):
        record = inside.load_record(path)
        table = typing.cast("dict[str, object]", record["table"])
        zones = typing.cast("dict[str, object]", record["zones"])
        tables[path.name] = {"description": table["description"] if "description" in table else None,
                             "trajectories": I.ZONE in zones}
    return Made(clinic, other, twin, dates_alone, unhanded, after_other, tables)


# -- item 2 ---------------------------------------------------------------------------------------------------


def test_the_twin_dates_keep_their_made_up_days_through_the_trajectories_zone(made: Made) -> None:
    """A clinic seen only on each month's first Monday: with the zone applied, the twin's visit dates land on a real
    day about as often as the dates zone's own made-up days do (within half again, and on under half the rows), never
    as the real calendar's points put them (b9165d2d: 18,920 of 20,000, against 5,412 for the dates zone alone; this
    head 6,515), and every one is still a Monday (b9165d2d: 18,920). Mutant: the generate step lets the zone time the
    dates again (`dates_kept` off)."""
    real = set(_column(made.clinic, "visit_date"))
    twin = _column(made.twin, "visit_date")
    alone = _column(made.dates_alone, "visit_date")
    assert len(twin) == ROWS and len(alone) == ROWS
    on_real = sum(1 for cell in twin if cell in real)
    yardstick = sum(1 for cell in alone if cell in real)
    assert 0 < yardstick < 0.5 * ROWS, yardstick
    assert on_real <= 1.5 * yardstick and on_real < 0.5 * ROWS, (on_real, yardstick)
    assert all(datetime.date.fromisoformat(cell).weekday() == 0 for cell in twin)


def test_each_twin_patient_is_one_timeline_in_its_rows_order(made: Made) -> None:
    """The zone still sets the census (1,000 people of 20 rows, where the walk alone gives 13 to 27), and the dates
    zone writes the dates again over the patients the rows then form: each patient's dates rise with its rows and its
    visit numbers 1 to 20 (the second clause of the item's fix; b9165d2d timed them in order, from the real days).
    Mutant: the dates zone's columns not written again after the rows move (they move with their rows)."""
    assert _census(made.twin) == {20: 1000}
    assert _census(made.dates_alone) != {20: 1000}
    keys = _column(made.twin, PERSON)
    dates = _column(made.twin, "visit_date")
    visits = _column(made.twin, "visit")
    broken = 0
    for row in range(1, len(keys)):
        if keys[row] == keys[row - 1]:
            if dates[row] < dates[row - 1] or int(visits[row]) != int(visits[row - 1]) + 1:
                broken += 1
    assert broken == 0, broken


def test_a_twin_without_its_dates_zone_keeps_its_dates_off_the_real_calendar(made: Made) -> None:
    """Where no dates zone is handed to the zone (the twin's dates not the dates zone's to write again), the zone
    still sets the census and times no date: the dates move with their rows, so they land on a real day as often as
    before the zone ran (b9165d2d: the real calendar's days, 18,920 of 20,000). Mutant: the zone times the dates where
    no dates zone is handed (`dates_kept` off on that path)."""
    real = set(_column(made.clinic, "visit_date"))
    yardstick = sum(1 for cell in _column(made.dates_alone, "visit_date") if cell in real)
    unhanded = _column(made.unhanded, "visit_date")
    assert _census(made.unhanded) == {20: 1000}
    assert sorted(unhanded) == sorted(_column(made.dates_alone, "visit_date"))
    assert sum(1 for cell in unhanded if cell in real) == yardstick


# -- item 14 --------------------------------------------------------------------------------------------------


def test_two_tables_of_one_name_and_header_keep_their_own_models(made: Made) -> None:
    """Table B, of the same file name, header and rows, profiled after table A into another folder of the same
    installation, leaves A's model alone: A's twin keeps A's census (b9165d2d: B's 500 of 10 and 500 of 30), and the
    private folder holds one record a description, each with the zone, each naming its own description's bytes.
    Mutant: the zone written and read under the table's bare name again."""
    assert _census(made.other) == {10: 500, 30: 500}
    assert _census(made.after_other) == {20: 1000}
    bound = [name for name, table in made.tables.items() if table["trajectories"]]
    assert len(bound) == 2, made.tables
    digests = {json.dumps(made.tables[name]["description"], sort_keys=True) for name in bound}
    assert len(digests) == 2 and all(made.tables[name]["description"] is not None for name in bound)


def test_a_zone_is_read_only_beside_the_bytes_it_was_written_for(tmp_path: pathlib.Path,
                                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """The record at a description's place gives its zone for those very bytes only: the description written anew at
    that place with the same columns and rows (another table's), the same bytes at another place, or another row
    count get none; the zone joins the record written beside its description (keeping its other zones) and never
    makes a record of its own (b9165d2d: no such binding; the record was found by the table's bare name). Mutant: the
    description's digest not compared on reading."""
    private = tmp_path / "private"
    places = inside.Places(private, (), (), "posix")
    monkeypatch.setattr(inside, "default_places", lambda: places)
    real = _recut_table(60)
    names = list(real)
    rows = len(real["pid"])
    zone = I.zone_from_columns(real, "pid", ())
    assert zone is not None
    description = tmp_path / "out" / "visits-profile.json"
    description.parent.mkdir()
    description.write_text('{"a": 1}\n', encoding="utf-8", newline="\n")
    target = cli._inside_record_at(description, private)
    data = description.read_bytes()
    bound: "dict[str, object]" = {"digest": inside_relations.digest_of(data), "bytes": len(data)}
    assert I.write_zone(zone, "", rows, names, places, at=target, description=bound) is None
    assert not target.exists()
    record = {"format": inside.FORMAT, "version": inside.VERSION, "mode": inside.MODE,
              "table": {"rows": rows, "columns": names, "description": bound}, "zones": {"marginals": {}}}
    inside.write_record(record, target, places)
    assert I.write_zone(zone, "", rows, names, places, at=target, description={"digest": "0", "bytes": 1}) is None
    assert I.write_zone(zone, "", rows, names, places, at=target, description=bound) is not None
    kept = inside.load_record(target)
    assert sorted(typing.cast("dict[str, object]", kept["zones"])) == ["marginals", I.ZONE]
    assert cli._inside_trajectories_for(f"{description}", names, rows) == json.loads(json.dumps(zone))
    assert cli._inside_trajectories_for(f"{description}", names, rows + 1) is None
    elsewhere = tmp_path / "other" / "visits-profile.json"
    elsewhere.parent.mkdir()
    elsewhere.write_bytes(data)
    assert cli._inside_trajectories_for(f"{elsewhere}", names, rows) is None
    description.write_text('{"a": 2}\n', encoding="utf-8", newline="\n")
    assert cli._inside_trajectories_for(f"{description}", names, rows) is None


# -- items 15 and 16: linear growth, counted ------------------------------------------------------------------


class _TooMuch(Exception):
    pass


def _lines_run(call: "typing.Callable[[], object]", most: int) -> int:
    """The lines of Python run while `call` runs (every function it calls included); stops past `most`."""
    count = [0]

    def local(frame: object, event: str, arg: object) -> object:
        if event == "line":
            count[0] += 1
            if count[0] > most:
                raise _TooMuch()
        return local

    def top(frame: object, event: str, arg: object) -> object:
        return local

    previous = sys.gettrace()
    sys.settrace(top)  # type: ignore[arg-type]
    try:
        call()
    finally:
        sys.settrace(previous)
    return count[0]


def _grows_linearly(work: "typing.Callable[[int], typing.Callable[[], object]]", size: int) -> "tuple[int, int]":
    """The lines run at `size` and at twice it; the second stopped once past three times the first."""
    small = _lines_run(work(size), 10 ** 9)
    try:
        large = _lines_run(work(2 * size), 3 * small)
    except _TooMuch:
        large = 3 * small + 1
    return small, large


def _long_patient(size: int) -> "tuple[list[int | None], list[list[int]], list[int]]":
    """One patient of `size` dated rows (gaps of 7 to 11 days) beside 200 patients of two rows."""
    anchor: "list[int | None]" = []
    members: "list[list[int]]" = []
    rows_of: "list[int]" = []
    for k in range(size):
        rows_of += [len(anchor)]
        anchor += [86400 * (k * 7 + k % 5)]
    members += [rows_of]
    for p in range(200):
        members += [[len(anchor), len(anchor) + 1]]
        anchor += [86400 * p, 86400 * (p + 7 + p % 9)]
    return anchor, members, [len(rows) for rows in members]


def _gap_work(monkeypatch: pytest.MonkeyPatch) -> "typing.Callable[[int], typing.Callable[[], object]]":
    # The serial term's calibration simulates on the patients' own lengths (linear, and not the subject here).
    monkeypatch.setattr(I, "calibrated_lag", lambda observed, sample, detrended: observed)

    def at(size: int) -> "typing.Callable[[], object]":
        anchor, members, lengths = _long_patient(size)
        return lambda: I._gap_entry(anchor, members, lengths)

    return at


def test_the_gap_model_takes_each_patients_mean_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """One patient of 600 rows, then of 1,200, beside 200 of two rows: the gap model's work doubles, never quadruples
    (b9165d2d: the patient's mean taken again for every gap; at 20,000 rows, one patient of 18,002 rows, 3.8 CPU s
    against 0.6). Mutant: the per-gap mean restored."""
    small, large = _grows_linearly(_gap_work(monkeypatch), 600)
    assert large <= 2.5 * small, (small, large)


def test_the_gap_model_reads_each_patients_own_mean(monkeypatch: pytest.MonkeyPatch) -> None:
    """The serial term and the paces' tie to the rows are those of each patient's gaps about its own mean, worked
    out here the plain way (the mean taken again for each gap, as before the change): the same numbers, bit for bit.
    Mutant: the deviations taken about the first patient's mean."""
    anchor, members, lengths = _long_patient(300)
    gaps = typing.cast("dict[str, object]", _gap_work(monkeypatch)(300)())
    assert gaps is not None
    found: "list[float]" = []
    owner: "list[int]" = []
    for patient in range(len(members)):
        for place in range(1, len(members[patient])):
            found += [float(typing.cast(int, anchor[members[patient][place]])
                            - typing.cast(int, anchor[members[patient][place - 1]]))]
            owner += [patient]
    scores = I.mid_scores(found)
    rows_scores = I.mid_scores([float(length) for length in lengths])
    sxy = sum(rows_scores[owner[at]] * scores[at] for at in range(len(found)))
    sxx = sum(rows_scores[owner[at]] * rows_scores[owner[at]] for at in range(len(found)))
    term = I._bounded(sxy / sxx, -I.CORR_MOST, I.CORR_MOST)
    by_patient: "dict[int, list[float]]" = {}
    for at in range(len(found)):
        by_patient.setdefault(owner[at], []).append(scores[at] - term * rows_scores[owner[at]])
    patients = sorted(by_patient)
    deviations = [[value - I._mean(by_patient[patient]) for value in by_patient[patient]] for patient in patients]
    lag = I._bounded(I._residual_lag(deviations), I.LAG_LEAST, I.LAG_MOST)
    paces = [I._mean(by_patient[patient]) for patient in patients]
    tie = I._bounded(I._corr(paces, [rows_scores[patient] for patient in patients]), -I.CORR_MOST, I.CORR_MOST)
    assert gaps["lag1"] == lag and gaps["pace_rows"] == tie, (gaps["lag1"], lag, gaps["pace_rows"], tie)


def _recut_table(patients: int) -> "dict[str, list[str]]":
    """An invented table of `patients` people of two rows, a fixed column whose cells differ from person to person."""
    real: "dict[str, list[str]]" = {"pid": [], "baseline": [], "reading": []}
    for p in range(patients):
        for k in range(2):
            real["pid"] += [f"R{1000000 + p}"]
            real["baseline"] += [f"{p * 7.123457:.6f}"]
            real["reading"] += [f"{120 + (p * 11 + k * 5) % 40}"]
    return real


def _recut_work() -> "typing.Callable[[int], typing.Callable[[], object]]":
    def at(size: int) -> "typing.Callable[[], object]":
        zone = I.zone_from_columns(_recut_table(2 * size), "pid", ())
        assert zone is not None and zone["fixed"] == ["baseline"]
        twin: "dict[str, list[str]]" = {"pid": [], "baseline": [], "reading": []}
        for p in range(2 * size):
            for k in range(3 if p < size else 1):
                twin["pid"] += [f"T{1000000 + p}"]
                twin["baseline"] += [f"{(p + 0.5) * 7.123457:.6f}"]
                twin["reading"] += [f"{120 + (p * 3 + k) % 40}"]
        return lambda: I._recut(zone, {name: list(cells) for name, cells in twin.items()},
                                I._patients_of(twin["pid"])[1], "pid", ["baseline"])

    return at


def test_the_recut_reads_each_donor_once() -> None:
    """300 patients of one row too many, each with fixed cells of its own, and 300 of one row too few; then 600 and
    600: the recut's work doubles, never quadruples (b9165d2d: each patient short of rows copied and walked the whole
    donor list; at 20,000 rows, 5,000 and 5,000, 1.1 CPU s against 0.3, the same rows moved), and every patient meets
    the census. Mutant: the walk through the whole pool restored."""
    work = _recut_work()
    small, large = _grows_linearly(work, 300)
    assert large <= 2.5 * small, (small, large)
    cut = work(300)()
    assert cut is not None
    members = typing.cast("tuple[list[list[int]], list[int] | None]", cut)[0]
    assert sorted({len(rows_of) for rows_of in members}) == [2]


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield

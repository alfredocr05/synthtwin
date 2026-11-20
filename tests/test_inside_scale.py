"""Gate file of lane IN-8 (plan P4-D502): the inside record read a column at a time, drawn a block at a time, its size bound to its columns.

THE BOUND. The whole record `synthtwin profile` writes (the marginals,
the relations and the dates zones) for an invented table of several rows
a person, dates with a clock, labels and related numbers grows by under
5 per cent when the rows double (20,000, the owner's table floor, against
40,000), and no list in it is longer than the quantile grid: a model,
never data (PLAN-INSIDE 1.1). Mutant: the dates zone keeps each date
column's present rows.

ONE READING. The profile hook asks the reader for each column of the
table once (the person column once more, for the persons first), so a
table read in groups of columns is read once a group for the whole
record. Mutant: the dates zone reads the table a second time, as it did
before lane IN-8. At batch 4x's merge the keyed zone (plan P4-D499),
which reads the table whole, walks it once more where a person column
repeats and the table holds at most `cli._KEYED_ZONE_MOST_ROWS` rows:
the one reading is held past that bound (set to 30,000 rows here, so
the 40,000-row run is past it), and the keyed walk under it is counted,
the zone's own sub-switch set on in place (off on the shipped route
since batch 4x, plan P4-D503).

THE CENSUS. The dates zone's census, a column at a time, keeps a date
column's days and seconds and a label column's words, each value one
object, and nothing of a column of numbers or of free text. Mutants: a
number column kept as a label; the days kept one object a row.

THE DRAW'S BLOCK. A twin drawn with blocks of 7 rows is the twin drawn
with the default block, byte for byte, and no term of the draw is made
for more rows than a block. Mutants: the block is the whole table; a
block reads its rows' words from the block's start.

THE HELD FRAME. A frame held compactly gives back its rows as they were,
a score of -0.0 apart from 0.0. Mutant: zeros held by value.

THE DATES HELD. `write_dates_held` holds the cells `write_dates` writes.
Mutant: the held columns spelled on another stream.

Each clause is red on its mutant (lane IN-8's report).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import math
import pathlib
import random

import pytest

import reliability_tables as T
from synthtwin import cli, inside, inside_dates, inside_relations, installation, reading


def _places(folder: pathlib.Path) -> inside.Places:
    """The run's own installation's private folder, no temporary folder refused (the suite's folders are temporary)."""
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _day(day: int) -> str:
    import datetime

    return (datetime.date(2031, 1, 1) + datetime.timedelta(days=day)).isoformat()


def _visits(rows: int, seed: int) -> str:
    """An invented table of visits: a person's several rows, a start and a stop with a clock, labels, related numbers."""
    draw = random.Random(f"scale-{seed}-{rows}")
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["pid", "start", "stop", "service", "flag", "n1", "n2", "n3", "note", "code"])
    person, left, day, base = 0, 0, 0, 0.0
    for row in range(rows):
        if left == 0:
            person += 1
            left = 1 + min(11, int(draw.expovariate(0.3)))
            day = draw.randrange(1200)
            base = draw.gauss(0.0, 3.0)
        else:
            day += 7 + int(draw.expovariate(1.0 / 20.0))
        left -= 1
        if (day + 2) % 7 >= 5 and draw.random() < 0.8:
            day += 7 - (day + 2) % 7
        minute = 450 if draw.random() < 0.13 else 480 + 15 * draw.randrange(36)
        service = draw.choice(("A", "B", "C", "D"))
        flag = draw.random() < 0.35
        length = {"A": 30, "B": 60, "C": 120, "D": 240}[service] + int(draw.expovariate(1.0 / 15.0))
        n1 = 50.0 + 6.0 * flag + {"A": 0.0, "B": 3.0, "C": 6.0, "D": 9.0}[service] + base + draw.gauss(0.0, 8.0)
        n2 = 20.0 + 0.4 * (n1 - 50.0) + 4.0 * (flag and service == "B") + draw.gauss(0.0, 4.0)
        n3 = 10.0 + 0.02 * (n1 - 50.0) ** 2 + draw.gauss(0.0, 2.0)
        stop = minute + length
        writer.writerow([f"P{100000 + 7 * person}", f"{_day(day)} {minute // 60:02d}:{minute % 60:02d}",
                         f"{_day(day + stop // 1440)} {(stop % 1440) // 60:02d}:{stop % 60:02d}",
                         service, "Y" if flag else "N", f"{n1:.1f}", "" if draw.random() < 0.03 else f"{n2:.1f}",
                         f"{n3:.1f}", f"review in {draw.randint(1, 60)} days" if draw.random() < 0.3 else "no change",
                         f"C{500000 + 13 * row}"])
    return out.getvalue()


def _answered(questions: pathlib.Path) -> int:
    """An answer written to every open question (the first offered of a fixed list); how many."""
    document = json.loads(questions.read_text(encoding="utf-8"))
    wrote = 0
    entries: "list[object]" = list(document.get("about_your_file") or []) + list(document.get("asked") or [])
    checklist = document.get("checklist")
    if isinstance(checklist, dict):
        entries += list(checklist.get("columns") or [])
    for entry in entries:
        if isinstance(entry, dict) and "answers_you_can_give" in entry and not entry.get("your_answer"):
            offered = [str(a.get("answer")) for a in entry["answers_you_can_give"] if isinstance(a, dict)]
            for pick in ("keep", "no", "measurement", "code", "label"):
                if pick in offered:
                    entry["your_answer"] = pick
                    wrote += 1
                    break
    questions.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8", newline="\n")
    return wrote


def _profiled(folder: pathlib.Path, text: str) -> "tuple[pathlib.Path, pathlib.Path]":
    """`synthtwin profile` of the table, the answers' rounds after; the description and the record."""
    table = pathlib.Path(folder, "visits.csv")
    table.write_text(text, encoding="utf-8", newline="\n")
    out = pathlib.Path(folder, "out")
    out.mkdir()
    argv = ["profile", str(table), "--out-dir", str(out), "--person", "pid", "--identifier", "code"]
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
        questions = pathlib.Path(out, "visits-questions.json")
        rounds = 1
        while code != 0 and rounds < 4 and questions.exists() and _answered(questions):
            code = cli.main(argv + ["--answers", str(questions), "--replace"])
            rounds += 1
    assert code == 0, said.getvalue()[-2000:]
    records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    return pathlib.Path(out, "visits-profile.json"), records[0]


def _lists(value: object) -> "list[int]":
    if isinstance(value, list):
        return [len(value)] + [n for item in value for n in _lists(item)]
    if isinstance(value, dict):
        return [n for item in value.values() for n in _lists(item)]
    return []


@pytest.fixture(scope="module")
def two_sizes(tmp_path_factory: pytest.TempPathFactory) -> "dict[int, dict[str, object]]":
    """The record of the invented table at 20,000 and 40,000 rows, and the reader's calls the hook made at 20,000."""
    made: "dict[int, dict[str, object]]" = {}
    for rows in (20_000, 40_000):
        folder = tmp_path_factory.mktemp(f"scale-{rows}")
        asked: "dict[int, int]" = {}
        in_hook = [False]
        original_hook = cli._inside_record_written
        original_values = reading.column_values

        def hook(*args: object, **kwargs: object) -> object:
            in_hook[0] = True
            try:
                return original_hook(*args, **kwargs)  # type: ignore[arg-type]
            finally:
                in_hook[0] = False

        def values(table: object, place: int) -> "list[str]":
            if in_hook[0]:
                asked[place] = asked.get(place, 0) + 1
            return original_values(table, place)  # type: ignore[arg-type]

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(inside, "default_places", lambda: _places(folder))
            patch.setattr(cli, "_inside_record_written", hook)
            patch.setattr(reading, "column_values", values)
            # The keyed zone's bound between the two sizes: 20,000 rows under it, 40,000 past it (ONE READING); its
            # own sub-switch on, as the 4x merge measured it (off on the shipped route, plan P4-D503).
            patch.setattr(cli, "_KEYED_ZONE_MOST_ROWS", 30_000)
            patch.setattr(cli, "_KEYED_ZONE_SHIPPED", True)
            described, record = _profiled(folder, _visits(rows, 1))
        loaded = inside.load_record(record)
        made[rows] = {"bytes": record.stat().st_size, "record": loaded, "asked": asked, "described": described}
    return made


def test_the_whole_record_keeps_its_size_when_the_rows_double(two_sizes) -> None:  # type: ignore[no-untyped-def]
    small, large = two_sizes[20_000], two_sizes[40_000]
    zones = large["record"]["zones"]
    assert sorted(zones) == ["dates", "marginals", "relations"], sorted(zones)
    assert large["bytes"] <= 1.05 * small["bytes"], f"{small['bytes']} bytes at 20,000 rows, {large['bytes']} at 40,000"
    for rows in (20_000, 40_000):
        longest = max(_lists(two_sizes[rows]["record"]))
        assert longest <= inside.GRID, f"a list of {longest} entries in the record at {rows} rows"


def test_the_profile_hook_reads_each_column_once(two_sizes) -> None:  # type: ignore[no-untyped-def]
    # Past the keyed zone's bound (40,000 rows): the record's one reading, the person column once more.
    asked = two_sizes[40_000]["asked"]
    columns = len(two_sizes[40_000]["record"]["table"]["columns"])
    assert sorted(asked) == list(range(columns)), asked
    person_place = two_sizes[40_000]["record"]["table"]["columns"].index("pid")
    for place, times in asked.items():
        assert times <= (2 if place == person_place else 1), f"column {place} read {times} times by the hook"
    # Under it (20,000 rows), the keyed zone's one walk more (plan P4-D499), and nothing beyond it.
    asked = two_sizes[20_000]["asked"]
    assert sorted(asked) == list(range(columns)), asked
    for place, times in asked.items():
        assert times <= (3 if place == person_place else 2), f"column {place} read {times} times by the hook"


def test_the_census_keeps_dates_and_labels_each_value_one_object() -> None:
    rows = 5000
    draw = random.Random(7)
    gathered = inside_dates.census("pid", None, ("code",))
    columns = {
        "pid": [f"P{row // 4}" for row in range(rows)],
        "when": [f"{_day(draw.randrange(900))} {draw.randrange(24):02d}:{15 * draw.randrange(4):02d}" for _row in range(rows)],
        "unit": [draw.choice(("ward", "clinic", "home")) for _row in range(rows)],
        "value": [f"{draw.gauss(80.0, 12.0):.3f}" for _row in range(rows)],
        "note": [f"seen {draw.randrange(100000)} times" for _row in range(rows)],
        "code": [f"C{row}" for row in range(rows)],
    }
    for name in columns:
        inside_dates.take_column(gathered, name, [f"{cell}" for cell in columns[name]])
    assert sorted(gathered.days_of) == ["when"] and sorted(gathered.seconds_of) == ["when"]
    assert sorted(gathered.labels) == ["unit"], sorted(gathered.labels)
    assert gathered.keys is not None and len(gathered.keys) == rows
    for held in (gathered.days_of["when"], gathered.seconds_of["when"], gathered.labels["unit"], gathered.keys):
        objects = len(set(id(value) for value in held))
        assert objects == len(set(held)), f"{objects} objects for {len(set(held))} values"
    zone = inside_dates.zone_of(gathered)
    assert zone == inside_dates.build_zone(columns, "pid", None, ("code",))
    assert zone["order"] == ["when"]


def _draw(folder: pathlib.Path, described: pathlib.Path, block: int, seen: "list[int]") -> bytes:
    """The twin of `described` with the draw's block set to `block`; the most rows a term of the draw was made for."""
    out = pathlib.Path(folder, f"twin-{block}")
    out.mkdir()
    in_draw = [False]
    original_draw = inside_relations.draw_columns
    original_terms = inside_relations.term_values

    def draw(*args: object, **kwargs: object) -> object:
        in_draw[0] = True
        try:
            return original_draw(*args, **kwargs)  # type: ignore[arg-type]
        finally:
            in_draw[0] = False

    def terms(term: object, frames: object, rows: int) -> "list[float]":
        if in_draw[0]:
            seen.append(rows)
        return original_terms(term, frames, rows)  # type: ignore[arg-type]

    said = io.StringIO()
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        patch.setattr(inside_relations, "DRAW_BLOCK", block)
        patch.setattr(inside_relations, "draw_columns", draw)
        patch.setattr(inside_relations, "term_values", terms)
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(["generate", str(described), "--out-dir", str(out), "--seed", "3"])
    assert code == 0, said.getvalue()[-2000:]
    report = pathlib.Path(out, "visits-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith("THIS TWIN WAS DRAWN FROM THE INSIDE RECORD")
    return pathlib.Path(out, "visits-twin.csv").read_bytes()


def test_the_draw_makes_its_terms_a_block_of_rows_at_a_time_and_the_twin_is_the_same(tmp_path: pathlib.Path) -> None:
    # At the owner's table floor: the record is written for a table at the floor alone (plan P4-D503, lane IN-2b).
    rows = 20_000
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(tmp_path))
        described, _record = _profiled(tmp_path, _visits(rows, 2))
    whole: "list[int]" = []
    small: "list[int]" = []
    first = _draw(tmp_path, described, inside_relations.DRAW_BLOCK, whole)
    second = _draw(tmp_path, described, 7, small)
    assert first == second, "the twin drawn with blocks of 7 rows differs from the default block's"
    assert whole and max(whole) <= rows
    assert small and max(small) <= 7, f"a term of the draw made for {max(small)} rows with blocks of 7"


def test_a_held_frame_gives_its_rows_back_as_they_were() -> None:
    draw = random.Random(11)
    rows = 2000
    scores = [draw.choice((0.0, -0.0, 0.25, -1.5, 2.0)) if draw.random() < 0.5 else draw.gauss(0.0, 1.0) for _row in range(rows)]
    states = [draw.randrange(5) for _row in range(rows)]
    number = inside_relations.Frame(inside_relations.NUMBER, scores, states, [])
    codes = [draw.randrange(300) for _row in range(rows)]
    label = inside_relations.Frame(inside_relations.LABEL, [], [], codes)
    for frame in (number, label):
        held = inside_relations.held_frame(frame, rows)
        assert held.held is not None and not held.scores and not held.codes
        for start, stop in ((0, rows), (0, 7), (13, 1029), (1990, rows)):
            back = inside_relations.frame_rows(held, start, stop)
            assert back.scores == frame.scores[start:stop] and back.states == frame.states[start:stop]
            assert back.codes == frame.codes[start:stop]
            assert [math.copysign(1.0, s) for s in back.scores] == [math.copysign(1.0, s) for s in frame.scores[start:stop]]


def test_the_dates_held_are_the_dates_written() -> None:
    text = T.text("T3", 4000, 1)
    body = list(csv.reader(io.StringIO(text)))
    columns = {name: [row[i] for row in body[1:]] for i, name in enumerate(body[0])}
    person = T.PERSON["T3"]
    zone = inside_dates.build_zone(columns, person)
    assert zone["order"]
    written = inside_dates.write_dates(zone, 4000, columns[person], None, None, None, 5)
    held = inside_dates.write_dates_held(zone, 4000, columns[person], None, None, None, 5)
    from synthtwin import twinstore

    assert sorted(written) == sorted(held)
    for name in written:
        assert twinstore.column_cells(held[name]) == written[name], name

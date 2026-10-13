"""The minute census of a column of clock times (stage 3b landing 3b.5's second step, lane C2, plan P4-D374).

A column of clock times publishing its step publishes, since this
landing, how many of its body's cells -- the heaps' among them -- fall on
each group of minutes of the hour (`minute_census`, the moments' key on
this role), and its twin meets it by method G7A.4c: each census group's
cells cut at its pins into stretches, the table of stretches by minute
groups fitted to both counts and rounded with both kept, completed along
shortest paths. Before it, appointment times typed on `:00` or `:30` at
a quarter or a fifth of their rows came back at 8 to 16 per cent there.
The gate's minute clause stands in `tests/test_stage3b_clock.py` (U);
this file holds the landing's own rules, each red on its mutant:

* the producer: flatness asked of CELLS, not different values
  (`test_flatness_is_asked_of_the_cells`); no few-values rule on this
  role (`test_no_few_values_rule_on_clock_times`); no middle-half rule
  (MC4), so walk-ins whose middle half spans 3.5 hours publish;
* the loader: MC1, MC2, MC3 (its total and its scope beside a step),
  and MC5, each refused by name; an empty census, and a description
  written before the key, load; and every description the producer
  writes over a battery of shapes, sizes, forms and floors loads
  (`test_every_description_the_producer_writes_loads`);
* the generator: every published census met and every twin validated;
  a column publishing none laid byte for byte as before; lanes keep off
  the places the table calls absent; a group on such places alone stands
  its cells on those the other width spells another way; heap ranks
  windowed by their group (G12.10b), the checker drawing them as the
  construction does;
* the checker: one cell moved off its minute is MISSED, and a MISSED line
  prints no count below the line;
* growth: placing the cells grows with the rows, and the table with the
  groups, never the rows -- machine-free line counts up to 100,000 rows;
* and the two items owed to the lane that touch the producer: route 1's
  rare words beside clock times stay present and unread, so no twin
  writes a blank the source never left (the 198 cells over 2 columns of
  the route-2 correction's capsweep tables), and a place the table calls
  absent holding the line in present cells of the other width is a heap
  (`tests/test_stage3b_clock_review.py` holds that one).
"""

from __future__ import annotations

import collections
import csv
import dataclasses
import io
import pathlib
import random
import sys
import tempfile
import typing

import pytest

import clock_census_shapes as shapes
import fixtures

from synthtwin import calendar_clock
from synthtwin import contract
from synthtwin import errors
from synthtwin import generation
from synthtwin import parsing
from synthtwin import profile
from synthtwin import reading
from synthtwin import rendering
from synthtwin import taxonomy
from synthtwin import validation

_HOME: "list[pathlib.Path]" = []


@pytest.fixture(scope="module", autouse=True)
def _home(tmp_path_factory: pytest.TempPathFactory) -> "typing.Iterator[None]":
    _HOME[:] = [tmp_path_factory.mktemp("clock-minutes")]
    yield


def _folder() -> pathlib.Path:
    return pathlib.Path(tempfile.mkdtemp(dir=_HOME[0]))


def _document(
    columns: "dict[str, list[str]]", floor: int = 11, declared: "tuple[str, ...]" = ()
) -> "tuple[dict[str, typing.Any], pathlib.Path, pathlib.Path]":
    """The table's description, its file and the table's file."""
    folder = _folder()
    names = tuple(columns)
    count = len(columns[names[0]])
    lines = [",".join(names)] + [
        ",".join(columns[name][index] for name in names) for index in range(count)
    ]
    table = fixtures.write(folder, "t.csv", "\n".join(lines) + "\n")
    settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=declared)
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor), settings, [], []
    )
    return document, fixtures.write_profile(folder, "p.json", document), table


def _twin(loaded: contract.Profile, seed: int) -> "tuple[dict[str, list[str]], pathlib.Path]":
    text = rendering.twin_csv(generation.generate(loaded, seed))
    path = fixtures.write(_folder(), f"twin-{seed}.csv", text)
    rows = list(csv.reader(io.StringIO(text)))
    return {name: [row[place] for row in rows[1:] if row] for place, name in enumerate(rows[0])}, path


def _checks(loaded: contract.Profile, path: pathlib.Path) -> "list[validation.Check]":
    return list(validation.measure(loaded, str(path)).checks)


def _missed(loaded: contract.Profile, path: pathlib.Path) -> "list[str]":
    return sorted(
        f"{check.column}:{check.subcheck}"
        for check in _checks(loaded, path)
        if check.verdict == validation.MISSED
    )


def _block(document: "dict[str, typing.Any]", name: str) -> "dict[str, typing.Any]":
    for block in document["columns"]:
        if block["name"] == name:
            return typing.cast("dict[str, typing.Any]", block)
    raise AssertionError(name)


def _second(text: str) -> "int | None":
    parts = parsing.clock_parts(text)
    if parts is None:
        return None
    return parsing.clock_second(parts, parts[5])


def _slots(cells: "list[str]") -> float:
    read = [second for second in (_second(cell) for cell in cells) if second is not None]
    return sum(1 for second in read if (second // 60) % 60 in (0, 30)) / max(1, len(read))


_BATTERY = shapes.CLOCKS


# -- the producer -----------------------------------------------------------


def test_the_battery_publishes_where_the_minutes_are_heaped() -> None:
    """At 1,000 rows and a floor of eleven the five shapes typed on `:00` and
    `:30` or booked on a grid publish their minute census, and the eight whose
    cells off the heaps are flat over the minutes publish none."""
    columns = {name: shapes.cells(name, 1000) for name in _BATTERY}
    document, _path, _table = _document(columns)
    published = sorted(name for name in _BATTERY if _block(document, name)["minute_census"])
    assert published == ["ampm", "clinic", "ed_triage_s", "excel_hmm", "walkin"], published


def test_flatness_is_asked_of_the_cells(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: flatness asked of the different values, as the moments' census
    asks it -- triage times typed on `:00` and `:30` and walk-ins on a
    ten-minute grid hold about as many different values on every minute,
    and neither publishes."""
    built = calendar_clock.clock_minute_decision

    def by_value(ordinals, form, step, line, body, heaps, published, size):  # type: ignore[no-untyped-def]
        flat = {at: 1 for at in ordinals}
        heaped = {at for at, _count in heaps}
        if not calendar_clock.departs_from_flat(
            [
                sum(1 for at in flat if at not in heaped and calendar_clock.clock_minute_of(at, form) == minute)
                for minute in range(60)
            ]
        ):
            return (), calendar_clock.FIELD_REASON_FLAT
        return built(ordinals, form, step, line, body, heaps, published, size)

    monkeypatch.setattr(calendar_clock, "clock_minute_decision", by_value)
    columns = {name: shapes.cells(name, 1000) for name in ("ed_triage_s", "walkin")}
    document, _path, _table = _document(columns)
    assert [_block(document, name)["minute_census"] for name in columns] == [[], []]


def test_no_few_values_rule_on_clock_times(monkeypatch: pytest.MonkeyPatch) -> None:
    """Clinic slots of 14 to 35 rows below a raised floor of 36 publish their
    minute census and their twins come back near the table's share on `:00`
    or `:30` (71 per cent; 51 with no census, the open item of plan P4-D373).
    MUTATION: the moments' few-values rule asked of the cells on no heap --
    the census is left out."""
    columns = {"clinic": shapes.cells("clinic", 1000)}
    document, path, _table = _document(columns, floor=36)
    block = _block(document, "clinic")
    assert block["minute_census"], block["minute_census"]
    loaded = contract.load_profile(str(path))
    for seed in (0, 4):
        twin, twin_path = _twin(loaded, seed)
        assert abs(_slots(twin["clinic"]) - _slots(columns["clinic"])) <= 0.04, seed
        assert _missed(loaded, twin_path) == []
    built = calendar_clock.field_groups

    def few(bins, sure, line):  # type: ignore[no-untyped-def]
        groups = built(bins, sure, line)
        return () if calendar_clock.few_values(groups, [2] * 60, ()) else groups

    monkeypatch.setattr(calendar_clock, "field_groups", few)
    document, _path, _table = _document(columns, floor=36)
    assert _block(document, "clinic")["minute_census"] == []


def test_no_middle_half_rule_on_clock_times() -> None:
    """MC4 does not apply (the 3b.5 skeptic's MINOR 3): walk-ins whose middle
    half spans under four hours publish their minute census, and it loads."""
    columns = {"walkin": shapes.cells("walkin", 1000)}
    document, path, _table = _document(columns)
    block = _block(document, "walkin")
    ladder = block["clock_percentiles"]
    span = _second(ladder["p75"]) - _second(ladder["p25"])  # type: ignore[operator]
    assert span < 4 * 3600 and block["minute_census"], (span, block["minute_census"])
    assert isinstance(contract.load_profile(str(path)), contract.Profile)


# -- the loader ---------------------------------------------------------------


def _walkin_document() -> "tuple[dict[str, typing.Any], pathlib.Path]":
    columns = {"walkin": shapes.cells("walkin", 1000)}
    document, path, _table = _document(columns)
    assert _block(document, "walkin")["minute_census"]
    return document, path


def _refused(document: "dict[str, typing.Any]") -> str:
    path = fixtures.write_profile(_folder(), "edited.json", document)
    try:
        contract.load_profile(str(path))
    except errors.ProfileError as refusal:
        return str(refusal)
    return ""


def _edited(change: "typing.Callable[[dict[str, typing.Any]], None]") -> str:
    document, _path = _walkin_document()
    change(_block(document, "walkin"))
    return _refused(document)


def _gap(block: "dict[str, typing.Any]") -> None:
    block["minute_census"] = block["minute_census"][1:]


def _overrun(block: "dict[str, typing.Any]") -> None:
    last = block["minute_census"][-1]
    block["minute_census"][-1] = {**last, "last": 60}


def _five(block: "dict[str, typing.Any]") -> None:
    """A group of several minutes splits its last minute off as a group of 5."""
    groups = block["minute_census"]
    for index in range(len(groups)):
        group = groups[index]
        if group["first"] < group["last"] and group["count"] >= 16:
            groups[index] = {**group, "last": group["last"] - 1, "count": group["count"] - 5}
            groups.insert(index + 1, {"first": group["last"], "last": group["last"], "count": 5})
            return
    raise AssertionError("no group to split")


def _one_off(block: "dict[str, typing.Any]") -> None:
    first = block["minute_census"][0]
    block["minute_census"][0] = {**first, "count": first["count"] + 1}


def _no_step(block: "dict[str, typing.Any]") -> None:
    block["clock_step"] = None
    block["clock_census"] = []
    block["clock_heaps"] = []
    block["clock_codes"] = []


def _below_the_heaps(block: "dict[str, typing.Any]") -> None:
    """A heap's cells moved out of the group of its minute: the group then
    holds fewer cells than its heaps put there for certain."""
    heap = block["clock_heaps"][0]
    minute = (_second(heap["value"]) // 60) % 60  # type: ignore[operator]
    groups = block["minute_census"]
    for index in range(len(groups)):
        group = groups[index]
        if group["first"] <= minute <= group["last"]:
            other = index + 1 if index + 1 < len(groups) else index - 1
            moved = group["count"] - heap["count"] + 1
            groups[index] = {**group, "count": group["count"] - moved}
            groups[other] = {**groups[other], "count": groups[other]["count"] + moved}
            return
    raise AssertionError("no group holds the heap")


@pytest.mark.parametrize(
    "rule,change",
    [
        ("MC1", _gap),
        ("MC1", _overrun),
        ("MC2", _five),
        ("MC3", _one_off),
        ("MC3", _no_step),
        ("MC5", _below_the_heaps),
    ],
)
def test_the_loader_refuses_a_broken_minute_census(
    rule: str, change: "typing.Callable[[dict[str, typing.Any]], None]"
) -> None:
    refusal = _edited(change)
    assert f"(it is called {rule} " in refusal, refusal


def test_an_empty_minute_census_and_one_written_before_load() -> None:
    document, _path = _walkin_document()
    block = _block(document, "walkin")
    block["minute_census"] = []
    assert _refused(document) == ""
    del block["minute_census"]
    assert _refused(document) == ""


# THE PRODUCER-ALWAYS-LOADS BATTERY: every description the producer writes of
# a clock column loads, over shapes typed on minutes, grids, columns at the
# second and on the 12-hour face, columns with no tails, columns beside
# declared absences of either hour width and beside rare words, at sizes from
# 100 to 3,000 rows and floors of 2, 11 and 36.


def _shape(kind: int, rows: int, draw: random.Random) -> "tuple[list[str], tuple[str, ...]]":
    out: "list[str]" = []
    declared: "tuple[str, ...]" = ()
    for _row in range(rows):
        hour = draw.choice((7, 8, 9, 10, 13, 14, 20, 23, 0, 3))
        minute = draw.choice((0, 15, 30, 45)) if draw.random() < 0.4 else draw.randrange(60)
        if kind == 0:
            out += [f"{hour:02d}:{minute:02d}"]
        elif kind == 1:
            out += [f"{hour:02d}:{minute:02d}:{draw.randrange(60) if draw.random() < 0.7 else 0:02d}"]
        elif kind == 2:
            out += [parsing.written_clock(hour * 3600 + minute * 60, False, "h AM-PM")]
        elif kind == 3:
            out += [f"{hour:02d}:{minute - minute % 10:02d}"]
        elif kind == 4:
            out += [f"{hour}:{minute:02d}" if hour < 10 and draw.random() < 0.2 else f"{hour:02d}:{minute:02d}"]
            declared = ("08:00", "07:30")
        else:
            out += ["UNK" if draw.random() < 0.012 else f"{hour:02d}:{minute:02d}"]
    if kind == 4:
        out += ["08:00"] * 9 + ["07:30"] * 4
    return out, declared


def test_every_description_the_producer_writes_loads() -> None:
    """Six kinds of clock column at five sizes and three floors, two seeds each:
    every description loads, and at least a third of them publish a minute
    census."""
    loaded = 0
    published = 0
    for kind in range(6):
        for rows in (100, 300, 1000, 3000):
            for floor in (2, 11, 36):
                for seed in (0, 1):
                    cells, declared = _shape(kind, rows, random.Random(1000 * kind + rows + floor + seed))
                    document, path, _table = _document({"c": cells}, floor=floor, declared=declared)
                    contract.load_profile(str(path))
                    loaded = loaded + 1
                    if document["columns"][0].get("minute_census"):
                        published = published + 1
    assert loaded == 144 and published * 3 >= loaded, (loaded, published)


# -- the generator and the checker ----------------------------------------------


@pytest.mark.parametrize("rows,floor", ((1000, 11), (1000, 36), (300, 11)))
def test_every_published_minute_census_is_met(rows: int, floor: int) -> None:
    columns = {name: shapes.cells(name, rows) for name in _BATTERY}
    document, path, table = _document(columns, floor=floor)
    loaded = contract.load_profile(str(path))
    publishing = [name for name in _BATTERY if _block(document, name)["minute_census"]]
    assert _missed(loaded, table) == []
    for seed in (0, 4):
        _twin_cells, twin_path = _twin(loaded, seed)
        checks = _checks(loaded, twin_path)
        held = sorted(
            check.column for check in checks if check.subcheck == "minute_census.groups" and check.verdict == validation.HELD
        )
        assert held == sorted(publishing), (rows, floor, seed, held, publishing)
        assert [check for check in checks if check.verdict == validation.MISSED] == []


def test_a_column_publishing_no_minute_census_is_laid_as_before(monkeypatch: pytest.MonkeyPatch) -> None:
    """Byte for byte: every column of the battery publishing no minute census
    writes the same cells with the minute step withdrawn, and one publishing
    it does not (the step's own mutant)."""
    columns = {name: shapes.cells(name, 1000) for name in _BATTERY}
    document, path, _table = _document(columns)
    loaded = contract.load_profile(str(path))
    now, _path_now = _twin(loaded, 0)
    monkeypatch.setattr(generation, "_clock_minutes_laid", lambda column, facts, floor, layout, holes=(): layout)
    before, _path_before = _twin(loaded, 0)
    for name in _BATTERY:
        same = now[name] == before[name]
        assert same == (not _block(document, name)["minute_census"]), name


def test_the_heap_ranks_are_windowed_by_their_group(monkeypatch: pytest.MonkeyPatch) -> None:
    """G12.10b, widened: on a body laid on its minute census a heap's ranks
    move inside its group, so the checker windows them by the group, as the
    construction lays them. MUTATION: the checker's windows drawn as G7A.4b
    lays a body -- a heap's ranks on its value -- and the 12-hour column's
    p75, which its minute census moved off the heap's ranks, is MISSED."""
    columns = {name: shapes.cells(name, 1000) for name in ("ampm", "clinic")}
    _document_now, path, _table = _document(columns)
    loaded = contract.load_profile(str(path))
    _cells, twin_path = _twin(loaded, 0)
    assert _missed(loaded, twin_path) == []
    built = calendar_clock.clock_rank_windows

    def as_before(parsed, tails, body, groups, heaps, form, stride, absent=(), minutes=False):  # type: ignore[no-untyped-def]
        return built(parsed, tails, body, groups, heaps, form, stride, absent, False)

    monkeypatch.setattr(validation.calendar_clock, "clock_rank_windows", as_before)
    assert "ampm:clock-ladder.p75" in _missed(loaded, twin_path)


def test_one_cell_moved_off_its_minute_is_missed(monkeypatch: pytest.MonkeyPatch) -> None:
    """V5-C2, widened: a good twin with one cell of minute 0 moved to minute 7
    of its hour is MISSED, and the line names no count below the line.
    MUTATION: the check always held."""
    columns = {"walkin": shapes.cells("walkin", 1000)}
    _document_now, path, _table = _document(columns)
    loaded = contract.load_profile(str(path))
    twin, _twin_path = _twin(loaded, 0)
    cells = list(twin["walkin"])
    for index in range(len(cells)):
        second = _second(cells[index])
        if second is not None and (second // 60) % 60 == 0 and 9 * 3600 <= second < 17 * 3600:
            cells[index] = cells[index][:3] + "07"
            break
    moved = fixtures.write(_folder(), "moved.csv", "walkin\n" + "\n".join(cells) + "\n")
    found = [check for check in _checks(loaded, moved) if check.subcheck == "minute_census.groups"]
    assert [check.verdict for check in found] == [validation.MISSED]
    line = parsing.census_floor(11)
    for text in found[0].note:
        for number in [int(word) for word in text.replace(":", " ").replace(",", " ").split() if word.isdigit()]:
            assert number == 0 or number >= line or number > 59, text
    monkeypatch.setattr(validation, "_clock_minute_checks", lambda *_arguments: [])
    assert [check for check in _checks(loaded, moved) if check.subcheck == "minute_census.groups"] == []


def test_a_lane_keeps_off_the_places_the_table_calls_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    """A lane's steps leave out the places the table calls absent (G7A.4c step
    2): walk-ins on a ten-minute grid beside `12:00` declared missing -- the
    grid's own `12:00` rows written for an unknown time -- publish their
    minute census, and every twin writes `12:00` on the table's 15 rows
    alone. MUTATION: the absent places left in the lanes -- the twin writes
    present times on `12:00`, cells the table counts as no value."""
    cells = shapes.cells("walkin", 1000)
    document, path, _table = _document({"t": cells}, declared=("12:00",))
    block = _block(document, "t")
    assert block["minute_census"] and block["missing_by_source"] == {"12:00": 15}, block["missing_by_source"]
    loaded = contract.load_profile(str(path))
    for seed in (0, 1):
        twin, twin_path = _twin(loaded, seed)
        assert twin["t"].count("12:00") == 15 and _missed(loaded, twin_path) == [], seed
    monkeypatch.setattr(calendar_clock, "absent_places", lambda spellings, form: ())
    twin, _twin_path = _twin(loaded, 0)
    assert twin["t"].count("12:00") > 15


def test_a_group_on_absent_places_alone_is_laid_on_those_the_other_width_spells() -> None:
    """A census group whose every step is an absent place stands its cells on
    those the hour's other width spells another way, in that width -- on a
    body laid on its minute census too (G7A.4c step 2's lanes on absent
    places). Twenty `1:15` beside `01:15` declared missing, the only step of
    its group on a quarter-hour grid (the place made no heap, as landing
    3b.5's first step read it), the minute census published by hand from the
    table's own minutes: every twin writes the twenty `1:15` and misses
    nothing."""
    cells: "list[str]" = []
    for at in range(0, 1440, 15):
        cells += (["1:15"] if at == 75 else [f"{at // 60:02d}:{at % 60:02d}"]) * 20
    cells += ["01:15"] * 15
    for _row in range(200):
        cells += ["09:15"]
    random.Random(11).shuffle(cells)
    built = calendar_clock.clock_census_of
    calendar_clock_census_of = calendar_clock.clock_census_of
    try:
        calendar_clock.clock_census_of = lambda ordinals, form, line, body, absent=(): built(ordinals, form, line, body)  # type: ignore[assignment]
        document, _path, _table = _document({"t": cells}, declared=("01:15",))
    finally:
        calendar_clock.clock_census_of = calendar_clock_census_of  # type: ignore[assignment]
    block = _block(document, "t")
    assert {"count": 20, "first": 7, "last": 7} in block["clock_census"], block["clock_census"]
    low, high = block["low_tail"], block["high_tail"]
    body = [
        second
        for second in (_second(cell) for cell in cells if cell != "01:15")
        if second is not None and _second(low["boundary"]) <= second <= _second(high["boundary"])  # type: ignore[operator]
    ]
    by_minute = collections.Counter((second // 60) % 60 for second in body)
    groups: "list[dict[str, int]]" = []
    start = 0
    for minute in (0, 15, 30, 45):
        if minute > start:
            groups += [{"first": start, "last": minute - 1, "count": 0}]
        groups += [{"first": minute, "last": minute, "count": by_minute[minute]}]
        start = minute + 1
    groups += [{"first": 46, "last": 59, "count": 0}]
    block["minute_census"] = groups
    path = fixtures.write_profile(_folder(), "by-hand.json", document)
    loaded = contract.load_profile(str(path))
    for seed in (0, 1):
        twin, twin_path = _twin(loaded, seed)
        assert (twin["t"].count("1:15"), twin["t"].count("01:15")) == (20, 15), seed
        assert _missed(loaded, twin_path) == []


# -- growth -------------------------------------------------------------------


def _lines_run(function: "object", *arguments: object) -> int:
    """How many lines `function` and everything it calls ran: a growth measure
    with no clock (`tests/test_stage3b_minutes.py`'s)."""
    code = function.__code__  # type: ignore[attr-defined]
    ran = [0]
    inside = [False]

    def below(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        return below

    def top(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        elif event == "return":
            inside[0] = False
        return top

    def calls(frame: object, event: str, argument: object) -> object:
        if event != "call":
            return None
        if frame.f_code is code and not inside[0]:  # type: ignore[attr-defined]
            inside[0] = True
            return top
        return below if inside[0] else None

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return ran[0]


def _laid(rows: int) -> "tuple[contract.ColumnBlock, generation._ClockLayout]":
    columns = {"walkin": shapes.cells("walkin", rows)}
    _document_now, path, _table = _document(columns)
    loaded = contract.load_profile(str(path))
    column = loaded.columns[0]
    layout = generation._clock_layout(column, column.facts, 11, ())  # type: ignore[arg-type]
    assert layout.census is not None and layout.census.minutes is not None
    return column, layout


def test_placing_grows_with_the_rows_and_the_table_with_the_groups() -> None:
    """At 10,000 and 100,000 rows: laying the body (G7A.4c step 4) runs no more
    than 1.25 times ten times the lines, and building the plan (steps 1 to 3)
    no more than 1.25 times as many -- its work is the groups', not the
    rows'. Machine-free, so a million rows cost ten times 100,000's."""
    placing: "list[int]" = []
    planning: "list[int]" = []
    for rows in (10000, 100000):
        column, layout = _laid(rows)
        census = layout.census
        assert census is not None and census.minutes is not None
        words = [(7919 * rank) % (1 << 64) for rank in range(layout.parsed)]
        ordinals = [0 for _rank in range(layout.parsed)]
        placing += [
            _lines_run(
                generation._clock_minute_body, census.minutes, census.stride, column.facts.clock_form,  # type: ignore[union-attr]
                layout.apart, words, ordinals,
            )
        ]
        tails, body = generation._clock_minute_body_ends(column.facts, layout, census.stride)  # type: ignore[arg-type]
        planning += [
            _lines_run(
                generation._clock_minute_plan, column, column.facts, layout, census, (), tails, body,
            )
        ]
    assert placing[1] <= 1.25 * 10 * placing[0], placing
    assert planning[1] <= 1.25 * planning[0] + 20000, planning


def test_a_lane_is_read_by_its_hours_and_indexes_not_its_steps() -> None:
    """A lane of seconds over twenty hours, 72,000 steps: asking it 10 indexes
    and 1,000 runs lines that grow with the indexes and the hours alone."""
    spent: "list[int]" = []
    for asked in (10, 1000):
        wanted = [(index * 3600) // asked * 2 for index in range(asked)]
        spent += [
            _lines_run(
                calendar_clock.minute_lane_points, 3600, 75599, 1, parsing.CLOCK_HH_MM_SS, 0, 59,
                [7200, 7201], wanted,
            )
        ]
    assert spent[1] <= 1.25 * 100 * spent[0] and spent[0] < 2000, spent


# -- route 1's rare words, kept present ----------------------------------------


def _capsweep(share: float, rows: int, floor: int) -> "list[str]":
    """The route-2 correction's capsweep table (plans P4-D390 and P4-D373):
    appointment slots beside one-off notes, at a share."""
    draw = random.Random(int(share * 10000) + rows + floor)
    cells: "list[str]" = []
    written = 0
    for _row in range(rows):
        pick = draw.random()
        if pick < 0.80:
            hour = draw.choices(range(7, 17), weights=(3, 9, 10, 10, 8, 4, 8, 9, 8, 5))[0]
            minute = hour * 60 + 15 * draw.randrange(4)
        elif pick < 0.92:
            minute = 390 + draw.randrange(750)
        else:
            minute = 17 * 60 + 30 * draw.randrange(6)
        if draw.random() < share:
            written = written + 1
            cells += [f"see note {written}"]
        else:
            cells += [f"{minute // 60:02d}:{minute % 60:02d}"]
    return cells


@pytest.mark.parametrize("share,rows,notes", ((0.025, 1000, 17), (0.022, 10000, 181)))
def test_rare_notes_beside_clock_times_are_written_not_blanked(share: float, rows: int, notes: int) -> None:
    """The two of the 112 tables route 1 reached: clock times whose notes stay
    present, unread by the clock, and every twin writes a word in each --
    where counted missing, 17 and 181 cells, its twins wrote that many blanks
    the source never left (the route-2 correction's ruling, 2026-10-08)."""
    cells = _capsweep(share, rows, 36)
    document, path, table = _document({"c": cells}, floor=36)
    block = document["columns"][0]
    assert (block["role"], block["n_missing"], block["n_unparsed"]) == (taxonomy.ROLE_CLOCK, 0, notes)
    loaded = contract.load_profile(str(path))
    assert _missed(loaded, table) == []
    twin, twin_path = _twin(loaded, 0)
    assert "" not in twin["c"] and _missed(loaded, twin_path) == []
    assert sum(1 for cell in twin["c"] if _second(cell) is None) == notes


def test_red_when_the_clock_line_is_asked_with_the_rare_words(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the clock line asked over every present cell, the rare words
    too -- the column misses the line and is labels."""
    built = taxonomy._clock_reading
    monkeypatch.setattr(
        taxonomy, "_clock_reading", lambda cells: built(dataclasses.replace(cells, clock_line_exempt=0))
    )
    cells = _capsweep(0.025, 1000, 36)
    document, _path, _table = _document({"c": cells}, floor=36)
    assert document["columns"][0]["role"] != taxonomy.ROLE_CLOCK

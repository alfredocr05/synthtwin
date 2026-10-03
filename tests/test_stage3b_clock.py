"""THE CLOCK'S GATE (stage 3b landing 3b.5, lane C1, plan P4-D373): clock-only columns keep their time of day.

Before this landing a column of clock times holding few enough different
values was a set of LABELS: its rare times were written blank by the
level pass, or as made-up text of the clock's shape no clock reader takes
(`36:54`, `57:95`), so code reading the times ran on the table and raised
on its twin. A column read as clock times spread its body linearly
between its rungs: the hour of day came back 0.18 to 0.33 off at 1,000
rows (total variation over the 24 hours), every heap smaller than a rung
gap was lost -- handover's 07:00 and 19:00 came back halved -- and a
column with no tails was a ramp from 00:00. One clause per rule, and every
clause red on its own mutant but the floor and checker half of F, which
holds the whole battery, and NF106's sentence:

* R `test_r_every_column_is_a_clock_and_every_twin_cell_a_time` -- the
  battery's clock columns are read as clock times at 100, 300 and 1,000
  rows (floors 11 and 36), and no twin holds a cell no clock reader takes
  or a blank the real column does not, beyond the rare words the level
  pass counts missing (mutant: rule 8 asked after rule 7 again); and,
  since the repair round, appointment times beside clock-shaped codes
  near the clock line and small tables beside a few past it keep their
  reading: as clock times, their twins refusing no cell the table does
  not, or as labels, refusing fewer than a held-back level's more;
* F `test_f_no_count_below_the_line_and_nothing_missed` -- every printed
  count is nought or at least the census line, the loader accepts every
  description (CC1 to CC5, CH1 and CH2), and every twin and every real
  table validates with nothing missed (V5-C1 and V5-C2 among the checks);
  so do the repair round's code mixes at 300 to 3,000 rows and its small
  tables, whose twins read back as labels where the tables are labels
  (mutant: G8.3's clock line withdrawn, and the role is MISSED);
* H `test_h_the_hour_comes_back` -- at 1,000 rows every column's hour of
  day is within 0.03 of the real one, and at every size within the bound
  of the cells the census cannot place in their hour: the cells of groups
  spanning two hours and the tail cells on no heap and among no listed
  values of one hour (mutant: the census withdrawn from the layout);
* P `test_p_every_heap_comes_back_exactly` -- each published heap's
  count, and the top value's where it is one, at every size and seed
  (mutant: no heap published);
* S `test_s_the_heaps_are_the_values_that_stand_out` -- the heaps are
  exactly the steps standing out from the five either side by the median
  rule, on the step (mutant: the mean in place of the median);
* N `test_n_the_census_nests_in_the_hours` -- the hours merged first
  coarsen the published groups (mutant: one flat merge of the bins); and
  a column with no tails publishes its census over every parsed cell,
  its twin's other cells staying in the table's stretch of the day
  (BLOCKER (a); mutant: the census of such a column withdrawn);
* B `test_b_a_boundary_below_a_heap_takes_its_cell_first` -- the 3b.5
  skeptic's MAJOR 1: a low boundary two steps below a heap comes back on
  its value at five seeds (mutant: steps alone share a group);
* C `test_c_codes_are_written_back` -- a code at least the line's rows
  wrote is published and written back exactly (mutant: no code
  published);
* T `test_t_the_step_is_kept` -- a five-minute grid publishes a step of
  300 seconds and its twin stays on it (mutant: the step of the form);
* V `test_v_one_cell_moved_is_missed` -- the checker's own three new
  checks each MISS a good twin with one cell moved: a heap's cell moved
  off its value, a code's cell rewritten, a grid's cell moved off its
  step (mutant, one each: that check always held);
* L `test_l_each_rung_its_run_holds_is_met` -- the 3b.5 skeptic's
  MINOR 2: every published rung whose rank lies in a run holding its
  value on the step is met exactly at its rank, 108 rungs over the
  battery's twins at 1,000 rows and the floor of eleven (mutant: the
  rungs left unpinned, and 72 of them move);
* M `test_m_a_clock_shaped_stand_in_is_a_time` -- three clock columns
  beside 2 % words, two-figure and one-figure hours and Excel's `h:mm AM`,
  read as labels, write their held-back levels as times (mutants: the
  form filled figure by figure; the key of a clock with a space before
  its marker withdrawn);
* W `test_w_rare_words_beside_clock_times_keep_the_clock` -- 296 shift
  starts beside four `UNK` are clock times, the words counted missing,
  and the twin reads back the same way (mutant: the level pass keeps the
  labels);
* Q `test_q_a_few_shared_times_are_asked_about` -- where a set of labels
  could hold the column too and the times many rows share hold every
  cell of its body, the questions file asks, and the answer `code` reads
  it as labels; where a census is published, nobody is asked (mutants:
  no question; the question asked beside a census);
* G `test_g_the_guard_holds_each_clock_leaf_to_its_kind` -- the
  publication guard refuses a clock census bin, group count, heap count,
  heap value and step each of the wrong kind (mutant, one each: that
  kind always published);
* and NF106, `test_the_description_says_so_where_the_census_is_left_out`
  -- fewer than the line left beside the heaps leaves the census out
  and the description says so, the fold-back the 3b.5 skeptic dropped.
"""

from __future__ import annotations

import collections
import copy
import csv
import dataclasses
import functools
import io
import pathlib
import random
import re
import tempfile
import typing

import pytest

import clock_census_shapes as shapes
import fixtures

from synthtwin import asking
from synthtwin import calendar_clock
from synthtwin import calendar_rules
from synthtwin import contract
from synthtwin import errors
from synthtwin import generation
from synthtwin import parsing
from synthtwin import profile
from synthtwin import reading
from synthtwin import rendering
from synthtwin import taxonomy
from synthtwin import validation

_CLOCKS = shapes.CLOCKS

# The one folder this module's tables and twins are written under, pytest's
# own, set for the module and emptied of the cached runs after it.
_HOME: "list[pathlib.Path]" = []


@pytest.fixture(scope="module", autouse=True)
def _home(tmp_path_factory: pytest.TempPathFactory) -> "typing.Iterator[None]":
    _HOME[:] = [tmp_path_factory.mktemp("clock-gate")]
    yield
    _described.cache_clear()
    _twin.cache_clear()


@functools.lru_cache(maxsize=None)
def _described(names: "tuple[str, ...]", rows: int, floor: int, codes: "tuple[str, ...]" = ()):
    """The battery table's description, loaded, and where it lies."""
    folder = pathlib.Path(tempfile.mkdtemp(dir=_HOME[0]))
    columns = {name: shapes.cells(name, rows) for name in names}
    count = len(next(iter(columns.values())))
    lines = [",".join(names)] + [
        ",".join(columns[name][index] for name in names) for index in range(count)
    ]
    table = fixtures.write(folder, "clocks.csv", "\n".join(lines) + "\n")
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        [],
        list(codes),
    )
    written = fixtures.write_profile(folder, "clocks.json", document)
    return folder, columns, document, contract.load_profile(str(written)), table


@functools.lru_cache(maxsize=None)
def _twin(names: "tuple[str, ...]", rows: int, floor: int, seed: int, codes: "tuple[str, ...]" = ()):
    """One twin: its cells by column, and what validation MISSED on it."""
    folder, _columns, _document, loaded, _table = _described(names, rows, floor, codes)
    text = rendering.twin_csv(generation.generate(loaded, seed))
    target = fixtures.write(folder, f"twin-{seed}.csv", text)
    body = list(csv.reader(io.StringIO(text)))
    cells = {name: [row[place] for row in body[1:] if row] for place, name in enumerate(body[0])}
    return cells, _missed(loaded, target)


def _missed(loaded: contract.Profile, path: pathlib.Path) -> "list[str]":
    outcome = validation.measure(loaded, str(path))
    return sorted(
        f"{check.column}:{check.subcheck}"
        for check in outcome.checks
        if check.verdict == validation.MISSED
    )


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    for block in document["columns"]:  # type: ignore[union-attr]
        if block["name"] == name:
            return block
    raise AssertionError(name)


def _second(text: str) -> "int | None":
    parts = parsing.clock_parts(text)
    if parts is None:
        return None
    return parsing.clock_second(parts, parts[5])


def _hours(cells: "list[str]") -> "collections.Counter[int]":
    return collections.Counter(
        second // 3600 for second in (_second(cell) for cell in cells) if second is not None
    )


def _tvd(real: "list[str]", twin: "list[str]") -> float:
    first, second = _hours(real), _hours(twin)
    a, b = max(1, sum(first.values())), max(1, sum(second.values()))
    return 0.5 * sum(abs(first[hour] / a - second[hour] / b) for hour in range(24))


_SIZES = ((100, 11), (300, 11), (1000, 11), (1000, 36))
_SEEDS = (0, 4)


# -- R: every column a clock, every twin cell a time --------------------


def _unreadable(real: "list[str]", twin: "list[str]") -> int:
    """Twin cells no clock reader takes, blanks among them, beyond the real column's.

    A rare word the level pass counts missing comes back blank, as the
    owner's ruling of 2026-09-17 (item 5) has every such label do, so a
    blank stands for a real cell no clock reader took; a rare TIME counted
    missing and written blank is the defect this clause is for.
    """
    def counted(cells: "list[str]") -> int:
        return sum(1 for cell in cells if cell == "" or _second(cell) is None)

    return max(0, counted(twin) - counted(real))


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_r_every_column_is_a_clock_and_every_twin_cell_a_time(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CLOCKS, rows, floor)
    for name in _CLOCKS:
        assert _block(document, name)["role"] == taxonomy.ROLE_CLOCK, (rows, floor, name)
    for seed in _SEEDS:
        cells, _missed_now = _twin(_CLOCKS, rows, floor, seed)
        for name in _CLOCKS:
            assert _unreadable(columns[name], cells[name]) == 0, (rows, floor, seed, name)


def test_r_red_when_rule_8_is_asked_after_rule_7(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_clock_spellings_reach", lambda _cells: False)
    _described.cache_clear()
    _twin.cache_clear()
    try:
        _folder, columns, document, _loaded, _table = _described(("clinic", "shift_start"), 1000, 11)
        assert _block(document, "clinic")["role"] != taxonomy.ROLE_CLOCK
        cells, _missed_now = _twin(("clinic", "shift_start"), 1000, 11, 0)
        bad = sum(_unreadable(columns[name], cells[name]) for name in ("clinic", "shift_start"))
        assert bad > 0
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# THE REPAIR ROUND'S SHAPES (the 3b.5 skeptic's item 1): appointment times
# beside clock-shaped codes near the clock line, five mixes as the columns
# of one table, and small tables beside a few such codes past it, three
# variants of each as the columns of one.
_CODED = tuple(shapes.CODE_MIXES)
_CODED_SIZES = ((300, 11), (300, 36), (1000, 11), (1000, 36), (3000, 11), (3000, 36))
_SMALL = tuple(sorted(shapes.SMALL_TABLES))


def _small(spec: str) -> "tuple[tuple[str, ...], int]":
    """A small table's three variants, as one table's columns, and its rows."""
    return tuple(f"{spec}{variant}" for variant in (1, 2, 3)), shapes.SMALL_TABLES[spec][0]


def _refused(cells: "list[str]") -> int:
    """How many cells hold text no clock reader takes; a blank is no text."""
    return sum(1 for cell in cells if cell and _second(cell) is None)


def _kept_reading(document: "dict[str, object]", columns: "dict[str, list[str]]", twin: "dict[str, list[str]]", floor: int) -> "list[str]":
    """The columns whose twin does not keep the reading the table has.

    Read as clock times, the twin refuses no cell the table does not,
    blanks among them. Read as labels, it holds fewer more cells of text
    no clock reader takes than one held-back level covers -- the slack of
    G8.3's clock line, whose stand-ins are written figure by figure from
    the first that would cross it. The blanks of a column of labels are
    the level pass's (the owner's ruling of 2026-09-17, item 5), which the
    description publishes, and are not asked about here.
    """
    broken: "list[str]" = []
    for name in columns:
        if _block(document, name)["role"] == taxonomy.ROLE_CLOCK:
            if _unreadable(columns[name], twin[name]) != 0:
                broken += [name]
        elif _refused(twin[name]) - _refused(columns[name]) >= floor:
            broken += [name]
    return broken


@pytest.mark.parametrize("rows,floor", _CODED_SIZES)
def test_r_times_beside_codes_keep_their_reading(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CODED, rows, floor)
    cells, _missed_now = _twin(_CODED, rows, floor, 0)
    assert _kept_reading(document, columns, cells, floor) == [], (rows, floor)


@pytest.mark.parametrize("spec", _SMALL)
@pytest.mark.parametrize("floor", (11, 36))
def test_r_small_tables_beside_codes_keep_their_reading(spec: str, floor: int) -> None:
    names, rows = _small(spec)
    _folder, columns, document, _loaded, _table = _described(names, rows, floor)
    cells, _missed_now = _twin(names, rows, floor, 0)
    assert _kept_reading(document, columns, cells, floor) == [], (spec, floor)


# -- F: the floor, the loader, and nothing missed ---------------------


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_f_no_count_below_the_line_and_nothing_missed(rows: int, floor: int) -> None:
    folder, _columns, document, loaded, table = _described(_CLOCKS, rows, floor)
    line = parsing.census_floor(floor)
    for name in _CLOCKS:
        block = _block(document, name)
        for group in block["clock_census"]:  # type: ignore[union-attr]
            assert group["count"] == 0 or group["count"] >= line, (name, group)
        for entry in list(block["clock_heaps"]) + list(block["clock_codes"]):  # type: ignore[arg-type]
            assert entry["count"] >= line, (name, entry)
    assert _missed(loaded, table) == []
    for seed in _SEEDS:
        _cells_now, missed = _twin(_CLOCKS, rows, floor, seed)
        assert missed == [], (rows, floor, seed, missed)


@pytest.mark.parametrize("rows,floor", _CODED_SIZES)
def test_f_times_beside_codes_validate(rows: int, floor: int) -> None:
    _folder, _columns, _document, loaded, table = _described(_CODED, rows, floor)
    assert _missed(loaded, table) == []
    _cells_now, missed = _twin(_CODED, rows, floor, 0)
    assert missed == [], (rows, floor, missed)


@pytest.mark.parametrize("spec", _SMALL)
@pytest.mark.parametrize("floor", (11, 36))
def test_f_small_tables_beside_codes_validate(spec: str, floor: int) -> None:
    """The 3b.5 skeptic's small tables: labels on the table, labels on the twin."""
    names, rows = _small(spec)
    _folder, _columns, document, loaded, table = _described(names, rows, floor)
    assert all(_block(document, name)["role"] != taxonomy.ROLE_CLOCK for name in names)
    assert _missed(loaded, table) == []
    _cells_now, missed = _twin(names, rows, floor, 0)
    assert missed == [], (spec, floor, missed)


# THE CLOCK LINE IS THE PRODUCER'S OWN (method G8.3, the repair round): the
# room is the most cells of a column of labels a clock reader may take
# before the producer reads it as clock times -- exactly that many beside
# rare words and one published word are labels, one more is clock times.
# Each case is a number of present cells and the cells of `UNK`, published
# where they reach the floor.
_LINE_CASES = ((250, 0), (1000, 0), (3000, 11), (3000, 30))


def _read_with(present: int, words: int, timed: int) -> str:
    """The role of a column of ``timed`` quarter hours, ``words`` `UNK` and rare words."""
    draw = random.Random(7 * present + words)
    column = [
        parsing.clock_spelling(15 * draw.randrange(32, 72), parsing.CLOCK_HH_MM) for _ in range(timed)
    ]
    column += ["UNK"] * words + [f"w{index}" for index in range(present - timed - words)]
    draw.shuffle(column)
    folder = pathlib.Path(tempfile.mkdtemp(dir=_HOME[0]))
    table = fixtures.write(folder, "line.csv", "c\n" + "\n".join(column) + "\n")
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=11), taxonomy.Settings(small_cell_floor=11), []
    )
    return f"{document['columns'][0]['role']}"  # type: ignore[index]


def _line_holds(present: int, words: int) -> bool:
    room = generation._clock_line_room(present, taxonomy.Settings().minimum_parse_rate, 0, words, True)
    if _read_with(present, words, room) == taxonomy.ROLE_CLOCK:
        return False
    return room == present - words or _read_with(present, words, room + 1) == taxonomy.ROLE_CLOCK


@pytest.mark.parametrize("present,words", _LINE_CASES)
def test_f_the_clock_line_is_the_producers_own(present: int, words: int) -> None:
    assert _line_holds(present, words)


def test_f_red_on_the_clock_line_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    """The skeptic's line alone, without the rare words: a twin the producer reads as clock times."""
    monkeypatch.setattr(
        generation,
        "_clock_cells_stand",
        lambda present, rate, clocks, _others, _stand_ins, taken: clocks + taken < taxonomy.clock_line(rate, present),
    )
    assert not all(_line_holds(present, words) for present, words in _LINE_CASES)


def test_f_red_without_the_clock_line(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        generation, "_clock_line_room", lambda present, _rate, _clocks, _others, _settled: present
    )
    _twin.cache_clear()
    try:
        names, rows = _small("small_f")
        _cells_now, missed = _twin(names, rows, 11, 0)
        assert any(entry.endswith(":axes.role") for entry in missed), missed
    finally:
        _twin.cache_clear()


# -- H: the hour of day -----------------------------------------------


def _unplaced(block: "dict[str, object]", parsed: int) -> int:
    """The cells the published census and heaps cannot place in their hour."""
    form = f"{block['clock_form']}"
    heaps = {
        parsing.clock_ordinal(f"{heap['value']}", form): int(heap["count"])
        for heap in block["clock_heaps"]  # type: ignore[union-attr]
    }
    unit = parsing.clock_step(form)
    loose = 0
    body = parsed
    ends = [0, parsing.CLOCK_CAPACITY[form] - 1]
    for key in ("low_tail", "high_tail"):
        tail = block[key]
        if not isinstance(tail, dict):
            continue
        at = parsing.clock_ordinal(f"{tail['boundary']}", form)
        assert at is not None
        ends[0 if key == "low_tail" else 1] = at
        held = sum(
            count for value, count in heaps.items()
            if value is not None and (value < at if key == "low_tail" else value > at)
        )
        rows = int(tail["rows"])
        body = body - rows
        listed = tail["values"]
        if listed is not None and len(
            {(parsing.clock_ordinal(f"{value}", form) or 0) * unit // 3600 for value in listed}
        ) == 1:
            continue
        loose = loose + rows - held
    census = block["clock_census"]
    if not census:
        # ...and with no census, the body's cells on no heap anywhere in it.
        inside = sum(
            count for value, count in heaps.items()
            if value is not None and ends[0] <= value <= ends[1]
        )
        return loose + max(0, body - inside)
    for group in census:  # type: ignore[union-attr]
        if group["first"] // calendar_clock.BINS_PER_HOUR != group["last"] // calendar_clock.BINS_PER_HOUR:
            loose = loose + int(group["count"])
    return loose


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_h_the_hour_comes_back(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CLOCKS, rows, floor)
    for seed in _SEEDS:
        cells, _missed_now = _twin(_CLOCKS, rows, floor, seed)
        for name in _CLOCKS:
            block = _block(document, name)
            parsed = int(block["n_present"]) - int(block["n_unparsed"])  # type: ignore[arg-type]
            found = _tvd(columns[name], cells[name])
            assert found <= _unplaced(block, parsed) / parsed + 1e-9, (rows, floor, seed, name, found)
            if rows == 1000 and floor == 11:
                assert found <= 0.03, (seed, name, found)


def test_h_red_without_the_census(monkeypatch: pytest.MonkeyPatch) -> None:
    built = calendar_clock.clock_body_blocks

    def withdrawn(parsed, tails, body, groups, heaps, form, stride):  # type: ignore[no-untyped-def]
        return built(parsed, tails, body, (), heaps, form, stride)

    monkeypatch.setattr(calendar_clock, "clock_body_blocks", withdrawn)
    _folder, columns, _document, loaded, _table = _described(_CLOCKS, 1000, 11)
    body = list(csv.reader(io.StringIO(rendering.twin_csv(generation.generate(loaded, 0)))))
    worst = 0.0
    for name in ("handover", "night_obs", "med_round"):
        place = body[0].index(name)
        worst = max(worst, _tvd(columns[name], [row[place] for row in body[1:] if row]))
    assert worst > 0.03


# -- P and S: the heaps --------------------------------------------------


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_p_every_heap_comes_back_exactly(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CLOCKS, rows, floor)
    for seed in _SEEDS:
        cells, _missed_now = _twin(_CLOCKS, rows, floor, seed)
        for name in _CLOCKS:
            block = _block(document, name)
            twin = collections.Counter(cells[name])
            real = collections.Counter(columns[name])
            for heap in block["clock_heaps"]:  # type: ignore[union-attr]
                assert twin[heap["value"]] == heap["count"] == real[heap["value"]], (name, heap)
            top, count = real.most_common(1)[0]
            if any(heap["value"] == top for heap in block["clock_heaps"]):  # type: ignore[union-attr]
                assert twin[top] == count, (name, top)


def test_p_red_without_the_heaps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(calendar_clock, "heaps_on_the_step", lambda *_a: ())
    _described.cache_clear()
    _twin.cache_clear()
    try:
        _folder, columns, _document, _loaded, _table = _described(("clinic", "handover"), 1000, 11)
        cells, _missed_now = _twin(("clinic", "handover"), 1000, 11, 0)
        real = collections.Counter(columns["handover"])
        twin = collections.Counter(cells["handover"])
        assert twin["07:00"] != real["07:00"] or twin["19:00"] != real["19:00"]
    finally:
        _described.cache_clear()
        _twin.cache_clear()


def _standing(cells: "list[str]", form: str, step: int, line: int) -> "list[tuple[str, int]]":
    unit = parsing.clock_step(form)
    stride = step // unit
    size = calendar_clock.clock_day(form) // step
    counts = [0 for _ in range(size)]
    for cell in cells:
        found = parsing.clock_ordinal(cell, form)
        if found is not None:
            counts[found // stride] = counts[found // stride] + 1
    found_out = calendar_rules.standing_out(counts, line, 5, calendar_rules.CENTRE_MEDIAN)
    return [(parsing.clock_spelling(index * stride, form), count) for index, count in found_out]


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_s_the_heaps_are_the_values_that_stand_out(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CLOCKS, rows, floor)
    line = parsing.census_floor(floor)
    for name in _CLOCKS:
        block = _block(document, name)
        published = [(f"{heap['value']}", int(heap["count"])) for heap in block["clock_heaps"]]  # type: ignore[union-attr]
        assert published == _standing(
            columns[name], f"{block['clock_form']}", int(block["clock_step"]), line  # type: ignore[arg-type]
        ), name


def test_s_red_on_the_mean(monkeypatch: pytest.MonkeyPatch) -> None:
    def on_the_mean(counts, units, line):  # type: ignore[no-untyped-def]
        dense = [counts[index] if index in counts else 0 for index in range(units)]
        return calendar_rules.standing_out(dense, line, 5, calendar_rules.CENTRE_MEAN)

    monkeypatch.setattr(calendar_clock, "heaps_on_the_step", on_the_mean)
    _described.cache_clear()
    try:
        _folder, columns, document, _loaded, _table = _described(("handover",), 1000, 11)
        block = _block(document, "handover")
        published = [(f"{heap['value']}", int(heap["count"])) for heap in block["clock_heaps"]]  # type: ignore[union-attr]
        assert published != _standing(columns["handover"], "hh-mm", 60, 11)
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# -- N: the census nests in the hours -----------------------------------


def _nested(block: "dict[str, object]", cells: "list[str]", line: int) -> bool:
    form = f"{block['clock_form']}"
    heaps = {f"{heap['value']}" for heap in block["clock_heaps"]}  # type: ignore[union-attr]
    low, high = 0, parsing.CLOCK_CAPACITY[form] - 1
    if isinstance(block["low_tail"], dict) and isinstance(block["high_tail"], dict):
        low = parsing.clock_ordinal(f"{block['low_tail']['boundary']}", form) or 0
        high = parsing.clock_ordinal(f"{block['high_tail']['boundary']}", form) or 0
    hours = [0 for _ in range(calendar_clock.clock_bin_count(form) // calendar_clock.BINS_PER_HOUR)]
    for cell in cells:
        found = parsing.clock_ordinal(cell, form)
        if found is None or cell in heaps or not low <= found <= high:
            continue
        hour = calendar_clock.clock_bin_of(found, form) // calendar_clock.BINS_PER_HOUR
        hours[hour] = hours[hour] + 1
    top = calendar_rules.merged_groups(hours, [], line) or ((0, len(hours) - 1, sum(hours)),)
    for group in block["clock_census"]:  # type: ignore[union-attr]
        # A group counting nothing places no cell, and two side by side
        # are one whichever hour groups they lie in.
        if group["count"] == 0:
            continue
        first = group["first"] // calendar_clock.BINS_PER_HOUR
        last = group["last"] // calendar_clock.BINS_PER_HOUR
        if not any(start <= first and last <= stop for start, stop, _count in top):
            return False
    return True


@pytest.mark.parametrize("rows,floor", _SIZES)
def test_n_the_census_nests_in_the_hours(rows: int, floor: int) -> None:
    _folder, columns, document, _loaded, _table = _described(_CLOCKS, rows, floor)
    line = parsing.census_floor(floor)
    for name in _CLOCKS:
        assert _nested(_block(document, name), columns[name], line), (rows, floor, name)


def test_n_red_on_a_flat_merge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        calendar_clock,
        "nested_groups",
        lambda bins, line: calendar_rules.merged_groups(bins, [], line) or ((0, len(bins) - 1, sum(bins)),),
    )
    _described.cache_clear()
    try:
        _folder, columns, document, _loaded, _table = _described(_CLOCKS, 1000, 11)
        assert not all(_nested(_block(document, name), columns[name], 11) for name in _CLOCKS)
    finally:
        _described.cache_clear()
        _twin.cache_clear()


def _no_tails_kept(rows: int) -> bool:
    """Whether `dominant`, which has no tails, publishes a census and keeps its stretch.

    Its eighteen cells off the heap at 08:00 lie between 06:00 and 17:59;
    the census over every parsed cell holds the twin's there too.
    """
    _folder, _columns, document, _loaded, _table = _described(("dominant",), rows, 11)
    block = _block(document, "dominant")
    if block["low_tail"] is not None or not block["clock_census"]:
        return False
    heaps = {f"{heap['value']}" for heap in block["clock_heaps"]}  # type: ignore[union-attr]
    for seed in _SEEDS:
        cells, missed = _twin(("dominant",), rows, 11, seed)
        others = [_second(cell) for cell in cells["dominant"] if cell not in heaps]
        if missed or not others:
            return False
        if not all(second is not None and 6 * 3600 <= second < 18 * 3600 for second in others):
            return False
    return True


@pytest.mark.parametrize("rows", (300, 1000))
def test_n_a_column_with_no_tails_publishes_its_census(rows: int) -> None:
    assert _no_tails_kept(rows)


def test_n_red_without_the_census_of_a_column_with_no_tails(monkeypatch: pytest.MonkeyPatch) -> None:
    built = calendar_clock.clock_census_of

    def withdrawn(ordinals, form, line, body):  # type: ignore[no-untyped-def]
        found = built(ordinals, form, line, body)
        if body is None:
            return calendar_clock.ClockCensus(found.step, found.heaps, (), bool(found.groups))
        return found

    monkeypatch.setattr(calendar_clock, "clock_census_of", withdrawn)
    _described.cache_clear()
    _twin.cache_clear()
    try:
        assert not _no_tails_kept(300)
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# -- B: the boundary's run takes one cell first --------------------------


def test_b_a_boundary_below_a_heap_takes_its_cell_first() -> None:
    _folder, _columns, document, _loaded, _table = _described(("boundary",), 79, 11)
    block = _block(document, "boundary")
    assert block["low_tail"]["boundary"] == "06:58"  # type: ignore[index]
    assert {"value": "07:00", "count": 25} in block["clock_heaps"]  # type: ignore[operator]
    for seed in range(5):
        cells, missed = _twin(("boundary",), 79, 11, seed)
        assert "06:58" in cells["boundary"] and missed == [], (seed, missed)


def test_b_red_when_steps_alone_share(monkeypatch: pytest.MonkeyPatch) -> None:
    shared = calendar_clock.run_shares
    monkeypatch.setattr(
        calendar_clock, "run_shares", lambda count, units, firsts: shared(count, units, [0 for _ in units])
    )
    _twin.cache_clear()
    try:
        held = [_twin(("boundary",), 79, 11, seed) for seed in range(5)]
        assert any("06:58" not in cells["boundary"] or missed for cells, missed in held)
    finally:
        _twin.cache_clear()


# -- L: each rung pinned in its run --------------------------------------


def _rungs_off(loaded: contract.Profile, name: str, twin: "list[str]") -> "tuple[int, int]":
    """How many published rungs the rank rule pins, and how many the twin misses.

    A published interior rung is pinned where its rank lies in a run -- a
    stretch of a census group between heaps -- holding its value on the
    step (method G7A.4b, step 3): the twin's value at that rank, its
    parsed cells sorted, is then the rung itself. The runs are the
    layout's own (`calendar_clock.clock_body_blocks`, held to the census
    by clause F); what this asks is the pin.
    """
    column = next(block for block in loaded.columns if block.name == name)
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts)
    census = generation._clock_layout(column, facts, loaded.settings.small_cell_floor).census
    if census is None or facts.low_tail is None:
        return 0, 0
    form = facts.clock_form
    ordered = sorted(
        found for found in (parsing.clock_ordinal(cell, form) for cell in twin) if found is not None
    )
    pinned = missed = 0
    for step in range(1, len(generation._PCT) - 1):
        rung = facts.clock_percentiles[generation._LADDER_NAMES[step]]
        if rung is None:
            continue
        rank = generation._rung_rank(generation._PCT[step], len(ordered))
        value = parsing.clock_ordinal(rung, form)
        assert value is not None
        for block in census.blocks:
            if (
                not block.heap
                and block.first_rank <= rank < block.first_rank + block.cells
                and block.low <= value <= block.high
                and (value - block.low) % census.stride == 0
            ):
                pinned = pinned + 1
                missed = missed + (1 if ordered[rank] != value else 0)
    return pinned, missed


@pytest.mark.parametrize("rows,floor", ((1000, 11), (1000, 36)))
def test_l_each_rung_its_run_holds_is_met(rows: int, floor: int) -> None:
    _folder, _columns, _document, loaded, _table = _described(_CLOCKS, rows, floor)
    total = 0
    for seed in _SEEDS:
        cells, _missed_now = _twin(_CLOCKS, rows, floor, seed)
        for name in _CLOCKS:
            pinned, missed = _rungs_off(loaded, name, cells[name])
            total = total + pinned
            assert missed == 0, (rows, floor, seed, name)
    assert total > 0


def test_l_red_without_the_rung_pins(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generation, "_clock_rung_pins", lambda *_a: [])
    _twin.cache_clear()
    try:
        _folder, _columns, _document, loaded, _table = _described(_CLOCKS, 1000, 11)
        cells, _missed_now = _twin(_CLOCKS, 1000, 11, 0)
        assert sum(_rungs_off(loaded, name, cells[name])[1] for name in _CLOCKS) > 0
    finally:
        _twin.cache_clear()


# -- C: codes are written back -------------------------------------------


def test_c_codes_are_written_back() -> None:
    _folder, columns, document, _loaded, _table = _described(("coded",), 2500, 11)
    block = _block(document, "coded")
    real = collections.Counter(columns["coded"])
    assert block["role"] == taxonomy.ROLE_CLOCK
    assert block["clock_codes"] == [{"spelling": "not recorded", "count": real["not recorded"]}]
    # ...and the block says so (NF107), naming the census line.
    said = taxonomy.rendered(taxonomy.REMARK_CLOCK_CODES_WRITTEN, (parsing.census_floor(11),))
    assert said in block["remarks"]  # type: ignore[operator]
    for seed in _SEEDS:
        cells, missed = _twin(("coded",), 2500, 11, seed)
        assert collections.Counter(cells["coded"])["not recorded"] == real["not recorded"]
        assert missed == []


def test_c_red_without_the_codes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(calendar_clock, "codes_of", lambda _unread, _line: [])
    _described.cache_clear()
    _twin.cache_clear()
    try:
        _folder, columns, _document, _loaded, _table = _described(("coded",), 2500, 11)
        cells, _missed_now = _twin(("coded",), 2500, 11, 0)
        assert collections.Counter(cells["coded"])["not recorded"] != collections.Counter(columns["coded"])["not recorded"]
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# -- T: the step ----------------------------------------------------------


def _off_the_grid(cells: "list[str]") -> int:
    return sum(1 for cell in cells if (_second(cell) or 0) % 300)


def test_t_the_step_is_kept() -> None:
    _folder, _columns, document, _loaded, _table = _described(("grid5",), 1000, 11)
    assert _block(document, "grid5")["clock_step"] == 300
    for seed in _SEEDS:
        cells, missed = _twin(("grid5",), 1000, 11, seed)
        assert _off_the_grid(cells["grid5"]) == 0 and missed == []


def test_t_red_on_the_forms_own_step(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(calendar_clock, "written_step", lambda _seconds, _day: 60)
    _described.cache_clear()
    _twin.cache_clear()
    try:
        cells, _missed_now = _twin(("grid5",), 1000, 11, 0)
        assert _off_the_grid(cells["grid5"]) > 0
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# -- V: the checker misses one cell moved ---------------------------------


def _tampered(names: "tuple[str, ...]", rows: int, name: str, change: "typing.Callable[[list[str]], int]") -> "list[str]":
    """What validation MISSES on ``name`` of a good twin with one of its cells changed."""
    folder, _columns, _document, loaded, _table = _described(names, rows, 11)
    body = list(csv.reader(io.StringIO(rendering.twin_csv(generation.generate(loaded, 0)))))
    place = body[0].index(name)
    column = [row[place] for row in body[1:]]
    row = change(column)
    body[row + 1][place] = column[row]
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(body)
    target = fixtures.write(folder, f"tampered-{name}.csv", out.getvalue())
    return [entry.split(":", 1)[1] for entry in _missed(loaded, target) if entry.startswith(name + ":")]


def _first(cells: "list[str]", wanted: "typing.Callable[[str], bool]") -> int:
    return next(place for place in range(len(cells)) if wanted(cells[place]))


def _heap_moved(cells: "list[str]") -> int:
    """One cell of the heap at 22:00 moved to 22:01, a step of its own group."""
    place = _first(cells, lambda cell: cell == "22:00")
    cells[place] = "22:01"
    return place


def _code_rewritten(cells: "list[str]") -> int:
    """One cell of the code `not recorded` rewritten as another unread spelling."""
    place = _first(cells, lambda cell: cell == "not recorded")
    cells[place] = "not done"
    return place


def _off_the_step(cells: "list[str]") -> int:
    """One cell of the five-minute grid moved a minute off it."""
    place = _first(cells, lambda cell: (_second(cell) or 0) % 3600 < 3000)
    second = _second(cells[place]) or 0
    cells[place] = parsing.clock_spelling(second // 60 + 1, parsing.CLOCK_HH_MM)
    return place


_TAMPERED = {
    "clock_heaps.counts": (("night_obs",), 1000, "night_obs", _heap_moved),
    "clock_codes.counts": (("coded",), 2500, "coded", _code_rewritten),
    "clock_step.values": (("grid5",), 1000, "grid5", _off_the_step),
}


@pytest.mark.parametrize("subcheck", sorted(_TAMPERED))
def test_v_one_cell_moved_is_missed(subcheck: str) -> None:
    names, rows, name, change = _TAMPERED[subcheck]
    _cells_now, missed = _twin(names, rows, 11, 0)
    assert missed == []
    assert subcheck in _tampered(names, rows, name, change)


@pytest.mark.parametrize("subcheck", sorted(_TAMPERED))
def test_v_red_when_the_check_always_holds(subcheck: str, monkeypatch: pytest.MonkeyPatch) -> None:
    built = validation._clock_census_checks

    def always(*arguments):  # type: ignore[no-untyped-def]
        return [
            dataclasses.replace(check, verdict=validation.HELD) if check.subcheck == subcheck else check
            for check in built(*arguments)
        ]

    monkeypatch.setattr(validation, "_clock_census_checks", always)
    names, rows, name, change = _TAMPERED[subcheck]
    assert subcheck not in _tampered(names, rows, name, change)


# -- M: a clock-shaped stand-in is a time ---------------------------------


# The forms a clock time wears as `parsing.shape_form` writes them: an hour
# of one or two figures, a colon and two, optionally a colon and two more,
# and optionally a marker with no space before it (a cell holding a space
# has no form, and a held-back level of one is written `group-N`).
_CLOCK_SHAPE = re.compile(r"^%{1,2}:%%(:%%)?(@@|&&|@\.@\.|&\.&\.)?$")
# ...and Excel's `h:mm AM`, whose space before the marker leaves it no
# form: its held-back levels take the key `%:%% @@` (the repair round).
_MIXED = ("mixed_walkin", "mixed_hmm", "mixed_ampm")


def _shaped_but_no_time(cells: "list[str]") -> int:
    return sum(
        1 for cell in cells
        if cell and _CLOCK_SHAPE.match(parsing.shape_form(cell)) and _second(cell) is None
    )


def _neither_word_nor_time(cells: "list[str]") -> int:
    """Cells that are neither the column's published word nor a time."""
    return sum(1 for cell in cells if cell and cell != "unknown" and _second(cell) is None)


def test_m_a_clock_shaped_stand_in_is_a_time() -> None:
    _folder, _columns, document, _loaded, _table = _described(_MIXED, 1000, 11)
    for name in _MIXED:
        assert _block(document, name)["role"] != taxonomy.ROLE_CLOCK, name
    for seed in _SEEDS:
        cells, missed = _twin(_MIXED, 1000, 11, seed)
        for name in _MIXED:
            assert _shaped_but_no_time(cells[name]) == 0, (seed, name)
        assert _neither_word_nor_time(cells["mixed_ampm"]) == 0, seed
        assert missed == [], (seed, missed)


def test_m_red_when_the_form_is_filled_figure_by_figure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generation, "_clock_filled_form", lambda _form, _step: None)
    _twin.cache_clear()
    try:
        cells, _missed_now = _twin(_MIXED, 1000, 11, 0)
        for name in _MIXED[:2]:
            assert _shaped_but_no_time(cells[name]) > 0, name
        assert _neither_word_nor_time(cells["mixed_ampm"]) > 0
    finally:
        _twin.cache_clear()


def test_m_red_without_the_key_of_a_spaced_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(generation, "_SPACED_CLOCK_MARKS", {})
    _twin.cache_clear()
    try:
        cells, _missed_now = _twin(_MIXED, 1000, 11, 0)
        assert _neither_word_nor_time(cells["mixed_ampm"]) > 0
    finally:
        _twin.cache_clear()


# -- W: rare words beside clock times keep the clock ----------------------


def test_w_rare_words_beside_clock_times_keep_the_clock() -> None:
    _folder, _columns, document, _loaded, _table = _described(("unk4",), 300, 11)
    block = _block(document, "unk4")
    assert block["role"] == taxonomy.ROLE_CLOCK and block["n_missing"] == 4
    for seed in _SEEDS:
        _cells_now, missed = _twin(("unk4",), 300, 11, seed)
        assert missed == []


def _codes_beside(column: "list[str]", floor: int) -> "int | None":
    """The cells of a few rare codes beside clock times, or None where they are not.

    The times alone miss the clock line, every spelling no clock reader
    takes is held by fewer rows than the floor, and together they hold at
    most one present cell in fifty -- the rule stated here, not read off
    `taxonomy.RARE_WORDS_BESIDE_CLOCKS`, so a mutant of it is seen: the
    level pass counts exactly these missing and reads the column as clock
    times.
    """
    present = [cell for cell in column if cell]
    codes = collections.Counter(cell for cell in present if _second(cell) is None)
    rate = taxonomy.Settings().minimum_parse_rate
    if not codes or len(present) - sum(codes.values()) >= taxonomy.clock_line(rate, len(present)):
        return None
    if max(codes.values()) >= floor:
        return None
    held = sum(codes.values())
    return held if held * 50 <= len(present) else None


def _rare_codes_kept(rows: int, floor: int) -> "tuple[int, list[str]]":
    """How many code-mix columns hold a few rare codes, and which of them are not clock times."""
    _folder, columns, document, _loaded, _table = _described(_CODED, rows, floor)
    asked = 0
    broken: "list[str]" = []
    for name in _CODED:
        held = _codes_beside(columns[name], floor)
        if held is None:
            continue
        asked = asked + 1
        block = _block(document, name)
        if block["role"] != taxonomy.ROLE_CLOCK or block["n_missing"] != held:
            broken += [name]
    return asked, broken


@pytest.mark.parametrize("rows,floor", _CODED_SIZES)
def test_w_a_few_rare_codes_beside_times_keep_the_clock(rows: int, floor: int) -> None:
    """Asked of every reading as labels or free text (the repair round, item 3).

    Beside a few rare codes no level is forced to a count of one, so the
    level pass used not to ask, and a column of `7:30 AM` beside 0.6 %
    `UNK` and 0.3 % `99:99` stayed free text whose twin was `group-N`.
    """
    _asked_here, broken = _rare_codes_kept(rows, floor)
    assert broken == [], (rows, floor, broken)


def test_w_rare_codes_are_met_at_every_size() -> None:
    assert sum(_rare_codes_kept(rows, floor)[0] for rows, floor in _CODED_SIZES) >= 6


def test_w_red_when_the_few_words_are_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "RARE_WORDS_BESIDE_CLOCKS", 10**9)
    _described.cache_clear()
    _twin.cache_clear()
    try:
        assert any(_rare_codes_kept(rows, floor)[1] for rows, floor in _CODED_SIZES)
    finally:
        _described.cache_clear()
        _twin.cache_clear()


def test_w_red_when_the_level_pass_keeps_the_labels(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "_rare_beside_clocks", lambda *_a: ())
    _described.cache_clear()
    _twin.cache_clear()
    try:
        _folder, _columns, document, _loaded, _table = _described(("unk4",), 300, 11)
        # Labels, whose twin G8.3's clock line keeps labels too: what is
        # lost is the column's time of day, which no label publishes.
        assert _block(document, "unk4")["role"] != taxonomy.ROLE_CLOCK
    finally:
        _described.cache_clear()
        _twin.cache_clear()


# -- Q: a few shared times are asked about --------------------------------


def _asked(document: "dict[str, object]", columns: "dict[str, list[str]]", names: "tuple[str, ...]") -> "list[asking.Question]":
    return asking.questions_for(
        document, [columns[name] for name in names], taxonomy.Settings(small_cell_floor=11), []
    )


_ASKED = ("shifts3", "shift_start", "handover")


def _asked_about_times(names: "tuple[str, ...]", rows: int) -> "list[str]":
    _folder, columns, document, _loaded, _table = _described(names, rows, 11)
    return [
        question.name for question in _asked(document, columns, names)
        if question.reason == asking.BECAUSE_FEW_CLOCK_TIMES
    ]


def test_q_a_few_shared_times_are_asked_about() -> None:
    """Asked of three shift starts, whose heaps hold every cell; not of times a census spreads."""
    _folder, columns, document, _loaded, _table = _described(_ASKED, 1000, 11)
    asked = {question.name: question for question in _asked(document, columns, _ASKED)}
    assert asked["shifts3"].reason == asking.BECAUSE_FEW_CLOCK_TIMES
    assert [choice.answer for choice in asked["shifts3"].choices] == [asking.ANSWER_KEEP, asking.ANSWER_CODE]
    # Shift starts with 10 % jitter and the handover publish a census: the
    # data says they are times, and nobody is asked.
    assert _asked_about_times(_ASKED, 1000) == ["shifts3"]
    # ...nor of walk-ins at 10,000 rows, 700 times spread over the day.
    assert _asked_about_times(("walkin",), 10000) == []
    # ...and the answer `code` is `--code`, which reads the column as labels.
    _folder, _columns, answered, _loaded, _table = _described(_ASKED, 1000, 11, ("shifts3",))
    assert _block(answered, "shifts3")["role"] == taxonomy.ROLE_CATEGORICAL


def test_q_red_without_the_question(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asking, "_clock_or_labels_question", lambda *_a: None)
    assert "shifts3" not in _asked_about_times(_ASKED, 1000)


def test_q_red_when_asked_beside_a_census(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(asking, "_heaps_hold_the_body", lambda _block: True)
    assert _asked_about_times(_ASKED, 1000) != ["shifts3"]


def test_the_description_says_so_where_the_census_is_left_out() -> None:
    """NF106: fewer than the line left beside the heaps leaves the census out, and says so."""
    _folder, _columns, document, _loaded, _table = _described(("lonely",), 45, 11)
    block = _block(document, "lonely")
    assert block["clock_census"] == [] and block["clock_heaps"] == [{"value": "08:00", "count": 40}]
    said = [entry["note"] for entry in document["publication_notes"] if entry["column"] == "lonely"]  # type: ignore[union-attr]
    assert any("ten-minute stretch" in sentence for sentence in said), said
    for seed in _SEEDS:
        _cells_now, missed = _twin(("lonely",), 45, 11, seed)
        assert missed == []


# -- G: the publication guard holds each clock leaf to its kind ---------------


# One leaf of each kind the profile's registry gives a clock block, and a
# value of the wrong kind for it: a bin past the dial, a group of five, a
# heap of five, a heap that is no time, and a step that does not divide
# the dial.
_LEAVES = {
    "a-ten-minute-bin-of-the-dial": ("clock_census", "first", 144),
    "a-clock-group-count-zero-or-at-the-census-line": ("clock_census", "count", 5),
    "a-clock-count-at-the-census-line": ("clock_heaps", "count", 5),
    "a-clock-time-in-its-columns-form": ("clock_heaps", "value", "25:00"),
    "seconds-a-clock-steps-by-or-nothing": ("clock_step", "", 7),
}


def _perturbed(kind: str) -> "dict[str, object]":
    """The coded column's description with one leaf of ``kind`` of the wrong kind."""
    _folder, _columns, document, _loaded, _table = _described(("coded",), 2500, 11)
    changed = copy.deepcopy(document)
    key, field, value = _LEAVES[kind]
    block = _block(changed, "coded")
    if not field:
        block[key] = value
    else:
        block[key][0][field] = value  # type: ignore[index]
    return changed


def test_g_the_guard_holds_each_clock_leaf_to_its_kind() -> None:
    _folder, _columns, document, _loaded, _table = _described(("coded",), 2500, 11)
    profile.check_publication(document)
    for kind in sorted(_LEAVES):
        with pytest.raises(errors.ProfileError):
            profile.check_publication(_perturbed(kind))


@pytest.mark.parametrize("kind", sorted(_LEAVES))
def test_g_red_when_the_kind_is_always_published(kind: str, monkeypatch: pytest.MonkeyPatch) -> None:
    built = profile._leaf_is_published

    def always(rule, value, key, path, context):  # type: ignore[no-untyped-def]
        return rule == kind or built(rule, value, key, path, context)

    monkeypatch.setattr(profile, "_leaf_is_published", always)
    profile.check_publication(_perturbed(kind))

"""Stage 4 lane S4b-num: four million-row costs of numbers and codes, without their square.

docs/STATE.md named them under lane S4b, and each was measured on
3434682 before it was changed:

1. **G6.5a's push** (`generation._pushed_apart`, plan P4-D377). For every
   collision the walks leave it read every stratum to find the lowest
   collision, every stratum again for its holders and, for every way and
   mover, every stratum for the strata the walk passed; and it walked
   each way to its free point in full however far the other way's
   stood. Consecutive whole numbers beside five far ones, declared a
   measurement at a floor of eleven, took 2.1, 5.0 and 14.1 s to
   `generate` at 4,000, 8,000 and 16,000 rows.
2. **G6.6's identity walk** (`generation._identity_walk`, split out of
   `_number_cells`, plan P4-D387). Each repeated spelling of a value began
   its walk of leading-zero orders at the first again: 249 of the 624 s
   `generate` took on the Codex column of a million rows.
3. **G8.3c's pooled placement** (`generation._pooled_spelling` and the
   offers above it, plan P4-D390). Each group stepped out from where it
   was asked past every place the rules refuse, up to 2,048 of them, and
   every group asked those rules again of the same places: 13.7 million
   spellings offered for 17,690 groups at 50,000 rows of decimal codes,
   and 13 to 22 minutes at 1,000,000.
4. **The quality report** (`quality.quality_report`, plan P4-D390). Every
   check's lines were added to a copy of every line before them, and
   the text grew by a copy of itself for every line: validating a
   register of 50,000 consecutive codes was killed at 960 s and 1.7 GB.

None of the four changes a byte, so each keeps the function it replaced
as its ORACLE (`tests/stage4_as_built.py`), asks both the same questions
and requires the same answers, and measures the work with a count that
needs no clock, taken on the replaced function too, which is required
to show the defect: under 2.5 times a doubling now, at least three times
as built. Each count is also taken at the size of a 1,000,000-row
table, where the replaced function is stopped once it passes the bound
the new one keeps.
"""

from __future__ import annotations

import copy
import dataclasses
import pathlib
import sys
import tracemalloc
import types

import pytest

import kpi_shapes
import stage4_as_built
from synthtwin import generation, parsing, quality, validation

LINEAR_AT_MOST = 2.5
SQUARE_AT_LEAST = 3.0


class _TooMuchWork(Exception):
    """Raised by a counter once a replaced function passes the bound the new one keeps."""


def _table(columns: "dict[str, list[str]]") -> str:
    """A table of ``columns``, every cell quoted."""
    names = list(columns)
    lines = [",".join(names)]
    for index in range(len(columns[names[0]])):
        lines += [",".join('"' + columns[name][index] + '"' for name in names)]
    return "\n".join(lines) + "\n"


def _lines_run(codes: "set[object]", function: "object", *arguments: object) -> int:
    """How many lines the frames of ``codes`` run while ``function(*arguments)`` answers."""
    counted = [0]

    def local(frame: object, event: str, argument: object) -> object:
        if event == "line":
            counted[0] += 1
        return local

    def calls(frame: object, event: str, argument: object) -> object:
        if event == "call" and frame.f_code in codes:  # type: ignore[attr-defined]
            return local
        return None

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return counted[0]


def _allocated_in(codes: "set[object]", function: "object", *arguments: object, cap: int = 0) -> int:
    """The bytes the lines of the frames of ``codes`` allocate above what each line found, summed.

    A line that copies a list of n items allocates n more pointers while
    the old one is held, and a line that adds a text to a copy of a
    longer one allocates the longer one again; a line that grows a list
    in place allocates what it adds. Read off `tracemalloc`'s peak, taken
    and reset at every such line, so no clock plays a part. With ``cap``
    the count stops the call by raising `_TooMuchWork` once it passes it.
    """
    total = [0]
    since = [0]

    def local(frame: object, event: str, argument: object) -> object:
        if event in ("line", "return"):
            peak = tracemalloc.get_traced_memory()[1]
            total[0] += max(0, peak - since[0])
            tracemalloc.reset_peak()
            since[0] = tracemalloc.get_traced_memory()[0]
            if cap and total[0] > cap:
                raise _TooMuchWork(total[0])
        return local

    def calls(frame: object, event: str, argument: object) -> object:
        if event == "call" and frame.f_code in codes:  # type: ignore[attr-defined]
            return local
        return None

    tracing = tracemalloc.is_tracing()
    if not tracing:
        tracemalloc.start()
    previous = sys.gettrace()
    try:
        tracemalloc.reset_peak()
        since[0] = tracemalloc.get_traced_memory()[0]
        sys.settrace(calls)  # type: ignore[arg-type]
        try:
            function(*arguments)  # type: ignore[operator]
        finally:
            sys.settrace(previous)
    finally:
        if not tracing:
            tracemalloc.stop()
    return total[0]


# -- 4. the quality report ----------------------------------------------------


def _report_as_built() -> "tuple[object, dict]":
    return stage4_as_built.compiled(quality, stage4_as_built.QUALITY_REPORT, "quality_report")


_REGISTERS: "dict[tuple[int, bool], tuple[object, validation.Outcome]]" = {}


def _register(folder: pathlib.Path, codes: int, damaged: bool) -> "tuple[object, validation.Outcome]":
    """A register of ``codes`` consecutive seven-figure codes, eleven rows each and one in 25 on one row.

    Described by the real producer with the codes declared, and measured
    against itself, or with ``damaged`` against a file missing a fifth of
    its rows, so the report has misses to put first.
    """
    if (codes, damaged) in _REGISTERS:
        return _REGISTERS[(codes, damaged)]
    cells: "list[str]" = []
    for place in range(codes):
        cells += [str(1000001 + place)] * (1 if place % 25 == 7 else 11)
    arms = ["a" if place % 3 else "b" for place in range(len(cells))]
    stem = f"register{codes}{'d' if damaged else ''}"
    described = kpi_shapes.describe(folder / stem, stem, _table({"code": cells, "arm": arms}), 11, codes=["code"])
    measured = cells
    measured_arms = arms
    if damaged:
        measured = [cells[place] for place in range(len(cells)) if place % 5]
        measured_arms = [arms[place] for place in range(len(cells)) if place % 5]
    outcome = kpi_shapes.measure(described, _table({"code": measured, "arm": measured_arms}), f"{stem}-measured.csv")
    _REGISTERS[(codes, damaged)] = (described.loaded, outcome)
    return _REGISTERS[(codes, damaged)]


def _with_checks(outcome: validation.Outcome, count: int) -> validation.Outcome:
    """``outcome`` with its checks repeated, in order, to ``count`` checks."""
    checks = list(outcome.checks)
    grown: "list[validation.Check]" = []
    while len(grown) < count:
        grown += checks[: count - len(grown)]
    return dataclasses.replace(outcome, checks=tuple(grown))


def _report_codes(as_built: bool) -> "tuple[object, set[object]]":
    """The report function and the code of every function its lines are counted in."""
    if as_built:
        function, names = _report_as_built()
        built = ("quality_report", "_detail_lines", "_missed_lines", "_column_order")
        return function, {names[name].__code__ for name in built}  # type: ignore[attr-defined]
    shipped = ("quality_report", "_detail_lines", "_missed_lines", "_column_order", "_lines_joined")
    return quality.quality_report, {getattr(quality, name).__code__ for name in shipped}


def report_bytes(loaded: object, outcome: validation.Outcome, as_built: bool = False, cap: int = 0) -> int:
    """The bytes the report's own lines allocate writing the report of ``outcome``."""
    function, codes = _report_codes(as_built)
    return _allocated_in(codes, function, loaded, outcome, cap=cap)


def test_the_report_is_the_report_as_built_wrote(tmp_path: pathlib.Path) -> None:
    """Registers of 40 and 300 codes, met and damaged: the same report, byte for byte."""
    built, _names = _report_as_built()
    for codes in (40, 300):
        for damaged in (False, True):
            loaded, outcome = _register(tmp_path, codes, damaged)
            assert damaged == any(check.verdict == validation.MISSED for check in outcome.checks), "premise"
            assert quality.quality_report(loaded, outcome) == built(loaded, outcome), (codes, damaged)  # type: ignore[operator]
    loaded, outcome = _register(tmp_path, 40, True)
    for count in (1, 2, 997):
        grown = _with_checks(outcome, count)
        assert quality.quality_report(loaded, grown) == built(loaded, grown), count  # type: ignore[operator]


def test_the_report_is_written_with_work_that_grows_with_its_checks(tmp_path: pathlib.Path) -> None:
    """2,000 and 4,000 checks: the bytes its lines allocate grow under 2.5 times; as built, at least three."""
    loaded, outcome = _register(tmp_path, 40, True)
    small, large = (report_bytes(loaded, _with_checks(outcome, count)) for count in (2000, 4000))
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small, old_large = (report_bytes(loaded, _with_checks(outcome, count), True) for count in (2000, 4000))
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


class _Copied(str):
    """A line of the report that counts the characters each concatenation it takes part in copies."""

    __slots__ = ()
    copied = [0]
    cap = [0]

    def __add__(self, other: str) -> "_Copied":  # type: ignore[override]
        return _Copied._counted(str.__add__(self, other))

    def __radd__(self, other: str) -> "_Copied":
        return _Copied._counted(str.__add__(other, self))

    @staticmethod
    def _counted(text: str) -> "_Copied":
        _Copied.copied[0] += len(text)
        if _Copied.cap[0] and _Copied.copied[0] > _Copied.cap[0]:
            raise _TooMuchWork(_Copied.copied[0])
        return _Copied(text)


def report_copied(loaded: object, outcome: validation.Outcome, as_built: bool = False, cap: int = 0) -> "tuple[int, int]":
    """The characters the report's concatenations copy, every check's lines counted (`_Copied`), and the report's length."""
    function = _report_as_built()[0] if as_built else quality.quality_report
    shipped = quality._detail_of
    # Each check hands back as many lines as it writes, each one character
    # long, so the join is asked to copy as many lines as the report has
    # while the test holds a few bytes of text a line.
    written: "dict[int, list[_Copied]]" = {}

    def detail(check: validation.Check) -> "list[_Copied]":
        if id(check) not in written:
            written[id(check)] = [_Copied("x") for _line in shipped(check)]
        return written[id(check)]

    _Copied.copied[0] = 0
    _Copied.cap[0] = cap
    try:
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(quality, "_detail_of", detail)
            if as_built:
                names = _report_as_built()[1]
                names["_detail_of"] = quality._detail_of
                function = names["quality_report"]
            length = len(function(loaded, outcome))  # type: ignore[operator]
    finally:
        _Copied.cap[0] = 0
    return _Copied.copied[0], length


def test_the_report_of_a_million_row_register_copies_each_character_a_bounded_number_of_times(
    tmp_path: pathlib.Path,
) -> None:
    """The checks of a register of 1,000,000 rows: each character of the report copied under 30 times; as built, stopped there.

    Such a register -- consecutive codes on eleven rows, one in 25 on one
    row -- holds 94,339 codes, and its own table is measured here over
    the checks a code of the 300-code register carries, that many times:
    473,267 checks. Each check's lines are written one character long, so
    the join is asked for as many lines as that report has (about 1.1
    million) while the test holds a few bytes a line. Joined in halves,
    each character is copied once a level, as many levels as the line
    count has binary digits. As built the text grew by a copy of itself
    for every line, and it passes the bound before a tenth of the checks
    are written.
    """
    loaded, outcome = _register(tmp_path, 300, False)
    codes = 1000000 * 25 // (24 * 11 + 1)
    count = len(outcome.checks) * codes // 300
    tenth = report_copied(loaded, _with_checks(outcome, count // 10), cap=30 * 1000000)[1]
    copied, length = report_copied(loaded, _with_checks(outcome, count), cap=30 * 11 * tenth)
    assert length <= copied < 30 * length, (count, copied, length)
    with pytest.raises(_TooMuchWork):
        report_copied(loaded, _with_checks(outcome, count // 10), True, cap=30 * length)


# -- 2. the identity walk -----------------------------------------------------


def _walk_as_built() -> "tuple[object, dict]":
    return stage4_as_built.compiled(generation, stage4_as_built.IDENTITY_WALK, "_identity_walk")


def _codex_cells(rows: int) -> "list[str]":
    """The Codex review's column of P4-D387: two values written a hundredth of the rows' ways each."""
    hundredth = rows // 100
    cells = ["0.1" + "0" * place for place in range(hundredth)]
    cells += ["0.10000000000000002" + "0" * place for place in range(hundredth)]
    cells += [str(5 * place) if place % 10 < 7 else str(5 * place + 0.25) for place in range(rows - 2 * hundredth)]
    return cells


def _walks_handed(folder: pathlib.Path, stem: str, cells: "list[str]", floor: int = 11) -> "list[tuple[object, ...]]":
    """What the identity walk is handed while the twin of a one-column table is written, at seeds 0 and 4."""
    described = kpi_shapes.describe(folder / stem, stem, _table({"value": cells}), floor)
    handed: "list[tuple[object, ...]]" = []
    shipped = generation._identity_walk

    def captured(*arguments: object) -> object:
        handed.extend([copy.deepcopy(arguments)])
        return shipped(*arguments)  # type: ignore[arg-type]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_identity_walk", captured)
        for seed in (0, 4):
            kpi_shapes.twin_text(described, seed)
    return handed


def _counting_spelling(counted: "list[int]", cap: int = 0) -> "object":
    """A stand-in for `_styled_number` that counts its calls and spells each order apart."""

    def spelled(value, style, order, whole, width=-1, pad=-1, mark="", negative="-", plus=False):  # type: ignore[no-untyped-def]
        counted[0] += 1
        if cap and counted[0] > cap:
            raise _TooMuchWork(counted[0])
        return f"{order}|{value!r}|{style}|{width}|{pad}|{mark}|{negative}|{plus}"

    return spelled


def walk_spellings(handed: "tuple[object, ...]", as_built: bool = False, cap: int = 0) -> int:
    """How many spellings the identity walk asks `_styled_number` for, on ``handed``."""
    function = _walk_as_built()[0] if as_built else generation._identity_walk
    counted = [0]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_styled_number", _counting_spelling(counted, cap))
        if as_built:
            names = _walk_as_built()[1]
            names["_styled_number"] = generation._styled_number
            function = names["_identity_walk"]
        function(*handed)  # type: ignore[operator]
    return counted[0]


def test_each_cell_takes_the_spelling_the_walk_as_built_gave(tmp_path: pathlib.Path) -> None:
    """The Codex column, leading zeros, marks and pluses at floors 11 and 36: the same spellings."""
    built, _names = _walk_as_built()
    shapes = {
        "codex": (_codex_cells(1500), 11),
        "zeros": ([("0" * (place % 4)) + str(place % 90) for place in range(900)], 11),
        "zeros36": ([("0" * (place % 3)) + str(place % 40) for place in range(900)], 36),
        "plus": ([("+" if place % 3 == 0 else "") + str(place % 70) + ".5" for place in range(700)], 11),
        "marks": ([f"{1000 + place % 50:,}" if place % 2 else str(1000 + place % 50) for place in range(800)], 11),
    }
    walked = 0
    for stem, (cells, floor) in shapes.items():
        for handed in _walks_handed(tmp_path, stem, cells, floor):
            ours = generation._identity_walk(*copy.deepcopy(handed))  # type: ignore[arg-type]
            theirs = built(*copy.deepcopy(handed))  # type: ignore[operator]
            assert list(ours.items()) == list(theirs.items()), stem
            walked += 1
    assert walked >= 10, walked


def test_the_twin_of_the_codex_column_is_the_twin_the_walk_as_built_wrote(tmp_path: pathlib.Path) -> None:
    """3,000 rows of the Codex column, seeds 0 and 4: the twin's bytes with either walk."""
    described = kpi_shapes.describe(tmp_path / "codex", "codex", _table({"value": _codex_cells(3000)}), 11)
    ours = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_identity_walk", _walk_as_built()[0])
        theirs = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    assert ours == theirs


def test_the_identity_walk_asks_for_spellings_that_grow_with_the_rows(tmp_path: pathlib.Path) -> None:
    """The Codex column at 2,000 and 4,000 rows: the spellings asked grow under 2.5 times; as built, at least three."""
    small = _walks_handed(tmp_path, "c2000", _codex_cells(2000))[0]
    large = _walks_handed(tmp_path, "c4000", _codex_cells(4000))[0]
    ours = (walk_spellings(small), walk_spellings(large))
    assert ours[0] > 0 and ours[1] / ours[0] < LINEAR_AT_MOST, ours
    theirs = (walk_spellings(small, True), walk_spellings(large, True))
    assert theirs[1] / theirs[0] >= SQUARE_AT_LEAST, theirs


def test_a_million_cells_spelling_one_value_twenty_thousand_ways_ask_no_more_spellings_than_cells(
    tmp_path: pathlib.Path,
) -> None:
    """1,000,000 cells shaped as the Codex column: fewer spellings asked than cells; as built, stopped past them.

    The twin of 2,000 rows of the column writes its two values on 21
    cells of one stratum, 0.1, and owes 25 spellings more than its values
    carry. Here those 21 cells are repeated to 20,000 -- the two values'
    10,000 cells each at 1,000,000 rows -- and owe 20,000 spellings, and
    the column's other cells fill the million, each a value of its own.
    """
    handed = _walks_handed(tmp_path, "c2000m", _codex_cells(2000))[0]
    holds, styles, base, widths, pads, marks, notations, plussed, whole, owed = handed  # type: ignore[misc]
    seen: "dict[float, list[int]]" = {}
    for index in range(len(holds)):  # type: ignore[arg-type]
        seen.setdefault(holds[index], []).extend([index])  # type: ignore[index]
    widest = max(seen.values(), key=len)
    assert len(widest) == 21 and holds[widest[0]] == 0.1 and owed == 25, "premise"  # type: ignore[index]
    others = [places[0] for places in seen.values() if places is not widest]
    order = [widest[step % 21] for step in range(20000)]
    order += [others[step % len(others)] for step in range(1000000 - 20000)]
    grown = [[column[index] for index in order] for column in (holds, styles, base, widths, pads, marks, notations, plussed)]  # type: ignore[index]
    for step in range(20000, 1000000):
        grown[0][step] = float(step)
        grown[2][step] = str(step)
    million = tuple(grown) + (whole, 20000)
    asked = walk_spellings(million, cap=1000000)
    assert 19999 <= asked < 1000000, asked
    with pytest.raises(_TooMuchWork):
        walk_spellings(million, True, cap=1000000)


# -- 1. the push --------------------------------------------------------------


def _push_as_built() -> "tuple[object, dict]":
    return stage4_as_built.compiled(generation, stage4_as_built.PUSHED_APART, "_pushed_apart")


def _dense_tail(rows: int) -> "list[str]":
    """Consecutive whole numbers to 999999 beside five of seven figures (Codex's review of lane G2, item 3)."""
    cells = [str(value) for value in range(1000005 - rows, 1000000)]
    return cells + [str(999999 + int(1.56 * rows) + step) for step in range(5)]


def _pushes_handed(folder: pathlib.Path, stem: str, cells: "list[str]", floor: int, measured: "list[str]") -> "list[tuple[object, ...]]":
    """What the push is handed while the twin of a one-column table is written, at seeds 0 and 4."""
    described = kpi_shapes.describe(folder / stem, stem, _table({"value": cells}), floor, measured=measured)
    handed: "list[tuple[object, ...]]" = []
    shipped = generation._pushed_apart

    def captured(*arguments: object) -> object:
        handed.extend([copy.deepcopy(arguments)])
        return shipped(*arguments)  # type: ignore[arg-type]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_pushed_apart", captured)
        for seed in (0, 4):
            kpi_shapes.twin_text(described, seed)
    return handed


def _pushed(function: "object", handed: "tuple[object, ...]") -> "tuple[object, ...]":
    moved, texts, held = function(*copy.deepcopy(handed))  # type: ignore[operator]
    return (repr(moved), list(texts), list(held.items()))


def _staircase(strata: int, figures: int = 0) -> "tuple[object, ...]":
    """``strata`` positive strata two grid units apart, every 64th on its neighbour's unit: one free point beside each collision."""
    units = [10 + 2 * place for place in range(strata)]
    for place in range(1, strata - 1):
        if place % 64 == 1:
            units[place] = units[place - 1]
    texts = [generation._grid_at(unit, figures) for unit in units]
    moved = [float(text) for text in texts]
    held: "dict[str, int]" = {}
    for text in texts:
        held[text] = held.get(text, 0) + 1
    facts = types.SimpleNamespace(
        n_distinct_values=strata, empty_edges=(), kept_stand_ins=(), integer_valued=True, numeric_styles={}
    )
    layout = types.SimpleNamespace(bands=("positive",) * strata)
    rungs = (moved[0], moved[-1])
    return (facts, layout, rungs, moved, texts, held, figures, False)


def _push_codes(as_built: bool) -> "tuple[object, set[object]]":
    if as_built:
        function, names = _push_as_built()
        return function, {names["_pushed_apart"].__code__, names["_push_plan"].__code__}  # type: ignore[attr-defined]
    shipped = ("_pushed_apart", "_push_way", "_push_plan", "_strata_passed", "_unit_heap_push", "_unit_heap_pop", "_push_kind")
    return generation._pushed_apart, {getattr(generation, name).__code__ for name in shipped}


def push_lines(handed: "tuple[object, ...]", as_built: bool = False) -> int:
    """The lines the push and its own walk run on ``handed``."""
    function, codes = _push_codes(as_built)
    return _lines_run(codes, function, *copy.deepcopy(handed))


def test_the_push_moves_what_the_push_as_built_moved(tmp_path: pathlib.Path) -> None:
    """Dense tails, stand-ins, whole and fractional heaps, staircases: the same values, texts and counts."""
    built, _names = _push_as_built()
    shapes = (
        ("tail2000", _dense_tail(2000), 11, ["value"]),
        ("tail3000", _dense_tail(3000), 36, ["value"]),
        ("stand", [f"{-999.0 + (place % 37) / 10:.1f}" for place in range(600)] + ["-999"] * 25, 11, []),
        ("halves", [str(place // 3) + (".5" if place % 2 else "") for place in range(900)], 11, []),
        ("crowded", [f"{(place * 7919) % 1500 / 100:.2f}" for place in range(1200)] + ["-0.01"] * 12, 11, []),
    )
    asked = 0
    for stem, cells, floor, measured in shapes:
        for handed in _pushes_handed(tmp_path, stem, cells, floor, measured):
            assert _pushed(generation._pushed_apart, handed) == _pushed(built, handed), stem
            asked += 1
    for strata in (130, 700):
        for figures in (0, 2):
            handed = _staircase(strata, figures)
            assert _pushed(generation._pushed_apart, handed) == _pushed(built, handed), (strata, figures)
    assert asked >= 8, asked


def test_the_twin_of_the_dense_tail_is_the_twin_the_push_as_built_wrote(tmp_path: pathlib.Path) -> None:
    """4,000 rows of the dense tail, seeds 0 and 4: the twin's bytes with either push."""
    described = kpi_shapes.describe(tmp_path / "tail", "tail", _table({"value": _dense_tail(4000)}), 11, measured=["value"])
    ours = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_pushed_apart", _push_as_built()[0])
        theirs = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    assert ours == theirs


def test_the_push_runs_lines_that_grow_with_the_strata() -> None:
    """A staircase of 2,000 and 4,000 strata: the lines run grow under 2.5 times; as built, at least three."""
    small, large = _staircase(2000), _staircase(4000)
    ours = (push_lines(small), push_lines(large))
    assert ours[1] / ours[0] < LINEAR_AT_MOST, ours
    theirs = (push_lines(small, True), push_lines(large, True))
    assert theirs[1] / theirs[0] >= SQUARE_AT_LEAST, theirs


def _counted_calls(names: "tuple[str, ...]", counted: "list[int]", cap: int, where: "dict") -> None:
    """Wrap each of ``names`` in ``where`` to count its calls, raising `_TooMuchWork` past ``cap``."""
    for name in names:
        shipped = where[name]

        def counting(*arguments: object, _shipped: object = shipped, **named: object) -> object:
            counted[0] += 1
            if cap and counted[0] > cap:
                raise _TooMuchWork(counted[0])
            return _shipped(*arguments, **named)  # type: ignore[operator]

        where[name] = counting


_PUSH_HELPERS = ("_grid_units", "_grid_at", "_band_step", "_push_allowed", "_whole_valued")


def push_calls(handed: "tuple[object, ...]", as_built: bool = False, cap: int = 0) -> int:
    """How many grid, step and permission questions the push asks on ``handed``."""
    counted = [0]
    if as_built:
        function, names = _push_as_built()
        _counted_calls(_PUSH_HELPERS, counted, cap, names)
        function(*handed)  # type: ignore[operator]
        return counted[0]
    with pytest.MonkeyPatch.context() as patch:
        where = dict(vars(generation))
        _counted_calls(_PUSH_HELPERS, counted, cap, where)
        for name in _PUSH_HELPERS:
            patch.setattr(generation, name, where[name])
        generation._pushed_apart(*handed)  # type: ignore[arg-type]
    return counted[0]


def test_a_million_strata_ask_the_push_a_bounded_number_of_questions() -> None:
    """A staircase of 1,000,000 strata: fewer than six grid, step and permission questions a stratum; as built, stopped there.

    Its 15,624 collisions each find a free point beside them. As built
    each read every stratum's grid unit again for each way, so it passes
    the bound within its first collisions.
    """
    strata = 1000000
    asked = push_calls(_staircase(strata), cap=6 * strata)
    assert asked < 6 * strata, asked
    with pytest.raises(_TooMuchWork):
        push_calls(_staircase(strata), True, cap=6 * strata)


def test_the_push_on_the_dense_tail_asks_steps_that_grow_with_the_rows(tmp_path: pathlib.Path) -> None:
    """The dense tail at 4,000 and 8,000 rows: under eight band steps a row; as built, 27 at 4,000."""
    for rows in (4000, 8000):
        handed = _pushes_handed(tmp_path, f"steps{rows}", _dense_tail(rows), 11, ["value"])[0]
        counted = [0]
        with pytest.MonkeyPatch.context() as patch:
            where = dict(vars(generation))
            _counted_calls(("_band_step",), counted, 0, where)
            patch.setattr(generation, "_band_step", where["_band_step"])
            generation._pushed_apart(*copy.deepcopy(handed))  # type: ignore[arg-type]
        assert counted[0] < 8 * rows, (rows, counted[0])
        if rows == 4000:
            built, names = _push_as_built()
            old = [0]
            _counted_calls(("_band_step",), old, 0, names)
            built(*copy.deepcopy(handed))  # type: ignore[operator]
            assert old[0] > 8 * rows, old[0]


# -- 3. the pooled placement --------------------------------------------------


def _placed_as_built() -> "tuple[object, dict]":
    return stage4_as_built.compiled(generation, stage4_as_built.POOLED_PLACED, "_pooled_numbers_placed")


def _decimal_codes(rows: int, codes: int, seed: int = 29) -> "list[str]":
    """Codes of one to three figures, a point and one or two figures, drawn by a Zipf law over ``codes`` ranks.

    Skeptic 2 of lane G4 measured `generate` on these (its `gen_dec.py`,
    seed 29): 1,000,000 rows over 60,000 codes took 13 to 22 minutes.
    """
    import bisect
    import random

    draw = random.Random(seed)
    names: "list[str]" = []
    seen: "dict[str, int]" = {}
    while len(names) < codes:
        whole = draw.randrange(1, 1000)
        places = draw.choice((1, 2))
        code = f"{whole}.{draw.randrange(10 ** places):0{places}d}"
        if code not in seen:
            seen[code] = 1
            names += [code]
    cumulative: "list[float]" = []
    total = 0.0
    for rank in range(codes):
        total += 1.0 / (rank + 1)
        cumulative += [total]
    cells: "list[str]" = []
    for _row in range(rows):
        cells += [names[bisect.bisect_left(cumulative, draw.random() * total)]]
        draw.random()
    return cells


class _Captured(Exception):
    """Raised by a spy once it holds what it was set to capture."""


def _placements_handed(
    folder: pathlib.Path, stem: str, cells: "list[str]", floor: int, codes: "list[str]", seeds: "tuple[int, ...]" = (0, 4)
) -> "list[tuple[object, ...]]":
    """What G8.3c's placement is handed while the twin of a one-column table is written, at ``seeds``."""
    described = kpi_shapes.describe(folder / stem, stem, _table({"value": cells}), floor, codes=codes)
    handed: "list[tuple[object, ...]]" = []

    def captured(*arguments: object) -> object:
        handed.extend([copy.deepcopy(arguments)])
        raise _Captured()

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_pooled_numbers_placed", captured)
        for seed in seeds:
            with pytest.raises(_Captured):
                kpi_shapes.twin_text(described, seed)
    return handed


def _placed(function: "object", handed: "tuple[object, ...]") -> "tuple[object, ...]":
    arguments = copy.deepcopy(handed)
    placed = function(*arguments)  # type: ignore[operator]
    return (list(placed.items()), list(arguments[4].items()), list(arguments[5].items()))  # type: ignore[attr-defined]


def _readings_beside_a_word() -> "list[str]":
    """One-decimal readings beside a word, seeded so that no moved offer lands the pool and the carried one is asked."""
    import random

    draw = random.Random("carried/48")
    cells = ["alpha"] * draw.randint(50, 400) + [f"{draw.gauss(7.0, 0.9):.1f}" for _row in range(draw.choice((1000, 2500)))]
    draw.choice((11, 20, 36))
    draw.shuffle(cells)
    return cells


_POOLS = {
    "anchored": ["alpha"] * 100 + ["100"] * 20 + [str(number) for number in range(200, 210) for _row in range(10)],
    "dwarfed": ["alpha"] * 100 + ["990"] * 20 + [str(number) for number in range(940, 950) for _row in range(10)],
    "pushed": ["alpha"] * 200 + ["48.0"] * 30 + [number for number in ("0.6", "20.1", "64.0", "90.8", "93.1") for _row in range(10)],
}


def test_each_pool_is_placed_where_the_placement_as_built_placed_it(tmp_path: pathlib.Path) -> None:
    """Pools beside labels and registers of decimal codes at floors 11 and 36: the same spellings, and the same used.

    Among them every offer is asked: the plain one, the moved ones and the
    one in which the groups carry each other's arrears, with its order.
    """
    built, _names = _placed_as_built()
    shapes = [(stem, cells, 11, []) for stem, cells in _POOLS.items()]
    shapes += [("readings", _readings_beside_a_word(), 20, [])]
    shapes += [("dec2500", _decimal_codes(2500, 1000), 11, ["value"]), ("dec3000", _decimal_codes(3000, 600), 36, ["value"])]
    asked: "dict[str, int]" = {"_pooled_offered": 0, "_pooled_carried": 0}
    with pytest.MonkeyPatch.context() as patch:
        for name in asked:
            shipped = getattr(generation, name)

            def counting(*arguments: object, _name: str = name, _shipped: object = shipped) -> object:
                asked[_name] += 1
                return _shipped(*arguments)  # type: ignore[operator]

            patch.setattr(generation, name, counting)
        placements = 0
        for stem, cells, floor, codes in shapes:
            for handed in _placements_handed(tmp_path, stem, cells, floor, codes):
                assert _placed(generation._pooled_numbers_placed, handed) == _placed(built, handed), stem
                placements += 1
    assert placements == 2 * len(shapes), placements
    assert asked["_pooled_carried"] >= 1 and asked["_pooled_offered"] > placements + 2, f"premise: {asked}"


def test_the_twin_of_a_decimal_register_is_the_twin_the_placement_as_built_wrote(tmp_path: pathlib.Path) -> None:
    """3,000 rows of decimal codes over 1,200 codes, seeds 0 and 4: the twin's bytes with either placement."""
    cells = _decimal_codes(3000, 1200)
    described = kpi_shapes.describe(tmp_path / "dec", "dec", _table({"value": cells}), 11, codes=["value"])
    ours = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_pooled_numbers_placed", _placed_as_built()[0])
        theirs = [kpi_shapes.twin_text(described, seed) for seed in (0, 4)]
    assert ours == theirs


def placement_questions(handed: "tuple[object, ...]", as_built: bool = False, cap: int = 0) -> int:
    """How many census forms the placement asks for on ``handed`` -- one for each spelling it offers, and its dressing's."""
    counted = [0]
    shipped = parsing.census_form

    def asking(*arguments: object) -> object:
        counted[0] += 1
        if cap and counted[0] > cap:
            raise _TooMuchWork(counted[0])
        return shipped(*arguments)  # type: ignore[arg-type]

    function = _placed_as_built()[0] if as_built else generation._pooled_numbers_placed
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(parsing, "census_form", asking)
        function(*copy.deepcopy(handed))  # type: ignore[operator]
    return counted[0]


def test_each_offer_asks_each_place_its_rules_once(tmp_path: pathlib.Path) -> None:
    """Decimal codes at 2,500, 5,000 and 10,000 rows: under 64 census forms a group; as built, over 700.

    The stepping is bounded at 2,048 places a group, so as built the
    questions grew with the groups times the places each stepped over,
    and those grew with the groups packed round the pool's mean until the
    bound: 987, 1,450 and 1,570 a group here.
    """
    for rows in (2500, 5000, 10000):
        handed = _placements_handed(tmp_path, f"q{rows}", _decimal_codes(rows, rows * 2 // 5), 11, ["value"], (0,))[0]
        groups = len(handed[2])  # type: ignore[arg-type]
        asked = placement_questions(handed, cap=64 * groups)
        assert asked < 64 * groups, (rows, groups, asked)
        if rows == 2500:
            assert placement_questions(handed, True) > 700 * groups, rows


def _held_back_of_a_million_rows() -> "list[str]":
    """The 46,581 codes the floor holds back of 1,000,000 rows of decimal codes over 60,000, on their own rows.

    Each of the 8,669 codes it publishes is kept on eleven rows, so the
    pool and the spellings around it are the million-row register's,
    on 258,274 rows.
    """
    cells = _decimal_codes(1000000, 60000)
    counts: "dict[str, int]" = {}
    for cell in cells:
        counts[cell] = counts.get(cell, 0) + 1
    kept: "list[str]" = []
    for code in counts:
        kept += [code] * min(counts[code], 11)
    return kept


def test_the_pool_of_a_million_row_register_is_placed_in_a_bounded_number_of_questions(tmp_path: pathlib.Path) -> None:
    """The 46,581 held-back codes of 1,000,000 rows of decimal codes: under 16 census forms a group; as built, stopped there.

    As built each group stepped out past the places the groups before it
    took, up to 2,048 of them: 763 s of `generate` on a quiet machine and
    1,296 s under load (skeptic 2 of lane G4). Each offer now asks each
    place its rules once.
    """
    cells = _held_back_of_a_million_rows()
    handed = _placements_handed(tmp_path, "million", cells, 11, ["value"], (0,))[0]
    groups = len(handed[2])  # type: ignore[arg-type]
    assert groups == 46581, f"premise: {groups} groups"
    asked = placement_questions(handed, cap=16 * groups)
    assert asked < 16 * groups, (groups, asked)
    with pytest.raises(_TooMuchWork):
        placement_questions(handed, True, cap=16 * groups)

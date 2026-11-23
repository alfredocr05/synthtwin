"""A column whose values are written two ways: `45%` beside `45.0%` (lane ZOO-Y, plan P4-D517).

A health table is full of such columns: a percent typed `45%` by one
person and `45.0%` by another, a temperature `98` beside `98.6`, a
weight `78` beside `78.4`. The column publishes more different
spellings than different numbers, and the twin owes the difference.

MEASURED BEFORE THIS (lane ZOO-X's data-type zoo, 20,000 rows, the
floor on): a percent column written both ways owed 84 spellings, and
G6.6's identity walk -- which raised every repeated cell in turn --
spent all of them on the first repeated values it met, writing up to
66 zeros in front of one value (`0000...006.8%`, 67 cells). And the
affixed core's push (`generation._pushed_apart`) parted its collisions
by moving WHOLE-valued heaps of about ninety cells one whole unit each
along the band: the column's 95th percentile came back 85 against a
published 69.7, its high tail heaped on the whole numbers 85 to 94.

THE TWO RULES (method G6.5 and G6.5a, as amended):

1. the owed spellings are spread one a value before two, at an even
   stride over the repeated values (`_identity_walk`);
2. on a column that writes some cells with no point, a collision on a
   WHOLE value is not pushed: whole values there are the heaps the
   point-free cells share, and pushing one moves every heap between it
   and a free whole number by a unit (`_pushed_apart`).

Each case below goes red on the rule as it stood (`stage4_as_built`).
"""

from __future__ import annotations

import collections
import copy
import pathlib
import random
import re
import types

import pytest

import kpi_shapes
import stage4_as_built
from synthtwin import generation

# The spread's handed walk: three values, each written four times with one
# spelling, a decimal column, three identities owed.
_SPREAD = (
    [1.5, 1.5, 1.5, 1.5, 2.5, 2.5, 2.5, 2.5, 3.5, 3.5, 3.5, 3.5],
    ["decimal"] * 12,
    ["1.5"] * 4 + ["2.5"] * 4 + ["3.5"] * 4,
    [-1] * 12,
    [-1] * 12,
    [""] * 12,
    ["minus"] * 12,
    [False] * 12,
    False,
    3,
)


def _walk_as_built() -> object:
    return stage4_as_built.compiled(generation, stage4_as_built.IDENTITY_WALK, "_identity_walk")[0]


def _zeros(cell: str) -> int:
    """The zeros written in front of a cell's first figure that is not a zero, past its sign."""
    body = cell.lstrip("+-(")
    found = re.match(r"0+(?=\d)", body)
    return len(found.group()) if found else 0


def test_the_owed_spellings_go_one_a_value_before_two() -> None:
    """Three values, four cells each, three spellings owed: one cell of each value raised, never two of one."""
    ours = generation._identity_walk(*copy.deepcopy(_SPREAD))  # type: ignore[arg-type]
    raised = [index for index in range(12) if ours[index] != _SPREAD[2][index]]
    assert len(raised) == 3, ours
    assert sorted({_SPREAD[0][index] for index in raised}) == [1.5, 2.5, 3.5], ours
    assert all(_zeros(ours[index]) == 1 for index in raised), ours
    assert len({ours[index] for index in range(12)}) == 6
    theirs = _walk_as_built()(*copy.deepcopy(_SPREAD))  # type: ignore[operator]
    assert sorted({_SPREAD[0][index] for index in range(12) if theirs[index] != _SPREAD[2][index]}) == [1.5], (
        "premise: the walk as built spends every owed spelling on the first value"
    )


def test_a_round_takes_its_values_at_an_even_stride() -> None:
    """Eight repeated values, two spellings owed: the two raised stand apart, neither at the low end."""
    holds = [float(value) for value in range(8) for _copy in range(2)]
    handed = (
        holds, ["decimal"] * 16, [f"{value:.1f}" for value in holds], [-1] * 16, [-1] * 16, [""] * 16,
        ["minus"] * 16, [False] * 16, False, 2,
    )
    ours = generation._identity_walk(*copy.deepcopy(handed))  # type: ignore[arg-type]
    raised = sorted(holds[index] for index in range(16) if ours[index] != handed[2][index])
    assert raised == [2.0, 6.0], raised


def test_the_unmarked_cells_are_spread_before_a_marked_one_is_raised() -> None:
    """Two values written grouped and bare: the bare duplicates give their spellings first, so no mark is lost."""
    holds = [1234.0] * 4 + [5678.0] * 4
    marks = [",", "", ",", ""] * 2
    base = ["1,234.0", "1234.0", "1,234.0", "1234.0", "5,678.0", "5678.0", "5,678.0", "5678.0"]
    handed = (holds, ["decimal"] * 8, base, [-1] * 8, [-1] * 8, marks, ["minus"] * 8, [False] * 8, False, 2)
    ours = generation._identity_walk(*copy.deepcopy(handed))  # type: ignore[arg-type]
    assert all(ours[index] == base[index] for index in range(8) if marks[index]), ours
    assert len({ours[index] for index in range(8)}) == 6, ours


def _mixed_percents(rows: int, seed: int) -> "list[str]":
    """Percents written `45%` or `45.0%`, as two people type them."""
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(rows):
        value = min(max(draw.gauss(45, 15), 0), 100)
        cells += [f"{value:.1f}%" if draw.random() < 0.5 else f"{round(value)}%"]
    return cells


def _table(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


def test_a_percent_column_written_two_ways_writes_no_cell_with_two_invented_zeros(tmp_path: pathlib.Path) -> None:
    """2,000 rows of `45%` beside `45.0%`: at most one zero in front of any twin cell; as built, a heap of them."""
    described = kpi_shapes.describe(tmp_path / "pct", "pct", _table(_mixed_percents(2000, 7)), 11, measured=["value"])
    ours = kpi_shapes.twin_text(described, 0).split("\n")[1:]
    zeros = collections.Counter(_zeros(cell.strip('"')) for cell in ours if cell)
    assert max(zeros) <= 1, zeros
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_identity_walk", _walk_as_built())
        theirs = kpi_shapes.twin_text(described, 0).split("\n")[1:]
    assert max(_zeros(cell.strip('"')) for cell in theirs if cell) >= 3, "premise: as built, zeros heap on one value"
    # The count of different spellings is met either way: only where the spellings stand moved.
    assert len({cell for cell in ours if cell}) == len({cell for cell in theirs if cell})


def _whole_heaps() -> "tuple[object, ...]":
    """A push the walks leave on a column writing some cells with no point: whole heaps beside fractions.

    Twelve whole values 10 to 21 each a stratum, two strata sharing 15,
    and the fractions 21.1 to 21.9 above them, so the only free whole
    point is 22: the push as built moves every whole stratum from 16 to
    21 one unit up to make room.
    """
    values = [float(value) for value in range(10, 16)] + [15.0] + [float(value) for value in range(16, 22)]
    values += [21.0 + step / 10 for step in range(1, 10)] + [25.0]
    texts = [generation._grid_text(value, 1) for value in values]
    held: "dict[str, int]" = {}
    for text in texts:
        held[text] = held.get(text, 0) + 1
    facts = types.SimpleNamespace(
        n_distinct_values=len(values), empty_edges=(), kept_stand_ins=(), integer_valued=False,
        numeric_styles={"plain": 13, "decimal": 9},
    )
    layout = types.SimpleNamespace(bands=("positive",) * len(values))
    return (facts, layout, (values[0], values[-1]), values, texts, held, 1, True)


def test_a_whole_heap_is_not_pushed_on_a_column_writing_cells_with_no_point() -> None:
    """The collision on 15 stays (the heaps stand where the ladder put them); as built, six heaps move a unit up."""
    handed = _whole_heaps()
    ours = generation._pushed_apart(*copy.deepcopy(handed))  # type: ignore[arg-type]
    assert ours[0] == handed[3], ours[0]
    built = stage4_as_built.compiled(generation, stage4_as_built.PUSHED_APART, "_pushed_apart")[0]
    theirs = built(*copy.deepcopy(handed))  # type: ignore[operator]
    moved = [place for place in range(len(handed[3])) if theirs[0][place] != handed[3][place]]  # type: ignore[index]
    assert len(moved) >= 6 and all(handed[3][place] == int(handed[3][place]) for place in moved), (  # type: ignore[index]
        "premise: as built, the push moves the whole heaps", theirs[0])

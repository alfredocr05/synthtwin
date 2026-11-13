"""Lane H2: the packing walk reads together the counts one margin owes (`generation._owed_together`).

A column of signed changes -- gauss(0, 40) written `+3.25`, `+12`, `12`,
`-1.50` and `-4` -- stalled `synthtwin generate` in `_style_strata` at
4,000 and 5,000 rows (lane H1's build report, 2026-10-16): the style
question it asks has no answer, because `leading_plus` and `plain` owe
more rows together than the made-up values that can be written without a
point hold, and no condition the walk read on entering a cell read two
counts together. So the cell answering for `leading_plus` was offered
every fill of 397 rows out of 20 sizes -- about 7.6e11 partial fills --
each refused only when it had taken more than 388 rows: 24.2 million
reserve readings in five minutes inside one cell. Condition 6 refuses the
question on entering the first cell.
"""

import importlib.util
import pathlib
import random
import sys

import pytest

import stage4_as_built
from synthtwin import generation

# The style question that column's twin asks, at 4,000 and 5,000 rows:
# the published counts in `contract.NUMERIC_STYLES` order, then the
# copies of each group size under the styles its made-up value may wear,
# as bits of that order -- 56 a decimal or an exponent only, 59 every
# style but `leading_plus`, 63 every style.
_SIGNED_CHANGES = {
    4000: (
        [1028, 0, 397, 2575, 0, 0],
        {
            56: {1: 2468, 2: 12, 3: 4, 4: 5, 5: 3, 6: 1, 7: 1, 10: 1, 11: 2},
            59: {1: 33, 2: 3, 6: 1, 19: 1, 24: 1, 25: 8, 26: 7, 27: 6, 29: 1, 30: 1, 34: 1},
            63: {
                1: 16, 2: 13, 3: 5, 4: 3, 5: 3, 6: 1, 7: 1, 8: 1, 9: 3, 10: 4,
                11: 4, 12: 5, 13: 7, 14: 1, 15: 2, 16: 1, 28: 5, 29: 1, 31: 1, 32: 2,
            },
        },
    ),
    5000: (
        [1287, 0, 491, 3222, 0, 0],
        {
            56: {1: 2940, 2: 41, 3: 10, 4: 5, 5: 13, 6: 7, 8: 1, 9: 1, 10: 3, 11: 1, 13: 1, 16: 1, 45: 1},
            59: {1: 30, 2: 6, 3: 1, 29: 1, 32: 1, 33: 4, 34: 7, 35: 6, 36: 3, 37: 3, 43: 1},
            63: {
                1: 20, 2: 13, 3: 6, 4: 6, 5: 2, 6: 5, 7: 10, 8: 8, 9: 5, 10: 3, 12: 3,
                13: 1, 14: 1, 17: 1, 18: 1, 31: 2, 33: 1, 35: 1, 39: 1, 45: 2, 47: 1,
            },
        },
    ),
}

# The reserve readings a test lets one walk take before it fails it, so
# a walk that would not end fails at once rather than holding the suite.
_READINGS_AT_MOST = 20000


class _Read(Exception):
    """The walk passed the reserve readings a test allows it."""


def _style_question(rows: int) -> "tuple[tuple[int, ...], list[int], list[int]]":
    """The groups, published style counts and permitted styles of the signed-change twin at ``rows``."""
    quotas, table = _SIGNED_CHANGES[rows]
    groups: "list[int]" = []
    allowed: "list[int]" = []
    for mask in sorted(table):
        for size in sorted(table[mask]):
            groups += [size for _each in range(table[mask][size])]
            allowed += [mask for _each in range(table[mask][size])]
    return tuple(groups), quotas, allowed


def _walked(
    question: "tuple[tuple[int, ...], list[int], list[int]]",
) -> "tuple[list[int] | None, dict[str, int], bool]":
    """`_allotted`'s answer to ``question``, the states it entered, the fills it was asked for and its reserve readings, and whether it ended.

    The walk's own functions are wrapped by counters that pass each call
    straight through, and put back however the walk ends; a walk past
    `_READINGS_AT_MOST` readings is stopped and reported as not ended.
    """
    seen = {"states": 0, "fills": 0, "readings": 0}
    room = generation._cell_room
    offered = generation._cell_next
    read = generation._reserves_met

    def entering(*given):  # type: ignore[no-untyped-def]
        seen["states"] += 1
        return room(*given)

    def offering(*given):  # type: ignore[no-untyped-def]
        seen["fills"] += 1
        return offered(*given)

    def reading(*given):  # type: ignore[no-untyped-def]
        seen["readings"] += 1
        if seen["readings"] > _READINGS_AT_MOST:
            raise _Read(f"the walk passed {_READINGS_AT_MOST} reserve readings")
        return read(*given)

    generation._cell_room = entering  # type: ignore[assignment]
    generation._cell_next = offering  # type: ignore[assignment]
    generation._reserves_met = reading  # type: ignore[assignment]
    try:
        answer = generation._allotted(*question)
    except _Read:
        return None, seen, False
    finally:
        generation._cell_room = room  # type: ignore[assignment]
        generation._cell_next = offered  # type: ignore[assignment]
        generation._reserves_met = read  # type: ignore[assignment]
    return answer, seen, True


def counts_together_measures() -> "dict[str, int]":
    """`K-S4-18`: the states, fills and reserve readings of the signed-change style question at 4,000 and 5,000 rows.

    Machine-free counts of work. A walk stopped past `_READINGS_AT_MOST`
    readings records its readings there, past the ledger's 0.
    """
    value: "dict[str, int]" = {}
    for rows in sorted(_SIGNED_CHANGES):
        answer, seen, ended = _walked(_style_question(rows))
        value[f"states_{rows}_rows"] = seen["states"]
        value[f"fills_{rows}_rows"] = seen["fills"]
        value[f"reserve_readings_{rows}_rows"] = seen["readings"]
        value[f"answered_{rows}_rows"] = int(ended and answer is not None)
    return value


@pytest.mark.parametrize("rows", [4000, 5000])
def test_a_signed_change_column_s_style_question_is_refused_on_entering(rows: int) -> None:
    """No packing exists, and the walk says so in its first state, offering no fill.

    Mutation, run: without condition 6 the walk passes 20,000 reserve
    readings inside the cell answering for `leading_plus` (on 36ad3061 it
    read 24.2 million in 300 s at 4,000 rows and did not finish).
    """
    answer, seen, ended = _walked(_style_question(rows))
    assert ended, f"the walk passed {_READINGS_AT_MOST} reserve readings: {seen}"
    assert answer is None
    assert seen == {"states": 1, "fills": 0, "readings": 0}, seen


@pytest.mark.parametrize(
    ("rows", "owed", "held"), [(4000, 1425, 1416), (5000, 1778, 1689)]
)
def test_the_point_free_counts_owe_more_rows_than_can_wear_them(
    rows: int, owed: int, held: int
) -> None:
    """Why there is no answer: `plain`, `leading_zero` and `leading_plus` owe more rows than the made-up values that can be written without a point hold."""
    groups, quotas, allowed = _style_question(rows)
    point_free = 0b111
    holding = 0
    for place in range(len(groups)):
        if allowed[place] & point_free:
            holding += groups[place]
    assert (quotas[0] + quotas[1] + quotas[2], holding) == (owed, held)
    assert sum(groups) == sum(quotas) == rows


def _nested_question(
    draw: random.Random,
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """A small style question of nested permissions, as `_style_strata` asks: drawn from a filling, then a few rows moved between two counts."""
    cells = draw.randint(2, 6)
    chain = list(range(cells))
    draw.shuffle(chain)
    groups: "list[int]" = []
    allowed: "list[int]" = []
    quotas = [0 for _each in range(cells)]
    for _each in range(draw.randint(1, 12)):
        size = draw.randint(1, 6)
        depth = draw.randint(1, cells)
        mask = 0
        for cell in chain[cells - depth:]:
            mask = mask | (1 << cell)
        home = chain[cells - draw.randint(1, depth)]
        groups += [size]
        allowed += [mask]
        quotas[home] += size
    if draw.random() < 0.7:
        giver, taker = draw.sample(range(cells), 2)
        moved = min(quotas[giver], draw.randint(1, 3))
        quotas[giver] -= moved
        quotas[taker] += moved
    return (
        tuple(groups),
        [(quotas, list(range(cells))), ([sum(quotas)], [0 for _each in range(cells)])],
        allowed,
    )


def test_seeded_style_questions_are_answered_as_the_walk_as_built_answered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """3,000 seeded style questions: the same answer as 493f6f8's walk, never more states, and fewer where condition 6 refuses.

    Condition 6 is a necessary condition, so it passes over only states
    holding no answer; the walk's order, and so its first complete
    filling, is the one method G9.5 fixes.
    """
    built, names = stage4_as_built.compiled(
        generation, stage4_as_built.ALLOTTED_OVER, "_allotted_over"
    )
    old_states = [0]
    asked_old = names["_cell_room"]

    def counting_old(*given):  # type: ignore[no-untyped-def]
        old_states[0] += 1
        return asked_old(*given)

    names["_cell_room"] = counting_old
    new_states = [0]
    asked = generation._cell_room

    def counting(*given):  # type: ignore[no-untyped-def]
        new_states[0] += 1
        return asked(*given)

    monkeypatch.setattr(generation, "_cell_room", counting)
    draw = random.Random(20261017)
    refused = fewer = 0
    for _case in range(3000):
        question = _nested_question(draw)
        old_states[0] = new_states[0] = 0
        expected = built(*question)  # type: ignore[operator]
        assert generation._allotted_over(*question) == expected, question
        assert new_states[0] <= old_states[0], (question, old_states[0], new_states[0])
        fewer += new_states[0] < old_states[0]
        refused += expected is None
    assert refused > 300 and fewer > 30, (refused, fewer)


def _sweep_driver() -> object:
    """tools/measurements/kpi_packing_sweep.py, loaded (it measures nothing on import); sys.path as it was."""
    place = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_packing_sweep.py"
    loaded = importlib.util.spec_from_file_location("kpi_packing_sweep_here", place)
    assert loaded is not None and loaded.loader is not None
    module = importlib.util.module_from_spec(loaded)
    was = tuple(sys.path)
    try:
        loaded.loader.exec_module(module)
    finally:
        sys.path[:] = was
    return module


def test_the_sweep_counts_only_twins_finished_in_under_its_limit() -> None:
    """K-S4-19's count is of twins that took less than 30 s, never of every twin that ended.

    Codex's review of lane H2 (2026-10-18): the driver counted a twin as
    finished whenever `generate` returned, so where no alarm stops it
    (a platform without SIGALRM) a 40-second twin counted toward
    `sweep_finished_within_30_s`. One late twin beside 29 quick ones is
    now 29 finished, its 40 s kept as the slowest; a twin at exactly
    the limit is not under it; a twin the alarm stopped stands at the
    limit and is not counted.
    """
    driver = _sweep_driver()
    tally = getattr(driver, "sweep_tally")
    assert getattr(driver, "LIMIT_SECONDS") == 30
    assert tally([40.0] + [0.5] * 29) == (29, 40.0)
    assert tally([29.99, 30.0, 1.25]) == (2, 30.0)
    assert tally([None, 2.5]) == (1, 30.0)
    assert tally([0.66, 2.6]) == (2, 2.6)

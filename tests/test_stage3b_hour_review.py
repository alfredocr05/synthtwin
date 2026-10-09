"""THE HOUR'S REVIEW (landing 3b.2-H, lane T2, plan P4-D371): Codex's four items, each reproduced.

Codex reviewed the landing once (2026-10-08) and raised four items; each
is reproduced here on the review's own scenario, red on the head it
reviewed (b3fb647), and fixed:

* item 3 -- PUT BACK (method G7.3g step 6) sorted and filtered every run
  again for each size before its first merge, so a clock state of one run
  of each size 1 to `k` beside `k(k-1)/2` alone did `k` times the work
  of one sort: `test_put_back_sorts_its_runs_once`.

Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import builtins

import pytest

from synthtwin import generation

DAY = 86400
_MONDAY = 19723  # 2024-01-01, a Monday


# -- item 3: PUT BACK's runs, sorted once ---------------------------------------


def _put_back_state(size: int) -> "tuple[generation._WeekdayPass, int]":
    """Codex's family: one run of each size 1 to `size` -- that many ranks on one
    second each -- beside `size * (size - 1) / 2` ranks alone, `size**2` movable
    ranks in one gap, seven seconds apart from 08:00 of a Monday; and how many
    runs there are."""
    sizes = list(range(1, size + 1)) + [1] * (size * (size - 1) // 2)
    ordinals: "list[int]" = []
    place = _MONDAY * DAY + 8 * 3600
    for each in sizes:
        place = place + 7
        if place % DAY == 0:
            place = place + 1
        ordinals += [place] * each
    rows = len(ordinals)
    state = generation._WeekdayPass(
        moved=list(ordinals), held={}, where=tuple(0 for _hour in range(24)), facts=None,  # type: ignore[arg-type]
        word="", widths=False, kinds={}, holes=frozenset(), lows=[ordinals[0]] * rows,
        highs=[ordinals[-1]] * rows, keep_units=True, unit=3600, step=1, day=DAY, bins="hour",
        period=24, keeps="day",
    )
    for ordinal in state.moved:
        generation._weekday_tally(state.held, ordinal, 1)
        generation._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state, len(sizes)


def _sorted_by_put_back(monkeypatch: pytest.MonkeyPatch, size: int) -> "tuple[int, int, bool]":
    """How many elements PUT BACK hands to `sorted` on Codex's state of `size`,
    how many runs the state holds, and whether the one excess was restored.
    A count of operations, not of seconds: the same on any machine."""
    state, runs = _put_back_state(size)
    rows = len(state.moved)
    count = generation._weekday_count(state)
    seen = [0]

    def counting(values, *arguments, **named):  # type: ignore[no-untyped-def]
        found = builtins.sorted(values, *arguments, **named)
        seen[0] = seen[0] + len(found)
        return found

    monkeypatch.setattr(generation, "sorted", counting, raising=False)
    try:
        generation._clock_count_put_back(
            state, 0, rows - 1, [False] * rows, count - 1, tuple(range(7))
        )
    finally:
        monkeypatch.delattr(generation, "sorted")
    return seen[0], runs, generation._weekday_count(state) == count - 1


def test_put_back_sorts_its_runs_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3. The written seconds one too many, one merge restores them;
    before it, PUT BACK may read each run a bounded number of times whatever
    how many sizes the runs come in. b3fb647 handed `sorted` 33,660 elements
    for the 820 runs of `size` 40 (41 a run) and 262,520 for the 3,240 of
    `size` 80 (81 a run), growing as the square root of the rows; sorted once,
    they cost two readings a run at both sizes (1,640 and 6,480)."""
    for size in (40, 80):
        elements, runs, restored = _sorted_by_put_back(monkeypatch, size)
        assert restored, size
        assert elements <= 3 * runs, (size, elements, runs)

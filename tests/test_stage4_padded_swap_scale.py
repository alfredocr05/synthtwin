"""Stage 4, lane H1: the padded exchange works in time that grows with the rows (plan P4-D402).

`generation._padded_style_swaps` moves the leading-zero style onto the
values a published field width can hold. A numeric column reaches it
only where its description publishes `pad_widths` -- postal codes,
record numbers, zero-padded procedure and laboratory codes -- and on
those columns generate grew x3.0 to x3.4 a doubling of the rows where
every other column grew about x2.0: measured on 68dae22f, a postal
code column took 76 s of generate at 200,000 rows, and fitted on lane
B0's measurement window it projects to about 3,600 s at two million.
Four walks asked for a partner by scanning the column from its first
cell every time: `_first_giver`, once per cell of every whole-value
trial; `give_up`, once per cell-by-cell hand-over; the overflow pass,
once per cell no published width holds; and `_point_free_form_worn`,
which recounted every style handed in for each of those cells left
without a partner.

They now walk forward over structures that give the same answer: a
roster of givers per style taken with a next-alive list, a reach per
style for each trial, one cursor per wearing key in the overflow pass,
and the point-free form asked once per key for the call. Nothing about
the exchange's RULE changed, so every partner chosen is the one the
scan chose and every twin is byte-identical; `tools/reference` mirrors
no padded swap, and its plus exchange states the rule the forward walk
still meets, so no oracle, vector or METHOD text moved.

This file holds 68dae22f's `_padded_style_swaps` and `_first_giver` as
its ORACLE, comments and docstrings dropped and nothing else changed,
and requires:

(a) the same answers over 2,000 seeded cases and four large ones of
    12,500 to 25,000 cells, and the comparison seen to fail on four
    mutants of the walk that would each pick a different partner;
(b) predicate work, counted without a clock, that grows with the rows:
    `_pad_need`, `_can_wear` and `_carries_plainly` calls at 100,000
    cells against 50,000 at most x2.2, where the oracle's own count
    grows at least x3.0 (so the measure is seen to catch the defect);
(c) `_point_free_form_worn` still asked by name, so swapping it in
    changes the twin, as `tests/test_stage3b_width.py` and
    `tools/measurements/kpi_cost_rule.py` rely on;
(f) the walk's own lines, counted under `sys.settrace`, growing at most
    x2.2 a doubling on four shapes, and red on three mutants that pick
    the same partners but step over the same cells again (a trial from
    each roster's start, the overflow cursor put back to cell 0, a
    next-alive list that never shortens its links); and the point-free
    form asked at most once per wearing key, red on asking it per cell
    (lane H1's repair round 1: skeptic 1's items 1 and 2, Codex's
    condition).

THE PLUS EXCHANGE BESIDE IT (`generation._plus_style_swaps`) is the
same rescan: every giver walked the takers from the first, stepping over
those already given a style. Counted on the arguments of a signed column
the style walk left short by a tenth of its non-negative decimals, its
steps grew x4.0 a doubling, 783,131 at 50,000 rows and 12,592,672 at
200,000, so it walks forward too, and this file holds its 68dae22f text
as a second oracle with the same three demands: (d) the same answers
over seeded and large cases, failing on two mutants; (e) the lines it
runs growing with the rows.

`padded_swap_measures` is K-S4-16's measure (tests/test_kpi_ledger.py).
"""

from __future__ import annotations

import inspect
import pathlib
import random
import sys

import pytest

import fixtures
from synthtwin import contract, generation, profile, reading, rendering, taxonomy

# The predicate functions every walk of the exchange asks, counted by
# name under `sys.setprofile`: work the walk does, whatever the clock.
PREDICATES = ("_pad_need", "_can_wear", "_carries_plainly")
LINEAR_AT_MOST = 2.2
SQUARE_AT_LEAST = 3.0
SEEDED_CASES = 2_000


# -- the oracle: 68dae22f's walk, comments and docstrings dropped -------------


def _as_built_first_giver(
    moved: "list[str]",
    holds: "list[float]",
    reserved: "dict[int, int]",
    taken: "dict[int, int]",
    width: int,
    taking: str,
    whole_column: bool,
) -> int:
    for other in range(len(moved)):
        if moved[other] != "leading_zero":
            continue
        if other in reserved or other in taken:
            continue
        if generation._pad_need(holds[other], whole_column) < width:
            continue
        if not generation._can_wear(taking, holds[other], whole_column):
            continue
        return other
    return -1


def _as_built_padded_style_swaps(
    styles: "list[str]",
    holds: "list[float]",
    widths: "dict[str, int]",
    pinned: "list[int]",
    whole_column: bool,
    far: "tuple[int, tuple[bool, ...]]" = (0, ()),
) -> "list[str]":
    quotas: dict[int, int] = {}
    for key in sorted(widths):
        if key == contract.WITHHELD:
            continue
        quotas[int(key)] = widths[key]
    if not quotas:
        return styles
    moved = list(styles)

    def need_of(index: int) -> int:
        return generation._pad_need(holds[index], whole_column)

    def receivable(index: int, other: str) -> bool:
        return generation._can_wear(other, holds[index], whole_column)

    eligible: "list[int]" = []
    for index in range(len(moved)):
        if moved[index] == "leading_zero":
            continue
        if not generation._carries_plainly(holds[index], whole_column):
            continue
        eligible += [index]
    reserved: "dict[int, int]" = {}
    spent: "dict[int, int]" = {}

    def give_up(width: int, taking: str) -> int:
        for other in range(len(moved)):
            if moved[other] != "leading_zero" or other in reserved:
                continue
            if need_of(other) < width:
                continue
            if not receivable(other, taking):
                continue
            return other
        return -1

    def hand_over(index: int, width: int) -> bool:
        partner = give_up(width, moved[index])
        if partner < 0:
            return False
        moved[partner] = moved[index]
        moved[index] = "leading_zero"
        spent[index] = 1
        reserved[index] = width
        return True

    for width in sorted(quotas):
        owing = quotas[width]
        for index in range(len(moved)):
            if owing < 1:
                break
            if moved[index] != "leading_zero" or index in reserved:
                continue
            if need_of(index) >= width:
                continue
            reserved[index] = width
            owing = owing - 1
        for group in generation._eligible_groups(eligible, moved, holds, spent):
            if owing < 1:
                break
            if len(group) > owing:
                continue
            if need_of(group[0]) >= width:
                continue
            trial: "list[tuple[int, int]]" = []
            taken: "dict[int, int]" = {}
            for index in group:
                partner = _as_built_first_giver(
                    moved, holds, reserved, taken, width, moved[index], whole_column
                )
                if partner < 0:
                    trial = []
                    break
                taken[partner] = 1
                trial += [(index, partner)]
            if not trial:
                continue
            for index, partner in trial:
                moved[partner] = moved[index]
                moved[index] = "leading_zero"
                spent[index] = 1
                reserved[index] = width
                owing = owing - 1
        for index in eligible:
            if owing < 1:
                break
            if index in spent or moved[index] == "leading_zero":
                continue
            if need_of(index) >= width:
                continue
            if not hand_over(index, width):
                break
            owing = owing - 1
    widest = 0
    for width in quotas:
        if width > widest:
            widest = width
    for index in range(len(moved)):
        if moved[index] != "leading_zero" or index in reserved:
            continue
        if need_of(index) < widest:
            continue
        swapped = False
        for other in range(len(moved)):
            if moved[other] == "leading_zero" or other in reserved:
                continue
            if not generation._carries_plainly(holds[other], whole_column):
                continue
            if need_of(other) >= widest:
                continue
            if not generation._can_wear(moved[other], holds[index], whole_column):
                continue
            moved[index] = moved[other]
            moved[other] = "leading_zero"
            spent[other] = 1
            reserved[other] = widest
            swapped = True
            break
        if swapped:
            continue
        given = generation._point_free_form_worn(styles, holds[index], whole_column)
        if not given and generation._proven_side_holds(holds[index], far, whole_column):
            given = "plain"
        if given:
            moved[index] = given
    return moved


# -- the cases ------------------------------------------------------------------

# One case is the walk's arguments: styles, values, the published
# census, the pinned cells, whether the column is whole, and `far`.
Case = "tuple[list[str], list[float], dict[str, int], list[int], bool, tuple[int, tuple[bool, ...]]]"


def _seeded_case(number: int) -> Case:
    """One adversarial case: five shapes of value, every numeric style, 1-4 widths, withheld counts and far sides."""
    draw = random.Random(f"h1/padded/{number}")
    rows = draw.choice([3, 8, 20, 60, 200, 500])
    whole = draw.random() < 0.75
    mode = draw.choice(["overflow", "groups", "mixed", "signs", "narrow"])
    kinds = draw.sample(list(contract.NUMERIC_STYLES), draw.randint(1, len(contract.NUMERIC_STYLES)))
    if "leading_zero" not in kinds:
        kinds += ["leading_zero"]
    low, high = {
        "overflow": (1000, 999999),
        "groups": (0, 400),
        "mixed": (-9999, 99999),
        "signs": (-999, 999),
        "narrow": (0, 99),
    }[mode]
    distinct = max(1, rows // draw.choice([1, 2, 5, 25, 100]))
    pool = [draw.randint(low, high) for _value in range(distinct)]
    values: "list[float]" = [float(value) for value in pool]
    if not whole:
        values += [round(draw.uniform(-80, 900), draw.choice([1, 2, 3])) for _value in range(draw.randint(1, 6))]
    holds = [draw.choice(values) for _cell in range(rows)]
    padded = draw.choice([0.05, 0.3, 0.6, 0.9, 1.0])
    styles = [("leading_zero" if draw.random() < padded else draw.choice(kinds)) for _cell in range(rows)]
    widths: "dict[str, int]" = {}
    for _width in range(draw.randint(1, 4)):
        widths[str(draw.randint(1, 8))] = draw.randint(1, max(1, rows // draw.choice([1, 2, 4, 10])))
    if draw.random() < 0.15:
        widths[contract.WITHHELD] = draw.randint(1, 20)
    pinned = sorted(draw.sample(range(rows), min(rows, draw.randint(0, 4))))
    far: "tuple[int, tuple[bool, ...]]" = (0, ())
    if draw.random() < 0.4:
        far = (draw.randint(1, 7), tuple(draw.sample([True, False], draw.randint(1, 2))))
    return styles, holds, widths, pinned, whole, far


def _code_column(rows: int, padded: float, seed: int, low: int, high: int, kinds: "list[str]") -> "tuple[list[str], list[float]]":
    """``rows`` cells of 1,500 codes between ``low`` and ``high``, ``padded`` of them wearing the leading zero."""
    draw = random.Random(f"h1/codes/{seed}")
    codes = [float(draw.randint(low, high)) for _code in range(1500)]
    holds = [draw.choice(codes) for _cell in range(rows)]
    styles = [("leading_zero" if draw.random() < padded else draw.choice(kinds)) for _cell in range(rows)]
    return styles, holds


def _postal_case(rows: int, padded: float = 0.14) -> Case:
    """A postal-code column: five-figure codes, ``padded`` of the cells padded, one width of five."""
    styles, holds = _code_column(rows, padded, 7, 0, 99999, ["plain"])
    narrow = 0
    for value in holds:
        if value < 10000.0:
            narrow = narrow + 1
    return styles, holds, {"5": min(narrow, int(padded * rows))}, [], True, (0, ())


def _large_cases() -> "list[Case]":
    """Four cases of 12,500 to 25,000 cells: postal codes, a column overflowing two widths, and signed codes."""
    overflow_styles, overflow_holds = _code_column(12_500, 0.3, 3, 100, 999999, ["plain"])
    signed_styles, signed_holds = _code_column(25_000, 0.1, 4, -99999, 99999, ["plain", "leading_plus"])
    return [
        _postal_case(12_500),
        _postal_case(25_000),
        (overflow_styles, overflow_holds, {"4": 625, "6": 1250}, [], True, (0, ())),
        (signed_styles, signed_holds, {"5": 2083}, [], True, (0, ())),
    ]


def _answer(walk: object, case: Case) -> "list[str]":
    """The walk's styles for one case, handed fresh lists so no answer leaks into the next."""
    styles, holds, widths, pinned, whole, far = case
    return walk(list(styles), list(holds), dict(widths), list(pinned), whole, far)  # type: ignore[operator]


# -- (a) the same answers, and the comparison failing on its mutants ----------


def test_the_walk_answers_every_seeded_case_as_68dae22f_did() -> None:
    """2,000 seeded cases: every style the product returns is the oracle's, and the cases do move styles."""
    moved = 0
    for number in range(SEEDED_CASES):
        case = _seeded_case(number)
        expected = _answer(_as_built_padded_style_swaps, case)
        assert _answer(generation._padded_style_swaps, case) == expected, f"case {number}"
        for before, after in zip(case[0], expected):
            if before != after:
                moved = moved + 1
    assert moved > 10_000, f"premise: the seeded cases move styles ({moved})"


def test_the_walk_answers_every_large_case_as_68dae22f_did() -> None:
    """Four cases of 12,500 to 25,000 cells, each moving thousands of styles, answered as the oracle answers them."""
    for case in _large_cases():
        expected = _answer(_as_built_padded_style_swaps, case)
        assert _answer(generation._padded_style_swaps, case) == expected, f"{len(case[0])} cells"
        changed = 0
        for before, after in zip(case[0], expected):
            if before != after:
                changed = changed + 1
        assert changed > 1000, f"premise: {len(case[0])} cells move styles ({changed})"


# Each mutant is one edit of the product's own text: the walk it names,
# done the way that picks a different partner. The comparison above must
# see every one.
MUTANTS = {
    "the reach kept from one trial to the next": [
        ('            reach: "dict[str, int]" = {}\n', ""),
        ("        owing = quotas[width]\n", '        owing = quotas[width]\n        reach: "dict[str, int]" = {}\n'),
    ],
    "a giver spoken for in the trial not skipped": [
        ("while at < len(found) and found[at] in taken:", "while at < len(found) and found[at] in taken and not taken:"),
    ],
    "a cell one style cannot wear retired from every roster": [
        ('    places: "dict[str, dict[int, int]]" = {}\n', '    places: "dict[str, dict[int, int]]" = {}\n    refused: "dict[int, int]" = {}\n'),
        (
            "            if moved[other] != \"leading_zero\" or other in reserved:\n                continue\n            # A PINNED",
            "            if moved[other] != \"leading_zero\" or other in reserved or other in refused:\n                continue\n            # A PINNED",
        ),
        (
            "            if not receivable(other, taking):\n                continue\n            where[other]",
            "            if not receivable(other, taking):\n                refused[other] = 1\n                continue\n            where[other]",
        ),
    ],
    "one cursor shared by every wearing key": [
        (
            "wear_key = tuple([_can_wear(style, holds[index], whole_column) for style in present])",
            "wear_key = tuple([False for style in present])",
        ),
    ],
}


def _mutant(
    edits: "list[tuple[str, str]]",
    name: str = "_padded_style_swaps",
    helper: "tuple[str, list[tuple[str, str]]]" = ("", []),
) -> object:
    """The product's function ``name`` with ``edits`` applied to its text, each found exactly once.

    The one place this file runs a string of source (tests/test_version_reach.py
    names it): a shipped function read by `inspect.getsource`, with one edit
    of this file's own made to it. A ``helper`` named with edits of its own
    is mutated first into the same namespace, so the walk calls the mutated
    helper while the module's own stays as it is.
    """
    space = dict(vars(generation))
    steps = [helper, (name, edits)] if helper[0] else [(name, edits)]
    for each, changes in steps:
        text = inspect.getsource(getattr(generation, each))
        for before, after in changes:
            assert text.count(before) == 1, f"the mutant's edit no longer finds its text: {before!r}"
            text = text.replace(before, after)
        exec(compile(text, "<mutant>", "exec"), space)
    return space[name]


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_the_comparison_fails_on_each_mutant(name: str) -> None:
    """Each mutant answers some seeded or large case differently from the oracle."""
    walk = _mutant(MUTANTS[name])
    cases = [_seeded_case(number) for number in range(SEEDED_CASES)]
    differ = 0
    for case in cases:
        if _answer(walk, case) != _answer(_as_built_padded_style_swaps, case):
            differ = differ + 1
            if differ >= 3:
                break
    assert differ >= 1, f"the mutant {name!r} answers every seeded case as the oracle does"


# -- (b) predicate work grows with the rows -------------------------------------


def _predicate_calls(walk: object, case: Case) -> int:
    """Calls of `_pad_need`, `_can_wear` and `_carries_plainly` while ``walk`` answers ``case``."""
    return _calls(walk, case, PREDICATES)


def _calls(walk: object, case: Case, functions: "tuple[str, ...]") -> int:
    """Calls of the functions named while ``walk`` answers ``case``, counted under `sys.setprofile`."""
    counted = [0]
    names = frozenset(functions)

    def watch(frame: object, event: str, _argument: object) -> None:
        if event == "call" and frame.f_code.co_name in names:  # type: ignore[attr-defined]
            counted[0] = counted[0] + 1

    previous = sys.getprofile()
    sys.setprofile(watch)
    try:
        _answer(walk, case)
    finally:
        sys.setprofile(previous)
    return counted[0]


def padded_swap_measures() -> "dict[str, object]":
    """K-S4-16: the padded exchange's work on a postal-code column, 100,000 and 200,000 cells.

    Machine-free: calls and lines are counted, not timed. Judged: the
    predicate calls' growth and the walk's own lines' growth (`_walk_lines`),
    200,000 cells over 100,000, each unrounded, about 2 for work that
    grows with the rows and about 4 with their square; and the asks of
    `_point_free_form_worn` at 200,000 cells, at most one per wearing key.
    """
    small_case = _postal_case(100_000)
    large_case = _postal_case(200_000)
    small = _predicate_calls(generation._padded_style_swaps, small_case)
    large = _predicate_calls(generation._padded_style_swaps, large_case)
    small_lines = _walk_lines(generation._padded_style_swaps, small_case)[0]
    large_lines = _walk_lines(generation._padded_style_swaps, large_case)[0]
    return {
        "predicate_calls_100000_cells": small,
        "predicate_calls_200000_cells": large,
        "predicate_call_growth_200000_over_100000_cells": large / small,
        "walk_lines_100000_cells": small_lines,
        "walk_lines_200000_cells": large_lines,
        "walk_line_growth_200000_over_100000_cells": large_lines / small_lines,
        "point_free_form_asks_200000_cells": _calls(generation._padded_style_swaps, large_case, ("_point_free_form_worn",)),
    }


def test_predicate_calls_grow_with_the_rows_and_the_oracle_s_with_their_square() -> None:
    """At 100,000 cells against 50,000 the product's calls grow at most x2.2; the oracle's grow at least x3.0.

    The oracle is counted at 3,000 and 6,000 cells, where its square is
    already plain and the count is a few seconds rather than hours.
    """
    small = _predicate_calls(generation._padded_style_swaps, _postal_case(50_000))
    large = _predicate_calls(generation._padded_style_swaps, _postal_case(100_000))
    assert large / small <= LINEAR_AT_MOST, f"{small} calls at 50,000 cells, {large} at 100,000"
    assert large < 10 * 100_000, f"{large} calls at 100,000 cells"
    old_small = _predicate_calls(_as_built_padded_style_swaps, _postal_case(3_000))
    old_large = _predicate_calls(_as_built_padded_style_swaps, _postal_case(6_000))
    assert old_large / old_small >= SQUARE_AT_LEAST, f"the oracle: {old_small} calls at 3,000, {old_large} at 6,000"


# -- (f) the walk's own steps grow with the rows ----------------------------------
#
# A walk can choose every partner as the scan did and ask the predicates
# no more often, yet step over the same cells again and again: a trial
# asking each style from its roster's start, an overflow cursor put back
# to cell 0, a next-alive list that never shortens its links. Each picks
# the partners the scan picked (the comparisons in (a) cannot see it) and
# makes the walk quadratic, so the walk's own lines are counted too, on
# the shape that shows each one, and so are the asks of the point-free
# form, whose answer kept per wearing key is what keeps them few.

# The frames of the walk: the exchange, the helpers it defines, and the
# next-alive list. A predicate's own lines are not the walk's.
WALK_FRAMES = ("_padded_style_swaps", "roster", "retire", "first_from", "give_up", "hand_over", "_alive_from")


def _walk_lines(walk: object, case: Case) -> "tuple[int, list[str]]":
    """Lines the walk's own frames run while ``walk`` answers ``case``, and its answer: work, not time."""
    counted = [0]
    names = frozenset(WALK_FRAMES)

    def watch(frame: object, event: str, _argument: object) -> object:
        if frame.f_code.co_name not in names:  # type: ignore[attr-defined]
            return None
        if event == "line":
            counted[0] = counted[0] + 1
        return watch

    previous = sys.gettrace()
    sys.settrace(watch)  # type: ignore[arg-type]
    try:
        answer = _answer(walk, case)
    finally:
        sys.settrace(previous)
    return counted[0], answer


def _repeated_case(rows: int) -> Case:
    """``rows`` plain cells of 1, then ``rows`` padded cells of 123: one group of ``rows`` takes ``rows`` partners."""
    return ["plain"] * rows + ["leading_zero"] * rows, [1.0] * rows + [123.0] * rows, {"2": rows}, [], True, (0, ())


def _reserved_prefix_case(rows: int) -> Case:
    """``rows`` plain cells of 1, then ``rows`` padded cells of 123456 no width of 3 holds: every partner reserved in turn."""
    return ["plain"] * rows + ["leading_zero"] * rows, [1.0] * rows + [123456.0] * rows, {"3": 1}, [], True, (0, ())


def _distinct_code_case(rows: int) -> Case:
    """``rows`` codes of up to seven figures, nearly every one a value of its own, 30% padded, one width of 7."""
    draw = random.Random(f"h1/distinct/{rows}")
    holds = [float(draw.randint(0, 9_999_999)) for _cell in range(rows)]
    styles = [("leading_zero" if draw.random() < 0.3 else "plain") for _cell in range(rows)]
    narrow = 0
    for value in holds:
        if value < 1_000_000.0:
            narrow = narrow + 1
    return styles, holds, {"7": min(narrow, int(0.3 * rows))}, [], True, (0, ())


# Each shape at the cells it is counted on, and its count doubled.
WALK_SHAPES = {
    "one value taking a partner per cell": (_repeated_case, 1_000),
    "overflowing cells after a reserved prefix": (_reserved_prefix_case, 1_000),
    "distinct codes": (_distinct_code_case, 12_500),
    "postal codes": (_postal_case, 12_500),
}

# Each mutant leaves every partner as it was and walks the same cells
# again: its shape, the edits of the exchange, and a helper's edits.
WALK_MUTANTS = {
    "a trial asking each style from its roster's start": (
        "one value taking a partner per cell",
        [("start = reach[taking] if taking in reach else 0", "start = 0")],
        ("", []),
    ),
    "the overflow cursor put back to cell 0 for every cell": (
        "overflowing cells after a reserved prefix",
        [("other = cursors[wear_key] if wear_key in cursors else 0", "other = 0")],
        ("", []),
    ),
    "a next-alive list that never shortens its links": (
        "distinct codes",
        [],
        ("_alive_from", [("    while link[at] != root:\n        step = link[at]\n        link[at] = root\n        at = step\n", "")]),
    ),
}

FORM_ASKED_PER_CELL = [
    (
        "        if wearing not in forms:\n            forms[wearing] = _point_free_form_worn(styles, holds[index], whole_column)\n        given = forms[wearing]\n",
        "        given = _point_free_form_worn(styles, holds[index], whole_column)\n",
    )
]
# One ask per wearing key at most: each of `_WHOLE_STYLES` worn or not.
FORM_ASKS_AT_MOST = 2 ** len(generation._WHOLE_STYLES)


def _walk_growth(walk: object, shape: str) -> "tuple[float, int, int, list[str]]":
    """The walk's lines on ``shape`` at its cells and twice them: growth, both counts, and the smaller answer."""
    build, rows = WALK_SHAPES[shape]
    small, answer = _walk_lines(walk, build(rows))
    large = _walk_lines(walk, build(2 * rows))[0]
    return large / small, small, large, answer


@pytest.mark.parametrize("shape", sorted(WALK_SHAPES))
def test_the_walk_s_own_lines_grow_with_the_rows(shape: str) -> None:
    """On every shape the walk's lines grow at most x2.2 a doubling, and 68dae22f's answer holds at 1,000 cells."""
    growth, small, large, _answer_counted = _walk_growth(generation._padded_style_swaps, shape)
    assert growth <= LINEAR_AT_MOST, f"{shape}: {small} lines, then {large} at twice the cells"
    case = WALK_SHAPES[shape][0](1_000)
    assert _answer(generation._padded_style_swaps, case) == _answer(_as_built_padded_style_swaps, case), shape


@pytest.mark.parametrize("name", sorted(WALK_MUTANTS))
def test_each_walk_mutant_answers_alike_and_breaks_the_bound(name: str) -> None:
    """Each mutant answers its shape as the product does, so only the count sees it, and its lines grow past x2.2."""
    shape, edits, helper = WALK_MUTANTS[name]
    walk = _mutant(edits, helper=helper)
    growth, small, large, answer = _walk_growth(walk, shape)
    build, rows = WALK_SHAPES[shape]
    assert answer == _answer(generation._padded_style_swaps, build(rows)), f"premise: {name!r} picks the same partners"
    assert growth > LINEAR_AT_MOST, f"the mutant {name!r}: {small} lines, then {large} at twice the cells"


def test_the_point_free_form_is_asked_once_per_wearing_key() -> None:
    """On 25,000 postal cells the form is asked at most once per wearing key; asked per cell, hundreds of times."""
    case = _postal_case(25_000)
    asks = _calls(generation._padded_style_swaps, case, ("_point_free_form_worn",))
    assert 1 <= asks <= FORM_ASKS_AT_MOST, f"{asks} asks"
    mutant = _calls(_mutant(FORM_ASKED_PER_CELL), case, ("_point_free_form_worn",))
    assert mutant > 10 * FORM_ASKS_AT_MOST, f"premise: asked per cell, the form is asked {mutant} times"


# -- (c) the point-free form is still asked by name ------------------------------


def _postal_twin(folder: pathlib.Path) -> str:
    """The twin of 800 five-figure postal codes at the default floor, seed 7: a census its own draw cannot meet."""
    draw = random.Random(7)
    lines = ["code"] + [f"{draw.randrange(0, 99999):05d}" for _row in range(800)]
    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(folder, "codes.csv", "\n".join(lines) + "\n")
    settings = taxonomy.Settings()
    table = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(table, settings, [])
    target = fixtures.write_profile(folder, "codes-profile.json", document)
    loaded = contract.load_profile(str(target))
    return rendering.twin_csv(generation.generate(loaded, 7))


def test_the_point_free_form_is_still_asked_by_name(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Swapping `_point_free_form_worn` in still reaches the twin: asked, and its answer written.

    The answer is kept for one call per wearing key, never past it, and
    asked through the module's name, so a measure that swaps the
    function in (`tools/measurements/kpi_cost_rule.py`) or a test that
    withdraws it (`tests/test_stage3b_width.py`) still changes what it
    means to change.
    """
    real = generation._point_free_form_worn
    asked = [0]

    def counted(styles: "list[str]", value: float, whole: bool) -> str:
        asked[0] = asked[0] + 1
        return real(styles, value, whole)

    monkeypatch.setattr(generation, "_point_free_form_worn", counted)
    twin = _postal_twin(tmp_path / "counted")
    assert asked[0] >= 1, "the give-up never asked the point-free form"
    monkeypatch.setattr(generation, "_point_free_form_worn", real)
    assert _postal_twin(tmp_path / "real") == twin
    monkeypatch.setattr(generation, "_point_free_form_worn", lambda styles, value, whole: "")
    withdrawn = _postal_twin(tmp_path / "withdrawn")
    assert withdrawn != twin, "withdrawing the point-free form left the twin unchanged"
    assert max(len(cell) for cell in withdrawn.splitlines()[1:]) == 6
    assert max(len(cell) for cell in twin.splitlines()[1:]) == 5


def test_the_answer_is_asked_again_on_every_call(monkeypatch: pytest.MonkeyPatch) -> None:
    """No answer of `_point_free_form_worn` outlives the call that asked it: a second call asks again."""
    real = generation._point_free_form_worn
    asked = [0]

    def counted(styles: "list[str]", value: float, whole: bool) -> str:
        asked[0] = asked[0] + 1
        return real(styles, value, whole)

    monkeypatch.setattr(generation, "_point_free_form_worn", counted)
    case: Case = (["leading_zero"] * 6 + ["plain"] * 3, [123456.0] * 6 + [1.0, 2.0, 3.0], {"3": 2}, [], True, (0, ()))
    first = _answer(generation._padded_style_swaps, case)
    once = asked[0]
    assert once >= 1, "premise: the give-up asks the point-free form"
    assert _answer(generation._padded_style_swaps, case) == first
    assert asked[0] == 2 * once
    # The three cells of 123456 left without a partner share one
    # wearing key, so the call asks once (asked afresh per cell: 3).
    assert once == 1, "the answer is kept per wearing key within the call"


# -- (d) and (e): the plus exchange ---------------------------------------------


def _as_built_plus_style_swaps(
    facts: object,
    styles: "list[str]",
    holds: "list[float]",
    whole_column: bool,
) -> "list[str]":
    """68dae22f's `_plus_style_swaps`, comments and docstring dropped."""
    wanted = 0
    if "+" in facts.decimal_plus:  # type: ignore[attr-defined]
        wanted = facts.decimal_plus["+"]  # type: ignore[attr-defined]
    if wanted <= 0:
        return styles
    have = 0
    givers: "list[int]" = []
    for index in range(len(holds)):
        if holds[index] < 0.0:
            continue
        if styles[index] == "decimal":
            have = have + 1
        elif styles[index] == "plain" or styles[index] == "leading_zero":
            givers += [index]
    if have >= wanted:
        return styles
    takers: "list[int]" = []
    for index in range(len(holds) - 1, -1, -1):
        if styles[index] != "decimal" or not holds[index] < 0.0:
            continue
        if generation._can_wear("plain", holds[index], whole_column):
            takers += [index]
    moved = list(styles)
    used: "dict[int, int]" = {}
    short = wanted - have
    for giver in givers:
        if short <= 0:
            break
        for taker in takers:
            if taker in used:
                continue
            if moved[giver] == "leading_zero" and generation._pad_need(
                holds[taker], whole_column
            ) > generation._pad_need(holds[giver], whole_column):
                continue
            used[taker] = 1
            moved[taker] = moved[giver]
            moved[giver] = "decimal"
            short = short - 1
            break
    return moved


class _Plus:
    """The one field of the numeric block the plus exchange reads."""

    def __init__(self, wanted: int) -> None:
        self.decimal_plus = {"+": wanted}


PlusCase = "tuple[_Plus, list[str], list[float], bool]"


def _signed_column(
    rows: int, seed: str, short: "int | None", padded: float, spread: float = 0.0
) -> PlusCase:
    """Signed changes as the style walk hands them in, short of the plus count by ``short`` (a tenth if None)."""
    draw = random.Random(seed)
    holds: "list[float]" = []
    styles: "list[str]" = []
    if spread <= 0.0:
        spread = draw.choice([9.0, 300.0, 30000.0])
    for _cell in range(rows):
        value = draw.gauss(0.0, spread)
        value = float(round(value)) if draw.random() < 0.5 else round(value, 2)
        holds += [value]
        if value < 0.0:
            styles += ["decimal" if draw.random() < 0.9 else "plain"]
        elif draw.random() < padded:
            styles += ["leading_zero"]
        else:
            styles += [draw.choice(["plain", "decimal", "decimal", "leading_plus"])]
    have = 0
    for value, style in zip(holds, styles):
        if value >= 0.0 and style == "decimal":
            have = have + 1
    owed = have // 10 if short is None else short
    return _Plus(have + owed), styles, holds, draw.random() < 0.5


def _plus_answer(walk: object, case: PlusCase) -> "list[str]":
    """The plus exchange's styles for one case, handed fresh lists."""
    facts, styles, holds, whole = case
    return walk(facts, list(styles), list(holds), whole)  # type: ignore[operator]


def _seeded_plus_case(number: int) -> PlusCase:
    """One seeded signed column: 3 to 900 cells, short by 0 to 60 or by a tenth, up to every giver padded."""
    draw = random.Random(f"h1/plus/{number}")
    rows = draw.choice([3, 10, 40, 150, 900])
    short = None if draw.random() < 0.3 else draw.randint(0, 60)
    return _signed_column(rows, f"h1/plus/cells/{number}", short, draw.choice([0.0, 0.2, 0.6, 1.0]))


def test_the_plus_exchange_answers_every_seeded_case_as_68dae22f_did() -> None:
    """2,000 seeded signed columns and two of 25,000 cells: the same styles as the oracle, and styles do move."""
    moved = 0
    cases = [_seeded_plus_case(number) for number in range(SEEDED_CASES)]
    cases += [
        _signed_column(25_000, "h1/plus/large/1", None, 0.3),
        _signed_column(25_000, "h1/plus/large/2", 400, 0.9),
    ]
    for number in range(len(cases)):
        expected = _plus_answer(_as_built_plus_style_swaps, cases[number])
        assert _plus_answer(generation._plus_style_swaps, cases[number]) == expected, f"case {number}"
        for before, after in zip(cases[number][1], expected):
            if before != after:
                moved = moved + 1
    assert moved > 5_000, f"premise: the seeded cases move styles ({moved})"


PLUS_MUTANTS = {
    "a padded giver taking the first free taker, whatever it needs": [
        ('        if moved[giver] == "leading_zero":\n            own', '        if moved[giver] == "leading_zero" and not moved:\n            own'),
    ],
    "a taker given a style left free in its figure group": [
        ("        need_links[need_of[found]][place[found]] = place[found] + 1\n", ""),
    ],
}


@pytest.mark.parametrize("name", sorted(PLUS_MUTANTS))
def test_the_plus_comparison_fails_on_each_mutant(name: str) -> None:
    """Each mutant of the plus exchange answers some seeded case differently from the oracle."""
    walk = _mutant(PLUS_MUTANTS[name], "_plus_style_swaps")
    for number in range(SEEDED_CASES):
        case = _seeded_plus_case(number)
        if _plus_answer(walk, case) != _plus_answer(_as_built_plus_style_swaps, case):
            return
    raise AssertionError(f"the mutant {name!r} answers every seeded case as the oracle does")


def _lines_run(walk: object, case: PlusCase) -> int:
    """Lines the plus exchange and `_alive_from` run while ``walk`` answers ``case``: work, not time."""
    counted = [0]
    names = frozenset(["_plus_style_swaps", "_as_built_plus_style_swaps", "_alive_from", "_pad_need"])

    def watch(frame: object, event: str, _argument: object) -> object:
        if frame.f_code.co_name not in names:  # type: ignore[attr-defined]
            return None
        if event == "line":
            counted[0] = counted[0] + 1
        return watch

    previous = sys.gettrace()
    sys.settrace(watch)  # type: ignore[arg-type]
    try:
        _plus_answer(walk, case)
    finally:
        sys.settrace(previous)
    return counted[0]


def test_the_plus_exchange_runs_lines_that_grow_with_the_rows() -> None:
    """Short by a tenth: x2.2 at most from 50,000 to 100,000 cells; the oracle's grow x3.0 or more from 25,000 to 50,000."""

    def column(rows: int) -> PlusCase:
        facts, styles, holds, _whole = _signed_column(rows, f"h1/plus/grow/{rows}", None, 0.3, 300.0)
        return facts, styles, holds, False

    small = _lines_run(generation._plus_style_swaps, column(50_000))
    large = _lines_run(generation._plus_style_swaps, column(100_000))
    assert large / small <= LINEAR_AT_MOST, f"{small} lines at 50,000 cells, {large} at 100,000"
    old_small = _lines_run(_as_built_plus_style_swaps, column(25_000))
    old_large = _lines_run(_as_built_plus_style_swaps, column(50_000))
    assert old_large / old_small >= SQUARE_AT_LEAST, f"the oracle: {old_small} lines at 25,000, {old_large} at 50,000"

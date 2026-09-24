"""The tail's back-solve walks its own stack, and answers what it answered.

THE DEFECT. `taxonomy._lattice_fill` -- the walk that decides whether a
tail's published pair would give the tail's own cells back (plan
P4-D349) -- called itself once per distance still to place. A tail holds
about a hundredth of its column, so the walk nested once per hundred
rows, and past the interpreter's own limit it raised a bare
`RecursionError` inside `synthtwin profile`. Measured on ONE Gaussian
numeric column at two decimal places and the default floor of eleven:
98,456 rows described cleanly and 98,457 rows raised. A hundred thousand
rows is an ordinary table for this tool -- landing 4's gate is two
million by fifty -- and the tool refused nothing and crashed, which is
the worst of both. The STEP budget bounded the work and could not bound
the stack, exactly as it could not in `generation._settles`.

THE REPAIR COSTS NO BEHAVIOUR. The same walk carries an explicit stack:
`_lattice_enter` is one call, `_lattice_onward` is one turn of its
candidate loop, pushing is entering and popping is returning. The order
of the candidates, the memo of dead remainders, the step budget and its
accounting are untouched -- the budget is charged once per
`_lattice_enter`, which is once per call, so a search spends its steps
on exactly the sub-problems it spent them on before.

WHAT THIS FILE PINS, and every number in it is worked out from the rule
that decides it rather than read off any output:

1. **The two walks agree**, over seeded shapes covering what the walk
   meets -- a few cells, heavy ties, all-different distances, a heap
   with one far cell, a wide range, and a tail big enough to make the
   walk work. They must agree on the multiset returned by the fill
   itself, on the meters that multiset cost (steps taken, budget spent,
   every remainder marked dead), on the verdict `_tail_pinned` gives,
   and on the published side `_tail_side` builds -- its rows, its mean
   distance, its root-mean-square distance and its listed values, which
   are the extremes a reader is handed.
2. **The review's own case**, eleven distances summing to 24 with
   squares summing to 104, answered the same by both.
3. **A budget-exhausted search agrees too**, twice over: a shape that
   spends the shipped budget of its own accord, and every shape above
   re-asked at budgets small enough that the walk gives up early.
4. **A tail deeper than the interpreter can nest describes cleanly**,
   at a size taken from `sys.getrecursionlimit()` and the tail rule's
   own arithmetic rather than from a number somebody typed.
5. **And the walk does not name itself**, read off the source, so the
   recursion cannot come back without this file going red.

THE RED CHECK. Item 4's column is described again with
`taxonomy._lattice_fill` REPLACED by the pre-repair text carried below,
and it raises `RecursionError` -- so the clean description above is the
repair's doing and not the shape's.
"""

from __future__ import annotations

import ast
import pathlib
import random
import sys

import pytest

import kpi_shapes
from synthtwin import parsing, taxonomy

# The shipped default smallest group (plan P3-D2, the rulings of
# 2026-09-22), named here because the reproduction was measured at it.
FLOOR = 11

# The two row counts of the reproduction, on ONE Gaussian numeric column
# at two decimal places, seed 20260913, described at `FLOOR` by
# `synthtwin profile`: the largest that described and the smallest that
# raised. They are recorded, not asserted -- a column of a hundred
# thousand rows does not belong in this suite -- and what IS asserted
# here is the property that made them differ, at a size this suite can
# afford (`test_a_tail_deeper_than_the_walk_could_nest_describes`).
CRASHED_FROM = (98_456, 98_457)


# -- the pre-repair walk, carried whole ---------------------------------
#
# VERBATIM, but for its name and for naming this module's helpers
# through `taxonomy`. It is the reference the repair is proved against
# and the mutation the regression test is watched failing under, so it
# is copied rather than paraphrased: a reference written afresh would
# prove agreement with itself.


def recursive_fill(
    lattice: taxonomy._Lattice,
    count: int,
    total: int,
    squares: int,
    least: int,
    most: int,
    barred: int,
) -> "list[int] | None":
    """`_lattice_fill` as it stood before the repair: it calls itself."""
    if lattice.spent:
        return None
    lattice.steps = lattice.steps + 1
    if lattice.steps > taxonomy.TAIL_LATTICE_STEPS:
        lattice.spent = True
        return None
    if count == 0:
        if total == 0 and squares == 0:
            return []
        return None
    if total < 0 or squares < 0:
        return None
    most = min(most, lattice.edge)
    room = squares - (count - 1) * least * least
    if room < 0:
        return None
    most = min(most, taxonomy._root_of(room))
    if most < least:
        return None
    if lattice.distinct:
        if most - least + 1 < count:
            return None
        low_sum = count * least + (count * (count - 1)) // 2
        high_sum = count * most - (count * (count - 1)) // 2
    else:
        low_sum = count * least
        high_sum = count * most
    if total < low_sum or total > high_sum:
        return None
    if (squares - total) % 2 != 0:
        return None
    even, spare = divmod(total, count)
    if squares < (count - spare) * even * even + spare * (even + 1) * (even + 1):
        return None
    if squares > taxonomy._lattice_widest(count, total, least, most):
        return None
    key = (count, total, squares, least, most, barred)
    if key in lattice.dead:
        return None
    if count == 1:
        if total != barred and total * total == squares:
            return [total]
        lattice.dead[key] = True
        return None
    if count == 2:
        spread = 2 * squares - total * total
        if spread >= 0:
            root = taxonomy._root_of(spread)
            if root * root == spread and (total + root) % 2 == 0:
                big = (total + root) // 2
                small = total - big
                if (
                    least <= small <= big <= most
                    and big != barred
                    and small != barred
                    and (not lattice.distinct or big > small)
                ):
                    return [big, small]
        lattice.dead[key] = True
        return None
    lowest = -(-total // count)
    highest = (
        total
        + taxonomy._root_of((count - 1) * (count * squares - total * total))
    ) // count
    value = min(most, total - (count - 1) * least, highest)
    while value >= lowest:
        if value != barred:
            below = value - 1 if lattice.distinct else value
            rest = recursive_fill(
                lattice,
                count - 1,
                total - value,
                squares - value * value,
                least,
                below,
                barred,
            )
            if rest is not None:
                found = [value]
                found += rest
                return found
            if lattice.spent:
                return None
        value = value - 1
    if not lattice.spent:
        lattice.dead[key] = True
    return None


# -- the shapes the walk meets ------------------------------------------


class Shape:
    """One tail the walk is asked about: its distances and its readings."""

    def __init__(
        self,
        distances: "list[int]",
        floor: int,
        edge: int,
        distinct: bool,
        least: int,
    ) -> None:
        self.distances = distances
        self.floor = floor
        self.edge = edge
        self.distinct = distinct
        self.least = least

    @property
    def triple(self) -> "tuple[int, int, int]":
        """The three numbers a reader is given: rows, sum, sum of squares."""
        return (
            len(self.distances),
            sum(self.distances),
            sum(one * one for one in self.distances),
        )

    def __repr__(self) -> str:
        return (
            f"Shape(rows={self.triple[0]}, total={self.triple[1]}, "
            f"squares={self.triple[2]}, floor={self.floor}, edge={self.edge}, "
            f"distinct={self.distinct}, least={self.least})"
        )


def seeded_shapes(seed: int, how_many: int) -> "list[Shape]":
    """Seeded tails covering the shapes the back-solve meets.

    Six families, drawn in turn: a few cells at small distances; a heap
    of ties with a stray or two; all-different distances, which is the
    reading a column of unique values publishes; a real tail's own shape
    -- many cells close in and one far out; a wide range over few cells;
    and a tail big enough that the walk has to work for its answer.
    """
    draw = random.Random(seed)
    made: "list[Shape]" = []
    for _each in range(how_many):
        family = draw.randrange(6)
        if family == 0:
            size = draw.randint(1, 6)
            top = draw.randint(1, 12)
            distances = [draw.randint(1, top) for _cell in range(size)]
        elif family == 1:
            size = draw.randint(4, 20)
            one = draw.randint(1, 9)
            distances = [one for _cell in range(size)]
            for _stray in range(draw.randint(0, 3)):
                distances[draw.randrange(size)] = draw.randint(1, 20)
        elif family == 2:
            size = draw.randint(3, 16)
            distances = sorted(
                {step + draw.randint(0, 2) * step for step in range(1, size + 1)}
            )
        elif family == 3:
            size = draw.randint(5, 18)
            distances = [draw.randint(1, 4) for _cell in range(size - 1)]
            distances += [draw.randint(10, 60)]
        elif family == 4:
            size = draw.randint(2, 7)
            distances = [draw.randint(1, 400) for _cell in range(size)]
        else:
            size = draw.randint(8, 30)
            distances = [draw.randint(1, 30) for _cell in range(size)]
        if not distances:
            distances = [1]
        apart = len(set(distances)) == len(distances) and draw.random() < 0.7
        if apart:
            distances = sorted(set(distances))
        furthest = max(distances)
        edge = max(
            furthest,
            draw.choice(
                [furthest, furthest + draw.randint(0, 50), 100_000]
            ),
        )
        # `least` is the smallest distance a reader cannot rule out, and
        # a numeric tail's is nought where the boundary rung's own grid
        # point is a candidate. It can never exceed a real distance.
        least = min(draw.choice([0, 1, 1, 1]), min(distances))
        made += [Shape(distances, draw.choice([2, 3, 5, 11, 11, 11]), edge, apart, least)]
    return made


# The review's own reconstruction, the case stage 3 raised by hand:
# eleven distances summing to 24 whose squares sum to 104, which
# `[8, 4, 4] + [1] * 8` and `[8, 5, 2, 2] + [1] * 7` both meet.
REVIEWS_OWN = Shape([8, 4, 4] + [1] * 8, FLOOR, 24, False, 1)

# Eleven DIFFERENT distances summing to 66: the integers 0 to 1100, whose
# tail the review read back exactly.
ALL_APART = Shape(list(range(1, 12)), FLOOR, 66, True, 1)

# A SHAPE THAT SPENDS THE SHIPPED BUDGET of its own accord, so that the
# `spent` road is walked at the budget the product ships rather than only
# at a lowered one. Twenty-six all-different distances three units apart,
# with no distance past the largest plus one step: the remainder cannot
# be settled and cannot be ruled out inside `TAIL_LATTICE_STEPS`.
def _budget_eater() -> Shape:
    distances = [3 * step for step in range(26)]
    return Shape(distances, FLOOR, max(distances) + 3, True, 0)


# -- 1. the two walks agree ---------------------------------------------


def _meters(lattice: taxonomy._Lattice) -> "tuple[int, bool, list]":
    """What one search cost: steps taken, budget spent, remainders killed."""
    return (lattice.steps, lattice.spent, sorted(lattice.dead))


def _both_fills(shape: Shape, budget: int) -> "list[tuple]":
    """Both walks over the SAME two sub-problems, from the same start.

    The two sub-problems are the two the back-solve actually asks: the
    remainder beside a candidate largest distance (`_lattice_with_top`)
    and the remainder beside a barred value (`_lattice_with_count`).
    """
    kept = taxonomy.TAIL_LATTICE_STEPS
    taxonomy.TAIL_LATTICE_STEPS = budget
    try:
        size, total, squares = shape.triple
        top = max(shape.distances)
        answers: "list[tuple]" = []
        for barred, most in ((-1, top - 1 if shape.distinct else top), (top, shape.edge)):
            here = taxonomy._Lattice(
                size, total, squares, shape.edge, shape.distinct, least=shape.least
            )
            there = taxonomy._Lattice(
                size, total, squares, shape.edge, shape.distinct, least=shape.least
            )
            answers += [
                (
                    taxonomy._lattice_fill(
                        here,
                        size - 1,
                        total - top,
                        squares - top * top,
                        shape.least,
                        most,
                        barred,
                    ),
                    recursive_fill(
                        there,
                        size - 1,
                        total - top,
                        squares - top * top,
                        shape.least,
                        most,
                        barred,
                    ),
                    _meters(here),
                    _meters(there),
                )
            ]
        return answers
    finally:
        taxonomy.TAIL_LATTICE_STEPS = kept


# The repaired walk, taken once at import so a test can hand it back to
# `_tail_pinned` beside the recursive one without catching a probe.
ITERATIVE = taxonomy._lattice_fill


def _watched(shape: Shape, budget: int, fill) -> "tuple[bool, int, bool]":
    """One whole back-solve under ``fill``: its verdict and what it cost.

    `_tail_pinned` makes its own search, so the meters are read off it
    through the fill it calls: the steps it had taken and whether the
    budget ran out.
    """
    kept = taxonomy.TAIL_LATTICE_STEPS
    taxonomy.TAIL_LATTICE_STEPS = budget
    standing = taxonomy._lattice_fill
    seen = {"steps": 0, "spent": False}

    def probe(lattice, count, total, squares, least, most, barred):
        answer = fill(lattice, count, total, squares, least, most, barred)
        if lattice.steps > seen["steps"]:
            seen["steps"] = lattice.steps
        seen["spent"] = seen["spent"] or lattice.spent
        return answer

    taxonomy._lattice_fill = probe
    try:
        verdict = taxonomy._tail_pinned(
            shape.distances, shape.floor, shape.edge, shape.distinct, least=shape.least
        )
    finally:
        taxonomy._lattice_fill = standing
        taxonomy.TAIL_LATTICE_STEPS = kept
    return (verdict, seen["steps"], seen["spent"])


def _both_verdicts(shape: Shape, budget: int) -> "tuple[tuple, tuple]":
    """`_tail_pinned` under each walk, at one budget, with its meters."""
    return (
        _watched(shape, budget, ITERATIVE),
        _watched(shape, budget, recursive_fill),
    )


def _both_sides(shape: Shape) -> "tuple[dict, dict]":
    """The PUBLISHED side each walk builds: rows, the pair, the values.

    This is what a reader is handed, so it is what agreement has to mean.
    The texts are the distances written out, which is enough for
    `_tail_side` to name a value where the listing rule admits one.
    """
    texts = [f"{one:06d}" for one in shape.distances]
    standing = taxonomy._lattice_fill
    try:
        here = taxonomy._tail_side(
            shape.distances, texts, "boundary", shape.floor, shape.edge,
            shape.distinct, len(set(shape.distances)), len(shape.distances),
        )
        taxonomy._lattice_fill = recursive_fill
        there = taxonomy._tail_side(
            shape.distances, texts, "boundary", shape.floor, shape.edge,
            shape.distinct, len(set(shape.distances)), len(shape.distances),
        )
        return (here, there)
    finally:
        taxonomy._lattice_fill = standing


# How many seeded shapes the agreement is proved over, and the budgets
# each is asked at: the shipped one, then three small enough that the
# walk gives up part-way, which is the only cheap way to reach the
# `spent` road on a shape that would otherwise settle.
SHAPES = 4_000
BUDGETS = (taxonomy.TAIL_LATTICE_STEPS, 400, 40, 3)


def test_the_two_walks_return_the_same_multiset_at_the_same_cost() -> None:
    """Same answer, same steps, same budget verdict, same dead remainders.

    The meters are compared as well as the answer: a walk that agreed on
    the answer while charging the budget differently would drift apart
    on the first shape big enough to spend it.
    """
    differed: "list[str]" = []
    for shape in seeded_shapes(20260924, SHAPES) + [REVIEWS_OWN, ALL_APART]:
        for budget in BUDGETS:
            for here, there, meter_here, meter_there in _both_fills(shape, budget):
                if here != there:
                    differed += [f"{shape} at budget {budget}: {here} vs {there}"]
                if meter_here != meter_there:
                    differed += [
                        f"{shape} at budget {budget}: cost "
                        f"{meter_here[:2]} vs {meter_there[:2]}, "
                        f"{len(meter_here[2])} vs {len(meter_there[2])} dead"
                    ]
    assert differed == [], "\n".join(differed[:20])


def test_the_two_walks_give_the_same_verdict_and_publish_the_same_side() -> None:
    """The verdict a tail turns on, and the extremes the tail then reports.

    A tail the back-solve pins publishes its boundary and its rows and
    NOTHING else; one it does not pins publishes its mean and its
    root-mean-square distance, or its own values where the listing rule
    admits them. Both walks must reach the same door and put the same
    thing through it.
    """
    differed: "list[str]" = []
    census = {"pinned": 0, "open": 0}
    for shape in seeded_shapes(20260924, SHAPES) + [REVIEWS_OWN, ALL_APART]:
        for budget in BUDGETS:
            here, there = _both_verdicts(shape, budget)
            if here != there:
                differed += [f"{shape} at budget {budget}: pinned {here} vs {there}"]
            if budget == BUDGETS[0]:
                census["pinned" if here[0] else "open"] += 1
        here_side, there_side = _both_sides(shape)
        if here_side != there_side:
            differed += [f"{shape}: published {here_side} vs {there_side}"]
    assert differed == [], "\n".join(differed[:20])
    # THE SHAPES MUST REACH BOTH ANSWERS AND NEITHER RARELY, or the
    # agreement above is an agreement about one road. A tenth of the
    # family each way is the bar; it stands at about a quarter pinned
    # and three quarters open. This is a property of the shape family,
    # not a measurement of the walk.
    floor_share = SHAPES // 10
    assert census["pinned"] >= floor_share, census
    assert census["open"] >= floor_share, census


def test_the_reviews_own_case_answers_the_same_under_both_walks() -> None:
    """Eleven distances summing to 24 with squares 104, by hand.

    Two multisets meet those three facts and both put the largest
    distance at 8 on one row, so the extreme is named and the tail must
    read PINNED. Both walks say so.
    """
    rows, total, squares = REVIEWS_OWN.triple
    assert (rows, total, squares) == (11, 24, 104), (rows, total, squares)
    here, there = _both_verdicts(REVIEWS_OWN, taxonomy.TAIL_LATTICE_STEPS)
    assert here == there, (here, there)
    assert here[0] is True, here


def test_a_search_that_spends_the_shipped_budget_agrees_too() -> None:
    """The `spent` road, at the budget the product ships.

    A walk that gives up answers PINNED, the answer that publishes less,
    and it must give up in the same place and after the same number of
    steps under both forms.
    """
    shape = _budget_eater()
    here, there = _both_verdicts(shape, taxonomy.TAIL_LATTICE_STEPS)
    assert here == there, (here, there)
    verdict, steps, spent = here
    assert spent, (
        "this case is here because the shipped budget runs out on it; if "
        "that stopped being true it would prove nothing"
    )
    assert steps == taxonomy.TAIL_LATTICE_STEPS + 1, steps
    assert verdict is True, (
        "a walk that gives up answers PINNED, which publishes less"
    )


# -- 4. a tail deeper than the interpreter can nest ---------------------


def _deep_tail_column() -> "tuple[int, int, int]":
    """The smallest column whose tail outruns the old walk's stack.

    Derived, not chosen. The old walk nested once per distance still to
    place, so it needed a tail of more than `sys.getrecursionlimit()`
    rows to raise -- with room to spare for the frames the product
    itself is standing on. `parsing.tail_percent` answers the boundary
    percent of a column of `n` values at a floor of `f`, and
    `parsing.tail_rows` how many rows that leaves beyond the boundary;
    a column of exactly `2 * tail_units(f) + 1` values takes the widest
    percent the rule allows, which is what makes a deep tail affordable
    here instead of the hundred thousand rows the reproduction needed.

    Returns (floor, rows, tail rows).
    """
    wanted = sys.getrecursionlimit() + 64
    floor = wanted
    while True:
        units = parsing.tail_units(floor)
        rows = 2 * units + 1
        percent = parsing.tail_percent(rows, units)
        assert percent is not None, (floor, rows)
        beyond = parsing.tail_rows(rows, percent, "low")
        if beyond >= wanted:
            return (floor, rows, beyond)
        floor = floor + 1


def _gaussian_column(rows: int) -> "list[str]":
    """One numeric column of Gaussian readings at two decimal places."""
    draw = random.Random(20260913)
    return [f"{draw.gauss(50, 5):.2f}" for _cell in range(rows)]


def test_a_tail_deeper_than_the_walk_could_nest_describes(tmp_path) -> None:
    """The regression: the whole product path, on a tail past the limit.

    The column is described through the reader, the producer and the
    strict loader, and its tails are asked the back-solve like any
    other. The size is the tail rule's own arithmetic over
    `sys.getrecursionlimit()`, so it tracks the interpreter this suite
    is running on rather than a number that was true once.
    """
    floor, rows, beyond = _deep_tail_column()
    assert beyond > sys.getrecursionlimit(), (beyond, sys.getrecursionlimit())
    described = kpi_shapes.describe(
        tmp_path, "deep", "value\n" + "\n".join(_gaussian_column(rows)) + "\n", floor
    )
    block = described.document["columns"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS, block["role"]
    tails = block["tails"]
    assert isinstance(tails, dict), tails
    # BOTH SIDES ARE THERE AND BOTH ARE THIS DEEP: the crash was in the
    # walk this many rows drive, so a tail that quietly shrank would make
    # the test pass without exercising anything.
    for side in ("low", "high"):
        assert tails[side] is not None, side
        assert tails[side]["rows"] == beyond, (side, tails[side]["rows"], beyond)


def test_the_same_column_raises_under_the_recursive_walk(tmp_path) -> None:
    """RED CHECK: put the old walk back and the description crashes.

    This is the mutation the test above is verified against. Without it
    the test says only that a small table describes, which it did before
    the repair as well.
    """
    floor, rows, _beyond = _deep_tail_column()
    text = "value\n" + "\n".join(_gaussian_column(rows)) + "\n"
    standing = taxonomy._lattice_fill
    taxonomy._lattice_fill = recursive_fill
    try:
        with pytest.raises(RecursionError):
            kpi_shapes.describe(tmp_path, "deep-recursive", text, floor)
    finally:
        taxonomy._lattice_fill = standing


# -- 5. and the walk does not name itself -------------------------------

WALK = ("_lattice_fill", "_lattice_enter", "_lattice_onward")


def _calls_among(names: "tuple[str, ...]") -> "dict[str, set[str]]":
    """Which of ``names`` each of ``names`` mentions, read off the source."""
    source = pathlib.Path(taxonomy.__file__).resolve()
    tree = ast.parse(source.read_text(encoding="utf-8"))
    found = {name: set() for name in names}
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in found:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Name) and inner.id in found:
                found[node.name] = found[node.name] | {inner.id}
    return found


def test_the_walk_can_never_reach_itself() -> None:
    """Read off the source: the three functions' call graph has no cycle.

    `_lattice_fill` names the other two, which is the repair. What no
    longer exists, and must not come back, is a road from any of the
    three BACK to itself -- naming itself, or naming one that names it.
    That is the defect counted directly rather than its symptom: a timed
    guard cannot say it, because the crash needs a hundred thousand rows
    to appear, and a test that merely described a deep tail would go
    quiet the day the tail rule changed shape. This costs milliseconds
    and cannot flake, which is what `tests/test_no_quadratic_list_growth.py`
    settled for the other scale defect of this project.
    """
    names = _calls_among(WALK)
    assert names["_lattice_fill"] == {"_lattice_enter", "_lattice_onward"}, names
    cycles: "list[str]" = []
    for start in WALK:
        reached = set(names[start])
        while True:
            onward = set(reached)
            for name in reached:
                onward = onward | names[name]
            if onward == reached:
                break
            reached = onward
        if start in reached:
            cycles += [f"{start} reaches itself through {sorted(reached)}"]
    assert cycles == [], "\n".join(cycles)

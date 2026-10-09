"""Stage 4: the packing walk of method G9.5 offers a cell only the fills the cells after it can finish (plan P4-D389).

The wave-1 critic of review item 1 of landing S1 left one case of that
item failing end to end: Codex's declared identifier -- `7` written
``2k + 1`` times beside ``k`` values written 2, 4, ... ``2k`` times --
whose one packing question made `generation._cell_walk` try every set
of the even sizes that fits the cell of ordinary numbers written in
figures alone before the lone odd group that finishes it: 101,994 fills
at ``k = 60``, 826,616 and 1.26 GB at ``k = 80``, and the ``k = 100``
witness, 10,301 rows the producer and the loader accept, past 1.8 GB.
Each ten more groups cost about 3.5 times the time.

The lane's identity battery then found a description the three
conditions 45f85b0 added -- 2, 3 and 4 below -- could not answer
either: a declared identifier of 300 values written in four forms, each
value held by a different number of rows from 1 to 300 -- 45,150 rows
the producer and the loader accept -- whose twin 493f6f8 could not
build within 1.6 GB, and which the walk with only those three was still
walking after twenty minutes. A count of lengths only one cell can answer for fixes that
cell's total, and the rest of its class is then nought, which no fact
about one count says.

The walk now reads five necessary conditions on entering a cell
(`generation._cell_entry`): what each cell from this one on may hold,
read off every count it answers for together (`_bounds_settled`); where
each size can still go; whether every count still owed can be made;
which totals the cells after this one can complete; and what those
cells must still find among the groups this one leaves (`_reserves_met`,
read again inside `_cell_next` wherever the cell takes a copy of a size
it reads). A fill any of
them refuses held no answer, so the answer is the walk's old answer,
fill for fill in the same order, and what changed is how many fills
are tried. The states a walk writes down are held as one number each
(`generation._walk_mark`) and bounded (`generation._WALK_MEMORY`), and
forgetting one costs time and never an answer.

THE ORACLE IS THE WALK AS 493f6f8 SHIPPED IT, frozen as text in
`tests/stage4_as_built.py` (`ALLOTTED_OVER`), so a change of meaning
made to the product cannot reach it. Every answer here is compared with
it wherever it finishes, and the growth measure is taken of it too, so
the measure is known to see the defect it guards against.
"""

from __future__ import annotations

import ast
import itertools
import operator
import pathlib
import random
import sys
import tempfile

import pytest

import stage4_as_built
import test_stage4_linear_work as linear
from synthtwin import contract, generation, rendering

# What the walk's states may grow by when the groups of Codex's
# identifier double, and what the walk it replaced must reach to show
# the measure sees the defect. The walk now enters ``k + 12`` states on
# ``k`` groups -- one for each of the ``k`` packing questions it refuses
# at once and one for each cell of the question that packs: 32, 52 and
# 92 at 20, 40 and 80 -- so they grow less than twice; the walk replaced
# grew 21.8 times from 20 groups to 40, 402 states to 8,748.
DOUBLED_AT_MOST = 2.5
REPLACED_AT_LEAST = 8.0


def _as_built() -> "tuple[object, dict]":
    """The packing walk as 493f6f8 shipped it, among a copy of today's names."""
    return stage4_as_built.compiled(
        generation, stage4_as_built.ALLOTTED_OVER, "_allotted_over"
    )


def _counted(names: dict, key: str = "_cell_room") -> "list[int]":
    """Count every state a walk enters: `_cell_room` is asked once per state."""
    seen = [0]
    asked = names[key]

    def counting(*given):  # type: ignore[no-untyped-def]
        seen[0] += 1
        return asked(*given)

    names[key] = counting
    return seen


# -- the seeded questions ------------------------------------------------


def _grid(parts: "list[int]") -> "tuple[int, list[list[int]]]":
    """The cells of a grid over margins of ``parts`` counts, and each cell's count per margin."""
    cells = 1
    for count in parts:
        cells = cells * count
    part_of: "list[list[int]]" = []
    for margin in range(len(parts)):
        stride = 1
        for later in parts[margin + 1:]:
            stride = stride * later
        part_of += [[(cell // stride) % parts[margin] for cell in range(cells)]]
    return cells, part_of


def _question(draw: random.Random) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """One packing question: groups, margins over one grid, and each group's permitted cells.

    Half are built by drawing an assignment and publishing what it
    counts, so an answer exists; half draw each margin's counts on its
    own, so most have none. A group's permitted cells are drawn from a
    pool of two or three sets, as the roles that pack hand the walk a
    few windows and not one per group.
    """
    margins_count = draw.choice((1, 2, 2, 2, 3))
    parts = [
        draw.randint(1, 3 if margins_count == 3 else 4)
        for _each in range(margins_count)
    ]
    cells, part_of = _grid(parts)
    sizes: "list[int]" = []
    for _each in range(draw.randint(1, 7)):
        sizes += [draw.randint(1, 10)] * draw.choice((1, 1, 1, 2, 3))
    draw.shuffle(sizes)
    groups = tuple(sizes)
    pool = [
        draw.getrandbits(cells) | (1 << draw.randrange(cells))
        for _each in range(draw.randint(1, 3))
    ]
    allowed = [draw.choice(pool) for _each in groups]
    quotas: "list[list[int]]" = []
    if draw.random() < 0.5:
        truth = []
        for place in range(len(groups)):
            open_cells = [
                cell for cell in range(cells) if (allowed[place] >> cell) & 1
            ]
            truth += [draw.choice(open_cells)]
        for margin in range(margins_count):
            counted = [0 for _each in range(parts[margin])]
            for place in range(len(groups)):
                counted[part_of[margin][truth[place]]] += groups[place]
            quotas += [counted]
    else:
        total = sum(groups)
        for margin in range(margins_count):
            cuts = sorted(draw.randint(0, total) for _each in range(parts[margin] - 1))
            edges = [0] + cuts + [total]
            quotas += [[edges[step + 1] - edges[step] for step in range(parts[margin])]]
    return groups, [(quotas[margin], part_of[margin]) for margin in range(margins_count)], allowed


def test_every_seeded_question_is_answered_as_the_walk_it_replaced_answered(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """2,400 seeded questions over one, two and three margins: the same answer, never more states.

    The answer is compared whole -- the cell of every group, or None --
    and the states each walk enters are counted. The new conditions pass
    over only fills the old walk tried and found no answer under, so on
    none of these questions does the walk enter more states than the
    walk it replaced, and on more than 300 it enters fewer: a question
    on which it entered more would be one where it offered a fill the
    old order did not.
    """
    built, names = _as_built()
    old_states = _counted(names)
    new_states = [0]
    asked = generation._cell_room

    def counting(*given):  # type: ignore[no-untyped-def]
        new_states[0] += 1
        return asked(*given)

    monkeypatch.setattr(generation, "_cell_room", counting)
    draw = random.Random(20261005)
    answered = refused = fewer = 0
    for _case in range(2400):
        question = _question(draw)
        old_states[0] = new_states[0] = 0
        expected = built(*question)  # type: ignore[operator]
        got = generation._allotted_over(*question)
        assert got == expected, question
        assert new_states[0] <= old_states[0], (question, old_states[0], new_states[0])
        fewer += new_states[0] < old_states[0]
        if expected is None:
            refused += 1
        else:
            answered += 1
    assert answered > 800 and refused > 800, (answered, refused)
    assert fewer > 300, "the conditions passed over no fill the old walk tried"


def test_a_walk_that_remembers_nothing_answers_the_same(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Forgetting a state costs time and never an answer: the memory is a cache.

    With room for no state at all, every seeded question is answered as
    the walk with its full memory answers it -- and one of them, which
    meets a state twice, walks more states to get there (6,098 against
    5,843 over the 800), so the memory being left out is seen. The
    conditions of `generation._cell_entry` leave the walk few states to
    meet twice: over the 800 questions of seed 3891 it met none.
    """
    draw = random.Random(2)
    questions = [_question(draw) for _each in range(800)]
    full = [generation._allotted_over(*question) for question in questions]
    seen = [0]
    asked = generation._cell_room

    def counting(*given):  # type: ignore[no-untyped-def]
        seen[0] += 1
        return asked(*given)

    monkeypatch.setattr(generation, "_cell_room", counting)
    remembered = 0
    for question in questions:
        seen[0] = 0
        generation._allotted_over(*question)
        remembered += seen[0]
    monkeypatch.setattr(generation, "_WALK_MEMORY", 0)
    forgetting = 0
    for place in range(len(questions)):
        seen[0] = 0
        assert generation._allotted_over(*questions[place]) == full[place], questions[place]
        forgetting += seen[0]
    assert forgetting > remembered, (remembered, forgetting)


# Eleven groups of odd sizes asked for three row counts and two column
# counts that no packing meets.
_NO_PACKING = (
    (3, 5, 7, 7, 9, 9, 11, 11, 11, 13, 13),
    [([28, 39, 32], [0, 0, 1, 1, 2, 2]), ([58, 41], [0, 1, 0, 1, 0, 1])],
    [0b111111 for _each in range(11)],
)


class _Watched(set):  # type: ignore[type-arg]
    """A walk's memory that keeps the most members it ever held.

    The walk writes a state down as ``failed |= {mark}``, the one way to
    grow a set the offline policy reads (plan D6.2), so that is the
    operation watched.
    """

    held = 0

    def __ior__(self, marks):  # type: ignore[no-untyped-def]
        grown = super().__ior__(marks)
        self.held = max(self.held, len(self))
        return grown


def _watched_walk(
    monkeypatch: pytest.MonkeyPatch,
) -> "tuple[list[_Watched], list[int]]":
    """Hand every packing walk a watched memory; return the memories and the spans counted."""
    memories: "list[_Watched]" = []
    spans: "list[int]" = []
    walk = generation._cell_walk
    counted = generation._state_bytes

    def watched(*given):  # type: ignore[no-untyped-def]
        nonlocal memories
        memories += [_Watched()]
        return walk(*given, failed=memories[len(memories) - 1])

    def spanned(span: int) -> int:
        nonlocal spans
        spans += [span]
        return counted(span)

    monkeypatch.setattr(generation, "_cell_walk", watched)
    monkeypatch.setattr(generation, "_state_bytes", spanned)
    return memories, spans


def test_the_walk_writes_down_no_more_states_than_its_memory_holds(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The states written down never pass the number `_WALK_MEMORY` holds.

    `_NO_PACKING` makes the walk fail 31 different states on its way to
    saying no packing exists, and it is watched writing each of them
    down. With its memory cut to room for five states it holds five at
    the most, and still says no packing exists. Mutation, run: writing
    down every failed state whatever the room holds 31 again.
    """
    memories, spans = _watched_walk(monkeypatch)
    assert generation._allotted_over(*_NO_PACKING) is None
    assert memories[0].held == 31, memories[0].held
    monkeypatch.setattr(
        generation, "_WALK_MEMORY", generation._state_bytes(spans[0]) * 5
    )
    assert generation._allotted_over(*_NO_PACKING) is None
    assert memories[len(memories) - 1].held == 5, memories[len(memories) - 1].held


def test_a_state_is_one_number_no_other_state_shares_and_its_bytes_are_counted_high(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every state of a small walk is its own number, below the span, and `_state_bytes` covers it.

    Two cells, two sizes of 2 and 1 copies, and counts owed of up to 3
    and 2 on two margins: every state the walk can stand in -- each
    count of copies from nought to all of them, each count owed from
    nought to its published value -- is written as a number with the
    figures `generation._walk_radices` gives the walk, and no two share
    one: a memory that took one state for another would end a branch
    that held an answer. And on the walk of `_NO_PACKING`, every number
    written down is below the span the walk counted its bytes by, and
    `_state_bytes` counts it at no less than twice what `sys.getsizeof`
    reads for it, past the 128 bytes it counts for the set's table.
    Mutations, run: figures that run to the copies rather than one past
    them share numbers; counting a number at 4 bytes for each 30 figures
    alone, or at what `sys.getsizeof` reads and not twice it, counts it
    low.
    """
    counts = [2, 1]
    tops = [[3, 1], [2, 2]]
    radices = generation._walk_radices(counts, tops)
    span = 3
    for radix in radices:
        span = span * radix
    seen: "dict[int, tuple[int, ...]]" = {}
    ranges = [range(2)] + [
        range(top + 1) for top in counts + tops[0] + tops[1]
    ]
    for figures in itertools.product(*ranges):
        left = [figures[1], figures[2]]
        owed = [[figures[3], figures[4]], [figures[5], figures[6]]]
        mark = generation._walk_mark(figures[0], left, owed, radices)
        assert mark not in seen, (figures, seen.get(mark))
        assert 0 <= mark < span
        seen[mark] = figures
    assert len(seen) == 2 * 3 * 2 * 4 * 2 * 3 * 3
    memories, spans = _watched_walk(monkeypatch)
    generation._allotted_over(*_NO_PACKING)
    assert memories[0], "the walk wrote down no state, so nothing was measured"
    for mark in memories[0]:
        assert mark < spans[0]
        assert 2 * sys.getsizeof(mark) <= generation._state_bytes(spans[0]) - 128


# -- Codex's identifier ----------------------------------------------------


def _codex_identifier(k: int) -> contract.Profile:
    """The review's witness at ``k``, described by the real producer and loaded by the real loader."""
    with tempfile.TemporaryDirectory() as home:
        loaded = linear._described(
            pathlib.Path(home), linear._one_odd_group(k), declared=["value"]
        )
    assert isinstance(loaded.columns[0].facts, contract.IdentifierFacts)
    return loaded


@pytest.fixture(scope="module")
def codex_identifiers() -> "dict[int, contract.Profile]":
    """Codex's identifier at 10, 20, 40 and 80 groups beside the one odd group."""
    return {k: _codex_identifier(k) for k in (10, 20, 40, 80)}


def _states_of(
    loaded: contract.Profile, built: "object | None" = None, names: "dict | None" = None
) -> "tuple[int, str, str]":
    """The states one twin's packing walks entered, and the twin's bytes and report.

    With ``built``, the walk as 493f6f8 shipped it answers every packing
    question the generator asks, and its own states are counted.
    """
    with pytest.MonkeyPatch.context() as patch:
        if built is None:
            seen = [0]
            asked = generation._cell_room

            def counting(*given):  # type: ignore[no-untyped-def]
                seen[0] += 1
                return asked(*given)

            patch.setattr(generation, "_cell_room", counting)
        else:
            assert names is not None
            seen = _counted(names)
            patch.setattr(generation, "_allotted_over", built)
        twin = generation.generate(loaded, 0)
        return seen[0], rendering.twin_csv(twin), rendering.report(loaded, twin)


def test_codex_s_identifier_is_written_as_the_walk_it_replaced_wrote_it(
    codex_identifiers: "dict[int, contract.Profile]",
) -> None:
    """At 10, 20 and 40 groups the twin and its report are byte for byte the old walk's."""
    built, names = _as_built()
    for k in (10, 20, 40):
        loaded = codex_identifiers[k]
        _old_states, old_twin, old_report = _states_of(loaded, built, names)
        _states, twin, report = _states_of(loaded)
        assert twin == old_twin, k
        assert report == old_report, k


def walk_states(loaded: contract.Profile) -> int:
    """The states the packing walks enter building one twin of ``loaded``."""
    return _states_of(loaded)[0]


def as_built_walk_states(loaded: contract.Profile) -> int:
    """The same count with the walk as 493f6f8 shipped it."""
    built, names = _as_built()
    return _states_of(loaded, built, names)[0]


def test_the_walk_on_codex_s_identifier_grows_with_its_groups_and_not_past_them(
    codex_identifiers: "dict[int, contract.Profile]",
) -> None:
    """Machine-free: the states the walk enters as the groups double, 20 to 40 to 80.

    The old walk tried every set of the even sizes before the odd group,
    so its states grew with the number of ways to write a number as a
    sum of different whole numbers -- 402 at 20 groups and 8,748 at 40,
    21.8 times, and 102,054 at 60 -- and it is measured here at 20 and
    40 so the measure is known to see that. The generator asks one
    packing question for each of the ``k + 1`` group sizes that could
    carry the shortest value; the walk now refuses all but one of them
    in the state it enters first, and answers the one that packs in a
    state per cell, ``k + 12`` states in all: 32, 52 and 92. Mutation,
    run: with condition 1, condition 2's forced copies, condition 4 and
    condition 5's reserve for a count all taken out, the cell that must
    take the odd group is offered every set of even sizes again, 402
    states to 8,748, 21.8 times. Any one of the four alone answers this
    question, so the questions below hold them apart.
    """
    states = {k: walk_states(codex_identifiers[k]) for k in (20, 40)}
    assert states[40] / states[20] <= DOUBLED_AT_MOST, states
    states[80] = walk_states(codex_identifiers[80])
    assert states[80] / states[40] <= DOUBLED_AT_MOST, states
    old = {k: as_built_walk_states(codex_identifiers[k]) for k in (20, 40)}
    assert old[40] / old[20] >= REPLACED_AT_LEAST, old


def packing_question_fills(
    k: int,
    odd: "tuple[int, ...] | None" = None,
    held_to: "tuple[int, ...]" = (0, 10, 11),
) -> "tuple[list[int] | None, int]":
    """Codex's packing question at ``k`` groups, handed to the walk directly: its answer and the fills it tried.

    The question as the generator asks it -- the classes and alphabets
    the description publishes, every even group in the middle window and
    the odd group held to the shortest -- so the count is the walk's own
    and nothing else the generator does. A fill tried is one call of
    `generation._cell_next`, the call that offers a cell its next fill.
    ``odd`` names the sizes held to the shortest, ``2k + 1`` alone
    unless given; the counts of figures and of ordinary numbers are
    their total. ``held_to`` names the cells they may take, the
    shortest window's unless given.
    """
    held = (2 * k + 1,) if odd is None else odd
    groups = tuple([2 * place for place in range(1, k + 1)] + list(held))
    short = 0
    for size in held:
        short = short + size
    classes = [short, k * (k + 1), 0, 0]
    alphabets = [short, k * (k + 1), 0]
    width = len(alphabets)
    cells = len(classes) * width
    middle = 0
    for cell in (0, 1, 2, 4, 5, 7, 10, 11):
        middle = middle | (1 << cell)
    shortest = 0
    for cell in held_to:
        shortest = shortest | (1 << cell)
    allowed = [middle for _each in range(k)] + [shortest for _each in held]
    margins = [
        (classes, [cell // width for cell in range(cells)]),
        (alphabets, [cell - (cell // width) * width for cell in range(cells)]),
    ]
    fills = [0]
    offered = generation._cell_next

    def counting(*given):  # type: ignore[no-untyped-def]
        fills[0] += 1
        return offered(*given)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_cell_next", counting)
        answer = generation._allotted_over(groups, margins, allowed)
    return answer, fills[0]


def test_the_odd_group_s_cell_is_offered_only_the_odd_group() -> None:
    """The packing question itself, at 60 groups: a fill per cell, where the old walk tried 101,994.

    The cell of ordinary numbers in figures alone must take the whole
    figures count, 121, since no cell after it can take a figure; that
    total is odd, and only the odd group makes it. Every even group goes
    to the cell of numbers too large to hold written in the code
    alphabet, and the odd group to the first cell.
    """
    k = 60
    answer, fills = packing_question_fills(k)
    assert answer == [4 for _each in range(k)] + [0]
    assert fills <= 12, fills


def test_a_size_only_this_cell_can_hold_is_taken_whole() -> None:
    """Two groups only one cell can hold are both taken there, at once.

    Codex's question at 40 groups with a second odd group, 83, held to
    the shortest beside the first, 81. The cell of ordinary numbers in
    figures alone must total the figures count, 164: the two odd groups
    make it, and so do many sets of the even sizes. But no cell after
    this one is open to either odd group -- the other shortest cells
    answer for a count of nought -- so condition 2 takes each here
    whole, and the cell is offered that one fill. Condition 5 sees the
    same thing from the other side: the count of numbers too large to
    hold, which this cell does not answer for, must keep every even
    group, and so must the one cell condition 1 fixes at that whole
    count. Mutation, run: with condition 2's forced copies, condition 1
    and condition 5's reserve for a count all taken out, every set of
    even sizes totalling 164 is offered first, 82,920 fills where this
    takes 12; any one of the three alone answers it, condition 1 through
    the reserve it gives that cell, and the forced copies are held alone
    by a question of `_LESSER_READINGS`.
    """
    k = 40
    answer, fills = packing_question_fills(k, (2 * k + 1, 2 * k + 3))
    assert answer == [4 for _each in range(k)] + [0, 0]
    assert fills <= 12, fills


def test_a_cell_takes_only_a_total_the_cells_after_it_can_finish() -> None:
    """The odd group may stand later too, so nothing takes it whole, and the cell still takes only it.

    Codex's question at 40 groups with the odd group, 81, allowed in the
    cell of numbers too large to hold written in the code alphabet as
    well as in the shortest window. That cell has room for it, so
    condition 2 no longer takes it whole in the cell of ordinary numbers
    in figures alone. But no cell after that one can take a figure, so
    it may total only the whole figures count, 81, which no set of even
    sizes makes: it is offered the odd group alone. On Codex's own
    question either condition is enough, which is why each has a
    question of its own here. Mutation, run: with condition 4, and
    conditions 1 and 5's reserve for a count which see the same thing,
    taken out, every set of even sizes up to 81 is offered first, 8,708
    fills -- the count the walk as 493f6f8 shipped it tries on Codex's
    own question at 40 groups; any one of the three alone answers it.
    """
    k = 40
    answer, fills = packing_question_fills(k, held_to=(0, 4, 10, 11))
    assert answer == [4 for _each in range(k)] + [0]
    assert fills <= 12, fills


# -- the counts read together ----------------------------------------------
#
# Each question below is one the generator asked of the walk for a
# declared identifier the real producer described, its groups, counts
# and permitted cells written out: the identity battery's 300 values of
# 1 to 300 rows in four forms, and two seeded identifiers of 122 and 104
# values in mixed forms (`_mixed_identifier`). Neither 493f6f8's walk
# nor the walk of 45f85b0's three conditions answered any of them within
# 20,000 states.


class _Walked(Exception):
    """The walk passed the states a test allows it."""


def _grid_question(
    sizes: "list[int]", quotas: "list[list[int]]", allowed: "list[int]"
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """A packing question over the grid the counts of ``quotas`` span, as `_grid` lays one out."""
    _cells, part_of = _grid([len(family) for family in quotas])
    return (
        tuple(sizes),
        [(quotas[margin], part_of[margin]) for margin in range(len(quotas))],
        allowed,
    )


def _of_sizes(copies: "dict[int, int]") -> "list[int]":
    """``copies[s]`` groups of size ``s``, the smallest first, as the generator hands them over."""
    sizes: "list[int]" = []
    for size in sorted(copies):
        sizes += [size for _each in range(copies[size])]
    return sizes


def _work(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]",
    limit: int = 20000,
) -> "tuple[list[int] | None, int, int]":
    """The walk's answer to ``question``, and the states it entered and the fills it was asked for.

    A walk past ``limit`` states fails the test that asked at once,
    rather than leaving the suite waiting on a walk that would not end.
    """
    states = [0]
    fills = [0]
    room = generation._cell_room
    offered = generation._cell_next

    def entering(*given):  # type: ignore[no-untyped-def]
        states[0] += 1
        if states[0] > limit:
            raise _Walked(f"the walk passed {limit} states")
        return room(*given)

    def offering(*given):  # type: ignore[no-untyped-def]
        fills[0] += 1
        return offered(*given)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_cell_room", entering)
        patch.setattr(generation, "_cell_next", offering)
        try:
            answer = generation._allotted_over(*question)
        except _Walked as stopped:
            pytest.fail(str(stopped))
    return answer, states[0], fills[0]


def _meets(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]",
    answer: "list[int] | None",
) -> bool:
    """Whether ``answer`` puts every group in a cell it may take and meets every count exactly."""
    if answer is None:
        return False
    groups, margins, allowed = question
    for place in range(len(groups)):
        if (allowed[place] >> answer[place]) & 1 == 0:
            return False
    for quotas, part_of in margins:
        met = [0 for _each in quotas]
        for place in range(len(groups)):
            met[part_of[answer[place]]] += groups[place]
        if met != list(quotas):
            return False
    return True


# The identity battery's 300-value identifier: its second question,
# over classes, alphabets and five counts of lengths.
_LENGTHS_FIX_A_CELL = _grid_question(
    list(range(1, 301)),
    [[23058, 11314, 0, 10778], [23058, 22092, 0], [11790, 10107, 11314, 10778, 1161]],
    [608003542438920851 for _each in range(300)],
)

# The seeded identifier of 122 values: its second question.
_ONE_LEFT_FOR_A_CELL = _grid_question(
    _of_sizes({1: 14, 2: 10, 3: 15, 4: 8, 5: 9, 6: 9, 7: 12, 8: 14, 9: 22, 10: 9}),
    [[362, 134, 0, 198], [238, 332, 124], [150, 134, 20, 124, 20, 54, 192]],
    [9801276246884183809728833 for _each in range(122)],
)

# The seeded identifier of 104 values: its second question.
_THREE_LEFT_FOR_A_COUNT = _grid_question(
    _of_sizes({1: 12, 2: 12, 3: 8, 4: 16, 5: 10, 6: 7, 7: 9, 8: 15, 9: 6, 10: 9}),
    [[383, 160, 0, 0], [212, 160, 171], [17, 160, 168, 198]],
    [151766973418665 for _each in range(104)],
)


def test_a_count_only_one_cell_can_answer_for_fixes_that_cell() -> None:
    """Condition 1: the 300-value identifier's lengths are answered in a state per cell.

    One count of lengths, 10,778, can be met by only one cell the groups
    may stand in, which is in the class of numbers too large to hold, and
    that class owes 10,778 too: so that cell holds all of it and the
    class's other cells hold nought. Read together, the counts say so on
    entering the first of those other cells, and the walk answers in 60
    states, one per cell, every count met. Mutation, run: with the
    counts read one at a time, as 45f85b0's three conditions read them,
    that cell is offered every set of the 300 sizes up to 1,161 first,
    past 20,000 states -- and so is the walk that never closes a cell no
    unplaced group may stand in.
    """
    answer, states, _fills = _work(_LENGTHS_FIX_A_CELL)
    assert _meets(_LENGTHS_FIX_A_CELL, answer)
    assert states <= 60, states


def test_a_cell_that_must_hold_one_row_keeps_a_group_of_one() -> None:
    """Condition 5, a cell's own reserve: a later cell that must hold exactly 1 keeps a group of size 1.

    In the 122-value identifier's question the counts fix a later cell
    of the code alphabet at exactly one row, so it needs a group of size
    1, and the first cell of that alphabet would take all fourteen. The
    walk passes over every fill that takes the last of them the moment
    it decides the size, and answers in 85 states. Mutation, run: with
    no reserve for a single cell it enters 87, and with the counts read
    one at a time, past 20,000.
    """
    answer, states, _fills = _work(_ONE_LEFT_FOR_A_CELL)
    assert _meets(_ONE_LEFT_FOR_A_CELL, answer)
    assert states <= 85, states


def test_a_count_s_loose_cells_keep_what_they_must_make_together() -> None:
    """Condition 5, a count's reserve: the cells of a class whose totals are not fixed keep the 3 rows they owe together.

    In the 104-value identifier's question the counts fix three cells of
    the class of ordinary numbers -- 17, 195 and 168 rows -- and its
    other three cells then owe 3 rows between them, which only groups of
    1 to 3 rows can make, while the first cell of the second class would
    take every such group. The walk answers in 56 states. Mutation, run:
    with no reserve for a count it passes 20,000 states, with the reserve
    read only on entering a cell and never while a fill is decided it
    passes 20,000, and with no reserve for a single cell it enters
    2,475.
    """
    answer, states, _fills = _work(_THREE_LEFT_FOR_A_COUNT)
    assert _meets(_THREE_LEFT_FOR_A_COUNT, answer)
    assert states <= 56, states


# Five seeded questions of `_question` and of the lane's wider battery,
# each one on which one reading below passes over work no other does.
_LESSER_READINGS = (
    (
        "a size only this cell can hold is taken whole, and past its room ends the branch (condition 2)",
        (
            (2, 3, 1, 2, 3, 2, 3, 2, 3, 3, 8, 2, 3, 8, 2, 2),
            [([5, 15, 29], [0, 1, 2])],
            [1, 5, 5, 7, 1, 1, 1, 7, 7, 7, 7, 7, 1, 5, 5, 1],
        ),
        "states",
        1,
    ),
    (
        "a size with nowhere left to go ends the branch (condition 2)",
        _grid_question(
            [9, 3, 1, 9, 1, 1, 9],
            [[0, 13, 11, 9], [10, 9, 14]],
            [2827, 2989, 2989, 3041, 3041, 2989, 2827],
        ),
        "states",
        13,
    ),
    (
        "condition 2 reads the room condition 1 left each cell",
        _grid_question(
            [4, 9, 6, 1, 1, 8, 6],
            [[28, 7], [2, 10, 23], [24, 2, 9]],
            [46697 for _each in range(7)],
        ),
        "states",
        2,
    ),
    (
        "condition 3 reads where each size can still go, not every cell it may take",
        _grid_question(
            [2, 3, 3, 1, 6, 2, 5, 6, 3, 2, 2, 2, 2],
            [[25, 14], [14, 12, 13], [12, 11, 16]],
            [
                254013, 254013, 122542, 122542, 254013, 254013, 254013,
                122542, 254013, 122542, 122542, 122542, 254013,
            ],
        ),
        "states",
        192,
    ),
    (
        "a reserve no fill can meet refuses the state on entering it (condition 5)",
        _grid_question(
            [1, 1, 1, 1, 7, 7, 7, 3, 7],
            [[7, 25, 3], [27, 8], [21, 6, 8]],
            [115817, 223648, 223648, 142713, 115817, 223648, 115817, 223648, 115817],
        ),
        "fills",
        62,
    ),
)


def test_each_lesser_reading_passes_over_work_on_a_question_of_its_own() -> None:
    """Five readings no question above holds apart, each held to a question on which it alone saves work.

    Every answer is the walk's as 493f6f8 shipped it, and each question
    takes no more states, or fills, than the bound beside it. Mutations,
    run, one row each: no size taken whole, 14 states where the first
    refuses on entering; a size with nowhere to go passed over rather
    than ending the branch, 14; condition 2's room read from what each
    count owes alone, 4; condition 3 read over every cell a size may
    take, 202; and the reserves read only while a fill is decided, never
    on entering a cell, 63 fills.
    """
    built, _names = _as_built()
    for reading, question, measure, most in _LESSER_READINGS:
        answer, states, fills = _work(question)
        assert answer == built(*question), reading  # type: ignore[operator]
        spent = states if measure == "states" else fills
        assert spent <= most, (reading, spent)


# A group of 100 rows only the first cell may hold, beside groups of 1 to
# 24 rows the first and the last cell may hold and thirty groups of 10
# rows the last two may hold, over one margin of three counts.
_ONE_GROUP_ONLY_HERE = (
    tuple(list(range(1, 25)) + [100] + [10 for _each in range(30)]),
    [([115, 200, 385], [0, 1, 2])],
    [5 for _each in range(24)] + [1] + [6 for _each in range(30)],
)


def test_a_size_taken_whole_counts_whole_in_the_totals_the_cell_can_reach() -> None:
    """Condition 2's forced copies, read by `_reach_bits`: the cell decides its other sizes knowing the forced group comes too.

    Over the counts 115, 200 and 385, the first cell must total exactly
    115, and the group of 100 rows may stand nowhere else, so condition 2
    takes it there whole. `generation._reach_bits` then adds the whole
    100 to every total the sizes after a place can make, so the groups
    of 1 to 24 rows are decided knowing they must make 15: 3 states, 3
    fills and 9 readings of the reserves, the answer the walk as 493f6f8
    shipped it gives after 5,839 states. Neither the states nor the fills
    see this reading, so the readings are what is held. Mutation, run:
    with `_reach_bits` choosing the group of 100 like any other size --
    the branch for a size the cell takes whole never taken -- the cell
    tries every set of the groups of 1 to 24 that makes 115 without it
    before learning the 100 must come too: the same 3 states, 3 fills
    and answer, and 8,127 readings, 27,207 with groups of 1 to 32 and
    40,557 with groups of 1 to 40, where this reads 9.
    """
    built, _names = _as_built()
    readings = [0]
    met = generation._reserves_met

    def reading(*given):  # type: ignore[no-untyped-def]
        readings[0] += 1
        return met(*given)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_reserves_met", reading)
        answer, states, fills = _work(_ONE_GROUP_ONLY_HERE)
    assert answer == built(*_ONE_GROUP_ONLY_HERE)  # type: ignore[operator]
    assert _meets(_ONE_GROUP_ONLY_HERE, answer)
    assert readings[0] <= 20, readings[0]
    assert states <= 3 and fills <= 3, (states, fills)


# -- the readings of a total ---------------------------------------------
#
# Whether some copies can make a total in a range (`_reach_any` for
# condition 3, `_reserves_met` for condition 5) and which totals leave a
# count what the cells after it can make (`_owed_less`, condition 4) were
# each the halving walk over every copy, with totals as wide as the
# counts. On a declared identifier of 1,414 values held by 1 to 1,414
# rows each -- 1,000,405 rows -- that was about 45 s of the walk's 48
# on a213d43, where 493f6f8's walk took 16. From
# `generation._WIDE_TOTAL` rows on, readings that need no number as wide
# as the total come first (`_makes_a_total`, `_owed_less`); under it the
# halving walk reads them at once, as it did.


def _plain_makes(sizes: "list[tuple[int, int]]", least: int, most: int) -> bool:
    """Whether some copies of ``sizes`` total from ``least`` to ``most``: every total built one copy at a time."""
    if most < 0 or least > most:
        return False
    limit = (1 << (most + 1)) - 1
    reach = 1
    for size, copies in sizes:
        for _each in range(copies):
            reach = (reach | (reach << size)) & limit
    return reach >> max(least, 0) != 0


def _plain_owed(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    where: "list[int]",
    theirs: int,
    due: int,
) -> int:
    """Condition 4's totals built one copy at a time: bit ``t`` set when the copies of ``theirs`` can make ``due - t``."""
    rest = 1 << due
    for place in range(len(keys)):
        if where[place] & theirs == 0:
            continue
        for _each in range(left[place]):
            rest = rest | (rest >> keys[place][0])
    return rest


def _plain_reach_any(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    where: "list[int]",
    cells: int,
    target: int,
) -> bool:
    """Condition 3 read one copy at a time: whether the copies that can reach one of ``cells`` make ``target``."""
    if target < 1:
        return True
    sizes = [
        (keys[place][0], left[place])
        for place in range(len(keys))
        if where[place] & cells and left[place] > 0
    ]
    return _plain_makes(sizes, target, target)


def _plain_reserves(
    keys: "list[tuple[int, int]]",
    left: "list[int]",
    walk: "list[int]",
    reserves: "list[tuple[int, int, list[int], list[int]]]",
) -> bool:
    """Condition 5 read one copy at a time: whether every reserve can still find a total in its range."""
    for least, most, places, _found in reserves:
        sizes: "list[tuple[int, int]]" = []
        for place in places:
            copies = left[place]
            if place < len(walk):
                copies = copies - walk[place]
            if copies > 0:
                sizes += [(keys[place][0], copies)]
        if not _plain_makes(sizes, least, most):
            return False
    return True


def _drawn_sizes(draw: random.Random, wide: bool) -> "list[int]":
    """Ascending group sizes: up to nine of 1 to 200, or a run from 1 beside up to four sizes of up to 2,500."""
    if not wide:
        top = draw.choice((1, 2, 3, 5, 9, 20, 60, 200))
        return sorted(draw.sample(range(1, top + 1), min(draw.randint(0, 9), top)))
    sizes = list(range(1, draw.choice((1, 2, 3, 6, 20, 40)) + 1))
    for _each in range(draw.randint(0, 4)):
        sizes += [draw.randint(2, 2500)]
    return sorted(set(sizes))


def _drawn_range(draw: random.Random, whole: int, wide: bool) -> "tuple[int, int]":
    """A range to read: wide ones from `_WIDE_TOTAL` on where the copies reach it, some empty or below nought."""
    least = draw.randint(-3, whole + 3)
    if wide and whole >= generation._WIDE_TOTAL and draw.random() < 0.8:
        least = draw.randint(generation._WIDE_TOTAL, whole + 3)
    return least, least + draw.choice((-4, -1, 0, 0, 0, 1, 2, 5, 17, 300))


def test_the_readings_of_a_total_answer_as_the_walk_over_every_total() -> None:
    """30,000 seeded inputs on each side of `_WIDE_TOTAL`: each reading of a total gives what the copies give one at a time.

    `_makes_a_total`, `_owed_less`, `_reach_any` and `_reserves_met`
    against the totals built one copy at a time. The sizes come
    ascending, as the walk hands them over, or for `_makes_a_total` in
    no order at all and with a size of nought among them, since its
    answer may need neither; keys of one size come with two permissions,
    as a size written in two forms does; copies run from nought to
    forty; ranges are empty, below nought or past every total; and wide
    totals from `_WIDE_TOTAL` on stand beside narrow ones. Mutations,
    run, each red here: copies totalling exactly ``least`` refused; a
    copy more of a size taken than fits under ``most``; a range from one
    counted as met without a copy; a size of nought divided by; a run
    let through a size two past its end; the run's whole sum left out of
    what it makes; the sizes past the run never walked; a narrow
    condition 4 walked down from one more than is owed; condition 3 read
    wide as a range rather than its exact total; condition 5 read wide
    without what the cell takes; a narrow reserve stopped at its first
    size whatever that made; and the walk `_makes_a_total` falls back on
    read from one past ``least``.
    """
    draw = random.Random(20261007)
    for case in range(30000):
        wide = case % 3 == 0
        sizes = [
            (size, draw.choice((0, 1, 1, 1, 2, 3, 7, 40)))
            for size in _drawn_sizes(draw, wide)
        ]
        if draw.random() < 0.05:
            sizes += [(0, draw.randint(1, 3))]
        if draw.random() < 0.3:
            draw.shuffle(sizes)
        whole = 0
        for size, copies in sizes:
            whole = whole + size * copies
        least, most = _drawn_range(draw, whole, wide)
        assert generation._makes_a_total(sizes, least, most) == _plain_makes(
            sizes, least, most
        ), (sizes, least, most)
        keys = sorted({
            (size, draw.getrandbits(4) | 1)
            for size in _drawn_sizes(draw, wide) + _drawn_sizes(draw, wide)[:3]
        })
        left = [draw.choice((0, 1, 1, 2, 3, 9)) for _each in keys]
        where = [draw.getrandbits(4) for _each in keys]
        theirs = draw.getrandbits(4) | 1
        owed = 0
        for place in range(len(keys)):
            owed = owed + keys[place][0] * left[place]
        due = draw.randint(0, owed + 3)
        if wide and owed >= generation._WIDE_TOTAL:
            due = draw.randint(generation._WIDE_TOTAL, owed + 3)
        assert generation._owed_less(keys, left, where, theirs, due) == _plain_owed(
            keys, left, where, theirs, due
        ), (keys, left, where, theirs, due)
        assert generation._reach_any(keys, left, where, theirs, due) == _plain_reach_any(
            keys, left, where, theirs, due
        ), (keys, left, where, theirs, due)
        walk = [
            draw.randint(0, left[place])
            for place in range(draw.randint(0, len(keys)))
        ]
        reserves: "list[tuple[int, int, list[int], list[int]]]" = []
        for _each in range(draw.randint(1, 3)):
            places = [place for place in range(len(keys)) if draw.random() < 0.7]
            low, high = _drawn_range(draw, owed, wide)
            low = max(low, 1)
            reserves += [(low, max(high, low), places, [-1])]
        assert generation._reserves_met(keys, left, walk, reserves) == _plain_reserves(
            keys, left, walk, reserves
        ), (keys, left, walk, reserves)
        for least, most, places, _found in reserves:
            found = generation._found_from(keys, left, walk, places, least, most)
            above = [place for place in places if place >= found]
            assert (found >= 0) == _plain_reserves(
                keys, left, walk, [(least, most, places, [-1])]
            ), (keys, left, walk, least, most, places)
            if found >= 0:
                assert _plain_reserves(
                    keys, left, walk, [(least, most, above, [-1])]
                ), (keys, left, walk, least, most, places, found)


def _reading_work(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]",
) -> "tuple[list[int] | None, dict[str, int]]":
    """The walk's answer to ``question``, and what its readings of a total did on the way.

    ``wide`` counts the readings of conditions 3 and 5 from `_WIDE_TOTAL`
    on -- condition 3's go to `_makes_a_total` and condition 5's to
    `_found_from` -- and ``walked`` those of them that fell back on the
    walk over every total (`_reach_between`, `_reach_down`); ``remembered``
    counts condition 5's wide reserves met without a reading, where one
    already found the total (`_reserves_met`). ``owed_wide`` counts the
    readings of condition 4 from `_WIDE_TOTAL` on, and ``owed_past``
    those of them that walked sizes past their run. ``owed_narrow`` counts
    the narrower readings of condition 4, and ``owed_not_halved`` those of
    them that were not one walk down from what is owed over every size.
    """
    seen = {
        "wide": 0, "walked": 0, "remembered": 0, "owed_wide": 0, "owed_past": 0,
        "owed_narrow": 0, "owed_not_halved": 0,
    }
    current = {"due": -1, "walks": 0, "halved": 1}
    makes = generation._makes_a_total
    found_from = generation._found_from
    between = generation._reach_between
    down = generation._reach_down
    met = generation._reserves_met
    owed_less = generation._owed_less
    owed_past = generation._owed_past

    def making(*given):  # type: ignore[no-untyped-def]
        seen["wide"] += 1
        return makes(*given)

    def finding(*given):  # type: ignore[no-untyped-def]
        seen["wide"] += 1
        return found_from(*given)

    def walking(*given):  # type: ignore[no-untyped-def]
        seen["walked"] += 1
        return between(*given)

    def walking_down(*given):  # type: ignore[no-untyped-def]
        seen["walked"] += 1
        return down(*given)

    def meeting(keys, left, walk, reserves):  # type: ignore[no-untyped-def]
        for reserve in reserves:
            if reserve[1] >= generation._WIDE_TOTAL and reserve[3][0] >= len(walk):
                seen["remembered"] += 1
        return met(keys, left, walk, reserves)

    def owing(keys, left, where, theirs, due):  # type: ignore[no-untyped-def]
        current["due"] = due
        current["walks"] = 0
        current["halved"] = 1
        answer = owed_less(keys, left, where, theirs, due)
        if due >= generation._WIDE_TOTAL:
            seen["owed_wide"] += 1
        else:
            seen["owed_narrow"] += 1
            if current["walks"] != 1 or not current["halved"]:
                seen["owed_not_halved"] += 1
        return answer

    def passing(keys, left, where, theirs, start, rest):  # type: ignore[no-untyped-def]
        current["walks"] += 1
        due = current["due"]
        if due >= generation._WIDE_TOTAL:
            seen["owed_past"] += 1
        elif start != 0 or rest != 1 << due:
            current["halved"] = 0
        return owed_past(keys, left, where, theirs, start, rest)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_makes_a_total", making)
        patch.setattr(generation, "_found_from", finding)
        patch.setattr(generation, "_reach_between", walking)
        patch.setattr(generation, "_reach_down", walking_down)
        patch.setattr(generation, "_reserves_met", meeting)
        patch.setattr(generation, "_owed_less", owing)
        patch.setattr(generation, "_owed_past", passing)
        answer, _states, _fills = _work(question)
    return answer, seen


def test_each_reading_of_a_total_spares_the_walk_over_every_total() -> None:
    """Each reading settles a question of its own without the walk over every total, and each width is read its own way.

    Two copies of 5 cannot make 11: refused on their total. Three copies
    of 1 and two of 4 make 9: found taking the largest size first; and
    three of 4 make 8 at the place of the 4s, so `_found_from` names
    that place and not the 1s below it. And sizes 1, 2, 4 ... 2,048 make
    every total to 4,095, so condition 4 sets what they leave of 5,000 at
    once. On the 300-value identifier's question (`_LENGTHS_FIX_A_CELL`,
    45,150 rows), 1,192 readings of conditions 3 and 5 from
    `_WIDE_TOTAL` on are asked, as on 489c783: 605 of condition 5's are
    met by the total an earlier reading of the same cell found
    (`_reserves_met`), and of the 587 read, 174 walk every total, where
    489c783 read all 1,192 and walked 431; condition 4 walks past its
    run 57 times in 99. On the 122-value identifier's
    (`_ONE_LEFT_FOR_A_CELL`, 694 rows) no reading is that wide, and each
    of condition 4's 241 is one halving walk down from what is owed.
    Mutations, run, each red here: no refusal on the total, and the
    first question walks every total; no size taken first, and the
    second does; no run, and condition 4 walks past it on the third;
    condition 3, 4 or 5 read the narrow way at every width, or the wide
    way at every width; no total counted wide, or every one; and no
    total remembered, all 1,192 read.
    """
    seen = {"_reach_between": [0], "_reach_down": [0], "_owed_past": [0]}

    def counted(name: str):  # type: ignore[no-untyped-def]
        inner = getattr(generation, name)

        def counting(*given):  # type: ignore[no-untyped-def]
            seen[name][0] += 1
            return inner(*given)

        return counting

    doubling = [(1 << power, 1) for power in range(12)]
    with pytest.MonkeyPatch.context() as patch:
        for name in seen:
            patch.setattr(generation, name, counted(name))
        assert not generation._makes_a_total([(5, 2)], 11, 20)
        assert generation._makes_a_total([(1, 3), (4, 2)], 9, 9)
        assert generation._found_from([(5, 1)], [2], [], [0], 11, 20) == -1
        assert generation._found_from([(1, 1), (4, 1)], [3, 2], [], [0, 1], 9, 9) == 0
        assert generation._found_from([(1, 1), (4, 1)], [3, 3], [], [0, 1], 8, 8) == 1
        assert generation._owed_less(
            doubling, [1 for _each in doubling], [1 for _each in doubling], 1, 5000
        ) == _plain_owed(
            doubling, [1 for _each in doubling], [1 for _each in doubling], 1, 5000
        )
        assert seen == {"_reach_between": [0], "_reach_down": [0], "_owed_past": [0]}, seen
    answer, wide = _reading_work(_LENGTHS_FIX_A_CELL)
    assert _meets(_LENGTHS_FIX_A_CELL, answer)
    assert wide["wide"] + wide["remembered"] >= 1192, wide
    assert wide["remembered"] >= 605 and wide["walked"] <= 174, wide
    assert wide["owed_wide"] >= 99 and wide["owed_past"] <= 57, wide
    answer, narrow = _reading_work(_ONE_LEFT_FOR_A_CELL)
    assert _meets(_ONE_LEFT_FOR_A_CELL, answer)
    assert narrow["wide"] == 0 and narrow["owed_wide"] == 0, narrow
    assert narrow["owed_narrow"] >= 241 and narrow["owed_not_halved"] == 0, narrow


def test_a_record_saying_a_total_needs_no_number_as_wide_names_condition_4_s_run() -> None:
    """Each sentence of this walk's records saying a reading needs no number as wide as the total names condition 4's run.

    From `_WIDE_TOTAL` rows on, conditions 3 and 5 ask `_makes_a_total`,
    whose two readings need no number as wide as the total; condition 4
    asks neither: `_owed_less` sets the run of smallest sizes at once, as
    one number as wide as the total. ddcf147's CHANGELOG, `K-S4-04`'s
    evidence and the ledger note's clause on 25d89cd said such a total is
    read without that number, and ef37517's CHANGELOG and clause still
    counted the run among the two readings, where on the plain-number
    identifier of 1,414 values 119 of the 1,853 wide readings are
    condition 4's, each a number 499,501 to 1,000,406 bits wide set at
    once (plan P4-D389, its second review). The records read are P4-D389's
    CHANGELOG entry, the ledger's note and `K-S4-04`'s evidence; the plan
    is sealed. Mutations, run, each red here: the CHANGELOG and the
    ledger as ef37517 left them, and as ddcf147 did; each of the three
    records alone without the run; and condition 4 walking every size,
    no run, which turns the premise.
    """
    import json
    import re

    asked = {"_makes_a_total": [0], "_owed_past": [0]}

    def counted(name: str):  # type: ignore[no-untyped-def]
        inner = getattr(generation, name)

        def counting(*given):  # type: ignore[no-untyped-def]
            asked[name][0] += 1
            return inner(*given)

        return counting

    doubling = [(1 << power, 1) for power in range(12)]
    with pytest.MonkeyPatch.context() as patch:
        for name in asked:
            patch.setattr(generation, name, counted(name))
        owed = generation._owed_less(
            doubling, [1 for _each in doubling], [1 for _each in doubling], 1, 5000
        )
    assert asked == {"_makes_a_total": [0], "_owed_past": [0]}, (
        f"premise: condition 4 sets its run at once and asks neither reading ({asked})"
    )
    assert owed.bit_length() == 5001, "premise: the run is one number as wide as the total"
    root = pathlib.Path(__file__).resolve().parents[1]
    entries = (root / "CHANGELOG.md").read_text(encoding="utf-8").split("\n### ")
    ledger = json.loads((root / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    records = [("the CHANGELOG", entry) for entry in entries if "P4-D389" in entry]
    records += [("the ledger's note", ledger["measurement_note"])]
    records += [
        ("K-S4-04's evidence", entry["evidence"])
        for entry in ledger["entries"]
        if entry["id"] == "K-S4-04"
    ]
    claim = re.compile(r"\b(?:no|without an?) number as wide as\b")
    run = re.compile(r"\brun of smallest sizes\b[^.;]*\bat once\b")
    said: list[str] = []
    wrong: list[str] = []
    for where, text in records:
        for sentence in re.split(r"(?<=[.;])\s+", " ".join(text.split())):
            if claim.search(sentence):
                said += [where]
                if not run.search(sentence):
                    wrong += [f"{where}: {sentence!r}"]
    assert said, "premise: a record of this walk says a reading needs no number as wide as the total"
    assert wrong == [], "condition 4's run is left among the readings that need no such number:\n" + "\n".join(wrong)


class _Counted(list):  # type: ignore[type-arg]
    """A list that counts the places read from it, to show where a reading stopped."""

    def __init__(self, items: "list[object]") -> None:
        super().__init__(items)
        self.read = 0

    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        self.read += 1
        return super().__getitem__(index)

    def __iter__(self):  # type: ignore[no-untyped-def]
        for index in range(len(self)):
            yield self[index]


def test_a_reading_of_a_total_stops_at_the_first_size_that_settles_it() -> None:
    """The halving walk of `_reserves_met`, of `_reach_between` and of `_reach_down` stops at the first size that brings a total in range.

    Totals only gain members as sizes are added, so the size that first
    brings one in range settles the reading. Ten sizes of 1 to 10 rows
    and a reserve of 1 to 5: the first size makes 1, and the other nine
    are never read. Five thousand copies of 1 and a reading from 4,096
    to 9,000: the first size makes it, and the 7 and the 9 are never
    read; and read from the largest size down, a size of 4,100 rows
    makes it alone, and the 1 and the 7 below it are never read.
    Mutations, run, each red here: a narrow reserve read to its last
    size, all ten read; and the walk `_makes_a_total` falls back on, or
    the one `_found_from` falls back on, read to its last size, all
    three.
    """
    keys = [(size, 1) for size in range(1, 11)]
    left = _Counted([1 for _each in keys])
    assert generation._reserves_met(keys, left, [], [(1, 5, list(range(10)), [-1])])  # type: ignore[arg-type]
    assert left.read == 1, left.read
    sizes = _Counted([(1, 5000), (7, 1), (9, 1)])
    assert generation._reach_between(sizes, 4096, 9000)  # type: ignore[arg-type]
    assert sizes.read == 1, sizes.read
    sizes = _Counted([(1, 3), (7, 1), (4100, 1)])
    assert generation._reach_down(sizes, 4096, 9000) == 2  # type: ignore[arg-type]
    assert sizes.read == 1, sizes.read


def test_a_remembered_total_answers_as_a_new_reading_as_the_walk_goes_on() -> None:
    """Condition 5's remembered totals (`_reserves_met`): read again all along one cell's walk, each answer is a new reading's.

    4,000 seeded cells, each with up to three reserves of both widths
    over drawn sizes and copies, and a walk that decides its places in
    ascending order and goes back as `_cell_next` goes back -- its last
    place one copy fewer, or given up -- for forty steps. The same
    reserves are read at every step, so what one reading remembers is
    there for the next, and each answer is compared with new reserves
    read one copy at a time. Mutations, run, each red here: the total
    remembered also where it was found among the places the walk had
    decided; remembered and never read again whatever the walk decides;
    and taken as met while the walk stands one place past the one
    remembered.
    """
    draw = random.Random(20261008)
    remembered = 0
    for _case in range(4000):
        wide = draw.random() < 0.6
        keys = sorted({
            (size, draw.getrandbits(3) | 1)
            for size in _drawn_sizes(draw, wide) + _drawn_sizes(draw, wide)[:3]
        })
        if not keys:
            continue
        left = [draw.choice((0, 1, 1, 2, 3, 9)) for _each in keys]
        owed = 0
        for place in range(len(keys)):
            owed = owed + keys[place][0] * left[place]
        reserves: "list[tuple[int, int, list[int], list[int]]]" = []
        for _each in range(draw.randint(1, 3)):
            places = [place for place in range(len(keys)) if draw.random() < 0.7]
            low, high = _drawn_range(draw, owed, wide)
            low = max(low, 1)
            reserves += [(low, max(high, low), places, [-1])]
        walk: "list[int]" = []
        for _step in range(40):
            if len(walk) < len(keys) and (not walk or draw.random() < 0.7):
                walk += [draw.randint(0, left[len(walk)])]
            elif walk[len(walk) - 1] > 0:
                walk[len(walk) - 1] -= 1
            else:
                walk = walk[: len(walk) - 1]
            for reserve in reserves:
                if reserve[1] >= generation._WIDE_TOTAL and reserve[3][0] >= len(walk):
                    remembered += 1
            fresh = [(least, most, places, [-1]) for least, most, places, _found in reserves]
            assert generation._reserves_met(keys, left, walk, reserves) == _plain_reserves(
                keys, left, walk, fresh
            ), (keys, left, walk, reserves)
    assert remembered > 1000, remembered


def _mixed_identifier(seed: int) -> "list[str]":
    """A declared identifier of 100 to 160 values written in two to five forms, each held by 1 to 10, 40 or 120 rows.

    Plain numbers, numbers padded to seven figures, codes of two letters
    and four figures, numbers too large to hold, codes with a hyphen,
    numbers in brackets, numbers with a half and negative numbers --
    drawn from `random.Random(7000 + seed)`, so the column is fixed by
    the seed and the standard library's own draws.
    """
    forms = (
        lambda index: f"{index}",
        lambda index: f"{index:07d}",
        lambda index: f"AB{index:04d}",
        lambda index: f"{index:04d}e999",
        lambda index: f"x-{index}",
        lambda index: f"({index})",
        lambda index: f"{index}.5",
        lambda index: f"-{index}",
    )
    draw = random.Random(7000 + seed)
    groups = draw.randint(100, 160)
    largest = draw.choice((10, 40, 120))
    mix = draw.sample(range(len(forms)), draw.randint(2, 5))
    values: "list[str]" = []
    for index in range(groups):
        values += [forms[draw.choice(mix)](index + 1)] * draw.randint(1, largest)
    draw.shuffle(values)
    return values


def mixed_identifier_states(seed: int, limit: int = 20000) -> "int | None":
    """The states the packing walk enters building the twin of `_mixed_identifier(seed)`, or None past ``limit``.

    The column is described by the real producer with `value` declared
    and loaded by the real loader, and its twin built at seed 0; a walk
    past ``limit`` states is stopped there and reads as None, so a
    measure never waits on a walk that would not end.
    """
    with tempfile.TemporaryDirectory() as home:
        loaded = linear._described(
            pathlib.Path(home), _mixed_identifier(seed), declared=["value"]
        )
    assert isinstance(loaded.columns[0].facts, contract.IdentifierFacts)
    states = [0]
    room = generation._cell_room

    def entering(*given):  # type: ignore[no-untyped-def]
        states[0] += 1
        if states[0] > limit:
            raise _Walked(f"the walk passed {limit} states")
        return room(*given)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_cell_room", entering)
        try:
            generation.generate(loaded, 0)
        except _Walked:
            return None
    return states[0]


def test_a_mixed_identifier_the_producer_describes_is_packed_in_few_states() -> None:
    """End to end: two seeded mixed-form identifiers, described by the real producer, build their twins in a few states.

    Seed 20 is 543 rows of 104 values and seed 6 694 rows of 122 -- each
    over the 100 people `synthtwin profile` asks of a declared identifier
    -- and every packing question their twins ask is answered in 70 and
    100 states in all. The walk as 493f6f8 shipped it, and the walk of
    45f85b0's three conditions, each passed 20,000 states on both.
    """
    for seed, most in ((20, 70), (6, 100)):
        states = mixed_identifier_states(seed)
        assert states is not None, f"seed {seed}: the walk passed 20,000 states"
        assert states <= most, (seed, states)


class _Enough(Exception):
    """The packing questions a measure reads have all been answered."""


def seed_105_reserve_readings(limit: int = 2000) -> "tuple[int | None, int, bool]":
    """The reserve readings and the states of the first two packing questions seed 105's twin asks.

    `_mixed_identifier(105)` is described by the real producer with
    `value` declared and loaded by the real loader, and its twin built
    at seed 0 until the walk has answered two packing questions.
    Returns how many times the walk read its reserves
    (`generation._reserves_met`) -- None past ``limit``, where the build
    is stopped, so a measure never waits on a cell that would not end --
    the states it entered, and whether both questions were answered.
    """
    with tempfile.TemporaryDirectory() as home:
        loaded = linear._described(
            pathlib.Path(home), _mixed_identifier(105), declared=["value"]
        )
    assert isinstance(loaded.columns[0].facts, contract.IdentifierFacts)
    readings = [0]
    states = [0]
    answers: "list[object]" = []
    met = generation._reserves_met
    room = generation._cell_room
    packed = generation._allotted_over

    def reading(*given):  # type: ignore[no-untyped-def]
        readings[0] += 1
        if readings[0] > limit:
            raise _Walked(f"the walk read its reserves more than {limit} times")
        return met(*given)

    def entering(*given):  # type: ignore[no-untyped-def]
        states[0] += 1
        return room(*given)

    def asked(*given):  # type: ignore[no-untyped-def]
        nonlocal answers
        answers += [packed(*given)]
        if len(answers) == 2:
            raise _Enough()
        return answers[len(answers) - 1]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_reserves_met", reading)
        patch.setattr(generation, "_cell_room", entering)
        patch.setattr(generation, "_allotted_over", asked)
        try:
            generation.generate(loaded, 0)
        except _Walked:
            return None, states[0], False
        except _Enough:
            pass
    answered = len(answers) == 2 and answers[0] is not None and answers[1] is not None
    return readings[0], states[0], answered


def test_a_reserve_is_read_at_every_size_it_reads_so_one_cell_never_tries_every_way() -> None:
    """Inside one state: a reserve filed under every size it reads stops one cell's fills early.

    Seed 105 of `_mixed_identifier` -- 7,404 rows of 132 values written
    as codes, negative numbers, numbers in brackets, numbers too large
    to hold and numbers padded to seven figures, described by the real
    producer -- has its twin ask the packing walk 33 questions. On the
    second, of 82 sizes over 72 cells, a reserve filed under only the
    last size it reads let the walk try every way of taking the smaller
    sizes into one cell before it read the reserve at all: more than
    2,000,000 readings without leaving the 70th state, and the twin
    still unbuilt after eighteen minutes, which no count of states sees.
    Filed under every size it reads and read wherever the cell takes a
    copy, the first two questions take 27 and 89 states and 282
    readings. Mutations, run: filing each reserve under its last size
    alone passes 2,000 readings on the second question, and reading
    every reserve at every size the cell decides, a copy taken or not,
    passes them over the two -- the answers and the states the same.
    """
    readings, states, answered = seed_105_reserve_readings()
    assert readings is not None, "the walk read its reserves more than 2,000 times"
    assert answered, "a packing question with an answer was refused"
    assert states <= 150, states


def test_a_total_s_binary_figures_are_read_as_bit_length_reads_them() -> None:
    """`generation._binary_length` agrees with `int.bit_length` on nought, the edges of each figure and wide totals.

    The walk reads the largest total a cell may take with it, because
    the offline policy accepts no method call on a computed value; a
    length one figure short would cut the reach the walk descends by.
    Mutation, run: dropping the first figure's own count is off by one
    to four on every number.
    """
    draw = random.Random(1789)
    numbers = [0, 1, 2, 3, 7, 8, 15, 16, 17, 255, 256, (1 << 64) - 1, 1 << 64]
    numbers += [draw.getrandbits(draw.randint(1, 40000)) for _each in range(300)]
    for number in numbers:
        assert generation._binary_length(number) == number.bit_length(), number


# -- the arithmetic a walk does --------------------------------------------
#
# Codex's review of this landing (item 1): a declared identifier of 1,413
# values, value ``i`` held by ``i`` rows -- written ``10000 + i`` where
# ``i`` is odd and with an exponent of nought, ``10002e0``, where it is
# even -- is 998,991 rows the producer describes and the loader accepts,
# and so is the same identifier written with leading zeros and a sign on
# the even values, ``00001`` and ``-0002``. Its twin's first packing
# question took 4.5 s of CPU on 489c783 where the walk as 493f6f8 shipped
# it took 0.57, in the same 12 states with the same answer: each time the
# cell of the even values took one more size, the reserve the last cell
# must find among the sizes left was read again over every one of them,
# a number half a million bits wide shifted once a size, 640 times. No
# count of states or fills sees that, so the measures below count the
# arithmetic itself: every |, &, <<, >>, + and - the walk does on whole
# numbers, at the binary figures it reads and writes.

_METERED = {
    "LShift": operator.lshift,
    "RShift": operator.rshift,
    "BitOr": operator.or_,
    "BitAnd": operator.and_,
    "Add": operator.add,
    "Sub": operator.sub,
}
_METERED_IN_PLACE = {
    "LShift": operator.ilshift,
    "RShift": operator.irshift,
    "BitOr": operator.ior,
    "BitAnd": operator.iand,
    "Add": operator.iadd,
    "Sub": operator.isub,
}

# The values of Codex's identifier the arithmetic is read at: 250,278 and
# 500,500 rows, twice the rows apart.
_ARITHMETIC_AT = (707, 1000)

# What the walk's arithmetic may grow by from the first of those to the
# second, as the rows double. The walk as 493f6f8 shipped it grows 2.82
# times there -- its cost is the totals each cell can reach, one number
# as wide as the cell's count for each of the ``n`` sizes, so it grows
# as the rows to the power one and a half -- and 489c783 grew 5.94 times,
# its reserve read again over every size for each size the cell took.
ARITHMETIC_DOUBLED_AT_MOST = 3.5


class _Metering(ast.NodeTransformer):
    """Send every |, &, <<, >>, + and - through a counter, the assigning forms as well."""

    def visit_BinOp(self, node: ast.BinOp) -> ast.AST:
        self.generic_visit(node)
        name = type(node.op).__name__
        if name not in _METERED:
            return node
        call = ast.Call(
            ast.Name("__metered__", ast.Load()),
            [ast.Constant(name), node.left, node.right],
            [],
        )
        return ast.copy_location(call, node)

    def visit_AugAssign(self, node: ast.AugAssign) -> ast.AST:
        self.generic_visit(node)
        name = type(node.op).__name__
        if name not in _METERED or not isinstance(node.target, ast.Name):
            return node
        call = ast.Call(
            ast.Name("__metered_in_place__", ast.Load()),
            [ast.Constant(name), ast.Name(node.target.id, ast.Load()), node.value],
            [],
        )
        return ast.copy_location(
            ast.Assign([ast.Name(node.target.id, ast.Store())], call), node
        )


def _metered(source: str, label: str) -> "tuple[dict, list[int]]":
    """Every function ``source`` defines, compiled among a copy of the generation module's names with its arithmetic counted.

    The count is the binary figures each |, &, <<, >>, + and - on whole
    numbers reads and writes -- both operands and the answer -- summed
    over the run: a shift of a number a million figures wide counts two
    million, an addition of two small counts a handful. A function
    ``source`` does not define is taken from those names uncounted, so
    ``source`` must hold the whole walk. The answers are the functions'
    own: each operation is done as written, the assigning forms in place.
    """
    bits = [0]

    def metered(name, left, right):  # type: ignore[no-untyped-def]
        answer = _METERED[name](left, right)
        if isinstance(left, int) and isinstance(right, int):
            bits[0] += left.bit_length() + right.bit_length() + answer.bit_length()
        return answer

    def metered_in_place(name, left, right):  # type: ignore[no-untyped-def]
        answer = _METERED_IN_PLACE[name](left, right)
        if isinstance(left, int) and isinstance(right, int):
            bits[0] += left.bit_length() + right.bit_length() + answer.bit_length()
        return answer

    tree = ast.parse(source)
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    tree = _Metering().visit(tree)
    ast.fix_missing_locations(tree)
    names = dict(vars(generation))
    names["__metered__"] = metered
    names["__metered_in_place__"] = metered_in_place
    exec(compile(tree, label, "exec"), names)
    return names, bits


def codex_first_question(
    n: int,
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """The first packing question the twin of Codex's identifier at ``n`` values asks, written out.

    Value ``i`` is held by ``i`` rows, so the groups are 1 to ``n`` rows;
    every value reads as one class of numbers, whose count is every row;
    the odd values are written in figures alone and the even ones in the
    code alphabet, so the alphabets count the odd rows, the even rows and
    nought; and every group may stand in the same cells of the four
    classes by three alphabets, those of permission set 3351.
    """
    odd = 0
    even = 0
    for size in range(1, n + 1):
        if size % 2:
            odd = odd + size
        else:
            even = even + size
    return _grid_question(
        list(range(1, n + 1)),
        [[odd + even, 0, 0, 0], [odd, even, 0]],
        [3351 for _each in range(n)],
    )


def question_arithmetic(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]",
    as_built: bool = False,
    calls: "tuple[str, ...]" = (),
) -> "tuple[object, int, int, dict[str, int]]":
    """The answer, the states and the arithmetic of one walk over ``question``, and how often it called each of ``calls``.

    With ``as_built`` the walk is the one 493f6f8 shipped
    (`stage4_as_built.ALLOTTED_OVER`); without it, every function of
    today's generation module, read from its own file, so a helper the
    walk calls is counted wherever it is written. A function of
    ``calls`` the module does not define is counted at -1.
    """
    if as_built:
        names, bits = _metered(stage4_as_built.ALLOTTED_OVER, "<the walk as built, metered>")
    else:
        source = pathlib.Path(generation.__file__).read_text(encoding="utf-8")
        names, bits = _metered(source, "<generation, metered>")
    states = _counted(names)
    called = {name: _counted(names, name) for name in calls if name in names}
    answer = names["_allotted_over"](*question)
    return answer, states[0], bits[0], {
        name: called[name][0] if name in called else -1 for name in calls
    }


def codex_question_arithmetic(n: int, as_built: bool = False) -> "tuple[object, int, int]":
    """The answer, the states and the arithmetic of one walk over `codex_first_question` at ``n`` values (`question_arithmetic`)."""
    answer, states, bits, _calls = question_arithmetic(codex_first_question(n), as_built)
    return answer, states, bits


def sibling_first_question(
    k: int,
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """The first packing question the twin of the verify's identifier at ``k`` asks, written out.

    One value held by 3 rows beside ``k`` values held by 2, 4, ... ``2k``
    rows, so the groups are 2, 3, 4, 6, ... ``2k`` rows; every value
    reads as one class of numbers, whose count is every row; the 3-row
    value and those held by 4, 8, 12, ... rows are written in figures
    alone and the others, held by 2, 6, 10, ... rows, in the code
    alphabet, so the alphabets count ``3 + 4 + 8 + ...`` -- an odd count,
    the larger for an even ``k`` -- then ``2 + 6 + 10 + ...`` and nought;
    and every group may stand in the cells of permission set 3351.
    """
    sizes = [3] + [2 * step for step in range(1, k + 1)]
    figures = 3
    other = 0
    for step in range(1, k + 1):
        if step % 2 == 0:
            figures = figures + 2 * step
        else:
            other = other + 2 * step
    return _grid_question(
        sorted(sizes),
        [[figures + other, 0, 0, 0], [figures, other, 0]],
        [3351 for _each in sizes],
    )


def test_the_producer_asks_the_packing_question_of_each_identifier_written_out_here() -> None:
    """Premise: the producer describes the three identifiers of the review and its verify, and the twin's first packing question is the one written out.

    Codex's two at 150 values, 11,325 rows: ``10000 + i`` held by ``i``
    rows, the even values written ``10002e0``, and the same values as
    five figures with leading zeros, the even ones signed (``00001``,
    ``-0002``) -- `codex_first_question`. And the verify's at 150 values
    beside the one held by 3 rows, 22,653 rows: five figures with
    leading zeros, ``00001`` held by 3 rows, then ``-0002``, ``00003``,
    ``-0004`` ... held by 2, 4, 6 ... rows, every other one signed --
    `sibling_first_question`. Each is described by the real producer
    with the column declared and loaded by the real loader, and its twin
    is built until the walk is asked its first question, which is the
    question written out.
    """
    sibling: "list[str]" = [f"{1:05d}"] * 3
    for step in range(1, 151):
        sibling += [f"{step + 1:05d}" if step % 2 == 0 else f"{-(step + 1):05d}"] * (2 * step)
    shapes = {
        "an exponent of nought": lambda i: str(10000 + i) if i % 2 else f"{10000 + i}e0",
        "signed with leading zeros": lambda i: f"{i:05d}" if i % 2 else f"{-i:05d}",
    }
    columns: "dict[str, tuple[list[str], tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]]]" = {
        "the verify's, one value held by 3 rows": (sibling, sibling_first_question(150)),
    }
    for shape, written in shapes.items():
        values: "list[str]" = []
        for size in range(1, 151):
            values += [written(size)] * size
        columns[shape] = (values, codex_first_question(150))
    for shape, (values, expected) in columns.items():
        with tempfile.TemporaryDirectory() as home:
            loaded = linear._described(pathlib.Path(home), values, declared=["value"])
        assert isinstance(loaded.columns[0].facts, contract.IdentifierFacts), shape
        asked: "list[object]" = []

        def first(*given):  # type: ignore[no-untyped-def]
            nonlocal asked
            asked += [given]
            raise _Enough()

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_allotted_over", first)
            with pytest.raises(_Enough):
                generation.generate(loaded, 0)
        groups, margins, allowed = asked[0]  # type: ignore[misc]
        assert tuple(groups) == expected[0], shape
        assert [(list(quotas), list(part)) for quotas, part in margins] == expected[1], shape
        assert list(allowed) == expected[2], shape


def test_the_reserves_cost_the_walk_no_arithmetic_past_the_walk_it_replaced() -> None:
    """Machine-free: Codex's identifier of the review of landing S3, its first packing question at 250,278 and 500,500 rows.

    Both walks answer alike in the same 12 states, one per cell, and the
    walk today does no more arithmetic than the walk as 493f6f8 shipped
    it, whose cost is the totals each cell can reach; and as the rows
    double its arithmetic grows less than `ARITHMETIC_DOUBLED_AT_MOST`
    times. 489c783 did 2.3 and 4.9 times the old walk's arithmetic and
    grew 5.94 times, reading the last cell's reserve over every size left
    each time the cell before it took one: 640 times at 998,991 rows,
    each a number half a million bits wide shifted once a size.
    """
    old_bits: "dict[int, int]" = {}
    new_bits: "dict[int, int]" = {}
    for n in _ARITHMETIC_AT:
        old_answer, old_states, old_bits[n] = codex_question_arithmetic(n, as_built=True)
        answer, states, new_bits[n] = codex_question_arithmetic(n)
        assert answer == old_answer, n
        assert states == old_states == 12, (n, states, old_states)
        assert new_bits[n] <= old_bits[n], (n, new_bits, old_bits)
    small, large = _ARITHMETIC_AT
    assert new_bits[large] / new_bits[small] <= ARITHMETIC_DOUBLED_AT_MOST, new_bits


# The verify of that review found the same reading again wherever only a
# small size completes a reserve's total (item 1 still open on c75ef22's
# repair): one value held by 3 rows beside values held by 2, 4, ... 2k
# rows, the 3-row value's notation holding the larger count, so the cell
# of the other notation fills first. The place the reserve remembers is
# the 3-row size's, below every size that cell takes, so the memory never
# holds and each size it took walked the last cell's totals again from
# the largest size down. The values of ``k`` it is read at: 250,503 and
# 499,145 rows, the rows twice apart.
_SIBLING_AT = (500, 706)

# How much arithmetic the walk may do on that question beside the walk as
# 493f6f8 shipped it, and what it does. The question asks for the same
# 12 states, and on entering each the reserves are read once over every
# size where the largest-first readings leave them open -- a cost the
# old walk paid in condition 3's halving walk instead -- so the walk
# today does 1.28 and 1.29 times the old walk's arithmetic; 630a2cc did
# 12.7 and 17.4 times, reading the reserve again at every size.
SIBLING_SHARE_AT_MOST = 1.5


def test_a_reserve_only_a_small_size_completes_is_not_walked_again_at_every_size() -> None:
    """Machine-free: the verify's identifier, its first packing question at 250,503 and 499,145 rows.

    Both walks answer alike in the same 12 states, and the walk today
    does at most `SIBLING_SHARE_AT_MOST` times the arithmetic of the
    walk as 493f6f8 shipped it, and grows less than
    `ARITHMETIC_DOUBLED_AT_MOST` times as the rows double; it walks a
    reserve's totals over every size once or twice on entering a cell,
    and after that reads the table `generation._owed_table` built,
    folding in only the group of 3 rows the cell leaves. 630a2cc walked
    the last cell's totals over every size at 362 of its readings at
    250,503 rows, 12.7 times the old walk's arithmetic and growing 3.86
    times; 489c783, reading them from the smallest size up, 5.4 times.
    Mutations, run, each red here: no table ever built; the table built
    again at every reading it answers; and the stretch of the table the
    walk stands in worked out again at every reading.
    """
    old_bits: "dict[int, int]" = {}
    new_bits: "dict[int, int]" = {}
    for k in _SIBLING_AT:
        old_answer, old_states, old_bits[k], _calls = question_arithmetic(
            sibling_first_question(k), as_built=True
        )
        answer, states, new_bits[k], calls = question_arithmetic(
            sibling_first_question(k), calls=("_reach_down", "_owed_table")
        )
        assert answer == old_answer, k
        assert states == old_states == 12, (k, states, old_states)
        assert new_bits[k] <= SIBLING_SHARE_AT_MOST * old_bits[k], (k, new_bits, old_bits)
        assert calls["_owed_table"] >= 1 and calls["_reach_down"] <= 2 * states, (k, calls)
    small, large = _SIBLING_AT
    assert new_bits[large] / new_bits[small] <= ARITHMETIC_DOUBLED_AT_MOST, new_bits


def test_only_the_cell_the_walk_stands_in_holds_a_table() -> None:
    """The tables of `generation._owed_table` are emptied as the walk leaves their cell, so no state is entered holding one.

    The verify's identifier at 200 values, 40,203 rows: the cell of the
    code alphabet builds a table for the reserve the last cell must
    find, and empties it as the walk moves on, so the last cell, and
    every state the walk enters, finds no memory holding one. Mutation,
    run: the tables never emptied, and the last cell is entered beside
    the first one's.
    """
    built: "list[list[int]]" = []
    held: "list[int]" = []
    table = generation._owed_table
    room = generation._cell_room

    def building(keys, left, places, least, most, found):  # type: ignore[no-untyped-def]
        nonlocal built
        built += [found]
        return table(keys, left, places, least, most, found)

    def entering(*given):  # type: ignore[no-untyped-def]
        nonlocal held
        held += [len([found for found in built if found[2] > 0])]
        return room(*given)

    question = sibling_first_question(200)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_owed_table", building)
        patch.setattr(generation, "_cell_room", entering)
        answer = generation._allotted_over(*question)
    assert _meets(question, answer)
    assert built, "premise: the walk built no table, so nothing was measured"
    assert held == [0 for _each in held], held


def _parity_sizes(draw: random.Random) -> "list[int]":
    """Ascending sizes most of which share a factor, beside a few small ones that do not, so the largest-first readings often fall short."""
    factor = draw.choice((2, 2, 3, 5))
    sizes = {factor * draw.randint(1, 120) for _each in range(draw.randint(8, 60))}
    for _each in range(draw.randint(0, 2)):
        sizes |= {draw.choice((1, 3, 7, 11))}
    return sorted(sizes)


def test_a_reserve_read_from_its_table_answers_as_a_new_reading() -> None:
    """`_owed_table` and `_owed_read`: a reserve read from its table answers as the copies read one at a time, all along a walk.

    2,000 seeded cells, each with up to three reserves of `_WIDE_TOTAL`
    rows or more over 8 to 62 sizes, most sharing a factor beside a few
    that do not -- the shape the largest-first readings leave open --
    and copies from nought to three; each reserve builds its table at
    the first reading those readings leave open (`_WALKED_BEFORE_TABLE`
    set to nought). A walk decides its places in ascending order and
    goes back as `_cell_next` goes back -- its last place one copy
    fewer, or given up -- for sixty steps, now and then emptying the
    tables as `_cell_walk` does on leaving a cell, and every answer is
    compared with new reserves read one copy at a time: 30,890 readings
    off a table, 1,183 of them with every place decided, and 4,963
    stretches worked out as the walk moves between them. Mutations, run,
    each red here: the table built from one copy fewer of a size; the
    decided sizes folded in at every copy, or not at all; the stretch
    the walk stands in not worked out again when it moves to another;
    and a stretch worked out from the kept entry below it rather than
    above.
    """
    draw = random.Random(20261009)
    read = [0]
    stretches = [0]
    decided = [0]
    owed_read = generation._owed_read

    def reading(keys, left, walk, places, most, found):  # type: ignore[no-untyped-def]
        read[0] += 1
        before = found[3]
        answer = owed_read(keys, left, walk, places, most, found)
        if found[3] != before:
            stretches[0] += 1
        if places[len(places) - 1] < len(walk):
            decided[0] += 1
        return answer

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_WALKED_BEFORE_TABLE", 0)
        patch.setattr(generation, "_owed_read", reading)
        for _case in range(2000):
            sizes = _parity_sizes(draw)
            keys = [(size, draw.getrandbits(3) | 1) for size in sizes]
            left = [draw.choice((0, 1, 1, 1, 2, 3)) for _each in keys]
            whole = 0
            for place in range(len(keys)):
                whole = whole + keys[place][0] * left[place]
            if whole < generation._WIDE_TOTAL:
                continue
            reserves: "list[tuple[int, int, list[int], list[int]]]" = []
            for _each in range(draw.randint(1, 3)):
                places = [place for place in range(len(keys)) if draw.random() < 0.8]
                if not places:
                    continue
                least = draw.randint(generation._WIDE_TOTAL, whole)
                if draw.random() < 0.6:
                    least = least | 1
                most = least + draw.choice((0, 0, 0, 1, 2, 9))
                reserves += [(least, most, places, [-1])]
            if not reserves:
                continue
            walk: "list[int]" = []
            for _step in range(60):
                if len(walk) < len(keys) and (not walk or draw.random() < 0.75):
                    walk += [draw.randint(0, left[len(walk)])]
                elif walk[len(walk) - 1] > 0:
                    walk[len(walk) - 1] -= 1
                else:
                    walk = walk[: len(walk) - 1]
                if draw.random() < 0.05:
                    for reserve in reserves:
                        generation._owed_dropped(reserve[3])
                fresh = [(least, most, places, [-1]) for least, most, places, _found in reserves]
                assert generation._reserves_met(keys, left, walk, reserves) == _plain_reserves(
                    keys, left, walk, fresh
                ), (keys, left, walk, reserves)
    assert read[0] > 20000 and stretches[0] > 3000 and decided[0] > 600, (read, stretches, decided)


# -- how far condition 1 narrows -------------------------------------------
#
# Codex's review of this landing (item 2): `_bounds_settled` narrowed each
# later cell's least and most for at most one round more than there are
# cells, where G9.5 and plan P4-D389 say it narrows until no end moves.
# The grid below is Codex's: four classes by three alphabets by three
# more counts, 4,150 groups of one row each permitted in six cells, two
# of its counts answered for by the same open cells and one row apart,
# so no filling meets them; with cell 10 open as well, one does.


def _codex_grid(
    scale: int = 1, one_row_apart: bool = False, wider: bool = False
) -> "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]":
    """Codex's grid with every count and the groups ``scale`` times larger.

    With ``one_row_apart`` its two conflicting counts stay one row apart
    at every scale; with ``wider`` cell 10 is open too, and holds the
    row they differ by.
    """
    quotas = [
        [1593 * scale, 1731 * scale, 826 * scale, 0],
        [1322 * scale, 1851 * scale, 977 * scale],
        [1730 * scale, 2420 * scale, 0],
    ]
    if one_row_apart:
        quotas[2] = [1731 * scale - 1, 2419 * scale + 1, 0]
    mask = 0
    for cell in (1, 4, 9, 12, 15, 22) + ((10,) if wider else ()):
        mask = mask | (1 << cell)
    return _grid_question(
        [1 for _each in range(4150 * scale)],
        quotas,
        [mask for _each in range(4150 * scale)],
    )


def narrowing_rounds(
    question: "tuple[tuple[int, ...], list[tuple[list[int], list[int]]], list[int]]",
) -> "tuple[bool, int, int]":
    """Condition 1 on entering the first cell of ``question``: what it answers, its rounds, and the cells.

    The ends `_cell_entry` hands `generation._bounds_settled` there are
    narrowed again with the counts owed read through a counter: a round
    reads every count once, so the rounds are the counts read over the
    counts there are, a round cut short by a refusal counted whole.
    """
    seen: "list[tuple[object, ...]]" = []

    def first(owed, families, cell, low, high):  # type: ignore[no-untyped-def]
        nonlocal seen
        seen += [(owed, families, cell, low, high)]
        raise _Enough()

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_bounds_settled", first)
        with pytest.raises(_Enough):
            generation._allotted_over(*question)
    owed, families, cell, low, high = seen[0]
    read = _Counted(owed)  # type: ignore[arg-type]
    answer = generation._bounds_settled(read, families, cell, low, high)  # type: ignore[arg-type]
    return answer, -(-read.read // len(families)), len(low)  # type: ignore[arg-type]


def test_condition_1_settles_so_codex_s_grid_is_refused_on_entering() -> None:
    """Condition 1 narrows until no end moves (method G9.5), so the walk refuses Codex's grid in its first state.

    On entering the first cell the narrowing refuses at its 378th round,
    ten times the grid's 36 cells, and the walk enters one state before
    answering that no filling meets the counts -- the answer of the walk
    as 493f6f8 shipped it, which enters 4,748. 489c783 stopped the
    narrowing after 37 rounds with ends still moving, let the cell be
    filled and entered 706 states (red there). The rounds grow with the
    counts and no faster: with every count ten times larger and the two
    counts the same cells answer for still one row apart, 3,771, and
    the walk still enters one state. With cell 10 open the counts can be
    met, and the narrowing settles in 4 rounds and the walk answers in 36
    states (plan P4-D389, Codex's review of this landing, item 2).
    Mutations, run, each red here: the rounds stopped at one more than
    the cells, or at ten times the cells; and the counts read again only
    while a most moves.
    """
    built, names = _as_built()
    question = _codex_grid()
    kept, rounds, cells = narrowing_rounds(question)
    assert kept is False and rounds > cells + 1, (kept, rounds, cells)
    old_states = _counted(names)
    expected = built(*question)  # type: ignore[operator]
    answer, states, _fills = _work(question)
    assert answer == expected is None
    assert states == 1 < old_states[0], (states, old_states[0])
    tenfold = _codex_grid(10, one_row_apart=True)
    kept, rounds_ten, _cells = narrowing_rounds(tenfold)
    assert kept is False and rounds < rounds_ten <= 11 * rounds, (rounds, rounds_ten)
    answer, states, _fills = _work(tenfold)
    assert answer is None and states == 1, states
    wider = _codex_grid(wider=True)
    kept, rounds_wide, _cells = narrowing_rounds(wider)
    assert kept is True and rounds_wide <= cells + 1, rounds_wide
    answer, states, _fills = _work(wider)
    assert _meets(wider, answer) and states <= 36, states

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

import itertools
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

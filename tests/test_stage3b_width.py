"""Lane G2 of stage 3b: a tail pair that proves a wider cell lets the end past the width (plan P4-D377).

Method G6.6.8. The width census counts a width fewer than the line wrote
into its commonest (plan P4-D222), so `1000` to `1148` beside one `99999`
publishes one width of four figures, and the derived end was held at
`9998`: the twins missed the column's mean and spread at every seed
(`K-S3-22`, 99 of its 111 misses). A published pair proves the furthest
row stands at least `rms**2 / d1` from its boundary; where a width hold
lowers the end inside that reach, and at or past the mean distance, the
hold stands aside and the end goes to the first whole number at or past
the reach. The width walk then leaves up to the line less one of the
tail's own cells past every named width, stopping before their
distances pass the pair's own totals; it moves the tail's other cells
past the width under it before serving any demand, and takes every cell
still past it off the unpadded demand the census counted it into.

Each clause here is held up by a test and, beside it, the mutant that
withdraws it and turns the test's own measurement the other way. The
end rule is also frozen in `tail_width_past_the_reach`
(tests/reference/generation-branch-vectors-23.json); the walk has no
frozen case, because the oracle does not run G6.6's walk, so it is
pinned here.

Every column is built from a fixed seed at run time; nothing is read
from disk but the tree's own code.
"""

from __future__ import annotations

import math
import pathlib
import random

import pytest

import complement_reader as reader
import kpi_shapes
from synthtwin import contract, generation, parsing

SEEDS = (0, 4, 9)

_REAL_PAST_THE_WIDTH = contract._past_the_width
_REAL_FREED = generation._freed_past_the_width
_REAL_PULLED = generation._pulled_under_the_width


def _text(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


def _described(tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int) -> kpi_shapes.Described:
    return kpi_shapes.describe(tmp_path / name, name, _text(cells), floor)


def _facts(described: kpi_shapes.Described) -> contract.NumericFacts:
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    return facts


def _twin_numbers(described: kpi_shapes.Described, seed: int) -> "list[float]":
    text = kpi_shapes.twin_text(described, seed)
    return [float(line) for line in text.split("\n")[1:] if line]


def _missed(described: kpi_shapes.Described, seed: int) -> "list[str]":
    text = kpi_shapes.twin_text(described, seed)
    return kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))


def _reach_end(block: dict, side: str, boundary: float) -> float:
    """The first whole number at or past the side's reach, from the published pair alone."""
    tail = block["tails"][side]
    root = tail["rms_distance"]
    reach = root * (root / tail["mean_distance"])
    reach = reach - reach / 16777216.0
    if side == "high":
        return float(math.ceil(boundary + reach))
    return float(math.floor(boundary - reach))


# -- the columns ------------------------------------------------------------


def _ten_wide() -> "list[str]":
    """1000 to 1089 and ten of five figures, 10000 to 10009: the census names four on every cell."""
    return [str(1000 + step) for step in range(90)] + [str(10000 + step) for step in range(10)]


def _held_heap() -> "list[str]":
    """9000 to 9500 a thousand times, `9999` fifteen times (the mode, so held) and one `10500`."""
    draw = random.Random("p4d377/held-heap")
    return [str(draw.randint(9000, 9500)) for _row in range(1000)] + ["9999"] * 15 + ["10500"]


def _wide_inside_the_mean() -> "list[str]":
    """110 cells nine apart from 9000 and ten from 20000 to 29000, a thousand apart."""
    return [str(9000 + 9 * step) for step in range(110)] + [str(20000 + 1000 * step) for step in range(10)]


def _mixed(padded: int, unpadded: int, far: "list[str]", seed: int) -> "list[str]":
    """Codes `0001` to `0999` padded to four, plain four-figure numbers beside them, then the far cells."""
    draw = random.Random(f"g2/mixed/{padded}/{unpadded}/{far[0]}/{seed}")
    cells = [f"{draw.randint(1, 999):04}" for _row in range(padded)]
    cells += [str(draw.randint(1000, 9999)) for _row in range(unpadded)]
    return cells + far


def _narrow_beside_five() -> "list[str]":
    """Nine four-figure cells, 1000 to 9000, beside 51 of five figures: the census names five."""
    return (
        [str(1000 + 1000 * step) for step in range(9)]
        + [str(30000 + 500 * step) for step in range(3)]
        + [str(40000 + 1000 * step) for step in range(48)]
    )


_PAST_THE_REACH = (
    ("cfh99999_150", reader.shape("cfh99999", 150, 1), 11),
    ("pad99999_150", reader.shape("pad99999", 150, 1), 11),
    ("par20d_150_s2", reader.shape("par20d", 150, 2), 36),
)


# -- 1. the end -------------------------------------------------------------


@pytest.mark.parametrize("name,cells,floor", _PAST_THE_REACH, ids=[one[0] for one in _PAST_THE_REACH])
def test_the_end_stands_at_the_first_whole_number_past_the_pair_s_reach(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int
) -> None:
    """K-S3-22's own columns: the high end is the reach, and the twins miss nothing at seeds 0, 4 and 9."""
    described = _described(tmp_path, name, cells, floor)
    block = described.document["columns"][0]
    ladder = contract.tail_ladder(_facts(described))
    assert ladder is not None and ladder.high is not None
    widest = max(int(key) for key in block["field_widths"]) - (1 if block["pad_widths"] else 0)
    assert ladder.high.boundary + 1.0 < 10.0 ** widest <= max(float(cell) for cell in cells), (
        "premise: the census's ceiling stands below the real largest value"
    )
    assert ladder.high.end == _reach_end(block, "high", ladder.high.boundary)
    assert ladder.high.end > 10.0 ** widest - 1.0
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        assert max(written) == ladder.high.end, f"seed {seed}"
        assert _missed(described, seed) == [], f"seed {seed}"


def test_withdrawn_the_end_stays_under_the_width_and_the_moments_are_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant of the end rule: `1000` to `1148` beside `99999` ends at 9998 and misses its mean and spread."""
    described = _described(tmp_path, "cfh99999_150", reader.shape("cfh99999", 150, 1), 11)
    monkeypatch.setattr(contract, "_past_the_width", lambda clamped, *_rest: clamped)
    ladder = contract.tail_ladder(_facts(described))
    assert ladder is not None and ladder.high is not None and ladder.high.end == 9998.0
    for seed in SEEDS:
        missed = _missed(described, seed)
        assert "value:moments.mean" in missed and "value:moments.std" in missed, f"seed {seed}: {missed}"


# -- 2. the walk ------------------------------------------------------------


def _past(written: "list[float]", ceiling: float) -> int:
    return len([value for value in written if value > ceiling])


def test_the_walk_leaves_the_tail_s_wide_cells_past_the_width(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ten five-figure cells under a census of four: the walk frees the tail's wide rows, at most the line less one.

    Its mutant frees nothing, and the walk pulls a row the ladder put past
    the width back under it, at every seed.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    assert described.document["columns"][0]["field_widths"] == {"4": 100}, "premise: one width of four"
    room = parsing.census_floor(11) - 1
    freed = {seed: _past(_twin_numbers(described, seed), 9999.0) for seed in SEEDS}
    for seed in SEEDS:
        assert 1 < freed[seed] <= room, f"seed {seed}: {freed[seed]}"
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(generation, "_freed_past_the_width", lambda *_arguments: (0, []))
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 9999.0) < freed[seed], f"seed {seed}"


def _freed_without_the_pair_s_totals(facts, layout, values, demands, floor):  # type: ignore[no-untyped-def]
    """The walk's freeing with its stop at the pair's own totals withdrawn: every wide tail cell, up to the line less one."""
    if _REAL_FREED(facts, layout, values, demands, floor) == (0, []):
        return 0, []
    widest = max(wanted for wanted, _exact, _cells in demands)
    freed = 0
    for place in sorted(generation._tail_strata(facts, layout)):
        if values[place] > 10.0 ** widest - 1.0:
            freed += layout.sizes[place]
    return min(freed, parsing.census_floor(floor) - 1), []


def test_the_freed_cells_stop_at_the_pair_s_own_totals(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`1000` to `1398` beside one `99999`: the pair carries one far row, so one cell stands past the width.

    The ladder puts a second row past it, by the end; the end's own
    distance already spends the pair's total of squares, so the walk pulls
    that row under the width. Its mutant frees every wide tail cell, and
    the twin writes two cells near 99,934 where the table holds one.
    """
    described = _described(tmp_path, "cfh99999_400", reader.shape("cfh99999", 400, 1), 11)
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 9999.0) == 1, f"seed {seed}"
    monkeypatch.setattr(generation, "_freed_past_the_width", _freed_without_the_pair_s_totals)
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 9999.0) == 2, f"seed {seed}"


def _demands_less_the_commonest(demands, freed):  # type: ignore[no-untyped-def]
    """The demand choice withdrawn: the freed cells come off the demand asking for the most cells, of either kind."""
    if freed < 1 or not demands:
        return demands
    chosen = 0
    for index in range(1, len(demands)):
        if demands[index][2] > demands[chosen][2] or (
            demands[index][2] == demands[chosen][2] and demands[index][0] > demands[chosen][0]
        ):
            chosen = index
    return [
        (wanted, exact, cells - freed if index == chosen else cells)
        for index, (wanted, exact, cells) in enumerate(demands)
        if cells - (freed if index == chosen else 0) > 0
    ]


def test_the_cells_still_past_come_off_the_unpadded_demand(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """200 padded codes beside 100 four-figure numbers, `99999` and `88888`: the unpadded demand gives up the cells.

    The two far cells are plain, so the census counts them into the width
    most unpadded cells wrote; the twin writes its own cells past the width
    plainly too, so they come off the exact demand and the padded ceiling
    still asks for all 200 small values. Its mutant takes them off the
    demand asking for the most cells, which is the padded one here, and
    the twin misses the padded census.
    """
    described = _described(tmp_path, "mixed_far2", _mixed(200, 100, ["99999", "88888"], 3), 11)
    block = described.document["columns"][0]
    assert block["pad_widths"] == {"4": 200} and block["field_widths"] == {"4": 302}, "premise: two far cells pooled"
    assert generation._field_demands(_facts(described)) == [(3, 0, 200), (4, 1, 102)], "premise: the padded demand is the larger"
    for seed in SEEDS:
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(generation, "_demands_less_the_freed", _demands_less_the_commonest)
    for seed in SEEDS:
        assert "value:pads.published.4" in _missed(described, seed), f"seed {seed}"


def test_the_cells_past_the_pair_s_stop_are_pulled_under_first(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """60 padded codes beside 90 four-figure numbers and one `99999`: the tail cells the pair cannot carry go under the width first.

    The staircase to the pair's end puts more cells past `9999` than the
    pair's totals leave room for. Before any demand is served the pass
    moves them under the width where their room lets it, and counts the
    one the order holds past it with the cells freed; the walk then has
    the four-figure cell it moves down to the padded ceiling, and the
    twins miss nothing. Three mutants: withdrawing both halves leaves
    them to the walk, which stops at the padded ceiling first; counting
    them without moving them leaves one more cell past the width at
    every seed; moving them without counting the one left leaves the
    unpadded demand a cell too many, and the padded census is missed
    again. The padded misses fall at two of the three seeds each time.
    """
    described = _described(tmp_path, "mixed_one_far", _mixed(60, 90, ["99999"], 2), 11)
    assert described.document["columns"][0]["pad_widths"] == {"4": 60}, "premise: sixty padded cells"
    past = {seed: _past(_twin_numbers(described, seed), 9999.0) for seed in SEEDS}
    for seed in SEEDS:
        assert _missed(described, seed) == [], f"seed {seed}"

    def padded_missed() -> "list[int]":
        return [seed for seed in SEEDS if "value:pads.published.4" in _missed(described, seed)]

    with monkeypatch.context() as patch:
        patch.setattr(generation, "_freed_past_the_width", lambda *arguments: (_REAL_FREED(*arguments)[0], []))
        assert len(padded_missed()) >= 2
    with monkeypatch.context() as patch:
        patch.setattr(
            generation,
            "_pulled_under_the_width",
            lambda _column, _facts, layout, _rungs, values, _tails, places, _widest: (
                list(values),
                sum(layout.sizes[place] for place in places),
            ),
        )
        for seed in SEEDS:
            assert _past(_twin_numbers(described, seed), 9999.0) > past[seed], f"seed {seed}"
    with monkeypatch.context() as patch:
        patch.setattr(generation, "_pulled_under_the_width", lambda *arguments: (_REAL_PULLED(*arguments)[0], 0))
        assert len(padded_missed()) >= 2


# -- 3. what the rule leaves alone --------------------------------------------


def test_a_hold_on_a_stand_in_the_block_holds_stays(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`9999` fifteen times, the block's mode, beside one `10500`: the end stays on the heap.

    The pair's reach passes 9999, which stands at or past the mean
    distance, so the rule would take the end past the width; the hold put
    it on a stand-in the block publishes as held, and the table's own heap
    is kept. Its mutant reads no held stand-in and the end leaves 9999.
    """
    described = _described(tmp_path, "held_heap", _held_heap(), 11)
    block = described.document["columns"][0]
    facts = _facts(described)
    assert facts.kept_stand_ins == (9999.0,) and block["mode"] == 9999.0, "premise: 9999 is held"
    ladder = contract.tail_ladder(facts)
    assert ladder is not None and ladder.high is not None
    tail = block["tails"]["high"]
    reach = contract.pair_reach(tail["mean_distance"], tail["rms_distance"])
    assert tail["mean_distance"] <= 9999.0 - ladder.high.boundary < reach, "premise: the rule would fire"
    assert ladder.high.end == 9999.0
    for seed in SEEDS:
        held = len([value for value in _twin_numbers(described, seed) if value == 9999.0])
        assert abs(held - 15) <= max(15 // 4, 1016 // 100), f"seed {seed}: {held}"
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(
        contract,
        "_past_the_width",
        lambda clamped, held, low, boundary, pair, kept: _REAL_PAST_THE_WIDTH(clamped, held, low, boundary, pair, ()),
    )
    moved = contract.tail_ladder(facts)
    assert moved is not None and moved.high is not None and moved.high.end > 9999.0


def _past_inside_the_mean(clamped, held, low, boundary, pair, kept):  # type: ignore[no-untyped-def]
    """The end rule with its mean-distance clause withdrawn."""
    return _REAL_PAST_THE_WIDTH(clamped, held, low, boundary, (0.0, pair[1]), kept)


def test_inside_the_mean_distance_the_guard_s_fitted_end_stands(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ten cells 20000 to 29000 beside 9000 to 9981: the hold falls inside the mean distance, and the guard keeps the fitted end.

    Its mutant reads the reach there too, and the end moves in from the
    fitted one, crowding the tail's rows onto it.
    """
    described = _described(tmp_path, "inside_the_mean", _wide_inside_the_mean(), 11)
    block = described.document["columns"][0]
    facts = _facts(described)
    ladder = contract.tail_ladder(facts)
    assert ladder is not None and ladder.high is not None
    assert 9999.0 - ladder.high.boundary < block["tails"]["high"]["mean_distance"], "premise: inside the mean distance"
    monkeypatch.setattr(contract, "_past_the_width", lambda clamped, *_rest: clamped)
    fitted = contract.tail_ladder(facts)
    assert fitted is not None and fitted.high is not None
    assert ladder.high.end == fitted.high.end
    monkeypatch.setattr(contract, "_past_the_width", _past_inside_the_mean)
    crowded = contract.tail_ladder(facts)
    assert crowded is not None and crowded.high is not None
    assert crowded.high.end == _reach_end(block, "high", ladder.high.boundary) < fitted.high.end


def test_a_hold_raising_a_size_is_a_floor_and_is_left_alone(tmp_path: pathlib.Path) -> None:
    """Nine four-figure cells under a census of five: the low end stays at 10000, the census's floor.

    The pair's reach passes 10000 on the low side too, but that hold raised
    the end's size, a floor the lane does not read; only a ceiling stands
    aside (`contract._past_the_width`'s first clause). Asked of the
    function itself, with the ceiling clause the one thing between.
    """
    described = _described(tmp_path, "narrow_beside_five", _narrow_beside_five(), 11)
    block = described.document["columns"][0]
    facts = _facts(described)
    assert block["field_widths"] == {"5": 60}, "premise: one width of five"
    ladder = contract.tail_ladder(facts)
    assert ladder is not None and ladder.low is not None
    boundary = ladder.low.boundary
    tail = block["tails"]["low"]
    pair = (tail["mean_distance"], contract.pair_reach(tail["mean_distance"], tail["rms_distance"]))
    assert pair[0] <= boundary - 10000.0 < pair[1], "premise: the reach passes the floor"
    assert ladder.low.end == 10000.0
    # The function, handed a raised size, leaves it; handed the same
    # distance as a lowered size, it moves it to the reach.
    assert contract._past_the_width(10000.0, 1.0, True, boundary, pair, ()) == 10000.0
    assert contract._past_the_width(10000.0, -1.0e9, True, boundary, pair, ()) == _reach_end(block, "low", boundary)


# -- 4. the reach itself ----------------------------------------------------


def test_the_reach_is_bhatia_and_davis_s_at_a_least_distance_of_nought() -> None:
    """rms**2 / d1, lowered by 2**-24 of itself; nought without a pair; the largest finite number past the range."""
    assert contract.pair_reach(None, 3.0) == 0.0
    assert contract.pair_reach(2.0, None) == 0.0
    assert contract.pair_reach(0.0, 3.0) == 0.0
    reach = contract.pair_reach(2.0, 4.0)
    assert reach < 8.0 and 8.0 - reach == pytest.approx(8.0 / 16777216.0)
    assert contract.pair_reach(1e-300, 1e200) == contract._LARGEST_FINITE
    # Every set of distances at least nought has its furthest at or past it.
    draw = random.Random("p4d377/reach")
    for _trial in range(200):
        distances = [draw.expovariate(1.0) ** draw.choice((1, 2, 3)) for _row in range(draw.randint(1, 40))]
        mean = sum(distances) / len(distances)
        root = math.sqrt(sum(one * one for one in distances) / len(distances))
        assert max(distances) >= contract.pair_reach(mean, root)

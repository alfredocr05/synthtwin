"""Lane G2 of stage 3b: a tail pair that proves a wider cell lets the end past the width (plan P4-D377).

Method G6.6.8. The width census counts a width fewer than the line wrote
into its commonest (plan P4-D222), so `1000` to `1148` beside one `99999`
publishes one width of four figures, and the derived end was held at
`9998`: the twins missed the column's mean and spread at every seed
(`K-S3-22`, 99 of its 111 misses). A published pair proves the furthest
row stands at least `rms**2 / d1` from its boundary; where a width hold
lowers the end inside that reach, and at or past the mean distance, the
hold stands aside and the end goes to the first whole number at or past
the reach (rule 1).

The width walk (rule 2) then leaves past every named width only the
tail's outermost strata that fit the line less one and the pair's own
totals -- its squares after those the tail's strata under the width
already hold -- and moves every other stratum of the tail past the width
under it before any demand is served: the end's own among them, beside
its inner neighbour where the end stays past the width, where the pair's
squares put it where the end moves too, and onto the end the width held
on 110cb46 where no value under the width is free. It takes the cells
left past it off the demand the census counted them into. On a side
rule 1 moved it always walks; on another proven side, where 110cb46's
end already stood past the width, its walk stands only where it serves
the census strictly better and leaves neither published moment further
off, and is given up where a stratum finds no room. A side is proven
only where the width census counts every number of the column, and a
far cell a pair proves past every named pad is written plain (method
G6.3).

Each clause is held up by a test here and, where a mutant is cheap to
write, by the mutant that withdraws it turning the test's own
measurement the other way. The repair round ran a source mutant of each
of 64 clauses of the two rules and of G6.3's give-up against this file,
and every one turns it red. The end rule is also frozen in
`tail_width_past_the_reach` (tests/reference/generation-branch-vectors-23.json);
the walk has no frozen case, because the oracle does not run G6.6's
walk, so it is pinned here. The mean and spread 110cb46 wrote on the
first skeptic's shapes are the constants named `_ON_110CB46`.

Every column is built from a fixed seed at run time; nothing is read
from disk but the tree's own code.
"""

from __future__ import annotations

import csv
import dataclasses
import io
import math
import pathlib
import random
import statistics

import pytest

import complement_reader as reader
import kpi_shapes
from synthtwin import contract, generation, parsing

SEEDS = (0, 4, 9)

_REAL_PAST_THE_WIDTH = contract._past_the_width
_REAL_WALK = generation._walked_past_the_width
_REAL_PULLED = generation._pulled_under_the_width
_REAL_WORN = generation._point_free_form_worn
_REAL_OWED = generation._census_owed


def _text(cells: "list[str]") -> str:
    return "value\n" + "\n".join(f'"{cell}"' if "," in cell else cell for cell in cells) + "\n"


def _described(tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int) -> kpi_shapes.Described:
    return kpi_shapes.describe(tmp_path / name, name, _text(cells), floor)


def _facts(described: kpi_shapes.Described) -> contract.NumericFacts:
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    return facts


def _cells(described: kpi_shapes.Described, seed: int) -> "list[str]":
    text = kpi_shapes.twin_text(described, seed)
    return [row[0] for row in list(csv.reader(io.StringIO(text)))[1:] if row]


def _numbers(cells: "list[str]") -> "list[float]":
    found: "list[float]" = []
    for cell in cells:
        number = parsing.parse_number(cell)
        if number is not None:
            found += [number]
    return found


def _twin_numbers(described: kpi_shapes.Described, seed: int) -> "list[float]":
    return _numbers(_cells(described, seed))


def _missed(described: kpi_shapes.Described, seed: int) -> "list[str]":
    text = kpi_shapes.twin_text(described, seed)
    return kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))


def _errors(cells: "list[str]", written: "list[float]") -> "tuple[float, float]":
    """The twin's mean off the real one and its spread's ratio off one, both against the real spread."""
    real = _numbers(cells)
    spread = statistics.pstdev(real)
    return (
        abs(statistics.fmean(written) - statistics.fmean(real)) / spread,
        abs(statistics.pstdev(written) / spread - 1.0),
    )


def _own_census(tmp_path: pathlib.Path, described: kpi_shapes.Described, seed: int, floor: int) -> "tuple[dict, dict]":
    """The twin's own `field_widths` and `pad_widths`, described at the source's floor."""
    text = kpi_shapes.twin_text(described, seed)
    own = kpi_shapes.describe(tmp_path / f"own-{seed}", "own", text, floor).document["columns"][0]
    return own["field_widths"], own["pad_widths"]


def _census(described: kpi_shapes.Described) -> "tuple[dict, dict]":
    block = described.document["columns"][0]
    return block["field_widths"], block["pad_widths"]


def _past(written: "list[float]", ceiling: float) -> int:
    return len([value for value in written if abs(value) > ceiling])


def _reach_end(block: dict, side: str, boundary: float) -> float:
    """The first whole number at or past the side's reach, from the published pair alone."""
    tail = block["tails"][side]
    root = tail["rms_distance"]
    reach = root * (root / tail["mean_distance"])
    reach = reach - reach / 16777216.0
    if side == "high":
        return float(math.ceil(boundary + reach))
    return float(math.floor(boundary - reach))


def _walk_calls(described: kpi_shapes.Described, seed: int = 0) -> "list[tuple]":
    """Every call of the width walk's first step, caught as the generator makes it, in order."""
    caught: "list[tuple]" = []

    def catch(*arguments):  # type: ignore[no-untyped-def]
        caught.append(arguments)
        return _REAL_WALK(*arguments)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_walked_past_the_width", catch)
        kpi_shapes.twin_text(described, seed)
    assert caught, "premise: the walk is asked"
    return caught


def _with_totals(sides: "list[tuple]", first: float, second: float) -> "list[tuple]":
    return [(high, boundary, first, second, moved, held) for high, boundary, _first, _second, moved, held in sides]


def _left_past(facts: contract.NumericFacts, values: "list[float]", widest: int) -> "list[int]":
    return [
        place
        for place in range(len(values))
        if generation._carries_plainly(values[place], facts.integer_valued)
        and generation._figure_count(values[place], facts.integer_valued) > widest
    ]


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


def _plus_mixed() -> "list[str]":
    """100 codes `0001` to `0999`, 40 plus-signed numbers `+100` to `+999` and one `99999` (the first skeptic's shape)."""
    draw = random.Random("g2/plus/4")
    cells = [f"{draw.randint(1, 999):04}" for _row in range(100)]
    cells += ["+" + str(draw.randint(100, 999)) for _row in range(40)]
    return cells + ["99999"]


def _grid(rows: int) -> "list[str]":
    """Readings 1000 to 1900 in steps of a hundred, `rows` of them, beside one `99900`."""
    return [str(1000 + 100 * (step % 10)) for step in range(rows)] + ["99900"]


def _beside_one_far(rows: int) -> "list[str]":
    """`00001` up, padded to five, beside one `12345` (follow-up A's shape)."""
    return [f"{value:05}" for value in range(1, rows)] + ["12345"]


def _narrow_beside_five() -> "list[str]":
    """Nine four-figure cells, 1000 to 9000, beside 51 of five figures: the census names five."""
    return (
        [str(1000 + 1000 * step) for step in range(9)]
        + [str(30000 + 500 * step) for step in range(3)]
        + [str(40000 + 1000 * step) for step in range(48)]
    )


def _both_sides() -> "list[str]":
    """300 four-figure numbers beside `-99999` and `-88888` and beside `99999` and `77777`."""
    draw = random.Random("g2/both/300/2")
    return [str(draw.randint(1000, 9999)) for _row in range(300)] + ["-99999", "-88888", "99999", "77777"]


def _codes_beside_decimals() -> "list[str]":
    """Codes `01` to `07` written twice, beside forty decimals from -400.125 to 575.125: the census names the codes alone."""
    return [f"0{digit}" for digit in range(1, 8)] * 2 + [f"{value}.125" for value in range(-400, 600, 25)]


def _staircase_far(rows: int, far: int, start: int) -> "list[str]":
    """Four-figure numbers beside a run of far cells one apart, fewer than the line."""
    draw = random.Random(f"g2/stair/{rows}/{far}/{start}")
    return [str(draw.randint(1000, 9999)) for _row in range(rows)] + [str(start + step) for step in range(far)]


def _bulk(rows: int) -> "list[str]":
    """1000 to 1999 over and over, beside five of five figures: the first skeptic's million-row shape, smaller."""
    far = ["99999", "98765", "97531", "96420", "95555"]
    return [str(1000 + (step * 7919) % 1000) for step in range(rows - len(far))] + far


def _ones_beside_eleven() -> "list[str]":
    """Readings 1 to 9 in turn, 400 of them, beside one `11`: every value under the width is held."""
    return [str(1 + step % 9) for step in range(400)] + ["11"]


def _ones_bell() -> "list[str]":
    """A thousand one-figure readings shaped like a bell around 5, beside `15` and `18`."""
    draw = random.Random("g2/bell/1000")
    return [str(max(1, min(9, int(round(draw.gauss(5, 4 / 3)))))) for _row in range(1000)] + ["15", "18"]


def _ones_low_heavy() -> "list[str]":
    """150 one-figure readings crowded towards 1, beside `12`, `39` and `72`."""
    draw = random.Random("g2/low/150")
    return [str(max(1, min(9, int(1 + 8 * draw.random() ** 3)))) for _row in range(150)] + ["12", "39", "72"]


def _two_figures_beside_185() -> "list[str]":
    """150 two-figure readings 10 to 99 drawn evenly, beside one `185`: a reading with a figure typed twice."""
    draw = random.Random("g2/uniform/150/185")
    return [str(draw.randint(10, 99)) for _row in range(150)] + ["185"]


_PAST_THE_REACH = (
    ("cfh99999_150", reader.shape("cfh99999", 150, 1), 11),
    ("pad99999_150", reader.shape("pad99999", 150, 1), 11),
    ("par20d_150_s2", reader.shape("par20d", 150, 2), 36),
)

# THE MEAN AND THE SPREAD 110cb46 WROTE, each as its distance from the real
# column's in real standard deviations -- the mean's distance and the
# spread's ratio's distance from one -- the same at seeds 0, 4 and 9: the
# first skeptic's grid shapes, follow-up A's codes beside one far value,
# and the hundred-thousand-row shape at seed 0.
_ON_110CB46 = {
    ("grid", 4000, 11): (0.0412, 0.4338),
    ("grid", 1000, 11): (0.0205, 0.6159),
    ("grid", 1000, 20): (0.0205, 0.6159),
    ("grid", 400, 36): (0.0954, 0.5048),
    ("codes", 150, 11): (0.0504, 0.1396),
    ("codes", 150, 36): (0.0544, 0.1405),
    ("codes", 400, 11): (0.0296, 0.1349),
    ("codes", 400, 36): (0.0323, 0.1369),
    ("bulk", 100000, 11): (0.0023, 0.5752),
    ("ones", 401, 50): (0.0067, 0.0064),
    ("bell", 1002, 36): (0.0083, 0.0105),
    ("low", 153, 50): (0.1369, 0.4951),
}
_SLACK = 1e-4


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


def test_the_end_goes_no_further_out_than_the_end_the_fitted_reading_left() -> None:
    """Where the reach lies past the end the fitted reading derived, the end is that end, on either side.

    Asked of the rule itself: a hold that took a fitted end of 10200 down
    to 9998, at or past the mean distance of 100 from a boundary of 1000
    and inside a reach of 9500, would move it to 10500 -- past anything the
    fitted reading allows -- and the rule stops at 10200. Its mutant
    returns the reach's own whole number.
    """
    pair = (100.0, 9500.0)
    assert contract._past_the_width(9998.0, 10200.0, False, 1000.0, pair, ()) == 10200.0
    assert contract._past_the_width(9998.0, 10900.0, False, 1000.0, pair, ()) == 10500.0
    assert contract._past_the_width(-9998.0, -10200.0, True, -1000.0, pair, ()) == -10200.0
    assert contract._past_the_width(-9998.0, -10900.0, True, -1000.0, pair, ()) == -10500.0


def test_the_ladder_read_without_the_reach_rule_holds_the_width_s_end(tmp_path: pathlib.Path) -> None:
    """`reach_rule` False is the ladder 110cb46 read; the walk reads from it which side the rule moved.

    `1000` to `1148` beside `99999`: the rule moved the high end from 9998
    to the reach, so the high side is walked always. 60 codes beside 90
    plain numbers and `99999`, at a floor of eleven: the end stood past the
    width already -- the mean-distance guard kept the fitted end -- so the
    rule moved nothing and the side's walk is weighed against 110cb46's.
    """
    moved = _facts(_described(tmp_path, "cfh99999_150", reader.shape("cfh99999", 150, 1), 11))
    read = contract.tail_ladder(moved)
    held = contract.tail_ladder(moved, reach_rule=False)
    assert read is not None and read.high is not None and held is not None and held.high is not None
    assert held.high.end == 9998.0 < read.high.end
    sides = generation._proven_sides(moved, 4)
    assert [(side[0], side[4]) for side in sides] == [(True, True)]
    stood = _facts(_described(tmp_path, "mixed_60_90", _mixed(60, 90, ["99999"], 2), 11))
    sides = generation._proven_sides(stood, 4)
    assert [(side[0], side[4]) for side in sides] == [(True, False)]


def test_a_side_is_walked_only_where_its_reach_passes_the_width(tmp_path: pathlib.Path) -> None:
    """`_proven_sides`: a tail's pair proves a cell past every named width only where its reach passes `10**widest - 1`.

    Nine four-figure cells beside 51 of five figures: the high pair's reach
    stops short of `99999` and the low one cannot pass `-99999`, so no side
    is walked. 300 four-figure numbers beside far cells on both sides of
    nought: each side's reach passes the width on its own side, and both
    are walked, low first.
    """
    narrow = _facts(_described(tmp_path, "narrow_beside_five", _narrow_beside_five(), 11))
    assert narrow.tails is not None and narrow.tails.high is not None and narrow.tails.high.mean_distance is not None
    assert generation._proven_sides(narrow, 5) == []
    both = _facts(_described(tmp_path, "both", _both_sides(), 11))
    assert [side[0] for side in generation._proven_sides(both, 4)] == [False, True]
    # ...and none where the census does not count every number: two-figure
    # padded codes beside decimals reaching 575, whose tails are decimals
    # far past `9`. The census counts the codes alone, and says nothing of
    # the cells the tails hold.
    beside = _facts(_described(tmp_path, "codes_beside_decimals", _codes_beside_decimals(), 11))
    assert sum(beside.field_widths.values()) < beside.n_used_in_statistics, "premise: decimals the census does not count"
    assert beside.tails is not None and beside.tails.high is not None and beside.tails.high.mean_distance is not None
    ladder = contract.tail_ladder(beside)
    assert ladder is not None and ladder.high is not None and ladder.high.boundary > 9.0, "premise: a tail past 9"
    assert generation._proven_sides(beside, 1) == []


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


# -- 2. which of the tail's strata stay past the width ------------------------


def test_the_walk_leaves_the_tail_s_wide_cells_past_the_width(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ten five-figure cells under a census of four: the walk leaves the tail's outermost wide rows past it.

    At most the line less one, and nothing missed. Its mutant walks no
    side, and 110cb46's walk moves one more of them under the width.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    assert _census(described) == ({"4": 100}, {}), "premise: one width of four"
    room = parsing.census_floor(11) - 1
    left = {seed: _past(_twin_numbers(described, seed), 9999.0) for seed in SEEDS}
    for seed in SEEDS:
        assert 1 < left[seed] <= room, f"seed {seed}: {left[seed]}"
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(generation, "_walked_past_the_width", lambda _f, _l, values, _d, _fl, _s: (list(values), 0))
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 9999.0) < left[seed], f"seed {seed}"


def test_the_cells_left_stop_at_the_pair_s_own_totals(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`1000` to `1398` beside one `99999`: the pair carries one far row, so one cell stands past the width.

    The ladder puts a second row past it, by the end; the end's own
    distance already spends the pair's total of squares, so the walk moves
    that row under the width. Its mutant reads no totals, and the twin
    writes two cells past `9999` where the table holds one, its spread
    0.41 off the real one where the walk leaves it 0.001 off.
    """
    cells = reader.shape("cfh99999", 400, 1)
    described = _described(tmp_path, "cfh99999_400", cells, 11)
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        assert _past(written, 9999.0) == 1, f"seed {seed}"
        assert _errors(cells, written)[1] < 0.01, f"seed {seed}"
    monkeypatch.setattr(
        generation,
        "_walked_past_the_width",
        lambda facts, layout, values, demands, floor, sides: _REAL_WALK(
            facts, layout, values, demands, floor, _with_totals(sides, math.inf, math.inf)
        ),
    )
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        assert _past(written, 9999.0) == 2 and _errors(cells, written)[1] > 0.1, f"seed {seed}"


def _squares_under_the_width(facts, layout, values, demands, side) -> float:  # type: ignore[no-untyped-def]
    """What the side's tail strata under the width hold of `m rms**2`, each at its own distance from the boundary."""
    past = _left_past(facts, values, generation._widest_demanded(demands))
    held = 0.0
    for place in generation._side_strata(facts, layout, side[0]):
        if place in past:
            continue
        far = abs(values[place] - side[1])
        held += layout.sizes[place] * far * far
    return held


def test_the_squares_the_rows_under_the_width_hold_come_off_the_pair_s_total_first(tmp_path: pathlib.Path) -> None:
    """150 two-figure readings beside one `185`, at a floor of fifty: no stratum of the tail stays past `99`.

    The high tail's 51 rows are fifty readings beside its boundary and the
    one far cell, which holds most of the pair's squares. The reach puts
    the end at `103`, and the staircase stacks 24 of the tail's rows on it:
    inside the pair's two totals alone they fit, 24 rows at the reach
    holding no more than `m d1` and `m rms**2`. But the tail's strata under
    the width already hold their share of `m rms**2` wherever the far
    cells stand, and what they leave holds none of the 24, so the end's
    stratum goes under the width with the rest: the twin writes no cell
    past `99`, where the source holds one, its own census is the source's
    and it misses nothing. Its mutant reads the squares as the whole pair's
    -- the total raised by what the strata under the width hold -- and the
    walk leaves all 24 past the width, the source's one far value written
    24 times at the reach.
    """
    described = _described(tmp_path, "two_figures_185", _two_figures_beside_185(), 50)
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 99.0) == 0, f"seed {seed}"
        assert _own_census(tmp_path, described, seed, 50) == _census(described), f"seed {seed}"
        assert _missed(described, seed) == [], f"seed {seed}"
    ladder = contract.tail_ladder(_facts(described))
    assert ladder is not None and ladder.high is not None and ladder.high.end == 103.0, "premise: the end at the reach"
    facts, layout, values, demands, floor, sides = [call for call in _walk_calls(described) if call[5]][0]
    assert [(side[0], side[4]) for side in sides] == [(True, True)], "premise: the side rule 1 moved"
    widest = generation._widest_demanded(demands)
    stacked = _left_past(facts, values, widest)
    assert sum(layout.sizes[place] for place in stacked) == 24, "premise: 24 rows past the width by the staircase"
    moved, freed = generation._walked_past_the_width(facts, layout, values, demands, floor, sides)
    assert freed == 0 and _left_past(facts, moved, widest) == []
    raised = _with_totals(sides, sides[0][2], sides[0][3] + _squares_under_the_width(facts, layout, values, demands, sides[0]))
    moved, freed = generation._walked_past_the_width(facts, layout, values, demands, floor, raised)
    assert freed == 24 and _left_past(facts, moved, widest) == stacked


def test_the_line_and_each_total_bind_on_their_own(tmp_path: pathlib.Path) -> None:
    """The walk's own three bounds, each asked alone of the ten-wide column's first step.

    Five strata stand past `9999` after the staircase, one cell each. A
    floor of four leaves room for three; a first total of exactly the
    outermost stratum's distance, or a total of squares of exactly its
    square beside the squares the tail's strata under the width hold,
    leaves that one alone; and every stratum the walk does not leave is
    moved under the width, so no other cell stays past it.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    facts, layout, values, demands, floor, sides = _walk_calls(described)[0]
    assert floor == 11 and [side[0] for side in sides] == [True], "premise: the high side alone"
    widest = generation._widest_demanded(demands)
    before = _left_past(facts, values, widest)
    assert len(before) == 5 and all(layout.sizes[place] == 1 for place in before), "premise: five one-cell strata"
    moved, freed = generation._walked_past_the_width(facts, layout, values, demands, floor, sides)
    assert freed == 5 and _left_past(facts, moved, widest) == before
    moved, freed = generation._walked_past_the_width(facts, layout, values, demands, 4, sides)
    assert freed == 3 and _left_past(facts, moved, widest) == before[2:]
    boundary = sides[0][1]
    outermost = values[before[-1]] - boundary
    # The squares the strata under the width hold come off the total first,
    # summed in another order here, so the total is raised by a part in
    # 10**12 to stand clear of that rounding.
    under = _squares_under_the_width(facts, layout, values, demands, sides[0])
    for first, second in ((outermost, math.inf), (math.inf, (outermost * outermost + under) * (1.0 + 1e-12))):
        moved, freed = generation._walked_past_the_width(
            facts, layout, values, demands, floor, _with_totals(sides, first, second)
        )
        assert freed == 1 and _left_past(facts, moved, widest) == before[-1:], (first, second)


def test_the_walk_stops_at_the_first_stratum_that_does_not_fit(tmp_path: pathlib.Path) -> None:
    """Whole strata stay outermost first, and the first that does not fit sends every one inside it under.

    A total of squares that holds -- beside what the tail's strata under
    the width hold -- the outermost stratum and the third but not the
    second leaves the outermost alone: the cells left past the width are
    always the outermost, never a gap with a stratum beyond it.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    facts, layout, values, demands, floor, sides = _walk_calls(described)[0]
    widest = generation._widest_demanded(demands)
    before = _left_past(facts, values, widest)
    boundary = sides[0][1]
    outermost, second, third = (values[place] - boundary for place in before[-1:-4:-1])
    assert outermost > second > third, "premise: three strata at three distances"
    squares = outermost * outermost + third * third + (second * second - third * third) / 2.0
    squares += _squares_under_the_width(facts, layout, values, demands, sides[0])
    moved, freed = generation._walked_past_the_width(
        facts, layout, values, demands, floor, _with_totals(sides, math.inf, squares)
    )
    assert freed == 1 and _left_past(facts, moved, widest) == before[-1:]


def test_on_a_tie_the_outermost_by_rank_stays(tmp_path: pathlib.Path) -> None:
    """100 codes beside 40 plus-signed numbers and one `99999`: the far value stays on the stratum holding the end.

    The staircase's last row stands on the end's own value, a tie in
    distance, and the pair's total of squares carries one of the two. The
    walk keeps the outermost by rank -- the stratum holding the end -- and
    moves the row under the width, so the strata keep their order. Taken
    the other way, the first form wrote `99999` twice at every seed and
    the spread 1.41 times the real one; with the end's stratum movable, it
    would put the far value on the row and the end under the width, out
    of order. The far value is written once and the mean and spread are
    110cb46's.
    """
    cells = _plus_mixed()
    for floor in (11, 36):
        described = _described(tmp_path, f"plus_mixed_{floor}", cells, floor)
        walked = [call for call in _walk_calls(described) if call[5]]
        assert walked, "premise: the side is walked"
        facts, layout, values, demands, walk_floor, sides = walked[0]
        last = len(values) - 1
        if floor == 11:
            widest = generation._widest_demanded(demands)
            ties = [place for place in _left_past(facts, values, widest) if values[place] == values[last]]
            assert len(ties) == 2, "premise: a staircase row on the end's value"
        moved, _freed = generation._walked_past_the_width(facts, layout, values, demands, walk_floor, sides)
        assert moved[last] == values[last], f"floor {floor}"
        tail = [moved[place] for place in generation._side_strata(facts, layout, True)]
        assert tail == sorted(tail), f"floor {floor}"
        # ...and the count of different values stands: the row's own value
        # is the end's too, so moving it gives no value up, and it may land
        # on a value another stratum holds -- its inner neighbour's.
        assert len(set(moved)) == len(set(values)), f"floor {floor}"
        for seed in SEEDS:
            written = _twin_numbers(described, seed)
            assert _past(written, 9999.0) == 1, f"floor {floor} seed {seed}"
            mean, spread = _errors(cells, written)
            assert mean < 0.0031 and spread < 0.001, f"floor {floor} seed {seed}: {mean} {spread}"


def test_each_side_walks_its_own_tail(tmp_path: pathlib.Path) -> None:
    """Far cells on both sides of nought: each side walks only the strata of its own tail's rows.

    300 four-figure numbers beside `-99999` and `-88888` and beside `99999`
    and `77777`, at floors 11 and 36: each end keeps its sign and the twins
    miss nothing. A walk that took the other tail's strata as its own
    would carry a far negative stratum under the high side's width.
    """
    cells = _both_sides()
    for floor in (11, 36):
        described = _described(tmp_path, f"both_{floor}", cells, floor)
        for seed in SEEDS:
            written = _twin_numbers(described, seed)
            assert min(written) < -9999.0 < 9999.0 < max(written), f"floor {floor} seed {seed}"
            assert len([value for value in written if value < 0.0]) == 2, f"floor {floor} seed {seed}"
            assert _missed(described, seed) == [], f"floor {floor} seed {seed}"


# -- 3. where the strata moved under the width go ----------------------------


def _keep_the_pinned_past(facts, layout, values, places, pulled, side, width):  # type: ignore[no-untyped-def]
    """The first form's fault: the stratum holding the end is never moved."""
    kept = [place for place in pulled if place not in (0, len(values) - 1)]
    if not kept:
        return list(values)
    return _REAL_PULLED(facts, layout, values, places, kept, side, width)


_GRIDS = ((4000, 11), (1000, 11), (1000, 20), (400, 36))


@pytest.mark.parametrize("rows,floor", _GRIDS, ids=[f"grid{rows}_f{floor}" for rows, floor in _GRIDS])
def test_an_end_whose_stratum_does_not_fit_goes_under_the_width(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, rows: int, floor: int
) -> None:
    """The first skeptic's grid shapes: one stratum holds the whole tail and the end, and it goes under the width.

    Readings 1000 to 1900 beside one `99900`: the end's stratum holds 40,
    19 or 35 rows, more than the line less one and far past the pair's
    totals, so it is moved under the width with the rest -- to `9998`,
    where the pair's squares put it and where 110cb46 wrote it. The twin's
    own census is the source's, and its mean and spread are 110cb46's. Its
    mutant never moves the end's stratum: every one of its rows lands on
    `99900`, the source's single maximum, the mean and spread many times
    further off and, at a floor of eleven, the twin's own census naming a
    width of five.
    """
    cells = _grid(rows)
    described = _described(tmp_path, f"grid{rows}", cells, floor)
    mean_most, spread_most = _ON_110CB46[("grid", rows, floor)]
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        assert _past(written, 9999.0) == 0 and max(written) == 9998.0, f"seed {seed}"
        assert _own_census(tmp_path, described, seed, floor) == _census(described), f"seed {seed}"
        mean, spread = _errors(cells, written)
        assert mean <= mean_most + _SLACK and spread <= spread_most + _SLACK, f"seed {seed}: {mean} {spread}"
    monkeypatch.setattr(generation, "_pulled_under_the_width", _keep_the_pinned_past)
    written = _twin_numbers(described, 0)
    assert _past(written, 9999.0) > parsing.census_floor(floor) // 2 and max(written) == 99900.0
    mean, spread = _errors(cells, written)
    assert mean > 5 * mean_most and spread > 5 * spread_most
    if floor == 11:
        assert _own_census(tmp_path, described, 0, floor) != _census(described)


@pytest.mark.parametrize("rows,floor", ((150, 11), (150, 36), (400, 11), (400, 36)))
def test_a_row_moved_under_the_width_stands_beside_its_inner_neighbour(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, rows: int, floor: int
) -> None:
    """Follow-up A's codes beside one far value: the staircase row the end leaves past the width lands beside the codes.

    The end stays past the width at the reach and carries the distance the
    pair proves, so the row moved under it goes to the boundary's side --
    the first free value past its inner neighbour, any figure count up to
    four, the padded ceiling being what the census asks -- and the twin's
    spread is no further from the real one than 110cb46's. Its mutant aims
    the row at the width's end, and the walk puts it on `09998`: the first
    form's fault, which left the spread 0.23 to 0.28 off the real one where
    110cb46 stood 0.14 off.
    """
    cells = _beside_one_far(rows)
    described = _described(tmp_path, f"codes{rows}", cells, floor)
    mean_most, spread_most = _ON_110CB46[("codes", rows, floor)]
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        mean, spread = _errors(cells, written)
        assert mean <= mean_most + _SLACK and spread <= spread_most + _SLACK, f"seed {seed}: {mean} {spread}"
        assert not [value for value in written if 9000.0 <= value < 10000.0], f"seed {seed}"
    facts, layout, values, demands, walk_floor, sides = _walk_calls(described)[0]
    assert sides and sides[0][4], "premise: the side the reach rule moved"
    moved, _freed = generation._walked_past_the_width(facts, layout, values, demands, walk_floor, sides)
    pulled = [place for place in range(len(values)) if moved[place] != values[place]]
    assert pulled, "premise: a staircase row is moved under the width"
    for place in pulled:
        assert 0.0 < moved[place] - moved[place - 1] <= 2.0, (place, moved[place - 1], moved[place])
    monkeypatch.setattr(
        generation,
        "_targets_under_the_width",
        lambda _layout, _values, _places, pulled, _side, end: [end for _place in pulled],
    )
    aimed, _freed = generation._walked_past_the_width(facts, layout, values, demands, walk_floor, sides)
    assert [aimed[place] for place in pulled] == [9998.0 for _place in pulled]


def test_the_targets_spread_the_squares_left_outermost_first_and_never_past_the_width() -> None:
    """`_targets_under_the_width` asked directly, on a tail of three strata above a boundary of 900.

    Where the end's stratum moves too, what the total of squares has left
    after the stratum staying goes to the moved strata outermost first,
    each at `sqrt(left / size)` from the boundary and never past the
    width's end -- so a second stratum still finds squares left after the
    first is held at the end. Where the end's stratum stays, it carries
    the distance the pair proves and every moved stratum stands at the
    boundary.
    """
    layout = generation._NumericLayout(
        sizes=(1, 1, 3, 2, 1), starts=(0, 1, 2, 5, 7), bands=("positive",) * 5, raw_budgets=(), folded_budgets=()
    )
    values = [100.0, 900.0, 950.0, 20000.0, 50000.0]
    side = (True, 900.0, 1.0e10)
    assert generation._targets_under_the_width(layout, values, [2, 3, 4], [4, 3], side, 9999.0) == [9999.0, 9999.0]
    assert generation._targets_under_the_width(layout, values, [2, 3, 4], [3], side, 9999.0) == [900.0]


def test_a_moved_stratum_takes_exactly_the_widest_count_only_where_a_demand_asks_exactly_that_many() -> None:
    """`_width_of`: the widest figure count a demand lets a value hold, exact where an unpadded demand asks for it."""
    assert generation._width_of([(3, 0, 200), (4, 1, 102)]) == (4, True)
    assert generation._width_of([(4, 0, 400)]) == (4, False)
    assert generation._width_of([(3, 0, 101), (3, 1, 40)]) == (3, True)
    assert generation._width_of([(2, 1, 10), (4, 0, 90)]) == (4, False)
    assert generation._width_of([]) == (0, False)


def test_a_free_value_under_the_width_is_the_walk_s_own_rule(tmp_path: pathlib.Path) -> None:
    """`_free_under_the_width` and `_nearest_under_the_width` asked directly, on a column of whole numbers holding no stand-in.

    Free: held by no other stratum, on the stratum's side of nought, never
    a stand-in the block does not hold, and of exactly the widest figure
    count where a demand asks exactly that many, any count up to it where
    only a padded ceiling asks; never past the width.
    """
    facts = _facts(_described(tmp_path, "ten_wide", _ten_wide(), 11))
    assert facts.integer_valued and facts.kept_stand_ins == ()
    free = generation._free_under_the_width
    assert free(9998.0, {}, "positive", (4, True), facts)
    assert not free(999.0, {}, "positive", (4, True), facts)
    assert free(999.0, {}, "positive", (4, False), facts)
    assert not free(10000.0, {}, "positive", (4, False), facts)
    assert not free(9999.0, {}, "positive", (4, True), facts)
    assert not free(9998.0, {9998.0: 1}, "positive", (4, True), facts)
    assert not free(-9998.0, {}, "positive", (4, True), facts)
    nearest = generation._nearest_under_the_width
    assert nearest((900.0, 1100.0), {}, "positive", (4, True), 950.0, True, ()) == 1000.0
    assert nearest((900.0, 1100.0), {}, "positive", (4, False), 950.0, True, ()) == 950.0


def test_where_the_end_moves_too_the_moved_strata_carry_the_pair_s_squares(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """4,000 readings beside one `99900`: with the end moved, the tail's one stratum stands where the pair's squares put it.

    Nothing past the width carries the tail's spread, so the moved strata
    carry what the total of squares has left, outermost first, each at
    `sqrt(left / size)` from the boundary and never past the width: here
    the width's end, `9998` (`9999` is a stand-in the block does not
    hold). Its mutant puts it beside the boundary instead, on `1901`, and
    the spread falls from 0.57 to 0.18 of the real one.
    """
    cells = _grid(4000)
    described = _described(tmp_path, "grid4000", cells, 11)
    written = _twin_numbers(described, 0)
    assert written.count(9998.0) == 40 and 9999.0 not in written
    monkeypatch.setattr(
        generation,
        "_targets_under_the_width",
        lambda _layout, _values, _places, pulled, side, _end: [side[1] for _place in pulled],
    )
    written = _twin_numbers(described, 0)
    assert written.count(1901.0) == 40 and _errors(cells, written)[1] > 0.8


def test_a_far_cell_no_pad_can_hold_is_written_plain(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Follow-up A's codes beside one far value: every cell of the twin is five characters, as every real one is.

    The end G6.6.8 leaves past the width, `12280`, needs every figure of
    the one field the census names, so no pad can hold it, and the map
    carries no other point-free form to give the padded style up to; the
    tail's pair proves a cell past the width on its side, so it is written
    plain (method G6.3, plan P4-D377). Its mutant keeps the pad and writes
    `012280`, six characters in a column of five.
    """
    for rows in (150, 400):
        for floor in (11, 36):
            described = _described(tmp_path, f"codes{rows}_{floor}", _beside_one_far(rows), floor)
            for seed in SEEDS:
                cells = _cells(described, seed)
                assert {len(cell) for cell in cells} == {5}, f"{rows} {floor} seed {seed}"
                assert max(_numbers(cells)) > 9999.0, f"premise: a cell past the width, {rows} {floor} seed {seed}"
    monkeypatch.setattr(
        generation, "_point_free_form_worn", lambda styles, value, whole: _REAL_WORN(styles, value, whole) or "leading_zero"
    )
    assert max(len(cell) for cell in _cells(described, 0)) == 6


def test_only_a_far_cell_a_pair_proves_gives_its_pad_up_to_a_form_the_map_does_not_name() -> None:
    """`_padded_style_swaps` and `_proven_side_holds` asked directly: every cell padded, one value no pad can hold.

    `12` in a column whose one pad width is two keeps the padded style
    where no tail's pair proves a cell past the width (plan P4-D105: the
    stage-2b style battery gives its named padded count up at eight runs
    of 1,920, and writing plain there missed it at 34), and is written
    plain where the high side's pair does (plan P4-D377). A value inside
    the width, or one on the side no pair proves, is no far cell.
    """
    styles = ["leading_zero", "leading_zero", "leading_zero"]
    holds = [12.0, 3.0, 4.0]
    swaps = generation._padded_style_swaps
    assert swaps(styles, holds, {"2": 3}, [], True) == styles
    assert swaps(styles, holds, {"2": 3}, [], True, (1, (False,))) == styles
    assert swaps(styles, holds, {"2": 3}, [], True, (1, (True,))) == ["plain", "leading_zero", "leading_zero"]
    holds_far = generation._proven_side_holds
    assert holds_far(12.0, (1, (True,)), True)
    assert not holds_far(9.0, (1, (True,)), True)
    assert not holds_far(-12.0, (1, (True,)), True)
    assert holds_far(-12.0, (1, (False, True)), True)
    assert not holds_far(12.0, (0, (True,)), True)


def test_a_run_with_too_little_room_under_the_width_widens_inward(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """K-S3-22's Pareto(2.5) readings: a tail with more strata past `999` than free values beside it under the width.

    The run takes the side's strata under the width beside it, one at a
    time, until the room between the stratum inside them and the width
    holds a free value for each, and spreads them down from `999`: no
    stratum the walk moved is left past the width -- only the cells it
    leaves there are -- and the order of the values and the count of
    different ones stand.
    """
    short: "list[int]" = []
    real_tops = generation._tops_under_the_width

    def watched(taken, span, band, width, facts):  # type: ignore[no-untyped-def]
        found = real_tops(taken, span, band, width, facts)
        if len(found) < span[2]:
            short.append(span[2])
        return found

    monkeypatch.setattr(generation, "_tops_under_the_width", watched)
    for seed in range(10):
        for floor in (36, 50):
            described = _described(tmp_path, f"pareto_{seed}_{floor}", reader.pareto(400, seed), floor)
            for facts, layout, values, demands, walk_floor, sides in _walk_calls(described):
                if not sides:
                    continue
                widest = generation._widest_demanded(demands)
                tails: "list[int]" = []
                for side in sides:
                    tails += generation._side_strata(facts, layout, side[0])
                moved, freed = generation._walked_past_the_width(facts, layout, values, demands, walk_floor, sides)
                left = [place for place in _left_past(facts, moved, widest) if place in tails]
                assert sum(layout.sizes[place] for place in left) == freed, f"seed {seed} floor {floor}"
                walked = [moved[place] for place in sorted(tails)]
                assert walked == sorted(walked) and len(set(moved)) == len(set(values)), f"seed {seed} floor {floor}"
    assert short, "premise: some run found too few free values beside it on its own"


_HELD_SHAPES = (
    ("ones", _ones_beside_eleven, 50),
    ("bell", _ones_bell, 36),
    ("low", _ones_low_heavy, 50),
)


def _without_the_held_end(facts, layout, values, places, pulled, side, width):  # type: ignore[no-untyped-def]
    """The fallback withdrawn: the pull is handed no end the width held."""
    return _REAL_PULLED(facts, layout, values, places, pulled, (side[0], side[1], side[2], None), width)


@pytest.mark.parametrize("label,shape,floor", _HELD_SHAPES, ids=[f"{one[0]}_f{one[2]}" for one in _HELD_SHAPES])
def test_a_stratum_with_no_room_under_the_width_takes_the_end_the_width_held(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, label: str, shape, floor: int  # type: ignore[no-untyped-def]
) -> None:
    """One-figure readings beside far cells, every value under the width held: the end goes back to 110cb46's `9`.

    Rule 1 moved the high end past `9`, and the stratum holding it -- most
    of the tail's rows -- does not fit the line less one and the pair's
    totals, so the walk moves it under the width; but every whole value
    from 1 to 9 is held by another stratum, and the side's whole tail
    taken in finds too few free values. The strata that find none take
    the end the width held on 110cb46, `9`, beside the stratum holding it.
    No cell stands past the width, the twin's own census is the source's,
    its mean and spread are no further off than 110cb46's and it misses
    nothing. Its mutant hands the pull no end: the walk gives the side up,
    and the end's stratum stays past the width with most of the tail --
    the first skeptic's first fault, on a column of one figure. 71a7b31
    wrote 49 of the 401 cells on `10` this way, its mean 0.054 of the
    real spread off where 110cb46 stood 0.007 off.
    """
    cells = shape()
    described = _described(tmp_path, f"{label}{floor}", cells, floor)
    sides = generation._proven_sides(_facts(described), 1)
    assert [(side[0], side[4], side[5]) for side in sides] == [(True, True, 9.0)], "premise: rule 1 moved the end off 9"
    mean_most, spread_most = _ON_110CB46[(label, len(cells), floor)]
    for seed in SEEDS:
        written = _twin_numbers(described, seed)
        assert _past(written, 9.0) == 0 and max(written) == 9.0, f"seed {seed}"
        assert _own_census(tmp_path, described, seed, floor) == _census(described), f"seed {seed}"
        mean, spread = _errors(cells, written)
        assert mean <= mean_most + _SLACK and spread <= spread_most + _SLACK, f"seed {seed}: {mean} {spread}"
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(generation, "_pulled_under_the_width", _without_the_held_end)
    assert _past(_twin_numbers(described, 0), 9.0) > parsing.census_floor(floor) // 2


def _heap_far3() -> "list[str]":
    """400 readings 9000 to 9500, `9999` fifteen times and `10500`, `50000` and `99999` (the first skeptic's attack shape)."""
    draw = random.Random("g2skep/heap/400/15/3")
    return [str(draw.randint(9000, 9500)) for _row in range(400)] + ["9999"] * 15 + ["10500", "50000", "99999"]


def test_a_side_the_rule_left_gives_its_walk_up_where_a_stratum_finds_no_room(tmp_path: pathlib.Path) -> None:
    """Readings 9000 to 9500 beside a heap of `9999` and three far cells, at a floor of eleven: no room under the width.

    Rule 1 moved nothing on this side -- the end stood past the width on
    110cb46 -- so its walk is weighed against 110cb46's. The end's stratum
    fits and would stay; the six inside it do not, and the tail's boundary
    is the heap of `9999` itself, so no value under the width lies past
    the stratum inside the tail. With no end the width held to fall back
    to, the side's walk is given up whole: the first step hands the values
    back as they stood and counts no cell left past the width, so the
    walk weighed is 110cb46's. Its mutant keeps the end's cell counted,
    beside six strata the rule does not allow past the width.
    """
    described = _described(tmp_path, "heap_far3", _heap_far3(), 11)
    calls = [call for call in _walk_calls(described) if call[5]]
    assert calls, "premise: the side is weighed"
    facts, layout, values, demands, floor, sides = calls[0]
    assert [(side[0], side[4]) for side in sides] == [(True, False)], "premise: a side the rule did not move"
    widest = generation._widest_demanded(demands)
    assert len(_left_past(facts, values, widest)) > 1, "premise: strata past the width"
    moved, freed = generation._walked_past_the_width(facts, layout, values, demands, floor, sides)
    assert moved == values and freed == 0


def _run_layout(values: "list[float]") -> "generation._NumericLayout":
    """One cell a stratum, every stratum positive: the layout the direct tests of the pull hand it."""
    count = len(values)
    return generation._NumericLayout(
        sizes=(1,) * count,
        starts=tuple(range(count)),
        bands=("positive",) * count,
        raw_budgets=(),
        folded_budgets=(),
    )


def test_the_last_resort_places_what_it_can_on_the_outermost_free_values_and_the_rest_on_the_held_end(
    tmp_path: pathlib.Path,
) -> None:
    """`_pulled_under_the_width` asked directly, on one-figure strata where the side's tail cannot make room.

    Strata 1, 7 and 8 under the width and 15, 15 and 20 past it, the tail
    the last four. The run of the three past it finds one free value, `9`,
    takes the stratum at 8 in, finds two, and stops at the body's 7; so
    the pulled strata alone are moved, the innermost onto `9` -- aimed at
    the limit, though its own value is shared and every value is open to
    it -- and the two outermost take the held end. The body is untouched,
    the order stands, nothing stays past the width. Handed no held end,
    the two outermost stay where they stood. A held end inside the
    stratum beside them is lifted to it, and one past the width gives way
    to the width's own end. A run reaching the column's own edge has no
    stratum inside it and takes the held end whole.
    """
    facts = _facts(_described(tmp_path, "ones50", _ones_beside_eleven(), 50))
    values = [1.0, 7.0, 8.0, 15.0, 15.0, 20.0]
    layout = _run_layout(values)
    places = [2, 3, 4, 5]
    pulled = [5, 4, 3]
    width = (1, False)
    moved = generation._pulled_under_the_width(facts, layout, values, places, pulled, (True, 5.0, 0.0, 9.0), width)
    assert moved == [1.0, 7.0, 8.0, 9.0, 9.0, 9.0]
    stood = generation._pulled_under_the_width(facts, layout, values, places, pulled, (True, 5.0, 0.0, None), width)
    assert stood == [1.0, 7.0, 8.0, 9.0, 15.0, 20.0]
    lifted = generation._pulled_under_the_width(facts, layout, values, places, pulled, (True, 5.0, 0.0, 8.0), width)
    assert lifted == [1.0, 7.0, 8.0, 9.0, 9.0, 9.0]
    beyond = generation._pulled_under_the_width(facts, layout, values, places, pulled, (True, 5.0, 0.0, 12.0), width)
    assert beyond == [1.0, 7.0, 8.0, 9.0, 9.0, 9.0]
    # A run reaching the column's own edge has no stratum inside it to find
    # room beside, and takes the held end whole; handed none, it stands.
    edge = [15.0, 20.0]
    held = generation._pulled_under_the_width(facts, _run_layout(edge), edge, [0, 1], [1, 0], (True, 5.0, 0.0, 9.0), width)
    assert held == [9.0, 9.0]
    stands = generation._pulled_under_the_width(facts, _run_layout(edge), edge, [0, 1], [1, 0], (True, 5.0, 0.0, None), width)
    assert stands == edge
    # A width whose own end is a stand-in the block does not hold: `9999`
    # is refused there as everywhere, and the held end is `9998`.
    four = [9995.0, 9996.0, 9997.0, 9998.0, 15000.0, 20000.0]
    moved = generation._pulled_under_the_width(
        facts, _run_layout(four), four, [1, 2, 3, 4, 5], [5, 4], (True, 9000.0, 0.0, 15000.0), (4, True)
    )
    assert moved == [9995.0, 9996.0, 9997.0, 9998.0, 9998.0, 9998.0]


def test_a_run_never_takes_in_a_stratum_past_the_side_s_own_tail(tmp_path: pathlib.Path) -> None:
    """`_pulled_under_the_width` asked directly: the widening stops at the body however much room lies inside it.

    Strata 1, 7, 8, 15 and 20, the tail the last three. The run of the two
    past the width takes the stratum at 8 in and finds two free values for
    three strata; the stratum at 7 belongs to the body, so the run stops
    there and the last resort places the stratum at 15 on `9` and the
    held end takes the one at 20. Taking 7 in would have found room enough
    -- `2` to `9` -- and moved a stratum of the body.
    """
    facts = _facts(_described(tmp_path, "ones50", _ones_beside_eleven(), 50))
    values = [1.0, 7.0, 8.0, 15.0, 20.0]
    moved = generation._pulled_under_the_width(
        facts, _run_layout(values), values, [2, 3, 4], [4, 3], (True, 5.0, 0.0, 9.0), (1, False)
    )
    assert moved == [1.0, 7.0, 8.0, 9.0, 9.0]


# -- 4. the demands, and which walk a side keeps -------------------------------


def _demands_less_the_commonest(demands, freed, _facts):  # type: ignore[no-untyped-def]
    """The demand choice withdrawn: the cells left come off the demand asking for the most cells, of either kind."""
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


def test_the_cells_left_come_off_the_demand_the_census_counted_them_into(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """200 padded codes beside 100 four-figure numbers, `99999` and `88888`: the unpadded demand gives up the cells.

    The census counts a cell too few to name into its commonest width, and
    into that width's unpadded part where some of its cells are unpadded
    (`_counted_into`); the twin writes its far cells plainly too, so they
    come off the exact demand and the padded ceiling still asks for all
    200 small values. Where every cell of the commonest width is published
    padded -- 100 codes beside 40 plus-signed numbers and `99999` -- the
    census counted the far cell with the padded ones. Its mutant takes the
    cells off the demand asking for the most, the padded one here, and the
    twin misses the padded census.
    """
    described = _described(tmp_path, "mixed_far2", _mixed(200, 100, ["99999", "88888"], 3), 11)
    assert _census(described) == ({"4": 302}, {"4": 200}), "premise: two far cells pooled"
    facts = _facts(described)
    assert generation._field_demands(facts) == [(3, 0, 200), (4, 1, 102)], "premise: the padded demand is the larger"
    assert generation._counted_into(facts) == (4, 1)
    # A tie for the commonest width goes to the first in sorted order, as
    # the census itself breaks it (`parsing.absorbed_census`).
    tied = dataclasses.replace(facts, field_widths={"3": 151, "4": 151}, pad_widths={})
    assert generation._counted_into(tied) == (3, 1)
    assert generation._demands_less_the_freed([(3, 0, 200), (4, 1, 102)], 2, facts) == [(3, 0, 200), (4, 1, 100)]
    plus = _facts(_described(tmp_path, "plus_mixed", _plus_mixed(), 11))
    assert generation._counted_into(plus) == (3, 0)
    assert generation._field_demands(plus) == [(3, 0, 101), (3, 1, 40)]
    assert generation._demands_less_the_freed([(3, 0, 101), (3, 1, 40)], 1, plus) == [(3, 0, 100), (3, 1, 40)]
    for seed in SEEDS:
        assert _missed(described, seed) == [], f"seed {seed}"
    monkeypatch.setattr(generation, "_demands_less_the_freed", _demands_less_the_commonest)
    for seed in SEEDS:
        assert "value:pads.published.4" in _missed(described, seed), f"seed {seed}"


def test_on_a_side_the_reach_rule_left_the_full_walk_stands_where_it_serves_the_census(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codes beside plain numbers and one far value: 110cb46's walk misses the padded census, the full walk does not.

    60 codes beside 90 plain numbers and `99999`, and 90 beside 59, at a
    floor of eleven: the end stood past the width on 110cb46 already, so
    the rule moved nothing, and the full walk -- the tail's other strata
    moved under the width before any demand is served -- stands because it
    serves the census better and neither moment worse. Its mutant keeps
    110cb46's walk, and the twin misses the padded census.
    """
    for padded, unpadded, shape_seed in ((60, 90, 2), (90, 59, 1)):
        described = _described(tmp_path, f"mixed_{padded}_{unpadded}", _mixed(padded, unpadded, ["99999"], shape_seed), 11)
        sides = generation._proven_sides(_facts(described), 4)
        assert [(side[0], side[4]) for side in sides] == [(True, False)], "premise: a side the rule did not move"
        for seed in SEEDS:
            assert _missed(described, seed) == [], f"{padded}/{unpadded} seed {seed}"
        with monkeypatch.context() as patch:
            patch.setattr(generation, "_serves_better", lambda *_arguments: False)
            missed = [seed for seed in SEEDS if "value:pads.published.4" in _missed(described, seed)]
        assert len(missed) >= 2, f"{padded}/{unpadded}: {missed}"


def test_where_the_full_walk_would_cost_a_moment_the_twin_is_110cb46_s(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """300 four-figure numbers beside nine cells from 20000: the full walk would serve the census and move the mean.

    The side's end stood past the width on 110cb46, and there the walk
    stands only where neither published moment is worse: the full walk
    takes the twin's mean from 0.019 to 0.036 real standard deviations
    off, so the twin is 110cb46's. Its mutant takes the full walk always.
    """
    cells = _staircase_far(300, 9, 20000)
    described = _described(tmp_path, "stair", cells, 11)
    kept = {seed: _errors(cells, _twin_numbers(described, seed))[0] for seed in SEEDS}
    monkeypatch.setattr(generation, "_serves_better", lambda *_arguments: True)
    for seed in SEEDS:
        assert _errors(cells, _twin_numbers(described, seed))[0] > kept[seed] + 0.01, f"seed {seed}"


def test_the_full_walk_stands_only_on_a_census_strictly_better_and_no_moment_further_off(tmp_path: pathlib.Path) -> None:
    """`_serves_better` asked directly, on the ten-wide column's hundred one-cell strata.

    The trial leaves ten cells past the width and owes nothing; the walk
    held leaves eleven and owes two. Each published moment is weighed only
    where it is published: with neither, the census decides; a mean or a
    spread published nearer the held walk's refuses the trial; both nearer
    the trial's let it stand; and a trial that serves the census no better
    is refused whatever its moments.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    facts, layout, _values, demands, floor, _sides = _walk_calls(described)[0]
    held = [1000.0 + place for place in range(89)] + [20000.0 + place for place in range(11)]
    trial = [1000.0 + place for place in range(90)] + [20000.0 + place for place in range(10)]
    level = [1100.0 + place for place in range(90)] + [30000.0 + place for place in range(10)]
    owed = generation._census_owed
    assert owed(facts, layout, trial, demands, floor) == 0 == owed(facts, layout, level, demands, floor)
    assert owed(facts, layout, held, demands, floor) == 2
    trial_mean, trial_spread = generation._strata_moments(layout, trial)
    held_mean, held_spread = generation._strata_moments(layout, held)

    def asked(mean, spread, walks):  # type: ignore[no-untyped-def]
        published = dataclasses.replace(facts, mean=mean, std=spread)
        return generation._serves_better(published, layout, walks, demands, floor)

    assert asked(None, None, (trial, held))
    assert not asked(held_mean, None, (trial, held))
    assert not asked(None, held_spread, (trial, held))
    assert asked(trial_mean, trial_spread, (trial, held))
    level_mean, level_spread = generation._strata_moments(layout, level)
    assert not asked(level_mean, level_spread, (level, trial))


def test_where_the_full_walk_serves_the_census_no_better_the_side_keeps_110cb46_s_walk(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """K-S3-22's Pareto(2.5) readings of seed 0 at 36: 16 cells past `999`, as the source holds, where the full walk would leave 7.

    The side's end stood past the width before the reach rule, and its
    census is served on 110cb46's walk with every wide cell pooled; the
    full walk would leave the census no better served and only moves the
    tail's spread, so the side keeps 110cb46's walk. Its mutant takes the
    full walk wherever the census is no worse.
    """
    described = _described(tmp_path, "pareto_0_36", reader.pareto(400, 0), 36)
    sides = generation._proven_sides(_facts(described), 3)
    assert [(side[0], side[4]) for side in sides] == [(True, False)], "premise: a side the rule did not move"
    for seed in SEEDS:
        assert _past(_twin_numbers(described, seed), 999.0) == 16, f"seed {seed}"
    real = generation._census_owed

    def no_worse(facts, layout, walks, demands, floor):  # type: ignore[no-untyped-def]
        return real(facts, layout, walks[0], demands, floor) <= real(facts, layout, walks[1], demands, floor)

    monkeypatch.setattr(generation, "_serves_better", no_worse)
    assert _past(_twin_numbers(described, 0), 999.0) < 10


def test_the_census_owed_counts_the_cells_past_the_width_beyond_the_pool(tmp_path: pathlib.Path) -> None:
    """What `_serves_better` weighs: the demands' unserved cells, and every cell past the width beyond the line less one.

    The ten-wide column's own strata, one cell each, given four-figure
    values and then `wide` of them five: up to the line less one the
    census pools the wide cells into its one width and nothing is owed;
    each cell past that is owed twice, once to the demand it should have
    served and once as a cell at a width the source's census does not
    name.
    """
    described = _described(tmp_path, "ten_wide", _ten_wide(), 11)
    facts, layout, values, demands, floor, _sides = _walk_calls(described)[0]
    assert demands == [(4, 1, 100)] and set(layout.sizes) == {1}, "premise: a hundred one-cell strata, one demand"
    room = parsing.census_floor(floor) - 1
    for wide in (0, 1, room, room + 1, room + 3):
        trial = [1000.0 + place for place in range(len(values) - wide)]
        trial += [20000.0 + place for place in range(wide)]
        assert generation._census_owed(facts, layout, trial, demands, floor) == 2 * max(wide - room, 0), wide


def test_the_strata_moments_are_the_cells_own() -> None:
    """The mean and the n-1 spread of every cell the strata hold, each stratum's value counted once a cell."""
    layout = generation._NumericLayout(
        sizes=(3, 1, 4, 2), starts=(0, 3, 4, 8), bands=("positive",) * 4, raw_budgets=(), folded_budgets=()
    )
    values = [1.0, 2.5, 7.0, 100.0]
    cells = [1.0] * 3 + [2.5] + [7.0] * 4 + [100.0] * 2
    mean, spread = generation._strata_moments(layout, values)
    assert mean == pytest.approx(statistics.fmean(cells))
    assert spread == pytest.approx(statistics.stdev(cells))
    assert generation._strata_moments(layout, [1.0, math.inf, 7.0, 100.0]) == (None, None)


# -- 5. a large table -----------------------------------------------------------


def test_a_hundred_thousand_rows_keep_their_census_and_their_moments(tmp_path: pathlib.Path) -> None:
    """The first skeptic's million-row shape at a hundred thousand rows: the far cells the pair carries, and no more.

    `1000` to `1999` beside five cells from `95555` to `99999`, at a floor
    of eleven. Rule 1 takes the high end to the pair's reach; the walk
    leaves the tail's outermost strata past the width inside the line less
    one and the pair's totals, and moves the rest under it. The twin's own
    census is the source's, its spread no further
    off than 110cb46's and it misses nothing -- 110cb46's twin held every
    cell under the width, read 0.42 of the real spread and missed
    `moments.std`; on a million rows the first form wrote a thousand
    cells on one five-figure value.
    """
    cells = _bulk(100000)
    described = _described(tmp_path, "bulk", cells, 11)
    text = kpi_shapes.twin_text(described, 0)
    written = _numbers([row[0] for row in list(csv.reader(io.StringIO(text)))[1:] if row])
    assert 0 < _past(written, 9999.0) <= parsing.census_floor(11) - 1
    own = kpi_shapes.describe(tmp_path / "own", "own", text, 11).document["columns"][0]
    assert (own["field_widths"], own["pad_widths"]) == _census(described)
    _mean, spread = _errors(cells, written)
    assert spread <= _ON_110CB46[("bulk", 100000, 11)][1] + _SLACK, spread
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "twin-0.csv")) == []

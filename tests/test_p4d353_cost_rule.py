"""Plan P4-D353's readers and stand-in rules, which outlive its cost rule (plan P4-D375).

P4-D353 published a withheld tail pair only where withholding it cost the
twin its mean or spread; plan P4-D375 withdrew the withholding with it,
under the owner's principle of 2026-10-01, and every pair binary64 holds
is published. What stands, and is held here:

* no twin of the battery misses a moment;
* a side binary64 cannot hold says so, in its remark and on both pages;
* a description written BEFORE P4-D375 still carries a side publishing
  neither distance for one of six reasons, and its remark, its summary
  line and its report sentence each say that reason
  (`kpi_shapes.written_before_p4d375`);
* no derived end is a stand-in number (method G5.3b step 5, on both of
  its paths), no row of the staircase on either path, no value G6.6's
  width walk moves, `-9999` among them, and no stratum the convex form
  reads between the tails (G5.4's last rule), in the oracle too -- nor any
  point G6.5a's fills, walk or push take, even in a gap between two values
  the column holds (plan P4-D357 A, which withdrew P4-D353's exemption).

Every table is built at test time from a fixed seed string; no
data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import pathlib
import random

import pytest

import complement_reader as columns
import kpi_shapes
from synthtwin import contract, parsing, summary, taxonomy, validation


def _one_column(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


def _block(folder: pathlib.Path, name: str, cells: "list[str]", floor: int) -> "dict":
    return kpi_shapes.describe(folder, name, _one_column(cells), floor).document["columns"][0]


# -- 2. no twin misses a moment a published pair would keep ------------------

_BATTERY = (
    ("padded_399_beside_one_far", [f"{value:05}" for value in range(1, 400)] + ["12345"], 11),
    ("whole_uniform_150", columns.ordinary("whole_uniform", 150), 36),
    ("two_place_lognormal_150", columns.ordinary("two_place_lognormal", 150), 36),
    ("whole_uniform_distinct_400", columns.ordinary("whole_uniform_distinct", 400), 36),
    ("rung_chained_s2", columns.rung_chained(102, 11, 2)[1], 11),
    ("one_jump_n400_s2", columns.one_jump(400, 36, 2, 100)[1], 36),
)


@pytest.mark.parametrize("name,cells,floor", _BATTERY)
def test_no_twin_misses_a_moment_a_published_pair_would_keep(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int
) -> None:
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), floor)
    for seed in (0, 4):
        outcome = kpi_shapes.measure(
            described, kpi_shapes.twin_text(described, seed), f"twin-{seed}.csv"
        )
        moments = [
            one for one in kpi_shapes.missed(outcome)
            if one.endswith(":moments.mean") or one.endswith(":moments.std")
        ]
        assert moments == [], f"{name} seed {seed}: {moments}"


_STAND_INS = tuple(parsing.NUMERIC_SENTINELS)

_STAND_IN_SHAPES = (
    ("padded_149_beside_one_far", [f"{value:05}" for value in range(1, 150)] + ["12345"]),
    ("far_negative_beside_a_run", columns.far_low(4000, 150)),
)


def _held_stand_ins(written: "list[str]", cells: "list[str]") -> "list[str]":
    """The twin cells on a stand-in number the source column never holds."""
    held = {float(cell) for cell in cells if cell}
    return [
        cell for cell in written if float(cell) in _STAND_INS and float(cell) not in held
    ]


@pytest.mark.parametrize("name,cells", _STAND_IN_SHAPES)
def test_a_derived_end_at_the_width_ceiling_is_never_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]"
) -> None:
    """The far cell's own width is pooled at the floor, so the twin's tail is held to four characters.

    The ceiling of that width is `9999` or `-999`, and a derived end placed
    there is read back by the twin's own description as a stand-in for "no
    value" (plan P4-D353 part 4, `contract._off_the_stand_ins`). The rule
    publishes the far side's pair on both shapes (asserted), and every
    obligation the description publishes must then hold at seeds 0 and 4,
    with no twin cell on a stand-in number.
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    tails = described.document["columns"][0]["tails"]
    assert [side for side in ("low", "high") if tails[side]["mean_distance"] is not None], (
        "premise: the rule publishes the far side's pair on this shape"
    )
    for seed in (0, 4):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = [one for one in written if float(one) in _STAND_INS]
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"{name} seed {seed}: {kpi_shapes.missed(outcome)}"


def _wide_beside_narrow(name: str, narrow: "range", wide: "range", negative: bool) -> "list[str]":
    """145 values of one figure count beside five of one more, shuffled (skeptic A2's shapes).

    Five cells are fewer than the floor, so the width census pools them into
    the commonest width and names ONE width over every cell; the far tail's
    rows then sit past that width's ceiling, and G6.6 moves one of them back
    inside it for the census.
    """
    draw = random.Random(f"skA2/{name}")
    values = draw.sample(narrow, 145) + draw.sample(wide, 5)
    cells = [str(-value if negative else value) for value in values]
    draw.shuffle(cells)
    return cells


def _pareto_all_different() -> "list[str]":
    """1,500 all-different whole Pareto(2) readings times a thousand (skeptic A2's `par2_distinct_1500`)."""
    return columns._distinct_draw(
        random.Random("skA2/par2_distinct_1500"),
        1500,
        lambda draw: str(int(1000 * draw.paretovariate(2.0))),
    )


def _figures_beside(
    name: str, narrow: "range", many: int, wide: "range", few: int, negative: bool
) -> "list[str]":
    """`many` values of one figure count beside `few` of more, shuffled, drawn from a seed of their own."""
    draw = random.Random(f"fA3/{name}")
    values = draw.sample(list(narrow), many) + draw.sample(list(wide), few)
    draw.shuffle(values)
    return [str(-value if negative else value) for value in values]


# (name, cells, the width whose ceiling is a stand-in): the first, second and
# fourth put the walk's value in a TAIL, the third inside the ladder. The
# fourth is the only one whose ceiling is `-9999`.
_WIDTH_WALK_SHAPES = (
    ("w4far5_5_150_s0", _wide_beside_narrow("w4far5_5_150_s0", range(1000, 4000), range(10000, 40000), False), "4"),
    ("negw3_5_150_s0", _wide_beside_narrow("negw3_5_150_s0", range(100, 700), range(1000, 6000), True), "3"),
    ("par2_distinct_1500", _pareto_all_different(), "4"),
    ("negw4_150_4", _figures_beside("negw4_150_4", range(1000, 5000), 150, range(10000, 60000), 4, True), "4"),
)


@pytest.mark.parametrize("name,cells,width", _WIDTH_WALK_SHAPES)
def test_no_value_the_width_walk_moves_is_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", width: str
) -> None:
    """G6.6's width walk takes the nearest value of a census width -- never `9999`, `-999` or `-9999`.

    Measured before the refusal, at a floor of eleven and seeds 0, 4 and 9:
    the four-figure column's twin wrote `9999` inside its high tail and its
    own description read it as absent, MISSING seven obligations (present
    cells, numbers, forms); the three-figure negative column's twin wrote
    `-999` in its low tail; the Pareto column's twin wrote `9999` inside
    its ladder, where it was too rare to be read as absent. With the
    refusal blind to `-9999` alone, the four-figure negative column's twin
    writes `-9999` in its low tail at all three seeds. None of the four
    columns holds a stand-in number.
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    block = described.document["columns"][0]
    assert width in block["field_widths"] and block["field_widths"][width] > len(cells) // 2, (
        "premise: the census names the width whose ceiling is a stand-in, over most cells"
    )
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"{name} seed {seed}: {kpi_shapes.missed(outcome)}"


def _oracle() -> object:
    """The reference oracle (`tools/reference`), as the reference test already loads it."""
    import test_generation_reference as reference

    return reference.gen


def _generator_and_oracle(described: "kpi_shapes.Described") -> "tuple[object, object]":
    """The generator's tail ladder and the oracle's, read from one description."""
    facts = described.loaded.columns[0].facts
    ours = contract.tail_ladder(facts)
    block = dict(described.document["columns"][0])
    block["_rungs"] = {**block["percentiles"], **block["percentiles_between"]}
    return ours, _oracle().tail_ladder(block)


# (name, cells, side): 1,101 whole numbers whose tail on `side` runs through a
# stand-in number. The tail publishes neither distance, so its staircase is one
# grid step a row from the boundary -- through the stand-in. The third column
# skips `-9999` itself: `-10010` to `-10000` beside `-9998` to `-8909`.
_STAIRCASE_SHAPES = (
    ("through_9999", [str(value) for value in range(8900, 10001)], "high"),
    ("through_minus_999", [str(value) for value in range(-1009, 92)], "low"),
    (
        "through_minus_9999",
        [str(value) for value in range(-10010, -9999)] + [str(value) for value in range(-9998, -8908)],
        "low",
    ),
)


@pytest.mark.parametrize("name,cells,side", _STAIRCASE_SHAPES)
def test_no_staircase_row_stands_on_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", side: str
) -> None:
    """G5.3b step 5's rows on the WITHHELD path, in the generator and in the oracle alike.

    1,101 whole numbers at a floor of eleven: eleven rows a side, both pairs
    withheld, so each tail's staircase stands on the eleven grid points past
    its boundary -- `9990` to `10000` above, `-1009` to `-999` below, `-9999`
    to `-10009` below -- and one of them is a stand-in number. The row there
    takes the next grid point outward, held at the end. On the third column,
    which holds no `-9999`, the twin wrote one through G6.5a's separation
    walk on 2af1f03, whose exemption plan P4-D357 A withdrew: no twin of the
    three writes a stand-in its column does not hold at seeds 0, 4 and 9.
    Since plan P4-D375 both pairs are published, so the withheld path is
    asked of the description P4-D349 wrote of each column.
    """
    described = kpi_shapes.written_before_p4d375(
        kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11), ("low", "high")
    )
    tail = described.document["columns"][0]["tails"][side]
    ours, theirs = _generator_and_oracle(described)
    reader = ours.high if side == "high" else ours.low
    boundary = reader.boundary
    reach = [boundary + step if side == "high" else boundary - step for step in range(1, tail["rows"] + 1)]
    assert tail["mean_distance"] is None and [one for one in reach if one in _STAND_INS], (
        "premise: the tail publishes neither distance and its one-step staircase runs through a stand-in"
    )
    rows = list(reader.steps)
    assert [row for row in rows if row in _STAND_INS] == [], f"{name}: a staircase row is a stand-in: {rows}"
    oracle_rows = list((theirs.high if side == "high" else theirs.low)["steps"])
    assert oracle_rows == rows, (
        f"{name}: the oracle, reading method G5.3b step 5, places the rows at {oracle_rows}"
    )
    for seed in (0, 4, 9):
        written = [line for line in kpi_shapes.twin_text(described, seed).split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"


# (name, cells, side): a tail that PUBLISHES its pair, so its staircase is the
# fitted reading of G5.3b step 4, and a stand-in number lies inside its reach.
# Four-figure values beside ten just past `9999`, and three-figure negatives
# beside four of four figures.
_FITTED_STAIRCASE_SHAPES = (
    ("w4_near_11", _figures_beside("w4_near_11", range(6000, 9999), 100, range(10000, 10060), 10, False), "high"),
    ("n3_7", _figures_beside("n3_7", range(700, 999), 298, range(1000, 6000), 4, True), "low"),
)


@pytest.mark.parametrize("name,cells,side", _FITTED_STAIRCASE_SHAPES)
def test_no_fitted_staircase_row_stands_on_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", side: str
) -> None:
    """G5.3b's rows on the FITTED path, in the generator and in the oracle alike.

    The side publishes both distances, so its rows are read through the shape
    fitted to them, and `9999` (`-999`) lies between its boundary and its end.
    With the fitted path's refusal withdrawn, a row lands on it and the twin
    writes it at seeds 0, 4 and 9; with the refusal, no row is a stand-in,
    the oracle places the same rows, and no twin cell is one.
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    tail = described.document["columns"][0]["tails"][side]
    ours, theirs = _generator_and_oracle(described)
    reader = ours.high if side == "high" else ours.low
    inside = [
        one for one in _STAND_INS
        if min(reader.boundary, reader.end) < one < max(reader.boundary, reader.end)
    ]
    assert tail["mean_distance"] is not None and not tail["values"] and inside, (
        "premise: the side publishes its pair, lists no value, and a stand-in lies inside its reach"
    )
    rows = list(reader.steps)
    assert [row for row in rows if row in _STAND_INS] == [], f"{name}: a fitted row is a stand-in: {rows}"
    oracle_rows = list((theirs.high if side == "high" else theirs.low)["steps"])
    assert oracle_rows == rows, (
        f"{name}: the oracle, reading method G5.3b, places the rows at {oracle_rows}"
    )
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"{name} seed {seed}: {kpi_shapes.missed(outcome)}"


# (name, cells, side, moved): 8899 to 9988, then 9989 to 9998, then one far
# 10005 -- and its mirror. At a floor of eleven the far side's eleven rows
# publish neither distance, so its end is eleven grid steps past the boundary
# rung 9988, which is 9999: step 5's WITHHELD path moves it to 9998.
_WITHHELD_END_SHAPES = (
    (
        "withheld_end_on_9999",
        [str(value) for value in range(8899, 9999)] + ["10005"],
        "high",
        9998.0,
    ),
    (
        "withheld_end_on_minus_9999",
        [str(-value) for value in range(8899, 9999)] + ["-10005"],
        "low",
        -9998.0,
    ),
)


@pytest.mark.parametrize("name,cells,side,moved", _WITHHELD_END_SHAPES)
def test_a_withheld_end_on_a_stand_in_moves_one_step_inside(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", side: str, moved: float
) -> None:
    """G5.3b step 5 on its WITHHELD path (`contract._derived_end`, step 2a's end).

    The end of a tail publishing neither distance is `rows` grid steps past
    its boundary; here that is `9999` (`-9999`), and the column holds no
    stand-in number. The generator's end and the oracle's must both stand
    one step inside, and no twin cell may be a stand-in at seeds 0, 4, 9.
    Withdrawn, the twin writes `9999` (`-9999`) at every seed. Asked of the
    description P4-D349 wrote, as plan P4-D375 publishes the far pair.
    """
    described = kpi_shapes.written_before_p4d375(
        kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11), ("low", "high")
    )
    tail = described.document["columns"][0]["tails"][side]
    ours, theirs = _generator_and_oracle(described)
    reader = ours.high if side == "high" else ours.low
    step = 1.0 if side == "high" else -1.0
    assert tail["mean_distance"] is None and reader.boundary + step * tail["rows"] in _STAND_INS, (
        "premise: the far side publishes neither distance and its end would be a stand-in"
    )
    assert reader.end == moved, f"{name}: the withheld end stands at {reader.end}"
    assert (theirs.high if side == "high" else theirs.low)["end"] == moved, (
        f"{name}: the oracle, reading method G5.3b step 5, puts the end elsewhere"
    )
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"


def _run_beside(low: int, high: int, beside: "tuple[int, ...]") -> "list[str]":
    """Every whole number from `low` to `high`, and the few `beside` them, each once (skeptic Ac's shapes)."""
    return [str(value) for value in range(low, high + 1)] + [str(value) for value in beside]


# (name, cells, the stand-in, the side whose tail it lands in): a column whose
# own gap holds a stand-in number. G6.5a's walk to the published count of
# different numbers took it on 2af1f03, where the plan exempted that pass;
# the exemption is withdrawn (plan P4-D357 A, review item 2). One case per
# number of `parsing.NUMERIC_SENTINELS`, and `-999` twice: in a low tail, and
# in a high tail between the column's own -1000 and -998.
_WALK_STAND_IN_SHAPES = (
    ("run_9000_9998_beside_10000", _run_beside(9000, 9998, (10000, 10001)), "9999", "high"),
    ("run_m998_0_beside_m1001", _run_beside(-998, 0, (-1001, -1003)), "-999", "low"),
    ("run_m9998_m9000_beside_m10000", _run_beside(-9998, -9000, (-10000, -10003)), "-9999", "low"),
    ("run_m1300_m1000_beside_m998", _run_beside(-1300, -1000, (-998, -997)), "-999", "high"),
)


@pytest.mark.parametrize(
    "name,cells,stand_in,side",
    _WALK_STAND_IN_SHAPES,
    ids=[case[0] for case in _WALK_STAND_IN_SHAPES],
)
def test_the_separation_walk_takes_no_stand_in_even_in_a_gap_of_the_column_s_own(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", stand_in: str, side: str
) -> None:
    """G6.5a writes no stand-in, not even in a gap of the column's own, and misses nothing.

    PREMISE: the column holds no stand-in number, holds a value on each
    side of this one, and every number it holds is different, so a twin
    holding the published count of different numbers in as many rows
    writes each number once; the stand-in lies beyond that side's
    published boundary. On 2af1f03 the twin wrote that stand-in in one
    cell at seeds 0, 4 and 9 and validation reported nothing: code that
    reads the number as "no value" met a missing cell the source does not
    have. Now the fill and the walk pass it over as a point another stratum
    holds (method G6.5a, plan P4-D357 A) and the twin still meets every
    obligation, its count of different numbers among them.
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    block = described.document["columns"][0]
    number = float(stand_in)
    held = [float(cell) for cell in cells]
    assert number not in held and min(held) < number < max(held), (
        "premise: the stand-in is a gap of the column's own, between two values it holds"
    )
    assert block["n_distinct_values"] == len(cells), "premise: every number is different"
    boundary = validation._file_rung(block, block["tails"][side]["percent"])
    assert boundary is not None and (number > boundary if side == "high" else number < boundary), (
        f"premise: {stand_in} lies beyond the {side} boundary ({boundary})"
    )
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"{name} seed {seed}: {kpi_shapes.missed(outcome)}"


# (value, lowest, highest, figures): the refusal of method G5.4's last rule at
# each grid it names -- whole numbers (0), one width (1 and 2 places) and none
# (-1) -- toward nought, away from it where nought's side leaves the published
# range, and kept where both sides do.
_DRAWN_STAND_INS = (
    (-999.0, -2000.0, 0.0, 0),
    (9999.0, 0.0, 20000.0, 0),
    (-9999.0, -20000.0, 0.0, 0),
    (-999.0, -2000.0, -999.0, 0),
    (-999.0, -999.0, -999.0, 0),
    (-999.0, -2000.0, 0.0, 1),
    (9999.0, 0.0, 20000.0, 2),
    (-9999.0, -20000.0, -9999.0, 1),
    (9999.0, 0.0, 20000.0, -1),
    (-999.0, -2000.0, -999.0, -1),
    (-998.0, -2000.0, 0.0, 0),
)


@pytest.mark.parametrize("value,lowest,highest,figures", _DRAWN_STAND_INS)
def test_the_oracle_moves_a_drawn_stand_in_where_the_generator_does(
    value: float, lowest: float, highest: float, figures: int
) -> None:
    """G5.4's last rule read from the method's sentence (the oracle) and from the generator agree.

    The generator's ladder here is a plain tuple, so no tail reads the share
    and the value stands between the two tails.
    """
    from synthtwin import generation

    rungs = (lowest,) + (value,) * 99 + (highest,)
    ours = generation._drawn_off_the_stand_ins(value, rungs, 1, 2, figures)
    theirs = _oracle().drawn_off_the_stand_ins(value, lowest, highest, figures)
    assert ours == theirs, f"the generator moves {value} to {ours}, the oracle to {theirs}"
    assert lowest <= ours <= highest, f"{value} left the published range for {ours}"
    kept = value not in _STAND_INS or lowest == highest
    assert (ours == value) == kept, f"{value} at grid {figures} in [{lowest}, {highest}] became {ours}"


def test_a_stand_in_read_inside_a_tail_is_the_tail_s(tmp_path: pathlib.Path) -> None:
    """G5.4's last rule stops at a tail: G5.3b step 5 answers for the rows there.

    `through_minus_999` publishes a low tail of eleven rows over 1,101
    numbers. A share inside it is read by the tail, so `-999` read there is
    left to step 5 (a row on the tail's end is the end's); the same number
    read at a share between the two tails moves one unit toward nought.
    """
    from synthtwin import generation

    name, cells, _side = _STAIRCASE_SHAPES[1]
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    ladder = contract.tail_ladder(described.loaded.columns[0].facts)
    numbers = len(cells)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None, "premise: a low tail"
    assert contract.tail_read(ladder, 1, numbers) is not None, "premise: share 1/K is the tail's"
    assert contract.tail_read(ladder, numbers // 2, numbers) is None, "premise: the middle is no tail's"
    assert generation._drawn_off_the_stand_ins(-999.0, ladder, 1, numbers, 0) == -999.0
    assert generation._drawn_off_the_stand_ins(-999.0, ladder, numbers // 2, numbers, 0) == -998.0


# (name, cells): a column whose values run across `-999` without holding it,
# read between its tails -- skeptic Ad's 899 whole numbers, on G5.4's whole
# grid, and 199 tenths from -1010.0 to -990.1, on G5.3's one-width grid.
_DRAWN_STAND_IN_SHAPES = (
    ("gap_interior_m999", _run_beside(-1400, -1000, ()) + _run_beside(-998, -501, ())),
    ("tenths_gap_m999", [f"{tenths / 10:.1f}" for tenths in range(-10100, -9900) if tenths != -9990]),
)


@pytest.mark.parametrize("name,cells", _DRAWN_STAND_IN_SHAPES, ids=[case[0] for case in _DRAWN_STAND_IN_SHAPES])
def test_no_stratum_read_between_the_tails_is_a_stand_in(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str, cells: "list[str]"
) -> None:
    """G5.4's last rule on both of its grids, in the generator and in the oracle alike.

    PREMISE: the column holds no stand-in number, and `-999` lies between
    the two published tail boundaries. The convex form of G5.3 reads `-999`
    for a stratum at seeds 0, 4 and 9, and before the rule every twin of
    skeptic Ad's column wrote it deep in its interior. The draw now holds
    no stand-in; the oracle, reading the method's sentences, builds the
    column's content from seed 0's words cell for cell (the oracle's own
    exact arithmetic takes seconds a seed); and the twin writes `-999` in
    no cell -- on 2af1f03 G6.5a's walk to the published count of different
    numbers, then exempt, took the one free point between two of the
    column's own values at seeds 4 and 9; the exemption is withdrawn (plan
    P4-D357 A) -- and misses nothing.
    """
    from synthtwin import generation

    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
    block = dict(described.document["columns"][0])
    low = validation._file_rung(block, block["tails"]["low"]["percent"])
    high = validation._file_rung(block, block["tails"]["high"]["percent"])
    assert [cell for cell in cells if float(cell) in _STAND_INS] == [], "premise: no stand-in held"
    assert low is not None and high is not None and low < -999.0 < high, (
        f"premise: -999 lies between the boundaries ({low}, {high})"
    )
    block["_rungs"] = {**block["percentiles"], **block["percentiles_between"]}
    reached: "list[float]" = []
    drawn: "list[list[float]]" = []
    built: "list[tuple[list[int], list[str]]]" = []
    refuse = generation._drawn_off_the_stand_ins
    draw = generation._stratum_values
    content = generation._numeric_content

    def refused(
        value: float,
        rungs: "tuple[float, ...]",
        numerator: int,
        denominator: int,
        figures: int,
        kept: "tuple[float, ...]" = (),
    ) -> float:
        if value in _STAND_INS:
            reached.extend([value])
        return refuse(value, rungs, numerator, denominator, figures, kept=kept)

    def values(*arguments, **named):
        found = draw(*arguments, **named)
        drawn.extend([list(found[0])])
        return found

    def cells_of(plan, words):
        found = content(plan, words)
        built.extend([(list(words), list(found[0]))])
        return found

    monkeypatch.setattr(generation, "_drawn_off_the_stand_ins", refused)
    monkeypatch.setattr(generation, "_stratum_values", values)
    monkeypatch.setattr(generation, "_numeric_content", cells_of)
    for seed in (0, 4, 9):
        reached.clear()
        drawn.clear()
        built.clear()
        text = kpi_shapes.twin_text(described, seed)
        assert reached, f"premise: the convex form reads a stand-in at seed {seed}"
        assert len(drawn) == 1 and [one for one in drawn[0] if one in _STAND_INS] == [], (
            f"seed {seed}: the draw holds {[one for one in drawn[0] if one in _STAND_INS]}"
        )
        if seed == 0:
            words, ours = built[0]
            theirs = _oracle()._numeric_content(dict(block, _content_words=words))[0]
            assert theirs == ours, (
                f"seed {seed}: the oracle, reading method G5.4, builds other cells: "
                f"{[(one, two) for one, two in zip(theirs, ours) if one != two][:5]}"
            )
        written = [line for line in text.split("\n")[1:] if line]
        stand_ins = _held_stand_ins(written, cells)
        assert stand_ins == [], f"seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"seed {seed}: {kpi_shapes.missed(outcome)}"


# -- 7. a side withheld for a reason says which ------------------------------
#
# The summary and the quality report once said of EVERY side without a pair
# that its own two distances would give its values back one by one: false
# of a side withheld for the other's sake, unproven on a side whose walk
# did not finish, and false on one binary64 cannot hold (skeptic A1, item
# 2). The producer says each reason in a remark per side (contract NF62 to
# NF67, NF79 to NF84); both pages read it. Since plan P4-D375 the producer
# writes only the binary64 reason, and a description written before it
# carries the other five, so each is asked of such a description here. The
# sentences are asserted by their WORDS, not through the tables the pages
# read, so a table with two causes swapped is red here.


def heap_then_one_far() -> "list[str]":
    """0 to 1,088 once each, 1,089 eleven times and 1,100 once (the stage-3 gate's attack)."""
    return [str(value) for value in range(1089)] + ["1089"] * 11 + ["1100"]


def run_then_scatter() -> "list[str]":
    """0 to 299, then 101 all-different values drawn from 301 to 2,999."""
    return [str(value) for value in range(300)] + [
        str(value) for value in random.Random("skA1/x").sample(range(301, 3000), 101)
    ]


def uniform_distinct_1500() -> "list[str]":
    """1,500 all-different whole numbers drawn from 1 to 29,999."""
    return [str(value) for value in random.Random("skA1/cross2").sample(range(1, 30000), 1500)]


def far_apart_100() -> "list[str]":
    """Eleven cells near `-1.7e308` beside 89 near `1.68e308` (stage 3's review, verdict item 2)."""
    return [repr(-1.7e308 + place * 1e305) for place in range(11)] + [
        repr(1.68e308 - place * 1e305) for place in range(89)
    ]


# The words each page uses for each cause, and nothing but the words: a
# page saying the wrong one is the defect this section exists for.
NOT_ASKED = "not_asked"
SUMMARY_WORDS = {
    taxonomy.TAIL_PINNED: "would give back something the smallest group protects",
    taxonomy.TAIL_PINS_EVERY: "the two distances together would give those values back one by one",
    taxonomy.TAIL_PINS_END: "would give back at least the outermost of those values",
    taxonomy.TAIL_PINS_A_COUNT: "would give back at least how many rows hold one of those values",
    taxonomy.TAIL_WITHHELD_FOR_THE_OTHER: "they could give back the other end's, which are withheld",
    taxonomy.TAIL_WITHHELD_UNSETTLED: "could not be settled, so they are withheld",
    taxonomy.TAIL_WITHHELD_UNHOLDABLE: "too large for this file format to hold",
}
REPORT_WORDS = {
    taxonomy.TAIL_PINNED: "would give back something of the file's own outer cells that the smallest group protects",
    taxonomy.TAIL_PINS_EVERY: "would give the file's own outer cells back one by one",
    taxonomy.TAIL_PINS_END: "would give back at least the file's own outermost cell",
    taxonomy.TAIL_PINS_A_COUNT: "would give back at least how many of the file's own outer cells hold one value",
    taxonomy.TAIL_WITHHELD_FOR_THE_OTHER: "they could give back the other tail's, whose own two distances that description withholds",
    taxonomy.TAIL_WITHHELD_UNSETTLED: "could not be settled, and the rule this description follows withholds them where that cannot be ruled out",
    taxonomy.TAIL_WITHHELD_UNHOLDABLE: "the two numbers are too large for this file format to hold",
}
REMARK_WORDS = {
    taxonomy.TAIL_WITHHELD_FOR_THE_OTHER: "they could give back, by subtraction, the two distances withheld from its",
    taxonomy.TAIL_WITHHELD_UNSETTLED: "did not finish, and a tail is withheld where that cannot be ruled out",
    taxonomy.TAIL_WITHHELD_UNHOLDABLE: "because they are too large for this file format to hold",
    taxonomy.TAIL_PINS_EVERY: "because together they would give every one of those values back",
    taxonomy.TAIL_PINS_END: "because together they would give back at least the outermost of those values",
    taxonomy.TAIL_PINS_A_COUNT: "because together they would give back at least how many rows hold one of those values",
}
SIDE_WORDS = {"low": ("lower", "upper"), "high": ("upper", "lower")}


def _which_page_words(said: str, words: "dict[str, str]") -> str:
    """The one cause whose words a page's sentence carries, or what it carries instead."""
    found = [cause for cause in words if words[cause] in said]
    return found[0] if len(found) == 1 else f"none of the four: {said.strip()!r}"


def _pages_of(block: "dict", document: "dict", name: str, floor: int, side: str) -> "tuple[str, str, str]":
    """What the remark, the summary's line and the report's sentence each say of one silent side."""
    page = summary.render(document, "")
    tail = block["tails"][side]
    which = "smallest" if side == "low" else "largest"
    lines = [
        line for line in page.split("\n")
        if f"the {tail['rows']} {which} values are not published, and neither is how far" in line
    ]
    assert len(lines) == 1, (name, floor, side, lines)
    return (
        taxonomy.tail_withheld_because(block["remarks"], side),
        _which_page_words(lines[0], SUMMARY_WORDS),
        _which_page_words(validation._tail_withheld_reason(block, side), REPORT_WORDS),
    )


def withheld_sides(
    folder: pathlib.Path, name: str, cells: "list[str]", floor: int
) -> "tuple[dict, list[tuple[str, str, str, str, str]]]":
    """The column described, and for each numeric side withheld without a pair and without values:
    (side, why the producer withheld it, the cause its remarks say, the cause
    the summary's words say, the cause the quality report's words say).

    Since plan P4-D375 the one reason the producer has is a pair binary64
    cannot hold, recorded off the real producer's own call (`NOT_ASKED`);
    a side withheld for any other reason would be `TAIL_OPEN`, a defect.
    """
    unholdable: "list[str]" = []
    real_distances = taxonomy._tail_distances

    def distances(ordered, first, last, boundary, side):  # type: ignore[no-untyped-def]
        nonlocal unholdable
        found = real_distances(ordered, first, last, boundary, side)
        if found is None:
            unholdable += [side]
        return found

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(taxonomy, "_tail_distances", distances)
        described = kpi_shapes.describe(folder, name, _one_column(cells), floor)
    block = described.document["columns"][0]
    found: "list[tuple[str, str, str, str, str]]" = []
    tails = block["tails"] if "tails" in block else None
    if not isinstance(tails, dict):
        return block, found
    for side in ("low", "high"):
        tail = tails[side]
        if not isinstance(tail, dict) or tail["mean_distance"] is not None or tail["values"]:
            continue
        own = NOT_ASKED if side in unholdable else taxonomy.TAIL_OPEN
        found += [(side, own) + _pages_of(block, described.document, name, floor, side)]
    return block, found


# The reason true of a withheld side, from why the producer withheld it.
# and, for a PINNED side, from `pinned_reading`.
TRUE_CAUSE = {
    taxonomy.TAIL_OPEN: taxonomy.TAIL_WITHHELD_FOR_THE_OTHER,
    NOT_ASKED: taxonomy.TAIL_WITHHELD_UNHOLDABLE,
}


def misstated(sides: "list[tuple[str, str, str, str, str]]") -> "list[tuple[str, str, str, str, str]]":
    """The sides whose pages say a reason that is not the one true of them, or disagree.

    True of a side the producer withholds: binary64, where its pair was
    never asked; a side withheld for any other reason has none true of it
    since plan P4-D375, and its pages saying the cross-side rule is the
    defect this names.
    """
    wrong: "list[tuple[str, str, str, str, str]]" = []
    for one in sides:
        if not one[2] == one[3] == one[4] or one[2] != TRUE_CAUSE[one[1]] or one[1] != NOT_ASKED:
            wrong += [one]
    return wrong


def test_a_side_binary64_cannot_hold_says_so(tmp_path: pathlib.Path) -> None:
    """The one side the producer still withholds: its remark and both pages say binary64.

    Eleven cells near `-1.7e308` beside 89 near `1.68e308`: the low tail's
    distances pass the largest finite binary64, so it publishes neither
    distance and says why, and the high tail publishes its pair (plan
    P4-D375, withdrawing P4-D357 A's item 4).
    """
    block, sides = withheld_sides(tmp_path / "far", "far_apart_100", far_apart_100(), 11)
    assert [one[0] for one in sides] == ["low"], sides
    _side, own, cause, said, cited = sides[0]
    assert own == NOT_ASKED
    reason = taxonomy.TAIL_WITHHELD_UNHOLDABLE
    assert (cause, said, cited) == (reason, reason, reason), sides
    remark = [line for line in block["remarks"] if "beyond this column's lower tail boundary" in line]
    assert len(remark) == 1 and REMARK_WORDS[reason] in remark[0], block["remarks"]
    assert block["tails"]["high"]["mean_distance"] is not None
    assert misstated(sides) == []


# (cause, side): each reason a description written before plan P4-D375 may
# carry, on the side it was written of.
_BEFORE_REASONS = (
    (taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, "low"),
    (taxonomy.TAIL_WITHHELD_UNSETTLED, "high"),
    (taxonomy.TAIL_WITHHELD_UNHOLDABLE, "low"),
    (taxonomy.TAIL_PINS_EVERY, "high"),
    (taxonomy.TAIL_PINS_END, "low"),
    (taxonomy.TAIL_PINS_A_COUNT, "high"),
)


@pytest.mark.parametrize("cause,side", _BEFORE_REASONS, ids=[one[0] for one in _BEFORE_REASONS])
def test_a_side_withheld_before_p4d375_says_its_reason(
    tmp_path: pathlib.Path, cause: str, side: str
) -> None:
    """A description written before plan P4-D375: the remark and both pages say the reason it carries.

    `heap_then_one_far` described at a floor of eleven, then the named
    side's pair withheld with the remark its producer wrote for ``cause``
    -- as P4-D349 and P4-D353 wrote such sides. The strict loader still
    reads it, the remark names this side in that reason's words, and the
    summary's line and the report's sentence say the same reason.
    """
    described = kpi_shapes.written_before_p4d375(
        kpi_shapes.describe(tmp_path, "heap", _one_column(heap_then_one_far()), 11), (side,), cause
    )
    block = described.document["columns"][0]
    remark, said, cited = _pages_of(block, described.document, "heap", 11, side)
    assert (remark, said, cited) == (cause, cause, cause), (remark, said, cited)
    this, that = SIDE_WORDS[side]
    lines = [line for line in block["remarks"] if f"beyond this column's {this} tail boundary" in line]
    assert len(lines) == 1 and REMARK_WORDS[cause] in lines[0], block["remarks"]
    if cause == taxonomy.TAIL_WITHHELD_FOR_THE_OTHER:
        assert lines[0].endswith(f"withheld from its {that} tail"), lines[0]


def _repeating_draw(size: int) -> "list[str]":
    """`size` whole numbers drawn from 1 to 30,000, repeats allowed: both pairs publish at 11 and at 20."""
    draw = random.Random(f"fA3/pairs_{size}_0")
    return [str(draw.randint(1, 30000)) for _ in range(size)]


def _heaped_draw(size: int, heap: int) -> "list[str]":
    """`_repeating_draw(size)` with its first `heap` cells set to -500 and its last `heap` to 40,000: both ends heaped."""
    cells = _repeating_draw(size)
    return ["-500"] * heap + cells[heap:size - heap] + ["40000"] * heap


# (name, the description's column, its floor, the checked file's column,
# side -> the reason the file's own description gives): the description
# publishes BOTH ENDS, heaped, so each is checked one-sided (method G5.6a)
# against the file's own tail -- and that tail publishes neither distance,
# so the check says why in the words of the file's own reason (skeptic Ac,
# item 1: a report saying the pinned sentence at both ends stayed green).
# Since plan P4-D375 a checked file's own tail is silent only where binary64
# cannot hold its pair.
_HEAPED_REASONS = (
    (
        "far_apart_100",
        _heaped_draw(100, 25),
        11,
        far_apart_100(),
        {"low": taxonomy.TAIL_WITHHELD_UNHOLDABLE},
    ),
)


@pytest.mark.parametrize(
    "name,described_cells,floor,checked_cells,reasons",
    _HEAPED_REASONS,
    ids=[case[0] for case in _HEAPED_REASONS],
)
def test_the_report_says_why_the_file_s_own_tail_is_silent_at_a_heaped_end(
    tmp_path: pathlib.Path,
    name: str,
    described_cells: "list[str]",
    floor: int,
    checked_cells: "list[str]",
    reasons: "dict[str, str]",
) -> None:
    """A heaped end the file's own tail cannot settle is WITHHELD for the reason true of that tail.

    PREMISE, the back-solve's own: the description publishes its minimum
    and maximum; the checked file's own description publishes neither end
    and, on each side named, neither distance nor a value, and that side's
    own verdict is the reason named. Then the one-sided check of that end
    is WITHHELD and its citation carries that reason's words and no
    other's.
    """
    described = kpi_shapes.describe(tmp_path / "described", "described", _one_column(described_cells), floor)
    ends = described.document["columns"][0]["percentiles"]
    assert ends["min"] is not None and ends["max"] is not None, "premise: the description publishes both ends"
    own, sides = withheld_sides(tmp_path / "own", name, checked_cells, floor)
    found = {one[0]: one for one in sides}
    for side, reason in sorted(reasons.items()):
        assert side in found and TRUE_CAUSE[found[side][1]] == reason, f"premise: {name} {side} ({sides})"
        key = "min" if side == "low" else "max"
        assert key not in own["percentiles"] or own["percentiles"][key] is None, f"premise: no {key} of its own"
    outcome = kpi_shapes.measure(described, _one_column(checked_cells), f"{name}.csv")
    for side, reason in sorted(reasons.items()):
        key = "min" if side == "low" else "max"
        checked = [check for check in outcome.checks if check.subcheck == f"ladder.{key} (heaped end, one-sided)"]
        assert len(checked) == 1, (name, side, checked)
        assert checked[0].verdict == validation.WITHHELD, (name, side, checked[0])
        assert _which_page_words(checked[0].citation, REPORT_WORDS) == reason, (name, side, checked[0].citation)


def test_a_heaped_end_over_a_tail_that_does_not_read_says_the_file_s_own_reason() -> None:
    """The heaped-end check's other quiet branch: the file's own tail publishes no distance and
    does not read as a tail (its values are not a list), so no bound is taken from it, and the
    reason is still the one that block's remarks give -- or the whole rule where its role says none.
    """
    remark = taxonomy.rendered(taxonomy.REMARK_LOW_TAIL_FOR_THE_HIGH, ())
    quiet = {"percent": 1, "rows": 12, "mean_distance": None, "rms_distance": None, "values": None}
    for role, remarks, expected in (
        ("count", [remark], taxonomy.TAIL_WITHHELD_FOR_THE_OTHER),
        ("continuous", [], taxonomy.TAIL_PINNED),
    ):
        block = {"role": role, "tails": {"low": quiet}, "remarks": remarks}
        assert validation._file_tail(block, "low") is None, "premise: the tail does not read"
        checked = validation._heaped_end_check("value", "min", -500.0, block, True)
        assert checked.verdict == validation.WITHHELD, checked
        assert _which_page_words(checked.citation, REPORT_WORDS) == expected, checked.citation
    unsaid = validation._heaped_end_check("value", "min", -500.0, {"tails": {"low": quiet}, "remarks": [remark]}, True)
    assert unsaid.citation == validation._GATE_TAIL_WITHHELD_UNSAID, unsaid.citation


def _date_lines_say(page: str) -> "list[str]":
    """The cause the summary's words give for the earliest and the latest tail of a date or clock column."""
    found: "list[str]" = []
    for side in ("earliest", "latest"):
        said = f"the {side} lie beyond it and no distance is published for them: "
        lines = [line for line in page.split("\n") if said in line]
        assert len(lines) == 1, (side, lines)
        clause = lines[0][lines[0].index(said):]
        if "; the latest lie" in clause:
            clause = clause[: clause.index("; the latest lie")]
        found += [_which_page_words(clause, SUMMARY_WORDS)]
    return found


def _minutes_900() -> "list[str]":
    minutes = random.Random("fA3/clock_3").sample(range(24 * 60), 900)
    return ["%02d:%02d" % divmod(minute, 60) for minute in minutes]


# (role, cause): the date and clock reasons a description written before
# plan P4-D375 may carry on both of its sides.
_DATE_REASONS = tuple(
    (name, cause)
    for name in ("clock", "dates")
    for cause in (
        taxonomy.TAIL_WITHHELD_UNSETTLED,
        taxonomy.TAIL_PINS_EVERY,
        taxonomy.TAIL_PINS_END,
        taxonomy.TAIL_PINS_A_COUNT,
    )
)


@pytest.mark.parametrize("name,cause", _DATE_REASONS, ids=[f"{one[0]}-{one[1]}" for one in _DATE_REASONS])
def test_a_date_or_clock_side_withheld_before_p4d375_says_its_reason(
    tmp_path: pathlib.Path, name: str, cause: str
) -> None:
    """The date and clock roles read each reason a description written before plan P4-D375 carries.

    900 all-different minutes of the day (seed `fA3/clock_3`) and 240
    consecutive days publish both pairs since that plan; written as P4-D349
    wrote them -- both pairs withheld, each side's remark the reason named
    -- each side's remark reads back as that reason and the summary says
    it of the earliest and the latest alike, and an UNSETTLED side is never
    said to give its values back one by one.
    """
    cells = _minutes_900() if name == "clock" else columns.consecutive_dates(240)
    fresh = kpi_shapes.describe(tmp_path, name, _one_column(cells), 11)
    for key in ("low_tail", "high_tail"):
        assert fresh.document["columns"][0][key]["mean_distance"] is not None, "premise: the pair is published"
    described = kpi_shapes.written_before_p4d375(fresh, ("low", "high"), cause)
    block = described.document["columns"][0]
    for side in ("low", "high"):
        assert taxonomy.tail_withheld_because(block["remarks"], side) == cause, block["remarks"]
    page = summary.render(described.document, "")
    assert _date_lines_say(page) == [cause, cause]
    if cause == taxonomy.TAIL_WITHHELD_UNSETTLED:
        assert "one by one" not in page


def test_a_block_that_says_no_reason_gets_the_whole_rule_and_no_cause() -> None:
    """A tail the report reads off a block whose producer writes no remark -- a joined part, a wrapper's
    numbers -- is explained by the whole rule, never by a cause the block cannot vouch for.

    `_heaped_end_check` hands a joined part's own block, which carries no
    role; the remark is written by `_numeric_verdict` alone, so on any
    other block a missing remark does not mean PINNED.
    """
    remark = taxonomy.rendered(taxonomy.REMARK_LOW_TAIL_FOR_THE_HIGH, ())
    tails = {"low": {"percent": 1, "rows": 12, "mean_distance": None, "rms_distance": None, "values": []}}
    for block, expected in (
        ({"tails": tails, "remarks": [remark]}, taxonomy.TAIL_PINNED),
        ({"role": "affixed_number", "tails": tails, "remarks": [remark]}, taxonomy.TAIL_PINNED),
        ({"role": "count", "tails": tails, "remarks": [remark]}, taxonomy.TAIL_WITHHELD_FOR_THE_OTHER),
        ({"role": "continuous", "tails": tails, "remarks": []}, taxonomy.TAIL_PINNED),
    ):
        sentence = validation._tail_withheld_reason(block, "low")
        if "role" in block and block["role"] in ("count", "continuous"):
            assert _which_page_words(sentence, REPORT_WORDS) == expected, block
        else:
            assert sentence == validation._GATE_TAIL_WITHHELD_UNSAID, block
            assert "which withholds them where they would give back an outer cell or how many" in sentence
    assert _which_page_words(validation._GATE_TAIL_WITHHELD_UNSAID, REPORT_WORDS).startswith("none of the four")

"""Plan P4-D353: a withheld tail pair that costs the twin its mean or spread is published.

The owner's rulings of 2026-09-25: a tail whose pair would give its own
cells back publishes it ANYWAY where withholding it would make the twin
miss its column's mean or spread, and ONLY there. The producer asks the
description it is about to publish, moment by moment, whether the G12.3
window drawn from it contains the published value; candidates are
offered in the order of what they disclose, and the first that keeps
both moments is published, else the first that keeps the most, else
nothing more.

What is held here, each case asserting its premise from the checker's
own windows before it asserts what the rule did:

* the producer's question IS the checker's window, moment by moment;
* no twin of the battery misses a moment a published pair would keep;
* the candidates come in their order: the other side's own pair first,
  an unsettled side before a pinned one, the low side before the high
  where both say the same, and ONE withheld side with the other's pair;
* where no pair keeps either moment none is published, and where one
  keeps a single moment it is;
* where closing the complement costs nothing it stays closed;
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

import fractions
import math
import pathlib
import random

import pytest

import complement_reader as columns
import cost_rule_window as window
import kpi_shapes
from synthtwin import contract, parsing, summary, taxonomy, validation


def _one_column(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


def _block(folder: pathlib.Path, name: str, cells: "list[str]", floor: int) -> "dict":
    return kpi_shapes.describe(folder, name, _one_column(cells), floor).document["columns"][0]


class _CountsOf:
    """The four counts and the settings the producer's question reads, from a published block."""

    def __init__(self, block: "dict", floor: int) -> None:
        self.settings = taxonomy.Settings(small_cell_floor=floor)
        self.present = [None] * block["n_present"]
        self.numbers = [None] * block["n_numeric"]
        self.n_out_of_range = block["n_out_of_range"]
        self.n_contradictory = block["n_contradictory"]


def _opened(folder: pathlib.Path, name: str, cells: "list[str]", floor: int, monkeypatch) -> "dict":
    """The column described with the back-solve answering OPEN: every real pair, published."""
    with monkeypatch.context() as patched:
        patched.setattr(
            taxonomy, "_numeric_answer", lambda *_arguments, **_named: taxonomy.TAIL_OPEN
        )
        return _block(folder, name, cells, floor)


# -- 1. the producer's question is the checker's window ----------------------

# (name, cells, floor, sides withheld from the published description): one
# moment each way. 150 whole numbers at a floor of 36 publish both pairs, and
# with the low one taken back the MEAN window misses while the spread's still
# reaches; the rung-chained attack column at seed 2 publishes its low pair
# beside a withheld high one, and with the low one taken back too only the
# SPREAD window misses. That is what makes a producer blind to either moment
# visible.
_ONE_MOMENT = (
    ("whole_uniform_150_low_withheld", columns.ordinary("whole_uniform", 150), 36, ("low",)),
    ("rung_chained_s2_both_withheld", columns.rung_chained(102, 11, 2)[1], 11, ("low",)),
)


@pytest.mark.parametrize("name,cells,floor,sides", _ONE_MOMENT)
def test_the_producer_asks_the_checkers_window(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", floor: int, sides: "tuple[str, ...]"
) -> None:
    block = _block(tmp_path, name, cells, floor)
    edited = window.withheld(block, sides)
    checker = window.window_misses(edited, floor)
    assert checker["mean"] != checker["std"], (
        f"{name}: this case must cost ONE moment, or it cannot see a producer blind to one"
    )
    producer = taxonomy._moments_missed(_CountsOf(block, floor), edited)
    assert producer == len(window.missed(edited, floor)), (name, producer, checker)


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


# -- 3. the candidates, in the order of what they disclose -------------------


def test_an_unsettled_side_is_offered_before_a_pinned_one(tmp_path: pathlib.Path) -> None:
    """Either side alone keeps this column's moments (both are unsettled at 36).

    Relabel the LOW side pinned: the rule must publish the HIGH side, the
    one whose pair has not been shown to give its cells back.
    """
    cells = columns.engineering_distinct("whole_uniform", 400, "skA")
    block = _block(tmp_path, "order", cells, 36)
    tails = block["tails"]
    values = sorted(float(one) for one in cells)
    held: "dict[str, tuple[float, float, str]]" = {}
    for side in ("low", "high"):
        percent = tails[side]["percent"]
        where, rung = taxonomy._rung_name(percent)
        first, last = taxonomy._tail_positions(len(values), percent, side)
        pair = taxonomy._tail_distances(values, first, last, block[where][rung], side)
        assert pair is not None
        verdict = taxonomy.TAIL_PINNED if side == "low" else taxonomy.TAIL_UNSETTLED
        held[side] = (pair[0], pair[1], verdict)
    both = window.withheld(block, ("low", "high"))
    counts = _CountsOf(block, 36)
    assert taxonomy._moments_missed(counts, both), "premise: withholding both must cost"
    chosen = taxonomy._pairs_that_cost(counts, both, held)  # type: ignore[arg-type]
    assert chosen["tails"]["high"]["mean_distance"] is not None
    assert chosen["tails"]["low"]["mean_distance"] is None, (
        "the pinned side was published although the unsettled side alone keeps the moments"
    )


def test_the_other_sides_pair_is_offered_before_the_withheld_side(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """The rung-chained attack column at seed 2, floor 11: the high run is withheld, the low side open.

    Premise, from the checker's windows: with both pairs withheld the
    spread misses; with the LOW pair alone back, both windows reach. So the
    rule stops there and the high side the back-solve withheld stays
    withheld. A rule that skipped the other side's own pair would publish
    both.
    """
    cells = columns.rung_chained(102, 11, 2)[1]
    opened = _opened(tmp_path / "open", "chained", cells, 11, monkeypatch)
    block = _block(tmp_path / "shipped", "chained", cells, 11)
    assert window.missed(window.with_pairs(block, opened, ()), 11), "premise: closing both must cost"
    assert window.missed(window.with_pairs(block, opened, ("low",)), 11) == [], (
        "premise: the low pair alone keeps both moments"
    )
    assert block["tails"]["low"]["mean_distance"] is not None
    assert block["tails"]["high"]["mean_distance"] is None, (
        "the withheld side was published although the other side's own pair keeps both moments"
    )


def test_one_withheld_side_is_published_with_the_other_sides_pair(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """150 all-different whole numbers drawn uniformly, floor 36: ONE side withheld by the back-solve.

    The back-solve withholds the high side alone, and the cross-side rule
    withholds the low pair beside it. Premise, from the checker's windows:
    closing both costs a moment, the low pair alone costs both, and the
    two pairs together keep both. So the candidate published is the
    withheld side WITH the other's pair. A rule that offered the withheld
    side alone would find it costs too, publish nothing, and its twin
    would miss its spread.
    """
    draw = random.Random("skeptic-A1/uniform_distinct_150")
    cells = columns._distinct_draw(draw, 150, lambda one: str(one.randint(0, 99999)))
    seen: "dict[str, tuple[float, float, str]]" = {}
    real = taxonomy._pairs_that_cost

    def recording(counts, shaped, held, *present):  # type: ignore[no-untyped-def]
        seen.update(held)
        return real(counts, shaped, held, *present)

    opened = _opened(tmp_path / "open", "one", cells, 36, monkeypatch)
    monkeypatch.setattr(taxonomy, "_pairs_that_cost", recording)
    block = _block(tmp_path / "shipped", "one", cells, 36)
    assert sorted(seen) == ["high"], f"premise: the back-solve withholds the high side alone, not {seen}"
    assert window.missed(window.with_pairs(block, opened, ()), 36), "premise: closing both must cost"
    assert window.missed(window.with_pairs(block, opened, ("low",)), 36), (
        "premise: the other side's pair alone must cost"
    )
    assert window.missed(window.with_pairs(block, opened, ("low", "high")), 36) == [], (
        "premise: the two pairs together keep both moments"
    )
    published = [side for side in ("low", "high") if block["tails"][side]["mean_distance"] is not None]
    assert published == ["low", "high"], (
        f"the withheld side was not published with the other side's pair: {published}"
    )


def test_the_low_side_is_offered_first_where_both_say_the_same(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """400 all-different whole numbers at floor 36 (the engineering review's `skA` draw).

    Both sides are withheld by the back-solve with the same verdict, and
    each ALONE keeps both moments (premise, from the windows), so the
    order decides, and it is written: the low side first.
    """
    cells = columns.engineering_distinct("whole_uniform", 400, "skA")
    seen: "dict[str, tuple[float, float, str]]" = {}
    real = taxonomy._pairs_that_cost

    def recording(counts, shaped, held, *present):  # type: ignore[no-untyped-def]
        seen.update(held)
        return real(counts, shaped, held, *present)

    opened = _opened(tmp_path / "open", "tie", cells, 36, monkeypatch)
    monkeypatch.setattr(taxonomy, "_pairs_that_cost", recording)
    block = _block(tmp_path / "shipped", "tie", cells, 36)
    assert sorted(seen) == ["high", "low"] and seen["low"][2] == seen["high"][2], seen
    assert window.missed(window.with_pairs(block, opened, ()), 36), "premise: withholding both must cost"
    assert window.missed(window.with_pairs(block, opened, ("low",)), 36) == []
    assert window.missed(window.with_pairs(block, opened, ("high",)), 36) == []
    assert block["tails"]["low"]["mean_distance"] is not None
    assert block["tails"]["high"]["mean_distance"] is None


# -- 4. what is published where no candidate keeps both ----------------------


def test_where_no_pair_keeps_a_moment_none_is_published(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """149 padded record numbers beside one far `99999`, floor 11: beyond every pair's reach.

    Premise: every candidate -- nothing, the low pair, the high pair, both
    -- leaves BOTH windows short of their values, so no pair keeps either
    moment and the rule publishes none (the owner's ruling 4: only where
    it costs). The twin still misses its mean and spread: ledger entry
    `K-S3-22`.
    """
    cells = columns.shape("pad99999", 150, 1)
    opened = _opened(tmp_path / "open", "far", cells, 11, monkeypatch)
    block = _block(tmp_path / "shipped", "far", cells, 11)
    for sides in ((), ("low",), ("high",), ("low", "high")):
        assert window.missed(window.with_pairs(block, opened, sides), 11) == ["mean", "std"], (
            f"premise: {sides} must miss both windows"
        )
    assert block["tails"]["low"]["mean_distance"] is None
    assert block["tails"]["high"]["mean_distance"] is None, (
        "a pair was published although no pair keeps either moment"
    )


def test_a_pair_that_keeps_one_moment_is_published_where_none_keeps_both(
    tmp_path: pathlib.Path, monkeypatch
) -> None:
    """One far `-4000` beside 500 to 648, floor 36: both sides withheld by the back-solve.

    Premise: withholding both leaves both windows short; the LOW pair back
    brings the mean's window onto its value and leaves the spread's short;
    no candidate keeps both. The owner's ruling 4 publishes where
    withholding makes the twin miss its mean OR its spread, so the low
    pair is published.
    """
    cells = columns.far_low(4000, 150)
    opened = _opened(tmp_path / "open", "farlow", cells, 36, monkeypatch)
    block = _block(tmp_path / "shipped", "farlow", cells, 36)
    assert window.missed(window.with_pairs(block, opened, ()), 36) == ["mean", "std"]
    assert window.missed(window.with_pairs(block, opened, ("low",)), 36) == ["std"]
    for sides in (("high",), ("low", "high")):
        assert window.missed(window.with_pairs(block, opened, sides), 36), (
            f"premise: {sides} keeps both moments"
        )
    assert block["tails"]["low"]["mean_distance"] is not None, (
        "a pair that keeps the mean was withheld because it does not also keep the spread"
    )
    assert block["tails"]["high"]["mean_distance"] is None


# -- 5. where closing the complement costs nothing it stays closed ------------


def test_the_complement_stays_closed_where_closing_it_is_free(tmp_path: pathlib.Path) -> None:
    """The rung-chained attack column at seed 4, floor 11.

    `d93fd43` published the low pair beside the withheld high run and a
    reader took the twelve high values back by subtraction from the
    column's exact mean and spread. With both pairs withheld the column's
    windows still reach its mean and spread, so the cross-side rule
    stands and the cost rule offers nothing back: no tail's sums are
    published for a subtraction to start from.
    """
    cells = columns.rung_chained(102, 11, 4)[1]
    block = _block(tmp_path, "chained_s4", cells, 11)
    assert block["tails"]["high"]["mean_distance"] is None
    assert block["tails"]["low"]["mean_distance"] is None, (
        "one pair is published beside a withheld one where withholding both costs nothing"
    )
    assert window.missed(block, 11) == []


# -- 6. no derived end, staircase row or width-walk value is a stand-in ------
#
# Plan P4-D353 part 4. `9999`, `-999` and `-9999` are the numbers the
# profiler reads as "no value" where they stand out from a column, and a
# tail's cells are the ones that stand out: a twin cell on one is read back
# by the twin's own description as absent. The derived end moves one grid
# step inside (method G5.3b step 5), a staircase row one grid point outward,
# and G6.6's width walk, whose nearest candidate from beyond a width's
# ceiling is the ceiling itself, refuses them for every value it moves.

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
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
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
    Withdrawn, the twin writes `9999` (`-9999`) at every seed.
    """
    described = kpi_shapes.describe(tmp_path / name, name, _one_column(cells), 11)
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


# -- 7. a side withheld for any other reason than its own pair says which ----
#
# Plan P4-D353 part 2 withholds a side whose own back-solve found it OPEN,
# because beside the column's exact mean and spread its pair would give the
# other, withheld side's back by subtraction. The summary and the quality
# report said of EVERY side without a pair that its own two distances would
# give its values back one by one: false there, unproven on a side whose
# walk did not finish, and false on one binary64 cannot hold (skeptic A1,
# item 2). The producer says each such reason in a remark per side
# (contract NF62 to NF67); both pages read it, and the premise of every
# case here is the back-solve's OWN verdict, recorded where the cost rule
# is handed it. The sentences are asserted by their WORDS, not through the
# tables the pages read, so a table with two causes swapped is red here.


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


def withheld_sides(
    folder: pathlib.Path, name: str, cells: "list[str]", floor: int
) -> "tuple[dict, list[tuple[str, str, str, str, str]]]":
    """The column described, and for each numeric side withheld without a pair and without values:
    (side, the back-solve's OWN verdict, the cause its remarks say, the cause
    the summary's words say, the cause the quality report's words say).

    The own verdict is `TAIL_PINNED` or `TAIL_UNSETTLED` where the walk
    withheld it, `TAIL_OPEN` where the walk did not (the cross-side rule
    withheld it), `NOT_ASKED` where binary64 cannot hold its pair, each
    recorded off the real producer's own calls -- and a PINNED side is
    read again by `pinned_reading`, which enumerates the multisets its
    facts admit without the producer's lattice (plan P4-D357 A): every
    value, the outermost, a count, or `TAIL_PINNED` where the enumeration
    could not decide.
    """
    verdicts: "dict[str, str]" = {}
    unholdable: "list[str]" = []
    real_cost = taxonomy._pairs_that_cost
    real_distances = taxonomy._tail_distances

    def recording(counts, shaped, held, *present):  # type: ignore[no-untyped-def]
        for side in held:
            verdicts[side] = held[side][2]
        return real_cost(counts, shaped, held, *present)

    def distances(ordered, first, last, boundary, side):  # type: ignore[no-untyped-def]
        nonlocal unholdable
        found = real_distances(ordered, first, last, boundary, side)
        if found is None:
            unholdable += [side]
        return found

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(taxonomy, "_pairs_that_cost", recording)
        patched.setattr(taxonomy, "_tail_distances", distances)
        described = kpi_shapes.describe(folder, name, _one_column(cells), floor)
    block = described.document["columns"][0]
    page = summary.render(described.document, "")
    found: "list[tuple[str, str, str, str, str]]" = []
    tails = block["tails"] if "tails" in block else None
    if not isinstance(tails, dict):
        return block, found
    for side in ("low", "high"):
        tail = tails[side]
        if not isinstance(tail, dict) or tail["mean_distance"] is not None or tail["values"]:
            continue
        which = "smallest" if side == "low" else "largest"
        lines = [
            line for line in page.split("\n")
            if f"the {tail['rows']} {which} values are not published, and neither is how far" in line
        ]
        assert len(lines) == 1, (name, floor, side, lines)
        own = NOT_ASKED if side in unholdable else verdicts.get(side, taxonomy.TAIL_OPEN)
        if own == taxonomy.TAIL_PINNED:
            own = pinned_reading(block, side, cells, floor)
        found += [(
            side,
            own,
            taxonomy.tail_withheld_because(block["remarks"], side),
            _which_page_words(lines[0], SUMMARY_WORDS),
            _which_page_words(validation._tail_withheld_reason(block, side), REPORT_WORDS),
        )]
    return block, found


def pinned_reading(block: "dict", side: str, cells: "list[str]", floor: int) -> str:
    """What a PINNED numeric side's pair gives back, by enumerating the multisets its facts admit.

    Independent of the producer's lattice: the tail's own whole parts are
    read off the column's cells and its published boundary on the block's
    grid, and `complement_reader._tail_multisets` lists the multisets of
    that many parts, nought or more and no larger than the sign cap, with
    their sum and sum of squares -- different from one another where the
    column's numbers all are. One multiset: every value. Several, every one
    with the same largest part, held by fewer rows than the floor: the
    outermost. Several with different largest parts: a count. Anything the
    enumeration cannot finish, or a column off a grid: `TAIL_PINNED`,
    which `misstated` reads as undecided.
    """
    figures = columns._grid(block)
    tail = block["tails"][side]
    if figures is None or not isinstance(tail, dict):
        return taxonomy.TAIL_PINNED
    scale = 10**figures
    numbers = sorted(float(cell) for cell in cells if _is_number(cell))
    boundary = fractions.Fraction(columns.rung_of(block, tail["percent"])) * scale
    home = math.floor(boundary) if side == "low" else math.ceil(boundary)
    rows = tail["rows"]
    outer = numbers[:rows] if side == "low" else numbers[len(numbers) - rows:]
    parts = [home - round(value * scale) if side == "low" else round(value * scale) - home for value in outer]
    total = sum(parts)
    squares = sum(part * part for part in parts)
    edge = max(1, columns._cap(block, side, home, squares))
    apart = block["n_distinct_values"] == block["n_used_in_statistics"]
    found, finished = columns._tail_multisets(rows, total, squares, 0, edge, 1 if apart else 0, cap=64)
    if not finished or len(found) >= 64 or sorted(parts) not in found:
        return taxonomy.TAIL_PINNED
    if len(found) == 1:
        return taxonomy.TAIL_PINS_EVERY
    top = max(parts)
    if {max(one) for one in found} == {top} and parts.count(top) < floor:
        return taxonomy.TAIL_PINS_END
    return taxonomy.TAIL_PINS_A_COUNT


def _is_number(cell: str) -> bool:
    try:
        float(cell)
    except ValueError:
        return False
    return True


# The reason true of a withheld side, from the back-solve's own verdict on it
# and, for a PINNED side, from `pinned_reading`.
TRUE_CAUSE = {
    taxonomy.TAIL_PINS_EVERY: taxonomy.TAIL_PINS_EVERY,
    taxonomy.TAIL_PINS_END: taxonomy.TAIL_PINS_END,
    taxonomy.TAIL_PINS_A_COUNT: taxonomy.TAIL_PINS_A_COUNT,
    taxonomy.TAIL_UNSETTLED: taxonomy.TAIL_WITHHELD_UNSETTLED,
    taxonomy.TAIL_OPEN: taxonomy.TAIL_WITHHELD_FOR_THE_OTHER,
    NOT_ASKED: taxonomy.TAIL_WITHHELD_UNHOLDABLE,
}
_PINNED_READINGS = (taxonomy.TAIL_PINS_EVERY, taxonomy.TAIL_PINS_END, taxonomy.TAIL_PINS_A_COUNT)


def misstated(sides: "list[tuple[str, str, str, str, str]]") -> "list[tuple[str, str, str, str, str]]":
    """The sides whose pages say a reason that is not the one true of them.

    True of a side: its own verdict where the walk left it unsettled, the
    cross-side rule where the walk left it open, binary64 where the pair
    was never asked -- and, where the walk PINNED it, what the enumeration
    of `pinned_reading` finds its pair gives back: every value, the
    outermost, or a count (plan P4-D357 A; the pages said "one by one" of
    every pinned side until then). Where that enumeration cannot decide,
    any of the three readings is taken as said, and no other.
    """
    wrong: "list[tuple[str, str, str, str, str]]" = []
    for one in sides:
        if not one[2] == one[3] == one[4]:
            wrong += [one]
        elif one[1] == taxonomy.TAIL_PINNED:
            if one[2] not in _PINNED_READINGS:
                wrong += [one]
        elif one[2] != TRUE_CAUSE[one[1]]:
            wrong += [one]
    return wrong


# (name, cells, floor, side, the reason, the other side's own verdict or ""):
# the three columns the review found, and the two other reasons.
_WITHHELD_REASONS = (
    ("heap_then_one_far", heap_then_one_far(), 11, "low", taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, taxonomy.TAIL_PINS_EVERY),
    ("run_then_scatter", run_then_scatter(), 11, "high", taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, taxonomy.TAIL_PINS_EVERY),
    ("uniform_distinct_1500", uniform_distinct_1500(), 20, "high", taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, taxonomy.TAIL_UNSETTLED),
    ("uniform_distinct_1500", uniform_distinct_1500(), 20, "low", taxonomy.TAIL_WITHHELD_UNSETTLED, ""),
    ("far_apart_100", far_apart_100(), 11, "low", taxonomy.TAIL_WITHHELD_UNHOLDABLE, ""),
)


@pytest.mark.parametrize("name,cells,floor,side,reason,other", _WITHHELD_REASONS)
def test_a_side_withheld_for_another_reason_says_which(
    tmp_path: pathlib.Path,
    name: str,
    cells: "list[str]",
    floor: int,
    side: str,
    reason: str,
    other: str,
) -> None:
    """The remark, the summary's line and the report's sentence each say the reason true of the side.

    PREMISE, the back-solve's own: a side withheld FOR THE OTHER was left
    open by its own walk and the other side was withheld by its own; an
    UNSETTLED side's walk did not finish; an UNHOLDABLE side was never
    asked. Then the remark names THIS side and this reason in its words,
    and neither page says the pair would give the values back.
    """
    block, sides = withheld_sides(tmp_path / name, name, cells, floor)
    found = {one[0]: one for one in sides}
    assert side in found, f"premise: {side} publishes no pair ({sides})"
    _side, own, cause, said, cited = found[side]
    if reason == taxonomy.TAIL_WITHHELD_FOR_THE_OTHER:
        twin = "high" if side == "low" else "low"
        assert own == taxonomy.TAIL_OPEN and found[twin][1] == other, (
            f"premise: {side}'s own walk left it open and {twin}'s withheld it ({sides})"
        )
    elif reason == taxonomy.TAIL_WITHHELD_UNSETTLED:
        assert own == taxonomy.TAIL_UNSETTLED, f"premise: {sides}"
    else:
        assert own == NOT_ASKED, f"premise: {sides}"
    assert cause == reason
    this, that = SIDE_WORDS[side]
    remark = [line for line in block["remarks"] if f"beyond this column's {this} tail boundary" in line]
    assert len(remark) == 1 and REMARK_WORDS[reason] in remark[0], (name, side, block["remarks"])
    if reason == taxonomy.TAIL_WITHHELD_FOR_THE_OTHER:
        assert remark[0].endswith(f"withheld from its {that} tail"), remark[0]
    assert said == reason, f"{name} {side}: the summary says {said}"
    assert cited == reason, f"{name} {side}: the report says {cited}"


def test_a_pinned_side_says_what_its_own_pair_would_give_back(tmp_path: pathlib.Path) -> None:
    """The other side of `heap_then_one_far`, whose own walk PINNED it: one multiset fits, so every value.

    Its eleven rows are ten at the boundary and `1100`, distances
    `[0]*10 + [11]`: sum 11 and squares 121 admit no other multiset, which
    `pinned_reading` finds by enumeration, and the remark and both pages say
    the pair gives every value back (plan P4-D357 A).
    """
    block, sides = withheld_sides(tmp_path / "heap", "heap", heap_then_one_far(), 11)
    found = {one[0]: one for one in sides}
    assert found["high"][1] == taxonomy.TAIL_PINS_EVERY, sides
    assert found["high"][2:] == (taxonomy.TAIL_PINS_EVERY,) * 3, sides
    assert [line for line in block["remarks"] if "upper tail boundary" in line] == [
        taxonomy.rendered(taxonomy.REMARK_HIGH_TAIL_EVERY_VALUE, ())
    ]
    assert misstated(sides) == []


def _repeating_draw(size: int) -> "list[str]":
    """`size` whole numbers drawn from 1 to 30,000, repeats allowed: both pairs publish at 11 and at 20."""
    draw = random.Random(f"fA3/pairs_{size}_0")
    return [str(draw.randint(1, 30000)) for _ in range(size)]


# (name, the description's column, its floor, the checked file's column,
# side -> the reason the file's own description gives): the description
# publishes both pairs at the checked file's own percent, so each tail
# distance is compared and the file's own silence is what the report says.
_CHECKED_REASONS = (
    (
        "heap_then_one_far",
        _repeating_draw(1101),
        11,
        heap_then_one_far(),
        {"low": taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, "high": taxonomy.TAIL_PINS_EVERY},
    ),
    (
        "uniform_distinct_1500",
        _repeating_draw(1500),
        20,
        uniform_distinct_1500(),
        {"low": taxonomy.TAIL_WITHHELD_UNSETTLED, "high": taxonomy.TAIL_WITHHELD_FOR_THE_OTHER},
    ),
)


@pytest.mark.parametrize("name,described_cells,floor,checked_cells,reasons", _CHECKED_REASONS)
def test_the_report_says_why_the_file_s_own_tail_is_silent(
    tmp_path: pathlib.Path,
    name: str,
    described_cells: "list[str]",
    floor: int,
    checked_cells: "list[str]",
    reasons: "dict[str, str]",
) -> None:
    """The quality report's reason for a WITHHELD tail distance is the reason the file's own description gives.

    The description publishes both pairs (premise); the checked file's own
    description publishes neither, and each distance check cites, in the
    words of that side's reason, why -- never the sentence saying its own
    two numbers give the outer cells back where they do not.
    """
    described = kpi_shapes.describe(tmp_path / "described", "described", _one_column(described_cells), floor)
    tails = described.document["columns"][0]["tails"]
    assert [side for side in ("low", "high") if tails[side]["mean_distance"] is not None] == ["low", "high"], (
        "premise: the description publishes both pairs"
    )
    outcome = kpi_shapes.measure(described, _one_column(checked_cells), f"{name}.csv")
    for side, reason in sorted(reasons.items()):
        cited = [
            check.citation for check in outcome.checks
            if check.subcheck in (f"tails.{side}.mean_distance", f"tails.{side}.rms_distance")
        ]
        assert len(cited) == 2, (name, side, cited)
        assert [_which_page_words(one, REPORT_WORDS) for one in cited] == [reason, reason], (name, side, cited)


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
_HEAPED_REASONS = (
    (
        "heap_then_one_far",
        _heaped_draw(1101, 60),
        11,
        heap_then_one_far(),
        {"low": taxonomy.TAIL_WITHHELD_FOR_THE_OTHER, "high": taxonomy.TAIL_PINS_EVERY},
    ),
    (
        "uniform_distinct_1500",
        _heaped_draw(1500, 60),
        20,
        uniform_distinct_1500(),
        {"low": taxonomy.TAIL_WITHHELD_UNSETTLED, "high": taxonomy.TAIL_WITHHELD_FOR_THE_OTHER},
    ),
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


@pytest.mark.parametrize(
    "name,cells",
    (("clock", _minutes_900()), ("dates", columns.consecutive_dates(240))),
    ids=("clock", "dates"),
)
def test_a_date_or_clock_side_whose_walk_did_not_finish_says_so(
    tmp_path: pathlib.Path, monkeypatch, name: str, cells: "list[str]"
) -> None:
    """The date and clock roles say an UNSETTLED side too, and its summary line is not the pinned one.

    900 all-different minutes of the day (seed `fA3/clock_3`) and 240
    consecutive days withhold both pairs, each PINNED by its own walk
    (premise: each side's remark says what the pair gives back, plan
    P4-D357 A, and the page says the same). A walk that spends its budget
    answers UNSETTLED instead, which no seeded column here reaches, so the
    verdict is turned: each side must then carry its remark, and the page
    must say the question could not be settled.
    """
    pinned = kpi_shapes.describe(tmp_path / "pinned", name, _one_column(cells), 11).document
    block = pinned["columns"][0]
    for key in ("low_tail", "high_tail"):
        assert block[key]["mean_distance"] is None and block[key]["values"] is None, "premise: both pairs withheld"
    readings = [taxonomy.tail_withheld_because(block["remarks"], side) for side in ("low", "high")]
    assert [one for one in readings if one not in _PINNED_READINGS] == [], block["remarks"]
    assert _date_lines_say(summary.render(pinned, "")) == readings
    real = taxonomy._tail_verdict

    def spent(*arguments, **named):  # type: ignore[no-untyped-def]
        verdict = real(*arguments, **named)
        return taxonomy.TAIL_UNSETTLED if verdict == taxonomy.TAIL_PINNED else verdict

    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_tail_verdict", spent)
        unsettled = kpi_shapes.describe(tmp_path / "unsettled", name, _one_column(cells), 11).document
    block = unsettled["columns"][0]
    for side, this in (("low", "lower"), ("high", "upper")):
        remark = [line for line in block["remarks"] if f"beyond this column's {this} tail boundary" in line]
        assert len(remark) == 1 and REMARK_WORDS[taxonomy.TAIL_WITHHELD_UNSETTLED] in remark[0], block["remarks"]
        assert taxonomy.tail_withheld_because(block["remarks"], side) == taxonomy.TAIL_WITHHELD_UNSETTLED
    page = summary.render(unsettled, "")
    assert "one by one" not in page
    assert _date_lines_say(page) == [taxonomy.TAIL_WITHHELD_UNSETTLED] * 2


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

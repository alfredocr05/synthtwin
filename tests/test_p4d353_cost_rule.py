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
* no tail cell the construction writes is a stand-in number: not the
  derived end (method G5.3b step 5, on both of its paths), not a row
  of the staircase -- and no value G6.6's width walk moves either.

Every table is built at test time from a fixed seed string; no
data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import pathlib
import random

import pytest

import complement_reader as columns
import cost_rule_window as window
import kpi_shapes
from synthtwin import contract, parsing, taxonomy


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

    def recording(counts, shaped, held):  # type: ignore[no-untyped-def]
        seen.update(held)
        return real(counts, shaped, held)

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

    def recording(counts, shaped, held):  # type: ignore[no-untyped-def]
        seen.update(held)
        return real(counts, shaped, held)

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


# -- 6. no tail cell the construction writes is a stand-in number -----------
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


# (name, cells, the width whose ceiling is a stand-in): the first two put the
# walk's value in a TAIL, the third inside the ladder.
_WIDTH_WALK_SHAPES = (
    ("w4far5_5_150_s0", _wide_beside_narrow("w4far5_5_150_s0", range(1000, 4000), range(10000, 40000), False), "4"),
    ("negw3_5_150_s0", _wide_beside_narrow("negw3_5_150_s0", range(100, 700), range(1000, 6000), True), "3"),
    ("par2_distinct_1500", _pareto_all_different(), "4"),
)


@pytest.mark.parametrize("name,cells,width", _WIDTH_WALK_SHAPES)
def test_no_value_the_width_walk_moves_is_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", width: str
) -> None:
    """G6.6's width walk takes the nearest value of a census width -- never `9999` or `-999`.

    Measured before the refusal, at a floor of eleven and seeds 0, 4 and 9:
    the four-figure column's twin wrote `9999` inside its high tail and its
    own description read it as absent, MISSING seven obligations (present
    cells, numbers, forms); the three-figure negative column's twin wrote
    `-999` in its low tail; the Pareto column's twin wrote `9999` inside
    its ladder, where it was too rare to be read as absent. None of the
    three columns holds a stand-in number.
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


# (name, cells, side): consecutive whole numbers whose tail on `side` runs
# through a stand-in number. The tail publishes neither distance, so its
# staircase is one grid step a row from the boundary -- through the stand-in.
_STAIRCASE_SHAPES = (
    ("through_9999", [str(value) for value in range(8900, 10001)], "high"),
    ("through_minus_999", [str(value) for value in range(-1009, 92)], "low"),
)


@pytest.mark.parametrize("name,cells,side", _STAIRCASE_SHAPES)
def test_no_staircase_row_stands_on_a_stand_in(
    tmp_path: pathlib.Path, name: str, cells: "list[str]", side: str
) -> None:
    """G5.3b step 5's rows, in the generator and in the oracle alike.

    1,101 consecutive whole numbers at a floor of eleven: eleven rows a side,
    both pairs withheld, so each tail's staircase stands on the eleven grid
    points past its boundary -- `9990` to `10000` above, `-1009` to `-999`
    below -- and one of them is a stand-in number. The row there takes the
    next grid point outward, held at the end.
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

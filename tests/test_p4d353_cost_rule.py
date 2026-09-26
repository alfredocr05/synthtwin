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
  where both say the same;
* where no pair keeps either moment none is published, and where one
  keeps a single moment it is;
* where closing the complement costs nothing it stays closed;
* a published pair never makes the twin write a stand-in number.

Every table is built at test time from a fixed seed string; no
data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import pathlib

import pytest

import complement_reader as columns
import cost_rule_window as window
import kpi_shapes
from synthtwin import taxonomy


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
    stands, the cost rule offers nothing back, and the reader rebuilds
    nothing.
    """
    values, cells = columns.rung_chained(102, 11, 4)
    block = _block(tmp_path, "chained_s4", cells, 11)
    assert block["tails"]["high"]["mean_distance"] is None
    assert block["tails"]["low"]["mean_distance"] is None, (
        "one pair is published beside a withheld one where withholding both costs nothing"
    )
    assert window.missed(block, 11) == []
    assert columns.by_subtraction(block, values)["values_rebuilt"] == 0


# -- 6. a published pair never makes the twin write a stand-in number --------

_STAND_IN_SHAPES = (
    ("padded_149_beside_one_far", [f"{value:05}" for value in range(1, 150)] + ["12345"]),
    ("far_negative_beside_a_run", columns.far_low(4000, 150)),
)


@pytest.mark.parametrize("name,cells", _STAND_IN_SHAPES)
def test_a_published_pair_never_makes_the_twin_write_a_stand_in(
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
        stand_ins = [one for one in written if float(one) in (-9999.0, -999.0, 9999.0)]
        assert stand_ins == [], f"{name} seed {seed}: the twin wrote {stand_ins}"
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], f"{name} seed {seed}: {kpi_shapes.missed(outcome)}"

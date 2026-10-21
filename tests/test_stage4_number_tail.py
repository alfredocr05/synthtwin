"""Stage 4 lane G2T: the number tail and spread at scale (plan P4-D405).

Lane G2T's gate. Three measured misses of a number column's published
within-column facts, each red on 36ad3061 and green here:

(a) A column that repeats its numbers read its unlisted tails through the
    one-point-a-row staircase of method G5.3b, so a tail of `m` rows on a
    grid stood over at least `m` points: lane B0's 250,000 x 50 table of
    bells at two places missed every column's published spread by about
    12 per cent (`validate` exit 3, 50 obligations), and a bell at one
    place misses it at 20,000 rows (`test_a_bell_written_at_one_place_meets_its_spread_and_tails`).
(b) G2's dense tail -- whole numbers to `999999` beside five far ones --
    crowded its derived end and was read as no dense side, so G6.6.8's
    rule 4 left it, and where rule 4 placed it G12.3's windows were drawn
    through the staircase alone: 200,000 rows missed the column's mean and
    skew and the tail's two distances on 36ad3061, and 1,000,000 rows the
    mean, skew and kurtosis (`test_the_dense_tail_at_200000_rows_meets_its_moments`).
(c) Counts of a few values piled their high tail on the derived end: 194
    of 200 tail rows on `13` where the source's largest is `12`
    (`test_counts_of_a_few_values_do_not_heap_on_their_derived_end`).

The fix is G5.3b's shared staircase (`contract._shares_its_points`,
`contract._shared_steps`, `contract._spread_for_the_count`), rule 4's
dense test admitting rows held on the derived end (`contract._dense_grid`)
and the moments' and root-mean-square's windows drawn through the ladder
rule 4's placement reads as well (`contract.dense_placed`). Every fixture
is invented: no real data.

THE REPAIR (skeptic 1 of 2026-10-19, plan P4-D405), each case red on its
mutant: the spread aims at the strata G5.2 divides into
(`NumericFacts.strata_asked`) and holds each side's summed distance
(`contract._spread_side`); G5.2a never joins a pinned end's run on a
shared ladder (`generation._merge_down`'s `pinned`); a stratum inside a
tail reads the rank rounded down on both sides (`contract.tail_read`); a
heap-listed tail counts each value from the floor (`contract._heap_floor`);
and the three rules no case reached before -- every zero on a nought end,
the half-step test, the twin report's hull -- each have one.

THE SECOND REPAIR (lane G2T's combined verify and Codex's review of
2026-10-20), each case red on its mutant: the shared staircase holds G5.2's
sign bands (`contract._sign_held`, `_sign_frozen`) and settles each sum to
half a step; the spread finds its moves in logarithmic time
(`contract._Spread`), counted machine-free; grid points are read exactly
(`contract._grid_index`, `_grid_value`, `_grid_exact`); the oracle's three
unread mirrors are read against the product; and K-S4-20's ceilings fail
on 36ad3061's pushed staircase.
"""

from __future__ import annotations

import dataclasses
import math
import pathlib
import random

import pytest

import kpi_shapes
import test_stage3b_width as width
import test_stage4_million_rows as million
from synthtwin import contract, generation, parsing, taxonomy


def _table(columns: "dict[str, list[str]]") -> str:
    """A plain table of ``columns``: none of their cells needs quoting."""
    names = list(columns)
    lines = [",".join(names)]
    for index in range(len(columns[names[0]])):
        lines += [",".join(columns[name][index] for name in names)]
    return "\n".join(lines) + "\n"


def _bell_one_place(rows: int) -> "list[str]":
    """Readings of a bell around 50, spread 5, written at one place."""
    draw = random.Random("g2t/bell/one-place")
    return [f"{50 + 5 * draw.gauss(0.0, 1.0):.1f}" for _row in range(rows)]


_FEW = (
    (0, 0.080), (1, 0.4157), (2, 0.2952), (3, 0.1247), (4, 0.050), (5, 0.020),
    (6, 0.008), (7, 0.003), (8, 0.0015), (9, 0.0008), (10, 0.0004), (11, 0.0002),
    (12, 0.0001), (13, 0.00005), (14, 0.00003), (15, 0.00002), (16, 0.00001),
)


def _counts(rows: int) -> "dict[str, list[str]]":
    """Two count columns: a count of few values mostly 1 to 3, and visits drawn from an exponential, at most 25."""
    draw = random.Random("g2t/counts")
    few: "list[str]" = []
    visits: "list[str]" = []
    for _row in range(rows):
        share = draw.random()
        total = 0.0
        found = 3
        for value, weight in _FEW:
            total = total + weight
            if share < total:
                found = value
                break
        few += [str(found)]
        visits += [str(min(int(draw.expovariate(0.4)), 25))]
    return {"few": few, "visits": visits}


def _twin_numbers(described: kpi_shapes.Described, seed: int) -> "dict[str, list[float]]":
    """Each column's twin cells read back as numbers, the empty ones left out."""
    twin = generation.generate(described.loaded, seed)
    found: "dict[str, list[float]]" = {}
    for place, block in enumerate(described.loaded.columns):
        values: "list[float]" = []
        for cell in twin.columns[place]:
            number = parsing.parse_number(cell) if cell != "" else None
            if number is not None:
                values += [number]
        found[block.name] = values
    return found


def _spread(values: "list[float]") -> float:
    mean = math.fsum(values) / len(values)
    return math.sqrt(math.fsum([(value - mean) ** 2 for value in values]) / (len(values) - 1))


def _tail_mean(values: "list[float]", boundary: float, rows: int, low: bool) -> float:
    ordered = sorted(values)
    kept = ordered[:rows] if low else ordered[len(ordered) - rows:]
    return math.fsum([abs(value - boundary) for value in kept]) / rows


def _boundary(facts: contract.NumericFacts, low: bool) -> float:
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder)
    reader = ladder.low if low else ladder.high
    assert reader is not None
    return reader.boundary


def _outside(facts: contract.NumericFacts, values: "list[float]") -> int:
    """Twin cells past the range the description publishes: its `min` and `max` where printed, the ladder's derived ends otherwise."""
    ladder = contract.tail_ladder(facts)
    assert ladder is not None
    lowest = facts.percentiles.minimum if facts.percentiles.minimum is not None else ladder[0]
    highest = facts.percentiles.maximum if facts.percentiles.maximum is not None else ladder[100]
    return len([value for value in values if value < lowest or value > highest])


def _missed(described: kpi_shapes.Described, seed: int) -> "list[str]":
    text = kpi_shapes.twin_text(described, seed)
    return kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv"))


# -- (a) a column that repeats its numbers --------------------------------------


def test_a_bell_written_at_one_place_meets_its_spread_and_tails(tmp_path: pathlib.Path) -> None:
    """20,000 readings of a bell at one place: the twin's spread within 1 per cent, each tail's mean distance within 10.

    On 36ad3061 both tails stood on one point a row, 200 rows over 200
    tenths, and the twin's spread was 7.5 per cent above the published
    one, its kurtosis 4.98 against 2.97 and each tail's mean distance four
    times the published one (7.4 and 7.3 against 1.7 and 1.6) -- every
    window drawn through that staircase, so `validate` named nothing. At
    250,000 rows on two places (lane B0's table) the same staircase took
    every window past the published spread and `validate` exited 3.
    """
    described = kpi_shapes.describe(tmp_path / "bell", "bell", _table({"reading": _bell_one_place(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.std is not None
    written = _twin_numbers(described, 0)["reading"]
    assert abs(_spread(written) / facts.std - 1.0) < 0.01, _spread(written)
    for side, low in ((facts.tails.low, True), (facts.tails.high, False)):
        assert side is not None and side.mean_distance is not None
        reached = _tail_mean(written, _boundary(facts, low), side.rows, low)
        assert abs(reached / side.mean_distance - 1.0) < 0.10, (low, reached, side.mean_distance)
    assert _outside(facts, written) == 0
    assert _missed(described, 0) == []
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None and ladder.high is not None
    figures = contract._tail_figures(facts)
    for reader in (ladder.low, ladder.high):
        assert reader.steps != contract._tail_steps(reader, figures), "each side reads the shared staircase"


# -- (c) counts of a few values ----------------------------------------------------


def test_counts_of_a_few_values_do_not_heap_on_their_derived_end(tmp_path: pathlib.Path) -> None:
    """20,000 counts of few values: at most five cells on the high tail's derived end, its mean distance within 10 per cent.

    Lane BTp's measurement on 36ad3061: the pushed staircase ran out of
    whole numbers past the boundary and held 194 of the 200 tail rows of
    a count of few values on `13` and 188 of visits on `25`, past the
    source's own largest (`12`, `23`), with the column's spread 27 and 27
    per cent above the published one. Each count now holds its tail rows
    on their own readings, sharing whole numbers, and only the outermost
    stands on the end.
    """
    described = kpi_shapes.describe(tmp_path / "counts", "counts", _table(_counts(20000)))
    written = _twin_numbers(described, 0)
    for block in described.loaded.columns:
        facts = block.facts
        assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.std is not None
        high = facts.tails.high
        ladder = contract.tail_ladder(facts)
        assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and high is not None
        assert high.mean_distance is not None
        values = written[block.name]
        assert len([value for value in values if value == ladder.high.end]) <= 5, block.name
        reached = _tail_mean(values, ladder.high.boundary, high.rows, False)
        assert abs(reached / high.mean_distance - 1.0) < 0.10, (block.name, reached, high.mean_distance)
        assert abs(_spread(values) / facts.std - 1.0) < 0.02, (block.name, _spread(values), facts.std)
        assert _outside(facts, values) == 0, block.name
    assert _missed(described, 0) == []


def test_the_spread_gives_the_count_its_points_past_the_shared_rows(tmp_path: pathlib.Path) -> None:
    """Visits read through the shared staircase alone reach fewer points than the column's count; the spread pushes the outermost rows apart.

    Without it the division of G5.2a divides the column's longest run and
    the walks of G6.5a push its strata apart through the body: on the
    fixture's twin the ones fell from the source's 8,000-odd to about
    1,100 (`contract._spread_for_the_count`'s docstring).
    """
    described = kpi_shapes.describe(tmp_path / "visits", "visits", _table({"visits": _counts(20000)["visits"]}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    figures = contract._tail_figures(facts)
    shared = contract._shared_steps(ladder.high, figures, contract._end_rows(ladder.high, facts))
    assert len(set(ladder.high.steps)) > len(set(shared)), "the spread adds points"
    inner = len(shared) // 2
    assert all(
        abs(moved - read) <= 1.0 for moved, read in zip(ladder.high.steps[:inner], shared[:inner])
    ), "the inner rows stay, or settle one step"
    written = _twin_numbers(described, 0)["visits"]
    assert len(set(written)) == facts.n_distinct_values
    ones = len([value for value in written if value == 1.0])
    source = len([cell for cell in _counts(20000)["visits"] if cell == "1"])
    assert abs(ones / source - 1.0) < 0.10, (ones, source)


def test_the_shared_staircase_stands_only_where_its_conditions_hold(tmp_path: pathlib.Path) -> None:
    """`contract._shares_its_points` and its three refusals, each on its own.

    A column of numbers nearly all different keeps the pushed staircase
    (one point a row is its own model), as does a block whose census names
    one width the shared rows would pass (a figure short where a pad is
    published) and a block whose end G6.6.8's reach rule moved; a tail the
    pushed staircase already meets stays as it was.
    """
    described = kpi_shapes.describe(tmp_path / "bell", "bell", _table({"reading": _bell_one_place(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    figures = contract._tail_figures(facts)
    pushed = dataclasses.replace(ladder.high, steps=contract._tail_steps(ladder.high, figures))
    mean = facts.tails.high.mean_distance if facts.tails.high is not None else None
    assert mean is not None
    assert contract._shares_its_points(pushed, facts, mean), "premise: the bell's high tail shares"
    assert not contract._shares_its_points(pushed, facts, 1000.0), "a staircase that meets the mean stays"
    distinct = dataclasses.replace(facts, n_distinct_values=facts.n_used_in_statistics // 2 + 1)
    assert not contract._shares_its_points(pushed, distinct, mean), "fewer than two cells a number"
    assert contract._shares_its_points(
        pushed, dataclasses.replace(facts, n_distinct_values=facts.n_used_in_statistics // 2), mean
    ), "two cells a number"
    assert not contract._shares_its_points(dataclasses.replace(pushed, withheld=True), facts, mean)
    assert not contract._shares_its_points(dataclasses.replace(pushed, flat=True), facts, mean)
    assert not contract._shares_its_points(dataclasses.replace(pushed, listed=(70.0,)), facts, mean)
    rows = (61.7, 99.0, 150.0)
    assert contract._past_one_width(rows, dataclasses.replace(facts, field_widths={"2": 20000}))
    assert not contract._past_one_width(rows, dataclasses.replace(facts, field_widths={"3": 20000}))
    assert contract._past_one_width(
        rows, dataclasses.replace(facts, field_widths={"3": 20000}, pad_widths={"3": 20000})
    ), "a pad figure stands in front of a value"
    assert not contract._past_one_width(rows, dataclasses.replace(facts, field_widths={"2": 10, "3": 10}))
    reached = width._described(tmp_path, "two_figures_185", width._two_figures_beside_185(), 50)
    reached_facts = reached.loaded.columns[0].facts
    assert isinstance(reached_facts, contract.NumericFacts)
    assert contract.reach_moved_an_end(reached_facts), "premise: the reach rule moved an end"
    moved = contract.tail_ladder(reached_facts)
    assert isinstance(moved, contract.ShapedLadder) and moved.high is not None
    assert moved.high.steps == contract._tail_steps(moved.high, contract._tail_figures(reached_facts))


def test_rows_on_a_zero_end_are_the_zero_stratum_s() -> None:
    """`contract._end_rows`: every zero stands on a nought end, one row on any other."""
    reader = dataclasses.replace(million._HIGH, low=True, end=0.0, rows=40)

    def zeros(count: int) -> contract.NumericFacts:
        facts = million._numeric_facts(40, 400)
        object.__setattr__(facts, "n_zero", count)
        return facts

    assert contract._end_rows(reader, zeros(12)) == 12
    assert contract._end_rows(reader, zeros(0)) == 1
    assert contract._end_rows(reader, zeros(90)) == 40
    assert contract._end_rows(dataclasses.replace(reader, end=1.0), zeros(12)) == 1


def test_the_spread_holds_the_tail_s_summed_distance() -> None:
    """`contract._spread_side` on staircases made to measure: points gained or lost one row at a time, the summed distance held (plan P4-D405, the repair's item 4).

    A row leaves a point that keeps a row for the nearest free point,
    outward while the sum stands at or inside the published one and
    inward past it; where only outward room is left, rows of a run of one
    are brought back inward, through the free points as far as the sum
    owes (the sparse `40` to `32` below, one move since the second
    repair), and a row of a point that keeps a row then settles one step
    onto the occupied point beside it while the sum stands more than half
    a step off (the first staircase's last `1` onto `0`). Spread outward
    only, the build's rule, a count of Pareto draws stood 10.8 per cent
    past its published mean distance at 20,000 rows. Mutant: without the
    shifts back the second staircase's sum stands 14 past the published
    one, more than the bound of half a step a row.
    """

    def spread(steps: "tuple[float, ...]", change: int) -> "tuple[float, ...]":
        side = dataclasses.replace(
            million._HIGH, boundary=0.0, steps=steps, end=steps[len(steps) - 1], rows=len(steps)
        )
        return contract._spread_side(side, -2, change, math.fsum(steps) / len(steps))

    near = (0.0, 0.0, 1.0, 1.0, 1.0, 2.0, 2.0, 9.0, 15.0)
    assert spread(near, 2) == (0.0, 0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 9.0, 15.0), "two points, one row settled"
    heavy = (1.0, 1.0, 1.0, 1.0, 2.0, 2.0, 2.0, 3.0, 3.0, 40.0, 70.0, 100.0)
    spread_heavy = spread(heavy, 4)
    assert spread_heavy == (1.0, 1.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 32.0, 70.0, 100.0)
    assert len(set(spread_heavy)) == len(set(heavy)) + 4
    assert abs(math.fsum(spread_heavy) - math.fsum(heavy)) <= len(heavy) / 2.0
    apart = (1.0, 2.0, 4.0, 5.0, 7.0, 9.0, 9.0, 12.0, 15.0)
    drawn = spread(apart, -3)
    assert drawn == (1.0, 1.0, 5.0, 5.0, 9.0, 9.0, 9.0, 12.0, 15.0), "three runs of one drawn onto their neighbours"
    assert len(set(drawn)) == len(set(apart)) - 3
    for moved in (spread_heavy, drawn):
        assert moved[len(moved) - 1] == 15.0 or moved[len(moved) - 1] == 100.0, "the end's row never moves"
        assert moved.count(moved[len(moved) - 1]) == 1, "no row is moved onto the end"


def test_the_oracle_reads_the_shared_staircase_as_the_product_does(tmp_path: pathlib.Path) -> None:
    """The oracle's `tail_ladder` (written from the method's words) reads every fixture's ladder as `contract.tail_ladder` does (A-P4-59)."""
    from tools.reference import make_generation_reference_vectors as oracle

    tables = {
        "bell": {"reading": _bell_one_place(20000)},
        "counts": _counts(20000),
    }
    shared = 0
    for stem, columns in tables.items():
        described = kpi_shapes.describe(tmp_path / stem, stem, _table(columns))
        for place, block in enumerate(described.loaded.columns):
            facts = block.facts
            assert isinstance(facts, contract.NumericFacts)
            mine = contract.tail_ladder(facts)
            theirs = oracle.tail_ladder(oracle.plain_numbers(described.document["columns"][place]))  # type: ignore[attr-defined]
            assert isinstance(mine, contract.ShapedLadder)
            assert list(mine) == list(theirs), (stem, block.name)
            for reader, other in ((mine.low, theirs.low), (mine.high, theirs.high)):
                assert reader is not None
                assert list(reader.steps) == list(other["steps"]), (stem, block.name, reader.low)
                if reader.steps != contract._tail_steps(reader, contract._tail_figures(facts)):
                    shared += 1
    assert shared >= 4, shared


# -- (b) G2's dense tail -------------------------------------------------------------


def test_the_dense_tail_at_200000_rows_meets_its_moments(tmp_path: pathlib.Path) -> None:
    """G2's dense tail at 200,000 rows: a dense side though its staircase crowds its end, and the twin misses nothing.

    On 36ad3061 the staircase held fifteen rows on the derived end, the
    side was read as no dense side and rule 4 left it: the twin's tail
    stood at a mean distance of 2,035 against a published 2,280 (300,000
    rows) and `validate` missed the column's mean and skew and the tail's
    two distances at 200,000 and 300,000 rows. And G12.3's windows on a
    dense side are now the hull with those the placed ladder draws
    (`contract.dense_placed`): at 1,000,000 rows the staircase's mean
    window, 500,051.9 to 500,061.4, did not reach the published 500,012.3.
    """
    described = million._described_tail(tmp_path / "dense", "dense", million._dense_tail(200000))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    assert _missed(described, 0) == []
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    assert ladder.high.dense_grid == 0, "the high side is dense"
    placed = contract.dense_placed(ladder, facts)
    assert placed is not None and placed.high is not None
    assert facts.tails is not None and facts.tails.high is not None
    published = facts.tails.high.mean_distance
    assert published is not None
    distances = [step - placed.high.boundary for step in placed.high.steps]
    assert abs(math.fsum(distances) / len(distances) - published) <= 1.0, "the placed ladder meets the mean"
    windows = taxonomy.windows_of(None, facts, 11)
    for field, value in (("mean", facts.mean), ("skew", facts.skew), ("kurtosis", facts.kurtosis)):
        assert value is not None
        assert windows[field][0] <= value <= windows[field][1], (field, windows[field], value)
    # AND THE TWIN'S OWN REPORT DRAWS THE SAME HULL (`generation.
    # _numeric_approximations`; the repair's item 6, mutant M9): its
    # windows for the column's moments reach the published values.
    twin = generation.generate(described.loaded, 0)
    reported = {one.fact: one for one in twin.approximations if one.fact in ("mean", "skew", "kurtosis")}
    assert sorted(reported) == ["kurtosis", "mean", "skew"], sorted(reported)
    for fact, one in reported.items():
        assert one.covers_published, (fact, one.lowest, one.published, one.highest)


# -- the repair (skeptic 1 of 2026-10-19) ------------------------------------------


def _clipped_bell(rows: int) -> "list[str]":
    """A bell written at one place, `gauss(28, 6)` clipped at 12 and 70: skeptic 1's battery column of that shape at seed 1, its draws taken in the battery's order."""
    draw = random.Random(1 * 104729 + rows)
    written: "list[str]" = []
    for _row in range(rows):
        draw.gauss(0, 1)
        share = draw.random()
        draw.gauss(0, 1)
        draw.lognormvariate(1.0, 0.8)
        draw.gauss(0, 1)
        draw.gammavariate(1.5, 2.0)
        draw.gauss(0, 1)
        draw.gauss(0, 1)
        if share >= 0.8:
            draw.expovariate(0.5)
        draw.paretovariate(1.5)
        draw.lognormvariate(1.2, 0.9)
        written += [f"{min(max(draw.gauss(28, 6), 12), 70):.1f}"]
    return written


def _pareto(rows: int) -> "list[str]":
    """A count of Pareto draws, `int(pareto(1.5) * 10)`: a heap at 10 and a heavy high tail."""
    draw = random.Random("g2t/pareto")
    return [str(int(draw.paretovariate(1.5) * 10)) for _row in range(rows)]


def _stay(rows: int) -> "list[str]":
    """A length of stay at one place, `lognormal(1.2, 0.9)`."""
    draw = random.Random("g2t/stay")
    return [f"{draw.lognormvariate(1.2, 0.9):.1f}" for _row in range(rows)]


def _few_zeros(rows: int) -> "list[str]":
    """Readings at one place, `lognormal(3, 0.3)`, with a zero on about one row in two hundred: half the low tail's rows, its others too sparse to list."""
    draw = random.Random("g2t/zeros")
    return ["0" if draw.random() < 0.005 else f"{draw.lognormvariate(3.0, 0.3):.1f}" for _row in range(rows)]


def _side_mean(reader: contract.TailReader) -> float:
    return math.fsum([abs(step - reader.boundary) for step in reader.steps]) / len(reader.steps)


def test_a_column_written_two_ways_spreads_to_the_strata_it_divides_into(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """500 potassium readings writing `4` and `4.0`: 31 numbers in 33 spellings, and the twin holds 31 (item 1 (i)).

    G5.2 divides a plain column into the numbers' share of its folded
    spellings, 33 here, and the shared staircase spreads to that count
    (`NumericFacts.strata_asked`). Mutant: spread to `n_distinct_values`
    alone, the build's rule -- the ladder reaches 32 points, G5.2a divides
    the run of `4.0`, its carriers move cells across the low tail and the
    twin holds 29 numbers at seed 4.
    """
    import test_p4d193_twice_written_wholes as twice
    from tests.test_files_review_repairs import _trip

    data = twice._lab_book(404, 500, 0.12)
    result = _trip(tmp_path / "shipped", "labs", data, seed=4)
    column = result["document"]["columns"][0]
    assert (column["n_distinct"], column["n_distinct_values"]) == (33, 31)
    counts = (column["n_numeric"], column["n_out_of_range"], column["n_contradictory"], column["n_not_numeric"])
    assert contract._numbers_share(column["n_distinct_folded"], counts) == 33, "the strata the twin divides into"
    assert result["exits"] == {"real": 0, "twin": 0}, result["twin_missed"]
    monkeypatch.setattr(contract, "_numbers_share", lambda _folded, _counts: 0)
    mutant = _trip(tmp_path / "mutant", "labs", data, seed=4)
    assert mutant["exits"]["twin"] == 3, "the mutant misses the count"


def _delays(rows: int) -> "list[str]":
    """Delays rounded from `lognormal(0.3, 1.0)`: lane G2T's combined verify's `dly` at seed 1, its draws taken in that battery's order."""
    draw = random.Random(1 * 6007 + rows)
    written: "list[str]" = []
    for _row in range(rows):
        draw.lognormvariate(2, 0.6)
        draw.lognormvariate(2, 0.6)
        written += [str(round(draw.lognormvariate(0.3, 1.0)))]
    return written


def test_a_pinned_end_s_run_is_joined_last(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """20,000 delays: one cell on the shared high tail's derived end, its mean distance within 5 per cent (item 2; the second repair's fixture).

    The ladder reaches a few more points than the column publishes, and
    G5.2a's join took the outermost runs of a few rows into the pinned
    end. The join that would take the pinned run now takes the pair
    beside it, inward. Mutant: the pinned runs joined like any other --
    9 cells on the derived end `54` and the tail 9.2 per cent out. (The
    first repair's clipped bell no longer needs the rule since the sums
    settle, and keeps its own case in K-S4-20's battery.)
    """
    described = kpi_shapes.describe(tmp_path / "delays", "delays", _table({"delay": _delays(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and ladder.high.shared

    def measured() -> "tuple[int, float]":
        written = _twin_numbers(described, 0)["delay"]
        assert ladder.high is not None and facts.tails is not None and facts.tails.high is not None
        published = facts.tails.high.mean_distance
        assert published is not None
        reached = _tail_mean(written, ladder.high.boundary, facts.tails.high.rows, False)
        return written.count(ladder.high.end), reached / published - 1.0

    on_end, off = measured()
    assert on_end <= 2 and abs(off) < 0.05, (on_end, off)
    assert _missed(described, 0) == []
    shipped = generation._merge_down
    monkeypatch.setattr(
        generation,
        "_merge_down",
        lambda lengths, held, strata, cap=0, pinned=(False, False): shipped(lengths, held, strata, cap),
    )
    on_end, off = measured()
    assert on_end > 5, ("the mutant piles rows on the end", on_end)


def test_a_stratum_inside_a_shared_tail_reads_a_row_inside_its_ranks() -> None:
    """`contract.tail_read` rounds the rank down on a shared high side as on the low (item 3).

    Rounded up, a one-rank stratum at rank `s` read row `s + 1` at any
    word above nought, so the end was held twice and the innermost row
    never: a count of Pareto draws came back with its spread 11.0 per
    cent above the published one. The pushed staircase keeps rounding up
    (lane G2T2's, plan P4-D405): G6.6.8's width walk and 22 of its cases
    are built on that reading.
    """
    high = dataclasses.replace(million._HIGH, steps=(101.0, 102.0, 103.0, 130.0), shared=True)
    low = dataclasses.replace(
        million._HIGH, low=True, percent=1, boundary=10.0, end=0.0, steps=(9.0, 8.0, 7.0, 0.0), shared=True
    )
    ladder = contract._shaped(tuple([0.0] * 101), low, high)
    for rank, row in ((36, 0), (37, 1), (38, 2)):
        assert contract.tail_read(ladder, 2 * rank, 80) == high.steps[row], rank
        assert contract.tail_read(ladder, 2 * rank + 1, 80) == high.steps[row], rank
    for rank, row in ((1, 2), (2, 1), (3, 0)):
        assert contract.tail_read(ladder, 2 * rank + 1, 80) == low.steps[row], rank
    pushed = contract._shaped(tuple([0.0] * 101), low, dataclasses.replace(high, shared=False))
    assert contract.tail_read(pushed, 2 * 36 + 1, 80) == high.steps[1], "the pushed staircase still rounds up"


def test_a_heavy_tailed_count_keeps_its_tail_s_mean_distance(tmp_path: pathlib.Path) -> None:
    """A count of Pareto draws: the ladder's and the twin's high-tail mean distance within 2 per cent (item 4).

    The shared staircase meets the published mean distance; spread
    outward only for the count, it stood 10.8 per cent past it at 20,000
    rows, 10.0 at 100,000 and 7.4 at 250,000 (skeptic 1's measurement).
    The 250,000-row side is `test_a_heavy_tailed_count_at_250000_rows`.
    """
    described = kpi_shapes.describe(tmp_path / "pareto", "pareto", _table({"count": _pareto(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    published = facts.tails.high.mean_distance
    assert published is not None and facts.std is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and ladder.high.shared
    assert abs(_side_mean(ladder.high) / published - 1.0) < 0.02, _side_mean(ladder.high)
    written = _twin_numbers(described, 0)["count"]
    reached = _tail_mean(written, ladder.high.boundary, facts.tails.high.rows, False)
    assert abs(reached / published - 1.0) < 0.02, reached
    assert abs(_spread(written) / facts.std - 1.0) < 0.02, _spread(written)
    assert len(set(written)) == facts.n_distinct_values
    assert _missed(described, 0) == []


def test_a_heavy_tailed_count_at_250000_rows(tmp_path: pathlib.Path) -> None:
    """The same count at 250,000 rows: the ladder's high-tail mean distance within 1 per cent (item 4; 7.4 per cent out spread outward only)."""
    described = kpi_shapes.describe(tmp_path / "pareto", "pareto", _table({"count": _pareto(250000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None
    published = facts.tails.high.mean_distance
    assert published is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and ladder.high.shared
    assert abs(_side_mean(ladder.high) / published - 1.0) < 0.01, _side_mean(ladder.high)


def test_a_heap_listed_tail_counts_each_value_from_the_floor(tmp_path: pathlib.Path) -> None:
    """A length of stay at one place, 100,000 rows: each listed low-tail value on at least the floor's rows, and the twin misses nothing (item 5).

    The column holds more than 256 different numbers, so its low tail was
    listed only as a heap -- every value on at least eleven cells. Counted
    from two, the twin held `0.2` on 2 cells against the source's 182 and
    `validate` MISSED `tails.low.values`.
    """
    described = kpi_shapes.describe(tmp_path / "stay", "stay", _table({"stay": _stay(100000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.low is not None
    assert facts.tails.low.values, "premise: the low tail is listed"
    assert facts.listing_floor == parsing.DEFAULT_SMALL_CELL_FLOOR
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None
    for value, count in zip(ladder.low.listed, ladder.low.counts):
        if value != ladder.low.boundary:
            assert count >= facts.listing_floor, (value, count)
    assert _missed(described, 0) == []


def test_zeros_on_a_nought_end_are_the_zero_stratum_s(tmp_path: pathlib.Path) -> None:
    """Counts whose zeros are half the low tail: every zero stands on the end in the ladder (the repair's item 6, mutant M3).

    `tail_ladder` hands `_shared_steps` the zero stratum's rows
    (`_end_rows`); handed one, the rows read inside the zeros take the
    shape's readings `1` and up, which no stratum of the twin holds.
    """
    described = kpi_shapes.describe(tmp_path / "zeros", "zeros", _table({"count": _few_zeros(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.low is not None
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None and ladder.low.shared
    assert ladder.low.end == 0.0 and 0 < facts.n_zero < ladder.low.rows, (facts.n_zero, ladder.low.rows)
    assert ladder.low.steps.count(0.0) == facts.n_zero


def test_a_staircase_within_half_a_step_keeps_its_rows(tmp_path: pathlib.Path) -> None:
    """`_shares_its_points` asks for MORE than half a grid step past the published mean distance (the repair's item 6, mutant M12)."""
    described = kpi_shapes.describe(tmp_path / "bell", "bell", _table({"reading": _bell_one_place(20000)}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None
    figures = contract._tail_figures(facts)
    pushed = dataclasses.replace(ladder.high, steps=contract._tail_steps(ladder.high, figures))
    stair = _side_mean(pushed)
    unit = contract._tail_unit(figures)
    assert not contract._shares_its_points(pushed, facts, stair - 0.4 * unit), "within half a step"
    assert contract._shares_its_points(pushed, facts, stair - 0.6 * unit), "past half a step"


def test_the_million_row_driver_keeps_the_caller_s_environment(monkeypatch: "pytest.MonkeyPatch") -> None:
    """`tools/measurements/kpi_dense_million.py` hands its child the caller's environment, two names set (item 9).

    A bare environment drops SYSTEMROOT and the rest Windows needs to
    start Python; `kpi_run.py` and `kpi_suite_time.py` build theirs from
    `os.environ` too. Mutant: the old three-name dictionary.
    """
    import importlib.util
    import os
    import subprocess

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_dense_million.py"
    spec = importlib.util.spec_from_file_location("kpi_dense_million_under_test", path)
    assert spec is not None and spec.loader is not None
    driver = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(driver)
    seen: "list[dict[str, str]]" = []

    class _Done:
        returncode = 0

    def recording(*_arguments: object, **keywords: object) -> _Done:
        environment = keywords["env"]
        assert isinstance(environment, dict)
        seen.append(environment)
        return _Done()

    monkeypatch.setenv("G2T_KEPT_FOR_THE_CHILD", "kept")
    monkeypatch.setattr(subprocess, "run", recording)
    assert driver._run(["--version"]) == 0
    assert seen and seen[0]["G2T_KEPT_FOR_THE_CHILD"] == "kept"
    assert seen[0]["PYTHONHASHSEED"] == "0" and seen[0]["PYTHONPATH"].endswith("src")
    assert seen[0].get("PATH") == os.environ.get("PATH")


# -- the second repair (lane G2T's combined verify and Codex's review, plan P4-D405) --------


def _sign_crossing(rows: int, seed: int) -> "dict[str, list[str]]":
    """The combined verify's `make6` columns at one of its seeds, its draws taken in that battery's order: `hb` is 50 less a rounded `lognormal(1.9, 0.6)`, a few negatives and zeros at its low tail's outermost ranks; `wt` a bell at two places about 0.6 per cent below nought."""
    draw = random.Random(seed * 2741 + rows)
    found: "dict[str, list[str]]" = {"hb": [], "wt": []}
    for _row in range(rows):
        draw.gauss(5, 2)
        draw.gauss(3, 1.2)
        found["hb"] += [str(50 - round(draw.lognormvariate(1.9, 0.6)))]
        found["wt"] += [f"{draw.gauss(4, 1.6):.2f}"]
        if draw.random() > 0.0008:
            draw.gauss(30, 8)
    return found


def _signs_withdrawn(monkeypatch: "pytest.MonkeyPatch") -> None:
    """The mutant: the shared staircase read without G5.2's sign bands."""
    monkeypatch.setattr(contract, "_sign_held", lambda steps, _side, _facts, _figures: steps)
    monkeypatch.setattr(contract, "_sign_frozen", lambda _side, _facts: 0)


def test_a_shared_tail_crossing_nought_holds_the_sign_bands(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """`hb` and `wt` at 20,000 rows, data seeds 1 to 4: every rung and the count held, `hb`'s mean within 0.05 published spreads (new item 1).

    G5.2 lays the negatives and the zero stratum at the column's lowest
    ranks, and the shared staircase read `0`, `1` and `2` at three of
    `hb`'s six negative ranks; the twin held them at `-1`, the count of
    points was two short, G5.2a divided two runs of the body and G6.5a
    pushed them down: `hb`'s median 41 against 43 at seed 1, `wt`'s p25
    and p50 at seed 1, p75 and p90 at seed 2 and `n_distinct_values` at
    seeds 3 and 4 missed, where 36ad3061 met them (`contract._sign_held`,
    `contract._sign_frozen`). Mutant: the sign bands withdrawn.
    """
    tables = {seed: _table(_sign_crossing(20000, seed)) for seed in (1, 2, 3, 4)}
    for seed, text in tables.items():
        described = kpi_shapes.describe(tmp_path / f"head{seed}", f"signs{seed}", text)
        assert _missed(described, 0) == [], seed
        if seed == 1:
            facts = described.loaded.columns[0].facts
            assert isinstance(facts, contract.NumericFacts) and facts.mean is not None and facts.std is not None
            ladder = contract.tail_ladder(facts)
            assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None and ladder.low.shared
            assert facts.n_negative > 0 and facts.n_zero > 0, "premise: the low tail crosses nought"
            written = _twin_numbers(described, 0)["hb"]
            assert abs(math.fsum(written) / len(written) - facts.mean) / facts.std < 0.05
    _signs_withdrawn(monkeypatch)
    missed: "list[str]" = []
    for seed, text in tables.items():
        missed += _missed(kpi_shapes.describe(tmp_path / f"mutant{seed}", f"signs{seed}", text), 0)
    assert "hb:ladder.p50" in missed and "wt:distinct.n_distinct_values" in missed, missed


def _negskew(rows: int) -> "list[str]":
    """Skeptic 1's `negskew`, 100 less a `lognormal(1.0, 0.8)` at two places, its draws taken in that battery's order at seed 1: two cells below nought at 250,000 rows."""
    draw = random.Random(1 * 104729 + rows)
    written: "list[str]" = []
    for _row in range(rows):
        draw.gauss(0, 1)
        share = draw.random()
        draw.gauss(0, 1)
        value = 100 - draw.lognormvariate(1.0, 0.8)
        draw.gauss(0, 1)
        draw.gammavariate(1.5, 2.0)
        draw.gauss(0, 1)
        draw.gauss(0, 1)
        if share >= 0.8:
            draw.expovariate(0.5)
        draw.paretovariate(1.5)
        draw.lognormvariate(1.2, 0.9)
        draw.gauss(28, 6)
        written += [f"{value:.2f}"]
    return written


def test_two_cells_below_nought_at_250000_rows_keep_the_count_and_the_spellings(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """`negskew` at 250,000 rows: `n_distinct_values` held and no signed leading-zero spelling written (new item 1).

    The source holds `-1.98` and `-11.44` below nought. Read without the
    sign bands, the shared staircase counted a point the twin never
    holds, the twin held 2,936 numbers against 2,937 and filled its
    spelling count with `-01.00`, a spelling the source never wrote.
    Mutant: the sign bands withdrawn.
    """
    text = _table({"negskew": _negskew(250000)})
    assert text.count("\n-") == 2, "premise: two cells below nought"
    described = kpi_shapes.describe(tmp_path / "head", "negskew", text)
    written = kpi_shapes.twin_text(described, 0)
    assert "\n-0" not in written
    assert kpi_shapes.missed(kpi_shapes.measure(described, written, "twin-0.csv")) == []
    _signs_withdrawn(monkeypatch)
    mutant = kpi_shapes.describe(tmp_path / "mutant", "negskew", text)
    assert "negskew:distinct.n_distinct_values" in _missed(mutant, 0)


def test_a_coarse_tail_settles_its_sum_to_half_a_step(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """20,000 negated rounded `lognormal(2, 0.6)` with one `-0`: the high tail's mean distance within 5 per cent (new item 1's `lsk`).

    The high tail publishes 200 rows at 0.5 from its boundary `-2`, and
    the shared staircase stood 122 rows on `-2` and 77 on `-1`, 21 per
    cent short, where the source holds 101 and 98: within `m / 2` steps of
    the sum is no bound on a tail of three points. Every shared side now
    settles its sum to half a step, a row of a point that keeps a row
    moving one step onto the occupied point beside it. Mutant: no
    settling move left.
    """
    draw = random.Random("g2t/lsk")
    cells = [f"{-draw.lognormvariate(2, 0.6):.0f}" for _row in range(20000)]
    cells[10000] = "-0"
    described = kpi_shapes.describe(tmp_path / "lsk", "lsk", _table({"lsk": cells}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.tails.high is not None

    def off() -> float:
        ladder = contract.tail_ladder(facts)
        assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and ladder.high.shared
        assert facts.tails is not None and facts.tails.high is not None and facts.tails.high.mean_distance
        written = _twin_numbers(described, 0)["lsk"]
        reached = _tail_mean(written, ladder.high.boundary, facts.tails.high.rows, False)
        return reached / facts.tails.high.mean_distance - 1.0

    assert abs(off()) < 0.05, off()
    assert _missed(described, 0) == []
    monkeypatch.setattr(contract, "_spread_settle", lambda _state, _outward: None)
    assert off() < -0.15, "the mutant stands short"


def _counted_units(monkeypatch: "pytest.MonkeyPatch") -> "list[int]":
    """Count the spread's work units: every search of a sorted list and every heap push and pop."""
    counted = [0]
    for name in ("_found_at", "_heap_in", "_heap_out"):
        shipped = getattr(contract, name)

        def counting(*arguments: object, _shipped: object = shipped) -> object:
            counted[0] = counted[0] + 1
            return _shipped(*arguments)  # type: ignore[operator]

        monkeypatch.setattr(contract, name, counting)
    return counted


def _units(facts: contract.NumericFacts, counted: "list[int]") -> "tuple[int, int]":
    """The work units of one `tail_ladder` and the tail's rows `m`."""
    counted[0] = 0
    ladder = contract.tail_ladder(facts)
    assert isinstance(ladder, contract.ShapedLadder) and ladder.low is not None and ladder.high is not None
    return counted[0], max(ladder.low.rows, ladder.high.rows)


def test_the_spread_works_in_near_linear_time(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """A Pareto column at two places, 250,000 rows: one ladder's work at most `16 m log2 m` units (new item 2).

    Rescanning every run for each move, and moving the sum back one step
    at a time, one ladder took 321.6 s here (6,017 s at 500,000 rows)
    against 0.05 s on 36ad3061; the moves are found in logarithmic time
    now (`contract._Spread`), and a shift moves on through the free points
    as far as the sum owes. Counted, not timed: machine-free. Mutant: the
    sum moved back one step a shift, as the repair did.
    """
    draw = random.Random(1 * 7919 + 250000 * 3)
    cells = [f"{draw.paretovariate(1.1):.2f}" for _row in range(250000)]
    described = kpi_shapes.describe(tmp_path / "pareto", "pareto", _table({"par2": cells}))
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    counted = _counted_units(monkeypatch)
    units, rows = _units(facts, counted)
    bound = 16 * rows * math.log2(rows)
    assert units <= bound, (units, bound)
    shipped = contract._spread_shift

    def one_step(state: contract._Spread, outward: bool, owed: float) -> "tuple[int, int, int] | None":
        return shipped(state, outward, min(owed, 1.0) if owed >= 1.0 else owed)

    monkeypatch.setattr(contract, "_spread_shift", one_step)
    assert _units(facts, counted)[0] > 10 * bound, "the mutant moves one step at a time"


def test_the_spread_s_work_doubles_with_the_rows(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """Codex's measurement columns, `50000 + (N / 100) gauss` at one place, 40,000 and 80,000 rows: the work at most 2.5 times as much at twice the rows (Codex's item 4).

    Each changed point rescanned every run and rebuilt the runs:
    119,277 and 481,700 entries inspected, 4.04 times as many. Mutant:
    every point's entries pushed again after each move, a rescan.
    """
    counted = _counted_units(monkeypatch)
    facts_of: "dict[int, contract.NumericFacts]" = {}
    for rows in (40000, 80000):
        draw = random.Random(77)
        cells = [f"{50000 + (rows / 100) * draw.gauss(0, 1):.1f}" for _row in range(rows)]
        described = kpi_shapes.describe(tmp_path / f"m{rows}", "measure", _table({"x": cells}))
        facts = described.loaded.columns[0].facts
        assert isinstance(facts, contract.NumericFacts)
        facts_of[rows] = facts
    work = {rows: _units(facts_of[rows], counted)[0] for rows in facts_of}
    assert work[80000] <= 2.5 * work[40000], work
    shipped = contract._spread_move

    def rescanning(state: contract._Spread, source: int, target: int) -> None:
        shipped(state, source, target)
        contract._spread_touched(state, sorted(state.count))

    monkeypatch.setattr(contract, "_spread_move", rescanning)
    mutant = {rows: _units(facts_of[rows], counted)[0] for rows in facts_of}
    assert mutant[80000] > 3.0 * mutant[40000], mutant


def test_a_decimal_grid_is_read_exactly(tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch") -> None:
    """Codex's 5,000 readings at 25 places near `4e-10`: every tail reading on the decimal grid, inside its boundary, and the oracle's (Codex's item 1).

    A scale built by multiplying tens is `9.999999999999999e24`, not ten
    to the 25th, and the point `4000000000000001` read back as
    `...000`: 82 of the 100 readings differed from the oracle's and ten
    crossed their boundary. The grid check here is the decimal module's,
    derived apart from both. Mutant: the floating scale.
    """
    import decimal

    from tools.reference import make_generation_reference_vectors as oracle

    draw = random.Random("g2t/decimal-index")
    cells = [f"0.{4000000000000000 + round(50 * draw.gauss(0, 1)):025d}" for _row in range(5000)]
    described = kpi_shapes.describe(tmp_path / "decimal", "decimal", _table({"reading": cells}), floor=11)
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and contract._tail_figures(facts) == 25
    numbers = facts.n_used_in_statistics
    context = decimal.Context(prec=80)
    power = context.power(decimal.Decimal(10), 25)

    def on_the_grid(value: float) -> bool:
        steps = context.multiply(decimal.Decimal(value), power).to_integral_value(rounding=decimal.ROUND_HALF_EVEN)
        return float(context.divide(steps, power)) == value

    def readings() -> "tuple[int, int, int]":
        mine = contract.tail_ladder(facts)
        theirs = oracle.tail_ladder(oracle.plain_numbers(described.document["columns"][0]))  # type: ignore[attr-defined]
        assert isinstance(mine, contract.ShapedLadder) and mine.low is not None and mine.high is not None
        assert mine.low.shared and mine.high.shared, "premise: both sides read the shared staircase"
        differ = crossed = off = 0
        for side in (mine.low, mine.high):
            for row in range(side.rows):
                rank = side.rows - 1 - row if side.low else numbers - side.rows + row
                read = contract.tail_read(mine, 2 * rank + 1, 2 * numbers)
                assert read is not None
                differ += read != oracle.tail_read_at(theirs, 2 * rank + 1, 2 * numbers)  # type: ignore[attr-defined]
                crossed += (read > side.boundary) if side.low else (read < side.boundary)
                off += not on_the_grid(read)
        return differ, crossed, off

    assert readings() == (0, 0, 0)

    def floating(value: float, figures: int) -> "int | None":
        scale = 1.0
        for _figure in range(max(figures, 0)):
            scale = scale * 10.0
        if not math.isfinite(value) or abs(value) * scale >= 2.0**52:
            return None
        return int(round(value * scale))

    monkeypatch.setattr(contract, "_grid_index", floating)
    monkeypatch.setattr(contract, "_grid_value", lambda index, figures: index / float(contract._ten_to(figures)))
    differ, crossed, _off = readings()
    assert differ > 0 and crossed > 0, (differ, crossed)


def test_the_oracle_s_tail_mirrors_are_each_read_against_the_product(tmp_path: pathlib.Path) -> None:
    """Three mirrors no case read (new item 3): `tail_read_at`'s shared high side, `band_allotment`'s pinned join and `heap_floor`.

    Each mutant passed the gate and both reference files: O2 rounds the
    shared high side's rank up, O1 turns the pinned redirect off, O3
    returns a heap floor of nought. Here the oracle reads the Pareto
    count's high tail at every row's middle share as `contract.tail_read`
    does, divides the delays' positive band as `generation._shape_sizes`
    does, and reads the length of stay's heap-listed low tail as
    `contract.tail_ladder` does.
    """
    from tools.reference import make_generation_reference_vectors as oracle

    pareto = kpi_shapes.describe(tmp_path / "pareto", "pareto", _table({"count": _pareto(20000)}))
    facts = pareto.loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts)
    mine = contract.tail_ladder(facts)
    theirs = oracle.tail_ladder(oracle.plain_numbers(pareto.document["columns"][0]))  # type: ignore[attr-defined]
    assert isinstance(mine, contract.ShapedLadder) and mine.high is not None and mine.high.shared
    numbers = facts.n_used_in_statistics
    for rank in range(numbers - mine.high.rows, numbers):
        read = contract.tail_read(mine, 2 * rank + 1, 2 * numbers)
        assert read == oracle.tail_read_at(theirs, 2 * rank + 1, 2 * numbers), rank  # type: ignore[attr-defined]

    delays = kpi_shapes.describe(tmp_path / "delays", "delays", _table({"delay": _delays(20000)}))
    delay_facts = delays.loaded.columns[0].facts
    assert isinstance(delay_facts, contract.NumericFacts) and delay_facts.n_zero > 0
    ladder = contract.tail_ladder(delay_facts)
    other = oracle.tail_ladder(oracle.plain_numbers(delays.document["columns"][0]))  # type: ignore[attr-defined]
    assert isinstance(ladder, contract.ShapedLadder) and ladder.high is not None and ladder.high.shared
    count = delay_facts.n_used_in_statistics
    zeros = delay_facts.n_zero
    strata = delay_facts.n_distinct_values - 1
    sizes = generation._shape_sizes(
        zeros, count - zeros, strata, ladder, count, True, -1, 0, generation._BAND_POSITIVE
    )
    assert sizes == oracle.band_allotment(  # type: ignore[attr-defined]
        count - zeros, strata, other, zeros, count, True, -1, 0, generation._BAND_POSITIVE
    )
    assert sizes[len(sizes) - 1] == 1, "the pinned end keeps its own row"

    stay = kpi_shapes.describe(tmp_path / "stay", "stay", _table({"stay": _stay(100000)}))
    stay_facts = stay.loaded.columns[0].facts
    assert isinstance(stay_facts, contract.NumericFacts) and contract._heap_floor(stay_facts) > 0
    read = contract.tail_ladder(stay_facts)
    heaped = oracle.tail_ladder(oracle.plain_numbers(stay.document["columns"][0]))  # type: ignore[attr-defined]
    assert isinstance(read, contract.ShapedLadder) and read.low is not None and read.low.listed
    assert list(read) == list(heaped)
    assert list(read.low.counts) == list(heaped.low["counts"])


def test_k_s4_20_s_ceilings_fail_on_the_pushed_staircase(
    tmp_path: pathlib.Path, monkeypatch: "pytest.MonkeyPatch"
) -> None:
    """K-S4-20's ceilings judge the repair (Codex's item 3): the fixtures read through 36ad3061's pushed staircase break all three.

    Spread off at most 20 per thousand, a tail's mean distance at most
    100 per thousand and at most five cells on a derived end; 36ad3061
    stood at 76, 3,355 and 193, its counts of misses and of cells past the
    range nought as here. Mutant: no side reads the shared staircase.
    """
    monkeypatch.setattr(contract, "_shares_its_points", lambda _side, _facts, _mean: False)
    measured = number_tail_measures(tmp_path)
    assert measured["widest_spread_off_per_thousand"] > 20.0, measured
    assert measured["widest_tail_mean_distance_off_per_thousand"] > 100.0, measured
    assert measured["most_cells_on_a_derived_end"] > 5, measured


# -- K-S4-20 -------------------------------------------------------------------------


def number_tail_measures(folder: pathlib.Path) -> "dict[str, float]":
    """K-S4-20's values over the gate's fixtures at 20,000 rows and seed 0: the bell at one place and the two counts.

    Machine-free counts: the twin cells written past the range each
    description publishes (its `min` and `max` where printed, the
    ladder's derived ends otherwise), and the spread obligations
    `validate` MISSED -- the moments and each tail's two distances. And,
    recorded beside them, each fixture's twin spread off the published one
    and each tail's mean distance off its published one, in parts per
    thousand, the widest of each. On 36ad3061 the bell's spread stood 76
    parts per thousand off and its tails 3,355; the count's high tail held
    193 cells on its derived end.
    """
    tables = {
        "bell": {"reading": _bell_one_place(20000)},
        "counts": _counts(20000),
    }
    outside = 0
    misses = 0
    spread_off = 0.0
    tail_off = 0.0
    on_end = 0
    for stem, columns in tables.items():
        described = kpi_shapes.describe(folder / stem, stem, _table(columns))
        written = _twin_numbers(described, 0)
        for block in described.loaded.columns:
            facts = block.facts
            assert isinstance(facts, contract.NumericFacts) and facts.tails is not None and facts.std is not None
            values = written[block.name]
            outside = outside + _outside(facts, values)
            spread_off = max(spread_off, abs(_spread(values) / facts.std - 1.0) * 1000.0)
            ladder = contract.tail_ladder(facts)
            assert isinstance(ladder, contract.ShapedLadder)
            for side, reader, low in ((facts.tails.low, ladder.low, True), (facts.tails.high, ladder.high, False)):
                if side is None or reader is None or not side.mean_distance:
                    continue
                reached = _tail_mean(values, reader.boundary, side.rows, low)
                tail_off = max(tail_off, abs(reached / side.mean_distance - 1.0) * 1000.0)
                if not reader.listed and reader.end not in (reader.boundary,):
                    on_end = max(on_end, len([value for value in values if value == reader.end]))
        spread_named = ("moments.", "tails.")
        misses = misses + len(
            [entry for entry in _missed(described, 0) if entry.split(":", 1)[1].startswith(spread_named)]
        )
    return {
        "twin_cells_outside_the_published_range": outside,
        "spread_misses": misses,
        "widest_spread_off_per_thousand": round(spread_off, 1),
        "widest_tail_mean_distance_off_per_thousand": round(tail_off, 1),
        "most_cells_on_a_derived_end": on_end,
    }

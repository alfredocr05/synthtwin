"""Landing 2b.1's gate: the numeric twin is the population it claims to be.

Three defects, all silent, all on the commonest numeric columns there are.

1. ONE NUMBER HELD BY FAR MORE CELLS THAN ANY REAL NUMBER WAS. The join
   of method G5.2a grew a stratum without bound on every ladder that
   moves continuously: 4,000 two-figure cells publishing a `mode_count`
   of 62 came back holding one number 760 times, with `p25` at 0.64
   against 0.79.
2. CELLS AT FULL BINARY PRECISION AND LEADING ZEROS THE COLUMN NEVER
   WROTE. On a column of tenths the strata did not line up with the
   tenths, the width snap refused the narrow ones, and 2,000 cells
   publishing 517 numbers came back with 227 cells like
   `55.44657068472738`, spellings like `053.6`, and 479 numbers.
3. A SELF-CHECK THAT COULD NOT FAIL. The twin's own report drew its
   windows from the inflated stratum and called every one of those
   twins inside.

So each shape here is DESCRIBED, BUILT, AND DESCRIBED AGAIN, at several
seeds and at the sizes these columns really have, and the facts the
defects broke must come back: the fraction widths, the count of
different numbers, no number held by more cells than the published
`mode_count`, no cell outside the published width, and both the twin
and the real table checked against the description with exit code 0.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import collections
import math
import pathlib
import random
import re

import pytest

from synthtwin import contract, generation, profile, reading, rendering, taxonomy
from synthtwin import validation
from tests import fixtures
from tests.test_stage2_round_trip import _round_trip

SEEDS = ("1", "7", "23")


def _one_figure_gaussian(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(70, 12):.1f}" for _ in range(rows)]


def _narrow_one_figure(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(37, 0.5):.1f}" for _ in range(rows)]


def _small_one_figure(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(6.5, 1.2):.1f}" for _ in range(rows)]


def _skewed_two_figures(draw: random.Random, rows: int) -> "list[str]":
    return ["%.2f" % draw.lognormvariate(0.0, 0.35) for _ in range(rows)]


def _gaussian_two_figures(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(4.2, 0.6):.2f}" for _ in range(rows)]


def _folded_one_figure(draw: random.Random, rows: int) -> "list[str]":
    return [f"{abs(draw.gauss(12, 4)):.1f}" for _ in range(rows)]


def _bounded_share(draw: random.Random, rows: int) -> "list[str]":
    return [
        "%.1f" % min(100.0, max(0.0, draw.betavariate(2, 5) * 100))
        for _ in range(rows)
    ]


def _uniform_three_figures(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.random():.3f}" for _ in range(rows)]


def _whole_hundreds(draw: random.Random, rows: int) -> "list[str]":
    return [
        str(int(round(draw.lognormvariate(10.8, 0.7), -2)))
        for _ in range(rows)
    ]


def _whole_gaussian(draw: random.Random, rows: int) -> "list[str]":
    return [str(int(draw.gauss(78, 12))) for _ in range(rows)]


def _wrapped_one_figure(draw: random.Random, rows: int) -> "list[str]":
    return [f"{draw.gauss(80, 16):.1f} kg" for _ in range(rows)]


# The commonest real shapes first: a column of tenths around a centre, a
# narrow one, a small one, then hundredths, then the rest.
SHAPES = [
    ("one_figure_gaussian", _one_figure_gaussian, 2000, 17),
    ("one_figure_gaussian", _one_figure_gaussian, 500, 5),
    ("narrow_one_figure", _narrow_one_figure, 2000, 17),
    ("small_one_figure", _small_one_figure, 4000, 17),
    ("skewed_two_figures", _skewed_two_figures, 4000, 23),
    ("skewed_two_figures", _skewed_two_figures, 2000, 23),
    ("gaussian_two_figures", _gaussian_two_figures, 2000, 17),
    ("folded_one_figure", _folded_one_figure, 400, 17),
    ("bounded_share", _bounded_share, 4000, 23),
    ("uniform_three_figures", _uniform_three_figures, 3000, 41),
    ("whole_hundreds", _whole_hundreds, 2000, 17),
    ("whole_gaussian", _whole_gaussian, 4000, 23),
    ("wrapped_one_figure", _wrapped_one_figure, 2000, 41),
]


def _number(cell: str) -> "float | None":
    found = re.fullmatch(r"(-?\d+(?:\.\d+)?)( kg)?", cell)
    return float(found.group(1)) if found else None


def _figures(cell: str) -> int:
    found = re.fullmatch(r"-?\d+(?:\.(\d+))?( kg)?", cell)
    if found is None or found.group(1) is None:
        return 0
    return len(found.group(1))


@pytest.mark.parametrize(
    "name,build,rows,data_seed",
    SHAPES,
    ids=[f"{shape[0]}-{shape[2]}" for shape in SHAPES],
)
def test_the_numeric_facts_come_back_from_the_twin(
    tmp_path: pathlib.Path, name: str, build, rows: int, data_seed: int
) -> None:
    """Described, built, described again: the broken facts return."""
    cells = build(random.Random(data_seed), rows)
    real = collections.Counter(_number(cell) for cell in cells)
    real_most = max(real.values())
    real_leading = any(re.match(r"-?0\d", cell) for cell in cells)
    for seed in SEEDS:
        first, second, written, twin_exit, real_exit = _round_trip(
            tmp_path / seed, cells, check_real=seed == SEEDS[0], seed=seed
        )
        assert twin_exit == 0, (name, rows, seed, "the twin missed")
        assert real_exit == 0, (name, rows, seed, "the real table missed")
        assert first["mode_count"] == real_most
        held = collections.Counter(_number(cell) for cell in written)
        assert None not in held, (name, seed, "a cell that is not a number")
        # NO NUMBER OF THE TWIN HELD BY MORE CELLS THAN ANY REAL NUMBER.
        assert max(held.values()) <= first["mode_count"], (
            name,
            rows,
            seed,
            max(held.values()),
            first["mode_count"],
        )
        assert second["mode_count"] <= first["mode_count"]
        # THE COUNT OF DIFFERENT NUMBERS AND THE FRACTION WIDTHS, EXACTLY.
        assert second["n_distinct_values"] == first["n_distinct_values"], (
            name,
            rows,
            seed,
        )
        assert second["fraction_widths"] == first["fraction_widths"], (
            name,
            rows,
            seed,
        )
        assert second["numeric_styles"] == first["numeric_styles"]
        # ...CELL BY CELL: no cell outside a published width, none at
        # full binary precision, and no leading zero the column never
        # wrote.
        widths = {int(width) for width in first["fraction_widths"]}
        if not widths:
            widths = {0}
        outside = [cell for cell in written if _figures(cell) not in widths]
        assert outside == [], (name, rows, seed, outside[:5])
        if not real_leading:
            leading = [cell for cell in written if re.match(r"-?0\d", cell)]
            assert leading == [], (name, rows, seed, leading[:5])


def _described(
    folder: pathlib.Path, cells: "list[str]"
) -> "tuple[contract.Profile, contract.ColumnBlock]":
    path = fixtures.write(folder, "real.csv", "value\n" + "\n".join(cells) + "\n")
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), []
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, "real-profile.json", document))
    )
    return loaded, loaded.columns[0]


@pytest.mark.parametrize(
    "build,rows,data_seed",
    [
        (_skewed_two_figures, 4000, 23),
        (_one_figure_gaussian, 3000, 17),
        (_uniform_three_figures, 3000, 41),
        (_whole_gaussian, 4000, 23),
    ],
)
def test_no_stratum_holds_more_cells_than_the_published_count(
    tmp_path: pathlib.Path, build, rows: int, data_seed: int
) -> None:
    """G5.2a's cap on the layout itself, where the defect was made."""
    _loaded, column = _described(tmp_path, build(random.Random(data_seed), rows))
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    layout, _notes, _content = generation._numeric_layout(column, facts, None)
    assert facts.mode is not None
    assert max(layout.sizes) <= facts.mode_count, (
        sorted(layout.sizes, reverse=True)[:5],
        facts.mode_count,
    )
    assert sum(layout.sizes) == column.n_numeric


def test_a_plateau_longer_than_the_count_gives_its_overflow_away(
    tmp_path: pathlib.Path,
) -> None:
    """The levelling step, on the whole-number shape that needs it.

    A five-point score's ladder is flat over each value, and interpolation
    rounds a plateau's edges onto it, so the run the ladder gives the
    commonest value can be longer than the cells the real column held
    there. Measured: 345 against a published 333.
    """
    draw = random.Random(3)
    cells = [str(draw.randint(1, 5)) for _ in range(1500)]
    _loaded, column = _described(tmp_path, cells)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    rungs = generation._merged_rungs(facts)
    assert rungs is not None
    held = generation._rank_values(
        0, column.n_numeric, rungs, column.n_numeric, True, 0
    )
    runs, _values = generation._runs_of(held)
    assert max(runs) > facts.mode_count, (max(runs), facts.mode_count)
    layout, _notes, _content = generation._numeric_layout(column, facts, None)
    assert max(layout.sizes) <= facts.mode_count


def test_the_levelling_keeps_the_total_and_moves_to_the_nearest() -> None:
    """`_levelled` by hand: nearest first, the lower one on a tie."""
    assert generation._levelled([1, 9, 1, 1], 4) == [4, 4, 3, 1]
    assert generation._levelled([2, 2, 8, 2, 2], 4) == [2, 4, 4, 4, 2]
    assert generation._levelled([5, 5], 4) == [5, 5]
    assert generation._levelled([3, 1, 7], 0) == [3, 1, 7]
    draw = random.Random(11)
    for _case in range(400):
        sizes = [draw.randint(1, 30) for _ in range(draw.randint(1, 40))]
        cap = draw.randint(1, 35)
        got = generation._levelled(sizes, cap)
        assert sum(got) == sum(sizes)
        assert len(got) == len(sizes)
        if sum(sizes) <= cap * len(sizes):
            assert max(got) <= cap
        else:
            assert got == sizes


def test_the_capped_heap_merge_is_the_repeated_scan() -> None:
    """`_merge_down` with a cap gives what `_merge_nearest` with it gives.

    The heap is the linear form of the scan, and equivalence is the whole
    of its contract (landing 1); the cap is a new first part of the key,
    so both have to carry it the same way.
    """
    draw = random.Random(29)
    for _case in range(600):
        count = draw.randint(2, 60)
        lengths = [draw.randint(1, 12) for _ in range(count)]
        held = sorted(
            draw.choice([float(draw.randint(0, 40)), draw.uniform(0, 40)])
            for _ in range(count)
        )
        strata = draw.randint(1, count)
        cap = draw.choice([0, draw.randint(1, 30)])
        want_lengths, want_values = list(lengths), list(held)
        while len(want_lengths) > strata:
            want_lengths, want_values = generation._merge_nearest(
                want_lengths, want_values, cap
            )
        got_lengths, got_values = generation._merge_down(
            lengths, held, strata, cap
        )
        assert got_lengths == want_lengths, (lengths, held, strata, cap)
        assert [repr(v) for v in got_values] == [repr(v) for v in want_values]


def test_a_join_that_stays_under_the_cap_is_taken_first() -> None:
    """The overshoot part decides before the smaller side does."""
    lengths, _values = generation._merge_nearest([5, 1, 1], [1.0, 1.1, 5.0])
    assert lengths == [6, 1]
    lengths, _values = generation._merge_nearest([5, 1, 1], [1.0, 1.1, 5.0], 5)
    assert lengths == [5, 2]


@pytest.mark.parametrize(
    "build,rows,data_seed",
    [
        (_skewed_two_figures, 4000, 23),
        (_one_figure_gaussian, 2000, 17),
        (_bounded_share, 4000, 23),
        (_whole_gaussian, 4000, 23),
    ],
)
def test_the_cap_read_off_the_ladder_is_true_of_the_real_column(
    tmp_path: pathlib.Path, build, rows: int, data_seed: int
) -> None:
    """The withheld-pair bound holds on columns whose true count is known.

    The ladder bound of G5.2a is what the cap falls back to where the pair
    is withheld, and it is a claim about the REAL column: no number of it
    was held by more cells. So it is measured against the column itself.
    """
    cells = build(random.Random(data_seed), rows)
    _loaded, column = _described(tmp_path, cells)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    rungs = generation._merged_rungs(facts)
    assert rungs is not None
    longest = 1
    run = 1
    for place in range(1, len(rungs)):
        run = run + 1 if rungs[place] == rungs[place - 1] else 1
        longest = max(longest, run)
    bound = ((longest + 1) * (column.n_numeric - 1)) // 100 + 2
    most = max(collections.Counter(float(cell) for cell in cells).values())
    assert most <= bound, (most, bound)
    assert validation._stratum_bound(facts) == facts.mode_count


def test_the_twin_report_can_say_outside(tmp_path: pathlib.Path) -> None:
    """The generator's own windows can fail, and on a faithful twin they agree.

    Built on the column that showed the defect: its windows were drawn from
    a 760-cell stratum and said inside for a twin holding one number 760
    times. A twin scaled by three per cent must now land outside at least
    one of them, and on the unscaled twin every window the generator calls
    inside is one the checker does not call MISSED.
    """
    loaded, column = _described(
        tmp_path, _skewed_two_figures(random.Random(23), 4000)
    )
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    plan = generation._plan_column(column, loaded.n_rows)
    for seed in (5, 17):
        twin = generation.generate(loaded, seed)
        written = list(twin.columns[0])
        own = generation._numeric_approximations(column, facts, plan, written)
        assert own and all(entry.inside for entry in own), [
            entry.fact for entry in own if not entry.inside
        ]
        target = fixtures.write(
            tmp_path, f"twin-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, str(target))
        missed = {check.fact for check in outcome.checks if check.verdict == validation.MISSED}
        assert missed == set(), missed
        scaled = [f"{float(cell) * 1.03:.2f}" for cell in written]
        moved = generation._numeric_approximations(column, facts, plan, scaled)
        assert any(not entry.inside for entry in moved), [
            (entry.fact, entry.lowest, entry.highest, entry.achieved)
            for entry in moved
        ]


def test_a_heavy_tail_window_is_no_longer_vacuous(tmp_path: pathlib.Path) -> None:
    """The spread window of a heavy-tailed column, and the verdict it gives.

    On the base commit a Pareto column of 4,000 two-figure charges drew its
    spread window from a 41-cell stratum as (0.0, 17423.04): no spread at
    all was ruled out. With the cap every stratum holds at most the
    published count of three, the window's low end is well above nought,
    and the twin report and the quality report give the SAME verdict on
    the mean and the spread.

    THE VERDICT IS A MISS, AND THAT IS A NAMED LIMIT RATHER THAN THIS
    LANDING'S TO REPAIR. The ladder is straight between `p99` and the
    published maximum, so the construction's own mean and spread lie far
    above the column's, and neither window covers the published value.
    Stage 3 replaces the exact extremes with the tail's shape; this test
    pins that both reports say so rather than one of them staying silent.
    """
    draw = random.Random(41)
    cells = ["%.2f" % (1000 * draw.paretovariate(1.5)) for _ in range(4000)]
    loaded, column = _described(tmp_path, cells)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    plan = generation._plan_column(column, loaded.n_rows)
    assert plan.layout is not None
    assert max(plan.layout.sizes) <= facts.mode_count
    for seed in (1, 2):
        twin = generation.generate(loaded, seed)
        own = {
            entry.fact: entry
            for entry in generation._numeric_approximations(
                column, facts, plan, list(twin.columns[0])
            )
        }
        assert float(own["std"].lowest) > 0.5 * facts.std
        assert math.isfinite(float(own["std"].highest))
        target = fixtures.write(
            tmp_path, f"tail-{seed}.csv", rendering.twin_csv(twin)
        )
        outcome = validation.measure(loaded, str(target))
        verdicts = {check.fact: check.verdict for check in outcome.checks}
        for fact, checked in (("mean", "numeric.mean"), ("std", "numeric.std")):
            assert (verdicts[checked] == validation.MISSED) == (
                not own[fact].inside
            ), (fact, verdicts[checked], own[fact])


def test_both_windows_widen_by_half_a_grid_unit_and_no_more() -> None:
    """G12.2's second widening, stated as a number in both modules."""
    assert generation._grid_half_unit(1) == 0.05
    assert generation._grid_half_unit(2) == 0.005
    assert generation._grid_half_unit(0) == 0.0
    assert generation._grid_half_unit(-1) == 0.0


def test_the_checker_reads_half_a_grid_unit_off_the_description(
    tmp_path: pathlib.Path,
) -> None:
    """The validator's half unit on a column of tenths is the generator's."""
    _loaded, column = _described(
        tmp_path, _one_figure_gaussian(random.Random(17), 600)
    )
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert validation._half_unit(facts) == generation._grid_half_unit(1)
    assert validation._one_grid(facts) == generation._pinned_fraction(column, facts)

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

from synthtwin import contract, generation, parsing, profile, reading, rendering, taxonomy
from synthtwin import validation
from tests import fixtures
from tests.test_stage2_round_trip import _round_trip

SEEDS = ("1", "7", "23")

# THE FLOOR THESE SHAPES ARE DESCRIBED AT, the shipped default (11 since
# plan P4-D316). Where a column's commonest number is held by fewer cells
# than it, the mode pair is withheld and the withheld pair proves no
# number was held by `FLOOR` cells, so G5.2a's cap is `FLOOR - 1`
# (`test_a_pair_the_floor_withheld_caps_every_number_under_the_floor`).
FLOOR = parsing.DEFAULT_SMALL_CELL_FLOOR


def _cap(mode: "float | None", mode_count: int) -> int:
    """The most cells one twin number may hold, from the published pair."""
    return mode_count if mode is not None else FLOOR - 1


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


def _dropped_zero(text: str) -> str:
    """A number as a spreadsheet writes it: `37.0` becomes `37`."""
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def _spreadsheet_narrow(draw: random.Random, rows: int) -> "list[str]":
    return [_dropped_zero(f"{draw.gauss(37, 0.5):.1f}") for _ in range(rows)]


def _spreadsheet_weights(draw: random.Random, rows: int) -> "list[str]":
    return [_dropped_zero(f"{draw.gauss(80, 16):.1f}") for _ in range(rows)]


def _spreadsheet_scores(draw: random.Random, rows: int) -> "list[str]":
    return [
        _dropped_zero(f"{min(10.0, max(0.0, draw.gauss(6, 2))):.1f}")
        for _ in range(rows)
    ]


def _halves_spreadsheet(draw: random.Random, rows: int) -> "list[str]":
    """Halves as a spreadsheet writes them: `37` beside `37.5`.

    One published fraction width, and the point-free cells are `plain`,
    so the column is on the written grid of G5.2a step 1 -- and its
    values are sparse enough on that grid that the profiler names empty
    stretches, which is what sends it through G6.7's pass.
    """
    return [
        _dropped_zero(f"{round(draw.gauss(37.5, 1.2) * 2) / 2:.1f}")
        for _ in range(rows)
    ]


def _zero_inflated(draw: random.Random, rows: int) -> "list[str]":
    return [
        "0" if draw.random() < 0.3 else f"{draw.lognormvariate(1, 0.6):.1f}"
        for _ in range(rows)
    ]


def _zero_inflated_two_figures(draw: random.Random, rows: int) -> "list[str]":
    return [
        "0" if draw.random() < 0.25 else f"{draw.lognormvariate(0, 0.5):.2f}"
        for _ in range(rows)
    ]


def _signed_change(draw: random.Random, rows: int) -> "list[str]":
    """Changes rounded to two places, each written with its sign: `+1.25`, `-0.00`."""
    return [f"{round(draw.gauss(0, 3), 2):+.2f}" for _ in range(rows)]


def _unsigned_change(draw: random.Random, rows: int) -> "list[str]":
    return [cell.lstrip("+") for cell in _signed_change(draw, rows)]


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
    # A SPREADSHEET'S DECIMALS AND A ZERO-INFLATED COLUMN (landing 2b.1,
    # repair): one fraction width beside cells written with no point at
    # all. At 53bb012 a 2,000-row column of weights written this way held
    # 238 cells at full binary precision and 51 leading zeros; a 4,000-row
    # column of temperatures held one number 601 times against 308.
    ("spreadsheet_narrow", _spreadsheet_narrow, 2000, 101),
    ("spreadsheet_narrow", _spreadsheet_narrow, 500, 101),
    ("spreadsheet_weights", _spreadsheet_weights, 4000, 101),
    ("spreadsheet_weights", _spreadsheet_weights, 500, 202),
    ("spreadsheet_scores", _spreadsheet_scores, 2000, 101),
    ("zero_inflated", _zero_inflated, 4000, 202),
    ("zero_inflated_two_figures", _zero_inflated_two_figures, 2000, 101),
    # A COLUMN OF CHANGES EITHER SIDE OF NOUGHT (integration repair). A
    # negative stratum whose grid value rounded to `0.00` took G5.5's
    # plain fallback `-1.0`: two strata became one number beside a third,
    # and six cells were written `-1.0` against a published width of two.
    ("signed_change", _signed_change, 2000, 2),
    ("signed_change", _signed_change, 4000, 2),
    ("unsigned_change", _unsigned_change, 2000, 2),
    ("unsigned_change", _unsigned_change, 4000, 2),
]


# ONE CASE COMES BACK TWO NUMBERS SHORT, AND IT IS CARRIED BY NAME (landing
# 2b.1, repair). On this spreadsheet column at seed 23 G5.3's grid value
# puts two strata on `37.9`, and G6.4's reach chain trades three strata a
# value inside their shares that no grid holds, `36.001675000000006` among
# them, which the writer then prints on a neighbour's number; G6.5 buys the
# spelling count back with one leading zero, `035.3`. The chain is
# a generator rule the oracle has never carried, so it is not changed here.
# The assertion below turns red the moment the count comes back.
#
# AND IT CAME BACK (the carried numbers repair pass of 2026-09-19). After
# the walks the 34 strata held 32 texts: `36.0` twice (a whole stratum and
# one holding 36.0017) and `37.9` twice. G6.5a's push takes each in turn:
# at `36.0` the mover not whole walks the points not whole upward to the
# free `36.3`, three strata; at `37.9` the free `38.0` is whole and the
# mover is not, so it walks the points not whole to the free `38.5`,
# five strata, the downward way being refused by the whole `37.0`. 32 + 2
# = 34, the published count, so nothing is carried.
CARRIED_SHORT: "dict[tuple[str, int, str], int]" = {}

# ONE CASE COMES BACK ONE NUMBER OVER, AND IT IS CARRIED BY NAME
# (integration repair). The 4,000-row column of changes writes nought as
# `-0.00` and as `0.00` or `+0.00`: two spellings of one number, so its
# count of spellings is one above its count of numbers, and the layout of
# G5.2 sizes the strata by the spellings. Before the repair of G5.5 on a
# grid the extra stratum was hidden by two strata repaired onto `-1.0`,
# which spent a number and missed the published width; now every stratum
# is its own number and the count comes back one over, which the quality
# report's window holds. The assertion turns red the moment it changes.
CARRIED_EXTRA = {("signed_change", 4000): 1, ("unsigned_change", 4000): 1}


def test_the_generator_and_the_oracle_join_the_same_pair(
    tmp_path: pathlib.Path,
) -> None:
    """G5.2a step 3's key is one arithmetic, and both writings take it.

    The integration verdict: the method fixes binary64 and divides before
    it subtracts, for the overflow reason G5.3 gives; the oracle took the
    gap as an exact rational instead. On 501 one-decimal cells over eleven
    values the two chose different pairs -- [56, 40, 4, 17, 50, ...] in the
    oracle against [56, 40, 4, 18, 49, ...] in the generator, which is what
    the twin holds.
    """
    oracle = _oracle()
    values = [0.9, 3.4, 4.0, 5.9, 6.8, 7.7, 9.6, 9.8, 10.6, 11.6, 12.5]
    counts = [60, 38, 18, 3, 50, 66, 63, 45, 27, 66, 65]
    cells = [f"{value:.1f}" for value, count in zip(values, counts) for _ in range(count)]
    first, _second, _written, _twin, _real = _round_trip(
        tmp_path / "join", cells, seed="1"
    )
    # The hundred and one rungs stand in two blocks: the eleven named
    # ones and the ninety between them -- and on a TAIL BLOCK the rungs
    # outside the two boundary percents are withheld and read through
    # the tails instead (contract 6.7a, method G5.1a). The oracle reads
    # its own, so the ladder both merges below are taken over is the
    # oracle's, exactly as the rest of this comparison is.
    rungs_of = {**first["percentiles"], **first["percentiles_between"]}
    block = dict(first)
    block["_rungs"] = rungs_of
    ladder = list(oracle.tail_ladder(block))
    total = len(cells)
    strata = first["n_distinct_values"]
    cap = first["mode_count"]
    lengths, heights = oracle.ladder_runs(ladder, 0, total, total, False, 1)

    def merged(key_of: object) -> "list[int]":
        sizes, held = list(lengths), list(heights)
        while len(sizes) > strata:
            at = min(
                range(len(sizes) - 1),
                key=lambda index: key_of(sizes, held, index),  # type: ignore[operator]
            )
            sizes[at] += sizes[at + 1]
            del sizes[at + 1]
            del held[at + 1]
        return oracle.levelled(sizes, cap)

    theirs = merged(
        lambda sizes, held, index: (oracle.overshoot(sizes, index, cap),)
        + oracle.join_key(sizes, held, index)
    )
    ours = merged(
        lambda sizes, held, index: generation._pair_key(
            sizes, [float(value) for value in held], index, index + 1, cap
        )
    )
    assert theirs == ours, (theirs, ours)


def _oracle() -> object:
    """The reference oracle, imported the way the reference test does."""
    import importlib.util

    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference"
    spec = importlib.util.spec_from_file_location(
        "make_generation_reference_vectors",
        where / "make_generation_reference_vectors.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _number(cell: str) -> "float | None":
    found = re.fullmatch(r"([-+]?\d+(?:\.\d+)?)( kg)?", cell)
    return float(found.group(1)) if found else None


def _figures(cell: str) -> int:
    found = re.fullmatch(r"[-+]?\d+(?:\.(\d+))?( kg)?", cell)
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
        short = CARRIED_SHORT.get((name, rows, seed), 0)
        assert (twin_exit == 0) == (short == 0), (name, rows, seed, twin_exit)
        assert real_exit == 0, (name, rows, seed, "the real table missed")
        # THE MODE PAIR IS PUBLISHED WHERE THE COMMONEST NUMBER REACHES
        # THE FLOOR, and withheld whole below it.
        if real_most >= FLOOR:
            assert first["mode_count"] == real_most
        else:
            assert first["mode"] is None and first["mode_count"] == 0
        held = collections.Counter(_number(cell) for cell in written)
        assert None not in held, (name, seed, "a cell that is not a number")
        # NO NUMBER OF THE TWIN HELD BY MORE CELLS THAN ANY REAL NUMBER
        # -- the published count, or under the floor where it is withheld.
        cap = _cap(first["mode"], first["mode_count"])
        assert max(held.values()) <= cap, (
            name,
            rows,
            seed,
            max(held.values()),
            cap,
        )
        if first["mode"] is None:
            assert second["mode"] is None, (name, rows, seed)
        else:
            assert second["mode_count"] <= first["mode_count"]
        # THE COUNT OF DIFFERENT NUMBERS AND THE FRACTION WIDTHS, EXACTLY.
        extra = CARRIED_EXTRA.get((name, rows), 0)
        assert second["n_distinct_values"] == first["n_distinct_values"] - short + extra, (
            name,
            rows,
            seed,
            second["n_distinct_values"],
            first["n_distinct_values"],
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
        # A cell written with no point carries no figure after it, and a
        # column publishing a point-free style count wrote such cells.
        if not widths or first["numeric_styles"].get("plain", 0) > 0:
            widths = widths | {0}
        outside = [cell for cell in written if _figures(cell) not in widths]
        assert outside == [], (name, rows, seed, outside[:5])
        if not real_leading:
            leading = [cell for cell in written if re.match(r"-?0\d", cell)]
            # The carried case buys back the spelling count its lost numbers
            # cost with G6.5's leading zeros, at most one per lost number.
            assert len(leading) <= short, (name, rows, seed, leading[:5])


@pytest.mark.parametrize(
    "name,build,rows,data_seed",
    [
        ("uniform_three_figures", _uniform_three_figures, 2500, 404),
        ("whole_hundreds", _whole_hundreds, 1000, 404),
    ],
)
def test_a_pair_the_floor_withheld_caps_every_number_under_the_floor(
    tmp_path: pathlib.Path, name: str, build, rows: int, data_seed: int
) -> None:
    """A withheld mode pair proves no number was held by `floor` cells.

    Described under `--smallest-group 11`, a column whose commonest number
    is held by ten cells or fewer publishes no mode pair, and G5.2a's cap
    is then `floor - 1`. Measured before this: 2,500 thousandths held one
    number 27 times in the twin, 1,000 incomes in hundreds 21 times, and a
    twin
    described again at the same floor published a mode pair the real column
    had withheld.
    """
    cells = build(random.Random(data_seed), rows)
    real_most = max(collections.Counter(float(cell) for cell in cells).values())
    assert real_most < 11, real_most
    flags = ("--smallest-group", "11")
    for seed in SEEDS:
        first, second, written, twin_exit, real_exit = _round_trip(
            tmp_path / seed, cells, flags, check_real=seed == SEEDS[0], seed=seed
        )
        assert first["mode"] is None and first["mode_count"] == 0, name
        held = collections.Counter(float(cell) for cell in written)
        assert max(held.values()) <= 10, (name, seed, max(held.values()))
        assert second["mode"] is None, (name, seed, second["mode_count"])
        assert second["n_distinct_values"] == first["n_distinct_values"]
        assert twin_exit == 0, (name, seed)
        assert real_exit == 0, (name, seed)


def test_a_withheld_style_pool_is_not_a_written_grid(
    tmp_path: pathlib.Path,
) -> None:
    """An anonymous style pool proves no point-free cell (Codex 2b.1, item 4).

    490 cells written at one decimal place beside ten `-1e-2` cells. The
    census names the width `1` for 490 of them and the styles map names
    `decimal` 490 and pools the other ten under `(withheld)`, because ten
    is under the floor of eleven.

    Counting that pool as point-free demand made 490 + 10 the whole numeric
    count, so the column was read as being written on the grid of tenths --
    and `-0.01` is not a tenth. A pooled count says how many cells it
    covered and never which form they took, so it cannot prove its cells
    carry no point. Measured at seeds 1, 7 and 23: the twin held 28
    different numbers against a published 31, and reads 30 with the grid
    inferred from the NAMED counts alone.

    The real table misses here whichever way the grid reads -- its lone
    exponent style is pooled below the floor -- so the twin is what this
    gate checks, and that shortfall is named rather than asserted away.

    AND ONE MORE CELL WRITTEN `-1E-2` (plan P4-D221; stage 2 closed by the
    owner rulings of 2026-09-17). A pool of ten below the disclosure line
    now takes in the named `decimal` count, which leaves no named count to
    read a grid from; ten lower-case and one upper-case exponent are two
    forms each held by fewer than eleven cells, a pool of eleven that
    stands beside the named 490. SINCE PLAN P4-D222 the eleven are
    counted into the decimals and no pool is left to prove anything; the
    width census is one pool instead, because the published minimum,
    `-0.01`, needs two figures after the point and no width it names holds
    them, so no grid is read either way.
    """
    draw = random.Random(17)
    cells = (
        [f"{draw.gauss(37, 0.5):.1f}" for _each in range(490)]
        + ["-1e-2"] * 10
        + ["-1E-2"]
    )
    for seed in SEEDS:
        first, _second, written, _twin_exit, _real_exit = _round_trip(
            tmp_path / f"pool-{seed}",
            cells,
            ("--smallest-group", "11"),
            check_real=False,
            seed=seed,
        )
        assert first["fraction_widths"] == {"(withheld)": 501}, first["fraction_widths"]
        assert first["numeric_styles"] == {"decimal": 501}, first["numeric_styles"]
        held = {float(cell) for cell in written}
        assert len(held) >= 30, (seed, len(held), first["n_distinct_values"])
    (tmp_path / "grid").mkdir()
    _loaded, column = _described(tmp_path / "grid", cells)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert generation._written_grid(column, facts) == -1


def _missed_facts(folder: pathlib.Path) -> "list[str]":
    """Every obligation the twin's quality report names as missed."""
    found: "list[str]" = []
    for page in sorted((folder / "check-twin").glob("*.txt")):
        for line in page.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if ": MISSED" not in stripped or "[" not in stripped:
                continue
            fact = stripped.split("[")[1].split("]")[0]
            if fact not in found:
                found += [fact]
    return sorted(found)


@pytest.mark.parametrize("rows,every_fact", [(400, False), (4000, True)])
def test_a_value_moved_off_an_empty_stretch_keeps_the_written_grid(
    tmp_path: pathlib.Path, rows: int, every_fact: bool
) -> None:
    """G6.7.4 clause 8 (landing 2b.7), through the whole product.

    G6.7 moves a stratum out of a stretch the description says holds
    nothing, walking outward from the stretch's published edge in
    SIXTY-FOURTHS OF A BIN. A bin is not a grid. On a whole-valued
    column the walk already rounds each candidate to a whole number,
    the integers being that column's grid; on a column written at one
    fixed width there was no such step, so the stratum took a value
    between two grid points and G6.6 wrote that cell at the width its
    own value needed rather than at a published one.

    MEASURED before the repair, at both floors and all three seeds:
    one cell of each twin came out `38.55126953125` at 400 rows and
    `39.05078125` at 4,000, the twin wrote 207 cells at the one
    published width against 208 and 2,000 against 2,001, and
    `widths.published.1` MISSED on all twelve runs.

    THE TWO SIZES ASSERT DIFFERENT THINGS, and that is deliberate
    rather than a weakened gate. At 4,000 rows the repair closed the
    column outright, so every published fact was asserted and both
    files validated at exit 0. At 400 rows it closes the WIDTH and the
    column still comes back holding 14 of its published 15 different
    numbers -- a shortfall of the separation walk, not of this rule --
    so what is pinned there is the fact this rule owns: no cell is
    written outside the published census. Asserting exit 0 at 400 rows
    would be asserting somebody else's defect away.

    AND THE 4,000-ROW TWIN MISSES ONE OBLIGATION SINCE LANDING 3.3,
    which is named here rather than asserted away. Its low tail lists
    three values -- 33.5, 34.0 and 34.5 -- and the counts G5.3e solves
    for them (1, 33 and 6) are not the sizes the layout divides that
    band into (1, 26 and 33), so two strata begin inside the run of 33,
    the rule that no two strata share a number pushes one of them off,
    and the twin writes 34.2 where the tail names 34.5:
    `tails.low.values` MISSED. Both other sizes and the real table are
    unaffected. Giving the second stratum the next listed value instead
    was measured and moved nothing: the collision is resolved later, by
    the separation walk, and lands in the same place.

    AND ONE SEED COSTS ONE NUMBER BESIDES, for the repair that keeps a
    run reaching ACROSS a tail's edge whole (method G5.3e): that run is
    one stratum where the walk could have divided it, so at seed 1 this
    twin holds 16 of the 17 different numbers its description publishes
    and `n_distinct_values` MISSES with the two tails. Seeds 7 and 23
    hold all 17. The repair is worth that: without it a run the ladder
    reads across the edge is joined to its neighbours and the tail's own
    value is written nowhere at all -- KPI K-P4-11's ClinVar column, one
    of eighteen coding systems, stopped validating clean.

    What is pinned is therefore the exact shape of the cost, seed by
    seed, and nothing else of the seventy-three obligations this twin is
    measured against moves.
    """
    cells = _halves_spreadsheet(random.Random(101 + rows), rows)
    for seed in SEEDS:
        first, second, written, twin_exit, real_exit = _round_trip(
            tmp_path / f"{rows}-{seed}", cells, check_real=True, seed=seed
        )
        # NO CELL OUTSIDE THE PUBLISHED CENSUS. A point-free cell
        # carries no figure after the point, and this column writes
        # those, so nought is a width it may wear.
        widths = {int(width) for width in first["fraction_widths"]} | {0}
        outside = [cell for cell in written if _figures(cell) not in widths]
        assert outside == [], (rows, seed, outside[:4])
        # ...and the real table still meets its own description.
        assert real_exit == 0, (rows, seed, "the real table missed")
        if every_fact:
            missed = _missed_facts(tmp_path / f"{rows}-{seed}")
            assert set(missed) == {
                "1": {
                    "numeric.n_distinct_values",
                    "numeric.tails.high.values",
                    "numeric.tails.low.values",
                },
                "7": {"numeric.tails.low.values"},
                "23": {"numeric.tails.low.values"},
            }[seed], (rows, seed, missed)
            assert second["fraction_widths"] == first["fraction_widths"], (
                rows,
                seed,
            )
            assert second["n_distinct_values"] == first[
                "n_distinct_values"
            ] - (1 if seed == "1" else 0), (rows, seed)


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
    layout, _notes, _content = generation._numeric_layout(
        column, facts, None, _loaded.settings.small_cell_floor
    )
    # The published count, or under the floor where the pair is withheld
    # (the three-figure column's commonest number is held by fewer than
    # the default floor of 11 cells).
    assert max(layout.sizes) <= _cap(facts.mode, facts.mode_count), (
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
    layout, _notes, _content = generation._numeric_layout(
        column, facts, None, _loaded.settings.small_cell_floor
    )
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
    assert (
        validation._stratum_bound(facts, _loaded.settings.small_cell_floor)
        == facts.mode_count
    )


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
    plan = generation._plan_column(
        column, loaded.n_rows, loaded.settings.small_cell_floor
    )
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

    THE VERDICT WAS A MISS AND IS NOT ONE SINCE LANDING 3.3. The ladder
    was straight between `p99` and the published maximum, so the
    construction's own mean and spread lay far above the column's and
    neither window covered the published value. The tail rule withholds
    that maximum and states the rows beyond `p99` as a group, and the
    twin now holds a spread of 13512.15 against a published 13536.83 --
    two tenths of a per cent -- and misses nothing.

    AND THE WINDOW IS VACUOUS AGAIN, WHICH IS THIS LANDING'S OWN COST
    AND IS PINNED HERE AS ONE. G12.2 reads the widest stratum a
    description allows off the ladder's longest run of equal rungs, and
    a tail's staircase repeats a value wherever the grid runs out of
    points for its rows -- so the run is longer, the bound is wider,
    and the spread window reaches from nought to 36562.38 on this
    column where the cap had lifted its low end above nought. The check
    is weaker; the twin it is checking is far better. What this test
    still holds is the half that can fail: the window's high end is a
    number, the low end is not above the published spread, and the twin
    report and the quality report give the SAME verdict on both
    moments.
    """
    draw = random.Random(41)
    cells = ["%.2f" % (1000 * draw.paretovariate(1.5)) for _ in range(4000)]
    loaded, column = _described(tmp_path, cells)
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    plan = generation._plan_column(
        column, loaded.n_rows, loaded.settings.small_cell_floor
    )
    assert plan.layout is not None
    # The published count of three at a floor of one; under the default
    # floor of 11 the pair is withheld and the cap is ten (plan P4-D316).
    assert max(plan.layout.sizes) <= _cap(facts.mode, facts.mode_count)
    for seed in (1, 2):
        twin = generation.generate(loaded, seed)
        own = {
            entry.fact: entry
            for entry in generation._numeric_approximations(
                column, facts, plan, list(twin.columns[0])
            )
        }
        assert float(own["std"].lowest) <= facts.std
        assert math.isfinite(float(own["std"].highest))
        # ...and the twin's own spread, which is what the window is
        # drawn around: within a per cent of the published one.
        written = [
            float(cell) for cell in twin.columns[0] if cell != ""
        ]
        spread = taxonomy.spread_of(written)
        assert spread is not None
        assert abs(spread / facts.std - 1) <= 0.01, spread
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

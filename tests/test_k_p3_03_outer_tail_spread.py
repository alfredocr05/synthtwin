"""K-P3-03: a numeric twin's spread is too wide, and why, held both ways.

THE DEFECT. Method G5.3 reads the hundred-and-one-rung ladder as a
straight line between each pair of neighbours, INCLUDING the two outer
segments: from `p01` down to the exact published minimum and from `p99`
up to the exact published maximum. The real column reaches those
extremes only with its last few cells, so the straight line spreads the
outer one per cent at each end too far out, and every bell-shaped
numeric twin measured comes out with a standard deviation 1.4 to 3.7
per cent wider than the published one, at 5,000 rows and above,
whatever the quality report says (a triangular or clipped column 0.2
to 0.8 per cent, a uniform one none). Twenty `gauss(50, 10)` columns
at 20,000 rows miss `moments.std` on 19 and exit 3; at 5,000 rows, and
on coarsely
rounded columns at any size, the same excess is reported as held,
because the window is wide there. Measured, shape by shape, by
`tools/measurements/k_p3_03_spread.py`.

WHOSE IT IS. It is a within-column method defect of stage 2, in G5.3,
and NOT the heavy-tail mean and spread the owner deferred to stage 3:
these columns are light-tailed. It can be mended from published facts
alone -- one power per column bending the two outer segments, solved
from the published spread, keeps every published rung and meets the
spread exactly (the second test below) -- but the G12.3 window is drawn
from the SAME straight reading (the third test), so mending G5.3 alone
would turn a faithful twin into a miss on 20 columns of 20. Any repair
is G5.3 and G12.3 together, and it moves the bytes of every numeric
twin. The orchestrator deferred it to stage 3 on 2026-09-18, under the
owner's principle of 2026-09-17 ("build after the machinery of stage
3"); the owner may reverse that (the plan's owner decisions of
2026-09-18, and the ledger's K-P3-03).

WHAT IS PINNED, so that a correct repair stays green and a worse twin
turns red: the twin's spread against the published one, on BOTH sides;
the fact that the straight reading of the published rungs is what is
too wide; the fact that the published facts fix a bend that meets the
spread; and the coupling of the window to the generator's own reading.
No verdict count is pinned: it moves with G12.3.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import math
import pathlib
import random

from synthtwin import contract, generation, profile, reading, rendering
from synthtwin import taxonomy, validation
from tests import fixtures

# THE WIDEST A TWIN'S SPREAD STANDS FROM THE PUBLISHED ONE, either way,
# in per cent, each the measured largest on e53d5f4 rounded up to the
# next tenth: 2.154 on the four normal columns at 5,000 rows, 3.055 on
# the two at 20,000 rows, 3.207 on the one-figure lab column at 5,000
# rows. A repair brings the measured value toward nought and leaves
# these green; a twin pushed further out or pulled further in turns
# them red.
WIDEST_NORMAL = 2.2
WIDEST_LARGE = 3.1
WIDEST_ROUNDED = 3.3
# The largest power the bend is looked for below. Measured on the four
# normal columns at 5,000 rows it is 2.8 to 5.8.
STEEPEST = 16.0


def _table(shape: str, rows: int, columns: int) -> "list[list[str]]":
    """The ledger's construction: row after row, one draw per cell."""
    if shape == "normal":
        draw = random.Random(7)
        return [
            [f"{draw.gauss(50, 10):.2f}" for _ in range(columns)]
            for _ in range(rows)
        ]
    if shape == "rounded":
        # A lab value written to one figure, the skeptic's potassium.
        draw = random.Random(11)
        return [
            [f"{draw.gauss(4.2, 0.5):.1f}" for _ in range(columns)]
            for _ in range(rows)
        ]
    draw = random.Random(7)
    return [
        [f"{draw.uniform(20, 80):.2f}" for _ in range(columns)]
        for _ in range(rows)
    ]


def _described(
    folder: pathlib.Path, cells: "list[list[str]]"
) -> contract.Profile:
    names = [f"c{index}" for index in range(len(cells[0]))]
    path = fixtures.write(folder, "real.csv", fixtures.rows_to_csv(names, cells))
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), []
    )
    return contract.load_profile(
        str(fixtures.write_profile(folder, "real-profile.json", document))
    )


def _column_numbers(cells: "list[list[str]]", index: int) -> "list[float]":
    return [float(row[index]) for row in cells]


def _facts(column: contract.ColumnBlock) -> contract.NumericFacts:
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    assert facts.std is not None
    assert facts.mean is not None
    return facts


def _ladder(
    rungs: "tuple[float, ...]",
    bend: float = 1.0,
    real: "list[float] | None" = None,
) -> "tuple[float, float]":
    """The exact mean and spread of the ladder read segment by segment.

    Worked out in closed form from the published rungs alone, with no
    draw and without calling the generator, so it states what the
    PUBLISHED facts imply and a repair of the generator leaves it where
    it is. Each segment carries one hundredth of the cells.

    With ``bend`` 1 every segment is G5.3's straight line. Above 1 the
    two outer segments are bent toward `p01` and `p99`: a share ``s``
    of the lower one reads ``p01 - (p01 - min) (1 - s) ** bend``, so it
    still starts at the published minimum and ends at `p01` -- every
    published rung is kept -- and its first two moments are
    ``p01 - d / (bend + 1)`` and
    ``p01**2 - 2 p01 d / (bend + 1) + d**2 / (2 bend + 1)``; the upper
    one is its mirror. With ``real`` given (sorted), the two outer
    segments carry the real cells' own moments instead.
    """
    segments = len(rungs) - 1
    first = 0.0
    second = 0.0
    for step in range(segments):
        low, high = rungs[step], rungs[step + 1]
        outer = step in (0, segments - 1)
        if real is not None and outer:
            inside = len(real) // segments
            part = real[:inside] if step == 0 else real[len(real) - inside :]
            one = math.fsum(part) / len(part)
            two = math.fsum([value * value for value in part]) / len(part)
        elif outer:
            # Both outer segments measured from their INNER rung.
            anchor = high if step == 0 else low
            reach = (low - high) if step == 0 else (high - low)
            one = anchor + reach / (bend + 1)
            two = (
                anchor * anchor
                + 2 * anchor * reach / (bend + 1)
                + reach * reach / (2 * bend + 1)
            )
        else:
            one = (low + high) / 2
            two = (low * low + low * high + high * high) / 3
        first += one / segments
        second += two / segments
    return first, math.sqrt(max(0.0, second - first * first))


def _bend_meeting(rungs: "tuple[float, ...]", published: float) -> float:
    """The power whose bent ladder has exactly the published spread.

    The spread falls as the power rises, so halving the interval finds
    it; the two ends are checked first, so a column no bend can meet
    fails here and not somewhere quieter.
    """
    low, high = 1.0, STEEPEST
    assert _ladder(rungs, low)[1] > published
    assert _ladder(rungs, high)[1] < published
    for _ in range(60):
        middle = (low + high) / 2
        if _ladder(rungs, middle)[1] > published:
            low = middle
        else:
            high = middle
    return high


def _wider(published: float, numbers: "list[float]") -> float:
    spread = taxonomy.spread_of(numbers)
    assert spread is not None
    return 100 * (spread / published - 1)


def test_a_normal_twin_at_five_thousand_rows_stands_within_its_band(
    tmp_path: pathlib.Path,
) -> None:
    """Four `gauss(50, 10)` columns at 5,000 rows, held on both sides.

    The twin AND the real table meet every obligation. On every column
    the twin's spread stands within WIDEST_NORMAL per cent of the
    published one either way. And the diagnosis, from published facts:
    the straight reading of the published rungs is wider than the
    column, the twin is no wider than that reading, and putting the real
    cells back into ONLY the two outer segments brings the reading
    within a quarter of a per cent, so they make nine tenths of the
    excess at least.
    """
    cells = _table("normal", 5000, 4)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    # The spread first, so a twin pulled in or pushed out is named as
    # that before any verdict it also moves.
    for index, column in enumerate(loaded.columns):
        facts = _facts(column)
        assert facts.std is not None
        written = [float(cell) for cell in twin.columns[index]]
        wider = _wider(facts.std, written)
        assert -WIDEST_NORMAL <= wider <= WIDEST_NORMAL, (column.name, wider)
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))
    for measured in (target, tmp_path / "real.csv"):
        outcome = validation.measure(loaded, str(measured))
        assert not [
            (check.column, check.subcheck)
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ], measured.name
    for index, column in enumerate(loaded.columns):
        facts = _facts(column)
        assert facts.std is not None
        written = [float(cell) for cell in twin.columns[index]]
        rungs = generation._merged_rungs(facts)
        assert rungs is not None
        real = sorted(_column_numbers(cells, index))
        straight = _ladder(rungs)[1]
        mended = _ladder(rungs, 1.0, real)[1]
        spread = taxonomy.spread_of(written)
        assert spread is not None
        assert spread <= straight + 0.001 * facts.std, column.name
        assert abs(mended / facts.std - 1) <= 0.0025, column.name
        assert straight - facts.std > 0.0, column.name
        assert (straight - mended) >= 0.9 * (straight - facts.std), column.name


def test_the_published_facts_fix_a_bend_that_meets_the_published_spread(
    tmp_path: pathlib.Path,
) -> None:
    """The repair needs nothing the description does not publish.

    On each of the four normal columns at 5,000 rows, from the loaded
    description ALONE: the straight reading is more than one per cent
    too wide; one power, found from the published spread, bends the two
    outer segments so the reading's spread is the published one to a
    millionth, keeping the published minimum, `p01`, `p99` and maximum
    as the segments' ends, and leaving the mean nearer the published
    one than the straight reading does. So G5.3's straight outer tail is
    a choice the published facts can correct, not a shape they fail to
    publish.
    """
    cells = _table("normal", 5000, 4)
    loaded = _described(tmp_path, cells)
    for column in loaded.columns:
        facts = _facts(column)
        assert facts.std is not None and facts.mean is not None
        rungs = generation._merged_rungs(facts)
        assert rungs is not None
        named = facts.percentiles.rungs
        # The ends are the published minimum, `p01`, `p99` and maximum.
        assert (rungs[0], rungs[1], rungs[99], rungs[100]) == (
            named[0],
            named[1],
            named[-2],
            named[-1],
        ), column.name
        assert _ladder(rungs)[1] > 1.01 * facts.std, column.name
        bend = _bend_meeting(rungs, facts.std)
        mean, spread = _ladder(rungs, bend)
        assert 1.0 < bend < STEEPEST, column.name
        assert abs(spread / facts.std - 1) <= 1e-6, (column.name, bend)
        # The bend brings the mean NEARER the published one than the
        # straight reading stands (measured 0.0007-0.0028 of a spread
        # off straight, 0.0003-0.0011 bent), never further from it.
        straight = abs(_ladder(rungs)[0] - facts.mean)
        assert abs(mean - facts.mean) <= straight, (column.name, bend)
        assert abs(mean - facts.mean) <= 0.002 * facts.std, (column.name, bend)


def test_the_std_window_is_drawn_from_the_reading_the_generator_uses(
    tmp_path: pathlib.Path,
) -> None:
    """G12.3's window moves with G5.3, so a repair must move both.

    Two `gauss(50, 10)` columns at 20,000 rows. The spread of the ladder
    the GENERATOR reads -- G5.3 at every rank, through
    `generation._interpolated` -- is the midpoint of the `moments.std`
    window the validator draws, on every column, and the twin's lies
    inside it. Today that window excludes the published spread on both
    columns (its low end is 0.14 and 0.74 per cent above it), so a
    repair of G5.3 alone, which brings the reading to the published
    spread, leaves the window behind and turns this test red; so does a
    repair of G12.3 alone, which moves the window and not the reading.
    The repair's scope is G5.3 AND G12.3, and a repair of both keeps
    this green. The twin's own spread is held here too, within
    WIDEST_LARGE per cent of the published one either way.
    """
    cells = _table("normal", 20000, 2)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    floor = loaded.settings.small_cell_floor
    for index, column in enumerate(loaded.columns):
        facts = _facts(column)
        rungs = generation._merged_rungs(facts)
        assert rungs is not None
        numbers = facts.n_used_in_statistics
        read = [
            generation._interpolated(rungs, rank, numbers - 1)
            for rank in range(numbers)
        ]
        spread = taxonomy.spread_of(read)
        found = taxonomy.spread_of([float(cell) for cell in twin.columns[index]])
        assert spread is not None and found is not None
        low, high = validation._windows_of(column, facts, floor)["std"]
        # The window is CENTRED on the generator's reading: measured, its
        # midpoint and that spread agree to the sixth figure and beyond.
        assert abs((low + high) / 2 - spread) <= 1e-6 * (high - low), (
            column.name,
            low,
            spread,
            high,
        )
        assert low <= spread <= high, (column.name, low, spread, high)
        assert low <= found <= high, (column.name, low, found, high)
        wider = 100 * (found / facts.std - 1)
        assert -WIDEST_LARGE <= wider <= WIDEST_LARGE, (column.name, wider)


def test_a_one_figure_lab_column_is_held_as_spread_not_as_verdict(
    tmp_path: pathlib.Path,
) -> None:
    """The excess the report does not see, on a coarsely rounded column.

    A `gauss(4.2, 0.5)` column written to one figure at 5,000 rows: the
    half unit G12.2 grants makes its `moments.std` window reach from
    below nought to about double the spread, so twin and real both meet
    every obligation whatever the spread. Its spread is therefore held
    directly, within WIDEST_ROUNDED per cent of the published one
    either way.
    """
    cells = _table("rounded", 5000, 1)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    facts = _facts(loaded.columns[0])
    assert facts.std is not None
    wider = _wider(facts.std, [float(cell) for cell in twin.columns[0]])
    assert -WIDEST_ROUNDED <= wider <= WIDEST_ROUNDED, wider
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))
    for measured in (target, tmp_path / "real.csv"):
        outcome = validation.measure(loaded, str(measured))
        assert not [
            (check.column, check.subcheck)
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ], measured.name


def test_a_uniform_column_at_twenty_thousand_rows_misses_no_moment(
    tmp_path: pathlib.Path,
) -> None:
    """The control: the excess is the tail's shape, not the row count.

    A uniform column's outer one per cent IS spread evenly between `p01`
    and its minimum, so the straight segment is right there, and at
    20,000 rows nothing is missed. The quality report re-describes the
    file and hands `validation._moment_checks` its four moments; this
    hands it the four `taxonomy.moments_of` works out, and first proves
    on the real table that they are the published ones to the bit.
    """
    cells = _table("uniform", 20000, 2)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    for index, column in enumerate(loaded.columns):
        facts = _facts(column)
        assert taxonomy.moments_of(_column_numbers(cells, index)) == (
            facts.mean,
            facts.std,
            facts.skew,
            facts.kurtosis,
        ), column.name
        numbers = [float(cell) for cell in twin.columns[index]]
        mean, spread, skew, kurtosis = taxonomy.moments_of(numbers)
        block: "dict[str, object]" = {
            "mean": mean,
            "std": spread,
            "skew": skew,
            "kurtosis": kurtosis,
        }
        assert not [
            check.subcheck
            for check in validation._moment_checks(
                column, facts, block, loaded.settings.small_cell_floor
            )
            if check.verdict == validation.MISSED
        ], column.name

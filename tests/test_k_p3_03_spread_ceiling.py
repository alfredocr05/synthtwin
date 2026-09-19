"""K-P3-03: the spread a large numeric twin misses, held where it stands.

THE MISS. Twenty columns of `gauss(50, 10)` at two figures, 20,000 rows:
the twin's standard deviation is 2 to 3.5 per cent wider than the
published one on every column, the quality report calls `moments.std`
MISSED on 19 of the 20 and `synthtwin validate` exits 3. At 5,000 rows
it misses nothing.

WHAT MAKES IT, measured (`tools/measurements/k_p3_03_spread.py`). The
twin is faithful to its own construction: its spread is the spread of
the hundred-and-one-rung ladder read as method G5.3 reads it, to within
a few hundredths of a per cent, so the strata, their sizes and the draw
inside each add nothing. The ladder's spread is what is too wide, and
it is made by its two OUTER segments: G5.3 draws a straight line from
`p01` down to the published minimum and from `p99` up to the published
maximum, so the outer one per cent at each end is spread evenly over a
stretch the real column only reaches with its last few cells. Replace
those two segments' moments with the real cells' own and the excess
falls from 3 per cent to about a tenth of one. It GROWS with the rows,
because the extremes of a larger column lie farther out, while the
window narrows; the window's low end passes the published value near
20,000 rows and V6.1-A2 then holds the twin to half the window's width.
A uniform column, whose outer one per cent really is spread evenly,
misses nothing at any size; a skewed one misses its mean as well.

WHO OWNS IT. That is the exact extremes and the straight tail beside
them, which stage 3 replaces with a published shape for the tail -- the
heavy-tail mean and spread the owner deferred to it. Building it here
would be building stage 3, so this file pins the miss instead: it may
not get worse, and the day stage 3 lands the ceiling below comes down
to its target of nought.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import math
import pathlib
import random

from synthtwin import contract, generation, profile, reading, rendering
from synthtwin import taxonomy, validation
from tests import fixtures

# THE LEDGER'S COUNT on e53d5f4, which this file may not see exceeded.
# The target is nought, and stage 3 is what reaches it.
CEILING = 19
# The widest a twin's spread stood from the published one on that table,
# in per cent, rounded up to the next tenth.
WIDEST = 3.5


def _table(shape: str, rows: int, columns: int) -> "list[list[str]]":
    """The ledger's construction: row after row, one draw per cell."""
    draw = random.Random(7)
    if shape == "normal":
        return [
            [f"{draw.gauss(50, 10):.2f}" for _ in range(columns)]
            for _ in range(rows)
        ]
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


def _moment_checks(
    loaded: contract.Profile, columns: "list[list[float]]"
) -> "list[validation.Check]":
    """The quality report's four moment verdicts on every column.

    The report re-describes the file and hands each column's published
    moments to `validation._moment_checks`; this hands it the same four,
    worked out by `taxonomy.moments_of`, the one implementation the
    profiler publishes them with. The first test below proves the two
    agree on the real table before it trusts them on the twin.
    """
    found: "list[validation.Check]" = []
    for column, numbers in zip(loaded.columns, columns):
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts)
        mean, spread, skew, kurtosis = taxonomy.moments_of(numbers)
        block: "dict[str, object]" = {
            "mean": mean,
            "std": spread,
            "skew": skew,
            "kurtosis": kurtosis,
        }
        found += validation._moment_checks(
            column, facts, block, loaded.settings.small_cell_floor
        )
    return found


def _ladder_spread(
    rungs: "tuple[float, ...]", real: "list[float] | None" = None
) -> float:
    """The exact spread of G5.3's straight-line ladder, with no draw.

    With ``real`` given, the two outer segments carry the real cells'
    own first and second moments instead of a straight line's.
    """
    segments = len(rungs) - 1
    first = 0.0
    second = 0.0
    for step in range(segments):
        low, high = rungs[step], rungs[step + 1]
        if real is not None and step in (0, segments - 1):
            inside = len(real) // segments
            part = real[:inside] if step == 0 else real[len(real) - inside :]
            one = math.fsum(part) / len(part)
            two = math.fsum([value * value for value in part]) / len(part)
        else:
            one = (low + high) / 2
            two = (low * low + low * high + high * high) / 3
        first += one / segments
        second += two / segments
    return math.sqrt(max(0.0, second - first * first))


def test_the_ledger_table_misses_no_more_spreads_than_it_did(
    tmp_path: pathlib.Path,
) -> None:
    """20,000 rows by 20: at most 19 moments MISSED, every one a spread."""
    cells = _table("normal", 20000, 20)
    loaded = _described(tmp_path, cells)
    real = [_column_numbers(cells, index) for index in range(20)]
    # The block this file builds IS the one the profiler publishes: on
    # the real table every column's four moments come back to the bit.
    for column, numbers in zip(loaded.columns, real):
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts)
        assert taxonomy.moments_of(numbers) == (
            facts.mean,
            facts.std,
            facts.skew,
            facts.kurtosis,
        ), column.name
    assert not [
        check
        for check in _moment_checks(loaded, real)
        if check.verdict == validation.MISSED
    ]
    twin = generation.generate(loaded, 0)
    written = [
        [float(cell) for cell in twin.columns[index]] for index in range(20)
    ]
    missed = [
        check
        for check in _moment_checks(loaded, written)
        if check.verdict == validation.MISSED
    ]
    assert len(missed) <= CEILING, [check.column for check in missed]
    assert {check.subcheck for check in missed} <= {"moments.std"}
    wider = []
    for column, numbers in zip(loaded.columns, written):
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts)
        assert facts.std is not None
        spread = taxonomy.spread_of(numbers)
        assert spread is not None
        wider += [100 * (spread / facts.std - 1)]
    assert max(wider) <= WIDEST, wider
    # Every miss is a twin WIDER than the column, which is the direction
    # the straight outer segments push; a narrower one is a new defect.
    assert min(wider) > 0.0, wider


def test_at_five_thousand_rows_nothing_is_missed_and_the_tails_make_the_excess(
    tmp_path: pathlib.Path,
) -> None:
    """The ledger's other half, and the diagnosis, on a table a test can build.

    Four columns of the same draw at 5,000 rows: the twin AND the real
    table meet every obligation. On every column the twin is no wider
    than its own ladder, and the ladder with the real table's two outer
    segments put back stands within a quarter of a per cent of the
    published spread, so at least nine tenths of the excess is made by
    those two segments.
    """
    cells = _table("normal", 5000, 4)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    target = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))
    for measured in (target, tmp_path / "real.csv"):
        outcome = validation.measure(loaded, str(measured))
        assert not [
            (check.column, check.subcheck)
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ], measured.name
    for index, column in enumerate(loaded.columns):
        facts = column.facts
        assert isinstance(facts, contract.NumericFacts)
        assert facts.std is not None
        rungs = generation._merged_rungs(facts)
        assert rungs is not None
        real = sorted(_column_numbers(cells, index))
        ladder = _ladder_spread(rungs)
        mended = _ladder_spread(rungs, real)
        spread = taxonomy.spread_of([float(cell) for cell in twin.columns[index]])
        assert spread is not None
        assert spread <= ladder + 0.001 * facts.std, column.name
        assert abs(mended / facts.std - 1) <= 0.0025, column.name
        assert ladder - facts.std > 0.0, column.name
        assert (ladder - mended) >= 0.9 * (ladder - facts.std), column.name


def test_a_uniform_column_at_twenty_thousand_rows_misses_no_moment(
    tmp_path: pathlib.Path,
) -> None:
    """The control: the miss is the tail's shape, not the row count.

    A uniform column's outer one per cent IS spread evenly between `p01`
    and its minimum, so the straight segment is right there, and at the
    ledger's own size nothing is missed.
    """
    cells = _table("uniform", 20000, 2)
    loaded = _described(tmp_path, cells)
    twin = generation.generate(loaded, 0)
    written = [[float(cell) for cell in twin.columns[index]] for index in range(2)]
    assert not [
        (check.column, check.subcheck)
        for check in _moment_checks(loaded, written)
        if check.verdict == validation.MISSED
    ]

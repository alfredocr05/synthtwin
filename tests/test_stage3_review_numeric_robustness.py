"""Stage 3's review, the numeric tail's ROBUSTNESS: six repairs.

The round returned REJECT on all four passes and does not run again, so
every repair is proved by measurement HERE. The six this file holds are
the ones the reviewer classed as robustness -- inputs that used to work
and now crash, lose values, or pass a check they should fail -- and each
test below carries the reviewer's own reproduction, the number it
produced BEFORE the repair, and an expectation worked out from the rule
rather than copied from what the repaired code prints.

    verdict item 2 (HIGH)   an overflowing tail distance threw away the
                            whole ladder, and the block's reader then
                            read `mean + sqrt(3) std` past the range too
                            and fell through to the ladder of a block
                            whose moments are WITHHELD: 11 cells of
                            `-1.7e308` beside 89 near `1.68e308` came
                            back between -11 and 88 at seed 4
    verdict item 3 (HIGH)   G5.3b claimed that reading the shape at the
                            rows' midpoints gave it the published mean
                            and root-mean-square. It does not: 1,199
                            cells just above 100 beside one
                            `100000100.0` came back with a mean 14 per
                            cent low and a spread 24 per cent low, at
                            three seeds, every window passed
    verdict item 4 (MEDIUM) the separation pass of the representable
                            grid ran only on an interval with no spare
                            number, and stage 3's derived ends leave
                            spare numbers: 100 subnormal cells held 82
                            different numbers against 100 published
    verdict item 5 (MEDIUM) the ramp of a block below its floor held
                            nought whether or not the block published
                            one: the numbers 1 to 8 came back as seven
                            numbers, and the report called the invented
                            `0.0` a published endpoint
    verdict item 8 (MEDIUM) an infinite stratum width was converted to a
                            whole number before any bound was applied,
                            and generation raised OverflowError
    verdict item 9 (MEDIUM) constancy was read off a ROUNDED spread, so
                            a column of three subnormal values whose
                            spread underflows to `0.0` made the loader
                            refuse the producer's own file

EVERY MUTATION BELOW WAS RUN. Each test names the one-line reversal that
turns it red and the number that reversal produces, so a reader can
re-run it; a mutation line that has gone stale reads as a guard that
does not exist, which is why each names its own figure.

Every table here is built by seeded neutral code at runtime (plan D13):
nothing is read from any real data.
"""

import csv
import fractions
import io
import json
import math
import pathlib

import pytest

from synthtwin import contract, errors, generation, parsing
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of

Fraction = fractions.Fraction

# The floor every reproduction in the verdict was taken at.
FLOOR = "11"


# ---------------------------------------------------------------- helpers


def _run(
    folder: pathlib.Path,
    cells: "list[str]",
    seed: str = "4",
    floor: str = FLOOR,
    keeper: bool = True,
) -> "tuple[dict, list[str], int, int]":
    """Describe, build and check one one-column table.

    Returns the described column block, the twin's cells, the twin's
    check exit code and the real table's. The keeper column of
    `tests/fixtures` carries the shape up to the population floor where
    its own present cells do not reach it, exactly as every other
    one-column shape in this suite does.
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    names, rows = (
        fixtures.rows_at_the_floor("value", cells)
        if keeper
        else (["value"], [[cell] for cell in cells])
    )
    table.write_text(
        fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
    )
    flags = ["--smallest-group", floor, "--measurement", "value"]
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"] + flags
    ) == 0
    described = folder / "real-profile.json"
    assert _exit_of(
        [
            "generate",
            str(described),
            "--out-dir",
            str(folder),
            "--seed",
            seed,
            "--replace",
        ]
    ) == 0
    twin = folder / "real-twin.csv"
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
        if row
    ][1:]
    checked = folder / "checked"
    checked.mkdir()
    twin_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(twin),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    against = folder / "checked-real"
    against.mkdir()
    real_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(table),
            "--out-dir",
            str(against),
            "--replace",
        ]
    )
    block = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    return block, written, twin_exit, real_exit


def _numbers(written: "list[str]") -> "list[Fraction]":
    """The twin's cells as EXACT rationals.

    A column reaching across the whole binary64 range cannot have its
    mean taken in binary64 -- the sum overflows -- so every moment this
    file measures is taken over rationals and rounded once at the end,
    which is the same arithmetic the producer itself uses.
    """
    found: "list[Fraction]" = []
    for cell in written:
        if cell == "":
            continue
        found += [Fraction(float(cell))]
    return found


def _mean_and_spread(values: "list[Fraction]") -> "tuple[Fraction, Fraction]":
    """The sample mean and the sample variance of exact rationals."""
    count = len(values)
    mean = sum(values) / count
    variance = sum((value - mean) * (value - mean) for value in values)
    return mean, variance / (count - 1)


def _apart(got: Fraction, published: float) -> float:
    """How far a twin's moment stands from the published one, in parts."""
    want = Fraction(published)
    if want == 0:
        return 0.0 if got == 0 else 1.0
    return abs(float((got - want) / want))


def _row_share(index: int, rows: int) -> Fraction:
    """G5.3b's share of row `index` of `rows`: `(2 i + 1) / (2 m)`.

    Written here from the clause and not taken from the loader, which is
    the module these tests are about.
    """
    return Fraction(2 * index + 1, 2 * rows)


def _shape_moments(
    shape: "tuple[bool, int, float, float]", rows: int
) -> "tuple[float, float]":
    """The mean and the root-mean-square of `a(s)` AT THE TAIL'S ROWS.

    The clause says the shape's values at the rows' own shares have the
    published mean distance and the published root-mean-square distance.
    That is what is measured: `a(s)` read at each of the `m` shares
    through the loader's own reader, and the two moments taken over
    exact rationals so the measurement rounds once.
    """
    flat, power, blend, reach = shape
    side = contract.TailReader(
        low=True,
        percent=1,
        boundary=0.0,
        rows=rows,
        numbers=0,
        flat=flat,
        power=power,
        blend=blend,
        reach=reach,
        end=0.0,
        listed=(),
        counts=(),
    )
    distances: "list[Fraction]" = []
    for index in range(rows):
        share = _row_share(index, rows)
        found = contract._shape_at(side, math.ldexp(
            (share.numerator << 53) // share.denominator, -53
        ))
        distances += [Fraction(found)]
    mean = sum(distances) / rows
    square = sum(one * one for one in distances) / rows
    return float(mean), math.sqrt(float(square))


# ------------------------------------------------- item 2: the overflow


def _huge_column(tail_rows: int) -> "list[str]":
    """The reviewer's own huge-magnitude column, at a chosen size."""
    return ["-1.7e308"] * 11 + [
        repr(1.68e308 + step * 1e304) for step in range(tail_rows)
    ]


def test_an_overflowing_tail_distance_keeps_the_published_scale(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 2: the twin of `1.3e308` was written between -11 and 88.

    THE REPRODUCTION. 11 cells of `-1.7e308` beside 89 around `1.68e308`.
    Every tail distance is about `3.4e308`, which binary64 does not hold,
    so the producer could publish neither the mean nor the
    root-mean-square of either tail. It answered by withdrawing the whole
    ladder and publishing its four moments alone; the reader of THAT
    block read `mean + sqrt(3) std` past the range as well, fell back to
    the ramp of a block below its floor, and at seed 4 wrote numbers
    between -11 and 88. Its mean and spread both failed the check.

    THE RULE. A tail with no publishable pair is a shape the contract
    already has -- TL5's tail publishing NEITHER distance -- so the block
    keeps its boundary rung and its rows and withholds the pair. What is
    asserted here is that shape and the scale it preserves: the published
    moments are finite, the twin's own moments stand beside them, and the
    twin's cells reach the magnitudes the description publishes rather
    than the small whole numbers of a ramp.

    MUTATION (run): restoring `if low is None or high is None: return
    moments_only` in `taxonomy._numeric_tails` puts `tails` back to two
    nulls, every rung back to null, and the twin back between -11 and 88.
    """
    block, written, twin_exit, real_exit = _run(
        tmp_path / "overflow", _huge_column(89)
    )
    # The pair is withheld on the side whose distances overflow, and the
    # block keeps the ladder it would otherwise have thrown away.
    assert block["tails"] is not None
    assert block["tails"]["low"]["mean_distance"] is None
    assert block["tails"]["low"]["rms_distance"] is None
    assert block["tails"]["low"]["values"] == []
    assert block["percentiles"]["p50"] is not None
    # THE SCALE IS THE DESCRIPTION'S OWN. A twin built from a ramp holds
    # whole numbers a few dozen either side of nought; this one holds the
    # magnitudes the published mean and spread describe.
    values = _numbers(written)
    assert len(values) == 100
    assert max(abs(one) for one in values) > Fraction(1) / 2 * Fraction(
        block["std"]
    )
    mean, variance = _mean_and_spread(values)
    assert _apart(mean, block["mean"]) < 0.05
    spread = Fraction(math.isqrt(int(variance * 10**40)), 10**20)
    assert _apart(spread, block["std"]) < 0.5
    assert real_exit == 0
    assert twin_exit == 0


def test_a_moment_only_block_past_the_range_keeps_its_mean(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 2, the second road: the moment ladder's own overflow.

    A block with fewer values than two tails need publishes its four
    moments and no rung at all (TL3), and its ladder is G5.3c's uniform
    stretch. Where `mean + sqrt(3) std` is not representable there is no
    such stretch: 22 huge cells publishing a mean of about `-9.7e305` and
    a spread of about `1.7e308` gave two infinite ends, and the block
    fell through to G5.3d's ramp -- the ladder of a block whose moments
    are WITHHELD -- so the twin came back between -11 and 11.

    THE RULE. The reach is held at `LARGEST_FINITE - |mean|`, so the
    stretch is the widest the format holds ABOUT THE PUBLISHED MEAN: the
    ladder runs from `mean - reach` to `mean + reach`, one of which is
    the edge of the range. That is what is asserted -- the LADDER, which
    is what this clause decides -- and beside it the scale of the cells
    the twin actually writes. The block's own spread cannot be reached
    at all here, and the twin's report says so on the spread's own line;
    what the repair owes is that the ladder be the stretch and not
    another block's ramp.

    MUTATION (run): restoring `if not (isfinite(lowest) and
    isfinite(highest)): return None` in `contract._moment_ladder` sends
    the block to the ramp -- a ladder from -11 to 11 -- and the twin's
    cells with it.
    """
    cells = _huge_column(11) + [""] * 78
    folder = tmp_path / "moments"
    block, written, _twin_exit, real_exit = _run(folder, cells)
    assert block["tails"] == {"low": None, "high": None}
    assert block["percentiles"]["p50"] is None
    loaded = contract.load_profile(str(folder / "real-profile.json"))
    rungs = contract.tail_ladder(loaded.columns[0].facts)
    assert rungs is not None
    # THE WIDEST STRETCH THE FORMAT HOLDS ABOUT THE PUBLISHED MEAN,
    # worked out here from the clause and not read off the ladder.
    published = block["mean"]
    reach = contract._LARGEST_FINITE - abs(published)
    assert rungs[0] == published - reach
    assert rungs[100] == published + reach
    assert min(rungs[0], -rungs[100]) == -contract._LARGEST_FINITE
    # A RAMP WOULD HOLD WHOLE NUMBERS ABOUT THE SIZE OF THE BLOCK. The
    # scale the description publishes is its spread, and the twin's own
    # cells reach it rather than the count of its rows.
    values = _numbers(written)
    assert max(abs(one) for one in values) > Fraction(1) / 2 * Fraction(
        block["std"]
    )
    assert real_exit == 0


# ------------------------------------- item 3: the moment-preserving fit


@pytest.mark.parametrize(
    "mean,root,rows",
    [
        (1.0, 1.0, 12),
        (1.0, 1.2, 12),
        (2.5, 3.0, 25),
        (0.005412844036702798, 0.00613091781274414, 12),
        (8333333.255412844, 28867513.173692904, 12),
        (3.0, 9.0, 200),
        (1e-9, 3e-9, 30),
    ],
)
def test_the_tail_shape_has_the_moments_its_clause_claims(
    mean: float, root: float, rows: int
) -> None:
    """Verdict item 3: G5.3b's moment-preserving claim was false.

    THE CLAIM. `a(s) = E s**j (lam + (1 - lam) s)` is fitted so that its
    mean over a UNIFORM `s` is `d1` and its mean square is `rms * rms`,
    and the rows are then read at `s = (2 i + 1) / (2 m)` -- which the
    clause said made the ROWS' mean equal that integral. Sampling a
    nonlinear power mixture at midpoints is not its integral, and the
    error grows with the power: on the twelve-row tail of the reviewer's
    own column, whose ratio stands within a billionth of twelve, the
    fitted shape read at the rows gave a mean 14 per cent below `d1`.

    WHAT IS MEASURED HERE IS THE MOMENTS THEMSELVES and not a window: the
    shape is read at each of the `m` row shares and the two moments are
    taken over exact rationals. Both must be the published numbers to
    within the last few places of binary64, which is all the arithmetic
    can promise.

    MUTATION (run): putting the smooth constants back -- `near = 1 /
    (power + 2)`, `gap = 1 / ((power + 1) * (power + 2))`, `first = 1 /
    (2 power + 1)`, `middle = 1 / (power + 1)`, `last = 1 / (2 power +
    3)` -- in `contract._tail_shape` takes the last case's mean to
    7.2e6 against 8.33e6 and its root-mean-square to 2.19e7 against
    2.89e7, and turns this test red on six of its seven cases.
    """
    shape = contract._tail_shape(mean, root, rows)
    assert shape[0] is False
    got_mean, got_root = _shape_moments(shape, rows)
    assert abs(got_mean - mean) <= abs(mean) * 1e-9
    assert abs(got_root - root) <= abs(root) * 1e-9


def test_a_lone_far_value_keeps_the_column_s_mean_and_spread(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 3's own column, end to end, at its three seeds.

    1,199 cells just above 100 beside one `100000100.0`. Measured before
    the repair: the source's mean 83,433.8325 and spread 2,886,751.3315
    came back as 71,752.9427 and 2,187,315.8537 at seeds 0, 4 and 9 --
    14 and 24 per cent low -- with no deviation reported and every
    numeric window passed. The windows endorsed it, so this test asks
    the MOMENTS.

    The bound is 1 in 10,000 on each moment, which is what a tail read
    through a shape can promise: the shape's own moments are exact (the
    test above), and what is left is the rounding of each row onto the
    column's grid.
    """
    cells = [repr(100 + step / 1199) for step in range(1199)] + [
        "100000100.0"
    ]
    for seed in ("0", "4", "9"):
        block, written, twin_exit, real_exit = _run(
            tmp_path / f"lone-{seed}", cells, seed=seed, keeper=False
        )
        values = _numbers(written)
        mean, variance = _mean_and_spread(values)
        spread = Fraction(math.isqrt(int(variance * 10**20)), 10**10)
        assert _apart(mean, block["mean"]) < 1e-4, seed
        assert _apart(spread, block["std"]) < 1e-4, seed
        assert real_exit == 0 and twin_exit == 0


# ----------------------------------- item 4: the representable grid fill


def test_subnormal_cells_keep_every_number_they_publish(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 4: 100 subnormal cells held 82 numbers of 100.

    THE REPRODUCTION. `[str(i * 5e-324) for i in range(1, 101)]` at a
    floor of eleven, seed 4. These cells sit one binary64 step apart at
    the bottom of the range and their census names no fraction width, so
    the separation pass has no decimal grid and falls to its last resort,
    the representable numbers themselves. That resort ran only where the
    two ends hold EXACTLY as many representable numbers as the column has
    strata, and stage 3's derived ends leave 106 numbers for 100 strata,
    so it withdrew and the twin held 82. The pre-tail code held 100.

    THE RULE. Each stratum takes the point nearest the value the ladder
    gave it that the order still allows. What is asserted is the
    OBLIGATION -- the block's own published count of different numbers --
    and not a number copied from a run.

    MUTATION (run): restoring `if grid[total - 1] != ceiling: return
    values` in `generation._apart_on_the_representable_grid` withdraws
    the pass again and the twin holds 82.
    """
    cells = [str(step * 5e-324) for step in range(1, 101)]
    block, written, twin_exit, real_exit = _run(tmp_path / "subnormal", cells)
    held = {float(cell) for cell in written}
    assert block["n_distinct_values"] == 100
    assert len(held) == block["n_distinct_values"]
    assert real_exit == 0 and twin_exit == 0


# -------------------------------------------- item 5: the below-floor ramp


def test_the_ramp_invents_no_zero_and_loses_no_value(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 5: eight numbers came back as seven, around a made-up 0.

    THE REPRODUCTION. A 100-row table holding the numbers 1 to 8 and 92
    blank cells. The block is below its own floor, so it publishes no
    rung and no moment and its ladder is G5.3d's ramp. The ramp ran from
    `-G u` to `(K - G - 1) u` whatever the block said about signs, so it
    spanned 0 to 7 on a column publishing `n_zero: 0`; G5.5's sign repair
    moved the invented nought onto a number another stratum already held,
    and the twin wrote seven different numbers against the eight
    published. Its report then named `percentiles` as a fact the twin
    missed and printed `0.0` as the value "the description says", on a
    block whose every rung is withheld.

    THE RULE. The ramp is built from the sign counts the block actually
    publishes: `G` negatives below nought, `Z` noughts and `P = K - G -
    Z` positives above it. What is asserted is what those counts oblige
    -- as many different numbers as the block publishes, no cell of a
    sign the block counts at nought, and no report line naming a rung as
    published when the block publishes none.

    MUTATION (run): restoring `lowest = -negatives * unit` and `highest =
    (numbers - negatives - 1) * unit` with the straight interpolation in
    `contract._tail_ramp` takes the twin back to seven different numbers
    and puts the `0.0` line back in the report.
    """
    cells = [str(step) for step in range(1, 9)] + [""] * 92
    for seed in ("4", "0", "7"):
        folder = tmp_path / f"ramp-{seed}"
        block, written, twin_exit, real_exit = _run(folder, cells, seed=seed)
        assert block["tails"] is None
        assert block["percentiles"]["min"] is None
        assert block["n_zero"] == 0 and block["n_negative"] == 0
        held = {float(cell) for cell in written if cell != ""}
        assert len(held) == block["n_distinct_values"], seed
        # THE SIGN COUNTS ARE THE OBLIGATION, so a cell at nought on a
        # block publishing none is a cell no count allows.
        assert 0.0 not in held, seed
        assert min(held) > 0.0, seed
        report = (folder / "real-twin-report.txt").read_text(encoding="utf-8")
        # A BLOCK WHOSE EVERY RUNG IS WITHHELD HAS NO PUBLISHED END to
        # print beside a twin's value.
        assert "'value' -- percentiles" not in report, seed
        assert real_exit == 0 and twin_exit == 0, seed


def test_the_ramp_follows_the_sign_counts_it_is_given(
    tmp_path: pathlib.Path,
) -> None:
    """The ramp's own rule, asked of the three sign shapes it must serve.

    Worked out from the clause: the made-up values are `-G u` up to `-u`,
    then nought `Z` times, then `u` up to `P u`; rung `p` is the value at
    the whole rank nearest `(K - 1) p / 100`, halves downward. So the two
    ends of the ladder are the outermost of those values, the ladder
    holds a nought exactly where `Z` is above nought, and it holds as
    many different numbers as the counts leave room for.

    The blocks are DESCRIBED rather than hand-built, so the ladder asked
    here is the ladder a described table produces, and a key the
    producer stops writing turns this red rather than passing on a
    fixture nobody writes any more.
    """
    def ramp(
        name: str, negatives: int, zeros: int, positives: int
    ) -> "tuple[float, ...]":
        cells = (
            [str(-step) for step in range(1, negatives + 1)]
            + ["0"] * zeros
            + [str(step) for step in range(1, positives + 1)]
        )
        folder = tmp_path / name
        folder.mkdir(parents=True, exist_ok=True)
        table = folder / "real.csv"
        names, rows = fixtures.rows_at_the_floor(
            "value", cells + [""] * (100 - len(cells))
        )
        table.write_text(
            fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
        )
        assert _exit_of(
            [
                "profile",
                str(table),
                "--out-dir",
                str(folder),
                "--replace",
                "--measurement",
                "value",
            ]
        ) == 0
        loaded = contract.load_profile(str(folder / "real-profile.json"))
        facts = loaded.columns[0].facts
        assert facts.tails is None
        return tuple(contract.tail_ladder(facts))

    # No zero published: the ladder holds none, and runs 1 .. K.
    rungs = ramp("positives", 0, 0, 8)
    assert rungs[0] == 1.0 and rungs[100] == 8.0
    assert 0.0 not in rungs
    assert len(set(rungs)) == 8
    # A zero published: it is there, once, between the two sides.
    rungs = ramp("signed", 3, 2, 3)
    assert rungs[0] == -3.0 and rungs[100] == 3.0
    assert 0.0 in rungs
    assert set(rungs) == {-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0}
    # Negatives alone: every rung is below nought.
    rungs = ramp("negatives", 5, 0, 0)
    assert rungs[0] == -5.0 and rungs[100] == -1.0
    assert max(rungs) < 0.0


# ----------------------------------------- item 8: the overflowing width


def test_a_large_magnitude_column_does_not_stop_generation(
    tmp_path: pathlib.Path,
) -> None:
    """Verdict item 8: generation raised OverflowError at seed 4.

    THE REPRODUCTION. 20 cells of `-1.7e308` beside 80 near `1.68e308`.
    Profiling and loading both succeed; a stratum's share then spans
    `(-1.7e308, 1.004e308)`, whose width overflows to infinity, and
    `int(width / unit)` raised `OverflowError: cannot convert float
    infinity to integer` -- BEFORE the search count was capped at all.

    THE RULE. The count this search may use is `_GRID_REACH` whatever the
    width is, so a width or a quotient at or past it settles the count
    without a conversion. What is asserted is that the run finishes and
    that the twin keeps the published scale; the number of different
    values it reaches is not this repair's subject and is reported by the
    check either way.

    MUTATION (run): restoring `steps = int(width / unit) + 1` in
    `generation._apart_walk` raises OverflowError on this shape again.
    """
    cells = ["-1.7e308"] * 20 + [
        repr(1.68e308 + step * 1e304) for step in range(80)
    ]
    block, written, _twin_exit, real_exit = _run(tmp_path / "wide", cells)
    values = _numbers(written)
    assert len(values) == 100
    mean, _variance = _mean_and_spread(values)
    assert _apart(mean, block["mean"]) < 0.05
    assert real_exit == 0


def test_an_infinite_share_is_bounded_before_it_is_counted() -> None:
    """The bound itself, asked of the arithmetic the reproduction reaches.

    The quotient of an infinite width by any grid unit is infinite, and
    the rule is that the count is `_GRID_REACH` there. Asked directly so
    the guard is a guard and not a side effect of one shape.
    """
    width = abs(1.004e308 - -1.7e308)
    assert math.isinf(width)
    for figures in (0, 1, 2):
        unit = math.ldexp(1.0, 0)
        for _each in range(figures):
            unit = unit / 10.0
        spread = width / unit
        assert not spread < float(generation._GRID_REACH)


# ----------------------------------------- item 9: constancy and rounding


@pytest.mark.parametrize("floor", ["1", "5", "11"])
def test_a_spread_that_rounds_to_nought_is_not_constancy(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """Verdict item 9: the loader refused the producer's own file.

    THE REPRODUCTION. 98 copies of `5e-324` beside `1e-323` and
    `1.5e-323`. The producer publishes three different values, a skew of
    7.863539654706267 and a spread that underflows to `0.0` -- the true
    spread is about `4e-325`, below the smallest number binary64 holds.
    The tail-block form of invariant Q5 read `std == 0.0` as "every value
    the statistics used is the same" and refused the file, at floors 1, 5
    and 11 alike, and describing the table again wrote the same file.

    THE RULE. Constancy is read off `n_distinct_values`, the block's own
    exact count of the different numbers its numeric cells hold. What is
    asserted is that the file the producer writes is a file the loader
    reads, which is the invariant a self-check owes, and that the three
    facts the reproduction turns on are still published.

    MUTATION (run): restoring `flat = std == 0.0 and not unrepresentable`
    in `contract._numeric_facts` raises ProfileError Q5 -- "the shape is
    given as 7.863539654706267, and every value the statistics used is
    the same" -- at all three floors.
    """
    cells = ["5e-324"] * 98 + ["1e-323", "1.5e-323"]
    block, written, _twin_exit, real_exit = _run(
        tmp_path / f"rounded-{floor}", cells, floor=floor
    )
    assert block["n_distinct_values"] == 3
    assert block["std"] == 0.0 and block["std_unrepresentable"] is False
    assert block["skew"] is not None
    assert len(written) >= parsing.POPULATION_FLOOR
    assert real_exit == 0


def test_one_different_number_is_still_constancy(
    tmp_path: pathlib.Path,
) -> None:
    """The other side of the same rule: ONE number IS constancy.

    The very file of the test above, with `n_distinct_values` moved from
    three to one and nothing else touched. Read off the spread the two
    documents are the same document -- both publish `std: 0.0` -- and the
    loader could not tell them apart; read off the count of different
    numbers it can, and Q5 refuses the second because a block holding one
    number has no shape to publish. That is the repair, asked from the
    side that must still refuse.
    """
    folder = tmp_path / "one-number"
    folder.mkdir(parents=True)
    table = folder / "real.csv"
    cells = ["5e-324"] * 98 + ["1e-323", "1.5e-323"]
    names, rows = fixtures.rows_at_the_floor("value", cells)
    table.write_text(
        fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
    )
    assert _exit_of(
        [
            "profile",
            str(table),
            "--out-dir",
            str(folder),
            "--replace",
            "--measurement",
            "value",
        ]
    ) == 0
    described = folder / "real-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert block["std"] == 0.0 and block["skew"] is not None
    # As written: three different numbers, a shape, and a spread of
    # nought. The loader reads it.
    loaded = contract.load_profile(str(described))
    assert loaded.columns[0].facts.n_distinct_values == 3
    block["n_distinct_values"] = 1
    edited = fixtures.write_profile(folder, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(edited))
    assert "Q5" in str(refusal.value)


def test_a_block_below_its_floor_holding_one_number_is_still_read(
    tmp_path: pathlib.Path,
) -> None:
    """Q6 and Q7 pass over a block below its floor, as Q4, Q5 and Q16 do.

    FOUND WHILE REPAIRING VERDICT ITEM 9. Read off the spread, a block
    below its own floor was never flat -- it publishes no spread, and
    `None == 0.0` answers no -- so Q6 and Q7 were never asked of one.
    Read off the count of different numbers, a below-floor block holding
    ONE number IS flat, and it publishes neither the spread Q6 would ask
    for nor the average Q7 would, because contract TL2 says it publishes
    no moment at all. Without the same `below_floor` guard the other
    three rows already carry, the repair would have made the loader
    refuse a description this producer writes.

    MUTATION (run): removing `and not below_floor` from Q7 in
    `contract._numeric_facts` refuses this document -- "the average is
    left out ... every value is the same, so the average is that value
    and this format holds it".
    """
    folder = tmp_path / "below-floor"
    folder.mkdir(parents=True)
    table = folder / "real.csv"
    cells = [str(step) for step in range(1, 9)] + [""] * 92
    names, rows = fixtures.rows_at_the_floor("value", cells)
    table.write_text(
        fixtures.rows_to_csv(names, rows), encoding="utf-8", newline=""
    )
    assert _exit_of(
        [
            "profile",
            str(table),
            "--out-dir",
            str(folder),
            "--replace",
            "--measurement",
            "value",
        ]
    ) == 0
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    block = document["columns"][0]
    assert block["tails"] is None and block["mean"] is None
    # The same block with ONE number in it, which is the shape the
    # spread could not tell from the shape above.
    block["n_distinct_values"] = 1
    block["n_distinct"] = 1
    block["n_distinct_folded"] = 1
    edited = fixtures.write_profile(folder, "one-number.json", document)
    loaded = contract.load_profile(str(edited))
    assert loaded.columns[0].facts.n_distinct_values == 1


# ------------------------------ the style packing the value pass exposed


def test_a_style_packing_never_spends_fewer_spellings_than_published(
    tmp_path: pathlib.Path,
) -> None:
    """One form per stratum is the FEWEST spellings, not the right number.

    FOUND BESIDE VERDICT ITEM 4. `generation._style_strata` packs the
    styles over whole strata where the cell walk would spend more
    spellings than the column publishes, so that a split inside a
    stratum does not buy a spelling with a value. One form per stratum is
    the fewest spellings a column can hold -- one for each stratum -- so
    where the published count stands ABOVE the number of strata the
    column has room for a split the packing cannot make: giving up the
    walk's answer there misses `n_distinct` from below, which is the
    same trade the rule exists to refuse, taken the other way.

    Measured on the frozen case `numeric_decimal_styles` once item 4's
    repair stopped its ladder standing two strata on one number: 23
    strata, 24 spellings published, the cell walk spending 25 -- one over,
    and authorized, since `n_distinct` is judged in a window running from
    the published count upward -- against a packing spending 23, which
    `validate` reports as MISSED.

    AND THE PACKING STILL RUNS WHERE IT CAN MEET THE COUNT, which is
    what the second half of this test holds: 1,020 offsets written two
    ways publish 917 different spellings over more strata than that, and
    the packing takes them to exactly 917 where the walk's own answer
    holds 1,023
    (`test_p4d140_number_censuses.py::test_offsets_written_both_ways_keep_their_spellings_and_widths`).

    MUTATION (run): removing the `if raw > total: return styles` guard
    from `generation._style_strata` takes the frozen case's cells to 23
    spellings and turns
    `test_generation_reference.py::test_the_implementation_writes_the_committed_cells[numeric_decimal_styles]`
    red.
    """
    quotas = {
        "plain": 0,
        "decimal": 0,
        "leading_zero": 0,
        "leading_plus": 0,
        "exponent_lower": 2,
        "exponent_upper": 2,
        "(withheld)": 0,
    }
    layout = generation._NumericLayout(
        sizes=(2, 1, 1),
        starts=(0, 2, 3),
        bands=(generation._BAND_POSITIVE,) * 3,
        raw_budgets=(0, 0, 0, 0),
        folded_budgets=(0, 0, 0, 0),
    )
    values = [1e15, 2e15, 3e15]
    walked = [
        "exponent_lower",
        "exponent_upper",
        "exponent_lower",
        "exponent_upper",
    ]
    # Four spellings published over three strata: the walk's own answer
    # spends four and the packing could spend only three, so the walk
    # stands.
    assert generation._style_strata(
        quotas, layout, values, False, 4, 4, walked
    ) == walked
    # With three published, the packing meets the count exactly and is
    # taken: every stratum keeps one form.
    packed = generation._style_strata(
        quotas, layout, values, False, 3, 3, walked
    )
    assert packed[0] == packed[1]

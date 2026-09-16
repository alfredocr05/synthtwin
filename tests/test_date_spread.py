"""Landing 2b.6 part 2: a twin's dates are spread across days as the real ones are.

THE DEFECT THIS GATE EXISTS FOR, measured on the commit before it. The
generator wrote one cell per rank inside that rank's own `1 / P` slice
of the distribution, so every day received almost exactly its expected
count -- a below-Poisson spread, where a real table's per-day counts
vary at least Poisson. Over 54 runs of uniform, seasonal and
admissions-style columns, date-only and at midnight, at 400, 1,500 and
3,000 rows and three seeds, the twin's per-day count variance was
**0.057 to 0.514 of the real column's** (median 0.334), and it got WORSE
as the column grew, because stratifying ever more finely is ever further
from sampling.

And a second defect rode with it: at every one of the nine interior
rungs the twin sat BELOW the published value, because the interpolation
floors. **Every published rung was missed in all 54 runs** -- one day
early on a 400-row admissions column, so a rung published as a Monday
was written as a Sunday.

Both are repaired by pinning each rung's rank to its PUBLISHED value and
drawing every other rank independently inside the gap between the two
pinned ranks either side of it (method G7.3). Measured again over the
same 54 runs: every rung exact in 54 of 54, and the variance ratio 0.52
to 1.41.

WHAT THIS GATE DOES NOT CLAIM, asserted here as a named limit rather
than left for a reader to discover. The gap is filled EVENLY, so
structure the description does not publish does not come back: which
weekday a value falls on, the time of day, days the real column heaps
values on, and a column whose values sit on a few scheduled dates. On a
seasonal or admissions-style column that structure is most of the
day-to-day variance at 3,000 rows, and the ratio there stays near 0.55
-- above the 0.06 it was, and below the band the smaller columns meet.
Each would need a fact no datetime block carries, and each of those
publishes counts over small groups, so what may be published is a
question for the stage that sets the disclosure floor. The generator
says so in the twin's own report, and the last test here is what holds
it to saying it.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import datetime
import io
import json
import math
import pathlib
import random
import statistics
import sys

import pytest

from tests import fixtures

# The nine interior rungs, by the percent each is published at.
INTERIOR = (1, 5, 10, 25, 50, 75, 90, 95, 99)

# The band the repaired construction is held to. Measured over ten seeds
# per shape and size: uniform 0.93-1.41, seasonal 0.71-1.07 at 400 and
# 0.62-0.71 at 1,500, admissions 0.86-1.17 at 400 and 0.68-0.88 at
# 1,500. The floor is not a round number chosen for comfort -- the
# closest any measured case came to it is seasonal at 1,500 rows, at
# 0.618.
LOWEST = 0.6
HIGHEST = 1.6

# What a column whose shape is carried by the weekday is held to at
# 3,000 rows, where the evenly-filled gap cannot reach the band. The
# measured range there is 0.524 to 0.711; the withdrawn construction
# reached 0.057 to 0.066 on the same columns, so this floor is still
# seven times what the defect allowed and is a bound on the RESIDUAL,
# not a weakened form of the band above.
RESIDUAL_LOWEST = 0.45


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _span(first: "datetime.date", last: "datetime.date") -> "list[datetime.date]":
    return [
        first + datetime.timedelta(days=step)
        for step in range((last - first).days + 1)
    ]


def _uniform(draw: "random.Random", count: int) -> "list[datetime.date]":
    """Arrivals with no calendar shape at all."""
    pool = _span(datetime.date(2025, 1, 1), datetime.date(2025, 12, 31))
    return [draw.choice(pool) for _ in range(count)]


def _seasonal(draw: "random.Random", count: int) -> "list[datetime.date]":
    """A yearly swell, with most weekend days dropped."""
    pool = _span(datetime.date(2025, 1, 1), datetime.date(2025, 12, 31))
    weights: "list[float]" = []
    for day in pool:
        weight = 1.0 + 0.8 * math.cos(
            2 * math.pi * (day.timetuple().tm_yday / 365.0)
        )
        if day.weekday() >= 5:
            weight = weight * 0.3
        weights += [max(0.02, weight)]
    return draw.choices(pool, weights=weights, k=count)


def _admissions(draw: "random.Random", count: int) -> "list[datetime.date]":
    """Hospital admissions: a full week, a quiet weekend, no public holidays."""
    accept = (1.0, 0.9, 0.9, 0.9, 0.85, 0.3, 0.25)
    holidays = ((1, 1), (1, 6), (4, 7), (5, 1), (8, 15), (11, 1), (12, 25), (12, 26))
    pool: "list[datetime.date]" = []
    weights: "list[float]" = []
    for day in _span(datetime.date(2023, 1, 1), datetime.date(2024, 12, 31)):
        if (day.month, day.day) in holidays:
            continue
        pool += [day]
        weights += [accept[day.weekday()]]
    return draw.choices(pool, weights=weights, k=count)


SHAPES = {
    "uniform": _uniform,
    "seasonal": _seasonal,
    "admissions": _admissions,
}


def _written(days: "list[datetime.date]", midnight: bool) -> "list[str]":
    if midnight:
        return [f"{day.isoformat()} 00:00:00" for day in days]
    return [day.isoformat() for day in days]


def _per_day(cells: "list[str]", whole: "list[str]") -> "list[int]":
    """One count per day of the real column's whole span, empty days included."""
    held: "dict[str, int]" = {}
    for cell in cells:
        day = cell[0:10]
        held[day] = held.get(day, 0) + 1
    return [held.get(day, 0) for day in whole]


def _round_trip(
    folder: pathlib.Path, cells: "list[str]", seed: str
) -> "tuple[dict, dict, list[str], int, int]":
    """Describe, build, describe the twin; check the twin AND the real table."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["when"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"]) == 0
    described = folder / "real-profile.json"
    assert (
        _exit_of(
            [
                "generate",
                str(described),
                "--out-dir",
                str(folder),
                "--seed",
                seed,
                "--replace",
            ]
        )
        == 0
    )
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(["profile", str(copied), "--out-dir", str(again), "--replace"]) == 0
    first = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
    ][1:]
    checked = folder / "check-twin"
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
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(table),
            "--out-dir",
            str(real_checked),
            "--replace",
        ]
    )
    return first, second, written, twin_exit, real_exit


def _measured(
    folder: pathlib.Path, shape: str, rows: int, seed: int, midnight: bool
) -> "tuple[float, list[str]]":
    """One run: the variance ratio, and any rung the twin failed to place."""
    draw = random.Random(seed * 7919 + rows)
    days = sorted(SHAPES[shape](draw, rows))
    cells = _written(days, midnight)
    first, _second, written, twin_exit, real_exit = _round_trip(
        folder, cells, str(seed)
    )
    assert twin_exit == 0, f"{shape} {rows} {seed}: the twin missed an obligation"
    assert real_exit == 0, f"{shape} {rows} {seed}: the REAL table missed one"
    whole = [
        day.isoformat()
        for day in _span(
            datetime.date.fromisoformat(cells[0][0:10]),
            datetime.date.fromisoformat(cells[-1][0:10]),
        )
    ]
    real_variance = statistics.pvariance(_per_day(cells, whole))
    twin_variance = statistics.pvariance(_per_day(written, whole))
    assert real_variance > 0, "the real column varies by nothing, so there is no ratio"
    # EVERY PUBLISHED RUNG, ASKED OF THE TWIN'S OWN CELLS at the rank the
    # profiler selects it from -- the fact itself, not a window around it.
    parsed = rows - first["n_unparsed"]
    ordered = sorted(written)
    missed: "list[str]" = []
    for place in range(1, len(INTERIOR) + 1):
        percent = INTERIOR[place - 1]
        rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
        published = first["date_percentiles"][f"p{percent:02d}"]
        if ordered[rank] != published:
            missed += [f"p{percent:02d}: {published} -> {ordered[rank]}"]
    return (twin_variance / real_variance, missed)


@pytest.mark.parametrize("midnight", [False, True])
@pytest.mark.parametrize("rows", [400, 1500])
@pytest.mark.parametrize("shape", sorted(SHAPES))
@pytest.mark.parametrize("seed", [4, 7])
def test_a_twin_spreads_its_days_as_the_real_column_did(
    tmp_path: pathlib.Path, shape: str, rows: int, seed: int, midnight: bool
) -> None:
    """The gate: the day-to-day variance is the real column's, and every rung is exact.

    Three shapes a researcher actually holds -- arrivals with no calendar
    shape, a yearly swell with quiet weekends, and hospital admissions
    with a quiet weekend and no public holidays -- written as whole dates
    and as moments at midnight, at two realistic sizes and two seeds. The
    twin and the REAL table both validate with nothing missed.
    """
    ratio, missed = _measured(
        tmp_path / f"{shape}-{rows}-{seed}", shape, rows, seed, midnight
    )
    assert not missed, (
        f"{shape} at {rows} rows, seed {seed}: the twin does not hold the "
        f"published rung at its own rank: {missed}"
    )
    assert LOWEST <= ratio <= HIGHEST, (
        f"{shape} at {rows} rows, seed {seed}: the twin's per-day count "
        f"variance is {ratio:.3f} of the real column's, outside "
        f"{LOWEST}-{HIGHEST}. Below the band the twin spreads its values "
        f"more evenly than the real table did; above it, less evenly."
    )


@pytest.mark.parametrize("shape", ["uniform"])
@pytest.mark.parametrize("seed", [4, 7])
def test_a_large_column_with_no_calendar_shape_still_meets_the_band(
    tmp_path: pathlib.Path, shape: str, seed: int
) -> None:
    """Three thousand rows, where the defect was worst: it was 0.07 of the real.

    The withdrawn construction got WORSE as the column grew -- 0.070 to
    0.083 at this size -- because stratifying ever more finely is ever
    further from sampling. A column with no calendar shape is the one
    whose whole variance the description can carry, so this is the size
    and shape where the repair is asked for the full band.
    """
    ratio, missed = _measured(tmp_path / f"{shape}-3000-{seed}", shape, 3000, seed, False)
    assert not missed, missed
    assert LOWEST <= ratio <= HIGHEST, f"{shape} at 3000 rows: {ratio:.3f}"


@pytest.mark.parametrize("shape", ["seasonal", "admissions"])
def test_a_large_column_shaped_by_the_weekday_is_short_and_says_so(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """THE NAMED LIMIT, pinned so that closing it is a visible decision.

    At 3,000 rows most of a seasonal or admissions column's day-to-day
    variance is structure the description does not publish: which weekday
    a value falls on, and how the density moves WITHIN a gap between two
    published rungs. The gap is filled evenly, so the twin cannot reach
    it -- measured 0.524 to 0.711 against the band's 0.6.

    This is asserted as a floor and a ceiling rather than left silent,
    because the number is what a later landing will move: the withdrawn
    construction reached 0.057 to 0.066 on these same columns, so what is
    pinned here is a sevenfold repair that is still short, and a change
    in either direction shows up as a failure rather than as nothing.
    """
    ratio, missed = _measured(tmp_path / f"{shape}-3000", shape, 3000, 4, False)
    assert not missed, missed
    assert RESIDUAL_LOWEST <= ratio <= HIGHEST, (
        f"{shape} at 3000 rows: {ratio:.3f}, outside "
        f"{RESIDUAL_LOWEST}-{HIGHEST}"
    )
    assert ratio < LOWEST, (
        f"{shape} at 3000 rows now reaches {ratio:.3f}, which is inside the "
        f"band this test records it as SHORT of. If a landing carried the "
        f"weekday census or a finer ladder, this test and the report "
        f"sentence it guards are what should be rewritten -- and the plan's "
        f"residual closed -- rather than this assertion deleted."
    )


def test_the_report_names_what_a_column_of_dates_does_not_reproduce(
    tmp_path: pathlib.Path,
) -> None:
    """The enumerated remark, and all four things it must name.

    Part A repairs the day-to-day variance and leaves four kinds of
    structure behind. A report that said only that the distinctness
    counts were inside their window would be true and would tell a
    reader nothing about any of them, so the generator says it plainly
    and this holds it to saying it.
    """
    draw = random.Random(11)
    days = sorted(_admissions(draw, 400))
    folder = tmp_path / "named"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["when"], [[cell] for cell in _written(days, False)]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"]) == 0
    assert (
        _exit_of(
            [
                "generate",
                str(folder / "real-profile.json"),
                "--out-dir",
                str(folder),
                "--seed",
                "4",
                "--replace",
            ]
        )
        == 0
    )
    report = (folder / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "how these dates are spread across the calendar" in report
    for clause in (
        "which days of the week",
        "the time of day",
        "far more values than their neighbours",
        "a few scheduled dates",
    ):
        assert clause in report, f"the report no longer names: {clause}"


def test_a_column_beside_the_dates_is_untouched_by_this_rule(
    tmp_path: pathlib.Path,
) -> None:
    """The word budget is unchanged, so no other column's cells move.

    Each rank between the pinned ones draws exactly one word and a
    pinned rank draws its word and discards it, so a column of dates
    consumes exactly what it always consumed. The numpy stream is shared
    across columns, so had the budget changed, every column generated
    after a column of dates would have moved with it. This builds one
    table with a column of dates beside a column of numbers and asserts
    the numbers are the same whatever the dates do.
    """
    draw = random.Random(5)
    numbers = [f"{draw.uniform(0, 500):.2f}" for _ in range(600)]
    rows_early = [
        [day.isoformat(), numbers[place]]
        for place, day in enumerate(sorted(_uniform(random.Random(6), 600)))
    ]
    rows_late = [
        [day.isoformat(), numbers[place]]
        for place, day in enumerate(sorted(_seasonal(random.Random(7), 600)))
    ]
    written: "list[list[str]]" = []
    for name, rows in (("early", rows_early), ("late", rows_late)):
        folder = tmp_path / name
        folder.mkdir()
        table = folder / "real.csv"
        table.write_text(
            fixtures.rows_to_csv(["when", "amount"], rows),
            encoding="utf-8",
            newline="",
        )
        assert (
            _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"])
            == 0
        )
        assert (
            _exit_of(
                [
                    "generate",
                    str(folder / "real-profile.json"),
                    "--out-dir",
                    str(folder),
                    "--seed",
                    "4",
                    "--replace",
                ]
            )
            == 0
        )
        twin = (folder / "real-twin.csv").read_text(encoding="utf-8")
        written += [
            [row[1] for row in csv.reader(io.StringIO(twin))][1:]
        ]
    assert written[0] == written[1], (
        "the column of numbers beside the dates moved when only the dates' "
        "own shape changed, so the two columns are sharing words"
    )

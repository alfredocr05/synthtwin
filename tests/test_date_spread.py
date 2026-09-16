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
to 1.41 -- on columns whose shape eleven rungs can carry. On a column
whose values burst around a few onset dates it carries nothing and the
ratio stays near 0.15 to 0.47, which the repair pass of landing 2b.6
pinned here rather than leaving the sentence above unqualified.

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

AND A GAP'S TWO PINNED DAYS STOPPED TAKING A WHOLE DAY EACH (plan
P4-D130; review of 158c811, item 2). Every gap drew over `[low, high]`
inclusive, so a rung's day took a day's mass from the gap below it, a
day's from the gap above and the pin on top: 3,000 dates drawn uniformly
over sixty days, seed 4, came back with a per-day variance of 301.33
against the real column's 45.47 -- 6.63 times -- with 31 January at 91
values against 44, and both files validated. Each pin now stands at a
place inside its own day on the straightest count the pins allow, and
the gate for SHORT study spans below is what holds it. The bands above
were re-measured with it, and they moved DOWN on the shaped columns,
because part of what the withdrawn rule's ratios measured was those
spikes: over seeds 4, 7, 11 and 23, seasonal at 1,500 rows went from
0.605-0.680 to 0.516-0.572 and admissions from 0.712-0.781 to
0.675-0.749, while uniform at 3,000 rows went from 1.159-1.283 -- above
the real column's own variance, which no shape-free column has -- to
0.911-1.115.

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

# The band the repaired construction is held to. Measured over seeds 4,
# 7, 11 and 23 per shape and size, dates and midnight moments alike,
# once the pins were placed inside their days (plan P4-D130): uniform
# 1.020-1.284 at 400 and 0.936-1.117 at 1,500, seasonal 0.790-0.922 and
# 0.516-0.572, admissions 0.909-1.049 and 0.675-0.749. The floor is not a
# round number chosen for comfort -- the closest any measured case came
# to it is seasonal at 1,500 rows, at 0.516. It was 0.6 while a rung's
# day took a spike of its own, which is what lifted the shaped columns.
LOWEST = 0.5
HIGHEST = 1.6

# What a column whose shape is carried by the weekday is held to at
# 3,000 rows, where the evenly-filled gap cannot reach the band. The
# measured range there is 0.421 to 0.565 over seeds 4, 7 and 11 (0.524 to
# 0.617 while each rung's day carried a spike, plan P4-D130); the
# stratified construction before it reached 0.057 to 0.066 on the same
# columns, so this floor is still six times what that defect allowed and
# is a bound on the RESIDUAL, not a weakened form of the band above.
RESIDUAL_LOWEST = 0.38

# WHAT A COLUMN THE ELEVEN RUNGS DO CARRY REACHES AT 3,000 ROWS, which
# is what a shaped column there is SHORT of: uniform arrivals measured
# 0.911 to 1.115 over seeds 4, 7 and 11 (plan P4-D130).
CARRIED_LOWEST = 0.85

# THE SHORT STUDY SPAN (plan P4-D130). Uniform arrivals over a week to
# two months, measured against the variance a column of that many rows
# over that many days has in expectation, `rows / days * (1 - 1 / days)`,
# and at the busiest day any rung falls on, in standard units of that
# expectation. Measured over seeds 0, 4, 7 and 11: the repaired twin
# 0.16-0.95 and 0.29-2.97; the withdrawn inclusive draw 3.37-23.8 and
# 2.67-10.64. The real columns themselves measured 0.38-1.04.
SHORT_SPAN_VARIANCE = 1.5
SHORT_SPAN_PEAK = 4.0

# AND WHAT AN OUTBREAK COLUMN IS HELD TO, which nothing pinned until the
# repair pass of landing 2b.6 (skeptic finding 5). Where most values sit
# within a few days of three onset dates, the eleven published rungs
# cannot carry the shape at all: eleven pins over a year leave gaps
# weeks wide, and a gap is filled EVENLY. Measured on this construction
# -- three seeds at each size -- 0.335 to 0.466 at 400 rows and 0.150 to
# 0.182 at 1,500, against 0.402 to 0.449 and 0.187 to 0.284 on the
# commit before the repair: the repair neither helps nor harms this
# shape, and at 1,500 rows the two are the same to within noise. With
# the pins placed inside their days (plan P4-D130), 0.278 to 0.372 and
# 0.127 to 0.155. That is
# pinned rather than left out, because the landing's own sentences gave
# a repaired range of 0.52 to 1.41 with no qualification, and this is
# the shape that qualification is about. The remedy is a finer ladder or
# a value-count map over days, both of which publish observed dates, so
# both wait on the stage that sets the disclosure floor.
BURST_LOWEST = 0.10


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


def _burst(draw: "random.Random", count: int) -> "list[datetime.date]":
    """An outbreak: most values within a few days of three onset dates.

    The one common epidemiological shape where this construction does
    almost nothing, added by the repair pass of landing 2b.6 because the
    landing's own numbers were stated without it.
    """
    onsets = (
        datetime.date(2024, 2, 3),
        datetime.date(2024, 5, 19),
        datetime.date(2024, 9, 7),
    )
    found: "list[datetime.date]" = []
    for _place in range(count):
        if draw.random() < 0.6:
            start = draw.choice(onsets)
            found += [start + datetime.timedelta(days=int(abs(draw.gauss(0, 3))))]
        else:
            found += [
                datetime.date(2024, 1, 1)
                + datetime.timedelta(days=draw.randrange(0, 365))
            ]
    return found


SHAPES = {
    "uniform": _uniform,
    "seasonal": _seasonal,
    "admissions": _admissions,
    "burst": _burst,
}

# THE SHAPES THE BAND IS ASKED OF. `burst` is deliberately not among
# them: it has its own test below, held to its own measured range, for
# the reason that test gives. A shape is in `SHAPES` so that one
# measurement harness reaches all four.
BAND_SHAPES = ("admissions", "seasonal", "uniform")


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
@pytest.mark.parametrize("shape", sorted(BAND_SHAPES))
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
    assert CARRIED_LOWEST <= ratio <= HIGHEST, f"{shape} at 3000 rows: {ratio:.3f}"


@pytest.mark.parametrize("shape", ["seasonal", "admissions"])
def test_a_large_column_shaped_by_the_weekday_is_short_and_says_so(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """THE NAMED LIMIT, pinned so that closing it is a visible decision.

    At 3,000 rows most of a seasonal or admissions column's day-to-day
    variance is structure the description does not publish: which weekday
    a value falls on, and how the density moves WITHIN a gap between two
    published rungs. The gap is filled evenly, so the twin cannot reach
    it -- measured 0.421 to 0.565 against the 0.911 to 1.115 a column
    with no calendar shape reaches at the same size (plan P4-D130).

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
    assert ratio < CARRIED_LOWEST, (
        f"{shape} at 3000 rows now reaches {ratio:.3f}, which is inside the "
        f"band this test records it as SHORT of. If a landing carried the "
        f"weekday census or a finer ladder, this test and the report "
        f"sentence it guards are what should be rewritten -- and the plan's "
        f"residual closed -- rather than this assertion deleted."
    )


@pytest.mark.parametrize("rows", [400, 1500])
@pytest.mark.parametrize("seed", [4, 7])
def test_an_outbreak_column_is_short_of_the_band_and_says_so(
    tmp_path: pathlib.Path, rows: int, seed: int
) -> None:
    """THE SECOND NAMED LIMIT, and the shape the band's numbers are not about.

    Most values sit within a few days of three onset dates. Eleven
    published rungs over a year leave gaps weeks wide, a gap is filled
    evenly, and no pinning of the rungs changes that -- measured at
    0.335 to 0.466 at 400 rows and 0.150 to 0.182 at 1,500, against
    0.402 to 0.449 and 0.187 to 0.284 before the repair.

    It is asserted in both directions for the reason the weekday limit
    is: the number is what a later landing will move, and a change in
    either direction should show up as a failure rather than as nothing.
    The twin and the real table still validate with nothing missed, and
    every published rung is still exact -- what this column loses is
    structure no datetime block publishes, which the twin's own report
    names in its fourth clause.
    """
    ratio, missed = _measured(
        tmp_path / f"burst-{rows}-{seed}", "burst", rows, seed, False
    )
    assert not missed, missed
    assert BURST_LOWEST <= ratio < LOWEST, (
        f"a burst column at {rows} rows, seed {seed}, reaches {ratio:.3f}. "
        f"Below {BURST_LOWEST} the twin has lost ground this pass measured "
        f"it holding; at {LOWEST} or above it now meets the band, which "
        f"would mean a landing has carried the heaped days -- and then "
        f"this test, the report's fourth clause and the plan's residual "
        f"are what should be rewritten, not this assertion deleted."
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


def test_a_twin_written_one_day_early_is_missed_at_every_rung(
    tmp_path: pathlib.Path,
) -> None:
    """A PINNED RANK'S WINDOW IS A POINT, and this is the witness for it.

    Landing 2b.6 part 2 said in four sealed places that each of the nine
    interior rungs is now checked AT its published value rather than
    inside a band. The code did not do it: both writings of G12.4
    subtracted the reading allowance from every non-end rank, pinned or
    not, so a rung's window was `[published - 1 day, published]` on a
    column of dates -- and a twin with every interior cell moved one day
    EARLIER, which is precisely the defect that landing repaired, came
    back WITHIN-BOUND at all nine rungs.

    So the allowance is spent only where the rank has room to be drawn
    in, and this test is the reproduction that found it: build the
    admissions column, take the twin the generator writes, move every
    interior cell one day earlier, and require the check to name all
    nine. It is deliberately not a unit test of the window arithmetic --
    the two writings already compare rank by rank in
    `tests/test_p3v4f4_datetime_windows.py` -- but of what a person is
    told about a file.
    """
    draw = random.Random(4 * 7919 + 400)
    days = sorted(_admissions(draw, 400))
    folder = tmp_path / "early"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["when"], [[day.isoformat()] for day in days]),
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
                "4",
                "--replace",
            ]
        )
        == 0
    )
    written = [
        row[0]
        for row in csv.reader(
            io.StringIO(
                (folder / "real-twin.csv").read_text(encoding="utf-8")
            )
        )
    ][1:]
    block = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    first = datetime.date.fromisoformat(block["date_percentiles"]["min"])
    last = datetime.date.fromisoformat(block["date_percentiles"]["max"])
    moved: "list[str]" = []
    for cell in written:
        held = datetime.date.fromisoformat(cell)
        if held <= first + datetime.timedelta(days=1) or held == last:
            moved += [cell]
        else:
            moved += [(held - datetime.timedelta(days=1)).isoformat()]
    assert moved != written, "the shift must actually move some cell"
    early = folder / "early-twin.csv"
    early.write_text(
        fixtures.rows_to_csv(["when"], [[cell] for cell in moved]),
        encoding="utf-8",
        newline="",
    )
    checked = folder / "check"
    checked.mkdir()
    code = _exit_of(
        [
            "validate",
            str(described),
            "--twin",
            str(early),
            "--out-dir",
            str(checked),
            "--replace",
        ]
    )
    assert code == 3, "a twin written a day early must not pass the check"
    text = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted(checked.glob("*quality.txt"))
    )
    missed = [
        line
        for line in text.splitlines()
        if "date-ladder." in line and "MISSED" in line
    ]
    named = {line.split("date-ladder.")[1][0:3] for line in missed}
    assert named == {f"p{percent:02d}" for percent in INTERIOR}, sorted(named)


@pytest.mark.parametrize("resolution", ["month", "quarter"])
def test_the_report_of_a_column_of_periods_names_only_what_a_period_can_lose(
    tmp_path: pathlib.Path, resolution: str
) -> None:
    """The sentence is the one true OF THE COLUMN (repair pass of 2b.6).

    The note above names four things, two of which a column of months or
    quarters cannot have: a period has no weekday and no time of day. It
    was filed unchanged on every datetime column whatever its
    resolution, so a month column's report told a reader it had lost two
    things no column of months can lose. A column of periods takes the
    two-clause form instead.
    """
    draw = random.Random(21)
    if resolution == "month":
        cells = sorted(
            f"{2000 + draw.randrange(0, 24)}-{draw.randrange(1, 13):02d}"
            for _place in range(300)
        )
    else:
        cells = sorted(
            f"{2000 + draw.randrange(0, 24)}-Q{draw.randrange(1, 5)}"
            for _place in range(300)
        )
    folder = tmp_path / f"periods-{resolution}"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv([resolution], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"]) == 0
    described = folder / "real-profile.json"
    block = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    assert block["resolution"] == resolution, block["resolution"]
    assert (
        _exit_of(
            [
                "generate",
                str(described),
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
    assert "how these periods are spread across the calendar" in report
    for clause in (
        "periods that hold far more values than their neighbours",
        "a few scheduled periods",
    ):
        assert clause in report, f"the report no longer names: {clause}"
    for absent in (
        "which days of the week",
        "the time of day",
        "how these dates are spread across the calendar",
    ):
        assert absent not in report, (
            f"a column of {resolution}s has no {absent!r} to lose, and its "
            f"report "
            f"says it does"
        )


def test_a_column_beside_the_dates_is_untouched_by_this_rule(
    tmp_path: pathlib.Path,
) -> None:
    """The word budget is unchanged, so no other column's cells move.

    Each rank that is not pinned draws exactly one word and a pinned
    rank draws none, and the BUDGET is unchanged either way: the column
    is handed `P - 2` content words and the pins leave up to NINE of
    them unread, so a column of dates consumes exactly the allocation it
    always consumed. (The repair pass of landing 2b.6 amended this
    paragraph: it said a pinned rank draws its word and discards it, and
    a probe of the shipped code measured 389 words read of 398.) The
    stream of words is shared
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
    # THE ROWS ARE NOT LEFT SORTED BY DATE (the integration of landings
    # 2b.6 to 2b.10, 2026-09-16). Landing 2b.10 publishes the order a
    # file's rows stand in and the twin keeps it, so two tables sorted by
    # their dates put the numbers beside them in two different row
    # orders, and the columns compared below differed row by row while
    # holding the same cells. One fixed shuffle, the same for both
    # tables, leaves no order to publish, so what is compared is again
    # only whether the words the numbers draw moved.
    shuffle = list(range(600))
    random.Random(8).shuffle(shuffle)
    rows_early = [rows_early[place] for place in shuffle]
    rows_late = [rows_late[place] for place in shuffle]
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
        described = json.loads(
            (folder / "real-profile.json").read_text(encoding="utf-8")
        )
        assert described["source"]["dialect"]["row_order"] is None
        twin = (folder / "real-twin.csv").read_text(encoding="utf-8")
        written += [
            [row[1] for row in csv.reader(io.StringIO(twin))][1:]
        ]
    assert written[0] == written[1], (
        "the column of numbers beside the dates moved when only the dates' "
        "own shape changed, so the two columns are sharing words"
    )


def _inclusive_gaps(ladder: "list[int]", parsed: int, words: "list[int]") -> "list[int]":
    """G7.3 AS IT SHIPPED AT 158c811: every gap drawn over `[low, high]`.

    The withdrawn rule, restored for `REINSTATE=P4-D130`. It spends the
    same words on the same ranks, so it differs from the rule in force
    only in where a rank lands.
    """
    from synthtwin import generation

    ordinals = [0 for _rank in range(parsed)]
    if parsed <= 0:
        return ordinals
    pinned = generation._ordinal_pins(ladder, parsed)
    for rank in sorted(pinned):
        ordinals[rank] = pinned[rank]
    places = sorted(pinned)
    taken = 0
    for step in range(len(places) - 1):
        below, above = places[step], places[step + 1]
        low, high = ordinals[below], ordinals[above]
        drawn = []
        for _rank in range(below + 1, above):
            word = words[taken]
            taken += 1
            drawn.append(min(low + (word * (high - low + 1)) // 2**64, high))
        for place, value in enumerate(sorted(drawn)):
            ordinals[below + 1 + place] = value
    return ordinals


@pytest.fixture
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """`REINSTATE=P4-D130` puts the inclusive draw back, to see this go red."""
    import os

    from synthtwin import generation

    if os.environ.get("REINSTATE") == "P4-D130":
        monkeypatch.setattr(generation, "_spread_ordinals", _inclusive_gaps)


@pytest.mark.parametrize(
    "days, rows, seed",
    [(60, 3000, 4), (60, 3000, 0), (60, 3000, 11), (30, 1000, 7), (14, 3000, 4), (7, 500, 4)],
)
def test_a_short_study_span_puts_no_spike_on_a_published_rung(
    tmp_path: pathlib.Path, _reinstated: None, days: int, rows: int, seed: int
) -> None:
    """The reviewer's shape: uniform arrivals over a short span (P4-D130).

    `random.Random(34676)` draws each date's day inside the span, as the
    review did, and the column is round-tripped. The twin and the real
    table both validate with nothing missed, every rung is exact, the
    twin's per-day variance is no more than `SHORT_SPAN_VARIANCE` times
    what that many rows over that many days vary by in expectation, and
    no day a rung falls on holds more than `SHORT_SPAN_PEAK` standard
    units above the expected count. The withdrawn inclusive draw put
    that variance at 3.37 to 23.8 times and a rung's day at up to 10.6
    standard units.
    """
    import math

    draw = random.Random(34676)
    start = datetime.date(2025, 1, 1)
    chosen = sorted(
        start + datetime.timedelta(days=draw.randrange(days)) for _ in range(rows)
    )
    cells = [day.isoformat() for day in chosen]
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"short-{days}-{seed}", cells, str(seed)
    )
    assert (twin_exit, real_exit) == (0, 0)
    ordered = sorted(written)
    parsed = rows - first["n_unparsed"]
    for percent in INTERIOR:
        rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
        assert ordered[rank] == first["date_percentiles"][f"p{percent:02d}"]
    whole = [
        day.isoformat()
        for day in _span(chosen[0], chosen[-1])
    ]
    counts = _per_day(written, whole)
    span = len(whole)
    expected = rows / span
    ratio = statistics.pvariance(counts) / (expected * (1 - 1 / span))
    assert ratio <= SHORT_SPAN_VARIANCE, (
        f"{rows} dates over {span} days, seed {seed}: the twin's per-day "
        f"variance is {ratio:.2f} of what such a column varies by"
    )
    held = dict(zip(whole, counts))
    rungs = {first["date_percentiles"][f"p{percent:02d}"] for percent in INTERIOR}
    peak = max((held[day] - expected) / math.sqrt(expected) for day in rungs)
    assert peak <= SHORT_SPAN_PEAK, (
        f"{rows} dates over {span} days, seed {seed}: a published rung's "
        f"day holds {peak:.2f} standard units above the expected count"
    )


class _WordSpy(list):  # type: ignore[type-arg]
    """A word list that records the highest index the construction read."""

    high = -1

    def __getitem__(self, index):  # type: ignore[no-untyped-def]
        if index > self.high:
            self.high = index
        return list.__getitem__(self, index)


@pytest.mark.parametrize("parsed", [11, 12, 13, 60, 240, 400, 401, 1500])
def test_a_pinned_rank_spends_no_word_and_the_budget_is_unchanged(
    parsed: int,
) -> None:
    """THE RULE FIVE DOCUMENTS STATED WRONGLY, measured (landing 2b.14).

    Every one of them said that each rank between the ends spends
    exactly one word, a pinned rank included, because a pinned rank
    draws its word and discards it. The construction does no such thing:
    it takes a word only for the ranks strictly BETWEEN two pins. The
    repair pass of landing 2b.6 amended four of the five places after
    its reviewer measured 389 words read of 398; the plan was the fifth
    and still carried the withdrawn sentence, which landing 2b.14
    amended.

    Nothing was pinning either rule, which is why the two could drift
    apart at all -- the oracle mirrored the CODE while its own docstring
    stated the other rule, so no vector comparison could see it. This is
    that pin, and it states the rule in the form that makes it
    checkable: a column reads one word for every rank that is not
    pinned, so `read == parsed - (the number of DISTINCT pinned ranks)`.

    The budget is the half that matters for every other column, and it
    is asserted here too: the column is handed `parsed - 2` words
    whatever it does with them, so the words a pinned rank does not
    draw are simply left unread and no column generated afterwards
    moves.
    """
    from synthtwin import generation

    span = 365
    ladder = (
        [0]
        + [round(span * percent / 100) for percent in INTERIOR]
        + [span]
    )
    handed = max(parsed - 2, 0)
    words = _WordSpy(range(1, handed + 1))
    ordinals = generation._spread_ordinals(ladder, parsed, words)
    pins = generation._ordinal_pins(ladder, parsed)
    read = words.high + 1
    assert ordinals == sorted(ordinals), "the ranks must stay ascending"
    # ONE WORD PER UNPINNED RANK, AND NONE FOR A PINNED ONE.
    assert read == parsed - len(set(pins)), (
        f"{parsed} ranks over {len(set(pins))} distinct pins read {read} "
        f"words; the rule says one for each rank that is not pinned"
    )
    # ...AND THE BUDGET IS UNCHANGED, the surplus simply never read.
    assert read <= handed, (read, handed)
    assert handed - read == len(set(pins)) - 2, (
        f"{handed - read} words left unread against {len(set(pins))} "
        f"distinct pins: the two ends are not drawn for either way"
    )


def test_the_measured_word_spend_of_a_four_hundred_row_column() -> None:
    """The number the amended sentences carry, asserted as a number.

    A rule stated as arithmetic can be met by an implementation that
    pins nothing, so the headline measurement is pinned as itself: a
    400-row column with eleven distinct pins is handed 398 content words
    and reads 389 of them.
    """
    from synthtwin import generation

    span = 365
    ladder = (
        [0]
        + [round(span * percent / 100) for percent in INTERIOR]
        + [span]
    )
    words = _WordSpy(range(1, 399))
    generation._spread_ordinals(ladder, 400, words)
    assert len(set(generation._ordinal_pins(ladder, 400))) == 11
    assert words.high + 1 == 389, words.high + 1


@pytest.mark.parametrize(
    "parsed", [2, 3, 5, 11, 12, 13, 20, 60, 101, 240, 400, 401, 1500, 3000]
)
def test_the_pins_leave_at_most_nine_words_unread(parsed: int) -> None:
    """THE NUMBER THE AMENDED SENTENCE ITSELF CARRIED WAS WRONG.

    Landing 2b.14 rewrote the word-spend rule in five places and every
    one of them went on to say that the pins leave `up to eleven` of
    the handed words unread. The ceiling is NINE, and the code says so
    twice over: the published tail pins AT MOST ELEVEN RANKS -- the two
    ends and the nine interior rungs -- and neither end is ever drawn
    for, so the surplus a column leaves unread is the number of
    DISTINCT pinned ranks less two.

    Measured across the fourteen sizes below, the surplus runs 0, 1, 3,
    5, 6, 6, 6, 8 and then 9 from a hundred and one rows upward. It
    never reaches ten, at any size.

    This is the same class of defect the landing exists to close -- a
    written sentence that does not follow the code -- carried this time
    by the correction itself, which is why the ceiling is pinned here
    as a number rather than left to arithmetic that no reader checks.
    """
    from synthtwin import generation

    span = 365
    ladder = (
        [0]
        + [round(span * percent / 100) for percent in INTERIOR]
        + [span]
    )
    handed = max(parsed - 2, 0)
    words = _WordSpy(range(1, handed + 1))
    generation._spread_ordinals(ladder, parsed, words)
    pins = generation._ordinal_pins(ladder, parsed)
    read = words.high + 1
    unread = handed - read
    # WHERE THE ELEVEN COMES FROM, so a ladder that grew a rung cannot
    # leave this ceiling standing.
    assert len(generation._PCT) == 11, len(generation._PCT)
    assert len(set(pins)) <= 11, (
        f"{len(set(pins))} ranks pinned at {parsed} rows: the tail pins "
        f"the two ends and the nine interior rungs and no more"
    )
    # THE CEILING ITSELF.
    assert unread <= 9, (
        f"{unread} of the {handed} words handed to a {parsed}-row column "
        f"were left unread; the documents say at most nine"
    )
    assert unread == max(len(set(pins)) - 2, 0), (
        f"{unread} unread against {len(set(pins))} distinct pins: the "
        f"surplus is the pinned ranks less the two ends"
    )


def test_the_ceiling_of_nine_is_reached_and_not_merely_respected() -> None:
    """A ceiling nothing reaches would be met by a column pinning none.

    At a hundred and one rows and upward all eleven pinned ranks are
    distinct, so the surplus stands at exactly nine -- the number the
    method, the plan, the generator, the oracle and the gate all now
    carry.
    """
    from synthtwin import generation

    span = 365
    ladder = (
        [0]
        + [round(span * percent / 100) for percent in INTERIOR]
        + [span]
    )
    reached: "list[int]" = []
    for parsed in (101, 400, 1500, 3000):
        handed = parsed - 2
        words = _WordSpy(range(1, handed + 1))
        generation._spread_ordinals(ladder, parsed, words)
        reached += [handed - (words.high + 1)]
        assert len(set(generation._ordinal_pins(ladder, parsed))) == 11
    assert reached == [9, 9, 9, 9], reached

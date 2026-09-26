"""THE STAGE-3B GATE: dates keep their calendar shape, one clause per landing.

"Weekend share, hour of day and heaps come back; no calendar count below
the floor" is stage 3b's gate as the plan of record states it
(docs/STATE.md, line 3b). Each clause lands with the landing that makes
it true, and landing 3b.0 (plan P4-D354) makes the first one true:

* `test_every_day_filled` -- where a column of dates holds a value on
  EVERY day of its range, its twin holds every one of those days: the
  twin validates with nothing missed, holds as many different days (or
  seconds) as the real column, and its own report finds each published
  approximation inside its window. Before the landing a tail's tie group
  stood on ONE distance and its gap was that point, so the count pass
  could not split it: two years of admissions, 731 days, came back as
  730 at every seed, both distinct counts MISSED; billing dates as 729;
  300 days at a floor of 36 as 299. On moments the same loss was hidden:
  the twin bought the missing value back as a SPELLING -- one cell
  written with a mark the real column never used (method G7.9) -- so
  validation passed on 730 days. G7.3b step 9 lets the group give way.

THE BATTERY is built here, seeded and neutral, every shape filling
every unit of its range (asserted, not assumed): admissions, billing
dates heaped on the 1st and 15th, a short range, the admissions days
written as midnight moments, every second of ten minutes, and one
105-row column whose high tail's group stands one day off an empty unit.
Admissions and billing are also asked at floors 1 and 36.

AND ITS ORDER IS WITNESSED where no shape of the battery reaches it:
`test_the_low_tail_gives_way_first_on_a_tie` rewrites a mirrored
column's description one different value short, so the step takes one of
two tied offers and must take the low tail's.

AND THE WINDOW IS WRITTEN TWICE. G12.14's summed window -- a group's
ranks as near as one and as far as its reach where step 9 may move
them -- is the generator's (`_tail_sum_bounds`, which its report reads)
and the validator's (`_date_tail_windows(..., summed=True)`), and
`test_the_two_writings_of_the_summed_window_agree` holds them equal,
rank for rank, on every description of the battery.

THE MUTATIONS, each run on this file (plan P4-D354): the step withdrawn
(the group's gap left a point) turns red the four shapes that MISSED
and the two that hid it; the validator's summed window left at the
strata turns red on `tails.low.mean_distance` of admissions; the
report's window left at the strata turns red on the approximations; the
validator's inner ranks summed one unit further out turns the agreement
red; the high tail offered first on a tie turns
`test_the_low_tail_gives_way_first_on_a_tie` red; and the frozen case
`every_day_group` of tests/test_generation_reference.py turns red on the
step withdrawn and on the inner units handed out largest first.
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import contract, generation, rendering, validation

SEEDS = (0, 1, 2, 3, 4)

_WEEKDAY = (1.45, 1.20, 1.15, 1.10, 1.10, 0.55, 0.50)
_TWO_YEARS = [
    datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)
]


def _admission_days(rows: int, seed: int) -> "list[datetime.date]":
    """Two years of days, Monday heaviest and the weekend lightest, a winter season."""
    draw = random.Random(seed)
    weights = [
        _WEEKDAY[day.weekday()] * (1.0 + 0.25 * math.cos(2 * math.pi * (day.month - 1) / 12))
        for day in _TWO_YEARS
    ]
    return draw.choices(_TWO_YEARS, weights=weights, k=rows)


def _admissions() -> "tuple[str, list[str], int]":
    cells = [day.isoformat() for day in _admission_days(10000, 17000)]
    return "admission_date", cells, 731


def _billing() -> "tuple[str, list[str], int]":
    """Two years of billing days, four in ten on the 1st or the 15th of a month."""
    draw = random.Random(18001)
    cells: "list[str]" = []
    for _row in range(10000):
        day = draw.choice(_TWO_YEARS)
        if draw.random() < 0.40:
            day = datetime.date(day.year, day.month, draw.choice((1, 15)))
        cells += [day.isoformat()]
    return "billing_date", cells, 731


def _short_range() -> "tuple[str, list[str], int]":
    """300 days from 2024-01-01, weighted by weekday."""
    draw = random.Random(23000)
    days = [datetime.date(2024, 1, 1) + datetime.timedelta(days=step) for step in range(300)]
    weights = [_WEEKDAY[day.weekday()] for day in days]
    return "seen_on", [day.isoformat() for day in draw.choices(days, weights=weights, k=10000)], 300


def _midnight_moments() -> "tuple[str, list[str], int]":
    """The admission days written as moments at midnight."""
    cells = [f"{day.isoformat()} 00:00:00" for day in _admission_days(10000, 17000)]
    return "admitted_at", cells, 731


def _every_second() -> "tuple[str, list[str], int]":
    """Ten minutes from 08:00:00, every second held, busiest four minutes in."""
    draw = random.Random(21000)
    start = datetime.datetime(2024, 3, 4, 8, 0, 0)
    cells: "list[str]" = []
    for _row in range(10000):
        second = draw.randrange(600)
        if draw.random() >= 0.7:
            second = min(599, int(draw.triangular(0, 600, 240)))
        cells += [(start + datetime.timedelta(seconds=second)).strftime("%Y-%m-%dT%H:%M:%S")]
    return "read_at", cells, 600


# How many cells each of 23 days from 2024-05-06 holds. The high tail
# beyond 2024-05-24 holds 1, 5, 6 and 1 cells one to four days out, and
# its group of three ranks stands two days out, one day off the day one
# real cell holds.
_SMALL_COUNTS = (
    8, 6, 4, 1, 8, 3, 4, 6, 5, 5, 5, 4, 3, 4, 5, 3, 6, 6, 6, 1, 5, 6, 1,
)


def _small_tail_group() -> "tuple[str, list[str], int]":
    cells: "list[str]" = []
    for step in range(len(_SMALL_COUNTS)):
        day = datetime.date(2024, 5, 6) + datetime.timedelta(days=step)
        cells += [day.isoformat()] * _SMALL_COUNTS[step]
    return "seen_on", cells, len(_SMALL_COUNTS)


_BUILDERS = {
    "admissions": _admissions,
    "billing": _billing,
    "short_range": _short_range,
    "midnight_moments": _midnight_moments,
    "every_second": _every_second,
    "small_tail_group": _small_tail_group,
}

# Each shape at the floor its base twin fell short at, and the two
# two-year shapes at the other two floors the landing was measured at.
EVERY_DAY_CASES = (
    ("admissions", 11),
    ("billing", 11),
    ("short_range", 36),
    ("midnight_moments", 11),
    ("every_second", 11),
    ("small_tail_group", 11),
    ("admissions", 1),
    ("admissions", 36),
    ("billing", 1),
    ("billing", 36),
)


def _unit(cell: str) -> str:
    """The unit a cell holds: its day, or its day and clock with the mark between them dropped."""
    return cell[:10] + cell[11:]


@pytest.mark.parametrize(
    "shape,floor", EVERY_DAY_CASES, ids=[f"{shape}-{floor}" for shape, floor in EVERY_DAY_CASES]
)
def test_every_day_filled(tmp_path: pathlib.Path, shape: str, floor: int) -> None:
    """Every day of the range filled comes back as every day, at seeds 0 to 4."""
    name, cells, span = _BUILDERS[shape]()
    real = {_unit(cell) for cell in cells}
    assert len(real) == span, (
        f"{shape}: the table holds {len(real)} of the {span} units of its "
        f"range, so it no longer witnesses a range filled on every unit"
    )
    text = name + "\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, f"{shape}-{floor}", text, floor)
    for seed in SEEDS:
        twin = generation.generate(described.loaded, seed)
        written = rendering.twin_csv(twin)
        missed = kpi_shapes.missed(kpi_shapes.measure(described, written, f"twin-{seed}.csv"))
        assert missed == [], f"{shape} at floor {floor}, seed {seed}: {missed}"
        held = {_unit(line) for line in written.splitlines()[1:] if line}
        assert len(held) == span, (
            f"{shape} at floor {floor}, seed {seed}: the twin holds {len(held)} "
            f"different units where the real column holds all {span}"
        )
        outside = sorted(
            approximation.fact
            for approximation in twin.approximations
            if not approximation.inside
        )
        assert outside == [], f"{shape} at floor {floor}, seed {seed}: {outside}"


@pytest.mark.parametrize(
    "shape,floor", EVERY_DAY_CASES, ids=[f"{shape}-{floor}" for shape, floor in EVERY_DAY_CASES]
)
def test_the_two_writings_of_the_summed_window_agree(
    tmp_path: pathlib.Path, shape: str, floor: int
) -> None:
    """G12.14's summed window, the generator's and the validator's, rank for rank."""
    name, cells, _span = _BUILDERS[shape]()
    text = name + "\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, f"{shape}-{floor}", text, floor)
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    parsed = column.n_present - facts.n_unparsed
    layout = generation._date_layout(column, facts, parsed, floor)
    counted = contract.datetime_counts_reachable(column)
    mine = validation._date_tail_windows(column, facts, floor, "", True)
    for side, plan in (("low", layout.low), ("high", layout.high)):
        assert plan is not None, side
        if plan.shape is None:
            assert side not in mine, side
            continue
        near, far = generation._tail_sum_bounds(plan, counted)
        assert mine[side] == (near, far), f"{shape} at floor {floor}, {side} tail"


def test_the_summed_window_is_wider_than_the_strata_somewhere(tmp_path: pathlib.Path) -> None:
    """The agreement above is not vacuous: the admissions' low tail group is widened."""
    name, cells, _span = _admissions()
    text = name + "\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, "admissions", text, 11)
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert contract.datetime_counts_reachable(column)
    layout = generation._date_layout(column, facts, column.n_present, 11)
    assert layout.low is not None and layout.low.shape is not None
    near, far = generation._tail_sum_bounds(layout.low, True)
    assert (near, far) != (list(layout.low.near), list(layout.low.far))


# A column mirrored about its middle day: its two tails publish one pair,
# and each loses the day one unit beyond its boundary, so their offers tie.
_MIRRORED_COUNTS = (
    1, 7, 11, 4, 6, 4, 2, 7, 6, 3, 3, 3, 6, 7, 2, 4, 6, 4, 11, 7, 1,
)


def test_the_low_tail_gives_way_first_on_a_tie(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9's order: at one distance from both groups, the low tail's unit first.

    The mirrored column's description is rewritten one different value
    short, so the step takes one of the two tied offers, and it is the low
    tail's: the day one unit below the low boundary is written and the day
    one unit above the high boundary is not.
    """
    cells: "list[str]" = []
    for step in range(len(_MIRRORED_COUNTS)):
        day = datetime.date(2024, 5, 6) + datetime.timedelta(days=step)
        cells += [day.isoformat()] * _MIRRORED_COUNTS[step]
    text = "seen_on\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, "mirrored", text, 11)
    block = described.document["columns"][0]
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    shorter = dict(described.document)
    shorter["columns"] = [
        dict(
            block,
            n_distinct=block["n_distinct"] - 1,
            n_distinct_folded=block["n_distinct_folded"] - 1,
        )
    ]
    loaded = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "shorter-profile.json", shorter))
    )
    below = datetime.date.fromisoformat(block["low_tail"]["boundary"]) - datetime.timedelta(days=1)
    above = datetime.date.fromisoformat(block["high_tail"]["boundary"]) + datetime.timedelta(days=1)
    for seed in SEEDS:
        written = set(rendering.twin_csv(generation.generate(loaded, seed)).splitlines()[1:])
        assert len(written) == block["n_distinct"] - 1, seed
        assert below.isoformat() in written and above.isoformat() not in written, seed

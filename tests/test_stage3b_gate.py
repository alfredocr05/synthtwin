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

AND EACH CLAUSE OF THE STEP IS WITNESSED where no shape of the battery
reaches it, most of them on a description rewritten to ask for fewer
or more different values than the real column held -- one the loader
accepts and no producer writes:

* `test_the_low_tail_gives_way_first_on_a_tie` -- a mirrored column one
  value short, so the step takes one of two tied offers: the low tail's;
* `test_the_offers_are_taken_nearest_the_group_first` -- the frozen
  case's column one to four values short, so the step takes the first
  offers in the method's order, which this test derives: nearest the
  group's own distance, then the smaller distance, then the low tail;
* `test_no_unit_an_absent_spelling_names_is_offered` -- a day the run
  names as holding no value, two days inside a tail's reach;
* `test_the_ranks_stay_in_order` -- the same column, whose low tail
  gives two ranks outside its group, the larger distance to the outer;
* `test_a_group_keeps_one_rank` -- a tail of twelve cells, so a group
  of two ranks, asked for more values than it can give;
* `test_no_rank_is_moved_onto_a_midnight` -- seconds whose high tail's
  reach holds a midnight no cell held.

Two bounds of the step have no witness, because no description found
reaches them: the reach itself and the width-kind half of the standing
clause (method G7.3b step 9).

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
`test_the_low_tail_gives_way_first_on_a_tie` red; the outer unit taken
before the inner at one remove, the smallest distance taken first, and
the inner unit of each tail taken before any outer one each turn
`test_the_offers_are_taken_nearest_the_group_first` red; an absent
spelling's unit offered, the outer units handed out smallest first to
the outermost ranks, every rank of a group given away, and a unit of
another midnight standing offered each turn their own witness red; and
the frozen case `every_day_group` of tests/test_generation_reference.py
turns red on the step withdrawn and on the inner units handed out
largest first.
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random

import pytest

import fixtures
import kpi_shapes
from synthtwin import contract, generation, profile, reading, rendering, taxonomy, validation

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


def _cells_of(counts: "tuple[int, ...]", start: datetime.date) -> "list[str]":
    """``counts[i]`` cells of the day ``i`` days after ``start``, in order."""
    cells: "list[str]" = []
    for step in range(len(counts)):
        day = start + datetime.timedelta(days=step)
        cells += [day.isoformat()] * counts[step]
    return cells


def _recounted(
    tmp_path: pathlib.Path, document: dict, name: str, by: int
) -> contract.Profile:
    """The one-column description with both its counts of different values moved by ``by``, loaded."""
    block = document["columns"][0]
    rewritten = dict(document)
    rewritten["columns"] = [
        dict(
            block,
            n_distinct=block["n_distinct"] + by,
            n_distinct_folded=block["n_distinct_folded"] + by,
        )
    ]
    return contract.load_profile(
        str(fixtures.write_profile(tmp_path, f"{name}-profile.json", rewritten))
    )


def _written(loaded: contract.Profile, seed: int) -> "set[str]":
    """Every different cell the twin of a one-column description writes at ``seed``."""
    return set(rendering.twin_csv(generation.generate(loaded, seed)).splitlines()[1:])


def _layout(loaded: contract.Profile, floor: int) -> "generation._DateLayout":
    column = loaded.columns[0]
    assert isinstance(column.facts, contract.DatetimeFacts)
    return generation._date_layout(
        column, column.facts, column.n_present - column.facts.n_unparsed, floor
    )


# THE FROZEN CASE `every_day_group`'s COLUMN (tests/test_generation_reference.py):
# 105 dates on every one of 22 days from 2024-05-06. At a floor of eleven
# its low tail's group stands three days out and reaches five, its high
# tail's two days out and reaching three.
_EVERY_DAY_GROUP_COUNTS = (
    5, 4, 1, 6, 9, 2, 4, 7, 6, 2, 7, 7, 5, 5, 3, 2, 9, 7, 1, 1, 11, 1,
)
_EVERY_DAY_GROUP_START = datetime.date(2024, 5, 6)


def test_the_offers_are_taken_nearest_the_group_first(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9's order: by remove from `g`, then the smaller distance, then the low tail.

    The frozen case's column with its counts of different values lowered
    by four: the count pass leaves its twin 18 of the 22 days, so the
    step has nothing to give, and the four days that twin lacks are the
    units the step offers. Lowered by three, two and one, the step gives
    one, two and three of them, so the twin lacks the rest -- which the
    method's order decides, and which is derived here from the order and
    not read off a twin. The column parts that order from the three it
    rules out, which is asserted, so each of them turns this red: the
    inner unit of each tail before any outer one, the outer unit before
    the inner at one remove, and the smallest distance first.
    """
    cells = _cells_of(_EVERY_DAY_GROUP_COUNTS, _EVERY_DAY_GROUP_START)
    text = "seen_on\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, "every_day_group", text, 11)
    block = described.document["columns"][0]
    layout = _layout(described.loaded, 11)
    assert layout.low is not None and layout.low.shape is not None
    assert layout.high is not None and layout.high.shape is not None
    low = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    high = datetime.date.fromisoformat(block["high_tail"]["boundary"])
    groups = (layout.low.shape.group, layout.high.shape.group)

    def place(day: str) -> "tuple[int, int, int]":
        """A free day's side, its distance from its boundary and its group's distance."""
        on = datetime.date.fromisoformat(day)
        assert on < low or on > high, f"{day} is no tail's unit"
        side = 0 if on < low else 1
        distance = (low - on).days if side == 0 else (on - high).days
        return (side, distance, groups[side])

    def method(day: str) -> "tuple[int, int, int]":
        side, distance, group = place(day)
        return (abs(distance - group), distance, side)

    def inner_first(day: str) -> "tuple[int, int, int]":
        side, distance, group = place(day)
        return (abs(distance - group), 0 if distance < group else 1, side)

    def outer_first(day: str) -> "tuple[int, int, int]":
        side, distance, group = place(day)
        return (abs(distance - group), -distance, side)

    def smallest_first(day: str) -> "tuple[int, int]":
        side, distance, _group = place(day)
        return (distance, side)

    real = set(cells)
    lowered = [_recounted(tmp_path, described.document, f"lowered-{by}", -by) for by in (0, 1, 2, 3, 4)]
    for seed in SEEDS:
        free = real - _written(lowered[4], seed)
        assert len(free) == 4, (seed, sorted(free))
        order = sorted(free, key=method)
        for ruled_out in (inner_first, outer_first, smallest_first):
            other = sorted(free, key=ruled_out)
            assert any(set(other[:given]) != set(order[:given]) for given in (1, 2, 3)), (
                f"seed {seed}: the column does not part the method's order from "
                f"{ruled_out.__name__}"
            )
        for given in (1, 2, 3):
            lacks = real - _written(lowered[4 - given], seed)
            assert lacks == set(order[given:]), (
                f"seed {seed}, {given} given: the twin lacks {sorted(lacks)} where "
                f"the order leaves {sorted(order[given:])}"
            )


# The same column with 2024-05-12 named as holding no value: its four cells
# and twelve more are written with that spelling, so the description
# publishes it among the absent cells, and the low tail's boundary moves to
# 2024-05-14 -- the absent day two units out, inside the group's reach.
_ABSENT_DAY = "2024-05-12"


def _with_an_absent_day(tmp_path: pathlib.Path) -> kpi_shapes.Described:
    cells = _cells_of(_EVERY_DAY_GROUP_COUNTS, _EVERY_DAY_GROUP_START) + [_ABSENT_DAY] * 12
    table = fixtures.write(tmp_path, "absent_day.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=(_ABSENT_DAY,))
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=11), settings, [], [], []
    )
    written = fixtures.write_profile(tmp_path, "absent_day-profile.json", document)
    return kpi_shapes.Described(tmp_path, table, document, contract.load_profile(str(written)))


def test_no_unit_an_absent_spelling_names_is_offered(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9 offers no unit a column's absent spelling names.

    The absent day stands inside the low group's reach and holds no rank
    once the count pass is done. Offered, a group rank moved onto it is
    written as a cell the description reads as absent, so the twin comes
    back a day short with both distinct counts MISSED; not offered, the
    step takes the next units and the twin holds every day the real
    column holds, at every seed.
    """
    described = _with_an_absent_day(tmp_path)
    block = described.document["columns"][0]
    assert block["missing_by_source"] == {_ABSENT_DAY: 16}
    layout = _layout(described.loaded, 11)
    assert layout.low is not None and layout.low.shape is not None
    boundary = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    away = (boundary - datetime.date.fromisoformat(_ABSENT_DAY)).days
    shape = layout.low.shape
    assert 1 <= away <= generation._group_reach(shape) and away != shape.group
    real = set(_cells_of(_EVERY_DAY_GROUP_COUNTS, _EVERY_DAY_GROUP_START)) - {_ABSENT_DAY}
    for seed in SEEDS:
        text = kpi_shapes.twin_text(described, seed)
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"absent-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"
        held = set(text.splitlines()[1:]) - {"", _ABSENT_DAY}
        assert held == real, f"seed {seed}: {sorted(real ^ held)}"


def test_the_ranks_stay_in_order(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3b step 9 keeps the ranks in order: the larger distance to the outer rank.

    On the column with the absent day the low tail's group gives two
    ranks to units outside its own distance; the one further out goes to
    the outermost group rank, so every rank still stands at or beyond the
    rank inside it. The twin's cells are written in a shuffled order, so
    the ranks are read where the step leaves them.
    """
    described = _with_an_absent_day(tmp_path)
    shipped = generation._group_gives_way
    seen: "dict[int, tuple[generation._DateLayout, list[int], list[int]]]" = {}

    def watched(
        column: object,
        facts: object,
        layout: "generation._DateLayout",
        moved: "list[int]",
        *rest: object,
    ) -> None:
        before = list(moved)
        shipped(column, facts, layout, moved, *rest)
        seen[len(seen)] = (layout, before, list(moved))

    monkeypatch.setattr(generation, "_group_gives_way", watched)
    for seed in SEEDS:
        seen.clear()
        generation.generate(described.loaded, seed)
        assert len(seen) == 1, seed
        layout, before, after = seen[0]
        assert after == sorted(after), f"seed {seed}: a rank passes another"
        plan = layout.low
        assert plan is not None and plan.shape is not None
        outward = [
            rank
            for rank in range(len(after))
            if after[rank] != before[rank]
            and (plan.anchor - after[rank]) // plan.unit > plan.shape.group
        ]
        assert len(outward) == 2, f"seed {seed}: {len(outward)} ranks given outside the group"


# A body of twenty days, six cells each, four empty days, then twelve cells
# on three days: at a floor of eleven the high tail is those twelve, so its
# group holds two ranks and may give one, four days out with a reach of five.
_CLUSTER_COUNTS = (6,) * 20 + (0, 0, 0, 0, 8, 1, 3)


def test_a_group_keeps_one_rank(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9: each group keeps one rank, so its own day is still written.

    The description asks for three more different days than the real
    column held, which no twin of this tail can reach, so the step is
    still short when the high group has given its one spare rank. It
    stops there: the group's own day, four days out, is written at every
    seed. Here the drawn ranks stand past that day, so a group that gave
    its last rank would empty it and gain nothing; and the window of
    G12.14 is summed with one rank kept.
    """
    cells = _cells_of(_CLUSTER_COUNTS, datetime.date(2024, 5, 6))
    text = "seen_on\n" + "".join(f"{cell}\n" for cell in cells if cell)
    described = kpi_shapes.describe(tmp_path, "cluster", text, 11)
    block = described.document["columns"][0]
    layout = _layout(described.loaded, 11)
    plan = layout.high
    assert plan is not None and plan.shape is not None
    shape = plan.shape
    spare = plan.rows - max(shape.grouped, 1) - 1
    assert spare == 1 and generation._group_reach(shape) - 1 > spare
    own = datetime.date.fromisoformat(block["high_tail"]["boundary"]) + datetime.timedelta(
        days=shape.group
    )
    raised = _recounted(tmp_path, described.document, "raised", 3)
    for seed in SEEDS:
        written = _written(raised, seed)
        assert len(written) < block["n_distinct"] + 3, seed
        assert own.isoformat() in written, f"seed {seed}: the group's own day is empty"


# Seconds from 23:59:14 to 00:00:06 of the next day, every one of them held
# but the midnight itself. At a floor of eleven the high tail's boundary is
# 23:59:59 and its group stands two seconds out, so its reach holds the
# free midnight one second out.
_ACROSS_MIDNIGHT_COUNTS = (
    11, 9, 4, 7, 7, 2, 12, 4, 11, 13, 6, 5, 14, 7, 8, 6, 7, 11, 7, 4, 4, 8,
    8, 5, 5, 4, 6, 6, 3, 4, 9, 4, 6, 7, 4, 3, 4, 9, 6, 5, 6, 4, 4, 3, 1, 3,
    0, 4, 2, 2, 2, 2, 2,
)


def test_no_rank_is_moved_onto_a_midnight(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9 offers a group no unit of another midnight standing.

    The description asks for one more different second than the real
    column held, so the step is short and the midnight in the high
    group's reach holds no rank. It is not offered, because the group
    stands off midnight, and the twin writes as many cells at midnight
    as it writes where the step has nothing to do: none.
    """
    start = datetime.datetime(2024, 3, 4, 23, 59, 14)
    cells: "list[str]" = []
    for step in range(len(_ACROSS_MIDNIGHT_COUNTS)):
        moment = start + datetime.timedelta(seconds=step)
        cells += [moment.strftime("%Y-%m-%d %H:%M:%S")] * _ACROSS_MIDNIGHT_COUNTS[step]
    text = "read_at\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, "across_midnight", text, 11)
    block = described.document["columns"][0]
    assert block["high_tail"]["boundary"] == "2024-03-04 23:59:59"
    layout = _layout(described.loaded, 11)
    plan = layout.high
    assert plan is not None and plan.shape is not None
    assert plan.shape.group > 1 and generation._group_reach(plan.shape) > 1
    raised = _recounted(tmp_path, described.document, "raised", 1)

    def at_midnight(written: "set[str]") -> int:
        return len([cell for cell in written if cell[11:19] == "00:00:00"])

    for seed in SEEDS:
        assert at_midnight(_written(described.loaded, seed)) == 0, seed
        assert at_midnight(_written(raised, seed)) == 0, f"seed {seed}: a rank moved onto midnight"

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

AND A MERGED RUN KEEPS EVERY RANK INSIDE ITS GAP (the landing's fix
pass): `test_a_merged_run_keeps_every_rank_inside_its_gap` holds G7.3's
merges to the gap of every rank of a run, on the random column that
missed its low tail's spread when they asked the run's first rank alone;
`test_a_run_no_merge_can_take_is_split` holds the split of a run whose
room is its own day, on the small dense column that then missed its
counts; and `test_the_count_is_met_where_a_chain_of_runs_reaches_it`
holds the stack of the ranks afresh where no one run can give a unit up,
on the two columns of the fourth skeptic whose tail pairs on alternate
days could give a day up only as a chain.

AND THE WINDOW IS WRITTEN TWICE. G12.14's summed window -- a group's
ranks as near as one and as far as its reach where step 9 may move
them -- is the generator's (`_tail_sum_bounds`, which its report reads)
and the validator's (`_date_tail_windows(..., summed=True)`), and
`test_the_two_writings_of_the_summed_window_agree` holds them equal,
rank for rank, on every description of the battery. Both widen only
where the distinct count is reachable, and
`test_the_window_is_summed_wider_only_where_the_count_is_reachable`
holds that on a column whose two marks make it unreachable: its windows
are the strata, and a file two units past them MISSES its mean.

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
largest first. And the validator's window widened where the count is
not reachable turns the reachable-count witness red, its file WITHIN
where it MISSES; the report's window widened there turns it red on the
report's bounds (the second skeptic of the landing, 2026-09-26, found
that condition witnessed nowhere, the whole suite green without it).
The count pass asking a merged run's room of its first rank alone turns
the gapped year red at seed 3, three ranks outside their gaps.
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


def test_the_window_is_summed_wider_only_where_the_count_is_reachable(
    tmp_path: pathlib.Path,
) -> None:
    """G12.14 sums a group wider only where the distinct count is reachable.

    The frozen case's column written as midnight moments, every other cell
    marked with `T` and the rest with a space: the census publishes both
    marks, so one instant has two spellings, the count of different values
    is not reachable (contract `datetime_counts_reachable`) and step 9
    never runs. Its groups could give way were it reachable, so the summed
    window would move -- and must not: the validator's and the report's
    windows are the strata. A file whose low tail stands two units past
    the strata's furthest sum, inside the widened one, MISSES its mean.
    """
    cells = _cells_of(_EVERY_DAY_GROUP_COUNTS, _EVERY_DAY_GROUP_START)
    marked = [f"{cell}{'T' if place % 2 else ' '}00:00:00" for place, cell in enumerate(cells)]
    described = kpi_shapes.describe(
        tmp_path, "two_marks", "seen_at\n" + "".join(f"{cell}\n" for cell in marked), 11
    )
    block = described.document["columns"][0]
    assert sorted(block["datetime_separators"]) == ["space", "upper_t"]
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert not contract.datetime_counts_reachable(column)
    layout = _layout(described.loaded, 11)
    summed = validation._date_tail_windows(column, facts, 11, "", True)
    records = {record.fact: record for record in generation.generate(described.loaded, 0).approximations}
    for side, plan in (("low", layout.low), ("high", layout.high)):
        assert plan is not None and plan.shape is not None, side
        strata = (list(plan.near), list(plan.far))
        assert generation._tail_sum_bounds(plan, True) != strata, f"{side}: nothing to widen"
        assert summed[side] == strata, f"{side}: the validator widened an unreachable count"
        record = records[f"{side}_tail.mean_distance"]
        assert (record.lowest, record.highest) == (
            generation._bound_figure(sum(strata[0]) / plan.rows),
            generation._bound_figure(sum(strata[1]) / plan.rows),
        ), f"{side}: the report widened an unreachable count"
    plan = layout.low
    assert plan is not None and plan.shape is not None
    distances = list(plan.far)
    distances[plan.shape.grouped] += 1
    distances[plan.shape.grouped + 1] += 1
    assert sum(plan.far) < sum(distances) <= sum(generation._tail_sum_bounds(plan, True)[1])
    boundary = datetime.date.fromisoformat(block["low_tail"]["boundary"][:10])
    lines = kpi_shapes.twin_text(described, 0).splitlines()
    beyond = [place for place in range(1, len(lines)) if lines[place] and lines[place][:10] < boundary.isoformat()]
    assert len(beyond) == plan.rows
    for place, distance in zip(beyond, distances):
        lines[place] = (boundary - datetime.timedelta(days=distance)).isoformat() + lines[place][10:]
    outcome = kpi_shapes.measure(described, "\n".join(lines) + "\n", "past_the_strata.csv")
    verdicts = {check.subcheck: check.verdict for check in outcome.checks}
    assert verdicts["tails.low.mean_distance"] == validation.MISSED


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


def _gapped_year() -> "tuple[list[str], int]":
    """392 days from a seeded start, a fifth of them empty and the first and
    last twenty all but empty, 2,469 dates, described at a floor of 36.

    Drawn exactly as the landing's second skeptic drew its random column
    40, so the column is the one that measured the defect.
    """
    draw = random.Random(900040)
    assert draw.choice(["date", "date", "date", "second", "minute", "usdate"]) == "date"
    span = draw.randint(12, 400)
    rows = min(max(100, draw.randint(span // 2, span * 12)), 6000)
    empty = draw.choice([0.0, 0.0, 0.05, 0.2])
    light = draw.random() < 0.3
    assert (span, rows, empty, light) == (392, 2469, 0.2, True)
    weights: "list[float]" = []
    for step in range(span):
        weight = 0.0 if draw.random() < empty else draw.random() + 0.1
        if step < span // 20 + 1 or step >= span - span // 20 - 1:
            weight = weight * 0.02
        weights += [weight]
    steps = draw.choices(range(span), weights=weights, k=rows)
    if draw.random() < 0.5:
        steps = list(range(span)) + steps[: rows - span]
    start = datetime.date(2020, 1, 1) + datetime.timedelta(days=draw.randint(0, 900))
    cells = [(start + datetime.timedelta(days=step)).isoformat() for step in steps]
    draw.shuffle(cells)
    floor = draw.choice([1, 5, 11, 11, 20, 36])
    assert floor == 36
    return cells, floor


def _settled_off_their_gaps(
    described: kpi_shapes.Described, seeds: "tuple[int, ...]", monkeypatch: pytest.MonkeyPatch
) -> "list[tuple[list[int], str]]":
    """Per seed, the ranks the count pass leaves outside their gaps, and the twin.

    A tail group's ranks are left out: step 9 alone may move those.
    """
    shipped = generation._units_settled
    seen: "list[tuple[list[int], list[int], list[int], generation._DateLayout | None]]" = []

    def watched(
        column: contract.ColumnBlock,
        facts: contract.DatetimeFacts,
        ordinals: "list[int]",
        parsed: int,
        whole: "list[bool]",
        lows: "list[int]",
        highs: "list[int]",
        small: int,
        layout: "generation._DateLayout | None" = None,
    ) -> "list[int]":
        moved = shipped(column, facts, ordinals, parsed, whole, lows, highs, small, layout)
        seen[:] = [(list(moved), list(lows), list(highs), layout)]
        return moved

    monkeypatch.setattr(generation, "_units_settled", watched)
    found: "list[tuple[list[int], str]]" = []
    for seed in seeds:
        text = kpi_shapes.twin_text(described, seed)
        assert len(seen) == 1, seed
        moved, lows, highs, layout = seen[0]
        assert layout is not None
        group: "set[int]" = set()
        for plan in (layout.low, layout.high):
            assert plan is not None and plan.shape is not None
            for index in range(max(plan.shape.grouped, 1), plan.rows):
                group.add(generation._tail_rank_of(plan, len(moved), index))
        off = [
            rank
            for rank in range(len(moved))
            if rank not in group and not lows[rank] <= moved[rank] <= highs[rank]
        ]
        found += [(off, text)]
    return found


def test_a_merged_run_keeps_every_rank_inside_its_gap(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """G7.3's merges move a run whole only where EVERY rank of it may go.

    The count pass merges a run of ranks on one day onto a day ranks
    already hold, and asked the run's FIRST rank alone whether that day
    lay inside its gap. A tail rank's gap is its own stratum (G7.3b step
    8), so the rest of a tail run went past theirs: on this column two
    low-tail ranks stood a day outside their strata and the tail's
    root-mean-square distance came out 5.063 against a window of 4.747 to
    5.057, MISSED at seeds 3 and 8 while the real table passed (plan
    P4-D354, the fix pass of landing 3b.0). Here every rank but a tail
    group's -- which step 9 alone may move -- stands inside its gap once
    the count pass is done, and the twin misses nothing.
    """
    cells, floor = _gapped_year()
    described = kpi_shapes.describe(
        tmp_path, "gapped_year", "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    settled = _settled_off_their_gaps(described, (3, 8), monkeypatch)
    for seed, (off, text) in zip((3, 8), settled):
        assert off == [], f"seed {seed}: ranks {off} stand outside their gaps"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"gapped-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


def _small_dense_dates() -> "tuple[list[str], int]":
    """59 days from a seeded start, 83 dates, 37 of them different, at a floor of 36.

    Drawn exactly as the landing's third skeptic drew its column q283, and
    written as ISO dates, so the column is the one that measured the defect.
    """
    draw = random.Random(720283)
    assert draw.choice(["date", "midnight", "midnight", "tmark", "usdate"]) == "midnight"
    span = draw.randint(15, 150)
    rows = draw.randint(max(60, span), min(900, span * 12))
    empty = draw.choice([0.0, 0.05, 0.2])
    light = draw.random() < 0.5
    assert (span, rows, empty, light) == (59, 83, 0.05, False)
    weights: "list[float]" = []
    for _step in range(span):
        weights += [0.0 if draw.random() < empty else draw.random() + 0.1]
    steps = draw.choices(range(span), weights=weights, k=rows)
    assert draw.random() >= 0.5
    start = datetime.date(2019, 6, 1) + datetime.timedelta(days=draw.randint(0, 900))
    cells = [(start + datetime.timedelta(days=step)).isoformat() for step in steps]
    draw.shuffle(cells)
    floor = draw.choice([11, 20, 36, 50])
    assert floor == 36
    return cells, floor


def test_a_run_no_merge_can_take_is_split(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """G7.3's count pass splits a run whose room holds no other held unit.

    A run moves whole only inside the gap of every rank of it (the test
    above), and two tail ranks whose strata meet on one day have that day
    as their room: no merge can take them. This column came back holding
    41 and 43 different days at seeds 3 and 8 against 37, both distinct
    counts MISSED, where shipped stage 3 met them with ranks outside their
    gaps (plan P4-D354, the third skeptic of landing 3b.0). Such a run now
    gives its day up rank by rank, onto its two neighbours' days, each
    inside its own gap. Here both counts are met, the twin misses nothing,
    and every rank but a tail group's stands inside its gap.
    """
    cells, floor = _small_dense_dates()
    described = kpi_shapes.describe(
        tmp_path, "small_dense", "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    block = described.document["columns"][0]
    assert block["n_distinct"] == len(set(cells))
    settled = _settled_off_their_gaps(described, (3, 8), monkeypatch)
    for seed, (off, text) in zip((3, 8), settled):
        assert off == [], f"seed {seed}: ranks {off} stand outside their gaps"
        written = {line for line in text.split("\n")[1:] if line}
        assert len(written) == block["n_distinct"], f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"dense-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


def _midnight_moments_over_111_days() -> "tuple[list[str], int]":
    """123 T-marked midnight moments over 111 days, 52 of them different, at a floor of 50.

    Drawn exactly as the landing's fourth skeptic drew its column dense136,
    so the column is the one that measured the defect.
    """
    draw = random.Random(740136)
    assert draw.choice(["date", "date", "midnight", "tmark", "usdate"]) == "tmark"
    span = draw.randint(12, 120)
    rows = draw.randint(max(40, span), min(700, span * 10))
    empty = draw.choice([0.0, 0.05, 0.1, 0.25])
    assert (span, rows, empty) == (111, 123, 0.1)
    weights: "list[float]" = []
    for _step in range(span):
        weights += [
            0.0 if draw.random() < empty else draw.lognormvariate(0.0, draw.choice([0.5, 1.0, 1.5]))
        ]
    assert draw.random() >= 0.4
    steps = draw.choices(range(span), weights=weights, k=rows)
    assert draw.random() >= 0.3
    start = datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randint(0, 1500))
    cells = [(start + datetime.timedelta(days=step)).isoformat() + "T00:00:00" for step in steps]
    draw.shuffle(cells)
    return cells, 50


def _month_first_dates_over_48_days() -> "tuple[list[str], int]":
    """77 dates written m/d/yyyy over 48 days, 33 of them different, at a floor of 36.

    Drawn exactly as the landing's fourth skeptic drew its column za190.
    """
    draw = random.Random(730190)
    assert draw.choice(["date", "date", "usdate", "midnight", "tmark", "second", "minute"]) == "usdate"
    span = draw.randint(10, 400)
    rows = min(max(60, draw.randint(span // 2, span * 8)), 4000)
    empty = draw.choice([0.0, 0.05, 0.15, 0.3])
    edge = draw.random() < 0.5
    draw.choice([0.01, 0.05, 0.2])
    heavy = draw.random() < 0.5
    assert (span, rows, empty, edge, heavy) == (48, 77, 0.0, False, True)
    weights: "list[float]" = []
    for _step in range(span):
        weights += [0.0 if draw.random() < empty else draw.lognormvariate(0.0, 1.0)]
    assert draw.random() < 0.3
    for _hot in range(draw.randint(1, 3)):
        weights[draw.randrange(span)] *= 10.0
    steps = draw.choices(range(span), weights=weights, k=rows)
    assert draw.random() >= 0.3
    start = datetime.date(2018, 1, 1) + datetime.timedelta(days=draw.randint(0, 1500))
    cells = []
    for step in steps:
        day = start + datetime.timedelta(days=step)
        cells += [f"{day.month}/{day.day}/{day.year}"]
    draw.shuffle(cells)
    return cells, 36


@pytest.mark.parametrize(
    "shape", ["midnight_moments_over_111_days", "month_first_dates_over_48_days"]
)
def test_the_count_is_met_where_a_chain_of_runs_reaches_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, shape: str
) -> None:
    """G7.3's count pass stacks the ranks afresh where no one run can give a unit up.

    Tail ranks in pairs on alternate days, their two-day strata shifted
    by one rank each, have each pair's own day as its room and their
    neighbours two days off, so neither a merge nor the split takes any
    pair -- while every pair moving one day onto the next frees a day.
    These two columns came back holding 54 different days against 52 at
    floor 50, seeds 3 and 8, and 35 against 33 at floor 36, seed 3, both
    distinct counts MISSED, where shipped stage 3 met them with ranks
    outside their gaps (plan P4-D354, the fourth skeptic of landing
    3b.0), though a placement inside every gap holding the count existed.
    The ranks are now stacked afresh on the fewest units their gaps and
    standings allow and raised to the count. Here both counts are met,
    the twin misses nothing, and every rank but a tail group's stands
    inside its gap.
    """
    cells, floor = {
        "midnight_moments_over_111_days": _midnight_moments_over_111_days,
        "month_first_dates_over_48_days": _month_first_dates_over_48_days,
    }[shape]()
    described = kpi_shapes.describe(
        tmp_path, shape, "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    block = described.document["columns"][0]
    assert block["n_distinct"] == len(set(cells))
    settled = _settled_off_their_gaps(described, (3, 8), monkeypatch)
    for seed, (off, text) in zip((3, 8), settled):
        assert off == [], f"seed {seed}: ranks {off} stand outside their gaps"
        written = {line for line in text.split("\n")[1:] if line}
        assert len(written) == block["n_distinct"], f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"{shape}-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"

"""THE STAGE-3B GATE: dates keep their calendar shape, one clause per landing.

"Weekend share, hour of day and heaps come back; no calendar count below
the floor" is stage 3b's gate as the plan of record states it
(docs/STATE.md, line 3b). Each clause lands with the landing that makes
it true, and landing 3b.0 (plan P4-D354) makes the first one true:

* `test_every_day_filled` -- where a column of dates holds a value on
  EVERY day of its range, its twin validates with nothing missed, holds
  as many different days (or seconds) as the real column and none past
  the two ends its tails derive, and its own report finds each published
  approximation inside its window; where the derived ends are the real
  first and last unit it holds exactly the real units, and where one
  stands past a real end (four of the eleven cases, `_UNSETTLED`, the
  review of landing 3b.0's item 3) it writes that end in place of one
  real unit inside. Before the landing a tail's tie group
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
days could give a day up only as a chain; and
`test_the_count_is_met_where_no_placement_inside_the_gaps_reaches_it`
holds the count met past the strata -- a tail rank leaving its stratum
by the least amount that meets it, the orchestrator's call of 2026-09-28
(not an owner ruling; the owner may reverse it) -- on three columns of
the fifth skeptic whose count no placement inside every gap reaches.

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
the gapped year red at seed 3, three ranks outside their gaps, and the
three columns met past the strata red, more ranks outside their gaps
than the count needs; every gap given one more day below turns those
three red on the fewest days inside the gaps, which then reach the
count; and the pass past the strata withdrawn, its splits taken
farthest first, or taken from the ranks where the rounds left them
rather than from the stack, turns all three red, and its splits taken
with no regard to how many ranks leave turns one red.

THE REVIEW OF LANDING 3b.0 (plan P4-D358), items 2 and 4: no count pass
offers a rank a day an absent spelling of the run names, a rank drawn
onto one leaves it before the passes count, and a stuck tail rank's day
is counted as the absent cell it is.
`test_no_rank_is_stacked_on_a_day_the_table_declares_missing` (the
review's column), `test_a_rank_drawn_onto_a_missing_day_leaves_it_before_the_count`
and `test_no_rank_is_offered_a_day_another_column_declares_missing` fail
on the reviewed tree (2af1f03); the review's column turns red only with
every hole clause withdrawn together, each alone being covered by
another, so the clauses are witnessed one call at a time by the `hole`
rows of tests/test_oracle_rule_witnesses.py, where each of twelve
generator mutants turns the shipped rows red. The step off withdrawn
turns the second red, the group step's own holes alone the third, and
the stuck count withdrawn
`test_a_tail_rank_stuck_on_a_missing_day_is_counted_as_absent`. The
unit an absent spelling names is read a day, a month or a quarter by
the `absent` rows there; the month or the quarter withdrawn from
`generation._COUNT_HOLE_UNITS` turns its own `absent` row red and
`test_no_rank_is_offered_a_month_the_table_declares_missing` or
`test_no_rank_is_offered_a_quarter_the_table_declares_missing` (the
final review of 3b.0, where it turned no test red). The reading stopped
at the first spelling the member cannot read turns the `absent` rows
opening on `-` or `#N/A` red and
`test_a_missing_month_is_read_past_a_spelling_the_member_cannot_read`
(its second skeptic, where it turned no test red). G7.3b step 7 reads
the column's own hole under its member by the `tail_hole` rows there;
its reading withdrawn on months and quarters, on every member but an
ISO one, or stopped at the first spelling it cannot read turns those
rows red and a column of
`test_a_tail_group_steps_off_a_missing_month_or_month_first_day`
(that skeptic again).

LANDING 3b.1 (plan P4-D355) makes the second clause true on DATE
columns: the weekday census. Its clauses are the second half of this
file. Landing 3b.1 published a census only where a full-fill
certificate held; its three reviews (plans P4-D355 and P4-D359) added
the form, placeholder and declared holes, one spelling per day, one
storage, a withholding's own certificate and its bands, each with a
witness and a mutation record kept in the history of this file.

LANDING 3b.G (plan P4-D365) RETIRED THE CERTIFICATE under the owner's
principle of 2026-10-01 -- the threat is a HIPAA exposure, never a
reader rebuilding counts from a description -- because its price was
high: 366 of 1,147 measured censuses withheld, the twins' weekday
share .123 from the real one against .036 without it, and 1,159 s of
describe against 67 s. Withdrawn with it: its bands, its 20,000 cap, its
ties refusal, and the loader's WC5, WC7, WC8 and WC9; the verifier and
the brute force that checked them are deleted. What stands, and the
mutation that turns each witness red:

* the floor and the shape (WC1 to WC4, WC6): the battery's censuses,
  `calendar_rules.shape_breach` and the loader's mutations in
  tests/test_contract_loader.py -- red when a count of one to ten
  publishes or the loader asks a retired rule again;
* the few-dates rule (`calendar_rules.few_dates`): fewer than three
  different real dates in a non-empty group, or fewer than seven and a
  half a group on average over two or more -- red on `k7_sessions_s0`,
  `B2_oneweek_1201_s0`, `payroll_1000`, `first_2021_52m`,
  `tenth_2021_54m`, `ties40_1000` and `w_month_wide_1000_s0`, which then
  publish: the twins of the first five miss at seeds 0 to 2 (seven
  sessions, payroll and one date a month their count of different
  values, one week its census), forty ties at one seed of three, and
  one March's meet it, the rule's cost; and red on the hand-made bodies
  of `test_the_few_dates_rule_counts_the_real_dates_of_each_group`;
* the room rule (`calendar_rules.room_short`), asked beside every
  published hole but width holes -- the holes of a month-name census
  that holds every cell to May, placeholder days and declared days: a
  group with no free day holding a one-row date -- red on `mays_only`,
  whose twin then holds 83 different values for 93, on
  `decl4_240_5_2_r1`, whose twins then hold 234 different days for 235,
  and on the bodies of
  `test_the_room_rule_asks_only_where_holes_leave_no_free_day_for_a_one_row_date`;
  red too when it is asked beside width holes, which withholds
  `_straddling_february`, whose twins meet its census, and when a
  month-name word other than May's is read as May's
  (`calendar_rules.may_only_published`), which withholds every column
  written with month names;
* every hole -- form, placeholder, declared -- read by the producer, the
  generator and the validator alike (`calendar_rules.public_holes`):
  red when the twins of the form-hole, placeholder and declared columns
  stand a date on one;
* the fold read on both sides (plan P4-D250, `validation._day_as_counted`),
  asked only where the file's own description folded the moments
  (`validation._folded_by_the_file`): red when the source of `_FOLDED`
  misses its own census, and when the source of `_UNPARSED` -- moments
  the description left unparsed -- does;
* every REAL twin clause of the deleted tests is kept: the battery's
  twins and statistics, the declared missing day, the placeholder days,
  the form holes, and the drawn-hole node of the review of 3b.0, whose
  count pass is now asked on its census emptied.

EVERY LANDING AFTER 3b.1 (plan P4-D364) names its own gate file here,
on a line of its own below its own anchor. The base they build on is
held by tests/test_stage3b_base.py.
anchor 3b-D1 (P4-D365)
3b.G: this file's weekday half and tests/test_stage3b_weekday_review.py.
anchor 3b-D0 (P4-D366)
anchor 3b-D2 (P4-D367)
anchor 3b-D3 (P4-D368)
anchor 3b-D4 (P4-D369)
anchor 3b-T1 (P4-D370)
anchor 3b-T2 (P4-D371)
anchor 3b-T3 (P4-D372)
anchor 3b-C1 (P4-D373)
anchor 3b-C2 (P4-D374)
anchor 3b-G1 (P4-D375)
anchor 3b-G3 (P4-D376)
anchor 3b-G2 (P4-D377)
anchor 3b-7 (P4-D378)
anchor 3b-J (P4-D379)
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random
import re

import pytest

import fixtures
import kpi_shapes
import workbooks
from synthtwin import (
    calendar_rules,
    contract,
    errors,
    generation,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)

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


# How many cells each of the 32 days from 2024-01-01 holds: the review of
# landing 3b.0's item 3, 100 dates filling every day of their range.
_THIRTY_TWO_COUNTS = (
    5, 1, 3, 1, 4, 4, 4, 4, 2, 1, 4, 1, 4, 4, 5, 1, 13, 3, 2, 5, 1, 3, 1, 1,
    1, 5, 1, 4, 2, 4, 1, 5,
)


def _thirty_two_days() -> "tuple[str, list[str], int]":
    cells: "list[str]" = []
    for step in range(len(_THIRTY_TWO_COUNTS)):
        day = datetime.date(2024, 1, 1) + datetime.timedelta(days=step)
        cells += [day.isoformat()] * _THIRTY_TWO_COUNTS[step]
    return "seen_on", cells, len(_THIRTY_TWO_COUNTS)


_BUILDERS = {
    "admissions": _admissions,
    "billing": _billing,
    "short_range": _short_range,
    "midnight_moments": _midnight_moments,
    "every_second": _every_second,
    "small_tail_group": _small_tail_group,
    "thirty_two_days": _thirty_two_days,
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
    ("thirty_two_days", 11),
)

# THE CASES WHOSE PUBLISHED FACTS DO NOT SETTLE WHICH UNITS THE TWIN HOLDS
# (plan P4-D354's recorded limit, P4-D358): a tail's derived end stands one
# unit past the real column's first or last, so the twin writes that unit
# and holds one real unit fewer inside the range -- billing's day before
# 2023, the 300 days' day before 2024, the second after the ten minutes,
# and both of the 32 days' neighbours. Every other case's two derived ends
# are the real ends, and there the twin holds the real column's units.
_UNSETTLED = {
    ("billing", 11),
    ("short_range", 36),
    ("every_second", 11),
    ("thirty_two_days", 11),
}


def _unit(cell: str) -> str:
    """The unit a cell holds: its day, or its day and clock with the mark between them dropped."""
    return cell[:10] + cell[11:]


@pytest.mark.parametrize(
    "shape,floor", EVERY_DAY_CASES, ids=[f"{shape}-{floor}" for shape, floor in EVERY_DAY_CASES]
)
def test_every_day_filled(tmp_path: pathlib.Path, shape: str, floor: int) -> None:
    """On the gate's filled ranges: as many units, and the same ones where the facts settle them.

    At seeds 0 to 4: nothing missed, as many different units as the real
    column, no unit beyond the two ends the tails derive, and -- where
    those ends are the real column's first and last unit -- exactly the
    real column's units. Where a derived end stands past a real end
    (`_UNSETTLED`), the units beyond the real ends are those derived ends
    and nothing else, each in place of one real unit inside.
    """
    name, cells, span = _BUILDERS[shape]()
    real = {_unit(cell) for cell in cells}
    assert len(real) == span, (
        f"{shape}: the table holds {len(real)} of the {span} units of its "
        f"range, so it no longer witnesses a range filled on every unit"
    )
    text = name + "\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, f"{shape}-{floor}", text, floor)
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    layout = _layout(described.loaded, floor)
    assert layout.low is not None and layout.high is not None
    # A TAIL'S DERIVED END, or the outermost value a tail that lists its
    # values publishes.
    ends = (
        generation._tail_place(
            layout.low, layout.low.shape.end if layout.low.shape is not None else layout.low.fixed[0]
        ),
        generation._tail_place(
            layout.high, layout.high.shape.end if layout.high.shape is not None else layout.high.fixed[0]
        ),
    )
    units = sorted({generation._written_ordinal(cell, facts) for cell in cells})
    first, last = units[0], units[len(units) - 1]
    assert first is not None and last is not None
    settled = ends == (first, last)
    assert settled is ((shape, floor) not in _UNSETTLED), (
        f"{shape} at floor {floor}: derived ends {ends}, real ends {(first, last)}"
    )
    beyond_the_ends = {end for end in ends if not first <= end <= last}
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
        placed = {generation._written_ordinal(line, facts) for line in written.splitlines()[1:] if line}
        assert None not in placed, f"{shape} at floor {floor}, seed {seed}"
        assert {unit for unit in placed if unit is not None and not ends[0] <= unit <= ends[1]} == set(), (
            f"{shape} at floor {floor}, seed {seed}: a unit beyond the derived ends"
        )
        if settled:
            assert held == real, f"{shape} at floor {floor}, seed {seed}: {sorted(held ^ real)}"
        else:
            outside_the_real = {unit for unit in placed if unit is not None and not first <= unit <= last}
            assert outside_the_real == beyond_the_ends, (
                f"{shape} at floor {floor}, seed {seed}: {sorted(outside_the_real)}"
            )
            assert len(real - held) == len(beyond_the_ends), f"{shape} at floor {floor}, seed {seed}"
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


def _settled(
    described: kpi_shapes.Described, seeds: "tuple[int, ...]", monkeypatch: pytest.MonkeyPatch
) -> "list[tuple[list[int], list[int], list[int], generation._DateLayout, contract.DatetimeFacts, str]]":
    """Per seed, the instants the count pass leaves, the gaps, the layout, the facts, the twin."""
    shipped = generation._units_settled
    seen: "list[tuple[list[int], list[int], list[int], generation._DateLayout | None, contract.DatetimeFacts]]" = []

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
        *rest: object,
    ) -> "list[int]":
        moved = shipped(column, facts, ordinals, parsed, whole, lows, highs, small, layout, *rest)
        seen[:] = [(list(moved), list(lows), list(highs), layout, facts)]
        return moved

    monkeypatch.setattr(generation, "_units_settled", watched)
    found: "list[tuple[list[int], list[int], list[int], generation._DateLayout, contract.DatetimeFacts, str]]" = []
    for seed in seeds:
        text = kpi_shapes.twin_text(described, seed)
        assert len(seen) == 1, seed
        moved, lows, highs, layout, facts = seen[0]
        assert layout is not None
        found += [(moved, lows, highs, layout, facts, text)]
    return found


def _settled_off_their_gaps(
    described: kpi_shapes.Described, seeds: "tuple[int, ...]", monkeypatch: pytest.MonkeyPatch
) -> "list[tuple[list[int], str]]":
    """Per seed, the ranks the count pass leaves outside their gaps, and the twin.

    A tail group's ranks are left out: step 9 alone may move those.
    """
    found: "list[tuple[list[int], str]]" = []
    for moved, lows, highs, layout, _facts, text in _settled(described, seeds, monkeypatch):
        found += [(_off_their_gaps(moved, lows, highs, layout), text)]
    return found


def _off_their_gaps(
    moved: "list[int]", lows: "list[int]", highs: "list[int]", layout: "generation._DateLayout"
) -> "list[int]":
    """The ranks standing outside their gaps, a tail group's left out: step 9 alone may move those."""
    group: "set[int]" = set()
    for plan in (layout.low, layout.high):
        assert plan is not None and plan.shape is not None
        for index in range(max(plan.shape.grouped, 1), plan.rows):
            group.add(generation._tail_rank_of(plan, len(moved), index))
    return [
        rank
        for rank in range(len(moved))
        if rank not in group and not lows[rank] <= moved[rank] <= highs[rank]
    ]


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


def _chain_prone(index: int) -> "list[str]":
    """Few rows a day over a sparse range, alternate days empty in stretches.

    Drawn exactly as the landing's fifth skeptic drew its column ch<index>,
    so each column is one that measured the cost.
    """
    draw = random.Random(780000 + index)
    kind = draw.choice(["iso", "us", "tmark", "mid", "mon"])
    span = draw.randint(40, 220)
    rows = draw.randint(100, max(101, min(400, span * 3)))
    assert (kind, span, rows) == _GAP_RULE_COSTS[index][0]
    weights: "list[float]" = []
    for _step in range(span):
        weight = draw.lognormvariate(0.0, draw.choice([0.4, 0.9, 1.4]))
        if draw.random() < 0.15:
            weight = 0.0
        weights += [weight]
    for _stretch in range(draw.randint(1, 4)):
        low = draw.randrange(span)
        for step in range(low, min(span, low + draw.randint(6, 30))):
            if (step - low) % 2 == 1:
                weights[step] = 0.0
            else:
                weights[step] = weights[step] * draw.choice([0.1, 0.3, 1.0])
    if draw.random() < 0.6:
        edge = draw.randint(4, max(5, span // 5))
        for step in range(edge):
            if step % 2 == 1:
                weights[step] = 0.0
                weights[span - 1 - step] = 0.0
            else:
                weights[step] = weights[step] * 0.2
                weights[span - 1 - step] = weights[span - 1 - step] * 0.2
    assert sum(weights) > 0
    steps = draw.choices(range(span), weights=weights, k=rows)
    start = datetime.date(2017, 6, 1) + datetime.timedelta(days=draw.randint(0, 2000))
    cells = []
    for step in steps:
        day = start + datetime.timedelta(days=step)
        if kind == "us":
            cells += [f"{day.month}/{day.day}/{day.year}"]
        elif kind == "tmark":
            cells += [day.isoformat() + "T00:00:00"]
        else:
            cells += [day.isoformat()]
    draw.shuffle(cells)
    return cells


# The fifth skeptic's columns: (its kind, days and rows; the floor).
_GAP_RULE_COSTS = {
    6: (("iso", 56, 123), 36),
    18: (("us", 92, 123), 36),
    32: (("tmark", 140, 114), 50),
}


def _fewest_inside_the_gaps(
    moved: "list[int]", lows: "list[int]", highs: "list[int]", layout: "generation._DateLayout"
) -> int:
    """The fewest different days any placement of the ranks inside their gaps holds.

    A rank the count pass may not move -- one the tail pins, or one whose
    gap is a single day -- stands where it stands; every other rank may
    stand anywhere inside its gap. Taken by the gaps' upper ends, each gap
    either holds the day last stacked or stacks its own upper end: the
    stabbing of intervals, the least number of days meeting every gap.
    Width kind and midnight are ignored, so it is a lower bound on what a
    placement keeping every standing holds.
    """
    pinned = generation._ranks_the_tail_pins(layout)
    bounds: "list[tuple[int, int]]" = []
    for rank in range(len(moved)):
        if pinned[rank] or lows[rank] >= highs[rank]:
            bounds += [(moved[rank], moved[rank])]
        else:
            bounds += [(highs[rank], lows[rank])]
    stacked: "int | None" = None
    days = 0
    for high, low in sorted(bounds):
        if stacked is None or stacked < low:
            stacked = high
            days = days + 1
    return days


def _drawn_tail_ranks(layout: "generation._DateLayout", parsed: int) -> "dict[int, generation._TailPlan]":
    """Every tail rank that draws a word -- neither its tail's end nor its group -- with its tail."""
    found: "dict[int, generation._TailPlan]" = {}
    for plan in (layout.low, layout.high):
        assert plan is not None
        if plan.shape is None:
            continue
        for index in range(1, plan.shape.grouped):
            found[generation._tail_rank_of(plan, parsed, index)] = plan
    return found


@pytest.mark.parametrize("index", sorted(_GAP_RULE_COSTS))
def test_the_count_is_met_where_no_placement_inside_the_gaps_reaches_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, index: int
) -> None:
    """THE GAP RULE'S COST, REPAIRED: a tail rank leaves its stratum by the least amount.

    123 ISO dates over 56 days, 24 different, and 123 month-first dates
    over 92 days, 35 different, at floor 36, and 114 midnight moments over
    140 days, 43 different, at floor 50, came back holding 26, 38 and 46
    different days with every rank inside its gap, both distinct counts
    MISSED, where shipped stage 3 (d93fd43) met them with tail ranks a day
    below their strata and validated (the fifth skeptic of landing 3b.0).
    No placement inside every gap holds fewer than 25, 37 and 44 days.
    The orchestrator's call of 2026-09-28 (not an owner ruling; the owner
    may reverse it; plan P4-D354): where no placement with every rank
    inside its gap can meet the distinct count, a tail rank may leave its
    stratum by the least amount that meets it, and only where the tail's
    published windows and every other published check still hold. Here,
    at seeds 3 and 8: the fewest days inside the gaps stands above the
    count, so the rule is the one that acts; the twin holds exactly the
    published count and misses nothing -- every tail window, rung and
    count held; and every rank outside its gap is a tail rank that draws a
    word, strictly beyond its boundary, ONE unit outside -- no leaving is
    shorter -- and no more of them than the fewest days inside the gaps
    exceed the count, which is the fewest any placement needs, since
    letting one rank out lowers the fewest by at most one.
    """
    cells = _chain_prone(index)
    floor = _GAP_RULE_COSTS[index][1]
    described = kpi_shapes.describe(
        tmp_path, f"chain{index}", "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    block = described.document["columns"][0]
    assert block["n_distinct"] == len(set(cells))
    for seed, (moved, lows, highs, layout, facts, text) in zip(
        (3, 8), _settled(described, (3, 8), monkeypatch)
    ):
        assert generation._ordinal_space(facts) == "date"
        assert facts.n_unparsed == 0
        fewest = _fewest_inside_the_gaps(moved, lows, highs, layout)
        assert fewest > block["n_distinct"], f"seed {seed}: {fewest} days inside the gaps reach the count"
        written = {line for line in text.split("\n")[1:] if line}
        assert len(written) == block["n_distinct"], f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"chain{index}-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"
        drawn = _drawn_tail_ranks(layout, len(moved))
        off = _off_their_gaps(moved, lows, highs, layout)
        for rank in off:
            assert rank in drawn, f"seed {seed}: rank {rank} outside its gap draws no tail word"
            assert generation._tail_distance_of(drawn[rank], moved[rank]) >= 1, (
                f"seed {seed}: rank {rank} stands on or inside its boundary"
            )
            away = max(lows[rank] - moved[rank], moved[rank] - highs[rank])
            assert away == drawn[rank].unit, f"seed {seed}: rank {rank} stands {away} outside its gap"
        assert 0 < len(off) <= fewest - block["n_distinct"], (
            f"seed {seed}: {len(off)} ranks outside their gaps, the fewest days inside them {fewest}"
        )




def _drawn_past_the_strata() -> "tuple[list[str], int]":
    """114 ISO dates over the 245 days from 2023-01-01, 35 different, at a floor of 50.

    Drawn exactly as the review of landing 3b.0 drew its item 1, so the
    column is the one that measured the defect.
    """
    draw = random.Random(982004)
    rows = draw.randrange(100, 241)
    span = draw.randrange(35, 350)
    floor = draw.choice((11, 36, 50))
    weights = [
        draw.lognormvariate(0, draw.choice((0.4, 1, 2))) if draw.random() > 0.25 else 0
        for _step in range(span)
    ]
    steps = draw.choices(range(span), weights=weights, k=rows)
    cells = [(datetime.date(2023, 1, 1) + datetime.timedelta(days=step)).isoformat() for step in steps]
    assert (rows, floor, len(set(cells))) == (114, 50, 35)
    return cells, floor


def test_a_count_the_pass_meets_past_the_strata_is_held_exactly(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The review of landing 3b.0, item 1: the envelope follows the pass (P4-D358).

    Counted in the strata alone, G12.5's lower end for this column stood
    at 39, above the 35 different dates it publishes, so neither the
    validator nor the twin's report held the count exactly: the twin the
    pass writes held 35, and a file holding 60 -- the pass past the strata
    withdrawn -- was WITHIN-BOUND of 39 to 114 with nothing missed, and
    inside the report's bound. Where the count is reachable, an unpinned
    rank of a shape-drawn tail is now windowed as far as the pass may
    take it, the published count lies inside the envelope, and both hold
    it exactly: the twin's count HELD, the file of 60 MISSED on both
    counts, the report's bound the published count alone.
    """
    cells, floor = _drawn_past_the_strata()
    described = kpi_shapes.describe(
        tmp_path, "past_the_strata", "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert contract.datetime_counts_reachable(column)
    lowest, highest = validation._datetime_distinct_window(column, facts, floor, "")
    assert lowest <= column.n_distinct <= highest, (lowest, highest)
    text = kpi_shapes.twin_text(described, 3)
    verdicts = {
        check.subcheck: check.verdict
        for check in kpi_shapes.measure(described, text, "met.csv").checks
    }
    assert verdicts["distinct.n_distinct"] == validation.HELD
    assert verdicts["distinct.n_distinct_folded"] == validation.HELD
    monkeypatch.setattr(generation, "_count_met_past_the_strata", lambda *arguments: False)
    twin = generation.generate(described.loaded, 3)
    written = rendering.twin_csv(twin)
    # THE FILE THE REVIEW PASSED: its count is not the published one, and
    # it lies inside the envelope counted in the strata alone, whose lower
    # end stands above the published count.
    held = len({line for line in written.split("\n")[1:] if line})
    dated = column.n_present - facts.n_unparsed
    strata = validation._ranks_forced_apart(*validation._rank_windows(facts, dated, column, floor, ""))
    assert column.n_distinct < strata + facts.n_unparsed <= held <= highest, (strata, held)
    outcome = kpi_shapes.measure(described, written, "withdrawn.csv")
    missed = kpi_shapes.missed(outcome)
    assert "c:distinct.n_distinct" in missed and "c:distinct.n_distinct_folded" in missed, missed
    records = {record.fact: record for record in twin.approximations}
    shown = str(column.n_distinct)
    for fact in ("n_distinct", "n_distinct_folded"):
        record = records[fact]
        assert (record.lowest, record.highest, record.inside) == (shown, shown, False), fact


def test_the_fewest_units_are_counted_in_the_order_of_the_windows_upper_ends() -> None:
    """G12.5's lower end is the stabbing of the windows, in upper-end order (P4-D358).

    Windows past the strata need not arrive in order of both ends, and a
    walk in rank order keeps a wide first window and skips every window
    it touches: over [0, 10], [2, 3] and [5, 6] it counts one where two
    are forced apart. Both writings of the count, the validator's and the
    report's, count two.
    """
    assert validation._ranks_forced_apart([0, 2, 5], [10, 3, 6]) == 2
    assert generation._forced_apart([0, 2, 5], [10, 3, 6]) == 2


def test_the_envelope_follows_the_pass_only_where_the_count_is_reachable(
    tmp_path: pathlib.Path,
) -> None:
    """G12.5's windows past the strata stand only where the pass may use them.

    The column above written as midnight moments, every other cell marked
    with `T` and the rest with a space: two marks, so one instant has two
    spellings, the count is not reachable (contract
    `datetime_counts_reachable`) and the pass never runs. The validator's
    rank windows and the report's are then the strata as G12.4 draws them,
    where the reachable column's are wider.
    """
    cells, floor = _drawn_past_the_strata()
    for marked in (False, True):
        written = [
            f"{cell}{'T' if place % 2 else ' '}00:00:00" if marked else cell
            for place, cell in enumerate(cells)
        ]
        described = kpi_shapes.describe(
            tmp_path, f"envelope-{marked}", "c\n" + "".join(f"{cell}\n" for cell in written), floor
        )
        column = described.loaded.columns[0]
        facts = column.facts
        assert isinstance(facts, contract.DatetimeFacts)
        assert contract.datetime_counts_reachable(column) is not marked
        dated = column.n_present - facts.n_unparsed
        lows, highs = validation._rank_windows(facts, dated, column, floor, "")
        past = validation._past_the_strata(column, facts, dated, floor, "", lows, highs)
        layout = _layout(described.loaded, floor)
        drawn = generation._datetime_window(layout, facts, dated)
        report = generation._past_the_strata_windows(layout, drawn[0], drawn[1])
        assert (past == (lows, highs)) is marked, f"marked {marked}: the validator"
        records = {record.fact: record for record in generation.generate(described.loaded, 3).approximations}
        strata = generation._forced_apart(drawn[0], drawn[1])
        widened = generation._forced_apart(report[0], report[1])
        assert widened < strata, "the pass could meet no lower count here"
        if marked:
            assert int(records["n_distinct"].lowest) >= strata, "the report widened an unreachable count"
            continue
        # EACH UNPINNED RANK OF A SHAPE-DRAWN TAIL reaches from the tail's
        # outermost rank to one tail unit short of the boundary, and keeps
        # its own reading allowance: the validator's windows in seconds, the
        # report's in days.
        assert layout.low is not None and layout.high is not None
        tails = (
            (layout.low, facts.low_tail, range(layout.low.rows)),
            (layout.high, facts.high_tail, range(dated - 1, dated - 1 - layout.high.rows, -1)),
        )
        for plan, tail, ranks in tails:
            assert tail is not None
            boundary = validation._ordinal_of(tail.boundary, facts.resolution)
            ranks = [rank for rank in ranks if lows[rank] < highs[rank]]
            assert ranks, "no unpinned rank in the tail"
            for rank in ranks:
                if plan.low_side:
                    assert (past[0][rank], past[1][rank]) == (
                        min(lows[rank], lows[0]), max(highs[rank], boundary - 86400)
                    ), rank
                    assert (report[0][rank], report[1][rank]) == (
                        min(drawn[0][rank], drawn[0][0]), max(drawn[1][rank], plan.anchor - 1)
                    ), rank
                else:
                    assert (past[0][rank], past[1][rank]) == (
                        min(lows[rank], boundary + 86400), max(highs[rank], highs[dated - 1])
                    ), rank
                    assert (report[0][rank], report[1][rank]) == (
                        min(drawn[0][rank], plan.anchor + 1), max(drawn[1][rank], drawn[1][dated - 1])
                    ), rank
            assert any(past[0][rank] < lows[rank] or past[1][rank] > highs[rank] for rank in ranks)


def _drawn_short_of_the_window() -> "tuple[list[str], int]":
    """127 ISO dates over the 78 days from 2023-01-01, 29 different, at a floor of 50.

    Drawn as the second review of landing 3b.0 drew its strata family,
    at 983174, so the column is the one that measured the limit.
    """
    draw = random.Random(983174)
    rows = draw.randrange(100, 241)
    span = draw.randrange(35, 350)
    floor = draw.choice((36, 50, 50))
    weights = [
        draw.lognormvariate(0, draw.choice((0.4, 1, 2))) if draw.random() > 0.25 else 0
        for _step in range(span)
    ]
    steps = draw.choices(range(span), weights=weights, k=rows)
    cells = [(datetime.date(2023, 1, 1) + datetime.timedelta(days=step)).isoformat() for step in steps]
    assert (rows, floor, len(set(cells))) == (127, 50, 29)
    return cells, floor


def test_a_count_the_summed_window_keeps_out_of_reach_is_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A recorded limit (plan P4-D358): the envelope does not ask the summed window.

    G12.5 widens each rank the pass may move past its stratum on its own,
    so this column's lower end falls below its 29 different dates, and
    the count is held exactly. The pass reaches 29 by its splits and then
    finds the high tail's summed square past G12.14's window, so nothing
    moves and the twin holds more: the validator MISSES both counts and
    the twin's own report says it does not hold them. The second review
    measured it on 4 of 900 columns of its strata family, 6 of 1,200
    twins, all at a floor of 50; counted in the strata alone, the lower
    end stood above 29 and those twins were WITHIN-BOUND. A repair that
    meets the count, or widens only where the pass can, turns this red
    and restates the record.
    """
    cells, floor = _drawn_short_of_the_window()
    described = kpi_shapes.describe(
        tmp_path, "short_of_the_window", "c\n" + "".join(f"{cell}\n" for cell in cells), floor
    )
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    lowest, highest = validation._datetime_distinct_window(column, facts, floor, "")
    dated = column.n_present - facts.n_unparsed
    strata = validation._ranks_forced_apart(*validation._rank_windows(facts, dated, column, floor, ""))
    assert lowest <= column.n_distinct < strata + facts.n_unparsed <= highest, (lowest, strata)
    taken: "list[bool]" = []
    pass_itself = generation._count_met_past_the_strata

    def spied(*arguments: object) -> bool:
        nonlocal taken
        met = pass_itself(*arguments)  # type: ignore[arg-type]
        taken += [met]
        return met

    monkeypatch.setattr(generation, "_count_met_past_the_strata", spied)
    twin = generation.generate(described.loaded, 3)
    assert taken == [False], taken
    written = rendering.twin_csv(twin)
    assert len({line for line in written.split("\n")[1:] if line}) > column.n_distinct
    missed = kpi_shapes.missed(kpi_shapes.measure(described, written, "short.csv"))
    assert "c:distinct.n_distinct" in missed and "c:distinct.n_distinct_folded" in missed, missed
    records = {record.fact: record for record in twin.approximations}
    shown = str(column.n_distinct)
    for fact in ("n_distinct", "n_distinct_folded"):
        record = records[fact]
        assert (record.lowest, record.highest, record.inside) == (shown, shown, False), fact

# ---------------------------------------------------------------------
# THE REVIEW OF LANDING 3b.0, ITEMS 2 AND 4 (plan P4-D358): a day the
# table declares missing is offered to no rank by any count pass, a rank
# drawn onto one leaves it before the passes count, and a tail rank no
# pass may move that stands on one is counted as the absent cell it is.


def _described_with_a_missing_day(
    tmp_path: pathlib.Path, stem: str, cells: "list[str]", floor: int, day: str, *others: str
) -> kpi_shapes.Described:
    """The table of ``cells`` described at ``floor`` with ``day`` and ``others`` declared missing."""
    table = fixtures.write(tmp_path, f"{stem}.csv", "c\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=(day, *others))
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor), settings, [], [], []
    )
    written = fixtures.write_profile(tmp_path, f"{stem}-profile.json", document)
    return kpi_shapes.Described(tmp_path, table, document, contract.load_profile(str(written)))


def _day_number(text: str) -> int:
    """An ISO date as the day the count pass counts it in (days from 1970-01-01)."""
    return (datetime.date.fromisoformat(text) - datetime.date(1970, 1, 1)).days


_RESTACK_HOLE = "2019-03-11"


def test_no_rank_is_stacked_on_a_day_the_table_declares_missing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The review of landing 3b.0, item 2: the stack offers no rank a missing day.

    The fifth skeptic's 123 ISO dates over 56 days, 24 different, with 36
    cells of 2019-03-11, a day inside their range, declared missing, at a
    floor of 36: stage 3 (d93fd43) met both distinct counts at seed 3.
    The landing's stack put two present ranks on the missing day to reach
    24 units, the spelling step then moved them apart, and the twin held
    25 different days, both distinct counts MISSED. Here, at seeds 3 and
    8, no rank stands on the missing day once the count pass is done, the
    written cells hold the published 24 days, and nothing is missed.
    """
    cells = _chain_prone(6) + [_RESTACK_HOLE] * 36
    described = _described_with_a_missing_day(tmp_path, "restack_hole", cells, 36, _RESTACK_HOLE)
    block = described.document["columns"][0]
    assert (block["n_present"], block["n_distinct"], block["missing_by_source"]) == (
        123, 24, {_RESTACK_HOLE: 36}
    )
    assert block["weekday_census"] == []
    hole = _day_number(_RESTACK_HOLE)
    for seed, (moved, _lows, _highs, _layout, _facts, text) in zip(
        (3, 8), _settled(described, (3, 8), monkeypatch)
    ):
        assert hole not in moved, f"seed {seed}: a rank stands on the missing day"
        written = {line for line in text.split("\n")[1:] if line} - {_RESTACK_HOLE}
        assert len(written) == 24, f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"restack-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


def test_no_rank_is_offered_a_day_another_column_declares_missing(tmp_path: pathlib.Path) -> None:
    """G7.3b step 9 offers no day ANY column's absent spelling names (P4-D358).

    The frozen case's column without its four cells of 2024-05-12, beside
    a column of kinds sixteen of whose cells are `2024-05-12`, declared
    missing: the dates publish no absent spelling of their own, the kinds
    publish that one. A date cell written 2024-05-12 reads back absent, so
    the spelling step moved the rank the low group gave that day onto a
    day ranks held, and the dates came back with 20 of their 21 days,
    both distinct counts MISSED at seeds 0 to 4. The step now takes every
    absent spelling of the run: 21 days, nothing missed.
    """
    days = [
        cell for cell in _cells_of(_EVERY_DAY_GROUP_COUNTS, _EVERY_DAY_GROUP_START)
        if cell != _ABSENT_DAY
    ]
    kinds = ([_ABSENT_DAY] * 16 + ["x", "y", "z"] * 40)[: len(days)]
    table = fixtures.write(
        tmp_path, "two.csv", "seen_on,kind\n" + "".join(f"{a},{b}\n" for a, b in zip(days, kinds))
    )
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=(_ABSENT_DAY,))
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=11), settings, [], [], []
    )
    written = fixtures.write_profile(tmp_path, "two-profile.json", document)
    described = kpi_shapes.Described(tmp_path, table, document, contract.load_profile(str(written)))
    dates, labels = document["columns"]
    assert (dates["missing_by_source"], labels["missing_by_source"]) == ({}, {_ABSENT_DAY: 16})
    for seed in SEEDS:
        text = kpi_shapes.twin_text(described, seed)
        held = {line.split(",")[0] for line in text.split("\n")[1:] if line}
        assert _ABSENT_DAY not in held, f"seed {seed}"
        assert len(held - {""}) == dates["n_distinct"], f"seed {seed}: {len(held - {''})} days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"two-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


# 116 ISO dates over the 41 days from 2020-10-02, 37 of them on
# 2020-10-20, which is declared missing (a seeded column of the review's
# hole battery). At a floor of eleven three body ranks are drawn onto it.
_DRAWN_HOLE_COUNTS = (
    3, 5, 1, 1, 1, 1, 0, 7, 0, 2, 3, 5, 0, 0, 1, 1, 0, 0, 37, 0, 0, 4, 3,
    12, 1, 2, 1, 2, 0, 3, 2, 2, 5, 2, 0, 4, 0, 0, 1, 2, 2,
)


def test_a_rank_drawn_onto_a_missing_day_leaves_it_before_the_count(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A rank drawn onto a missing day is counted where its cell will stand (P4-D358).

    The count pass counted the missing day three body ranks were drawn
    onto and met its 28; the spelling step then moved the three onto the
    day beside it, which other ranks held, and the twin held 27 at seeds
    3 and 8, both distinct counts MISSED -- on stage 3 (d93fd43) and on
    the reviewed tree alike. Each such rank now moves off the day before
    the passes' first round: none stands there once they are done, the
    cells hold the published 28 days, and nothing is missed. The frozen
    case `count_off_the_hole` of tests/test_generation_reference.py holds
    the oracle to the same column.

    THE COUNT PASS ALONE, ITS PREMISE KEPT (plan P4-D365). Since the
    weekday guards were dropped the column publishes `[Mon-Fri] 34
    [Sat-Sun] 23`, and with a census standing the count pass leaves a
    body rank on the hole to the weekday pass by design
    (`_left_to_the_weekday_pass`). So the count pass is asked on the
    description with its census emptied -- an empty census is always
    legal -- and the published description is held to its REAL clause:
    its twins at seeds 3 and 8 hold the 28 days and miss nothing.
    """
    cells: "list[str]" = []
    for step in range(len(_DRAWN_HOLE_COUNTS)):
        day = datetime.date(2020, 10, 2) + datetime.timedelta(days=step)
        cells += [day.isoformat()] * _DRAWN_HOLE_COUNTS[step]
    random.Random(20201020).shuffle(cells)
    published = _described_with_a_missing_day(tmp_path, "drawn_hole", cells, 11, "2020-10-20")
    block = published.document["columns"][0]
    assert (block["n_present"], block["n_distinct"], block["weekday_census"]) == (
        79, 28, [{"first": 0, "last": 4, "count": 34}, {"first": 5, "last": 6, "count": 23}]
    )
    for seed in (3, 8):
        text = kpi_shapes.twin_text(published, seed)
        written = {line for line in text.split("\n")[1:] if line} - {"2020-10-20"}
        assert len(written) == 28, f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(published, text, f"published-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"
    document = dict(published.document)
    document["columns"] = [dict(block, weekday_census=[])]
    emptied = fixtures.write_profile(tmp_path, "drawn_hole-alone-profile.json", document)
    described = kpi_shapes.Described(tmp_path, published.table, document, contract.load_profile(str(emptied)))
    hole = _day_number("2020-10-20")
    for seed, (moved, _lows, _highs, _layout, _facts, text) in zip(
        (3, 8), _settled(described, (3, 8), monkeypatch)
    ):
        assert hole not in moved, f"seed {seed}: a rank stands on the missing day"
        written = {line for line in text.split("\n")[1:] if line} - {"2020-10-20"}
        assert len(written) == 28, f"seed {seed}: {len(written)} different days"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"drawn-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"


# 336 months over the 54 from 2012-01, 13 of them 2015-02, declared
# missing; and 171 quarters over the 30 from 1992-Q1, 30 of them 1998-Q1,
# declared missing (the final review's month and quarter batteries,
# `random.Random(996000)` and `random.Random(997002)`, at a floor of 11).
_MONTH_HOLE_COUNTS = (
    13, 1, 24, 6, 0, 2, 7, 2, 11, 3, 0, 0, 19, 0, 1, 5, 5, 8, 77, 0, 3, 0,
    4, 0, 3, 7, 6, 4, 7, 2, 4, 0, 0, 5, 1, 9, 1, 13, 15, 1, 1, 1, 3, 2, 2,
    3, 4, 26, 0, 5, 0, 0, 1, 19,
)
_QUARTER_HOLE_COUNTS = (
    4, 8, 2, 0, 3, 0, 0, 2, 10, 0, 0, 2, 0, 1, 2, 3, 2, 14, 5, 6, 0, 2, 3,
    57, 30, 3, 4, 0, 0, 8,
)


def _span_hole_held(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    cells: "list[str]",
    hole: str,
    unit: int,
    floor: int = 11,
    others: "tuple[str, ...]" = (),
) -> dict:
    """At seeds 3 and 8 no rank stands on ``unit``, the cells hold the published count, nothing missed."""
    described = _described_with_a_missing_day(tmp_path, "span_hole", cells, floor, hole, *others)
    block = described.document["columns"][0]
    for seed, (moved, _lows, _highs, _layout, _facts, text) in zip(
        (3, 8), _settled(described, (3, 8), monkeypatch)
    ):
        assert unit not in moved, f"seed {seed}: a rank stands on the missing {hole}"
        written = {line for line in text.split("\n")[1:] if line} - {hole, *others}
        assert len(written) == block["n_distinct"], f"seed {seed}: {len(written)} different values"
        missed = kpi_shapes.missed(kpi_shapes.measure(described, text, f"span-{seed}.csv"))
        assert missed == [], f"seed {seed}: {missed}"
    return block


def test_no_rank_is_offered_a_month_the_table_declares_missing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A month an absent spelling names is a hole of the count pass (P4-D358).

    `2015-02` read under `iso-month` names month 12 * 45 + 1 from 1970.
    With the month withdrawn from the pass's holes a rank was offered it,
    the spelling step moved that rank onto a month ranks held, and the
    twin held 40 months against the published 41, both distinct counts
    MISSED at seeds 3 and 8 -- 88 of 400 twins of the battery.
    """
    cells: "list[str]" = []
    for step, count in enumerate(_MONTH_HOLE_COUNTS):
        cells += [f"{2012 + step // 12}-{step % 12 + 1:02d}"] * count
    random.Random(996000).shuffle(cells)
    block = _span_hole_held(tmp_path, monkeypatch, cells, "2015-02", 12 * 45 + 1)
    assert (block["format"], block["n_present"], block["n_distinct"], block["missing_by_source"]) == (
        "iso-month", 323, 41, {"2015-02": 13}
    )


def test_no_rank_is_offered_a_quarter_the_table_declares_missing(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A quarter an absent spelling names is a hole of the count pass (P4-D358).

    `1998-Q1` read under `year-quarter` names quarter 4 * 28 from 1970.
    With the quarter withdrawn from the pass's holes the twin held 19
    quarters against the published 20, both distinct counts MISSED at
    seeds 3 and 8 -- 121 of 400 twins of the battery.
    """
    cells: "list[str]" = []
    for step, count in enumerate(_QUARTER_HOLE_COUNTS):
        cells += [f"{1992 + step // 4}-Q{step % 4 + 1}"] * count
    random.Random(997002).shuffle(cells)
    block = _span_hole_held(tmp_path, monkeypatch, cells, "1998-Q1", 4 * 28)
    assert (block["format"], block["n_present"], block["n_distinct"], block["missing_by_source"]) == (
        "year-quarter", 141, 20, {"1998-Q1": 30}
    )


# 494 months over the 72 from 2012-03, beside 27 cells of 2013-06 and 13
# of `-`, both declared missing (the final review's second skeptic,
# `random.Random(460004)`, at a floor of 11).
_DASHED_MONTH_COUNTS = (
    10, 1, 0, 0, 21, 0, 0, 6, 6, 20, 0, 7, 0, 12, 0, 27, 1, 3, 18, 1, 12, 0,
    61, 0, 81, 0, 28, 7, 8, 7, 69, 0, 4, 12, 11, 2, 1, 0, 0, 1, 0, 1, 22, 0,
    0, 4, 0, 1, 1, 3, 2, 5, 0, 0, 0, 1, 8, 0, 1, 0, 0, 2, 1, 0, 0, 1, 2, 0,
    21, 0, 0, 8,
)


def test_a_missing_month_is_read_past_a_spelling_the_member_cannot_read(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An absent spelling the member cannot read hides no hole after it (P4-D358).

    `-` sorts before `2013-06`, and `iso-month` reads no month in it. With
    the reading stopped at the first spelling it cannot read, a rank was
    offered 2013-06, the spelling step moved it onto a month ranks held,
    and the twin held 42 months against the published 43, both distinct
    counts MISSED at seeds 3 and 8 -- 167 of 400 twins of the battery.
    """
    cells: "list[str]" = ["-"] * 13
    for step, count in enumerate(_DASHED_MONTH_COUNTS):
        cells += [f"{2012 + (step + 2) // 12}-{(step + 2) % 12 + 1:02d}"] * count
    random.Random(460004).shuffle(cells)
    block = _span_hole_held(tmp_path, monkeypatch, cells, "2013-06", 12 * 43 + 5, 11, ("-",))
    assert (block["format"], block["n_present"], block["n_distinct"], block["missing_by_source"]) == (
        "iso-month", 494, 43, {"-": 13, "2013-06": 27}
    )


# 124 values over the 110 units from the first, beside 56 cells of the
# seventeenth and 40 of `-`, both declared missing, at a floor of 36:
# months from 1992-02, the seventeenth 1993-06, or month-first days from
# 1992-01-02, the seventeenth 1992-01-18 (the final review's second
# skeptic, `random.Random(450226)`).
_STEP_OFF_COUNTS = (
    2, 0, 0, 5, 0, 0, 0, 14, 0, 5, 0, 0, 2, 0, 0, 16, 56, 0, 6, 0, 1, 0, 1,
    2, 0, 0, 2, 0, 0, 0, 1, 3, 0, 0, 3, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0,
    0, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 3, 0, 0,
    0, 0, 0, 0, 0, 2, 3, 1, 1, 5, 0, 0, 1, 0, 1, 0, 1, 5, 0, 8, 0, 6, 0, 0,
    0, 4, 0, 1, 4, 0, 0, 0, 2, 1, 0, 1, 0, 0, 1,
)


@pytest.mark.parametrize("member", ("iso-month", "month-first-date"))
def test_a_tail_group_steps_off_a_missing_month_or_month_first_day(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, member: str
) -> None:
    """G7.3b step 7 reads the column's own hole under its own member (P4-D358).

    The low tail's tie group of nine ranks falls on the missing unit and
    steps one unit inward off it. With step 7's reading withdrawn on
    months and quarters, or on every member but an ISO one, or stopped at
    the `-` that sorts before the unit, the group stood there: 65 cells
    read back absent where the column holds 56, and ten checks MISSED at
    seeds 3 and 8, the median and the low tail's boundary, mean, spread
    and rows among them.
    """
    cells: "list[str]" = ["-"] * 40
    for step, count in enumerate(_STEP_OFF_COUNTS):
        day = datetime.date(1992, 1, 2) + datetime.timedelta(days=step)
        month = f"{1992 + (step + 1) // 12}-{(step + 1) % 12 + 1:02d}"
        cells += [month if member == "iso-month" else f"{day.month}/{day.day}/{day.year}"] * count
    random.Random(450226).shuffle(cells)
    hole, unit = ("1993-06", 12 * 23 + 5) if member == "iso-month" else ("1/18/1992", 8052)
    block = _span_hole_held(tmp_path, monkeypatch, cells, hole, unit, 36, ("-",))
    assert (block["format"], block["n_present"], block["n_distinct"], block["missing_by_source"]) == (
        member, 124, 43, {"-": 40, hole: 56}
    )


# 116 ISO dates over the 41 days from 2019-11-08, eleven of them on
# 2019-11-11, which is declared missing (a seeded column of the review's
# search at a floor of eleven). A low-tail rank's stratum is that one day.
_STUCK_HOLE_COUNTS = (
    4, 0, 0, 11, 0, 2, 3, 0, 1, 3, 0, 0, 0, 0, 0, 4, 2, 14, 1, 2, 2, 3, 3,
    3, 2, 7, 0, 0, 5, 0, 5, 20, 11, 0, 7, 0, 0, 0, 0, 0, 1,
)

# What that twin misses whatever the count pass does: the stuck rank's
# cell is written absent (a carried edge case, plan P4-D358).
_STUCK_HOLE_MISSES = {
    "c:counts.n_not_numeric",
    "c:holes.by_source.2019-11-11",
    "c:offsets.(none)",
    "c:presence.n_missing",
    "c:presence.n_present",
    "c:tails.low.rows",
}


def test_a_tail_rank_stuck_on_a_missing_day_is_counted_as_absent(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A stuck tail rank's missing day is none of the column's present values (P4-D358).

    A low-tail rank whose stratum is the one day 2019-11-11 stands there
    at seed 0, and its cell is written absent: six checks are missed, on
    the reviewed tree as on stage 3, and that carried edge case is held
    here at those six. Once no pass offers a rank the missing day, the
    passes counted that day among the column's values and the written
    cells held one day fewer than the published count, both distinct
    counts MISSED beside the six; they now reach the count with that day
    added, and the cells hold the published count of present days.
    """
    cells: "list[str]" = []
    for step in range(len(_STUCK_HOLE_COUNTS)):
        day = datetime.date(2019, 11, 8) + datetime.timedelta(days=step)
        cells += [day.isoformat()] * _STUCK_HOLE_COUNTS[step]
    random.Random(20191111).shuffle(cells)
    described = _described_with_a_missing_day(tmp_path, "stuck_hole", cells, 11, "2019-11-11")
    block = described.document["columns"][0]
    hole = _day_number("2019-11-11")
    for moved, lows, highs, layout, _facts, text in _settled(described, (0,), monkeypatch):
        assert layout.low is not None
        stuck = [
            rank for rank in range(layout.low.rows)
            if moved[rank] == hole and lows[rank] == highs[rank] == hole
        ]
        assert stuck, "no low-tail rank's stratum is the missing day"
        written = {line for line in text.split("\n")[1:] if line} - {"2019-11-11"}
        assert len(written) == block["n_distinct"], f"{len(written)} different days"
        missed = set(kpi_shapes.missed(kpi_shapes.measure(described, text, "stuck.csv")))
        assert missed == _STUCK_HOLE_MISSES, sorted(missed ^ _STUCK_HOLE_MISSES)


# 259 quarters over the 47 from 1986-Q2, 31 of them 1986-Q4, declared
# missing (the final review's quarter battery, `random.Random(997059)`).
_STUCK_QUARTER_COUNTS = (
    2, 1, 31, 40, 1, 0, 1, 3, 1, 1, 0, 0, 2, 0, 4, 1, 4, 0, 7, 1, 3, 0, 2,
    2, 9, 0, 5, 0, 7, 1, 5, 42, 0, 1, 0, 4, 3, 27, 1, 8, 11, 0, 4, 3, 9, 0, 12,
)


def test_a_tail_rank_stuck_on_a_missing_quarter_costs_rungs_and_a_boundary(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A recorded limit (plan P4-D358): the stuck rank's absent cell costs more than its counts.

    A low-tail rank whose stratum is 1986-Q4 alone stands there at seeds 3
    and 8 and is written absent. The count of different quarters is held,
    and beside the absent cells' own checks the twin misses a ladder rung,
    the low tail's boundary and its `Q` marks. A repair that moves such a
    rank turns this red and restates the record, which gave this limit as
    six checks on days alone.
    """
    cells: "list[str]" = []
    for step, count in enumerate(_STUCK_QUARTER_COUNTS):
        cells += [f"{1986 + (step + 1) // 4}-Q{(step + 1) % 4 + 1}"] * count
    random.Random(997059).shuffle(cells)
    described = _described_with_a_missing_day(tmp_path, "stuck_quarter", cells, 11, "1986-Q4")
    block = described.document["columns"][0]
    assert (block["format"], block["n_distinct"], block["missing_by_source"]) == (
        "year-quarter", 34, {"1986-Q4": 31}
    )
    hole = 4 * 16 + 3
    for seed, (moved, lows, highs, layout, _facts, text) in zip(
        (3, 8), _settled(described, (3, 8), monkeypatch)
    ):
        assert layout.low is not None
        assert any(
            moved[rank] == lows[rank] == highs[rank] == hole for rank in range(layout.low.rows)
        ), f"seed {seed}: no low-tail rank's stratum is the missing quarter"
        written = {line for line in text.split("\n")[1:] if line} - {"1986-Q4"}
        assert len(written) == block["n_distinct"], f"seed {seed}: {len(written)} different quarters"
        missed = set(kpi_shapes.missed(kpi_shapes.measure(described, text, f"stuckq-{seed}.csv")))
        assert {
            "c:holes.by_source.1986-Q4", "c:presence.n_present", "c:date-ladder.p25",
            "c:tails.low.boundary", "c:markers.upper",
        } <= missed, f"seed {seed}: {sorted(missed)}"


# 115 unpadded day-first dates over 58 days from 22/9/1959 and 65 cells of
# 8/11/1959 declared missing, at a floor of 36 (column 800101 of the
# day-first hole battery in `tests/test_p4d361_compared_reaches.py`).
_WIDER_HOLE_COUNTS = (
    2, 0, 1, 5, 2, 1, 4, 1, 2, 2, 0, 0, 0, 0, 6, 2, 3, 6, 1, 2, 0, 0, 1, 3,
    3, 0, 0, 0, 0, 0, 3, 0, 3, 2, 0, 4, 1, 0, 2, 0, 4, 4, 3, 4, 7, 7, 4, 0,
    7, 4, 0, 1, 2, 4, 1, 0, 0, 1,
)


def test_a_stuck_rank_written_in_another_width_holds_one_day_more(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A recorded limit (plan P4-D358): the stuck rank's cell is a present day.

    A high-tail rank whose stratum is 8/11/1959 alone stands there at
    seeds 7 and 13. The column publishes no width census, so the twin
    writes the day padded, `08/11/1959`, which is not the absent spelling:
    the passes counted that day as absent, the twin holds one day more
    than published, and exactly the two distinct counts are MISSED. A
    repair that counts it as present turns this red.
    """
    cells: "list[str]" = []
    for step, count in enumerate(_WIDER_HOLE_COUNTS):
        day = datetime.date(1959, 9, 22) + datetime.timedelta(days=step)
        cells += [f"{day.day}/{day.month}/{day.year}"] * count
    cells += ["8/11/1959"] * 65
    random.Random(800101).shuffle(cells)
    described = _described_with_a_missing_day(tmp_path, "wider_hole", cells, 36, "8/11/1959")
    block = described.document["columns"][0]
    assert (block["format"], block["n_distinct"], block["date_field_widths"]) == ("day-first-date", 38, {})
    hole = _day_number("1959-11-08")
    for seed, (moved, lows, highs, layout, _facts, text) in zip(
        (7, 13), _settled(described, (7, 13), monkeypatch)
    ):
        assert layout.high is not None
        assert any(
            moved[rank] == lows[rank] == highs[rank] == hole
            for rank in range(len(moved) - layout.high.rows, len(moved))
        ), f"seed {seed}: no high-tail rank's stratum is the missing day"
        written = [line for line in text.split("\n")[1:] if line]
        assert "08/11/1959" in written, f"seed {seed}"
        assert len(set(written) - {"8/11/1959"}) == block["n_distinct"] + 1, f"seed {seed}"
        missed = set(kpi_shapes.missed(kpi_shapes.measure(described, text, f"wider-{seed}.csv")))
        assert missed == {"c:distinct.n_distinct", "c:distinct.n_distinct_folded"}, f"seed {seed}: {sorted(missed)}"


def test_a_minute_on_a_missing_moment_is_written_absent_and_named(tmp_path: pathlib.Path) -> None:
    """A recorded limit (plan P4-D358): a column counted in minutes names no hole.

    210 stamps written `yyyy/mm/dd hh:mm` over 362 minutes, with 20 cells
    of `2021/05/03 10:24`, a minute inside their range no present cell
    holds, declared missing, at a floor of eleven. The member has one
    mark to write, so nothing keeps a rank off that minute: at seed 0 the
    twin writes present ranks with it, and they read back absent. The
    twin's report names them rather than passing them in silence. A
    repair that offers no rank the missing minute turns this red and
    restates the record.
    """
    draw = random.Random(8803)
    rows = draw.randrange(120, 300)
    start = datetime.datetime(2021, 5, 3, 8, 0)
    span = draw.randrange(60, 400)
    weights = [draw.lognormvariate(0, 1.2) if draw.random() > 0.4 else 0 for _minute in range(span)]
    picks = draw.choices(range(span), weights=weights, k=rows)

    def stamp(minute: int) -> str:
        return (start + datetime.timedelta(minutes=minute)).strftime("%Y/%m/%d %H:%M")

    hole = stamp(draw.randrange(5, span - 5))
    cells = [stamp(minute) for minute in picks] + [hole] * draw.choice((11, 20))
    draw.shuffle(cells)
    assert (rows, span, hole, hole in {stamp(minute) for minute in picks}) == (
        210, 362, "2021/05/03 10:24", False
    )
    described = _described_with_a_missing_day(tmp_path, "minute_hole", cells, 11, hole)
    block = described.document["columns"][0]
    assert (block["format"], block["time_precision"]) == ("slashed-iso-datetime", "minute")
    twin = generation.generate(described.loaded, 0)
    written = rendering.twin_csv(twin).split("\n")[1:]
    assert written.count(hole) > block["missing_by_source"][hole]
    named = [
        deviation for deviation in twin.deviations
        if deviation.fact == "n_present" and "spelling the table declares absent" in deviation.achieved
    ]
    assert named, [(deviation.fact, deviation.achieved) for deviation in twin.deviations]

# ======================================================================
# LANDING 3b.1 (plan P4-D355): THE WEEKDAY CENSUS OF A COLUMN OF DATES,
# as landing 3b.G (plan P4-D365) left it.
#
# "Weekend share and weekday come back; no calendar count below the
# floor." A column of whole dates publishes which days of the week its
# body falls on, in groups the floor alone chooses from a fixed menu.
# Since plan P4-D365 (the owner's principle of 2026-10-01: the threat is
# a HIPAA exposure, never a reader rebuilding counts) the census the
# menu offers is published wherever its twin can meet it: the full-fill
# certificate, its bands, its cap, its ties refusal and WC5, WC7, WC8 and
# WC9 are gone. The producer withholds where a group holds too few
# different dates (`calendar_rules.few_dates`) or the published holes
# other than width holes leave a group too little room
# (`calendar_rules.room_short`), and the loader holds a census to its shape (`calendar_rules.shape_breach`).
# The clauses below are the landing's: the battery keeps every census
# and its twins meet them with nothing missed and the weekday statistics
# inside their scoped bounds; each rule has a seeded witness publishing
# what the rule derives, its published twins meeting it; and a validate
# run never produces a census.
# ======================================================================

_LINE = 11
_BATTERY_DAYS = [datetime.date(2023, 1, 1) + datetime.timedelta(days=step) for step in range(731)]
_SEASON = [1.0 + 0.25 * math.cos(2 * math.pi * (day.month - 1) / 12) for day in _BATTERY_DAYS]


def _battery_admissions(rows: int) -> "dict[str, list[str]]":
    """Admission days, Monday heaviest and the weekend lightest, a winter season."""
    draw = random.Random(rows)
    weights = [_WEEKDAY[day.weekday()] * _SEASON[step] for step, day in enumerate(_BATTERY_DAYS)]
    return {"admission_date": [draw.choices(_BATTERY_DAYS, weights=weights, k=1)[0].isoformat() for _ in range(rows)]}


_BIRTH_YEARS = list(range(1935, 2006))
_BIRTH_WEIGHTS = [math.exp(-((year - 1958) / 16.0) ** 2) + 0.15 for year in _BIRTH_YEARS]


def _battery_heaps(rows: int) -> "dict[str, list[str]]":
    """Billing on the 1st and 15th for four rows in ten; births heaped on 1 January and firsts."""
    draw = random.Random(3000 + rows)
    billing: "list[str]" = []
    births: "list[str]" = []
    for _row in range(rows):
        if draw.random() < 0.40:
            day = draw.choice(_BATTERY_DAYS)
            bill = datetime.date(day.year, day.month, draw.choice((1, 15)))
        else:
            bill = draw.choice(_BATTERY_DAYS)
        year = draw.choices(_BIRTH_YEARS, weights=_BIRTH_WEIGHTS, k=1)[0]
        pick = draw.random()
        if pick < 0.06:
            born = datetime.date(year, 1, 1)
        elif pick < 0.15:
            born = datetime.date(year, draw.randint(1, 12), 1)
        else:
            first = datetime.date(year, 1, 1)
            born = first + datetime.timedelta(days=draw.randrange((datetime.date(year + 1, 1, 1) - first).days))
        billing += [bill.isoformat()]
        births += [born.isoformat()]
    return {"billing_date": billing, "birth_date": births}


_MONDAYS = [day for day in _BATTERY_DAYS if day.weekday() == 0]
_CYCLE = [
    datetime.date(2023, 1, 3) + datetime.timedelta(days=28 * step)
    for step in range(40)
    if datetime.date(2023, 1, 3) + datetime.timedelta(days=28 * step) <= datetime.date(2024, 12, 31)
]
_TENTHS = [datetime.date(year, month, 10) for year in (2023, 2024) for month in range(1, 13)]


def _battery_schedules(rows: int) -> "dict[str, list[str]]":
    """A weekly clinic on Mondays, a 28-day cycle and a monthly visit, one in ten moved."""
    draw = random.Random(5000 + rows)
    weekly: "list[str]" = []
    cycle: "list[str]" = []
    monthly: "list[str]" = []

    def moved(day: datetime.date) -> datetime.date:
        return day + datetime.timedelta(days=draw.choice((-3, -2, -1, 1, 2, 3)))

    for _row in range(rows):
        week = draw.choice(_MONDAYS)
        if draw.random() >= 0.90:
            week = week + datetime.timedelta(days=draw.choice((1, 2, 3)))
        turn = draw.choice(_CYCLE)
        if draw.random() >= 0.90:
            turn = moved(turn)
        tenth = draw.choice(_TENTHS)
        if draw.random() >= 0.90:
            tenth = moved(tenth)
        weekly += [week.isoformat()]
        cycle += [turn.isoformat()]
        monthly += [tenth.isoformat()]
    return {"weekly_clinic": weekly, "cycle_28": cycle, "monthly_visit": monthly}


_BATTERY = {
    "admissions": _battery_admissions,
    "heaps": _battery_heaps,
    "schedules": _battery_schedules,
}


def _table_text(columns: "dict[str, list[str]]") -> str:
    names = list(columns)
    rows = len(columns[names[0]])
    lines = [",".join(names)]
    for row in range(rows):
        lines += [",".join(columns[name][row] for name in names)]
    return "\n".join(lines) + "\n"


def _days_of(cells: "list[str]") -> "list[int]":
    """The day of every ISO cell, counted from 1970-01-01, ascending."""
    return sorted(_day_number(cell) for cell in cells if cell)


def _decided(block: dict, cells: "list[str]", floor: int = 11, holes: "tuple[str, ...]" = ()) -> taxonomy.WeekdayDecision:
    """The producer's decision for this block, asked again."""
    return taxonomy.weekday_decision(
        block,
        tuple(_days_of(cells)),
        block["n_distinct"],
        taxonomy.Settings(small_cell_floor=floor, declared_missing_values=holes),
        texts=len({cell for cell in cells if cell}),
    )


def _groups(block: dict) -> "tuple[tuple[int, int, int], ...]":
    return tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])


def _twins_meet(described: kpi_shapes.Described, seeds: "tuple[int, ...]" = (0, 1, 2)) -> "list[tuple[int, list[str]]]":
    """Every seed whose twin misses a check, with what it misses."""
    found: "list[tuple[int, list[str]]]" = []
    for seed in seeds:
        missed = kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"twin-{seed}.csv"))
        if missed:
            found += [(seed, missed)]
    return found


def _weekday_statistics(cells: "list[str]") -> "tuple[float, list[float]]":
    """The weekend share and the share of each weekday, over every cell."""
    counts = [0] * 7
    for cell in cells:
        counts[datetime.date.fromisoformat(cell[:10]).weekday()] += 1
    total = sum(counts)
    return (counts[5] + counts[6]) / total, [count / total for count in counts]


def _statistics_failures(block: dict, real: "list[str]", twin: "list[str]") -> "list[str]":
    """The scoped statistics clauses of the gate (BOUND, CAP, SHAPE), for one twin.

    BOUND holds everywhere: the twin's weekend share and weekday
    distribution lie within `(tail cells + cells the census leaves
    unresolved) / parsed` of the real column's. CAP and SHAPE hold where
    the census resolves the statistic, on tables of 1,000 rows or more:
    the bound itself at most 0.10 below 10,000 rows and 0.02 from them,
    and the twin's gap at most a quarter of the real column's distance
    from flat wherever that distance is three times its sampling scale.
    """
    parsed = block["n_present"] - block["n_unparsed"]
    groups = block["weekday_census"]
    tails = block["low_tail"]["rows"] + block["high_tail"]["rows"]
    mixed = sum(group["count"] for group in groups if group["first"] <= 4 and group["last"] >= 5)
    joined = sum(group["count"] for group in groups if group["last"] > group["first"])
    real_weekend, real_share = _weekday_statistics(real)
    twin_weekend, twin_share = _weekday_statistics(twin)
    found: "list[str]" = []
    for statistic in ("weekend", "weekday"):
        unresolved = mixed if statistic == "weekend" else joined
        bound = (tails + unresolved) / parsed
        if statistic == "weekend":
            gap = abs(twin_weekend - real_weekend)
            flat = abs(real_weekend - 2 / 7)
            scale = (real_weekend * (1 - real_weekend) / len(real)) ** 0.5
        else:
            gap = 0.5 * sum(abs(a - b) for a, b in zip(twin_share, real_share))
            flat = 0.5 * sum(abs(a - 1 / 7) for a in real_share)
            scale = 0.5 * sum((q * (1 - q) / len(real)) ** 0.5 for q in real_share)
        if gap > bound + 1e-12:
            found += [f"BOUND {statistic}: {gap:.4f} > {bound:.4f}"]
        if unresolved == 0 and parsed >= 1000:
            cap = 0.02 if parsed >= 10000 else 0.10
            if bound > cap:
                found += [f"CAP {statistic}: {bound:.4f} > {cap}"]
            if flat > 3 * scale and gap > 0.25 * flat:
                found += [f"SHAPE {statistic}: {gap:.4f} > a quarter of {flat:.4f}"]
    return found


@pytest.mark.parametrize("shape", sorted(_BATTERY))
def test_the_battery_keeps_its_weekday_census(tmp_path: pathlib.Path, shape: str) -> None:
    """Every date column of the battery publishes its seven counts, held to its shape.

    At 1,000 rows and a floor of eleven each of the six columns -- two
    years of admissions, billing dates heaped on the 1st and 15th, birth
    dates over seventy years, a weekly Monday clinic, a 28-day cycle and a
    monthly visit -- publishes the seven weekday counts, the clinic's
    empty Friday to Sunday as one group of nought: every count nought or
    at least the line, adding up to the body, and the loader's own check
    (`calendar_rules.shape_breach`) finding nothing. The real table's own
    census is the body's, weekday by weekday.
    """
    columns = _BATTERY[shape](1000)
    described = kpi_shapes.describe(tmp_path, shape, _table_text(columns), 11)
    for name, cells in columns.items():
        block = described.block(name)
        groups = _groups(block)
        assert calendar_rules.entry_of(groups) == calendar_rules.ENTRY_SEVEN, (name, groups)
        days = _days_of(cells)
        body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
        assert all(calendar_rules.calendar_floor_ok(count, _LINE) for _first, _last, count in groups), groups
        assert calendar_rules.group_counts(groups, calendar_rules.body_bins(body)) == [count for _f, _l, count in groups]
        assert calendar_rules.shape_breach(groups, len(body), _LINE, True) is None
        assert _decided(block, cells).reason == "", name


@pytest.mark.parametrize("shape", sorted(_BATTERY))
def test_the_battery_twins_meet_their_census(tmp_path: pathlib.Path, shape: str) -> None:
    """Clause (d) and the statistics clauses, at seeds 0 and 4 of the 1,000-row battery.

    Every twin validates with nothing missed -- its weekday census HELD
    among the rest -- and its weekend share and weekday distribution lie
    inside the scoped bounds (`_statistics_failures`). The real table
    validates with nothing missed too. PRICE: a census counting days
    together is priced, not asserted -- no battery column counts any.
    """
    columns = _BATTERY[shape](1000)
    text = _table_text(columns)
    described = kpi_shapes.describe(tmp_path, shape, text, 11)
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == []
    for seed in (0, 4):
        written = kpi_shapes.twin_text(described, seed)
        outcome = kpi_shapes.measure(described, written, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], (shape, seed)
        held = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
        assert len(held) == len(columns) and all(check.verdict == validation.HELD for check in held)
        rows = [line.split(",") for line in written.splitlines()[1:] if line]
        header = written.splitlines()[0].split(",")
        for name, cells in columns.items():
            twin = [row[header.index(name)] for row in rows]
            failures = _statistics_failures(described.block(name), cells, twin)
            assert failures == [], (shape, name, seed, failures)


# THE EXPECTED PUBLICATIONS: a seeded witness per rule, each asserting
# what that rule derives (plans P4-D355 and P4-D365).


def _walk_case(seed: int) -> "list[str]":
    """1,001 different dates: dense runs and two sparse stretches, no day repeated."""
    draw = random.Random(8100 + seed)
    state = [datetime.date(2019, 1, 7)]
    cells: "list[datetime.date]" = []

    def dense(count: int) -> "list[datetime.date]":
        found = [state[0] + datetime.timedelta(days=step) for step in range(count)]
        state[0] = state[0] + datetime.timedelta(days=count)
        return found

    def sparse(count: int, span: int, saturdays: int, ranks: "list[int]") -> "list[datetime.date]":
        days = [state[0] + datetime.timedelta(days=step) for step in range(span)]
        while days[-1].weekday() == 5:
            days = days[:-1]
        state[0] = days[-1] + datetime.timedelta(days=1)
        while True:
            on = [day for day in days[:-1] if day.weekday() == 5]
            off = [day for day in days[:-1] if day.weekday() != 5]
            chosen = sorted(draw.sample(on, saturdays) + draw.sample(off, count - 1 - saturdays)) + [days[-1]]
            if all(chosen[rank].weekday() != 5 for rank in ranks + [count - 1]):
                return chosen

    cells += dense(11) + dense(40)
    cells += sparse(200, 600, 3, [49])
    cells += dense(250)
    cells += sparse(400, 1200, 4, [249])
    cells += dense(100)
    texts = [day.isoformat() for day in cells]
    draw.shuffle(texts)
    return texts


def _thin_midweek(seed: int) -> "list[str]":
    """Mondays and Tuesdays heavy, Wednesday on 6 days and Thursday on 8, nothing Friday to Sunday."""
    draw = random.Random(seed)
    start = datetime.date(2023, 1, 2)
    end = start + datetime.timedelta(days=7 * 104)

    def on(first: datetime.date, last: datetime.date, weekday: int) -> "list[datetime.date]":
        day = first
        while day.weekday() != weekday:
            day += datetime.timedelta(days=1)
        found: "list[datetime.date]" = []
        while day <= last:
            found += [day]
            day += datetime.timedelta(days=7)
        return found

    cells = [start] * 11
    low = on(start + datetime.timedelta(days=1), end, 2)[0]
    high = on(start, end - datetime.timedelta(days=3), 3)[-1]
    beyond = high + datetime.timedelta(days=1)
    while beyond.weekday() in (2, 3):
        beyond += datetime.timedelta(days=1)
    cells += [beyond] * 11
    for weekday in (0, 1):
        for day in on(low + datetime.timedelta(days=1), high - datetime.timedelta(days=1), weekday):
            cells += [day] * draw.randint(0, 4)
    wednesdays = on(low + datetime.timedelta(days=1), high - datetime.timedelta(days=1), 2)
    thursdays = on(low + datetime.timedelta(days=1), high - datetime.timedelta(days=1), 3)
    cells += [low] + draw.sample(wednesdays, 5)
    cells += [high] + draw.sample(thursdays, 7)
    draw.shuffle(cells)
    return [day.isoformat() for day in cells]


def _twenty_sessions(seed: int) -> "list[str]":
    """Twenty session dates on weekdays over five months, 30 to 80 rows each, a thin spread beside."""
    draw = random.Random(1000 + seed)
    start = datetime.date(2024, 1, 8)
    weekdays = [start + datetime.timedelta(days=step) for step in range(150)
                if (start + datetime.timedelta(days=step)).weekday() < 5]
    cells: "list[str]" = []
    for day in sorted(draw.sample(weekdays, 20)):
        cells += [day.isoformat()] * (30 + draw.randrange(51))
    spread = len(cells) // 19
    for _cell in range(spread):
        cells += [(start + datetime.timedelta(days=draw.randrange(150))).isoformat()]
    draw.shuffle(cells)
    return cells


def _seven_sessions(seed: int) -> "list[str]":
    """Seven session dates, one per weekday, each tail on one date."""
    draw = random.Random(seed)
    start = datetime.date(2024, 3, 4)
    cells: "list[str]" = []
    for offset in (0, 1, 16, 17, 32, 33, 34):
        cells += [(start + datetime.timedelta(days=offset)).isoformat()] * (140 + draw.randrange(25))
    cells += [(start - datetime.timedelta(days=10)).isoformat()] * 12
    cells += [(start + datetime.timedelta(days=44)).isoformat()] * 12
    draw.shuffle(cells)
    return cells


def _one_week(rows: int, seed: int) -> "list[str]":
    """A body of one week, its span widened by two far boundary cells."""
    draw = random.Random(seed)
    base = datetime.date(2024, 1, 1)
    days = [base + datetime.timedelta(days=step) for step in range(11)] + [base + datetime.timedelta(days=12)]
    week = base + datetime.timedelta(days=21)
    for _row in range(rows - 24):
        days += [week + datetime.timedelta(days=draw.choices(range(7), [30, 25, 20, 15, 6, 2, 2])[0])]
    high = base + datetime.timedelta(days=45)
    days += [high] + [high + datetime.timedelta(days=2 + step) for step in range(11)]
    draw.shuffle(days)
    return [day.isoformat() for day in days]


def _business_days(extra: int, seed: int) -> "list[str]":
    """One row per business day over about four and a half years, and `extra` more."""
    draw = random.Random(100 + seed)
    day = datetime.date(2020, 1, 6)
    days: "list[datetime.date]" = []
    while len(days) < 1180:
        if day.weekday() < 5:
            days += [day]
        day += datetime.timedelta(days=1)
    cells = [each.isoformat() for each in days]
    cells += [each.isoformat() for each in draw.sample(days[20:-20], extra)]
    draw.shuffle(cells)
    return cells


def _one_month_wide(rows: int, seed: int) -> "list[str]":
    """The bulk inside March 2024, twelve cells each side about three months away."""
    draw = random.Random(500 + seed)
    march = [datetime.date(2024, 3, day) for day in range(1, 32)]
    weights = [3.0 if day.weekday() < 5 else 1.0 for day in march]
    weights[29] = 0.12
    low = datetime.date(2024, 3, 1) - datetime.timedelta(days=85)
    high = datetime.date(2024, 3, 31) + datetime.timedelta(days=85)
    days = [low - datetime.timedelta(days=1 + step) for step in range(11)] + [low]
    days += [draw.choices(march, weights)[0] for _row in range(rows - 24)]
    days += [high] + [high + datetime.timedelta(days=1 + step) for step in range(11)]
    draw.shuffle(days)
    return [day.isoformat() for day in days]


def _payroll(rows: int, seed: int) -> "list[str]":
    """Payroll on the 15th and the last day of 24 months, written as dates (plan P4-D365).

    The 3b.2-W skeptic's shape cut to its days: 48 dates, six or seven
    of them on each weekday.
    """
    draw = random.Random(seed)
    days: "list[datetime.date]" = []
    for step in range(24):
        year, month = 2023 + step // 12, 1 + step % 12
        days += [datetime.date(year, month, 15)]
        following = datetime.date(year + (month == 12), 1 if month == 12 else month + 1, 1)
        days += [following - datetime.timedelta(days=1)]
    return [draw.choice(days).isoformat() for _row in range(rows)]


def _monthly(day: int, start: int, months: int, seed: int) -> "list[str]":
    """One date a month, the `day`th, over `months` months from January of `start`; 1,000 rows.

    The shape of the guard drop's review (its `monthly3` battery): over
    51 to 54 months the body holds 7.00 to 7.43 dates a weekday group,
    which the mean of seven published and whose twins held 53 or 54
    different days for 52.
    """
    draw = random.Random(seed)
    days = [datetime.date(start + step // 12, 1 + step % 12, day) for step in range(months)]
    return [draw.choice(days).isoformat() for _row in range(1000)]


def _tie_days(rows: int, count: int, seed: int) -> "list[str]":
    """`count` days drawn from two years, every row on one of them (the 3b.2-W skeptic's ties)."""
    plan = random.Random(seed)
    days = sorted(plan.sample(_TWO_YEARS, count))
    draw = random.Random(seed + 1)
    cells: "list[str]" = []
    for _row in range(rows):
        cells += [draw.choice(days).isoformat()]
        # The skeptic's shape drew its one clock for every cell too.
        draw.choice(("09:00:00",))
    return cells


_HOLE_DAY = "2024-01-01"


def _with_a_declared_day(seed: int) -> "list[str]":
    """Dates over two years, weekday-shaped, six in a hundred written 2024-01-01."""
    draw = random.Random(700 + seed)
    cells: "list[str]" = []
    for _row in range(1000):
        if draw.random() < 0.06:
            cells += [_HOLE_DAY]
            continue
        while True:
            day = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(731))
            if day.weekday() < 5 or draw.random() < 0.3:
                break
        cells += [day.isoformat()]
    return cells


# name -> (column name, cells, the groups expected or [] with the reason word)
_EXPECTED = {
    "walkcase4_s0": (
        "seen_on", lambda: _walk_case(0),
        [(0, 0, 141), (1, 1, 159), (2, 2, 160), (3, 3, 148), (4, 4, 159), (5, 5, 61), (6, 6, 151)], "",
    ),
    "gr_wedthu_6_8_s1": ("visit_date", lambda: _thin_midweek(1), [(0, 4, 453), (5, 6, 0)], ""),
    "sessions20_s0": (
        "session_date", lambda: _twenty_sessions(0),
        [(0, 0, 352), (1, 1, 201), (2, 2, 261), (3, 3, 114), (4, 4, 143), (5, 6, 16)], "",
    ),
    "k7_sessions_s0": ("session_date", lambda: _seven_sessions(0), [], calendar_rules.REASON_FEW_DATES),
    "B2_oneweek_1201_s0": ("visit_date", lambda: _one_week(1201, 0), [], calendar_rules.REASON_FEW_DATES),
    "bizlog_x1_s1": (
        "log_date", lambda: _business_days(1, 1),
        [(0, 0, 231), (1, 1, 232), (2, 2, 232), (3, 3, 233), (4, 4, 231), (5, 6, 0)], "",
    ),
    "w_month_wide_1000_s0": ("visit_date", lambda: _one_month_wide(1000, 0), [], calendar_rules.REASON_FEW_DATES),
    "payroll_1000": ("paid_on", lambda: _payroll(1000, 86004), [], calendar_rules.REASON_FEW_DATES),
    "first_2021_52m": ("report_on", lambda: _monthly(1, 2021, 52, 9740), [], calendar_rules.REASON_FEW_DATES),
    "tenth_2021_54m": ("report_on", lambda: _monthly(10, 2021, 54, 9802), [], calendar_rules.REASON_FEW_DATES),
    "ties40_1000": ("seen_on", lambda: _tie_days(1000, 40, 83040), [], calendar_rules.REASON_FEW_DATES),
    "ties60_1000": (
        "seen_on", lambda: _tie_days(1000, 60, 83060),
        [(0, 0, 134), (1, 1, 158), (2, 2, 127), (3, 3, 204), (4, 4, 123), (5, 5, 104), (6, 6, 107)], "",
    ),
}


@pytest.mark.parametrize("name", sorted(_EXPECTED))
def test_each_rule_publishes_what_it_derives(tmp_path: pathlib.Path, name: str) -> None:
    """The seeded witnesses of the rules, each publishing what its rule derives (plan P4-D365).

    * `walkcase4_s0` (1,001 different dates, no day repeated) and
      `bizlog_x1_s1` (one row a business day and one more) publish the
      census the menu offers: the ties refusal that withheld them, no
      date able to hold eleven rows, is retired with the certificate.
    * `gr_wedthu_6_8_s1`: Wednesday on six days and Thursday on eight,
      so neither the seven counts nor the weekend grouping holds the line
      in every group: entry 3, `[Mon-Fri] [Sat-Sun]`.
    * `sessions20_s0`: every weekday alone reaches the line, the weekend
      together does too: entry 2.
    * `k7_sessions_s0` (one session date a weekday), `B2_oneweek_1201_s0`
      (one week), `ties40_1000` (forty days, one weekday holding one) and
      `w_month_wide_1000_s0` (one March, four or five dates a weekday)
      hold a group of fewer than three different dates, or fewer than
      seven and a half a group on average: withheld, `few_dates`. So
      does `payroll_1000`, 48 dates on the 15th and the last day of 24
      months, 6.9 a weekday on average, and so do `first_2021_52m` and
      `tenth_2021_54m`, one date a month over 52 and 54 months: 50 and
      52 body dates, 7.14 and 7.43 a weekday on average, which the mean
      of seven published (the review of the guard drop, item 1). Published
      without the rule, the twins of seven sessions, of payroll and of
      one date a month miss their count of different values at seeds 0
      to 2 and one week's its census; forty ties' miss at one seed of three, and one
      March's meet it -- the rule's measured cost (plan P4-D365's B1).
    * `ties60_1000`: sixty days, at least six on each weekday and more
      than seven on average: published.

    Every published census here is met by the twins of seeds 0 to 2 with
    nothing missed, and the real table validates; every withheld one says
    so in the one sentence every rule the table's own numbers decide
    shares.
    """
    column, build, expected, reason = _EXPECTED[name]
    cells = build()
    text = f"{column}\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, name, text, 11)
    block = described.block(column)
    assert list(_groups(block)) == expected, (name, _groups(block))
    decided = _decided(block, cells)
    assert decided.reason == reason, (name, decided.reason)
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == [], name
    if expected:
        assert _twins_meet(described) == [], name
        return
    said = [entry["note"] for entry in described.document["publication_notes"] if entry["column"] == column]
    assert any("and why is not said" in sentence for sentence in said), said


def test_the_few_dates_rule_counts_the_real_dates_of_each_group() -> None:
    """`calendar_rules.few_dates` withholds below three dates a group, or seven and a half a group on average (plan P4-D365).

    Asked of hand-made bodies, Monday 2024-01-01 first: a group of two
    dates is few however many rows they hold; three dates in each of
    seven groups average fewer than seven and a half; one group alone is
    never averaged; seven and eight dates in two groups are enough, and
    seven and seven, or seven and six, are not (the review of the guard
    drop, item 1: one date a month over 52 months, 7.14 a group, came
    back 53 days for 52); and the same body counted as Monday to Friday
    and the weekend holds enough where its seven groups do not. Red when
    the floor of three, the mean of seven and a half, the two-group
    condition, the counting of DATES rather than rows or of groups rather
    than weekdays moves.
    """
    monday = _day_number("2024-01-01")

    def weeks(weekdays: "tuple[int, ...]", count: int, rows: int) -> "list[int]":
        return [monday + 7 * week + weekday for weekday in weekdays for week in range(count) for _row in range(rows)]

    def seven(body: "list[int]") -> "tuple[tuple[int, int, int], ...]":
        bins = calendar_rules.body_bins(body)
        return tuple((weekday, weekday, bins[weekday]) for weekday in range(7))

    two = weeks((0,), 2, 30) + weeks((1, 2, 3, 4, 5, 6), 9, 2)
    assert calendar_rules.few_dates(seven(two), two)
    three = weeks((0, 1, 2, 3, 4, 5, 6), 3, 20)
    assert calendar_rules.few_dates(seven(three), three)
    lone = weeks((2,), 3, 40)
    assert not calendar_rules.few_dates(seven(lone), lone)
    both = weeks((0,), 7, 2) + weeks((1,), 8, 2)
    assert not calendar_rules.few_dates(seven(both), both)
    sevens = weeks((0, 1), 7, 2)
    assert calendar_rules.few_dates(seven(sevens), sevens)
    short = weeks((0,), 7, 2) + weeks((1,), 6, 2)
    assert calendar_rules.few_dates(seven(short), short)
    split = weeks((0, 1, 2, 3, 4), 7, 1) + weeks((5, 6), 6, 1)
    assert calendar_rules.few_dates(seven(split), split)
    assert not calendar_rules.few_dates(((0, 4, 35), (5, 6, 12)), split)


def test_the_room_rule_asks_only_where_holes_leave_no_free_day_for_a_one_row_date() -> None:
    """`calendar_rules.room_short` withholds where a group has no free day and a one-row date (plan P4-D365).

    Two weeks from Monday 2024-01-01, every day holding two rows but
    Tuesday January 2, which holds one, and Tuesday January 9, which holds
    none. With no hole the rule asks nothing -- not even where every day
    holds a date, as a business-day log's weekdays do. With January 9 a hole the
    Tuesday group has no free day for its one-row date: withheld. With
    January 2 given its second row, no date holds one row: published. And
    with the body running on to Sunday January 21, the Tuesday group gains
    a free day, January 16: published. Red when the rule asks without a
    hole, counts a hole as a free day, counts every date rather than the
    one-row dates, or counts the days of the span but not the dates on
    them.
    """
    monday = _day_number("2024-01-01")
    days = [monday + step for step in range(14) if step != 8]
    groups = tuple((weekday, weekday, 1) for weekday in range(7))
    base = [day for day in days for _row in range(2)]
    base.remove(monday + 1)
    hole = (monday + 8,)
    assert not calendar_rules.room_short(groups, base, ())
    full = [monday + step for step in range(14) for _row in range(2)]
    full.remove(monday + 1)
    assert not calendar_rules.room_short(groups, full, ())
    assert calendar_rules.room_short(groups, base, hole)
    assert not calendar_rules.room_short(groups, base + [monday + 1], hole)
    assert not calendar_rules.room_short(groups, base + [monday + 20] * 2, hole)


# THE FORM HOLES (review of landing 3b.1, finding 1): days the censuses of
# written forms tell a reader no cell holds. Since plan P4-D365 they are
# what the twin may not stand a date on, and where May's leave a group no
# free day for a one-row date the room rule withholds; width holes alone
# never ask it.


def _past_the_ninth() -> "list[datetime.date]":
    """Two visits on every day past the ninth, 2025-01-21 to 2025-03-20; eleven-day tails beside.

    Written `m/d/yyyy`, no cell falls on the first to the ninth of a
    month, so the width census names one form, `first-field-unpadded`,
    and the tails hold 2025-01-10 to 01-20 and 2025-03-21 to 03-31, one
    cell a day.
    """
    one = datetime.timedelta(days=1)
    days = [datetime.date(2025, 1, 10) + one * step for step in range(11)]
    days += [datetime.date(2025, 3, 21) + one * step for step in range(11)]
    day = datetime.date(2025, 1, 21)
    while day <= datetime.date(2025, 3, 20):
        if day.day >= 10:
            days += [day, day]
        day += one
    random.Random(11).shuffle(days)
    return days


def _mays_only() -> "list[datetime.date]":
    """Every day of May 2023 to May 2025 between the tails, one or two cells; eleven-day tails.

    Written `17 May 2023`, every cell is in May, so the month-name
    census names one form of length `either`; the tails hold 2023-05-01
    to 05-11 and 2025-05-21 to 05-31.
    """
    one = datetime.timedelta(days=1)
    days = [datetime.date(2023, 5, 1) + one * step for step in range(11)]
    days += [datetime.date(2025, 5, 21) + one * step for step in range(11)]
    body = [
        datetime.date(year, 5, 1) + one * step
        for year in (2023, 2024, 2025)
        for step in range(31)
        if datetime.date(2023, 5, 12) <= datetime.date(year, 5, 1) + one * step <= datetime.date(2025, 5, 20)
    ]
    for place, day in enumerate(body):
        days += [day] * (1 if place % 5 == 0 else 2)
    random.Random(5).shuffle(days)
    return days


def _october_to_december() -> "list[datetime.date]":
    """Two visits on every day of October to December between the tails, over two years; eleven-day tails.

    The tails hold 2024-11-15 to 11-25 and 2025-10-21 to 10-31, one cell
    a day, and the body 2024-12-01 to 2025-10-20, so every day of
    January to September between the boundaries holds none.
    """
    one = datetime.timedelta(days=1)
    days = [datetime.date(2024, 11, 15) + one * step for step in range(11)]
    days += [datetime.date(2025, 10, 21) + one * step for step in range(11)]
    day = datetime.date(2024, 12, 1)
    while day <= datetime.date(2025, 10, 20):
        if day.month >= 10:
            days += [day, day]
        day += one
    random.Random(7).shuffle(days)
    return days


def _month_first(day: datetime.date) -> str:
    return f"{day.month}/{day.day}/{day.year}"


def _day_first(day: datetime.date) -> str:
    return f"{day.day}/{day.month}/{day.year}"


# name -> (the days, how each is written, the one form the censuses of
# written forms name, which days a reader holds empty). A one-field width
# word leaves empty every day whose OTHER field is below ten: the day of
# a month-first member, the month of a day-first one.
_FORM_HOLES = {
    "past_the_ninth": (
        _past_the_ninth, _month_first, "first-field-unpadded", lambda day: day.day < 10,
    ),
    "past_the_ninth_day_first": (
        _past_the_ninth, _day_first, "second-field-unpadded", lambda day: day.day < 10,
    ),
    "october_to_december_month_first": (
        _october_to_december, _month_first, "second-field-unpadded", lambda day: day.month < 10,
    ),
    "october_to_december_day_first": (
        _october_to_december, _day_first, "first-field-unpadded", lambda day: day.month < 10,
    ),
    "mays_only": (
        _mays_only, lambda day: f"{day.day} May {day.year}", "title-either-space-no-comma",
        lambda day: day.month != 5,
    ),
}

# name -> the reason the census is withheld for, or "" where it is published.
_FORM_HOLE_REASONS = {
    "past_the_ninth": calendar_rules.REASON_FEW_DATES,
    "past_the_ninth_day_first": calendar_rules.REASON_FEW_DATES,
    "october_to_december_month_first": calendar_rules.REASON_FEW_DATES,
    "october_to_december_day_first": calendar_rules.REASON_FEW_DATES,
    "mays_only": calendar_rules.REASON_ROOM,
}


@pytest.mark.parametrize("name", sorted(_FORM_HOLES))
def test_a_day_the_form_censuses_leave_empty_is_a_hole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    """A day the form censuses leave empty is a hole, and the room rule reads May's alone.

    `past_the_ninth` publishes `date_field_widths {first-field-unpadded}`
    and `mays_only` `month_name_styles {title-either-space-no-comma}`, so
    the first to the ninth of every month, and every day outside May, are
    holes; the same days past the ninth written `d/m/yyyy` publish
    `{second-field-unpadded}`, whose other field is the day; two years of
    October to December publish `{second-field-unpadded}` written
    `m/d/yyyy` and `{first-field-unpadded}` written `d/m/yyyy`, whose
    other field is the month either way. The holes are exactly those
    days, and no body date stands on one. Then:

    * the days past the ninth hold 6.8 dates a weekday on average, and
      October to December 7.3: withheld, `few_dates`. Under the mean of
      seven October to December published and its twins met it; the
      mean of seven and a half withholds it, the cost the review of the
      guard drop (item 1) priced. A column past the ninth that publishes
      and is met is `_straddling_february`;
    * every day of three Mays holds a date, some of them one row, so no
      group has a free day: withheld, `room`. With the room rule
      withdrawn the census publishes and its twin holds 83 different
      values for 93, both distinct counts MISSED (plan P4-D365).

    The month-name census is what asks the room rule
    (`calendar_rules.may_only_published`): true of the Mays alone.
    """
    build, written, form, empty = _FORM_HOLES[name]
    dates = build()
    text = "visit\n" + "".join(f"{written(day)}\n" for day in dates)
    described = kpi_shapes.describe(tmp_path, name, text, 11)
    block = described.block("visit")
    named = block["month_name_styles"] if block["format"].startswith("textual-") else block["date_field_widths"]
    assert list(named) == [form], (block["format"], named)
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    low, high = body[0], body[-1]
    epoch = datetime.date(1970, 1, 1)
    forms = {census: dict(block[census] or {}) for census in calendar_rules.FORM_CENSUSES}
    holes = set(calendar_rules.form_holes(forms, block["format"], low, high))
    assert holes == {day for day in range(low, high + 1) if empty(epoch + datetime.timedelta(days=day))}
    assert holes and not holes & set(body)
    assert calendar_rules.may_only_published(forms, block["format"]) == (name == "mays_only")
    decided = taxonomy.weekday_decision(
        block, tuple(days), block["n_distinct"], taxonomy.Settings(small_cell_floor=11),
        texts=len(set(days)),
    )
    assert decided.reason == _FORM_HOLE_REASONS[name], decided.reason
    assert block["weekday_census"] == [] and decided.said == calendar_rules.REASON_UNSAID
    said = [entry["note"] for entry in described.document["publication_notes"]]
    assert any("and why is not said" in sentence for sentence in said), said
    if name != "mays_only":
        return
    with monkeypatch.context() as roomy:
        roomy.setattr(calendar_rules, "room_short", lambda *_arguments: False)
        unruled = kpi_shapes.describe(tmp_path / "unruled", name, text, 11)
        assert calendar_rules.entry_of(_groups(unruled.block("visit"))) == calendar_rules.ENTRY_SEVEN
        missed = kpi_shapes.missed(kpi_shapes.measure(unruled, kpi_shapes.twin_text(unruled, 0), "unruled-0.csv"))
    assert "visit:distinct.n_distinct" in missed, missed


def _straddling_february() -> "list[datetime.date]":
    """981 visits past the ninth, 2024-01-10 to 04-30, with 120 on January 31 and 250 on February 10.

    Written `m/d/yyyy`, the width census names `first-field-unpadded`.
    The two heavy days are consecutive knot days of the ladder, so the
    open stretch between them is the first to the ninth of February:
    every day of it a hole.
    """
    draw = random.Random(0)

    def open_days(first: datetime.date, last: datetime.date) -> "list[datetime.date]":
        span = [first + datetime.timedelta(days=step) for step in range((last - first).days + 1)]
        return [day for day in span if day.day >= 10]

    early = open_days(datetime.date(2024, 1, 21), datetime.date(2024, 1, 30))
    late = open_days(datetime.date(2024, 2, 11), datetime.date(2024, 4, 30))
    days = [datetime.date(2024, 1, 10) + datetime.timedelta(days=step) for step in range(11)]
    days += [draw.choices(early, [_WEEKDAY[day.weekday()] for day in early])[0] for _row in range(150)]
    days += [datetime.date(2024, 1, 31)] * 120 + [datetime.date(2024, 2, 10)] * 250
    days += [draw.choices(late, [_WEEKDAY[day.weekday()] for day in late])[0] for _row in range(450)]
    draw.shuffle(days)
    return days


def test_a_full_column_between_width_holes_publishes_and_its_twins_meet_it(tmp_path: pathlib.Path) -> None:
    """The room rule is not asked beside width holes: a heavy column past the ninth publishes (review of 3b.G, item 3).

    `_straddling_february`'s width census leaves the first to the ninth
    of every month empty, and every other day from January 21 to April 30
    holds a date: 981 visits, two of them alone on a Saturday and a
    Sunday, so no group has a free day for a one-row date. The room rule
    withheld it while it was asked beside every hole; the review of the
    guard drop measured 40 columns past the ninth that it withheld and
    none whose twins missed the census without it, and 668f276 published
    this one with its twins meeting it. The rule is now asked beside a
    month-name census holding every cell to May
    (`calendar_rules.may_only_published`) and, since its second review
    (item 1), beside placeholder and declared holes, never beside width
    holes alone: this column publishes the seven counts, and its twins
    meet them at seeds 0 to 4 with nothing missed. Red when the
    room rule is asked beside width holes again.
    """
    dates = _straddling_february()
    text = "seen_on\n" + "".join(f"{day.month}/{day.day}/{day.year}\n" for day in dates)
    described = kpi_shapes.describe(tmp_path, "straddle", text, 11)
    block = described.block("seen_on")
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    forms = {census: dict(block[census] or {}) for census in calendar_rules.FORM_CENSUSES}
    holes = calendar_rules.form_holes(forms, block["format"], body[0], body[-1])
    groups = _groups(block)
    assert calendar_rules.entry_of(groups) == calendar_rules.ENTRY_SEVEN, groups
    assert holes and calendar_rules.room_short(groups, body, holes)
    assert not calendar_rules.may_only_published(forms, block["format"])
    decided = taxonomy.weekday_decision(
        block, tuple(days), block["n_distinct"], taxonomy.Settings(small_cell_floor=11), texts=len(set(days)),
    )
    assert decided.reason == "", decided.reason
    assert _twins_meet(described, (0, 1, 2, 3, 4)) == []


_MONTH_NAMES = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
)

# name -> how each date is written, and the one month-name word its census names.
_MONTH_NAME_COLUMNS = {
    "full_names": (lambda day: f"{day.day} {_MONTH_NAMES[day.month - 1]} {day.year}", "title-full-space-no-comma"),
    "short_names": (lambda day: f"{day.day} {_MONTH_NAMES[day.month - 1][:3]} {day.year}", "title-abbreviated-space-no-comma"),
}


@pytest.mark.parametrize("name", sorted(_MONTH_NAME_COLUMNS))
def test_a_column_of_month_names_over_a_year_is_not_held_to_may_and_publishes(
    tmp_path: pathlib.Path, name: str
) -> None:
    """A month-name census of one word that is not `either` holds no cell to May (second review of 3b.G, item 2).

    1,500 visits drawn over 2023, written `17 March 2023` or
    `17 Mar 2023`: the month-name census names one word, of length
    `full` or `abbreviated`, so no day is a hole, `may_only_published`
    is False, the seven counts publish and the twins of seeds 0 to 2
    meet them with nothing missed. Asked of hand-made censuses, one word
    of length `either` is the Mays (`mays_only` is the column), and two
    words -- the `either` one first -- are not. Red when any one
    month-name word is read as May's (every month-name column then loses
    its census) and when two words are read as one.
    """
    written, word = _MONTH_NAME_COLUMNS[name]
    draw = random.Random(17)
    dates = [datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(365)) for _row in range(1500)]
    described = kpi_shapes.describe(tmp_path, name, "visit\n" + "".join(f"{written(day)}\n" for day in dates), 11)
    block = described.block("visit")
    assert block["format"] == "textual-day-first-date" and dict(block["month_name_styles"]) == {word: 1500}
    forms = {census: dict(block[census] or {}) for census in calendar_rules.FORM_CENSUSES}
    assert not calendar_rules.may_only_published(forms, block["format"])
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    assert calendar_rules.form_holes(forms, block["format"], days[0], days[-1]) == ()
    assert calendar_rules.entry_of(_groups(block)) == calendar_rules.ENTRY_SEVEN, _groups(block)
    assert _twins_meet(described) == []
    either = "title-either-space-no-comma"
    assert calendar_rules.may_only_published({"month_name_styles": {either: 40}}, block["format"])
    assert not calendar_rules.may_only_published({"month_name_styles": {either: 40, word: 900}}, block["format"])
    assert not calendar_rules.may_only_published({"month_name_styles": {either: 40}}, "iso-date")


def _one_autumn() -> "list[datetime.date]":
    """300 visits, 2024-10-12 to 12-20, weekday-shaped; eleven-day tails beside, one cell a day."""
    draw = random.Random(0)
    one = datetime.timedelta(days=1)
    days = [datetime.date(2024, 10, 1) + one * step for step in range(11)]
    days += [datetime.date(2024, 12, 21) + one * step for step in range(11)]
    span = [datetime.date(2024, 10, 12) + one * step for step in range(70)]
    days += [draw.choices(span, [_WEEKDAY[day.weekday()] for day in span])[0] for _row in range(278)]
    draw.shuffle(days)
    return days


def test_a_day_first_column_with_no_hole_between_its_boundaries_publishes(tmp_path: pathlib.Path) -> None:
    """A day-first column's form census reads its OTHER field as the month, and one autumn leaves no hole.

    `_one_autumn` written `d/m/yyyy` publishes `{first-field-unpadded}`:
    every cell's month is ten or more, and every day from October 12 to
    December 20 can be written so. Read as a month-first member the same
    word would leave the first to the ninth of November and December
    empty, days the column holds -- and the census would be withheld. No
    hole is read, the census publishes the seven counts, and the twins
    meet them at seeds 0 to 2 with nothing missed.
    """
    dates = _one_autumn()
    described = kpi_shapes.describe(
        tmp_path, "autumn", "visit\n" + "".join(f"{_day_first(day)}\n" for day in dates), 11
    )
    block = described.block("visit")
    assert block["format"] == "day-first-date" and list(block["date_field_widths"]) == ["first-field-unpadded"]
    assert calendar_rules.entry_of(_groups(block)) == calendar_rules.ENTRY_SEVEN, _groups(block)
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    forms = {census: dict(block[census] or {}) for census in calendar_rules.FORM_CENSUSES}
    assert calendar_rules.form_holes(forms, block["format"], days[0], days[-1]) == ()
    assert _twins_meet(described) == []


def test_a_declared_missing_day_holds_no_twin_date(tmp_path: pathlib.Path) -> None:
    """A day the table declares missing holds no body cell, and the twins meet the census beside it.

    Six rows in a hundred are written 2024-01-01 and that spelling is
    declared missing, so a cell written so is absent, never a body cell:
    the census publishes the seven counts, the day is a published hole
    (`calendar_rules.public_holes`), and the twins meet the census with
    nothing missed at three seeds -- the day pass never moves a rank onto
    the hole, which the validator would count against the census.
    """
    cells = _with_a_declared_day(0)
    table = fixtures.write(tmp_path, "declared.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=(_HOLE_DAY,))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
    written = fixtures.write_profile(tmp_path, "declared-profile.json", document)
    described = kpi_shapes.Described(tmp_path, table, document, contract.load_profile(str(written)))
    block = document["columns"][0]
    assert calendar_rules.entry_of(_groups(block)) == calendar_rules.ENTRY_SEVEN
    present = [cell for cell in cells if cell != _HOLE_DAY]
    days = _days_of(present)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    holes = calendar_rules.public_holes({}, block["format"], body[0], body[-1], (), taxonomy.published_absent(block, settings))
    assert holes == (_day_number(_HOLE_DAY),)
    assert _twins_meet(described) == []


def _declared_days_beside_every_other() -> "tuple[list[str], tuple[str, ...]]":
    """`decl4_240_5_2_r1`: 240 days from 2023-03-06, one or two cells on each but five declared missing, fifteen on each.

    The five days are drawn from the inner span (2023-04-09, 05-22,
    06-29, 08-02 and 08-22), written fifteen times each and declared
    missing; every other day holds one or two cells: 433 rows, 235
    different present days, 112 of them holding one row.
    """
    draw = random.Random(6446)
    span = [datetime.date(2023, 3, 6) + datetime.timedelta(days=step) for step in range(240)]
    declared = sorted(draw.sample(span[20:-20], 5))
    cells: "list[str]" = []
    for day in span:
        cells += [day.isoformat()] * (15 if day in declared else draw.randint(1, 2))
    draw.shuffle(cells)
    return cells, tuple(day.isoformat() for day in declared)


def _described_with_declared(folder: pathlib.Path, stem: str, text: str, declared: "tuple[str, ...]") -> kpi_shapes.Described:
    """``text`` described at floor 11 with ``declared`` as the declared missing values."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, f"{stem}.csv", text)
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=declared)
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))


def test_declared_days_beside_a_date_on_every_other_day_withhold_by_the_room_rule(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The room rule is asked beside declared holes: `decl4_240_5_2_r1` is withheld, `room` (second review of 3b.G, item 1).

    Every day of the span but the five declared missing holds a date,
    112 of them one row, so no group has a free day for a one-row date.
    The block publishes the five days as absent spellings, and they are
    the column's holes (`calendar_rules.public_holes`); none is a form
    hole, so the room rule is asked and withholds the census in the one
    shared sentence, and the real table validates with nothing missed.
    With the room rule withdrawn the seven counts publish and the twins
    of seeds 0, 1 and 4 hold 234 different days for 235, both distinct
    counts MISSED: 668f276 withheld this census and its twins met every
    check. A twin must pass its own checks, so the census stays withheld
    until the shared count steps can keep both it and the count of
    different days. Red when the room rule is asked beside May's holes
    alone again, as it was at ba37935.
    """
    cells, declared = _declared_days_beside_every_other()
    assert declared == ("2023-04-09", "2023-05-22", "2023-06-29", "2023-08-02", "2023-08-22")
    text = "seen_on\n" + "".join(f"{cell}\n" for cell in cells)
    described = _described_with_declared(tmp_path, "declared_room", text, declared)
    block = described.block("seen_on")
    assert sorted(block["missing_by_source"]) == list(declared)
    present = [cell for cell in cells if cell not in declared]
    assert len(present) == 433 - 75 and len(set(present)) == 235 == block["n_distinct"]
    days = _days_of(present)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    forms = {census: dict(block[census] or {}) for census in calendar_rules.FORM_CENSUSES}
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=declared)
    holes = calendar_rules.public_holes(
        forms, block["format"], body[0], body[-1], (), taxonomy.published_absent(block, settings)
    )
    assert holes == tuple(sorted(_day_number(day) for day in declared))
    assert calendar_rules.form_holes(forms, block["format"], body[0], body[-1]) == ()
    assert not calendar_rules.may_only_published(forms, block["format"])
    assert block["weekday_census"] == []
    decided = _decided(block, present, holes=declared)
    assert decided.reason == calendar_rules.REASON_ROOM, decided.reason
    said = [entry["note"] for entry in described.document["publication_notes"] if entry["column"] == "seen_on"]
    assert any("and why is not said" in sentence for sentence in said), said
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == []
    with monkeypatch.context() as roomy:
        roomy.setattr(calendar_rules, "room_short", lambda *_arguments: False)
        unruled = _described_with_declared(tmp_path / "unruled", "declared_room", text, declared)
        assert calendar_rules.entry_of(_groups(unruled.block("seen_on"))) == calendar_rules.ENTRY_SEVEN
        missed = kpi_shapes.missed(kpi_shapes.measure(unruled, kpi_shapes.twin_text(unruled, 0), "unruled-0.csv"))
    assert "seen_on:distinct.n_distinct" in missed, missed


# THE PLACEHOLDER HOLES (second review of landing 3b.1, finding 2): a
# placeholder day the block publishes as read as missing holds no cell.

_PLACEHOLDER = "1900-01-01"


def _with_a_placeholder_day() -> "list[str]":
    """Birth dates around a placeholder day: eleven in November 1899, a dense December and January, 800 in 2020 to 2022.

    December 1899 and January 1900 hold one to three cells a day, and
    twenty cells are written 1900-01-01: they stand far outside the
    dates' quartiles and are many, so the description reads that day as
    a placeholder meaning no value. The low tail is November's eleven,
    so the body runs from 1899-12-01 and holds the placeholder day.
    """
    draw = random.Random(1)
    one = datetime.timedelta(days=1)
    days = [datetime.date(1899, 11, 1) + one * step for step in range(11)]
    day = datetime.date(1899, 12, 1)
    while day <= datetime.date(1900, 1, 31):
        if day != datetime.date(1900, 1, 1):
            days += [day] * draw.choice([1, 2, 3])
        day += one
    days += draw.choices([datetime.date(2020, 1, 1) + one * step for step in range(365 * 3)], k=800)
    cells = [day.isoformat() for day in days] + [_PLACEHOLDER] * 20
    draw.shuffle(cells)
    return cells


def test_a_placeholder_day_read_as_missing_is_a_hole_no_twin_date_stands_on(tmp_path: pathlib.Path) -> None:
    """A placeholder day the block reads as no value is a hole, and the twins meet the census beside it.

    `sentinel_verdicts` publishes 1900-01-01 as `read_as_missing`, and
    the day lies between the two tail boundaries, so it is a hole
    (`calendar_rules.placeholder_holes`). The census publishes the seven
    counts, and the twins meet them at seeds 0 to 2 with nothing missed:
    a twin date on the day would miss the census whatever its counts.
    """
    cells = _with_a_placeholder_day()
    described = kpi_shapes.describe(tmp_path, "placeholder", "born\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("born")
    decisions = [(entry["candidate"], entry["verdict"]) for entry in block["sentinel_verdicts"]]
    assert decisions == [(_PLACEHOLDER, "read_as_missing")], decisions
    hole = _day_number(_PLACEHOLDER)
    assert calendar_rules.placeholder_holes((_PLACEHOLDER,), hole - 40, hole + 40) == (hole,)
    assert calendar_rules.entry_of(_groups(block)) == calendar_rules.ENTRY_SEVEN, _groups(block)
    assert _twins_meet(described) == []


_HEAVY_DAYS = {
    datetime.date(1899, 12, 5): 30,
    datetime.date(1899, 12, 13): 40,
    datetime.date(1899, 12, 21): 40,
    datetime.date(1899, 12, 29): 40,
    datetime.date(1900, 1, 7): 30,
}


def _around_a_placeholder_day() -> "list[str]":
    """Five weeks, Tuesday 1899-12-05 to Sunday 1900-01-07, with eleven-day tails, and twenty cells written 1900-01-01.

    Five heavy days -- the two boundaries and December 13, 21 and 29 --
    hold every rung, so the knot days fall on a Tuesday, a Wednesday, a
    Thursday, a Friday and a Sunday; the Mondays December 11, 18 and 25
    hold six cells each and every other day four to six. No cell but the
    twenty written as the placeholder falls on Monday 1900-01-01.
    """
    one = datetime.timedelta(days=1)
    first, last = datetime.date(1899, 12, 5), datetime.date(1900, 1, 7)
    days = [first - one * (1 + step) for step in range(11)] + [last + one * (1 + step) for step in range(11)]
    day = first
    while day <= last:
        if day in _HEAVY_DAYS:
            days += [day] * _HEAVY_DAYS[day]
        elif day != datetime.date(1900, 1, 1):
            days += [day] * (6 if day.weekday() == 0 else 4 + day.toordinal() % 3)
        day += one
    cells = [day.isoformat() for day in days] + [_PLACEHOLDER] * 20
    random.Random(3).shuffle(cells)
    return cells


def test_a_placeholder_day_the_block_keeps_is_no_hole(tmp_path: pathlib.Path) -> None:
    """A placeholder day the block keeps as a value is a day like any other.

    Described plainly, `_around_a_placeholder_day`'s twenty cells of
    1900-01-01 sit inside the dates' quartiles, so `sentinel_verdicts`
    keeps the day (`kept_as_a_number`): it holds twenty body cells, no
    hole is read off the block, and the census is decided on its dates
    alone -- five weeks, about five dates a weekday, so `few_dates` --
    never on a hole (`texts`) or on the room the holes leave (`room`).
    """
    cells = _around_a_placeholder_day()
    described = kpi_shapes.describe(tmp_path, "kept", "seen_on\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("seen_on")
    decisions = [(entry["candidate"], entry["verdict"]) for entry in block["sentinel_verdicts"]]
    assert decisions == [(_PLACEHOLDER, "kept_as_a_number")], decisions
    assert taxonomy._read_as_missing(block["sentinel_verdicts"]) == ()
    assert _decided(block, cells).reason == calendar_rules.REASON_FEW_DATES


def test_a_placeholder_day_between_the_boundaries_is_a_hole_the_loader_reads_only_for_its_shape(
    tmp_path: pathlib.Path,
) -> None:
    """A census around a placeholder hole is withheld for its few dates, and a copied one loads (plan P4-D365).

    Described with 1900-01-01 read as missing -- the hand-over by which
    the validator reads a checked file as its description did -- five
    weeks of about five dates a weekday are withheld, `few_dates`, said in
    the shared sentence. The seven counts the menu offers, copied onto
    the description, now LOAD: the loader holds a census to its shape
    alone, and WC7, which refused them, is retired.
    """
    cells = _around_a_placeholder_day()
    table = fixtures.write(tmp_path, "around.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=11),
        taxonomy.Settings(small_cell_floor=11),
        [],
        [],
        [],
        judged_candidates={"seen_on": (_PLACEHOLDER,)},
    )
    contract.load_profile(str(fixtures.write_profile(tmp_path, "around-profile.json", document)))
    block = document["columns"][0]
    decisions = [(entry["candidate"], entry["verdict"]) for entry in block["sentinel_verdicts"]]
    assert decisions == [(_PLACEHOLDER, "read_as_missing")], decisions
    assert block["weekday_census"] == []
    present = [cell for cell in cells if cell != _PLACEHOLDER]
    assert _decided(block, present).reason == calendar_rules.REASON_FEW_DATES
    said = [entry["note"] for entry in document["publication_notes"] if entry["column"] == "seen_on"]
    assert any("and why is not said" in sentence for sentence in said), said
    days = _days_of(present)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    offered, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), _LINE)
    doctored = dict(document)
    doctored["columns"] = [
        dict(block, weekday_census=[{"first": first, "last": last, "count": count} for first, last, count in offered])
    ]
    contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))


def _unpadded(cells: "list[str]") -> "list[str]":
    written: "list[str]" = []
    for cell in cells:
        day = datetime.date.fromisoformat(cell)
        written += [f"{day.month}/{day.day}/{day.year}"]
    return written


def test_a_date_written_two_ways_publishes_no_census_and_its_loader_refuses_one(
    tmp_path: pathlib.Path,
) -> None:
    """One spelling per day (WC6): a column writing its dates two widths publishes `[]`.

    The battery's admissions written month first: every other row padded
    and the rest not. The width census names two forms, so the column's
    count of different values is not a count of days: the census is
    withheld with its reason, and a census copied onto that description
    from the same admissions written one way is refused on load by name.
    """
    days = _battery_admissions(1000)["admission_date"]
    one_way = _unpadded(days)
    mixed = [
        (datetime.date.fromisoformat(cell).strftime("%m/%d/%Y") if place % 2 else one_way[place])
        for place, cell in enumerate(days)
    ]
    single = kpi_shapes.describe(tmp_path / "single", "single", "admission_date\n" + "".join(f"{c}\n" for c in one_way), 11)
    two = kpi_shapes.describe(tmp_path / "two", "two", "admission_date\n" + "".join(f"{c}\n" for c in mixed), 11)
    published = single.block("admission_date")["weekday_census"]
    assert published, "the admissions written one way publish their census"
    block = two.block("admission_date")
    assert block["weekday_census"] == [] and len(block["date_field_widths"]) == 2
    said = [entry["note"] for entry in two.document["publication_notes"]]
    assert any("more than one way here" in sentence for sentence in said), said
    doctored = dict(two.document)
    doctored["columns"] = [dict(block, weekday_census=published)]
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    assert contract.INVARIANTS["WC6"] in str(refusal.value)


def test_a_missed_weekday_group_below_the_line_prints_no_count(tmp_path: pathlib.Path) -> None:
    """A file holding one to ten of a published group is MISSED, and that number is never printed.

    The battery's admissions, and a file of them with every Sunday
    strictly between the two published boundaries moved to the Monday
    after it but three: the Sunday group holds one to ten cells. The
    census check is MISSED; its line reads `Sunday fewer than 11`, the
    note says why the number is kept back, and no number below the line
    appears on the line, in the note or anywhere in the quality report
    beside the census (plan P4-D347).
    """
    cells = _battery_admissions(1000)["admission_date"]
    described = kpi_shapes.describe(tmp_path, "admissions", "admission_date\n" + "".join(f"{c}\n" for c in cells), 11)
    block = described.block("admission_date")
    low = datetime.date.fromisoformat(block["low_tail"]["boundary"])
    high = datetime.date.fromisoformat(block["high_tail"]["boundary"])
    kept = 0
    moved: "list[str]" = []
    for cell in cells:
        day = datetime.date.fromisoformat(cell)
        if low < day < high and day.weekday() == 6:
            if kept < 3:
                kept += 1
            else:
                day += datetime.timedelta(days=1)
        moved += [day.isoformat()]
    held = sum(1 for cell in moved if low <= datetime.date.fromisoformat(cell) <= high
               and datetime.date.fromisoformat(cell).weekday() == 6)
    assert 0 < held < _LINE, held
    outcome = kpi_shapes.measure(described, "admission_date\n" + "".join(f"{c}\n" for c in moved), "moved.csv")
    [check] = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
    assert check.verdict == validation.MISSED
    assert "Sunday fewer than 11" in check.achieved, check.achieved
    assert any("fewer than 11" in line for line in check.note), check.note
    for text in (check.achieved, " ".join(check.note)):
        numbers = [int(word) for word in text.replace(",", " ").split() if word.isdigit()]
        assert all(number >= _LINE for number in numbers), (text, numbers)
    printed = quality.quality_report(described.loaded, outcome)
    census = [line for line in printed.splitlines() if "Monday" in line and "Sunday" in line]
    counts = [int(found) for line in census for found in re.findall(r"day (\d+)\b", line)]
    assert any("Sunday fewer than 11" in line for line in census), census
    assert counts and min(counts) >= _LINE, counts


def test_a_column_with_unparsed_cells_publishes_and_its_twins_meet_it(tmp_path: pathlib.Path) -> None:
    """Unparsed cells take nothing from the census: one row a business day and ten impossible dates publish.

    One row a business day over four and a half years, five days
    repeated, and ten cells written as three impossible dates. The
    certificate's reader once took every unparsed cell off its fewest
    days and withheld the census, `narrowed`; with the certificate retired
    (plan P4-D365) the census the menu offers is published -- Monday to
    Friday one by one, the weekend nought -- and the twins meet it at
    seeds 0 to 2 with nothing missed.
    """
    draw = random.Random(100)
    day = datetime.date(2020, 1, 6)
    days: "list[datetime.date]" = []
    while len(days) < 1180:
        if day.weekday() < 5:
            days += [day]
        day += datetime.timedelta(days=1)
    wrong = ("2021-02-30", "2021-02-31", "2021-04-31")
    cells = [each.isoformat() for each in days] + [each.isoformat() for each in draw.sample(days[20:-20], 5)]
    cells += [wrong[place % 3] for place in range(10)]
    draw.shuffle(cells)
    described = kpi_shapes.describe(tmp_path, "log", "log_date\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block("log_date")
    assert block["n_unparsed"] == 10 and block["n_distinct"] == 1180 + 3
    groups = _groups(block)
    assert groups[-1] == (5, 6, 0) and calendar_rules.entry_of(groups) == calendar_rules.ENTRY_SEVEN, groups
    assert _twins_meet(described) == []


def test_a_day_written_with_a_trailing_blank_is_two_spellings(tmp_path: pathlib.Path) -> None:
    """Two texts for one day that no census of written forms shows still withhold the census.

    The battery's admissions, published with the seven counts, and the
    same column with every fortieth cell written with a blank after it
    (quoted, so it is kept): no census of written forms counts a
    trailing blank, so WC6's published half passes, but the count of
    different values exceeds the real days (WC6 (b)): `[]`, reason
    `texts`, said in the one sentence every rule the table's own numbers
    decide shares (plan P4-D359).
    """
    cells = _battery_admissions(1000)["admission_date"]
    blanked = [f'"{cell} "' if place % 40 == 0 else cell for place, cell in enumerate(cells)]
    plain = kpi_shapes.describe(tmp_path / "plain", "plain", "admission_date\n" + "".join(f"{c}\n" for c in cells), 11)
    assert plain.block("admission_date")["weekday_census"]
    described = kpi_shapes.describe(tmp_path / "blank", "blank", "admission_date\n" + "".join(f"{c}\n" for c in blanked), 11)
    block = described.block("admission_date")
    days = tuple(_days_of(cells))
    assert block["n_distinct"] > len(set(days))
    assert calendar_rules.one_spelling_published(
        {name: block[name] or {} for name in calendar_rules.FORM_CENSUSES}, block["format"], len(days)
    )
    decided = taxonomy.weekday_decision(
        block, days, block["n_distinct"], taxonomy.Settings(small_cell_floor=11), texts=len(set(blanked)),
    )
    assert decided.reason == calendar_rules.REASON_TEXTS, decided.reason
    assert block["weekday_census"] == []
    said = [entry["note"] for entry in described.document["publication_notes"]]
    assert any("and why is not said" in sentence for sentence in said), said


def _date_book(cells: "list[str]", text_every: int) -> bytes:
    """A workbook of one date column: date cells, and every `text_every`-th cell ISO text."""
    body = [(1, [workbooks.cell("A1", "seen_on", "inlineStr")])]
    for place, text in enumerate(cells):
        number = place + 2
        day = datetime.date.fromisoformat(text)
        if text_every and place % text_every == 0:
            one = workbooks.cell(f"A{number}", text, "inlineStr")
        else:
            one = workbooks.cell(f"A{number}", str((day - datetime.date(1899, 12, 30)).days), "", 1)
        body += [(number, [one])]
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:A{len(cells) + 1}")),
        ]
    )


def test_a_workbook_storing_dates_two_ways_publishes_no_census(tmp_path: pathlib.Path) -> None:
    """One storage class per workbook column: dates stored as dates and as text publish `[]`.

    The same weekday-shaped dates stored as date cells publish a census;
    with every sixth cell stored as ISO text instead, the column is read
    back differently cell by cell, so the census is withheld and says why.
    """
    draw = random.Random(3100)
    cells: "list[str]" = []
    for step in range(730):
        day = datetime.date(2022, 1, 3) + datetime.timedelta(days=step)
        times = draw.choice((0, 1, 2, 3)) if day.weekday() < 5 else draw.choice((0, 0, 0, 1))
        cells += [day.isoformat()] * times
    draw.shuffle(cells)
    found = {}
    for name, every in (("dates", 0), ("mixed", 6)):
        path = tmp_path / f"{name}.xlsx"
        path.write_bytes(_date_book(cells, every))
        document = profile.build_document(
            reading.read_table(str(path), small_cell_floor=11), taxonomy.Settings(small_cell_floor=11), [], [], []
        )
        found[name] = document
    assert found["dates"]["columns"][0]["weekday_census"], "date cells alone publish a census"
    assert found["mixed"]["columns"][0]["weekday_census"] == []
    said = [entry["note"] for entry in found["mixed"]["publication_notes"]]
    assert any("and why is not said" in sentence for sentence in said), said


def test_validating_a_file_never_produces_a_census(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The validator counts the file's body against the PUBLISHED groups and asks no producer.

    Its two re-descriptions of the file skip the census producer, so a
    validate run of a twin whose description publishes three censuses
    completes with the producer made to fail on entry, and still holds
    every census.
    """
    columns = _battery_schedules(1000)
    described = kpi_shapes.describe(tmp_path, "schedules", _table_text(columns), 11)
    written = kpi_shapes.twin_text(described, 0)

    def refused(*_arguments: object, **_named: object) -> None:
        raise AssertionError("a validate run produced a weekday census")

    monkeypatch.setattr(taxonomy, "weekday_decision", refused)
    outcome = kpi_shapes.measure(described, written, "twin.csv")
    held = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
    assert len(held) == 3 and all(check.verdict == validation.HELD for check in held)


# THE FOLD (plan P4-D250) COUNTED ON BOTH SIDES (plan P4-D365): a column
# read jointly whose one ISO moment the date pass counts into the dates.

_FOLDED = {
    "tuesday_clinic_20w": lambda draw: [
        (datetime.date(2024, 1, 2) + datetime.timedelta(days=7 * draw.randrange(20))).isoformat() for _ in range(395)
    ],
    "admissions_90d": lambda draw: [
        (datetime.date(2023, 1, 2) + datetime.timedelta(days=draw.randrange(90))).isoformat() for _ in range(395)
    ],
    "every_day_395": lambda _draw: [
        (datetime.date(2020, 1, 1) + datetime.timedelta(days=step)).isoformat() for step in range(395)
    ],
}


@pytest.mark.parametrize("name", sorted(_FOLDED))
def test_a_folded_moment_is_counted_where_the_census_counted_it(tmp_path: pathlib.Path, name: str) -> None:
    """The validator reads a folded ISO moment on its day, as the census counted it (plan P4-D365).

    395 ISO dates, one moment at midnight among them and four unreadable
    words (the shape of
    tests/test_extra_round_disclosure.py's joint reading): the date pass
    counts the moment into the dates (plan P4-D250), so the column is
    published wholly as `iso-date` and its census counts the moment on its
    day. The validator read the file's cells under `iso-date` alone and
    left the moment out, so the source itself missed its own census by
    one row; it now reads such a cell under the joint reading
    (`validation._day_as_counted`) wherever the file's own description
    folded it -- here `n_unparsed` 4 for five present cells the member
    fails (`validation._folded_by_the_file`). The real file validates
    with nothing missed, and the twins of seeds 0 and 1 too.
    """
    cells = _FOLDED[name](random.Random(5))
    moment = "2020-05-03T00:00:00" if name == "every_day_395" else sorted(cells)[len(cells) // 2] + "T00:00:00"
    cells = cells + [moment] + ["unparsed"] * 4
    text = "value\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, name, text, 11)
    block = described.block("value")
    assert block["format"] == "iso-date" and block["resolution_mix"] == {"iso-date": 396}, block["resolution_mix"]
    assert block["weekday_census"], name
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == [], name
    assert _twins_meet(described, (0, 1)) == []


# THE FOLD READ ONLY WHERE THE FILE'S OWN DESCRIPTION FOLDED (review of
# landing 3b.G, item 2): 600 ISO dates with a few moments mixed in, the
# review's probe shapes. Read under one ISO form from the start, the
# column leaves the moments UNPARSED (`n_unparsed` counts them) and its
# census never counted them; ten moments are read jointly and folded.

_UNPARSED = {
    "T_midnight_1": (["2024-03-05T00:00:00"], 1),
    "T_clock_1": (["2024-03-05T14:30:00"], 1),
    "space_clock_1": (["2024-03-05 14:30:00"], 1),
    "T_clock_5": (["2024-03-%02dT14:30:00" % date for date in (5, 6, 7, 8, 9)], 5),
    "T_clock_10": (["2024-03-%02dT14:30:00" % date for date in range(5, 15)], 0),
    "Z_1": (["2024-03-05T14:30:00Z"], 1),
    "offset_1": (["2024-03-05T14:30:00+02:00"], 1),
    "offset_late_1": (["2024-03-05T23:30:00-05:00"], 1),
    "minutes_1": (["2024-03-05T14:30"], 1),
    "T_clock_1_NA3": (["2024-03-05T14:30:00", "NA", "NA", "NA"], 1),
    "T_midnight_1_words4": (["2024-03-05T00:00:00"] + ["unparsed"] * 4, 5),
    "T_clock_1_blank30": (["2024-03-05T14:30:00"] + ['""'] * 30, 1),
}


def _probe_dates() -> "list[str]":
    """600 ISO dates drawn from 200 days from 2024-01-01 (the review's probe base)."""
    draw = random.Random(5)
    span = [datetime.date(2024, 1, 1) + datetime.timedelta(days=step) for step in range(200)]
    return [draw.choice(span).isoformat() for _row in range(600)]


@pytest.mark.parametrize("name", sorted(_UNPARSED))
def test_a_moment_the_description_left_unparsed_is_not_counted(tmp_path: pathlib.Path, name: str) -> None:
    """The source validates clean whether its moments were folded or left unparsed (review of 3b.G, item 2).

    Each shape places its cells over the probe's 600 ISO dates, 17 rows
    apart from row 37. One to five moments, written with a `T`, a space,
    minutes alone, a `Z` or an offset, beside `NA` cells, unreadable
    words or thirty blank cells, are left unparsed: the column is published as `iso-date`, its
    `n_unparsed` counts them, and its census never counted them. Ten
    moments are read jointly and folded: `n_unparsed` 0. On fb257b0 the
    validator read every cell the member fails under the joint reading,
    so the source missed its own census on ten of these shapes; it now
    does so only where the file's own description folded them
    (`validation._folded_by_the_file`). The source validates with nothing
    missed, and the twin of seed 0 too. Red when the fold read is asked
    of every column of an ISO member, or counts a blank cell as one the
    description may have parsed.
    """
    extra, unparsed = _UNPARSED[name]
    cells = _probe_dates()
    for place, cell in enumerate(extra):
        cells[37 + 17 * place] = cell
    text = "seen\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, name, text, 11)
    block = described.block("seen")
    assert (block["format"], block["n_unparsed"]) == ("iso-date", unparsed), (block["format"], block["n_unparsed"])
    assert block["weekday_census"], name
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == [], name
    assert _twins_meet(described, (0,)) == []


def test_a_month_first_column_with_an_unparsed_iso_date_validates_clean(tmp_path: pathlib.Path) -> None:
    """A month-first column's one ISO date is unparsed, and no fold read counts it (review of 3b.G, item 2).

    The probe's 600 dates written `m/d/yyyy`, one of them left in ISO:
    the member is `month-first-date`, `n_unparsed` 1, and the census
    published over the rest. The fold read belongs to the two ISO forms
    alone, so the ISO cell is counted nowhere and the source validates
    with nothing missed.
    """
    cells = []
    for cell in _probe_dates():
        day = datetime.date.fromisoformat(cell)
        cells += [f"{day.month}/{day.day}/{day.year}"]
    cells[37] = "2024-03-05"
    text = "seen\n" + "".join(f"{cell}\n" for cell in cells)
    described = kpi_shapes.describe(tmp_path, "month_first", text, 11)
    block = described.block("seen")
    assert (block["format"], block["n_unparsed"]) == ("month-first-date", 1), (block["format"], block["n_unparsed"])
    assert block["weekday_census"]
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "real.csv")) == []

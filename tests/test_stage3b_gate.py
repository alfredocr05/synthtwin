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

LANDING 3b.1 (plan P4-D355) makes the second clause true on DATE
columns: the weekday census, published only where the full-fill
certificate holds (`calendar_certificate`). Its clauses are the second
half of this file, and each of its rules has the mutation record
below, every mutation run on a copy of this tree with the rule
withdrawn and nothing else changed:

* the certificate withdrawn (every census the menu offers published)
  turns red the verifier on all three battery shapes, the brute force,
  five of the seven seeded witnesses and the declared missing day;
* compaction withdrawn, the brute force and `w_month_wide_1000_s0`;
* the real count of different days withdrawn (the reader's bounds on
  both sides), the verifier on the three shapes, `sessions20_s0`,
  `w_month_wide_1000_s0` and the declared missing day;
* the residue check withdrawn, the brute force (unsound censuses);
* the entry's inference withdrawn from the witness (no short weekday
  kept), the brute force and `gr_wedthu_6_8_s1`;
* menu entry 2 withdrawn, `sessions20_s0`; entry 3, `gr_wedthu_6_8_s1`;
* WC7 withdrawn, `B2_oneweek_1201_s0` and `k7_sessions_s0`;
* one spelling per day withdrawn, the column written two widths; the
  holes withdrawn, the declared missing day; the one-storage rule
  withdrawn, the workbook stored two ways; the validator's
  re-descriptions producing the census, the validate run;
* the day pass withdrawn, the battery's twins and the seven frozen
  `weekday_*` cases of tests/test_generation_reference.py;
* the loader's check withdrawn, the eight WC mutations of
  tests/test_contract_loader.py and the copied census the loader
  refuses;
* the ties fast path withdrawn changes what two withheld censuses SAY
  (`walkcase4_s0` and `bizlog_x1_s1` fall to the residue's sentence
  rather than the repeats', still withheld), and the residue's rank cap
  withdrawn changes nothing here, as the design measured.

THE REVIEW OF LANDING 3b.1 found the certificate's premise -- every
published fact unchanged by exchanging two days of one class -- false
where a census of written forms names a form only some days are written
in, and three rules with no witness. Its witnesses, each with the
mutation that turns it red:

* the FORM HOLES (`calendar_rules.form_holes`): 104 visits past the ninth
  written `m/d/yyyy` and 149 dates of three Mays, whose census a reader
  holding the holes pins on every open day, are withheld -- red when the
  holes are withdrawn from the producer (the census publishes), from its
  certificate alone (its self-check still withholds, but the verdict
  holds), from the loader or from `breach` (the copied census loads),
  and from the verifier (it finds no witness on a hole); and each half
  of the rule -- the OTHER field of a one-field width word, the month of
  May -- turns its own column red when it is read wrong;
* a heavy column past the ninth PUBLISHES, a stretch of holes between
  two of its knot days: red when the verifier keeps holes in its
  classes, and when the producer's certificate is asked blind to them
  (its witnesses stand on holes);
* WC7 counts no hole: red when `few_dates_group`, its caller or `breach`
  counts them;
* a MISSED weekday line prints no count below the line: red when the
  line prints the group's count (plan P4-D347);
* the reader's fewest days take every unparsed cell away: red when they
  take one text (the census then falls to `ties` from `narrowed`);
* a day written with a trailing blank no census shows is two spellings:
  red when WC6 (b) is withdrawn (the census then PUBLISHES, its count of
  different values a count of texts and not of days).
"""

from __future__ import annotations

import datetime
import math
import pathlib
import random
import re

import pytest

import calendar_certificate_brute as brute_force
import calendar_certificate_verify as verifier
import fixtures
import kpi_shapes
import workbooks
from synthtwin import (
    calendar_certificate,
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


# ======================================================================
# LANDING 3b.1 (plan P4-D355): THE WEEKDAY CENSUS OF A COLUMN OF DATES.
#
# "Weekend share and weekday come back; no calendar count below the
# floor." A column of whole dates publishes which days of the week its
# body falls on, in groups the floor alone chooses from a fixed menu, and
# only where the full-fill certificate holds (calendar_certificate). The
# clauses below are the landing's: the battery keeps every census and its
# twins meet them with nothing missed and the weekday statistics inside
# their scoped bounds; the certificate is checked by two checkers that
# import nothing of the calendar code -- the verifier, witness by witness
# and day by day, and the brute force over every table of tiny bodies;
# each rule has a seeded witness publishing what the rule derives; and a
# validate run never enters the certificate.
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
    return sorted(verifier.day_number(cell) for cell in cells if cell)


def _certified(block: dict, cells: "list[str]", floor: int = 11, holes: "tuple[str, ...]" = ()) -> "calendar_certificate.Verdict":
    """The certificate the producer asked for this block, asked again."""
    decided = taxonomy.weekday_decision(
        block,
        tuple(_days_of(cells)),
        block["n_distinct"],
        taxonomy.Settings(small_cell_floor=floor, declared_missing_values=holes),
    )
    assert decided.verdict is not None
    return decided.verdict


def _verified(block: dict, cells: "list[str]", holes: "tuple[str, ...]" = ()) -> "list[str]":
    """What the independent verifier says of a published census, and nothing else."""
    verdict = _certified(block, cells, holes=holes)
    days = _days_of([cell for cell in cells if cell not in holes])
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    witnesses = [(witness.klass, witness.day, witness.table) for witness in verdict.witnesses]
    return verifier.census_problems(
        block,
        _LINE,
        witnesses,
        real_days=len(set(body)),
        holes=tuple(verifier.day_number(hole) for hole in holes),
    )


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
    """Every date column of the battery publishes its census, and the verifier passes it.

    At 1,000 rows and a floor of eleven each of the six columns -- two
    years of admissions, billing dates heaped on the 1st and 15th, birth
    dates over seventy years, a weekly Monday clinic, a 28-day cycle and a
    monthly visit -- publishes the seven weekday counts, the clinic's
    empty Friday to Sunday as one group of nought. The 28-day cycle and
    the monthly visit certify with RESIDUE, stretches the rank facts hold
    below the line beside a boundary. Every witness is re-checked day by
    day by the verifier, which imports nothing of the calendar code, and
    every class it cannot see covered it re-derives as capped.
    """
    columns = _BATTERY[shape](1000)
    described = kpi_shapes.describe(tmp_path, shape, _table_text(columns), 11)
    for name, cells in columns.items():
        block = described.block(name)
        groups = [(group["first"], group["last"], group["count"]) for group in block["weekday_census"]]
        assert calendar_rules.entry_of(tuple(groups)) == calendar_rules.ENTRY_SEVEN, (name, groups)
        assert _verified(block, cells) == [], name
        if name in ("cycle_28", "monthly_visit"):
            assert _certified(block, cells).residue, f"{name} certifies with no residue"


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


def brute_force_battery(trials: int = 400, larger: int = 200) -> "dict[str, int]":
    """The certificate against the brute force: every published census judged.

    `trials` tiny bodies at seed 0 and `larger` larger ones at seed 1, the
    census the menu offers each, asked of `calendar_certificate.certify`
    at the brute force's line of three with the count of different days
    exact. WC7, which is the heavy-date ruling's and not the floor's, is
    not asked: a body of seven days is all few dates.
    """
    totals = {
        "censuses": 0, "published": 0, "unsound": 0, "not_a_table": 0,
        "unfillable": 0, "vertices": 0, "full": 0,
    }
    for seed, count, larger_bodies in ((0, trials, False), (1, larger, True)):
        draw = random.Random(seed)
        for _trial in range(count):
            instance = brute_force.instance(draw, larger_bodies)
            if instance is None:
                continue
            totals["censuses"] += 1
            facts = calendar_certificate.facts_of(
                instance["body"], 0, 0, instance["low"], instance["high"],
                tuple(instance["rungs"]), instance["different"], instance["different"],
                brute_force.LINE, tuple(instance["groups"]), -1, (),
            )
            verdict = calendar_certificate.certify(facts)
            judged = brute_force.judge(
                instance, verdict.holds, [(witness.day, witness.table) for witness in verdict.witnesses]
            )
            if not verdict.holds:
                continue
            totals["published"] += 1
            if verdict.mode:
                totals[verdict.mode] += 1
            for key in ("unsound", "not_a_table", "unfillable"):
                totals[key] += judged[key]
    return totals


def test_the_certificate_survives_the_brute_force() -> None:
    """No published census confines any set of days below the line.

    Over 400 tiny bodies and 200 larger ones: every census the
    certificate publishes has no census-caused pin, every witness is a
    table of the facts, and every certified class has a table filling
    its day. Both of the residue's paths publish -- the vertex slices and
    the full enumeration -- so neither is exercised vacuously.
    """
    totals = brute_force_battery()
    assert totals["unsound"] == 0 and totals["not_a_table"] == 0 and totals["unfillable"] == 0, totals
    assert totals["published"] > 0 and totals["vertices"] > 0 and totals["full"] > 0, totals


# THE EXPECTED PUBLICATIONS: a seeded witness per rule, each asserting
# what that rule derives (plan P4-D355).


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
    "walkcase4_s0": ("seen_on", lambda: _walk_case(0), [], calendar_rules.REASON_TIES),
    "gr_wedthu_6_8_s1": ("visit_date", lambda: _thin_midweek(1), [(0, 4, 453), (5, 6, 0)], ""),
    "sessions20_s0": (
        "session_date", lambda: _twenty_sessions(0),
        [(0, 0, 352), (1, 1, 201), (2, 2, 261), (3, 3, 114), (4, 4, 143), (5, 6, 16)], "",
    ),
    "k7_sessions_s0": ("session_date", lambda: _seven_sessions(0), [], calendar_rules.REASON_FEW_DATES),
    "B2_oneweek_1201_s0": ("visit_date", lambda: _one_week(1201, 0), [], calendar_rules.REASON_FEW_DATES),
    "bizlog_x1_s1": ("log_date", lambda: _business_days(1, 1), [], calendar_rules.REASON_TIES),
    "w_month_wide_1000_s0": ("visit_date", lambda: _one_month_wide(1000, 0), [], calendar_rules.REASON_NARROWED),
}


@pytest.mark.parametrize("name", sorted(_EXPECTED))
def test_each_rule_publishes_what_it_derives(tmp_path: pathlib.Path, name: str) -> None:
    """The seeded witnesses of the rules, each publishing what its rule derives.

    * `walkcase4_s0`: 1,001 different dates, so no date can hold eleven
      rows (the reader's repeated cells are none): withheld, `ties`.
    * `gr_wedthu_6_8_s1`: Wednesday on six days and Thursday on eight,
      so neither the seven counts nor the weekend grouping holds the line
      in every group: entry 3, `[Mon-Fri] [Sat-Sun]`, certified with a
      weekday kept short in every witness.
    * `sessions20_s0`: every weekday alone reaches the line, the weekend
      together does too: entry 2.
    * `k7_sessions_s0` and `B2_oneweek_1201_s0`: each group would be the
      count of a few single dates (WC7): withheld, `few_dates`.
    * `bizlog_x1_s1`: one row a business day and one more, so no day can
      hold eleven: withheld, `ties`.
    * `w_month_wide_1000_s0`: certified only on a count of different
      days that is not the real one, so the census keeps a day below the
      line where stage 3 does not: withheld, `narrowed`.

    Every published census here passes the verifier; every withheld one
    says why in the one sentence its reason carries.
    """
    column, build, expected, reason = _EXPECTED[name]
    cells = build()
    described = kpi_shapes.describe(tmp_path, name, f"{column}\n" + "".join(f"{cell}\n" for cell in cells), 11)
    block = described.block(column)
    groups = [(group["first"], group["last"], group["count"]) for group in block["weekday_census"]]
    assert groups == expected, (name, groups)
    decided = taxonomy.weekday_decision(
        block, tuple(_days_of(cells)), block["n_distinct"], taxonomy.Settings(small_cell_floor=11)
    )
    assert decided.reason == reason, (name, decided.reason)
    if expected:
        assert _verified(block, cells) == [], name
        return
    said = [entry["note"] for entry in described.document["publication_notes"] if entry["column"] == column]
    assert any("are not counted" in sentence for sentence in said), said


def test_a_declared_missing_day_is_a_hole_no_witness_stands_on(tmp_path: pathlib.Path) -> None:
    """A day the table declares missing holds no body cell in any table, and no witness uses it.

    Six rows in a hundred are written 2024-01-01 and that spelling is
    declared missing, so a cell written so is absent, never a body cell:
    the census publishes the seven counts, every witness keeps the day
    empty (the verifier asked with the hole), and the twins meet the census
    with nothing missed at three seeds -- the day pass never moves a rank
    onto the hole.
    """
    cells = _with_a_declared_day(0)
    table = fixtures.write(tmp_path, "declared.csv", "seen_on\n" + "".join(f"{cell}\n" for cell in cells))
    settings = taxonomy.Settings(small_cell_floor=11, declared_missing_values=(_HOLE_DAY,))
    document = profile.build_document(reading.read_table(str(table), small_cell_floor=11), settings, [], [], [])
    written = fixtures.write_profile(tmp_path, "declared-profile.json", document)
    described = kpi_shapes.Described(tmp_path, table, document, contract.load_profile(str(written)))
    block = document["columns"][0]
    assert calendar_rules.entry_of(
        tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    ) == calendar_rules.ENTRY_SEVEN
    present = [cell for cell in cells if cell != _HOLE_DAY]
    verdict = _certified(block, present, holes=(_HOLE_DAY,))
    hole = verifier.day_number(_HOLE_DAY)
    assert all(dict(witness.table).get(hole, 0) == 0 for witness in verdict.witnesses)
    assert _verified(block, present, holes=(_HOLE_DAY,)) == []
    for seed in (0, 1, 2):
        text = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"twin-{seed}.csv")) == [], seed


# THE FORM HOLES (review of landing 3b.1, finding 1): days the censuses of
# written forms tell a reader no cell holds.


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


# name -> (the days, how each is written, which days a reader holds empty)
_FORM_HOLES = {
    "past_the_ninth": (_past_the_ninth, lambda day: f"{day.month}/{day.day}/{day.year}", lambda day: day.day < 10),
    "mays_only": (_mays_only, lambda day: f"{day.day} May {day.year}", lambda day: day.month != 5),
}


@pytest.mark.parametrize("name", sorted(_FORM_HOLES))
def test_a_day_the_form_censuses_leave_empty_is_a_hole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str
) -> None:
    """A census that would pin every day a reader holds, once the form censuses' holes are known, is withheld.

    `past_the_ninth` publishes `date_field_widths {first-field-unpadded}`
    and `mays_only` `month_name_styles {title-either-space-no-comma}`: a
    reader holds the first to the ninth of every month, and every day
    outside May, empty. THE READER HERE knows those holes (the
    verifier's own `form_holes`, restated from each table's rule) and
    nothing of the calendar code: its least count of different days
    equals the days left between the boundaries, so each of them holds
    a cell in every table, and under the census the menu offers each
    day's weekday count less one cell for every other day of its group
    leaves EVERY day below the line. So:

    * the certificate itself refuses (its verdict does not hold) and the
      column publishes `[]` with the narrowed sentence;
    * asked blind to the form holes, the certificate would have
      published that census, and the verifier finds its witnesses
      standing on holes;
    * that census copied onto the description is refused on load (WC8),
      because the loader reads the holes off the same censuses.
    """
    build, written, empty = _FORM_HOLES[name]
    dates = build()
    described = kpi_shapes.describe(
        tmp_path, name, "visit\n" + "".join(f"{written(day)}\n" for day in dates), 11
    )
    block = described.block("visit")
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    low, high = body[0], body[-1]
    epoch = datetime.date(1970, 1, 1)
    holes = verifier.form_holes(block)
    assert holes == {day for day in range(low, high + 1) if empty(epoch + datetime.timedelta(days=day))}
    assert holes and not holes & set(body)
    allowed = [day for day in range(low, high + 1) if day not in holes]
    fewest = verifier.reader_facts(dict(block, weekday_census=[]), _LINE)["fewest"]
    assert len(allowed) == fewest, "every day a reader leaves open holds a cell in every table"
    offered, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), _LINE)
    pinned = 0
    for first, last, count in offered:
        members = [day for day in allowed if first <= verifier.weekday(day) <= last]
        if count and count - (len(members) - 1) < _LINE:
            pinned += len(members)
    assert pinned == len(allowed), (pinned, len(allowed))

    assert block["weekday_census"] == []
    decided = taxonomy.weekday_decision(
        block, tuple(days), block["n_distinct"], taxonomy.Settings(small_cell_floor=11)
    )
    assert decided.verdict is not None and not decided.verdict.holds
    assert decided.reason == calendar_rules.REASON_NARROWED
    said = [entry["note"] for entry in described.document["publication_notes"]]
    assert any("could be narrowed to fewer than 11 rows" in sentence for sentence in said), said

    with monkeypatch.context() as blind:
        blind.setattr(calendar_rules, "form_holes", lambda *_arguments: ())
        calendar_certificate._ANSWERS.clear()
        unaware = taxonomy.weekday_decision(
            block, tuple(days), block["n_distinct"], taxonomy.Settings(small_cell_floor=11)
        )
    calendar_certificate._ANSWERS.clear()
    assert unaware.groups == offered and unaware.verdict is not None
    census = [{"first": first, "last": last, "count": count} for first, last, count in offered]
    problems = verifier.census_problems(
        dict(block, weekday_census=census),
        _LINE,
        [(witness.klass, witness.day, witness.table) for witness in unaware.verdict.witnesses],
        real_days=len(set(body)),
    )
    assert any("on a hole" in problem for problem in problems), problems

    doctored = dict(described.document)
    doctored["columns"] = [dict(block, weekday_census=census)]
    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(str(fixtures.write_profile(tmp_path, "doctored-profile.json", doctored)))
    assert contract.INVARIANTS["WC8"] in str(refusal.value)


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


def test_a_column_with_form_holes_publishes_where_every_open_day_can_hold_the_line(tmp_path: pathlib.Path) -> None:
    """Holes withhold nothing a table can fill: a heavy column past the ninth publishes the seven counts.

    `_straddling_february`'s width census leaves the first to the ninth
    of every month empty, and two of its knot days enclose February's
    nine: a stretch of holes only, whose weekdays form no class. The
    census publishes the seven counts, and the verifier -- deriving the
    same holes itself, leaving them out of its classes and standing no
    witness cell on one -- passes every witness day by day.
    """
    dates = _straddling_february()
    text = "seen_on\n" + "".join(f"{day.month}/{day.day}/{day.year}\n" for day in dates)
    described = kpi_shapes.describe(tmp_path, "straddle", text, 11)
    block = described.block("seen_on")
    groups = tuple((group["first"], group["last"], group["count"]) for group in block["weekday_census"])
    assert calendar_rules.entry_of(groups) == calendar_rules.ENTRY_SEVEN, groups
    holes = verifier.form_holes(block)
    knots = verifier.reader_facts(block, _LINE)["knots"]
    assert any(
        after - before > 1 and all(day in holes for day in range(before + 1, after))
        for before, after in zip(knots, knots[1:])
    ), knots
    days = sorted((day - datetime.date(1970, 1, 1)).days for day in dates)
    body = days[block["low_tail"]["rows"]: len(days) - block["high_tail"]["rows"]]
    verdict = taxonomy.weekday_decision(
        block, tuple(days), block["n_distinct"], taxonomy.Settings(small_cell_floor=11)
    ).verdict
    assert verdict is not None and verdict.holds
    assert verifier.census_problems(
        block, _LINE, [(witness.klass, witness.day, witness.table) for witness in verdict.witnesses],
        real_days=len(set(body)),
    ) == []


def test_a_group_left_few_dates_by_its_holes_is_withheld() -> None:
    """WC7 counts a group's calendar days less its holes.

    Five weeks, Monday to Sunday, with only the two boundaries as knot
    days and every weekday counting twenty: each group has four or five
    calendar days besides its knot days. Two of the five Saturdays
    holes, the Saturday group can hold three dates at most, a few single
    dates, and WC7 withholds; the same question with no holes passes
    WC7 and reaches the certificate.
    """
    low = verifier.day_number("2024-01-01")
    high = low + 34
    groups = tuple((weekday, weekday, 20) for weekday in range(7))
    asked = (160, 10, 10, low, high, (), 25, 35, _LINE, groups, -1)
    calendar_certificate._ANSWERS.clear()
    assert calendar_certificate.check(*asked).reason != calendar_rules.REASON_FEW_DATES
    holed = calendar_certificate.check(*asked, (low + 5, low + 12))
    assert holed.reason == calendar_rules.REASON_FEW_DATES
    assert calendar_certificate.breach(
        groups, 160, 10, 10, low, high, (), 25, 35, _LINE, True, (low + 5, low + 12)
    )[0] == "WC7"


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


def test_the_reader_leaves_every_unparsed_cell_out_of_its_fewest_days(tmp_path: pathlib.Path) -> None:
    """The reader's least count of different days takes EVERY unparsed cell away, not one text.

    One row a business day over four and a half years, five days
    repeated, and ten cells written as three impossible dates. The
    count of different values holds the three texts, and a reader
    cannot tell three texts from ten, so its fewest days take all ten
    unparsed cells away and its most takes one: the bounds equal the
    verifier's own and those numbers. The body's own count of
    different days leaves five repeated cells, so no census witness can
    put eleven on a day, while a stage-3 table on the reader's bounds
    can: withheld, `narrowed`. Taking one text away instead would leave
    the reader no room for eleven either, and the census would fall to
    the repeats' sentence (`ties`).
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
    low_tail, high_tail = block["low_tail"], block["high_tail"]
    bounds = calendar_certificate.reader_days(
        block["n_distinct"], block["n_unparsed"],
        low_tail["rows"], len(low_tail["values"]) if low_tail["values"] else -1,
        high_tail["rows"], len(high_tail["values"]) if high_tail["values"] else -1,
    )
    facts = verifier.reader_facts(dict(block, weekday_census=[]), _LINE)
    assert bounds == (facts["fewest"], facts["most_days"])
    assert bounds == (1183 - 10 - low_tail["rows"] - high_tail["rows"], 1183 - 1 - 2)
    good = sorted(verifier.day_number(cell) for cell in cells if cell not in wrong)
    decided = taxonomy.weekday_decision(block, tuple(good), block["n_distinct"], taxonomy.Settings(small_cell_floor=11))
    assert decided.reason == calendar_rules.REASON_NARROWED, decided.reason
    assert block["weekday_census"] == []


def test_a_day_written_with_a_trailing_blank_is_two_spellings(tmp_path: pathlib.Path) -> None:
    """Two texts for one day that no census of written forms shows still withhold the census.

    The battery's admissions, published with the seven counts, and the
    same column with every fortieth cell written with a blank after it
    (quoted, so it is kept): no census of written forms counts a
    trailing blank, so WC6's published half passes, but the count of
    different values exceeds the real days (WC6 (b)): `[]`, reason
    `spellings`, and the sentence says so.
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
    decided = taxonomy.weekday_decision(block, days, block["n_distinct"], taxonomy.Settings(small_cell_floor=11))
    assert decided.reason == calendar_rules.REASON_SPELLINGS, decided.reason
    assert block["weekday_census"] == []
    said = [entry["note"] for entry in described.document["publication_notes"]]
    assert any("more than one way here" in sentence for sentence in said), said


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
    assert any("stores this column's dates in more than one way" in sentence for sentence in said), said


def test_validating_a_file_never_enters_the_certificate(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The validator counts the file's body against the PUBLISHED groups and asks no certificate.

    Its two re-descriptions of the file skip the census producer, so a
    validate run of a twin whose description publishes three censuses --
    one of them certified with residue -- completes with the certificate
    made to fail on entry, and still holds every census.
    """
    columns = _battery_schedules(1000)
    described = kpi_shapes.describe(tmp_path, "schedules", _table_text(columns), 11)
    written = kpi_shapes.twin_text(described, 0)

    def refused(*_arguments: object, **_named: object) -> None:
        raise AssertionError("a validate run entered the calendar certificate")

    monkeypatch.setattr(calendar_certificate, "check", refused)
    monkeypatch.setattr(calendar_certificate, "certify", refused)
    outcome = kpi_shapes.measure(described, written, "twin.csv")
    held = [check for check in outcome.checks if check.fact == "datetime.weekday_census"]
    assert len(held) == 3 and all(check.verdict == validation.HELD for check in held)

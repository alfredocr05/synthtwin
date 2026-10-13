"""THE DATES THAT STAND OUT (stage 3b landing 3b.6, plan P4-D369).

A column the twin counts in days -- whole dates, or moments every value
of which stands at midnight on the local clock, not in the joint member,
with both tails (`calendar_rules.heavy_scope`, the 3b.6 skeptic's M1) --
publishes `heavy_dates`: every date between the two tail boundaries
holding at least the heavy line (`calendar_rules.heavy_line`: eleven, or
the census line where it is higher) and at least three times the mean of
the three days either side, counting every parsed cell, tail cells
included, each with its exact count (contract HD1 to HD5). The twin
holds every listed date at its count (method G7.3j): the listed rows are
pinned, every other rank of the body is drawn in a PART between the
unlisted knots and the covered runs, the split repaired by a flow to the
censuses' groups and to the count's new days, and drawn by key, as many
new days as the count leaves. The validator counts the file's parsed
cells on each listed date (V5-D1).

THE GATE'S CLAUSES, each beside what turns it red:

* H1, every listed count held and nothing else missed:
  `test_the_battery_twins_hold_every_listed_date` -- the gate's battery
  (heaps, schedules, admissions) at 1,000 and 10,000 rows, seeds 0 and
  4: V5-D1 HELD on every listed column and nothing MISSED on the source
  or the twin; mutant: the pins seam withdrawn (`_heavy_layout` hands
  the layout back), so the body is drawn over the listed dates.
* H2, the heaps come back: `test_the_heaps_come_back` -- the 28-day
  cycle's days, the 10th, the 1st and the 15th, 1 January and the
  heaviest date, each within its measured bound; mutant: no list
  published.
* H3, the line: `test_no_listed_count_below_the_heavy_line` at floors 1,
  11 and 36, and `test_a_missed_line_prints_fewer_than_the_line`.
* H4, nothing on an ordinary column: `test_the_battery_lists_what_stands_out`
  -- admissions lists nothing at 1,000 or 10,000 rows, and the heaps and
  schedules list what the design measured.
* the scope (M1): `test_a_clocked_column_lists_nothing` and
  `test_midnight_moments_list_and_hold`.
* the rule: `test_the_rule_on_hand_counts`, and HD4 against a brute
  enumeration of tiny bodies, `test_the_runs_are_the_brute_force_s`.
* the nineteenth vectors file: `test_every_case_is_asked` and
  `test_the_product_gives_each_case_its_answer_and_its_mutant_another`,
  each state red on its own source edit (the covered run, the loose
  dates, the boundary anchor, the holes of a key, the census repair, the
  count's repair, the second census).
* the oracle on whole columns: `test_whole_columns_are_the_oracle_s`.
* the producer always loads: `test_every_description_the_producer_writes_loads`.
* the report: `test_the_report_says_the_listed_dates_are_met` and
  `test_a_listed_date_the_twin_misses_is_named_and_said`.
* the joint fix with lane D3 (plan P4-D368's limits, lifted): quarter
  ends and one month a year at 10,000 rows meet every check (tests of
  `tests/test_stage3b_day_of_month.py`), and the business-day visit on
  the 10th at eight seeds, `test_the_tenth_on_business_days_meets_every_check_at_eight_seeds`.
* the work is bounded: `test_the_plan_and_the_draw_count_no_more_as_rows_grow`,
  machine-free, up to 1,000,000 rows.
* NF71 is dropped beside a list: `test_the_weekday_floor_remark_stands_only_without_a_list`.

Test-local mutants build the product's module with one source edit (one
`compile` and one `exec` below); the oracle is run by path (one
`runpy.run_path`).
"""

from __future__ import annotations

import copy
import itertools
import json
import pathlib
import random
import runpy
import sys
import types

import pytest

import kpi_shapes
import test_stage3b_day_of_month as dom
import test_stage3b_gate as gate
from synthtwin import (
    calendar_rules,
    generation,
    parsing,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-19.json"
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"
SOURCE = pathlib.Path(generation.__file__).read_text(encoding="utf-8")
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))
SEEDS = (0, 4)


def _oracle() -> "dict[str, object]":
    return runpy.run_path(str(ORACLE))


def _day(cell: str) -> int:
    return parsing.days_from_civil(int(cell[0:4]), int(cell[5:7]), int(cell[8:10]))


def _listed(block: dict) -> "list[tuple[int, int]]":
    return [(_day(entry["date"]), entry["count"]) for entry in block["heavy_dates"]]


def _counts(cells: "list[str]") -> "dict[int, int]":
    found: "dict[int, int]" = {}
    for cell in cells:
        if cell:
            found[_day(cell)] = found.get(_day(cell), 0) + 1
    return found


def _column(text: str, name: str) -> "list[str]":
    lines = text.splitlines()
    at = lines[0].split(",").index(name)
    return [line.split(",")[at] for line in lines[1:] if line]


class _Run:
    """One table of the battery, described, with each seed's twin and what it misses."""

    def __init__(self, folder: pathlib.Path, label: str, columns: "dict[str, list[str]]", floor: int) -> None:
        self.columns = columns
        self.described = kpi_shapes.describe(folder, label, gate._table_text(columns), floor)
        self.source = kpi_shapes.missed(
            kpi_shapes.measure(self.described, self.described.table.read_text(encoding="utf-8"), "source.csv")
        )
        self.twins: "dict[int, str]" = {}
        self.missed: "dict[int, list[str]]" = {}
        self.checks: "dict[int, list[validation.Check]]" = {}
        for seed in SEEDS:
            text = kpi_shapes.twin_text(self.described, seed)
            outcome = kpi_shapes.measure(self.described, text, f"twin-{seed}.csv")
            self.twins[seed] = text
            self.missed[seed] = kpi_shapes.missed(outcome)
            self.checks[seed] = list(outcome.checks)


@pytest.fixture(scope="module")
def battery(tmp_path_factory: pytest.TempPathFactory) -> "dict[int, dict[str, _Run]]":
    """The gate's battery at 1,000 and 10,000 rows, a floor of eleven."""
    found: "dict[int, dict[str, _Run]]" = {}
    for rows in (1000, 10000):
        found[rows] = {}
        for shape in ("heaps", "schedules", "admissions"):
            folder = tmp_path_factory.mktemp(f"heavy-{shape}-{rows}")
            found[rows][shape] = _Run(folder, shape, gate._BATTERY[shape](rows), 11)
    return found


# -- H4 and what the battery lists ------------------------------------------------------

# What the design measured on the gate's battery (3b.6 design, section 1): listed dates and
# the rows on them, per column; re-derived on the base of this landing.
_LISTED = {
    1000: {
        "billing_date": (17, 211), "birth_date": (0, 0), "weekly_clinic": (25, 295),
        "cycle_28": (25, 831), "monthly_visit": (22, 836), "admission_date": (0, 0),
    },
    10000: {
        "billing_date": (47, 4397), "birth_date": (30, 555), "weekly_clinic": (103, 8853),
        "cycle_28": (27, 9060), "monthly_visit": (24, 8955), "admission_date": (0, 0),
    },
}


def test_the_battery_lists_what_stands_out(battery: "dict[int, dict[str, _Run]]") -> None:
    """H4 and the producer: admissions lists nothing at 1,000 or 10,000 rows, and the heaps
    and schedules list the dates the design measured. Red where the producer is withdrawn."""
    for rows, expected in _LISTED.items():
        for run in battery[rows].values():
            for name in run.columns:
                listed = _listed(run.described.block(name))
                assert (len(listed), sum(count for _day, count in listed)) == expected[name], (rows, name)


def test_the_rule_on_hand_counts() -> None:
    """THE RULE: a date stands out at the line and at three times the mean of its six
    neighbours, compared as twice its count against their sum; a neighbour outside the column
    holds nought, a tail cell beside the boundary counts, and a hole is never listed."""
    day = 1000
    counts = {day - 3: 2, day - 2: 2, day - 1: 2, day: 11, day + 1: 4, day + 2: 4, day + 3: 8}
    # 2 * 11 = 22 = 2+2+2+4+4+8: equality stands.
    assert calendar_rules.heavy_listed(counts, day, day, 11, frozenset()) == ((day, 11),)
    counts[day + 3] = 9
    assert calendar_rules.heavy_listed(counts, day, day, 11, frozenset()) == ()
    counts[day + 3] = 8
    assert calendar_rules.heavy_listed(counts, day, day, 12, frozenset()) == ()
    assert calendar_rules.heavy_listed(counts, day, day, 11, frozenset({day})) == ()
    # A boundary date: the tail cells beside it are counted among its neighbours.
    edge = {day: 20, day - 1: 41}
    assert calendar_rules.heavy_listed(edge, day, day + 5, 11, frozenset()) == ()
    assert calendar_rules.heavy_listed({day: 20}, day, day + 5, 11, frozenset()) == ((day, 20),)
    assert calendar_rules.heavy_line(1) == 11
    assert calendar_rules.heavy_line(11) == 11
    assert calendar_rules.heavy_line(36) == 36


def _brute_starts(
    knots: "list[tuple[int, int]]", listed: "list[tuple[int, int]]", holes: "set[int]"
) -> "list[set[int]] | None":
    """Every start rank each listed date's run takes over every ascending assignment of days to
    the body's ranks that keeps the knots, the listed counts and the holes; None where none."""
    low_rank, low_day = knots[0]
    high_rank, high_day = knots[-1]
    count_of = dict(listed)
    knot_at = dict(knots)
    ranks = list(range(low_rank, high_rank + 1))
    days = [d for d in range(low_day, high_day + 1) if d not in holes or d in count_of]
    starts: "list[set[int]]" = [set() for _ in listed]
    found = False
    for choice in itertools.combinations_with_replacement(days, len(ranks)):
        if any(knot_at.get(rank, choice[index]) != choice[index] for index, rank in enumerate(ranks)):
            continue
        held = {d: choice.count(d) for d in set(choice)}
        if any(held.get(d, 0) != c for d, c in listed):
            continue
        found = True
        for index, (d, _c) in enumerate(listed):
            starts[index].add(ranks[choice.index(d)])
    return starts if found else None


def test_the_runs_are_the_brute_force_s() -> None:
    """HD4 (`calendar_rules.heavy_runs`) against a brute enumeration of tiny bodies: no rank
    order exactly where none is found, and each run's start bounds exactly the starts found.
    Red where the forced start after a hole is withdrawn."""
    draw = random.Random(369)
    asked = 0
    for _case in range(160):
        ranks = draw.randint(4, 7)
        low_day = 100
        high_day = low_day + draw.randint(2, 5)
        middle = sorted(draw.sample(range(1, ranks - 1), draw.randint(0, min(2, ranks - 2))))
        knot_days = sorted(draw.randint(low_day, high_day) for _ in middle)
        knots = [(0, low_day)] + list(zip(middle, knot_days)) + [(ranks - 1, high_day)]
        pool = list(range(low_day, high_day + 1))
        listed = sorted((d, draw.randint(1, 3)) for d in draw.sample(pool, draw.randint(1, 2)))
        holes = {d for d in pool if draw.random() < 0.2 and d not in dict(listed) and d not in knot_days + [low_day, high_day]}
        brute = _brute_starts(knots, listed, holes)
        runs = calendar_rules.heavy_runs(tuple(knots), tuple(listed), frozenset(holes))
        if brute is None:
            assert runs is None, (knots, listed, holes)
            continue
        asked += 1
        assert runs is not None, (knots, listed, holes)
        for index, (first, last) in enumerate(runs):
            assert (first, last) == (min(brute[index]), max(brute[index])), (knots, listed, holes, runs, brute)
    assert asked >= 40


def test_a_clocked_column_lists_nothing(tmp_path: pathlib.Path) -> None:
    """THE SCOPE (the 3b.6 skeptic's M1): the billing days written with a clock list nothing (a
    stated limit of plan P4-D369), and the validator's own re-description asks nothing."""
    cells = [cell + " 09:30:00" for cell in gate._BATTERY["heaps"](1000)["billing_date"]]
    described = kpi_shapes.describe(tmp_path, "clocked", gate._table_text({"billed_at": cells}), 11)
    assert described.block("billed_at")["heavy_dates"] == []
    block, notes, remarks = taxonomy._heavy_published(
        dict(described.block("billed_at")),
        None,  # type: ignore[arg-type]
        None,  # type: ignore[arg-type]
        taxonomy.Settings(),
        False,
        False,
        [],
        {},
    )
    assert block["heavy_dates"] == [] and notes == [] and remarks == []


def test_midnight_moments_list_and_hold(tmp_path: pathlib.Path) -> None:
    """THE SCOPE (M1): the billing days written as moments at midnight list the dates the whole
    dates list, and every twin holds them and misses nothing."""
    days = gate._BATTERY["heaps"](1000)["billing_date"]
    plain = kpi_shapes.describe(tmp_path / "plain", "plain", gate._table_text({"billed": days}), 11)
    moments = kpi_shapes.describe(
        tmp_path / "moments", "moments", gate._table_text({"billed": [cell + " 00:00:00" for cell in days]}), 11
    )
    assert _listed(moments.block("billed")) == _listed(plain.block("billed")) != []
    for seed in SEEDS:
        text = kpi_shapes.twin_text(moments, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(moments, text, f"t{seed}.csv")) == [], seed


@pytest.mark.parametrize("floor", (1, 11, 36))
def test_no_listed_count_below_the_heavy_line(tmp_path: pathlib.Path, floor: int) -> None:
    """H3: every listed count is at least `max(11, line)` at floors 1, 11 and 36 (plan section 8:
    at a floor of one the census line is two, and the list keeps to eleven)."""
    line = calendar_rules.heavy_line(floor)
    for shape in ("heaps", "schedules"):
        described = kpi_shapes.describe(tmp_path / shape, shape, gate._table_text(gate._BATTERY[shape](1000)), floor)
        for block in described.document["columns"]:
            for entry in block.get("heavy_dates") or []:
                assert entry["count"] >= line >= 11, (shape, floor, entry)


# -- H1 and H2 on the battery ------------------------------------------------------------


def test_the_battery_twins_hold_every_listed_date(battery: "dict[int, dict[str, _Run]]", monkeypatch: pytest.MonkeyPatch) -> None:
    """H1: on the source and on every twin nothing is MISSED, and V5-D1 is HELD on every
    listed column. Red where the pins seam is withdrawn: the body is drawn over the listed
    dates, gap by gap."""
    for rows, runs in battery.items():
        for shape, run in runs.items():
            assert run.source == [], (rows, shape)
            for seed in SEEDS:
                assert run.missed[seed] == [], (rows, shape, seed, run.missed[seed])
                for name in run.columns:
                    if not run.described.block(name)["heavy_dates"]:
                        continue
                    held = [c for c in run.checks[seed] if c.column == name and c.subcheck == "heavy_dates.counts"]
                    assert len(held) == 1 and held[0].verdict == validation.HELD, (rows, name, seed)
    monkeypatch.setattr(generation, "_heavy_layout", lambda column, facts, layout: layout)
    run = battery[1000]["heaps"]
    text = kpi_shapes.twin_text(run.described, 0)
    assert "billing_date:heavy_dates.counts" in kpi_shapes.missed(kpi_shapes.measure(run.described, text, "mutant.csv"))


def _share(cells: "list[str]", keep: "object") -> float:
    found = [cell for cell in cells if cell]
    return sum(1 for cell in found if keep(cell)) / len(found)  # type: ignore[operator]


_CYCLE_DAYS = {day.isoformat() for day in gate._CYCLE}


def _heap_bounds(rows: int) -> "list[tuple[str, str, object, float]]":
    """(table, column, the cells kept, the bound on |twin - real|) per heap of H2."""
    found: "list[tuple[str, str, object, float]]" = [
        ("schedules", "cycle_28", lambda cell: cell in _CYCLE_DAYS, 0.005),
        ("schedules", "monthly_visit", lambda cell: cell[8:10] == "10", 0.015 if rows == 1000 else 0.001),
    ]
    if rows == 10000:
        found += [("heaps", "billing_date", lambda cell: cell[8:10] in ("01", "15"), 0.001)]
    return found


def test_the_heaps_come_back(battery: "dict[int, dict[str, _Run]]", tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """H2: the cycle's days, the 10th and (at 10,000 rows) the 1st and the 15th come back within
    their bounds; 1 January's births hold at least the listed rows at 10,000 rows; the heaviest
    date is the real one wherever it is listed. Red where no list is published."""
    for rows, runs in battery.items():
        for table, name, keep, bound in _heap_bounds(rows):
            run = runs[table]
            real = _share(run.columns[name], keep)
            for seed in SEEDS:
                twin = _share(_column(run.twins[seed], name), keep)
                assert abs(twin - real) <= bound, (rows, name, seed, real, twin)
        for run in runs.values():
            for name in run.columns:
                listed = dict(_listed(run.described.block(name)))
                real = _counts(run.columns[name])
                top = max(real, key=lambda day: (real[day], -day))
                if top not in listed:
                    continue
                for seed in SEEDS:
                    twin = _counts(_column(run.twins[seed], name))
                    assert max(twin.values()) == real[top] == twin[top], (rows, name, seed)
    births = battery[10000]["heaps"]
    listed = _listed(births.described.block("birth_date"))
    floor_share = sum(count for _day, count in listed) / len(births.columns["birth_date"])
    for seed in SEEDS:
        assert _share(_column(births.twins[seed], "birth_date"), lambda cell: cell[5:10] == "01-01") >= floor_share
    monkeypatch.setattr(taxonomy, "heavy_dates_decided", lambda *args: ())
    columns = gate._BATTERY["schedules"](1000)
    described = kpi_shapes.describe(tmp_path, "none", gate._table_text(columns), 11)
    twin = _column(kpi_shapes.twin_text(described, 0), "cycle_28")
    assert abs(_share(twin, lambda cell: cell in _CYCLE_DAYS) - _share(columns["cycle_28"], lambda cell: cell in _CYCLE_DAYS)) > 0.005


def test_a_missed_line_prints_fewer_than_the_line(battery: "dict[int, dict[str, _Run]]") -> None:
    """V5-D1 on a file holding three rows on a listed date: MISSED, and the line prints no count
    below the heavy line (P4-D347)."""
    run = battery[1000]["schedules"]
    listed = _listed(run.described.block("monthly_visit"))
    day, count = listed[0]
    year, month, date = parsing.civil_from_days(day)
    text = f"{year:04d}-{month:02d}-{date:02d}"
    cells = list(run.columns["monthly_visit"])
    moved = 0
    for place, cell in enumerate(cells):
        if cell == text and moved < count - 3:
            cells[place] = parsing_next(cell)
            moved += 1
    columns = dict(run.columns, monthly_visit=cells)
    outcome = kpi_shapes.measure(run.described, gate._table_text(columns), "short.csv")
    checks = [c for c in outcome.checks if c.column == "monthly_visit" and c.subcheck == "heavy_dates.counts"]
    assert len(checks) == 1 and checks[0].verdict == validation.MISSED
    line = calendar_rules.heavy_line(11)
    shown = checks[0].achieved
    assert " 3" not in shown.replace(text, ""), shown
    assert f"fewer than {line}" in shown or any(f"fewer than {line}" in note for note in checks[0].note), (shown, checks[0].note)


def parsing_next(cell: str) -> str:
    """The ISO date one day after `cell`."""
    year, month, date = parsing.civil_from_days(_day(cell) + 1)
    return f"{year:04d}-{month:02d}-{date:02d}"


# -- the report --------------------------------------------------------------------------


def test_the_report_says_the_listed_dates_are_met(battery: "dict[int, dict[str, _Run]]") -> None:
    """The column's sentence on its spread says each listed date holds its count, and no longer
    names the heaps among what is not reproduced; a column listing nothing still names them."""
    run = battery[1000]["schedules"]
    twin = generation.generate(run.described.loaded, 0)
    said = [r for r in twin.remarks if r.column == "cycle_28" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_HEAVY_MET in said[0].held, said
    assert generation._SPREAD_HEAVY_OWN in said[0].note and generation._SPREAD_HEAVY_THING[0] not in said[0].note, said
    plain = battery[1000]["admissions"]
    twin = generation.generate(plain.described.loaded, 0)
    said = [r for r in twin.remarks if r.column == "admission_date" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_HEAVY_MET not in said[0].held, said
    assert generation._SPREAD_HEAVY_THING[0] in said[0].note, said


def test_a_listed_date_the_twin_misses_is_named_and_said(battery: "dict[int, dict[str, _Run]]", monkeypatch: pytest.MonkeyPatch) -> None:
    """With the pins seam withdrawn the twin's listed counts are off: the post-pass names
    `heavy_dates` among its deviations, and the sentence says the listed dates are not met.
    Red where either is withdrawn."""
    monkeypatch.setattr(generation, "_heavy_layout", lambda column, facts, layout: layout)
    run = battery[1000]["heaps"]
    twin = generation.generate(run.described.loaded, 0)
    notes = [d.note for d in twin.deviations if d.column == "billing_date" and d.fact == "heavy_dates"]
    assert notes == [generation._HEAVY_MISSED]
    said = [r.note for r in twin.remarks if r.column == "billing_date" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_HEAVY_MISSED in said[0], said


def test_the_weekday_floor_remark_stands_only_without_a_list(battery: "dict[int, dict[str, _Run]]") -> None:
    """NF71 ("never of one date") is not said beside a list -- a weekday group less its listed
    dates can be read off -- and is said beside a weekday census with no list. NF105 is said
    beside every list and nowhere else."""
    floor_remark = taxonomy.rendered(taxonomy.REMARK_WEEKDAY_FLOOR, (calendar_rules.census_line(11),))
    listed_remark = taxonomy.rendered(taxonomy.REMARK_HEAVY_DATES, (calendar_rules.heavy_line(11),))
    asked = {True: 0, False: 0}
    for run in battery[1000].values():
        for name in run.columns:
            block = run.described.block(name)
            if not block["weekday_census"]:
                continue
            has_list = bool(block["heavy_dates"])
            asked[has_list] += 1
            assert (floor_remark in block["remarks"]) is not has_list, name
            assert (listed_remark in block["remarks"]) is has_list, name
    assert asked[True] and asked[False]


# -- the nineteenth vectors file ---------------------------------------------------------

CASES = (
    "heavy_adjacent_dates",
    "heavy_boundary_day",
    "heavy_count_reach_repair",
    "heavy_covered_run",
    "heavy_loose_dates",
    "heavy_two_censuses",
    "heavy_two_weekdays_repair",
)

# Each case's own source edit of the product, and what it withdraws.
MUTANTS = {
    # a knot on a listed date covered by its run
    "heavy_covered_run": (
        "        covered = [day for day in inside if day in knot_days]\n",
        '        covered: "list[int]" = []\n',
    ),
    # a loose date's run standing at the start of its part
    "heavy_loose_dates": (
        "                    for day in inside\n                    if lo <= day <= hi and day not in knot_days\n",
        "                    for day in inside\n                    if lo <= day <= hi and day not in knot_days and False\n",
    ),
    # the anchor before a listed low boundary day
    "heavy_boundary_day": (
        "        anchors += [(low_rank - 1, low_day - 1, False)]\n",
        "        anchors += [(low_rank - 1, low_day, False)]\n",
    ),
    # a hole is no key's free day
    "heavy_adjacent_dates": (
        "            for day in range(segment.lows[part], segment.highs[part] + 1):\n"
        "                if day in listed_days or day in holes:\n"
        "                    continue\n"
        "                key = tuple(",
        "            for day in range(segment.lows[part], segment.highs[part] + 1):\n"
        "                if day in listed_days:\n"
        "                    continue\n"
        "                key = tuple(",
    ),
    # the repair of the split (the 3b.6 skeptic's B1)
    "heavy_two_weekdays_repair": (
        "    current = _heavy_score(segments, rooms, splits, budget)\n    for _round in range(_HEAVY_REPAIRS):\n",
        "    current = _heavy_score(segments, rooms, splits, budget)\n    for _round in range(0):\n",
    ),
    # the count's new days in the repair's score
    "heavy_count_reach_repair": (
        "    return deficit, max(0, budget - _heavy_reach_of(segments, rooms, splits))\n",
        "    return deficit, 0\n",
    ),
    # the second census beside the list
    "heavy_two_censuses": (
        "    if len(demands) == 1:\n        for place in range(len(days_of)):\n",
        "    if len(demands) >= 1:\n        for place in range(len(days_of)):\n",
    ),
}


def _mutant(monkeypatch: pytest.MonkeyPatch, before: str, after: str) -> types.ModuleType:
    """The product's generation module with ONE source edit, built beside it (an edit that no
    longer applies turns the test red)."""
    assert SOURCE.count(before) == 1, before
    name = "synthtwin._generation_heavy_dates_mutant"
    module = types.ModuleType(name)
    module.__file__ = generation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(compile(SOURCE.replace(before, after), generation.__file__, "exec"), module.__dict__)
    return module


def _answer(case: dict, module: types.ModuleType = generation) -> "dict[str, object] | None":
    """What the product makes of a case: `_heavy_plan` and `_heavy_values`."""
    listed = tuple(tuple(pair) for pair in case["listed"])
    planned = module._heavy_plan(
        tuple(tuple(knot) for knot in case["knots"]),
        listed,
        frozenset(case["holes"]),
        (tuple(tuple(g) for g in case["weekdays"]), tuple(tuple(g) for g in case["month"])),
        case["budget"],
    )
    if planned is None:
        return None
    placed, parts, owed = planned
    days = {day for day, _count in listed}
    knots = frozenset(day for _rank, day in case["knots"] if day not in days)
    try:
        values = module._heavy_values(parts, owed, knots, case["left"], case["words"])
    except IndexError:
        return None
    runs: "list[list[int]]" = []
    for rank in sorted(placed):
        low, high = placed[rank]
        if low != high or low not in days:
            continue
        if runs and runs[-1][1] == low and runs[-1][0] + runs[-1][2] == rank:
            runs[-1][2] += 1
        else:
            runs += [[rank, low, 1]]
    return {"runs": runs, "parts": [[p.lo, p.hi, p.first, p.count] for p in parts], "values": values}


def test_every_case_is_asked() -> None:
    """The file holds these cases and no other, each with its own mutant, and the oracle, run
    again, gives each the answer the file carries."""
    assert tuple(sorted(_FILE["cases"])) == CASES
    assert tuple(sorted(MUTANTS)) == CASES
    oracle = _oracle()
    assert sorted(oracle["HEAVY_STEP_CASES"]) == list(CASES)  # type: ignore[call-overload]
    for name, case in _FILE["cases"].items():
        assert oracle["heavy_answer"](case) == case["answer"], name  # type: ignore[operator]


@pytest.mark.parametrize("name", CASES)
def test_the_product_gives_each_case_its_answer_and_its_mutant_another(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """Each state: the product's answer is the file's, every listed run covers its knots, every
    ordinary value keeps off the listed dates and the holes, and under its own source edit the
    answer moves."""
    case = _FILE["cases"][name]
    answer = _answer(case)
    assert answer == case["answer"], name
    listed = dict(tuple(pair) for pair in case["listed"])
    for first, day, count in answer["runs"]:  # type: ignore[index]
        assert listed[day] == count, name
        for rank, knot in case["knots"]:
            if knot == day:
                assert first <= rank < first + count, name
    for values in answer["values"]:  # type: ignore[index]
        for value in values:
            assert value not in listed and value not in case["holes"], name
    before, after = MUTANTS[name]
    assert _answer(case, _mutant(monkeypatch, before, after)) != case["answer"], name


# -- the oracle on whole columns ---------------------------------------------------------

_WHOLE = {
    "billing": ("billing_date", lambda: gate._BATTERY["heaps"](1000)["billing_date"]),
    "monthly": ("monthly_visit", lambda: gate._BATTERY["schedules"](1000)["monthly_visit"]),
    "clinic": ("weekly_clinic", lambda: gate._BATTERY["schedules"](1000)["weekly_clinic"]),
    "sessions": ("sessions", lambda: dom._skeptic(1000)["sessions"]),
    "mays": ("visit", lambda: dom._mays(range(2019, 2025), 1000, 1600, 0.4)),
}


@pytest.mark.parametrize("label", sorted(_WHOLE))
def test_whole_columns_are_the_oracle_s(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, label: str) -> None:
    """A-P4-59: the cells the generator writes for a column listing dates that stand out, through
    the oracle's own content (method G7.3j and every pass beside it), from the same words."""
    name, build = _WHOLE[label]
    described = kpi_shapes.describe(tmp_path, label, gate._table_text({name: build()}), 11)
    assert described.block(name)["heavy_dates"] != []
    seen: "list[tuple[list[int], list[str]]]" = []
    content = generation._datetime_content

    def captured(plan, words):  # type: ignore[no-untyped-def]
        found = content(plan, words)
        seen[:] = [(list(words), list(found[0]))]
        return found

    monkeypatch.setattr(generation, "_datetime_content", captured)
    kpi_shapes.twin_text(described, 0)
    words, ours = seen[0]
    block = copy.deepcopy(described.block(name))
    theirs = _oracle()["_datetime_content"](dict(block, _content_words=words))  # type: ignore[operator]
    assert theirs == ours, label


# -- the producer always loads -----------------------------------------------------------


def test_every_description_the_producer_writes_loads(tmp_path: pathlib.Path) -> None:
    """THE PRODUCER-ALWAYS-LOADS BATTERY: every table below, at floors 1, 11 and 36, is
    described by the shipped producer and loaded by the shipped loader (HD1 to HD5 asked of
    every list it writes), and its twin at seed 0 holds every listed date."""
    tables: "dict[str, dict[str, list[str]]]" = {}
    for shape in ("heaps", "schedules", "admissions"):
        tables[shape] = gate._BATTERY[shape](1000)
    for name, cells in dom._skeptic(1000).items():
        tables[f"skeptic_{name}"] = {name: cells}
    for name, cells in dom._monthend(1000).items():
        tables[f"monthend_{name}"] = {name: cells}
    tables["mays"] = {"visit": dom._mays(range(2019, 2025), 1000, 1600, 0.4)}
    days = gate._BATTERY["heaps"](1000)["billing_date"]
    tables["slashed"] = {"billed": [f"{c[5:7]}/{c[8:10]}/{c[0:4]}" for c in days]}
    tables["midnight"] = {"billed": [c + "T00:00:00" for c in days]}
    listed = 0
    for floor in (1, 11, 36):
        for label, columns in tables.items():
            described = kpi_shapes.describe(tmp_path / f"{label}-{floor}", label, gate._table_text(columns), floor)
            for name in columns:
                block = described.block(name)
                if not block.get("heavy_dates"):
                    continue
                listed += 1
                if floor != 11:
                    continue
                text = kpi_shapes.twin_text(described, 0)
                outcome = kpi_shapes.measure(described, text, f"{label}.csv")
                held = [c for c in outcome.checks if c.column == name and c.subcheck == "heavy_dates.counts"]
                assert len(held) == 1 and held[0].verdict == validation.HELD, (label, name)
    assert listed >= 30


# -- the joint fix with lane D3 ----------------------------------------------------------


def test_the_tenth_on_business_days_meets_every_check_at_eight_seeds(tmp_path: pathlib.Path) -> None:
    """The 3b.6 skeptic's M2: the business-day visit on the 10th at 1,000 rows, beside both
    censuses, missed the weekday census at seeds 0, 5 and 7 under both prototypes together.
    Every twin at seeds 0 to 7 now meets every check."""
    columns = {"visit": dom._monthend(1000)["visit_10th_business"]}
    described = kpi_shapes.describe(tmp_path, "tenth", gate._table_text(columns), 11)
    block = described.block("visit")
    assert block["heavy_dates"] and block["day_of_month_census"] and block["weekday_census"]
    for seed in range(8):
        text = kpi_shapes.twin_text(described, seed)
        assert kpi_shapes.missed(kpi_shapes.measure(described, text, f"t{seed}.csv")) == [], seed


# -- the work is bounded -----------------------------------------------------------------


def _scaled_state(rows: int) -> "dict[str, object]":
    """A column of `rows` ranks over two years: knots at the ladder's ranks, every Monday
    listed with a tenth of the rows between them, a weekday census of seven groups."""
    first = parsing.days_from_civil(2024, 1, 2)
    last = first + 728
    knots = [(0, first)]
    for percent in (10, 25, 50, 75, 90):
        knots += [(((rows - 1) * percent) // 100, first + (728 * percent) // 100 + 1)]
    knots += [(rows - 1, last)]
    mondays = [day for day in range(first + 1, last) if (day + 3) % 7 == 0 and day not in dict(knots).values()]
    each = max(11, rows // (2 * len(mondays)))
    listed = tuple((day, each) for day in mondays)
    ordinary = rows - len(knots) - each * len(mondays)
    weekdays = [0] * 7
    for _rank, day in knots:
        weekdays[(day + 3) % 7] += 1
    weekdays[0] += each * len(mondays)
    for weekday in range(7):
        weekdays[weekday] += ordinary // 7 + (1 if weekday < ordinary % 7 else 0)
    return {
        "knots": tuple(knots),
        "listed": listed,
        "weekdays": tuple((weekday, weekday, weekdays[weekday]) for weekday in range(7)),
        "budget": 400,
        "left": 380,
        "ordinary": ordinary,
    }


def test_the_plan_and_the_draw_count_no_more_as_rows_grow(monkeypatch: pytest.MonkeyPatch) -> None:
    """MACHINE-FREE, UP TO 1,000,000 ROWS: on one shape at 10,000, 100,000 and 1,000,000 rows the
    plan runs as many flow searches and as many augmenting rounds whatever the rows -- they are bounded
    by the parts and the groups -- and the draw reads one word per ordinary rank, no step
    restarting a search per rank or rebuilding a list per part. Red where the draw reads a word
    per rank per part."""
    asked: "dict[str, int]" = {}

    def counted(name: str, function):  # type: ignore[no-untyped-def]
        def wrapper(*args, **named):  # type: ignore[no-untyped-def]
            asked[name] = asked.get(name, 0) + 1
            return function(*args, **named)
        return wrapper

    for name in ("_heavy_flow", "_heavy_cheapest", "_heavy_spread_cells", "_heavy_few_cells", "_heavy_wide_cells"):
        monkeypatch.setattr(generation, name, counted(name, getattr(generation, name)))
    found: "dict[int, tuple[dict[str, int], int]]" = {}
    for rows in (10000, 100000, 1000000):
        state = _scaled_state(rows)
        asked.clear()
        planned = generation._heavy_plan(state["knots"], state["listed"], frozenset(), (state["weekdays"], ()), state["budget"])  # type: ignore[arg-type]
        assert planned is not None, rows
        placed, parts, owed = planned
        total = sum(part.count for part in parts)
        assert total == state["ordinary"], rows

        class Words:
            read = 0

            def __getitem__(self, index: int) -> int:
                Words.read += 1
                return (index * 0x9E3779B97F4A7C15) % (1 << 64)

        days = {day for day, _count in state["listed"]}  # type: ignore[union-attr]
        knots = frozenset(day for _rank, day in state["knots"] if day not in days)  # type: ignore[union-attr]
        values = generation._heavy_values(parts, owed, knots, state["left"], Words())  # type: ignore[arg-type]
        assert sum(len(found_values) for found_values in values) == total
        assert Words.read <= total, rows
        found[rows] = (dict(asked), len(parts))
    small, large = found[10000], found[1000000]
    assert large[1] == small[1]
    for name in small[0]:
        assert large[0].get(name, 0) <= small[0][name] + 2, (name, small, large)

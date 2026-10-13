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
* what gives way (G7.3j step 7, the orchestrator's rulings of 2026-10-13):
  `test_the_list_stands_and_what_gave_way_is_named` -- sixty tie days (the count gives
  way, named; mutant: the count weighed as e34b853 weighed it), one date a month (the
  day-of-month census gives way, named; mutant: the listed dates' rows left out of the
  weighing) and a weekly schedule of 33 at a floor of 36 (the count read as the validator
  judges it, a window; mutant: the count read exactly wherever it is reached);
  `test_the_weighing_keeps_the_list_on_a_tie_and_gives_it_way_below` (mutant: a tie gives
  the list way); `test_a_count_left_off_is_the_day_pass_s_to_repair` (mutant: step 5 no
  longer asks the count); `test_every_listed_date_is_a_hole_of_the_count_pass` (mutant: the
  holes dropped on midnight moments in a member with a mark).
  The report's sentences (D4 skeptic 2, item 1): the count case's one `n_distinct` line is the
  list's and its folded line says so (mutants: the list's causes left out of `_COUNT_CAUSES`,
  the folded line's never chosen); a weekly schedule of 0 at a floor of 36, whose twin listing
  nothing misses the day-of-month census by as many rows, keeps the day pass's own sentence
  (mutant: the census named given way where the bare twin misses it too);
  `test_the_count_s_cause_stays_the_day_pass_s_where_the_bare_twin_is_as_far` (mutant: the
  count named given way whatever the bare twin holds); `test_a_list_given_way_is_said_so_beside_the_spread`
  (mutants: the spread's missed clause in place of its given-way clause, and the given-way
  flag never raised).
* the oracle's rulings against the product's (D4 skeptic 2, item 2):
  `test_the_oracle_reads_the_count_as_the_product_does` (mutant: the oracle reads the count
  exactly below G12.5's lower end) and `test_the_oracle_weighs_a_tie_as_the_product_does`
  (mutant: the oracle's tie gives the list way).
* each part holds exactly its ranks: `test_each_part_holds_exactly_its_ranks` (mutant: the
  ranks a rounding placed beyond a part's own not trimmed).
* the Codex review of landing 3b.6 (2026-10-13): the spelling keeps the date (G7.3j step 8),
  `test_the_spelling_keeps_the_date` at floors 11 and 36 (mutant:
  the trade withdrawn, and the recount on the written cells names it) and
  `test_the_oracle_s_spelling_keeps_the_date` (mutant: the oracle's trade
  withdrawn); HD3's bound on different values, `test_repeated_unread_text_keeps_the_list`
  (mutant: rows subtracted again), `test_hd3_refuses_one_date_more`
  and its producer-always-loads battery,
  `test_unread_text_always_loads`; the census lines in
  near-linear work, `test_short_counts_in_closed_form` and
  `test_census_lines_grow_with_the_list`; and, from the verifier of
  those fixes (item 4), the trade passing a refused date in one step,
  its spellings the oracle's (`test_trades_are_the_oracle_s`) and its
  reads growing with the rows, not with the rows squared
  (`test_trades_read_dates_not_ranks`).

Test-local mutants build the product's module, and the oracle's
namespace, with one source edit (one `compile` and one `exec` each
below); the oracle is run by path (one `runpy.run_path`).
"""

from __future__ import annotations

import copy
import dataclasses
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
    rendering,
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
    # ...and two of step 7 (the orchestrator's rulings of 2026-10-13): a census that gives way
    # to the list, and the count that gives way to it
    "firsts": ("visit", lambda: _monthly_firsts()),
    "ties": ("visit", lambda: gate._tie_days(1000, 60, 83060)),
}


@pytest.mark.parametrize("label", sorted(_WHOLE))
def test_whole_columns_are_the_oracle_s(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, label: str) -> None:
    """A-P4-59: the cells the generator writes for a column listing dates that stand out, through
    the oracle's own content (method G7.3j and every pass beside it), from the same words; and
    the lower end of G12.5's envelope on the description's own gaps that steps 5 and 7 read the
    count by (the orchestrator's ruling (c) of 2026-10-13), the oracle's `count_lower_end`
    against the product's `_DateLayout.count_window`. The oracle draws tails at a floor of 11,
    so the cases stand there."""
    name, build = _WHOLE[label]
    described = kpi_shapes.describe(tmp_path, label, gate._table_text({name: build()}), 11)
    assert described.block(name)["heavy_dates"] != []
    seen: "list[tuple[list[int], list[str]]]" = []
    content = generation._datetime_content

    def captured(plan, words, settled=None):  # type: ignore[no-untyped-def]
        found = content(plan, words, settled)
        seen[:] = [(list(words), list(found[0]))]
        return found

    monkeypatch.setattr(generation, "_datetime_content", captured)
    kpi_shapes.twin_text(described, 0)
    words, ours = seen[0]
    block = copy.deepcopy(described.block(name))
    theirs = _oracle()["_datetime_content"](dict(block, _content_words=words))  # type: ignore[operator]
    assert theirs == ours, label
    column = described.loaded.columns[[one.name for one in described.loaded.columns].index(name)]
    parsed = block["n_present"] - block["n_unparsed"]
    layout = generation._date_layout(column, column.facts, parsed, 11)  # type: ignore[arg-type]
    lowest = _oracle()["count_lower_end"](block, parsed)  # type: ignore[operator]
    assert layout.count_window[0] == lowest, label


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


# -- what gives way (G7.3j step 7, the orchestrator's rulings of 2026-10-13) -------------

_STANDING = {
    # sixty tie days (tests/test_stage3b_gate.py's `_tie_days`): 53 listed, and the twin drawn
    # with the list holds 68 different days for 60, a count held exactly: the count gives way
    "count": (lambda: gate._tie_days(1000, 60, 83060), 11),
    # one date a month over 60 months (tests/test_stage3b_count_room.py's `_monthly`): 55 of
    # its 60 firsts listed, the three left a Wednesday, a Saturday and a Sunday in three parts
    # the split does not open together, so the twin drawn with the list misses the
    # day-of-month census by a few rows, where the twin listing nothing misses the listed dates
    # by hundreds: the census gives way
    "census": (lambda: _monthly_firsts(), 11),
    # a weekly schedule of 33 dates at a floor of 36 (tests/test_stage3b_weekday_review.py's
    # `_weekly_schedule`): its published count of 24 stands below G12.5's lower end, so the
    # count is a window, which the listed twin's 26 days meet (the 3b.6 skeptic's sched33)
    "window": (lambda: _weekly_schedule(33), 36),
    # a weekly schedule of 0 at a floor of 36 (the D4 skeptic 2's sched0@36): one date listed,
    # and the twins drawn with the list and listing nothing miss the day-of-month census by as
    # many rows, so the list stands and the census is not named given way to it: the day
    # pass's own sentence stands
    "both": (lambda: _weekly_schedule(0), 36),
}

# Each case's source edit of the product, red there.
_STANDING_MUTANTS = {
    # the count weighed as e34b853 weighed it: a census first, then the count's distance
    "count": (
        """    census_off, missed = _heavy_census_off(facts, ordinals, layout)
    if census_off == 0:
        return None, None
    listed = census_off + _heavy_listed_off(facts, ordinals)
""",
        """    census_off, missed = _heavy_census_off(facts, ordinals, layout)
    missed = missed or (calendar_rules.WEEKDAY_CENSUS,)
    listed = (min(census_off, 1), abs(len(set(ordinals)) - layout.distinct))
    if listed == (0, 0):
        return None, None
    def _heavy_standing(facts, ordinals, layout):  # noqa: E306
        return (min(_heavy_census_off(facts, ordinals, layout)[0], 1), abs(len(set(ordinals)) - layout.distinct))
""",
    ),
    # the listed dates' rows left out of the weighing
    "census": (
        """    return _heavy_census_off(facts, ordinals, layout)[0] + _heavy_listed_off(
        facts, ordinals
    )
""",
        """    return _heavy_census_off(facts, ordinals, layout)[0]
""",
    ),
    # the count read exactly wherever the count pass reaches it
    "window": (
        """    return contract.datetime_count_off(
        column,
        column.n_distinct,
        len(set(ordinals)) + facts.n_unparsed,
        layout.count_window,
    )
""",
        """    return abs(len(set(ordinals)) - layout.distinct)
""",
    ),
    # the census named given way to the list where the bare twin misses it too
    "both": ("        ) and note.fact not in bare_missed:\n", "        ):\n"),
}


def _monthly_firsts() -> "list[str]":
    import test_stage3b_count_room as room

    return room._monthly(1, 2017, 60, 9740)


def _weekly_schedule(shape: int) -> "list[str]":
    import test_stage3b_weekday_review as review

    return review._weekly_schedule(shape)


def _lines(twin: "generation.Twin", fact: str) -> "list[str]":
    """The sentences of one fact's deviations, but an approximated fact's line outside its
    bound (`generation._bound_notes`), which every count landing outside G12.1's range prints."""
    return [
        note.note
        for note in twin.deviations
        if note.fact == fact and not note.note.startswith("This fact is approximate by construction")
    ]


def _gave_way(twin: "generation.Twin", fact: str) -> "list[str]":
    """The deviations of one fact naming the listed dates as what it gave way to."""
    return [note.note for note in twin.deviations if note.fact == fact and "gave way to the listed dates" in note.note]


@pytest.mark.parametrize("label", sorted(_STANDING))
def test_the_list_stands_and_what_gave_way_is_named(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, label: str
) -> None:
    """G7.3j step 7 under the orchestrator's rulings of 2026-10-13. (a) Where the twin drawn
    with the list meets every census, the list stands and the count of different values gives
    way, named as the count's cause (`count`: `distinct.n_distinct` and its folded twin the only
    misses). (b) Where it misses a census by fewer rows than the twin listing nothing stands off
    the listed dates, the list stands and the census gives way, named (`census`). (c) The count
    is read as the validator judges it: a published count outside G12.5's envelope is a window,
    and a twin inside it misses nothing and names nothing (`window`). Red on each case's source
    edit: the list given way, or a count named given way that the validator holds."""
    build, floor = _STANDING[label]
    text = gate._table_text({"visit": build()})
    described = kpi_shapes.describe(tmp_path / "listed", "listed", text, floor)
    assert described.block("visit")["heavy_dates"], label
    twin = generation.generate(described.loaded, 0)
    missed = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(twin), "twin.csv"))
    assert not [note for note in twin.deviations if note.fact == calendar_rules.HEAVY_DATES], label
    expected = {
        "count": ["visit:distinct.n_distinct", "visit:distinct.n_distinct_folded"],
        "census": ["visit:day_of_month_census.groups"],
        "window": [],
        "both": ["visit:day_of_month_census.groups"],
    }
    assert missed == expected[label], label
    if label == "count":
        # one line of the count, the list's, read by the recount as the count's cause, and
        # the folded count's line saying so
        assert _lines(twin, "n_distinct") == [generation._HEAVY_COUNT_LONG]
        assert _lines(twin, "n_distinct_folded") == [generation._HEAVY_FOLDED_LONG]
    if label == "census":
        assert _gave_way(twin, calendar_rules.DAY_OF_MONTH_CENSUS) == [
            generation._HEAVY_CENSUS_GIVEN_WAY[calendar_rules.DAY_OF_MONTH_CENSUS]
        ]
    if label == "window":
        assert _gave_way(twin, "n_distinct") == []
    if label == "both":
        assert _lines(twin, calendar_rules.DAY_OF_MONTH_CENSUS) == [generation._DAY_OF_MONTH_GIVEN_WAY]
    module = _mutant(monkeypatch, *_STANDING_MUTANTS[label])
    mutated = module.generate(described.loaded, 0)
    if label == "window":
        assert _gave_way(mutated, "n_distinct") != []
        return
    if label == "both":
        assert _gave_way(mutated, calendar_rules.DAY_OF_MONTH_CENSUS) != []
        return
    kept = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(mutated), "kept.csv"))
    assert "visit:heavy_dates.counts" in kept, (label, kept)


def _step_seven(described: "kpi_shapes.Described", monkeypatch: pytest.MonkeyPatch) -> "tuple[object, ...]":
    """What step 7 is handed on the first twin of a description: the plan, the words, the
    listed twin's ranks and the layout."""
    seen: "list[tuple[object, ...]]" = []
    real = generation._heavy_given_way

    def captured(plan, words, ordinals, layout):  # type: ignore[no-untyped-def]
        if not seen:
            seen[:] = [(plan, list(words), list(ordinals), layout)]
        return real(plan, words, ordinals, layout)

    with monkeypatch.context() as patch:
        patch.setattr(generation, "_heavy_given_way", captured)
        generation.generate(described.loaded, 0)
    return seen[0]


def test_the_weighing_keeps_the_list_on_a_tie_and_gives_it_way_below(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ruling (b) at its edge, on the one-date-a-month column: the twin drawn as if no date
    were listed is taken only where it stands FEWER rows off the censuses and the listed dates
    than the listed twin, which here misses the day-of-month census alone; at as many rows the
    list stands. Taken, its deviation names the list and the census it gave way to. Red when a
    tie gives the list way."""
    text = gate._table_text({"visit": _monthly_firsts()})
    described = kpi_shapes.describe(tmp_path, "firsts", text, 11)
    plan, words, ordinals, layout = _step_seven(described, monkeypatch)
    facts = plan.column.facts  # type: ignore[attr-defined]
    census, missed = generation._heavy_census_off(facts, ordinals, layout)  # type: ignore[arg-type]
    assert census > 0 and missed == (calendar_rules.DAY_OF_MONTH_CENSUS,)
    assert generation._heavy_listed_off(facts, ordinals) == 0  # type: ignore[arg-type]
    for module, tie_stands in (
        (generation, True),
        (_mutant(monkeypatch, "    if _heavy_standing(facts, ranks, layout) >= listed:\n", "    if _heavy_standing(facts, ranks, layout) > listed:\n"), False),
    ):
        for weight, stands in ((census, tie_stands), (census - 1, False)):
            with monkeypatch.context() as patch:
                patch.setattr(module, "_heavy_standing", lambda *arguments, weight=weight: weight)
                found = module._heavy_given_way(plan, words, ordinals, layout)[0]
            assert (found is None) is stands, (module.__name__, weight)
            if found is not None:
                assert found[1][-1].fact == calendar_rules.HEAVY_DATES
                assert found[1][-1].note == generation._HEAVY_GIVEN_WAY[(calendar_rules.DAY_OF_MONTH_CENSUS,)]


def test_a_count_left_off_is_the_day_pass_s_to_repair(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3j step 5: drawn ranks that meet every census beside the list and keep off every hole
    but hold the count of different values off, as the validator judges it, are not left as
    drawn: the day pass runs, its step 8.5 included. Asked of the sixty tie days' finished
    ranks, which meet every census and hold 68 different days for 60. Red when step 5 no
    longer asks the count. Over the session family, the gate's battery at 1,000 rows, the
    joint shapes and lane D3's battery at 1,000 rows, floors 11 and 36, seeds 0 and 1, no twin
    moves when it is not asked (the repair round of plan P4-D369): a guard, the day pass
    finding no move there."""
    text = gate._table_text({"visit": gate._tie_days(1000, 60, 83060)})
    described = kpi_shapes.describe(tmp_path, "ties", text, 11)
    plan, _words, ordinals, layout = _step_seven(described, monkeypatch)
    column = plan.column  # type: ignore[attr-defined]
    facts = column.facts
    holes = generation._all_holes_of(plan)  # type: ignore[arg-type]
    assert generation._heavy_census_met(facts, ordinals, layout)  # type: ignore[arg-type]
    assert generation._heavy_count_off(column, facts, ordinals, layout) > 0  # type: ignore[arg-type]
    assert not generation._heavy_met(column, facts, ordinals, layout, holes)  # type: ignore[arg-type]
    module = _mutant(
        monkeypatch,
        "    if _heavy_count_off(column, facts, ordinals, layout) > 0:\n        return False\n    if not _heavy_census_met(",
        "    if not _heavy_census_met(",
    )
    assert module._heavy_met(column, facts, ordinals, layout, holes)


def test_the_count_s_cause_stays_the_day_pass_s_where_the_bare_twin_is_as_far(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Ruling (a)'s naming at its edge (the D4 skeptic 2's item 1, F): the count is named given way
    to the list only where the twin listing nothing stands NEARER the count as the validator
    judges it. Asked of the sixty tie days' kept notes, `_heavy_count_off` held at one distance
    for both twins and the day pass's own cause of a long count among the notes: that cause is
    kept and the list is not named. Red when the count is named given way whatever the twin
    listing nothing holds."""
    text = gate._table_text({"visit": gate._tie_days(1000, 60, 83060)})
    described = kpi_shapes.describe(tmp_path, "ties", text, 11)
    plan, words, ordinals, layout = _step_seven(described, monkeypatch)
    name = plan.column.name  # type: ignore[attr-defined]
    own = generation._deviation(name, "n_distinct", "60 different values", "68 different values", generation._WEEKDAY_DAYS_LEFT_LONG)
    named = (generation._HEAVY_COUNT_SHORT, generation._HEAVY_COUNT_LONG)
    edit = ("    caused = off > 0 and _heavy_count_off(column, facts, bare, layout) < off\n", "    caused = off > 0\n")
    # the product first, then the mutant built from its source
    for kept in (True, False):
        module = generation if kept else _mutant(monkeypatch, *edit)
        with monkeypatch.context() as patch:
            patch.setattr(module, "_heavy_count_off", lambda *arguments: 5)
            found = [note.note for note in module._heavy_kept_notes(plan, words, ordinals, layout, [own], None)]
        assert (found == [own.note]) is kept, module.__name__
        assert (not [note for note in found if note in named]) is kept, module.__name__


def test_a_list_given_way_is_said_so_beside_the_spread(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Where step 7 gives the list way, the column's sentence on its spread says the listed dates
    gave way to a census beside them (`_SPREAD_HEAVY_GIVEN_WAY`), not that the twin missed them
    (the D4 skeptic 2's item 1, N and T). No column of the batteries gives its list way under the
    rulings of 2026-10-13, so the weighing is held one row below the listed twin's, as the tie
    test holds it, on the one-date-a-month column. Red when the spread's missed clause is said in
    its place, and when the given-way flag is never raised."""
    text = gate._table_text({"visit": _monthly_firsts()})
    described = kpi_shapes.describe(tmp_path, "firsts", text, 11)
    plan, _words, ordinals, layout = _step_seven(described, monkeypatch)
    census = generation._heavy_census_off(plan.column.facts, ordinals, layout)[0]  # type: ignore[attr-defined]
    edits = (
        ("                + [_SPREAD_HEAVY_GIVEN_WAY if given_way else _SPREAD_HEAVY_MISSED]\n", "                + [_SPREAD_HEAVY_MISSED]\n"),
        ("                and note.note in _HEAVY_GIVEN_WAY_NOTES\n", "                and False\n"),
    )
    # the product first, then each mutant built from its source
    for edit in (None, *edits):
        module, said = (generation, True) if edit is None else (_mutant(monkeypatch, *edit), False)
        with monkeypatch.context() as patch:
            patch.setattr(module, "_heavy_standing", lambda *arguments: census - 1)
            twin = module.generate(described.loaded, 0)
        assert [note.fact for note in twin.deviations] == [calendar_rules.HEAVY_DATES], module.__name__
        spread = [remark.note for remark in twin.remarks if remark.column == "visit" and "spread across the calendar" in remark.subject]
        assert len(spread) == 1, module.__name__
        assert (generation._SPREAD_HEAVY_GIVEN_WAY in spread[0]) is said, module.__name__
        assert (generation._SPREAD_HEAVY_MISSED in spread[0]) is not said, module.__name__


def _oracle_mutant(before: str, after: str) -> "dict[str, object]":
    """The oracle's namespace with ONE source edit, built as the product's mutants are (an edit
    that no longer applies turns the test red)."""
    text = ORACLE.read_text(encoding="utf-8")
    assert text.count(before) == 1, before
    found: "dict[str, object]" = {"__name__": "oracle_mutant", "__file__": str(ORACLE)}
    exec(compile(text.replace(before, after), str(ORACLE), "exec"), found)
    return found


def test_the_oracle_reads_the_count_as_the_product_does(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A-P4-59 on ruling (c) (the D4 skeptic 2's item 2, O): the oracle's `heavy_count_off`
    against the product's `_heavy_count_off` on hand-built ranks of the sixty tie days at a floor
    of 11 -- their ranks folded onto fewer and fewer of their own days -- with the published
    count where the description puts it (inside G12.5's envelope: read exactly) and two below the
    envelope's lower end (a window: the distance below that end, nought at or above it), the
    folded count published beside it as raw so that the count stays reached. The
    oracle's whole columns stand at a floor of 11, where no column of the batteries publishes a
    count below that end, so the window is asked here. Red when the oracle reads the count
    exactly below the lower end."""
    text = gate._table_text({"visit": gate._tie_days(1000, 60, 83060)})
    described = kpi_shapes.describe(tmp_path, "ties", text, 11)
    plan, _words, ordinals, layout = _step_seven(described, monkeypatch)
    column = plan.column  # type: ignore[attr-defined]
    block = copy.deepcopy(described.block("visit"))
    parsed = block["n_present"] - block["n_unparsed"]
    lowest = int(layout.count_window[0])  # type: ignore[attr-defined]
    assert column.n_distinct >= lowest > 3
    days = sorted(set(ordinals))  # type: ignore[arg-type]
    place = {day: index for index, day in enumerate(days)}
    asked = []
    for published in (column.n_distinct, lowest - 2):
        changed = dataclasses.replace(column, n_distinct=published, n_distinct_folded=published)
        for held in (lowest - 3, lowest - 2, lowest, len(days)):
            ranks = [days[min(place[day], held - 1)] for day in ordinals]  # type: ignore[union-attr]
            asked += [(published, ranks, generation._heavy_count_off(changed, column.facts, ranks, layout))]  # type: ignore[arg-type]
    assert [off for published, _ranks, off in asked if published < lowest] == [3, 2, 0, 0]
    edit = ('    if column["n_distinct"] >= lowest:\n', "    if True:\n")
    # the oracle first, then its mutant
    for agrees in (True, False):
        oracle = _oracle() if agrees else _oracle_mutant(*edit)
        assert oracle["count_lower_end"](block, parsed) == lowest  # type: ignore[operator]
        theirs = [oracle["heavy_count_off"](dict(block, n_distinct=published, n_distinct_folded=published), ranks, parsed) for published, ranks, _off in asked]  # type: ignore[operator]
        assert (theirs == [off for _published, _ranks, off in asked]) is agrees


def test_the_oracle_weighs_a_tie_as_the_product_does(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A-P4-59 on ruling (b) (the D4 skeptic 2's item 2, Q): step 7's weighing in the oracle's
    content against the product's, on the one-date-a-month column at a floor of 11, the twin
    listing nothing held at as many rows off as the listed twin (the list stands) and at one
    fewer (it gives way), in both. No column of the batteries ties. Red when the oracle's tie
    gives the list way."""
    text = gate._table_text({"visit": _monthly_firsts()})
    described = kpi_shapes.describe(tmp_path, "firsts", text, 11)
    plan, _words, ordinals, layout = _step_seven(described, monkeypatch)
    facts = plan.column.facts  # type: ignore[attr-defined]
    census = generation._heavy_census_off(facts, ordinals, layout)[0]  # type: ignore[arg-type]
    assert census > 0 and generation._heavy_listed_off(facts, ordinals) == 0  # type: ignore[arg-type]
    content = generation._datetime_content
    drawn = []
    for weight in (census, census - 1):
        seen: "list[tuple[list[int], list[str]]]" = []

        def captured(plan, words, settled=None, seen=seen):  # type: ignore[no-untyped-def]
            found = content(plan, words, settled)
            seen[:] = [(list(words), list(found[0]))]
            return found

        with monkeypatch.context() as patch:
            patch.setattr(generation, "_datetime_content", captured)
            patch.setattr(generation, "_heavy_standing", lambda *arguments, weight=weight: weight)
            generation.generate(described.loaded, 0)
        drawn += [(weight, *seen[0])]
    assert drawn[0][2] != drawn[1][2]
    block = copy.deepcopy(described.block("visit"))
    edit = ("            if heavy_standing(column, kept[0], parsed) < listed:\n", "            if heavy_standing(column, kept[0], parsed) <= listed:\n")
    # the oracle first, then its mutant
    for agrees in (True, False):
        oracle = _oracle() if agrees else _oracle_mutant(*edit)
        found = []
        for weight, words, ours in drawn:
            oracle["_datetime_content"].__globals__["heavy_standing"] = lambda *arguments, weight=weight: weight  # type: ignore[attr-defined]
            found += [oracle["_datetime_content"](dict(block, _content_words=words)) == ours]  # type: ignore[operator]
        assert all(found) is agrees


def test_every_listed_date_is_a_hole_of_the_count_pass(tmp_path: pathlib.Path) -> None:
    """G7.3j step 5: every listed date is a unit the count pass offers no rank
    (`_count_holes`), on whole dates and on moments at midnight in a member with a mark,
    where no absent spelling names one. Red when the holes are dropped on the second."""
    days = gate._BATTERY["heaps"](1000)["billing_date"]
    for label, cells in (("dates", days), ("midnight", [cell + "T00:00:00" for cell in days])):
        described = kpi_shapes.describe(tmp_path / label, label, gate._table_text({"billed": cells}), 11)
        listed = described.block("billed")["heavy_dates"]
        assert listed, label
        facts = described.loaded.columns[0].facts
        held = generation._count_holes(facts, ())
        assert {parsing.days_from_civil(*map(int, entry["date"].split("-"))) for entry in listed} <= set(held), label


def test_each_part_holds_exactly_its_ranks(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.3j step 4: each part's shares hold exactly its ranks (`_heavy_whole`) -- a rank no
    flow placed goes to the part's widest key, and ranks a rounding placed beyond the part's own
    leave its fullest key. Asked of every call on a weekly schedule of 2 at a floor of 11, whose
    rake places more than a part's own at seed 0 (the repair round of plan P4-D369: 31 columns of
    the batteries reach it, 193 times). Red when the excess is not trimmed."""
    text = gate._table_text({"visit": _weekly_schedule(2)})
    described = kpi_shapes.describe(tmp_path, "schedule2", text, 11)
    assert described.block("visit")["heavy_dates"]
    seen: "list[tuple[object, ...]]" = []
    real = generation._heavy_whole

    def captured(shares, days_of, supply):  # type: ignore[no-untyped-def]
        seen[len(seen):] = [(copy.deepcopy(shares), days_of, list(supply))]
        return real(shares, days_of, supply)

    with monkeypatch.context() as patch:
        patch.setattr(generation, "_heavy_whole", captured)
        generation.generate(described.loaded, 0)

    def beyond(shares, days_of, supply) -> bool:  # type: ignore[no-untyped-def]
        return any(
            sum(count for key, count in shares[place].items() if key in days_of[place] and count > 0) > supply[place]
            for place in range(len(shares))
        )

    assert any(beyond(*call) for call in seen)
    module = _mutant(monkeypatch, "        while short < 0:\n", "        while False:\n")
    for whole, holds in ((generation._heavy_whole, True), (module._heavy_whole, False)):
        found = [whole(copy.deepcopy(shares), days_of, supply) for shares, days_of, supply in seen]
        exact = all(
            sum(parts[place].values()) == supply[place]
            for parts, (_shares, _days, supply) in zip(found, seen)
            for place in range(len(supply))
        )
        assert exact is holds


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


# -- the Codex review of landing 3b.6 (2026-10-13) -----------------------------------------


def _absent_third_of_may() -> "list[str]":
    """Codex's item 1: 900 dates cycling daily through 2022, then 100 copies of 3 May, written
    alternately padded and unpadded day first, then twenty `3/5/2022` cells."""
    days = [parsing.days_from_civil(2022, 1, 1) + step % 365 for step in range(900)]
    days += [parsing.days_from_civil(2022, 5, 3)] * 100
    cells: "list[str]" = []
    for index in range(len(days)):
        year, month, day = parsing.civil_from_days(days[index])
        cells += [f"{day:02d}/{month:02d}/{year}" if index % 2 == 0 else f"{day}/{month}/{year}"]
    return cells + ["3/5/2022"] * 20


def _described_missing(folder: pathlib.Path, cells: "list[str]", floor: int, missing: "tuple[str, ...]") -> kpi_shapes.Described:
    """One column described with `missing` declared as no value, as `synthtwin describe
    --missing` declares it."""
    import fixtures
    from synthtwin import contract, profile, reading

    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "visits.csv", gate._table_text({"visit": cells}))
    settings = taxonomy.Settings(small_cell_floor=floor, declared_missing_values=missing)
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor, missing_under=settings), settings, [], [], [],
    )
    written = fixtures.write_profile(folder, "visits-profile.json", document)
    return kpi_shapes.Described(folder, table, document, contract.load_profile(str(written)))


@pytest.mark.parametrize("floor", (11, 36))
def test_the_spelling_keeps_the_date(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, floor: int) -> None:
    """THE CODEX REVIEW OF LANDING 3b.6, ITEM 1 (G7.3j step 8). 3 May lists 52 rows; half the ranks
    the spelling allocation put there were `3/5/2022`, which the table declares missing, and
    the step off an absent spelling moved 21 of them to other dates after the ranks held 52: the
    twin at seed 0 held 31, V5-D1 MISSED, and the report said every listed count was met. Now
    each such rank trades its spelling with a rank of its class on an ordinary date
    (`_listed_date_respelled`): the twin holds 52, nothing the source meets is missed (the
    width census included), and the report says the listed dates are met. Mutant: the
    trade withdrawn -- the cells miss 3 May again and the recount on the written cells
    (`_heavy_written_notes`) names `heavy_dates`, so the sentence says they are not met."""
    described = _described_missing(tmp_path, _absent_third_of_may(), floor, ("3/5/2022",))
    assert described.block("visit")["heavy_dates"] == [{"date": "2022-05-03", "count": 52}]
    source = kpi_shapes.missed(kpi_shapes.measure(described, described.table.read_text(encoding="utf-8"), "source.csv"))
    text = kpi_shapes.twin_text(described, 0)
    assert _column(text, "visit").count("03/05/2022") == 52
    assert kpi_shapes.missed(kpi_shapes.measure(described, text, "twin.csv")) == source == []
    twin = generation.generate(described.loaded, 0)
    # the one thing the report names is the width census's own spread, named on ba02cd8 too
    assert {d.fact for d in twin.deviations if d.column == "visit"} == {"date_field_widths"}
    said = [r for r in twin.remarks if r.column == "visit" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_HEAVY_MET in said[0].held, said
    monkeypatch.setattr(generation, "_listed_date_respelled", lambda keep, rank: False)
    text = kpi_shapes.twin_text(described, 0)
    assert _column(text, "visit").count("03/05/2022") < 52
    missed = kpi_shapes.missed(kpi_shapes.measure(described, text, "mutant.csv"))
    assert "visit:heavy_dates.counts" in missed, missed
    twin = generation.generate(described.loaded, 0)
    notes = [d.note for d in twin.deviations if d.column == "visit" and d.fact == "heavy_dates"]
    assert notes == [generation._HEAVY_WRITTEN_MISSED], notes
    said = [r.note for r in twin.remarks if r.column == "visit" and r.subject == generation._SPREAD_SUBJECT]
    assert len(said) == 1 and generation._SPREAD_HEAVY_MISSED in said[0], said


def test_the_oracle_s_spelling_keeps_the_date(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A-P4-59 for G7.3j step 8: on item 1's column at a floor of 11 the oracle's content, from
    the same words, is the product's cell for cell; mutant: the oracle's trade withdrawn."""
    described = _described_missing(tmp_path, _absent_third_of_may(), 11, ("3/5/2022",))
    seen: "list[tuple[list[int], list[str]]]" = []
    content = generation._datetime_content

    def captured(plan, words, settled=None):  # type: ignore[no-untyped-def]
        found = content(plan, words, settled)
        seen[:] = [(list(words), list(found[0]))]
        return found

    monkeypatch.setattr(generation, "_datetime_content", captured)
    kpi_shapes.twin_text(described, 0)
    words, ours = seen[0]
    block = copy.deepcopy(described.block("visit"))
    assert ours[:1000].count("03/05/2022") == 52
    theirs = _oracle()["_datetime_content"](dict(block, _content_words=words))  # type: ignore[operator]
    assert theirs == ours
    mutant = _oracle_mutant("        spellings = listed_dates_kept_in_spelling(\n", "        spellings = spellings if True else listed_dates_kept_in_spelling(\n")
    assert mutant["_datetime_content"](dict(block, _content_words=words)) != ours  # type: ignore[operator]


def _weekly_with_unread(unread: "list[str]", replaced: bool) -> "list[str]":
    """Codex's item 2: sixty weekly dates from 2020-01-02, each eleven times, with `unread`
    texts in place of cells 300 onward (`replaced`) or after them."""
    cells: "list[str]" = []
    for week in range(60):
        year, month, day = parsing.civil_from_days(parsing.days_from_civil(2020, 1, 2) + 7 * week)
        cells += [f"{year:04d}-{month:02d}-{day:02d}"] * 11
    if replaced:
        return cells[:300] + unread + cells[300 + len(unread):]
    return cells + unread


def test_repeated_unread_text_keeps_the_list(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """THE CODEX REVIEW OF LANDING 3b.6, ITEM 2 (contract HD3, amended). Five copies of one unread
    text in place of cells 300 to 304: 60 dates, 61 different values, five unread rows; 57
    dates stand out, and the producer withdrew the whole list against 61 - 5 = 56, where five
    different unread texts kept all 57. The bound is now the column's different values less
    one where any cell is unread (`calendar_rules.heavy_different`), asked by the producer and
    the loader alike: both columns list the same 57 dates. Mutant: rows subtracted again."""
    same = kpi_shapes.describe(tmp_path / "same", "same", gate._table_text({"visit": _weekly_with_unread(["2020-07-09T00:00:00"] * 5, True)}), 11)
    other = kpi_shapes.describe(tmp_path / "other", "other", gate._table_text({"visit": _weekly_with_unread([f"2020-07-0{k}T00:00:00" for k in range(5)], True)}), 11)
    assert (same.block("visit")["n_distinct"], same.block("visit")["n_unparsed"]) == (61, 5)
    assert len(same.block("visit")["heavy_dates"]) == 57
    assert same.block("visit")["heavy_dates"] == other.block("visit")["heavy_dates"]
    assert calendar_rules.heavy_different(61, 5) == 60 and calendar_rules.heavy_different(61, 0) == 61
    monkeypatch.setattr(calendar_rules, "heavy_different", lambda n_distinct, n_unparsed: n_distinct - n_unparsed)
    mutant = kpi_shapes.describe(tmp_path / "mutant", "same", gate._table_text({"visit": _weekly_with_unread(["2020-07-09T00:00:00"] * 5, True)}), 11)
    assert mutant.block("visit")["heavy_dates"] == []


def test_hd3_refuses_one_date_more() -> None:
    """HD3 as the loader asks it: a list as long as the bound passes, one date more is refused,
    with and without unread cells."""
    first = parsing.days_from_civil(2020, 1, 2)
    listed = tuple((first + 7 * week, 11) for week in range(1, 4))
    knots = ((0, first), (200, first + 7 * 10))
    for n_distinct, n_unparsed in ((4, 3), (3, 0)):
        room = (first, first + 70, 180, calendar_rules.heavy_different(n_distinct, n_unparsed))
        assert calendar_rules.heavy_breach(listed, 11, room, frozenset(), knots, ((), ())) is None
        room = (first, first + 70, 180, calendar_rules.heavy_different(n_distinct - 1, n_unparsed))
        broken = calendar_rules.heavy_breach(listed, 11, room, frozenset(), knots, ((), ()))
        assert broken is not None and broken[0] == "HD3", broken


def test_unread_text_always_loads(tmp_path: pathlib.Path) -> None:
    """THE PRODUCER-ALWAYS-LOADS BATTERY OF THE AMENDED HD3: the weekly column beside unread
    text repeated in every way a column of dates keeps it -- one text five times in place of
    cells, six times after the dates, two texts three times each, three texts twice each in
    place of cells, a text no member reads five times -- at floors 1, 11 and 36, described by
    the shipped producer and loaded by the shipped loader (`kpi_shapes.describe` loads each);
    at floors 1 and 11 each lists dates (four of the five lists the rows bound withdrew), and
    at 11 the twin at seed 0 holds every listed date (V5-D1 HELD)."""
    tables = {
        "five_same": _weekly_with_unread(["2020-07-09T00:00:00"] * 5, True),
        "six_after": _weekly_with_unread(["2020-07-09T00:00:00"] * 6, False),
        "two_by_three": _weekly_with_unread(["2020-07-09T00:00:00", "2020-08-13T00:00:00"] * 3, False),
        "three_by_two": _weekly_with_unread(["2020-07-09T00:00:00", "2020-02-06T00:00:00", "2020-03-05T00:00:00"] * 2, True),
        "garbled": _weekly_with_unread(["2020-13-45"] * 5, False),
    }
    listed = 0
    withdrawn = 0
    for floor in (1, 11, 36):
        for label, cells in tables.items():
            described = kpi_shapes.describe(tmp_path / f"{label}-{floor}", label, gate._table_text({"visit": cells}), floor)
            block = described.block("visit")
            assert block["n_unparsed"] > 0, label
            if not block["heavy_dates"]:
                assert floor == 36, label
                continue
            listed += 1
            withdrawn += len(block["heavy_dates"]) > block["n_distinct"] - block["n_unparsed"]
            if floor != 11:
                continue
            text = kpi_shapes.twin_text(described, 0)
            outcome = kpi_shapes.measure(described, text, f"{label}.csv")
            held = [c for c in outcome.checks if c.column == "visit" and c.subcheck == "heavy_dates.counts"]
            assert len(held) == 1 and held[0].verdict == validation.HELD, label
    assert (listed, withdrawn) == (10, 8)


def _pinned_by_walking(found: "list[int]", short: "list[int]", line: int) -> bool:
    """`validation._short_counts_pinned` as 64c452c wrote it, every total and value walked."""
    total = sum(found)
    many = len(short)
    others = len(found) - many
    possible: "set[int]" = set()
    for together in range(many, many * (line - 1) + 1):
        rest = total - together
        if rest < 0 or (rest != 0 and (others == 0 or rest < line)):
            continue
        for value in range(1, line):
            left = together - value
            if (many - 1) <= left <= (many - 1) * (line - 1):
                possible = possible | {value}
    return len(possible) <= 1


def test_short_counts_in_closed_form() -> None:
    """THE CODEX REVIEW OF LANDING 3b.6, ITEM 3: the closed form of `_short_counts_pinned` answers
    as the walk did on 6,000 random censuses of one to nine groups, lines 2 to 12."""
    chooser = random.Random(20261013)
    for _ in range(6000):
        line = chooser.randint(2, 12)
        groups = chooser.randint(1, 9)
        found = [chooser.choice([0, chooser.randint(1, line - 1), chooser.randint(line, 3 * line)]) for _ in range(groups)]
        short = [index for index in range(groups) if 0 < found[index] < line]
        if not short:
            continue
        assert validation._short_counts_pinned(found, short, line) == _pinned_by_walking(found, short, line), (found, line)


def _census_seconds(entries: int, short: bool) -> float:
    """The least of three timings of `_census_lines` over `entries` listed dates."""
    import time

    groups = [(f"date {index}", 40) for index in range(entries)]
    found = [5 if short and index % 2 == 0 else 40 for index in range(entries)]
    least = 0.0
    for attempt in range(3):
        started = time.process_time()
        validation._census_lines(groups, found, 11)
        spent = time.process_time() - started
        least = spent if attempt == 0 else min(least, spent)
    return least


def test_census_lines_grow_with_the_list() -> None:
    """THE CODEX REVIEW OF LANDING 3b.6, ITEM 3: V5-D1 prints one group per listed date, and
    `_census_lines` rebuilt its cumulative text per group and scanned the short groups' list
    per group -- 0.014 seconds at 5,000 entries, 2.4 at 80,000 (ten at 80,000 with half of
    them short). Eight times the entries now take less than twenty times the time, met and
    short, and 80,000 short entries print in under a second; the walk restored is red."""
    chooser = random.Random(7)
    for many in range(0, 40):
        parts = [f"date {chooser.randint(0, 99)}" for _ in range(many)]
        assert validation._comma_joined(parts) == ", ".join(parts)
    for short in (False, True):
        small = _census_seconds(10000, short)
        large = _census_seconds(80000, short)
        assert large < 20 * max(small, 0.002), (short, small, large)
        assert large < 1.0, (short, large)



# -- the verifier of the Codex review's fixes (2026-10-13): the trade reads a date in one step --

_TRADE_FORMAT = "trade-test-numeric"


def _trade_case(chooser: random.Random) -> "dict[str, object]":
    """A random column for G7.3j step 8's trade: up to 150 dates of one to six ranks, two or
    three spellings, two marks, sometimes two offsets and bare dates, and each date, mark and
    spelling absent at a random rate; or, a third of the time, a few dates out of order, each
    split into short runs in shuffled order, the listed ones into more."""
    ordinals: "list[int]" = []
    if chooser.random() < 0.3:
        days = sorted(chooser.sample(range(18000, 18400), chooser.randint(3, 8)))
        listed = chooser.sample(days, chooser.randint(1, 2))
        runs: "list[list[int]]" = []
        for day in days:
            many = chooser.randint(6, 12) if day in listed else chooser.randint(2, 5)
            runs += [[day] * chooser.randint(1, 3) for _ in range(many)]
        chooser.shuffle(runs)
        for run in runs:
            ordinals += run
    else:
        days = sorted(chooser.sample(range(18000, 18400), chooser.randint(3, 150)))
        listed = chooser.sample(days, chooser.randint(1, min(3, len(days))))
        for day in days:
            ordinals += [day] * chooser.randint(1, 6)
    ranks = range(len(ordinals))
    styles = ("padded", "bare", "named")[: chooser.randint(2, 3)]
    spread = chooser.random() < 0.3
    rate = chooser.choice((0.3, 0.8, 0.97, 0.99))
    return {
        "ordinals": ordinals,
        "offsets": [chooser.choice(("", "+01:00")) if spread else "" for _ in ranks],
        "marks": [chooser.choice(("", "pm")) for _ in ranks],
        "whole": [spread and chooser.random() < 0.2 for _ in ranks],
        "spellings": [chooser.choice(styles) for _ in ranks],
        "listed": listed,
        "absent": {(day, mark, style): chooser.random() < rate for day in days for mark in ("", "pm") for style in styles},
    }


def _rejoined_case() -> "dict[str, object]":
    """A refused day rejoined: D (marks none, then `pm`), X twice, D again, then three ranks of a
    listed date L wearing an absent spelling. The trades take both X; D's later run then joins
    its refused first, so the third rank finds no partner and takes the spelling alone."""
    days = [18000, 18002, 18002, 18000, 18004, 18004, 18004]
    absent = {(day, mark, style): False for day in (18000, 18002, 18004) for mark in ("", "pm") for style in ("padded", "bare")}
    absent.update({(18004, "", "bare"): True, (18000, "", "bare"): True})
    return {
        "ordinals": days,
        "offsets": [""] * 7,
        "marks": ["", "", "", "pm", "", "", ""],
        "whole": [False] * 7,
        "spellings": ["padded"] * 4 + ["bare"] * 3,
        "listed": [18004],
        "absent": absent,
    }


def _limit_case() -> "dict[str, object]":
    """Sixty-four dates refused, then one that would take the trade, then a listed date's rank
    wearing an absent spelling: the trade gives up at the limit and takes the spelling alone."""
    days = [18000 + 2 * step for step in range(66)]
    absent = {(day, mark, style): day != days[64] and style == "bare" for day in days for mark in ("", "pm") for style in ("padded", "bare")}
    return {
        "ordinals": days,
        "offsets": [""] * 66,
        "marks": [""] * 66,
        "whole": [False] * 66,
        "spellings": ["padded"] * 65 + ["bare"],
        "listed": [days[65]],
        "absent": absent,
    }


def _traded(case: "dict[str, object]", module: types.ModuleType, monkeypatch: pytest.MonkeyPatch, oracle: "dict[str, object] | None" = None) -> "list[object]":
    """The spellings `_listed_spellings` gives the case (or the oracle's step, `oracle`), every
    cell's absence read off the case: a written cell is `(day, offset, mark, form, spelling)`."""
    ordinals, offsets, marks, whole = case["ordinals"], case["offsets"], case["marks"], case["whole"]
    absent = case["absent"]
    fields = [(1 + 10 * (day % 2), 5) for day in ordinals]  # type: ignore[union-attr]

    def asked(written: "tuple[object, ...]") -> bool:
        return absent[(written[0], written[2], written[4])]  # type: ignore[index]

    if oracle is not None:
        listed = [parsing.civil_from_days(day) for day in case["listed"]]  # type: ignore[union-attr]
        column = {"format": _TRADE_FORMAT, "heavy_dates": [{"date": f"{y:04d}-{m:02d}-{d:02d}", "count": 1} for y, m, d in listed]}
        return oracle["listed_dates_kept_in_spelling"](  # type: ignore[operator]
            column, ordinals, list(case["spellings"]), fields, whole, offsets,  # type: ignore[call-overload]
            lambda rank, style: (ordinals[rank], offsets[rank], marks[rank], whole[rank], style), asked,  # type: ignore[index]
        )
    monkeypatch.setattr(module, "_written_fields", lambda facts, ordinals, offsets, parsed: fields)
    monkeypatch.setattr(module, "_listed_absent", lambda keep, rank, style: asked((keep.ordinals[rank], keep.offsets[rank], keep.marks[rank], keep.whole[rank], style)))
    facts = types.SimpleNamespace(parser_family=_TRADE_FORMAT)
    return module._listed_spellings(facts, ordinals, offsets, marks, whole, list(case["spellings"]), ("x",), frozenset(case["listed"]))  # type: ignore[call-overload]


_TRADE_SCAN_NEW = """        starts = keep.runs[place]
        spent = keep.spent[place]
        last = len(starts) - 1
        run = _listed_free(spent, 0)
        refused = 0
        while run < last and refused < _LISTED_PROBES:
            # The run's first rank not yet traded: a run in `spent` has none.
            at = _listed_free(skip, starts[run])
            other = queue[at]
            if not _listed_absent(keep, other, own):
                keep.spellings[rank] = style
                keep.spellings[other] = own
                skip[at] = at + 1
                if _listed_free(skip, at + 1) >= starts[run + 1]:
                    spent[run] = run + 1
                return True
            refused = refused + 1
            day = keep.ordinals[other]
            # A refused date's following ranks are passed over: its run,
            # and any run of the same day its traded neighbours now join.
            run = _listed_free(spent, run + 1)
            while run < last and keep.ordinals[queue[starts[run]]] == day:
                run = _listed_free(spent, run + 1)
"""
# The rank walk of 9a0338d, which the verifier measured.
_TRADE_SCAN_OLD = """        at = _listed_free(skip, 0)
        refused = 0
        while at < len(queue) and refused < _LISTED_PROBES:
            other = queue[at]
            if not _listed_absent(keep, other, own):
                keep.spellings[rank] = style
                keep.spellings[other] = own
                skip[at] = at + 1
                return True
            refused = refused + 1
            day = keep.ordinals[other]
            while at < len(queue) and keep.ordinals[queue[at]] == day:
                at = _listed_free(skip, at + 1)
"""


def test_trades_are_the_oracle_s(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE VERIFIER OF THE CODEX REVIEW'S FIXES, ITEM 4 (G7.3j step 8): the trade now passes a
    refused date in one step (`keep.runs`, `keep.spent`) where it walked the date's ranks. On
    700 random columns -- dates out of order, runs emptied by trades, several spellings of
    listed ranks seeking one queue -- and two built ones (a refused day's run rejoining it
    once the runs between are traded, `_rejoined_case`; a date past the limit of 64,
    `_limit_case`), the product's spellings are
    the oracle's rank walk's and 9a0338d's; each mutant (a refused day's later runs read
    again, a run emptied still read, one date more than the limit) is red."""
    oracle = _oracle()
    chooser = random.Random(19)
    cases = [_trade_case(chooser) for _ in range(700)] + [_rejoined_case(), _limit_case()]
    theirs = [_traded(case, generation, monkeypatch, oracle) for case in cases]
    walk = _mutant(monkeypatch, _TRADE_SCAN_NEW, _TRADE_SCAN_OLD)
    changed = 0
    for index in range(len(cases)):
        ours = _traded(cases[index], generation, monkeypatch)
        assert ours == theirs[index], index
        assert _traded(cases[index], walk, monkeypatch) == ours, index
        changed += ours != cases[index]["spellings"]
    assert changed > 250, changed
    assert theirs[-2] == ["padded", "bare", "bare", "padded", "padded", "padded", "padded"], theirs[-2]
    assert theirs[-1] == ["padded"] * 66, theirs[-1]
    for before, after in (
        ("            while run < last and keep.ordinals[queue[starts[run]]] == day:\n", "            while False:\n"),
        ("                    spent[run] = run + 1\n", "                    pass\n"),
        ("        while run < last and refused < _LISTED_PROBES:\n", "        while run < last and refused <= _LISTED_PROBES:\n"),
    ):
        mutant = _mutant(monkeypatch, before, after)
        assert any(_traded(cases[index], mutant, monkeypatch) != theirs[index] for index in range(len(cases))), before


def _trade_shape(scale: int) -> "dict[str, object]":
    """The verifier's shape at `scale`: a tail date of 400 * `scale` ranks spelled padded, whose
    unpadded spelling is absent, then 900 * `scale` ranks cycling over 362 days and 100 *
    `scale` on 3 May, whose unpadded spelling is absent, spelled alternately padded and not;
    the tail date (1 January) shows the conventions 3 May shows (`_traded`'s fields)."""
    front = parsing.days_from_civil(2022, 1, 1)
    listed = parsing.days_from_civil(2022, 5, 3)
    days = [front] * (400 * scale)
    days += sorted([parsing.days_from_civil(2022, 1, 3) + step % 362 for step in range(900 * scale)] + [listed] * (100 * scale))
    return {
        "ordinals": days,
        "offsets": [""] * len(days),
        "marks": [""] * len(days),
        "whole": [False] * len(days),
        "spellings": ["padded" if rank < 400 * scale or rank % 2 == 0 else "bare" for rank in range(len(days))],
        "listed": [listed],
        "absent": {(day, "", style): style == "bare" and day in (front, listed) for day in set(days) for style in ("padded", "bare")},
    }


def _trade_reads(module: types.ModuleType, monkeypatch: pytest.MonkeyPatch, case: "dict[str, object]") -> "tuple[int, list[object]]":
    """How many queue places the trade reads (`_listed_free`) on `case`, and the spellings given."""
    reads = [0]
    free = module._listed_free

    def counted(skip: "dict[int, int]", at: int) -> int:
        reads[0] += 1
        return free(skip, at)

    monkeypatch.setattr(module, "_listed_free", counted)
    found = _traded(case, module, monkeypatch)
    monkeypatch.setattr(module, "_listed_free", free)
    return reads[0], found


def test_trades_read_dates_not_ranks(monkeypatch: pytest.MonkeyPatch) -> None:
    """THE VERIFIER OF THE CODEX REVIEW'S FIXES, ITEM 4: beside a tail date whose other spelling
    is absent, every listed rank's trade walked that date's ranks again -- 11 seconds of trades
    at 227,220 rows, 3.7 times as long for twice the rows. Four times the rows now read fewer
    than six times the queue places, every rank of the listed date kept in the spelling not
    absent and the census of spellings unchanged; the rank walk restored reads more than
    twelve times as many, and gives the same spellings."""
    small, _found = _trade_reads(generation, monkeypatch, _trade_shape(1))
    case = _trade_shape(4)
    large, found = _trade_reads(generation, monkeypatch, case)
    assert large < 6 * small, (small, large)
    ordinals, before = case["ordinals"], case["spellings"]
    held = {found[rank] for rank in range(len(found)) if ordinals[rank] == case["listed"][0]}  # type: ignore[index]
    assert held == {"padded"} and found.count("bare") == before.count("bare")  # type: ignore[union-attr]
    walk = _mutant(monkeypatch, _TRADE_SCAN_NEW, _TRADE_SCAN_OLD)
    slow_small, _found = _trade_reads(walk, monkeypatch, _trade_shape(1))
    slow_large, slow = _trade_reads(walk, monkeypatch, case)
    assert slow == found
    assert slow_large > 12 * slow_small, (slow_small, slow_large)

"""Landing 3b.7's gate (plan P4-D378): the calendar on columns of two offsets and of the joint member.

Every census of the calendar -- the weekday (WC3), the day of the month
(DM5) and the hour (HC3) -- is published on a column whose cells wear more
than one UTC offset, and on one mixing bare dates with moments, each cell
RANKED by its instant on the published clock and COUNTED at the day and
hour it is WRITTEN at, on its own clock, a bare date at its midnight. The
generator writes every rank at its own offset and form, the offset
allocation (G7.4, with its new step 1a) and the form allocation keeping
their counts, and meets the censuses with every pass reading each rank on
its own clock; the validator places each cell by its instant and counts it
as written. Each clause below is red on its mutant (`_red_on`).

S1 the scope, S2 the ranking, S3 the censuses met, S4 the recount, S5 item
(a), S6 item (b), S7 the forms, S8 the work, S9 every description loads,
and the twenty-fourth vectors file, each case red on its mutant. The
landing's Codex review added three columns to S3, each red on its mutant:
a fixed block two keys share, bare dates in the frame's days, and a leap
second beside Z and +00:00.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import random
import typing

import pytest

import kpi_shapes
import shared_clock_shapes
from synthtwin import calendar_clock, calendar_rules, generation, parsing, rendering, taxonomy, validation

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-24.json"
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))

ROWS = 1000
FLOORS = (11, 36)
SEEDS = (0, 1, 2)
# The battery's columns the censuses are met on (S3): two offsets across both
# changes of daylight saving time, two sites, a -06:00 clinic with one cell in
# fifty at +05:30, an instrument writing Z beside a ward at +02:00, sixtieth
# seconds at +05:30, and three columns of the joint member; and, from the
# landing's Codex review, a fixed block two keys share (item 1), bare dates
# beside -03:00 midnight stamps all on the 15th, the all-midnight DM5 case (item 2),
# and a leap second beside Z and +00:00 (item 3).
MET = (
    "dst_clinic", "dst_ed", "two_sites", "few_off", "z_plus", "leap_shared",
    "isomix_admit", "isomix_offsets", "clinic_isomix",
    "split_block", "midnight_dates", "leap_noon",
)

_DESCRIBED: "dict[tuple[str, int], kpi_shapes.Described]" = {}


def _described(tmp_path_factory: pytest.TempPathFactory, name: str, floor: int, rows: int = ROWS) -> kpi_shapes.Described:
    """One column of the battery, described at a floor (kept for the module)."""
    key = (f"{name}-{rows}", floor)
    if key not in _DESCRIBED:
        cells = shared_clock_shapes.build(name, rows)
        text = "t\n" + "".join(f"{cell}\n" for cell in cells)
        _DESCRIBED[key] = kpi_shapes.describe(tmp_path_factory.mktemp(name), name, text, floor)
    return _DESCRIBED[key]


def _missed(described: kpi_shapes.Described, seed: int) -> "list[str]":
    return kpi_shapes.missed(kpi_shapes.measure(described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))


def _checks(described: kpi_shapes.Described, text: str, name: str) -> "dict[str, validation.Check]":
    outcome = kpi_shapes.measure(described, text, name)
    return {check.subcheck: check for check in outcome.checks}


# -- S1: the scope ---------------------------------------------------------


@pytest.mark.parametrize("name", ("two_sites", "dst_ed", "isomix_admit"))
def test_s1_a_column_of_two_offsets_or_of_the_joint_member_publishes_its_censuses(
    tmp_path_factory: pytest.TempPathFactory, name: str
) -> None:
    """The weekday and hour censuses stand on the shared clock and in the joint member at both
    floors, and the loader reads them (`kpi_shapes.describe` loads every description)."""
    for floor in FLOORS:
        block = _described(tmp_path_factory, name, floor).block("t")
        assert block["weekday_census"] and block["hour_census"], (name, floor)


def test_s1_red_with_the_clock_and_the_member_clauses_restored(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: the producer's scope asks the local clock and no joint member again."""
    days, hours = taxonomy._census_days, taxonomy._census_hours

    def local_days(details: "dict[str, object]", pairs: "list[tuple[str, str]]", ranked: "list[int] | None" = None) -> "tuple[int, ...]":
        if taxonomy._on_own_clocks(details):
            return ()
        return days(details, pairs, ranked)

    def local_hours(details: "dict[str, object]", pairs: "list[tuple[str, str]]", ranked: "list[int] | None" = None) -> "tuple[int, ...]":
        if taxonomy._on_own_clocks(details):
            return ()
        return hours(details, pairs, ranked)

    monkeypatch.setattr(taxonomy, "_census_days", local_days)
    monkeypatch.setattr(taxonomy, "_census_hours", local_hours)
    for name in ("two_sites", "isomix_admit"):
        cells = shared_clock_shapes.build(name, ROWS)
        block = kpi_shapes.describe(tmp_path / name, name, "t\n" + "".join(f"{cell}\n" for cell in cells), 11).block("t")
        assert block["weekday_census"] == [] and block["hour_census"] == [], name


def test_s1_the_one_predicate() -> None:
    """`calendar_rules.census_scope` asks the resolution and the midnight flag alone."""
    assert calendar_rules.census_scope(calendar_rules.SCOPE_DAYS, "datetime", False)
    assert calendar_rules.census_scope(calendar_rules.SCOPE_DAYS, "date", None)
    assert not calendar_rules.census_scope(calendar_rules.SCOPE_DAYS, "month", None)
    assert calendar_rules.census_scope(calendar_rules.SCOPE_MONTH_DAYS, "datetime", True)
    assert not calendar_rules.census_scope(calendar_rules.SCOPE_MONTH_DAYS, "datetime", False)
    assert calendar_rules.census_scope(calendar_rules.SCOPE_CLOCK, "datetime", False)
    assert not calendar_rules.census_scope(calendar_rules.SCOPE_CLOCK, "datetime", True)
    assert not calendar_rules.census_scope(calendar_rules.SCOPE_CLOCK, "date", None)


# -- S2: ranked by the instant, counted by the text -------------------------

_SHARED = {"resolution": "datetime", "datetimes_read_at": "utc", "format": "iso-datetime", "all_at_midnight": False}
# One instant, 2024-03-03 23:30 on the shared clock, written at +05:30 and at
# Z, and a later one written at -06:00 on the day before its instant's.
_PAIRS = [
    ("2024-03-03 20:00:00", "-06:00"),
    ("2024-03-03 23:30:00", "Z"),
    ("2024-03-04 05:00:00", "+05:30"),
]


def test_s2_cells_are_ranked_by_their_instant_and_counted_where_written() -> None:
    """Two cells of one instant under two offsets rank by `ordered_moments`' tie rule (the
    published text, then the offset: `+05:30` before `Z`), and a later instant written on an
    earlier day ranks after them; each counts at the day and hour its own text writes."""
    assert taxonomy._census_ranked(_SHARED, _PAIRS) == [2, 1, 0]
    assert taxonomy._census_hours(_SHARED, _PAIRS) == (5, 23, 20)
    day = parsing.days_from_civil
    assert taxonomy._census_days(_SHARED, _PAIRS) == (day(2024, 3, 4), day(2024, 3, 3), day(2024, 3, 3))
    placed = taxonomy.ordered_moments(_PAIRS, taxonomy.READ_AT_UTC)[0]
    assert placed == ["2024-03-03 23:30:00", "2024-03-03 23:30:00", "2024-03-04 02:00:00"]


def test_s2_a_sixtieth_second_counts_where_it_is_written() -> None:
    """`2016-12-31 23:59:60` written at +05:30 counts on 31 December at hour 23, its instant
    the next minute's first second."""
    pairs = [("2016-12-31 23:59:60", "+05:30"), ("2017-01-01 10:00:00", "-06:00")]
    assert taxonomy._census_hours(_SHARED, pairs) == (23, 10)
    assert taxonomy._census_days(_SHARED, pairs)[0] == parsing.days_from_civil(2016, 12, 31)


def test_s2_red_ranked_by_the_written_text(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: the cells ranked by their written text, as on one clock -- the -06:00 cell,
    whose instant is the latest, ranks first and the body the tails cut holds another hour."""
    monkeypatch.setattr(
        taxonomy, "_census_ranked",
        lambda _details, pairs: sorted(range(len(pairs)), key=lambda place: pairs[place][0]),
    )
    assert taxonomy._census_hours(_SHARED, _PAIRS) != (5, 23, 20)


# -- S3: the censuses met, every offset and form kept ----------------------


@pytest.mark.parametrize("name", MET)
def test_s3_every_census_is_met_and_every_offset_and_form_kept(
    tmp_path_factory: pytest.TempPathFactory, name: str
) -> None:
    """At 1,000 rows, floors 11 and 36, seeds 0 to 2, every twin of the column meets every
    published census on its own clock and misses no check: its offsets and its forms are held
    exactly (`utc_offsets`, `resolution_mix` on the joint member) and its count of different
    values where it is exact."""
    for floor in FLOORS:
        described = _described(tmp_path_factory, name, floor)
        for seed in SEEDS:
            assert _missed(described, seed) == [], (name, floor, seed)


def test_s3_minute_and_second_heaps_on_the_shared_clock_are_met(tmp_path_factory: pytest.TempPathFactory) -> None:
    """THE MINUTE AND THE SECOND ON THE SHARED CLOCK (landing 3b.7's MC3/SE3 widening, re-applied
    at batch 3b's merge of lane J2, plan P4-D378): two sites at -06:00 and +05:30, about a third
    of the cells on minute 0 and half on second 0 of their own clocks, publish both heaps, each
    counted where its cell is written, and at floors 11 and 36, seeds 0 to 2, every twin meets
    them and misses no check. Before the widening, T3's scope (the local clock only) published
    neither."""
    for floor in FLOORS:
        described = _described(tmp_path_factory, "heaped_fields", floor)
        block = described.block("t")
        assert block["datetimes_read_at"] == "utc"
        assert [heap["value"] for heap in block["minute_heaps"]] == [0], floor
        assert [heap["value"] for heap in block["second_heaps"]] == [0], floor
        for seed in SEEDS:
            assert _missed(described, seed) == [], (floor, seed)


def test_s3_minute_and_second_heaps_red_without_the_frame(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: the passes read every rank on the shared clock (no frame) -- the twins of the
    heaped two-site column miss the minute's heap."""
    monkeypatch.setattr(generation, "_own_clock_frame", lambda *_arguments: None)
    described = _described(tmp_path_factory, "heaped_fields", 11)
    assert "t:minute_heaps.counts" in _missed(described, 0)


def test_s3_minute_and_second_heaps_red_without_the_field_pass(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: G7.3h moves no rank -- the heaps the drawing rule leaves are missed."""
    monkeypatch.setattr(
        generation, "_clock_fields_settled", lambda _column, _facts, ordinals, *_rest, **_named: (ordinals, [])
    )
    described = _described(tmp_path_factory, "heaped_fields", 36)
    missed = _missed(described, 0)
    assert "t:minute_heaps.counts" in missed and "t:second_heaps.counts" in missed


def test_s3_red_without_the_frame(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: the passes read every rank on the shared clock (no frame) -- the two-site
    column's twins miss their censuses."""
    monkeypatch.setattr(generation, "_own_clock_frame", lambda *_arguments: None)
    described = _described(tmp_path_factory, "two_sites", 11)
    assert any(check.endswith("_census.groups") for check in _missed(described, 0))


def test_s3_red_with_the_whole_guard_restored(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: the day and hour passes stop at the first bare date, as before the landing --
    the joint member's twins miss their censuses."""
    day, hour = generation._day_settled, generation._hour_settled

    def guarded(settled: "typing.Callable[..., tuple[list[int], list[generation.Deviation]]]") -> "typing.Callable[..., tuple[list[int], list[generation.Deviation]]]":
        def run(*arguments: object, **named: object) -> "tuple[list[int], list[generation.Deviation]]":
            if any(typing.cast("list[bool]", arguments[4])):
                return typing.cast("list[int]", arguments[2]), []
            return settled(*arguments, **named)
        return run

    monkeypatch.setattr(generation, "_day_settled", guarded(day))
    monkeypatch.setattr(generation, "_hour_settled", guarded(hour))
    described = _described(tmp_path_factory, "isomix_admit", 11)
    assert any(check.endswith("_census.groups") for check in _missed(described, 0))


# -- S3, from the landing's Codex review: each item red on its mutant ----------


def test_s3_red_with_one_key_a_block(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 1. Mutant: G7.4 step 1a never splits a fixed block -- the 251 ranks two rungs
    fix at 2024-07-19 09:00 on the shared clock all take +01:00, writing them in hour 10, which
    holds 150, and the twin misses its hour census (132, 251, 297, 298 for 150, 150, 339, 339)."""
    monkeypatch.setattr(generation, "_pinned_split", lambda *_arguments: [])
    for floor in FLOORS:
        missed = _missed(_described(tmp_path_factory, "split_block", floor), 0)
        assert "t:hour_census.groups" in missed, (floor, missed)


def test_s3_red_with_the_bare_dates_frozen_in_days(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 2. Mutant: the passes pin a bare date by the column's own facts on the shared
    clock even in the frame's days -- the bare dates stay where the form step put them, and the
    twin writes about 620 cells off the 15th the day of the month's census counts nought."""
    pinned = generation._whole_pinned

    def frozen(column: object, whole: "list[bool]", flags: "list[bool]", _read: object = None) -> None:
        pinned(column, whole, flags)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_whole_pinned", frozen)
    for floor in FLOORS:
        missed = _missed(_described(tmp_path_factory, "midnight_dates", floor), 0)
        assert "t:day_of_month_census.groups" in missed, (floor, missed)


def test_s3_red_without_the_sixtieth_spelling(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 3. Mutant: no fixed block is written at a sixtieth second -- the 251 ranks
    two rungs fix at the instant of 2016-12-31T23:59:60Z, published as midnight, come back at
    00:00:00 on the Sunday, and the twin misses its hour and weekday censuses."""
    offsets = generation._pinned_offsets
    monkeypatch.setattr(
        generation, "_pinned_offsets",
        lambda facts, layout, parsed, whole, _sixtieths=None: offsets(facts, layout, parsed, whole),
    )
    for floor in FLOORS:
        missed = _missed(_described(tmp_path_factory, "leap_noon", floor), 0)
        assert "t:hour_census.groups" in missed and "t:weekday_census.groups" in missed, (floor, missed)


def test_s3_the_leap_block_is_written_at_sixty(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Codex's item 3, the cells: the twin writes the fixed block at the sixtieth second the source
    wrote, 251 cells `2016-12-31T23:59:60` at an offset of nought, and none at midnight."""
    for floor in FLOORS:
        text = kpi_shapes.twin_text(_described(tmp_path_factory, "leap_noon", floor), 0)
        cells = text.splitlines()[1:]
        assert sum(1 for cell in cells if cell.startswith("2016-12-31T23:59:60")) >= 251, floor
        assert not any("T00:00:00" in cell for cell in cells), floor


# -- S4: the recount on each cell's own clock --------------------------------


def test_s4_the_source_holds_its_censuses_and_red_counted_on_the_shared_clock(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The unchanged source of the two-site column holds its weekday and hour censuses; with
    the recount reading each cell's conversion to the shared clock (the mutant), it misses."""
    described = _described(tmp_path_factory, "two_sites", 11)
    source = described.table.read_text(encoding="utf-8")
    held = _checks(described, source, "source.csv")
    assert held["weekday_census.groups"].verdict == validation.HELD
    assert held["hour_census.groups"].verdict == validation.HELD
    readings = validation._tail_readings_of

    def converted(facts: object, cells: "list[str]", folded: bool = False, written: bool = False) -> "list[tuple[int, str] | None]":
        return readings(typing.cast("validation.contract.DatetimeFacts", facts), cells, folded, False)

    monkeypatch.setattr(validation, "_tail_readings_of", converted)
    mutant = _checks(described, source, "mutant.csv")
    assert validation.MISSED in (mutant["weekday_census.groups"].verdict, mutant["hour_census.groups"].verdict)


# -- S5: item (a), a listed tail off a withheld midnight ----------------------


@pytest.mark.parametrize("name", ("c0", "c551"))
def test_s5_a_withheld_count_at_midnight_is_kept(tmp_path_factory: pytest.TempPathFactory, name: str) -> None:
    """C1's two columns, whose listed low tails stood at a midnight of the first sorted key, hold
    their count at midnight (withheld for its size) at seeds 0 to 2 at the floor of 11, and miss
    nothing (item (a): 4 twins of 4 missed it before the landing)."""
    described = _described(tmp_path_factory, name, 11)
    assert described.block("t")["n_at_midnight"] is None
    for seed in SEEDS:
        assert _missed(described, seed) == [], (name, seed)


def test_s5_red_without_the_pinned_offsets(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: G7.4 step 1a off -- the listed tails take the first sorted key again."""
    monkeypatch.setattr(generation, "_pinned_offsets", lambda *_arguments: {})
    missed = _missed(_described(tmp_path_factory, "c551", 11), 0)
    assert any(check.endswith(":midnight.withheld") for check in missed), missed


# -- The repair's item 4: each new rule at its use site, end to end -----------


def test_s3_the_spread_meets_few_off_hour_census_at_ten_thousand_rows(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """G7.4 step 2 on the shared clock spreads the keys gap by gap (beyond the design): `few_off`
    at 10,000 rows, floor 11, seed 0, meets its hour census; red with the spread off at its call
    (the 196 `+05:30` cells in one block on the body's first ranks missed it at every seed)."""
    described = _described(tmp_path_factory, "few_off", 11, 10000)
    assert described.block("t")["hour_census"]
    held = _checks(described, kpi_shapes.twin_text(described, 0), "f.csv")["hour_census.groups"]
    assert held.verdict == validation.HELD
    allocation = generation._offset_allocation

    def unspread(*arguments: object) -> "tuple[list[str], list[generation.Deviation]]":
        given = list(arguments)
        given[6] = False
        return allocation(*given)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_offset_allocation", unspread)
    missed = _checks(described, kpi_shapes.twin_text(described, 0), "m.csv")["hour_census.groups"]
    assert missed.verdict == validation.MISSED


def test_s7_the_body_holds_no_more_bare_dates_than_hour_zero(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """100 bare dates beside 299 noon stamps and one at midnight publish hour 0 at 94, fewer
    than the dates: the twins at seeds 0 to 2 meet the hour census; red with the cap at hour 0
    off in `_clocked_forms`."""
    described = _described(tmp_path_factory, "noon_dates", 11, 400)
    assert described.block("t")["hour_census"]
    for seed in SEEDS:
        held = _checks(described, kpi_shapes.twin_text(described, seed), f"n{seed}.csv")["hour_census.groups"]
        assert held.verdict == validation.HELD, seed
    flags = generation._clocked_form_flags
    monkeypatch.setattr(
        generation, "_clocked_form_flags",
        lambda gaps, dates, moments, apart, _cap=None: flags(gaps, dates, moments, apart, None),
    )
    missed = _checks(described, kpi_shapes.twin_text(described, 0), "m.csv")["hour_census.groups"]
    assert missed.verdict == validation.MISSED


def _joins(cells: "list[str]", groups: "list[dict[str, int]]") -> "list[dict[str, int]]":
    """The published hour groups joining an hour no cell is written at to one some cell is."""
    written = {int(cell[11:13]) for cell in cells if len(cell) >= 13}
    return [
        group for group in groups
        if group["first"] < group["last"]
        and len({hour in written for hour in range(group["first"], group["last"] + 1)}) > 1
    ]


def test_s4_no_hour_group_joins_an_hour_never_written(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Blocker 1's producer half: on the shared clock the hour census's sure cells are rule 4's
    alone, so `dst_clinic` at 1,000 rows publishes no group joining an hour the source never
    writes to an hour it does, at either floor; red with the producer reading the sure cells
    as the local clock does (the design skeptic measured 5 such joins)."""
    cells = shared_clock_shapes.build("dst_clinic", ROWS)
    text = "t\n" + "".join(f"{cell}\n" for cell in cells)
    for floor in FLOORS:
        groups = kpi_shapes.describe(tmp_path / f"h{floor}", "c", text, floor).block("t")["hour_census"]
        assert groups and _joins(cells, groups) == [], floor
    sure = calendar_clock.own_clock_sure
    monkeypatch.setattr(
        calendar_clock, "own_clock_sure",
        lambda published, tails, _reading: sure(published, tails, "local"),
    )
    joined = [
        _joins(cells, kpi_shapes.describe(tmp_path / f"m{floor}", "c", text, floor).block("t")["hour_census"])
        for floor in FLOORS
    ]
    assert joined != [[], []]


# -- S6: item (b), an all-different joint column ------------------------------


def _different(text: str) -> int:
    return len(set(text.split("\n")[1:]) - {""})


def _shortfall_said(described: kpi_shapes.Described, seed: int) -> "tuple[int, list[str]]":
    """The twin's count of different values and the remarks its report makes of that count."""
    twin = generation.generate(described.loaded, seed)
    text = rendering.twin_csv(twin)
    said = [remark.held for remark in twin.remarks if remark.subject == "how many of these values are different"]
    return _different(text), said


@pytest.mark.parametrize(("name", "rows", "seeds"), (
    ("isomix_alldiff", ROWS, SEEDS), ("isomix_alldiff", 10000, (0,)), ("isomix_alldiff_b", 10000, (0,)),
))
def test_s6_an_all_different_joint_column_comes_back_all_different(
    tmp_path_factory: pytest.TempPathFactory, name: str, rows: int, seeds: "tuple[int, ...]"
) -> None:
    """Item (b), as the construction reaches it: every value of the twin different -- 1,000 of
    1,000 at seeds 0 to 2 and 10,000 of 10,000, where 973 to 992 of 1,000 came back before the
    landing (99,997 to 100,000 of 100,000 measured at the repair, said where short) -- the count
    held to G12.5's envelope, as the base holds it (the repair's item 1: the contract's one
    statement of reach is the only statement of exactness), and the report saying nothing of it."""
    described = _described(tmp_path_factory, name, 11, rows)
    assert described.block("t")["n_distinct"] == rows
    for seed in seeds:
        different, said = _shortfall_said(described, seed)
        assert (different, said) == (rows, []), (name, rows, seed)
        held = _checks(described, kpi_shapes.twin_text(described, seed), f"b{seed}.csv")["distinct.n_distinct"]
        assert held.verdict != validation.MISSED, (name, rows, seed)


def test_s6_red_without_the_cap(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: the bare dates spent with no cap per gap, as the rotation alone spends them --
    the tight column comes back shorter than the cap leaves it (999 of 1,000)."""
    described = _described(tmp_path_factory, "isomix_alldiff_b", 11)
    capped = _different(kpi_shapes.twin_text(described, 0))
    flags = generation._clocked_form_flags
    monkeypatch.setattr(
        generation, "_clocked_form_flags",
        lambda gaps, dates, moments, _apart, cap=None: flags(gaps, dates, moments, False, cap),
    )
    assert _different(kpi_shapes.twin_text(described, 0)) < capped


def test_s6_the_tight_column_keeps_its_forms_and_says_its_shortfall(tmp_path_factory: pytest.TempPathFactory) -> None:
    """The repair's item 2: the tight column (a bare date on every day of its span) writes all
    200 of its bare dates -- the ones its gaps have no free midnight day for on a day another
    value holds -- so it misses nothing at either floor (`resolution_mix`, `n_at_midnight` and
    every offset held), where 196 of 200 were written as moments and two checks were MISSED;
    its count of different values falls inside G12.5's envelope, 998 or 999 of 1,000, and the
    twin's report says so (`generation._joint_count_remarks`)."""
    for floor in FLOORS:
        described = _described(tmp_path_factory, "isomix_alldiff_b", floor)
        text = kpi_shapes.twin_text(described, 0)
        checks = _checks(described, text, f"t{floor}.csv")
        assert [name for name, check in checks.items() if check.verdict == validation.MISSED] == [], floor
        assert checks["resolution_mix.counts"].verdict == validation.HELD
        different, said = _shortfall_said(described, 0)
        assert different < ROWS and said == [f"{different} different values of {ROWS}, where every value of the real column was different"]


def test_s6_the_tight_column_red_with_its_leftover_dates_written_as_moments(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: a bare date the free days cannot place is written as a moment, as before the
    repair -- `resolution_mix` is MISSED."""
    described = _described(tmp_path_factory, "isomix_alldiff_b", 11)
    flags = generation._clocked_form_flags

    def no_leftover(gaps: "tuple[list[int], list[int]]", dates: int, moments: int, apart: bool, cap: "tuple[int, int, int] | None" = None) -> "list[bool]":
        whole = flags(gaps, dates, moments, apart, cap)
        lows, highs = gaps
        room: "dict[tuple[int, int], int]" = {}
        held = {lows[rank] // 86400 for rank in range(len(lows)) if lows[rank] == highs[rank] and lows[rank] % 86400 == 0}
        for rank in range(len(whole)):
            if not whole[rank] or lows[rank] == highs[rank]:
                continue
            spot = (lows[rank], highs[rank])
            if spot not in room:
                first, last = generation._midnight_room(spot[0], spot[1])
                room[spot] = max(0, last - first + 1) - len([day for day in held if first <= day <= last])
            if room[spot] <= 0:
                whole[rank] = False
                continue
            room[spot] = room[spot] - 1
        return whole

    monkeypatch.setattr(generation, "_clocked_form_flags", no_leftover)
    checks = _checks(described, kpi_shapes.twin_text(described, 0), "m.csv")
    assert checks["resolution_mix.counts"].verdict == validation.MISSED


# The repair's second skeptic, item 1: where hour 0's group caps the body and the twin's tails
# hold fewer midnight days than the source's tails held bare dates, the leftover pass stops at the cap:
# the hour census holds and `resolution_mix` gives way, named in the twin's report.
_ENDS = 400


@pytest.mark.parametrize("floor", FLOORS)
def test_s6_the_cap_at_hour_zero_holds_against_the_leftover_dates(tmp_path_factory: pytest.TempPathFactory, floor: int) -> None:
    """`noon_ends` at 400 rows: the body holds as many bare dates as hour 0's group counts (83
    at the floor of 11) and the twin's tails take 15 of the source's 17, so 98 (97 at the floor
    of 36) of 100 bare dates are written; `hour_census.groups` is HELD, `resolution_mix.counts`
    is the one check MISSED, and the twin names it."""
    described = _described(tmp_path_factory, "noon_ends", floor, _ENDS)
    twin = generation.generate(described.loaded, 0)
    text = rendering.twin_csv(twin)
    checks = _checks(described, text, f"e{floor}.csv")
    assert checks["hour_census.groups"].verdict == validation.HELD
    assert [name for name, check in checks.items() if check.verdict == validation.MISSED] == ["resolution_mix.counts"]
    assert "resolution_mix" in {deviation.fact for deviation in twin.deviations}


def _leftover_without_the_cap(flags: typing.Callable[..., "list[bool]"]) -> typing.Callable[..., "list[bool]"]:
    """The mutant `leftover_nocap`: the bare dates the capped passes leave over written on the first
    unsettled ranks whose gap holds a midnight, the body's cap at hour 0 ignored."""

    def mutant(gaps: "tuple[list[int], list[int]]", dates: int, moments: int, apart: bool, cap: "tuple[int, int, int] | None" = None) -> "list[bool]":
        whole = flags(gaps, dates, moments, apart, cap)
        lows, highs = gaps
        left = dates - len([rank for rank in range(len(whole)) if whole[rank]])
        for rank in range(len(whole)):
            if left <= 0:
                break
            first, last = generation._midnight_room(lows[rank], highs[rank])
            if whole[rank] or lows[rank] == highs[rank] or first > last:
                continue
            whole[rank] = True
            left = left - 1
        return whole

    return mutant


def test_s6_the_cap_at_hour_zero_red_with_the_leftover_dates_past_it(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: the leftover pass ignores the cap -- every bare date is written and hour 0's group
    takes 85 for 83 (62 for 59 at the floor of 36): `hour_census.groups` is MISSED."""
    monkeypatch.setattr(generation, "_clocked_form_flags", _leftover_without_the_cap(generation._clocked_form_flags))
    for floor in FLOORS:
        described = _described(tmp_path_factory, "noon_ends", floor, _ENDS)
        checks = _checks(described, kpi_shapes.twin_text(described, 0), f"m{floor}.csv")
        assert checks["hour_census.groups"].verdict == validation.MISSED, floor


@pytest.mark.xfail(strict=True, reason=(
    "the repair's second skeptic, item 1, measured: `noon_ends` -- bare dates on the first and "
    "last eighth of a span of noon stamps, every value different -- writes 98 of 100 bare dates at "
    "400 rows (97 at the floor of 36), 248 of 250 at 1,000, 2,498 of 2,500 at 10,000: hour 0's "
    "group caps the body at 83 and the twin's tails, their extremes drawn off midnight, hold 15 of "
    "the source's 17, so `resolution_mix` gives way, named; with the cap off the hour census "
    "misses instead"
))
@pytest.mark.parametrize("floor", FLOORS)
def test_s6_the_cap_at_hour_zero_writes_every_bare_date(tmp_path_factory: pytest.TempPathFactory, floor: int) -> None:
    described = _described(tmp_path_factory, "noon_ends", floor, _ENDS)
    checks = _checks(described, kpi_shapes.twin_text(described, 0), f"x{floor}.csv")
    assert checks["resolution_mix.counts"].verdict == validation.HELD


@pytest.mark.xfail(strict=True, reason=(
    "the repair's item 1, measured: stamps on consecutive minutes beside bare dates, every value "
    "different, come back 778 to 805 of 1,000 -- method G7.3's count pass never runs on a clocked "
    "column of the joint member (`contract.datetime_counts_reachable` refuses a bare date beside "
    "moments), so moments drawn in dense gaps meet at minute precision; the count stays in "
    "G12.5's envelope and the twin's report says the shortfall"
))
def test_s6_moments_on_consecutive_minutes_come_back_all_different(tmp_path_factory: pytest.TempPathFactory) -> None:
    described = _described(tmp_path_factory, "sparse_local", 11)
    assert _different(kpi_shapes.twin_text(described, 0)) == ROWS


def test_s6_moments_on_consecutive_minutes_stay_in_the_envelope_and_are_said(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 1: `sparse_local`'s twins are WITHIN-BOUND, never MISSED, and the report says the
    count; red with a second statement of exactness for the joint member (the mutant: every
    joint column's count held exactly), as the landing had it."""
    described = _described(tmp_path_factory, "sparse_local", 11)
    text = kpi_shapes.twin_text(described, 0)
    assert _checks(described, text, "s.csv")["distinct.n_distinct"].verdict == validation.WITHIN_BOUND
    different, said = _shortfall_said(described, 0)
    assert different < ROWS and len(said) == 1
    exact = validation.contract.datetime_count_exact
    monkeypatch.setattr(
        validation.contract, "datetime_count_exact",
        lambda column, published: True if column.name == "t" else exact(column, published),
    )
    assert _checks(described, text, "e.csv")["distinct.n_distinct"].verdict == validation.MISSED


def test_s6_the_shared_clock_keeps_its_envelope(tmp_path_factory: pytest.TempPathFactory) -> None:
    """The skeptic's major 3: all-different hourly stamps over +01:00 and +02:00 stay inside
    G12.5's envelope, never EXACT, on the shared clock."""
    described = _described(tmp_path_factory, "consec_hours_off", 11)
    checks = _checks(described, kpi_shapes.twin_text(described, 0), "h.csv")
    assert checks["distinct.n_distinct"].verdict != validation.MISSED


# -- S7: the forms written as published ---------------------------------------


@pytest.mark.parametrize("name", ("isomix_admit", "clinic_isomix"))
def test_s7_the_bare_dates_are_written_as_published(tmp_path_factory: pytest.TempPathFactory, name: str) -> None:
    """`resolution_mix` is EXACT on the joint member, and HELD: the twin writes the published
    count of bare dates, where it wrote none before the landing."""
    described = _described(tmp_path_factory, name, 11)
    checks = _checks(described, kpi_shapes.twin_text(described, 0), "f.csv")
    assert checks["resolution_mix.counts"].verdict == validation.HELD
    assert checks["format.member"].verdict == validation.HELD


def test_s7_red_without_the_form_step(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: no rank of a clocked column of the joint member is a bare date."""
    monkeypatch.setattr(generation, "_clocked_forms", lambda facts, layout, _distinct: [False] * layout.parsed)
    described = _described(tmp_path_factory, "isomix_admit", 11)
    checks = _checks(described, kpi_shapes.twin_text(described, 0), "m.csv")
    assert checks["resolution_mix.counts"].verdict == validation.MISSED


# -- S8: the work -------------------------------------------------------------


def _form_input(rows: int) -> "tuple[list[int], tuple[list[int], list[int]], list[bool]]":
    """Gaps of 1,000 ranks over thirty days each, a fifth of the ranks bare dates."""
    ordinals: "list[int]" = []
    lows: "list[int]" = []
    highs: "list[int]" = []
    whole: "list[bool]" = []
    for rank in range(rows):
        gap = rank // 1000
        low = gap * 30 * 86400 + 3600
        high = low + 29 * 86400
        ordinals += [low + (rank % 1000) * 2500]
        lows += [low]
        highs += [high]
        whole += [rank % 5 == 0]
    return ordinals, (lows, highs), whole


@pytest.mark.parametrize("rows", (10000, 100000, 1000000))
def test_s8_the_form_step_asks_each_day_a_bounded_number_of_times(monkeypatch: pytest.MonkeyPatch, rows: int) -> None:
    """The form step asks whether a day is shut at most a fixed number of times a rank, up to
    1,000,000 rows: no day stored, no walk begun again per rank."""
    asked = [0]
    shut = generation._form_day_shut

    def counted(day: int, closed: "tuple[frozenset[int], frozenset[int]]") -> bool:
        asked[0] = asked[0] + 1
        return shut(day, closed)

    monkeypatch.setattr(generation, "_form_day_shut", counted)
    ordinals, gaps, whole = _form_input(rows)
    generation._form_step_days(ordinals, gaps, whole, True, (frozenset({5, 6}), frozenset()))
    assert asked[0] <= 16 * rows, (rows, asked[0])


def test_s8_the_frame_is_taken_back_once_a_rank(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every body rank is matched in one run, once: the runs' sizes add up to at most the body."""
    spans: "list[int]" = []
    run = generation._own_clock_run

    def counted(*arguments: object) -> None:
        first, end = typing.cast("tuple[int, int]", arguments[5])
        spans.append(end - first)
        run(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_own_clock_run", counted)
    rows = 200000
    before = [rank * 60 for rank in range(rows)]
    shifts = [3600 if rank % 2 else 7200 for rank in range(rows)]
    offsets = ["+01:00" if rank % 2 else "+02:00" for rank in range(rows)]
    pinned = [rank % 1000 == 0 for rank in range(rows)]
    lows = [(rank // 1000) * 60000 for rank in range(rows)]
    highs = [(rank // 1000) * 60000 + 59999 for rank in range(rows)]
    framed = [before[rank] + shifts[rank] for rank in range(rows)]
    generation._off_own_clocks(before, framed, shifts, offsets, [False] * rows, pinned, (0, rows - 1), (lows, highs), 1)
    assert sum(spans) <= rows and len(spans) <= rows // 1000 + 1


def _gaps_counted(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch, through: bool
) -> "list[int]":
    """How many gaps each pass on the joint admissions column moves its ranks in."""
    found: "list[int]" = []
    gaps = generation._weekday_gaps

    def counted(state: "generation._WeekdayPass", low: int, high: int, pinned: "list[bool]") -> "list[list[int]]":
        if not through and state.see_through:
            state = generation.dataclasses.replace(state, see_through=frozenset())
        made = gaps(state, low, high, pinned)
        found.append(len(made))
        return made

    monkeypatch.setattr(generation, "_weekday_gaps", counted)
    kpi_shapes.twin_text(_described(tmp_path_factory, "isomix_admit", 11), 0)
    return found


def test_s8_a_gap_runs_across_its_bare_dates(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The passes move a joint column's ranks in its rung gaps, a gap running across the bare
    dates pinned inside it; cut at each, about one gap a bare date, G7.3f's shares, asked once a
    gap over the gap's span, took 39 of 77 seconds at 100,000 rows (the mutant)."""
    with monkeypatch.context() as patch:
        through = _gaps_counted(tmp_path_factory, patch, True)
    cut = _gaps_counted(tmp_path_factory, monkeypatch, False)
    assert through and max(through) <= 40, through
    assert max(cut) > 4 * max(through), (cut, through)


def test_s8_one_ranking_a_column(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The ranking is computed once a column and handed to every census (the skeptic's minor 7)."""
    calls = [0]
    ranked = taxonomy._census_ranked

    def counted(
        details: "dict[str, object]", pairs: "list[tuple[str, str]]", instants: "list[int] | None" = None
    ) -> "list[int] | None":
        calls[0] = calls[0] + 1
        return ranked(details, pairs, instants)

    monkeypatch.setattr(taxonomy, "_census_ranked", counted)
    cells = shared_clock_shapes.build("two_sites", ROWS)
    kpi_shapes.describe(tmp_path, "one", "t\n" + "".join(f"{cell}\n" for cell in cells), 11)
    assert calls[0] == 1


@pytest.mark.parametrize("name", ("dst_ed", "two_sites", "isomix_admit"))
def test_s8_one_instant_key_a_pair(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str) -> None:
    """The censuses compute at most one instant key a pair, n a column (the design skeptic's
    minor 7; the repair's item 5): the ranking fills the instants the census of moments reads,
    and spells the shared clock's text from the key. Three keys a pair before the repair --
    `parsing.instant_key` ran 1,000,002 times in one describe of 200,000 pairs."""
    inside = [0]
    calls = [0]
    key = parsing.instant_key

    def counted_key(canonical: str, offset: str) -> "int | None":
        if inside[0] > 0:
            calls[0] = calls[0] + 1
        return key(canonical, offset)

    def entered(census: "typing.Callable[..., typing.Any]") -> "typing.Callable[..., typing.Any]":
        def run(*arguments: object, **named: object) -> object:
            inside[0] = inside[0] + 1
            try:
                return census(*arguments, **named)
            finally:
                inside[0] = inside[0] - 1
        return run

    monkeypatch.setattr(parsing, "instant_key", counted_key)
    for census in ("_census_ranked", "_census_moments", "_census_days", "_census_hours"):
        monkeypatch.setattr(taxonomy, census, entered(getattr(taxonomy, census)))
    cells = shared_clock_shapes.build(name, ROWS)
    block = kpi_shapes.describe(tmp_path, name, "t\n" + "".join(f"{cell}\n" for cell in cells), 11).block("t")
    assert block["hour_census"], name
    assert 0 < calls[0] <= ROWS, (name, calls[0])


def test_s8_the_shared_clock_text_spelled_from_the_key() -> None:
    """`taxonomy._utc_text_of` is `parsing.utc_moment` from a key already computed, the clamp at
    the calendar's two edges `parsing.utc_moment`'s own."""
    for canonical in ("2024-03-10 02:30:00", "2024-02-29", "0001-01-01 00:30:00", "0001-01-01", "9999-12-31 23:30:00", "9999-12-31", "2016-12-31 23:59:60"):
        for offset in ("", "Z", "+05:30", "-06:00", "+14:00", "-12:00"):
            instant = parsing.instant_key(canonical, offset)
            assert instant is not None
            assert taxonomy._utc_text_of(canonical, instant, offset) == parsing.utc_moment(canonical, offset), (canonical, offset)


# -- S9: every description loads ------------------------------------------------


@pytest.mark.parametrize("name", sorted(shared_clock_shapes.SHAPES))
def test_s9_the_producer_always_loads(tmp_path_factory: pytest.TempPathFactory, name: str) -> None:
    """Every column of the battery, at both floors, is described and loaded (`kpi_shapes.describe`
    loads what it writes): the widened scope adds no refusal the producer can trip."""
    for floor in FLOORS:
        assert _described(tmp_path_factory, name, floor).loaded.columns


# -- The twenty-fourth vectors file, each case red on its mutant -----------------


def _field(case: "dict[str, typing.Any]", shift: "typing.Callable[[str], int]") -> "dict[str, int]":
    local = case["instant"] + shift(case["key"]) - (1 if case["sixtieth"] else 0)
    return {rule: generation._census_bin_of(rule, local) for rule in ("weekday", "day_of_month", "hour", "minute", "second")}


def test_vectors_fields() -> None:
    for name, case in _FILE["fields"].items():
        assert _field(case, generation._offset_seconds) == case["answer"], name
    assert any(_field(case, lambda _key: 0) != case["answer"] for case in _FILE["fields"].values())


def _unframed(case: "dict[str, typing.Any]") -> "dict[str, list[typing.Any]]":
    moved, given = generation._off_own_clocks(
        case["before"], case["framed"], case["shifts"], case["offsets"], case["whole"],
        case["pinned"], tuple(case["body"]), (case["lows"], case["highs"]), case["scale"],
    )
    return {"ordinals": moved, "offsets": given}


def test_vectors_frames(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, case in _FILE["frames"].items():
        assert _unframed(case) == case["answer"], name

    def rank_by_rank(moved: "list[int]", given: "list[str]", framed: "list[int]", shifts: "list[int]", offsets: "list[str]", span: "tuple[int, int]", _gap: "tuple[int, int]", scale: int) -> None:
        for rank in range(span[0], span[1]):
            moved[rank] = framed[rank] * scale - shifts[rank]
            given[rank] = offsets[rank]

    # Codex's item 2: a bare date in the frame's days given back where it stood, or rank by rank
    # at the day the pass handed it, past the gap's top (mutants).
    days = _FILE["frames"]["bare_dates_in_days"]
    stood = dict(days, pinned=[days["pinned"][rank] or days["whole"][rank] for rank in range(len(days["whole"]))])
    assert _unframed(stood) != days["answer"]

    def handed(moved: "list[int]", framed: "list[int]", shifts: "list[int]", _whole: "list[bool]", span: "tuple[int, int]", _high: int, scale: int) -> None:
        for rank in range(span[0], span[1]):
            moved[rank] = framed[rank] * scale - shifts[rank]

    with monkeypatch.context() as patched:
        patched.setattr(generation, "_own_clock_days", handed)
        assert _unframed(days) != days["answer"]
    monkeypatch.setattr(generation, "_own_clock_run", rank_by_rank)
    assert any(_unframed(case) != case["answer"] for case in _FILE["frames"].values())


def _pins(case: "dict[str, typing.Any]") -> "list[str]":
    return generation._pinned_offset_keys(
        dict(case["left"]), list(case["keys"]), [tuple(block) for block in case["blocks"]],
        tuple(case["body"]), [(rule, tuple(where), list(counts)) for rule, where, counts in case["censuses"]],
        case["off_midnight"], case["step"],
    )


def _shares(case: "dict[str, typing.Any]") -> "list[typing.Any]":
    found = generation._pinned_offset_shares(
        dict(case["left"]), list(case["keys"]), [tuple(block) for block in case["blocks"]],
        tuple(case["body"]), [(rule, tuple(where), list(counts)) for rule, where, counts in case["censuses"]],
        case["off_midnight"], case["step"], list(case["leaps"]),
    )
    return [[[[key, count] for key, count in taken], sixtieth] for taken, sixtieth in found]


def test_vectors_pins(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, case in _FILE["pins"].items():
        assert _pins(case) == case["answer"], name
        assert _shares(case) == case["shares"], name
    lexical = dict(_FILE["pins"]["few_off_rung"], censuses=[])
    assert _pins(lexical) != _FILE["pins"]["few_off_rung"]["answer"]
    blind = dict(_FILE["pins"]["c551_listed_tail"], off_midnight=False)
    assert _pins(blind) != _FILE["pins"]["c551_listed_tail"]["answer"]
    # Codex's items 1 and 3: a block the keys share, and a block written at a sixtieth second.
    no_leap = dict(_FILE["pins"]["leap_block_at_sixty"], leaps=[False])
    assert _shares(no_leap) != _FILE["pins"]["leap_block_at_sixty"]["shares"]
    monkeypatch.setattr(generation, "_pinned_split", lambda *_arguments: [])
    assert _shares(_FILE["pins"]["split_hour_block"]) != _FILE["pins"]["split_hour_block"]["shares"]


def _spread(case: "dict[str, typing.Any]") -> "list[str]":
    found = generation._keys_by_gap(list(case["keys"]), dict(case["left"]), list(case["open_ranks"]), (case["lows"], case["highs"]))
    return [found[rank] for rank in sorted(case["open_ranks"])]


def test_vectors_spreads() -> None:
    """G7.4 step 2 on the shared clock: a rare key takes whole gaps inside the column."""
    for name, case in _FILE["spreads"].items():
        assert _spread(case) == case["answer"], name
    case = _FILE["spreads"]["few_off_spread"]
    in_rank_order: "list[str]" = []
    for key in case["keys"]:
        in_rank_order += [key] * case["left"][key]
    assert in_rank_order != case["answer"]


def _forms(case: "dict[str, typing.Any]", apart: bool, cap: "typing.Any") -> "list[bool]":
    return generation._clocked_form_flags(
        (case["lows"], case["highs"]), case["dates"], case["moments"], apart,
        None if cap is None else tuple(cap),
    )


def test_vectors_forms() -> None:
    for name, case in _FILE["forms"].items():
        assert _forms(case, case["apart"], case["cap"]) == case["answer"], name
    capped = _FILE["forms"]["tight_gap_capped"]
    assert _forms(capped, False, None) != capped["answer"]
    hour_zero = _FILE["forms"]["body_capped_by_hour_zero"]
    assert _forms(hour_zero, hour_zero["apart"], None) != hour_zero["answer"]
    # The repair's item 2: every published bare date is spent, the two the free days leave over
    # among them.
    leftover = _FILE["forms"]["leftover_stays_a_date"]
    assert sum(leftover["answer"]) == leftover["dates"]
    # Its second skeptic's item 1: the leftover pass stops at the body's cap at hour 0, so a bare
    # date is left unwritten (red on `leftover_nocap`, the oracle's mirror of the clause pinned).
    capped = _FILE["forms"]["leftover_capped_at_hour_zero"]
    assert sum(capped["answer"]) < capped["dates"]
    assert _leftover_without_the_cap(generation._clocked_form_flags)(
        (capped["lows"], capped["highs"]), capped["dates"], capped["moments"], capped["apart"], tuple(capped["cap"]),
    ) != capped["answer"]


def _days(case: "dict[str, typing.Any]", apart: bool, shut: bool) -> "list[int]":
    closed = (frozenset(case["shut_weekdays"]), frozenset(case["shut_bins"])) if shut else (frozenset(), frozenset())
    return generation._form_step_days(case["ordinals"], (case["lows"], case["highs"]), case["whole"], apart, closed)


def test_vectors_form_days() -> None:
    for name, case in _FILE["form_days"].items():
        assert _days(case, case["apart"], True) == case["answer"], name
    assert _days(_FILE["form_days"]["days_apart"], False, True) != _FILE["form_days"]["days_apart"]["answer"]
    weekend = _FILE["form_days"]["off_the_weekend"]
    assert _days(weekend, weekend["apart"], False) != weekend["answer"]
    # The repair's item 2: the bare date the gap's one free day cannot hold stands on that
    # midnight too, never off midnight.
    held = _FILE["form_days"]["leftover_on_a_held_day"]["answer"]
    assert held[1] == held[2] and held[1] % 86400 == 0


def test_the_shared_sure_cells() -> None:
    """On the shared clock the sure-cell rules read rule 4's count alone (blocker 1)."""
    published = [(0, "2024-01-01 22:30:00")]
    tails: "list[tuple[int, tuple[str, ...] | None]]" = [(3, ("2024-01-01 00:00:00",))]
    assert calendar_clock.own_clock_sure(published, tails, "utc") == ([], [(3, None)])
    assert calendar_clock.own_clock_sure(published, tails, "local") == (published, tails)


# -- Batch 3b part 2b: the shared clock meets the dates that stand out -------


def _heavy_column(kind: str) -> "list[str]":
    """1,000 cells at midnight over 2023, 81 of them on 15 June, a date that stands out.

    `local` writes bare dates (G7.1's ordinal space `date`); `shared` writes
    each day's local midnight on the central European clock, `+01:00` in
    winter and `+02:00` in summer; `joint` writes bare dates beside
    `T00:00:00-03:00` stamps of the same days."""
    draw = random.Random(5)
    start = datetime.date(2023, 1, 2)
    heavy = datetime.date(2023, 6, 15)
    days = [heavy] * 80 + [start + datetime.timedelta(days=draw.randrange(364)) for _ in range(920)]
    cells: "list[str]" = []
    for place, day in enumerate(days):
        if kind == "local" or (kind == "joint" and place % 2):
            cells += [day.isoformat()]
        elif kind == "joint":
            cells += [day.isoformat() + "T00:00:00-03:00"]
        else:
            local = datetime.datetime(day.year, day.month, day.day)
            cells += [local.isoformat() + shared_clock_shapes.off_text(shared_clock_shapes.eu_central(local))]
    return cells


@pytest.mark.parametrize("kind", ("local", "shared", "joint"))
def test_a_midnight_column_with_a_date_that_stands_out_meets_both(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Heavy dates keep their scope (G7.3j: `_ordinal_space` "date", the local clock); 3b.7's
    censuses stand beside them.

    The bare dates list 15 June with its 81 rows and their twin meets the list and the
    censuses together; the same days at local midnight on two offsets, or as bare dates
    beside -03:00 midnight stamps, are counted on the shared clock and in seconds, list
    nothing, and their twins meet every census 3b.7 publishes there, at floors 11 and 36,
    seeds 0 to 2."""
    text = "t\n" + "".join(f"{cell}\n" for cell in _heavy_column(kind))
    for floor in (11, 36):
        described = kpi_shapes.describe(tmp_path / f"{kind}{floor}", kind, text, floor)
        block = described.block("t")
        if kind == "local":
            assert block["heavy_dates"] == [{"date": "2023-06-15", "count": 81}], floor
        else:
            assert block["datetimes_read_at"] == "utc" and block["all_at_midnight"] is True, floor
            assert block["heavy_dates"] == [], floor
        assert block["weekday_census"], (kind, floor)
        for seed in SEEDS:
            assert _missed(described, seed) == [], (kind, floor, seed)

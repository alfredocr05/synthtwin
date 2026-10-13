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
and the twenty-fourth vectors file, each case red on its mutant.
"""

from __future__ import annotations

import json
import pathlib
import typing

import pytest

import kpi_shapes
import shared_clock_shapes
from synthtwin import calendar_clock, calendar_rules, generation, parsing, taxonomy, validation

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-24.json"
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))

ROWS = 1000
FLOORS = (11, 36)
SEEDS = (0, 1, 2)
# The battery's columns the censuses are met on (S3): two offsets across both
# changes of daylight saving time, two sites, a -06:00 clinic with one cell in
# fifty at +05:30, an instrument writing Z beside a ward at +02:00, sixtieth
# seconds at +05:30, and three columns of the joint member.
MET = (
    "dst_clinic", "dst_ed", "two_sites", "few_off", "z_plus", "leap_shared",
    "isomix_admit", "isomix_offsets", "clinic_isomix",
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


# -- S6: item (b), an all-different joint column ------------------------------


def test_s6_an_all_different_joint_column_is_held_exactly(tmp_path_factory: pytest.TempPathFactory) -> None:
    """800 ISO stamps beside 200 consecutive ISO dates, all different: every twin at seeds 0 to
    2 holds 1,000 different values, and `distinct.n_distinct` is checked EXACTLY (HELD, never
    WITHIN-BOUND), where 881 of 1,000 passed validate before the landing."""
    described = _described(tmp_path_factory, "isomix_alldiff_b", 11)
    assert described.block("t")["n_distinct"] == ROWS
    for seed in SEEDS:
        held = _checks(described, kpi_shapes.twin_text(described, seed), f"b{seed}.csv")["distinct.n_distinct"]
        # EXACT: the count printed as the published one, never a measure inside a window.
        assert (held.verdict, held.achieved) == (validation.HELD, held.published), seed


def test_s6_red_without_the_cap_or_the_exact_check(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutants: the bare dates spent with no cap per gap, as the rotation alone spends them, and
    the check widened back to the envelope."""
    described = _described(tmp_path_factory, "isomix_alldiff_b", 11)
    flags = generation._clocked_form_flags
    with monkeypatch.context() as patch:
        patch.setattr(generation, "_clocked_form_flags", lambda gaps, dates, moments, _apart: flags(gaps, dates, moments, False))
        text = kpi_shapes.twin_text(described, 0)
        assert len(set(text.split("\n")[1:]) - {""}) < ROWS
    monkeypatch.setattr(validation, "_joint_all_different", lambda *_arguments: False)
    widened = _checks(described, kpi_shapes.twin_text(described, 0), "w.csv")["distinct.n_distinct"]
    assert widened.achieved != widened.published, widened


@pytest.mark.xfail(strict=True, reason=(
    "measured on the landing's build: the tight column's gaps hold fewer free midnight days than "
    "its 200 dates at 1,000 rows and a floor of 11, so 4 of its bare dates are written as "
    "moments (196 of 200), resolution_mix and n_at_midnight are MISSED and the twin names "
    "resolution_mix -- never silent (the design's stated limit)"
))
def test_s6_the_tight_column_writes_every_bare_date(tmp_path_factory: pytest.TempPathFactory) -> None:
    described = _described(tmp_path_factory, "isomix_alldiff_b", 11)
    assert _missed(described, 0) == []


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

    def counted(details: "dict[str, object]", pairs: "list[tuple[str, str]]") -> "list[int] | None":
        calls[0] = calls[0] + 1
        return ranked(details, pairs)

    monkeypatch.setattr(taxonomy, "_census_ranked", counted)
    cells = shared_clock_shapes.build("two_sites", ROWS)
    kpi_shapes.describe(tmp_path, "one", "t\n" + "".join(f"{cell}\n" for cell in cells), 11)
    assert calls[0] == 1


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

    monkeypatch.setattr(generation, "_own_clock_run", rank_by_rank)
    assert any(_unframed(case) != case["answer"] for case in _FILE["frames"].values())


def _pins(case: "dict[str, typing.Any]") -> "list[str]":
    return generation._pinned_offset_keys(
        dict(case["left"]), list(case["keys"]), [tuple(block) for block in case["blocks"]],
        tuple(case["body"]), [(rule, tuple(where), list(counts)) for rule, where, counts in case["censuses"]],
        case["off_midnight"], case["step"],
    )


def test_vectors_pins(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, case in _FILE["pins"].items():
        assert _pins(case) == case["answer"], name
    lexical = dict(_FILE["pins"]["few_off_rung"], censuses=[])
    assert _pins(lexical) != _FILE["pins"]["few_off_rung"]["answer"]
    blind = dict(_FILE["pins"]["c551_listed_tail"], off_midnight=False)
    assert _pins(blind) != _FILE["pins"]["c551_listed_tail"]["answer"]


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


def _days(case: "dict[str, typing.Any]", apart: bool, shut: bool) -> "list[int]":
    closed = (frozenset(case["shut_weekdays"]), frozenset(case["shut_bins"])) if shut else (frozenset(), frozenset())
    return generation._form_step_days(case["ordinals"], (case["lows"], case["highs"]), case["whole"], apart, closed)


def test_vectors_form_days() -> None:
    for name, case in _FILE["form_days"].items():
        assert _days(case, case["apart"], True) == case["answer"], name
    assert _days(_FILE["form_days"]["days_apart"], False, True) != _FILE["form_days"]["days_apart"]["answer"]
    weekend = _FILE["form_days"]["off_the_weekend"]
    assert _days(weekend, weekend["apart"], False) != weekend["answer"]


def test_the_shared_sure_cells() -> None:
    """On the shared clock the sure-cell rules read rule 4's count alone (blocker 1)."""
    published = [(0, "2024-01-01 22:30:00")]
    tails: "list[tuple[int, tuple[str, ...] | None]]" = [(3, ("2024-01-01 00:00:00",))]
    assert calendar_clock.own_clock_sure(published, tails, "utc") == ([], [(3, None)])
    assert calendar_clock.own_clock_sure(published, tails, "local") == (published, tails)

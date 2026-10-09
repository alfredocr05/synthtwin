"""THE HOUR'S REVIEW (landing 3b.2-H, lane T2, plan P4-D371): Codex's four items, each reproduced.

Codex reviewed the landing once (2026-10-08) and raised four items; each
is reproduced here on the review's own scenario, red on the head it
reviewed (b3fb647), and fixed:

* item 2 -- on a stamp declared a 12-hour clock with no marker, the
  validator took G7.3b step 10 onto the ranks but not onto the tie group
  before the end and step 9's reach were read off it, so its window was
  narrower than the construction's and a twin the construction drew was
  MISSED: `test_a_twin_the_half_day_draws_is_not_missed` (Codex's own
  column at seed 102) and `test_the_half_day_windows_are_the_construction_s`
  (a high and a low tail, both measures, red with the projection
  withdrawn);
* item 4 -- the withheld census's sentences: a middle half whose 25th or
  75th percentile lies inside a tail is NOT PUBLISHED, which is not SHORT
  (NF117 beside NF90), and where the sure cells leave no grouping, NF92
  names them: `test_a_middle_half_not_published_is_not_called_short`,
  `test_a_short_middle_half_is_still_called_short` and
  `test_the_sure_cells_that_leave_no_grouping_are_named`;
* item 3 -- PUT BACK (method G7.3g step 6) sorted and filtered every run
  again for each size before its first merge, so a clock state of one run
  of each size 1 to `k` beside `k(k-1)/2` alone did `k` times the work
  of one sort: `test_put_back_sorts_its_runs_once`.

Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import builtins
import datetime
import math
import pathlib
import random
import sys
import types

import pytest

import fixtures
import kpi_shapes
from synthtwin import (
    calendar_rules,
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

DAY = 86400
_MONDAY = 19723  # 2024-01-01, a Monday


# -- item 2: the half day's tie group, projected before a window stands on it ---------

_TWELVE = "%m/%d/%Y %I:%M"


def _codex_half_day() -> "list[datetime.datetime]":
    """Codex's column: 400 morning moments of 320 days, each written twice, beside
    a high tail of one moment at 2024-12-01 02:31 and twelve up to two days on."""
    draw = random.Random(42)
    found: "list[datetime.datetime]" = []
    for _row in range(400):
        moment = datetime.datetime(2024, 1, 1) + datetime.timedelta(
            days=draw.randrange(320), minutes=draw.randrange(720)
        )
        found += [moment, moment]
    start = datetime.datetime(2024, 12, 1, 2, 31)
    found += [start]
    for minutes in (1336, 1355, 1416, 1439, 1549, 1924, 1952, 2006, 2884, 2927, 1317, 1317):
        found += [start + datetime.timedelta(minutes=minutes)]
    return found


def _half_day_column(seed: int) -> "list[datetime.datetime]":
    """Morning moments, once or twice each, beside a cluster at each end spread
    over one to three days, every one of them on the dial's morning."""
    draw = random.Random(seed)
    found: "list[datetime.datetime]" = []
    days = draw.randint(60, 300)
    start = datetime.datetime(2024, 1, 10)
    for _row in range(draw.randint(150, 450)):
        moment = start + datetime.timedelta(days=draw.randrange(days), minutes=draw.randrange(1, 720))
        found += [moment] * draw.choice((1, 2))
    end = start + datetime.timedelta(days=days)
    for _row in range(draw.randint(12, 40)):
        found += [start - datetime.timedelta(minutes=draw.randint(1, 60 * 24 * draw.randint(1, 3)))]
        found += [end + datetime.timedelta(minutes=draw.randint(1, 60 * 24 * draw.randint(1, 3)))]
    return [moment if moment.hour < 12 else moment - datetime.timedelta(hours=12) for moment in found]


def _twelve_hour_described(
    folder: pathlib.Path, moments: "list[datetime.datetime]", floor: int
) -> "tuple[kpi_shapes.Described, str]":
    """The moments written on the dial with no marker, declared `--twelve-hour`, described."""
    text = "seen_at\n" + "\n".join(moment.strftime(_TWELVE) for moment in moments) + "\n"
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, "real.csv", text)
    settings = taxonomy.Settings(small_cell_floor=floor, forced_twelve_hour_clocks=("seen_at",))
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor), settings, [], [], []
    )
    loaded = contract.load_profile(str(fixtures.write_profile(folder, "real-profile.json", document)))
    return kpi_shapes.Described(folder, table, document, loaded), text


def test_a_twin_the_half_day_draws_is_not_missed(tmp_path: pathlib.Path) -> None:
    """Codex's item 2, his own column at floor 11 and seed 102: the construction
    draws the high tail at a mean of 1897.92 minutes, inside its bound of
    1908.75, and says nothing; b3fb647's validator held it to 1896.25 and
    reported `tails.high.mean_distance` MISSED (as at seed 194)."""
    described, _text = _twelve_hour_described(tmp_path, _codex_half_day(), 11)
    twin = generation.generate(described.loaded, 102)
    assert not twin.deviations
    outcome = kpi_shapes.measure(described, rendering.twin_csv(twin), "twin.csv")
    assert kpi_shapes.missed(outcome) == []
    high = [check for check in outcome.checks if check.subcheck == "tails.high.mean_distance"]
    assert [check.verdict for check in high] == [validation.WITHIN_BOUND]


# The edit withdrawing the group's projection from the validator's construction.
_GROUP_ON_THE_HALF_DAY = (
    "            group = calendar_clock.half_day_distances(\n"
    "                [group], half_day[0], half_day[1], half_day[2], False, edge\n"
    "            )[0]\n"
)


def _validation_without_the_projection(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    source = pathlib.Path(validation.__file__).read_text(encoding="utf-8")
    assert source.count(_GROUP_ON_THE_HALF_DAY) == 1
    name = "synthtwin._validation_review_mutant"
    module = types.ModuleType(name)
    module.__file__ = validation.__file__
    monkeypatch.setitem(sys.modules, name, module)
    exec(
        compile(source.replace(_GROUP_ON_THE_HALF_DAY, "            group = group\n"), validation.__file__, "exec"),
        module.__dict__,
    )
    return module


def _measures(near: "list[int]", far: "list[int]", rows: int) -> "tuple[float, float, float, float]":
    """The windows of the mean and the root-mean-square distance two bounds give."""
    return (
        sum(near) / rows,
        sum(far) / rows,
        math.sqrt(sum(value * value for value in near) / rows),
        math.sqrt(sum(value * value for value in far) / rows),
    )


@pytest.mark.parametrize(
    ("shape", "floor", "side"),
    [("codex", 11, "high"), ("cluster-10", 36, "high"), ("cluster-170", 36, "low")],
)
def test_the_half_day_windows_are_the_construction_s(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, shape: str, floor: int, side: str
) -> None:
    """Codex's item 2, on both sides and both measures. Each side's window,
    rank by rank and as the mean and root-mean-square distance it bounds, is
    the construction's own (`generation._tail_sum_bounds` over
    `generation._date_layout`); and on the side named, whose tail holds a tie
    group, the validator with the group's projection withdrawn -- b3fb647's --
    draws another, so this column asks the projection there."""
    moments = _codex_half_day() if shape == "codex" else _half_day_column(int(shape.split("-")[1]))
    described, _text = _twelve_hour_described(tmp_path, moments, floor)
    column = described.loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts)
    checked = validation._date_tail_windows(column, facts, floor, "", True)
    layout = generation._date_layout(column, facts, column.n_present - facts.n_unparsed, floor, "")
    counted = contract.datetime_counts_reachable(column)
    for key, plan in (("low", layout.low), ("high", layout.high)):
        assert plan is not None and plan.shape is not None, key
        if key == side:
            assert plan.shape.grouped < plan.rows, (key, "no tie group")
        built = generation._tail_sum_bounds(plan, counted)
        assert (list(checked[key][0]), list(checked[key][1])) == (list(built[0]), list(built[1])), key
        assert _measures(checked[key][0], checked[key][1], plan.rows) == _measures(
            built[0], built[1], plan.rows
        ), key
    before = _validation_without_the_projection(monkeypatch)._date_tail_windows(
        column, facts, floor, "", True
    )
    assert before[side] != checked[side], side


# -- item 4: why a census is withheld, said as it is ---------------------------------

_HOURS_SAID = "hours of the day this column's values fall on"


def _hour_sentences(described: kpi_shapes.Described) -> "list[str]":
    """Every sentence of the description about the one column's hours of the day."""
    return [
        entry["note"] for entry in described.document["publication_notes"]
        if entry["column"] == "seen_at" and _HOURS_SAID in entry["note"]
    ]


def _plain(folder: pathlib.Path, cells: "list[str]") -> kpi_shapes.Described:
    return kpi_shapes.describe(folder, "real", "seen_at\n" + "\n".join(cells) + "\n", 11)


def test_a_middle_half_not_published_is_not_called_short(tmp_path: pathlib.Path) -> None:
    """Codex's item 4, NF90: 30 values at 2024-01-01 08:00, 40 at 2024-01-20 and
    30 at 2024-02-01, floor 11. Each tail holds 30 rows, so the 25th and 75th
    percentiles lie inside the tails and are not published; the real middle half
    spans 31 days. b3fb647 said it spans fewer than four; the column now says its
    middle half is not published (NF117)."""
    cells = (
        ["2024-01-01 08:00:00"] * 30 + ["2024-01-20 08:00:00"] * 40 + ["2024-02-01 08:00:00"] * 30
    )
    described = _plain(tmp_path, cells)
    block = described.block("seen_at")
    assert block["hour_census"] == []
    assert block["date_percentiles"]["p25"] is None and block["date_percentiles"]["p75"] is None
    sentences = _hour_sentences(described)
    assert len(sentences) == 1 and "fewer than four days" not in sentences[0], sentences
    assert sentences == [taxonomy.rendered(taxonomy.NOTE_HOUR_WITHHELD_UNPUBLISHED_SPAN, ())]


def test_a_short_middle_half_is_still_called_short(tmp_path: pathlib.Path) -> None:
    """NF90 where it is true: 300 moments over three days publish a 25th and a
    75th percentile fewer than four days apart, and the column says so."""
    draw = random.Random(40101)
    start = datetime.datetime(2024, 3, 4)
    cells = [
        (start + datetime.timedelta(seconds=draw.randrange(3 * DAY))).strftime("%Y-%m-%d %H:%M:%S")
        for _row in range(300)
    ]
    described = _plain(tmp_path, cells)
    block = described.block("seen_at")
    assert block["hour_census"] == []
    assert block["date_percentiles"]["p25"] is not None and block["date_percentiles"]["p75"] is not None
    assert _hour_sentences(described) == [taxonomy.rendered(taxonomy.NOTE_HOUR_WITHHELD_SHORT_SPAN, ())]


def test_the_sure_cells_that_leave_no_grouping_are_named(tmp_path: pathlib.Path) -> None:
    """Codex's item 4, NF92: one moment on each of 100 dates from 2024-01-01, the
    first eleven and the last eleven at midnight and the 78 between at 23:00,
    floor 11. The tails list no value, so the 22 rows the description counts at
    midnight are sure cells of hour 0 where the body holds none, and no group
    short of the whole day holds them -- though hours 0 to 22 at nought and hour
    23 at 78 meet the floor. b3fb647 said only that no grouping met the floor;
    the sentence now names the sure cells."""
    cells: "list[str]" = []
    for step in range(100):
        day = datetime.date(2024, 1, 1) + datetime.timedelta(days=step)
        clock = "00:00:00" if step < 11 or step >= 89 else "23:00:00"
        cells += [f"{day.isoformat()} {clock}"]
    described = _plain(tmp_path, cells)
    block = described.block("seen_at")
    assert block["hour_census"] == [] and block["n_at_midnight"] == 22
    assert block["low_tail"]["values"] is None and block["high_tail"]["values"] is None
    bins = [0] * 23 + [78]
    assert calendar_rules.merged_groups(bins, [0] * 24, 11, False) == ((0, 22, 0), (23, 23, 78))
    assert calendar_rules.merged_groups(bins, [22] + [0] * 23, 11, False) == ()
    sentences = _hour_sentences(described)
    assert sentences == [taxonomy.rendered(taxonomy.NOTE_HOUR_WITHHELD_NO_GROUPING, (11,))]
    assert "places in its hours for certain" in sentences[0] and "at midnight" in sentences[0]


# -- item 3: PUT BACK's runs, sorted once ---------------------------------------


def _put_back_state(size: int) -> "tuple[generation._WeekdayPass, int]":
    """Codex's family: one run of each size 1 to `size` -- that many ranks on one
    second each -- beside `size * (size - 1) / 2` ranks alone, `size**2` movable
    ranks in one gap, seven seconds apart from 08:00 of a Monday; and how many
    runs there are."""
    sizes = list(range(1, size + 1)) + [1] * (size * (size - 1) // 2)
    ordinals: "list[int]" = []
    place = _MONDAY * DAY + 8 * 3600
    for each in sizes:
        place = place + 7
        if place % DAY == 0:
            place = place + 1
        ordinals += [place] * each
    rows = len(ordinals)
    state = generation._WeekdayPass(
        moved=list(ordinals), held={}, where=tuple(0 for _hour in range(24)), facts=None,  # type: ignore[arg-type]
        word="", widths=False, kinds={}, holes=frozenset(), lows=[ordinals[0]] * rows,
        highs=[ordinals[-1]] * rows, keep_units=True, unit=3600, step=1, day=DAY, bins="hour",
        period=24, keeps="day",
    )
    for ordinal in state.moved:
        generation._weekday_tally(state.held, ordinal, 1)
        generation._weekday_tally(state.units_held, ordinal // state.unit, 1)
    return state, len(sizes)


def _sorted_by_put_back(monkeypatch: pytest.MonkeyPatch, size: int) -> "tuple[int, int, bool]":
    """How many elements PUT BACK hands to `sorted` on Codex's state of `size`,
    how many runs the state holds, and whether the one excess was restored.
    A count of operations, not of seconds: the same on any machine."""
    state, runs = _put_back_state(size)
    rows = len(state.moved)
    count = generation._weekday_count(state)
    seen = [0]

    def counting(values, *arguments, **named):  # type: ignore[no-untyped-def]
        found = builtins.sorted(values, *arguments, **named)
        seen[0] = seen[0] + len(found)
        return found

    monkeypatch.setattr(generation, "sorted", counting, raising=False)
    try:
        generation._clock_count_put_back(
            state, 0, rows - 1, [False] * rows, count - 1, tuple(range(7))
        )
    finally:
        monkeypatch.delattr(generation, "sorted")
    return seen[0], runs, generation._weekday_count(state) == count - 1


def test_put_back_sorts_its_runs_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3. The written seconds one too many, one merge restores them;
    before it, PUT BACK may read each run a bounded number of times whatever
    how many sizes the runs come in. b3fb647 handed `sorted` 33,660 elements
    for the 820 runs of `size` 40 (41 a run) and 262,520 for the 3,240 of
    `size` 80 (81 a run), growing as the square root of the rows; sorted once,
    they cost two readings a run at both sizes (1,640 and 6,480)."""
    for size in (40, 80):
        elements, runs, restored = _sorted_by_put_back(monkeypatch, size)
        assert restored, size
        assert elements <= 3 * runs, (size, elements, runs)

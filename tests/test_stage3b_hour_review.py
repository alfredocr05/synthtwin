"""THE HOUR'S REVIEW (landing 3b.2-H, lane T2, plan P4-D371): Codex's four items, each reproduced.

Codex reviewed the landing once (2026-10-08) and raised four items; each
is reproduced here on the review's own scenario, red on the head it
reviewed (b3fb647), and fixed:

* item 1 -- a sixtieth second, `23:59:60`, is WRITTEN in hour 23 while
  its instant is the next day's first second; the producer, the loader,
  the generator and the validator all binned the instant, so eleven of
  them on each of 100 dates published every body cell in hour 0 and the
  twin wrote its body there: `test_a_sixtieth_second_counts_in_the_hour_
  it_is_written_in`, `test_the_twin_writes_its_hours_as_written` and,
  for the ranks two pins of one such second leave their one place,
  `test_the_ranks_two_pins_of_one_sixtieth_second_leave_are_written_as_it`
  (each with the generator's own mutant), beside the sixteenth vectors
  file's `hour_sixtieth_second` and `hour_sixtieth_ties`;
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
  of one sort: `test_put_back_sorts_its_runs_once` counts what reaches
  `sorted`, and `test_put_back_work_grows_with_the_rows` the lines it
  runs at nine times the rows, b3fb647's order held beside it.

Each mutant is the module's own source with ONE edit, built by
`_edited`. Every table is built here, seeded and neutral (plan D13).
"""

from __future__ import annotations

import builtins
import copy
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
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

DAY = 86400
_MONDAY = 19723  # 2024-01-01, a Monday


def _edited(
    module: types.ModuleType, old: str, new: str, name: str, monkeypatch: pytest.MonkeyPatch
) -> types.ModuleType:
    """`module` built again from its own source with ONE edit: `old`, found
    exactly once, made `new`. The one route here that runs a string of
    source (`tests/test_version_reach.py` names it)."""
    source = pathlib.Path(str(module.__file__)).read_text(encoding="utf-8")
    assert source.count(old) == 1, name
    built = types.ModuleType(name)
    built.__file__ = module.__file__
    monkeypatch.setitem(sys.modules, name, built)
    exec(compile(source.replace(old, new), str(module.__file__), "exec"), built.__dict__)
    return built


# -- item 1: a sixtieth second, in the hour it is written in -----------------------------


def _codex_leap() -> "list[str]":
    """Codex's column: eleven copies of 23:59:60 on each of 100 dates from 2024-01-01."""
    found: "list[str]" = []
    for step in range(100):
        day = datetime.date(2024, 1, 1) + datetime.timedelta(days=step)
        found += [f"{day.isoformat()} 23:59:60"] * 11
    return found


def _leap_beside_midnight() -> "list[str]":
    """On each of 100 dates: four values at 23:59:60, three at 23:05, 23:20 and 23:40,
    and two at 00:30 -- the hours on either side of midnight, both published."""
    found: "list[str]" = []
    for step in range(100):
        day = (datetime.date(2024, 1, 1) + datetime.timedelta(days=step)).isoformat()
        found += [f"{day} 23:59:60"] * 4
        found += [f"{day} 23:{minute:02d}:00" for minute in (5, 20, 40)]
        found += [f"{day} 00:30:00"] * 2
    return found


def _instant(cell: str) -> "tuple[datetime.datetime, str]":
    """A cell's rank key: its instant, a sixtieth second at the next minute's first, then its text."""
    if cell.endswith(":60"):
        return (datetime.datetime.fromisoformat(cell[:-2] + "59") + datetime.timedelta(seconds=1), cell)
    return (datetime.datetime.fromisoformat(cell), cell)


def _body_hours(text: str, block: dict) -> "dict[int, int]":
    """The file's body by written hour: its cells ranked by instant, the tails' rows off."""
    cells = sorted((line for line in text.split("\n")[1:] if line), key=_instant)
    body = cells[block["low_tail"]["rows"] : len(cells) - block["high_tail"]["rows"]]
    found: "dict[int, int]" = {}
    for cell in body:
        found[int(cell[11:13])] = found.get(int(cell[11:13]), 0) + 1
    return found


def test_a_sixtieth_second_counts_in_the_hour_it_is_written_in(tmp_path: pathlib.Path) -> None:
    """Codex's item 1, publication and validation. The column's 1,078 body cells are all
    written in hour 23, and the census says so; b3fb647 published them all in hour 0, and
    its loader and validator agreed with it. The loader now refuses that census -- the
    boundaries and rungs it publishes at 23:59:60 are sure cells of hour 23 (HC5) -- and
    V5-H1 counts a file whose body is written at 00:30 MISSED, where it counted it HELD."""
    cells = _codex_leap()
    text = "seen_at\n" + "\n".join(cells) + "\n"
    described = kpi_shapes.describe(tmp_path, "real", text, 11)
    block = described.block("seen_at")
    assert block["hour_census"] == [
        {"first": 0, "last": 22, "count": 0}, {"first": 23, "last": 23, "count": 1078},
    ]
    outcome = kpi_shapes.measure(described, text, "real.csv")
    assert kpi_shapes.missed(outcome) == []
    assert [c.verdict for c in outcome.checks if c.subcheck == "hour_census.groups"] == [validation.HELD]
    old = copy.deepcopy(described.document)
    old["columns"][0]["hour_census"] = [
        {"first": 0, "last": 0, "count": 1078}, {"first": 1, "last": 23, "count": 0},
    ]
    with pytest.raises(errors.ProfileError, match="HC5"):
        contract.load_profile(str(fixtures.write_profile(tmp_path, "old-profile.json", old)))
    low, high = block["low_tail"]["rows"], block["high_tail"]["rows"]
    moved = cells[:low] + [
        (datetime.date.fromisoformat(cell[:10]) + datetime.timedelta(days=1)).isoformat() + " 00:30:00"
        for cell in cells[low : len(cells) - high]
    ] + cells[len(cells) - high :]
    late = kpi_shapes.measure(described, "seen_at\n" + "\n".join(moved) + "\n", "late.csv")
    assert [c.verdict for c in late.checks if c.subcheck == "hour_census.groups"] == [validation.MISSED]


# The edit that has the hour's pass meet the census by ordinal, as b3fb647 did.
_AS_WRITTEN = (
    "    counts = _clock_counts_as_written(\n"
    "        state,\n"
    "        [count for _first, _last, count in census],\n"
    "        _sixtieth_seconds(layout, moved, pinned, body_low, body_high),\n"
    "    )\n"
)
_BY_ORDINAL = "    counts = [count for _first, _last, count in census]\n"


def test_the_twin_writes_its_hours_as_written(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 1, generation. Codex's column at seeds 0 to 4: every body cell of the
    twin written in hour 23 -- the boundaries and rungs at 23:59:60 from their own fields,
    every other at an ordinary second -- nothing missed and no deviation, where b3fb647's
    twin wrote 1,069 of them in hour 0. And on 100 dates of 23:59:60, three other times of
    hour 23 and two at 00:30, nothing missed at seeds 0 to 2. Mutant: the pass meeting the
    census by ordinal, which files a deviation the twin does not deserve on the first
    column and, silently, misses the census on the second."""
    codex = kpi_shapes.describe(tmp_path / "codex", "codex", "seen_at\n" + "\n".join(_codex_leap()) + "\n", 11)
    beside = kpi_shapes.describe(
        tmp_path / "beside", "beside", "seen_at\n" + "\n".join(_leap_beside_midnight()) + "\n", 11
    )
    for seed in range(5):
        twin = generation.generate(codex.loaded, seed)
        written = rendering.twin_csv(twin)
        assert not twin.deviations, seed
        assert kpi_shapes.missed(kpi_shapes.measure(codex, written, f"twin-{seed}.csv")) == [], seed
        assert _body_hours(written, codex.block("seen_at")) == {23: 1078}, seed
    for seed in range(3):
        written = rendering.twin_csv(generation.generate(beside.loaded, seed))
        assert kpi_shapes.missed(kpi_shapes.measure(beside, written, f"beside-{seed}.csv")) == [], seed
    mutant = _edited(generation, _AS_WRITTEN, _BY_ORDINAL, "synthtwin._generation_review_mutant", monkeypatch)
    assert [d.fact for d in mutant.generate(codex.loaded, 0).deviations] == ["hour_census"]
    written = rendering.twin_csv(mutant.generate(beside.loaded, 0))
    assert kpi_shapes.missed(kpi_shapes.measure(beside, written, "mutant.csv")) == ["seen_at:hour_census.groups"]


# The edit that writes a rank between two pins of one sixtieth second from its ordinal.
_TIED = "        elif rank in tied:\n            published, at = tied[rank]\n"
_UNTIED = "        elif False:\n            published, at = tied[rank]\n"


def test_the_ranks_two_pins_of_one_sixtieth_second_leave_are_written_as_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's column at a floor of 36: the low boundary and the 5th percentile both
    publish 2024-01-05 23:59:60, and the nine ranks between them have that one place,
    every row there holding that moment. They are written as it -- in hour 23, one value
    -- so at seeds 0 to 2 the twin holds 100 different values as published and its census,
    and nothing is missed. Mutant: those ranks written from the place's ordinal, at
    2024-01-06 00:00:00, a value and an hour the source never wrote -- 101 values, and
    the census missed though the pass counted them as written and filed nothing of it."""
    deep = kpi_shapes.describe(tmp_path, "deep", "seen_at\n" + "\n".join(_codex_leap()) + "\n", 36)
    block = deep.block("seen_at")
    assert block["low_tail"]["boundary"] == block["date_percentiles"]["p05"] == "2024-01-05 23:59:60"
    for seed in range(3):
        twin = generation.generate(deep.loaded, seed)
        written = rendering.twin_csv(twin)
        assert not twin.deviations, seed
        assert kpi_shapes.missed(kpi_shapes.measure(deep, written, f"deep-{seed}.csv")) == [], seed
        assert _body_hours(written, block) == {23: 1012}, seed
        assert len({line for line in written.split("\n")[1:] if line}) == block["n_distinct"] == 100
    mutant = _edited(generation, _TIED, _UNTIED, "synthtwin._generation_review_untied", monkeypatch)
    twin = mutant.generate(deep.loaded, 0)
    written = rendering.twin_csv(twin)
    assert "hour_census" not in [deviation.fact for deviation in twin.deviations]
    assert len({line for line in written.split("\n")[1:] if line}) == 101
    assert "seen_at:hour_census.groups" in kpi_shapes.missed(kpi_shapes.measure(deep, written, "untied.csv"))


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
    return _edited(
        validation, _GROUP_ON_THE_HALF_DAY, "            group = group\n",
        "synthtwin._validation_review_mutant", monkeypatch,
    )


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


def _put_back_state(
    size: int, module: types.ModuleType = generation
) -> "tuple[generation._WeekdayPass, int]":
    """Codex's family: one run of each size 1 to `size` -- that many ranks on one
    second each -- beside `size * (size - 1) / 2` ranks alone, `size**2` movable
    ranks in one gap, seven seconds apart from 08:00 of a Monday; and how many
    runs there are. Built of `module`'s own state."""
    sizes = list(range(1, size + 1)) + [1] * (size * (size - 1) // 2)
    ordinals: "list[int]" = []
    place = _MONDAY * DAY + 8 * 3600
    for each in sizes:
        place = place + 7
        if place % DAY == 0:
            place = place + 1
        ordinals += [place] * each
    rows = len(ordinals)
    state = module._WeekdayPass(
        moved=list(ordinals), held={}, where=tuple(0 for _hour in range(24)), facts=None,
        word="", widths=False, kinds={}, holes=frozenset(), lows=[ordinals[0]] * rows,
        highs=[ordinals[-1]] * rows, keep_units=True, unit=3600, step=1, day=DAY, bins="hour",
        period=24, keeps="day",
    )
    for ordinal in state.moved:
        module._weekday_tally(state.held, ordinal, 1)
        module._weekday_tally(state.units_held, ordinal // state.unit, 1)
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


# The edit that puts b3fb647's order back: every run sorted and filtered again
# for each size, before the first merge.
_SORTED_ONCE = (
    "        ranked = sorted(whole)\n"
    "        place = 0\n"
    "        while place < len(ranked):\n"
    "            size = ranked[place][0]\n"
    '            alike: "list[list[int]]" = []\n'
    "            while place < len(ranked) and ranked[place][0] == size:\n"
    "                alike += [runs[ranked[place][1]]]\n"
    "                place = place + 1\n"
    "            order += _clock_rotated(alike, count - wanted)\n"
)
_SORTED_FOR_EACH_SIZE = (
    "        for size in sorted({size for size, _key in whole}):\n"
    "            order += _clock_rotated(\n"
    "                [runs[key] for each, key in sorted(whole) if each == size], count - wanted\n"
    "            )\n"
)


def _lines_run(function: "object", *arguments: object) -> "tuple[object, int]":
    """What `function` returns, and how many lines it and everything it calls ran.

    Every line event of the call's own frame and of each frame opened under
    it is counted, a loop's line once per pass -- the growth measure of
    `tests/test_stage4_linear_work.py`, which no clock plays a part in.
    """
    code = function.__code__  # type: ignore[attr-defined]
    ran = [0]
    inside = [False]

    def below(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        return below

    def top(frame: object, event: str, argument: object) -> object:
        if event == "line":
            ran[0] += 1
        elif event == "return":
            inside[0] = False
        return top

    def calls(frame: object, event: str, argument: object) -> object:
        if event != "call":
            return None
        if frame.f_code is code and not inside[0]:  # type: ignore[attr-defined]
            inside[0] = True
            return top
        return below if inside[0] else None

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        answer = function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return answer, ran[0]


def test_put_back_work_grows_with_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3 as a growth measure, a count of lines and no clock: PUT
    BACK on Codex's family at `size` 40 and 120, nine times the rows (1,600
    and 14,400), each with one excess to restore. Its lines grow with the
    rows (41,995 and 370,675, 8.8 times); b3fb647's order, put back by one
    edit, grows as the rows' power one and a half (73,113 and 1,227,233, 16.8
    times) and is held to show it, so the measure is known to see the
    defect it guards against."""
    before = _edited(
        generation, _SORTED_ONCE, _SORTED_FOR_EACH_SIZE, "synthtwin._generation_review_put_back", monkeypatch
    )
    grown: "dict[str, float]" = {}
    for name, module in (("shipped", generation), ("b3fb647", before)):
        spent: "list[int]" = []
        for size in (40, 120):
            state, _runs = _put_back_state(size, module)
            rows = len(state.moved)
            count = module._weekday_count(state)
            _answer, ran = _lines_run(
                module._clock_count_put_back, state, 0, rows - 1, [False] * rows, count - 1, tuple(range(7))
            )
            assert module._weekday_count(state) == count - 1, (name, size)
            spent += [ran]
        grown[name] = spent[1] / spent[0]
    rows_grew = (120 * 120) / (40 * 40)
    assert grown["shipped"] <= 1.25 * rows_grew, grown
    assert grown["b3fb647"] >= 1.5 * rows_grew, grown

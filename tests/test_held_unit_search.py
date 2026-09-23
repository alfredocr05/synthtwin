"""The held-unit search answers as the walk does, without the walk (K-2B-14).

WHAT BROKE. The merge that lets a date column reach its published count
of different values (plan P4-D258) asks `generation._nearest_held_unit`
for the nearest unit some other rank already holds, of the run's own
standing. Its rule is a walk outward from the run's own unit ONE UNIT AT
A TIME, and on a column counted in seconds a unit is a second: the
nearest held unit of a moment's own standing lies hours or days away, so
every search stepped across tens of thousands of empty seconds. The
landing that brought the search (8e4306c) took `_partly(400, 0.9, 1)`
from 0.24 s to 96.9 s and `_partly(2000, 0.7, 2)` from 0.98 s to 103.6 s
(median of three generate runs each, on the parent c5d09d5 and on
8e4306c, one shared machine); nothing in the suite was slow enough to
notice, because every test that reached the path took its minutes
quietly.

WHAT THIS PINS, AND HOW. Time is not measured -- the machine is shared
and a wall clock is not a gate. Three things are counted instead:

- the ANSWER: over thousands of seeded cases the search gives exactly
  what a transcription of the walk gives, the transcription below being
  the rule as stated and as it stood at e53d5f4. The twin bytes follow
  from the answers, and `tests/test_twin_golden.py` and the oracle in
  `tests/test_generation_reference.py` hold them too;
- the OPERATIONS on a real column: every search must ask the table of
  held units whether a unit is held, so the number of those questions is
  a count every search incurs, whichever way it is written. On
  `_partly(2000, 0.7, 2)` at seed 4 the walk asked 190,524,866 of them
  (measured on e53d5f4 by the driver this file's counter was built
  from); the search asks 2,444, two for each of its 1,222 calls, because
  each call's first visit is its answer. The ceiling is set far below
  the walk and a little above that;
- the GROWTH: the walk's cost follows the SECONDS a column spans, the
  search's the units ranks hold. The same 2,000 rows spread over four
  times as many days give the walk farther to step between two held
  units of one standing: measured on e53d5f4, its questions a call went
  from 106,070 at 350 days to 225,884 at 1,400 (a ratio of 2.13), while
  the ROW count is no witness at all -- 1,000, 2,000 and 4,000 rows over
  700 days cost it 168.7, 190.5 and 202.7 million questions, flatter
  than the search's own 1,520, 2,444 and 3,786. The search asks two a
  call at both spans. The ratio is asserted at the two spans, and a
  returned walk fails it.

THE FREE-UNIT SEARCH WALKED THE SAME SECONDS. Where the restoration
SPLITS a shared unit, `generation._nearest_free_unit` looks for the
nearest unit no rank holds, of the run's own standing, by the same
one-unit walk; a run at midnight keeps its standing only on another
midnight, so it stepped 86,400 seconds for every held midnight it
passed. One stray time among 999 values at midnight took 450 s to
generate at seed 4. It now steps whole days where the run stands at
midnight, which visits exactly the candidates the walk could accept, in
the walk's order; its answers and its questions are pinned the same two
ways at the end of this file.
"""

import datetime
import hashlib
import json
import pathlib
import random
import re
import typing

import pytest

from synthtwin import contract, generation
from tests.test_stage2_round_trip import _round_trip
from tests.test_stage2_timestamp_spellings import _days, _partly


def _walk(
    facts: object,
    value: int,
    lowest: int,
    highest: int,
    day: int,
    step: int,
    unit: int,
    held: "dict[int, int]",
    spot: "dict[int, int]",
    widths: bool,
    word: str = "",
    flip: bool = False,
    skip: int = -1,
) -> "int | None":
    """The rule as stated: outward one unit at a time, earlier first.

    Transcribed from `_nearest_held_unit` as it stood at e53d5f4, and
    reading the same two standing functions from the module, so a test
    that replaces them replaces them for both.
    """
    counts = typing.cast(typing.Any, generation)._counts_into_width
    at_midnight = typing.cast(typing.Any, generation)._written_at_midnight
    away = 1
    while True:
        earlier = value - away * unit
        later = value + away * unit
        if earlier < lowest and later > highest:
            return None
        for candidate in (earlier, later):
            if candidate < lowest or candidate > highest:
                continue
            key = candidate // unit
            if key not in held or held[key] <= 0:
                continue
            if key not in spot:
                continue
            found = spot[key]
            if found < lowest or found > highest:
                continue
            if key == skip:
                continue
            if flip:
                if counts(facts, found // day, word) == counts(facts, value // day, word):
                    continue
                if day == 86400 and at_midnight(found, 0, step) != at_midnight(value, 0, step):
                    continue
                return found
            if widths and counts(facts, value // day, word) != counts(
                facts, found // day, word
            ):
                continue
            if day == 86400 and at_midnight(value, 0, step) != at_midnight(found, 0, step):
                continue
            return found
        away = away + 1


def _arbitrary_width(_facts: object, day_number: int, _word: str) -> bool:
    """A width kind that varies from day to day with no pattern a search sees."""
    return (day_number * 2654435761) % 7 < 3


def _instants(draw: random.Random, day: int, step: int) -> "tuple[int, int]":
    """A window of instants to place held units in: its first and its span."""
    if day == 1:
        return (730000 + draw.randrange(0, 50), draw.randrange(2, 400))
    if step == 60:
        # Minutes over up to three days, starting a little before a midnight.
        return (86400 * 19000 - 60 * draw.randrange(0, 600), 60 * draw.randrange(10, 4320))
    # Seconds over up to six hours around a midnight.
    return (86400 * 19000 - draw.randrange(0, 10800), draw.randrange(10, 21600))


def _case(draw: random.Random) -> "dict[str, typing.Any]":
    """One seeded search: held units, their instants, a run and its bounds."""
    day, step = draw.choice([(1, 1), (86400, 60), (86400, 1)])
    unit = step if day == 86400 else 1
    first, span = _instants(draw, day, step)
    places: "list[int]" = []
    for _ in range(draw.randrange(1, 40)):
        where = first + draw.randrange(0, span + 1)
        if day == 86400 and draw.random() < 0.4:
            where = where - where % 86400
        if unit > 1 and draw.random() < 0.7:
            where = where - where % unit
        places += [where]
    held: "dict[int, int]" = {}
    spot: "dict[int, int]" = {}
    for where in places:
        key = where // unit
        held[key] = (held[key] if key in held else 0) + 1
        spot[key] = where
    for key in sorted(held):
        roll = draw.random()
        if roll < 0.1:
            held[key] = 0
        elif roll < 0.15:
            del spot[key]
    value = draw.choice(places)
    if draw.random() < 0.1:
        value = first + draw.randrange(-span, 2 * span + 1)
    lowest = value - draw.randrange(0, span + 1)
    highest = value + draw.randrange(0, span + 1)
    if draw.random() < 0.05:
        lowest = value + draw.randrange(1, 5)
    flip = draw.random() < 0.3
    widths = flip or draw.random() < 0.6
    skip = -1
    if draw.random() < 0.3:
        skip = draw.choice(sorted(held))
    return {
        "value": value, "lowest": lowest, "highest": highest, "day": day,
        "step": step, "unit": unit, "held": held, "spot": spot,
        "widths": widths, "flip": flip, "skip": skip,
    }


def test_the_search_answers_as_the_walk_does(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every seeded case: the search's instant is the walk's, None where it is None.

    The standing reaches both searches through the module's own two
    functions; the width kind is replaced by one that changes from day to
    day, so a search that files a unit under the wrong kind is caught on
    the cases where the two kinds lie at different distances.
    """
    monkeypatch.setattr(generation, "_counts_into_width", _arbitrary_width)
    facts = typing.cast(contract.DatetimeFacts, None)
    draw = random.Random(20260918)
    reached = {"found": 0, "none": 0, "not_nearest": 0, "flip": 0, "skip": 0}
    for _ in range(3000):
        case = _case(draw)
        want = _walk(
            facts, case["value"], case["lowest"], case["highest"], case["day"],
            case["step"], case["unit"], case["held"], case["spot"],
            case["widths"], "", case["flip"], case["skip"],
        )
        order = generation._held_order(
            facts, case["spot"], case["day"], case["step"],
            case["widths"] or case["flip"],
        )
        got = generation._nearest_held_unit(
            facts, case["value"], case["lowest"], case["highest"], case["day"],
            case["step"], case["unit"], case["held"], case["spot"], order,
            case["widths"], "", case["flip"], case["skip"],
        )
        assert got == want, case
        if want is None:
            reached["none"] = reached["none"] + 1
            continue
        reached["found"] = reached["found"] + 1
        if case["flip"]:
            reached["flip"] = reached["flip"] + 1
        if case["skip"] >= 0:
            reached["skip"] = reached["skip"] + 1
        # The standing decided it: some held unit in the bounds lay nearer.
        anything = _walk(
            facts, case["value"], case["lowest"], case["highest"], 1, 1,
            case["unit"], case["held"], case["spot"], False,
        )
        if anything != want:
            reached["not_nearest"] = reached["not_nearest"] + 1
    # A check that cannot fail is a defect: the cases reach every branch.
    assert reached["found"] >= 1000, reached
    assert reached["none"] >= 300, reached
    assert reached["not_nearest"] >= 300, reached
    assert reached["flip"] >= 200, reached
    assert reached["skip"] >= 200, reached


# The search as the module defines it, taken once: a count wraps this and
# never a wrapper left by an earlier count.
_SEARCH = generation._nearest_held_unit


class _Counting(dict):  # type: ignore[type-arg]
    """The held-unit table, counting every question asked of it."""

    asked = 0

    def __contains__(self, key: object) -> bool:
        _Counting.asked = _Counting.asked + 1
        return dict.__contains__(self, key)

    def __getitem__(self, key: object) -> typing.Any:
        _Counting.asked = _Counting.asked + 1
        return dict.__getitem__(self, key)


def _counted(
    monkeypatch: pytest.MonkeyPatch,
) -> "dict[str, int]":
    """Count the calls of the search and the questions each asks of `held`."""
    tally = {"calls": 0}
    _Counting.asked = 0

    def counting(*args: typing.Any) -> "int | None":
        tally["calls"] = tally["calls"] + 1
        given = list(args)
        given[7] = _Counting(given[7])
        return _SEARCH(*given)

    monkeypatch.setattr(generation, "_nearest_held_unit", counting)
    return tally


def test_the_search_on_a_column_partly_at_midnight_asks_little(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """`_partly(2000, 0.7, 2)` at seed 4: a round trip, and a ceiling on the questions.

    The walk asked 190,524,866 questions of the held-unit table on this
    column; the search asks 2,444 over its 1,222 calls. The ceiling is two
    visits per call on average over at most one call per row -- four
    questions a call, 2,000 rows -- so 8,000, and it is more than twenty
    thousand times below the walk.
    """
    tally = _counted(monkeypatch)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "partly", _partly(2000, 0.7, 2), seed="4"
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert len(written) == 2000
    assert first["n_distinct"] == second["n_distinct"]
    assert 0 < tally["calls"] <= 2000, tally
    assert _Counting.asked <= 4 * tally["calls"], (_Counting.asked, tally)
    assert _Counting.asked <= 8000, _Counting.asked


def _asked_per_call(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, days: int
) -> float:
    """Questions per call of the search, generating 2,000 rows over ``days`` days."""
    tally = _counted(monkeypatch)
    _first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / f"days-{days}", _partly(2000, 0.7, 2, days=days), seed="4"
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert tally["calls"] > 0
    return _Counting.asked / tally["calls"]


def test_the_search_grows_with_the_units_held_not_the_seconds_spanned(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """2,000 rows over 350 days and over 1,400: the questions a call asks hold.

    The walk steps across every second between a run and the held unit
    it answers with, so spreading the same rows over four times the days
    took its questions a call from 106,070 to 225,884, a ratio of 2.13;
    the search visits held units only, and asks two a call at both
    spans, a ratio of 1.00. The line is drawn at 1.5, midway between the
    two on a ratio's own scale (the square root of 2.13 is 1.46), so a
    search that spends its questions on the seconds again fails it.
    """
    narrow = _asked_per_call(tmp_path, monkeypatch, 350)
    wide = _asked_per_call(tmp_path, monkeypatch, 1400)
    assert wide / narrow <= 1.5, (narrow, wide)


# ---------------------------------------------------------------------------
# The free-unit search, which walked the same seconds to find a midnight.


def _free_walk(
    facts: object,
    value: int,
    lowest: int,
    highest: int,
    day: int,
    step: int,
    unit: int,
    held: "dict[int, int]",
    widths: bool,
    word: str = "",
) -> "int | None":
    """The rule as stated: outward one unit at a time, earlier first.

    Transcribed from `_nearest_free_unit` as it stood at e53d5f4, with
    `_same_standing` written out and reading the module's two standing
    functions.
    """
    counts = typing.cast(typing.Any, generation)._counts_into_width
    at_midnight = typing.cast(typing.Any, generation)._written_at_midnight
    away = 1
    while True:
        earlier = value - away * unit
        later = value + away * unit
        if earlier < lowest and later > highest:
            return None
        for candidate in (earlier, later):
            if candidate < lowest or candidate > highest:
                continue
            key = candidate // unit
            if key in held and held[key] > 0:
                continue
            if widths and counts(facts, value // day, word) != counts(
                facts, candidate // day, word
            ):
                continue
            if day == 86400 and at_midnight(value, 0, step) != at_midnight(
                candidate, 0, step
            ):
                continue
            return candidate
        away = away + 1


def _free_case(draw: random.Random) -> "dict[str, typing.Any]":
    """One seeded free search: most days held at midnight, a run, its bounds."""
    day, step, days = draw.choice([(86400, 60, 20), (86400, 1, 2), (1, 1, 0)])
    unit = step if day == 86400 else 1
    held: "dict[int, int]" = {}
    places: "list[int]" = []
    day_starts: "list[int]" = []
    if day == 1:
        first = 730000 + draw.randrange(0, 50)
        span = draw.randrange(2, 200)
        for where in range(first, first + span + 1):
            if draw.random() < 0.8:
                places += [where]
    else:
        first = 86400 * 19000
        span = 86400 * draw.randrange(1, days + 1)
        for midnight in range(first, first + span + 1, 86400):
            if draw.random() < 0.8:
                day_starts += [midnight + draw.randrange(0, step)]
        places += day_starts
        for _ in range(draw.randrange(0, 30)):
            places += [first + draw.randrange(0, span + 1)]
    if not places:
        places = [first]
    for where in places:
        key = where // unit
        held[key] = (held[key] if key in held else 0) + 1
        if draw.random() < 0.05:
            held[key] = 0
    value = draw.choice(places)
    if day_starts and draw.random() < 0.7:
        value = draw.choice(day_starts)
    lowest = value - draw.randrange(0, span + 1)
    highest = value + draw.randrange(0, span + 1)
    return {
        "value": value, "lowest": lowest, "highest": highest, "day": day,
        "step": step, "unit": unit, "held": held,
        "widths": draw.random() < 0.6,
    }


def test_the_free_search_answers_as_the_walk_does(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every seeded case: the free instant is the walk's, None where it is None.

    Most days are held at midnight, so a run at midnight is often
    answered days away -- the case the day-at-a-time search exists for --
    and the width kind changes from day to day, so a day skipped or taken
    out of order is caught.
    """
    monkeypatch.setattr(generation, "_counts_into_width", _arbitrary_width)
    facts = typing.cast(contract.DatetimeFacts, None)
    draw = random.Random(20260919)
    reached = {"found": 0, "none": 0, "midnight_days_away": 0}
    for _ in range(600):
        case = _free_case(draw)
        arguments = (
            facts, case["value"], case["lowest"], case["highest"], case["day"],
            case["step"], case["unit"], case["held"], case["widths"], "",
        )
        want = _free_walk(*arguments)
        got = generation._nearest_free_unit(*arguments)
        assert got == want, case
        if want is None:
            reached["none"] = reached["none"] + 1
            continue
        reached["found"] = reached["found"] + 1
        if (
            case["day"] == 86400
            and generation._written_at_midnight(case["value"], 0, case["step"])
            and abs(want - case["value"]) >= 2 * 86400
        ):
            reached["midnight_days_away"] = reached["midnight_days_away"] + 1
    assert reached["found"] >= 200, reached
    assert reached["none"] >= 60, reached
    assert reached["midnight_days_away"] >= 35, reached


def test_the_free_search_is_not_asked_at_all_for_one_stray_time(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """999 values at midnight and one stray time, seed 4: nothing to search.

    The shape `tests/test_stage2_timestamp_spellings.py` holds at a stray
    time among values at midnight; at seed 4 the restoration splits
    values at midnight onto free midnight units, and the walk stepped
    every second between them: 256,954,962 questions of the held-unit table over 763
    calls, measured on e53d5f4, and 450 s to generate on the shared
    machine. It was slow before the held-unit search arrived (164.8 s at
    c5d09d5); the free search it uses came with 4c430b0. The day-at-a-
    time search asks 4,330 questions over the same 763 calls, a ceiling
    of ten a call over at most one call per row, 10,000.

    **AND THE SEARCH IS NOT REACHED ON THIS COLUMN ANY MORE** (stage 3,
    plan P4-D328), which is asserted here rather than left as a ceiling
    nothing tests. G12.4 now places a run whose gap must hold a midnight
    into a gap that can hold one before any split asks where a free unit
    is, so the restoration finds nothing to search for: measured on
    2026-09-22, 0 calls and 0 questions, where e53d5f4 made 763 calls.
    A regression that puts the splitting back makes a call here and
    turns this red, and the CEILING the file exists for is measured on
    the month-first column below, which still reaches the search 2,193
    times. The figures above are kept because the searches' own
    docstrings cite them and
    `test_the_figures_the_searches_cite_are_the_ones_counted_here`
    holds this file to carrying every one.
    """
    tally = {"calls": 0}
    _Counting.asked = 0
    search = generation._nearest_free_unit

    def counting(*args: typing.Any) -> "int | None":
        tally["calls"] = tally["calls"] + 1
        given = list(args)
        given[7] = _Counting(given[7])
        return search(*given)

    monkeypatch.setattr(generation, "_nearest_free_unit", counting)
    cells = _days(999, " 00:00:00", 3) + ["2024-05-05 14:30:00"]
    _first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "stray", cells, seed="4"
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert len(written) == 1000
    assert tally["calls"] == 0, tally
    assert _Counting.asked == 0, _Counting.asked


# ---------------------------------------------------------------------------
# A gap with no free day, searched once a pass for each width kind.

# The gap's name as the module defines it, taken once.
_FULL_GAP = generation._full_gap


def _gap_case(draw: random.Random) -> "dict[str, typing.Any]":
    """One seeded restoration pass that must split ranks: gaps, ranks, a want.

    On a column of days each gap is filled but for a few free days, and a
    gap may leave free only days of one width kind, so it is full for the
    other kind and not for its own. On a column of minutes each gap holds
    one midnight, held twice and first in rank order, with free minutes
    after it: full for a run at midnight, open for every other run.
    """
    day, step = draw.choice([(1, 1), (1, 1), (86400, 60)])
    unit = step if day == 86400 else 1
    moved: "list[int]" = []
    lows: "list[int]" = []
    highs: "list[int]" = []
    start = 730000 + draw.randrange(0, 50) if day == 1 else 86400 * 19000
    for _gap in range(draw.randrange(1, 5)):
        if day == 1:
            low = start
            high = low + draw.randrange(3, 40)
            mode = draw.randrange(0, 3)
            kind = draw.random() < 0.5
            places: "list[int]" = []
            for where in range(low, high + 1):
                open_day = mode == 2 and draw.random() < 0.2
                if mode == 1 and _arbitrary_width(None, where, "") == kind:
                    open_day = draw.random() < 0.3
                if not open_day:
                    places += [where]
            if not places:
                places = [low]
            ranks = sorted(places + [draw.choice(places) for _ in range(draw.randrange(1, 12))])
            start = high + 1
        else:
            midnight = start + 86400 * draw.randrange(1, 3)
            low = midnight - 60 * draw.randrange(0, 30)
            high = midnight + 60 * draw.randrange(2, 200)
            others = [
                midnight + 60 * draw.randrange(1, (high - midnight) // 60 + 1)
                for _ in range(draw.randrange(1, 10))
            ]
            ranks = sorted([midnight, midnight] + others + [draw.choice(others)])
            start = midnight
        moved += ranks
        lows += [low for _ in ranks]
        highs += [high for _ in ranks]
    pinned = [draw.random() < 0.1 for _ in moved]
    count = len({value // unit for value in moved})
    return {
        "moved": moved, "pinned": pinned, "lows": lows, "highs": highs,
        "day": day, "step": step, "wanted": count + draw.randrange(1, 6),
        "widths": draw.random() < 0.7,
    }


def _pass(case: "dict[str, typing.Any]") -> "tuple[bool, list[int]]":
    """Run one restoration pass on a copy of the case; what it changed and left."""
    moved = list(case["moved"])
    changed = generation._distinct_reached(
        typing.cast(contract.DatetimeFacts, None), moved, list(case["pinned"]),
        case["lows"], case["highs"], case["day"], case["step"], case["wanted"],
        case["widths"],
    )
    return changed, moved


def test_a_full_gap_skipped_leaves_the_pass_as_every_search_would(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every seeded pass ends where it ends when every shared rank is searched.

    The rule is a free search for every shared rank; a gap found full is
    not searched again only for a rank whose answer is the same None
    (`generation._full_gap`). The reference names no gap, so it searches
    every rank. Cases reach a gap full for one standing and open for
    another -- by width kind on a column of days, by midnight on one of
    minutes -- where a key that forgot the standing would skip a rank that
    had somewhere to go.
    """
    monkeypatch.setattr(generation, "_counts_into_width", _arbitrary_width)
    search = generation._nearest_free_unit
    draw = random.Random(20260920)
    reached = {"skipped": 0, "standing_decided": 0, "changed": 0}
    for _ in range(1500):
        case = _gap_case(draw)
        answers: "dict[tuple[int, int], dict[tuple[bool, bool], bool]]" = {}
        tally = {"calls": 0}

        def recording(*args: typing.Any) -> "int | None":
            tally["calls"] = tally["calls"] + 1
            found = search(*args)
            standing = (
                bool(args[8]) and _arbitrary_width(None, args[1] // args[4], ""),
                args[4] == 86400 and generation._written_at_midnight(args[1], 0, args[5]),
            )
            bounds = (args[2], args[3])
            if bounds not in answers:
                answers[bounds] = {}
            answers[bounds][standing] = found is None
            return found

        monkeypatch.setattr(generation, "_nearest_free_unit", recording)
        monkeypatch.setattr(generation, "_full_gap", lambda *_args: None)
        want = _pass(case)
        every = tally["calls"]
        monkeypatch.setattr(generation, "_full_gap", _FULL_GAP)
        tally["calls"] = 0
        got = _pass(case)
        assert got == want, case
        if tally["calls"] < every:
            reached["skipped"] = reached["skipped"] + 1
        for seen in answers.values():
            if True in seen.values() and False in seen.values():
                reached["standing_decided"] = reached["standing_decided"] + 1
                break
        if want[0]:
            reached["changed"] = reached["changed"] + 1
    monkeypatch.setattr(generation, "_nearest_free_unit", search)
    assert reached["skipped"] >= 300, reached
    assert reached["standing_decided"] >= 300, reached
    assert reached["changed"] >= 500, reached



def _month_first(rows: int, seed: int, days: int) -> "list[str]":
    """Dates written m/d/Y without padding, drawn over ``days`` days."""
    draw = random.Random(seed)
    first = datetime.date(2020, 1, 1)
    cells: "list[str]" = []
    for _ in range(rows):
        when = first + datetime.timedelta(days=draw.randrange(days))
        cells += [f"{when.month}/{when.day}/{when.year}"]
    return cells


def test_a_full_gap_of_a_width_census_is_searched_once_a_pass(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """4,000 m/d/Y dates over 800 days, seed 4: round trip, and no None asked twice.

    THE SKEPTIC'S LEFTOVER. The memo of full gaps was kept only where no
    width census was read, so on a column of days with one every shared
    rank of a full gap searched the whole gap again: 20,000 such dates
    over 2,000 days searched 19,989 times and asked the held-unit table
    13,445,643 questions (the same on e53d5f4); with the gap and its kind
    as the key, 3,008 times, 9 of them None, asking 973,675. On this
    column the free search was called 3,979 times, 1,792 of them None,
    and asked 748,633 questions; with the memo it was called 2,195
    times, 8 of them None, asking 299,675, and since the tail rule it is
    called 2,193 times asking 299,389. The rule this asserts is exact:
    within one
    pass, no gap is found full twice for one width kind -- the days held
    only grow while ranks split, so a gap found full stays full, and a
    rank searched again because an earlier split took its day is
    answered from what was found. Keeping the memo out of that second
    search leaves 16 None here, 8 of them a gap found full again.

    **AND THE CEILING IS MEASURED HERE SINCE STAGE 3** (plan P4-D328).
    It stood on the one-stray-time column above, which the tail rule's
    own placement now builds without asking the search at all; this
    column still asks it, so the ceiling moved to the shape that reaches
    it. Measured on 2026-09-22: 2,193 calls and 299,389 questions of the
    held-unit table, where the same column asked 748,633 before the
    memo, so the ceiling is half a million questions over at most one
    call a row. The twin's bytes moved with the tail rule -- its ranks
    are drawn inside the two tail boundaries now -- and the digest below
    is the one this landing measured.

    **AND THEY MOVED AGAIN WITH PLAN P4-D342**, because the DESCRIPTION
    moved first. This column's low tail listed `2020-01-01` and
    `2020-01-02` -- and `2020-01-01` is the column's own earliest date,
    held by 4 of its 4,000 rows, four being under the floor of eleven.
    797 different dates over 4,000 rows is a fine grid, not a bounded
    scale, so the tail publishes its shape now and lists nothing. The
    two assertions below say that in the description's own terms, so
    the digest is not the only thing holding this; the digest follows
    from them, and from nothing in the generator, which this pass did
    not touch.
    """
    search = generation._nearest_free_unit
    reached = generation._distinct_reached
    passes = {"now": 0, "none": 0, "again": 0}
    tally = {"calls": 0}
    _Counting.asked = 0
    seen: "dict[tuple[int, int, int, bool], bool]" = {}

    def counting_pass(*args: typing.Any) -> bool:
        passes["now"] = passes["now"] + 1
        return reached(*args)

    def counting(*args: typing.Any) -> "int | None":
        tally["calls"] = tally["calls"] + 1
        given = list(args)
        given[7] = _Counting(given[7])
        found = search(*given)
        if found is None:
            kind = bool(args[8]) and generation._counts_into_width(
                args[0], args[1] // args[4], args[9]
            )
            key = (passes["now"], args[2], args[3], kind)
            passes["none"] = passes["none"] + 1
            if key in seen:
                passes["again"] = passes["again"] + 1
            seen[key] = True
        return found

    monkeypatch.setattr(generation, "_distinct_reached", counting_pass)
    monkeypatch.setattr(generation, "_nearest_free_unit", counting)
    folder = tmp_path / "month-first"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, _month_first(4000, 7, 800), seed="4"
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert len(written) == 4000
    assert first["n_distinct"] == second["n_distinct"]
    assert passes["none"] >= 1, passes
    assert passes["again"] == 0, passes
    assert 0 < tally["calls"] <= 4000, tally
    assert _Counting.asked <= 500000, (_Counting.asked, tally)
    # THE RULE THE BYTES FOLLOW FROM (plan P4-D342), asserted before the
    # digest that follows from it: a fine-grid column lists no tail
    # value, so its earliest date is named nowhere.
    assert first["low_tail"]["values"] is None
    assert first["high_tail"]["values"] is None
    earliest = min(
        f"{int(cell.split('/')[2]):04d}-{int(cell.split('/')[0]):02d}-"
        f"{int(cell.split('/')[1]):02d}"
        for cell in _month_first(4000, 7, 800)
    )
    assert earliest not in json.dumps(first)
    twin = (folder / "real-twin.csv").read_bytes()
    assert hashlib.sha256(twin).hexdigest() == _MONTH_FIRST_TWIN


# sha256 of the twin this landing writes for `_month_first(4000, 7, 800)`
# at seed 4. It was e53d5f4's until the tail rule (plan P4-D328) drew the
# ranks inside the two published boundaries, and 9e51fd6's until plan
# P4-D342 stopped this column's low tail listing `2020-01-01`, its own
# earliest date, held by 4 of its 4,000 rows.
#
# AND IT MOVED AGAIN FOR PLAN P4-D346, read before it was written: this
# column's two published pairs SETTLED their tails to one multiset each
# -- the reader's own arithmetic, with the calendar's edge and the
# column's all-different remark -- so both boundaries move inward until
# a second multiset fits. Low `2020-01-03` to `2020-01-04` and 13 rows
# to 18; high `2022-03-07` to `2022-03-06` and 13 rows to 20. That is
# five and seven more rows withheld of four thousand, and it is what
# `edge_pinned` reaching nought costs on a column this size. Every
# assertion above this digest still holds: neither tail lists, the
# column's earliest date is named nowhere, and both files validate.
_MONTH_FIRST_TWIN = "8e4f04daadb2e009ed3e87bf6a00065ecdf77d9323d231342569a57a6e23aa44"


def test_the_figures_the_searches_cite_are_the_ones_counted_here() -> None:
    """Every measured figure a search's docstring cites stands in this file.

    The skeptic found `_held_order` citing a pair of generate times that
    no run had produced, and `_nearest_free_unit` cited a profiled time
    no log held. A figure with a thousands comma, a decimal point, or a
    unit of seconds is a measurement, and each is stated here beside the
    test that counts it -- so this file must never quote the old pair.
    """
    text = pathlib.Path(__file__).read_text(encoding="utf-8")
    stated = set(re.findall(r"\d{1,3}(?:,\d{3})+|\d+\.\d+|\d+(?= s\b)", text))
    cited: "list[str]" = []
    for function in (
        generation._held_order, generation._nearest_held_unit,
        generation._nearest_free_unit, generation._full_gap,
    ):
        doc = function.__doc__ if function.__doc__ else ""
        cited += re.findall(r"\d{1,3}(?:,\d{3})+|\d+\.\d+|\d+(?= s\b)", doc)
    assert len(cited) >= 8, cited
    assert [figure for figure in cited if figure not in stated] == []

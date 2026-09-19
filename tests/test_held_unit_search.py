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

import pathlib
import random
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


def test_the_free_search_on_one_stray_time_among_values_at_midnight_asks_little(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """999 values at midnight and one stray time, seed 4: round trip, ceiling.

    The shape `tests/test_stage2_timestamp_spellings.py` holds at a stray
    time among values at midnight; at seed 4 the restoration splits
    values at midnight onto free midnight units, and the walk stepped
    every second between them: 256,954,962 questions of the held-unit table over 763
    calls, measured on e53d5f4, and 450 s to generate on the shared
    machine. It was slow before the held-unit search arrived (164.8 s at
    c5d09d5); the free search it uses came with 4c430b0. The day-at-a-
    time search asks 4,330 questions over the same 763 calls. The
    ceiling is ten a call over at most one call per row, 10,000.
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
    assert 0 < tally["calls"] <= 1000, tally
    assert _Counting.asked <= 10 * tally["calls"], (_Counting.asked, tally)
    assert _Counting.asked <= 10000, _Counting.asked

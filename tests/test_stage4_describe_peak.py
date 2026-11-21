"""P4-D463 (lane SR2a): the plain describe's step between a date column's two descriptions keeps nothing a row.

THE DEFECT (measured on c47a6aee). Beside a person column, a column of dates
or times one of whose published points few people hold is walked down its
ladder and described again at a coarser grain (plan P4-D417, lane PS). The
walk kept, for every row of every rung, the row's moment, a key text, a
one-key tuple, the bucket's start and a list of its holders: 650 to 740
traced bytes a row for stamps to the second at 20,000 rows, and, at 500,000
rows of K-S4-02's invented mixed table, 231 MB of footprint over the end of
the stamp's first description -- the step that carried the plain describe's
projected peak at 2,000,000 rows.

THE RULE. Nothing a row outlives one pass: whether a cell reads as a moment
is one byte a row, each moment one whole number (its second and its row)
sorted once, and every rung is counted in one walk of that order, each
bucket counted in people as the walk passes it and let go before the next.
Every rung is a second or coarser, so the second a moment falls in decides
its bucket at every rung. The record, the thin rungs, the unread cells'
count, the padding and every coarse cell are the walk's as c47a6aee wrote
them (`stage4_as_built.GRAIN_WALK`): every description is the bytes it was.

THE GATE: the walk answers as it did on adversarial columns -- offsets on the
shared clock and on their own, unread and absent cells, twelve-hour stamps,
clock times, counted dates, moments before 1678 and after 2262 (past a
64-bit count of nanoseconds), buckets at the floor and one under it, two
subject columns, one of few people attached or not, the rows as holders,
floors 1 to 20, no row at all -- and the traced bytes a row the walk holds
above its cells at 20,000 rows, its memos held as at 2,000,000 rows, stay
under each bound.

REPAIR 1 (the lane's two reviews): the floor's edge one case each way; the
count in people counted by code in one pass, each different cell read once
and nothing kept a row, and the present rows' count ended at the floor --
CPU first, each asserted as c47a6aee answered it on sixty columns drawn at
random, and its work counted (cells read, `_attached` asked, cells passed).

REPAIR 2 (Codex's review of the lane, items 1 and 2, and its verify): the
count in people counts one subject column at a time, in c47a6aee's order,
ending where the first finds a key few hold, as c47a6aee's did; many
published levels beside several subject columns hold one column's subjects
at once, and read no more rows times subject columns than c47a6aee read;
the number of each row past the memo is kept, where another column follows,
and read back; the second of two subject columns is read through its own
subjects, in the count and in the present rows' count; and the step back's
coarse cells past the 65,536 different texts it shares are the bytes they
were, each a text of its own.
"""

from __future__ import annotations

import datetime
import gc
import random
import tracemalloc

import pytest

import stage4_as_built
from synthtwin import date_counts, grains, profile, taxonomy

_OLD_WALK, _OLD_NAMES = stage4_as_built.compiled(profile, stage4_as_built.GRAIN_WALK, "_grain_walk")
_OLD_CELLS_AT = _OLD_NAMES["_cells_at"]
_OLD_COUNTED, _COUNTED_NAMES = stage4_as_built.compiled(
    profile, stage4_as_built.COUNTED_IN_SUBJECTS, "_counted_in_subjects"
)
_OLD_PRESENT, _PRESENT_NAMES = stage4_as_built.compiled(profile, stage4_as_built.PRESENT_TOO_FEW, "_present_too_few")
_SETTINGS = taxonomy.Settings()

_STAMP = grains.Reading(grains.STAMP, "iso-datetime")
_TWELVE = grains.Reading(grains.STAMP, "month-first-datetime")
_DATE = grains.Reading(grains.DATE, "iso-date")
_CLOCK = grains.Reading(grains.CLOCK, "hh-mm")
_COUNTED = grains.Reading(grains.COUNTED, "days-since-1970", date_counts.POINT)
_OFFSETS = ("Z", "+05:00", "-08:00", "+01:00", "+05:30", "")


def _people(draw: random.Random, rows: int, people: int) -> "list[str]":
    """A person key a row, `P` and figures, about ``rows`` / ``people`` rows a person."""
    return [f"P{draw.randrange(people):05d}" for _ in range(rows)]


def _stamps(draw: random.Random, rows: int, form: str, start: datetime.datetime, seconds: int) -> "list[str]":
    """Stamps written ``form``, each at a second drawn over ``seconds``, a few blank or unread."""
    made: "list[str]" = []
    for _ in range(rows):
        roll = draw.random()
        if roll < 0.01:
            made += [""]
        elif roll < 0.015:
            made += ["unknown"]
        else:
            made += [(start + datetime.timedelta(seconds=draw.randrange(seconds))).strftime(form)]
    return made


def _case(name: str) -> "tuple[list[str], grains.Reading, list[list[str]], list[bool], int, frozenset[str], bool]":
    """One adversarial column, its reading, its subject columns, the floor, its absent spellings and the clock."""
    draw = random.Random(name)
    start = datetime.datetime(2019, 1, 1)
    rows = 3_000
    people = _people(draw, rows, 750)
    if name.startswith("seconds"):
        floor = int(name.split("-")[1]) if "-" in name else 11
        return _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 2 * 365 * 86_400), _STAMP, [people], [True], floor, frozenset(), False
    if name.startswith("offsets") or name == "rows-utc":
        cells = [
            f"{(start + datetime.timedelta(seconds=draw.randrange(400 * 86_400))).strftime('%Y-%m-%dT%H:%M:%S')}{draw.choice(_OFFSETS)}"
            for _ in range(rows)
        ]
        if name == "rows-utc":
            return cells, _STAMP, [], [], 3, frozenset(), True
        return cells, _STAMP, [people], [True], 3, frozenset(), name == "offsets-utc"
    if name == "twelve":
        return _stamps(draw, rows, "%m/%d/%Y %I:%M %p", start, 3 * 365 * 86_400), _TWELVE, [people], [True], 11, frozenset(), False
    if name == "ties":
        minutes = [start + datetime.timedelta(minutes=draw.randrange(90 * 24 * 60)) for _ in range(150)]
        cells = [draw.choice(minutes).strftime("%Y-%m-%dT%H:%M:00") for _ in range(rows)]
        few = _people(draw, rows, 200)
        return cells, _STAMP, [few], [True], 3, frozenset(), False
    if name == "dates-absent":
        cells = [
            "1900-01-01" if draw.random() < 0.02 else (start + datetime.timedelta(days=draw.randrange(900))).strftime("%Y-%m-%d")
            for _ in range(rows)
        ]
        return cells, _DATE, [people], [True], 11, frozenset({"1900-01-01"}), False
    if name == "clock":
        cells = [f"{draw.randrange(24):02d}:{draw.randrange(60):02d}" for _ in range(rows)]
        return cells, _CLOCK, [people], [True], 11, frozenset(), False
    if name == "counted":
        cells = [f"{17_900 + draw.randrange(900)}.{draw.randrange(100):02d}" for _ in range(rows)]
        return cells, _COUNTED, [people], [True], 11, frozenset(), False
    if name == "far":
        cells = [
            f"{draw.choice((1650, 1677, 2263, 2450))}-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}T"
            f"{draw.randrange(24):02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}"
            for _ in range(rows)
        ]
        return cells, _STAMP, [people], [True], 3, frozenset(), False
    if name == "held":
        families = [f"F{draw.randrange(6)}" for _ in range(rows)]
        days = {family: f"2020-0{place + 1}-1{place}" for place, family in enumerate(sorted(set(families)))}
        return [days[family] for family in families], _DATE, [people, families], [True, False], 11, frozenset(), False
    if name == "two-subjects":
        visits = [f"V{draw.randrange(1_500):05d}" for _ in range(rows)]
        cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 30 * 86_400)
        return cells, _STAMP, [people, visits], [True, True], 5, frozenset(), False
    if name == "few-apart":
        wards = [f"W{draw.randrange(5)}" for _ in range(rows)]
        cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 365 * 86_400)
        return cells, _STAMP, [people, wards], [True, False], 11, frozenset(), False
    if name.startswith("rows"):
        # Each row its own holder (`rows_hold`): alone, beside a ward column of
        # five values attached to nothing, or beside families that hold it.
        cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 200 * 86_400)
        if name == "rows-beside-few":
            return cells, _STAMP, [[f"W{draw.randrange(5)}" for _ in range(rows)]], [False], 11, frozenset(), False
        if name == "rows-held":
            families = [f"F{draw.randrange(6)}" for _ in range(rows)]
            days = {family: f"2020-0{place + 1}-1{place}" for place, family in enumerate(sorted(set(families)))}
            return [days[family] for family in families], _DATE, [families], [False], 11, frozenset(), False
        return cells, _STAMP, [], [], 11, frozenset(), False
    if name == "nobody-counted":
        wards = [f"W{draw.randrange(5)}" for _ in range(rows)]
        return _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 365 * 86_400), _STAMP, [wards], [False], 11, frozenset(), False
    if name.startswith("edge"):
        # Five days: 30, 10 (or 11), 11, 12 and 30 different people, one row each.
        middle = 11 if name == "edge-held" else 10
        cells: "list[str]" = []
        keys: "list[str]" = []
        for day, count in enumerate((30, middle, 11, 12, 30)):
            for person in range(count):
                cells += [f"2021-03-0{day + 1}"]
                keys += [f"Q{day}-{person}"]
        return cells, _DATE, [keys], [True], 11, frozenset(), False
    if name == "empty":
        return [], _STAMP, [[]], [True], 11, frozenset(), False
    if name == "boundaries":
        # Each stamp on a bucket's first second or its last, at every rung from the year to the minute.
        edges = [datetime.datetime(2020, month, 1) for month in range(1, 13)] + [datetime.datetime(2021, 1, 1)]
        cells = []
        for _ in range(rows):
            edge = draw.choice(edges) + datetime.timedelta(hours=draw.randrange(3), minutes=draw.randrange(2))
            cells += [(edge - datetime.timedelta(seconds=draw.randrange(2))).strftime("%Y-%m-%dT%H:%M:%S")]
        return cells, _STAMP, [_people(draw, rows, 300)], [True], 5, frozenset(), False
    if name == "one-moment":
        return ["2022-02-02T02:02:02"] * rows, _STAMP, [_people(draw, rows, 500)], [True], 11, frozenset(), False
    if name == "counted-before-1970":
        cells = [f"-{draw.randrange(1, 400)}.{draw.randrange(100):02d}" for _ in range(rows)]
        return cells, _COUNTED, [people], [True], 3, frozenset(), False
    # Stamps, and `later` written on five rows of three people: an unread shape few people hold.
    cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 365 * 86_400)
    for place in range(5):
        cells[place] = "later"
        people[place] = f"P{place % 3:05d}"
    return cells, _STAMP, [people], [True], 11, frozenset(), False


_CASES = [
    "seconds", "seconds-1", "seconds-2", "seconds-20", "offsets-utc", "offsets-own", "twelve", "ties",
    "dates-absent", "clock", "counted", "far", "held", "two-subjects", "few-apart", "rows", "rows-beside-few",
    "rows-held", "rows-utc", "nobody-counted",
    "edge-thin", "edge-held", "empty", "unread", "boundaries", "one-moment", "counted-before-1970",
]
# The step back's coarse cells are compared on these (each cell's coarse text costs a quarter of a millisecond).
_COARSE_CASES = ("seconds", "offsets-utc", "dates-absent", "clock", "counted", "far", "rows", "boundaries", "counted-before-1970")


@pytest.mark.parametrize("name", _CASES)
def test_the_walk_answers_as_it_did(name: str) -> None:
    """Each row its own holder was a subject column of a text a row (`rows_as_holders`), now the walk's own count."""
    cells, reading, subjects, enough, floor, absent, at_utc = _case(name)
    rows_hold = name.startswith("rows")
    holders = [profile.rows_as_holders(len(cells))] if rows_hold else []
    present = sum(1 for cell in cells if cell.strip() and cell not in absent)
    old = _OLD_WALK(  # type: ignore[operator]
        cells, present, reading, subjects + holders, enough + [True] * len(holders), floor, absent, at_utc
    )
    new = profile._grain_walk(cells, present, reading, subjects, enough, floor, absent, at_utc, rows_hold)
    assert new.grain == old.grain, name
    assert new.thin == old.thin, name
    assert (new.unread_thin, new.padded) == (old.unread_thin, old.padded), name
    assert bytes(new.read) == bytes([0 if moment is None else 1 for moment in old.moments]), name
    if name in _COARSE_CASES and new.grain.spans:
        span = new.grain.spans[len(new.grain.spans) - 1]
        assert profile._cells_at(cells, new, span) == _OLD_CELLS_AT(cells, old, span), name  # type: ignore[operator]


def test_the_cases_reach_what_they_were_made_for() -> None:
    """The adversarial cases are not vacuous: a span, a thin rung, an unread count, a held column, an offset kept."""
    reached: "dict[str, profile._Walked]" = {}
    for name in ("seconds", "offsets-utc", "ties", "held", "edge-thin", "edge-held", "unread"):
        cells, reading, subjects, enough, floor, absent, at_utc = _case(name)
        present = sum(1 for cell in cells if cell.strip() and cell not in absent)
        reached[name] = profile._grain_walk(cells, present, reading, subjects, enough, floor, absent, at_utc)
    assert reached["seconds"].grain.spans and reached["seconds"].grain.rung != grains.HELD
    assert len(reached["ties"].grain.spans) > len(reached["seconds"].grain.spans)
    assert reached["held"].grain.rung == grains.HELD and reached["held"].thin == {}
    assert reached["edge-thin"].thin[grains.DAY] and not reached["edge-held"].thin[grains.DAY]
    assert reached["unread"].unread_thin
    assert reached["offsets-utc"].grain.spans


def _both_walks(
    cells: "list[str]",
    reading: grains.Reading,
    subjects: "list[list[str]]",
    floor: int,
    at_utc: bool = False,
    rows_hold: bool = False,
) -> profile._Walked:
    """The walk of a column, asserted to answer as c47a6aee's (`stage4_as_built.GRAIN_WALK`) in every field."""
    holders = [profile.rows_as_holders(len(cells))] if rows_hold else []
    enough = [True] * len(subjects)
    present = sum(1 for cell in cells if cell.strip())
    old = _OLD_WALK(  # type: ignore[operator]
        cells, present, reading, subjects + holders, enough + [True] * len(holders), floor, frozenset(), at_utc
    )
    new = profile._grain_walk(cells, present, reading, subjects, enough, floor, frozenset(), at_utc, rows_hold)
    assert new.grain == old.grain
    assert new.thin == old.thin
    assert (new.unread_thin, new.padded) == (old.unread_thin, old.padded)
    assert bytes(new.read) == bytes([0 if moment is None else 1 for moment in old.moments])
    return new


# THE FLOOR'S EDGE, ONE CASE EACH WAY (lane SR2a's repair 1, skeptic 1's items 1
# and 2): a count of floor - 1 is held back and a count of floor is not, counted
# in people where people are counted and in rows where each row is its own
# holder; each case is asserted as written and as c47a6aee answered it.
@pytest.mark.parametrize(("holders", "thin"), [(10, True), (11, False)])
def test_a_day_inside_the_span_of_more_rows_than_the_floor_counts_its_people(holders: int, thin: bool) -> None:
    """Forty days of stamps, a hundred people a day; the twentieth holds twelve rows of ``holders`` people.

    Its twelve rows reach the floor, so the people decide: ten make the day
    thin (a day whose count ten people hold, strictly inside the span), eleven
    do not.
    """
    start = datetime.datetime(2021, 1, 1)
    cells: "list[str]" = []
    keys: "list[str]" = []
    for day in range(40):
        for row in range(12 if day == 20 else 100):
            cells += [(start + datetime.timedelta(days=day, seconds=600 * row + 7)).strftime("%Y-%m-%dT%H:%M:%S")]
            keys += [f"E{row % holders:02d}" if day == 20 else f"D{day:02d}-{row:03d}"]
    walked = _both_walks(cells, _STAMP, [keys], 11)
    assert walked.thin[grains.DAY] is thin


@pytest.mark.parametrize(("rows", "thin"), [(10, True), (11, False)])
def test_an_unread_spelling_on_fewer_rows_than_the_floor_is_thin_where_each_row_holds_itself(rows: int, thin: bool) -> None:
    """Two thousand stamps, ``rows`` of them written `later`: each row its own holder, counted in rows."""
    draw = random.Random("unread-rows")
    cells = _stamps(draw, 2_000, "%Y-%m-%dT%H:%M:%S", datetime.datetime(2019, 1, 1), 90 * 86_400)
    cells = [cell if cell.strip() and cell != "unknown" else "2019-02-02T02:02:02" for cell in cells]
    for place in range(rows):
        cells[place * 7] = "later"
    walked = _both_walks(cells, _STAMP, [], 11, rows_hold=True)
    assert walked.unread_thin is thin


def test_an_offset_few_people_hold_in_the_first_held_day_is_outside_the_span() -> None:
    """On the shared clock the first held day also holds `+05:00` on five rows of five people.

    That key lies in the span's first bucket, not strictly inside the span:
    the day rung is not thin, as c47a6aee read it (skeptic 1's item 2: the
    first bucket compared with `>=` would hold the column back).
    """
    start = datetime.datetime(2021, 1, 1, 8)
    cells: "list[str]" = []
    keys: "list[str]" = []
    for day in range(10):
        for row in range(400):
            offset = "+05:00" if row < (5 if day == 0 else 30) else "Z"
            cells += [(start + datetime.timedelta(days=day, seconds=60 * row)).strftime("%Y-%m-%dT%H:%M:%S") + offset]
            keys += [f"P{day:02d}-{row:03d}"]
    walked = _both_walks(cells, _STAMP, [keys], 11, at_utc=True)
    assert walked.thin[grains.DAY] is False


def _traced_walk_a_row(name: str, rows: int, monkeypatch: pytest.MonkeyPatch) -> float:
    """The most `tracemalloc` sees the walk hold above its column's cells and subjects, a row.

    THE MEMOS HELD TO 1,024 TEXTS (`profile._PEOPLE_MEMO_TEXTS`, 65,536 a column:
    a fixed few megabytes at 2,000,000 rows, every text at 20,000), as lane H3's
    gate holds its own: the bytes counted are the ones a row adds past them.
    """
    monkeypatch.setattr(profile, "_PEOPLE_MEMO_TEXTS", 1_024)
    draw = random.Random(name)
    start = datetime.datetime(2019, 1, 1)
    people = _people(draw, rows, rows // 4)
    reading = _STAMP
    at_utc = False
    if name == "seconds" or name == "rows":
        cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", start, 2 * 365 * 86_400)
    elif name == "twelve":
        cells = _stamps(draw, rows, "%m/%d/%Y %I:%M %p", start, 2 * 365 * 86_400)
        reading = _TWELVE
    elif name == "offsets":
        cells = [
            f"{(start + datetime.timedelta(seconds=draw.randrange(2 * 365 * 86_400))).strftime('%Y-%m-%dT%H:%M:%S')}{draw.choice(_OFFSETS)}"
            for _ in range(rows)
        ]
        at_utc = True
    else:
        cells = [(start + datetime.timedelta(days=draw.randrange(2_000))).strftime("%Y-%m-%d") for _ in range(rows)]
        reading = _DATE
    rows_hold = name == "rows"
    subjects = [] if rows_hold else [people]
    enough = [True] * len(subjects)
    present = sum(1 for cell in cells if cell.strip())
    profile._grain_walk(
        cells[:200], 200, reading, [subject[:200] for subject in subjects], enough, 11, frozenset(), at_utc, rows_hold
    )
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        walked = profile._grain_walk(cells, present, reading, subjects, enough, 11, frozenset(), at_utc, rows_hold)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert walked.grain.spans, name
    return held / rows


# Each bound over the measured bytes a row at 20,000 rows, memos held as at
# 2,000,000 rows (Python 3.11 and 3.13 alike: 50.1 for stamps to the second,
# twelve-hour stamps and the rows as holders, 51.9 with offsets on the shared
# clock, 50.3 for dates), against 650 to 740 for the stamps and 150 to 200 for
# the dates on c47a6aee, its memos then holding every text: the sorted moments
# (a whole number and its place in the list, about 45 bytes a moment) and the
# byte a row that says which rows read.
@pytest.mark.parametrize(
    ("name", "bound"),
    [("seconds", 56), ("twelve", 56), ("offsets", 58), ("dates", 56), ("rows", 56)],
)
def test_the_walk_holds_under_its_bound_a_row(name: str, bound: int, monkeypatch: pytest.MonkeyPatch) -> None:
    per_row = _traced_walk_a_row(name, 20_000, monkeypatch)
    assert per_row < bound, (name, per_row)


def test_the_coarse_cells_share_their_texts(monkeypatch: pytest.MonkeyPatch) -> None:
    """The step back's coarse cells hold one text for each different one: a pointer a row (plan P4-D463).

    Measured at 20,000 rows of stamps to the second, its memos held as at
    2,000,000 rows (Python 3.11): 10.25 traced bytes a row at the
    month, the list itself as it grows, against 97 on c47a6aee (a new text
    a row).
    """
    monkeypatch.setattr(profile, "_PEOPLE_MEMO_TEXTS", 1_024)
    rows = 20_000
    draw = random.Random("coarse")
    cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", datetime.datetime(2019, 1, 1), 2 * 365 * 86_400)
    people = _people(draw, rows, rows // 4)
    present = sum(1 for cell in cells if cell.strip())
    walked = profile._grain_walk(cells, present, _STAMP, [people], [True], 11, frozenset(), False)
    span = walked.grain.spans[len(walked.grain.spans) - 1]
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        coarse = profile._cells_at(cells, walked, span)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert coarse is not None and span[0] == grains.MONTH
    assert held / rows < 11.5, held / rows




def _counted_case(name: str) -> "tuple[list[str], list[list[str]], list[bool] | None, bool]":
    """One column beside its subject columns for `_counted_in_subjects`, and whether its block's pool is in people."""
    draw = random.Random(name)
    rows = 4_000
    people = _people(draw, rows, 1_000)
    if name == "stamps":
        return _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", datetime.datetime(2019, 1, 1), 90 * 86_400), [people], [True], False
    if name in ("labels-rare", "labels-pooled"):
        cells = [draw.choice(("red", "green", "blue", "grey")) for _ in range(rows)]
        for place in range(40):
            cells[place] = "violet"
            people[place] = f"P{place % 3:05d}"
        return cells, [people], [True], name == "labels-pooled"
    if name == "labels-fine":
        return [draw.choice(("red", "green", "blue")) for _ in range(rows)], [people], None, False
    if name == "numbers":
        return [f"{draw.gauss(80, 12):.1f}" for _ in range(rows)], [people], [True], False
    if name == "units":
        return [f"{draw.gauss(37, 0.6):.1f} C" for _ in range(rows)], [people], [True], False
    if name == "names-of-few":
        families = [f"F{draw.randrange(6)}" for _ in range(rows)]
        return [f"Name {family}" for family in families], [people, families], [True, False], False
    if name == "two-subjects":
        visits = [f"V{draw.randrange(2_000):05d}" for _ in range(rows)]
        return [draw.choice(("in", "out", "day")) for _ in range(rows)], [people, visits], [True, True], False
    if name == "rows-dates":
        return [f"2021-0{draw.randrange(1, 10)}-1{draw.randrange(10)}" for _ in range(rows - 5)] + ["2024-01-01"] * 5, [], [], False
    if name == "rows-labels":
        return [draw.choice(("x", "y", "z")) for _ in range(rows - 5)] + ["w"] * 5, [], [], False
    return [draw.choice(("A1", "B2", "C3", "")) for _ in range(rows)], [[f"W{draw.randrange(4)}" for _ in range(rows)]], [False], False


@pytest.mark.parametrize(
    "name",
    [
        "stamps", "labels-rare", "labels-pooled", "labels-fine", "numbers", "units", "names-of-few", "two-subjects",
        "rows-dates", "rows-labels", "few-apart",
    ],
)
def test_the_count_in_people_answers_as_it_did(name: str) -> None:
    cells, subjects, enough, pooled = _counted_case(name)
    rows_hold = name.startswith("rows")
    holders = [profile.rows_as_holders(len(cells))] if rows_hold else []
    described = taxonomy.profile_column(name, 0, cells, len(cells), _SETTINGS)
    affixed = described.role == taxonomy.ROLE_AFFIXED
    reading = profile._CellReading(
        "", False, affixed, profile._published_wrappers(described.details) if affixed else ()
    )
    old = _OLD_COUNTED(  # type: ignore[operator]
        described, cells, subjects + holders, 11, enough if not holders else (enough or []) + [True], reading, pooled
    )
    new = profile._counted_in_subjects(described, cells, subjects, 11, enough, reading, pooled, rows_hold)
    assert new == old, name
    if name in ("labels-rare", "names-of-few", "rows-dates"):
        assert new, name


@pytest.mark.parametrize(("rows", "few"), [(10, True), (11, False)])
def test_a_published_date_on_fewer_rows_than_the_floor_is_counted_where_each_row_holds_itself(rows: int, few: bool) -> None:
    """Days over a month, and one far day on ``rows`` rows that the description publishes (skeptic 1's item 1 (c)).

    Each row its own holder: ten rows are a published value ten rows hold,
    eleven are not.
    """
    draw = random.Random("far-day")
    start = datetime.datetime(2021, 1, 1)
    days = [(start + datetime.timedelta(days=draw.randrange(30))).strftime("%Y-%m-%d") for _ in range(4_000 - rows)]
    days += ["2030-01-01"] * rows
    described = taxonomy.profile_column("day", 0, days, len(days), _SETTINGS)
    assert described.role == taxonomy.ROLE_DATETIME
    old = _OLD_COUNTED(  # type: ignore[operator]
        described, days, [profile.rows_as_holders(len(days))], 11, [True], profile._CellReading()
    )
    new = profile._counted_in_subjects(described, days, [], 11, [], profile._CellReading(), rows_hold=True)
    assert new == old
    assert new is few


@pytest.mark.parametrize(
    ("people", "enough", "rows"),
    [(5, True, 20_000), (30, True, 20_000), (5, False, 20_000), (5, False, 600), (0, True, 20_000)],
)
def test_the_present_rows_count_answers_as_it_did(people: int, enough: bool, rows: int) -> None:
    draw = random.Random(people)
    cells = [""] * 300
    keys = [f"P{draw.randrange(1_000):05d}" for _ in range(300)]
    for place in range(people * 2):
        cells[place] = "yes"
        keys[place] = f"P{place % people:05d}"
    absent = frozenset({"NA"})
    old = _OLD_PRESENT(cells, absent, [keys], [enough], 11, rows)  # type: ignore[operator]
    assert profile._present_too_few(cells, absent, [keys], [enough], 11, rows) == old


def test_the_codes_grow_a_byte_wider_where_a_number_needs_it() -> None:
    """A code a row kept in one byte, then two, then three, every earlier code read back unchanged (P4-D463)."""
    rows = 300
    codes = profile._Codes(bytearray(rows), 1)
    wanted = [0] * rows
    for place in range(rows):
        wanted[place] = (place * 977) % (70_000 if place > 200 else 300 if place > 100 else 200)
        profile._code_kept(codes, place, wanted[place], rows)
    assert codes.width == 3
    assert [profile._code_at(codes, place) for place in range(rows)] == wanted


def test_the_count_in_people_holds_nothing_a_row(monkeypatch: pytest.MonkeyPatch) -> None:
    """Counting a column of stamps in people holds nothing a row, no reference and no map of every subject (P4-D463).

    Measured at 20,000 rows of stamps to the second beside a person column of
    about four rows a person, the memo held as at 2,000,000 rows: 4.48 traced
    bytes a row on Python 3.11 and 4.37 on 3.13 (the memo's thousand texts and
    each set of keys' first subjects, a fixed amount), against 5.43 and 5.33
    with a code a row (the lane's build, afb48553) and 54 on c47a6aee with its
    memo then holding every text (a reference a row to the row's keys and a
    map of every subject's first text, asked whether the column is attached).
    """
    monkeypatch.setattr(profile, "_PEOPLE_MEMO_TEXTS", 1_024)
    rows = 20_000
    draw = random.Random("counted")
    cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", datetime.datetime(2019, 1, 1), 2 * 365 * 86_400)
    people = _people(draw, rows, rows // 4)
    described = taxonomy.profile_column("stamp", 0, cells, rows, _SETTINGS)
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        answer = profile._counted_in_subjects(described, cells, [people], 11, [True], profile._CellReading())
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert answer
    assert held / rows < 5.0, held / rows


def _random_counted(draw: random.Random) -> "tuple[list[str], list[list[str]], list[bool], int, bool, bool]":
    """A column and its subject columns drawn at random, the floor, the pool in people and the rows as holders."""
    rows = draw.randrange(200, 1_500)
    kind = draw.choice(("labels", "many", "codes", "numbers", "units", "stamps", "days", "sparse"))
    if kind == "labels":
        cells = [draw.choice(("red", "green", "blue", "grey")) for _ in range(rows)]
    elif kind == "many":
        cells = [f"L{draw.randrange(rows // 3)}" for _ in range(rows)]
    elif kind == "codes":
        cells = [draw.choice(("A1", "B2", "C3", "D4", "", "NA")) for _ in range(rows)]
    elif kind == "numbers":
        cells = [f"{draw.gauss(80, 12):.{draw.randrange(2)}f}" for _ in range(rows)]
    elif kind == "units":
        cells = [f"{draw.gauss(37, 0.6):.1f} C" for _ in range(rows)]
    elif kind == "stamps":
        cells = _stamps(draw, rows, "%Y-%m-%dT%H:%M:%S", datetime.datetime(2019, 1, 1), draw.choice((3, 90)) * 86_400)
    elif kind == "days":
        cells = [f"2021-0{draw.randrange(1, 10)}-1{draw.randrange(10)}" for _ in range(rows)]
    else:
        cells = [draw.choice(("yes", "", "", "")) for _ in range(rows)]
    for _rare in range(draw.randrange(3)):
        value = draw.choice(("violet", "2030-01-01", "999.9", "Z9"))
        for place in draw.sample(range(rows), draw.randrange(1, 25)):
            cells[place] = value
    subjects: "list[list[str]]" = []
    enough: "list[bool]" = []
    for _subject in range(draw.randrange(4)):
        shape = draw.choice(("people", "few", "attached", "blank"))
        if shape == "people":
            subjects += [[f"P{draw.randrange(rows // draw.choice((1, 2, 5)) + 1)}" for _ in range(rows)]]
        elif shape == "few":
            subjects += [[f"W{draw.randrange(5)}" for _ in range(rows)]]
        elif shape == "attached":
            owners = [f"F{draw.randrange(8)}" for _ in range(rows)]
            subjects += [owners]
            cells = [f"Name {owner}" if draw.random() < 0.9 else cells[place] for place, owner in enumerate(owners)]
        else:
            subjects += [[draw.choice(("", f"P{draw.randrange(30)}")) for _ in range(rows)]]
        enough += [shape in ("people", "blank") and draw.random() < 0.8]
    return cells, subjects, enough, draw.randrange(1, 21), draw.random() < 0.2, draw.random() < 0.3


def test_the_count_in_people_and_the_present_rows_answer_as_they_did_on_random_columns() -> None:
    """Sixty columns drawn at random, each counted as c47a6aee counted it (lane SR2a's repair 1).

    Labels few and many, codes beside blanks and absent spellings, numbers,
    units, stamps, days and sparse flags; values a few rows hold; zero to
    three subject columns of people, few values, values attached to their
    column or many blanks, each counting in people or not; floors 1 to 20;
    a block pooled in people; each row its own holder.
    """
    draw = random.Random("random-counted")
    answered: "dict[bool, int]" = {True: 0, False: 0}
    for case in range(60):
        cells, subjects, enough, floor, pooled, rows_hold = _random_counted(draw)
        described = taxonomy.profile_column(f"c{case}", 0, cells, len(cells), _SETTINGS)
        affixed = described.role == taxonomy.ROLE_AFFIXED
        reading = profile._CellReading(
            "", False, affixed, profile._published_wrappers(described.details) if affixed else ()
        )
        holders = [profile.rows_as_holders(len(cells))] if rows_hold else []
        old = _OLD_COUNTED(  # type: ignore[operator]
            described, cells, subjects + holders, floor, enough + [True] * len(holders), reading, pooled
        )
        new = profile._counted_in_subjects(described, cells, subjects, floor, enough, reading, pooled, rows_hold)
        assert new == old, case
        answered[new] = answered[new] + 1
        absent = frozenset(described.absent_spellings)
        for n_rows in (len(cells), 20_000):
            assert profile._present_too_few(cells, absent, subjects, enough, floor, n_rows) == _OLD_PRESENT(  # type: ignore[operator]
                cells, absent, subjects, enough, floor, n_rows
            ), case
    assert answered[True] >= 10 and answered[False] >= 10, answered


def _counting_calls(monkeypatch: pytest.MonkeyPatch, module: object, name: str) -> "dict[str, int]":
    """Each call of ``module``'s function ``name`` counted while the test runs."""
    calls = {"n": 0}
    inner = getattr(module, name)

    def counted(*args: object, **kwargs: object) -> object:
        calls["n"] = calls["n"] + 1
        return inner(*args, **kwargs)

    monkeypatch.setattr(module, name, counted)
    return calls


def test_the_count_in_people_reads_each_different_cell_once(monkeypatch: pytest.MonkeyPatch) -> None:
    """20,000 labels of five spellings beside a person column: five cells read, not one a row (repair 1).

    CPU first (the orchestrator's LANE I4m RULINGS 25): c47a6aee read every
    cell's keys again (`_cell_keys`, 20,000 calls) and asked whether the
    column is attached to its people (`_attached`, a map of every subject);
    a column all of whose values many people hold needs neither.
    """
    draw = random.Random("labels-read-once")
    rows = 20_000
    cells = [draw.choice(("red", "green", "blue", "grey", "white")) for _ in range(rows)]
    people = _people(draw, rows, 4_000)
    described = taxonomy.profile_column("labels", 0, cells, rows, _SETTINGS)
    keys = _counting_calls(monkeypatch, profile, "_cell_keys")
    attached = _counting_calls(monkeypatch, profile, "_attached")
    assert not profile._counted_in_subjects(described, cells, [people], 11, [True], profile._CellReading())
    assert (keys["n"], attached["n"]) == (5, 0)
    for place in range(30):
        cells[place] = "violet"
        people[place] = f"P{place % 5:05d}"
    described = taxonomy.profile_column("labels", 0, cells, rows, _SETTINGS)
    keys["n"] = 0
    profile._counted_in_subjects(described, cells, [people], 11, [True], profile._CellReading())
    assert (keys["n"], attached["n"]) == (6, 1)


def test_the_present_rows_count_stops_once_the_floor_is_met(monkeypatch: pytest.MonkeyPatch) -> None:
    """20,000 cells, most of them present, of 4,000 people: the count ends at the floor's eleventh person (repair 1)."""
    draw = random.Random("present-stops")
    rows = 20_000
    cells = [draw.choice(("yes", "yes", "")) for _ in range(rows)]
    people = [f"P{place:05d}" for place in range(rows)]
    folded = _counting_calls(monkeypatch, profile.parsing, "folded")
    assert not profile._present_too_few(cells, frozenset(), [people], [True], 11, rows)
    assert folded["n"] < 40, folded["n"]
    folded["n"] = 0
    assert not profile._present_too_few(cells, frozenset(), [], [], 11, rows)
    assert folded["n"] < 40, folded["n"]
    folded["n"] = 0
    assert profile._present_too_few(cells, frozenset(), [[f"P{place % 7}" for place in range(rows)]], [True], 11, rows)
    assert folded["n"] == rows


@pytest.mark.parametrize(("people", "few"), [(10, True), (11, False)])
def test_a_column_whose_present_rows_fewer_people_than_the_floor_hold_is_counted(people: int, few: bool) -> None:
    """20,000 rows beside 4,000 people, a flag present on 600 rows of ``people`` people (P4-D453 at the floor's edge).

    The count ends once the floor's eleventh person is met; ten people never
    reach it, so the column's present rows are a group of ten.
    """
    rows = 20_000
    draw = random.Random("present-edge")
    keys = _people(draw, rows, 4_000)
    cells = [""] * rows
    for place in range(600):
        cells[place * 30] = "yes"
        keys[place * 30] = f"Q{place % people:02d}"
    new = profile._present_too_few(cells, frozenset(), [keys], [True], 11, rows)
    assert new == _OLD_PRESENT(cells, frozenset(), [keys], [True], 11, rows)  # type: ignore[operator]
    assert new is few


@pytest.mark.parametrize(("present", "few"), [(10, True), (11, False)])
def test_a_column_present_on_fewer_rows_than_the_floor_is_counted_where_no_person_column_counts(present: int, few: bool) -> None:
    """20,000 rows and no subject column that counts: each row its own holder, ten present rows a group of ten."""
    rows = 20_000
    cells = [""] * rows
    for place in range(present):
        cells[place * 900] = "yes"
    wards = [f"W{place % 5}" for place in range(rows)]
    for subjects, enough in (([], []), ([wards], [False])):
        new = profile._present_too_few(cells, frozenset(), subjects, enough, 11, rows)
        assert new == _OLD_PRESENT(cells, frozenset(), subjects, enough, 11, rows)  # type: ignore[operator]
        assert new is few


def test_a_date_column_s_present_rows_are_not_its_count_in_rows() -> None:
    """Eight dates present on 4,000 rows, each row its own holder: no published value or form is counted, so no hold.

    Its present rows as a whole are the present rows' count's
    (`_present_too_few`, plan P4-D453), never a key of the count in rows,
    as on c47a6aee.
    """
    rows = 4_000
    cells = [""] * rows
    for place in range(8):
        cells[place * 300] = f"2021-03-{1 + place:02d}"
    described = taxonomy.profile_column("day", 0, cells, rows, _SETTINGS)
    assert described.role == taxonomy.ROLE_DATETIME
    new = profile._counted_in_subjects(described, cells, [], 11, [], profile._CellReading(), rows_hold=True)
    assert new == _OLD_COUNTED(  # type: ignore[operator]
        described, cells, [profile.rows_as_holders(rows)], 11, [True], profile._CellReading()
    )
    assert new is False


# REPAIR 2 (Codex's review of the lane, item 1; LANE SR2 RULINGS 6 (1)): the
# count in people one subject column at a time. Repair 1 counted every subject
# column in one pass: beside a code column of many published levels and many
# open candidates it held a map of subjects a level under EVERY column at once
# (about 4 GB at 2,000,000 rows on Codex's shape) and read every column to the
# end where c47a6aee's first column had already decided.
class _Read(list):  # type: ignore[type-arg]
    """A subject column that counts the rows read from it: the count's work in rows times subject columns."""

    def __init__(self, cells: "list[str]") -> None:
        super().__init__(cells)
        self.reads = 0

    def __getitem__(self, place):  # type: ignore[no-untyped-def]
        self.reads = self.reads + 1
        return super().__getitem__(place)


def _labels_beside_candidates(columns: int, first_rejects: bool) -> "tuple[list[str], list[list[str]]]":
    """Codex's shape at 20,000 rows: 1,818 six-letter labels each on eleven rows, two rows more, ``columns`` candidates.

    Each candidate but the first cycles through 1,000 keys, so a label's
    eleven rows are eleven different subjects under it. The first does the
    same, or, where ``first_rejects``, is one subject a label: every label
    then one subject's, a value the column may not publish under that one.
    """
    keys = [f"K{key:03d}" for key in range(1_000)]
    names: "list[str]" = []
    for label in range(1_818):
        number = label * 7_919
        text = ""
        for _letter in range(6):
            text += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[number % 26]
            number = number // 26
        names += [text]
    cells: "list[str]" = []
    subjects: "list[list[str]]" = [[] for _column in range(columns)]
    owners = [f"S{label:04d}" for label in range(1_818)]
    for place in range(20_000):
        label = place // 11 if place < 19_998 else 0
        cells += [names[label]]
        for column in range(columns):
            if column == 0 and first_rejects:
                subjects[column] += [owners[label]]
            else:
                subjects[column] += [keys[(place * (column + 3)) % 1_000]]
    return cells, subjects


def _traced_count(described: taxonomy.ColumnProfile, cells: "list[str]", subjects: "list[list[str]]") -> "tuple[int, bool]":
    """The most `tracemalloc` sees the count in people hold above its cells and subjects, and its answer."""
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        answer = profile._counted_in_subjects(described, cells, subjects, 11, [True] * len(subjects), profile._CellReading())
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    return held, answer


@pytest.mark.parametrize("first_rejects", [True, False])
def test_the_count_in_people_holds_one_subject_column_and_reads_no_more_than_c47a6aee(first_rejects: bool) -> None:
    """1,818 published labels beside eight candidates: one column's subjects held at once, c47a6aee's work or less.

    Where the first candidate holds each label in one subject, c47a6aee's
    count ended with that column, after reading it twice (whether the column
    is attached to it, then its holders): the count does the same and reads
    no other column. Where every label is eleven subjects' under every
    candidate, each column is read once (c47a6aee: twice), the answer is no
    hold, and the most held at once is what one column holds: about the
    same beside eight as beside one (Python 3.11, 20,000 rows: measured in
    the lane's repair 2), where counting the eight at once held eight
    columns' subjects.
    """
    cells, subjects = _labels_beside_candidates(8, first_rejects)
    described = taxonomy.profile_column("code", 0, cells, len(cells), _SETTINGS, forced_code=True)
    assert described.role == taxonomy.ROLE_LONG_TAIL
    old_read = [_Read(column) for column in subjects]
    new_read = [_Read(column) for column in subjects]
    old = _OLD_COUNTED(described, cells, old_read, 11, [True] * 8, profile._CellReading())  # type: ignore[operator]
    new = profile._counted_in_subjects(described, cells, new_read, 11, [True] * 8, profile._CellReading())
    assert new == old
    assert new is first_rejects
    reads = [column.reads for column in new_read]
    if first_rejects:
        assert reads == [column.reads for column in old_read] == [40_000] + [0] * 7, reads
    else:
        # Each row read once until its label has met the floor's eleven
        # subjects: all but the two rows that repeat the first label.
        assert reads == [19_998] * 8, reads
        assert [column.reads for column in old_read] == [40_000] * 8
    held_all, answer_all = _traced_count(described, cells, subjects)
    held_one, answer_one = _traced_count(described, cells, subjects[:1])
    assert answer_all is answer_one is first_rejects
    assert held_all < 1.25 * held_one + 65_536, (held_all, held_one)


@pytest.mark.parametrize(("holders", "few"), [(10, True), (11, False)])
def test_the_rows_past_the_memo_are_read_back_by_the_next_subject_column(
    holders: int, few: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The memo held to 256 texts: the last label, met long after it filled, is ``holders`` subjects' under the third column only.

    The first pass keeps the number of each row past the memo, since two
    columns follow, and the third column's pass reads them back: ten
    subjects hold that label there (a hold), eleven do not, as c47a6aee
    counted them.
    """
    monkeypatch.setattr(profile, "_PEOPLE_MEMO_TEXTS", 256)
    cells, subjects = _labels_beside_candidates(3, False)
    block = 1_817 * 11
    assert cells[block - 1] != cells[block] == cells[block + 10] != cells[block + 11]
    for place in range(block, block + 11):
        subjects[2][place] = f"Q{place % holders:02d}"
    described = taxonomy.profile_column("code", 0, cells, len(cells), _SETTINGS, forced_code=True)
    old = _OLD_COUNTED(described, cells, subjects, 11, [True] * 3, profile._CellReading())  # type: ignore[operator]
    new = profile._counted_in_subjects(described, cells, subjects, 11, [True] * 3, profile._CellReading())
    assert new == old
    assert new is few


def _two_subject_columns(present: "list[bool]", people: int) -> "tuple[list[str], list[str]]":
    """Visits that differ on every row, and patients: the flagged rows ``people`` patients', the others 4,000's."""
    visits = [f"V{place % 9_000:05d}" for place in range(len(present))]
    patients = [f"P{place % people:02d}" if present[place] else f"P{place % 4_000 + 10:05d}" for place in range(len(present))]
    return visits, patients


@pytest.mark.parametrize(("people", "few"), [(5, True), (11, False)])
def test_the_second_subject_column_is_counted_through_its_own_subjects(people: int, few: bool) -> None:
    """20,000 rows: `violet` on thirty rows, thirty visits but ``people`` patients; the visits column first.

    Under the visits it is thirty subjects' and not held; under the patients
    five hold it (a hold) or eleven (none): each subject column is counted
    through its own subjects, as c47a6aee counted them.
    """
    draw = random.Random("two-columns")
    rows = 20_000
    flagged = [place < 30 for place in range(rows)]
    visits, patients = _two_subject_columns(flagged, people)
    cells = ["violet" if flagged[place] else draw.choice(("red", "green", "blue", "grey")) for place in range(rows)]
    described = taxonomy.profile_column("labels", 0, cells, rows, _SETTINGS)
    old = _OLD_COUNTED(described, cells, [visits, patients], 11, [True, True], profile._CellReading())  # type: ignore[operator]
    new = profile._counted_in_subjects(described, cells, [visits, patients], 11, [True, True], profile._CellReading())
    assert new == old
    assert new is few


@pytest.mark.parametrize(("people", "few"), [(5, True), (11, False)])
def test_the_present_rows_count_reads_the_second_subject_column_through_its_own_subjects(people: int, few: bool) -> None:
    """20,000 rows: a flag present on thirty rows, thirty visits but ``people`` patients; the visits column first.

    Both columns hold the floor's number of values. The visits meet the
    floor, the patients five (a group of five: the flag's count is held)
    or eleven (none), as c47a6aee counted them (the verify of repair 1,
    item 2: read through the first column's subjects, five patients' flag
    was published).
    """
    rows = 20_000
    flagged = [place < 30 for place in range(rows)]
    visits, patients = _two_subject_columns(flagged, people)
    flags = ["yes" if flagged[place] else "" for place in range(rows)]
    old = _OLD_PRESENT(flags, frozenset(), [visits, patients], [True, True], 11, rows)  # type: ignore[operator]
    new = profile._present_too_few(flags, frozenset(), [visits, patients], [True, True], 11, rows)
    assert new == old
    assert new is few


def test_the_coarse_cells_past_the_shared_texts_are_the_bytes_they_were() -> None:
    """70,000 stamps over 67,998 minutes, read at the minute: past 65,536 different texts, each cell a text of its own (Codex's item 2).

    The step back shares the first 65,536 different coarse texts it meets
    (`profile._PEOPLE_MEMO_TEXTS`): the two stamps of each of the first
    thousand minutes are written as one text, and so are the two of minute
    65,535, the 65,536th text met. A text first met after them is made
    again at each cell, equal in value, as c47a6aee made every one: minute
    65,536's two stamps are two texts. The cells are the bytes c47a6aee
    wrote, and only the memory of a column of more different buckets than
    that is not cut. The limit is pinned at its edge (the scoped verify 2
    of lane SR2a, its item 1): shared to 65,535 texts, minute 65,535's two
    cells are two texts; shared to 65,537, minute 65,536's are one.
    """
    start = datetime.datetime(2019, 1, 1)
    cells: "list[str]" = []
    rows_of: "dict[int, list[int]]" = {}
    for minute in range(68_000):
        if minute in (66_998, 66_999):
            # Two single minutes fewer, past the edge, for minute 65,535's
            # and 65,536's second stamps: still 70,000 rows, and every
            # minute up to 65,536 still the text met in its own place.
            continue
        twice = minute < 1_000 or minute in (65_535, 65_536) or minute >= 67_000
        for second in (7, 37) if twice else (7,):
            rows_of.setdefault(minute, []).append(len(cells))
            cells += [(start + datetime.timedelta(minutes=minute, seconds=second)).strftime("%Y-%m-%dT%H:%M:%S")]
    rows = len(cells)
    assert rows == 70_000
    first = grains.start_of(grains.moment_of(cells[0], _STAMP), grains.MINUTE)  # type: ignore[arg-type]
    last = grains.start_of(grains.moment_of(cells[rows - 1], _STAMP), grains.MINUTE)  # type: ignore[arg-type]
    span = (grains.MINUTE, first, last)
    grain = grains.Grain(grains.MINUTE, _STAMP, rows, (span,), grains.SECOND, 0)
    padded = grains.column_padded(cells, _STAMP)
    new = profile._cells_at(cells, profile._Walked(grain, bytearray(b"\x01" * rows), {}, False, padded), span)
    old = _OLD_CELLS_AT(cells, _OLD_NAMES["_Walked"](grain, [1] * rows, {}, False, padded), span)  # type: ignore[operator]
    assert new is not None and new == old
    assert len(set(new)) == 67_998
    assert all(new[2 * minute] is new[2 * minute + 1] for minute in range(1_000))
    # THE EDGE: minute 65,535's text is the 65,536th met, the last shared;
    # minute 65,536's is the first that is not.
    assert rows_of[65_535] == [66_535, 66_536] and rows_of[65_536] == [66_537, 66_538]
    assert new[66_535] is new[66_536]
    assert new[66_537] == new[66_538]
    assert new[66_537] is not new[66_538]
    past = 2_000 + 66_000
    assert rows_of[67_000][0] == past
    assert all(new[past + 2 * pair] == new[past + 2 * pair + 1] for pair in range(1_000))
    assert not any(new[past + 2 * pair] is new[past + 2 * pair + 1] for pair in range(1_000))
    # 65,536 shared texts (minutes 0 to 65,535), then one text a row:
    # minute 65,536's two rows, the 1,461 minutes met once from 65,537 to
    # 66,997 and the last thousand's 2,000 rows.
    assert len({id(text) for text in new}) == 65_536 + 2 + 1_461 + 2_000

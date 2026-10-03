"""Lane G3: the count pass's paid merge keeps its book between attempts (plan P4-D376).

WHAT WAS SLOW. Where a timestamp column's twin holds more different
instants than its description publishes, method G7.3's count pass merges
runs of ranks, and where no unit of a run's own midnight standing lies
in its gap it makes the merge WITH A PAYMENT (`generation._traded_merges`,
plan P4-D258 and item 2 of the dates pass of the second Codex round).
Every attempt rebuilt the held units, the runs and their offers from all
the ranks, and every offer walked all the ranks again to find its
payment, asking each its standing. A made-up column of 40,000 clinic
slots took 117 to 188 s to generate on 110cb46, a 40,000-row quarter-hour
grid 124 s and a lab panel 84 s, 94 % of it there; the same clinic
column at 20,000 rows, where the pass asks for no trade, took 2.3 s.

WHAT CHANGED, AND WHAT DID NOT. The pass keeps a book (`_TradeBook`):
built once per call and brought up to date by the ranks a paid merge
moved, with the ranks that can pay filed by their standing so a payment
is sought among them alone. No answer changes. So this file keeps the
function as 110cb46 shipped it (`_traded_merges_as_built`, with the
payment walk it called) as its ORACLE and asks both the same questions:

1. seeded hand-built trades, width and midnight, every argument drawn,
   the ranks, the counts per unit and the merges made compared whole;
2. every call the real generator makes on seeded clinic-slot columns,
   each answered by both from the same state.

THE GROWTH MEASURE NEEDS NO CLOCK. Every rank the pass looks at is
asked first whether the tail pins it, so the reads of its ``pinned``
list count the ranks it reads, whichever way it is written. Ledger
entry K-S3-51 holds the reads per rank and their growth when the rows
double; the as-built pass is measured the same way here and must read
far more, so the measure is known to see the defect it guards against.
"""

from __future__ import annotations

import collections
import csv
import io
import pathlib
import random
import types
import typing

import pytest

import fixtures
from synthtwin import contract, generation, parsing, profile, reading, rendering, taxonomy

DAY = 86400
# The reads a rank the book allows the pass, and what the as-built pass
# must exceed on the same columns for the measure to be known to see it.
READS_PER_RANK_AT_MOST = 10
AS_BUILT_READS_PER_RANK_AT_LEAST = 50


# -- the oracle: the pass as 110cb46 shipped it -----------------------------


def _repaid_standings_as_built(
    facts: contract.DatetimeFacts,
    moved: "list[int]",
    pinned: "list[bool]",
    lows: "list[int]",
    highs: "list[int]",
    day: int,
    step: int,
    unit: int,
    held: "dict[int, int]",
    spot: "dict[int, int]",
    order: "dict[tuple[int, int], list[int]]",
    word: str,
    wanted: int,
    gaining: bool,
    skip: int,
    onto: int,
    clock: bool,
    widths: bool,
    gone: "frozenset[int]",
) -> "dict[int, int]":
    """`generation._repaid_standings` as 110cb46 shipped it: every rank walked."""
    paid: "dict[int, int]" = {}
    for rank in range(len(moved)):
        if len(paid) >= wanted:
            break
        if pinned[rank]:
            continue
        own = moved[rank] // unit
        if own == skip or own == onto:
            continue
        if held[own] <= 1:
            continue
        standing = generation._counts_into_width(facts, moved[rank] // day, word)
        if clock:
            standing = generation._written_at_midnight(moved[rank], 0, step)
        if standing == gaining:
            continue
        target = generation._nearest_held_unit(
            facts, moved[rank], lows[rank], highs[rank], day, step, unit,
            held, spot, order, widths or not clock, word, not clock, skip,
            clock, (), gone,
        )
        if target is None:
            continue
        paid[rank] = moved[rank]
        generation._moved_between(moved, held, unit, rank, target)
    return paid


def _traded_merges_as_built(
    facts: contract.DatetimeFacts,
    moved: "list[int]",
    pinned: "list[bool]",
    lows: "list[int]",
    highs: "list[int]",
    day: int,
    step: int,
    unit: int,
    held: "dict[int, int]",
    widths: bool,
    word: str,
    owed: int,
    clock: bool = False,
    gone: "frozenset[int]" = frozenset(),
) -> int:
    """`generation._traded_merges` as 110cb46 shipped it: every attempt rebuilt."""
    if owed <= 0:
        return 0
    if not clock and not widths:
        return 0
    if clock and day != DAY:
        return 0
    parsed = len(moved)
    made = 0
    for _attempt in range(owed):
        spot: "dict[int, int]" = {}
        for rank in range(parsed):
            spot[moved[rank] // unit] = moved[rank]
        order = generation._held_order(facts, spot, day, step, widths or not clock, word)
        offers: "list[tuple[int, int, int, int]]" = []
        first = 0
        while first < parsed:
            last = first
            while last + 1 < parsed and moved[last + 1] // unit == moved[first] // unit:
                last = last + 1
            loose = True
            for rank in range(first, last + 1):
                if pinned[rank]:
                    loose = False
            if loose and held[moved[first] // unit] == last - first + 1:
                tried: "list[int]" = []
                room = generation._TRADE_TARGETS if clock else 1
                lowest, highest = generation._run_room(lows, highs, first, last)
                while len(tried) < room:
                    target = generation._nearest_held_unit(
                        facts, moved[first], lowest, highest, day, step, unit,
                        held, spot, order, widths, word, not clock, -1, clock,
                        tried, gone,
                    )
                    if target is None:
                        break
                    offers += [(abs(target - moved[first]), last - first + 1, first, target)]
                    tried += [target // unit]
            first = last + 1
        if not offers:
            return made
        asked = sorted(offers)
        if not clock:
            asked = [asked[0]]
        settled = False
        for offer in asked:
            size = offer[1]
            start = offer[2]
            target = offer[3]
            own = moved[start] // unit
            gaining = generation._counts_into_width(facts, target // day, word)
            if clock:
                gaining = generation._written_at_midnight(target, 0, step)
            paid = _repaid_standings_as_built(
                facts, moved, pinned, lows, highs, day, step, unit, held, spot,
                order, word, size, not gaining, own, target // unit, clock,
                widths, gone,
            )
            if len(paid) < size:
                for rank in sorted(paid):
                    generation._moved_between(moved, held, unit, rank, paid[rank])
                continue
            for rank in range(start, start + size):
                moved[rank] = target
            held[own] = 0
            held[target // unit] = held[target // unit] + size
            made = made + 1
            settled = True
            break
        if not settled:
            return made
    return made


# -- 1. seeded hand-built trades ---------------------------------------------

# Month-first dates: a day shows a width where its month or its day is
# below ten, so under each word below some days count and some do not.
_FACTS = typing.cast(
    contract.DatetimeFacts, types.SimpleNamespace(parser_family="month-first-date")
)
_WORDS = ("first-field-padded", "second-field-padded", "padded")
# Day numbers of 2020-09-25 onward: the months 9, 10 and 11 and days on
# both sides of ten, so both width kinds stand close together.
_FIRST_DAY = 18530


def _trade_case(draw: random.Random) -> "dict[str, object]":
    """One trade's arguments, drawn: sorted ranks, pinned ends, gaps between pins."""
    clock = draw.random() < 0.6
    count = draw.randrange(6, 48)
    if clock:
        unit = draw.choice((1, 60, 900))
        step = unit
        day = DAY
        start = _FIRST_DAY * DAY
        span = draw.randrange(2, 9)
        places: "list[int]" = []
        for _place in range(draw.randrange(3, 14)):
            if draw.random() < draw.choice((0.2, 0.5, 0.8)):
                places += [start + DAY * draw.randrange(span)]
            else:
                places += [
                    start + DAY * draw.randrange(span) + unit * draw.randrange(1, DAY // unit)
                ]
    else:
        unit = 1
        step = 1
        day = 1
        start = _FIRST_DAY
        places = [start + draw.randrange(70) for _place in range(draw.randrange(3, 16))]
    moved = [draw.choice(places) for _rank in range(count)]
    if clock and unit > 1 and draw.random() < 0.4:
        # Instants off the precision's lattice, so the ranks of one unit
        # stand on different instants and the instant a unit is held at
        # (the last rank's) can move when a payment takes that rank.
        moved = [value + draw.randrange(unit) for value in moved]
    moved = sorted(moved)
    pinned = [rank in (0, count - 1) or draw.random() < 0.08 for rank in range(count)]
    lows = [0] * count
    highs = [0] * count
    below = moved[0]
    for rank in range(count):
        if pinned[rank]:
            below = moved[rank]
        above = moved[count - 1]
        for later in range(rank, count):
            if pinned[later]:
                above = moved[later]
                break
        lows[rank] = moved[rank] if pinned[rank] else below
        highs[rank] = moved[rank] if pinned[rank] else above
    widths = (not clock) or draw.random() < 0.3
    word = draw.choice(_WORDS) if widths else ""
    held = dict(collections.Counter(value // unit for value in moved))
    gone: "frozenset[int]" = frozenset()
    if draw.random() < 0.2:
        gone = frozenset({draw.choice(moved) // unit})
    return {
        "moved": moved, "pinned": pinned, "lows": lows, "highs": highs,
        "day": day, "step": step, "unit": unit, "held": held, "widths": widths,
        "word": word, "owed": draw.randrange(1, 6), "clock": clock, "gone": gone,
    }


def _asked(
    trade: typing.Callable[..., int], case: "dict[str, object]"
) -> "tuple[int, list[int], dict[int, int]]":
    moved = list(typing.cast("list[int]", case["moved"]))
    held = dict(typing.cast("dict[int, int]", case["held"]))
    made = trade(
        _FACTS, moved, list(typing.cast("list[bool]", case["pinned"])),
        list(typing.cast("list[int]", case["lows"])),
        list(typing.cast("list[int]", case["highs"])),
        case["day"], case["step"], case["unit"], held, case["widths"],
        case["word"], case["owed"], case["clock"], case["gone"],
    )
    return made, moved, held


def test_hand_built_trades_answer_as_built() -> None:
    """3,000 drawn trades: the same merges, the same ranks, the same counts per unit."""
    draw = random.Random(376)
    missed: "list[str]" = []
    traded = {True: 0, False: 0}
    for number in range(3000):
        case = _trade_case(draw)
        want = _asked(_traded_merges_as_built, case)
        got = _asked(generation._traded_merges, case)
        if got != want:
            missed += [f"case {number}: {got!r}, as built {want!r}"]
        if want[0] > 0:
            traded[bool(case["clock"])] += 1
    assert not missed, missed[:3]
    # The cases reach both trades, and more than once: a draw that never
    # traded would prove nothing about the book.
    assert traded[True] >= 100 and traded[False] >= 100, traded


# -- 2. every call the generator makes, on clinic slots ----------------------

_YEAR_START = 19358  # 2023-01-01
_HOURS = (8, 9, 10, 11, 12, 13, 14, 15, 16)
_HOUR_WEIGHTS = (1.0, 1.2, 1.2, 1.1, 0.4, 1.0, 1.1, 1.0, 0.7)


def clinic_slots(rows: int, seed: int = 0) -> "list[str]":
    """``rows`` made-up clinic appointments to the minute, about 154 a weekday.

    Weekdays from 2023-01-02, as many as keep about 154 rows each, hours
    8 to 16 with a lunch dip, 70 % on the hour or half hour, 25 % on a
    quarter and 5 % on any minute: the stage-4 skeptic's clinic slots,
    held at one density so the trade pass is asked at every size.
    """
    draw = random.Random(20261001 + rows + 7919 * seed)
    days = max(5, rows // 154)
    cells: "list[str]" = []
    for _row in range(rows):
        place = draw.randrange(days)
        year, month, day = parsing.civil_from_days(
            _YEAR_START + 7 * (place // 5) + place % 5 + 1
        )
        hour = draw.choices(_HOURS, weights=_HOUR_WEIGHTS)[0]
        pick = draw.random()
        if pick < 0.70:
            minute = draw.choice((0, 30))
        elif pick < 0.95:
            minute = draw.choice((15, 45))
        else:
            minute = draw.randrange(60)
        cells += [f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}"]
    return cells


def _described(folder: pathlib.Path, values: "list[str]") -> contract.Profile:
    """Write ``values`` as a one-column table, describe it with the real producer, load it."""
    folder.mkdir(parents=True, exist_ok=True)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["slot"])
    for value in values:
        writer.writerow([value])
    path = fixtures.write(folder, "table.csv", out.getvalue())
    settings = taxonomy.Settings()
    table = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(table, settings, [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


@pytest.mark.parametrize(("rows", "seed"), [(2500, 0), (2500, 3), (2500, 4), (5000, 1), (5000, 4)])
def test_generator_calls_answer_as_built(
    rows: int, seed: int, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each trade the generator asks for, answered from one state by both: the same."""
    loaded = _described(tmp_path, clinic_slots(rows, seed))
    plain = rendering.twin_csv(generation.generate(loaded, seed))
    traded = generation._traded_merges
    asked: "list[int]" = []
    missed: "list[str]" = []

    def both(facts, moved, pinned, lows, highs, day, step, unit, held, widths, word, owed, clock=False, gone=frozenset()):
        nonlocal asked, missed
        old_moved = list(moved)
        old_held = dict(held)
        want = _traded_merges_as_built(
            facts, old_moved, pinned, lows, highs, day, step, unit, old_held,
            widths, word, owed, clock, gone,
        )
        got = traded(
            facts, moved, pinned, lows, highs, day, step, unit, held, widths,
            word, owed, clock, gone,
        )
        asked += [got]
        if (got, moved, held) != (want, old_moved, old_held):
            missed += [f"call {len(asked)}: made {got} against {want}"]
        return got

    monkeypatch.setattr(generation, "_traded_merges", both)
    checked = rendering.twin_csv(generation.generate(loaded, seed))
    assert not missed, missed
    assert sum(asked) >= 1, "no trade was made, so nothing was compared"
    assert checked == plain


# -- the growth measure (K-S3-51) --------------------------------------------


def trade_reads(
    rows: int,
    folder: pathlib.Path,
    trade: "typing.Callable[..., int] | None" = None,
    checked: bool = False,
) -> "tuple[int, int]":
    """The ranks the trade pass reads generating the clinic slots of ``rows``, and the merges.

    Every rank the pass looks at -- building its offers, walking for a
    payment -- is first asked whether the tail pins it, so the reads of
    its ``pinned`` list count them. ``trade`` stands in for the pass, so
    the as-built one is measured the same way. Where ``checked``, the
    twin is also generated uncounted and must be the counted one, byte
    for byte, or this raises.
    """
    loaded = _described(folder, clinic_slots(rows))
    plain = rendering.twin_csv(generation.generate(loaded, 0)) if checked else ""
    reads = [0]
    made = [0]

    class Counted(list):  # type: ignore[type-arg]
        def __getitem__(self, index):  # type: ignore[no-untyped-def]
            reads[0] += 1
            return list.__getitem__(self, index)

    asked = trade or generation._traded_merges
    original = generation._traded_merges

    def counted(facts, moved, pinned, *rest):  # type: ignore[no-untyped-def]
        done = asked(facts, moved, Counted(pinned), *rest)
        made[0] += done
        return done

    generation._traded_merges = counted
    try:
        twin = rendering.twin_csv(generation.generate(loaded, 0))
    finally:
        generation._traded_merges = original
    if checked and twin != plain:
        raise AssertionError("counting the reads changed the twin")
    return reads[0], made[0]


def test_the_measure_sees_the_rebuild(tmp_path: pathlib.Path) -> None:
    """5,000 clinic slots: the book reads at most ten ranks a rank, the as-built pass over fifty.

    Measured with this measure: the as-built pass reads 90 a rank here,
    159 at 10,000 rows and 1,600 at 20,000; the book 3.1, 2.6 and 5.2.
    Ledger entry K-S3-51 holds the book at 10,000 and 40,000 rows.
    """
    reads, made = trade_reads(5000, tmp_path / "new", checked=True)
    assert made >= 1
    assert reads <= READS_PER_RANK_AT_MOST * 5000, reads
    reads, made = trade_reads(5000, tmp_path / "old", _traded_merges_as_built, checked=True)
    assert made >= 1
    assert reads >= AS_BUILT_READS_PER_RANK_AT_LEAST * 5000, reads

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
is sought among them alone; a payer whose search finds no unit at all
leaves its list until it moves or the book is built again; a run that
was offered the unit a merge left trades that one offer for its next
nearest; that unit leaves the files the searches walk; and the offers
stand sorted in blocks of a few hundred (`_OfferPool`), so putting one
in or taking one out moves one block. No answer changes. So this file
keeps the function as 110cb46 shipped it (`_traded_merges_as_built`,
with the payment walk it called) as its ORACLE and asks both the same
questions:

1. seeded hand-built trades, width and midnight, every argument drawn,
   the ranks, the counts per unit and the merges made compared whole,
   and the same draws moved to straddle 1970-01-01, where the unit
   numbered -1 is held;
2. after every paid merge of more such trades, the book against one
   built afresh from the trade's state at that moment, so a book that
   drifts is caught where it drifts and not only where it moves a cell,
   with blocks of two offers so the pool halves and drops blocks all
   the while; and drawn puts and takes of the pool against one sorted
   list;
3. every call the real generator makes on seeded clinic-slot columns,
   and on the same slots with one cell in fifty written date-only, at
   midnight, each answered by both from the same state.

THE GROWTH MEASURES NEED NO CLOCK. Every rank the pass looks at is
asked first whether the tail pins it, so the reads of its ``pinned``
list count the ranks it reads, whichever way it is written; the
held-unit searches it makes are counted where it makes them; and the
offers its pool moves are counted where a put or a take finds its
place in a block, with the entries a block's halving or removal moves.
Ledger entry K-S3-51 holds each per rank at two sizes; the as-built
pass, or the pool held as one sorted list as 311cf30 held it, is
measured the same way here and must count far more, so each measure is
known to see the defect it guards against.
"""

from __future__ import annotations

import bisect
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
# The same for the held-unit searches the pass makes, on clinic slots
# with one cell in fifty at midnight, where it makes hundreds of merges.
SEARCHES_PER_RANK_AT_MOST = 10
AS_BUILT_SEARCHES_PER_RANK_AT_LEAST = 50
# The offers the pool moves a rank on those midnight slots at 5,000 rows,
# and what the pool held as one sorted list must exceed there.
MOVES_PER_RANK_AT_MOST = 500
ONE_BLOCK_MOVES_PER_RANK_AT_LEAST = 1500


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


def _gaps(moved: "list[int]", pinned: "list[bool]") -> "tuple[list[int], list[int]]":
    """Each rank's bounds: its own instant where pinned, else the pins on either side."""
    count = len(moved)
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
    return lows, highs


def _trade_case(draw: random.Random, large: bool = False) -> "dict[str, object]":
    """One trade's arguments, drawn: sorted ranks, pinned ends, gaps between pins.

    ``large`` draws more ranks over more instants and owes more merges,
    so one call makes many attempts; the draws a small case makes are
    the same either way.
    """
    clock = draw.random() < 0.6
    count = draw.randrange(30, 260) if large else draw.randrange(6, 48)
    if clock:
        unit = draw.choice((1, 60, 900))
        step = unit
        day = DAY
        start = _FIRST_DAY * DAY
        span = draw.randrange(2, 9)
        places: "list[int]" = []
        for _place in range(draw.randrange(5, 60) if large else draw.randrange(3, 14)):
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
        places = [
            start + draw.randrange(70)
            for _place in range(draw.randrange(5, 50) if large else draw.randrange(3, 16))
        ]
    moved = [draw.choice(places) for _rank in range(count)]
    if clock and unit > 1 and draw.random() < 0.4:
        # Instants off the precision's lattice, so the ranks of one unit
        # stand on different instants and the instant a unit is held at
        # (the last rank's) can move when a payment takes that rank.
        moved = [value + draw.randrange(unit) for value in moved]
    moved = sorted(moved)
    pinned = [rank in (0, count - 1) or draw.random() < 0.08 for rank in range(count)]
    lows, highs = _gaps(moved, pinned)
    widths = (not clock) or draw.random() < 0.3
    word = draw.choice(_WORDS) if widths else ""
    held = dict(collections.Counter(value // unit for value in moved))
    gone: "frozenset[int]" = frozenset()
    if draw.random() < 0.2:
        gone = frozenset({draw.choice(moved) // unit})
    return {
        "moved": moved, "pinned": pinned, "lows": lows, "highs": highs,
        "day": day, "step": step, "unit": unit, "held": held, "widths": widths,
        "word": word, "owed": draw.randrange(1, 60) if large else draw.randrange(1, 6),
        "clock": clock, "gone": gone,
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


def _before_the_epoch(draw: random.Random) -> "dict[str, object]":
    """One drawn trade moved back whole, so its lowest instant stands just before 1970.

    `_trade_case` draws every instant from 2020-09-25 on, so the unit
    numbered -1 -- the last day, minute or second of 1969 -- is held in
    none of its cases, and a payment walk that set that unit aside to
    mean "none" passed them all (the lane's first skeptic). Here a
    column of dates moves so its lowest day stands 1 to 11 days before
    1970-01-01, and a column of moments by whole days, so every instant
    keeps its clock, until its lowest stands 1 or 2 days before it. A
    moment of the last unit of a day is rare in the draws, so in half the
    columns of moments those of 1969-12-31 not written at midnight move
    to that unit, minute or quarter hour as drawn. The bounds, the ranks
    per unit and the unit an absent spelling names are taken again.
    """
    case = _trade_case(draw)
    unit = typing.cast(int, case["unit"])
    moved = typing.cast("list[int]", case["moved"])
    lowest = moved[0]
    if case["clock"]:
        shift = lowest - lowest % DAY + DAY * draw.randrange(1, 3)
    else:
        shift = lowest + draw.randrange(1, 12)
    moved = [value - shift for value in moved]
    if case["clock"] and draw.random() < 0.5:
        moved = sorted(
            -unit + value % unit
            if -DAY <= value < 0 and (value - value % unit) % DAY != 0
            else value
            for value in moved
        )
    case["moved"] = moved
    case["lows"], case["highs"] = _gaps(moved, typing.cast("list[bool]", case["pinned"]))
    case["held"] = dict(collections.Counter(value // unit for value in moved))
    if case["gone"]:
        case["gone"] = frozenset({draw.choice(moved) // unit})
    return case


def test_hand_built_trades_answer_as_built() -> None:
    """3,000 drawn trades and 3,000 before 1970: the same merges, ranks and counts per unit."""
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
    # THE UNIT NUMBERED -1 IS A UNIT LIKE ANY OTHER: the same draws moved
    # to straddle 1970-01-01, where some trade holds it.
    early = random.Random(3763)
    before = {True: 0, False: 0}
    for number in range(3000):
        case = _before_the_epoch(early)
        want = _asked(_traded_merges_as_built, case)
        got = _asked(generation._traded_merges, case)
        if got != want:
            missed += [f"case {number} before 1970: {got!r}, as built {want!r}"]
        if want[0] > 0 and -1 in typing.cast("dict[int, int]", case["held"]):
            before[bool(case["clock"])] += 1
    assert not missed, missed[:3]
    # Measured: 293 trades of moments and 48 of dates hold it.
    assert before[True] >= 100 and before[False] >= 20, before


# -- 2. the book against one built afresh, after every paid merge -----------


def _pool_offers(pool: typing.Any) -> "list[tuple[int, int, int, int]]":
    """The offers of a pool, read block after block."""
    offers: "list[tuple[int, int, int, int]]" = []
    for block in pool.blocks:
        offers += block
    return offers


def _pool_faults(pool: typing.Any) -> "list[str]":
    """What a pool's blocks break of the statements `generation._OfferPool` makes."""
    wrong: "list[str]" = []
    if len(pool.lasts) != len(pool.blocks):
        wrong += [f"{len(pool.lasts)} lasts for {len(pool.blocks)} blocks"]
    for at, block in enumerate(pool.blocks):
        if not block or len(block) > 2 * generation._OFFER_BLOCK:
            wrong += [f"block {at} holds {len(block)} offers"]
        elif at < len(pool.lasts) and pool.lasts[at] != block[-1]:
            wrong += [f"block {at}'s last offer is not the one filed for it"]
    offers = _pool_offers(pool)
    if any(offers[at] >= offers[at + 1] for at in range(len(offers) - 1)):
        wrong += ["the offers out of order"]
    return wrong


def _drift(book: typing.Any, left: int) -> "list[str]":
    """What ``book`` says that a book built afresh from the trade's state does not.

    Built afresh, a book holds what every attempt rebuilt before plan
    P4-D376: the same offers (the pool, read block after block), the same
    runs and the same ranks on each unit. Beyond that the kept book
    promises that its pool's blocks are what `generation._OfferPool`
    states; that ``left``, the unit the merge left, is in no file a
    search walks; that each payer stands filed under its standing now, in
    rank order; and that a rank the tail does not pin is out of its list
    only where its search, with no unit set aside, finds no held unit at
    all.
    """
    wrong: "list[str]" = []
    fresh = generation._trade_book(
        book.facts, book.moved, book.pinned, book.lows, book.highs, book.day,
        book.step, book.unit, book.held, book.widths, book.word, book.clock,
        book.gone,
    )
    if _pool_offers(book.pool) != _pool_offers(fresh.pool):
        wrong += ["the offers"]
    wrong += _pool_faults(book.pool)
    if book.last_of != fresh.last_of:
        wrong += ["the runs"]
    held_ranks = {key: ranks for key, ranks in book.on_unit.items() if ranks}
    if held_ranks != fresh.on_unit:
        wrong += ["the ranks on each unit"]
    for keys in book.order.values():
        if left in keys:
            wrong += [f"unit {left}, which the merge left, still filed"]
    for standing in (False, True):
        ranks = book.payers[standing]
        if ranks != sorted(ranks):
            wrong += ["payers out of rank order"]
        for rank in ranks:
            if book.pinned[rank] or book.stands[rank] != standing:
                wrong += [f"rank {rank} filed under the wrong standing"]
    for rank in book.free:
        if book.stands[rank] != fresh.stands[rank]:
            wrong += [f"rank {rank} keeps a standing it left"]
        if rank in book.payers[book.stands[rank]]:
            continue
        found = generation._nearest_held_unit(
            book.facts, book.moved[rank], book.lows[rank], book.highs[rank],
            book.day, book.step, book.unit, book.held, fresh.spot, fresh.order,
            book.widths or not book.clock, book.word, not book.clock,
            book.lows[rank] // book.unit - 1, book.clock, (), book.gone,
        )
        if found is not None:
            wrong += [f"rank {rank} is out of its list but can pay"]
    return wrong


def test_the_book_is_the_rebuild_after_every_merge(monkeypatch: pytest.MonkeyPatch) -> None:
    """1,500 small and 300 large drawn trades: after each paid merge, the book is a fresh one.

    The kept book is compared with a book built afresh from the trade's
    state after EVERY paid merge, and the ranks a walk takes out of its
    list are checked as it takes them, so a book that drifts is caught
    at the merge where it drifts. The draws must reach every way the
    book changes: payers taken out, offers traded for the next nearest
    with and without one to find, the book built again whole, and its
    pool's blocks halved and dropped, which blocks of two offers here
    make happen all the while.
    """
    monkeypatch.setattr(generation, "_OFFER_BLOCK", 2)
    drifted: "list[str]" = []
    reached: "collections.Counter[str]" = collections.Counter()
    # The books built afresh to check against are not the pass's own.
    checking = [False]
    settled = generation._book_settled
    dropped = generation._book_payers_dropped
    replaced = generation._book_offer_replaced
    filled = generation._book_filled

    def settled_checked(
        book: typing.Any, done: "tuple[int, int, int, int, dict[int, int]]"
    ) -> None:
        nonlocal drifted
        settled(book, done)
        reached["merges"] += 1
        checking[0] = True
        drifted += _drift(book, done[2])
        checking[0] = False

    def dropped_checked(book: typing.Any, standing: bool, dead: "list[int]") -> None:
        nonlocal drifted
        checking[0] = True
        fresh = generation._trade_book(
            book.facts, book.moved, book.pinned, book.lows, book.highs,
            book.day, book.step, book.unit, book.held, book.widths, book.word,
            book.clock, book.gone,
        )
        checking[0] = False
        for rank in dead:
            found = generation._nearest_held_unit(
                book.facts, book.moved[rank], book.lows[rank], book.highs[rank],
                book.day, book.step, book.unit, book.held, fresh.spot,
                fresh.order, book.widths or not book.clock, book.word,
                not book.clock, book.lows[rank] // book.unit - 1, book.clock,
                (), book.gone,
            )
            if found is not None:
                drifted += [f"rank {rank} taken out of its list, but it can pay"]
        if dead:
            reached["payers taken out"] += 1
        kept = [rank for rank in book.payers[standing] if rank not in dead]
        dropped(book, standing, dead)
        if book.payers[standing] != kept:
            drifted += ["a walk's list lost a rank it did not name, or kept one it did"]

    def replaced_counted(book: typing.Any, first: int, left: int) -> None:
        before = len(book.offers_of[first])
        replaced(book, first, left)
        if len(book.offers_of[first]) == before:
            reached["offers traded for a next nearest"] += 1
        else:
            reached["offers given up"] += 1

    def filled_counted(book: typing.Any) -> None:
        if not checking[0]:
            reached["books built"] += 1
        filled(book)

    monkeypatch.setattr(generation, "_book_settled", settled_checked)
    monkeypatch.setattr(generation, "_book_payers_dropped", dropped_checked)
    monkeypatch.setattr(generation, "_book_offer_replaced", replaced_counted)
    monkeypatch.setattr(generation, "_book_filled", filled_counted)
    upkept = generation._pool_blocks_replaced

    def upkept_counted(pool: typing.Any, at: int, blocks: "list[list[typing.Any]]") -> None:
        reached["blocks halved" if blocks else "blocks dropped"] += 1
        upkept(pool, at, blocks)

    monkeypatch.setattr(generation, "_pool_blocks_replaced", upkept_counted)
    draw = random.Random(3761)
    missed: "list[str]" = []
    calls = 0
    for number in range(1800):
        case = _trade_case(draw, large=number >= 1500)
        want = _asked(_traded_merges_as_built, case)
        before = reached["books built"]
        got = _asked(generation._traded_merges, case)
        if reached["books built"] > before:
            calls += 1
        if got != want:
            missed += [f"case {number}: {got!r}, as built {want!r}"]
    assert not missed, missed[:3]
    assert not drifted, drifted[:5]
    # Measured: 2,152 merges, 711 walks taking payers out, 201 offers
    # traded for a next nearest and 274 given up, 63 books built again,
    # and 400 blocks of the pool halved and 3,657 dropped.
    assert reached["merges"] >= 1000, reached
    assert reached["payers taken out"] >= 100, reached
    assert reached["offers traded for a next nearest"] >= 100, reached
    assert reached["offers given up"] >= 100, reached
    assert reached["blocks halved"] >= 100 and reached["blocks dropped"] >= 100, reached
    # Built again whole after a merge, beyond the one build of each call.
    assert reached["books built"] - calls >= 20, (reached, calls)


@pytest.mark.parametrize(("seed", "number"), [(107, 0), (2618, 31)])
def test_a_payer_taken_out_and_moved_is_filed_again(
    seed: int, number: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A payer a walk took out of its list moves with a merged run and is filed again.

    Its own search, from its own instant, found no held unit; the run it
    belongs to searches from its first rank's instant, which on a unit of
    fifteen minutes can reach a unit the payer's walk could not. Drawn:
    the first case of seed 107, and the 32nd of seed 2618, where taking
    the moved rank out of its list by its place alone, without asking
    whether it is there, takes out another rank that can pay. Each is
    held to the as-built pass and to a book built afresh.
    """
    draw = random.Random(seed)
    for _number in range(number + 1):
        case = _trade_case(draw)
    moved_out: "list[int]" = []
    drifted: "list[str]" = []
    settled = generation._book_settled

    def watched(
        book: typing.Any, done: "tuple[int, int, int, int, dict[int, int]]"
    ) -> None:
        nonlocal moved_out, drifted
        start, size, _left, _onto, paid = done
        for rank in list(range(start, start + size)) + sorted(paid):
            if rank not in book.payers[book.stands[rank]]:
                moved_out += [rank]
        settled(book, done)
        drifted += _drift(book, done[2])

    monkeypatch.setattr(generation, "_book_settled", watched)
    assert _asked(generation._traded_merges, case) == _asked(_traded_merges_as_built, case)
    assert not drifted, drifted
    assert moved_out, "the case no longer moves a payer taken out of its list"


@pytest.mark.parametrize("block", [1, 2, 3, 256])
def test_the_pool_reads_as_one_sorted_list(block: int, monkeypatch: pytest.MonkeyPatch) -> None:
    """Drawn puts and takes, at four block sizes: the pool reads as one sorted list does.

    After every put or take the pool's offers, read block after block,
    are the offers a sorted list holds after the same steps, and every
    few steps its blocks are what `generation._OfferPool` states: none
    empty or over twice the block size, each block's last offer filed.
    The draws crowd their offers together so blocks fill, halve and
    empty at every size, the last of them at 256 offers a block.
    """
    monkeypatch.setattr(generation, "_OFFER_BLOCK", block)
    upkept = generation._pool_blocks_replaced
    reached: "collections.Counter[str]" = collections.Counter()

    def upkept_counted(pool: typing.Any, at: int, blocks: "list[list[typing.Any]]") -> None:
        reached["halved" if blocks else "dropped"] += 1
        upkept(pool, at, blocks)

    monkeypatch.setattr(generation, "_pool_blocks_replaced", upkept_counted)
    draw = random.Random(3764 + block)
    wrong: "list[str]" = []
    for number in range(12):
        held: "dict[tuple[int, int, int, int], bool]" = {}
        for _offer in range(draw.randrange(0, 1300)):
            held[(draw.randrange(40), draw.randrange(1, 4), draw.randrange(400), draw.randrange(-3, 50))] = True
        sorted_list = sorted(held)
        pool = generation._offer_pool(list(sorted_list))
        # Every third case mostly puts, and at the nearest two distances,
        # into the first blocks, so that a block of 256 fills and halves.
        spread = 40
        taken = 0.3 if number % 2 else 0.7
        steps = draw.randrange(200, 1800)
        if number % 3 == 0:
            spread = 2
            taken = 0.2
            steps = steps + 1500
        for step in range(steps):
            taking = bool(sorted_list) and draw.random() < taken
            if taking:
                offer = sorted_list[draw.randrange(len(sorted_list))]
                generation._pool_take(pool, offer)
                del sorted_list[bisect.bisect_left(sorted_list, offer)]
                del held[offer]
            else:
                offer = (draw.randrange(spread), draw.randrange(1, 4), draw.randrange(400), draw.randrange(-3, 50))
                if offer in held:
                    continue
                generation._pool_put(pool, offer)
                held[offer] = True
                at = bisect.bisect_left(sorted_list, offer)
                sorted_list[at:at] = [offer]
            if _pool_offers(pool) != sorted_list:
                wrong += [f"case {number}, step {step}: the offers part from a sorted list"]
                break
            if step % 25 == 0:
                wrong += _pool_faults(pool)
        wrong += _pool_faults(pool)
    assert not wrong, wrong[:3]
    # Measured at 256 offers a block: 15 halved, 353 dropped.
    assert reached["halved"] >= 5 and reached["dropped"] >= 5, reached


# -- 3. every call the generator makes, on clinic slots ----------------------

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


def few_at_midnight(rows: int, seed: int = 0) -> "list[str]":
    """The clinic slots of ``rows``, about one cell in fifty written date-only, at midnight.

    A clinic that books some visits by the day alone. The twin holds the
    published count of cells at midnight, so its count pass makes
    hundreds of paid merges here where the clinic slots alone make a
    handful: 293 at 10,000 rows and 698 at 20,000, against 2 and 11.
    """
    draw = random.Random(4343 + rows)
    cells: "list[str]" = []
    for cell in clinic_slots(rows, seed):
        if draw.random() < 0.02:
            cell = cell[:10] + " 00:00"
        cells += [cell]
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


def _calls_answer_as_built(
    loaded: contract.Profile, seed: int, monkeypatch: pytest.MonkeyPatch
) -> int:
    """Generate ``loaded`` at ``seed`` with every trade answered by both passes; the merges made."""
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
    monkeypatch.setattr(generation, "_traded_merges", traded)
    assert not missed, missed
    assert checked == plain
    return sum(asked)


@pytest.mark.parametrize(("rows", "seed"), [(2500, 0), (2500, 3), (2500, 4), (5000, 1), (5000, 4)])
def test_generator_calls_answer_as_built(
    rows: int, seed: int, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each trade the generator asks for, answered from one state by both: the same."""
    made = _calls_answer_as_built(_described(tmp_path, clinic_slots(rows, seed)), seed, monkeypatch)
    assert made >= 1, "no trade was made, so nothing was compared"


@pytest.mark.parametrize(("rows", "seed"), [(2500, 0), (5000, 2)])
def test_generator_calls_answer_as_built_on_midnight_slots(
    rows: int, seed: int, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The same, where one cell in fifty is written at midnight: hundreds of paid merges each."""
    loaded = _described(tmp_path, few_at_midnight(rows, seed))
    made = _calls_answer_as_built(loaded, seed, monkeypatch)
    assert made >= 100, made


# -- the growth measures (K-S3-51) -------------------------------------------


def _trade_counts(
    rows: int,
    folder: pathlib.Path,
    trade: "typing.Callable[..., int] | None",
    checked: bool,
    cells: "typing.Callable[[int], list[str]]",
) -> "dict[str, int]":
    """What the trade pass reads, searches and moves generating ``cells(rows)`` at seed 0, and its merges.

    Every rank the pass looks at -- building its offers, walking for a
    payment -- is first asked whether the tail pins it, so the reads of
    its ``pinned`` list count them; each held-unit search
    (`generation._nearest_held_unit`) it makes is counted while it runs;
    and every put or take of its pool first finds its place in the block
    it changes (`generation._offer_slot`), where the offers at and after
    that place are the ones it moves, beside which a block's halving or
    removal (`generation._pool_blocks_replaced`) moves the offers of the
    new blocks and the entries filed after it. ``trade`` stands in for
    the pass, so the as-built one is measured the same way. Where
    ``checked``, the twin is also generated uncounted by the shipped
    pass and must be the counted one, byte for byte, or this raises.
    """
    loaded = _described(folder, cells(rows))
    plain = rendering.twin_csv(generation.generate(loaded, 0)) if checked else ""
    counts = {"reads": 0, "searches": 0, "made": 0, "moved": 0}
    inside = [False]

    class Counted(list):  # type: ignore[type-arg]
        def __getitem__(self, index):  # type: ignore[no-untyped-def]
            counts["reads"] += 1
            return list.__getitem__(self, index)

    asked = trade or generation._traded_merges
    original = generation._traded_merges
    search = generation._nearest_held_unit
    slot_of = generation._offer_slot
    upkept = generation._pool_blocks_replaced

    def searched(*arguments, **named):  # type: ignore[no-untyped-def]
        if inside[0]:
            counts["searches"] += 1
        return search(*arguments, **named)

    def placed(block, offer):  # type: ignore[no-untyped-def]
        slot = slot_of(block, offer)
        if inside[0]:
            counts["moved"] += len(block) - slot
        return slot

    def upkeep(pool, at, blocks):  # type: ignore[no-untyped-def]
        if inside[0]:
            counts["moved"] += sum(len(block) for block in blocks) + 2 * (len(pool.blocks) - at - 1)
        upkept(pool, at, blocks)

    def counted(facts, moved, pinned, *rest):  # type: ignore[no-untyped-def]
        inside[0] = True
        try:
            done = asked(facts, moved, Counted(pinned), *rest)
        finally:
            inside[0] = False
        counts["made"] += done
        return done

    generation._traded_merges = counted
    generation._nearest_held_unit = searched
    generation._offer_slot = placed
    generation._pool_blocks_replaced = upkeep
    try:
        twin = rendering.twin_csv(generation.generate(loaded, 0))
    finally:
        generation._traded_merges = original
        generation._nearest_held_unit = search
        generation._offer_slot = slot_of
        generation._pool_blocks_replaced = upkept
    if checked and twin != plain:
        raise AssertionError("counting the pass changed the twin")
    return counts


def trade_reads(
    rows: int,
    folder: pathlib.Path,
    trade: "typing.Callable[..., int] | None" = None,
    checked: bool = False,
) -> "tuple[int, int]":
    """The ranks the trade pass reads generating the clinic slots of ``rows``, and the merges."""
    counts = _trade_counts(rows, folder, trade, checked, clinic_slots)
    return counts["reads"], counts["made"]


def trade_searches(
    rows: int,
    folder: pathlib.Path,
    trade: "typing.Callable[..., int] | None" = None,
    checked: bool = False,
) -> "tuple[int, int]":
    """The held-unit searches the trade pass makes on `few_at_midnight`'s ``rows``, and the merges."""
    counts = _trade_counts(rows, folder, trade, checked, few_at_midnight)
    return counts["searches"], counts["made"]


def midnight_counts(rows: int, folder: pathlib.Path, checked: bool = False) -> "dict[str, int]":
    """What the trade pass reads, searches and moves on `few_at_midnight`'s ``rows``, and the merges.

    The offers moved (``moved``) are what ledger entry K-S3-51 bounds at
    40,000 and 160,000 rows; the reads and searches there are recorded
    beside them, unbounded, because they still rise with the rows (plan
    P4-D376, what is left).
    """
    return _trade_counts(rows, folder, None, checked, few_at_midnight)


def test_the_measure_sees_the_rebuild(tmp_path: pathlib.Path) -> None:
    """5,000 clinic slots: the book reads at most ten ranks a rank, the as-built pass over fifty.

    Measured with this measure: the as-built pass reads 90 a rank here,
    159 at 10,000 rows and 1,600 at 20,000; the book 2.9, 2.1 and 3.6.
    Ledger entry K-S3-51 holds the book at 10,000 and 40,000 rows.
    """
    reads, made = trade_reads(5000, tmp_path / "new", checked=True)
    assert made >= 1
    assert reads <= READS_PER_RANK_AT_MOST * 5000, reads
    reads, made = trade_reads(5000, tmp_path / "old", _traded_merges_as_built, checked=True)
    assert made >= 1
    assert reads >= AS_BUILT_READS_PER_RANK_AT_LEAST * 5000, reads


def test_the_measure_sees_the_walks(tmp_path: pathlib.Path) -> None:
    """5,000 slots, one cell in fifty at midnight: ten searches a rank at most, as built over fifty.

    Measured with this measure: the as-built pass searches 111 times a
    rank here and 197 at 10,000 rows; the book as 40f1205 left it, whose
    every walk asked again the payers that could pay nowhere, 12.6 and
    20.6; this book 4.5 and 5.2. Ledger entry K-S3-51 holds it at 10,000
    and 20,000 rows.
    """
    searches, made = trade_searches(5000, tmp_path / "new", checked=True)
    assert made >= 100
    assert searches <= SEARCHES_PER_RANK_AT_MOST * 5000, searches
    searches, made = trade_searches(5000, tmp_path / "old", _traded_merges_as_built, checked=True)
    assert made >= 100
    assert searches >= AS_BUILT_SEARCHES_PER_RANK_AT_LEAST * 5000, searches


def test_the_measure_sees_the_pool(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """5,000 slots, one cell in fifty at midnight: the pool moves at most 500 offers a rank, one block over 1,500.

    Held as one block, the pool is the single sorted list 311cf30 kept,
    where every put or take moved every offer after its place. Measured
    with this measure: 144.5 offers a rank in blocks here and 2,262.8 as
    one list, which 311cf30 itself moves too; at 40,000 and 160,000 rows
    762 and 1,352 in blocks, where 311cf30 moved 57,160 and 391,482.
    Ledger entry K-S3-51 holds the blocks at those two sizes.
    """
    counts = midnight_counts(5000, tmp_path / "blocks", checked=True)
    assert counts["made"] >= 100
    assert counts["moved"] <= MOVES_PER_RANK_AT_MOST * 5000, counts
    monkeypatch.setattr(generation, "_OFFER_BLOCK", 10**12)
    counts = midnight_counts(5000, tmp_path / "one", checked=True)
    assert counts["made"] >= 100
    assert counts["moved"] >= ONE_BLOCK_MOVES_PER_RANK_AT_LEAST * 5000, counts

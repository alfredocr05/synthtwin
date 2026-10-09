"""Stage 4, tier 2a: whole numbers on a long ladder, and the reader (plan P4-D387).

Each change below was measured on made-up tables before it was made,
and none moves a byte of any output, so each keeps the function it
replaced as this file's ORACLE (`*_as_built`, the text of 110cb46 with
its docstring left out), asks both the same questions and requires the
same answers. Where the replaced work grew faster than the table, a
growth measure that needs no clock -- the lines the interpreter runs,
or the calls one question makes -- is taken at N and at 2N, and the
replaced function is required to grow as the square on the same shape,
so the measure is known to see the defect rather than assumed to.

1. **The walk for whole numbers** (`generation._whole_enough`, method
   G6.4). Every stratum it visited interpolated the share of every
   stratum after it (`_shares_after`), and asked whole numbers out to
   the column's strata whatever its share allowed, so a column of mostly
   whole charges with a stratum per row cost the square of its rows:
   5.6, 23.2 and 89.8 s to generate at 1,000, 2,000 and 4,000 rows. The
   shares are worked out once per walk and the strata still to be walked
   are asked of an index (`_walk_shares`, `_held_after`); `_whole_inside`
   stops at the first step past the half unit, which on a column crowded
   onto fewer whole numbers than strata was most of the walk; one holder
   is counted and not searched for; the numbers taken are kept as the
   strata move (`_seat_given`, `_taken_again`). Where the shares step
   back -- the convex form rounds, so between two rungs a unit in the
   last place apart one end can read the higher rung and the next the
   lower -- the index is laid over the pieces of the line the shares'
   ends cut (`_covering_index`), where 9fa2008 asked every stratum (the
   Codex review of P4-D387, item 1).
2. **The reach step's free whole number** (`_free_whole`,
   `_reach_window`, `_reach_held`, method G5.2). Each question listed
   every candidate out to the column's strata before asking the first,
   each window search asked from the first number again for every answer
   it took, and each round interpolated each share three times. And the
   rounds themselves (`_reach_sizes`): on a column crowded onto few whole
   numbers they come back to a division they reached before and walked
   round it again to their bound, one more than the strata; a repeat is
   now stepped past.
3. **The row order** (`dialect.row_order_of`). Every cell of a column
   was keyed under each collation before the order was asked.
4. **Detection** (`dialect.delimiter_reading`, `detected_initial_space`)
   cut the file's first megabyte into lines 29 times.
5. **The checking pass** (`reading._check_against_pandas`) held the
   second reading whole beside the first: 4.8 KB a row at the peak where
   the first reading holds 2.7. It reads and compares a piece at a time,
   each piece the rows pandas' own reader parses at a time, and reads the
   whole frame only where a piece differs, to refuse in its words -- at
   the line the pieces are read at, so a warning pandas gives about the
   file is shown once, as it was, save for a file pandas reads in part
   and then cannot read at all, where pandas may warn about the part it
   read and 110cb46 showed nothing.
"""

from __future__ import annotations

import csv
import dataclasses
import gc
import io
import math
import pathlib
import random
import sys
import tempfile
import tracemalloc
import warnings

import pandas
import pytest

import fixtures
from synthtwin import contract, dialect, generation, parsing, profile, reading, rendering, taxonomy

# What a path whose work grows with the rows may grow by when they
# double, and what the replaced path must reach to show the measure can
# fail. Linear work doubles; work in the square of the rows quadruples.
LINEAR_AT_MOST = 2.5
SQUARE_AT_LEAST = 3.0


def _table(values: "list[str]") -> str:
    """A one-column table of ``values``, every cell quoted so an edge space survives."""
    out = io.StringIO()
    writer = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(["value"])
    for value in values:
        writer.writerow([value])
    return out.getvalue()


def _described(folder: pathlib.Path, values: "list[str]") -> contract.Profile:
    """Write ``values`` as a one-column table, describe it with the real producer, load it."""
    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(folder, "table.csv", _table(values))
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def _lines_run(function: "object", *arguments: object, inside: str = "") -> int:
    """How many lines the interpreter runs answering ``function(*arguments)``.

    Every frame's lines are counted, or, with ``inside``, only the lines
    of functions whose name begins with it.
    """
    counted = [0]

    def local(frame: object, event: str, argument: object) -> object:
        if event == "line":
            counted[0] += 1
        return local

    def calls(frame: object, event: str, argument: object) -> object:
        if inside and not frame.f_code.co_name.startswith(inside):  # type: ignore[attr-defined]
            return None
        return local

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return counted[0]


# -- the made-up columns -------------------------------------------------


def _charges(rows: int, seed: int, centre: float = 7.0, spread: float = 1.2) -> "list[str]":
    """Amounts of a log-normal spread, 85 in a hundred written as whole numbers."""
    draw = random.Random(seed)
    values: "list[str]" = []
    for _row in range(rows):
        amount = math.exp(draw.gauss(centre, spread))
        values += [f"{round(amount)}" if draw.random() < 0.85 else f"{amount:.2f}"]
    return values


def _day_counts(rows: int, seed: int, days: int) -> "list[str]":
    """Counts of days with a second visit's fraction on a few rows, as a day-and-visit count writes them."""
    draw = random.Random(seed)
    values: "list[str]" = []
    for _row in range(rows):
        day = 64000 + draw.randrange(days)
        values += [f"{day}" if draw.random() < 0.85 else f"{day}.{draw.randrange(1, 9):02d}"]
    return values


def _signed(rows: int, seed: int) -> "list[str]":
    """Changes either side of zero, most of them whole."""
    draw = random.Random(seed)
    values: "list[str]" = []
    for _row in range(rows):
        change = draw.gauss(0.0, 40.0)
        values += [f"{round(change)}" if draw.random() < 0.8 else f"{change:.2f}"]
    return values


def _flat(rows: int, seed: int) -> "list[str]":
    """One whole number most rows share, with fractions near it."""
    draw = random.Random(seed)
    values = ["18"] * (rows // 2)
    values += [f"{18 + draw.random() * 3:.2f}" for _row in range(rows // 4)]
    values += [f"{draw.randint(10, 40)}" for _row in range(rows - len(values))]
    draw.shuffle(values)
    return values


def _whole_battery() -> "list[tuple[str, list[str]]]":
    """Mostly whole columns that reach every walk of G6.4 and the reach step of G5.2."""
    import test_p2c4f3_style_capacity as capacity
    import test_pool_alone_marks as marks

    cases: "list[tuple[str, list[str]]]" = [
        ("charges", _charges(160, 1)),
        ("charges-wide", _charges(220, 2, 11.0, 1.0)),
        ("day-counts", _day_counts(200, 3, 150)),
        ("day-counts-sparse", _day_counts(200, 4, 3000)),
        ("signed", _signed(200, 5)),
        ("flat", _flat(160, 6)),
        ("pooled-pair", [f"{index % 9 + 1}" for index in range(30)] + ["1.5", "2.5"]),
    ]
    for name, values in capacity.BATTERY:
        cases += [(f"capacity-{name}", list(values))]
    for name, cells, _census in marks.TRAILING:
        cases += [(f"trailing-{name}", list(cells))]
    for name, cells, _census in marks.PLUS_BESIDE_WHOLE:
        cases += [(name, list(cells))]
    return cases


# -- the oracles: the replaced functions as 110cb46 shipped them ---------------
#
# Each is the shipped text with its docstring left out, its module's own
# names reached through the module, and its name ending `_as_built`.


def _free_whole_as_built(low, high, band, rungs, held, reach, nearest):
    lowest = max(low, float(rungs[0]))
    highest = min(high, float(rungs[-1]))
    if band == generation._BAND_POSITIVE:
        lowest = max(lowest, 1.0)
    if band == generation._BAND_NEGATIVE:
        highest = min(highest, -1.0)
    if not generation.math.isfinite(lowest) or not generation.math.isfinite(highest):
        return None
    lowest = max(lowest, -float(generation._PLAIN_LIMIT))
    highest = min(highest, float(generation._PLAIN_LIMIT))
    first = max(generation._ceiling_of(lowest), -generation._PLAIN_LIMIT)
    last = min(generation._floor_of(highest), generation._PLAIN_LIMIT)
    if first > last:
        return None
    steps = max(reach, 1)
    candidates: list[int] = []
    if nearest:
        middle = generation._ceiling_of(lowest + (highest - lowest) / 2)
        middle = max(first, min(last, middle))
        for step in range(steps + 1):
            if step == 0:
                candidates += [middle]
                continue
            candidates += [middle + step, middle - step]
    elif band == generation._BAND_NEGATIVE:
        for step in range(steps + 1):
            candidates += [last - step]
    else:
        for step in range(steps + 1):
            candidates += [first + step]
    for number in candidates:
        if number < first or number > last:
            continue
        value = float(number)
        if value in held or not generation._carries_plainly(value, False):
            continue
        return value
    return None


def _reach_held_as_built(sizes, bands, rungs, whole_column, numbers):
    total = len(sizes)
    starts = generation._starts_of(sizes)
    held: dict[float, int] = {}
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if pinned or band == generation._BAND_ZERO:
            continue
        low = generation._interpolated(rungs, starts[place], numbers)
        high = generation._interpolated(rungs, starts[place] + sizes[place], numbers)
        crosses = band == generation._BAND_POSITIVE and low <= 0.0
        crosses = crosses or (band == generation._BAND_NEGATIVE and high >= 0.0)
        if not crosses:
            continue
        fallback = generation._sign_fallback(band, rungs)
        if band == generation._BAND_NEGATIVE and fallback >= 0.0:
            fallback = -1.0
        if band == generation._BAND_POSITIVE and fallback <= 0.0:
            fallback = 1.0
        if whole_column:
            fallback = generation._whole_valued(fallback)
        if generation._carries_plainly(fallback, False):
            held[fallback] = 1
    settled: dict[int, int] = {}
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if pinned or band == generation._BAND_ZERO:
            continue
        low = generation._interpolated(rungs, starts[place], numbers)
        high = generation._interpolated(rungs, starts[place] + sizes[place], numbers)
        if low != high or low in held:
            continue
        if band == generation._BAND_POSITIVE and low <= 0.0:
            continue
        if band == generation._BAND_NEGATIVE and low >= 0.0:
            continue
        if not generation._carries_plainly(low, whole_column):
            continue
        held[low] = 1
        settled[place] = 1
    flags: list[bool] = []
    for place in range(total):
        band = bands[place]
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if band == generation._BAND_ZERO:
            held[0.0] = 1
            flags += [True]
            continue
        if pinned:
            end = rungs[0] if place == 0 else rungs[-1]
            held[end] = 1
            flags += [generation._carries_plainly(end, whole_column)]
            continue
        if place in settled:
            flags += [True]
            continue
        low = generation._interpolated(rungs, starts[place], numbers)
        high = generation._interpolated(rungs, starts[place] + sizes[place], numbers)
        want = _free_whole_as_built(low, high, band, rungs, held, total + 1, True)
        if want is None:
            flags += [False]
            continue
        held[want] = 1
        flags += [True]
    return (flags, held)


def _reach_window_as_built(rungs, numbers, band, held, floor, ceiling, reach):
    if floor >= ceiling:
        return None
    lowest = generation._interpolated(rungs, floor, numbers)
    highest = generation._interpolated(rungs, ceiling, numbers)
    seen: dict[float, int] = {name: 1 for name in held}
    best: tuple[int, int, int] | None = None
    for _step in range(max(reach, 1)):
        found = _free_whole_as_built(lowest, highest, band, rungs, seen, reach, False)
        if found is None:
            break
        seen[found] = 1
        low = max(generation._reach_rank(rungs, numbers, found, False), floor)
        high = min(generation._reach_rank(rungs, numbers, found, True), ceiling)
        low = min(low, ceiling)
        high = max(high, floor)
        if low > high:
            low, high = (high, low)
        if high == low:
            if high < ceiling:
                high = high + 1
            else:
                low = low - 1
        if generation._interpolated(rungs, low, numbers) > found:
            continue
        if generation._interpolated(rungs, high, numbers) < found:
            continue
        if best is None or high - low < best[0]:
            best = (high - low, low, high)
    if best is None:
        return None
    return (best[1], best[2])


def _reach_sizes_as_built(sizes, bands, rungs, whole_column, numbers, demand, plus_demand, grid):
    if rungs is None or whole_column or (demand < 1 and plus_demand < 1):
        return sizes
    moved = [size for size in sizes]
    for _round in range(len(sizes) + 2):
        flags, held = generation._reach_held(moved, bands, rungs, whole_column, numbers)
        if generation._reach_met(moved, bands, flags, demand, plus_demand):
            break
        stepped = generation._carrier_sizes(moved, bands, flags, demand, plus_demand, grid)
        if stepped != moved:
            moved = stepped
            continue
        grown = generation._reach_grow(moved, bands, flags, held, rungs, numbers, demand, plus_demand)
        if grown == moved:
            break
        moved = grown
    return moved


def _whole_inside_as_built(value, band, share, ends, reach, taken, later=(), kept=()):
    want = generation._whole_valued(value)
    step = 0
    while step <= reach:
        for candidate in [want] if step == 0 else [want + step, want - step]:
            if candidate in taken or not generation._carries_plainly(candidate, False):
                continue
            if generation._is_a_stand_in(candidate, kept):
                continue
            if band == generation._BAND_NEGATIVE and candidate >= 0.0:
                continue
            if band == generation._BAND_POSITIVE and candidate <= 0.0:
                continue
            if ends is not None and (candidate < ends[0] or candidate > ends[1]):
                continue
            outside = share is None or (candidate < share[0] or candidate > share[1])
            if outside:
                if share is None:
                    if step > 0:
                        continue
                elif candidate < share[0] - generation._HALF_UNIT or candidate > share[1] + generation._HALF_UNIT:
                    continue
                if _held_later_as_built(candidate, later):
                    continue
            return candidate
        step = step + 1
    return None


def _held_later_as_built(candidate, later):
    for share in later:
        if share[0] <= candidate <= share[1]:
            return True
    return False


def _sole_holder_as_built(moved, value):
    seen = 0
    for place in range(len(moved)):
        if moved[place] == value:
            seen = seen + 1
    return seen == 1


def _rehomed_as_built(place, moved, layout, rungs, numbers, taken, ends, reach, locked, seen, budget, order=None, kept=()):
    total = len(layout.sizes)
    band = layout.bands[place]
    share = generation._share_of(place, layout, rungs, numbers)
    later = _shares_after_as_built(place, layout, rungs, numbers, order)
    want = _whole_inside_as_built(moved[place], band, share, ends, reach, taken, later, kept=kept)
    if want is not None:
        return [(place, want)]
    if len(seen) >= generation._CHAIN_DEPTH:
        return None
    best_moves: 'list[tuple[int, float]] | None' = None
    best_cost = 0
    for other in range(total):
        budget[0] = budget[0] - 1
        if budget[0] < 0:
            return best_moves
        if other == place or other in seen or other in locked:
            continue
        if other == 0 or (other == total - 1 and total >= 2):
            continue
        if layout.bands[other] == generation._BAND_ZERO:
            continue
        offered = moved[other]
        if not generation._carries_plainly(offered, False):
            continue
        if not _sole_holder_as_built(moved, offered):
            continue
        probe: dict[float, int] = {}
        for value in taken:
            if value != offered:
                probe[value] = taken[value]
        mine = _whole_inside_as_built(moved[place], band, share, ends, reach, probe, later, kept=kept)
        if mine is None or mine != offered:
            continue
        ahead: dict[int, int] = {}
        for step in seen:
            ahead[step] = seen[step]
        ahead[place] = 1
        onward = _rehomed_as_built(other, moved, layout, rungs, numbers, taken, ends, reach, locked, ahead, budget, order, kept=kept)
        if onward is not None:
            best_moves, best_cost = generation._cheaper(best_moves, best_cost, onward + [(place, mine)], layout)
            continue
        if layout.sizes[other] < layout.sizes[place]:
            fraction = generation._fraction_inside(generation._share_of(other, layout, rungs, numbers), taken, layout.bands[other])
            if fraction is not None:
                best_moves, best_cost = generation._cheaper(best_moves, best_cost, [(other, fraction), (place, mine)], layout)
    return best_moves


def _whole_enough_as_built(column, facts, layout, rungs, values):
    if facts.integer_valued:
        return values
    owed = min(generation._whole_demand(facts), column.n_numeric)
    if owed < 1:
        return values
    total = len(values)
    free = 0
    negatives = 0
    for place in range(total):
        if layout.bands[place] != generation._BAND_NEGATIVE:
            free = free + layout.sizes[place]
        else:
            negatives = negatives + layout.sizes[place]
    quotas = generation._style_quotas(facts.numeric_styles)
    taken = {value: 1 for value in values}
    moved = [value for value in values]
    locked: dict[int, int] = {}
    budget = [generation._CHAIN_WORK]
    signed = 0
    if '+' in facts.decimal_plus:
        signed = facts.decimal_plus['+']
    below = 0
    if signed > 0:
        below = max(0, owed - max(0, free - signed))
    trailing = generation._trailing_owed(facts, negatives)
    above = 0
    if trailing > 0:
        above = max(0, owed - max(0, negatives - trailing))
    for wanted, reachable in ((min(quotas['leading_plus'], free), generation._REACHABLE[0]), (below, (generation._BAND_NEGATIVE,)), (min(above, free), generation._REACHABLE[0]), (owed, generation._REACHABLE[1])):
        order = None
        if trailing > 0 and reachable != generation._REACHABLE[0]:
            order = generation._negatives_last(layout.bands)
        places = range(total) if order is None else order
        carried = 0
        for place in range(total):
            if layout.bands[place] not in reachable:
                continue
            if generation._carries_plainly(moved[place], False):
                carried = carried + layout.sizes[place]
        for _round in range(total):
            settled = carried
            for place in places:
                if carried >= wanted:
                    break
                if place == 0 or (place == total - 1 and total >= 2):
                    continue
                if place in locked:
                    continue
                if layout.bands[place] not in reachable:
                    continue
                if generation._carries_plainly(moved[place], False):
                    continue
                band = layout.bands[place]
                if band == generation._BAND_ZERO:
                    continue
                share = None
                ends = None
                if rungs is not None:
                    share = (generation._interpolated(rungs, layout.starts[place], column.n_numeric), generation._interpolated(rungs, layout.starts[place] + layout.sizes[place], column.n_numeric))
                    ends = (rungs[0], rungs[-1])
                want = _whole_inside_as_built(moved[place], band, share, ends, total + 1, taken, _shares_after_as_built(place, layout, rungs, column.n_numeric, order), kept=facts.kept_stand_ins)
                if want is None:
                    moves = _rehomed_as_built(place, moved, layout, rungs, column.n_numeric, taken, ends, total + 1, locked, {}, budget, order, kept=facts.kept_stand_ins)
                    if moves is None:
                        continue
                    for step in range(len(moves)):
                        seat = moves[step][0]
                        value = moves[step][1]
                        moved[seat] = value
                        if not generation._carries_plainly(value, False):
                            locked[seat] = 1
                    taken = {value: 1 for value in moved}
                    carried = 0
                    for seat in range(total):
                        if layout.bands[seat] not in reachable:
                            continue
                        if generation._carries_plainly(moved[seat], False):
                            carried = carried + layout.sizes[seat]
                    continue
                taken[want] = 1
                moved[place] = want
                carried = carried + layout.sizes[place]
            if carried == settled:
                break
    return moved


def _shares_after_as_built(place, layout, rungs, numbers, order=None):
    if rungs is None:
        return ()
    total = len(layout.sizes)
    upcoming: 'tuple[int, ...] | range' = range(place + 1, total)
    if order is not None:
        start = 0
        for step in range(len(order)):
            if order[step] == place:
                start = step + 1
        upcoming = order[start:]
    after: list[tuple[float, float]] = []
    for later in upcoming:
        if later == 0 or (later == total - 1 and total >= 2):
            continue
        if layout.bands[later] == generation._BAND_ZERO:
            continue
        after += [(generation._interpolated(rungs, layout.starts[later], numbers), generation._interpolated(rungs, layout.starts[later] + layout.sizes[later], numbers))]
    return tuple(after)


# The index as this landing first shipped it (9fa2008), not 110cb46's: the
# one question whose work the Codex review of P4-D387 (item 1) found
# growing as the square of the rows, where shares that do not rise asked
# every stratum. It reads the index's own fields, so it runs over the
# index built now.


def _held_after_scanning(shares, place, candidate):
    if shares.rungs is None:
        return False
    if not shares.ahead:
        shares.ahead += [generation._ahead_index(shares)]
    index = shares.ahead[0]
    rank = shares.rank[place]
    count = len(index.ranks)
    if not index.rising:
        for step in range(count):
            if (
                index.ranks[step] > rank
                and index.lows[step] <= candidate <= index.highs[step]
            ):
                return True
        return False
    first = generation._first_reaching(index.highs, candidate) + count
    last = generation._first_past(index.lows, candidate) + count
    furthest = -1
    while first < last:
        if first % 2 == 1:
            furthest = max(furthest, index.tree[first])
            first = first + 1
        if last % 2 == 1:
            last = last - 1
            furthest = max(furthest, index.tree[last])
        first = first // 2
        last = last // 2
    return furthest > rank


def records_as_built(text, delimiter, escape, initial_space, at=0, limit=-1):
    found = dialect._text(text)
    span = found[at:] if limit < 0 else found[at:at + 1048576]
    cursor = dialect._Cursor(dialect.physical_lines(span), 0, delimiter, escape, initial_space)
    taken: list[dialect.Record] = []
    while limit < 0 or len(taken) < limit:
        record = dialect._record_at(cursor)
        if record is None:
            break
        taken += [record]
    return taken


def delimiter_reading_as_built(text, at):
    chosen = ','
    best_share = 0.0
    best_width = 0
    best_numbers = -1
    best_sample: 'list[dialect.Record]' = []
    for candidate in dialect.DELIMITERS:
        found = _best_reading_as_built(text, candidate, at)
        if found is None:
            continue
        share, width, sample = found
        numbers = -1
        if share == best_share and width == best_width:
            numbers = dialect._numbers_read(sample)
            if best_numbers < 0:
                best_numbers = dialect._numbers_read(best_sample)
        if share > best_share or (share == best_share and width > best_width) or (share == best_share and width == best_width and (numbers > best_numbers)):
            chosen = candidate
            best_share = share
            best_width = width
            best_numbers = numbers
            best_sample = sample
    tied: list[str] = []
    for candidate in dialect.DELIMITERS:
        if candidate == chosen:
            continue
        found = _best_reading_as_built(text, candidate, at)
        if found is None:
            continue
        if found[0] == best_share:
            tied += [candidate]
    if not tied:
        return (chosen, ())
    return (chosen, tuple([chosen] + tied))


def _best_reading_as_built(text, candidate, at):
    best: 'tuple[float, int, list[dialect.Record]] | None' = None
    for spaced in (False, True):
        for escaping in dialect.ESCAPES:
            sample = records_as_built(text, candidate, escaping, spaced, at, dialect._SAMPLE_RECORDS)
            share, width = dialect._width_share(sample)
            if width < 2:
                continue
            opening = 0
            while opening < len(sample) and dialect._leads_the_table(sample[opening]):
                opening = opening + 1
            if opening < len(sample) and len(sample[opening].fields) != width:
                continue
            if best is None or (share, width) > (best[0], best[1]):
                best = (share, width, sample)
    return best


def detected_initial_space_as_built(text, at, delimiter):
    sample = records_as_built(text, delimiter, dialect.ESCAPE_DOUBLED, False, at, dialect._SAMPLE_RECORDS)
    seen = False
    for record in sample:
        if len(record.fields) < 2:
            continue
        for index in range(1, len(record.fields)):
            value = record.fields[index]
            if value[:1] != dialect._SPACE or value[1:2] == dialect._SPACE:
                return False
            seen = True
    return seen


def row_order_of_as_built(columns, sequences, n_rows, declared_commas=None):
    if n_rows < 3:
        return dialect.NO_ORDER
    for index in range(len(columns)):
        if sequences[index] >= 0:
            continue
        declared = bool(declared_commas is not None and index < len(declared_commas) and declared_commas[index])
        for collation in dialect._collations_for(declared):
            keys = dialect._order_keys(columns[index], collation)
            if keys is None:
                continue
            direction = dialect._monotone(keys)
            if direction:
                return dialect.RowOrder(column=index + 1, direction=direction, collation=collation)
            break
    return dialect.NO_ORDER


def _check_against_pandas_as_built(raw_path, found, shown, refusals=reading.REFUSALS_MAY_QUOTE):
    validated = reading.validate_local_path(raw_path, purpose='input')
    file_path = reading.pathlib.Path(validated)
    surveyed = found.survey
    if surveyed is None:
        raise ValueError('synthtwin internal check: a reading without its survey')
    form = surveyed.form
    headed = found.header_source == reading.HEADER_FROM_FILE
    lead = 1 if form.separator_line else 0
    lead = lead + reading.dialect.preamble_lines_holding_text(form.preamble)
    header_row = lead if headed or lead else None
    offset = len(form.header_rows)
    first_as_names = not headed and bool(lead)
    wanted = None
    if form.end_of_file_mark:
        wanted = found.n_rows + offset - (1 if first_as_names else 0)
    backslash = form.escape == reading.dialect.ESCAPE_BACKSLASH
    try:
        frame = reading.pandas.read_csv(file_path, encoding=reading.dialect.READING_CODECS[found.encoding], encoding_errors='strict', header=header_row, index_col=False, dtype=str, keep_default_na=False, na_filter=False, skip_blank_lines=True, engine='c', sep=form.delimiter, quotechar='"', doublequote=not backslash, escapechar='\\' if backslash else None, skipinitialspace=form.initial_space, comment=None, nrows=wanted)
    except MemoryError as error:
        raise reading.errors.ProfileError(reading.errors.out_of_memory(shown, reading._file_size(file_path))) from error
    except Exception as error:
        if refusals == reading.REFUSALS_NAME_POSITIONS:
            raise reading.errors.ProfileError(reading.errors.checked_file_unreadable_as_csv(shown)) from error
        raise reading.errors.ProfileError(reading.errors.unreadable_as_csv(shown, f'{error}')) from error
    found_rows = len(frame)
    keys = list(frame.columns)
    width = len(found.column_names)
    if form.header_trailing_delimiter and len(keys) == width + 1:
        keys = keys[:width]
    expected_rows = found.n_rows + offset - (1 if first_as_names else 0)
    if found_rows != expected_rows or len(keys) != width:
        raise reading.errors.ProfileError(reading.errors.readers_disagree(shown, f'{found.n_rows} rows of {width} values', f'{found_rows - offset} rows of {len(keys)} values'))
    named_cells: list[str] = []
    if headed:
        named_cells = list(surveyed.header)
    elif first_as_names:
        named_cells = [found.columns[place][0] for place in range(width)]
    for index in range(len(named_cells)):
        second = f'{keys[index]}'
        expected = named_cells[index]
        if second != expected and (not reading._pandas_may_rename(expected, named_cells)):
            if refusals == reading.REFUSALS_NAME_POSITIONS:
                raise reading.errors.ProfileError(reading.errors.checked_file_readers_disagree_about_a_name(shown, index + 1))
            raise reading.errors.ProfileError(reading.errors.readers_disagree_about_a_name(shown, index + 1, found.column_names[index], second))
    for index in range(len(keys)):
        mine = found.columns[index]
        theirs = [f'{cell}' for cell in list(frame[keys[index]])]
        if first_as_names:
            theirs = [mine[0]] + theirs
        if offset:
            above = [row[index] for row in form.header_rows]
            for place in range(offset):
                if theirs[place] != above[place]:
                    if refusals == reading.REFUSALS_NAME_POSITIONS:
                        raise reading.errors.ProfileError(reading.errors.checked_file_readers_disagree_about_a_name(shown, index + 1))
                    raise reading.errors.ProfileError(reading.errors.readers_disagree_about_a_name(shown, index + 1, above[place], theirs[place]))
        last = len(theirs) - 1
        if form.end_of_file_mark and (not form.final_line_ending) and (theirs[last][len(theirs[last]) - 1:] == '\x1a'):
            theirs[last] = theirs[last][:len(theirs[last]) - 1]
        for position in range(found.n_rows):
            if theirs[position + offset] != mine[position]:
                if refusals == reading.REFUSALS_NAME_POSITIONS:
                    raise reading.errors.ProfileError(reading.errors.checked_file_readers_disagree_about_a_value(shown, position + 1, index + 1))
                raise reading.errors.ProfileError(reading.errors.readers_disagree_about_a_value(shown, position + 1, found.column_names[index]))


# -- 1 and 2. the walk for whole numbers and the reach step ------------------


_WATCHED = ("_whole_enough", "_free_whole", "_reach_window", "_reach_held")
_AS_BUILT = {
    "_whole_enough": _whole_enough_as_built,
    "_free_whole": _free_whole_as_built,
    "_reach_window": _reach_window_as_built,
    "_reach_held": _reach_held_as_built,
}


def _same(ours: object, theirs: object) -> bool:
    """Equal answers, a negative zero told from a zero and a dictionary's order counted."""
    if isinstance(ours, dict) and isinstance(theirs, dict):
        return _same(list(ours.items()), list(theirs.items()))
    if isinstance(ours, (list, tuple)) and isinstance(theirs, (list, tuple)):
        return len(ours) == len(theirs) and all(
            _same(ours[place], theirs[place]) for place in range(len(ours))
        )
    return repr(ours) == repr(theirs)


def _held_to_the_oracle(monkeypatch: pytest.MonkeyPatch) -> "dict[str, int]":
    """Make every call of the four watched functions also ask its oracle, and require one answer."""
    asked = {name: 0 for name in _WATCHED}
    asked["rehomed"] = 0
    asked["window"] = 0
    for name in _WATCHED:
        shipped = getattr(generation, name)

        def watched(*arguments: object, _name: str = name, _shipped: object = shipped) -> object:
            copied = [list(item) if isinstance(item, list) else dict(item) if isinstance(item, dict) else item
                      for item in arguments]
            theirs = _AS_BUILT[_name](*copied)
            ours = _shipped(*arguments)  # type: ignore[operator]
            assert _same(ours, theirs), (_name, ours, theirs)
            asked[_name] += 1
            if _name == "_reach_window" and ours is not None:
                asked["window"] += 1
            return ours

        monkeypatch.setattr(generation, name, watched)
    homed = generation._rehomed

    def counted(*arguments: object, **named: object) -> object:
        moves = homed(*arguments, **named)  # type: ignore[arg-type]
        if moves is not None and len(moves) > 1:
            asked["rehomed"] += 1
        return moves

    monkeypatch.setattr(generation, "_rehomed", counted)
    return asked


def test_every_walk_for_whole_numbers_answers_as_it_did(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Each call of the walk and of the reach step's three questions gives what 110cb46 gave.

    Over mostly whole columns -- charges, counts of days, changes either
    side of zero, a flat ladder -- and the style-capacity and notation
    batteries, at three seeds each. The four are pure questions of their
    arguments, so asking each one's oracle beside it at every call holds
    every column, every seed and every round of the reach step to the
    old answer; the chain that trades a number and the window search are
    required to have been reached.
    """
    built = []
    for step, (name, values) in enumerate(_whole_battery()):
        loaded = _described(tmp_path / f"case-{step}", values)
        if isinstance(loaded.columns[0].facts, contract.NumericFacts):
            built += [(name, loaded)]
    assert len(built) >= 25, [name for name, _loaded in built]
    asked = _held_to_the_oracle(monkeypatch)
    for _name, loaded in built:
        for seed in (0, 1, 7):
            generation.generate(loaded, seed)
    assert asked["_whole_enough"] >= 75, asked
    assert asked["_reach_held"] >= 20 and asked["window"] >= 1, asked
    assert asked["rehomed"] >= 1 and asked["_free_whole"] >= 1, asked


def test_the_twins_are_the_twins_the_old_walks_wrote(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """With the four replaced functions put back, every twin and its report are the same bytes."""
    shipped = []
    for step, (_name, values) in enumerate(_whole_battery()[:7]):
        loaded = _described(tmp_path / f"case-{step}", values)
        twin = generation.generate(loaded, 3)
        shipped += [(loaded, rendering.twin_csv(twin), rendering.report(loaded, twin))]
    for name in _WATCHED:
        monkeypatch.setattr(generation, name, _AS_BUILT[name])
    for loaded, csv_text, report in shipped:
        twin = generation.generate(loaded, 3)
        assert rendering.twin_csv(twin) == csv_text
        assert rendering.report(loaded, twin) == report


def _layout(draw: random.Random) -> "tuple[generation._NumericLayout, int]":
    """A made-up layout: strata in band order, negatives, maybe a zero, positives."""
    total = draw.randrange(1, 40)
    sizes = tuple(draw.randrange(1, 6) for _place in range(total))
    starts: "list[int]" = []
    running = 0
    for size in sizes:
        starts += [running]
        running += size
    negatives = draw.randrange(0, total + 1)
    zero = 1 if negatives < total and draw.random() < 0.4 else 0
    bands = tuple(
        "negative" if place < negatives else "zero" if place < negatives + zero else "positive"
        for place in range(total)
    )
    layout = generation._NumericLayout(
        sizes=sizes, starts=tuple(starts), bands=bands, raw_budgets=(), folded_budgets=()
    )
    return layout, running


def _rungs(draw: random.Random, rising: bool) -> "tuple[float, ...]":
    """A ladder of a hundred and one rungs, read upward or shuffled."""
    rungs = sorted(round(draw.uniform(-60.0, 60.0), draw.choice((0, 1, 2))) for _rung in range(101))
    if draw.random() < 0.3:
        rungs = sorted(rungs[:5] * 20 + rungs[:1])
    if not rising:
        draw.shuffle(rungs)
    return tuple(rungs)


def test_the_index_of_the_strata_ahead_answers_as_every_share_did() -> None:
    """`_held_after` gives what the shares of every later stratum gave, a ladder read upward or shuffled.

    Over 600 made-up layouts, both walk orders and candidates at and
    around every share's ends. A shuffled ladder is not read upward, so
    the index falls back to asking every stratum, and is held to the same
    answer there too; both branches are required to have run.
    """
    draw = random.Random(387)
    branches = {True: 0, False: 0}
    for case in range(600):
        layout, numbers = _layout(draw)
        rungs = _rungs(draw, case % 3 != 0)
        for order in (None, generation._negatives_last(layout.bands)):
            shares = generation._walk_shares(layout, rungs, numbers, order)
            for place in range(len(layout.sizes)):
                later = _shares_after_as_built(place, layout, rungs, numbers, order)
                candidates = [draw.uniform(-70.0, 70.0) for _try in range(3)]
                for share in later[:6]:
                    candidates += [share[0], share[1], share[0] - 0.5, share[1] + 0.25]
                for candidate in candidates:
                    ours = generation._held_after(shares, place, candidate)
                    assert ours == _held_later_as_built(candidate, later), (case, place, candidate)
                    assert generation._own_share(shares, place) == generation._share_of(
                        place, layout, rungs, numbers
                    )
            if shares.ahead:
                branches[shares.ahead[0].rising] += 1
    assert branches[True] > 60 and branches[False] > 60, branches


def _unit_steps(draw: random.Random) -> "tuple[float, ...]":
    """A ladder read upward whose 101 rungs stand a unit in the last place apart, or level."""
    rungs = [draw.choice((0.1, 1.1, 37.25, 0.001, 123456.789, -2.5))]
    for _rung in range(100):
        rungs += [math.nextafter(rungs[len(rungs) - 1], math.inf) if draw.random() < 0.7 else rungs[len(rungs) - 1]]
    return tuple(rungs)


def _one_cell_strata(total: int, negatives: int = 0) -> "tuple[generation._NumericLayout, int]":
    """``total`` strata of a cell each, the first ``negatives`` of them negative and the rest positive."""
    bands = tuple("negative" if place < negatives else "positive" for place in range(total))
    layout = generation._NumericLayout(
        sizes=tuple(1 for _place in range(total)), starts=tuple(range(total)), bands=bands,
        raw_budgets=(), folded_budgets=(),
    )
    return layout, total


def test_the_index_answers_as_every_share_did_where_a_ladder_read_upward_steps_back() -> None:
    """`_held_after` gives what the shares of every later stratum gave where the convex form steps back.

    The Codex review of plan P4-D387 (item 1): between two rungs a unit in
    the last place apart, one end of a share can read the higher rung and
    the next end the lower, so a ladder read upward gives shares that do
    not rise. Over 60 sets of such rungs and 60 to 300 one-cell strata,
    both walk orders, the index is required to step back on at least 20
    of them and to answer as 110cb46's every share did there.
    """
    draw = random.Random(3881)
    stepped_back = 0
    for _case in range(60):
        total = draw.randrange(60, 300)
        layout, numbers = _one_cell_strata(total, draw.choice((0, 0, total // 3)))
        rungs = _unit_steps(draw)
        for order in (None, generation._negatives_last(layout.bands)):
            shares = generation._walk_shares(layout, rungs, numbers, order)
            for place in sorted(draw.sample(range(total), 25)):
                later = _shares_after_as_built(place, layout, rungs, numbers, order)
                candidates = [rungs[0], rungs[50], rungs[100], math.nextafter(rungs[0], -math.inf)]
                for share in later[:: max(1, len(later) // 8)]:
                    candidates += [share[0], share[1]]
                for candidate in candidates:
                    ours = generation._held_after(shares, place, candidate)
                    assert ours == _held_later_as_built(candidate, later), (place, candidate)
            stepped_back += 0 if shares.ahead[0].rising else 1
    assert stepped_back >= 20, stepped_back


def test_a_whole_number_inside_a_share_is_the_one_the_full_walk_found() -> None:
    """`_whole_inside` stopping past the half unit answers as walking on to the column's reach did."""
    draw = random.Random(3871)
    for _case in range(20000):
        value = draw.uniform(-50.0, 50.0)
        low = value - draw.uniform(0.0, 6.0)
        share = None if draw.random() < 0.15 else (low, low + draw.uniform(0.0, 9.0))
        ends = None if draw.random() < 0.2 else (draw.uniform(-80.0, -20.0), draw.uniform(20.0, 80.0))
        band = draw.choice(("negative", "positive", "zero"))
        taken = {float(number): 1 for number in range(-60, 61) if draw.random() < 0.6}
        later = tuple((point, point + draw.uniform(0.0, 3.0)) for point in
                      (draw.uniform(-50.0, 50.0) for _share in range(draw.randrange(0, 4))))
        reach = draw.randrange(0, 40)
        kept = (-999.0,) if draw.random() < 0.5 else ()
        ours = generation._whole_inside(value, band, share, ends, reach, taken, later, kept=kept)
        theirs = _whole_inside_as_built(value, band, share, ends, reach, taken, later, kept=kept)
        assert repr(ours) == repr(theirs), (value, band, share, ends, reach, later)


def test_a_free_whole_number_is_the_one_the_listed_candidates_gave() -> None:
    """`_free_whole` asking one step at a time, and from where it left off, answers as the list did."""
    draw = random.Random(3872)
    for _case in range(20000):
        rungs = tuple(sorted(draw.uniform(-40.0, 40.0) for _rung in range(11)))
        low = draw.uniform(-45.0, 45.0)
        high = low + draw.uniform(-1.0, 12.0)
        band = draw.choice(("negative", "positive", "zero"))
        held = {float(number): 1 for number in range(-45, 46) if draw.random() < 0.7}
        reach = draw.randrange(0, 30)
        nearest = draw.random() < 0.5
        theirs = _free_whole_as_built(low, high, band, rungs, held, reach, nearest)
        assert repr(generation._free_whole(low, high, band, rungs, held, reach, nearest)) == repr(theirs)
        if nearest or theirs is None:
            continue
        found, step = generation._free_whole_at(low, high, band, rungs, held, reach, False, 0)
        again = dict(held)
        again[found] = 1
        assert repr(generation._free_whole_at(low, high, band, rungs, again, reach, False, step + 1)[0]) == repr(
            _free_whole_as_built(low, high, band, rungs, again, reach, False)
        )


def test_the_window_search_gives_the_window_it_gave() -> None:
    """`_reach_window`, resuming past each answer and stopping at a window one cell wide, gives 110cb46's window.

    Over 12,000 made-up rung sets -- flat at whole numbers and halves in
    places, or rising smoothly -- with every band, held numbers from none
    to most, any floor, ceiling and reach. A search that skipped a
    candidate when it resumed, or stopped at a window two cells wide,
    gives another window on about one ladder in two hundred here.
    """
    draw = random.Random(3879)
    for _case in range(12_000):
        numbers = draw.randrange(2, 80)
        if draw.random() < 0.5:
            values = [draw.choice((float(draw.randrange(-5, 30)), draw.randrange(-10, 60) / 2.0))
                      for _rung in range(101)]
        else:
            low = draw.uniform(-10.0, 10.0)
            values = [low + draw.uniform(0.0, 30.0) for _rung in range(101)]
        rungs = tuple(sorted(values))
        band = draw.choice(("positive", "negative", "zero", "positive"))
        share = draw.choice((0.0, 0.3, 0.7))
        held = {float(number): 1 for number in range(-12, 40) if draw.random() < share}
        floor = draw.randrange(0, numbers)
        ceiling = draw.randrange(floor, numbers + 1)
        reach = draw.randrange(0, 40)
        ours = generation._reach_window(rungs, numbers, band, held, floor, ceiling, reach)
        theirs = _reach_window_as_built(rungs, numbers, band, held, floor, ceiling, reach)
        assert ours == theirs, (rungs, numbers, band, held, floor, ceiling, reach)


def test_a_stratum_with_no_whole_number_near_its_share_stops_asking() -> None:
    """`_whole_inside` refusing a stratum runs the same lines at any reach, where 110cb46 walked to the reach.

    Every whole number from 0 to 20 is taken and the share holds none, so
    past the half unit around it no step can answer: the walk stops there,
    and as built it stepped on to the column's reach, one more than its
    strata, for every stratum so refused.
    """
    taken = {float(number): 1 for number in range(0, 21)}

    def lines(function: "object", reach: int) -> int:
        return _lines_run(function, 10.5, "positive", (10.2, 10.8), None, reach, taken, ())

    ours = [lines(generation._whole_inside, reach) for reach in (500, 1000, 2000)]
    theirs = [lines(_whole_inside_as_built, reach) for reach in (500, 1000, 2000)]
    assert generation._whole_inside(10.5, "positive", (10.2, 10.8), None, 2000, taken, ()) is None
    assert ours[0] == ours[1] == ours[2] and ours[0] < 300, ours
    assert theirs[2] >= 1.9 * theirs[1] and theirs[1] >= 1.9 * theirs[0], theirs


def test_the_counts_kept_as_strata_move_are_the_counts_worked_out_again() -> None:
    """`_seat_given` and `_taken_again` keep what 110cb46 worked out again from every stratum.

    Over 3,000 made-up walks of single takes and of chains moving up to
    five strata at once: the holders of each value are the strata holding
    it, counted, and after each chain the numbers taken are the numbers
    held -- the dictionary 110cb46 built again from every stratum.
    """
    draw = random.Random(3880)
    chains = 0
    for _walk in range(3000):
        strata = draw.randrange(2, 30)
        moved = [float(draw.randrange(0, 12)) + draw.choice((0.0, 0.5)) for _stratum in range(strata)]
        held: "dict[float, int]" = {}
        for value in moved:
            held[value] = (held[value] if value in held else 0) + 1
        taken = {value: 1 for value in moved}
        left: "list[float]" = []
        for _move in range(draw.randrange(1, 40)):
            if draw.random() < 0.6:
                seat = draw.randrange(strata)
                want = float(draw.randrange(0, 14))
                taken[want] = 1
                generation._seat_given(moved, held, left, seat, want)
            else:
                moves = [(draw.randrange(strata), float(draw.randrange(0, 14)) + draw.choice((0.0, 0.25)))
                         for _step in range(draw.randrange(1, 6))]
                for seat, value in moves:
                    generation._seat_given(moved, held, left, seat, value)
                generation._taken_again(taken, held, left, moves)
                assert sorted(taken) == sorted({value: 1 for value in moved}) and not left
                chains += 1
            counted: "dict[float, int]" = {}
            for value in moved:
                counted[value] = (counted[value] if value in counted else 0) + 1
            assert held == counted
    assert chains > 10_000, chains


def whole_walk_lines(rows: int, as_built: bool = False) -> int:
    """The lines run walking one mostly whole column of ``rows`` different values to its whole numbers.

    The column is described with the real producer and its twin built,
    and the walk is then asked again, line-counted, with the arguments
    the twin's own build handed it. With ``as_built`` it is 110cb46's
    walk, which interpolated every later stratum's share for every
    stratum it visited.
    """
    handed: "list[tuple[object, ...]]" = []
    walked = generation._whole_enough

    def captured(*arguments: object) -> object:
        nonlocal handed
        handed += [arguments]
        return walked(*arguments)  # type: ignore[arg-type]

    with tempfile.TemporaryDirectory() as home:
        loaded = _described(pathlib.Path(home), _charges(rows, rows, 14.0, 1.0))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_whole_enough", captured)
        generation.generate(loaded, 0)
    assert len(handed) == 1, len(handed)
    column, facts, layout, rungs, values = handed[0]
    function = _whole_enough_as_built if as_built else generation._whole_enough
    return _lines_run(function, column, facts, layout, rungs, list(values))  # type: ignore[arg-type]


def test_the_walk_for_whole_numbers_grows_with_the_rows() -> None:
    """Lines run at 2N rows against N: about two now, and four as 110cb46 walked."""
    small, large = whole_walk_lines(200), whole_walk_lines(400)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small = whole_walk_lines(200, as_built=True)
    old_large = whole_walk_lines(400, as_built=True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


def crowded_walk_lines(rows: int) -> int:
    """The lines run walking a column of day counts crowded onto a day for every two rows to its whole numbers.

    As `whole_walk_lines`, on a column with more strata than whole numbers
    free for them, so most strata ask `_whole_inside` for a number it does
    not have.
    """
    handed: "list[tuple[object, ...]]" = []
    walked = generation._whole_enough

    def captured(*arguments: object) -> object:
        nonlocal handed
        handed += [arguments]
        return walked(*arguments)  # type: ignore[arg-type]

    with tempfile.TemporaryDirectory() as home:
        loaded = _described(pathlib.Path(home), _day_counts(rows, rows, rows // 2))
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_whole_enough", captured)
        generation.generate(loaded, 0)
    assert len(handed) == 1, len(handed)
    column, facts, layout, rungs, values = handed[0]
    return _lines_run(generation._whole_enough, column, facts, layout, rungs, list(values))  # type: ignore[arg-type]


def test_the_walk_over_a_crowded_column_grows_with_the_rows() -> None:
    """Lines run at 1,200 rows of crowded day counts against 600: about one and a half now.

    As built the walk ran 67.5 and 237.5 million lines there, 3.5 times
    for twice the rows, and with `_whole_inside` walking on to the reach
    past the half unit 2.8 times (plan P4-D387).
    """
    small, large = crowded_walk_lines(600), crowded_walk_lines(1200)
    assert large / small < LINEAR_AT_MOST, (small, large)


def _stepping_back(rows: int) -> "list[str]":
    """The Codex review's column of P4-D387 (item 1), which the producer reads as continuous.

    A hundredth of the rows hold `0.1` and a hundredth `0.10000000000000002`,
    each written one zero longer than the last; the rest count up in fives,
    three in ten of them with a quarter. Its rungs rise, and between the
    two that stand a unit in the last place apart the convex form reads
    some shares stepping back.
    """
    hundredth = rows // 100
    values = ["0.1" + "0" * place for place in range(hundredth)]
    values += ["0.10000000000000002" + "0" * place for place in range(hundredth)]
    values += [str(5 * place) if place % 10 < 7 else str(5 * place + 0.25) for place in range(rows - 2 * hundredth)]
    return values


def _walk_handed(values: "list[str]") -> "tuple[object, ...]":
    """What the twin's own build hands G6.4's walk for a one-column table of ``values``, described by the producer."""
    handed: "list[tuple[object, ...]]" = []
    walked = generation._whole_enough

    def captured(*arguments: object) -> object:
        nonlocal handed
        handed += [arguments]
        return walked(*arguments)  # type: ignore[arg-type]

    with tempfile.TemporaryDirectory() as home:
        loaded = _described(pathlib.Path(home), values)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_whole_enough", captured)
        generation.generate(loaded, 0)
    assert len(handed) == 1, len(handed)
    return handed[0]


def _index_read(patch: pytest.MonkeyPatch, asked: "object") -> "dict[str, object]":
    """Count the questions ``asked`` answers for `_held_after`, and every entry they read of the index it builds.

    The index's fields are handed over as tuples that count each entry
    read from them, so the count is the lookup's work whichever way the
    index is laid out; the indexes built are kept to say how they were.
    """
    counted: "dict[str, object]" = {"questions": 0, "reads": 0, "built": []}
    building = generation._ahead_index

    class Counted(tuple):  # type: ignore[type-arg]
        def __getitem__(self, item: object) -> object:
            counted["reads"] += 1  # type: ignore[operator]
            return tuple.__getitem__(self, item)  # type: ignore[index]

    def built(shares: "generation._WalkShares") -> "generation._AheadIndex":
        index = building(shares)
        fields = {field.name: Counted(getattr(index, field.name)) for field in dataclasses.fields(index)
                  if isinstance(getattr(index, field.name), tuple)}
        index = dataclasses.replace(index, **fields)  # type: ignore[arg-type]
        counted["built"] += [index]  # type: ignore[operator]
        return index

    def question(shares: "generation._WalkShares", place: int, candidate: float) -> bool:
        counted["questions"] += 1  # type: ignore[operator]
        return asked(shares, place, candidate)  # type: ignore[operator, no-any-return]

    patch.setattr(generation, "_ahead_index", built)
    patch.setattr(generation, "_held_after", question)
    return counted


def stepped_back_reads(handed: "tuple[object, ...]", scanning: bool = False) -> "dict[str, object]":
    """The questions G6.4's walk asks of the strata ahead and the index entries read answering them.

    With ``scanning`` the questions are answered as 9fa2008 answered them,
    asking every stratum where the shares do not rise.
    """
    column, facts, layout, rungs, values = handed
    with pytest.MonkeyPatch.context() as patch:
        counted = _index_read(patch, _held_after_scanning if scanning else generation._held_after)
        generation._whole_enough(column, facts, layout, rungs, list(values))  # type: ignore[arg-type]
    return counted


def test_a_ladder_whose_shares_step_back_is_asked_in_reads_that_grow_with_the_rows() -> None:
    """The Codex review's column at 2,000 and 4,000 rows: the reads of the index grow as the rows, as 9fa2008's grew as their square.

    Its shares step back, so the index is the one laid over the pieces
    of the line (`_covering_index`), and each question may read at most
    four times the logarithm of the strata and two, an operation count
    that a scan of every stratum exceeds tens of times over. The whole walk's
    lines are required to grow under two and a half times as well. 9fa2008
    asked every stratum there: 1,250,748 and 5,005,496 shares' steps read,
    and its reads are required to grow at least three times here, so the
    measure is known to see the defect.
    """
    small_handed, large_handed = _walk_handed(_stepping_back(2000)), _walk_handed(_stepping_back(4000))
    small, large = stepped_back_reads(small_handed), stepped_back_reads(large_handed)
    for counted in (small, large):
        built = counted["built"]
        assert built and not any(index.rising for index in built), built  # type: ignore[union-attr]
        strata = len(built[0].ranks)  # type: ignore[index]
        assert counted["reads"] <= counted["questions"] * 4 * (math.log2(strata) + 2), counted  # type: ignore[operator]
    assert large["reads"] / small["reads"] < LINEAR_AT_MOST, (small["reads"], large["reads"])  # type: ignore[operator]
    small_lines = _lines_run(generation._whole_enough, *small_handed[:4], list(small_handed[4]))  # type: ignore[arg-type]
    large_lines = _lines_run(generation._whole_enough, *large_handed[:4], list(large_handed[4]))  # type: ignore[arg-type]
    assert large_lines / small_lines < LINEAR_AT_MOST, (small_lines, large_lines)
    old_small, old_large = stepped_back_reads(small_handed, True), stepped_back_reads(large_handed, True)
    assert old_small["questions"] == small["questions"] and old_large["questions"] == large["questions"]
    assert old_large["reads"] / old_small["reads"] >= SQUARE_AT_LEAST, (old_small["reads"], old_large["reads"])  # type: ignore[operator]


def test_shares_in_no_order_are_asked_in_reads_that_grow_as_the_logarithm_of_the_strata() -> None:
    """A shuffled ladder and one of unit steps, at 2,000 and 8,000 strata: each question reads under four times the logarithm and two.

    The answers coverage above holds the index to every share's answer on
    shares in no order, and this holds its work: 300 questions a ladder,
    half of them a number no share holds, half an end of a share. 9fa2008
    read every stratum's step for each question no share holds, which is
    required of it here so the count is known to see a scan.
    """
    draw = random.Random(3882)
    for total in (2000, 8000):
        layout, numbers = _one_cell_strata(total, total // 4)
        for rungs in (_rungs(draw, False), _unit_steps(draw)):
            asked: "list[tuple[int, float]]" = []
            beyond = max(abs(rung) for rung in rungs) * 2 + 1
            for _question in range(150):
                asked += [(draw.randrange(total), draw.choice((beyond, -beyond)))]
                share = generation._share_of(draw.randrange(1, total - 1), layout, rungs, numbers)
                asked += [(draw.randrange(total), draw.choice(share))]
            answers = []
            for scanning in (False, True):
                shares = generation._walk_shares(layout, rungs, numbers, None)
                with pytest.MonkeyPatch.context() as patch:
                    counted = _index_read(patch, _held_after_scanning if scanning else generation._held_after)
                    answers += [[generation._held_after(shares, place, candidate) for place, candidate in asked]]
                built = counted["built"]
                assert len(built) == 1 and not built[0].rising, built  # type: ignore[arg-type, union-attr, index]
                if scanning:
                    assert counted["reads"] >= 150 * len(built[0].ranks), counted["reads"]  # type: ignore[index, operator]
                else:
                    assert counted["reads"] <= len(asked) * 4 * (math.log2(total) + 2), counted["reads"]  # type: ignore[operator]
            assert answers[0] == answers[1]
            assert any(answers[0]) and not all(answers[0])


def _spread_ladder(low: float, high: float) -> "tuple[float, ...]":
    """A hundred and one rungs evenly from ``low`` to ``high``."""
    return tuple(low + (high - low) * rung / 100 for rung in range(101))


def reach_lines(strata: int, as_built: bool = False) -> "tuple[int, int]":
    """The lines run offering whole numbers to the reach step's two questions over ``strata`` one-cell strata.

    First which strata can hold a whole number (`_reach_held`) on a
    ladder three units a stratum wide, then the narrowest window of a
    ladder half a unit a stratum wide (`_reach_window`). The lines counted
    are those of `_free_whole` and the functions it asks, which is where
    the candidates are offered; the ladder's own reading, which grows
    with the strata either way, is left out.
    """
    sizes = [1] * strata
    bands = ["positive"] * strata
    held = _reach_held_as_built if as_built else generation._reach_held
    window = _reach_window_as_built if as_built else generation._reach_window
    first = _lines_run(
        held, sizes, bands, _spread_ladder(1.0, 3.0 * strata), False, strata, inside="_free_whole"
    )
    second = _lines_run(
        window, _spread_ladder(1.0, strata / 2.0), strata, "positive", {}, 0, strata, strata + 1,
        inside="_free_whole",
    )
    return first, second


def test_the_reach_step_s_questions_grow_with_the_strata() -> None:
    """Lines run at 2N strata against N: about two now for each question, and four as built."""
    small, large = reach_lines(150), reach_lines(300)
    old_small, old_large = reach_lines(150, as_built=True), reach_lines(300, as_built=True)
    for question in (0, 1):
        assert large[question] / small[question] < LINEAR_AT_MOST, (question, small, large)
        assert old_large[question] / old_small[question] >= SQUARE_AT_LEAST, (question, old_small, old_large)


def _staircase(steps: int) -> "tuple[float, ...]":
    """A hundred and one rungs climbing one whole number at a time, each step three rungs wide."""
    return tuple(float(min(steps, 1 + rung // 3)) for rung in range(101))


def window_lines(steps: int, as_built: bool = False) -> int:
    """The lines run offering whole numbers to one window search over a staircase of ``steps`` whole numbers.

    Every whole number on the staircase is flat over many cells, so no
    window is one cell wide and the search takes every number it is
    offered, as many as its reach.
    """
    window = _reach_window_as_built if as_built else generation._reach_window
    return _lines_run(window, _staircase(steps), 1000, "positive", {}, 0, 1000, steps + 1, inside="_free_whole")


def test_a_window_search_over_a_staircase_grows_with_its_steps() -> None:
    """Lines run at 32 steps against 16: about two now, and three and a half as built.

    Each asking of a search resumes past its last answer; asked from the
    first number again every time, the search runs about 3.5 times the
    lines for twice the steps, as 110cb46's did.
    """
    small, large = window_lines(16), window_lines(32)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small, old_large = window_lines(16, as_built=True), window_lines(32, as_built=True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


def _crowded() -> "list[tuple[str, list[str]]]":
    """Mostly whole columns crowded onto fewer whole numbers than strata, whose reach rounds come round again."""
    return [
        ("charges-crowded", _charges(600, 11, 5.0, 0.5)),
        ("day-counts-crowded", _day_counts(600, 11, 300)),
        ("charges-crowded-narrow", _charges(400, 11, 4.0, 0.6)),
        ("signed-crowded", _signed(600, 11)),
    ]


def reach_rounds(values: "list[str]", as_built: bool = False) -> "tuple[int, int, list[object], str]":
    """The rounds the reach step runs twinning a one-column table of ``values``, their bound, its divisions and the twin.

    A round is one question of which strata can hold a whole number
    (`_reach_held`); the bound is the strata and two; the divisions are
    what each asking of the step handed back. With ``as_built`` the
    rounds are 110cb46's, which walked to the bound.
    """
    asked = [0]
    strata = [0]
    divisions: "list[object]" = []
    held = generation._reach_held
    sizes_step = _reach_sizes_as_built if as_built else generation._reach_sizes

    def counted(sizes: "list[int]", *rest: object) -> object:
        asked[0] += 1
        strata[0] = len(sizes)
        return held(sizes, *rest)  # type: ignore[arg-type]

    def kept(*arguments: object) -> object:
        nonlocal divisions
        found = sizes_step(*arguments)  # type: ignore[operator]
        divisions += [list(found)]
        return found

    with tempfile.TemporaryDirectory() as home:
        loaded = _described(pathlib.Path(home), values)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_reach_held", counted)
        patch.setattr(generation, "_reach_sizes", kept)
        twin = generation.generate(loaded, 0)
    return asked[0], strata[0] + 2, divisions, rendering.twin_csv(twin)


def test_the_reach_rounds_stop_once_a_division_comes_round_again() -> None:
    """On four crowded columns: every round to the bound as built, at most a third of them now, one division.

    A round costs every stratum, so walking a repeat round to the bound,
    one more than the strata, was the square of the strata. The division
    each asking hands back, and the twin, are the same either way.
    """
    for name, values in _crowded():
        rounds, bound, divisions, twin = reach_rounds(values)
        old_rounds, old_bound, old_divisions, old_twin = reach_rounds(values, as_built=True)
        assert old_bound == bound and old_rounds == bound, (name, old_rounds, bound)
        assert rounds * 3 <= bound, (name, rounds, bound)
        assert divisions and divisions == old_divisions, name
        assert twin == old_twin, name


def test_a_repeat_stepped_past_ends_where_the_rounds_as_written_end(monkeypatch: pytest.MonkeyPatch) -> None:
    """Over 4,000 made-up round functions the rounds end on the division 110cb46's rounds end on.

    Each made-up division leads to one next division by the cell step or
    by a grown window, meets the demand, or has nothing to grow, so the
    rounds stop, come round again after any number of rounds and any
    repeat length, or run to a bound of any size. The four questions a
    round asks are answered from the made-up function, and both loops ask
    them; repeats stepped past are required to have been met.
    """
    draw = random.Random(3877)
    kinds: "list[str]" = []
    following: "list[int]" = []
    walked = [0]

    def state(sizes: "list[int]") -> int:
        return sizes[0] - 1

    def division(at: int, strata: int) -> "list[int]":
        return [at + 1] + [1] * (strata - 1)

    def held(sizes: "list[int]", *_rest: object) -> "tuple[list[bool], dict[float, int]]":
        walked[0] += 1
        return [], {}

    def met(sizes: "list[int]", *_rest: object) -> bool:
        return kinds[state(sizes)] == "met"

    def stepped(sizes: "list[int]", *_rest: object) -> "list[int]":
        if kinds[state(sizes)] != "step":
            return sizes
        return division(following[state(sizes)], len(sizes))

    def grown(sizes: "list[int]", *_rest: object) -> "list[int]":
        if kinds[state(sizes)] != "grow":
            return sizes
        return division(following[state(sizes)], len(sizes))

    monkeypatch.setattr(generation, "_reach_held", held)
    monkeypatch.setattr(generation, "_reach_met", met)
    monkeypatch.setattr(generation, "_carrier_sizes", stepped)
    monkeypatch.setattr(generation, "_reach_grow", grown)
    skipped = 0
    for _case in range(4000):
        count = draw.randrange(1, 30)
        kinds[:] = [draw.choice(("step", "grow", "grow", "step", "met", "stuck")) if draw.random() < 0.2
                    else draw.choice(("step", "grow")) for _state in range(count)]
        following[:] = [draw.randrange(count) for _state in range(count)]
        strata = draw.randrange(1, 70)
        start = division(draw.randrange(count), strata)
        arguments = (["positive"] * strata, (1.0, 2.0), False, strata, 1, 0, 0)
        walked[0] = 0
        theirs = _reach_sizes_as_built(list(start), *arguments)
        old_rounds = walked[0]
        walked[0] = 0
        ours = generation._reach_sizes(list(start), *arguments)
        assert ours == theirs, (kinds, following, strata, start)
        if walked[0] < old_rounds:
            skipped += 1
    assert skipped > 1000, skipped


def test_a_mostly_whole_column_of_100000_rows_is_twinned_and_meets_its_point_free_count(
    tmp_path: pathlib.Path,
) -> None:
    """The 100,000-row node: a column of mostly whole amounts, one stratum a row, described and twinned.

    At 110cb46 the walk alone would interpolate ten thousand million
    shares here. The twin is required to write the published point-free
    count, which is what the walk is for. The amounts spread over many
    whole numbers a row, so the reach step's rounds are not what is
    timed (plan P4-D387 names the shape where they are).
    """
    loaded = _described(tmp_path, _charges(100_000, 20261002, 14.0, 1.0))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.NumericFacts) and not facts.integer_valued
    twin = generation.generate(loaded, 0)
    published = sum(facts.numeric_styles.get(style, 0) for style in ("plain", "leading_zero", "leading_plus"))
    written = sum(
        1 for cell in twin.columns[0]
        if cell and parsing.classify_number(cell) == parsing.NUMBER
        and parsing.numeric_style(cell) in ("plain", "leading_zero", "leading_plus")
    )
    assert published > 80_000 and written == published, (published, written)



# -- 3. the row order ----------------------------------------------------------


_ORDER_CELLS = ("", "1", "2", "2", "10", "-3", "1,5", "2,25", "a", "b", "B", "1e3", "0.5", "x 1", " 7")


def test_the_row_order_read_once_is_the_order_read_in_full() -> None:
    """`row_order_of` reading each column only until it is settled answers as reading every cell did.

    Over 20,000 made-up tables of up to six columns, cells drawn from
    numbers, decimal commas, words and empty cells, sorted, reversed or
    shuffled, with and without declared decimal commas and sequence
    columns.
    """
    draw = random.Random(3873)
    found = {"number": 0, "text": 0, "decimal_comma": 0, "none": 0}
    for _case in range(20000):
        rows = draw.randrange(0, 9)
        width = draw.randrange(1, 7)
        columns: "list[list[str]]" = []
        for _column in range(width):
            cells = [draw.choice(_ORDER_CELLS) for _row in range(rows)]
            shape = draw.random()
            if shape < 0.3:
                cells = sorted(cells, key=lambda cell: (parsing.parse_number(cell) or 0.0, cell))
            elif shape < 0.45:
                cells = sorted(cells, reverse=True)
            elif shape < 0.55:
                cells = [draw.choice(("3", "3,5")) for _row in range(rows)]
            columns += [cells]
        sequences = [draw.choice((-1, -1, -1, 0)) for _column in range(width)]
        declared = None if draw.random() < 0.5 else [draw.random() < 0.5 for _column in range(width)]
        ours = dialect.row_order_of(columns, sequences, rows, declared)
        assert ours == row_order_of_as_built(columns, sequences, rows, declared), (columns, sequences, declared)
        found["none" if ours.column == 0 else ours.collation] += 1
    assert min(found.values()) > 100, found


def order_keys_asked(rows: int, as_built: bool = False) -> int:
    """How many cells are read as numbers asking the order of a table of ``rows`` unsorted readings."""
    draw = random.Random(rows)
    columns = [[f"{draw.uniform(0.0, 500.0):.2f}" for _row in range(rows)] for _column in range(5)]
    asked = [0]
    classify = parsing.classify_number

    def counted(text: str) -> str:
        asked[0] += 1
        return classify(text)

    function = row_order_of_as_built if as_built else dialect.row_order_of
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(parsing, "classify_number", counted)
        assert function(columns, [-1] * 5, rows) == dialect.NO_ORDER
    return asked[0]


def test_an_unsorted_column_is_read_only_until_it_has_stepped_both_ways() -> None:
    """Cells read for the order of five unsorted columns: a handful whatever the rows, every cell as built.

    The handful is how far each column runs before it has stepped both
    ways, which the made-up readings at each size settle, so it is bounded
    and not counted exactly; 110cb46 read every cell of every column.
    """
    small, large = order_keys_asked(1000), order_keys_asked(4000)
    assert small < 50 and large < 50, (small, large)
    assert order_keys_asked(1000, as_built=True) == 5000
    assert order_keys_asked(4000, as_built=True) == 20000


# -- 4. detection ----------------------------------------------------------------


def _detection_texts() -> "list[str]":
    """Opening records of every shape detection weighs: delimiters, spacing, quoting, ties, prose."""
    draw = random.Random(3874)
    texts = [
        "id,pair|code\n1,2|3\n4,5|6\n",
        "id,measure|low|high\n" + "".join(f"{i},{100 + i % 4}|90|110\n" for i in range(120)),
        '"id"; "note"\n"1"; "alpha; beta"\n"2"; "gamma"\n',
        "Gewicht, kg;Länge, cm\n41943,91;166,5\n0,166;3,5\n",
        'a,b\n"x \\"q, r\\"",2\n"y",3\n',
        "one\n100|30\n200|40\n",
        "a\tb\tc\r\n1\t2\t3\r\n4\t5\t6\r\n",
        "",
        "x",
        "a, b, c\n1, 2, 3\n4, 5, 6\n",
    ]
    for _case in range(60):
        delimiter = draw.choice((",", ";", "\t", "|"))
        width = draw.randrange(1, 5)
        rows = []
        for row in range(draw.randrange(1, 30)):
            cells = [draw.choice(("1", "2,5", "a b", '"q;r"', "", "x|y", " 3")) for _cell in range(width)]
            rows += [delimiter.join(cells)]
        texts += [draw.choice(("\n", "\r\n", "\r")).join(rows)]
    return texts


def test_detection_cut_once_reads_as_detection_cut_every_time() -> None:
    """The delimiter, its ties and the spacing come out as they did when each reading cut its own lines."""
    for text in _detection_texts():
        for at in (0, min(2, len(text))):
            assert dialect.delimiter_reading(text, at) == delimiter_reading_as_built(text, at), (text, at)
            for delimiter in dialect.DELIMITERS:
                assert dialect.detected_initial_space(text, at, delimiter) == detected_initial_space_as_built(
                    text, at, delimiter
                ), (text, at, delimiter)


def test_the_lines_handed_over_one_at_a_time_are_the_lines_cut_at_once() -> None:
    """`lines_in_turn` gives `physical_lines`' lines, at every block size and over every line ending."""
    draw = random.Random(3875)
    parts = ("a", "bc", "\n", "\r", "\r\n", ",", '"', "x" * 7, "")
    for _case in range(5000):
        text = "".join(draw.choice(parts) for _part in range(draw.randrange(0, 50)))
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(dialect, "_LINES_BLOCK", draw.choice((1, 2, 3, 7, 64, 1 << 16)))
            assert list(dialect.lines_in_turn(text)) == dialect.physical_lines(text), repr(text)


_ENDINGS = {"lf": "\n", "cr": "\r", "crlf": "\r\n"}


def _ended(lines: "list[str]", ending: str) -> str:
    """The lines, each ended by one ending, or by "mixed" ones.

    "mixed" ends the first quarter of the lines by line feeds, the rest by
    carriage returns alone, and the last line by the pair: a long run of
    carriage-return lines after the last line feed.
    """
    if ending in _ENDINGS:
        return _ENDINGS[ending].join(lines) + _ENDINGS[ending]
    quarter = len(lines) // 4
    last = len(lines) - 1
    return "".join(
        line + ("\n" if place < quarter else "\r\n" if place == last else "\r") for place, line in enumerate(lines)
    )


def test_lines_are_cut_a_block_at_a_time_whatever_ends_them() -> None:
    """`lines_in_turn` never cuts more than a block and a line of the text at once, whatever ends its lines.

    The Codex review of plan P4-D387 (item 2): 9fa2008 cut the text at its
    line feeds a block at a time, so a file of carriage-return lines, or
    a run of them after the last line feed, was cut into lines as one
    piece -- a list of every one of its lines. The pieces handed to
    `_cut_at_returns` are measured here at a block of 64 characters over
    2,000 lines of 1 to 40 characters: at most a block and the longest
    line, with every ending, and the lines `physical_lines` cuts. A pair
    standing across a block's end is one ending, at every block size and
    line length.
    """
    draw = random.Random(3883)
    lines = [f"{row},{'x' * draw.randrange(0, 30)}" for row in range(2000)]
    longest = max(len(line) for line in lines) + 2
    real = dialect._cut_at_returns
    for ending in ("lf", "cr", "crlf", "mixed"):
        text = _ended(lines, ending)
        widest = [0]

        def measured(piece: str, cut_at_a_feed: bool) -> "list[str]":
            widest[0] = max(widest[0], len(piece))
            return real(piece, cut_at_a_feed)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(dialect, "_LINES_BLOCK", 64)
            patch.setattr(dialect, "_cut_at_returns", measured)
            handed = list(dialect.lines_in_turn(text))
        assert handed == dialect.physical_lines(text), ending
        assert len(handed) == len(lines), ending
        assert widest[0] <= 64 + longest, (ending, widest[0])
    for block in (1, 2, 3, 4, 5, 8):
        for width in range(2 * block + 3):
            for ending in ("\r\n", "\r", "\n"):
                text = ("y" * width + ending) * 7 + "y" * width
                with pytest.MonkeyPatch.context() as patch:
                    patch.setattr(dialect, "_LINES_BLOCK", block)
                    assert list(dialect.lines_in_turn(text)) == dialect.physical_lines(text), (block, repr(text))


def splits_reading(rows: int, as_built: bool = False) -> int:
    """How many times reading a table of ``rows`` cuts text into lines, every candidate reading counted."""
    with tempfile.TemporaryDirectory() as home:
        lines = ["id,amount,note"] + [f"{row},{row * 3}.5,n{row % 7}" for row in range(rows)]
        path = fixtures.write(pathlib.Path(home), "table.csv", "\n".join(lines) + "\n")
        cut = [0]
        physical = dialect.physical_lines

        def counted(text: str) -> "list[str]":
            cut[0] += 1
            return physical(text)

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(dialect, "physical_lines", counted)
            if as_built:
                patch.setattr(dialect, "delimiter_reading", lambda text, at, opening=None: (
                    delimiter_reading_as_built(text, at)))
                patch.setattr(dialect, "detected_initial_space", lambda text, at, delimiter, opening=None: (
                    detected_initial_space_as_built(text, at, delimiter)))
            reading.read_table(str(path))
        return cut[0]


def test_detection_cuts_the_opening_lines_once() -> None:
    """Reading a table cuts its opening megabyte into a list of lines once, and the whole text never.

    110cb46 cut the megabyte once a candidate reading, and the whole text
    once more for the walk; the walk now cuts each line as it reaches it.
    """
    assert splits_reading(300) == 1
    assert splits_reading(300, as_built=True) >= 20


def _hinted_texts() -> "list[str]":
    """Tables under a separator line: spaced after the delimiter or not, quoted, every delimiter and line ending."""
    return [
        "sep=,\na, b, c\n1, 2, 3\n4, 5, 6\n",
        "sep=;\na; b; c\n1; 2; 3\n4; 5; 6\n",
        "sep=|\r\nid| v\r\n1| 2\r\n3| 4\r\n",
        "sep=\t\nid\t v\n1\t 2\n3\t 4\n",
        "sep=,\na,b,c\n1,2,3\n4,5,6\n",
        "sep=,\na, b,c\n1, 2,3\n4, 5,6\n",
        'sep=;\n"a"; "b"\n"1"; "2"\n"3"; "4"\n',
        "sep=,\r\na, b\r\n1, 2\r\n",
    ]


def test_detection_under_a_separator_line_reads_from_where_the_table_begins() -> None:
    """A table under a `sep=` line is spaced as its records are, and its names are read as 110cb46 read them.

    The opening lines detection reads are cut once, from where the table
    begins, past the separator line. Cut from the text's start instead,
    `sep=,` is read as a record of two fields, the second not spaced, so
    a table written comma-space is read with its spaces kept and names
    the columns 'a', ' b' and ' c'. Every text is settled as shipped and
    again with detection as 110cb46 cut it, each question its own lines.
    """
    for text, delimiter in (("sep=,\na, b, c\n1, 2, 3\n4, 5, 6\n", ","), ("sep=;\na; b; c\n1; 2; 3\n4; 5; 6\n", ";")):
        found = dialect.settle(text, "utf-8", False, False, "table.csv")
        assert found.form.separator_line and found.form.delimiter == delimiter, text
        assert found.form.initial_space is True and found.header == ("a", "b", "c"), (
            text, found.form.initial_space, found.header,
        )
    for text in _hinted_texts():
        ours = _settled(text)
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(dialect, "delimiter_reading", lambda text, at, opening=None: (
                delimiter_reading_as_built(text, at)))
            patch.setattr(dialect, "detected_initial_space", lambda text, at, delimiter, opening=None: (
                detected_initial_space_as_built(text, at, delimiter)))
            theirs = _settled(text)
        assert ours == theirs, text


def _listed_cursor(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make every walk cut its whole text into a list before the first record, as 110cb46 walked.

    The cursor is made with the five fields 110cb46's cursor has, so on
    110cb46 itself the walk is the one it already walked and the test
    below fails by its own measure.
    """
    real = dialect._Cursor

    def listed(lines: "list[str]", index: int, delimiter: str, escape: str, initial_space: bool,
               more: "object" = None, base: int = 0) -> "dialect._Cursor":
        if more is not None:
            lines = list(more)  # type: ignore[call-overload]
        return real(lines, index, delimiter, escape, initial_space)

    monkeypatch.setattr(dialect, "_Cursor", listed)


def _survey_texts() -> "list[str]":
    """Whole tables of every shape the walk reads: quoted lines, every ending, blank lines, preambles, escapes."""
    draw = random.Random(3878)
    texts = [
        'id,note\n1,"two\nlines"\n2,"three\r\nmore\rlines"\n',
        "id,v\r1,2\r\r\n3,4\r\r\n",
        "Export of 3 October\n\nid,v\n1,2\n\n3,4\n   \n5,6\n",
        "sep=;\nid;v\n1;2\n3;4\n",
        'id,v\n"a\\"b",1\n"c",2\n',
        "a, b\n1, 2\n3, 4\n",
        "id,v,\n1,2,\n3,4,\n",
        "id,v,w\n1,2\n3,4\n",
        "id,v\n1,2\n3,4\x1a",
        'id,v\n1,"open\n',
        "id\n1\n2\n3\n",
        "id,v\n",
    ]
    for _case in range(300):
        delimiter = draw.choice((",", ";", "\t", "|"))
        width = draw.randrange(1, 4)
        ending = draw.choice(("\n", "\r\n", "\r"))
        rows = [delimiter.join(f"h{place}" for place in range(width))]
        for _row in range(draw.randrange(1, 25)):
            cells = [draw.choice(("1", "x y", '"q\nr"', '"s\r\nt"', '"u""v"', "", "2.5", '"w' + delimiter + 'z"'))
                     for _cell in range(width)]
            rows += [delimiter.join(cells)]
            if draw.random() < 0.1:
                rows += [""]
        texts += [ending.join(rows) + draw.choice(("", ending, ending + ending))]
    return texts


def _settled(text: str) -> str:
    """What `dialect.settle` makes of a text, or the refusal it raises."""
    try:
        return repr(dialect.settle(text, "utf-8", False, False, "table.csv"))
    except Exception as refusal:  # noqa: BLE001 -- the kind and words are what is compared
        return f"{type(refusal).__name__}: {refusal}"


def test_the_walk_cutting_lines_as_it_goes_reads_what_the_listed_walk_read(monkeypatch: pytest.MonkeyPatch) -> None:
    """Over 312 made-up tables, the survey is the one a walk over every line cut first made, refusals word for word."""
    ours = [_settled(text) for text in _survey_texts()]
    _listed_cursor(monkeypatch)
    theirs = [_settled(text) for text in _survey_texts()]
    assert ours == theirs
    surveys = sum(1 for said in ours if said.startswith("Survey("))
    assert surveys > 200 and len(ours) - surveys > 30, surveys


def walk_peak(rows: int, listed: bool = False, ending: str = "lf") -> "tuple[int, int]":
    """The most memory the survey of a table of ``rows`` holds above its text, and the text's size.

    ``ending`` ends its lines, as `_ended` says.
    """
    lines = ["id,amount,label,note"] + [f"{row},{row * 7}.25,L{row % 13},note number {row}" for row in range(rows)]
    text = _ended(lines, ending)
    with pytest.MonkeyPatch.context() as patch:
        if listed:
            _listed_cursor(patch)
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()[0]
            tracemalloc.reset_peak()
            found = dialect.settle(text, "utf-8", False, False, "table.csv")
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
    assert found.n_rows == rows
    return peak - before, len(text)


def test_the_walk_holds_a_line_and_not_a_list_of_them(monkeypatch: pytest.MonkeyPatch) -> None:
    """The survey's peak above its text: a list of every line less than the walk that cut them first."""
    ours, size = walk_peak(20_000)
    theirs, _size = walk_peak(20_000, listed=True)
    assert theirs - ours > size, (ours, theirs, size)


def test_the_walk_holds_a_line_and_not_a_list_of_them_whatever_ends_the_lines() -> None:
    """The survey's peak above its text with lines ended by carriage returns alone, the pair, or mixed, as by line feeds.

    The Codex review of plan P4-D387 (item 2): on 9fa2008 a file of
    carriage-return lines, or a run of them after the last line feed,
    was cut into one list held while the walk filled the table -- on
    these 20,000 rows 840,000 bytes above the line feeds' peak, 1.2 times
    the text, and 467,000 with the mixed endings. Each ending is held
    within an eighth of the text of the line feeds' peak, and a walk
    handed every line first is required to hold more than the text
    above it with that ending, so the measure is known to see the list.
    """
    lines_fed, size = walk_peak(20_000)
    for ending in ("cr", "crlf", "mixed"):
        ours, _size = walk_peak(20_000, ending=ending)
        assert ours - lines_fed < size // 8, (ending, ours, lines_fed, size)
        theirs, _size = walk_peak(20_000, listed=True, ending=ending)
        assert theirs - ours > size, (ending, ours, theirs, size)


# -- 5. the checking pass ------------------------------------------------------


def _checked(check: "object", found: object, path: pathlib.Path, refusals: str) -> str:
    """What one checking pass says of a reading: nothing, or the refusal it raises."""
    try:
        check(str(path), found, "table.csv", refusals)  # type: ignore[operator]
    except Exception as refusal:  # noqa: BLE001 -- the kind and words are what is compared
        return f"{type(refusal).__name__}: {refusal}"
    return "agrees"


def _with_columns(found: "reading._Reading", columns: "list[list[str]]", rows: int) -> "reading._Reading":
    """The reading with other columns and row count, its survey left as it was."""
    return dataclasses.replace(found, columns=columns, n_rows=rows)


def _check_cases(folder: pathlib.Path) -> "list[tuple[str, reading._Reading, pathlib.Path]]":
    """Readings the checking pass must accept, and the same readings changed where it must refuse."""
    cases: "list[tuple[str, reading._Reading, pathlib.Path]]" = []
    draw = random.Random(3876)
    body = ["id,amount,label"] + [f"{row},{draw.randint(1, 900)}.{row % 10},L{row % 13}" for row in range(700)]
    plain = fixtures.write(folder, "plain.csv", "\n".join(body) + "\n")
    found = reading._read_authoritatively(plain, "plain.csv", reading.FIRST_ROW_NAMES)
    cases += [("plain", found, plain)]
    for column, row in ((1, 650), (2, 3), (0, 699), (2, 0)):
        changed = [list(cells) for cells in found.columns]
        changed[column][row] = changed[column][row] + "?"
        cases += [(f"value {column} {row}", _with_columns(found, changed, found.n_rows), plain)]
    both = [list(cells) for cells in found.columns]
    both[2][600] = "?"
    both[1][10] = "?"
    cases += [("two values", _with_columns(found, both, found.n_rows), plain)]
    short = [list(cells[:-1]) for cells in found.columns]
    cases += [("a row short", _with_columns(found, short, found.n_rows - 1), plain)]
    # A reading a row longer than the file, every value pandas reads
    # agreeing with it: only the count of rows tells them apart.
    long = [list(cells) + [cells[-1]] for cells in found.columns]
    cases += [("a row long", _with_columns(found, long, found.n_rows + 1), plain)]
    # A reading a column wider than the file: only the columns pandas
    # reads tell them apart.
    wider = dataclasses.replace(
        found,
        column_names=list(found.column_names) + ["extra"],
        columns=[list(cells) for cells in found.columns] + [list(found.columns[0])],
    )
    cases += [("a column more", wider, plain)]
    narrower = dataclasses.replace(
        found,
        column_names=list(found.column_names[:-1]),
        columns=[list(cells) for cells in found.columns[:-1]],
    )
    cases += [("a column fewer", narrower, plain)]
    marked = fixtures.write(folder, "marked.csv", "\n".join(body) + "\x1a")
    glued = reading._read_authoritatively(marked, "marked.csv", reading.FIRST_ROW_NAMES)
    cases += [("end-of-file mark", glued, marked)]
    for column in (0, 2):
        changed = [list(cells) for cells in glued.columns]
        changed[column][-1] = changed[column][-1] + "\x1a"
        cases += [(f"end-of-file mark, last value {column} changed", _with_columns(glued, changed, glued.n_rows),
                   marked)]
    described = ["name,weight", "text,kg"] + [f"n{row},{row}" for row in range(400)]
    rows_above = fixtures.write(folder, "above.csv", "\n".join(described) + "\n")
    above = reading._read_authoritatively(
        rows_above, "above.csv", reading.FIRST_ROW_NAMES, metadata_rows=1, metadata_rows_confirmed=True
    )
    assert above.survey is not None and above.survey.form.header_rows, "no row of descriptions was read"
    cases += [("rows above", above, rows_above)]
    form = dataclasses.replace(above.survey.form, header_rows=(("text", "lb"),))
    renamed = dataclasses.replace(above, survey=dataclasses.replace(above.survey, form=form))
    cases += [("a row above changed", renamed, rows_above)]
    headless = ["Export of 3 October", ""] + [f"{row},{row * 2}" for row in range(500)]
    lead = fixtures.write(folder, "lead.csv", "\n".join(headless) + "\n")
    unnamed = reading._read_authoritatively(lead, "lead.csv", reading.FIRST_ROW_DATA)
    cases += [("lines above, no names", unnamed, lead)]
    for column, row in ((0, 0), (1, 1), (1, 499)):
        changed = [list(cells) for cells in unnamed.columns]
        changed[column][row] = changed[column][row] + "?"
        cases += [(f"lines above, no names, value {column} {row}", _with_columns(unnamed, changed, unnamed.n_rows),
                   lead)]
    # Pandas asked for no rows at all: one record under lines above it,
    # taken as names, with an end-of-file mark glued on. It hands over no
    # piece, where the whole frame still named the columns it read.
    single = fixtures.write(folder, "single.csv", "Export of 3 October\n\n1,2\x1a")
    one = reading._read_authoritatively(single, "single.csv", reading.FIRST_ROW_DATA)
    cases += [("no rows asked for", one, single)]
    # A header ending in a delimiter, with rows that do not or that do:
    # pandas reads a column more, named and holding nothing, which the
    # piece's size is worked out for and which is never compared. And rows
    # ending in a delimiter under a header that does not, which pandas 3
    # warns about. Each is read as written and with one value changed.
    for name, header, ending, trails in (
        ("header ends in a delimiter", "id,amount,label,", "", (True, False)),
        ("every row ends in a delimiter", "id,amount,label,", ",", (True, True)),
        ("rows end in a delimiter", "id,amount,label", ",", (False, True)),
    ):
        lines = [header] + [f"{row},{row * 3},L{row % 11}{ending}" for row in range(300)]
        written = fixtures.write(folder, name.replace(" ", "-") + ".csv", "\n".join(lines) + "\n")
        trailing = reading._read_authoritatively(written, "table.csv", reading.FIRST_ROW_NAMES)
        assert trailing.survey is not None, name
        written_form = trailing.survey.form
        assert (written_form.header_trailing_delimiter, written_form.rows_trailing_delimiter) == trails, name
        assert len(trailing.column_names) == 3, (name, trailing.column_names)
        cases += [(name, trailing, written)]
        changed = [list(cells) for cells in trailing.columns]
        changed[1][299] = changed[1][299] + "?"
        cases += [(f"{name}, last value changed", _with_columns(trailing, changed, trailing.n_rows), written)]
    return cases


def _asks_the_whole_frame(named: "dict[str, object]") -> bool:
    """Whether a call of pandas asks for the whole frame: no piece at all, or one piece holding every row."""
    return named.get("chunksize") in (None, getattr(reading, "_EVERY_ROW", None))


def _counted_reads(monkeypatch: pytest.MonkeyPatch) -> "dict[str, int]":
    """Count the checking pass's readings by pandas: in pieces, and as one whole frame."""
    reads = {"pieces": 0, "whole": 0}
    shipped = reading.pandas.read_csv

    def counted(*arguments: object, **named: object) -> object:
        reads["whole" if _asks_the_whole_frame(named) else "pieces"] += 1
        return shipped(*arguments, **named)

    monkeypatch.setattr(reading.pandas, "read_csv", counted)
    return reads


def test_the_checking_pass_read_in_pieces_says_what_the_whole_frame_said(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Agreement, and each refusal word for word, as 110cb46's pass that held the whole frame.

    Pieces of 7 rows, so every file is read in many; changed values in
    the first and the last pieces, two at once, a row short, a row long,
    a column more and one fewer, an end-of-file mark glued to the last
    value and that value changed, a row of descriptions under the names
    and one of them changed, lines above a table with no names, whose
    first record pandas takes as names, with values changed in its first,
    second and last rows, such a table of one record with a mark glued
    on, which pandas is asked for no rows of, and a header ending in a
    delimiter, every row ending in one, and rows ending in one under a
    header that does not, each with its last value changed -- under both
    kinds of refusal. A file the pieces agree on is never read whole,
    the column a header's trailing delimiter adds counted among the ones
    a piece is read for; every other file is, once, and its refusal is
    the whole frame's; and pandas is read to its end each time, so no
    file is left open. The piece is set whether or not the module names
    one, so on 110cb46, which reads every file whole, the test fails by
    its own measure.
    """
    monkeypatch.setattr(reading, "_pandas_rows_a_piece", lambda width: 7, raising=False)
    said = []
    whole = {"agrees": 0, "refused": 0}
    agreed = set()
    for name, found, path in _check_cases(tmp_path):
        for refusals in (reading.REFUSALS_MAY_QUOTE, reading.REFUSALS_NAME_POSITIONS):
            with warnings.catch_warnings(record=True):
                # Pandas may warn about a file it reads -- rows ending in
                # a delimiter their header does not end in -- and that is
                # kept out of this test's report.
                warnings.simplefilter("always")
                theirs = _checked(_check_against_pandas_as_built, found, path, refusals)
            with pytest.MonkeyPatch.context() as patch, warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                reads = _counted_reads(patch)
                ours = _checked(reading._check_against_pandas, found, path, refusals)
                gc.collect()
            assert ours == theirs, (name, refusals, ours, theirs)
            left_open = [f"{warning.message}" for warning in caught if issubclass(warning.category, ResourceWarning)]
            assert not left_open, (name, left_open)
            if name == "no rows asked for":
                assert reads == {"pieces": 0, "whole": 1}, (name, reads)
            elif ours == "agrees":
                assert reads == {"pieces": 1, "whole": 0}, (name, reads)
                whole["agrees"] += 1
                agreed |= {name}
            else:
                assert reads == {"pieces": 1, "whole": 1}, (name, reads)
                whole["refused"] += 1
            said += [ours]
    trailing = {"header ends in a delimiter", "every row ends in a delimiter", "rows end in a delimiter"}
    assert trailing <= agreed, agreed
    assert said.count("agrees") >= 8 and len(set(said)) >= 8, said
    assert whole["agrees"] >= 8 and whole["refused"] >= 20, whole


def test_a_reader_that_fails_sends_the_check_to_the_whole_frame(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pandas failing before the first piece or after the last decides nothing: the whole frame does.

    Pandas is made to fail where it hands over pieces and nowhere else, so
    the whole frame agrees and the file is accepted -- by the whole frame,
    read once, and not by pieces that never came or never finished. On
    110cb46, which reads no piece, the test fails by its own measure. And
    pandas failing everywhere, the whole frame before it hands anything
    over too, with an error or out of memory, is refused in 110cb46's
    words.
    """
    monkeypatch.setattr(reading, "_pandas_rows_a_piece", lambda width: 7, raising=False)
    _name, found, path = _check_cases(tmp_path)[0]
    shipped = reading.pandas.read_csv
    for where in ("before the first piece", "after the last piece"):
        reads = {"pieces": 0, "whole": 0}

        def failing(*arguments: object, _where: str = where, **named: object) -> object:
            if _asks_the_whole_frame(named):
                reads["whole"] += 1
                return shipped(*arguments, **named)
            reads["pieces"] += 1
            if _where == "before the first piece":
                raise ValueError(f"a made-up failure {_where}")

            def handed() -> object:
                yield from shipped(*arguments, **named)
                raise ValueError(f"a made-up failure {_where}")

            return handed()

        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(reading.pandas, "read_csv", failing)
            said = _checked(reading._check_against_pandas, found, path, reading.REFUSALS_MAY_QUOTE)
        assert said == "agrees" and reads == {"pieces": 1, "whole": 1}, (where, said, reads)
    # Pandas failing before anything is handed over, the whole frame too,
    # and running out of memory there: the refusal is 110cb46's, word for
    # word, under both kinds of refusal.
    for failure in (ValueError("a made-up failure everywhere"), MemoryError()):

        def failing_everywhere(*arguments: object, _failure: BaseException = failure, **named: object) -> object:
            raise _failure

        for refusals in (reading.REFUSALS_MAY_QUOTE, reading.REFUSALS_NAME_POSITIONS):
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(reading.pandas, "read_csv", failing_everywhere)
                theirs = _checked(_check_against_pandas_as_built, found, path, refusals)
                ours = _checked(reading._check_against_pandas, found, path, refusals)
            assert ours == theirs and ours.startswith("ProfileError: "), (failure, refusals, ours, theirs)


def _read_in_part_only(path: pathlib.Path, found: "reading._Reading") -> bool:
    """Whether the installed pandas, asked as the checking pass asks it, fails reading the file whole but hands over a first piece of 7 rows.

    Asked of a headed file with no line above its header and no
    end-of-file mark, which the checking pass reads from its first line
    with no count of rows.
    """
    assert found.survey is not None, path
    form = found.survey.form
    assert found.header_source == reading.HEADER_FROM_FILE and not form.end_of_file_mark, path
    assert not form.separator_line and not dialect.preamble_lines_holding_text(form.preamble), path
    backslash = form.escape == dialect.ESCAPE_BACKSLASH
    asked: "dict[str, object]" = {
        "encoding": dialect.READING_CODECS[found.encoding],
        "encoding_errors": "strict",
        "header": 0,
        "index_col": False,
        "dtype": str,
        "keep_default_na": False,
        "na_filter": False,
        "skip_blank_lines": True,
        "engine": "c",
        "sep": form.delimiter,
        "quotechar": '"',
        "doublequote": not backslash,
        "escapechar": "\\" if backslash else None,
        "skipinitialspace": form.initial_space,
        "comment": None,
    }
    with warnings.catch_warnings(record=True):
        warnings.simplefilter("always")
        try:
            pandas.read_csv(path, **asked)
        except Exception:  # noqa: BLE001 -- any failure is the answer asked for
            pass
        else:
            return False
        try:
            with pandas.read_csv(path, chunksize=7, **asked) as pieces:
                first = next(pieces)
        except Exception:  # noqa: BLE001 -- any failure is the answer asked for
            return False
    return len(first) == 7


def test_a_file_refused_after_its_pieces_shows_pandas_warning_as_often_as_before(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A warning pandas gives about a file is shown once at most: as often as 110cb46 showed it, save for a file pandas reads in part and then cannot read at all.

    Rows ending in a delimiter their header does not end in make pandas 3
    warn on every piece it hands over and on the whole frame. Python
    shows a warning once for each line of code it comes from, so the
    pieces and the whole frame are read at one line: read at two, a file
    the pieces could not agree on and the whole frame then refused showed
    the warning twice, where 110cb46, which read it once, showed it once.
    Whether the installed pandas warns about the file at all is asked of
    it first, read once, since a pandas that takes the empty column for
    the one set of trailing delimiters it allows warns about nothing.
    Pieces of 7 rows, under Python's own filter, for the file as written
    and with one value changed.

    And two files pandas reads in part and then cannot read at all (plan
    P4-D387): the same rows, ended by carriage returns alone, with one
    record beginning with a space, or two, the second the last. Such a
    record sends pandas' reader back over the lines before it: read
    whole, pandas fails before it hands anything over, and read in pieces
    it hands over pieces with rows repeated, the second file's last piece
    failing too. Where the installed pandas does so, both passes refuse
    in the same words, 110cb46's showing no warning and this pass the one
    pandas gives about the part it read, once -- 1 under pandas 3, 0
    under pandas 2; where it does not, both show as many.
    """
    monkeypatch.setattr(reading, "_pandas_rows_a_piece", lambda width: 7, raising=False)
    lines = ["id,amount,label"] + [f"{row},{row * 3},L{row % 11}," for row in range(300)]
    path = fixtures.write(tmp_path, "rows-end-in-a-delimiter.csv", "\n".join(lines) + "\n")
    found = reading._read_authoritatively(path, "table.csv", reading.FIRST_ROW_NAMES)
    changed = [list(cells) for cells in found.columns]
    changed[1][150] = changed[1][150] + "?"
    # Whether the installed pandas warns about this file at all, read once.
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pandas.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, index_col=False)
    once = min(1, sum(1 for warning in caught if issubclass(warning.category, pandas.errors.ParserWarning)))
    for name, checked in (("as written", found), ("a value changed", _with_columns(found, changed, found.n_rows))):
        for refusals in (reading.REFUSALS_MAY_QUOTE, reading.REFUSALS_NAME_POSITIONS):
            shown = []
            for check in (_check_against_pandas_as_built, reading._check_against_pandas):
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("default")
                    said = _checked(check, checked, path, refusals)
                warned = [warning for warning in caught if issubclass(warning.category, pandas.errors.ParserWarning)]
                shown += [(said, len(warned))]
            assert shown[1] == shown[0] and shown[0][1] == once, (name, refusals, once, shown)
            assert (shown[0][0] == "agrees") == (name == "as written"), (name, refusals, shown)
    for spaced in ((150,), (150, 299)):
        lines = ["id,amount,label"]
        lines += [f"{' ' if row in spaced else ''}{row},{row * 3},L{row % 11}," for row in range(300)]
        damaged = fixtures.write(tmp_path, f"read-in-part-{len(spaced)}.csv", "\r".join(lines) + "\r")
        assert b"\n" not in damaged.read_bytes(), damaged
        found = reading._read_authoritatively(damaged, "table.csv", reading.FIRST_ROW_NAMES)
        assert found.survey is not None and found.survey.form.rows_trailing_delimiter, spaced
        assert not found.survey.form.header_trailing_delimiter and found.n_rows == 300, spaced
        in_part = _read_in_part_only(damaged, found)
        for refusals in (reading.REFUSALS_MAY_QUOTE, reading.REFUSALS_NAME_POSITIONS):
            shown = []
            for check in (_check_against_pandas_as_built, reading._check_against_pandas):
                with warnings.catch_warnings(record=True) as caught:
                    warnings.simplefilter("default")
                    said = _checked(check, found, damaged, refusals)
                warned = [warning for warning in caught if issubclass(warning.category, pandas.errors.ParserWarning)]
                shown += [(said, len(warned))]
            if in_part:
                assert shown[1][0] == shown[0][0] != "agrees", (spaced, refusals, shown)
                assert shown[0][1] == 0 and shown[1][1] == once, (spaced, refusals, once, shown)
            else:
                assert shown[1][1] == shown[0][1], (spaced, refusals, shown)


# Made-up files whose lines end in carriage returns alone and hold quoted
# line breaks, on which pandas' own reader goes wrong: read whole it
# fails with a buffer overflow or hands back hundreds of thousands of rows
# that are not in the file, and read in pieces of another size than its
# own it fails elsewhere, or reads the file right. Cases 208, 670, 1712 and
# 1949 of the skeptic's fuzz of plan P4-D387.
_DAMAGED = (
    'h0\r10\r3\r4.5\r2.5\r1\rx\r"cr\r\nlf"\r2.5\r\\"\r 7\r"s;t"\r2\r12:30\r<0.3\r<0.3\rN/A\r5 mg\r3\ra b\r5 mg\r',
    'A title line of a made-up export\r\r1,5,12:30,"q,r",N/A\r3,12,12,4.5\r<0.3,-3,\\",2\r1,12,12,12\r\rx,"s;t",,'
    '"two\nlines"\r 7,\\","cr\r\nlf","q,r"\r2,1,4.5,12\r12,4.5,12,2\r12:30,03/01/2024,-3,2\r"cr\r\nlf",é,N/A,"s;t"'
    '\r\r1,5,N/A,2024-01-03,"s;t"\r12:30,"cr\r\nlf",2024-01-03,10\r"s;t",<0.3,é, 7,N/A\r2,12,12,12\r3,3,3,3\rx,'
    '"say ""hi""",12:30,"say ""hi"""\rx,<0.3,x,"s;t"\r12,2,2,1\r"two\nlines","q,r",\\",-3\r-3,N/A,2024-01-03\r'
    '"s;t",,"q,r",2.5\r"q,r","two\nlines","two\nlines",é\r03/01/2024,"cr\r\nlf",2024-01-03,\\"\rx,2.5,x,"s;t"\r'
    '"cr\r\nlf",<0.3,"cr\r\nlf",1,5\r\r',
    'h0|h1|h2|h3\r-3|"q,r"|x|<0.3\r3|3|4.5|12\r10|2024-01-03|5 mg|03/01/2024\r1|1|2|3\r2024-01-03| 7|03/01/2024|x\r'
    '10|2.5|03/01/2024|x\r3|3|4.5|12\r2024-01-03|2024-01-03|é|2.5\r"say ""hi"""|2.5|N/A|1,5\r3|3|1|3\r4.5|12|1|3\r'
    '2.5|10|<0.3|"cr\r\nlf"\r 7|2|10|10\r4.5|2|1|12\r10|é|N/A|"say ""hi"""\r1|2|4.5|2\r',
    'h0|\r1|2.5\r3|2\r10|-3\r"two\nlines"|x\r1|é\rx|\r|<0.3\r|5 mg\ra b|N/A\rx|"two\nlines"\r 7|2024-01-03\r'
    '"two\nlines"|"say ""hi"""\r"two\nlines"|-3\r2|2\r1|2\r|5 mg\r 7|-3\r2|2024-01-03\rN/A|é\r',
)


def test_a_damaged_file_is_refused_as_the_whole_frame_refused_it(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Four files pandas misreads, under every first-row setting and both kinds of refusal: 110cb46's words.

    Read in pandas' own steps, a piece fails where the whole frame fails
    and the whole frame then says why. Read in pieces of one row, the
    same files are read right and accepted where 110cb46 refused them, so
    the piece's size is what this test holds; on 110cb46, which reads no
    piece, none is misread and the test fails by its own measure.
    """
    checked = 0
    misread = 0
    for number, text in enumerate(_DAMAGED):
        path = tmp_path / f"damaged-{number}.csv"
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        for first in (reading.FIRST_ROW_AUTOMATIC, reading.FIRST_ROW_NAMES, reading.FIRST_ROW_DATA):
            found = reading._read_authoritatively(path, "table.csv", first)
            for refusals in (reading.REFUSALS_MAY_QUOTE, reading.REFUSALS_NAME_POSITIONS):
                theirs = _checked(_check_against_pandas_as_built, found, path, refusals)
                assert theirs != "agrees", (number, first)
                assert _checked(reading._check_against_pandas, found, path, refusals) == theirs, (
                    number, first, refusals,
                )
                checked += 1
                with pytest.MonkeyPatch.context() as patch:
                    patch.setattr(reading, "_pandas_rows_a_piece", lambda width: 1, raising=False)
                    if _checked(reading._check_against_pandas, found, path, refusals) != theirs:
                        misread += 1
    assert checked == 24 and misread == 24, (checked, misread)


def _splits_at(width: int, rows_before: int) -> bool:
    """Whether pandas read a column's whole numbers and the letters after ``rows_before`` of them in two steps.

    Pandas works out a column's type one step of rows at a time and warns
    where two steps came out of different types, so the warning says
    whether row ``rows_before`` began a step of its own.
    """
    filler = ",1" * (width - 1)
    lines = [",".join(f"c{index}" for index in range(width))]
    lines += ["1" + filler] * rows_before
    lines += ["x" + filler] * 10
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        pandas.read_csv(io.StringIO("\n".join(lines) + "\n"))
    return any(issubclass(warning.category, pandas.errors.DtypeWarning) for warning in caught)


def test_a_piece_is_the_rows_pandas_own_reader_parses_at_a_time() -> None:
    """`_pandas_rows_a_piece` is the step of rows the installed pandas takes, at five widths.

    That step is the library's own and not this package's, so it is found
    in the library: a column whose whole numbers give way to letters is
    read as one type where the letters begin inside the first step, and
    as two where they begin the second.
    """
    for width in (1, 3, 50, 64, 333):
        rows = reading._pandas_rows_a_piece(width)
        assert not _splits_at(width, rows - 1) and _splits_at(width, rows), (width, rows)


def check_peak(rows: int, as_built: bool = False) -> int:
    """The most memory the checking pass of a table of ``rows`` holds above the reading it checks."""
    with tempfile.TemporaryDirectory() as home:
        lines = ["a,b,c,d,e"] + [f"{row},x{row},{row * 7}.25,y{row % 97},{row % 5}" for row in range(rows)]
        path = fixtures.write(pathlib.Path(home), "table.csv", "\n".join(lines) + "\n")
        found = reading._read_authoritatively(path, "table.csv", reading.FIRST_ROW_NAMES)
        check = _check_against_pandas_as_built if as_built else reading._check_against_pandas
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()[0]
            tracemalloc.reset_peak()
            check(str(path), found, "table.csv", reading.REFUSALS_MAY_QUOTE)
            peak = tracemalloc.get_traced_memory()[1]
        finally:
            tracemalloc.stop()
    return peak - before


def test_the_checking_pass_holds_a_piece_and_not_a_second_table(monkeypatch: pytest.MonkeyPatch) -> None:
    """Over a reading, the pass holds about what one piece needs, where 110cb46 held the whole frame.

    The piece is set to 819 rows of the five columns whether or not the
    module names a piece, so on 110cb46, which reads the whole frame, the
    test fails by its own measure.
    """
    monkeypatch.setattr(reading, "_pandas_rows_a_piece", lambda width: 4096 // width, raising=False)
    ours = check_peak(40_000)
    theirs = check_peak(40_000, as_built=True)
    assert ours * 4 < theirs, (ours, theirs)
    assert check_peak(80_000) < ours * 1.5, ours

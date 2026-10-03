"""The censuses of the time of day: their keys, and the rules they will share.

Stage 3b (plan P4-D364). A column of moments will publish how many cells
of its BODY -- the cells between the two tail boundaries, both included
-- fall on each hour (`hour_census`), each minute and each second of the
written wall clock (`minute_census`, `second_census`), beside the
minutes and seconds that stand out from their neighbours
(`minute_heaps`, `second_heaps`); and a column of clock times its own
census of ten-minute bins (`clock_census`), its heaps (`clock_heaps`),
the step its values were written on (`clock_step`), the codes it
writes among them (`clock_codes`) and, under the moments' own key, its
census of the minutes of the hour (`minute_census`). Each landing of
stage 3b's time-of-day track fills its own keys and its own block below;
until it does, every one of these keys is empty on every block --
`clock_step` is `null` -- and the loader refuses anything else.

The bin rules every census shares -- the floor, the merge, the
stand-out rule and the checker of a published census -- are
`calendar_rules`', stated once there for the dates and the clock alike.

Nothing here reads a table: every name is a constant or a function of
the numbers handed to it. No I/O of any kind.
"""

import dataclasses
import math

from synthtwin import calendar_rules, parsing

# The keys of a column block of moments (contract 6.6.2), each `[]` on
# every block until its landing fills it.
HOUR_CENSUS = "hour_census"
MINUTE_CENSUS = "minute_census"
SECOND_CENSUS = "second_census"
MINUTE_HEAPS = "minute_heaps"
SECOND_HEAPS = "second_heaps"

# The keys of a column block of clock times (contract 6.13): the three
# lists `[]` and the step `null` on every block until their landing fills
# them -- and `MINUTE_CENSUS`, `[]` there until its own landing (3b.C2).
CLOCK_CENSUS = "clock_census"
CLOCK_HEAPS = "clock_heaps"
CLOCK_STEP = "clock_step"
CLOCK_CODES = "clock_codes"

# The empty lists among them, in the order the keys are named above.
DATETIME_CLOCK_LISTS = (
    HOUR_CENSUS,
    MINUTE_CENSUS,
    SECOND_CENSUS,
    MINUTE_HEAPS,
    SECOND_HEAPS,
)
CLOCK_LISTS = (CLOCK_CENSUS, CLOCK_HEAPS, CLOCK_CODES)


# THE LANDINGS' ANCHORS (plan P4-D364). Each landing of stage 3b that
# adds to this module adds below its own line, so two landings built
# side by side never touch the same lines; a landing with nothing to add
# leaves its line alone. In the order of the plan's numbering table.
# anchor 3b-D1 (P4-D365)
# anchor 3b-D0 (P4-D366)
# anchor 3b-D2 (P4-D367)
# anchor 3b-D3 (P4-D368)
# anchor 3b-D4 (P4-D369)
# anchor 3b-T1 (P4-D370)
# anchor 3b-T2 (P4-D371)
# anchor 3b-T3 (P4-D372)
# anchor 3b-C1 (P4-D373)
# THE CENSUS OF A COLUMN OF CLOCK TIMES (landing 3b.5, lane C1, plan
# P4-D373; contract 6.13, CC1 to CC5 and CH1 to CH2; method G7A.4b).
#
# A column of clock times publishes, beside its tails and its ladder:
#
# - `clock_step`, the step every parsed value was written on: the
#   greatest common divisor, in seconds, of the length of the form's dial
#   and every value's second of it -- 60 on a column of minutes, 300 on a
#   five-minute grid, 1 on a column of seconds;
# - `clock_heaps`, every value on that step that stands out from the five
#   steps on each side of it (`calendar_rules.standing_out`, the median
#   and the census line), counted over EVERY parsed cell, the tails' too;
# - `clock_census`, how many of the BODY's other cells -- between the two
#   tail boundaries, both included, or every parsed cell of a column with
#   no tails -- fall in each group of ten-minute bins, nested in hours:
#   the hours first merged by `calendar_rules.merged_groups`, then the
#   bins inside each hour group. `[]` where nothing is left beside the
#   heaps, or fewer cells than the line, which no count may name;
# - `clock_codes`, every spelling no clock reading of the column accepts
#   that at least the line's rows wrote, with its count.
#
# Every one of them is a count of the column's own cells, so the twin is
# held to each exactly and the checker counts them off the file.

# Seconds per bin of the census, and bins per hour.
TEN_MINUTES = 600
BINS_PER_HOUR = 6
# How many steps on each side the stand-out rule reads, and where it
# centres them: the median, because on a grid the mean of a value's
# neighbours is a neighbouring heap's.
CLOCK_REACH = 5


def clock_day(form: str) -> int:
    """How many seconds one form's dial holds: 86,400, or 43,200 on the
    declared 12-hour face, which writes no marker.

    Raises ValueError for a form `parsing` does not know. No I/O.
    """
    return parsing.CLOCK_CAPACITY[form] * parsing.clock_step(form)


def clock_bin_count(form: str) -> int:
    """How many ten-minute bins one form's dial holds: 144, or 72."""
    return clock_day(form) // TEN_MINUTES


def clock_bin_of(ordinal: int, form: str) -> int:
    """The ten-minute bin one ordinal of a form falls in, from nought."""
    return (ordinal * parsing.clock_step(form)) // TEN_MINUTES


def written_step(seconds: "list[int]", day: int) -> int:
    """The step a column's values were written on, in seconds.

    The greatest common divisor of the dial's length and every value's
    second of it, so it divides the dial and every value stands on it.
    A column whose every value is midnight is on a step of the whole dial.

    Guarantees: accepts seconds of the dial and its length; returns a
    whole number from 1 to `day`. Determinism: a function of the two.
    Raises nothing. No I/O of any kind.
    """
    step = day
    for second in seconds:
        # Euclid's rule, written out: `math` lends this package only the
        # names its offline audit enumerates.
        other = second
        while other:
            step, other = other, step % other
        if step == 1:
            break
    return step


def heaps_on_the_step(
    counts: "dict[int, int]", units: int, line: int
) -> "tuple[tuple[int, int], ...]":
    """The steps whose count stands out, read sparsely (method G7A.4b).

    `calendar_rules.standing_out` over `units` consecutive steps, of which
    `counts` names the ones holding a cell, at the reach of five and the
    median, on a line and not a cycle -- asked only of the steps holding
    at least the line, so a column of seconds is not walked step by step.

    Guarantees: accepts the counts by step, the number of steps and the
    census line; returns `(step, count)` ascending, exactly what
    `standing_out` returns over the dense counts. Determinism: a function
    of the three. Raises nothing. No I/O of any kind.
    """
    found: "list[tuple[int, int]]" = []
    for index in sorted(counts):
        count = counts[index]
        if count < line or count <= 0:
            continue
        around: "list[int]" = []
        for step in range(1, CLOCK_REACH + 1):
            for other in (index - step, index + step):
                held = 0
                if 0 <= other < units and other in counts:
                    held = counts[other]
                around += [held]
        ordered = sorted(around)
        middle = len(ordered) // 2
        twice = ordered[middle - 1] + ordered[middle]
        if 2 * count >= 3 * twice:
            found += [(index, count)]
    return tuple(found)


def nested_groups(
    bins: "list[int]", line: int
) -> "tuple[tuple[int, int, int], ...]":
    """The groups of a clock census: hours merged first, then their bins.

    THE ONE MERGE RULE (`calendar_rules.merged_groups`), asked twice. The
    hourly counts are merged first; where that leaves one group over every
    hour, the day is that one group. Inside each hour group its ten-minute
    bins are merged the same way, and a group they cannot split stands
    whole. Two groups of nought side by side are one. So every hour group
    is a union of the census's groups, and every count is nought or at
    least the line wherever the bins add to at least the line.

    Guarantees: accepts one count per ten-minute bin, six to an hour, and
    the census line; returns `(first, last, count)` covering every bin in
    order. Determinism: a function of the two. Raises nothing. No I/O.
    """
    size = len(bins)
    hours = size // BINS_PER_HOUR
    hourly: "list[int]" = []
    for hour in range(hours):
        first = BINS_PER_HOUR * hour
        hourly += [sum(bins[first : first + BINS_PER_HOUR])]
    top = calendar_rules.merged_groups(hourly, [], line)
    if not top:
        top = ((0, hours - 1, sum(hourly)),)
    found: "list[tuple[int, int, int]]" = []
    for first_hour, last_hour, count in top:
        low = BINS_PER_HOUR * first_hour
        high = BINS_PER_HOUR * last_hour + BINS_PER_HOUR - 1
        inner = calendar_rules.merged_groups(bins[low : high + 1], [], line)
        if not inner:
            inner = ((0, high - low, count),)
        for first, last, held in inner:
            group = (low + first, low + last, held)
            if found and held == 0 and found[len(found) - 1][2] == 0:
                group = (found[len(found) - 1][0], low + last, 0)
                found = found[: len(found) - 1]
            found += [group]
    return tuple(found)


def group_span(
    first: int,
    last: int,
    form: str,
    stride: int,
    body: "tuple[int, int]",
) -> "tuple[int, int] | None":
    """The first and last step of a group of bins inside the body, or None.

    Ordinals in the form's own unit, both on the step (`stride` units),
    from the first bin's first instant to the last bin's last, clipped to
    the body's two ends. None where no step of the group lies in the body.

    Guarantees: a function of the arguments. Raises nothing. No I/O.
    """
    unit = parsing.clock_step(form)
    low = -(-(first * TEN_MINUTES) // unit)
    high = ((last + 1) * TEN_MINUTES - 1) // unit
    low = max(low, body[0])
    high = min(high, body[1])
    low = -(-low // stride) * stride
    high = (high // stride) * stride
    if low > high:
        return None
    return (low, high)


def clock_group_reach(
    groups: "list[tuple[int, int, int]] | tuple[tuple[int, int, int], ...]",
    form: str,
    stride: int,
    body: "tuple[int, int]",
    heaps: "list[int]",
) -> "list[int]":
    """How many steps of each group lie in the body and on no heap (CC5).

    Guarantees: accepts the groups, the form, the step in the form's
    units, the body's two ends and the heaps' ordinals; returns one count
    per group. Determinism: a function of the arguments. Raises nothing.
    """
    found: "list[int]" = []
    for first, last, _count in groups:
        span = group_span(first, last, form, stride, body)
        if span is None:
            found += [0]
            continue
        units = (span[1] - span[0]) // stride + 1
        for at in heaps:
            if span[0] <= at <= span[1] and at % stride == 0:
                units = units - 1
        found += [units]
    return found


@dataclasses.dataclass(frozen=True)
class ClockCensus:
    """What a column of clock times publishes beside its tails (P4-D373).

    `step` in seconds; `heaps` as `(ordinal, count)` in the form's own
    unit, ascending; `groups` the census, or `()`; `left_out` whether the
    census was left out because one to the line less one cells were left
    beside the heaps.
    """

    step: int
    heaps: "tuple[tuple[int, int], ...]"
    groups: "tuple[tuple[int, int, int], ...]"
    left_out: bool


def clock_census_of(
    ordinals: "dict[int, int]",
    form: str,
    line: int,
    body: "tuple[int, int] | None",
) -> ClockCensus:
    """A column's step, heaps and census, from its parsed values (G7A.4b).

    `ordinals` counts every parsed cell by its place in the form's own
    unit, `body` the two tail boundaries as ordinals, or None on a column
    with no tails, whose body is every parsed cell. The heaps are counted
    over every cell; the census over the body's cells that stand on no
    heap.

    Guarantees: accepts the counts, the form, the census line and the
    body; returns the census. Determinism: a function of the four.
    Raises nothing. No I/O of any kind.
    """
    unit = parsing.clock_step(form)
    day = clock_day(form)
    step = written_step([ordinal * unit for ordinal in sorted(ordinals)], day)
    stride = step // unit
    counts: "dict[int, int]" = {}
    for ordinal in sorted(ordinals):
        counts[ordinal // stride] = ordinals[ordinal]
    standing = heaps_on_the_step(counts, day // step, line)
    heaps = tuple((index * stride, count) for index, count in standing)
    on_a_heap: "dict[int, bool]" = {}
    for value, _count in heaps:
        on_a_heap[value] = True
    bins = [0 for _bin in range(clock_bin_count(form))]
    left = 0
    for ordinal in sorted(ordinals):
        if ordinal in on_a_heap:
            continue
        if body is not None and not body[0] <= ordinal <= body[1]:
            continue
        place = clock_bin_of(ordinal, form)
        bins[place] = bins[place] + ordinals[ordinal]
        left = left + ordinals[ordinal]
    if left < line:
        return ClockCensus(step, heaps, (), left > 0)
    return ClockCensus(step, heaps, nested_groups(bins, line), False)


@dataclasses.dataclass(frozen=True)
class ClockBlock:
    """One stretch of a clock body's ranks (method G7A.4b).

    `cells` ranks from `first_rank`, standing between the ordinals `low`
    and `high`, both on the step: a HEAP's ranks all stand on its value
    (`low == high`), and a RUN's are laid over the steps from `low` to
    `high`, which hold no heap. `group` is the census group the stretch
    lies in, by its index, or nought on a body that publishes no census.
    """

    first_rank: int
    cells: int
    low: int
    high: int
    heap: bool
    group: int


def run_shares(count: int, units: "list[int]", first: "list[int]") -> "list[int]":
    """A group's count shared over its runs by their steps (method G7A.4b).

    Run `j` takes `first[j]` cells first -- one for each tail boundary
    standing in it on no heap -- and then `floor(r U<=j / U) -
    floor(r U<j / U)` of the `r` left, `U` the group's steps and `U<=j`
    and `U<j` those through and before run `j`. Where the first cells
    outnumber the count, none is taken first.

    Guarantees: returns one share per run, adding to `count`.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    taken = [cells for cells in first]
    rest = count - sum(taken)
    if rest < 0:
        taken = [0 for _run in units]
        rest = count
    total = sum(units)
    shares: "list[int]" = []
    before = 0
    for place in range(len(units)):
        share = (rest * (before + units[place])) // total - (rest * before) // total
        before = before + units[place]
        shares += [taken[place] + share]
    return shares


def codes_of(unread: "dict[str, int]", line: int) -> "list[tuple[str, int]]":
    """The codes a column of clock times publishes (contract CH2).

    Every spelling its clock reading did not accept that at least the
    census line's rows wrote, with its count, in text order.

    Guarantees: a function of the two. Raises nothing. No I/O.
    """
    return [
        (spelling, unread[spelling])
        for spelling in sorted(unread)
        if unread[spelling] >= line
    ]


def clock_body_blocks(
    parsed: int,
    tails: "tuple[int, int] | None",
    body: "tuple[int, int]",
    groups: "tuple[tuple[int, int, int], ...]",
    heaps: "tuple[tuple[int, int], ...]",
    form: str,
    stride: int,
) -> "tuple[ClockBlock, ...] | None":
    """Every stretch of a clock body, in rank order (method G7A.4b).

    THE RANK RULE, the part of it no word decides. The body's ranks run
    from the low tail's rows (nought with no tails) and are laid out in
    ordinal order: each heap inside the body is one stretch of its count;
    each census group's steps inside the body and on no heap are cut by
    the heaps inside it into RUNS, and its count is shared over them by
    their steps: run j takes `floor(n U<=j / U) - floor(n U<j / U)` of
    the group's `n`, with `U` the group's steps. A run holding a tail
    boundary that stands on no heap takes ONE CELL FIRST and shares the
    rest, so the boundary's rank always lands in it (the 3b.5 skeptic's
    MAJOR 1: a first run of two steps in forty-one took none of twenty
    cells, and the pinned boundary took a heap's cell). A body publishing
    no census is one group over the whole dial, counting the body's cells
    on no heap.

    Guarantees: accepts the parsed count, the two tails' rows or None,
    the body's two ends, the census, the heaps as ordinals, the form and
    the step in the form's units; returns the stretches, or None where
    the counts do not add up to the body or a group counting cells has
    no step to hold them -- which a description the loader accepted never
    is (CC3, CC5). Determinism: a function of the arguments. Raises
    nothing. No I/O of any kind.
    """
    low_rows = 0 if tails is None else tails[0]
    high_rows = 0 if tails is None else tails[1]
    size = parsed - low_rows - high_rows
    inside = [(at, count) for at, count in heaps if body[0] <= at <= body[1]]
    heap_values = [at for at, _count in inside]
    held = 0
    for _at, count in inside:
        held = held + count
    taken: "tuple[tuple[int, int, int], ...]" = groups
    if not groups:
        taken = ((0, clock_bin_count(form) - 1, size - held),)
    ends: "list[int]" = []
    if tails is not None:
        for end in body:
            if end not in heap_values and end not in ends:
                ends += [end]
    blocks: "list[ClockBlock]" = []
    cursor = low_rows
    for index in range(len(taken)):
        first, last, count = taken[index]
        mine = [
            (at, cells)
            for at, cells in inside
            if first <= clock_bin_of(at, form) <= last
        ]
        events: "list[tuple[int, int, int, bool]]" = []
        for at, cells in mine:
            events += [(at, at, cells, True)]
        if count > 0:
            span = group_span(first, last, form, stride, body)
            if span is None:
                return None
            runs: "list[tuple[int, int]]" = []
            start = span[0]
            for at, _cells in mine:
                if at < span[0] or at > span[1]:
                    continue
                if at > start:
                    runs += [(start, at - stride)]
                start = at + stride
            if start <= span[1]:
                runs += [(start, span[1])]
            units = [(stop - begin) // stride + 1 for begin, stop in runs]
            total = sum(units)
            if total < 1:
                return None
            forced = [0 for _run in runs]
            for end in ends:
                for place in range(len(runs)):
                    if runs[place][0] <= end <= runs[place][1]:
                        forced[place] = forced[place] + 1
            shares = run_shares(count, units, forced)
            for place in range(len(runs)):
                events += [(runs[place][0], runs[place][1], shares[place], False)]
        events = sorted(events)
        for low, high, cells, heap in events:
            if cells <= 0:
                continue
            blocks += [ClockBlock(cursor, cells, low, high, heap, index)]
            cursor = cursor + cells
    if cursor != parsed - high_rows:
        return None
    return tuple(blocks)


def clock_rank_windows(
    parsed: int,
    tails: "tuple[int, int] | None",
    body: "tuple[int, int]",
    groups: "tuple[tuple[int, int, int], ...]",
    heaps: "tuple[tuple[int, int], ...]",
    form: str,
    stride: int,
) -> "tuple[list[int], list[int]] | None":
    """The window every rank of a census-laid clock column stands in (G12.10).

    A tail rank anywhere beyond its boundary; a boundary rank on its
    boundary; every other body rank inside its census GROUP's steps in the
    body -- the group's, not its run's, so a real column whose rung stands
    on the far side of a heap from where the twin's share put it is still
    inside. Ordinals in the form's own unit.

    Guarantees: as `clock_body_blocks`, whose stretches it reads; None
    where that is None. Determinism: a function of the arguments. Raises
    nothing. No I/O of any kind.
    """
    blocks = clock_body_blocks(parsed, tails, body, groups, heaps, form, stride)
    if blocks is None:
        return None
    top = parsing.CLOCK_CAPACITY[form] - 1
    reach: "dict[int, tuple[int, int]]" = {}
    for block in blocks:
        low, high = block.low, block.high
        if block.group in reach:
            low = min(low, reach[block.group][0])
            high = max(high, reach[block.group][1])
        reach[block.group] = (low, high)
    lows = [0 for _rank in range(parsed)]
    highs = [top for _rank in range(parsed)]
    if tails is not None:
        for rank in range(min(tails[0], parsed)):
            highs[rank] = max(0, body[0] - 1)
        for rank in range(max(0, parsed - tails[1]), parsed):
            lows[rank] = min(top, body[1] + 1)
    for block in blocks:
        low, high = reach[block.group]
        if block.heap:
            low, high = block.low, block.high
        for rank in range(block.first_rank, block.first_rank + block.cells):
            lows[rank] = low
            highs[rank] = high
    if tails is not None and 0 <= tails[0] < parsed:
        lows[tails[0]] = body[0]
        highs[tails[0]] = body[0]
        last = parsed - 1 - tails[1]
        if 0 <= last < parsed:
            lows[last] = body[1]
            highs[last] = body[1]
    return (lows, highs)


def off_the_heaps(distance: int, heaps: "list[int]") -> int:
    """The `distance`-th distance beyond a boundary that is no heap's.

    A tail's cells on no heap are drawn through its shape in a space with
    the heaps' distances taken out, and read back here, so no such cell
    lands on a heap and every heap's count stays its own (method G7A.4b).
    `heaps` are the heaps' distances, ascending.

    Guarantees: accepts a whole distance of at least one and the heaps'
    distances; returns a whole distance at least as large, on no heap,
    and strictly increasing in `distance`. Raises nothing. No I/O.
    """
    found = distance
    for heap in heaps:
        if heap <= found:
            found = found + 1
    return found


def tail_less_heaps(
    rows: int,
    mean: "float | None",
    root: "float | None",
    heaps: "list[tuple[int, int]]",
) -> "tuple[int, float, float]":
    """A tail's rows and two distances once the cells on its heaps are out.

    `heaps` are `(distance, cells)` of the heaps beyond the boundary. What
    is left of the published sum and sum of squares, over the rows left,
    gives the mean and the root-mean-square the tail's shape is drawn
    through (method G7A.4b), at least one unit and the root at least the
    mean. A tail publishing no mean is drawn at one unit, as G7.3b draws
    it.

    Guarantees: returns (rows left, mean, root). Determinism: a function
    of the arguments, in binary64 in a fixed order. Raises nothing.
    """
    left = rows
    total = 0
    squares = 0
    for distance, cells in heaps:
        left = left - cells
        total = total + cells * distance
        squares = squares + cells * distance * distance
    if left <= 0:
        return (0, 1.0, 1.0)
    if mean is None:
        return (left, 1.0, 1.0)
    whole = root if root is not None else mean
    kept = (rows * mean - total) / left
    kept = max(kept, 1.0)
    square = (rows * (whole * whole) - squares) / left
    rooted = math.sqrt(square) if square > 0.0 else kept
    return (left, kept, max(rooted, kept))


# anchor 3b-C2 (P4-D374)
# anchor 3b-G1 (P4-D375)
# anchor 3b-G3 (P4-D376)
# anchor 3b-G2 (P4-D377)
# anchor 3b-7 (P4-D378)
# anchor 3b-J (P4-D379)

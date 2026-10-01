"""The full-fill certificate of a weekday census (landing 3b.1, plan P4-D355).

WHAT A READER HOLDS about a column of whole dates, from its description
alone: the body `B = P - low.rows - high.rows` (P the parsed cells);
the KNOT days -- the two tail boundaries and every published rung --
each with two rank facts, the body cells strictly before it at most
`lt` and at or before it at least `le` (a rung selected at body rank
`i` gives `lt = i`, `le = i + 1`; the low boundary `lt = 0`, the high
boundary `le = B`); the count of different days the body holds, read
from `n_distinct` as `[D_min, D_max]` (one spelling per day, contract
WC6); and the census, an entry of the menu (`calendar_rules`).

STRETCHES AND CLASSES. Each knot day is a stretch, and so is each run
of days strictly between two consecutive knots. A CLASS is a knot day,
or the days of one open stretch that fall on one weekday, less any
HOLE -- a day no body cell can hold: one the column's declared missing
values name, a placeholder day its `sentinel_verdicts` publish as
`read_as_missing` (`calendar_rules.placeholder_holes`), or one the
censuses of written forms leave empty (`calendar_rules.form_holes`: a
width word one field alone shows says the other field is ten or more in
every cell, a month name of either length says every cell is in May).
Every published fact is unchanged by exchanging two days of one class,
and ONLY of one class: the rank facts see stretch totals, the census
and the menu weekday totals, the count of different days is a count,
the tails are not touched, and a form census names the same form for
either day because neither is a hole. A hole is not exchangeable with
anything, which is why it is no member of a class (review of landing
3b.1, finding 1: `m/d/yyyy` dates all past the ninth published
`{first-field-unpadded}`, a reader held the first to the ninth of
every month empty, and a witness standing there certified days the
count of different days pinned below the line).

THE CERTIFICATE. For every class whose weekday lies in a non-zero
group, a WITNESS: a table meeting every published fact, what the menu
entry tells, and the count of different days, that puts at least the
line on one day of the class. A witness is one min-cost circulation --
the source feeds the chain of prefix counts, the chain feeds each
stretch (a knot day at least one cell), each stretch feeds its classes
(capacity one cell a day at cost nought, any more at cost one), the
classes feed their weekday, the weekdays their group, and each group
takes exactly its count -- whose least cost, the cells no day holds
alone, is at most `B - D`, and whose non-empty parts number at most
`D`, so the table can be laid on exactly `D` different days
(`_laid_out`). Then every set of days holding a day of a certified
class can hold the line: exchanging the witness's day with any day of
its class changes no fact.

A class no witness certifies is asked on stage 3's facts alone -- the
same network with no census at all, every weekday open, the ones the
census publishes as empty included, on the reader's bounds (a count of
nought is census information too: review of landing 3b.1, finding 1).
If stage 3 could put the
line on its day, the census is what keeps it below and the census is
WITHHELD. Otherwise the class is RESIDUE: it must lie in a stretch the
rank facts cap below the line, and every CONFIGURATION of the residue
stage 3 allows -- each residue class's cells and the residue's occupied
days -- the census must allow too (`_residue_equivalent`). Then no set
of days is confined inside one to the line less one by the census.

THE PRODUCER asks it with the REAL count of different days on the
census side and the reader's bounds on stage 3's side, and with every
hole; the LOADER asks it with the reader's bounds on both sides and
the holes the published form censuses and placeholder decisions show,
leaving out only the declared missing days no description publishes.
Either answer is cached on its question.

Guarantees for the whole module: every function is a function of its
arguments; nothing reads a table, a clock, an environment variable or
a random source. No I/O of any kind.
"""

import dataclasses

from synthtwin import calendar_rules

# More residue configurations than this and the census is withheld.
CONFIGURATION_CAP = 20000

# A number no count of this module reaches.
_FAR = 1 << 60

# The cache of answers, keyed on the whole question (`check`), and the
# most it keeps before it forgets them all.
_ANSWERS: "dict[tuple[object, ...], Verdict]" = {}
_ANSWERS_KEPT = 512


@dataclasses.dataclass(frozen=True)
class Witness:
    """One certified class and the table that certifies it, day by day.

    `klass` is (stretch, weekday), `day` the day of the class holding
    at least the line, and `table` every body day the table occupies
    with its cells, in day order.
    """

    klass: "tuple[int, int]"
    day: int
    table: "tuple[tuple[int, int], ...]"


@dataclasses.dataclass(frozen=True)
class Verdict:
    """The certificate's answer for one census.

    `holds` says whether it is published; `reason` is a
    `calendar_rules.REASON_*` word where it is not; `detail` says what
    decided it, for a test to read, and is never published; `witnesses`
    are the certified classes' tables; `residue` the residue classes;
    `solves` how many networks were solved; `mode` how the residue was
    checked (`vertices`, `full` or empty).
    """

    holds: bool
    reason: str
    detail: str
    witnesses: "tuple[Witness, ...]"
    residue: "tuple[tuple[int, int], ...]"
    solves: int
    mode: str


@dataclasses.dataclass(frozen=True)
class Facts:
    """The description-level facts of one column's body (module docstring).

    `fewest` and `most_days` bound the body's different days on the
    census side; `reader_fewest` and `reader_most` are the reader's
    bounds, on stage 3's side. `prefix_low[s]` and `prefix_high[s]`
    bound the cells in stretches 0 to s from the rank facts;
    `most[s]` is the most stretch s can hold once those bounds are made
    monotone.
    """

    body: int
    low: int
    high: int
    knots: "dict[int, tuple[int, int]]"
    knot_days: "tuple[int, ...]"
    stretches: "tuple[tuple[bool, int, int], ...]"
    prefix_low: "tuple[int, ...]"
    prefix_high: "tuple[int, ...]"
    most: "tuple[int, ...]"
    classes: "dict[tuple[int, int], tuple[int, ...]]"
    keys: "tuple[tuple[int, int], ...]"
    groups: "tuple[tuple[int, int, int], ...]"
    where: "tuple[int, ...]"
    zero: "frozenset[int]"
    shortable: "tuple[int, ...]"
    entry: int
    line: int
    fewest: int
    most_days: int
    reader_fewest: int
    reader_most: int
    holes: "frozenset[int]"


def facts_of(
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
    reader_fewest: int,
    reader_most: int,
    line: int,
    groups: "tuple[tuple[int, int, int], ...]",
    real_days: int,
    holes: "tuple[int, ...]",
) -> Facts:
    """The facts of one census, from the numbers a description publishes.

    `rungs` are `(rank, day)` for every published rung, the rank over
    the parsed cells; `real_days` is the body's real count of different
    days where the producer asks (the census side then uses it) or -1
    where the loader asks (the reader's bounds on both sides); `holes`
    are days no body cell can hold.

    Guarantees: accepts the description's numbers; returns the facts.
    Determinism: a function of the arguments. Raises nothing. No I/O.
    """
    body = parsed - rows_low - rows_high
    knots = _knots_of(parsed, rows_low, rows_high, low, high, rungs)
    knot_days = tuple(sorted(knots))
    stretches: "list[tuple[bool, int, int]]" = []
    for index in range(len(knot_days)):
        day = knot_days[index]
        stretches += [(True, day, day)]
        if index + 1 < len(knot_days) and knot_days[index + 1] - day > 1:
            stretches += [(False, day + 1, knot_days[index + 1] - 1)]
    count = len(stretches)
    prefix_low: "list[int]" = []
    prefix_high: "list[int]" = []
    for place in range(count):
        least = 0
        greatest = body
        is_knot, first, _last = stretches[place]
        if is_knot:
            least = knots[first][1]
        if place + 1 < count:
            after_knot, after_first, _after_last = stretches[place + 1]
            if after_knot:
                greatest = min(greatest, knots[after_first][0])
        else:
            least = body
        prefix_low += [least]
        prefix_high += [greatest]
    rising = [value for value in prefix_low]
    for place in range(1, count):
        rising[place] = max(rising[place], rising[place - 1])
    falling = [value for value in prefix_high]
    for place in range(count - 2, -1, -1):
        falling[place] = min(falling[place], falling[place + 1])
    most: "list[int]" = []
    for place in range(count):
        before = rising[place - 1] if place > 0 else 0
        most += [max(0, falling[place] - before)]
    holed = set(holes)
    # EACH CLASS IS GROWN AS A LIST AND FROZEN ONCE (review of landing
    # 3b.1, finding 10): a class grown as a tuple copied everything it
    # held on every day, so 100 dates spread over 6,000 years took 316
    # seconds here before a refusal the numbers alone decide.
    growing: "dict[tuple[int, int], list[int]]" = {}
    for place in range(count):
        is_knot, first, last = stretches[place]
        for day in range(first, last + 1):
            if not is_knot and day in holed:
                continue
            key = (place, calendar_rules.weekday_of(day))
            if key in growing:
                members = growing[key]
                members += [day]
            else:
                growing[key] = [day]
    classes: "dict[tuple[int, int], tuple[int, ...]]" = {
        key: tuple(growing[key]) for key in growing
    }
    where = calendar_rules.where_of(groups)
    zero = frozenset(
        weekday
        for weekday in range(calendar_rules.WEEKDAYS)
        if groups and groups[where[weekday]][2] == 0
    )
    shortable = tuple(
        sorted({key[1] for key in classes if key[1] not in zero})
    )
    fewest = reader_fewest
    most_days = reader_most
    if real_days >= 0:
        fewest = real_days
        most_days = real_days
    return Facts(
        body=body,
        low=low,
        high=high,
        knots=knots,
        knot_days=knot_days,
        stretches=tuple(stretches),
        prefix_low=tuple(prefix_low),
        prefix_high=tuple(prefix_high),
        most=tuple(most),
        classes=classes,
        keys=tuple(sorted(classes)),
        groups=groups,
        where=where,
        zero=zero,
        shortable=shortable,
        entry=calendar_rules.entry_of(groups),
        line=line,
        fewest=fewest,
        most_days=most_days,
        reader_fewest=reader_fewest,
        reader_most=reader_most,
        holes=frozenset(holed),
    )


def _knots_of(
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
) -> "dict[int, tuple[int, int]]":
    """Every knot day with its two rank facts (module docstring).

    Counted from the boundaries and the rungs alone, so WC5 and the
    cheap refusals read them without walking a single day of the span.
    """
    body = parsed - rows_low - rows_high
    knots: "dict[int, tuple[int, int]]" = {low: (0, 1)}
    if high in knots:
        knots[high] = (0, body)
    else:
        knots[high] = (body - 1, body)
    for rank, day in rungs:
        inside = rank - rows_low
        if day in knots:
            before, upto = knots[day]
            knots[day] = (min(before, inside), max(upto, inside + 1))
        else:
            knots[day] = (inside, inside + 1)
    knots[low] = (0, knots[low][1])
    knots[high] = (knots[high][0], body)
    return knots


# -- the network ------------------------------------------------------------
#
# A min-cost circulation with lower bounds. Arc `a` and its reverse
# `a + 1` are stored side by side, so `a ^ 1` is always the partner. A
# lower bound becomes a demand at each end; a super source and sink then
# carry the demands, and the least cost is found by the primal-dual
# method: shortest distances under reduced costs (every cost here is a
# small whole number, so the distances are counted in buckets), then a
# maximum flow over the arcs whose reduced cost is nought, repeated
# until every demand is met.


@dataclasses.dataclass(frozen=True)
class _Net:
    nodes: int
    head: "list[list[int]]"
    to: "list[int]"
    cap: "list[int]"
    cost: "list[int]"
    excess: "list[int]"
    fixed: "list[int]"


def _net(nodes: int) -> _Net:
    return _Net(
        nodes=nodes,
        head=[[] for _ in range(nodes + 2)],
        to=[],
        cap=[],
        cost=[],
        excess=[0 for _ in range(nodes + 2)],
        fixed=[0],
    )


def _arc(net: _Net, tail: int, head: int, capacity: int, cost: int) -> int:
    arc = len(net.to)
    outgoing = net.head[tail]
    outgoing += [arc]
    incoming = net.head[head]
    incoming += [arc + 1]
    targets = net.to
    targets += [head, tail]
    capacities = net.cap
    capacities += [capacity, 0]
    costs = net.cost
    costs += [cost, -cost]
    return arc


def _add(
    net: _Net, tail: int, head: int, least: int, greatest: int, cost: int
) -> int:
    """An arc carrying `least` to `greatest` at `cost` a unit."""
    if least:
        net.excess[head] = net.excess[head] + least
        net.excess[tail] = net.excess[tail] - least
        net.fixed[0] = net.fixed[0] + least * cost
    return _arc(net, tail, head, max(0, greatest - least), cost)


def _distances(net: _Net, potential: "list[int]", start: int) -> "list[int]":
    """Shortest distances from `start` under reduced costs, by buckets."""
    total = net.nodes + 2
    distance = [_FAR for _ in range(total)]
    distance[start] = 0
    buckets: "list[list[int]]" = [[start]]
    level = 0
    head, to, cap, cost = net.head, net.to, net.cap, net.cost
    while level < len(buckets):
        bucket = buckets[level]
        index = 0
        while index < len(bucket):
            node = bucket[index]
            index = index + 1
            if distance[node] != level:
                continue
            for arc in head[node]:
                if cap[arc] <= 0:
                    continue
                other = to[arc]
                reach = level + cost[arc] + potential[node] - potential[other]
                if reach < distance[other]:
                    distance[other] = reach
                    while len(buckets) <= reach:
                        buckets += [[]]
                    waiting = buckets[reach]
                    waiting += [other]
        level = level + 1
    return distance


def _pushed(
    net: _Net, potential: "list[int]", start: int, end: int, limit: int
) -> int:
    """A maximum flow up to `limit` over the arcs of reduced cost nought."""
    total = net.nodes + 2
    head, to, cap, cost = net.head, net.to, net.cap, net.cost
    moved = 0
    while moved < limit:
        level = [-1 for _ in range(total)]
        level[start] = 0
        queue = [start]
        index = 0
        while index < len(queue):
            node = queue[index]
            index = index + 1
            for arc in head[node]:
                other = to[arc]
                if (
                    cap[arc] > 0
                    and level[other] < 0
                    and cost[arc] + potential[node] - potential[other] == 0
                ):
                    level[other] = level[node] + 1
                    queue += [other]
        if level[end] < 0:
            return moved
        pointer = [0 for _ in range(total)]
        path = [0 for _ in range(total)]
        while moved < limit:
            depth = 0
            node = start
            found = 0
            while True:
                if node == end:
                    found = limit - moved
                    for step in range(depth):
                        found = min(found, cap[path[step]])
                    for step in range(depth):
                        arc = path[step]
                        cap[arc] = cap[arc] - found
                        cap[arc ^ 1] = cap[arc ^ 1] + found
                    break
                advanced = False
                arcs = head[node]
                while pointer[node] < len(arcs):
                    arc = arcs[pointer[node]]
                    other = to[arc]
                    if (
                        cap[arc] > 0
                        and level[other] == level[node] + 1
                        and cost[arc] + potential[node] - potential[other] == 0
                    ):
                        path[depth] = arc
                        depth = depth + 1
                        node = other
                        advanced = True
                        break
                    pointer[node] = pointer[node] + 1
                if advanced:
                    continue
                if depth == 0:
                    break
                level[node] = -1
                depth = depth - 1
                node = to[path[depth] ^ 1]
                pointer[node] = pointer[node] + 1
            if found == 0:
                break
            moved = moved + found
    return moved


def _solve(net: _Net) -> "int | None":
    """The least cost of a circulation meeting every bound, or None."""
    start = net.nodes
    end = net.nodes + 1
    need = 0
    for node in range(net.nodes):
        if net.excess[node] > 0:
            _arc(net, start, node, net.excess[node], 0)
            need = need + net.excess[node]
        elif net.excess[node] < 0:
            _arc(net, node, end, -net.excess[node], 0)
    potential = [0 for _ in range(net.nodes + 2)]
    flow = 0
    spent = net.fixed[0]
    while flow < need:
        distance = _distances(net, potential, start)
        if distance[end] >= _FAR:
            return None
        for node in range(net.nodes + 2):
            if distance[node] < _FAR:
                potential[node] = potential[node] + distance[node]
        moved = _pushed(net, potential, start, end, need - flow)
        if moved <= 0:
            return None
        spent = spent + moved * (potential[end] - potential[start])
        flow = flow + moved
    return spent


# -- one table ----------------------------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Table:
    """A flow read as a table: per part, its class, whether it is the
    taken part, its cells and its days."""

    parts: "tuple[tuple[tuple[int, int], bool, int, int], ...]"
    nonempty: int
    cost: int


def _chain(facts: Facts, net: _Net, chain: int, rows: int) -> bool:
    """The source, the chain of prefix counts and each stretch's arc."""
    body = facts.body
    count = len(facts.stretches)
    _add(net, 0, chain, body, body, 0)
    for place in range(count):
        least = 1 if facts.stretches[place][0] else 0
        _add(net, chain + place, rows + place, least, body, 0)
        if place + 1 < count:
            low = facts.prefix_low[place]
            high = facts.prefix_high[place]
            if low > high:
                return False
            _add(net, chain + place, chain + place + 1, body - high, body - low, 0)
    return True


def _read(
    net: _Net,
    arcs: "list[tuple[tuple[int, int], bool, int, int, int]]",
) -> "tuple[tuple[tuple[int, int], bool, int, int], ...]":
    parts: "list[tuple[tuple[int, int], bool, int, int]]" = []
    for key, taken, base, over, days in arcs:
        cells = net.cap[base ^ 1] + net.cap[over ^ 1]
        parts += [(key, taken, cells, days)]
    return tuple(parts)


def _census_table(
    facts: Facts,
    take: "dict[tuple[int, int], int]",
    need: "dict[int, tuple[int, int]]",
    bounds: "dict[int, tuple[int, int]]",
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
    tally: "list[int]",
    top_bounds: "tuple[tuple[int, int], ...] | None" = None,
) -> "_Table | None":
    """A table meeting every fact and the census, or None.

    `take[k]` days of class k (its first ones) are the TAKEN part, and
    for each weekday of `need` its taken days together hold `need[w]`;
    `bounds` bounds weekday totals (one alternative of
    `calendar_rules.branches_of`); `fixed` holds residue classes at
    exact cells, whose overflow `spent` and occupied days `occupied` are
    counted against the budget and the count of different days.
    `top_bounds`, where given, bounds each group's total `(least, most)` in place of
    its published count: the withholding's own side (`withholding`).
    """
    count = len(facts.stretches)
    chain = 2
    rows = chain + count
    days = rows + count
    hubs = days + calendar_rules.WEEKDAYS
    tops = hubs + calendar_rules.WEEKDAYS
    net = _net(tops + len(facts.groups))
    body = facts.body
    if not _chain(facts, net, chain, rows):
        return None
    arcs: "list[tuple[tuple[int, int], bool, int, int, int]]" = []
    for key in facts.keys:
        place, weekday = key
        if key in fixed:
            if fixed[key] > 0:
                _add(net, rows + place, days + weekday, fixed[key], fixed[key], 0)
            continue
        members = len(facts.classes[key])
        taken = take[key] if key in take else 0
        if taken > 0:
            into = hubs + weekday if weekday in need else days + weekday
            base = _add(net, rows + place, into, 0, taken, 0)
            over = _add(net, rows + place, into, 0, body, 1)
            arcs += [(key, True, base, over, taken)]
        if members - taken > 0:
            base = _add(net, rows + place, days + weekday, 0, members - taken, 0)
            over = _add(net, rows + place, days + weekday, 0, body, 1)
            arcs += [(key, False, base, over, members - taken)]
    for weekday in sorted(need):
        least, greatest = need[weekday]
        _add(net, hubs + weekday, days + weekday, least, greatest, 0)
    for weekday in range(calendar_rules.WEEKDAYS):
        least, greatest = 0, body
        if weekday in bounds:
            least, greatest = bounds[weekday]
        _add(net, days + weekday, tops + facts.where[weekday], least, greatest, 0)
    for index in range(len(facts.groups)):
        held = facts.groups[index][2]
        least, greatest = held, held
        if top_bounds is not None:
            least, greatest = top_bounds[index]
        _add(net, tops + index, 1, least, greatest, 0)
    _add(net, 1, 0, body, body, 0)
    tally[0] = tally[0] + 1
    cost = _solve(net)
    if cost is None or cost > facts.body - facts.fewest - spent:
        return None
    parts = _read(net, arcs)
    nonempty = len([part for part in parts if part[2] > 0])
    if nonempty + occupied > facts.most_days:
        if top_bounds is None:
            return None
        merged = _merged(
            facts, parts, cost, facts.body - facts.fewest - spent, occupied,
            (need, bounds, fixed, top_bounds),
        )
        if merged is None:
            return None
        parts, cost = merged
        nonempty = len([part for part in parts if part[2] > 0])
    return _Table(parts=parts, nonempty=nonempty, cost=cost)


def _merged(
    facts: Facts,
    parts: "tuple[tuple[tuple[int, int], bool, int, int], ...]",
    cost: int,
    budget: int,
    occupied: int,
    sides: "tuple[dict[int, tuple[int, int]], dict[int, tuple[int, int]], dict[tuple[int, int], int], tuple[tuple[int, int], ...]]",
) -> "tuple[tuple[tuple[tuple[int, int], bool, int, int], ...], int] | None":
    """A table's parts merged until they fit the most different days, or None.

    THE CHEAPEST TABLE SPREADS ITS CELLS OVER EVERY PART IT CAN, and a
    column of few dates has far fewer days than classes: 471 rows on 26
    to 36 different days over 57 classes found no table at all, so its
    withholding could not be certified (review of landing 3b.1, item 2,
    measured on sparse schedules). Where only group TOTALS are bounded
    -- the withholding's two halves of the week -- every cell of one
    untaken part of a stretch between two knots moves into another
    non-empty part, of any stretch and either half, wherever every bound
    still holds after the move: each prefix of stretches the move passes
    stays within its rank facts, both group totals within `top_bounds`,
    both weekday totals within `bounds`, and a taken part within `need`.
    A merge inside one stretch and one half was not enough: 800 visits
    of a weekly Friday clinic on 18 different days, seven of them knot
    days, kept a part in each half of each of six stretches between the
    knots -- nineteen -- and neither band found a table (review of the
    third review's repair). Each merge takes the move that raises the
    cost least -- into the part with the most room left, which only the
    room decides -- and the cost may not pass `budget`. Every move keeps
    every bound the network holds, so a table found this way is a table,
    which is all a witness needs. `sides` is `(need, bounds, fixed,
    top_bounds)` as `_census_table` holds them.
    """
    need, bounds, fixed, top_bounds = sides
    keys = [part[0] for part in parts]
    taken = [part[1] for part in parts]
    cells = [part[2] for part in parts]
    days = [part[3] for part in parts]
    spent = cost
    count = len(facts.stretches)
    held = [0 for _ in range(count)]
    weekday_held = [0 for _ in range(calendar_rules.WEEKDAYS)]
    hub = [0 for _ in range(calendar_rules.WEEKDAYS)]
    for key in fixed:
        held[key[0]] = held[key[0]] + fixed[key]
        weekday_held[key[1]] = weekday_held[key[1]] + fixed[key]
    for place in range(len(keys)):
        stretch, weekday = keys[place]
        held[stretch] = held[stretch] + cells[place]
        weekday_held[weekday] = weekday_held[weekday] + cells[place]
        if taken[place] and weekday in need:
            hub[weekday] = hub[weekday] + cells[place]
    group_held = [0 for _ in top_bounds]
    for weekday in range(calendar_rules.WEEKDAYS):
        group_held[facts.where[weekday]] = group_held[facts.where[weekday]] + weekday_held[weekday]

    def over(cells_held: int, room: int) -> int:
        return max(0, cells_held - room)

    def movable(first: int, second: int, prefix: "list[int]") -> bool:
        moved = cells[first]
        source, from_day = keys[first]
        target, to_day = keys[second]
        for place in range(min(source, target), max(source, target)):
            if source < target and prefix[place] - moved < facts.prefix_low[place]:
                return False
            if source > target and prefix[place] + moved > facts.prefix_high[place]:
                return False
        if from_day != to_day:
            if from_day in bounds and weekday_held[from_day] - moved < bounds[from_day][0]:
                return False
            if to_day in bounds and weekday_held[to_day] + moved > bounds[to_day][1]:
                return False
        losing = facts.where[from_day]
        gaining = facts.where[to_day]
        if losing != gaining and (
            group_held[losing] - moved < top_bounds[losing][0]
            or group_held[gaining] + moved > top_bounds[gaining][1]
        ):
            return False
        return not (taken[second] and to_day in need and hub[to_day] + moved > need[to_day][1])

    nonempty = len([cells_held for cells_held in cells if cells_held > 0])
    while nonempty + occupied > facts.most_days:
        prefix: "list[int]" = []
        running = 0
        for place in range(count):
            running = running + held[place]
            prefix += [running]
        into = sorted(
            (-max(0, days[place] - cells[place]), place)
            for place in range(len(keys))
            if cells[place] > 0
        )
        best: "tuple[int, int, int, int] | None" = None
        for first in range(len(keys)):
            if cells[first] <= 0 or taken[first] or facts.stretches[keys[first][0]][0]:
                continue
            for _room, second in into:
                if second == first or not movable(first, second, prefix):
                    continue
                raised = (
                    spent
                    - over(cells[first], days[first])
                    - over(cells[second], days[second])
                    + over(cells[first] + cells[second], days[second])
                )
                if raised <= budget and (best is None or (raised, cells[first], first, second) < best):
                    best = (raised, cells[first], first, second)
                break
        if best is None:
            return None
        raised, moved, first, second = best
        source, from_day = keys[first]
        target, to_day = keys[second]
        held[source] = held[source] - moved
        held[target] = held[target] + moved
        weekday_held[from_day] = weekday_held[from_day] - moved
        weekday_held[to_day] = weekday_held[to_day] + moved
        group_held[facts.where[from_day]] = group_held[facts.where[from_day]] - moved
        group_held[facts.where[to_day]] = group_held[facts.where[to_day]] + moved
        if taken[second] and to_day in need:
            hub[to_day] = hub[to_day] + moved
        cells[second] = cells[second] + moved
        cells[first] = 0
        spent = raised
        nonempty = nonempty - 1
    return (
        tuple(
            (keys[place], taken[place], cells[place], days[place])
            for place in range(len(keys))
        ),
        spent,
    )


def _stage3_table(
    facts: Facts,
    take: "dict[tuple[int, int], int]",
    least: int,
    greatest: int,
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
    tally: "list[int]",
) -> "_Table | None":
    """A table meeting stage 3's facts alone, on the reader's bounds.

    NO CENSUS AT ALL: one group holds every weekday, the ones the census
    publishes as empty included. The baseline is what a reader holds
    WITHOUT the census, so none of the census's information may stand in
    it, and a count of nought is information too (review of landing
    3b.1, finding 1): with the weekend held empty on this side, 1,035
    business dates whose p05 left ten body rows before January 16 had
    every business day of January 2 to 15 pinned to one row by the
    census -- a Saturday could take any of them -- and the certificate
    counted those days as residue both sides agreed on. The taken days
    together hold `least` to `greatest` cells.
    """
    count = len(facts.stretches)
    chain = 2
    rows = chain + count
    hub = rows + count
    top = hub + 1
    net = _net(top + 1)
    body = facts.body
    if not _chain(facts, net, chain, rows):
        return None
    arcs: "list[tuple[tuple[int, int], bool, int, int, int]]" = []
    for key in facts.keys:
        place, weekday = key
        if key in fixed:
            if fixed[key] > 0:
                _add(net, rows + place, top, fixed[key], fixed[key], 0)
            continue
        members = len(facts.classes[key])
        taken = take[key] if key in take else 0
        if taken > 0:
            base = _add(net, rows + place, hub, 0, taken, 0)
            over = _add(net, rows + place, hub, 0, body, 1)
            arcs += [(key, True, base, over, taken)]
        if members - taken > 0:
            base = _add(net, rows + place, top, 0, members - taken, 0)
            over = _add(net, rows + place, top, 0, body, 1)
            arcs += [(key, False, base, over, members - taken)]
    if take:
        _add(net, hub, top, least, greatest, 0)
    _add(net, top, 1, body, body, 0)
    _add(net, 1, 0, body, body, 0)
    tally[0] = tally[0] + 1
    cost = _solve(net)
    if cost is None or cost > facts.body - facts.reader_fewest - spent:
        return None
    # THIS SIDE MAY CLAIM TOO MUCH, NEVER TOO LITTLE (review of landing
    # 3b.1, finding 1). The least-cost table spreads its cells over as
    # many parts as it can, so asking IT to fit the reader's most
    # different days refused tables a reader allows -- a smaller spread
    # fits where the cheapest does not -- and a class stage 3 could fill
    # was taken for residue both sides agreed on. What every table
    # holds is asked instead: a cell on each knot day, one more day for
    # a taken class between two knots, and the residue's occupied days,
    # all different days. The census side keeps the whole check: there a
    # refusal withholds.
    held = occupied
    for place in range(count):
        is_knot, day, _last = facts.stretches[place]
        if is_knot and (place, calendar_rules.weekday_of(day)) not in fixed:
            held = held + 1
    for key in take:
        if take[key] > 0 and least > 0 and not facts.stretches[key[0]][0]:
            held = held + 1
    if held > facts.reader_most:
        return None
    parts = _read(net, arcs)
    nonempty = len([part for part in parts if part[2] > 0])
    return _Table(parts=parts, nonempty=nonempty, cost=cost)


def _laid_out(
    facts: Facts, table: _Table, take: "dict[tuple[int, int], int]"
) -> "tuple[tuple[int, int], ...]":
    """The table laid out day by day, on the census side's count of days.

    Each non-empty part takes one day first, then the largest parts
    take more, one day each, until the count reaches the census side's
    least different days (never more than the parts can hold one cell a
    day). A part's cells are spread over its days as evenly as whole
    cells go, the larger shares first; a taken part is its class's
    first days and the rest its other days.
    """
    parts = table.parts
    room = 0
    for _key, _taken, cells, days in parts:
        room = room + min(cells, days)
    want = min(max(table.nonempty, facts.fewest), room)
    occupied = [1 if part[2] > 0 else 0 for part in parts]
    have = sum(occupied)
    order = sorted((-parts[index][2], index) for index in range(len(parts)))
    for _cells, index in order:
        if have >= want:
            break
        extra = min(min(parts[index][2], parts[index][3]) - occupied[index], want - have)
        if extra > 0:
            occupied[index] = occupied[index] + extra
            have = have + extra
    laid: "dict[int, int]" = {}
    for index in range(len(parts)):
        key, taken, cells, _days = parts[index]
        if cells <= 0:
            continue
        members = facts.classes[key]
        first = take[key] if key in take else 0
        chosen = members[:first] if taken else members[first:]
        spread = occupied[index]
        base, rest = divmod(cells, spread)
        for place in range(spread):
            laid[chosen[place]] = base + (1 if place < rest else 0)
    return tuple((day, laid[day]) for day in sorted(laid))


# -- the residue ---------------------------------------------------------------


def _acyclic(edges: "list[tuple[int, int]]") -> bool:
    """Whether these weekday precedences admit one order."""
    into = [0 for _ in range(calendar_rules.WEEKDAYS)]
    after: "list[list[int]]" = [[] for _ in range(calendar_rules.WEEKDAYS)]
    for first, second in edges:
        into[second] = into[second] + 1
        waiting = after[first]
        waiting += [second]
    ready = [weekday for weekday in range(calendar_rules.WEEKDAYS) if into[weekday] == 0]
    seen = 0
    index = 0
    while index < len(ready):
        weekday = ready[index]
        index = index + 1
        seen = seen + 1
        for other in after[weekday]:
            into[other] = into[other] - 1
            if into[other] == 0:
                ready += [other]
    return seen == calendar_rules.WEEKDAYS


def _orders(
    live: "list[int]", weekdays: "dict[int, tuple[int, ...]]"
) -> "list[tuple[int, ...]]":
    """Every choice of one weekday per live stretch some order of the week
    makes: each stretch's cells on the first of its weekdays in that
    order. A choice is made by an order exactly when the precedences it
    needs -- the chosen weekday before every other weekday of its
    stretch -- admit one."""
    choices: "list[tuple[int, ...]]" = [()]
    for place in live:
        grown: "list[tuple[int, ...]]" = []
        for choice in choices:
            for weekday in weekdays[place]:
                grown += [choice + (weekday,)]
        choices = grown
    kept: "list[tuple[int, ...]]" = []
    for choice in choices:
        edges: "list[tuple[int, int]]" = []
        for position in range(len(live)):
            for other in weekdays[live[position]]:
                if other != choice[position]:
                    edges += [(choice[position], other)]
        if _acyclic(edges):
            kept += [choice]
    return kept


def _choices_count(
    live: "list[int]", weekdays: "dict[int, tuple[int, ...]]"
) -> int:
    total = 1
    for place in live:
        total = total * len(weekdays[place])
    return total


def _compositions(total: int, parts: int) -> int:
    """How many ways `0 .. total` cells split over `parts` classes."""
    ways = 1
    for step in range(1, parts + 1):
        ways = ways * (total + step) // step
    return ways


def _residue_equivalent(
    facts: Facts,
    residue: "list[tuple[int, int]]",
    tally: "list[int]",
    alternatives: "list[tuple[dict[int, tuple[int, int]], tuple[tuple[int, int], ...] | None]] | None" = None,
    known: "_Known | None" = None,
) -> "tuple[bool, str, str]":
    """Every residue configuration stage 3 allows, the census allows too.

    A CONFIGURATION is each residue class's cells and the residue's
    occupied days. The census's network sees one only through its
    stretch totals `t`, its weekday totals and its occupied days. Where
    the count of different days cannot bind -- every other class one
    part and the residue's most occupied days together within the
    census's most different days -- the census-realisable weekday totals
    at fixed `(t, occupied days)` are a convex set and the residue's own
    form a base polytope, so its VERTICES decide: each residue
    stretch's cells on one of its weekdays, one vertex per order of the
    week. Both readings are monotone in the occupied days there, so the
    least occupied days stage 3 allows is the one asked; for entry 2 or
    3 one alternative of the menu must realise every vertex of a slice.
    Where the count could bind, every configuration is enumerated, up
    to `CONFIGURATION_CAP`; more withholds, and so do more slices.

    `alternatives` are what the side asked tells a reader, each weekday
    bounds and group-total bounds (`_census_table`); by default the
    census's own, one per `calendar_rules.branches_of`; `known` what a
    withholding's band search has learnt (`_Known`). Returns whether it
    holds, the mode (`vertices` or `full`) and what decided it.
    """
    by_stretch: "dict[int, list[tuple[int, int]]]" = {}
    for key in residue:
        if key[0] in by_stretch:
            listed = by_stretch[key[0]]
            listed += [key]
        else:
            by_stretch[key[0]] = [key]
    stretches = sorted(by_stretch)
    for place in stretches:
        if facts.most[place] >= facts.line:
            return False, "", "a residue stretch the rank facts do not cap below the line"
    days_in: "dict[int, int]" = {}
    weekdays: "dict[int, tuple[int, ...]]" = {}
    for place in stretches:
        days_in[place] = sum(len(facts.classes[key]) for key in by_stretch[place])
        weekdays[place] = tuple(key[1] for key in by_stretch[place])
    residue_set = set(residue)
    rest_parts = len(
        [key for key in facts.keys if key[1] not in facts.zero and key not in residue_set]
    )
    occupied_most = sum(min(facts.most[place], days_in[place]) for place in stretches)
    branches: "list[tuple[dict[int, tuple[int, int]], tuple[tuple[int, int], ...] | None]]" = []
    if alternatives is None:
        for bounds in calendar_rules.branches_of(
            facts.groups, facts.line, facts.shortable, -1
        ):
            branches += [(bounds, None)]
    else:
        branches = alternatives
    zeros = {key: 0 for key in residue}
    if rest_parts + occupied_most > facts.most_days:
        return _residue_full(facts, by_stretch, stretches, branches, zeros, tally, known)
    slices = 1
    for place in stretches:
        least = 1 if facts.stretches[place][0] else 0
        slices = slices * (facts.most[place] - least + 1)
    if slices > CONFIGURATION_CAP:
        return False, "vertices", "too many residue slices"
    remembered: "dict[tuple[int, ...], list[tuple[int, ...]]]" = {}
    totals = [1 if facts.stretches[place][0] else 0 for place in stretches]
    while True:
        positions = [index for index in range(len(stretches)) if totals[index] > 0]
        live = [stretches[index] for index in positions]
        signature = tuple(live)
        if signature not in remembered:
            if _choices_count(live, weekdays) > CONFIGURATION_CAP:
                return False, "vertices", "too many residue vertices"
            remembered[signature] = _orders(live, weekdays)
        vertices: "list[dict[tuple[int, int], int]]" = []
        for choice in remembered[signature]:
            config = dict(zeros)
            for position in range(len(live)):
                config[(live[position], choice[position])] = totals[positions[position]]
            vertices += [config]
        cells = sum(totals)
        least_days = len(live)
        most_days = 0
        for index in range(len(stretches)):
            most_days = most_days + min(totals[index], days_in[stretches[index]])
        first, beyond = least_days, most_days + 1
        while first < beyond:
            middle = (first + beyond) // 2
            if _stage3_found(facts, {}, 0, 0, vertices[0], cells - middle, middle, tally, known):
                beyond = middle
            else:
                first = middle + 1
        if first <= most_days:
            spent = cells - first
            realised = any(
                all(
                    _census_known(facts, {}, {}, bounds, config, spent, first, top_bounds, known)
                    for config in vertices
                )
                for bounds, top_bounds in branches
            )
            for bounds, top_bounds in branches:
                if realised:
                    break
                every = True
                for config in vertices:
                    if not _census_found(
                        facts, {}, {}, bounds, config, spent, first, tally,
                        top_bounds, known,
                    ):
                        every = False
                        break
                if every:
                    realised = True
                    break
            if not realised:
                return (
                    False,
                    "vertices",
                    "a residue configuration stage 3 allows the census does not",
                )
        index = 0
        while index < len(stretches):
            if totals[index] < facts.most[stretches[index]]:
                totals[index] = totals[index] + 1
                break
            totals[index] = 1 if facts.stretches[stretches[index]][0] else 0
            index = index + 1
        if index == len(stretches):
            break
    return True, "vertices", ""


def _residue_full(
    facts: Facts,
    by_stretch: "dict[int, list[tuple[int, int]]]",
    stretches: "list[int]",
    branches: "list[tuple[dict[int, tuple[int, int]], tuple[tuple[int, int], ...] | None]]",
    zeros: "dict[tuple[int, int], int]",
    tally: "list[int]",
    known: "_Known | None" = None,
) -> "tuple[bool, str, str]":
    """Every residue configuration, enumerated (`_residue_equivalent`)."""
    total = 1
    for place in stretches:
        total = total * _compositions(facts.most[place], len(by_stretch[place]))
        if total > CONFIGURATION_CAP:
            return False, "full", "too many residue configurations"
    options: "list[list[dict[tuple[int, int], int]]]" = []
    for place in stretches:
        keys = by_stretch[place]
        found: "list[dict[tuple[int, int], int]]" = [{}]
        for position in range(len(keys)):
            grown: "list[dict[tuple[int, int], int]]" = []
            for partial in found:
                used = sum(partial[key] for key in partial)
                for cells in range(facts.most[place] - used + 1):
                    extended = dict(partial)
                    extended[keys[position]] = cells
                    grown += [extended]
            found = grown
        options += [found]
    pointer = [0 for _ in stretches]
    while True:
        config = dict(zeros)
        for index in range(len(stretches)):
            chosen = options[index][pointer[index]]
            for key in chosen:
                config[key] = chosen[key]
        cells = sum(config[key] for key in config)
        least_days = len([key for key in config if config[key] > 0])
        most_days = sum(min(config[key], len(facts.classes[key])) for key in config)
        for occupied in range(least_days, most_days + 1):
            spent = cells - occupied
            if not _stage3_found(facts, {}, 0, 0, config, spent, occupied, tally, known):
                continue
            realised = any(
                _census_known(facts, {}, {}, bounds, config, spent, occupied, top_bounds, known)
                for bounds, top_bounds in branches
            )
            for bounds, top_bounds in branches:
                if realised:
                    break
                realised = _census_found(
                    facts, {}, {}, bounds, config, spent, occupied, tally,
                    top_bounds, known,
                )
            if not realised:
                return (
                    False,
                    "full",
                    "a residue configuration stage 3 allows the census does not",
                )
        index = 0
        while index < len(stretches):
            if pointer[index] + 1 < len(options[index]):
                pointer[index] = pointer[index] + 1
                break
            pointer[index] = 0
            index = index + 1
        if index == len(stretches):
            break
    return True, "full", ""


# -- the certificate -------------------------------------------------------------


def certify(facts: Facts) -> Verdict:
    """The full-fill certificate of one census (module docstring).

    Guarantees: accepts the facts; returns the verdict, its witnesses
    and its residue. Determinism: a function of the facts -- classes are
    asked in (stretch, weekday) order and the alternatives of the menu
    in weekday order. Raises nothing. No I/O of any kind.
    """
    tally = [0]
    line = facts.line
    if ties_refused(facts.body, facts.reader_fewest, line):
        return Verdict(
            False, calendar_rules.REASON_TIES,
            "no day can hold the line: too few repeated cells",
            (), (), 0, "",
        )
    witnesses: "list[Witness]" = []
    residue: "list[tuple[int, int]]" = []
    for key in facts.keys:
        weekday = key[1]
        if weekday in facts.zero:
            continue
        take = {key: 1}
        need = {weekday: (line, facts.body)}
        found: "_Table | None" = None
        for bounds in calendar_rules.branches_of(
            facts.groups, line, facts.shortable, weekday
        ):
            found = _census_table(facts, take, need, bounds, {}, 0, 0, tally)
            if found is not None:
                break
        if found is not None:
            witnesses += [
                Witness(key, facts.classes[key][0], _laid_out(facts, found, take))
            ]
            continue
        if _stage3_table(facts, take, line, facts.body, {}, 0, 0, tally) is not None:
            return Verdict(
                False, calendar_rules.REASON_NARROWED,
                "the census keeps a day below the line where stage 3 does not",
                tuple(witnesses), tuple(residue), tally[0], "",
            )
        residue += [key]
    mode = ""
    if residue:
        held, mode, detail = _residue_equivalent(facts, residue, tally)
        if not held:
            return Verdict(
                False, calendar_rules.REASON_NARROWED, detail,
                tuple(witnesses), tuple(residue), tally[0], mode,
            )
    return Verdict(True, "", "", tuple(witnesses), tuple(residue), tally[0], mode)


# -- the withholding's own certificate ------------------------------------------------
#
# THE FIRING OF A WITHHOLDING IS A PUBLICATION TOO (review of landing
# 3b.1, item 2). A reader who is told a census is withheld knows that the
# table is one whose census the rules withhold, and where that set confines
# some set of days to one to the line less one, the sentence has said what
# a census may not: 1,040 business-day rows beside ONE Saturday row were
# withheld because no grouping met the line, which told a reader holding
# the count of different days that the weekend held one to ten rows, where
# thirteen published the seven counts. So every withholding the table's own
# numbers decide is said in ONE sentence, and that sentence is published
# only where its set is certified the way a census is: its sure part W0 --
# the tables whose weekend, or whose Monday to Friday together, lies in its
# BAND, which the producer always withholds -- has a witness putting the
# line on a day of every class, or the class is residue whose every
# stage-3 configuration W0 allows. Every table withheld is then in a set
# holding W0, and a set holding a certified set confines nothing either.
# ANY CERTIFIED W0 WILL DO, so EACH HALF'S BAND IS SEARCHED ON ITS OWN
# (the review's second round and its skeptic's): the weekend band runs
# from the larger of one and the least any table of stage 3's facts puts
# there through that and `a` rows more, Monday to Friday's likewise with
# `b`, and the pair taken is the certified one of least `a + b`, the one
# with fewer Monday-to-Friday rows where two tie. Each width stops at the
# census line and what the capped stretches can take past the least, where
# the band always reached. One width for both halves past the capped
# stretches cost real censuses: a weekend market beside thirty Wednesday
# rows stood inside a Monday-to-Friday band the capped stretches alone
# stretched seventeen rows past its least, and publishes now. The search
# walks the pairs as though a wider band never certified less, a reading
# that saves networks and can at worst miss a narrower pair, never take an
# uncertified one: every pair it takes is asked in full. Where
# the widest pair does not certify, the one width is asked as before
# (`_narrowed`), and where that does not either, the census is withheld
# whatever the table, which the published numbers alone decide and so
# says nothing. W0's CLASSES ARE COARSER than a
# census's: what W0 asks of a table is its rank facts, its count of
# different days and its two half totals, so exchanging two days of one
# stretch between two knots and one half of the week changes nothing W0
# asks (`_pooled`).


@dataclasses.dataclass(frozen=True)
class Withholding:
    """Whether withholding a census on the table's own numbers is certified.

    `holds` says whether it is; `detail` what decided it where it is not,
    for a test to read; `weekend` and `weekdays` are the two BANDS, each
    `(least, most)` of that total that the producer always withholds, and
    `(1, 0)` where no table meeting stage 3's facts reaches one; `solves`
    how many networks were solved.
    """

    holds: bool
    detail: str
    weekend: "tuple[int, int]"
    weekdays: "tuple[int, int]"
    solves: int


# The two totals every entry of the menu publishes: Monday to Friday, and
# Saturday with Sunday.
_HALVES = ((0, calendar_rules.FRIDAY, 0), (calendar_rules.SATURDAY, calendar_rules.SUNDAY, 0))


def _halves_facts(facts: Facts) -> Facts:
    """The facts asked with the two halves of the week as the only groups.

    No weekday is empty and every weekday holding a class can be the
    short one, because the halves say neither.
    """
    return dataclasses.replace(
        facts,
        groups=_HALVES,
        where=calendar_rules.where_of(_HALVES),
        zero=frozenset(),
        shortable=tuple(sorted({key[1] for key in facts.classes})),
        entry=calendar_rules.ENTRY_WEEKDAYS,
    )


def _pooled(facts: Facts) -> Facts:
    """The halves' facts with each stretch between two knots one class a half.

    THE WITHHOLDING'S CLASSES (review of the third review's repair). W0
    tells two days apart only by what it asks of a table -- its rank
    facts, its count of different days, and its weekend and Monday to
    Friday totals -- so every day of one stretch between two knots in one
    half of the week is exchangeable with every other, holes left out as
    before. Asked a class per weekday, a stretch of a column of few
    dates had up to seven residue classes where two stand, and 6 of 120
    seeded schedules were withheld whatever they held, their residue
    having more arrangements than `CONFIGURATION_CAP`. A knot day stays
    its own class. The class's weekday is Monday or Saturday, the one
    each half's network reads.
    """
    grown: "dict[tuple[int, int], list[int]]" = {}
    for key in facts.keys:
        place, weekday = key
        if not facts.stretches[place][0]:
            weekday = 0 if weekday < calendar_rules.SATURDAY else calendar_rules.SATURDAY
        if (place, weekday) in grown:
            members = grown[(place, weekday)]
            members += list(facts.classes[key])
        else:
            grown[(place, weekday)] = list(facts.classes[key])
    classes = {key: tuple(sorted(grown[key])) for key in grown}
    return dataclasses.replace(
        facts,
        classes=classes,
        keys=tuple(sorted(classes)),
        shortable=tuple(sorted({key[1] for key in classes})),
    )


def _least_half(facts: Facts, weekend: bool, tally: "list[int]") -> int:
    """The least cells one half of the week holds over the tables of `facts`, or -1.

    Asked on the census side's network (every table it finds is a
    table), by halving the most the half may hold.
    """
    body = facts.body

    def fits(most: int) -> bool:
        bounds = ((body - most, body), (0, most)) if weekend else ((0, most), (body - most, body))
        return _census_table(facts, {}, {}, {}, {}, 0, 0, tally, bounds) is not None

    if not fits(body):
        return -1
    first, last = 0, body
    while first < last:
        middle = (first + last) // 2
        if fits(middle):
            last = middle
        else:
            first = middle + 1
    return first


def _band(least: int, line: int, capped: int) -> "tuple[int, int]":
    """The WIDEST band: at least one row, and at most the line and what the
    capped stretches can put in this half beyond the least the half can
    hold."""
    if least < 0:
        return (1, 0)
    return (max(1, least), least + line + capped)


def _narrowed(banded: "Bands", width: int, solves: int) -> "Bands":
    """The bands of ONE width for both halves: `width` rows past the larger
    of one and each half's least and what its capped stretches can take,
    never past the widest band. Asked only where no pair of `_at_widths`
    certifies (`withholding`)."""
    halves: "list[tuple[int, int]]" = []
    for band, capped in ((banded.weekend, banded.capped[0]), (banded.weekdays, banded.capped[1])):
        if band[0] > band[1]:
            halves += [band]
        else:
            halves += [(band[0], min(band[0] + capped + width, band[1]))]
    return dataclasses.replace(banded, weekend=halves[0], weekdays=halves[1], solves=solves)


def _at_widths(banded: "Bands", weekend: int, weekdays: int, solves: int) -> "Bands":
    """The weekend band `weekend` rows past the larger of one and its least,
    and Monday to Friday's `weekdays` rows past theirs, never past the
    widest band; a band no table reaches stays empty."""
    halves: "list[tuple[int, int]]" = []
    for band, width in ((banded.weekend, weekend), (banded.weekdays, weekdays)):
        if band[0] > band[1]:
            halves += [band]
        else:
            halves += [(band[0], min(band[0] + width, band[1]))]
    return dataclasses.replace(banded, weekend=halves[0], weekdays=halves[1], solves=solves)


def _reach(banded: "Bands") -> "tuple[int, int]":
    """How many rows past its least each half's widest band reaches."""
    return (
        max(0, banded.weekend[1] - banded.weekend[0]),
        max(0, banded.weekdays[1] - banded.weekdays[0]),
    )


@dataclasses.dataclass(frozen=True)
class _Known:
    """What one withholding's band search has learnt, asked again at every
    pair of widths it tries (`withholding`).

    `stage3` holds whether each stage-3 network asked found a table: its
    question holds no band, so its answer is the same at every pair.
    `weekends` holds, per question the census side asked less its two half
    totals, the weekend total of every table it found: a table found under
    one band IS a table under any band holding its totals, so it is taken
    again there without a network, and nothing stands for a table no
    network found. `refused` holds each census-side question, its two half
    totals included, whose network found none: asked again whole, it
    would find none again. All three grow as the search asks.
    """

    stage3: "dict[tuple[object, ...], bool]"
    weekends: "dict[tuple[object, ...], list[int]]"
    refused: "dict[tuple[object, ...], bool]"


def _stage3_found(
    facts: Facts,
    take: "dict[tuple[int, int], int]",
    least: int,
    greatest: int,
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
    tally: "list[int]",
    known: "_Known | None",
) -> bool:
    """Whether `_stage3_table` finds a table, each question asked once
    where the band search keeps what it learnt."""
    if known is None:
        return _stage3_table(facts, take, least, greatest, fixed, spent, occupied, tally) is not None
    question: "tuple[object, ...]" = (
        tuple(sorted((key, take[key]) for key in take)),
        least,
        greatest,
        tuple(sorted((key, fixed[key]) for key in fixed)),
        spent,
        occupied,
    )
    if question not in known.stage3:
        known.stage3[question] = (
            _stage3_table(facts, take, least, greatest, fixed, spent, occupied, tally) is not None
        )
    return known.stage3[question]


def _question(
    take: "dict[tuple[int, int], int]",
    need: "dict[int, tuple[int, int]]",
    bounds: "dict[int, tuple[int, int]]",
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
) -> "tuple[object, ...]":
    """A census-side question less its two half totals, as `_Known` keeps it."""
    return (
        tuple(sorted((key, take[key]) for key in take)),
        tuple(sorted((key, need[key]) for key in need)),
        tuple(sorted((key, bounds[key]) for key in bounds)),
        tuple(sorted((key, fixed[key]) for key in fixed)),
        spent,
        occupied,
    )


def _census_known(
    facts: Facts,
    take: "dict[tuple[int, int], int]",
    need: "dict[int, tuple[int, int]]",
    bounds: "dict[int, tuple[int, int]]",
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
    top_bounds: "tuple[tuple[int, int], ...] | None",
    known: "_Known | None",
) -> bool:
    """Whether a table the band search already found answers this question
    with these two half totals (`_Known`); asks no network."""
    if known is None or top_bounds is None:
        return False
    question = _question(take, need, bounds, fixed, spent, occupied)
    if question not in known.weekends:
        return False
    weekdays, weekend = top_bounds[0], top_bounds[1]
    for total in known.weekends[question]:
        if weekend[0] <= total <= weekend[1] and weekdays[0] <= facts.body - total <= weekdays[1]:
            return True
    return False


def _census_found(
    facts: Facts,
    take: "dict[tuple[int, int], int]",
    need: "dict[int, tuple[int, int]]",
    bounds: "dict[int, tuple[int, int]]",
    fixed: "dict[tuple[int, int], int]",
    spent: int,
    occupied: int,
    tally: "list[int]",
    top_bounds: "tuple[tuple[int, int], ...] | None",
    known: "_Known | None",
) -> bool:
    """Whether `_census_table` finds a table; asked with the two half totals
    of the withholding's alternatives where the band search keeps what it
    learnt, a table found before whose totals lie inside these is taken
    again without a network."""
    if known is None or top_bounds is None:
        return (
            _census_table(facts, take, need, bounds, fixed, spent, occupied, tally, top_bounds)
            is not None
        )
    if _census_known(facts, take, need, bounds, fixed, spent, occupied, top_bounds, known):
        return True
    question = _question(take, need, bounds, fixed, spent, occupied)
    earlier = known.weekends[question] if question in known.weekends else []
    whole = (question, tuple(top_bounds))
    if whole in known.refused:
        return False
    table = _census_table(facts, take, need, bounds, fixed, spent, occupied, tally, top_bounds)
    if table is None:
        known.refused[whole] = True
        return False
    total = sum(part[2] for part in table.parts if part[0][1] >= calendar_rules.SATURDAY)
    total = total + sum(fixed[key] for key in fixed if key[1] >= calendar_rules.SATURDAY)
    earlier += [total]
    known.weekends[question] = earlier
    return True


def _capped_cells(facts: Facts, weekend: bool) -> int:
    """The most cells one half of the week can take in the stretches the
    rank facts cap below the line -- the stretches whose classes can only
    ever be residue. The band reaches that far past the least and the
    line, so every arrangement of the residue stage 3 allows fits a table
    of the band (measured: 400 admissions whose four capped stretches by
    the boundaries hold fifteen weekend days' worth of cells had their
    withholding uncertified with a band of the line alone)."""
    total = 0
    for place in range(len(facts.stretches)):
        if facts.most[place] >= facts.line:
            continue
        for weekday in range(calendar_rules.WEEKDAYS):
            if (weekday >= calendar_rules.SATURDAY) != weekend:
                continue
            if (place, weekday) in facts.classes:
                total = total + facts.most[place]
                break
    return total


def withholding(
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
    reader_fewest: int,
    reader_most: int,
    line: int,
    holes: "tuple[int, ...]" = (),
) -> Withholding:
    """The withholding's certificate, from the published numbers alone.

    The BANDS: the least cells the weekend, and the least Monday to
    Friday together, hold over the tables meeting stage 3's facts on the
    reader's bounds and the holes (`bands`); the weekend band runs from
    the larger of one and its least through that and `a` rows more,
    Monday to Friday's with `b` rows more (`_at_widths`), each at most
    the line plus what the capped stretches can take in that half, the
    widest. The pair taken is the certified one of least `a + b` that a
    walk reading a wider band as never certifying less finds, the smaller
    `b` where two tie (`_least_pair`). Where the widest pair is
    not certified, one width for both halves past the capped stretches
    (`_narrowed`, nought) is asked, and where that is not either, the
    widest's answer stands. W0 is the tables whose
    weekend lies in its band or whose weekdays lie in theirs: every class
    -- a knot day, or the days of one stretch between two knots in one
    half of the week (`_pooled`) -- needs a witness in W0 putting the
    line on one of its days, or no table of stage 3's facts may put the
    line there (else W0, and with it the withholding, narrows the
    class) and the class is residue, whose every stage-3 configuration
    W0 allows (`_residue_equivalent` with W0's two alternatives).

    CACHED ON THE WHOLE QUESTION, as `check` is. Guarantees: accepts the
    description's numbers; returns the answer. Determinism: a function
    of the arguments. Raises nothing. No I/O of any kind.
    """
    key: "tuple[object, ...]" = (
        "withholding", parsed, rows_low, rows_high, low, high,
        tuple(sorted(rungs)), reader_fewest, reader_most, line,
        tuple(sorted(set(holes))),
    )
    if key in _WITHHOLDINGS:
        return _WITHHOLDINGS[key]
    banded = bands(
        parsed, rows_low, rows_high, low, high, rungs, reader_fewest,
        reader_most, line, holes,
    )
    given = facts_of(
        parsed, rows_low, rows_high, low, high, rungs, reader_fewest,
        reader_most, line, _HALVES, -1, holes,
    )
    known = _Known({}, {}, {})
    reach = _reach(banded)
    answer = _withheld_certified(given, _at_widths(banded, 0, 0, banded.solves), known)
    if not answer.holds and reach != (0, 0):
        if reach[1] > 0:
            answer = _withheld_certified(given, _at_widths(banded, 0, reach[1], answer.solves), known)
        if answer.holds:
            answer = _least_pair(given, banded, known, answer, (0, reach[1]))
        elif reach[0] > 0:
            answer = _withheld_certified(given, _at_widths(banded, reach[0], reach[1], answer.solves), known)
            if answer.holds:
                answer = _least_pair(given, banded, known, answer, reach)
        if not answer.holds:
            common = _withheld_certified(given, _narrowed(banded, 0, answer.solves), known)
            answer = common if common.holds else dataclasses.replace(answer, solves=common.solves)
    if len(_WITHHOLDINGS) >= _ANSWERS_KEPT:
        for earlier in list(_WITHHOLDINGS):
            del _WITHHOLDINGS[earlier]
    _WITHHOLDINGS[key] = answer
    return answer


def _least_pair(
    given: Facts, banded: "Bands", known: _Known, held: Withholding, best: "tuple[int, int]"
) -> Withholding:
    """The certified pair of widths of least sum, the fewer Monday-to-Friday
    rows first where two tie (`withholding`). `held` is the answer at the
    pair `best`, which holds: the widest Monday-to-Friday width beside a
    weekend width of nought, or the widest pair where that one does not
    hold; the pair of noughts was asked and does not hold.

    Weekend widths are walked up from nought, each asked at the most
    Monday-to-Friday width that could still match the best sum, and where
    that holds, the least such width is found by asking a quarter of the
    way up what is left -- a refused pair costs a few networks, a held one
    every question again -- a walk that reads a wider band as never
    certifying less. Every pair it keeps held when asked. `solves` counts
    every network the search spent.
    """
    reach = _reach(banded)
    chosen = held
    spent = held.solves
    for weekend in range(reach[0] + 1):
        top = min(reach[1], best[0] + best[1] - weekend)
        if top < 0:
            break
        if (weekend, top) == (0, 0) or (weekend == 0 and best[0] > 0):
            continue
        tried = held
        if (weekend, top) != best:
            tried = _withheld_certified(given, _at_widths(banded, weekend, top, spent), known)
            spent = tried.solves
        if not tried.holds:
            continue
        first, last, found = (1 if weekend == 0 else 0), top, tried
        while first < last:
            middle = first + (last - first) // 4
            tried = _withheld_certified(given, _at_widths(banded, weekend, middle, spent), known)
            spent = tried.solves
            if tried.holds:
                last, found = middle, tried
            else:
                first = middle + 1
        best, chosen = (weekend, last), found
    return dataclasses.replace(chosen, solves=spent)


_WITHHOLDINGS: "dict[tuple[object, ...], Withholding]" = {}
_BANDS: "dict[tuple[object, ...], Bands]" = {}


@dataclasses.dataclass(frozen=True)
class Bands:
    """Two BANDS: weekend and Monday to Friday totals, each `(least, most)`.

    `(1, 0)` where no table meeting stage 3's facts is found; `solves`
    how many networks were solved; `capped` what the capped stretches can
    take in the weekend and in Monday to Friday (`_capped_cells`).
    """

    weekend: "tuple[int, int]"
    weekdays: "tuple[int, int]"
    solves: int
    capped: "tuple[int, int]" = (0, 0)


def bands(
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
    reader_fewest: int,
    reader_most: int,
    line: int,
    holes: "tuple[int, ...]" = (),
) -> Bands:
    """The two WIDEST bands, from the published numbers alone (`withholding`).

    The least cells the weekend, and Monday to Friday together, hold
    over the tables meeting stage 3's facts on the reader's bounds and
    the holes, asked on the census side's network so every table found
    is a table; each band runs from the larger of one and that least to
    the least plus the line plus the most that half can take in the
    stretches the rank facts cap below the line (`_capped_cells`), which
    it carries. `withholding` narrows each to the widths of the certified
    pair it takes, and the loader (WC9) each to its least alone. CACHED ON
    THE WHOLE QUESTION.

    Guarantees: accepts the description's numbers; returns the bands.
    Determinism: a function of the arguments. Raises nothing. No I/O.
    """
    key: "tuple[object, ...]" = (
        "bands", parsed, rows_low, rows_high, low, high,
        tuple(sorted(rungs)), reader_fewest, reader_most, line,
        tuple(sorted(set(holes))),
    )
    if key in _BANDS:
        return _BANDS[key]
    tally = [0]
    facts = _halves_facts(
        facts_of(
            parsed, rows_low, rows_high, low, high, rungs, reader_fewest,
            reader_most, line, _HALVES, -1, holes,
        )
    )
    capped = (_capped_cells(facts, True), _capped_cells(facts, False))
    answer = Bands(
        _band(_least_half(facts, True, tally), line, capped[0]),
        _band(_least_half(facts, False, tally), line, capped[1]),
        tally[0],
        capped,
    )
    if len(_BANDS) >= _ANSWERS_KEPT:
        for known in list(_BANDS):
            del _BANDS[known]
    _BANDS[key] = answer
    return answer


def _withheld_certified(given: Facts, banded: Bands, known: "_Known | None" = None) -> Withholding:
    """W0 of these bands certified (`withholding`), what the band search
    learnt kept in `known` where it is given; `solves` counts on from
    `banded.solves`."""
    tally = [banded.solves]
    facts = _pooled(_halves_facts(given))
    line = facts.line
    body = facts.body
    weekend = banded.weekend
    weekdays = banded.weekdays
    alternatives: "list[tuple[dict[int, tuple[int, int]], tuple[tuple[int, int], ...] | None]]" = []
    if weekend[0] <= weekend[1]:
        alternatives += [({}, ((body - weekend[1], body - weekend[0]), weekend))]
    if weekdays[0] <= weekdays[1]:
        alternatives += [({}, (weekdays, (body - weekdays[1], body - weekdays[0])))]
    residue: "list[tuple[int, int]]" = []
    for klass in facts.keys:
        weekday = klass[1]
        take = {klass: 1}
        need = {weekday: (line, body)}
        found = any(
            _census_known(facts, take, need, bounds, {}, 0, 0, top_bounds, known)
            for bounds, top_bounds in alternatives
        )
        for bounds, top_bounds in alternatives:
            if found:
                break
            found = _census_found(facts, take, need, bounds, {}, 0, 0, tally, top_bounds, known)
        if found:
            continue
        if _stage3_found(facts, take, line, body, {}, 0, 0, tally, known):
            return Withholding(
                False, "the withheld tables keep a day below the line where stage 3 does not",
                weekend, weekdays, tally[0],
            )
        residue += [klass]
    if residue:
        held, _mode, detail = _residue_equivalent(facts, residue, tally, alternatives, known)
        if not held:
            return Withholding(False, detail, weekend, weekdays, tally[0])
    return Withholding(True, "", weekend, weekdays, tally[0])


def in_band(
    groups: "tuple[tuple[int, int, int], ...]", withheld: "Withholding | Bands"
) -> bool:
    """Whether a census's weekend, or its Monday to Friday, lies in its band.

    Every entry of the menu publishes both totals: a group of nought
    counts nought, and every non-zero group lies inside one half.

    Guarantees: accepts a menu grouping and the bands (or the
    withholding's answer, which carries them); returns the answer. Determinism: a function of the two. Raises
    nothing. No I/O of any kind.
    """
    weekend = 0
    weekdays = 0
    for first, last, count in groups:
        if count == 0:
            continue
        if first >= calendar_rules.SATURDAY:
            weekend = weekend + count
        else:
            weekdays = weekdays + count
    return (
        withheld.weekend[0] <= weekend <= withheld.weekend[1]
        or withheld.weekdays[0] <= weekdays <= withheld.weekdays[1]
    )


def check(
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
    reader_fewest: int,
    reader_most: int,
    line: int,
    groups: "tuple[tuple[int, int, int], ...]",
    real_days: int = -1,
    holes: "tuple[int, ...]" = (),
) -> Verdict:
    """WC7 and WC8 of one weekday census, from the description's numbers.

    Asked by the producer (with the body's real count of different days
    and every hole) and by the loader (with `real_days` -1, so the
    reader's bounds stand on both sides, and the holes the form censuses
    and the placeholder decisions show). The groups must already be a
    menu grouping whose counts add to the body. The refusals a handful
    of published numbers decide come first and walk no day
    (`_refused`: a grouping of no menu entry, and too few repeated
    cells for any day to hold the line); then WC7 -- a group a reader
    can hold to fewer than four dates besides the knot days and the
    holes withholds (reason `few_dates`); then the certificate.

    CACHED ON THE WHOLE QUESTION: the producer, its self-check, the
    generator's loader and the validator's loader ask the same
    questions of one description, and each answer is a function of the
    arguments alone.

    Guarantees: accepts the numbers; returns the verdict. Determinism: a
    function of the arguments. Raises nothing. No I/O of any kind.
    """
    key: "tuple[object, ...]" = (
        parsed, rows_low, rows_high, low, high, tuple(sorted(rungs)),
        reader_fewest, reader_most, line, tuple(groups), real_days,
        tuple(sorted(set(holes))),
    )
    if key in _ANSWERS:
        return _ANSWERS[key]
    verdict = _refused(parsed - rows_low - rows_high, reader_fewest, line, groups)
    if verdict is None:
        facts = facts_of(
            parsed, rows_low, rows_high, low, high, rungs, reader_fewest,
            reader_most, line, groups, real_days, holes,
        )
        verdict = _decided(facts)
    if len(_ANSWERS) >= _ANSWERS_KEPT:
        for known in list(_ANSWERS):
            del _ANSWERS[known]
    _ANSWERS[key] = verdict
    return verdict


def _refused(
    body: int,
    reader_fewest: int,
    line: int,
    groups: "tuple[tuple[int, int, int], ...]",
) -> "Verdict | None":
    """The refusals the published numbers decide before any day is walked.

    A grouping no entry of the menu is, and a body whose repeated cells
    cannot put the line on any day (`ties_refused`), are decided from a
    handful of numbers; asking them first keeps a column spread over
    thousands of years from enumerating its span only to be refused
    (review of landing 3b.1, finding 10). None where neither refuses.
    """
    if calendar_rules.entry_of(groups) == calendar_rules.ENTRY_NONE:
        return Verdict(
            False, calendar_rules.REASON_MENU, "not a grouping of the menu",
            (), (), 0, "",
        )
    if ties_refused(body, reader_fewest, line):
        return Verdict(
            False, calendar_rules.REASON_TIES,
            "no day can hold the line: too few repeated cells",
            (), (), 0, "",
        )
    return None


def ties_refused(body: int, reader_fewest: int, line: int) -> bool:
    """Whether no day of the body can hold the line in any table a reader allows.

    A day holding the line needs `line - 1` cells beyond the one each
    occupied day holds, and a reader's tables hold at most
    `body - reader_fewest` such cells. A function of three published
    numbers: it walks no day.

    Guarantees: accepts the body, the reader's least different days and
    the line; returns the answer. Determinism: a function of the three.
    Raises nothing. No I/O of any kind.
    """
    return body - reader_fewest < line - 1


def _decided(facts: Facts) -> Verdict:
    if facts.entry == calendar_rules.ENTRY_NONE:
        return Verdict(
            False, calendar_rules.REASON_MENU, "not a grouping of the menu",
            (), (), 0, "",
        )
    short = calendar_rules.few_dates_group(
        facts.groups, facts.low, facts.high, facts.knot_days, facts.reader_most,
        facts.holes,
    )
    if short >= 0:
        return Verdict(
            False, calendar_rules.REASON_FEW_DATES,
            "a group holds a few single dates", (), (), 0, "",
        )
    return certify(facts)


# -- what the loader asks -----------------------------------------------------------


def reader_days(
    n_distinct: int,
    unparsed: int,
    low_rows: int,
    low_listed: int,
    high_rows: int,
    high_listed: int,
) -> "tuple[int, int]":
    """The reader's least and most different days of the body, `[D_min, D_max]`.

    `n_distinct` counts the column's different TEXTS; with one spelling
    per day (WC6) a parsed text is a day. The body holds at least what
    is left once every unparsed cell and each tail's most different
    values -- its listed values, or one per row -- are taken away, and
    at most what is left once one unparsed text (where any) and each
    tail's least -- its listed values, or one -- are. `low_listed` and
    `high_listed` are -1 where a tail lists no values.

    Guarantees: accepts the six published numbers; returns the two
    bounds. Determinism: a function of the six. Raises nothing. No I/O.
    """
    low_most = low_listed if low_listed >= 0 else low_rows
    high_most = high_listed if high_listed >= 0 else high_rows
    low_least = low_listed if low_listed >= 0 else (1 if low_rows > 0 else 0)
    high_least = high_listed if high_listed >= 0 else (1 if high_rows > 0 else 0)
    fewest = n_distinct - unparsed - low_most - high_most
    most = n_distinct - (1 if unparsed > 0 else 0) - low_least - high_least
    return fewest, most


def breach(
    groups: "tuple[tuple[int, int, int], ...]",
    parsed: int,
    rows_low: int,
    rows_high: int,
    low: int,
    high: int,
    rungs: "tuple[tuple[int, int], ...]",
    fewest: int,
    most: int,
    line: int,
    one_spelling: bool,
    holes: "tuple[int, ...]" = (),
) -> "tuple[str, str, str] | None":
    """The loader's check of one published weekday census, or None.

    WC1 the groups cover Monday to Sunday in order, each weekday once;
    WC2 every count is nought or at least the line; WC3 the counts add
    to the body; WC4 the grouping is an entry of the menu; WC6 the
    published forms give every date one text; WC5 no group is left one
    to the line less one once the knot days' sure cells are taken out;
    then WC9, no weekend and no Monday to Friday at its least alone --
    the larger of one and the least the rest of the description allows
    that half (`_at_widths` at nought), which every band the producer
    withholds holds, whatever pair of widths its search takes -- asked
    without the withholding's own certificate, which the producer asks
    and the loader need not repeat to refuse what the producer never
    writes (`bands`, `in_band`), and asked where any day can hold the
    line at all; then WC7 and WC8 (`check`, on
    the reader's bounds, with `holes` -- every hole the description
    publishes, `calendar_rules.public_holes`). The
    first broken rule is returned as (rule, what the census says, what
    the rule asks), the two phrases a person reads beside the rule's own
    words.

    Guarantees: accepts the census and the description's numbers;
    returns None or the broken rule. Determinism: a function of the
    arguments. Raises nothing. No I/O of any kind.
    """
    body = parsed - rows_low - rows_high
    expect = 0
    for first, last, _count in groups:
        if first != expect or last < first or last >= calendar_rules.WEEKDAYS:
            return (
                "WC1",
                f"a group runs from weekday {first} to weekday {last}",
                f"the next group must start at weekday {expect} and no group "
                f"may end past weekday 6",
            )
        expect = last + 1
    if expect != calendar_rules.WEEKDAYS:
        return (
            "WC1",
            f"the groups stop at weekday {expect - 1}",
            "they must cover every weekday up to 6, Sunday",
        )
    for first, last, count in groups:
        if 0 < count < line:
            return (
                "WC2",
                f"the group from weekday {first} to weekday {last} counts {count}",
                f"a count is nought or at least {line}",
            )
    total = sum(count for _first, _last, count in groups)
    if total != body:
        return (
            "WC3",
            f"the groups add to {total}",
            f"the values between the two tail boundaries number {body}",
        )
    if calendar_rules.entry_of(groups) == calendar_rules.ENTRY_NONE:
        return (
            "WC4",
            "the groups are not one of the three groupings the census uses",
            "each weekday alone, Monday to Friday alone with the weekend "
            "together, or the weekdays together and the weekend together",
        )
    if not one_spelling:
        return (
            "WC6",
            "a weekday census is published",
            "the censuses of written forms must give every date one text",
        )
    knots = _knots_of(parsed, rows_low, rows_high, low, high, rungs)
    sure = [0 for _ in range(calendar_rules.WEEKDAYS)]
    for day in sorted(knots):
        before, upto = knots[day]
        weekday = calendar_rules.weekday_of(day)
        sure[weekday] = sure[weekday] + max(1, upto - before)
    short = calendar_rules.sure_cells_breach(groups, sure, line)
    if short >= 0:
        first, last, count = groups[short]
        return (
            "WC5",
            f"the group from weekday {first} to weekday {last} counts {count}",
            f"what is left of it once its boundary and rung days are "
            f"counted must be nought or at least {line}",
        )
    if not ties_refused(body, fewest, line):
        widest = bands(
            parsed, rows_low, rows_high, low, high, rungs, fewest, most,
            line, holes,
        )
        banded = _at_widths(widest, 0, 0, widest.solves)
        if in_band(groups, banded):
            return (
                "WC9",
                "the weekday census",
                "the weekend, and Monday to Friday together, must each hold "
                "none, or more than the larger of one and the least the rest "
                "of this description allows that half: a weekend of "
                f"{banded.weekend[0]} row{'' if banded.weekend[0] == 1 else 's'}, "
                f"and Monday to Friday of {banded.weekdays[0]}, are always "
                "withheld",
            )
    verdict = check(
        parsed, rows_low, rows_high, low, high, rungs, fewest, most, line,
        groups, -1, holes,
    )
    if verdict.holds:
        return None
    if verdict.reason == calendar_rules.REASON_FEW_DATES:
        return (
            "WC7",
            "a group of the weekday census",
            "every non-zero group must be able to hold at least four dates "
            "besides its boundary and rung days",
        )
    return (
        "WC8",
        "the weekday census",
        f"every day of a counted weekday must be able to hold {line} rows in "
        "some table meeting this description, or lie where the rank facts "
        "already hold it below the line and the census allows everything "
        f"the rest of the description allows there ({verdict.detail})",
    )

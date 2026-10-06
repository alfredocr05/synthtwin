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
# THE HOUR CENSUS OF A COLUMN OF MOMENTS (landing 3b.2-H, lane T2, plan
# P4-D371; contract 6.6.2, HC1 to HC6; method G7.3g; validation V5-H1).
#
# A column of moments read on its own clock publishes how many cells of
# its BODY -- the cells between the two tail boundaries, both included --
# fall on each hour of the written wall clock (`canonical[11:13]`), in
# GROUPS merged from the twenty-four hours by the one merge rule every
# census shares (`calendar_rules.merged_groups`), ON A LINE: hour 23 and
# hour 0 are no neighbours, because a day ends between them, so no group
# runs past midnight (HC1). Every count is nought or at least the census
# line (HC2), the counts add to the body (HC3), the published p75 less
# p25 is at least `HOUR_SPAN_DAYS` days, so no census is the hourly series
# of a few dates (HC4), every group holds at least the cells the rest of
# the description places in it for certain and what is left of it is
# nought or at least the line (HC5, `hour_sure`), and a workbook's
# published cell classes do not show the column stored two ways (HC6).
#
# A census with one non-empty group is published: its one count is the
# body, which the description already gives, and it says the empty hours
# are empty (the measurement of 2026-10-01: a column of morning draws
# came back at an hour TVD of 0.953 without it, 0.021 with it). One
# group over every hour says nothing and is never published.

HOURS = 24
HOUR_SECONDS = 3600
DAY_SECONDS = 86400
# HC4: the fewest days the published p75 less p25 may span.
HOUR_SPAN_DAYS = 4

# Why a column of moments publishes no hour census, each said in a
# sentence of its own: no tails (HC3), a middle half shorter than
# `HOUR_SPAN_DAYS` days (HC4), a workbook storing the column two ways
# (HC6), or no grouping the merge rule can publish.
HOUR_REASON_NO_TAILS = "no_tails"
HOUR_REASON_SPAN = "span"
HOUR_REASON_WORKBOOK = "workbook"
HOUR_REASON_GROUPING = "grouping"
HOUR_REASONS = (
    HOUR_REASON_NO_TAILS,
    HOUR_REASON_SPAN,
    HOUR_REASON_WORKBOOK,
    HOUR_REASON_GROUPING,
)

# The names `calendar_rules.census_breach` reports the hour census's
# cover, floor, total and sure cells under.
HOUR_RULES = ("HC1", "HC2", "HC3", "HC5")


def hour_of(instant: int) -> int:
    """The hour of the written wall clock of an instant counted in seconds.

    Guarantees: accepts whole seconds from 1970-01-01 00:00:00 on the
    column's own clock; returns 0 to 23. Raises nothing. No I/O.
    """
    return (instant // HOUR_SECONDS) % HOURS


def hour_bins(instants: "list[int]") -> "list[int]":
    """How many of these instants fall on each hour, hour 0 first.

    Guarantees: accepts instants in seconds; returns twenty-four counts.
    Determinism: a function of the instants. Raises nothing. No I/O.
    """
    bins = [0 for _hour in range(HOURS)]
    for instant in instants:
        hour = hour_of(instant)
        bins[hour] = bins[hour] + 1
    return bins


def rung_rank(percent: int, parsed: int) -> int:
    """The rank a published rung at `percent` is read off (contract D11).

    `floor((P - 1) * c / 100)`, the rank the producer reads the rung off
    and the generator pins it to. Raises nothing. No I/O.
    """
    return min(parsed - 1, ((parsed - 1) * percent) // 100)


def midnight_sure(
    at_midnight: "int | None", tails: "list[tuple[int, tuple[str, ...] | None]]"
) -> "int | None":
    """RULE 4: how many body cells stand at 00:00:00 for certain, or None.

    `n_at_midnight` counts every parsed cell at midnight, the tails'
    too. A tail publishing its values holds only those values (TL1), so
    a tail whose every listed value stands at midnight holds all of its
    rows there: those rows come out (the design skeptic's M1 -- an epoch
    sentinel, `1970-01-01 00:00:00`, IS the low tail, and charging its
    rows to the body put clinic visits at night). The rest is the body's.
    None where the count is withheld.

    Guarantees: accepts the published count and each tail's rows and
    listed canonical values (None where it lists none); returns the
    count, never below nought, or None. Raises nothing. No I/O.
    """
    if at_midnight is None:
        return None
    left = at_midnight
    for rows, values in tails:
        if not values:
            continue
        every = True
        for value in values:
            if value[11:19] != "00:00:00":
                every = False
        if every:
            left = left - rows
    return max(left, 0)


def hour_sure(
    published: "list[tuple[int, int]]", at_midnight: "int | None"
) -> "list[int]":
    """The SURE cells of each hour: those the rest of a description places there.

    `published` is every published body instant with the rank it is
    read off -- both tail boundaries and every published rung -- and
    every rank between two of one instant stands there too. Each such
    rank counts in its own hour. `at_midnight` is rule 4's count
    (`midnight_sure`); where it is not None it goes in hour 0 IN PLACE OF
    the published ranks at exactly 00:00:00, whichever is more, since
    both count body cells at midnight.

    Guarantees: accepts the (rank, instant) pairs and the count; returns
    twenty-four counts. Determinism: a function of the two. Raises
    nothing. No I/O of any kind.
    """
    known: "dict[int, int]" = {}
    ordered = sorted(published)
    for rank, instant in ordered:
        known[rank] = instant
    for place in range(len(ordered) - 1):
        first, here = ordered[place]
        last, there = ordered[place + 1]
        if here == there:
            for rank in range(first, last + 1):
                known[rank] = here
    sure = [0 for _hour in range(HOURS)]
    zero = 0
    for rank in sorted(known):
        instant = known[rank]
        if instant % DAY_SECONDS == 0:
            zero = zero + 1
            continue
        hour = hour_of(instant)
        sure[hour] = sure[hour] + 1
    if at_midnight is not None:
        zero = max(zero, at_midnight)
    sure[0] = sure[0] + zero
    return sure


def hour_groups(
    bins: "list[int]", sure: "list[int]", line: int
) -> "tuple[tuple[int, int, int], ...]":
    """The groups an hour census publishes, or none: the one merge rule
    (`calendar_rules.merged_groups`) over twenty-four hours on a line.

    Guarantees: accepts the hour counts of the body, the sure cells and
    the census line; returns `(first, last, count)` per group, or `()`.
    Determinism: a function of the three. Raises nothing. No I/O.
    """
    return calendar_rules.merged_groups(bins, sure, line, False)


def hour_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    body: int,
    line: int,
    sure: "list[int]",
) -> "tuple[str, str, str] | None":
    """A published hour census held to HC1, HC2, HC3's total and HC5, or None.

    THE ONE CHECK THE PRODUCER AND THE LOADER BOTH ASK, through the one
    checker every census shares (`calendar_rules.census_breach`), over
    hours 0 to 23 on a line: the first rule broken, as (rule, what the
    census says, what the rule asks).

    Guarantees: accepts the groups, the body, the census line and the
    sure cells; returns None or the broken rule. Determinism: a function
    of the four. Raises nothing. No I/O of any kind.
    """
    return calendar_rules.census_breach(
        groups, HOURS, line, body, tuple(sure), False, 0, "hour", HOUR_RULES
    )


def span_long_enough(p25: "int | None", p75: "int | None") -> bool:
    """HC4: whether the published middle half spans `HOUR_SPAN_DAYS` days.

    `p25` and `p75` are the two rungs in seconds, None where withheld;
    a rung withheld leaves the span unpublished, and no census stands.
    Raises nothing. No I/O of any kind.
    """
    if p25 is None or p75 is None:
        return False
    return p75 - p25 >= HOUR_SPAN_DAYS * DAY_SECONDS


def seconds_of(canonical: str) -> int:
    """The instant of a canonical moment, `YYYY-MM-DD HH:MM:SS`, in whole
    seconds from 1970-01-01 00:00:00 on its own wall clock; a sixtieth
    second counts as the next minute's first. Raises ValueError for text
    that is not canonical. No I/O of any kind.
    """
    day = parsing.days_from_civil(
        int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10])
    )
    return (
        day * DAY_SECONDS
        + int(canonical[11:13]) * HOUR_SECONDS
        + int(canonical[14:16]) * 60
        + int(canonical[17:19])
    )


# THE HALF DAY OF A DECLARED 12-HOUR STAMP (landing 3b.2-H, plan P4-D370's
# carve-out, method G7.3b step 10 and G12.14). A slashed stamp the person
# declared a 12-hour clock with no marker (`--twelve-hour`) is read on its
# dial: `12` is the first hour, so every value it holds stands from 00:00
# to 11:59 of its day, and a twin instant after noon is written on the
# dial and reads twelve hours earlier. Its tail ranks stand on the MORNING
# of a day -- the dial's half day -- and never at a written midnight,
# which the column's count at midnight holds: from one unit past 00:00 to
# the last unit before noon.
HALF_DAY_SECONDS = 43200


def morning(place: int, unit: int) -> bool:
    """Whether an instant in seconds stands on the dial's half day, one
    `unit` of seconds past midnight at least and before noon."""
    clock = place % DAY_SECONDS
    return unit <= clock < HALF_DAY_SECONDS


def morning_at_or_after(place: int, unit: int) -> int:
    """The first place of the half day at or after `place`, on its unit's
    grid (a place on the grid is a whole number of units from midnight)."""
    if morning(place, unit):
        return place
    day = place // DAY_SECONDS
    if place % DAY_SECONDS < unit:
        return day * DAY_SECONDS + unit
    return (day + 1) * DAY_SECONDS + unit


def morning_at_or_before(place: int, unit: int) -> int:
    """The last place of the half day at or before `place`, on its grid."""
    if morning(place, unit):
        return place
    day = place // DAY_SECONDS
    if place % DAY_SECONDS >= HALF_DAY_SECONDS:
        return day * DAY_SECONDS + HALF_DAY_SECONDS - unit
    return (day - 1) * DAY_SECONDS + HALF_DAY_SECONDS - unit


def half_day_distances(
    found: "list[int]",
    anchor: int,
    unit: int,
    low_side: bool,
    apart: bool,
    edge: int,
) -> "list[int]":
    """A tail's whole distances, each on the dial's half day (G7.3b step 10).

    A rank at distance `d` stands at `anchor - d * unit` on the low side
    and `anchor + d * unit` on the high side, in seconds. Each distance
    whose place is not on the half day (`morning`) is taken to the
    nearest one whose place is -- the later place of the morning after,
    or the earlier of the morning before -- the nearer the boundary on a
    tie, and at least one. Where the ranks must all differ (`apart`),
    the construction's two passes are made again over those distances
    alone: from the innermost out, each made the next one past the one
    inside it, then, from the outermost in, the one before the one
    outside it; and each is kept at the furthest such distance within
    `edge`. Every step is monotone in each distance, so the strata of
    G12.14 drawn through it bound every rank.

    Guarantees: accepts the distances outermost first, the boundary in
    seconds, the seconds of one tail unit, the side, whether the ranks
    must differ and the edge; returns as many distances. Raises
    nothing. No I/O of any kind.
    """

    def place(distance: int) -> int:
        return anchor - distance * unit if low_side else anchor + distance * unit

    def distance_of(spot: int) -> int:
        return (anchor - spot) // unit if low_side else (spot - anchor) // unit

    def further(distance: int) -> int:
        spot = place(distance)
        if low_side:
            return distance_of(morning_at_or_before(spot, unit))
        return distance_of(morning_at_or_after(spot, unit))

    def nearer(distance: int) -> int:
        spot = place(distance)
        if low_side:
            return distance_of(morning_at_or_after(spot, unit))
        return distance_of(morning_at_or_before(spot, unit))

    first = further(1)
    top = nearer(edge)
    if top < first:
        top = first

    def nearest(distance: int) -> int:
        if distance < 1:
            distance = 1
        out = further(distance)
        if out == distance:
            return distance
        inward = nearer(distance)
        if inward < 1:
            return out
        if distance - inward <= out - distance:
            return inward
        return out

    rows = len(found)
    placed = [nearest(value) for value in found]
    if apart:
        for index in range(rows - 2, -1, -1):
            if placed[index] <= placed[index + 1]:
                placed[index] = further(placed[index + 1] + 1)
            placed[index] = min(placed[index], top)
        for index in range(1, rows):
            if placed[index] >= placed[index - 1]:
                inward = nearer(placed[index - 1] - 1)
                placed[index] = max(first, inward)
    return [min(value, top) for value in placed]


# anchor 3b-T3 (P4-D372)
# anchor 3b-C1 (P4-D373)
# anchor 3b-C2 (P4-D374)
# anchor 3b-G1 (P4-D375)
# anchor 3b-G3 (P4-D376)
# anchor 3b-G2 (P4-D377)
# anchor 3b-7 (P4-D378)
# anchor 3b-J (P4-D379)
# anchor 3b-R2a (P4-D383)
# anchor 3b-R2b (P4-D383)
# anchor 3b-R2c (P4-D383)
# anchor 3b-R4 (P4-D384)

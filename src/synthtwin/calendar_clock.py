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
# THE HOUR CENSUS OF A COLUMN OF MOMENTS (landing 3b.2-H, lane T2, plan
# P4-D371; contract 6.6.2, HC1 to HC6; method G7.3g; validation V5-H1).
#
# A column of moments read on its own clock publishes how many cells of
# its BODY -- the cells between the two tail boundaries, both included --
# fall on each hour of the written wall clock (`canonical[11:13]`, read
# off the text, so a sixtieth second counts in the hour it is written in:
# `written_hour`), in GROUPS merged from the twenty-four hours by the one
# merge rule every census shares (`calendar_rules.merged_groups`), ON A
# LINE: hour 23 and hour 0 are no neighbours, because a day ends between
# them, so no group runs past midnight (HC1). Every count is nought or at
# least the census line (HC2), the counts add to the body (HC3), the
# published p75 less p25 is at least `HOUR_SPAN_DAYS` days, so no census
# is the hourly series of a few dates (HC4), every group holds at least
# the cells the rest of the description places in it for certain and
# what is left of it is nought or at least the line (HC5, `hour_sure`),
# and a workbook's published cell classes do not show the column stored
# two ways (HC6).
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
# sentence of its own: no tails (HC3), a published middle half shorter
# than `HOUR_SPAN_DAYS` days, or one whose 25th or 75th percentile lies
# inside a tail and so is not published (HC4 both: Codex's review of the
# landing, item 4, found a column whose real middle half spans 31 days
# told that it spans fewer than four), a workbook storing the column two
# ways (HC6), or no grouping the merge rule can publish with every
# group's sure cells inside it (HC2 and HC5).
HOUR_REASON_NO_TAILS = "no_tails"
HOUR_REASON_SPAN = "span"
HOUR_REASON_SPAN_UNPUBLISHED = "span_unpublished"
HOUR_REASON_WORKBOOK = "workbook"
HOUR_REASON_GROUPING = "grouping"
HOUR_REASONS = (
    HOUR_REASON_NO_TAILS,
    HOUR_REASON_SPAN,
    HOUR_REASON_SPAN_UNPUBLISHED,
    HOUR_REASON_WORKBOOK,
    HOUR_REASON_GROUPING,
)

# The names `calendar_rules.census_breach` reports the hour census's
# cover, floor, total and sure cells under.
HOUR_RULES = ("HC1", "HC2", "HC3", "HC5")


def written_hour(canonical: str) -> int:
    """The hour a canonical moment, `YYYY-MM-DD HH:MM:SS`, is WRITTEN in:
    `canonical[11:13]`, the hour census's own definition (contract 6.6.2).

    THE WRITTEN HOUR IS READ OFF THE TEXT, NEVER OFF THE INSTANT (Codex's
    review of landing 3b.2-H, item 1). A sixtieth second, `23:59:60`, is
    written in hour 23, and its instant (`seconds_of`) is the next day's
    first second: eleven of them on each of 100 dates had all 1,078 body
    cells counted in hour 0, and the twin wrote its body there. The
    companion of `calendar_rules.written_day`, lane D2's written day, which
    reads `canonical[0:10]` for the same reason.

    Guarantees: accepts canonical text; returns 0 to 23. Raises
    ValueError for text that is not canonical. No I/O of any kind.
    """
    return int(canonical[11:13])


def hour_bins(hours: "list[int]") -> "list[int]":
    """How many cells fall on each written hour, hour 0 first.

    Guarantees: accepts each cell's written hour (`written_hour`), 0 to
    23; returns twenty-four counts. Determinism: a function of the hours.
    Raises nothing. No I/O.
    """
    bins = [0 for _hour in range(HOURS)]
    for hour in hours:
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
    published: "list[tuple[int, str]]", at_midnight: "int | None"
) -> "list[int]":
    """The SURE cells of each hour: those the rest of a description places there.

    `published` is every published body value -- both tail boundaries
    and every published rung, as canonical text -- with the rank it is
    read off, and every rank between two of one value stands there too.
    Each such rank counts in its WRITTEN hour (`written_hour`): two values
    of one instant written differently, a sixtieth second and the next
    day's midnight, are two values, and a rank between them may hold
    either. `at_midnight` is rule 4's count (`midnight_sure`); where it is
    not None it goes in hour 0 IN PLACE OF the published ranks written at
    00:00:00, whichever is more, since both count body cells at midnight.

    Guarantees: accepts the (rank, canonical text) pairs and the count;
    returns twenty-four counts. Determinism: a function of the two.
    Raises nothing for canonical text. No I/O of any kind.
    """
    known: "dict[int, str]" = {}
    ordered = sorted(published)
    for rank, value in ordered:
        known[rank] = value
    for place in range(len(ordered) - 1):
        first, here = ordered[place]
        last, there = ordered[place + 1]
        if here == there:
            for rank in range(first, last + 1):
                known[rank] = here
    sure = [0 for _hour in range(HOURS)]
    zero = 0
    for rank in sorted(known):
        value = known[rank]
        if value[11:19] == "00:00:00":
            zero = zero + 1
            continue
        hour = written_hour(value)
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
    second counts as the next minute's first. The ARITHMETIC ordinal --
    what orders cells, measures a span and places a cell between two
    boundaries -- and never the hour a cell is written in, which
    `written_hour` reads off the text. Raises ValueError for text that is
    not canonical. No I/O of any kind.
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
# THE MINUTE AND SECOND CENSUSES OF A COLUMN OF MOMENTS, AND THEIR HEAPS
# (landing 3b.4, lane T3, plan P4-D372; contract 6.6.2, MC1 to MC6, SE1 to
# SE6, MH1, MH2, SH1 and SH2; method G7.3h; validation V5-M1 and V5-S1).
#
# A column of moments whose hour census may stand publishes, over the same
# BODY, how its cells fall on the minutes of the hour (`canonical[14:16]`)
# and -- written to the second or finer -- on the seconds of the minute
# (`canonical[17:19]`), each read off the text: a sixtieth second,
# `HH:MM:60`, counts in the minute it is written in and in that minute's
# last second, 59, never in the next minute (`written_minute`,
# `written_second`). Each field publishes two lists:
#
# - its HEAPS, every value holding at least the census line and at least
#   three times the median of the five values on each side of it on the
#   cycle of sixty (`calendar_rules.standing_out`, the clock's centre --
#   the design skeptic's M1: below 2,500 rows a contiguous census folded a
#   clinic's quarter hours into their neighbours, and the heaps keep them),
#   each with its count, and only where that count less the cells the rest
#   of the description places there for certain is nought or at least the
#   line, as every census group's is;
# - its CENSUS, the cells on no heap counted in groups of values merged by
#   the one merge rule on a line, each count nought or at least the line;
#   `[]` where nothing is left beside the heaps or the rule leaves one
#   group over every value.
#
# A field publishes only where the body's sixty counts depart from flat,
# chi-squared per degree of freedom of `FLAT_DEPARTURE` or more (the
# design's producer-only choice: heaped columns measured 55 to 9,978, flat
# ones 0.8 to 1.3), and not where how the body falls on the field depends
# on the hour of the day (the design skeptic's M3: night charting on the
# hour beside day entries at any minute came back with the comparison
# reversed): the same statistic over the body's hour groups crossed with
# the field's groups by the one merge rule on the line (the Codex review of
# landing 3b.4, item 2) -- and over the single values holding a twentieth
# of the body and the rest -- the cells at a published midnight left out, of
# `HOUR_DEPENDENCE` or more withholds it -- where one count over every hour
# would also put some hour group farther from its own shares than a flat
# field (`misled_by_the_count`, the lane's skeptic, item 7).

MINUTE = "minute"
SECOND = "second"
FIELD_VALUES = 60
# MC4 and SE4: the fewest seconds the published p75 less p25 may span, so
# no census is the minutes of a few hours or the seconds of a few minutes.
FIELD_SPAN_SECONDS = {MINUTE: 4 * HOUR_SECONDS, SECOND: 4 * 60}
# The chi-squared per degree of freedom a field's sixty counts depart from
# flat at, and the one at which the field depends on the hour (M3) -- where
# its strength, Cramer's V, is also at least `DEPENDENCE_STRENGTH`
# hundredths.
FLAT_DEPARTURE = 4
HOUR_DEPENDENCE = 4
DEPENDENCE_STRENGTH = 20
# M3's COARSE columns: the single values holding at least this share of the
# body, in hundredths, and the rest as one; its FINE columns are the field's
# groups by the one merge rule on the line (`_hour_table`).
DEPENDENCE_SHARE_PERCENT = 5
# How many values on each side the stand-out rule reads (median and three
# times, `calendar_rules.CENTRE_MEDIAN`).
FIELD_REACH = 5

# Why a column of moments publishes no minute or second census. The three
# the hour census shares -- no tails, an unpublished span, two storages --
# withhold every census of the clock, and the hour census's own sentence
# says so once (NF89, NF117, NF91); the other three are each said in a
# sentence of the field's own: a middle half too short (MC4, SE4), no
# grouping the merge rule publishes and no heap (MC5, SE5), and a field
# depending on the hour (M3), and a census of the rest standing on a few
# different values beside no heap (`few_values`), and counts away from
# value 0 a body could be left too few cells off a midnight to hold
# (`off_midnight_short`). A field whose counts do not depart from flat
# publishes nothing and says nothing: its twin's flat draw is its shape.
FIELD_REASON_FLAT = "flat"
FIELD_REASON_HOUR = "hour"
FIELD_REASON_FEW_VALUES = "few_values"
FIELD_REASON_OFF_MIDNIGHT = "off_midnight"
# ...and, for both fields at once, a lattice the column's different values
# crowd (`lattice_crowded`; lane J2's skeptic, item 1).
FIELD_REASON_CROWDED = "crowded"
# ...and, for both fields at once, a column nearly every value of which is
# at midnight, its count there withheld (Codex's review of lane J2, item 4:
# the fallback had said NF118's reason, though no count away from value 0
# stood).
FIELD_REASON_MIDNIGHT_UNCOUNTED = "midnight_uncounted"
FIELD_REASONS = (
    HOUR_REASON_NO_TAILS,
    HOUR_REASON_SPAN,
    HOUR_REASON_SPAN_UNPUBLISHED,
    HOUR_REASON_WORKBOOK,
    HOUR_REASON_GROUPING,
    FIELD_REASON_FLAT,
    FIELD_REASON_HOUR,
    FIELD_REASON_FEW_VALUES,
    FIELD_REASON_OFF_MIDNIGHT,
    FIELD_REASON_CROWDED,
    FIELD_REASON_MIDNIGHT_UNCOUNTED,
)
# The reasons said in a sentence of the field's own.
FIELD_REASONS_SAID = (
    HOUR_REASON_SPAN,
    HOUR_REASON_GROUPING,
    FIELD_REASON_HOUR,
    FIELD_REASON_FEW_VALUES,
    FIELD_REASON_OFF_MIDNIGHT,
    FIELD_REASON_CROWDED,
    FIELD_REASON_MIDNIGHT_UNCOUNTED,
)

# The names `calendar_rules.census_breach` reports each field's census
# under, and each field's heap rules.
FIELD_RULES = {
    MINUTE: ("MC1", "MC2", "MC3", "MC5"),
    SECOND: ("SE1", "SE2", "SE3", "SE5"),
}
FIELD_HEAP_RULES = {MINUTE: ("MH1", "MH2"), SECOND: ("SH1", "SH2")}
# Each field's keys, census then heaps.
FIELD_KEYS = {
    MINUTE: (MINUTE_CENSUS, MINUTE_HEAPS),
    SECOND: (SECOND_CENSUS, SECOND_HEAPS),
}


def written_minute(canonical: str) -> int:
    """The minute of the hour a canonical moment is WRITTEN in, 0 to 59:
    `canonical[14:16]`, so a sixtieth second stays in its own minute.
    Raises ValueError for text that is not canonical. No I/O."""
    return int(canonical[14:16])


def written_second(canonical: str) -> int:
    """The second of the minute a canonical moment is WRITTEN in, 0 to 59:
    `canonical[17:19]`, a sixtieth second counted in 59, the last second
    of the minute it is written in -- never the next minute's first,
    where its instant (`seconds_of`) stands. Raises ValueError for text
    that is not canonical. No I/O."""
    return min(int(canonical[17:19]), FIELD_VALUES - 1)


def written_field(canonical: str, field: str) -> int:
    """The value of `field` -- `MINUTE` or `SECOND` -- a moment is written at."""
    if field == SECOND:
        return written_second(canonical)
    return written_minute(canonical)


def field_bins(values: "list[int] | tuple[int, ...]") -> "list[int]":
    """How many cells fall on each value of a field, 0 first: sixty counts.

    Guarantees: accepts each cell's written value, 0 to 59. Raises
    nothing. No I/O of any kind.
    """
    bins = [0 for _value in range(FIELD_VALUES)]
    for value in values:
        bins[value] = bins[value] + 1
    return bins


def field_sure(
    published: "list[tuple[int, str]]", at_midnight: "int | None", field: str
) -> "list[int]":
    """The SURE cells of each value of a field (MC5, SE5), sixty counts.

    As `hour_sure`: every published body value -- the tail boundaries and
    the rungs, with every rank between two of one value -- in the value
    it is written at, and rule 4's cells at midnight (`midnight_sure`) in
    value 0 in place of the published ranks written at 00:00:00, whichever
    is more. Guarantees: a function of the three. Raises nothing for
    canonical text. No I/O of any kind.
    """
    known: "dict[int, str]" = {}
    ordered = sorted(published)
    for rank, value in ordered:
        known[rank] = value
    for place in range(len(ordered) - 1):
        first, here = ordered[place]
        last, there = ordered[place + 1]
        if here == there:
            for rank in range(first, last + 1):
                known[rank] = here
    sure = [0 for _value in range(FIELD_VALUES)]
    zero = 0
    for rank in sorted(known):
        value = known[rank]
        if value[11:19] == "00:00:00":
            zero = zero + 1
            continue
        place = written_field(value, field)
        sure[place] = sure[place] + 1
    if at_midnight is not None:
        zero = max(zero, at_midnight)
    sure[0] = sure[0] + zero
    return sure


def departs_from_flat(bins: "list[int]") -> bool:
    """Whether a field's counts depart from flat: chi-squared per degree of
    freedom of `FLAT_DEPARTURE` or more, asked in whole numbers.

    With n cells over k values, chi-squared is k times the sum of the
    squared counts over n, less n; so the test is
    k * sum(c * c) - n * n >= FLAT_DEPARTURE * (k - 1) * n. No cells, no
    departure. Raises nothing. No I/O.
    """
    total = sum(bins)
    if total <= 0:
        return False
    size = len(bins)
    squares = sum(count * count for count in bins)
    return size * squares - total * total >= FLAT_DEPARTURE * (size - 1) * total


def _hour_table(
    hours: "list[int] | tuple[int, ...]",
    values: "list[int] | tuple[int, ...]",
    line: int,
    fine: bool,
    starts: "list[bool] | tuple[bool, ...] | None" = None,
) -> "tuple[list[list[int]], list[int]]":
    """One of M3's two TABLES: the body's hour groups crossed with the field.

    Its rows are the HOUR GROUPS -- the one merge rule over the twenty-four
    hour counts at the census line with no sure cells (`hour_groups`). Its
    columns are COARSE -- the field's single values each holding at least
    `DEPENDENCE_SHARE_PERCENT` hundredths of the body, and the rest as one
    -- or, `fine`, the FIELD GROUPS, the same merge rule over the sixty
    counts of the field (`field_groups`), so every value holding the line's
    cells is a column of its own. M3 asks both (the Codex review of landing
    3b.4, item 2: coarse alone pooled every minute of 3,600 rows under a
    twentieth of the body into one column, and the dependence it hid
    doubled a morning's share on twenty minutes in the twin; fine alone
    spreads night charting on the hour over some 27 columns of a thousand
    cells, where its chi-squared per degree of freedom falls to 1.6).
    Given `starts` -- whether each cell is the first of its different
    written value -- the table counts EVENTS, each different value once,
    in the rows and columns the cells draw (the verifier's item 8 on the
    Codex round of landing 3b.4). Returns the table, row by row, and each
    column's width in values; `([], [])` where the hours merge to one
    group or the field to one column. Raises nothing. No I/O.
    """
    total = len(values)
    if total <= 0 or len(hours) != total:
        return [], []
    groups = hour_groups(hour_bins(list(hours)), [], line)
    if not groups:
        return [], []
    row_of = [0 for _hour in range(HOURS)]
    for index in range(len(groups)):
        for hour in range(groups[index][0], groups[index][1] + 1):
            row_of[hour] = index
    bins = field_bins(values)
    column_of = [0 for _value in range(FIELD_VALUES)]
    widths: "list[int]" = []
    if fine:
        for first, last, _count in field_groups(bins, [], line):
            for value in range(first, last + 1):
                column_of[value] = len(widths)
            widths += [last - first + 1]
    else:
        widths = [FIELD_VALUES]
        for value in range(FIELD_VALUES):
            if 100 * bins[value] >= DEPENDENCE_SHARE_PERCENT * total:
                column_of[value] = len(widths)
                widths += [1]
                widths[0] = widths[0] - 1
    if len(widths) < 2:
        return [], []
    table = [[0 for _column in widths] for _row in range(len(groups))]
    for place in range(total):
        if starts is not None and place < len(starts) and not starts[place]:
            continue
        row = row_of[hours[place]]
        column = column_of[values[place]]
        table[row][column] = table[row][column] + 1
    return table, widths


def depends_on_the_hour(
    hours: "list[int] | tuple[int, ...]",
    values: "list[int] | tuple[int, ...]",
    line: int,
    squares: int = 0,
    fine: bool = False,
    starts: "list[bool] | tuple[bool, ...] | None" = None,
) -> bool:
    """M3: whether how a body falls on a field depends on the hour of the day.

    The table (`_hour_table`): the body's hour groups crossed with the
    field's coarse columns, or its `fine` ones. Its
    chi-squared per degree of freedom, asked exactly in fractions, of
    `HOUR_DEPENDENCE` or more is a dependence -- where its STRENGTH,
    Cramer's V, is also at least `DEPENDENCE_STRENGTH` hundredths (the
    builder's measurement of 2026-10-12: chi-squared grows with the rows,
    so 10,000 cells written `HH:MM:00` whose minute does not follow the
    hour scored 3.9 counted by value, at a V of 0.11; night charting on the
    hour beside day entries scores a V near 0.98). Cells written alike are
    one event written on several rows, so THE TABLE COUNTS EVENTS: given
    `starts`, whether each cell is the first of its different written
    value, each different value is counted once, in the rows and columns
    the cells draw (the verifier's item 8 on the Codex round of landing
    3b.4: one global design effect -- the squared ties over the cells --
    sank a strong dependence under one stamp written a hundred times, the
    twin then putting 205 of 459 daytime cells on minute 0 against 6, and
    under day stamps written thirty times beside night stamps once; and
    divided row by row it still called one burst among independent minutes
    a dependence). Without `starts`, the cells are counted, and `squares`
    -- the sum of the squared number of cells each different value holds,
    nought for none -- over the cells is an even DESIGN EFFECT dividing
    the test, as the events would under ties all alike. The strength is
    chi-squared over the counts, LESS what a table with no dependence gives
    -- the design effect times the degrees of freedom -- over the counts
    times one less than the table's shorter side (the Codex review of
    landing 3b.4, item 1), so ties alone neither sink a complete dependence
    nor raise none; and it is the larger of that and the strongest HOUR
    GROUP's against the rest of the body, the two-row table's chi-squared
    less the design effect times one less than its columns, over the counts
    (the verifier's item 9: 40,800 cells over fourteen hour groups and
    sixty minute groups held one morning's dependence to a V squared of
    0.017, and the twin put 2,282 of 5,400 cells of hour 08 on minutes 00
    to 19 against 1,800). Where the hours merge to one group, or the field
    to one column, there is no table and no dependence. The caller leaves
    out the cells at a published midnight. `hours` and `values` are the
    cells' written hour and value, pair by pair.

    Guarantees: a function of the six. Raises nothing. No I/O.
    """
    table, _widths = _hour_table(hours, values, line, fine, starts)
    if not table:
        return False
    rows = [sum(row) for row in table]
    total = sum(rows)
    sums = [sum(table[row][column] for row in range(len(table))) for column in range(len(table[0]))]
    kept_rows = len([count for count in rows if count > 0])
    kept_columns = len([count for count in sums if count > 0])
    freedom = (kept_rows - 1) * (kept_columns - 1)
    if freedom <= 0:
        return False
    # chi-squared = n * (sum of O * O / (row * column) - 1), in fractions;
    # each row's sum of O * O / column kept for its own two-row table.
    numerator = 0
    denominator = 1
    parts: "list[tuple[int, int]]" = []
    for row in range(len(table)):
        part_top = 0
        part_bottom = 1
        for column in range(len(sums)):
            count = table[row][column]
            if count > 0:
                part_top, part_bottom = _fraction_sum(
                    part_top, part_bottom, count * count, sums[column]
                )
        parts += [(part_top, part_bottom)]
        if rows[row] > 0:
            numerator, denominator = _fraction_sum(
                numerator, denominator, part_top, part_bottom * rows[row]
            )
    # chi-squared = total * excess / denominator, the design effect weight /
    # total. The test: chi-squared over the design effect, over freedom, at
    # least HOUR_DEPENDENCE. The strength: (chi-squared - the design effect
    # times freedom) over total times (the shorter side less one) at least
    # the strength squared, in hundredths -- each times total * denominator.
    weight = squares if starts is None and squares > 0 else total
    shorter = min(kept_rows, kept_columns) - 1
    excess = numerator - denominator
    floor = DEPENDENCE_STRENGTH * DEPENDENCE_STRENGTH
    if total * total * excess >= HOUR_DEPENDENCE * freedom * weight * denominator and (
        10000 * (total * total * excess - weight * freedom * denominator)
        >= floor * shorter * total * total * denominator
    ):
        return True
    # One hour group of R against the rest: chi-squared = n (n a - R * R)
    # over R (n - R), a its row's sum of O * O / column; the test and the
    # strength each asked times n * R * (n - R) * a's denominator.
    for row in range(len(table)):
        size = rows[row]
        if size <= 0 or size >= total:
            continue
        part_top, part_bottom = parts[row]
        spread = size * (total - size) * part_bottom
        scaled = total * total * (total * part_top - size * size * part_bottom)
        if scaled >= HOUR_DEPENDENCE * (kept_columns - 1) * weight * spread and (
            10000 * (scaled - weight * (kept_columns - 1) * spread)
            >= floor * total * total * spread
        ):
            return True
    return False


def _fraction_sum(top: int, bottom: int, part_top: int, part_bottom: int) -> "tuple[int, int]":
    """`top / bottom` plus `part_top / part_bottom`, lowest terms, both
    bottoms above nought. Raises nothing. No I/O."""
    top = top * part_bottom + part_top * bottom
    bottom = bottom * part_bottom
    common = common_divisor(top, bottom)
    return top // common, bottom // common


def misled_by_the_count(
    hours: "list[int] | tuple[int, ...]",
    values: "list[int] | tuple[int, ...]",
    line: int,
    fine: bool = False,
) -> bool:
    """M3's second question: whether one count over every hour would mislead.

    THE LANE'S SKEPTIC, item 7: where how a body falls on a field depends
    on the hour, a published census is drawn the same in every hour, and
    withholding it draws the field flat. Mornings 70 per cent on :00 or :30
    beside afternoons at 40 came back at 52.5 and 54.9 published and at 4.6
    and 4.4 withheld -- closer published in both -- while night charting on
    the hour beside day entries at any minute came back with its days at 42
    per cent on :00 published, against 1.8 real and 1.1 withheld. So M3
    withholds only where some HOUR GROUP -- a row of `depends_on_the_hour`'s
    table (`_hour_table`), holding at least the census `line` of cells --
    lies FARTHER from the field's published shares than from a flat field's,
    distance the total variation over the table's columns, coarse or
    `fine` as `depends_on_the_hour` asks them (a flat field gives a column
    of w values w sixtieths). Asked in whole numbers. `hours` and `values`
    as `depends_on_the_hour` reads them, the cells at a published midnight
    already left out.

    Guarantees: a function of the four. Raises nothing. No I/O.
    """
    table, widths = _hour_table(hours, values, line, fine)
    if not table:
        return False
    total = len(values)
    columns = len(widths)
    sums = [sum(table[row][column] for row in range(len(table))) for column in range(columns)]
    for row in range(len(table)):
        size = sum(table[row])
        if size < line:
            continue
        # Both distances times size * total * 60, in whole numbers.
        published = sum(
            abs(FIELD_VALUES * total * table[row][column] - FIELD_VALUES * size * sums[column])
            for column in range(columns)
        )
        drawn_flat = sum(
            abs(FIELD_VALUES * total * table[row][column] - total * size * widths[column])
            for column in range(columns)
        )
        if published > drawn_flat:
            return True
    return False


def _count_at_zero(
    census: "tuple[tuple[int, int, int], ...] | list[tuple[int, int, int]]",
    heaps: "tuple[tuple[int, int], ...] | list[tuple[int, int]]",
) -> int:
    """The cells a field's published facts place on its value 0 for certain:
    the heap at 0, or a census group of value 0 alone; nought elsewhere."""
    for value, count in heaps:
        if value == 0:
            return count
    for first, last, count in census:
        if first == 0 and last == 0:
            return count
    return 0


def body_sure_at_midnight(
    hour_census: "tuple[tuple[int, int, int], ...] | list[tuple[int, int, int]]",
    minute: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    second: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    precision: str,
    body: int,
) -> int:
    """How many body cells the clock's published facts put at midnight for
    certain (method G7.3b step 7; the Codex review of landing 3b.4, item 4).

    Hour 0's count where the hour census counts it alone, less the body's
    cells off minute 0 -- its `body` less the minute's count at 0
    (`_count_at_zero`) -- and less those off second 0, none on a column
    written to the minute; nought where that is below nought, on a column
    written finer than the second, or where hour 0 is counted with other
    hours. `minute` and `second` are each field's (census, heaps).
    Guarantees: a function of the five. Raises nothing. No I/O.
    """
    if precision not in ("minute", "second"):
        return 0
    hour_zero = 0
    for first, last, count in hour_census:
        if first == 0 and last == 0:
            hour_zero = count
    on_minute = _count_at_zero(minute[0], minute[1])
    on_second = body if precision == "minute" else _count_at_zero(second[0], second[1])
    return max(0, hour_zero - (body - on_minute) - (body - on_second))


def end_stepped_off(
    distance: int,
    boundary: int,
    low_side: bool,
    holes: "dict[int, bool]",
    unit_seconds: int,
    off_midnight: bool,
) -> int:
    """A tail's END, its outermost word-less rank (G7.3b step 7), stepped
    inward off every unit a hole names and, `off_midnight`, every unit
    written at midnight -- `boundary` and the units in tail units of
    `unit_seconds` seconds, a midnight a unit whose seconds a day divides.
    Never below one. Read alike by the generator's construction and the
    checker's window (the Codex review of landing 3b.4, item 4: a column on
    the hour whose high tail ended at 2024-12-31 00:00 held one midnight
    more than its published count left the tails, and its body's heap at
    minute 0 came back one short at every seed). Raises nothing. No I/O.
    """
    while distance > 1:
        unit = boundary - distance if low_side else boundary + distance
        if unit in holes:
            distance = distance - 1
            continue
        if off_midnight and (unit * unit_seconds) % DAY_SECONDS == 0:
            distance = distance - 1
            continue
        break
    return distance


def tail_end_at_midnight(distance: int, boundary: int, low_side: bool, unit_seconds: int) -> bool:
    """Whether a tail's END at `distance` units from `boundary` is written at
    midnight (`end_stepped_off`'s test). Raises nothing. No I/O."""
    unit = boundary - distance if low_side else boundary + distance
    return (unit * unit_seconds) % DAY_SECONDS == 0


def tail_ends_midnight_room(
    counted: int,
    forced: int,
    listed: "list[tuple[int, tuple[str, ...] | None]]",
) -> int:
    """How many cells at midnight the published count at midnight leaves the tails'
    ENDS (method G7.3b step 7; the Codex review of landing 3b.4, item 4):
    `counted` less the body's cells at midnight for certain (`forced`,
    `body_sure_at_midnight`) and less the rows each tail listing its values
    holds at midnight for certain -- all its rows where every listed value
    is a midnight, else one for each that is; a midnight any value written
    `00:00:00`, as `midnight_sure` reads it (the verifier's item 11 on the
    Codex round of landing 3b.4: asked as nought seconds from 1970, only
    the epoch counted, and a low tail listing 2024-06-01 00:00:00 left the
    high tail's END at a midnight the count had already spent). `listed` is
    each tail's rows and listed values, None where it lists none. May be
    below nought. Raises nothing. No I/O."""
    left = counted - forced
    for rows, values in listed:
        if values is None:
            continue
        at = [value for value in values if value[11:19] == "00:00:00"]
        left = left - (rows if values and len(at) == len(values) else len(at))
    return left


def common_divisor(first: int, second: int) -> int:
    """The greatest common divisor of two whole numbers, by Euclid's rule
    (the offline scan admits no divisor helper of the math module); nought's
    with a number is the number. Raises nothing. No I/O."""
    first = abs(first)
    second = abs(second)
    while second:
        first, second = second, first % second
    return first


def field_heaps(
    bins: "list[int]", sure: "list[int]", line: int, units: "list[int]"
) -> "tuple[tuple[int, int], ...]":
    """A field's HEAPS: every value standing out (`calendar_rules.standing_out`
    with the median of `FIELD_REACH` values each side, on the cycle of
    sixty), with its count, kept only where its count holds its sure cells
    and what is left is nought or at least the line (MH1, SH1), and where
    its cells are written at no fewer than the line's different values
    (`units`, the different values written at each).

    A HEAP IS A VALUE OF THE CLOCK, NOT A FEW EVENTS (the builder's
    measurement of 2026-10-12): check-ins in bursts of one to six on one
    minute put 15 cells on minute 23 in three bursts, which stood out; the
    twin had to hold exactly 15 there, split its bursts to do it, and
    missed the column's count of different values. A minute standing out
    over fewer different values than the line is left to the census of
    the rest, which counts it with its neighbours.

    Guarantees: accepts the sixty counts, the sure cells, the census line
    and the sixty counts of different values; returns `(value, count)`
    ascending. Raises nothing. No I/O.
    """
    found: "list[tuple[int, int]]" = []
    for value, count in calendar_rules.standing_out(
        bins, line, FIELD_REACH, calendar_rules.CENTRE_MEDIAN, True
    ):
        held = sure[value] if value < len(sure) else 0
        if count < held or not calendar_rules.calendar_floor_ok(count - held, line):
            continue
        if value >= len(units) or units[value] < line:
            continue
        found += [(value, count)]
    return tuple(found)


# THE FEW-VALUES RULE OF A FIELD'S CENSUS (the builder's measurement of
# 2026-10-12, after D2's FEW UNITS): the census of the rest is published
# only where every non-empty group's cells are written at no fewer than
# `FEW_VALUES_LEAST` different values and at `FEW_VALUES_MEAN` on average.
FEW_VALUES_LEAST = 3
FEW_VALUES_MEAN = 8


def few_values(
    groups: "tuple[tuple[int, int, int], ...]",
    units: "list[int]",
    heaps: "tuple[tuple[int, int], ...]",
) -> bool:
    """Whether a field's census of the rest stands on too few different values.

    A census of exact counts over few different values is a census of a
    few events, not of the clock: check-ins in bursts of one to six on one
    minute published groups of 11 to 24 cells over 3 to 7 bursts each,
    which the twin met only by splitting its bursts, and its count of
    different values came back 1 to 14 long at every seed (the builder's
    measurement of 2026-10-12). Too few: a non-empty group whose cells off
    the heaps are written at fewer than `FEW_VALUES_LEAST` different
    values, or non-empty groups averaging fewer than `FEW_VALUES_MEAN`.

    Guarantees: accepts the groups, the different values at each value of
    the field and the heaps; returns the answer. Raises nothing. No I/O.
    """
    on_heaps = {value for value, _count in heaps}
    held: "list[int]" = []
    for first, last, count in groups:
        if count <= 0:
            continue
        held += [
            sum(units[value] for value in range(first, last + 1) if value not in on_heaps)
        ]
    if not held:
        return False
    return min(held) < FEW_VALUES_LEAST or sum(held) < FEW_VALUES_MEAN * len(held)


def off_midnight_short(
    groups: "tuple[tuple[int, int, int], ...]",
    heaps: "tuple[tuple[int, int], ...]",
    body: int,
    at_midnight: "int | None",
) -> bool:
    """Whether a field's counts away from value 0 could outrun its body's
    cells off a midnight (landing 3b.4, plan P4-D372).

    A published count at midnight is the column's, and its twin may stand
    every one of those cells between the two tail boundaries -- all but
    the rows of a tail whose every listed value is at midnight, which hold theirs there
    (rule 4, `midnight_sure`): its other tails draw their cells where
    their published distances put them, at any time of day. Its body is
    then sure of only `body` less that many cells off a midnight
    (`at_midnight`), and every cell at a midnight falls on value 0
    -- so the counts that do not hold value 0 (each heap on another
    value, and each group of the rest where 0 is a heap or lies outside
    it) must fit in those. A column of 989 days at midnight and 11 cells
    at 09:30, its tails holding 23 rows, published a heap of 11 on minute
    30 that its twins, their tails standing 5 of their cells off a
    midnight, met with 6 (the builder's measurement of 2026-10-12).

    Guarantees: accepts the groups, the heaps, the number of body cells
    and rule 4's count at midnight (`midnight_sure`), or None where none
    is published; returns the answer -- never True where it is None.
    Raises nothing. No I/O of any kind.
    """
    if at_midnight is None or at_midnight <= 0:
        return False
    sure = body - min(at_midnight, body)
    zero_heaped = False
    asked = 0
    for value, count in heaps:
        if value == 0:
            zero_heaped = True
        else:
            asked = asked + count
    for first, last, count in groups:
        if zero_heaped or not first <= 0 <= last:
            asked = asked + count
    return asked > sure


def field_off_the_heaps(
    counts: "list[int]", heaps: "tuple[tuple[int, int], ...] | list[tuple[int, int]]"
) -> "list[int]":
    """Sixty counts with every heap's value set to nought: what the census
    counts beside the heaps, of the cells or of the sure cells alike."""
    left = [count for count in counts]
    for value, _count in heaps:
        left[value] = 0
    return left


def field_groups(
    bins: "list[int]", sure: "list[int]", line: int
) -> "tuple[tuple[int, int, int], ...]":
    """A field's census groups, or none: the one merge rule over sixty
    values on a line (`calendar_rules.merged_groups`), the counts and the
    sure cells handed in already off the heaps (`field_off_the_heaps`)."""
    return calendar_rules.merged_groups(bins, sure, line, False)


def field_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    body: int,
    line: int,
    sure: "list[int]",
    field: str,
) -> "tuple[str, str, str] | None":
    """A published census of a field held to MC1/SE1, MC2/SE2, MC3/SE3's
    total and MC5/SE5, or None: THE ONE CHECK THE PRODUCER AND THE LOADER
    BOTH ASK (`calendar_rules.census_breach`), over values 0 to 59 on a
    line. `body` is the body less the heaps' cells and `sure` is off the
    heaps. Raises nothing. No I/O of any kind."""
    return calendar_rules.census_breach(
        groups, FIELD_VALUES, line, body, tuple(sure), False, 0, field,
        FIELD_RULES[field],
    )


def heaps_breach(
    heaps: "tuple[tuple[int, int], ...]",
    body: int,
    line: int,
    sure: "list[int]",
    field: str,
    census: bool,
) -> "tuple[str, str, str] | None":
    """A field's published heaps held to MH1/SH1 and MH2/SH2, or None.

    MH1: each heap is a value 0 to 59, after the one before it, counting
    at least the line, at least its sure cells, and what is left of it
    nought or at least the line. MH2: the heaps hold no more than the
    body -- exactly the body where no census stands beside them and no
    value off the heaps is left: the census's own total (MC3) asks the
    rest where one stands. Raises nothing. No I/O.
    """
    first_rule, second_rule = FIELD_HEAP_RULES[field]
    previous = -1
    total = 0
    for value, count in heaps:
        if value <= previous or not 0 <= value < FIELD_VALUES:
            return (
                first_rule,
                f"a heap stands at {field} {value}",
                f"each heap is a {field} from 0 to 59, after the one before it",
            )
        held = sure[value] if value < len(sure) else 0
        if count < line or count < held or not calendar_rules.calendar_floor_ok(
            count - held, line
        ):
            return (
                first_rule,
                f"the heap at {field} {value} counts {count}",
                f"a heap counts at least {line} and at least the {held} values "
                f"the rest of the description places there, and what is left "
                f"is nought or at least {line}",
            )
        previous = value
        total = total + count
    if total > body:
        return (
            second_rule,
            f"the heaps count {total} values",
            f"the values between the two tail boundaries number {body}",
        )
    return None


def span_long_enough_for(p25: "int | None", p75: "int | None", field: str) -> bool:
    """MC4 and SE4: whether the published middle half spans four hours (a
    minute census) or four minutes (a second census). A rung withheld
    publishes no span. Raises nothing. No I/O."""
    if p25 is None or p75 is None:
        return False
    return p75 - p25 >= FIELD_SPAN_SECONDS[field]


def field_lattice(
    census: "tuple[tuple[int, int, int], ...]",
    heaps: "tuple[tuple[int, int], ...]",
    published: "list[int]",
    body: int,
    line: int,
) -> int:
    """The LATTICE a field's published facts pin the body to, or nought.

    METHOD G7.3's DRAWING RULE (landing 3b.4; the design's construction
    rule, widened by its skeptic's M2 and m2). Where the field publishes
    heaps and no census beside them, and the rest -- the `body` cells off
    the heaps -- is fewer than the census `line`, so it could only have
    been one group the merge rule withholds, every body cell but those few
    stands on a heap, and the lattice is the greatest step dividing sixty
    and every heap's value -- sixty where the one heap is 0, thirty for a
    half-hour grid, fifteen for quarter hours. A REST OF THE LINE OR MORE
    IS A CENSUS WITHHELD, NOT A FEW STRAYS (the lane's skeptic, item 2):
    check-ins in bursts, a third of them off their heaps at 0 and 30, their
    census withheld for its few values, were drawn on half hours and the
    pass piled that third on :01 and :29, 15 to 24 per cent of every cell
    against 1.2 to 1.8 real; so there, and where the body is not known
    (below nought), it pins nothing. Where it publishes a census and no
    heap, the lattice is sixty -- every cell on value 0 -- only where the
    census's one non-zero group holds 0 and every value the description
    publishes in the body stands on 0. Anything else pins nothing: nought.

    Guarantees: accepts the census, the heaps, the field's value of each
    published body value, the body's cells and the census line; returns 0
    or a divisor of sixty. Raises nothing. No I/O.
    """
    if heaps and not census:
        if body < 0 or body - sum(count for _value, count in heaps) >= line:
            return 0
        step = FIELD_VALUES
        for value, _count in heaps:
            step = common_divisor(step, value)
        return step
    if census and not heaps:
        holding = [group for group in census if group[2] > 0]
        if len(holding) != 1 or holding[0][0] != 0:
            return 0
        for value in published:
            if value != 0:
                return 0
        return FIELD_VALUES
    return 0


def drawing_unit(
    precision: str,
    minute_facts: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    second_facts: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    published: "list[str]",
    body: int,
    line: int,
) -> int:
    """How many seconds one body draw of a column of moments steps in (G7.3).

    One -- every draw as before -- unless a minute or second census or
    heap is published. Then the seconds are pinned where the column is
    written to the minute, or where the second's facts pin a lattice
    (`field_lattice`); a lattice finer than the minute is the unit. With
    the seconds on 0, the minute's own lattice widens it: sixty seconds
    times the minutes' step, the hour for a column every cell of which is
    on the hour (the design: on the hour at 10,000 rows met its minute
    census 1 time in 3 drawn in minutes and 3 in 3 drawn in hours), half
    an hour for a half-hour grid (its skeptic's m2: missed 2 in 3 drawn in
    minutes, met 6 in 6 at thirty). A column written to the minute whose
    minute pins nothing keeps one, its written unit already the minute.

    Guarantees: accepts the precision, each field's census and heaps,
    every published body value's canonical text, the body's cells (below
    nought where not known) and the census line (`field_lattice`); returns
    a divisor of 3,600 of one or more. Raises nothing. No I/O.
    """
    minute_census, minute_heaps = minute_facts
    second_census, second_heaps = second_facts
    if not (minute_census or minute_heaps or second_census or second_heaps):
        return 1
    seconds = FIELD_VALUES
    if precision != "minute":
        seconds = field_lattice(
            second_census,
            second_heaps,
            [written_second(value) for value in published],
            body,
            line,
        )
    if seconds <= 0:
        return 1
    if seconds < FIELD_VALUES:
        return seconds
    minutes = field_lattice(
        minute_census, minute_heaps, [written_minute(value) for value in published], body, line
    )
    if minutes <= 0:
        return 1 if precision == "minute" else FIELD_VALUES
    return FIELD_VALUES * minutes


def phased_field_lattice(
    census: "tuple[tuple[int, int, int], ...]",
    heaps: "tuple[tuple[int, int], ...]",
    published: "list[int]",
    body: int,
    line: int,
) -> int:
    """The LATTICE a field's published facts pin the body to AT ITS OWN PHASE, or nought.

    Lane J3 (plan P4-D391): `field_lattice` reads the lattice as it stands
    on value 0 -- the greatest step dividing sixty and every heap's value
    --, so stamps five minutes apart from 07:13, heaps at 3, 8, ..., 58,
    pin a step of one minute there, though every body cell stands on a
    five-minute lattice three minutes off the hour. Here the step divides
    sixty and every DIFFERENCE between two heaps' values: five for those
    heaps, thirty for heaps at 15 and 45, sixty for one heap at any value.
    Under the same conditions as `field_lattice` (heaps beside no census
    and a rest below the census `line`); a census and no heap pins sixty
    where its one non-zero group holds every value the description
    publishes in the body and those values are one. Anything else: nought.
    A multiple of `field_lattice`'s step wherever that pins one, as every
    heap's value is a multiple of it.

    Guarantees: accepts what `field_lattice` accepts; returns 0 or a
    divisor of sixty. Raises nothing. No I/O.
    """
    if heaps and not census:
        if body < 0 or body - sum(count for _value, count in heaps) >= line:
            return 0
        step = FIELD_VALUES
        first = heaps[0][0]
        for value, _count in heaps:
            step = common_divisor(step, value - first)
        return step
    if census and not heaps:
        holding = [group for group in census if group[2] > 0]
        if len(holding) != 1:
            return 0
        written = published[0] if published else holding[0][0]
        if not holding[0][0] <= written <= holding[0][1]:
            return 0
        for value in published:
            if value != written:
                return 0
        return FIELD_VALUES
    return 0


def crowding_unit(
    precision: str,
    minute_facts: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    second_facts: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int], ...]]",
    published: "list[str]",
    body: int,
    line: int,
) -> int:
    """The lattice, in seconds, a column's clock facts pin its body to, at its own phase.

    Lane J3 (plan P4-D391): `drawing_unit` read through
    `phased_field_lattice`, the lattice the crowded rule
    (`lattice_crowded`) counts its points on. Equal to `drawing_unit`
    wherever the lattice stands on midnight; above it where the facts pin
    a lattice off midnight -- stamps five minutes apart from 07:13 or 00:37
    (300 here, 60 there), on the hour at 07:13:20 (3,600 here, 20 there)
    -- which the body is drawn finer than.

    Guarantees: accepts what `drawing_unit` accepts; returns a divisor of
    3,600 of one or more. Raises nothing. No I/O.
    """
    minute_census, minute_heaps = minute_facts
    second_census, second_heaps = second_facts
    if not (minute_census or minute_heaps or second_census or second_heaps):
        return 1
    seconds = FIELD_VALUES
    if precision != "minute":
        seconds = phased_field_lattice(
            second_census,
            second_heaps,
            [written_second(value) for value in published],
            body,
            line,
        )
    if seconds <= 0:
        return 1
    if seconds < FIELD_VALUES:
        return seconds
    minutes = phased_field_lattice(
        minute_census, minute_heaps, [written_minute(value) for value in published], body, line
    )
    if minutes <= 0:
        return 1 if precision == "minute" else FIELD_VALUES
    return FIELD_VALUES * minutes


# THE SHARE OF A LATTICE'S POINTS a column's different values may fill
# before its minute and second facts are withheld (`lattice_crowded`), as
# a fraction: half; a third where every value is different, so no repeat
# can take up a collision.
CROWDED_SHARE = (1, 2)
CROWDED_SHARE_ALL_DIFFERENT = (1, 3)
# HOW FAR ABOVE A UNIFORM DRAW the different values must fill the lattice
# before they crowd it (`lattice_crowded`, lane J2's second skeptic, item
# 1): a twentieth of its points.
CROWDED_EXCESS = (1, 20)
# ...and a fifth where no value is written once -- every different value
# written at least twice --, the column's count at midnight is not
# published and it holds no more than `CROWDED_REPEATED_VALUES` different
# values (Codex's review of lane J2, item 2, its two verifiers and the
# orchestrator's ruling on the last): 80 % of 1,250, the smallest count of
# different values at which a grid with no value written once missed a fact
# in a sweep of such grids (stamps one to sixty minutes apart, each written
# exactly two, three or four times, 500 to 2,500 values). A grid some value
# of which is written once keeps the twentieth: with the fifth such grids
# missed their count at 1,000, 1,100 and 1,171 values.
CROWDED_EXCESS_REPEATED = (1, 5)
CROWDED_REPEATED_VALUES = 1000


def lattice_crowded(
    unit: int,
    low: int,
    high: int,
    distinct: int,
    all_different: bool = False,
    parsed: int = 0,
    midnight_counted: bool = True,
    none_once: bool = False,
    off_phase: bool = False,
) -> bool:
    """Whether a column's different values crowd the lattice its clock facts pin.

    METHOD G7.3's DRAWING RULE MEETS THE COUNT (lane J2's skeptic, item 1).
    `unit` is the lattice the minute's and second's facts would pin the
    body to (`drawing_unit`), `low` and `high` the two tail boundaries in
    seconds (`seconds_of`), `distinct` the column's count of different
    values and `all_different` whether every parsed cell is one. Where the
    unit is above one and the different values fill at least
    `CROWDED_SHARE` of the lattice's points from `low` to `high` -- at
    least `CROWDED_SHARE_ALL_DIFFERENT` where every value is different --
    the facts are crowded: drawn on the lattice the values collide, the count
    pass keeps them apart a second at a time, and the field passes, moving
    them back onto it, find too few free points inside their gaps -- a gap
    between two interpolated rungs of a regular series holds one rank
    more than lattice points -- so the lattice, the ladder and the count
    cannot all hold. Measured on stamps five minutes apart, every one
    different, at 1,000 rows: 998 values met the count drawn a second at a
    time; the minute's and the second's passes left 893. Every 10th of
    3,800 such stamps written twice (91 % of the points held) came back
    3,090 of 3,455; each point kept at random with chance one half, 3,751
    of 3,800, with chance 0.4, 3,798; with 0.35 and less, every value. A
    column with repeats takes collisions up in them: T2's grids on the
    hour and on half hours at 10,000 rows, 7,334 values filling more than
    a third of their points and less than half, meet their heaps.

    A DENSE GRID IS NOT A REGULAR SERIES (lane J2's second skeptic, item
    1). Where `parsed`, the column's count of parsed cells, is given, the
    values crowd the lattice only where they also fill it more than
    `parsed` cells drawn uniformly over its points would -- `distinct /
    points` at least `CROWDED_EXCESS` above `1 - (1 - 1 / points) **
    parsed`, about `1 - exp(-parsed / points)`.
    Random times on the hour, on 5-, 15- and 30-minute slots, and stamps
    written to the minute with seconds `:00`, 3,000 to 100,000 rows, fill
    half to nine tenths of their lattice yet stand within 0.01 of such a
    draw (-0.002 to 0.017) and meet their heaps -- 26 of 28 twins miss
    nothing at floors 11 and 36, against 7 % or less of their cells at
    second 0 with the facts withheld; every regular series measured
    stands 0.111 to 0.382 above it and stays withheld. `parsed` 0 asks the
    fill alone.

    A SMALL GRID NO VALUE OF WHICH IS WRITTEN ONCE, WITH NO COUNT AT
    MIDNIGHT, IS NOT CROWDED UNDER A FIFTH (Codex's review of lane J2, item
    2, its two verifiers and the orchestrator's ruling on the last). Where
    `none_once` -- every different value written at least twice; false
    where not known --, the column publishes no count at midnight
    (`midnight_counted` false) and it holds no more than
    `CROWDED_REPEATED_VALUES` different values, the excess must reach
    `CROWDED_EXCESS_REPEATED`. 1,000 stamps five minutes or a minute apart,
    each written twice, stand 0.144 above the draw, and with their facts
    their twins met the count and every heap at floors 11 and 36 (the
    twentieth had withheld them). Each looser bound measured published
    grids whose twins missed: none (from 5,000 rows written twice), 4,500
    rows (five minutes apart with a fifth of their values once, 2,431 to
    2,436 of 2,489 at floor 36), and 1,171 values with some written once (2
    minutes apart with about a third once, 999 of 1,000 and 1,096 of 1,100
    at floor 11; 10 minutes apart with a twentieth once, 1,169 of 1,171 at
    floor 36); the twentieth withholds these and meets.
    Swept with the fifth at any size over 276 grids with no value written
    once -- stamps 1, 2, 3, 5, 10, 15, 30 and 60 minutes apart, each written
    exactly two, three or four times, 500 to 2,500 values, and 60 more from
    800 to 1,200 values written twice, or twice or three times, floors 11
    and 36, three twins each (1,173 twins) -- every published twin of fewer
    than 1,250 values met all its facts, 261 of them published by the fifth
    alone at up to 1,000 values. At 1,250 the first missed: stamps five
    minutes apart written twice, the count at midnight withheld, in one twin
    at floor 11; at 2,500 values 2,457 to 2,464 at floor 36. (Written four
    times with a count at midnight, 5 to 30 minutes apart, 1,250 to 2,500
    values missed their count too, by 1 to 21 values at floor 11: they stand
    within a twentieth of the draw and publish under either rule.) The bound
    is 80 % of 1,250; 93 grids of 1,001 to 2,500 values that met their facts
    with the fifth withhold them. Above it, or with a value written once, the
    twentieth stands.
    Where a count at midnight is published the twin holds it exactly, and on
    a lattice its values fill the ranks there find no free place: written
    twice, 10,000 stamps five minutes apart came back 34 to 90 values short,
    4,000 ten minutes apart 53 to 56 short, 2,000 fifteen minutes apart and
    coarser off their count or their second's heap, 40,000 a minute apart
    off the second's heap in one twin of two, and 10,000 written three times
    five or sixty minutes apart off their count or their count at midnight
    -- so the twentieth stands there, as it does for a column every value of
    which is different, and from a fifth on (every second stamp written
    twice, 0.227 above, missed its count either way).

    Guarantees: a function of the arguments; raises nothing. No I/O.
    """
    if unit <= 1:
        return False
    if high < low:
        return False
    points = (high - low) // unit + 1
    share, whole = CROWDED_SHARE_ALL_DIFFERENT if all_different else CROWDED_SHARE
    if distinct * whole < points * share:
        return False
    if parsed <= 0:
        return True
    if none_once and (off_phase or (midnight_counted and distinct > CROWDED_REPEATED_VALUES)):
        return True
    above, over = CROWDED_EXCESS
    if (
        none_once
        and not all_different
        and not midnight_counted
        and not off_phase
        and distinct <= CROWDED_REPEATED_VALUES
    ):
        above, over = CROWDED_EXCESS_REPEATED
    # The share of the points `parsed` uniform draws fill, on average.
    drawn = 1.0 - (1.0 - 1.0 / points) ** parsed
    return distinct / points - drawn >= above / over

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


def absent_places(spellings: "tuple[str, ...] | list[str]", form: str) -> "tuple[int, ...]":
    """The places of a form's dial the table calls absent (method G7A.4b).

    Every spelling the table publishes among its absent cells -- a key of
    the column's own `missing_by_source` or of any other column's, since
    a declaration reaches the whole table and the checker reads it so --
    that reads as a time in the column's form, at the place it reads at,
    where the one spelling the form writes for that place is that absent
    spelling once both are trimmed and case-folded: a twin cell written
    there is one the column's own reader counts as no value. A body
    run's steps and a tail's distances leave these places out (the
    round-2 fix of landing 3b.5: `00:00` written for an unknown time
    beside a ten-minute grid came back on 21 rows of 20, and `12:00`
    beside an hourly one on 285 of 279).

    Guarantees: accepts the spellings and one of `parsing.CLOCK_FORMS`;
    returns each place once, ascending, every one below the form's
    capacity. Determinism: a function of the two. Raises ValueError for
    a form `parsing` does not know. No I/O of any kind.
    """
    found: "list[int]" = []
    for spelling in spellings:
        if not isinstance(spelling, str):
            continue
        body = parsing.trimmed(spelling)
        # The case of a marker the person typed need not be the form's:
        # `08:00 am` names the place the form writes `08:00 AM`.
        for text in (body, body.upper(), body.lower()):
            at = parsing.clock_ordinal(text, form)
            if at is None or at in found:
                continue
            if parsing.folded(parsing.clock_spelling(at, form)) == parsing.folded(spelling):
                found += [at]
    return tuple(sorted(found))


def _other_width_form(form: str) -> str:
    """The form one form's hour is written in at its other width (`h-mm` for `hh-mm`)."""
    style = parsing.clock_style_of(form)
    width = parsing.clock_hour_width(style)
    other = ("h" if width == "hh" else "hh") + parsing.clock_face(style)
    return parsing.clock_form_of(other, parsing.clock_step(form) == 1)


def absent_with_another_width(
    absent: "tuple[int, ...] | list[int]", form: str
) -> "tuple[int, ...]":
    """The absent places the hour's other width spells another way (method G7A.4b steps 1 and 2).

    Of the places `absent_places` gives, those whose hour shows a width --
    `0` to `9`, or `1` to `9` on a marked face -- so a present time can
    still have stood there in the table, written in the other width. A
    census group counting cells whose every step on no heap is an absent
    place counts present cells the table wrote on these so: its runs
    take these steps alone (`clock_body_blocks`), CC5 counts them as its
    room (`clock_group_reach`), and the twin writes them in that width
    (`present_spellings`); and so does a drawn tail whose every step
    beyond its boundary on no heap is an absent place
    (`absent_room_beyond`).

    Guarantees: accepts absent places and one of `parsing.CLOCK_FORMS`;
    returns those of them with another width's spelling, in the order
    given. Determinism: a function of the two. Raises ValueError for a
    form `parsing` does not know. No I/O of any kind.
    """
    other = _other_width_form(form)
    found: "list[int]" = []
    for at in absent:
        if parsing.clock_spelling(at, other) != parsing.clock_spelling(at, form):
            found += [at]
    return tuple(found)


def present_spellings(
    spellings: "tuple[str, ...] | list[str]",
    form: str,
    published: "tuple[int, ...] | list[int]",
) -> "dict[int, str]":
    """The places a present time is written off the form's own spelling, each with the spelling it is written in (method G7A.4).

    A place the table calls absent (`absent_places`) that the description
    stands present cells on -- a heap's value, a tail's boundary, a listed
    tail value, a published rung, such a place in a census group whose
    every step is an absent place (`absent_with_another_width`), or such
    a place beyond a drawn tail's boundary whose every step on no heap is
    an absent place (`absent_room_beyond`), `published` --
    held present cells in the table, and the form's own spelling of it is
    one the column's reader counts as no value. So those cells can only
    have shown the hour's OTHER width -- `0:00` in a column of `hh:mm`
    beside `00:00` declared missing -- the one other spelling that reader
    reads at that place (`parsing.clock_ordinal`). That is the spelling
    the source wrote, and the twin writes it (the owner's ruling of
    2026-09-15; the verification of the round-2 fix of landing 3b.5:
    every twin of such a column wrote every time at midnight `00:00`). A
    place whose hour shows no width -- `10` to `23`, and `12` on a marked
    face -- has no such spelling, and a place the description stands
    nothing present on is one no present cell of the table is known to
    have stood on: a drawn or a run's cell is kept off it (G7A.4b steps 1,
    2 and 4), never written in a spelling the table may not hold. Neither
    is mapped.

    Guarantees: accepts the spellings the table calls absent, one of
    `parsing.CLOCK_FORMS` and the places the description stands present
    cells on, in the form's unit; returns a map from each place both
    absent and published to the other width's spelling of it, which the
    form's reader reads there. Determinism: a function of the three.
    Raises ValueError for a form `parsing` does not know. No I/O of any
    kind.
    """
    other_form = _other_width_form(form)
    named: "dict[int, int]" = {at: 1 for at in published}
    found: "dict[int, str]" = {}
    for at in absent_places(spellings, form):
        written = parsing.clock_spelling(at, other_form)
        if at in named and written != parsing.clock_spelling(at, form):
            found[at] = written
    return found


def absent_beyond(
    absent: "tuple[int, ...]", boundary: int, low_side: bool, stride: int
) -> "list[int]":
    """The distances beyond a tail boundary an absent place stands at, on the step.

    In the form's own unit, ascending: each place of `absent_places`
    strictly below the low boundary or strictly above the high one, whose
    distance from it is a whole number of steps. A tail drawn through its
    shape takes these out of its draw beside its heaps' (method G7A.4b,
    step 1), so no drawn cell lands on one -- save those that are its
    room (`absent_room_beyond`).

    Guarantees: a function of the arguments. Raises nothing. No I/O.
    """
    found: "list[int]" = []
    for at in absent:
        distance = boundary - at if low_side else at - boundary
        if distance > 0 and distance % stride == 0:
            found += [distance]
    return sorted(found)


def absent_room_beyond(
    absent: "tuple[int, ...]",
    form: str,
    boundary: int,
    low_side: bool,
    stride: int,
    heaps: "list[int]",
) -> "list[int]":
    """The distances beyond a drawn tail's boundary its draw stands on although absent places name them (method G7A.4b step 1).

    A tail drawn through its shape skips its heaps' distances and the
    absent places' (`absent_beyond`) -- save where EVERY step beyond its
    boundary that is no heap's, on the step and out to the end of the
    dial, is an absent place. The rows its heaps leave stood on such a
    place in the table, present, so on one the hour's other width spells
    another way (`absent_with_another_width`), in that width -- as a
    census group's cells do on such places alone (step 2) -- and never on
    one whose hour shows no width, where no present cell can stand. So
    the places of the first kind are then the draw's room: CC5 counts
    them, the draw skips the heaps' distances and the second kind's
    alone, and the twin writes each cell it draws there in that width
    (`present_spellings`). Read off the absence alone, the loader
    refused the producer's own description of 70 `00:30` and one `0:00`
    beyond a low boundary at `01:00`, beside `00:00` declared missing, and
    the table had no twin at all (the third verification of the round-2
    fix of landing 3b.5); and of one `01:00 AM` beyond `2:00 AM`'s heap,
    beside `1:00 AM` and `12:00 AM` declared missing (that repair's own
    probe).

    Guarantees: accepts the absent places (`absent_places`), one of
    `parsing.CLOCK_FORMS`, the boundary's ordinal and side, the step and
    the heaps' distances beyond the boundary, both in the form's unit;
    returns the distances of the absent places of the first kind in that
    unit, ascending -- none where a step beyond the boundary on no heap
    is no absent place, and none where no step is of that kind.
    Determinism: a function of the arguments. Raises ValueError for a
    form `parsing` does not know. No I/O of any kind.
    """
    if not absent:
        return []
    top = parsing.CLOCK_CAPACITY[form] - 1
    edge = max(1, boundary if low_side else top - boundary) // stride
    heaped: "dict[int, int]" = {distance: 1 for distance in heaps}
    named: "dict[int, int]" = {at: 1 for at in absent}
    wide: "dict[int, int]" = {at: 1 for at in absent_with_another_width(absent, form)}
    room: "list[int]" = []
    for steps in range(1, edge + 1):
        distance = steps * stride
        if distance in heaped:
            continue
        at = boundary - distance if low_side else boundary + distance
        if at in wide:
            room += [distance]
        elif at not in named:
            return []
    return room


def clock_group_reach(
    groups: "list[tuple[int, int, int]] | tuple[tuple[int, int, int], ...]",
    form: str,
    stride: int,
    body: "tuple[int, int]",
    heaps: "list[int]",
    absent: "tuple[int, ...]" = (),
) -> "list[int]":
    """How many steps of each group lie in the body, on no heap and on no
    place the column calls absent (CC5).

    The steps `clock_body_blocks` shares a group's count over: a group
    counting cells with none of them left is refused at load (the round-2
    fix of landing 3b.5), where the generator would stop on an internal
    error. A group whose every step on no heap is an absent place counts
    those of them the hour's other width spells another way
    (`absent_with_another_width`), as its runs do: they hold the present
    cells the table wrote there in that width, and none stands on one
    whose hour shows no width (the third verification of that fix).

    Guarantees: accepts the groups, the form, the step in the form's
    units, the body's two ends, the heaps' ordinals and the absent places
    (`absent_places`); returns one count per group. Determinism: a
    function of the arguments. Raises nothing.
    """
    heaped: "set[int]" = set(heaps)
    wide = absent_with_another_width(absent, form)
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
        free = units
        narrow = 0
        for at in absent:
            if span[0] <= at <= span[1] and at % stride == 0 and at not in heaped:
                units = units - 1
                if at not in wide:
                    narrow = narrow + 1
        # A GROUP WHOSE EVERY STEP ON NO HEAP IS AN ABSENT PLACE holds the
        # present cells the table wrote on those the other width spells
        # another way, in that width, as its runs do (`clock_body_blocks`).
        if units < 1:
            units = free - narrow
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
    absent: "tuple[int, ...]" = (),
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

    A STEP THE COLUMN CALLS ABSENT IS NO STEP OF A RUN'S SHARE (the
    round-2 fix of landing 3b.5): `absent` are the places of
    `absent_places`, and a run's units count only its other steps, so a
    run whose every step is absent takes no cell. Counted, an hourly
    grid's run holding nothing but `12:00`, written for an unknown time,
    took six cells no rank could move off it, and the twin wrote 285
    `12:00` where the table wrote 279. Save one group: where EVERY step
    of a group counting cells is an absent place, the table held those
    cells, present, on the ones the hour's other width spells another way
    (`absent_with_another_width`), in that width, and its runs take those
    steps alone.

    Guarantees: accepts the parsed count, the two tails' rows or None,
    the body's two ends, the census, the heaps as ordinals, the form,
    the step in the form's units and the absent places; returns the
    stretches, or None where the counts do not add up to the body or a
    group counting cells has no step to hold them -- which a description
    the loader accepted never is (CC3, CC5). Determinism: a function of
    the arguments. Raises nothing. No I/O of any kind.
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
            units = [
                (stop - begin) // stride
                + 1
                - len([at for at in absent if begin <= at <= stop and (at - begin) % stride == 0])
                for begin, stop in runs
            ]
            total = sum(units)
            if total < 1:
                # A GROUP WHOSE EVERY STEP IS AN ABSENT PLACE counts present
                # cells the table wrote on those the other width spells
                # another way, in that width (the verification of the
                # round-2 fix, and its third for a group beside a place
                # whose hour shows no width): its runs take those steps
                # alone, and the twin writes their cells so
                # (`present_spellings`). Read off the absence alone, CC5
                # refused the producer's own description of 20 `1:15`
                # beside `01:15` declared missing.
                wide = absent_with_another_width(absent, form)
                units = [
                    len([at for at in range(begin, stop + 1, stride) if at in wide])
                    for begin, stop in runs
                ]
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
    absent: "tuple[int, ...]" = (),
) -> "tuple[list[int], list[int]] | None":
    """The window every rank of a census-laid clock column stands in (G12.10).

    A tail rank anywhere beyond its boundary; a boundary rank on its
    boundary; every other body rank inside its census GROUP's steps in the
    body -- the group's, not its run's, so a real column whose rung stands
    on the far side of a heap from where the twin's share put it is still
    inside. Ordinals in the form's own unit.

    Guarantees: as `clock_body_blocks`, whose stretches it reads over the
    same absent places; None where that is None. Determinism: a function
    of the arguments. Raises nothing. No I/O of any kind.
    """
    blocks = clock_body_blocks(parsed, tails, body, groups, heaps, form, stride, absent)
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


def off_the_heaps(distance: int, heaps: "list[int] | tuple[int, ...]") -> int:
    """The `distance`-th distance beyond a boundary that is no heap's.

    A tail's cells on no heap are drawn through its shape in a space with
    the heaps' distances taken out, and read back here, so no such cell
    lands on a heap and every heap's count stays its own (method G7A.4b).
    `heaps` are the heaps' distances, ascending, each once -- beside them,
    since the round-2 fix of landing 3b.5, the distances of the places the
    column calls absent (`absent_beyond`), so no drawn cell lands on one,
    save those that are the draw's room (`absent_room_beyond`).

    Guarantees: accepts a whole distance of at least one and the
    distances to pass; returns a whole distance at least as large, on
    none of them, and strictly increasing in `distance`. Raises nothing.
    No I/O.
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
# anchor 3b-R2a (P4-D383)
# anchor 3b-R2b (P4-D383)
# anchor 3b-R2c (P4-D383)
# anchor 3b-R4 (P4-D384)

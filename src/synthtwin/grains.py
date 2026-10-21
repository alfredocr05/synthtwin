"""Dates and times beside a person column, pooled in people (lane PS, plan P4-D417).

THE DEFECT THIS CLOSES (measured at batch 4e's integration). Plan P4-D406
counts every point a column of dates or times publishes in PEOPLE, and a
column one of whose points one to ten people hold was held WHOLE: its twin
wrote made-up figures in the date's layout (`4191-54-63`, `77:21`), so code
that parses the column failed on the twin. A patient key beside timestamps
is almost every real EHR table.

TWO THINGS, in this order.

THE G1 FLOOR, NEVER FAILING. A held column of dates, stamps, clock times or
counted dates keeps its record (`time_grain`, rung `held`) of how its cells
are read, and its twin writes VALID values in each of the column's own
layouts (`filled`): days that exist, clock times inside the day, the
fraction's own figures, counts from the member's own epoch, offsets as
written. They are drawn inside the deepest span the record publishes, every
end of which at least the floor's number of people hold, or, where it
publishes none, inside the fixed span `FIXED_FIRST` to `FIXED_LAST` (a
clock: the whole day). Never from the table.

POOLING IN PEOPLE. A column that would publish a point one to ten people
hold is described at a coarser calendar GRAIN instead: each cell is written
as the start of its bucket (`coarse_cell`) in its own form, and the column
of those cells is described as any column is, so every rule of the
description holds it and every published point is a bucket. The ladder of each
kind, coarsest first: dates year, quarter, month, day; stamps the same and then
hour, minute, second; clock times a block of `BLOCK_HOURS` hours, hour,
minute, second. A counted date climbs the dates' or the stamps' ladder by
the precision its counts carry.

THE WALK (`ladder_walk`). At each rung the SPAN is the first and the last
bucket at least the floor's number of people hold, under every subject
column; the walk starts at the top rung and goes one rung finer while the
finer rung has a span that reaches both ends of the coarser one (its first
bucket inside the coarser first, its last inside the coarser last) and the
column's ESTIMATE of its people's visits -- the whole square root of its
present rows (`rows`, the block's own `n_present`) times the people the
subject column names (`people`, the population the description counts) --
is at least `ROWS_A_BUCKET` floors for every bucket of that finer SPAN
(repair round 1: the finer rung's own span, so a short session reaches a
fine rung inside a long coarse bucket).
The estimate lies between the people, each in one bucket, and the rows,
each in its own, so neither a table of a few rows a person nor one of many
on a visit day leads the walk far astray. The rows before the first bucket
of the chosen rung and after its last are counted in those two (the TAILS
POOLED).

THE STEP BACK (plan P4-D417 as amended in repair round 1). The description
at the rung the walk reached is used only where it publishes no count one
to ten people hold: every bucket inside its span holds nobody or the
floor's number of people (`thin`), the cells that read as no moment hold
nobody or the floor (they are one published count, `n_unparsed`), and so
does each written member a joint column's `resolution_mix` counts. Where it
would, the walk steps back one rung -- the record keeping the spans down to
that rung and no finer -- and asks again, up to the top; where no rung
serves, the column is HELD as plan P4-D406 holds it, with the G1 floor
above and every span the walk passed. A record says nothing of why the
walk stopped where it did: the loader (`walk_holds`) checks that each span
is one the walk could enter and that the rung is the last span's, and the
plan's proof shows that the one fact a stop publishes -- the column is not
described finer -- fixes no count of one to ten people.

THE TWIN draws each value uniformly inside the bucket its coarse cell names
(`drawn_inside`), at the column's own precision, and writes it in the
cell's own form; the validator reads the grain and describes a checked
file's cells at it (`coarse_cell`), so the real table meets its own
description and the twin meets it too.

Nothing here reads a file, draws a word or keeps state: the words are drawn
where the generator is made, and handed in. No I/O of any kind.
"""

import dataclasses

from synthtwin import date_counts, parsing

# -- what a column holds, and how its cells are read ---------------------

DATE = "date"
STAMP = "stamp"
CLOCK = "clock"
COUNTED = "counted"
KINDS = (DATE, STAMP, CLOCK, COUNTED)

# -- the rungs ----------------------------------------------------------

YEAR = "year"
QUARTER = "quarter"
MONTH = "month"
DAY = "day"
BLOCK = "four hours"
HOUR = "hour"
MINUTE = "minute"
SECOND = "second"
# The record of a column held whole (plan P4-D406) whose twin writes valid
# values by the G1 floor.
HELD = "held"
RUNGS = (YEAR, QUARTER, MONTH, DAY, BLOCK, HOUR, MINUTE, SECOND)
# Each rung's place, coarsest first.
RANK = {YEAR: 0, QUARTER: 1, MONTH: 2, DAY: 3, BLOCK: 4, HOUR: 5, MINUTE: 6, SECOND: 7}

# The hours one block of a clock holds: six blocks a day, from midnight.
BLOCK_HOURS = 4

# THE WALK'S ONE CONSTANT: the estimated visits a finer rung must hold, on
# average, in every bucket inside the current span, counted in floors. Two
# floors -- 22 a bucket at the default floor of 11 -- so a rung is entered
# only where a bucket of it would on average hold twice what its points
# need.
ROWS_A_BUCKET = 2

# THE FIXED SPAN the G1 floor draws from where nothing is published under
# the floor in people: 1 January 2000 to 31 December 2029, the method's own
# span, never the table's.
FIXED_FIRST = (2000, 1, 1)
FIXED_LAST = (2029, 12, 31)

_NS_SECOND = date_counts.SECOND
_NS_MINUTE = date_counts.MINUTE
_NS_HOUR = date_counts.HOUR
_NS_DAY = date_counts.DAY
_NS_BLOCK = BLOCK_HOURS * _NS_HOUR

_FIXED_LENGTHS = {
    SECOND: _NS_SECOND,
    MINUTE: _NS_MINUTE,
    HOUR: _NS_HOUR,
    BLOCK: _NS_BLOCK,
    DAY: _NS_DAY,
}

_DATE_LADDER = (YEAR, QUARTER, MONTH, DAY)
_STAMP_LADDER = (YEAR, QUARTER, MONTH, DAY, HOUR, MINUTE, SECOND)
_CLOCK_LADDER = (BLOCK, HOUR, MINUTE, SECOND)

_WORD_SPAN = 2**64


@dataclasses.dataclass(frozen=True)
class Reading:
    """How one column's cells are read: its kind and its member.

    ``member`` is the date member (`parsing.DATE_FORMATS`, or a layout) of
    a column of dates or stamps, the clock form of a column of clock times,
    and the counting member (`date_counts.MEMBERS`) of counted dates;
    ``mark`` the decimal mark counted dates are written with.
    """

    kind: str
    member: str
    mark: str = date_counts.POINT


@dataclasses.dataclass(frozen=True)
class Grain:
    """A column's `time_grain` record: its rung, its reading, and the spans its walk passed.

    ``spans`` holds, coarsest first, `(rung, first, last)`: the starts of the
    first and the last bucket at that rung that the floor's number of people
    hold, in nanoseconds from the start of 1 January 1970 (from midnight for
    a clock). ``rows`` is the column's present rows, its block's
    `n_present`, and ``people`` the people the subject columns name (the
    fewest, under several), which the walk reads. A held record's rung is `HELD`, and
    its spans are those its walk passed before it stopped (none where the
    top rung had no span, and none on a clock's, whose day is all its
    twin draws from).
    """

    rung: str
    reading: Reading
    rows: int
    spans: "tuple[tuple[str, int, int], ...]"
    # The column's own precision, the foot of its ladder.
    finest: str = DAY
    people: int = 0


# -- the ladder of each kind ---------------------------------------------


def ladder(kind: str, finest: str) -> "tuple[str, ...]":
    """The rungs of a kind's ladder, coarsest first, down to ``finest``."""
    rungs = _CLOCK_LADDER if kind == CLOCK else _STAMP_LADDER
    if kind == DATE:
        rungs = _DATE_LADDER
    found: "list[str]" = []
    for rung in rungs:
        found += [rung]
        if rung == finest:
            break
    return tuple(found)


def start_of(moment: int, rung: str) -> int:
    """The start of the bucket at ``rung`` that holds ``moment``."""
    if rung in _FIXED_LENGTHS:
        length = _FIXED_LENGTHS[rung]
        return (moment // length) * length
    year, month, _date = parsing.civil_from_days(moment // _NS_DAY)
    if rung == QUARTER:
        month = ((month - 1) // 3) * 3 + 1
    elif rung == YEAR:
        month = 1
    return parsing.days_from_civil(year, month, 1) * _NS_DAY


def after(start: int, rung: str) -> int:
    """The start of the bucket after the one starting at ``start``."""
    if rung in _FIXED_LENGTHS:
        return start + _FIXED_LENGTHS[rung]
    year, month, _date = parsing.civil_from_days(start // _NS_DAY)
    step = 1
    if rung == QUARTER:
        step = 3
    elif rung == YEAR:
        step = 12
    months = year * 12 + (month - 1) + step
    return parsing.days_from_civil(months // 12, months % 12 + 1, 1) * _NS_DAY


def buckets_between(first: int, end: int, rung: str) -> int:
    """How many buckets at ``rung`` start in ``first`` .. ``end`` - 1 (``first`` a bucket start)."""
    if end <= first:
        return 0
    if rung in _FIXED_LENGTHS:
        length = _FIXED_LENGTHS[rung]
        return (end - first + length - 1) // length
    year, month, _date = parsing.civil_from_days(first // _NS_DAY)
    last_year, last_month, _last = parsing.civil_from_days((end - 1) // _NS_DAY)
    months = (last_year * 12 + last_month) - (year * 12 + month) + 1
    if rung == QUARTER:
        return (last_year * 12 + last_month - 1) // 3 - (year * 12 + month - 1) // 3 + 1
    if rung == YEAR:
        return last_year - year + 1
    return months


def walk_holds(grain: Grain, floor: int) -> bool:
    """Whether a record's spans are a walk its own published facts allow (plan P4-D417, TG1).

    The spans run one a rung from the ladder's top, each a pair of bucket
    starts at its rung, first at most last, and each past the first one
    the walk could enter: it reaches both ends of the one before, and the
    estimate (`estimate`) is at least `ROWS_A_BUCKET` floors a bucket of
    it (`_goes_finer`). A held record stops at its last span or before any; a
    pooled one's rung is its last span's. Where the walk stopped -- for a
    finer span too wide, a finer rung with none, or a finer description
    that would publish a count one to ten people hold (the step back) -- is
    not checked: no published fact records it, which is what the plan's
    proof rests on. The ladder's foot is the record's own `finest`, the
    column's precision.
    """
    rungs = ladder(_ladder_kind(grain), grain.finest)
    if not rungs or rungs[len(rungs) - 1] != grain.finest:
        return False
    spans = grain.spans
    if len(spans) > len(rungs):
        return False
    visits = estimate(grain.rows, grain.people)
    for place in range(len(spans)):
        rung, first, last = spans[place]
        if rung != rungs[place] or first > last:
            return False
        if start_of(first, rung) != first or start_of(last, rung) != last:
            return False
        if place == 0:
            continue
        if not _goes_finer(visits, floor, spans[place - 1], spans[place]):
            return False
    if grain.rung == HELD:
        return True
    return bool(spans) and grain.rung == spans[len(spans) - 1][0]


def estimate(rows: int, people: int) -> int:
    """The visits the walk reads: the whole square root of the rows times the people.

    Whole-number arithmetic: the largest whole number whose square is at
    most the product, found by halving. Determinism: a function of the
    two. Raises nothing. No I/O.
    """
    product = rows * people
    if product <= 0:
        return 0
    low = 0
    high = product + 1
    while high - low > 1:
        middle = (low + high) // 2
        if middle * middle <= product:
            low = middle
        else:
            high = middle
    return low


def _ladder_kind(grain: Grain) -> str:
    """The ladder a record climbs: a counted date the dates' or the stamps', by its precision."""
    if grain.reading.kind == COUNTED and RANK[grain.finest] <= RANK[DAY]:
        return DATE
    return grain.reading.kind


def _goes_finer(
    visits: int, floor: int, outer: "tuple[str, int, int]", span: "tuple[str, int, int]"
) -> bool:
    """Whether the walk may enter a finer rung whose span is ``span`` from the span ``outer``.

    The finer span must REACH both ends of the one before -- its first
    bucket inside ``outer``'s first, its last inside ``outer``'s last -- so
    the tails it pools stay inside the end buckets the coarser rung
    already pools them into, and the estimate must be at least
    `ROWS_A_BUCKET` floors a bucket of the finer span ITSELF (repair round
    1, the statistics skeptic's item 2: a short session reaches a fine
    rung inside a long coarse bucket). Every bucket the decision reads is
    an end of a span, held by the floor's number of people, which the
    record publishes once the walk enters.
    """
    outer_rung, outer_first, outer_last = outer
    rung, first, last = span
    if start_of(first, outer_rung) != outer_first or start_of(last, outer_rung) != outer_last:
        return False
    return visits >= ROWS_A_BUCKET * floor * buckets_between(first, after(last, rung), rung)


def ladder_walk(
    visits: int,
    floor: int,
    finest: str,
    kind: str,
    ends: "dict[str, tuple[int, int] | None]",
) -> "tuple[str, tuple[tuple[str, int, int], ...]]":
    """The rung the walk reaches, or `HELD` where the top rung has no span, and the spans it passed.

    ``ends`` holds, for each rung of the ladder, the starts of the first
    and the last bucket the floor's number of people hold, or None where
    none does: the one place the people are counted. The walk goes one
    rung finer while that rung has a span the estimate covers
    (`_goes_finer`); the description it reaches may still step back
    (`walk_holds`, the profile's `_grain_walk`).
    """
    rungs = ladder(kind, finest)
    found = ends[rungs[0]] if rungs[0] in ends else None
    if found is None:
        return HELD, ()
    spans: "list[tuple[str, int, int]]" = [(rungs[0], found[0], found[1])]
    for place in range(1, len(rungs)):
        found = ends[rungs[place]] if rungs[place] in ends else None
        if found is None or not _goes_finer(
            visits, floor, spans[len(spans) - 1], (rungs[place], found[0], found[1])
        ):
            break
        spans += [(rungs[place], found[0], found[1])]
    return spans[len(spans) - 1][0], tuple(spans)


# -- the runs of a written cell -----------------------------------------

_DIGIT = 0
_LETTER = 1
_OTHER = 2


def _class_of(character: str) -> int:
    if "0" <= character <= "9":
        return _DIGIT
    if "a" <= character <= "z" or "A" <= character <= "Z":
        return _LETTER
    return _OTHER


def _runs(cell: str) -> "list[tuple[int, int, int]]":
    """Each maximal run of figures or letters, and each other character, as `(start, end, class)`."""
    found: "list[tuple[int, int, int]]" = []
    place = 0
    size = len(cell)
    while place < size:
        kind = _class_of(cell[place])
        end = place + 1
        if kind != _OTHER:
            while end < size and _class_of(cell[end]) == kind:
                end = end + 1
        found += [(place, end, kind)]
        place = end
    return found


def _date_order(member: str) -> "str | None":
    """The fields a member writes before its clock, in order, or None."""
    if member in ("iso-date", "iso-datetime", "slashed-iso-date",
                  "slashed-iso-datetime", "iso-mixed"):
        return "YMD"
    if member == "iso-month":
        return "YM"
    if member == "compact-date":
        return "C"
    if member == "year-quarter":
        return "YQ"
    if member == "textual-day-first-date":
        return "DNY"
    if member == "textual-month-first-date":
        return "NDY"
    if member in parsing.MONTH_FIRST_MEMBERS:
        return "MDY"
    if member in parsing.DAY_FIRST_MEMBERS:
        return "DMY"
    return None


# The layout fields this module writes, each as the field code it is: the
# year at four or two figures, the month and the day fixed or flexible, the
# hours of either dial, the minutes, the seconds and the fraction. A layout
# holding any other field (a weekday, a month name, the day of the year)
# is not rewritten, and its column is held whole as before.
_LAYOUT_CODES = {
    "YYYY": "Y", "YY": "Y", "YY1900": "Y", "YY1930": "Y", "YY1940": "Y",
    "MM": "M", "M": "M", "DD": "D", "D": "D",
    "HH": "h", "H": "h", "hh": "i", "h": "i", "MI": "m", "SS": "s", "F": "f",
}


def _fields(
    cell: str, reading: Reading, made_up: bool = False
) -> "list[tuple[str, int, int]] | None":
    """Each run of a cell that names a field, as `(code, start, end)`, or None.

    Assigned by the member's own order, never by the cell's values, so a
    made-up cell in the column's layout is read the same way: `Y` a year,
    `M` a month, `D` a day, `N` a month's name, `C` an eight-figure date,
    `Q` a quarter, `h` an hour of the 24-hour dial, `i` of the 12-hour,
    `m` minutes, `s` seconds, `f` a fraction, `P` a marker of the half of
    the day, `T` the letter joining a date to its clock, `Z` a zulu letter,
    `O` the figures of an offset. Every other run is kept as written.
    ``made_up``: the cell is a held column's made-up value, whose letters
    are any letters in the layout's places, so a letter run is read by
    where it stands rather than by what it spells.
    """
    runs = _runs(cell)
    order = ""
    clock = True
    if reading.kind == CLOCK:
        return _clock_fields(cell, runs, 0, [], made_up)
    if parsing.is_layout_name(reading.member):
        return _layout_fields(cell, runs, reading.member)
    else:
        found = _date_order(reading.member)
        if found is None:
            return None
        order = found
        clock = reading.kind == STAMP or reading.member in (
            "iso-datetime", "slashed-iso-datetime", "month-first-datetime",
            "day-first-datetime", "iso-mixed",
        )
    fields: "list[tuple[str, int, int]]" = []
    place = 0
    for code in order:
        want = _LETTER if code == "N" else _DIGIT
        if code == "Q":
            while place < len(runs) and runs[place][2] != _LETTER:
                place = place + 1
            place = place + 1
        while place < len(runs) and runs[place][2] != want:
            if runs[place][2] != _OTHER:
                return None
            place = place + 1
        if place >= len(runs):
            return None
        start, end, _kind = runs[place]
        fields += [(code, start, end)]
        place = place + 1
    if not clock:
        return fields if place >= len(runs) or _only_other(runs, place) else None
    return _clock_fields(cell, runs, place, fields, made_up)


def _only_other(runs: "list[tuple[int, int, int]]", place: int) -> bool:
    for one in runs[place:]:
        if one[2] != _OTHER:
            return False
    return True


def _clock_fields(
    cell: str,
    runs: "list[tuple[int, int, int]]",
    place: int,
    fields: "list[tuple[str, int, int]]",
    made_up: bool = False,
) -> "list[tuple[str, int, int]] | None":
    """The clock half of a cell: hours, minutes, seconds, fraction, marker, offset."""
    time_codes = "hms"
    taken = 0
    offset = False
    marked = False
    for start, end, kind in runs[place:]:
        before = cell[start - 1 : start] if start > 0 else ""
        if kind == _OTHER:
            continue
        if kind == _LETTER:
            word = parsing.folded(cell[start:end])
            if made_up:
                word = _letters_by_place(word, taken, cell[end : end + 1], before)
            if word in ("am", "pm") or (word in ("a", "p") and cell[end : end + 1] == "."):
                fields += [("P", start, end)]
                marked = True
            elif word == "m" and before == ".":
                fields += [("P", start, end)]
            elif word in ("t",) and taken == 0:
                fields += [("T", start, end)]
            elif word in ("z", "utc", "gmt") and taken > 0:
                fields += [("Z", start, end)]
            else:
                return None
            continue
        if offset or (taken >= 2 and before in ("+", "-")):
            offset = True
            fields += [("O", start, end)]
            continue
        if taken >= 2 and before in (".", ",") and taken <= 3:
            fields += [("f", start, end)]
            taken = 4
            continue
        if taken >= 3:
            return None
        fields += [(time_codes[taken], start, end)]
        taken = taken + 1
    if marked:
        fields = [("i", one[1], one[2]) if one[0] == "h" else one for one in fields]
    if taken == 1:
        return None
    return fields


def _letters_by_place(word: str, taken: int, after_it: str, before: str) -> str:
    """What a made-up letter run stands for, by where it stands in its layout."""
    if taken == 0 and len(word) == 1:
        return "t"
    if taken >= 2 and len(word) == 2:
        return "am"
    if taken >= 2 and len(word) == 1 and after_it == ".":
        return "a"
    if taken >= 2 and len(word) == 1 and before == ".":
        return "m"
    if taken >= 2 and len(word) == 1:
        return "z"
    if taken >= 2 and len(word) == 3:
        return "utc"
    return word


def _layout_fields(
    cell: str, runs: "list[tuple[int, int, int]]", member: str
) -> "list[tuple[str, int, int]] | None":
    """A layout's fields, by its own items, where every field is one this module writes."""
    items = parsing.layout_items(member)
    if items is None:
        return None
    codes: "list[str]" = []
    for kind, field in items:
        if kind != "f":
            continue
        bare = field[: len(field) - 1] if field[len(field) - 1 : len(field)] == "?" else field
        if bare not in _LAYOUT_CODES:
            return None
        codes += [_LAYOUT_CODES[bare]]
    fields: "list[tuple[str, int, int]]" = []
    taken = 0
    for start, end, sort in runs:
        if sort == _DIGIT:
            if taken >= len(codes):
                return None
            fields += [(codes[taken], start, end)]
            taken = taken + 1
        elif sort == _LETTER:
            word = parsing.folded(cell[start:end])
            if word == "t":
                fields += [("T", start, end)]
            else:
                return None
    return fields if taken == len(codes) else None


# -- reading a cell's moment --------------------------------------------


@dataclasses.dataclass(frozen=True)
class _Parts:
    year: int
    month: int
    day: int
    hour: int
    minute: int
    second: int
    nanos: int


def _parts_of(moment: int) -> _Parts:
    day = moment // _NS_DAY
    year, month, date = parsing.civil_from_days(day)
    rest = moment - day * _NS_DAY
    return _Parts(
        year, month, date, rest // _NS_HOUR, (rest // _NS_MINUTE) % 60,
        (rest // _NS_SECOND) % 60, rest % _NS_SECOND,
    )


def _fraction_of(cell: str, fields: "list[tuple[str, int, int]]") -> int:
    for code, start, end in fields:
        if code == "f":
            figures = cell[start:end]
            if len(figures) > 9:
                return -1
            return int(figures) * int(10 ** (9 - len(figures)))
    return 0


def moment_of(cell: str, reading: Reading) -> "int | None":
    """The moment a cell names, in nanoseconds from 1970 (from midnight for a clock), or None."""
    if not parsing.folded(cell):
        return None
    if reading.kind == CLOCK:
        if reading.member not in parsing.CLOCK_FORMS:
            return None
        ordinal = parsing.clock_ordinal(cell, reading.member)
        if ordinal is None:
            return None
        return ordinal * parsing.clock_step(reading.member) * _NS_SECOND
    if reading.kind == COUNTED:
        if reading.member not in date_counts.MEMBERS:
            return None
        written = date_counts.counted(reading.member, cell, reading.mark)
        if written is None:
            return None
        numerator, denominator = date_counts.exact_value(written)
        return date_counts.moment_of(
            reading.member, numerator, denominator, date_counts.NANOSECOND
        )
    read = parsing.parse_datetime(cell, reading.member)
    if read is None:
        return None
    canonical = read[0]
    fields = _fields(cell, reading)
    if len(canonical) == 7 and canonical[4:6] in ("-Q", "-q"):
        year = int(canonical[0:4])
        quarter = int(canonical[6:7])
        return parsing.days_from_civil(year, (quarter - 1) * 3 + 1, 1) * _NS_DAY
    year = int(canonical[0:4])
    month = int(canonical[5:7])
    date = int(canonical[8:10]) if len(canonical) >= 10 else 1
    moment = parsing.days_from_civil(year, month, date) * _NS_DAY
    if len(canonical) >= 19:
        moment = (
            moment
            + int(canonical[11:13]) * _NS_HOUR
            + int(canonical[14:16]) * _NS_MINUTE
            + int(canonical[17:19]) * _NS_SECOND
        )
        fraction = _fraction_of(cell, fields) if fields is not None else _trailing_fraction(cell)
        if fraction < 0:
            return None
        moment = moment + fraction
    return moment


def _trailing_fraction(cell: str) -> int:
    """A layout cell's fraction: its last run of figures after a point or a comma, in nanoseconds."""
    runs = _runs(cell)
    if not runs:
        return 0
    start, end, sort = runs[len(runs) - 1]
    if sort != _DIGIT or cell[start - 1 : start] not in (".", ",") or end - start > 9:
        return 0
    return int(cell[start:end]) * int(10 ** (9 - (end - start)))


def _ends_in_a_fraction(cell: str) -> bool:
    runs = _runs(cell)
    if not runs:
        return False
    start, _end, sort = runs[len(runs) - 1]
    return sort == _DIGIT and cell[start - 1 : start] in (".", ",")


def _layout_finest(member: str) -> str:
    """The finest field a layout writes: its rung."""
    items = parsing.layout_items(member)
    finest = DAY
    for kind, field in items if items is not None else ():
        bare = field[: len(field) - 1] if field[len(field) - 1 : len(field)] == "?" else field
        if kind != "f":
            continue
        if bare in ("SS", "F"):
            return SECOND
        if bare == "MI":
            finest = MINUTE
        elif bare in ("HH", "H", "_H", "hh", "h", "_h") and finest == DAY:
            finest = HOUR
    return finest


def finest_of(cell: str, reading: Reading) -> str:
    """The finest rung one cell writes: its own precision."""
    if reading.kind == CLOCK:
        return SECOND if parsing.clock_step(reading.member) == 1 else MINUTE
    if reading.kind == COUNTED:
        written = date_counts.counted(reading.member, cell, reading.mark)
        places = 0 if written is None else date_counts.figures_after_the_mark(written)
        step = int(date_counts.TABLE[reading.member].unit // 10 ** min(places, 9))
        return DAY if step >= _NS_DAY else SECOND
    if reading.member == "iso-month":
        return MONTH
    if reading.member == "year-quarter":
        return QUARTER
    fields = _fields(cell, reading)
    if fields is None:
        return _layout_finest(reading.member) if parsing.is_layout_name(reading.member) else DAY
    codes = ""
    for code, _start, _end in fields:
        codes = codes + code
    if "s" in codes or "f" in codes:
        return SECOND
    if "m" in codes:
        return MINUTE
    if "h" in codes or "i" in codes:
        return HOUR
    return DAY


def unit_of(cell: str, reading: Reading) -> int:
    """The smallest step one cell can write, in nanoseconds: what a draw inside a bucket steps by."""
    if reading.kind == CLOCK:
        return parsing.clock_step(reading.member) * _NS_SECOND
    if reading.kind == COUNTED:
        written = date_counts.counted(reading.member, cell, reading.mark)
        places = 0 if written is None else date_counts.figures_after_the_mark(written)
        unit = date_counts.TABLE[reading.member].unit
        step = int(unit // 10 ** min(places, 9))
        return max(step, 1)
    finest = finest_of(cell, reading)
    if finest == SECOND:
        fields = _fields(cell, reading)
        for code, start, end in fields if fields is not None else []:
            if code == "f":
                return int(10 ** max(9 - (end - start), 0))
        if fields is None and _trailing_fraction(cell + "") != 0 or (
            fields is None and _ends_in_a_fraction(cell)
        ):
            runs = _runs(cell)
            return int(10 ** max(9 - (runs[len(runs) - 1][1] - runs[len(runs) - 1][0]), 0))
        return _NS_SECOND
    if finest in _FIXED_LENGTHS:
        return _FIXED_LENGTHS[finest]
    return _NS_DAY


# -- writing a cell in its own form -------------------------------------


def _width_text(value: int, run: str, padded: bool) -> str:
    """One field's figures at the width its run shows, or the column's where it shows none."""
    if len(run) == 1:
        return f"{value}"
    if run[0:1] == "0" or padded:
        return f"{value:02d}"
    return f"{value}"


# THE FEW WORDS A REWRITTEN CELL SPELLS OF ITS OWN, each in the three cases
# a cell may write it in: small, capitals, and a first capital.
_CASED = {
    "am": ("am", "AM", "Am"),
    "pm": ("pm", "PM", "Pm"),
    "a": ("a", "A", "A"),
    "p": ("p", "P", "P"),
    "m": ("m", "M", "M"),
    "t": ("t", "T", "T"),
    "z": ("z", "Z", "Z"),
    "utc": ("utc", "UTC", "Utc"),
}


def _case_of(like: str) -> str:
    """How ``like`` is written: `upper`, `lower` or `title` (`parsing.NAME_CASES`)."""
    upper = True
    lower = True
    for character in like:
        if "a" <= character <= "z":
            upper = False
        if "A" <= character <= "Z":
            lower = False
    if upper:
        return "upper"
    if lower:
        return "lower"
    return "title"


def _cased(word: str, like: str) -> str:
    """One of this module's own words in the case ``like`` is written in."""
    found = _CASED[word]
    case = _case_of(like)
    if case == "upper":
        return found[1]
    if case == "lower":
        return found[0]
    return found[2]


def _month_name(month: int, like: str, exact: bool = False) -> "str | None":
    """A month's name written as ``like`` is: abbreviated where it has three letters, else in full.

    In its case; ``exact`` asks for the very length of ``like`` (a made-up
    name filling its layout), and None where this month's name has
    another.
    """
    case = _case_of(like)
    full = parsing.month_spelling(month, "full", case)
    short = parsing.month_spelling(month, "abbreviated", case)
    word = short if len(like) == len(short) else full
    if exact and len(word) != len(like):
        return None
    return word


def rewritten(cell: str, reading: Reading, moment: int, padded: bool = True) -> "str | None":
    """The cell written again in its own form, naming ``moment`` at its own precision, or None.

    A clock is written by `parsing.clock_spelling` in the column's form, a
    counted date by its member's count at the cell's own figures after the
    mark, and a date or stamp field by field over its own runs: each field
    at the width its run shows (``padded`` decides a run of two figures
    that shows none), a month's name at its length and case, the marker of
    the half of the day by the hour, every other character as written.
    None where the result does not read back as the moment.
    """
    if reading.kind == CLOCK:
        return _clock_written(reading, moment)
    if reading.kind == COUNTED:
        return _count_written(cell, reading, moment)
    fields = _fields(cell, reading)
    if fields is None:
        return _layout_written(cell, reading, moment, False)
    parts = _parts_of(moment)
    text = _filled_in(cell, fields, parts, padded, False)
    if text is None:
        return None
    if moment_of(text, reading) != moment - moment % unit_of(cell, reading):
        return None
    before = parsing.parse_datetime(cell, reading.member)
    again = parsing.parse_datetime(text, reading.member)
    if before is None or again is None or before[1] != again[1]:
        return None
    return text


# The width words a layout's flexible fields are written at, each tried in
# turn for the one that writes a cell in its own form.
_LAYOUT_WIDTHS = (
    parsing.WIDTH_PADDED,
    parsing.WIDTH_UNPADDED,
    parsing.WIDTH_FIRST_PADDED,
    parsing.WIDTH_SECOND_PADDED,
)


def _form_of(text: str) -> str:
    """A cell's form, as the layouts census reads one: a figure `9`, a letter `a` or `A`, the rest as written."""
    found = ""
    for character in text:
        if "0" <= character <= "9":
            found = found + "9"
        elif "a" <= character <= "z":
            found = found + "a"
        elif "A" <= character <= "Z":
            found = found + "A"
        else:
            found = found + character
    return found


def shape_of(text: str) -> str:
    """A cell's written shape, a figure `9` and a letter `a` or `A`: what tells a cell's written form apart."""
    return _form_of(text)


def _layout_written(cell: str, reading: Reading, moment: int, made_up: bool) -> "str | None":
    """A layout cell written by the layout's own writer (`parsing.written_layout_date`), or None.

    The moment's canonical text with the layout's clock where it has one,
    the cell's own offset (none for a made-up cell), its fraction's
    figures; the first width word that writes the cell's own form (a
    made-up cell: its very form) and reads back under the member.
    """
    if not parsing.is_layout_name(reading.member):
        return None
    parts = _parts_of(moment)
    canonical = f"{parts.year:04d}-{parts.month:02d}-{parts.day:02d}"
    if parsing.layout_has_clock(reading.member):
        canonical = f"{canonical} {parts.hour:02d}:{parts.minute:02d}:{parts.second:02d}"
    offset = ""
    if not made_up:
        read = parsing.parse_datetime(cell, reading.member)
        if read is None:
            return None
        offset = read[1]
    figures = 0
    runs = _runs(cell)
    if runs and runs[len(runs) - 1][2] == _DIGIT and cell[runs[len(runs) - 1][0] - 1 : runs[len(runs) - 1][0]] in (".", ","):
        figures = runs[len(runs) - 1][1] - runs[len(runs) - 1][0]
    shape = _form_of(cell)
    for width in _LAYOUT_WIDTHS:
        text = parsing.written_layout_date(reading.member, canonical, offset, width, figures)
        again = parsing.parse_datetime(text, reading.member)
        if again is None:
            continue
        if made_up and _form_of(text) != shape:
            continue
        if not made_up and again[1] != offset:
            continue
        return text
    return None


def _clock_written(reading: Reading, moment: int) -> "str | None":
    if reading.member not in parsing.CLOCK_FORMS:
        return None
    step = parsing.clock_step(reading.member)
    ordinal = (moment // _NS_SECOND) // step
    if ordinal < 0 or ordinal >= parsing.CLOCK_CAPACITY[reading.member]:
        return None
    return parsing.clock_spelling(ordinal, reading.member)


def _count_written(cell: str, reading: Reading, moment: int) -> "str | None":
    written = date_counts.counted(reading.member, cell, reading.mark)
    if written is None or date_counts.TABLE[reading.member].contacts:
        return None
    places = date_counts.figures_after_the_mark(written)
    found = date_counts.count_of(reading.member, moment, date_counts.NANOSECOND)
    if found is None:
        return None
    form = date_counts.CountForm(places, False, None, False, reading.mark, None)
    text = date_counts.spelled_count(found[0], found[1], form)
    if moment_of(text, reading) is None:
        return None
    return text


def _filled_in(
    cell: str,
    fields: "list[tuple[str, int, int]]",
    parts: _Parts,
    padded: bool,
    fill: bool,
) -> "str | None":
    """The cell with each field run written for ``parts``; ``fill`` also mends joints and offsets."""
    text = ""
    place = 0
    for code, start, end in fields:
        run = cell[start:end]
        text = text + cell[place:start]
        piece = run
        if code == "Y":
            piece = f"{parts.year:04d}" if len(run) == 4 else f"{parts.year % 100:02d}"
        elif code == "C":
            piece = f"{parts.year:04d}{parts.month:02d}{parts.day:02d}"
        elif code == "M":
            piece = _width_text(parts.month, run, padded)
        elif code == "D":
            piece = _width_text(parts.day, run, padded)
        elif code == "Q":
            piece = f"{(parts.month - 1) // 3 + 1}"
        elif code == "N":
            named = _month_name(parts.month, run, fill)
            if named is None:
                return None
            piece = named
        elif code == "h":
            piece = _width_text(parts.hour, run, padded)
        elif code == "i":
            piece = _width_text(parts.hour % 12 if parts.hour % 12 else 12, run, padded)
        elif code == "m":
            piece = f"{parts.minute:02d}"
        elif code == "s":
            piece = f"{parts.second:02d}"
        elif code == "f":
            piece = f"{parts.nanos // 10 ** (9 - len(run)):0{len(run)}d}" if len(run) <= 9 else run
        elif code == "P" and len(run) == 1 and cell[start - 1 : start] == ".":
            piece = _cased("m", run)
        elif code == "P":
            piece = _cased("pm" if parts.hour >= 12 else "am", run) if len(run) == 2 else (
                _cased("p" if parts.hour >= 12 else "a", run)
            )
        elif fill and code == "T":
            piece = _cased("t", run)
        elif fill and code == "Z":
            piece = _cased("z", run) if len(run) == 1 else _cased("utc", run)
        elif fill and code == "O":
            piece = "0" * len(run)
        text = text + piece
        place = end
    return text + cell[place:]


def column_padded(cells: "list[str]", reading: Reading, made_up: bool = False) -> bool:
    """Whether a column's two-figure fields that show no width are read as padded.

    Padded unless some cell shows a field written with one figure and none
    shows one written with an opening zero: a column written `3/7/2024`
    writes `12/1/2024` for the first of December, never `12/01/2024`.
    ``made_up``: the cells are a held column's made-up values, read by
    their layout alone: where some layout writes a field with one figure,
    a field of two figures writes ten or more.
    """
    if reading.kind == COUNTED:
        return True
    padded = False
    unpadded = False
    seen = 0
    for cell in cells:
        if seen >= 100000 or (padded and unpadded):
            break
        fields = _fields(cell, reading, made_up) if parsing.folded(cell) else None
        if fields is None:
            continue
        seen = seen + 1
        for code, start, end in fields:
            if code not in ("M", "D", "h", "i"):
                continue
            if end - start == 1:
                unpadded = True
            elif cell[start:start + 1] == "0" and not made_up:
                padded = True
    return padded or not unpadded


def coarse_cell(
    cell: str, reading: Reading, rung: str, first: int, last: int, padded: bool = True
) -> "str | None":
    """A cell written as the start of its bucket at ``rung``, the tails pooled into ``first`` .. ``last``."""
    moment = moment_of(cell, reading)
    if moment is None:
        return None
    start = start_of(moment, rung)
    if start < first:
        start = first
    if start > last:
        start = last
    return rewritten(cell, reading, start, padded)


def coarse_cells(
    cells: "list[str]", grain: Grain, padded: "bool | None" = None
) -> "list[str]":
    """Every cell of a column at a grain's rung; a cell that does not read is kept as written."""
    rung, first, last = grain.spans[len(grain.spans) - 1]
    if rung != grain.rung:
        return cells
    shown = column_padded(cells, grain.reading) if padded is None else padded
    memo: "dict[str, str]" = {}
    found: "list[str]" = []
    for cell in cells:
        if cell in memo:
            found += [memo[cell]]
            continue
        made = coarse_cell(cell, grain.reading, rung, first, last, shown)
        written = cell if made is None else made
        if len(memo) < 65536:
            memo[cell] = written
        found += [written]
    return found


def bounded(word: int, span: int) -> int:
    """One word into ``0 .. span - 1`` by the multiply-high rule (method G3.4b)."""
    return (word * span) >> 64


def drawn_inside(cell: str, reading: Reading, rung: str, word: int) -> str:
    """A twin cell drawn uniformly inside the bucket its coarse cell names, in the cell's own form.

    The draw steps by the cell's own precision (`unit_of`), so a date
    draws a day of its month, a stamp to the minute a minute of its hour.
    A cell that does not read, or whose redrawn value does not read back,
    is kept as written.
    """
    moment = moment_of(cell, reading)
    if moment is None:
        return cell
    start = start_of(moment, rung)
    end = after(start, rung)
    if reading.kind == CLOCK:
        end = min(end, parsing.CLOCK_CAPACITY[reading.member]
                  * parsing.clock_step(reading.member) * _NS_SECOND)
    finest = finest_of(cell, reading)
    if finest in (MONTH, QUARTER):
        count = buckets_between(start, end, finest)
        if count <= 1:
            return cell
        target = start
        for _step in range(bounded(word, count)):
            target = after(target, finest)
    else:
        unit = unit_of(cell, reading)
        count = (end - start) // unit
        if count <= 1:
            return cell
        target = start + bounded(word, count) * unit
    made = rewritten(cell, reading, target, not _shows_unpadded(cell, reading))
    return cell if made is None else made


def _shows_unpadded(cell: str, reading: Reading) -> bool:
    fields = _fields(cell, reading) if reading.kind in (DATE, STAMP) else None
    for code, start, end in fields if fields is not None else []:
        if code in ("M", "D", "h", "i") and end - start == 1:
            return True
    return False


# -- the count of different values, met at the rung ----------------------


def canonical_moment(text: str, resolution: str) -> "int | None":
    """A published point's canonical text (contract 5.6) as a moment, or None where it does not read.

    `YYYY-Qn` at the resolution `quarter`, `YYYY-MM` at `month`,
    `YYYY-MM-DD` at `date` and `YYYY-MM-DD HH:MM:SS` at `datetime`.
    """
    try:
        year = int(text[0:4])
        if resolution == "quarter":
            return parsing.days_from_civil(year, 3 * (int(text[6]) - 1) + 1, 1) * _NS_DAY
        month = int(text[5:7])
        if resolution == "month":
            return parsing.days_from_civil(year, month, 1) * _NS_DAY
        days = parsing.days_from_civil(year, month, int(text[8:10]))
        if resolution == "date":
            return days * _NS_DAY
        seconds = 3600 * int(text[11:13]) + 60 * int(text[14:16]) + int(text[17:19])
        return days * _NS_DAY + seconds * _NS_SECOND
    except (ValueError, IndexError):
        return None


def ordinal_moment(ordinal: int, resolution: str) -> int:
    """A published ordinal (method G7.1: quarters, months, days or seconds from 1970) as a moment."""
    if resolution == "quarter":
        return parsing.days_from_civil(1970 + ordinal // 4, 3 * (ordinal % 4) + 1, 1) * _NS_DAY
    if resolution == "month":
        return parsing.days_from_civil(1970 + ordinal // 12, ordinal % 12 + 1, 1) * _NS_DAY
    if resolution == "date":
        return ordinal * _NS_DAY
    return ordinal * _NS_SECOND


def _census_key(start: int, rung: str, kind: str, finest: str) -> "tuple[int, ...] | None":
    """What a published census reads of a bucket start, or None where a row may not move.

    A clock's censuses read every block it fills, so no row of a clock
    moves. A column written to the month or coarser writes no day, so a
    row moves freely. Otherwise a bucket keeps its weekday, and, at the
    day or finer, its day of the month and its time of day too.
    """
    if kind == CLOCK:
        return None
    if finest in (YEAR, QUARTER, MONTH):
        return ()
    days = start // _NS_DAY
    if RANK[rung] <= RANK[MONTH]:
        return ((days + 4) % 7,)
    _year, _month, date = parsing.civil_from_days(days)
    return ((days + 4) % 7, date, start % _NS_DAY)


def count_filled(
    buckets: "list[int | None]",
    points: "list[int]",
    span: "tuple[int, int]",
    rung: str,
    kind: str,
    finest: str,
    target: int,
    pinned: "dict[int, tuple[int, int]] | None" = None,
) -> "dict[int, int]":
    """Rows moved to empty buckets so the column holds ``target`` different ones (method G7.13).

    ``buckets`` holds each row's bucket start at ``rung``, None for a row
    that holds none; ``points`` the buckets the description's published
    points name; ``span`` the record's first and last bucket; ``pinned``
    the lowest and highest rank of a ladder rung each published bucket
    holds (a bucket a heavy date or a tail names is in ``points`` and not
    here). A row moves only to an empty bucket between the same two
    published points (or the span's ends) whose census key is its own
    (`_census_key`): from a bucket no point names that holds two rows or
    more, and then from the rung just below (its last ranks) or just above
    (its first ranks) where every rank pinned to it stays inside it. So
    every published point keeps its rank, every tail and every heavy date
    its rows, and every census at the rung its counts. Inside each stretch
    donors give fullest first (ties earlier), then the rung below, then
    the rung above, each row to the earliest empty bucket of its key.
    Returns the moved rows and their buckets.

    Guarantees: a function of its arguments. Raises nothing. No I/O.
    """
    rows_of: "dict[int, list[int]]" = {}
    for row in range(len(buckets)):
        bucket = buckets[row]
        if bucket is None:
            continue
        if bucket not in rows_of:
            rows_of[bucket] = []
        rows_of[bucket] += [row]
    first, last = span
    need = target - len(rows_of)
    moved: "dict[int, int]" = {}
    if need <= 0 or first > last:
        return moved
    ranks = pinned if pinned is not None else {}
    below: "dict[int, int]" = {}
    seen = 0
    for bucket in sorted(rows_of):
        below[bucket] = seen
        seen += len(rows_of[bucket])
    ends = sorted({first, last} | {point for point in points if first <= point <= last})
    steps = 4 * len(buckets) + 4096
    for place in range(len(ends) - 1):
        low = ends[place]
        high = ends[place + 1]
        givers: "list[tuple[int, list[int]]]" = []
        for _size, bucket in sorted(
            (-len(rows_of[bucket]), bucket)
            for bucket in rows_of
            if low < bucket < high and len(rows_of[bucket]) >= 2
        ):
            rows = rows_of[bucket]
            givers += [(bucket, [rows[give] for give in range(len(rows) - 1, 0, -1)])]
        if low in ranks and low in rows_of:
            # The rung below gives its last ranks, from its last rows.
            rows = rows_of[low]
            spare = min(len(rows) - 1, below[low] + len(rows) - 1 - ranks[low][1])
            givers += [(low, [rows[len(rows) - 1 - give] for give in range(max(spare, 0))])]
        if high in ranks and high in rows_of:
            # The rung above gives its first ranks, from its first rows, so
            # a rung giving to both its stretches never gives one row twice.
            rows = rows_of[high]
            spare = min(len(rows) - 1, ranks[high][0] - below[high])
            givers += [(high, [rows[give] for give in range(max(spare, 0))])]
        if not any(rows for _bucket, rows in givers):
            continue
        empties: "dict[tuple[int, ...], list[int]]" = {}
        start = after(low, rung)
        while start < high and steps > 0:
            steps -= 1
            if start not in rows_of:
                key = _census_key(start, rung, kind, finest)
                if key is not None:
                    if key not in empties:
                        empties[key] = []
                    empties[key] += [start]
            start = after(start, rung)
        taken: "dict[tuple[int, ...], int]" = {}
        for key in empties:
            taken[key] = 0
        for bucket, rows in givers:
            key = _census_key(bucket, rung, kind, finest)
            if key is None or key not in empties:
                continue
            for row in rows:
                if need <= 0 or taken[key] >= len(empties[key]):
                    break
                moved[row] = empties[key][taken[key]]
                taken[key] = taken[key] + 1
                need -= 1
            if need <= 0:
                return moved
    return moved


def moved_to(cell: str, reading: Reading, start: int) -> str:
    """A cell written as the start of another bucket, in its own form; as written where it cannot be."""
    made = rewritten(cell, reading, start, not _shows_unpadded(cell, reading))
    return cell if made is None else made


# -- the G1 floor: a held column's twin writes valid values -------------


def fixed_span(kind: str, rung: str = DAY) -> "tuple[int, int]":
    """The method's fixed span: its first moment and the moment after its last."""
    if kind == CLOCK:
        return 0, _NS_DAY
    first = parsing.days_from_civil(FIXED_FIRST[0], FIXED_FIRST[1], FIXED_FIRST[2])
    last = parsing.days_from_civil(FIXED_LAST[0], FIXED_LAST[1], FIXED_LAST[2])
    return first * _NS_DAY, (last + 1) * _NS_DAY


def held_span(grain: Grain) -> "tuple[int, int]":
    """What a held column's twin draws from: its deepest published span, else the fixed one."""
    if not grain.spans:
        return fixed_span(grain.reading.kind)
    rung, first, last = grain.spans[len(grain.spans) - 1]
    end = after(last, rung)
    if grain.reading.kind == CLOCK:
        end = min(end, _NS_DAY)
    return first, end


def filled(
    cell: str, reading: Reading, word: int, span: "tuple[int, int]",
    padded: bool, taken: "dict[str, bool]",
) -> "str | None":
    """A made-up cell of a held column written as a VALID value in its own layout (the G1 floor).

    Each figure run keeps its width and each letter its case: a field of
    one figure takes a value below ten, one of two a value its width holds
    (from ten up where the column writes no opening zero); a joint letter
    is written `T`, a zulu letter `Z`, an offset as nought hours. The value
    is drawn uniformly inside ``span`` and stepped forward to the first one
    the layout can write and ``taken`` does not hold. None where none is
    found, or the member is not one this module writes.
    """
    first, end = span
    if end <= first:
        return None
    if reading.kind == COUNTED:
        return _filled_count(cell, reading, word, span, taken)
    fields = _fields(cell, reading, True)
    if fields is None:
        return _filled_layout(cell, reading, word, span, taken)
    unit = _NS_DAY
    for code, start, stop in fields:
        if code in ("h", "i") and unit > _NS_HOUR:
            unit = _NS_HOUR
        if code == "m" and unit > _NS_MINUTE:
            unit = _NS_MINUTE
        if code in ("s", "f") and unit > _NS_SECOND:
            unit = _NS_SECOND
    count = (end - first) // unit
    if count <= 0:
        return None
    moment = first + bounded(word, count) * unit
    steps = 0
    while steps < 200000:
        steps = steps + 1
        if moment >= end:
            moment = first
        parts = _parts_of(moment)
        miss = _fits(cell, fields, parts, padded)
        if miss == "":
            made = _filled_in(cell, fields, parts, padded, True)
            if made is not None and made not in taken and _reads(made, reading):
                return made
            moment = moment + unit
            continue
        moment = after(start_of(moment, miss), miss)
    return None


def _filled_layout(
    cell: str, reading: Reading, word: int, span: "tuple[int, int]", taken: "dict[str, bool]",
) -> "str | None":
    """A made-up cell of a layout no field rule writes, filled by the layout's own writer.

    Steps of a day, or of a second where the layout has a clock, from the
    drawn start to the first moment the layout writes in the made-up
    cell's very form, no earlier made-up cell took; at most 20,000 steps.
    """
    if not parsing.is_layout_name(reading.member):
        return None
    first, end = span
    unit = _NS_SECOND if parsing.layout_has_clock(reading.member) else _NS_DAY
    count = (end - first) // unit
    if count <= 0:
        return None
    moment = first + bounded(word, count) * unit
    for _step in range(20000):
        if moment >= end:
            moment = first
        made = _layout_written(cell, reading, moment, True)
        if made is not None and made not in taken:
            return made
        moment = moment + (_NS_DAY if unit == _NS_DAY else 3607 * _NS_SECOND)
    return None


def _fits(cell: str, fields: "list[tuple[str, int, int]]", parts: _Parts, padded: bool) -> str:
    """The rung of the first field of ``parts`` that cannot fill its run at the run's width, or ""."""
    for code, start, end in fields:
        size = end - start
        value = -1
        rung = DAY
        if code == "M":
            value = parts.month
        elif code == "D":
            value = parts.day
        elif code in ("h", "i"):
            value = parts.hour if code == "h" else (parts.hour % 12 if parts.hour % 12 else 12)
            rung = HOUR
        elif code == "N":
            if _month_name(parts.month, cell[start:end], True) is None:
                return DAY
            continue
        if value < 0:
            continue
        if size == 1 and value >= 10:
            return rung
        if size == 2 and value < 10 and not padded:
            return rung
    return ""


def _reads(text: str, reading: Reading) -> bool:
    if reading.kind == CLOCK:
        return reading.member in parsing.CLOCK_FORMS and (
            parsing.clock_ordinal(text, reading.member) is not None
        )
    return parsing.parse_datetime(text, reading.member) is not None


def _filled_count(
    cell: str, reading: Reading, word: int, span: "tuple[int, int]", taken: "dict[str, bool]",
) -> "str | None":
    """A made-up counted date written as a count of the member's own, at its own figures."""
    if reading.member not in date_counts.MEMBERS or date_counts.TABLE[reading.member].contacts:
        return None
    runs = _runs(cell)
    whole = ""
    places = 0
    for start, end, kind in runs:
        if kind == _DIGIT:
            if not whole:
                whole = cell[start:end]
            else:
                places = end - start
    if not whole:
        return None
    first, end = span
    unit = _NS_DAY
    count = (end - first) // unit
    if count <= 0:
        return None
    place = bounded(word, count)
    form = date_counts.CountForm(places, False, None, False, reading.mark, None)
    for tries in range(min(count, 400000)):
        moment = first + ((place + tries) % count) * unit
        found = date_counts.count_of(reading.member, moment, date_counts.NANOSECOND)
        if found is None:
            continue
        text = date_counts.spelled_count(found[0], found[1], form)
        if len(text) != len(cell) or text in taken:
            continue
        if moment_of(text, reading) is not None:
            return text
    return None


# -- the record, as the description writes it ---------------------------


def span_text(moment: int, kind: str) -> str:
    """One bucket start as the record writes it: `YYYY-MM-DD`, `YYYY-MM-DD HH:MM:SS`, or `HH:MM:SS`."""
    if kind == CLOCK:
        seconds = moment // _NS_SECOND
        return f"{seconds // 3600:02d}:{(seconds // 60) % 60:02d}:{seconds % 60:02d}"
    parts = _parts_of(moment)
    text = f"{parts.year:04d}-{parts.month:02d}-{parts.day:02d}"
    if kind == STAMP or (kind == COUNTED and moment % _NS_DAY):
        text = f"{text} {parts.hour:02d}:{parts.minute:02d}:{parts.second:02d}"
    return text


def span_moment(text: str, kind: str) -> "int | None":
    """The moment one record text names, or None (`span_text` read back)."""
    if not isinstance(text, str):
        return None
    if kind == CLOCK:
        if len(text) != 8 or text[2:3] != ":" or text[5:6] != ":":
            return None
        figures = text[0:2] + text[3:5] + text[6:8]
        for character in figures:
            if not "0" <= character <= "9":
                return None
        hours, minutes, seconds = int(text[0:2]), int(text[3:5]), int(text[6:8])
        if hours > 23 or minutes > 59 or seconds > 59:
            return None
        return (hours * 3600 + minutes * 60 + seconds) * _NS_SECOND
    if len(text) == 10:
        return date_counts.moment_of_iso(text, date_counts.NANOSECOND)
    if len(text) == 19 and text[10:11] == " ":
        return date_counts.moment_of_iso(text, date_counts.NANOSECOND)
    return None


def record(grain: Grain) -> "dict[str, object]":
    """The `time_grain` block a description writes for a grain."""
    return {
        "rung": grain.rung,
        "finest": grain.finest,
        "kind": grain.reading.kind,
        "reading": grain.reading.member,
        "mark": grain.reading.mark,
        "rows": grain.rows,
        "people": grain.people,
        "spans": [
            [rung, span_text(first, grain.reading.kind), span_text(last, grain.reading.kind)]
            for rung, first, last in grain.spans
        ],
    }

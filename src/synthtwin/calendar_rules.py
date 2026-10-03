"""The weekday census of a column of dates: its menu and its rules.

Stage 3b, landing 3b.1 (plan P4-D355, contract WC1 to WC4 and WC6),
as landing 3b.G left it (plan P4-D365). A column of whole dates read on
the local clock publishes `weekday_census`: how many cells of its BODY
-- the cells between the two tail boundaries, both included -- fall on
each day of the week, in GROUPS whose count is nought or at least the
census line (`parsing.census_floor`). Monday is weekday 0 and Sunday 6;
a group is `(first, last, count)` over a run of weekdays.

THE GROUPING IS CHOSEN BY THE FLOOR ALONE, from a fixed MENU, and
nothing else ever chooses one:

  entry 1  the seven weekday counts, consecutive empty weekdays one
           group of nought -- where every weekday holds nought or at
           least the line;
  entry 2  Monday to Friday one group each and `[Sat-Sun]` -- where
           entry 1 failed and these pass, so Saturday or Sunday holds
           one to the line less one;
  entry 3  `[Mon-Fri]` and `[Sat-Sun]` -- where entries 1 and 2 failed
           and these pass, so one of Monday to Friday holds one to the
           line less one;
  else     no census.

A merged group of the menu says only that SOME member is short: the
entry is read back from the shape of the groups alone (`entry_of`).

WHETHER THE CENSUS THE MENU OFFERS IS PUBLISHED is decided by what the
twin can meet, not by what a reader could work out from it (the
owner's principle of 2026-10-01: the threat is a HIPAA exposure, never a
reader rebuilding counts; plan P4-D365 dropped the full-fill
certificate, its bands, its cap, its ties refusal and WC5, WC7, WC8 and
WC9). The producer withholds a census whose twin cannot keep the
column's count of different values (`few_dates`, `room_short`), and
both the producer and the loader hold a published census to its shape
(`shape_breach`): WC1 the cover, WC2 the floor, WC3 the total, WC4 the
menu and WC6 one spelling per day (`one_spelling_published`) -- the
published censuses of written forms give every date one text, so the
count of different values is a count of different days. One storage
class per workbook column (`stored_one_way`) is the producer's too.

AND THE RULES EVERY CENSUS OF STAGE 3B SHARES (plan P4-D364), each
stated once so that no census writes its own: a count is nought or at
least the line (`calendar_floor_ok`); a census's groups are merged from
its bins by one rule (`merged_groups`); a value stands out from its
neighbours by one rule (`standing_out`); and a published census is held
to its groups' cover, floor, total and sure cells by one checker
(`census_breach`), whose weekday form stays here as
`sure_cells_breach`.

Nothing here reads a table: every function is a function of the
numbers handed to it. No I/O of any kind.
"""

from synthtwin import parsing

# The key of the census in a column block of dates (contract 6.6.2).
WEEKDAY_CENSUS = "weekday_census"
# ...and the two more stage 3b's day track publishes there (plan
# P4-D364): the census of the days of the month and the dates that stand
# out, each `[]` on every block until its landing fills it.
DAY_OF_MONTH_CENSUS = "day_of_month_census"
HEAVY_DATES = "heavy_dates"

# Monday is weekday 0 and Sunday weekday 6: seven bins, the last two
# the weekend.
WEEKDAYS = 7
SATURDAY = 5
SUNDAY = 6
FRIDAY = 4

# The one month whose name is the same at either length (`form_holes`).
MAY = 5

# The three entries of the menu, and nought for a grouping that is none
# of them (`entry_of`).
ENTRY_NONE = 0
ENTRY_SEVEN = 1
ENTRY_WEEKEND = 2
ENTRY_WEEKDAYS = 3

# WHY A COLUMN OF DATES PUBLISHES NO WEEKDAY CENSUS, one word per rule
# that withholds it. Never printed as it stands.
REASON_NO_TAILS = "no_tails"
REASON_SPELLINGS = "spellings"
REASON_WORKBOOK = "workbook"
REASON_MENU = "menu"
# Too few different dates in a group, by the conservative rule
# `few_dates`, for the twin to be sure to keep the count of different
# values while it meets the census.
REASON_FEW_DATES = "few_dates"
# Too little room between the published holes, by the conservative rule
# `room_short`, for the twin to be sure to lay the body's different dates
# on.
REASON_ROOM = "room"
# The producer's own census broke a rule the loader asks (`shape_breach`).
REASON_NARROWED = "narrowed"
# A day written in two texts by the table's own cells, or standing on a
# day the published forms or absent spellings hold empty: what the forms
# publish does not account for how the column was written.
REASON_TEXTS = "texts"
REASONS = (
    REASON_NO_TAILS,
    REASON_SPELLINGS,
    REASON_WORKBOOK,
    REASON_MENU,
    REASON_FEW_DATES,
    REASON_ROOM,
    REASON_NARROWED,
    REASON_TEXTS,
)
# WHICH REASONS A SENTENCE MAY NAME (review of landing 3b.1, item 2).
# A withholding says what decided it only where the published numbers
# alone decide it -- no tails, forms that may write a date two ways.
# Every other rule reads the table's own numbers and is said in ONE
# sentence, `REASON_UNSAID`'s (`taxonomy.NOTE_WEEKDAY_WITHHELD_NARROWED`,
# kept by plan P4-D365 under the owner's rule that a guard goes only at a
# high price).
SAID_REASONS = (REASON_NO_TAILS, REASON_SPELLINGS)
REASON_UNSAID = "unsaid"

# THE FEW-DATES RULE (plan P4-D365, measured on the guard drop's
# batteries and its review's): a census is withheld where a non-empty
# group holds fewer than `FEWEST_REAL_DATES` different real dates of the
# body, or where at least two groups are non-empty and they hold fewer
# than seven and a half different real dates each on average -- fewer
# than `MEAN_REAL_HALF_DATES` halves, so the rule stays in whole
# numbers. A CONSERVATIVE rule, set on measured cases: below either,
# the day pass can split a date's rows across two dates to meet the
# census, and the twins measured that did held more different values
# than the column (k7 sessions 17 for 9; payroll on the 15th and the
# last day 53 for 48; one date a month over 51 to 54 months, 7.00 to
# 7.43 dates a group, 53 to 54 for 52). It withholds censuses a twin
# meets as well: 1 to 21 January 2024, a hundred rows a date, met at
# seeds 0 to 2 with all 21 dates once restored (the Codex review of
# P4-D365, item 2). The thresholds stay; that is their price.
FEWEST_REAL_DATES = 3
MEAN_REAL_HALF_DATES = 15

# The censuses of written forms whose one form per cell makes one text
# per date (WC6), in the order the description publishes them.
FORM_CENSUSES = (
    "datetime_separators",
    "date_field_widths",
    "month_name_styles",
    "quarter_marker_case",
    "zulu_case",
)

# The storage classes a workbook cell holding a value can have, for
# the one-storage rule. A blank, empty or absent cell holds no value
# and is no class of the rule.
_VALUE_CLASSES = ("date", "number", "text", "boolean", "error")

def calendar_floor_ok(count: int, line: int) -> bool:
    """Whether one census count may be published: nought, or at least the line.

    THE ONE STATEMENT OF CA2 (plan P4-D364). Every census of stage 3b --
    the weekday's WC2 and each census after it -- asks this, so the rule
    cannot drift between two of them. A group holding one to `line - 1`
    cells would name that many rows; nought names none, and a count at
    the line names a group the floor allows.

    Guarantees: accepts a count and the census line
    (`parsing.census_floor`); returns the answer, false for a negative
    count. Determinism: a fixed function of the two. Raises nothing. No
    I/O of any kind.
    """
    return count == 0 or count >= line


def weekday_of(day: int) -> int:
    """The weekday of a day number counted from 1970-01-01: Monday 0.

    Day 0 was a Thursday, weekday 3. Guarantees: accepts any whole day
    number; returns 0 to 6. Determinism: a fixed function. Raises
    nothing. No I/O of any kind.
    """
    return (day + 3) % WEEKDAYS


def _single_runs(
    bins: "list[int]", first: int, last: int
) -> "list[tuple[int, int, int]]":
    """Weekdays `first` to `last` one group each, empty runs merged."""
    groups: "list[tuple[int, int, int]]" = []
    weekday = first
    while weekday <= last:
        if bins[weekday] > 0:
            groups += [(weekday, weekday, bins[weekday])]
            weekday = weekday + 1
            continue
        end = weekday
        while end + 1 <= last and bins[end + 1] == 0:
            end = end + 1
        groups += [(weekday, end, 0)]
        weekday = end + 1
    return groups


def menu_groups(
    bins: "list[int]", line: int
) -> "tuple[tuple[tuple[int, int, int], ...], int]":
    """The census the menu offers for these seven weekday counts.

    The first entry whose every group holds nought or at least `line`
    (module docstring), with its entry number; `((), ENTRY_NONE)` where
    no entry passes. Decided by the counts and the line alone.

    Guarantees: accepts seven counts and the census line; returns the
    groups in weekday order and the entry. Determinism: a function of
    the two. Raises nothing. No I/O of any kind.
    """
    seven = True
    for count in bins:
        if not calendar_floor_ok(count, line):
            seven = False
    if seven:
        return tuple(_single_runs(bins, 0, SUNDAY)), ENTRY_SEVEN
    weekend = bins[SATURDAY] + bins[SUNDAY]
    weekdays = sum(bins[0:SATURDAY])
    weekend_ok = calendar_floor_ok(weekend, line)
    single = True
    for weekday in range(SATURDAY):
        if not calendar_floor_ok(bins[weekday], line):
            single = False
    if single and weekend_ok and weekend > 0:
        groups = _single_runs(bins, 0, FRIDAY) + [(SATURDAY, SUNDAY, weekend)]
        return tuple(groups), ENTRY_WEEKEND
    if weekend_ok and weekdays >= line:
        return (
            (0, FRIDAY, weekdays),
            (SATURDAY, SUNDAY, weekend),
        ), ENTRY_WEEKDAYS
    return (), ENTRY_NONE


def entry_of(groups: "tuple[tuple[int, int, int], ...]") -> int:
    """Which entry of the menu a published grouping is, read from its shape.

    1: every non-zero group is one weekday. 2: Monday to Friday one
    group each or empty runs, then a non-zero `[Sat-Sun]`. 3:
    `[Mon-Fri]` non-zero, then `[Sat-Sun]` of any count. 0: none of
    them. An empty `[Mon-Fri]` beside a non-zero weekend is entry 2,
    since entry 3 never has an empty `[Mon-Fri]`.

    Guarantees: accepts groups in weekday order; returns 0 to 3.
    Determinism: a function of the groups. Raises nothing. No I/O.
    """
    if not groups:
        return ENTRY_NONE
    every_single = True
    for first, last, count in groups:
        if first != last and count != 0:
            every_single = False
    if every_single:
        return ENTRY_SEVEN
    closing = groups[len(groups) - 1]
    if closing[0] == SATURDAY and closing[1] == SUNDAY and closing[2] > 0:
        before = True
        for first, last, count in groups[: len(groups) - 1]:
            if last > FRIDAY or (first != last and count != 0):
                before = False
        if before:
            return ENTRY_WEEKEND
    if (
        len(groups) == 2
        and groups[0][0] == 0
        and groups[0][1] == FRIDAY
        and groups[0][2] > 0
        and groups[1][0] == SATURDAY
        and groups[1][1] == SUNDAY
    ):
        return ENTRY_WEEKDAYS
    return ENTRY_NONE


def where_of(groups: "tuple[tuple[int, int, int], ...]") -> "tuple[int, ...]":
    """For each weekday, the index of the group holding it.

    Guarantees: accepts groups covering the seven weekdays; returns
    seven indices. Determinism: a function of the groups. Raises
    nothing. No I/O of any kind.
    """
    found = [0 for _ in range(WEEKDAYS)]
    for index in range(len(groups)):
        for weekday in range(groups[index][0], groups[index][1] + 1):
            if 0 <= weekday < WEEKDAYS:
                found[weekday] = index
    return tuple(found)


def sure_cells_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    sure: "list[int]",
    line: int,
) -> int:
    """The closed form of the sure-cells rule on weekday groups: the first
    group the sure cells leave short, or -1.

    `sure` is, per weekday, the cells a reader places there for
    certain: each knot day -- a tail boundary or a published rung --
    holds at least one body cell, and more where rungs at several ranks
    share its day. A non-zero group whose count less those cells is one
    to `line - 1` would hand that remainder back by subtraction. The
    weekday census no longer asks it (WC5 retired, plan P4-D365); it
    stays for the censuses of the clock that reuse it (plan P4-D364).

    Guarantees: accepts the groups, seven sure counts and the line;
    returns a group index or -1. Determinism: a function of the three.
    Raises nothing. No I/O of any kind.
    """
    for index in range(len(groups)):
        first, last, count = groups[index]
        if count == 0:
            continue
        placed = 0
        for weekday in range(first, last + 1):
            placed = placed + sure[weekday]
        left = count - placed
        if 0 < left < line:
            return index
    return -1


def one_spelling_published(
    forms: "dict[str, dict[str, int]]", format_name: str, parsed: int
) -> bool:
    """WC6 (a): whether the published form censuses give a date one text.

    `n_distinct` counts TEXTS, and the census rules count DAYS; the two
    agree only where every published census of written forms names at
    most one form and that form holds every parsed cell, and where the
    member can show a width (`parsing.VARIABLE_WIDTH_MEMBERS`,
    `parsing.TEXTUAL_MEMBERS`) the width census names its one form --
    and a textual member its one month-name form too. An empty census
    there is a withheld census or one no cell could show, and no reader
    can tell which (`parsing.disclosed_census`), so it does not count.

    Guarantees: accepts the five censuses by name, the parser family
    and the parsed cells; returns the answer. Determinism: a function
    of the three. Raises nothing. No I/O of any kind.
    """
    for name in FORM_CENSUSES:
        census: "dict[str, int]" = {}
        if name in forms:
            census = forms[name]
        if len(census) > 1:
            return False
        for form in census:
            if census[form] != parsed:
                return False
    widths: "dict[str, int]" = {}
    if "date_field_widths" in forms:
        widths = forms["date_field_widths"]
    styles: "dict[str, int]" = {}
    if "month_name_styles" in forms:
        styles = forms["month_name_styles"]
    if (
        format_name in parsing.VARIABLE_WIDTH_MEMBERS
        or format_name in parsing.TEXTUAL_MEMBERS
    ) and len(widths) != 1:
        return False
    if format_name in parsing.TEXTUAL_MEMBERS and len(styles) != 1:
        return False
    return True


def form_holes(
    forms: "dict[str, dict[str, int]]", format_name: str, low: int, high: int
) -> "tuple[int, ...]":
    """The days from `low` to `high` the censuses of written forms leave empty.

    WHAT A READER HOLDS BESIDE THE COUNTS (review of landing 3b.1,
    finding 1). WC6 (a) asks every census of written forms to name one
    form holding every parsed cell, and two kinds of form can be
    written only on some days:

    * a WIDTH word one field alone shows (`parsing.width_is_value_bound`)
      is written by a cell whose OTHER field is ten or more. A cell both
      of whose fields are ten or more shows no width and is counted into
      it (`taxonomy.absorbed_width_tally`); a cell whose other field is
      below ten shows a joint word, into which the one-field word would
      have been folded (`parsing.folded_width_tally`), or the other
      field's own word, a second form. So every day whose other field --
      the day of a month-first member, the month of a day-first one --
      is below ten is a HOLE: `{first-field-unpadded: 104}` on
      `m/d/yyyy` says no cell falls on the first to the ninth of any
      month;
    * a month-name word of length `either` (`parsing.name_is_value_bound`)
      is written by a name of May alone, and a cell of any other month
      would show a length the May cells fold into, or a second form:
      every day outside May is a hole.

    Every other word -- a joint width, the one-field width of a textual
    member, a name of a length -- can be written on any day. The ONE
    statement of the rule, asked by the producer, the loader, the
    generator and the validator (`public_holes`), so that no twin date
    stands on a hole and the room rule (`room_short`) counts none.

    Guarantees: accepts the five censuses by name, the parser family and
    the two boundary days; returns the holes between them ascending.
    Determinism: a function of the four. Raises nothing. No I/O of any
    kind.
    """
    width = ""
    if "date_field_widths" in forms and len(forms["date_field_widths"]) == 1:
        for word in forms["date_field_widths"]:
            width = word
    first_field = ""
    if format_name in parsing.VARIABLE_WIDTH_MEMBERS and parsing.width_is_value_bound(width):
        first_field = "month" if format_name in parsing.MONTH_FIRST_MEMBERS else "day"
    shows_first = width in parsing.FIELD_WIDTH_STYLES_FIRST
    may_only = may_only_published(forms, format_name)
    if not first_field and not may_only:
        return ()
    found: "list[int]" = []
    for day in range(low, high + 1):
        _year, month, date = parsing.civil_from_days(day)
        hole = may_only and month != MAY
        if first_field:
            first, second = (month, date) if first_field == "month" else (date, month)
            other = second if shows_first else first
            hole = hole or other < 10
        if hole:
            found += [day]
    return tuple(found)


def may_only_published(forms: "dict[str, dict[str, int]]", format_name: str) -> bool:
    """Whether the month-name census holds every cell of a column to May.

    The month-name half of `form_holes`: a textual member whose one
    published month-name word has the length `either`
    (`parsing.name_is_value_bound`) is written by names of May alone, so
    every day outside May is a hole. The producer asks it alone too:
    the room rule (`room_short`) is asked beside these holes, and beside
    placeholder and declared holes, but never beside width holes alone
    (reviews of landing 3b.G).

    Guarantees: accepts the five censuses by name and the parser family;
    returns the answer. Determinism: a function of the two. Raises
    nothing. No I/O of any kind.
    """
    if (
        format_name not in parsing.TEXTUAL_MEMBERS
        or "month_name_styles" not in forms
        or len(forms["month_name_styles"]) != 1
    ):
        return False
    for word in forms["month_name_styles"]:
        return parsing.name_is_value_bound(word)
    return False


def placeholder_holes(
    judged: "tuple[str, ...]", low: int, high: int
) -> "tuple[int, ...]":
    """The placeholder days from `low` to `high` a block reads as no value.

    A placeholder day (`parsing.CALENDAR_PLACEHOLDERS`) whose decision
    the block publishes as `read_as_missing` in `sentinel_verdicts` has
    every cell written on it counted absent, so a reader holds it empty:
    a HOLE wherever it falls between the two boundaries (second review
    of landing 3b.1, finding 2). `judged` are the candidates of those
    decisions; a candidate that is a number names no day. The ONE
    statement of the rule, asked by the producer and the loader.

    Guarantees: accepts the candidates and the two boundary days;
    returns the holes between them ascending. Determinism: a function of
    the three. Raises nothing. No I/O of any kind.
    """
    found: "list[int]" = []
    for candidate in parsing.CALENDAR_PLACEHOLDERS:
        if candidate not in judged:
            continue
        day = parsing.days_from_civil(
            int(candidate[0:4]), int(candidate[5:7]), int(candidate[8:10])
        )
        if low <= day <= high:
            found += [day]
    return tuple(sorted(found))


def declared_holes(
    spellings: "tuple[str, ...]",
    forms: "dict[str, dict[str, int]]",
    format_name: str,
    low: int,
    high: int,
) -> "tuple[int, ...]":
    """The days from `low` to `high` a PUBLISHED absent spelling names.

    WHAT A READER HOLDS OF THE DECLARED MISSING VALUES (review of landing
    3b.1, finding 6). A description publishes two lists of spellings every
    cell of which was counted absent: the column's `missing_by_source`
    keys, and the placeholder days a declaration named out of this
    package's own vocabulary (`built_in_dates` of the settings'
    `declared_missing_values`). Where one of them is the text a day is
    written in -- the column's member, its one width word and its one
    month-name word, which WC6 asks for -- no parsed cell can stand on
    that day, so it is a HOLE; matched as the declaration rule matches,
    by the exact number where the spelling reads as one and by the
    folded spelling otherwise. Only what is published counts: a day the
    person declared that no key names is a day like any other to a
    reader, and so to the generator and the validator.

    Guarantees: accepts the published spellings, the five censuses of
    written forms, the parser family and the two boundary days; returns
    the holes between them ascending. Determinism: a function of the
    five. Raises nothing. No I/O of any kind.
    """
    width = parsing.DEFAULT_FIELD_WIDTH
    if "date_field_widths" in forms and len(forms["date_field_widths"]) == 1:
        for word in forms["date_field_widths"]:
            width = word
    style = parsing.DEFAULT_NAME_STYLE
    if "month_name_styles" in forms and len(forms["month_name_styles"]) == 1:
        for word in forms["month_name_styles"]:
            style = word
    found: "set[int]" = set()
    for spelling in spellings:
        folded = parsing.folded(spelling)
        read = parsing.parse_datetime(folded, format_name)
        if read is None:
            read = parsing.parse_datetime(parsing.trimmed(spelling), format_name)
        if read is None:
            continue
        canonical = read[0]
        year = int(canonical[0:4])
        month = int(canonical[5:7])
        date = int(canonical[8:10])
        day = parsing.days_from_civil(year, month, date)
        if day < low or day > high:
            continue
        written = parsing.written_date(year, month, date, format_name, width, style)
        exact = parsing.exact_of_spelling(spelling)
        if exact is not None:
            if parsing.exact_of_spelling(written) == exact:
                found = found | {day}
        elif parsing.folded(written) == folded:
            found = found | {day}
    return tuple(sorted(found))


def public_holes(
    forms: "dict[str, dict[str, int]]",
    format_name: str,
    low: int,
    high: int,
    judged: "tuple[str, ...]",
    absent: "tuple[str, ...]",
) -> "tuple[int, ...]":
    """Every hole a description publishes between its two boundaries.

    THE ONE STATEMENT the producer, the loader, the generator and the
    validator each ask (review of landing 3b.1, items 4, 6 and 9): the
    days the censuses of written forms leave empty (`form_holes`), the
    placeholder days the block reads as no value (`placeholder_holes`,
    `judged` its decisions' candidates) and the days a published absent
    spelling names (`declared_holes`, `absent` those spellings).

    Guarantees: accepts the published facts; returns the holes
    ascending. Determinism: a function of the six. Raises nothing. No
    I/O of any kind.
    """
    found = set(form_holes(forms, format_name, low, high))
    found = found | set(placeholder_holes(judged, low, high))
    found = found | set(declared_holes(absent, forms, format_name, low, high))
    return tuple(sorted(found))


def published_one_way(classes: "dict[str, int | None]") -> bool:
    """Whether a workbook's PUBLISHED cell classes leave its values stored one way.

    False where two value classes are published holding cells: a reader
    then knows the column is read back differently cell by cell, and no
    twin can meet a weekday census of it (review of landing 3b.1,
    finding 8). A class withheld (`None`) may hold nought, so it says
    nothing either way; the producer's own rule (`stored_one_way`) reads
    the cells and is the stricter.

    Guarantees: accepts the published census of cell classes; returns
    the answer. Determinism: a function of the census. Raises nothing.
    No I/O of any kind.
    """
    holding = 0
    for kind in _VALUE_CLASSES:
        if kind in classes:
            counted = classes[kind]
            if counted is not None and counted > 0:
                holding = holding + 1
    return holding <= 1


def stored_one_way(classes: "list[str]") -> bool:
    """Whether a workbook column stores every cell holding a value one way.

    A column whose dates are stored partly as dates or dated numbers and
    partly as text is read back differently cell by cell, so no twin
    can meet a weekday census of it (plan P4-D355). Blank, empty and
    absent cells hold no value and are no class of the rule.

    Guarantees: accepts the per-cell storage classes; returns the
    answer. Determinism: a function of the classes. Raises nothing. No
    I/O of any kind.
    """
    seen: "set[str]" = set()
    for kind in classes:
        if kind in _VALUE_CLASSES:
            seen = seen | {kind}
    return len(seen) <= 1


def body_bins(days: "list[int]") -> "list[int]":
    """How many of these days fall on each weekday, Monday first.

    Guarantees: accepts day numbers; returns seven counts. Determinism:
    a function of the days. Raises nothing. No I/O of any kind.
    """
    bins = [0 for _ in range(WEEKDAYS)]
    for day in days:
        weekday = weekday_of(day)
        bins[weekday] = bins[weekday] + 1
    return bins


def group_counts(
    groups: "tuple[tuple[int, int, int], ...]", bins: "list[int]"
) -> "list[int]":
    """Each group's count of these seven weekday counts.

    Guarantees: accepts groups and seven counts; returns one count per
    group. Determinism: a function of the two. Raises nothing. No I/O.
    """
    found: "list[int]" = []
    for first, last, _count in groups:
        found += [sum(bins[first : last + 1])]
    return found


def census_line(floor: int) -> int:
    """The census line of a floor: `parsing.census_floor`, restated.

    Guarantees: accepts the settings floor; returns the line.
    Determinism: a fixed function. Raises nothing. No I/O of any kind.
    """
    return parsing.census_floor(floor)


# HOW A CENSUS'S NEIGHBOURS ARE CENTRED, for `standing_out`: the MEAN of
# the units either side, which the heavy dates read (owner ruling of
# 2026-09-26: "Only dates that stand out"), or their MEDIAN, which a
# grid of clock values reads, because a mean beside a neighbouring heap
# is that heap's.
CENTRE_MEAN = "mean"
CENTRE_MEDIAN = "median"

# The names `census_breach` reports its four rules under unless a census
# passes its own: CA1 the cover, CA2 the floor, CA3 the total and CA5
# the sure cells.
CENSUS_RULES = ("CA1", "CA2", "CA3", "CA5")


def _group_short(count: int, placed: int, line: int) -> bool:
    """Whether a group of `merged_groups` must merge: its count, or its
    count less the cells a reader places in it for certain, is one to
    `line - 1`, or it holds fewer cells than those."""
    left = count - placed
    return (
        not calendar_floor_ok(count, line)
        or left < 0
        or not calendar_floor_ok(left, line)
    )


def _cycle_ordered(groups: "list[list[int]]") -> "list[list[int]]":
    """Groups of a partition of the bins, in bin order: every group that
    runs forward by its first bin, then the one group that runs past the
    last bin, which a census on a cycle lists last."""
    # The groups partition the bins, so no two share a first bin, and a
    # list of whole numbers sorts by its first.
    forward = sorted([group for group in groups if group[0] <= group[1]])
    wrapped = [group for group in groups if group[0] > group[1]]
    return forward + wrapped


def merged_groups(
    counts: "list[int]",
    sure: "list[int]",
    line: int,
    cyclic: bool = False,
) -> "tuple[tuple[int, int, int], ...]":
    """The groups a census of these bins publishes, or none (plan P4-D364).

    ONE MERGE RULE FOR EVERY CENSUS OF BINS. Every bin starts alone, and
    each run of empty bins is one group of nought. A group is SHORT where
    its count is one to `line - 1`, or where its count less its SURE
    cells -- `sure[i]` per bin, the cells a reader places there for
    certain from the rest of the description -- is below nought or one
    to `line - 1`. While a group is short, the short group of least
    count (the earlier on a tie) joins its smaller non-zero neighbour
    (the earlier on a tie), taking in the groups of nought between them.
    On a CYCLE (`cyclic`) the last bin neighbours the first, so one group
    may run past the last bin; it is listed last. Where a short group
    has no non-zero neighbour left, or the merging ends in one group
    covering every bin, no census is published: one group over every
    bin says nothing a reader does not already hold.

    Guarantees: accepts one count per bin, the sure cells per bin
    (shorter lists read as nought) and the census line; returns
    `(first, last, count)` per group, bin indices from nought, `first`
    after `last` only for the one group of a cycle that runs past the
    last bin; or `()`. Determinism: a function of the four. Raises
    nothing. No I/O of any kind.
    """
    size = len(counts)
    if size == 0:
        return ()
    held = [0 for _bin in range(size)]
    for index in range(min(size, len(sure))):
        held[index] = sure[index]
    groups: "list[list[int]]" = []
    index = 0
    while index < size:
        if counts[index] != 0:
            groups += [[index, index, counts[index], held[index]]]
            index = index + 1
            continue
        end = index
        placed = held[index]
        while end + 1 < size and counts[end + 1] == 0:
            end = end + 1
            placed = placed + held[end]
        groups += [[index, end, 0, placed]]
        index = end + 1
    if cyclic and len(groups) > 1 and groups[0][2] == 0 and groups[-1][2] == 0:
        first = groups[0]
        last = groups[len(groups) - 1]
        groups = groups[1 : len(groups) - 1] + [
            [last[0], first[1], 0, first[3] + last[3]]
        ]
    while True:
        pick = -1
        for place in range(len(groups)):
            count, placed = groups[place][2], groups[place][3]
            if not _group_short(count, placed, line):
                continue
            if pick < 0 or count < groups[pick][2]:
                pick = place
        if pick < 0:
            break
        total = len(groups)
        before = -1
        after = -1
        for step in range(1, total):
            place = pick - step
            if place < 0:
                if not cyclic:
                    break
                place = place + total
            if groups[place][2] != 0:
                before = place
                break
        for step in range(1, total):
            place = pick + step
            if place >= total:
                if not cyclic:
                    break
                place = place - total
            if groups[place][2] != 0:
                after = place
                break
        if before < 0 and after < 0:
            return ()
        start, stop = pick, pick
        if after < 0 or (
            before >= 0 and groups[before][2] <= groups[after][2]
        ):
            start = before
        else:
            stop = after
        span = [start]
        while span[len(span) - 1] != stop:
            span += [(span[len(span) - 1] + 1) % total]
        merged = [
            groups[start][0],
            groups[stop][1],
            sum(groups[place][2] for place in span),
            sum(groups[place][3] for place in span),
        ]
        kept = [groups[place] for place in range(total) if place not in span]
        groups = _cycle_ordered(kept + [merged])
    if len(groups) == 1:
        return ()
    return tuple((group[0], group[1], group[2]) for group in groups)


def standing_out(
    counts: "list[int]",
    line: int,
    reach: int,
    centre: str,
    cyclic: bool = False,
) -> "tuple[tuple[int, int], ...]":
    """The units whose count stands out from their neighbours (plan P4-D364).

    THE ONE RULE OF A HEAP. A unit stands out where its count is at least
    the census line AND at least three times the CENTRE of the `reach`
    units on each side of it: their mean (`CENTRE_MEAN`, the heavy
    dates: "at least 11 rows and at least three times the neighbouring
    dates", the owner's ruling of 2026-09-26) or their median
    (`CENTRE_MEDIAN`, a grid of clock values), compared in whole
    numbers. A neighbour past either end of `counts` holds nought --
    except on a CYCLE (`cyclic`: the minutes of an hour, the seconds of a
    minute), where the unit after the last is the first and every
    neighbour is taken modulo the number of units, as `merged_groups`
    reads a cycle and as the minute heaps were measured.

    Guarantees: accepts one count per consecutive unit, the census line,
    the reach, the centre word and whether the units are a cycle;
    returns `(index, count)` per unit that stands out, ascending.
    Determinism: a function of the five. Raises nothing. No I/O of any
    kind.
    """
    size = len(counts)
    found: "list[tuple[int, int]]" = []
    for index in range(size):
        count = counts[index]
        if count < line or count <= 0:
            continue
        around: "list[int]" = []
        for step in range(1, reach + 1):
            for other in (index - step, index + step):
                if cyclic:
                    around += [counts[other % size]]
                else:
                    around += [counts[other] if 0 <= other < size else 0]
        stands = True
        if around and centre == CENTRE_MEDIAN:
            ordered = sorted(around)
            middle = len(ordered) // 2
            twice = 2 * ordered[middle]
            if len(ordered) % 2 == 0:
                twice = ordered[middle - 1] + ordered[middle]
            stands = 2 * count >= 3 * twice
        elif around:
            stands = len(around) * count >= 3 * sum(around)
        if stands:
            found += [(index, count)]
    return tuple(found)


def census_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    bins: int,
    line: int,
    body: int,
    sure: "tuple[int, ...]" = (),
    cyclic: bool = False,
    low: int = 0,
    unit: str = "bin",
    rules: "tuple[str, str, str, str]" = CENSUS_RULES,
) -> "tuple[str, str, str] | None":
    """A published census of bins held to CA1, CA2, CA3 and its sure cells.

    THE ONE CHECKER EVERY CENSUS'S LOADER AND PRODUCER ASK (plan
    P4-D364), in order: the groups cover the bins `low` to
    `low + bins - 1` in order, each once (CA1) -- on a cycle the last
    group alone may run past the last bin; every count is nought or at
    least the line (CA2, `calendar_floor_ok`); the counts add to the
    body (CA3); and every group holds at least its SURE cells, `sure`
    per bin from the first, with what is left of it nought or at least
    the line (the closed form of CA5, WC5's rule for every census). The
    first rule broken is returned under its name in `rules`, as (rule,
    what the census says, what the rule asks), with the bins named by
    `unit`. An empty census is legal and breaks nothing.

    Guarantees: accepts the groups, the bin count, the line, the body,
    the sure cells, whether the bins are a cycle, the first bin's
    number, the bins' word and the four rule names; returns None or the
    broken rule. Determinism: a function of the arguments. Raises
    nothing. No I/O of any kind.
    """
    cover, floor_rule, total_rule, sure_rule = rules
    if not groups:
        return None
    top = low + bins - 1
    # ONE ORDER PER GROUPING: from the first bin, or -- on a cycle whose
    # last group runs past the last bin -- from the bin after that group.
    closing = groups[len(groups) - 1]
    expect = low
    if cyclic and closing[1] < closing[0]:
        expect = closing[1] + 1
    covered = 0
    for place in range(len(groups)):
        first, last, _count = groups[place]
        if first != expect or not low <= first <= top or not low <= last <= top:
            return (
                cover,
                f"a group runs from {unit} {first} to {unit} {last}",
                f"the next group must start at {unit} {expect}, and every "
                f"{unit} lies from {low} to {top}",
            )
        if last < first:
            if not cyclic or place != len(groups) - 1:
                return (
                    cover,
                    f"a group runs from {unit} {first} back to {unit} {last}",
                    f"only the last group of a census on a cycle may run "
                    f"past {unit} {top}",
                )
            covered = covered + (top - first + 1) + (last - low + 1)
        else:
            covered = covered + (last - first + 1)
        expect = last + 1
    if covered != bins:
        return (
            cover,
            f"the groups cover {covered} of the {bins} {unit}s",
            f"they must cover every {unit} from {low} to {top}, each once",
        )
    for first, last, count in groups:
        if not calendar_floor_ok(count, line):
            return (
                floor_rule,
                f"the group from {unit} {first} to {unit} {last} counts {count}",
                f"a count is nought or at least {line}",
            )
    total = sum(count for _first, _last, count in groups)
    if total != body:
        return (
            total_rule,
            f"the groups add to {total}",
            f"the values between the two tail boundaries number {body}",
        )
    for first, last, count in groups:
        placed = 0
        position = first
        while True:
            index = position - low
            if 0 <= index < len(sure):
                placed = placed + sure[index]
            if position == last:
                break
            position = position + 1
            if position > top:
                position = low
        left = count - placed
        if left < 0 or not calendar_floor_ok(left, line):
            return (
                sure_rule,
                f"the group from {unit} {first} to {unit} {last} counts {count}",
                f"it holds at least the {placed} cells the rest of this "
                f"description places in it, and what is left of it is "
                f"nought or at least {line}",
            )
    return None


# THE LANDINGS' ANCHORS (plan P4-D364). Each landing of stage 3b that
# adds to this module adds below its own line, so two landings built
# side by side never touch the same lines; a landing with nothing to add
# leaves its line alone. In the order of the plan's numbering table.
# anchor 3b-D1 (P4-D365)


def shape_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    body: int,
    line: int,
    one_spelling: bool,
) -> "tuple[str, str, str] | None":
    """The loader's check of one published weekday census, or None (P4-D365).

    WC1 the groups cover Monday to Sunday in order, each weekday once;
    WC2 every count is nought or at least the line (`calendar_floor_ok`);
    WC3 the counts add to the body -- the three asked through the one
    checker of every census of stage 3b (`census_breach`); then WC4 the
    grouping is an entry of the menu; and WC6 the published forms give
    every date one text. The first broken rule is returned as (rule, what
    the census says, what the rule asks), the two phrases a person reads
    beside the rule's own words. Nothing here walks a day: the check is a
    function of the census and three published numbers.

    Guarantees: accepts the census, the body (the parsed cells less both
    tails' rows), the census line and WC6 (a)'s answer; returns None or
    the broken rule. Determinism: a function of the four. Raises
    nothing. No I/O of any kind.
    """
    broken = census_breach(
        groups, WEEKDAYS, line, body, unit="weekday",
        rules=("WC1", "WC2", "WC3", "WC2"),
    )
    if broken is not None:
        return broken
    if entry_of(groups) == ENTRY_NONE:
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
    return None


def _dates_by_group(
    groups: "tuple[tuple[int, int, int], ...]", body: "list[int]"
) -> "list[int]":
    """How many different days of `body` each group's weekdays hold."""
    where = where_of(groups)
    held = [0 for _group in groups]
    for day in sorted(set(body)):
        index = where[weekday_of(day)]
        held[index] = held[index] + 1
    return held


def few_dates(
    groups: "tuple[tuple[int, int, int], ...]", body: "list[int]"
) -> bool:
    """Whether the census's groups hold too few different dates (plan P4-D365).

    THE PRODUCER'S FEW-DATES RULE, on the REAL body (its days, one per
    cell): true where a non-empty group holds fewer than
    `FEWEST_REAL_DATES` different days, or where at least two groups are
    non-empty and they hold fewer than seven and a half different days
    each on average (`MEAN_REAL_HALF_DATES` halves). There the day pass
    can meet the census by splitting a date's rows across dates, and a
    twin that does holds more different values than the column, as the
    measured cases did. A CONSERVATIVE rule, not a proof that no twin
    can meet the census: it withholds some a twin meets (1 to 21 January
    2024, a hundred rows a date; the Codex review of P4-D365, item 2),
    and that is its price. A rule of what the twin is sure to meet,
    never of what a reader could work out: the loader cannot ask it, and
    need not.

    Guarantees: accepts the census and the body's days; returns the
    answer. Determinism: a function of the two. Raises nothing. No I/O.
    """
    held = _dates_by_group(groups, body)
    filled = [held[index] for index in range(len(groups)) if groups[index][2] > 0]
    if not filled:
        return False
    if min(filled) < FEWEST_REAL_DATES:
        return True
    return len(filled) >= 2 and 2 * sum(filled) < MEAN_REAL_HALF_DATES * len(filled)


def room_short(
    groups: "tuple[tuple[int, int, int], ...]",
    body: "list[int]",
    holes: "tuple[int, ...]",
) -> bool:
    """Whether the published holes leave a group too little room (plan P4-D365).

    THE PRODUCER'S ROOM RULE, asked where the month-name census holds
    every cell to May (`may_only_published`) or a placeholder or declared
    day is a hole, and never beside width holes alone, with every hole
    the description publishes between the body's first and last day
    (`public_holes`). A group's FREE days are its weekdays' days from the
    first to the last that are no hole and hold no date of the body. True
    where a non-empty group has NO free day and holds a date of ONE row:
    the day pass can meet the census by moving single rows, a one-row
    date it moves can be left empty, and with no free day to stand a
    date on, a twin that leaves one holds fewer different values than
    the column. A CONSERVATIVE rule, set on the cases measured where a
    twin missed, not a proof that none can meet the census (the Codex
    review of P4-D365, item 2). Measured on the
    guard drop's batteries and its review's (plan P4-D365): every column
    whose twin missed its count of different values with the rule off was
    one of May dates written `17 May 2023` that filled every open day and
    held one-row dates (every day of three Mays: 83 for 93). Columns of
    days past the ninth written `m/d/yyyy` met it in every run, so the
    rule is not asked of width holes alone, and their censuses keep
    their weekday statistics. Its second review measured the declared
    days: a column with a date on every day of 240 but five declared
    missing came back 234 different days for 235 with the rule off, so
    it is asked beside placeholder and declared days, and a twin passes
    its own checks there. Counted, not
    walked: each weekday's days by arithmetic, then the holes and the
    dates one by one.

    Guarantees: accepts the census, the body's days (one per cell) and
    the holes; returns the answer. Determinism: a function of the three.
    Raises nothing. No I/O of any kind.
    """
    if not body:
        return False
    low, high = min(body), max(body)
    inside = sorted({day for day in holes if low <= day <= high})
    if not inside:
        return False
    where = where_of(groups)
    free = [0 for _group in groups]
    for weekday in range(WEEKDAYS):
        first = low + (weekday - weekday_of(low)) % WEEKDAYS
        if first <= high:
            index = where[weekday]
            free[index] = free[index] + (high - first) // WEEKDAYS + 1
    for day in inside:
        index = where[weekday_of(day)]
        free[index] = free[index] - 1
    rows: "dict[int, int]" = {}
    for day in body:
        if day in rows:
            rows[day] = rows[day] + 1
        else:
            rows[day] = 1
    single = [0 for _group in groups]
    for day in sorted(rows):
        index = where[weekday_of(day)]
        free[index] = free[index] - 1
        if rows[day] == 1:
            single[index] = single[index] + 1
    for index in range(len(groups)):
        if groups[index][2] > 0 and free[index] <= 0 < single[index]:
            return True
    return False


# anchor 3b-D0 (P4-D366)
# anchor 3b-D2 (P4-D367)
# anchor 3b-D3 (P4-D368)
# anchor 3b-D4 (P4-D369)
# anchor 3b-T1 (P4-D370)
# anchor 3b-T2 (P4-D371)
# anchor 3b-T3 (P4-D372)
# anchor 3b-C1 (P4-D373)
# anchor 3b-C2 (P4-D374)
# anchor 3b-G1 (P4-D375)
# anchor 3b-G3 (P4-D376)
# anchor 3b-G2 (P4-D377)
# anchor 3b-7 (P4-D378)
# anchor 3b-J (P4-D379)

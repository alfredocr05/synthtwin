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

WHETHER THE CENSUS THE MENU OFFERS IS PUBLISHED is decided by rules
about the twin and the census's own shape, never by what a reader could
work out from it (the owner's principle of 2026-10-01: the threat is a
HIPAA exposure, never a reader rebuilding counts; plan P4-D365 dropped
the full-fill certificate, its bands, its cap, its ties refusal and
WC5, WC7, WC8 and WC9). The producer withholds a census by four
CONSERVATIVE rules, set on the cases where a twin was measured to miss
the column's count of different values: too few different dates in a
group (`few_dates`); too few of the column's different days left to the
body, once the most its rebuilt tails can hold is set aside, for the
days the census needs between the body's pins (`count_room_short`, plan
P4-D388), which errs towards a count left LONG; too few days the census
lets the body reach for what the column's count asks of it -- its
rebuilt tails at their most, or, where the twin's count pass merges, no
fewer than their fewest beside a body that keeps no more than its draw
(`count_reach_short`, the Codex review of P4-D388, item 2) -- which
errs towards a count left SHORT, the two asked at every floor; and,
beside May's holes, placeholder days or declared days (never width
holes alone), a group with no free day that holds a date of one row
(`room_short`). They are rules, not proofs that no twin can meet the
census: each also withholds some censuses a twin meets (1 to 21 January
2024, a hundred rows a date; the 50 columns plan P4-D365 counts, and
those P4-D388 counts). Both the producer and the loader hold a published
census to its shape (`shape_breach`): WC1 the cover, WC2 the floor, WC3
the total, WC4 the menu and WC6 one spelling per day
(`one_spelling_published`) -- the published censuses of written forms
give every date one text, so the count of different values is a count
of different days. One storage class per workbook column
(`stored_one_way`) is the producer's too.

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

import math

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
# Too few of the column's different days left to the body, once the most
# its tails can hold is set aside, for the days the census asks of the
# body's gaps, by the conservative rule `count_room_short` (plan
# P4-D388): a raised floor widens the tails a twin rebuilds.
REASON_COUNT_ROOM = "count_room"
# Too few days the census lets the body reach for what the column's count
# asks of it once the twin's count pass has spread or merged its rebuilt
# tails, by the conservative rule `count_reach_short` (the Codex review of
# plan P4-D388, item 2): a rebuilt tail can hold fewer days than the real
# one.
REASON_COUNT_REACH = "count_reach"
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
    REASON_COUNT_ROOM,
    REASON_COUNT_REACH,
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

# THE SHARE OF SEEDS AT WHICH A PUBLISHED CENSUS'S TWIN MAY MISS (the
# orchestrator's ruling of 2026-10-07 on the price of plan P4-D388's count
# rules): a weekday census its twins meet at nine seeds in ten or more
# stands, so the two count rules withhold a census only where the twin's
# tails, as its count pass leaves them, keep too many or too few different
# days with a chance above one in ten (`tails_kept`).
KEPT_MISS = 0.1

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
    may run past the last bin; it is listed last. Earlier is always the
    order the groups are listed in, so of two neighbours of one count a
    short group joins the one listed first even where that is the one
    after it, and where both of its neighbours are one group it joins
    that group through the bins before it. Where a short group
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
        # A tie goes to the neighbour listed earlier in the census, which
        # on a cycle need not be the one before: the group past the last
        # bin is listed last. One group on both sides is joined through
        # the bins before the short group.
        if after < 0 or (
            before >= 0
            and (
                groups[before][2] < groups[after][2]
                or (groups[before][2] == groups[after][2] and before <= after)
            )
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


def body_pins(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    percents: "list[int]",
) -> "tuple[tuple[int, int], ...]":
    """The body's pinned ranks with their days, ascending (method G7.3).

    The ranks no pass of the twin moves inside the body: the two tail
    boundaries, ranks `rows_low` and `len(days) - 1 - rows_high`, and each
    published rung strictly between them, at the rank its percent is read
    off -- `(len(days) - 1) * percent // 100`, as the generator lays it
    (`generation._date_layout`). `days` is the day of every parsed cell
    ascending and `percents` the percents of the published rungs.

    Guarantees: accepts the days, the two tails' rows (a body of at least
    one rank between them) and the percents; returns each pinned rank
    once with its day. Determinism: a function of the four. Raises
    nothing. No I/O of any kind.
    """
    parsed = len(days)
    high = parsed - 1 - rows_high
    found = [(rows_low, days[rows_low])]
    for percent in sorted(set(percents)):
        rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
        if found[len(found) - 1][0] < rank < high:
            found += [(rank, days[rank])]
    if high > found[len(found) - 1][0]:
        found += [(high, days[high])]
    return tuple(found)


def count_room_short(
    groups: "tuple[tuple[int, int, int], ...]",
    pins: "tuple[tuple[int, int], ...]",
    days: int,
    tails: int,
) -> bool:
    """Whether the body is left too few different days for the census (plan P4-D388).

    THE PRODUCER'S COUNT-ROOM RULE, the few-dates rule's companion, asked
    at every floor: it was asked above the floor of 11 alone until the
    Codex review of P4-D388 (item 1) moved one cell of a column the rule
    withholds at 12 and found its census at 11 leaving a twin long, 27
    different values for 24 at seed 17. `pins` are the body's pinned
    ranks with their days, ascending (`body_pins`); `days` is how many
    different days the column holds; `tails` the most different days the
    twin's two tails keep once its count pass has run, but at a share of
    seeds no larger than `KEPT_MISS` (`tails_kept`, the orchestrator's
    ruling of 2026-10-07 on the rule's price).

    The twin's count pass leaves the body the column's different days
    less those its tails keep -- `days - tails`, its ROOM. Its
    day pass moves a body rank only inside its GAP, between the two pins
    either side of it, both days included, so the census NEEDS every pin
    day and, inside each gap, one more day for each group holding rows
    that has a day strictly inside the gap and stands on neither of its
    two pin days (at most one a rank of the gap). True where the census
    needs a day past the pin days and the room is less than the need: a
    twin whose tails keep that many days cannot meet the census then
    without holding more different values than the column. A room equal
    to the need publishes the census. Where the census needs no day past
    the pin days, the body holds every pin day with or without it, so it
    is no cause of a count left long.

    Its price and its risk are both measured (plan P4-D388): a group with
    a day in a gap is counted whether or not the twin puts rows there, and
    the tails' most counts no merge, so where the count pass merges a body
    down to a few days and takes days from the tails as well it withholds
    censuses their twins meet; and the tails are read at the share of
    seeds the ruling allows, so a twin of a census it publishes can still
    be left long at that share of seeds, a miss the twin's report and
    validation name.

    Guarantees: accepts the census, the pins, the count and the tails'
    days; returns the answer. Determinism: a function of the four. Raises
    nothing. No I/O of any kind.
    """
    where = where_of(groups)
    held: "list[int]" = []
    for _rank, day in pins:
        if day not in held:
            held += [day]
    need = len(held)
    for place in range(len(pins) - 1):
        rank, first = pins[place]
        following, last = pins[place + 1]
        inner = following - rank - 1
        if inner < 1 or last <= first:
            continue
        ends = (where[weekday_of(first)], where[weekday_of(last)])
        found: "list[int]" = []
        for day in range(first + 1, min(last, first + WEEKDAYS)):
            index = where[weekday_of(day)]
            if groups[index][2] > 0 and index not in ends and index not in found:
                found += [index]
        need = need + min(len(found), inner)
    return need > len(held) and days - tails < need


# THE TWIN'S REBUILT TAIL, AS METHOD G7.3b LAYS IT (the Codex review of
# plan P4-D388, item 2), for `tails_fewest` and `tails_most_rebuilt`. The
# producer may not import the generator -- the validator describes a file
# with the producer and never imports the generator -- so the steps the
# generator takes from a tail's published rows, distances and floor to
# every rank's nearest and
# furthest whole distance are written here a second time, operation for
# operation in the same order, and tests/test_stage3b_count_room.py holds
# them equal to `generation._tail_distance_bounds` on a seeded grid of
# tails and to the layout the generator lays on described columns.
# `_REBUILT_WORDS` is the generator's word scale, 2**64, and the two
# slacks are its own: how far a root of the weight's quadratic may fall
# outside [0, 1], and the share of the Bhatia-Davis reach given up to the
# rounding of the two published distances.
_REBUILT_WORDS = 18446744073709551616
_REBUILT_WEIGHT_SLACK = 1e-12
_REBUILT_END_SLACK = 1.0 / 16777216.0


def _half_up(value: float) -> int:
    """The whole number nearest a non-negative binary64 value, halves up, exactly."""
    if value <= 0.0:
        return 0
    fraction, exponent = math.frexp(value)
    significand = int(math.ldexp(fraction, 53))
    shift = exponent - 53
    if shift >= 0:
        return significand << shift
    below = 1 << (-shift)
    return (2 * significand + below) // (2 * below)


def _power_of(base: float, power: int) -> float:
    """base**power by squaring and multiplying over the bits of `power`,
    the most significant first, each step rounded to binary64."""
    result = 1.0
    bit = 1
    while bit * 2 <= power:
        bit = bit * 2
    while bit >= 1:
        result = result * result
        if power & bit:
            result = result * base
        bit = bit // 2
    return result


def _mixture_power(ratio: float) -> int:
    """The largest n with (n + 1)**2 <= ratio * (2n + 1), decided exactly."""
    fraction, exponent = math.frexp(ratio)
    top = int(math.ldexp(fraction, 53))
    shift = exponent - 53
    bottom = 1
    if shift >= 0:
        top = top << shift
    else:
        bottom = 1 << (-shift)
    power = 0
    while (power + 2) * (power + 2) * bottom <= top * (2 * power + 3):
        power = power + 1
    return power


def _mixture_weight(power: int, ratio: float) -> float:
    """The weight of the lower power in the mixture, the root in [0, 1]."""
    a2 = 1.0 / (power + 2)
    de = 1.0 / ((power + 1) * (power + 2))
    b1 = 1.0 / (2 * power + 1)
    c = 1.0 / (power + 1)
    b2 = 1.0 / (2 * power + 3)
    qa = ((b1 - c) + b2) - ((ratio * de) * de)
    qb = (c - (2.0 * b2)) - (((2.0 * ratio) * a2) * de)
    qc = b2 - ((ratio * a2) * a2)
    if qc <= 0.0:
        return 0.0
    disc = (qb * qb) - ((4.0 * qa) * qc)
    if disc < 0.0:
        disc = 0.0
    root = math.sqrt(disc)
    if qb >= 0.0:
        half = -0.5 * (qb + root)
    else:
        half = -0.5 * (qb - root)
    best = 2.0
    for candidate_top, candidate_bottom in ((half, qa), (qc, half)):
        if candidate_bottom == 0.0:
            continue
        candidate = candidate_top / candidate_bottom
        if (
            -_REBUILT_WEIGHT_SLACK <= candidate <= 1.0 + _REBUILT_WEIGHT_SLACK
            and candidate < best
        ):
            best = candidate
    if best > 1.0 + _REBUILT_WEIGHT_SLACK:
        return 1.0
    return min(max(best, 0.0), 1.0)


def _mixture_at(mixture: "tuple[float, int, float]", s: float) -> float:
    """a(s) = scale * (s**power * (weight + (1 - weight) * s))."""
    scale, power, weight = mixture
    return scale * (_power_of(s, power) * (weight + ((1.0 - weight) * s)))


def _mixture_mean_to(mixture: "tuple[float, int, float]", s: float) -> float:
    """The integral of a from 0 to s."""
    scale, power, weight = mixture
    lifted = _power_of(s, power + 1)
    return scale * (
        ((weight * lifted) / (power + 1))
        + (((1.0 - weight) * (lifted * s)) / (power + 2))
    )


def _mixture_square_to(mixture: "tuple[float, int, float]", s: float) -> float:
    """The integral of a**2 from 0 to s."""
    scale, power, w = mixture
    rest = 1.0 - w
    lifted = _power_of(s, 2 * power + 1)
    first = ((w * w) * lifted) / (2 * power + 1)
    second = (((2.0 * w) * rest) * (lifted * s)) / (2 * power + 2)
    third = ((rest * rest) * ((lifted * s) * s)) / (2 * power + 3)
    return (scale * scale) * ((first + second) + third)


def _least_end(mean: float, root: float, edge: int) -> int:
    """The nearest the outermost rank may stand: the Bhatia-Davis reach."""
    if not mean > 1.0:
        return 0
    reach = ((root * root) - mean) / (mean - 1.0)
    lowered = reach - ((1.0 + reach) * _REBUILT_END_SLACK)
    if not lowered < edge:
        return edge
    above = int(lowered)
    if float(above) < lowered:
        above = above + 1
    return min(max(above, 0), edge)


def rebuilt_tail(
    rows: int, mean: float, root: float, floor: int, edge: int, apart: bool
) -> "tuple[tuple[float, int, float], float, int, int, int]":
    """The shape one tail of dates is rebuilt through (method G7.3b steps 1 to 5).

    `(mixture, stretch, end, group, grouped)`: the mixture
    `(scale, power, weight)`, the stretch of every rank but the outermost,
    the outermost rank's whole distance, the one whole distance the
    innermost ranks share where the tail holds more rows than the floor,
    and the first outer index of that group (`rows` where there is none),
    exactly as `generation._tail_shape` takes them from the published rows,
    mean and root-mean-square distances, the settings floor, the furthest
    distance the member can write and whether the column's values all
    differ, a tail of dates always grouped.

    Guarantees: accepts a tail of one row or more; returns the five.
    Determinism: a function of the six, in binary64 operation for
    operation as the generator takes it. Raises nothing. No I/O.
    """
    ratio = 1.0
    if mean > 0.0:
        quotient = root / mean
        ratio = quotient * quotient
    if ratio < 1.0:
        ratio = 1.0
    power = _mixture_power(ratio)
    weight = _mixture_weight(power, ratio)
    scale = mean / (
        (1.0 / (power + 2)) + (weight * (1.0 / ((power + 1) * (power + 2))))
    )
    mixture = (scale, power, weight)
    total = rows * mean
    squares = rows * (root * root)
    inner = (rows - 1) / rows
    lower = rows * _mixture_mean_to(mixture, inner)
    lower_squares = rows * _mixture_square_to(mixture, inner)
    reach = _mixture_at(mixture, inner)
    qa = (lower * lower) + lower_squares
    qb = -2.0 * (total * lower)
    qc = (total * total) - squares
    stretch = 1.0
    end = -1.0
    if qa > 0.0:
        disc = (qb * qb) - ((4.0 * qa) * qc)
        if disc >= 0.0:
            spread = math.sqrt(disc)
            for candidate in ((-qb - spread) / (2.0 * qa), (-qb + spread) / (2.0 * qa)):
                far = total - (candidate * lower)
                if candidate <= 0.0 or far < candidate * reach:
                    continue
                if end < 0.0 or abs(candidate - 1.0) < abs(stretch - 1.0):
                    stretch = candidate
                    end = far
    if end < 0.0:
        stretch = 1.0
        outer = rows * (
            _mixture_square_to(mixture, 1.0) - _mixture_square_to(mixture, inner)
        )
        end = math.sqrt(max(outer, 0.0))
    if end > edge:
        end = float(edge)
        if lower > 0.0:
            stretch = (total - end) / lower
    end_units = min(max(1, _half_up(end)), edge)
    grouped = rows
    group = 0
    if not apart and rows > floor >= 1:
        grouped = floor - 1
        share = (rows - grouped) / rows
        mean_of_group = (rows * _mixture_mean_to(mixture, share)) / (rows - grouped)
        group = min(max(1, _half_up(stretch * mean_of_group)), edge)
        if grouped == 0:
            end_units = group
    end_units = max(end_units, _least_end(mean, root, edge))
    return mixture, stretch, end_units, group, grouped


def rebuilt_distances(
    rows: int,
    rebuilt: "tuple[tuple[float, int, float], float, int, int, int]",
    edge: int,
    apart: bool,
    word: int,
) -> "list[int]":
    """Every rank's whole distance, outermost first, every rank reading `word` (G7.3b).

    `generation._tail_distances` with every rank's word the same, the
    shape `rebuilt` as `rebuilt_tail` gives it with its end and group as
    the generator steps them off the holes: nought gives every rank's
    nearest distance and `2**64 - 1` its furthest
    (`generation._tail_distance_bounds`), which bound every word between
    them because each step is monotone in every word.

    Guarantees: returns `rows` whole distances. Determinism: a function
    of the five. Raises nothing. No I/O of any kind.
    """
    mixture, stretch, end, group, grouped = rebuilt
    found = [0 for _index in range(rows)]
    if rows == 0:
        return found
    found[0] = end
    for index in range(1, rows):
        if index >= grouped:
            found[index] = group
            continue
        s = ((rows - 1 - index) * _REBUILT_WORDS + word) / (rows * _REBUILT_WORDS)
        found[index] = max(1, _half_up(stretch * _mixture_at(mixture, s)))
    for index in range(rows - 2, -1, -1):
        if found[index] < found[index + 1]:
            found[index] = found[index + 1]
    if apart:
        for index in range(rows - 2, -1, -1):
            if found[index] <= found[index + 1]:
                found[index] = found[index + 1] + 1
            found[index] = min(found[index], edge)
        for index in range(1, rows):
            if found[index] >= found[index - 1]:
                found[index] = max(1, found[index - 1] - 1)
    for index in range(rows):
        found[index] = min(found[index], edge)
    return found


def _off_the_holes(
    distance: int, boundary: int, low_side: bool, holes: "frozenset[int]"
) -> int:
    """A point rank's whole distance, stepped inward off every hole's day
    (G7.3b step 7, `generation._off_the_holes`)."""
    while distance > 1:
        unit = boundary - distance if low_side else boundary + distance
        if unit not in holes:
            break
        distance = distance - 1
    return distance


def _fewest_spots(near: "list[int]", far: "list[int]") -> int:
    """The fewest whole distances that leave one inside every rank's span
    `[near, far]`: the spans by their furthest end, a distance taken at
    the furthest end of each span no distance taken so far reaches."""
    spans = sorted((far[index], near[index]) for index in range(len(near)))
    taken = 0
    last = -1
    for furthest, nearest in spans:
        if taken == 0 or nearest > last:
            taken = taken + 1
            last = furthest
    return taken


def _untaken(taken: "dict[int, int]", point: int) -> int:
    """The least whole distance at `point` or past it that no span has
    taken: each taken distance points past itself, and the path walked is
    pointed at the answer."""
    walked: "list[int]" = []
    while point in taken:
        walked += [point]
        point = taken[point]
    for step in walked:
        taken[step] = point
    return point


def _most_spots(near: "list[int]", far: "list[int]") -> int:
    """The most different whole distances the ranks can take, one inside
    each rank's span `[near, far]`: the spans by their furthest end, each
    given the nearest distance inside it no span before it took."""
    spans = sorted((far[index], near[index]) for index in range(len(near)))
    taken: "dict[int, int]" = {}
    found = 0
    for furthest, nearest in spans:
        point = _untaken(taken, nearest)
        if point <= furthest:
            taken[point] = point + 1
            found = found + 1
    return found


def _side_rebuilt(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    facts: "tuple[int | None, float | None, float | None]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]",
    low_side: bool,
) -> "tuple[int, tuple[tuple[float, int, float], float, int, int, int] | None, int]":
    """One tail as method G7.3b rebuilds it: `(fixed, rebuilt, edge)`.

    `fixed` is the different days the tail holds whatever its draws -- as
    many as it lists, nought where it holds no row, its rows as far as the
    member's edge allows where the column's values all differ -- and
    `rebuilt` None; otherwise `fixed` is -1 and `rebuilt` is the shape its
    ranks are drawn through (`rebuilt_tail`), its end and group stepped
    inward off the holes (step 7), with `edge` the furthest distance the
    member can write."""
    listed, mean_distance, rms_distance = facts
    if listed is not None:
        return listed, None, 0
    rows = rows_low if low_side else rows_high
    if rows <= 0:
        return 0, None, 0
    parsed = len(days)
    at = days[rows_low] if low_side else days[parsed - 1 - rows_high]
    edge = max(1, at - edges[0] if low_side else edges[1] - at)
    if apart:
        return min(rows, edge), None, edge
    mean = 1.0 if mean_distance is None else mean_distance
    root = mean if rms_distance is None else rms_distance
    mixture, stretch, end, group, grouped = rebuilt_tail(
        rows, mean, root, floor, edge, apart
    )
    end = _off_the_holes(end, at, low_side, holes)
    if grouped < rows:
        group = _off_the_holes(group, at, low_side, holes)
    return -1, (mixture, stretch, max(end, group), group, grouped), edge


def _side_counted(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    facts: "tuple[int | None, float | None, float | None]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]",
    low_side: bool,
    most: bool,
) -> int:
    """The fewest (or, with `most`, the most) different days ONE rebuilt
    tail can hold: its ranks' spans read off `rebuilt_distances`."""
    fixed, rebuilt, edge = _side_rebuilt(
        days, rows_low, rows_high, facts, floor, edges, apart, holes, low_side
    )
    if rebuilt is None:
        return fixed
    rows = rows_low if low_side else rows_high
    near = rebuilt_distances(rows, rebuilt, edge, apart, 0)
    far = rebuilt_distances(rows, rebuilt, edge, apart, _REBUILT_WORDS - 1)
    if most:
        return _most_spots(near, far)
    return _fewest_spots(near, far)


def _tails_counted(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    published: "tuple[tuple[int | None, float | None, float | None], tuple[int | None, float | None, float | None]]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]",
    most: bool,
) -> int:
    """The fewest (or, with `most`, the most) different days the two
    rebuilt tails can hold, as `tails_fewest` and `tails_most_rebuilt`
    say."""
    counted = 0
    for low_side, facts in ((True, published[0]), (False, published[1])):
        counted = counted + _side_counted(
            days, rows_low, rows_high, facts, floor, edges, apart, holes,
            low_side, most,
        )
    return counted


def tails_fewest(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    published: "tuple[tuple[int | None, float | None, float | None], tuple[int | None, float | None, float | None]]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]" = frozenset(),
) -> int:
    """The fewest different days the twin's two tails can hold (method G7.3b).

    `days` is the day of every parsed cell ascending, `rows_low` and
    `rows_high` the two tails' rows, and `published` each tail's count of
    listed values, or None where it publishes its two distances instead,
    with its published mean and root-mean-square distances; `edges` the
    first and last day the column's member can write
    (`taxonomy.tail_edges`), `apart` whether the column's values all
    differ, and `holes` the days the column's published absent spellings
    name (`generation._hole_units`).

    A tail that lists its values is written on every one of them, each on
    a rank at least, so on exactly as many days as it lists. A tail that
    publishes its two distances is rebuilt by G7.3b (`rebuilt_tail`), its
    end and group stepped inward off the holes (step 7), and each rank's
    distance lies between its distances at the least and the largest word
    (`rebuilt_distances`), its SPAN, which the count pass moves it inside
    and no further: the twin's tail holds at least the fewest whole
    distances that leave one inside every rank's span (`_fewest_spots`),
    whatever its draws and its passes. Where the column's values all
    differ the ranks are made all different, as far as the member's edge
    allows.

    Guarantees: accepts the days, the two tails' rows (each less than the
    days' count), their published facts, the settings floor, the edges,
    the flag and the holes; returns the sum. Determinism: a function of
    the eight. Raises nothing. No I/O of any kind.
    """
    return _tails_counted(
        days, rows_low, rows_high, published, floor, edges, apart, holes, False
    )


def tails_most_rebuilt(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    published: "tuple[tuple[int | None, float | None, float | None], tuple[int | None, float | None, float | None]]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]" = frozenset(),
) -> int:
    """The most different days the twin's two tails can hold as G7.3b rebuilds them.

    The arguments are `tails_fewest`'s, and so are the spans: a tail that
    lists its values holds exactly as many days as it lists, one whose
    column's values all differ as many as its rows the member's edge
    allows, and any other at most the most whole distances that can stand
    one inside each rank's span, each a distance of its own
    (`_most_spots`): the days the count pass can spread it onto, moving
    ranks that share a day onto free days of their own spans. Never fewer
    than `tails_fewest`; a tail of distances holds no more than the
    floor's number of days, its ranks past it sharing one distance.

    Guarantees: accepts what `tails_fewest` accepts; returns the sum.
    Determinism: a function of the eight. Raises nothing. No I/O.
    """
    return _tails_counted(
        days, rows_low, rows_high, published, floor, edges, apart, holes, True
    )


def _weekday_days(first: int, last: int) -> "list[int]":
    """How many days of each weekday lie from `first` to `last`, both
    included, counted without a walk: none where `last` is before
    `first`."""
    found = [0 for _weekday in range(WEEKDAYS)]
    total = last - first + 1
    if total <= 0:
        return found
    start = weekday_of(first)
    for step in range(WEEKDAYS):
        extra = 1 if step < total % WEEKDAYS else 0
        found[(start + step) % WEEKDAYS] = total // WEEKDAYS + extra
    return found


def _rank_drawn(
    rows: int,
    rebuilt: "tuple[tuple[float, int, float], float, int, int, int]",
    edge: int,
    index: int,
    word: int,
) -> int:
    """The whole distance drawn rank `index` of a rebuilt tail stands at
    when it reads `word` (G7.3b), kept at most `edge`. Each step of the
    reckoning is monotone in binary64, so the distance never falls as the
    word rises, and an outer rank, whose stratum of the shape lies past
    the next one in, stands no nearer at any word than the next one in at
    any."""
    mixture, stretch, _end, _group, _grouped = rebuilt
    s = ((rows - 1 - index) * _REBUILT_WORDS + word) / (rows * _REBUILT_WORDS)
    return min(max(1, _half_up(stretch * _mixture_at(mixture, s))), edge)


def _words_through(
    rows: int,
    rebuilt: "tuple[tuple[float, int, float], float, int, int, int]",
    edge: int,
    index: int,
    distance: int,
) -> int:
    """How many of the generator's words put drawn rank `index` of a
    rebuilt tail at `distance` or nearer (G7.3b): none short of its
    nearest distance, every word from its furthest on, and between them
    the largest word giving `distance` or nearer, found by halving the
    words, plus one. Exact: a whole number of words of the scale."""
    if distance < _rank_drawn(rows, rebuilt, edge, index, 0):
        return 0
    if distance >= _rank_drawn(rows, rebuilt, edge, index, _REBUILT_WORDS - 1):
        return _REBUILT_WORDS
    low, high = 0, _REBUILT_WORDS - 1
    while high - low > 1:
        middle = (low + high) // 2
        if _rank_drawn(rows, rebuilt, edge, index, middle) <= distance:
            low = middle
        else:
            high = middle
    return low + 1


def _law_put(
    under: "dict[int, float]",
    held: "dict[int, dict[int, float]]",
    onward: int,
    outermost: bool,
    stands: int,
    count: int,
    chance: float,
) -> None:
    """Add `chance` to the walk's state of `count` different days whose
    last distance is `stands` (`_drawn_law`): with every count whose last
    distance lies below `onward`, the nearest the next step can bring, or
    on its own -- and past the outermost drawn rank, where only the end
    is asked, every distance at or past the end as one."""
    if chance <= 0.0:
        return
    if stands < onward:
        under[count] = (under[count] if count in under else 0.0) + chance
        return
    key = onward if outermost else stands
    if key not in held:
        held[key] = {}
    held[key][count] = (held[key][count] if count in held[key] else 0.0) + chance


def _drawn_law(
    rows: int,
    rebuilt: "tuple[tuple[float, int, float], float, int, int, int]",
    edge: int,
) -> "dict[int, float]":
    """The chance of each count of different days a rebuilt tail's ranks
    draw (G7.3b, its column's values not all different): the end, each
    drawn rank's distance raised to the group's, and the group. Each drawn
    rank reads its own word and the distances never fall outward, so the
    different days are one more than the places where a rank's distance
    passes the last one in -- counted from the innermost rank out,
    carrying the distance last drawn.

    A WALK THAT READS ONLY WHERE A RANK CAN MEET THE LAST DISTANCE. A
    rank's stratum lies past the next one in (`_rank_drawn`), so it passes
    every last distance below its nearest and can share a day only with
    one at or past it -- where two strata meet, or a group's or an edge's
    distance. So the walk carries every count whose last distance lies
    below the next step's nearest as one, each other last distance on its
    own, and reads a rank's chances only at those distances
    (`_words_through`): a few halvings of the words a rank however far
    its stratum spreads. Read at every distance of every stratum, one
    tail of fifty ranks spread over two centuries took 85 s.
    """
    _mixture, _stretch, end, group, grouped = rebuilt
    ranks = [index for index in range(min(grouped, rows) - 1, 0, -1)]
    nearest = [_rank_drawn(rows, rebuilt, edge, index, 0) for index in ranks]
    # `under`: the chance of each count whose last distance lies below the
    # nearest the next step can bring; `held`: each other last distance's.
    under: "dict[int, float]" = {}
    held: "dict[int, dict[int, float]]" = {}
    if grouped < rows:
        held = {group: {1: 1.0}}
    else:
        under = {0: 1.0}
    for place in range(len(ranks)):
        index = ranks[place]
        outermost = place + 1 == len(ranks)
        onward = end if outermost else nearest[place + 1]
        far = _rank_drawn(rows, rebuilt, edge, index, _REBUILT_WORDS - 1)
        passed: "dict[int, float]" = {}
        for count in sorted(under):
            passed[count] = under[count]
        starts: "list[tuple[int, dict[int, float], bool]]" = []
        for last in sorted(held):
            if last >= nearest[place]:
                starts += [(last, held[last], True)]
                continue
            for count in sorted(held[last]):
                passed[count] = (passed[count] if count in passed else 0.0) + held[last][count]
        starts = [(nearest[place] - 1, passed, False)] + starts
        moved_under: "dict[int, float]" = {}
        moved_held: "dict[int, dict[int, float]]" = {}
        for last, counts, stays in starts:
            # Drawn at `last` or nearer, the rank stands on the last
            # distance and adds no day; drawn past it, it adds one.
            kept = _words_through(rows, rebuilt, edge, index, last)
            split = max(last, onward - 1)
            lumped = _words_through(rows, rebuilt, edge, index, split) - kept
            singles: "list[tuple[int, int]]" = []
            if outermost:
                singles = [(onward, _REBUILT_WORDS - kept - lumped)]
            else:
                below = kept + lumped
                for distance in range(split + 1, far + 1):
                    through = _words_through(rows, rebuilt, edge, index, distance)
                    singles += [(distance, through - below)]
                    below = through
            for count in sorted(counts):
                chance = counts[count]
                if stays:
                    _law_put(
                        moved_under, moved_held, onward, outermost, last, count,
                        chance * (kept / _REBUILT_WORDS),
                    )
                _law_put(
                    moved_under, moved_held, onward, outermost, onward - 1,
                    count + 1, chance * (lumped / _REBUILT_WORDS),
                )
                for distance, words in singles:
                    _law_put(
                        moved_under, moved_held, onward, outermost, distance,
                        count + 1, chance * (words / _REBUILT_WORDS),
                    )
        under, held = moved_under, moved_held
    found: "dict[int, float]" = {}
    for count in sorted(under):
        found[count + 1] = (found[count + 1] if count + 1 in found else 0.0) + under[count]
    for last in sorted(held):
        added = 1 if max(end, last) != last else 0
        for count in sorted(held[last]):
            total = count + added
            found[total] = (found[total] if total in found else 0.0) + held[last][count]
    return found


def tail_days_law(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    published: "tuple[tuple[int | None, float | None, float | None], tuple[int | None, float | None, float | None]]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]",
    low_side: bool,
) -> "dict[int, float]":
    """The chance of each count of different days one tail of the twin draws (method G7.3b).

    The arguments are `tails_fewest`'s, and `low_side` names the tail. A
    tail that lists its values draws exactly as many days as it lists, one
    holding no row none, and one whose column's values all differ its
    rows as far as the member's edge allows. Any other is drawn through
    its rebuilt shape (`rebuilt_tail`, its end and group stepped off the
    holes), each drawn rank reading its own uniform word, so the law of
    the days it draws is worked out exactly from the shape
    (`_drawn_law`): no draw is made. The count pass may then merge or
    spread the tail (`tails_kept`).

    Guarantees: accepts what `tails_fewest` accepts and the side; returns
    each count with its chance, the chances summing to one within
    binary64. Determinism: a function of the arguments, in binary64.
    Raises nothing. No I/O of any kind.
    """
    facts = published[0] if low_side else published[1]
    fixed, rebuilt, edge = _side_rebuilt(
        days, rows_low, rows_high, facts, floor, edges, apart, holes, low_side
    )
    if rebuilt is None:
        return {fixed: 1.0}
    return _drawn_law(rows_low if low_side else rows_high, rebuilt, edge)


def body_draw(
    pins: "tuple[tuple[int, int], ...]", holes: "frozenset[int]" = frozenset()
) -> float:
    """The different days the body's ranks draw, in expectation (method G7.3).

    `pins` are the body's pinned ranks with their days, ascending
    (`body_pins`), and `holes` the days the description publishes as
    holding no body cell (`public_holes`). The body's ranks are drawn
    independently inside their gaps, so a gap of `r` ranks strictly
    between its two pins over `n` days strictly between them that are no
    hole lands on `n * (1 - (1 - 1/n)**r)` of them in expectation; the
    body's DRAW is that, gap by gap in order, beside the distinct pin
    days. No day is walked: each weekday's days in a gap are counted and
    the holes inside it set aside one by one.

    Guarantees: accepts the pins and the holes; returns the draw.
    Determinism: a function of the two, in binary64. Raises nothing. No
    I/O of any kind.
    """
    if not pins:
        return 0.0
    held: "list[int]" = []
    for _rank, day in pins:
        if day not in held:
            held += [day]
    first_day = pins[0][1]
    last_day = pins[len(pins) - 1][1]
    inside = sorted(day for day in holes if first_day <= day <= last_day)
    draw = float(len(held))
    at = 0
    for place in range(len(pins) - 1):
        rank, first = pins[place]
        following, last = pins[place + 1]
        while at < len(inside) and inside[at] <= first:
            at = at + 1
        inner = following - rank - 1
        if inner < 1 or last - first < 2:
            continue
        counts = _weekday_days(first + 1, last - 1)
        while at < len(inside) and inside[at] < last:
            weekday = weekday_of(inside[at])
            counts[weekday] = counts[weekday] - 1
            at = at + 1
        every = 0
        for weekday in range(WEEKDAYS):
            every = every + counts[weekday]
        if every > 0:
            draw = draw + every * (1.0 - _power_of(1.0 - 1.0 / every, inner))
    return draw


def _law_mean(law: "dict[int, float]") -> float:
    """The expected count of a law."""
    mean = 0.0
    for count in sorted(law):
        mean = mean + count * law[count]
    return mean


def _law_reached(law: "dict[int, float]", share: float, strictly: bool) -> int:
    """The least count at which the law's chance of no more passes `share`
    (`strictly`) or reaches it; its largest count where none does."""
    total = 0.0
    for count in sorted(law):
        total = total + law[count]
        if total > share if strictly else total >= share:
            return count
    return max(law)


def tails_kept(
    days: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    published: "tuple[tuple[int | None, float | None, float | None], tuple[int | None, float | None, float | None]]",
    floor: int,
    edges: "tuple[int, int]",
    apart: bool,
    holes: "frozenset[int]",
    pins: "tuple[tuple[int, int], ...]",
    census_holes: "frozenset[int]" = frozenset(),
) -> "tuple[int, int]":
    """The fewest and the most different days the twin's two tails keep once its count pass has run: where it merges, but at a share of seeds no larger than `KEPT_MISS`; where it splits, the most they can hold.

    The first eight arguments are `tails_fewest`'s; `pins` are the body's
    pinned ranks with their days (`body_pins`) and `census_holes` the days
    the description publishes as holding no body cell (`public_holes`).
    The two count rules are handed these (the orchestrator's ruling of
    2026-10-07 on the price of plan P4-D388: a census its twins meet at
    nine seeds in ten or more stands): the room rule the most, the reach
    rule the fewest.

    THE COUNT PASS DECIDES WHAT THE TAILS KEEP (method G7.3's count
    passes), and it knows nothing of the census. Where the body's draw
    (`body_draw`, beside the census holes) and the days the two tails
    draw in expectation (`tail_days_law`) pass the column's count of
    different days, it MERGES runs onto held days, nearest first, then
    the shorter run, then the LOWER rank: the low tail's ranks are the
    column's lowest, so it is merged first, at most down to its fewest
    days (`_side_counted`), and the high tail's are the highest, so it
    keeps the days it drew -- each with the measured exceptions below.
    Where they fall short it SPLITS ranks onto free days, THE TWO TAILS'
    RANKS FIRST, then the body's, each nearest first and then the LOWER
    rank (since lane D4s, plan P4-D369 part one); a tail splits a rank
    only onto a free day inside that rank's own stratum, and only while
    the count wants more, so no body rank splits while a tail rank still
    can. Until lane D4s it split nearest first alone: a body rank one day
    from a free day split before any high tail rank whose free day was
    further, so the high tail kept the days it drew unless the body's
    nearer splits ran out first, and the low tail, first at each
    distance, ended below its most (`tails_most_rebuilt`) at two seeds or
    more on 10 of 272 censuses of logs just above one row an open day and
    64 of 125 of fresh logs where the pass split, none of them costing the
    count (plan P4-D388). So, merging, the
    FEWEST is the low tail's fewest and the least count
    the high tail draws with a chance above `KEPT_MISS` of drawing no
    more; and the MOST counts no merge at all -- the least count the two
    tails draw together with a chance of at least `1 - KEPT_MISS` of
    drawing no more. A merge only takes days away, so where the pass
    merges, the days the tails draw bound the days they keep; how far a
    merge takes the low tail is not read here, and a day it keeps is a day
    the body loses. Measured (plan P4-D388): the low tail kept a day or two
    above its fewest on the median of the twins measured and up to ten on
    a column of monthly dates whose low tail's days stand apart, whose
    census a most read at that fewest published, its twins long at every
    seed; it fell below its fewest only where the column's count leaves
    the body a few days or none beside the two tails' fewest, and the pass
    moves tail ranks out of their strata to meet it; and the high tail gave
    up days where the pass took more than a quarter of the body's drawn
    days, which the fewest does not count. Splitting, both are read at the
    two tails' most, and the body passes its draw only once the tails hold
    every day their strata give: on the 90 logs just above one row an
    open day of P4-D388's second verification, the censuses whose twins
    miss the count at two seeds or more fell from 21 of 310 published to
    1, and their twins short of the count from 97 to 7, each of the 7
    where the pass merges (plan P4-D369 part one, seeds 0 to 9); until
    lane D4s, the high tail kept the days it drew at more than a tenth of
    seeds there and a census the reach rule published could come back
    short at up to seven seeds in ten, the risk the orchestrator's ruling
    of 2026-10-08 let stand.

    Guarantees: accepts what `tails_fewest` accepts, the pins and the
    holes; returns the fewest and the most, the fewest never above the
    most. Determinism: a function of the arguments, in binary64. Raises
    nothing. No I/O of any kind.
    """
    rebuilt = (days, rows_low, rows_high, published, floor, edges, apart, holes)
    low = tail_days_law(*rebuilt, True)
    high = tail_days_law(*rebuilt, False)
    most = tails_most_rebuilt(*rebuilt)
    drawn = body_draw(pins, census_holes) + _law_mean(low) + _law_mean(high)
    if drawn <= len(set(days)):
        return most, most
    merged = _side_counted(
        days, rows_low, rows_high, published[0], floor, edges, apart, holes,
        True, False,
    )
    fewest = merged + _law_reached(high, KEPT_MISS, True)
    together: "dict[int, float]" = {}
    for low_days in sorted(low):
        for high_days in sorted(high):
            both = low_days + high_days
            chance = low[low_days] * high[high_days]
            together[both] = (together[both] if both in together else 0.0) + chance
    return fewest, max(fewest, _law_reached(together, 1.0 - KEPT_MISS, False))


def count_reach_short(
    groups: "tuple[tuple[int, int, int], ...]",
    pins: "tuple[tuple[int, int], ...]",
    days: int,
    fewest: int,
    most: int,
    holes: "frozenset[int]" = frozenset(),
) -> bool:
    """Whether the census leaves the body too few days for the count (the Codex review of plan P4-D388, item 2).

    THE COUNT-ROOM RULE'S OTHER DIRECTION, asked at every floor. `pins`
    are the body's pinned ranks with their days, ascending (`body_pins`);
    `days` is how many different days the column holds; `fewest` the
    fewest different days the twin's two tails keep once its count pass
    has run, but at a share of seeds no larger than `KEPT_MISS` where it
    merges, and their most where it splits (`tails_kept`, the
    orchestrator's ruling of 2026-10-07), and `most`
    the most they can hold as G7.3b rebuilds them
    (`tails_most_rebuilt`); `holes` the days the description publishes as
    holding no body cell (`public_holes`).

    WHERE THE CENSUS LETS THE BODY REACH. The twin's day pass moves a
    body rank only inside its gap, both pin days included, and onto no
    day of a group the census leaves empty and no hole, and each group
    holds no more different days than its count: so the body can REACH
    the distinct pin days and, inside each gap, as many of the days
    strictly inside it the census allows as the gap has ranks, and no
    more different days of a group than the group's count. Without the
    census it would reach every day inside each gap that is no hole, as
    many as the gap has ranks.

    WHAT THE COUNT ASKS OF IT. Before the day pass, the count pass meets
    the column's count of different days on the drawn twin, knowing
    nothing of the census. The body's ranks land on its DRAW
    (`body_draw`, beside the holes). Where the draw and the tails' most
    fall short of the count, the pass only SPLITS, moving ranks that share
    a day onto days no rank holds -- a tail's ranks onto free days of
    their own spans -- the two tails' ranks first, then the body's, each
    nearest first and then the lower rank (since lane D4s, plan P4-D369
    part one), and the rule reads the tails at their most: a tail splits
    a rank only onto a free day inside that rank's own stratum, and only
    while the count wants more, so no body rank splits while a tail rank
    still can -- one row a
    business day over four and a half years draws about 830 of its 1,180
    days and comes back holding every one. Until lane D4s it split
    nearest first alone, and the low tail, first at each distance, ended
    below its most at two seeds or more on 10 of 272 censuses of logs
    just above one row an open day and 64 of 125 of fresh logs where the
    pass split, none of them costing the count (plan P4-D388).
    Otherwise it MERGES, and merging only takes days away: the body keeps
    no more than its draw, and the tails no fewer than `fewest`. So the
    body's NEED is what the tails at their most leave it, and, where its
    draw passes that, as much of the draw as the tails at `fewest` leave
    room for.

    True where the need is more than the reach and the census narrows it
    -- without the census the body would reach further -- so the twin
    can lose a value to the census: a 14-day column whose high tail of 31
    rows the twin rebuilds on three days where the real tail held four,
    its body every weekday between the boundaries and the weekend empty,
    came back with 11 for 12 at every seed, and 12 with the census
    withheld. A need equal to the reach publishes the census.

    Its price and its risk are both measured (plan P4-D388): the low tail
    is read at its fewest, where a twin's low tail keeps a day or two more
    on the median, so where the margin is that narrow it withholds
    censuses their twins meet; and the tails are read at the share of
    seeds the ruling allows, and the draw at its expectation, so a twin of
    a census it publishes can still come back a value short at that share
    of seeds, and at more where its body draws past that expectation and
    the pass merges where the rule read a split: a Tuesday-to-Thursday
    clinic of 1.15 rows a clinic day over 45 weeks at the floor of 11
    draws 137 to 139 days for its 135 at seeds 2, 4, 6 and 8 and comes
    back one or two values short there (plan P4-D369 part one). Until lane
    D4s split the two tails' ranks first, 21 of the 310 censuses published
    on the 90 logs just above one row an open day came back one to four
    values short at two to seven seeds of ten, the high tail keeping the
    days it drew, a risk the orchestrator's ruling of 2026-10-08 let
    stand; 1 does now, where the pass merges.
    Each miss is one the twin's report and validation name.
    No day of the body's span is walked: the days of each weekday in a
    gap are counted, and the holes inside it set aside one by one.

    Guarantees: accepts the census, the pins, the count, the tails'
    fewest and most and the holes; returns the answer. Determinism: a
    function of the six, in binary64 where the draw is reckoned. Raises
    nothing. No I/O of any kind.
    """
    if not pins:
        return False
    where = where_of(groups)
    held: "list[int]" = []
    for _rank, day in pins:
        if day not in held:
            held += [day]
    first_day = pins[0][1]
    last_day = pins[len(pins) - 1][1]
    inside = sorted(day for day in holes if first_day <= day <= last_day)
    reach = len(held)
    free = len(held)
    at = 0
    for place in range(len(pins) - 1):
        rank, first = pins[place]
        following, last = pins[place + 1]
        while at < len(inside) and inside[at] <= first:
            at = at + 1
        inner = following - rank - 1
        if inner < 1 or last - first < 2:
            continue
        counts = _weekday_days(first + 1, last - 1)
        while at < len(inside) and inside[at] < last:
            weekday = weekday_of(inside[at])
            counts[weekday] = counts[weekday] - 1
            at = at + 1
        every = 0
        allowed = 0
        for weekday in range(WEEKDAYS):
            every = every + counts[weekday]
            if groups[where[weekday]][2] > 0:
                allowed = allowed + counts[weekday]
        reach = reach + min(inner, allowed)
        free = free + min(inner, every)
    draw = body_draw(pins, holes)
    spans = _weekday_days(first_day, last_day)
    for day in inside:
        weekday = weekday_of(day)
        spans[weekday] = spans[weekday] - 1
    capped = [0 for _group in groups]
    for weekday in range(WEEKDAYS):
        capped[where[weekday]] = capped[where[weekday]] + spans[weekday]
    room = 0
    for index in range(len(groups)):
        room = room + min(groups[index][2], capped[index])
    reach = min(reach, room)
    need = max(float(days - most), min(float(days - fewest), draw))
    return reach < free and need > reach


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


# THE WEEKDAY CENSUS OF A COLUMN OF MOMENTS (landing 3b.D2, plan
# P4-D367). A column of dates and times read on the local clock
# publishes the same census as a column of whole dates: its BODY's cells
# counted on the weekday of the day each falls on, the body being the
# cells between the two tail boundaries, both included, compared as
# instants (WC3). Three rules more than a column of dates asks, and one
# fewer: the middle half of the column spans at least four weeks (WC10),
# so a census of weekdays is never a census of a few dates; the body
# holds at least `FEWEST_MEAN_UNITS` different WRITTEN units a non-empty
# group on average wherever two or more groups are non-empty (the
# few-units rule, the producer's alone); and at every floor the units its
# tails leave it reach what the census needs between its pins (the
# unit-room rule, the producer's alone) -- on a column every value of
# which stands at midnight, which the twin counts and moves in days, the
# two count rules of a column of dates instead (`count_room_short` and
# `count_reach_short`); and WC6's half on written forms is not asked, as
# the count of different values on a column of moments is a count of
# instants, never of days -- its half on a workbook's storage is.

# WC10: the days the middle half of a column of moments spans at least,
# from its published `p25` to its published `p75` (four cycles of the
# week, the build plan's call (e), CA4).
SPAN_DAYS = 28
# THE FEW-UNITS RULE (the 3b.2-W skeptic's blocker 1, measured on the
# design's tie batteries): where two or more groups are non-empty, the
# body holds fewer than eight different written units a non-empty group
# on average -- instants at the column's precision, or days where every
# value stands at midnight -- and the census is withheld. Below it the
# day pass meets the census by splitting a written unit's rows across
# two days, and the twins measured that did held more different values
# than the column (seven sessions at 09:00, 17 for 9; payroll on the
# 15th and the last day at 18:00, 53 for 48). A CONSERVATIVE rule, like
# the few-dates rule beside it: it withholds some censuses a twin meets.
FEWEST_MEAN_UNITS = 8

# WHY A COLUMN OF MOMENTS PUBLISHES NO WEEKDAY CENSUS, besides the
# reasons of a column of dates: its middle half spans fewer than
# `SPAN_DAYS` days, its groups hold too few different written units, or
# its tails leave its body too few for the census (`unit_room_short`).
# Each is said in the one sentence of every rule the table's own numbers
# decide (NF74, `REASON_UNSAID`).
REASON_SPAN = "span"
REASON_FEW_UNITS = "few_units"
REASON_UNIT_ROOM = "unit_room"
MOMENTS_REASONS = (REASON_SPAN, REASON_FEW_UNITS, REASON_UNIT_ROOM)


def span_short(p25: "int | None", p75: "int | None") -> bool:
    """WC10: whether a column's middle half spans fewer than four weeks.

    `p25` and `p75` are the days of the column's published rungs of
    those names, None where a rung is withheld: a middle half no reader
    can measure is held short, so no census stands beside it.

    Guarantees: accepts two day numbers or None; returns the answer.
    Determinism: a function of the two. Raises nothing. No I/O of any
    kind.
    """
    if p25 is None or p75 is None:
        return True
    return p75 - p25 < SPAN_DAYS


def few_units(
    groups: "tuple[tuple[int, int, int], ...]",
    body: "list[int]",
    units: "list[int]",
) -> bool:
    """Whether the census's groups hold too few different written units (P4-D367).

    THE PRODUCER'S FEW-UNITS RULE, on the REAL body: `body` is the day
    of every body cell and `units` its written unit (its instant in
    whole units of the column's precision, or its day where every value
    stands at midnight), in the same order. True where at least two
    groups are non-empty and they hold fewer than `FEWEST_MEAN_UNITS`
    different written units each on average. A CONSERVATIVE rule, set on
    the measured cases where a twin missed its count of different values
    (module text above), not a proof that no twin can meet the census;
    a rule of what the twin is sure to meet, never of what a reader
    could work out, so the loader cannot ask it, and need not.

    Guarantees: accepts the census, the body's days and its written
    units, one each a cell; returns the answer. Determinism: a function
    of the three. Raises nothing. No I/O of any kind.
    """
    where = where_of(groups)
    held = [0 for _group in groups]
    for index, _unit in {
        (where[weekday_of(day)], unit) for day, unit in zip(body, units)
    }:
        held[index] = held[index] + 1
    filled = [held[index] for index in range(len(groups)) if groups[index][2] > 0]
    return len(filled) >= 2 and sum(filled) < FEWEST_MEAN_UNITS * len(filled)


def moments_pins(
    moments: "tuple[int, ...]",
    rows_low: int,
    rows_high: int,
    percents: "list[int]",
) -> "tuple[tuple[int, int], ...]":
    """The body's pinned ranks with their instants, ascending (method G7.3).

    The ranks no pass of the twin moves inside the body: the two tail
    boundaries, ranks `rows_low` and `len(moments) - 1 - rows_high`, and
    each published rung strictly between them, at the rank its percent is
    read off -- `(len(moments) - 1) * percent // 100`, as the generator
    lays it. `moments` is the instant of every parsed cell ascending and
    `percents` the percents of the published rungs.

    Guarantees: accepts the instants, the two tails' rows (a body of at
    least one rank between them) and the percents; returns each pinned
    rank once with its instant. Determinism: a function of the four.
    Raises nothing. No I/O of any kind.
    """
    parsed = len(moments)
    high = parsed - 1 - rows_high
    found = [(rows_low, moments[rows_low])]
    for percent in sorted(set(percents)):
        rank = min(parsed - 1, ((parsed - 1) * percent) // 100)
        if found[len(found) - 1][0] < rank < high:
            found += [(rank, moments[rank])]
    if high > found[len(found) - 1][0]:
        found += [(high, moments[high])]
    return tuple(found)


def unit_room_short(
    groups: "tuple[tuple[int, int, int], ...]",
    pins: "tuple[tuple[int, int], ...]",
    step: int,
    units: int,
    tails: int,
) -> bool:
    """Whether the body is left too few written units for the census (plan P4-D367).

    THE PRODUCER'S UNIT-ROOM RULE ON A COLUMN OF MOMENTS, asked at every
    floor of a column whose values do not all stand at midnight (one that
    does asks `count_room_short` and `count_reach_short`, as a column of
    dates does): lane D1b's count-room rule for whole dates (plan
    P4-D388), restated in WRITTEN units. Asked above the floor of 11
    alone until skeptic 1 of landing 3b.D2 (item 1) wrote `_hunt(690)`
    with one cell moved at noon: at 11 it published Monday to Friday 73
    and the weekend 31, and every twin came back 26 different values for
    24; asked, the rule withholds it. `pins` are the body's
    pinned ranks with their instants, ascending (`moments_pins`); `step`
    the seconds a written unit spans; `units` how many different written
    units the column holds; `tails` the most its twin's two tails can
    hold (the floor's number on a side publishing its two distances, its
    rows where fewer, the count of a side listing its values).

    The twin's count pass leaves the body at least `units - tails`
    different values, its ROOM, and may stack a body rank on a pin's own
    instant. Its day pass moves a body rank only inside its gap, between
    the pins either side, so the census NEEDS every pin's written unit
    and, inside each gap, one more for each group holding rows that has a
    day strictly between the two pin days and stands on neither (at most
    one a rank of the gap). True where the census needs a unit past the
    pins' and the room is less than the need: measured at a floor of 36,
    a Wednesday schedule written at noon, 35 different values and tails
    of 59 and 40 rows, was left three by its tails, its pins, and asked
    for two Thursdays more: its twins held 37. A CONSERVATIVE rule: a
    tail rebuilt rarely holds the floor's number, so it withholds some
    censuses a twin would meet, and that is its price (plan P4-D367).

    Guarantees: accepts the census, the pins, the written unit, the
    count and the tails' most; returns the answer. Determinism: a
    function of the five. Raises nothing. No I/O of any kind.
    """
    where = where_of(groups)
    held: "list[int]" = []
    for _rank, instant in pins:
        if instant // step not in held:
            held += [instant // step]
    need = len(held)
    for place in range(len(pins) - 1):
        rank, first = pins[place]
        following, last = pins[place + 1]
        inner = following - rank - 1
        first_day, last_day = first // 86400, last // 86400
        if inner < 1 or last_day <= first_day:
            continue
        ends = (where[weekday_of(first_day)], where[weekday_of(last_day)])
        found: "list[int]" = []
        for day in range(first_day + 1, min(last_day, first_day + WEEKDAYS)):
            index = where[weekday_of(day)]
            if groups[index][2] > 0 and index not in ends and index not in found:
                found += [index]
        need = need + min(len(found), inner)
    return need > len(held) and units - tails < need


def moments_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    body: int,
    line: int,
    p25: "int | None",
    p75: "int | None",
) -> "tuple[str, str, str] | None":
    """The loader's check of a weekday census on a column of moments (P4-D367).

    WC1 to WC4 as on a column of dates (`shape_breach`), with WC6's half
    on written forms not asked -- the count of different values counts
    instants there, never days -- and then WC10, the middle half
    spanning at least `SPAN_DAYS` days (`span_short`). The first broken
    rule is returned as (rule, what the census says, what the rule
    asks); an empty census breaks nothing.

    Guarantees: accepts the census, the body, the census line and the
    days of the published `p25` and `p75` (None where withheld);
    returns None or the broken rule. Determinism: a function of the
    five. Raises nothing. No I/O of any kind.
    """
    if not groups:
        return None
    broken = shape_breach(groups, body, line, True)
    if broken is not None:
        return broken
    if span_short(p25, p75):
        return (
            "WC10",
            "a weekday census is published on a column of moments whose "
            "middle half spans fewer than four weeks",
            f"the column's p75 stands at least {SPAN_DAYS} days after its "
            f"p25, both published",
        )
    return None


# anchor 3b-D3 (P4-D368)


# THE DAY-OF-MONTH CENSUS (landing 3b.3, plan P4-D368, contract DM1 to
# DM5). A column of whole dates -- or of moments every value of which
# stands at midnight on the local clock, which the twin counts and moves
# in days (the 3b.3 skeptic's major 4) -- publishes `day_of_month_census`:
# how many cells of its BODY, the cells between the two tail boundaries,
# both included, fall on each day of the month, in GROUPS of consecutive
# BINS whose count is nought or at least the census line. Thirty-four
# bins, numbered from 1: bins 1 to 27 the days 1 to 27; bins 28, 29 and
# 30 the 28th, 29th and 30th of a month where that day is NOT the last;
# and bins 31, 32, 33 and 34 the month's LAST day, in a month of 28, 29,
# 30 and 31 days. A month-end heap so comes back on the month's last day,
# never on a 31st a 30-day month does not hold (the design measured 0.43
# of 0.612 with plain days), and a heap on the 30th never puts one on the
# 31st (the skeptic's minor 2: 0.13 against a real 0.009). The bins are a
# CYCLE: bin 34, the last day of a long month, neighbours bin 1.

MONTH_DAY_BINS = 34
# The first bin of the month's last day: a month of 28 days's.
MONTH_LAST_FIRST_BIN = 31
# THE FEW-DATES RULE OF THE DAY OF THE MONTH (the 3b.3 skeptic's blocker
# 1 (a), measured): a group that holds rows holds them on at least four
# different body dates, or no census is published. Every column whose
# twins missed their count of different values had a group of one to
# three dates; every column whose twins held it had four or more.
FEWEST_MONTH_DATES = 4
# DM4: the days the middle half of the column spans at least, from its
# published `p25` to its published `p75` (four months), so no census of
# days of the month is a census of a few dates.
MONTH_SPAN_DAYS = 124
# THE LINE A DAY OF THE MONTH DEPARTS BY, in chi-squared per degree of
# freedom, before a census of it is published (plan P4-D368).
MONTH_SCORE_LINE = 4.0
# The days of a 400-year Gregorian cycle: a whole number of weeks, so the
# weekday of every day of the month repeats with it.
_CYCLE_DAYS = 146097
_CYCLE_MONTHS = 4800

# WHY A COLUMN WHOSE DAY OF THE MONTH DEPARTS PUBLISHES NO CENSUS OF IT:
# a body day stands on a published hole, its middle half spans fewer than
# `MONTH_SPAN_DAYS` days (DM4), a group holds fewer than
# `FEWEST_MONTH_DATES` different dates, the two censuses leave the body
# too few days for the count (`month_reach_short`), or the loader's own
# check refuses the census (`REASON_NARROWED`). Said in one publication
# note.
REASON_MONTH_HOLE = "month_hole"
REASON_MONTH_SPAN = "month_span"
REASON_MONTH_FEW_DATES = "month_few_dates"
REASON_MONTH_REACH = "month_reach"
MONTH_REASONS = (
    REASON_MONTH_HOLE, REASON_MONTH_SPAN, REASON_MONTH_FEW_DATES,
    REASON_MONTH_REACH, REASON_NARROWED,
)
# The names `day_census_breach` reports its rules under.
MONTH_CENSUS_RULES = ("DM1", "DM2", "DM3", "DM2")


def month_length(year: int, month: int) -> int:
    """How many days a month of the proleptic Gregorian calendar holds.

    Guarantees: accepts a year and a month from 1 to 12; returns 28 to
    31. Determinism: a fixed function. Raises nothing. No I/O.
    """
    if month == 2:
        leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        return 29 if leap else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31


def month_bin_of(date: int, length: int) -> int:
    """The bin, from 1 to 34, of the `date`-th day of a month of `length` days.

    Guarantees: accepts a day of the month and its month's length;
    returns its bin. Determinism: a fixed function. Raises nothing. No
    I/O of any kind.
    """
    if date == length:
        return length + MONTH_LAST_FIRST_BIN - 28
    return date


def month_bin(day: int) -> int:
    """The bin, from 1 to 34, a day number falls in (module text above).

    Guarantees: accepts a day number counted from 1970-01-01; returns its
    bin. Determinism: a fixed function. Raises nothing. No I/O of any
    kind.
    """
    year, month, date = parsing.civil_from_days(day)
    return month_bin_of(date, month_length(year, month))


def month_bins(days: "list[int]") -> "list[int]":
    """How many of these days fall in each bin, bin 1 first.

    Guarantees: accepts day numbers; returns thirty-four counts.
    Determinism: a function of the days. Raises nothing. No I/O.
    """
    bins = [0 for _ in range(MONTH_DAY_BINS)]
    for day in days:
        index = month_bin(day) - 1
        bins[index] = bins[index] + 1
    return bins


def month_where(groups: "tuple[tuple[int, int, int], ...]") -> "tuple[int, ...]":
    """Each bin's group, bin 1 first, on a census that may wrap past bin 34.

    Guarantees: accepts the groups, bins from 1; returns thirty-four
    group indices. Determinism: a function of the groups. Raises
    nothing. No I/O of any kind.
    """
    where = [0 for _ in range(MONTH_DAY_BINS)]
    for index in range(len(groups)):
        first, last, _count = groups[index]
        position = first
        while True:
            if 1 <= position <= MONTH_DAY_BINS:
                where[position - 1] = index
            if position == last or not 1 <= position <= MONTH_DAY_BINS:
                break
            position = position % MONTH_DAY_BINS + 1
    return tuple(where)


def month_groups(bins: "list[int]", line: int) -> "tuple[tuple[int, int, int], ...]":
    """The groups a day-of-month census publishes, or none (plan P4-D368).

    The one merge rule of every census of bins (`merged_groups`), on a
    CYCLE (the skeptic's major 1): a bin at the line stands alone, a run
    of empty bins is one group of nought, and a short group joins its
    smaller NON-ZERO neighbour, so a heap day is never folded into the
    empty run beside it; where everything merges into one group, no
    census. Numbered from 1.

    Guarantees: accepts thirty-four counts and the line; returns
    `(first, last, count)` per group, or `()`. Determinism: a function
    of the two. Raises nothing. No I/O of any kind.
    """
    merged = merged_groups(bins, [], line, cyclic=True)
    return tuple((first + 1, last + 1, count) for first, last, count in merged)


def month_calendar(
    low: int, high: int, holes: "tuple[int, ...]" = ()
) -> "list[list[int]]":
    """How many calendar days from `low` to `high` fall on each weekday and bin.

    COUNTED, NEVER WALKED DAY BY DAY (review of landing 3b.1, finding
    10): whole 400-year cycles at once, then month by month, every whole
    month by its length and the weekday of its first day, so a span of
    6,000 years costs at most two cycles' months, as 800 years do; a day
    of `holes` between the two is taken off. Each weekday is reckoned
    here, `weekday_of`'s own sum, never asked of it day by day.
    `[weekday][bin - 1]`, Monday nought.

    Guarantees: accepts two day numbers and the holes; returns seven
    rows of thirty-four counts. Determinism: a function of the three.
    Raises nothing. No I/O of any kind.
    """
    table = [[0 for _ in range(MONTH_DAY_BINS)] for _ in range(WEEKDAYS)]
    if high < low:
        return table
    kinds: "dict[tuple[int, int], int]" = {}
    cycles = (high - low + 1) // _CYCLE_DAYS
    start = low + cycles * _CYCLE_DAYS
    if cycles:
        year, month, _date = parsing.civil_from_days(low)
        for _month in range(_CYCLE_MONTHS):
            first = parsing.days_from_civil(year, month, 1)
            key = (month_length(year, month), (first + 3) % WEEKDAYS)
            kinds[key] = (kinds[key] if key in kinds else 0) + cycles
            year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    year, month, _date = parsing.civil_from_days(start)
    while True:
        first = parsing.days_from_civil(year, month, 1)
        if first > high:
            break
        length = month_length(year, month)
        begin = max(1, start - first + 1)
        end = min(length, high - first + 1)
        if begin == 1 and end == length:
            key = (length, (first + 3) % WEEKDAYS)
            kinds[key] = (kinds[key] if key in kinds else 0) + 1
        else:
            for date in range(begin, end + 1):
                row = table[(first + date + 2) % WEEKDAYS]
                index = month_bin_of(date, length) - 1
                row[index] = row[index] + 1
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    for length, weekday in sorted(kinds):
        count = kinds[(length, weekday)]
        for date in range(1, length + 1):
            row = table[(weekday + date - 1) % WEEKDAYS]
            index = month_bin_of(date, length) - 1
            row[index] = row[index] + count
    for hole in sorted(set(holes)):
        if low <= hole <= high:
            row = table[(hole + 3) % WEEKDAYS]
            index = month_bin(hole) - 1
            row[index] = row[index] - 1
    return table


def _per_freedom(observed: "list[int]", weights: "list[float]") -> float:
    """Chi-squared per degree of freedom of these counts against weights.

    Each count's expectation is the counts' total shared out in
    proportion to the weights; a cell of no weight is not asked. Nought
    where fewer than two cells are asked or nothing is counted.
    """
    asked = [index for index in range(len(observed)) if weights[index] > 0]
    total = sum(observed[index] for index in asked)
    mass = sum(weights[index] for index in asked)
    if len(asked) < 2 or total <= 0 or mass <= 0:
        return 0.0
    score = 0.0
    for index in asked:
        expected = total * weights[index] / mass
        score = score + (observed[index] - expected) ** 2 / expected
    return score / (len(asked) - 1)


def day_scores(
    groups: "tuple[tuple[int, int, int], ...]",
    weekdays: "tuple[tuple[int, int, int], ...]",
    table: "list[list[int]]",
) -> "tuple[float, float]":
    """How far the day of the month and the weekday each depart beyond the other.

    THE PRODUCER'S TWO SCORES (plan P4-D368), both on the PUBLISHED
    groups (the 3b.3 skeptic's major 2), over the calendar `table`
    (`month_calendar`, the holes taken off): the day-of-month groups'
    chi-squared per degree of freedom against the calendar weighted by
    the weekday census's rate per calendar day of each weekday group --
    by nothing where no weekday census is published -- and the weekday
    groups' that hold rows, against the calendar weighted by the
    day-of-month census's rate per calendar day of each of its groups.

    Guarantees: accepts the two censuses (bins from 1, weekdays from 0)
    and the calendar; returns the two scores. Determinism: a function
    of the three. Raises nothing. No I/O of any kind.
    """
    where_days = month_where(groups)
    week_rate = [1.0 for _ in range(WEEKDAYS)]
    if weekdays:
        where_week = where_of(weekdays)
        held = [0 for _ in weekdays]
        for weekday in range(WEEKDAYS):
            held[where_week[weekday]] = held[where_week[weekday]] + sum(table[weekday])
        for weekday in range(WEEKDAYS):
            group = where_week[weekday]
            week_rate[weekday] = (
                weekdays[group][2] / held[group] if held[group] > 0 else 0.0
            )
    weights = [0.0 for _ in groups]
    for weekday in range(WEEKDAYS):
        for index in range(MONTH_DAY_BINS):
            group = where_days[index]
            weights[group] = weights[group] + table[weekday][index] * week_rate[weekday]
    month_score = _per_freedom([count for _first, _last, count in groups], weights)
    if not weekdays:
        return month_score, 0.0
    held_days = [0 for _ in groups]
    for weekday in range(WEEKDAYS):
        for index in range(MONTH_DAY_BINS):
            group = where_days[index]
            held_days[group] = held_days[group] + table[weekday][index]
    where_week = where_of(weekdays)
    week_weights = [0.0 for _ in weekdays]
    for weekday in range(WEEKDAYS):
        group = where_week[weekday]
        if weekdays[group][2] <= 0:
            continue
        for index in range(MONTH_DAY_BINS):
            place = where_days[index]
            if held_days[place] > 0:
                week_weights[group] = (
                    week_weights[group]
                    + table[weekday][index] * groups[place][2] / held_days[place]
                )
    week_score = _per_freedom([count for _first, _last, count in weekdays], week_weights)
    return month_score, week_score


def day_of_month_stands(month_score: float, week_score: float, weekdays: bool) -> bool:
    """Whether the day of the month departs enough to be published (plan P4-D368).

    (a) Beside a published weekday census: it departs by at least
    `MONTH_SCORE_LINE` beyond the weekday AND more than the weekday
    departs beyond it. (b) With none: it departs by at least the line
    from the plain calendar. The weekday census is never withdrawn (the
    design's 2.2: CA6 read literally lost 7 of 10 weekday censuses).
    """
    if month_score < MONTH_SCORE_LINE:
        return False
    return not weekdays or month_score > week_score


def few_month_dates(
    groups: "tuple[tuple[int, int, int], ...]",
    body: "list[int]",
    table: "list[list[int]]",
) -> bool:
    """Whether a group holding rows holds too few different body dates.

    THE PRODUCER'S RULE (the 3b.3 skeptic's blocker 1 (a)), on the REAL
    body's days: true where a group holding rows holds them on fewer than
    `FEWEST_MONTH_DATES` different dates, unless the group counts only a
    month's last day (bins 31 to 34, never wrapping) and holds a date on
    every one the calendar `table` (`month_calendar`, the holes taken
    off) gives it between the two boundaries. Below four the day pass
    meets the census by splitting a date's rows across the group's other
    days, and the twins measured that did held more different values than
    the column (sessions, forty tied dates); a month's last day whose
    every calendar date holds rows has no other day to split onto -- the
    last day of February, one date a year, is such a group on a short
    column. Any other group of fewer than four dates leaves the weekday
    pass, which keeps each rank's group, too few dates to move between
    weekdays: May alone over three years, its other months empty by its
    written month names, held every bin's three dates and its twins
    missed the weekday census at every seed the weekday pass alone had
    met (repair of landing 3b.3). ITS PRICE, STATED (P4-D368): three and
    four Mays at 1,000 rows and a floor of 36 publish no census, where
    every group standing on its calendar published 11 and 12 groups, the
    heaps on the 1st and the 15th among them, and every twin met both
    censuses. A conservative rule set on the measured
    cases, never a rule of what a reader could work out, so the loader
    cannot ask it, and need not.

    Guarantees: accepts the census, the body's days and the calendar;
    returns the answer. Determinism: a function of the three. Raises
    nothing. No I/O of any kind.
    """
    where = month_where(groups)
    held = [0 for _ in groups]
    for day in sorted(set(body)):
        index = where[month_bin(day) - 1]
        held[index] = held[index] + 1
    days = [0 for _ in groups]
    for row in table:
        for index in range(MONTH_DAY_BINS):
            days[where[index]] = days[where[index]] + row[index]
    for index in range(len(groups)):
        first, last, count = groups[index]
        month_ends = MONTH_LAST_FIRST_BIN <= first <= last
        if (
            count > 0
            and held[index] < FEWEST_MONTH_DATES
            and (held[index] < days[index] or not month_ends)
        ):
            return True
    return False


def _month_allowed(
    table: "list[list[int]]",
    groups: "tuple[tuple[int, int, int], ...]",
    weekdays: "tuple[tuple[int, int, int], ...]",
) -> "tuple[int, int, list[int]]":
    """Of a calendar table (`month_calendar`): every day, the days both
    censuses allow -- a bin of a group counting rows and a weekday of a
    group counting rows (any weekday where none is published) -- and the
    allowed days of each day-of-month group."""
    where = month_where(groups)
    week = where_of(weekdays) if weekdays else ()
    every = 0
    allowed = 0
    per = [0 for _ in groups]
    for weekday in range(WEEKDAYS):
        open_day = not weekdays or weekdays[week[weekday]][2] > 0
        for index in range(MONTH_DAY_BINS):
            count = table[weekday][index]
            every = every + count
            if open_day and groups[where[index]][2] > 0:
                allowed = allowed + count
                per[where[index]] = per[where[index]] + count
    return every, allowed, per


def month_reach_short(
    groups: "tuple[tuple[int, int, int], ...]",
    weekdays: "tuple[tuple[int, int, int], ...]",
    pins: "tuple[tuple[int, int], ...]",
    days: int,
    fewest: int,
    most: int,
    holes: "frozenset[int]" = frozenset(),
) -> bool:
    """Whether the two censuses leave the body too few days for the count (plan P4-D368).

    THE COUNT-REACH RULE OF A COLUMN OF DAYS (`count_reach_short`, plan
    P4-D388 and its Codex review, item 2), asked of the day-of-month
    census beside the weekday census: the body REACHES its distinct pin
    days and, inside each gap, as many of the days strictly inside it
    that both censuses allow -- a bin of a day-of-month group counting
    rows, on a weekday of a weekday group counting rows, no hole -- as
    the gap has ranks, and no more different days of a day-of-month group
    than its count; it NEEDS what the twin's rebuilt tails at their most
    (`most`) leave of the column's count of different days (`days`), and,
    where its draw passes that, as much of the draw as the tails at their
    fewest (`fewest`) leave room for. True where the need is more than
    the reach and the censuses narrow it. Measured on a monthly visit at
    10,000 rows and a floor of 36: its body held every one of the 160
    days of the 7th to the 13th, its rebuilt tails two days fewer than
    the real ones, and every twin came back 166 days for 168. The calendar
    is counted, never walked (`month_calendar`). A conservative rule of
    what the twin is sure to meet, never of what a reader could work out.

    Guarantees: accepts the two censuses, the pins, the count, the
    tails' fewest and most and the holes; returns the answer.
    Determinism: a function of the seven, in binary64 where the draw is
    reckoned. Raises nothing. No I/O of any kind.
    """
    if not pins:
        return False
    held: "list[int]" = []
    for _rank, day in pins:
        if day not in held:
            held += [day]
    first_day = pins[0][1]
    last_day = pins[len(pins) - 1][1]
    inside = tuple(day for day in holes if first_day <= day <= last_day)
    reach = len(held)
    free = len(held)
    for place in range(len(pins) - 1):
        rank, first = pins[place]
        following, last = pins[place + 1]
        inner = following - rank - 1
        if inner < 1 or last - first < 2:
            continue
        every, allowed, _per = _month_allowed(
            month_calendar(first + 1, last - 1, inside), groups, weekdays
        )
        reach = reach + min(inner, allowed)
        free = free + min(inner, every)
    _every, _allowed, per = _month_allowed(
        month_calendar(first_day, last_day, inside), groups, weekdays
    )
    room = 0
    for index in range(len(groups)):
        room = room + min(groups[index][2], per[index])
    reach = min(reach, room)
    draw = body_draw(pins, holes)
    need = max(float(days - most), min(float(days - fewest), draw))
    return reach < free and need > reach


def month_span_short(p25: "int | None", p75: "int | None") -> bool:
    """DM4: whether the column's middle half spans fewer than `MONTH_SPAN_DAYS` days.

    A middle half no reader can measure, a rung withheld, is held short.
    """
    if p25 is None or p75 is None:
        return True
    return p75 - p25 < MONTH_SPAN_DAYS


def day_census_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    body: int,
    line: int,
    p25: "int | None",
    p75: "int | None",
) -> "tuple[str, str, str] | None":
    """The loader's check of one published day-of-month census, or None (P4-D368).

    DM1 the groups cover bins 1 to 34 in order, each once, the last
    alone running past bin 34 back to bin 1; DM2 every count is nought
    or at least the line (`calendar_floor_ok`); DM3 the counts add to
    the body -- the three asked through the one checker of every census
    of stage 3b (`census_breach`); then DM4, the middle half spanning
    at least `MONTH_SPAN_DAYS` days. DM5, the column's scope, is the
    loader's, read off the block. An empty census breaks nothing.

    Guarantees: accepts the census, the body, the census line and the
    days of the published `p25` and `p75` (None where withheld);
    returns None or the broken rule as (rule, what the census says,
    what the rule asks). Determinism: a function of the five. Raises
    nothing. No I/O of any kind.
    """
    if not groups:
        return None
    broken = census_breach(
        groups, MONTH_DAY_BINS, line, body, cyclic=True, low=1, unit="bin",
        rules=MONTH_CENSUS_RULES,
    )
    if broken is not None:
        return broken
    if month_span_short(p25, p75):
        return (
            "DM4",
            "a day-of-month census is published on a column whose middle "
            "half spans fewer than four months",
            f"the column's p75 stands at least {MONTH_SPAN_DAYS} days after "
            f"its p25, both published",
        )
    return None



# anchor 3b-D4 (P4-D369)
# THE DATES THAT STAND OUT (landing 3b.6, plan P4-D369, contract HD1 to
# HD5). A date of the body stands out where it holds at least the heavy
# line and at least three times the mean of the three dates either side
# (`standing_out`, the mean, three either side); the column then
# publishes `heavy_dates`, each such date with its exact count, and the
# twin holds every one of them exactly.
HEAVY_FLOOR = 11
HEAVY_REACH = 3
HEAVY_RULES = ("HD1", "HD2", "HD3", "HD4", "HD5")


def heavy_line(floor: int) -> int:
    """The least count a listed date may hold: eleven, or the census line.

    The orchestrator's call of 2026-10-01 (plan section 8, its minors):
    heavy dates list at `max(11, line)`, so a floor of one or two, whose
    census line is two, lists no noise on an ordinary column.

    Guarantees: accepts the settings floor; returns the line.
    Determinism: a fixed function. Raises nothing. No I/O of any kind.
    """
    return max(HEAVY_FLOOR, census_line(floor))


def heavy_scope(
    resolution: str,
    all_at_midnight: bool,
    read_at: str,
    family: str,
    tails: bool,
) -> bool:
    """Whether a column may list dates that stand out (the 3b.6 skeptic's M1).

    THE ONE STATEMENT the producer, the loader, the generator and the
    validator each ask: a column the twin counts in days -- whole dates,
    or moments every value of which stands at midnight -- read on the
    local clock, not in the joint member, with both tails. A column of
    moments with a clock lists none (a stated limit of plan P4-D369).

    Guarantees: accepts the block's resolution, whether every value is
    at midnight, its clock, its member and whether both tails stand;
    returns the answer. Determinism: a function of the five. Raises
    nothing. No I/O of any kind.
    """
    if resolution != "date" and not (resolution == "datetime" and all_at_midnight):
        return False
    return read_at == "local" and family != "iso-mixed" and tails


def heavy_listed(
    counts: "dict[int, int]",
    first: int,
    last: int,
    line: int,
    holes: "frozenset[int]",
) -> "tuple[tuple[int, int], ...]":
    """The dates from `first` to `last` that stand out, with their counts.

    `counts` holds the parsed cells of the WHOLE column on each day,
    tail cells included, so a date beside a boundary is judged against
    every cell around it; a day with no cell holds nought. A date stands
    out by `standing_out` (the mean of the `HEAVY_REACH` days either
    side, at least the line and three times it, in whole numbers); a
    hole of the description is never listed.

    Guarantees: accepts the counts, the first and last day that may be
    listed, the line and the holes; returns `(day, count)` ascending.
    Linear in the days from `first` to `last`. Determinism: a function
    of the five. Raises nothing. No I/O of any kind.
    """
    if last < first:
        return ()
    start = first - HEAVY_REACH
    stop = last + HEAVY_REACH
    span = [counts[day] if day in counts else 0 for day in range(start, stop + 1)]
    found: "list[tuple[int, int]]" = []
    for index, count in standing_out(span, line, HEAVY_REACH, CENTRE_MEAN):
        day = start + index
        if first <= day <= last and day not in holes:
            found += [(day, count)]
    return tuple(found)


def heavy_runs(
    knots: "tuple[tuple[int, int], ...]",
    listed: "tuple[tuple[int, int], ...]",
    holes: "frozenset[int]",
) -> "tuple[tuple[int, int], ...] | None":
    """HD4: where each listed date's run of ranks may start, or None.

    The knots are the body's pinned ranks with their days, ascending --
    the low boundary first, each published rung, the high boundary last
    (`body_pins`). A listed date of count c is a run of c consecutive
    ranks on its day: every knot on that day stands inside the run, every
    knot on an earlier day before it and every knot on a later day after
    it, inside the body, and the runs follow one another in day order.
    Between two listed dates with no knot between them, the ordinary
    ranks need a day of their own: where every day between them is a
    hole, the second run starts where the first ends. The bounds are
    carried forward and then back along the runs, which on a chain of
    such constraints is exact.

    Guarantees: accepts the knots, the listed dates ascending and the
    holes; returns `(first, last)` start rank per listed date, or None
    where no rank order holds them all. Linear in the knots, the listed
    dates and the days between listed dates. Determinism: a function of
    the three. Raises nothing. No I/O of any kind.
    """
    if not listed or not knots:
        return ()
    low_rank = knots[0][0]
    high_rank = knots[len(knots) - 1][0]
    lows: "list[int]" = []
    highs: "list[int]" = []
    forced: "list[bool]" = []
    below = 0
    for index in range(len(listed)):
        day, count = listed[index]
        while below < len(knots) and knots[below][1] < day:
            below = below + 1
        above = below
        while above < len(knots) and knots[above][1] == day:
            above = above + 1
        least = low_rank
        most = high_rank - count + 1
        if below > 0:
            least = max(least, knots[below - 1][0] + 1)
        if above < len(knots):
            most = min(most, knots[above][0] - count)
        if above > below:
            least = max(least, knots[above - 1][0] - count + 1)
            most = min(most, knots[below][0])
        lows += [least]
        highs += [most]
        tied = False
        if index > 0:
            before = listed[index - 1][0]
            between = below > 0 and knots[below - 1][1] > before
            free = any(
                other not in holes for other in range(before + 1, day)
            )
            tied = not between and not free
        forced += [tied]
    for index in range(1, len(listed)):
        step = listed[index - 1][1]
        lows[index] = max(lows[index], lows[index - 1] + step)
        if forced[index]:
            highs[index] = min(highs[index], highs[index - 1] + step)
    for index in range(len(listed) - 2, -1, -1):
        step = listed[index][1]
        highs[index] = min(highs[index], highs[index + 1] - step)
        if forced[index + 1]:
            lows[index] = max(lows[index], lows[index + 1] - step)
    found: "list[tuple[int, int]]" = []
    for index in range(len(listed)):
        if lows[index] > highs[index]:
            return None
        found += [(lows[index], highs[index])]
    return tuple(found)


def _heavy_group_breach(
    listed: "tuple[tuple[int, int], ...]",
    census: "tuple[tuple[int, int, int], ...]",
    bin_of: str,
) -> "tuple[str, str, str] | None":
    """HD3 beside one census: no group's listed rows exceed its count."""
    if not census:
        return None
    where = where_of(census) if bin_of == "weekday" else month_where(census)
    held = [0 for _ in census]
    for day, count in listed:
        if bin_of == "weekday":
            group = where[weekday_of(day)]
        else:
            group = where[month_bin(day) - 1]
        held[group] = held[group] + count
    for index in range(len(census)):
        if held[index] > census[index][2]:
            return (
                "HD3",
                f"the listed dates of one {bin_of} group hold {held[index]} rows",
                f"at most that group's published count, {census[index][2]}",
            )
    return None


def heavy_breach(
    listed: "tuple[tuple[int, int], ...]",
    line: int,
    room: "tuple[int, int, int, int]",
    holes: "frozenset[int]",
    knots: "tuple[tuple[int, int], ...]",
    censuses: "tuple[tuple[tuple[int, int, int], ...], tuple[tuple[int, int, int], ...]]",
) -> "tuple[str, str, str] | None":
    """The loader's check of one published list of heavy dates, or None (P4-D369).

    THE ONE STATEMENT the loader and the producer's self-check ask, in
    order, the first broken rule returned by name:

    * HD1 every date strictly after the one before it, from the low
      boundary to the high boundary (`room`'s first two), on no hole;
    * HD2 every count at least the heavy line (`heavy_line`), never
      nought;
    * HD3 the counts add to at most the body (`room`'s third), the list
      holds at most as many dates as the column's different parsed
      values (its fourth), and beside a weekday census or a day-of-month
      census (`censuses`) no group's listed rows exceed its count;
    * HD4 the knots and the runs fit one rank order (`heavy_runs`);
    * HD5 every listed date holds at least half the listed rows within
      three days of it (2c >= their sum): a list that runs on as a daily
      series breaks it.

    Guarantees: accepts the list `(day, count)`, the line, `(low, high,
    body rows, different parsed values)`, the holes, the knots and the
    weekday and day-of-month censuses; returns None or (rule, what the
    list says, what the rule asks). Determinism: a function of the six.
    Raises nothing. No I/O of any kind.
    """
    if not listed:
        return None
    low, high, body, different = room
    previous = low - 1
    for day, _count in listed:
        if day <= previous or day > high or day in holes:
            return (
                "HD1",
                "a listed date out of order, outside the two boundaries or "
                "on a day the description holds empty",
                "dates strictly ascending from the low boundary to the high "
                "boundary, none on a hole",
            )
        previous = day
    for _day, count in listed:
        if count < line or count <= 0:
            return (
                "HD2",
                f"a listed date holding {count} rows",
                f"every listed count at least {line}",
            )
    total = sum(count for _day, count in listed)
    if total > body:
        return (
            "HD3",
            f"listed dates holding {total} rows",
            f"at most the {body} rows between the two boundaries",
        )
    if len(listed) > different:
        return (
            "HD3",
            f"{len(listed)} listed dates",
            f"at most the column's {different} different parsed values",
        )
    weekdays, month = censuses
    broken = _heavy_group_breach(listed, weekdays, "weekday")
    if broken is None:
        broken = _heavy_group_breach(listed, month, "day-of-month")
    if broken is not None:
        return broken
    if heavy_runs(knots, listed, holes) is None:
        return (
            "HD4",
            "listed runs the published boundaries and rungs cannot stand beside",
            "every boundary and rung on a listed date inside its run, and "
            "every other one before or after it, in one rank order",
        )
    for index in range(len(listed)):
        day, count = listed[index]
        near = 0
        for step in (-1, 1):
            other = index + step
            while 0 <= other < len(listed) and abs(listed[other][0] - day) <= HEAVY_REACH:
                near = near + listed[other][1]
                other = other + step
        if 2 * count < near:
            return (
                "HD5",
                f"a listed date holding {count} rows beside {near} listed rows "
                "within three days",
                "every listed date at least half the listed rows within three days",
            )
    return None


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
# anchor 3b-R2a (P4-D383)
# anchor 3b-R2b (P4-D383)
# anchor 3b-R2c (P4-D383)
# anchor 3b-R4 (P4-D384)

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
    """The fewest and the most different days the twin's two tails keep once its count pass has run, but at a share of seeds no larger than `KEPT_MISS`.

    The first eight arguments are `tails_fewest`'s; `pins` are the body's
    pinned ranks with their days (`body_pins`) and `census_holes` the days
    the description publishes as holding no body cell (`public_holes`).
    The two count rules are handed these (the orchestrator's ruling of
    2026-10-07 on the price of plan P4-D388: a census its twins meet at
    nine seeds in ten or more stands): the room rule the most, the reach
    rule the fewest.

    THE COUNT PASS DECIDES WHAT THE TAILS KEEP (method G12.5), and it knows
    nothing of the census. Where the body's draw (`body_draw`) and the
    days the two tails draw in expectation (`tail_days_law`) pass the
    column's count of different days, it MERGES runs onto held days,
    nearest first, then the shorter run, then the LOWER rank: the low
    tail's ranks are the column's lowest, so it is merged first, at most
    down to its fewest days (`_side_counted`), and the high tail's are the
    highest, so it keeps the days it drew. Where they fall short it SPLITS
    ranks onto free days, the low tail first again, and both tails spread
    to their most (`tails_most_rebuilt`). So, merging, the FEWEST is the
    low tail's fewest and the least count the high tail draws with a
    chance above `KEPT_MISS` of drawing no more; and the MOST counts no
    merge at all -- the least count the two tails draw together with a
    chance of at least `1 - KEPT_MISS` of drawing no more. A merge only
    takes days away, so where the pass merges, the days the tails draw
    bound the days they keep; how far a merge takes the low tail is not
    read here, and a day it keeps is a day the body loses. Measured (plan
    P4-D388): the low tail kept a day or two above its fewest on the
    median of the twins measured and up to ten on a column of monthly
    dates whose low tail's days stand apart, whose census a most read at
    that fewest published, its twins long at every seed; it fell below
    its fewest only where the column's count leaves the body a few days
    or none beside the two tails' fewest, and the pass moves tail ranks
    out of their strata to meet it; and the high tail gave up days where
    the pass took more than a quarter of the body's drawn days, which the
    fewest does not count. Splitting, both are the two tails' most.

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
    has run, but at a share of seeds no larger than `KEPT_MISS`
    (`tails_kept`, the orchestrator's ruling of 2026-10-07), and `most`
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
    (`body_draw`). Where the draw and the tails' most fall short of the
    count, the pass only SPLITS, moving ranks that share a day onto days
    no rank holds -- a tail's ranks onto free days of their own spans --
    and the tails reach their most: one row a business day over four and
    a half years draws about 830 of its 1,180 days and comes back
    holding every one. Otherwise it MERGES, and merging only takes days
    away: the body keeps no more than its draw, and the tails no fewer
    than `fewest`. So the body's NEED is what the tails at their most
    leave it, and, where its draw passes that, as much of the draw as
    the tails at `fewest` leave room for.

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
    of seeds, a miss the twin's report and validation name.
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

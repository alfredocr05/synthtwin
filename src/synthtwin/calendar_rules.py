"""The weekday census of a column of dates: its menu and its rules.

Stage 3b, landing 3b.1 (plan P4-D355, contract WC1 to WC8). A column
of whole dates read on the local clock publishes `weekday_census`: how
many cells of its BODY -- the cells between the two tail boundaries,
both included -- fall on each day of the week, in GROUPS whose count is
nought or at least the census line (`parsing.census_floor`). Monday is
weekday 0 and Sunday 6; a group is `(first, last, count)` over a run of
weekdays.

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

A merged group of the menu says only that SOME member is short, and a
reader reads exactly that and nothing more (`branches_of`): the entry
is read back from the shape of the groups alone (`entry_of`). A rule
that merged a SPECIFIC short weekday into its neighbour would tell a
reader that weekday held fewer than the line together with the
neighbour, and no day of it could then hold the line in any table
consistent with the rule -- which is why no such rule exists here
(plan P4-D355).

Whether a census the menu offers is PUBLISHED is the full-fill
certificate's question (`calendar_certificate`). This module holds the
menu and the cheap rules the producer and the loader both ask:

* WC5, the knot days' sure cells: a group less the cells a reader
  places in it for certain -- one for each boundary and rung day, more
  where several rungs share a day -- is nought or at least the line;
* WC7, no group the count of a few single dates (`few_dates_group`,
  owner ruling 7 of 2026-09-26 leaves single dates to landing 3b.6);
* WC6, one spelling per day (`one_spelling_published`): the published
  censuses of written forms give every date one text, so the count of
  different values a reader holds is a count of different days;
* one storage class per workbook column (`stored_one_way`).

Nothing here reads a table: every function is a function of the
numbers handed to it. No I/O of any kind.
"""

from synthtwin import parsing

# The key of the census in a column block of dates (contract 6.6.2).
WEEKDAY_CENSUS = "weekday_census"

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

# WHY A COLUMN OF DATES PUBLISHES NO WEEKDAY CENSUS, one word per
# reason. Each is the argument of one enumerated sentence of the
# description (`taxonomy.NOTE_WEEKDAY_WITHHELD_*`), never printed as it
# stands.
REASON_NO_TAILS = "no_tails"
REASON_SPELLINGS = "spellings"
REASON_WORKBOOK = "workbook"
REASON_MENU = "menu"
REASON_TIES = "ties"
REASON_FEW_DATES = "few_dates"
REASON_NARROWED = "narrowed"
REASONS = (
    REASON_NO_TAILS,
    REASON_SPELLINGS,
    REASON_WORKBOOK,
    REASON_MENU,
    REASON_TIES,
    REASON_FEW_DATES,
    REASON_NARROWED,
)

# WC7: a non-zero group must be able to hold at least this many
# different dates besides the knot days a reader already holds.
FEWEST_DATES = 4

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
        if 0 < count < line:
            seven = False
    if seven:
        return tuple(_single_runs(bins, 0, SUNDAY)), ENTRY_SEVEN
    weekend = bins[SATURDAY] + bins[SUNDAY]
    weekdays = sum(bins[0:SATURDAY])
    weekend_ok = weekend == 0 or weekend >= line
    single = True
    for weekday in range(SATURDAY):
        if 0 < bins[weekday] < line:
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


def branches_of(
    groups: "tuple[tuple[int, int, int], ...]",
    line: int,
    shortable: "tuple[int, ...]",
    exclude: int,
) -> "list[dict[int, tuple[int, int]]]":
    """What the census tells a reader about the seven weekday totals.

    A list of ALTERNATIVES, each a bound `(least, most)` per weekday it
    bounds: entry 1 fixes all seven totals; entry 2 fixes Monday to
    Friday and holds Saturday, or else Sunday, at one to `line - 1`;
    entry 3 holds one of Monday to Friday at one to `line - 1`. A
    weekday in an empty group is fixed at nought and one alone in a
    group at its count, in every entry. `shortable` names the weekdays
    that can hold a cell at all -- a weekday no day of the body falls
    on cannot be the short one -- and `exclude` a weekday that may not
    be the short one (the weekday a witness fills to the line; -1 for
    none). The alternatives are exactly what a reader can conclude
    from the grouping and the floor, and every table consistent with
    the census meets at least one of them.

    Guarantees: accepts a menu grouping, the line, the weekdays that
    can be short and the one excluded; returns the alternatives in
    weekday order of the short one. Determinism: a function of the
    four. Raises nothing. No I/O of any kind.
    """
    exact: "dict[int, tuple[int, int]]" = {}
    for first, last, count in groups:
        if count == 0:
            for weekday in range(first, last + 1):
                exact[weekday] = (0, 0)
        elif first == last:
            exact[first] = (count, count)
    entry = entry_of(groups)
    if entry == ENTRY_SEVEN:
        return [exact]
    candidates: "tuple[int, ...]" = (SATURDAY, SUNDAY)
    if entry == ENTRY_WEEKDAYS:
        candidates = (0, 1, 2, 3, FRIDAY)
    found: "list[dict[int, tuple[int, int]]]" = []
    for short in candidates:
        if short == exclude or short not in shortable:
            continue
        if short in exact and exact[short] == (0, 0):
            continue
        alternative = dict(exact)
        alternative[short] = (1, line - 1)
        found += [alternative]
    return found


def sure_cells_breach(
    groups: "tuple[tuple[int, int, int], ...]",
    sure: "list[int]",
    line: int,
) -> int:
    """WC5: the first group a reader's sure cells leave short, or -1.

    `sure` is, per weekday, the cells a reader places there for
    certain: each knot day -- a tail boundary or a published rung --
    holds at least one body cell, and more where rungs at several ranks
    share its day. A non-zero group whose count less those cells is one
    to `line - 1` would hand that remainder back by subtraction.

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


def few_dates_group(
    groups: "tuple[tuple[int, int, int], ...]",
    low: int,
    high: int,
    knot_days: "tuple[int, ...]",
    most_days: int,
    holes: "frozenset[int]" = frozenset(),
) -> int:
    """WC7: the first non-zero group a reader can hold to few dates, or -1.

    For a non-zero group, the most different dates it can hold besides
    the knot days a reader already holds is the least of three: its
    calendar days between the boundaries that are not knot days, less
    its HOLES (days no body cell can hold, `form_holes` and the days a
    declared missing value names); its count less one per knot day in
    it; and the body's most different days (`most_days`, the reader's
    `D_max`) less every knot day and one date for each other non-zero
    group holding no knot day. Fewer than `FEWEST_DATES` makes the
    group the count of a few single dates, which is the heavy-date
    landing's business (owner ruling 7 of 2026-09-26), not this
    census's.

    Guarantees: accepts the groups, the two boundary days, the knot
    days, the reader's most different days and the holes; returns a
    group index or -1. Determinism: a function of the six. Raises
    nothing. No I/O of any kind.
    """
    where = where_of(groups)
    calendar = [0 for _ in groups]
    knotted = [0 for _ in groups]
    knots = set(knot_days)
    for day in range(low, high + 1):
        index = where[weekday_of(day)]
        if day in knots:
            knotted[index] = knotted[index] + 1
        elif day in holes:
            continue
        calendar[index] = calendar[index] + 1
    nonzero = [index for index in range(len(groups)) if groups[index][2] > 0]
    for index in nonzero:
        others = 0
        for other in nonzero:
            if other != index and knotted[other] == 0:
                others = others + 1
        most = min(
            calendar[index] - knotted[index],
            groups[index][2] - knotted[index],
            most_days - len(knot_days) - others,
        )
        if most < FEWEST_DATES:
            return index
    return -1


def one_spelling_published(
    forms: "dict[str, dict[str, int]]", format_name: str, parsed: int
) -> bool:
    """WC6 (a): whether the published form censuses give a date one text.

    `n_distinct` counts TEXTS, and the certificate counts DAYS; the two
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
    statement of the rule, asked by the producer and the loader, so
    that both sides of the certificate (`calendar_certificate.facts_of`)
    and WC7 leave the holes out.

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
    may_only = False
    if (
        format_name in parsing.TEXTUAL_MEMBERS
        and "month_name_styles" in forms
        and len(forms["month_name_styles"]) == 1
    ):
        for word in forms["month_name_styles"]:
            may_only = parsing.name_is_value_bound(word)
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

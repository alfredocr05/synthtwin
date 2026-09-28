"""The INDEPENDENT verifier of the weekday census's certificate (landing 3b.1).

It imports nothing from synthtwin. From a column block of dates alone it
re-derives what a reader holds -- the body, the knot days and their rank
facts, the reader's least and most different days, the grouping and the
entry of the menu it is, the classes -- and then checks every witness the
producer's certificate returned DAY BY DAY:

* the body's cells lie between the two boundary days, both of which are
  occupied, and add up to the body;
* every knot day's rank facts hold (cells strictly before it at most
  `lt`, at or before it at least `le`);
* every group holds its published count, and what the entry tells holds
  too (entry 2: Saturday or Sunday one to the line less one; entry 3:
  one of Monday to Friday so);
* the count of different days lies within the reader's bounds and, where
  the real table is handed in, equals the real body's;
* no cell stands on a hole, and the witness's own day holds the line;

and that every class of a counted weekday is covered by a witness day,
or lies in a stretch the rank facts cap below the line (the residue's
rule, re-derived here from the description).

THE HOLES ARE RE-DERIVED HERE TOO, from the block's own censuses of
written forms (`form_holes`), beside the declared ones handed in: a
width word one field alone shows (`first-field-*`, `second-field-*`)
says the OTHER field is ten or more in every cell, and a month name
whose length is `either` says every cell is in May, so a reader holds
every other day empty (review of landing 3b.1, finding 1). A hole is
no member of a class and no witness may stand on it. The residue's configuration
equivalence is the one part of the certificate it does not redo; the
brute force beside it (`calendar_certificate_brute`) exercises that.

Every function is a function of its arguments; nothing is read or
written.
"""

from __future__ import annotations

import datetime

PERCENTS = (1, 5, 10, 25, 50, 75, 90, 95, 99)
_EPOCH = datetime.date(1970, 1, 1)


def day_number(text: str) -> int:
    """The day of a canonical date text, counted from 1970-01-01."""
    return (datetime.date.fromisoformat(text[:10]) - _EPOCH).days


def weekday(day: int) -> int:
    """Monday 0 to Sunday 6."""
    return (_EPOCH + datetime.timedelta(days=day)).weekday()


def entry_of(groups: "list[tuple[int, int, int]]") -> int:
    """Which grouping of the menu this is: 1, 2, 3, or 0 for none."""
    if all(first == last or count == 0 for first, last, count in groups):
        return 1
    if (
        groups
        and groups[-1][:2] == (5, 6)
        and groups[-1][2] > 0
        and all(last <= 4 and (first == last or count == 0) for first, last, count in groups[:-1])
    ):
        return 2
    if [(first, last) for first, last, _count in groups] == [(0, 4), (5, 6)] and groups[0][2] > 0:
        return 3
    return 0


def form_holes(block: dict) -> "set[int]":
    """The days between the two boundaries the block's form censuses leave empty.

    Written from the vocabulary alone: a width word naming ONE field is
    written only where the other field -- the day where the month comes
    first, the month where the day does -- is ten or more; a month name
    of length `either` is May's. Every other word says nothing.
    """
    low = day_number(block["low_tail"]["boundary"])
    high = day_number(block["high_tail"]["boundary"])
    widths = block.get("date_field_widths") or {}
    names = block.get("month_name_styles") or {}
    width = next(iter(widths)) if len(widths) == 1 else ""
    name = next(iter(names)) if len(names) == 1 else ""
    month_first = "month-first" in block["format"]
    textual = block["format"].startswith("textual-")
    found = set()
    for day in range(low, high + 1):
        date = _EPOCH + datetime.timedelta(days=day)
        first, second = (date.month, date.day) if month_first else (date.day, date.month)
        if not textual and width.startswith("first-field-") and second < 10:
            found.add(day)
        if not textual and width.startswith("second-field-") and first < 10:
            found.add(day)
        if textual and name.split("-")[1:2] == ["either"] and date.month != 5:
            found.add(day)
    return found


def reader_facts(block: dict, line: int, holes: "set[int] | None" = None) -> dict:
    """What a reader of this block holds about its body, `holes` left out of every class."""
    holes = form_holes(block) if holes is None else holes
    parsed = block["n_present"] - block["n_unparsed"]
    low_tail, high_tail = block["low_tail"], block["high_tail"]
    rows_low, rows_high = low_tail["rows"], high_tail["rows"]
    body = parsed - rows_low - rows_high

    def most(tail: dict) -> int:
        return len(tail["values"]) if tail.get("values") else tail["rows"]

    def least(tail: dict) -> int:
        return len(tail["values"]) if tail.get("values") else (1 if tail["rows"] > 0 else 0)

    unparsed = block["n_unparsed"]
    fewest = block["n_distinct"] - unparsed - most(low_tail) - most(high_tail)
    most_days = block["n_distinct"] - (1 if unparsed > 0 else 0) - least(low_tail) - least(high_tail)
    low, high = day_number(low_tail["boundary"]), day_number(high_tail["boundary"])
    below_at_most = {low: 0, high: body - 1}
    upto_at_least = {low: 1, high: body}
    for percent in PERCENTS:
        text = (block.get("date_percentiles") or {}).get(f"p{percent:02d}")
        if not text:
            continue
        rank = min(parsed - 1, (parsed - 1) * percent // 100)
        if not rows_low <= rank <= parsed - 1 - rows_high:
            continue
        day, inside = day_number(text), rank - rows_low
        below_at_most[day] = min(below_at_most.get(day, body - 1), inside)
        upto_at_least[day] = max(upto_at_least.get(day, 1), inside + 1)
    below_at_most[low] = 0
    upto_at_least[high] = body
    knots = sorted(below_at_most)
    groups = [(group["first"], group["last"], group["count"]) for group in block["weekday_census"]]
    where = {}
    for index, (first, last, _count) in enumerate(groups):
        for day in range(first, last + 1):
            where[day] = index
    stretches: "list[tuple[str, int, int]]" = []
    for index, day in enumerate(knots):
        stretches += [("knot", day, day)]
        if index + 1 < len(knots) and knots[index + 1] - day > 1:
            stretches += [("open", day + 1, knots[index + 1] - 1)]
    classes: "dict[tuple[int, int], list[int]]" = {}
    for place, (kind, first, last) in enumerate(stretches):
        for day in range(first, last + 1):
            if kind == "open" and day in holes:
                continue
            members = classes.setdefault((place, weekday(day)), [])
            members += [day]
    count = len(stretches)
    least_before = [0] * count
    most_before = [body] * count
    for place, (kind, first, _last) in enumerate(stretches):
        if kind == "knot":
            least_before[place] = max(least_before[place], upto_at_least[first])
        if place + 1 < count and stretches[place + 1][0] == "knot":
            most_before[place] = min(most_before[place], below_at_most[stretches[place + 1][1]])
    least_before[count - 1] = body
    for place in range(1, count):
        least_before[place] = max(least_before[place], least_before[place - 1])
    for place in range(count - 2, -1, -1):
        most_before[place] = min(most_before[place], most_before[place + 1])
    stretch_most = [
        max(0, most_before[place] - (least_before[place - 1] if place else 0))
        for place in range(count)
    ]
    return {
        "body": body, "low": low, "high": high, "below": below_at_most,
        "upto": upto_at_least, "knots": knots, "groups": groups,
        "entry": entry_of(groups), "where": where, "fewest": fewest,
        "most_days": most_days, "classes": classes, "stretches": stretches,
        "stretch_most": stretch_most, "line": line,
    }


def table_problems(facts: dict, table: "dict[int, int]", target: int) -> "list[str]":
    """Why one witness is not a table meeting the facts, or nothing."""
    line = facts["line"]
    held = {day: cells for day, cells in table.items() if cells > 0}
    found = []
    if sum(held.values()) != facts["body"]:
        found += [f"adds to {sum(held.values())}, the body holds {facts['body']}"]
    if any(day < facts["low"] or day > facts["high"] for day in held):
        found += ["a cell outside the two boundaries"]
    if held.get(facts["low"], 0) < 1 or held.get(facts["high"], 0) < 1:
        found += ["a boundary day holds no cell"]
    for knot in facts["knots"]:
        below = sum(cells for day, cells in held.items() if day < knot)
        upto = below + held.get(knot, 0)
        if below > facts["below"][knot] or upto < facts["upto"][knot]:
            found += [f"the rank facts of knot day {knot} fail"]
    bins = [0] * 7
    for day, cells in held.items():
        bins[weekday(day)] += cells
    for first, last, count in facts["groups"]:
        if sum(bins[first:last + 1]) != count:
            found += [f"group {first}-{last} holds {sum(bins[first:last + 1])}, not {count}"]
    if facts["entry"] == 2 and not any(1 <= cells <= line - 1 for cells in bins[5:7]):
        found += ["entry 2, and neither Saturday nor Sunday is short"]
    if facts["entry"] == 3 and not any(1 <= cells <= line - 1 for cells in bins[0:5]):
        found += ["entry 3, and no weekday from Monday to Friday is short"]
    if not facts["fewest"] <= len(held) <= facts["most_days"]:
        found += [f"{len(held)} different days, outside [{facts['fewest']}, {facts['most_days']}]"]
    if held.get(target, 0) < line:
        found += [f"the witness's day holds {held.get(target, 0)}, below the line {line}"]
    return found


def census_problems(
    block: dict,
    line: int,
    witnesses: "list[tuple[tuple[int, int], int, tuple[tuple[int, int], ...]]]",
    real_days: "int | None" = None,
    holes: "tuple[int, ...]" = (),
) -> "list[str]":
    """Every way a published census's certificate fails the checks above.

    `witnesses` are (class, day, table as (day, cells) pairs); `real_days`
    the real body's count of different days where the real table is in
    hand; `holes` the declared days no body cell may stand on, to which
    the block's own form holes are added (`form_holes`).
    """
    hole_days = set(holes) | form_holes(block)
    facts = reader_facts(block, line, hole_days)
    found = []
    if facts["entry"] == 0:
        found += ["the census is not a grouping of the menu"]
    covered = set()
    for _klass, target, pairs in witnesses:
        table = dict(pairs)
        problems = table_problems(facts, table, target)
        occupied = sum(1 for cells in table.values() if cells > 0)
        if real_days is not None and occupied != real_days:
            problems += [f"{occupied} different days, the real body {real_days}"]
        on_holes = sum(cells for day, cells in table.items() if day in hole_days and cells > 0)
        if on_holes:
            problems += [f"{on_holes} cells on a hole"]
        found += [f"witness on day {target}: {problem}" for problem in problems]
        for key, days in facts["classes"].items():
            if target in days:
                covered.add(key)
    for key in sorted(facts["classes"]):
        group = facts["groups"][facts["where"][key[1]]]
        if group[2] == 0 or key in covered:
            continue
        if facts["stretch_most"][key[0]] >= line:
            found += [
                f"class {key} is neither certified nor held below the line by the rank facts"
            ]
    return found

"""The order the real table's rows stand in, kept in the inside record and given to the twin (lane TOOLS).

WHAT WAS LOST, MEASURED. Eight invented tables of 20,000 rows, each sorted
the way health extracts are, through `synthtwin twin`: the twin kept the
order of a table sorted by an ISO date, a number or a descending ISO date
(the description's own `rows.order`, read off the cells as text or
numbers), and lost it -- half of its adjacent rows out of order, as a
shuffle gives -- for a table sorted by a date written month first
(`3/14/2023`, with or without a clock), by a stamp with its empty cells
last, and by the person then each person's visit dates (the long table of
visits, a person's rows together and in time order). Code that reads a
person's first row as their baseline (`groupby(...).first()`), takes
`diff()` within a person, or asserts the file is sorted, then ran on the
twin and gave another answer.

WHAT IS KEPT. The order is a fact about the arrangement of the rows, no
value of any of them: which column (or which two) the rows are sorted by,
read how (`number`, `date`, `text`) and which way, and whether empty cells
stand last. It is measured on the real table where the inside record is
written (`zone_of`) and kept in the record's `order` zone, which never
leaves the protected computer -- so no published fact of the description
changes, and the description's own row order (`rows.order`, held by the
quality report) stands where it is published: this zone is written only
where the description publishes none. The twin's rows are then put in
that order by the twin's own cells (`permutation`): a stable sort, the
all-empty records and a row-sequence column left where the arrangement put
them (the generator's `_sorted_again` rule).

TWO KINDS OF ORDER.

* ONE KEY: the leftmost column whose cells, read as numbers, as dates (a
  date in the layouts `date_key` reads, a clock after it or none) or as
  text, never step back and change at least once, its empty cells, if any,
  all at the end.
* THE PERSON, THEN A KEY: the person column's rows each in one run (every
  person's rows together), the runs in the order of the person's own key
  or of their first date, and, within every run, the leftmost other
  column that never steps back and changes within at least one run.

Guarantees: the standard library and `parsing` alone; no random source,
no clock, no I/O; every function a fixed function of its arguments.
"""

import dataclasses

from synthtwin import parsing

ZONE = "order"
VERSION = 1
READ_AS_NUMBER = "number"
READ_AS_DATE = "date"
READ_AS_TEXT = "text"
READINGS = (READ_AS_NUMBER, READ_AS_DATE, READ_AS_TEXT)
ASCENDING = "ascending"
DESCENDING = "descending"
# How a grouped order puts its persons: by their own key, or by the first
# value of the key within each.
PERSONS_BY_KEY = "key"
PERSONS_BY_KEY_DESCENDING = "key descending"
PERSONS_BY_FIRST = "first"
# How the groups of a two-key order stand: by the first key's own order,
# or by the first value of the second key in each group.
GROUPS_BY_KEY = "by key"
GROUPS_BY_FIRST = "by first"
GROUPS = (GROUPS_BY_KEY, GROUPS_BY_FIRST)
# The runs of tied cells a first key holds, at least, before a second key
# is looked for within them.
_TIE_RUNS_LEAST = 5
# A run of equal cells this long or longer in the person column, at least
# once, for the rows to count as grouped by the person.
_GROUP_LEAST = 2
_NOT_TEXT = "a cell must be text"


def _figures(text: str) -> bool:
    return bool(text) and all(character in "0123456789" for character in text)


def _pieces(text: str, mark: str) -> "list[str]":
    """The text cut at every ``mark``, read a character at a time (the offline audit's form)."""
    pieces: "list[str]" = []
    piece = ""
    for character in text:
        if character == mark:
            pieces += [piece]
            piece = ""
        else:
            piece = piece + character
    return pieces + [piece]


def _clock(text: str) -> "int | None":
    """Seconds past midnight of `9:15`, `09:15:30`, `09:15:30.250`, `9:15 PM`, or None."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = parsing.folded(text)
    shift = -1
    if body[-2:] in ("am", "pm"):
        shift = 0 if body[-2:] == "am" else 12
        body = parsing.trimmed(body[:-2])
    elif body[-1:] == "z":
        body = body[:-1]
    parts = _pieces(body, ":")
    if len(parts) not in (2, 3):
        return None
    if len(parts) == 3:
        parts = [parts[0], parts[1], _pieces(parts[2], ".")[0]]
    if not all(_figures(part) and len(part) <= 2 for part in parts):
        return None
    hour, minute = int(parts[0]), int(parts[1])
    second = int(parts[2]) if len(parts) == 3 else 0
    if shift >= 0:
        if not 1 <= hour <= 12:
            return None
        hour = hour % 12 + shift
    if hour > 23 or minute > 59 or second > 59:
        return None
    return hour * 3600 + minute * 60 + second


def _day(year: int, month: int, day: int) -> bool:
    return year >= 1000 and 1 <= month <= 12 and 1 <= day <= 31 and parsing.valid_date(year, month, day)


def date_key(text: str) -> "tuple[int, int, int, int] | None":
    """A date cell's sort key (year, month, day, seconds of its clock or -1), or None for any other cell.

    Reads `2023-03-14`, `2023/03/14`, `3/14/2023`, `03-14-2023` (the month
    first wherever the year is last, as `parsing.date_parts` reads it, its
    figures with or without a zero in front), and a clock after a space or
    a `T`. A fixed function of the text; raises TypeError for a cell that
    is not text.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = parsing.trimmed(text)
    clock = -1
    for place in range(len(body)):
        if body[place] == " " or (body[place] == "T" and place >= 8):
            found = _clock(parsing.trimmed(body[place + 1 :]))
            if found is None:
                return None
            clock = found
            body = body[:place]
            break
    for mark in ("-", "/"):
        parts = _pieces(body, mark)
        if len(parts) != 3 or not all(_figures(part) for part in parts):
            continue
        if len(parts[0]) == 4 and len(parts[1]) <= 2 and len(parts[2]) <= 2:
            year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
        elif len(parts[2]) == 4 and len(parts[0]) <= 2 and len(parts[1]) <= 2:
            year, month, day = int(parts[2]), int(parts[0]), int(parts[1])
        else:
            return None
        return (year, month, day, clock) if _day(year, month, day) else None
    return None


def _key(cell: str, reading: str) -> "object | None":
    """One cell's key under ``reading``; None for a cell the reading has no key for."""
    if reading == READ_AS_NUMBER:
        return parsing.parse_number(parsing.trimmed(cell))
    if reading == READ_AS_DATE:
        return date_key(cell)
    return cell


def _empty(cell: str) -> bool:
    if not isinstance(cell, str):
        raise TypeError(_NOT_TEXT)
    return not parsing.trimmed(cell)


def _steps(keys: "list[object]") -> str:
    """ASCENDING, DESCENDING or "" for keys in their order: never stepping back one way, changing at least once."""
    rising = falling = True
    changed = False
    for place in range(1, len(keys)):
        before, after = keys[place - 1], keys[place]
        if after != before:
            changed = True
            if after < before:  # type: ignore[operator]
                rising = False
            else:
                falling = False
        if not rising and not falling:
            return ""
    if not changed:
        return ""
    return ASCENDING if rising else (DESCENDING if falling else "")


def one_key(cells: "list[str]") -> "tuple[str, str] | None":
    """How one column orders the rows: (reading, direction), or None.

    Its present cells, read under the first reading of `READINGS` that has
    a key for every one of them, never step back and change at least once;
    its empty cells, if any, stand together at the end. Each reading stops
    at the first cell it has no key for or the first step that settles it
    has no order, so a column in no order costs a few cells. A fixed
    function of the cells.
    """
    present = 0
    while present < len(cells) and not _empty(cells[present]):
        present = present + 1
    if present < 3:
        return None
    for place in range(present, len(cells)):
        if not _empty(cells[place]):
            return None
    for reading in READINGS:
        rising = falling = True
        changed = False
        keyed = True
        before = _key(cells[0], reading)
        if before is None:
            continue
        for place in range(1, present):
            after = _key(cells[place], reading)
            if after is None:
                keyed = False
                break
            if after != before:
                changed = True
                if after < before:  # type: ignore[operator]
                    rising = False
                else:
                    falling = False
                if not rising and not falling:
                    break
            before = after
        if not keyed:
            continue
        # A column every cell of which reads as numbers, or as dates, is
        # ordered by them or not at all; text is the last reading.
        if changed and (rising or falling):
            return (reading, ASCENDING if rising else DESCENDING)
        return None
    return None


def _runs(cells: "list[str]") -> "list[tuple[int, int]] | None":
    """The runs of equal cells, as (start, end); None where a value stands in two runs or a cell is empty."""
    runs: "list[tuple[int, int]]" = []
    seen: "set[str]" = set()
    start = 0
    for place in range(1, len(cells) + 1):
        if place == len(cells) or cells[place] != cells[start]:
            if _empty(cells[start]) or cells[start] in seen:
                return None
            # ...grown in place (the outside review of release 37, item 14: `seen = seen | {...}` copied the whole set for
            # every run, about 125 billion copies for 500,000 two-row persons).
            seen |= {cells[start]}
            runs += [(start, place)]
            start = place
    return runs


def grouped(
    person: "list[str]", other: "list[str]", runs_given: "list[tuple[int, int]] | None" = None
) -> "tuple[str, str, str] | None":
    """How the rows order within each person's run by ``other``: (reading, direction, how the persons stand), or None.

    The person's rows must stand in runs, one run a person, at least one of
    `_GROUP_LEAST` rows; ``other`` never steps back within any run under one
    reading and direction, and changes within at least one, its empty cells
    allowed only at the end of a run. The persons stand by their own key
    (read as numbers where every key is one, else as text) where the runs
    are in its order, else by the first value of ``other`` in each.
    ``runs_given`` are ``person``'s runs where the caller holds them
    already (`Finder` reads them once a table, not once a column).
    """
    runs = runs_given if runs_given is not None else _runs(person)
    if runs is None or not any(end - start >= _GROUP_LEAST for start, end in runs):
        return None
    for reading in READINGS:
        direction = ""
        works = True
        changed = False
        firsts: "list[object]" = []
        for start, end in runs:
            run = other[start:end]
            present = 0
            while present < len(run) and not _empty(run[present]):
                present = present + 1
            if any(not _empty(cell) for cell in run[present:]):
                works = False
                break
            keys = [_key(cell, reading) for cell in run[:present]]
            if any(key is None for key in keys):
                works = False
                break
            firsts += [keys[0] if keys else None]
            found = _steps(keys) if len(keys) > 1 else ""
            if found:
                changed = True
                if direction and found != direction:
                    works = False
                    break
                direction = found
            elif len(set(keys)) > 1:
                works = False
                break
        if not works:
            continue
        if not changed:
            return None
        return (reading, direction, _persons_stand(person, runs, firsts, direction))
    return None


def _persons_stand(person: "list[str]", runs: "list[tuple[int, int]]", firsts: "list[object]", direction: str) -> str:
    """Whether the runs stand in the order of the person's own key, either way (`PERSONS_BY_KEY`,
    `PERSONS_BY_KEY_DESCENDING`), or else of their first values (`PERSONS_BY_FIRST`)."""
    keys = [person[start] for start, _end in runs]
    numbers = [parsing.parse_number(parsing.trimmed(key)) for key in keys]
    readable: "list[object]" = list(numbers) if all(number is not None for number in numbers) else list(keys)
    found = _steps(readable)
    if found == ASCENDING:
        return PERSONS_BY_KEY
    if found == DESCENDING:
        return PERSONS_BY_KEY_DESCENDING
    return PERSONS_BY_FIRST


def _tie_runs(cells: "list[str]") -> int:
    """How many runs of two or more equal cells a column holds."""
    count = 0
    start = 0
    for place in range(1, len(cells) + 1):
        if place == len(cells) or cells[place] != cells[start]:
            if place - start >= _GROUP_LEAST:
                count = count + 1
            start = place
    return count


def _entry(name: str, reading: str, direction: str) -> "dict[str, object]":
    return {"column": name, "read_as": reading, "direction": direction}


@dataclasses.dataclass
class Finder:
    """What the columns read so far, left to right, say of the rows' order (`see`, then `finished`).

    ``person`` is the column the description names as the person (or "").
    One column's cells are held at most: the first ordered column's where
    it holds tied runs, and the person's where its rows stand together.
    """

    person: str
    # Columns the description publishes as the row sequence (0, 1, 2, ...
    # written again in row order whatever the rows' order): passed over,
    # as the description's own survey passes over them.
    skip: "tuple[str, ...]" = ()
    single: "dict[str, object] | None" = None
    single_cells: "list[str] | None" = None
    single_runs: "list[tuple[int, int]] | None" = None
    then: "dict[str, object] | None" = None
    person_cells: "list[str] | None" = None
    person_runs: "list[tuple[int, int]] | None" = None
    by_person: "dict[str, object] | None" = None


def see(finder: Finder, name: str, cells: "list[str]") -> None:
    """Read one more column, the next to the right, into the finder.

    The first column ordering the rows on its own (`one_key`) is the
    single key; where it holds at least `_TIE_RUNS_LEAST` runs of tied
    cells, the first column after it ordering the rows within every run
    (`grouped`) is its second key. Where the person's rows stand
    together, the first column after the person ordering each person's
    rows is the order kept should no column order the rows on its own.
    A column `Finder.skip` names is passed over.
    """
    if name in finder.skip:
        return
    if finder.single is not None and finder.single_cells is not None and finder.then is None:
        found = grouped(finder.single_cells, cells, finder.single_runs)
        if found is not None:
            finder.then = _entry(name, found[0], found[1])
            finder.single_cells = None
    if finder.person_cells is not None and finder.by_person is None and name != finder.person:
        found_person = grouped(finder.person_cells, cells, finder.person_runs)
        if found_person is not None:
            first = one_key(finder.person_cells)
            groups = GROUPS_BY_KEY if found_person[2] != PERSONS_BY_FIRST and first is not None else GROUPS_BY_FIRST
            reading, direction = first if groups == GROUPS_BY_KEY and first is not None else (READ_AS_TEXT, ASCENDING)
            finder.by_person = {
                "version": VERSION,
                "groups": groups,
                "keys": [_entry(finder.person, reading, direction), _entry(name, found_person[0], found_person[1])],
            }
            finder.person_cells = None
    if finder.single is None:
        found_one = one_key(cells)
        if found_one is not None:
            finder.single = _entry(name, found_one[0], found_one[1])
            if _tie_runs(cells) >= _TIE_RUNS_LEAST:
                finder.single_runs = _runs(cells)
                finder.single_cells = list(cells) if finder.single_runs is not None else None
            finder.person_cells = None
    if name == finder.person and finder.single is None:
        finder.person_runs = _runs(cells)
        finder.person_cells = list(cells) if finder.person_runs is not None else None


def finished(finder: Finder) -> "dict[str, object] | None":
    """The order zone the columns read say: the single key (with its second key, where one was found), else the person's grouping, else None.

    The zone keeps column names and words, no value of the table.
    """
    if finder.single is not None:
        keys = [finder.single] + ([finder.then] if finder.then is not None else [])
        return {"version": VERSION, "groups": GROUPS_BY_KEY, "keys": keys}
    return finder.by_person


def zone_of(columns: "list[tuple[str, list[str]]]", person: str = "") -> "dict[str, object] | None":
    """The order zone of a real table's columns (name, cells), read left to right (`see`, `finished`)."""
    finder = Finder(person)
    for name, cells in columns:
        see(finder, name, cells)
    return finished(finder)


def read_zone(zone: object, names: "list[str]") -> "dict[str, object] | None":
    """The zone as `permutation` reads it, or None where it is not one this version wrote about these columns."""
    if not isinstance(zone, dict) or "version" not in zone or zone["version"] != VERSION or "keys" not in zone:
        return None
    if "groups" not in zone or zone["groups"] not in GROUPS:
        return None
    keys = zone["keys"]
    if not isinstance(keys, list) or len(keys) not in (1, 2):
        return None
    for key in keys:
        if not isinstance(key, dict):
            return None
        for field in ("column", "read_as", "direction"):
            if field not in key:
                return None
        if key["column"] not in names or key["read_as"] not in READINGS or key["direction"] not in (ASCENDING, DESCENDING):
            return None
    return zone


def _sorted_rows(rows: "list[int]", values: "list[str]", reading: str, direction: str) -> "list[int]":
    """The rows by their cells' keys, a stable sort the key's way round (Python's sort keeps ties in place either way),
    and every row whose cell has no key after them, in its own order."""
    keyed: "list[tuple[object, int]]" = []
    rest: "list[int]" = []
    turned = direction == DESCENDING
    for row in rows:
        key = None if _empty(values[row]) else _key(values[row], reading)
        if key is None:
            rest += [row]
        else:
            # The row's place breaks a tie, turned with the key, so tied rows
            # keep their own order either way round.
            keyed += [(key, -row if turned else row)]
    placed = sorted(keyed, reverse=turned)
    return [-row if turned else row for _key_of, row in placed] + rest


def _key_of(entry: object) -> "tuple[str, str, str]":
    assert isinstance(entry, dict)
    return (f"{entry['column']}", f"{entry['read_as']}", f"{entry['direction']}")


def permutation(zone: "dict[str, object]", columns: "dict[str, list[str]]", rows: "list[int]") -> "list[int]":
    """The ``rows`` in the zone's order, read off the twin's own cells: a stable sort, ties kept as they stand.

    ``columns`` maps the zone's columns to the twin's cells. One key: the
    rows by that key, the cells it reads no key in last. Two keys: the rows
    sharing a cell of the first key together, each group's rows by the
    second key, and the groups by the first key (`GROUPS_BY_KEY`) or by the
    first value of the second key in each (`GROUPS_BY_FIRST`). A fixed
    function of its arguments.
    """
    keys = zone["keys"]
    assert isinstance(keys, list)
    name, reading, direction = _key_of(keys[0])
    if len(keys) == 1:
        return _sorted_rows(rows, columns[name], reading, direction)
    then_name, then_reading, then_direction = _key_of(keys[1])
    whose = columns[name]
    within: "dict[str, list[int]]" = {}
    order: "list[str]" = []
    for row in rows:
        if whose[row] not in within:
            within[whose[row]] = []
            order += [whose[row]]
        within[whose[row]] += [row]
    for group in order:
        within[group] = _sorted_rows(within[group], columns[then_name], then_reading, then_direction)
    firsts = [within[group][0] for group in order]
    if zone["groups"] == GROUPS_BY_KEY:
        placed = [whose[row] for row in _sorted_rows(firsts, whose, reading, direction)]
    else:
        placed = [whose[row] for row in _sorted_rows(firsts, columns[then_name], then_reading, then_direction)]
    out: "list[int]" = []
    for group in placed:
        out += within[group]
    return out

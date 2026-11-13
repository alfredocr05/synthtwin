"""Offsets that follow the date: the rule families a zone's daylight saving keeps (lane DST, plan P4-D474).

A column of stamps written with their UTC offsets wears, in nearly every
export, the offset its zone had in force on each stamp's own date: a
summer stamp of a New York export `-04:00`, a winter one `-05:00`. The
offset census (`utc_offsets`) counts how many cells wore each offset and
says nothing of WHICH cells, so a twin that spent it by counts wrote a
winter date at the summer offset and a cell inside the hour the clocks
skip. Where every cell of the column agrees with one rule below, the
description publishes that rule (`offset_rule`, method G7.4r) and the
twin writes each cell at the offset the rule puts in force on its date.

THE FAMILIES ARE CLOSED AND WRITTEN OUT HERE (no `zoneinfo`: Windows
ships no zone database, and the twin must be the same bytes on every
platform). A rule is a family and the zone's STANDARD offset; its summer
offset is one hour east of it. Each family states, for every year it
covers, the two instants its clocks change on, as Python integers:

- ``us``: the United States and Canada. From 2007, 02:00 local on the
  second Sunday of March to 02:00 local (summer time) on the first Sunday
  of November; from 1987 to 2006, the first Sunday of April to the last
  Sunday of October. Any standard offset (Eastern `-05:00`, Central
  `-06:00`, Mountain, Pacific, Alaska, Hawaii-Aleutian, Atlantic).
- ``eu``: the European Union from 1996: 01:00 UTC on the last Sunday of
  March to 01:00 UTC on the last Sunday of October, whatever the zone
  (`+00:00`, `+01:00`, `+02:00`).
- ``au``: south-eastern Australia from 2008: 02:00 local standard time on
  the first Sunday of October to 03:00 local summer time on the first
  Sunday of April (a southern rule: summer spans the new year).
- ``nz``: New Zealand from 2008: 02:00 local standard time on the last
  Sunday of September to 03:00 local summer time on the first Sunday of
  April.

A column is read under a family only where every one of its years lies in
the years the family covers (`covers`); the twin, whose ranks can reach a
little past the real range, reads a year outside them under the nearest
era of the same family, and a published rule is checked over that whole
calendar (`grains.wears_the_rule`).

ONE DEFINITION ADMITS A RULE (lane DST's repair 2, Codex's items 4, 7 and
8), in inference, in publication and in the loader alike (`admitted`): a
family of `FAMILIES` and a standard offset from -12:00 to +13:00 whose
minutes are 00, 30 or 45 -- the offsets zones wear, so every change of a
family falls on a quarter hour of the wall clock and the reading's cache
of a quarter hour holds for every offset admitted. A column wearing any
other offset keeps the description it had before the rule.

Every function is a function of the numbers handed to it: Python
integers, no float, no clock, no I/O of any kind.
"""

import dataclasses

from synthtwin import parsing

US = "us"
EU = "eu"
AU = "au"
NZ = "nz"
# The order a column is tried in: the first family every cell agrees
# with is the one published.
FAMILIES = (US, EU, AU, NZ)
_FIRST_YEAR = {US: 1987, EU: 1996, AU: 2008, NZ: 2008}
LAST_YEAR = 2099
_SOUTHERN = (AU, NZ)
_HOUR = 3600
_DAY = 86400
# The standard offsets a rule admits (`admitted`): -12:00 to +13:00, so its
# summer time runs to +14:00, the furthest a zone's clock stands.
_LOWEST = -12 * _HOUR
_HIGHEST = 13 * _HOUR
# ...each a whole hour, a half or three quarters past it.
_MINUTES_ADMITTED = (0, 30 * 60, 45 * 60)


@dataclasses.dataclass(frozen=True)
class Rule:
    """A zone's daylight-saving rule: its family and its standard offset, in seconds east of UTC."""

    family: str
    standard: int


def offset_seconds(text: str) -> "int | None":
    """A written offset's seconds east of UTC (`+05:30`, `-0400`, `-04`), or None for anything else, `Z` included."""
    if len(text) < 3 or text[0:1] not in ("+", "-"):
        return None
    figures = ""
    for character in text[1:]:
        if character == ":":
            continue
        if character not in "0123456789":
            return None
        figures = figures + character
    if len(figures) not in (2, 4):
        return None
    hours = int(figures[0:2])
    minutes = int(figures[2:4]) if len(figures) == 4 else 0
    if hours > 23 or minutes > 59:
        return None
    seconds = hours * _HOUR + minutes * 60
    return -seconds if text[0:1] == "-" else seconds


def offset_text(seconds: int) -> str:
    """Seconds east of UTC as the census writes an offset: `+HH:MM` or `-HH:MM`."""
    sign = "-" if seconds < 0 else "+"
    size = -seconds if seconds < 0 else seconds
    return f"{sign}{size // _HOUR:02d}:{(size % _HOUR) // 60:02d}"


def rule_text(rule: Rule) -> str:
    """A rule as the description publishes it: its family, a space, its standard offset (`us -05:00`)."""
    return f"{rule.family} {offset_text(rule.standard)}"


def admitted(rule: Rule) -> bool:
    """Whether a rule is one the description may publish: one family of `FAMILIES`, its standard offset from -12:00 to +13:00 with minutes 00, 30 or 45.

    The one definition inference (`read_cell`), publication and the loader
    (`parsed_rule`) apply (lane DST's repair 2, Codex's items 7 and 8): a
    column whose offsets only a rule outside it would fit reads no rule, so
    it keeps the description it had before the rule.
    """
    size = -rule.standard if rule.standard < 0 else rule.standard
    return (
        rule.family in FAMILIES
        and _LOWEST <= rule.standard <= _HIGHEST
        and size % _HOUR in _MINUTES_ADMITTED
    )


def parsed_rule(text: str) -> "Rule | None":
    """The rule a published `offset_rule` names, or None where the text names none."""
    if not isinstance(text, str):
        return None
    space = -1
    for place in range(len(text)):
        if text[place] == " ":
            if space >= 0:
                return None
            space = place
    family = text[0:space] if space > 0 else ""
    written = text[space + 1 :] if space > 0 else ""
    if family not in FAMILIES:
        return None
    standard = offset_seconds(written)
    if standard is None or offset_text(standard) != written:
        return None
    rule = Rule(family, standard)
    return rule if admitted(rule) else None


def _weekday(days: int) -> int:
    """Monday 0 to Sunday 6 of a day counted from 1970-01-01, a Thursday."""
    return (days + 3) % 7


def _sunday(year: int, month: int, nth: int) -> int:
    """The day number of a month's `nth` Sunday, or of its last where `nth` is 0."""
    if nth > 0:
        first = parsing.days_from_civil(year, month, 1)
        return first + (6 - _weekday(first)) % 7 + 7 * (nth - 1)
    following = parsing.days_from_civil(year + 1, 1, 1) if month == 12 else parsing.days_from_civil(year, month + 1, 1)
    last = following - 1
    return last - (_weekday(last) + 1) % 7


def changes(rule: Rule, year: int, memo: "dict[tuple[str, int, int], tuple[int, int]] | None" = None) -> "tuple[int, int]":
    """The two instants, in seconds from 1970 UTC, a year's clocks change on: summer time's start, then its end.

    For a southern family the end (April) comes before the start (its
    September or October) in the same year. A year outside the family's
    own years is read under its nearest era. ``memo``, where given, keeps
    each year's pair for the caller's own run (no module-level cache).
    """
    key = (rule.family, rule.standard, year)
    if memo is not None and key in memo:
        return memo[key]
    standard = rule.standard
    if rule.family == US:
        if year >= 2007:
            start, end = _sunday(year, 3, 2), _sunday(year, 11, 1)
        else:
            start, end = _sunday(year, 4, 1), _sunday(year, 10, 0)
        found = (start * _DAY + 2 * _HOUR - standard, end * _DAY + 2 * _HOUR - (standard + _HOUR))
    elif rule.family == EU:
        found = (_sunday(year, 3, 0) * _DAY + _HOUR, _sunday(year, 10, 0) * _DAY + _HOUR)
    else:
        start = _sunday(year, 10, 1) if rule.family == AU else _sunday(year, 9, 0)
        end = _sunday(year, 4, 1)
        found = (start * _DAY + 2 * _HOUR - standard, end * _DAY + 3 * _HOUR - (standard + _HOUR))
    if memo is not None:
        memo[key] = found
    return found


def _year_of(rule: Rule, instant: int) -> int:
    """The year of an instant on the zone's standard clock."""
    return parsing.civil_from_days((instant + rule.standard) // _DAY)[0]


def offset_at(rule: Rule, instant: int, memo: "dict[tuple[str, int, int], tuple[int, int]] | None" = None) -> int:
    """The offset, in seconds east of UTC, the rule puts in force at an instant (seconds from 1970 UTC)."""
    start, end = changes(rule, _year_of(rule, instant), memo)
    if rule.family in _SOUTHERN:
        summer = instant < end or instant >= start
    else:
        summer = start <= instant < end
    return rule.standard + _HOUR if summer else rule.standard


def in_force(
    rule: Rule, local: int, memo: "dict[tuple[str, int, int], tuple[int, int]] | None" = None
) -> "tuple[int, ...]":
    """Every offset a wall-clock moment may wear under the rule, the earlier occurrence first.

    ``local`` is the wall clock in seconds from 1970-01-01 00:00 read as
    if it were UTC. Empty in the hour the clocks skip, both offsets in the
    hour they repeat (summer time's first), the one in force elsewhere.
    """
    found: "list[int]" = []
    for offset in (rule.standard + _HOUR, rule.standard):
        if offset_at(rule, local - offset, memo) == offset:
            found += [offset]
    return tuple(found)


def first_instant(
    rule: Rule, local: int, memo: "dict[tuple[str, int, int], tuple[int, int]] | None" = None
) -> int:
    """The first instant whose wall clock under the rule stands at ``local`` or after it.

    In the hour the clocks skip it is the instant they change on; in the
    hour they repeat, its first occurrence.
    """
    here = in_force(rule, local, memo)
    if here:
        return local - here[0]
    start, _end = changes(rule, _year_of(rule, local - rule.standard), memo)
    return start


def covers(rule: Rule, local: int) -> bool:
    """Whether a wall-clock moment's year is one the rule's family is written for."""
    year = parsing.civil_from_days(local // _DAY)[0]
    return _FIRST_YEAR[rule.family] <= year <= LAST_YEAR


def local_seconds(canonical: str) -> "int | None":
    """A canonical stamp's wall clock (`YYYY-MM-DD HH:MM:SS`, any fraction after it) in seconds, or None."""
    if len(canonical) < 19:
        return None
    try:
        days = parsing.days_from_civil(int(canonical[0:4]), int(canonical[5:7]), int(canonical[8:10]))
        return days * _DAY + int(canonical[11:13]) * _HOUR + int(canonical[14:16]) * 60 + int(canonical[17:19])
    except ValueError:
        return None


def changes_around(
    rule: Rule, instant: int, memo: "dict[tuple[str, int, int], tuple[int, int]] | None" = None
) -> "tuple[int, int]":
    """The last change at or before an instant and the first after it: the stretch it wears one offset across."""
    year = _year_of(rule, instant)
    found: "list[int]" = []
    for near in (year - 1, year, year + 1):
        first, second = changes(rule, near, memo)
        found += [first, second]
    before = min(found)
    after = max(found)
    for change in found:
        if before < change <= instant:
            before = change
        if instant < change < after:
            after = change
    return before, after


@dataclasses.dataclass
class Reading:
    """The rule a column's cells agree with, read one cell at a time (method G7.4r's reading; `read_cell`, `rule_read`).

    Each parsed cell gives its canonical text and its offset as the census
    keys it (`+HH:MM`, `""` for none). The rule read is the first family of
    `FAMILIES` every stamp agrees with, with the column's standard offset,
    or none: where any stamp carries no offset, where the column carries
    other than exactly two offsets an hour apart (`Z` among them), where
    one of its years lies outside the family's own, or where a stamp wears
    an offset not in force on its date under every family -- a cell in the
    hour the clocks skip agrees with none -- or where no rule `admitted`
    admits fits it. A whole date carries no offset and is passed over.
    Linear in the cells; nothing is kept per cell. The offsets in force are
    the same through every quarter hour of the wall clock under every rule
    admitted (each change falls on one: `admitted`), so each quarter hour is
    asked once a rule.
    """

    offsets: "dict[str, int]" = dataclasses.field(default_factory=dict)
    alive: "list[Rule]" = dataclasses.field(default_factory=list)
    started: bool = False
    failed: bool = False
    memo: "dict[tuple[str, int, int], tuple[int, int]]" = dataclasses.field(default_factory=dict)
    quarters: "dict[tuple[Rule, int], tuple[int, ...]]" = dataclasses.field(default_factory=dict)


def read_cell(reading: Reading, canonical: str, offset: str) -> None:
    """One parsed cell into a `Reading`: its canonical text and its offset key."""
    if reading.failed:
        return
    if len(canonical) < 19:
        if offset:
            reading.failed = True
        return
    written = offset_seconds(offset) if offset else None
    local = local_seconds(canonical)
    if written is None or local is None:
        reading.failed = True
        return
    if offset not in reading.offsets:
        if offset_text(written) != offset or len(reading.offsets) >= 2:
            reading.failed = True
            return
        reading.offsets[offset] = written
    if not reading.started:
        reading.started = True
        # ...only the rules `admitted` admits, as publication and the loader do.
        reading.alive = [
            rule
            for rule in (Rule(family, standard) for family in FAMILIES for standard in (written, written - _HOUR))
            if admitted(rule)
        ]
    kept: "list[Rule]" = []
    for rule in reading.alive:
        if written != rule.standard and written != rule.standard + _HOUR:
            continue
        key = (rule, local // 900)
        if key not in reading.quarters:
            if len(reading.quarters) > 400000:
                reading.quarters = {}
            reading.quarters[key] = in_force(rule, local - local % 900, reading.memo) if covers(rule, local) else ()
        if written in reading.quarters[key]:
            kept += [rule]
    reading.alive = kept
    if not kept:
        reading.failed = True


def rule_read(reading: Reading) -> str:
    """The rule a `Reading` read, as published, or `""`."""
    if reading.failed or len(reading.offsets) != 2 or not reading.alive:
        return ""
    values = sorted(reading.offsets[key] for key in reading.offsets)
    for rule in reading.alive:
        if rule.standard == values[0] and values[1] == values[0] + _HOUR:
            return rule_text(rule)
    return ""


def rule_of(pairs: "list[tuple[str, str]]") -> str:
    """The rule every pair (canonical text, offset key) agrees with, as a `Reading` reads it, or `""`."""
    reading = Reading()
    for canonical, offset in pairs:
        read_cell(reading, canonical, offset)
        if reading.failed:
            return ""
    return rule_read(reading)

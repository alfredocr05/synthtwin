"""Batch 4q's fix round 4: the held-date room against four families of the product's own date vocabulary (plan P4-D457).

The verify of fix round 3 found four families of spellings that exports write and the room read no year from; on
Codex's construction (`Random(5)`, 19,989 or 19,990 different ISO days of 1930 to 1999, the days 1 to 11 January
2028 at 09:15:30 once each in the spelling named -- eleven cells, their layout named by the census, or ten,
withheld --, shuffled with the same stream, one column `ref` held with `--identifier`, seed 0) 36023624 published
`made_up_years` [[2028, 2137]] beside each, and where the layout was named its twin wrote eight of the eleven real
days as ISO dates; f0ce1e06 wrote none:

1. A ZONE OR A MERIDIEM GLUED TO A STAMP'S RUN-ON CLOCK (`20280101091530Z`, ASN.1's GeneralizedTime;
   `280101091530Z`, its UTCTime; `202801010915AM`): `taxonomy._compact_runs` took the zone's letter as a key's.
2. SAS'S DATETIME AND DATEAMPM, a two-figure year joined to its clock by a colon (`01JAN28:09:15:30`): the two
   figures before the `:` left with the clock as its hour, and ten such cells left 2028 in the room.
3. DATES WRITTEN AS COUNTS (Excel's `46753` to `46763`, Unix seconds): read by nothing.
4. A DAY OF THE YEAR (`2028001`, `%Y%j`; `28001`, `%y%j`): read by nothing (the days 1 to 10 and 20 January,
   since `2028011` is read as 2028-01-1 too).

Each table here is red on 36023624 and on the mutant of its family. The twin's cells are read by CALENDAR DAY,
never by text: against every real day in the product's reader's, ISO, compact and slashed forms, and against the
special days in the family's own spelling too (a twin's record number of five figures read as `%y%j` names a
birth day of the 1900s by chance; the special days are those of 2028).

FOR THE GENERATED SPELLINGS: the generator (tools/measurements/date_spellings.py) writes SAS's DATETIME and
DATEAMPM at every width from 7 to 40 with a year of four figures or a two-figure year from 28 (from 24 to 27 and
below, only where no two-figure room passes 99) and a day of the year with no clock (`%Y%j`, `%y%j`, `%y-%j`,
`%Y-%j`), and the unit gate of tests/test_held_dates_spellings.py asks the room of those. Two forms of these
families stay open, stated limits (lane ID-ROOM3, plan P4-D457), beside the others that file names: a day of the
year with its clock run on in its figures (`28001091530`, `20280010915`, `280010915`, `2028001091530Z`,
`28-001091530`: on this construction with the days 1 to 10 and 20 January 2028, 8 of the 11 real days written on
fix round 4's head 15c89b3b as on 36023624, none on f0ce1e06); and SAS's DATETIME and DATEAMPM with a two-figure
year of 00 to 23, read as the hour, where a two-figure room passes 99 (on the fourth round's verify's table that
wraps it, 20,000 rows, the room [[0, 7], [28, 99]] holds 03 and the twin writes 3 of the ten real days, where
f0ce1e06, with no room, writes 8).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random
import sys
from collections.abc import Callable

import pytest

from synthtwin import cli, date_counts, parsing, taxonomy

import unanswered_identifier_shapes as held_shapes

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
ROWS = 20_000
# The days 1 to 11 January 2028 at 09:15:30; for a day of the year, 1 to 10 and 20 January (the verify's choice).
SPECIAL_DAYS = [datetime.datetime(2028, 1, 1 + step, 9, 15, 30) for step in range(11)]
ORDINAL_DAYS = [datetime.datetime(2028, 1, day, 9, 15, 30) for day in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20)]
EXCEL_ZERO = datetime.datetime(1899, 12, 30)
UNIX_ZERO = datetime.datetime(1970, 1, 1)


def _excel(moment: datetime.datetime) -> str:
    return f"{(moment - EXCEL_ZERO).days}"


def _unix_seconds(moment: datetime.datetime) -> str:
    return f"{int((moment - UNIX_ZERO).total_seconds())}"


def _strp(form: str) -> Callable[[str], "datetime.date | None"]:
    def read(cell: str) -> "datetime.date | None":
        try:
            return datetime.datetime.strptime(cell.strip(), form).date()
        except ValueError:
            return None
    return read


def _counted(cell: str) -> "datetime.date | None":
    """A twin cell read as Excel's serial (five or six figures) or Unix seconds (nine or ten)."""
    text = cell.strip()
    if not text.isdigit():
        return None
    try:
        if 4 <= len(text) <= 7:
            return (EXCEL_ZERO + datetime.timedelta(days=int(text))).date()
        if 9 <= len(text) <= 10:
            return (UNIX_ZERO + datetime.timedelta(seconds=int(text))).date()
    except OverflowError:
        return None
    return None


def _days(cell: str) -> "set[datetime.date]":
    """The calendar days a twin cell names: each reading of the product's reader, ISO and compact forms."""
    found: "set[datetime.date]" = set()
    for member in parsing.DATE_FORMATS:
        read = parsing.parse_datetime(cell, member)
        if read is not None and len(read[0]) >= 10 and read[0][4] == "-" and read[0][7] == "-":
            found.add(datetime.date(int(read[0][0:4]), int(read[0][5:7]), int(read[0][8:10])))
    for form in ("%Y-%m-%d", "%Y%m%d", "%m/%d/%Y", "%d/%m/%Y"):
        day = _strp(form)(cell)
        if day is not None:
            found.add(day)
    return found


def _run(folder: pathlib.Path, speller: Callable[[datetime.datetime], str], specials: "list[datetime.datetime]",
         own: Callable[[str], "datetime.date | None"]) -> "dict[str, object]":
    """Codex's construction with the ``specials`` written by ``speller``: profile `ref` with `--identifier`
    (nobody at the keyboard), generate at seed 0; the block, the room's years, and the twin cells naming a real
    day by calendar day (`_days`), or a special day in the family's own spelling (``own``), or equal to a real
    cell."""
    draw = random.Random(5)
    low = datetime.date(1930, 1, 1).toordinal()
    days = draw.sample(range(low, datetime.date(1999, 12, 31).toordinal() + 1), ROWS - len(specials))
    cells = [datetime.date.fromordinal(day).isoformat() for day in days]
    cells += [speller(one) for one in specials]
    draw.shuffle(cells)
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "t.csv"
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["ref"])
        writer.writerows([[cell] for cell in cells])
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        profiled = cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace", "--identifier", "ref"])
        generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir", f"{folder}", "--seed", "0",
                              "--replace"]) if profiled == 0 else -1
    block = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] if row else "" for row in list(csv.reader(handle))[1:]]
    real: "set[datetime.date]" = set()
    for day in days:
        real.add(datetime.date.fromordinal(day))
    special: "set[datetime.date]" = set()
    for one in specials:
        real.add(one.date())
        special.add(one.date())
    named: "dict[str, bool]" = {}
    for cell in set(twin):
        named[cell] = bool(_days(cell) & real) or own(cell) in special
    room: "set[int]" = set()
    for first, last in block.get("made_up_years", []):
        room.update(range(first, last + 1))
    written = set(cells)
    return {
        "exits": (profiled, generated),
        "block": block,
        # the years the special cells name, four figures and two, that the room holds
        "room_named": sorted(room & {2028, 28}),
        "same_day": sum(1 for cell in twin if named[cell]),
        "equal": sum(1 for cell in twin if cell in written),
    }


def _assert_no_room_for_the_specials(seen: "dict[str, object]") -> None:
    assert seen["exits"] == (0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert seen["room_named"] == [], (block["made_up_years"], seen["room_named"])  # type: ignore[index]
    assert seen["same_day"] == 0 and seen["equal"] == 0, (seen["same_day"], seen["equal"])


@pytest.mark.parametrize(
    ("form", "count"),
    [("%Y%m%d%H%M%SZ", 11), ("%y%m%d%H%M%SZ", 10), ("%Y%m%d%I%M%p", 11)],
)
def test_a_zone_or_a_meridiem_glued_to_a_run_on_clock_leaves_no_room(tmp_path: pathlib.Path, form: str,
                                                                     count: int) -> None:
    """BLOCKER 1: `20280101091530Z` (eleven, named), `280101091530Z` (ten, withheld), `202801010915AM` (eleven).
    On 36023624 [[2028, 2137]] each, eight real days written where named. MUTANT: a zone or meridiem after a run of
    more than eight figures glued like any letter (`_compact_runs`' `zoned` removed), all three red."""
    seen = _run(tmp_path, lambda one: one.strftime(form), SPECIAL_DAYS[0:count], _strp(form))
    _assert_no_room_for_the_specials(seen)


@pytest.mark.parametrize(
    ("form", "count"),
    [("%d%b%y:%H:%M:%S", 10), ("%d%b%y:%I:%M:%S %p", 10), ("%d%b%y:%H:%M", 10)],
)
def test_sas_datetimes_with_a_two_figure_year_leave_no_room(tmp_path: pathlib.Path, form: str, count: int) -> None:
    """BLOCKER 2: SAS's DATETIME16. `01JAN28:09:15:30`, DATEAMPM. `01JAN28:09:15:30 AM` and DATETIME13.
    `01JAN28:09:15`, ten withheld beside the births: on 36023624 a room holding 2028, the year they name (no day
    written: the room is a guarantee by construction). Eleven, named, publish no room on either tree (a named
    clock's layout). MUTANT: two figures before a `:` past 23 read as the hour again (`_without_clocks`), all
    three red."""
    seen = _run(tmp_path, lambda one: one.strftime(form).upper(), SPECIAL_DAYS[0:count], _strp(form))
    _assert_no_room_for_the_specials(seen)


@pytest.mark.parametrize(("system", "count"), [("excel", 11), ("excel", 10), ("seconds", 11)])
def test_dates_written_as_counts_leave_no_room(tmp_path: pathlib.Path, system: str, count: int) -> None:
    """BLOCKER 3: Excel's serials `46753` to `46763` (eleven, named; ten, withheld) and Unix seconds
    `1830330930` and on: on 36023624 [[2028, 2137]], eight, seven and eight real days written. MUTANT: no count
    read (`counted_years` naming nothing), all three red."""
    speller = _excel if system == "excel" else _unix_seconds
    seen = _run(tmp_path, speller, SPECIAL_DAYS[0:count], _counted)
    _assert_no_room_for_the_specials(seen)


@pytest.mark.parametrize(("form", "count"), [("%Y%j", 11), ("%y%j", 11), ("%y%j", 10)])
def test_a_day_of_the_year_leaves_no_room(tmp_path: pathlib.Path, form: str, count: int) -> None:
    """BLOCKER 4: `2028001` .. `2028010`, `2028020` (`%Y%j`, eleven) and `28001` .. (`%y%j`, eleven named, ten
    withheld): on 36023624 [[2028, 2137]], eight real days written where named. MUTANTS: no day of the year read
    (`day_of_year_years` naming nothing), the first red; the two `%y%j` tables stay green there, since a count of
    five figures names a year of the block in some counting system (`28001` days from 1960 fall in 2036), and are
    red where no count is read either."""
    seen = _run(tmp_path, lambda one: one.strftime(form), ORDINAL_DAYS[0:count], _strp(form))
    _assert_no_room_for_the_specials(seen)


@pytest.mark.parametrize(
    ("cell", "four", "two"),
    [
        # BLOCKER 1: a zone or a meridiem glued to a run of more than eight figures ends a stamp's clock
        ("20280101091530Z", [2028], [20]),
        ("280101091530Z", [2801], [28, 1]),
        ("202801010915AM", [2028], [20]),
        ("2801010915p.m.", [2801], [28, 1]),
        ("20280101091530UTC", [2028], [20]),
        # ...a key's figures glued to a letter stay no date, and a zone after eight figures or fewer stays glued
        ("R20280101091530Z", [], []),
        ("20280105Z", [], []),
    ],
)
def test_a_zone_after_a_stamp_s_run_on_clock_is_no_glued_letter(cell: str, four: "list[int]",
                                                                 two: "list[int]") -> None:
    """`taxonomy.unread_years` on blocker 1's cells: the run is read as a compact stamp. MUTANT: `zoned` removed,
    the first five red."""
    assert taxonomy.unread_years(cell) == (four, two)


@pytest.mark.parametrize(
    ("cell", "two"),
    [
        ("01JAN28:09:15:30", [1, 28, 2]),
        ("01JAN28:09:15", [1, 28, 2]),
        ("01JAN28:09", [1, 28, 9, 2]),
        ("01JAN28:09:15:30 AM", [1, 28, 2]),
        ("01JAN28:9:15:30.123 PM", [1, 28, 2]),
        # ...and, read with the hour's last figure alone, a field and an hour: `37-4-7` and `9:15` glued
        ("37-4-79:15", [79, 37]),
        ("Sat 28 Jan 49:15", [49, 28, 4]),
    ],
)
def test_two_figures_past_the_last_hour_before_a_colon_are_no_hour(cell: str, two: "list[int]") -> None:
    """`taxonomy.cell_date_years` on blocker 2's cells (SAS's DATETIME and DATEAMPM): two figures before a `:`
    read past 23 are the date's year, and the clock opens at the next `:`; read with the hour's last figure alone,
    they are a field and an hour (`49:15`: the day 4 and `9:15`). MUTANTS: the joint read as the hour, the first
    five red; two figures past 23 never split, the last red."""
    assert taxonomy.cell_date_years(cell) == ([], two)


@pytest.mark.parametrize(
    ("cell", "year"),
    [
        ("46753", 2028), ("46757.385764", 2028), ("46757,385764", 2028),  # Excel's 1900 serial, a time after a mark
        ("45291", 2028),  # Excel's 1904 serial of 1 January 2028
        ("24837", 2028),  # days from 1960
        ("2145950130", 2028),  # seconds from 1960
        ("2145950130000", 2028),  # milliseconds from 1960
        ("21184", 2028),  # days from 1970
        ("1830330930", 2028), ("1830330930000", 2028), ("1830330930000000", 2028),
        ("1830330930000000000", 2028),  # seconds to nanoseconds from 1970
        ("68300", 2027), ("68301", 2028),  # days from 31 December 1840
        ("14049710130", 2028),  # seconds from 14 October 1582
    ],
)
def test_every_counting_system_names_its_year(cell: str, year: int) -> None:
    """`taxonomy.counted_years`: each member of `date_counts.MEMBERS` reads a count as the day it names, to the
    nanosecond and never rounded past midnight, and holds its year. MUTANT: no count read, every case red."""
    assert year in taxonomy.counted_years(cell)


def test_a_count_after_noon_on_the_year_s_last_day_holds_that_year() -> None:
    """A count of 31 December 2028 at 18:00 holds 2028 (the day it falls on), where a reading rounded to the
    nearest day would name 1 January 2029 alone."""
    moment = datetime.datetime(2028, 12, 31, 18, 0, 0)
    assert 2028 in taxonomy.counted_years(_unix_seconds(moment))
    assert 2028 in taxonomy.counted_years(f"{(moment - EXCEL_ZERO).days}.75")


@pytest.mark.parametrize(
    ("cell", "four", "two"),
    [
        ("2028001", [2028], []), ("2028366", [2028], []), ("2027365", [2027], []),
        ("28001", [], [28]), ("28-001", [], [28]), ("2028-001", [2028], []), ("28/150", [], [28]),
        ("Sat 2028005", [2028], []), ("2028005T0915", [2028], []),
        # ...no day of the year: day 0, past the year's last day, a year opening with a nought, letters glued
        ("2028000", [], []), ("2027366", [], []), ("0280010", [], []), ("D2028001", [], []), ("28367", [], []),
    ],
)
def test_a_day_of_the_year_names_its_year(cell: str, four: "list[int]", two: "list[int]") -> None:
    """`taxonomy.day_of_year_years`: a compact run of seven figures (`%Y%j`, SAS's JULIAN7.) or of five (`%y%j`,
    JULIAN5.), and a year of two or four figures beside a field of three (`%y-%j`, `%Y-%j`), where the three are a
    day of that year. MUTANT: no day of the year read, the first nine red."""
    assert taxonomy.day_of_year_years(cell) == (four, two)


def test_the_generator_writes_every_member_of_the_product_s_vocabulary(monkeypatch: pytest.MonkeyPatch) -> None:
    """tools/measurements/date_spellings.py writes every zone word and offset of the layout grammar, every
    meridiem, every zone word the room's clock reader reads, every counting system the product names and the four
    day-of-the-year forms, so the unit gate (tests/test_held_dates_spellings.py) asks the room of each: a member the
    product gains and the generator does not write turns this red."""
    monkeypatch.syspath_prepend(str(REPOSITORY / "tools" / "measurements"))
    monkeypatch.delitem(sys.modules, "date_spellings", raising=False)
    import date_spellings as generator

    for word in parsing._LAYOUT_ZULU_FIELDS:
        assert word in generator.ZONE_WORDS, word
    for field in parsing._LAYOUT_SIGNED_FIELDS:
        shape = field.replace("H", "0").replace("M", "0")
        for sign in ("+", "-"):
            assert any(
                offset[0] == sign and offset[1:].replace("5", "0").replace("6", "0") == shape[1:]
                for offset in generator.ZONE_OFFSETS
            ), (sign, field)
    for word in taxonomy._CLOCK_ZONES:
        assert word in [parsing.folded(one) for one in generator.ZONE_WORDS], word
    for morning, evening in parsing._LAYOUT_MERIDIEMS.values():
        assert morning in generator.MERIDIEMS and evening in generator.MERIDIEMS, (morning, evening)
    assert [system[0] for system in generator.COUNT_SYSTEMS] == list(date_counts.MEMBERS)
    assert [form for form, _year in generator.DAY_OF_YEAR_FORMS] == ["%Y%j", "%y%j", "%y-%j", "%Y-%j"]
    families = {generator.family_of(one) for one in generator.spellings()}
    assert families >= {"date_part", "glued_unpadded_hour", "zone_or_meridiem", "sas", "count", "day_of_year"}

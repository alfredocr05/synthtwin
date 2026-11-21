"""Batch 4q's fix round 3: the held-date room against every spelling of a day the generator writes (plan P4-D457).

The verify of fix round 2 found two more neighbours of the round's own blocker. A COMPACT STAMP -- its clock run on
in one run of figures (`202801010915`, `2801010915`, `20280101091530`), after a `T` (`20280101T091530`,
`280101T0915`) or with a fraction after a point (`20280101091530.000000`) -- was read by no member of the date
reader and no order of its layout, held no run of exactly four figures, and `taxonomy.unread_years` read a run only
of five to eight figures: on Codex's construction (`Random(5)`, 19,989 different ISO days of 1930 to 1999, the
eleven days 1 to 11 January 2028 once each in the spelling named, shuffled with the same stream, one column `ref`
held with `--identifier`, seed 0) c22837e6 published `made_up_years` [[2028, 2137]] and its twin wrote eight of the
eleven real days as ISO dates in each of the six spellings; f0ce1e06 wrote none. And a CLOCK WRITTEN FIRST
(`09:15 01/01/28`, `9:15 AM 01 Jan 28`): the cell's fields stopped at the clock, so ten such cells beside the
births left 2028 in the room (no day was written at seeds 0 to 3: a guarantee missing, not a day measured).

Three hand lists in three rounds each left a neighbour open, so the spellings are now WRITTEN, not listed:
tools/measurements/date_spellings.py builds them combinatorially -- every order of year, month and day; years of
one to four figures; months in figures, three letters, with a point and in full, in upper, lower and title case;
days padded, not, and with an ordinal's letters; no mark, a hyphen, a slash, a point, a space or a comma between
the fields; a clock none, after, glued, after a `T`, run on, with seconds, a fraction, a meridiem or a zone, or
before; a weekday word, brackets or a label -- and the unit gate asks of each spelling of a day whose year the room
may take whether `taxonomy.cell_date_years` (with the cross rule) holds that year. Fix round 4 (the verify of fix
round 3) adds five families the generator writes in full: a zone or a meridiem glued to a clock run on in a stamp's
figures; SAS's DATETIME and DATEAMPM at every width from 7 to 40, with a year of four figures or a two-figure year
from 28 (from 24 to 27 and below, only where no two-figure room passes 99); dates written as counts in every
counting system the product names; a day of the year with no clock (`%Y%j`, `%y%j`, `%y-%j`, `%Y-%j`); and a clock
glued to the date with an hour of one figure.

FOR THE GENERATED SPELLINGS ONLY, what stays open is named below (`_stays_open`, four classes, lane ID-ROOM2) with
its reason, and no other generated spelling may be. The gate closes nothing the generator does not write, and among
the spellings beyond it these stay open, stated limits (lane ID-ROOM3, plan P4-D457): a month alone (`202801`,
HL7's month; `January of 28`); month words outside English, roman months and ranges of days (`01-ENE-28`,
`01.I.28`, `Jan 1 to 4 '28`); letters glued to a date's run (`DOB20280101`) and a zone glued to a compact date with
no clock (`20280105Z`); the rare compact forms (ISBT 128's `028001`, `12801010915`, `28010109`) and a day of the
year in six figures (`128001`); a day of the year with its clock run on in its figures (`28001091530`,
`20280010915`, `2028001091530Z`: on Codex's construction with the days 1 to 10 and 20 January 2028 at 09:15:30, 8 of
the 11 real days written on fix round 4's head 15c89b3b as on 36023624, none on f0ce1e06); SAS's DATETIME and
DATEAMPM with a two-figure year of 00 to 23, read as the hour, where a two-figure room passes 99
(`09JAN03:21:45:05`: on the fourth round's verify's table that wraps it, 20,000 rows, the room [[0, 7], [28, 99]]
holds 03 and the twin writes 3 of the ten real days, where f0ce1e06, with no room, writes 8); counts outside the
count grammar (`46,753`, `[46757]`, a leading plus); and a zone word outside the clock's list glued to a stamp's
clock (`20280101091530IST`).

The table cases run the command at the table floor (20,000 rows) and read the twin's cells against the real days
by CALENDAR DAY, never by spelling.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import importlib
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import cli, parsing, taxonomy

import unanswered_identifier_shapes as held_shapes

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
ROWS = 20_000


def _generator(monkeypatch: pytest.MonkeyPatch) -> object:
    """tools/measurements/date_spellings.py, imported afresh by its name, the search path restored after."""
    monkeypatch.syspath_prepend(str(REPOSITORY / "tools" / "measurements"))
    monkeypatch.delitem(sys.modules, "date_spellings", raising=False)
    return importlib.import_module("date_spellings")


def _stays_open(spelling: object) -> str:
    """The class a spelling the room may leave open belongs to, or '' (the gate: no other generated spelling is open).

    Each is a reading in which the year stands where common layouts put a DAY or a year's own figures, so holding
    it would take the room of every held column of those layouts (NF137, the owned price): a two-figure year
    written first beside a month's word (`28-Jan-01`: 28 January 2001 in the `dd-Mon-yy` of many exports; LANE
    ID-ROOM2's, as stated since fix round 2); a two-figure year written between the month and the day where it
    reads as a day (`01-28-05`, `05/28/01`: the day of `mm-dd-yy` and `dd/mm/yy`; past 31 it is read as the year,
    `07-37-04`); and a compact run so ordered (`012805`, `01202805`, `0102805`, and a stamp's run, `0260290915`),
    which no export writes and whose middle figures are the day of `mmddyy` and `ddmmyy`, the year's own last
    two of `yyyymm` (`194503` would hold 2045) and `ddyy` of `mmddyyyy` (`01211945` would hold 2119). And a
    three-figure year in a compact stamp, its clock run on (`02801050915`), which no export writes either: a
    stamp's first seven figures read as a date name years of the room in the commonest stamp, `yyyymmddhhmm`
    (`195204300259` would hold 2043), and a held column of births beside such stamps of the 1900s loses its room.
    """
    if spelling.kind != "date":  # type: ignore[attr-defined]
        # fix round 4's families (SAS's DATETIME and DATEAMPM, counts, a day of the year): none stays open
        return ""
    order = spelling.order  # type: ignore[attr-defined]
    year_form = spelling.year_form  # type: ignore[attr-defined]
    figures = spelling.month_form.startswith("figures")  # type: ignore[attr-defined]
    as_a_day = spelling.day[0] % 100 <= 31  # type: ignore[attr-defined]
    if order == "YMD" and year_form == "two" and not figures and as_a_day:
        return "a two-figure year first beside a month's word"
    if order in ("MYD", "DYM") and figures and spelling.separator == "none":  # type: ignore[attr-defined]
        return "a compact run with its year between the month and the day"
    if order in ("MYD", "DYM") and figures and year_form == "two" and as_a_day:
        return "a two-figure year between the month and the day, where it reads as a day"
    placement = spelling.clock.split(":", 1)[0]  # type: ignore[attr-defined]
    if year_form == "three" and spelling.separator == "none" and placement in _RUN_ON_WITHOUT_T:  # type: ignore[attr-defined]
        return "a three-figure year in a compact stamp, its clock run on"
    return ""


# The clocks run on in a compact date's figures with no `T` before them, a zone or a meridiem after them or none
# (fix round 4): a three-figure year before them stays open.
_RUN_ON_WITHOUT_T = (
    "run_on", "run_on_seconds", "run_on_fraction", "zone_run_on", "zone_run_on_seconds", "zone_run_on_fraction",
    "meridiem_run_on", "meridiem_run_on_seconds",
)


def test_every_generated_spelling_of_a_day_of_the_room_holds_the_year_it_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """THE UNIT GATE: for each generated spelling of a day whose year -- a year of four figures as itself, one of one
    to three figures as its last figures in both centuries, a count's or a day of the year's own -- is one the room
    may take (from `taxonomy.MADE_UP_FIRST_YEAR`), `taxonomy.cell_date_years` holds that year (a two-figure year as
    19yy and 20yy), save the classes `_stays_open` names; it says nothing of a spelling the generator does not
    write. Of SAS's DATETIME and DATEAMPM the generator writes a year of four figures or a two-figure year from 28,
    and of a day of the year the four forms with no clock, so the gate asks no two-figure year below 28, a year of
    the room only where a two-figure room passes 99 (there SAS's 00 to 23, read as the hour, stays open), and no day
    of the year with its clock run on (open: plan P4-D457, lane ID-ROOM3). On c22837e6 (the readings composed as its
    `with_made_up_years` composed them) 23,589 of the 153,450 such spellings of round 3 were open, in every clock
    class; on 36023624, round 3's head, fix round 4's families were open. MUTANTS: a run of more than eight figures not read (the compact stamps), the clock set aside with what
    follows it (a clock written first), the `T` before a stamp's clock glued like any letter; and fix round 4's: a
    zone or a meridiem after a stamp's run-on clock glued like any letter, two figures past 23 before a `:` read as
    the hour, no count read, no day of the year read, a glued clock's hour never read as its last figure alone:
    each red here.
    """
    spellings = _generator(monkeypatch)
    spelled = spellings.spellings()  # type: ignore[attr-defined]
    named = 0
    families: "dict[str, int]" = {}
    for spelling in spelled:
        if any(year >= taxonomy.MADE_UP_FIRST_YEAR for year in spellings.years_named(spelling)):  # type: ignore[attr-defined]
            named += 1
        family = spellings.family_of(spelling)  # type: ignore[attr-defined]
        families[family] = families.get(family, 0) + 1
    assert len(spelled) > 230_000 and named > 195_000, (len(spelled), named)
    for family in ("date_part", "glued_unpadded_hour", "zone_or_meridiem", "sas", "count", "day_of_year"):
        assert families.get(family, 0) > 100, families
    found = spellings.open_spellings(  # type: ignore[attr-defined]
        spelled, taxonomy.cell_date_years, taxonomy.MADE_UP_FIRST_YEAR
    )
    kept: "dict[str, int]" = {}
    outside: "list[tuple[str, list[int]]]" = []
    for spelling, missed in found:
        reason = _stays_open(spelling)
        if reason:
            kept[reason] = kept.get(reason, 0) + 1
        else:
            outside += [(spelling.text, missed)]
    assert not outside, (len(outside), outside[:12], kept)


@pytest.mark.parametrize(
    ("cell", "four", "two"),
    [
        # a compact stamp: the clock run on, after a `T`, with a fraction after a point
        ("202801010915", [2028], [20]),
        ("2801010915", [2801], [28, 1]),
        ("20280101091530", [2028], [20]),
        ("20280101T091530", [2028], []),
        ("280101T0915", [], [28, 1]),
        ("20280101091530.000000", [2028], [20]),
        # a clock written first, glued, with a meridiem or a zone, the fields on both sides of it read
        ("09:15 01/01/28", [], [1, 28]),
        ("9:15 AM 01 Jan 28", [], [1, 28]),
        ("09:15:30 28-01-01 (Sat)", [], [28, 1]),
        ("01/05/2809:15", [], [1, 5, 28, 80]),
        ("99-30-NovT09:15", [], [99]),
        # a month's word glued to its day and a year of three or four figures
        ("Mar132045", [2045], []),
        ("206029Feb", [6029, 2060], []),
        # a run of seven figures with a year of three
        ("1208098", [1208, 8098], [98]),
        ("9812Aug (Sat)", [], [98]),
        # no letter glued to the run, save a stamp's `T`: a key's figures stay no date
        ("R10052028", [], []),
        ("R202801010915", [], []),
    ],
)
def test_the_readings_of_a_cell_no_reading_reads(cell: str, four: "list[int]", two: "list[int]") -> None:
    """`taxonomy.unread_years` on the verify's spellings and their neighbours: a run of more than eight figures read
    by its first eight and six; a `T` before a clock's figures glued to the run; the clock set aside wherever it
    stands; a month's word beside its day and year run together wherever the pair stands. A reading of a run's first
    figures may name a year no day of the cell is in (`2801`, `20`): the room holds it too, the conservative side; a
    run's first seven are not read (a three-figure year in a stamp stays open: `_stays_open`). MUTANTS: the long-run reading removed, the clock set aside with what follows it."""
    assert taxonomy.unread_years(cell) == (four, two)


@pytest.mark.parametrize(
    ("cell", "two"),
    [
        ("07-37-04", [37]),
        ("04/37/07", [37]),
        ("Sat 28-01-05", [28]),
        ("09:15 28-01-05", [28]),
        ("28-01-05T09:15 EST", [28]),
        # ...a middle run of 31 or less is the day of `mm-dd-yy` and `dd-mm-yy`
        ("01-28-05", []),
    ],
)
def test_a_run_that_can_be_no_day_is_read_as_the_year_wherever_it_stands(cell: str, two: "list[int]") -> None:
    """`taxonomy.year_first_years`: three neighbouring runs of one or two figures anywhere in the cell, read year
    first; and a middle run past 31 read as the year. MUTANT: the middle run never read, `07-37-04` red."""
    assert taxonomy.year_first_years(cell) == two


def _days(cell: str) -> "set[datetime.date]":
    """The calendar days a twin cell names: each reading of the product's reader, ISO and compact forms."""
    found: "set[datetime.date]" = set()
    for member in parsing.DATE_FORMATS:
        read = parsing.parse_datetime(cell, member)
        if read is not None and len(read[0]) >= 10 and read[0][4] == "-" and read[0][7] == "-":
            found.add(datetime.date(int(read[0][0:4]), int(read[0][5:7]), int(read[0][8:10])))
    for form in ("%Y-%m-%d", "%Y%m%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            found.add(datetime.datetime.strptime(cell.strip(), form).date())
        except ValueError:
            continue
    return found


def _run(folder: pathlib.Path, written: str, count: int) -> "dict[str, object]":
    """Codex's construction with ``count`` days from 1 January 2028 written as ``written``: profile `ref` with
    `--identifier` (nobody at the keyboard), generate at seed 0; the block and the twin cells naming a real day."""
    draw = random.Random(5)
    low = datetime.date(1930, 1, 1).toordinal()
    days = draw.sample(range(low, datetime.date(1999, 12, 31).toordinal() + 1), ROWS - count)
    cells = [datetime.date.fromordinal(day).isoformat() for day in days]
    special = [datetime.datetime(2028, 1, 1 + step, 9, 15, 30) for step in range(count)]
    cells += [one.strftime(written) for one in special]
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
    for one in special:
        real.add(one.date())
    named: "dict[str, bool]" = {}
    for cell in set(twin):
        named[cell] = bool(_days(cell) & real)
    return {
        "exits": (profiled, generated),
        "block": block,
        "same_day": sum(1 for cell in twin if named[cell]),
        "equal": sum(1 for cell in twin if cell in set(cells)),
    }


@pytest.mark.parametrize("written", ["%Y%m%d%H%M", "%y%m%d%H%M", "%Y%m%dT%H%M%S"])
def test_codex_s_eleven_days_written_as_compact_stamps_leave_no_room(tmp_path: pathlib.Path, written: str) -> None:
    """Codex's construction, the eleven days written `202801010915`, `2801010915` and `20280101T091530`: on
    c22837e6 `[[2028, 2137]]` and eight of the real days written as ISO dates in each. Now 2028 is held, the block
    from 2028 is no room (NF137, the owned price) and no twin cell names a real day. MUTANTS: a run of more than
    eight figures not read, the two runs of figures red; the `T` glued like any letter, the third red."""
    seen = _run(tmp_path, written, 11)
    assert seen["exits"] == (0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert block["made_up_years"] == [], block["made_up_years"]  # type: ignore[index]
    assert seen["same_day"] == 0 and seen["equal"] == 0, seen["same_day"]


@pytest.mark.parametrize("written", ["%H:%M %m/%d/%y", "%I:%M %p %d %b %y"])
def test_ten_days_written_after_their_clock_leave_no_room(tmp_path: pathlib.Path, written: str) -> None:
    """The verify's CARRY 1: ten cells `09:15 01/01/28` (or `09:15 AM 01 Jan 28`) beside the births, their layout
    withheld by the census: on c22837e6 `[[2028, 2137]]`, a room holding the year those cells name (no day was
    written at seeds 0 to 3; the room is a guarantee by construction, not by chance). Now the clock is set aside
    wherever it stands, 2028 is held and the block from 2028 is no room. MUTANT: the clock set aside with what
    follows it, red."""
    seen = _run(tmp_path, written, 10)
    assert seen["exits"] == (0, 0)
    block = seen["block"]
    assert block["made_up_years"] == [], block["made_up_years"]  # type: ignore[index]
    assert seen["same_day"] == 0 and seen["equal"] == 0, seen["same_day"]

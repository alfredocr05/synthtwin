"""K-HZ-27: the zoo's stamp columns whose offset or zone word is not the one in force on their date, at 20,000 rows (plan P4-D474).

Lane DST (method G7.4r) makes a twin write each stamp at the offset its
zone has in force on the stamp's own date. The zoo holds the stamp columns
that carry an offset or a zone word across the days the clocks change:
`encounters`' admit and discharge stamps (US Eastern), `adt_events`' in
and out stamps (US Central), `wearable_stream`'s local stamps with the
offset after a space (`-0400`), `fhir_observations`' ISO 8601 instants,
`hl7_obx`'s MSH-7 (`YYYYMMDDHHMMSS-0400`) and `zoned_stamps`' Central and
European stamps and Eastern stamps followed by their zone word (`EDT`,
`EST`). Each table runs through `tests/health_zoo.py`'s `run_table` at
20,000 rows with the owner's table floor on -- profiled, answered with the
zoo's general facts, generated at seed 0, validated -- and the analyst's
own checks of those columns are read: the cells written at an offset, or
with a zone word, not in force on their date (the zoo's fold-aware
calendars, never `zoneinfo`), and a zone-word column whose twin does not
write stamps with their word at all (its reading is lane TR's, plan
P4-D473; the word follows the offset once both lanes stand).

Printed: `columns` the stamp columns read, `columns_wrong` those with a
cell off its date (or not written as a stamp with its word), `cells_wrong`
their cells, `validate_misses` the six tables' validate misses, and
`later_share_off` the zoo's two checks of the hour the clocks repeat (its
later occurrence present, and its share) that fail -- the twin's cells in
that hour are where its instants stand, which the description places only
as finely as its facts. And, for the Central and European stamps of
`zoned_stamps` (repair 1 of lane DST, skeptic 1's items 1 and 3):
`empty_windows_named`, each column's 12-hour windows within 72 hours of the
four changes of 2023 and 2024 that hold no twin cell, beside the real's
(48 windows a column), and `first_occurrence_named`, the twin's and the
real's cells in the hour the clocks repeat that wear its FIRST
occurrence's offset, of all its cells there.

THE INVENTED TABLES (repair 1 of lane DST: skeptic 1's items 1 and 2, the
statistics check's item 2), each through the same `run_table` with the
floor on and the zoo's answers, its calendar written below from the
families' own words (never the product's module, never `zoneinfo`):
`six_zones_even`, one row an event, stamps drawn evenly over 2023 and 2024
under six rules (`us` at -05:00 and -06:00, `eu` at +01:00 and +00:00,
`au` at +10:00, `nz` at +12:00); `six_zones_heaped`, the same zones with a
quarter of each column on its four change days and a third of a fall-back
day's in the hour the clocks repeat, which puts a south-eastern rung in
April's repeated hour; `decade_visits`, 1,000 people of 20 rows over 2015
to 2024 with a south-eastern zone's stamps and a western European zone's
ISO stamps, which a change of the clocks cuts a quarter or a month thinly;
and `two_year_visits` at TEN times the rows (10,000
people of 20 rows, 2023 and 2024, US Eastern, Central and Pacific written
`-0700`, and Paris), pooled at the day with its weekday census. REPAIR 2
adds `seven_zones_events` (the statistics check's event table: seven rule
columns of four families, one with the US rule of 1987 to 2006, one to the
minute, one in clinic hours, and a mixed column that reads none) and
`fall_back_hours` (1,000 people, stamps within 36 hours of a fall-back
change in US, European and south-eastern zones, each pooled at the hour,
and US stamps from 01:55 to 02:04:59, at the minute, which the rule does
not admit). Printed: `invented_rules` the columns that publish their rule,
of 28; `invented_off` their twin cells whose offset is not in force on
their date; `invented_misses` the six tables' validate misses beside the
not-admitted minute column's (`minute_column`, which also counts its
twin cells off their date, the base's way of spending its offsets); and
`invented_empty_windows` the even and the heaped tables' twins' empty
12-hour windows within 72 hours of their changes (288 and 240 a table;
the real fills every one: a stated limit, owner RT2, P4-D474). The
scoped verify 2's item 1 of lane DST: `repeated_hour_bucket`, each of
the fall-back table's three hour columns' cells whose wall clock stands
in the hour the clocks repeat (the bucket that holds both its
occurrences), the twin's beside the real's -- at the hour rung the twin
fills that bucket off the real count, short in the European and
south-eastern columns and over in the US one, a stated limit, owner
RT2, P4-D474 -- recorded and never failing (no target bounds it). And
Codex's
item 3: `checked_file_break_named`, whether validate names one cell in the
hour the clocks skip in a file checked against a column pooled at the
month (Codex's own table and probe, 20,000 rows), target true.

EVERY RUN MUST HAVE CHECKED (Codex's item 9 of lane DST): a table whose
profile, answers or generation did not complete, whose validate did not
run, whose real side the analyst could not read, or whose described
columns lack one this driver checks, counts as unchecked:
`checks_incomplete`, target 0, names each (the zoo's six tables and the
invented ones alike).

    python tools/measurements/kpi_zoo_offsets.py --kpi [--rows N] [--zoo-only]
"""

from __future__ import annotations

import argparse
import csv
import datetime
import pathlib
import re
import shutil
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))

import health_zoo  # noqa: E402
import health_zoo_wide  # noqa: E402
import kpi_rules  # noqa: E402

ROWS = 20_000
# The zoned stamps read beside the checks: each column's calendar (the zoo's
# own, fold-aware) and the four changes of the clocks as UTC moments -- US
# Central at 02:00 local on the zoo's spring days (08:00 UTC) and on its
# autumn days (07:00 UTC), Europe at 01:00 UTC on its four days.
_US_CHANGES = tuple(
    datetime.datetime.combine(day, datetime.time(8 if day.month == 3 else 7)) for day in health_zoo.CHANGE_DAYS
)
_EU_CHANGES = tuple(datetime.datetime.combine(day, datetime.time(1)) for day in health_zoo_wide.EU_CHANGE_DAYS)
ZONED = (
    ("central_ts", health_zoo_wide.central_offsets, _US_CHANGES),
    ("eu_ts", health_zoo_wide.eu_offsets, _EU_CHANGES),
)
_HALF_DAY = 43_200
_HOUR = datetime.timedelta(hours=1)


def _sunday(year: int, month: int, nth: int) -> datetime.date:
    """A month's nth Sunday, or its last for nth 0."""
    if nth:
        first = datetime.date(year, month, 1)
        return first + datetime.timedelta(days=(6 - first.weekday()) % 7 + 7 * (nth - 1))
    following = datetime.date(year + (month == 12), month % 12 + 1, 1)
    last = following - datetime.timedelta(days=1)
    return last - datetime.timedelta(days=(last.weekday() + 1) % 7)


def _summer(family: str, standard: int, year: int) -> "tuple[datetime.datetime, datetime.datetime]":
    """Summer time's start and end in a year as UTC moments, by the family's own words (`us` from 1987, `eu`, `au`, `nz`)."""
    zone = datetime.timedelta(seconds=standard)
    if family == "us":
        spring, autumn = (_sunday(year, 3, 2), _sunday(year, 11, 1)) if year >= 2007 else (
            _sunday(year, 4, 1), _sunday(year, 10, 0))
        return (datetime.datetime.combine(spring, datetime.time(2)) - zone,
                datetime.datetime.combine(autumn, datetime.time(2)) - zone - _HOUR)
    if family == "eu":
        return (datetime.datetime.combine(_sunday(year, 3, 0), datetime.time(1)),
                datetime.datetime.combine(_sunday(year, 10, 0), datetime.time(1)))
    start = _sunday(year, 10, 1) if family == "au" else _sunday(year, 9, 0)
    return (datetime.datetime.combine(start, datetime.time(2)) - zone,
            datetime.datetime.combine(_sunday(year, 4, 1), datetime.time(3)) - zone - _HOUR)


def _in_force(family: str, standard: int, local: datetime.datetime) -> "tuple[int, ...]":
    """Every offset a wall clock may wear, summer time's first; none in the hour the clocks skip."""
    found: "list[int]" = []
    for offset in (standard + 3600, standard):
        moment = local - datetime.timedelta(seconds=offset)
        start, end = _summer(family, standard, (moment + datetime.timedelta(seconds=standard)).year)
        summer = (moment < end or moment >= start) if family in ("au", "nz") else start <= moment < end
        if (standard + 3600 if summer else standard) == offset:
            found += [offset]
    return tuple(found)


def _written(offset: int, colon: bool) -> str:
    sign = "-" if offset < 0 else "+"
    size = -offset if offset < 0 else offset
    return f"{sign}{size // 3600:02d}{':' if colon else ''}{size % 3600 // 60:02d}"


# The invented tables: (column, family, standard offset, written form, first year, years).
SIX_ZONES = tuple(
    (name, family, standard, "space", 2023, 2)
    for name, family, standard in (
        ("zone_east", "us", -18000), ("zone_central", "us", -21600), ("zone_west_eu", "eu", 3600),
        ("zone_gmt_eu", "eu", 0), ("zone_south", "au", 36000), ("zone_far_south", "nz", 43200),
    )
)
DECADE = (("visit_south", "au", 36000, "space", 2015, 10), ("visit_west", "eu", 3600, "iso", 2015, 10))
TWO_YEAR = (
    ("seen_east", "us", -18000, "space", 2023, 2), ("seen_central", "us", -21600, "iso", 2023, 2),
    ("seen_pacific", "us", -28800, "compact", 2023, 2), ("seen_paris", "eu", 3600, "space", 2023, 2),
)
# The statistics check's event table (repair 2, the verify's item 1): (column, family, standard, form, first, years).
EVENTS = (
    ("au_ts", "au", 36000, "space", 2012, 13), ("nz_iso", "nz", 43200, "iso", 2012, 13),
    ("sa_compact", "au", 34200, "compact", 2012, 13), ("us_span", "us", -18000, "space", 1995, 21),
    ("uk_ts", "eu", 0, "space", 2016, 9), ("us_minute", "us", -21600, "minute", 2020, 5),
    ("us_clinic", "us", -25200, "clinic", 2019, 6),
)
MIXED = ("us_mixed", "us", -18000)
# The fall-back table (repair 2, Codex's item 1): (column, family, standard, the spans from the 2024 fall-back change,
# in seconds); the last, at the minute rung across the repeated hour, is not admitted to the rule.
FALL_BACK = (
    ("back_us_hour", "us", -18000, ((-36 * 3600, 36 * 3600),)),
    ("back_eu_hour", "eu", 3600, ((-36 * 3600, 36 * 3600),)),
    ("back_au_hour", "au", 36000, ((-36 * 3600, 36 * 3600),)),
    ("back_us_minute", "us", -18000, ((-300, 0), (3300, 3900))),
)


def _even(draw: object, family: str, standard: int, first: int, years: int) -> "tuple[datetime.datetime, int]":
    """A wall clock drawn evenly over the years at an offset in force (either occurrence where the clocks repeat)."""
    while True:
        local = datetime.datetime(first, 1, 1) + datetime.timedelta(seconds=draw.randrange(years * 365 * 86400))  # type: ignore[attr-defined]
        here = _in_force(family, standard, local)
        if here:
            return local, draw.choice(here)  # type: ignore[attr-defined]


def _heaped(draw: object, family: str, standard: int) -> "tuple[datetime.datetime, int]":
    """A wall clock of 2023 or 2024: a quarter on the four days the clocks change, a third of a change day's moved into
    the hour the clocks repeat where that day has one, at an offset in force (skeptic 1's heaped shape)."""
    days = [(change + datetime.timedelta(seconds=standard)).date()
            for year in (2023, 2024) for change in _summer(family, standard, year)]
    if draw.random() < 0.25:  # type: ignore[attr-defined]
        day = draw.choice(days)  # type: ignore[attr-defined]
    else:
        day = datetime.date(2023, 1, 1) + datetime.timedelta(days=draw.randrange(731))  # type: ignore[attr-defined]
    local = datetime.datetime.combine(
        day, datetime.time(draw.randint(0, 23), draw.randint(0, 59), draw.randint(0, 59))  # type: ignore[attr-defined]
    )
    if day in days and draw.random() < 0.34:  # type: ignore[attr-defined]
        for hour in range(24):
            if len(_in_force(family, standard, local.replace(hour=hour))) == 2:
                local = local.replace(hour=hour)
                break
    here = _in_force(family, standard, local)
    while not here:
        local = local + _HOUR
        here = _in_force(family, standard, local)
    return local, draw.choice(here)  # type: ignore[attr-defined]


def _offset_at(family: str, standard: int, moment: datetime.datetime) -> int:
    """The offset in force at a UTC moment, by the family's own words."""
    start, end = _summer(family, standard, (moment + datetime.timedelta(seconds=standard)).year)
    summer = (moment < end or moment >= start) if family in ("au", "nz") else start <= moment < end
    return standard + 3600 if summer else standard


def _cell(draw: object, family: str, standard: int, form: str, first: int, years: int, shape: str) -> str:
    """One stamp of an invented column in its written form."""
    local, offset = _heaped(draw, family, standard) if shape == "heaped" else _even(draw, family, standard, first, years)
    while form == "clinic" and not 8 <= local.hour < 17:
        local, offset = _even(draw, family, standard, first, years)
    if form == "minute":
        return local.strftime("%Y-%m-%d %H:%M") + _written(offset, True)
    joint = "T" if form == "iso" else " "
    return local.strftime(f"%Y-%m-%d{joint}%H:%M:%S") + _written(offset, form != "compact")


def _table_of(columns: "tuple[tuple[str, str, int, str, int, int], ...]", shape: str, key: str) -> object:
    """A builder of an invented table: a person's 20 rows (``shape`` `visits`), one row an event (`even`, `heaped`),
    the event table with its mixed column (`events`) or the fall-back table (`fall_back`)."""

    def build(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        import random

        draw = random.Random(4700 + seed)
        people = max(1, n // 20)
        rows: "list[list[str]]" = []
        for index in range(n):
            row = [f"VP{3000000 + index % people}" if shape in ("visits", "fall_back") else f"EV{3100000 + index}"]
            if shape == "fall_back":
                for _name, family, standard, spans in FALL_BACK:
                    low, high = draw.choice(spans)
                    moment = _summer(family, standard, 2024)[1] + datetime.timedelta(seconds=draw.randrange(low, high))
                    offset = _offset_at(family, standard, moment)
                    local = moment + datetime.timedelta(seconds=offset)
                    row += [local.strftime("%Y-%m-%d %H:%M:%S") + _written(offset, True)]
                rows += [row]
                continue
            for _name, family, standard, form, first, years in columns:
                row += [_cell(draw, family, standard, form, first, years, shape)]
            if shape == "events":
                mixed = _cell(draw, MIXED[1], MIXED[2], "space", 2020, 5, "even")
                if draw.random() < 0.01:
                    mixed = mixed[:-6] + ("-04:00" if mixed.endswith("-05:00") else "-05:00")
                row += [mixed]
            rows += [row]
        names = [column[0] for column in (FALL_BACK if shape == "fall_back" else columns)]
        return [key] + names + ([MIXED[0]] if shape == "events" else []), rows

    return build


def _completed(result: "dict[str, object]", columns: "tuple[str, ...]") -> str:
    """Why a `run_table` result did not check its columns (Codex's item 9 of lane DST), or `""` where it did.

    The profile, every answers round and generation completed, validate
    ran to its report (exit 0 or 3), the analyst read the real side
    without an error, and the description holds every column named.
    """
    steps = result.get("steps") if isinstance(result, dict) else None
    if not isinstance(steps, dict) or result.get("refused_by_floor"):
        return "refused or not run"
    for step in ("profile", "answers", "generate", "validate"):
        found = steps.get(step)
        if found is None and step == "answers":
            continue
        code = found.get("exit") if isinstance(found, dict) else None
        if code not in ((0, 3) if step == "validate" else (0,)):
            return f"{step} exit {code}"
    if result.get("analyst_real_errors"):
        return "the real side unread"
    roles = result.get("roles")
    missing = [column for column in columns if not isinstance(roles, dict) or column not in roles]
    return f"no column {missing[0]}" if missing else ""


def _worn(text: str) -> "tuple[datetime.datetime, int] | None":
    """A twin stamp's wall clock and the offset it wears, or None where the text is no stamp of the invented forms."""
    match = re.match(r"^(\d{4}-\d\d-\d\d)[T ](\d\d:\d\d)(:\d\d)?([+-])(\d\d):?(\d\d)$", text)
    if not match:
        return None
    local = datetime.datetime.strptime(f"{match.group(1)} {match.group(2)}{match.group(3) or ':00'}", "%Y-%m-%d %H:%M:%S")
    return local, (-1 if match.group(4) == "-" else 1) * (int(match.group(5)) * 3600 + int(match.group(6)) * 60)


def _invented(name: str, columns: "tuple[tuple[str, str, int, str, int, int], ...]", rows: int,
              folder: pathlib.Path, shape: str) -> "dict[str, object]":
    """One invented table through `run_table`: its columns publishing their rule, its twin cells off their date, its
    validate misses (the not-admitted minute column's apart, with its cells off their date), its twin's empty 12-hour
    windows within 72 hours of the changes of 2023 and 2024 (even and heaped tables), and why it did not check, if it
    did not."""
    key = "visit_person" if shape in ("visits", "fall_back") else "event_ref"
    named = tuple(column[0] for column in (FALL_BACK if shape == "fall_back" else columns))
    named = named + ((MIXED[0],) if shape == "events" else ())
    table = health_zoo.Table(
        name, ".csv", _table_of(columns, shape, key), lambda header, body: health_zoo.csv_bytes(header, body),
        {name: (key,) + named}, {key: "identifier"},
        health_zoo._csv_reader(), (), person=key if shape in ("visits", "fall_back") else "",
    )
    result = health_zoo.run_table(table, folder / name, rows, 0, small_tables_refused=True)
    profile = folder / name / f"{name}-profile.json"
    twin = folder / name / f"{name}-twin.csv"
    why = _completed(result, named)
    found: "dict[str, object]" = {"ruled": 0, "off": 0, "misses": 0, "empty": 0, "minute": "", "repeated": "", "why": why}
    if why or not profile.exists() or not twin.exists():
        found["why"] = why or "no twin"
        shutil.rmtree(folder / name, ignore_errors=True)
        return found
    import json

    blocks = {block["name"]: block for block in json.loads(profile.read_text(encoding="utf-8"))["columns"]}
    misses = [miss for miss in result["misses"] if not (isinstance(miss, list) and miss and miss[0] == "back_us_minute")]
    found["misses"] = len(misses)
    if shape == "fall_back":
        block = blocks.get("back_us_minute", {})
        astray = 0
        for text in _column(twin, "back_us_minute"):
            worn = _worn(text)
            astray += 1 if worn is None or worn[1] not in _in_force("us", -18000, worn[0]) else 0
        found["minute"] = (
            f"rung {(block.get('time_grain') or {}).get('rung')}, rule {block.get('offset_rule') or 'none'}, "
            f"validate misses {len(result['misses']) - len(misses)}, cells off their date {astray}"
        )
        found["repeated"] = _repeated_hour_bucket(folder / name / f"{name}.csv", twin)
    listed = [(column[0], column[1], column[2]) for column in (FALL_BACK[:3] if shape == "fall_back" else columns)]
    ruled = off = empty = 0
    for column, family, standard in listed:
        ruled += 1 if blocks.get(column, {}).get("offset_rule") else 0
        held: "set[tuple[int, int]]" = set()
        changes = [change for year in (2023, 2024) for change in _summer(family, standard, year)]
        for text in _column(twin, column):
            worn = _worn(text)
            if worn is None:
                off += 1
                continue
            local, written = worn
            off += 0 if written in _in_force(family, standard, local) else 1
            moment = local - datetime.timedelta(seconds=written)
            for place, change in enumerate(changes):
                distance = (moment - change).total_seconds()
                if -3 * 86400 <= distance < 3 * 86400:
                    held.add((place, int(distance // _HALF_DAY)))
        if shape in ("even", "heaped"):
            empty += sum(1 for place in range(len(changes)) for window in range(-6, 6) if (place, window) not in held)
    found.update({"ruled": ruled, "off": off, "empty": empty})
    shutil.rmtree(folder / name, ignore_errors=True)
    return found


def _repeated_hour_bucket(real: pathlib.Path, twin: pathlib.Path) -> str:
    """Each hour column of the fall-back table: its cells whose wall clock, as written, stands in the hour the clocks
    repeat on the 2024 change (the bucket that holds both occurrences), the twin's beside the real's (the scoped
    verify 2's item 1 of lane DST; recorded, never failing, owner RT2)."""
    found: "list[str]" = []
    for column, family, standard, _spans in FALL_BACK[:3]:
        repeated = _summer(family, standard, 2024)[1] + datetime.timedelta(seconds=standard)
        counts: "list[int]" = []
        for path in (twin, real):
            held = 0
            for text in _column(path, column):
                worn = _worn(text)
                held += 1 if worn is not None and worn[0].replace(minute=0, second=0) == repeated else 0
            counts += [held]
        found += [f"{column} twin {counts[0]}, real {counts[1]}"]
    return "; ".join(found)


def _codex_months(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's table of item 3, its generator as written: a person's 2024 visits at US Eastern's offsets in force,
    March on its 1st to 9th, November on its 1st and 2nd, every other month on its 1st to 28th."""
    import random

    draw = random.Random(701)
    rows: "list[list[str]]" = []
    for index in range(n):
        month = index % 12 + 1
        day = draw.randrange(1, 10) if month == 3 else draw.randrange(1, 3) if month == 11 else draw.randrange(1, 29)
        offset = "-04:00" if 4 <= month <= 11 else "-05:00"
        clock = f"{draw.randrange(24):02d}:{draw.randrange(60):02d}:{draw.randrange(60):02d}"
        rows += [[f"PT{500000 + index % 1000}", f"2024-{month:02d}-{day:02d} {clock}{offset}"]]
    return ["patient_ref", "seen_at"], rows


def _checked_file_break(rows: int, folder: pathlib.Path) -> "tuple[bool, str]":
    """Codex's item 3 at the floor: the table described through `run_table`, then its own rows as the checked file with
    the third replaced by `2024-03-10 02:30:00-05:00`; whether validate names `offsets.rule`, and why it did not
    check, if it did not."""
    import contextlib
    import io

    from synthtwin import cli

    table = health_zoo.Table(
        "codex_months", ".csv", _codex_months, lambda header, body: health_zoo.csv_bytes(header, body),
        {"codex_months": ("patient_ref", "seen_at")}, {"patient_ref": "identifier"},
        health_zoo._csv_reader(), (), person="patient_ref",
    )
    place = folder / "codex_months"
    result = health_zoo.run_table(table, place, rows, 0, small_tables_refused=True)
    why = _completed(result, ("seen_at",))
    if why:
        shutil.rmtree(place, ignore_errors=True)
        return False, why
    header, body = _codex_months(rows, 0)
    body[2][1] = "2024-03-10 02:30:00-05:00"
    (place / "codex_months-twin.csv").write_bytes(health_zoo.csv_bytes(header, body))
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        cli.main(["validate", str(place / "codex_months-profile.json"), "--replace"], small_tables_refused=True)
    quality = (place / "codex_months-twin-quality.txt").read_text(encoding="utf-8")
    shutil.rmtree(place, ignore_errors=True)
    return "offsets.rule [datetime.offset_rule]: MISSED" in quality, ""


# (table, column, the zoo's check of it) in the order the plan names them.
CHECKS = (
    ("encounters", "admit_ts", "admit_ts wears an offset in force on its date"),
    ("encounters", "discharge_ts", "discharge_ts wears an offset in force on its date"),
    ("adt_events", "in_ts", "in_ts wears a Central offset in force on its date"),
    ("adt_events", "out_ts", "out_ts wears a Central offset in force on its date"),
    ("wearable_stream", "recorded_local", "the local offset is in force on its date"),
    ("fhir_observations", "effective_date_time", "each instant wears an offset in force on its date"),
    ("hl7_obx", "msh_7", "MSH-7 wears an offset in force on its date"),
    ("zoned_stamps", "central_ts", "each Central stamp wears an offset in force on its date"),
    ("zoned_stamps", "eu_ts", "each European stamp wears an offset in force on its date"),
    ("zoned_stamps", "zoned_word", "each zone word is the one in force on its date"),
)
# A zone-word column the twin writes as no stamp with its word is wrong whole.
WORD_PATTERN = ("zoned_stamps", "Eastern stamps with their zone word")
LATER = (
    "some Central stamp in the hour that happens twice is its later occurrence",
    "the later occurrences, as a share of the Central hour that happens twice",
    "some European stamp in the hour that happens twice is its later occurrence",
    "the later occurrences, as a share of the European hour that happens twice",
)
BAD = re.compile(r"^(\d+) bad cell")


def _column(path: pathlib.Path, name: str) -> "list[str]":
    """One column of a CSV file the zoo wrote, as text."""
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = csv.reader(handle)
        header = next(rows)
        place = header.index(name)
        return [row[place] for row in rows if len(row) > place]


def _offset_seconds(text: str) -> int:
    sign = -1 if text[0:1] == "-" else 1
    return sign * (int(text[1:3]) * 3600 + int(text[4:6]) * 60)


def _zoned_reading(cells: "list[str]", offsets: object, changes: "tuple[datetime.datetime, ...]") -> "tuple[int, int, int]":
    """A column's empty 12-hour windows within 72 hours of each change, and its cells in the hour the clocks repeat
    wearing the first occurrence's offset, of all its cells there."""
    held: "dict[tuple[int, int], int]" = {}
    first = twice = 0
    for text in cells:
        try:
            local = datetime.datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        written = text[19:]
        if len(written) != 6:
            continue
        here = offsets(local)  # type: ignore[operator]
        if len(here) == 2:
            twice += 1
            first += 1 if written == here[0] else 0
        moment = local - datetime.timedelta(seconds=_offset_seconds(written))
        for place, change in enumerate(changes):
            distance = (moment - change).total_seconds()
            if -3 * 86400 <= distance < 3 * 86400:
                window = (place, int(distance // _HALF_DAY))
                held[window] = held.get(window, 0) + 1
    empty = sum(1 for place in range(len(changes)) for window in range(-6, 6) if (place, window) not in held)
    return empty, first, twice


def _zoned(folder: pathlib.Path) -> "tuple[str, str]":
    """`empty_windows_named` and `first_occurrence_named` of the zoned stamps' twin, beside the real's."""
    windows: "list[str]" = []
    firsts: "list[str]" = []
    for column, offsets, changes in ZONED:
        twin = _zoned_reading(_column(folder / "zoned_stamps-twin.csv", column), offsets, changes)
        real = _zoned_reading(_column(folder / "zoned_stamps.csv", column), offsets, changes)
        windows += [f"{column} twin {twin[0]}, real {real[0]} of 48"]
        firsts += [f"{column} twin {twin[1]} of {twin[2]}, real {real[1]} of {real[2]}"]
    return "; ".join(windows), "; ".join(firsts)


def measure(rows: int, invented: bool = True) -> "dict[str, object]":
    """Every table of CHECKS at ``rows``, and the invented tables at ``rows`` (one at ten times it), read as the docstring says."""
    tables = sorted({table for table, _column, _check in CHECKS})
    results: "dict[str, dict[str, object]]" = {}
    found: "dict[str, dict[str, object]]" = {}
    seconds: "dict[str, float]" = {}
    windows = firsts = "the zoned stamps did not run"
    breaks: "tuple[bool, str] | None" = None
    with tempfile.TemporaryDirectory(prefix="synthtwin-kpi-offsets-") as folder:
        for name in tables:
            started = time.perf_counter()
            table = health_zoo.table_named(name)
            results[name] = health_zoo.run_zoo(pathlib.Path(folder) / name, rows, tables=(table,))[0]
            seconds[name] = round(time.perf_counter() - started, 1)
            if name == "zoned_stamps" and not _completed(results[name], ("central_ts", "eu_ts")):
                windows, firsts = _zoned(pathlib.Path(folder) / name / name)
            shutil.rmtree(pathlib.Path(folder) / name, ignore_errors=True)
        if invented:
            for name, columns, size, shape in (
                ("six_zones_even", SIX_ZONES, rows, "even"), ("six_zones_heaped", SIX_ZONES, rows, "heaped"),
                ("decade_visits", DECADE, rows, "visits"), ("two_year_visits", TWO_YEAR, 10 * rows, "visits"),
                ("seven_zones_events", EVENTS, rows, "events"), ("fall_back_hours", (), rows, "fall_back"),
            ):
                started = time.perf_counter()
                found[name] = _invented(name, columns, size, pathlib.Path(folder), shape)
                seconds[name] = round(time.perf_counter() - started, 1)
            started = time.perf_counter()
            breaks = _checked_file_break(rows, pathlib.Path(folder))
            seconds["codex_months"] = round(time.perf_counter() - started, 1)
    value = tally(results, found, breaks, rows)
    value["empty_windows_named"] = windows
    value["first_occurrence_named"] = firsts
    value["seconds"] = seconds
    return value


def tally(
    results: "dict[str, dict[str, object]]",
    found: "dict[str, dict[str, object]]",
    breaks: "tuple[bool, str] | None",
    rows: int,
) -> "dict[str, object]":
    """The KPI's value from the runs: the zoo's ``results`` by table, the invented tables' ``found`` (`_invented`), the
    checked-file probe's ``breaks`` (`_checked_file_break`); a table that did not check counts in
    `checks_incomplete`, never as a column checked (Codex's item 9 of lane DST)."""
    failures: "dict[tuple[str, str], str]" = {}
    misses = 0
    incomplete: "list[str]" = []
    for name in sorted({table for table, _column, _check in CHECKS}):
        result = results.get(name, {})
        why = _completed(result, tuple(column for table, column, _check in CHECKS if table == name))
        if why:
            incomplete += [f"{name}: {why}"]
            continue
        misses += len(result["misses"])  # type: ignore[arg-type]
        for _kind, check, reason in result["analyst"]:  # type: ignore[union-attr]
            failures[(name, check)] = reason
    wrong_columns: "list[str]" = []
    cells = 0
    for name, column, check in CHECKS:
        if any(entry.startswith(f"{name}:") for entry in incomplete):
            continue
        why = failures.get((name, check), "")
        if not why and (name, column) == ("zoned_stamps", "zoned_word"):
            why = failures.get(WORD_PATTERN, "")
        if why:
            wrong_columns += [f"{name}.{column}"]
            match = BAD.match(why)
            cells += int(match.group(1)) if match else rows
    later = [f"{check}: {failures[('zoned_stamps', check)]}" for check in LATER if ("zoned_stamps", check) in failures]
    ruled = off = invented_misses = 0
    windows: "list[str]" = []
    minute = repeated = "the fall-back table did not run"
    for name in sorted(found):
        entry = found[name]
        if entry["why"]:
            incomplete += [f"{name}: {entry['why']}"]
            continue
        ruled += int(entry["ruled"])  # type: ignore[call-overload]
        off += int(entry["off"])  # type: ignore[call-overload]
        invented_misses += int(entry["misses"])  # type: ignore[call-overload]
        if name in ("six_zones_even", "six_zones_heaped"):
            windows += [f"{name[10:]} {entry['empty']} of {288 if name == 'six_zones_even' else 240}"]
        if name == "fall_back_hours":
            minute = str(entry["minute"])
            repeated = str(entry.get("repeated") or repeated)
    if breaks is not None and breaks[1]:
        incomplete += [f"codex_months: {breaks[1]}"]
    return {
        "columns": len(CHECKS),
        "columns_wrong": len(wrong_columns),
        "columns_wrong_named": ", ".join(wrong_columns) or "none",
        "cells_wrong": cells,
        "validate_misses": misses,
        "later_share_off": len(later),
        "later_share_off_named": "; ".join(later) or "none",
        "invented_rules": ruled,
        "invented_off": off,
        "invented_misses": invented_misses,
        "invented_empty_windows": "; ".join(windows) or "none",
        "minute_column": minute,
        "repeated_hour_bucket": repeated,
        "checked_file_break_named": bool(breaks is not None and breaks[0]),
        "checks_incomplete": len(incomplete),
        "checks_incomplete_named": "; ".join(incomplete) or "none",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--kpi", action="store_true", help="print the KPI line for kpi_run")
    parser.add_argument("--rows", type=int, default=ROWS)
    parser.add_argument("--zoo-only", action="store_true", help="leave out the invented person tables")
    arguments = parser.parse_args()
    value = measure(arguments.rows, not arguments.zoo_only)
    timing = value.pop("seconds")
    detail = f"{arguments.rows} rows a table, the floor on; seconds a table {timing}"
    if arguments.kpi:
        kpi_rules.emit("K-HZ-27", value, detail)
    else:
        print(value, detail)


if __name__ == "__main__":
    main()

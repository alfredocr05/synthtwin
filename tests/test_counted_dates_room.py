"""P4-D488 (lane ID-ROOM3, part a): no held date, stamp or counted column writes a real day.

WHAT WAS MEASURED (invented tables of 20,000 rows and 1,000 patients born 1928 to 2005, through the commands a
person types; the public head and the lane's base read the same). A held column whose grain reads COUNTED
dates -- spreadsheet serials, seconds or days from an epoch, SAS dates and datetimes -- had no made-up-date
room and its G1 floor drew from the spans its grain records: the method's fixed span while the Safe Harbor
question was open, the real span of the births once it was answered `no`; up to 940 twin cells on 47 real birth
days of single patients, the day counts writing the very real cell up to 749 times, and validate exiting 3. A
held column of counts with no grain wrote the walk's record numbers at the column's widths, and counts of nine to
thirteen figures with a sign cover the real span: 640 twin cells on 32 birth days with nobody answering. And any
held date column that had no room drew from its grain's span the same way: a visit column whose three `99999`
took its room 17,064 twin cells copying real visit days, one patient's rows in another layout (the census
withheld whole) 16,901, a day of the year answered `dates` 203 cells on 10 birth days.

THE RULE (method G9.6c, contract 7.12c). A3: a held column whose grain reads dates, stamps or counted dates draws
its made-up values from the room alone; with no room it writes no date (NF137) -- a date or a stamp blank (since
the lane's repair 1), a count the walk's value only where its published facts put it off every real day, else
the spill. A1: a held counted grain takes the room (`taxonomy.with_made_up_years`'s counted arm: every cell read
in its declared member and in every reading the room holds against, the cross rule too), its G1 floor drawing
each count at the column's own finest unit and reading it back in its member. A1b: a held column of counts with
no grain is read as the counted dates it may be -- declared, its member's counted grain; held by a question about
dates, by an open question offering `identifier` or in people or in rows, the room its counts would take and a
walk that keeps only values off every real day, each only where the span-and-density test reads its counts as
dates (`taxonomy.counts_may_be_dates`, repair 1), a stray word set aside whatever its share and a numeric
placeholder up to one present cell in three. A2: a census withheld whole is read in the layout the grain's reading writes a day in (`taxonomy.member_date_layout`).
A5: a day of the year takes the room as a stamp's is taken.

This file holds the rule's parts, each case fast, and ONE case at 20,000 rows for the writers together; the
planning tables in their modes, the census-withheld shapes, the placeholder table and the zoo's held counted
columns are K-HZ-38's (tools/measurements/kpi_dates_never_real.py, kpi_run --slow). Each case names the mutant
it is red on (the build's wave6/ID-ROOM3/mutants.log; repair 1's wave6/ID-ROOM3/r1c/mutants-final.log).
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import contract, date_counts, generation, grains, parsing, taxonomy, validation

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "measurements"))
sys.path.insert(0, str(ROOT / "tools" / "reference"))

_EPOCHS = {
    "excel-1900": datetime.datetime(1899, 12, 30), "excel-1904": datetime.datetime(1904, 1, 1),
    "days-since-1960": datetime.datetime(1960, 1, 1), "seconds-since-1960": datetime.datetime(1960, 1, 1),
    "milliseconds-since-1960": datetime.datetime(1960, 1, 1), "days-since-1970": datetime.datetime(1970, 1, 1),
    "seconds-since-1970": datetime.datetime(1970, 1, 1), "milliseconds-since-1970": datetime.datetime(1970, 1, 1),
    "microseconds-since-1970": datetime.datetime(1970, 1, 1), "nanoseconds-since-1970": datetime.datetime(1970, 1, 1),
    "days-since-1840": datetime.datetime(1840, 12, 31), "seconds-since-1582": datetime.datetime(1582, 10, 14),
}


def _count(moment: datetime.datetime, member: str, fraction: bool = False) -> str:
    """``moment`` written as a count of ``member``: whole days (five figures after the point where asked), or whole units."""
    delta = moment - _EPOCHS[member]
    unit = date_counts.TABLE[member].unit
    if unit == date_counts.DAY:
        if fraction:
            return f"{delta.total_seconds() / 86400:.5f}"
        return f"{delta.days}"
    return f"{(delta.days * 86400 + delta.seconds) * (date_counts.SECOND // unit)}"


def _births(n: int, seed: int) -> "list[datetime.datetime]":
    draw = random.Random(seed)
    found: "list[datetime.datetime]" = []
    for _one in range(n):
        day = datetime.date(1928, 1, 1) + datetime.timedelta(days=draw.randrange(78 * 365))
        found += [datetime.datetime.combine(day, datetime.time(draw.randrange(24), draw.randrange(60)))]
    return found


def _day_of(cell: str, reading: grains.Reading) -> "datetime.date | None":
    moment = grains.moment_of(cell, reading)
    if moment is None:
        return None
    return datetime.date(1970, 1, 1) + datetime.timedelta(days=moment // date_counts.DAY)


def _held_profile(forms: "dict[str, int]", distinct: int, grain: "dict[str, object] | None") -> taxonomy.ColumnProfile:
    """A record-number block naming ``forms``, ``distinct`` different values, a grain where given (the producer's side)."""
    details: "dict[str, object]" = {"layout_forms": dict(forms), "n_code_alphabet": 0, "n_all_digits": 0}
    if grain is not None:
        details["time_grain"] = grain
    return taxonomy.ColumnProfile(
        name="dob", position=1, role=taxonomy.ROLE_IDENTIFIER, statistical_type="code",
        quality_state="ok", structural_role="identifier",
        detection_evidence=taxonomy.note(taxonomy.EVIDENCE_HELD_IN_PEOPLE),
        n_present=sum(forms.values()), n_missing=0, missing_by_source={},
        missing_by_class={}, n_missing_blank=0, n_missing_withheld=0,
        details=details, publication_notes=[], remarks=[], n_distinct=distinct,
    )


def _runs(column: taxonomy.ColumnProfile) -> "list[list[int]]":
    years = column.details["made_up_years"] if "made_up_years" in column.details else None
    assert isinstance(years, list), column.details
    return years


@pytest.fixture(scope="module")
def template(tmp_path_factory: pytest.TempPathFactory) -> contract.ColumnBlock:
    """A held column block as the command writes one (births from 1925 on are held whole), to set facts and grains on."""
    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    folder = tmp_path_factory.mktemp("template")
    table = folder / "t.csv"
    first = datetime.date(1925, 1, 1).toordinal()
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        handle.write("person_key,dob,value\n")
        for row in range(600):
            handle.write(f"Q{700000 + row},{datetime.date.fromordinal(first + 37 * row).isoformat()},{row % 7}\n")
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"], small_tables_refused=False) == 0
    column = [one for one in contract.load_profile(f"{folder / 't-profile.json'}").columns if one.name == "dob"][0]
    assert isinstance(column.facts, contract.IdentifierFacts) and column.time_grain is not None
    return column


def _facts(forms: "dict[str, int]", years: "tuple[tuple[int, int], ...] | None",
           exclusions: "dict[str, tuple[str, ...]] | None" = None) -> contract.IdentifierFacts:
    return contract.IdentifierFacts(
        min_length=1, max_length=40, all_whole_numbers=False, n_all_digits=0, n_code_alphabet=0,
        n_distinct_by_occurrences={}, layout_forms=forms, layout_prefixes={}, made_up_years=years,
        layout_exclusions=exclusions or {},
    )


# -- the generated check: every kind, member, form, room state and hold ---------------------------------------------

# The room states: a room; an empty room; a room cut by one year; a two-figure room; none published (a held
# grain whose producer published no room: before the lane its G1 floor fell back to the grain's spans).
ROOM_STATES: "dict[str, tuple[tuple[int, int], ...] | None]" = {
    "room": ((2028, 2031),),
    "empty": (),
    "cut": ((2028, 2029), (2031, 2033)),
    "two-figure": ((28, 31),),
    "none published": None,
}
# The ways a held column records its spans: none (held while its Safe Harbor question is open, or typed an
# identifier: the method's fixed span was its fallback) and the real span its walk published in people.
_REAL = (datetime.datetime(1928, 1, 1), datetime.datetime(2006, 1, 1))


def _real_span() -> "tuple[tuple[str, int, int], ...]":
    first = parsing.days_from_civil(1928, 1, 1) * date_counts.DAY
    last = parsing.days_from_civil(2005, 1, 1) * date_counts.DAY
    return (("year", first, last),)


HOLDS = {"question open or typed": (), "held in people": _real_span()}


def _date_forms() -> "list[tuple[str, str, list[str]]]":
    """(kind, member, made-up cells) of the date and stamp readings and the day-of-year layouts, cells of births."""
    births = _births(50, 3)
    made: "list[tuple[str, str, list[str]]]" = []
    for member, form in (
        ("iso-date", "%Y-%m-%d"), ("month-first-date", "%m/%d/%Y"), ("day-first-date", "%d/%m/%Y"),
        ("layout {DD}-{MON}-{YYYY}", "%d-%b-%Y"), ("layout {DD}-{MON}-{YY}", "%d-%b-%y"),
        ("layout {YYYY}{DDD}", "%Y%j"), ("layout {YYYY}-{DDD}", "%Y-%j"), ("layout {YY}-{DDD}", "%y-%j"),
    ):
        made += [(grains.DATE, member, [one.strftime(form).upper() for one in births])]
    for member, form in (("iso-datetime", "%Y-%m-%d %H:%M:%S"), ("iso-datetime", "%Y-%m-%dT%H:%M:%S")):
        made += [(grains.STAMP, member, [one.strftime(form) for one in births])]
    return made


def _counted_forms() -> "list[tuple[str, str, list[str]]]":
    births = _births(50, 5)
    made: "list[tuple[str, str, list[str]]]" = []
    for member in date_counts.MEMBERS:
        made += [(grains.COUNTED, member, [_count(one, member) for one in births])]
        if date_counts.TABLE[member].unit == date_counts.DAY and not date_counts.TABLE[member].contacts:
            made += [(grains.COUNTED, member, [_count(one, member, True) for one in births])]
    return made


def _room_years(years: "tuple[tuple[int, int], ...] | None", reading: grains.Reading) -> "set[int]":
    found: "set[int]" = set()
    for first, last in years or ():
        for year in range(first, last + 1):
            found.add(year)
    if parsing.is_layout_name(reading.member) and parsing.layout_two_figure_year(reading.member) > 0:
        return {2000 + year for year in found if year <= 99}
    return {year for year in found if year > 99}


def test_the_class_is_closed_over_every_kind_member_form_room_and_hold(template: contract.ColumnBlock) -> None:
    """A3, the generated check for dates and stamps (LANE I4r RULINGS 1 (4)): every date reading, day-of-year layout
    and stamp the room serves, by the room states (a room; an empty room; a room cut by one year; a two-figure room;
    none published), by the spans a held grain records (none, the fallback to the fixed span; the real span
    published in people): every made-up cell the G1 floor writes reads back, in its layout, on a day of a year the
    room publishes, or, where the room draws nothing, is written BLANK -- never the walk's value, which is text that
    is no date (`9978557`, day 557 of a year), nor a day of the grain's spans (lane ID-ROOM3's repair 1, LANE
    ID-ROOM3 RULINGS 6 (3)). The counted readings are the next case's, on the producer's own facts. Mutants: X0,
    the fallback to the grain's spans restored (the base); X4, the member-layout call of the G1 floor removed; the
    blank of `_no_date_cells` dropped (the walk's values written).
    """
    checked = 0
    for kind, member, cells in _date_forms():
        reading = grains.Reading(kind, member)
        forms: "dict[str, int]" = {}
        for cell in cells:
            layout = parsing.layout_form(cell, parsing.LAYOUT_PLAIN)
            forms[layout] = forms.get(layout, 0) + 1
        for state_name, years in ROOM_STATES.items():
            for hold_name, spans in HOLDS.items():
                finest = grains.SECOND if kind != grains.DATE else grains.DAY
                grain = grains.Grain(grains.HELD, reading, len(cells), spans, finest, 0)
                facts = _facts(forms, years)
                # ...and the census withheld whole, as A2 reads it, for the dates.
                if kind == grains.DATE and state_name == "room" and hold_name == "held in people":
                    facts = _facts({contract.WITHHELD: len(cells)}, years)
                column = dataclasses.replace(template, facts=facts, time_grain=grain, n_distinct=len(set(cells)),
                                             n_present=len(cells))
                found, _unwritten = generation._inside_the_grain(column, cells, [7 + 13 * k for k in range(len(cells))])
                published = _room_years(years, reading)
                drew = generation._room_spans(generation._room_years(facts) or ([], []), reading)
                written = 0
                for before, after in zip(cells, found):
                    checked += 1
                    if not drew:
                        # ...no room: blank, the base's blank of a zone word made the rule of every date and stamp.
                        assert after == "", (kind, member, state_name, hold_name, before, after)
                        continue
                    if after == before:
                        assert facts.layout_forms.get(contract.WITHHELD), (kind, member, state_name, hold_name, after)
                        continue
                    day = _day_of(after, reading)
                    assert day is not None and day.year in published, (kind, member, state_name, hold_name, after)
                    written += 1
                if drew:
                    assert written > 0, (kind, member, state_name, hold_name, found[:3])
    assert checked > 4_000, checked


# -- the generated check for counts, on the producer's own facts -----------------------------------------------------

# The counted readings: every member of `date_counts.MEMBERS`, days written whole and, for a spreadsheet's or a
# day count's member that writes no contact number, with a time after the point.
_COUNTED_READINGS = tuple(
    (member, fraction) for member in date_counts.MEMBERS
    for fraction in ((False, True) if date_counts.TABLE[member].unit == date_counts.DAY
                     and not date_counts.TABLE[member].contacts else (False,))
)


def _producer_block(cells: "list[str]", grain: "dict[str, object] | None") -> taxonomy.ColumnProfile:
    """A held column of these real cells as the producer publishes it: census, exclusions with the spill, room."""
    forms: "dict[str, int]" = {}
    for cell in cells:
        if parsing.figures_in(cell) or cell.strip():
            forms[parsing.layout_form(cell, parsing.LAYOUT_PLAIN)] = forms.get(
                parsing.layout_form(cell, parsing.LAYOUT_PLAIN), 0) + 1
    column = _held_profile(forms, len(set(cells)), grain)
    lengths = [len(cell) for cell in cells if cell.strip()]
    column = dataclasses.replace(column, details={**column.details, "layout_prefixes": {}, "layout_exclusions": {},
                                                  "max_length": max(lengths), "min_length": min(lengths)})
    column = taxonomy.with_layout_exclusions(column, cells, 11)
    if grain is not None:
        return taxonomy.with_made_up_years(column, cells)
    return taxonomy.with_made_up_counts(column, cells)


def _facts_of(column: taxonomy.ColumnProfile, years: "tuple[tuple[int, int], ...] | None") -> contract.IdentifierFacts:
    exclusions = column.details["layout_exclusions"] if "layout_exclusions" in column.details else {}
    assert isinstance(exclusions, dict) and parsing.EXCLUSION_SPILL in exclusions, column.details
    forms = column.details["layout_forms"]
    assert isinstance(forms, dict)
    return _facts(dict(forms), years, {key: (value,) if isinstance(value, str) else tuple(value)
                                       for key, value in exclusions.items()})


def _made_up_inputs(real: "list[str]", draw: random.Random) -> "list[str]":
    """The walk's values a held column of counts may hand its writer: the real cells, real cells a count away and a
    figure away, values of the real cells' widths and signs, and the stray words."""
    found = list(real[:200])
    for cell in real[:40]:
        sign = "-" if cell[:1] == "-" else ""
        body = cell[len(sign):]
        whole, mark, after = body.partition(".")
        found += [f"{sign}{int(whole) + 1}{mark}{after}", f"{sign}{max(int(whole) - 1, 0)}{mark}{after}"]
        place = draw.randrange(len(whole))
        figure = f"{(int(whole[place]) + 1 + draw.randrange(8)) % 10}" if place else whole[place]
        found += [f"{sign}{whole[:place]}{figure}{whole[place + 1:]}{mark}{after}"]
        found += [f"{sign}{draw.randrange(10 ** (len(whole) - 1), 10 ** len(whole))}{mark}{after}"]
        # ...and the real count written with noughts before its first figure, as the walk spells a value off the real
        # where no real cell opens with a nought (lane ID-ROOM3's repair 2).
        found += [f"{sign}000{whole}{mark}{after}"]
    return found + ["UNK", "UNKNOWN", "N.D."]


def _real_days_in(cells: "list[str]", member: str) -> "set[int]":
    days: "set[int]" = set()
    for cell in cells:
        moment = grains.moment_of(cell, grains.Reading(grains.COUNTED, member))
        if moment is not None:
            days.add(moment // date_counts.DAY)
    return days


def _days_named(cell: str, member: str) -> "set[int]":
    """The days a count names in ``member``, read with the point and with the comma, as a reader of numbers reads it:
    noughts opening its whole part set aside (`000009985,039` is 9,985; lane ID-ROOM3's repair 2)."""
    sign = "-" if cell[:1] == "-" else ""
    body = cell[len(sign):]
    while len(body) > 1 and body[0] == "0" and "0" <= body[1] <= "9":
        body = body[1:]
    days: "set[int]" = set()
    for mark in date_counts.MARKS:
        moment = grains.moment_of(sign + body, grains.Reading(grains.COUNTED, member, mark))
        if moment is not None:
            days.add(moment // date_counts.DAY)
    return days


def test_a_held_count_names_no_real_day_on_the_producer_s_own_facts(template: contract.ColumnBlock) -> None:
    """The class closed for counts (lane ID-ROOM3's repair 1; LANE ID-ROOM3 RULINGS 5 (4) and 6 (4)), generated over
    every counting system (days whole and with a time), the room states (the producer's room; a room it did not find;
    an empty room; none published) and the holds (a held counted grain recording the real span; a held count with no grain declared in
    its member; one declared in none, read as unbounded or not), on the PRODUCER'S OWN FACTS -- the census, the
    exclusions with the spill and the room `with_layout_exclusions`, `with_made_up_years` and `with_made_up_counts`
    publish of 400 real births -- fed the real cells, real cells a count and a figure away, values at the real
    widths and stray words: EVERY cell written, unchanged or not, names in its member (point or comma) no day inside
    the span the real days fill there -- so no real day either -- or is the stray word as written. And the margins: a real count at the top of its width and one
    just below a width's nine hundreds beside made-up values a second past them; and births of one calendar year
    at an epoch, read by the span-and-density test since repair 2. Mutants: X5, the walk's test removed;
    Y1, the floor's last walk test removed; Y7 and Y8, a day's margin of the spill and of the nine hundreds dropped;
    Y10, the walk test of a counted grain with no room removed; the stand-in of a stray word in the floor dropped.
    """
    draw = random.Random(41)
    checked = 0
    for member, fraction in _COUNTED_READINGS:
        births = _births(400, 43)
        real = [_count(one, member, fraction) for one in births]
        real_days = _real_days_in(real, member)
        first_real, last_real = min(real_days), max(real_days)
        inputs = _made_up_inputs(real, draw)
        reading = grains.Reading(grains.COUNTED, member)
        grain_record = {"kind": "counted", "rung": "held", "reading": member,
                        "finest": "second" if fraction or date_counts.TABLE[member].unit < date_counts.DAY else "day",
                        "mark": ".", "spans": []}
        grained = _producer_block(real * 3, grain_record)
        loose = _producer_block(real * 3, None)
        for state in ("producer", "forced", "empty", "none"):
            for hold in ("grain", "declared", "undeclared", "unbounded"):
                block = grained if hold == "grain" else loose
                runs = block.details["made_up_years"] if "made_up_years" in block.details else []
                assert isinstance(runs, list)
                # ...`forced`, a room the producer did not find (a member writing no count of it, days from 1840,
                # leaves the floor's cells to its last walk test).
                years: "tuple[tuple[int, int], ...] | None" = (
                    tuple((int(run[0]), int(run[1])) for run in runs) if state == "producer"
                    else ((2028, 2033),) if state == "forced" else () if state == "empty" else None)
                if hold != "grain" and years is None:
                    continue
                facts = _facts_of(block, years)
                if hold == "grain":
                    grain = grains.Grain(grains.HELD, reading, len(inputs), _real_span(), grains.SECOND, 0)
                    column = dataclasses.replace(template, facts=facts, time_grain=grain, n_present=len(real) * 3,
                                                 n_distinct=len(set(real)))
                    found, _unwritten = generation._inside_the_grain(
                        column, inputs, [draw.getrandbits(64) for _one in inputs])
                else:
                    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=len(real) * 3,
                                                 n_distinct=len(set(real)))
                    found = generation._counts_off_the_real(
                        column, facts, inputs, (member,) if hold == "declared" else (), (), hold == "unbounded")
                for before, after in zip(inputs, found):
                    checked += 1
                    if not parsing.figures_in(before):
                        assert after == before, (member, state, hold, before, after)
                        continue
                    # ...EVERY cell, unchanged or not, read in its member with either mark: no day of it lies inside
                    # the span the real days fill (LANE ID-ROOM3 RULINGS 6 (4)), so none is a real day either.
                    named = _days_named(after, member)
                    assert not [day for day in named if first_real <= day <= last_real], (
                        member, fraction, state, hold, before, after)
                    assert not named & real_days, (member, fraction, state, hold, before, after)
    # ...THE MARGINS: a real count at the top of its width (`9999999999` seconds, 2286-11-20) and one just below a
    # width's nine hundreds (`8999999999`), beside births of nine figures (so the longest real cell is the edge's and
    # the spill one figure past it): a made-up count a second past either names that same day.
    member = "seconds-since-1970"
    real = _seconds_of(_young_births(400, 47))
    for edge, made in (("9999999999", "10000000000"), ("8999999999", "9000000000")):
        cells = real + [edge] * 12
        block = _producer_block(cells * 2, None)
        facts = _facts_of(block, ((2028, 2028),))
        column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=len(cells) * 2, n_distinct=413)
        found = generation._counts_off_the_real(column, facts, [made], (), ())
        assert not _days_named(found[0], member) & _real_days_in(cells, member), (edge, made, found)
        checked += 1
    # ...AND BIRTHS OF ONE CALENDAR YEAR AT AN EPOCH (repair 2, LANE ID-ROOM3 RULINGS 7 (2): 4,940 to 5,620 twin cells
    # on 96 to 100 real birth days with nobody answering before): 1970 as seconds and as milliseconds from 1970, 1960
    # as SAS datetimes, the common year 1999 as seconds; the span-and-density test reads each in its system, and the
    # walk's test of the column held with no grain, declared in none, on the producer's own facts, writes every
    # count outside the span the cohort's days fill, bounded or not.
    for member, year, unit in (("seconds-since-1970", 1970, 1), ("milliseconds-since-1970", 1970, 1000),
                               ("seconds-since-1960", 1960, 1), ("seconds-since-1970", 1999, 1)):
        real = _seconds_of(_cohort(year, 400, 119 + year), unit, _EPOCHS[member])
        real_days = _real_days_in(real, member)
        first_real, last_real = min(real_days), max(real_days)
        assert member in taxonomy.counts_may_be_dates(_held_counts(real * 3), real * 3), (member, year)
        loose = _producer_block(real * 3, None)
        runs = loose.details["made_up_years"]
        # ...the room the producer publishes, empty where the cross rule finds a real count naming a year of it
        # (a millisecond of January 1970 read as seconds names 2028).
        assert isinstance(runs, list), (member, year)
        facts = _facts_of(loose, tuple((int(run[0]), int(run[1])) for run in runs))
        column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=len(real) * 3,
                                     n_distinct=len(set(real)))
        inputs = _made_up_inputs(real, draw)
        for unbounded in (False, True):
            found = generation._counts_off_the_real(column, facts, inputs, (), (), unbounded)
            for before, after in zip(inputs, found):
                checked += 1
                if not parsing.figures_in(before):
                    assert after == before, (member, year, before, after)
                    continue
                named = _days_named(after, member)
                assert not [day for day in named if first_real <= day <= last_real], (member, year, before, after)
    assert checked > 10_000, checked


# -- A1: the counted room, published by the producer -----------------------------------------------------------------


def _readings(core: str, member: str) -> "set[int]":
    """Every four-figure year a cell names in its member and in each of the twelve counting systems (the cross rule)."""
    years = set(taxonomy.counted_years(core))
    written = date_counts.counted(member, core, date_counts.POINT)
    if written is not None:
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(member, numerator, denominator, date_counts.NANOSECOND)
        if moment is not None:
            years.add(parsing.civil_from_days(moment // date_counts.DAY)[0])
    return years


@pytest.mark.parametrize("member", date_counts.MEMBERS)
def test_the_counted_room_holds_no_year_a_real_count_names(member: str) -> None:
    """A1's producer, generated over every counting system: 1,000 births of 1928 to 2005 written as counts of the
    member (days whole) under a held counted grain publish a room no year of which any real cell names -- in its
    member or in each of the twelve counting systems -- and a room where none of those readings reaches 2028
    (seconds, milliseconds and finer); a member whose figures after the point are a contact number publishes none. Mutants: X2, the counted test of `with_made_up_years` removed (a held count
    publishes `[]`); X3, the cross rule dropped.
    """
    cells = [_count(one, member) for one in _births(1000, 11)]
    grain = {"kind": "counted", "rung": "held", "reading": member, "finest": "second", "mark": ".", "spans": []}
    forms: "dict[str, int]" = {}
    for cell in cells:
        forms[parsing.layout_form(cell, parsing.LAYOUT_PLAIN)] = forms.get(parsing.layout_form(cell, parsing.LAYOUT_PLAIN), 0) + 1
    held = taxonomy.with_made_up_years(_held_profile(forms, len(set(cells)), grain), cells)
    runs = _runs(held)
    named: "set[int]" = set()
    for cell in cells:
        named |= _readings(cell, member)
    room = {year for first, last in runs for year in range(first, last + 1)}
    assert not room & named, (member, sorted(room & named)[:5])
    if date_counts.TABLE[member].contacts:
        assert runs == []
    elif not {year for year in named if year >= taxonomy.MADE_UP_FIRST_YEAR and year < taxonomy.MADE_UP_FIRST_YEAR + 3}:
        assert runs and runs[0][0] == taxonomy.MADE_UP_FIRST_YEAR, (member, runs)


def test_the_cross_rule_reads_a_count_in_every_counting_system() -> None:
    """X3's case, batch 4q's cross rule: day counts `24837` to `24857` declared Excel serials (days of 1968) read as
    days from 1960 name days of 2028, so a counted column of them publishes no room from 2028; read in their member
    alone 2028 was free. And a count is read as a count, not as a text date: seconds of the 1970s whose figures
    open with `28` (`283996800`) leave the room standing. Mutant X3, the cross rule dropped."""
    cells = [f"{24837 + k}" for k in range(21)]
    grain = {"kind": "counted", "rung": "held", "reading": "excel-1900", "finest": "day", "mark": ".", "spans": []}
    held = taxonomy.with_made_up_years(_held_profile({"%%%%%": 21}, 1, grain), cells)
    assert _runs(held) == [], _runs(held)
    seconds = [f"{283996800 + 86400 * k}" for k in range(21)]
    grain = {**grain, "reading": "seconds-since-1970", "finest": "second"}
    held = taxonomy.with_made_up_years(_held_profile({"%%%%%%%%%": 21}, 21, grain), seconds)
    assert _runs(held) == [[2028, 2028]], _runs(held)


def test_a_held_count_is_written_in_the_room_at_its_own_finest_unit(template: contract.ColumnBlock) -> None:
    """A1's writer: a held serial with five figures after the point is written in the room with its time of day
    (before, every made-up moment was midnight, `42494.00000`), and a held count of seconds steps inside the day;
    each reads back in its member in a published year. Mutant X6, the fraction dropped (the day's step)."""
    for member, fraction in (("excel-1900", True), ("seconds-since-1970", False)):
        cells = [_count(one, member, fraction) for one in _births(60, 17)]
        reading = grains.Reading(grains.COUNTED, member)
        grain = grains.Grain(grains.HELD, reading, len(cells), (), grains.SECOND, 0)
        forms = {parsing.layout_form(cells[0], parsing.LAYOUT_PLAIN): len(cells)}
        column = dataclasses.replace(template, facts=_facts(forms, ((2028, 2028),)), time_grain=grain,
                                     n_distinct=len(set(cells)), n_present=len(cells))
        words = [random.Random(31 + k).getrandbits(64) for k in range(len(cells))]
        found, _unwritten = generation._inside_the_grain(column, cells, words)
        moments = [grains.moment_of(cell, reading) for cell in found]
        assert all(moment is not None for moment in moments), found[:3]
        assert all(_day_of(cell, reading).year == 2028 for cell in found), found[:3]  # type: ignore[union-attr]
        clocks = {moment % date_counts.DAY for moment in moments if moment is not None}
        assert len(clocks) > len(found) // 2, (member, found[:4])


# -- A1b: a held count with no grain, its walk kept off every real day -----------------------------------------------


def test_a_walk_value_stands_only_off_every_real_day(template: contract.ColumnBlock) -> None:
    """A1b (ii), the walk's test: a held column of seconds with no grain whose room is published (the Safe Harbor
    question's arm about dates holds it) keeps a made-up value only where its published facts put it off every
    real day: one past the spill's figures, one opening with a nine where every named layout's exclusion opens
    with one, one naming no date; a value inside the span real counts fill (`-797741927`, 1944) is written as the
    spill, its sign kept. A column of day numbers written from nine hundreds no real count reaches keeps every
    byte (the zoo's held day numbers); a block publishing no spill keeps the walk's values. Mutants X5, the walk's
    test removed; Y11, the values of a block with no spill written past it."""
    forms = {"-%%%%%%%%%": 60, "-%%%%%%%%%%": 30, "%%%%%%%%%%": 30}
    exclusions = {"-%%%%%%%%%": ("-%%%%%%9%7",), "-%%%%%%%%%%": ("-9%%%%%%%%%",),
                  "%%%%%%%%%%": ("9%%%%%%%%%",), parsing.EXCLUSION_SPILL: ("%%%%%%%%%%%%",)}
    facts = _facts(forms, ((2028, 2028),), exclusions)
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=120, n_distinct=120)
    cells = ["-797741927", "-9098933081", "474707388860", "-123456907", "9512345678"]
    found = generation._counts_off_the_real(column, facts, cells, (), ())
    assert found[1] == cells[1] and found[2] == cells[2] and found[4] == cells[4], found
    assert found[0].startswith("-9000000000") and found[3].startswith("-9000000000"), found
    assert len(set(found)) == len(found)
    # ...and a column whose description reads cells as blank (its real cells unbounded by its published facts):
    # only a value naming no date or a published year stands; any other is written with a plus, a number no
    # counting system's grammar reads.
    # (`474707388860`, no date read as seconds, is a day of 1985 read as milliseconds: it goes too.)
    found = generation._counts_off_the_real(column, facts, cells, (), (), True)
    assert all(cell.startswith("+") and not [member for member in date_counts.MEMBERS
                                             if date_counts.counted(member, cell, ".") is not None]
               for cell in found), found
    assert len(set(found)) == len(found)
    days = ["95941", "92104.69", "96194", "98210.07", "97427.62"]
    forms = {"%%%%%": 700, "%%%%%.%": 70, "%%%%%.%%": 1230}
    exclusions = {"%%%%%": ("9%%%%",), "%%%%%.%": ("9%%%%.%",), "%%%%%.%%": ("9%%%%.%%",),
                  parsing.EXCLUSION_SPILL: ("%%%%%%%%%",)}
    facts = _facts(forms, ((2028, 2038),), exclusions)
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=2000, n_distinct=2000)
    assert generation._counts_off_the_real(column, facts, days, ("days-since-1840",), ()) == days
    assert generation._counts_off_the_real(column, facts, days, (), ()) == days
    # ...and a block publishing no spill (a description written before the spill was published) gives the test no
    # bound to write past: its values stand as the walk wrote them (skeptic 1's Y11).
    bare = _facts(forms, ((2028, 2038),), {})
    assert generation._counts_off_the_real(dataclasses.replace(column, facts=bare), bare, cells, (), ()) == cells


def test_the_oracle_writes_a_held_count_s_walk_as_the_product_does(template: contract.ColumnBlock) -> None:
    """Method G9.6c's counts and the oracle (tools/reference/make_generation_reference_vectors.py,
    `counts_off_the_real`, from the rule statement) write the same cells, generated over signs, widths, fractions
    after a point or a comma, published rooms, exclusions, declared members, stray words beside the counts and short
    counts beside a wider layout (A-P4-59; lane ID-ROOM3's repair 1); and since repair 2 a stray layout the count
    grammar does not read beside the counts, under the cap and past it, and five figures after a point, which the
    unbounded spill keeps; and since the suite repair a census withheld whole beside a spill of sixteen to
    twenty-two characters, values of eight to ten whole figures with one to twelve after the point: the plus spill
    of a fraction the bounded spill loses to a reader of numbers, written in some of those cases (mutant: the plus
    spill for a fraction removed)."""
    import make_generation_reference_vectors as oracle

    draw = random.Random(23)
    for case in range(240):
        width = draw.choice((6, 7, 9, 10, 12, 13))
        signed = draw.random() < 0.5
        mark = draw.choice(("", "", ",", "."))
        comma = mark == ","
        after = {"": "", ",": ",%%%", ".": ".%%%%%"}[mark]
        layout = ("-" if signed else "") + "%" * width + after
        nine = draw.random() < 0.5
        forms = {layout: 400}
        if draw.random() < 0.3:
            forms[contract.WITHHELD] = 10
        if draw.random() < 0.3:
            forms["@@@"] = 20
        stray = draw.choice((0, 0, 20, 200))
        if stray:
            forms["%%%%-%%-%%"] = stray
        exclusions = {layout: (("-" if signed else "") + ("9" if nine else "%") + "%" * (width - 1) + after,),
                      parsing.EXCLUSION_SPILL: ("%" * (width + 2),)}
        years = ((2028, 2028 + draw.randrange(3)),) if draw.random() < 0.7 else ()
        member = draw.choice(("",) + date_counts.MEMBERS)
        cells = []
        for _one in range(30):
            figures = f"{draw.choice('9' if nine else '123456789')}{draw.randrange(10 ** (width - 1)):0{width - 1}d}"
            cells += [("-" if signed else "") + figures + (f",{draw.randrange(1000):03d}" if comma else "")
                      + (f".{draw.randrange(1, 100000):05d}" if mark == "." else "")]
        cells += ["UNK", f"{draw.randrange(1, 999)}"] + (["1985-03-04"] if stray else [])
        facts = _facts(forms, years, exclusions)
        blank = draw.choice((0, 0, 25))
        # ...as the identifier branch asks it: only of a census of counts (`_counts_alone`, the stray layout's cap).
        product = generation._counts_off_the_real(
            dataclasses.replace(template, facts=facts, time_grain=None, n_present=410), facts, cells,
            (member,) if member else (), (), blank > 0) if generation._counts_alone(facts, 410) else cells
        block = {"role": "identifier", "made_up_years": [list(run) for run in years], "layout_forms": forms,
                 "layout_exclusions": {key: list(value) for key, value in exclusions.items()}, "n_present": 410,
                 "n_missing_blank": blank}
        assert oracle.counts_off_the_real(block, cells, member) == product, (case, member, cells[:3])
    # ...AND THE SUITE REPAIR: a census withheld whole, a long spill, long and short fractions.
    plus = 0
    for case in range(120):
        places = draw.randrange(1, 13)
        forms = {} if draw.random() < 0.5 else {contract.WITHHELD: 410}
        exclusions = {parsing.EXCLUSION_SPILL: ("%" * draw.randrange(16, 23),)}
        member = draw.choice(("",) + date_counts.MEMBERS)
        cells = [("-" if draw.random() < 0.3 else "") + f"{draw.randrange(10**7, 10**10)}.{draw.randrange(10**places):0{places}d}"
                 for _one in range(20)] + [f"{draw.randrange(10**7, 10**10)}", "UNK"]
        facts = _facts(forms, ((2028, 2031),), exclusions)
        blank = draw.choice((0, 0, 25))
        product = generation._counts_off_the_real(
            dataclasses.replace(template, facts=facts, time_grain=None, n_present=410), facts, cells,
            (member,) if member else (), (), blank > 0) if generation._counts_alone(facts, 410) else cells
        block = {"role": "identifier", "made_up_years": [[2028, 2031]], "layout_forms": forms,
                 "layout_exclusions": {key: list(value) for key, value in exclusions.items()}, "n_present": 410,
                 "n_missing_blank": blank}
        assert oracle.counts_off_the_real(block, cells, member) == product, (case, member, cells[:3])
        plus += 0 if blank else sum(1 for cell in product if cell[:1] == "+")
    assert plus > 0, plus


# -- A1b's arms: the span-and-density test, a stray word, the person's word ---------------------------------------


def _held_counts(cells: "list[str]", evidence: str = taxonomy.EVIDENCE_HELD_IN_PEOPLE) -> taxonomy.ColumnProfile:
    """A record-number block of these cells as the producer holds it, before `_held_counts_read` (census alone)."""
    forms: "dict[str, int]" = {}
    for cell in cells:
        if cell.strip():
            forms[parsing.layout_form(cell, parsing.LAYOUT_PLAIN)] = forms.get(
                parsing.layout_form(cell, parsing.LAYOUT_PLAIN), 0) + 1
    column = _held_profile(forms, len(set(cells)), None)
    return dataclasses.replace(column, detection_evidence=taxonomy.note(evidence))


def _seconds_of(births: "list[datetime.datetime]", unit: int = 1, epoch: "datetime.datetime | None" = None) -> "list[str]":
    origin = epoch or datetime.datetime(1970, 1, 1)
    return [f"{int((one - origin).total_seconds()) * unit}" for one in births]


def _young_births(n: int, seed: int) -> "list[datetime.datetime]":
    """Births of 1973-04 to 2001-08: every count of seconds since 1970 nine figures and positive (skeptic 1's Z)."""
    draw = random.Random(seed)
    first = datetime.datetime(1973, 4, 1)
    return [first + datetime.timedelta(seconds=draw.randrange(int((datetime.datetime(2001, 8, 31) - first)
                                                                  .total_seconds()))) for _one in range(n)]


def _record_number_shapes() -> "dict[str, list[str]]":
    """Ordinary record-number columns no question about dates concerns (skeptic 1's item 2, the statistics check's
    item 2): a seven-figure member number on each of a patient's rows, case numbers of twelve to eighteen figures,
    claim numbers of sixteen, encounter keys numbered one after another from 700000000."""
    draw = random.Random(53)
    return {
        "member number": [f"{draw.randrange(1_000_000, 9_999_999)}" for _one in range(1000)] * 20,
        "case numbers": [f"{draw.randrange(10 ** (width - 1), 10 ** width)}" for width in (12, 13, 14, 16, 17, 18)
                         for _one in range(166)] * 20,
        "claim numbers": [f"{draw.randrange(10 ** 15, 10 ** 16)}" for _one in range(1000)] * 20,
        "encounter keys": [f"{700_000_000 + one}" for one in range(20_000)],
    }


def _cohort(year: int, n: int, seed: int) -> "list[datetime.datetime]":
    """``n`` births of one calendar year at a random second of it."""
    draw = random.Random(seed)
    first = datetime.datetime(year, 1, 1)
    seconds = int((datetime.datetime(year + 1, 1, 1) - first).total_seconds())
    return [first + datetime.timedelta(seconds=draw.randrange(seconds)) for _one in range(n)]


def test_the_span_and_density_test_reads_dates_and_never_record_numbers() -> None:
    """The span-and-density test (LANE ID-ROOM3 RULINGS 4 (2), 5 (1) and (2), 7 (2); `taxonomy.counts_may_be_dates`):
    births of 1973 to 2001 written as nine-figure seconds, births of 1940 to 2005 as milliseconds, SAS datetimes and
    seconds with a fraction, visits of 2016 on as seconds (twenty thousand different values over six years), births
    beside ten counts past 2050 (one in a hundred, as Q3's rule A excepts strays), and since repair 2 BIRTHS OF ONE
    CALENDAR YEAR -- 1970 as seconds and milliseconds from 1970, 1960 as SAS datetimes, the common years 1971, 1999
    and 2001 (4,940 to 5,620 twin cells on 96 to 100 real birth days with nobody answering before: Q3's rule B and a
    year's cap no common year meets kept them unread) -- read as dates in their systems; the seven-figure member
    number (within a year of 1970 read as seconds, past 9999 as days), case numbers of mixed widths (piled in the
    first year read as nanoseconds), claim numbers of sixteen figures (past 2050 read as microseconds), encounter keys
    numbered one after another (twenty thousand on two days read as seconds), codes of seven figures and compact
    dates beside months (a few different days of 1970 read as seconds) read in none. Mutants: the test always reading
    dates; never; its spread rule dropped; the cap at a year again (the common years unread); rule B whole again (the
    epoch's cohorts unread); the pile at the epoch dropped (case numbers read); the pile's different days dropped
    (codes read); no stray let past the band (V3); the cap a hundred times (the visits unread, V9)."""
    young = _young_births(1000, 59)
    old = _births(1000, 61)
    draw = random.Random(63)
    visits = [datetime.datetime(2016, 1, 1) + datetime.timedelta(seconds=draw.randrange(6 * 365 * 86400))
              for _one in range(20_000)]
    beyond = [datetime.datetime(2100, 1, 1) + datetime.timedelta(days=draw.randrange(3650)) for _one in range(10)]
    dated = {
        "young seconds": _seconds_of(young) * 20,
        "milliseconds": _seconds_of(old, 1000) * 20,
        "SAS datetimes": _seconds_of(old, 1, datetime.datetime(1960, 1, 1)) * 20,
        "seconds with a fraction": [f"{cell}.{k % 1000:03d}" for k, cell in enumerate(_seconds_of(old))] * 20,
        "visits": _seconds_of(visits),
        "births beside ten counts past 2050": _seconds_of(old[:990] + beyond) * 20,
        "1970 as seconds": _seconds_of(_cohort(1970, 1000, 65)) * 20,
        "1970 as milliseconds": _seconds_of(_cohort(1970, 1000, 67), 1000) * 20,
        "1960 as SAS datetimes": _seconds_of(_cohort(1960, 1000, 69), 1, datetime.datetime(1960, 1, 1)) * 20,
        "1971 as seconds": _seconds_of(_cohort(1971, 1000, 71)) * 20,
        "1999 as seconds": _seconds_of(_cohort(1999, 1000, 73)) * 20,
        "2001 as seconds": _seconds_of(_cohort(2001, 1000, 75)) * 20,
    }
    for name, cells in dated.items():
        assert taxonomy.counts_may_be_dates(_held_counts(cells), cells), name
    shapes = _record_number_shapes()
    shapes["codes of seven figures"] = ["197361", "866924", "617312", "860975", "310965", "1049621", "2797130",
                                        "704641", "5076214"] * 2000
    shapes["compact dates beside months"] = [f"{one.year}{one.month:02d}{one.day:02d}" if k % 7 else
                                             f"{one.year}{one.month:02d}" for k, one in enumerate(old)] * 20
    for name, cells in shapes.items():
        assert taxonomy.counts_may_be_dates(_held_counts(cells), cells) == (), name


def test_a_held_count_takes_the_room_only_where_its_counts_may_be_dates() -> None:
    """A1b's arms, each way (skeptic 1's items 1 and 2, the statistics check's item 2): a held column of counts with
    no grain publishes the room its counts would take -- held in people, held while an open question offers
    `identifier` (the measurement, code or identifier question and Q3: births of 1973 to 2001 as nine-figure seconds
    with nobody answering named 1,620 twin cells on 81 real birth days before), or held by the Safe Harbor question's
    arms about dates -- only where its counts may be dates; an ordinary record-number column so held keeps its block
    as it came (a member number held in people had a room and 4,240 of 20,000 twin cells written wider); and a
    column the person said holds codes keeps it too. Mutants: Y4, the arm of a column held in people removed; Y6,
    the Safe Harbor arms removed; the open question's arm removed; the person's word on codes ignored."""
    from synthtwin import profile

    settings = taxonomy.Settings()
    young = _seconds_of(_young_births(1000, 67)) * 20
    milliseconds = _seconds_of(_births(1000, 71), 1000) * 20
    for evidence, cells, held_for_dates in (
        (taxonomy.EVIDENCE_HELD_IN_PEOPLE, milliseconds, False),
        (taxonomy.EVIDENCE_HELD_IN_ROWS, milliseconds, False),
        (taxonomy.EVIDENCE_UNANSWERED_IDENTITY, young, False),
        (taxonomy.EVIDENCE_DECLARED_IDENTIFIER, milliseconds, True),
    ):
        held = profile._held_counts_read(_held_counts(cells, evidence), cells, settings, "c", held_for_dates)
        assert "made_up_years" in held.details, (evidence, held_for_dates)
        kept = profile._held_counts_read(_held_counts(cells, evidence), cells, settings, "c", held_for_dates, True)
        assert "made_up_years" not in kept.details, evidence
    assert "made_up_years" not in profile._held_counts_read(
        _held_counts(milliseconds, taxonomy.EVIDENCE_DECLARED_IDENTIFIER), milliseconds, settings, "c", False).details
    for name, cells in _record_number_shapes().items():
        for evidence in (taxonomy.EVIDENCE_HELD_IN_PEOPLE, taxonomy.EVIDENCE_UNANSWERED_IDENTITY):
            column = _held_counts(cells, evidence)
            assert profile._held_counts_read(column, cells, settings, "c", True) == column, (name, evidence)


def test_a_declared_count_takes_its_member_s_counted_grain_and_a_stray_word_never_defeats_it() -> None:
    """A1b (i) and the statistics check's item 1 (LANE ID-ROOM3 RULINGS 6 (1)): a held column of counts declared in
    a member takes that member's counted grain, so the one writer of counted dates writes it in the room -- and so
    it does beside one patient's `UNK`, `UNKNOWN` or a placeholder of nines (before, the word took the column out of
    every test: 660 twin cells on real birth days with the counts declared, 540 with nobody answering); a word in
    half the cells is set aside too, and the counts left still judged. Mutants: Y5, the declared counted grain
    removed; a stray word not set aside."""
    from synthtwin import profile

    member = "seconds-since-1970"
    settings = dataclasses.replace(taxonomy.Settings(), forced_date_counts=(("c", member),))
    births = _seconds_of(_births(1000, 73))
    # ...and since repair 2 a stray figure the count grammar does not read: one patient's twenty rows written as ISO
    # dates, eleven zero fills (the verify of repair 1, item 1: 380 and 600 twin cells on real birth days before).
    for stray, share in (("", 0), ("UNK", 20), ("UNKNOWN", 60), ("99999999", 20), ("N/A", 10_000),
                         ("1985-03-04", 20), ("00000000", 11)):
        cells = births * 20
        if share:
            cells = [stray] * share + cells[share:]
        column = _held_counts(cells)
        assert taxonomy.held_counts_widest(column, cells) == 10, (stray, share)
        held = profile._held_counts_read(column, cells, settings, "c", False)
        grain = held.details["time_grain"] if "time_grain" in held.details else None
        assert isinstance(grain, dict) and grain["kind"] == grains.COUNTED and grain["reading"] == member, stray
        assert taxonomy.counts_may_be_dates(column, cells), (stray, share)
    # ...and a count declared with a decimal comma is read with it (V4: the point alone read none of its counts).
    comma = [f"{cell},{k % 1000:03d}" for k, cell in enumerate(births)] * 20
    held = profile._held_counts_read(_held_counts(comma), comma, settings, "c", False)
    grain = held.details["time_grain"] if "time_grain" in held.details else None
    assert isinstance(grain, dict) and grain["kind"] == grains.COUNTED and grain["mark"] == date_counts.COMMA, grain
    # ...and with no declaration, beside the word, the room its counts would take.
    cells = ["UNK"] * 20 + births * 20
    assert "made_up_years" in profile._held_counts_read(_held_counts(cells), cells, taxonomy.Settings(), "c", False).details


# The stray words and their shares (the statistics check's item 1): one patient's twenty cells, a few patients'
# hundred, half the cells, and a word so rare that the census withholds its layout.
_STRAY = (("UNK", 20), ("UNKNOWN", 100), ("N.D.", 1200), ("unk.", 3))


def test_a_stray_word_never_takes_a_held_count_out_of_its_room_or_its_test(template: contract.ColumnBlock) -> None:
    """The statistics check's item 1, generated (LANE ID-ROOM3 RULINGS 6 (1)): every counting system (days whole and
    with a time) by the stray words by their share (`_STRAY`), on 400 real births written three times: the producer
    judges the counts left -- `held_counts_widest` and the span-and-density test read as they read without the
    word, and a held counted grain publishes the room it publishes without it -- the census holding the word's
    layout (or the pool, for the rare word); the G1 floor of the counted grain, and the walk's test of a count with
    no grain, write the word where the walk wrote one and every count, read in its member with either mark, outside
    the span the real days fill; the generator's census test and the validator read a census of counts beside the
    word's layout. Before, one patient's word took the column out of every test: 540 twin cells on real birth days
    with nobody answering, 660 with the counts declared. Mutants: a stray word not set aside (R1); a word's layout
    read as no count's in the generator's census test (R13)."""
    draw = random.Random(97)
    checked = 0
    for member, fraction in _COUNTED_READINGS:
        real = [_count(one, member, fraction) for one in _births(400, 101)]
        real_days = _real_days_in(real, member)
        first_real, last_real = min(real_days), max(real_days)
        clean = real * 3
        grain_record = {"kind": "counted", "rung": "held", "reading": member,
                        "finest": "second" if fraction or date_counts.TABLE[member].unit < date_counts.DAY else "day",
                        "mark": ".", "spans": []}
        widest = taxonomy.held_counts_widest(_held_counts(clean), clean)
        systems = taxonomy.counts_may_be_dates(_held_counts(clean), clean)
        room = _producer_block(clean, grain_record).details["made_up_years"]
        assert widest >= 4, (member, widest)
        reading = grains.Reading(grains.COUNTED, member)
        for word, share in _STRAY:
            cells = clean[:share // 2] + [word] * share + clean[share // 2:]
            column = _held_counts(cells)
            if share < 11:
                # ...a word the census withholds: its layout pooled, as the census pools a spelling under the floor.
                forms = dict(column.details["layout_forms"])  # type: ignore[call-overload]
                forms[taxonomy.SUPPRESSED_LABEL] = forms.pop(parsing.layout_form(word, parsing.LAYOUT_PLAIN))
                column = dataclasses.replace(column, details={**column.details, "layout_forms": forms})
            assert taxonomy.held_counts_widest(column, cells) == widest, (member, word, share)
            assert taxonomy.counts_may_be_dates(column, cells) == systems, (member, word, share)
            grained = _producer_block(cells, grain_record)
            assert grained.details["made_up_years"] == room, (member, word, share, grained.details["made_up_years"])
            years = tuple((int(run[0]), int(run[1])) for run in room)  # type: ignore[union-attr]
            facts = _facts_of(grained, years)
            inputs = real[:60] + [word] * 4 + [f"{int(cell.partition('.')[0]) + 1}{cell.partition('.')[1]}"
                                               f"{cell.partition('.')[2]}" for cell in real[60:80]]
            block = dataclasses.replace(
                template, facts=facts, n_present=len(cells), n_distinct=len(set(cells)),
                time_grain=grains.Grain(grains.HELD, reading, len(inputs), _real_span(), grains.SECOND, 0))
            found, _unwritten = generation._inside_the_grain(block, inputs, [draw.getrandbits(64) for _one in inputs])
            loose = _facts_of(_producer_block(cells, None), ((2028, 2028),))
            assert generation._counts_alone(loose, len(cells)), (member, word, share)
            walked = generation._counts_off_the_real(
                dataclasses.replace(template, facts=loose, time_grain=None, n_present=len(cells),
                                    n_distinct=len(set(cells))), loose, inputs, (), ())
            for out in (found, walked):
                for before, after in zip(inputs, out):
                    checked += 1
                    if not parsing.figures_in(before):
                        assert after == before, (member, word, share, before, after)
                        continue
                    assert not [day for day in _days_named(after, member) if first_real <= day <= last_real], (
                        member, fraction, word, share, before, after)
            assert validation.counted_in_the_room(block), (member, word, share)
            assert validation.counted_in_the_room(dataclasses.replace(block, facts=loose, time_grain=None))
    assert checked > 10_000, checked


def _stray_figures(real: "list[str]", born: datetime.datetime) -> "list[str]":
    """Cells holding a figure that the count grammar does not read (LANE ID-ROOM3 RULINGS 7 (1)): zero fills of
    eight and ten figures, a real count zero-padded (after its sign), one patient's birth written as dates in four
    layouts, a grouped number, a plus, spaces, a second point, a day of the year with a two-figure year, `00.00`."""
    sign = "-" if real[0][:1] == "-" else ""
    body = real[0][len(sign):]
    whole = body.partition(".")[0]
    spaced = " ".join(whole[place:place + 3] for place in range(0, len(whole), 3))
    return ["00000000", "0000000000", f"{sign}0{body}", born.strftime("%Y-%m-%d"), born.strftime("%m/%d/%Y"),
            born.strftime("%d-%b-%Y").upper(), born.strftime("%Y-%m-%d %H:%M:%S"), "1,234,567", f"+{body}",
            spaced, f"{whole}.5.1", born.strftime("%y-%j"), "00.00"]


def test_a_stray_figure_never_takes_a_held_count_out_of_its_room_or_its_test(template: contract.ColumnBlock) -> None:
    """The verify of repair 1, item 1, generated (LANE ID-ROOM3 RULINGS 7 (1)): every counting system (days whole and
    with a time) by the stray figures the count grammar does not read (`_stray_figures`) by their share (one cell,
    eleven, one patient's twenty rows, a third), beside 60 real births written three times: the producer judges the
    counts left -- `held_counts_widest` and the span-and-density test read as they read without the stray, the
    stray's layout passed over in the census -- and a held counted grain publishes the room it publishes without it;
    the G1 floor of the counted grain and the walk's test of a count with no grain, fed counts and the walk's
    stand-ins holding a figure, write every count outside the span the real days fill in its system, the floor each
    text value as a word holding no figure; the generator's census test and the validator read the census of counts
    beside the stray's layout. Beyond a third, the strays are judged, and the column is no column of counts. A stray
    date of the room's first years leaves no room (NF137). Before, one such cell took the column out of
    every test: births as seconds beside eleven `00000000` wrote 600 twin cells on 30 real birth days of single
    patients with nobody answering, one patient's 20 ISO rows 380 on 19, declared or not. Mutants: a stray figure not
    set aside; the strays always judged (V1); never judged past a third (V2); the census not passing over a stray's
    layout; a stray date's years not read by the room; the floor's word for a text value dropped."""
    draw = random.Random(107)
    checked = 0
    for member, fraction in _COUNTED_READINGS:
        births = _births(60, 109)
        real = [_count(one, member, fraction) for one in births]
        real_days = _real_days_in(real, member)
        first_real, last_real = min(real_days), max(real_days)
        clean = real * 3
        grain_record = {"kind": "counted", "rung": "held", "reading": member,
                        "finest": "second" if fraction or date_counts.TABLE[member].unit < date_counts.DAY else "day",
                        "mark": ".", "spans": []}
        widest = taxonomy.held_counts_widest(_held_counts(clean), clean)
        systems = taxonomy.counts_may_be_dates(_held_counts(clean), clean)
        room = _producer_block(clean, grain_record).details["made_up_years"]
        assert widest >= 4 and systems, (member, widest, systems)
        reading = grains.Reading(grains.COUNTED, member)
        for stray in _stray_figures(real, births[0]):
            assert taxonomy._no_count_read(stray), stray
            for share in (1, 11, 20, len(clean) // 2):
                cells = clean + [stray] * share
                column = _held_counts(cells)
                assert taxonomy.held_counts_widest(column, cells) == widest, (member, stray, share)
                assert taxonomy.counts_may_be_dates(column, cells) == systems, (member, stray, share)
                checked += 1
            # ...past a third the strays are judged: no column of counts; a single nought counted with them under the cap.
            cells = clean + [stray] * len(clean)
            assert taxonomy.held_counts_widest(_held_counts(cells), cells) == 0, (member, stray)
            cells = clean + ["0"] * (len(clean) // 3) + [stray] * (len(clean) // 4)
            assert taxonomy.held_counts_widest(_held_counts(cells), cells) == 0, (member, stray, "0")
            # ...a third: the producer's room and the twin, on the producer's own facts.
            cells = clean + [stray] * (len(clean) // 2)
            grained = _producer_block(cells, grain_record)
            assert grained.details["made_up_years"] == room, (member, stray, grained.details["made_up_years"])
            years = tuple((int(run[0]), int(run[1])) for run in room)  # type: ignore[union-attr]
            facts = _facts_of(grained, years)
            inputs = real[:30] + [f"{int(cell.partition('.')[0]) + 1}{cell.partition('.')[1]}{cell.partition('.')[2]}"
                                  for cell in real[30:60]] + ["A--", "A-1", "A---------0"]
            block = dataclasses.replace(
                template, facts=facts, n_present=len(cells), n_distinct=len(set(cells)),
                time_grain=grains.Grain(grains.HELD, reading, len(inputs), _real_span(), grains.SECOND, 0))
            found, _unwritten = generation._inside_the_grain(block, inputs, [draw.getrandbits(64) for _one in inputs])
            loose = _facts_of(_producer_block(cells, None), ((2028, 2028),))
            assert generation._counts_alone(loose, len(cells)), (member, stray)
            walked = generation._counts_off_the_real(
                dataclasses.replace(template, facts=loose, time_grain=None, n_present=len(cells),
                                    n_distinct=len(set(cells))), loose, inputs, (), ())
            for out, floor in ((found, bool(years)), (walked, False)):
                texts = 0
                for before, after in zip(inputs, out):
                    checked += 1
                    if parsing.classify_number(after) == parsing.NOT_A_NUMBER:
                        texts += 1
                        # ...the floor's word holds no figure; the walk's text, no count, stands as it wrote it.
                        assert (not parsing.figures_in(after)) if floor else after == before, (
                            member, stray, before, after)
                        continue
                    assert not [day for day in _days_named(after, member) if first_real <= day <= last_real], (
                        member, fraction, stray, before, after)
                assert texts == 3 and len(set(out)) == len(set(inputs)), (member, stray, out[-3:])
            assert validation.counted_in_the_room(block), (member, stray)
            assert validation.counted_in_the_room(dataclasses.replace(block, facts=loose, time_grain=None))
    # ...a stray date of the room's first year is a real cell naming a year of the block: no room (NF137), the twin's
    # counts the walk's, each off every real day.
    real = [_count(one, "seconds-since-1970") for one in _births(200, 111)] * 3
    for grain_record in ({"kind": "counted", "rung": "held", "reading": "seconds-since-1970", "finest": "second",
                          "mark": ".", "spans": []}, None):
        assert _producer_block(real, grain_record).details["made_up_years"]
        assert _producer_block(real + ["2028-06-01"] * 11, grain_record).details["made_up_years"] == []
    assert checked > 2_000, checked


def test_a_walk_value_written_with_noughts_before_its_figures_is_read_as_its_count(template: contract.ColumnBlock) -> None:
    """Lane ID-ROOM3's repair 2 (found at 20,000 rows by the repair, old): births written as seconds from 1970 with a
    decimal comma before three figures, held with nobody answering, are described as text, and where no real cell
    opens with a nought the walk spells its values off the real by opening them with noughts (`000009985,039`), which
    the count grammar reads as no count and so the walk's test let stand; a reader of numbers reads 9,985 seconds, a
    day of January 1970, and 8,200 twin cells fell on the one real birth day of 1970 the column held. The walk's test
    now reads such a value as the count its figures name, so it stands only off every real day. Mutant: the noughts
    read as the grammar reads them (no count)."""
    member = "seconds-since-1970"
    forms = {"%%%%%%%%%,%%%": 4400, "%%%%%%%%,%%%": 620, "-%%%%%%%%%%,%%%": 2000, "-%%%%%%%%%,%%%": 4040}
    exclusions = {"%%%%%%%%%,%%%": ("000009%%%,0%%",), "%%%%%%%%,%%%": ("00009%%%,0%%",),
                  "-%%%%%%%%%%,%%%": ("-9%%%%%%%%%,%%%",), "-%%%%%%%%%,%%%": ("-9999%%%%%,%%%",),
                  parsing.EXCLUSION_SPILL: ("%" * 16,)}
    facts = _facts(forms, ((2028, 2031),), exclusions)
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=11_060, n_distinct=600)
    cells = ["000009985,039", "00009597,077", "000009173,038", "-0692611907,533", "000009985,039"]
    found = generation._counts_off_the_real(column, facts, cells, (), ())
    real_days = _days_named("9985,039", member) | _days_named("692611907,533", member)
    for before, after in zip(cells, found):
        assert after != before and not _days_named(after, member) & real_days, (before, after)
    # ...the positive ones past every real count (the spill: these layouts' exclusions open with noughts), the
    # negative one inside its layout's nine hundreds, which no real count of that layout reaches (1684).
    assert all(len(one) > 16 for one in found[:3]) and found[3].startswith("-9"), found
    assert found[0] == found[4] and len(set(found)) == 4, found
    # ...and beside day numbers of five figures whose layouts' exclusions open with a nine (the zoo's held day numbers),
    # such a value, read as its count, joins its own layout's nine hundreds at the width it is written at, as the walk's
    # other values do, so the census of layouts and the lengths hold.
    forms = {"%%%%%": 9000, "%%%%%.%%": 11_000}
    exclusions = {"%%%%%": ("9%%%%",), "%%%%%.%%": ("9%%%%.%%",), parsing.EXCLUSION_SPILL: ("%" * 9,)}
    facts = _facts(forms, (), exclusions)
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=20_000, n_distinct=4000)
    found = generation._counts_off_the_real(column, facts, ["06059.00", "07666.00", "98072"], ("days-since-1840",), ())
    assert [len(one) for one in found] == [8, 8, 5] and found[0][:1] == "9" and found[1][:1] == "9", found
    assert found[0].endswith(".00") and found[0] != found[1] and found[2] == "98072", found


def test_a_walk_value_is_read_with_the_comma_and_in_the_widest_layout_s_systems(template: contract.ColumnBlock) -> None:
    """Skeptic 1's items 6 and 5: a made-up count written with a decimal comma is read with it (`692611907,533`,
    seconds of 1991, stood as no date, read with the point alone), and a value declared in no system is tested in
    each system the column's widest published layout reads (`98` days from 1960, a short count near an epoch,
    stood tested in the systems of its own two figures); a stray word's layout in the census is passed over. Mutants:
    the comma's reading dropped; the widest layout's systems dropped; a word's layout read as no count's."""
    member = "seconds-since-1970"
    for cell in ("692611907,533", "427728358,002", "296799054,626"):
        assert not generation._count_off_every_real_day(cell, member, {}, 10, {}), cell
    assert generation._count_off_every_real_day("90000000000,533", member, {}, 10, {})
    forms = {"%%%%%%%%%,%%%": 300, "-%%%%%%%%%,%%%": 100}
    exclusions = {parsing.EXCLUSION_SPILL: ("%" * 14,)}
    facts = _facts(forms, ((2028, 2028),), exclusions)
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=400, n_distinct=400)
    found = generation._counts_off_the_real(column, facts, ["692611907,533", "98", "-27"], (), ())
    assert found[0] != "692611907,533" and found[0].endswith(",533"), found
    assert found[1] != "98" and found[2] != "-27", found
    # ...and a stray word's layout in the census, holding no figure, is passed over as the pool is: the census is of
    # counts alone, and the nine hundreds of the counts' width still stand.
    worded = _facts({"%%%%%%%%%%": 900, "@@@": 100}, ((2028, 2028),),
                    {"%%%%%%%%%%": ("9%%%%%%%%%",), parsing.EXCLUSION_SPILL: ("%" * 11,)})
    assert generation._counts_alone(worded, 1000)
    assert generation._first_place_nines(worded, 1000) == {10: True}


def test_a_held_count_s_text_values_are_written_as_words_holding_no_figure(template: contract.ColumnBlock) -> None:
    """The verify of repair 1, item 3 (LANE ID-ROOM3 RULINGS 7 (3)): the walk writes as many text values as the column
    publishes cells that are no number -- a pool's stand-ins `A--`, `A-1`, `A---------0` for two or three patients'
    `UNK` and `UNKNOWN` -- and the G1 floor of a held counted grain with a room wrote a count over each such value
    holding a figure, so the twin held fewer text cells than published and validation exited 3 on `n_numeric` and
    `n_not_numeric` (two patients' words: 40 asked, 20 written). Each is now written as a word holding no figure,
    each figure the capital its value counts from `A`, none of the column's other made-up values; every count is
    still drawn in the room. Mutant: the floor's word for a text value dropped."""
    member = "seconds-since-1970"
    reading = grains.Reading(grains.COUNTED, member)
    real = [_count(one, member) for one in _births(60, 113)]
    inputs = real + ["A--", "A-1", "A---------0", "A-B"]
    block = dataclasses.replace(
        template, facts=_facts({"%%%%%%%%%": 600, contract.WITHHELD: 40}, ((2028, 2028),)),
        n_present=640, n_distinct=64, time_grain=grains.Grain(grains.HELD, reading, len(inputs), (), grains.SECOND, 0))
    found, _unwritten = generation._inside_the_grain(block, inputs, [13 * k for k in range(len(inputs))])
    texts = [cell for cell in found if parsing.classify_number(cell) == parsing.NOT_A_NUMBER]
    assert len(texts) == 4 and len(set(texts)) == 4, found[-4:]
    assert all(not parsing.figures_in(cell) for cell in texts), texts
    assert found[-4] == "A--" and found[-1] == "A-B" and found[-3] == "A-BA", found[-4:]
    for cell in found[:60]:
        assert _day_of(cell, reading) is not None and _day_of(cell, reading).year == 2028, cell  # type: ignore[union-attr]


def test_an_unbounded_spill_keeps_the_figures_after_its_mark(template: contract.ColumnBlock) -> None:
    """The verify of repair 1, item 4 (LANE ID-ROOM3 RULINGS 7 (3)): a held column of counts with no grain whose
    description reads cells as blank writes every value its walk's test refuses as the spill with a plus in place of
    its sign; at the spill's own width a value of seconds with five or ten figures after the point, or milliseconds
    with three, had sixteen whole figures or more (`+9000000000000061.24759`), a reader of numbers read it back as a
    whole number, and validation exited 3 on `all_whole_numbers` with nobody answering (the line passed). The spill
    is now one figure past the census's longest whole part of counts, its merged key still as long as the spill's:
    read back, each value keeps its fraction, no system's count grammar reads it, and none is another's. Mutant: the
    unbounded spill at the spill's own width."""
    for layout, cells, bound in (
        ("%%%%%%%%%%.%%%%%", ["1692611907.53312", "-692611907.11111", "823456789.20001"], 16),
        ("%%%%%%%%%%.%%%%%%%%%%", ["1692611907.5331212345", "-692611907.1111112345"], 21),
        ("%%%%%%%%%%%%%.%%%", ["1692611907533.123", "-692611907533.456"], 17),
    ):
        exclusions = {parsing.EXCLUSION_SPILL: ("%" * bound,)}
        facts = _facts({layout: 400}, ((2028, 2028),), exclusions)
        column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=400, n_distinct=400)
        found = generation._counts_off_the_real(column, facts, cells, (), (), True)
        for before, after in zip(cells, found):
            assert after != before and after[:1] == "+", (before, after)
            assert parsing.numeric_whole(after) == parsing.WHOLE_NO, (layout, after)
            assert after.partition(".")[2] == before.partition(".")[2], (before, after)
            assert len(parsing.merged_key(after)) >= bound, (after, bound)
            assert date_counts.written_count(after) is None, after
        assert len(set(found)) == len(found), found


def test_a_bounded_spill_keeps_a_fraction_a_reader_of_numbers_reads(template: contract.ColumnBlock) -> None:
    """The suite repair (tests/test_stage3b_counted_codex.py's item-1 battery, red on 265536d4): beside one stray ISO
    datetime cell, its count under the floor, the walk of a held column of seconds or milliseconds writes the
    column's only fraction, `12848498.947889330816`, a day of 1970 read as seconds; its census withheld whole and its
    spill twenty characters long, the bounded spill wrote it `90000000000000000000.947889330816`, which a reader of
    numbers reads back as a whole number, and validation exited 3 on `all_whole_numbers` (at 20,000 rows too,
    declared and with nobody answering). Such a value is now written as the unbounded spill is: a plus in place of
    its sign, its figures after the point kept and read as a fraction, its merged key as long as the spill's, read
    by no system's count grammar. A whole value, a fraction whose plus spill would be read whole too (one or two
    figures after the point) and a fraction a shorter spill keeps are written as the bounded spill, as before.
    Mutant: the plus spill for a fraction removed (the bounded spill at the spill's own width)."""
    facts = _facts({}, ((2028, 2031),), {parsing.EXCLUSION_SPILL: ("%" * 20,)})
    column = dataclasses.replace(template, facts=facts, time_grain=None, n_present=600, n_distinct=600)
    cells = ["12848498.947889330816", "-12848498.94788933", "12848498", "-12848498.5", "1600000000.25"]
    found = generation._counts_off_the_real(column, facts, cells, (), ())
    for before, after in zip(cells[:2], found[:2]):
        assert after[:1] == "+" and parsing.numeric_whole(after) == parsing.WHOLE_NO, (before, after)
        assert after.partition(".")[2] == before.partition(".")[2], (before, after)
        assert len(parsing.merged_key(after)) >= 20, after
        assert not [member for member in date_counts.MEMBERS for mark in date_counts.MARKS
                    if date_counts.counted(member, after, mark) is not None], after
    for before, after in zip(cells[2:], found[2:]):
        sign = "-" if before[:1] == "-" else ""
        assert after.startswith(f"{sign}9000000000000000000") and len(after.partition(".")[0]) == len(sign) + 20, (
            before, after)
        assert after.partition(".")[2] == before.partition(".")[2], (before, after)
    assert len(set(found)) == len(found), found
    # ...and a spill of twelve characters keeps the fraction itself: the bounded spill, as before.
    short = _facts({}, ((2028, 2031),), {parsing.EXCLUSION_SPILL: ("%" * 12,)})
    found = generation._counts_off_the_real(dataclasses.replace(column, facts=short), short, cells[:1], (), ())
    assert found == ["900000000000.947889330816"], found


def test_a_count_the_person_said_holds_codes_keeps_its_block(tmp_path: pathlib.Path) -> None:
    """The person's word on codes reaches the held reading (LANE ID-ROOM3 RULINGS 4 (2), the verify's V5): births of
    1928 to 2005 written as seconds from 1970, twice, nobody answering, on a small table (the library's internal
    switch), one column typed `--code`: that column is held with no room, the other publishes the room its counts
    would take. Mutant V5: the person's word never passed from `build_document`."""
    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    people = [f"R{one + 1:04d}" for one in range(60)]
    births = dict(zip(people, _births(60, 115)))
    rows = [[people[place % 60], _count(births[people[place % 60]], "seconds-since-1970"),
             _count(births[people[place % 60]], "seconds-since-1970"), f"{1 + place % 9}"] for place in range(600)]
    with open(tmp_path / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["person_ref", "birth_code", "birth_count", "grade"])
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{tmp_path / 't.csv'}", "--out-dir", f"{tmp_path}", "--replace", "--code",
                         "birth_code"], small_tables_refused=False) == 0
    blocks = {one.name: one for one in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns}
    coded, counted = blocks["birth_code"].facts, blocks["birth_count"].facts
    assert isinstance(coded, contract.IdentifierFacts) and coded.made_up_years is None
    assert isinstance(counted, contract.IdentifierFacts) and counted.made_up_years


def test_the_validator_reads_the_year_width_of_a_held_date_s_room(template: contract.ColumnBlock) -> None:
    """`validation.held_written_blank` (lane ID-ROOM3's repair 1; the verify's V6): a held date whose reading writes a
    two-figure year draws from a two-figure room and one whose reading writes four figures from a four-figure room;
    a room of the other width draws nothing, so the twin is written blank. Mutant V6: the two-figure room unread."""
    for member, years, blank in (("layout {DD}-{MON}-{YY}", ((28, 31),), False),
                                 ("layout {DD}-{MON}-{YY}", ((2028, 2031),), True),
                                 ("iso-date", ((2028, 2031),), False), ("iso-date", ((28, 31),), True)):
        column = dataclasses.replace(
            template, facts=_facts({"%%-@@@-%%": 30}, years),
            time_grain=grains.Grain(grains.HELD, grains.Reading(grains.DATE, member), 30, (), grains.DAY, 0))
        assert validation.held_written_blank(column) is blank, (member, years)


def test_a_room_less_held_date_keeps_a_made_up_word(template: contract.ColumnBlock) -> None:
    """A3 with no room (lane ID-ROOM3's repair 1; the verify's V11): every made-up value holding a figure of a held
    date with no room is written blank, and a made-up word holding none, which stands for a real word, is kept as
    the walk wrote it. Mutant V11: the word written blank too."""
    reading = grains.Reading(grains.DATE, "iso-date")
    column = dataclasses.replace(
        template, facts=_facts({"%%%%-%%-%%": 30}, ()), n_present=32, n_distinct=32,
        time_grain=grains.Grain(grains.HELD, reading, 32, _real_span(), grains.DAY, 0))
    cells = [one.date().isoformat() for one in _births(30, 117)] + ["A--", "UNKNOWN"]
    found, _unwritten = generation._inside_the_grain(column, cells, [3 * k for k in range(32)])
    assert found[:30] == [""] * 30 and found[30:] == ["A--", "UNKNOWN"], found[-3:]


# -- A2: the census withheld whole ------------------------------------------------------------------------------------


def test_a_census_withheld_whole_is_read_in_its_reading_s_layout(template: contract.ColumnBlock) -> None:
    """A2, K-HZ-06's path A (LANE ID-ROOM2 RULINGS 7 (1)): a held birth column whose layout census is withheld whole
    names no date layout; the producer reads it as the layout its grain's reading writes a day in, every cell in
    that layout's orders and its own, and publishes the room; the G1 floor reads its made-up values in that layout
    and writes them in the room. The verify of lane ID-ROOM2's repair 2 measured 17,513 to 17,517 of 20,000 twin
    cells on a real birth date on the public head. Mutant X4, either call of `member_date_layout` removed."""
    draw = random.Random(5)
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    cells: "list[str]" = []
    for place in range(6000):
        low, high = (1980, 1985) if place % 500 == 0 else (2000, 2025)
        day = datetime.date.fromordinal(draw.randint(datetime.date(low, 1, 1).toordinal(),
                                                     datetime.date(high, 12, 31).toordinal()))
        year = f"{day.year}" if low == 1980 else f"{day.year % 100:02d}"
        cells += [f"{day.day:02d}-{months[day.month - 1]}-{year}"]
    grain = {"finest": "day", "kind": "date", "mark": ".", "people": 60, "reading": "layout {DD}-{Mon}-{YY}",
             "rows": 6000, "rung": "held", "spans": [["year", "2000-01-01", "2025-01-01"]]}
    held = taxonomy.with_made_up_years(_held_profile({"(withheld)": 6000}, len(set(cells)), grain), cells)
    runs = _runs(held)
    assert runs and runs[0][0] == 28 and runs[-1][1] < 80, runs
    assert taxonomy.member_date_layout("layout {DD}-{Mon}-{YY}") == "%%-@&&-%%"
    assert taxonomy.member_date_layout("iso-date") == "%%%%-%%-%%"
    assert taxonomy.member_date_layout("layout {YYYY}{DDD}") == ""
    reading = grains.Reading(grains.DATE, "iso-date")
    births = [one.date().isoformat() for one in _births(30, 7)]
    column = dataclasses.replace(
        template, facts=_facts({contract.WITHHELD: 30}, ((2028, 2030),)),
        time_grain=grains.Grain(grains.HELD, reading, 30, _real_span(), grains.DAY, 0), n_distinct=30, n_present=30)
    found, _unwritten = generation._inside_the_grain(column, births, [11 * k for k in range(30)])
    assert all(datetime.date.fromisoformat(cell).year in (2028, 2029, 2030) for cell in found), found[:4]


# -- A5: a day of the year -------------------------------------------------------------------------------------------


def test_a_day_of_the_year_takes_the_room() -> None:
    """A5: a held column read as days of the year (`%Y%j`, SAS's JULIAN7., answered dates) names no layout a merged
    order reads; it now takes the room as a stamp's is taken -- every cell read by every reading the room holds
    against, a day of the year among them -- where before it had none and drew from its grain's span (203 twin
    cells on 10 real birth days at 20,000 rows). Mutant X7, the day-of-year arm of `with_made_up_years` removed."""
    grain = {"kind": "date", "rung": "held", "reading": "layout {YYYY}{DDD}", "finest": "day", "mark": ".",
             "spans": []}
    # ...births whose every reading leaves the block free: no reading of the cell names a year of 2028 to 2040 (a
    # birth of 1942 on its 32nd day, `1942032`, holds the run `2032`; one of 2005 on its 128th, `2005128`, a
    # two-figure 28).
    def named_by(cell: str) -> "set[int]":
        four, two = taxonomy.cell_date_years(cell)
        return set(four) | {1900 + year for year in two} | {2000 + year for year in two}

    cells = [cell for cell in (one.strftime("%Y%j") for one in _births(3000, 13))
             if not {year for year in named_by(cell) if 2028 <= year <= 2040}][:1000]
    named: "set[int]" = set()
    for cell in cells:
        named |= named_by(cell)
    held = taxonomy.with_made_up_years(_held_profile({"%%%%%%%": len(cells)}, len(set(cells)), grain), cells)
    runs = _runs(held)
    room = {year for first, last in runs for year in range(first, last + 1)}
    assert not room & named, sorted(room & named)
    assert runs and runs[0][0] == 2028, runs
    # ...and every birth of the year: a run the room reader reads as a year of the block takes it, so the block finds
    # no room and the column comes back as it came, the base's bytes (lane ID-ROOM3's repair 1): its twin is written
    # blank (`_no_date_cells`), never a real day nor text that is no date (the price, stated in P4-D488).
    every = [one.strftime("%Y%j") for one in _births(1000, 13)]
    column = _held_profile({"%%%%%%%": 1000}, len(set(every)), grain)
    assert taxonomy.with_made_up_years(column, every) == column
    assert generation._stamp_in_the_room("2028123", generation._room_published(([2028, 2029], [])))


# -- the validator and the reports -------------------------------------------------------------------------------------


def test_the_validator_lists_a_room_count_s_lengths_and_the_reports_name_a_room_less_grain(
    template: contract.ColumnBlock,
) -> None:
    """A held column of counted dates written in the room has its lengths, layouts and counts of figures alone
    listed report-only (`validation.counted_in_the_room`), its room's years not the table's, and so does one
    publishing an empty room, whose walk's values were moved off every real day; a held grain of a kind the room
    serves publishing none is named by both reports' F10 line, its twin writing no date."""
    reading = grains.Reading(grains.COUNTED, "seconds-since-1970")
    grain = grains.Grain(grains.HELD, reading, 10, (), grains.SECOND, 0)
    column = dataclasses.replace(template, facts=_facts({"-%%%%%%%%%": 10}, ((2028, 2028),)), time_grain=grain)
    assert validation.counted_in_the_room(column)
    assert validation.counted_in_the_room(dataclasses.replace(column, facts=_facts({"-%%%%%%%%%": 10}, ())))
    assert not validation.counted_in_the_room(dataclasses.replace(column, facts=_facts({"-%%%%%%%%%": 10}, None)))
    clock = grains.Grain(grains.HELD, grains.Reading(grains.CLOCK, "hh-mm"), 10, (), grains.MINUTE, 0)
    assert not validation.counted_in_the_room(dataclasses.replace(column, time_grain=clock))
    assert generation.dates_written_as_record_numbers(["-%%%%%%%%%"], None, grains.COUNTED, "seconds-since-1970")
    assert generation.dates_written_as_record_numbers(["%%%%-%%-%%"], None, grains.DATE, "iso-date")
    assert not generation.dates_written_as_record_numbers(["%%:%%"], None, grains.CLOCK, "hh-mm")
    assert not generation.dates_written_as_record_numbers(
        ["-%%%%%%%%%"], ((2028, 2028),), grains.COUNTED, "seconds-since-1970")


def test_a_small_table_s_held_counts_are_walked_and_its_room_less_stamps_written_blank(tmp_path: pathlib.Path) -> None:
    """Through the commands a person types on a small table (the library's internal switch; the command refuses
    tables under its floor), nobody answering: births of 1928 to 2005 written as seconds beside one patient's `UNK`
    are held with no grain while the questions offering `identifier` are open, publish the room their counts would
    take and have their walk kept off every real day by the plan (`_plan_column`'s call), the word's pool written
    as the walk's stand-ins (the same column in milliseconds, too thin at 600 rows, is counted absent there); births
    written
    as SAS datetimes with a two-figure year are held with no room and written BLANK, never the walk's text, the twin's
    report naming the blank cells; validation exits 0, listing the blank column's facts with the reason (LANE
    ID-ROOM3 RULINGS 3 (2) and 6 (3): the description's bytes as the base's, validate's exit 0). Mutants: Y12, the
    plan's walk test removed; the open question's arm removed; the blank of `_no_date_cells` dropped; the
    validator's listing of a blank column dropped; a stray word not set aside."""
    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    draw = random.Random(83)
    people = [f"R{one + 1:04d}" for one in range(60)]
    births = dict(zip(people, _births(60, 89)))
    header = ["person_ref", "birth_ms", "birth_unk", "birth_sdt2", "grade"]
    rows: "list[list[str]]" = []
    for place in range(600):
        person = people[place % 60]
        born = births[person]
        rows += [[person, _count(born, "milliseconds-since-1970"),
                  "UNK" if person == people[0] else _count(born, "seconds-since-1970"),
                  born.strftime("%d%b%y:%H:%M:%S").upper(), f"{1 + draw.randrange(9)}"]]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"],
                        small_tables_refused=False) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"], small_tables_refused=False) == 0
        exit_code = cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                              "--out-dir", f"{tmp_path}", "--replace"], small_tables_refused=False)
    blocks = {block.name: block for block in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns}
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    for name, member in (("birth_unk", "seconds-since-1970"),):
        facts = blocks[name].facts
        assert isinstance(facts, contract.IdentifierFacts) and facts.made_up_years is not None, name
        assert blocks[name].time_grain is None, name
        place = header.index(name)
        real = _real_days_in([row[place] for row in rows], member)
        written = [row[twin[0].index(name)] for row in twin[1:]]
        assert not [cell for cell in written if _days_named(cell, member) & real], name
        # ...and every value the twin wrote is one the walk's test keeps by the published facts alone: the plan
        # asked it of every value (with no plan's test the walk's record numbers stood at the real widths).
        assert generation._counts_off_the_real(blocks[name], facts, written, (), (), blocks[name].n_missing_blank > 0
                                               ) == written, name
    grain = blocks["birth_sdt2"].time_grain
    assert grain is not None and grain.rung == grains.HELD and validation.held_written_blank(blocks["birth_sdt2"])
    stamps = [row[twin[0].index("birth_sdt2")] for row in twin[1:]]
    assert all(cell == "" for cell in stamps), stamps[:3]
    assert "600 cells written blank" in (tmp_path / "t-twin-report.txt").read_text(encoding="utf-8")
    quality = (tmp_path / "t-twin-quality.txt").read_text(encoding="utf-8")
    assert exit_code == 0, quality[-1500:]
    assert "has its twin written blank" in " ".join(quality.split())


def test_a_count_declared_in_a_system_none_of_its_counts_reads_is_held_never_a_traceback(
    tmp_path: pathlib.Path,
) -> None:
    """Births of 1928 to 2005 written as seconds from 1970 and declared `--date-count birth_s excel-1900`, a
    counting system in which not one of them names a date, through the commands a person types on a small table
    (the library's internal switch; the command refuses tables under its floor), nobody answering: the declaration
    decides nothing and the column is held as record numbers, the room its counts would take published and every
    count its twin writes off every real birth day; generate and validate exit 0. Before, describing it raised
    (`min` of no lengths in the identifier block) on every table, at 2,000 rows as at 20,000, on the lane's base as
    on the merged line, and the command stopped with a traceback. Mutant: a declaration that read no count as a
    date asked for its verdict again (`cells.present` not asked first)."""
    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    draw = random.Random(71)
    people = [f"R{one + 1:04d}" for one in range(60)]
    births = dict(zip(people, _births(60, 73)))
    header = ["person_ref", "birth_s", "grade"]
    rows = [[people[place % 60], _count(births[people[place % 60]], "seconds-since-1970"),
             f"{1 + draw.randrange(9)}"] for place in range(600)]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
                         "--date-count", "birth_s", "excel-1900"], small_tables_refused=False) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"], small_tables_refused=False) == 0
        exit_code = cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                              "--out-dir", f"{tmp_path}", "--replace"], small_tables_refused=False)
    block = {one.name: one for one in contract.load_profile(f"{tmp_path / 't-profile.json'}").columns}["birth_s"]
    assert block.role == taxonomy.ROLE_IDENTIFIER and isinstance(block.facts, contract.IdentifierFacts)
    assert block.facts.made_up_years is not None
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    written = [row[twin[0].index("birth_s")] for row in twin[1:]]
    real = _real_days_in([row[1] for row in rows], "seconds-since-1970")
    assert not [cell for cell in written if _days_named(cell, "seconds-since-1970") & real]
    quality = (tmp_path / "t-twin-quality.txt").read_text(encoding="utf-8")
    assert exit_code == 0, quality[-1500:]


# -- one case at the table floor for the writers together ----------------------------------------------------------


def _real_days(cells: "list[str]", read: "object") -> "set[datetime.date]":
    found: "set[datetime.date]" = set()
    for cell in cells:
        day = read(cell)  # type: ignore[operator]
        if day is not None:
            found.add(day)
    return found


def test_at_the_table_floor_no_held_date_or_count_names_a_real_day(tmp_path: pathlib.Path) -> None:
    """20,000 rows, 1,000 patients born 1928 to 2005, nobody at the keyboard: births written as seconds from 1970,
    declared (A1b (i), its counted grain and room) and not (A1b (ii), the walk's test); births written as days of
    the year, declared dates (A5; with no room, written blank); visits in ISO with one patient's twenty rows in
    another layout (A2, the census withheld at the floor); visits in ISO with three `99999` (A3: no room, no date);
    births of 1973 to 2001 written as nine-figure seconds, which only the open question offering `identifier` holds
    (skeptic 1's item 1: 1,620 twin cells on 81 real birth days before); births written as seconds beside one
    patient's `UNK` (the statistics check's item 1: 540 before), and the same column with the counts declared and
    the patient answered `identifier` (660 before). And since repair 2 (the verify of repair 1, LANE ID-ROOM3 RULINGS
    7): births as seconds beside eleven `00000000` (600 twin cells on 30 real birth days before) and beside one
    patient's twenty rows written as ISO dates (380 on 19, nobody answering and declared alike); births of 1970 as
    seconds, one calendar year at the epoch (5,420 on 100); births as seconds with five figures after the point
    (validation exited 3 on `all_whole_numbers`); and, declared, two patients' words (validation exited 3 on the
    counts of numbers). Not one twin cell of any of them falls on a day a real cell of its column names, and
    validation exits 0 on both runs. Before the lane: 640 birth cells, 203, 16,901 and 17,064 visit cells (planning
    measure). Mutants X0 to X7 and the repairs' each turn a column red here or above."""
    from synthtwin import cli

    import unanswered_identifier_shapes as held_shapes

    draw = random.Random(206)
    people = [f"P{one + 1:05d}" for one in range(1000)]
    births = {person: born for person, born in zip(people, _births(1000, 29))}
    visits: "dict[str, list[datetime.date]]" = {}
    for person in people:
        day = datetime.date(2016, 1, 1) + datetime.timedelta(days=draw.randrange(6 * 365))
        seen: "list[datetime.date]" = []
        for _visit in range(20):
            seen += [day]
            day += datetime.timedelta(days=1 + int(draw.expovariate(1 / 40)))
        visits[person] = seen
    order = [(person, visit) for person in people for visit in range(20)]
    draw.shuffle(order)
    young = {person: born for person, born in zip(people, _young_births(1000, 211))}
    cohort = {person: born for person, born in zip(people, _cohort(1970, 1000, 213))}
    header = ["person_ref", "birth_s", "birth_u", "birth_j", "visit_mix", "visit_ph", "birth_z", "birth_x", "birth_z8",
              "birth_w", "birth_c70", "birth_f5", "birth_w2", "grade"]
    rows: "list[list[str]]" = []
    zeros = {7 + 1811 * one for one in range(11)}
    for place, (person, visit) in enumerate(order):
        born = births[person]
        seen = visits[person][visit]
        mix = seen.strftime("%d-%b-%Y").upper() if person == order[0][0] else seen.isoformat()
        ph = "99999" if place in (5, 5000, 15000) else seen.isoformat()
        count = _count(born, "seconds-since-1970")
        stray = "UNK" if person == order[1][0] else count
        words = {order[1][0]: "UNK", order[3][0]: "UNKNOWN"}
        rows += [[person, count, count, born.strftime("%Y%j"), mix, ph, _count(young[person], "seconds-since-1970"),
                  stray, "00000000" if place in zeros else count,
                  born.date().isoformat() if person == order[2][0] else count,
                  _count(cohort[person], "seconds-since-1970"), f"{count}.{(int(person[1:]) * 7919) % 100000:05d}",
                  words.get(person, count), f"{1 + place % 9}"]]
    table = tmp_path / "t.csv"
    with open(table, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    typed = ["--date-count", "birth_s", "seconds-since-1970", "--date-column", "birth_j"]
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", *typed]) == 0
        assert cli.main(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--seed", "0",
                         "--replace"]) == 0
        exit_code = cli.main(["validate", f"{tmp_path / 't-profile.json'}", "--twin", f"{tmp_path / 't-twin.csv'}",
                              "--out-dir", f"{tmp_path}", "--replace"])
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = list(csv.reader(handle))
    seconds = grains.Reading(grains.COUNTED, "seconds-since-1970")

    def read_seconds(cell: str) -> "datetime.date | None":
        return _day_of(cell, seconds)

    def read_doy(cell: str) -> "datetime.date | None":
        try:
            return datetime.datetime.strptime(cell, "%Y%j").date()
        except ValueError:
            return None

    def read_iso(cell: str) -> "datetime.date | None":
        for form in ("%Y-%m-%d", "%d-%b-%Y"):
            try:
                return datetime.datetime.strptime(cell.title() if "-" in cell[2:3] else cell, form).date()
            except ValueError:
                continue
        return None

    def read_both(cell: str) -> "datetime.date | None":
        return read_seconds(cell) or read_iso(cell)

    readers = {"birth_s": read_seconds, "birth_u": read_seconds, "birth_j": read_doy, "visit_mix": read_iso,
               "visit_ph": read_iso, "birth_z": read_seconds, "birth_x": read_seconds, "birth_z8": read_seconds,
               "birth_w": read_both, "birth_c70": read_seconds, "birth_f5": read_seconds, "birth_w2": read_seconds}
    on_real: "dict[str, int]" = {}
    for name, read in readers.items():
        place = header.index(name)
        real = _real_days([row[place] for row in rows], read)
        on_real[name] = sum(1 for row in twin[1:] if read(row[twin[0].index(name)]) in real)
    assert on_real == {name: 0 for name in readers}, on_real
    assert exit_code == 0, (tmp_path / "t-twin-quality.txt").read_text(encoding="utf-8")[-1500:]
    # ...a day of the year with no room is written blank, never text that is no date.
    assert not [row for row in twin[1:] if row[twin[0].index("birth_j")] and read_doy(row[twin[0].index("birth_j")])
                is None], "no text that is no date"
    # ...AND THE STRAY WORD WITH THE COUNTS DECLARED (mode A of the statistics check's item 1, 660 twin cells on real
    # birth days before): the patient answered `identifier`, the column typed `--date-count`; and since repair 2 one
    # patient's ISO rows and two patients' words, declared alike.
    small = tmp_path / "a"
    small.mkdir()
    kept = ["birth_x", "birth_w", "birth_w2"]
    with open(small / "t.csv", "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["person_ref", *kept, "grade"])
        writer.writerows([[row[0], *[row[header.index(name)] for name in kept], row[-1]] for row in rows])
    typed = [one for name in kept for one in ("--date-count", name, "seconds-since-1970")]
    with held_shapes.nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), \
            contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{small / 't.csv'}", "--out-dir", f"{small}", "--replace", *typed]) == 0
        questions = small / "t-questions.json"
        asked = json.loads(questions.read_text(encoding="utf-8"))
        for entry in list(asked.get("asked") or []) + list((asked.get("checklist") or {}).get("columns") or []):
            offered = [choice.get("answer") for choice in entry.get("answers_you_can_give", [])]
            if entry.get("column") == "person_ref" and "identifier" in offered:
                entry["your_answer"] = "identifier"
        questions.write_text(json.dumps(asked, indent=2), encoding="utf-8", newline="\n")
        # The answered round is the first to publish between columns (the patient layer at the floor, lane W5-PL):
        # the record of earlier descriptions asks for --replace-description, as the first round's screen says.
        assert cli.main(["profile", f"{small / 't.csv'}", "--out-dir", f"{small}", "--replace", *typed,
                         "--answers", f"{questions}", "--replace-description"]) == 0
        assert cli.main(["generate", f"{small / 't-profile.json'}", "--out-dir", f"{small}", "--seed", "0",
                         "--replace"]) == 0
        declared_exit = cli.main(["validate", f"{small / 't-profile.json'}", "--twin", f"{small / 't-twin.csv'}",
                                  "--out-dir", f"{small}", "--replace"])
    with open(small / "t-twin.csv", encoding="utf-8", newline="") as handle:
        declared = list(csv.reader(handle))
    for place, name in enumerate(kept):
        read = read_both if name == "birth_w" else read_seconds
        real = _real_days([row[header.index(name)] for row in rows], read)
        assert declared[0][place + 1] == name, declared[0]
        assert not [row for row in declared[1:] if read(row[place + 1]) in real], f"declared: a real day of {name}"
    assert declared_exit == 0, (small / "t-twin-quality.txt").read_text(encoding="utf-8")[-1500:]

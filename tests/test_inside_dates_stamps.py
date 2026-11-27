"""Gate file of lane IN-5b: a twin's stamps drawn from census shapes, never from a real person's time.

THE OWNER'S RULING OF 2026-11-18: no line of a twin may be a real patient, and
the five twin-versus-real checks of `synthtwin.twin_checks` stay strict. The
dates zone of the inside record (version 3) is read so that a twin's dates
keep the real table's shapes (weekday, hour, minute, month, the gaps between
dates) while its stamps meet real stamps only as often as an independent
sample of the same table would. Each case pins one clause, on the invented
tables of the reliability battery or on cells written here, and each is red
on its mutant (lane IN-5b's report names them):

* where a person starts inside the room its span leaves is kept as shares
  of at most ten bins, a place drawn evenly inside its bin: twin persons
  start on as many different days as real ones, over the whole width of a
  bin, and the twin's stamps equal a real stamp no more often than
  independent samples of the same table do;
* a month's weekdays read from few persons are its calendar's weekdays, and
  a real departure (a clinic held on Mondays one year, on Thursdays the
  next) is kept;
* an hour's own minutes (a first slot at 08:30, none at 08:00) are kept,
  and minutes read from few stamps are the clock's minutes; the weekend's
  own hours are kept;
* a band of persons of one date keeps its own months: its persons start
  where real persons of one date start, not where persons of many do;
* a date column written alone keeps each month's count of the table to
  within a few rows, so a monthly series' spread is the table's own;
* a minute moved off a five-minute mark lands on any minute between marks;
* the writer refuses a zone of version 2, whose twins sat on real persons'
  times;
* the charting table's twin drawn through the commands passes lane IN-1's
  nearest-record check (C2) and its rare-date clause (C4) at table seed 1,
  where the version 2 zone's twin failed both.
"""

from __future__ import annotations

import copy
import csv
import datetime
import io
import json
import pathlib
import random
import statistics
import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import inside, inside_dates, installation, twin_checks

PERSON = T.PERSON["T3"]
ROWS = 20000


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    return {name: [row[i] for row in body] for i, name in enumerate(header)}


def _skip(table: str) -> "tuple[str, ...]":
    return tuple(name for name, known in T.KNOWS[table].items() if known == "identifier" and name != T.PERSON[table])


def _reading(zone: "dict[str, object]", name: str) -> inside_dates.Reading:
    entry = typing.cast("dict[str, typing.Any]", zone["columns"])[name]
    return inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])


@pytest.fixture(scope="module")
def charting() -> "dict[str, object]":
    """The battery's charting table at 20,000 rows, its zone and the writer's twins at seeds 0 to 2 (the real
    persons and labels standing in for the generate step's), and three independent samples of the table."""
    real = _columns(T.text("T3", ROWS, 1))
    zone = inside_dates.build_zone(real, PERSON, skip=_skip("T3"))
    twins = [inside_dates.write_dates(zone, ROWS, people=real[PERSON], given=real, seed=seed) for seed in range(3)]
    samples = [_columns(T.text("T3", ROWS, seed))["charted_at"] for seed in (11, 12, 13)]
    return {"real": real, "zone": zone, "twins": twins, "samples": samples}


# -- where a person starts, and how often a twin stamp is a real one ------------------------------------------


def test_a_person_s_place_is_kept_as_bins_and_twin_persons_start_on_many_days(charting) -> None:  # type: ignore[no-untyped-def]
    """Places are shares of at most ten bins; twin persons start on at least half as many days as real ones
    (mutants: places kept on a thousand bins, a grid of real persons' own places; a place at its bin's start)."""
    zone = typing.cast("dict[str, typing.Any]", charting["zone"])
    assert zone["version"] == 3
    places = zone["timeline"]["places"]
    assert places and all(len(shares) <= 10 and sum(shares) == inside_dates.PER for shares in places.values())
    real = typing.cast("dict[str, list[str]]", charting["real"])
    twin = typing.cast("list[dict[str, list[str]]]", charting["twins"])[0]
    reading = _reading(zone, "charted_at")

    def first_days(cells: "list[str]") -> "set[int]":
        firsts: "dict[str, int]" = {}
        for person, cell in zip(real[PERSON], cells):
            moment = inside_dates.moment_of(cell, reading) if cell else None
            if moment is not None and (person not in firsts or moment[0] < firsts[person]):
                firsts[person] = moment[0]
        return set(firsts.values())

    real_days, twin_days = first_days(real["charted_at"]), first_days(twin["charted_at"])
    assert len(twin_days) >= 0.5 * len(real_days), f"{len(twin_days)} first days in the twin, {len(real_days)} real"


def test_a_place_is_drawn_evenly_inside_its_bin(charting) -> None:  # type: ignore[no-untyped-def]
    """Every person's place set in the fifth tenth of its room: the twin's persons of two dates or more start over
    at least six different weeks of that tenth (mutant: the place at its bin's start, two weeks at most)."""
    zone = copy.deepcopy(typing.cast("dict[str, typing.Any]", charting["zone"]))
    places = zone["timeline"]["places"]
    for key in places:
        places[key] = [0, 0, 0, 0, inside_dates.PER, 0, 0, 0, 0, 0]
    real = typing.cast("dict[str, list[str]]", charting["real"])
    twin = inside_dates.write_dates(zone, ROWS, people=real[PERSON], given=real, seed=0)
    reading = _reading(zone, "charted_at")
    by: "dict[str, list[int]]" = {}
    for person, cell in zip(real[PERSON], twin["charted_at"]):
        moment = inside_dates.moment_of(cell, reading) if cell else None
        if moment is not None:
            by.setdefault(person, []).append(moment[0])
    weeks = {min(days) // 7 for days in by.values() if len(days) >= 2}
    assert len(weeks) >= 6, f"the twin's persons start in {len(weeks)} weeks"


def test_a_twin_s_stamps_meet_real_stamps_as_often_as_an_independent_sample_s(charting) -> None:  # type: ignore[no-untyped-def]
    """The share of twin stamps equal to a real stamp, over three twin seeds, is at most 1.2 times that of three
    independent samples of the table (measured 1.11; mutant: places kept on a thousand bins, 1.32)."""
    real = typing.cast("dict[str, list[str]]", charting["real"])
    stamps = {cell for cell in real["charted_at"] if cell}

    def rate(cells: "list[str]") -> float:
        return sum(1 for cell in cells if cell in stamps) / len(cells)

    twins = statistics.mean(rate(twin["charted_at"]) for twin in typing.cast("list[dict[str, list[str]]]", charting["twins"]))
    samples = statistics.mean(rate(cells) for cells in typing.cast("list[list[str]]", charting["samples"]))
    assert twins <= 1.2 * samples, f"twin {twins * 1e4:.1f} per 10,000 against independent samples {samples * 1e4:.1f}"


# -- the calendar: a month's weekdays ---------------------------------------------------------------------------


def _month_weekdays(entry: "dict[str, object]") -> "dict[tuple[int, int], list[float]]":
    years = typing.cast("list[int]", entry["years"])
    cells = typing.cast("list[list[int]]", entry["cells"])
    out: "dict[tuple[int, int], list[float]]" = {}
    for year, row in zip(years, cells):
        for month in range(12):
            week = row[month * 7:(month + 1) * 7]
            if sum(week):
                out[(year, month + 1)] = [share / sum(week) for share in week]
    return out


def test_a_month_of_few_persons_takes_the_calendar_s_weekdays_and_a_real_departure_stays() -> None:
    """Days of 2,400 persons over two years, Mondays about a fifth of them: every month writes the calendar's weekdays
    (within 0.05 in total variation; mutant: each month its own counts); a clinic on Mondays in 2023 and on
    Thursdays in 2024 keeps each month's own weekday (mutant: every month the pooled weekdays)."""
    r = random.Random(3)
    start = datetime.date(2023, 1, 2)
    days: "list[int]" = []
    while len(days) < 2400:
        day = start + datetime.timedelta(days=r.randrange(728))
        if day.weekday() == 0 or r.random() < 0.6:
            days += [(day - datetime.date(1970, 1, 1)).days]
    noisy = _month_weekdays(inside_dates._calendar(days, {}))
    pooled = [0.0] * 7
    for day in days:
        pooled[inside_dates.weekday(day)] += 1 / len(days)
    worst = max(0.5 * sum(abs(a - b) for a, b in zip(week, pooled)) for week in noisy.values())
    assert worst <= 0.05, f"a month's weekdays depart from the calendar's by {worst:.3f}"
    clinic: "list[int]" = []
    for k in range(2000):
        day = start + datetime.timedelta(days=r.randrange(357))
        while day.weekday() != 0:
            day = day + datetime.timedelta(days=1)
        if k % 2:
            day = day + datetime.timedelta(days=367)
        clinic += [(day - datetime.date(1970, 1, 1)).days]
    kept = _month_weekdays(inside_dates._calendar(clinic, {}))
    for (year, _month), week in kept.items():
        assert week[0 if year == 2023 else 3] >= 0.95, (year, _month, [round(x, 3) for x in week])


# -- the clock: an hour's minutes and a weekday's hours ----------------------------------------------------------


def _stamps(days: "list[int]", seconds: "list[int]") -> "dict[str, object]":
    return inside_dates._clock(days, [second * inside_dates.TICKS for second in seconds])


def test_an_hour_s_own_minutes_stay_and_minutes_of_few_stamps_are_the_clock_s() -> None:
    """A weekday schedule from 08:30 to 16:15 whose 08:00 hour holds only 08:30 and 08:45 writes under 1 per cent of
    that hour at 08:00 or 08:15 (measured 0.65; mutant: every hour the pooled minutes); 1,200 stamps at any minute write each
    hour's minutes within 0.15 of the clock's in total variation (mutant: each hour its own counts); weekend stamps
    at any hour keep over a third of the Saturday outside 08:00 to 17:00, where weekdays hold none (mutant: the
    pooled hours)."""
    r = random.Random(5)
    base = (datetime.date(2024, 1, 1) - datetime.date(1970, 1, 1)).days
    days: "list[int]" = []
    seconds: "list[int]" = []
    for _ in range(12000):
        day = base + r.randrange(364)
        if inside_dates.weekday(day) >= 5:
            hour, minute = r.randrange(24), r.randrange(60)
        else:
            slot = 0 if r.random() < 0.3 else r.randrange(1, 32)
            hour, minute = divmod(8 * 60 + 30 + 15 * slot, 60)
        days += [day]
        seconds += [hour * 3600 + minute * 60]
    clock = typing.cast("dict[str, list[list[int]]]", _stamps(days, seconds))
    eight = clock["minute"][8]
    assert (eight[0] + eight[15]) <= 0.01 * sum(eight), eight[0:46:15]
    saturday = clock["hour"][5]
    outside = sum(saturday[hour] for hour in range(24) if not 8 <= hour < 17)
    assert outside >= sum(saturday) / 3, saturday
    sparse_days = [base + r.randrange(364) for _ in range(1200)]
    sparse = typing.cast("dict[str, list[list[int]]]", _stamps(sparse_days, [r.randrange(86400) for _ in range(1200)]))
    every = [sum(sparse["minute"][hour][minute] for hour in range(24)) for minute in range(60)]
    total = sum(every)
    for hour in range(24):
        own = sparse["minute"][hour]
        if sum(own):
            distance = 0.5 * sum(abs(own[m] / sum(own) - every[m] / total) for m in range(60))
            assert distance <= 0.15, f"hour {hour}: {distance:.3f}"


# -- a band of persons of one date --------------------------------------------------------------------------------


def test_persons_of_one_date_start_where_real_persons_of_one_date_start() -> None:
    """Cases at 6,000 rows: a patient of one case is admitted any day of the two years, one of several cases early;
    the twin's patients of one case keep the invented table's median day within 60 days (measured 28; mutants: no band keeps a
    calendar, 151; every census the pooled one, 148)."""
    cases = _columns(T.text("T4", 6000, 1))
    zone = inside_dates.build_zone(cases, T.PERSON["T4"], skip=_skip("T4"))
    twin = inside_dates.write_dates(zone, 6000, people=cases[T.PERSON["T4"]], given=cases, seed=0)
    reading = _reading(zone, "sched_start")

    def single(cells: "list[str]") -> "list[int]":
        by: "dict[str, list[int]]" = {}
        for person, cell in zip(cases[T.PERSON["T4"]], cells):
            moment = inside_dates.moment_of(cell, reading) if cell else None
            if moment is not None:
                by.setdefault(person, []).append(moment[0])
        return [found[0] for found in by.values() if len(found) == 1]

    real, mine = single(cases["sched_start"]), single(twin["sched_start"])
    assert len(real) == len(mine) > 500
    assert abs(statistics.median(real) - statistics.median(mine)) <= 60


# -- a column written alone: its monthly counts ---------------------------------------------------------------------


def test_a_column_written_alone_keeps_its_monthly_counts() -> None:
    """The cohort at 20,000 rows, one row a patient: every month of the twin's admissions holds the real month's count
    to within three rows, so a monthly series' spread about its trend is the table's own and not a second spread drawn
    on top of it (mutant: each row's month drawn on its own, months up to dozens of rows off)."""
    cohort = _columns(T.text("T1", ROWS, 1))
    zone = inside_dates.build_zone(cohort, "", skip=_skip("T1"))
    name = typing.cast("list[str]", zone["order"])[0]
    twin = inside_dates.write_dates(zone, ROWS, given=cohort, seed=0)

    def months(cells: "list[str]") -> "dict[str, int]":
        counts: "dict[str, int]" = {}
        for cell in cells:
            if cell:
                counts[cell[:7]] = counts.get(cell[:7], 0) + 1
        return counts

    real, mine = months(cohort[name]), months(twin[name])
    assert set(mine) <= set(real)
    worst = max(abs(real[month] - mine.get(month, 0)) for month in real)
    assert worst <= 3, f"a month of the twin is {worst} rows off the table's"


# -- the minute off a mark -----------------------------------------------------------------------------------------


def test_a_minute_moved_off_a_mark_lands_on_any_minute_between_marks() -> None:
    """Charting at 6,000 rows: of the device rows' twin minutes off a five-minute mark, at most 0.32 fall one minute
    after a mark (measured 0.247, an even spread 0.25; mutant: always one minute later, 0.460)."""
    real = _columns(T.text("T3", 6000, 1))
    zone = inside_dates.build_zone(real, PERSON, skip=_skip("T3"))
    twin = inside_dates.write_dates(zone, 6000, people=real[PERSON], given=real, seed=1)
    reading = _reading(zone, "charted_at")
    minutes: "list[int]" = []
    for cell, device in zip(twin["charted_at"], real["device"]):
        moment = inside_dates.moment_of(cell, reading) if cell else None
        if moment is not None and device == "Y":
            minutes += [moment[1] // 60 % 60]
    off = [minute for minute in minutes if minute % 5]
    assert len(off) > 1000
    assert sum(1 for minute in off if minute % 5 == 1) <= 0.32 * len(off)


# -- the version -----------------------------------------------------------------------------------------------------


def test_the_writer_refuses_a_zone_of_version_2() -> None:
    """A version 2 zone (each band's first dates in cells of a few real persons, places on real persons' own
    places) is refused, and the twin keeps the description's dates (mutant: version 2 read)."""
    columns = _columns(T.text("T2", 3000, 1))
    zone = inside_dates.build_zone(columns, T.PERSON["T2"])
    inside_dates.write_dates(zone, 100, seed=0)
    older = dict(zone, version=2)
    with pytest.raises(inside_dates.DatesError):
        inside_dates.write_dates(older, 100, seed=0)


# -- through the commands: lane IN-1's checks on the charting twin ----------------------------------------------------


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def test_the_charting_twin_drawn_through_the_commands_passes_c2_and_c4(tmp_path: pathlib.Path) -> None:
    """Route S at 20,000 rows, table seed 1 (where the version 2 zone's twin used 1.25 of C2's allowance and 1.57 of
    C4's on its minute stamps): every check passes, C2 and C4 among them (mutant: every census its own counts)."""
    folder = tmp_path / "product"
    text = T.text("T3", ROWS, 1)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        product = B.make_twins(folder, "T3", text, (0,), False)
    assert not product.errors, product.errors
    records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1
    record = json.loads(records[0].read_text(encoding="utf-8").split("\n", 1)[1])
    assert record["zones"]["dates"]["version"] == 3
    real_path, twin_path = tmp_path / "real.csv", tmp_path / "twin.csv"
    real_path.write_text(text, encoding="utf-8", newline="\n")
    twin_path.write_text(product.twins[0], encoding="utf-8", newline="\n")
    outcome = twin_checks.run_checks(str(real_path), str(twin_path), person=PERSON)
    by_code = {check.code: check for check in outcome.checks}
    for code in ("C1", "C2", "C3", "C4", "C5"):
        assert by_code[code].passed, twin_checks.report_lines(outcome)

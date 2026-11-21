"""Gate file of lane IN-5: the dates zone of the inside record and the writer of a twin's dates.

THE OWNER'S RULING OF 2026-11-18: a twin's dates keep the real weekday and
time of day, their day of the month is made up, and date analyses (by
weekday, hour, season, month and year; the time between two dates, the time
to an event, the gaps between a person's visits) behave as on the real
table. Each case below pins one clause on the invented tables of the
reliability battery or on a table written here, and each is red on its
mutant (lane IN-5's report names them):

* the zone is a model: no list longer than the gap grid, no cell of the
  table, no person's key, and its size follows columns, never rows;
* the weekday and the clock come back, the five-minute heaping by the label
  that heaps it too;
* the day of the month is made up: a clinic held on each month's first
  Monday writes Mondays across the whole month in the twin;
* a chained date keeps its gap (by a label's level on a minute scale, by
  the reference's weekday on a day scale), a fixed offset stays exact, and
  no later column precedes its reference, nor any column a column it never
  precedes in the table;
* a person's dates keep their gaps and their order and stay inside the
  calendar's months;
* every written form reads back under its own reading, the declared
  counting systems included;
* the generate step's scores order the dates and the gaps they tie;
* the record carries the zone and the same zone and seed write the same
  cells.
"""

from __future__ import annotations

import csv
import datetime
import io
import json
import pathlib
import random
import typing

import reliability_tables as T
from synthtwin import inside, inside_dates, installation

# The battery's person column (one name for every table that has one).
PERSON = T.PERSON["T2"]


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    header, body = rows[0], rows[1:]
    return {name: [row[i] for row in body] for i, name in enumerate(header)}


def _skip(table: str) -> "tuple[str, ...]":
    return tuple(name for name, known in T.KNOWS[table].items() if known == "identifier" and name != T.PERSON[table])


def _battery(table: str, rows: int, seed: int = 1) -> "tuple[dict[str, list[str]], dict[str, object]]":
    columns = _columns(T.text(table, rows, seed))
    return columns, inside_dates.build_zone(columns, T.PERSON[table], skip=_skip(table))


def _moments(cells: "list[str]", zone: "dict[str, object]", name: str) -> "list[tuple[int, int] | None]":
    entry = zone["columns"][name]  # type: ignore[index]
    reading = inside_dates.Reading(entry["reading"]["kind"], entry["reading"]["member"])
    return [inside_dates.moment_of(cell, reading) for cell in cells]


def _share(values: "list[bool]") -> float:
    return sum(1 for value in values if value) / max(1, len(values))


def _lists(value: object) -> "list[int]":
    if isinstance(value, list):
        return [len(value)] + [n for item in value for n in _lists(item)]
    if isinstance(value, dict):
        return [n for item in value.values() for n in _lists(item)]
    return []


def _quantile(values: "list[float]", p: float) -> float:
    ordered = sorted(values)
    return ordered[int(p * (len(ordered) - 1))]


# -- the zone is a model ------------------------------------------------------------------------------


def test_the_zone_holds_no_cell_no_key_and_no_long_list() -> None:
    """No list longer than the gap grid, no cell of a date column as written, no person's key."""
    for table in ("T2", "T4"):
        columns, zone = _battery(table, 4000)
        written = json.dumps(zone, sort_keys=True)
        assert max(_lists(zone)) <= inside_dates.GAP_GRID
        for name in zone["order"]:  # type: ignore[union-attr]
            for cell in sorted(set(columns[name]))[:400]:
                assert cell not in written, f"{table}: a cell of {name} is in the zone"
        for key in sorted(set(columns[PERSON]))[:400]:
            assert key not in written, f"{table}: a person's key is in the zone"


def test_the_zone_s_size_follows_columns_never_rows() -> None:
    """Shares per million and fixed grids: doubling the rows moves the zone by under 5 per cent."""
    for table in ("T3", "T4"):
        sizes = []
        for rows in (20_000, 40_000):
            _columns_, zone = _battery(table, rows)
            sizes += [len(json.dumps(zone, sort_keys=True, separators=(",", ":")))]
        assert sizes[1] <= 1.05 * sizes[0], f"{table}: {sizes[0]} bytes at 20,000 rows, {sizes[1]} at 40,000"


# -- the weekday, the clock and the made-up day -----------------------------------------------------


def test_the_weekday_and_the_clock_come_back() -> None:
    """Cases: the weekend share, the 07:30 first slot and the hours; admissions: the weekday shares."""
    columns, zone = _battery("T4", 6000)
    twin = inside_dates.write_dates(zone, 6000, people=columns[PERSON], given=columns, seed=2)
    real_m = [m for m in _moments(columns["sched_start"], zone, "sched_start") if m is not None]
    twin_m = [m for m in _moments(twin["sched_start"], zone, "sched_start") if m is not None]
    assert len(twin_m) == len(twin["sched_start"])

    def weekend(ms: "list[tuple[int, int]]") -> float:
        return _share([inside_dates.weekday(day) >= 5 for day, _second in ms])

    def first_slot(ms: "list[tuple[int, int]]") -> float:
        return _share([second == 7 * 3600 + 30 * 60 for _day, second in ms])

    assert abs(weekend(twin_m) - weekend(real_m)) <= 0.02
    assert abs(first_slot(twin_m) - first_slot(real_m)) <= 0.03
    for hour in range(24):
        assert abs(_share([s // 3600 == hour for _d, s in twin_m]) - _share([s // 3600 == hour for _d, s in real_m])) <= 0.03
    cohort, cohort_zone = _battery("T1", 6000)
    made = inside_dates.write_dates(cohort_zone, 6000, given=cohort, seed=2)
    admitted = typing.cast("list[str]", cohort_zone["order"])[0]
    real_days = [m[0] for m in _moments(cohort[admitted], cohort_zone, admitted) if m is not None]
    twin_days = [m[0] for m in _moments(made[admitted], cohort_zone, admitted) if m is not None]
    for day in range(7):
        real = _share([inside_dates.weekday(d) == day for d in real_days])
        assert abs(_share([inside_dates.weekday(d) == day for d in twin_days]) - real) <= 0.025


def _first_mondays(rows: int, seed: int) -> "dict[str, list[str]]":
    """A clinic held on the first Monday of each month, 2022 to 2024, a quarter of its visits in the morning slot."""
    r = random.Random(seed)
    days = []
    for year in (2022, 2023, 2024):
        for month in range(1, 13):
            day = datetime.date(year, month, 1)
            while day.weekday() != 0:
                day = day + datetime.timedelta(days=1)
            days += [day]
    cells = []
    for _ in range(rows):
        day = r.choice(days)
        cells += [f"{day.isoformat()} {'08:00' if r.random() < 0.25 else f'{r.randrange(9, 17):02d}:{r.choice((0, 30)):02d}'}"]
    return {"seen_at": cells, "room": [r.choice(("A", "B")) for _ in range(rows)]}


def test_the_day_of_the_month_is_made_up() -> None:
    """Every real visit is on a first Monday: the twin's are Mondays, spread over the month's Mondays."""
    columns = _first_mondays(3000, 4)
    zone = inside_dates.build_zone(columns)
    twin = inside_dates.write_dates(zone, 3000, given=columns, seed=1)
    moments = [m for m in _moments(twin["seen_at"], zone, "seen_at") if m is not None]
    assert len(moments) == 3000
    assert all(inside_dates.weekday(day) == 0 for day, _second in moments)
    first = _share([(datetime.date(1970, 1, 1) + datetime.timedelta(days=day)).day <= 7 for day, _second in moments])
    assert first <= 0.40, f"{first:.2f} of the twin's visits fall on a first Monday, as every real one does"
    months = {(datetime.date(1970, 1, 1) + datetime.timedelta(days=day)).strftime("%Y-%m") for day, _s in moments}
    assert len(months) == 36
    assert abs(_share([second == 8 * 3600 for _d, second in moments]) - 0.25) <= 0.04


# -- chains ----------------------------------------------------------------------------------------------


def test_a_chained_date_keeps_its_gap_its_level_and_its_order() -> None:
    """Cases: the delay, the duration by service, the fixed offset of the second clock; nothing before its reference."""
    columns, zone = _battery("T4", 6000)
    twin = inside_dates.write_dates(zone, 6000, people=columns[PERSON], given=columns, seed=3)

    def minutes(side: "dict[str, list[str]]", late: str, early: str) -> "list[float | None]":
        a, b = _moments(side[late], zone, late), _moments(side[early], zone, early)
        return [None if x is None or y is None else ((x[0] - y[0]) * 86400 + x[1] - y[1]) / 60.0 for x, y in zip(a, b)]

    offset = minutes(twin, "in_room_utc", "in_room")
    assert offset and all(gap == 360.0 for gap in offset if gap is not None)
    for late, early in (("incision", "in_room"), ("close", "incision"), ("out_room", "close")):
        assert min(gap for gap in minutes(twin, late, early) if gap is not None) >= 0
    real_close = minutes(columns, "close", "in_room")
    twin_close = minutes(twin, "close", "in_room")
    for service in ("GEN", "ORTHO", "CARD", "SPINE"):
        real = [g for g, s in zip(real_close, columns["service"]) if s == service and g is not None]
        mine = [g for g, s in zip(twin_close, columns["service"]) if s == service and g is not None]
        assert abs(_quantile(mine, 0.5) - _quantile(real, 0.5)) <= 0.08 * _quantile(real, 0.5), service
    real_delay = [g for g in minutes(columns, "in_room", "sched_start") if g is not None]
    twin_delay = [g for g in minutes(twin, "in_room", "sched_start") if g is not None]
    for p in (0.1, 0.5, 0.9):
        assert abs(_quantile(twin_delay, p) - _quantile(real_delay, p)) <= 2.0


def _stays(rows: int, seed: int) -> "dict[str, list[str]]":
    """Admissions on weekdays; stays longer from a Thursday or a Friday; no one leaves on a Sunday."""
    r = random.Random(seed)
    admitted, left = [], []
    for _ in range(rows):
        day = datetime.date(2023, 1, 2) + datetime.timedelta(days=r.randrange(700))
        while day.weekday() >= 5:
            day = day + datetime.timedelta(days=1)
        nights = r.choice((1, 2, 2, 3, 3, 4, 5, 7)) + (3 if day.weekday() >= 3 else 0)
        out = day + datetime.timedelta(days=nights)
        if out.weekday() == 6:
            out = out + datetime.timedelta(days=1)
        admitted += [f"{day.isoformat()} {r.randrange(7, 20):02d}:{r.randrange(60):02d}"]
        left += [f"{out.isoformat()} {r.randrange(10, 15):02d}:{r.randrange(60):02d}"]
    return {"admitted_at": admitted, "left_at": left}


def test_a_day_scale_gap_keeps_the_weekday_the_later_date_falls_on() -> None:
    """No one leaves on a Sunday in the twin either, and the stay in days keeps its quantiles."""
    columns = _stays(4000, 7)
    zone = inside_dates.build_zone(columns)
    assert zone["columns"]["left_at"]["chain"]["scale"] == "day"  # type: ignore[index]
    twin = inside_dates.write_dates(zone, 4000, seed=2)
    left = [m for m in _moments(twin["left_at"], zone, "left_at") if m is not None]
    assert _share([inside_dates.weekday(day) == 6 for day, _second in left]) <= 0.005
    assert all(10 <= second // 3600 < 15 for _day, second in left)

    def stays(side: "dict[str, list[str]]") -> "list[float]":
        a, b = _moments(side["left_at"], zone, "left_at"), _moments(side["admitted_at"], zone, "admitted_at")
        return [float(x[0] - y[0]) for x, y in zip(a, b) if x is not None and y is not None]

    for p in (0.1, 0.5, 0.9):
        assert abs(_quantile(stays(twin), p) - _quantile(stays(columns), p)) <= 1.0


def _steps(rows: int, seed: int) -> "dict[str, list[str]]":
    """Three steps of a row: the second up to 100 minutes after the first, the third after the second, always,
    but nearer in spread to the first (it falls 95 to 105 minutes after it unless the second ran later)."""
    r = random.Random(seed)
    out: "dict[str, list[str]]" = {"called_at": [], "seen_at": [], "closed_at": []}
    for _ in range(rows):
        start = datetime.datetime(2023, 1, 2, 8, 0) + datetime.timedelta(days=r.randrange(500), minutes=r.randrange(480))
        seen = r.randrange(0, 101)
        closed = max(seen + 1, 95 + r.randrange(0, 11))
        for name, minutes in (("called_at", 0), ("seen_at", seen), ("closed_at", closed)):
            out[name] += [(start + datetime.timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M")]
    return out


def test_every_ordering_the_table_keeps_holds_in_the_twin() -> None:
    """The third step chains to the first (its tighter gap), yet it never comes before the second in the twin."""
    columns = _steps(3000, 2)
    zone = inside_dates.build_zone(columns)
    assert zone["columns"]["closed_at"]["chain"]["reference"] == "called_at"  # type: ignore[index]
    assert ["seen_at", "closed_at"] in zone["orders"]  # type: ignore[operator]
    twin = inside_dates.write_dates(zone, 3000, seed=6)
    seen, closed = _moments(twin["seen_at"], zone, "seen_at"), _moments(twin["closed_at"], zone, "closed_at")
    broken = sum(1 for a, b in zip(seen, closed) if a is not None and b is not None and (b[0], b[1]) < (a[0], a[1]))
    assert broken == 0


# -- a person's dates --------------------------------------------------------------------------------------


def test_a_person_s_dates_keep_their_gaps_their_order_and_the_calendar() -> None:
    """Visits: the gaps between a person's visits keep their quantiles, come in order and stay in the months."""
    columns, zone = _battery("T2", 6000)
    twin = inside_dates.write_dates(zone, 6000, people=columns[PERSON], given=columns, seed=5)

    def gaps(side: "dict[str, list[str]]") -> "tuple[list[float], int]":
        by: "dict[str, list[int]]" = {}
        out_of_order = 0
        for person, m in zip(columns[PERSON], _moments(side["visit_date"], zone, "visit_date")):
            if m is None:
                continue
            if person in by and m[0] < by[person][-1]:
                out_of_order += 1
            by.setdefault(person, []).append(m[0])
        found = [float(b - a) for days in by.values() for a, b in zip(sorted(days), sorted(days)[1:])]
        return found, out_of_order

    real, _unordered = gaps(columns)
    mine, unordered = gaps(twin)
    assert unordered == 0
    for p in (0.1, 0.5, 0.9):
        assert abs(_quantile(mine, p) - _quantile(real, p)) <= 1.0
    months = {cell[:7] for cell in columns["visit_date"] if cell}
    assert {cell[:7] for cell in twin["visit_date"] if cell} <= months


def test_the_label_that_heaps_the_minutes_heaps_them_in_the_twin() -> None:
    """Charting: hand-typed rows on five-minute marks, device rows at any minute, in the twin as in the table."""
    columns, zone = _battery("T3", 6000)
    assert zone["columns"]["charted_at"]["clock"]["by"] == "device"  # type: ignore[index]
    twin = inside_dates.write_dates(zone, 6000, people=columns[PERSON], given=columns, seed=1)
    for level in ("Y", "N"):
        def marks(side: "dict[str, list[str]]") -> float:
            found = [m[1] for m, d in zip(_moments(side["charted_at"], zone, "charted_at"), columns["device"])
                     if m is not None and d == level]
            return _share([(second // 60) % 5 == 0 for second in found])
        assert abs(marks(twin) - marks(columns)) <= 0.05, level


# -- forms, ranks, the record --------------------------------------------------------------------------


def _forms(rows: int, seed: int) -> "dict[str, list[str]]":
    r = random.Random(seed)
    cols: "dict[str, list[str]]" = {k: [] for k in ("stamp", "us", "textual", "serial", "seconds", "day_1960", "day_1840")}
    for _ in range(rows):
        day = datetime.date(2021, 1, 4) + datetime.timedelta(days=r.randrange(800))
        if day.weekday() == 6:
            day = day + datetime.timedelta(days=1)
        moment = datetime.datetime(day.year, day.month, day.day, r.randrange(7, 19), r.randrange(60), r.randrange(60))
        cols["stamp"] += [moment.strftime("%Y-%m-%dT%H:%M:%S") + f".{r.randrange(1000):03d}+02:00"]
        hour = moment.hour % 12 or 12
        cols["us"] += [f"{moment.month:02d}/{moment.day:02d}/{moment.year} {hour}:{moment.minute:02d} "
                       f"{'PM' if moment.hour >= 12 else 'AM'}"]
        cols["textual"] += [f"{moment.day} {moment.strftime('%b')} {moment.year}"]
        cols["serial"] += [f"{(moment - datetime.datetime(1899, 12, 30)).total_seconds() / 86400:.4f}"]
        cols["seconds"] += [f"{int((moment - datetime.datetime(1970, 1, 1)).total_seconds())}"]
        cols["day_1960"] += [f"{(day - datetime.date(1960, 1, 1)).days}"]
        cols["day_1840"] += [f"{(day - datetime.date(1840, 12, 31)).days}.{r.randrange(1, 30)}"]
    return cols


def test_every_written_form_reads_back_under_its_own_reading() -> None:
    """Text members and declared counting systems: every twin cell reads back, no Sunday is written, widths kept."""
    columns = _forms(2000, 3)
    readings = {"serial": "excel-1900", "seconds": "seconds-since-1970", "day_1960": "days-since-1960",
                "day_1840": "days-since-1840"}
    zone = inside_dates.build_zone(columns, readings=readings)
    assert set(zone["columns"]) == set(columns)  # type: ignore[arg-type]
    twin = inside_dates.write_dates(zone, 2000, seed=9)
    for name in columns:
        moments = _moments(twin[name], zone, name)
        assert all(m is not None for m in moments), name
        assert _share([inside_dates.weekday(m[0]) == 6 for m in moments if m is not None]) == 0.0, name
    assert all(cell[0] != "0" for cell in twin["textual"]), "a day the table writes unpadded is written padded"
    assert all(cell[len(cell) - 6:] == "+02:00" and cell[10] == "T" for cell in twin["stamp"])
    assert all("." in cell for cell in twin["day_1840"])


def _rank_correlation(xs: "list[float]", ys: "list[float]") -> float:
    """Spearman's correlation: the correlation of the two lists' ranks (ties in order of place)."""
    def ranks(values: "list[float]") -> "list[float]":
        order = sorted(range(len(values)), key=lambda k: (values[k], k))
        out = [0.0] * len(values)
        for place, k in enumerate(order):
            out[k] = float(place)
        return out
    a, b = ranks(xs), ranks(ys)
    mean = (len(a) - 1) / 2.0
    num = sum((x - mean) * (y - mean) for x, y in zip(a, b))
    den = sum((x - mean) ** 2 for x in a)
    return num / den


def test_the_generate_step_s_scores_order_the_dates_and_the_gaps() -> None:
    """The order of the scores is the order of the first dates, and of the gaps of each cell of the chain."""
    columns = _stays(3000, 11)
    zone = inside_dates.build_zone(columns)
    scores = {"admitted_at": [float(k) for k in range(3000)], "left_at": [float(k) for k in range(3000)]}
    twin = inside_dates.write_dates(zone, 3000, scores=scores, present={"admitted_at": [True] * 3000,
                                                                        "left_at": [True] * 3000}, seed=1)
    admitted = _moments(twin["admitted_at"], zone, "admitted_at")
    days = [float(m[0]) for m in admitted if m is not None]
    assert _rank_correlation([float(k) for k in range(3000)], days) >= 0.98
    left = _moments(twin["left_at"], zone, "left_at")
    by_weekday: "dict[int, list[tuple[float, float]]]" = {}
    for k, (a, b) in enumerate(zip(admitted, left)):
        if a is not None and b is not None:
            by_weekday.setdefault(inside_dates.weekday(a[0]), []).append((float(k), float(b[0] - a[0])))
    for pairs in by_weekday.values():
        assert _rank_correlation([x for x, _y in pairs], [y for _x, y in pairs]) >= 0.9


def test_dates_among_other_values_are_made_up_and_the_rest_kept() -> None:
    """A result column of numbers and some dates: every date the twin's cells hold is made up, every number kept."""
    r = random.Random(8)
    cells = []
    for _ in range(4000):
        if r.random() < 0.08:
            day = datetime.date(2022, 1, 3) + datetime.timedelta(days=r.randrange(600))
            cells += [day.isoformat() if day.weekday() < 5 else (day + datetime.timedelta(days=2)).isoformat()]
        else:
            cells += [f"{r.uniform(1, 400):.1f}"]
    zone = inside_dates.build_zone({"result": cells, "unit": [r.choice(("g/L", "U/L")) for _ in cells]})
    assert "result" not in zone["columns"] and "result" in zone["mixed"]  # type: ignore[operator]
    written = inside_dates.rewrite_mixed(zone, "result", cells, seed=3)
    dated = [k for k, cell in enumerate(cells) if cell[4:5] == "-"]
    assert all(written[k][4:5] == "-" for k in dated)
    assert all(written[k] == cells[k] for k in range(len(cells)) if k not in set(dated))
    kept = sum(1 for k in dated if written[k] == cells[k])
    assert kept <= 0.02 * len(dated), f"{kept} of {len(dated)} rows keep their real date"
    assert all(datetime.date.fromisoformat(written[k]).weekday() < 5 for k in dated)


def test_the_record_carries_the_zone_and_the_writer_repeats_itself(tmp_path: pathlib.Path) -> None:
    """The zone sits beside the marginals, the record loads, and the same zone and seed write the same cells."""
    columns, _zone = _battery("T2", 3000)
    record = inside_dates.add_zone(inside.build_record(columns, (PERSON,)), columns, PERSON)
    home = pathlib.Path(tmp_path, "home")
    places = inside.Places(pathlib.Path(home, "data", "synthtwin", "inside"), (pathlib.Path(tmp_path, "tmp"),),
                           (pathlib.Path(home, "Downloads"),), installation.system_name(), ())
    target = inside.record_path("visits", places)
    inside.write_record(record, target, places)
    loaded = inside.load_record(target)
    zones = loaded["zones"]
    assert isinstance(zones, dict) and set(zones) == {"marginals", inside_dates.ZONE}
    zone = zones[inside_dates.ZONE]
    one = inside_dates.write_dates(zone, 3000, people=columns[PERSON], seed=4)
    two = inside_dates.write_dates(zone, 3000, people=columns[PERSON], seed=4)
    other = inside_dates.write_dates(zone, 3000, people=columns[PERSON], seed=5)
    assert one == two and one != other

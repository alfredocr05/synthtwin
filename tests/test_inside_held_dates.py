"""Dates the description holds are made up on the route that writes the inside record (lane ZOO-Y, plan P4-D517).

A column whose cells read as dates beside other values -- Excel days,
ISO dates beside two impossible placeholders -- has those dates read as
blank cells while the Safe Harbor question about them is open or
answered `yes` (plan P4-D446), in the description and on the twin.
MEASURED (lane ZOO-X's data-type zoo, 20,000 rows, the floor on, the
shipped route): a column of Excel days answered `yes` came back 20,000
blank, and a column of ISO dates beside `2023-02-30` and `0000-00-00`
left unanswered 19,598 blank -- the column gone for any analysis, where
the owner's ruling of 2026-11-18 lets the twin hold made-up dates (the
real weekday and clock, the day of the month made up).

The dates zone now counts such a column (`inside_dates.Census.held`)
and `inside_dates.fill_held` writes, on as many of the twin's blank
cells as the real column held dates, a made-up date in the column's own
spelling: a count in its own places, a date as text in its own form.
The tables are invented here, drawn from their seeds.
"""

from __future__ import annotations

import datetime
import random

from synthtwin import inside_dates

EXCEL_NOUGHT = datetime.datetime(1899, 12, 30)
ROWS = 3000


def _moments(seed: int) -> "list[datetime.datetime]":
    draw = random.Random(seed)
    found = []
    for _row in range(ROWS):
        day = datetime.date(2021, 1, 1) + datetime.timedelta(days=draw.randint(0, 900))
        # Weekdays only, office hours: a pattern the made-up dates must keep.
        while day.weekday() >= 5:
            day = day + datetime.timedelta(days=1)
        found += [datetime.datetime.combine(day, datetime.time(draw.randint(8, 16), draw.randint(0, 59)))]
    return found


def _excel(moment: datetime.datetime) -> str:
    return f"{(moment - EXCEL_NOUGHT).total_seconds() / 86400:.4f}"


def test_a_held_column_of_excel_days_is_written_as_made_up_counts_on_its_blank_rows() -> None:
    real = [_excel(moment) for moment in _moments(3)]
    zone = inside_dates.build_zone({"serial": real}, declared_only=True, held=("serial",))
    assert inside_dates.held_columns(zone) == ("serial",)
    twin_blank = [""] * ROWS
    made = inside_dates.fill_held(zone, "serial", twin_blank, seed=1)
    assert made is not None and all(made), "every real cell was a date, so every blank cell takes one"
    for cell in made:
        whole, point, places = cell.partition(".")
        assert point and len(places) == 4 and len(whole) == 5, cell
        moment = EXCEL_NOUGHT + datetime.timedelta(days=float(cell))
        assert moment.weekday() < 5, cell
        assert 7 <= moment.hour <= 17, cell
    span = sorted(float(cell) for cell in real)
    assert span[0] - 31 <= min(float(cell) for cell in made) and max(float(cell) for cell in made) <= span[-1] + 31


def test_a_held_column_of_dates_beside_placeholders_keeps_the_placeholders() -> None:
    draw = random.Random(5)
    real = [f"{moment:%Y-%m-%d}" if draw.random() > 0.02 else draw.choice(("2023-02-30", "0000-00-00"))
            for moment in _moments(4)]
    zone = inside_dates.build_zone({"seen_on": real}, declared_only=True, held=("seen_on",))
    # The description's twin: the placeholders where it writes them, blank where the real dates were.
    twin = [cell if cell in ("2023-02-30", "0000-00-00") else "" for cell in real]
    made = inside_dates.fill_held(zone, "seen_on", twin, seed=2)
    assert made is not None
    dated = sum(1 for cell in real if cell not in ("2023-02-30", "0000-00-00"))
    assert sum(1 for cell in made if cell and cell not in ("2023-02-30", "0000-00-00")) == dated
    assert [cell for cell in made if cell in ("2023-02-30", "0000-00-00")] == [
        cell for cell in twin if cell in ("2023-02-30", "0000-00-00")]
    for cell in made:
        if cell not in ("2023-02-30", "0000-00-00"):
            assert datetime.datetime.strptime(cell, "%Y-%m-%d").weekday() < 5, cell


def test_a_column_the_description_does_not_hold_is_not_filled() -> None:
    """The same cells, no hold named: the zone counts no held column, and the filler writes nothing (the mutant)."""
    real = [_excel(moment) for moment in _moments(3)]
    zone = inside_dates.build_zone({"serial": real}, declared_only=True)
    assert inside_dates.held_columns(zone) == ()
    assert inside_dates.fill_held(zone, "serial", [""] * ROWS, seed=1) is None


def test_the_filled_dates_are_a_function_of_the_seed() -> None:
    real = [_excel(moment) for moment in _moments(3)]
    zone = inside_dates.build_zone({"serial": real}, declared_only=True, held=("serial",))
    one = inside_dates.fill_held(zone, "serial", [""] * ROWS, seed=1)
    assert one == inside_dates.fill_held(zone, "serial", [""] * ROWS, seed=1)
    assert one != inside_dates.fill_held(zone, "serial", [""] * ROWS, seed=2)


def test_the_command_names_the_held_columns_by_their_remark_and_the_zone_by_its_mark() -> None:
    """`cli._inside_dated_held` reads the description's remark; `cli._held_dates_filled` the zone's `held` mark."""
    from synthtwin import cli, taxonomy

    remark = taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    published = {"columns": [{"name": "serial", "remarks": [remark]}, {"name": "visit_on", "remarks": []},
                             {"name": "other"}]}
    assert cli._inside_dated_held(published) == ("serial",)
    real = [_excel(moment) for moment in _moments(3)]
    zone = inside_dates.build_zone({"serial": real}, declared_only=True, held=("serial",))
    assert cli._held_dates_filled({"dates": zone}) == {"serial"}
    assert cli._held_dates_filled({"dates": inside_dates.build_zone({"serial": real}, declared_only=True)}) == set()


def test_no_made_up_date_falls_in_a_year_at_or_before_the_year_cut() -> None:
    """Birth dates held beside a placeholder, half of them in 1930: no twin date in 1937 or earlier (batch 4z's fix round).

    The outside review of batch 4z, item 3: a column of birth dates, a few
    of them in 1930, beside `pending` placeholders reached the held-dates
    route, and the calendar the zone keeps gave the twin six dates in 1930
    -- a year that shows an age over 89 in this release's reference year.
    A date drawn in such a year is not written; its cell stays blank, as
    the description wrote it. A count column (Excel days) is held the same.
    """
    from synthtwin import taxonomy

    cut = taxonomy.year_cutoff(taxonomy.SAFE_HARBOR_REFERENCE_YEAR)
    draw = random.Random(9)
    real = []
    for row in range(ROWS):
        if row % 10 == 0:
            real += ["pending"]
            continue
        year = 1930 if row % 2 else 1970
        real += [f"{datetime.date(year, 1, 1) + datetime.timedelta(days=draw.randint(0, 360)):%Y-%m-%d}"]
    zone = inside_dates.build_zone({"birth_date": real}, declared_only=True, held=("birth_date",))
    twin = [cell if cell == "pending" else "" for cell in real]
    made = inside_dates.fill_held(zone, "birth_date", twin, seed=1)
    assert made is not None
    years = [int(cell[:4]) for cell in made if cell and cell != "pending"]
    assert years and min(years) > cut, min(years)
    assert [cell for cell in made if cell == "pending"] == [cell for cell in twin if cell == "pending"]
    # About half the real dates are in 1930, so about half the cells the twin would date stay blank.
    assert 0.3 * len(twin) < sum(1 for cell in made if not cell) < 0.7 * len(twin)
    counted = [_excel(datetime.datetime.strptime(cell, "%Y-%m-%d")) if cell != "pending" else "" for cell in real]
    zone = inside_dates.build_zone({"serial": counted}, declared_only=True, held=("serial",))
    made = inside_dates.fill_held(zone, "serial", [""] * ROWS, seed=1)
    assert made is not None
    for cell in made:
        if cell:
            assert (EXCEL_NOUGHT + datetime.timedelta(days=float(cell))).year > cut, cell

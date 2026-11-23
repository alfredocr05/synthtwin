"""A twin's dates are written as their column writes them, hour and month name too (lane ZOO-X).

Measured by the data-type zoo (`tests/types_zoo.py`, the typed_dates
table at 20,000 rows, the shipped route, its inside record written): a
column of 12-hour stamps written with the hour as it falls (`8:52 AM`,
`11:17 AM`) came back with 13,847 of 20,000 cells at two figures of hour
(`04:02 PM`), and a column of dates with the month's whole name (`March
5, 2023`) came back with June written `Jun`. A cell whose hour is ten or
past shows no hour width, and a cell in May shows no length of a month's
name; the dates zone keyed such a cell at two figures and at the
`either` length, and the twin wrote every moment dealt that key so.
`inside_dates._resolved_keys` now gives such a key the width, or the
length, the column's other cells show. Each test below is red on the
mutant that returns the keys unresolved.
"""

from __future__ import annotations

import random
import re

from synthtwin import inside_dates


def _keys(cells: "list[str]") -> "list[list[object] | None]":
    reading = inside_dates.reading_of(cells)
    assert reading is not None
    return inside_dates._resolved_keys([inside_dates._spelling_shown(cell, reading) for cell in cells])


def test_a_clock_whose_hour_shows_no_width_takes_the_width_its_column_shows() -> None:
    twelve = _keys(["3/5/2021 8:52 AM", "3/5/2021 11:17 AM", "3/5/2021 12:05 PM", "3/5/2021 1:05 PM"])
    assert [key[3] for key in twelve if key is not None] == ["h-mm AM-PM"] * 4
    day = _keys(["3/5/2021 8:22", "3/5/2021 14:22", "3/5/2021 23:59"])
    assert [key[3] for key in day if key is not None] == ["h-mm"] * 3


def test_a_column_that_pads_its_hour_and_one_that_shows_no_width_keep_their_keys() -> None:
    padded = _keys(["2021-03-05 08:22:10", "2021-03-05 14:22:10", "2021-03-05 23:00:01"])
    assert [key[3] for key in padded if key is not None] == ["hh-mm-ss"] * 3
    late = _keys(["3/5/2021 10:52 AM", "3/5/2021 11:17 AM"])
    assert [key[3] for key in late if key is not None] == ["hh-mm AM-PM"] * 2


def test_may_takes_the_length_of_its_column_s_other_months() -> None:
    full = _keys(["March 5, 2023", "May 5, 2023", "June 1, 2022"])
    assert [key[1] for key in full if key is not None] == ["title-full-space-comma"] * 3
    short = _keys(["Mar 5, 2023", "May 5, 2023", "Jun 1, 2022"])
    assert {f"{key[1]}" for key in short if key is not None} == {"title-abbreviated-space-comma"}
    alone = _keys(["May 5, 2023", "May 9, 2023"])
    assert {f"{key[1]}" for key in alone if key is not None} == {"title-either-space-comma"}


def _stamps(count: int) -> "list[str]":
    draw = random.Random(5)
    out = []
    for _ in range(count):
        hour = draw.randint(0, 23)
        shown = hour % 12 or 12
        out += [f"{draw.randint(1, 12)}/{draw.randint(1, 28)}/2021 {shown}:{draw.randint(0, 59):02d} {'AM' if hour < 12 else 'PM'}"]
    return out


def test_the_twin_of_a_column_of_unpadded_hours_writes_no_padded_hour() -> None:
    cells = _stamps(3000)
    zone = inside_dates.build_zone({"seen_at": cells})
    written = inside_dates.write_dates(zone, 3000, seed=3)["seen_at"]
    padded = [cell for cell in written if re.search(r" 0\d:\d\d [AP]M$", cell)]
    assert written and not padded, padded[:5]
    months = [f"{name} {day}, 2023" for name in ("March", "May", "June", "July") for day in range(1, 29)] * 20
    zone = inside_dates.build_zone({"seen_on": months})
    written = inside_dates.write_dates(zone, len(months), seed=3)["seen_on"]
    short = [cell for cell in written if re.match(r"(Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec) ", cell)]
    assert written and not short, short[:5]

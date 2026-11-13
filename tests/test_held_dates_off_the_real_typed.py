"""P4-D457 (lane ID-ROOM2), repair 2: columns held with `--identifier` (the date pass), at 20,000 rows.

The verify of repair 1 (LANE ID-ROOM2 RULINGS 6 (3)) found NF136 -- "code that reads the column as dates runs on
the twin" -- published over twin cells that are no dates on the commonest route a birth date is held by: ISO
dates beside hourly stamps (S12: 19,600 of 20,000 cells stamps the date pass does not write), month-first births
beside three withheld unpadded layouts (W: the 12 withheld values left as the walk wrote them) and diagnosis
dates of which one in twenty is a year alone (D3: 1,008 cells of figures alone written as eleven-figure
numbers). And the suite of repair 1's head found ISO and month-first births held with `--identifier` written
as record numbers, every cell: the block that the month-first layout's 144 dates a year asked reached 2119,
which a month-first `02/01/1955` names read year first. Each case runs as tests/test_held_dates_off_the_real_widths.py's
do, is red on af60db46 and on the mutant its docstring names (wave6/ID-ROOM2/r2/mutants.log). The last case, from
K-HZ-13's proof on batch 4q's head b93f128a (the same births at 200,000 rows written as record numbers, the ISO
layout's share past 2100), is red there.
"""

from __future__ import annotations

import datetime
import pathlib
import random

import test_held_dates_off_the_real_widths as widths

ROWS = widths.ROWS
NF136_SAID = "code that reads the column as dates runs on the twin"


def _said(block: "dict[str, object]") -> str:
    return " ".join(f"{remark}" for remark in block.get("remarks") or [])


def test_s12_a_column_naming_a_stamp_publishes_no_room(tmp_path: pathlib.Path) -> None:
    """S12: 1,200 values from 1900, every fiftieth an ISO date and the others hourly ISO stamps, with
    `--identifier`: af60db46 published `[[2028, 2030]]` and NF136 while 19,600 cells are stamps the date pass
    leaves as the walk wrote them. The column now publishes `[]` and no remark saying its cells are dates; no
    twin cell names a real day. Mutant M18 (the stamp's layout not looked at).
    """
    start = datetime.datetime(1900, 1, 1)
    values = []
    for place in range(1200):
        at = start + datetime.timedelta(hours=place)
        values += [at.strftime("%Y-%m-%d") if place % 50 == 0 else at.strftime("%Y-%m-%dT%H:%M:%S")]
    seen = widths._run(tmp_path, [values[place % 1200] for place in range(ROWS)], ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert seen["block"]["made_up_years"] == []  # type: ignore[index]
    assert NF136_SAID not in _said(seen["block"])  # type: ignore[arg-type]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def test_w_the_cells_not_dates_are_the_withheld_layouts_values(tmp_path: pathlib.Path) -> None:
    """W: month-first births, padded, beside four each of `M/D/YYYY`, `M/DD/YYYY` and `MM/D/YYYY` (the census
    withholds the twelve), with `--identifier`: the twelve withheld values are the walk's, as on af60db46, and
    NF136 now names them -- values of a layout too rare to be named, which the twin may write as a record number
    (writing them as dates on the date pass is carried to lane ID-ROOM3) -- while every other cell is a date and
    none names a real day.
    """
    draw = random.Random(7)
    cells = []
    for _place in range(4):
        day = widths._day(draw, 1930, 1999, 9)
        cells += [f"{day.month % 9 + 1}/{day.day}/{day.year}"]
        day = widths._day(draw, 1930, 1999)
        cells += [f"{day.month % 9 + 1}/{10 + day.day % 19}/{day.year}"]
        day = widths._day(draw, 1930, 1999, 9)
        cells += [f"{10 + day.month % 3:02d}/{day.day}/{day.year}"]
    cells += [widths._day(draw, 1930, 1999).strftime("%m/%d/%Y") for _place in range(ROWS - 12)]
    draw.shuffle(cells)
    seen = widths._run(tmp_path, cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    said = _said(seen["block"])  # type: ignore[arg-type]
    assert NF136_SAID in said and "a layout too rare for this description to name" in said, said
    assert "carries the column's longest length" in said, said
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0
    undated = [cell for cell in seen["twin"] if not widths._days(cell)]  # type: ignore[attr-defined]
    assert len(undated) <= 12, undated[:5]


def test_d3_a_year_alone_is_written_as_a_year(tmp_path: pathlib.Path) -> None:
    """D3: diagnosis dates of 1990 to 2025, four in five a full ISO date, three in twenty a month and year, one in
    twenty a year alone (cells of figures alone the census does not name), with `--identifier`: af60db46 wrote the
    1,008 years alone as eleven-figure numbers under NF136. The date pass now writes them as years of the block,
    which the producer read every cell as: every twin cell a date but the walk's carrier of the longest length,
    which NF136 names; none naming a real day or year. Mutants M19 (no cell read as a year alone) and M20 (the
    year alone not named to the twin's check).
    """
    draw = random.Random(11)
    cells = []
    for _place in range(ROWS):
        day = widths._day(draw, 1990, 2025)
        share = draw.random()
        cells += [day.isoformat() if share < 0.8 else day.strftime("%m/%Y") if share < 0.95 else f"{day.year}"]
    seen = widths._run(tmp_path, cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    assert NF136_SAID in _said(seen["block"])  # type: ignore[arg-type]
    real_years = {cell for cell in cells if len(cell) == 4}
    twin = seen["twin"]
    assert isinstance(twin, list)
    alone = [cell for cell in twin if len(cell) == 4]
    assert alone and all(cell.isdigit() and int(cell) >= 2028 for cell in alone), alone[:5]
    assert not real_years & set(alone)
    # ...save the walk's one value of figures alone at the column's longest length, which carries that length
    # (P4-D442's stated limit (l); NF136 names it): the final pass's number, no date.
    unread = {cell for cell in twin if not (len(cell) == 4 or widths._days(cell) or _a_month(cell))}
    assert len(unread) <= 1 and all(cell.isdigit() for cell in unread), sorted(unread)[:5]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def _a_month(cell: str) -> bool:
    try:
        datetime.datetime.strptime(cell, "%m/%Y")
    except ValueError:
        return False
    return True


def test_iso_and_month_first_births_keep_their_room(tmp_path: pathlib.Path) -> None:
    """The suite's `birth_held` case (tests/test_zoo_held_layouts.py) in a shape of its own: 20,000 births of 1930
    to 1999, three in twenty ISO and the rest month first, with `--identifier`: af60db46 wrote the whole column as
    record numbers (its block, sized by the month-first layout's 144 dates a year, held 2119 and 2101). Each layout
    now takes its own share of the block at the days the date pass writes: every twin cell a date, none naming a
    real day. Mutants M21 (no day cap), M22 (the shares not looked at) and M24 (the whole block a layout).
    """
    draw = random.Random(1)
    cells = []
    for _place in range(ROWS):
        day = widths._day(draw, 1930, 1999)
        cells += [day.isoformat() if draw.random() < 0.15 else day.strftime("%m/%d/%Y")]
    seen = widths._run(tmp_path, cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    years = seen["block"]["made_up_years"]  # type: ignore[index]
    assert years and years[0][0] == 2028, years
    assert seen["dated"] == ROWS, seen["dated"]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0


def test_iso_births_of_many_days_beside_month_first_keep_their_room(tmp_path: pathlib.Path) -> None:
    """K-HZ-13's proof on batch 4q's head b93f128a (its mixed birth dates at 200,000 rows, 200,000 twin cells no
    date) at the table floor: 20,000 births of 1930 to 1999, nine in ten ISO, each of those a different day, the
    rest month first, with `--identifier`. The ISO layout's share of the block, its 18,000 values twice at 365
    dates a year, ran from 2028 to 2126, past the years a month-first cell names read year first (`02/01/1955`
    names 2119), so b93f128a published `[]` and wrote the whole column as record numbers. Beside a layout written
    year last, a year-first layout's share takes the block's years whose second figure is a nought (2028 to 2099,
    then 3000 on): every twin cell a date, none naming a real day.
    """
    draw = random.Random(5)
    first = datetime.date(1930, 1, 1).toordinal()
    days = draw.sample(range(first, datetime.date(1999, 12, 31).toordinal() + 1), ROWS * 9 // 10)
    cells = [datetime.date.fromordinal(day).isoformat() for day in days]
    cells += [widths._day(draw, 1930, 1999).strftime("%m/%d/%Y") for _place in range(ROWS - len(cells))]
    draw.shuffle(cells)
    seen = widths._run(tmp_path, cells, ["--identifier", "dob"])
    assert seen["exits"] == (0, 0, 0)
    years = seen["block"]["made_up_years"]  # type: ignore[index]
    assert years and years[0][0] == 2028 and years[-1][0] >= 3000, years
    assert seen["dated"] == ROWS, seen["dated"]
    assert seen["equal"] == 0 and seen["merged"] == 0 and seen["same_day"] == 0

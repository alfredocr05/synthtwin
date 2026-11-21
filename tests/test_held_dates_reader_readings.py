"""Codex's review of batch 4q, item 2: the held-date room reads every cell as the product's own date reader does.

Lane ID-ROOM2's room (plan P4-D457) read each real cell in the orders its layout's merged key stands in
(`taxonomy._own_date_orders`), and a month written first by its word (`Jan 01, 2028`), a month in full or a
quarter stands in none, though `parsing.parse_datetime` reads each as a day. Codex's table -- `Random(5)`, 19,989
different ISO days of 1930 to 1999 and the eleven days `Jan 01, 2028` to `Jan 11, 2028` once each, shuffled with
the same stream, one column `ref` held with `--identifier`, seed 0 -- published `made_up_years` [[2028, 2137]] on
29fdf3aa and its twin wrote eight of those eleven real days as ISO dates; f0ce1e06 wrote none of them. Every cell
is now read by the reader too, in every member of `parsing.DATE_FORMATS` (`taxonomy.date_reader_years`), and
each year it names is held, so 2028 is no made-up year here: the column has no room, its twin's cells are
record numbers (NF137, the owned price), and no twin cell names a real day. AND THE ROUND'S SWEEP: `Jan. 05,
2028`, a month word with a point, is read by no member of the reader, and the round's first cut still wrote
eight of those eleven real days; each run of four figures a cell holds is held as its year too
(`taxonomy.four_figure_runs`), so a year in four figures leaves no room whatever its spelling.

Each case runs the command at the table floor (20,000 rows) and reads the twin's cells against the real ones
by CALENDAR DAY, never by spelling: every reading the reader gives a cell, and the ordinary strptime forms,
each real cell's days and each twin cell's read once.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random

import pytest

from synthtwin import cli, parsing, taxonomy

import unanswered_identifier_shapes as held_shapes

ROWS = 20_000
# The forms a cell is read in apart from the product's reader: four-figure years as written.
FORMS = (
    "%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y",
    "%d-%b-%Y", "%b-%d-%Y", "%Y%m%d", "%Y/%m/%d", "%m.%d.%Y", "%d.%m.%Y", "%b. %d, %Y", "%d%b%Y",
)


def _days(cell: str) -> "set[datetime.date]":
    """Every calendar day a cell names: each reading of the product's date reader, and each of `FORMS`."""
    found: "set[datetime.date]" = set()
    for member in parsing.DATE_FORMATS:
        read = parsing.parse_datetime(cell, member)
        if read is not None and len(read[0]) >= 10 and read[0][4] == "-" and read[0][7] == "-":
            found.add(datetime.date(int(read[0][0:4]), int(read[0][5:7]), int(read[0][8:10])))
    for form in FORMS:
        try:
            found.add(datetime.datetime.strptime(cell.strip(), form).date())
        except ValueError:
            continue
    return found


def _codex_cells(written: str) -> "list[str]":
    """Codex's table: 19,989 different ISO days of 1930 to 1999, the eleven days of 2028 written as ``written``."""
    draw = random.Random(5)
    first = datetime.date(1930, 1, 1).toordinal()
    days = draw.sample(range(first, datetime.date(1999, 12, 31).toordinal() + 1), ROWS - 11)
    cells = [datetime.date.fromordinal(day).isoformat() for day in days]
    cells += [datetime.date(2028, 1, day).strftime(written) for day in range(1, 12)]
    draw.shuffle(cells)
    return cells


def _run(folder: pathlib.Path, cells: "list[str]") -> "dict[str, object]":
    """Profile `ref` with `--identifier` (nobody at the keyboard), generate at seed 0, validate; the counts."""
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
        validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin", f"{folder / 't-twin.csv'}",
                              "--out-dir", f"{folder}", "--replace"]) if generated == 0 else -1
    block = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))["columns"][0]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] if row else "" for row in list(csv.reader(handle))[1:]]
    real: "set[datetime.date]" = set()
    for cell in set(cells):
        real |= _days(cell)
    named: "dict[str, bool]" = {}
    for cell in set(twin):
        named[cell] = bool(_days(cell) & real)
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "same_day": sum(1 for cell in twin if named[cell]),
        "equal": sum(1 for cell in twin if cell in set(cells)),
    }


@pytest.mark.parametrize("written", ["%b %d, %Y", "%B %d, %Y", "%d %B %Y", "%b. %d, %Y"])
def test_codex_s_eleven_days_of_2028_are_held_in_every_reading(tmp_path: pathlib.Path, written: str) -> None:
    """Codex's table with its eleven days written month first by its word (Codex's), with the month in full, day
    first with the month in full, and month first by its word with a point, which no member of the reader
    reads: on 29fdf3aa `[[2028, 2137]]` and eight real days written for Codex's and for the last. Now 2028 is
    held, the block from it is no room, and no twin cell names a real day by any reading. MUTANTS: both
    `taxonomy.date_reader_years` and `taxonomy.four_figure_runs` naming nothing (the layout's own orders alone,
    as on 29fdf3aa), every spelling red; `four_figure_runs` alone naming nothing, the last red.
    """
    seen = _run(tmp_path, _codex_cells(written))
    assert seen["exits"] == (0, 0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert block["made_up_years"] == [], block["made_up_years"]  # type: ignore[index]
    assert seen["same_day"] == 0 and seen["equal"] == 0, seen["same_day"]


@pytest.mark.parametrize(
    ("cell", "four", "two"),
    [
        ("2028-01-05", [2028], []),
        ("2028-01-05 10:00:00", [2028], []),
        ("2028/01/05", [2028], []),
        ("2028-01", [2028], []),
        ("20280105", [2028], []),
        ("01/05/2028", [2028], []),
        ("13/05/2028", [2028], []),
        ("05 Jan 2028", [2028], []),
        ("05-January-2028", [2028], []),
        ("Jan 05, 2028", [2028], []),
        ("January 05 2028", [2028], []),
        ("Jan-05-2028", [2028], []),
        ("01.05.2028", [2028], []),
        ("01/05/28", [], [28]),
        ("01.05.28", [], [28]),
        ("01/05/2028 10:00", [2028], []),
        ("2028/01/05 10:00", [2028], []),
        ("2028-Q1", [2028], []),
        ("Jan. 05, 2028", [], []),
        ("Cedar", [], []),
    ],
)
def test_the_reader_s_years_of_a_cell(cell: str, four: "list[int]", two: "list[int]") -> None:
    """`date_reader_years`: every reading of the product's date reader, each member of `parsing.DATE_FORMATS`
    (the joint ISO member's readings are its two members'), a two-figure year as its two figures; a cell the
    reader reads in no member names none."""
    assert taxonomy.date_reader_years(cell) == (four, two)


@pytest.mark.parametrize(
    ("cell", "years"),
    [
        ("Jan. 05, 2028", [2028]),
        ("5th January 2028", [2028]),
        ("2028 Jan 05", [2028]),
        ("05Jan2028", [2028]),
        ("2028/2029", [2028, 2029]),
        ("1950-03-17", [1950]),
        ("20280105", []),
        ("12345", []),
        ("R-0123", []),
        ("Cedar", []),
    ],
)
def test_each_run_of_four_figures_a_cell_holds_is_a_year_of_it(cell: str, years: "list[int]") -> None:
    """`four_figure_runs`: each maximal run of exactly four figures opening with no nought, whatever stands beside
    it; a run of another width (a compact date, read in its own orders) or opening with a nought is none."""
    assert taxonomy.four_figure_runs(cell) == years

"""The fix round's verify of batch 4q, blocker 2: the held-date room reads every reading of a cell's own fields.

The first round held the years of the product's own date reader (`taxonomy.date_reader_years`) and of each run of
four figures (`taxonomy.four_figure_runs`), but a two-figure year in a spelling neither the reader nor the layout's
orders read -- `Jan 01, 28`, `Jan 01 '28` -- and a year written first in two figures -- `28-01-01`, read by its
layout's orders day first alone (28 January 2001) -- named a year of the room. Codex's construction (`Random(5)`,
19,989 different ISO days of 1930 to 1999, the eleven days 1 to 11 January 2028 once each in the spelling named,
shuffled with the same stream, one column `ref` held with `--identifier`, seed 0) published `made_up_years`
[[2028, 2137]] on 037d4fcd and its twin wrote eight of the eleven real days as ISO dates in each spelling; f0ce1e06
wrote none. A cell of three runs of one or two figures is now read with its year first too
(`taxonomy.year_first_years`), and a cell no reading reads has its fields read every way a person writes a day or
a month (`taxonomy.unread_years`: three neighbouring fields as a year, a month and a day in any order, a year of
one to three figures as a two-figure year; two fields as a month and a year; a run of five to eight figures no
letter is glued to as a compact date); the cross rule holds 19yy and 20yy beside a two-figure year. On these
tables 2028 (or 2045) is held, the block from 2028 is no room, the twin writes record numbers (NF137, the owned
price) and no twin cell names a real day.

Each case runs the command at the table floor (20,000 rows) and reads the twin's cells against the real ones by
CALENDAR DAY, never by spelling: each reading of the product's reader, the strptime forms of four-figure years, and
the two-figure forms in both centuries; each real cell's days and each different twin cell read once.
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
# The forms a cell is read in apart from the product's reader: four-figure years as written, and two-figure ones,
# each read in both centuries.
FORMS = ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y", "%d %b %Y", "%Y%m%d")
FORMS_TWO = ("%b %d, %y", "%b %d '%y", "%y-%m-%d", "%d-%m-%y", "%m-%d-%y", "%m/%d/%y", "%d/%m/%y")


def _days(cell: str) -> "set[datetime.date]":
    """Every calendar day a cell names: each reading of the product's reader, each of `FORMS`, each of `FORMS_TWO`
    in both centuries."""
    found: "set[datetime.date]" = set()
    for member in parsing.DATE_FORMATS:
        read = parsing.parse_datetime(cell, member)
        if read is not None and len(read[0]) >= 10 and read[0][4] == "-" and read[0][7] == "-":
            found.add(datetime.date(int(read[0][0:4]), int(read[0][5:7]), int(read[0][8:10])))
    for form in FORMS + FORMS_TWO:
        try:
            day = datetime.datetime.strptime(cell.strip(), form).date()
        except ValueError:
            continue
        found.add(day)
        if form in FORMS_TWO:
            for year in (1900 + day.year % 100, 2000 + day.year % 100):
                try:
                    found.add(day.replace(year=year))
                except ValueError:
                    continue
    return found


def _cells(written: str, first: datetime.date) -> "list[str]":
    """Codex's table: 19,989 different ISO days of 1930 to 1999, eleven days from ``first`` written as ``written``."""
    draw = random.Random(5)
    low = datetime.date(1930, 1, 1).toordinal()
    days = draw.sample(range(low, datetime.date(1999, 12, 31).toordinal() + 1), ROWS - 11)
    cells = [datetime.date.fromordinal(day).isoformat() for day in days]
    cells += [(first + datetime.timedelta(days=step)).strftime(written) for step in range(11)]
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


# The verify's three spellings of Codex's eleven days, and the ruling's birth-date table: eleven days of March 2045
# written `Mar 05, 45`, which leaves 2045 inside the block from 2028 as the room.
TABLES = {
    "month_word_year_two": ("%b %d, %y", datetime.date(2028, 1, 1)),
    "month_word_year_apostrophe": ("%b %d '%y", datetime.date(2028, 1, 1)),
    "year_two_first": ("%y-%m-%d", datetime.date(2028, 1, 1)),
    "births_of_45": ("%b %d, %y", datetime.date(2045, 3, 1)),
}


@pytest.mark.parametrize("name", sorted(TABLES))
def test_a_two_figure_year_in_any_spelling_is_held(tmp_path: pathlib.Path, name: str) -> None:
    """Codex's table with its eleven days written `Jan 01, 28`, `Jan 01 '28` and `28-01-01`, and the births of
    `Mar 01, 45` to `Mar 11, 45`: on 037d4fcd `[[2028, 2137]]` and real days written as ISO dates in each. Now the
    year is held, the block from 2028 is no room, and no twin cell names a real day by any reading. MUTANTS:
    `taxonomy.unread_years` naming nothing (the first round's readings alone), the three unread spellings red;
    `taxonomy.year_first_years` naming nothing, `28-01-01` red.
    """
    written, first = TABLES[name]
    seen = _run(tmp_path, _cells(written, first))
    assert seen["exits"] == (0, 0, 0)
    block = seen["block"]
    assert block["role"] == taxonomy.ROLE_IDENTIFIER  # type: ignore[index]
    assert block["made_up_years"] == [], block["made_up_years"]  # type: ignore[index]
    assert seen["same_day"] == 0 and seen["equal"] == 0, seen["same_day"]


@pytest.mark.parametrize(
    ("cell", "four", "two"),
    [
        # three neighbouring fields, every order: month word first, year two figures; an apostrophe; an ordinal
        ("Jan 01, 28", [], [1, 28]),
        ("Jan 01 '28", [], [1, 28]),
        ("Mar 05, 45", [], [45]),
        ("January 1st, 28", [], [1, 28]),
        ("Sept. 3rd, 28", [], [3, 28]),
        ("Jan 01, 028", [], [28]),
        ("Jan 1, 8", [], [1, 8]),
        ("Jan 01, 28 09:15", [], [1, 28]),
        ("28-01-01 09:15", [], [28, 1]),
        ("Jan. 05, 2028", [2028], []),
        # two fields: a month and a year; a month's word beside its day and year run together
        ("Jan 28", [], [28]),
        ("01/28", [], [28]),
        ("Jan0128", [], [28, 1]),
        # a compact date no letter is glued to, its year first or last
        ("280101", [], [28, 1]),
        ("01012028", [2028], []),
        # no day and no month named: placeholders, a key's figures glued to its letter, a quarter, a word
        ("99/99/9999", [], []),
        ("00/00/0000", [], []),
        ("9469-14-85", [], []),
        ("R10052028", [], []),
        ("UNKNOWN", [], []),
        ("2028-Q1", [], []),
    ],
)
def test_the_years_every_reading_of_an_unread_cell_s_fields_names(cell: str, four: "list[int]", two: "list[int]") -> None:
    """`unread_years`: three neighbouring fields as a year, a month and a day in all six orders; two as a month and
    a year; a run of five to eight figures no letter is glued to as a compact date; a year of one to three figures
    read as two figures, valid in either century; four figures never opening with a nought; none where no reading
    names a day or a month."""
    assert taxonomy.unread_years(cell) == (four, two)


@pytest.mark.parametrize(
    ("cell", "two"),
    [
        ("28-01-01", [28]),
        ("28/01/01", [28]),
        ("28.1.1", [28]),
        ("28/03/30", [28]),
        ("05/03/45", []),
        ("01/02/28", [1]),
        ("13/13/13", []),
        # ...a month's word between them is read as its layout's orders read it, its year last
        ("28-Jan-01", []),
        ("2028-01-05", []),
        ("01/02/1955", []),
        ("Jan 01, 28", []),
    ],
)
def test_three_runs_of_one_or_two_figures_are_read_year_first_too(cell: str, two: "list[int]") -> None:
    """`year_first_years`: a cell of three runs of one or two figures names its first as a two-figure year where the
    second is a month and the third a day of it in either century; a month's word, a year of four figures or a
    cell of other fields names none."""
    assert taxonomy.year_first_years(cell) == two


def _held_dates_column(cells: "list[str]") -> taxonomy.ColumnProfile:
    """A column held as record numbers on the date pass, every layout named with its count (the producer's input)."""
    census: "dict[str, int]" = {}
    for cell in cells:
        layout = parsing.layout_form(cell, parsing.LAYOUT_PLAIN)
        census[layout] = census.get(layout, 0) + 1
    return taxonomy.ColumnProfile(
        name="dob", position=1, role=taxonomy.ROLE_IDENTIFIER, statistical_type="code", quality_state="ok",
        structural_role="identifier", detection_evidence=taxonomy.note(taxonomy.EVIDENCE_HELD_IN_PEOPLE),
        n_present=len(cells), n_missing=0, missing_by_source={}, missing_by_class={}, n_missing_blank=0,
        n_missing_withheld=0, details={"layout_forms": census, "n_code_alphabet": 0, "n_all_digits": 0},
        publication_notes=[], remarks=[], n_distinct=len(set(cells)),
    )


def test_a_cell_is_read_by_its_text_not_by_its_merged_key() -> None:
    """`Jan 12, 8` and `Jan 1, 28` merge to one key, `jan128`; the room read each key once, so the second cell's
    reading -- 1 January 2028 -- was never asked where the first came before it. Each cell's text is now read
    once: 2028 is held and the block from it is no room. MUTANT: the cells remembered by merged key and layout
    orders again (the first round's), the block from 2028 published."""
    births = [(datetime.date(1940, 1, 1) + datetime.timedelta(days=step * 37)).isoformat() for step in range(400)]
    column = _held_dates_column(["Jan 12, 8", "Jan 1, 28"] + births)
    held = taxonomy.with_made_up_years(column, ["Jan 12, 8", "Jan 1, 28"] + births)
    assert held.details["made_up_years"] == [], held.details["made_up_years"]
    alone = _held_dates_column(["Jan 12, 8"] + births)
    assert taxonomy.with_made_up_years(alone, ["Jan 12, 8"] + births).details["made_up_years"][0][0] == 2028

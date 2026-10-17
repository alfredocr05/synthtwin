"""A workbook column of numbers some of which are stored as text is read (P4-D187).

THE REPRODUCTION. Excel's green-triangle column: measurements typed or
pasted so that some cells hold the number and some hold its figures as
TEXT. P4-D166 refused the whole workbook, naming the column, because
the description does not say which values were stored which way. A file
the owner expects to read must be read. Each such cell is now read as
the file stores it -- a text cell holding figures -- the census
publishes both counts, the column's values stay one distribution, and
the twin writes the text count back as text cells spread evenly over the
column rather than piled into its last rows. Which VALUES were the text
ones is a fact the description does not publish, and the twin's report
says so for the column.

Every test is a round trip: describe, generate, describe the twin, and
validate the twin AND the real workbook at exit 0, then ask an
independent reader (openpyxl) what the cells are.
"""

import pathlib
import random

import pytest

from synthtwin import sheetwriting
from tests import crosscheck
from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _measurements(rows: int, share: float, seed: int) -> "tuple[bytes, list[bool]]":
    """`weight` of `rows` gauss values, a `share` of them stored as text."""
    draw = random.Random(seed)
    strings = ["weight", "arm", "A", "B"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    stored_as_text: "list[bool]" = []
    for place in range(rows):
        number = 2 + place
        value = f"{draw.gauss(70, 12):.1f}"
        if draw.random() < share:
            strings += [value]
            cell = _cell(f"A{number}", f"{len(strings) - 1}", "s")
            stored_as_text += [True]
        else:
            cell = _cell(f"A{number}", value)
            stored_as_text += [False]
        grid[number] = [cell, _cell(f"B{number}", f"{2 + place % 2}", "s")]
    return _book([("Data", _rows(grid))], strings), stored_as_text


@pytest.mark.parametrize("floor", ["1", "11"])
def test_numbers_stored_as_text_are_read_and_written_back_as_text(
    tmp_path: pathlib.Path, floor: str
) -> None:
    data, stored = _measurements(300, 0.07, 5)
    result = _trip(tmp_path, "weights", data, ("--smallest-group", floor))
    _held(result)
    document = result["document"]
    assert document["columns"][0]["role"] == "continuous"
    census = document["source"]["workbook"]["columns"][0]["cell_classes"]
    texts = sum(stored)
    assert (census["text"], census["number"]) == (texts, 300 - texts), census
    report = (tmp_path / "weights-twin-report.txt").read_text(encoding="utf-8")
    assert (
        f"'weight' stores {texts} of its values as text and {300 - texts} as numbers,"
        in report
    )
    # LAST: what the independent reader finds in the twin's cells.
    sheet = crosscheck.reader().load_workbook(result["twin"]).active
    kinds = [isinstance(sheet.cell(row=row, column=1).value, str) for row in range(2, 302)]
    assert sum(kinds) == texts
    places = [index for index in range(300) if kinds[index]]
    # Spread over the column: not the last rows, and no gap wider than
    # twice an even spacing.
    assert places[0] < 300 // texts + 1
    widest = max(places[index + 1] - places[index] for index in range(len(places) - 1))
    assert widest <= 2 * (300 // texts) + 1, places


def test_the_count_is_spread_where_more_cells_fit_than_it_names() -> None:
    """The writer's rule on its own (method G2.2 step 1, P4-D187)."""
    census = {
        "absent": 0, "blank": 0, "empty": 0, "text": 3,
        "number": 9, "boolean": 0, "error": 0, "date": 0,
    }
    cells = tuple(f"{10 + index}.5" for index in range(12))
    written = sheetwriting.cell_classes(census, cells, "number")
    assert written.count("text") == 3 and written.count("number") == 9
    assert [index for index in range(12) if written[index] == "text"] != [9, 10, 11]
    assert sheetwriting._spread_over(list(range(12)), 9) == [
        1, 2, 3, 5, 6, 7, 9, 10, 11,
    ]
    assert sheetwriting._spread_over([4, 5], 3) == [4, 5]


def test_words_beside_numbers_are_not_called_figures(tmp_path: pathlib.Path) -> None:
    """The sentence is said only where some text cells hold figures.

    Sixty numbers beside forty words: every value stored as text is a
    word, which the writer keeps apart by its spelling, so the report
    says nothing about which values were stored which way.
    """
    strings = ["value", "other"] + [f"word{index}" for index in range(40)] + ["x", "y"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(100):
        number = 2 + place
        if place < 60:
            cell = _cell(f"A{number}", f"{place + 1}")
        else:
            cell = _cell(f"A{number}", f"{2 + place - 60}", "s")
        grid[number] = [cell, _cell(f"B{number}", f"{42 + place % 2}", "s")]
    result = _trip(tmp_path, "words", _book([("Data", _rows(grid))], strings),
                   ("--smallest-group", "11"))
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert (census["number"], census["text"]) == (60, 40), census
    report = (tmp_path / "words-twin-report.txt").read_text(encoding="utf-8")
    assert "of its values as text" not in report

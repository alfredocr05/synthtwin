"""Plan P4-D197: a count of figures stored as text is not read by subtraction.

THE REPRODUCTION (final skeptic of stage 2's close, MINOR). A workbook of 400
readings, one stored as text and one the word `pending`, at the default
floor, published `cell_classes {"number": 398, "text": 2}` beside
`n_numeric` 399: 399 less 398 is one cell of figures stored as text, a count
of one the census rule had held nowhere. Where that difference is one the
disclosure rule would not print, the column's census is withheld whole; two
such cells publish as before. The loader holds a hand-written description to
the same rule (WB3).

Every test is a round trip: describe, generate, describe the twin, and
validate the twin and the real workbook at exit 0.
"""

import pathlib
import random

import pytest

from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _readings(stored: int, words: int) -> bytes:
    draw = random.Random(77)
    strings = ["value", "grp"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(400):
        number = 2 + place
        value = f"{round(draw.gauss(50, 10), 1)}"
        if place < stored:
            strings += [value]
            cell = _cell(f"A{number}", f"{len(strings) - 1}", "s")
        elif place < stored + words:
            strings += ["pending"]
            cell = _cell(f"A{number}", f"{len(strings) - 1}", "s")
        else:
            cell = _cell(f"A{number}", value)
        grid[number] = [cell, _cell(f"B{number}", f"{place % 4}")]
    return _book([("Data", _rows(grid))], strings)


@pytest.mark.parametrize(
    "stored,words,withheld",
    [(1, 1, True), (2, 1, False), (0, 2, False)],
)
def test_one_figure_stored_as_text_withholds_the_census(
    tmp_path: pathlib.Path, stored: int, words: int, withheld: bool
) -> None:
    """Mutation: with `profile._stored_as_text_withheld` returning its block
    unchanged, the first shape publishes 398 number cells beside 399 numbers.
    """
    result = _trip(tmp_path, "readings", _readings(stored, words), ("--smallest-group", "1"))
    _held(result)
    column = result["document"]["columns"][0]
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert column["n_numeric"] == 400 - words
    if withheld:
        assert all(count is None for count in census.values()), census
        return
    assert census["number"] == 400 - stored - words, census
    assert census["text"] == stored + words, census

"""A workbook's number format codes are written as the source wrote them (P4-D189).

THE REPRODUCTION. The final skeptic's openpyxl workbook formatted a
region code `00000` and a visit time `yyyy-mm-dd hh:mm`. The twin wrote
the codes as `General` and `yyyy\\-mm\\-dd\\ hh:mm:ss`: a region stored
as 802 displayed `00802` in the table and `802` in the twin, and every
moment gained seconds on the screen. Plan P4-D79 published a custom code
as the canonical code of its kind because a custom code can carry text
out of somebody's file. A code built of the number format language's
own tokens alone carries none, so it is now published and written as
written (`dialect.sheet_format_code_publishable`); a code carrying a
quoted word, a currency or a locale still gives way to the canonical
code of its kind.

Every test is a round trip -- describe, generate, describe the twin,
validate the twin AND the real workbook at exit 0 -- and asks openpyxl
what code each cell of the twin wears.
"""

import collections
import pathlib

import pytest

from synthtwin import dialect, workbook
from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip

_FORMATS = ("General", "00000", "yyyy-mm-dd hh:mm", "yyyy-mm-dd", '0.0" kg"', "0.00")


def _visits(rows: int) -> bytes:
    """Five columns, each wearing one code of `_FORMATS` (style 1 to 5)."""
    names = ["region", "visit", "day", "weight", "creatinine"]
    strings = list(names)
    grid = {1: [_cell(f"{'ABCDE'[place]}1", f"{place}", "s") for place in range(5)]}
    for place in range(rows):
        number = 2 + place
        day = 45000 + (place * 7) % 400
        grid[number] = [
            _cell(f"A{number}", ("802", "1101", "901", "2201")[place % 4], "", 1),
            _cell(f"B{number}", f"{day}.{(place * 37) % 90 + 10}", "", 2),
            _cell(f"C{number}", f"{day}", "", 3),
            _cell(f"D{number}", f"{60 + (place * 13) % 40}.5", "", 4),
            _cell(f"E{number}", f"{1 + (place * 7) % 90 / 100:.2f}", "", 5),
        ]
    return _book([("Data", _rows(grid))], strings, _FORMATS)


def test_codes_of_the_format_language_are_written_as_written(
    tmp_path: pathlib.Path,
) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    result = _trip(tmp_path, "visits", _visits(120), ("--smallest-group", "5"))
    _held(result)
    published = [
        column["format_code"] for column in result["document"]["source"]["workbook"]["columns"]
    ]
    assert published == [
        "00000", "yyyy-mm-dd hh:mm", "yyyy-mm-dd",
        dialect.SHEET_CANONICAL_FORMAT_CODES["plain"], "0.00",
    ]
    again = [
        column["format_code"] for column in result["again"]["source"]["workbook"]["columns"]
    ]
    assert again == published
    sheet = openpyxl.load_workbook(result["twin"]).active
    for place, wanted in enumerate(published):
        worn = collections.Counter(
            sheet.cell(row=row, column=place + 1).number_format for row in range(2, 122)
        )
        assert worn == {wanted: 120}, (place, worn)
    assert b"kg" not in result["described"].read_bytes()


def test_the_grammar_admits_tokens_and_refuses_words() -> None:
    for code in ("00000", "yyyy-mm-dd hh:mm", "#,##0.00_);[Red](#,##0.00)",
                 "[h]:mm:ss", "h:mm AM/PM", "0.0%", "dd/mm/yyyy"):
        assert dialect.sheet_format_code_speakable(code), code
    for code in ('0.0" kg"', '"Record "0', "[$USD-409]#,##0.00", "[>=100]0",
                 "# ??/16", "0" * 65, "0;0;0;0;0", "yyyy\\Q"):
        assert not dialect.sheet_format_code_speakable(code), code
    assert workbook.format_kind("yyyy-mm-dd hh:mm") == dialect.SHEET_FORMAT_DATETIME
    for code in dialect.SHEET_FORMAT_CODE_KINDS:
        assert dialect.sheet_format_kind(code) == dialect.SHEET_FORMAT_CODE_KINDS[code]

"""The twin's report says which name the table's sheet is written under (P4-D188).

THE REPRODUCTION. The final skeptic's openpyxl workbook kept its table
on a sheet called `Visits`. That name is not one synthtwin can rebuild
from its own vocabulary, so the disclosure rule withholds it and the
twin writes the sheet as `Sheet1` -- and `read_excel(sheet_name=
"Visits")` failed on the twin while nothing on the twin's page said the
name had changed or why. A published name is written as published and a
withheld one under a neutral name, as before; the report now says which
of the two happened, and under which name the twin holds the table.

Each test is a round trip -- describe, generate, describe the twin,
validate the twin AND the real workbook at exit 0 -- and asks openpyxl
for the twin's sheet names, so the sentence is held to the file.
"""

import pathlib

import pytest

from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _table() -> str:
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(40):
        number = 2 + place
        grid[number] = [
            _cell(f"A{number}", f"{2 + place % 2}", "s"),
            _cell(f"B{number}", f"{100 + place}"),
        ]
    return _rows(grid)


def _report(folder: pathlib.Path, name: str) -> str:
    return (folder / f"{name}-twin-report.txt").read_text(encoding="utf-8")


def test_a_withheld_sheet_name_is_named_in_the_report(tmp_path: pathlib.Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    strings = ["arm", "score", "Low", "High"]
    folder = tmp_path / "withheld"
    result = _trip(folder, "visits", _book([("Visits", _table())], strings))
    _held(result)
    assert result["document"]["source"]["workbook"]["sheet_names"] == [None]
    assert openpyxl.load_workbook(result["twin"]).sheetnames == ["Sheet1"]
    report = _report(folder, "visits")
    assert "The sheet holding your table is written under the name Sheet1." in report
    assert "Its own name is withheld from the description" in report
    assert "Visits" not in report


def test_a_published_sheet_name_is_named_as_published(tmp_path: pathlib.Path) -> None:
    openpyxl = pytest.importorskip("openpyxl")
    strings = ["arm", "score", "Low", "High", "note"]
    notes = _rows({1: [_cell("A1", "4", "s")]})
    folder = tmp_path / "published"
    result = _trip(
        folder, "data", _book([("Data", _table()), ("Private notes", notes)], strings)
    )
    _held(result)
    assert result["document"]["source"]["workbook"]["sheet_names"] == ["Data", None]
    assert openpyxl.load_workbook(result["twin"]).sheetnames[0] == "Data"
    report = _report(folder, "data")
    assert "The sheet holding your table is written under its own name, Data," in report
    assert "1 other sheet name(s) are withheld the same way" in report


def test_a_delimited_report_carries_no_workbook_paragraph(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "plain.csv"
    source.write_text(
        "arm,score\n" + "".join(f"{['Low', 'High'][row % 2]},{100 + row}\n" for row in range(40)),
        encoding="utf-8",
    )
    result = _trip(tmp_path / "csv", "plain", source.read_bytes(), suffix=".csv")
    _held(result)
    assert "The twin is written as a workbook" not in _report(tmp_path / "csv", "plain")

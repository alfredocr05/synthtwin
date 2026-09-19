"""The calendar a twin's date cells are held to (plan P4-D291).

THE DEFECT THIS LANDING CLOSED. A workbook column of 118 cells stored
as dates, beside two texts, has its cell-class census held back whole
at a smallest group of eleven; the column's role falls to free text, so
its twin's cells are made up from the column's published SHAPE and wear
a date's shape without naming a day. `dialect.sheet_class_fits` read
the shape alone, so `2006-06-32` was written as a date cell (`t="d"`),
openpyxl raised `day is out of range for month` and could not open the
twin AT ALL, and `synthtwin validate` returned 0 for the table and 0
for the twin -- so nothing caught it.

WHAT IS CHECKED HERE, and why each part is here rather than only in the
frozen case beside it (`workbook_made_up_dates`, method G14.3): the
frozen case pins the two rules against the oracle's own bytes, and
these run the rules end to end through the three commands a person
runs, and ask an INDEPENDENT reader (openpyxl, which `src/synthtwin`
never imports) the question the defect was about.

Three things the measurement of this landing settled, each pinned below:

* the defect is NOT a property of the withheld census. At a smallest
  group of two the same table publishes its census in full -- `date
  118, text 2` -- and the twin was unreadable in exactly the same way,
  so publishing the census buys nothing and costs the disclosure rule;
* narrowing the class alone opens the twin and writes those cells as
  TEXT, and the twin then MISSES `workbook.value-class` at exit 3;
* bringing a date-storing column's made-up cells onto the calendar
  before the classes are allocated keeps both: the twin opens and it
  meets its own description at exit 0.

Every workbook here is built by neutral code at runtime (plan D13).
"""

import contextlib
import datetime
import io
import pathlib
import random
import sys
import zipfile

import pytest

from synthtwin import dialect, sheetwriting
from tests import workbooks

# The shipped rule, held before any test puts a withdrawn one in its
# place, so that a mutant of one class does not silence the others.
_SHIPPED_FITS = dialect.sheet_class_fits

_FLOOR_ELEVEN = "11"
_FLOOR_TWO = "2"


def _exit_of(argv: "list[str]") -> int:
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _quiet(argv: "list[str]") -> int:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = _exit_of(argv)
    return code


def _styles(codes: "list[str]") -> bytes:
    """One style per format code, the first being the general format."""
    formats = ""
    cells = '<xf numFmtId="0" fontId="0" fillId="0" borderId="0"/>'
    for index in range(len(codes)):
        number = 200 + index
        formats = formats + (
            f'<numFmt numFmtId="{number}" formatCode="{codes[index]}"/>'
        )
        cells = cells + (
            f'<xf numFmtId="{number}" fontId="0" fillId="0" borderId="0" '
            'applyNumberFormat="1"/>'
        )
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<styleSheet xmlns="http://schemas.openxmlformats.org/'
        'spreadsheetml/2006/main">'
        f'<numFmts count="{len(codes)}">{formats}</numFmts>'
        '<fonts count="1"><font/></fonts>'
        '<fills count="1"><fill/></fills>'
        '<borders count="1"><border/></borders>'
        '<cellStyleXfs count="1"><xf/></cellStyleXfs>'
        f'<cellXfs count="{len(codes) + 1}">{cells}</cellXfs>'
        "</styleSheet>"
    ).encode("utf-8")


def _book(rows: "list[tuple[int, list[str]]]", span: str) -> bytes:
    """One visible sheet of those rows, wearing one date format code."""
    return workbooks.package(
        [
            (
                "[Content_Types].xml",
                workbooks._content_types(1, False, False, False),
            ),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", _styles(["yyyy-mm-dd"])),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet(rows, dimension=span, frozen=0),
            ),
        ]
    )


def _dated_book() -> bytes:
    """118 ISO date cells beside two texts, and two columns of labels."""
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "seen_on", "inlineStr"),
                workbooks.cell("B1", "site", "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 2 + index
        if index < 118:
            first = workbooks.cell(
                f"A{number}",
                f"2024-{1 + index % 12:02d}-{1 + index % 28:02d}",
                "d",
                1,
            )
        else:
            first = workbooks.cell(f"A{number}", "not recorded", "inlineStr")
        rows += [
            (
                number,
                [
                    first,
                    workbooks.cell(
                        f"B{number}", f"s{index % 4}", "inlineStr"
                    ),
                ],
            )
        ]
    return _book(rows, "A1:B121")


def _date_cells(sheet: str) -> "list[str]":
    """Every spelling the twin's sheet stores as a date cell."""
    out: "list[str]" = []
    for piece in sheet.split('t="d"'):
        opened = piece.find("<v>")
        if opened < 0 or piece.find("<c ") in range(opened):
            continue
        out += [piece[opened + 3 : piece.find("</v>", opened)]]
    return out


def _run(folder: pathlib.Path, floor: str) -> "tuple[list[str], list[object]]":
    """Describe, generate and read the twin back with openpyxl."""
    openpyxl = pytest.importorskip("openpyxl")
    table = folder / "table.xlsx"
    table.write_bytes(_dated_book())
    assert _quiet(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace",
         "--smallest-group", floor]
    ) == 0
    described = folder / "table-profile.json"
    assert _quiet(
        ["generate", f"{described}", "--out-dir", f"{folder}", "--replace",
         "--seed", "0"]
    ) == 0
    twin = folder / "table-twin.xlsx"
    with zipfile.ZipFile(twin) as packed:
        sheet = packed.read("xl/worksheets/sheet1.xml").decode("utf-8")
    book = openpyxl.load_workbook(twin)
    read = book[book.sheetnames[0]]
    values = [
        row[0].value
        for row in read.iter_rows(min_row=2, min_col=1, max_col=1)
    ]
    for checked in (table, twin):
        assert _quiet(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{folder}", "--replace"]
        ) == 0, checked.name
    return _date_cells(sheet), values


@pytest.mark.parametrize("floor", (_FLOOR_ELEVEN, _FLOOR_TWO))
def test_a_date_column_gives_a_twin_a_reader_opens(
    floor: str, tmp_path: pathlib.Path
) -> None:
    """The defect, at the floor that withholds the census and at one that does not.

    At eleven the cell-class census is held back whole and the cells
    fall to the published commonest class; at two the census is
    published in full as `date 118, text 2` and the count is handed out
    by number. BOTH wrote a twin openpyxl could not open before this
    landing, which is what says the defect was never a property of the
    withholding -- so publishing the census would have bought nothing
    and cost the disclosure rule.
    """
    written, values = _run(tmp_path, floor)
    assert len(written) == 118, len(written)
    assert [one for one in written if not dialect.sheet_date_is_real(one)] == []
    dates = [one for one in values if isinstance(one, datetime.date)]
    assert len(dates) == 118, len(dates)
    assert len([one for one in values if isinstance(one, str)]) == 2, values[:4]


def test_the_shape_the_description_publishes_does_not_move(
    tmp_path: pathlib.Path,
) -> None:
    """What the repair may change, and what it may not.

    The cells it touches are cells of a column whose role publishes no
    value of it: what the description DOES publish about them is their
    shape and their length, and neither moves -- each cell comes back
    ten characters long, four figures, a hyphen, two figures, a hyphen
    and two figures. That is why the twin still meets its description.
    """
    written, _values = _run(tmp_path, _FLOOR_ELEVEN)
    for one in written:
        assert len(one) == 10, one
        assert one[4] == "-" and one[7] == "-", one
        assert one.replace("-", "").isdigit(), one


def test_the_calendar_is_asked_of_every_field() -> None:
    """`sheet_date_is_real`: the shape first, then each field's range."""
    for text in (
        "2024-03-17",
        "2024-02-29",
        "2000-02-29",
        "2024-03-17T00:00",
        "2024-03-17T23:59:59",
        "2024-03-17T23:59:59.250",
        "00:00",
        "23:59:59",
    ):
        assert dialect.sheet_date_is_real(text), text
    for text in (
        "2006-06-32",
        "8204-84-03",
        "2106-36-14",
        "0000-01-01",
        "2023-02-29",
        "2100-02-29",
        "2024-00-10",
        "2024-01-00",
        "2024-04-31",
        "2024-03-17T24:00",
        "2024-03-17T23:60",
        "2024-03-17T23:59:60",
        "24:00",
        "not a date",
        "",
    ):
        assert not dialect.sheet_date_is_real(text), text
        assert not dialect.sheet_class_fits(dialect.SHEET_CELL_DATE, text), text


def test_a_made_up_date_is_brought_to_the_nearest_day_the_calendar_has() -> None:
    """`sheet_date_on_the_calendar`, field by field, at its own width."""
    for text, wanted in (
        ("2006-06-32", "2006-06-30"),
        ("8204-84-03", "8204-12-03"),
        ("2106-36-14", "2106-12-14"),
        ("0000-01-01", "0001-01-01"),
        ("2023-02-29", "2023-02-28"),
        ("2100-02-29", "2100-02-28"),
        ("2024-00-10", "2024-01-10"),
        ("2024-01-00", "2024-01-01"),
        ("9999-99-99", "9999-12-31"),
        ("2024-02-30T10:15:30", "2024-02-29T10:15:30"),
        ("2024-03-21T99:99:99", "2024-03-21T23:59:59"),
        ("2024-03-22T23:59:99.250", "2024-03-22T23:59:59.250"),
        ("99:99", "23:59"),
    ):
        assert dialect.sheet_date_on_the_calendar(text) == wanted, text
    # A cell that already names a day, and one that is no date at all,
    # come back exactly as they came.
    for text in ("2024-03-17", "2024-02-29T10:15:30", "not a date", "", "104"):
        assert dialect.sheet_date_on_the_calendar(text) == text, text


def test_every_cell_of_the_shape_comes_back_a_day_the_calendar_has() -> None:
    """The property the twin's readability rests on, over 20,000 draws.

    Whatever four, two and two figures a column generator writes, what
    the writer hands a date cell names a day -- and at the width it was
    written with, so the published shape of the column does not move.
    """
    rng = random.Random(11)
    for _draw in range(20000):
        text = (
            f"{rng.randrange(10000):04d}-{rng.randrange(100):02d}"
            f"-{rng.randrange(100):02d}"
        )
        if rng.randrange(2):
            text = text + (
                f"T{rng.randrange(100):02d}:{rng.randrange(100):02d}"
                f":{rng.randrange(100):02d}"
            )
        brought = dialect.sheet_date_on_the_calendar(text)
        assert dialect.sheet_date_is_real(brought), (text, brought)
        assert len(brought) == len(text), (text, brought)


def test_a_column_the_description_does_not_store_as_dates_is_left_alone() -> None:
    """Which cells the calendar step reaches, asked of what it settles.

    Step 0a runs only where the description says the column stores
    dates -- a published `date` count above nought, or a `value_class`
    of `date` where the census was withheld. A column whose commonest
    class is `number` is left alone, and the FIT rule alone then keeps
    its made-up cells off the `date` class: they are written as text.
    """
    withheld: "dict[str, int | None]" = {
        "absent": None, "blank": None, "empty": None, "text": None,
        "number": None, "boolean": None, "error": None, "date": None,
    }
    cells = ("2024-77-88", "2024-03-17", "104")
    assert sheetwriting.cell_classes(withheld, cells, "number") == (
        "text", "date", "number",
    )
    # The same cells brought onto the calendar, which is what a column
    # the description DOES store as dates gets first.
    brought = tuple(
        dialect.sheet_date_on_the_calendar(one) for one in cells
    )
    assert brought == ("2024-12-31", "2024-03-17", "104"), brought
    assert sheetwriting.cell_classes(withheld, brought, "date") == (
        "date", "date", "number",
    )


def test_the_writer_never_marks_a_cell_a_date_it_cannot_carry(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The last line of defence, measured with BOTH rules withdrawn.

    The fit rule no longer lets a cell that names no day take the
    `date` class, and the calendar step no longer leaves such a cell in
    a date-storing column. With both put back the way they were -- the
    fit asking the SHAPE alone and the calendar step handing every cell
    back unchanged -- the writer's own branch still refuses to mark the
    cell a date cell, and openpyxl still opens the twin. A twin no
    reader can open is never acceptable, so this rule is stated in two
    places on purpose.
    """
    openpyxl = pytest.importorskip("openpyxl")
    monkeypatch.setattr(dialect, "sheet_date_on_the_calendar", lambda text: text)
    monkeypatch.setattr(
        dialect,
        "sheet_class_fits",
        lambda kind, text: (
            dialect.sheet_iso_date(text)
            if kind == dialect.SHEET_CELL_DATE
            else _SHIPPED_FITS(kind, text)
        ),
    )
    table = tmp_path / "table.xlsx"
    table.write_bytes(_dated_book())
    assert _quiet(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
         "--smallest-group", _FLOOR_ELEVEN]
    ) == 0
    assert _quiet(
        ["generate", f"{tmp_path / 'table-profile.json'}", "--out-dir",
         f"{tmp_path}", "--replace", "--seed", "0"]
    ) == 0
    twin = tmp_path / "table-twin.xlsx"
    with zipfile.ZipFile(twin) as packed:
        sheet = packed.read("xl/worksheets/sheet1.xml").decode("utf-8")
    # Not one date cell is written, although the class was handed out.
    assert _date_cells(sheet) == []
    openpyxl.load_workbook(twin)

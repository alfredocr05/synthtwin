"""A row of one cell above a workbook's names is asked what a text line is (P4-D186).

P4-D174 stopped every workbook holding a row of one cell above its
header unless the sheet froze its panes or filtered its header there,
because such a row is either a title or the names of a table that
leaves its other names blank. That refused workbooks whose delimited
twin -- the same rows as lines -- a text file's preamble rule reads
without a question: a line of one field holding a space is a title, a
line beginning with `#` a comment, a blank line a blank, and each is
published by its shape and never by its text.

The rule is one now (`dialect.lone_field_leads_a_table`): a row of one
cell that a text file's survey would step over is stepped over and
counted in `rows_above_header`; a row of one word, or of one number, is
the names. The row taken as names then meets the question a text
file's header meets. Every test is a round trip -- describe, generate,
describe the twin, validate the twin AND the real workbook at exit 0 --
or the parity of a workbook with the text file of the same rows.
"""

import pathlib

import pytest

from synthtwin import dialect, errors, reading, workbook
from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _titled(title: str, names: "list[str]", records: "list[list[str]]") -> bytes:
    """`title` alone in A1 (B1, C1 blank), `names` in row 2, `records` below."""
    strings: "list[str]" = [title] + list(names)
    grid = {
        1: [_cell("A1", "0", "s")],
        2: [_cell(f"{'ABC'[place]}2", f"{1 + place}", "s") for place in range(3)],
    }
    for index, record in enumerate(records):
        number = 3 + index
        cells = []
        for place, value in enumerate(record):
            strings += [value]
            cells += [_cell(f"{'ABC'[place]}{number}", f"{len(strings) - 1}", "s")]
        grid[number] = cells
    return _book([("Data", _rows(grid))], strings)


def _records(count: int) -> "list[list[str]]":
    return [
        [f"CASE-{1000 + place}", ["red", "blue"][place % 2],
         ["Eastham", "Westbury", "Southport"][place % 3]]
        for place in range(count)
    ]


def _as_lines(title: str, names: "list[str]", records: "list[list[str]]") -> str:
    lines = [title, ",".join(names)] + [",".join(record) for record in records]
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    "title, where",
    [("Extract of the visits", "title"), ("# made by hand", "comment"), ("", "blank")],
)
def test_a_title_row_is_counted_and_not_asked_about(
    tmp_path: pathlib.Path, title: str, where: str
) -> None:
    """THE REPRODUCTION: a titled workbook with no frozen pane or filter.

    It stopped at exit 1 under P4-D174. Now the title is a row above the
    header, published as a count, its text nowhere in the description,
    and the twin -- which writes the row back holding nothing -- is read
    the same way again.
    """
    names = ["subject", "colour", "place"]
    result = _trip(tmp_path / where, "titled", _titled(title, names, _records(40)),
                   ("--smallest-group", "5"))
    _held(result)
    document = result["document"]
    assert [one["name"] for one in document["columns"]] == names
    assert document["n_rows"] == 40
    assert document["source"]["workbook"]["rows_above_header"] == 1
    assert result["again"]["source"]["workbook"]["rows_above_header"] == 1
    if title:
        assert title.encode() not in result["described"].read_bytes()


def test_the_workbook_and_the_text_file_of_the_same_rows_agree(
    tmp_path: pathlib.Path,
) -> None:
    """Parity: which row is the names, and whether the run stops, match.

    Four shapes, each written once as a workbook and once as the text
    file of the same rows: a title holding a space over names; a title
    over a row that reads as a record, which both stop and ask; a row of
    one word over records of three, which a text file refuses as ragged
    and a workbook reads as the names with the others blank (a text file
    of that sheet writes `subject,,`, which reads the same); and a
    comment over names.
    """
    records = _records(40)
    looking = [["CASE-ZEBRA-471", "red", "Eastham"]] + records
    shapes = [
        ("Extract of the visits", ["subject", "colour", "place"], records),
        ("Extract of the visits", ["CASE-900", "red", "Eastham"], looking),
        ("# made by hand", ["subject", "colour", "place"], records),
    ]
    for number, (title, names, rows) in enumerate(shapes):
        book = tmp_path / f"shape{number}.xlsx"
        book.write_bytes(_titled(title, names, rows))
        text = tmp_path / f"shape{number}.csv"
        text.write_text(_as_lines(title, names, rows), encoding="utf-8", newline="")
        outcomes = []
        for path in (book, text):
            try:
                table = reading.read_table(str(path))
                outcomes += [("read", tuple(table.column_names), table.n_rows)]
            except errors.ProfileError:
                outcomes += [("asked",)]
        assert outcomes[0] == outcomes[1], (number, outcomes)
        assert outcomes[0][0] == ("asked" if number == 1 else "read"), outcomes
    word = tmp_path / "word.xlsx"
    word.write_bytes(_titled("subject", ["CASE-ZEBRA-471", "amber", "Northfield"], records))
    commas = tmp_path / "word.csv"
    commas.write_text(
        _as_lines("subject,,", ["CASE-ZEBRA-471", "amber", "Northfield"], records),
        encoding="utf-8",
        newline="",
    )
    read_book = reading.read_table(str(word))
    read_text = reading.read_table(str(commas))
    assert tuple(read_book.column_names) == tuple(read_text.column_names) == (
        "subject", "Unnamed: 1", "Unnamed: 2",
    )


def test_the_one_rule_is_the_text_files_rule() -> None:
    """The workbook asks `dialect.lone_field_leads_a_table`, as the survey does."""
    for text, leads in (("Extract of the visits", True), ("# note", True),
                        ("subject", False), ("12", False), ("", False)):
        assert dialect.lone_field_leads_a_table(text) is leads
    row = {1: workbook.Cell(1, 1, workbook.CELL_TEXT, "", "General", False, False)}
    assert workbook._row_leads_the_table(row)
    row = {1: workbook.Cell(1, 1, workbook.CELL_NUMBER, "2024", "General", False, False)}
    assert not workbook._row_leads_the_table(row)

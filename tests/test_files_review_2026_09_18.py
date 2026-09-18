"""The files review of 2026-09-18, each test built from its reproduction.

One review round on commit `c5d09d5` read the workbook reader and
writer, the delimiter survey and the first-row rules, and found ten
items in the files area: three blockers, six major, one minor. Plan
entries P4-D280 to P4-D289 carry the measurement for each; this file
carries the reproduction, run end to end wherever the defect is one a
person meets -- a realistic source is written, described, generated,
and both files validated -- and an INDEPENDENT reader (openpyxl, which
`src/synthtwin` never imports) is asked the question the defect was
about, because a twin holding every published fact can still hand a
reader a different table.

THE RED CHECKS, each measured by withdrawing the rule in place:

* `reading._shares_the_shape_below` put back to demanding every value
  below -- `test_one_identifier_in_another_layout_still_names_no_column`
  and `test_a_missing_identifier_still_names_no_column`;
* `workbook.marks_the_header` counting the frozen pane again --
  `test_a_frozen_pane_does_not_publish_an_ambiguous_row`;
* `dialect.delimiter_reading`'s competitor requiring the width again --
  `test_a_narrower_consistent_delimiter_is_a_competitor`;
* `workbook.mixed_number_formats` returning None --
  `test_a_column_wearing_two_codes_of_one_kind_is_refused`;
* `sheetwriting._dates_as_day_counts` converting every cell again --
  `test_iso_date_cells_stay_date_cells`;
* `workbook._CellWalk.had_inline` read as `in_inline` again --
  `test_an_empty_inline_string_is_an_empty_string`;
* the mixed-storage refusal moved back above the first-row decision --
  `test_a_workbook_refusal_names_no_cell_of_an_unsettled_first_row`;
* `workbook.reference_column`'s bound removed --
  `test_a_hostile_cell_reference_is_refused_at_once`;
* WB4 held to how many rows the table has again --
  `test_a_legal_freeze_below_the_table_loads`;
* `workbook.is_packaged_unreadably` returning False --
  `test_a_package_this_reader_cannot_expand_is_refused_in_words`.

Every table and every workbook here is built by neutral code at runtime
(plan D13); the vocabulary is made up on the spot.
"""

import contextlib
import io
import json
import pathlib
import struct
import sys
import time
import zipfile

import pytest

from synthtwin import asking, dialect, errors, reading, workbook
from tests import workbooks

_FLOOR_ELEVEN = "11"
_FLOOR_FIVE = "5"


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
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


def _quiet(argv: "list[str]") -> "tuple[int, str]":
    """The same, with the command's pages captured rather than logged."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = _exit_of(argv)
    return code, out.getvalue() + err.getvalue()


def _profiled(folder: pathlib.Path, table: pathlib.Path, *flags: str) -> int:
    code, _said = _quiet(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace", *flags]
    )
    return code


def _document(path: pathlib.Path) -> "dict":
    return json.loads(path.read_text(encoding="utf-8"))


def _first_row_questions(questions: pathlib.Path) -> "list[dict]":
    written = _document(questions)
    return [
        entry
        for entry in written["about_your_file"]
        if entry["column"] == asking.FIRST_ROW_SUBJECT
    ]


# -- the delimited reproduction of item 1 ------------------------------

_TITLE = "Cohort extract"
_LEAD = "CASE-ZEBRA-471,Northfield Clinic 3,<0.10"


def _cohort(odd: str = "") -> str:
    """240 records under a title; record 120's identifier is ``odd``."""
    lines = [_TITLE, _LEAD]
    for index in range(1, 240):
        name = f"CASE-ALPHA-{1000 + index}"
        if index == 120 and odd:
            name = odd
        lines += [f"{name},location {index},{1 + index / 10:.1f}"]
    return "\n".join(lines) + "\n"


def _named_nothing(tmp_path: pathlib.Path, body: str) -> "dict":
    """Describe that body and hand back what the description says."""
    table = tmp_path / "table.csv"
    table.write_text(body, encoding="utf-8", newline="")
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_ELEVEN) == 0
    document = _document(tmp_path / "table-profile.json")
    return {
        "names": [block["name"] for block in document["columns"]],
        "n_rows": document["n_rows"],
        "source": document["source"]["header_source"],
        "asked": len(_first_row_questions(tmp_path / "table-questions.json")),
        "bytes": (tmp_path / "table-profile.json").read_text("utf-8"),
    }


def test_the_unanimous_layout_still_names_no_column(
    tmp_path: pathlib.Path,
) -> None:
    """The shape P4-D241 closed, unchanged: it is the control."""
    found = _named_nothing(tmp_path, _cohort())
    assert found["names"] == ["column_1", "column_2", "column_3"]
    assert found["n_rows"] == 240
    assert found["asked"] == 1


@pytest.mark.parametrize("odd", ["CASE_ALPHA_1120", "NA"])
def test_one_identifier_in_another_layout_still_names_no_column(
    tmp_path: pathlib.Path, odd: str
) -> None:
    """Item 1 (BLOCKER), plan P4-D280.

    One of 239 identifiers written in a second system's layout -- which
    ruling 7 says a file may hold -- or left as a missing-value word
    silenced the rule, and the whole first record became the three
    column names with the table 239 rows long.
    """
    found = _named_nothing(tmp_path, _cohort(odd))
    assert found["names"] == ["column_1", "column_2", "column_3"], found
    assert found["n_rows"] == 240, found
    assert found["source"] == "generated"
    assert found["asked"] == 1
    # NOT ONE CHARACTER OF THE RECORD IS PUBLISHED, which is the whole
    # of ruling 8 and the half a row count cannot show.
    for cell in _LEAD.split(","):
        assert cell not in found["bytes"], cell


def test_a_missing_identifier_still_names_no_column(
    tmp_path: pathlib.Path,
) -> None:
    """The same, said once more for the missing-value word alone."""
    found = _named_nothing(tmp_path, _cohort("NA"))
    assert found["names"] == ["column_1", "column_2", "column_3"]


def test_a_headed_export_is_still_read_as_headed(
    tmp_path: pathlib.Path,
) -> None:
    """The commonest-silhouette rule stays off an ordinary export.

    `record_id` over `R001` is `A_A` over `A9`: not the same shape, and
    `A_A` is not structured either. A file whose header is words over
    columns of words is the same story.
    """
    body = "record_id,site,reading\n" + "".join(
        f"R{100 + index:03d},north,{index}\n" for index in range(40)
    )
    table = tmp_path / "headed.csv"
    table.write_text(body, encoding="utf-8", newline="")
    assert _profiled(tmp_path, table, "--smallest-group", "5") == 0
    document = _document(tmp_path / "headed-profile.json")
    assert [one["name"] for one in document["columns"]] == [
        "record_id", "site", "reading",
    ]
    assert document["n_rows"] == 40


# -- the workbook reproductions ----------------------------------------


def _styles(codes: "list[str]") -> bytes:
    """A style sheet whose style `i + 1` wears `codes[i]`; style 0 is general."""
    parts = [
        workbooks._DECLARATION,
        f'<styleSheet xmlns="{workbooks._MAIN}">',
        f'<numFmts count="{len(codes)}">',
    ]
    for place in range(len(codes)):
        parts += [
            f'<numFmt numFmtId="{164 + place}" '
            f'formatCode="{workbooks._escaped(codes[place])}"/>'
        ]
    parts += [
        "</numFmts>",
        '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font>'
        "</fonts>",
        '<fills count="2"><fill><patternFill patternType="none"/></fill>'
        '<fill><patternFill patternType="gray125"/></fill></fills>',
        '<borders count="1"><border><left/><right/><top/><bottom/>'
        "<diagonal/></border></borders>",
        '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" '
        'borderId="0"/></cellStyleXfs>',
        f'<cellXfs count="{len(codes) + 1}">',
        '<xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>',
    ]
    for place in range(len(codes)):
        parts += [
            f'<xf numFmtId="{164 + place}" fontId="0" fillId="0" '
            'borderId="0" xfId="0" applyNumberFormat="1"/>'
        ]
    parts += [
        "</cellXfs>",
        '<cellStyles count="1"><cellStyle name="Normal" xfId="0" '
        'builtinId="0"/></cellStyles>',
        "</styleSheet>",
    ]
    return "".join(parts).encode("utf-8")


def _book(
    rows: "list[tuple[int, list[str]]]",
    codes: "list[str]",
    span: str,
    frozen: int = 0,
) -> bytes:
    """One visible sheet of those rows, with those format codes."""
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", _styles(codes)),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet(rows, dimension=span, frozen=frozen),
            ),
        ]
    )


def _openpyxl_column(path: pathlib.Path, column: int = 1) -> "list[object]":
    """One column of a workbook as an INDEPENDENT reader hands it back."""
    openpyxl = pytest.importorskip("openpyxl")
    book = openpyxl.load_workbook(path)
    sheet = book[book.sheetnames[0]]
    out: "list[object]" = []
    for row in sheet.iter_rows(min_row=2, min_col=column, max_col=column):
        for cell in row:
            out += [cell.value]
    return out


def _openpyxl_formats(path: pathlib.Path) -> "dict[str, int]":
    openpyxl = pytest.importorskip("openpyxl")
    book = openpyxl.load_workbook(path)
    sheet = book[book.sheetnames[0]]
    out: "dict[str, int]" = {}
    for row in sheet.iter_rows(min_row=2, min_col=1, max_col=1):
        for cell in row:
            if cell.value is None:
                continue
            out[cell.number_format] = out.get(cell.number_format, 0) + 1
    return out


_CANARY_ONE = "PERSON_CANARY"
_CANARY_TWO = "PRIVATE_CANARY"


def _ambiguous_sheet(frozen: int) -> bytes:
    """A title, a row of two texts, and 120 records of text pairs."""
    rows = [(1, [workbooks.cell("A1", "Study overview", "inlineStr")])]
    rows += [
        (
            2,
            [
                workbooks.cell("A2", _CANARY_ONE, "inlineStr"),
                workbooks.cell("B2", _CANARY_TWO, "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 3 + index
        rows += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", f"record{index}word", "inlineStr"),
                    workbooks.cell(f"B{number}", f"word{index}record", "inlineStr"),
                ],
            )
        ]
    return _book(rows, ["General"], "A1:B122", frozen=frozen)


@pytest.mark.parametrize("frozen", [0, 2])
def test_a_frozen_pane_does_not_publish_an_ambiguous_row(
    tmp_path: pathlib.Path, frozen: int
) -> None:
    """Item 2 (BLOCKER), plan P4-D281.

    Without the pane the sheet is read with placeholder names and 121
    records. With it, one attribute of a VIEW published both of row 2's
    values as the column names, dropped the row count to 120 and copied
    them into the twin's header -- and the description passed every
    contract check.
    """
    table = tmp_path / "table.xlsx"
    table.write_bytes(_ambiguous_sheet(frozen))
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0
    described = tmp_path / "table-profile.json"
    document = _document(described)
    assert [one["name"] for one in document["columns"]] == [
        "column_1", "column_2",
    ], document["columns"]
    assert document["n_rows"] == 121
    assert document["source"]["header_source"] == "generated"
    assert len(_first_row_questions(tmp_path / "table-questions.json")) == 1
    for canary in (_CANARY_ONE, _CANARY_TWO):
        assert canary not in described.read_text("utf-8")
        assert canary not in (tmp_path / "table-profile.txt").read_text("utf-8")
    # AND THE ROUND TRIP HOLDS: the pane is still published and written.
    assert document["source"]["workbook"]["frozen_rows"] == frozen
    assert _quiet(
        ["generate", f"{described}", "--out-dir", f"{tmp_path}",
         "--replace", "--seed", "0"]
    )[0] == 0
    again = tmp_path / "again"
    again.mkdir()
    for checked in (table, tmp_path / "table-twin.xlsx"):
        assert _quiet(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{again}", "--replace"]
        )[0] == 0, checked


# -- item 3, the delimiter ---------------------------------------------


_COMPETING = "id,measure|low|high\n" + "".join(
    f"{index},{100 + index % 4}|90|110\n" for index in range(120)
)


def test_a_narrower_consistent_delimiter_is_a_competitor() -> None:
    """Item 3 (BLOCKER), plan P4-D282.

    Both readings are whole: the comma gives two columns at a share of
    1.0 and the bar three at a share of 1.0. The competitor list
    required the WIDTH to tie as well, so the wider reading took the
    file in silence.
    """
    chosen, competing = dialect.delimiter_reading(_COMPETING, 0)
    assert chosen == "|"
    assert competing == ("|", ","), competing


def test_the_competing_delimiter_is_asked_about(
    tmp_path: pathlib.Path,
) -> None:
    """...and the person is told and asked, which is the repair."""
    table = tmp_path / "table.csv"
    table.write_text(_COMPETING, encoding="utf-8", newline="")
    code, said = _quiet(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
         "--smallest-group", _FLOOR_FIVE]
    )
    assert code == 0
    assert "READS EQUALLY WELL WITH MORE THAN ONE DELIMITER" in said
    asked = [
        entry
        for entry in _document(tmp_path / "table-questions.json")["about_your_file"]
        if entry["column"] == asking.DELIMITER_SUBJECT
    ]
    assert len(asked) == 1, asked


def test_the_declared_comma_reads_the_baseline_columns(
    tmp_path: pathlib.Path,
) -> None:
    """And `--delimiter ,` reads the two columns commit 53bb012 read."""
    table = tmp_path / "table.csv"
    table.write_text(_COMPETING, encoding="utf-8", newline="")
    assert _profiled(
        tmp_path, table, "--smallest-group", _FLOOR_FIVE, "--delimiter", ","
    ) == 0
    document = _document(tmp_path / "table-profile.json")
    assert [one["name"] for one in document["columns"]] == [
        "id", "measure|low|high",
    ]


@pytest.mark.parametrize(
    "body",
    [
        "id,site,amount\n" + "".join(f"{i},north,{i * 2}\n" for i in range(50)),
        "a;b\n" + "".join(f"{i},5;{i},25\n" for i in range(50)),
        "a\tb\tc\n" + "".join(f"{i}\tx\ty\n" for i in range(50)),
        "reading\n" + "".join(f"{i}\n" for i in range(50)),
        "a,b\n" + "".join(f'"x,{i}",{i}\n' for i in range(50)),
        "a,b\n" + "".join(f"{i},p|q\n" for i in range(50)),
    ],
)
def test_an_ordinary_file_records_no_competitor(body: str) -> None:
    """The widened rule must not start asking about every file.

    Every other candidate fails to read such a file as two fields at
    all, which `dialect._best_reading` already rejects, so no competitor
    is recorded.
    """
    _chosen, competing = dialect.delimiter_reading(body, 0)
    assert competing == (), competing


# -- item 4, two number formats of one kind ----------------------------


def _two_code_book(odd: int, codes: "list[str]") -> bytes:
    """120 numeric cells; the first ``odd`` wear the SECOND code."""
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "amount", "inlineStr"),
                workbooks.cell("B1", "tag", "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 2 + index
        rows += [
            (
                number,
                [
                    workbooks.cell(
                        f"A{number}", f"{(index % 10 + 1) / 10:.1f}", "",
                        2 if index < odd else 1,
                    ),
                    workbooks.cell(f"B{number}", f"t{index % 3}", "inlineStr"),
                ],
            )
        ]
    return _book(rows, codes, "A1:B121")


def test_a_column_wearing_two_codes_of_one_kind_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4 (MAJOR), plan P4-D283.

    Sixty cells written `0%` beside sixty written `0.0`: the
    description published `0%`, the twin wore it 120 times, openpyxl
    read `{0%: 60, 0.0: 60}` from the source and `{0%: 120}` from the
    twin, and both files validated with nothing missed.
    """
    table = tmp_path / "table.xlsx"
    table.write_bytes(_two_code_book(60, ["0%", "0.0"]))
    # The independent reader confirms the source really is a mixture.
    assert _openpyxl_formats(table) == {"0%": 60, "0.0": 60}
    code, said = _quiet(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
         "--smallest-group", _FLOOR_FIVE]
    )
    assert code == 1, said
    assert "more than one number format of the same kind" in said
    # NO CODE IS NAMED: a custom code can hold somebody's text.
    assert "0.0" not in said.replace(f"{table}", "")


@pytest.mark.parametrize("odd", [1, 4])
def test_a_code_under_the_line_is_counted_into_the_commonest(
    tmp_path: pathlib.Path, odd: int
) -> None:
    """Ruling 6's own arithmetic, at the floor this refusal uses.

    A code worn by fewer cells than the line is the stray cell somebody
    reformatted, not a second population of the column.
    """
    table = tmp_path / "table.xlsx"
    table.write_bytes(_two_code_book(odd, ["0%", "0.0"]))
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0
    document = _document(tmp_path / "table-profile.json")
    assert document["source"]["workbook"]["columns"][0]["format_code"] == "0%"


def test_a_column_of_one_code_is_read(tmp_path: pathlib.Path) -> None:
    """And the refusal speaks only about a mixture."""
    table = tmp_path / "table.xlsx"
    table.write_bytes(_two_code_book(0, ["0%"]))
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0


def test_the_mixed_format_rule_reads_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """The threshold is the LINE, measured at the boundary itself.

    Four cells of the second code at a floor of five are absorbed; five
    are a population, and the column is declined.
    """
    for odd, wanted in ((4, 0), (5, 1)):
        folder = tmp_path / f"odd{odd}"
        folder.mkdir()
        table = folder / "table.xlsx"
        table.write_bytes(_two_code_book(odd, ["0%", "0.0"]))
        assert _profiled(
            folder, table, "--smallest-group", _FLOOR_FIVE
        ) == wanted, odd


# -- item 5, ISO date cells --------------------------------------------


def _date_book(stored_as_text: bool) -> bytes:
    """120 date cells wearing `yyyy-mm-dd`, stored as ISO text or as serials."""
    import datetime

    rows = [
        (
            1,
            [
                workbooks.cell("A1", "day", "inlineStr"),
                workbooks.cell("B1", "tag", "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 2 + index
        day = datetime.date(2024, 1, 1) + datetime.timedelta(days=index % 28)
        if stored_as_text:
            value, marked = day.isoformat(), "d"
        else:
            value = f"{(day - datetime.date(1899, 12, 30)).days}"
            marked = ""
        rows += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", value, marked, 1),
                    workbooks.cell(f"B{number}", f"t{index % 3}", "inlineStr"),
                ],
            )
        ]
    return _book(rows, ["yyyy\\-mm\\-dd"], "A1:B121")


@pytest.mark.parametrize("stored_as_text", [True, False])
def test_iso_date_cells_stay_date_cells(
    tmp_path: pathlib.Path, stored_as_text: bool
) -> None:
    """Item 5 (MAJOR), plan P4-D284.

    A workbook storing its dates as ISO text (`t="d"`) had them turned
    into day counts before any class could be allocated, so the whole
    column fell through to text and every reader handed back strings
    such as `"45315"`. Describing the twin again turned the role from
    `datetime` into `count`, and the twin missed its storage class, its
    value class, its role, its statistical type and its numeric counts.
    The serial shape beside it is the control, and it must not move.
    """
    import datetime

    table = tmp_path / "table.xlsx"
    table.write_bytes(_date_book(stored_as_text))
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0
    described = tmp_path / "table-profile.json"
    assert _document(described)["columns"][0]["role"] == "datetime"
    assert _quiet(
        ["generate", f"{described}", "--out-dir", f"{tmp_path}",
         "--replace", "--seed", "0"]
    )[0] == 0
    twin = tmp_path / "table-twin.xlsx"
    wanted = datetime.date if stored_as_text else datetime.datetime
    held = _openpyxl_column(twin)
    assert len(held) == 120
    for value in held:
        assert isinstance(value, wanted), value
        assert not isinstance(value, str)
    again = tmp_path / "again"
    again.mkdir()
    for checked in (table, twin):
        assert _quiet(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{again}", "--replace"]
        )[0] == 0, checked


# -- item 6, the empty inline string -----------------------------------


def _inline_book() -> bytes:
    """120 rows alternating an EMPTY inline string with a text."""
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "note", "inlineStr"),
                workbooks.cell("B1", "tag", "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 2 + index
        text = "" if index % 2 == 0 else f"alpha{index % 5}"
        rows += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", text, "inlineStr"),
                    workbooks.cell(f"B{number}", f"t{index % 3}", "inlineStr"),
                ],
            )
        ]
    return _book(rows, ["General"], "A1:B121")


def test_an_empty_inline_string_is_an_empty_string(
    tmp_path: pathlib.Path,
) -> None:
    """Item 6 (MAJOR), plan P4-D285.

    `<c t="inlineStr"><is><t></t></is></c>` was read as a styled blank,
    because the flag asked says where the walk STANDS and `</is>` has
    already cleared it. The description published `blank 60, empty 0`,
    the twin wrote blanks, and openpyxl read `""` from the source and
    `None` from the twin for those 60 records -- with nothing missed on
    either file.
    """
    table = tmp_path / "table.xlsx"
    table.write_bytes(_inline_book())
    assert _openpyxl_column(table).count("") == 60
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0
    described = tmp_path / "table-profile.json"
    census = _document(described)["source"]["workbook"]["columns"][0][
        "cell_classes"
    ]
    assert census["empty"] == 60, census
    assert census["blank"] == 0, census
    assert _quiet(
        ["generate", f"{described}", "--out-dir", f"{tmp_path}",
         "--replace", "--seed", "0"]
    )[0] == 0
    twin = tmp_path / "table-twin.xlsx"
    held = _openpyxl_column(twin)
    assert held.count("") == 60, held[:8]
    assert held.count(None) == 0
    again = tmp_path / "again"
    again.mkdir()
    for checked in (table, twin):
        assert _quiet(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{again}", "--replace"]
        )[0] == 0, checked


# -- item 7, a refusal that quotes a record ----------------------------


def test_a_workbook_refusal_names_no_cell_of_an_unsettled_first_row(
    tmp_path: pathlib.Path,
) -> None:
    """Item 7 (MAJOR), plan P4-D286.

    The mixed-storage refusal stood above the first-row decision and
    named the column it refused -- so it printed a cell of a row that
    12 standing among 11 and 13 shows to be a record.
    """
    rows = [
        (1, [workbooks.cell("A1", _CANARY_ONE, "inlineStr"),
             workbooks.cell("B1", "12")]),
        (2, [workbooks.cell("A2", "45000", "", 1),
             workbooks.cell("B2", "11")]),
        (3, [workbooks.cell("A3", "20"), workbooks.cell("B3", "13")]),
    ]
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book(rows, ["yyyy\\-mm\\-dd"], "A1:B3"))
    code, said = _quiet(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
         "--smallest-group", "2"]
    )
    assert code == 1
    assert _CANARY_ONE not in said, said[:400]
    assert "column_1" in said


# -- item 8, a hostile cell reference ----------------------------------


def _stored_package(members: "list[tuple[str, bytes]]") -> bytes:
    """The same package, packed UNCOMPRESSED, so no ratio cap speaks first."""
    buffer = io.BytesIO()
    bundle = zipfile.ZipFile(buffer, "w", zipfile.ZIP_STORED)
    try:
        for name, data in members:
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_STORED
            bundle.writestr(entry, data)
    finally:
        bundle.close()
    return buffer.getvalue()


def _hostile_members(letters: int) -> "list[tuple[str, bytes]]":
    rows = [(1, ['<c r="%s1"><v>1</v></c>' % ("A" * letters)])]
    return [
        ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
        ("xl/styles.xml", _styles(["General"])),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(rows, dimension="A1:A1")),
    ]


def test_a_reference_past_the_last_column_stops_at_once() -> None:
    """The bound itself, asked of the rule rather than of a clock."""
    assert workbook.reference_column("A1") == 1
    assert workbook.reference_column("AB7") == 28
    assert workbook.reference_column("XFD1") == workbook.MAXIMUM_COLUMNS
    past = workbook.reference_column("A" * 160_000 + "1")
    assert past == workbook.MAXIMUM_COLUMNS + 1


def test_a_hostile_cell_reference_is_refused_at_once(
    tmp_path: pathlib.Path,
) -> None:
    """Item 8 (MAJOR), plan P4-D287.

    The walk built the base-26 integer 160,000 letters spell before
    anything asked whether it was past the last column. Measured on
    `c5d09d5` at 10,000, 40,000 and 160,000 letters: 0.011, 0.162 and
    2.592 seconds to refuse ONE invalid cell, in a worksheet of 163 KB
    that no size cap turns away. The bound here is deliberately loose --
    a whole second for work that now takes microseconds -- because a
    timing assertion tight enough to be interesting is one a loaded
    machine fails for the wrong reason.
    """
    table = tmp_path / "hostile.xlsx"
    table.write_bytes(_stored_package(_hostile_members(160_000)))
    began = time.perf_counter()
    with pytest.raises(errors.ProfileError):
        reading.read_table(f"{table}")
    assert time.perf_counter() - began < 1.0


# -- item 9, a legal freeze below the table ----------------------------


def test_a_legal_freeze_below_the_table_loads(
    tmp_path: pathlib.Path,
) -> None:
    """Item 9 (MAJOR), plan P4-D288.

    `ySplit="200"` over a header and 120 records is a layout openpyxl
    accepts. Profiling published `frozen_rows 200` and the loader then
    refused that same description under WB4, with advice to describe the
    table again that repeats the failure for ever.
    """
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "reading", "inlineStr"),
                workbooks.cell("B1", "site", "inlineStr"),
            ],
        )
    ]
    for index in range(120):
        number = 2 + index
        rows += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", f"{index + 1}"),
                    workbooks.cell(f"B{number}", f"s{index % 4}", "inlineStr"),
                ],
            )
        ]
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book(rows, ["General"], "A1:B121", frozen=200))
    openpyxl = pytest.importorskip("openpyxl")
    book = openpyxl.load_workbook(table)
    assert book[book.sheetnames[0]].freeze_panes == "A201"
    assert _profiled(tmp_path, table, "--smallest-group", _FLOOR_FIVE) == 0
    described = tmp_path / "table-profile.json"
    assert _document(described)["source"]["workbook"]["frozen_rows"] == 200
    assert _quiet(
        ["generate", f"{described}", "--out-dir", f"{tmp_path}",
         "--replace", "--seed", "0"]
    )[0] == 0
    again = tmp_path / "again"
    again.mkdir()
    for checked in (table, tmp_path / "table-twin.xlsx"):
        assert _quiet(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{again}", "--replace"]
        )[0] == 0, checked


# -- item 10, a package this reader cannot expand ----------------------


_SHEET_PART = b"xl/worksheets/sheet1.xml"


def _marked_package(mark: str) -> bytes:
    """A workbook whose sheet member is flagged encrypted, or method 99.

    `zipfile` will not WRITE either, so the package is written plainly
    and its local header and central-directory record are then edited.
    """
    raw = bytearray(_stored_package(_hostile_members(1)))
    for signature, flag_at, method_at, len_at, name_at in (
        (b"PK\x03\x04", 6, 8, 26, 30),
        (b"PK\x01\x02", 8, 10, 28, 46),
    ):
        at = raw.find(signature)
        while at >= 0:
            length = struct.unpack_from("<H", raw, at + len_at)[0]
            start = at + name_at
            if bytes(raw[start:start + length]) == _SHEET_PART:
                if mark == "encrypted":
                    flags = struct.unpack_from("<H", raw, at + flag_at)[0]
                    struct.pack_into("<H", raw, at + flag_at, flags | 0x1)
                else:
                    struct.pack_into("<H", raw, at + method_at, 99)
            at = raw.find(signature, at + 4)
    return bytes(raw)


@pytest.mark.parametrize("mark", ["encrypted", "method99"])
def test_a_package_this_reader_cannot_expand_is_refused_in_words(
    tmp_path: pathlib.Path, mark: str
) -> None:
    """Item 10 (MINOR), plan P4-D289.

    Both escaped the reader as a bare `RuntimeError` and a bare
    `NotImplementedError`, with no sentence a person could act on.
    """
    table = tmp_path / "packed.xlsx"
    table.write_bytes(_marked_package(mark))
    listed = [
        (item.flag_bits & 0x1, item.compress_type)
        for item in zipfile.ZipFile(table).infolist()
        if item.filename == _SHEET_PART.decode()
    ]
    assert listed == [(1, 0) if mark == "encrypted" else (0, 99)], listed
    with pytest.raises(errors.ProfileError) as stopped:
        reading.read_table(f"{table}")
    said = f"{stopped.value}"
    assert "packed in a way synthtwin cannot open" in said
    assert "save it again as an ordinary" in said


def test_the_packaging_rule_lets_an_ordinary_package_through() -> None:
    """Stored and deflated members are the two this reader expands."""
    assert not workbook.is_packaged_unreadably(0, zipfile.ZIP_STORED)
    assert not workbook.is_packaged_unreadably(0, zipfile.ZIP_DEFLATED)
    assert workbook.is_packaged_unreadably(0x1, zipfile.ZIP_DEFLATED)
    assert workbook.is_packaged_unreadably(0, 99)

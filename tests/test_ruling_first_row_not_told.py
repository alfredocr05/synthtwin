"""A first row that cannot be told from a record names no column.

Item 8 of the owner's rulings of 2026-09-17 (plan P4-D232). Where a
file's first row cannot be told from a data record -- a title over a
headerless table, or no header at all, on delimited text and on
workbooks alike -- synthtwin publishes placeholder names `column_1`,
`column_2` and so on, never that row's own text, keeps every row of the
file, and asks in the questions file. `--first-row names` publishes the
real names.

THE MEASURED CASE this closes: `subject id` over
`CASE-ZEBRA-471,amber,Northfield` and 239 more records. The title was
stepped over as furniture, the record beneath it became the three
column names, and its text stood in the description, in the plain
summary, in the twin's own header line and in the quality report, with
the table one row short -- on a delimited file and in a workbook alike.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the furniture rule (`reading._stood_under_furniture` forced to False)
  -- `test_a_title_over_a_headerless_table_names_no_column`,
  `test_no_text_of_that_row_reaches_any_file` and
  `test_a_titled_sheet_of_labels_names_no_column`;
* the two withdrawn refusals turned back into refusals -- the moved
  witnesses of `tests/test_p1r6f6_first_row_decision.py`,
  `tests/test_reading_agreement.py`, `tests/test_reading_header_shape.py`
  and `tests/test_reading.py`;
* the furniture rule asked BEFORE the names evidence rather than after
  -- `test_a_title_over_a_real_header_is_still_read_as_names`, and three
  round trips of `tests/test_file_dialect_round_trip.py` whose twin then
  fails its own description at exit 3.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib

from synthtwin import asking, cli
from tests import workbooks

_COLOURS = ("slate", "olive", "rust")
_TOWNS = ("Eastbourne", "Westmill", "Southgate")


def _records(rows: int = 240) -> "list[str]":
    """A headerless table whose first record carries two lone values."""
    made = ["CASE-ZEBRA-471,amber,Northfield"]
    for index in range(1, rows):
        made += [
            f"CASE-ZEBRA-{471 + index},"
            f"{_COLOURS[index % 3]},{_TOWNS[index % 3]}"
        ]
    return made


def _run(folder: pathlib.Path, body: str, *flags: str) -> int:
    """Describe one file in this process; return the exit code."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "table.csv"
    target.write_text(body, encoding="utf-8", newline="")
    return cli.main(
        ["profile", f"{target}", "--out-dir", f"{folder}", "--replace", *flags]
    )


def _document(folder: pathlib.Path) -> dict:
    return json.loads((folder / "table-profile.json").read_text("utf-8"))


def _asked(folder: pathlib.Path) -> "list[dict]":
    """The questions this run put about the FILE."""
    written = json.loads((folder / "table-questions.json").read_text("utf-8"))
    return [
        entry
        for entry in written["about_your_file"]
        if entry["column"] == asking.FIRST_ROW_SUBJECT
    ]


def test_a_title_over_a_headerless_table_names_no_column(
    tmp_path: pathlib.Path,
) -> None:
    """The measured case: a title, then a record taken for the names.

    The title is furniture the survey steps over, and what stands under
    it is the column names as often as it is the first record -- so the
    reading taken is the one that publishes nothing of it.
    """
    body = "subject id\n" + "\n".join(_records()) + "\n"
    assert _run(tmp_path, body) == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "column_1",
        "column_2",
        "column_3",
    ]
    # NOT ONE RECORD IS LOST, which is the other half of the defect: the
    # row taken for the names was described as names and counted out of
    # the rows.
    assert document["n_rows"] == 240
    source = document["source"]
    assert source["header_source"] == "generated"
    assert source["header_by_convention"] is False
    assert "could not be told" in source["header_evidence"]
    # The written names a delimited file publishes are the header's
    # own, and there is no header now.
    assert source["dialect"]["written_names"] == []


def test_the_questions_file_asks_which_reading_is_right(
    tmp_path: pathlib.Path,
) -> None:
    """The ask is in the questions file, and it quotes no cell."""
    body = "subject id\n" + "\n".join(_records()) + "\n"
    assert _run(tmp_path, body) == 0
    asked = _asked(tmp_path)
    assert len(asked) == 1, asked
    entry = asked[0]
    assert entry["read_as_now"] == asking.ANSWER_FIRST_ROW_DATA
    answers = [choice["answer"] for choice in entry["answers_you_can_give"]]
    assert answers == [
        asking.ANSWER_FIRST_ROW_DATA,
        asking.ANSWER_FIRST_ROW_NAMES,
    ]
    spoken = json.dumps(entry)
    for word in ("CASE-ZEBRA-471", "amber", "Northfield", "subject id"):
        assert word not in spoken, word


def test_no_text_of_that_row_reaches_any_file(
    tmp_path: pathlib.Path,
) -> None:
    """At a floor that names no lone value, the row leaves no trace.

    The first record's two label values are lone values of their
    columns, and above a floor of one nothing publishes them -- so the
    description, the summary, the questions file, the twin and the
    twin's report hold no character of them, and none of the title
    either. At the default floor of one they are published exactly as
    every other row's values are, because that row is a row of the table
    now and the floor governs it; that is the floor's decision and not
    this rule's.

    WHAT IS NOT ASSERTED, and why. The first column is read as a number
    wearing a shared piece of text, so the description publishes the
    affix and the ends of the numbers, and a twin cell may spell
    `CASE-ZEBRA-471` because the arithmetic left no other answer. That
    is the qualified record claim CLAUDE.md states, and it is true of
    every row of that column rather than of this one.
    """
    body = "subject id\n" + "\n".join(_records()) + "\n"
    assert _run(tmp_path, body, "--smallest-group", "11") == 0
    described = tmp_path / "table-profile.json"
    assert cli.main(
        [
            "generate", f"{described}", "--out-dir", f"{tmp_path}",
            "--seed", "4", "--replace",
        ]
    ) == 0
    written = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted(tmp_path.iterdir())
        if path.is_file() and path.name != "table.csv"
    )
    for word in ("amber", "Northfield", "subject id"):
        assert word not in written, word
    document = _document(tmp_path)
    for block in document["columns"]:
        assert block["name"] != "CASE-ZEBRA-471"


def test_a_title_over_a_real_header_is_still_read_as_names(
    tmp_path: pathlib.Path,
) -> None:
    """The file's own evidence beats the shape of the file.

    A title over a real header is the commonest shape a spreadsheet
    exports. Where a column below the header holds numbers and the
    header's own value does not, the file SHOWS the row is names, and
    outcome 3 is asked before the furniture rule for exactly that
    reason.
    """
    rows = [f"p{index},{index + 20},north" for index in range(1, 30)]
    body = "Report: cohort extract\ncode,age,site\n" + "\n".join(rows) + "\n"
    assert _run(tmp_path, body) == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "code",
        "age",
        "site",
    ]
    assert document["n_rows"] == 29
    assert _asked(tmp_path) == []


def test_a_blank_line_above_the_table_is_not_furniture(
    tmp_path: pathlib.Path,
) -> None:
    """A spare newline at the top says nothing about the row below it.

    Measured before the rule was narrowed: counting a blank run here
    read `age` over four numbers as a headerless table of five records.
    """
    body = "\ncode,site\n" + "\n".join(
        f"p{index},north" for index in range(1, 20)
    ) + "\n"
    assert _run(tmp_path, body) == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == ["code", "site"]
    assert _asked(tmp_path) == []


def test_the_person_can_say_the_row_holds_the_names(
    tmp_path: pathlib.Path,
) -> None:
    """`--first-row names` publishes the real names, and asks nothing."""
    body = "subject id\n" + "\n".join(_records()) + "\n"
    assert _run(tmp_path, body, "--first-row", "names") == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "CASE-ZEBRA-471",
        "amber",
        "Northfield",
    ]
    assert document["n_rows"] == 239
    assert _asked(tmp_path) == []


def test_the_answer_in_the_questions_file_is_the_declaration(
    tmp_path: pathlib.Path,
) -> None:
    """A person writes `names` in the file, and the next run takes it.

    Answering in the file and typing `--first-row names` are the same
    act, so they end in the same reading -- and an answer the command
    dropped would be an answer a person was told had been heard.
    """
    body = "subject id\n" + "\n".join(_records()) + "\n"
    assert _run(tmp_path, body) == 0
    written = json.loads(
        (tmp_path / "table-questions.json").read_text("utf-8")
    )
    for entry in written["about_your_file"]:
        if entry["column"] == asking.FIRST_ROW_SUBJECT:
            entry["your_answer"] = asking.ANSWER_FIRST_ROW_NAMES
    answered = tmp_path / "answers.json"
    answered.write_text(
        json.dumps(written), encoding="utf-8", newline=""
    )
    again = tmp_path / "again"
    again.mkdir()
    assert cli.main(
        [
            "profile", f"{tmp_path / 'table.csv'}", "--out-dir", f"{again}",
            "--replace", "--answers", f"{answered}",
        ]
    ) == 0
    document = json.loads((again / "table-profile.json").read_text("utf-8"))
    assert [block["name"] for block in document["columns"]] == [
        "CASE-ZEBRA-471",
        "amber",
        "Northfield",
    ]
    assert document["n_rows"] == 239


def test_a_headerless_file_with_no_furniture_is_the_stated_limit(
    tmp_path: pathlib.Path,
) -> None:
    """What this ruling does NOT reach, measured rather than described.

    The same records with no title above them and no value marking the
    first row as a record are still read as names by convention: nothing
    in the file says otherwise, and the only rule that could say it --
    the first row wearing the shape its column's values wear -- reads
    `sites` over `north`, `south` and `east` the same way. It is put to
    the owner in plan P4-D232 rather than built.
    """
    body = "\n".join(_records()) + "\n"
    assert _run(tmp_path, body) == 0
    document = _document(tmp_path)
    assert [block["name"] for block in document["columns"]] == [
        "CASE-ZEBRA-471",
        "amber",
        "Northfield",
    ]
    assert document["source"]["header_by_convention"] is True


def _titled_sheet_of_labels(rows: int = 40) -> bytes:
    """A workbook: a title row of one cell, then records of three texts."""
    strings = ["Cohort extract"]
    for index in range(rows):
        strings += [
            f"CASE-ZEBRA-{471 + index}",
            "amber" if index == 0 else _COLOURS[index % 3],
            "Northfield" if index == 0 else _TOWNS[index % 3],
        ]
    body: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell("A1", "0", "s")])
    ]
    for index in range(rows):
        number = 2 + index
        body += [
            (
                number,
                [
                    workbooks.cell(
                        f"A{number}", f"{1 + index * 3}", "s"
                    ),
                    workbooks.cell(
                        f"B{number}", f"{2 + index * 3}", "s"
                    ),
                    workbooks.cell(
                        f"C{number}", f"{3 + index * 3}", "s"
                    ),
                ],
            )
        ]
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, True, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/sharedStrings.xml", workbooks._shared_strings(strings)),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet(body, dimension=f"A1:C{rows + 1}"),
            ),
        ]
    )


def test_a_titled_sheet_of_labels_names_no_column(
    tmp_path: pathlib.Path,
) -> None:
    """The same shape in a workbook is answered the same way.

    A row of one cell above the table is furniture the workbook reader
    steps over (plan P4-D186), exactly as a title line is in a text
    file, so the row under it cannot be told from a record either.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    target = tmp_path / "book.xlsx"
    target.write_bytes(_titled_sheet_of_labels())
    assert cli.main(
        ["profile", f"{target}", "--out-dir", f"{tmp_path}", "--replace"]
    ) == 0
    document = json.loads(
        (tmp_path / "book-profile.json").read_text("utf-8")
    )
    assert [block["name"] for block in document["columns"]] == [
        "column_1",
        "column_2",
        "column_3",
    ]
    assert document["n_rows"] == 40
    assert document["source"]["header_source"] == "generated"
    written = json.loads(
        (tmp_path / "book-questions.json").read_text("utf-8")
    )
    asked = [
        entry
        for entry in written["about_your_file"]
        if entry["column"] == asking.FIRST_ROW_SUBJECT
    ]
    assert len(asked) == 1, written["about_your_file"]
    # THE TITLE ROW IS STILL FURNITURE, which is why the workbook is
    # asked for records from the HEADER row rather than from the
    # sheet's first: read from the top, `Cohort extract` would be a
    # value of the first column, published at every smallest group,
    # which contract FD11 and plan P4-D80 forbid.
    assert document["source"]["workbook"]["rows_above_header"] == 1
    assert "Cohort extract" not in json.dumps(document)
    # ...AND THE TWIN AND THE BOOK BOTH HOLD THE DESCRIPTION. The
    # validator reads a checked workbook from the row the description
    # starts its records on; read from the sheet's first row instead,
    # the book it was written from missed its own row count and its
    # count of rows above the header.
    described = tmp_path / "book-profile.json"
    assert cli.main(
        [
            "generate", f"{described}", "--out-dir", f"{tmp_path}",
            "--seed", "4", "--replace",
        ]
    ) == 0
    for label, checked in (
        ("twin", tmp_path / "book-twin.xlsx"), ("book", target)
    ):
        folder = tmp_path / f"check-{label}"
        folder.mkdir()
        assert cli.main(
            [
                "validate", f"{described}", "--twin", f"{checked}",
                "--out-dir", f"{folder}", "--replace",
            ]
        ) == 0, label


def test_the_verdict_is_an_enumerated_sentence() -> None:
    """The published sentence has a form behind it, like every other.

    A verdict built at a call site would be the one string in the
    document with no form behind it, and one exception is all a guard
    needs to stop meaning anything.
    """
    from synthtwin import taxonomy

    assert taxonomy.HEADER_NAMES_NOT_TOLD in taxonomy.NOTE_ARITY
    assert taxonomy.NOTE_ARITY[taxonomy.HEADER_NAMES_NOT_TOLD] == 0
    spoken = f"{taxonomy.note(taxonomy.HEADER_NAMES_NOT_TOLD)}"
    assert spoken.endswith(".")
    assert "column_1" in spoken and "--first-row names" in spoken

"""The files review's repairs, each built from the review's own reproduction.

The Codex review of commit 158c811 read the workbook reader, the
workbook writer, the delimiter survey and the command line, and found
six blockers and thirteen majors there, and five more in the merge pass
(plan P4-D164 to P4-D173). Every test below is that reproduction, run
end to end wherever the defect was one a person meets: a realistic
source is written, described, generated, the twin described again, and
BOTH files validated at exit 0 -- and an INDEPENDENT reader (openpyxl or
pandas, which `src/synthtwin` never imports) is asked the question the
defect was about, because a twin that holds every published fact can
still hand a reader a different table.

Every workbook here is assembled by this module out of the standard
library, with fixed zip timestamps (plan D13); the vocabulary is neutral
and made up on the spot.
"""

import contextlib
import io
import json
import pathlib
import random
import sys
import zipfile

import pytest

import crosscheck
import fixtures
from tests.test_stage2_round_trip import describe_with_the_producer
from synthtwin import (
    contract,
    dialect,
    errors,
    parsing,
    reading,
    sheetwriting,
    workbook,
)

# EVERY SHEET THIS FILE DESCRIBES THROUGH THE COMMAND IS WRITTEN AT THE
# POPULATION FLOOR (plan P4-D341): `synthtwin profile` refuses a table
# under it and writes nothing. None of the shapes here is a shape of a
# ROW COUNT -- each is about a header, a sheet name, a format code, a
# storage type or a census -- so each generator is simply run to the
# floor and every count below is derived from that rule. The one
# exception is the census of a table SHORTER than the line, whose
# whole subject is its length; that one is described by the producer,
# which refuses no table for its size.
_FLOOR = parsing.POPULATION_FLOOR

# -- a workbook written by hand ----------------------------------------

_DECLARATION = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_RELS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PACKAGE_RELS = "http://schemas.openxmlformats.org/package/2006/relationships"


def _escaped(text: str) -> str:
    out = text
    for mark, written in (("&", "&amp;"), ("<", "&lt;"), (">", "&gt;"), ('"', "&quot;")):
        out = out.replace(mark, written)
    return out


def _book(
    sheets: "list[tuple[str, str]]",
    strings: "list[str]",
    formats: "tuple[str, ...]" = ("General",),
    pane: str = "",
) -> bytes:
    """A workbook of these sheets: (name, the rows of `<sheetData>`).

    ``strings`` are whole `<si>` elements or plain text; ``formats`` are
    the codes of the cell styles, style `i` wearing `formats[i]`.
    """
    count = len(sheets)
    types = [
        _DECLARATION,
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
        '<Default Extension="rels" ContentType="application/vnd.'
        'openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for number in range(1, count + 1):
        types += [
            f'<Override PartName="/xl/worksheets/sheet{number}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.'
            'spreadsheetml.worksheet+xml"/>'
        ]
    types += [
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.'
        'openxmlformats-officedocument.spreadsheetml.styles+xml"/>',
        '<Override PartName="/xl/sharedStrings.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>',
        "</Types>",
    ]
    book = [_DECLARATION, f'<workbook xmlns="{_MAIN}" xmlns:r="{_RELS}"><sheets>']
    links = [_DECLARATION, f'<Relationships xmlns="{_PACKAGE_RELS}">']
    for place in range(count):
        book += [
            f'<sheet name="{_escaped(sheets[place][0])}" sheetId="{place + 1}" '
            f'r:id="rId{place + 1}"/>'
        ]
        links += [
            f'<Relationship Id="rId{place + 1}" Type="{_RELS}/worksheet" '
            f'Target="worksheets/sheet{place + 1}.xml"/>'
        ]
    book += ["</sheets></workbook>"]
    links += [
        f'<Relationship Id="rId{count + 1}" Type="{_RELS}/styles" Target="styles.xml"/>',
        f'<Relationship Id="rId{count + 2}" Type="{_RELS}/sharedStrings" '
        'Target="sharedStrings.xml"/>',
        "</Relationships>",
    ]
    styles = [_DECLARATION, f'<styleSheet xmlns="{_MAIN}"><numFmts count="{len(formats)}">']
    for place in range(len(formats)):
        styles += [
            f'<numFmt numFmtId="{164 + place}" formatCode="{_escaped(formats[place])}"/>'
        ]
    styles += [
        '</numFmts><fonts count="1"><font><sz val="11"/><name val="Calibri"/>'
        '</font></fonts><fills count="2"><fill><patternFill patternType="none"/>'
        '</fill><fill><patternFill patternType="gray125"/></fill></fills>'
        '<borders count="1"><border><left/><right/><top/><bottom/><diagonal/>'
        '</border></borders><cellStyleXfs count="1"><xf numFmtId="0" fontId="0" '
        f'fillId="0" borderId="0"/></cellStyleXfs><cellXfs count="{len(formats)}">'
    ]
    for place in range(len(formats)):
        identifier = 0 if formats[place] == "General" else 164 + place
        styles += [
            f'<xf numFmtId="{identifier}" fontId="0" fillId="0" borderId="0" '
            'xfId="0" applyNumberFormat="1"/>'
        ]
    styles += ["</cellXfs></styleSheet>"]
    shared = [_DECLARATION, f'<sst xmlns="{_MAIN}">']
    for item in strings:
        shared += [item if item.startswith("<si>") else f"<si><t>{_escaped(item)}</t></si>"]
    shared += ["</sst>"]
    members = [
        ("[Content_Types].xml", "".join(types)),
        (
            "_rels/.rels",
            _DECLARATION + f'<Relationships xmlns="{_PACKAGE_RELS}"><Relationship '
            f'Id="rId1" Type="{_RELS}/officeDocument" Target="xl/workbook.xml"/>'
            "</Relationships>",
        ),
        ("xl/workbook.xml", "".join(book)),
        ("xl/_rels/workbook.xml.rels", "".join(links)),
        ("xl/styles.xml", "".join(styles)),
        ("xl/sharedStrings.xml", "".join(shared)),
    ]
    for place in range(count):
        members += [
            (
                f"xl/worksheets/sheet{place + 1}.xml",
                _DECLARATION + f'<worksheet xmlns="{_MAIN}" xmlns:r="{_RELS}">'
                f"{pane}<sheetData>{sheets[place][1]}</sheetData></worksheet>",
            )
        ]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, text in members:
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, text)
    return buffer.getvalue()


def _cell(reference: str, value: str, kind: str = "", style: int = 0) -> str:
    marks = f' r="{reference}"' + (f' t="{kind}"' if kind else "")
    marks = marks + (f' s="{style}"' if style else "")
    return f"<c{marks}><v>{_escaped(value)}</v></c>"


def _rows(grid: "dict[int, list[str]]") -> str:
    return "".join(
        f'<row r="{number}">' + "".join(grid[number]) + "</row>"
        for number in sorted(grid)
    )


# -- the commands, run in this process ---------------------------------


def _exit_of(argv: "list[str]") -> "tuple[int, str]":
    """One synthtwin command: its exit code, and what it said."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = cli.main()
            except SystemExit as stop:
                code = 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code, out.getvalue() + err.getvalue()


def _missed(report: pathlib.Path) -> "list[str]":
    return [
        line.strip()
        for line in report.read_text(encoding="utf-8").splitlines()
        if line.strip().endswith("MISSED")
    ]


def _trip(
    folder: pathlib.Path,
    name: str,
    data: bytes,
    flags: "tuple[str, ...]" = (),
    suffix: str = ".xlsx",
    seed: int = 4,
    checked: "tuple[str, ...]" = (),
    by_command: bool = True,
) -> "dict[str, object]":
    """Describe, generate, describe the twin, and validate BOTH at exit 0.

    ``by_command`` FALSE DESCRIBES WITH THE PRODUCER (plan P4-D341),
    for the one shape here whose subject is a table SHORTER than the
    disclosure line: the command refuses a table under the population
    floor, and growing that one past it is deleting the case. Nothing
    else changes -- the twin is built, both files are checked and the
    twin is described again by the commands, exactly as before.
    """
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / f"{name}{suffix}"
    source.write_bytes(data)
    described = folder / f"{name}-profile.json"
    if by_command:
        code, said = _exit_of(
            ["profile", str(source), "--out-dir", str(folder)] + list(flags)
        )
        assert code == 0, said[-600:]
    else:
        describe_with_the_producer(source, described, flags)
    code, said = _exit_of(["generate", str(described), "--seed", f"{seed}"])
    assert code == 0, said[-600:]
    twin = folder / f"{name}-twin{suffix}"
    real_check = folder / "real-check"
    twin_check = folder / "twin-check"
    again = folder / "again"
    for made in (real_check, twin_check, again):
        made.mkdir()
    real_code, _said = _exit_of(
        ["validate", str(described), "--twin", str(source), "--out-dir", str(real_check)]
        + list(checked)
    )
    twin_code, _said = _exit_of(
        ["validate", str(described), "--twin", str(twin), "--out-dir", str(twin_check)]
        + list(checked)
    )
    if by_command:
        code, said = _exit_of(
            ["profile", str(twin), "--out-dir", str(again)] + list(flags)
        )
        assert code == 0, said[-600:]
    else:
        describe_with_the_producer(
            twin, again / f"{name}-twin-profile.json", flags
        )
    return {
        "source": source,
        "twin": twin,
        "described": described,
        "document": json.loads(described.read_text(encoding="utf-8")),
        "again": json.loads(
            (again / f"{name}-twin-profile.json").read_text(encoding="utf-8")
        ),
        "real_missed": _missed(real_check / f"{name}-quality.txt"),
        "twin_missed": _missed(twin_check / f"{name}-twin-quality.txt"),
        "exits": {"real": real_code, "twin": twin_code},
    }


def _held(result: "dict[str, object]") -> None:
    assert result["exits"] == {"real": 0, "twin": 0}, (
        result["exits"], result["real_missed"], result["twin_missed"],
    )


# -- item 1: a sparse sheet may not buy a table of a million cells -----


def test_a_sparse_sheet_is_refused_before_its_table_is_built(
    tmp_path: pathlib.Path,
) -> None:
    """Files review, BLOCKER 1 (plan P4-D165).

    `A1` and `ALM1001` are two stored cells, well inside the cap on cells
    stored, and they span a table of 1,001,000 cells: 1,001 rows by
    1,000 columns. It was admitted and built. It is refused now, by the
    cap on the table's rectangle, and the refusal says why.
    """
    body = _rows({1: [_cell("A1", "0", "s")], 1001: [_cell("ALM1001", "10")]})
    source = tmp_path / "sparse.xlsx"
    source.write_bytes(_book([("Data", body)], ["reading"]))
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(source))
    assert "stretches across more than 1000000 cells" in f"{raised.value}"


# -- item 2: a blank header cell may not publish a person's row --------


def _headed_with_a_blank(records: int = _FLOOR) -> bytes:
    strings = ["record_key", "arm", "CASE-ZEBRA-471", "amber", "blue"]
    grid = {
        1: [_cell("A1", "0", "s"), _cell("C1", "1", "s")],
        2: [_cell("A2", "2", "s"), _cell("B2", "37"), _cell("C2", "3", "s")],
    }
    for place in range(records - 1):
        number = 3 + place
        strings += [f"CASE-{1000 + place}"]
        grid[number] = [
            _cell(f"A{number}", f"{len(strings) - 1}", "s"),
            _cell(f"B{number}", f"{20 + place}"),
            _cell(f"C{number}", f"{3 + place % 2}", "s"),
        ]
    return _book([("Data", _rows(grid))], strings)


def test_a_header_with_a_blank_cell_is_the_header(tmp_path: pathlib.Path) -> None:
    """Files review, BLOCKER 2 (plan P4-D165).

    THE REPRODUCTION. A header `record_key`, blank, `arm` over thirty-one
    records was two cells wide against records of three, so the rule
    that took the first row as wide as the widest stepped over it: the
    first record became the column names -- `CASE-ZEBRA-471`, `37`,
    `amber`, published whole at a floor of five -- and the table lost
    that record. The header is the first row holding two cells now.
    """
    result = _trip(tmp_path, "blank", _headed_with_a_blank(), ("--smallest-group", "5"))
    _held(result)
    document = result["document"]
    assert [one["name"] for one in document["columns"]] == [
        "record_key", "Unnamed: 1", "arm",
    ]
    assert document["n_rows"] == _FLOOR
    assert document["source"]["workbook"]["rows_above_header"] == 0
    assert b"CASE-ZEBRA-471" not in result["described"].read_bytes()
    # The twin's header leaves the same cell blank, so every reader names
    # its columns the way it names the source's. Everything above is
    # synthtwin reading its own files, so the second reader is asked last.
    sheet = crosscheck.reader().load_workbook(result["twin"]).worksheets[0]
    assert sheet["B1"].value is None
    assert list(crosscheck.read_excel(result["twin"]).columns) == list(
        crosscheck.read_excel(result["source"]).columns
    )


def test_first_row_data_is_honoured_on_a_workbook(tmp_path: pathlib.Path) -> None:
    """Files review, BLOCKER 2's second half (plan P4-D165).

    `--first-row data` was dropped on the workbook branch, so a person
    who said their first row was a record still had it published as
    names. Every row is a record now and the columns are named for their
    places.
    """
    result = _trip(tmp_path, "data", _headed_with_a_blank(), ("--first-row", "data"))
    _held(result)
    document = result["document"]
    # One more than the header reading keeps: the header row becomes a
    # record, which is what `--first-row data` says.
    assert document["n_rows"] == _FLOOR + 1
    assert document["source"]["header_source"] == "generated"
    assert [one["name"] for one in document["columns"]] == [
        "column_1", "column_2", "column_3",
    ]


def test_a_header_that_reads_as_a_record_stops_and_asks(
    tmp_path: pathlib.Path,
) -> None:
    """An undeclared header whose cells read as a record is asked about.

    The question a delimited file's first row has always been put to
    reaches a workbook's header too (plan P4-D165): a header whose cell
    is a number lying among its column's numbers is a record's cell.

    IT IS ASKED IN THE QUESTIONS FILE NOW AND NOT BY A REFUSAL (the
    owner's ruling of 2026-09-17, item 8; plan P4-D232). The reading
    taken is the one that publishes nothing of that row -- synthtwin's
    own column names, every row kept -- and the words of what was seen
    are carried for the questions file, naming the column by its
    position and quoting no cell.
    """
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "37")]}
    for place in range(30):
        number = 2 + place
        grid[number] = [_cell(f"A{number}", "1", "s"), _cell(f"B{number}", f"{20 + place}")]
    source = tmp_path / "numbered.xlsx"
    source.write_bytes(_book([("Data", _rows(grid))], ["CASE-ZEBRA-471", "amber"]))
    table = reading.read_table(str(source))
    assert list(table.column_names) == ["column_1", "column_2"]
    assert table.n_rows == 31
    assert table.first_row_seen
    assert "column 2" in table.first_row_seen
    assert "ZEBRA" not in table.first_row_seen


# -- item 3: an answer of `data` is an answer --------------------------


def test_an_answer_of_data_overrides_a_typed_metadata_declaration(
    tmp_path: pathlib.Path,
) -> None:
    """Files review, BLOCKER 3 (plan P4-D172).

    THE REPRODUCTION. Two columns, a person's record under the names,
    then an `ImportId` marker row, then two more records. The questions
    file was answered `data` and the command run with `--metadata-rows
    2`: the answer is nought rows, a truthiness test read nought as no
    answer, and both rows were published as `header_rows`. Four records
    became two.
    """
    # AT THE POPULATION FLOOR (plan P4-D341): the four records of the
    # reproduction are the two named rows and the two below them, and
    # the rest are the same shape repeated, so the count the command
    # describes is derived from the rule.
    people = [
        "person,result",
        "Person-ZETA-000,private-result-000",
        '{"ImportId":"person"},{"ImportId":"result"}',
    ]
    while len(people) - 1 < _FLOOR:
        people += [f"Person-{len(people) - 2},result-{len(people) - 2}"]
    source = tmp_path / "real.csv"
    source.write_bytes(("\n".join(people) + "\n").encode())
    code, said = _exit_of(["profile", str(source), "--out-dir", str(tmp_path)])
    assert code == 0, said[-400:]
    questions = json.loads((tmp_path / "real-questions.json").read_text(encoding="utf-8"))
    assert questions["about_your_file"], questions
    for entry in questions["about_your_file"]:
        entry["your_answer"] = "data"
    answers = tmp_path / "answered.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    second = tmp_path / "second"
    second.mkdir()
    code, said = _exit_of(
        ["profile", str(source), "--out-dir", str(second), "--metadata-rows", "2",
         "--answers", str(answers)]
    )
    assert code == 0, said[-400:]
    described = json.loads((second / "real-profile.json").read_text(encoding="utf-8"))
    assert described["n_rows"] == _FLOOR
    assert described["source"]["dialect"]["header_rows"] == []
    assert b"Person-ZETA-000" not in (second / "real-profile.json").read_bytes()


# -- item 4: no census reveals a count under the line ------------------


def _hundred_mixed() -> bytes:
    strings = ["value", "North", "South", "East"]
    grid = {1: [_cell("A1", "0", "s")]}
    for place in range(100):
        number = 2 + place
        if place < 60:
            grid[number] = [_cell(f"A{number}", f"{place}")]
        elif place < 99:
            grid[number] = [_cell(f"A{number}", f"{1 + place % 3}", "s")]
        else:
            grid[number] = [_cell(f"A{number}", "1", "b")]
    return _book([("Data", _rows(grid))], strings)


@pytest.mark.parametrize("floor", ["1", "5"])
def test_a_workbook_census_names_no_count_under_the_line(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """Files review, BLOCKER 4 (plan P4-D164).

    THE REPRODUCTION. Sixty numbers, thirty-nine texts and one boolean.
    At the default floor the boolean's count of 1 was published; at a
    floor of five the census read `60, 39, null` beside noughts, and
    100 - 60 - 39 rebuilt it. Neither survives: no published count, no
    complement and no difference a reader can take is under the line,
    and the loader holds a census to the same rule.
    """
    result = _trip(tmp_path, "mixed", _hundred_mixed(), ("--smallest-group", floor))
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    published = [one for one in census.values() if one is not None]
    assert 1 not in published and 99 not in published, census
    assert census["boolean"] is None
    assert dialect.sheet_census_broken(census, 100, int(floor)) == ""
    withheld = 100 - sum(published)
    assert withheld == 0 or withheld >= dialect.sheet_line(int(floor)), census
    # The census the review measured is refused by name.
    measured = {
        "absent": 0, "blank": 0, "boolean": None, "date": 0, "empty": 0,
        "error": 0, "number": 60, "text": 39,
    }
    assert dialect.sheet_census_broken(measured, 100, 5) != ""
    # A WITHHELD COUNT NEVER SAYS "SOME, BUT FEW". Four texts and four
    # booleans beside ninety-two numbers at a floor of five are withheld
    # together; the noughts beside them are withheld too, or a reader
    # would know each withheld count is at least one.
    every = dialect.SHEET_CELL_CLASSES
    held = dialect.sheet_census({"number": 92, "text": 4, "boolean": 4}, every, 100, 5)
    assert held["number"] == 92
    assert [key for key in every if key != "number" and held[key] is not None] == []
    noughts = dict(held)
    for key in every:
        if key not in ("number", "text", "boolean"):
            noughts[key] = 0
    assert "nought" in dialect.sheet_census_broken(noughts, 100, 5)


# -- item 5 and 12: sheet names ----------------------------------------


def _table_rows(records: int = _FLOOR) -> str:
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(records):
        number = 2 + place
        grid[number] = [_cell(f"A{number}", f"{place}"), _cell(f"B{number}", f"{place % 3}")]
    return _rows(grid)


def test_a_sheet_named_with_a_long_number_is_withheld(tmp_path: pathlib.Path) -> None:
    """Files review, BLOCKER 5 (plan P4-D171).

    THE REPRODUCTION. A sheet called `Report123456789` survived whole at
    a floor of five, because the name rule stripped any number of
    figures to test the stem and then published the name. One or two
    figures, not beginning with a nought, is all a published name may end
    in now, and the loader refuses a description that names more.
    """
    notes = _rows({1: [_cell("A1", "2", "s")]})
    data = _book(
        [("Data", _table_rows()), ("Report123456789", notes)],
        ["reading", "site", "note"],
    )
    result = _trip(tmp_path, "named", data, ("--smallest-group", "5"))
    _held(result)
    assert result["document"]["source"]["workbook"]["sheet_names"] == ["Data", None]
    assert b"123456789" not in result["described"].read_bytes()
    assert dialect.sheet_name_published("Report123456789") is None
    assert dialect.sheet_name_published("Sheet12") == "Sheet12"
    assert dialect.sheet_name_published("Sheet01") is None


def test_a_placeholder_is_never_a_published_name_in_another_case(
    tmp_path: pathlib.Path,
) -> None:
    """Files review, MAJOR 12 (plan P4-D171).

    THE REPRODUCTION. Sheets `Private notes` and `sheet1` published as
    `[null, "sheet1"]` and the twin allocated `Sheet1` beside `sheet1`,
    which a spreadsheet cannot hold: openpyxl renamed the published sheet
    `sheet11`, and validation missed nothing.
    """
    notes = _rows({1: [_cell("A1", "2", "s")]})
    data = _book(
        [("Private notes", notes), ("sheet1", _table_rows())],
        ["reading", "site", "note"],
    )
    result = _trip(
        tmp_path, "cased", data, ("--sheet", "sheet1"), checked=("--sheet", "sheet1")
    )
    _held(result)
    assert result["document"]["source"]["workbook"]["sheet_names"] == [None, "sheet1"]
    assert dialect.twin_sheet_names((None, "sheet1")) == ("Sheet2", "sheet1")
    assert crosscheck.reader().load_workbook(result["twin"]).sheetnames == [
        "Sheet2", "sheet1",
    ]


# -- item 6 and merge item 2: storage types and their values -----------


def test_a_column_mixing_numbers_and_numeric_text_is_read(
    tmp_path: pathlib.Path,
) -> None:
    """Files review, BLOCKER 6 (plan P4-D166), reversed in part by P4-D187.

    THE REPRODUCTION. Thirty numeric cells of 10 and thirty text cells of
    `1000`: at seed 0 half of each value took the other storage type and
    validation reported nothing missed, so P4-D166 refused the column.
    A file the person expects to read must be read (P4-D187): the text
    cells are read as text holding figures, both counts are published,
    the twin writes thirty of each, and its report says which values
    were which is not kept. A column whose NUMBERS wear a date format
    and a plain one is still refused.
    """
    # HALF THE FLOOR OF EACH STORAGE TYPE (plan P4-D341): the shape is
    # "as many numeric cells as text cells, all of them the same two
    # values", and the table is written at the floor because the
    # command refuses a smaller one.
    half = _FLOOR // 2
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "2", "s")]}
    for place in range(2 * half):
        number = 2 + place
        value = (
            _cell(f"A{number}", "10") if place < half
            else _cell(f"A{number}", "1", "s")
        )
        grid[number] = [value, _cell(f"B{number}", f"{place % 3}")]
    result = _trip(tmp_path / "typed", "typed", _book([("Data", _rows(grid))], ["v", "1000", "k"]))
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert (census["number"], census["text"]) == (half, half), census
    report = (tmp_path / "typed" / "typed-twin-report.txt").read_text(encoding="utf-8")
    assert (
        f"stores {half} of its values as text and {half} as numbers,"
        in report
    )

    dated = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(20):
        number = 2 + place
        dated[number] = [
            _cell(f"A{number}", "45000", "", 1 if place < 10 else 2),
            _cell(f"B{number}", f"{place}"),
        ]
    other = tmp_path / "formatted.xlsx"
    other.write_bytes(
        _book([("Data", _rows(dated))], ["v", "k"], ("General", "yyyy-mm-dd", "[h]:mm:ss"))
    )
    code, said = _exit_of(["profile", str(other), "--out-dir", str(tmp_path)])
    assert code != 0
    assert "more than one kind of number format" in said, said[-500:]


def test_error_and_boolean_cells_keep_their_values(tmp_path: pathlib.Path) -> None:
    """Files review merge pass, MAJOR 2 (plan P4-D166).

    THE REPRODUCTION. A column repeating an `#N/A` error, `North` and
    `South` forty times: pandas read the source as 40, 40 and 40 missing
    and the twin as 27, 27 and 66, because the error count was handed to
    labels in row order. A boolean beside labels lost its booleans the
    same way. A class goes only to a cell spelled the way it is written.
    """
    runs = []
    for name, odd in (("errors", lambda row: _cell(f"A{row}", "#N/A", "e")),
                      ("booleans", lambda row: _cell(f"A{row}", f"{row % 2}", "b"))):
        grid = {1: [_cell("A1", "0", "s")]}
        for place in range(120):
            number = 2 + place
            grid[number] = [odd(number) if place % 3 == 0 else _cell(
                f"A{number}", f"{place % 3}", "s"
            )]
        result = _trip(tmp_path / name, name, _book([("Data", _rows(grid))], ["v", "North", "South"]))
        _held(result)
        runs.append((name, result))
    # Both shapes are described, generated and validated above; the
    # second reader is asked about them once both have been.
    for name, result in runs:
        held = crosscheck.read_excel(result["source"])["v"].astype(str)
        source = held.value_counts().to_dict()
        made = crosscheck.read_excel(result["twin"])["v"].astype(str)
        twin = made.value_counts().to_dict()
        assert twin == source, (name, source, twin)


# -- item 7: a bracket in a format code is not a date ------------------


@pytest.mark.parametrize("code", ["[Red]0.00", "[$USD-409]#,##0.00"])
def test_a_colour_or_a_currency_does_not_make_a_date(
    tmp_path: pathlib.Path, code: str
) -> None:
    """Files review, MAJOR 7 (plan P4-D169).

    THE REPRODUCTION. Sixty values `101.25` to `160.25` formatted
    `[Red]0.00` were classed as dates by the `d` of `Red`; pandas read
    floats from the source and datetimes from the twin, and validation
    missed nothing. An elapsed count in brackets is still elapsed.
    """
    grid = {1: [_cell("A1", "0", "s")]}
    for place in range(_FLOOR):
        number = 2 + place
        grid[number] = [_cell(f"A{number}", f"{101.25 + place}", "", 1)]
    result = _trip(tmp_path, "coloured", _book([("Data", _rows(grid))], ["amount"], ("General", code)))
    _held(result)
    kinds = result["document"]["source"]["workbook"]["columns"][0]["format_kinds"]
    assert kinds["plain"] == _FLOOR, kinds
    assert workbook.format_kind("[h]:mm:ss") == dialect.SHEET_FORMAT_ELAPSED
    assert workbook.format_kind("[mm]:ss") == dialect.SHEET_FORMAT_ELAPSED
    assert workbook.format_kind("[$-409]d-mmm-yy") == dialect.SHEET_FORMAT_DATE
    assert str(crosscheck.read_excel(result["twin"])["amount"].dtype) == "float64"


# -- items 8 and 9: a second table, and refusals that name positions ---


def test_a_second_table_one_column_wide_is_refused(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 8 (plan P4-D170).

    THE REPRODUCTION. A second sheet holding a header `site` over thirty
    values was accepted, because a table had to be two columns wide, and
    every one of its cells came back as the withheld word with nothing
    missed. Any block of two rows is records.
    """
    column = {1: [_cell("A1", "2", "s")]}
    for place in range(30):
        column[2 + place] = [_cell(f"A{2 + place}", f"{100 + place}")]
    source = tmp_path / "second.xlsx"
    source.write_bytes(
        _book([("Data", _table_rows()), ("Sheet1", _rows(column))], ["reading", "site", "site"])
    )
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(source))
    assert "holds a table on the sheet 'Sheet1'" in f"{raised.value}"


def test_a_checked_workbook_refusal_names_no_sheet(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 9 (plan P4-D170).

    THE REPRODUCTION. Reading a two-table workbook for the validator,
    which asks for refusals by position, printed its second sheet's name
    -- `PERSON-ZEBRA-471` -- twice. The workbook branch drops nothing of
    that request now, for the second table, an unknown sheet and an
    empty one alike.

    EACH LOOK IS AT THE MESSAGE APART FROM THE PATH. A refusal may name
    the file it was pointed at and may not name what is inside it, and
    both sit in one string; on Windows pytest's `tmp_path` runs through
    `AppData`, which holds `Data`, the first sheet's own name, so this
    test reported a leak on every Windows cell where the refusal had
    leaked nothing. `fixtures.aside_from_the_path` is what the test
    always meant, and `test_a_refusal_s_own_path_is_not_a_leaked_sheet_name`
    below builds that Windows path here and proves it.
    """
    source = tmp_path / "checked.xlsx"
    source.write_bytes(
        _book([("Data", _table_rows()), ("PERSON-ZEBRA-471", _table_rows())], ["a", "b"])
    )
    positions = reading.REFUSALS_NAME_POSITIONS
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(source), refusals=positions)
    assert "ZEBRA" not in fixtures.aside_from_the_path(f"{raised.value}", source)
    assert "sheet number 2" in f"{raised.value}"
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(source), refusals=positions, sheet="Nope")
    said = fixtures.aside_from_the_path(f"{raised.value}", source)
    assert "ZEBRA" not in said and "Data" not in said
    empty = tmp_path / "empty.xlsx"
    empty.write_bytes(_book([("PERSON-ZEBRA-471", "")], ["a"]))
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(empty), refusals=positions)
    assert "ZEBRA" not in fixtures.aside_from_the_path(f"{raised.value}", empty)


# The path a Windows cell of the matrix actually gave the test above,
# copied out of the run that failed (job 106160150046 of CI run
# 35541541720). `AppData` is not a choice pytest makes -- it is where
# `TEMP` points on a GitHub-hosted Windows runner and on most Windows
# machines -- so this is the shape, not one unlucky path.
_A_WINDOWS_TEMPORARY_PATH = (
    "C:\\Users\\runneradmin\\AppData\\Local\\Temp\\pytest-of-runneradmin"
    "\\pytest-0\\test_a_checked_workbook_refusa0\\checked.xlsx"
)


def test_a_refusal_s_own_path_is_not_a_leaked_sheet_name() -> None:
    """The Windows shape of that refusal, built HERE, on a machine that is not Windows.

    THIS IS THE RED CHECK for the repair above, and it is the point of
    the repair: the difference between the platforms was a path, so the
    path is constructed rather than waited for. The first assertion is
    the defect -- the sheet name `Data` is findable in the refusal's
    text, and it is findable only because the path says `AppData`. The
    second is the repair. The third is the thing the whole test exists
    for, still caught: a refusal that really does print a sheet name is
    still reported, with the path taken out or not.

    Before the repair this file's `test_a_checked_workbook_refusal_names_no_sheet`
    passed here and failed on five Windows cells. After it, the defect
    it was failing on fails here too.
    """
    message = errors.checked_workbook_sheet_not_found(_A_WINDOWS_TEMPORARY_PATH, 2)
    assert "Data" in message
    said = fixtures.aside_from_the_path(message, _A_WINDOWS_TEMPORARY_PATH)
    assert "Data" not in said and "ZEBRA" not in said
    assert "no sheet by the name given after --sheet" in said
    leaked = errors.checked_workbook_sheet_not_found(
        _A_WINDOWS_TEMPORARY_PATH, 2
    ) + " The sheets are Data and PERSON-ZEBRA-471."
    still_seen = fixtures.aside_from_the_path(leaked, _A_WINDOWS_TEMPORARY_PATH)
    assert "ZEBRA" in still_seen and "Data" in still_seen
    # And a POSIX path, where the defect never showed, reads the same way.
    posix = "/tmp/pytest-of-alfredo/pytest-0/test_a_checked_workbook_refusa0/checked.xlsx"
    clean = fixtures.aside_from_the_path(
        errors.checked_workbook_sheet_not_found(posix, 2), posix
    )
    assert "Data" not in clean and "ZEBRA" not in clean


# -- item 10 and merge item 3: only a cell's own text is its value -----


def test_a_phonetic_run_and_indentation_are_not_data(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 10 and merge pass MAJOR 3 (plan P4-D167).

    THE REPRODUCTIONS. A shared string whose visible text is `alpha` and
    whose phonetic run reads `READING` was read as `alphaREADING`, and
    an inline string written `<is>` newline, `<t>North</t>`, newline
    `</is>` kept the indentation in its value; both twins carried the
    wrong text and both files validated. The independent reader is the
    judge of what the value is.
    """
    items = [
        '<si><t>alpha</t><rPh sb="0" eb="5"><t>READING</t></rPh></si>',
        "<si><t>v</t></si>",
        '<si><r><t>be</t></r><r><t>ta</t></r><rPh sb="0" eb="2"><t>B</t></rPh></si>',
    ]
    grid = {1: [_cell("A1", "1", "s")]}
    for place in range(_FLOOR):
        grid[2 + place] = [_cell(f"A{2 + place}", "0" if place % 2 else "2", "s")]
    phonetic = _trip(
        tmp_path / "phonetic", "phonetic", _book([("Data", _rows(grid))], items)
    )
    _held(phonetic)
    assert b"READING" not in phonetic["described"].read_bytes()

    inline = '<row r="1"><c r="A1" t="inlineStr"><is><t>v</t></is></c></row>' + "".join(
        f'<row r="{2 + place}"><c r="A{2 + place}" t="inlineStr"><is>\n <t>North</t>\n'
        f' <rPh sb="0" eb="5"><t>NORTH</t></rPh>\n </is></c></row>'
        for place in range(_FLOOR)
    )
    result = _trip(tmp_path / "inline", "inline", _book([("Data", inline)], []))
    _held(result)
    assert b"NORTH" not in result["described"].read_bytes()
    # Both twins are written before either is handed to the second reader.
    source = sorted(crosscheck.read_excel(phonetic["source"])["v"].tolist())
    assert sorted(crosscheck.read_excel(phonetic["twin"])["v"].tolist()) == source
    assert crosscheck.read_excel(result["twin"])["v"].tolist() == ["North"] * _FLOOR


# -- item 11 and merge item 4: the table keeps its place ---------------


def test_the_columns_before_a_table_are_kept(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 11 and merge pass MAJOR 4 (plan P4-D165).

    THE REPRODUCTION. Headers `x` and `y` in `B1:C1` over 120 records:
    pandas read the source as 120 by 3 and the twin as 120 by 2, both
    validated, and code reaching a column by its position reached a
    different one.
    """
    grid = {1: [_cell("B1", "0", "s"), _cell("C1", "1", "s")]}
    for place in range(120):
        number = 2 + place
        grid[number] = [_cell(f"B{number}", f"{place}"), _cell(f"C{number}", f"{place % 7}")]
    result = _trip(tmp_path, "offset", _book([("Data", _rows(grid))], ["x", "y"]))
    _held(result)
    assert crosscheck.read_excel(result["source"]).shape == (120, 3)
    assert crosscheck.read_excel(result["twin"]).shape == (120, 3)
    assert list(crosscheck.read_excel(result["twin"]).columns) == [
        "Unnamed: 0", "x", "y",
    ]


# -- item 13 and merge item 5: a date stored as a date -----------------


def test_an_iso_date_cell_stays_a_date(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 13 and merge pass MAJOR 5 (plan P4-D168).

    THE REPRODUCTION. 120 `t="d"` cells were counted as numbers because
    the reader had no branch for them, and the twin wrote them as TEXT:
    pandas read datetimes from the source and strings from the twin, and
    the twin missed `workbook.cell-classes` on 120 cells. They are their
    own class now and written back as date cells.
    """
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(120):
        number = 2 + place
        grid[number] = [
            f'<c r="A{number}" t="d" s="1"><v>2024-01-{1 + place % 28:02d}T00:00:00</v></c>',
            _cell(f"B{number}", f"{place % 5}"),
        ]
    result = _trip(
        tmp_path, "dated", _book([("Data", _rows(grid))], ["when", "k"], ("General", "yyyy-mm-dd"))
    )
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert census["date"] == 120 and census["number"] == 0, census
    with zipfile.ZipFile(result["twin"]) as bundle:
        assert 't="d"' in bundle.read("xl/worksheets/sheet1.xml").decode("utf-8")
    source_dtype = crosscheck.read_excel(result["source"])["when"].dtype
    assert str(source_dtype).startswith("datetime64")
    twin_dtype = crosscheck.read_excel(result["twin"])["when"].dtype
    assert str(twin_dtype).startswith("datetime64")


# -- item 14: a withheld format is not a licence for plain -------------


def test_a_withheld_format_census_is_not_written_plain() -> None:
    """Files review, MAJOR 14 (plan P4-D166).

    THE REPRODUCTION. Twenty numbers wearing a date and an elapsed format
    at a floor of eleven published `plain 0, date null, elapsed null`,
    and the twin wrote `plain 20`. The producer no longer publishes a
    nought beside a withheld count and the loader refuses one (WB3); the
    writer, handed such a census anyway, writes no plain cell.
    """
    census: "dict[str, int | None]" = {
        "plain": 0, "date": None, "datetime": 0, "time": 0, "elapsed": None, "text": 0,
    }
    classes = tuple("number" for _row in range(20))
    kinds = sheetwriting.cell_format_kinds(census, classes, "[h]:mm:ss")
    assert "plain" not in kinds, kinds
    assert dialect.sheet_census_broken(census, 20, 11) != ""


# -- item 15: a split pane freezes nothing -----------------------------


def test_a_split_pane_is_not_a_frozen_row_count(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 15 (plan P4-D169).

    THE REPRODUCTION. A pane `state="split" ySplit="3000"` published
    `frozen_rows: 3000` and the workbook's own description then failed
    WB4 as though it had been edited, so generation stopped.
    """
    pane = (
        '<sheetViews><sheetView workbookViewId="0"><pane ySplit="3000" '
        'topLeftCell="A10" activePane="bottomLeft" state="split"/></sheetView>'
        "</sheetViews>"
    )
    result = _trip(tmp_path, "split", _book([("Data", _table_rows())], ["a", "b"], pane=pane))
    _held(result)
    assert result["document"]["source"]["workbook"]["frozen_rows"] == 0
    frozen = pane.replace('state="split"', 'state="frozen"').replace("3000", "2")
    other = _trip(tmp_path / "frozen", "frozen", _book([("Data", _table_rows())], ["a", "b"], pane=frozen))
    assert other["document"]["source"]["workbook"]["frozen_rows"] == 2


# -- item 16: a declaration names a headerless table's columns too -----


def test_a_headerless_decimal_comma_column_keeps_its_order(
    tmp_path: pathlib.Path,
) -> None:
    """Files review, MAJOR 16 (plan P4-D172).

    THE REPRODUCTION. 120 headerless semicolon rows of four-figure
    identifiers and amounts `0,1` to `12,0`, declared `--first-row data
    --delimiter ';' --decimal-comma column_2`: the setting was recorded
    and the order not published, because the declaration was matched
    against a header the table does not have, and seed 4 wrote 59
    descending pairs. The headed equivalent wrote none.
    """
    draw = random.Random(41)
    lines = [
        f"{draw.randint(1000, 9999)};{(place + 1) / 10:.1f}".replace(".", ",")
        for place in range(120)
    ]
    data = ("\n".join(lines) + "\n").encode()
    flags = ("--first-row", "data", "--delimiter", ";", "--decimal-comma", "column_2")
    result = _trip(tmp_path, "headerless", data, flags, suffix=".csv")
    assert result["exits"]["real"] == 0, result["real_missed"]
    order = result["document"]["source"]["dialect"]["row_order"]
    assert order == {"collation": "decimal_comma", "column": 2, "direction": "ascending"}
    assert not [one for one in result["twin_missed"] if one.startswith("rows.order")]
    written = [
        float(line.split(";")[1].replace(",", "."))
        for line in result["twin"].read_text(encoding="utf-8").splitlines()
        if line
    ]
    assert sum(1 for left, right in zip(written, written[1:]) if right < left) == 0


# -- item 17: a less-than sign is not markup ---------------------------


def test_a_table_opening_with_a_less_than_sign_is_read(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 17 (plan P4-D172).

    THE REPRODUCTION. `<5 ng/mL,group` over three ordinary records read
    correctly at 53bb012 and was refused as a web page by this snapshot.
    Markup is refused where the bytes open like markup.
    """
    source = tmp_path / "limit.csv"
    source.write_bytes(b"<5 ng/mL,group\n1,a\n2,b\n3,c\n")
    found = reading.read_table(str(source), first_row=reading.FIRST_ROW_NAMES)
    assert found.column_names == ["<5 ng/mL", "group"]
    assert found.n_rows == 3
    for page in (b"<html><body></body></html>", b"\xef\xbb\xbf <?xml version='1.0'?><x/>",
                 b"<!DOCTYPE html>", b"<TABLE>\n"):
        assert workbook.kind_of(page) == workbook.KIND_MARKUP, page
    assert workbook.kind_of(b"<tablespoon,x\n") == workbook.KIND_OTHER


# -- item 18: a carriage return survives the writing -------------------


def test_a_carriage_return_in_a_header_is_written_back(tmp_path: pathlib.Path) -> None:
    """Files review, MAJOR 18 (plan P4-D167).

    THE REPRODUCTION. A header `line&#13;name` was read as `line\\rname`
    and written with a literal carriage return, which every reader turns
    into a line feed: the real workbook validated and its twin missed
    `header.presence`, `header.names`, `columns.order` and `position.at`.
    """
    strings = _DECLARATION + (
        f'<sst xmlns="{_MAIN}"><si><t>line&#13;name</t></si><si><t>other</t></si></sst>'
    )
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(_FLOOR):
        grid[2 + place] = [_cell(f"A{2 + place}", f"{place}"), _cell(f"B{2 + place}", f"{place % 4}")]
    data = _book([("Data", _rows(grid))], [])
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        members = [(one, bundle.read(one)) for one in bundle.namelist()]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for name, held in members:
            entry = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            bundle.writestr(entry, strings if name == "xl/sharedStrings.xml" else held)
    result = _trip(tmp_path, "returned", buffer.getvalue())
    _held(result)
    sheet = crosscheck.reader().load_workbook(result["twin"]).worksheets[0]
    assert sheet["A1"].value == "line\rname"


# -- item 19: the oracle refuses what it does not read -----------------


def test_the_oracle_refuses_a_cell_outside_its_number_grammar() -> None:
    """Files review, MAJOR 19 (plan P4-D173).

    THE REPRODUCTION. For a form quoting numbers always and text bare,
    the product wrote `"1,234";A` and the oracle `1,234;A`, because the
    oracle's narrow grammar called `1,234` text instead of refusing it;
    and `1e` went the other way, an empty exponent being accepted. The
    oracle refuses the first now, and neither it nor the product reads
    the second as a number.
    """
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "oracle",
        pathlib.Path(__file__).resolve().parents[1]
        / "tools" / "reference" / "make_generation_reference_vectors.py",
    )
    assert spec is not None and spec.loader is not None
    oracle = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(oracle)
    for cell in ("1,234", "(12)", " 12", "1 234", "12%"):
        with pytest.raises(AssertionError):
            oracle.written_cell_class(cell)
    assert oracle.doc_is_a_plain_number("1e") is False
    assert dialect.cell_class("1e") == dialect.CELL_TEXT
    assert sheetwriting.number_spelling("1e") == ""
    assert oracle.written_cell_class("North") == "text"
    # ...and the absent class is read from contract 5.4.1's whole
    # vocabulary, as the product reads it, not from a sample of it.
    for cell in ("-", "?", "#N/A", "   ", "NaT", "nat", "NA"):
        assert oracle.written_cell_class(cell) == dialect.cell_class(cell), cell
    assert oracle.written_cell_class("12.5") == "number"


# -- merge item 7: FD7 counts every cell the twin writes empty ---------


def test_a_sorted_column_with_declared_missing_values_keeps_its_order(
    tmp_path: pathlib.Path,
) -> None:
    """Files review merge pass, MAJOR 7 (plan P4-D173).

    THE REPRODUCTION. Two hundred sorted free-text values and twenty
    `ZZZ`, declared `--missing-value ZZZ`, beside a column holding
    `North`. The free-text column publishes no spelling of those twenty
    cells, so FD7's count of blank and pooled cells was nought, the
    ascending order was published and loaded, the twin wrote the twenty
    cells empty, and the twin missed `rows.order`.
    """
    values = sorted(
        ["Value" + chr(65 + place // 26) + chr(65 + place % 26) for place in range(200)]
        + ["ZZZ"] * 20
    )
    data = ("x,other\n" + "".join(f"{value},North\n" for value in values)).encode()
    result = _trip(tmp_path, "sorted", data, ("--missing-value", "ZZZ"), suffix=".csv")
    _held(result)
    loaded = contract.load_profile(str(result["described"]))
    column = loaded.columns[0]
    assert column.n_missing == 20 and not column.missing_by_source
    assert result["document"]["source"]["dialect"]["row_order"] is None
    # ...and the loader refuses the description the review measured: the
    # same document with the ascending order put back.
    document = result["document"]
    document["source"]["dialect"]["row_order"] = {
        "collation": "text", "column": 1, "direction": "ascending",
    }
    import fixtures

    edited = fixtures.write_profile(tmp_path, "edited-profile.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(edited))
    assert "FD7" in f"{raised.value}"


# -- the two facts the disclosure rule leaves a twin to write from -----


def test_a_withheld_census_still_keeps_digit_codes_as_text(
    tmp_path: pathlib.Path,
) -> None:
    """The published commonest class decides where the census cannot (P4-D164).

    Sixty text cells of digits and ONE absent cell: the disclosure rule
    withholds the whole census, because any count it published would let
    a reader subtract the absent cell's. Without the class named beside
    it the twin could not tell these texts from numbers, and pandas would
    read integers from the twin and strings from the source.
    """
    # ONE ABSENT CELL BESIDE A FULL FLOOR OF TEXT CELLS (plan
    # P4-D341): the property is that any count the census published
    # would leave the one absent cell to be subtracted, which holds at
    # any length, and the table is written at the floor because the
    # command refuses a smaller one.
    codes = _FLOOR
    strings = ["code", "k"] + [f"{place:05d}" for place in range(1, codes + 1)]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(codes + 1):
        number = 2 + place
        cells = [_cell(f"B{number}", f"{place % 4}")]
        if place != 30:
            cells = [_cell(f"A{number}", f"{2 + place % codes}", "s")] + cells
        grid[number] = cells
    result = _trip(tmp_path, "codes", _book([("Data", _rows(grid))], strings))
    _held(result)
    column = result["document"]["source"]["workbook"]["columns"][0]
    assert set(column["cell_classes"].values()) == {None}, column
    assert column["value_class"] == "text"
    source = crosscheck.read_excel(result["source"], dtype=object)["code"].dropna()
    twin = crosscheck.read_excel(result["twin"], dtype=object)["code"].dropna()
    assert {type(one) for one in twin} == {type(one) for one in source} == {str}


def test_a_mostly_empty_date_column_keeps_its_date_format(
    tmp_path: pathlib.Path,
) -> None:
    """The published code is the commonest among the cells holding a value.

    Thirty dates wearing a date format among seventy absent cells: the
    code was the commonest over EVERY cell, absent ones wearing the
    general format, so the general format was published and the twin's
    dates came back from pandas as numbers (plan P4-D164).
    """
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(100):
        number = 2 + place
        cells = [_cell(f"B{number}", f"{place % 4}")]
        if place % 10 < 3:
            cells = [_cell(f"A{number}", f"{45000 + place}", "", 1)] + cells
        grid[number] = cells
    result = _trip(
        tmp_path, "sparse-dates", _book([("Data", _rows(grid))], ["when", "k"], ("General", "yyyy-mm-dd"))
    )
    _held(result)
    column = result["document"]["source"]["workbook"]["columns"][0]
    # Published as the source wrote it since plan P4-D189.
    assert column["format_code"] == "yyyy-mm-dd", column
    when = crosscheck.read_excel(result["twin"])["when"].dtype
    assert str(when).startswith("datetime64")


# -- the repair pass after the files review (plan P4-D174) -------------
#
# Each test below is a reproduction a second, independent reading of the
# repairs above measured on the repaired tree: a header of one name, a
# table shorter than the line, whitespace cells under the floor, the
# noise a writer leaves in a stored number, the loader's two subtraction
# rules, and a first header cell opening like a tag.


# The records `_one_name_over_text_records` writes under its one-word
# header, counting the first: the population floor, because the command
# describes no smaller table (plan P4-D341). It was forty-one.
_ONE_NAME_RECORDS = _FLOOR


def _one_name_over_text_records(
    pane: str = "", merged: bool = False, records: int = _ONE_NAME_RECORDS
) -> bytes:
    """`subject` in A1 (B1, C1 blank) over records of three texts.

    ``records`` records in all, the first of them the review's own
    `CASE-ZEBRA-471`.
    """
    strings = ["subject", "CASE-ZEBRA-471", "amber", "Northfield"]
    grid = {
        1: [_cell("A1", "0", "s")],
        2: [_cell("A2", "1", "s"), _cell("B2", "2", "s"), _cell("C2", "3", "s")],
    }
    for place in range(records - 1):
        number = 3 + place
        strings += [f"CASE-{1000 + place}", ["red", "blue"][place % 2],
                    ["Eastham", "Westbury", "Southport"][place % 3]]
        top = len(strings)
        grid[number] = [
            _cell(f"A{number}", f"{top - 3}", "s"),
            _cell(f"B{number}", f"{top - 2}", "s"),
            _cell(f"C{number}", f"{top - 1}", "s"),
        ]
    data = _book([("Data", _rows(grid))], strings, pane=pane)
    if not merged:
        return data
    # A banner: the one cell of row 1 merged across the table's columns.
    buffer = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(
        buffer, "w", zipfile.ZIP_DEFLATED
    ) as bundle:
        for entry in source.infolist():
            held = source.read(entry.filename)
            if entry.filename == "xl/worksheets/sheet1.xml":
                held = held.replace(
                    b"</sheetData>",
                    b'</sheetData><mergeCells count="1"><mergeCell ref="A1:C1"/></mergeCells>',
                )
            bundle.writestr(entry, held)
    return buffer.getvalue()


def test_a_header_of_one_name_is_read_as_the_names(tmp_path: pathlib.Path) -> None:
    """A header naming one column is not stepped over as a title (P4-D174, P4-D186).

    THE REPRODUCTION. `subject` in `A1` with `B1` and `C1` blank, over
    forty-one records of three texts, at a floor of five: the header rule
    took the one-cell row for a title, the first record became the names
    -- `CASE-ZEBRA-471`, `amber`, `Northfield`, published whole -- and
    both files validated, while pandas named the source's columns
    `subject`, `Unnamed: 1`, `Unnamed: 2`. P4-D174 stopped and asked;
    since P4-D186 the row is asked what a text file's one-field line is
    asked, and a row of one word is not furniture, so it is the names.

    THE OWNER'S RULING OF 2026-09-17, ITEM 8 (plan P4-D232) does not
    reach this sheet, and that is the limit the plan entry names: the
    header rule takes the one-word row ITSELF as the names, so nothing
    stands above them as furniture and the rule that reads a row under
    furniture as a record is never asked. What the reproduction was
    about is unmoved -- `CASE-ZEBRA-471` is never a column name -- and
    the round trip holds, declared and undeclared alike.
    """
    for flags, where in (
        (("--smallest-group", "5"), "undeclared"),
        (("--smallest-group", "5", "--first-row", "names"), "declared"),
    ):
        result = _trip(
            tmp_path / where, "one-name", _one_name_over_text_records(), flags
        )
        _held(result)
        assert [one["name"] for one in result["document"]["columns"]] == [
            "subject", "Unnamed: 1", "Unnamed: 2",
        ]
    document = result["document"]
    assert [one["name"] for one in document["columns"]] == [
        "subject", "Unnamed: 1", "Unnamed: 2",
    ]
    assert document["n_rows"] == _ONE_NAME_RECORDS
    assert document["source"]["workbook"]["rows_above_header"] == 0
    assert b"ZEBRA" not in result["described"].read_bytes()
    # AND UNDECLARED IT IS UNMOVED TOO, which is the limit plan P4-D232
    # names: the header rule takes the one-word row itself, so nothing
    # is furniture above the names and the row under them is read by
    # convention. `subject` is a name here, not a record.
    table = reading.read_table(
        str(tmp_path / "declared" / "one-name.xlsx")
    )
    assert list(table.column_names) == ["subject", "Unnamed: 1", "Unnamed: 2"]
    assert table.n_rows == _ONE_NAME_RECORDS
    assert table.first_row_seen == ""
    # Last: what a second reader names the twin's columns.
    assert list(crosscheck.read_excel(result["twin"]).columns) == list(
        crosscheck.read_excel(result["source"]).columns
    )


def test_a_title_the_sheet_marks_is_not_asked_about(tmp_path: pathlib.Path) -> None:
    """Frozen panes or a filter on the names settle the header (P4-D174).

    The same rows, with the panes frozen below row 2 or the autofilter
    on row 2, are a title above the names: the run is not stopped, one
    row stands above the header, and the twin -- which carries both --
    is described again without a question. A merged banner is not
    evidence, because a twin merges nothing: the banner's one word is
    read as the names, as the unmerged row is (P4-D186).
    """
    frozen = tmp_path / "frozen"
    pane = ('<sheetViews><sheetView workbookViewId="0"><pane ySplit="2" '
            'topLeftCell="A3" activePane="bottomLeft" state="frozen"/>'
            "</sheetView></sheetViews>")
    result = _trip(frozen, "frozen", _one_name_over_text_records(pane=pane),
                   ("--smallest-group", "5"))
    # THE SHEET'S MARK SETTLES WHICH ROW THE HEADER IS ON, and that is
    # what P4-D174 decided and what this witness holds. It does not
    # settle that the row IS names rather than a record, which is a
    # different question and is the owner's ruling of 2026-09-17, item
    # 8 (plan P4-D232): the row under the title is read as the record it
    # may be and the columns are synthtwin's own.
    _held(result)
    assert result["document"]["source"]["workbook"]["rows_above_header"] == 1
    assert [one["name"] for one in result["document"]["columns"]] != [
        "subject", "Unnamed: 1", "Unnamed: 2",
    ]
    filtered = tmp_path / "filtered"
    # ONE RECORD MORE THAN THE FROZEN SHEET (plan P4-D341). The filter
    # on row 2 marks that row as the NAMES, so the records under it are
    # one fewer than the sheet holds -- and the command describes a
    # table of the population floor or more. The filter covers the
    # names and every record under them: row 2 to the sheet's last row.
    marked = _ONE_NAME_RECORDS + 1
    result = _trip(filtered, "filtered",
                   _one_name_over_text_records(
                       pane=f'<autoFilter ref="A2:C{1 + marked}"/>',
                       records=marked,
                   ),
                   ("--smallest-group", "5"))
    _held(result)
    assert result["document"]["source"]["workbook"]["rows_above_header"] == 1
    banner = tmp_path / "banner.xlsx"
    banner.write_bytes(_one_name_over_text_records(merged=True))
    table = reading.read_table(str(banner))
    # A merged banner is read as the names by the header rule, which
    # leaves nothing above them as furniture, so the rule of P4-D232 is
    # not asked and the banner's word is the first name, as before.
    assert list(table.column_names) == ["subject", "Unnamed: 1", "Unnamed: 2"]


def _short_table(rows: int) -> bytes:
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(rows):
        number = 2 + place
        cells = [_cell(f"B{number}", f"{10 + place * 3}")]
        if place == 1:
            cells = [_cell(f"A{number}", "2", "s")] + cells
        elif place > 1:
            cells = [_cell(f"A{number}", f"{place * 7}")] + cells
        grid[number] = cells
    return _book([("Data", _rows(grid))], ["v", "k", "note"])


@pytest.mark.parametrize("rows, floor", [(8, "11"), (4, "5")])
def test_a_table_shorter_than_the_line_loads_its_own_census(
    tmp_path: pathlib.Path, rows: int, floor: str
) -> None:
    """A census held back whole stands in a table shorter than the line (P4-D174).

    THE REPRODUCTION. Eight rows at a floor of eleven, a column of one
    absent cell, one text and six numbers: the producer withheld every
    count -- nothing else it could do -- and the loader refused that
    census because the eight withheld cells were fewer than the line,
    so `generate` said the description had been changed since it was
    written. What a census with nothing published leaves to subtract
    from is the row count alone, which names nobody.
    """
    # DESCRIBED BY THE PRODUCER (plan P4-D341). The subject here is a
    # table SHORTER than the disclosure line: growing it to the
    # population floor the COMMAND requires is deleting the case. The
    # producer refuses no table for its size, and the loader -- which
    # is what the reproduction was about -- still reads what it writes.
    result = _trip(
        tmp_path,
        "short",
        _short_table(rows),
        ("--smallest-group", floor),
        by_command=False,
    )
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert set(census.values()) == {None}, census
    assert dialect.sheet_census_broken(census, rows, int(floor)) == ""


def test_every_census_the_producer_writes_is_one_the_loader_takes() -> None:
    """The producer's census and the loader's rule agree, exhaustively (P4-D174).

    Every split of up to fifteen cells among three classes, at floors of
    one, two, five and eleven: the census `sheet_census` publishes is one
    `sheet_census_broken` accepts. The rule the loader enforces and the
    rule the producer follows are written beside each other, and a table
    shorter than the line is where they parted.
    """
    every = dialect.SHEET_CELL_CLASSES
    for total in range(0, 16):
        for first in range(0, total + 1):
            for second in range(0, total - first + 1):
                counts = {"number": first, "text": second, "absent": total - first - second}
                for floor in (1, 2, 5, 11):
                    published = dialect.sheet_census(counts, every, total, floor)
                    assert dialect.sheet_census_broken(published, total, floor) == "", (
                        counts, total, floor, published,
                    )


def test_the_loader_refuses_each_subtraction_a_census_could_leave() -> None:
    """Each of WB3's two subtraction rules refuses on its own (P4-D174).

    Neither census publishes a nought, so only the rule named can refuse
    it: one withheld count beside every other class published rebuilds
    that count by subtraction, and two withheld counts that come to five
    at a floor of eleven are a difference under the line.
    """
    one_withheld = {
        "absent": 30, "blank": 30, "boolean": 30, "date": None, "empty": 30,
        "error": 30, "number": 30, "text": 30,
    }
    assert "withholds one count" in dialect.sheet_census_broken(one_withheld, 240, 11)
    under_the_line = {
        "absent": 30, "blank": 30, "boolean": 30, "date": None, "empty": 30,
        "error": None, "number": 85, "text": 30,
    }
    assert "come to 5" in dialect.sheet_census_broken(under_the_line, 240, 11)


def _spaced(cells: int) -> bytes:
    strings = ["v", "k", "North", "South", "   "]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(100):
        number = 2 + place
        label = "4" if place < cells else ("2" if place % 2 else "3")
        grid[number] = [_cell(f"A{number}", label, "s"), _cell(f"B{number}", f"{place % 4}")]
    return _book([("Data", _rows(grid))], strings)


@pytest.mark.parametrize("cells", [1, 3])
def test_a_cell_of_spaces_under_the_floor_is_counted_as_its_twin_writes_it(
    tmp_path: pathlib.Path, cells: int
) -> None:
    """A cell the twin writes empty is counted as a cell holding nothing (P4-D174).

    THE REPRODUCTION. A hundred labels, one or three of them three
    spaces, at a floor of five: the spelling is under the floor and not
    published, so the twin writes those cells empty -- and the census
    counted them as text, published `text 100`, and the twin missed
    `workbook.cell-classes` while the source passed. The census counts
    what the twin writes, on both files alike.
    """
    result = _trip(tmp_path, "spaced", _spaced(cells), ("--smallest-group", "5"))
    _held(result)
    column = result["document"]["columns"][0]
    assert column["missing_by_source"] == {}
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert census["text"] != 100, census


def test_a_judged_sentinel_is_counted_as_its_twin_writes_it(tmp_path: pathlib.Path) -> None:
    """The cells a judged pass reads as missing are counted as the twin writes them.

    Two hundred and forty ages, every twelfth `-999`: the judged pass
    reads the twenty as missing. When the twin wrote them empty the
    census had to count them `absent` -- it counted `number 240` and the
    twin missed `workbook.cell-classes` (plan P4-D174) -- and it did,
    `absent 20` beside `number 220`. Since plan P4-D6.4 (the owner's
    ruling of 2026-09-15) the twin writes them as the sheet held them,
    numbers, so the census counts what it writes again: the twenty move
    from `absent` to `number`, 220 + 20 = 240 and 20 - 20 = 0, and both
    files still hold every obligation.
    """
    rnd = random.Random(5)
    grid = {1: [_cell("A1", "0", "s")]}
    for place in range(240):
        number = 2 + place
        value = "-999" if place % 12 == 0 else f"{rnd.randint(20, 90)}"
        grid[number] = [_cell(f"A{number}", value)]
    result = _trip(tmp_path, "sentinel", _book([("Data", _rows(grid))], ["age"]),
                   ("--smallest-group", "5"))
    _held(result)
    census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
    assert census["absent"] == 0 and census["number"] == 240, census
    assert result["again"]["source"]["workbook"]["columns"][0]["cell_classes"] == census


def test_a_stored_number_is_read_without_its_writers_noise(tmp_path: pathlib.Path) -> None:
    """`73.09999999999999` is the stored 73.1, and is read so (plan P4-D174).

    THE REPRODUCTION. openpyxl stores a weight of 73.1 as
    `73.09999999999999` and Excel as `73.099999999999994`, the same
    binary64 either way. The column machinery read those figures as the
    cell's spelling, published fraction widths of one and fourteen, and
    the person's own unchanged workbook failed `styles.spelled` against
    its own description.
    """
    rnd = random.Random(3)
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(200):
        number = 2 + place
        weight = round(rnd.gauss(72, 12), 1)
        grid[number] = [_cell(f"A{number}", f"{place + 1}"),
                        _cell(f"B{number}", f"{weight:.16g}")]
    result = _trip(tmp_path, "weights", _book([("Data", _rows(grid))], ["id", "weight"]))
    _held(result)
    widths = result["document"]["columns"][1]["fraction_widths"]
    assert sorted(widths) == ["1"], widths
    for noisy, read in (
        ("73.09999999999999", "73.1"), ("73.099999999999994", "73.1"),
        ("6.9000000000000006E-2", "6.9E-2"), ("+73.09999999999999", "+73.1"),
    ):
        assert workbook.stored_number_spelling(noisy) == read
    # A different binary64, a whole number, a text too short to be noise
    # and a fraction padded to a published width -- the twin writes
    # `45353.39257371100` for a width of eleven -- are kept as the file
    # holds them.
    for kept in ("0.30000000000000004", "12345678901234567", "73.10", "1e999",
                 "45353.39257371100"):
        assert workbook.stored_number_spelling(kept) == kept


def test_a_header_opening_like_a_tag_name_is_read(tmp_path: pathlib.Path) -> None:
    """`<body temp` is a header cell, not a web page (plan P4-D174).

    A name ending in a space was enough to call the file markup, so a
    delimited table whose first header was `<body temp` or `<table 2`
    was refused. Markup's name is followed by the tag's end or an
    attribute.
    """
    source = tmp_path / "temps.csv"
    source.write_bytes(b"<body temp,x\n1,2\n3,4\n5,6\n")
    found = reading.read_table(str(source), first_row=reading.FIRST_ROW_NAMES)
    assert found.column_names == ["<body temp", "x"]
    assert workbook.kind_of(b"<table 2,x\n1,2\n") == workbook.KIND_OTHER
    for page in (b'<html lang="en">', b"<table border=1>", b"<body/>",
                 b"<html\n  xmlns:o='x'>", b"<table>\n<tr>"):
        assert workbook.kind_of(page) == workbook.KIND_MARKUP, page

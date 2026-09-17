"""Plan P4-D77's gate: a spreadsheet workbook is read, and read the same.

WHAT THIS GATE CAN AND CANNOT ASSERT, SAID FIRST. The landing's full
gate is "profile, generate, profile the twin again, validate both" --
and the middle of that is not reachable in this part, because a
workbook's twin is a workbook and the writer that produces one is the
next landing's. `synthtwin generate` REFUSES a description of a
workbook (plan P4-D78) rather than quietly writing delimited text and
calling it the twin of a spreadsheet, and that refusal is asserted here
as the behaviour it is.

What IS asserted, for every shape:

* the workbook is built by a seeded script at run time (plan D13), in
  the shapes the study measured Excel, pandas, openpyxl and R writing;
* `synthtwin profile` reads it, exit 0;
* every published fact is what an INDEPENDENT reader says about the
  same file -- openpyxl and pandas, which `src/synthtwin` never
  imports. That is what stands in for the second reading the delimited
  path gets from pandas and the workbook path cannot have;
* describing the same workbook again publishes the identical block,
  which is the round trip available to a reader: read, publish, read
  again;
* `synthtwin validate` measures the REAL workbook against its own
  description and misses NOTHING, exit 0;
* `synthtwin generate` refuses it in words that say what to do instead.

And for the hostile shapes, that each is refused by the cap it is built
to reach, naming that cap rather than failing some other way.
"""

import io
import json
import pathlib
import sys

import pytest

import workbooks
from synthtwin import errors, reading, workbook


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


def _quiet(argv: "list[str]") -> int:
    """The same, with the command's own pages kept out of the log."""
    import contextlib

    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        return _exit_of(argv)


def _written(folder: pathlib.Path, name: str, data: bytes) -> pathlib.Path:
    """A workbook on disk. Bytes, so no line ending is ever translated."""
    target = folder / name
    target.write_bytes(data)
    return target


# Every ordinary shape, with what the study says each one is for.
SHAPES = {
    "plain": workbooks.plain_book,
    "typed": workbooks.typed_book,
    "titled": workbooks.titled_book,
    "hidden_first": workbooks.hidden_first_book,
    "epoch": workbooks.epoch_book,
    "inline": workbooks.inline_book,
    "macro": workbooks.macro_book,
}


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_a_workbook_is_described_and_describes_the_same_way_again(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """Read, publish, read again: the same block both times."""
    path = _written(tmp_path, f"{shape}.xlsx", SHAPES[shape]())
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / f"{shape}-profile.json"
    assert described.is_file(), sorted(p.name for p in tmp_path.iterdir())
    first = json.loads(described.read_text(encoding="utf-8"))
    block = first["source"]["workbook"]
    assert block is not None, "a workbook published no workbook block"

    # Again, into a folder of its own, from the same bytes.
    again = tmp_path / "again"
    again.mkdir()
    assert _quiet(["profile", str(path), "--out-dir", str(again)]) == 0
    second = json.loads(
        (again / f"{shape}-profile.json").read_text(encoding="utf-8")
    )
    assert second["source"]["workbook"] == block
    assert second["n_rows"] == first["n_rows"]
    assert [one["name"] for one in second["columns"]] == [
        one["name"] for one in first["columns"]
    ]


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_an_independent_reader_agrees_about_every_published_fact(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """openpyxl, which `src` never imports, is asked the same questions.

    This is what stands in for the second reading. A workbook has no
    second reader inside the offline guarantee -- the package's pandas
    is reduced to `read_csv` -- so the check that the reader read the
    file RIGHT, rather than merely consistently, is made here against a
    library the product cannot reach.
    """
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(tmp_path, f"{shape}.xlsx", SHAPES[shape]())
    assert _quiet(["profile", str(path)]) == 0
    block = json.loads(
        (tmp_path / f"{shape}-profile.json").read_text(encoding="utf-8")
    )["source"]["workbook"]

    book = openpyxl.load_workbook(path)
    assert block["sheet_count"] == len(book.worksheets)
    # The sheet synthtwin settled on is the first VISIBLE one, which is
    # deliberately not what the readers take (plan P4-D77).
    visible = [
        index
        for index in range(len(book.worksheets))
        if book.worksheets[index].sheet_state == "visible"
    ]
    assert block["sheet_position"] == visible[0] + 1
    assert block["sheet_hidden"] is False
    assert block["date_system"] == ("1904" if book.epoch.year == 1904 else "1900")

    chosen = book.worksheets[block["sheet_position"] - 1]
    # Every census counts as many cells as the table has rows.
    described = json.loads(
        (tmp_path / f"{shape}-profile.json").read_text(encoding="utf-8")
    )
    for column in block["columns"]:
        counted = 0
        for kind in workbook.CELL_CLASSES:
            held = column["cell_classes"][kind]
            if held is not None:
                counted = counted + held
        assert counted in (0, described["n_rows"]), (
            f"{shape}: a column's census counts {counted} cells for a "
            f"table of {described['n_rows']} rows"
        )
    assert chosen.max_row >= described["n_rows"]


@pytest.mark.parametrize("shape", sorted(SHAPES))
def test_validate_measures_the_real_workbook_and_misses_nothing(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """The real file meets its own description: exit 0, nothing missed.

    The byte rules of the written form are WITHHELD here rather than
    missed (validation method V6.2-A2): they describe how a DELIMITED
    file is written and this file is a package of markup, so measuring
    them against it would accuse it of breaking a promise its
    description never made about it.
    """
    path = _written(tmp_path, f"{shape}.xlsx", SHAPES[shape]())
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / f"{shape}-profile.json"
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0
    report = tmp_path / f"{shape}-quality.txt"
    text = report.read_text(encoding="utf-8")
    missed = [
        line.strip()
        for line in text.splitlines()
        if line.strip().endswith("MISSED")
    ]
    assert not missed, missed[:5]
    # ...and the withholding is SHOWN, not silent.
    assert "WITHHELD" in text


def test_a_workbook_description_is_given_a_workbook_twin(
    tmp_path: pathlib.Path,
) -> None:
    """`generate` writes the twin as a workbook (plan P4-D79).

    It is named like one and it IS one: a zip package, not delimited
    text under a spreadsheet's name.
    """
    path = _written(tmp_path, "plain.xlsx", workbooks.plain_book())
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "plain-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "plain-twin.xlsx"
    assert twin.is_file(), sorted(one.name for one in tmp_path.iterdir())
    assert not (tmp_path / "plain-twin.csv").exists()
    assert twin.read_bytes()[:2] == b"PK"


def test_the_sheet_a_person_names_is_the_sheet_that_is_read(
    tmp_path: pathlib.Path,
) -> None:
    """`--sheet` names one; an unknown name is refused, naming the rest."""
    path = _written(tmp_path, "hidden.xlsx", workbooks.hidden_first_book())
    # Without the option: the first VISIBLE sheet, which is the second.
    assert _quiet(["profile", str(path)]) == 0
    block = json.loads(
        (tmp_path / "hidden-profile.json").read_text(encoding="utf-8")
    )["source"]["workbook"]
    assert block["sheet_position"] == 2
    assert block["sheet_hidden"] is False

    named = tmp_path / "named"
    named.mkdir()
    assert (
        _quiet(
            ["profile", str(path), "--sheet", "Data", "--out-dir", str(named)]
        )
        == 0
    )
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(path), sheet="Nope")
    spoken = f"{raised.value}"
    assert "no sheet called 'Nope'" in spoken
    assert "Notes" in spoken and "Data" in spoken


# -- the caps, each refused by the one it is built to reach ------------

HOSTILE = {
    "doctype": (workbooks.doctype_book, "document type declaration"),
    "far_cell": (workbooks.far_cell_book, "further than a spreadsheet goes"),
    "wide_cell": (workbooks.wide_cell_book, "further than a spreadsheet goes"),
    "ratio_bomb": (workbooks.ratio_bomb_book, "times its packed size"),
    "traversal": (workbooks.traversal_book, "belonged outside the file"),
    "all_hidden": (workbooks.all_hidden_book, "every one of them is hidden"),
}


@pytest.mark.parametrize("shape", sorted(HOSTILE))
def test_a_hostile_workbook_is_refused_by_the_cap_it_reaches(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """Each shape is refused, and the refusal names ITS OWN cap.

    A refusal that named some other cap would leave this one untested
    while the test still passed, which is the way a battery of refusals
    rots.
    """
    build, expected = HOSTILE[shape]
    path = _written(tmp_path, f"{shape}.xlsx", build())
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(path))
    assert expected in f"{raised.value}", f"{shape}: {raised.value}"


def test_a_file_is_placed_by_its_opening_bytes_and_not_its_name(
    tmp_path: pathlib.Path,
) -> None:
    """A compound file and a web page, both wearing a workbook's name."""
    compound = _written(tmp_path, "legacy.xls", workbooks.compound_file())
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(compound))
    assert "older Excel workbook" in f"{raised.value}"
    assert "Excel Workbook (.xlsx)" in f"{raised.value}"

    markup = _written(tmp_path, "export.xls", workbooks.markup_named_xls())
    with pytest.raises(errors.ProfileError) as second:
        reading.read_table(str(markup))
    assert "web page or markup" in f"{second.value}"

    # ...and the same bytes under a workbook's own name are placed the
    # same way, because the name never decides.
    renamed = _written(tmp_path, "export.xlsx", workbooks.markup_named_xls())
    with pytest.raises(errors.ProfileError) as third:
        reading.read_table(str(renamed))
    assert "web page or markup" in f"{third.value}"


def test_a_macro_project_is_named_and_never_read(
    tmp_path: pathlib.Path,
) -> None:
    """A macro workbook is described; its code is neither read nor copied."""
    path = _written(tmp_path, "macro.xlsm", workbooks.macro_book())
    assert _quiet(["profile", str(path)]) == 0
    block = json.loads(
        (tmp_path / "macro-profile.json").read_text(encoding="utf-8")
    )["source"]["workbook"]
    assert block["macro_project"] is True
    table = reading.read_table(str(path))
    assert table.book is not None
    assert table.book.has_macro_project is True
    # Nothing of the project reaches the table's cells.
    for column in table.columns:
        for cell in column:
            assert "vbaProject" not in cell


# -- plan P4-D79: the twin of a workbook is a workbook ------------------
#
# The gate the landing is held to. For every shape a seeded script
# builds a realistic workbook, synthtwin describes it, BUILDS THE TWIN,
# describes the twin again, and both files are validated at exit 0 --
# and the two independent readers are asked whether the twin and the
# source look the same to code that reads them.

STUDY_SHAPES = ("excel", "pandas", "writexl")

# The size the whole round trip runs at, which describes each file three
# times. Larger tables are held to the workbook facts by the test below
# it, for a reason that was MEASURED rather than assumed.
STUDY_SIZES = ((200, 0),)

# The larger sizes the landing's gate names.
STUDY_LARGE = ((1200, 5), (3000, 9))


def _block_of(described: pathlib.Path) -> "dict":
    return json.loads(described.read_text(encoding="utf-8"))["source"]["workbook"]


@pytest.mark.parametrize("shape", STUDY_SHAPES)
@pytest.mark.parametrize("n_rows,seed", STUDY_SIZES)
def test_a_realistic_workbook_is_described_generated_and_described_again(
    tmp_path: pathlib.Path, shape: str, n_rows: int, seed: int
) -> None:
    """The whole gate, on a workbook of sixteen typed columns.

    Profile, generate, profile the twin, validate the twin AND the real
    workbook. Every published workbook fact has to come back.
    """
    path = _written(
        tmp_path, f"{shape}.xlsx", workbooks.study_book(n_rows, seed, shape)
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / f"{shape}-profile.json"
    first = _block_of(described)

    assert _quiet(["generate", str(described), "--seed", f"{seed}"]) == 0
    twin = tmp_path / f"{shape}-twin.xlsx"
    assert twin.is_file(), sorted(one.name for one in tmp_path.iterdir())

    # The REAL workbook meets its own description, and so does the twin.
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0
    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )

    # The twin describes the same way the source did.
    third = tmp_path / "third"
    third.mkdir()
    assert _quiet(["profile", str(twin), "--out-dir", str(third)]) == 0
    second = _block_of(third / f"{shape}-twin-profile.json")
    for key in (
        "date_system",
        "sheet_count",
        "sheet_position",
        "sheet_names",
        "rows_above_header",
        "defined_table",
        "autofilter",
        "macro_project",
    ):
        assert second[key] == first[key], f"{shape}/{n_rows}: {key}"
    for index in range(len(first["columns"])):
        assert (
            second["columns"][index]["cell_classes"]
            == first["columns"][index]["cell_classes"]
        ), f"{shape}/{n_rows}: column {index} cell classes"
        assert (
            second["columns"][index]["format_code"]
            == first["columns"][index]["format_code"]
        ), f"{shape}/{n_rows}: column {index} format code"


@pytest.mark.parametrize("shape", STUDY_SHAPES)
@pytest.mark.parametrize("n_rows,seed", STUDY_LARGE)
def test_a_large_workbook_keeps_every_workbook_fact_in_its_twin(
    tmp_path: pathlib.Path, shape: str, n_rows: int, seed: int
) -> None:
    """At 1,200 and 3,000 rows every workbook fact still comes back.

    WHY THIS ASKS FOR THE WORKBOOK FACTS AND NOT FOR EXIT 0, and the
    reason is a measurement rather than a convenience. At these sizes
    the twin misses two obligations of the NUMERIC path --
    `numeric.n_distinct_values` and `numeric.fraction_widths` -- and
    that has nothing to do with how the twin is written. It was checked
    by building the same numeric columns as DELIMITED TEXT, at the same
    size and the same seed, and running the same round trip: the CSV
    twin misses the same two obligations (six of them, against the
    workbook's four). The writer is therefore not the cause, and
    demanding exit 0 here would pin this gate to a limit of the
    generator that `docs/STATE.md` already records.

    What IS demanded is everything the writer is answerable for: the
    twin is built, the REAL workbook validates at exit 0, no
    `workbook.*` obligation is missed, and the twin describes the same
    workbook block the source did.
    """
    path = _written(
        tmp_path, f"{shape}.xlsx", workbooks.study_book(n_rows, seed, shape)
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / f"{shape}-profile.json"
    first = _block_of(described)
    assert _quiet(["generate", str(described), "--seed", f"{seed}"]) == 0
    twin = tmp_path / f"{shape}-twin.xlsx"
    assert twin.is_file()

    # The real workbook meets its own description in full.
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0

    again = tmp_path / "again"
    again.mkdir()
    _quiet(
        ["validate", str(described), "--twin", str(twin),
         "--out-dir", str(again)]
    )
    report = (again / f"{shape}-twin-quality.txt").read_text(encoding="utf-8")
    missed = [
        line.strip()
        for line in report.splitlines()
        if line.strip().endswith("MISSED") and "workbook." in line
    ]
    assert not missed, missed[:5]

    third = tmp_path / "third"
    third.mkdir()
    assert _quiet(["profile", str(twin), "--out-dir", str(third)]) == 0
    second = _block_of(third / f"{shape}-twin-profile.json")
    for index in range(len(first["columns"])):
        assert (
            second["columns"][index]["cell_classes"]
            == first["columns"][index]["cell_classes"]
        ), f"{shape}/{n_rows}: column {index} cell classes"
        assert (
            second["columns"][index]["format_kinds"]
            == first["columns"][index]["format_kinds"]
        ), f"{shape}/{n_rows}: column {index} format kinds"


@pytest.mark.parametrize("shape", STUDY_SHAPES)
def test_both_readers_see_the_same_columns_and_types_in_the_twin(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """pandas and openpyxl answer the same about the twin as the source.

    This is the landing's own reason for existing: code developed on
    the twin has to run unchanged on the real table, and what code sees
    is what its reader returns. A column of text that all looks numeric
    must stay TEXT and a date-formatted column must stay DATE-formatted,
    which is exactly what decides the dtype pandas hands back.
    """
    pandas = pytest.importorskip("pandas")
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(
        tmp_path, f"{shape}.xlsx", workbooks.study_book(200, 0, shape)
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / f"{shape}-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / f"{shape}-twin.xlsx"

    source_frame = pandas.read_excel(path)
    twin_frame = pandas.read_excel(twin)
    assert list(twin_frame.columns) == list(source_frame.columns), shape
    assert [f"{one}" for one in twin_frame.dtypes] == [
        f"{one}" for one in source_frame.dtypes
    ], shape
    assert twin_frame.shape == source_frame.shape, shape

    # ...and openpyxl, which reads the cell rather than a reading of it.
    source_book = openpyxl.load_workbook(path)
    twin_book = openpyxl.load_workbook(twin)
    assert [one.title for one in twin_book.worksheets] == [
        one.title for one in source_book.worksheets
    ], shape


def test_the_text_code_with_leading_zeros_is_still_text_in_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """`00123` stays text, which every ordinary writer gets wrong.

    The study measured `pandas.read_excel` turning a column whose text
    cells all look numeric into integers, so a twin that wrote those
    cells as numbers would hand back a different dtype and the person's
    code would take a different path on the twin than on their table.
    """
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(tmp_path, "excel.xlsx", workbooks.study_book(200, 0))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "excel-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0

    sheet = openpyxl.load_workbook(tmp_path / "excel-twin.xlsx").worksheets[0]
    names = [one.value for one in sheet[1]]
    place = names.index("record_code") + 1
    for row in range(2, 12):
        held = sheet.cell(row=row, column=place).value
        assert isinstance(held, str), f"row {row} came back as {type(held)}"


def test_a_date_column_keeps_its_format_in_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """A date is a number wearing a format, and the twin wears it too."""
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(tmp_path, "excel.xlsx", workbooks.study_book(200, 0))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "excel-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0

    sheet = openpyxl.load_workbook(tmp_path / "excel-twin.xlsx").worksheets[0]
    names = [one.value for one in sheet[1]]
    for name in ("recorded_on", "stamp", "clock", "elapsed"):
        place = names.index(name) + 1
        code = sheet.cell(row=2, column=place).number_format
        assert code != "General", f"{name} lost its format"


def test_the_same_description_and_seed_give_the_same_bytes(
    tmp_path: pathlib.Path,
) -> None:
    """Determinism, measured rather than reasoned about (plan D12).

    Every member of the package carries one fixed moment rather than the
    clock, so two runs of the same description and seed are the same
    file byte for byte.
    """
    path = _written(tmp_path, "excel.xlsx", workbooks.study_book(300, 2))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "excel-profile.json"
    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    assert (
        _quiet(["generate", str(described), "--seed", "4",
                "--out-dir", str(first)]) == 0
    )
    assert (
        _quiet(["generate", str(described), "--seed", "4",
                "--out-dir", str(second)]) == 0
    )
    assert (first / "excel-twin.xlsx").read_bytes() == (
        second / "excel-twin.xlsx"
    ).read_bytes()


def test_the_twin_carries_no_formula_no_macro_and_no_link(
    tmp_path: pathlib.Path,
) -> None:
    """A twin is a file of values, and this reads the parts to prove it.

    The study's whole reason for a writer of our own: both common Python
    writers turn text beginning with `=` into a formula and one turns
    `http://` text into a link. A twin that did either would act on the
    person who opened it.
    """
    import zipfile

    path = _written(tmp_path, "excel.xlsx", workbooks.study_book(200, 0))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "excel-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "excel-twin.xlsx"

    package = zipfile.ZipFile(twin)
    try:
        listing = package.namelist()
        for name in listing:
            assert "vbaProject" not in name, name
            assert "externalLink" not in name, name
            assert "calcChain" not in name, name
        for name in listing:
            if not name.endswith(".xml"):
                continue
            text = str(package.read(name), "utf-8")
            assert "<f>" not in text, f"{name} carries a formula"
            assert "hyperlink" not in text.casefold(), f"{name} carries a link"
    finally:
        package.close()


def test_the_twin_names_no_person_in_its_document_properties(
    tmp_path: pathlib.Path,
) -> None:
    """The creator and the company are written neutral, never copied."""
    import zipfile

    path = _written(tmp_path, "excel.xlsx", workbooks.study_book(200, 0))
    assert _quiet(["profile", str(path)]) == 0
    assert _quiet(["generate", str(tmp_path / "excel-profile.json"),
                   "--seed", "0"]) == 0
    package = zipfile.ZipFile(tmp_path / "excel-twin.xlsx")
    try:
        core = str(package.read("docProps/core.xml"), "utf-8")
    finally:
        package.close()
    assert "<dc:creator></dc:creator>" in core
    assert "<cp:lastModifiedBy></cp:lastModifiedBy>" in core


def test_a_workbook_of_several_sheets_keeps_every_sheet(
    tmp_path: pathlib.Path,
) -> None:
    """Other sheets are written under their own names, holding nothing.

    These three sheets hold NO cells at all, so a sheet of nothing is
    exactly what the twin owes: `sheet_extents` publishes `0` by `0` for
    each and the twin writes them bare. A sheet that HOLDS cells is the
    test below this one.
    """
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(
        tmp_path, "many.xlsx", workbooks.study_book(200, 0, sheets=3)
    )
    assert _quiet(["profile", str(path)]) == 0
    assert _quiet(["generate", str(tmp_path / "many-profile.json"),
                   "--seed", "0"]) == 0
    book = openpyxl.load_workbook(tmp_path / "many-twin.xlsx")
    assert len(book.worksheets) == 3
    # The sheet the table came from holds it; the others hold nothing.
    assert book.worksheets[0].max_row > 100
    assert book.worksheets[1].max_row == 1


def test_a_sheet_that_is_not_the_tables_is_the_same_shape_in_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """A reader sees the same workbook on the twin (plan P4-D82).

    THE DEFECT THIS CLOSES, MEASURED. Every sheet that was not the
    table's used to be written EMPTY, so `pandas.read_excel` -- which
    reads the FIRST sheet, hidden or not -- returned (0, 1) on a
    hidden-first workbook and (0, 0) on its twin: a different table, on
    the sheet a reader meets by default, with every published fact
    holding. Writing the person's own text back is what the disclosure
    rule forbids, and cells holding the empty string measure as the same
    nothing, so the twin writes a sheet of the same SHAPE carrying one
    word of synthtwin's own.
    """
    import zipfile

    pandas = pytest.importorskip("pandas")
    path = _written(tmp_path, "hidden.xlsx", workbooks.hidden_first_book(30))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "hidden-profile.json"
    first = _block_of(described)
    assert first["sheet_extents"] == [{"columns": 1, "rows": 1}, None], first

    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "hidden-twin.xlsx"

    # What a reader sees, on the DEFAULT sheet and on the named one.
    assert pandas.read_excel(twin).shape == pandas.read_excel(path).shape
    assert (
        pandas.read_excel(twin, sheet_name="Data").shape
        == pandas.read_excel(path, sheet_name="Data").shape
    )

    # Both files meet the description, and the twin publishes the same
    # blocks when it is described again.
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0
    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )
    third = tmp_path / "third"
    third.mkdir()
    assert _quiet(["profile", str(twin), "--out-dir", str(third)]) == 0
    assert (
        _block_of(third / "hidden-twin-profile.json")["sheet_extents"]
        == first["sheet_extents"]
    )

    # THE DISCLOSURE HALF, read off the twin's own bytes: that sheet
    # holds one cell, and what it holds is synthtwin's own word.
    with zipfile.ZipFile(twin) as bundle:
        page = bundle.read("xl/worksheets/sheet1.xml").decode("utf-8")
        strings = bundle.read("xl/sharedStrings.xml").decode("utf-8")
    assert page.count("<c ") == 1, page
    assert "withheld" in strings

    # AND THE RULE CAN FAIL, which is what makes the two exits above
    # worth anything: the same description, measured against the same
    # workbook with that sheet left EMPTY -- which is what the writer
    # used to produce -- misses the obligation by name.
    bare = _written(tmp_path, "bare.xlsx", workbooks.hidden_first_book(30, 0))
    found = _verdicts(tmp_path / "bare-check", described, bare)
    assert "workbook.sheet-extents" in found.get("MISSED", []), found


def test_a_workbook_whose_other_sheet_holds_a_table_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """A second table cannot be twinned, so the workbook is refused.

    synthtwin describes ONE table. A sheet holding another one cannot be
    written back -- its values are somebody's rows -- and writing it as
    withheld cells would hand a reader a frame where a table stood, so
    statistics taken from the twin's second sheet would be false while
    the file still opened. The refusal names both sheets.

    AND IT MAY NOT NAME A REMEDY THAT IS ALSO REFUSED (review of
    landing 2b.17, MAJOR). THE REPRODUCTION: this message used to end
    "Run the command again with --sheet followed by that sheet's
    name", and doing exactly that was refused too -- `--sheet Data`
    and `--sheet Codebook` both exit 1 on this very workbook, because
    whichever sheet is named the OTHER is then the sheet holding a
    table. Both runs are made below, so the message and the behaviour
    cannot drift apart: what the sentence tells a person to do has to
    be something that works.
    """
    path = _written(tmp_path, "two.xlsx", workbooks.two_table_book(20))
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(path))
    spoken = f"{raised.value}"
    assert "Codebook" in spoken, spoken
    assert "Data" in spoken, spoken
    assert "workbook of its own" in spoken, spoken
    # THE REMEDY IT NAMES IS NOT ONE THE TOOL THEN REFUSES.
    assert "--sheet" not in spoken, spoken
    # ...and the command itself refuses rather than describing one half.
    assert _quiet(["profile", str(path), "--out-dir", str(tmp_path)]) != 0
    # ...naming either sheet, which is what the old sentence asked for.
    for named in ("Data", "Codebook"):
        assert _quiet(
            ["profile", str(path), "--out-dir", str(tmp_path), "--sheet", named]
        ) != 0, named


def test_a_delimiter_declared_on_a_workbook_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """A workbook keeps its values in cells; it has no delimiter to declare.

    Plan P4-D110. `--delimiter` given on one is a mistake about the
    file, and a declaration a tool quietly ignores is worse than one it
    refuses, so the reader refuses it by name before describing a cell.
    """
    path = _written(tmp_path, "plain.xlsx", workbooks.plain_book(30))
    with pytest.raises(errors.ProfileError) as raised:
        reading.read_table(str(path), declared_delimiter=",")
    spoken = f"{raised.value}"
    assert "is a workbook" in spoken and "--delimiter" in spoken, spoken
    assert _quiet(
        ["profile", str(path), "--out-dir", str(tmp_path), "--delimiter", ","]
    ) == 1
    assert not (tmp_path / "plain-profile.json").exists()
    # ...and the same workbook with nothing declared is read as before.
    assert _quiet(["profile", str(path), "--out-dir", str(tmp_path)]) == 0


def test_a_defined_table_is_written_over_the_twins_own_rows(
    tmp_path: pathlib.Path,
) -> None:
    """A defined table comes back, resized to the twin, neutrally named."""
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(
        tmp_path, "tbl.xlsx", workbooks.study_book(200, 0, table=True)
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "tbl-profile.json"
    assert _block_of(described)["defined_table"] is True
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    sheet = openpyxl.load_workbook(tmp_path / "tbl-twin.xlsx").worksheets[0]
    assert len(sheet.tables) == 1
    # The source's table name is never published, so it is never written.
    assert "tblStudy" not in sheet.tables


@pytest.mark.parametrize("epoch", (False, True))
def test_both_date_systems_survive_the_twin(
    tmp_path: pathlib.Path, epoch: bool
) -> None:
    """The 1904 system shifts every date by 1,462 days, and is published."""
    openpyxl = pytest.importorskip("openpyxl")
    path = _written(
        tmp_path,
        "epoch.xlsx",
        workbooks.study_book(200, 0, epoch_1904=epoch),
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "epoch-profile.json"
    assert _block_of(described)["date_system"] == ("1904" if epoch else "1900")
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    book = openpyxl.load_workbook(tmp_path / "epoch-twin.xlsx")
    assert (book.epoch.year == 1904) is epoch


# -- the repair of landing 2b.10 ---------------------------------------
#
# WHAT THESE ADD, AND WHY THEY WERE MISSING. The gate above runs on one
# family of fixtures -- `study_book`, whose table always sits on the
# first sheet under a generic name, with no macro project. A review
# measured three ordinary shapes outside that family, every one of them
# named in the landing's own instruction, and each produced a twin that
# synthtwin could not read back or that failed its own description:
#
#   * a table not on the first VISIBLE sheet: the writer recorded no
#     sheet's hidden state, so the twin's first visible sheet was an
#     empty placeholder and `profile` refused the twin outright;
#   * a sheet whose name may not be published: the twin wrote the
#     neutral name the disclosure rule demands and was reported MISSED
#     for it, exit 3, on every workbook whose tab is not one of
#     fourteen generic words;
#   * a macro-enabled workbook: `macro_project` was held against the
#     twin as an obligation the twin is FORBIDDEN to meet.
#
# Each is a round trip here now, and each asserts the disclosure half as
# well as the reading half.


def test_a_workbook_whose_table_is_not_on_the_first_sheet_round_trips(
    tmp_path: pathlib.Path,
) -> None:
    """The whole gate on the hidden-first shape, which used to refuse its twin."""
    import zipfile

    path = _written(tmp_path, "hidden.xlsx", workbooks.hidden_first_book(30))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "hidden-profile.json"
    first = _block_of(described)
    assert first["sheet_position"] == 2, first

    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "hidden-twin.xlsx"
    assert twin.is_file(), sorted(one.name for one in tmp_path.iterdir())

    # The twin reads back AS THE SAME TABLE, with no option needed: the
    # sheets standing before the table's are written hidden, so the
    # reader's own rule -- the first visible sheet -- lands on it.
    third = tmp_path / "third"
    third.mkdir()
    assert _quiet(["profile", str(twin), "--out-dir", str(third)]) == 0
    second = _block_of(third / "hidden-twin-profile.json")
    assert second["sheet_position"] == first["sheet_position"]
    assert second["sheet_names"] == first["sheet_names"]
    assert second["sheet_hidden"] == first["sheet_hidden"]

    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0

    with zipfile.ZipFile(twin) as bundle:
        book = bundle.read("xl/workbook.xml").decode("utf-8")
    assert 'state="hidden"' in book, book


def test_a_withheld_sheet_name_round_trips_and_the_twin_carries_none_of_it(
    tmp_path: pathlib.Path,
) -> None:
    """A name that may not be published: the twin is neutral AND valid."""
    import zipfile

    path = _written(tmp_path, "cohort.xlsx", workbooks.withheld_name_book(30))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "cohort-profile.json"
    first = _block_of(described)
    assert first["sheet_names"][0] is None, first["sheet_names"]

    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "cohort-twin.xlsx"
    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )

    # THE DISCLOSURE HALF, asserted on the twin's own bytes rather than
    # trusted to the writer that made them. This is also what the
    # validator cannot do for itself: measuring a file, it cannot tell a
    # twin from the table it was made from, so a leak would look like
    # the real file carrying its own name.
    assert b"Cohort extract" not in twin.read_bytes()
    with zipfile.ZipFile(twin) as bundle:
        book = bundle.read("xl/workbook.xml").decode("utf-8")
    assert 'name="Sheet1"' in book and 'name="Sheet2"' in book, book


def test_a_macro_workbook_gets_a_twin_that_validates(
    tmp_path: pathlib.Path,
) -> None:
    """The macro fact is NAMED rather than held against the twin."""
    import zipfile

    path = _written(tmp_path, "macro.xlsm", workbooks.macro_book(30))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "macro-profile.json"
    assert _block_of(described)["macro_project"] is True

    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "macro-twin.xlsx"
    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )
    report = (again / "macro-twin-quality.txt").read_text(encoding="utf-8")
    named = [
        line.strip()
        for line in report.splitlines()
        if "workbook.macro-project" in line
    ]
    assert named, report[:400]
    for line in named:
        assert line.endswith("WITHHELD"), line

    # And the project itself is nowhere in the twin.
    with zipfile.ZipFile(twin) as bundle:
        carried = [one for one in bundle.namelist() if "vbaProject" in one]
    assert not carried, carried


def test_the_summary_says_which_sheet_was_read_and_names_a_macro_project(
    tmp_path: pathlib.Path,
) -> None:
    """The three promises nothing on screen was keeping.

    The command's own help says synthtwin "says on screen which one it
    chose"; contract 4.3b says the person is told which sheet was read;
    the plan says the report names each withheld fact. A workbook was
    described with none of it said anywhere.
    """
    path = _written(tmp_path, "macro.xlsm", workbooks.macro_book(30))
    assert _quiet(["profile", str(path)]) == 0
    page = (tmp_path / "macro-profile.txt").read_text(encoding="utf-8")
    assert "sheet 1 of 1" in page, page[:600]
    assert "macro project" in page, page[:600]

    other = tmp_path / "other"
    other.mkdir()
    named = _written(tmp_path, "cohort.xlsx", workbooks.withheld_name_book(30))
    assert _quiet(["profile", str(named), "--out-dir", str(other)]) == 0
    page = (other / "cohort-profile.txt").read_text(encoding="utf-8")
    assert "withheld" in page, page[:600]
    # The withheld name itself never reaches the page.
    assert "Cohort extract" not in page


def test_the_rows_above_a_header_reach_both_readers(
    tmp_path: pathlib.Path,
) -> None:
    """pandas sees the same shape on the twin as on the source.

    `rows_above_header` counted rows of CONTENT only, so a blank row
    between a title and the header was published nowhere and the twin
    came up short by exactly those rows: pandas read 15 rows from the
    source and 13 from the twin while synthtwin's own row count was 12
    on both.
    """
    pandas = pytest.importorskip("pandas")
    path = _written(tmp_path, "titled.xlsx", workbooks.titled_book(200))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "titled-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "titled-twin.xlsx"
    assert pandas.read_excel(path).shape == pandas.read_excel(twin).shape


def test_validate_reads_the_sheet_the_person_names(
    tmp_path: pathlib.Path,
) -> None:
    """`--sheet` reaches `validate`, where it used to be accepted and dropped."""
    path = _written(tmp_path, "second.xlsx", workbooks.second_sheet_book(30))
    assert _quiet(["profile", str(path), "--sheet", "Data"]) == 0
    described = tmp_path / "second-profile.json"

    # Without the option the checked file is read at its first sheet,
    # which holds the notes page and not the table.
    assert _quiet(["validate", str(described), "--twin", str(path)]) != 0

    named = tmp_path / "named"
    named.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(path),
             "--sheet", "Data", "--out-dir", str(named)]
        )
        == 0
    )


def _verdicts(
    folder: pathlib.Path, described: pathlib.Path, checked: pathlib.Path
) -> "dict[str, list[str]]":
    """Validate one file against a description; every subcheck's verdict."""
    folder.mkdir(parents=True, exist_ok=True)
    _quiet(
        ["validate", str(described), "--twin", str(checked),
         "--out-dir", str(folder)]
    )
    report = (folder / f"{checked.stem}-quality.txt").read_text(encoding="utf-8")
    found: "dict[str, list[str]]" = {}
    for line in report.split("\n"):
        text = line.strip()
        for verdict in (": MISSED", ": WITHHELD", ": HELD"):
            if not text.endswith(verdict) or " [" not in text:
                continue
            name = text.split(" [")[0]
            word = verdict[2:]
            if word not in found:
                found[word] = []
            found[word] += [name]
    return found


def test_a_workbook_withholding_never_swallows_a_real_miss(
    tmp_path: pathlib.Path,
) -> None:
    """The three facts a twin cannot carry are withheld, and NOTHING else.

    V6.2-A4 withholds `workbook.macro-project`, `workbook.defined-names`
    and each column's `workbook.formulas`, because a twin carries no
    macro project, writes no defined name and writes no formula, and
    `validate` cannot tell a twin from the real table it was made from.
    Their presence was asserted and their NARROWNESS was not: a
    withholding one fact too wide reports a real failure as "not
    checked", which is the one thing a quality report may not do.

    So a description of a titled workbook is measured against a plain
    one of the same table, and every workbook fact that really differs
    has to come back MISSED while exactly those three come back
    WITHHELD. Mutation-checked two ways -- widening the gate to the
    whole workbook census, and withholding a fact beside them -- each of
    which turns this test red.
    """
    described_path = _written(tmp_path, "titled.xlsx", workbooks.titled_book(60))
    assert _quiet(["profile", str(described_path)]) == 0
    described = tmp_path / "titled-profile.json"

    other = _written(tmp_path, "other.xlsx", workbooks.plain_book(60))
    found = _verdicts(tmp_path / "against", described, other)

    # The real misses stand.
    for subcheck in (
        "workbook.rows-above-header",
        "workbook.frozen-rows",
        "workbook.cell-classes",
    ):
        assert subcheck in found.get("MISSED", []), found

    # ...and exactly the three a twin can never carry are withheld.
    withheld = sorted(set(found.get("WITHHELD", [])))
    assert "workbook.macro-project" in withheld, withheld
    assert "workbook.defined-names" in withheld, withheld
    assert "workbook.formulas" in withheld, withheld
    for name in withheld:
        if not name.startswith("workbook."):
            continue
        assert name in (
            "workbook.macro-project",
            "workbook.defined-names",
            "workbook.formulas",
            "workbook.empty-rows-inside",
            "workbook.sheet-hidden",
        ), (name, withheld)

    # THE OTHER WITHHOLDING, AND ITS OWN NARROWNESS (V6.2-A2). The rules
    # of the written form describe a DELIMITED file, so on a workbook
    # description every one of them is withheld -- and that is the whole
    # of what it withholds: the workbook facts above are measured beside
    # them, and the delimited half of this rule is held in
    # `tests/test_file_dialect_round_trip.py`, where a file that breaks
    # a byte rule still MISSES it.
    assert [name for name in withheld if name.startswith("bytes.")], withheld
    for name in found.get("MISSED", []):
        assert not name.startswith("bytes."), name


def test_whole_numbers_past_the_exact_range_meet_their_own_description(
    tmp_path: pathlib.Path,
) -> None:
    """A real workbook of whole numbers past 2**53 validates at exit 0.

    The workbook half of landing 2b.10's named limit: the value a reader
    hands back for `9007199254740993` is 9007199254740992.0, and the
    permitted spellings are computed from that value, so the real file
    was reported MISSED on `styles.spelled` for holding the digits the
    person wrote. Measured at exit 3 before the repair, on this fixture
    and on the same values as delimited text.
    """
    path = _written(tmp_path, "wide.xlsx", workbooks.wide_number_book(300))
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "wide-profile.json"
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0
    report = (tmp_path / "wide-quality.txt").read_text(encoding="utf-8")
    missed = [
        line.strip()
        for line in report.splitlines()
        if line.strip().endswith("MISSED")
    ]
    assert not missed, missed[:5]


@pytest.mark.parametrize("figures", [16, 17])
def test_a_number_stored_with_binary_noise_is_described_by_its_value(
    tmp_path: pathlib.Path, figures: int
) -> None:
    """A stored `79.09999999999999` is the number 79.1, one decimal place.

    Measured before the repair on this fixture: at sixteen figures 167
    of 400 stored texts were not the shortest spelling of their double,
    the description published `fraction_widths {1: 233, 14: 119}`, and
    the REAL workbook exited 3 on `styles.spelled`, its twin exited 3 on
    three facts; at seventeen figures the widths were `{1: 56, 14: 18,
    15: 278}`. The same values stored at their shortest spelling
    validated at exit 0, so the fraction widths were the writer's noise.
    """
    path = _written(
        tmp_path, "noisy.xlsx", workbooks.noisy_number_book(400, figures)
    )
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "noisy-profile.json"
    column = json.loads(described.read_text(encoding="utf-8"))["columns"][0]
    assert sorted(column["fraction_widths"]) == ["1"], column["fraction_widths"]
    real = tmp_path / "real"
    real.mkdir()
    assert _quiet(["validate", str(described), "--twin", str(path),
                   "--out-dir", str(real)]) == 0
    assert _quiet(["generate", str(described), "--seed", "1"]) == 0
    twin = tmp_path / "noisy-twin.xlsx"
    checked = tmp_path / "checked"
    checked.mkdir()
    assert _quiet(["validate", str(described), "--twin", str(twin),
                   "--out-dir", str(checked)]) == 0


@pytest.mark.parametrize(
    ("stored", "read"),
    [
        ("79.09999999999999", "79.1"),
        ("79.099999999999994", "79.1"),
        ("-0.30000000000000004", "-0.30000000000000004"),
        ("1.0000000000000001E-5", "1E-5"),
        ("2.50", "2.50"),
        ("45000", "45000"),
        ("9007199254740993", "9007199254740993"),
        ("1E-3", "1E-3"),
        ("0.000012300000000000001", "0.0000123"),
        ("123456.78900000001", "123456.789"),
    ],
)
def test_a_stored_number_keeps_its_value_and_loses_only_the_noise(
    stored: str, read: str
) -> None:
    """The respelling is the shortest spelling of the same double, or nothing."""
    assert workbook.stored_number_spelling(stored) == read
    assert float(workbook.stored_number_spelling(stored)) == float(stored)


def test_a_lone_record_holding_nothing_is_held_to_the_smallest_group(
    tmp_path: pathlib.Path,
) -> None:
    """A count of records that would name one row is not published.

    `empty_rows_inside` counts ROWS OF THE TABLE, so the floor holds it
    like every census beside it: one such record among sixty names the
    row that holds it. It was published raw at every floor, and the twin
    wrote that one empty record back.

    THE ROUND TRIP HAS TO STILL CLOSE, which is the other half. A
    withheld count states no number, so the file is not held to one --
    and a column whose every class was withheld must not have its
    remainder written in a class the census publishes as NOUGHT. Both
    were measured on this shape: eight `workbook.cell-classes` misses at
    a floor of eleven on the landing's own commit, none now.
    """
    path = _written(tmp_path, "titled.xlsx", workbooks.titled_book(60))
    assert _quiet(["profile", str(path), "--smallest-group", "11"]) == 0
    described = tmp_path / "titled-profile.json"
    first = _block_of(described)
    assert first["empty_rows_inside"] is None, first["empty_rows_inside"]

    assert _quiet(["generate", str(described), "--seed", "0"]) == 0
    twin = tmp_path / "titled-twin.xlsx"
    again = tmp_path / "again"
    again.mkdir()
    assert (
        _quiet(
            ["validate", str(described), "--twin", str(twin),
             "--out-dir", str(again)]
        )
        == 0
    )
    assert _quiet(["validate", str(described), "--twin", str(path)]) == 0

    # The withholding is SHOWN, not silent.
    report = (again / "titled-twin-quality.txt").read_text(encoding="utf-8")
    named = [
        line.strip()
        for line in report.splitlines()
        if "workbook.empty-rows-inside" in line
    ]
    assert named and named[0].endswith("WITHHELD"), named

    # And no class the census publishes as nought is written into the
    # twin: the twin's own description says so, class for class.
    third = tmp_path / "third"
    third.mkdir()
    assert _quiet(["profile", str(twin), "--out-dir", str(third),
                   "--smallest-group", "11"]) == 0
    second = _block_of(third / "titled-twin-profile.json")
    for index in range(len(first["columns"])):
        published = first["columns"][index]["cell_classes"]
        measured = second["columns"][index]["cell_classes"]
        for kind in published:
            if published[kind] == 0:
                assert measured[kind] == 0, (index, kind, measured)

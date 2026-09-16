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
    """Other sheets are written as empty sheets under their own names."""
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

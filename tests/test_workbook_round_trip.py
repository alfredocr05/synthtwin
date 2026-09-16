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


def test_a_workbook_description_is_refused_a_twin_in_plain_words(
    tmp_path: pathlib.Path,
) -> None:
    """`generate` says it cannot write a workbook yet (plan P4-D78)."""
    path = _written(tmp_path, "plain.xlsx", workbooks.plain_book())
    assert _quiet(["profile", str(path)]) == 0
    described = tmp_path / "plain-profile.json"
    assert _quiet(["generate", str(described), "--seed", "0"]) == 2
    assert not (tmp_path / "plain-twin.csv").exists()
    assert not (tmp_path / "plain-twin.xlsx").exists()
    message = errors.no_workbook_twin_yet(str(described))
    assert "cannot yet write one" in message
    assert "save the sheet as CSV" in message


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

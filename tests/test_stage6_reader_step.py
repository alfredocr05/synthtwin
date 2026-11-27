"""The product reads back every twin it writes: pandas' own step and the blanks a record starts with (lane BT2, plan P4-D448).

THE DEFECT, MEASURED (lane BT's verify, `wave6/BT-verify.md`; re-measured
by lane BT2 at a5702b71). With the chain's switch at its default, the hunt
table's twin at 200,000 rows, seed 3, was refused by the product's own
reader: "two separate readers ... do not agree about the value in row
29109, column 'serial'". Its record 29109 holds nothing, written
``' , ,, ,, ,,,, '``, and its first blank is the 1,310,720th character of
the file: pandas' C reader takes the text in steps of 262,144 characters
and drops the blanks a record starts with where a step ends inside them,
so pandas read ``''`` where the survey read ``' '``. The real table read
fine only because none of its records stands so.

THE CHOICE: THE READER SETTLES IT (`reading._step_settles`). The writer
cannot be the fix: the twin writes each spelling as the source wrote it,
and a real table holding such a record at such a place is refused the
same way. So where pandas' value is the survey's without the blanks a
step cut off that very record's start -- each cut found in the file's
own text and settling one value at most, in the file's order -- the
survey's reading stands, as it stood on the real table; every other
value pandas reads is compared as before.

Every case here is below the owner's table floor, through the library
(the floor is the command's rule); the 200,000-row twin is read back in
K-S6-02's driver under `kpi_run --slow`. Each case beside its mutant:
the settle switched off (`reading._step_settles` answering no) refuses the
same file.
"""

import pathlib
import sys

import pandas
import pytest

import fixtures
from synthtwin import contract, dialect, errors, generation, profile, reading, rendering, taxonomy

STEP = reading._PANDAS_STEP_CHARACTERS


def _placed(folder: pathlib.Path, record: str, start: int, glyph: str = "", above: str = "") -> "tuple[pathlib.Path, int]":
    """A file whose ``record`` line starts at character ``start``, the lines ``above`` (rows of neither reader) just before it: its path and the record's row (from 0)."""
    header = "serial,visits,flag\n"
    filler = f"1{glyph},2,z\n"
    count = (start - len(header) - len(above) - 40) // len(filler)
    text = header + filler * count
    pad = start - len(above) - len(text) - len(",2,z\n")
    text = text + "7" * pad + ",2,z\n" + above
    assert len(text) == start
    text = text + record + "\n" + "3,4,z\n" * 5
    path = folder / "placed.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path, count + 1


def _pandas_first(path: pathlib.Path, row: int) -> str:
    frame = pandas.read_csv(path, dtype=str, keep_default_na=False, na_filter=False, engine="c", encoding="utf-8-sig")
    return f"{frame.iloc[row, 0]}"


def test_pandas_steps_by_the_number_the_reader_names(tmp_path: pathlib.Path) -> None:
    """The installed pandas drops a record's leading blank exactly where a step of `_PANDAS_STEP_CHARACTERS` ends, counted in characters."""
    for glyph in ("", "é"):
        for start, kept in ((STEP - 2, " "), (STEP - 1, ""), (STEP, " "), (2 * STEP - 1, "")):
            path, row = _placed(tmp_path, " , ,", start, glyph)
            assert _pandas_first(path, row) == kept, (glyph, start)


def test_a_record_holding_nothing_cut_by_the_step_is_read_as_written(tmp_path: pathlib.Path) -> None:
    """The record shape of lane BT's verify, its first blank the step's last character: read, and read as the file holds it."""
    path, row = _placed(tmp_path, " , ,", STEP - 1)
    back = reading.read_table(str(path), small_cell_floor=11)
    assert [reading.column_values(back, place)[row] for place in range(3)] == [" ", " ", ""]
    assert _pandas_first(path, row) == ""


def test_red_with_the_step_unsettled(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: with no value settled, the same file is refused, as the base refused the hunt table's twin."""
    monkeypatch.setattr(reading, "_step_settles", lambda settle, mine, theirs, row: False)
    path, _row = _placed(tmp_path, " , ,", STEP - 1)
    with pytest.raises(errors.ProfileError, match="two separate readers"):
        reading.read_table(str(path), small_cell_floor=11)


def test_a_run_of_blanks_cut_inside_and_a_value_behind_it(tmp_path: pathlib.Path) -> None:
    """Three blanks the step cuts after two, and blanks before a value: pandas keeps what follows the cut; the survey's reading stands."""
    path, row = _placed(tmp_path, "   ,x,", STEP - 2)
    assert _pandas_first(path, row) == " "
    assert reading.column_values(reading.read_table(str(path), small_cell_floor=11), 0)[row] == "   "
    path, row = _placed(tmp_path, "  12,x,", STEP - 1)
    assert _pandas_first(path, row) == " 12"
    assert reading.column_values(reading.read_table(str(path), small_cell_floor=11), 0)[row] == "  12"


def test_the_whole_frame_settles_as_the_pieces_do(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """With every piece sent on to the whole frame, the whole frame's comparison settles the same value."""
    monkeypatch.setattr(reading, "_piece_agrees", lambda *given: False)
    path, row = _placed(tmp_path, " , ,", STEP - 1)
    assert reading.column_values(reading.read_table(str(path), small_cell_floor=11), 0)[row] == " "


def _settle(path: pathlib.Path, blanks: str = " \t", delimiter: str = ",") -> "reading._StepBlanks":
    """The matcher the checking pass makes of a headed file: the survey's first row on its second record."""
    return reading._StepBlanks(path, "utf-8-sig", blanks, delimiter, dialect.ESCAPE_DOUBLED, False, 1)


def test_each_cut_settles_its_own_record_once_and_nothing_else(tmp_path: pathlib.Path) -> None:
    """A value pandas reads short is settled only at the row whose own record a cut of this file dropped blanks from, once."""
    path, row = _placed(tmp_path, " , ,", STEP - 1)
    settle = _settle(path)
    assert not reading._step_settles(settle, "x", "", row)
    assert not reading._step_settles(settle, " x", "y", row)
    assert reading._step_settles(settle, " ", "", row)
    assert not reading._step_settles(settle, " ", "", row)
    assert not reading._step_settles(_settle(path), "  ", "", row)
    assert reading._step_cut_leads(path, "utf-8-sig", " \t") == {row + 1: " "}
    assert reading._step_cut_leads(path, "utf-8-sig", "") == {}
    placed, _row = _placed(tmp_path, " , ,", STEP)
    assert reading._step_cut_leads(placed, "utf-8-sig", " \t") == {}


def test_a_cut_settles_no_other_row(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane BT2, item 3: the allowance is bound to the record the cut stands on. A row the step did not cut, read short by pandas (a file changed between the two readings), is not settled by another record's cut; the cut's own row still is."""
    path, row = _placed(tmp_path, " , ,", STEP - 1)
    settle = _settle(path)
    assert not reading._step_settles(settle, " ", "", row - 5)
    assert not reading._step_settles(settle, " ", "", row + 1)
    assert reading._step_settles(settle, " ", "", row)


def _quoted_continuation(folder: pathlib.Path) -> pathlib.Path:
    """Codex's file: a quoted field whose second line starts with a blank the step cuts; both readers read every cell alike."""
    text = "a,b\nx,one\ny,\"" + "q" * (STEP - 15) + "\n z\"\n"
    assert text[STEP - 1 : STEP + 1] == " z"
    path = folder / "quoted.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path


def test_a_line_inside_a_quoted_field_is_no_records_start(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane BT2, item 3: the cut found on a quoted field's second line settles nothing, so a first record pandas read short -- the file rewritten between the survey and pandas, the stale ``' x'`` -- is refused, not settled; the file itself reads."""
    path = _quoted_continuation(tmp_path)
    assert reading._step_cut_leads(path, "utf-8-sig", " \t") == {}
    assert not reading._step_settles(_settle(path), " x", "x", 0)
    back = reading.read_table(str(path), small_cell_floor=11)
    assert reading.column_values(back, 1)[1] == "q" * (STEP - 15) + "\n z"


def test_a_run_of_blanks_longer_than_a_step_is_settled_at_its_last_cut(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane BT2, item 8: a record's blanks running across two step ends lose to pandas every blank before the second; the survey's reading stands (the base and the first build refused the file)."""
    text = "a,b\n" + "x" * (STEP - 10) + ",y\n" + " " * (STEP + 3) + "v,z\n"
    path = tmp_path / "long-run.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    assert _pandas_first(path, 1) == "v"
    assert reading._step_cut_leads(path, "utf-8-sig", " \t") == {2: " " * (STEP + 3)}
    assert reading.column_values(reading.read_table(str(path), small_cell_floor=11), 0)[1] == " " * (STEP + 3) + "v"


def _placed_tab(folder: pathlib.Path, record: str, start: int) -> "tuple[pathlib.Path, int]":
    """A tab-delimited file whose ``record`` line starts at character ``start``: its path and the record's row (from 0)."""
    header = "serial\tvisits\tflag\n"
    filler = "1\t2\tz\n"
    count = (start - len(header) - 40) // len(filler)
    text = header + filler * count
    pad = start - len(text) - len("\t2\tz\n")
    text = text + "7" * pad + "\t2\tz\n"
    assert len(text) == start
    text = text + record + "\n" + "3\t4\tz\n" * 5
    path = folder / "placed.tsv"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path, count + 1


def test_a_tab_delimited_record_cut_by_the_step_is_read_as_written(tmp_path: pathlib.Path) -> None:
    """Lane BT2's skeptic 1, item 5: on a tab-delimited file a space is the blank the step cuts (the tab is the delimiter); the survey's reading stands."""
    path, row = _placed_tab(tmp_path, " \t \t", STEP - 1)
    frame = pandas.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_filter=False, engine="c", encoding="utf-8-sig")
    assert f"{frame.iloc[row, 0]}" == ""
    back = reading.read_table(str(path), small_cell_floor=11)
    assert [reading.column_values(back, place)[row] for place in range(3)] == [" ", " ", ""]


def test_red_with_a_tab_delimited_file_unsettled(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT R4: no blank settled on a tab-delimited file: the same file is refused."""
    built = reading._StepBlanks

    def unsettled(table_path, codec, blanks, delimiter=",", *rest):  # type: ignore[no-untyped-def]
        return built(table_path, codec, "" if delimiter == "\t" else blanks, delimiter, *rest)

    monkeypatch.setattr(reading, "_StepBlanks", unsettled)
    path, _row = _placed_tab(tmp_path, " \t \t", STEP - 1)
    with pytest.raises(errors.ProfileError, match="two separate readers"):
        reading.read_table(str(path), small_cell_floor=11)


def test_blank_lines_above_a_cut_record_stay_out_of_its_count(tmp_path: pathlib.Path) -> None:
    """Lane BT2's verify of its first repair, item 1: a blank line and a line of spaces alone stand above the record the step cuts. Pandas reads both as blank lines and leaves them out of its rows, so they stay out of the count of records too (`reading._blank_to_pandas`), and the cut settles its own record: the file is read as written (red with every such line counted, which refuses it)."""
    path, row = _placed(tmp_path, " , ,", STEP - 1, above="\n   \n")
    assert _pandas_first(path, row) == ""
    back = reading.read_table(str(path), small_cell_floor=11)
    assert [reading.column_values(back, place)[row] for place in range(3)] == [" ", " ", ""]
    assert reading._step_cut_leads(path, "utf-8-sig", " \t") == {row + 1: " "}


def test_the_blank_line_rule_is_the_installed_pandas_own(tmp_path: pathlib.Path) -> None:
    """Lane BT2's second repair: `reading._blank_to_pandas` answers as the installed pandas counts its rows. A line of spaces and tabs alone is a blank line to it unless one of them is the delimiter, the line's first character too: a lone tab in a tab-delimited file, or a lone space in a space-delimited one, is a record of empty cells."""
    bodies = ("", " ", "   ", "\t", "\t\t", " \t ", "\t  ", " \t", "  \t", ",", " ,", "x", " x")
    for delimiter in (",", "\t", ";", " "):
        path = tmp_path / "blank.txt"
        for body in bodies:
            path.write_text(delimiter.join("abcd") + "\n" + delimiter.join("1234") + "\n" + body + "\n5\n", encoding="utf-8", newline="\n")
            frame = pandas.read_csv(path, sep=delimiter, dtype=str, keep_default_na=False, na_filter=False, skip_blank_lines=True, engine="c")
            assert reading._blank_to_pandas(body, delimiter) == (frame.shape[0] == 2), (delimiter, body)


def _placed_pair(folder: pathlib.Path, record: str, start: int, above: str) -> "tuple[pathlib.Path, int]":
    """A two-column tab-delimited file whose ``record`` line starts at character ``start``, the records ``above`` just before it: its path and the record's row (from 0)."""
    header = "serial\tflag\n"
    filler = "1\tz\n"
    count = (start - len(header) - len(above) - 40) // len(filler)
    text = header + filler * count
    pad = start - len(above) - len(text) - len("\tz\n")
    text = text + "7" * pad + "\tz\n" + above
    assert len(text) == start
    text = text + record + "\n" + "3\tz\n" * 5
    path = folder / "pair.tsv"
    path.write_text(text, encoding="utf-8", newline="\n")
    return path, count + 1 + above.count("\n")


def test_a_lone_tab_record_above_a_cut_record_is_counted(tmp_path: pathlib.Path) -> None:
    """Lane BT2's second repair: in a two-column tab-delimited file a record whose cells hold nothing is written as a lone tab, which both readers read as a record. Counted so, the cut below it settles its own record and the file is read as written (the first repair's rule took the lone tab for a blank line, counted the cut one record short and refused the file)."""
    path, row = _placed_pair(tmp_path, " \t", STEP - 1, "\t\n")
    frame = pandas.read_csv(path, sep="\t", dtype=str, keep_default_na=False, na_filter=False, engine="c", encoding="utf-8-sig")
    assert frame.iloc[row - 1].tolist() == ["", ""] and f"{frame.iloc[row, 0]}" == ""
    back = reading.read_table(str(path), small_cell_floor=11)
    assert [reading.column_values(back, place)[row - 1 : row + 1] for place in range(2)] == [["", " "], ["", ""]]
    assert reading._step_cut_leads(path, "utf-8-sig", " ", "\t") == {row + 1: " "}


def test_the_drivers_cells_apart_are_the_cells_the_reader_settles(tmp_path: pathlib.Path) -> None:
    """Codex's review of lane BT2, item 6: K-S6-02 (ix) counts the cells the reader settles, not the cuts a file holds. Under the skipped initial space both readers drop a cut record's leading space, so the cut settles nothing; the record holding nothing settles one cell."""
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
    import kpi_band_totals as kpi

    header = "serial, visits, flag\n"
    filler = "1, 2, z\n"
    count = (STEP - 1 - len(header) - 40) // len(filler)
    text = header + filler * count
    text = text + "7" * (STEP - 1 - len(text) - len(", 2, z\n")) + ", 2, z\n"
    text = text + " 5, 6, z\n" + "3, 4, z\n" * 5
    path = tmp_path / "spaced.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    assert len(reading._step_cut_leads(path, "utf-8-sig", " \t", ",", dialect.ESCAPE_DOUBLED, True)) == 1
    back, apart = kpi._two_readers(path)
    assert back is not None and reading.column_values(back, 0)[count + 1] == "5" and apart == 0
    placed, _row = _placed(tmp_path, " , ,", STEP - 1)
    back, apart = kpi._two_readers(placed)
    assert back is not None and apart == 1


def test_a_twin_the_product_writes_across_the_step_is_read_back(tmp_path: pathlib.Path) -> None:
    """The product's own twin of a table whose first column is a blank: a line starts at the step's last character, and the twin is read back."""
    source = tmp_path / "blank-first.csv"
    source.write_text("k,vvvv\n" + " ,a\n" * 66_000, encoding="utf-8", newline="\n")
    table = reading.read_table(str(source), small_cell_floor=11)
    described = fixtures.write_profile(
        tmp_path, "blank-first.json", profile.build_document(table, taxonomy.Settings(small_cell_floor=11), [], [], [])
    )
    text = "".join(rendering.twin_csv_pieces(generation.generate_held(contract.load_profile(str(described)), 0)))
    assert text[STEP - 2 : STEP + 2] == "\n ,a"
    twin = tmp_path / "blank-first-twin.csv"
    twin.write_text(text, encoding="utf-8", newline="")
    back = reading.read_table(str(twin), small_cell_floor=11)
    assert set(reading.column_values(back, 0)) == {" "}

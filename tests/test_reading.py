"""The two-pass reader and its refusals (plan P1-D3, P1-D7).

The structural pass exists because the data pass cannot be trusted to
report a malformed row: pandas pads a short row out to the header's
width, so `4,5` under a three-column header becomes `4`, `5` and an
empty third value that looks exactly like a genuinely empty cell. The
first test below is the one that would catch that padding coming back.
"""

import pathlib

import pytest

import fixtures
from synthtwin import errors, reading
from synthtwin.paths import PathValidationError


def _read(folder: pathlib.Path, text: str, name: str = "table.csv"):
    return reading.read_table(str(fixtures.write(folder, name, text)))


def test_a_short_row_is_refused_not_padded(tmp_path: pathlib.Path) -> None:
    # The defect this whole design exists to prevent: a row with too few
    # values must never arrive as a row with empty cells SILENTLY. A row
    # short by exactly its trailing empty cells is a way some writers
    # write every row that ends empty (plan P4-D75), and it is read that
    # way only where the whole file agrees: no full row ends with an
    # empty cell and no short row does. Where the file does not agree, a
    # short row is refused exactly as it always was.
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "a,b,c\n1,2,\n4,5\n6,7,8\n")
    message = f"{caught.value}"
    assert "row 2 has 2" in message, message
    assert "3 columns" in message or "names 3" in message, message


def test_rows_short_by_their_empty_cells_are_read_and_published(
    tmp_path: pathlib.Path,
) -> None:
    table = _read(tmp_path, "a,b,c\n1,2,3\n4,5\n6,7,8\n")
    assert table.columns == [["1", "4", "6"], ["2", "5", "7"], ["3", "", "8"]]
    assert table.survey is not None
    assert table.survey.form.short_rows


def test_a_long_row_is_refused_with_its_position(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "a,b\n1,2\n3,4,5\n")
    assert "row 2 has 3" in f"{caught.value}"


def test_ragged_rows_report_the_first_three_and_the_total(
    tmp_path: pathlib.Path,
) -> None:
    rows = ["a,b"] + ["1,2,3"] * 5
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "\n".join(rows) + "\n")
    message = f"{caught.value}"
    assert "row 1 has 3" in message
    assert "row 3 has 3" in message
    assert "row 4" not in message, "only the first three are named"
    assert "5 rows in total" in message


def test_rows_are_counted_after_the_header_and_past_blank_lines(
    tmp_path: pathlib.Path,
) -> None:
    # A blank line is not a row, in either pass. If the two passes
    # counted blank lines differently the agreement check would fire on
    # a perfectly good file.
    table = _read(tmp_path, "a,b\n1,2\n\n3,4\n")
    assert table.n_rows == 2
    assert table.columns == [["1", "3"], ["2", "4"]]


def test_a_value_containing_a_line_break_is_one_value(
    tmp_path: pathlib.Path,
) -> None:
    table = _read(tmp_path, 'a,b\n"first\nsecond",2\n')
    assert table.n_rows == 1
    assert table.columns[0] == ["first\nsecond"]


def test_quoted_commas_do_not_split_a_row(tmp_path: pathlib.Path) -> None:
    table = _read(tmp_path, 'a,b\n"one, two",3\n')
    assert table.columns[0] == ["one, two"]


def test_empty_cells_stay_empty_text(tmp_path: pathlib.Path) -> None:
    # Not a not-a-number float, and not the word "nan": empty text, so
    # that the missing-value rules -- and only they -- decide what it
    # means.
    table = _read(tmp_path, "a,b\n,2\n")
    assert table.columns[0] == [""]
    assert isinstance(table.columns[0][0], str)


def test_duplicate_column_names_are_named_and_written_back(
    tmp_path: pathlib.Path,
) -> None:
    # Refused until plan P4-D75, which cost the person an edit to the
    # real table and code that no longer matched it. A repeated name is
    # named the way pandas names it, and the header cell as the file
    # writes it is published, so the twin's header is the table's.
    table = _read(tmp_path, "a,a,b\n1,2,3\n")
    assert table.column_names == ["a", "a.1", "b"]
    assert table.survey is not None
    written = table.survey.form.written_names
    assert [(entry.position, entry.text) for entry in written] == [(2, "a")]


def test_empty_column_name_is_named_and_written_back(
    tmp_path: pathlib.Path,
) -> None:
    table = _read(tmp_path, "a,,b\n1,2,3\n")
    assert table.column_names == ["a", "Unnamed: 1", "b"]
    assert table.survey is not None
    written = table.survey.form.written_names
    assert [(entry.position, entry.text) for entry in written] == [(2, "")]


def test_a_file_with_no_header_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "1,2\n3,4\n")
    assert "does not look like column names" in f"{caught.value}"


def test_a_header_with_one_word_is_accepted(tmp_path: pathlib.Path) -> None:
    # Only a first row where EVERY cell reads as a number is refused;
    # one numeric-looking name among words is a legitimate column name.
    table = _read(tmp_path, "a,2024\n1,2\n")
    assert table.column_names == ["a", "2024"]


def test_empty_file_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "")
    assert "is empty" in f"{caught.value}"


def test_header_without_rows_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, "a,b\n")
    assert "no data rows" in f"{caught.value}"


def test_missing_file_is_refused_with_the_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(tmp_path / "not-here.csv"))
    assert "There is no file at" in f"{caught.value}"


def test_a_folder_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(tmp_path))
    assert "is a folder, not a file" in f"{caught.value}"


def test_a_url_never_reaches_the_reader() -> None:
    # The path validator refuses it lexically, before any filesystem
    # call and long before the network-capable library is involved
    # (plan P1-D2.1).
    with pytest.raises(PathValidationError):
        reading.read_table("https://example.invalid/table.csv")


def test_utf8_byte_order_mark_is_not_glued_to_the_first_name(
    tmp_path: pathlib.Path,
) -> None:
    target = tmp_path / "bom.csv"
    target.write_bytes("﻿a,b\n1,2\n".encode())
    table = reading.read_table(str(target))
    assert table.column_names == ["a", "b"]


def test_latin1_fallback_reads_a_file_utf8_cannot(
    tmp_path: pathlib.Path,
) -> None:
    target = tmp_path / "latin.csv"
    target.write_bytes("name,note\ncafé,ok\n".encode("latin-1"))
    table = reading.read_table(str(target))
    assert table.used_fallback_encoding
    assert table.encoding == "latin-1"
    assert table.columns[0] == ["café"]


def test_utf16_behind_its_mark_is_read(tmp_path: pathlib.Path) -> None:
    # Excel's 'Unicode Text' is UTF-16 behind a byte-order mark, and it is
    # read as the text it is (plan P4-D75). Without the mark Latin-1
    # would still decode anything, which is why the zero-byte refusal
    # below stays.
    target = tmp_path / "wide.csv"
    target.write_bytes(b"\xff\xfe" + "a,b\n1,2\n".encode("utf-16-le"))
    table = reading.read_table(str(target))
    assert table.column_names == ["a", "b"]
    assert table.encoding == "utf-16-le"
    assert not table.used_fallback_encoding


def test_utf16_without_its_mark_is_refused_with_advice(
    tmp_path: pathlib.Path,
) -> None:
    target = tmp_path / "wide.csv"
    target.write_bytes("a,b\n1,2\n".encode("utf-16-le"))
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "UTF-16" in f"{caught.value}"


def test_binary_content_is_refused(tmp_path: pathlib.Path) -> None:
    target = tmp_path / "picture.csv"
    target.write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00")
    with pytest.raises(errors.ProfileError):
        reading.read_table(str(target))


def test_an_over_long_value_is_refused(tmp_path: pathlib.Path) -> None:
    # An unclosed quotation mark makes the reader run to the end of the
    # file looking for its partner; the limit is what turns that into a
    # message instead of an unbounded read.
    huge = "x" * (reading.FIELD_SIZE_LIMIT + 10)
    with pytest.raises(errors.ProfileError) as caught:
        _read(tmp_path, f'a,b\n"{huge}",2\n')
    assert "longer than" in f"{caught.value}"


def test_the_field_size_limit_is_restored_afterwards(
    tmp_path: pathlib.Path,
) -> None:
    import csv

    before = csv.field_size_limit()
    _read(tmp_path, "a,b\n1,2\n")
    assert csv.field_size_limit() == before, (
        "the reader must put the standard library's per-value limit back "
        "the way it found it: it is a setting of the whole program"
    )


def test_every_role_fixture_reads_with_the_expected_shape(
    tmp_path: pathlib.Path,
) -> None:
    table = _read(tmp_path, fixtures.every_role_table())
    assert table.n_rows == 240
    assert len(table.column_names) == 13
    assert all(len(column) == 240 for column in table.columns)
    assert not table.used_fallback_encoding

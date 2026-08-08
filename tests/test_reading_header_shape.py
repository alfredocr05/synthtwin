"""What SHAPE alone can and cannot settle about the first row.

These are the regressions for the second half of review item P1-R1-F5,
found while reviewing the round-6 reader design. Every one of them fails
against that design:

* a column of numbers whose FIRST value simply has fewer digits than the
  rest was read as a CONTRADICTION -- proof that the first row is a
  header -- and that verdict overrode two other columns that said, as
  loudly as this rule can say it, that the first row looks exactly like
  a record. The file was accepted with a person's values as column
  names and one record fewer;
* a headerless table with one word column and one number column was
  accepted the same way, because a number column can never contradict a
  first row that is itself a number, and words of different lengths
  share no signature;
* a blank line in a table of ONE column was dropped, which deletes a
  record and a missing value from the description without a word;
* the message for two readings that disagree about a column name said
  the file must have changed, which is not the only cause and, for a
  file nobody was writing to, sends the reader after a ghost;
* the profile document recorded how the file was decoded but not
  whether the column names came out of it, so a profile built with
  --first-row data claimed names the table never had.

No data file is committed: every table here is built from bytes in the
test that needs it (plan D13).
"""

import pathlib

import pytest

from synthtwin import errors, profile, reading, taxonomy


def _write(folder: pathlib.Path, body: bytes) -> pathlib.Path:
    target = folder / "table.csv"
    target.write_bytes(body)
    return target


def _rows(*lines: str) -> bytes:
    return ("\n".join(lines) + "\n").encode()


# --------------------------------------------------------------------
# headerless tables whose first row must not become the column names
# --------------------------------------------------------------------

_HEADERLESS = {
    "a record only narrower than its own column": _rows(
        *[
            f"{7 if index == 0 else 11 + index},2024-01-{3 + index:02d},"
            f"alpha{index}"
            for index in range(9)
        ]
    ),
    "a record narrower in its only shaped column": _rows(
        *[
            f"{9 if index == 0 else 10 + index},site{index % 3},x"
            for index in range(9)
        ]
    ),
    "words of differing lengths beside numbers": _rows(
        "elm,140", "birch,99", "fir,20", "sycamore,7", "oak,101", "yew,3"
    ),
    "labels, places and amounts": _rows(
        "aa bb,cc dd,120.50",
        "ee ff,gg hh,89.9",
        "ii jj,kk ll,1004.25",
        "mm nn,oo pp,17.5",
        "qq rr,ss tt,340.0",
        "uu vv,ww xx,9.75",
    ),
    "one shaped column and free text": _rows(
        "aaa,12.5,some note",
        "bb,13.25,another note",
        "cccc,9.5,a third note",
        "ddddd,101.125,and a fourth",
    ),
}


@pytest.mark.parametrize("name", sorted(_HEADERLESS))
def test_a_first_row_shape_cannot_settle_is_refused(
    tmp_path: pathlib.Path, name: str
) -> None:
    target = _write(tmp_path, _HEADERLESS[name])
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    message = f"{caught.value}"
    assert "cannot tell whether the first row" in message, message
    assert "--first-row names" in message and "--first-row data" in message


# --------------------------------------------------------------------
# ordinary headed tables that must still go through without a question
# --------------------------------------------------------------------

_HEADED = {
    "wide-format year columns over decimals": _rows(
        "region,2019,2020",
        *[f"place {index},3.1{index},3.2{index}" for index in range(1, 13)],
    ),
    "wide-format year columns over counts": _rows(
        "county,2019,2020",
        *[f"place {index},{100 + index},{200 + index}" for index in range(1, 13)],
    ),
    "item columns over a coded scale": _rows(
        "record_id,q1,q2,q3", *[f"{100 + index},1,2,3" for index in range(12)]
    ),
    "names that look like their own codes": _rows(
        "visit1,visit2", *[f"a{index % 9},b{index % 9}" for index in range(12)]
    ),
    "two-letter names over two-letter codes": _rows(
        "aa,bb", *["xy,zw" for _index in range(12)]
    ),
    "a subject column of differing widths": _rows(
        "subject,age,score,note",
        *[f"S{index},{20 + index},{index * 1.5},note {index}" for index in range(12)],
    ),
}


@pytest.mark.parametrize("name", sorted(_HEADED))
def test_an_ordinary_headed_table_is_not_questioned(
    tmp_path: pathlib.Path, name: str
) -> None:
    target = _write(tmp_path, _HEADED[name])
    table = reading.read_table(str(target))
    assert table.header_source == reading.HEADER_FROM_FILE
    assert table.n_rows == 12


# --------------------------------------------------------------------
# a blank line in a table of one column
# --------------------------------------------------------------------


def test_a_blank_line_in_a_one_column_table_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # Dropping it silently deletes a record AND a missing value -- the
    # two things this tool exists to describe.
    target = _write(tmp_path, b"age\n34\n\n36\n41\n50\n")
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    message = f"{caught.value}"
    assert "empty line" in message, message
    assert "only one column" in message, message


def test_blank_lines_at_the_ends_are_not_refused(
    tmp_path: pathlib.Path,
) -> None:
    # A file that ends with a spare newline is ordinary, and a leading
    # blank line costs nothing: neither can be a record with data still
    # to come.
    for body in (b"age\n34\n36\n41\n50\n\n", b"\nage\n34\n36\n41\n50\n"):
        target = _write(tmp_path, body)
        table = reading.read_table(str(target))
        assert table.n_rows == 4, body
    # A blank line in a wider table carries no values at all.
    target = _write(tmp_path, b"age,site\n34,a\n\n36,b\n41,c\n50,d\n")
    assert reading.read_table(str(target)).n_rows == 4


# --------------------------------------------------------------------
# the message for a name the two readers read differently
# --------------------------------------------------------------------


def test_the_name_disagreement_message_names_both_causes() -> None:
    # Two readers can disagree about the FIRST row for exactly the
    # reasons they can disagree about any other row. Naming only the
    # rewrite sends a reader of a static file after a ghost.
    message = errors.readers_disagree_about_a_name(
        "/data/table.csv", 1, "note", "Unnamed: 0"
    )
    assert "writing to the file" in message
    assert "read differently" in message
    assert "changed between the two readings" not in message


def test_a_static_file_can_reach_the_name_disagreement(
    tmp_path: pathlib.Path,
) -> None:
    # Found by differential fuzzing: nobody rewrites this file, and the
    # two readers still name its one column differently.
    target = _write(tmp_path, b"\r \" \n \r \r\\'\t\t")
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "name of column number 1" in f"{caught.value}", f"{caught.value}"


# --------------------------------------------------------------------
# the profile must say where the column names came from
# --------------------------------------------------------------------


def test_the_profile_says_the_column_names_were_generated(
    tmp_path: pathlib.Path,
) -> None:
    target = _write(tmp_path, b"P001,34\nP002,35\nP003,36\nP004,37\nP005,38\n")
    table = reading.read_table(str(target), reading.FIRST_ROW_DATA)
    document = profile.build_document(table, taxonomy.Settings(), [])
    source = document["source"]
    assert isinstance(source, dict)
    assert source["header_source"] == reading.HEADER_GENERATED
    read = reading.read_table(str(target), reading.FIRST_ROW_NAMES)
    named = profile.build_document(read, taxonomy.Settings(), [])
    assert named["source"]["header_source"] == reading.HEADER_FROM_FILE

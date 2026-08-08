"""What the two reading passes prove, and how the header is decided.

These are the regressions for review items P1-R1-F4, P1-R1-F5,
P1-R1-F15 and P1-R1-F18, and for R1-X3 from the round-1 response.
Every one of them fails against the reader as it stood at round 5:

* the two passes compared row and column COUNTS, so a file rewritten
  between them was accepted with the old header and the new values, a
  zero byte past the fifth row truncated a value in one reader only,
  and a stray carriage return moved values between columns;
* a headerless file became a table with one fewer record and somebody's
  identifier published as a column name;
* the pass that claimed to hold one row at a time held all of them;
* a Latin-1 header beginning with the byte 0xFF was refused as UTF-16.

No data file is committed: every table here is built from bytes in the
test that needs it (plan D13).
"""

import csv
import io
import pathlib
import random
import tracemalloc

import pytest

from synthtwin import cli, errors, profile, reading


def _write(folder: pathlib.Path, body: bytes, name: str = "table.csv"):
    target = folder / name
    target.write_bytes(body)
    return target


def _numbered(count: int, template: bytes) -> bytes:
    return b"".join(template % index for index in range(1, count + 1))


# --------------------------------------------------------------------
# P1-R1-F4 and R1-X3: the passes must agree about VALUES
# --------------------------------------------------------------------


def test_a_file_rewritten_between_the_passes_is_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The exact round-1 reproduction: same shape, new header, new
    # values. Counts alone cannot see it.
    target = _write(tmp_path, b"old_name,value\nold_a,1\nold_b,2\n")
    real = reading._read_authoritatively

    def rewrite_after_reading(table_path, shown, first_row):
        found = real(table_path, shown, first_row)
        pathlib.Path(table_path).write_bytes(
            b"new_name,value\nnew_a,8\nnew_b,9\n"
        )
        return found

    monkeypatch.setattr(reading, "_read_authoritatively", rewrite_after_reading)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    message = f"{caught.value}"
    assert "name of column number 1" in message, message
    assert "old_name" in message and "new_name" in message, message


def test_values_rewritten_between_the_passes_are_refused(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The harder half: the header is untouched, so only a value
    # comparison can catch it.
    target = _write(tmp_path, b"name,value\nold_a,1\nold_b,2\n")
    real = reading._read_authoritatively

    def rewrite_after_reading(table_path, shown, first_row):
        found = real(table_path, shown, first_row)
        pathlib.Path(table_path).write_bytes(b"name,value\nnew_a,8\nnew_b,9\n")
        return found

    monkeypatch.setattr(reading, "_read_authoritatively", rewrite_after_reading)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    message = f"{caught.value}"
    assert "row 1, column 'name'" in message, message
    # A value is somebody's data; a refusal never prints one.
    assert "old_a" not in message and "new_a" not in message, message


def test_a_zero_byte_past_the_first_rows_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    # pandas' reader stops the value at the zero byte and the standard
    # reader keeps it whole: six rows and two columns either way.
    body = (
        b"a,b\n"
        + b"".join(b"v%d,w%d\n" % (index, index) for index in range(1, 6))
        + b"alpha\x00omega,z\n"
    )
    target = _write(tmp_path, body)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "zero bytes" in f"{caught.value}", f"{caught.value}"


def test_readers_that_split_a_row_differently_are_refused(
    tmp_path: pathlib.Path,
) -> None:
    # R1-X3. The standard reader yields ["", "B"] and pandas' C reader
    # yields ["B", ""]: two columns profiled wrongly, equal counts, no
    # zero byte anywhere. Binding both readers to the same bytes cannot
    # catch this one; only comparing the values can.
    target = _write(tmp_path, b"c0,c1\n\r,B\nz,w\n")
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "do not agree about the value" in f"{caught.value}", f"{caught.value}"


def test_the_agreement_check_is_silent_on_well_formed_files(
    tmp_path: pathlib.Path,
) -> None:
    # A control that refuses ordinary files is worse than none. Every
    # awkward thing CSV allows, both line endings, 300 seeded files.
    rng = random.Random(20260808)
    words = ["", "a", "b b", 'q"q', "one, two", "line\nbreak", "0", "-1", " x "]
    target = tmp_path / "well-formed.csv"
    for trial in range(300):
        width = rng.randint(1, 4)
        buffer = io.StringIO()
        writer = csv.writer(
            buffer, lineterminator="\r\n" if trial % 2 else "\n"
        )
        writer.writerow([f"col_{index}" for index in range(width)])
        for _ in range(rng.randint(1, 6)):
            writer.writerow([rng.choice(words) for _ in range(width)])
        target.write_bytes(buffer.getvalue().encode())
        table = reading.read_table(str(target))
        with target.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = [row for row in csv.reader(handle) if row]
        assert table.column_names == rows[0]
        assert table.columns == [
            [row[index] for row in rows[1:]] for index in range(len(rows[0]))
        ]


# --------------------------------------------------------------------
# P1-R1-F5: the header decision
# --------------------------------------------------------------------

_HEADERLESS = {
    "identifier beside a measurement": b"P001,34\nP002,35\nP003,36\n"
    b"P004,37\nP005,38\nP006,39\n",
    "all text": b"".join(
        b"pa-%03d,site-%d\n" % (index, index % 3) for index in range(1, 30)
    ),
    "one data row": b"P001,34\nP002,35\n",
    "wide": b"".join(
        b"P%03d,site-%d,2024-01-0%d,%d\n"
        % (index, index % 3, index % 9 + 1, index)
        for index in range(1, 20)
    ),
    "one free-text column among coded ones": b"".join(
        b"P%03d,%d,note number %d\n" % (index, index, index)
        for index in range(1, 20)
    ),
}

_HEADED = {
    "pivoted years over one-digit values": b"region,2019,2020,2021\n"
    + b"".join(b"r%d,1,2,3\n" % index for index in range(1, 15)),
    "pivoted years over four-digit values": b"region,2019,2020,2021\n"
    + b"".join(b"place%d,1234,1567,1890\n" % index for index in range(1, 15)),
    "identifier column with a real name": b"record_code,age\n"
    + b"".join(b"P%03d,%d\n" % (index, 30 + index) for index in range(1, 20)),
    "a column whose name looks like a code": b"age,B10\n"
    + b"".join(b"%d,B%02d\n" % (30 + index, index) for index in range(1, 20)),
    "a date column beside a coded one": b"visit,B10\n"
    + b"".join(b"2024-01-%02d,B%02d\n" % (index, index) for index in range(1, 20)),
    "ordinary mixed table": b"label,age,note\n"
    + b"".join(
        b"item %d,%d,a note\n" % (index, 20 + index) for index in range(1, 20)
    ),
    "single text column": b"town\n"
    + b"".join(b"place %d\n" % index for index in range(1, 20)),
    "short repeated labels": b"hue,n\n"
    + b"".join(
        b"%s,%d\n" % (label, index)
        for index, label in enumerate([b"red", b"tan", b"sky"] * 6)
    ),
}


@pytest.mark.parametrize("name", sorted(_HEADERLESS))
def test_a_first_row_that_could_be_a_record_is_refused(
    tmp_path: pathlib.Path, name: str
) -> None:
    target = _write(tmp_path, _HEADERLESS[name])
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    message = f"{caught.value}"
    assert "cannot tell whether the first row" in message, message
    assert "--first-row names" in message and "--first-row data" in message
    # The row itself is never quoted back: if it IS a record, printing
    # it prints somebody's data in order to ask about it.
    assert "P001" not in message and "pa-001" not in message, message


@pytest.mark.parametrize("name", sorted(_HEADED))
def test_an_ordinary_headed_table_is_not_questioned(
    tmp_path: pathlib.Path, name: str
) -> None:
    # The rule sketched at round 1 refused the two pivoted year tables.
    target = _write(tmp_path, _HEADED[name])
    table = reading.read_table(str(target))
    assert table.header_source == reading.HEADER_FROM_FILE
    assert table.column_names[0] == _HEADED[name].split(b"\n")[0].split(b",")[
        0
    ].decode()


def test_first_row_data_keeps_every_record_and_names_the_columns(
    tmp_path: pathlib.Path,
) -> None:
    target = _write(tmp_path, _HEADERLESS["identifier beside a measurement"])
    table = reading.read_table(str(target), reading.FIRST_ROW_DATA)
    assert table.n_rows == 6, "not one record may be lost"
    assert table.column_names == ["column_1", "column_2"]
    assert table.columns[0][0] == "P001"
    assert table.header_source == reading.HEADER_GENERATED


def test_first_row_names_still_reads_the_first_row_as_names(
    tmp_path: pathlib.Path,
) -> None:
    target = _write(tmp_path, _HEADERLESS["identifier beside a measurement"])
    table = reading.read_table(str(target), reading.FIRST_ROW_NAMES)
    assert table.column_names == ["P001", "34"]
    assert table.n_rows == 5
    assert table.header_source == reading.HEADER_FROM_FILE


def test_the_command_refuses_and_then_accepts_the_answer(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    target = _write(tmp_path, _HEADERLESS["identifier beside a measurement"])
    assert cli.main(["profile", str(target)]) == 1
    refusal = capsys.readouterr()
    assert "--first-row data" in refusal.err, refusal.err
    assert cli.main(["profile", str(target), "--first-row", "data"]) == 0
    written = capsys.readouterr().out
    assert "6 rows" in written, written
    assert "column_1" in written, written


# --------------------------------------------------------------------
# P1-R1-F15: the memory model
# --------------------------------------------------------------------


def test_the_authoritative_pass_does_not_hold_every_row(
    tmp_path: pathlib.Path,
) -> None:
    # The claim P1-D3 made and the code did not keep. A pass that
    # streams peaks a hair above what it hands back; one that builds a
    # list of every row and turns it into columns afterwards peaks at
    # about 1.43 times that, measured at 5,000, 50,000 and 200,000 rows.
    # The threshold sits between the two.
    target = tmp_path / "big.csv"
    with target.open("w", encoding="utf-8", newline="") as handle:
        handle.write("record_code,site,amount,note\n")
        for index in range(20_000):
            handle.write(
                f"R{index:08d},site-{index % 7},{(index % 977) * 0.5},"
                f"note number {index}\n"
            )
    tracemalloc.start()
    tracemalloc.reset_peak()
    found = reading._read_authoritatively(
        target, f"{target}", reading.FIRST_ROW_AUTOMATIC
    )
    held, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert found.n_rows == 20_000
    assert peak <= held * 1.15, (
        f"the authoritative pass peaked at {peak} bytes while handing back "
        f"{held}: it is holding more than one row at a time, which is what "
        f"P1-D3 promises it does not do"
    )


def test_running_out_of_memory_in_the_checking_pass_is_a_refusal(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = _write(tmp_path, b"a,b\n" + _numbered(20, b"%d,x\n"))

    def out_of_memory(*_args: object, **_kwargs: object) -> None:
        raise MemoryError("simulated")

    monkeypatch.setattr(reading, "_check_against_pandas", out_of_memory)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "not enough memory" in f"{caught.value}"


def test_running_out_of_memory_while_describing_is_not_a_traceback(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    target = _write(tmp_path, b"a,b\n" + _numbered(20, b"%d,x\n"))

    def out_of_memory(*_args: object, **_kwargs: object) -> None:
        raise MemoryError("simulated")

    monkeypatch.setattr(profile, "build_document", out_of_memory)
    assert cli.main(["profile", str(target)]) == 1
    assert "not enough memory" in capsys.readouterr().err


# --------------------------------------------------------------------
# P1-R1-F18: byte-order marks are complete byte sequences
# --------------------------------------------------------------------

_TAIL = b"".join(b"x,%d\n" % index for index in range(12))


@pytest.mark.parametrize(
    "name,body",
    sorted(
        {
            "a Latin-1 name beginning with 0xFF": b"\xffnote,value\n" + _TAIL,
            "a Latin-1 name beginning with 0xFE": b"\xfenote,value\n" + _TAIL,
        }.items()
    ),
)
def test_a_lone_high_byte_is_not_a_byte_order_mark(
    tmp_path: pathlib.Path, name: str, body: bytes
) -> None:
    target = _write(tmp_path, body)
    table = reading.read_table(str(target))
    assert table.used_fallback_encoding
    assert table.column_names[0][1:] == "note"


@pytest.mark.parametrize(
    "name,body",
    sorted(
        {
            "UTF-16 little-endian": b"\xff\xfe"
            + "a,b\n1,2\n".encode("utf-16-le"),
            "UTF-16 big-endian": b"\xfe\xff" + "a,b\n1,2\n".encode("utf-16-be"),
            "UTF-32 little-endian": b"\xff\xfe\x00\x00"
            + "a,b\n1,2\n".encode("utf-32-le"),
        }.items()
    ),
)
def test_a_complete_byte_order_mark_is_refused(
    tmp_path: pathlib.Path, name: str, body: bytes
) -> None:
    target = _write(tmp_path, body)
    with pytest.raises(errors.ProfileError) as caught:
        reading.read_table(str(target))
    assert "UTF-16" in f"{caught.value}"

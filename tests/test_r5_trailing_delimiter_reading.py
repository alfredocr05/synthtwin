"""Lane R5, reading (plan P4-D387): a trailing delimiter on one side, and huge figures.

1. **A trailing delimiter on one side only.** A semicolon table whose
   rows end in `;` and whose header does not was read as ONE column
   named by its whole header line, holding whole records as free text:
   `profile` exited 0, asked nothing and described one column, so code
   written on its twin could not run on the real table. The rule that
   the table's first record has the table's width rejected the semicolon
   reading (a header of four fields over rows of five), no other
   candidate read two fields, and the comma a table no candidate reads
   falls back to took it. The same held for a tab or a vertical bar, and
   for a header ending in the delimiter over rows that do not. The walk
   in `dialect.survey` already read both shapes; detection now accepts
   exactly those two (`dialect.opening_lines_up`).
2. **A whole number of 5,001 figures.** `dialect._sequence_of` turned
   the first cell, and every later one, into an int, and Python refuses
   to read an int of more than 4,300 figures from text: ValueError, the
   reader crashed. Sequence cells are now compared as text.

Each test is red on the mutant it names: `opening_lines_up` answering
False everywhere (the rule withdrawn), and `_sequence_of` as it was.
"""

import contextlib
import io
import json
import pathlib
import sys

import pytest

from synthtwin import dialect

ROWS = 400
NAMES = ("record_id", "age", "arm", "weight")


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process, quietly, and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _table(delimiter: str, header_ends: bool, rows_end: bool, ending: str = "\n") -> bytes:
    """A neutral made-up table of four columns, with or without trailing delimiters."""
    header = delimiter.join(NAMES) + (delimiter if header_ends else "")
    lines = [header]
    for index in range(ROWS):
        cells = [
            f"P{index + 1:04d}",
            f"{18 + (index * 13) % 70}",
            ("F", "M")[index % 2],
            f"{50 + (index * 7) % 40},{index % 10}" if delimiter == ";" else f"{50 + (index * 7) % 40}.{index % 10}",
        ]
        lines += [delimiter.join(cells) + (delimiter if rows_end else "")]
    return (ending.join(lines) + ending).encode("utf-8")


def _round_trip(folder: pathlib.Path, data: bytes) -> "dict[str, object]":
    """Describe, build, describe the twin again; validate the twin and the table."""
    folder.mkdir(parents=True, exist_ok=True)
    real = folder / "real.csv"
    real.write_bytes(data)
    assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"]) == 0
    described = folder / "real-profile.json"
    assert _exit_of(
        ["generate", str(described), "--out-dir", str(folder), "--seed", "4", "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    assert _exit_of(["profile", str(copied), "--out-dir", str(again), "--replace"]) == 0
    first = json.loads(described.read_text(encoding="utf-8"))
    second = json.loads((again / "twin-profile.json").read_text(encoding="utf-8"))
    exits = {}
    for label, target in (("twin", twin), ("real", real)):
        checked = folder / f"check-{label}"
        checked.mkdir()
        exits[label] = _exit_of(
            ["validate", str(described), "--twin", str(target), "--out-dir", str(checked), "--replace"]
        )
    return {
        "names": [column["name"] for column in first["columns"]],
        "form": first["source"]["dialect"],
        "twin_form": second["source"]["dialect"],
        "twin": twin.read_bytes(),
        "exits": exits,
    }


def _ends(data: bytes, delimiter: str) -> "list[bool]":
    """Which lines end in the delimiter, line by line."""
    mark = delimiter.encode()
    return [line.rstrip(b"\r").endswith(mark) for line in data.split(b"\n") if line]


@pytest.mark.parametrize(
    ("label", "delimiter", "header_ends", "rows_end", "ending"),
    [
        ("semicolon rows", ";", False, True, "\n"),
        ("semicolon rows crlf", ";", False, True, "\r\n"),
        ("semicolon header", ";", True, False, "\n"),
        ("tab rows", "\t", False, True, "\n"),
        ("bar header", "|", True, False, "\r\n"),
    ],
)
def test_a_trailing_delimiter_on_one_side_is_read_as_the_delimiter(
    tmp_path: pathlib.Path, label: str, delimiter: str, header_ends: bool,
    rows_end: bool, ending: str,
) -> None:
    """The table is read as its four columns, named as the header names
    them, and the twin writes each line's trailing delimiter where the
    source wrote one. Red on the mutant: one column named by the whole
    header line."""
    data = _table(delimiter, header_ends, rows_end, ending)
    result = _round_trip(tmp_path, data)
    assert result["names"] == list(NAMES), (label, result["names"])
    assert result["form"]["delimiter"] == delimiter, label
    assert result["form"]["trailing_delimiter"] == {"header": header_ends, "rows": rows_end}
    assert _ends(result["twin"], delimiter) == _ends(data, delimiter), label
    assert result["twin_form"] == result["form"], label
    assert result["exits"] == {"twin": 0, "real": 0}, (label, result["exits"])


def test_detection_lines_up_only_the_two_shapes_the_survey_reads() -> None:
    """`opening_lines_up` on its own: the two shapes, and the files it
    leaves as they were read."""
    rows_end = "a;b;c\n1;2;3;\n4;5;6;\n7;8;9;\n"
    header_ends = "a\tb\tc\t\n1\t2\t3\n4\t5\t6\n"
    assert dialect.delimiter_reading(rows_end, 0) == (";", ())
    assert dialect.delimiter_reading(header_ends, 0) == ("\t", ())
    # Each counts the header at the table's width: a share of one.
    assert dialect._best_reading(rows_end, ";", 0)[0] == 1.0
    assert dialect._best_reading(header_ends, "\t", 0)[0] == 1.0
    # A one-column table whose cells end in `;` stays one column: its
    # first record is one field wide.
    assert dialect.delimiter_reading("name\nalpha;\nbeta;\ngamma;\n", 0) == (",", ())
    # Rows one field wider than their header whose last field is not
    # always empty line up with nothing.
    assert dialect._best_reading("id|age|site\n1|2|3|x\n4|5|6|\n7|8|9|y\n", "|", 0) is None
    # A header one field wider whose last field holds a name does not
    # line up either.
    assert dialect._best_reading("a;b;c;d\n1;2;3\n4;5;6\n", ";", 0) is None
    # EXACTLY ONE FIELD, EITHER WAY (lane R5's repair, skeptic item 2).
    # A header two fields narrower than rows that end empty, and a
    # header two fields wider whose last field is empty, line up with
    # nothing. Red on the mutants that accept one OR TWO either way.
    assert dialect._best_reading("a;b\n1;2;3;\n4;5;6;\n", ";", 0) is None
    assert dialect.delimiter_reading("a;b\n1;2;3;\n4;5;6;\n", 0) == (",", ())
    assert dialect._best_reading("a;b;c;;\n1;2;3\n4;5;6\n", ";", 0) is None


def test_tables_read_right_before_are_read_as_before() -> None:
    """The readings this rule could not reach: delimiter, tie and share of
    tables the reader already read right (the lane's battery measured
    their descriptions and twins byte-identical; these pin the readings)."""
    plain = "a;b;c\n1;2;3\n4;5;6\n"
    both = "a;b;c;\n1;2;3;\n4;5;6;\n"
    comma_rows = "a,b,c\n1,2,3,\n4,5,6,\n"
    assert dialect.delimiter_reading(plain, 0) == (";", ())
    assert dialect.delimiter_reading(both, 0) == (";", ())
    assert dialect._best_reading(both, ";", 0)[:2] == (1.0, 4)
    # The comma form read right before only as the fall-back; it now
    # reads as the comma itself, the same delimiter and no tie.
    assert dialect.delimiter_reading(comma_rows, 0) == (",", ())


def test_the_lining_up_reads_no_more_than_the_sample_at_a_million_rows() -> None:
    """Machine-free: the records `opening_lines_up` is handed, summed over
    every candidate, spacing and escaping, are the same at 1,000 rows and
    at 1,000,000, because detection reads a bounded sample."""
    seen: "list[int]" = []
    shipped = dialect.opening_lines_up

    def counting(sample, opening, width):
        seen[len(seen):] = [len(sample)]
        return shipped(sample, opening, width)

    totals = []
    for rows in (1_000, 1_000_000):
        text = "a;b;c;d\n" + "1;22;3;4;\n" * rows
        del seen[:]
        dialect.opening_lines_up = counting
        try:
            assert dialect.delimiter_reading(text, 0)[0] == ";"
        finally:
            dialect.opening_lines_up = shipped
        totals += [sum(seen)]
        del text
    assert totals[0] == totals[1], totals
    assert totals[1] <= 16 * dialect._SAMPLE_RECORDS, totals


def test_a_whole_number_of_5001_figures_reads_without_a_crash(tmp_path: pathlib.Path) -> None:
    """`_sequence_of` asks no int of a cell: a first cell, or a later one,
    of 5,001 figures is no sequence and raises nothing. Red on the
    function as it was: ValueError past Python's 4,300 figures."""
    huge = "1" + "0" * 5000
    assert dialect._sequence_of([huge, "2", "3"]) == -1
    assert dialect._sequence_of(["1", "2", huge]) == -1
    assert dialect._sequence_of(["0", "1", "2"]) == 0
    assert dialect._sequence_of(["1", "2", "3"]) == 1
    assert dialect._sequence_of(["1", "02", "3"]) == -1
    assert dialect._sequence_of(["2", "3", "4"]) == -1
    for place in (0, 5):
        lines = ["big,age"]
        for index in range(120):
            lines += [f"{huge if index == place else index + 1},{20 + index % 50}"]
        folder = tmp_path / f"at-{place}"
        folder.mkdir()
        real = folder / "real.csv"
        real.write_bytes(("\n".join(lines) + "\n").encode())
        assert _exit_of(["profile", str(real), "--out-dir", str(folder), "--replace"]) == 0


def _said(argv: "list[str]") -> "tuple[int, str]":
    """Run one synthtwin command in this process and return its exit code and what it printed."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    sink = io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            code = cli.main()
    except SystemExit as stop:
        code = 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return (code, " ".join(sink.getvalue().split()))


def _uneven(header_ends: bool, row_end: "dict[int, str]", default: "str | None", rows: int) -> bytes:
    """A semicolon table whose rows end as ``row_end`` says (index -> ending, None for none)."""
    lines = [";".join(NAMES) + (";" if header_ends else "")]
    for index in range(rows):
        cells = [
            f"P{index + 1:04d}",
            f"{18 + (index * 13) % 70}",
            ("F", "M")[index % 2],
            # Decimal POINTS, as in skeptic 1's probes: with decimal
            # commas the baseline refused these files anyway.
            f"{50 + (index * 7) % 40}.{index % 10}",
        ]
        ending = row_end[index] if index in row_end else default
        lines += [";".join(cells) + ("" if ending is None else ";" + ending)]
    return ("\n".join(lines) + "\n").encode("utf-8")


@pytest.mark.parametrize(
    ("label", "data", "reason"),
    [
        (
            "one row in ten does not end in the semicolon",
            _uneven(False, {index: None for index in range(3, 120, 10)}, "", 120),
            "row 4 does not end in a semicolon, row 14 does not end in a "
            "semicolon, row 24 does not end in a semicolon (12 rows in total)",
        ),
        (
            "row 501, past the sample, does not end in the semicolon",
            _uneven(False, {500: None}, "", 600),
            "row 501 does not end in a semicolon.",
        ),
        (
            "row 501, past the sample, holds a value after its last semicolon",
            _uneven(False, {500: "x"}, "", 600),
            "row 501 has a value after the semicolon that ends the other rows.",
        ),
        (
            "the header ends in the semicolon and row 51 does too",
            _uneven(True, {50: ""}, None, 120),
            "row 51 ends in a semicolon.",
        ),
    ],
    ids=["one-in-ten-unclosed", "row-501-unclosed", "row-501-value-after", "header-closed-row-51-closed"],
)
def test_a_row_that_does_not_close_like_the_others_is_refused_for_that_reason(
    tmp_path: pathlib.Path, label: str, data: bytes, reason: str,
) -> None:
    """THE REFUSAL STATES ITS TRUE REASON (lane R5's repair, skeptic item 1).

    These semicolon tables were described as ONE column before the
    lining-up rule (exit 0 on 0ecc82d, measured); read now
    under the semicolon, a row that does not close the way the others
    do cannot be read, and the file is refused. The ragged-rows sentence
    said "The first row names 4 columns, but row 51 has 4" and blamed a
    value needing quotation marks; red on that message, this one names
    the row and the trailing semicolon it lacks or carries."""
    real = tmp_path / "real.csv"
    real.write_bytes(data)
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, (label, code, said)
    assert reason in said, (label, said)
    assert "Make every row end the same way" in said, (label, said)
    assert "quotation marks" not in said, (label, said)
    assert "names 4 columns" not in said, (label, said)


def test_a_ragged_row_among_trailing_rows_keeps_the_ragged_reason(tmp_path: pathlib.Path) -> None:
    """Only a file whose EVERY offender differs by the trailing delimiter
    alone gets the new sentence: one row of six fields among rows that
    end in `;` is still ragged, and says so as before."""
    data = _uneven(False, {50: "x;y"}, "", 120)
    real = tmp_path / "real.csv"
    real.write_bytes(data)
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, said
    assert "The first row names 4 columns, but row 51 has 6" in said, said

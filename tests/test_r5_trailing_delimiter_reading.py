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

from synthtwin import dialect, errors

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


def _with_rows(data: bytes, rows: "dict[int, str]") -> bytes:
    """``data`` with the data rows numbered in ``rows`` (1-based, after the header) replaced."""
    lines = data.decode("utf-8").split("\n")
    for number, text in rows.items():
        lines[number] = text
    return "\n".join(lines).encode("utf-8")


@pytest.mark.parametrize(
    ("label", "rows", "shown", "hidden"),
    [
        (
            "probe A: row 51 holds three values and ends in the semicolon",
            {51: "P0051;age;arm;"},
            "The first row names 4 columns, but row 51 has 3.",
            "does not end in",
        ),
        (
            "probe E: row 51 ends in two semicolons",
            {51: "P0051;30;F;55.0;;"},
            "The first row names 4 columns, but row 51 has 5.",
            "row 51 has 6",
        ),
        (
            "probe F: row 51 is unclosed and row 61 holds two values",
            {51: "P0051;30;F;55.0", 61: "P0061;30;"},
            "The first row names 4 columns, but row 61 has 2 (2 rows in total).",
            "row 51 has 4",
        ),
        (
            "probe K: row 51 holds two values and does not end in the semicolon",
            {51: "P0051;30"},
            "The first row names 4 columns, but row 51 has 2.",
            "does not end in",
        ),
    ],
    ids=[
        "probe-A-three-values-closed",
        "probe-E-two-closing",
        "probe-F-mixed",
        "probe-K-two-values-unclosed",
    ],
)
def test_a_row_the_reading_cannot_read_is_named_by_its_own_values(
    tmp_path: pathlib.Path, label: str, rows: "dict[int, str]", shown: str, hidden: str,
) -> None:
    """THE RAGGED SENTENCE COUNTS A ROW'S OWN VALUES (lane R5's second
    repair, skeptic 2 items 1 and 2).

    Rows ending in `;` over a header that does not. A row that ends in
    the semicolon like the others but holds three values was filed as
    lacking the trailing semicolon ("row 51 does not end in a
    semicolon", false), red here on that filing (mutant
    ``kind0_no_closed_check``). A row of two values that does not close
    (probe K, `P0051;30`) is short, not merely unclosed: "row 51 has 2",
    red on mutant ``kind0_count_only`` (``count <= width and not
    closed``), which files it as lacking the semicolon and hides its
    missing values.
    The closing empty field is the delimiter, not a value, so the ragged
    sentence counts 3 and 5, not 4 and 6. And in a file mixing an
    unclosed row with a ragged one, the unclosed row of four values is
    left out of the ragged listing ("names 4 columns, but row 51 has 4"
    contradicts itself) yet counted in the total; red on mutant
    ``any_uneven_not_every``, which names row 51 alone and hides row 61."""
    real = tmp_path / "real.csv"
    real.write_bytes(_with_rows(_uneven(False, {}, "", 120), rows))
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, (label, code, said)
    assert shown in said, (label, said)
    assert hidden not in said, (label, said)
    assert "Make every row end the same way" not in said, (label, said)


def test_a_quoted_empty_last_value_is_a_value_not_the_closing_delimiter(
    tmp_path: pathlib.Path,
) -> None:
    """A QUOTED EMPTY LAST VALUE IS NOT THE CLOSING DELIMITER (lane R5's
    third repair, verifier item 2, probe Q).

    Rows ending in `;` over a header that does not; row 51 is
    `P0051;30;F;""`: four values, the last one quoted and empty, and no
    closing semicolon. The row holds every value and lacks only the
    trailing semicolon, so that is the sentence; reading the quoted
    empty field as the delimiter said "row 51 has 3", which is false
    (red on mutant ``closed_ignores_quote``: ``closed`` without the
    ``found.quoted`` test)."""
    real = tmp_path / "real.csv"
    real.write_bytes(_with_rows(_uneven(False, {}, "", 120), {51: 'P0051;30;F;""'}))
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, (code, said)
    assert "row 51 does not end in a semicolon" in said, said
    assert "row 51 has 3" not in said, said


# -- Codex's review of landing R5 (head 3215f2e), 2026-10-13 -----------


def _read(text: str) -> "dialect.Survey":
    """The reader's settled survey of a text, its first row the names."""
    return dialect.settle(text, "utf-8", False, False, "t.csv")


def _competing() -> str:
    """Codex item 1: a comma table the baseline read right, with a short
    row 51, whose header also ends in a semicolon."""
    lines = ["id,notes,measure;type;unit;"]
    for index in range(1, 121):
        lines += [f"{index},x;y;z,6" if index != 51 else "51,x;y;z"]
    return "\n".join(lines) + "\n"


def test_a_reading_read_right_before_is_not_taken_by_a_lined_up_one() -> None:
    """A STRAIGHT READING COMES BEFORE A LINED-UP ONE (Codex item 1).

    Under the comma the header and 119 rows are three fields and row 51
    is a supported short row (an empty last cell left out): 120 of 121.
    Under the semicolon the header ends in `;` and lines up with rows of
    three, every one: 121 of 121. On 3215f2e the lined-up reading won on
    that share and the table was read as `id,notes,measure`, `type`,
    `unit` over rows such as `1,x`, `y`, `z,6`, with no question. A
    reading whose first record already has the table's width is the one
    0ecc82d took, and it stands; the lined-up reading reads the file at
    least as consistently, so it is recorded as the competitor and the
    person is asked. Red on 3215f2e (`(";", ())`)."""
    text = _competing()
    assert dialect.delimiter_reading(text, 0) == (",", (",", ";"))
    found = _read(text)
    assert found.form.delimiter == ","
    assert list(found.header) == ["id", "notes", "measure;type;unit;"]
    assert [column[0] for column in found.columns] == ["1", "x;y;z", "6"]
    assert [column[50] for column in found.columns] == ["51", "x;y;z", ""]
    assert found.form.short_rows
    assert not found.form.header_trailing_delimiter
    assert found.delimiter_tie == (",", ";")


def test_the_tie_notice_says_why_the_straight_reading_was_taken(tmp_path: pathlib.Path) -> None:
    """The notice printed for Codex item 1's file names the reason the
    comma was taken -- its first row is as wide as the rows -- and not a
    count of columns or of numbers, which are the same or not asked."""
    real = tmp_path / "real.csv"
    real.write_bytes(_competing().encode("utf-8"))
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said
    assert "READS EQUALLY WELL WITH MORE THAN ONE DELIMITER" in said, said
    assert "as many fields as the rows" in said, said


def _rows_of(header: str, rows: "list[str]") -> str:
    return header + "\n" + "".join(row + "\n" for row in rows)


@pytest.mark.parametrize(
    ("label", "text", "header", "cell"),
    [
        ("rows end in a quoted empty value", _rows_of("a;b", ['1;2;""'] * 120), "a;b", '1;2;""'),
        ("the header ends in a quoted empty name", _rows_of('a;b;""', ["1;2"] * 120), 'a;b;""', "1;2"),
        (
            "rows end in a bare and a quoted empty field by turns",
            _rows_of("a;b", ['1;2;""', "1;2;"] * 60),
            "a;b",
            '1;2;""',
        ),
    ],
    ids=["rows-quoted", "header-quoted", "mixed"],
)
def test_a_quoted_empty_last_field_lines_a_reading_up(
    label: str, text: str, header: str, cell: str
) -> None:
    """A QUOTED EMPTY LAST FIELD CLOSES A LINE TOO (lane R6, superseding
    Codex item 2's refusal of landing R5). Item 2 found the twin writing
    `1;2;` where the source wrote `1;2;""`, and R5 stopped reading such a
    field as the closing delimiter, so these files were read as ONE
    comma-delimited column. The twin now closes each line as the source
    closed it, so the semicolon reads them as their two columns: the
    rows closed `""` throughout, the header closed `""`, and the rows
    closed both ways by turns -- runs of one, below the census line, so
    published closed the commonest way, a tie going bare. Red on
    6a248e7, which read each as one column."""
    assert dialect.delimiter_reading(text, 0) == (";", ()), label
    found = _read(text)
    assert list(found.header) == ["a", "b"], (label, header)
    assert [column[0] for column in found.columns] == cell.split(";")[:2], label
    form = found.form
    if label.startswith("the header"):
        assert form.header_trailing_delimiter and form.header_closing_quoted, label
        assert not form.rows_trailing_delimiter, label
    else:
        assert not form.header_trailing_delimiter, label
        assert form.rows_trailing_delimiter, label
        assert form.rows_closing_quoted == label.startswith("rows end in a quoted"), label
        assert form.rows_closing_runs == (), label


_QUOTED_SENTENCE = 'ends in an empty value in quotation marks ("")'
_NAME_SENTENCE = 'The first row of t.csv ends in an empty name in quotation marks ("")'


def _refusal(text: str, mark: bool = False) -> str:
    """The reader's refusal of a text, its first row the names, on one
    line; ``mark`` says a byte-order mark led the file."""
    with pytest.raises(errors.ProfileError) as refused:
        dialect.settle(text, "utf-8", mark, False, "t.csv")
    return " ".join(str(refused.value).split())


def _past_the_sample(quoted: "range") -> str:
    """600 rows ending in `;` under a header that does not; the rows
    numbered in ``quoted`` end in `;""` instead (the verifier's probe)."""
    lines = []
    for number in range(1, 601):
        lines += [f"P{number:04d};30;F;" + ('""' if number in quoted else "")]
    return _rows_of("id;age;arm", lines)


@pytest.mark.parametrize(
    ("label", "text", "listed"),
    [
        ("row 501 alone", _past_the_sample(range(501, 502)), "but row 501 " + _QUOTED_SENTENCE + "."),
        (
            "rows 451 to 600",
            _past_the_sample(range(451, 601)),
            "row 453 " + _QUOTED_SENTENCE + " (150 rows in total).",
        ),
        (
            "row 501 alone, CRLF and a byte-order mark",
            "\ufeff" + _past_the_sample(range(501, 502)).replace("\n", "\r\n"),
            "but row 501 " + _QUOTED_SENTENCE + ".",
        ),
    ],
    ids=["row-501", "rows-451-600", "row-501-crlf-bom"],
)
def test_a_quoted_empty_closing_past_the_sample_is_read_and_published_at_the_line(
    label: str, text: str, listed: str
) -> None:
    """A QUOTED EMPTY CLOSING PAST THE SAMPLE (Codex item 2's verifier,
    open half (a); lane R6). Rows ending in `;` under a header that does
    not; row 501, past the 400-record sample, ends `;""`. R5 refused the
    file so that the `""` was not lost silently; it is now read as the
    closing it is. One row closed `""` is a count of one, below the
    census line, so the closings are published bare throughout as the
    line endings are (plan P4-D290); 150 rows closed `""` in one run
    stand, and are published as that run. Red on 6a248e7, which refused
    each."""
    mark = text[:1] == "\ufeff"
    found = dialect.settle(text[1:] if mark else text, "utf-8", mark, False, "t.csv")
    assert list(found.header) == ["id", "age", "arm"], label
    assert found.n_rows == 600, label
    form = found.form
    assert form.rows_trailing_delimiter and not form.rows_closing_quoted, label
    if "151" in listed or "150 rows" in listed:
        assert form.rows_closing_runs == (
            dialect.EndingRun(ending=dialect.CLOSING_BARE, lines=450),
            dialect.EndingRun(ending=dialect.CLOSING_QUOTED, lines=150),
        ), label
    else:
        assert form.rows_closing_runs == (), label


@pytest.mark.parametrize(
    ("label", "text", "said"),
    [
        (
            "rows end in a quoted empty value",
            _rows_of("a,b", ['1,2,""'] * 120),
            "The first row names 2 columns, but row 1 has 3",
        ),
        ("the header ends in a quoted empty name", _rows_of('a,b,""', ["1,2"] * 120), _NAME_SENTENCE),
        (
            "rows end in a quoted empty value and a bare comma by turns",
            _rows_of("a,b", ['1,2,""', "1,2,"] * 60),
            "but row 1 " + _QUOTED_SENTENCE,
        ),
        (
            "rows end in a bare comma and a quoted empty value by turns",
            _rows_of("a,b", ["1,2,", '1,2,""'] * 60),
            "but row 2 " + _QUOTED_SENTENCE,
        ),
    ],
    ids=["rows-quoted", "header-quoted", "mixed-quoted-first", "mixed-bare-first"],
)
def test_the_comma_forms_of_a_quoted_empty_last_field_are_read(
    label: str, text: str, said: str
) -> None:
    """THE COMMA FORMS (Codex item 2's verifier, open half (b); lane R6).
    The comma is the fall-back, so these never needed detection; R5
    refused each so that no `""` was written back bare. Each is now read
    as two columns with the closing spelled as the source spelled it:
    `""` on every row, `""` on the header, and the two mixes published
    bare (runs of one, below the census line). Red on 6a248e7, which
    refused each (``said`` is the sentence it refused with)."""
    found = _read(text)
    assert found.form.delimiter == ",", label
    assert list(found.header) == ["a", "b"], (label, said)
    form = found.form
    if label.startswith("the header"):
        assert form.header_trailing_delimiter and form.header_closing_quoted, label
        assert not form.rows_trailing_delimiter, label
        return
    assert form.rows_trailing_delimiter, label
    assert form.rows_closing_quoted == (label == "rows end in a quoted empty value"), label
    assert form.rows_closing_runs == (), label


def test_two_wider_rows_among_rows_at_the_header_width_keep_the_ragged_reason() -> None:
    """The quoted rows are named only where every row is one field
    wider than the header and ends empty, the mix above. Where the rows
    mostly have the header's width and one ends `,""` and another `,`,
    the rows do not end in the comma, and the ragged sentence names both
    (red on the mutant that names the quoted row whenever both kinds
    stand)."""
    body = ["1,2"] * 120
    body[4] = '1,2,""'
    body[8] = "1,2,"
    said = _refusal(_rows_of("a,b", body))
    assert "The first row names 2 columns, but row 5 has 3, row 9 has 3" in said, said
    assert _QUOTED_SENTENCE not in said, said


_DELIMITERS = [",", ";", "\t", "|"]
_DELIMITER_IDS = ["comma", "semicolon", "tab", "bar"]


@pytest.mark.parametrize("delimiter", _DELIMITERS, ids=_DELIMITER_IDS)
def test_a_closed_header_over_quoted_empty_values_reads_three_columns(delimiter: str) -> None:
    """Both sides end at the same place, the header in a bare delimiter
    and every row in `""` (`a;b;` over `1;2;""`). bbce243 took both for
    closing delimiters and its twin wrote `1;2;`. Every row holds a
    third value, so the header's closing delimiter names a third column
    with no name, and nothing is taken off; the twin writes `""` back
    (the round trip below). Red on bbce243 under all four delimiters."""
    found = _read(_rows_of(f"a{delimiter}b{delimiter}", [f'1{delimiter}2{delimiter}""'] * 120))
    assert found.form.delimiter == delimiter
    assert list(found.header) == ["a", "b", ""]
    assert [column[0] for column in found.columns] == ["1", "2", ""]
    assert not found.form.header_trailing_delimiter
    assert not found.form.rows_trailing_delimiter


@pytest.mark.parametrize("delimiter", _DELIMITERS, ids=_DELIMITER_IDS)
def test_a_quoted_empty_against_a_closing_delimiter_on_both_sides_is_read(delimiter: str) -> None:
    """THE QUOTED EMPTY WHERE THE OTHER LINES CLOSE (Codex item 2's
    verifier, step (iii); lane R6). Header and rows end at the same
    place, one side in `""` and the other in a bare delimiter, or the
    rows in both by turns. R5 refused each, because the twin closed
    every line bare; the header's closing is now published as it was
    written, and the rows' runs of one fall below the census line and
    are published bare, so each reads as two columns closed on both
    sides. Red on 6a248e7 under all four delimiters."""
    d = delimiter
    found = _read(_rows_of(f'a{d}b{d}""', [f"1{d}2{d}"] * 120))
    assert list(found.header) == ["a", "b"]
    assert found.form.header_trailing_delimiter and found.form.header_closing_quoted
    assert found.form.rows_trailing_delimiter and not found.form.rows_closing_quoted
    for row in ([f'1{d}2{d}""', f"1{d}2{d}"], [f"1{d}2{d}", f'1{d}2{d}""']):
        for head in (f"a{d}b{d}", f'a{d}b{d}""'):
            found = _read(_rows_of(head, row * 60))
            assert list(found.header) == ["a", "b"], (head, row)
            assert found.form.header_trailing_delimiter, (head, row)
            assert found.form.header_closing_quoted == head.endswith('""'), (head, row)
            assert found.form.rows_trailing_delimiter, (head, row)
            assert not found.form.rows_closing_quoted, (head, row)
            assert found.form.rows_closing_runs == (), (head, row)


def test_a_quoted_empty_name_written_quoted_throughout_is_read() -> None:
    """The refusal is owed only where the twin would close the line: a
    header quoted throughout (`"a";"b";""`) is written so, `""` and
    all, and reads as three columns over rows `1;2;`."""
    found = _read(_rows_of('"a";"b";""', ["1;2;"] * 120))
    assert list(found.header) == ["a", "b", ""]
    assert found.form.header_quoting == dialect.QUOTE_ALWAYS


@pytest.mark.parametrize(("delimiter", "word"), [(",", "comma"), (";", "semicolon")], ids=["comma", "semicolon"])
def test_the_quoted_empty_values_are_written_back(tmp_path: pathlib.Path, delimiter: str, word: str) -> None:
    """The round trip of `a;b;` over `1;2;""`: the twin writes `""` at
    the end of every row as the source did, reads back to the same
    form, and twin and table validate at 0. On bbce243 it wrote `1;2;`."""
    data = _rows_of(f"a{delimiter}b{delimiter}", [f'{index}{delimiter}{index % 7}{delimiter}""' for index in range(120)])
    result = _round_trip(tmp_path, data.encode("utf-8"))
    twin = result["twin"].split(b"\n")
    assert twin[0] == f"a{delimiter}b{delimiter}".encode(), (word, twin[:2])
    assert twin[1].endswith(f'{delimiter}""'.encode()), (word, twin[:2])
    assert result["twin_form"] == result["form"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


@pytest.mark.parametrize(
    ("label", "text", "cell"),
    [
        ("quoted values, rows ending in the semicolon", '"id"; "note"\n' + '"1"; "alpha";\n' * 120, "alpha"),
        (
            "a quoted value holding the semicolon",
            '"id"; "note"\n' + '"1"; "alpha; beta";\n' * 120,
            "alpha; beta",
        ),
        ("the header ending in the semicolon", '"id"; "note";\n' + '"1"; "alpha"\n' * 120, "alpha"),
        ("both ending in the semicolon", '"id"; "note";\n' + '"1"; "alpha; beta";\n' * 120, "alpha; beta"),
    ],
    ids=["rows", "rows-holding-the-delimiter", "header", "both"],
)
def test_the_closing_delimiter_is_not_asked_for_a_space(label: str, text: str, cell: str) -> None:
    """THE SPACING READS THE CLOSING DELIMITER AS THE ADMISSION DOES
    (Codex item 3). `"id"; "note"` over `"1"; "alpha";` lines up under
    the semicolon read with the space after it skipped; on 3215f2e
    `detected_initial_space` then asked the closing delimiter's empty
    field for its space, found none, and read the file without the
    space: names `id` and ` "note"`, values ` "alpha"`, a twin header
    naming ` "note"` with its quotation marks; holding `alpha; beta`, the record split into four
    and the file was refused. `_spaces_broken` asked the same of the
    walk's records. The closing delimiter has no field after it to
    carry a space, and neither asks it now. Red on 3215f2e."""
    found = _read(text)
    assert found.form.delimiter == ";", label
    assert found.form.initial_space, label
    assert list(found.header) == ["id", "note"], label
    assert [column[0] for column in found.columns] == ["1", cell], label


def test_the_spaced_twin_is_written_and_read_back_as_its_source(tmp_path: pathlib.Path) -> None:
    """Codex item 3's round trip: the twin's header is `"id"; "note"` as
    the source wrote it, each row ends in the semicolon, the twin reads
    back to the same form, and both validate at exit 0."""
    rows = [f'"{index}"; "note {index % 9}";' for index in range(120)]
    data = ('"id"; "note"\n' + "\n".join(rows) + "\n").encode("utf-8")
    result = _round_trip(tmp_path, data)
    assert result["names"] == ["id", "note"], result["names"]
    assert result["form"]["initial_space"], result["form"]
    assert result["twin"].split(b"\n")[0] == b'"id"; "note"', result["twin"][:40]
    assert result["twin_form"] == result["form"]
    assert result["exits"] == {"twin": 0, "real": 0}, result["exits"]


def _header_closed(delimiter: str, row_51: str) -> bytes:
    lines = [delimiter.join(["col_a", "col_b", "col_c"]) + delimiter]
    for index in range(1, 121):
        lines += [delimiter.join(["31", "72", "Q"]) if index != 51 else row_51]
    return ("\n".join(lines) + "\n").encode("utf-8")


_WORDS = {",": "comma", ";": "semicolon", "\t": "tab", "|": "vertical bar"}


@pytest.mark.parametrize("delimiter", [",", ";", "\t", "|"], ids=["comma", "semicolon", "tab", "bar"])
def test_a_quoted_empty_value_after_a_closed_header_is_a_fourth_value(
    tmp_path: pathlib.Path, delimiter: str
) -> None:
    """THE REFUSAL'S REASON IS THE ROW'S (Codex item 4). The header ends
    in the delimiter and the rows do not; row 51 is `31,72,Q,""`: four
    values, the last quoted and empty, so it holds a value more than the
    header names, which is what 0ecc82d said of the comma form. 3215f2e
    said "row 51 ends in a comma" and asked for uniform endings, though
    the row ends in quotation marks. Red on 3215f2e, all four
    delimiters."""
    real = tmp_path / "real.csv"
    real.write_bytes(_header_closed(delimiter, delimiter.join(["31", "72", "Q", '""'])))
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, (delimiter, code, said)
    assert "The first row names 3 columns, but row 51 has 4" in said, said
    assert "ends in a" not in said, said
    assert "Make every row end the same way" not in said, said


@pytest.mark.parametrize("delimiter", [",", ";", "\t", "|"], ids=["comma", "semicolon", "tab", "bar"])
def test_a_bare_closing_delimiter_after_a_closed_header_keeps_its_reason(
    tmp_path: pathlib.Path, delimiter: str
) -> None:
    """The header-only trailing case beside item 4: row 51 ends in a bare
    delimiter, so it does end in it, and the trailing-delimiter sentence
    stands, for each of the four delimiters."""
    real = tmp_path / "real.csv"
    real.write_bytes(_header_closed(delimiter, delimiter.join(["31", "72", "Q"]) + delimiter))
    code, said = _said(["profile", str(real), "--out-dir", str(tmp_path), "--replace"])
    assert code == 1, (delimiter, code, said)
    word = _WORDS[delimiter]
    assert f"row 51 ends in a {word}" in said, said
    assert "Make every row end the same way" in said, said

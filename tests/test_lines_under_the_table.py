"""Lines written under a table are named as such, not as a quoting fault (lane ZOO-X).

Measured by the data-type zoo (`tests/types_zoo.py`, the total_row
table): a report saved with a row of totals and a line saying when it
ran under its rows was refused with "a value contains a comma and needs
quotation marks around it", which sent a person hunting through 20,000
rows for a comma that is not there. Where every row that does not fit
the columns is one of the file's last rows, the refusal now says they
are lines under the table and asks for them -- and a row of totals above
them -- to be deleted. A ragged row anywhere else keeps the quoting
sentence. Each test below is red on the mutant that drops the reading
(`rows` not passed to `errors.ragged_rows`, or its test removed).
"""

from __future__ import annotations

import contextlib
import io
import pathlib

from synthtwin import cli, errors


def test_rows_that_end_the_file_are_named_lines_under_the_table() -> None:
    message = errors.ragged_rows("/data/report.csv", 4, [(602, 1)], 1, "a comma", 602)
    assert "last 1 line(s)" in message
    assert "delete those last lines" in message
    assert "a row of totals" in message
    assert "quotation marks" not in message
    two = errors.ragged_rows("/data/report.csv", 4, [(601, 1), (602, 2)], 2, "a comma", 602)
    assert "last 2 line(s)" in two and "row 601 has 1" in two


def test_a_ragged_row_inside_the_table_keeps_the_quoting_sentence() -> None:
    for offenders, total, rows in (([(17, 3)], 1, 602), ([(601, 1), (602, 1)], 5, 602), ([(600, 1)], 1, 602)):
        message = errors.ragged_rows("/data/report.csv", 4, offenders, total, "a comma", rows)
        assert "needs quotation marks" in message, (offenders, total, rows)
        assert "delete those last lines" not in message
    assert "needs quotation marks" in errors.ragged_rows("/data/report.csv", 4, [(602, 1)], 1)


def _profile(path: pathlib.Path, refused: bool = True) -> str:
    sink = io.StringIO()
    with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
        code = cli.main(["profile", f"{path}", "--out-dir", f"{path.parent}", "--replace"], small_tables_refused=False)
    assert (code == 1) == refused, (code, sink.getvalue()[-400:])
    return sink.getvalue()


ROWS = [f"R{place:06d},Lab,{10 + place % 40}.50,2024-01-{1 + place % 28:02d}" for place in range(300)]


def test_the_command_names_a_footer_under_a_report(tmp_path: pathlib.Path) -> None:
    lines = ["visit_ref,service,charge,posted_on", *ROWS]
    lines += ["Total,,4321.00,", "", "Report generated 2024-01-31 by the information office"]
    footer = tmp_path / "report.csv"
    footer.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    said = _profile(footer)
    assert "delete those last lines" in said, said
    assert "quotation marks" not in said
    middle = tmp_path / "middle.csv"
    broken = lines[:-3]
    broken[120] = "R000119,Lab,10.50,2024-01-01,extra"
    middle.write_text("\n".join(broken) + "\n", encoding="utf-8", newline="\n")
    said = _profile(middle)
    assert "needs quotation marks" in said, said


def test_a_closing_line_is_no_row_with_its_last_values_left_off(tmp_path: pathlib.Path) -> None:
    """No row ends in an empty value, so the closing line was read as a short row: its sentence a key, the rest blank."""
    lines = ["visit_ref,service,charge,posted_on", *ROWS, "Report generated 2024-01-31 by the information office"]
    footer = tmp_path / "closing.csv"
    footer.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    said = _profile(footer)
    assert "delete those last lines" in said, said
    # A short row of two values, or one inside the table, is read as before.
    for name, tail in (("two", ["R999999,Lab"]), ("inside", [])):
        rows = list(ROWS)
        if not tail:
            rows[150] = "R000150"
        kept = tmp_path / f"{name}.csv"
        kept.write_text("\n".join(["visit_ref,service,charge,posted_on", *rows, *tail]) + "\n", encoding="utf-8", newline="\n")
        _profile(kept, refused=False)


def test_a_row_of_totals_under_the_table_is_refused_in_words_that_name_it(tmp_path: pathlib.Path) -> None:
    for word in ("Total", "GRAND TOTAL", " totals "):
        lines = ["visit_ref,service,charge,posted_on", *ROWS, f"{word},All,4321.00,2024-01-31"]
        totals = tmp_path / "totals.csv"
        totals.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        said = _profile(totals)
        assert "a row of totals" in said and "delete that last row" in said, said
        assert "4321" not in said
    # A total word on a row that is not the last, or on two rows, is a value of the table.
    for rows in (
        [*ROWS[:100], "Total,All,1.00,2024-01-31", *ROWS[100:]],
        [*ROWS, "Total,All,1.00,2024-01-31", "Total,All,2.00,2024-01-31"],
    ):
        kept = tmp_path / "kept.csv"
        kept.write_text("\n".join(["visit_ref,service,charge,posted_on", *rows]) + "\n", encoding="utf-8", newline="\n")
        _profile(kept, refused=False)

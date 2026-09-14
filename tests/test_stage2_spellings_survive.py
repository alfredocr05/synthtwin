"""Stage 2: the twin writes values the way the source wrote them.

WHAT THIS FILE PINS. Three spellings the twin changes today, each of
which makes a researcher's numbers wrong with NO ERROR RAISED. These
are the tests first, red, and the repair follows them.

**1. A THOUSANDS SEPARATOR.** A charge written `$2,198.92` comes back
from the twin as `$2198.92`. A researcher develops on the twin, never
sees a separator, writes the obvious parser, and it converts all of it.
Run that same code on the REAL table and every charge over a thousand
fails to convert and is silently discarded. Measured on 1,000 rows: a
mean of 412 against a true 918, with no error and nothing in any report
mentioning the separator. **This is the worst defect in the product**,
because it is a single-column analysis -- the one thing the tool tells a
reader it is reliable at -- and because the patients it drops are the
expensive ones a cost study is about.

`parsing._without_group_separators` already reads the grouping properly:
a comma is accepted only where the whole part reads as groups of exactly
three digits after a first group of one to three. Six callers use it and
NOT ONE records that it fired, so the fact never reaches the profile and
the generator cannot write it back.

**2. A MOMENT'S SEPARATOR.** Every clinical warehouse writes a timestamp
with a space: `2025-09-04 06:16:00`. The twin writes a capital T.
`parsing.parse_datetime` observes the separator, accepts "T", " " or
"t", and then returns a canonical form, discarding which it saw. Code
that splits or searches on that character works on every twin row and no
real row, returning the untouched stamp with no error.

**3. A DATE STORED AT MIDNIGHT.** A date-only field is held as the date
plus 00:00:00. The tool reads midnight as a real clock reading and
invents times across the whole day: 800 of 800 real rows at midnight
became 2 of 800. An after-hours or case-start-time analysis is then
built on a distribution that does not exist.

WHY THESE ARE ONE FILE. All three are the same failure -- a spelling the
source chose that the description does not record -- and a reader
meeting one should meet the other two.

Every table here is built by seeded neutral code at runtime (plan D13);
no committed data file is read.
"""

import csv
import datetime
import io
import pathlib
import random
import sys

import pytest

from tests import fixtures


def _run(argv: "list[str]") -> None:
    """Run one synthtwin command in this process and require success."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        cli.main()
    except SystemExit as stop:
        if stop.code not in (None, 0):
            raise AssertionError(f"{argv} exited {stop.code}") from stop
    finally:
        sys.argv = before


def _twin_of(folder: pathlib.Path, name: str, text: str) -> "list[list[str]]":
    """Describe the table, build the twin, return the twin's rows."""
    table = folder / f"{name}.csv"
    # `newline=""`: the bytes on disk are the bytes composed above, on
    # every platform, which is what the line-ending guard requires.
    table.write_text(text, encoding="utf-8", newline="")
    _run(["profile", str(table), "--out-dir", str(folder), "--replace"])
    _run(
        [
            "generate",
            str(folder / f"{name}-profile.json"),
            "--out-dir",
            str(folder),
            "--seed",
            "4",
            "--replace",
        ]
    )
    written = (folder / f"{name}-twin.csv").read_text(encoding="utf-8")
    # READ IT AS CSV, NOT BY SPLITTING ON COMMAS. Review caught this:
    # once the comma repair lands, the twin correctly QUOTES the cell
    # (`rendering._needs_quoting` already does), a naive split
    # fragments `"2,198.92"` into two pieces, the first holds no
    # comma, and this witness would go on reporting the defect open
    # after it had been repaired -- silently, with the suite green.
    # A test that cannot detect its own fix is worse than no test.
    return [row for row in csv.reader(io.StringIO(written))]


def _charges(count: int) -> "list[str]":
    """Costs written the way finance writes them, with a group separator."""
    draw = random.Random(21)
    amounts = [round(2.718281828 ** (6.4 + draw.gauss(0, 1.0)), 2) for _ in range(count)]
    return [f"{amount:,.2f}" for amount in amounts]


def _stamps(count: int) -> "list[str]":
    """Moments written with a SPACE, as every warehouse writes them."""
    draw = random.Random(22)
    start = datetime.datetime(2025, 3, 1)
    return [
        (start + datetime.timedelta(minutes=draw.randrange(0, 400000))).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        for _ in range(count)
    ]


def _service_dates(count: int) -> "list[str]":
    """A date-only field, held as the date plus midnight."""
    draw = random.Random(23)
    start = datetime.date(2025, 3, 1)
    return [
        (start + datetime.timedelta(days=draw.randrange(0, 300))).isoformat()
        + " 00:00:00"
        for _ in range(count)
    ]


def test_a_thousands_separator_survives_into_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """A charge written `2,198.92` is written that way in the twin.

    The witness for the worst defect in the product. Without it, code
    developed on the twin silently discards every charge over a
    thousand when it meets the real table.
    """
    count = 600
    amounts = _charges(count)
    carried = sum(1 for amount in amounts if "," in amount)
    assert carried > 100, "the fixture itself must hold plenty of separators"
    rows = _twin_of(
        tmp_path,
        "charges",
        fixtures.rows_to_csv(["charge"], [[amount] for amount in amounts]),
    )
    grouped = sum(1 for row in rows[1:] if "," in row[0])
    assert grouped > 0, (
        f"the source wrote {carried} of {count} charges with a thousands "
        f"separator and the twin wrote none. Code developed on this twin "
        f"will silently drop every charge over a thousand from the real "
        f"table: measured, a mean of 412 against a true 918."
    )


@pytest.mark.xfail(
    reason="stage 2 is not built yet: `parse_datetime` observes the "
    "separator and discards it, so the twin always writes a T",
    strict=True,
)
def test_a_moment_keeps_the_separator_the_source_used(
    tmp_path: pathlib.Path,
) -> None:
    """A stamp written with a space is written with a space in the twin."""
    count = 400
    rows = _twin_of(
        tmp_path,
        "stamps",
        fixtures.rows_to_csv(["admit_ts"], [[stamp] for stamp in _stamps(count)]),
    )
    spaced = sum(1 for row in rows[1:] if len(row[0]) > 10 and row[0][10] == " ")
    assert spaced == count, (
        f"the source wrote all {count} moments with a space and the twin "
        f"wrote {spaced} that way. Code that splits or searches on that "
        f"character works on every twin row and no real row, returning "
        f"the untouched stamp with no error raised."
    )


@pytest.mark.xfail(
    reason="stage 2 is not built yet: midnight is read as a clock "
    "reading, so times of day are invented across the range",
    strict=True,
)
def test_a_date_held_at_midnight_stays_at_midnight(
    tmp_path: pathlib.Path,
) -> None:
    """A date-only field is not given an invented time of day."""
    count = 400
    rows = _twin_of(
        tmp_path,
        "service",
        fixtures.rows_to_csv(
            ["service_date"], [[day] for day in _service_dates(count)]
        ),
    )
    midnight = sum(1 for row in rows[1:] if row[0].endswith("00:00:00"))
    assert midnight == count, (
        f"every one of the {count} source rows sat at midnight, which is "
        f"how a warehouse holds a date with no time, and the twin left "
        f"{midnight} there. An after-hours or case-start-time analysis "
        f"developed on this twin is built on a distribution that does "
        f"not exist in the real table."
    )

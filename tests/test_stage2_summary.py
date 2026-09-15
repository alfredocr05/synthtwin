"""Stage 2: the plain-language summary says the three new spellings aloud.

WHAT THIS FILE PINS. Stage 2 taught the description three facts about
how a column was WRITTEN (plan P4-D38, P4-D39): the mark between
thousands on every numeric block (`group_separator`), the census of
marks between a moment's day and its time of day
(`datetime_separators`), and whether every moment stood at midnight
(`all_at_midnight`). The twin honours all three, and until these lines
the summary beside the description said none of them -- the gap
residual R-P4-26 closed for the width censuses: a published census a
person can learn of only by opening the JSON.

Each test runs `synthtwin profile` in this process, the way
`test_stage2_spellings_survive` does, reads the summary it wrote, and
requires the line where the fact is published and its absence where it
is not. Every expected count is read back from the description written
beside the summary, so the page and the record are held to one answer.

Every table here is built by seeded neutral code at runtime (plan D13);
no committed data file is read.
"""

import datetime
import json
import pathlib
import random
import sys

from synthtwin import summary
from tests import fixtures


def _run(argv: "list[str]") -> None:
    """Run one synthtwin command in this process and require success."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        if stop.code not in (None, 0):
            raise AssertionError(f"{argv} exited {stop.code}") from stop
    finally:
        sys.argv = before
    if code != 0:
        raise AssertionError(f"{argv} returned {code}")


def _profile_of(
    folder: pathlib.Path,
    name: str,
    header: "list[str]",
    rows: "list[list[str]]",
    extra: "list[str]",
) -> "tuple[str, dict[str, object]]":
    """Describe a table; return the summary text and the description."""
    table = folder / f"{name}.csv"
    # `newline=""`: the bytes on disk are the bytes composed here, on
    # every platform, which is what the line-ending guard requires.
    table.write_text(
        fixtures.rows_to_csv(header, rows), encoding="utf-8", newline=""
    )
    _run(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
        + extra
    )
    page = (folder / f"{name}-profile.txt").read_text(encoding="utf-8")
    document = json.loads(
        (folder / f"{name}-profile.json").read_text(encoding="utf-8")
    )
    return page, document


def _block_of(page: str, name: str) -> "list[str]":
    """The lines of one column's block on the summary page.

    A block opens with the column's name indented two spaces and ends
    at the first blank line, which is how `summary.render` writes it.
    """
    lines = page.split("\n")
    start = lines.index("COLUMNS, ONE BY ONE")
    for place in range(start, len(lines)):
        if lines[place] == f"  {name}":
            block: "list[str]" = []
            for line in lines[place + 1 :]:
                if not line:
                    return block
                block.append(line)
            return block
    raise AssertionError(f"the summary has no block for the column {name!r}")


def _column(document: "dict[str, object]", name: str) -> "dict[str, object]":
    """The description's block for one column, by name."""
    columns = document["columns"]
    assert isinstance(columns, list)
    for column in columns:
        if column["name"] == name:
            return column
    raise AssertionError(f"the description has no column {name!r}")


def _charges(count: int, seed: int) -> "list[str]":
    """Costs written with a comma between thousands, like 2,198.92."""
    draw = random.Random(seed)
    return [
        f"{round(2.718281828 ** (6.4 + draw.gauss(0, 1.0)), 2):,.2f}"
        for _ in range(count)
    ]


def _stamps(count: int, seed: int, marks: str) -> "list[str]":
    """Moments off the minute, each written with the mark its place picks."""
    draw = random.Random(seed)
    start = datetime.datetime(2025, 3, 1, 0, 7)
    written = []
    for place in range(count):
        moment = start + datetime.timedelta(
            minutes=draw.randrange(0, 400000)
        )
        # Never on the hour and minute zero, so no stamp is at midnight.
        moment = moment.replace(minute=moment.minute % 50 + 7)
        mark = marks[place % len(marks)]
        written.append(
            moment.strftime("%Y-%m-%d") + mark + moment.strftime("%H:%M:%S")
        )
    return written


def _dates_at_midnight(count: int, seed: int) -> "list[str]":
    """A date-only field, held as the date plus 00:00:00."""
    draw = random.Random(seed)
    start = datetime.date(2025, 3, 1)
    return [
        (start + datetime.timedelta(days=draw.randrange(0, 300))).isoformat()
        + " 00:00:00"
        for _ in range(count)
    ]


_GROUP_COMMA = (
    "    numbers written with ',' between the thousands, and the twin "
    "writes ',' between the thousands too"
)
_GROUP_POINT = (
    "    numbers written with '.' between the thousands, and the twin "
    "writes '.' between the thousands too"
)
_MIDNIGHT = (
    "    every value stood exactly at midnight, so this column holds "
    "dates, and the twin keeps every value at midnight too"
)
_SEPARATOR_OPENING = "    between the day and the time of day, written with: "


def test_a_comma_grouped_column_is_said_to_be_grouped(
    tmp_path: pathlib.Path,
) -> None:
    """A column of `2,198.92` says its mark, and the twin's, in words."""
    charges = _charges(400, 31)
    assert sum(1 for charge in charges if "," in charge) > 100
    page, document = _profile_of(
        tmp_path, "charges", ["charge"], [[one] for one in charges], []
    )
    assert _column(document, "charge")["group_separator"] == ","
    block = _block_of(page, "charge")
    assert _GROUP_COMMA in block, (
        "the description publishes ',' as this column's mark between "
        "thousands and the summary does not say so:\n" + "\n".join(block)
    )
    assert _GROUP_POINT not in block


def test_a_point_grouped_decimal_comma_column_is_said_to_be_grouped(
    tmp_path: pathlib.Path,
) -> None:
    """Under --decimal-comma, `42.037,34` is said as grouped with '.'."""
    swapped = []
    for charge in _charges(400, 32):
        text = ""
        for letter in charge:
            text = text + {",": ".", ".": ","}.get(letter, letter)
        swapped.append(text)
    page, document = _profile_of(
        tmp_path,
        "euro",
        ["amount"],
        [[one] for one in swapped],
        ["--decimal-comma", "amount"],
    )
    assert _column(document, "amount")["group_separator"] == "."
    block = _block_of(page, "amount")
    assert _GROUP_POINT in block, "\n".join(block)
    assert _GROUP_COMMA not in block


def test_a_space_stamped_column_names_its_mark_and_count(
    tmp_path: pathlib.Path,
) -> None:
    """Moments written `2025-09-04 06:16:00` say 'a space' with the count."""
    stamps = _stamps(400, 33, " ")
    page, document = _profile_of(
        tmp_path, "stamps", ["seen_at"], [[one] for one in stamps], []
    )
    column = _column(document, "seen_at")
    assert column["datetime_separators"] == {"space": 400}
    assert column["all_at_midnight"] is False
    block = _block_of(page, "seen_at")
    assert _SEPARATOR_OPENING + "a space in 400 value(s)" in block, (
        "the description publishes 400 moments written with a space and "
        "the summary does not say so:\n" + "\n".join(block)
    )
    assert _MIDNIGHT not in block


def test_marks_too_rare_to_name_are_said_as_a_count_and_never_as_a_mark(
    tmp_path: pathlib.Path,
) -> None:
    """The pooled `(withheld)` entry is a count of values, not a mark.

    Three hundred and eighty stamps with a space, ten with a `T` and ten
    with a `t`, under a smallest group of fifteen: the space is named,
    the capital T is named nowhere, and twenty values are said to wear
    a mark too rare to name.
    """
    marks = " " * 38 + "T" + "t"
    stamps = _stamps(400, 34, marks)
    page, document = _profile_of(
        tmp_path,
        "pooled",
        ["seen_at"],
        [[one] for one in stamps],
        ["--smallest-group", "15"],
    )
    assert _column(document, "seen_at")["datetime_separators"] == {
        "(withheld)": 20,
        "space": 380,
    }
    block = _block_of(page, "seen_at")
    expected = (
        _SEPARATOR_OPENING
        + "a space in 380 value(s), 20 value(s) whose mark was too rare "
        "to name here, because fewer than 15 value(s) were written with "
        "each such mark"
    )
    assert expected in block, "\n".join(block)
    said = "\n".join(block)
    assert "capital T" not in said
    assert "lower-case t" not in said
    assert "(withheld)" not in said


def test_every_mark_is_named_in_words_with_its_count(
    tmp_path: pathlib.Path,
) -> None:
    """A space, a capital T and a lower-case t, each with its own count."""
    stamps = _stamps(400, 35, "  Tt")
    page, document = _profile_of(
        tmp_path, "marks", ["seen_at"], [[one] for one in stamps], []
    )
    assert _column(document, "seen_at")["datetime_separators"] == {
        "lower_t": 100,
        "space": 200,
        "upper_t": 100,
    }
    block = _block_of(page, "seen_at")
    expected = (
        _SEPARATOR_OPENING
        + "a space in 200 value(s), a capital T in 100 value(s), a "
        "lower-case t in 100 value(s)"
    )
    assert expected in block, "\n".join(block)


def test_an_all_midnight_column_is_said_to_hold_dates(
    tmp_path: pathlib.Path,
) -> None:
    """Dates stored as the date plus 00:00:00 are said to be dates."""
    days = _dates_at_midnight(400, 36)
    page, document = _profile_of(
        tmp_path, "service", ["service_on"], [[one] for one in days], []
    )
    assert _column(document, "service_on")["all_at_midnight"] is True
    block = _block_of(page, "service_on")
    assert _MIDNIGHT in block, (
        "the description publishes that every value stood at midnight "
        "and the summary does not say so:\n" + "\n".join(block)
    )


def test_a_plain_table_says_none_of_the_three(tmp_path: pathlib.Path) -> None:
    """Ungrouped numbers and dates with no time of day earn no new line.

    The empty string and the empty census and `false` are ordinary
    answers, and a line printed for them would train a reader to skip
    the one that matters.
    """
    draw = random.Random(37)
    start = datetime.date(2025, 3, 1)
    rows = [
        [
            f"{draw.randrange(0, 900)}",
            f"{draw.randrange(1000, 90000) / 100:.2f}",
            (start + datetime.timedelta(days=draw.randrange(0, 300)))
            .isoformat(),
        ]
        for _ in range(400)
    ]
    page, document = _profile_of(
        tmp_path, "plain", ["visits", "weight", "seen_on"], rows, []
    )
    for name in ("visits", "weight"):
        assert _column(document, name)["group_separator"] == ""
    seen = _column(document, "seen_on")
    assert seen["datetime_separators"] == {}
    assert seen["all_at_midnight"] is False
    said = page.split("\n")
    assert not [line for line in said if "between the thousands" in line]
    assert not [line for line in said if "between the day and the" in line]
    assert _MIDNIGHT not in said


def test_every_numeric_block_of_a_column_is_asked() -> None:
    """A joined column's parts and a compound column's numbers are read.

    Neither shape reaches the description with grouped numbers from a
    table today, so this asks the summary's own helper about the block
    shapes the contract allows, the way `_empty_bin_lines` is asked:
    the fact sits one step below the column there, and a helper that
    read only the column would say nothing of it.
    """
    joined: "dict[str, object]" = {
        "parts": [
            {"empty_bins": [], "group_separator": ","},
            {"empty_bins": [], "group_separator": ""},
        ]
    }
    assert summary._group_separator_lines(joined) == [
        "    part 1 of each cell: numbers written with ',' between the "
        "thousands, and the twin writes ',' between the thousands too"
    ]
    compound: "dict[str, object]" = {
        "numbers": {"empty_bins": [], "group_separator": "."},
        "labels": {"levels": []},
    }
    assert summary._group_separator_lines(compound) == [
        "    its numbers: numbers written with '.' between the "
        "thousands, and the twin writes '.' between the thousands too"
    ]
    assert summary._group_separator_lines(
        {"empty_bins": [], "group_separator": ""}
    ) == []

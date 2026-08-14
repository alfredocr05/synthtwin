"""The walk before the reader reads what the reader reads (V9, V1.5).

REVIEW ITEM P3-V3-F6. `synthtwin validate` settles two questions before
it calls the shipped reader -- whether the file's first row can name a
table's columns, and whether the file holds any rows at all -- and it
settles them with a CSV walk of its own. That walk stands in for the
reader, so anywhere the two can disagree is a defect, and one place they
did was the field size limit: the reader raises the module-wide limit to
its own published ceiling for the length of its pass, and the walk ran
under whatever the interpreter's default happened to be. A strict-valid
description of eleven values one character longer than that default
generates a conforming twin; the reader read every row of it; the walk
parsed the header and stopped; `_holds_no_data` believed the truncated
list, and the conforming twin got a whole report of MISSED verdicts
without the reader ever being asked.

WHAT THE CLASS IS. Not "131,072". The walk is a second reading of the
same bytes, and the shipped reader is the one the description was made
with, so the property is: **wherever the reader gets a reading, the walk
gets the same one; and wherever the reader refuses, the walk does not
hand back a reading that a report could be built on.** Both directions
are asserted here, and the boundaries the two readings can differ at are
crossed rather than approached -- the catalogue's own long-field file is
two hundred characters, which is why nothing saw this.

THE LIMIT IS ONE CONSTANT, NOT TWO EQUAL ONES. `reading.FIELD_SIZE_LIMIT`
is what the walk sets, so the test that proves it is a test that MOVES
that constant and finds both readings moving together. It is also how
the far side of the limit is reached without writing a ten-megabyte
file: the code path is identical at any limit.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import csv
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814

# One character past the field size limit a Python interpreter starts
# with. Written as the sum so that a reader can see which side of the
# line the fixture sits on.
DEFAULT_LIMIT = 131_072
PAST_THE_DEFAULT = DEFAULT_LIMIT + 1


def _described(
    folder: pathlib.Path, text: str, stem: str
) -> contract.Profile:
    """One table through the real producer and the strict loader."""
    table_path = folder / f"{stem}.csv"
    table_path.write_text(text, encoding="utf-8", newline="")
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_NAMES
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _long_value_table(length: int, rows: int = 11) -> str:
    """A one-column table whose every value is ``length`` characters.

    One repeated value, which is the finding's own fixture: a constant
    column publishes its single value and the generator writes it back,
    so the twin is conforming by construction and the run is about the
    READING and not about what a long column is worth describing.
    """
    return fixtures.single_column_table("note", ["x" * length] * rows)


def test_a_conforming_twin_of_long_values_is_read_and_not_refused(
    tmp_path: pathlib.Path,
) -> None:
    """THE FINDING'S OWN WITNESS: the twin, measured against its profile.

    Eleven values one character past the interpreter's default limit.
    The description is strict-valid, the generator writes a conforming
    twin, and the shipped reader reads it -- so a report of MISSED
    verdicts about it is a report about a file nobody looked at.
    """
    folder = tmp_path / "long"
    folder.mkdir()
    described = _described(
        folder, _long_value_table(PAST_THE_DEFAULT), "long"
    )
    twin = rendering.twin_csv(generation.generate(described, SEED))
    target = folder / "twin.csv"
    target.write_text(twin, encoding="utf-8", newline="")
    outcome = validation.measure(described, str(target))
    assert outcome.census.missed == 0, sorted(
        {
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        }
    )
    assert outcome.census.withheld == 0
    assert outcome.census.held > 0


def test_the_walk_and_the_reader_agree_about_whether_a_file_has_rows(
    tmp_path: pathlib.Path,
) -> None:
    """The class, in the direction the finding was found in.

    `_holds_no_data` is what routes a file to the whole-report-of-MISSES
    exit, and it may say yes only about a file the reader would also
    read no rows from. The battery crosses the field limit in a value,
    in a name, inside quotes and beside a quoted line break, because a
    limit is counted over the parsed field and the four are not the same
    number of characters.
    """
    folder = tmp_path / "rows"
    folder.mkdir()
    long = "x" * PAST_THE_DEFAULT
    files = {
        "ordinary": "a,b\n1,2\n",
        "header-only": "a,b\n",
        "long-value": f"a,b\n{long},2\n",
        "long-value-quoted": f'a,b\n"{long}",2\n',
        "long-name": f"{long},b\n1,2\n",
        "long-with-a-break": f'a,b\n"{long}\ny",2\n',
        "long-and-blank-lines": f"a,b\n\n{long},2\n\n",
    }
    for label in sorted(files):
        target = folder / f"{label}.csv"
        target.write_text(files[label], encoding="utf-8", newline="")
        as_read = validation._read_utf8(target)
        assert as_read is not None, label
        theirs = 0
        try:
            theirs = reading.read_table(
                str(target), first_row=reading.FIRST_ROW_NAMES
            ).n_rows
        except errors.ProfileError:
            theirs = -1
        mine = validation._holds_no_data(as_read, True)
        if theirs > 0:
            assert not mine, (
                f"{label}: the reader reads {theirs} rows and the walk "
                f"before it calls the file empty, so the report is built "
                f"without the reader"
            )
        if theirs == 0:
            assert mine, label


def test_a_file_the_reader_refuses_is_refused_and_not_reported(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The class in the other direction, at the far side of the limit.

    A field longer than the reader's own ceiling stops both readings.
    The walk must not hand back the records it managed and let a report
    be built on them: a file nobody could read is a catalogued REFUSAL
    (V9), and the refusal names positions and never values, because on
    this path the file may not be the person's own table.

    The ceiling is MOVED rather than reached, which is what proves the
    walk reads the reader's own constant instead of a copy of its value:
    one assignment moves both readings, and the same code runs at any
    limit.
    """
    folder = tmp_path / "beyond"
    folder.mkdir()
    described = _described(folder, _long_value_table(400), "short")
    monkeypatch.setattr(reading, "FIELD_SIZE_LIMIT", 500)
    target = folder / "huge.csv"
    target.write_text(
        fixtures.single_column_table("note", ["y" * 900] * 11),
        encoding="utf-8",
        newline="",
    )
    with pytest.raises(errors.ProfileError) as refusal:
        reading.read_table(str(target), first_row=reading.FIRST_ROW_NAMES)
    assert "500" in f"{refusal.value}"
    as_read = validation._read_utf8(target)
    assert as_read is not None
    walked, whole = validation._walked(as_read)
    assert not whole, (
        "the walk says it read the whole file, and the reader cannot "
        "read it at all"
    )
    assert not validation._holds_no_data(as_read, True), (
        "a file the walk could not finish is being called a file with "
        "no rows, which is a verdict about a file nobody read"
    )
    with pytest.raises(errors.ProfileError) as raised:
        validation.measure(described, str(target))
    spoken = f"{raised.value}"
    assert "y" * 20 not in spoken, "the refusal quotes the measured file"
    assert walked is not None


def test_moving_the_readers_limit_moves_the_walk_with_it(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """One constant, read by both, proved by moving it.

    Two equal numbers written in two places are two numbers, and the
    next edit moves one of them. This asserts the walk reads the
    reader's own name: at a limit of 500 a 900-character field stops the
    walk, and at the reader's own ceiling the same field goes straight
    through.
    """
    folder = tmp_path / "moved"
    folder.mkdir()
    target = folder / "wide.csv"
    target.write_text(
        fixtures.single_column_table("note", ["y" * 900] * 4),
        encoding="utf-8",
        newline="",
    )
    as_read = validation._read_utf8(target)
    assert as_read is not None
    _records, whole = validation._walked(as_read)
    assert whole
    monkeypatch.setattr(reading, "FIELD_SIZE_LIMIT", 500)
    _records, narrowed = validation._walked(as_read)
    assert not narrowed


def test_the_walk_puts_the_module_wide_limit_back(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The limit belongs to the `csv` module and not to this walk.

    It is one setting for every reader in the process, so a walk that
    left it raised would change what some other caller can parse, and a
    walk that left it raised only when it FAILED would do it exactly on
    the files nobody expects. Both exits are checked.
    """
    folder = tmp_path / "restore"
    folder.mkdir()
    before = csv.field_size_limit()
    validation._walked("a,b\n1,2\n")
    assert csv.field_size_limit() == before
    monkeypatch.setattr(reading, "FIELD_SIZE_LIMIT", 500)
    _records, whole = validation._walked("a,b\n" + "y" * 900 + ",2\n")
    assert not whole
    assert csv.field_size_limit() == before

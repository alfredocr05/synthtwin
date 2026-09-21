"""A workbook's date cells are described as dates, and written back as dates.

THE DEFECT, AS MEASURED (repair of the stage-2b integration). A workbook
stores a date as a day count wearing a date format, and the reader
handed the count on as a number. A `dd.mm.yyyy` column of a 2,000-row
administrative extract was described as role `count` with percentiles
44937 to 45579, its datetime column as `continuous`, and the twin --
drawn as continuous numbers -- lost 110 of 1394 moments at midnight and missed
five facts at exit 3; a 5,000-row clinical book lost 151 of 3020.
Generating that twin took 75 seconds against 1.4 for the same table as
CSV, spent on fraction widths of ten and more places the day counts
wore. Stage 2 promises a date stored at midnight stays at midnight.

What is held here: the reader against openpyxl as an independent
oracle; a real round trip keeping every midnight and validating at exit
0 on both files; the generation time of a workbook against the same
table as delimited text; and the writer's two new rules against the
method oracle, value for value, over seeded random inputs.
"""

import contextlib
import datetime
import importlib.util
import io
import json
import pathlib
import random
import sys
import time

import pytest

from synthtwin import dialect, sheetwriting
from tests import crosscheck

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
ORACLE = REPOSITORY / "tools" / "reference" / "make_generation_reference_vectors.py"


def _oracle():
    spec = importlib.util.spec_from_file_location("oracle_workbook_dates", ORACLE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _exit_of(argv: "list[str]") -> int:
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _missed(folder: pathlib.Path) -> "list[str]":
    lines: "list[str]" = []
    for report in sorted(folder.glob("*.txt")):
        for line in report.read_text(encoding="utf-8").splitlines():
            if line.rstrip().endswith("MISSED"):
                lines += [line.strip()]
    return lines


def _extract(n_rows: int, seed: int, epoch_1904: bool = False) -> bytes:
    """A seeded extract: a day column, a moment column mostly at midnight, an amount."""
    openpyxl = crosscheck.reader()
    draw = random.Random(seed)
    book = openpyxl.Workbook()
    if epoch_1904:
        book.epoch = openpyxl.utils.datetime.CALENDAR_MAC_1904
    sheet = book.active
    sheet.append(["service_date", "paid_at", "amount"])
    for row in range(2, n_rows + 2):
        day = datetime.date(2024, 1, 1) + datetime.timedelta(
            days=draw.randrange(366)
        )
        moment = datetime.datetime.combine(day, datetime.time(0, 0))
        if draw.random() >= 0.7:
            moment = moment.replace(
                hour=draw.randrange(7, 19), minute=draw.randrange(60)
            )
        sheet.cell(row=row, column=1, value=day).number_format = "dd.mm.yyyy"
        sheet.cell(row=row, column=2, value=moment).number_format = (
            "yyyy-mm-dd hh:mm"
        )
        sheet.cell(row=row, column=3, value=round(draw.gauss(80, 12), 1))
    held = io.BytesIO()
    book.save(held)
    return held.getvalue()


def _at_midnight(values: "list[object]") -> int:
    return sum(
        1
        for value in values
        if isinstance(value, datetime.datetime)
        and (value.hour, value.minute, value.second) == (0, 0, 0)
    )


@pytest.mark.parametrize("epoch_1904", [False, True])
def test_a_date_column_is_described_as_dates_and_keeps_its_at_midnight(
    tmp_path: pathlib.Path, epoch_1904: bool
) -> None:
    """The measured shape: dates and moments in a workbook, round-tripped."""
    openpyxl = crosscheck.reader()
    source = tmp_path / "extract.xlsx"
    source.write_bytes(_extract(600, 5, epoch_1904))
    assert _exit_of(["profile", str(source), "--out-dir", str(tmp_path)]) == 0
    described = tmp_path / "extract-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    roles = {column["name"]: column["role"] for column in document["columns"]}
    assert roles["service_date"] == "datetime", roles
    assert roles["paid_at"] == "datetime", roles

    # openpyxl, which `src` never imports, agrees about every date read.
    real_sheet = openpyxl.load_workbook(source).worksheets[0]
    real_moments = [cell.value for cell in real_sheet["B"][1:]]
    assert all(isinstance(value, datetime.datetime) for value in real_moments)

    real = tmp_path / "real"
    real.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(source),
                     "--out-dir", str(real)]) == 0, _missed(real)
    assert _exit_of(["generate", str(described), "--out-dir", str(tmp_path),
                     "--seed", "1"]) == 0
    twin = tmp_path / "extract-twin.xlsx"
    checked = tmp_path / "checked"
    checked.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(twin),
                     "--out-dir", str(checked)]) == 0, _missed(checked)

    twin_book = openpyxl.load_workbook(twin)
    assert (twin_book.epoch.year == 1904) is epoch_1904
    twin_sheet = twin_book.worksheets[0]
    twin_days = [cell.value for cell in twin_sheet["A"][1:]]
    twin_moments = [cell.value for cell in twin_sheet["B"][1:]]
    assert all(isinstance(value, datetime.datetime) for value in twin_days)
    assert all(isinstance(value, datetime.datetime) for value in twin_moments)
    assert _at_midnight(twin_moments) == _at_midnight(real_moments)


def test_a_workbook_twin_is_generated_in_the_time_its_delimited_twin_is(
    tmp_path: pathlib.Path,
) -> None:
    """The same table as a workbook and as CSV: generation within a small factor.

    Measured before the repair on a 2,000-row, ten-column extract: 75.0
    seconds for the workbook against 1.4 for the CSV. The bound is loose
    on purpose, a factor of eight plus two seconds, so a slow machine
    does not turn it red; the defect was a factor of fifty.
    """
    openpyxl = crosscheck.reader()
    data = _extract(2000, 9)
    book = tmp_path / "book"
    book.mkdir()
    (book / "extract.xlsx").write_bytes(data)
    flat = tmp_path / "flat"
    flat.mkdir()
    sheet = openpyxl.load_workbook(io.BytesIO(data)).worksheets[0]
    lines = ["service_date,paid_at,amount"]
    for day, moment, amount in sheet.iter_rows(min_row=2, values_only=True):
        lines += [
            f"{day:%Y-%m-%d},{moment:%Y-%m-%d %H:%M:%S},{amount}"
        ]
    (flat / "extract.csv").write_bytes(("\n".join(lines) + "\n").encode("utf-8"))

    spent = {}
    for folder, name in ((book, "extract.xlsx"), (flat, "extract.csv")):
        assert _exit_of(["profile", str(folder / name),
                         "--out-dir", str(folder)]) == 0
        began = time.perf_counter()
        assert _exit_of(["generate", str(folder / "extract-profile.json"),
                         "--out-dir", str(folder), "--seed", "0"]) == 0
        spent[name] = time.perf_counter() - began
    assert spent["extract.xlsx"] <= 8 * spent["extract.csv"] + 2.0, spent


@pytest.mark.parametrize("epoch_1904", [False, True])
def test_a_day_count_and_its_date_are_one_reading_both_ways(
    epoch_1904: bool,
) -> None:
    """The reader's date and the writer's day count, against `datetime`."""
    base = datetime.datetime(1904, 1, 1) if epoch_1904 else datetime.datetime(
        1899, 12, 30
    )
    draw = random.Random(3)
    for _step in range(4000):
        days = draw.randrange(0 if epoch_1904 else 61, 2_900_000)
        milliseconds = draw.choice(
            [0, draw.randrange(86_400) * 1000, draw.randrange(86_400_000)]
        )
        stored = f"{days}" if milliseconds == 0 else repr(
            days + milliseconds / 86_400_000
        )
        moment = base + datetime.timedelta(days=days, milliseconds=milliseconds)
        read = dialect.sheet_serial_moment(stored, "datetime", epoch_1904)
        wanted = moment.strftime("%Y-%m-%d %H:%M:%S")
        if milliseconds % 1000:
            wanted = f"{wanted}.{milliseconds % 1000:03d}"
        assert read == wanted, stored
        assert dialect.sheet_serial_moment(
            dialect.sheet_moment_serial(read, epoch_1904), "datetime", epoch_1904
        ) == read
    # The 1900 system's day that never was, and its two neighbours.
    assert dialect.sheet_serial_moment("59", "date", False) == "1900-02-28"
    assert dialect.sheet_serial_moment("60", "date", False) == "60"
    assert dialect.sheet_serial_moment("61", "date", False) == "1900-03-01"
    assert dialect.sheet_moment_serial("1900-02-28", False) == "59"
    assert dialect.sheet_moment_serial("1900-03-01", False) == "61"
    # A time is a length of time and stays a number.
    assert dialect.sheet_serial_moment("0.5", "time", False) == "0.5"


def test_the_writer_and_the_method_oracle_agree_on_every_date_rule() -> None:
    """G2.2 steps 0 and 2, value for value, over seeded random columns."""
    oracle = _oracle()
    draw = random.Random(11)
    kinds = ("plain", "date", "datetime", "time", "elapsed", "text")
    for _step in range(3000):
        size = draw.randrange(1, 12)
        classes = tuple(
            draw.choice(("absent", "number", "text", "blank"))
            for _cell in range(size)
        )
        dated = tuple(draw.choice(("", "date", "datetime")) for _cell in range(size))
        census = {
            kind: draw.choice((None, 0, draw.randrange(size + 1)))
            for kind in kinds
        }
        assert list(
            sheetwriting.cell_format_kinds(census, classes, dated=dated)
        ) == oracle.sheet_format_kinds(census, list(classes), dated=list(dated)), (
            census, classes, dated,
        )
    for _step in range(3000):
        epoch_1904 = draw.random() < 0.5
        year = draw.choice((1899, 1900, 1903, 1904, 1905, 2024, 9999, 10000))
        text = f"{year:04d}-{draw.randrange(0, 14):02d}-{draw.randrange(0, 33):02d}"
        if draw.random() < 0.5:
            text = (
                f"{text} {draw.randrange(25):02d}:{draw.randrange(61):02d}"
                f":{draw.randrange(61):02d}"
            )
            if draw.random() < 0.3:
                text = f"{text}.{draw.randrange(1000):03d}"
        assert dialect.sheet_moment_serial(text, epoch_1904) == (
            oracle.sheet_day_count(text, epoch_1904)
        ), (text, epoch_1904)
        if dialect.sheet_moment_serial(text, epoch_1904):
            assert dialect.sheet_moment_kind(text) == oracle.sheet_date_kind(text)

"""Workbook cells read as what they store: dates, moments and clocks (plan P4-D382).

THE DEFECTS, AS MEASURED (the reach audit of 2026-10-01 and its
skeptic's W1 and N1, on 1,000 made-up cells at the floor of eleven):

* a column of dates a workbook STORES as dates, beside 5 % of the same
  dates typed in as text or 3 % of the word `UNK`, fell to free text or
  a long tail of labels; its twin was 1,000 strings such as `9147-54-59`
  and `synthtwin validate` exited 3 on the twin of the person's own
  table;
* moments wearing a date-only format, under 1 % of them at midnight,
  had those cells read as bare dates, counted unparsed and written
  as text: exit 3 again -- and that is the commonest moment column;
* a date beside a date with a time, or two date codes, in one column
  refused the WHOLE TABLE, with a message about decimal places;
* a column of clock times wearing a time format was read as continuous
  numbers -- a twin carrying seconds and microseconds its source never
  held, ten cells past one day read back as date-times, and with seconds
  stored a RecursionError and no description at all;
* a locale-tagged code (`[$-409]...`) was published as the canonical
  code of its kind, so the twin dressed every cell differently;
* the cell cap told a person with a table of a million rows to delete
  rows, where saving it as a .csv file is the route past it.

Each test below runs the commands a person runs -- profile, generate,
validate the twin AND the real workbook -- and reads the twin back with
openpyxl, which `src/synthtwin` never imports. The witnesses at the
foot withdraw each new rule and show the measured defect come back, so
no test here is one that cannot fail.

Every workbook is built by neutral code at runtime from made-up values
(plan D13).
"""

import collections
import contextlib
import datetime
import io
import json
import pathlib
import random
import sys

import pytest

from synthtwin import dialect, errors, sheetwriting, taxonomy, workbook
from tests import crosscheck
from tests.test_workbook_dates import _oracle

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
ROWS = 1000


def _exit_of(argv: "list[str]") -> "tuple[int, str]":
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main()
    except SystemExit as stop:
        code = 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code, said.getvalue()


def _day(draw: random.Random) -> datetime.datetime:
    return datetime.datetime(2021, 1, 1) + datetime.timedelta(
        days=draw.randrange(1461)
    )


def _moment(draw: random.Random) -> datetime.datetime:
    return _day(draw).replace(
        hour=draw.randrange(24), minute=draw.randrange(60),
        second=draw.randrange(60),
    )


def _book(cells: "list[tuple[object, str]]") -> bytes:
    """One sheet, one column `event_at`, each cell a (value, format code)."""
    openpyxl = crosscheck.fixture_writer()
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Data"
    sheet.cell(row=1, column=1, value="event_at")
    for row, (value, code) in enumerate(cells, start=2):
        cell = sheet.cell(row=row, column=1, value=value)
        cell.number_format = code
    held = io.BytesIO()
    book.save(held)
    return held.getvalue()


def _trip(
    folder: pathlib.Path, cells: "list[tuple[object, str]]",
    extra: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Describe, generate, validate both files; hand back what each said."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "table.xlsx"
    table.write_bytes(_book(cells))
    code, said = _exit_of(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace", *extra]
    )
    assert code == 0, said[-600:]
    described = folder / "table-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    code, said = _exit_of(
        ["generate", f"{described}", "--out-dir", f"{folder}", "--replace",
         "--seed", "0"]
    )
    assert code == 0, said[-600:]
    twin = folder / "table-twin.xlsx"
    exits = []
    for checked in (twin, table):
        out = folder / f"check-{checked.stem}"
        out.mkdir()
        code, _said = _exit_of(
            ["validate", f"{described}", "--twin", f"{checked}",
             "--out-dir", f"{out}", "--replace"]
        )
        exits += [code]
    return {
        "column": document["columns"][0],
        "workbook": document["source"]["workbook"]["columns"][0],
        "twin": twin,
        "twin_exit": exits[0],
        "real_exit": exits[1],
    }


def _cells_read(path: pathlib.Path) -> "list[tuple[object, str]]":
    """Every value cell of the first column as openpyxl reads it."""
    sheet = crosscheck.reader().load_workbook(path).worksheets[0]
    out: "list[tuple[object, str]]" = []
    for row in sheet.iter_rows(min_row=2, max_col=1):
        if row[0].value is not None:
            out += [(row[0].value, row[0].number_format)]
    return out


# -- 1. dates stored as dates, beside a few text cells -------------------


def _dates_beside(draw: random.Random, every: int, text: str) -> "list[tuple[object, str]]":
    out: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        day = _day(draw)
        if index % every == 0:
            spelled = day.strftime("%m/%d/%Y") if text == "dates" else "UNK"
            out += [(spelled, "@" if text == "dates" else "General")]
            continue
        out += [(day, "mm-dd-yy")]
    return out


@pytest.mark.parametrize(
    ("every", "text", "texts"), ((20, "dates", 50), (33, "UNK", 31))
)
def test_dates_stored_as_dates_are_read_beside_a_few_text_cells(
    every: int, text: str, texts: int, tmp_path: pathlib.Path
) -> None:
    """5 % of text dates, or 3 % of `UNK`: the column is dates, the text unparsed."""
    trip = _trip(tmp_path, _dates_beside(random.Random(every), every, text))
    column = trip["column"]
    assert column["role"] == "datetime"
    assert column["format"] == "iso-date"
    assert column["n_unparsed"] == texts
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    # LAST: the independent reader. The stored dates come back as dates
    # wearing the source's code, the text cells as text.
    read = _cells_read(trip["twin"])
    dates = [one for one in read if isinstance(one[0], datetime.datetime)]
    strings = [one for one in read if isinstance(one[0], str)]
    assert len(dates) == ROWS - texts
    assert {code for _value, code in dates} == {"mm-dd-yy"}
    assert len(strings) == texts


def test_a_word_named_missing_is_written_back_as_that_word(
    tmp_path: pathlib.Path,
) -> None:
    """`--missing-value UNK`: the 31 cells are missing, and the twin writes `UNK`."""
    trip = _trip(
        tmp_path, _dates_beside(random.Random(33), 33, "UNK"),
        ("--missing-value", "UNK"),
    )
    assert trip["column"]["n_missing"] == 31
    assert trip["column"]["n_unparsed"] == 0
    assert trip["twin_exit"] == 0
    words = [one for one in _cells_read(trip["twin"]) if one[0] == "UNK"]
    assert len(words) == 31


def test_only_a_column_stored_mostly_as_dates_is_read_this_way() -> None:
    """The line is MORE than half the value cells; half is not enough."""
    def column(dated: int, other: int) -> bool:
        texts = ["2024-03-17"] * dated + ["note"] * other + [""]
        classes = ["number"] * dated + ["text"] * other + ["absent"]
        codes = ["mm-dd-yy"] * dated + ["General"] * other + ["General"]
        return workbook.stored_as_dates(texts, classes, codes)

    assert column(51, 49)
    assert not column(50, 50)
    assert not column(0, 0)
    # A number wearing a date format that no date could be read from --
    # a negative stored under a date code -- is not a stored date.
    assert not workbook.stored_as_dates(
        ["-5", "-6", "2024-03-17"], ["number"] * 3, ["mm-dd-yy"] * 3
    )
    # AND THE READING ITSELF asks more than half the PRESENT cells to
    # read under one ISO reading, whatever the storage said: two dates
    # among three notes are no reading.
    assert taxonomy._stored_date_format(
        ["note"] * 3 + ["2024-03-17"] * 2, taxonomy.Settings()
    ) is None
    assert taxonomy._stored_date_format(
        ["note"] * 2 + ["2024-03-17"] * 3, taxonomy.Settings()
    ) is not None


def test_a_column_mostly_text_keeps_the_reading_it_had(
    tmp_path: pathlib.Path,
) -> None:
    """40 % stored dates beside notes: still free text, as before."""
    draw = random.Random(40)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        if index % 5 < 2:
            cells += [(_day(draw), "mm-dd-yy")]
            continue
        cells += [(f"note {draw.randrange(10 ** 6)}", "General")]
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book(cells))
    code, said = _exit_of(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]
    )
    assert code == 0, said[-400:]
    document = json.loads(
        (tmp_path / "table-profile.json").read_text(encoding="utf-8")
    )
    assert document["columns"][0]["role"] == "free_text"


# -- 2. a date format that hides a time ----------------------------------


def test_a_date_format_hiding_a_time_reads_every_cell_as_a_moment(
    tmp_path: pathlib.Path,
) -> None:
    """1,000 moments wearing `m/d/yyyy`, six at midnight: none unparsed."""
    draw = random.Random(6)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        moment = _moment(draw)
        if index % 167 == 0:
            moment = moment.replace(hour=0, minute=0, second=0)
        cells += [(moment, "m/d/yyyy")]
    trip = _trip(tmp_path, cells)
    column = trip["column"]
    assert column["role"] == "datetime"
    assert column["format"] == "iso-datetime"
    assert column["n_unparsed"] == 0
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    read = _cells_read(trip["twin"])
    assert len(read) == ROWS
    assert all(isinstance(value, datetime.datetime) for value, _code in read)
    assert {code for _value, code in read} == {"m/d/yyyy"}


def test_whole_days_under_a_date_format_stay_dates(tmp_path: pathlib.Path) -> None:
    """The control: a date format over whole days reads as dates, as it did."""
    draw = random.Random(7)
    trip = _trip(tmp_path, [(_day(draw), "m/d/yyyy") for _row in range(ROWS)])
    assert trip["column"]["format"] == "iso-date"
    assert trip["twin_exit"] == 0


def test_days_beside_a_few_timed_cells_stay_days(tmp_path: pathlib.Path) -> None:
    """995 weekday dates and 5 timed cells under `m/d/yyyy`: still dates.

    Measured with the column respelled as moments wherever one cell held
    a time: no weekday census, and a twin at midnight 0.009 of the time
    and on a weekend 0.282 of it, against the source's 0.995 and 0.0;
    and with the 5 left unparsed: a twin of 5 text cells, `validate`
    exit 3, and pandas reading the twin's column as text.
    """
    draw = random.Random(11)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        day = _day(draw)
        while day.weekday() >= 5:
            day = _day(draw)
        if index % 200 == 0:
            day = day.replace(hour=9, minute=30)
        cells += [(day, "m/d/yyyy")]
    trip = _trip(tmp_path, cells)
    column = trip["column"]
    assert column["format"] == "iso-date"
    assert column["n_unparsed"] == 0
    assert column["weekday_census"]
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    assert all(
        isinstance(value, datetime.datetime)
        for value, _code in _cells_read(trip["twin"])
    )


@pytest.mark.parametrize(("timed", "form"), ((10, "iso-date"), (11, "iso-datetime")))
def test_one_timed_cell_in_a_hundred_is_the_line_between_days_and_moments(
    timed: int, form: str, tmp_path: pathlib.Path
) -> None:
    """10 timed cells of 1,000 read as days, 11 as moments; both twins pass.

    Measured with the line at "as many timed cells as whole days": from
    11 to 499 timed cells the column was read jointly as `iso-mixed`,
    and at 40 and 50 the twin wrote 10 text cells and `validate` exited
    3. The line is one dated cell in a hundred, the default parse line
    of 0.99 read as cells.
    """
    assert workbook.DAYS_PER_TIMED_CELL == round(
        taxonomy.Settings().minimum_parse_rate
        / (1 - taxonomy.Settings().minimum_parse_rate)
    )
    draw = random.Random(timed)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        day = _day(draw)
        if index < timed:
            day = day.replace(hour=9, minute=30)
        cells += [(day, "m/d/yyyy")]
    trip = _trip(tmp_path, cells)
    column = trip["column"]
    assert column["format"] == form
    assert column["n_unparsed"] == 0
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    assert all(
        isinstance(value, datetime.datetime)
        for value, _code in _cells_read(trip["twin"])
    )


# -- 3. two date formats in one column ----------------------------------


def test_dates_beside_dates_with_a_time_are_read_jointly(
    tmp_path: pathlib.Path,
) -> None:
    """Half `m/d/yyyy` whole days, half `m/d/yyyy h:mm` moments: read, not refused."""
    draw = random.Random(8)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        moment = _moment(draw).replace(second=0)
        if index % 2:
            cells += [(moment.replace(hour=0, minute=0), "m/d/yyyy")]
            continue
        cells += [(moment, "m/d/yyyy h:mm")]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["format"] == "iso-mixed"
    kinds = trip["workbook"]["format_kinds"]
    assert (kinds["date"], kinds["datetime"]) == (500, 500)
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    read = _cells_read(trip["twin"])
    assert all(isinstance(value, datetime.datetime) for value, _code in read)


def test_two_date_codes_are_read_and_the_twin_wears_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """600 `m/d/yyyy` beside 400 `d-mmm-yy`: one column of days, one code."""
    draw = random.Random(9)
    cells = [
        (_day(draw), "m/d/yyyy" if index % 5 < 3 else "d-mmm-yy")
        for index in range(ROWS)
    ]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["format"] == "iso-date"
    assert trip["workbook"]["format_code"] == "m/d/yyyy"
    assert trip["twin_exit"] == 0
    assert {code for _value, code in _cells_read(trip["twin"])} == {"m/d/yyyy"}


@pytest.mark.parametrize(
    ("second", "said"),
    (
        ("clock", "some shown as dates and others as times of day"),
        ("plain", "some shown as plain numbers and others as dates"),
    ),
)
def test_a_mix_still_refused_says_which_kinds_it_holds(
    second: str, said: str, tmp_path: pathlib.Path
) -> None:
    """Dates beside clocks, or beside plain numbers, are refused, truly worded."""
    draw = random.Random(10)
    cells: "list[tuple[object, str]]" = []
    for index in range(200):
        if index % 2:
            cells += [(_day(draw), "m/d/yyyy")]
        elif second == "clock":
            cells += [(datetime.time(draw.randrange(24), draw.randrange(60)), "h:mm")]
        else:
            cells += [(draw.randrange(100, 900), "General")]
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book(cells))
    code, message = _exit_of(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]
    )
    assert code == 1
    assert said in " ".join(message.split())


# -- 4. clocks a workbook stores ------------------------------------------


@pytest.mark.parametrize(
    ("code", "seconds", "form"),
    (
        ("h:mm", False, "hh-mm"),
        ("h:mm", True, "hh-mm-ss"),
        ("h:mm:ss AM/PM", True, "hh-mm-ss"),
        ("[$-409]h:mm AM/PM;@", False, "hh-mm"),
    ),
)
def test_a_clock_column_is_read_as_clocks_keeping_its_seconds(
    code: str, seconds: bool, form: str, tmp_path: pathlib.Path
) -> None:
    """Every stored value under one day: clock times, the stored seconds kept."""
    draw = random.Random(11)
    cells = [
        (
            datetime.time(
                draw.randrange(24), draw.randrange(60),
                draw.randrange(60) if seconds else 0,
            ),
            code,
        )
        for _row in range(ROWS)
    ]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["role"] == "time_of_day"
    assert trip["column"]["clock_form"] == form
    assert trip["workbook"]["format_code"] == code
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    read = _cells_read(trip["twin"])
    assert len(read) == ROWS
    assert all(isinstance(value, datetime.time) for value, _code in read)
    assert {worn for _value, worn in read} == {code}
    assert all(value.microsecond == 0 for value, _code in read)
    if not seconds:
        assert all(value.second == 0 for value, _code in read)


def test_moments_wearing_a_clock_format_stay_numbers(tmp_path: pathlib.Path) -> None:
    """`h:mm` over full date-times reads as it did: their dates are kept."""
    draw = random.Random(12)
    cells = [(_moment(draw).replace(second=0), "h:mm") for _row in range(ROWS)]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["role"] == "continuous"
    assert trip["twin_exit"] == 0


@pytest.mark.parametrize("beside", ("UNK", "fraction"))
def test_a_clock_column_holding_anything_else_stays_as_it_was(
    beside: str, tmp_path: pathlib.Path
) -> None:
    """A word among the clocks, or a clock at a fraction of a second: numbers, as before."""
    draw = random.Random(13)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        clock = datetime.time(draw.randrange(24), draw.randrange(60))
        if index == 7 and beside == "fraction":
            clock = clock.replace(second=5, microsecond=250000)
        if index % 33 == 0 and beside == "UNK":
            cells += [("UNK", "General")]
            continue
        cells += [(clock, "h:mm")]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["role"] != "time_of_day"
    assert trip["twin_exit"] == 0


@pytest.mark.parametrize(
    ("step", "role"), ((15, "time_of_day"), (60, "categorical"))
)
def test_a_clock_grid_keeps_its_levels_only_where_each_can_be_named(
    step: int, role: str, tmp_path: pathlib.Path
) -> None:
    """A quarter-hour grid at 1,000 rows holds levels under the floor: clocks."""
    draw = random.Random(14)
    cells = []
    for _row in range(ROWS):
        slot = draw.randrange(24 * 60 // step) * step
        cells += [(datetime.time(slot // 60, slot % 60), "h:mm")]
    trip = _trip(tmp_path, cells)
    assert trip["column"]["role"] == role
    assert trip["twin_exit"] == 0
    read = _cells_read(trip["twin"])
    assert all(isinstance(value, datetime.time) for value, _code in read)


# -- 5. locale tags, text stored dates, the cell cap ----------------------


@pytest.mark.parametrize(
    "code", ("[$-409]m/d/yyyy h:mm AM/PM;@", "[$-F800]dddd, mmmm dd, yyyy")
)
def test_a_locale_tagged_code_is_published_and_worn(
    code: str, tmp_path: pathlib.Path
) -> None:
    """A locale tag alone is the format language's own; a currency is not."""
    draw = random.Random(15)
    moment = "h:mm" in code
    cells = [
        (_moment(draw).replace(second=0) if moment else _day(draw), code)
        for _row in range(ROWS)
    ]
    trip = _trip(tmp_path, cells)
    assert trip["workbook"]["format_code"] == code
    assert trip["twin_exit"] == 0
    assert {worn for _value, worn in _cells_read(trip["twin"])} == {code}
    assert not dialect.sheet_format_code_speakable("[$USD-409]#,##0.00")
    assert not dialect.sheet_format_code_speakable("[$-409X]m/d/yyyy")
    assert not dialect.sheet_format_code_speakable("[$-123456789]m/d/yyyy")


def test_a_date_stored_as_text_keeps_its_text(tmp_path: pathlib.Path) -> None:
    """950 stored dates beside 50 ISO dates stored as text: the 50 stay dates in text."""
    draw = random.Random(16)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        day = _day(draw)
        if index % 20 == 0:
            cells += [(day.strftime("%Y-%m-%d"), "@")]
            continue
        cells += [(day, "mm-dd-yy")]
    trip = _trip(tmp_path, cells)
    assert trip["twin_exit"] == 0
    texts = [value for value, _code in _cells_read(trip["twin"]) if isinstance(value, str)]
    assert len(texts) == 50
    assert all(dialect.sheet_moment_kind(text) == "date" for text in texts)


def test_the_cell_cap_names_the_route_past_it() -> None:
    """Both refusals say a .csv file is read at any size."""
    for said in (
        errors.workbook_holds_too_many_cells("/data/table.xlsx", 1_000_000),
        errors.workbook_table_spans_too_many_cells("/data/table.xlsx", 1_000_000),
    ):
        assert ".csv file" in said
        assert "any size" in said


def test_the_census_reading_of_stored_dates_is_handed_over(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A one-column workbook of typed dates is read once, not twice.

    Measured with the census reading every column as stored nowhere: its
    reading was never handed over, and `synthtwin profile` of 100,000
    typed dates took 12.7 s of CPU against 8.0 s.
    """
    draw = random.Random(5)
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book([(_day(draw), "m/d/yyyy") for _row in range(ROWS)]))
    calls = [0]
    reading_as_shipped = taxonomy._read_the_column

    def counted(*args: object, **named: object) -> object:
        calls[0] = calls[0] + 1
        return reading_as_shipped(*args, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_read_the_column", counted)
    code, said = _exit_of(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]
    )
    assert code == 0, said[-400:]
    assert calls[0] == 1
    # ...and a reading kept under another storage word is read again.
    values = [f"2024-03-{1 + row % 28:02d}" for row in range(ROWS)]
    held = taxonomy.population_census(
        ["only"], [values], [], taxonomy.Settings()
    )[2][0]
    calls[0] = 0
    taxonomy.profile_column(
        "only", 1, values, ROWS, taxonomy.Settings(), handed_over=held,
        stored_as=taxonomy.STORED_AS_DATES,
    )
    assert calls[0] == 1
    calls[0] = 0
    taxonomy.profile_column(
        "only", 1, values, ROWS, taxonomy.Settings(), handed_over=held
    )
    assert calls[0] == 0


# -- 6. the spellings, and the writer against the method's oracle --------


def test_a_clock_and_the_fraction_a_workbook_stores_are_one_reading() -> None:
    """Every second of the day both ways, and Excel's own stored spellings."""
    for second in range(dialect.SHEET_DAY_SECONDS):
        written = dialect.sheet_clock_text(second, True)
        assert dialect.sheet_serial_second(dialect.sheet_clock_serial(written)) == second
        if second % 60 == 0:
            short = dialect.sheet_clock_text(second, False)
            assert dialect.sheet_clock_serial(short) == dialect.sheet_clock_serial(written)
    # Excel stores 14:05 as seventeen figures; a day or more, a negative
    # and a fraction of a second are no clock.
    assert dialect.sheet_serial_second("0.58680555555555558") == 50_700
    assert dialect.sheet_serial_second("1") == -1
    assert dialect.sheet_serial_second("-0.5") == -1
    assert dialect.sheet_serial_second("0.5000001") == -1
    assert dialect.sheet_clock_serial("24:00") == ""
    assert dialect.sheet_clock_serial("9:05") == ""


def test_the_writer_and_the_method_oracle_agree_on_both_write_backs() -> None:
    """G2.2 steps 0 and 0b, value for value, over seeded random columns."""
    oracle = _oracle()
    draw = random.Random(17)
    classes = ("absent", "blank", "empty", "text", "number", "boolean", "error", "date")
    kinds = ("plain", "date", "datetime", "time", "elapsed", "text")
    from synthtwin import contract

    for _step in range(2000):
        size = draw.randrange(1, 14)
        census = {
            name: draw.choice((None, 0, draw.randrange(size + 1))) for name in classes
        }
        format_kinds = {
            name: draw.choice((None, 0, draw.randrange(size + 1))) for name in kinds
        }
        code = draw.choice(("General", "h:mm", "m/d/yyyy", "@", "[$-409]h:mm AM/PM;@"))
        value_class = draw.choice((None, "number", "text", "date"))
        cells = tuple(
            draw.choice((
                "", f"{draw.randrange(24):02d}:{draw.randrange(60):02d}",
                f"{draw.randrange(25):02d}:{draw.randrange(61):02d}:{draw.randrange(61):02d}",
                f"2024-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
                "UNK", "45369",
            ))
            for _cell in range(size)
        )
        column = contract.WorkbookColumn(
            cell_classes=census, format_code=code, format_kinds=format_kinds,
            formulas=None, value_class=value_class,
        )
        block = {
            "cell_classes": census, "format_code": code,
            "format_kinds": format_kinds, "value_class": value_class,
        }
        assert list(sheetwriting._clocks_as_day_fractions(column, cells)) == (
            oracle.sheet_clocks_as_day_fractions(block, list(cells))
        ), (block, cells)
        mine = sheetwriting._dates_as_day_counts(column, cells, False)
        theirs = oracle.sheet_dates_as_day_counts(block, list(cells), False)
        assert (list(mine[0]), list(mine[1])) == (theirs[0], theirs[1]), (block, cells)


# -- 7. each new rule, withdrawn: the measured defect comes back ---------


def test_each_reading_withdrawn_brings_its_defect_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The witnesses: a rule withdrawn, and the twin of the person's table fails again."""
    # The stored dates beside text cells, read as text again.
    with monkeypatch.context() as patched:
        patched.setattr(workbook, "stored_as_dates", lambda *arguments: False)
        trip = _trip(tmp_path / "dates", _dates_beside(random.Random(20), 20, "dates"))
        assert trip["column"]["role"] != "datetime"
        assert trip["twin_exit"] == 3
    # The cells at midnight a date format hides read as bare dates again.
    draw = random.Random(6)
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        moment = _moment(draw)
        if index % 167 == 0:
            moment = moment.replace(hour=0, minute=0, second=0)
        cells += [(moment, "m/d/yyyy")]
    with monkeypatch.context() as patched:
        patched.setattr(
            workbook, "_read_as_one_column", lambda *arguments: None
        )
        trip = _trip(tmp_path / "at_midnight", cells)
        assert trip["column"]["n_unparsed"] == 6
        assert trip["twin_exit"] == 3
    # The quarter-hour grid held to a list of labels again.
    draw = random.Random(14)
    grid = []
    for _row in range(ROWS):
        slot = draw.randrange(96) * 15
        grid += [(datetime.time(slot // 60, slot % 60), "h:mm")]
    with monkeypatch.context() as patched:
        patched.setattr(
            workbook, "stored_as_clocks", lambda texts, classes, codes: False
        )
        trip = _trip(tmp_path / "grid", grid)
        assert trip["column"]["role"] == "categorical"
        assert trip["twin_exit"] == 3
    # The writer's clocks written as text again.
    with monkeypatch.context() as patched:
        patched.setattr(
            sheetwriting, "_clocks_as_day_fractions", lambda column, own: own
        )
        draw = random.Random(11)
        clocks = [
            (datetime.time(draw.randrange(24), draw.randrange(60)), "h:mm")
            for _row in range(ROWS)
        ]
        trip = _trip(tmp_path / "written", clocks)
        assert trip["twin_exit"] == 3
        kinds = collections.Counter(
            type(value).__name__ for value, _code in _cells_read(trip["twin"])
        )
        assert kinds == {"str": ROWS}


# -- 8. the review of landing R3 ------------------------------------------


def _three_storages(epoch_1904: bool, code: str) -> bytes:
    """220 days: 180 stored as day counts, 20 as `t="d"` cells, 20 as text.

    Every cell wears ``code``; the day counts are counted from the
    workbook's own epoch.
    """
    openpyxl = crosscheck.fixture_writer()
    book = openpyxl.Workbook()
    book.iso_dates = True
    if epoch_1904:
        # openpyxl's own 1904 epoch, spelled here so that only
        # tests/crosscheck.py imports the cross-check reader.
        book.epoch = datetime.datetime(1904, 1, 1)
    sheet = book.active
    sheet.title = "Data"
    sheet.cell(row=1, column=1, value="event_at")
    start = datetime.date(2024, 1, 1)
    epoch = datetime.date(1904, 1, 1) if epoch_1904 else datetime.date(1899, 12, 30)
    for index in range(220):
        day = start + datetime.timedelta(days=index)
        value: object = (day - epoch).days
        if index % 11 == 3:
            value = datetime.datetime.combine(day, datetime.time())
        elif index % 11 == 7:
            value = day.isoformat()
        cell = sheet.cell(row=index + 2, column=1, value=value)
        cell.number_format = code
    held = io.BytesIO()
    book.save(held)
    return held.getvalue()


@pytest.mark.parametrize(
    ("epoch_1904", "code"),
    ((False, "yyyy-mm-dd"), (True, "[$-409]yyyy-mm-dd")),
)
def test_text_dates_keep_their_text_beside_iso_date_cells(
    epoch_1904: bool, code: str, tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Day counts, `t="d"` cells and text dates in one column: the text stays dates.

    Review item 1 of landing R3. The text cells' dates were restored
    only on a column storing no ISO date cells, so here the twin's 20
    text cells held day counts such as `"45404"`: described again, 20
    unparsed, `validate` exit 3, and pandas could not read the twin's
    column as dates where it read the source's.
    """
    monkeypatch.setattr(
        sys.modules[__name__], "_book",
        lambda cells: _three_storages(epoch_1904, code),
    )
    trip = _trip(tmp_path, [])
    column = trip["column"]
    assert column["role"] == "datetime"
    assert column["n_unparsed"] == 0
    census = trip["workbook"]["cell_classes"]
    assert (census["number"], census["date"], census["text"]) == (180, 20, 20)
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    read = _cells_read(trip["twin"])
    texts = [value for value, _code in read if isinstance(value, str)]
    assert len(texts) == 20
    for text in texts:
        datetime.datetime.fromisoformat(text)
    pandas = pytest.importorskip("pandas")
    for book in (tmp_path / "table.xlsx", trip["twin"]):
        frame = crosscheck.read_excel(book)
        assert len(pandas.to_datetime(frame["event_at"])) == 220


def test_a_date_count_goes_first_to_the_t_clocks_and_the_oracle_agrees() -> None:
    """G2.2 step 1's `T` clocks first and step 0's restoration beside date cells.

    Review item 1 of landing R3, value for value against the method's
    oracle over seeded random columns, with the first allocation passed
    as `_members` passes it to a column storing dates as ISO text.
    """
    census = {
        "absent": 0, "blank": 0, "boolean": 0, "date": 1, "empty": 0,
        "error": 0, "number": 0, "text": 2,
    }
    cells = ("2024-01-03T00:00:00", "2024-01-02", "2024-01-04")
    assert sheetwriting.cell_classes(census, cells) == ("date", "text", "text")
    oracle = _oracle()
    from synthtwin import contract

    draw = random.Random(21)
    names = ("absent", "blank", "empty", "text", "number", "boolean", "error", "date")
    for _step in range(2000):
        size = draw.randrange(1, 14)
        census = {
            name: draw.choice((None, 0, draw.randrange(size + 1))) for name in names
        }
        cells = tuple(
            draw.choice((
                "", f"2024-{draw.randrange(1, 13):02d}-{draw.randrange(1, 29):02d}",
                f"2024-02-{draw.randrange(1, 29):02d}T00:00:00",
                f"2024-03-{draw.randrange(1, 29):02d} 09:30:00", "UNK", "45369",
            ))
            for _cell in range(size)
        )
        value_class = draw.choice((None, "number", "text", "date"))
        assert list(sheetwriting.cell_classes(census, cells, value_class)) == (
            oracle.sheet_cell_classes(census, list(cells), value_class)
        ), (census, cells)
        column = contract.WorkbookColumn(
            cell_classes=census, format_code="yyyy-mm-dd",
            format_kinds={"date": size}, formulas=None, value_class=value_class,
        )
        block = {
            "cell_classes": census, "format_code": "yyyy-mm-dd",
            "format_kinds": {"date": size}, "value_class": value_class,
        }
        held = sheetwriting.cell_classes(census, cells, value_class)
        mine = sheetwriting._dates_as_day_counts(column, cells, True, held)
        theirs = oracle.sheet_dates_as_day_counts(block, list(cells), True, held)
        assert (list(mine[0]), list(mine[1])) == (theirs[0], theirs[1]), (block, cells)


@pytest.mark.parametrize(("word", "extra"), (("NA", ()), ("UNK", ("--missing-value", "UNK"))))
def test_stored_dates_are_counted_among_the_present_cells(
    word: str, extra: "tuple[str, ...]", tmp_path: pathlib.Path
) -> None:
    """950 stored dates, 50 text dates and 1,000 missing words: still dates.

    Review item 2 of landing R3. The storage majority counted the
    missing words among the value cells, so 95 % of the PRESENT cells
    stored as dates fell under half of all value cells and the column
    was read as free text: its twin held 2,000 strings and no date, and
    `validate` missed `workbook.cell-classes`.
    """
    draw = random.Random(22)
    cells: "list[tuple[object, str]]" = []
    for index in range(2 * ROWS):
        if index % 2:
            cells += [(word, "General")]
            continue
        day = _day(draw)
        if index % 40 == 0:
            cells += [(day.strftime("%m/%d/%Y"), "General")]
            continue
        cells += [(day, "m/d/yy")]
    texts = ["2024-03-17"] * 95 + ["03/17/2024"] * 5 + [word] * 100
    classes = ["number"] * 95 + ["text"] * 105
    codes = ["m/d/yy"] * 95 + ["General"] * 105
    assert not workbook.stored_as_dates(texts, classes, codes)
    settings = taxonomy.Settings(
        declared_missing_values=tuple(extra[1:]),
    )
    assert workbook.stored_as_dates(
        texts, classes, codes, taxonomy.missing_cells(texts, settings)
    )
    trip = _trip(tmp_path, cells, ("--smallest-group", "11", *extra))
    column = trip["column"]
    assert column["role"] == "datetime"
    assert column["n_missing"] == ROWS
    assert column["n_unparsed"] == 50
    assert trip["twin_exit"] == 0
    assert trip["real_exit"] == 0
    read = _cells_read(trip["twin"])
    dates = [value for value, _code in read if isinstance(value, datetime.datetime)]
    assert len(dates) == 950
    assert len([value for value, _code in read if value == word]) == ROWS


def _clocks_beside_moments(below: bool = False) -> "list[tuple[object, str]]":
    """1,000 `h:mm` numbers: 989 clocks under one day and 11 outside it.

    The 11 are date-times of a day or more, or, ``below``, numbers from
    one to eleven minutes below nought.
    """
    cells: "list[tuple[object, str]]" = []
    for index in range(ROWS):
        if index < 11:
            outside = -(index + 1) / 1440 if below else 45000 + index / 1440
            cells += [(outside, "h:mm")]
            continue
        cells += [(((7 * index) % 1440) / 1440, "h:mm")]
    return cells


@pytest.mark.parametrize("below", (False, True))
def test_clocks_beside_moments_under_one_time_format_are_refused(
    below: bool, tmp_path: pathlib.Path,
) -> None:
    """A time format over numbers both inside one day and outside it.

    Review item 3 of landing R3. openpyxl reads the source as 989 times
    and 11 date-times, all on whole minutes; the column fell back to
    continuous numbers and its twin read as 980 times and 20 date-times,
    979 of them carrying fractions of a second, while `validate`
    reported no miss. Nothing in a description says which values were
    the date-times, so the table is refused, naming the column and what
    to do, as every other mix a twin cannot carry is. ``below`` is the
    same mix with its 11 outside the day below nought, which openpyxl
    also reads as date-times: asked only for a day or more, the repair
    let it through, and its twin read as 988 times and 12 date-times,
    996 cells off the minute, with no miss reported.
    """
    source = [
        type(value).__name__
        for value, _code in _cells_read_from_bytes(
            _book(_clocks_beside_moments(below))
        )
    ]
    assert collections.Counter(source) == {"time": 989, "datetime": 11}
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book(_clocks_beside_moments(below)))
    code, said = _exit_of(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
         "--smallest-group", "11"]
    )
    assert code == 1, said[-600:]
    message = " ".join(said.split())
    assert "event_at" in message
    assert "shown as times of day" in message
    assert "a whole day or more" in message
    assert "or below nought" in message
    assert not (tmp_path / "table-profile.json").exists()
    # The line is drawn where the readers round, at the millisecond: a
    # number short of one day by less than half of one is a date with a
    # time to openpyxl, and stands outside the day.
    edge = 1 - 1e-9
    assert [
        type(value).__name__ for value, _code in _cells_read_from_bytes(
            _book([(edge, "h:mm"), (1 - 1e-7, "h:mm")])
        )
    ] == ["datetime", "time"]
    held = ["number", "number"]
    worn = ["h:mm", "h:mm"]
    assert workbook._clock_and_moment(["0.5", f"{edge!r}"], held, worn)
    assert not workbook._clock_and_moment(["0.5", f"{1 - 1e-7!r}"], held, worn)
    # The control: the same clocks with the eleven brought inside the
    # day are one kind of value to every reader, and are read as clocks
    # (a column of moments alone under `h:mm` is
    # `test_moments_wearing_a_clock_format_stay_numbers`).
    trip = _trip(
        tmp_path / "control",
        [(value % 1, code) for value, code in _clocks_beside_moments(below)],
    )
    assert trip["column"]["role"] == "time_of_day"
    assert trip["twin_exit"] == 0


def _cells_read_from_bytes(held: bytes) -> "list[tuple[object, str]]":
    """Every value cell of the first column of a workbook's bytes, as openpyxl reads it."""
    sheet = crosscheck.reader().load_workbook(io.BytesIO(held)).worksheets[0]
    out: "list[tuple[object, str]]" = []
    for row in sheet.iter_rows(min_row=2, max_col=1):
        if row[0].value is not None:
            out += [(row[0].value, row[0].number_format)]
    return out


def test_a_description_of_clocks_as_numbers_asks_to_be_made_again(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A description made under the reading before P4-D382 is not a file that misses.

    Review item 4 of landing R3. 1,000 `h:mm` cells holding `i/1440`
    were described as `continuous` before the clocks were read; checked
    against that unchanged workbook, the description missed `axes.role`,
    `axes.statistical_type`, `counts.n_numeric` and `counts.n_not_numeric`
    at exit 3. The check now stops and says to describe the table again.
    The description is made here with the clock reading withdrawn, which
    is the reading before (`_read_as_one_column` is where it lives).
    """
    table = tmp_path / "table.xlsx"
    table.write_bytes(_book([(row / 1440, "h:mm") for row in range(ROWS)]))
    with monkeypatch.context() as patched:
        patched.setattr(workbook, "_read_as_one_column", lambda *arguments: None)
        code, said = _exit_of(
            ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]
        )
    assert code == 0, said[-400:]
    described = tmp_path / "table-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    assert document["columns"][0]["role"] == "continuous"
    out = tmp_path / "check"
    out.mkdir()
    code, said = _exit_of(
        ["validate", f"{described}", "--twin", f"{table}", "--out-dir",
         f"{out}", "--replace"]
    )
    message = " ".join(said.split())
    assert code == 1, message[-600:]
    assert "Column number 1 of" in message
    assert "made by an earlier version of synthtwin" in message
    assert "describe the table again" in message
    assert "event_at" not in message
    # ...and the description made now checks the same file at exit 0.
    trip = _trip(tmp_path / "now", [(row / 1440, "h:mm") for row in range(ROWS)])
    assert trip["column"]["role"] == "time_of_day"
    assert trip["real_exit"] == 0


def test_a_format_showing_fewer_figures_is_said_to_show_fewer(
    tmp_path: pathlib.Path,
) -> None:
    """160 moments under `.0` and 40 under `.000`: the report names the cause truly.

    Review item 5 of landing R3. The column is read, wears its commonest
    code `yyyy-mm-dd hh:mm:ss.0` and publishes three figures after the
    second; the twin's report listed the two precision obligations as
    not checkable because the format "writes no figures after the
    second" -- it writes one.
    """
    draw = random.Random(23)
    cells: "list[tuple[object, str]]" = []
    for index in range(200):
        moment = _moment(draw).replace(microsecond=draw.randrange(1, 1000) * 1000)
        code = "yyyy-mm-dd hh:mm:ss.0" if index % 5 else "yyyy-mm-dd hh:mm:ss.000"
        cells += [(moment, code)]
    trip = _trip(tmp_path, cells)
    assert trip["workbook"]["format_code"] == "yyyy-mm-dd hh:mm:ss.0"
    assert trip["column"]["subsecond_digits"] == 3
    assert trip["twin_exit"] == 0
    report = " ".join(
        next((tmp_path / "check-table-twin").glob("*.txt")).read_text(
            encoding="utf-8"
        ).split()
    )
    assert "writes no figures after the second" not in report
    assert "writes fewer figures after the second than" in report

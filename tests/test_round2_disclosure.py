"""Round 2 of the review, the disclosure pass: each test from its reproduction.

Seven items were raised against commit `05e7d89` by a reviewer reading
only for what a description GIVES AWAY about one person. Each is
reproduced here from the reviewer's own inputs, with the numbers it was
reproduced with written into the test that closes it, and each carries a
RED CHECK that withdraws the repair and shows the defect come back.

THE SEVEN, in the reviewer's order:

1. the BLOCKER -- one recognised spelling of no value in the readings
   column defeated `reading._measurement_among_numbers`, so a headerless
   file published its whole first record as the column names, described
   239 records of 240 and asked nothing: ruling 8 of 2026-09-17 broken
   by one cell, in delimited text and in a workbook alike;
2. a judged placeholder's occurrence total minus its published
   `missing_by_source` count named one cell of a withheld spelling;
3. a form census counted levels that the published levels already
   account for, so subtraction named one held-back label's form --
   ruling 5 bypassed;
4. a column of dates AND timestamps published timestamp-only properties
   against the whole column, so subtracting the date-only cells named
   one exceptional timestamp;
5. `n_numeric` minus `n_negative` minus the plus-sign census named one
   unsigned non-negative cell;
6. a published present-cell population minus the formula count named
   one literal cell;
7. preamble lines and the header line padded a line-ending run over the
   floor, so subtracting them named one record's ending.

Every table and every workbook here is built by neutral code at runtime
(plan D13); the vocabulary is made up on the spot and no cell of anyone's
table appears in this file.
"""

import contextlib
import datetime
import io
import json
import pathlib
import sys

import pytest

from synthtwin import parsing, reading
from tests import workbooks

_FLOOR_ELEVEN = "11"


def _exit_of(argv: "list[str]") -> int:
    """Run one synthtwin command in this process and return its exit code."""
    from synthtwin import cli

    before = sys.argv
    sys.argv = ["synthtwin"] + argv
    try:
        code = cli.main()
    except SystemExit as stop:
        return 0 if stop.code is None else int(stop.code)
    finally:
        sys.argv = before
    return code


def _quiet(argv: "list[str]") -> int:
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        return _exit_of(argv)


def _document(path: pathlib.Path) -> dict:
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


# -- item 1: one cell of no value reopens publication of a record ------
#
# THE REVIEWER'S INPUT. A headerless file with no furniture above it:
# record 1 is `R001,North Unit,<0.10`, records 2 to 239 are
# `R{i:03},East,{i}.5`, and record 240 is `R240,East,NA`. Floor 11.
#
# MEASURED ON `05e7d89`, the last record's reading changed and nothing
# else, delimited text and workbook alike:
#
#   `240.5`  -> `column_1`..`column_3`, 240 records, the question asked
#   (empty)  -> the same; the old population already dropped the empty
#   `NA`     -> `R001`, `North Unit`, `<0.10` as the names; 239 records
#   `#N/A`   -> the same three names; 239 records
#   `<0.05`  -> the same three names; 239 records
#
# The three failing shapes all now read as records.

_LEAD = "R001,North Unit,<0.10"


def _records_ending_with(reading_text: str) -> str:
    """240 records, no header and no title, the last reading as given."""
    lines = [_LEAD]
    for index in range(2, 240):
        lines = lines + [f"R{index:03},East,{index}.5"]
    return "\n".join(lines + [f"R240,East,{reading_text}"]) + "\n"


def _described(tmp_path: pathlib.Path, body: str) -> dict:
    table = tmp_path / "table.csv"
    table.write_text(body, encoding="utf-8", newline="")
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{tmp_path}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    document = _document(tmp_path / "table-profile.json")
    questions = _document(tmp_path / "table-questions.json")
    from synthtwin import asking

    return {
        "names": [block["name"] for block in document["columns"]],
        "n_rows": document["n_rows"],
        "asked": [
            entry
            for entry in questions["about_your_file"]
            if entry["column"] == asking.FIRST_ROW_SUBJECT
        ],
        "written": (
            (tmp_path / "table-profile.json").read_text(encoding="utf-8")
            + (tmp_path / "table-profile.txt").read_text(encoding="utf-8")
            + (tmp_path / "table-questions.json").read_text(encoding="utf-8")
        ),
    }


@pytest.mark.parametrize("reading_text", ["NA", "#N/A", "<0.05", "", "240.5"])
def test_one_absent_or_censored_reading_never_publishes_a_record(
    tmp_path: pathlib.Path, reading_text: str
) -> None:
    """Item 1, the BLOCKER, reproduced and closed for delimited text.

    Three of these five spellings published the first record as the
    file's three column names on `05e7d89` and described 239 records of
    240; the other two were already right and must stay right.
    """
    read = _described(tmp_path, _records_ending_with(reading_text))
    assert read["names"] == ["column_1", "column_2", "column_3"]
    assert read["n_rows"] == 240
    assert len(read["asked"]) == 1
    seen = read["asked"][0]["what_synthtwin_saw"]
    assert "column 3" in seen and "measurement" in seen
    for text in ("R001", "North Unit", "<0.10"):
        assert text not in read["written"], (
            f"the first record's text {text!r} reached a published document"
        )


def _headerless_workbook(reading_text: str) -> bytes:
    """The same 240 records as a sheet of inline strings."""
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "R001", kind="inlineStr"),
                workbooks.cell("B1", "North Unit", kind="inlineStr"),
                workbooks.cell("C1", "<0.10", kind="inlineStr"),
            ],
        )
    ]
    for index in range(2, 241):
        written = f"{index}.5" if index < 240 else reading_text
        rows = rows + [
            (
                index,
                [
                    workbooks.cell(
                        f"A{index}", f"R{index:03}", kind="inlineStr"
                    ),
                    workbooks.cell(f"B{index}", "East", kind="inlineStr"),
                    workbooks.cell(
                        f"C{index}", written, kind="inlineStr"
                    ),
                ],
            )
        ]
    return workbooks.package(
        [
            (
                "[Content_Types].xml",
                workbooks._content_types(1, False, False, False),
            ),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            (
                "xl/_rels/workbook.xml.rels",
                workbooks._workbook_rels(1, False),
            ),
            ("xl/styles.xml", workbooks._styles()),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet(rows, dimension="A1:C240"),
            ),
        ]
    )


@pytest.mark.parametrize("reading_text", ["NA", "<0.05"])
def test_the_same_workbook_publishes_no_record_either(
    tmp_path: pathlib.Path, reading_text: str
) -> None:
    """Item 1 on the workbook side, through to the twin's header row.

    Measured on `05e7d89`: both spellings gave `R001`, `North Unit` and
    `<0.10` as the three column names over 239 records, and the twin's
    own first sheet row was that person's record verbatim.
    """
    table = tmp_path / "real.xlsx"
    table.write_bytes(_headerless_workbook(reading_text))
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{tmp_path}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    document = _document(tmp_path / "real-profile.json")
    assert [block["name"] for block in document["columns"]] == [
        "column_1", "column_2", "column_3",
    ]
    assert document["n_rows"] == 240
    assert (
        _quiet(
            [
                "generate", f"{tmp_path / 'real-profile.json'}",
                "--out-dir", f"{tmp_path}", "--seed", "4", "--replace",
            ]
        )
        == 0
    )
    import openpyxl

    book = openpyxl.load_workbook(tmp_path / "real-twin.xlsx")
    sheet = book[book.sheetnames[0]]
    header = [
        f"{sheet.cell(row=1, column=place).value}" for place in (1, 2, 3)
    ]
    assert header != ["R001", "North Unit", "<0.10"]
    assert sheet.max_row == 240


def test_the_missing_spellings_filter_is_what_holds_item_one_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 1's first half: the vocabulary of no value.

    With `parsing.is_missing_text` answering False for everything, the
    `NA` cell is back in the evidence population, the rule declines the
    column, and the file publishes the record again -- 239 records and
    the three real values as the names, which is exactly what `05e7d89`
    did.
    """
    monkeypatch.setattr(parsing, "is_missing_text", lambda text: False)
    read = _described(tmp_path, _records_ending_with("NA"))
    assert read["names"] == ["R001", "North Unit", "<0.10"]
    assert read["n_rows"] == 239


def test_the_reading_population_is_what_holds_the_censored_cell_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 1's second half: a second censored reading.

    Put `reading._reads_as_a_reading` back to the rule it replaced --
    "this value parses as a number" -- and the one `<0.05` cell defeats
    the column again, republishing the record over 239 rows.
    """
    monkeypatch.setattr(
        reading,
        "_reads_as_a_reading",
        lambda text: parsing.classify_number(text) != parsing.NOT_A_NUMBER,
    )
    read = _described(tmp_path, _records_ending_with("<0.05"))
    assert read["names"] == ["R001", "North Unit", "<0.10"]
    assert read["n_rows"] == 239


def test_a_column_of_readings_with_no_numbers_is_still_no_evidence(
    tmp_path: pathlib.Path
) -> None:
    """The rule stays anchored to a column of NUMBERS.

    Two numbers are required below, as they always were: a column
    written entirely as censored readings offers none for the first
    row's value to stand among, so this rule declines it and the file
    falls through to the furniture rule and to convention. Without that
    floor the widened population would have read any column of
    marked-up text as a column of readings.
    """
    below = ["<0.05"] * 12 + ["NA"] * 3
    assert not reading._measurement_among_numbers("<0.10", below)
    assert reading._measurement_among_numbers("<0.10", ["1.5", "2.5", "NA"])
    assert not reading._measurement_among_numbers("<0.10", ["1.5", "NA"])


# -- the round-trip harness the rest of the items are measured with ---


def _round_trip(
    folder: pathlib.Path,
    body: "str | bytes",
    flags: "list[str]",
    name: str = "table.csv",
    seed: str = "4",
) -> dict:
    """Describe, generate, and validate the twin AND the real file.

    Returns the description and the four exit codes. Every file is
    written with its bytes fixed, so the suite reads the same bytes on
    every platform (the rule `tests/test_description_line_endings.py`
    holds this suite to).
    """
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / name
    if isinstance(body, bytes):
        table.write_bytes(body)
    else:
        table.write_text(body, encoding="utf-8", newline="")
    stem = table.stem
    assert (
        _quiet(
            ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"]
            + flags
        )
        == 0
    )
    described = folder / f"{stem}-profile.json"
    assert (
        _quiet(
            [
                "generate", f"{described}", "--out-dir", f"{folder}",
                "--seed", seed, "--replace",
            ]
        )
        == 0
    )
    twin = folder / f"{stem}-twin{table.suffix}"
    checked_twin = folder / "check-twin"
    checked_twin.mkdir(exist_ok=True)
    checked_real = folder / "check-real"
    checked_real.mkdir(exist_ok=True)
    return {
        "document": _document(described),
        "twin_exit": _quiet(
            [
                "validate", f"{described}", "--twin", f"{twin}",
                "--out-dir", f"{checked_twin}", "--replace",
            ]
        ),
        "real_exit": _quiet(
            [
                "validate", f"{described}", "--twin", f"{table}",
                "--out-dir", f"{checked_real}", "--replace",
            ]
        ),
        "twin": twin,
    }


# -- item 2: a judged candidate's occurrences name a pooled spelling --
#
# THE REVIEWER'S INPUT, at a floor of eleven: a declared measurement of
# 400 cells -- 368 values `100 + i % 100`, twenty `-999`, one `-999.0`
# and eleven `NA`.
#
# MEASURED ON `05e7d89`: `missing_by_source {"-999": 20}` and
# `missing_by_class {"(numeric-sentinel)": 21, "(withheld)": 11}` beside
# a judged `-999` verdict of `n_occurrences` 21 -- so 21 less 20 is one
# cell of a spelling the description never names, twice over. Both files
# validated at nought and the twin wrote twenty `-999` cells and twelve
# blanks.


def _sentinel_column() -> str:
    cells = (
        [f"{100 + place % 100}" for place in range(368)]
        + ["-999"] * 20
        + ["-999.0"]
        + ["NA"] * 11
    )
    rows = ["reading,site"]
    for place in range(len(cells)):
        rows = rows + [f"{cells[place]},s{place % 3}"]
    return "\n".join(rows) + "\n"


def _reading_block(document: dict) -> dict:
    for block in document["columns"]:
        if block["name"] == "reading":
            assert isinstance(block, dict)
            return block
    raise AssertionError("the declared column is not in the description")


def test_a_judged_candidate_leaves_no_spelling_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """Item 2, reproduced and closed.

    The spelling census joins the pool rather than publishing a count
    whose difference from the verdict's own total is one, and both maps
    are raised together, as `_missing_maps` has done since P4-D293.
    """
    read = _round_trip(
        tmp_path / "sentinels",
        _sentinel_column(),
        ["--smallest-group", _FLOOR_ELEVEN, "--measurement", "reading"],
    )
    block = _reading_block(read["document"])
    assert block["missing_by_source"] == {}
    assert block["missing_by_class"]["(withheld)"] == 32
    assert block["n_missing"] == 32
    assert block["n_missing_withheld"] == 32
    verdicts = block["sentinel_verdicts"]
    assert len(verdicts) == 1
    assert verdicts[0]["n_occurrences"] == 21
    assert verdicts[0]["spellings"] == []
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_the_judged_total_is_what_holds_item_two_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 2: withdraw the verdict's own total.

    With `_judged_totals` handing back only the pair the caller already
    held, the pool is not raised and the description publishes
    `{"-999": 20}` beside an `n_occurrences` of 21 again -- the exact
    numbers measured on `05e7d89`.
    """
    from synthtwin import taxonomy

    monkeypatch.setattr(
        taxonomy,
        "_judged_totals",
        lambda entries, judged, by_source, first: [first],
    )
    folder = tmp_path / "sentinels"
    folder.mkdir(parents=True)
    table = folder / "table.csv"
    table.write_text(_sentinel_column(), encoding="utf-8", newline="")
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
                "--measurement", "reading",
            ]
        )
        == 0
    )
    block = _reading_block(_document(folder / "table-profile.json"))
    assert block["missing_by_source"] == {"-999": 20}
    assert block["sentinel_verdicts"][0]["n_occurrences"] == 21
    # ...AND THE LOADER'S HALF REFUSES WHAT THE PRODUCER JUST WROTE,
    # which is the mirror V5 gained with this item: the description
    # does not even reach the generator.
    assert (
        _quiet(
            [
                "generate", f"{folder / 'table-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_a_judged_candidate_may_still_leave_a_group_over(
    tmp_path: pathlib.Path,
) -> None:
    """The bound stays AT MOST and not EXACTLY, which V5 states.

    Twenty cells of one spelling beside five of another, both judged,
    publish one spelling worth twenty against an `n_occurrences` of
    twenty-five at a floor of eleven. Five is a group the pool holds,
    not a row, so nothing moves and the description is unchanged.
    """
    cells = (
        [f"{100 + place % 100}" for place in range(375)]
        + ["-999"] * 20
        + ["-999.0"] * 5
    )
    rows = ["reading,site"]
    for place in range(len(cells)):
        rows = rows + [f"{cells[place]},s{place % 3}"]
    read = _round_trip(
        tmp_path / "bound",
        "\n".join(rows) + "\n",
        ["--smallest-group", _FLOOR_ELEVEN, "--measurement", "reading"],
    )
    block = _reading_block(read["document"])
    assert block["missing_by_source"] == {"-999": 20}
    assert block["sentinel_verdicts"][0]["n_occurrences"] == 25
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


# -- item 3: a form census names a held-back label's form -------------
#
# THE REVIEWER'S INPUT, at a floor of eleven and seed 4: one column of
# `ABC-100` x100, `ABC-200` x100, `ABC-300` x1, `QQ-400` x5, `RR-500` x6.
#
# MEASURED ON `05e7d89`: both common levels published
# `shape_form_cells` 100 beside `shape_forms {"@@@-%%%": 201,
# "@@-%%%": 11}`, so 201 less 200 is one held-back level of one row with
# its form on the page. `n_missing` was nought, the twin wrote one
# `AAA-000`, and both files validated with 47 held and nothing missed.


def _form_column() -> str:
    cells = (
        ["ABC-100"] * 100
        + ["ABC-200"] * 100
        + ["ABC-300"]
        + ["QQ-400"] * 5
        + ["RR-500"] * 6
    )
    return "\n".join(["code"] + cells) + "\n"


def test_a_form_census_names_no_held_back_label(
    tmp_path: pathlib.Path,
) -> None:
    """Item 3, reproduced and closed by ruling 5 (2026-09-17, item 5).

    The singleton level's cell is counted as MISSING, so the census
    counts 200 where the published levels cover 200 and the difference
    is nought. The second key is left exactly as it was: its eleven
    cells belong to two held-back levels, no published level wears that
    form, and the pool is doing what the ruling asks of it.
    """
    read = _round_trip(
        tmp_path / "forms",
        _form_column(),
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    block = read["document"]["columns"][0]
    assert block["shape_forms"] == {"@@@-%%%": 200, "@@-%%%": 11}
    covered = 0
    for level in block["levels"]:
        covered = covered + level["shape_form_cells"]
    assert covered == 200
    assert block["n_missing"] == 1
    assert block["suppressed_levels"] == 2
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_the_form_pass_is_what_holds_item_three_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 3: withdraw the form reading of ruling 5.

    With `_levels_read_by_form` counting nothing out, the census
    publishes 201 against 200 published cells again and `n_missing`
    goes back to nought -- `05e7d89` exactly. The loader's own half
    then refuses the description, so it never reaches a twin.
    """
    from synthtwin import taxonomy

    monkeypatch.setattr(
        taxonomy, "_levels_read_by_form", lambda cells, role, rare: ()
    )
    folder = tmp_path / "forms"
    folder.mkdir(parents=True)
    table = folder / "table.csv"
    table.write_text(_form_column(), encoding="utf-8", newline="")
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    block = _document(folder / "table-profile.json")["columns"][0]
    assert block["shape_forms"]["@@@-%%%"] == 201
    assert block["n_missing"] == 0
    assert (
        _quiet(
            [
                "generate", f"{folder / 'table-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_a_form_census_leaving_two_cells_over_is_unmoved(
    tmp_path: pathlib.Path,
) -> None:
    """The rule fires at ONE cell and at no other number.

    The reviewer's column with a SECOND singleton level of the same
    form leaves two cells over the published levels, which is a group
    and not a row, so nothing is counted out, `n_missing` stays nought
    and the census publishes 202. A rule that counted out every
    held-back level would have emptied this column for nothing.
    """
    cells = (
        ["ABC-100"] * 100
        + ["ABC-200"] * 100
        + ["ABC-300"]
        + ["ABC-400"]
        + ["QQ-400"] * 5
        + ["RR-500"] * 6
    )
    read = _round_trip(
        tmp_path / "two",
        "\n".join(["code"] + cells) + "\n",
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    block = read["document"]["columns"][0]
    assert block["shape_forms"] == {"@@@-%%%": 202, "@@-%%%": 11}
    assert block["n_missing"] == 0
    assert block["suppressed_levels"] == 4
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


# -- item 4: a joint column's timestamp-only residuals ----------------
#
# THE REVIEWER'S TWO INPUTS, at a floor of eleven, each 400 cells:
#
# * 100 ISO dates, 299 timestamps at noon, one at midnight -- MEASURED
#   ON `05e7d89`: `resolution_mix {"iso-date": 100, "iso-datetime":
#   300}` beside `n_at_midnight` 101, and 101 less 100 is one person's
#   time of day;
# * 100 ISO dates, 299 noon timestamps ending `Z`, one unzoned noon
#   timestamp -- MEASURED: the same mix beside `utc_offsets
#   {"(none)": 101, "Z": 299}`, and 101 less 100 is that one cell.
#
# Both descriptions loaded and both source files validated with nothing
# missed.

_FIRST_DAY = datetime.date(2021, 1, 1)


def _day(place: int) -> str:
    return (_FIRST_DAY + datetime.timedelta(days=place)).isoformat()


def _joint_column(odd_one: str) -> str:
    cells: "list[str]" = []
    for place in range(100):
        cells = cells + [_day(place)]
    for place in range(299):
        cells = cells + [f"{_day(place)}T12:00:00"]
    return "\n".join(["moment"] + cells + [odd_one]) + "\n"


def _zoned_column(odd_one: str) -> str:
    cells: "list[str]" = []
    for place in range(100):
        cells = cells + [_day(place)]
    for place in range(299):
        cells = cells + [f"{_day(place)}T12:00:00Z"]
    return "\n".join(["moment"] + cells + [odd_one]) + "\n"


def test_a_joint_column_names_no_lone_midnight_timestamp(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4's first half, reproduced and closed.

    The whole dates stand at midnight by definition and the mix counts
    them exactly, so the count is held to the floor on both sides of
    the TIMESTAMPS' own residual -- and where it cannot be, the field
    goes to its one silence, `null`.
    """
    read = _round_trip(
        tmp_path / "midnight",
        _joint_column(f"{_day(5)}T00:00:00"),
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    block = read["document"]["columns"][0]
    assert block["resolution_mix"] == {"iso-date": 100, "iso-datetime": 300}
    assert block["n_at_midnight"] is None
    assert block["all_at_midnight"] is False
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_a_joint_column_names_no_lone_unzoned_timestamp(
    tmp_path: pathlib.Path,
) -> None:
    """Item 4's second half, reproduced and closed by ruling 6.

    The rare offset of the TIMESTAMPS is counted into the commonest one
    they wrote, so the one unzoned cell is read at `Z` and `(none)`
    counts the whole dates and nothing else: 100 against a mix of 100.
    """
    read = _round_trip(
        tmp_path / "offsets",
        _zoned_column(f"{_day(5)}T12:00:00"),
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    block = read["document"]["columns"][0]
    assert block["resolution_mix"] == {"iso-date": 100, "iso-datetime": 300}
    assert block["utc_offsets"] == {"(none)": 100, "Z": 300}
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_the_midnight_residual_is_what_holds_item_four_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 4's first half.

    With `_joint_midnight_nameable` answering True for everything the
    count comes back as 101 beside 100 date-only cells -- the number
    measured on `05e7d89` -- and the loader's own half then refuses it.
    """
    from synthtwin import taxonomy

    monkeypatch.setattr(
        taxonomy,
        "_joint_midnight_nameable",
        lambda format_name, sources, floor: True,
    )
    folder = tmp_path / "midnight"
    folder.mkdir(parents=True)
    table = folder / "table.csv"
    table.write_text(
        _joint_column(f"{_day(5)}T00:00:00"), encoding="utf-8", newline=""
    )
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    block = _document(folder / "table-profile.json")["columns"][0]
    assert block["n_at_midnight"] == 101
    assert (
        _quiet(
            [
                "generate", f"{folder / 'table-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_the_timestamp_population_is_what_holds_the_offset_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 4's second half.

    With `_date_only_places` finding none, the offset census is decided
    over the whole column again, `(none)` clears the floor on the whole
    dates' backs, and the map is `{"(none)": 101, "Z": 299}` -- the
    numbers measured on `05e7d89`. The loader then refuses it.
    """
    from synthtwin import taxonomy

    monkeypatch.setattr(
        taxonomy,
        "_date_only_places",
        lambda format_name, pairs, sources: {},
    )
    folder = tmp_path / "offsets"
    folder.mkdir(parents=True)
    table = folder / "table.csv"
    table.write_text(
        _zoned_column(f"{_day(5)}T12:00:00"), encoding="utf-8", newline=""
    )
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    block = _document(folder / "table-profile.json")["columns"][0]
    assert block["utc_offsets"] == {"(none)": 101, "Z": 299}
    assert (
        _quiet(
            [
                "generate", f"{folder / 'table-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_a_joint_column_of_ordinary_size_still_counts_that_hour(
    tmp_path: pathlib.Path,
) -> None:
    """A residual that is a GROUP on both sides still publishes.

    100 whole dates, 150 timestamps at midnight and 150 at noon leave
    150 and 150, so the count stands at 250 and nothing is withheld.
    """
    cells: "list[str]" = []
    for place in range(100):
        cells = cells + [_day(place)]
    for place in range(150):
        cells = cells + [f"{_day(place)}T00:00:00"]
    for place in range(150):
        cells = cells + [f"{_day(place)}T12:00:00"]
    read = _round_trip(
        tmp_path / "even",
        "\n".join(["moment"] + cells) + "\n",
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    block = read["document"]["columns"][0]
    assert block["resolution_mix"] == {"iso-date": 100, "iso-datetime": 300}
    assert block["n_at_midnight"] == 250
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


# -- item 5: the plus census and the population a reader derives ------
#
# THE REVIEWER'S INPUT, at a floor of eleven: a declared measurement of
# 500 cells -- 400 written `+100.5` upward, 99 written `-100.5` downward
# and ONE written `250.5`.
#
# MEASURED ON `05e7d89`: `n_numeric` 500, `n_negative` 99 and
# `decimal_plus {"+": 400}`, so 500 less 99 less 400 is one unsigned
# non-negative cell. The description loaded and the source file
# validated with 69 held and nothing missed.


def _signed_column() -> str:
    cells: "list[str]" = []
    for place in range(400):
        cells = cells + [f"+{100 + place}.5"]
    for place in range(99):
        cells = cells + [f"-{100 + place}.5"]
    return "\n".join(["reading"] + cells + ["250.5"]) + "\n"


def _profiled(
    tmp_path: pathlib.Path, body: str, flags: "list[str]"
) -> dict:
    """Describe one file and hand back its first column's block."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = tmp_path / "table.csv"
    table.write_text(body, encoding="utf-8", newline="")
    assert (
        _quiet(
            ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]
            + flags
        )
        == 0
    )
    block = _document(tmp_path / "table-profile.json")["columns"][0]
    assert isinstance(block, dict)
    return block


def test_the_plus_census_leaves_no_unsigned_cell_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """Item 5, reproduced and closed by ruling 6 (2026-09-17, item 6).

    The one unsigned non-negative cell is a spelling below the line, so
    it is counted into the commonest spelling the column wrote -- the
    plus -- and the census says 401. The subtraction then comes to
    nought, and 400 cells keep the plus the twin writes them with.
    """
    block = _profiled(
        tmp_path / "signed",
        _signed_column(),
        ["--smallest-group", _FLOOR_ELEVEN, "--measurement", "reading"],
    )
    assert block["n_numeric"] == 500
    assert block["n_negative"] == 99
    assert block["decimal_plus"] == {"+": 401}
    assert block["n_numeric"] - block["n_negative"] - 401 == 0


def test_the_derived_population_is_what_holds_item_five_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 5: withdraw the population a reader derives.

    With `_signable_decimals` answering nought, neither ruling 6 nor
    the second reading of the disclosure rule is asked, and the census
    publishes 400 against 500 decimals and 99 negatives -- `05e7d89`
    exactly, one cell recoverable by subtraction.
    """
    from synthtwin import taxonomy

    monkeypatch.setattr(
        taxonomy, "_signable_decimals", lambda decimals, negatives: 0
    )
    block = _profiled(
        tmp_path / "signed",
        _signed_column(),
        ["--smallest-group", _FLOOR_ELEVEN, "--measurement", "reading"],
    )
    assert block["decimal_plus"] == {"+": 400}
    assert block["n_numeric"] - block["n_negative"] - 400 == 1


def test_a_column_of_both_kinds_of_number_is_unmoved(
    tmp_path: pathlib.Path,
) -> None:
    """The derived population is read only where it is consistent.

    `n_negative` counts the negative WHOLE numbers too, so on a column
    written half `+12` and half `+3.25` the difference falls below the
    signed count and says nothing. It is not read there, and the census
    is the exact count of signed decimals it always was.
    """
    cells: "list[str]" = []
    for place in range(450):
        cells = cells + [f"{place - 225:+d}"]
    for place in range(450):
        cells = cells + [f"{(place - 225) + 0.25:+.2f}"]
    block = _profiled(
        tmp_path / "both",
        "\n".join(["change"] + cells) + "\n",
        ["--smallest-group", _FLOOR_ELEVEN, "--measurement", "change"],
    )
    signed = 0
    for cell in cells:
        if cell[:1] == "+" and "." in cell:
            signed = signed + 1
    assert block["decimal_plus"] == {"+": signed}


# -- item 6: a formula count names a lone literal cell ----------------
#
# THE REVIEWER'S INPUT, at a floor of eleven: a 400-record workbook
# whose measurement column holds twenty formulas `20+1` through `20+20`
# with cached results 21 to 40, ONE literal `41`, and 379 physically
# absent cells; a second column is populated throughout.
#
# MEASURED ON `05e7d89`: `cell_classes {"number": 21, "absent": 379}`
# with every other class nought, beside `formulas` 20 -- and 21 less 20
# is the one cell somebody typed by hand. Both ends of 20 against 400
# rows clear eleven, which is why the row count alone let it through.


def _formula_book(literal: int = 1, n_rows: int = 400) -> bytes:
    rows = [
        (
            1,
            [
                workbooks.cell("A1", "reading", kind="inlineStr"),
                workbooks.cell("B1", "site", kind="inlineStr"),
            ],
        )
    ]
    for index in range(2, n_rows + 2):
        record = index - 1
        cells: "list[str]" = []
        if record <= 20:
            cells = cells + [
                workbooks.cell(
                    f"A{index}", f"{20 + record}", formula=f"20+{record}"
                )
            ]
        elif record <= 20 + literal:
            cells = cells + [
                workbooks.cell(f"A{index}", f"{20 + record}")
            ]
        cells = cells + [
            workbooks.cell(f"B{index}", f"s{record % 4}", kind="inlineStr")
        ]
        rows = rows + [(index, cells)]
    return workbooks.package(
        [
            (
                "[Content_Types].xml",
                workbooks._content_types(1, False, False, False),
            ),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            (
                "xl/_rels/workbook.xml.rels",
                workbooks._workbook_rels(1, False),
            ),
            ("xl/styles.xml", workbooks._styles()),
            (
                "xl/worksheets/sheet1.xml",
                workbooks.sheet(rows, dimension=f"A1:B{n_rows + 1}"),
            ),
        ]
    )


def _sheet_column(document: dict, place: int) -> dict:
    block = document["source"]["workbook"]["columns"][place]
    assert isinstance(block, dict)
    return block


def test_a_formula_count_names_no_literal_cell(
    tmp_path: pathlib.Path,
) -> None:
    """Item 6, reproduced and closed.

    A formula cell is a PRESENT cell, so the count is held to the line
    inside the present cells the census publishes as well as inside the
    rows -- and twenty of twenty-one leaves one, so the count is
    withheld.
    """
    read = _round_trip(
        tmp_path / "formulas",
        _formula_book(),
        ["--smallest-group", _FLOOR_ELEVEN],
        name="real.xlsx",
    )
    block = _sheet_column(read["document"], 0)
    assert block["cell_classes"]["number"] == 21
    assert block["cell_classes"]["absent"] == 379
    assert block["formulas"] is None
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_the_present_cells_are_what_hold_item_six_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 6: withdraw the present-cell population.

    With `workbook._present_cells` answering None the count is asked
    only of the 400 rows again, both ends of 20 clear eleven, and the
    description publishes `formulas` 20 beside 21 number cells --
    `05e7d89` exactly. The loader's own half then refuses it.
    """
    from synthtwin import workbook

    monkeypatch.setattr(workbook, "_present_cells", lambda census: None)
    folder = tmp_path / "formulas"
    folder.mkdir(parents=True)
    table = folder / "real.xlsx"
    table.write_bytes(_formula_book())
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    block = _sheet_column(_document(folder / "real-profile.json"), 0)
    assert block["formulas"] == 20
    assert block["cell_classes"]["number"] == 21
    assert (
        _quiet(
            [
                "generate", f"{folder / 'real-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_a_formula_count_with_room_beside_it_still_publishes(
    tmp_path: pathlib.Path,
) -> None:
    """A count with a group on both sides inside the present cells stands.

    The same workbook with fifteen literal cells beside the twenty
    formulas leaves 35 present cells and fifteen over, which is a
    group, so the count is published exactly as before.
    """
    read = _round_trip(
        tmp_path / "room",
        _formula_book(literal=15),
        ["--smallest-group", _FLOOR_ELEVEN],
        name="real.xlsx",
    )
    block = _sheet_column(read["document"], 0)
    assert block["cell_classes"]["number"] == 35
    assert block["formulas"] == 20
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


# -- item 7: file furniture disguises a singleton record ending -------
#
# THE REVIEWER'S INPUT, at a floor of eleven: ten title lines, the
# header `record,reading`, record 1 written with a bare newline, and
# records 2 to 120 written with a carriage return and a newline.
#
# MEASURED ON `05e7d89`: a preamble of ten lines beside `line_endings
# [{"lf": 12}, {"crlf": 119}]` -- and 12 less 10 less 1 is the first
# record, the only one of the 120 written that way.


def _furnished_file(titles: int = 10) -> str:
    lines: "list[str]" = []
    for place in range(titles):
        lines = lines + [f"# extract note {place}\n"]
    lines = lines + ["record,reading\n", "R001,1\n"]
    for place in range(2, 121):
        lines = lines + [f"R{place:03},{place}\r\n"]
    return "".join(lines)


def _form_of(document: dict) -> dict:
    form = document["source"]["dialect"]
    assert isinstance(form, dict)
    return form


def test_file_furniture_never_carries_a_lone_record_ending(
    tmp_path: pathlib.Path,
) -> None:
    """Item 7, reproduced and closed.

    The lines above the table come off the front before the run rule is
    asked, so the file collapses to one run of the commonest ending --
    which is what P4-D290 already did for every other rare ending.
    """
    read = _round_trip(
        tmp_path / "furniture",
        _furnished_file(),
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    form = _form_of(read["document"])
    assert form["preamble"] == [{"kind": "comment", "lines": 10, "mark": "# "}]
    assert form["line_endings"] == [{"ending": "crlf", "lines": 131}]
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)


def test_the_furniture_subtraction_is_what_holds_item_seven_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """RED CHECK for item 7: withdraw the subtraction.

    With `record_endings` handing the runs back untouched, the ten
    title lines and the header carry the bare newline over the line
    again and the description publishes `[{lf: 12}, {crlf: 119}]` --
    `05e7d89` exactly. The loader's own half then refuses it.
    """
    from synthtwin import dialect

    monkeypatch.setattr(
        dialect, "record_endings", lambda runs, above: list(runs)
    )
    folder = tmp_path / "furniture"
    folder.mkdir(parents=True)
    table = folder / "table.csv"
    table.write_text(_furnished_file(), encoding="utf-8", newline="")
    assert (
        _quiet(
            [
                "profile", f"{table}", "--out-dir", f"{folder}",
                "--replace", "--smallest-group", _FLOOR_ELEVEN,
            ]
        )
        == 0
    )
    form = _form_of(_document(folder / "table-profile.json"))
    assert form["line_endings"] == [
        {"ending": "lf", "lines": 12}, {"ending": "crlf", "lines": 119},
    ]
    # ...AND THE LOADER'S HALF REFUSES IT once the rule is back in
    # place. It is put back first because `dialect.endings_broken` asks
    # the very function this test withdrew, which is what makes the two
    # halves one rule rather than two.
    monkeypatch.undo()
    assert (
        _quiet(
            [
                "generate", f"{folder / 'table-profile.json'}",
                "--out-dir", f"{folder}", "--seed", "4", "--replace",
            ]
        )
        == 1
    )


def test_a_file_whose_records_change_ending_in_groups_is_unmoved(
    tmp_path: pathlib.Path,
) -> None:
    """Runs that are groups on both sides of the furniture still stand.

    Ten title lines, a header, then sixty records with a bare newline
    and sixty with a carriage return and a newline: the records' own
    runs are sixty and sixty, so nothing collapses and the file's form
    is published as it stands.
    """
    lines: "list[str]" = []
    for place in range(10):
        lines = lines + [f"# extract note {place}\n"]
    lines = lines + ["record,reading\n"]
    for place in range(1, 61):
        lines = lines + [f"R{place:03},{place}\n"]
    for place in range(61, 121):
        lines = lines + [f"R{place:03},{place}\r\n"]
    read = _round_trip(
        tmp_path / "groups",
        "".join(lines),
        ["--smallest-group", _FLOOR_ELEVEN],
    )
    form = _form_of(read["document"])
    assert form["line_endings"] == [
        {"ending": "lf", "lines": 71}, {"ending": "crlf", "lines": 60},
    ]
    assert (read["twin_exit"], read["real_exit"]) == (0, 0)

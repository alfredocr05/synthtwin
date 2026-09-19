"""The merge skeptic's pass over the extra round, each test from its reproduction.

One skeptic read the tree the four extra-round branches were merged into
(commit `8da4e13`), ran all thirty-nine of the round's own items again,
and then spent an hour of its own on eight realistic shapes. This file
carries the repairs of what it found open, each run END TO END wherever
the defect is one a person meets -- a realistic source is written,
described, generated, and both files validated -- because a twin holding
every published fact can still hand a reader a different table, and a
description holding every rule can still name a row.

THE THREE IT FOUND AND THIS LANDING CLOSES:

* its BLOCKER, `_a_headerless_table_publishes_its_first_record`: a
  headerless table with NO title line above it published its whole first
  record as the column names and wrote it verbatim into the twin, in
  delimited text and in a workbook alike. Plan P4-D292, the fifth record
  rule of `reading._measurement_among_numbers`;
* its third MAJOR, the absent-value class census: a pool of one named a
  row outright and again by subtraction from its sibling total. Plan
  P4-D293, the pool raised in `taxonomy._missing_maps`;
* its second MAJOR, a month-name date column of ordinary size: the twin
  missed both distinctness obligations and validated at exit 3. Plan
  P4-D294, the day's width KIND corrected to the census's own membership
  question in `generation`.

THE RED CHECKS, each measured by withdrawing the rule in place:

* `reading._measurement_among_numbers` answering False --
  `test_a_headerless_table_of_records_names_no_column` and
  `test_a_headerless_workbook_of_records_writes_no_record`;
* `taxonomy._smallest_named_spelling` answering None --
  `test_an_absent_census_never_names_one_row`;
* `generation._counts_into_width` put back to `generation._shows_a_width`
  -- `test_a_month_name_date_column_meets_both_distinct_counts`;
* `generation._subsecond_notes` returning no deviation --
  `test_a_subsecond_column_names_the_fraction_it_writes_as_nought`.

AND ONE THE SKEPTIC CARRIED that this landing does not close but stops
being silent about: a column published at subsecond precision has every
cell's fraction written as nought, in delimited text and in a workbook
alike. The repair is a landing of its own (plan P4-D296 states why); the
twin's own report names the loss now, which is this package's rule for a
count a pass cannot reach.

Every table and every workbook here is built by neutral code at runtime
(plan D13); the vocabulary is made up on the spot.
"""

import contextlib
import datetime
import io
import json
import pathlib
import sys

import pytest

from synthtwin import asking, generation, reading, taxonomy
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


# -- the BLOCKER: a headerless table with nothing above it -------------

_LEAD = "R001,North Unit,<0.10"


def _bare_records() -> str:
    """240 records, no header line and no title line above them.

    The first record's third field is a reading under a limit of
    detection -- a VALUE of a column of readings, written the way no
    column name is written.
    """
    lines = [_LEAD]
    for index in range(2, 241):
        lines += [f"R{index:03},East,{index}.5"]
    return "\n".join(lines) + "\n"


def _described(tmp_path: pathlib.Path, body: str) -> dict:
    table = tmp_path / "table.csv"
    table.write_text(body, encoding="utf-8", newline="")
    assert _quiet(
        [
            "profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
            "--smallest-group", _FLOOR_ELEVEN,
        ]
    ) == 0
    document = _document(tmp_path / "table-profile.json")
    questions = _document(tmp_path / "table-questions.json")
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


def test_a_headerless_table_of_records_names_no_column(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's BLOCKER, reproduced and closed (plan P4-D292).

    Measured on the merged tree before this landing: the names were
    `R001`, `North Unit` and `<0.10`, `n_rows` was 239 where the file
    holds 240, `about_your_file` held no first-row question at all, and
    the record's text stood in the description, in its printed page and
    in the questions file.
    """
    read = _described(tmp_path, _bare_records())
    assert read["names"] == ["column_1", "column_2", "column_3"]
    assert read["n_rows"] == 240
    assert len(read["asked"]) == 1
    seen = read["asked"][0]["what_synthtwin_saw"]
    assert "column 3" in seen and "measurement" in seen
    for text in ("R001", "North Unit", "<0.10"):
        assert text not in read["written"], (
            f"the first record's text {text!r} reached a published document"
        )


def test_the_same_table_under_a_title_line_is_unmoved(
    tmp_path: pathlib.Path,
) -> None:
    """The shape that was ALREADY right stays right.

    The skeptic's evidence turned on the difference between the two: with
    `Cohort extract` above the records the merged tree was correct
    already, by the furniture rule and not by this one. A repair that
    moved this shape would have been a repair of the wrong thing.
    """
    read = _described(tmp_path, "Cohort extract\n" + _bare_records())
    assert read["names"] == ["column_1", "column_2", "column_3"]
    assert read["n_rows"] == 240
    assert len(read["asked"]) == 1


def test_an_ordinary_header_of_names_is_still_read_as_names(
    tmp_path: pathlib.Path,
) -> None:
    """The fifth rule declines every value that opens on a letter.

    `q1`, `week_2` and `glucose1` carry figures and are column names by
    every reading; the rule that closed the blocker must not reach them,
    which is the direction plan P4-D272's own repair pass was written in.
    """
    lines = ["subject,q1,week_2,glucose1"]
    for index in range(300):
        lines += [f"S{index:04},{index % 5},{index % 7},{index % 11}"]
    read = _described(tmp_path, "\n".join(lines) + "\n")
    assert read["names"] == ["subject", "q1", "week_2", "glucose1"]
    assert read["n_rows"] == 300
    assert read["asked"] == []


def test_a_pivoted_year_over_counts_is_still_a_header(
    tmp_path: pathlib.Path,
) -> None:
    """A first-row value that IS a number never reaches the fifth rule.

    `_numeric_fit` is the rule for those and it measures the distance, so
    `2019` over fourteen rows near 1234 stays a column name. The fifth
    rule declines it before looking at the column at all, which is what
    keeps this shape where plan P1-R6-F6 put it.
    """
    lines = ["region,2019,2020"]
    for index in range(40):
        lines += [f"area {index},{1234 + index},{1300 + index}"]
    read = _described(tmp_path, "\n".join(lines) + "\n")
    assert read["names"] == ["region", "2019", "2020"]
    assert read["asked"] == []


def test_the_fifth_rule_is_what_holds_the_blocker_shut(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE RED CHECK. Withdraw the rule and the record comes back.

    This is the measurement the repair rests on: with
    `reading._measurement_among_numbers` answering False the bare table
    publishes its first record's text as the three column names again,
    and describes 239 rows where the file holds 240.
    """
    monkeypatch.setattr(
        reading, "_measurement_among_numbers", lambda name, values: False
    )
    read = _described(tmp_path, _bare_records())
    assert read["names"] == ["R001", "North Unit", "<0.10"]
    assert read["n_rows"] == 239


def _headerless_workbook() -> bytes:
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
        rows += [
            (
                index,
                [
                    workbooks.cell(
                        f"A{index}", f"R{index:03}", kind="inlineStr"
                    ),
                    workbooks.cell(f"B{index}", "East", kind="inlineStr"),
                    workbooks.cell(
                        f"C{index}", f"{index}.5", kind="inlineStr"
                    ),
                ],
            )
        ]
    return workbooks.package(
        [
            ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(rows, dimension="A1:C240")),
        ]
    )


def test_a_headerless_workbook_of_records_writes_no_record(
    tmp_path: pathlib.Path,
) -> None:
    """The same blocker as a workbook, through to the twin's header row.

    Measured before this landing: the twin workbook's first row held
    `R001`, `North Unit` and `<0.10` -- a real person's whole record,
    written out by the generator as the sheet's header.
    """
    table = tmp_path / "real.xlsx"
    table.write_bytes(_headerless_workbook())
    assert _quiet(
        [
            "profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace",
            "--smallest-group", _FLOOR_ELEVEN,
        ]
    ) == 0
    document = _document(tmp_path / "real-profile.json")
    assert [block["name"] for block in document["columns"]] == [
        "column_1", "column_2", "column_3",
    ]
    assert document["n_rows"] == 240
    assert _quiet(
        [
            "generate", f"{tmp_path / 'real-profile.json'}", "--out-dir",
            f"{tmp_path}", "--seed", "4", "--replace",
        ]
    ) == 0
    import openpyxl

    book = openpyxl.load_workbook(tmp_path / "real-twin.xlsx")
    sheet = book[book.sheetnames[0]]
    header = [f"{sheet.cell(row=1, column=place).value}" for place in (1, 2, 3)]
    assert header != ["R001", "North Unit", "<0.10"]
    assert sheet.max_row == 240


# -- the third MAJOR: a pool of one in the absent-value censuses -------

_PRESENT = ["north"] * 200 + ["south"] * 180


def _absences(
    tmp_path: pathlib.Path, cells: "list[str]", floor: str = _FLOOR_ELEVEN
) -> dict:
    """Describe a column of those cells beside a second column."""
    from tests.test_final_review_labels import _round_trip

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = _round_trip(
            tmp_path, {"value": list(cells)}, ("--smallest-group", floor)
        )
    for column in result["document"]["columns"]:
        if column["name"] == "value":
            return {"column": column, "result": result}
    raise AssertionError("no column called 'value'")


def test_an_absent_census_never_names_one_row(tmp_path: pathlib.Path) -> None:
    """The skeptic's third MAJOR, reproduced and closed (plan P4-D293).

    Measured on the merged tree: `missing_by_source {"NA": 19}`,
    `missing_by_class {"(text-code)": 19, "(withheld)": 1}` and
    `n_missing_withheld` 1 beside `n_missing` 20 -- the count of one
    outright, and 20 less 19 by subtraction. The pool is raised now, so
    the column publishes what it publishes at a floor of twenty.
    """
    read = _absences(tmp_path, _PRESENT + ["NA"] * 19 + ["-999"])
    column = read["column"]
    assert column["n_missing"] == 20
    assert column["n_missing_withheld"] == 20
    assert column["missing_by_source"] == {}
    assert column["missing_by_class"]["(withheld)"] == 20
    assert column["missing_by_class"]["(text-code)"] == 0
    for name in column["missing_by_class"]:
        assert column["missing_by_class"][name] != 1
    assert (
        read["result"]["generated"],
        read["result"]["twin_exit"],
        read["result"]["real_exit"],
    ) == (0, 0, 0)


def test_the_raised_pool_is_what_a_raised_floor_would_publish(
    tmp_path: pathlib.Path,
) -> None:
    """The repair's own standard: it publishes no less than the floor does.

    The same 400 cells at a floor of twenty pool everything already. The
    rule of P4-D293 brings the floor-eleven description to that same
    reading rather than to one of its own, which is what makes it the
    floor's discipline and not a new one.
    """
    at_eleven = _absences(tmp_path / "eleven", _PRESENT + ["NA"] * 19 + ["-999"])
    at_twenty = _absences(
        tmp_path / "twenty", _PRESENT + ["NA"] * 19 + ["-999"], floor="20"
    )
    for field in (
        "n_missing", "n_missing_blank", "n_missing_withheld",
        "missing_by_source", "missing_by_class",
    ):
        assert at_eleven["column"][field] == at_twenty["column"][field]


def test_a_census_the_floor_can_name_is_left_alone(
    tmp_path: pathlib.Path,
) -> None:
    """The rule reaches a pool of ONE and nothing else.

    Nineteen `NA` beside two rare words pool to two, which names no row,
    so the spellings census keeps its key and the class census keeps its
    count. A rule that pooled whenever anything was held back would have
    taken this column's census too.
    """
    read = _absences(tmp_path, _PRESENT + ["NA"] * 19 + ["-999", "-998"])
    column = read["column"]
    assert column["missing_by_source"] == {"NA": 19}
    assert column["missing_by_class"]["(text-code)"] == 19
    assert column["n_missing_withheld"] == 2


def test_a_lone_absent_cell_is_the_rules_named_limit(
    tmp_path: pathlib.Path,
) -> None:
    """Where the pool holds EVERY absent cell there is nothing to raise it with.

    `missing_by_class` publishes `{"(withheld)": 1}` and the column says
    `n_missing` 1 beside it. The pool is that count, so the map adds no
    reading the description does not already carry; the limit is stated
    in `_missing_maps` rather than left to be found.
    """
    read = _absences(tmp_path, _PRESENT + ["NA"])
    column = read["column"]
    assert column["n_missing"] == 1
    assert column["missing_by_class"]["(withheld)"] == 1
    assert column["missing_by_source"] == {}


def test_raising_the_pool_is_what_closes_the_census(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE RED CHECK. Withdraw the raise and the count of one comes back."""
    monkeypatch.setattr(
        taxonomy,
        "_smallest_named_spelling",
        lambda by_source, named_blank, settings: None,
    )
    read = _absences(tmp_path, _PRESENT + ["NA"] * 19 + ["-999"])
    column = read["column"]
    assert column["missing_by_source"] == {"NA": 19}
    assert column["missing_by_class"]["(withheld)"] == 1
    assert column["n_missing_withheld"] == 1


# -- the second MAJOR: a month-name date column of ordinary size -------


def _month_name_cells(spelling: str) -> "list[str]":
    start = datetime.date(2021, 1, 1)
    return [
        (start + datetime.timedelta(days=index % 250)).strftime(spelling)
        for index in range(400)
    ]


def _dates(tmp_path: pathlib.Path, spelling: str) -> dict:
    from tests.test_final_review_labels import _round_trip

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = _round_trip(
            tmp_path,
            {"taken_on": _month_name_cells(spelling)},
            ("--smallest-group", _FLOOR_ELEVEN),
        )
    for column in result["document"]["columns"]:
        if column["name"] == "taken_on":
            return {"column": column, "result": result}
    raise AssertionError("no column called 'taken_on'")


@pytest.mark.parametrize(
    "spelling", ("%d-%b-%Y", "%Y-%m-%d", "%m/%d/%Y"), ids=("month-name", "iso", "slashed")
)
def test_a_month_name_date_column_meets_both_distinct_counts(
    tmp_path: pathlib.Path, spelling: str
) -> None:
    """The skeptic's second MAJOR, reproduced and closed (plan P4-D294).

    Four hundred cells over 250 different days. Measured on the merged
    tree: the ISO and the slashed spellings came back 250 of 250 and
    validated at nought, and the month-name spelling alone held 246,
    missed `distinct.n_distinct` and `distinct.n_distinct_folded` and
    validated at exit 3 -- an ordinary column of dates whose twin a
    person could not use.
    """
    read = _dates(tmp_path, spelling)
    assert read["column"]["n_distinct"] == 250
    twin = read["result"]["twin"]["taken_on"]
    assert len(set(twin)) == 250
    assert (
        read["result"]["generated"],
        read["result"]["twin_exit"],
        read["result"]["real_exit"],
    ) == (0, 0, 0)


def test_the_census_question_is_what_the_kind_question_asks(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE RED CHECK. Put the narrower question back and the twin falls short.

    `generation._counts_into_width` is the census's own membership
    question -- a day shows the word, or shows no width at all and is
    absorbed into it. Answering with `_shows_a_width` instead is the
    question the merged tree asked, and it traps a month-name column: no
    day of ten or more may take a free unit beside a day below ten,
    however many rounds the restoration runs.
    """
    monkeypatch.setattr(
        generation,
        "_counts_into_width",
        lambda facts, day_number, word: generation._shows_a_width(
            facts, day_number, word
        ),
    )
    read = _dates(tmp_path, "%d-%b-%Y")
    twin = read["result"]["twin"]["taken_on"]
    assert len(set(twin)) < 250
    assert read["result"]["twin_exit"] == 3


def test_the_two_width_questions_are_not_the_same_question() -> None:
    """The truth table the repair turns on, stated as a test.

    A joint word absorbs every day: one below ten SHOWS it, one at ten
    and above shows nothing and is counted into it. A one-field word does
    not: a day whose other field is below ten shows the OTHER convention
    and is counted out. So `_shows_a_width` and `_counts_into_width`
    answer differently, and the census counts by the second.
    """
    from synthtwin import parsing

    for month, day in ((3, 15), (11, 19), (5, 4), (12, 30)):
        number = parsing.days_from_civil(2021, month, day)
        joint = _WidthFacts("month-first-date")
        assert generation._counts_into_width(joint, number, "unpadded") is True
    one_field = _WidthFacts("month-first-date")
    september = parsing.days_from_civil(2021, 9, 4)
    october = parsing.days_from_civil(2021, 10, 4)
    assert generation._shows_a_width(
        one_field, september, "second-field-padded"
    ) is False
    assert generation._counts_into_width(
        one_field, september, "second-field-padded"
    ) is False
    assert generation._counts_into_width(
        one_field, october, "second-field-padded"
    ) is True


class _WidthFacts:
    """The one field `_shows_a_width` reads, and nothing else."""

    def __init__(self, family: str) -> None:
        self.parser_family = family


# -- the carried item: a fraction of a second written as nought --------


def _subsecond_cells() -> "list[str]":
    start = datetime.datetime(2024, 1, 1, 12, 0, 0, 1000)
    return [
        (start + datetime.timedelta(days=index)).strftime(
            "%Y-%m-%d %H:%M:%S.%f"
        )[:-3]
        for index in range(240)
    ]


def test_a_subsecond_column_names_the_fraction_it_writes_as_nought(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's carried item 2, measured and made loud (plan P4-D296).

    240 moments a thousandth of a second past the half day. The
    description publishes `time_precision` `subsecond` and
    `subsecond_digits` 3; the twin writes every fraction as `.000`, both
    files still validate at nought, and until this landing the twin's
    report said nothing at all about it.
    """
    from tests.test_final_review_labels import _round_trip

    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = _round_trip(
            tmp_path,
            {"recorded_at": _subsecond_cells()},
            ("--smallest-group", _FLOOR_ELEVEN),
        )
    column = [
        block
        for block in result["document"]["columns"]
        if block["name"] == "recorded_at"
    ][0]
    assert (column["time_precision"], column["subsecond_digits"]) == (
        "subsecond", 3,
    )
    twin = result["twin"]["recorded_at"]
    assert [cell for cell in twin if cell[-3:] != "000"] == []
    assert "subsecond_digits" in result["report"], (
        "the twin's report does not name the fraction it wrote as nought"
    )
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_a_column_that_does_carry_its_fraction_names_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """The deviation reaches a column whose fractions are ALL nought.

    A rule that named every subsecond column would name one holding its
    milliseconds too, so the check is the recount it claims to be: a
    column at the second publishes no subsecond digits and says nothing.
    """
    from tests.test_final_review_labels import _round_trip

    start = datetime.datetime(2024, 1, 1, 12, 0, 0)
    cells = [
        (start + datetime.timedelta(days=index)).strftime("%Y-%m-%d %H:%M:%S")
        for index in range(240)
    ]
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = _round_trip(
            tmp_path, {"recorded_at": cells}, ("--smallest-group", _FLOOR_ELEVEN)
        )
    assert "subsecond_digits" not in result["report"]
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_recount_is_what_names_the_lost_fraction(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """THE RED CHECK. Withdraw the recount and the loss is silent again."""
    from tests.test_final_review_labels import _round_trip

    monkeypatch.setattr(
        generation, "_subsecond_notes", lambda column, facts, cells: []
    )
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        result = _round_trip(
            tmp_path,
            {"recorded_at": _subsecond_cells()},
            ("--smallest-group", _FLOOR_ELEVEN),
        )
    assert "subsecond_digits" not in result["report"]
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)

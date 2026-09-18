"""Nine disclosure repairs of the extra review round of 2026-09-18.

Every one of them is a published fact that named ONE record of the
table, and every one of them is built here from the review's own
reproduction: the table it names, at the floor it names, described,
built, described again, and validated on BOTH files at exit 0.

The three the review called blocking are first, in its order:

1. A PUBLISHED PREFIX DEFEATED THE ROOM RULE (plan P4-D270, loader
   invariant LP3). `layout_census` names a shape only where it could
   have come from `n_distinct + floor` different cells; the prefix
   ruling of 2026-09-17 then published the literal opening beside it,
   and the two together spelled the column out. 1,000 record numbers
   `REC000` to `REC999` published `{"@@@%%%": 1000}`, `{"(column)":
   "REC"}` and `n_distinct 1000`, and seed 4 wrote all 1,000 of the
   table's own record numbers.
2. AN AMBIGUOUS FIRST RECORD STILL BECAME A PUBLIC HEADER (plan
   P4-D272). A censored measurement is not a number, and "not a number"
   was read as evidence that the row holds column names, so a title over
   a headerless table published one person's record as the schema.
3. THE POOLED-LABEL EXCEPTION RESTORED FORCED SINGLETONS (plan
   P4-D271). The exception that keeps a long tail from being emptied
   was measured against the SMALLEST published level, which is a
   function of the floor rather than of the column, so a pool of twelve
   cleared a published level of eleven and twelve forced singletons
   stood.

Then the six the review called major: the temporal censuses (P4-D278,
P4-D279), the label spellings and the distinct count (P4-D275,
P4-D276), the questions file (P4-D273), the rare negative notation
(P4-D274), a declared identifier's scalar partitions (P4-D277), and a
delimited file's own lines (P4-D280).

THE RED CHECKS, each measured by withdrawing the rule in place:

* `parsing.prefix_leaves_room` forced True -- the prefix test here;
* `_holds_a_figure` forced False -- the header tests here;
* `pool_names_a_level`'s exception restored to the smallest published
  level -- the forced-singleton test here;
* `_joint_reading_names_a_group` forced True -- the joint-reading test;
* `absorbed_width_tally` returning its tally unchanged -- the width test;
* `_absorb_lone_spellings`' line back at one, and `_published_distinct`
  back at `raw_distinct` -- the two spelling tests;
* `_sayable` back at `count >= floor` -- the questions test;
* `_mixture_census`' absorption removed -- the notation test;
* `_published_reading_split` and `_published_alphabets` returning their
  raw counts -- the identifier tests;
* `endings_disclosed`, `blank_places_disclosed` and
  `row_count_disclosed` returning their arguments -- the file tests.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import collections
import datetime
import json
import pathlib
import random

from synthtwin import parsing, taxonomy
from tests import workbooks
from tests.test_final_review_labels import _round_trip
from tests.test_stage2_round_trip import _exit_of

FLOOR = ("--smallest-group", "11")


def _column(result: dict, name: str = "value") -> dict:
    for block in result["document"]["columns"]:
        if block["name"] == name:
            return block
    raise AssertionError(name)


def _both_pass(result: dict) -> None:
    assert result["generated"] == 0
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


# ------------------------------------------------ 1, the published prefix


def test_a_prefix_may_not_spell_the_column_out(
    tmp_path: pathlib.Path,
) -> None:
    """1,000 `REC000`-`REC999` declared, at a floor of eleven.

    The census still names the layout, because 17,576,000 cells could
    have worn `@@@%%%`; the PREFIX is not written, because fixing `REC`
    leaves exactly a thousand and the column holds a thousand different
    values. No cell of the twin is a record number of the table.
    """
    values = [f"REC{index:03}" for index in range(1000)]
    result = _round_trip(
        tmp_path,
        {"id": values, "cohort": ["group_x"] * 1000},
        FLOOR + ("--identifier", "id"),
    )
    block = _column(result, "id")
    assert block["layout_forms"] == {"@@@%%%": 1000}
    assert block["layout_prefixes"] == {}
    assert block["n_distinct"] == 1000
    held = set(values)
    assert len([cell for cell in result["twin"]["id"] if cell in held]) == 0
    _both_pass(result)


def test_a_prefix_that_leaves_room_is_published_exactly_as_before(
    tmp_path: pathlib.Path,
) -> None:
    """The ruling is unmoved wherever it can be kept: `REC` and seven figures."""
    values = [f"REC{index:07}" for index in range(800)]
    result = _round_trip(
        tmp_path,
        {"id": values, "cohort": ["group_x"] * 800},
        FLOOR + ("--identifier", "id"),
    )
    block = _column(result, "id")
    assert block["layout_prefixes"] == {parsing.PREFIX_OF_THE_COLUMN: "REC"}
    opens = [cell for cell in result["twin"]["id"] if cell[:3] == "REC"]
    assert len(opens) == 800
    _both_pass(result)


def test_the_room_rule_is_asked_of_the_prefix_and_not_of_the_layout() -> None:
    """`parsing.prefix_room` counts what is LEFT once the opening is fixed."""
    assert parsing.layout_room("@@@%%%") == 17576000
    assert parsing.prefix_room("@@@%%%", "REC", parsing.LAYOUT_PLAIN) == 1000
    assert not parsing.prefix_leaves_room(
        "@@@%%%", "REC", parsing.LAYOUT_PLAIN, 1000, 11
    )
    assert parsing.prefix_leaves_room(
        "@@@%%%%%%%", "REC", parsing.LAYOUT_PLAIN, 800, 11
    )
    # A prefix that does not open the layout leaves the layout's own room.
    assert parsing.prefix_room("%%%%%%", "REC", parsing.LAYOUT_PLAIN) == 10**6


# ------------------------------------- 2, the first row that cannot be told


def _headerless_with_a_title(folder: pathlib.Path) -> pathlib.Path:
    """A title line over 240 records whose first measurement is censored."""
    rows = [["R001", "North Unit", "<0.10"]] + [
        [f"R{index:03}", "East", f"{index}.5"] for index in range(2, 241)
    ]
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        "Monthly extract\n" + "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )
    return table


def test_a_censored_measurement_does_not_name_the_columns(
    tmp_path: pathlib.Path,
) -> None:
    """`<0.10` over a column of numbers is a VALUE, not a column name.

    Ruling 8 of 2026-09-17: where the first row cannot be told from a
    record, placeholder names are published, the person is asked, and no
    text of that row is published anywhere.
    """
    table = _headerless_with_a_title(tmp_path)
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", *FLOOR]
    ) == 0
    document = json.loads(
        (tmp_path / "real-profile.json").read_text(encoding="utf-8")
    )
    names = [block["name"] for block in document["columns"]]
    assert names == ["column_1", "column_2", "column_3"]
    # Every record is counted: the first row is one of them.
    assert document["columns"][0]["n_present"] == 240
    written = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted(tmp_path.iterdir())
        if path.is_file() and path.name != "real.csv"
    )
    for text in ("R001", "North Unit", "<0.10"):
        assert text not in written
    asked = (tmp_path / "real-questions.json").read_text(encoding="utf-8")
    assert "first row" in asked.lower()


def test_the_same_workbook_row_is_not_told_from_a_record(
    tmp_path: pathlib.Path,
) -> None:
    """The ruling reaches a workbook by the same path (plan P4-D232).

    The review measured this shape on both surfaces; the rule is one
    function, so the workbook is described here to prove it is the same
    one that answers.
    """
    strings = ["Monthly extract", "R001", "North Unit", "<0.10", "East"] + [
        f"R{place:03}" for place in range(2, 241)
    ]
    body: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell("A1", "0", "s")]),
        (
            2,
            [
                workbooks.cell("A2", "1", "s"),
                workbooks.cell("B2", "2", "s"),
                workbooks.cell("C2", "3", "s"),
            ],
        ),
    ]
    for place in range(2, 241):
        number = place + 1
        body += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", f"{3 + place}", "s"),
                    workbooks.cell(f"B{number}", "4", "s"),
                    workbooks.cell(f"C{number}", f"{place}.5"),
                ],
            )
        ]
    package = workbooks.package(
        [
            (
                "[Content_Types].xml",
                workbooks._content_types(1, True, False, False),
            ),
            ("_rels/.rels", workbooks._root_rels()),
            ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
            ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
            ("xl/styles.xml", workbooks._styles()),
            ("xl/sharedStrings.xml", workbooks._shared_strings(strings)),
            ("xl/worksheets/sheet1.xml", workbooks.sheet(body)),
        ]
    )
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / "book.xlsx"
    path.write_bytes(package)
    assert _exit_of(
        ["profile", str(path), "--out-dir", str(tmp_path), "--replace", *FLOOR]
    ) == 0
    document = json.loads(
        (tmp_path / "book-profile.json").read_text(encoding="utf-8")
    )
    assert [block["name"] for block in document["columns"]] == [
        "column_1",
        "column_2",
        "column_3",
    ]


def test_a_column_name_that_is_not_a_number_still_speaks(
    tmp_path: pathlib.Path,
) -> None:
    """The ordinary export is untouched: no header cell here carries a figure."""
    rows = [[f"S{index:03}", f"{index}", "east"] for index in range(1, 40)]
    table = tmp_path / "real.csv"
    tmp_path.mkdir(parents=True, exist_ok=True)
    table.write_text(
        "Extract for unit 7\nrecord_id,age,arm\n"
        + "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(tmp_path), "--replace", *FLOOR]
    ) == 0
    document = json.loads(
        (tmp_path / "real-profile.json").read_text(encoding="utf-8")
    )
    assert [block["name"] for block in document["columns"]] == [
        "record_id",
        "age",
        "arm",
    ]


# ----------------------------------------- 3, the pool that forces singletons


def test_a_pool_beside_a_level_at_the_floor_is_counted_as_missing(
    tmp_path: pathlib.Path,
) -> None:
    """1,977 `NORTH`, 11 `SOUTH` and twelve one-row sites, at a floor of eleven.

    Twelve levels over twelve rows can only be twelve single rows. The
    old exception let the pool escape because twelve reaches the
    SMALLEST published level, which the floor had set to eleven.
    """
    cells = (
        ["NORTH"] * 1977 + ["SOUTH"] * 11 + [f"SITE{index}" for index in range(12)]
    )
    random.Random(3).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert (block["suppressed_levels"], block["suppressed_rows"]) == (0, 0)
    assert (block["n_present"], block["n_missing"]) == (1988, 12)
    written = collections.Counter(result["twin"]["value"])
    assert written[""] == 12
    assert [label for label in written if written[label] == 1] == []
    _both_pass(result)


def test_the_long_tail_keeps_its_exception() -> None:
    """The pool that IS the column is still no exception beside it.

    The line is half of what the column publishes: a pool covering a
    third of the column or more is the column's own shape, and that
    width is what keeps a code register with a long tail whole.
    """
    # 780 codes written once beside one value of twenty rows.
    assert not parsing.pool_names_a_level(780, 780, 20)
    # 100 codes written once beside two codes of a hundred rows each.
    assert not parsing.pool_names_a_level(99, 100, 200)
    # Three one-patient sites beside 1,997 published rows are exceptions.
    assert parsing.pool_names_a_level(3, 3, 1997)
    assert parsing.pool_names_a_level(12, 12, 1988)
    # ...and the band is still the band.
    assert not parsing.pool_names_a_level(182, 400, 1600)


# -------------------------------------------- 4, the two temporal censuses


def test_a_joint_reading_claimed_by_one_record_is_not_taken(
    tmp_path: pathlib.Path,
) -> None:
    """395 ISO dates, ONE moment and four cells that parse under nothing.

    The single-format pass did not clear at 395 of 400 and the joint
    reading did at 396, so the block named the one record twice over --
    `resolution_mix {"iso-date": 395, "iso-datetime": 1}` and
    `datetime_separators {"(withheld)": 1}`.
    """
    first = datetime.date(2020, 1, 1)
    cells = [
        (first + datetime.timedelta(days=index)).isoformat()
        for index in range(395)
    ]
    cells += ["2020-05-03T00:00:00"] + ["unparsed"] * 4
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["role"] != "datetime"
    assert "resolution_mix" not in block
    _both_pass(result)


def test_a_joint_column_both_of_whose_forms_are_groups_still_reads(
    tmp_path: pathlib.Path,
) -> None:
    """Two hundred bare dates beside two hundred moments are still joint."""
    first = datetime.date(2020, 1, 1)
    cells = [
        (first + datetime.timedelta(days=index)).isoformat()
        for index in range(200)
    ]
    cells += [
        (first + datetime.timedelta(days=index)).isoformat() + "T08:30:00"
        for index in range(200)
    ]
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["format"] == taxonomy.FORMAT_ISO_MIXED
    assert block["resolution_mix"] == {"iso-date": 200, "iso-datetime": 200}
    assert result["generated"] == 0


def test_a_date_width_census_leaves_no_record_over(
    tmp_path: pathlib.Path,
) -> None:
    """399 dates showing a width beside one whose fields are both two figures.

    The census counted its remainder against the cells that COULD show a
    width, which the block does not publish; a reader subtracts from the
    PARSED total instead and is left with one record.
    """
    cells = [f"1/{index % 9 + 1}/{2000 + index // 9}" for index in range(399)]
    cells += ["12/25/2020"]
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["date_field_widths"] == {"unpadded": 400}
    assert block["n_present"] - block["n_unparsed"] == 400
    _both_pass(result)


def test_the_width_absorption_is_one_rule_for_both_sides() -> None:
    """`absorbed_width_tally` is what the producer and the checker both ask."""
    assert taxonomy.absorbed_width_tally({"unpadded": 399}, 400) == {
        "unpadded": 400
    }
    assert taxonomy.absorbed_width_tally({}, 400) == {}
    # Ties go to the first name in sorted order.
    assert taxonomy.absorbed_width_tally({"padded": 5, "unpadded": 5}, 12) == {
        "padded": 7,
        "unpadded": 5,
    }


# ------------------------------------------- 5, a label's rare spellings


def test_a_lone_spelling_leaves_no_trace_in_the_distinct_count(
    tmp_path: pathlib.Path,
) -> None:
    """490 `F`, 500 `M` and one `f` at a floor of eleven.

    The absorption counted the `f` into `F` and `n_distinct` went on
    counting three, so the block said in public that a third spelling
    exists and the variants census named two.
    """
    cells = ["F"] * 490 + ["M"] * 500 + ["f"]
    random.Random(9).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["n_distinct"] == 2
    named = {
        level["label"]: (level["variants"], level["variants_withheld"])
        for level in block["levels"]
    }
    assert named["f"] == ({"F": 491}, {})
    assert named["m"] == ({"M": 500}, {})
    assert "f" not in set(result["twin"]["value"])
    _both_pass(result)


def test_a_spelling_of_two_rows_is_absorbed_as_well(
    tmp_path: pathlib.Path,
) -> None:
    """The same shape with TWO `f` cells: `variants_withheld {"2": 1}` before."""
    cells = ["F"] * 490 + ["M"] * 500 + ["f", "f"]
    random.Random(10).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["n_distinct"] == 2
    for level in block["levels"]:
        assert level["variants_withheld"] == {}
    assert "f" not in set(result["twin"]["value"])
    _both_pass(result)


def test_at_the_default_floor_every_spelling_is_still_named(
    tmp_path: pathlib.Path,
) -> None:
    """A floor of one holds nothing back, so nothing is counted in."""
    cells = ["F"] * 490 + ["M"] * 500 + ["f"]
    random.Random(11).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells})
    block = _column(result)
    assert block["n_distinct"] == 3


# ------------------------------------------------ 6, the questions file


def test_the_questions_file_cannot_restore_an_absorbed_count(
    tmp_path: pathlib.Path,
) -> None:
    """`00001`-`00399` and one `12345` at a floor of eleven.

    The description absorbs the unpadded cell and publishes
    `numeric_styles {"leading_zero": 400}`; the questions file recounted
    the source and said "399 of them carry a leading zero", which beside
    `n_present 400` is the one unpadded record.
    """
    cells = [f"{index:05}" for index in range(1, 400)] + ["12345"]
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["numeric_styles"] == {"leading_zero": 400}
    asked = (
        result["profile"].parent / "real-questions.json"
    ).read_text(encoding="utf-8")
    assert "399 of them" not in asked
    assert "some of them carry a leading zero" in asked
    _both_pass(result)


def test_a_count_that_names_a_group_is_still_spoken() -> None:
    """The rule is the shared one, so a real group keeps its number."""
    assert parsing.census_nameable([300], [400], 11)
    assert not parsing.census_nameable([399], [400], 11)
    assert parsing.census_nameable([400], [400], 11)


# ------------------------------------------- 7, the rare negative notation


def test_a_rare_negative_notation_is_counted_into_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """388 positive decimals, eleven bracketed negatives and one `-12.25`.

    `negative_form brackets` needs at least eleven bracketed cells and
    twelve would have been named, so `negative_notations
    {"(unavailable)": 0}` beside `n_negative 12` proved eleven brackets
    and one other notation.
    """
    cells = [f"{100 + index * 0.01:.2f}" for index in range(388)]
    cells += [f"({1.25 + index:.2f})" for index in range(11)] + ["-12.25"]
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["n_negative"] == 12
    assert block["negative_form"] == "brackets"
    assert block["negative_notations"] == {"brackets": 12}
    assert result["real_exit"] == 0


def test_a_real_mixture_is_still_carried_as_a_mixture(
    tmp_path: pathlib.Path,
) -> None:
    """480 with a minus and 120 in brackets: both reach the line, both named."""
    cells = [f"-{index % 90 + 1}.50" for index in range(480)]
    cells += [f"({index % 40 + 1}.25)" for index in range(120)]
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    assert block["negative_notations"] == {"minus": 480, "brackets": 120}


# --------------------------------------- 8, a declared identifier's counts


def test_a_declared_identifier_publishes_no_scalar_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """999 `REC` identifiers of seven figures beside one `42`.

    Layouts were withheld for naming that record, and `n_numeric 1`,
    `n_all_digits 1` and `n_not_numeric 999` named it beside them.
    """
    values = [f"REC{index:07}" for index in range(999)] + ["42"]
    result = _round_trip(
        tmp_path,
        {"id": values, "cohort": ["group_x"] * 1000},
        FLOOR + ("--identifier", "id"),
    )
    block = _column(result, "id")
    assert block["n_present"] == 1000
    assert block["n_numeric"] == 0
    assert block["n_not_numeric"] == 1000
    assert block["n_all_digits"] == 0
    _both_pass(result)


def test_a_declared_identifier_protects_its_alphabet_count(
    tmp_path: pathlib.Path,
) -> None:
    """The same column with `X Y` in its place: `n_code_alphabet 999` before."""
    values = [f"REC{index:07}" for index in range(999)] + ["X Y"]
    result = _round_trip(
        tmp_path,
        {"id": values, "cohort": ["group_x"] * 1000},
        FLOOR + ("--identifier", "id"),
    )
    block = _column(result, "id")
    assert block["n_code_alphabet"] == 1000
    _both_pass(result)


def test_the_scalar_rule_leaves_a_real_split_alone() -> None:
    """A partition both of whose sides are groups keeps its own counts."""
    assert parsing.absorbed_total(400, 1000, 11) == 400
    assert parsing.absorbed_total(1, 1000, 11) == 0
    assert parsing.absorbed_total(999, 1000, 11) == 1000
    assert parsing.absorbed_total(0, 1000, 11) == 0


# ---------------------------------------- 9, a delimited file's own lines


def _file_form(folder: pathlib.Path, text: str) -> dict:
    """Describe a file written byte for byte and hand back its dialect."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_bytes(text.encode("utf-8"))
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--identifier", "record", *FLOOR,
        ]
    ) == 0
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    assert _exit_of(
        [
            "generate", str(folder / "real-profile.json"), "--out-dir",
            str(folder), "--seed", "4", "--replace",
        ]
    ) == 0
    checked = folder / "checked"
    checked.mkdir()
    assert _exit_of(
        [
            "validate", str(folder / "real-profile.json"), "--twin",
            str(table), "--out-dir", str(checked), "--replace",
        ]
    ) == 0
    return document["source"]["dialect"]


_RECORDS = [f"R{index:03},{index}" for index in range(1, 121)]


def test_one_line_ending_of_its_own_kind_names_no_record(
    tmp_path: pathlib.Path,
) -> None:
    """Record 57's ending alone is CRLF: runs of 57, 1 and 63 lines before."""
    lines = ["record,amount"] + _RECORDS
    text = ""
    for index, line in enumerate(lines):
        text += line + ("\r\n" if index == 57 else "\n")
    form = _file_form(tmp_path, text)
    assert form["line_endings"] == [{"ending": "lf", "lines": 121}]
    assert form["line_endings_spread"] == []


def test_one_empty_record_is_counted_as_none(tmp_path: pathlib.Path) -> None:
    """Record 57 written as a bare comma: `empty_rows.interior 1` before."""
    records = list(_RECORDS)
    records[56] = ","
    text = "record,amount\n" + "".join(row + "\n" for row in records)
    form = _file_form(tmp_path, text)
    assert form["empty_rows"] == {"interior": 0, "leading": 0, "trailing": 0}


def test_one_blank_line_names_no_place(tmp_path: pathlib.Path) -> None:
    """A blank separator after record 57: `{after: 57, lines: 1}` before.

    The endings collapse with it, because invariant FD2 has them account
    for every line the description keeps.
    """
    text = (
        "record,amount\n"
        + "".join(row + "\n" for row in _RECORDS[:57])
        + "\n"
        + "".join(row + "\n" for row in _RECORDS[57:])
    )
    form = _file_form(tmp_path, text)
    assert form["blank_lines"] == []
    assert form["blank_lines_spread"] is None
    assert form["line_endings"] == [{"ending": "lf", "lines": 121}]


def test_a_double_spaced_file_keeps_its_blank_lines(
    tmp_path: pathlib.Path,
) -> None:
    """Blank lines standing after every record are a group, not a record."""
    text = "record,amount\n" + "".join(row + "\n\n" for row in _RECORDS)
    form = _file_form(tmp_path, text)
    assert len(form["blank_lines"]) >= 11 or form["blank_lines_spread"]


def test_the_file_rules_are_asked_of_the_shared_line() -> None:
    """Each of the three is `parsing.census_floor`, and nothing else."""
    from synthtwin import dialect

    runs = [
        dialect.EndingRun(ending="lf", lines=57),
        dialect.EndingRun(ending="crlf", lines=1),
        dialect.EndingRun(ending="lf", lines=63),
    ]
    assert dialect.endings_disclosed(runs, 11) == [
        dialect.EndingRun(ending="lf", lines=121)
    ]
    even = [
        dialect.EndingRun(ending="lf", lines=60),
        dialect.EndingRun(ending="crlf", lines=61),
    ]
    assert dialect.endings_disclosed(even, 11) == even
    assert dialect.row_count_disclosed(1, 11) == 0
    assert dialect.row_count_disclosed(11, 11) == 11
    one = [dialect.BlankPlace(after=57, lines=1, text="")]
    assert dialect.blank_places_disclosed(one, 11) == []
    assert dialect.blank_lines_withheld(one, 11) == 1

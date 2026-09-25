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
P4-D279, superseded at the integration by the date pass's P4-D250,
which the plan records), the label spellings and the distinct count (P4-D275,
P4-D276), the questions file (P4-D273), the rare negative notation
(P4-D274), a declared identifier's scalar partitions (P4-D277), and a
delimited file's own lines (P4-D290).

THE RED CHECKS, each measured by withdrawing the rule in place:

* `parsing.prefix_leaves_room` forced True -- the prefix test here;
* `_holds_a_figure_as_a_value` forced False -- the header tests here;
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

AND FIVE MORE, from the repair pass of 2026-09-18, which measured what
those nine left open or broke. Their tests stand in their own section at
the foot of this file, and their red checks are:

* `_holds_a_figure_as_a_value` without its opening test -- the ordinary
  header that carries a figure loses its own names again;
* `pool_names_a_level` without its pinned-pool branch -- 120 lone sites
  beside 200 published rows publish a pool of one row a level again;
* `endings_disclosed` without its run loop -- a lone CRLF run stands
  again where the ending has companions elsewhere;
* the three `dialect` rules without their `floor <= 1` gate -- the
  default floor takes a file's lone blank line again;
* the label note back at "how many different spellings this column
  holds" -- the person is told a column of three spellings holds two.

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
# A floor of one is no longer the default (plan P4-D316): a test about
# what a floor of one keeps asks for it.
FLOOR_ONE = ("--smallest-group", "1")


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
    # AT THE POPULATION FLOOR (plan P4-D341): the command refuses a
    # smaller table and writes nothing, and what this pins is that a
    # title line above a real header leaves the header where it is.
    rows = [
        [f"S{index:03}", f"{index}", "east"]
        for index in range(1, parsing.POPULATION_FLOOR + 1)
    ]
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


def test_a_joint_reading_claimed_by_one_record_names_nobody(
    tmp_path: pathlib.Path,
) -> None:
    """395 ISO dates, ONE moment and four cells that parse under nothing.

    THE DEFECT THIS PINS IS UNCHANGED. The single-format pass did not
    clear at 395 of 400 and the joint reading did at 396, so the block
    named the one record twice over -- `resolution_mix {"iso-date": 395,
    "iso-datetime": 1}` and `datetime_separators {"(withheld)": 1}`.

    WHAT CLOSES IT CHANGED AT THE INTEGRATION of the extra round's four
    branches. This pass refused the joint READING (P4-D279); the date
    pass counts the rare form INTO the commonest one (P4-D250), which is
    the owner's sixth ruling of 2026-09-17 applied to this census. The
    two cannot both stand -- after the fold the reading is no longer
    joint, so the refusal is unreachable -- and the fold is what the
    integration kept, because it closes this exposure exactly as far and
    does not cost the column its role. Measured here: no census key of
    the block carries a count of one, and the 400 dates are still
    described as dates. The plan records the supersede under P4-D279.
    """
    first = datetime.date(2020, 1, 1)
    cells = [
        (first + datetime.timedelta(days=index)).isoformat()
        for index in range(395)
    ]
    cells += ["2020-05-03T00:00:00"] + ["unparsed"] * 4
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    block = _column(result)
    # NOTHING NAMES THE ONE RECORD: not the form census, not the census
    # of marks, and not any other census the block publishes.
    assert block["resolution_mix"] == {"iso-date": 396}
    assert block["datetime_separators"] == {}
    for key in sorted(block):
        value = block[key]
        if isinstance(value, dict):
            assert 1 not in [
                count for count in value.values() if isinstance(count, int)
            ], key
    # ...and the column is still read as what it is.
    assert block["role"] == "datetime"
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


def test_at_a_floor_of_one_every_spelling_is_still_named(
    tmp_path: pathlib.Path,
) -> None:
    """A floor of one holds nothing back, so nothing is counted in."""
    cells = ["F"] * 490 + ["M"] * 500 + ["f"]
    random.Random(11).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, FLOOR_ONE)
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

    AND THE TWIN OF THIS SHAPE MISSES ITS COLUMN'S MEAN AND SPREAD, which
    is the accepted limit of plan P4-D349 and not this repair coming
    undone. The 399 codes run consecutively, so each of the column's
    tails would hand its own cells back -- twelve DIFFERENT whole
    distances summing to the least twelve different whole numbers can sum
    to -- and the description publishes neither distance for either of
    them. The HIGH tail is where the single `12345` lives, and the
    column's mean is what that one cell puts in it: no reading of a tail
    that keeps the cell back can average to 230.3625, and three were
    measured. So the twin is checked here for exactly the two obligations
    that limit predicts and for nothing else going wrong beside them, and
    the REAL table still passes at exit 0 -- which is what says the
    description itself is still true of the table it was made from.
    Ledger entry `K-S3-15` holds the number.
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
    assert result["generated"] == 0
    assert result["real_exit"] == 0, (
        "the real table no longer meets its own description, which would "
        "be a defect of this pass and not the accepted limit"
    )
    assert result["twin_exit"] == 3, (
        "the twin of a column whose withheld tail carries its whole spread "
        "is expected to miss its mean and its spread (K-S3-15); exit 0 here "
        "means the limit closed and this expectation must be re-derived"
    )
    tails = block["tails"]
    assert isinstance(tails, dict)
    for side in ("low", "high"):
        assert tails[side]["mean_distance"] is None, (
            f"the {side} tail of 399 consecutive codes publishes no "
            f"distance, which is why the twin misses the two moments"
        )
    # THE QUALITY REPORT IS THE PAGE THAT NAMES THEM, and it is written
    # into the folder `validate` was pointed at rather than beside the
    # description, so it is read from there.
    quality = "".join(
        path.read_text(encoding="utf-8")
        for path in sorted((result["profile"].parent / "twin_exit").iterdir())
        if path.is_file() and path.suffix == ".txt"
    )
    verdicts = [
        line.strip() for line in quality.splitlines()
        if "MISSED" in line and "[" in line and "]" in line
    ]
    assert verdicts, "the quality report names no missed obligation at all"
    for line in verdicts:
        assert "moments.mean" in line or "moments.std" in line, (
            f"the twin misses something other than the two moments the "
            f"accepted limit predicts: {line}"
        )
    assert any("moments.mean" in line for line in verdicts)
    assert any("moments.std" in line for line in verdicts)


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


# ============================================================ THE REPAIR PASS
#
# The verification of this landing measured five things the nine repairs
# above left open or broke, each reproduced here from its own report and
# each with the rule withdrawn to prove the check goes red.
#
# * `_holds_a_figure_as_a_value` without its opening test -- the two
#   header tests below;
# * `pool_names_a_level` without its pinned-pool branch -- the two pool
#   tests below;
# * `endings_disclosed` without its run loop -- the ending test below;
# * the three `dialect` rules without their `floor <= 1` gate -- the
#   default-floor test below;
# * the label note back at "how many different spellings this column
#   holds" -- the note test below.


def _titled(folder: pathlib.Path, title: str, rows: "list[list[str]]") -> str:
    """One title line over a table, written byte for byte, then described."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        title + "\n" + "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", *FLOOR]
    ) == 0
    return (folder / "real-profile.json").read_text(encoding="utf-8")


def test_a_column_name_carrying_a_figure_still_names_its_column(
    tmp_path: pathlib.Path,
) -> None:
    """`q1,q2,q3,q4` and `subject,glucose1,week_2` under a title line.

    The first writing of P4-D272 refused the header evidence of ANY
    first-row value holding a figure, and a column name holds one often.
    Both headers were read correctly before that rule and lost after it:
    `column_1..` names, one record too many, and -- the header row having
    become a RECORD -- a fresh `n_not_numeric 1` in every numeric column.
    """
    draw = random.Random(7)
    answers = [
        [f"{draw.randint(1, 5)}" for _ in range(4)] for _ in range(300)
    ]
    document = json.loads(
        _titled(
            tmp_path / "survey",
            "Patient questionnaire export 2021",
            [["q1", "q2", "q3", "q4"]] + answers,
        )
    )
    assert [block["name"] for block in document["columns"]] == [
        "q1", "q2", "q3", "q4",
    ]
    assert document["n_rows"] == 300
    # No column carries the count of one the lost header made.
    for block in document["columns"]:
        assert block["n_not_numeric"] == 0

    people = [
        [f"S{index:03}", f"{draw.randint(40, 90) / 10:.1f}",
         f"{draw.randint(1, 9)}"]
        for index in range(240)
    ]
    clinic = json.loads(
        _titled(
            tmp_path / "clinic",
            "Diabetes cohort extract",
            [["subject", "glucose1", "week_2"]] + people,
        )
    )
    assert [block["name"] for block in clinic["columns"]] == [
        "subject", "glucose1", "week_2",
    ]
    assert clinic["n_rows"] == 240


def test_a_figure_counts_in_a_value_and_not_in_a_name() -> None:
    """The opening character is the whole of the difference (P4-D272).

    A measurement opens on a mark or on a figure; a column name opens on
    a letter, or on the one mark a name is written with. Stated here as
    well as measured above, because this one character is what keeps
    ruling 8's shape closed while an ordinary header stands.
    """
    from synthtwin import reading

    for value in ("<0.10", "2-4", "5 mg", "0.5", "-3", ".25", "12345"):
        assert reading._holds_a_figure_as_a_value(value)
    for name in ("q1", "week_2", "glucose1", "visit1", "B10", "_2021", ""):
        assert not reading._holds_a_figure_as_a_value(name)
    # And a name with no figure at all is no figure either way.
    for name in ("record_id", "age", "arm", "site", "reading"):
        assert not reading._holds_a_figure_as_a_value(name)


def _sites(published: int, held: int) -> "list[str]":
    """Two published labels over `published` rows, beside `held` lone sites."""
    half = published // 2
    cells = ["NORTH"] * half + ["SOUTH"] * (published - half) + [
        f"S{index:04}" for index in range(held)
    ]
    random.Random(9).shuffle(cells)
    return cells


def test_a_pool_of_one_row_a_level_is_read_at_every_width(
    tmp_path: pathlib.Path,
) -> None:
    """120 lone sites beside 200 published rows, and 700 beside 1,200.

    `suppressed_levels` equal to `suppressed_rows` is a count of ONE for
    every held-back level, read off two published numbers. The width
    P4-D271 set let both through, because 240 is not below 200 and 1,400
    is not below 1,200; the pinned pool is read by subtraction whatever
    the width says.
    """
    for folder, published, held in (
        ("small", 200, 120), ("large", 1200, 700),
    ):
        result = _round_trip(
            tmp_path / folder, {"value": _sites(published, held)}, FLOOR
        )
        block = _column(result)
        assert block["suppressed_levels"] == 0
        assert block["suppressed_rows"] == 0
        assert block["n_present"] == published
        assert block["n_missing"] == held
        blanks = [cell for cell in result["twin"]["value"] if cell == ""]
        assert len(blanks) == held
        lone = [
            cell for cell in result["twin"]["value"]
            if cell and cell not in ("north", "south", "NORTH", "SOUTH")
        ]
        assert lone == []
        _both_pass(result)


def test_a_long_tail_that_is_the_column_still_keeps_its_pool(
    tmp_path: pathlib.Path,
) -> None:
    """780 codes written once beside one value of twenty rows: the column.

    The second half of P4-D271 is kept whole. This pool is pinned too --
    780 levels over 780 rows -- and it covers MORE rows than the column
    publishes, so it is the column's own shape and not an exception
    beside it. Nothing is counted missing and every cell is written.
    """
    cells = [f"code-{index:05d}" for index in range(780)] + ["CODE-00999"] * 20
    result = _round_trip(
        tmp_path, {"value": cells}, ("--code", "value") + FLOOR
    )
    block = _column(result)
    assert (block["suppressed_levels"], block["suppressed_rows"]) == (780, 780)
    assert block["n_missing"] == 0
    assert [cell for cell in result["twin"]["value"] if cell == ""] == []
    _both_pass(result)


def test_the_pinned_pool_is_asked_before_the_width() -> None:
    """The rule, stated: pinned and below the published rows, or the band."""
    # Pinned, and smaller than what the column publishes.
    assert parsing.pool_names_a_level(120, 120, 200)
    assert parsing.pool_names_a_level(700, 700, 1200)
    assert parsing.pool_names_a_level(12, 12, 1988)
    # Pinned, and the column's own shape: the exception stands.
    assert not parsing.pool_names_a_level(780, 780, 20)
    assert not parsing.pool_names_a_level(3, 3, 3)
    # Not pinned at all: the width decides, exactly as before.
    assert not parsing.pool_names_a_level(99, 100, 200)
    assert not parsing.pool_names_a_level(182, 400, 500)


def test_a_rare_ending_s_run_names_no_record_among_its_companions(
    tmp_path: pathlib.Path,
) -> None:
    """Lines 0-20 CRLF AND record 57 CRLF: a run of one stood before.

    `endings_disclosed` read each ending's TOTAL over the file, so an
    ending with twenty companions elsewhere never tripped the rule and
    its lone run -- record 57's exact position -- was published.
    """
    lines = ["record,amount"] + _RECORDS
    text = ""
    for index, line in enumerate(lines):
        crlf = index <= 20 or index == 57
        text += line + ("\r\n" if crlf else "\n")
    form = _file_form(tmp_path, text)
    # LF is the commonest, at 99 lines against CRLF's 22.
    assert form["line_endings"] == [{"ending": "lf", "lines": 121}]
    assert form["line_endings_spread"] == []


def test_a_run_below_the_line_is_read_as_well_as_a_total() -> None:
    """The rule itself: a run shorter than the line collapses the file."""
    from synthtwin import dialect

    companions = [
        dialect.EndingRun(ending="crlf", lines=21),
        dialect.EndingRun(ending="lf", lines=36),
        dialect.EndingRun(ending="crlf", lines=1),
        dialect.EndingRun(ending="lf", lines=63),
    ]
    assert dialect.endings_disclosed(companions, 11) == [
        dialect.EndingRun(ending="lf", lines=121)
    ]
    # Every run at the line and every total at the line: published.
    even = [
        dialect.EndingRun(ending="lf", lines=60),
        dialect.EndingRun(ending="crlf", lines=61),
    ]
    assert dialect.endings_disclosed(even, 11) == even


def test_at_a_floor_of_one_a_file_keeps_its_own_form(
    tmp_path: pathlib.Path,
) -> None:
    """A floor of one keeps the file's own form (the gate of 2026-09-18).

    At that same floor the column censuses beside these three publish a
    level covering ONE row, so holding the file's form to a stricter
    standard took its lone blank line, its lone empty record and its lone
    rare ending out of the twin for nothing.
    """
    from synthtwin import dialect

    one_place = [dialect.BlankPlace(after=57, lines=1, text="")]
    assert dialect.blank_places_disclosed(one_place, 1) == one_place
    assert dialect.blank_lines_withheld(one_place, 1) == 0
    assert dialect.row_count_disclosed(1, 1) == 1
    runs = [
        dialect.EndingRun(ending="lf", lines=57),
        dialect.EndingRun(ending="crlf", lines=1),
        dialect.EndingRun(ending="lf", lines=63),
    ]
    assert dialect.endings_disclosed(runs, 1) == runs
    # ...and a raised floor is unmoved.
    assert dialect.blank_places_disclosed(one_place, 11) == []
    assert dialect.row_count_disclosed(1, 11) == 0

    folder = tmp_path / "floor-one"
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_bytes(
        (
            "record,amount\n"
            + "".join(row + "\n" for row in _RECORDS[:57])
            + "\n"
            + "".join(row + "\n" for row in _RECORDS[57:])
        ).encode("utf-8")
    )
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--identifier", "record",
        ]
        + list(FLOOR_ONE)
    ) == 0
    document = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )
    assert document["source"]["dialect"]["blank_lines"] == [
        {"after": 57, "lines": 1, "text": ""}
    ]


def test_the_report_says_what_the_distinct_count_means_on_a_label_column(
    tmp_path: pathlib.Path,
) -> None:
    """490 `F`, 500 `M` and one `f`: `n_distinct` is 2 and the note says so.

    P4-D276 changed what the count means on the four label roles, and the
    note printed to the person went on saying "how many different
    spellings this column holds" -- telling them a column of three
    spellings holds two.
    """
    cells = ["F"] * 490 + ["M"] * 500 + ["f"]
    random.Random(2).shuffle(cells)
    result = _round_trip(tmp_path, {"value": cells}, FLOOR)
    assert _column(result)["n_distinct"] == 2
    assert "how many different spellings this column holds" not in (
        result["report"]
    )
    assert (
        "how many different spellings this column's description speaks of"
        in result["report"]
    )
    _both_pass(result)


# ================================= THE FILES REVIEW OF 2026-09-18, ROUND 2
#
# Item 3 of that review: a LEGITIMATE HEADER became an additional record.
# P4-D272's opening test asked whether the first character stood in the
# ASCII alphabet, so every other character in the world opened a reading
# -- an accented letter and a leading space among them -- and the fifth
# record rule then read an ordinary header as one of its own records.
# The red check for the two tests below:
#
# * `_holds_a_figure_as_a_value` back at `opening in _SILHOUETTE_ALPHABET
#   or opening == "_"` on `text[0]` -- `échelle1` and ` q1` open a
#   reading again, the header becomes record 121, and every assertion
#   below about the names, the count and the fresh count of one fails.


_ROUND_TWO_GROUPS = ("alpha", "beta", "gamma")


def _round_two_rows() -> "list[list[str]]":
    """120 records: the numbers 1 to 120 beside three repeating groups."""
    return [
        [f"{number}", _ROUND_TWO_GROUPS[number % 3]]
        for number in range(1, 121)
    ]


def _headed_file(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]"
) -> dict:
    """One headed delimited file, written byte for byte, then described."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        "".join(",".join(row) + "\n" for row in [header] + rows),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace", *FLOOR]
    ) == 0
    return json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )


def _headed_book(
    folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]"
) -> dict:
    """The same header and records as a workbook, described the same way."""
    strings = list(header) + list(_ROUND_TWO_GROUPS)
    body: "list[tuple[int, list[str]]]" = [
        (
            1,
            [
                workbooks.cell("A1", "0", "s"),
                workbooks.cell("B1", "1", "s"),
            ],
        )
    ]
    for place in range(len(rows)):
        number = place + 2
        group = strings.index(rows[place][1])
        body += [
            (
                number,
                [
                    workbooks.cell(f"A{number}", rows[place][0]),
                    workbooks.cell(f"B{number}", f"{group}", "s"),
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
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "book.xlsx"
    path.write_bytes(package)
    assert _exit_of(
        ["profile", str(path), "--out-dir", str(folder), "--replace", *FLOOR]
    ) == 0
    return json.loads(
        (folder / "book-profile.json").read_text(encoding="utf-8")
    )


def test_a_header_outside_ascii_still_names_its_own_columns(
    tmp_path: pathlib.Path,
) -> None:
    """`échelle1,group` and ` q1,group` over 120 records, at a floor of eleven.

    Both were read correctly before P4-D272 was written. Afterwards both
    published `column_1` and `column_2`, described 121 records where the
    file holds 120, gave the numeric column a fresh `n_not_numeric 1`
    and counted the word `group` as one missing cell -- a count of one
    made by the landing that was closing them. The spelling is kept as
    the file wrote it, the leading space included.
    """
    rows = _round_two_rows()
    for folder, header in (
        ("accented", ["échelle1", "group"]),
        ("spaced", [" q1", "group"]),
    ):
        document = _headed_file(tmp_path / folder, header, rows)
        assert [
            block["name"] for block in document["columns"]
        ] == header, header
        assert document["n_rows"] == 120
        assert document["columns"][0]["n_not_numeric"] == 0
        assert document["columns"][1]["n_missing"] == 0
        assert document["columns"][1]["n_present"] == 120
        asked = json.loads(
            (tmp_path / folder / "real-questions.json").read_text(
                encoding="utf-8"
            )
        )
        assert "first row" not in json.dumps(asked).lower()


def test_the_same_header_names_its_columns_in_a_workbook(
    tmp_path: pathlib.Path,
) -> None:
    """The rule is one function, so the workbook is described here too.

    Item 3 of the review measured the shape on both surfaces. A workbook
    header of `échelle1` and `group` over the same 120 records lost its
    names exactly as the delimited file did.
    """
    rows = _round_two_rows()
    document = _headed_book(
        tmp_path / "book", ["échelle1", "group"], rows
    )
    assert [block["name"] for block in document["columns"]] == [
        "échelle1",
        "group",
    ]
    assert document["n_rows"] == 120
    assert document["columns"][0]["n_not_numeric"] == 0


def test_the_opening_of_a_reading_is_a_mark_and_not_merely_non_ascii() -> None:
    """The rule, stated: a reading opens on a figure or an enumerated mark.

    Everything else opens a NAME, which is every letter of every
    alphabet and the underscore -- and the opening is found past the
    spaces a file may write before a name.
    """
    from synthtwin import reading

    for value in (
        "<0.10", "2-4", "5 mg", "0.5", "-3", ".25", "12345",
        " <0.10", "≤0.10", "±0.5", "€20",
    ):
        assert reading._holds_a_figure_as_a_value(value), value
    for name in (
        "q1", "week_2", "glucose1", "visit1", "B10", "_2021", "",
        "échelle1", " q1", "\tq1", "ßand2", "ω1",
        "größe1", "año2",
    ):
        assert not reading._holds_a_figure_as_a_value(name), name


# Item 4 of that review: UNRELATED BLANK LINES defeated the suppression
# of a unique file-layout fact. `blank_places_disclosed` counted the
# places together, so eleven ordinary blank lines carried a twelfth
# place of another spelling past the line and published the sole record
# standing beside it. The red check for the three tests below:
#
# * `blank_places_disclosed` back at `len(places) >= line` with no form
#   loop -- `{after: 57, lines: 1, text: " "}` and `{after: 57, lines: 3,
#   text: ""}` are published again and the twin writes them back.


def _blank_file(
    folder: pathlib.Path, blanks: "dict[int, tuple[int, str]]"
) -> "tuple[dict, bytes]":
    """120 records with blank lines after the named ones: the form and the twin."""
    folder.mkdir(parents=True, exist_ok=True)
    written = "record,amount\n"
    for index in range(len(_RECORDS)):
        written += _RECORDS[index] + "\n"
        if index + 1 in blanks:
            lines, text = blanks[index + 1]
            for _ in range(lines):
                written += text + "\n"
    table = folder / "real.csv"
    table.write_bytes(written.encode("utf-8"))
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
    for name, checked in (("real.csv", "check-real"), ("real-twin.csv", "check-twin")):
        where = folder / checked
        where.mkdir()
        assert _exit_of(
            [
                "validate", str(folder / "real-profile.json"), "--twin",
                str(folder / name), "--out-dir", str(where), "--replace",
            ]
        ) == 0, name
    return (
        document["source"]["dialect"],
        (folder / "real-twin.csv").read_bytes(),
    )


def test_a_blank_line_spelled_like_no_other_names_no_record(
    tmp_path: pathlib.Path,
) -> None:
    """Blank lines after records 1-11 and ONE holding a space after 57.

    The twelve places cleared the count, so the spelling was never
    asked: `{after: 57, lines: 1, text: " "}` was published, the twin
    wrote that spaced line back, and both files validated at exit 0
    while the description named the one record standing beside it.
    """
    blanks: "dict[int, tuple[int, str]]" = {
        place: (1, "") for place in range(1, 12)
    }
    blanks[57] = (1, " ")
    form, twin = _blank_file(tmp_path, blanks)
    assert len(form["blank_lines"]) == 12
    assert [place["text"] for place in form["blank_lines"]] == [""] * 12
    assert {"after": 57, "lines": 1, "text": " "} not in form["blank_lines"]
    assert b"\n \n" not in twin
    # Every line is still accounted for: 122 of the file, 12 blank.
    assert form["line_endings"] == [{"ending": "lf", "lines": 133}]


def test_a_blank_run_longer_than_every_other_names_no_record(
    tmp_path: pathlib.Path,
) -> None:
    """The same shape in the other field: THREE blank lines after 57.

    A place publishes a form as well as a position, and a run length
    worn by one place names that place's record as surely as a spelling
    does. The two lines the absorbed run does not keep leave the ending
    count with them, so FD2 still holds.
    """
    blanks: "dict[int, tuple[int, str]]" = {
        place: (1, "") for place in range(1, 12)
    }
    blanks[57] = (3, "")
    form, _ = _blank_file(tmp_path, blanks)
    assert [place["lines"] for place in form["blank_lines"]] == [1] * 12
    assert {"after": 57, "lines": 3, "text": ""} not in form["blank_lines"]
    assert form["line_endings"] == [{"ending": "lf", "lines": 133}]


def test_the_blank_line_rule_is_asked_of_each_form() -> None:
    """The rule, stated: the line per form, and the commonest takes the rest."""
    from synthtwin import dialect

    ordinary = [
        dialect.BlankPlace(after=place, lines=1, text="")
        for place in range(1, 12)
    ]
    spaced = ordinary + [dialect.BlankPlace(after=57, lines=1, text=" ")]
    told = dialect.blank_places_disclosed(spaced, 11)
    assert told == ordinary + [dialect.BlankPlace(after=57, lines=1, text="")]
    assert dialect.blank_lines_withheld(spaced, 11) == 0
    # A longer run is a form of its own and counts into the commonest.
    longer = ordinary + [dialect.BlankPlace(after=57, lines=3, text="")]
    assert dialect.blank_places_disclosed(longer, 11) == ordinary + [
        dialect.BlankPlace(after=57, lines=1, text="")
    ]
    assert dialect.blank_lines_withheld(longer, 11) == 2
    # And the other way round: the absorbed form was the shorter one.
    threes = [
        dialect.BlankPlace(after=place, lines=3, text="")
        for place in range(1, 12)
    ]
    shorter = threes + [dialect.BlankPlace(after=57, lines=1, text="")]
    assert dialect.blank_places_disclosed(shorter, 11) == threes + [
        dialect.BlankPlace(after=57, lines=3, text="")
    ]
    assert dialect.blank_lines_withheld(shorter, 11) == -2
    # A form every place wears is published exactly as it stands.
    assert dialect.blank_places_disclosed(ordinary, 11) == ordinary
    assert dialect.blank_lines_withheld(ordinary, 11) == 0
    # Fewer places than the line: none at all, as before.
    assert dialect.blank_places_disclosed(ordinary[:3], 11) == []
    assert dialect.blank_lines_withheld(ordinary[:3], 11) == 3
    # At the default floor nothing moves.
    assert dialect.blank_places_disclosed(spaced, 1) == spaced
    assert dialect.blank_lines_withheld(spaced, 1) == 0


# ====================================== THE REPAIR PASS OF 2026-09-19
#
# The skeptic of the round-2 landing measured what P4-D310 left open.
# The enumeration it wrote holds the ASCII marks and a handful outside
# ASCII, so a reading opening on a mark it does NOT hold was read as a
# name -- and a headerless table's first record was published as the
# schema and written verbatim as the twin's header line. That is ruling
# 8 of 2026-09-17 reversed, reached through the door P4-D272 was written
# to shut. **Measured** on 240 headerless records at a floor of eleven,
# over nine spellings of the first record's reading: `05e7d89` read all
# nine as readings; P4-D310 as first written read FIVE of them as names
# (`＜0.10`, `\u00a0<0.10`, `\u00d710`, `\uff100.10`, `\u20325`), published `North Unit`
# and the reading itself as the column names, described 239 records
# where the file holds 240 and asked nothing.
#
# The red check for the two tests below:
#
# * `_READING_MARKS_OUTSIDE_ASCII` back at its P4-D310 spelling and
#   `_FULL_WIDTH_FIGURES`, `_FULL_WIDTH_READING_MARKS` and the spaces
#   outside ASCII in `_NAME_LEADING_SPACES` emptied -- the five
#   spellings publish the record as the schema again and both tests go
#   red.


_NINE_READINGS = (
    "<0.10",
    "\u22640.10",
    "\uff1c0.10",
    "\u00a0<0.10",
    "\u00d710",
    "\uff100.10",
    "\u20325",
    "0.10",
    "\u00b10.5",
)


def _headerless_two_columns(
    folder: pathlib.Path, reading_text: str
) -> pathlib.Path:
    """240 records whose first is `North Unit` beside one reading.

    No title line and no furniture: the fifth record rule is the only
    evidence there is, so what the first record's second value OPENS
    WITH decides whether ruling 8 is obeyed.
    """
    rows = [["North Unit", reading_text]] + [
        ["East", f"{index}.5"] for index in range(2, 241)
    ]
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        "".join(",".join(row) + "\n" for row in rows),
        encoding="utf-8",
        newline="",
    )
    return table


def test_a_record_opening_on_a_mark_outside_ascii_is_no_schema(
    tmp_path: pathlib.Path,
) -> None:
    """Nine spellings of one censored reading, each over 240 records.

    Every one of them is a value, so every one of them gets placeholder
    names, 240 records, the question about the first row, and no text of
    that record anywhere -- in the description, in the questions file,
    in the quality report or in the twin's own header line.
    """
    for place in range(len(_NINE_READINGS)):
        spelling = _NINE_READINGS[place]
        folder = tmp_path / f"case{place}"
        table = _headerless_two_columns(folder, spelling)
        assert _exit_of(
            [
                "profile", str(table), "--out-dir", str(folder),
                "--replace", *FLOOR,
            ]
        ) == 0
        document = json.loads(
            (folder / "real-profile.json").read_text(encoding="utf-8")
        )
        names = [block["name"] for block in document["columns"]]
        assert names == ["column_1", "column_2"], (spelling, names)
        # The first row is one of the records, so the file's own 240
        # records are all counted. (`North Unit` stands once, so the
        # label column counts it as absent under the floor -- ruling 4
        # of 2026-09-17 -- which is why its `n_present` is 239 here and
        # on 05e7d89 alike.)
        assert document["n_rows"] == 240, spelling
        assert document["columns"][0]["n_present"] == 239, spelling
        asked = (folder / "real-questions.json").read_text(encoding="utf-8")
        assert "first row" in asked.lower(), spelling
        assert _exit_of(
            [
                "generate", str(folder / "real-profile.json"),
                "--out-dir", str(folder), "--seed", "4", "--replace",
            ]
        ) == 0
        written = "".join(
            path.read_text(encoding="utf-8", errors="replace")
            for path in sorted(folder.iterdir())
            if path.is_file() and path.name != "real.csv"
        )
        for text in ("North Unit", spelling):
            assert text not in written, (spelling, text)


def test_a_reading_opens_on_the_marks_a_file_writes_a_number_with() -> None:
    """The enumeration, stated: four pieces, and every letter opens a name.

    The pieces are the ASCII marks but the underscore, the comparison,
    sign, currency and unit marks outside ASCII, the full-width figures
    and the full-width forms of those same ASCII marks but the
    full-width underscore. A value that has opened a reading carries its
    figures in whatever alphabet its file writes them.
    """
    from synthtwin import reading

    for value in (
        "<0.10", "2-4", "5 mg", "0.5", "-3", ".25", "12345",
        " <0.10", "\u22640.10", "\u00b10.5", "\u20ac20",
        "\uff1c0.10", "\uff1d5", "\uff1e9", "\uff100.10", "\uff11\uff12\uff10",
        "\u00d710", "\u00f72", "\u20325", "\u203311",
        "\u00a0<0.10", "\ufeff<0.10", "\u30005 mg", "\u202f2-4", "\u200b0.5",
    ):
        assert reading._holds_a_figure_as_a_value(value), repr(value)
    for name in (
        "q1", "week_2", "glucose1", "visit1", "B10", "_2021", "",
        "\u00e9chelle1", " q1", "\tq1", "\u00dfand2", "\u03c91",
        "gr\u00f6\u00dfe1", "a\u00f1o2",
        "\uff3fq1", "\uff3f2021", "\u00a0q1", "\u3000week_2", "North Unit",
    ):
        assert not reading._holds_a_figure_as_a_value(name), repr(name)
    # The four pieces are disjoint and the underscore stands in neither
    # alphabet's marks, which is what keeps `_2021` a name.
    assert "_" not in reading._READING_OPENINGS
    assert "\uff3f" not in reading._READING_OPENINGS
    for mark in ("\uff1c", "\uff10", "\u00d7", "\u2032"):
        assert mark in reading._READING_OPENINGS, repr(mark)
    for space in ("\u00a0", "\u3000", "\ufeff", "\u202f"):
        assert space in reading._NAME_LEADING_SPACES, repr(space)


# -- and what P4-D311 takes out of `bytes.blank-lines` (plan P4-D314) --
#
# The checked file is read by the absorption rule too, so the two sides
# of that obligation meet AFTER it. **Measured** on twelve ordinary
# blank places at a floor of eleven: at `05e7d89` a candidate whose
# twelfth place held one space, a tab, or three lines was MISSED at
# exit 3; each is HELD at exit 0 now. That is the ruling's price -- the
# check cannot see what the description is forbidden to publish -- and
# the price is now SAID, in the check's own sentence and in the
# `blank_lines` row of the contract. The red check for the test below:
#
# * the two lines that add `_BLANK_FORM_ABSORBED` to the sentences
#   removed -- the report no longer says what the comparison cannot
#   see, and the test goes red on every one of its four shapes.


def _twelve_places(text: str = "", lines: int = 1, after: int = 57) -> bytes:
    """120 records, eleven ordinary blank places and a twelfth of one form."""
    places = {}
    for place in range(1, 12):
        places[place * 4] = (1, "")
    places[after] = (lines, text)
    written = "record,site,reading\n"
    for index in range(1, 121):
        written += f"R{index:03},North,{index}.5\n"
        if index in places:
            count, holds = places[index]
            written += (holds + "\n") * count
    return written.encode("utf-8")


def _described_at(folder: pathlib.Path, floor: str) -> pathlib.Path:
    """The all-ordinary file, described at one floor."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_bytes(_twelve_places())
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--identifier", "record", "--smallest-group", floor,
        ]
    ) == 0
    return folder / "real-profile.json"


def _blank_check(
    folder: pathlib.Path, described: pathlib.Path, data: bytes
) -> "tuple[int, str, str]":
    """Validate one candidate: the exit code, the verdict, the sentence."""
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "other.csv"
    target.write_bytes(data)
    checked = folder / "checked"
    checked.mkdir()
    code = _exit_of(
        [
            "validate", str(described), "--twin", str(target),
            "--out-dir", str(checked), "--replace",
        ]
    )
    report = (checked / "other-quality.txt").read_text(encoding="utf-8")
    verdict = "not filed"
    sentence = ""
    lines = report.split("\n")
    for place in range(len(lines)):
        text = lines[place].strip()
        if text.startswith("bytes.blank-lines"):
            verdict = text.rpartition(": ")[2]
            sentence = lines[place + 2].strip()
    return code, verdict, sentence


_ABSORBED_CLAUSE = "is compared as the commonest form"


def test_the_check_says_a_rare_blank_form_is_compared_as_the_commonest(
    tmp_path: pathlib.Path,
) -> None:
    """`bytes.blank-lines` cannot see what P4-D311 forbids publishing.

    So the check's own sentence says so, on both sides, wherever the
    floor is above one -- and the obligation still bites on everything
    it can see: a place that MOVES is MISSED, and at the default floor
    nothing is absorbed and nothing is said.
    """
    described = _described_at(tmp_path / "eleven", "11")
    for label, data in (
        ("space", _twelve_places(text=" ")),
        ("tab", _twelve_places(text="\t")),
        ("three", _twelve_places(lines=3)),
        ("same", _twelve_places()),
    ):
        code, verdict, sentence = _blank_check(
            tmp_path / f"eleven-{label}", described, data
        )
        assert (code, verdict) == (0, "HELD"), (label, code, verdict)
        assert _ABSORBED_CLAUSE in sentence, (label, sentence)
    # The obligation still bites on a place that moved.
    code, verdict, sentence = _blank_check(
        tmp_path / "eleven-moved", described, _twelve_places(after=58)
    )
    assert (code, verdict) == (3, "MISSED")
    assert _ABSORBED_CLAUSE in sentence
    # At the default floor nothing is absorbed, so nothing is said and
    # the rare spelling is MISSED exactly as it was before P4-D311.
    plain = _described_at(tmp_path / "one", "1")
    code, verdict, sentence = _blank_check(
        tmp_path / "one-space", plain, _twelve_places(text=" ")
    )
    assert (code, verdict) == (3, "MISSED")
    assert _ABSORBED_CLAUSE not in sentence, sentence

"""P4-D454 (lane SH3): ages in other units and parts of an address under the Safe Harbor rule.

THE FINDING, measured on the base 867a3cd5 through the shipped command
(planning-notes wave6/SH3, the lane's leak table). An age counted in
MONTHS (0 to 1,300, a tenth at 1,080 or more) was read as a count: its
description published percentiles from 1,090 to 1,263 months, and its
twin wrote ages of 1,080 months or more. An age in WEEKS published p91 to
p98 past 4,695 weeks. An age in DAYS was read as ZIP codes and held
whole, its twin writing made-up numbers up to 99,956, every statistic
lost; answered `yes` it stayed held. An age in years answered `yes`, as a
truthful person answers, was held whole, its twin writing 999. A unit
word in the cell (`1100 months`) read the number in years, no age. Ages
past the mark on six rows published `90.0` as a tail value. House
numbers were read as a count and published their real values.

THE RULE (plan P4-D454; 45 CFR 164.514(b)(2)(i)(B) and (C)). An age is
read in the unit its cell writes (`14 months`, `3 d`, `100 y/o`,
`92-year-old`), else the unit its name states (`taxonomy.age_mark_named`:
`age` and a unit word read whole, `age_in_months`, `AgeDays`,
`months_old`), else the unit answered; with none stated it is read in
years, its strays past 125 whatever their share read 90, and its one
question offers years, months, weeks and days (lane SH3's repair, the
orchestrator's LANE SH3 RULINGS 2 (1)). A value at or past the MARK of
its unit -- 90 years, 1,080 months, 4,695 weeks, 32,871 days, each
rounded down from 90 years, and a decimal at or past 32,871 days in
years or months -- is read as the mark, published as `top_coded`, the
column's other statistics kept. The answer `yes` keeps the top-code
where a unit in the cells, the name or a unit answered establishes the
column as ages; on its values alone `yes` holds it whole (RULINGS 1
(1)); `no` lifts it. A top category fewer rows -- or people of a subject
column -- than the floor hold is pooled with the value below it, never
named, and the block records that rule (`top_category_pooled`), which
the validator follows; a block recording none is read as it was before
the repair. A name saying a house, building, flat, apartment, unit or
suite number or a post office box (`taxonomy.named_as_an_address_part`)
holds the column whole until the Safe Harbor question is answered `no`,
decided before any date or time reading, as lane SH2 holds a street, a
district or a county.

THE GATE: every form of `tests/age_address_shapes.py` at 600 rows,
unanswered and answered as a truthful person answers -- 0 values of 90
years or more published, 0 twin cells past the mark, 0 top categories of
1 to 10 rows named, 0 address-part values published, the Safe Harbor
question put to every age past the mark and every address part, none to
the columns named alike, and no age column held whole where the top-code
serves; one 20,000-row case through the shipped floor. The sweep at both
sizes is K-HZ-20's (`tools/measurements/kpi_ages_and_address_parts.py`,
under `kpi_run.py --slow`).
"""

from __future__ import annotations

import json
import pathlib
import random
import re
import sys

import pytest

from synthtwin import cli, contract, generation, parsing, profile, quality, reading, rendering, taxonomy, validation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import age_address_shapes as shapes  # noqa: E402
import fixtures  # noqa: E402

SMALL = 600
# The address parts a role publishing nothing describes: free text, no value
# published and no question needed (lane SH2's rule for places).
FREE_TEXT_PARTS = ("apt", "home_apt", "mail_apt", "apt_suite")
# The forms only K-HZ-20 runs at 20,000 rows, or the gate's one case there.
AT_THE_FLOOR_ONLY = ("units_at_the_floor", "ages_long_table")


def _measured(tmp_path: pathlib.Path, form: str, rows: int, answered: bool) -> "dict[str, dict[str, object]]":
    return shapes.measure(cli.main, tmp_path / f"{form}-{rows}-{answered}", form, rows, 0, answered)


def _asked_safe_harbor(one: "dict[str, object]") -> bool:
    asked = [f"{offered}" for offered in one["open"]] + [f"{given}" for given in one["answers"]]  # type: ignore[attr-defined]
    return any(offered.startswith("no/yes") for offered in asked) or any(
        given.split("=")[-1] in ("yes", "years", "months", "weeks", "days") for given in asked
    )


def _held_by_another_question(one: "dict[str, object]") -> bool:
    """Held as record numbers by an open question offering `identifier`: that question is the one put (P4-D401, one a column)."""
    return one["role"] == taxonomy.ROLE_IDENTIFIER and any(
        "identifier" in f"{offered}".split(" (")[0].split("/") for offered in one["open"]  # type: ignore[attr-defined]
    )


def _check(form: str, measured: "dict[str, dict[str, object]]", answered: bool, rows: int = SMALL) -> None:
    for column in shapes.FORMS[form]:
        one = measured[column.name]
        if column.kind == shapes.AGE:
            assert one["published_over"] == 0, (column.name, one)
            # A COLUMN AN OPEN QUESTION HOLDS IS READ AS ITS CELLS AND ITS
            # ANSWERS READ IT, ITS NAME SAYING NOTHING (the orchestrator's LANE
            # I4m RULINGS 21 (1), Codex's review of batch 4o, item 1: record
            # numbers named as ages were top-coded and their twin wrote real
            # keys): where its cells reach no ages it is held from them as they
            # are written, and its twin writes made-up values in lane ID-ROOM's
            # room, past the mark where its cells lie there, none of them real
            # (P4-D454's stated limit, as before lane SH3 on such a column).
            held_as_written = shapes.held_as_written(one)
            if held_as_written:
                assert one["twin_real"] == 0, (column.name, one)
            else:
                assert one["twin_over"] == 0, (column.name, one)
            if rows >= parsing.TABLE_ROW_FLOOR:
                # ...pooled at the table floor and above, the command's rule
                # (below it the command refuses the table).
                assert one["few_top_named"] == 0, (column.name, one)
            if one["real_over"]:
                # ...the question put (or another one offering `identifier`
                # holding the column meanwhile), and the top-code in the
                # column's unit.
                assert _asked_safe_harbor(one) or _held_by_another_question(one), (column.name, one)
                assert held_as_written or one["top_coded"] in contract.TOP_CODE_MARKS, (column.name, one)
            elif taxonomy.age_mark_named(column.name):
                # ...and none to ages younger than 90 in a stated unit, which
                # no ZIP hold takes either (G1).
                assert not _asked_safe_harbor(one), (column.name, one)
                assert one["role"] != taxonomy.ROLE_IDENTIFIER, (column.name, one)
            if answered:
                # ...and no whole hold where the top-code serves (G1).
                assert one["role"] != taxonomy.ROLE_IDENTIFIER, (column.name, one)
        elif column.kind == shapes.ADDRESS:
            assert one["published_real"] == 0, (column.name, one)
            if column.name not in FREE_TEXT_PARTS:
                assert _asked_safe_harbor(one) or _held_by_another_question(one), (column.name, one)
                assert one["role"] == taxonomy.ROLE_IDENTIFIER, (column.name, one)
            if (
                not answered
                and taxonomy.named_as_an_address_part(column.name)
                and column.name not in FREE_TEXT_PARTS
                and not _held_by_another_question(one)
            ):
                # ...its question saying what it is: a part of an address,
                # not a ZIP code (a house number of five figures).
                assert any("part of a street address" in f"{offered}" for offered in one["open"]), (column.name, one)  # type: ignore[attr-defined]
        elif column.kind == shapes.RECORD:
            # ...record numbers its values alone read as ages: `yes` holds
            # them whole, as before lane SH3, and no twin cell is a real one
            # (Codex's item 1; the orchestrator's LANE SH3 RULINGS 1 (1)).
            if answered:
                assert one["role"] == taxonomy.ROLE_IDENTIFIER, (column.name, one)
                assert one["published_real"] == 0 and one["twin_real"] == 0, (column.name, one)
        elif column.kind == shapes.PLAIN:
            assert not _asked_safe_harbor(one), (column.name, one)
            assert one.get("top_coded") is None, (column.name, one)


@pytest.mark.parametrize("answered", [False, True], ids=["unanswered", "answered"])
@pytest.mark.parametrize("form", sorted(form for form in shapes.FORMS if form not in AT_THE_FLOOR_ONLY))
def test_each_form_publishes_and_writes_no_age_past_the_mark_and_no_address_part(
    tmp_path: pathlib.Path, form: str, answered: bool
) -> None:
    measured = _measured(tmp_path, form, SMALL, answered)
    _check(form, measured, answered)
    if form == "ages_named":
        # ...`999` beside ages in months is 83 years, a value, never a
        # placeholder (skeptic 1's item 8): no cell of it is read absent.
        assert measured["age_mos_nines"]["n_missing"] == measured["age_mos_nines"]["real_missing"] == 0
    if form == "ages_named" and not answered:
        # ...and a column whose name states its unit is asked no unit
        # (Codex's item 7; RULINGS 1 (3)).
        for name in ("age_in_days", "age_in_months", "age (days)", "age_in_years", "years_old"):
            assert all(not offered.split(" (")[0].endswith("days") for offered in measured[name]["open"]), measured[name]  # type: ignore[attr-defined]


def test_at_the_table_floor_the_named_units_are_top_coded_answered(tmp_path: pathlib.Path) -> None:
    """One 20,000-row case through the shipped floor: months, weeks and days by name, answered truthfully, and a top category of 6 and 8 rows pooled, never named, the validator meeting the description it made (skeptic 1's item 7)."""
    measured = _measured(tmp_path, "units_at_the_floor", 20000, True)
    _check("units_at_the_floor", measured, True, 20000)
    assert measured["age_in_months"]["top_coded"] == 1080
    assert measured["age_in_weeks"]["top_coded"] == 4695
    assert measured["age_in_days"]["top_coded"] == 32871
    for name in ("age_years_few", "age_days_few"):
        assert 0 < measured[name]["real_over"] < 11 and measured[name]["few_top_named"] == 0, measured[name]
    assert measured["(table)"]["validate_exit"] == 0 and measured["(table)"]["misses"] == [], measured["(table)"]
    folder = tmp_path / "units_at_the_floor-20000-True"
    for name, block in shapes.blocks(folder).items():
        # ...the rule recorded on every top-coded block, pooled or not.
        assert block["top_category_pooled"] == 11, (name, block.get("top_category_pooled"))
    # ...and the summary says the pooling in words true of every such
    # column, naming no count (Codex's item 9).
    words = (folder / "t-profile.txt").read_text(encoding="utf-8")
    assert words.count("where fewer than 11 rows or people hold such values, they are read as the largest value below it instead") == 5, words


def test_a_top_category_few_people_hold_is_pooled_on_a_long_table(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 6: 4 patients aged 92 to 101 on 40 rows of 20,000, ten rows a patient: pooled in people, the column top-coded and kept, never held whole (the library's describe alone, at the table floor)."""
    table = shapes.write(tmp_path, "ages_long_table", 20000, 0)
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(read, taxonomy.Settings(), [], subjects=["person_key"], top_code=True)
    block = next(one for one in document["columns"] if one["name"] == "age")  # type: ignore[union-attr]
    assert block["role"] != taxonomy.ROLE_IDENTIFIER, block["role"]
    assert block["top_coded"] == 90 and block["top_category_pooled"] == 11, block
    assert block["top_category_people"] == ["person_key"], block
    column = shapes.FORMS["ages_long_table"][1]
    assert shapes.ages_published(block, column) == 0 and not shapes.top_named(block, column)


def _before_the_rule(tmp_path: pathlib.Path, name: str, cells: "list[str]") -> "tuple[dict, set[str]]":
    """A description as one written before lane SH3's repair (top-coded, recording no pooling rule), and the misses of its own table checked against it."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(tmp_path, "t.csv", fixtures.single_column_table(name, cells))
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(
        read, taxonomy.Settings(), [], top_coded_only={name: taxonomy.TOP_CODE}, top_pooled_only={}
    )
    described = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}")
    report = quality.quality_report(described, validation.measure(described, f"{table}"))
    block = next(one for one in document["columns"] if one["name"] == name)  # type: ignore[union-attr]
    return block, set(re.findall(r"^\s+(\S+) \[[^\]]+\]: MISSED", report, re.M))


def test_a_description_written_before_the_repair_validates_as_it_did(tmp_path: pathlib.Path) -> None:
    """Codex's item 4 (RULINGS 1 (2)): a top-coded block recording no `top_category_pooled` is read as it was made -- no pooling, no newer unit reading -- so its own table meets it."""
    # ...the reading before the repair, cell for cell as 867a3cd5's
    # `top_coded_cells` wrote these (unit words read as years, lane SH2's
    # letter factors, no age's affix, no decimal cut).
    cells = ["14 months", "1100 months", "33000 days", "4800 wks", "92 years", "104Y", "1100M", "4700W",
             "33000D", "100 months", "89.9986", "1079.98", "100 y/o", "92-year-old", "999", "95 yrs"]
    assert taxonomy.top_coded_cells_before_sh3(cells, False, frozenset()) == [
        "14 months", "1100 months", "33000 days", "4800 wks", "90 years", "90Y", "1080M", "4695W",
        "32872D", "90 months", "89.9986", "90.00", "100 y/o", "92-year-old", "999", "90 yrs",
    ]
    # ...19,994 ages of 88 and six of 95 at the table floor, top-coded
    # before the rule: binary, two values, nothing pooled, and its own
    # table meets it.
    block, misses = _before_the_rule(tmp_path / "binary", "age", ["88"] * 19994 + ["95"] * 6)
    assert "top_category_pooled" not in block and block["n_distinct"] == 2, block
    assert misses == set(), misses
    # ...and the validator's own reading of a checked file pools where the
    # block records the rule, and only there (skeptic 1's item 7: its
    # pooling floor set to 0 left the gate green).
    table = fixtures.write(tmp_path / "binary", "pooled.csv", fixtures.single_column_table("age", ["88"] * 30 + ["95"] * 3))
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    pooled = validation._top_coded_table(read, {"age": 90}, {"age": (11, ())}, [], (), ())
    assert pooled.columns[0] == ["88"] * 33, pooled.columns[0]
    as_made = validation._top_coded_table(read, {"age": 90}, {}, [], (), ())
    assert as_made.columns[0] == ["88"] * 30 + ["90"] * 3, as_made.columns[0]
    # ...and ages written with their unit in each cell, below the floor.
    draw = random.Random(454)
    written = [shapes.FORMS["ages_in_cells"][0].make(draw) for _cell in range(600)]
    block, misses = _before_the_rule(tmp_path / "cells", "age_written", written)
    assert misses == set(), misses


def test_the_unit_answered_inside_the_question_is_the_reading(tmp_path: pathlib.Path) -> None:
    """A column named `age` whose cells and name state no unit: read in years until answered (RULINGS 2 (1); the build's coarsest-unit reading withdrawn), its question offering the units; `days` answered reads it so."""
    unanswered = _measured(tmp_path, "ages_bare", SMALL, False)
    for name in ("age", "person_age", "infant_age"):
        assert unanswered[name]["top_coded"] == 90, unanswered[name]
        assert any(offered.startswith("no/yes/years/months/weeks/days") for offered in unanswered[name]["open"])  # type: ignore[attr-defined]
    answered = _measured(tmp_path, "ages_bare", SMALL, True)
    assert answered["infant_age"]["top_coded"] is None
    assert answered["infant_age"]["answers"][0] == "0:infant_age=days"  # type: ignore[index]
    assert answered["age"]["top_coded"] == 1080 and answered["person_age"]["top_coded"] == 32871


def test_each_mark_is_90_years_rounded_down_in_its_unit() -> None:
    assert taxonomy.AGE_MARKS == {"y": 90, "m": 1080, "w": 4695, "d": 32871}
    assert taxonomy.TOP_CODE_MARKS == contract.TOP_CODE_MARKS
    # 4,695 weeks are 32,865 to 32,871 days old, and 90 years hold at least
    # 90 times 365 and 21 days: both may be 90.
    assert 7 * 4695 + 6 >= 90 * 365 + 21 == 32871
    assert taxonomy.top_coded_cells(["4694", "4695", "6000"], mark=4695) == ["4694", "4695", "4695"]
    assert taxonomy.top_coded_cells(["32870", "32871", "40000", "99999"], mark=32871) == [
        "32870", "32871", "32871", "99999",
    ]
    assert taxonomy.top_coded_cells(["1079", "1080", "1300.5"], mark=1080) == ["1079", "1080", "1080.0"]
    # ...and a number in years is its own value, untouched by the unit's
    # arithmetic (0.03 times 90 over 90 is 0.030000000000000002).
    for written in ("0.03", "0.24", "89.99"):
        read = taxonomy.safe_harbor_number(written)
        assert read is not None and taxonomy._in_years(read) == float(written)
    read = taxonomy.safe_harbor_number("2160")
    assert read is not None and taxonomy._in_years(read, 1080) == 180.0


def test_a_unit_word_in_the_cell_is_read_with_it() -> None:
    cells = ["14 months", "1100 months", "3 d", "33000 days", "6 wk", "4800 wks", "92 years", "45 y", "126O"]
    assert taxonomy.top_coded_cells(cells) == [
        "14 months", "1080 months", "3 d", "32871 days", "6 wk", "4695 wks", "90 years", "45 y", "126O",
    ]
    ages = [f"{age} years" for age in range(18, 89)] * 3 + ["1100 months", "40 months", "300 days"]
    assert taxonomy.safe_harbor_reach(ages, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES


@pytest.mark.parametrize(
    "name, mark",
    [
        ("age_in_months", 1080), ("AgeMonths", 1080), ("age (days)", 32871), ("AGEDAYS", 32871),
        ("age_at_death_days", 32871), ("Age_Wks", 4695), ("ageinmonths", 1080), ("age_in_years", 90),
        ("age", 0), ("age_m", 0), ("ages_seen", 0), ("stage_days", 0), ("dosage_months", 0),
        ("age_years_months", 90),
        # ...and `old` after a unit word (skeptic 1's item 4).
        ("months_old", 1080), ("days_old", 32871), ("daysold", 32871), ("age_months_old", 1080),
        ("years_old", 90), ("weeks_old", 4695), ("old_months", 0), ("gold_days", 0),
    ],
)
def test_a_name_states_the_unit_of_its_ages(name: str, mark: int) -> None:
    assert taxonomy.age_mark_named(name) == mark


@pytest.mark.parametrize(
    "name, part",
    [
        ("house_no", True), ("HouseNum", True), ("home_house_no", True), ("unit_number", True),
        ("SuiteNum", True), ("apartment", True), ("home_apt", True), ("apt_no", True), ("apt", True),
        ("suite", True), ("unit", False), ("nursing_unit", False), ("patient_unit", False),
        ("unit_cost", False), ("insulin_units", False), ("household_size", False), ("apt_type", False),
        ("in_house", False),
        # ...and the names skeptic 1's items 5 and 8 found missed.
        ("hse_no", True), ("bldg_no", True), ("building_num", True), ("po_box", True), ("pobox", True),
        ("flat_no", True), ("apt_suite", True), ("unit_apt", True), ("aptsuite", True), ("housenum", True),
        ("AptNo", True), ("flat_rate", False), ("box_count", False), ("building", False),
        # ...and the names the verify's item 1 found missed: a street run
        # together with a number word, a box after the letters `p` and `o`,
        # a box beside an address word or a number word (RULINGS 4 (1));
        # `street` alone is lane SH2's.
        ("streetno", True), ("streetnum", True), ("streetnumber", True), ("streetnbr", True),
        ("p_o_box", True), ("P.O. Box", True), ("mail_box_no", True), ("mail_box", True), ("mailbox", True),
        ("box_number", True), ("streetwise", False), ("specimen_box", False), ("o_box", False),
        # ...and `street` alone, or beside a name word, stays lane SH2's (the verify 2's
        # observation 1, pinned at batch 4o's merge).
        ("street", False), ("street_name", False),
    ],
)
def test_a_name_says_a_part_of_an_address(name: str, part: bool) -> None:
    assert taxonomy.named_as_an_address_part(name) is part


@pytest.mark.parametrize("name", ["StreetNum", "street_number", "street_no", "addr_no", "address_number"])
def test_a_street_number_written_apart_is_lane_sh2s_place(name: str) -> None:
    """The verify of repair 1, item 1 (RULINGS 4 (1)): the camel-case and separated spellings stay held by lane SH2's place words."""
    assert taxonomy.named_as_a_place(name)


def test_an_age_affix_in_the_cell_is_its_unit() -> None:
    """Skeptic 1's item 1 (RULINGS 2 (2)): `N y/o`, `N m/o`, `N-year-old`, `N years old` are ages in their unit, on every route."""
    cells = ["100 y/o", "92-year-old", "1100 m/o", "9 m/o", "91 years old", "3 months old", "45 y.o.", "93 yo", "40000-day-old"]
    assert taxonomy.top_coded_cells(cells) == [
        "90 y/o", "90-year-old", "1080 m/o", "9 m/o", "90 years old", "3 months old", "45 y.o.", "90 yo", "32871-day-old",
    ]
    assert taxonomy.ages_written_with_units(["14 y/o", "95-year-old", "3"], False, frozenset())
    assert not taxonomy.ages_written_with_units(["14", "95", "3 y/o"], False, frozenset())


def test_years_stand_beside_strays_where_the_name_says_age() -> None:
    """Skeptic 1's item 2 (RULINGS 2 (1)): years beside a share of strays past 125 are reached where the name says age, whatever the share."""
    ages = [f"{18 + place % 88}" for place in range(880)] + [f"{126 + place * 23}" for place in range(80)]
    assert taxonomy.safe_harbor_reach(ages, False, frozenset(), 11) == ""
    assert taxonomy.safe_harbor_reach(ages, False, frozenset(), 11, named=True) == taxonomy.SAFE_HARBOR_AGES


def test_a_decimal_age_at_the_ninetieth_birthday_is_90() -> None:
    """Skeptic 1's item 9: 32,871 days are 89.9959 years and 1,079.95 months; a decimal at or past that cut is the mark."""
    assert taxonomy.top_coded_cells(["89.9986", "89.99", "89.9958"]) == ["90.0000", "89.99", "89.9958"]
    assert taxonomy.top_coded_cells(["1079.98", "1079.90"], mark=1080) == ["1080.00", "1079.90"]
    # ...and the twin's free value below 90 is never at or past the cut.
    assert taxonomy.at_most_the_top_code(["95.0000", "89.0000"]) == ["89.9958", "89.0000"]


def test_a_twin_writes_the_mark_in_the_cells_own_form_only_where_published() -> None:
    """Codex's items 2 and 6, and a drawn cell at the mark: the mark less one in the cell's own unit and decimals where no cell of that unit holds the mark, and no cell at the mark where the description publishes none."""
    assert taxonomy.at_most_the_top_code(["1079.50 months", "1100.00 months"]) == ["1079.50 months", "1079.00 months"]
    assert taxonomy.at_most_the_top_code(["1079.50", "1100.00"], frozenset(), 1080) == ["1079.50", "1079.00"]
    assert taxonomy.at_most_the_top_code(["32871", "33000", "100"], frozenset(), 32871, False, False) == ["32870", "32870", "100"]
    assert taxonomy.at_most_the_top_code(["32000", "33000", "100"], frozenset(), 32871, False, True) == ["32000", "32871", "100"]
    assert taxonomy.at_most_the_top_code(["90", "95", "88"], frozenset(), 90, False, False) == ["89", "89", "88"]


def test_a_held_column_named_as_ages_writes_no_age_past_the_mark() -> None:
    """Skeptic 1's item 10: a held age column's made-up `999` is written within the mark; a held column named otherwise keeps its room."""
    assert taxonomy.at_most_the_top_code(["999", "45", "9999"], frozenset(), 90, True) == ["009", "45", "0009"]
    assert taxonomy.at_most_the_top_code(["9999", "45"], frozenset(), 1080, True) == ["0279", "45"]
    assert taxonomy.at_most_the_top_code(["999", "45"], frozenset(), 90, False) == ["999", "45"]


def test_yes_on_values_alone_holds_the_column(tmp_path: pathlib.Path) -> None:
    """Codex's item 1 (RULINGS 1 (1)): record numbers 1 to 100 its values alone read as ages, answered `yes` and nothing else, are held whole as before lane SH3, never kept as a count of ages."""
    table = shapes.write(tmp_path, "record_numbers_like_ages", SMALL, 0)
    assert shapes.quiet(cli.main, ["profile", f"{table}", "--replace"], small_tables_refused=False) in (0, 3)
    questions = tmp_path / "t-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    answered = 0
    for entry in shapes._entries(document):
        if entry.get("column") == "register_entry" and "yes" in [choice.get("answer") for choice in entry["answers_you_can_give"]]:
            entry["your_answer"] = "yes"
            answered += 1
    assert answered == 1, document
    questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    assert shapes.quiet(
        cli.main, ["profile", f"{table}", "--replace", "--answers", f"{questions}"], small_tables_refused=False
    ) in (0, 3)
    assert shapes.blocks(tmp_path)["register_entry"]["role"] == taxonomy.ROLE_IDENTIFIER


def test_a_stated_unit_governs_the_answer_and_the_year_reading(tmp_path: pathlib.Path) -> None:
    """Codex's items 5 and 7 (RULINGS 1 (3)): the name's unit beats an answered one, and ages in days of 1900 to 1999 are no years of birth."""
    days = [f"{32000 + place * 13 % 4000}" for place in range(600)]
    (tmp_path / "answer").mkdir()
    (tmp_path / "years").mkdir()
    table = fixtures.write(tmp_path / "answer", "t.csv", fixtures.single_column_table("age_in_days", days))
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(read, taxonomy.Settings(), [], top_code=True, ages_counted_in={"age_in_days": 1080})
    assert document["columns"][0]["top_coded"] == 32871  # type: ignore[index]
    years = [f"{1900 + place % 100}" for place in range(600)]
    table = fixtures.write(tmp_path / "years", "t.csv", fixtures.single_column_table("age_in_days", years))
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(
        read, taxonomy.Settings(), [], [], ["age_in_days"], top_code=True,
        harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR,
    )
    assert "top_coded_year" not in document["columns"][0]  # type: ignore[operator]


def test_a_twin_past_the_mark_names_no_pooled_top_category() -> None:
    """Where no cell holds the mark, a cell drawn past it is written one below it; where the top category stands, as the mark."""
    assert taxonomy.at_most_the_top_code(["32000", "33000", "100"], frozenset(), 32871) == ["32000", "32870", "100"]
    assert taxonomy.at_most_the_top_code(["32871", "33000", "100"], frozenset(), 32871) == ["32871", "32871", "100"]
    # ...and in years, 90 itself only where a cell holds it.
    assert taxonomy.at_most_the_top_code(["91", "88"]) == ["89", "88"]
    assert taxonomy.at_most_the_top_code(["91", "90", "88"]) == ["89", "90", "88"]
    pooled = taxonomy.top_category_pooled(["95", "40", "88", "60", ""], False, frozenset({""}), 11)
    assert pooled == ["88", "40", "88", "60", ""]
    # ...in the column's unit, and nothing pooled with no floor (below the
    # table floor the command refuses the table).
    assert taxonomy.top_category_pooled(["33000", "100", "32000"], False, frozenset(), 11, 32871) == ["32000", "100", "32000"]
    assert taxonomy.top_category_pooled(["95", "40"], False, frozenset(), 0) == ["95", "40"]
    assert taxonomy.top_category_pooled(["95"] * 11 + ["40"], False, frozenset(), 11) == ["95"] * 11 + ["40"]


def test_a_label_twins_made_up_labels_past_the_mark_stay_labels_of_their_own() -> None:
    """The verify of repair 1, item 2: a label column's made-up labels past the mark are written below it, each a label of its own, never the top category."""
    cells = [f"{age}y" for age in range(10, 90)] + ["90y", "95y", "95y", "96y", "1080m", "1084m", "47m", "777Y", "NA"]
    assert taxonomy.at_most_the_top_code(cells, frozenset({"NA"}), 90, False, None, True)[80:] == [
        "90y", "99m", "99m", "98m", "1080m", "1079m", "47m", "999M", "NA",
    ]
    # ...where the column is no label column, as before: the largest free
    # value below 90, and 90 itself where none is free.
    assert taxonomy.at_most_the_top_code(cells, frozenset({"NA"}))[81:84] == ["9y", "9y", "8y"]
    every = [f"{age}y" for age in range(90)] + ["95y"]
    assert taxonomy.at_most_the_top_code(every)[90] == "90y"
    assert taxonomy.at_most_the_top_code(every, frozenset(), 90, False, None, True)[90] == "99m"


def test_the_top_category_written_at_several_widths_takes_the_narrowest_first() -> None:
    """The verify of repair 1, item 3: the top category a top-coded source wrote at two widths (`90.0` beside `90.00`) meets the width census; given whole at the widest, a group of 4 fit neither remainder."""
    holds = [90.0] * 4 + [12.34] * 2 + [45.6] * 4
    arguments = ({"1": 3, "2": 7}, ["decimal"] * 10, holds, [0, 1, 2, 3], {value: (value, value) for value in holds}, (12.34, 90.0), False)
    assert generation._width_places(*arguments) == [2, 2, 2, 2, 2, 2, -1, -1, -1, -1]
    assert generation._width_places(*arguments, (), 90.0) == [1, 1, 1, 2, 2, 2, 2, 2, 2, 2]


@pytest.mark.parametrize("form, name", [("ages_in_cells", "age_letter"), ("ages_decimal_and_events", "age_decimal")])
def test_a_top_coded_twin_meets_its_own_description_at_the_table_floor(tmp_path: pathlib.Path, form: str, name: str) -> None:
    """The verify of repair 1, items 2 and 3, at 20,000 rows (the library's describe and generate alone): the label column's levels and the decimal column's widths, met by its twin."""
    header, rows = shapes.build(form, 20000, 0)
    table = fixtures.write(tmp_path, "t.csv", fixtures.single_column_table(name, [row[header.index(name)] for row in rows]))
    read = reading.read_table(f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC)
    document = profile.build_document(read, taxonomy.Settings(), [], top_code=True)
    assert document["columns"][0]["top_coded"] == 90  # type: ignore[index]
    described = contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}")
    twin = tmp_path / "t-twin.csv"
    twin.write_text(rendering.twin_csv(generation.generate(described, 0)), encoding="utf-8", newline="\n")
    report = quality.quality_report(described, validation.measure(described, f"{twin}"))
    assert not re.findall(r"^\s+(\S+) \[[^\]]+\]: MISSED", report, re.M)


def test_the_summary_names_the_unit_of_a_top_coded_column(tmp_path: pathlib.Path) -> None:
    """The description publishes the mark, and its summary says the mark and its unit."""
    measured = _measured(tmp_path, "ages_named", SMALL, False)
    assert measured["age_in_days"]["top_coded"] == 32871
    words = (tmp_path / "ages_named-600-False" / "t-profile.txt").read_text(encoding="utf-8")
    assert "ages over 89, counted in days: every value from 32871 is read as 32871" in words
    assert "ages over 89: every value above 89 is read as 90" in words
    assert contract.TOP_CODE_MARKS == (90, 1080, 4695, 32871)


def _oracle() -> object:
    import importlib.util

    where = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("oracle_safe_harbor_units", where)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_oracle_writes_the_twin_of_every_unit_as_the_product_does() -> None:
    """A-P4-59 for method G7.14 as lane SH3 widens it: the oracle's `safe_harbor_ages_twin` and the product's `at_most_the_top_code` write the same cells, in every unit, by the column's mark and by the cell's own word."""
    import random

    oracle = _oracle()
    draw = random.Random(4542)
    for mark in contract.TOP_CODE_MARKS:
        # ...a held column named as ages, and the mark published or not
        # (lane SH3's repair), beside the cells' own reading.
        for held, published, labels in (
            (False, None, False), (True, None, False), (False, False, False), (False, True, False),
            # ...and a label column's made-up labels (lane SH3's second repair).
            (False, None, True), (False, False, True),
        ):
            for _column in range(60):
                cells: "list[str]" = []
                for _cell in range(draw.randint(1, 25)):
                    value = draw.choice([
                        f"{draw.randint(0, mark * 3 // 2)}", f"{draw.randint(mark - 3, mark + 3)}",
                        f"{round(draw.uniform(mark * 0.95, mark * 1.4), draw.randint(1, 2))}", f"{draw.randint(-20, 99999)}",
                        f"{draw.uniform(mark * 0.998, mark):.{draw.randint(1, 4)}f}",
                    ])
                    cells += [draw.choice(["", "0", "+"]) + value + draw.choice([
                        "", " months", " d", "wk", " years", "Y", "O", " y/o", "-year-old", " m/o", " months old", " yo",
                    ]) if draw.random() < 0.3 else value]
                assert taxonomy.at_most_the_top_code(cells, frozenset({"NA"}), mark, held, published, labels) == \
                    oracle.safe_harbor_ages_twin(cells, frozenset({"NA"}), mark, held, published, labels), (mark, cells)  # type: ignore[attr-defined]

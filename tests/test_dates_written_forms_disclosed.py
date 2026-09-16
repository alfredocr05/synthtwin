"""The written forms of a date column, published under the disclosure rule.

The review of the merged work at 158c811 found four defects in the
censuses landing 2b.6 added to say how a column's dates were WRITTEN, and
each is reproduced here from the reviewer's own shape, built by seeded
neutral code at runtime (plan D13), round-tripped end to end -- the real
table described, its twin generated, the twin described again, and BOTH
files validated with nothing missed.

1. A CENSUS NAMED ONE PERSON (plan P4-D131). 400 moments at noon, one of
   them written with a lower-case `z`: the default description published
   `zulu_case {"lower": 1, "upper": 399}`, and at a smallest group size of
   eleven `{"upper": 399, "(withheld)": 1}` -- two forms, one of them
   named, so the pool was the other form's count. Both loaded.
2. A WIDTH WORD SPENT ON A CELL WHOSE OTHER FIELD SHOWED (P4-D132). 400
   dates written `m/dd/yyyy` published `unpadded` for a cell whose day was
   past the ninth and `padded` for one whose month was, and the twin wrote
   those words on cells showing both fields: 106 of 400 twin cells were
   spelled `5/4/2024` or `08/28/2022`. At a floor of fifty the twin lost a
   published convention and missed two obligations the real table met.
3. MAY WAS COUNTED UNDER NO KEY (P4-D133). A column of `17-MAY-2024`
   published an empty name census, and its twin was written `25 May 2024`:
   `%d-%b-%Y` with upper-case months read 240 real cells and no twin cell.
4. MARKER CASES WERE CHECKED AS A SET (P4-D134). Eighty lower-case and 320
   upper-case zulu markers, every marker's case then reversed: the
   validator reported both obligations HELD.

THE RED CHECKS, each withdrawing one repair in a copy of the package and
run against this file: the disclosure rule (items 1 and the loader
tests), the per-field width words and the reservation (item 2), the
`either` length (item 3) and the exact comparison (item 4). The numbers
each turned red on are in the landing's own record.
"""

import datetime
import json
import pathlib
import random

import pytest

from synthtwin import contract, errors, generation, parsing
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip


def _noon_moments(lower: "set[int]") -> "list[str]":
    """400 daily moments at noon, a zulu marker on each, some lower case."""
    start = datetime.datetime(2024, 1, 1, 12)
    return [
        (start + datetime.timedelta(days=place)).strftime("%Y-%m-%dT%H:%M:%S")
        + ("z" if place in lower else "Z")
        for place in range(400)
    ]


def _described(
    folder: pathlib.Path, cells: "list[str]", flags: "tuple[str, ...]" = ()
) -> "tuple[pathlib.Path, dict]":
    """One column described by the real command; its path and its block."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    argv = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    assert _exit_of(argv + list(flags)) == 0
    written = folder / "real-profile.json"
    return written, json.loads(written.read_text(encoding="utf-8"))


def _refused(folder: pathlib.Path, document: dict, rule: str) -> None:
    """The document, written canonically, is refused under `rule`."""
    path = fixtures.write_profile(folder, "edited.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{path}")
    assert rule in str(raised.value) or contract.INVARIANTS[rule] in str(
        raised.value
    ), str(raised.value)[:400]


# -- 1. the disclosure rule, one statement for all four censuses --------


@pytest.mark.parametrize(
    "census, population, floor, published",
    [
        # A form of one row is never named, and a pool is never written.
        ({"lower": 1, "upper": 399}, 400, 1, {}),
        ({"lower": 1, "upper": 399}, 400, 11, {}),
        # One row left over is one row named by subtraction.
        ({"upper": 399}, 400, 1, {}),
        # Two forms both groups, or one form and the whole: published.
        ({"lower": 80, "upper": 320}, 400, 11, {"lower": 80, "upper": 320}),
        ({"upper": 400}, 400, 11, {"upper": 400}),
        # A form under the line dropped, the rest left over a group.
        ({"padded": 5, "unpadded": 90}, 400, 11, {"unpadded": 90}),
        # ...but not where what is left over is under the line.
        ({"padded": 5, "unpadded": 390}, 400, 11, {}),
    ],
)
def test_one_rule_decides_every_census_of_written_forms(
    census: "dict[str, int]",
    population: int,
    floor: int,
    published: "dict[str, int]",
) -> None:
    """`parsing.disclosed_census` and `census_discloses`, the one statement."""
    assert parsing.disclosed_census(census, population, floor) == published
    assert parsing.census_discloses(published, population, floor)
    if published != census:
        assert not parsing.census_discloses(census, population, floor)


@pytest.mark.parametrize("floor", ["1", "11"])
def test_one_lower_case_zulu_marker_is_named_nowhere(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """The reviewer's shape: the census is withheld whole, at both floors."""
    cells = _noon_moments({31})
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / floor, cells, ("--smallest-group", floor)
    )
    assert first["utc_offsets"] == {"Z": 400}
    assert first["zulu_case"] == {}
    # A census published as nothing asks the twin for nothing, and it
    # writes the one marker every row but one wrote.
    assert second["zulu_case"] == {"upper": 400}
    assert (twin_exit, real_exit) == (0, 0)


def test_one_lower_case_quarter_marker_is_named_nowhere(
    tmp_path: pathlib.Path,
) -> None:
    """The same rule on the quarter's marker, whose census is exhaustive too."""
    draw = random.Random(11)
    cells = [
        f"{2010 + draw.randrange(12)}-{'q' if place == 7 else 'Q'}"
        f"{draw.randrange(4) + 1}"
        for place in range(300)
    ]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "quarters", cells
    )
    assert first["format"] == "year-quarter"
    assert first["quarter_marker_case"] == {}
    assert (twin_exit, real_exit) == (0, 0)


def test_the_loader_refuses_every_census_that_names_one_row(
    tmp_path: pathlib.Path,
) -> None:
    """What the producer used to write is refused, on all four censuses."""
    _path, document = _described(tmp_path / "zulu", _noon_moments(set()))
    block = document["columns"][0]
    assert block["zulu_case"] == {"upper": 400}
    for census in (
        {"lower": 1, "upper": 399},
        {"upper": 399},
        {"(withheld)": 1, "upper": 399},
    ):
        edited = json.loads(json.dumps(document))
        edited["columns"][0]["zulu_case"] = census
        if "(withheld)" in census:
            path = fixtures.write_profile(tmp_path, "pooled.json", edited)
            with pytest.raises(errors.ProfileError):
                contract.load_profile(f"{path}")
            continue
        _refused(tmp_path, edited, "D20")
    # At a smallest group size of eleven, the pool the reviewer found.
    _path, strict = _described(
        tmp_path / "zulu-11", _noon_moments(set()), ("--smallest-group", "11")
    )
    strict["columns"][0]["zulu_case"] = {"(withheld)": 1, "upper": 399}
    path = fixtures.write_profile(tmp_path, "strict.json", strict)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(f"{path}")
    # The quarter's marker.
    draw = random.Random(3)
    quarters = [f"{2010 + draw.randrange(9)}-Q{draw.randrange(4) + 1}" for _ in range(200)]
    _path, document = _described(tmp_path / "quarter", quarters)
    assert document["columns"][0]["quarter_marker_case"] == {"upper": 200}
    document["columns"][0]["quarter_marker_case"] = {"upper": 199}
    _refused(tmp_path, document, "D19")
    # The field widths of a month-first column.
    days = [
        datetime.date(2022, 1, 1) + datetime.timedelta(days=place * 3)
        for place in range(200)
    ]
    _path, document = _described(
        tmp_path / "widths", [f"{day.month}/{day.day}/{day.year}" for day in days]
    )
    widths = document["columns"][0]["date_field_widths"]
    assert widths and all(count >= 2 for count in widths.values())
    named = sorted(widths)[0]
    document["columns"][0]["date_field_widths"] = dict(widths, **{named: 1})
    _refused(tmp_path, document, "D17")
    # The month names of a textual column.
    _path, document = _described(
        tmp_path / "names", [day.strftime("%d-%b-%Y").upper() for day in days]
    )
    names = document["columns"][0]["month_name_styles"]
    assert names
    document["columns"][0]["month_name_styles"] = dict(
        names, **{"lower-full-space-no-comma": 1}
    )
    _refused(tmp_path, document, "D18")


# -- 2. a width word says which field showed it --------------------------


def _month_unpadded_day_padded() -> "list[str]":
    """The reviewer's `m/dd/yyyy` column: 400 dates over 900 days."""
    draw = random.Random(4)
    start = datetime.date(2022, 1, 1)
    days = [start + datetime.timedelta(days=draw.randrange(900)) for _ in range(400)]
    return [f"{day.month}/{day.day:02d}/{day.year}" for day in days]


def _keeps_the_convention(cell: str) -> bool:
    month, day, _year = cell.split("/")
    return month == str(int(month)) and len(day) == 2


@pytest.mark.parametrize("floor", ["1", "50"])
def test_a_month_unpadded_day_padded_column_keeps_its_convention(
    tmp_path: pathlib.Path, floor: str
) -> None:
    """No twin cell pads the month or leaves the day bare, at either floor."""
    cells = _month_unpadded_day_padded()
    assert all(_keeps_the_convention(cell) for cell in cells)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / floor, cells, ("--smallest-group", floor)
    )
    assert first["format"] == "month-first-date"
    assert "second-padded" in first["date_field_widths"]
    assert "first-field-unpadded" in first["date_field_widths"]
    broken = [cell for cell in written if cell and not _keeps_the_convention(cell)]
    assert not broken, (len(broken), broken[:5])
    for name in first["date_field_widths"]:
        assert name in second["date_field_widths"], name
    assert (twin_exit, real_exit) == (0, 0)


def test_a_rare_published_width_is_given_its_floor_in_the_twin(
    tmp_path: pathlib.Path,
) -> None:
    """The reservation: a word published at the floor keeps the floor.

    Three per cent of 400 cells written `%m/%d/%Y` and the rest
    `m/d/yyyy`, at a smallest group size of six. The twin's own class of
    cells whose first field alone shows a width is smaller than the real
    column's, so a proportional share gives `first-field-padded` five cells
    against a published six and the twin misses it; reserved first, it
    holds.
    """
    draw = random.Random(2)
    start = datetime.date(2022, 1, 1)
    days = [start + datetime.timedelta(days=draw.randrange(900)) for _ in range(400)]
    cells = [
        day.strftime("%m/%d/%Y")
        if draw.random() < 0.03
        else f"{day.month}/{day.day}/{day.year}"
        for day in days
    ]
    first, second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "rare", cells, ("--smallest-group", "6")
    )
    assert first["date_field_widths"]["first-field-padded"] == 6
    assert second["date_field_widths"]["first-field-padded"] >= 6
    assert (twin_exit, real_exit) == (0, 0)


def test_the_reservation_gives_every_named_form_its_least() -> None:
    """`generation._reserved`, asked directly where the rotation falls short."""
    weights = {"a": 200, "b": 6}
    plain = generation._rotated(weights, 150)
    assert plain.count("b") < 6
    reserved = generation._reserved(weights, 150, 6)
    assert len(reserved) == 150
    assert reserved.count("b") == 6
    # Where the rotation already serves every form, it is the answer.
    assert generation._reserved(weights, 400, 6) == generation._rotated(weights, 400)


# -- 3. a name of May keeps its case, its mark and its comma --------------


def test_a_column_of_may_keeps_its_upper_case_and_hyphens(
    tmp_path: pathlib.Path,
) -> None:
    """The reviewer's shape: `%d-%b-%Y` reads every twin cell, upper case."""
    cells = [f"{place % 31 + 1:02d}-MAY-2024" for place in range(240)]
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "may", cells
    )
    assert first["month_name_styles"] == {"upper-either-hyphen-no-comma": 240}
    assert second["month_name_styles"] == first["month_name_styles"]
    for cell in written:
        datetime.datetime.strptime(cell, "%d-%b-%Y")
        assert cell == cell.upper(), cell
    assert (twin_exit, real_exit) == (0, 0)


def test_may_beside_other_months_writes_other_months_in_the_same_style(
    tmp_path: pathlib.Path,
) -> None:
    """Both classes: a name of May, and a name that shows its length."""
    draw = random.Random(9)
    start = datetime.date(2023, 1, 1)
    days = [start + datetime.timedelta(days=draw.randrange(700)) for _ in range(300)]
    cells = [day.strftime("%d-%b-%Y").upper() for day in days]
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "mixed", cells
    )
    assert sorted(first["month_name_styles"]) == [
        "upper-abbreviated-hyphen-no-comma",
        "upper-either-hyphen-no-comma",
    ]
    for cell in written:
        datetime.datetime.strptime(cell, "%d-%b-%Y")
        assert cell == cell.upper(), cell
    assert (twin_exit, real_exit) == (0, 0)


# -- 4. a marker's case is held count for count ---------------------------


def _reversed_markers(cells: "list[str]") -> "list[str]":
    flipped = {"z": "Z", "Z": "z", "q": "Q", "Q": "q"}
    turned: "list[str]" = []
    for cell in cells:
        if cell[-1] in ("z", "Z"):
            turned += [cell[:-1] + flipped[cell[-1]]]
        else:
            turned += [cell[:5] + flipped[cell[5]] + cell[6:]]
    return turned


def _validated(folder: pathlib.Path, description: pathlib.Path, cells: "list[str]") -> "tuple[int, str]":
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "checked.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    code = _exit_of(
        ["validate", str(description), "--twin", str(table), "--out-dir", str(folder), "--replace"]
    )
    return code, (folder / "checked-quality.txt").read_text(encoding="utf-8")


def test_reversed_zulu_marker_cases_are_missed(tmp_path: pathlib.Path) -> None:
    """80 lower and 320 upper, reversed without moving a timestamp."""
    cells = _noon_moments({place for place in range(400) if place % 5 == 0})
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "zulu", cells, ("--smallest-group", "11")
    )
    assert first["zulu_case"] == {"lower": 80, "upper": 320}
    assert (twin_exit, real_exit) == (0, 0)
    code, report = _validated(
        tmp_path / "reversed",
        tmp_path / "zulu" / "real-profile.json",
        _reversed_markers(cells),
    )
    assert code == 3
    assert "zulu.lower [datetime.zulu_case]: MISSED" in report
    assert "zulu.upper [datetime.zulu_case]: MISSED" in report


def test_reversed_quarter_marker_cases_are_missed(tmp_path: pathlib.Path) -> None:
    """The same on a column of quarters: every cell shows its marker.

    AND THE TWIN OF A MIXED COLUMN OF QUARTERS IS NOT ACCUSED ON ITS
    DISTINCT COUNT (plan P4-D137). `2024-Q1` and `2024-q1` are two
    different cells, and before the envelope counted written forms this
    column published 81 different values against an upper end of 48, so
    the twin missed an obligation it met and the table did not.
    """
    draw = random.Random(5)
    cells = [
        f"{2010 + draw.randrange(12)}-{'q' if place % 4 == 0 else 'Q'}"
        f"{draw.randrange(4) + 1}"
        for place in range(300)
    ]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "quarters", cells
    )
    assert first["quarter_marker_case"] == {"lower": 75, "upper": 225}
    assert (twin_exit, real_exit) == (0, 0)
    code, report = _validated(
        tmp_path / "reversed",
        tmp_path / "quarters" / "real-profile.json",
        _reversed_markers(cells),
    )
    assert code == 3
    assert "markers.lower [datetime.quarter_marker_case]: MISSED" in report

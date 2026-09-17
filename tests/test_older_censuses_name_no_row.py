"""The two older pooled censuses name no row (plan P4-D220).

`utc_offsets` and `datetime_separators` were the last censuses of a
column of dates that did not ask the one disclosure rule,
`parsing.census_nameable` with its line `parsing.census_floor`. Each named
a count where it reached the SETTINGS floor and pooled the rest, so
400 moments with one `t` published `{"lower_t": 1, "upper_t": 399}` at
the default floor of one and `{"upper_t": 399, "(withheld)": 1}` at a
floor of eleven, and both loaded. Stage 2 closed by the owner rulings of
2026-09-17 with this carried to the landing that repairs it.

THE GATE, held literally: a 400-row column with one `lower_t` cell,
described at floors one and eleven, built, described again, and both the
twin and the real table validated at exit 0 -- and the description names
nothing about that cell. "Names nothing" is measured, not read: the same
table with that one cell written with a SPACE instead gives a
byte-identical description, so no reader of the description can tell
which mark the row wore. The offsets are held to the same gate with one
row at `+01:00` among 399 at `Z`.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import datetime
import json
import pathlib

import pytest

from synthtwin import contract, errors, parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

ROWS = 400
LONE = 137


def _moments(mark: str = "T", suffix: str = "") -> "list[str]":
    """Four hundred moments seven hours apart, at no midnight, one mark each."""
    start = datetime.datetime(2024, 1, 1, 12, 5)
    return [
        (start + datetime.timedelta(hours=7 * place)).strftime(
            f"%Y-%m-%d{mark}%H:%M:%S"
        )
        + suffix
        for place in range(ROWS)
    ]


def _respelled(cells: "list[str]", mark: str) -> "list[str]":
    """The same cells with the one at `LONE` written with another mark."""
    made = list(cells)
    made[LONE] = made[LONE][:10] + mark + made[LONE][11:]
    return made


def _description_bytes(folder: pathlib.Path, cells: "list[str]", floor: int) -> str:
    """What `synthtwin profile` writes for a one-column table, as text."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        [
            "profile", str(table), "--out-dir", str(folder), "--replace",
            "--smallest-group", str(floor),
        ]
    ) == 0
    return (folder / "real-profile.json").read_text(encoding="utf-8")


@pytest.mark.parametrize("floor", [1, 11])
def test_one_lower_case_t_among_four_hundred_is_named_nowhere(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE for the marks: nothing published names the one `t`."""
    cells = _respelled(_moments(), "t")
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "lone-t", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["datetime_separators"] == {"(withheld)": ROWS}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert (twin_exit, real_exit) == (0, 0)
    # The twin still meets a space and a `t`, one value each.
    marks = [cell[10] for cell in written]
    assert (marks.count("t"), marks.count(" "), marks.count("T")) == (1, 1, ROWS - 2)
    # NAMES NOTHING, measured: the row written with a space instead of a
    # `t` gives the same description, byte for byte.
    as_t = _description_bytes(tmp_path / "as-t", cells, floor)
    as_space = _description_bytes(
        tmp_path / "as-space", _respelled(_moments(), " "), floor
    )
    assert as_t == as_space
    assert "lower_t" not in as_t


@pytest.mark.parametrize("floor", [1, 11])
def test_one_offset_among_four_hundred_is_named_nowhere(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE for the offsets: nothing published names the one `+01:00`.

    A pool beside `Z` below the line took `Z` in with it, so the map is
    one pool; the twin writes those values with no offset, as the report
    says, and both files meet the description.
    """
    cells = _moments(suffix="Z")
    cells[LONE] = cells[LONE][:-1] + "+01:00"
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "lone-offset", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["utc_offsets"] == {"(withheld)": ROWS}
    assert first["zulu_case"] == {}
    assert (twin_exit, real_exit) == (0, 0)
    text = json.dumps(first)
    assert "+01:00" not in text
    assert '"Z"' not in text


def test_offsets_below_the_line_beside_a_named_one_take_the_smallest_in() -> None:
    """The open vocabulary folds; the closed one pools whole (the producer's rule)."""
    offsets = {"+01:00": 300, "+02:00": 95, "+05:30": 5}
    assert parsing.pooled_census(offsets, 400, 11, False) == {
        "(withheld)": 100,
        "+01:00": 300,
    }
    assert parsing.pooled_census(offsets, 400, 1, False) == offsets
    # A pool that already reaches the line keeps every named offset.
    assert parsing.pooled_census(
        {"Z": 380, "+01:00": 7, "+02:00": 6, "-05:00": 7}, 400, 11, False
    ) == {"(withheld)": 20, "Z": 380}
    # The marks: one below the line pools every mark, at any floor.
    marks = {"upper_t": 870, "space": 22, "lower_t": 8}
    assert parsing.pooled_census(marks, 900, 20, True) == {"(withheld)": 900}
    assert parsing.pooled_census(marks, 900, 1, True) == marks
    assert parsing.pooled_census({"upper_t": 399, "lower_t": 1}, 400, 1, True) == {
        "(withheld)": 400
    }
    # And a column too short to name anything pools its whole total.
    assert parsing.pooled_census({"upper_t": 1}, 1, 1, True) == {"(withheld)": 1}
    assert parsing.pooled_census({}, 0, 1, True) == {}


def _loaded_with(
    tmp_path: pathlib.Path, floor: int, **fields: object
) -> "contract.Profile":
    """A real description of 400 moments at `Z`, one datetime field replaced."""
    text = _description_bytes(tmp_path / "base", _moments(suffix="Z"), floor)
    document = json.loads(text)
    for key in sorted(fields):
        document["columns"][0][key] = fields[key]
    written = fixtures.write_profile(tmp_path, "edited.json", document)
    return contract.load_profile(f"{written}")


def _refused_by(tmp_path: pathlib.Path, floor: int, rule: str, **fields: object) -> None:
    with pytest.raises(errors.ProfileError) as refused:
        _loaded_with(tmp_path, floor, **fields)
    assert f"it is called {rule} " in f"{refused.value}", f"{refused.value}"


def test_the_loader_names_no_count_of_one_at_a_floor_of_one(tmp_path: pathlib.Path) -> None:
    """D3 and D12 at a floor of one, where only the raise to two can refuse.

    At a floor of eleven the settings floor refuses a count of one first,
    so a battery written there cannot show the line of two working.
    """
    _refused_by(
        tmp_path / "mark", 1, "D12",
        datetime_separators={"lower_t": 1, "upper_t": 399},
    )
    _refused_by(
        tmp_path / "offset", 1, "D3",
        utc_offsets={"+01:00": 1, "Z": 399},
        latest_utc_offset="(withheld)",
        earliest_utc_offset="(withheld)",
        datetimes_read_at="utc",
        zulu_case={},
    )


def test_a_pool_beside_a_named_count_is_held_by_the_loader(tmp_path: pathlib.Path) -> None:
    """The pool of offsets reaches the line; the pool of marks stands alone."""
    _refused_by(
        tmp_path / "offset-pool", 1, "D3",
        utc_offsets={"(withheld)": 1, "Z": 399},
        datetimes_read_at="utc",
    )
    _refused_by(
        tmp_path / "mark-pool", 11, "D12",
        datetime_separators={"(withheld)": 30, "upper_t": 370},
    )
    # ...and at a floor of one a pool standing alone, or a pool of two
    # beside a named offset, is the rule working (S13 as amended).
    loaded = _loaded_with(
        tmp_path / "alone", 1,
        datetime_separators={"(withheld)": ROWS},
    )
    assert loaded.columns[0].name == "value"
    loaded = _loaded_with(
        tmp_path / "beside", 1,
        utc_offsets={"(withheld)": 2, "Z": 398},
        datetimes_read_at="utc",
        zulu_case={"upper": 398},
    )
    assert loaded.columns[0].name == "value"


def _built_at(tmp_path: pathlib.Path, floor: int) -> "dict[str, object]":
    """The producer's document of 400 moments at `Z`, before it is written."""
    table = fixtures.write(
        tmp_path,
        "moments.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in _moments(suffix="Z")]),
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(small_cell_floor=floor), []
    )
    assert isinstance(document, dict)
    return document


@pytest.mark.parametrize(
    "field, census",
    [
        ("datetime_separators", {"lower_t": 1, "upper_t": 399}),
        ("utc_offsets", {"+01:00": 1, "Z": 399}),
    ],
)
def test_the_publication_guard_names_no_count_of_one_at_a_floor_of_one(
    tmp_path: pathlib.Path, field: str, census: "dict[str, int]"
) -> None:
    """The half that WRITES says what D3 and D12 say, at the line of two."""
    document = _built_at(tmp_path, 1)
    profile.check_publication(document)
    columns = document["columns"]
    assert isinstance(columns, list)
    columns[0][field] = census
    with pytest.raises(errors.ProfileError) as refused:
        profile.check_publication(document)
    assert "before writing anything" in f"{refused.value}"


def test_the_publication_guard_lets_a_pool_stand_at_a_floor_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """S13 as amended, on the writing half: a pool here is the rule working."""
    document = _built_at(tmp_path, 1)
    columns = document["columns"]
    assert isinstance(columns, list)
    columns[0]["datetime_separators"] = {"(withheld)": ROWS}
    columns[0]["utc_offsets"] = {"(withheld)": 2, "Z": 398}
    profile.check_publication(document)

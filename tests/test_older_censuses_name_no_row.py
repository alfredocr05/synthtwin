"""The two older censuses of a column of dates name no row (plans P4-D220, P4-D222).

`utc_offsets` and `datetime_separators` were the last censuses of a
column of dates that did not ask the one disclosure rule,
`parsing.census_nameable` with its line `parsing.census_floor`. Each named
a count where it reached the SETTINGS floor and pooled the rest, so
400 moments with one `t` published `{"lower_t": 1, "upper_t": 399}` at
the default floor of one and `{"upper_t": 399, "(withheld)": 1}` at a
floor of eleven, and both loaded. Stage 2 closed by the owner rulings of
2026-09-17 with this carried to the landing that repairs it.

THE FIRST REPAIR (P4-D220) pooled what it could not name, and a pool below
the line took the commonest named count in with it, so ONE odd cell pooled
the whole census and the twin lost the column's own spelling: one `T` among
space-separated moments came back as `T` on nearly every row, and one `Z`
among `+01:00` and `+02:00` came back as half the column with no offset.
THE SECOND (P4-D222) counts a name below the line into the commonest named
count, as ruling 4 of 2026-09-17 counts missing-value words below a raised
floor as absent: the description is that of the table with its rare
spellings written the commonest way, the table passes it, and the twin
writes the column as its writer did.

THE GATE, held literally: a 400-row column with one `lower_t` cell,
described at floors one and eleven, built, described again, and both the
twin and the real table validated at exit 0 -- and the description names
nothing about that cell. "Names nothing" is measured, not read: the same
table with that one cell written with a SPACE instead gives a
byte-identical description. The offsets are held to the same gate with one
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


def _moments(mark: str = "T", suffix: str = "", rows: int = ROWS) -> "list[str]":
    """Moments seven hours apart, at no midnight, one mark each."""
    start = datetime.datetime(2024, 1, 1, 12, 5)
    return [
        (start + datetime.timedelta(hours=7 * place)).strftime(
            f"%Y-%m-%d{mark}%H:%M:%S"
        )
        + suffix
        for place in range(rows)
    ]


def _respelled(cells: "list[str]", mark: str, place: int = LONE) -> "list[str]":
    """The same cells with the one at ``place`` written with another mark."""
    made = list(cells)
    made[place] = made[place][:10] + mark + made[place][11:]
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
    assert first["datetime_separators"] == {"upper_t": ROWS}
    assert second["datetime_separators"] == first["datetime_separators"]
    assert (twin_exit, real_exit) == (0, 0)
    marks = [cell[10] for cell in written]
    assert marks.count("T") == ROWS
    # NAMES NOTHING, measured: the row written with a space instead of a
    # `t` gives the same description, byte for byte.
    as_t = _description_bytes(tmp_path / "as-t", cells, floor)
    as_space = _description_bytes(
        tmp_path / "as-space", _respelled(_moments(), " "), floor
    )
    assert as_t == as_space
    assert "lower_t" not in as_t


@pytest.mark.parametrize("floor", [1, 11])
def test_one_t_among_space_separated_moments_leaves_the_twin_its_spaces(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The final skeptic's second BLOCKER: one odd mark flipped the whole column.

    Measured on the first repair: 5,000 moments written with a space, one
    of them with `T`, published one pool and the twin wrote `T` on 4,998
    rows, so code parsing the twin's `%Y-%m-%dT%H:%M:%S` failed on every
    real row but one. Here 2,000 moments carry the same shape.
    """
    cells = _respelled(_moments(" ", rows=2000), "T", 11)
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "spaces", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["datetime_separators"] == {"space": 2000}
    assert (twin_exit, real_exit) == (0, 0)
    assert [cell[10] for cell in written].count(" ") == 2000


@pytest.mark.parametrize("floor", [1, 11])
def test_one_offset_among_four_hundred_is_named_nowhere(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """THE GATE for the offsets: nothing published names the one `+01:00`.

    The row is read as written at `Z`, the commonest offset, so the column
    is published on its local clock with both ends at `Z`, exactly as the
    same column with that row written at `-05:00` is.
    """
    cells = _moments(suffix="Z")
    cells[LONE] = cells[LONE][:-1] + "+01:00"
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "lone-offset", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["utc_offsets"] == {"Z": ROWS}
    assert first["datetimes_read_at"] == "local"
    assert first["zulu_case"] == {"upper": ROWS}
    assert (twin_exit, real_exit) == (0, 0)
    assert [cell[-1] for cell in written].count("Z") == ROWS
    as_written = _description_bytes(tmp_path / "plus-one", cells, floor)
    otherwise = list(cells)
    otherwise[LONE] = otherwise[LONE][:-6] + "-05:00"
    assert as_written == _description_bytes(tmp_path / "minus-five", otherwise, floor)
    assert "+01:00" not in as_written


@pytest.mark.parametrize("floor", [1, 11])
def test_one_z_among_two_offsets_keeps_every_twin_value_zoned(
    tmp_path: pathlib.Path, floor: int
) -> None:
    """The final skeptic's third BLOCKER: a folded pool was written with no offset.

    Measured on the first repair: 495 values at `+01:00`, 504 at `+02:00`
    and one at `Z` published `{"+02:00": 504, "(withheld)": 496}`, and the
    twin wrote 496 values with no offset at all.
    """
    cells = _moments(suffix="+01:00", rows=1000)
    for place in range(0, 1000, 2):
        cells[place] = cells[place][:-6] + "+02:00"
    cells[3] = cells[3][:-6] + "Z"
    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "two-offsets", cells, ("--smallest-group", f"{floor}"), True
    )
    assert first["utc_offsets"] == {"+01:00": 499, "+02:00": 501}
    assert (twin_exit, real_exit) == (0, 0)
    zoned = [cell for cell in written if cell[-6:] in ("+01:00", "+02:00")]
    assert len(zoned) == 1000


def test_two_single_rows_below_the_line_are_counted_into_the_commonest_offset(
    tmp_path: pathlib.Path,
) -> None:
    """The final skeptic's sixth finding: two offsets of one row beside named ones.

    At a floor of one, `-05:00` and `Z` each carried by one row are counted
    into `+01:00`; `+02:00`, carried by 95, keeps its own count.
    """
    assert parsing.absorbed_census(
        {"+01:00": 300, "+02:00": 95, "-05:00": 1, "Z": 1}, 397, 1, 0
    ) == {"+01:00": 302, "+02:00": 95}
    cells = _moments(suffix="+01:00", rows=397)
    for place in range(0, 95 * 4, 4):
        cells[place] = cells[place][:-6] + "+02:00"
    cells[1] = cells[1][:-6] + "-05:00"
    cells[2] = cells[2][:-6] + "Z"
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "two-singles", cells, ("--smallest-group", "1"), True
    )
    assert first["utc_offsets"] == {"+01:00": 302, "+02:00": 95}
    assert (twin_exit, real_exit) == (0, 0)


def test_the_producer_rule_counts_rare_names_into_the_commonest() -> None:
    """`parsing.absorbed_census` and `parsing.census_pools`, read off directly."""
    offsets = {"+01:00": 300, "+02:00": 95, "+05:30": 5}
    assert parsing.absorbed_census(offsets, 400, 11, 0) == {
        "+01:00": 305,
        "+02:00": 95,
    }
    assert parsing.absorbed_census(offsets, 400, 1, 0) == offsets
    marks = {"upper_t": 870, "space": 22, "lower_t": 8}
    assert parsing.absorbed_census(marks, 900, 20, 3, "upper_t") == {
        "space": 22,
        "upper_t": 878,
    }
    assert parsing.absorbed_census(marks, 900, 1, 3, "upper_t") == marks
    # No name at the line: a pool, where a pool says no name was written...
    assert parsing.absorbed_census(
        {"space": 6, "lower_t": 6}, 12, 11, 3, "upper_t"
    ) == {"(withheld)": 12}
    # ...and ONE NAME THE CELLS WROTE over the band where a pool would
    # say every mark was written: eight of each of three marks at a floor
    # of eleven. It was the vocabulary's DEFAULT until plan P4-D242,
    # which measured that publishing a mark NO cell of the column wore --
    # twelve spaces and twelve lower-case `t` published `upper_t` for all
    # of them. Ties go to the first name in sorted order, which is the
    # rule the commonest named count above is chosen by.
    assert not parsing.census_pools(24, 11, 3)
    assert parsing.absorbed_census(
        {"space": 8, "lower_t": 8, "upper_t": 8}, 24, 11, 3, "upper_t"
    ) == {"lower_t": 24}
    assert parsing.absorbed_census(
        {"space": 12, "lower_t": 9}, 21, 11, 3, "upper_t"
    ) == {"space": 21}
    assert parsing.census_pools(24, 11, 0)
    assert parsing.absorbed_census({"upper_t": 1}, 1, 1, 3, "upper_t") == {
        "(withheld)": 1
    }
    assert parsing.absorbed_census({}, 0, 1, 3, "upper_t") == {}


def test_a_short_column_whose_offsets_pool_says_no_clock_and_no_end(
    tmp_path: pathlib.Path,
) -> None:
    """Beside a pool of offsets the clock and the ends say nothing either.

    Eight values at `+01:00` at a floor of eleven, and the same eight with
    one at `Z`: both pool the offsets, and the local clock and the named
    ends used to tell the one column from the other.
    """
    cells = _moments(suffix="+01:00", rows=8)
    one = json.loads(_description_bytes(tmp_path / "one", cells, 11))
    other = list(cells)
    other[5] = other[5][:-6] + "Z"
    two = json.loads(_description_bytes(tmp_path / "other", other, 11))
    for key in (
        "utc_offsets", "datetimes_read_at", "earliest_utc_offset", "latest_utc_offset"
    ):
        assert one["columns"][0][key] == two["columns"][0][key], key
    column = one["columns"][0]
    assert column["utc_offsets"] == {"(withheld)": 8}
    assert column["datetimes_read_at"] == "utc"
    assert column["earliest_utc_offset"] == "(withheld)"
    # ...AND A NAIVE END IS HELD BACK TOO: eight values with no offset,
    # one of them written at `Z`, publish the same ends as eight with none.
    naive = _moments(rows=8)
    zoned = list(naive)
    zoned[3] = zoned[3] + "Z"
    ends = [
        json.loads(_description_bytes(tmp_path / name, cells, 11))["columns"][0]
        for name, cells in (("naive", naive), ("zoned", zoned))
    ]
    for column in ends:
        assert column["earliest_utc_offset"] == "(withheld)", column
        assert column["latest_utc_offset"] == "(withheld)", column


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
    """D3 and D12 at a floor of one, where only the raise to two can refuse."""
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


def test_a_pool_stands_only_alone_and_only_where_it_names_no_one(
    tmp_path: pathlib.Path,
) -> None:
    """D3 and D12: no pool beside a named count, and no pool of every mark."""
    _refused_by(
        tmp_path / "offset-pool", 11, "D3",
        utc_offsets={"(withheld)": 30, "Z": 370},
        datetimes_read_at="utc",
        zulu_case={},
    )
    _refused_by(
        tmp_path / "mark-pool", 11, "D12",
        datetime_separators={"(withheld)": 30, "upper_t": 370},
    )
    # A pool of all 400 marks at a floor of one would say each of the three
    # was written: the producer names the commonest mark there.
    _refused_by(
        tmp_path / "every-mark", 1, "D12",
        datetime_separators={"(withheld)": ROWS},
    )
    # ...and a pool of offsets standing alone loads (S13 as amended).
    loaded = _loaded_with(
        tmp_path / "alone", 1,
        utc_offsets={"(withheld)": ROWS},
        earliest_utc_offset="(withheld)",
        latest_utc_offset="(withheld)",
        datetimes_read_at="utc",
        zulu_case={},
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
    columns[0]["utc_offsets"] = {"(withheld)": ROWS}
    profile.check_publication(document)

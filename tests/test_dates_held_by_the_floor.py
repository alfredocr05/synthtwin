"""P4-D433 (lane PS2): every published date held by the floor, in people or else in rows.

THE DEFECT (lane E0c's leak scan, `kpi_run.py --slow --only 'K-HZ-*'` on
93d57414). Lane PS (plan P4-D417) pools a column of dates beside a person
column whose people have several rows; a table of ONE ROW A PERSON, or of
NO PERSON COLUMN, published day-grain dates that one to ten people or rows
hold: the zoo's `patients.csv` printed 11 real birth dates (`dob_iso`'s
date percentiles p05 to p95 and both tail boundaries, each one person's
date) at 20,000 rows, and lane E0c's `phi_registry.csv` 40 (`birth_date`,
which no question flags). A full birth date is a HIPAA identifier element.

THE RULE. Where no subject column beside a column of dates counts it in
people, each ROW is its own holder: every date the description publishes
-- a percentile, a tail boundary or value, a mode, a heavy date, a census
entry -- is read as the calendar day it names (its month or quarter where
it names only that), and one that one to ten rows fall on sends the column
down lane PS's ladder (day, month, quarter, year), each row a holder, or
holds it with valid made-up dates in its own layouts where no grain serves
(`profile._dates_few_in_rows`, `profile.rows_as_holders`). On a table of
one row a person a row IS a person. A column whose every published day the
floor's rows already hold keeps its bytes -- the dense admission day stays
at the day, a stamp to the minute keeps its time of day -- and a column a
subject column counts in people is counted as lane PS counts it.

THE GATE, at 20,000 and 200,000 rows (the owner's table floor and ten times
it), every table through the zoo's own path (profile, the general answers,
profile --answers): the sweep's birth dates over seventy years, death
dates, sparse event dates and dense admission days on one row a person,
several rows a person and no person column, and lane E0c's two exposures;
0 real dates of one to ten people or rows published (`dates_held.
dates_held_few`, written apart from the product's count), the dense
columns' bytes pinned to the base's (ccebc947), the twins valid. Red on
the mutants of `wave6/PS2/mut_ps2.py` (`mutants.log`).
"""

from __future__ import annotations

import contextlib
import datetime
import hashlib
import io
import json
import pathlib

import pytest

from synthtwin import cli, contract, parsing, profile, taxonomy, validation

import dates_held

SIZES = (20000, 200000)


@pytest.fixture(scope="module")
def described(tmp_path_factory: pytest.TempPathFactory):
    """Each shape at each size through the zoo's path, once: its table's path and folder."""
    made: "dict[tuple[str, int], tuple[pathlib.Path, pathlib.Path]]" = {}

    def get(shape: str, rows: int) -> "tuple[pathlib.Path, pathlib.Path]":
        if (shape, rows) not in made:
            folder = tmp_path_factory.mktemp(f"{shape}-{rows}")
            made[(shape, rows)] = (dates_held.answered(dates_held.SWEEP[shape], folder, rows), folder)
        return made[(shape, rows)]

    return get


# -- (A): no date one to ten people or rows hold is published -------------


@pytest.mark.parametrize("rows", SIZES)
@pytest.mark.parametrize("shape", sorted(dates_held.SWEEP))
def test_no_date_one_to_ten_people_or_rows_hold_is_published(described, shape: str, rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder)
    assert found["dated"], f"{shape}: no column read as dates"
    assert found["few"] == 0, found["named"][:20]
    assert found["printed"] == [], found["printed"][:20]


# Lane E0c's two exposures, each column by name: counted in rows (one row a
# person, no person column that repeats), and every date it publishes held.
EXPOSED = (
    ("demographics", ("dob_iso", "dob_us", "dob_text")),
    ("phi_registry", ("birth_date",)),
)


@pytest.mark.parametrize("rows", SIZES)
@pytest.mark.parametrize(("shape", "columns"), EXPOSED)
def test_lane_e0c_exposures_are_counted_in_rows_and_held(described, shape: str, columns: "tuple[str, ...]",
                                                         rows: int) -> None:
    source, folder = described(shape, rows)
    found = dates_held.dates_held_few(source, folder)
    assert found["counted_in"] == "rows"
    for column in columns:
        assert column in found["dated"]
        block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
        grain = block.get("time_grain")
        # Pooled at a grain coarser than the day, or held: never the day.
        assert isinstance(grain, dict) and grain["rung"] in ("year", "quarter", "month", "held"), (column, grain)


# -- a column whose day grain the floor holds keeps its bytes --------------

# The sha256 of each dense column's block (json.dumps, sorted keys) on the
# base, ccebc947, through the same path (wave6/PS2/probe2.py, base-*.log).
PINNED: "dict[tuple[str, str, int], str]" = {
    ("one_row", "admit_date", 20000): "62edde5415265efa1fd62ff5d917d8a865e227b7d4396bdfc953bf7c648870f9",
    ("several_rows", "visit_date", 20000): "0066f4fe052f739dd6f3cd41ce98779f0acfc131c8f3e2193af26424b55c4e69",
    ("no_person", "admit_date", 20000): "670a7f2848427d5b25534e42737c2334993a539fd8a65fc7528a4403c83cd7c0",
    ("dense_only", "admit_date", 20000): "681b7844e6f374a54a1c04834d5a7708aae16dc50b1b07657f09f328972ed3f6",
    ("dense_only", "arrived_at", 20000): "24c21436cb1faea7e381e8780c43ba40b4f3c433738cfa0c1dac22fee34309e0",
}


@pytest.mark.parametrize("rows", SIZES)
@pytest.mark.parametrize(("shape", "column"), [(shape, column) for shape in sorted(dates_held.DENSE)
                                                for column in dates_held.DENSE[shape]])
def test_a_date_column_the_floor_holds_at_the_day_keeps_its_bytes(described, shape: str, column: str,
                                                                  rows: int) -> None:
    source, folder = described(shape, rows)
    block = dates_held.block_of(folder, dates_held.SWEEP[shape].name, column)
    assert "time_grain" not in block, block.get("time_grain")
    digest = hashlib.sha256(json.dumps(block, sort_keys=True).encode("utf-8")).hexdigest()
    assert digest == PINNED[(shape, column, rows)]


def test_a_stamp_whose_days_the_floor_holds_keeps_its_time_of_day(described) -> None:
    """The dense stamp to the minute, no person column, at 20,000 rows: its hours still published."""
    source, folder = described("dense_only", 20000)
    block = dates_held.block_of(folder, "dense_only", "arrived_at")
    assert block["role"] == "datetime"
    percentiles = block["date_percentiles"]
    assert isinstance(percentiles, dict)
    assert any(isinstance(point, str) and not point.endswith("00:00:00") for point in percentiles.values())


# -- the twin ---------------------------------------------------------------


@pytest.mark.parametrize("shape", sorted(dates_held.SWEEP))
def test_the_twin_writes_valid_dates_and_meets_its_description(described, shape: str) -> None:
    source, folder = described(shape, 20000)
    name = dates_held.SWEEP[shape].name
    quiet = io.StringIO()
    with contextlib.redirect_stdout(quiet), contextlib.redirect_stderr(quiet):
        made = cli.main(["generate", f"{folder / (name + '-profile.json')}", "--out-dir", f"{folder}",
                         "--seed", "0", "--replace"])
    assert made == 0, quiet.getvalue()[-2000:]
    found = dates_held.dates_held_few(source, folder)
    loaded = contract.load_profile(f"{folder / (name + '-profile.json')}")
    twin = folder / f"{name}-twin.csv"
    names, columns = dates_held.persons_counted.table_columns(twin)
    for column in found["dated"]:  # type: ignore[union-attr]
        for cell in columns[names.index(column)]:
            if cell:
                assert _parses(cell), (column, cell)
    outcome = validation.measure(loaded, f"{twin}")
    missed = {f"{check.column}" for check in outcome.checks if check.verdict == validation.MISSED}
    assert not missed & set(found["dated"]), sorted(missed)  # type: ignore[arg-type]


def _parses(cell: str) -> bool:
    for written in ("%Y-%m-%d", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%m/%d/%Y", "%d-%b-%Y"):
        try:
            datetime.datetime.strptime(cell, written)
        except ValueError:
            continue
        return True
    return False


# -- the words: rows, not people ---------------------------------------------


def test_the_description_and_its_summary_say_rows_where_rows_are_counted(described) -> None:
    """NF130 and NF131 where each row is its own holder; NF128 where a person column counts in people."""
    source, folder = described("no_person", 20000)
    held = dates_held.block_of(folder, "no_person", "event_date")
    pooled = dates_held.block_of(folder, "no_person", "birth_date")
    assert held["role"] == "identifier"
    assert held["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_ROWS, ())
    assert pooled["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_POOLED_IN_ROWS, ())
    summary = (folder / "no_person-profile.txt").read_text(encoding="utf-8")
    assert "because too few rows hold its dates" in summary
    assert "each row is counted as its own, and some date" in summary
    _source, people = described("several_rows", 20000)
    beside = dates_held.block_of(people, "several_rows", "birth_date")
    assert beside["detection_evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_POOLED_IN_PEOPLE, ())


# -- below the floor: refused by the command --------------------------------


def test_below_the_table_floor_the_command_refuses_the_table_writing_nothing(tmp_path: pathlib.Path) -> None:
    """The count in rows reaches every table the command describes; one row fewer is refused (plan P4-D425).

    The library keeps its bytes below `parsing.TABLE_ROW_FLOOR` rows, where
    the suite's small fixtures test what each date column does; the
    command never publishes a description there.
    """
    table = dates_held.SWEEP["one_row"]
    source = dates_held.health_zoo.write_table(table, tmp_path, parsing.TABLE_ROW_FLOOR - 1, dates_held.SEED)
    screen = io.StringIO()
    with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
        # explicitly, as tests/test_table_floor.py does: the suite's conftest
        # switches the floor off for every other call
        code = cli.main(["profile", f"{source}", "--out-dir", f"{tmp_path}", "--replace"], small_tables_refused=True)
    assert code != 0
    assert "below its floor" in screen.getvalue()
    assert not (tmp_path / "one_row-profile.json").exists()


# -- the product's own parts -----------------------------------------------


def test_the_parts_a_published_date_names() -> None:
    assert profile._date_parts("2023-01-05 18:07:00") == ("2023-01-05", "2023-01", "2023-q1")
    assert profile._date_parts("2023-11") == ("2023-11", "2023-q4")
    assert profile._date_parts("2023-q3") == ("2023-q3",)
    for word in ("2023", "18:07:00", "2023-13-01", "abcd-01-01", ""):
        assert profile._date_parts(word) == ()


def test_rows_as_holders_tells_every_row_apart() -> None:
    holders = profile.rows_as_holders(1000)
    assert len(holders) == 1000 and len(set(holders)) == 1000

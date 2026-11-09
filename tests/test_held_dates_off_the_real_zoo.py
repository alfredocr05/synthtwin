"""P4-D457 (lane ID-ROOM2): the zoo's held date columns, run through the zoo; split from
tests/test_held_dates_off_the_real.py at repair 1 by the CPU-seconds rule (LANE ID-ROOM2 RULINGS 3 (8)).

The zoo's six held date columns -- the five birth-date columns lane SH2 holds as identifiers and the
diagnosis dates held as record numbers -- wrote made-up dates equal to a real date of their column by
chance on the base (733 to 7,055 cells at 20,000 rows). Each case here runs a zoo table as the zoo runs
it, at its catalogue seed, and counts with the zoo's own counter (`identifier_room_shapes.zoo_equal_cells`):
each held date column at 600 rows (a test size: the command refuses such a table) and one column a writer
at 20,000 rows read 0 equal and 0 merging; the two writers' columns at 20,000 rows are
tests/test_held_dates_off_the_real_writers.py's, split from this file by the same rule. Each case is red on
the mutant its docstring names (wave6/ID-ROOM2/mutants.log, wave6/ID-ROOM2/r1/mutants.log).
"""

from __future__ import annotations

import csv
import datetime
import json
import pathlib

import pytest

import health_zoo
import identifier_room_shapes as room
from synthtwin import contract, generation, grains, parsing

# -- (4) the zoo's held date columns ----------------------------------------------------------

# The zoo's six held date columns, as K-HZ-06's driver names them: `table.column`, by table.
HELD: "dict[str, tuple[str, ...]]" = {}
for _named in room.ZOO_HELD_DATES:
    _table, _column = _named.split(".")
    HELD[_table] = HELD.get(_table, ()) + (_column,)
# ...the four of four-figure years, the one of two-figure years and the diagnosis dates.
FOUR_FIGURES = tuple(named for named in room.ZOO_HELD_DATES if named.split(".")[0] in ("patients", "phi_registry"))
TWO_FIGURES = tuple(named for named in room.ZOO_HELD_DATES if named.split(".")[0] == "registry_extract")
DIAGNOSES = tuple(named for named in room.ZOO_HELD_DATES if named.split(".")[0] == "tumor_registry")


def _held_dates(folder: pathlib.Path, rows: int, names: "tuple[str, ...]") -> "dict[str, dict[str, object]]":
    """Each named zoo table at ``rows``, run as the zoo runs it; each held date column's counts and facts."""
    tables = tuple(table for table in room.zoo_tables() if table.name in names)
    by_column: "dict[str, tuple[int, int]]" = {}
    same_days: "dict[str, int]" = {}
    found = room.zoo_equal_cells(folder, rows, tables=tables, by_column=by_column, same_days=same_days)
    assert found["unwritten"] == 0 and found["unread"] == 0
    seen: "dict[str, dict[str, object]]" = {}
    for table in tables:
        where = folder / table.name
        document = json.loads((where / f"{table.name}-profile.json").read_text(encoding="utf-8"))
        twin = where / f"{table.name}-twin{table.suffix}"
        with open(twin, encoding="utf-8", newline="") as handle:
            written = list(csv.DictReader(handle))
        for block in document["columns"]:
            if block["name"] in HELD[table.name] and block.get("role") == "identifier":
                named = f"{table.name}.{block['name']}"
                seen[named] = {
                    "counts": by_column.get(named, (0, 0)),
                    "same_day": same_days.get(named, 0),
                    "years": block.get("made_up_years"),
                    "twin": [one[block["name"]] for one in written],
                }
    return seen


def _years_written(cells: "list[str]") -> "set[int]":
    """The four-figure years the twin's cells write, read as the date forms they wear."""
    years: "set[int]" = set()
    for cell in cells:
        for form in ("%Y-%m-%d", "%m/%d/%Y", "%d-%b-%Y"):
            try:
                years.add(datetime.datetime.strptime(cell, form).year)
                break
            except ValueError:
                continue
    return years


def test_the_zoo_held_birth_dates_at_600_rows(tmp_path: pathlib.Path) -> None:
    """Every held birth date of the zoo at 600 rows (a test size): 0 equal, 0 merging; four figures from 2028.

    On the base, at 600 rows, 1 / 1 of the ISO column, 3 / 3 with a month word, 0 / 1 of the second ISO
    column. The two-figure column finds no room (its real years take some of the block from `28` its
    values need), so its twin is the walk's, off the real. Mutant: `with_made_up_years` returning its
    column unchanged (the base's dates from 2000 on): red on 1 equal.
    """
    seen = _held_dates(tmp_path, 600, ("patients", "phi_registry", "registry_extract"))
    assert sorted(seen) == sorted(FOUR_FIGURES + TWO_FIGURES)
    for named, facts in sorted(seen.items()):
        assert facts["counts"] == (0, 0) and facts["same_day"] == 0, named
    for named in FOUR_FIGURES:
        years = seen[named]["years"]
        assert isinstance(years, list) and years and years[0][0] == 2028, named
        written = _years_written(seen[named]["twin"])  # type: ignore[arg-type]
        assert written and min(written) >= 2028, named
    for named in TWO_FIGURES:
        assert seen[named]["years"] == []


def test_the_negative_control_counts_a_room_on_the_real_years(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The counter is not blind: the twin's writers given the base's years (1940 to 2019) write real dates again,
    which K-HZ-06's same-day count (LANE ID-ROOM2 RULINGS 6 (5)) reads too.

    The contract refuses such a room in a description (`test_the_contract_refuses_anything_else`), so
    the writers' reading of it is replaced here.
    """
    real = generation._room_years

    def base_years(facts: contract.IdentifierFacts) -> "tuple[list[int], list[int]] | None":
        return None if real(facts) is None else (list(range(1940, 2020)), [])

    monkeypatch.setattr(generation, "_room_years", base_years)
    seen = _held_dates(tmp_path, 600, ("patients",))
    assert sum(seen[named]["counts"][0] for named in seen) > 0  # type: ignore[index]
    assert sum(int(f"{seen[named]['same_day']}") for named in seen) > 0
    assert room.same_day_cells(["03-Mar-1932", "1950-01-07"], ["03-Mar-32", "01/07/1950", "07/01/1950", "2032-03-03"]) == 3


def test_the_zoo_table_is_the_zoos_own() -> None:
    """The tables run here are the catalogue's, at its seeds (the same runs K-HZ-06's driver reads)."""
    names = {table.name for table in room.zoo_tables()}
    assert set(HELD) <= names
    assert all(health_zoo.seed_of(table) >= 0 for table in room.zoo_tables() if table.name in HELD)



def test_the_g1_floor_writes_no_date_of_a_year_the_room_does_not_publish(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's item 3 (c): the G1 floor given spans over 1956, a year the room does not publish, writes no
    date of 1956 (each date is checked against the published years before it stands). Mutant B: the check
    dropped from the G1 floor.
    """
    real = generation._room_spans

    def wrong(room: "tuple[list[int], list[int]]", reading: grains.Reading) -> "list[tuple[int, int]]":
        spans = real(room, reading)
        if not spans:
            return spans
        day = grains.date_counts.DAY
        return [(parsing.days_from_civil(1956, 1, 1) * day, parsing.days_from_civil(1957, 1, 1) * day)]

    monkeypatch.setattr(generation, "_room_spans", wrong)
    seen = _held_dates(tmp_path, 600, ("phi_registry",))
    named = FOUR_FIGURES[-1]
    assert 1956 not in _years_written(seen[named]["twin"])  # type: ignore[arg-type]

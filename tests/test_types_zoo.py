"""The data-type zoo holds what it says, cheaply (lane ZOO-X).

`tests/types_zoo.py` writes every way a health table writes a value --
one column a way, grouped into tables of the shapes a hospital warehouse
writes -- and runs each table through the shipped commands at the
owner's table floor (its driver runs the 20,000-row leg; the suite runs
none of it). This file holds the battery to its word at the suite's
size:

* every type is served by exactly one column group of one table, and
  every column of every table serves exactly one type;
* each table rebuilds byte for byte from its seed, and a several-rows
  table holds at least the people the floor asks for at its size;
* the analyst's script holds on every real table, so a failure on a
  twin is the twin's and never the script's;
* EVERY check of every table goes red on a spoiled copy of its real
  table, so no check is blind;
* the owner's date rule (`types_zoo.date_rule`) reads a twin whose
  weekdays or hours moved as failing, and a twin like its source as
  passing;
* the verdicts name what failed a type: a failed step, a validate miss,
  an analyst failure, a failed check of the five, a twin leak and a
  date the rule fails each fail it;
* one table runs every step below the floor through the command's
  internal switch, its twin read by the five checks.
"""

from __future__ import annotations

import pathlib
import random

import pytest

import crosscheck
import health_zoo as zoo
import types_zoo as types

SMALL = 600


def test_every_type_is_served_by_one_column_group_of_one_table() -> None:
    seen: "dict[str, str]" = {}
    for table in types.TABLES:
        for kind in table.kinds:
            if kind == "several_rows_a_person":
                continue
            assert kind not in seen, f"{kind} is served by {seen[kind]} and {table.name}"
            seen[kind] = table.name
    assert sorted(seen) == sorted(types.TYPES)
    assert len(types.TYPES) >= 100


@pytest.mark.parametrize("name", [table.name for table in types.TABLES])
def test_each_column_serves_one_type_and_the_table_rebuilds_from_its_seed(name: str, tmp_path: pathlib.Path) -> None:
    table = types.table_named(name)
    header, rows = table.build(SMALL, types.seed_of(table))
    served = [column for columns in table.kinds.values() for column in columns]
    # A repeated name (the odd_header table's `value`, twice) is one column name serving one type.
    assert set(served) == set(header), f"{name}: {sorted(set(header) ^ set(served))}"
    assert len(served) == len(set(served)), f"{name}: a column serves two types"
    assert all(len(row) == len(header) for row in rows)
    first = table.write(header, rows)
    again = table.write(*table.build(SMALL, types.seed_of(table)))
    assert first == again
    if table.person:
        assert zoo.people_in(table, header, rows) >= zoo.PEOPLE_AT_LEAST[SMALL]


def test_the_analyst_scripts_run_clean_on_every_real_table(tmp_path: pathlib.Path) -> None:
    for table in types.TABLES:
        if table.suffix == ".xlsx" and not crosscheck.present():
            continue
        path = zoo.write_table(table, tmp_path / table.name, SMALL, types.seed_of(table))
        faults = zoo.real_faults(table, zoo.analyse(table, path))
        assert faults == [], f"{table.name}: {faults}"


def _pair(table: "zoo.Table", folder: pathlib.Path, change: "object") -> "list[tuple[str, str, str]]":
    header, rows = table.build(SMALL, types.seed_of(table))
    real = folder / "real" / f"{table.name}{table.suffix}"
    real.parent.mkdir(parents=True, exist_ok=True)
    real.write_bytes(table.write(header, rows))
    header, rows = table.build(SMALL, types.seed_of(table))
    change(header, rows)  # type: ignore[operator]
    twin = folder / "twin" / f"{table.name}{table.suffix}"
    twin.parent.mkdir(parents=True, exist_ok=True)
    twin.write_bytes(table.write(header, rows))
    return zoo.analyst_failures(table, zoo.analyse(table, real), zoo.analyse(table, twin))


@pytest.mark.parametrize("name", [table.name for table in types.TABLES])
def test_every_check_goes_red_on_its_spoiled_table(name: str, tmp_path: pathlib.Path) -> None:
    table = types.table_named(name)
    if table.suffix == ".xlsx":
        crosscheck.reader()
    assert _pair(table, tmp_path / "same", lambda header, rows: None) == []
    blind = []
    for place in range(len(table.checks)):
        check = table.checks[place]
        failures = _pair(table, tmp_path / f"{place}", zoo.spoil_of(check))
        if check.name not in [failure[1] for failure in failures]:
            blind += [check.name]
    assert not blind, f"{name}: these checks did not see their spoil: {blind}"


def _dated_pair(folder: pathlib.Path, change: "object") -> "dict[str, dict[str, object]]":
    table = types.DATE_TABLE
    header, rows = table.build(4000, types.seed_of(table))
    real = folder / "real.csv"
    folder.mkdir(parents=True, exist_ok=True)
    real.write_bytes(table.write(header, rows))
    header, rows = table.build(4000, types.seed_of(table) + 1)
    change(header, rows)  # type: ignore[operator]
    twin = folder / "twin.csv"
    twin.write_bytes(table.write(header, rows))
    return types.date_rule(real, twin, {"iso_day": types.DATED["iso_day"], "utc_moment": types.DATED["utc_moment"]}, table.read)


def test_the_date_rule_passes_a_fresh_draw_and_fails_a_moved_weekday_or_hour(tmp_path: pathlib.Path) -> None:
    same = _dated_pair(tmp_path / "same", lambda header, rows: None)
    assert same["iso_day"]["passes"] and same["utc_moment"]["passes"], same
    import datetime

    def weekdays_moved(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index("iso_day")
        for row in rows:
            day = datetime.date.fromisoformat(row[place])
            if day.weekday() == 0:
                row[place] = f"{day + datetime.timedelta(days=1)}"

    moved = _dated_pair(tmp_path / "weekday", weekdays_moved)
    assert not moved["iso_day"]["passes"], moved["iso_day"]

    def hours_moved(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index("utc_moment")
        for row in rows:
            row[place] = row[place][:11] + "03" + row[place][13:]

    shifted = _dated_pair(tmp_path / "hour", hours_moved)
    assert not shifted["utc_moment"]["passes"], shifted["utc_moment"]


def _passing_result(table: "zoo.Table") -> "dict[str, object]":
    return {
        "steps": {step: {"exit": 0, "error": ""} for step in ("profile", "answers", "generate", "validate")},
        "general": True, "misses": [], "analyst_real_errors": [], "analyst": [], "leaks": {},
        "five_checks": {"passed": True, "checks": {}}, "date_rule": {},
    }


def test_the_verdicts_name_every_prerequisite_a_type_fails() -> None:
    table = types.NUMBER_TABLE
    assert all(not failures for failures in types.type_verdicts(table, _passing_result(table)).values())
    broken = []
    for change in (
        lambda result: result["steps"].__setitem__("generate", {"exit": 1, "error": "no"}),
        lambda result: result.__setitem__("general", False),
        lambda result: result.__setitem__("misses", [["percent_written", "ladder.p05"]]),
        lambda result: result.__setitem__("analyst", [["percentages", "forms percent_written", "x"]]),
        lambda result: result.__setitem__("five_checks", {"passed": False, "checks": {"C4": {"passed": False}}}),
        lambda result: result.__setitem__("leaks", {"percent_written values": {"twin": 2, "twin_cells": 3}}),
    ):
        result = _passing_result(table)
        change(result)
        verdicts = types.type_verdicts(table, result)
        broken += [not verdicts["percentages"]]
    assert not any(broken), broken
    dated = _passing_result(types.DATE_TABLE)
    dated["date_rule"] = {"iso_day": {"read": True, "passes": False}}
    assert types.type_verdicts(types.DATE_TABLE, dated)["iso_dates"]


def test_one_table_runs_every_step_below_the_floor_and_its_twin_is_checked(tmp_path: pathlib.Path) -> None:
    result = types.run_type_table(types.FLAG_TABLE, tmp_path / "flags", SMALL, False)
    for step in ("profile", "answers", "generate", "validate"):
        assert result["steps"][step]["exit"] in (0, 3), (step, result["steps"][step])  # type: ignore[index]
    assert result["general"]
    checks = result["five_checks"]
    assert isinstance(checks, dict) and "checks" in checks, checks
    assert sorted(checks["checks"]) == ["C1", "C2", "C3", "C4", "C5"]


def test_the_build_is_random_enough_to_hold_rare_levels() -> None:
    table = types.FLAG_TABLE
    header, rows = table.build(SMALL, types.seed_of(table))
    clinics = {row[header.index("clinic_name")] for row in rows}
    assert len(clinics) >= 15
    assert random.Random(types.SEED).random() == random.Random(types.SEED).random()

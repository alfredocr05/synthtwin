"""The health data zoo at or above the owner's table floor, in shards (lane E0c, plan P4-D431).

The owner, 2026-10-22: "we don't make twins of small tables"
(`synthtwin profile` refuses a table under 20,000 rows that hold a value,
or one in which a person has several rows and fewer than 1,000 people
appear; plan P4-D425). Lane E0c re-defines the zoo at or above that
floor: every kind's KPI leg runs at 20,000 rows through the SHIPPED
floor, and the suite's 600-row runs are its fast smoke, BELOW THE FLOOR,
through the command's internal switch. This file holds the zoo to that,
cheaply, without running the product at 20,000 rows:

* the shards cover the catalogue once, at most thirty kinds each, a
  table's kinds together (K-HZ-03's bound);
* every several-rows-per-patient kind holds at least 100 people at 600
  rows and 1,000 at 20,000 (K-HZ-05), counted on the tables as built;
* `run_zoo` passes the floor ON at the KPI size and OFF below it, and a
  run the floor stops is named as refused, never read as a pass;
* the leak scan sees a real value of a person, place or record column in
  the description and in the twin (HIPAA first), and an age past 89.
"""

from __future__ import annotations

import json
import pathlib
import shutil

import pytest

import health_zoo as zoo


def test_the_kpi_size_is_the_owners_table_floor() -> None:
    """The zoo's KPI size is the product's own floor, and its people floor the product's."""
    from synthtwin import parsing

    assert zoo.KPI_ROWS == parsing.TABLE_ROW_FLOOR
    assert zoo.PEOPLE_AT_LEAST[zoo.KPI_ROWS] == parsing.TABLE_PEOPLE_FLOOR
    assert zoo.SMOKE_ROWS < zoo.KPI_ROWS


def shard_problems(shards: "tuple[tuple[zoo.Table, ...], ...]") -> "list[str]":
    """What is wrong with a sharding: a table missing or run twice, a shard over its kinds."""
    problems: "list[str]" = []
    seen = [table.name for shard in shards for table in shard]
    every = [table.name for table in zoo.catalogue()]
    if sorted(seen) != sorted(every):
        problems += [f"the shards run {len(seen)} tables, the catalogue holds {len(every)}"]
    for place, shard in enumerate(shards, 1):
        kinds = sum(len(table.kinds) for table in shard)
        if kinds > zoo.SHARD_KINDS_AT_MOST:
            problems += [f"shard {place} holds {kinds} kinds"]
        if not shard:
            problems += [f"shard {place} is empty"]
    return problems


def test_the_shards_cover_the_catalogue_once() -> None:
    """Each table in one shard, each shard at most thirty kinds; red on a missing table and on two shards joined."""
    shards = zoo.shards()
    assert shard_problems(shards) == []
    assert len(shards) >= 2
    missing = (shards[0][1:],) + shards[1:]
    assert shard_problems(missing)
    largest = sorted(range(len(shards)), key=lambda place: -sum(len(table.kinds) for table in shards[place]))[:2]
    joined = (shards[largest[0]] + shards[largest[1]],) + tuple(
        shard for place, shard in enumerate(shards) if place not in largest
    )
    assert any("holds" in problem for problem in shard_problems(joined))


def people_short(tables: "tuple[zoo.Table, ...]", n: int) -> "dict[str, int]":
    """Each several-rows table built at `n` rows whose person column names fewer people than the floor."""
    short: "dict[str, int]" = {}
    for table in tables:
        if not table.person:
            continue
        header, rows = table.build(n, zoo.seed_of(table))
        people = zoo.people_in(table, header, rows)
        assert people is not None
        if people < zoo.PEOPLE_AT_LEAST[n]:
            short[table.name] = people
    return short


@pytest.mark.parametrize("n", [zoo.SMOKE_ROWS, zoo.KPI_ROWS])
def test_every_several_rows_kind_holds_its_people(n: int) -> None:
    """100 people at 600 rows and 1,000 at 20,000 for every table whose person has several rows."""
    tables = tuple(table for table in zoo.catalogue() if table.person)
    assert len(tables) >= 14, "the catalogue's several-rows tables name their person column"
    assert people_short(tables, n) == {}
    for table in tables:
        header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
        place = header.index(table.person)
        assert len({row[place] for row in rows}) < len(rows), f"{table.name}: nobody has several rows"


def test_a_table_of_too_few_people_is_named() -> None:
    """The mutant: a several-rows table of thirty people is short at both sizes."""
    labs = zoo.table_named("labs")

    def few(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
        header, rows = labs.build(n, seed)
        place = header.index("patient_id")
        for index in range(len(rows)):
            rows[index][place] = f"PT{index % 30:07d}"
        return header, rows

    import dataclasses

    crowded = dataclasses.replace(labs, build=few)
    assert people_short((crowded,), zoo.SMOKE_ROWS) == {"labs": 30}
    found = zoo.floor_measures([{"table": "labs", "rows": zoo.KPI_ROWS, "people": 30}])
    assert found["several_rows_kinds_under_people_floor"] == 2
    assert found["fewest_people"] == 30


def test_run_zoo_turns_the_floor_on_at_the_kpi_size(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """The shipped floor at 20,000 rows, the internal switch off for the 600-row smoke, every table run."""
    seen: "list[tuple[str, int, bool]]" = []

    def run_table(table: "zoo.Table", folder: pathlib.Path, n: int, seed: int, small_tables_refused: bool = False) -> "dict":
        seen.extend([(table.name, n, small_tables_refused)])
        return {"table": table.name}

    monkeypatch.setattr(zoo, "run_table", run_table)
    first = zoo.shards()[0]
    zoo.run_zoo(tmp_path, zoo.SMOKE_ROWS, tables=first)
    zoo.run_zoo(tmp_path, zoo.KPI_ROWS, tables=first)
    runnable = zoo.runnable_tables(first)
    assert seen == [(t.name, zoo.SMOKE_ROWS, False) for t in runnable] + [(t.name, zoo.KPI_ROWS, True) for t in runnable]


def test_a_run_the_floor_stops_is_named_refused(tmp_path: pathlib.Path) -> None:
    """The patients' export at 600 rows with the shipped floor on: refused at profile, and K-HZ-05 counts it."""
    table = zoo.table_named("patients")
    refused = zoo.run_table(table, tmp_path / "on", zoo.SMOKE_ROWS, zoo.seed_of(table), small_tables_refused=True)
    assert refused["steps"] == {"profile": {"exit": 1, "error": refused["steps"]["profile"]["error"]}}
    assert refused["refused_by_floor"] == "profile"
    found = zoo.floor_measures([refused])
    assert found["kinds_refused_by_floor"] == len(table.kinds)
    verdicts = zoo.per_kind([refused])
    assert not any(verdict["passed"] for verdict in verdicts.values())
    assert zoo.smoke_ran([refused]) == {kind: False for kind in table.kinds}


def test_a_step_that_fails_for_another_reason_is_not_called_refused(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """The mutant of the refusal's naming: a profile that exits 1 with the floor off too is no refusal."""
    from synthtwin import cli

    monkeypatch.setattr(cli, "main", lambda arguments, **_switch: 1)
    table = zoo.table_named("patients")
    result = zoo.run_table(table, tmp_path, 150, zoo.seed_of(table), small_tables_refused=True)
    assert "refused_by_floor" not in result
    assert zoo.floor_measures([result])["kinds_refused_by_floor"] == 0


COUNTS = ("description", "twin", "twin_cells", "twin_by_chance")


def _counted(found: "dict[str, dict]") -> "dict[str, dict]":
    """Each entry's counts alone (an entry also names its column and how it is read)."""
    return {key: {name: entry[name] for name in COUNTS} for key, entry in found.items()}


def _leak_case(tmp_path: pathlib.Path, twin_change: "object", described: "dict") -> "dict[str, dict]":
    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    tmp_path.mkdir(parents=True, exist_ok=True)
    real = tmp_path / "real.csv"
    real.write_bytes(table.write(header, rows))
    twin_change(header, rows)  # type: ignore[operator]
    twin = tmp_path / "twin.csv"
    twin.write_bytes(table.write(header, rows))
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps(described), encoding="utf-8", newline="\n")
    return _counted(zoo.leaked(table, real, twin, profile))


def _made_up_zips(header: "list[str]", rows: "list[list[str]]") -> None:
    for column, value in (
        ("zip5", "99901"), ("zip4", "99901-0001"), ("dob_iso", "1990-01-01"), ("dob_us", "01/01/1990"),
        ("dob_text", "01-Jan-1990"), ("patient_id", "PX0000001"), ("birth_city", "Nowhere"),
    ):
        place = header.index(column)
        for row in rows:
            row[place] = value


def test_the_leak_scan_sees_a_real_value(tmp_path: pathlib.Path) -> None:
    """HIPAA first: a real ZIP in the twin, or printed in the column's block or its note, is found; made-up ones are not."""
    clean = _leak_case(tmp_path / "clean", _made_up_zips, {"columns": [{"name": "zip5", "role": "identifier"}]})
    patients = zoo.table_named("patients")
    every = zoo.leak_list(patients, patients.build(10, 1)[0])
    assert clean == {zoo._leak_key(column, how): dict.fromkeys(COUNTS, 0) for column, how in every}
    copied = _leak_case(tmp_path / "copied", lambda header, rows: None, {"columns": []})
    assert copied["zip5"]["twin"] >= 10 and copied["zip5"]["twin_cells"] == zoo.SMOKE_ROWS
    printed = _leak_case(tmp_path / "printed", _made_up_zips, {
        "columns": [{"name": "zip5", "percentiles": {"p50": 2139.0}, "mode": "06510", "mode_count": 2139}],
        "publication_notes": [{"column": "zip4", "note": ["02139-0001"]}],
    })
    assert printed["zip5"] == {"description": 2, "twin": 0, "twin_cells": 0, "twin_by_chance": 0}
    counted = _leak_case(tmp_path / "counted", _made_up_zips, {"columns": [{"name": "zip5", "rows": 2139, "n_distinct": 6510}]})
    assert counted["zip5"]["description"] == 0, "a count is not a value"


def test_made_up_keys_meeting_real_ones_by_chance_are_told_from_a_copy(tmp_path: pathlib.Path) -> None:
    """A twin of keys drawn in a range real keys fill meets them by chance; a copy of a few real keys is a leak.

    The control (the real keys moved past their range by its width) meets
    the twin as often as chance does, so the drawn twin counts nothing;
    the twin that copies twenty real keys and draws the rest past the
    range counts all twenty.
    """
    import dataclasses
    import random

    table = dataclasses.replace(zoo.table_named("patients"), leaks=(("patient_id", "values"),))
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("patient_id")
    for index in range(len(rows)):
        rows[index][place] = f"{100000 + index * 3}"
    real = tmp_path / "real.csv"
    real.write_bytes(table.write(header, rows))
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"columns": []}), encoding="utf-8", newline="\n")
    draw = random.Random(4)
    for row in rows:
        row[place] = f"{draw.randint(100000, 103599)}"
    drawn = tmp_path / "drawn.csv"
    drawn.write_bytes(table.write(header, rows))
    by_chance = _counted(zoo.leaked(table, real, drawn, profile))["patient_id"]
    assert by_chance["twin"] == 0 and by_chance["twin_by_chance"] > 0, by_chance
    for index in range(len(rows)):
        rows[index][place] = f"{100000 + index * 3}" if index < 20 else f"{200000 + index}"
    copied = tmp_path / "copied.csv"
    copied.write_bytes(table.write(header, rows))
    # Chance here is the real's density inside its range (600 keys over
    # 1,798 numbers) times the twenty values drawn there: 7, far under 20.
    assert _counted(zoo.leaked(table, real, copied, profile))["patient_id"] == {
        "description": 0, "twin": 20, "twin_cells": 20, "twin_by_chance": 7,
    }
    # The same between constant marks: 'MR' and seven figures, as a
    # medical record number is written.
    for index in range(len(rows)):
        rows[index][place] = f"MR{4000000 + index}"
    real.write_bytes(table.write(header, rows))
    for row in rows:
        row[place] = f"MR{draw.randint(4000000, 4001199)}"
    drawn.write_bytes(table.write(header, rows))
    marked = _counted(zoo.leaked(table, real, drawn, profile))["patient_id"]
    assert marked["twin"] == 0 and marked["twin_by_chance"] > 0, marked
    assert zoo._by_chance({"maria chen", "mr1"}, ["maria chen"]) == (False, 0, 0), "no control where the values are not numbers"
    # A number in scientific notation met once by chance: the control is
    # drawn, and one match under it is not a copy.
    assert zoo._by_chance({zoo._normal("4.56789E+11"), zoo._normal("1.23457E+11")}, [zoo._normal("4.56789E+11")])[0] is True


def test_the_age_scan_sees_an_age_past_89(tmp_path: pathlib.Path) -> None:
    """Safe Harbor: an age past 89 written as a number, in the twin or the block, is found; '90+' is not."""
    import dataclasses

    table = dataclasses.replace(zoo.table_named("patients"), leaks=(("age", "ages over 89"),))
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    real = tmp_path / "real.csv"
    real.write_bytes(table.write(header, rows))
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"columns": [{"name": "age", "levels": {"90+": 30}}]}), encoding="utf-8", newline="\n")
    assert _counted(zoo.leaked(table, real, real, profile))["age"] == {"description": 0, "twin": 0, "twin_cells": 0, "twin_by_chance": 0}
    place = header.index("age")
    rows[0][place] = "93"
    twin = tmp_path / "twin.csv"
    twin.write_bytes(table.write(header, rows))
    profile.write_text(json.dumps({"columns": [{"name": "age", "tails": {"high": {"values": [90.0, 91.0, 104]}}}]}), encoding="utf-8", newline="\n")
    assert _counted(zoo.leaked(table, real, twin, profile))["age"] == {"description": 2, "twin": 1, "twin_cells": 1, "twin_by_chance": 0}


def test_a_printed_value_is_read_in_the_description_alone(tmp_path: pathlib.Path) -> None:
    """A birth date the twin draws in its span meets a real one by chance: 'printed values' reads the description only."""
    case = _leak_case(tmp_path, lambda header, rows: None, {"columns": []})
    assert case["dob_iso"] == {"description": 0, "twin": 0, "twin_cells": 0, "twin_by_chance": 0}
    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    born = rows[0][header.index("dob_iso")]
    printed = _leak_case(tmp_path / "printed", lambda header, rows: None, {"columns": [{"name": "dob_iso", "percentiles": {"min": born}}]})
    assert printed["dob_iso"] == {"description": 1, "twin": 0, "twin_cells": 0, "twin_by_chance": 0}


def test_a_leak_fails_its_kind_and_is_counted() -> None:
    """A real value published fails its kind at the analyst step, needs an owner, and K-HZ-02 counts it."""
    result = {
        "table": "patients", "rows": zoo.SMOKE_ROWS, "misses": [], "analyst": [], "asked": [], "general": True,
        "analyst_real_errors": [], "steps": {step: {"exit": 0, "error": ""} for step in ("profile", "answers", "generate", "validate")},
        "leaks": {"zip5": {"description": 3, "twin": 4, "twin_cells": 90}, "zip4": {"description": 0, "twin": 0, "twin_cells": 0, "twin_by_chance": 0}},
    }
    verdicts = zoo.per_kind([result])
    assert "leak zip5" in verdicts["demographics"]["failures"]
    assert "leak zip4" not in verdicts["demographics"]["failures"]
    measured = zoo.zoo_measures([result])
    assert measured["K-HZ-02"]["real_values_published"] == 7
    assert "patients.zip5" in measured["K-HZ-02"]["real_values_published_named"]


def test_the_twin_of_a_text_export_is_found(tmp_path: pathlib.Path) -> None:
    """A '.txt' export is twinned as '.csv': the run reads that twin rather than stopping before the analyst."""
    table = zoo.table_named("critical_care_charting")
    result = zoo.run_table(table, tmp_path, zoo.SMOKE_ROWS, zoo.seed_of(table))
    assert result["steps"]["generate"]["exit"] == 0 and "validate" in result["steps"]
    assert result.get("analyst_real_errors") == []
    shutil.rmtree(tmp_path, ignore_errors=True)

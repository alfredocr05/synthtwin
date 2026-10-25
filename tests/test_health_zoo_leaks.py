"""The health data zoo's leak scan, HIPAA first (lane E0c's repair, plan P4-D431).

The zoo reads every column that names a person, a place, a record or a
Safe Harbor element for its real values in each description and in the
twin (`health_zoo.leaked`). These tests hold the scan to what it claims,
each red on the mutant named in its docstring:

* the columns read follow from the columns themselves (`leak_list`):
  every column answered `identifier` and every birth or death date,
  birth year, age, ZIP code, device identifier or UID, name, address,
  telephone, e-mail, social security or record number is read, and every
  entry reaches the scanner (skeptic 1 item 6, Codex item 3);
* a year of 1934 or earlier -- an age of 90 or more in the zoo's era --
  is counted wherever it is written, as a year or in a date (skeptic 1
  item 1);
* a birth date is compared as the ISO date the description prints,
  whatever its source's spelling, a two-figure year in the century the
  person named (items 2 and 3), and a date published at a year's grain
  is the grain's, not a person's day (item 4);
* the first description, written before any answer, is read at once and
  kept, whatever the later steps do (item 5, Codex item 4);
* one real value copied onto many rows is a copy whatever the control
  meets, and the control holds no real value (Codex item 1);
* a value published folded or as a number in another notation is the
  value (Codex item 2), and a census keyed by counts holds no value
  (item 11);
* each validate check a column misses is a failure of its own (Codex
  item 5).
"""

from __future__ import annotations

import dataclasses
import json
import pathlib

import pytest

import health_zoo as zoo


def _write(tmp_path: pathlib.Path, table: "zoo.Table", header: "list[str]", rows: "list[list[str]]", name: str) -> pathlib.Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / f"{name}{table.suffix}"
    path.write_bytes(table.write(header, rows))
    return path


def _profile(tmp_path: pathlib.Path, described: "dict", name: str = "profile") -> pathlib.Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(described), encoding="utf-8", newline="\n")
    return path


def _counts(found: "dict") -> "tuple[int, int, int]":
    return found["description"], found["twin"], found["twin_cells"]


# -- which columns are read ----------------------------------------------------

# Columns the hand-written lists of a974b1d9 left unread, each a person's
# value the product may publish (skeptic 1's L2 to L4, Codex item 3).
MUST_BE_READ = {
    ("patients", "dob_us", "printed values"), ("patients", "dob_text", "printed values"),
    ("patients", "dob_iso", "years over 89"), ("patients", "age", "ages over 89"),
    ("immunizations", "udi", "values"), ("registry_extract", "dob_short", "printed values"),
    ("registry_extract", "dob_short", "years over 89"), ("fhir_observations", "id", "values"),
    ("fhir_observations", "subject_reference", "values"), ("safe_harbor", "birth_year", "years over 89"),
    ("phi_registry", "birth_date", "years over 89"), ("imaging", "study_uid", "values"),
    ("sql_server", "death_date", "printed values"), ("edge_columns", "middle_name", "values"),
    ("long_visits_record_numbers", "med_rec_no", "values"), ("numeric_identifiers", "durable_key", "values"),
}


def _header(table: "zoo.Table") -> "list[str]":
    return table.build(30, zoo.seed_of(table))[0]


def _inventory(rules: "object" = None) -> "set[tuple[str, str, str]]":
    every: "set[tuple[str, str, str]]" = set()
    for table in zoo.catalogue():
        every |= {(table.name, column, how) for column, how in zoo.leak_list(table, _header(table))}
    return every


def test_every_sensitive_column_of_the_catalogue_is_read() -> None:
    """Every column answered `identifier`, and every column a Safe Harbor name rule reaches, has a leak entry.

    Red when a rule is removed (the UDI rule: immunizations.udi unread)
    or when the person's `identifier` answer no longer makes a column read.
    """
    inventory = _inventory()
    assert MUST_BE_READ <= inventory, sorted(MUST_BE_READ - inventory)
    for table in zoo.catalogue():
        header = _header(table)
        read = {column for column, _how in zoo.leak_list(table, header)}
        for column in header:
            if column in zoo.NOT_READ:
                assert column not in read
                continue
            named = any(pattern.search(column) for pattern, _modes, _what in zoo.SENSITIVE_NAMES)
            if named or table.knows.get(column) == "identifier":
                assert column in read, f"{table.name}.{column} is not read for real values"
        for column, how in table.leaks:
            assert (column, how) in zoo.leak_list(table, header) or column in read


def test_a_rule_removed_leaves_its_column_unread(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutants of the inventory: the UDI rule dropped, and the `identifier` answer ignored."""
    kept = tuple(rule for rule in zoo.SENSITIVE_NAMES if not rule[0].search("udi"))
    monkeypatch.setattr(zoo, "SENSITIVE_NAMES", kept)
    assert ("immunizations", "udi", "values") not in _inventory()
    monkeypatch.undo()
    fhir = zoo.table_named("fhir_observations")
    blind = dataclasses.replace(fhir, knows={})
    assert "subject_reference" not in {column for column, _how in zoo.leak_list(blind, _header(fhir))}


def test_every_entry_reaches_the_scanner(tmp_path: pathlib.Path) -> None:
    """Codex item 3: `leaked` returns an entry for every (column, how) of the inventory, on every delimited export."""
    for table in zoo.catalogue():
        if table.suffix == ".xlsx":
            continue
        header, rows = table.build(40, zoo.seed_of(table))
        source = _write(tmp_path / table.name, table, header, rows, "real")
        profile = _profile(tmp_path / table.name, {"columns": []})
        found = zoo.leaked(table, source, source, profile)
        wanted = {zoo._leak_key(column, how) for column, how in zoo.leak_list(table, header)}
        assert set(found) == wanted, table.name
        assert len(wanted) == len(zoo.leak_list(table, header)), f"{table.name}: two entries share a key"


# -- the years of an age of 90 or more ------------------------------------------


def test_a_year_of_an_age_over_89_is_counted(tmp_path: pathlib.Path) -> None:
    """Skeptic 1 item 1: a birth year of 1934 or earlier printed, or written by the twin, is counted; 1935 is not.

    Red on the mutant without the years mode (safe_harbor.birth_year
    read only for its age column).
    """
    table = zoo.table_named("safe_harbor")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("birth_year")
    for row in rows:
        row[place] = "1960"
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [{"name": "birth_year", "percentiles_between": {"p02": 1924}}]})
    found = zoo.leaked(table, source, source, profile)
    assert _counts(found["birth_year years"]) == (1, 0, 0)
    rows[0][place] = "1931"
    rows[1][place] = "1935"
    twin = _write(tmp_path, table, header, rows, "twin")
    clean = _profile(tmp_path, {"columns": [{"name": "birth_year", "percentiles": {"min": 1935, "n_rows": 1900}}]}, "clean")
    assert _counts(zoo.leaked(table, source, twin, clean)["birth_year years"]) == (0, 1, 1)


def test_a_birth_dates_years_are_read_in_every_spelling(tmp_path: pathlib.Path) -> None:
    """The year part of a birth date: an ISO date or a year-grain span printed, a US-spelt twin cell, all counted."""
    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [
        {"name": "dob_iso", "time_grain": {"spans": [["year", "1931-01-01", "2005-01-01"]]}},
        {"name": "dob_us", "date_percentiles": {"p01": "1929-05-02T00:00:00"}},
    ]})
    for row in rows:
        row[header.index("dob_us")] = "06/15/1970"
    rows[0][header.index("dob_us")] = "06/15/1930"
    twin = _write(tmp_path, table, header, rows, "twin")
    found = zoo.leaked(table, source, twin, profile)
    assert found["dob_iso years"]["description"] == 1
    assert _counts(found["dob_us years"]) == (1, 1, 1)


# -- birth dates as the description prints them ----------------------------------


def test_a_us_birth_date_is_compared_as_the_iso_date_printed(tmp_path: pathlib.Path) -> None:
    """Skeptic 1 item 3: a real '12/20/1936' printed as '1936-12-20' counts; red on the mutant without the parse."""
    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    born = rows[0][header.index("dob_us")]
    month, day, year = born.split("/")
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [{"name": "dob_us", "date_percentiles": {"p50": f"{year}-{month}-{day}T00:00:00"}}]})
    assert zoo.leaked(table, source, None, profile)["dob_us"]["description"] == 1
    written = rows[0][header.index("dob_text")]
    import datetime

    iso = datetime.datetime.strptime(written, "%d-%b-%Y").date().isoformat()
    profile = _profile(tmp_path, {"columns": [{"name": "dob_text", "heavy_dates": [iso]}]})
    assert zoo.leaked(table, source, None, profile)["dob_text"]["description"] == 1


def test_a_two_figure_year_is_read_in_the_century_named(tmp_path: pathlib.Path) -> None:
    """Skeptic 1 items 2 and 3: registry_extract's '13/03/77' printed as 1977-03-13 counts (the person said 1900-1999)."""
    table = zoo.table_named("registry_extract")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    written = rows[0][header.index("dob_short")]
    day, month, year = written.split("/")
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [{"name": "dob_short", "date_percentiles": {"p10": f"19{year}-{month}-{day}"}}]})
    assert zoo.leaked(table, source, None, profile)["dob_short"]["description"] == 1
    assert zoo._iso_dates(["13/03/27"], "%d/%m/%y", "1900-1999") == ["1927-03-13"]
    assert zoo._iso_dates(["13/03/27"], "%d/%m/%y") == ["2027-03-13"], "Python's own pivot, where no century is named"


def test_a_date_at_a_years_grain_is_not_a_persons_day(tmp_path: pathlib.Path) -> None:
    """Skeptic 1 item 4: '1949-01-01' published at a year grain is not a real birth date; at a day's grain it is."""
    table = zoo.table_named("phi_registry")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("birth_date")
    rows[0][place] = "1949-01-01"
    source = _write(tmp_path, table, header, rows, "real")
    yearly = _profile(tmp_path, {"columns": [{"name": "birth_date", "date_percentiles": {"p25": "1949-01-01"},
                                              "time_grain": {"finest": "year"}}]})
    assert zoo.leaked(table, source, None, yearly)["birth_date"]["description"] == 0
    daily = _profile(tmp_path, {"columns": [{"name": "birth_date", "date_percentiles": {"p25": "1949-01-01"},
                                             "time_grain": {"finest": "day"}}]}, "daily")
    assert zoo.leaked(table, source, None, daily)["birth_date"]["description"] == 1


# -- the description before the answers ---------------------------------------------


def test_the_first_description_is_read_before_the_answers(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """Skeptic 1 item 5 and Codex item 4: a ZIP printed before the answers is counted, though the answer holds it and generate fails.

    Red on the mutants that read only the answered description, or read
    nothing once a later step fails.
    """
    from synthtwin import cli

    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    real_zip = rows[0][header.index("zip5")]
    calls: "list[list[str]]" = []

    def main(arguments: "list[str]", **_switch: object) -> int:
        calls.extend([arguments])
        source = pathlib.Path(arguments[1])
        if arguments[0] != "profile":
            return 1
        profile = source.with_name(f"{table.name}-profile.json")
        held = "--answers" in arguments
        block = {"name": "zip5", "role": "identifier"} if held else {"name": "zip5", "mode": real_zip}
        profile.write_text(json.dumps({"columns": [block]}), encoding="utf-8")
        source.with_name(f"{table.name}-questions.json").write_text(json.dumps({"asked": []}), encoding="utf-8")
        return 0

    monkeypatch.setattr(cli, "main", main)
    result = zoo.run_table(table, tmp_path, zoo.SMOKE_ROWS, zoo.seed_of(table))
    assert [call[0] for call in calls] == ["profile", "profile", "generate"]
    assert result["leaks"]["zip5 unanswered"]["description"] == 1
    assert result["leaks"]["zip5"]["description"] == 0
    assert (tmp_path / "patients-profile-unanswered.json").is_file()
    verdicts = zoo.per_kind([result])
    assert "leak zip5 unanswered" in verdicts["demographics"]["failures"]


# -- the twin read against a control --------------------------------------------------


def test_one_real_key_copied_onto_every_row_is_a_copy(tmp_path: pathlib.Path) -> None:
    """Codex item 1: 'MR4000000' on every twin row is counted, though it is one distinct value; red on the distinct-only rule."""
    table = zoo.table_named("phi_registry")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("med_rec_no")
    source = _write(tmp_path, table, header, rows, "real")
    first = rows[0][place]
    for row in rows:
        row[place] = first
    twin = _write(tmp_path, table, header, rows, "twin")
    profile = _profile(tmp_path, {"columns": []})
    found = zoo.leaked(table, source, twin, profile)["med_rec_no"]
    assert found["twin"] == 1 and found["twin_cells"] == zoo.SMOKE_ROWS, found


def test_the_control_holds_no_real_value() -> None:
    """Codex item 1: the control of decimal numbers moved past their range never lands on the highest real one."""
    real = {"1.5", "2.5", "4.5"}
    drawn, chance, control = zoo._by_chance(real, ["4.5", "4.5", "4.5"])
    assert drawn and (chance, control) == (0, 0)
    drawn, chance, control = zoo._by_chance({"100", "105"}, ["105", "111", "111"])
    assert drawn and (chance, control) == (1, 1)


def test_made_up_keys_filling_the_real_range_are_chance() -> None:
    """A study's record numbers 1 to 223 and a twin drawn in 1 to 230: chance is the density inside the range."""
    real = {f"{number}" for number in range(1, 224)}
    twin = [f"{number}" for number in range(1, 231)] * 2
    drawn, chance, control = zoo._by_chance(real, twin)
    assert drawn and control == 7 and chance == 223


# -- what counts as the same value -------------------------------------------------------


def test_a_value_published_folded_or_in_another_notation_is_the_value(tmp_path: pathlib.Path) -> None:
    """Codex item 2: 'Maria Chen' printed 'maria chen', and '1.23457E+11' printed 123457000000.0, each count."""
    table = zoo.table_named("phi_registry")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    name = rows[0][header.index("patient_name")]
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [{"name": "patient_name", "levels": [{"variants": [name.casefold()]}]}]})
    assert zoo.leaked(table, source, None, profile)["patient_name"]["description"] == 1
    assert zoo._normal("1.23457E+11") == zoo._normal("123457000000.0") == "123457000000"
    assert zoo._normal(" Maria  Chen ") == zoo._normal("maria chen")
    mangled = zoo.table_named("excel_mangled")
    header, rows = mangled.build(zoo.SMOKE_ROWS, zoo.seed_of(mangled))
    shown = rows[0][header.index("account_shown")]
    source = _write(tmp_path / "mangled", mangled, header, rows, "real")
    profile = _profile(tmp_path / "mangled", {"columns": [{"name": "account_shown", "percentiles": {"p50": float(shown)}}]})
    assert zoo.leaked(mangled, source, None, profile)["account_shown"]["description"] == 1


def test_a_census_keyed_by_counts_holds_no_value(tmp_path: pathlib.Path) -> None:
    """Skeptic 1 item 11: `n_distinct_by_occurrences` {"1": 44} and the widths are counts, never record numbers 1 or 44."""
    table = zoo.table_named("redcap")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    source = _write(tmp_path, table, header, rows, "real")
    profile = _profile(tmp_path, {"columns": [{
        "name": "record_id", "n_distinct_by_occurrences": {"1": 44, "2": 10, "3": 7}, "field_widths": {"1": 9, "2": 90},
        "hour_census": {"3": 12}, "layout_forms": {"%%%": 9}, "missing_by_class": {"(blank)": 12},
    }]})
    assert zoo.leaked(table, source, None, profile)["record_id"]["description"] == 0
    printed = _profile(tmp_path, {"columns": [{"name": "record_id", "mode": "7"}]}, "printed")
    assert zoo.leaked(table, source, None, printed)["record_id"]["description"] == 1
    well = zoo.table_named("well_child")
    header, rows = well.build(zoo.SMOKE_ROWS, zoo.seed_of(well))
    source = _write(tmp_path / "well", well, header, rows, "real")
    forms = _profile(tmp_path / "well", {"columns": [{"name": "age_text", "layout_forms": {"%% &&": 149, "(withheld)": 451}}]})
    assert zoo.leaked(well, source, None, forms)["age_text"]["description"] == 0, "149 rows of a form are no age of 149"
    spelt = _profile(tmp_path / "well", {"columns": [{"name": "age_text", "levels": [
        {"count": 136, "label": "13 mo", "variants": {"13 mo": 136}, "variants_withheld": {}},
    ]}]}, "spelt")
    assert zoo.leaked(well, source, None, spelt)["age_text"]["description"] == 0, "136 rows of a spelling are no age"


# -- each validate check its own failure ----------------------------------------------------


def test_each_missed_check_of_a_column_is_its_own_failure() -> None:
    """Codex item 5: three checks labs.ref_range misses count three, each owned through the column's line."""
    done = {"exit": 0, "error": ""}
    result = {
        "table": "labs", "rows": zoo.KPI_ROWS, "analyst": [], "asked": [], "general": True, "analyst_real_errors": [],
        "steps": {step: dict(done) for step in ("profile", "answers", "generate", "validate")},
        "misses": [["ref_range", "distinct.n_distinct"], ["ref_range", "shape.forms"], ["ref_range", "missing.n_missing"]],
    }
    verdict = zoo.per_kind([result])["labs"]
    assert len([item for item in verdict["failures"] if item.startswith("miss ref_range")]) == 3
    assert zoo.zoo_measures([result])["K-HZ-02"]["failures"] >= 3

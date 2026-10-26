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
import re

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
    ("patients", "birth_city", "values"),
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


def test_a_date_at_a_months_grain_is_not_a_persons_day(tmp_path: pathlib.Path) -> None:
    """E0c verify of repair 1, item 2 (V1): '1950-03-01' published at a month grain is the month's, not a birth date.

    Red without the month clause of `_printed_dates`; at a day's grain the
    same date is a real one and counts.
    """
    table = zoo.table_named("phi_registry")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    rows[0][header.index("birth_date")] = "1950-03-01"
    source = _write(tmp_path, table, header, rows, "real")
    monthly = _profile(tmp_path, {"columns": [{"name": "birth_date", "heavy_dates": [{"date": "1950-03-01", "rows": 12}],
                                               "grain": "month"}]})
    assert zoo.leaked(table, source, None, monthly)["birth_date"]["description"] == 0
    daily = _profile(tmp_path, {"columns": [{"name": "birth_date", "heavy_dates": [{"date": "1950-03-01", "rows": 12}],
                                             "grain": "day"}]}, "daily")
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
        profile.write_text(json.dumps({"columns": [block]}), encoding="utf-8", newline="\n")
        source.with_name(f"{table.name}-questions.json").write_text(json.dumps({"asked": []}), encoding="utf-8", newline="\n")
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
    assert zoo._by_chance(real, ["4.5", "4.5", "4.5"]) == (True, 0)
    assert zoo._by_chance({"100", "105"}, ["105", "111", "111"]) == (True, 1)


def _real_values(cells: "list[str]") -> "set[str]":
    """The distinct real values `leaked` compares a 'values' entry by: placeholders and missing words aside."""
    return {
        zoo._normal(cell) for cell in cells
        if cell.strip() and not zoo.PLACEHOLDER.fullmatch(cell.strip()) and zoo._normal(cell) not in zoo.MISSING_WORDS
    }


def _past_the_control(real: "set[str]", index: int) -> str:
    """A made-up value past the real range AND past the control the scan draws there (`_by_chance`).

    A made-up half drawn just past the range would fill the control band
    as densely as the copied half fills the range: such a twin is what
    a twin drawing evenly over twice the range writes, and no scan of the
    values alone can tell it from chance, so the made-up half lies past
    both.
    """
    if not real:
        return f"made up {index}"
    parts = [re.fullmatch(r"(\D*?)(\d+)(\D*)", value) for value in real]
    marks = {(part.group(1), part.group(3)) for part in parts if part}
    if all(parts) and len(marks) == 1:
        (before, after), = marks
        numbers = [int(part.group(2)) for part in parts if part]
        width = max(numbers) - min(numbers) + 1
        return f"{before}{max(numbers) + width + 1 + index}{after}"
    try:
        values = [float(value) for value in real]
    except ValueError:
        return f"made up {index}"
    spread = max(values) - min(values) or 1.0
    return f"{int(max(values) + 3 * spread) + 1 + index}"


def test_every_identifier_copied_into_the_twin_is_counted(tmp_path: pathlib.Path) -> None:
    """E0c verify of repair 1, item 1 (HIPAA): a verbatim, a shuffled and a half copy of every 'values' entry count every copied value.

    At 600 rows (BELOW THE FLOOR: the library's scan, not the command),
    each entry of the catalogue read for its real values -- every column
    answered `identifier`, and every name, address, telephone, e-mail,
    SSN, record number, ZIP and device number a name rule reaches -- has
    its real cells written as the twin: as they stand, shuffled, and in
    half the rows beside made-up values past the range and its control.
    `leaked` must count every distinct real value copied. Red on the
    density mutant (chance read from the twin's own values inside the
    real range: on sequential keys 1 to N it equals the copy, and the
    copy counted nothing at 637d4b28 for 11 of 18 identifier columns).
    """
    import random

    missed: "list[str]" = []
    for table in zoo.catalogue():
        header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
        entries = [column for column, how in zoo.leak_list(table, header) if how == "values"]
        if not entries:
            continue
        folder = tmp_path / table.name
        source = _write(folder, table, header, rows, "real")
        profile = _profile(folder, {"columns": []})
        shuffled = [list(row) for row in rows]
        halved = [list(row) for row in rows]
        draw = random.Random(7)
        expected: "dict[str, dict[str, set[str]]]" = {"verbatim": {}, "shuffled": {}, "half": {}}
        for column in entries:
            place = header.index(column)
            cells = [row[place] for row in rows]
            real = _real_values(cells)
            mixed = list(cells)
            draw.shuffle(mixed)
            for row, cell in zip(shuffled, mixed):
                row[place] = cell
            for index, row in enumerate(halved):
                if index % 2:
                    row[place] = _past_the_control(real, index)
            expected["verbatim"][column] = real
            expected["shuffled"][column] = real
            expected["half"][column] = _real_values(cells[::2])
        for name, twin_rows in (("verbatim", rows), ("shuffled", shuffled), ("half", halved)):
            twin = _write(folder, table, header, twin_rows, name)
            found = zoo.leaked(table, source, twin, profile)
            for column in entries:
                wanted = len(expected[name][column])
                got = found[zoo._leak_key(column, "values")]["twin"]
                if got != wanted:
                    missed += [f"{table.name}.{column} {name}: {got} of {wanted}"]
    assert not missed, missed


def _just_past_the_range(real: "set[str]", index: int) -> str:
    """A made-up value JUST past the real range (E0c verify 2's halfnear shape): what a twin drawing evenly over twice the range writes.

    Keys of one run of figures between constant marks continue from the
    highest real key; any other value lies past the control, as
    `_past_the_control` draws it.
    """
    parts = [re.fullmatch(r"(\D*?)(\d+)(\D*)", value) for value in real]
    marks = {(part.group(1), part.group(3)) for part in parts if part}
    if real and all(parts) and len(marks) == 1:
        (before, after), = marks
        numbers = [int(part.group(2)) for part in parts if part]
        places = max(len(part.group(2)) for part in parts if part)
        return f"{before}{max(numbers) + 1 + index:0{places}d}{after}"
    return _past_the_control(real, index)


def test_a_half_copy_beside_keys_just_past_the_range_is_counted(tmp_path: pathlib.Path) -> None:
    """E0c verify 2 item 1 (HIPAA; LANE E0c RULINGS 2 (1)): half the rows copied, half drawn just past the range, every copied value counts.

    At 600 rows (BELOW THE FLOOR: the library's scan), every 'values'
    entry of the catalogue has its real cells written as the twin in the
    even rows and made-up values just past the real range in the odd
    ones: the twin a draw over twice the range writes, whose made-up
    half fills the control band. The strict scan counts every distinct
    real value copied. Red on the mutant "chance allowance restored"
    (`len(in_twin) <= 2 * chance + 3`): at efac0822 84 of the 93 numeric
    entries counted 0 of their copied half, 18,352 copied values hidden.
    """
    missed: "list[str]" = []
    for table in zoo.catalogue():
        header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
        entries = [column for column, how in zoo.leak_list(table, header) if how == "values"]
        if not entries:
            continue
        folder = tmp_path / table.name
        source = _write(folder, table, header, rows, "real")
        profile = _profile(folder, {"columns": []})
        halved = [list(row) for row in rows]
        expected: "dict[str, set[str]]" = {}
        for column in entries:
            place = header.index(column)
            cells = [row[place] for row in rows]
            real = _real_values(cells)
            made_up = 0
            for index, row in enumerate(halved):
                if index % 2:
                    row[place] = _just_past_the_range(real, made_up)
                    made_up += 1
            expected[column] = _real_values(cells[::2])
        twin = _write(folder, table, header, halved, "halfnear")
        found = zoo.leaked(table, source, twin, profile)
        for column in entries:
            got = found[zoo._leak_key(column, "values")]
            wanted = expected[column]
            cells = sum(1 for row in halved if zoo._normal(row[header.index(column)]) in wanted)
            if got["twin"] != len(wanted) or got["twin_cells"] != cells:
                missed += [f"{table.name}.{column}: {got['twin']} of {len(wanted)}, {got['twin_cells']} of {cells} cells"]
    assert not missed, missed


def test_one_real_value_met_once_in_the_twin_counts(tmp_path: pathlib.Path) -> None:
    """LANE E0c RULINGS 2 (1): a real key the twin writes on ONE cell counts, as on 2 x most + 3 cells; no copy threshold.

    `most` is the most rows any real value holds. Red on the mutant
    "chance allowance restored" (`len(in_twin) <= 2 * chance + 3`, then
    only a value past 2 x most + 3 cells counts): one cell, and 2 x most
    + 3 cells, each counted 0 at efac0822.
    """
    import collections

    table = zoo.table_named("phi_registry")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("med_rec_no")
    source = _write(tmp_path, table, header, rows, "real")
    cells = [row[place] for row in rows]
    most = max(collections.Counter(zoo._normal(cell) for cell in cells if cell.strip()).values())
    real = _real_values(cells)
    profile = _profile(tmp_path, {"columns": []})
    for written in (1, 2 * most + 3, 2 * most + 4):
        twin_rows = [list(row) for row in rows]
        for index, row in enumerate(twin_rows):
            row[place] = cells[0] if index < written else _past_the_control(real, index)
        twin = _write(tmp_path, table, header, twin_rows, f"twin-{written}")
        found = zoo.leaked(table, source, twin, profile)["med_rec_no"]
        assert (found["twin"], found["twin_cells"]) == (1, written), (written, most, found)


def test_a_missing_word_is_no_persons_value(tmp_path: pathlib.Path) -> None:
    """E0c verify of repair 1, item 2 (V3): a ZIP column's 'UNKNOWN' cells, printed as a level, count 0; a real ZIP printed counts.

    Red without the `MISSING_WORDS` clause of the real values (the word
    would count as a ZIP published).
    """
    table = zoo.table_named("patients")
    header, rows = table.build(zoo.SMOKE_ROWS, zoo.seed_of(table))
    place = header.index("zip5")
    for row in rows[:40]:
        row[place] = "UNKNOWN"
    source = _write(tmp_path, table, header, rows, "real")
    word = _profile(tmp_path, {"columns": [{"name": "zip5", "levels": [{"label": "UNKNOWN", "rows": 40}]}]})
    assert zoo.leaked(table, source, None, word)["zip5"]["description"] == 0
    real_zip = rows[100][place]
    printed = _profile(tmp_path, {"columns": [{"name": "zip5", "levels": [{"label": "UNKNOWN"}, {"label": real_zip}]}]}, "zip")
    assert zoo.leaked(table, source, None, printed)["zip5"]["description"] == 1


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


# -- the zoo answers truthfully ------------------------------------------------------------


def _safe_harbor_question(column: str) -> "dict":
    return {"asked": [{"column": column, "answers_you_can_give": [{"answer": "no", "means": "none of these"},
        {"answer": "yes", "means": "a person, a place, a date or a number"}]}]}


def test_the_safe_harbor_question_is_answered_as_the_column_truly_is() -> None:
    """THE ZOO ANSWERS TRUTHFULLY (the orchestrator, 2026-10-25): `yes` for a ZIP, a city, a device number, a birth year or a key.

    Red on the mutant that answers `yes` only for a column the person
    knows as a record number (lane SH's first form): a ZIP answered
    `code` would then be told to name nobody. Since LANE E0c RULINGS 2
    (2) a ZIP3 area and an age column holding an age over 89 answer
    `yes` too (each pinned below); an age column whose ages all lie
    under 90 answers `no`.
    """
    cases = {
        ("patients", "zip5"): "yes", ("patients", "birth_city"): "yes", ("patients", "patient_id"): "yes",
        ("patients", "dob_us"): "yes", ("patients", "age"): "yes", ("immunizations", "udi"): "yes",
        ("safe_harbor", "birth_year"): "yes", ("safe_harbor", "age_top"): "yes", ("vitals", "pulse"): "no",
        ("vcf_calls", "rsid"): "no", ("safe_harbor", "zip3"): "yes", ("edge_columns", "age_years"): "no",
        ("well_child", "age_text"): "no", ("prenatal_visits", "gest_age_wd"): "no",
    }
    for (name, column), wanted in cases.items():
        table = zoo.table_named(name)
        document = _safe_harbor_question(column)
        asked, general = zoo.answer_generally(table, document)
        assert asked[0]["given"] == wanted, (name, column, asked)
        assert general, (name, column)


def test_a_zip3_area_names_a_place_smaller_than_a_state() -> None:
    """LANE E0c RULINGS 2 (2): safe_harbor.zip3 ('021**') is answered `yes`, though the leak scan does not read it.

    `NOT_READ` still keeps the column out of the scan (its three figures
    and '**' are the Safe Harbor form itself); a later ZIP3 allowlist of
    areas over 20,000 people is lane CODES-2's. Red on the mutant that
    lets `NOT_READ` answer the Safe Harbor question too (efac0822's
    `names_a_safe_harbor_element`, which answered `no`).
    """
    table = zoo.table_named("safe_harbor")
    assert "zip3" in zoo.NOT_READ and "zip3" not in {column for column, _how in zoo.leak_list(table, ["zip3"])}
    assert zoo.names_a_safe_harbor_element(table, "zip3") is True
    asked, _general = zoo.answer_generally(table, _safe_harbor_question("zip3"))
    assert asked[0]["given"] == "yes", asked


def test_an_age_column_holding_an_age_over_89_answers_yes() -> None:
    """LANE E0c RULINGS 2 (2): patients.age holds ages of 90 and over, so the Safe Harbor question is answered `yes` and the top-code stays.

    The answer follows the person's table: `ages_over_89` names the age
    columns with an age over 89 (patients.age, safe_harbor.age_top),
    none of edge_columns.age_years (18 to 89); handed an empty set, the
    same column answers `no`. Red on the mutant that answers every age
    `no` (efac0822's "ages over 89" exclusion), and on the one that
    answers every age `yes`.
    """
    patients = zoo.table_named("patients")
    header, rows = patients.build(zoo.SMOKE_ROWS, zoo.seed_of(patients))
    assert "age" in zoo.ages_over_89(header, rows)
    edge = zoo.table_named("edge_columns")
    assert "age_years" not in zoo.ages_over_89(*edge.build(zoo.SMOKE_ROWS, zoo.seed_of(edge)))
    asked, _general = zoo.answer_generally(patients, _safe_harbor_question("age"), zoo.ages_over_89(header, rows))
    assert asked[0]["given"] == "yes", asked
    asked, _general = zoo.answer_generally(patients, _safe_harbor_question("age"), frozenset())
    assert asked[0]["given"] == "no", asked
    asked, _general = zoo.answer_generally(edge, _safe_harbor_question("age_years"))
    assert asked[0]["given"] == "no", asked
    assert zoo.ages_over_89(["age"], [["89"], ["90 years"], [""]]) == frozenset({"age"})
    assert zoo.ages_over_89(["age"], [["89"], ["89.9"], ["UNK"], ["1203"]]) == frozenset()


# -- every round of the questions file answered ----------------------------------------------


def test_a_question_put_after_another_answer_is_answered(tmp_path: pathlib.Path) -> None:
    """LANE E0c RULINGS 2 (3): run_table answers every round until no new question is put.

    The real product: titled_report's header is found only once the
    title rows are answered, and the next round puts report_ref's
    question, which the zoo answers `identifier`. Red on the one-round
    mutant (efac0822's run_table: one answer_generally, one profile
    --answers), under which report_ref stayed unanswered.
    """
    table = zoo.table_named("titled_report")
    result = zoo.run_table(table, tmp_path, zoo.SMOKE_ROWS, zoo.seed_of(table))
    given = [(entry["column"], entry["given"]) for entry in result["asked"]]
    assert result["answer_rounds"] == 2, (result["answer_rounds"], given)
    assert ("report_ref", "identifier") in given, given
    assert all(step["exit"] == 0 for step in result["steps"].values()), result["steps"]


def _put_after_each_answer(monkeypatch: pytest.MonkeyPatch, put: "object") -> "list[tuple[str, str]]":
    """Run the real commands, and after each profile --answers put the questions `put(round)` returns.

    The questions this test put are taken out again before the product
    reads the file, so the product meets only its own; the answers the
    zoo gave them are returned, in order.
    """
    quietly = zoo._quietly
    given: "list[tuple[str, str]]" = []
    rounds = [0]

    def answering(arguments: "list[str]", small_tables_refused: bool = False) -> "tuple[int, str]":
        if "--answers" not in arguments:
            return quietly(arguments, small_tables_refused)
        path = pathlib.Path(arguments[arguments.index("--answers") + 1])
        document = json.loads(path.read_text(encoding="utf-8"))
        ours = [entry for entry in document.get("asked") or [] if entry.get("put_by_this_test")]
        given.extend([(f"{entry.get('column') or entry.get('subject')}", f"{entry.get('your_answer')}") for entry in ours])
        document["asked"] = [entry for entry in document.get("asked") or [] if not entry.get("put_by_this_test")]
        path.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        code, error = quietly(arguments, small_tables_refused)
        rounds[0] += 1
        document = json.loads(path.read_text(encoding="utf-8"))
        document["asked"] = (document.get("asked") or []) + put(rounds[0])  # type: ignore[operator]
        path.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        return code, error

    monkeypatch.setattr(zoo, "_quietly", answering)
    return given


def test_the_safe_harbor_question_that_follows_a_code_answer_is_answered(
    monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path,
) -> None:
    """LANE E0c RULINGS 2 (3) with LANE SH ADDENDUM 7: zip5 answered `code`, then put the Safe Harbor question, is answered `yes`.

    The follow-up question is put by this test after the first profile
    --answers, as lane SH's product puts it (not on this base); the next
    round answers it truthfully and the run stops when no new question
    is put. Red on the one-round mutant (the question left unanswered).
    """
    def safe_harbor(round_: int) -> "list[dict]":
        if round_ != 1:
            return []
        question = _safe_harbor_question("zip5")["asked"][0]
        return [{**question, "your_answer": "", "put_by_this_test": True}]

    given = _put_after_each_answer(monkeypatch, safe_harbor)
    table = zoo.table_named("patients")
    result = zoo.run_table(table, tmp_path, 150, zoo.seed_of(table))
    assert given == [("zip5", "yes")], given
    assert result["answer_rounds"] == 2, result["answer_rounds"]
    assert ("zip5", "code") in [(entry["column"], entry["given"]) for entry in result["asked"]]
    assert ("zip5", "yes") in [(entry["column"], entry["given"]) for entry in result["asked"]]


def test_the_rounds_of_answers_are_bounded(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """A questions file that puts a new question after every answer is answered ANSWER_ROUNDS_AT_MOST rounds, then the run goes on."""
    def another(round_: int) -> "list[dict]":
        return [{
            "subject": f"the file, round {round_}", "put_by_this_test": True, "your_answer": "",
            "answers_you_can_give": [{"answer": "no", "means": "none of these"}, {"answer": "yes", "means": "one"}],
        }]

    given = _put_after_each_answer(monkeypatch, another)
    table = zoo.table_named("patients")
    result = zoo.run_table(table, tmp_path, 150, zoo.seed_of(table))
    assert result["answer_rounds"] == zoo.ANSWER_ROUNDS_AT_MOST, result["answer_rounds"]
    assert len(given) == zoo.ANSWER_ROUNDS_AT_MOST - 1, given
    assert result["steps"]["generate"]["exit"] == 0, result["steps"]

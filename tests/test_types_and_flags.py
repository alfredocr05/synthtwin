"""P4-D447 (lane CZ-D): types, codes and flags, eight invented forms.

THE FORMS (`tests/types_flags_zoo.py`): eight invented look-alikes with
generic column names, built from the zoo's own makers and seeds --
whole-number category codes beside figures kept with a leading nought,
dense Y/N flags in three spellings and yes-only columns, a wide mart of
180 columns with 70 1-or-blank indicators, near-empty measures beside
full columns, frequency and route words with an as-needed flag, a
Windows-1252 file whose units hold the micro and degree signs, a table of
60 columns of every role, and codes and flags with a level 1 to 10 people
hold on 11 rows or more.

WHAT THE GATE HOLDS. Each form's maker is pinned to its own counts. Each K-HZ-17 count is red on its own spoil of an exact copy
(a code written `3.0`, a held-back level written `group-1` in an integer
column, blanks written `N`, an indicator written `1.0`, the as-needed
words dropped, the single-byte file rewritten as UTF-8, a date at
midnight given a clock, a source value or a present count of a rare
column in the description, a level 1 to 10 people hold in any column's
block, a common level's cells moved onto another level of the source, a leak, a validator's
miss, a step's exit, made-up codes past the held rows, a fault of the
whole file, a check that fails on the source, a lost level), and the exact
copy reads nought on every one. Six forms run end to end at 600 rows, below
the owner's table floor, through the command's internal switch: the five
small ones and the person-held form; ONE case per writer at the floor
size: the codes form at 20,000 rows, its integer columns keeping their
pandas dtype, their spellings and their == and isin row shares, with no
group-N and no text cell in a column of numbers. The rest of the 20,000-
row legs -- every form and the wide mart's seconds -- are
`tools/measurements/kpi_types_and_flags.py`'s, under `kpi_run.py --slow`.
"""

from __future__ import annotations

import dataclasses
import json
import pathlib
import re
import shutil
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import health_zoo  # noqa: E402
import types_flags_zoo as zoo  # noqa: E402

COLUMN_NAME_FORM = re.compile(r"[a-z]+(_[a-z0-9]+)*")


def _cells(build: object, rows: int, seed: int = zoo.SEED) -> "dict[str, list[str]]":
    header, body = build(rows, seed)  # type: ignore[operator]
    return {name: [row[place] for row in body] for place, name in enumerate(header)}


def test_every_column_name_is_generic_and_every_form_is_named() -> None:
    assert tuple(table.name for table in zoo.tables()) == zoo.FORMS
    for table in zoo.tables():
        header = table.kinds[table.name]
        assert len(set(header)) == len(header)
        assert all(COLUMN_NAME_FORM.fullmatch(name) for name in header), table.name


def test_the_codes_form_holds_a_dozen_integer_codes_with_long_tails() -> None:
    cells = _cells(zoo.codes, 20_000)
    codes = [name for name in cells if name.endswith("_code")]
    assert len(codes) == 16
    nought = [name for name, *_rest, leading in zoo.CODE_COLUMNS if leading]
    assert len(nought) == 5
    for name in codes:
        present = [cell for cell in cells[name] if cell]
        levels = {cell: present.count(cell) for cell in set(present)}
        assert 2 <= len(levels) <= 52, name
        assert all(re.fullmatch(r"\d+", cell) for cell in levels), name
    tails = [name for name in codes if any(0 < cells[name].count(value) < 11 for value in set(cells[name]) if value)]
    assert len(tails) >= 10
    assert sum(1 for name in codes if "" in cells[name]) >= 8


def test_the_flags_form_spells_yes_and_no_three_ways() -> None:
    cells = _cells(zoo.flags, 2_000)
    yn = [name for name in cells if set(cells[name]) == {"Y", "N", ""}]
    assert len(yn) == zoo.FLAG_COUNT
    assert set(cells["consent_ynu"]) == {"Y", "N", "U", ""}
    assert set(cells["is_deceased"]) == {"Y", ""}
    assert set(cells["is_enrolled"]) == {"Y", "N"}
    assert set(cells["is_smoker_10"]) == {"1", "0", ""}
    assert set(cells["has_alert_yesno"]) == {"Yes", "No", ""}
    assert set(cells["screened_1"]) == set(cells["followup_1"]) == {"1", ""}


def test_the_wide_mart_holds_its_indicators_and_its_rare_ones() -> None:
    cells = _cells(zoo.wide_mart, 600)
    assert len(cells) == 180
    indicators = [name for name in cells if name.startswith("hx_indicator_")]
    assert len(indicators) == 70
    for place in range(zoo.RARE_INDICATORS):
        assert 1 <= cells[indicators[place]].count("1") <= 10
    assert sum(1 for name in cells if name.endswith("_code")) == 10
    stamps = [name for name in cells if name.endswith("_dttm")]
    assert len(stamps) == 18
    assert sum(1 for name in stamps if all(cell.endswith(" 00:00:00.000") for cell in cells[name] if cell)) == 6
    assert sum(1 for name in cells if name.startswith("count_")) == 30


def test_the_role_mix_holds_every_role_and_a_two_part_key() -> None:
    cells = _cells(zoo.role_mix, 3_000)
    assert len(cells) == 60
    roles = [zoo.role_of("role_mix", name) for name in cells]
    assert {role: roles.count(role) for role in set(roles)} == {
        "key": 9, "code": 16, "flag": 6, "datetime": 12, "measurement": 8, "text": 6, "amount": 3,
    }
    keys = [name for name in cells if zoo.role_of("role_mix", name) == "key"]
    assert sum(1 for name in keys if all(len(cell) == 18 and cell.isdigit() for cell in cells[name])) == 3
    assert sum(1 for name in cells if name.startswith("kind_")) == 6
    stamps = [name for name in cells if name.endswith("_dttm")]
    assert sum(1 for name in stamps if all(cell.endswith(" 00:00:00.000") for cell in cells[name] if cell)) == 4
    pairs = list(zip(cells["parent_key"], cells["line_no"]))
    assert len(set(pairs)) == len(pairs)
    assert all(re.fullmatch(r"-?\d+\.\d\d", cell) for cell in cells["amount_01"])


# -- each K-HZ-17 count, red on its own spoil -------------------------------


def _held_as_described(table: health_zoo.Table, header: "list[str]", body: "list[list[str]]") -> "list[dict]":
    """Each code column's block as a floor-keeping description states it: the rows of the levels 1 to 10 people hold are held back."""
    people = [row[header.index(table.person)] for row in body]
    blocks: "list[dict]" = []
    for place, column in enumerate(header):
        if zoo.role_of(table.name, column) == "code":
            cells = [row[place] for row in body]
            few = zoo._few_held(zoo._holders(cells, people))
            blocks += [{"name": column, "suppressed_rows": sum(1 for cell in cells if cell in few)}]
    return blocks


def _copy(
    table: health_zoo.Table, folder: pathlib.Path, spoil: object, key: str, edit: object = None,
) -> "dict[str, object]":
    """Write the form and a twin that is its exact copy, spoiled by ``spoil``; the counts form_measures reads.

    ``edit`` changes the description and the run's result the form is read with;
    the description holds back the source's few-people levels (`_held_as_described`).
    """
    shutil.rmtree(folder, ignore_errors=True)
    source = health_zoo.write_table(table, folder, 600, zoo.seed_of(table))
    header, body = table.build(600, zoo.seed_of(table))
    described: "dict" = {"columns": _held_as_described(table, header, body)}
    if spoil is not None:
        spoil(header, body)  # type: ignore[operator]
    twin = folder / f"{table.name}-twin{table.suffix}"
    data = table.write(header, body)
    if key == "utf8":
        data = data.decode("cp1252").encode("utf-8")
    if key == "crlf":
        data = data.replace(b"\n", b"\r\n")
    twin.write_bytes(data)
    real = health_zoo.analyse(table, source)
    made = health_zoo.analyse(table, twin)
    result = {
        "steps": {step: {"exit": 0} for step in ("profile", "answers", "generate", "validate")},
        "analyst": [list(failure) for failure in health_zoo.analyst_failures(table, real, made)],
        "analyst_real_errors": health_zoo.real_faults(table, real),
        "misses": [],
        "leaks": {},
    }
    if edit is not None:
        edit(described, result)  # type: ignore[operator]
    (folder / f"{table.name}-profile.json").write_text(json.dumps(described), encoding="utf-8", newline="\n")
    return zoo.form_measures(table, result, folder)


def _every(column: str, how: object) -> object:
    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        for row in rows:
            row[place] = how(row[place])  # type: ignore[operator]

    return change


def _first(column: str, value: str, count: int = 1) -> object:
    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        done = 0
        for row in rows:
            if row[place] and done < count:
                row[place] = value
                done = done + 1

    return change


def _changed(column: str, how: object) -> object:
    """Every cell of a column through ``how(cell, seen)``, ``seen`` counting that value's earlier cells."""

    def change(header: "list[str]", rows: "list[list[str]]") -> None:
        place = header.index(column)
        seen: "dict[str, int]" = {}
        for row in rows:
            seen[row[place]] = seen.get(row[place], 0) + 1
            row[place] = how(row[place], seen[row[place]])  # type: ignore[operator]

    return change


SPOILS = (
    ("codes", _first("status_code", "3.0"), "", "spelling"),
    ("codes", _first("status_code", "group-1", 4), "", "dtype"),
    ("codes", _first("status_code", "group-1", 4), "", "group_n"),
    ("codes", _first("status_code", "group-1", 4), "", "text_cells_in_number_columns"),
    ("codes", _every("status_code", lambda cell: "1" if cell in ("2", "3") else cell), "", "filter_share"),
    ("flags", _every("hx_indicator_01", lambda cell: cell or "N"), "", "blank_share"),
    ("flags", _first("has_alert_yesno", "Y"), "", "spelling"),
    ("frequency_route", _every("frequency_text", lambda cell: cell.replace(" as needed", "")), "", "filter_share"),
    ("single_byte_units", None, "utf8", "spelling"),
    ("role_mix", _every("event_01_dttm", lambda cell: cell.replace(" 00:00:00.000", " 07:13:41.250")), "", "spelling"),
    ("role_mix", _first("type_01_code", "1.0"), "", "spelling"),
    ("role_mix", _first("count_01", "3.0"), "", "spelling"),
    ("role_mix", _first("amount_01", "3.5"), "", "spelling"),
    ("role_mix", _first("entity_01_key", "1.0E17"), "", "spelling"),
    ("wide_mart", _every("event_02_dttm", lambda cell: cell.replace(":00.000", ":41.250")), "", "spelling"),
    ("wide_mart", _every("event_01_dttm", lambda cell: cell.replace(" 00:00:00.000", " 07:13:00.000")), "", "spelling"),
    ("wide_mart", _first("group_02_code", "1.0"), "", "spelling"),
    ("wide_mart", _first("count_02", "3.0"), "", "spelling"),
    ("flags", _first("hx_indicator_01", "y"), "", "spelling"),
    ("codes", _every("status_code", lambda cell: "2" if cell == "1" else cell), "", "other"),
)


@pytest.mark.parametrize("form,spoil,key,count", SPOILS, ids=[f"{form}-{count}-{place}" for place, (form, _s, _k, count) in enumerate(SPOILS)])
def test_each_count_is_red_on_its_spoil_and_nought_on_the_copy(
    tmp_path: pathlib.Path, form: str, spoil: object, key: str, count: str
) -> None:
    table = zoo.tables()[zoo.FORMS.index(form)]
    clean = _copy(table, tmp_path / "clean", None, "")
    assert clean[count] == 0 and not clean["failing_columns"], clean
    spoiled = _copy(table, tmp_path / "spoiled", spoil, key)
    assert int(spoiled[count]) > 0, spoiled  # type: ignore[call-overload]
    assert spoiled["failing_columns"] or count == "group_n"


def test_an_indicator_written_one_point_nought_is_a_spelling_fault(tmp_path: pathlib.Path) -> None:
    table = zoo.tables()[zoo.FORMS.index("wide_mart")]
    spoiled = _copy(table, tmp_path / "spoiled", _first("hx_indicator_020", "1.0"), "")
    assert spoiled["spelling"] == 1
    assert spoiled["failing_columns"] == ["hx_indicator_020"]


def _block(described: "dict", column: str, **facts: object) -> None:
    """A column's block given these facts, beside the facts it holds already."""
    old = [block for block in described["columns"] if block["name"] == column]
    described["columns"] = [block for block in described["columns"] if block["name"] != column] + [
        {**(old[0] if old else {"name": column}), **facts}
    ]


def _present_count(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_003", n_present=3)


def _held_count(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_003", suppressed_rows=3)


def _present_as_numbers(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_003", n_numeric=3)


def _present_as_words(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_003", n_not_numeric=3)


def _present_as_the_rows_less_missing(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_003", n_missing=597)


def _published(column: str, label: str, count: int, *, variant: str = "", withheld: str = "") -> object:
    """A block publishing a level in the product's own shape: its label, and the spellings under it."""

    def edit(described: "dict", _result: "dict") -> None:
        level: "dict[str, object]" = {"label": label, "count": count, "variants": {variant or label: count}}
        if withheld:
            level["variants_withheld"] = {withheld: count}
        _block(described, column, levels=[level])

    return edit


def _label_only(described: "dict", _result: "dict") -> None:
    """A level named by its label alone: every spelling under it held back, the withheld keys row counts."""
    _block(described, "few_people_code", levels=[{"label": "6", "count": 20, "variants": {}, "variants_withheld": {"10": 2}}])


def _rare_level(described: "dict", _result: "dict") -> None:
    _block(described, "hx_indicator_001", levels=[{"value": "1", "count": 1}])


def _a_leak(_described: "dict", result: "dict") -> None:
    result["leaks"] = {"record_key|values": {"column": "record_key", "how": "values", "description": 0, "twin": 3}}


def _a_miss(_described: "dict", result: "dict") -> None:
    result["misses"] = [["status_code", "mean"]]


def _a_step(_described: "dict", result: "dict") -> None:
    result["steps"]["generate"]["exit"] = 2


EDITS = (
    ("wide_mart", _present_count, "rare_counts_published", ["hx_indicator_003"]),
    ("wide_mart", _held_count, "rare_counts_published", ["hx_indicator_003"]),
    ("wide_mart", _present_as_numbers, "rare_counts_published", ["hx_indicator_003"]),
    ("wide_mart", _present_as_words, "rare_counts_published", ["hx_indicator_003"]),
    ("wide_mart", _present_as_the_rows_less_missing, "rare_counts_published", ["hx_indicator_003"]),
    ("codes", _published("status_code", "9", 4), "rare_values_published", ["status_code"]),
    ("person_held", _published("few_people_code", "6", 20), "rare_values_published", ["few_people_code"]),
    ("person_held", _published("is_flag_p8", "Y", 32), "rare_values_published", ["is_flag_p8"]),
    ("person_held", _published("few_people_code", "5", 20, variant="6"), "rare_values_published", ["few_people_code"]),
    ("person_held", _published("few_people_code", "5", 20, withheld="6"), "rare_values_published", ["few_people_code"]),
    ("person_held", _label_only, "rare_values_published", ["few_people_code"]),
    ("wide_mart", _rare_level, "rare_values_published", ["hx_indicator_001"]),
    ("codes", _a_leak, "leaks", ["record_key"]),
    ("codes", _a_miss, "validate_misses", ["status_code"]),
    ("codes", _a_step, "steps_failing", []),
)


@pytest.mark.parametrize("form,edit,count,columns", EDITS, ids=[f"{form}-{count}-{place}" for place, (form, _e, count, _c) in enumerate(EDITS)])
def test_each_count_of_the_run_is_red_on_its_edit_and_nought_on_the_copy(
    tmp_path: pathlib.Path, form: str, edit: object, count: str, columns: "list[str]"
) -> None:
    table = zoo.tables()[zoo.FORMS.index(form)]
    assert _copy(table, tmp_path / "clean", None, "")[count] == 0
    spoiled = _copy(table, tmp_path / "spoiled", None, "", edit)
    assert int(spoiled[count]) > 0, spoiled  # type: ignore[call-overload]
    assert spoiled["failing_columns"] == columns


def _held_rows(column: str, rows: int) -> object:
    def edit(described: "dict", _result: "dict") -> None:
        _block(described, column, suppressed_rows=rows)

    return edit


def _codes_form() -> health_zoo.Table:
    return zoo.tables()[zoo.FORMS.index("codes")]


def test_a_held_level_stand_in_within_the_held_rows_is_the_floors_price(tmp_path: pathlib.Path) -> None:
    spoil = _changed("status_code", lambda cell, _seen: "6" if cell == "9" else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "", _held_rows("status_code", 4))
    assert found["made_up_codes"] == 1 and found["codes_past_held"] == 0
    assert found["failing_columns"] == []


def test_a_common_level_published_reads_nothing(tmp_path: pathlib.Path) -> None:
    """The reading of published levels names only those 1 to 10 people hold: `common_code`'s `1` and the flag's `N` are the control."""
    table = zoo.tables()[zoo.FORMS.index("person_held")]
    for place, (column, label) in enumerate((("common_code", "1"), ("is_flag_p8", "N"))):
        found = _copy(table, tmp_path / f"{place}", None, "", _published(column, label, 200))
        assert found["rare_values_published"] == 0 and found["failing_columns"] == []


def test_a_common_level_moved_onto_the_next_real_level_costs_the_column(tmp_path: pathlib.Path) -> None:
    """`status_code`'s `4` moved to the real `5`, one kept: no code is new, and the analyst's filters name neither."""
    spoil = _changed("status_code", lambda cell, seen: "5" if cell == "4" and seen > 1 else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "")
    assert found["filter_share"] == 1 and found["codes_past_held"] == 0
    assert found["failing_columns"] == ["status_code"]


def test_common_levels_moved_onto_a_rare_real_level_cost_the_column(tmp_path: pathlib.Path) -> None:
    """Codex's shape aimed at a level the real writes: `4` and `5` moved onto `9`, one of each kept."""
    spoil = _changed("status_code", lambda cell, seen: "9" if cell in ("4", "5") and seen > 1 else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "")
    assert found["filter_share"] == 1 and found["codes_past_held"] == 1
    assert found["failing_columns"] == ["status_code"]


def test_a_wide_code_level_moved_onto_another_costs_the_column(tmp_path: pathlib.Path) -> None:
    spoil = _changed("group_02_code", lambda cell, seen: "3" if cell == "2" and seen > 1 else cell)
    found = _copy(zoo.tables()[zoo.FORMS.index("wide_mart")], tmp_path, spoil, "")
    assert found["filter_share"] == 1 and found["failing_columns"] == ["group_02_code"]


def test_cells_on_a_rare_real_level_past_the_held_rows_cost_the_column(tmp_path: pathlib.Path) -> None:
    """`5` moved onto the rare `9`, under the tolerance: the held rows alone bound it."""
    spoil = _changed("status_code", lambda cell, seen: "9" if cell == "5" and seen > 1 else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "")
    assert found["filter_share"] == 0 and found["codes_past_held"] == 1
    assert found["failing_columns"] == ["status_code"]


def test_a_column_counts_once_where_an_analyst_filter_also_failed(tmp_path: pathlib.Path) -> None:
    spoil = _every("status_code", lambda cell: "1" if cell in ("2", "3") else cell)
    assert _copy(_codes_form(), tmp_path, spoil, "")["filter_share"] == 1


def test_made_up_codes_past_the_held_rows_cost_the_column(tmp_path: pathlib.Path) -> None:
    """Most of one common level moved onto a code the real never writes, one cell kept: dtype and filters hold."""
    spoil = _changed("status_code", lambda cell, seen: "6" if cell == "5" and seen > 1 else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "", _held_rows("status_code", 4))
    assert found["dtype"] == 0 and found["filter_share"] == 0
    assert found["codes_past_held"] == 1 and found["made_up_codes"] == 0
    assert found["failing_columns"] == ["status_code"]


def test_made_up_codes_with_no_held_rows_cost_the_column(tmp_path: pathlib.Path) -> None:
    spoil = _changed("status_code", lambda cell, _seen: "6" if cell == "9" else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "", _held_rows("status_code", 0))
    assert found["codes_past_held"] == 1 and found["failing_columns"] == ["status_code"]


@pytest.mark.parametrize("written", ("6.0", "60", "6x"))
def test_made_up_codes_off_the_columns_form_cost_the_column(tmp_path: pathlib.Path, written: str) -> None:
    """A column of one-figure codes: a stand-in within the held rows, written with a point or in a width the column never writes."""
    spoil = _changed("status_code", lambda cell, _seen: written if cell == "9" else cell)
    found = _copy(_codes_form(), tmp_path, spoil, "", _held_rows("status_code", 4))
    assert found["codes_past_held"] == 1 and found["made_up_codes"] == 0
    assert "status_code" in found["failing_columns"]  # type: ignore[operator]


def test_a_fault_of_the_whole_file_is_the_whole_forms(tmp_path: pathlib.Path) -> None:
    table = _codes_form()
    clean = _copy(table, tmp_path / "clean", None, "")
    assert clean["file_wide"] == 0 and clean["failing_columns"] == []
    spoiled = _copy(table, tmp_path / "spoiled", None, "crlf")
    assert int(spoiled["file_wide"]) > 0  # type: ignore[call-overload]


def test_a_validators_miss_on_the_file_is_the_whole_forms(tmp_path: pathlib.Path) -> None:
    table = _codes_form()

    def miss(_described: "dict", result: "dict") -> None:
        result["misses"] = [["", "rows"]]

    spoiled = _copy(table, tmp_path, None, "", miss)
    assert spoiled["file_wide"] == 1 and spoiled["validate_misses"] == 1


def test_a_check_that_fails_on_the_source_fails_its_column(tmp_path: pathlib.Path) -> None:
    """A broken filter raises on both files, so `analyst_failures` compares nothing: its column fails."""

    def broken(_frames: "dict[str, object]") -> object:
        raise KeyError("no such column")

    base = _codes_form()
    table = dataclasses.replace(base, checks=base.checks + (health_zoo.Check("codes", "status_code: a broken filter", "share", broken, "status_code"),))
    found = _copy(table, tmp_path, None, "")
    assert found["source_check_errors"] == 1
    assert found["failing_columns"] == ["status_code"]


def test_a_near_empty_forms_count_written_three_point_nought_is_a_spelling_fault(tmp_path: pathlib.Path) -> None:
    table = zoo.tables()[zoo.FORMS.index("near_empty")]
    found = _copy(table, tmp_path, _first("full_count", "3.0"), "")
    assert found["spelling"] == 1 and "full_count" in found["failing_columns"]  # type: ignore[operator]


def test_a_near_empty_measures_real_value_in_the_twin_is_counted(tmp_path: pathlib.Path) -> None:
    table = zoo.tables()[zoo.FORMS.index("near_empty")]

    def made_up(keep: int) -> object:
        def change(header: "list[str]", rows: "list[list[str]]") -> None:
            for column in zoo.NEAR_EMPTY:
                place = header.index(column)
                kept = 0
                for row in rows:
                    if row[place]:
                        kept = kept + 1
                        if kept > keep:
                            row[place] = "1.5"

        return change

    assert _copy(table, tmp_path / "clean", made_up(0), "")["rare_values_published"] == 0
    found = _copy(table, tmp_path / "spoiled", made_up(1), "")
    assert int(found["rare_values_published"]) > 0  # type: ignore[call-overload]
    assert set(found["failing_columns"]) == set(zoo.NEAR_EMPTY)  # type: ignore[call-overload]


def test_a_real_level_few_people_hold_met_in_the_twin_is_recorded_apart(tmp_path: pathlib.Path) -> None:
    """`adjacent_code`'s `6`: the next free number, so a stand-in comes back as the held level; no fault, a count."""
    found = _copy(_codes_form(), tmp_path / "copy", None, "")
    assert int(found["held_levels_met_cells"]) > 0  # type: ignore[call-overload]
    assert found["failing_columns"] == []
    spoil = _changed("adjacent_code", lambda cell, _seen: "1" if cell == "6" else cell)
    fewer = _copy(_codes_form(), tmp_path / "fewer", spoil, "")
    assert int(fewer["held_levels_met_cells"]) == int(found["held_levels_met_cells"]) - 4  # type: ignore[call-overload]


def test_the_person_held_form_holds_levels_of_few_people_on_many_rows() -> None:
    cells = _cells(zoo.person_held, 20_000)
    people = cells["patient_key"]
    for column, level in (
        ("few_people_code", "6"), ("few_people_nought_code", "09"), ("person_home_code", "100"), ("person_home_code", "101"), ("is_flag_p8", "Y"),
        ("has_alert_p5", "Yes"), ("is_smoker_p8", "1"), ("ind_5people", "1"),
    ):
        held = [who for who, cell in zip(people, cells[column]) if cell == level]
        assert len(held) >= 11, column
        assert 1 <= len(set(held)) <= 10, column
    assert cells["common_code"].count("1") > 5_000


def test_the_ledger_bounds_every_count_at_both_sizes() -> None:
    """A count the ledger leaves out reddens nothing: every K-HZ-17 count but those recorded apart has its bound and target."""
    ledger = json.loads((pathlib.Path(__file__).resolve().parent / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    entry = next(kpi for kpi in ledger["entries"] if kpi["id"] == "K-HZ-17")
    for count in zoo.COUNTS:
        bounded = count not in zoo.RECORDED_APART
        for rows in (600, 20_000):
            assert (f"{count}_{rows}_rows" in entry["expected"]) == bounded, (count, rows)
        assert (f"{count}_20000_rows" in entry["target"]) == bounded, count
        assert f"{count}_20000_rows" in entry["value_at"]["value"], count


# -- end to end ---------------------------------------------------------------

SMALL_FORMS = ("codes", "flags", "near_empty", "frequency_route", "single_byte_units")
CLEAN_KEYS = (
    "steps_failing", "dtype", "spelling", "filter_share", "text_cells_in_number_columns", "leaks", "validate_misses",
    "codes_past_held", "source_check_errors", "file_wide",
)
NO_CODES_KEY = tuple(key for key in CLEAN_KEYS if key != "codes_past_held")


@pytest.mark.parametrize("form", SMALL_FORMS)
def test_below_the_floor_each_small_form_keeps_its_types_spellings_and_shares(tmp_path: pathlib.Path, form: str) -> None:
    table = zoo.tables()[zoo.FORMS.index(form)]
    result = health_zoo.run_table(table, tmp_path / form, health_zoo.SMOKE_ROWS, zoo.seed_of(table))
    found = zoo.form_measures(table, result, tmp_path / form)
    for key in (*CLEAN_KEYS, "rare_values_published", "blank_share"):
        assert found[key] == 0, (key, found, result["analyst"])
    # Below the floor a rare word's stand-in moves the word columns' shapes (limit (3) of P4-D447).
    assert found["other"] == (2 if form == "frequency_route" else 0), result["analyst"]
    # Limit (4) of P4-D447 is closed by its owner: lane PL's rule (P4-D453,
    # merged beside this gate in batch 4o) counts a column 1 to 10 people
    # fill absent and writes it blank, so no present count is published
    # (the near-empty form published all three on batch 4m's head).
    assert found["rare_counts_published"] == 0, found


def test_below_the_floor_a_level_few_people_hold_is_pooled_and_publishes_nothing(tmp_path: pathlib.Path) -> None:
    """Limit (3) of P4-D447, closed by its owner: lane PL's pool in people (P4-D453), merged beside this gate in batch 4o.

    On batch 4m's head the whole column's hold cost at least three filter
    shares here; with the pool every filter keeps its row share, and HIPAA
    holds as before.
    """
    table = zoo.tables()[zoo.FORMS.index("person_held")]
    result = health_zoo.run_table(table, tmp_path / "held", health_zoo.SMOKE_ROWS, zoo.seed_of(table))
    found = zoo.form_measures(table, result, tmp_path / "held")
    assert found["leaks"] == 0 and found["rare_values_published"] == 0 and found["dtype"] == 0
    assert found["filter_share"] == 0, found
    assert "common_code" not in found["failing_columns"]  # type: ignore[operator]


def test_at_the_floor_integer_codes_keep_their_dtype_spellings_and_filter_shares(tmp_path: pathlib.Path) -> None:
    """ONE case per writer at the owner's table floor: the codes form at 20,000 rows, the shipped floor on."""
    table = zoo.tables()[zoo.FORMS.index("codes")]
    result = health_zoo.run_table(table, tmp_path / "codes", health_zoo.KPI_ROWS, zoo.seed_of(table), small_tables_refused=True)
    found = zoo.form_measures(table, result, tmp_path / "codes")
    for key in (*NO_CODES_KEY, "group_n", "other"):
        assert found[key] == 0, (key, found, result["analyst"])
    # Limit (7) of P4-D447, CLOSED by lane CODES-2 (plan P4-D471): the codes,
    # answered `code` and their Safe Harbor question `no` as the zoo answers,
    # name their held-back levels beside the pooled total, so `198` and `199`
    # beside 100 to 127 are written as themselves, never `128` and `99`.
    assert found["codes_past_held"] == 0 and found["failing_columns"] == [], found
    # Every held-back level is written by its own name: the 93 cells of the
    # fourteen named pools meet the levels the source holds back.
    assert found["held_levels_met_cells"] == 93
    # ...so no held-back level is made up (rule A3's stand-ins, P4-D439, are
    # left to columns that name no pool).
    assert int(found["made_up_codes"]) == 0  # type: ignore[call-overload]

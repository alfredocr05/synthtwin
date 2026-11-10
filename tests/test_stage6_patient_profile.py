"""The patient layer's profile side, behind the chain's switch (lane GRa, plan P4-D449; contract 4.6c, NOT IN FORCE).

THE GATE OF LANE GRa. Several rows per patient are described in patients
where contract 4.6c.3's gate holds, and only behind the chain's switch:
`synthtwin profile` never turns the switch on, so every shipped
description, summary and twin stays byte for byte today's. This file
holds, each rule red on its mutant (the mutants are named beside each
case and run by the lane's mutation script):

- THE SWITCH OFF MOVES NO BYTE: an unswitched description of a table of
  several rows a patient carries no `grain` and keeps the person column's
  own repetition census; the loader refuses `grain` without the switch;
- THE GATE: one person column, no tabled row without a person value,
  at least `f` extra rows; two person columns or a blank person cell
  turn it off;
- THE CENSUS OF `r`: no band of 1 to `f - 1` patients is published; the
  deficit search agrees with the complete three-value search; the page's
  census cases (Codex's, the 99 patients of 10,000 rows, every census of
  11 to 20 patients of 1 to 5 rows);
- NO PATIENT-LEVEL CELL OF 1 TO `f - 1`: every family of the patient
  chain, every own-mean band (at least `max(2 f, f + 4)`), every row
  family's cell in rows;
- THE PERSON COLUMN'S CENSUS UNDER NO OTHER NAME: its multiplicity map
  withheld, its row-counting keys read over the patients, every other
  repeating map withheld;
- COMPLETE FOLLOW-UP: no `Q_P` where every patient holds every visit;
- THE SUBJECT QUESTION'S HOLD: no chain while it is open, in the library
  and through the command, and its answers release it;
- THE LOADER'S S29 TO S33 on a switched description, each red on a
  mutation of it;
- THE PAGE'S FIXTURES (4.6c.10 items 1 and 3 to 6), each with its reading.

Every fixture is invented here; the key is a fixed test key.
"""

import dataclasses
import io
import itertools
import json
import os
import pathlib
import math
import random
import re
import types
import typing

import pytest

import fixtures

from synthtwin import (
    asking,
    chain,
    cli,
    contract,
    errors,
    patient_layer,
    patient_rules,
    profile,
    reading,
    summary,
    taxonomy,
)

FLOOR = 11
TEST_KEY = bytes(range(32))


def _csv(header: "list[str]", rows: "list[list[str]]") -> str:
    out = io.StringIO()
    out.write(",".join(header) + "\n")
    for row in rows:
        out.write(",".join(row) + "\n")
    return out.getvalue()


def _visits(patients: int, seed: int, dropout: bool = True, keys: str = "code") -> "tuple[list[str], list[list[str]]]":
    """An invented visit table: an arm, a gender, an age, a visit date, a reading with a trend, a site."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        arm = draw.choice(["a", "b"])
        gender = draw.choice(["F", "M"])
        age = draw.randint(30, 80)
        visits = draw.randint(1, 8) if dropout else 8
        base = draw.gauss(100, 12)
        slope = 1.5 if arm == "b" else 0.3
        for j in range(visits):
            day = 1 + 30 * j + draw.randint(0, 5)
            date = f"{2024 + day // 336}-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}"
            key = f"S{patient:05d}" if keys == "code" else f"{patient + 1}"
            rows += [[key, arm, gender, f"{age}", date, f"{base + slope * j + draw.gauss(0, 6):.1f}", draw.choice(["clinic", "home", "phone"])]]
    return ["pid", "arm", "gender", "age", "visit_date", "value", "site"], rows


def _described(
    tmp_path: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    persons: "tuple[str, ...]" = ("pid",),
    rows_per_person: str = chain.ROWS_PERSON,
    name: str = "visits",
    floor: int = FLOOR,
    key: bytes = TEST_KEY,
    top_code: bool = False,
    held: "tuple[str, ...]" = (),
    held_by_person: "tuple[str, ...]" = (),
) -> "tuple[dict[str, object], chain.Chained]":
    """A table described by the library with its person columns, and its chain behind the switch."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(tmp_path, f"{name}.csv", _csv(header, rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=floor), person_columns=persons)
    table = reading.read_table(str(path), small_cell_floor=floor)
    document = profile.build_document(table, settings, list(persons), [], [], subjects=list(persons), top_code=top_code, unanswered=list(held) or None)
    return document, chain.describe(table, document, settings, chain.ChainSwitch(name, key, held, rows_per_person=rows_per_person, held_by_person=held_by_person))


def _switched(document: "dict[str, object]", chained: chain.Chained) -> "dict[str, object]":
    """The description a switched run writes: the chain, `grain` and the columns as the layer publishes them."""
    out = json.loads(json.dumps(document))
    out["relationships"]["statistical"] = chained.statistical
    if chained.grain is not None:
        out["relationships"]["grain"] = chained.grain
    if chained.columns is not None:
        out["columns"] = chained.columns
    return out


@pytest.fixture(scope="module")
def visits_layer(tmp_path_factory):
    """One description of 2,000 invented patients with the layer standing (about 9,000 rows)."""
    folder = tmp_path_factory.mktemp("visits")
    header, rows = _visits(2000, 1)
    document, chained = _described(folder, header, rows)
    return folder, document, chained


@pytest.fixture(scope="module")
def trend_layer(tmp_path_factory):
    """One description with change over visits published: no patient-fixed column, so `F_S` is `r`'s own family."""
    folder = tmp_path_factory.mktemp("trend")
    header, rows = _visits(3000, 2)
    kept = [0, 4, 5]
    return _described(folder, [header[at] for at in kept], [[row[at] for at in kept] for row in rows])


# -- THE SWITCH OFF MOVES NO BYTE -----------------------------------------


def test_switch_off_publishes_no_patient_layer(tmp_path, monkeypatch, capsys):
    # Mutant: the layer published without the switch (grain written on an
    # unswitched run, or the person column's census withheld there).
    monkeypatch.chdir(tmp_path)
    header, rows = _visits(1200, 3)
    fixtures.write(tmp_path, "visits.csv", _csv(header, rows))
    code = cli.main(["profile", "visits.csv", "--identifier", "pid"])
    capsys.readouterr()
    assert code == 0
    written = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    for key in written["relationships"]:
        assert written["relationships"][key] is None
    person = [block for block in written["columns"] if block["name"] == "pid"][0]
    assert isinstance(person["n_distinct_by_occurrences"], dict)
    questions = json.loads((tmp_path / "visits-questions.json").read_text(encoding="utf-8"))
    assert asking.BETWEEN_COLUMNS not in questions


def test_the_loader_refuses_grain_without_the_switch(tmp_path, visits_layer):
    # Mutant: `contract._relationships` letting `grain` through with chain=False.
    _folder, document, chained = visits_layer
    path = fixtures.write_profile(tmp_path, "layer.profile.json", _switched(document, chained))
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))
    loaded = contract.load_profile(str(path), chain=True)
    assert len(loaded.columns) == 7
    # `grain` alone, on the description a shipped command writes: S12 names it.
    alone = json.loads(json.dumps(document))
    alone["relationships"]["grain"] = chained.grain
    path = fixtures.write_profile(tmp_path, "grain-alone.profile.json", alone)
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(str(path))
    assert "grain" in str(caught.value)


# -- THE GATE (4.6c.3) ----------------------------------------------------


def test_two_person_columns_turn_the_layer_off(tmp_path):
    # Mutant: the gate's item 1 dropped (the layer read beside the first person column).
    header, rows = _visits(600, 5)
    rows = [row + [row[0] + "x"] for row in rows]
    document, chained = _described(tmp_path, header + ["pid2"], rows, persons=("pid", "pid2"))
    assert chained.statistical is None and chained.grain is None
    assert any(patient_layer.OFF_PERSONS in note for note in chained.notes)


def test_a_blank_person_cell_turns_the_layer_off(tmp_path):
    # Mutant: the gate's item 2 dropped (a row without its person counted as a patient).
    header, rows = _visits(600, 6)
    rows[7][0] = ""
    document, chained = _described(tmp_path, header, rows)
    assert chained.statistical is None and chained.grain is None
    assert any(patient_layer.OFF_BLANK in note for note in chained.notes)


def test_one_to_f_minus_one_extra_rows_turn_the_layer_off(tmp_path):
    header, rows = _visits(300, 7, dropout=False)
    one_each = [row for at, row in enumerate(rows) if at % 8 == 0]
    one_each += [rows[1], rows[9], rows[17]]
    document, chained = _described(tmp_path, header, one_each)
    assert chained.grain is None
    assert any(patient_layer.OFF_EXTRA in note or patient_layer.OFF_CENSUS in note for note in chained.notes)


# -- THE CENSUS OF r (4.6c.4) ---------------------------------------------


def _three_value_split(patients: int, excess: int, floor: int) -> bool:
    """The complete search over every set of at most three values of `0 .. t` (the page's first build)."""
    top = patient_rules.ceil_div(excess, patients)
    for size in (1, 2, 3):
        for chosen in itertools.combinations(range(top + 1), size):
            def fits(at: int, left: int, total: int) -> bool:
                if at == len(chosen) - 1:
                    return left >= floor and chosen[at] * left == total
                for count in range(floor, left - floor * (len(chosen) - 1 - at) + 1):
                    if fits(at + 1, left - count, total - chosen[at] * count):
                        return True
                return False
            if fits(0, patients, excess):
                return True
    return False


def test_the_deficit_search_decides_as_the_complete_search():
    # Mutant: any of the search's four steps dropped.
    for patients in range(3, 26):
        for excess in range(0, 3 * patients + 1):
            split, _steps = patient_rules.deficit_split(patients, excess, 3)
            assert (split is not None) == _three_value_split(patients, excess, 3), (patients, excess)
            if split is not None:
                assert patient_rules.split_checked(split, patients, excess, 3)


def test_the_page_census_cases():
    # Codex's census: c_1 = 1, c_2 = 87, c_3 = 12; only lo = 1 is eligible.
    found, _steps = patient_layer.census_candidates([1] + [2] * 87 + [3] * 12, FLOOR)
    assert [census.lo for census, _steps in found] == [1]
    # 99 patients of 10,000 rows and one of 9,999: refused at the deficit search's first step.
    found, _steps = patient_layer.census_candidates([10000] * 99 + [9999], FLOOR)
    assert found == []
    # 20 patients with 30 extra rows, each at most 2: the values 0, 1 and 2 would need 5, 0 and 15.
    assert patient_rules.deficit_split(20, 30, 10)[0] is not None
    eligible, _steps, _split = patient_rules.census_eligible(patient_rules.census_at(1, {1: 5, 2: 0, 3: 15}), 10)
    assert eligible is False or patient_rules.census_at(1, {1: 5, 3: 15}).excess == 30


def test_no_census_of_eleven_to_twenty_patients_with_one_to_ten_extra_rows_is_eligible():
    # The design's scan (`patient_layer.py`): at extra rows 1 to 10 no candidate is eligible.
    for counts in itertools.product(range(0, 21), repeat=5):
        patients = sum(counts)
        if not 11 <= patients <= 20:
            continue
        values: "list[int]" = []
        for rho in range(5):
            values += [rho + 1] * counts[rho]
        extra = sum(values) - patients
        if not 1 <= extra <= 10:
            continue
        found, _steps = patient_layer.census_candidates(values, FLOOR)
        assert found == [], counts


def test_no_census_band_holds_one_to_f_minus_one_patients(visits_layer):
    # Mutant: a census band of 1 to f - 1 patients published (item 1 of 4.6c.4 (b) dropped).
    _folder, _document, chained = visits_layer
    census = chained.grain["census"]
    for band in census["bands"]:
        assert band["patients"] == 0 or band["patients"] >= FLOOR
    assert census["top"]["patients"] == 0 or census["top"]["patients"] >= FLOOR


# -- NO PATIENT-LEVEL CELL OF 1 TO f - 1 ----------------------------------


def test_every_published_count_of_the_layer_is_floored(visits_layer):
    # Mutant: a patient-level cell of 1 to f - 1 published (the floor dropped in the patient chain or a row family).
    _folder, _document, chained = visits_layer
    for family in chained.statistical["chain"]:
        for row in family["table"]:
            for cell in row:
                assert cell == 0 or cell >= FLOOR
    for entry in chained.statistical["ladder"]:
        least = patient_rules.own_mean_floor(FLOOR) if entry["column"].startswith("(own mean") else FLOOR
        for total in entry["totals"]:
            assert total == 0 or total >= least
    for family in chained.grain["rows"]:
        for row in family["table"]:
            for cell in row:
                assert cell == 0 or cell >= FLOOR
    assert TEST_KEY.hex() not in json.dumps(chained.grain) + json.dumps(chained.statistical)


def _sparse_crossings(tmp_path: pathlib.Path) -> chain.Chained:
    """Columns nearly equal: `b` equals the patient-fixed `a` on all but five patients, a repeated label stands on its own levels by `r` on all but five rows; a family of two is the draw's strongest, and holds a cell of 1 to `f - 1`."""
    draw = random.Random(31)
    header = ["pid", "a", "b", "c", "unit", "visit_date"]
    rows: "list[list[str]]" = []
    for patient in range(1000):
        one = "p" if patient % 2 else "q"
        other = one if patient >= 5 else ("q" if one == "p" else "p")
        third = draw.choice(["u", "v"])
        for visit in range(3 + (patient // 2) % 2):
            short = (patient // 2) % 2 == 0
            levels = ["x", "w"] if short else ["y", "z"]
            unit = draw.choice(levels) if patient >= 5 or visit else "y" if short else "x"
            rows += [[f"S{patient:05d}", one, other, third, unit, f"2024-{1 + visit:02d}-{1 + patient % 28:02d}"]]
    _document, chained = _described(tmp_path, header, rows, name="sparse")
    return chained


def test_a_sparse_crossing_publishes_no_cell_of_one_to_f_minus_one(tmp_path):
    # Mutants: the patient chain's floor set to 1; a row family's floor and certificate dropped together.
    chained = _sparse_crossings(tmp_path)
    assert chained.grain is not None
    cells = [cell for family in chained.statistical["chain"] for row in family["table"] for cell in row]
    cells += [cell for family in chained.grain["rows"] for row in family["table"] for cell in row]
    assert cells and all(cell == 0 or cell >= FLOOR for cell in cells)
    assert chained.counts["floor_refusals"] > 0


def test_the_person_column_publishes_no_census_of_rows_per_patient(visits_layer):
    # Mutant: the person column's multiplicity map, or a key counting rows, published while the layer stands.
    _folder, document, chained = visits_layer
    patients = sum(band["patients"] for band in chained.grain["census"]["bands"]) + chained.grain["census"]["top"]["patients"]
    by_name = {block["name"]: block for block in chained.columns}
    person = by_name["pid"]
    assert person["n_distinct_by_occurrences"] is None
    assert sum(person["layout_forms"].values()) == patients
    assert person["n_present"] == chained.grain["census"]["top"]["rows"] + sum((at + 1) * band["patients"] for at, band in enumerate(chained.grain["census"]["bands"]))
    for block in chained.columns:
        found = block.get("n_distinct_by_occurrences")
        assert found is None or (len(found) == 1 and list(found.values()) == [block["n_present"]])
    for entry in chained.grain["classes"]:
        if entry["class"] == patient_rules.CLASS_FIXED:
            block = by_name[entry["column"]]
            assert block["n_present"] + block["n_missing"] == patients
    original = {block["name"]: block for block in document["columns"]}
    assert isinstance(original["pid"]["n_distinct_by_occurrences"], dict)


def test_the_switched_description_loads_and_each_invariant_refuses_its_mutation(tmp_path, visits_layer):
    # Mutants, one an invariant: S29 (the person's map back, a census band of
    # 1 to f - 1), S30 (a class changed), S31 (a row family's cell of 1 to
    # f - 1), S25 in patients (a patient chain's cell of 1 to f - 1).
    _folder, document, chained = visits_layer
    switched = _switched(document, chained)
    path = fixtures.write_profile(tmp_path, "ok.profile.json", switched)
    contract.load_profile(str(path), chain=True)

    def refused(mutate, invariant: str, name: str) -> None:
        mutated = json.loads(json.dumps(switched))
        mutate(mutated)
        target = fixtures.write_profile(tmp_path, f"{name}.profile.json", mutated)
        with pytest.raises(errors.ProfileError) as caught:
            contract.load_profile(str(target), chain=True)
        assert invariant in str(caught.value)

    def person_map(one):
        for block in one["columns"]:
            if block["name"] == "pid":
                block["n_distinct_by_occurrences"] = {"1": 5}
    refused(person_map, "S29", "map")

    def small_band(one):
        census = one["relationships"]["grain"]["census"]
        census["bands"][0]["patients"] -= census["bands"][0]["patients"] - 5
    refused(small_band, "S29", "band")

    def class_changed(one):
        for entry in one["relationships"]["grain"]["classes"]:
            if entry["class"] == patient_rules.CLASS_FIXED:
                entry["class"] = patient_rules.CLASS_REPEATED
                break
    refused(class_changed, "S3", "class")

    def small_row_cell(one):
        rows = one["relationships"]["grain"]["rows"]
        table = rows[0]["table"]
        table[0][0] -= table[0][0] - 3 if table[0][0] else -3
    if switched["relationships"]["grain"]["rows"]:
        refused(small_row_cell, "S31", "row")

    def small_patient_cell(one):
        families = [family for family in one["relationships"]["statistical"]["chain"] if family["parents"]]
        table = families[0]["table"]
        table[0][0] = 3
    refused(small_patient_cell, "S25", "patient")


# -- COMPLETE FOLLOW-UP AND THE TREND (4.6c.1 (b) 6) ----------------------


def test_complete_follow_up_publishes_no_trend(tmp_path):
    # Mutant: Q_P offered where the column's exact mean and tails fix its cells' code total (the guard dropped).
    header, rows = _visits(1500, 11, dropout=False)
    _document, chained = _described(tmp_path, header, rows)
    assert chained.grain is not None
    assert chained.grain["trend"] == []
    assert chained.counts["trend_published"] == 0
    # Every patient eight rows: no row stands outside `F_S`'s one cell, so `O_free` is 0 < f.
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (1500,), (0,))
    assert patient_rules.free_rows(cells, [(8, 8)], [0], 1, [6000, 6000], 2, [0, 0]) == 0


def test_two_complete_schedules_keep_the_code_total_free_of_no_trend(tmp_path):
    # Every row stands in a cell of one r: the guard of 4.6c.1 (b) 6 refuses every Q_P.
    # Mutant: the guard dropped; SWING then passes on these cells and a trend is published.
    draw = random.Random(41)
    rows: "list[list[str]]" = []
    for patient in range(3000):
        base = draw.gauss(100, 12)
        visits = 4 if patient % 2 else 6
        for j in range(visits):
            rows += [[f"S{patient:05d}", f"2024-{1 + j:02d}-{1 + patient % 28:02d}", f"{base + 0.8 * j + draw.gauss(0, 6):.1f}"]]
    _document, chained = _described(tmp_path, ["pid", "visit_date", "value"], rows, name="schedules")
    assert chained.grain is not None
    assert chained.counts["trend_refused_total"] > 0
    assert chained.grain["trend"] == []


def test_the_class_witness_refuses_where_the_swing_leaves_no_patient_with_two_levels():
    # Item 5 (4.6c.5 (e)): 22 patients of two rows, a two-band label, 22 rows in each band: the only
    # floored world holding V = 11 repeats holds no patient with two levels. Mutant: the witness dropped.
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (22,), (0,))
    stars = [((2, 22),)]

    def holds(witness: "int | None") -> "tuple[bool, dict[str, int]]":
        counts: "dict[str, int]" = {}
        found = patient_rules.certificate(cells, [(2, 2)], [[0]], [22, 22], 2, stars, False, None, witness, FLOOR, counts)
        return found, counts

    assert holds(None)[0] is True
    refused, counts = holds(FLOOR)
    assert refused is False and counts["witness_refusals"] == 1


def test_with_dropout_the_trend_stands_behind_swing(trend_layer):
    # The same visits with no patient-fixed column: F_S is r's own family, its
    # cells hundreds of patients of one r, and SWING passes on some of them.
    _document, chained = trend_layer
    assert chained.grain["trend"], chained.notes
    for entry in chained.grain["trend"]:
        assert isinstance(entry["q"], int)
        assert entry["cell"][0].startswith(patient_rules.R_NAME + "=")
    assert [entry["column"] for entry in chained.grain["grid"]] == ["value"]
    assert chained.counts["trend_published"] + chained.counts["trend_refused_swing"] == chained.counts["trend_cells"]


def test_the_loader_refuses_a_broken_derived_column_or_trend(tmp_path, trend_layer):
    # Mutants: S32 (a derived column's band under its floor) and S33 (a trend SWING
    # refuses, a grid its column's block does not give, a cell of no family).
    document, chained = trend_layer
    switched = _switched(document, chained)
    assert switched["relationships"]["grain"]["derived"] and switched["relationships"]["grain"]["trend"]
    path = fixtures.write_profile(tmp_path, "trend.profile.json", switched)
    contract.load_profile(str(path), chain=True)

    def refused(mutate, invariant: str, name: str) -> None:
        mutated = json.loads(json.dumps(switched))
        mutate(mutated)
        target = fixtures.write_profile(tmp_path, f"{name}.profile.json", mutated)
        with pytest.raises(errors.ProfileError) as caught:
            contract.load_profile(str(target), chain=True)
        assert invariant in str(caught.value), caught.value

    def small_own_mean_band(one):
        for entry in one["relationships"]["statistical"]["ladder"]:
            if entry["column"].startswith("(own mean"):
                entry["totals"][0] += entry["totals"][1] - 15
                entry["totals"][1] = 15
    refused(small_own_mean_band, "S32", "own")

    def trend_out_of_reach(one):
        one["relationships"]["grain"]["trend"][0]["q"] = 10 ** 12
    refused(trend_out_of_reach, "S33", "q")

    def grid_moved(one):
        one["relationships"]["grain"]["grid"][0]["K"] = "7"
    refused(grid_moved, "S33", "grid")

    def cell_of_no_family(one):
        one["relationships"]["grain"]["trend"][0]["cell"] = ["(rows per patient)=9999"]
    refused(cell_of_no_family, "S33", "cell")


def _refused_as(tmp_path: pathlib.Path, switched: "dict[str, object]", mutate: "typing.Callable[[dict[str, typing.Any]], None]", name: str, words: str) -> None:
    mutated = json.loads(json.dumps(switched))
    mutate(mutated)
    target = fixtures.write_profile(tmp_path, f"{name}.profile.json", mutated)
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(str(target), chain=True)
    assert words in str(caught.value), caught.value


def _staggered(patients: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Invented visits whose patients start on days spread over two years: an arm, a visit date, a reading."""
    import datetime

    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    start = datetime.date(2022, 1, 1)
    for patient in range(patients):
        first = start + datetime.timedelta(days=draw.randint(0, 700))
        for j in range(draw.randint(1, 8)):
            day = first + datetime.timedelta(days=30 * j + draw.randint(0, 5))
            rows += [[f"S{patient:05d}", draw.choice(["a", "b"]), day.isoformat(), f"{draw.gauss(100, 12) + j:.1f}"]]
    return ["pid", "arm", "visit_date", "value"], rows


def test_the_loader_reads_the_grain_family_and_the_derived_columns_off_the_chain(tmp_path):
    # Codex's items 2 and 9 at the floor size. MUTANTS: `grain_family` trusted as written (null, or an
    # earlier family, beside the latest keyed one: departure 13's check skipped); a derived column's
    # level, rise and count of edges unread (Codex's `level` "garbage" and three "2099-12-31" edges).
    header, rows = _staggered(4600, 3)
    assert len(rows) >= 20000
    document, chained = _described(tmp_path, header, rows, key=bytes(32))
    switched = _switched(document, chained)
    grain = switched["relationships"]["grain"]
    kinds = {entry["kind"]: entry for entry in grain["derived"]}
    assert grain["grain_family"] is not None and patient_rules.FIRST_DATE in kinds and patient_rules.OWN_MEAN in kinds
    path = fixtures.write_profile(tmp_path, "staggered.profile.json", switched)
    contract.load_profile(str(path), chain=True)
    latest = grain["grain_family"]

    def family_null(one):
        one["relationships"]["grain"]["grain_family"] = None
    _refused_as(tmp_path, switched, family_null, "null", "latest keyed family")

    def family_earlier(one):
        one["relationships"]["grain"]["grain_family"] = latest - 1
    _refused_as(tmp_path, switched, family_earlier, "earlier", "latest keyed family")

    def first_of(one: "dict[str, typing.Any]") -> "dict[str, typing.Any]":
        return [entry for entry in one["relationships"]["grain"]["derived"] if entry["kind"] == patient_rules.FIRST_DATE][0]

    def level_garbage(one):
        first_of(one)["level"] = "garbage"
    _refused_as(tmp_path, switched, level_garbage, "level", "level is L0, L1 or L2")

    def edges_far(one):
        first_of(one)["edges"] = ["2099-12-31"] * 3
    _refused_as(tmp_path, switched, edges_far, "far", "edges rise strictly")

    def edges_one_short(one):
        first_of(one)["edges"] = first_of(one)["edges"][1:]
    _refused_as(tmp_path, switched, edges_one_short, "short", "number one for each band")

    def mean_edges_falling(one):
        entry = [entry for entry in one["relationships"]["grain"]["derived"] if entry["kind"] == patient_rules.OWN_MEAN][0]
        entry["edges"] = list(reversed(entry["edges"]))
    _refused_as(tmp_path, switched, mean_edges_falling, "falling", "edges rise strictly")


def _two_cohorts_and_a_few_late(seed: int) -> "tuple[list[str], list[list[str]]]":
    """Invented visits, each on the first of a month: two cohorts of 2,300 patients starting a year apart with one to eight visits, and five patients starting in the first cohort's sixth month with one or two.

    The five leave every finer level of the first date a band of 1 to 10
    patients, so the first date stands at its source's `L2`, two bands,
    and the visit date keeps its row family and its block (the verify 2
    of lane GRa, item 1).
    """
    import datetime

    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    for year, month, patients, most in ((2022, 0, 2300, 8), (2023, 0, 2300, 8), (2022, 5, 5, 2)):
        for _one in range(patients):
            for visit in range(draw.randint(1, most)):
                at = month + visit
                day = datetime.date(year + at // 12, 1 + at % 12, 1)
                rows += [[f"S{patient:05d}", day.isoformat(), f"{draw.gauss(100, 12) + visit:.1f}"]]
            patient += 1
    order = list(range(len(rows)))
    draw.shuffle(order)
    return ["pid", "visit_date", "value"], [rows[at] for at in order]


def test_a_first_date_s_edges_off_its_standing_source_s_rungs_are_refused(tmp_path):
    # The verify 2 of lane GRa, item 1: S32's last clause (contract 4.6c.12 item 29) at the floor size, on
    # a table whose first date's source keeps its block and so its rungs (on the staggered table above the
    # source is held, departure 6, and the clause is never reached). Each edge moved a day off its rung
    # still rises and keeps its count. MUTANT own_item9_rungs: the edges never compared with the source's
    # rungs (`if edges != expected` read as `if False`), so both moved descriptions load.
    import datetime

    header, rows = _two_cohorts_and_a_few_late(41)
    assert len(rows) >= 20000
    document, chained = _described(tmp_path, header, rows, key=bytes(32))
    switched = _switched(document, chained)
    source = [one for one in switched["columns"] if one["name"] == "visit_date"][0]
    rungs = source["date_percentiles"]
    assert isinstance(rungs, dict) and [one for one in rungs.values() if one is not None]
    first = [entry for entry in switched["relationships"]["grain"]["derived"] if entry["kind"] == patient_rules.FIRST_DATE][0]
    assert first["source"] == "visit_date" and first["edges"] and all(edge in rungs.values() for edge in first["edges"])
    path = fixtures.write_profile(tmp_path, "cohorts.profile.json", switched)
    contract.load_profile(str(path), chain=True)

    def moved(days: int) -> "typing.Callable[[dict[str, typing.Any]], None]":
        def mutate(one: "dict[str, typing.Any]") -> None:
            for entry in one["relationships"]["grain"]["derived"]:
                if entry["kind"] == patient_rules.FIRST_DATE:
                    entry["edges"] = [(datetime.date.fromisoformat(edge) + datetime.timedelta(days=days)).isoformat() for edge in entry["edges"]]
        return mutate

    _refused_as(tmp_path, switched, moved(1), "later", "its source's rungs")
    _refused_as(tmp_path, switched, moved(-1), "earlier", "its source's rungs")


def _fixed_x_and_arm(patients: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's item 6 shape: eight rows a patient, a patient-fixed measurement of four readings, an arm, and a site on every row."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        x = ["1.5", "2.5", "3.5", "4.5"][patient % 4]
        arm = "a" if (patient // 4) % 2 == 0 else "b"
        for _row in range(8):
            rows += [[f"S{patient:05d}", x, arm, draw.choice(["p", "q", "r"])]]
    return ["pid", "x", "arm", "site"], rows


def _separated(table: "list[list[int]]") -> "list[list[int]]":
    """A family's table with its child's totals kept and each child band in one parent cell: no band of the child reaches two parent cells."""
    cells = len(table)
    bands = len(table[0])
    out = [[0] * bands for _cell in range(cells)]
    for band in range(bands):
        out[band * cells // bands if bands >= cells else band][band] = sum(row[band] for row in table)
    return out


def _northwest(table: "list[list[int]]") -> "list[list[int]]":
    """A family's table with both margins kept and its cells poured in order (the north-west corner rule): each child band in as few parent cells as the margins allow."""
    cells = len(table)
    bands = len(table[0])
    by_cell = [sum(row) for row in table]
    by_band = [sum(row[band] for row in table) for band in range(bands)]
    out = [[0] * bands for _cell in range(cells)]
    cell = band = 0
    while cell < cells and band < bands:
        poured = min(by_cell[cell], by_band[band])
        out[cell][band] += poured
        by_cell[cell] -= poured
        by_band[band] -= poured
        if by_cell[cell] == 0:
            cell += 1
        if band < bands and by_band[band] == 0:
            band += 1
    return out


def test_rule_w1_is_read_by_the_loader_in_patients_and_in_rows(tmp_path):
    # Codex's item 6 at its size (24,000 rows, 3,000 patients): a patient-fixed measurement of four
    # readings beside an arm, their family's table separated with its margins kept; and a row family of
    # a count of five readings on every row, separated with its child's totals kept. MUTANTS: the
    # patient chain's W1 read with empty groups; the row families' W1 unread by the loader.
    header, rows = _fixed_x_and_arm(3000, 5)
    assert len(rows) == 24000
    joined: "list[int]" = []
    for key in (bytes([k]) * 32 for k in range(6)):
        document, chained = _described(tmp_path, header, rows, key=key)
        switched = _switched(document, chained)
        joined = [
            at for at, family in enumerate(switched["relationships"]["statistical"]["chain"])
            if {family["child"], *[parent["column"] for parent in family["parents"]]} >= {"x", "arm"} and family["child"] in ("x", "arm")
        ]
        if joined:
            break
    assert joined
    path = fixtures.write_profile(tmp_path, "fixed.profile.json", switched)
    contract.load_profile(str(path), chain=True)

    def patients_separated(one):
        family = one["relationships"]["statistical"]["chain"][joined[0]]
        family["table"] = _northwest(family["table"])
    _refused_as(tmp_path, switched, patients_separated, "w1p", "RULE W1 in patients")
    header, rows = _visits(2000, 1)
    draw = random.Random(8)
    counted_rows = [row + [f"{draw.randint(0, 4)}"] for row in rows]
    tallied: "list[int]" = []
    for key in (bytes([k]) * 32 for k in range(6)):
        counted_document, counted = _described(tmp_path / "tally", header + ["tally"], counted_rows, key=key)
        visits = _switched(counted_document, counted)
        tallied = [at for at, family in enumerate(visits["relationships"]["grain"]["rows"]) if family["child"] == "tally"]
        if tallied:
            break
    assert tallied

    def rows_separated(one):
        family = one["relationships"]["grain"]["rows"][tallied[0]]
        family["table"] = _separated(family["table"])
    _refused_as(tmp_path, visits, rows_separated, "w1r", "RULE W1 in rows")


# -- THE SUBJECT QUESTION'S HOLD (P4-D418 limit (3)) ----------------------


def test_the_subject_question_holds_the_chain_in_the_library(tmp_path):
    # Mutant: the hold dropped (a chain drawn while the question is open).
    header, rows = _visits(600, 9, keys="number")
    for state, drawn in ((chain.ROWS_OPEN, False), (chain.ROWS_UNNAMED, False), (chain.ROWS_ONE, True)):
        document, chained = _described(tmp_path / state.replace(" ", "_"), header, rows, persons=(), rows_per_person=state)
        assert (chained.statistical is not None) == drawn, state
        if not drawn:
            assert chained.notes[-1].startswith("no chain is published")


def test_a_table_of_too_few_columns_for_a_chain_is_not_asked(tmp_path, monkeypatch, capsys):
    # 716 of the 880-description battery's: no answer could draw a chain, so the question decides
    # nothing. Mutant: the question put whatever the columns (false alarms); no chain either way.
    monkeypatch.chdir(tmp_path)
    draw = random.Random(61)
    fixtures.write(tmp_path, "one.csv", _csv(["value"], [[f"{draw.gauss(100, 12):.1f}"] for _row in range(2000)]))
    assert cli.main(["profile", "one.csv"], chain=cli.ChainRun(folder=str(tmp_path / "data"))) == 0
    capsys.readouterr()
    questions = json.loads((tmp_path / "one-questions.json").read_text(encoding="utf-8"))
    assert asking.ROWS_PER_PERSON not in questions[asking.BETWEEN_COLUMNS]
    written = json.loads((tmp_path / "one-profile.json").read_text(encoding="utf-8"))
    assert written["relationships"]["statistical"] is None


def test_the_subject_question_through_the_command(tmp_path, monkeypatch, capsys):
    # Mutant: the hold dropped in the command, or an answer not read back.
    monkeypatch.chdir(tmp_path)
    header, rows = _visits(1200, 12, keys="number")
    fixtures.write(tmp_path, "visits.csv", _csv(header, rows))
    run = cli.ChainRun(folder=str(tmp_path / "data"))
    assert cli.main(["profile", "visits.csv"], chain=run) == 0
    capsys.readouterr()
    written = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
    assert written["relationships"]["statistical"] is None
    questions = json.loads((tmp_path / "visits-questions.json").read_text(encoding="utf-8"))
    entry = questions[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]
    assert entry["question"] == asking.ROWS_PER_PERSON_QUESTION and entry["your_answer"] == ""
    # Each answer describes the table again under its name: the ledger is
    # told the description is replaced (4.6b.4's `--replace-description`).
    again = cli.ChainRun(folder=str(tmp_path / "data"), replace_description=True)
    # An answer naming no column of the table is refused, as a mistyped declared identifier is.
    entry["your_answer"] = "no such column"
    (tmp_path / "answers.json").write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    assert cli.main(["profile", "visits.csv", "--answers", "answers.json"], chain=again) == 2
    capsys.readouterr()
    for answer, stands in ((asking.ANSWER_ONE_ROW_EACH, "statistical"), ("pid", "grain")):
        entry["your_answer"] = answer
        (tmp_path / "answers.json").write_text(json.dumps(questions), encoding="utf-8", newline="\n")
        assert cli.main(["profile", "visits.csv", "--answers", "answers.json"], chain=again) == 0
        capsys.readouterr()
        written = json.loads((tmp_path / "visits-profile.json").read_text(encoding="utf-8"))
        assert written["relationships"][stands] is not None, answer
        kept = json.loads((tmp_path / "visits-questions.json").read_text(encoding="utf-8"))
        if answer == asking.ANSWER_ONE_ROW_EACH:
            assert kept[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] == answer


# -- THE PAGE'S SMALL CASES, COMPUTED -------------------------------------


def test_pwit_reads_the_page_cases():
    # 4.6c.8: 20 patients of two rows with a band of 21 of 40 rows fail; 22 with 23 of 44 pass.
    assert patient_rules.pwit(20, [21, 19], FLOOR) is False
    assert patient_rules.pwit(22, [23, 21], FLOOR) is True


def test_the_keyed_rule_refuses_codex_chain():
    # Codex's chain {r, A}, {B | A, r}, {C | B, r}: the third family leaves out A.
    placed = [
        chain.rules.Family("A", 0, (), None, (20, 20)),
        chain.rules.Family(patient_rules.R_NAME, 0, (("A", 0),), 0, (10, 10, 10, 10)),
        chain.rules.Family("B", 0, (("A", 0), (patient_rules.R_NAME, 0)), 1, (5,) * 8),
    ]
    good = chain.Option("C", ("A", "B", patient_rules.R_NAME), (0, 0, 0, 0), 2, (), chain.fractions.Fraction(0))
    bad = chain.Option("C", ("B", patient_rules.R_NAME), (0, 0, 0), 2, (), chain.fractions.Fraction(0))
    two = chain.rules.Ladder("x", (("a",), ("b",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (20, 20), (True, True))
    scales = {name: two for name in ("A", "B", "C", patient_rules.R_NAME)}
    assert patient_layer._keeps_keyed_rule(placed, good, set(), True, scales)
    assert not patient_layer._keeps_keyed_rule(placed, bad, set(), True, scales)


def test_a_keyed_family_leaving_r_star_no_world_is_not_offered():
    # 34 patients in the top band, 18 extra rows: cut 17 and 17 by a label there is no floored split
    # of each cell's share, so every column under it would be held; 34 together take it (a block of
    # 18 at one more row and 16 at none). Mutant: the rule dropped (the zoo's `claims`, every column held).
    census = patient_rules.census_at(3, {1: 20, 2: 20, 3: 16, 4: 18})
    assert census.top_patients == 34 and census.excess == 18
    scales = {
        patient_rules.R_NAME: patient_rules.r_ladder(census),
        "A": chain.rules.Ladder("A", (("x",), ("y",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (54, 40), (True, True)),
    }
    split = chain.Option(patient_rules.R_NAME, ("A",), (0, 0), None, (10, 10, 17, 10, 10, 17), chain.fractions.Fraction(0))
    whole = chain.Option(patient_rules.R_NAME, ("A",), (0, 0), None, (20, 20, 34, 0, 0, 0), chain.fractions.Fraction(0))
    assert patient_layer._keeps_r_star(split, scales, census, FLOOR, set()) is False
    assert patient_layer._keeps_r_star(whole, scales, census, FLOOR, set()) is True
    # The rule reads keyed families alone.
    free = chain.Option("A", (), (0,), None, (54, 40), chain.fractions.Fraction(0))
    assert patient_layer._keeps_r_star(free, scales, census, FLOOR, set()) is True


def test_the_class_witness_reads_v_and_v_k_from_the_patterns():
    blocks = (
        patient_rules.Block(0, 11, (2, 0)),
        patient_rules.Block(0, 11, (1, 1)),
    )
    assert patient_rules.witness_counts(blocks) == (11, 11)
    classes = [patient_rules.Klass(44, 2, (0, 0), (2, 2))]
    swung = patient_rules.swung((patient_rules.Block(0, 44, (1, 1)),), classes, FLOOR, 22)
    assert patient_rules.witness_counts(swung)[0] >= 22
    assert sum(block.count * block.pattern[0] for block in swung) == 44


def test_the_patient_cases_leak_nothing_by_exact_enumeration():
    # Mutants: PWIT, the floored split or the class witness weakened (a
    # certified cell leaking a union of types); the census's small-extra rule.
    import patient_enumeration

    found = patient_enumeration.patient_cases()
    assert found["census_small_extra_eligible"] == 0 and found["census_small_extra"] == 930
    assert found["pwit_passing_leaking"] == 0 and found["pwit_cells"] == 98
    assert found["split_passing_leaking"] == 0 and found["split_passing"] > 0
    assert found["witness_passing_leaking"] == 0
    assert found["witness_mutant_leaking"] == found["witness_leaking_with_class"] == 330


# -- THE PAGE'S FIXTURES (4.6c.10 items 1, 4, 5 and 6), EACH WITH ITS READING --


def test_the_design_attacks_read_refused():
    # Item 1: the 12-patient cell of 21 rows and the second attack's 16-patient,
    # 21-row cell; item 5: 22 patients of two rows with 13 and 31 rows.
    # Mutant: PWIT weakened (a band holding fewer rows a patient than the floor asks).
    assert patient_rules.pwit(12, [21, 3], FLOOR) is False
    assert patient_rules.pwit(16, [21, 11], FLOOR) is False
    classes = [patient_rules.Klass(22, 2, (0, 0), (2, 2))]
    assert patient_rules.floored_split(classes, [13, 31], FLOOR).blocks == ()


def test_a_top_band_with_no_floored_split_is_refused():
    # Item 4: 22 patients at the top edge with one extra row: no value but 0 and 1 reaches it on 11 patients each.
    # Mutant: the deficit search's re-check dropped (a split of a block under the floor taken).
    assert patient_rules.deficit_split(22, 1, FLOOR)[0] is None
    eligible, _steps, split = patient_rules.census_eligible(patient_rules.census_at(2, {1: 11, 2: 21, 3: 1}), FLOOR)
    assert eligible is False and split is None


def test_an_r_star_whose_tie_fails_is_refused():
    # Item 4: two cells of the top band sharing one extra row; neither can take it on a floored block.
    assert patient_rules.top_rows_shared([11, 11], 2, 1, FLOOR) is None
    assert patient_rules.r_star(22, 2 * 22 + 1, (2, None), FLOOR) is None
    # A band of one value gives every patient that value, and its rows must say so.
    assert patient_rules.r_star(22, 44, (2, 2), FLOOR) == ((2, 22),)
    assert patient_rules.r_star(22, 45, (2, 2), FLOOR) is None


def test_the_shared_top_rows_keep_the_block_s_tight_cap():
    # Codex's item 1, its own numbers (20,903 rows, 1,737 patients: 37 top-band patients of 503 rows at
    # `lo` 13, tight cap 14 rows): grain cells of 11, 13 and 13 patients share 22 extra rows only by
    # giving 11 patients 15 rows, a world no table of the description holds, so no `R*` is certified.
    # MUTANT: the cap unread (the shares `[165, 169, 169]`).
    census = patient_rules.census_at(13, {12: 1700, 13: 15, 14: 22})
    assert census.top_patients == 37 and census.top_rows == 503 and patient_rules.tight_cap(census) == 1
    assert patient_rules.top_rows_shared([11, 13, 13], 13, 22, FLOOR) is None
    # The same excess on cells of 11 and 13: the 11 take one row each, under the cap.
    assert patient_rules.top_rows_shared([11, 13], 13, 11, FLOOR) == [154, 169]
    # A block whose own rows hold more a patient keeps its own, higher cap: 22 patients, 66 extra rows.
    assert patient_rules.top_rows_shared([11, 11], 13, 66, FLOOR) == [176, 176]


def test_the_shared_top_rows_search_each_cell_a_bounded_number_of_times(monkeypatch):
    # Codex's item 5, the allocation trial: `[12] * k` cells sharing 11 extra rows rechecked every earlier
    # cell for each trial, a search count growing with the square of the cells. MUTANT: the recheck of
    # every cell for each trial (the searches at 400 cells four times those at 200).
    searched = {"count": 0}
    search = patient_rules.deficit_split

    def counted(patients: int, excess: int, floor: int) -> "tuple[patient_rules.Split | None, int]":
        searched["count"] += 1
        return search(patients, excess, floor)

    monkeypatch.setattr(patient_rules, "deficit_split", counted)
    found = {}
    for cells in (200, 400):
        searched["count"] = 0
        assert patient_rules.top_rows_shared([12] * cells, 13, 11, FLOOR) is None
        found[cells] = searched["count"]
    assert found[400] <= 4 and found[200] <= 4


def test_the_patients_of_each_cell_are_grouped_in_linear_time():
    # Codex's item 5, the trend's preparation: a cell's list copied on every patient added (about 40
    # billion copies a column at 400,000 patients of one cell). MUTANT: the copy restored (this case
    # then runs for hours, a timeout where the mutants run).
    import time

    for patients in (200000, 400000):
        started = time.perf_counter()
        grouped = patient_rules.grouped([0] * (patients - 3) + [1, 0, 1])
        assert grouped[1] == [patients - 3, patients - 1] and len(grouped[0]) == patients - 2
        assert time.perf_counter() - started < 30


def test_a_band_of_one_reading_asks_the_fallback_witness():
    # Codex's item 7: at a grid step of 1 the band [7, 8) holds 7 alone, so it spans no two readings;
    # a FINE column whose band holds one reading takes the floored split WITH the `V_K` witness of
    # 4.6c.5 (e) item 2. MUTANTS: the half-open edge read as two readings; the fallback asking no witness.
    import fractions

    from synthtwin import chain_rules as rules

    grid = patient_rules.Grid("x", fractions.Fraction(1), fractions.Fraction(0), 40)
    ladder = rules.Ladder("x", ((("p50", "p60"),), (("p60", "p70"),)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (22, 24), (True, True))
    block: "dict[str, object]" = {"percentiles": {"p50": 7, "p60": 8, "p70": 10}, "role": "count", "name": "x"}
    assert patient_rules.spans_two(ladder, block, 0, grid) is False
    block["percentiles"] = {"p50": 7, "p60": 9, "p70": 11}
    assert patient_rules.spans_two(ladder, block, 0, grid) is True
    assert patient_rules.class_witness(False, False, 11) == (11, False)
    assert patient_rules.class_witness(False, True, 11) == (None, False)
    assert patient_rules.class_witness(True, True, 11) == (11, True)
    # 23 patients of two rows, 24 and 22 rows in the bands: the floored split puts every patient's rows
    # in one band (12 and 11 patients), so no patient holds two readings: `V_K` 0. Thirty patients
    # of 30 and 30 rows spread one row a band each: `V_K` 30.
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (23,), (0,))
    stars = [((2, 23),)]
    assert patient_rules.certificate(cells, [(2, 2)], [[0]], [24, 22], 2, stars, False, None, None, FLOOR, {}) is True
    counts: "dict[str, int]" = {}
    assert patient_rules.certificate(cells, [(2, 2)], [[0]], [24, 22], 2, stars, False, None, 11, FLOOR, counts, False) is False
    assert counts["witness_refusals"] == 1
    thirty = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (30,), (0,))
    assert patient_rules.certificate(thirty, [(2, 2)], [[0]], [30, 30], 2, [((2, 30),)], False, None, 11, FLOOR, {}, False) is True


def test_a_first_date_cell_whose_residual_is_one_to_ten_rows_is_refused():
    # Item 4: 20 patients of three rows in each of two first-date bands; each patient's
    # first date stands in its own band, so the band's residual is its rows less 20.
    cells = patient_rules.Cells((("(first date of d)", 0),), (2,), (20, 20), (0, 0))
    restriction = patient_rules.Restriction(patient_rules.FIRST_DATE, 0, (), (), None, (True, True))

    def holds(table: "list[int]") -> bool:
        return patient_rules.certificate(cells, [(3, 3)], [[0], [1]], table, 2, None, True, restriction, None, FLOOR, {})

    assert holds([25, 35, 0, 60]) is False
    assert holds([31, 29, 0, 60]) is True


def test_an_own_mean_cell_takes_the_floored_split_within_its_allowed_patterns():
    # Item 4: codes 0 to 3, a patient of two rows, the own-mean band from 1.5 up: at most one row in the low band.
    grid = patient_rules.Grid("x", patient_rules.fractions.Fraction(1), patient_rules.fractions.Fraction(0), 3)
    restriction = patient_rules.Restriction(
        patient_rules.OWN_MEAN, 0, ((0, 1), (2, 3)), (patient_rules.fractions.Fraction(3, 2),), grid, (True, True)
    )
    cells = patient_rules.Cells((("(own mean of x)", 0),), (2,), (30, 30), (0, 0))
    one = patient_rules.klass(restriction, cells, 1, 2, 30, 2)
    assert one == patient_rules.Klass(30, 2, (0, 1), (1, 2))
    found = patient_rules.floored_split([one], [15, 45], FLOOR)
    assert found.blocks and all(block.pattern[0] <= 1 for block in found.blocks)
    assert patient_rules.floored_split([one], [31, 29], FLOOR).blocks == ()


def test_a_column_of_zero_central_span_has_no_grid():
    # Item 6: no grid, so no trend; the tails withheld read the same. Mutant: `K < 1` let through.
    block = {
        "integer_valued": True,
        "name": "x",
        "percentiles": {"p01": 5, "p50": 7, "p99": 9},
        "role": "count",
        "tails": {"high": {"percent": 99}, "low": {"percent": 1}},
    }
    found = patient_rules.grid_of(block)
    assert found is not None and found.codes == 4
    flat = {**block, "percentiles": {"p01": 5, "p50": 5, "p99": 5}}
    assert patient_rules.grid_of(flat) is None
    assert patient_rules.grid_of({**block, "tails": None}) is None


def _patients_of_two_rows(patients: int, cells: "list[list[str]]") -> "tuple[list[str], list[list[str]]]":
    """`patients` patients of `len(cells)` rows each; each column's cell is `cells[row][patient]`."""
    rows: "list[list[str]]" = []
    for patient in range(patients):
        for row in cells:
            rows += [[f"S{patient:05d}", row[patient]]]
    return ["pid", "x"], rows


def _class_of(chained: chain.Chained, column: str) -> str:
    return [entry["class"] for entry in chained.grain["classes"] if entry["column"] == column][0]


def test_a_label_at_t_and_t_plus_one_keeps_its_class_only_on_the_threshold(tmp_path):
    # Item 4: T is the floor less one here; a column whose values differ inside T patients is
    # patient-fixed; at T + 1 it is not. The same for the KEY test: a level held twice by T patients.
    # Mutant: the threshold read one higher.
    for moved, wanted in ((FLOOR - 1, patient_rules.CLASS_FIXED), (FLOOR, None)):
        first = ["F" if patient % 2 else "M" for patient in range(400)]
        second = list(first)
        for patient in range(moved):
            second[patient] = "M" if first[patient] == "F" else "F"
        header, rows = _patients_of_two_rows(400, [first, second])
        _document, chained = _described(tmp_path / f"fixed{moved}", header, rows)
        if wanted is None:
            assert _class_of(chained, "x") != patient_rules.CLASS_FIXED
        else:
            assert _class_of(chained, "x") == wanted
    for repeated, wanted in ((FLOOR - 1, patient_rules.CLASS_POSITION), (FLOOR, None)):
        second = ["b"] * 400
        for patient in range(repeated):
            second[patient] = "a"
        header, rows = _patients_of_two_rows(400, [["a"] * 400, second])
        _document, chained = _described(tmp_path / f"key{repeated}", header, rows)
        if wanted is None:
            assert _class_of(chained, "x") != patient_rules.CLASS_POSITION
        else:
            assert _class_of(chained, "x") == wanted


def test_a_position_like_column_of_two_schedules_in_equal_halves_lists_nulls(tmp_path):
    # Item 6: a tie at every position: the list is all `null` and the column keeps its class.
    first = ["a" if patient % 2 else "b" for patient in range(400)]
    second = ["b" if patient % 2 else "a" for patient in range(400)]
    header, rows = _patients_of_two_rows(400, [first, second])
    _document, chained = _described(tmp_path, header, rows)
    assert _class_of(chained, "x") == patient_rules.CLASS_POSITION
    listed = [entry["values"] for entry in chained.grain["positions"] if entry["column"] == "x"][0]
    assert listed and all(one is None for one in listed)


def test_a_position_list_writes_null_by_count_by_tie_and_by_a_repeated_level():
    # Item 4; the list is rebuilt by its tie world (4.6c.6 (d)). Mutant: any of the three dropped.
    def listed(cells: "list[list[str]]", length: int) -> "list[object]":
        texts: "list[str]" = []
        rows: "list[list[int]]" = []
        for patient in cells:
            rows += [[len(texts) + at for at in range(len(patient))]]
            texts += patient
        return patient_layer._position_list(texts, types.SimpleNamespace(rows=rows), length, FLOOR)

    # By count: the second position's mode stands on ten patients.
    assert listed([["a", "b"]] * 10 + [["a"]] * 20, 2) == ["a", None]
    assert listed([["a", "b"]] * 11 + [["a"]] * 20, 2) == ["a", "b"]
    # By tie: twenty `a` and twenty `b` at the first position.
    assert listed([["a"]] * 20 + [["b"]] * 20, 1) == [None]
    # By a repeated level: the second position's mode is the level the first already lists.
    assert listed([["a", "a"]] * 30, 2) == ["a", None]
    # A position no patient holds.
    assert listed([["a"]] * 30, 2) == ["a", None]


def test_one_row_count_for_every_patient_has_no_grain_family(tmp_path):
    # Item 6: 100 patients of two rows: `r` constant, no placed family holds it, `G` is the
    # census's one cell, and every row family under it is PWIT's. Mutant: `r` offered at one band.
    draw = random.Random(21)
    header = ["pid", "value"]
    rows: "list[list[str]]" = []
    for patient in range(100):
        for _visit in range(2):
            rows += [[f"S{patient:05d}", f"{draw.gauss(100, 12):.1f}"]]
    _document, chained = _described(tmp_path, header, rows)
    assert chained.grain is not None and chained.grain["grain_family"] is None
    assert patient_rules.R_NAME not in [entry["column"] for entry in chained.statistical["ladder"]]
    assert {"column": patient_rules.R_NAME, "reason": "one_band"} in chained.statistical["ineligible"]
    for family in chained.grain["rows"]:
        assert family["parents"] == []


def test_a_visit_trend_fixture_under_the_product_s_swing():
    # Item 3 on `F13` at eight patients; `kpi_run --slow` runs all fifteen. Mutants: SWING's reserve
    # dropped, or its gap condition (ii) (5 descriptions then pass and leak here).
    import patient_enumeration

    for fixture in [one for one in patient_enumeration.TREND_FIXTURES if one[0] == "F13"]:
        found = patient_enumeration.trend_fixture(*fixture[1:6], (8,), fixture[7])
        assert found["passing"] > 0 and found["leaking"] > 0
        assert found["passing_leaking"] == 0, fixture[0]


def test_a_block_the_layer_empties_reaches_the_disclosure_lines():
    # The zoo's `bedside_results`: a held block holds none of its role's keys, and the summary's
    # disclosure lines read them for a compound column. Mutant: the lines read the emptied block.
    held = {"name": "x", "position": 1, "role": taxonomy.ROLE_COMPOUND, "statistical_type": None, "labels": None, "numbers": None}
    assert summary._emptied_by_the_patient_layer(held)
    assert not summary._emptied_by_the_patient_layer({**held, "statistical_type": "x"})
    assert not summary._emptied_by_the_patient_layer({**held, "n_present": 0})
    written = summary._disclosure_lines({"columns": [held], "settings": {"small_cell_floor": FLOOR}, "publication_notes": [], "relationships": {}})
    assert not any("x" == line.strip() for line in written)


def test_a_date_declared_as_counts_on_a_repeated_column_keeps_the_patient_table_describable(tmp_path):
    # The zoo's `perioperative`: the patient table holds no such column, so its settings must not name it.
    # Mutant: the patient table described under the row table's settings (the publication check refuses).
    draw = random.Random(51)
    rows: "list[list[str]]" = []
    for patient in range(800):
        gender = draw.choice(["F", "M"])
        for _visit in range(1 + patient % 4):
            rows += [[f"S{patient:05d}", gender, f"{43000 + draw.randint(0, 900)}"]]
    path = fixtures.write(tmp_path, "served.csv", _csv(["pid", "gender", "when"], rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",), forced_date_counts=(("when", "excel-1900"),))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("served", TEST_KEY, rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is not None
    assert _class_of(chained, "when") in (patient_rules.CLASS_DEALT, patient_rules.CLASS_HELD)


def test_rows_sorted_by_a_column_the_layer_empties_load_behind_the_switch(tmp_path):
    # The zoo's `wearables` at 20,000 rows: the file sorted by a column the layer held. The sort is the
    # file's own fact; the block is emptied, so it publishes no absent cells for FD7 to read.
    # Mutant: FD7 reading the emptied block's count of absent cells (a refused description).
    draw = random.Random(100)
    ids = [f"S{patient:05d}" for patient in range(100) for _visit in range(2)]
    draw.shuffle(ids)
    rows = [[ids[at], f"{1000 + at * 7 + 0.5}"] for at in range(len(ids))]
    document, chained = _described(tmp_path, ["pid", "value"], rows, name="sorted")
    assert _class_of(chained, "value") in (patient_rules.CLASS_POSITION, patient_rules.CLASS_HELD)
    assert document["source"]["dialect"]["row_order"]["column"] == 2
    path = fixtures.write_profile(tmp_path, "sorted.profile.json", _switched(document, chained))
    contract.load_profile(str(path), chain=True)


# -- THE PATIENT TABLE TAKES EVERY RULE OF THE ROW DESCRIPTION (repair 1, HIPAA) --


def _fixed_facts_table() -> "tuple[list[str], list[list[str]], dict[str, dict[str, int]]]":
    """About 20,000 rows of about 3,100 patients: a fixed age from 18 to 104 and three fixed dates, and how many patients hold each date."""
    draw = random.Random(12)
    rows: "list[list[str]]" = []
    held: "dict[str, dict[str, int]]" = {"birth_date": {}, "death_date": {}, "enroll_date": {}}
    patient = 0
    while len(rows) < 20000:
        count = max(2, min(1 + int(draw.expovariate(1 / 5)), 60))
        one = {
            "birth_date": f"{draw.randint(1940, 2005)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}",
            "death_date": f"{draw.randint(2015, 2024)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}",
            "enroll_date": f"{draw.randint(2010, 2014)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}",
        }
        for name in one:
            held[name][one[name]] = held[name].get(one[name], 0) + 1
        age = draw.randint(18, 104)
        base = draw.gauss(100, 15)
        for _visit in range(count):
            rows += [[f"P{patient:07d}", f"{age}", one["birth_date"], one["death_date"], one["enroll_date"], f"{base + draw.gauss(0, 7):.1f}", draw.choice(["a", "b", "c"])]]
        patient += 1
    return ["pid", "age", "birth_date", "death_date", "enroll_date", "value", "site"], rows, held


def test_a_patient_fixed_column_keeps_every_rule_at_the_floor_size(tmp_path):
    # One 20,000-row case for the patient table's writer. Mutants: the top-code off in the
    # patient table's description; its dates read as a small table's (`long_table_dates` off).
    header, rows, held = _fixed_facts_table()
    document, chained = _described(tmp_path, header, rows, top_code=True)
    assert chained.grain is not None
    by_name = {block["name"]: block for block in chained.columns}
    assert _class_of(chained, "age") == patient_rules.CLASS_FIXED
    age = by_name["age"]
    assert age["top_coded"] == 90 and all(one <= 90 for one in age["percentiles"].values())
    assert age["tails"]["high"]["values"] == [90.0]
    import patient_enumeration

    for name in ("birth_date", "death_date", "enroll_date"):
        block = by_name[name]
        rung = block["time_grain"]["rung"] if isinstance(block.get("time_grain"), dict) else "day"
        holders: "dict[str, int]" = {}
        for date in held[name]:
            start = patient_enumeration.span_start(date, rung)
            holders[start] = holders.get(start, 0) + held[name][date]
        shown = re.findall(r"\d{4}-\d{2}-\d{2}", json.dumps({key: value for key, value in block.items() if key != "time_grain"}))
        assert shown or block["role"] == "identifier", name
        assert not [date for date in shown if 0 < holders.get(patient_enumeration.span_start(date, rung), 0) < FLOOR], name


def test_a_top_category_few_patients_hold_is_pooled_on_the_patient_table_as_on_its_rows(tmp_path):
    # Batch 4p's merge of this lane with lane SH3's rule (plan P4-D454): 24,000 rows of 2,000 patients,
    # twelve rows each, five of them aged 92 to 101. The rows' description pools the top-coded category
    # those five hold, counted in people, below the mark; the patient table, one row a patient, pools it
    # as a table at the floor does, so the published block names no age of 90 that five patients hold.
    # Since batch 4p's fix round the patient table takes each patient-fixed column's cells as the rows'
    # description read them, so the five come to it pooled already: its block publishes the rows' own
    # figures, and the top-code's marks stand on the rows' block alone (a stated limit, plan P4-D449).
    # MUTANT: the patient table's cells as the file wrote them and the pool's floor read on its own row
    # count (`long_table_dates` unread there): its high tail publishes 90, five patients by its rows and
    # its mean distance.
    draw = random.Random(7)
    old = {3: "92", 400: "95", 800: "97", 1200: "99", 1600: "101"}
    rows: "list[list[str]]" = []
    for patient in range(2000):
        gender = draw.choice(["F", "M"])
        age = old.get(patient, f"{draw.randint(20, 85)}")
        for _visit in range(12):
            rows += [[f"P{patient:06d}", gender, age, f"{draw.gauss(100, 12):.1f}", draw.choice(["a", "b", "c"])]]
    document, chained = _described(tmp_path, ["pid", "gender", "age", "value", "site"], rows, top_code=True)
    assert chained.grain is not None
    assert _class_of(chained, "age") == patient_rules.CLASS_FIXED
    on_rows = [block for block in document["columns"] if block["name"] == "age"][0]
    on_patients = [block for block in chained.columns if block["name"] == "age"][0]
    assert on_patients["n_present"] == 2000
    assert on_rows["top_coded"] == 90 and on_rows["top_category_pooled"] == FLOOR
    for block in (on_rows, on_patients):
        assert block["tails"]["high"]["values"] and all(one < 90 for one in block["tails"]["high"]["values"])
        assert all(one is None or one < 90 for one in block["percentiles"].values())
    assert on_patients["tails"]["high"]["values"] == on_rows["tails"]["high"]["values"]
    path = fixtures.write_profile(tmp_path, "pooled.profile.json", _switched(document, chained))
    assert contract.load_profile(str(path), chain=True) is not None


def test_a_top_coded_reading_takes_no_grid_no_own_mean_and_no_trend(tmp_path):
    # Mutant: `grid_of` reading a top-coded block: a patient's own mean of raw ages published above 90.
    draw = random.Random(8)
    rows: "list[list[str]]" = []
    for patient in range(800):
        start = draw.randint(18, 104)
        group = draw.choice(["a", "b"])
        for visit in range(draw.randint(1, 12)):
            rows += [[f"P{patient:06d}", group, f"{start + visit // 3}", draw.choice(["x", "y", "z"])]]
    for key in (TEST_KEY, b"\x01" * 32, b"\x02" * 32):
        document, chained = _described(tmp_path, ["pid", "group", "age", "site"], rows, top_code=True, key=key)
        age = [block for block in document["columns"] if block["name"] == "age"][0]
        assert age["top_coded"] == 90
        assert patient_rules.grid_of(age) is None
        assert not [entry for entry in chained.grain["derived"] if entry["source"] == "age"]
        assert not [entry for entry in chained.grain["trend"] if entry["column"] == "age"]
    assert patient_rules.grid_of({**age, "top_coded": None}) is not None


# -- THE CELLS AS THE DESCRIPTION READ THEM (Codex's review of batch 4p, item 1, HIPAA) --


def _keyed_folder(tmp_path: pathlib.Path) -> pathlib.Path:
    """An installation's data folder holding the test key, so a switched run through the command draws as the library's cases do."""
    data = tmp_path / "data"
    data.mkdir(mode=0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        data.chmod(0o700)
        key.chmod(0o600)
    key.write_bytes(TEST_KEY)
    return data


def _numbers_above(values: "list[object]", mark: int) -> "list[str]":
    """The entries of a published list that read as a number above `mark`."""
    above: "list[str]" = []
    for one in values:
        found = patient_rules.fraction_read(one)
        if found is not None and found > mark:
            above += [f"{one}"]
    return above


def test_a_position_list_reads_the_ages_as_the_description_top_coded_them(tmp_path, monkeypatch, capsys):
    # Codex's table at its size, through the switched command: 24,000 rows, 1,200 patients of 20 visits,
    # an age of 80 plus the visit index, an arm alternating by patient, `pid` the person by its name, age
    # declared a measurement, the table named `agecase`, the test key. The description top-codes age at 90;
    # the patient layer read the cells as the file wrote them and published the position list 80 to 92,
    # ages 91 and 92 among them. Unanswered and answered `yes`, no published position reads above 90 and
    # the column's block keeps its top-code; answered `no` (the column holds no age, so nothing is
    # top-coded), the list stands as the file writes it. MUTANT as_written: `chain.read_as_described` hands
    # back the cells as the file wrote them (91 and 92 published again; batch 4r's merge of lane BT3a: its
    # reader replaced the fix round's `patient_layer._as_described`, which this mutant named).
    monkeypatch.chdir(tmp_path)
    rows = [[f"P{patient:05d}", "a" if patient % 2 == 0 else "b", f"{80 + visit}"] for patient in range(1200) for visit in range(20)]
    fixtures.write(tmp_path, "agecase.csv", _csv(["pid", "arm", "age"], rows))
    data = _keyed_folder(tmp_path)
    typed = ["profile", "agecase.csv", "--identifier", "pid", "--measurement", "age"]

    def switched(answers: "dict[str, object] | None") -> "dict[str, typing.Any]":
        arguments = list(typed)
        if answers is not None:
            (tmp_path / "answers.json").write_text(json.dumps(answers), encoding="utf-8", newline="\n")
            arguments += ["--answers", "answers.json"]
        assert cli.main(arguments, chain=cli.ChainRun(name="agecase", folder=str(data), replace_description=answers is not None)) == 0
        capsys.readouterr()
        written = json.loads((tmp_path / "agecase-profile.json").read_text(encoding="utf-8"))
        assert written["settings"]["person_columns"] == ["pid"] and written["relationships"]["grain"] is not None
        assert contract.load_profile(str(tmp_path / "agecase-profile.json"), chain=True) is not None
        return written

    written = switched(None)
    asked = json.loads((tmp_path / "agecase-questions.json").read_text(encoding="utf-8"))
    for answer in (None, "yes", "no"):
        if answer is not None:
            given = json.loads(json.dumps(asked))
            put = [entry for entry in given["asked"] if entry["column"] == "age" and answer in [one["answer"] for one in entry["answers_you_can_give"]]]
            assert len(put) == 1
            put[0]["your_answer"] = answer
            written = switched(given)
        age = [block for block in written["columns"] if block["name"] == "age"][0]
        listed = [entry["values"] for entry in written["relationships"]["grain"]["positions"] if entry["column"] == "age"]
        if answer == "no":
            assert age.get("top_coded") is None and listed == [[f"{80 + visit}" for visit in range(13)]]
            continue
        assert not [one for values in listed for one in _numbers_above(values, 90)], answer
        assert age["top_coded"] == 90, answer


def test_a_position_list_s_first_entry_reads_the_age_as_the_description_top_coded_it(tmp_path, monkeypatch, capsys):
    # The scoped verify of batch 4p's fix round, its carry 1 (the orchestrator's LANE I4p RULINGS 7 (2) (a)),
    # at the table floor through the switched command: 22,000 rows, 2,000 patients of 11 visits, the first
    # visit's age 92 and the next ten 80 to 89, an arm alternating by patient, `pid` the person by its name,
    # age a measurement, unanswered, the test key. Read with every age above 89 as 90, no patient holds an
    # age twice, so the column stays position-like on its cells as the description read them (its block
    # emptied, the list in its place), and its position list must open at 90, every later position the
    # file's own age: the sealed head `d8f5e147` opened it at 92. MUTANT lists_read_raw (the verify's
    # mutant B: the classes read the described cells and the position lists the cells as the file wrote
    # them), which the case above leaves green, publishes 92 again.
    monkeypatch.chdir(tmp_path)
    rows = [[f"P{patient:05d}", "a" if patient % 2 == 0 else "b", "92" if visit == 0 else f"{79 + visit}"] for patient in range(2000) for visit in range(11)]
    fixtures.write(tmp_path, "firstage.csv", _csv(["pid", "arm", "age"], rows))
    data = _keyed_folder(tmp_path)
    typed = ["profile", "firstage.csv", "--identifier", "pid", "--measurement", "age"]
    assert cli.main(typed, chain=cli.ChainRun(name="firstage", folder=str(data))) == 0
    capsys.readouterr()
    written = json.loads((tmp_path / "firstage-profile.json").read_text(encoding="utf-8"))
    grain = written["relationships"]["grain"]
    assert written["settings"]["person_columns"] == ["pid"] and grain is not None
    assert {entry["column"]: entry["class"] for entry in grain["classes"]}["age"] == patient_rules.CLASS_POSITION
    listed = [entry["values"] for entry in grain["positions"] if entry["column"] == "age"]
    assert len(listed) == 1, listed
    assert len(listed[0]) >= 2 and listed[0] == ["90"] + [f"{79 + visit}" for visit in range(1, len(listed[0]))], listed[0]
    assert not _numbers_above(listed[0], 90)
    assert contract.load_profile(str(tmp_path / "firstage-profile.json"), chain=True) is not None


def _figures_of(block: "dict[str, typing.Any]") -> "list[float]":
    """Every value a number block publishes (its ends, mean, mode, rungs and tails), never a count."""
    found: "list[object]" = [block.get(key) for key in ("min", "max", "mean", "mode")]
    found += list((block.get("percentiles") or {}).values()) + list((block.get("percentiles_between") or {}).values())
    for side in (block.get("tails") or {}).values():
        if isinstance(side, dict):
            found += list(side.get("values") or [])
    return [float(one) for one in found if isinstance(one, (int, float)) and not isinstance(one, bool)]


def test_a_fixed_year_of_birth_reaches_the_patient_table_as_the_description_top_coded_it(tmp_path, monkeypatch, capsys):
    # The sibling sweep of Codex's item 1 (HIPAA), at the table floor through the switched command: 24,000
    # rows, 1,200 patients of 20 visits, a year of birth fixed by patient from 1925 to 1960 (each year held
    # by 33 or more patients) and one stray cell `19` on a patient's sixth row, the shape the row description
    # top-codes at 1937. The patient table took each patient's first cell as the file wrote it, held no stray,
    # and its own description published years of 1925 and on in the column's block and a band of 102
    # patients below its p10 in the patient chain. Read as the row description read it, the patient table
    # holds 1937 for every earlier year: no published figure and no band of patients lies below the cut.
    # MUTANT raw_patient_table: the patient table's cells read as the file wrote them again.
    monkeypatch.chdir(tmp_path)
    draw = random.Random(20261106)
    rows = [[f"P{patient:05d}", "a" if patient % 2 == 0 else "b", f"{1925 + patient % 36}", f"{draw.gauss(100, 12):.1f}"] for patient in range(1200) for _visit in range(20)]
    rows[5][2] = "19"
    fixtures.write(tmp_path, "yearcase.csv", _csv(["pid", "arm", "birth_year", "value"], rows))
    data = _keyed_folder(tmp_path)
    typed = ["profile", "yearcase.csv", "--identifier", "pid", "--measurement", "birth_year", "--measurement", "value"]
    assert cli.main(typed, chain=cli.ChainRun(name="yearcase", folder=str(data))) == 0
    capsys.readouterr()
    written = json.loads((tmp_path / "yearcase-profile.json").read_text(encoding="utf-8"))
    grain = written["relationships"]["grain"]
    assert grain is not None and {entry["column"]: entry["class"] for entry in grain["classes"]}["birth_year"] == patient_rules.CLASS_FIXED
    block = [one for one in written["columns"] if one["name"] == "birth_year"][0]
    assert block["n_present"] == 1200 and _figures_of(block)
    assert not [one for one in _figures_of(block) if one < 1937]
    rungs = {**(block.get("percentiles") or {}), **(block.get("percentiles_between") or {})}
    for entry in written["relationships"]["statistical"]["ladder"]:
        if entry["column"] != "birth_year":
            continue
        for band, total in zip(entry["l0"], entry["totals"]):
            if not all(isinstance(one, list) and len(one) == 2 for one in band):
                continue
            low, high = band[0][0], band[-1][1]
            assert not (low is None and high is not None and rungs[high] <= 1937 and total), (band, total)
    assert contract.load_profile(str(tmp_path / "yearcase-profile.json"), chain=True) is not None


# -- A SEQUENCE COLUMN IS NEVER A BLOCK (repair 1, the census under another name) --


def _visit_numbers(rows_wanted: int, seed: int, skipped: int = 0) -> "tuple[list[str], list[list[str]]]":
    """Rows a patient heavy-tailed, the largest far past 20 visits, a visit number 1 .. r; `skipped` the visit number every patient jumps past."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    patient = 0
    while len(rows) < rows_wanted:
        count = min(1 + int(math.exp(draw.gauss(math.log(3.0), 1.82))), rows_wanted - len(rows))
        gender = draw.choice(["F", "M"])
        base = draw.gauss(100, 15)
        for visit in range(count):
            number = visit + 1 + (1 if skipped and visit + 1 >= skipped else 0)
            rows += [[f"P{patient:07d}", gender, f"{number}", f"{base + draw.gauss(0, 7):.1f}", draw.choice(["a", "b", "c"])]]
        patient += 1
    return ["pid", "gender", "visit_no", "value", "site"], rows


def test_a_visit_number_of_many_readings_publishes_no_block_and_no_census(tmp_path):
    # At the floor size, one case. Mutant: a FINE column never tested (its block stands: the largest r
    # as `n_distinct`, one patient fixed by the tail); a fine run given an own mean or a row family.
    header, rows = _visit_numbers(20000, 3)
    document, chained = _described(tmp_path, header, rows)
    assert _class_of(chained, "visit_no") == patient_rules.CLASS_POSITION
    block = [one for one in chained.columns if one["name"] == "visit_no"][0]
    assert patient_rules.emptied(block)
    listed = [entry["values"] for entry in chained.grain["positions"] if entry["column"] == "visit_no"][0]
    assert listed == [f"{at + 1}" for at in range(chained.grain["census"]["lo"])]
    assert not [entry for entry in chained.grain["derived"] if entry["source"] == "visit_no"]
    assert not [entry for entry in chained.grain["rows"] if entry["child"] == "visit_no"]
    path = fixtures.write_profile(tmp_path, "seq.profile.json", _switched(document, chained))
    contract.load_profile(str(path), chain=True)


def test_a_fine_run_whose_list_cannot_stand_is_held_never_a_block():
    # Mutants: a `null` or an out-of-order entry let the list stand; a run read on raw steps alone
    # (a week counted in fours, a visit missed); a repeated reading read as a run.
    assert patient_layer._run_list(["1", "2", "3"]) and patient_layer._run_list(["9", "5"])
    assert not patient_layer._run_list(["1", None, "3"]) and not patient_layer._run_list(["1", "3", "2"])
    assert not patient_layer._run_list([])
    frac = patient_rules.fractions.Fraction
    one_patient = types.SimpleNamespace(rows=[[0, 1, 2, 3], [4, 5]])
    def broken(readings: "list[int | None]") -> int:
        return patient_layer._not_a_run([None if one is None else frac(one) for one in readings], one_patient)
    assert broken([4, 8, 12, 16, 8, 12]) == 0
    assert broken([1, 2, 4, 5, 1, 2]) == 0
    assert broken([1, 2, None, 3, 1, 2]) == 0
    # A visit written twice is a row written twice (the verify of repair 1, item 2): one repeat in four
    # readings, or in three, keeps the run; two in four, or one in two, break it.
    assert broken([1, 1, 2, 3, 1, 2]) == 0
    assert broken([1, 2, 2, None, 1, 2]) == 0
    assert broken([1, 1, 2, 2, 1, 2]) == 1
    assert broken([1, 2, 3, 4, 5, 5]) == 1
    # A repeat is allowed, a gap is not (the verify 2 of lane GRa, item 2): one reading written twice beside
    # a jump its DIFFERENT readings cannot span (1, 1, 2 and 5, the column holding 3 and 4 on another
    # patient: three different readings over five ranks, against 3 + 0 + 1). MUTANT own_v2_span_all: the
    # span read over every reading again (4 + 1 + 1), and the patient reads as a run.
    assert broken([1, 1, 2, 5, 3, 4]) == 1
    many = types.SimpleNamespace(rows=[[0, 1], [2, 3, 4, 5, 6, 7, 8, 9, 10, 11]])
    assert patient_layer._not_a_run([frac(one) for one in (1, 12, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)], many) == 1


def test_a_visit_number_beside_a_tied_first_position_is_held(tmp_path):
    # The list has a `null`, so the column is HELD: its block stays empty, no census by another name.
    # Mutant: the column falling back to its block (`repeated`) where its list cannot stand.
    rows: "list[list[str]]" = []
    draw = random.Random(14)
    for patient in range(600):
        first = 1 if patient % 2 else 40
        for visit in range(1 + patient % 30):
            rows += [[f"P{patient:06d}", f"{first + visit}", f"{draw.gauss(50, 9):.1f}"]]
    document, chained = _described(tmp_path, ["pid", "visit_no", "value"], rows)
    assert _class_of(chained, "visit_no") == patient_rules.CLASS_HELD
    assert patient_rules.emptied([one for one in chained.columns if one["name"] == "visit_no"][0])


def _visits_beside_a_lone_top(seed: int) -> "tuple[list[str], list[list[str]]]":
    """A visit number 1 .. r, one patient far above the rest (900 visits, every other at most 600), and a visit written twice on about one patient in twenty of three visits or more."""
    header, wide = _visit_numbers(21000, seed)
    rows: "list[list[str]]" = []
    held: "dict[str, int]" = {}
    for row in wide:
        held[row[0]] = held[row[0]] + 1 if row[0] in held else 1
        if held[row[0]] <= 600:
            rows += [row]
    rows += [["P9999999", "F", f"{visit + 1}", f"{100 + visit % 7}.0", "a"] for visit in range(900)]
    places: "dict[str, list[int]]" = {}
    for at in range(len(rows)):
        if rows[at][0] not in places:
            places[rows[at][0]] = []
        places[rows[at][0]] += [at]
    draw = random.Random(seed + 1)
    for patient in sorted(places):
        own = places[patient]
        if patient != "P9999999" and len(own) >= 3 and draw.random() < 0.05:
            rows[own[2]][2] = rows[own[1]][2]
    return header, rows


def test_a_visit_number_written_twice_on_a_few_patients_publishes_no_block(tmp_path):
    # The verify of repair 1, item 2, at the floor size: a visit number with one reading written twice
    # on a few patients read `repeated`, and its block published `n_distinct` 900 and the high tail's
    # rows of the one patient above 600 visits. MUTANT: a repeated reading breaking the run whatever
    # its share of the patient's rows (the block stands, the largest `r` named by `n_distinct`).
    header, rows = _visits_beside_a_lone_top(3)
    assert len(rows) >= 20000
    document, chained = _described(tmp_path, header, rows)
    assert _class_of(chained, "visit_no") in (patient_rules.CLASS_POSITION, patient_rules.CLASS_HELD)
    block = [one for one in chained.columns if one["name"] == "visit_no"][0]
    assert patient_rules.emptied(block)
    assert not [entry for entry in chained.grain["rows"] if entry["child"] == "visit_no"]
    path = fixtures.write_profile(tmp_path, "twice.profile.json", _switched(document, chained))
    contract.load_profile(str(path), chain=True)


# -- THE PERSON BLOCK READS THE PATIENTS (repair 1) --


def test_the_person_block_reads_its_forms_over_the_patients_and_holds_no_small_pool(tmp_path):
    # Mutants: `layout_prefixes` or the lengths read in rows beside forms read in patients (the
    # loader refuses the layer's own description); a pool of 1 to f - 1 patients published.
    draw = random.Random(6)
    rows: "list[list[str]]" = []
    for patient in range(1300):
        gender = draw.choice(["F", "M"])
        for _visit in range(draw.randint(1, 7)):
            rows += [[f"P{patient:06d}", gender, f"{draw.gauss(50, 9):.1f}", draw.choice(["x", "y", "z"])]]
    for _visit in range(60):
        rows += [["ZZ-99", "F", f"{draw.gauss(50, 9):.1f}", "x"]]
    for other in range(3):
        for _visit in range(40):
            rows += [[f"QX{other}", "M", f"{draw.gauss(50, 9):.1f}", "y"]]
    document, chained = _described(tmp_path, ["pid", "gender", "value", "site"], rows)
    assert chained.grain is not None
    person = [one for one in chained.columns if one["name"] == "pid"][0]
    forms = person["layout_forms"]
    assert all(count == 0 or count >= FLOOR for count in forms.values()), forms
    path = fixtures.write_profile(tmp_path, "forms.profile.json", _switched(document, chained))
    contract.load_profile(str(path), chain=True)
    # A pool of forms joins the smallest named form until it reaches the floor, its prefix unnamed with it.
    block = {"layout_forms": {"@%%": 40, "@@%": 30, "(withheld)": 4}, "layout_prefixes": {"@%%": "A", "@@%": "BB"}, "layout_exclusions": {"@@%": "Z"}}
    pooled = patient_layer._person_counts_floored(block, FLOOR)
    assert pooled["layout_forms"] == {"(withheld)": 34, "@%%": 40} and pooled["layout_prefixes"] == {"@%%": "A"} and pooled["layout_exclusions"] == {}


# -- THE GATE'S OTHER GUARDS (repair 1) --


def test_the_held_repeat_and_one_person_written_two_ways_turn_the_layer_off(tmp_path):
    # Mutants: the layer standing beside a held repeating column; `merged_key` read as the raw text,
    # or the merged count unread: P00001 beside P-00001 is one person (the POP ruling).
    header, rows = _visits(600, 5)
    _document, chained = _described(tmp_path / "held", header, rows, held=("site",))
    assert chained.grain is None and any(patient_layer.OFF_HELD in note for note in chained.notes)
    spelled = [["S-00001" if row[0] == "S00001" and at % 2 else row[0]] + row[1:] for at, row in enumerate(rows)]
    _document, chained = _described(tmp_path / "merged", header, spelled)
    assert chained.grain is None and any(patient_layer.OFF_MERGED in note for note in chained.notes)


def test_a_multiplicity_map_of_any_other_column_is_withheld(tmp_path):
    # Mutant: another column's map kept while the layer stands (a sparse label's map counts rows a value covers).
    header, rows = _visits(800, 21)
    draw = random.Random(22)
    words = ["pain", "fever", "cough", "nausea", "rash", "dizzy", "tired", "chills", "ache", "sore"]
    rows = [row + [" ".join(draw.choice(words) for _word in range(draw.randint(2, 6)))] for row in rows]
    document, chained = _described(tmp_path, header + ["memo"], rows)
    original = {block["name"]: block for block in document["columns"]}
    assert [name for name in original if name != "pid" and isinstance(original[name].get("n_distinct_by_occurrences"), dict) and len(original[name]["n_distinct_by_occurrences"]) > 1]
    for block in chained.columns:
        found = block.get("n_distinct_by_occurrences")
        assert found is None or (len(found) == 1 and list(found.values()) == [block["n_present"]]), block["name"]


def _witness_table() -> "tuple[list[str], list[list[str]]]":
    """A label whose real class stands (`V` 12, `V_K` 14, each above `T`) where the only floored world of its own counts holds every patient of two rows on both levels, or none."""
    rows: "list[list[str]]" = []
    at = 0
    for pattern, count in ((("a", "a"), 6), (("b", "b"), 6), (("a", "b"), 7), (("b", "a"), 7), (("a",), 20), (("b",), 20)):
        for _patient in range(count):
            rows += [[f"S{at:05d}", one] for one in pattern]
            at += 1
    return ["pid", "x"], rows


def test_the_producer_reads_the_class_witness(tmp_path):
    # Mutant: the witness dropped in the producer (a label the class witness refuses kept in rows).
    header, rows = _witness_table()
    found = patient_rules.certificate(patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (26,), (0,)), [(2, 2)], [[0]], [26, 26], 2, [((2, 26),)], False, None, FLOOR, FLOOR, {})
    assert found is False
    assert patient_rules.certificate(patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (26,), (0,)), [(2, 2)], [[0]], [26, 26], 2, [((2, 26),)], False, None, None, FLOOR, {}) is True
    for key in (TEST_KEY, b"\x05" * 32, b"\x06" * 32):
        _document, chained = _described(tmp_path, header, rows, key=key)
        if chained.grain is None:
            continue
        assert _class_of(chained, "x") == patient_rules.CLASS_HELD
        assert not chained.grain["rows"]


def test_the_one_cell_family_reads_its_certificate_and_the_pigeonhole_is_held():
    # Item 6, `one_cell_pigeonhole.py`: 20 patients of two rows, a band of 21 of 40 rows: no certificate,
    # the column HELD; 22 with 23 of 44: PWIT holds. Mutant: the one-cell certificate dropped.
    import patient_enumeration

    found = patient_enumeration.page_cases()
    assert found["one_cell_pigeonhole_passing"] == 0 and found["one_cell_neighbour_passing"] == 1
    assert found["fine_child_one_reading_spans_two"] == 0 and found["fine_child_split_taken"] == 1
    def row_of(first: int, second: int, fine: bool) -> "types.SimpleNamespace":
        names = (((None, "p50"),), (("p50", None),))
        ladder = chain.rules.Ladder("x", names, ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (first, second), (True, True))
        return types.SimpleNamespace(ladder=ladder, block={"percentiles": {"p50": 7}, "role": "count"}, key_read=False, fine=fine)

    def context_of(patients: int) -> "tuple[types.SimpleNamespace, types.SimpleNamespace]":
        cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (patients,), (0,))
        return (
            types.SimpleNamespace(census=patient_rules.census_at(3, {2: patients}), floor=FLOOR, threshold=FLOOR - 1, values_r=[(2, 2)], counts={}, stars=[((2, patients),)]),
            types.SimpleNamespace(patients=cells.patients, r_band=cells.r_band, sizes=cells.sizes, members=cells.members),
        )

    context, grain = context_of(20)
    assert patient_layer._one_cell(context, grain, row_of(21, 19, True), None) is False
    context, grain = context_of(22)
    assert patient_layer._one_cell(context, grain, row_of(23, 21, True), None) is True
    assert patient_layer._one_cell(context, grain, row_of(23, 21, False), None) is False


# -- R*'S ONE TIE (repair 1, HIPAA) --


def _crossing_table(count: int) -> "tuple[list[str], list[list[str]]]":
    """Two labels `x` and `y` and four repeated columns tied to one of them; the top band's rows fall so that no floored world meets both margins."""
    tops = {(0, 0): [4] * 30, (1, 0): [4] * 24, (0, 1): [6] * 6 + [7] * 6, (1, 1): [4] * 5 + [6] * 21 + [7] * 4}
    rows: "list[list[str]]" = []
    at = 0
    for (x, y), top in tops.items():
        for r in (1, 2, 3):
            rare = [(2 * count // 3 if x == 0 else 15) if k % 2 == 0 else (2 * count // 3 if y == 0 else 15) for k in range(4)]
            for _patient in range(count):
                for _row in range(r):
                    labels = []
                    for k in range(4):
                        labels += ["b" if rare[k] > 0 else "a"]
                        rare[k] -= 1
                    rows += [[f"P{at:07d}", "xa" if x == 0 else "xb", "yp" if y == 0 else "yq"] + labels]
                at += 1
        for r in top:
            for row in range(r):
                rows += [[f"P{at:07d}", "xa" if x == 0 else "xb", "yp" if y == 0 else "yq"] + [("b" if row < 2 else "a")] * 4]
            at += 1
    return ["pid", "x", "y", "c1", "c2", "c3", "c4"], rows


def test_one_r_star_ties_every_row_family_and_the_loader_repeats_it(tmp_path, monkeypatch):
    # Mutants: the tie read family by family (crossing cuts both taken: the producer then meets no
    # crossing, which this case counts); the loader's tie dropped.
    import patient_enumeration

    found = patient_enumeration.crossing_cuts()
    assert found["cut_refused"] == 1 and found["cut_coarser_taken"] == 1 and found["cut_no_floored_world"] == 1
    assert found["cut_large_margins_leak"] == 1 and found["cut_large_alone_leak"] == 0
    assert found["cut_small_both_leak"] == 1 and found["cut_small_alone_leak"] == 0
    # THE PRODUCER READS EVERY OPTION'S CUT AGAINST THE TIE (the verify's item 4): an option whose
    # top-band cut crosses the one standing is refused there, so the producer meets a crossing.
    joined = patient_rules.blocks_joined
    met = {"crossings": 0, "producing": 0}

    def watched(first: "dict[frozenset[int], int]", second: "dict[frozenset[int], int]") -> "dict[frozenset[int], int] | None":
        found_joined = joined(first, second)
        if met["producing"] and found_joined is None and len(first) > 1 and len(second) > 1:
            met["crossings"] += 1
        return found_joined

    monkeypatch.setattr(patient_rules, "blocks_joined", watched)
    header, rows = _crossing_table(120)
    tampered = False
    for key in (bytes([k]) * 32 for k in range(6)):
        met["producing"] = 1
        document, chained = _described(tmp_path / "tied", header, rows, key=key)
        met["producing"] = 0
        cuts = [tuple(sorted(parent["column"] for parent in entry["parents"] if parent["column"] != patient_rules.R_NAME)) for entry in chained.grain["rows"]]
        assert not (("x",) in cuts and ("y",) in cuts), key
        members = {name for family in chained.statistical["chain"][chained.grain["grain_family"]:chained.grain["grain_family"] + 1] for name in [family["child"]] + [parent["column"] for parent in family["parents"]]} if chained.grain["grain_family"] is not None else set()
        if cuts.count(("x",)) >= 2 and "y" in members:
            switched = _switched(document, chained)
            for parent in [entry for entry in switched["relationships"]["grain"]["rows"] if {"x"} <= {one["column"] for one in entry["parents"]}][1]["parents"]:
                if parent["column"] == "x":
                    parent["column"] = "y"
                    parent["level"] = "L2"
            path = fixtures.write_profile(tmp_path, "crossed.profile.json", switched)
            with pytest.raises(errors.ProfileError) as caught:
                contract.load_profile(str(path), chain=True)
            assert "one R*" in str(caught.value)
            tampered = True
    assert tampered
    assert met["crossings"] > 0


# -- THE LOADER RECOMPUTES (repair 1) --


def _loaded_or_refused(tmp_path: pathlib.Path, switched: "dict[str, object]", name: str, words: str) -> None:
    path = fixtures.write_profile(tmp_path, f"{name}.profile.json", switched)
    with pytest.raises(errors.ProfileError) as caught:
        contract.load_profile(str(path), chain=True)
    assert words in str(caught.value), caught.value


def test_the_loader_reads_each_row_family_s_floor(tmp_path, trend_layer):
    # Mutant: S31's floor on a row family's cell dropped.
    document, chained = trend_layer
    switched = _switched(document, chained)
    family = switched["relationships"]["grain"]["rows"][0]
    small = json.loads(json.dumps(switched))
    table = small["relationships"]["grain"]["rows"][0]["table"]
    moved = table[0][0] - 3
    table[0][0] = 3
    table[0][1] += moved
    _loaded_or_refused(tmp_path, small, "cell", "every cell is 0 or at least the floor")
    assert family["table"]


def test_the_loader_recomputes_a_row_family_s_certificate(tmp_path, monkeypatch):
    # Mutant: the certificate's re-check dropped in the loader: a family the producer's certificate
    # refuses, published by a producer told otherwise, is refused on its published counts.
    header, rows = _witness_table()
    real = patient_rules.certificate
    monkeypatch.setattr(patient_rules, "certificate", lambda *_args: True)
    published = False
    for key in (TEST_KEY, b"\x05" * 32, b"\x06" * 32, b"\x07" * 32):
        monkeypatch.setattr(patient_rules, "certificate", lambda *_args: True)
        document, chained = _described(tmp_path, header, rows, key=key)
        monkeypatch.setattr(patient_rules, "certificate", real)
        if chained.grain is not None and _class_of(chained, "x") != patient_rules.CLASS_HELD:
            published = True
            _loaded_or_refused(tmp_path, _switched(document, chained), "certificate", "certificate holds")
    assert published


def test_the_loader_reads_the_trend_s_guard(tmp_path, monkeypatch):
    # Mutant: the guard of 4.6c.1 (b) 6 dropped in the loader: a trend the producer's guard
    # refuses, published by a producer told otherwise, is refused on its published counts.
    draw = random.Random(41)
    rows: "list[list[str]]" = []
    for patient in range(3000):
        base = draw.gauss(100, 12)
        visits = 4 if patient % 2 else 6
        for j in range(visits):
            rows += [[f"S{patient:05d}", f"2024-{1 + j:02d}-{1 + patient % 28:02d}", f"{base + 0.8 * j + draw.gauss(0, 6):.1f}"]]
    real = patient_rules.free_rows
    monkeypatch.setattr(patient_rules, "free_rows", lambda *_args: 10 ** 9)
    document, chained = _described(tmp_path, ["pid", "visit_date", "value"], rows, name="schedules")
    monkeypatch.setattr(patient_rules, "free_rows", real)
    assert chained.grain["trend"], chained.notes
    _loaded_or_refused(tmp_path, _switched(document, chained), "guard", "keep their code total free")


def test_the_loader_refuses_a_fine_census_and_a_family_at_a_fine_child(tmp_path, trend_layer):
    # Mutants: the census's cap unread by the loader; the keyed family's `L2` rule unread by the loader.
    document, chained = trend_layer
    switched = _switched(document, chained)
    wide = json.loads(json.dumps(switched))
    census = wide["relationships"]["grain"]["census"]
    while census["lo"] <= patient_rules.CENSUS_TOP_EDGE_MAX:
        census["bands"] += [{"patients": 0, "r": census["lo"]}]
        census["lo"] += 1
    census["top"] = {"patients": 0, "rows": 0}
    _loaded_or_refused(tmp_path, wide, "wide", "at most 12 single values")
    placed = [chain.rules.Family("A", 0, (), None, (20, 20))]
    three = chain.rules.Ladder("x", (("a",), ("b",), ("c",)), ((0, 1, 2), (0, 1, 1), (0, 0, 1)), (3, 2, 2), (20, 20, 20), (True, True, True))
    scales = {"C": three, patient_rules.R_NAME: three, "A": three}
    fine = chain.Option("C", (patient_rules.R_NAME,), (0, 0), 0, (), chain.fractions.Fraction(0))
    median = chain.Option("C", (patient_rules.R_NAME,), (2, 0), 0, (), chain.fractions.Fraction(0))
    assert not patient_layer._keeps_keyed_rule(placed, fine, set(), True, scales)
    assert patient_layer._keeps_keyed_rule(placed, median, set(), True, scales)
    # After a derived column is drawn the child is free: the rule reads the first stage alone.
    assert patient_layer._keeps_keyed_rule(placed, fine, {"(own mean of z)"}, True, scales)


def test_the_census_offers_at_most_twelve_single_values(tmp_path):
    # Mutant: the cap dropped (a census of 58 single values leaves no row family on long tables).
    values: "list[int]" = []
    for rho in range(1, 40):
        values += [rho] * 15
    found, _steps = patient_layer.census_candidates(values, FLOOR)
    assert found and max(census.lo for census, _steps in found) == patient_rules.CENSUS_TOP_EDGE_MAX
    assert all(census.top_patients >= FLOOR for census, _steps in found)


def test_the_floored_split_counts_every_trial_and_names_its_give_up(monkeypatch):
    # Mutant: a kept split counted as no step, so a search over kept splits runs past its bound.
    classes = [patient_rules.Klass(40, 3, (0, 0), (3, 3)), patient_rules.Klass(30, 4, (0, 0), (4, 4))]
    budget: "dict[object, object]" = {"spent": 0}
    kept = patient_rules._split_kept(40, 7, FLOOR, budget)
    once = budget["spent"]
    assert patient_rules._split_kept(40, 7, FLOOR, budget) is kept
    assert budget["spent"] == once + 1
    found_at_default = patient_rules.floored_split(classes, [31, 209], FLOOR)
    assert found_at_default.blocks
    monkeypatch.setattr(patient_rules, "SPLIT_TRIES_MAX", 2)
    assert patient_rules.floored_split(classes, [31, 209], FLOOR).bound == patient_rules.SPLIT_BOUND
    counts: "dict[str, int]" = {}
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (2,), (40, 30), (0, 1))
    assert patient_rules.certificate(cells, [(3, 3), (4, 4)], [[0, 1]], [31, 209], 2, [((3, 40),), ((4, 30),)], False, None, None, FLOOR, counts) is False
    assert counts["split_bound_hit"] == 1


def test_the_loader_on_the_default_path_keeps_its_repetition_rule(tmp_path):
    # Mutant: `_pattern_closes` read only where a map holds pairs: an identifier's empty map loads with the chain off.
    header, rows = _visits(900, 4)
    fixture = fixtures.write(tmp_path, "t.csv", _csv(header, rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",))
    table = reading.read_table(str(fixture), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"])
    path = fixtures.write_profile(tmp_path, "ok.profile.json", document)
    contract.load_profile(str(path))
    emptied = json.loads(json.dumps(document))
    for block in emptied["columns"]:
        if block["name"] == "pid":
            block["n_distinct_by_occurrences"] = {}
    path = fixtures.write_profile(tmp_path, "empty.profile.json", emptied)
    with pytest.raises(errors.ProfileError):
        contract.load_profile(str(path))


def test_the_default_is_the_hold(tmp_path):
    # Mutant: `ChainSwitch.rows_per_person` defaulting to a grain no question stated.
    header, rows = _visits(600, 6)
    assert chain.ChainSwitch("t", TEST_KEY).rows_per_person == chain.ROWS_OPEN
    path = fixtures.write(tmp_path, "t.csv", _csv(header, rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"])
    assert chain.describe(table, document, settings, chain.ChainSwitch("t", TEST_KEY)).statistical is None
    for stated, drawn in ((chain.ROWS_UNNAMED, False), (chain.ROWS_ONE, False), (chain.ROWS_PERSON, True)):
        found = chain.describe(table, document, settings, chain.ChainSwitch("t", TEST_KEY, rows_per_person=stated))
        assert (found.grain is not None) == drawn, stated


# -- THE PERSON AND THE RECORD (RULINGS 1 (1), HIPAA) --


def _lines(rows_wanted: int) -> "tuple[list[str], list[list[str]]]":
    """Invented lines of encounters beside an encounter key and, here, a patient key: one person, many encounters."""
    draw = random.Random(5)
    rows: "list[list[str]]" = []
    encounter = 0
    person = 0
    while len(rows) < rows_wanted:
        person += 1
        gender = draw.choice(["F", "M"])
        for _encounter in range(1 + int(draw.expovariate(1 / 3))):
            encounter += 1
            for _line in range(1 + int(draw.expovariate(1 / 3))):
                rows += [[f"E{encounter:07d}", f"M{person:06d}", gender, draw.choice(["A10", "B20", "C30", "D40", "E50", "F60"]), draw.choice("YN"), f"{draw.gauss(100, 15):.1f}"]]
    return ["enc_id", "member", "gender", "dx", "poa", "charge"], rows


def _switched_run(tmp_path: pathlib.Path, arguments: "list[str]", capsys: "typing.Any", questions: "dict[str, object] | None" = None) -> "tuple[dict[str, object], dict[str, object]]":
    if questions is not None:
        (tmp_path / "answers.json").write_text(json.dumps(questions), encoding="utf-8", newline="\n")
        arguments = arguments + ["--answers", "answers.json"]
    run = cli.ChainRun(folder=str(tmp_path / "data"), replace_description=questions is not None)
    assert cli.main(arguments, chain=run) == 0
    capsys.readouterr()
    return (
        json.loads((tmp_path / "lines-profile.json").read_text(encoding="utf-8")),
        json.loads((tmp_path / "lines-questions.json").read_text(encoding="utf-8")),
    )


def test_a_repeating_key_nothing_reads_as_the_person_holds_the_layer_at_the_floor_size(tmp_path, monkeypatch, capsys):
    # One case at the floor size. Mutants: `identifier` read as the person whatever the key (the layer
    # counting encounters as patients); the question not put on a typed key; the answer not kept.
    monkeypatch.chdir(tmp_path)
    header, rows = _lines(20000)
    kept = [0, 2, 3, 4, 5]
    fixtures.write(tmp_path, "lines.csv", _csv([header[at] for at in kept], [[row[at] for at in kept] for row in rows]))
    written, asked = _switched_run(tmp_path, ["profile", "lines.csv", "--identifier", "enc_id"], capsys)
    assert written["relationships"]["grain"] is None and written["relationships"]["statistical"] is None
    entry = asked[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]
    assert "enc_id" in entry["seen"] and entry["your_answer"] == ""


def test_the_subject_question_s_answers_on_a_repeating_key(tmp_path, monkeypatch, capsys):
    # Mutants: the answer "no column names the person" read as the person; an answer naming the key unread; the answer not kept.
    monkeypatch.chdir(tmp_path)
    header, rows = _lines(4000)
    kept = [0, 2, 3, 4, 5]
    fixtures.write(tmp_path, "lines.csv", _csv([header[at] for at in kept], [[row[at] for at in kept] for row in rows]))
    typed = ["profile", "lines.csv", "--identifier", "enc_id"]
    _written, asked = _switched_run(tmp_path, typed, capsys)
    entry = asked[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]
    entry["your_answer"] = asking.ANSWER_NO_PERSON_COLUMN
    written, again = _switched_run(tmp_path, typed, capsys, asked)
    assert written["relationships"]["grain"] is None and written["relationships"]["statistical"] is None
    assert again[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] == asking.ANSWER_NO_PERSON_COLUMN
    entry["your_answer"] = asking.ANSWER_ONE_ROW_EACH
    written, _again = _switched_run(tmp_path, typed, capsys, asked)
    assert written["relationships"]["grain"] is None and written["relationships"]["statistical"] is None
    entry["your_answer"] = "enc_id"
    written, again = _switched_run(tmp_path, typed, capsys, asked)
    assert written["relationships"]["grain"] is not None
    assert again[asking.BETWEEN_COLUMNS][asking.COLUMNS_SAID]["person"] == ["enc_id"]
    written, _again = _switched_run(tmp_path, typed, capsys, again)
    assert written["relationships"]["grain"] is not None


def test_a_key_of_the_person_beside_a_key_of_the_record_stands_as_one_person_column(tmp_path, monkeypatch, capsys):
    # A patient key beside an encounter key: exactly one person column once they are read (RULINGS 1 (1)).
    # Mutants: both keys left person columns (the gate off); the name's record word unread.
    monkeypatch.chdir(tmp_path)
    header, rows = _lines(4000)
    fixtures.write(tmp_path, "lines.csv", _csv(header, rows))
    written, _asked = _switched_run(tmp_path, ["profile", "lines.csv", "--identifier", "enc_id", "--identifier", "member"], capsys)
    assert written["settings"]["person_columns"] == ["member"]
    assert written["relationships"]["grain"]["person"] == "member"
    assert sorted(written["settings"]["forced_identifiers"]) == ["enc_id", "member"]
    assert asking.names_a_person("PatientSurrogateKey") and asking.names_a_person("pat_num")
    for name in ("patient_encounter_id", "enc_id", "record_no", "patient_visit_id", "patient_name", "patient_zip", "id", "rsid"):
        assert not asking.names_a_person(name), name
    for name in ("patient_id", "PERSON_ID", "PATID", "pid_3", "subject_reference", "member_no"):
        assert asking.names_a_person(name), name


def test_the_person_question_offers_the_record_answer_only_behind_the_switch(tmp_path, monkeypatch, capsys):
    # Mutants: `record` offered on a shipped run (a byte moved); `record` read as the person.
    monkeypatch.chdir(tmp_path)
    draw = random.Random(9)
    rows: "list[list[str]]" = []
    for key in range(700):
        for _line in range(1 + key % 5):
            rows += [[f"K{key:05d}xz", draw.choice(["F", "M"]), f"{draw.gauss(100, 15):.1f}"]]
    fixtures.write(tmp_path, "lines.csv", _csv(["ref", "gender", "charge"], rows))
    assert cli.main(["profile", "lines.csv"]) == 0
    capsys.readouterr()
    plain = json.loads((tmp_path / "lines-questions.json").read_text(encoding="utf-8"))
    def answers_of(document: "dict[str, object]") -> "list[str]":
        return [choice["answer"] for entry in document["asked"] if entry["column"] == "ref" for choice in entry["answers_you_can_give"]]
    assert asking.ANSWER_RECORD not in answers_of(plain) and asking.ANSWER_IDENTIFIER in answers_of(plain)
    written, asked = _switched_run(tmp_path, ["profile", "lines.csv", "--replace"], capsys)
    assert asking.ANSWER_RECORD in answers_of(asked) and asking.ANSWER_IDENTIFIER in answers_of(asked)
    assert written["relationships"]["grain"] is None
    for entry in asked["asked"]:
        if entry["column"] == "ref":
            entry["your_answer"] = asking.ANSWER_RECORD
    written, again = _switched_run(tmp_path, ["profile", "lines.csv"], capsys, asked)
    assert written["relationships"]["grain"] is None and written["relationships"]["statistical"] is None
    assert again[asking.BETWEEN_COLUMNS][asking.COLUMNS_SAID][asking.ANSWER_RECORD] == ["ref"]
    # The kept reading stands on the next round's blank hand-back.
    written, _kept = _switched_run(tmp_path, ["profile", "lines.csv"], capsys, again)
    assert written["relationships"]["grain"] is None
    for entry in asked["asked"]:
        if entry["column"] == "ref":
            entry["your_answer"] = asking.ANSWER_IDENTIFIER
    written, again = _switched_run(tmp_path, ["profile", "lines.csv"], capsys, asked)
    assert written["relationships"]["grain"] is not None
    assert again[asking.BETWEEN_COLUMNS][asking.COLUMNS_SAID]["person"] == ["ref"]


# -- THE SUBJECT ANSWER BOUND AS EVERY NAMED ANSWER IS (Codex's review, items 3 and 4) --


def _first_row_answered(asked: "dict[str, object]") -> None:
    sections = asked["about_your_file"]
    assert isinstance(sections, list)
    assert asking.FIRST_ROW_SUBJECT in [entry["column"] for entry in sections]
    for entry in sections:
        if entry["column"] == asking.FIRST_ROW_SUBJECT:
            entry["your_answer"] = asking.ANSWER_FIRST_ROW_NAMES


def test_a_subject_answer_beside_a_header_correction_is_refused_never_re_pointed(tmp_path, monkeypatch, capsys):
    # Codex's item 3, its own case at the floor size: the header `column_2,column_1,value` read as a
    # record (its `column_1` repeats below), 1,000 patient keys of 20 rows in the first field. The
    # first-row question answered `names` and the subject question `column_1`, the first field under
    # the reading that wrote the file. MUTANT: the subject answer outside the named-answer checks (it
    # re-points at the second field, whose blank turns the layer off, and the first field's 1,000 real
    # keys are published as levels).
    monkeypatch.chdir(tmp_path)
    draw = random.Random(31)
    lines = ["column_2,column_1,value"]
    for place in range(20000):
        second = "column_1" if place < 11 else ("" if place == 9000 else draw.choice(["a", "b", "c"]))
        lines += [f"P{place % 1000 + 1:05d},{second},{draw.gauss(100, 15):.1f}"]
    fixtures.write(tmp_path, "lines.csv", "\n".join(lines) + "\n")
    assert cli.main(["profile", "lines.csv"], chain=cli.ChainRun(folder=str(tmp_path / "data"))) == 0
    capsys.readouterr()
    asked = json.loads((tmp_path / "lines-questions.json").read_text(encoding="utf-8"))
    _first_row_answered(asked)
    section = asked[asking.BETWEEN_COLUMNS] if asking.BETWEEN_COLUMNS in asked else {}
    section[asking.ROWS_PER_PERSON] = asking.rows_per_person_entry("column_1")
    asked[asking.BETWEEN_COLUMNS] = section
    fixtures.write(tmp_path, "answers.json", json.dumps(asked))
    before = (tmp_path / "lines-profile.json").read_bytes()
    again = cli.ChainRun(folder=str(tmp_path / "data"), replace_description=True)
    assert cli.main(["profile", "lines.csv", "--answers", "answers.json"], chain=again) == 2
    shown = capsys.readouterr()
    assert "column_1" in shown.err and "Nothing was written" in shown.err
    after = (tmp_path / "lines-profile.json").read_bytes()
    assert after == before
    assert not re.search(r"P0[0-9]{4}", after.decode("utf-8"))


def test_a_counted_date_typed_beside_the_named_person_keeps_the_person_and_the_people_floor(tmp_path, monkeypatch, capsys):
    # Codex's item 4, its own case at the floor size: 20,000 rows of 500 patients, `--date-count pid
    # excel-1900` typed in both rounds and the subject question answered `pid`. The answer is the newer
    # statement, as an `identifier` answer is: the column stays the person and the people floor refuses
    # the table. MUTANT: the named column not among the answers that replace a typed declaration (the
    # counted dates erase it, the answer reads `one row each`, a chain is drawn in rows over 500 people).
    monkeypatch.chdir(tmp_path)
    draw = random.Random(41)
    rows = [[f"{40000 + patient}", draw.choice(["F", "M"]), f"{draw.gauss(100, 15):.1f}", draw.choice(["a", "b", "c"])] for patient in range(500) for _visit in range(40)]
    fixtures.write(tmp_path, "lines.csv", _csv(["pid", "gender", "value", "site"], rows))
    typed = ["profile", "lines.csv", "--date-count", "pid", "excel-1900"]
    assert cli.main(typed, chain=cli.ChainRun(folder=str(tmp_path / "data")), small_tables_refused=True) == 0
    capsys.readouterr()
    asked = json.loads((tmp_path / "lines-questions.json").read_text(encoding="utf-8"))
    asked[asking.BETWEEN_COLUMNS][asking.ROWS_PER_PERSON]["your_answer"] = "pid"
    fixtures.write(tmp_path, "answers.json", json.dumps(asked))
    before = (tmp_path / "lines-profile.json").read_bytes()
    again = cli.ChainRun(folder=str(tmp_path / "data"), replace_description=True)
    assert cli.main(typed + ["--answers", "answers.json"], chain=again, small_tables_refused=True) == 1
    shown = capsys.readouterr()
    assert "large tables only" in shown.err + shown.out
    assert (tmp_path / "lines-profile.json").read_bytes() == before


def test_a_subject_answer_naming_a_column_is_never_read_as_one_row_each():
    # Codex's item 4, the second guard. MUTANT: a named answer whose column is no repeating key read as
    # `one row each` (a chain in rows).
    state = cli._ChainState(cli.ChainRun(), None)
    state.rows_answer = "pid"
    state.person_named = "pid"
    assert cli._persons_settled(state, ()) == ()
    assert state.rows_per_person == chain.ROWS_OPEN and state.subject_put and state.rows_answer == ""
    state.rows_answer = asking.ANSWER_ONE_ROW_EACH
    cli._persons_settled(state, ())
    assert state.rows_per_person == chain.ROWS_ONE


# -- ONE ROW EACH (the statistics skeptic's item 7) --


def test_one_row_each_releases_a_column_held_for_another_question(tmp_path):
    # Mutants: the release dropped (the question decides nothing on this answer); the release
    # reaching a key answered `identifier`, or a column the person question still holds.
    draw = random.Random(16)
    rows = [[draw.choice(["F", "M"]), f"{draw.gauss(100, 12):.1f}", draw.choice(["a", "b", "c"]), f"{52000 + draw.randint(0, 40)}"] for _row in range(2000)]
    header = ["gender", "value", "site", "zip"]
    _document, chained = _described(tmp_path / "one", header, rows, persons=(), rows_per_person=chain.ROWS_ONE, held=("zip",))
    assert chained.statistical is not None
    assert {"column": "zip", "reason": "identifier"} in chained.statistical["ineligible"]
    _document, chained = _described(tmp_path / "open", header, rows, persons=(), rows_per_person=chain.ROWS_OPEN, held=("zip",))
    assert chained.statistical is None and any(chain.OFF_SUBJECT in note for note in chained.notes)
    _document, chained = _described(tmp_path / "person", header, rows, persons=(), rows_per_person=chain.ROWS_ONE, held=("zip",), held_by_person=("zip",))
    assert chained.statistical is None and any(chain.OFF_HELD_REPEATS in note for note in chained.notes)
    assert chain.person_question_holds(chained)
    _document, chained = _described(tmp_path / "open2", header, rows, persons=(), rows_per_person=chain.ROWS_OPEN, held=("zip",), held_by_person=("zip",))
    assert chained.statistical is None and chain.person_question_holds(chained)
    _document, chained = _described(tmp_path / "walk", header, rows, persons=(), rows_per_person=chain.ROWS_UNASKED, held=("zip",))
    assert chained.statistical is None and any(chain.OFF_HELD_REPEATS in note for note in chained.notes)


# -- CHANGE OVER VISITS ON A READING OF FEW RUNGS (the statistics skeptic's item 1) --


def test_a_reading_of_rungs_one_grid_step_apart_carries_its_trend_at_the_floor_size(tmp_path):
    # One case at the floor size: the owner adopted this method by name, on this shape.
    # Mutant: `O_free` reading every one-code row as outside a cell (no cell published on ST2).
    import patient_enumeration

    header, rows = patient_enumeration.st2_rows(3000, 1)
    assert len(rows) >= 19000
    document, chained = _described(tmp_path, header, rows, persons=("sid",))
    assert chained.counts["trend_published"] > 0, chained.counts
    assert chained.counts["trend_refused_total"] == 0
    path = fixtures.write_profile(tmp_path, "st2.profile.json", _switched(document, chained))
    contract.load_profile(str(path), chain=True)


def test_the_guard_reads_the_outside_rows_in_their_own_bands():
    # A band of one code holding every outside row pins their total however many rows other bands
    # hold, so the pooled form `min(O, n - n_one)` is too wide. Mutant: the pooled form.
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (2,), (20, 30), (0, 1))
    values = [(1, 1), (8, 8)]
    # Parent cell 0 (one row each): 20 rows, all in the second band; the second band is one code.
    assert patient_rules.free_rows(cells, values, [0, 1], 2, [0, 20, 200, 40], 2, [0, 60]) == 0
    # The same outside rows beside a second band of two or more codes: all free.
    assert patient_rules.free_rows(cells, values, [0, 1], 2, [0, 20, 200, 40], 2, [0, 0]) == 20
    # Half the second band one code: the world holds the outside rows on the others.
    assert patient_rules.free_rows(cells, values, [0, 1], 2, [0, 20, 200, 40], 2, [0, 30]) == 20
    assert patient_rules.free_rows(cells, values, [0, 1], 2, [0, 20, 200, 40], 2, [0, 55]) == 5


def test_the_trend_beside_the_column_s_exact_facts_leaks_no_union_of_types():
    # Item 4 of 4.6c.10, one fixture here; `kpi_run --slow` reads them all. Mutant: SWING or the guard read wider.
    import patient_enumeration

    fixture = [one for one in patient_enumeration.MOMENT_FIXTURES if one[0].startswith("M3")][0]
    found = patient_enumeration.trend_beside_moments(fixture[0], fixture[1], fixture[2], fixture[3], fixture[4], fixture[5][:1], fixture[6][:1], fixture[7])
    assert found["product_passing"] > 0 or found["descriptions"] > 0
    assert found["product_types_leaking"] == 0 and found["pooled_types_leaking"] == 0


def test_a_first_date_band_of_one_to_f_minus_one_patients_takes_a_coarser_level():
    # Mutant: the first date's own floor dropped (a band of 5 patients published at `L0` beside clean residuals).
    frac = patient_rules.fractions.Fraction
    ladder = chain.rules.Ladder("d", (("a",), ("b",), ("c",)), ((0, 1, 2), (0, 0, 1), (0, 0, 1)), (3, 2, 2), (5, 12, 43), (True, True, True))
    first = [0 if patient < 5 else 1 if patient < 17 else 2 for patient in range(30)]
    l0: "list[int]" = []
    readings: "list[object]" = []
    for patient in range(30):
        l0 += [first[patient], 2]
        readings += [frac(patient), frac(1000 + patient)]
    row = types.SimpleNamespace(ladder=ladder, codes=(l0, [ladder.maps[1][one] for one in l0], [ladder.maps[2][one] for one in l0]), readings=readings)
    patients = types.SimpleNamespace(rows=[[2 * patient, 2 * patient + 1] for patient in range(30)])
    level, _first_of, totals = patient_layer._first_date(row, patients, FLOOR)
    assert level == 1 and totals == [17, 13]


def test_the_loader_reads_the_keyed_family_s_level_rule(tmp_path, monkeypatch):
    # Mutant: S31's `L2` rule unread by the loader. A producer told the rule holds everywhere, and drawing
    # `r` first and then a keyed family at its finest child, publishes what the loader must refuse.
    import collections

    draw = random.Random(3)
    rows: "list[list[str]]" = []
    for patient in range(3000):
        arm = draw.choice(["a", "b"])
        age = draw.randint(20, 90)
        base = draw.gauss(100, 12)
        for _visit in range(1 + patient % 2):
            rows += [[f"S{patient:05d}", arm, f"{age}", f"{base + draw.gauss(0, 5):.1f}"]]
    real_rule = patient_layer._keeps_keyed_rule
    real_draw = chain.draw_step
    flat = collections.defaultdict(lambda: types.SimpleNamespace(counts=(1, 1, 1)))

    def fine_keyed_first(search, switch, index, options):
        for at in range(1, len(options)):
            option = options[at]
            scale = search.scales[option.child]
            if patient_rules.R_NAME in option.parents and scale.counts[option.levels[0]] != scale.counts[2]:
                return at
        for at in range(1, len(options)):
            if options[at].child == patient_rules.R_NAME:
                return at
        return real_draw(search, switch, index, options)

    monkeypatch.setattr(patient_layer, "_keeps_keyed_rule", lambda placed, option, derived, r_eligible, scales: real_rule(placed, option, derived, r_eligible, flat))
    monkeypatch.setattr(chain, "draw_step", fine_keyed_first)
    document, chained = _described(tmp_path, ["pid", "arm", "age", "value"], rows)
    monkeypatch.setattr(chain, "draw_step", real_draw)
    monkeypatch.setattr(patient_layer, "_keeps_keyed_rule", real_rule)
    keyed = [family for family in chained.statistical["chain"] if patient_rules.R_NAME in [parent["column"] for parent in family["parents"]] and family["level"] != "L2"]
    assert keyed, chained.statistical["chain"]
    _loaded_or_refused(tmp_path, _switched(document, chained), "rule-off", "L2")


def test_the_chain_s_validation_follows_the_one_row_each_release(tmp_path):
    # Mutant: chain_validation reading a column the chain holds as a person on the table the person said
    # has one row each (every column of the twin's check then unchecked, counted in people).
    from synthtwin import chain_validation

    draw = random.Random(16)
    rows = [[draw.choice(["F", "M"]), f"{draw.gauss(100, 12):.1f}", draw.choice(["a", "b", "c"]), f"{52000 + draw.randint(0, 40)}"] for _row in range(2000)]
    document, chained = _described(tmp_path, ["gender", "value", "site", "zip"], rows, persons=(), rows_per_person=chain.ROWS_ONE, held=("zip",))
    assert chained.statistical is not None
    table = reading.read_table(str(tmp_path / "visits.csv"), small_cell_floor=FLOOR)
    switched = _switched(document, chained)
    assert chain_validation._counted_in_people(table, switched, document) is False
    assert chain_validation._counted_in_people(table, document, document) is True


def test_a_row_family_cell_of_one_to_f_minus_one_rows_has_no_certificate():
    # The producer's own floor on a row family's cell has a second guard, pinned here: PWIT reads
    # s <= |P| floor(s / f), false for 0 < s < f; a floored split puts at least f rows in any band a
    # block of at least f patients uses. Mutant: either certificate taking a band of 1 to f - 1 rows.
    cells = patient_rules.Cells(((patient_rules.R_NAME, 0),), (1,), (22,), (0,))
    for small in range(1, FLOOR):
        assert patient_rules.pwit(22, [small, 44 - small], FLOOR) is False
        found = patient_rules.certificate(cells, [(2, 2)], [[0]], [small, 44 - small], 2, [((2, 22),)], False, None, None, FLOOR, {})
        assert found is False, small


def test_a_row_without_its_person_ends_the_patients_read():
    # The gate's item 2 has a second guard, pinned here: the person column's read of the tabled rows
    # stops at a blank or absent person value. Mutant: a blank person counted as a patient.
    assert patient_layer._patients_of(["P1", "", "P2"], [0, 1, 2]) is None
    assert patient_layer._patients_of(["P1", "NA", "P2"], [0, 1, 2]) is None
    found = patient_layer._patients_of(["P1", "P2", "P1"], [0, 1, 2])
    assert found is not None and found[2] == [[0, 2], [1]]

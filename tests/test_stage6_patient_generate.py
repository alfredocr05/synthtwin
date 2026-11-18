"""The patient layer's generator, behind the chain's switch (lane GRb, plan P4-D465; method G16.13 to G16.17, NOT IN FORCE).

THE GATE OF LANE GRb. A description whose `relationships.grain` stands
(only behind the chain's switch) is made by the patient walk:
`generation.generate_held`'s one call site hands it to
`patient_walk.twin`, which makes the patient table and the row columns
by `generate_held` itself on one stream. This file holds, each rule red
on its mutant (the mutants are named beside each case and run by the
lane's mutation script):

- THE SWITCH OFF: a description without `grain` never reaches the
  patient walk, and `generate_held` with no stream is the function it
  was (the goldens hold the bytes);
- THE PATIENT TWIN MEETS ITS GRAIN, on invented tables behind the
  switch: `r`'s census exact, every patient-fixed column constant inside
  every patient, every row family's table met cell for cell (counted on
  the twin's own patient table), every published `Q_P` in its window,
  every position-like column at its listed positions, every dealt date
  in order inside every patient, every patient's own mean in its band;
- THE PURE RULES (G16.14, G16.15, G16.17): the excess line, the excess
  split's least vector and its tie `(5, 6)` at `q = 11`, the patient
  scores' order, the weight on its grid, the shared module's
  exponential and normal distribution function;
- A WITHHELD MULTIPLICITY MAP is written by G16.13 step 8's even map.

Every fixture is invented here; the key is a fixed test key.
"""

import dataclasses
import fractions
import json
import math
import pathlib
import sys
import typing

import pytest

import fixtures

from synthtwin import chain, contract, generation, patient_rules, patient_walk, profile, reading, taxonomy, twinstore

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))

import kpi_patient_twin  # noqa: E402
import patient_enumeration  # noqa: E402
import patient_twin_tables  # noqa: E402

KEY = bytes(range(32))


def _switched(folder: pathlib.Path, name: str, header: "list[str]", rows: "list[list[str]]", person: str, key: bytes = KEY) -> pathlib.Path:
    """The table described behind the switch with its person column answered, written as a description."""
    path = folder / f"{name}.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(header) + "\n")
        for row in rows:
            handle.write(",".join(row) + "\n")
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=(person,))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [person], [], [], subjects=[person], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, key, rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is not None and chained.statistical is not None and chained.columns is not None
    # G16.17 case 10, the floor gate, on every description this file generates (repair 1 of lane GRb, the first
    # skeptic's item 7): no published patient-level cell and no row family's cell holds 1 to f - 1.
    floored = kpi_patient_twin.floor_cells(chained.statistical, chained.grain, 11)
    assert floored == {"patient_cells_1_to_f_minus_1": 0, "row_cells_1_to_f_minus_1": 0}, floored
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    return fixtures.write_profile(folder, f"{name}-profile.json", switched)


def _made(path: pathlib.Path, seed: int = 7) -> "tuple[contract.Profile, generation.Twin, list[str], list[list[str]]]":
    loaded = contract.load_profile(str(path), chain=True)
    twin = generation.generate_held(loaded, seed)
    names = [column.name for column in loaded.columns]
    held = twin.held_columns if twin.held_columns is not None else ()
    return loaded, twin, names, [twinstore.column_cells(one) for one in held]


@pytest.fixture(scope="module")
def visits(tmp_path_factory) -> pathlib.Path:
    """An invented visit table (1,200 subjects, up to eight visits, a trend on the older half): an own-mean column, a row family and a trend stand."""
    header, rows = patient_enumeration.st2_rows(1200, 1, True)
    return _switched(tmp_path_factory.mktemp("visits"), "st2s", header, rows, "sid")


@pytest.fixture(scope="module")
def encounters(tmp_path_factory) -> pathlib.Path:
    """An invented encounter table (heavy-tailed rows a patient, an open top band, dates dealt)."""
    header, rows = patient_twin_tables.encounter_like(15000, 2)
    return _switched(tmp_path_factory.mktemp("encounters"), "enc-15000-2", header, rows, "pid")


@pytest.fixture(scope="module")
def labs(tmp_path_factory) -> pathlib.Path:
    """An invented laboratory table (a one-decimal result, an arm-by-visit trend, dropout on the previous result)."""
    header, rows = patient_twin_tables.lab_like(12000, 1)
    return _switched(tmp_path_factory.mktemp("labs"), "lab-12000-1", header, rows, "pid")


@pytest.fixture(scope="module")
def visit_twin(visits) -> "tuple[contract.Profile, generation.Twin, list[str], list[list[str]]]":
    """The visit table's twin at seed 7, made once for the cases that read it without damaging the walk."""
    return _made(visits)


@pytest.fixture(scope="module")
def unit_words(tmp_path_factory) -> pathlib.Path:
    """ST2 at 20,000 rows (19,914) with every reading written beside a unit word ('6.6 mmol'): a unit column publishes as
    the same numbers bare (lane UN-1a), so the producer publishes the layer as on plain ST2 (the first skeptic's item 1)."""
    import analyst_tables

    header = list(analyst_tables.ST2_COLUMNS)
    rows = [row[:4] + [row[4] + " mmol"] for row in analyst_tables.st2(20000, 1)]
    return _switched(tmp_path_factory.mktemp("units"), "st2u-20000-1", header, rows, "sid")


@pytest.fixture(scope="module")
def unit_twin(unit_words) -> "tuple[contract.Profile, generation.Twin, list[str], list[list[str]]]":
    """The unit-word table's twin at seed 7, made once."""
    return _made(unit_words)


@pytest.fixture(scope="module")
def first_dates(tmp_path_factory) -> "dict[str, pathlib.Path]":
    """Lane GRa's two floor-size shapes that publish a FIRST-DATE column (tests/test_stage6_patient_profile.py), at its key:
    the two cohorts (20,523 rows; the source date keeps its block) and the staggered starts (20,745 rows; the source held)."""
    import test_stage6_patient_profile as gra

    folder = tmp_path_factory.mktemp("firsts")
    # the names the first skeptic described them under (each name keys the chain's choices): his measured shapes
    header, rows = gra._two_cohorts_and_a_few_late(41)
    cohorts = _switched(folder, "cohorts-0-41", header, rows, "pid", bytes(32))
    header, rows = gra._staggered(4600, 3)
    staggered = _switched(folder, "stagger-4600-3", header, rows, "pid", bytes(32))
    return {"cohorts": cohorts, "staggered": staggered}


# -- THE SWITCH OFF -----------------------------------------------------------------


def test_a_description_without_grain_never_reaches_the_patient_walk(tmp_path, monkeypatch):
    header, rows = patient_enumeration.st2_rows(200, 3, False)
    path = tmp_path / "plain.csv"
    path.write_text(",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    written = fixtures.write_profile(tmp_path, "plain-profile.json", document)

    def refused(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("the patient walk ran on a description without grain")

    monkeypatch.setattr(patient_walk, "twin", refused)
    for chained in (False, True):
        loaded = contract.load_profile(str(written), chain=chained)
        assert loaded.relationships.grain is None
        first = generation.generate(loaded, 11)
        again = generation.generate(loaded, 11)
        assert first.columns == again.columns


# -- THE PATIENT TWIN MEETS ITS GRAIN ------------------------------------------------


def _checked(path: pathlib.Path) -> "dict[str, object]":
    return _checks_of(_made(path))


def _checks_of(made: "tuple[contract.Profile, generation.Twin, list[str], list[list[str]]]") -> "dict[str, object]":
    loaded, twin, names, columns = made
    checks = kpi_patient_twin.grain_checks(loaded, names, columns)
    checks["deviations"] = [(one.column, one.fact) for one in twin.deviations if one.fact.startswith("grain.")]
    return checks


def test_the_visit_twin_meets_its_grain(visit_twin):
    checks = _checks_of(visit_twin)
    assert checks["census_held"] is True
    assert checks["fixed_constant"] == 1.0
    families = checks["row_families"]
    assert isinstance(families, list) and families
    assert all(one["held"] for one in families)
    assert checks["trend_cells"] == checks["trend_met"] and checks["trend_cells"]
    assert checks["position_cells_wrong"] == 0
    assert checks["deviations"] == []


def test_the_encounter_twin_meets_its_grain_with_an_open_top_band(encounters):
    loaded = contract.load_profile(str(encounters), chain=True)
    grain = loaded.relationships.grain
    assert grain is not None and grain.top_patients > 0
    checks = _checked(encounters)
    assert checks["census_held"] is True
    assert checks["fixed_constant"] == 1.0
    families = checks["row_families"]
    assert isinstance(families, list) and families
    assert all(one["held"] for one in families)
    assert checks["patients_dates_out_of_order"] == 0
    assert checks["trend_cells"] == checks["trend_met"]
    assert checks["position_cells_wrong"] == 0


def test_the_lab_twin_carries_its_arm_by_visit_trend(labs):
    loaded, _twin, names, columns = _made(labs)
    checks = kpi_patient_twin.grain_checks(loaded, names, columns)
    assert checks["trend_cells"] == checks["trend_met"] and checks["trend_cells"]
    assert checks["patients_dates_out_of_order"] == 0
    measured = kpi_patient_twin.measured("lab", names, columns)
    real_header, real_rows = patient_twin_tables.lab_like(12000, 1)
    real = kpi_patient_twin.measured("lab", real_header, [[row[k] for row in real_rows] for k in range(len(real_header))])
    twin_slope = measured["slope_diff"]
    real_slope = real["slope_diff"]
    assert isinstance(twin_slope, float) and isinstance(real_slope, float)
    # K-BC-06 clause (2)'s rule: the arm difference of the mean per-patient slope within half of the real.
    assert abs(twin_slope - real_slope) <= 0.5 * abs(real_slope)


def test_the_twin_is_a_function_of_the_description_and_the_seed(visits):
    _loaded, first, _names, first_columns = _made(visits, 5)
    _loaded, again, _names, again_columns = _made(visits, 5)
    assert first_columns == again_columns
    assert first.words_drawn == again.words_drawn
    _loaded, other, _names, other_columns = _made(visits, 6)
    assert other_columns != first_columns


def test_the_person_column_writes_one_stand_in_a_patient_never_a_real_key(visit_twin):
    loaded, _twin, names, columns = visit_twin
    grain = loaded.relationships.grain
    assert grain is not None
    person = columns[names.index(grain.person)]
    real_header, real_rows = patient_enumeration.st2_rows(1200, 1, True)
    real_keys = {row[real_header.index("sid")] for row in real_rows}
    assert len(set(person)) == contract.patient_total(grain)
    assert not set(person) & real_keys


# -- MUTANTS: each rule above fails when its step is damaged -------------------------


def test_rows_dealt_over_the_whole_table_miss_the_row_family(visits, monkeypatch):
    """Mutant: the rows dealt against parent cells that are not their patients' own (G16.17 mutant 2)."""
    real = patient_walk._parent_cells

    def one_cell(patients, parents, entries):
        cells, count = real(patients, parents, entries)
        if any(name == "(own mean of reading)" for name, _level in parents):
            # every patient's parent cell another patient's: the cells' sizes kept, the patients' own cells lost
            return [cells[(k * 7919) % len(cells)] for k in range(len(cells))], count
        return cells, count

    monkeypatch.setattr(patient_walk, "_parent_cells", one_cell)
    checks = _checked(visits)
    families = checks["row_families"]
    assert isinstance(families, list)
    assert not all(one["held"] for one in families)


def test_the_own_mean_close_skipped_misses_the_row_family(visits, monkeypatch):
    """Mutant: step 6 skipped (G16.17 mutant 16): patients' own means outside their bands move rows across parent cells."""
    monkeypatch.setattr(patient_walk, "_own_mean_close", lambda *_args, **_kwargs: patient_walk._MeanClose(0, (), False, 0))
    monkeypatch.setattr(patient_walk, "omega_of", lambda *_args, **_kwargs: 0.0)
    checks = _checked(visits)
    families = checks["row_families"]
    assert isinstance(families, list)
    assert not all(one["held"] for one in families)


def test_the_trend_close_off_misses_a_published_cell(visits, monkeypatch):
    """Mutant: no close (the trend's random and exact exchanges off)."""
    monkeypatch.setattr(patient_walk, "_exact_close", lambda cells, codes, found, patients, rho, total, window: total)
    monkeypatch.setattr(patient_walk, "TREND_PROPOSALS", 0)
    checks = _checked(visits)
    assert checks["trend_met"] < checks["trend_cells"]


def test_dates_left_unsorted_run_out_of_order(encounters, monkeypatch):
    """Mutant: step 5's sort within each patient skipped."""
    monkeypatch.setattr(patient_walk, "_sorted_within", lambda cells, reader, patients: cells)
    checks = _checked(encounters)
    assert checks["patients_dates_out_of_order"] > 0


def test_a_position_list_dealt_misses_its_positions(visits, monkeypatch):
    """Mutant: a position-like column left as the row columns' run wrote it (G16.17 mutant 5)."""
    loaded = contract.load_profile(str(visits), chain=True)
    grain = loaded.relationships.grain
    assert grain is not None and grain.positions
    monkeypatch.setattr(patient_walk, "_write_positions", lambda rows, grain: None)
    checks = _checked(visits)
    assert checks["position_cells_wrong"] > 0


def test_the_top_band_given_its_mean_excess_misses_the_census(monkeypatch):
    """Mutant: the top band's patients each given the mean excess (G16.17 mutant 1): the census's rows missed."""
    values = patient_walk.straight_line(11, 3)
    assert sum(values) == 11 and values == sorted(values, reverse=True)
    assert [11 // 3 for _one in range(3)] != values and sum(11 // 3 for _one in range(3)) != 11


# -- THE PURE RULES ------------------------------------------------------------------


def test_the_excess_line_meets_the_census_exactly():
    for q in range(0, 60):
        for m in range(1, 12):
            line = patient_walk.straight_line(q, m)
            assert sum(line) == q and len(line) == m and min(line) >= 0
            assert line == sorted(line, reverse=True)
            assert line[0] <= 2 * (q // m) + 2


def test_the_excess_split_is_least_and_lexicographically_least():
    # Codex's tie of 2026-10-20 (item 13): two grain cells of 55 top-band patients, q = 11.
    targets = [fractions.Fraction(11 * 55, 110), fractions.Fraction(11 * 55, 110)]
    assert patient_walk.excess_split(targets, 11) == [5, 6]
    # Every split is a least sum of |q_C - t_C| (checked against all splits of small totals).
    import itertools

    for total in range(0, 9):
        for first in range(0, 5):
            for second in range(0, 5):
                targets = [fractions.Fraction(first, 2), fractions.Fraction(second, 3), fractions.Fraction(1, 1)]
                found = patient_walk.excess_split(targets, total)
                assert sum(found) == total
                cost = sum(abs(q - t) for q, t in zip(found, targets))
                best = min(
                    (sum(abs(q - t) for q, t in zip(split, targets)), split)
                    for split in itertools.product(range(total + 1), repeat=3)
                    if sum(split) == total
                )
                assert cost == best[0]
                least = min(split for split in itertools.product(range(total + 1), repeat=3) if sum(split) == total and sum(abs(q - t) for q, t in zip(split, targets)) == best[0])
                assert tuple(found) == least


def test_the_patient_scores_rise_with_the_band_and_are_normal_order_statistics():
    sums = [393210 + 1000 * ((7 * k) % 13 - 6) for k in range(40)]
    places = [(11 * k) % 17 for k in range(40)]
    bands = [k % 4 for k in range(40)]
    scores = patient_walk.patient_scores(sums, places, bands)
    by_band = [[scores[k] for k in range(40) if bands[k] == band] for band in range(4)]
    for band in range(3):
        assert max(by_band[band]) <= min(by_band[band + 1])
    assert sorted(scores) == sorted(patient_walk.chain_walk.hidden_score(one) for one in sums)


def test_the_weight_is_on_its_grid_and_rises_with_the_table_s_dependence():
    flat = [[500, 500], [500, 500]]
    steep = [[900, 100], [100, 900]]
    assert patient_walk.omega_of(flat, [100, 100]) == 0.0
    omega = patient_walk.omega_of(steep, [100, 100])
    assert 0.5 < omega < 1.0
    assert abs(omega / patient_walk.OMEGA_STEP - round(omega / patient_walk.OMEGA_STEP)) < 1e-9


def test_the_shared_module_s_exponential_and_normal_distribution_function():
    for k in range(-400, 400):
        x = k / 37.0
        assert abs(patient_walk.chain_walk.exponential(x) - math.exp(x)) <= 4e-16 * math.exp(x)
    for k in range(-80, 81):
        z = k / 10.0
        assert abs(patient_walk.chain_walk.normal_cdf(z) - 0.5 * math.erfc(-z / math.sqrt(2.0))) < 2e-15


def test_a_withheld_multiplicity_map_takes_the_even_map():
    block = contract.ColumnBlock(
        name="code", position=1, role=contract.ROLE_IDENTIFIER, statistical_type="code", quality_state="ok",
        structural_role="identifier", n_present=10, n_missing=0, missing_by_class=contract.MissingByClass(0, 0, 0, 0, 0, 0),
        missing_by_source={}, n_missing_blank=0, n_missing_withheld=0, n_distinct=4, n_distinct_folded=4, n_numeric=10,
        n_not_numeric=0, n_out_of_range=0, n_contradictory=0, n_sentinel_candidates_unpublished=0, sentinel_verdicts=(),
        detection_evidence="", remarks=(),
        facts=contract.IdentifierFacts(min_length=2, max_length=2, all_whole_numbers=True, n_all_digits=10, n_code_alphabet=10, n_distinct_by_occurrences={}, layout_forms={}, layout_prefixes={}),
    )
    even = patient_walk.with_even_map(block)
    assert isinstance(even.facts, contract.IdentifierFacts)
    assert even.facts.n_distinct_by_occurrences == {"2": 2, "3": 2}
    assert sum(int(times) * count for times, count in even.facts.n_distinct_by_occurrences.items()) == 10
    assert patient_walk.with_even_map(even) is even


def test_the_census_constant_reads_one_value(visits):
    loaded = contract.load_profile(str(visits), chain=True)
    grain = loaded.relationships.grain
    assert grain is not None
    assert contract.patient_total(grain) == sum(grain.bands) + grain.top_patients
    assert contract.class_in(grain, grain.person) == patient_rules.CLASS_PERSON


# -- V12.7 AND V12.9: the validator's patient lines on the twin and on its mutants ---------


def _lines_of(document: dict, names: "list[str]", columns: "list[list[str]]", folder: pathlib.Path):
    from synthtwin import chain_validation

    out = folder / "checked.csv"
    with open(out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(",".join(names) + "\n")
        for row in range(len(columns[0])):
            handle.write(",".join(column[row] for column in columns) + "\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(out), small_cell_floor=11)
    redescribed = profile.build_document(table, settings, [], [], [])
    return chain_validation.lines_of(document, table, redescribed, settings, [], [], [], tuple("" for _name in names))


def _verdicts(lines) -> "dict[str, str]":
    out = {f"total {one.column}": one.verdict for one in lines.totals}
    out.update({f"family {one.index} {one.child}": one.verdict for one in lines.families})
    out.update({f"{one.kind} {one.subject}": one.verdict for one in lines.patient})
    return out


def test_every_patient_line_holds_on_the_twin_and_each_mutant_misses_its_own(visits, visit_twin, tmp_path):
    """V12.7's lines HELD on the undamaged twin; V12.9's mutants 7, 8, 9, 10 and 12, each MISSED on its own line."""
    document = json.loads(visits.read_text(encoding="utf-8"))
    loaded, _twin, names, columns = visit_twin
    grain = loaded.relationships.grain
    assert grain is not None
    green = _verdicts(_lines_of(document, names, columns, tmp_path))
    assert green and all(verdict == "HELD" for verdict in green.values())
    person = names.index(grain.person)
    reading_at = names.index("reading")
    by: "dict[str, list[int]]" = {}
    for row, key in enumerate(columns[person]):
        by.setdefault(key, []).append(row)
    keys = list(by)
    # 7: one patient's rows split between two new person values: the census line MISSED.
    damaged = [list(column) for column in columns]
    eight = next(key for key in keys if len(by[key]) == 8)
    for at, row in enumerate(by[eight]):
        damaged[person][row] = "split-a" if at < 4 else "split-b"
    assert _verdicts(_lines_of(document, names, damaged, tmp_path))["total (rows per patient)"] == "MISSED"
    # 9: the readings of every patient of the trend's cell reversed in position: that cell's Q_P MISSED.
    damaged = [list(column) for column in columns]
    for key in keys:
        rows = by[key]
        if len(rows) == 8:
            values = [damaged[reading_at][row] for row in rows]
            for row, value in zip(rows, reversed(values)):
                damaged[reading_at][row] = value
    trend = {key: verdict for key, verdict in _verdicts(_lines_of(document, names, damaged, tmp_path)).items() if key.startswith("trend")}
    assert trend and any(verdict == "MISSED" for verdict in trend.values())
    # 10: the position-like column shifted by one position in every patient: its list MISSED.
    damaged = [list(column) for column in columns]
    visit = names.index("visit")
    for key in keys:
        rows = by[key]
        values = [damaged[visit][row] for row in rows]
        for at, row in enumerate(rows):
            damaged[visit][row] = values[(at + 1) % len(values)]
    assert _verdicts(_lines_of(document, names, damaged, tmp_path))["positions visit"] == "MISSED"
    # 12: a patient-fixed column's values exchanged on every row between 11 patients of one own-mean band and 11 of the other.
    damaged = [list(column) for column in columns]
    arm = names.index("arm")
    ones = [key for key in keys if damaged[arm][by[key][0]] == "1"]
    noughts = [key for key in keys if damaged[arm][by[key][0]] == "0"]

    def own_band(key: str) -> int:
        values = [fractions.Fraction(columns[reading_at][row]) for row in by[key]]
        mean = sum(values) / len(values)
        return len([edge for edge in grain.derived[0].edges if fractions.Fraction(edge) <= mean])

    high_ones = [key for key in ones if own_band(key) == 1][:11]
    low_noughts = [key for key in noughts if own_band(key) == 0][:11]
    for key in high_ones:
        for row in by[key]:
            damaged[arm][row] = "0"
    for key in low_noughts:
        for row in by[key]:
            damaged[arm][row] = "1"
    verdicts = _verdicts(_lines_of(document, names, damaged, tmp_path))
    assert verdicts["total arm"] == "HELD"
    crossed = any(family.parents and any(name == "arm" for name, _level in list(family.parents) + [(family.child, family.level)]) for family in grain.patient_chain)
    if crossed:
        assert any(key.startswith("family") and verdict == "MISSED" for key, verdict in verdicts.items())
    else:
        # this description's patient chain holds the column in no family with another member: no table moves
        assert all(verdict == "HELD" for verdict in verdicts.values())
    # 8: one repeated column's cells exchanged between rows of two patients in different parent cells and bands.
    # Two patients of eight rows whose own means stand a whole unit off the edge, so neither leaves its band: a reading just
    # below the edge and one just above exchanged between them moves a row of each across the child's middle cut.
    damaged = [list(column) for column in columns]
    edge = fractions.Fraction(grain.derived[0].edges[0])

    def mean_of(key: str) -> fractions.Fraction:
        values = [fractions.Fraction(columns[reading_at][row]) for row in by[key]]
        return sum(values) / len(values)

    far_low = [key for key in keys if len(by[key]) == 8 and mean_of(key) < edge - 1]
    far_high = [key for key in keys if len(by[key]) == 8 and mean_of(key) > edge + 1]
    low_row = next(row for key in far_low for row in by[key] if edge - 1 < fractions.Fraction(columns[reading_at][row]) < edge - fractions.Fraction(3, 10))
    high_row = next(row for key in far_high for row in by[key] if edge + fractions.Fraction(3, 10) < fractions.Fraction(columns[reading_at][row]) < edge + 1)
    damaged[reading_at][low_row], damaged[reading_at][high_row] = damaged[reading_at][high_row], damaged[reading_at][low_row]
    verdicts = _verdicts(_lines_of(document, names, damaged, tmp_path))
    assert any(key.startswith("family") and key.endswith("reading") and verdict == "MISSED" for key, verdict in verdicts.items())


# -- CARRIED ITEM (c): a source column named as the layer names its own columns ------------


def test_a_column_named_like_the_layer_s_own_labels_turns_the_layer_off_and_the_loader_refuses_it(tmp_path, visits):
    """Codex's case (20,000 rows, 8,000 patients, columns pid, (rows per patient) and value): no IndexError, no doubled name, the layer
    off with its note; and a switched description whose grain stands beside such a column is refused (S29)."""
    import random

    draw = random.Random(10)
    rows: "list[list[str]]" = []
    for patient in range(8000):
        for _visit in range(2 if patient % 2 else 3):
            if len(rows) < 20000:
                rows += [[f"Q{patient:05d}", f"{draw.randint(1, 5)}", f"{draw.gauss(50, 9):.1f}"]]
    header = ["pid", patient_rules.R_NAME, "value"]
    path = tmp_path / "names.csv"
    path.write_text(",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch("names", KEY, rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is None
    assert patient_rules.internal_name(patient_rules.R_NAME) and patient_rules.internal_name("(own mean of value)")
    assert not patient_rules.internal_name("value") and not patient_rules.internal_name("(own mean")
    switched = json.loads(visits.read_text(encoding="utf-8"))
    for block in switched["columns"]:
        if block["name"] == "age":
            block["name"] = "(first date of age)"
    for entry in switched["relationships"]["grain"]["classes"]:
        if entry["column"] == "age":
            entry["column"] = "(first date of age)"
    written = fixtures.write_profile(tmp_path, "renamed-profile.json", switched)
    with pytest.raises(Exception) as refused:
        contract.load_profile(str(written), chain=True)
    assert "S29" in f"{refused.value}" or "patient layer" in f"{refused.value}"


# -- REPAIR 1 OF LANE GRb: the reviews' items, each red on its mutant ----------------------


def _close_state(values: "list[int]", lows: "list[int]", highs: "list[int]") -> "patient_walk._CloseState":
    """The own-mean close's state over one parent cell of one-row patients: each row its patient's sum."""
    pool = sorted(range(len(values)), key=lambda row: (values[row], row))
    slot = {row: at for at, row in enumerate(pool)}
    return patient_walk._CloseState(list(values), list(lows), list(highs), list(values), slot, pool, [values[row] for row in pool],
                                    list(range(len(values))), 0, patient_walk.CLOSE_VISITS, patient_walk.CLOSE_WORK * len(values), 0)


def test_a_falling_patient_takes_the_nearest_reading_that_brings_it_into_its_band():
    """The statistics check's item 1 (LANE GRb RULINGS 3 (2)): patient 0 holds 10 above its band [0, 7] beside a near
    reading (7) and a far-low one (1); its exchange moves its sum by exactly `need` (3), to the band's near edge. MUTANT,
    the build head: the falling branch scanned upward from `v - room` and took the far reading (sum 1). The rising
    patient's mirror beside it."""
    far = 1 << 62
    falling = _close_state([10, 7, 1], [0, -far, -far], [7, far, far])
    assert patient_walk._one_exchange(0, falling, [(-10, 0)]) == (0, 1)
    assert falling.sums[0] == 7 and falling.sums[1] == 10 and falling.sums[2] == 1
    rising = _close_state([0, 3, 9], [3, -far, -far], [10, far, far])
    assert patient_walk._one_exchange(0, rising, [(0, 0)]) == (0, 1)
    assert rising.sums[0] == 3


# -- REPAIR 2 OF LANE GRb: Codex's review (LANE GRb RULINGS 5), each red on its mutant ---------------


def _closed(groups: "list[list[int]]", scale: int, edges: "list[fractions.Fraction]", bands: "list[int]") -> "tuple[patient_walk._MeanClose, list[int]]":
    """`mean_close` over one parent cell, each group one patient's readings in whole numbers of the finest step; and each patient's band after it."""
    values: "list[int | None]" = [value for group in groups for value in group]
    owner = [p for p, group in enumerate(groups) for _value in group]
    starts: "list[int]" = []
    for group in groups:
        starts += [sum(len(one) for one in groups[:len(starts)])]
    patients = patient_walk._Patients(len(groups), {}, {}, [len(group) for group in groups], starts)
    done = patient_walk.mean_close(list(values), scale, edges, bands, owner, patients, [0 for _group in groups])
    after = list(values)
    for row, other in done.exchanges:
        after[row], after[other] = after[other], after[row]
    ended: "list[int]" = []
    for p in range(len(groups)):
        mine = [fractions.Fraction(one if one is not None else 0, scale) for one in after[starts[p]:starts[p] + len(groups[p])]]
        mean = sum(mine, fractions.Fraction(0)) / len(mine)
        ended += [len([edge for edge in edges if edge <= mean])]
    return done, ended


def test_a_published_number_written_as_a_fraction_is_read_as_one():
    """Codex's item 2 at table level (the combined verify of repair 1: ST2 at 19,914 rows written at full binary64 precision, one
    reading in a hundred a ten-thousandth of itself): an own mean's edge and a grid's step and low end with no finite decimal are
    published as `p/q` (`patient_rules.decimal_text`), and the readers of V12.7 and of the walk's trend close read them as
    nothing, so V12.7 read every own mean below the edge (1,509 of 3,000 patients' bands differing) and every grid code 0.
    A GENERATED round trip over 6,000 fractions, finite decimals and not, negative, whole, of up to 40 figures: each is read
    back exactly as written, an own mean's band read against it is the exact comparison's, and a grid code read on its texts
    is the exact one (away from a half step). MUTANT, the repair-1 head: `decimal_fraction` refused the `/`."""
    import random

    draw = random.Random(4653)
    for _case in range(6000):
        denominator = draw.choice([1, 2, 5, 10, 3, 7, 13, 273, 4095, 10 ** draw.randint(0, 20), draw.randint(1, 10 ** draw.randint(1, 20))])
        value = fractions.Fraction(draw.randint(-10 ** draw.randint(0, 20), 10 ** draw.randint(0, 20)), denominator)
        text = patient_rules.decimal_text(value)
        assert patient_rules.decimal_fraction(text) == value, text
        mean = value + fractions.Fraction(draw.randint(-3, 3), draw.randint(1, 7))
        assert patient_rules.own_mean_band([mean], [text]) == (1 if value <= mean else 0), (text, mean)
        step = abs(value) + fractions.Fraction(1, draw.randint(1, 4095))
        low = fractions.Fraction(draw.randint(-1000, 1000), draw.randint(1, 999))
        reading = low + step * (fractions.Fraction(draw.randint(0, 4000)) + fractions.Fraction(draw.randint(-49, 49), 100))
        exact = patient_rules.grid_code(patient_rules.Grid("x", step, low, 4095), reading)
        assert patient_rules.grid_code_of(patient_rules.decimal_text(step), patient_rules.decimal_text(low), 4095, reading) == exact, (step, low, reading)


def test_an_open_band_holds_every_sum_at_every_finest_step():
    """Codex's item 2 (LANE GRb RULINGS 5 (2)): readings 1, 2, 0.00012345678901234567 and 0 make the finest step `10 ** -20`;
    patient A (1, 2) dealt the band below the edge 1 and B (0.00012345678901234567, 0) the band from it are both inside
    after the close. And a GENERATED check over the finest steps `10 ** 0` to `10 ** -30`: patients already inside a band
    with an open end stay there untouched, and two patients one exchange closes are closed. MUTANT, the repair-1 head: the
    open ends held at `2 ** 62`, so from `10 ** -19` on a band from the edge read empty and both patients stayed outside."""
    import random

    tiny = fractions.Fraction("0.00012345678901234567")
    scale = tiny.denominator
    assert scale == 10 ** 20
    done, ended = _closed([[scale, 2 * scale], [tiny.numerator, 0]], scale, [fractions.Fraction(1)], [0, 1])
    assert done.left == 0 and ended == [0, 1], (done, ended)
    draw = random.Random(4652)
    for power in range(31):
        scale = 10 ** power
        for _trial in range(8):
            edge = fractions.Fraction(draw.randint(1, 9), 1)
            groups = [[draw.randint(0, 9 * scale) for _row in range(draw.randint(1, 4))] for _p in range(6)]
            bands = [1 if fractions.Fraction(sum(group), len(group) * scale) >= edge else 0 for group in groups]
            done, ended = _closed(groups, scale, [edge], bands)
            assert done.left == 0 and done.exchanges == () and ended == bands, (power, groups, bands)
            small = draw.randint(1, max(1, scale // 10 ** 4))
            done, ended = _closed([[edge.numerator * scale, 2 * edge.numerator * scale], [small, 0]], scale, [edge], [0, 1])
            assert done.left == 0 and ended == [0, 1], (power, small)


def test_the_own_mean_close_s_work_stays_within_its_bound_and_grows_linearly(monkeypatch):
    """Codex's item 3 (LANE GRb RULINGS 5 (3)): two patients of `n` rows holding `j 10 n` and `j 10 n + 1` (`j < n`), both dealt
    the band `[M + 0.5, M + 0.501)` of `M = 10 n (n - 1) / 2`, need `n / 2` exchanges of one step each. At `n` = 100 to 1,600 the
    close's row reads stay within its total-work bound and grow linearly where the bound binds (within 10 per cent at each
    doubling); a close the bound stops says so and leaves the patients outside, to be named in the deviations. MUTANT, the
    repair-1 head: every proposal sorted and visited all of its patient's rows, `n ** 2 / 2` visits (quadratic).

    THE SORTING IT DOES (the scoped verify of repair 2, its item 1; LANE GRb RULINGS 6 (2) (a)): the items handed to `sorted`
    while `mean_close` runs (the module's own `sorted`, counted) are at most `CLOSE_PASSES * 2 * len(values)`, a pass sorting
    the parent cell's rows once and each proposing patient's own rows once; the head hands exactly that bound at `n` = 400 to
    1,600 (6,400, 12,800 and 25,600 items). MUTANT, the verify's 're-sorted after every exchange' (Codex's item 3 put back
    beside the bound): 57,600, 115,200 and 230,400 items there."""
    handed = [0]

    def counted(items, *rest, **named):  # type: ignore[no-untyped-def]
        out = sorted(items, *rest, **named)
        handed[0] += len(out)
        return out

    monkeypatch.setattr(patient_walk, "sorted", counted, raising=False)
    reads: "dict[int, int]" = {}
    for n in (100, 200, 400, 800, 1600):
        middle = fractions.Fraction(10 * n * (n - 1), 2)
        edges = [middle + fractions.Fraction(1, 2), middle + fractions.Fraction(501, 1000)]
        handed[0] = 0
        done, ended = _closed([[j * 10 * n for j in range(n)], [j * 10 * n + 1 for j in range(n)]], 1, edges, [1, 1])
        bound = patient_walk.CLOSE_PASSES * patient_walk.CLOSE_VISITS * 2 * n * (1 + 2 * patient_walk.CLOSE_PARTNERS)
        assert done.reads <= min(bound, patient_walk.CLOSE_WORK * 2 * n + 2 * patient_walk.CLOSE_PARTNERS + 1), (n, done.reads)
        assert 0 < handed[0] <= patient_walk.CLOSE_PASSES * 2 * (2 * n), (n, handed[0], "items handed to sorted inside mean_close")
        if done.left:
            assert done.bounded and ended != [1, 1]
        else:
            assert ended == [1, 1]
        reads[n] = done.reads
    assert reads[1600] <= 2.2 * reads[800] and reads[800] <= 2.2 * reads[400], reads


class _Counted(list):  # type: ignore[type-arg]
    """A holder list whose reads are counted (the trend close's work)."""

    reads = 0

    def __getitem__(self, at):  # type: ignore[no-untyped-def]
        _Counted.reads += 1
        return list.__getitem__(self, at)

    def __iter__(self):  # type: ignore[no-untyped-def]
        for one in list.__iter__(self):
            _Counted.reads += 1
            yield one


class _CountedMap(dict):  # type: ignore[type-arg]
    """A holder map whose reads are counted (the build's holders)."""

    def __iter__(self):  # type: ignore[no-untyped-def]
        for one in dict.__iter__(self):
            _Counted.reads += 1
            yield one


def test_the_trend_close_reads_the_least_holders_never_a_holder_set_whole(monkeypatch):
    """Codex's item 4 (LANE GRb RULINGS 5 (3)): `N` three-row patients each holding codes `(0, 0, 1)` in one cell, `S_P = 2 N`,
    window `[0, 0]`: the exact close moves one patient a round by the largest step that fits; the holder entries it reads at
    `N` = 1,000, 2,000 and 4,000 grow linearly (each step's patients kept ascending, its least two read), and the cell is met.
    MUTANT, the repair-1 head: the least holder found by `min` over every remaining patient (quadratic)."""
    real = patient_walk._hold

    def counted(holders, held, p):  # type: ignore[no-untyped-def]
        real(holders, held, p)
        for step in held:
            if step in holders and type(holders[step]) is list:
                holders[step] = _Counted(holders[step])
            elif step in holders and type(holders[step]) is dict:
                holders[step] = _CountedMap(holders[step])
            elif step in holders and type(getattr(holders[step], "heap", None)) is list:
                # Batch 4u's outside review, item 5: each step's patients in a heap (`_Holding`), its reads counted.
                holders[step].heap = _Counted(holders[step].heap)

    monkeypatch.setattr(patient_walk, "_hold", counted)
    reads: "dict[int, int]" = {}
    for count in (1000, 2000, 4000):
        codes = [0, 0, 1] * count
        cells = [f"{code}" for code in codes]
        patients = patient_walk._Patients(count, {}, {}, [3] * count, [3 * p for p in range(count)])
        _Counted.reads = 0
        total = patient_walk._exact_close(cells, codes, list(range(count)), patients, 3, 2 * count, (0, 0))
        assert total == 0
        reads[count] = _Counted.reads
    assert reads[4000] <= 2.5 * reads[2000] and reads[2000] <= 2.5 * reads[1000], reads


def test_a_bounded_search_may_miss_a_repair_that_exists():
    """Codex's item 8 (LANE GRb RULINGS 5 (4)): patient 0 holds (0) in the band from 0.5, 256 patients hold (1) in it, and the last
    holds (1, 0, 0) in the band below it. The close reads 256 partner rows a proposal, all of them the 256 patients that
    cannot give their 1, so patient 0 stays outside; yet the last patient's 1 exchanged for patient 0's 0 puts both inside.
    So the twin's note says the bounded search did not find a repair, never that none exists (the note's case:
    `test_a_derived_miss_names_the_row_family_it_moves`)."""
    groups = [[0]] + [[1] for _p in range(256)] + [[1, 0, 0]]
    bands = [1] + [1] * 256 + [0]
    done, ended = _closed(groups, 1, [fractions.Fraction(1, 2)], bands)
    assert done.left == 1 and ended[0] == 0 and ended[1:] == bands[1:]
    repaired = [list(group) for group in groups]
    repaired[0][0], repaired[-1][0] = repaired[-1][0], repaired[0][0]
    means = [fractions.Fraction(sum(group), len(group)) for group in repaired]
    assert [1 if mean >= fractions.Fraction(1, 2) else 0 for mean in means] == bands


def _spelled_columns(draw: "typing.Any", rows: int) -> "tuple[list[str], list[list[str]]]":
    """Four FINE number columns of generated spellings: a unit word, a unit letter, a leading plus on every other cell,
    and a decimal comma beside a point as the thousands mark (declared)."""
    header = ["unit_word", "unit_letter", "plus_sign", "comma_mark"]
    out: "list[list[str]]" = []
    for _row in range(rows):
        places = draw.choice([0, 1, 2])
        value = draw.uniform(2.0, 40.0)
        big = draw.uniform(100.0, 99999.0)
        whole = int(big)
        tenths = draw.randint(0, 99)
        grouped = f"{whole:,}".replace(",", ".")
        out += [[
            f"{value:.{places}f} mmol",
            f"{value:.{places}f}g",
            ("+" if draw.random() < 0.5 else "") + f"{value:.{places}f}",
            f"{grouped},{tenths:02d}",
        ]]
    return header, out


def test_the_walk_reads_every_number_spelling_as_the_profiler_does(tmp_path):
    """The first skeptic's item 1, its class closed by a generated check (the stopping rule): on every spelling the
    profiler reads as a number in a FINE column -- a unit word, a unit letter, a leading plus, a declared decimal comma
    beside a thousands mark -- the walk's exact reading (`patient_walk.exact_meaning`, what the own-mean and trend closes
    read) equals the profiler's (`chain.reading_of` with `patient_rules.reading_of`, what the producer and the
    validator read), and a spelling it reads as no number the walk reads as none. MUTANT, the build head's reader: the
    character filter (`patient_rules.decimal_fraction` of the stripped text), which reads no number in '6.6 mmol'."""
    import csv
    import random

    header, rows = _spelled_columns(random.Random(465), 3000)
    path = tmp_path / "spellings.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [], ["comma_mark"])
    loaded = contract.load_profile(str(fixtures.write_profile(tmp_path, "spellings-profile.json", document)))
    blocks = {f"{block['name']}": block for block in document["columns"]}
    compared = 0
    for at, name in enumerate(header):
        values = reading.column_values(table, at)
        block = blocks[name]
        declared = {"code": False, "measurement": False, "decimal_comma": name == "comma_mark"}
        meaning = chain.reading_of(block, values, settings, declared, "")
        walk = patient_walk.exact_meaning(loaded, loaded.columns[at], values)
        role = f"{block['role']}"
        numbers = 0
        filtered_misses = 0
        for text in set(values):
            kind, value = meaning[text] if text in meaning else ("missing", None)
            expected = patient_rules.reading_of(role, value, block) if kind == "value" else None
            assert walk[text] == expected, (name, text, walk[text], expected)
            if expected is not None:
                numbers += 1
                cleaned = text.strip().replace(",", ".") if name == "comma_mark" else text.strip()
                filtered_misses += 1 if patient_rules.decimal_fraction(cleaned) != expected else 0
        assert numbers >= 1000, (name, role, numbers)
        compared += numbers
        if name in ("unit_word", "unit_letter"):
            assert filtered_misses == numbers, (name, filtered_misses)
        if name == "comma_mark":
            assert filtered_misses >= numbers // 2, (name, filtered_misses)
    assert compared >= 4000


def test_a_twin_with_unit_words_holds_every_patient_line(unit_words, unit_twin, tmp_path):
    """The first skeptic's item 1 at 20,000 rows: on ST2 with every reading beside a unit word, the walk's twin holds every
    V12.7 line (the own mean's patients, every family, every Q_P) and its closes leave no deviation. MUTANT, the build
    head: the closes read no number in '6.6 mmol', so all seven Q_P and the own mean's totals MISSED."""
    document = json.loads(unit_words.read_text(encoding="utf-8"))
    loaded, twin, names, columns = unit_twin
    grain = loaded.relationships.grain
    assert grain is not None and grain.trend and any(one.kind == patient_rules.OWN_MEAN for one in grain.derived)
    verdicts = _verdicts(_lines_of(document, names, columns, tmp_path))
    assert any(key.startswith("trend") for key in verdicts)
    assert verdicts and all(verdict == "HELD" for verdict in verdicts.values()), {key: one for key, one in verdicts.items() if one != "HELD"}
    assert [one.fact for one in twin.deviations if one.fact.startswith("grain.")] == []
    checks = kpi_patient_twin.grain_checks(loaded, names, columns)
    assert checks["trend_cells"] == checks["trend_met"] and checks["trend_cells"]
    assert all(one["held"] for one in checks["row_families"])


def _patients_by(person: "list[str]") -> "dict[str, list[int]]":
    by: "dict[str, list[int]]" = {}
    for row, key in enumerate(person):
        by[key] = by[key] + [row] if key in by else [row]
    return by


def test_a_derived_column_s_own_totals_never_close_its_families(visits, visit_twin, tmp_path):
    """The first skeptic's item 2 (V12.7: the gate reads the L0 totals of the file's own columns and of `r`, never a derived
    column's): one exchange of readings moves ONE patient's own mean across an edge, its partner's staying in its band;
    the own mean's total line reads MISSED and so does its family of the patient chain, judged, never "not judged".
    MUTANT, the build head: the derived total in the gate, so the family read WITHHELD."""
    document = json.loads(visits.read_text(encoding="utf-8"))
    loaded, _twin, names, columns = visit_twin
    grain = loaded.relationships.grain
    assert grain is not None
    own = [one for one in grain.derived if one.kind == patient_rules.OWN_MEAN][0]
    edges = [fractions.Fraction(edge) for edge in own.edges]
    at = names.index(own.source)
    by = _patients_by(columns[names.index(grain.person)])

    def band(values: "list[fractions.Fraction]") -> int:
        mean = sum(values, fractions.Fraction(0)) / len(values)
        return len([edge for edge in edges if edge <= mean])

    readings = {key: [fractions.Fraction(columns[at][row]) for row in rows] for key, rows in by.items()}
    bands = {key: band(values) for key, values in readings.items()}
    found = None
    lows = sorted((key for key in by if bands[key] == 0), key=lambda key: edges[0] - sum(readings[key]) / len(readings[key]))[:200]
    highs = [key for key in by if bands[key] == 1]
    for p in lows:
        low_row = min(by[p], key=lambda row: fractions.Fraction(columns[at][row]))
        for q in highs:
            high_row = max(by[q], key=lambda row: fractions.Fraction(columns[at][row]))
            moved_p = [fractions.Fraction(columns[at][high_row]) if row == low_row else fractions.Fraction(columns[at][row]) for row in by[p]]
            moved_q = [fractions.Fraction(columns[at][low_row]) if row == high_row else fractions.Fraction(columns[at][row]) for row in by[q]]
            if band(moved_p) == 1 and band(moved_q) == 1:
                found = (low_row, high_row)
                break
        if found:
            break
    assert found is not None
    damaged = [list(column) for column in columns]
    damaged[at][found[0]], damaged[at][found[1]] = damaged[at][found[1]], damaged[at][found[0]]
    verdicts = _verdicts(_lines_of(document, names, damaged, tmp_path))
    assert verdicts[f"total {own.name}"] == "MISSED"
    family = [key for key in verdicts if key.startswith("family") and key.endswith(own.name)]
    assert family and all(verdicts[key] == "MISSED" for key in family), {key: verdicts[key] for key in family}
    # ...and in the ROW-FAMILY loop too (the verify of repair 1, item 10: removing the derived exclusion there left every
    # case green): each row family the own mean parents reads MISSED, judged, never "not judged".
    chain_count = len(document["relationships"]["statistical"]["chain"])
    row_keys = [f"family {chain_count + at} {one.child}" for at, one in enumerate(grain.rows) if any(name == own.name for name, _level in one.parents)]
    assert row_keys and all(verdicts[key] == "MISSED" for key in row_keys), {key: verdicts.get(key) for key in row_keys}
    assert verdicts["total (rows per patient)"] == "HELD"


def test_the_twin_s_report_counts_its_finished_cells_and_tells_patients_from_rows(visit_twin):
    """Codex's item 5 (LANE GRb RULINGS 5 (4)): on the 1,200-patient, 7,898-row visit table every column's report counts the
    finished cells (here every cell filled: `sid`, `arm` and `visit` 7,898 present), and a column the description counts in
    patients says so beside its row counts (`sid` and `arm`: 1,200 of the twin's 1,200 patients), as the position-like
    column says it was written from its list. MUTANT, the repair-1 head: the runs' outcomes kept, `sid` and `arm` 1,200
    present and `visit` 0 present with every cell missing."""
    loaded, twin, names, columns = visit_twin
    grain = loaded.relationships.grain
    assert grain is not None
    for outcome in twin.outcomes:
        cells = columns[names.index(outcome.name)]
        filled = [cell for cell in cells if cell != ""]
        assert (outcome.n_present, outcome.n_missing, outcome.n_distinct) == (len(filled), len(cells) - len(filled), len(set(filled))), outcome
    by = {outcome.name: outcome for outcome in twin.outcomes}
    assert by["visit"].n_present == by["sid"].n_present == by["arm"].n_present == len(columns[0]) == 7898
    for name in (grain.person, "arm"):
        said = [one for one in by[name].remarks if one.subject.startswith("the twin's patients")]
        assert said and said[0].held.startswith("1200 of the twin's 1200 patients hold a value"), by[name].remarks
        assert said[0] in twin.remarks
    assert any(one.subject.startswith("the rows of this position-like column") for one in by["visit"].remarks)


def _workbook_of(path: pathlib.Path, header: "list[str]", records: "list[list[str] | None]") -> pathlib.Path:
    """A workbook of one sheet built by the tests' own writer (`workbooks`): the header, then each record, a None record an empty one
    (its row left out, so the reader counts it inside the table); a number written as a number, other text inline, "" a blank cell."""
    import workbooks

    letters = "ABCDEFGHIJ"
    body: "list[tuple[int, list[str]]]" = [(1, [workbooks.cell(f"{letters[at]}1", name, "inlineStr") for at, name in enumerate(header)])]
    number = 1
    for record in records:
        number += 1
        if record is None:
            continue
        cells: "list[str]" = []
        for at, value in enumerate(record):
            spot = f"{letters[at]}{number}"
            numeric = value.replace(".", "", 1).isdigit()
            cells += [workbooks.cell(spot) if value == "" else workbooks.cell(spot, value) if numeric else workbooks.cell(spot, value, "inlineStr")]
        body += [(number, cells)]
    path.write_bytes(workbooks.package([
        ("[Content_Types].xml", workbooks._content_types(1, False, False, False)),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, False)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/worksheets/sheet1.xml", workbooks.sheet(body, dimension=f"A1:{letters[len(header) - 1]}{number}")),
    ]))
    return path


def _workbook_twin_checked(folder: pathlib.Path, name: str, subjects: int, seed: int, empty: int, place: int) -> "dict[str, typing.Any]":
    """`st2_rows(subjects, seed, True)`, every twentieth reading absent and `empty` empty records at `place`, as a workbook described behind
    the switch; its twin as made, then written as a workbook and read back."""
    from synthtwin import sheetwriting, writing

    header, rows = patient_enumeration.st2_rows(subjects, seed, True)
    rows = [list(row[:-1]) + ["" if at % 20 == 19 else row[-1]] for at, row in enumerate(rows)]
    records: "list[list[str] | None]" = list(rows[:place]) + [None] * empty + list(rows[place:])
    book = _workbook_of(folder / f"{name}.xlsx", header, records)
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("sid",))
    table = reading.read_table(str(book), small_cell_floor=11)
    document = profile.build_document(table, settings, ["sid"], [], [], subjects=["sid"], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, KEY, rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is not None and chained.statistical is not None and chained.columns is not None
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    loaded, twin, names, columns = _made(fixtures.write_profile(folder, f"{name}-profile.json", switched))
    assert loaded.source.workbook is not None and loaded.source.workbook.empty_rows_inside == empty
    person = columns[names.index("sid")]
    readings = columns[names.index("reading")]
    made: "dict[str, list[str]]" = {}
    for key, value in zip(person, readings):
        if key:
            made.setdefault(key, []).append(value)
    target = folder / f"{name}-twin.xlsx"
    writing.write_workbook_file(target, sheetwriting.workbook_stream(loaded, twin))
    back = reading.read_table(str(target), small_cell_floor=11)
    written = [reading.column_values(back, at) for at in range(len(back.column_names))]
    back_person = written[list(back.column_names).index("sid")]
    back_readings = written[list(back.column_names).index("reading")]
    read: "dict[str, list[str]]" = {}
    for key, value in zip(back_person, back_readings):
        if key:
            read.setdefault(key, []).append(value)
    return {
        "reserved_rows": twin.reserved_rows,
        "empty_at": [row for row in range(len(person)) if all(column[row] == "" for column in columns)],
        "no_person": len([row for row in range(len(person)) if person[row] == "" and any(column[row] != "" for column in columns)]),
        "written_empty_at": [row for row in range(len(back_person)) if all(column[row] == "" for column in written)],
        "moved": len([key for key in made if sorted(made[key]) != sorted(read[key] if key in read else [])]),
        "patients": len(made),
        "switched": switched,
        "back": back,
    }


def test_a_workbook_twin_keeps_every_patient_s_readings_on_its_rows(tmp_path):
    """Codex's item 1 (LANE GRb RULINGS 5 (1)), on his shape: 1,200 subjects, every twentieth reading absent, eleven empty records
    at row 100, a workbook. The twin's records holding nothing stand reserved on its first eleven rows (`reserved_rows`), none
    holds a cell without a person, and written as a workbook and read back every patient's readings are the twin's own and the
    empty records stand where they were reserved; V12.7 holds every line on the written file. MUTANT, the repair-1 head: the
    text file's arrangement gave the eleven records cells of other rows (eleven records without a person) and the writer
    moved each column's cells holding nothing on its own (ten patients' readings moved)."""
    from synthtwin import chain_validation

    found = _workbook_twin_checked(tmp_path, "st2s", 1200, 1, 11, 100)
    assert found["reserved_rows"] == 11 and found["empty_at"] == list(range(11)) and found["no_person"] == 0, found["empty_at"]
    assert found["written_empty_at"] == list(range(11)) and found["moved"] == 0 and found["patients"] == 1200
    back = found["back"]
    settings = taxonomy.Settings(small_cell_floor=11)
    lines = chain_validation.lines_of(found["switched"], back, profile.build_document(back, settings, [], [], [], []), settings, [], [], [],
                                      profile.stored_as_of(back, settings))
    verdicts = _verdicts(lines)
    assert verdicts and all(one == "HELD" for one in verdicts.values()), verdicts


def test_a_workbook_twin_keeps_its_patients_wherever_the_empty_records_stood(tmp_path):
    """Codex's item 1, its CLASS closed by a GENERATED variant: 400 subjects with 11 to 40 empty records (a count under the floor is
    held back, and the layer stands only beside a published one) at places drawn over the table (its first two rows among them;
    the build failed at rows 1 and 100 of his shape): every twin keeps its records holding nothing reserved on its first rows and
    every patient's readings on its rows, written and read back. MUTANT, the repair-1 head: the records holding nothing given
    cells of other rows, and patients' readings moved."""
    import random

    draw = random.Random(4651)
    places = [0, 1, draw.randint(2, 1300), draw.randint(1300, 2600)]
    for at, place in enumerate(places):
        empty = draw.choice([11, 17, 23, 40])
        found = _workbook_twin_checked(tmp_path, f"wb{at}", 400, 2, empty, place)
        assert found["reserved_rows"] == empty and found["empty_at"] == list(range(empty)) and found["no_person"] == 0, (place, empty)
        assert found["written_empty_at"] == list(range(empty)) and found["moved"] == 0, (place, empty, found["moved"])


def _position_rows(patients: int) -> "tuple[list[str], list[list[str]]]":
    """Codex's item 6 table: each patient eleven visits, age 92 at the first and 80 to 89 after, a reading beside it."""
    import random

    draw = random.Random(465)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        for visit, age in enumerate([92] + list(range(80, 90))):
            rows += [[f"P{patient:05d}", f"{age}", f"{draw.gauss(50, 8) + visit * 0.3:.1f}"]]
    return ["pid", "age", "value"], rows


def test_a_position_list_read_through_a_top_code_validates_its_own_source(tmp_path):
    """Codex's item 6 (LANE GRb RULINGS 5 (5)), on his table (2,000 patients, eleven visits, 22,000 rows; age a declared
    measurement, top-coded): the producer publishes the list `90, 80, ..., 89`, read on the cells as the description read
    them, and its emptied block keeps the reading's mark (`top_coded`), so V12.7 reads the SOURCE's cells through it and
    holds every line, the twin's too. MUTANT, the repair-1 head: the block emptied of the mark and the cells read as written,
    so the source's own `positions age` read MISSED."""
    from synthtwin import chain_validation

    header, rows = _position_rows(2000)
    path = tmp_path / "positions.csv"
    path.write_text(",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows), encoding="utf-8", newline="\n")
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=11), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, ["pid"], [], ["age"], subjects=["pid"], top_code=True)
    chained = chain.describe(table, document, settings, chain.ChainSwitch("pos", KEY, rows_per_person=chain.ROWS_PERSON))
    assert chained.grain is not None and chained.statistical is not None and chained.columns is not None
    assert chained.grain["positions"] == [{"column": "age", "values": ["90"] + [f"{age}" for age in range(80, 90)]}]
    assert [block for block in chained.columns if block["name"] == "age"][0]["top_coded"] == 90
    switched = json.loads(json.dumps(document))
    switched["relationships"]["statistical"] = chained.statistical
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    plain = taxonomy.Settings(small_cell_floor=11)
    redescribed = profile.build_document(table, plain, [], [], ["age"], [])
    lines = chain_validation.lines_of(switched, table, redescribed, plain, [], ["age"], [], profile.stored_as_of(table, plain))
    verdicts = _verdicts(lines)
    assert verdicts["positions age"] == "HELD" and all(one == "HELD" for one in verdicts.values()), verdicts
    loaded, _twin, names, columns = _made(fixtures.write_profile(tmp_path, "positions-profile.json", switched))
    assert set(columns[names.index("age")]) <= {"90"} | {f"{age}" for age in range(80, 90)}
    assert _verdicts(_lines_of(switched, names, columns, tmp_path))["positions age"] == "HELD"


def test_a_position_like_block_keeps_every_mark_its_list_was_read_through(tmp_path):
    """Codex's item 6, its CLASS closed by a GENERATED check (the stopping rule): for every combination of the marks a column
    block can carry that `chain.described_cells` reads (the age top-code at 90 or in months, its pooled top category and the
    people it counts, the year cut, a column counted absent, the dated remark beside another remark), over generated cells
    (ages past the mark, placeholders, years, dates in disguise, blanks), the position-like block the producer publishes
    (`patient_layer._position_block`) reads every cell as the row block does, holds no other key, and the loader's S30 and the
    summary accept it as emptied (`patient_rules.position_emptied`, `summary._emptied_by_the_patient_layer`). MUTANT, the
    repair-1 head: the block emptied whole."""
    import csv
    import itertools
    import random

    from synthtwin import patient_layer, summary

    dated = taxonomy.rendered(taxonomy.REMARK_DATED_VALUES_HELD, ())
    draw = random.Random(4656)
    tables: "list[reading.Table]" = []
    for at in range(1):
        path = tmp_path / f"marks-{at}.csv"
        with open(path, "w", encoding="utf-8", newline="\n") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(["pid", "x"])
            for row in range(140):
                kind = draw.randint(0, 6)
                cell = [f"{draw.randint(60, 125)}", f"{draw.randint(80, 140)}", "999", "", f"{draw.randint(1890, 2030)}",
                        f"{draw.randint(1, 28):02d}/{draw.randint(1, 12):02d}/{draw.randint(1990, 2030)}", f"{draw.randint(900, 1500)}"][kind]
                writer.writerow([f"P{row // 4:04d}", cell])
        tables += [reading.read_table(str(path), small_cell_floor=11)]
    declared = {"code": False, "measurement": True, "decimal_comma": False}
    settings = taxonomy.Settings(small_cell_floor=11)
    checked = 0
    marks = itertools.product((None, 90, 1080), (None, 11), (None, ["pid"]), (None, 1937), (None, True), ([], [dated], [dated, "another remark"], ["another remark"]))
    for top, pooled, people, year, absent, remarks in marks:
        row_block: "dict[str, object]" = {"name": "x", "position": 2, "role": "count", "statistical_type": "count", "n_present": 240, "n_missing": 0, "top_coded": top,
                                          "top_category_pooled": pooled, "top_category_people": people, "top_coded_year": year,
                                          "present_count_withheld": absent, "remarks": remarks, "levels": [], "detection_evidence": "read as numbers"}
        published = patient_layer._position_block(row_block)
        assert patient_rules.position_emptied(published) and summary._emptied_by_the_patient_layer(published), published
        kept = {key for key in published if published[key] not in (None, [], {})}
        assert kept <= set(patient_rules.EMPTIED_KEPT) | set(patient_rules.POSITION_MARKS) | {"remarks"}, kept
        for table in tables:
            assert chain.described_cells(table, 1, published, settings, declared, "") == chain.described_cells(table, 1, row_block, settings, declared, ""), (top, pooled, people, year, absent, remarks)
            checked += 1
    assert checked == 3 * 2 * 2 * 2 * 2 * 4 * len(tables)


def test_a_row_family_is_judged_only_where_its_child_s_totals_hold(visits, visit_twin, tmp_path):
    """Codex's item 7 (LANE GRb RULINGS 5 (6)): V12.7's dated line reads every non-derived member's `L0` totals before a family
    is judged, the row family's child too. One twin reading moved to another `L0` band inside its family's band moves the
    child's `L0` totals and no family table, so the row family reads "not judged", never HELD. MUTANT, the repair-1 head:
    the parents' totals alone, so the row family read HELD."""
    document = json.loads(visits.read_text(encoding="utf-8"))
    loaded, _twin, names, columns = visit_twin
    grain = loaded.relationships.grain
    assert grain is not None and grain.rows
    family = grain.rows[0]
    entry = [one for one in grain.ladder if one.column == family.child][0]
    block = [one for one in loaded.columns if one.name == family.child][0]
    reader = patient_walk._reading_of(loaded, block, entry)
    to_level = patient_walk._level_map(entry, family.level)
    at = names.index(family.child)
    l0 = [patient_walk._read(reader, cell)[0] for cell in columns[at]]
    first_of: "dict[int, int]" = {}
    for row, band in enumerate(l0):
        first_of.setdefault(band, row)
    moved = next((row, first_of[band]) for row in range(len(l0)) for band in first_of if band != l0[row] and to_level[band] == to_level[l0[row]])
    damaged = [list(column) for column in columns]
    damaged[at][moved[0]] = columns[at][moved[1]]
    lines = _lines_of(document, names, damaged, tmp_path)
    key = f"family {len(document['relationships']['statistical']['chain'])} {family.child}"
    verdicts = _verdicts(lines)
    assert verdicts[key] == "WITHHELD", {name: one for name, one in verdicts.items() if name.startswith("family")}
    assert [one.reason for one in lines.families if f"family {one.index} {one.child}" == key][0].startswith("not judged")


def test_a_derived_miss_names_the_row_family_it_moves(visits, monkeypatch):
    """The statistics check's item 5 (G16.15: a patient left outside its band is named in the twin's DEVIATIONS with the
    family it misses): with the own-mean close's exchanges off, the deviations name the derived miss (`grain.derived`)
    AND the row family whose parent the derived column is (`grain.rows`, its child). MUTANT, the build head: the
    derived line alone."""
    monkeypatch.setattr(patient_walk, "_one_exchange", lambda p, state, mine: None)
    loaded, twin, _names, _columns = _made(visits)
    grain = loaded.relationships.grain
    assert grain is not None
    own = [one for one in grain.derived if one.kind == patient_rules.OWN_MEAN][0]
    named = {(one.column, one.fact) for one in twin.deviations if one.fact.startswith("grain.")}
    assert (own.source, "grain.derived") in named
    children = [family.child for family in grain.rows if any(name == own.name for name, _level in family.parents)]
    assert children and all((child, "grain.rows") in named for child in children)
    # Codex's item 8 (repair 2): the note says what was searched, never that no exchange could repair the mean.
    note = [one.note for one in twin.deviations if (one.column, one.fact) == (own.source, "grain.derived")][0]
    assert "bounded search" in note and "did not find a repair" in note and "could" not in note, note


def test_the_driver_reads_first_dates_and_held_sources_without_stopping(first_dates, tmp_path):
    """The first skeptic's item 4 on lane GRa's two first-date shapes: K-BC-06's driver reads a first date by the reader's own
    order at the derived column's level (the cohorts: every row family held, as V12.7 holds them), and skips and counts a
    derived column whose source the layer holds (the staggered starts). MUTANT, the build head's driver: ValueError (a
    date's text read as a float) on the cohorts and KeyError (the held source's ladder) on the staggered starts."""
    for label, path in first_dates.items():
        loaded, _twin, names, columns = _made(path)
        grain = loaded.relationships.grain
        assert grain is not None and any(one.kind == patient_rules.FIRST_DATE for one in grain.derived)
        checks = kpi_patient_twin.grain_checks(loaded, names, columns)
        assert checks["census_held"] is True and checks["fixed_constant"] == 1.0
        if label == "staggered":
            assert checks["derived_source_held"] and checks["skipped_for_a_held_source"] > 0
        else:
            assert checks["derived_source_held"] == [] and checks["skipped_for_a_held_source"] == 0
            families = checks["row_families"]
            assert isinstance(families, list) and families and all(one["held"] for one in families)
            document = json.loads(path.read_text(encoding="utf-8"))
            verdicts = _verdicts(_lines_of(document, names, columns, tmp_path))
            assert verdicts and all(verdict == "HELD" for verdict in verdicts.values()), verdicts


def test_the_walk_holds_the_row_columns_twice_at_most(visits, monkeypatch):
    """G16.17's memory (LANE GRb RULINGS 3 (6): on the fifty-column table at 200,000 rows the walk's footprint stood 98 per
    cent above the plain generate's, the row columns held three times): the row columns' run is handed over in a box the
    walk empties of its columns once it has read them, and each row column is dropped once its finished column is made;
    the twin's bytes do not move. MUTANT, the build head: the run's columns kept to the end, and the walk's own copies
    kept beside the finished columns."""
    seen: "dict[str, object]" = {}
    real = patient_walk._assembled

    def spy(profile_, table, patients, rows, made, deviations, drawn, seed):
        seen["row_run_columns"] = made[0].held_columns
        out = real(profile_, table, patients, rows, made, deviations, drawn, seed)
        seen["row_columns_left"] = len(rows.cells)
        return out

    monkeypatch.setattr(patient_walk, "_assembled", spy)
    loaded = contract.load_profile(str(visits), chain=True)
    made = generation.generate_held(loaded, 7)
    assert made.held_columns and seen["row_run_columns"] is None and seen["row_columns_left"] == 0


# -- THE FOLLOW-UP OF LANE GRb: the two orders repair 2 keeps, pinned (its scoped verify; LANE GRb RULINGS 6 (2)) ----------


def _generated_parent_cells(count: int) -> "list[tuple[list[int | None], list[fractions.Fraction], list[int], list[int], patient_walk._Patients]]":
    """GENERATED parent cells of the own-mean close, one a close (the scoped verify of repair 2's generator and seed): 2 to 12
    patients of 1 to 30 rows, whole-number readings in narrow ranges (each 0 to 3, 9 or 40, so equal readings are common), 1
    to 3 edges in quarters, each patient dealt a band; each cell's readings, edges, bands, rows' patients and patient table."""
    import random

    draw = random.Random(4655)
    made: "list[tuple[list[int | None], list[fractions.Fraction], list[int], list[int], patient_walk._Patients]]" = []
    for _cell in range(count):
        patients = draw.randint(2, 12)
        groups = [[draw.randint(0, draw.choice([3, 9, 40])) for _row in range(draw.randint(1, 30))] for _p in range(patients)]
        edges = sorted({fractions.Fraction(draw.randint(0, 80), 4) for _edge in range(draw.randint(1, 3))})
        bands = [draw.randint(0, len(edges)) for _p in range(patients)]
        values: "list[int | None]" = [value for group in groups for value in group]
        owner = [p for p, group in enumerate(groups) for _value in group]
        starts: "list[int]" = []
        at = 0
        for group in groups:
            starts += [at]
            at += len(group)
        made += [(values, edges, bands, owner, patient_walk._Patients(patients, {}, {}, [len(group) for group in groups], starts))]
    return made


def test_the_own_mean_close_proposes_each_patient_s_rows_in_the_documented_order(monkeypatch):
    """The scoped verify of repair 2, its item 1 (LANE GRb RULINGS 6 (2) (a)): the own-mean close keeps each patient's rows in
    their proposal order as its readings change (an exchange removes one row and inserts it by a halving search; nothing is
    sorted again). Over 5,000 GENERATED parent cells (`_generated_parent_cells`), `mean_close`'s result (its exchanges in the
    order made, the patients left, the bound's flag and its row reads) equals that of a REFERENCE run in which
    `_one_exchange` is handed the patient's rows freshly sorted before every proposal: the lowest reading first where its
    sum must rise, the highest first where it must fall (the documented order); at least 4,000 of the cells make two
    exchanges or more. MUTANT, the verify's 'no order kept' (the two lines that move the exchanged row in the patient's
    kept order removed): the exchanges or the patients left of 1,090 of the 5,000 cells change, and the whole result (its
    row reads included) of 3,551."""
    cells = _generated_parent_cells(5000)
    kept = [patient_walk.mean_close(list(values), 1, edges, bands, owner, patients, [0 for _p in range(patients.count)])
            for values, edges, bands, owner, patients in cells]
    real = patient_walk._one_exchange
    proposing = [cells[0][4]]

    def freshly_sorted(p, state, mine):  # type: ignore[no-untyped-def]
        rising = state.sums[p] < state.lows[p]
        begin = proposing[0].start[p]
        mine[:] = sorted((value if rising else -value, row) for row in range(begin, begin + proposing[0].r[p])
                         for value in (state.values[row],) if value is not None)
        return real(p, state, mine)

    monkeypatch.setattr(patient_walk, "_one_exchange", freshly_sorted)
    differ: "list[int]" = []
    several = 0
    for at, (values, edges, bands, owner, patients) in enumerate(cells):
        proposing[0] = patients
        reference = patient_walk.mean_close(list(values), 1, edges, bands, owner, patients, [0 for _p in range(patients.count)])
        several += 1 if len(reference.exchanges) >= 2 else 0
        if kept[at] != reference:
            differ += [at]
    assert several >= 4000, several
    assert not differ, (f"{len(differ)} of {len(cells)} parent cells close otherwise than in the documented order", differ[:5])


def _lowest_patient_close(cells: "list[str]", codes: "list[int]", found: "list[int]", patients: "patient_walk._Patients", rho: int,
                          total: int, window: "tuple[int, int]") -> int:
    """THE REFERENCE of the trend close's exact steps on one cell (G16.15; `_exact_close`'s docstring: among equal choices the
    lowest patient, then its steps in their order): one exchange whose step equals the remaining gap, else two of different
    patients whose steps sum to it, else the largest step that fits, at most `4 |P| + 8` rounds; each step's holders kept as
    a set and the lowest patient taken by `min` over them at every choice, as the repair-1 head read it. Returns `S_P`."""
    low, high = window
    steps: "dict[int, dict[int, tuple[int, int, int]]]" = {}
    holders: "dict[int, dict[int, bool]]" = {}

    def hold(p: int) -> None:
        for step in steps[p]:
            if step in holders:
                holders[step][p] = True
            else:
                holders[step] = {p: True}

    def unhold(p: int) -> None:
        for step in steps[p]:
            if step in holders and p in holders[step]:
                del holders[step][p]
                if not holders[step]:
                    del holders[step]

    def two(want: int) -> "list[tuple[int, int, int]]":
        first = -1
        for step in holders:
            rest = want - step
            if rest in holders and [other for other in holders[rest] if other != min(holders[step])]:
                if first < 0 or min(holders[step]) < first:
                    first = min(holders[step])
        if first < 0:
            return []
        for step in steps[first]:
            others = [other for other in holders.get(want - step, {}) if other != first]
            if others:
                return [steps[first][step], steps[min(others)][want - step]]
        return []

    for p in found:
        steps[p] = patient_walk._steps_of(codes, patients.start[p], rho, p)
        hold(p)
    rounds = 0
    while patient_walk._gap(total, low, high) > 0 and rounds < 4 * len(found) + 8:
        rounds += 1
        want = (low - total) if total < low else (high - total)
        chosen = [steps[min(holders[want])][want]] if want in holders else two(want)
        if not chosen:
            fits = [step for step in holders if (want > 0 and 0 < step < want) or (want < 0 and want < step < 0)]
            if fits:
                best = max(fits, key=abs)
                chosen = [steps[min(holders[best])][best]]
        if not chosen:
            break
        for p, a, b in chosen:
            begin = patients.start[p]
            total += patient_walk._step(codes, begin, a, b)
            patient_walk._exchange(cells, codes, begin + a, begin + b)
            unhold(p)
            steps[p] = patient_walk._steps_of(codes, begin, rho, p)
            hold(p)
    return total


def test_the_trend_close_takes_the_lowest_patient_as_its_holders_change():
    """The scoped verify of repair 2, its item 2 (LANE GRb RULINGS 6 (2) (b)): the trend close keeps each step's patients
    ascending as their steps change (a patient inserted and removed by a halving search), so a step's first holder is its
    lowest patient. Over 4,000 GENERATED cells (2 to 40 patients of one `rho`, 3 to 12; whole-number codes from 0 to 1, 2,
    5 or 30, so steps repeat across patients; a window of 1 to 4 values within 60 of `S_P`), `_exact_close`'s `S_P` and
    every code and cell after it equal those of `_lowest_patient_close`, the reference that takes the lowest patient by
    `min` over each step's holders. MUTANT, the verify's 'holder lists appended, not kept ascending' (`_hold` appending
    where `bisect.insort` inserts): 233 of the 4,000 results change, 55 of them raising KeyError on a stale holder."""
    import random

    draw = random.Random(4654)
    differ: "list[int]" = []
    raised: "list[int]" = []
    moved = 0
    for case in range(4000):
        count = draw.randint(2, 40)
        rho = draw.randint(3, 12)
        top = draw.choice([1, 2, 5, 30])
        codes = [draw.randint(0, top) for _k in range(count * rho)]
        cells = [f"{code}" for code in codes]
        patients = patient_walk._Patients(count, {}, {}, [rho] * count, [rho * p for p in range(count)])
        total = sum(patient_walk._s_of(codes[rho * p:rho * p + rho]) for p in range(count))
        low = total + draw.randint(-60, 60)
        high = low + draw.choice([0, 0, 1, 3])
        expected_cells, expected_codes = list(cells), list(codes)
        expected = _lowest_patient_close(expected_cells, expected_codes, list(range(count)), patients, rho, total, (low, high))
        moved += 1 if expected_codes != codes else 0
        try:
            got = patient_walk._exact_close(cells, codes, list(range(count)), patients, rho, total, (low, high))
        except KeyError:
            raised += [case]
            differ += [case]
            continue
        if (got, codes, cells) != (expected, expected_codes, expected_cells):
            differ += [case]
    assert moved >= 3000, moved
    assert not differ, (f"{len(differ)} of 4000 cells close otherwise than the lowest-patient reference, {len(raised)} raising KeyError", differ[:5])

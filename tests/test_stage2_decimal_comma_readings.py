"""Regression witnesses for finding 2 (decimal-comma recounts mix readings)."""

import fixtures
from synthtwin import contract, generation, profile, reading, taxonomy, validation

A2_CELLS = [
    f"{1200.25 + 97 * i:,.2f}".translate(str.maketrans(".,", ",."))
    for i in range(40)
] + ["1,234,567"] * 5 + ["2,345,678"] * 5

A3_CELLS = [f"{-1000000 + 25 * i:,}".replace(",", ".") for i in range(41)] + [
    "-999,000"
] * 10


def _described(folder, cells, missing=()):
    table = fixtures.write(folder, "t.csv", fixtures.single_column_table("v", cells))
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(declared_missing_values=tuple(missing)),
        [],
        [],
        [],
        ["v"],
    )
    loaded = contract.load_profile(f"{fixtures.write_profile(folder, 't.json', document)}")
    return document, loaded, folder, table


def _missed(loaded, path):
    outcome = validation.measure(loaded, f"{path}")
    return [(c.fact, c.subcheck) for c in outcome.checks if c.verdict == "MISSED"]


def _twin_file(loaded, folder, seed=4):
    twin = generation.generate(loaded, seed)
    path = fixtures.write(folder, "twin.csv", fixtures.single_column_table("v", list(twin.columns[0])))
    return twin, path


def test_a2_profile_is_forty_numbers_and_ten_labels(tmp_path):
    document, *_ = _described(tmp_path, A2_CELLS)
    column = document["columns"][0]
    assert column["role"] == "numbers_with_labels"
    assert (column["n_numeric_cells"], column["n_label_cells"]) == (40, 10)


def test_a2_twin_report_counts_labels_as_labels(tmp_path):
    _document, loaded, folder, _table = _described(tmp_path, A2_CELLS)
    twin, _path = _twin_file(loaded, folder)
    assert [(d.fact, d.published, d.achieved) for d in twin.deviations] == []
    mean = [a for a in twin.approximations if a.fact == "mean"]
    # Re-pinned at landing 2b.1's stratum cap, which holds no value in
    # more cells than the published mode_count and so moves this mean
    # from 3101.313 to 3046.82675. What the test is about is unchanged:
    # the labels beside these numbers are not counted as numbers.
    assert mean and abs(float(mean[0].achieved) - 3046.82675) < 1e-6
    assert mean[0].inside


def test_a2_source_and_twin_miss_nothing(tmp_path):
    _document, loaded, folder, table = _described(tmp_path, A2_CELLS)
    _twin, path = _twin_file(loaded, folder)
    assert _missed(loaded, table) == []
    assert _missed(loaded, path) == []


def test_a2_vacuity_a_label_rewritten_as_a_declared_number_is_caught(tmp_path):
    _document, loaded, folder, _table = _described(tmp_path, A2_CELLS)
    other = [c if c != "1,234,567" else "1.234.567" for c in A2_CELLS]
    path = fixtures.write(folder, "other.csv", fixtures.single_column_table("v", other))
    assert _missed(loaded, path)


def test_a3_profile_keeps_the_grouped_maximum(tmp_path):
    document, *_ = _described(tmp_path, A3_CELLS, ["-999"])
    column = document["columns"][0]
    assert column["n_numeric"] == 41 and column["missing_by_source"] == {"-999,000": 10}


def test_a3_twin_report_keeps_the_grouped_maximum(tmp_path):
    _document, loaded, folder, _table = _described(tmp_path, A3_CELLS, ["-999"])
    twin, _path = _twin_file(loaded, folder)
    assert "-999.000" in twin.columns[0]
    assert [(d.fact, d.published, d.achieved) for d in twin.deviations] == []


def test_a3_source_and_twin_miss_nothing(tmp_path):
    _document, loaded, folder, table = _described(tmp_path, A3_CELLS, ["-999"])
    _twin, path = _twin_file(loaded, folder)
    assert _missed(loaded, table) == []
    assert _missed(loaded, path) == []


def test_a3_vacuity_the_maximum_written_as_the_hole_is_caught(tmp_path):
    _document, loaded, folder, _table = _described(tmp_path, A3_CELLS, ["-999"])
    other = ["-999,000" if c == "-999.000" else c for c in A3_CELLS]
    path = fixtures.write(folder, "other.csv", fixtures.single_column_table("v", other))
    assert _missed(loaded, path)


def test_a3_hole_identity_is_the_declared_grammar_on_the_file_text():
    cells = ["-999.000", "-999,000", "-999"]
    declared = ("-999", "-999,000")
    assert validation._holes_by_the_description({}, cells, (), declared, True) == [False, True, True]

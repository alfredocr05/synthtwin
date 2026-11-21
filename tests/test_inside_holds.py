"""Gate file of lane IN-7 (plan P4-D501): the holds narrowed for the inside record.

A column or a spelling is held from the record only as an identifier or a
Safe Harbor element; every other one is modelled and drawn, the twin
keeping every Safe Harbor rule (identifiers made up, ages capped at 90).

WHAT IT HOLDS, each clause red on its mutant (lane IN-7's report):

* A number written inside a unit (`72.5 kg`) is modelled: read as its
  number, its relation to the columns before it fitted, written back
  inside its unit; a few cells in another unit are words of the column.
* An age written inside a unit is never drawn past 90, a spike of old
  ages included.
* An ordinary label carries its rare real spellings, drawn at their
  real counts, and never a spelling that reads as a date, an age, a
  person's details or a long run of figures.
* `held_spelling` holds exactly those spellings.
* A column the description holds as record numbers although the person
  answered it a measurement is modelled as a number; capped at 90 where
  it could be an age; left held where it is declared or named an
  identifier, or where the person did not answer it so.
* An age label and a column named as an identifier element carry
  nothing new.
"""

from __future__ import annotations

import random

import numpy.random

from synthtwin import inside_holds, inside_relations

_CEILING = 18446744073709551615


def _words(count: int, seed: int) -> "list[int]":
    return [int(word) for word in numpy.random.default_rng(seed).integers(0, _CEILING, size=count, dtype="uint64",
                                                                         endpoint=True)]


def _mean(values: "list[float]") -> float:
    return sum(values) / max(1, len(values))


def _weights(rows: int, seed: int) -> "tuple[list[str], list[str]]":
    r = random.Random(f"in7-weights-{seed}")
    group = ["F" if r.random() < 0.5 else "M" for _row in range(rows)]
    cells = [f"{max(40.0, r.gauss(74.0 if g == 'F' else 80.0, 10.0)):.1f} kg" for g in group]
    for row in range(5):
        cells[row * 97] = f"{170.0 + row:.1f} lb"
    return group, cells


def test_a_number_written_inside_a_unit_is_modelled_and_written_back_inside_it() -> None:
    rows = 3000
    group, cells = _weights(rows, 1)
    sample = inside_relations.sample_rows(rows)
    parent = inside_relations.encode(inside_relations.ColumnSpec("gender", 0, inside_relations.LABEL, 0, ("F", "M"), ""),
                                     group, sample, None)
    weight = inside_relations.encode(inside_relations.ColumnSpec("weight", 1, inside_relations.NUMBER, 0, (), ""),
                                     cells, sample, None)
    assert parent is not None and weight is not None
    assert weight.entry["wrapper"] == ["", " kg"]
    assert weight.entry["states"][inside_relations.WORD] == 5  # type: ignore[index]
    zone = inside_relations.fit_zone([parent, weight], rows, rows)
    entries = zone["columns"]
    twin_group, _cells = _weights(rows, 2)
    codes = [0 if g == "F" else 1 for g in twin_group]
    if entries[0]["levels"][0] != "F":  # type: ignore[index]
        codes = [1 - code for code in codes]
    frames = {"gender": inside_relations.Frame(inside_relations.LABEL, [], [], codes)}
    drawn = inside_relations.draw_number(entries[1], frames, rows, _words(2 * rows, 5))  # type: ignore[arg-type]
    written = [cell for cell in drawn.cells if cell is not None and cell != ""]
    assert len(written) >= rows - 20
    assert all(cell[-3:] == " kg" for cell in written)
    female = [float(cell[:-3]) for cell, g in zip(drawn.cells, twin_group) if cell and g == "F"]
    male = [float(cell[:-3]) for cell, g in zip(drawn.cells, twin_group) if cell and g == "M"]
    real_female = [float(cell[:-3]) for cell, g in zip(cells, group) if g == "F" and cell[-3:] == " kg"]
    real_male = [float(cell[:-3]) for cell, g in zip(cells, group) if g == "M" and cell[-3:] == " kg"]
    assert abs((_mean(male) - _mean(female)) - (_mean(real_male) - _mean(real_female))) <= 1.2


def test_an_age_written_inside_a_unit_is_never_drawn_past_ninety() -> None:
    r = random.Random("in7-ages")
    rows = 3000
    cells = [f"{min(99, max(18, int(r.gauss(62, 15))))} years" for _row in range(rows)]
    for row in range(0, rows, 12):
        cells[row] = "99 years"
    sample = inside_relations.sample_rows(rows)
    found = inside_relations.encode(inside_relations.ColumnSpec("age", 0, inside_relations.NUMBER, 90, (), ""), cells,
                                    sample, None)
    assert found is not None and found.entry["wrapper"] == ["", " years"]
    assert found.entry["spikes"][1] is not None  # type: ignore[index]
    zone = inside_relations.fit_zone([found], rows, rows)
    drawn = inside_relations.draw_number(zone["columns"][0], {}, rows, _words(2 * rows, 9))  # type: ignore[index]
    values = [int(cell[: -len(" years")]) for cell in drawn.cells if cell]
    assert len(values) == rows
    assert max(values) == 90
    assert all(cell[-6:] == " years" for cell in drawn.cells if cell)


def _labels(rows: int, seed: int) -> "tuple[list[str], list[str], list[str]]":
    """Ten common levels, forty rare ones held by 1 to 10 rows each, and seven rows of spellings that stay held."""
    r = random.Random(f"in7-labels-{seed}")
    common = [f"C{k}" for k in range(10)]
    rare: "list[str]" = []
    for k in range(40):
        rare += [f"R{k:02d}"] * (1 + k % 10)
    held = ["2024-03-05", "2024-03-05", "2024-03-05", "age 95", "age 95", "ref 1234567", "ref 1234567"]
    cells = [r.choice(common) for _row in range(rows - len(rare) - len(held))] + rare + held
    r.shuffle(cells)
    return cells, common, held


def test_an_ordinary_label_carries_its_rare_spellings_at_their_real_counts_and_never_a_held_one() -> None:
    rows = 4000
    cells, common, held = _labels(rows, 1)
    spec = inside_relations.ColumnSpec("result_code", 0, inside_relations.LABEL, 0, tuple(common), "")
    carried = inside_holds.carried_spec(spec, {"name": "result_code", "role": "categorical"}, cells)
    assert carried.carried
    assert {f"R{k:02d}" for k in range(40)} <= set(carried.spellings)
    assert not set(held) & set(carried.spellings)
    found = inside_relations.encode(carried, cells, inside_relations.sample_rows(rows), None)
    assert found is not None
    zone = inside_relations.fit_zone([found], rows, rows)
    drawn = inside_relations.draw_label(zone["columns"][0], {}, rows, _words(rows, 3), set(common))  # type: ignore[index]
    written = [cell for cell in drawn.cells if cell is not None]
    rare_written = [cell for cell in written if cell[:1] == "R"]
    assert 0.7 * 220 <= len(rare_written) <= 1.3 * 220, len(rare_written)
    assert len(set(rare_written)) >= 30
    assert not set(held) & set(written)


def test_held_spelling_holds_dates_ages_and_long_runs_of_figures_and_nothing_ordinary() -> None:
    for text in ("2024-03-05", "age 95", "ref 1234567", "03/05/2024"):
        assert inside_holds.held_spelling(text), text
    for text in ("E11.65", "left knee", "Grade 2", "C4", "stage IIb", ""):
        assert not inside_holds.held_spelling(text), text


def _held(name: str) -> inside_relations.ColumnSpec:
    return inside_relations.ColumnSpec(name, 3, "", 0, (), inside_relations.AN_IDENTIFIER)


def test_a_column_answered_a_measurement_but_held_as_record_numbers_is_modelled_as_a_number() -> None:
    block = {"role": "identifier", "structural_role": "identifier"}
    big = [f"{100 + k % 90}.5" for k in range(400)]
    small = [f"{20 + k % 70}" for k in range(400)]

    def settings(measured: "list[str]", declared: "list[str]") -> "dict[str, object]":
        return {"forced_measurements": measured, "forced_identifiers": declared, "person_columns": []}

    narrowed = inside_holds.narrowed_spec(_held("reading"), block, settings(["reading"], []), big)
    assert (narrowed.kind, narrowed.top) == (inside_relations.NUMBER, 0)
    assert inside_holds.narrowed_spec(_held("reading"), block, settings(["reading"], []), small).top == 90
    assert inside_holds.narrowed_spec(_held("weight"), block, settings(["weight"], []), small).top == 0
    assert inside_holds.narrowed_spec(_held("reading"), block, settings([], []), big).kind == ""
    assert inside_holds.narrowed_spec(_held("reading"), block, settings(["reading"], ["reading"]), big).kind == ""
    assert inside_holds.narrowed_spec(_held("item_key"), block, settings(["item_key"], []), big).kind == ""


def test_a_column_answered_a_measurement_that_holds_five_figures_or_dates_stays_held() -> None:
    block = {"role": "identifier", "structural_role": "identifier"}
    settings = {"forced_measurements": ["reading"], "forced_identifiers": [], "person_columns": []}
    shaped = [f"{52240 + k % 60}" for k in range(400)]
    assert inside_holds.narrowed_spec(_held("reading"), block, settings, shaped).kind == ""
    dated = [f"2024-03-{1 + k % 28:02d}" for k in range(400)]
    assert inside_holds.narrowed_spec(_held("reading"), block, settings, dated).kind == ""


def test_an_age_label_and_a_column_named_as_an_identifier_element_carry_nothing_new() -> None:
    cells, common, _held_cells = _labels(1000, 2)
    spec = inside_relations.ColumnSpec("age_band", 0, inside_relations.LABEL, 0, tuple(common), "")
    assert inside_holds.carried_spec(spec, {"role": "categorical", "top_coded": 90}, cells) == spec
    named = inside_relations.ColumnSpec("town_name", 0, inside_relations.LABEL, 0, tuple(common), "")
    assert inside_holds.carried_spec(named, {"role": "categorical"}, cells) == named

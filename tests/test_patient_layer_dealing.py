"""Gate file of lane W5-PL: the trajectories zone's dealing leaves the dates zone's rows and a two-part number alone.

With the patient layer on, the inside record's trajectories zone (lane IN-3) deals each repeated number, each yes/no
outcome and, on a table keyed by an item, each key's values with the cells standing beside them, after the dates zone
(lane IN-5) has written the twin's dates. Measured on the battery's tables at 20,000 rows before this file's rules:
a charting table's device flag dealt with its key's values left the rows it is entered at once and charted on the
minute (rows entered at once 1.0 to 0.66, the five-minute difference 0.63 to 0.18; the real 1.0 and 0.63), a universal
clock dealt beside a case's service left its local one (six hours apart on every row to 52 in 100), and a blood loss
that is nought on most rows, dealt on one scale, lost half its arm's effect on the amount (-0.15 against -0.31).

WHAT IT HOLDS (each clause red on its mutant):

* A column the dealing is told to keep (`applied(..., kept=...)`: a date the dates zone wrote, a label its clocks are
  drawn by) stays on its row while its key's values and their unit and copy are dealt (mutant: the kept columns dealt
  with the rest of the row's content).
* A repeated number whose one commonest value holds at least `ATOM_SHARE` of its present cells is not dealt, while
  the other repeated numbers are (mutant: `_with_an_atom` reading no atom).
* A column the description publishes nothing of (the patient layer empties the block of a repeated column no row
  family carries, so the description's twin writes it blank) is drawn from the inside record's relations zone, a
  number and a label alike, never left blank; a column that twin holds is dealt inside its own cells as before
  (mutant: the emptied column dealt inside its blank cells; measured on the battery's orders table, two of its eight
  columns written blank on every row and every analysis of a dose or an action stopped). The validator lists such a
  column's emptied block, as a position-like column's, never holding a twin to its empty counts (mutant:
  `contract.held_by_the_layer` naming no column).
"""

from __future__ import annotations

import json
import random
import types

from synthtwin import contract, inside_relations as R, inside_trajectories as I, twinstore

PERSON = "patient_id"


def _apply(zone: "dict[str, object]", columns: "dict[str, list[str]]", seed: int = 0,
           kept: "tuple[str, ...]" = ()) -> "dict[str, list[str]]":
    """The zone applied, its dealing alone (the rows stay where they are), every column given back in the rows' order."""
    names = list(columns)
    got = I.applied(json.loads(json.dumps(zone)), names, columns, seed, timing=False, kept=kept)
    out = {name: list(cells) for name, cells in columns.items()}
    for name, cells in got.columns.items():
        out[name] = cells
    return out


def _charting(patients: int, seed: int) -> "dict[str, list[str]]":
    """An invented charting table keyed by item, with a device flag beside each row's moment."""
    r = random.Random(seed)
    names = (PERSON, "item", "value", "copy", "unit", "device", "taken_at")
    out: "dict[str, list[str]]" = {name: [] for name in names}
    for p in range(patients):
        level = r.gauss(0.0, 10.0)
        start = 18000 * 1440 + r.randrange(500 * 1440)
        moments = sorted(r.randrange(72 * 60) for _k in range(2 + int(r.expovariate(1 / 12.0))))
        for minutes in moments:
            item = r.choice("AAABC")
            if item == "A":
                text, unit = f"{80.0 + level - 0.08 * minutes / 60.0 + r.gauss(0.0, 8.0):.0f}", "per one"
            elif item == "B":
                text, unit = f"{r.gauss(17.0, 3.0):.0f}", "per minute"
            else:
                text, unit = r.choice(("alert", "voice", "pain")), ""
            moment = start + minutes
            year, month, date = I.civil_from_days(moment // 1440)
            stamp = f"{year:04d}-{month:02d}-{date:02d} {(moment % 1440) // 60:02d}:{moment % 60:02d}"
            for name, cell in ((PERSON, f"Q{5000 + p}"), ("item", item), ("value", text), ("copy", text),
                               ("unit", unit), ("device", r.choice("YN")), ("taken_at", stamp)):
                out[name] += [cell]
    return out


def _visits(patients: int, seed: int) -> "dict[str, list[str]]":
    """An invented visits table: a pressure with a patient level and a trend, and a loss that is nought on most rows."""
    r = random.Random(seed)
    out: "dict[str, list[str]]" = {name: [] for name in (PERSON, "arm", "visit", "sbp", "loss")}
    for p in range(patients):
        arm_b = r.random() < 0.5
        level = r.gauss(0.0, 12.0)
        for k in range(1 + min(20, int(r.expovariate(1 / 6.0)))):
            sbp = 138.0 + level - (0.4 + 0.8 * arm_b) * k + r.gauss(0.0, 8.0)
            loss = 0 if r.random() < (0.65 if arm_b else 0.55) else int(r.lognormvariate(5.0 if arm_b else 5.3, 1.0))
            for name, cell in ((PERSON, f"P{100000 + p}"), ("arm", "B" if arm_b else "A"), ("visit", f"{k + 1}"),
                               ("sbp", f"{round(sbp)}"), ("loss", f"{loss}")):
                out[name] += [cell]
    return out


def _shuffled(columns: "dict[str, list[str]]", names: "tuple[str, ...]", seed: int) -> "dict[str, list[str]]":
    r = random.Random(seed)
    out = {name: list(cells) for name, cells in columns.items()}
    for name in names:
        r.shuffle(out[name])
    return out


def test_a_kept_column_stays_on_its_row_while_its_keys_values_are_dealt() -> None:
    """The device flag kept, the values, units and copies dealt within each item (mutant: the kept columns dealt too)."""
    real = _charting(700, 5)
    zone = I.zone_from_columns(real, PERSON, (PERSON,))
    assert zone is not None and zone["key"] == "item" and "device" in zone["bundle"]  # type: ignore[operator]
    lost = _shuffled(real, ("value",), 9)
    lost["copy"] = list(lost["value"])
    kept = _apply(zone, lost, kept=("device",))
    assert kept["device"] == lost["device"]
    assert kept["value"] != lost["value"] and kept["value"] == kept["copy"]
    dealt = _apply(zone, lost)
    assert dealt["device"] != lost["device"]


def test_a_number_with_an_atom_is_left_where_it_was_dealt() -> None:
    """The loss, nought on most rows, keeps its cells on their rows; the pressure is dealt (mutant: no atom read)."""
    real = _visits(900, 3)
    zone = I.zone_from_columns(real, PERSON, (PERSON,))
    assert zone is not None
    numbers = [entry["column"] for entry in zone["numbers"]]  # type: ignore[union-attr]
    assert "sbp" in numbers and "loss" in numbers
    assert I._with_an_atom(real["loss"]) and not I._with_an_atom(real["sbp"])
    lost = _shuffled(real, ("sbp", "loss"), 7)
    twin = _apply(zone, lost)
    assert twin["loss"] == lost["loss"]
    assert twin["sbp"] != lost["sbp"] and sorted(twin["sbp"]) == sorted(lost["sbp"])


def _orders(persons: int, seed: int) -> "dict[str, list[str]]":
    """An invented orders table: a drug, its dose by the drug, and an action that follows the dose."""
    r = random.Random(f"orders-{seed}")
    out: "dict[str, list[str]]" = {"pid": [], "drug": [], "dose": [], "action": []}
    for k in range(persons):
        for _order in range(r.randint(2, 9)):
            drug = r.choice(("alpha", "beta", "gamma"))
            dose = {"alpha": 500.0, "beta": 40.0, "gamma": 5.0}[drug] * r.choice((1.0, 1.0, 2.0))
            action = "given" if r.random() < (0.9 if dose < 100.0 else 0.7) else r.choice(("held", "refused"))
            for name, cell in (("pid", f"Q{100000 + 3 * k}"), ("drug", drug), ("dose", f"{dose:.0f}"),
                               ("action", action)):
                out[name] += [cell]
    return out


def test_a_column_the_description_publishes_nothing_of_is_drawn_from_the_record() -> None:
    """The dose and the action written blank by the description's twin are drawn from the zone; the drug is dealt
    inside its own cells (mutant: the emptied columns dealt inside their blank cells)."""
    columns = _orders(800, 1)
    kinds = {"drug": R.LABEL, "dose": R.NUMBER, "action": R.LABEL}
    persons = R.persons_of(columns["pid"])
    sample = R.sample_rows(len(columns["pid"]), persons=persons)
    encoded = []
    for place, name in enumerate(columns):
        kind = kinds.get(name, "")
        spellings = tuple(sorted(set(columns[name]))) if kind == R.LABEL else ()
        spec = R.ColumnSpec(name, place, kind, 0, spellings, "" if kind else R.NAMES_THE_PERSON)
        found = R.encode(spec, columns[name], sample, persons)
        if found is not None:
            encoded += [found]
    owners = [persons.person[row] for row in sample]
    zone = R.fit_zone(encoded, len(sample), len(columns["pid"]), owners, "pid")
    rows = len(columns["pid"])
    strict = {"pid": columns["pid"], "drug": list(reversed(columns["drug"])), "dose": ["" for _row in range(rows)],
              "action": ["" for _row in range(rows)]}
    blocks = []
    for name, cells in columns.items():
        counts: "dict[str, int]" = {}
        for cell in cells:
            counts[cell] = counts[cell] + 1 if cell in counts else 1
        levels = tuple(contract.LevelEntry(label, count, {label: count}, {}, 0) for label, count in counts.items())
        blocks += [types.SimpleNamespace(name=name, facts=contract.LabelFacts(levels, 0, 0, {},
                                                                              contract.PooledNumbers(0, None)))]
    profile = types.SimpleNamespace(n_rows=rows, columns=blocks)
    held = {name: twinstore.held_column(cells) for name, cells in strict.items()}
    drawn = {name: twinstore.column_cells(column)
             for name, column in R.draw_columns(zone, profile, held, 7).items()}  # type: ignore[arg-type]
    assert sorted(drawn["drug"]) == sorted(strict["drug"])
    for name in ("dose", "action"):
        filled = [cell for cell in drawn[name] if cell.strip()]
        assert len(filled) > 0.9 * rows, (name, len(filled))
    # A label is written in its modelled spellings; a number on the zone's grid, inside the column's own range.
    assert {cell for cell in drawn["action"] if cell.strip()} <= set(columns["action"])
    real = [float(cell) for cell in columns["dose"]]
    assert all(min(real) <= float(cell) <= max(real) for cell in drawn["dose"] if cell.strip())
    given = {"low": [0, 0], "high": [0, 0]}
    for dose, action in zip(drawn["dose"], drawn["action"]):
        if dose.strip() and action.strip():
            band = "low" if float(dose) < 100.0 else "high"
            given[band][0] += action == "given"
            given[band][1] += 1
    assert given["low"][0] / given["low"][1] > given["high"][0] / given["high"][1]


def test_the_validator_reads_the_layer_s_emptied_columns_by_their_class() -> None:
    """The held and the position-like columns of `grain`, each in schema order (mutant: the held class read as none)."""
    grain = types.SimpleNamespace(classes=(("pid", "person"), ("dose", "held"), ("visit", "position_like"),
                                           ("arm", "patient_fixed"), ("action", "held"), ("sbp", "repeated")))
    assert contract.held_by_the_layer(grain) == ("dose", "action")  # type: ignore[arg-type]
    assert contract.position_like(grain) == ("visit",)  # type: ignore[arg-type]
    assert contract.held_by_the_layer(None) == () == contract.position_like(None)


# -- batch 4y's fix round -------------------------------------------------------------------------------------------


def _ages_held_once_a_person(persons: int, seed: int) -> "dict[str, list[str]]":
    """Codex's table of the batch 4y review, item 1: each person nineteen ages of 60 to 80 and one of 91 to 105, in a
    shuffled order."""
    r = random.Random(f"ages-{seed}")
    out: "dict[str, list[str]]" = {"pid": [], "age": []}
    for k in range(persons):
        ages = [str(r.randint(60, 80)) for _cell in range(19)] + [str(r.randint(91, 105))]
        r.shuffle(ages)
        for age in ages:
            out["pid"] += [f"Q{200000 + k}"]
            out["age"] += [age]
    return out


def _layered(rows_top: "int | None") -> "tuple[dict[str, object], dict[str, object]]":
    """A description the layer wrote (the age column held: its block emptied, contract 4.6c.5) and the same run's
    description before the layer (the age's block top-coded at 90)."""
    person = {"name": "pid", "position": 1, "role": "identifier", "structural_role": "identifier"}
    emptied = {"name": "age", "position": 2, "role": "count", "top_coded": None, "mean": None, "quantiles": []}
    rows_block = {"name": "age", "position": 2, "role": "count", "top_coded": rows_top, "mean": 71.4}
    grain = {"classes": [{"class": "person", "column": "pid"}, {"class": "held", "column": "age"}]}
    published = {"columns": [person, emptied], "settings": {"person_columns": ["pid"]},
                 "relationships": {"grain": grain}}
    return published, {"columns": [person, rows_block], "settings": {"person_columns": ["pid"]}}


def test_a_column_the_layer_holds_keeps_its_age_top_code_in_the_record() -> None:
    """Codex's review of batch 4y, item 1: the layer empties a held column's block, so the record read no top code and
    the writer drew 91 to 105 from the record's model; the record now reads a held column's holds off the rows'
    description, and the drawn column writes no age past 90 (mutant: `record_document` gives the layered description
    back as it is)."""
    published, rows_described = _layered(90)
    assert R.specs_of(published)[1].top == 0
    held = R.specs_of(R.record_document(published, rows_described))
    assert held[1].kind == R.NUMBER and held[1].top == 90
    assert R.record_document({"columns": [], "relationships": {}}, rows_described) == {"columns": [],
                                                                                      "relationships": {}}
    columns = _ages_held_once_a_person(1000, 1)
    rows = len(columns["pid"])
    persons = R.persons_of(columns["pid"])
    sample = R.sample_rows(rows, persons=persons)
    found = R.encode(held[1], columns["age"], sample, persons)
    assert found is not None
    zone = R.fit_zone([found], len(sample), rows, [persons.person[row] for row in sample], "pid")
    profile = types.SimpleNamespace(n_rows=rows, columns=[types.SimpleNamespace(name=name, facts=None)
                                                          for name in ("pid", "age")])
    kept = {"pid": twinstore.held_column(columns["pid"]), "age": twinstore.held_column(["" for _row in range(rows)])}
    drawn = twinstore.column_cells(R.draw_columns(zone, profile, kept, 7)["age"])  # type: ignore[arg-type]
    filled = [float(cell) for cell in drawn if cell.strip()]
    assert len(filled) > 0.9 * rows
    assert max(filled) <= 90.0, sum(1 for value in filled if value > 90.0)


def test_a_value_column_typed_by_a_key_moves_with_its_key_in_the_walk() -> None:
    """The batch 4y landing's keyed long table: the walk deals the key column as a row family's child, and a value
    column published key by key (no family deals it) now moves with it, so each level's values stay on its rows
    (mutants: `_followers` naming no column; `_following` leaving the cells where they stood). Through the commands
    on the review table: tests/test_inside_keyed.py::test_items_1_2_5_6_through_the_commands."""
    from synthtwin import patient_walk

    assert patient_walk._following(["a1", "b1", "a2", "c1"], ["A", "B", "A", "C"],
                                   ["B", "C", "A", "A"]) == ["b1", "c1", "a1", "a2"]
    assert patient_walk._following(["a1", "b1"], ["A", "B"], ["A", "A"]) is None
    columns = [types.SimpleNamespace(name=name, keyed_by=by) for name, by in
               (("pid", ""), ("measure", ""), ("value", "measure"), ("dose", "drug"), ("drug", ""), ("note", "pid"))]
    grain = types.SimpleNamespace(
        classes=(("pid", "person"), ("measure", "repeated"), ("value", "ineligible"), ("drug", "repeated"),
                 ("dose", "repeated"), ("note", "held")),
        rows=(types.SimpleNamespace(child="measure"), types.SimpleNamespace(child="dose")), trajectory=(), trend=())
    profile = types.SimpleNamespace(columns=columns)
    # The dose is a family's child (the walk deals it), the note's key is the person: neither follows.
    assert patient_walk._followers(profile, grain) == {"value": "measure"}  # type: ignore[arg-type]

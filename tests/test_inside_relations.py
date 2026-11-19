"""Gate file of lane IN-2 (plan P4-D496): the inside record's relations zone, fitted and drawn.

WHAT IT HOLDS THE ZONE TO, each clause red on its mutant (lane IN-2's report):

* An interaction of two yes/no columns enters the response it moves, as
  a product term, not folded into main effects (mutant: no interaction
  block is offered).
* A curved effect enters as a curve block, the restricted cubic spline
  of the parent's normal score (mutant: no curve block is offered).
* Columns drawn on their own streams stay unrelated: no parent passes
  the chi-square gate at 0.001 (mutant: the gate reads nought).
* A number whose lowest value most rows hold is a spike, a state of its
  own whose share the columns before it move (mutant: no spike is ever
  read).
* The zone is a model, never data: no list in it is longer than its
  quantile grid, and doubling the rows moves its size by under 10 per
  cent (mutant: the grid keeps every value).
* An age drawn from the zone is never written above its Safe Harbor top
  code of 90 (mutant: the top code is not read at the draw).
* A label drawn from the zone writes a spelling the description does not
  publish nowhere: that cell is left to the description's own twin
  (mutant: the published spellings are not read at the draw).
* Where a person column repeats, a column one value a person is drawn
  once a person, a number counting a person's rows is written as the
  row's place, and a number's residual keeps a person's share (mutants:
  every column read as varying by row; the person's share read as
  nought).
* The fit and the draw are fixed functions of their inputs.

Every table here is drawn by the standard library's `random` from a
seed, at run time; nothing is committed.
"""

from __future__ import annotations

import json
import math
import random
import types

from synthtwin import chain_walk, contract, inside_relations as R, twinstore

KINDS_NUMBER = R.NUMBER
KINDS_LABEL = R.LABEL


def _zone(columns: "dict[str, list[str]]", kinds: "dict[str, str]", person: str = "") -> "dict[str, object]":
    """The relations zone of an invented table, its labels' every spelling published, `age` top-coded at 90."""
    names = list(columns)
    rows = len(columns[names[0]])
    persons = R.persons_of(columns[person]) if person else None
    if persons is not None and not persons.repeats:
        persons = None
    sample = R.sample_rows(rows, persons=persons)
    encoded = []
    for place, name in enumerate(names):
        kind = kinds.get(name, "")
        spellings = tuple(sorted(set(columns[name]))) if kind == KINDS_LABEL else ()
        why = "" if kind else (R.NAMES_THE_PERSON if name == person else "kept here")
        spec = R.ColumnSpec(name, place, kind, 90 if name == "age" else 0, spellings, why)
        found = R.encode(spec, columns[name], sample, persons)
        if found is not None:
            encoded.append(found)
    owners = [persons.person[row] for row in sample] if persons is not None else None
    return R.fit_zone(encoded, len(sample), rows, owners, person if persons is not None else "")


def _entry(zone: "dict[str, object]", name: str) -> "dict[str, object]":
    for entry in zone["columns"]:  # type: ignore[union-attr]
        if entry["name"] == name:
            return entry
    raise AssertionError(f"no entry for {name}")


def _terms(zone: "dict[str, object]", name: str, model: str = "value") -> "list[object]":
    return [term for term in _entry(zone, name)[model]["terms"] if term != ["one"]]  # type: ignore[index]


def _yes(flag: bool) -> str:
    return "Y" if flag else "N"


def _logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def _interaction_table(rows: int, seed: int) -> "dict[str, list[str]]":
    r = random.Random(f"interaction-{seed}")
    out: "dict[str, list[str]]" = {"a": [], "b": [], "x": [], "y": []}
    for _ in range(rows):
        a, b = r.random() < 0.5, r.random() < 0.4
        x = r.gauss(0.0, 1.0)
        y = r.random() < _logistic(-1.6 + 0.2 * a + 0.2 * b + 1.8 * (a and b) + 0.3 * x)
        out["a"] += [_yes(a)]
        out["b"] += [_yes(b)]
        out["x"] += [f"{x:.3f}"]
        out["y"] += [_yes(y)]
    return out


KINDS = {"a": KINDS_LABEL, "b": KINDS_LABEL, "x": KINDS_NUMBER, "y": KINDS_LABEL}


def test_an_interaction_of_two_yes_no_columns_enters_as_a_product() -> None:
    zone = _zone(_interaction_table(3000, 1), KINDS)
    products = [term for term in _terms(zone, "y") if term[0] == "prod"]  # type: ignore[index]
    named = [json.dumps(term) for term in products]
    assert any('"a"' in text and '"b"' in text for text in named), named


def test_a_curved_effect_enters_as_a_curve_block() -> None:
    r = random.Random("curve")
    columns: "dict[str, list[str]]" = {"x": [], "y": []}
    for _ in range(3000):
        x = r.gauss(0.0, 1.0)
        columns["x"] += [f"{x:.3f}"]
        columns["y"] += [f"{x * x + 0.4 * r.gauss(0.0, 1.0):.3f}"]
    zone = _zone(columns, {"x": KINDS_NUMBER, "y": KINDS_NUMBER})
    assert ["s", "x", 0] in _terms(zone, "y")


def test_columns_drawn_on_their_own_streams_stay_unrelated() -> None:
    r = random.Random("unrelated")
    columns: "dict[str, list[str]]" = {"g": [], "h": [], "u": [], "v": [], "w": []}
    for _ in range(3000):
        columns["g"] += [r.choice(("north", "south", "east"))]
        columns["h"] += [_yes(r.random() < 0.3)]
        columns["u"] += [f"{r.gauss(50.0, 10.0):.1f}"]
        columns["v"] += [f"{r.expovariate(0.2):.2f}"]
        columns["w"] += [f"{r.randint(0, 9)}"]
    zone = _zone(columns, {"g": KINDS_LABEL, "h": KINDS_LABEL, "u": KINDS_NUMBER, "v": KINDS_NUMBER,
                           "w": KINDS_NUMBER})
    for name in columns:
        assert _terms(zone, name) == [], name


def test_a_value_most_rows_hold_at_the_low_end_is_a_spike_its_parents_move() -> None:
    r = random.Random("spike")
    columns: "dict[str, list[str]]" = {"arm": [], "loss": []}
    for _ in range(3000):
        second = r.random() < 0.5
        zero = r.random() < (0.75 if second else 0.45)
        columns["arm"] += ["B" if second else "A"]
        columns["loss"] += ["0" if zero else f"{int(math.exp(r.gauss(5.0, 1.0)))}"]
    zone = _zone(columns, {"arm": KINDS_LABEL, "loss": KINDS_NUMBER})
    entry = _entry(zone, "loss")
    assert entry["spikes"][0] == [0.0, "0"]  # type: ignore[index]
    assert any(term[0] == "level" and term[1] == "arm" for term in _terms(zone, "loss", "presence"))  # type: ignore[index]


def _lists(value: object) -> "list[int]":
    if isinstance(value, list):
        return [len(value)] + [size for each in value for size in _lists(each)]
    if isinstance(value, dict):
        return [size for each in value.values() for size in _lists(each)]
    return []


def test_the_zone_is_a_model_whose_size_holds_as_the_rows_double() -> None:
    small = _zone(_interaction_table(3000, 2), KINDS)
    large = _zone(_interaction_table(6000, 2), KINDS)
    assert max(_lists(small)) <= R.GRID and max(_lists(large)) <= R.GRID
    grown = len(json.dumps(large)) / len(json.dumps(small))
    assert grown < 1.10, grown


def _number_entry(grid: "list[float]", top: int) -> "dict[str, object]":
    return {"name": "age", "place": 0, "kind": R.NUMBER, "level": R.ROW, "grid": grid, "decimals": 0, "atoms": [],
            "spikes": [None, None], "top": top, "states": [1000, 0, 0, 0, 0], "presence": None,
            "value": {"terms": [["one"]], "coefficients": [0.0], "spread": 1.0,
                      "residuals": [chain_walk.normal_score((2 * k + 1) / (2 * R.RESIDUAL_POINTS))
                                    for k in range(R.RESIDUAL_POINTS)]}}


def _words(count: int, seed: int) -> "list[int]":
    r = random.Random(f"words-{seed}")
    return [r.getrandbits(64) for _ in range(count)]


def test_an_age_drawn_from_the_zone_is_never_written_above_ninety() -> None:
    grid = [40.0 + 60.0 * k / (R.GRID - 1) for k in range(R.GRID)]
    drawn = R.draw_number(_number_entry(grid, 90), {}, 1000, _words(2000, 1))
    ages = [float(cell) for cell in drawn.cells if cell]
    assert max(ages) == 90.0
    assert len([age for age in ages if age == 90.0]) > 100


def test_a_label_writes_only_spellings_the_description_publishes() -> None:
    entry = {"name": "unit", "place": 0, "kind": R.LABEL, "level": R.ROW, "levels": ["kept", "unpublished"],
             "counts": [600, 400], "rest": 0,
             "value": {"terms": [["one"]], "coefficients": [None, [0.0]]}}
    drawn = R.draw_label(entry, {}, 500, _words(500, 2), {"kept"})
    assert set(drawn.cells) == {"kept", None}
    filled = R._filled(drawn.cells, ["stand-in"])
    assert set(filled) == {"kept", "stand-in"}


def _visit_table(persons: int, seed: int) -> "dict[str, list[str]]":
    r = random.Random(f"visits-{seed}")
    out: "dict[str, list[str]]" = {"pid": [], "arm": [], "visit": [], "pressure": []}
    for k in range(persons):
        arm = r.random() < 0.5
        own = r.gauss(0.0, 10.0)
        for visit in range(1, r.randint(2, 8) + 1):
            out["pid"] += [f"Q{100000 + 3 * k}"]
            out["arm"] += ["B" if arm else "A"]
            out["visit"] += [f"{visit}"]
            out["pressure"] += [f"{130.0 + 6.0 * arm - 0.5 * visit + own + r.gauss(0.0, 8.0):.0f}"]
    return out


def _person_profile(columns: "dict[str, list[str]]") -> object:
    """A stand-in for a loaded description: its rows and each label's published spellings (all of them here)."""
    blocks = []
    for name, cells in columns.items():
        counts: "dict[str, int]" = {}
        for cell in cells:
            counts[cell] = counts.get(cell, 0) + 1
        levels = tuple(contract.LevelEntry(label, count, {label: count}, {}, 0) for label, count in counts.items())
        facts = contract.LabelFacts(levels, 0, 0, {}, contract.PooledNumbers(0, None))
        blocks.append(types.SimpleNamespace(name=name, facts=facts))
    return types.SimpleNamespace(n_rows=len(columns["pid"]), columns=blocks)


def _icc(groups: "dict[str, list[float]]") -> float:
    values = [v for vs in groups.values() for v in vs]
    grand = sum(values) / len(values)
    within = sum((v - sum(vs) / len(vs)) ** 2 for vs in groups.values() for v in vs) / (len(values) - len(groups))
    sizes = [len(vs) for vs in groups.values()]
    between = sum(len(vs) * (sum(vs) / len(vs) - grand) ** 2 for vs in groups.values()) / (len(groups) - 1)
    typical = (len(values) - sum(s * s for s in sizes) / len(values)) / (len(groups) - 1)
    share = max(0.0, (between - within) / typical)
    return share / (share + within)


def test_a_person_s_columns_are_drawn_once_a_person_and_the_rows_keep_a_person_s_share() -> None:
    columns = _visit_table(600, 1)
    zone = _zone(columns, {"arm": KINDS_LABEL, "visit": KINDS_NUMBER, "pressure": KINDS_NUMBER}, person="pid")
    assert _entry(zone, "arm")["level"] == R.PATIENT
    assert _entry(zone, "visit")["level"] == R.SEQUENCE
    assert _entry(zone, "pressure")["value"]["person_spread"] > 0.3  # type: ignore[index]
    twin_persons = _visit_table(600, 2)["pid"]
    strict = {"pid": twin_persons, "arm": ["A"] * len(twin_persons), "visit": ["1"] * len(twin_persons),
              "pressure": ["0"] * len(twin_persons)}
    profile = _person_profile({**columns, "pid": twin_persons})
    profile.n_rows = len(twin_persons)  # type: ignore[attr-defined]
    zone["rows"] = len(twin_persons)
    held = {name: twinstore.held_column(cells) for name, cells in strict.items()}
    drawn = {name: twinstore.column_cells(column)
             for name, column in R.draw_columns(zone, profile, held, 7).items()}  # type: ignore[arg-type]
    arms: "dict[str, set[str]]" = {}
    places: "dict[str, int]" = {}
    pressures: "dict[str, list[float]]" = {}
    for pid, arm, visit, pressure in zip(twin_persons, drawn["arm"], drawn["visit"], drawn["pressure"]):
        arms.setdefault(pid, set()).add(arm)
        places[pid] = places.get(pid, 0) + 1
        assert visit == f"{places[pid]}"
        pressures.setdefault(pid, []).append(float(pressure))
    assert all(len(held) == 1 for held in arms.values())
    real: "dict[str, list[float]]" = {}
    for pid, pressure in zip(columns["pid"], columns["pressure"]):
        real.setdefault(pid, []).append(float(pressure))
    assert _icc(pressures) > 0.5 * _icc(real), (_icc(pressures), _icc(real))


def test_the_fit_and_the_draw_are_fixed_functions_of_their_inputs() -> None:
    first = _zone(_interaction_table(2000, 3), KINDS)
    second = _zone(_interaction_table(2000, 3), KINDS)
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    grid = [float(k) for k in range(R.GRID)]
    once = R.draw_number(_number_entry(grid, 0), {}, 300, _words(600, 4)).cells
    again = R.draw_number(_number_entry(grid, 0), {}, 300, _words(600, 4)).cells
    assert once == again


def test_a_record_s_digest_is_fnv_one_a_of_its_bytes() -> None:
    assert R.digest_of(b"") == "cbf29ce484222325"
    assert R.digest_of(b"a") == "af63dc4c8601ec8c"

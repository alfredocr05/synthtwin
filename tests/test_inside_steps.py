"""Gate file of lane STATS-C: a label that changes at a threshold of a number, in the inside record's relations zone.

THE CLASS. A label's fit was offered each number parent's straight score and its smooth curve, whose knots stand at
fixed shares, so a step -- more patients dying past 65, a complication above a creatinine of 1.3 -- came back
flattened: on K-S6-01's table the shipped route's twin drew the old-young difference in the share who died 0.37 to
0.38 against the real 0.49. A label's fit is now offered each number parent's STEPS too (`inside_relations._band_block`: whether the
number stands at or above each of its tenths), and they enter as any extra does, by their statistic at the gate.

WHAT IT HOLDS, each clause red on its mutant (lane STATS-C's report):

* A label that steps at a threshold of a number takes the number's steps, and the twin keeps the difference across
  the threshold (mutant: no steps offered).
* A label that moves smoothly with a number keeps the twin's difference across any cut as the real table's, and no
  steps are taken where the gate does not pass them (the twin's difference within the same bound).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import math
import random
import types

from synthtwin import contract, inside_relations as R, twinstore


def _table(rows: int, seed: int, stepped: bool) -> "dict[str, list[str]]":
    """K-S6-01's recipe (an age, a pressure from it, a group; died by age), dying a step at 65 or a smooth curve."""
    r = random.Random(f"steps-{seed}")
    out: "dict[str, list[str]]" = {"age": [], "sbp": [], "group": [], "died": []}
    for _ in range(rows):
        age = r.gauss(55, 12)
        sbp = 100 + 0.8 * age + r.gauss(0, 8)
        group = r.choice("FM")
        if stepped:
            chance = 0.6 if age > 65 else 0.1
        else:
            chance = 1.0 / (1.0 + math.exp(-(-2.2 + 0.06 * (age - 55))))
        out["age"] += [f"{age:.0f}"]
        out["sbp"] += [f"{sbp:.0f}"]
        out["group"] += [group]
        out["died"] += ["yes" if r.random() < chance else "no"]
    return out


KINDS = {"age": R.NUMBER, "sbp": R.NUMBER, "group": R.LABEL, "died": R.LABEL}


def _zone(columns: "dict[str, list[str]]") -> "dict[str, object]":
    rows = len(columns["age"])
    sample = R.sample_rows(rows)
    encoded = []
    for place, name in enumerate(columns):
        kind = KINDS[name]
        spellings = tuple(sorted(set(columns[name]))) if kind == R.LABEL else ()
        found = R.encode(R.ColumnSpec(name, place, kind, 0, spellings, ""), columns[name], sample, None)
        if found is not None:
            encoded.append(found)
    return R.fit_zone(encoded, len(sample), rows)


def _profile(columns: "dict[str, list[str]]") -> object:
    blocks = []
    for name, cells in columns.items():
        counts: "dict[str, int]" = {}
        for cell in cells:
            counts[cell] = counts.get(cell, 0) + 1
        levels = tuple(contract.LevelEntry(label, count, {label: count}, {}, 0) for label, count in counts.items())
        facts = contract.LabelFacts(levels, 0, 0, {}, contract.PooledNumbers(0, None))
        blocks.append(types.SimpleNamespace(name=name, facts=facts))
    return types.SimpleNamespace(n_rows=len(columns["age"]), columns=blocks)


def _twin(columns: "dict[str, list[str]]", zone: "dict[str, object]", seed: int) -> "dict[str, list[str]]":
    shuffle = random.Random(f"strict-{seed}")
    strict: "dict[str, list[str]]" = {}
    for name, cells in columns.items():
        mixed = list(cells)
        shuffle.shuffle(mixed)
        strict[name] = mixed
    held = {name: twinstore.held_column(cells) for name, cells in strict.items()}
    drawn = R.draw_columns(zone, _profile(columns), held, seed)  # type: ignore[arg-type]
    return {name: twinstore.column_cells(column) for name, column in drawn.items()}


def _old_young(columns: "dict[str, list[str]]") -> float:
    old = [died == "yes" for age, died in zip(columns["age"], columns["died"]) if float(age) > 65]
    young = [died == "yes" for age, died in zip(columns["age"], columns["died"]) if float(age) <= 65]
    return sum(old) / len(old) - sum(young) / len(young)


def _steps_taken(zone: "dict[str, object]", name: str) -> bool:
    for entry in zone["columns"]:  # type: ignore[union-attr]
        if entry["name"] == name:
            return any(isinstance(term, list) and term[:1] == ["band"] for term in entry["value"]["terms"])
    raise AssertionError(name)


def test_a_label_that_steps_at_a_threshold_takes_the_number_s_steps_and_the_twin_keeps_the_difference() -> None:
    columns = _table(8000, 1, stepped=True)
    zone = _zone(columns)
    assert _steps_taken(zone, "died")
    real = _old_young(columns)
    for seed in (4, 5):
        twin = _old_young(_twin(columns, zone, seed))
        assert abs(twin - real) < 0.05, (twin, real)


def test_a_label_that_moves_smoothly_keeps_its_difference_across_a_cut() -> None:
    columns = _table(8000, 2, stepped=False)
    zone = _zone(columns)
    real = _old_young(columns)
    for seed in (4, 5):
        twin = _old_young(_twin(columns, zone, seed))
        assert abs(twin - real) < 0.05, (twin, real)

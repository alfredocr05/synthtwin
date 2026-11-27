"""Gate file of lane STATS-D: a label of many levels as a parent in the inside record's relations zone.

THE CLASS. A label parent enters a fit as one indicator a level but its commonest. At most 24 indicators were made,
so a label of the zone's 30 modelled levels -- the battery's operations table's thirty surgeons -- folded its five
rarest into its commonest: the twin's spread of the surgeons' effects on an operation's minutes came back 13.6 to 13.8
against a real 14.5 (a fresh sample's 14.3 to 14.6), and the crossed mixed model of the minutes missed it on every
twin. `inside_relations.INDICATOR_CAP` is now every modelled level but the commonest.

WHAT IT HOLDS, red on its mutant (lane STATS-D's report): with 30 surgeons of unequal size, the rarest five holding
the largest effects, each surgeon's mean minutes in the twin stands within a fifth of the minutes' spread of the real
table's (mutant: `INDICATOR_CAP` 24, as before the lane).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import random
import statistics

from synthtwin import inside_relations as R, twinstore

import test_inside_rates as rates

KINDS = {"age": R.NUMBER, "surgeon": R.LABEL, "minutes": R.NUMBER}


def _operations(rows: int, seed: int) -> "dict[str, list[str]]":
    r = random.Random(f"levels-{seed}")
    weights = [1.0 / (k + 1) ** 0.5 for k in range(30)]
    # the five rarest surgeons hold the largest effects, so folding them into the commonest moves them most
    effects = [8.0 * ((k % 5) - 2) for k in range(25)] + [40.0, -40.0, 35.0, -35.0, 30.0]
    out: "dict[str, list[str]]" = {"age": [], "surgeon": [], "minutes": []}
    for _ in range(rows):
        surgeon = r.choices(range(30), weights)[0]
        age = int(min(90.0, max(18.0, r.gauss(60.0, 14.0))))
        out["age"] += [f"{age}"]
        out["surgeon"] += [f"S{surgeon + 1:02d}"]
        out["minutes"] += [f"{max(20, int(round(110.0 + 0.4 * (age - 60) + effects[surgeon] + r.gauss(0.0, 20.0))))}"]
    return out


def _twin(columns: "dict[str, list[str]]", seed: int) -> "dict[str, list[str]]":
    encoded, sample = rates._encoded(columns, KINDS)
    zone = R.fit_zone(encoded, len(sample), len(sample))
    shuffle = random.Random(f"strict-{seed}")
    held = {}
    for name, cells in columns.items():
        mixed = list(cells)
        shuffle.shuffle(mixed)
        held[name] = twinstore.held_column(mixed)
    drawn = R.draw_columns(zone, rates._profile(columns), held, seed)  # type: ignore[arg-type]
    return {name: twinstore.column_cells(column) for name, column in drawn.items()}


def _means(columns: "dict[str, list[str]]") -> "dict[str, float]":
    by: "dict[str, list[float]]" = {}
    for surgeon, minutes in zip(columns["surgeon"], columns["minutes"]):
        by.setdefault(surgeon, []).append(float(minutes))
    return {surgeon: statistics.mean(values) for surgeon, values in by.items()}


def test_every_level_of_a_thirty_level_parent_keeps_its_effect() -> None:
    columns = _operations(12000, 1)
    real = _means(columns)
    assert len(real) == 30
    spread = statistics.stdev(float(m) for m in columns["minutes"])
    twin = _means(_twin(columns, 0))
    worst = max(abs(twin[s] - real[s]) for s in real)
    assert worst < 0.2 * spread, (worst, spread)

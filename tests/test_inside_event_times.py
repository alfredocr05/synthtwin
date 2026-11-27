"""Gate file of lane STATS-D: the time of an event, read on its hazard's scale in the inside record's relations zone.

THE CLASS. The relations zone fits each number on its normal scores by a shift of the linear predictor and one
residual shape, and a shift of a normal score cannot carry a hazard ratio: on the battery's cohort, keeping the real
table's own outcomes and columns and drawing only the days followed again from such a fit read the complication's log
hazard ratio 0.635 against 0.767, and every twin read it 0.06 to 0.07 short. `inside_relations.event_times` reads a
positive number as an event's time where a two-level label next to it (either side) has its event rows' times
shorter, and its response is then its cumulative hazard's logarithm (`hazard_scores`), on which a shift is a
proportional change of hazard.

WHAT IT HOLDS, each clause red on its mutant (lane STATS-D's report):

* The cohort's days followed are an event's time beside the death; a number beside a label whose event rows hold it
  LONGER is not, nor a number of decimals (mutants: the sign of the difference not read; the whole units not read).
* A score is log(-log(1 - share)) at the row's mid-rank share, ties one score (mutant: the normal score kept).
* The twin drawn from the zone alone keeps the complication's log hazard ratio of the death within 0.05 of the real
  table's on average over three twins, where the normal scores read it 0.07 short (mutant: no number read as an
  event's time).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import csv
import io
import math
import random
import types

import pytest

import reliability_tables as T
from synthtwin import chain_walk, contract, inside_relations as R, twinstore


def _columns(rows: int, seed: int) -> "dict[str, list[str]]":
    table = list(csv.reader(io.StringIO(T.text("T1", rows, seed))))
    return {name: [row[i] for row in table[1:]] for i, name in enumerate(table[0])}


def _encoded(columns: "dict[str, list[str]]") -> "tuple[list[R.Encoded], list[int]]":
    sample = R.sample_rows(len(columns["age"]))
    out = []
    for place, name in enumerate(columns):
        if place < 2:
            continue  # the cohort's first two columns: the person's key and the day of admission
        filled = [cell for cell in columns[name] if cell.strip()]
        numeric = sum(1 for cell in filled if R.number_of(cell) is not None)
        kind = R.NUMBER if filled and numeric >= 0.9 * len(filled) else R.LABEL
        if T.KNOWS["T1"].get(name) == "code" or len(set(filled)) <= 2:
            kind = R.LABEL
        spellings = tuple(sorted(set(columns[name]))) if kind == R.LABEL else ()
        found = R.encode(R.ColumnSpec(name, place, kind, 90 if name == "age" else 0, spellings, ""), columns[name],
                         sample, None)
        if found is not None:
            out.append(found)
    return out, sample


def test_the_days_followed_beside_a_death_are_an_event_s_time_and_others_are_not() -> None:
    columns = _columns(6000, 1)
    encoded, _sample = _encoded(columns)
    assert R.event_times(encoded) == {"fu_days"}
    # the death's levels flipped in meaning: the "event" rows now hold LONGER times
    flipped = dict(columns, died=["0" if cell == "1" else "1" for cell in columns["died"]])
    encoded, _sample = _encoded(flipped)
    assert "fu_days" not in R.event_times(encoded)
    # a number of decimals beside the death (the stay, its rows longer where the patient died, here shorter) is not
    shorter = dict(columns, died=["1" if float(stay) < 3.0 else "0" for stay in columns["stay_days"]])
    encoded, _sample = _encoded(shorter)
    assert "stay_days" not in R.event_times(encoded)


def test_a_hazard_score_is_the_log_of_the_cumulative_hazard_at_the_mid_rank() -> None:
    positions = [5.0, 1.0, 3.0, 3.0, 9.0]
    states = [R.PRESENT, R.PRESENT, R.PRESENT, R.PRESENT, R.EMPTY]
    scores = R.hazard_scores(states, positions)
    shares = {1.0: 0.5 / 4, 3.0: 2.0 / 4, 5.0: 3.5 / 4}
    for at in range(4):
        want = chain_walk.natural_log(-chain_walk.natural_log(1.0 - shares[positions[at]]))
        assert abs(scores[at] - want) < 1e-12, (at, scores[at], want)
    assert scores[4] == 0.0
    assert scores[2] == scores[3]


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


def _complication_log_hazard_ratio(columns: "dict[str, list[str]]") -> float:
    pandas = pytest.importorskip("pandas")
    smf = pytest.importorskip("statsmodels.formula.api")
    data = pandas.DataFrame({
        "time": [float(cell) for cell in columns["fu_days"]],
        "c": [1 if cell == "Y" else 0 for cell in columns["complication"]],
        "a": [(float(cell) - 57) / 10 for cell in columns["age"]],
        "r": [float(cell) for cell in columns["risk_class"]],
        "d": [1 if cell == "Y" else 0 for cell in columns["diabetes"]],
    })
    numpy = pytest.importorskip("numpy")
    status = numpy.asarray([int(cell) for cell in columns["died"]])
    fit = smf.phreg("time ~ c + a + r + d", data=data, status=status, ties="breslow").fit()
    return float(fit.params[list(fit.model.exog_names).index("c")])


def test_the_twin_keeps_the_complication_s_hazard_ratio() -> None:
    columns = _columns(20000, 1)
    encoded, sample = _encoded(columns)
    zone = R.fit_zone(encoded, len(sample), len(sample))
    real = _complication_log_hazard_ratio(columns)
    found = []
    for seed in (0, 1, 2):
        shuffle = random.Random(f"strict-{seed}")
        held = {}
        for name, cells in columns.items():
            mixed = list(cells)
            shuffle.shuffle(mixed)
            held[name] = twinstore.held_column(mixed)
        drawn = R.draw_columns(zone, _profile(columns), held, seed)  # type: ignore[arg-type]
        twin = {name: twinstore.column_cells(column) for name, column in drawn.items()}
        found += [_complication_log_hazard_ratio(twin)]
    mean = math.fsum(found) / len(found)
    assert abs(mean - real) < 0.05, (found, real)

"""Gate file of lane STATS-D: a number of few values read on its latent scale, in the inside record's relations zone.

THE CLASS. The relations zone fits a number on its normal scores by least squares, and a number of few values -- a
count of admissions whose ones are half its rows, a score of nought to ten -- holds every tie at one score: least
squares on such coarse scores reads each parent's relation short, and the twin drawn on it flattened it. On the
battery's methods table the admissions of the patients with any grew with the days followed 1.47 to 2.09 (by fifth of
the days) against a real 1.30 to 2.17, so the counts after a short follow-up ran high (lane STATS-C's carried item).
`inside_relations._tied_refit` fits such a number's chosen terms again by maximum likelihood on the latent normal
scale its ties stand for (`tied_bands`, `interval_fit`).

WHAT IT HOLDS, each clause red on its mutant (lane STATS-D's report):

* A column of many values takes no bands; a count does, each value's rows one band whose ends are the normal
  quantiles of the shares below and through it (mutant: `TIED_SHARE` not read).
* `interval_fit` gives back a latent slope and spread a coarse reading hides, where least squares on the bands'
  mid-rank scores reads the slope short (mutant: the expected latent read as its band's middle).
* The twin drawn from the zone keeps how the admissions of the patients with any grow with the days followed: its
  shortest fifth's within 0.08 of the real table's and its growth from the shortest fifth to the longest within 15
  per cent (mutant: the latent fit not made, least squares as before the lane).

Every table here is drawn by the standard library's `random` from a seed, at run time; nothing is committed.
"""

from __future__ import annotations

import math
import random

from synthtwin import chain_walk, inside_relations as R

import test_inside_rates as rates


def test_a_count_takes_bands_and_a_number_of_many_values_none() -> None:
    r = random.Random(3)
    many = [chain_walk.normal_score((k + 0.5) / 500) for k in range(500)]
    assert R.tied_bands(many) is None
    values = [min(6, int(r.expovariate(0.9))) for _ in range(2000)]
    order = sorted(range(len(values)), key=lambda k: values[k])
    scores = [0.0] * len(values)
    start = 0
    while start < len(order):
        end = start
        while end + 1 < len(order) and values[order[end + 1]] == values[order[start]]:
            end += 1
        for at in range(start, end + 1):
            scores[order[at]] = chain_walk.normal_score((start + end + 1) / (2 * len(order)))
        start = end + 1
    bands = R.tied_bands(scores)
    assert bands is not None
    below = sum(1 for v in values if v < 1)
    through = sum(1 for v in values if v <= 1)
    one = next(k for k, v in enumerate(values) if v == 1)
    assert abs(bands[one][0] - chain_walk.normal_score(below / len(values))) < 1e-12
    assert abs(bands[one][1] - chain_walk.normal_score(through / len(values))) < 1e-12
    assert {bands[k] for k, v in enumerate(values) if v == 1} == {bands[one]}
    assert min(band[0] for band in bands) == -8.0 and max(band[1] for band in bands) == 8.0


def test_the_latent_fit_gives_back_the_slope_the_ties_hide() -> None:
    r = random.Random(11)
    rows = 6000
    x = [r.gauss(0.0, 1.0) for _ in range(rows)]
    latent = [0.5 * value + r.gauss(0.0, 0.8) for value in x]
    total = math.sqrt(0.25 + 0.64)
    cuts = [-0.3 * total, 0.4 * total, 1.2 * total]
    level = [sum(1 for cut in cuts if value > cut) for value in latent]
    shares = [sum(1 for v in level if v == k) / rows for k in range(4)]
    edges = [-8.0]
    running = 0.0
    for k in range(3):
        running += shares[k]
        edges += [chain_walk.normal_score(running)]
    edges += [8.0]
    bands = [(edges[k], edges[k + 1]) for k in level]
    middle = [chain_walk.normal_score((sum(shares[:k]) + 0.5 * shares[k])) for k in level]
    columns = [[1.0] * rows, x]
    plain = R.least_squares(columns, middle)
    beta, sigma = R.interval_fit(columns, bands, plain.beta, math.sqrt(plain.scale))
    # on the latent's own standardised scale the slope is 0.5 / total and the spread 0.8 / total
    assert abs(beta[1] - 0.5 / total) < 0.03, beta
    assert abs(sigma - 0.8 / total) < 0.03, sigma
    assert plain.beta[1] < 0.5 / total - 0.04, plain.beta


def _sizes(columns: "dict[str, list[str]]") -> "list[float]":
    """The mean admissions of the patients with any, by fifth of the days followed."""
    pairs = sorted((float(d), float(a)) for d, a in zip(columns["days"], columns["admissions"]) if float(a) > 0)
    fifth = len(pairs) // 5
    return [sum(a for _d, a in pairs[k * fifth:(k + 1) * fifth]) / fifth for k in range(5)]


def test_the_twin_keeps_how_the_counts_grow_with_the_days_followed() -> None:
    columns = rates._rate_table(8000, 4)
    real = _sizes(columns)
    assert real[4] - real[0] > 0.8, real
    for seed in (0, 1):
        found = _sizes(rates._twin(columns, seed))
        assert abs(found[0] - real[0]) < 0.08, (found, real)
        assert 0.85 < (found[4] - found[0]) / (real[4] - real[0]) < 1.15, (found, real)

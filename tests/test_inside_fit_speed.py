"""Gate file of lane SPEED-2M, part 2: the relations fit made faster, every number it makes the same bits.

THE LOGISTIC FIT. Each step of `inside_relations.logistic` takes the
predictor and each row's mean that the deviance of the last coefficients
taken already made (`_scored`), instead of making them again; a row whose
response is one or nought has its one logarithm worked out (the other
term is a minus nought, which leaves the sum as it is); and where the
predictor holds few different values (a fit on labels alone), each
value's mean and logarithms are worked out once. The coefficients,
weights, residuals and the information's factor are the as-built fit's,
bit for bit, on designs of labels, numbers, both, a near separation and a
single level (the as-built loop is frozen below). Mutants: the step's
predictor taken from before its halving; the one logarithm taken for the
other level; the table of few values keyed without its sign.

THE GRAM ON INDICATORS. `_gram` sums a product with a column of noughts
and ones over the rows holding a one alone (a product with nought is a
nought, which `math.fsum` passes over): the same matrix, bit for bit, as
the as-built sums over every row. Mutant: the rows holding a nought taken.

A NUMBER'S EXTRAS GROWN, NOT REMADE. A number target's least-squares steps
keep every sum of the design's columns, its response and each extra's
terms from the step before and make the new ones alone (`Grown`), each
over the rows that add: the zone of a dense table of the scale harness is
the as-built `select`'s zone (frozen below), bit for bit, with every
extra's values kept and with none kept. Mutants: an old sum read for a new
column pair; the negative rows left out of a column's nonzero rows.

THE LADDER'S STEP FOUND BY HALVING (generation). `generation._segment`
finds the step of a ladder a share falls in by halving instead of a scan
from nought: the scan's step on each kind of ladder the method knows, on a
ladder with a repeated percent, and at every edge (the share at a step's end,
past either end, a denominator of nought or less). Mutant: a share at a
step's lower end read in the step below.

Every design here is drawn by the standard library's `random` from a
seed, at run time; nothing is committed.
"""

from __future__ import annotations

import math
import pathlib
import random

import pytest

from synthtwin import chain_walk, inside_relations as R


# -- the as-built fit, frozen ---------------------------------------------------------------------------------------


def _built_dot(first: "list[float]", second: "list[float]") -> float:
    return math.fsum([a * b for a, b in zip(first, second)])


def _built_gram(columns: "list[list[float]]", weights: "list[float] | None") -> "list[list[float]]":
    size = len(columns)
    weighted = columns if weights is None else [[x * w for x, w in zip(column, weights)] for column in columns]
    out = [[0.0 for _b in range(size)] for _a in range(size)]
    for a in range(size):
        for b in range(a + 1):
            value = _built_dot(weighted[a], columns[b])
            out[a][b] = value
            out[b][a] = value
    return out


def _built_deviance(response: "list[float]", eta: "list[float]") -> float:
    terms: "list[float]" = []
    for y, e in zip(response, eta):
        mean = min(1.0 - 1e-15, max(1e-15, R.expit(e)))
        terms += [y * chain_walk.natural_log(mean) + (1.0 - y) * chain_walk.natural_log(1.0 - mean)]
    return -2.0 * math.fsum(terms)


# How many times the frozen fit halved a step (the case that must reach the halving reads it).
HALVED = [0]


def _built_logistic(columns: "list[list[float]]", response: "list[float]") -> R.Fit:
    rows = len(response)
    size = len(columns)
    share = math.fsum(response) / max(1, rows)
    beta = [0.0 for _a in range(size)]
    beta[0] = R._log_odds(share)
    lower: "list[list[float]]" = []
    dropped: "list[bool]" = []
    deviance = _built_deviance(response, R._predictor(columns, beta, rows))
    for _step in range(R._ITERATIONS):
        eta = R._predictor(columns, beta, rows)
        means = [R.expit(e) for e in eta]
        weights = [max(m * (1.0 - m), 1e-10) for m in means]
        working = [e + (y - m) / w for e, y, m, w in zip(eta, response, means, weights)]
        lower, dropped = R._cholesky(R._ridged(_built_gram(columns, weights)))
        weighted = [w * z for w, z in zip(weights, working)]
        moved = R._solve(lower, dropped, [0.0 if dropped[a] else _built_dot(columns[a], weighted) for a in range(size)])
        if not all([math.isfinite(value) for value in moved]):
            beta = moved
            break
        reached = _built_deviance(response, R._predictor(columns, moved, rows))
        halved = 0
        while not reached <= deviance + 1e-9 * (1.0 + abs(deviance)) and halved < R._HALVINGS:
            moved = [(a + b) / 2.0 for a, b in zip(moved, beta)]
            reached = _built_deviance(response, R._predictor(columns, moved, rows))
            halved += 1
            HALVED[0] += 1
        change = max([abs(a - b) for a, b in zip(moved, beta)]) if size else 0.0
        beta = moved
        deviance = reached
        if change < R._CHANGE:
            break
    if not all([math.isfinite(value) for value in beta]):
        beta = [0.0 for _a in range(size)]
        beta[0] = R._log_odds(share)
    eta = R._predictor(columns, beta, rows)
    means = [R.expit(e) for e in eta]
    weights = [max(m * (1.0 - m), 1e-10) for m in means]
    lower, dropped = R._cholesky(R._ridged(_built_gram(columns, weights)))
    return R.Fit(beta, weights, [y - m for y, m in zip(response, means)], lower, dropped, 1.0)


def _bits(values: object) -> str:
    """Every float of a nested value spelled exactly (`float.hex`, the sign of a nought kept)."""
    if isinstance(values, float):
        return values.hex()
    if isinstance(values, (list, tuple)):
        return "[" + ",".join(_bits(each) for each in values) + "]"
    return repr(values)


def _fit_bits(fit: R.Fit) -> str:
    return _bits([fit.beta, fit.weights, fit.residuals, fit.lower, [float(flag) for flag in fit.dropped], fit.scale])


# -- the designs ----------------------------------------------------------------------------------------------------


def _design(rows: int, seed: int, labels: int, numbers: int, separated: bool = False) -> "tuple[list[list[float]], list[float]]":
    r = random.Random(f"fit-speed-{seed}")
    columns: "list[list[float]]" = [[1.0 for _row in range(rows)]]
    for _k in range(labels):
        share = 0.1 + 0.6 * r.random()
        columns += [[1.0 if r.random() < share else 0.0 for _row in range(rows)]]
    for _k in range(numbers):
        columns += [[round(r.gauss(0.0, 1.0), 3) for _row in range(rows)]]
    response: "list[float]" = []
    for row in range(rows):
        eta = -0.4 + sum((0.7 - 0.3 * k) * columns[k][row] for k in range(1, len(columns)))
        if separated:
            response += [1.0 if columns[1][row] == 1.0 else (1.0 if r.random() < 0.02 else 0.0)]
        else:
            response += [1.0 if r.random() < 1.0 / (1.0 + math.exp(-eta)) else 0.0]
    return columns, response


CASES = {
    "labels-only": (3000, 1, 4, 0, False),
    "numbers-only": (3000, 2, 0, 3, False),
    "both": (4000, 3, 3, 2, False),
    "separated": (2000, 4, 2, 0, True),
    "intercept-only": (1500, 5, 0, 0, False),
    "interaction-of-labels": (3000, 6, 2, 0, False),
}


@pytest.mark.parametrize("name", sorted(CASES))
def test_the_logistic_fit_is_the_as_built_fit_bit_for_bit(name: str) -> None:
    rows, seed, labels, numbers, separated = CASES[name]
    columns, response = _design(rows, seed, labels, numbers, separated)
    if name == "interaction-of-labels":
        columns += [[a * b for a, b in zip(columns[1], columns[2])]]
    assert _fit_bits(R.logistic(columns, response)) == _fit_bits(_built_logistic(columns, response))


def test_a_fit_whose_step_is_halved_is_the_as_built_fit_bit_for_bit() -> None:
    # A table a number and a flag separate (every row above 0.3 or flagged holds the level): the first step from
    # the intercept alone overshoots and is halved.
    r = random.Random(179)
    rows = 600
    x = [round(r.gauss(0.0, 1.0), 3) for _row in range(rows)]
    f = [1.0 if r.random() < 0.1 else 0.0 for _row in range(rows)]
    response = [1.0 if (xi > 0.3 or fi) else 0.0 for xi, fi in zip(x, f)]
    columns = [[1.0 for _row in range(rows)], f, x]
    HALVED[0] = 0
    built = _fit_bits(_built_logistic(columns, response))
    assert HALVED[0] > 0, "the case no longer reaches the halving"
    assert _fit_bits(R.logistic(columns, response)) == built


def test_the_deviance_is_the_as_built_one_where_a_response_is_neither_one_nor_nought() -> None:
    r = random.Random("weights")
    eta = [r.gauss(0.0, 2.0) for _row in range(500)] + [0.0, -0.0, 40.0, -40.0]
    response = [r.choice([0.0, 1.0, 0.25, -0.0]) for _row in range(len(eta))]
    assert R._deviance(response, eta).hex() == _built_deviance(response, eta).hex()
    few = [r.choice([0.5, -1.25, 0.0, -0.0, 3.0]) for _row in range(800)]
    response = [r.choice([0.0, 1.0, 0.5]) for _row in range(len(few))]
    assert R._deviance(response, few).hex() == _built_deviance(response, few).hex()


def test_the_gram_on_indicators_is_the_as_built_gram_bit_for_bit() -> None:
    columns, _response = _design(3000, 7, 4, 3)
    columns += [[a * b for a, b in zip(columns[1], columns[2])], [a * b for a, b in zip(columns[1], columns[5])]]
    r = random.Random("gram-weights")
    weights = [max(1e-10, r.random() * 0.25) for _row in range(3000)]
    assert _bits(R._gram(columns, weights)) == _bits(_built_gram(columns, weights))
    assert _bits(R._gram(columns, None)) == _bits(_built_gram(columns, None))


# -- the screen and its extras: the as-built `select`, frozen, against the zone -------------------------------------


def _built_least_squares(columns: "list[list[float]]", response: "list[float]") -> R.Fit:
    rows = len(response)
    lower, dropped = R._cholesky(R._ridged(_built_gram(columns, None)))
    beta = R._solve(lower, dropped, [0.0 if dropped[a] else _built_dot(columns[a], response) for a in range(len(columns))])
    eta = R._predictor(columns, beta, rows)
    residuals = [y - e for y, e in zip(response, eta)]
    kept = len([flag for flag in dropped if not flag])
    scale = math.fsum([r * r for r in residuals]) / max(1, rows - kept)
    return R.Fit(beta, [1.0 for _row in range(rows)], residuals, lower, dropped, max(scale, 1e-12))


def _built_fits(target: R.Target, columns_of: "list[list[list[float]]]") -> "list[R.Fit | None]":
    if target.kind == R.NUMBER:
        return [_built_least_squares(columns_of[0], target.response)]
    out: "list[R.Fit | None]" = []
    for level in range(1, target.levels):
        columns = columns_of[level]
        if not columns or len(columns[0]) == 0:
            out += [None]
            continue
        response = [1.0 if target.codes[row] == level else 0.0 for row in R._label_rows(target, level)]
        if len([y for y in response if y > 0.5]) < R.MIN_ROWS or len([y for y in response if y < 0.5]) < R.MIN_ROWS:
            out += [None]
            continue
        out += [_built_logistic(columns, response)]
    return out


def _built_score_statistic(fit: R.Fit, columns: "list[list[float]]", block: "list[list[float]]") -> float:
    size = len(columns)
    width = len(block)
    if width == 0:
        return 0.0
    weighted_block = [[b * w for b, w in zip(term, fit.weights)] for term in block]
    score = [_built_dot(term, fit.residuals) for term in block]
    cross = [[0.0 if fit.dropped[a] else _built_dot(weighted_block[k], columns[a]) for a in range(size)]
             for k in range(width)]
    solved = [R._solve(fit.lower, fit.dropped, cross[k]) for k in range(width)]
    variance = [[0.0 for _b in range(width)] for _a in range(width)]
    for k in range(width):
        for m in range(k + 1):
            value = _built_dot(weighted_block[k], block[m]) - _built_dot(cross[k], solved[m])
            variance[k][m] = value
            variance[m][k] = value
    lower, dropped = R._cholesky(variance)
    if all(dropped):
        return 0.0
    solved_score = R._solve(lower, dropped, [0.0 if dropped[k] else score[k] for k in range(width)])
    statistic = _built_dot(score, solved_score) / fit.scale
    return statistic if statistic > 0.0 else 0.0


def _built_block_statistic(target: R.Target, fits: "list[R.Fit | None]", design: "list[list[list[float]]]",
                           block: R.Block, frames: "dict[str, R.Frame]", rows: int) -> "tuple[float, int]":
    indicators = R._indicators_of(block, frames, rows)
    if indicators is not None:
        codes, wanted = indicators
        if target.kind == R.NUMBER:
            fit = fits[0]
            if fit is None:
                return 0.0, 0
            if len(design[0]) == 1:
                return R.indicator_statistic(fit, codes, wanted, target.rows), len(wanted)
        elif all(len(design[level]) == 1 for level in range(1, target.levels) if fits[level - 1] is not None):
            total = 0.0
            freedom = 0
            for level in range(1, target.levels):
                fit = fits[level - 1]
                if fit is None:
                    continue
                total += R.indicator_statistic(fit, codes, wanted, R._label_rows(target, level))
                freedom += len(wanted)
            return total, freedom
    values = R._evaluated(block, frames, rows, None)
    total = 0.0
    freedom = 0
    if target.kind == R.NUMBER:
        fit = fits[0]
        if fit is None:
            return 0.0, 0
        return _built_score_statistic(fit, design[0], [[column[row] for row in target.rows] for column in values]), len(values)
    for level in range(1, target.levels):
        fit = fits[level - 1]
        if fit is None:
            continue
        keep = R._label_rows(target, level)
        total += _built_score_statistic(fit, design[level], [[column[row] for row in keep] for column in values])
        freedom += len(values)
    return total, freedom


def _built_select(target: R.Target, candidates: "list[R.Block]", frames: "dict[str, R.Frame]",
                  rows: int) -> "tuple[list[R.Block], list[R.Fit | None]]":
    chosen: "list[R.Block]" = []
    design = R._design(target, chosen, frames, rows)
    fits = _built_fits(target, design)
    ranked: "list[tuple[float, int]]" = []
    for place in range(len(candidates)):
        screened = candidates[place]
        curve = R._curve_block(screened.parent, frames[screened.parent])
        if curve is not None:
            screened = R.Block(screened.terms + curve.terms, screened.parent, "screen")
        statistic, freedom = _built_block_statistic(target, fits, design, screened, frames, rows)
        if freedom > 0 and statistic >= R.critical(freedom):
            ranked += [(-R._standardised(statistic, freedom), place)]
    for _negative, place in sorted(ranked)[:R.PARENT_CAP]:
        chosen += [candidates[place]]
    if chosen:
        design = R._design(target, chosen, frames, rows)
        fits = _built_fits(target, design)
    # Lane STATS-B's conditional pass as built (merged in batch 4zz after this lane froze `select`).
    if chosen and len(chosen) < R.PARENT_CAP:
        again: "list[tuple[float, int]]" = []
        taken = [False for _place in range(len(candidates))]
        for _negative, place in sorted(ranked)[:R.PARENT_CAP]:
            taken[place] = True
        cheap: "list[tuple[float, int]]" = []
        for place in range(len(candidates)):
            if not taken[place]:
                cheap += [(-R._residual_score(target, fits, candidates[place], frames, rows), place)]
        for _negative, place in sorted(cheap)[:R.CONDITIONAL_EXACT]:
            statistic, freedom = _built_block_statistic(target, fits, design, candidates[place], frames, rows)
            if freedom > 0 and statistic >= R.critical(freedom):
                again += [(-R._standardised(statistic, freedom), place)]
        if again:
            for _negative, place in sorted(again)[:R.PARENT_CAP - len(chosen)]:
                chosen += [candidates[place]]
            design = R._design(target, chosen, frames, rows)
            fits = _built_fits(target, design)
    extras: "list[R.Block]" = []
    for block in chosen:
        curve = R._curve_block(block.parent, frames[block.parent])
        if curve is not None:
            extras += [curve]
    if target.kind == R.LABEL and target.levels > R.EXTRA_LEVELS_CAP:
        return chosen, fits
    for a in range(len(chosen)):
        for b in range(a + 1, len(chosen)):
            first, second = chosen[a], chosen[b]
            if frames[first.parent].kind == R.NUMBER and frames[second.parent].kind == R.LABEL:
                first, second = second, first
            joined = R._interactions(first, second, frames)
            if joined is not None:
                extras += [joined]
    for _step in range(R.EXTRA_CAP):
        best = -math.inf
        best_place = -1
        for place in range(len(extras)):
            statistic, freedom = _built_block_statistic(target, fits, design, extras[place], frames, rows)
            if freedom > 0 and statistic >= R.critical(freedom) and R._standardised(statistic, freedom) > best:
                best = R._standardised(statistic, freedom)
                best_place = place
        if best_place < 0:
            break
        chosen += [extras[best_place]]
        extras = [extras[place] for place in range(len(extras)) if place != best_place]
        design = R._design(target, chosen, frames, rows)
        fits = _built_fits(target, design)
    return chosen, fits


def _dense_columns(rows: int, columns: int, folder: "pathlib.Path") -> "dict[str, list[str]]":
    """The scale harness's dense table of ``rows`` rows by ``columns`` columns, its columns as read."""
    import csv
    import sys

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
    import kpi_inside_scale

    table = pathlib.Path(folder, "dense.csv")
    kpi_inside_scale.write_dense(rows, columns, table)
    with open(table, newline="", encoding="utf-8") as handle:
        read = list(csv.reader(handle))
    return {name: [row[at] for row in read[1:]] for at, name in enumerate(read[0])}


def _dense_zone(table: "dict[str, list[str]]", monkeypatch: "pytest.MonkeyPatch | None") -> str:
    import json

    rows = len(table["pid"])
    persons = R.persons_of(table["pid"])
    sample = R.sample_rows(rows, persons=persons)
    encoded = []
    for place, name in enumerate(table):
        kind = R.LABEL if name[0] in "fg" and name[1:].isdigit() else (R.NUMBER if name[0] == "n" and name[1:].isdigit() else "")
        spellings = tuple(sorted(set(table[name]))) if kind == R.LABEL else ()
        why = "" if kind else (R.NAMES_THE_PERSON if name == "pid" else "kept here")
        found = R.encode(R.ColumnSpec(name, place, kind, 0, spellings, why), table[name], sample, persons)
        if found is not None:
            encoded.append(found)
    if monkeypatch is not None:
        monkeypatch.setattr(R, "select", _built_select)
    zone = R.fit_zone(encoded, len(sample), rows, [persons.person[row] for row in sample], "pid")
    return json.dumps(zone, sort_keys=True, separators=(",", ":"), allow_nan=False)


@pytest.mark.parametrize("kept_most", [R._GROWN_CELLS_MOST, 0])
def test_the_zone_of_a_dense_table_is_the_as_built_zone_bit_for_bit(tmp_path: pathlib.Path, kept_most: int,
                                                                   monkeypatch: "pytest.MonkeyPatch") -> None:
    # ...with every extra's values kept between the steps, and with none kept (each worked out again at each step).
    monkeypatch.setattr(R, "_GROWN_CELLS_MOST", kept_most)
    table = _dense_columns(4000, 24, tmp_path)
    made = _dense_zone(table, None)
    built = _dense_zone(table, monkeypatch)
    assert made == built


# -- the ladder's step, found by halving (generation) ---------------------------------------------------------------


def _built_segment(numerator: int, denominator: int, percents: "tuple[int, ...]") -> int:
    scaled = 100 * numerator
    last = len(percents) - 2
    for step in range(last + 1):
        below = percents[step] * denominator <= scaled
        if below and scaled < percents[step + 1] * denominator:
            return step
    return last


def test_the_step_of_a_ladder_found_by_halving_is_the_scans_step() -> None:
    from synthtwin import generation

    kinds = [tuple(percents) for percents in generation._PERCENTS_BY_LENGTH.values()]
    kinds += [(0, 1, 1, 5, 50, 50, 100), (0, 100)]
    r = random.Random("segment")
    checked = 0
    for percents in kinds:
        for denominator in [-3, 0, 1, 2, 7, 100, 1000, 999_983] + [r.randrange(1, 10 ** 9) for _k in range(20)]:
            numerators = [-1, 0, 1, denominator - 1, denominator, denominator + 1, 2 * denominator]
            numerators += [r.randrange(-5, max(6, denominator + 5)) for _k in range(200)]
            for numerator in numerators:
                assert generation._segment(numerator, denominator, percents) == _built_segment(
                    numerator, denominator, percents), (numerator, denominator, percents)
                checked += 1
    assert checked > 10_000

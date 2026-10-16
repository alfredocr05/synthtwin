"""The analyst battery's fitting kit, held to closed forms it shares no code with (plan P4-D398).

`tests/analyst_kit.py` fits every model the analyst battery asks of a
twin, in plain Python. A fitter that is only checked against itself is
its own witness, so each one here is held to an answer worked out
another way:

* least squares to the normal equations of a tiny design, solved by
  Cramer's rule, and to the textbook slope, intercept and standard
  errors of a straight line;
* logistic regression on one two-valued term to the log odds ratio of
  the 2 x 2 table and Woolf's standard error, sqrt(1/a + 1/b + 1/c + 1/d);
* Poisson regression with an exposure offset to the log rate ratio and
  its standard error, sqrt(1/Y1 + 1/Y0);
* the random-intercept model's ICC to the balanced one-way analysis of
  variance at maximum likelihood: se2 = SSW / (k (m - 1)),
  sb2 = (SSB / k - se2) / m;
* the AUC to the Mann-Whitney count over every pair, ties a half;
* Spearman's correlation to 1 - 6 sum d^2 / (n (n^2 - 1)) without ties,
  and to Pearson's on average ranks counted pair by pair with ties;
* Cox's model to a brute-force Breslow partial likelihood, its score
  zero and its information the numerical second derivative;
* the spline to Harrell's formula, linear past its outer knots;
* the chi-square tail to its closed forms at one and two degrees of
  freedom, and the Kaplan-Meier median to a hand count;
* and the fits a table cannot carry -- a separated outcome, a repeated
  term, no rows -- refused by name.

Every case is built here from fixed numbers or a seeded draw.
"""

from __future__ import annotations

import math
import random

import pytest

import analyst_kit as K


def _design(columns: "dict[str, list[float]]", names: "list[str]", intercept: bool = True) -> K.Design:
    terms: "list[tuple[str, K.Term]]" = [("int", K.intercept)] if intercept else []
    terms += [(n, (lambda c, n=n: list(c[n]))) for n in names]
    return K.Design(columns, terms)


def _det3(m: "list[list[float]]") -> float:
    return (m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0]))


def test_least_squares_solves_the_normal_equations_of_a_tiny_design() -> None:
    """Three terms, six rows: the coefficients are Cramer's rule on X'X b = X'y."""
    x1 = [0.0, 1.0, 2.0, 3.0, 4.0, 5.0]
    x2 = [1.0, 0.0, 1.0, 1.0, 0.0, 0.0]
    y = [1.1, 2.9, 5.2, 7.1, 8.8, 11.2]
    rows = [[1.0, a, b] for a, b in zip(x1, x2)]
    xtx = [[sum(r[i] * r[j] for r in rows) for j in range(3)] for i in range(3)]
    xty = [sum(r[i] * yi for r, yi in zip(rows, y)) for i in range(3)]
    det = _det3(xtx)
    expected = []
    for k in range(3):
        swapped = [[xty[i] if j == k else xtx[i][j] for j in range(3)] for i in range(3)]
        expected += [_det3(swapped) / det]
    fit = K.ols(_design({"x1": x1, "x2": x2}, ["x1", "x2"]), y)
    for got, want in zip(fit.beta, expected):
        assert got == pytest.approx(want, abs=1e-10)


def test_a_straight_line_has_the_textbook_slope_and_standard_errors() -> None:
    """Slope Sxy / Sxx, intercept ybar - b xbar, se(b) = s / sqrt(Sxx), se(a) = s sqrt(1/n + xbar^2/Sxx)."""
    r = random.Random(3)
    x = [r.uniform(0, 10) for _ in range(40)]
    y = [2.0 + 0.7 * v + r.gauss(0, 1.5) for v in x]
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    sxx = sum((v - mx) ** 2 for v in x)
    sxy = sum((v - mx) * (w - my) for v, w in zip(x, y))
    b = sxy / sxx
    a = my - b * mx
    s2 = sum((w - a - b * v) ** 2 for v, w in zip(x, y)) / (n - 2)
    fit = K.ols(_design({"x": x}, ["x"]), y)
    assert fit.coef("x")[0] == pytest.approx(b, rel=1e-10)
    assert fit.coef("int")[0] == pytest.approx(a, rel=1e-10)
    assert fit.coef("x")[1] == pytest.approx(math.sqrt(s2 / sxx), rel=1e-9)
    assert fit.coef("int")[1] == pytest.approx(math.sqrt(s2 * (1 / n + mx * mx / sxx)), rel=1e-9)


@pytest.mark.parametrize("cells", [(30, 70, 12, 88), (5, 45, 40, 410), (100, 100, 60, 140)])
def test_logistic_regression_on_one_flag_is_the_log_odds_ratio_of_its_2x2_table(cells: "tuple[int, int, int, int]") -> None:
    """beta = log(ad / bc), se = sqrt(1/a + 1/b + 1/c + 1/d); the intercept is the reference's log odds."""
    a, b, c, d = cells
    x = [1.0] * (a + b) + [0.0] * (c + d)
    y = [1.0] * a + [0.0] * b + [1.0] * c + [0.0] * d
    fit = K.glm(_design({"x": x}, ["x"]), y, "logistic")
    assert fit.coef("x")[0] == pytest.approx(math.log(a * d / (b * c)), abs=1e-7)
    assert fit.coef("x")[1] == pytest.approx(math.sqrt(1 / a + 1 / b + 1 / c + 1 / d), abs=1e-7)
    assert fit.coef("int")[0] == pytest.approx(math.log(c / d), abs=1e-7)


def test_poisson_regression_with_an_offset_is_the_log_rate_ratio() -> None:
    """Counts over exposures in two groups: beta = log((Y1/T1)/(Y0/T0)), se = sqrt(1/Y1 + 1/Y0)."""
    r = random.Random(5)
    group = [1.0] * 30 + [0.0] * 50
    exposure = [r.uniform(0.5, 3.0) for _ in group]
    counts = [float(r.randrange(0, 9)) for _ in group]
    y1 = sum(c for c, g in zip(counts, group) if g)
    y0 = sum(c for c, g in zip(counts, group) if not g)
    t1 = sum(e for e, g in zip(exposure, group) if g)
    t0 = sum(e for e, g in zip(exposure, group) if not g)
    fit = K.glm(_design({"g": group}, ["g"]), counts, "poisson", offset=[math.log(e) for e in exposure])
    assert fit.coef("g")[0] == pytest.approx(math.log((y1 / t1) / (y0 / t0)), abs=1e-8)
    assert fit.coef("g")[1] == pytest.approx(math.sqrt(1 / y1 + 1 / y0), abs=1e-8)
    assert fit.coef("int")[0] == pytest.approx(math.log(y0 / t0), abs=1e-8)


def test_the_random_intercept_icc_is_the_balanced_one_way_anova_at_maximum_likelihood() -> None:
    """k groups of m: se2 = SSW / (k(m-1)), sb2 = (SSB/k - se2)/m, ICC = sb2 / (sb2 + se2)."""
    r = random.Random(11)
    k, m = 40, 6
    groups, y = [], []
    for g in range(k):
        b = r.gauss(0, 1.0)
        for _ in range(m):
            groups += [g]
            y += [3.0 + b + r.gauss(0, 0.8)]
    grand = sum(y) / len(y)
    means = [sum(y[g * m:(g + 1) * m]) / m for g in range(k)]
    ssb = m * sum((mu - grand) ** 2 for mu in means)
    ssw = sum((v - means[i // m]) ** 2 for i, v in enumerate(y))
    se2 = ssw / (k * (m - 1))
    sb2 = (ssb / k - se2) / m
    assert sb2 > 0
    fit, icc = K.random_intercept(_design({"z": [0.0] * len(y)}, []), y, groups)
    assert icc == pytest.approx(sb2 / (sb2 + se2), abs=1e-6)
    assert fit.coef("int")[0] == pytest.approx(grand, abs=1e-9)


def test_the_auc_is_the_mann_whitney_count_over_every_pair() -> None:
    """Pairs of a positive and a negative: 1 where the positive scores higher, a half on a tie."""
    r = random.Random(7)
    scores = [float(r.randrange(0, 12)) for _ in range(90)]
    labels = [1 if r.random() < 0.3 + 0.04 * s else 0 for s in scores]
    pos = [s for s, v in zip(scores, labels) if v]
    neg = [s for s, v in zip(scores, labels) if not v]
    count = sum(1.0 if p > q else 0.5 if p == q else 0.0 for p in pos for q in neg)
    assert K.auc(scores, labels) == pytest.approx(count / (len(pos) * len(neg)), abs=1e-12)


def test_spearman_is_the_rank_formula_and_pearson_on_counted_ranks() -> None:
    """No ties: 1 - 6 sum d^2 / (n(n^2-1)); with ties: Pearson on ranks counted pair by pair."""
    r = random.Random(13)
    a = r.sample(range(1000), 60)
    b = [v + r.gauss(0, 200) for v in a]
    ra = [sum(1 for w in a if w < v) + 1 for v in a]
    rb = [sum(1 for w in b if w < v) + 1 for v in b]
    n = len(a)
    expected = 1 - 6 * sum((x - y) ** 2 for x, y in zip(ra, rb)) / (n * (n * n - 1))
    assert K.spearman([float(v) for v in a], b) == pytest.approx(expected, abs=1e-12)
    tied_a = [float(r.randrange(0, 6)) for _ in range(50)]
    tied_b = [v + float(r.randrange(0, 4)) for v in tied_a]

    def counted(values: "list[float]") -> "list[float]":
        return [sum(1 for w in values if w < v) + (sum(1 for w in values if w == v) + 1) / 2 for v in values]

    ca, cb = counted(tied_a), counted(tied_b)
    ma, mb = sum(ca) / len(ca), sum(cb) / len(cb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ca, cb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ca) * sum((y - mb) ** 2 for y in cb))
    assert K.spearman(tied_a, tied_b) == pytest.approx(num / den, abs=1e-12)


def _breslow(beta: "list[float]", x: "list[list[float]]", time: "list[float]", event: "list[int]") -> float:
    """The Breslow log partial likelihood, every risk set summed afresh."""
    total = 0.0
    for i, (t, e) in enumerate(zip(time, event)):
        if not e:
            continue
        risk = sum(math.exp(sum(b * v for b, v in zip(beta, x[j]))) for j in range(len(time)) if time[j] >= t)
        total += sum(b * v for b, v in zip(beta, x[i])) - math.log(risk)
    return total


def test_cox_maximizes_the_breslow_partial_likelihood_counted_by_brute_force() -> None:
    """At the fitted coefficients the brute-force score is zero, and the standard errors are its curvature's."""
    r = random.Random(17)
    n = 60
    x = [[float(r.random() < 0.5), r.gauss(0, 1)] for _ in range(n)]
    time = [float(int(-math.log(r.random()) / math.exp(0.6 * a + 0.4 * b) * 10) + 1) for a, b in x]
    event = [1 if r.random() < 0.8 else 0 for _ in range(n)]
    assert len(set(time)) < n  # ties are present, so Breslow's handling is exercised
    fit = K.cox(_design({"a": [v[0] for v in x], "b": [v[1] for v in x]}, ["a", "b"], intercept=False),
                time, event)
    step = 1e-5
    hessian = [[0.0, 0.0], [0.0, 0.0]]
    for i in range(2):
        up = list(fit.beta)
        down = list(fit.beta)
        up[i] += step
        down[i] -= step
        score = (_breslow(up, x, time, event) - _breslow(down, x, time, event)) / (2 * step)
        assert abs(score) < 1e-5
        for j in range(2):
            uu, ud, du, dd = (list(fit.beta) for _ in range(4))
            uu[i] += step
            uu[j] += step
            ud[i] += step
            ud[j] -= step
            du[i] -= step
            du[j] += step
            dd[i] -= step
            dd[j] -= step
            hessian[i][j] = (_breslow(uu, x, time, event) - _breslow(ud, x, time, event)
                             - _breslow(du, x, time, event) + _breslow(dd, x, time, event)) / (4 * step * step)
    det = hessian[0][0] * hessian[1][1] - hessian[0][1] * hessian[1][0]
    assert fit.se[0] == pytest.approx(math.sqrt(-hessian[1][1] / det), rel=1e-3)
    assert fit.se[1] == pytest.approx(math.sqrt(-hessian[0][0] / det), rel=1e-3)


def test_the_spline_is_harrells_formula_and_straight_past_its_outer_knots() -> None:
    """At a point between the knots the terms are the formula's; below and above the knots, second differences vanish."""
    knots = [1.0, 3.0, 4.0, 8.0]
    x = 5.0
    norm = (8.0 - 1.0) ** 2
    first = ((x - 1) ** 3 - (x - 4) ** 3 * (8 - 1) / (8 - 4)) / norm
    second = ((x - 3) ** 3 - (x - 4) ** 3 * (8 - 3) / (8 - 4)) / norm
    assert K.rcs(x, knots) == pytest.approx([first, second], abs=1e-12)
    for j in (0, 1):
        assert K.rcs_term(knots, j, 2.5)(x) == pytest.approx(2.5 * K.rcs(x, knots)[j], abs=1e-12)
    for points in ((8.5, 9.5, 10.5), (-2.0, -1.0, 0.0)):
        for j in (0, 1):
            a, b, c = (K.rcs(p, knots)[j] for p in points)
            assert a - 2 * b + c == pytest.approx(0.0, abs=1e-9)


@pytest.mark.parametrize("x", [0.1, 1.0, 3.841458820694124, 6.0, 15.0, 40.0])
def test_the_chi_square_tail_meets_its_closed_forms(x: float) -> None:
    """One degree of freedom: erfc(sqrt(x/2)); two: exp(-x/2)."""
    assert K.chi2_sf(x, 1) == pytest.approx(math.erfc(math.sqrt(x / 2)), rel=1e-9, abs=1e-15)
    assert K.chi2_sf(x, 2) == pytest.approx(math.exp(-x / 2), rel=1e-9, abs=1e-15)


def test_the_kaplan_meier_median_is_the_hand_count() -> None:
    """Ten subjects: the curve steps to 0.9, 0.8, 0.686 (7 at risk), 0.549 (5) and 0.366 (3) at time 9."""
    time = [1, 2, 3, 4, 5, 6, 7, 9, 10, 12]
    event = [1, 1, 0, 1, 0, 1, 0, 1, 1, 0]
    assert K.km_median(time, event) == 9.0


def test_a_fit_the_table_cannot_carry_is_refused_by_name() -> None:
    """A separated outcome, a repeated term and no rows each stop with their trouble's name."""
    x = [float(i) for i in range(20)]
    y = [1.0 if v > 9 else 0.0 for v in x]
    with pytest.raises(K.FitTrouble) as separated:
        K.glm(_design({"x": x}, ["x"]), y, "logistic")
    assert separated.value.kind in ("separation", "no convergence")
    with pytest.raises(K.FitTrouble) as repeated:
        K.ols(_design({"x": x, "z": [2.0 * v for v in x]}, ["x", "z"]), [v + 1 for v in x])
    assert repeated.value.kind == "singular"
    with pytest.raises(K.FitTrouble) as empty:
        K.glm(_design({"x": [1.0, 2.0]}, ["x"]), [1.0, 1.0], "logistic")
    assert empty.value.kind == "empty"


def test_the_booster_finds_a_seeded_threshold_and_ignores_noise() -> None:
    """y follows x above 0.6; a noise column gains little, and a fresh draw scores an AUC above 0.85."""
    r = random.Random(23)

    def draw(n: int) -> "tuple[list[list[float | None]], list[int]]":
        x = [r.random() for _ in range(n)]
        noise = [r.random() for _ in range(n)]
        y = [1 if (v > 0.6) == (r.random() < 0.9) else 0 for v in x]
        return [list(x), list(noise)], y

    features, y = draw(1500)
    booster = K.Booster(rounds=20).fit(features, y)
    assert booster.gain[0] > 10 * booster.gain[1]
    test_features, test_y = draw(1500)
    assert K.auc(booster.predict(test_features), test_y) > 0.85


def test_the_design_never_holds_more_than_a_chunk_of_terms() -> None:
    """Memory is the table plus O(p^2): a design asks its terms for one chunk of rows at a time."""
    largest = [0]

    def term(c: "dict[str, list]") -> "list[float]":
        largest[0] = max(largest[0], len(c["x"]))
        return list(c["x"])

    rows = 3 * K.CHUNK + 5
    design = K.Design({"x": [float(i % 7) for i in range(rows)]}, [("int", K.intercept), ("x", term)])
    K.ols(design, [float(i % 5) for i in range(rows)])
    assert largest[0] == K.CHUNK

"""A plain-Python fitting kit for the analyst battery (plan P4-D398).

The analyst battery (`tests/analyst_battery.py`) asks of a twin what a
researcher would ask of the real table -- regressions, survival models,
mixed models, a trained classifier -- and needs a fitter for each. The
project adds no dependency for it: no statistics package is in the
development lock, and the orchestrator's ruling of 2026-10-16 keeps
numpy's linear algebra out of the tests as well. So every fit here is
the standard library over Python lists, and every one of them is
checked by `tests/test_analyst_kit.py` against a closed form it does not
share code with -- a fitter that is its own witness proves nothing.

MEMORY IS THE TABLE PLUS O(p^2). A model's design matrix is never held.
`Design` keeps the table's own columns and the model's terms as
functions; the fitters ask it for a CHUNK of rows at a time, build that
chunk's term columns, fold them into p x p sums and drop them. Column
products over a chunk run in C (`sum(map(mul, a, b))`), about four times
faster than a loop over rows (12.6 against 49.8 ns a multiply-add,
measured at 5,000 rows and twelve terms when this was written).

WHAT A FIT REFUSES. An analyst's software stops or warns where a model
cannot be fitted, and the battery counts those stops (K-BC-10), so the
fitters raise `FitTrouble` with one of `TROUBLES` rather than return a
number nobody should read: a design whose cross-product matrix is not
positive definite (`singular`), Newton steps that do not settle
(`no convergence`), a logistic fit whose fitted probabilities reach 0 or
1 (`separation`), an empty set of rows (`empty`).

Every function is deterministic: no randomness is drawn here except by
`Booster`, which draws none either -- its splits are exhaustive.
"""

from __future__ import annotations

import math
from operator import mul
from typing import Callable, Iterator, Sequence

# Rows a chunk holds. Large enough that the C loops dominate, small
# enough that a chunk of fifty term columns stays a few megabytes.
CHUNK = 2048

TROUBLES = ("singular", "no convergence", "separation", "empty")

Term = Callable[["dict[str, list]"], "list[float]"]


class FitTrouble(Exception):
    """A model the data cannot fit, named by one of `TROUBLES`."""

    def __init__(self, kind: str, message: str) -> None:
        if kind not in TROUBLES:
            raise ValueError(f"unknown trouble {kind!r}")
        super().__init__(f"{kind}: {message}")
        self.kind = kind


def intercept(chunk: "dict[str, list]") -> "list[float]":
    """The constant term, as long as the chunk."""
    for column in chunk.values():
        return [1.0] * len(column)
    return []


class Design:
    """A model's terms over a table's columns, built a chunk at a time.

    ``columns`` maps a column name to its values (one per row, every
    column the same length); ``terms`` is a list of (name, function),
    each function taking a dict of column CHUNKS and returning that
    chunk's term values. The design matrix itself is never formed.
    """

    def __init__(self, columns: "dict[str, list]", terms: "list[tuple[str, Term]]") -> None:
        lengths = {len(values) for values in columns.values()}
        if len(lengths) > 1:
            raise ValueError("every column of a design must have the same length")
        self.columns = columns
        self.terms = terms
        self.names = [name for name, _function in terms]
        self.rows = lengths.pop() if lengths else 0

    def reordered(self, order: "Sequence[int]") -> "Design":
        """The same terms over the rows taken in ``order``."""
        return Design({k: [v[i] for i in order] for k, v in self.columns.items()}, self.terms)

    def chunks(self) -> "Iterator[tuple[int, int, list[list[float]]]]":
        """(start, stop, the chunk's term columns) for every chunk of rows."""
        for start in range(0, self.rows, CHUNK):
            stop = min(self.rows, start + CHUNK)
            part = {k: v[start:stop] for k, v in self.columns.items()}
            yield start, stop, [function(part) for _name, function in self.terms]


class Fit:
    """Coefficients, their covariance and standard errors, by term name."""

    def __init__(self, names: "list[str]", beta: "list[float]", cov: "list[list[float]]",
                 iterations: int = 1, extra: "dict[str, float] | None" = None) -> None:
        self.names = names
        self.beta = beta
        self.cov = cov
        self.se = [math.sqrt(max(0.0, cov[i][i])) for i in range(len(beta))]
        self.iterations = iterations
        self.extra = extra or {}

    def coef(self, name: str) -> "tuple[float, float]":
        """(estimate, standard error) of one named term."""
        at = self.names.index(name)
        return self.beta[at], self.se[at]

    def contrast(self, weights: "dict[str, float]") -> "tuple[float, float]":
        """(estimate, standard error) of a weighted sum of named coefficients."""
        c = [weights.get(name, 0.0) for name in self.names]
        value = sum(map(mul, c, self.beta))
        var = 0.0
        for i, ci in enumerate(c):
            if ci:
                var += ci * sum(map(mul, self.cov[i], c))
        return value, math.sqrt(max(0.0, var))


# -- linear algebra on p x p lists ---------------------------------------


def cholesky(a: "list[list[float]]") -> "list[list[float]]":
    """The lower Cholesky factor of a symmetric matrix; FitTrouble if not positive definite.

    A pivot at or below 1e-10 of its own diagonal entry is refused: the
    design has a term that is (nearly) a combination of the others.
    """
    n = len(a)
    low = [[0.0] * n for _ in range(n)]
    for i in range(n):
        li = low[i]
        for j in range(i + 1):
            lj = low[j]
            s = a[i][j] - sum(map(mul, li[:j], lj[:j]))
            if i == j:
                if not s > 1e-10 * max(abs(a[i][i]), 1e-300):
                    raise FitTrouble("singular", f"term {i} is a combination of the others")
                li[i] = math.sqrt(s)
            else:
                li[j] = s / lj[j]
    return low


def independent_terms(design: "Design") -> "list[str]":
    """The terms left once each term that is (nearly) a combination of the ones before it is dropped.

    One pass for X'X, then Cholesky in term order, skipping a term whose
    pivot falls to 1e-9 of its own diagonal -- what R's `lm` reports as
    an aliased coefficient. For a design built automatically, where two
    missing-value indicators may sum to the intercept.
    """
    p = len(design.names)
    xtx = [[0.0] * p for _ in range(p)]
    for _start, _stop, cols in design.chunks():
        for i in range(p):
            row = xtx[i]
            for j in range(i, p):
                row[j] += _dot(cols[i], cols[j])
    _symmetrize(xtx)
    kept: "list[int]" = []
    low: "dict[int, dict[int, float]]" = {}
    for i in range(p):
        li: "dict[int, float]" = {}
        for j in kept:
            lj = low[j]
            li[j] = (xtx[i][j] - sum(li[k] * lj[k] for k in kept if k < j and k in li)) / lj[j]
        pivot = xtx[i][i] - sum(v * v for v in li.values())
        if pivot > 1e-9 * max(xtx[i][i], 1e-300):
            li[i] = math.sqrt(pivot)
            low[i] = li
            kept += [i]
    return [design.names[i] for i in kept]


def solve(low: "list[list[float]]", b: "list[float]") -> "list[float]":
    """x with (low low') x = b."""
    n = len(low)
    y = [0.0] * n
    for i in range(n):
        y[i] = (b[i] - sum(map(mul, low[i][:i], y[:i]))) / low[i][i]
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        s = y[i]
        for k in range(i + 1, n):
            s -= low[k][i] * x[k]
        x[i] = s / low[i][i]
    return x


def inverse(a: "list[list[float]]") -> "list[list[float]]":
    """The inverse of a symmetric positive definite matrix."""
    low = cholesky(a)
    n = len(a)
    columns = [solve(low, [1.0 if k == j else 0.0 for k in range(n)]) for j in range(n)]
    return [[columns[j][i] for j in range(n)] for i in range(n)]


def _symmetrize(a: "list[list[float]]") -> None:
    for i in range(len(a)):
        for j in range(i):
            a[i][j] = a[j][i]


def _dot(a: "Sequence[float]", b: "Sequence[float]") -> float:
    return sum(map(mul, a, b))


def _eta(columns: "list[list[float]]", beta: "list[float]", base: "list[float]") -> "list[float]":
    eta = list(base)
    for column, b in zip(columns, beta):
        if b:
            eta = [e + b * x for e, x in zip(eta, column)]
    return eta


def linear(columns: "list[list[float]]", beta: "list[float]") -> "list[float]":
    """The linear predictor of a chunk's term columns: sum of beta_j x_j, row by row."""
    return _eta(columns, beta, [0.0] * (len(columns[0]) if columns else 0))


# -- linear regression -----------------------------------------------------


def ols(design: Design, y: "Sequence[float]") -> Fit:
    """Ordinary least squares; FitTrouble 'empty' or 'singular'.

    One pass: X'X, X'y and y'y are summed chunk by chunk, so the
    residual sum of squares comes from the sums and no second pass is
    needed. The covariance is s^2 (X'X)^-1 with s^2 = RSS / (n - p);
    ``extra`` carries `r2` and `rss`.
    """
    p = len(design.names)
    n = design.rows
    if n <= p:
        raise FitTrouble("empty", f"{n} rows for {p} terms")
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    yy = 0.0
    ysum = 0.0
    for start, stop, cols in design.chunks():
        part = list(y[start:stop])
        yy += _dot(part, part)
        ysum += sum(part)
        for i in range(p):
            ci = cols[i]
            xty[i] += _dot(ci, part)
            row = xtx[i]
            for j in range(i, p):
                row[j] += _dot(ci, cols[j])
    _symmetrize(xtx)
    beta = solve(cholesky(xtx), xty)
    rss = yy - 2.0 * _dot(beta, xty) + sum(beta[i] * _dot(xtx[i], beta) for i in range(p))
    rss = max(rss, 0.0)
    s2 = rss / (n - p)
    inv = inverse(xtx)
    cov = [[s2 * v for v in row] for row in inv]
    tss = yy - ysum * ysum / n
    return Fit(design.names, beta, cov, 1, {"rss": rss, "r2": 1.0 - rss / tss if tss > 0 else 0.0})


# -- generalized linear models -------------------------------------------


def glm(
    design: Design,
    y: "Sequence[float]",
    family: str,
    offset: "Sequence[float] | None" = None,
    max_iter: int = 30,
    tol: float = 1e-8,
    strict: bool = True,
    start: "Sequence[float] | None" = None,
) -> Fit:
    """Logistic (``family`` 'logistic') or Poisson ('poisson') regression by IRLS.

    Starts from the outcome's mean on the intercept (the first term must
    be the intercept); stops when no coefficient moves more than ``tol``.
    FitTrouble: 'empty' with no rows or an outcome with one value,
    'no convergence' after ``max_iter`` steps, 'separation' where a
    logistic fit puts a fitted probability within 1e-9 of 0 or 1,
    'singular' from the cross-product matrix. The covariance is the
    inverse Fisher information; ``extra`` carries the deviance and, for
    Poisson, the Pearson dispersion (chi-square over n - p). With
    ``strict`` False the last step is returned where the steps did not
    settle or a probability reached 0 or 1 (a discriminator, whose
    fitted probabilities are the measure, not its coefficients); ``extra``
    then says `settled` 0.0. ``start`` gives the first coefficients (the
    same model's fit on another table): the steps end at the same
    maximum, in fewer of them.
    """
    if family not in ("logistic", "poisson"):
        raise ValueError(f"unknown family {family!r}")
    p = len(design.names)
    n = design.rows
    if n <= p:
        raise FitTrouble("empty", f"{n} rows for {p} terms")
    mean = math.fsum(y) / n
    if family == "logistic" and not 0.0 < mean < 1.0:
        raise FitTrouble("empty", "the outcome holds one value only")
    if family == "poisson" and not mean > 0.0:
        raise FitTrouble("empty", "the outcome is never above zero")
    beta = [0.0] * p
    beta[0] = math.log(mean / (1.0 - mean)) if family == "logistic" else math.log(mean)
    if start is not None and len(start) == p and all(math.isfinite(b) for b in start):
        beta = list(start)

    def accumulate(beta: "list[float]") -> "tuple[list[list[float]], list[float], float, float, bool]":
        info = [[0.0] * p for _ in range(p)]
        score = [0.0] * p
        deviance = pearson = 0.0
        extreme = False
        for start, stop, cols in design.chunks():
            part = y[start:stop]
            base = list(offset[start:stop]) if offset is not None else [0.0] * (stop - start)
            eta = _eta(cols, beta, base)
            if family == "logistic":
                mu = [1.0 / (1.0 + math.exp(-max(-35.0, min(35.0, e)))) for e in eta]
                if any(m < 1e-9 or m > 1.0 - 1e-9 for m in mu):
                    extreme = True
                w = [max(m * (1.0 - m), 1e-12) for m in mu]
                for yi, m in zip(part, mu):
                    if 0.0 < m < 1.0:
                        deviance -= 2.0 * (math.log(m) if yi else math.log1p(-m))
            else:
                mu = [math.exp(min(35.0, e)) for e in eta]
                w = mu
                for yi, m in zip(part, mu):
                    deviance += 2.0 * ((yi * math.log(yi / m) if yi > 0 else 0.0) - (yi - m))
                    pearson += (yi - m) ** 2 / m
            resid = [yi - m for yi, m in zip(part, mu)]
            for i in range(p):
                ci = cols[i]
                score[i] += _dot(ci, resid)
                wc = list(map(mul, w, ci))
                row = info[i]
                for j in range(i, p):
                    row[j] += _dot(wc, cols[j])
        _symmetrize(info)
        return info, score, deviance, pearson, extreme

    # Newton steps with step-halving: a step that raises the deviance is
    # halved back towards the last accepted point (as R's glm.fit does),
    # so a few rows of very large weight cannot throw the fit off.
    info: "list[list[float]]" = []
    accepted: "list[float] | None" = None
    accepted_state: "tuple[list[list[float]], list[float], float, float, bool] | None" = None
    halvings = 0
    iterations = 0
    converged = False
    deviance = pearson = 0.0
    extreme = False
    while iterations < max_iter:
        state = accumulate(beta)
        if accepted is not None and accepted_state is not None and not (
                state[2] <= accepted_state[2] + 1e-9 * (1.0 + abs(accepted_state[2]))):
            if halvings < 30:
                beta = [(a + b) / 2.0 for a, b in zip(beta, accepted)]
                halvings += 1
                continue
            beta, state, converged = accepted, accepted_state, True
            info, _score, deviance, pearson, extreme = state
            break
        halvings = 0
        accepted, accepted_state = beta, state
        info, score, deviance, pearson, extreme = state
        iterations += 1
        step = solve(cholesky(info), score)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < tol * (1.0 + max(abs(b) for b in beta)):
            converged = True
            break
    # Separation first: a separated term's coefficient runs off without
    # end, so its steps never settle either, and the name an analyst's
    # software gives it is the separation, not the steps.
    if strict and family == "logistic" and extreme:
        raise FitTrouble("separation", "a fitted probability reached 0 or 1")
    if strict and not converged:
        raise FitTrouble("no convergence", f"{max_iter} steps did not settle")
    extra = {"deviance": deviance, "settled": 1.0 if converged and not extreme else 0.0}
    if family == "poisson":
        extra["dispersion"] = pearson / (n - p)
    return Fit(design.names, beta, inverse(info), iterations, extra)


# -- the Cox model ------------------------------------------------------


def cox(
    design: Design,
    time: "Sequence[float]",
    event: "Sequence[int]",
    max_iter: int = 30,
    tol: float = 1e-9,
) -> Fit:
    """Cox proportional hazards, Breslow's ties, by Newton-Raphson. No intercept term.

    The rows are taken longest time first, so each risk set is a running
    sum: every row of a tied time joins the sums before that time's
    events are scored (Breslow). FitTrouble 'empty' with no event,
    'no convergence', or 'singular'.
    """
    p = len(design.names)
    n = design.rows
    if n == 0 or not any(event):
        raise FitTrouble("empty", "no event")
    order = sorted(range(n), key=lambda i: -time[i])
    ranked = design.reordered(order)
    times = [time[i] for i in order]
    events = [1 if event[i] else 0 for i in order]
    beta = [0.0] * p
    info: "list[list[float]]" = []
    for iterations in range(1, max_iter + 1):
        score = [0.0] * p
        info = [[0.0] * p for _ in range(p)]
        s0 = 0.0
        s1 = [0.0] * p
        s2 = [[0.0] * p for _ in range(p)]
        group: "list[tuple[tuple[float, ...], float, int]]" = []
        group_time = None

        def close(group: "list[tuple[tuple[float, ...], float, int]]") -> None:
            nonlocal s0
            for x, r, _e in group:
                s0 += r
                for a in range(p):
                    ra = r * x[a]
                    s1[a] += ra
                    row = s2[a]
                    for c in range(a, p):
                        row[c] += ra * x[c]
            failures = 0
            for x, _r, e in group:
                if e:
                    failures += 1
                    for a in range(p):
                        score[a] += x[a]
            if failures:
                m = [v / s0 for v in s1]
                for a in range(p):
                    score[a] -= failures * m[a]
                    row = info[a]
                    for c in range(a, p):
                        row[c] += failures * (s2[a][c] / s0 - m[a] * m[c])

        for start, stop, cols in ranked.chunks():
            eta = _eta(cols, beta, [0.0] * (stop - start))
            risk = [math.exp(min(60.0, e)) for e in eta]
            for k, x in enumerate(zip(*cols)):
                t = times[start + k]
                if group and t != group_time:
                    close(group)
                    group = []
                group_time = t
                group += [(x, risk[k], events[start + k])]
        if group:
            close(group)
        _symmetrize(info)
        step = solve(cholesky(info), score)
        beta = [b + s for b, s in zip(beta, step)]
        if max(abs(s) for s in step) < tol * (1.0 + max(abs(b) for b in beta)):
            return Fit(design.names, beta, inverse(info), iterations)
    raise FitTrouble("no convergence", f"{max_iter} steps did not settle")


# -- a linear mixed model with a random intercept ------------------------


def random_intercept(
    design: Design, y: "Sequence[float]", groups: "Sequence[object]"
) -> "tuple[Fit, float]":
    """A linear mixed model with one random intercept per group, by profiled maximum likelihood.

    Returns the fixed effects and the intra-class correlation
    sb2 / (sb2 + se2). The ratio lam = sb2 / se2 is searched by golden
    section on log lam over [1e-4, 1e3]; for each lam the fixed effects
    and se2 are closed forms. Per group only its row count, term sums and
    outcome sum are kept (O(p) each); the p x p sums are global.
    """
    p = len(design.names)
    if design.rows <= p:
        raise FitTrouble("empty", f"{design.rows} rows for {p} terms")
    xtx = [[0.0] * p for _ in range(p)]
    xty = [0.0] * p
    yy = 0.0
    per: "dict[object, list]" = {}
    for start, stop, cols in design.chunks():
        part = list(y[start:stop])
        yy += _dot(part, part)
        for i in range(p):
            ci = cols[i]
            xty[i] += _dot(ci, part)
            row = xtx[i]
            for j in range(i, p):
                row[j] += _dot(ci, cols[j])
        for k, x in enumerate(zip(*cols)):
            g = groups[start + k]
            held = per.get(g)
            if held is None:
                held = [0, [0.0] * p, 0.0]
                per[g] = held
            held[0] += 1
            sums = held[1]
            for a in range(p):
                sums[a] += x[a]
            held[2] += part[k]
    _symmetrize(xtx)
    stats = [(held[0], held[1], held[2]) for held in per.values()]
    # Where no group holds two rows, or one group holds them all, the
    # likelihood is flat in lam (measured: an ICC anywhere from 0.003 to
    # 0.98 over eight seeds of one-row groups), and an analyst's software
    # refuses the model (lme4: a grouping factor with as many levels as
    # rows, or one level). So does this one.
    if sum(ni - 1 for ni, _x1, _y1 in stats) == 0 or len(stats) < 2:
        raise FitTrouble("singular", "no group holds two rows, or one group holds every row")
    total = design.rows

    def at(lam: float) -> "tuple[float, list[float], float, list[list[float]]]":
        a = [row[:] for row in xtx]
        b = xty[:]
        logdet = 0.0
        for ni, x1, y1 in stats:
            f = lam / (1.0 + lam * ni)
            logdet += math.log1p(lam * ni)
            for i in range(p):
                fi = f * x1[i]
                b[i] -= fi * y1
                row = a[i]
                for j in range(i, p):
                    row[j] -= fi * x1[j]
        _symmetrize(a)
        beta = solve(cholesky(a), b)
        rr = yy - 2.0 * _dot(beta, xty) + sum(beta[i] * _dot(xtx[i], beta) for i in range(p))
        q = rr
        for ni, x1, y1 in stats:
            r1 = y1 - _dot(x1, beta)
            q -= lam / (1.0 + lam * ni) * r1 * r1
        s2 = max(q, 1e-300) / total
        return -0.5 * (total * math.log(s2) + logdet + total), beta, s2, a

    low, high = math.log(1e-4), math.log(1e3)
    ratio = (math.sqrt(5.0) - 1.0) / 2.0
    c1 = high - ratio * (high - low)
    c2 = low + ratio * (high - low)
    f1 = at(math.exp(c1))[0]
    f2 = at(math.exp(c2))[0]
    for _ in range(60):
        if f1 > f2:
            high, c2, f2 = c2, c1, f1
            c1 = high - ratio * (high - low)
            f1 = at(math.exp(c1))[0]
        else:
            low, c1, f1 = c1, c2, f2
            c2 = low + ratio * (high - low)
            f2 = at(math.exp(c2))[0]
    lam = math.exp((low + high) / 2.0)
    _ll, beta, s2, a = at(lam)
    cov = [[s2 * v for v in row] for row in inverse(a)]
    return Fit(design.names, beta, cov, 1, {"sigma2": s2, "lambda": lam}), lam / (1.0 + lam)


# -- ranks, correlation, discrimination ----------------------------------


def ranks(values: "Sequence[float]") -> "list[float]":
    """Ranks 1..n, ties given their average rank."""
    order = sorted(range(len(values)), key=values.__getitem__)
    out = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        shared = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            out[order[k]] = shared
        i = j + 1
    return out


def pearson(a: "Sequence[float]", b: "Sequence[float]") -> float:
    """Pearson's correlation; 0.0 where either side does not vary."""
    n = len(a)
    if n < 2:
        return 0.0
    ma, mb = math.fsum(a) / n, math.fsum(b) / n
    da = [v - ma for v in a]
    db = [v - mb for v in b]
    saa, sbb = _dot(da, da), _dot(db, db)
    if saa <= 0.0 or sbb <= 0.0:
        return 0.0
    return _dot(da, db) / math.sqrt(saa * sbb)


def spearman(a: "Sequence[float]", b: "Sequence[float]") -> float:
    """Spearman's rank correlation: Pearson's on average ranks."""
    return pearson(ranks(a), ranks(b))


def auc(scores: "Sequence[float]", labels: "Sequence[int]") -> float:
    """The area under the ROC curve by the Mann-Whitney rank sum (ties count a half)."""
    r = ranks(scores)
    positives = sum(1 for v in labels if v)
    negatives = len(labels) - positives
    if not positives or not negatives:
        raise FitTrouble("empty", "one class only")
    rank_sum = math.fsum(ri for ri, v in zip(r, labels) if v)
    return (rank_sum - positives * (positives + 1) / 2.0) / (positives * negatives)


# -- splines, quantiles, tables ------------------------------------------


def rcs(x: float, knots: "Sequence[float]") -> "list[float]":
    """Harrell's restricted cubic spline: k knots give k - 2 nonlinear terms.

    Each term is scaled by the squared span of the outer knots, so its
    size is that of x; the curve is linear beyond the outer knots.
    """
    k = len(knots)
    last, before = knots[-1], knots[-2]
    norm = (last - knots[0]) ** 2
    out = []
    for j in range(k - 2):
        tj = knots[j]
        value = (
            max(0.0, x - tj) ** 3
            - max(0.0, x - before) ** 3 * (last - tj) / (last - before)
            + max(0.0, x - last) ** 3 * (before - tj) / (last - before)
        )
        out += [value / norm]
    return out


def rcs_term(knots: "Sequence[float]", j: int, scale: float = 1.0) -> "Callable[[float], float]":
    """The j-th term of `rcs` as a function of x alone, its constants worked out once (times ``scale``)."""
    tj, before, last = knots[j], knots[-2], knots[-1]
    a = (last - tj) / (last - before)
    b = (before - tj) / (last - before)
    norm = (last - knots[0]) ** 2 / scale

    def term(x: float) -> float:
        u = x - tj
        if u <= 0.0:
            return 0.0
        value = u * u * u
        w = x - before
        if w > 0.0:
            value -= w * w * w * a
            w = x - last
            if w > 0.0:
                value += w * w * w * b
        return value / norm

    return term


def quantile(ordered: "Sequence[float]", q: float) -> float:
    """The q-th quantile of sorted values, by linear interpolation."""
    if not ordered:
        raise FitTrouble("empty", "no values")
    position = q * (len(ordered) - 1)
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (ordered[high] - ordered[low]) * (position - low)


def chi2_sf(statistic: float, df: int) -> float:
    """P(chi-square with ``df`` degrees of freedom >= statistic): the regularized upper gamma."""
    if statistic <= 0.0:
        return 1.0
    a, x = df / 2.0, statistic / 2.0
    lead = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1.0:
        term = total = 1.0 / a
        ap = a
        for _ in range(500):
            ap += 1.0
            term *= x / ap
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1.0 - total * lead)
    b = x + 1.0 - a
    c = 1.0 / 1e-300
    d = 1.0 / b
    h = d
    for i in range(1, 500):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        d = 1e-300 if abs(d) < 1e-300 else d
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-15:
            break
    return lead * h


def kruskal_wallis(values: "Sequence[float]", labels: "Sequence[object]") -> "tuple[float, int]":
    """Kruskal-Wallis H with the ties correction, and its degrees of freedom (groups - 1).

    H = 12 / (n (n + 1)) sum R_g^2 / n_g - 3 (n + 1), over average ranks,
    divided by 1 - sum (t^3 - t) / (n^3 - n) over the tied runs; its tail
    is `chi2_sf(H, groups - 1)`. Where every value is tied, H is 0.
    """
    n = len(values)
    if n == 0:
        raise FitTrouble("empty", "no values")
    r = ranks(values)
    sums: "dict[object, float]" = {}
    counts: "dict[object, int]" = {}
    for rank, label in zip(r, labels):
        sums[label] = sums.get(label, 0.0) + rank
        counts[label] = counts.get(label, 0) + 1
    h = 12.0 / (n * (n + 1.0)) * sum(sums[g] ** 2 / counts[g] for g in sums) - 3.0 * (n + 1.0)
    runs: "dict[float, int]" = {}
    for v in values:
        runs[v] = runs.get(v, 0) + 1
    tied = sum(t ** 3 - t for t in runs.values())
    correction = 1.0 - tied / (n ** 3 - n) if n > 1 else 0.0
    return (max(h, 0.0) / correction if correction > 0 else 0.0), len(sums) - 1


def contingency(a: "Sequence[object]", b: "Sequence[object]") -> "dict[tuple[object, object], int]":
    """The counts of each (a, b) pair of values."""
    counts: "dict[tuple[object, object], int]" = {}
    for pair in zip(a, b):
        counts[pair] = counts.get(pair, 0) + 1
    return counts


def chi_square(counts: "dict[tuple[object, object], int]") -> "tuple[float, int, int]":
    """Pearson's chi-square of a two-way table: (statistic, degrees of freedom, smallest cell)."""
    rows: "dict[object, int]" = {}
    cols: "dict[object, int]" = {}
    for (r, c), v in counts.items():
        rows[r] = rows.get(r, 0) + v
        cols[c] = cols.get(c, 0) + v
    n = sum(rows.values())
    statistic = 0.0
    smallest = n
    for r, nr in rows.items():
        for c, nc in cols.items():
            observed = counts.get((r, c), 0)
            smallest = min(smallest, observed)
            expected = nr * nc / n
            statistic += (observed - expected) ** 2 / expected
    return statistic, (len(rows) - 1) * (len(cols) - 1), smallest


def cramers_v(counts: "dict[tuple[object, object], int]") -> float:
    """Cramer's V of a two-way table."""
    statistic, _df, _smallest = chi_square(counts)
    n = sum(counts.values())
    k = min(len({r for r, _c in counts}), len({c for _r, c in counts}))
    if k < 2 or n == 0:
        return 0.0
    return math.sqrt(statistic / (n * (k - 1)))


def km_median(time: "Sequence[float]", event: "Sequence[int]") -> "float | None":
    """The Kaplan-Meier median: the first time the survival curve reaches 0.5 or below."""
    pairs = sorted(zip(time, event))
    at_risk = len(pairs)
    survival = 1.0
    i = 0
    while i < len(pairs):
        t = pairs[i][0]
        failures = removed = 0
        while i < len(pairs) and pairs[i][0] == t:
            failures += 1 if pairs[i][1] else 0
            removed += 1
            i += 1
        if failures:
            survival *= 1.0 - failures / at_risk
            if survival <= 0.5:
                return float(t)
        at_risk -= removed
    return None


# -- histogram gradient boosting (logistic loss) -------------------------


class Booster:
    """Gradient-boosted trees of fixed depth on binned features, logistic loss.

    Features are lists of floats or None (missing goes to bin 0, its own
    bin); each is cut at up to ``bins`` - 1 quantile edges of the
    TRAINING values, and the same edges bin any other table. Every split
    is the best of all features and all bin boundaries, so the fit draws
    no randomness. ``gain`` is each feature's summed split gain.
    """

    def __init__(self, rounds: int = 60, depth: int = 3, rate: float = 0.1,
                 min_leaf: int = 20, lam: float = 1.0, bins: int = 32) -> None:
        self.rounds, self.depth, self.rate = rounds, depth, rate
        self.min_leaf, self.lam, self.bins = min_leaf, lam, bins
        self.edges: "list[list[float]]" = []
        self.trees: "list[tuple[list[list[tuple[int, int] | None]], list[float]]]" = []
        self.base = 0.0
        self.gain: "list[float]" = []

    def _binned(self, features: "list[list[float | None]]") -> "list[bytearray]":
        out = []
        for column, edges in zip(features, self.edges):
            coded = bytearray(len(column))
            for i, v in enumerate(column):
                if v is None or v != v:
                    continue
                lo, hi = 0, len(edges)
                while lo < hi:
                    mid = (lo + hi) // 2
                    if v > edges[mid]:
                        lo = mid + 1
                    else:
                        hi = mid
                coded[i] = lo + 1
            out += [coded]
        return out

    def fit(self, features: "list[list[float | None]]", y: "Sequence[int]") -> "Booster":
        """Train on the feature columns and a 0/1 outcome."""
        n = len(y)
        positives = sum(y)
        if not 0 < positives < n:
            raise FitTrouble("empty", "one class only")
        self.edges = []
        for column in features:
            present = sorted(v for v in column if v is not None and v == v)
            edges: "list[float]" = []
            for q in range(1, self.bins - 1):
                if present:
                    e = quantile(present, q / (self.bins - 1))
                    if not edges or e > edges[-1]:
                        edges += [e]
            self.edges += [edges]
        binned = self._binned(features)
        widths = [len(e) + 2 for e in self.edges]
        self.base = math.log(positives / (n - positives))
        score = [self.base] * n
        self.gain = [0.0] * len(features)
        self.trees = []
        for _round in range(self.rounds):
            prob = [1.0 / (1.0 + math.exp(-s)) for s in score]
            g = [pr - yi for pr, yi in zip(prob, y)]
            h = [max(pr * (1.0 - pr), 1e-6) for pr in prob]
            nodes: "list[list[int]]" = [list(range(n))]
            levels: "list[list[tuple[int, int] | None]]" = []
            for _level in range(self.depth):
                level: "list[tuple[int, int] | None]" = []
                grown: "list[list[int]]" = []
                for idx in nodes:
                    best = self._split(idx, binned, widths, g, h)
                    if best is None:
                        level += [None]
                        grown += [idx, []]
                        continue
                    f, cut, gain = best
                    self.gain[f] += gain
                    column = binned[f]
                    level += [(f, cut)]
                    grown += [[i for i in idx if column[i] <= cut], [i for i in idx if column[i] > cut]]
                levels += [level]
                nodes = grown
            leaves = []
            for idx in nodes:
                if not idx:
                    leaves += [0.0]
                    continue
                gs = math.fsum(g[i] for i in idx)
                hs = math.fsum(h[i] for i in idx)
                value = -gs / (hs + self.lam) * self.rate
                leaves += [value]
                for i in idx:
                    score[i] += value
            self.trees += [(levels, leaves)]
        return self

    def _split(self, idx: "list[int]", binned: "list[bytearray]", widths: "list[int]",
               g: "list[float]", h: "list[float]") -> "tuple[int, int, float] | None":
        if len(idx) < 2 * self.min_leaf:
            return None
        gs = math.fsum(g[i] for i in idx)
        hs = math.fsum(h[i] for i in idx)
        base = gs * gs / (hs + self.lam)
        best: "tuple[int, int, float] | None" = None
        for f, column in enumerate(binned):
            hg = [0.0] * widths[f]
            hh = [0.0] * widths[f]
            hc = [0] * widths[f]
            for i in idx:
                b = column[i]
                hg[b] += g[i]
                hh[b] += h[i]
                hc[b] += 1
            gl = hl = 0.0
            cl = 0
            for b in range(widths[f] - 1):
                gl += hg[b]
                hl += hh[b]
                cl += hc[b]
                if cl < self.min_leaf or len(idx) - cl < self.min_leaf:
                    continue
                gr, hr = gs - gl, hs - hl
                gain = gl * gl / (hl + self.lam) + gr * gr / (hr + self.lam) - base
                if gain > 1e-12 and (best is None or gain > best[2]):
                    best = (f, b, gain)
        return best

    def predict(self, features: "list[list[float | None]]") -> "list[float]":
        """The fitted log-odds of every row of another table."""
        binned = self._binned(features)
        n = len(features[0]) if features else 0
        out = [self.base] * n
        for levels, leaves in self.trees:
            for i in range(n):
                node = 0
                for level in levels:
                    split = level[node]
                    node = node * 2 if split is None else node * 2 + (1 if binned[split[0]][i] > split[1] else 0)
                out[i] += leaves[node]
        return out

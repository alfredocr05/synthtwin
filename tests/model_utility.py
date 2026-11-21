"""The model-utility battery: does an advanced analysis fitted on the twin give the real table's answer? (lane MU, plan P4-D485)

THE QUESTION. The owner (2026-11-10): "what i need is tha the code
develped there will work and that any statistical study, including
advanced statistical analysis and modeling will work!" Lane E0b's battery
(`tests/analyst_battery.py`, K-BC-01 to K-BC-13) asks it of regressions,
survival, a random intercept and a trained classifier; this battery asks
it of the families E0b's plain-Python kit cannot fit, on six invented
tables whose generating structure is KNOWN (`tests/utility_tables.py`,
ST7 to ST12), with statsmodels and scikit-learn (the development lock's
test-only zone, plan P4-D409) and two fitters written here by hand on
numpy and scipy (a Weibull accelerated failure time model and the
Aalen-Johansen incidence), each held to a known answer.

ONE SCALE, E0b'S. Every estimate is scored as K-BC-01 scores one: it is
SUPPORTED where every cell defining it holds 22 rows on the real table
and 11 in each of the eight halves (E0b's `supports` rule, here
`cell`), and INSIDE where it lies within its half-split yardstick of the
real table's value (E0b's `yardstick` and `compare`: four splits of
sixteen SplitMix64 groups, drawn by PERSON on ST7 and ST8, by row
elsewhere). A family's primary measure is its share of supported
estimates inside, against the FRESH REPLICATE's share in the same run (a
perfect twin is inside about 77 % of the time). Every other measure --
standard-error ratios, variance components, calibration, the curvature
retained -- is reported beside it, never as a second scale for the same
estimate.

THE CONTROLS, IN EVERY RUN. The fresh replicate (the same generator at
another seed) and the shuffled twin (every column shuffled on its own,
E0b's `shuffled_text`), with E0b's rules: the replicate within three
binomial standard deviations of 77 %, the shuffled twin more than 10
points under it pooled and 25 points under it in every family of at least
five supported estimates (a family whose shuffle meets that is named
void). NEW: THE FLATTENED REPLICATE (ST7 and ST9): the generator at the
replicate's seed with its curvature halved. The curvature bar must pass
the replicate and FAIL the flattened replicate in the same run, or it is
void for that run. And every ABSOLUTE bar (a standard-error ratio, a
calibration slope, a variance ratio) is void in a run where the
replicate fails it: recorded, never judged.

THE TWIN. Which twin is read is named in every stamp, by route
(`tests/twin_routes.py`): route S, the twin the commands a person types
make (the headline); route C, the chain's switch handed in (the preview);
route P, the patient layer on (ST7 and ST8, until the shipped switch draws
the layer). A stamp never mixes routes.

THE FAMILIES, in the owner's order (the audit's question 4.5 (2)): F11
repeated visits (linear mixed models with a random intercept and slope,
the ICC, GEE exchangeable and AR(1), a binary GEE, rows per person and
the gaps between visits, the serial correlation left in the residuals);
F12 Cox models with a treatment that starts during follow-up (start-stop
rows with entry times, the naive ever-treated model whose immortal-time
bias a twin must give back too, the competing event's cause-specific
model, Kaplan-Meier survival by stage); F13 propensity scores (the
score's model and AUC, the weighted risk difference, nearest-neighbour
matching on the score's log odds within 0.2 SD, the balance after
weighting); F14 prediction models trained on the twin and tested on the
real table (a model with a spline and the interaction, a histogram
gradient-boosting classifier; AUC, calibration slope and intercept,
Brier score, the correlation of predicted risks), against the real half
A model on half B; F15 curved effects and interactions (a quadratic term,
a spline read on E0b's age grid, a GAM with fixed penalties, a threshold
step, a hinge, an interaction, a growth curve in years; CURVATURE
RETAINED); F16 counts over a time at risk (Poisson with the offset,
negative binomial, zero-inflated negative binomial, Poisson without the
offset); F17 missing data (who is missing, the monotone block, MICE with
ten imputations and Rubin's rules, the complete-case model, dropout on the
previous value); F18 ordinal and nominal outcomes with rare levels (the
ordinal model with level terms by E0b's rule of 22 rows, the multinomial
model fitted here by hand, chi-square, Kruskal-Wallis); F19 survival beyond
Cox (the Weibull model and the Aalen-Johansen incidence of both causes at
1, 3 and 5 years, both by hand; the censored share by centre; the four
structure rules every row keeps); F20 regularised regression (the lasso by
3-fold cross-validation over five penalties and an elastic net, saga, on
columns standardized by the real table; the selection's agreement); F21
Table 1 by group; F22 clustering (a Gaussian mixture of one to five
classes by BIC; the class count and the adjusted Rand index); F24 a
Bayesian check, APPROXIMATE (the binomial mixed model by variational
Bayes on 300 persons chosen by the same rule on every frame). F23 (daily
counts) is left to lane MU-b (`LEFT`, which says why); F11's three-level
model is a stated cost (plan P4-D485).

THE WORDS. Logistic models are fitted through the GLM with the binomial
family; the ordinal model is given a scipy distribution object; the
multinomial model is fitted here by hand.

Nothing here changes the product; every table is drawn at run time.
"""

from __future__ import annotations

import contextlib
import ctypes
import dataclasses
import gc
import math
import pathlib
import statistics
import time
import warnings
import zlib
from typing import Callable, Iterator

import numpy as np
import pandas as pd
import scipy.optimize
import scipy.stats
import statsmodels.api as sm
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.exceptions import ConvergenceWarning as LearnConvergenceWarning
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import adjusted_rand_score, roc_auc_score
from sklearn.mixture import GaussianMixture
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP
from statsmodels.discrete.discrete_model import NegativeBinomial
from statsmodels.duration.hazard_regression import PHReg
from statsmodels.duration.survfunc import SurvfuncRight
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
from statsmodels.gam.api import BSplines, GLMGam
from statsmodels.genmod.cov_struct import Autoregressive, Exchangeable
from statsmodels.genmod.generalized_estimating_equations import GEE
from statsmodels.imputation import mice
from statsmodels.miscmodels.ordinal_model import OrderedModel
from statsmodels.regression.mixed_linear_model import MixedLM
from statsmodels.tools.sm_exceptions import (
    ConvergenceWarning,
    IterationLimitWarning,
    PerfectSeparationError,
    PerfectSeparationWarning,
)
from threadpoolctl import threadpool_limits

import analyst_battery as B
import analyst_kit as K
import twin_routes
import utility_tables as U

Estimate = B.Estimate
Analysis = B.Analysis
AnalysisError = B.AnalysisError

FAMILIES = {
    "F11": "repeated visits",
    "F12": "Cox models with a treatment that starts during follow-up",
    "F13": "propensity scores",
    "F14": "prediction models trained on the twin",
    "F15": "curved effects and interactions",
    "F16": "counts over a time at risk",
    "F17": "missing data",
    "F18": "ordinal and nominal outcomes with rare levels",
    "F19": "survival beyond Cox",
    "F20": "regularised regression",
    "F21": "Table 1 by group",
    "F22": "clustering",
    "F23": "daily counts",
    "F24": "a Bayesian check",
}
# The family left to lane MU-b: daily counts (F23). The six tables carry no
# calendar structure tied to another column, and a column-wise shuffle keeps
# one date column's daily counts exactly, so F23 as specified would be void
# by construction; a generator with a weekday and seasonal pattern tied to
# another column is its owner's first step.
LEFT = ("F23",)
TIERS = {
    "fast": {"rows": 5000, "tables": ("ST7", "ST9"), "seeds": (1,), "twins": (0,)},
    "slow": {"rows": 20000, "tables": U.TABLES, "seeds": (1, 2, 3), "twins": (0, 1, 2)},
    "night": {"rows": 200000, "tables": U.TABLES, "seeds": (1,), "twins": (0,)},
}
STRONG_Z = 3.29
# THE SEEDS OF THE TWO FITS THAT DRAW (LANE MU RULINGS 6 (2), Codex's review, its item 2): MICE's imputations and the
# variational fit's starting values are drawn by the generator each is handed through its own `rng` argument, a new one
# from these seeds for every frame, so two fits of one frame are the same fit. statsmodels 0.15.0 draws them from a
# generator of fresh entropy where no `rng` is given, and numpy's global seed never reached it: two fits of one ST11
# frame read lab_a 0.4244 and 0.4255 and a fraction of missing information of 0.077 and 0.257.
MICE_SEED = 20251
VB_SEED = 20252
MICE_IMPUTATIONS = 10
MICE_BURN_IN = 10
# The ordinal model's and the zero-inflated model's iteration caps.
MAX_ITER = 400


# -- reading a frame ------------------------------------------------------------


def _numbers(v: B.View, column: str) -> np.ndarray:
    """The column as floats, NaN where empty; a text column stops the analysis (E0b's `View.num`)."""
    return np.asarray(v.num(column), dtype=float)


def _flag(v: B.View, column: str, value: str) -> np.ndarray:
    """1.0 where the cell reads ``value``, 0.0 elsewhere, NaN where empty."""
    return np.asarray(v.eq(column, value), dtype=float)


def _labels(v: B.View, column: str) -> "list[str | None]":
    return v.text(column)


def _cache(v: B.View) -> "dict[str, object]":
    held = v.__dict__.get("_mu")
    if held is None:
        held = {}
        v.__dict__["_mu"] = held
    return held  # type: ignore[return-value]


def _days(v: B.View, column: str) -> np.ndarray:
    """An ISO date column as days since 1970, read with `pandas.to_datetime` at the ISO format; a cell that does not parse stops."""
    try:
        parsed = pd.to_datetime(v.frame[column], format="%Y-%m-%d")  # type: ignore[index]
    except (ValueError, TypeError) as error:
        raise AnalysisError("not dates", str(error)[:80]) from error
    epoch = pd.Timestamp("1970-01-01")
    return np.asarray([math.nan if x != x else float((x - epoch).days) for x in parsed.tolist()], dtype=float)


def _complete(*columns: np.ndarray) -> np.ndarray:
    """The rows where every column is present (an analyst's complete-case filter); none stops the analysis."""
    keep = np.ones(len(columns[0]), dtype=bool)
    for c in columns:
        keep &= np.isfinite(c)
    if not keep.any():
        raise AnalysisError("empty filter", "no row keeps every column the model names")
    return keep


# The library warnings that say a fit did not settle: statsmodels' and scikit-learn's.
NOT_SETTLED = (ConvergenceWarning, IterationLimitWarning, LearnConvergenceWarning)
# Two of them are no failure: a variance component on the boundary of its space (a variance at 0 is a legitimate
# maximum; a shuffled table's random intercept sits there) and MixedLM's notice that it tries its next optimizer.
# The Hessian's warning stands beside the boundary's where a variance is at 0, and is a failure on its own.
BOUNDARY = "The MLE may be on the boundary of the parameter space"
RETRYING = "Retrying MixedLM optimization"
HESSIAN = "The Hessian matrix at the estimated parameter values is not positive definite"


def _settled(caught: "list[warnings.WarningMessage]") -> None:
    """Stop ('no convergence') on a recorded warning that says the fit did not settle (`NOT_SETTLED`), save the
    boundary's, the retry's and the Hessian's beside the boundary's."""
    said = [(w.category, str(w.message)) for w in caught]
    boundary = any(text.startswith(BOUNDARY) for _category, text in said)
    for category, text in said:
        if not issubclass(category, NOT_SETTLED) or text.startswith((BOUNDARY, RETRYING)):
            continue
        if text.startswith(HESSIAN) and boundary:
            continue
        raise AnalysisError("no convergence", text[:80])


def _fit(fit: "Callable[[], object]", binomial: bool = False) -> object:
    """A library fit, its warnings recorded (`_settled` reads them) and its refusals turned into the analyst's stop; a
    ``binomial`` fit (a binomial GLM or GEE, the multiple imputation's binomial model) also stops on the notices of a
    separation (`_not_separated`)."""
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            result = fit()
        except np.linalg.LinAlgError as error:
            raise AnalysisError("singular", str(error)[:80]) from error
        except PerfectSeparationError as error:
            raise AnalysisError("separation", str(error)[:80]) from error
        except (ValueError, ZeroDivisionError, FloatingPointError, OverflowError, IndexError) as error:
            raise AnalysisError("fit error", f"{type(error).__name__}: {str(error)[:80]}") from error
    if binomial:
        _not_separated(list(caught))
    _settled(list(caught))
    return result


# A BINOMIAL FIT THAT SEPARATES IS NO VALUE (LANE MU RULINGS 7 (2), the combined verify's item 3): under the locked
# statsmodels 0.15.0 a binomial GLM whose outcome a column separates raises no PerfectSeparationError: on complete
# separation it warns (PerfectSeparationWarning), on quasi-complete separation (one row breaks it) it warns nothing,
# says it converged and reads a coefficient of tens to tens of thousands with a standard error larger still (the verify:
# 64,919.8, SE 1,470,952; 2,000 rows of this lane's own: 33.7, SE 12,524), and the overflow of numpy's exponential is
# often the only sign. E0b's kit stops such a fit as 'separation' (K-BC-10's form); so does this battery, after each
# binomial GLM or GEE fit: where statsmodels' separation warning or numpy's overflow warning is recorded inside the fit,
# or where the fitted risks reach within `SEPARATED` of 0 or 1 on every row of the frame or on every row of a group of
# an indicator term (`_separation`). ITS LIMIT (the scoped verify 2's CARRY C1, owner lane MU2; P4-D485 states the
# numbers): a separated group of a few rows stops short of the threshold and is read (its own term never scored, its
# support 0), and so is a quasi-complete separation by a term that is not an indicator.
SEPARATED = 1e-10


def _not_separated(caught: "list[warnings.WarningMessage]") -> None:
    """Stop ('separation') on statsmodels' separation warning or numpy's overflow warning recorded inside a binomial fit."""
    for w in caught:
        text = str(w.message)
        if issubclass(w.category, PerfectSeparationWarning) or (issubclass(w.category, RuntimeWarning)
                                                               and "overflow" in text):
            raise AnalysisError("separation", text[:80])


def _separation(result: object, design: "dict[str, np.ndarray] | np.ndarray | pd.DataFrame", kind: str) -> None:
    """Stop ('separation') where a binomial fit's fitted risks reach within `SEPARATED` of 0 or 1 on every row, or on
    every row of either group of an indicator term of its design (a column of 0 and 1 only)."""
    p = np.asarray(getattr(result, "fittedvalues"), dtype=float).reshape(-1)
    if not len(p):
        return
    edge = (p < SEPARATED) | (p > 1.0 - SEPARATED)
    if bool(edge.all()):
        raise AnalysisError("separation", f"{kind}: every fitted risk at 0 or 1")
    if isinstance(design, pd.DataFrame):
        terms = [(str(name), design[name].to_numpy(dtype=float)) for name in design.columns]
    elif isinstance(design, dict):
        terms = [(name, np.asarray(values, dtype=float)) for name, values in design.items()]
    else:
        matrix = np.asarray(design, dtype=float)
        terms = [(f"column {j}", matrix[:, j]) for j in range(matrix.shape[1])]
    for name, x in terms:
        if len(x) != len(p) or not bool(np.all((x == 0.0) | (x == 1.0))):
            continue
        for group in (x == 0.0, x == 1.0):
            if bool(group.any()) and bool(edge[group].all()):
                raise AnalysisError("separation", f"{kind}: every fitted risk of a group of {name} at 0 or 1")


def _converged(result: object, kind: str) -> None:
    """Stop where the fit's own record says it did not settle (a stop counted on every side alike): statsmodels'
    `converged` or `mle_retvals`, scikit-learn's `converged_`, or an iteration count that reached its cap."""
    flag = getattr(result, "converged", None)
    if flag is None:
        flag = getattr(result, "converged_", None)
    if flag is None:
        retvals = getattr(result, "mle_retvals", None)
        flag = retvals.get("converged") if isinstance(retvals, dict) else None
    if flag is None:
        # A fitter with no such record (scikit-learn's saga): settled where it stopped before its iteration cap.
        steps, cap = getattr(result, "n_iter_", None), getattr(result, "max_iter", None)
        flag = not (steps is not None and isinstance(cap, int) and int(np.max(np.asarray(steps))) >= cap)
    if not flag:
        raise AnalysisError("no convergence", kind)


@contextlib.contextmanager
def one_openmp_thread() -> "Iterator[None]":
    """scikit-learn's histogram booster on ONE OpenMP thread for the block (it reads no n_jobs: its threads are OpenMP's,
    one a core by default, which a loaded machine oversubscribes; skeptic 1's item 2: 6,035 s wall against 279)."""
    with threadpool_limits(limits=1, user_api="openmp"):
        yield


# -- supports and estimates -------------------------------------------------------


def cell(x: np.ndarray, y: "np.ndarray | None" = None) -> int:
    """A term's smallest defining cell, E0b's rule (`analyst_battery.supports`): an indicator (every value 0 or 1, not
    every value 1; an indicator of no 1 has a cell of 0) by its two groups, with a two-valued outcome's events and
    non-events in each (a survival model's event flag is that outcome); any other term by the model's rows (or its
    events and non-events)."""
    n = len(x)
    binary = y is not None and bool(np.all((y == 0.0) | (y == 1.0)))
    indicator = bool(np.all((x == 0.0) | (x == 1.0))) and float(x.sum()) != n
    if indicator:
        if binary:
            assert y is not None
            e1 = float((x * y).sum())
            n1 = float(x.sum())
            e0 = float(y.sum()) - e1
            n0 = n - n1
            return int(min(e1, n1 - e1, e0, n0 - e0))
        return int(min(float(x.sum()), n - float(x.sum())))
    if binary:
        assert y is not None
        events = float(y.sum())
        return int(min(events, n - events))
    return n


def _coefs(prefix: str, family: str, result: object, names: "list[str]", columns: "dict[str, np.ndarray]",
           y: "np.ndarray | None", tags: "dict[str, tuple[str, ...]] | None" = None) -> "list[Estimate]":
    """One estimate per named coefficient of a fitted model, keyed `prefix:name`, its SE the library's."""
    params = getattr(result, "params")
    bse = getattr(result, "bse")
    if not hasattr(params, "index"):
        # A plain array (Cox's fit): in the order of the model's own columns.
        exog_names = list(getattr(getattr(result, "model"), "exog_names", None) or [])
        params = pd.Series(np.asarray(params, dtype=float), index=exog_names)
        bse = pd.Series(np.asarray(bse, dtype=float), index=exog_names)
    out = []
    for name in names:
        value = float(params[name])
        se = float(bse[name])
        if not (math.isfinite(value) and math.isfinite(se)):
            continue
        support = cell(columns[name], y) if name in columns else (len(y) if y is not None else 0)
        out += [Estimate(f"{prefix}:{name}", family, value, se, support, (tags or {}).get(name, ()))]
    return out


def _frame(columns: "dict[str, np.ndarray]", keep: np.ndarray) -> pd.DataFrame:
    return pd.DataFrame({k: v[keep] for k, v in columns.items()})


def _contrast(result: object, weights: "dict[str, float]") -> "tuple[float, float]":
    """A linear combination of a fit's coefficients and its standard error."""
    params = getattr(result, "params")
    cov = getattr(result, "cov_params")()
    names = list(weights)
    w = np.asarray([weights[n] for n in names], dtype=float)
    p = np.asarray([float(params[n]) for n in names], dtype=float)
    c = np.asarray(cov.loc[names, names], dtype=float)
    var = float(w @ c @ w)
    return float(w @ p), math.sqrt(max(var, 0.0))


def _near(values: np.ndarray, point: float, half: float, keep: "np.ndarray | None" = None) -> int:
    inside = np.abs(values - point) <= half
    if keep is not None:
        inside &= keep
    return int(inside.sum())


# -- the hand fitters ----------------------------------------------------------------


@dataclasses.dataclass
class AftFit:
    """A Weibull accelerated failure time fit: log T = mu + x beta + sigma W, W the standard minimum extreme value."""

    params: "dict[str, float]"
    bse: "dict[str, float]"
    sigma: float
    loglik: float
    converged: bool


def weibull_aft(time_: np.ndarray, event: np.ndarray, x: "dict[str, np.ndarray]",
                fixed_scale: "float | None" = None, max_iter: int = 100) -> AftFit:
    """The Weibull AFT by maximum likelihood (Newton with the analytic gradient and Hessian, step halving).

    The parameters are the intercept, one coefficient per column of
    ``x`` and log sigma (held at log ``fixed_scale`` where given: sigma 1
    is the exponential model, whose intercept is log(total time / events)).
    Standard errors from the inverse of the observed information.
    """
    names = ["intercept"] + list(x)
    n = len(time_)
    design = np.column_stack([np.ones(n)] + [np.asarray(x[k], dtype=float) for k in x])
    logt = np.log(np.asarray(time_, dtype=float))
    d = np.asarray(event, dtype=float)
    p = design.shape[1]
    free_scale = fixed_scale is None
    start = np.zeros(p + 1)
    start[0] = float(np.log(time_.sum() / max(d.sum(), 1.0)))
    start[p] = 0.0 if free_scale else math.log(fixed_scale)  # type: ignore[arg-type]

    def parts(theta: np.ndarray) -> "tuple[float, np.ndarray, np.ndarray]":
        eta = design @ theta[:p]
        s = theta[p]
        sigma = math.exp(s)
        z = (logt - eta) / sigma
        ez = np.exp(np.minimum(z, 700.0))
        ll = float(np.sum(d * (-s + z - logt) - ez))
        u = d - ez
        g_eta = design.T @ (-u / sigma)
        g_s = float(np.sum(-d - z * u))
        h_ee = -(design.T * (ez / sigma ** 2)) @ design
        h_es = design.T @ ((u - z * ez) / sigma)
        h_ss = float(np.sum(z * u - z * z * ez))
        grad = np.concatenate([g_eta, [g_s]])
        hess = np.zeros((p + 1, p + 1))
        hess[:p, :p] = h_ee
        hess[:p, p] = h_es
        hess[p, :p] = h_es
        hess[p, p] = h_ss
        return ll, grad, hess

    theta = start
    converged = False
    ll, grad, hess = parts(theta)
    for _ in range(max_iter):
        size = p + 1 if free_scale else p
        try:
            step = np.linalg.solve(-hess[:size, :size], grad[:size])
        except np.linalg.LinAlgError as error:
            raise AnalysisError("singular", "the Weibull model's information") from error
        moved = False
        factor = 1.0
        for _half in range(30):
            trial = theta.copy()
            trial[:size] += factor * step
            ll_t, grad_t, hess_t = parts(trial)
            if math.isfinite(ll_t) and ll_t >= ll - 1e-12:
                theta, ll, grad, hess = trial, ll_t, grad_t, hess_t
                moved = True
                break
            factor /= 2.0
        if not moved or float(np.max(np.abs(factor * step))) < 1e-9:
            converged = moved or float(np.max(np.abs(grad[:size]))) < 1e-6
            break
    size = p + 1 if free_scale else p
    try:
        cov = np.linalg.inv(-hess[:size, :size])
    except np.linalg.LinAlgError as error:
        raise AnalysisError("singular", "the Weibull model's information") from error
    se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    params = {name: float(theta[i]) for i, name in enumerate(names)}
    bse = {name: float(se[i]) for i, name in enumerate(names)}
    params["log_scale"] = float(theta[p])
    bse["log_scale"] = float(se[p]) if free_scale else 0.0
    return AftFit(params, bse, math.exp(theta[p]), ll, converged)


@dataclasses.dataclass
class Incidence:
    """The Aalen-Johansen cumulative incidence of each cause at the asked times, with delta-method standard errors."""

    value: "dict[tuple[int, float], float]"
    se: "dict[tuple[int, float], float]"
    at_risk: "dict[float, int]"


def aalen_johansen(time_: np.ndarray, cause: np.ndarray, at: "tuple[float, ...]",
                   causes: "tuple[int, ...]" = (1, 2)) -> Incidence:
    """The cumulative incidence of each cause by Aalen and Johansen, from times and causes (0 censored).

    At each distinct time t_j with n_j at risk (time at least t_j), d_kj
    ends by cause k and d_j by any: S(t_j) = S(t_j-) (1 - d_j / n_j) and
    F_k(t_j) = F_k(t_j-) + S(t_j-) d_kj / n_j; F_k(t) is its value at the
    last t_j at or before t. Ends and censorings at one time: the censored
    are at risk then. The variance is the delta method's
    (Marubini and Valsecchi): sum over t_j <= t of
    (F_k(t) - F_k(t_j))^2 d_j / (n_j (n_j - d_j))
    + S(t_j-)^2 d_kj (n_j - d_kj) / n_j^3
    - 2 (F_k(t) - F_k(t_j)) S(t_j-) d_kj / n_j^2.
    With no competing cause, F_1 is one minus Kaplan and Meier's curve.
    """
    t = np.asarray(time_, dtype=float)
    c = np.asarray(cause, dtype=int)
    order = np.argsort(t, kind="stable")
    t, c = t[order], c[order]
    n = len(t)
    distinct, first = np.unique(t, return_index=True)
    rows_after = n - first
    ends = {k: np.bincount(np.searchsorted(distinct, t[c == k]), minlength=len(distinct)) for k in causes}
    all_ends = np.bincount(np.searchsorted(distinct, t[c != 0]), minlength=len(distinct))
    surv_before = np.ones(len(distinct))
    surv = 1.0
    f = {k: np.zeros(len(distinct)) for k in causes}
    running = {k: 0.0 for k in causes}
    for j in range(len(distinct)):
        surv_before[j] = surv
        nj = rows_after[j]
        for k in causes:
            running[k] += surv * ends[k][j] / nj
            f[k][j] = running[k]
        surv *= 1.0 - all_ends[j] / nj
    value, se, risk = {}, {}, {}
    for point in at:
        last = int(np.searchsorted(distinct, point, side="right")) - 1
        risk[point] = int(rows_after[last + 1]) if last + 1 < len(distinct) else 0
        for k in causes:
            if last < 0:
                value[(k, point)], se[(k, point)] = 0.0, 0.0
                continue
            fk = f[k][last]
            nj = rows_after[: last + 1].astype(float)
            dj = all_ends[: last + 1].astype(float)
            dk = ends[k][: last + 1].astype(float)
            gap = fk - f[k][: last + 1]
            sb = surv_before[: last + 1]
            safe = np.where(nj - dj > 0, nj * (nj - dj), np.inf)
            var = float(np.sum(gap ** 2 * dj / safe) + np.sum(sb ** 2 * dk * (nj - dk) / nj ** 3)
                        - 2.0 * np.sum(gap * sb * dk / nj ** 2))
            value[(k, point)] = float(fk)
            se[(k, point)] = math.sqrt(max(var, 0.0))
    return Incidence(value, se, risk)


@dataclasses.dataclass
class MultinomialFit:
    """A multinomial model with a reference outcome: one coefficient vector per other outcome."""

    params: "dict[str, float]"
    bse: "dict[str, float]"
    loglik: float
    converged: bool


def multinomial(y: "list[str]", outcomes: "tuple[str, ...]", x: "dict[str, np.ndarray]",
                max_iter: int = 50) -> MultinomialFit:
    """The multinomial model by hand: outcome k against ``outcomes[0]``, log odds intercept + x beta_k.

    The softmax likelihood maximized by Newton's method with the analytic
    gradient X'(y_k - p_k) and Hessian blocks -X' diag(p_k (delta_kl -
    p_l)) X, step halving where the likelihood would fall; standard errors
    from the inverse of the observed information. Coefficients are keyed
    `<outcome>_<column>` (and `<outcome>_intercept`).
    """
    names = ["intercept"] + list(x)
    n = len(y)
    design = np.column_stack([np.ones(n)] + [np.asarray(x[k], dtype=float) for k in x])
    p = design.shape[1]
    others = outcomes[1:]
    m = len(others)
    target = np.zeros((n, m))
    for j, name in enumerate(others):
        target[:, j] = np.asarray([1.0 if v == name else 0.0 for v in y])
    if np.any(target.sum(axis=0) == 0) or float(target.sum()) == n:
        raise AnalysisError("level missing", "an outcome level holds no row")

    def parts(beta: np.ndarray) -> "tuple[float, np.ndarray, np.ndarray]":
        b = beta.reshape(m, p)
        eta = design @ b.T
        top = np.maximum(eta.max(axis=1), 0.0)
        ex = np.exp(eta - top[:, None])
        denom = np.exp(-top) + ex.sum(axis=1)
        prob = ex / denom[:, None]
        ll = float(np.sum(target * eta) - np.sum(top + np.log(denom)))
        grad = ((target - prob).T @ design).reshape(-1)
        hess = np.zeros((m * p, m * p))
        for k in range(m):
            for j in range(m):
                w = prob[:, k] * ((1.0 if k == j else 0.0) - prob[:, j])
                hess[k * p:(k + 1) * p, j * p:(j + 1) * p] = -(design.T * w) @ design
        return ll, grad, hess

    beta = np.zeros(m * p)
    ll, grad, hess = parts(beta)
    converged = False
    for _ in range(max_iter):
        try:
            step = np.linalg.solve(-hess, grad)
        except np.linalg.LinAlgError as error:
            raise AnalysisError("singular", "the multinomial model's information") from error
        factor = 1.0
        moved = False
        for _half in range(30):
            trial = beta + factor * step
            ll_t, grad_t, hess_t = parts(trial)
            if math.isfinite(ll_t) and ll_t >= ll - 1e-12:
                beta, ll, grad, hess = trial, ll_t, grad_t, hess_t
                moved = True
                break
            factor /= 2.0
        if not moved or float(np.max(np.abs(factor * step))) < 1e-10:
            converged = moved or float(np.max(np.abs(grad))) < 1e-6
            break
    try:
        cov = np.linalg.inv(-hess)
    except np.linalg.LinAlgError as error:
        raise AnalysisError("singular", "the multinomial model's information") from error
    se = np.sqrt(np.maximum(np.diag(cov), 0.0))
    params, bse = {}, {}
    for k, name in enumerate(others):
        for i, column in enumerate(names):
            params[f"{name}_{column}"] = float(beta[k * p + i])
            bse[f"{name}_{column}"] = float(se[k * p + i])
    return MultinomialFit(params, bse, ll, converged)


# -- ST7: clinic visits (F11, F15, F17) -------------------------------------------------


def _st7(v: B.View) -> "dict[str, np.ndarray]":
    """ST7's columns as an analyst derives them: years since the person's first visit from the dates, ordered by person and date."""
    held = _cache(v)
    if "st7" not in held:
        subject = np.asarray([s if s is not None else "" for s in _labels(v, "subject")], dtype=object)
        days = _days(v, "visit_date")
        frame = pd.DataFrame({"subject": subject, "days": days})
        first = frame.groupby("subject")["days"].transform("min").to_numpy(dtype=float)
        years = (days - first) / 365.25
        out = {
            "subject": subject, "days": days, "years": years,
            "arm": _flag(v, "arm", "B"), "male": _flag(v, "gender", "male"),
            "age_c": _numbers(v, "age") - 60.0, "sbp": _numbers(v, "sbp"),
            "controlled": _numbers(v, "controlled"), "visit": _numbers(v, "visit"),
        }
        order = np.lexsort((days, subject.astype(str)))
        out["order"] = order
        held["st7"] = out
    return held["st7"]  # type: ignore[return-value]


ST7_FIXED = ["intercept", "years", "arm", "arm_years", "arm_years_sq", "age", "male"]


def _st7_design(d: "dict[str, np.ndarray]", bend: bool = True) -> "tuple[dict[str, np.ndarray], np.ndarray]":
    y = d["sbp"]
    keep = _complete(y, d["years"], d["arm"], d["age_c"], d["male"]) & (d["subject"] != "")
    columns = {"intercept": np.ones(int(keep.sum())), "years": d["years"][keep], "arm": d["arm"][keep],
               "arm_years": (d["arm"] * d["years"])[keep], "age": d["age_c"][keep], "male": d["male"][keep]}
    if bend:
        columns["arm_years_sq"] = (d["arm"] * d["years"] ** 2)[keep]
    return columns, keep


# The random part of ST7's random-slope model reads the years in DECADES, centred on the real table's mean years. With
# the years as they stand, the slope's variance sits about ninety times under the intercept's on the scale statsmodels
# optimizes: L-BFGS stopped on 9 of 24 halves at table seeds 1 to 3 at 20,000 rows ("Gradient optimization failed",
# |grad| 100 to 500) or settled at a lower likelihood; in decades L-BFGS, BFGS, conjugate gradients and Powell settle
# at the one maximum (repair 1's probe). The slope's SD is stated per year.
RANDOM_YEARS = 10.0


def _st7_mixed(centre: float) -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F11: the linear mixed model with a random intercept and slope in years by REML, and its variance components.

        The random part's years are centred on the real table's mean years
        (`centre`, fixed in `plan_st7` as the growth curve's knots are), so
        the patient intercept is read where the visits are and its
        correlation with the slope is not an artefact of the origin, and
        read in decades (`RANDOM_YEARS`); the fixed part reads the years as
        the analysis computes them.
        """
        d = _st7(v)
        columns, keep = _st7_design(d)
        names = [n for n in ST7_FIXED if n in columns]
        exog = pd.DataFrame({n: columns[n] for n in names})
        exog_re = np.column_stack([np.ones(len(exog)), (columns["years"] - centre) / RANDOM_YEARS])
        result = _fit(lambda: MixedLM(d["sbp"][keep], exog, groups=d["subject"][keep], exog_re=exog_re).fit(
            reml=True, method=["lbfgs", "bfgs"]))
        _converged(result, "the random-slope model")
        params = getattr(result, "fe_params")
        bse = getattr(result, "bse_fe")
        n = int(keep.sum())
        out = []
        for name in names:
            tags = ("curvature",) if name == "arm_years_sq" else ()
            out += [Estimate(f"ST7/lmm:{name}", "F11", float(params[name]), float(bse[name]),
                             cell(columns[name]) if name != "intercept" else n, tags)]
        cov = np.asarray(getattr(result, "cov_re"), dtype=float)
        scale = float(getattr(result, "scale"))
        sd0, sd1 = math.sqrt(max(cov[0, 0], 0.0)), math.sqrt(max(cov[1, 1], 0.0))
        corr = cov[0, 1] / (sd0 * sd1) if sd0 > 0 and sd1 > 0 else math.nan
        sd1 /= RANDOM_YEARS
        for key, value in (("sd_patient", sd0), ("sd_slope", sd1), ("corr", corr), ("sd_residual", math.sqrt(scale))):
            if math.isfinite(value):
                out += [Estimate(f"ST7/lmm:{key}", "F11", float(value), None, n, ("varcomp",))]
        return out
    return run


def st7_intercept(v: B.View) -> "list[Estimate]":
    """F11: the random-intercept model by maximum likelihood (the ICC, K-BC-06's measure) and the serial correlation left in its residuals."""
    d = _st7(v)
    columns, keep = _st7_design(d, bend=False)
    names = ["intercept", "years", "arm", "arm_years", "age", "male"]
    exog = pd.DataFrame({n: columns[n] for n in names})
    result = _fit(lambda: MixedLM(d["sbp"][keep], exog, groups=d["subject"][keep]).fit(reml=False, method=["lbfgs",
                                                                                                         "bfgs"]))
    _converged(result, "the random-intercept model")
    var_p = float(np.asarray(getattr(result, "cov_re"), dtype=float)[0, 0])
    scale = float(getattr(result, "scale"))
    n = int(keep.sum())
    out = [Estimate("ST7/ri:icc", "F11", var_p / (var_p + scale), None, n, ("varcomp",)),
           Estimate("ST7/ri:arm_years", "F11", float(getattr(result, "fe_params")["arm_years"]),
                    float(getattr(result, "bse_fe")["arm_years"]), n)]
    # The residual left after the fixed effects and the person's own mean, lag one within a person in date order.
    fitted = exog.to_numpy() @ np.asarray(getattr(result, "fe_params"), dtype=float)
    resid = d["sbp"][keep] - fitted
    frame = pd.DataFrame({"s": d["subject"][keep].astype(str), "t": d["days"][keep], "r": resid})
    frame["r"] = frame["r"] - frame.groupby("s")["r"].transform("mean")
    frame = frame.sort_values(["s", "t"], kind="stable")
    same = frame["s"].to_numpy()[1:] == frame["s"].to_numpy()[:-1]
    r = frame["r"].to_numpy()
    a, b = r[:-1][same], r[1:][same]
    if len(a) >= 10 and float(np.std(a)) > 0 and float(np.std(b)) > 0:
        rho = float(np.corrcoef(a, b)[0, 1])
        out += [Estimate("ST7/serial:lag1", "F11", rho, (1.0 - rho * rho) / math.sqrt(len(a) - 3), len(a))]
    return out


def _gee(v: B.View, kind: str) -> "list[Estimate]":
    d = _st7(v)
    binary = kind == "bin"
    y = d["controlled"] if binary else d["sbp"]
    keep = _complete(y, d["years"], d["arm"], d["age_c"], d["male"], d["visit"]) & (d["subject"] != "")
    order = d["order"][keep[d["order"]]]
    columns = {"intercept": np.ones(len(order)), "years": d["years"][order], "arm": d["arm"][order],
               "age": d["age_c"][order], "male": d["male"][order]}
    if not binary:
        columns["arm_years"] = (d["arm"] * d["years"])[order]
    exog = pd.DataFrame(columns)
    family = sm.families.Binomial() if binary else sm.families.Gaussian()
    # AR(1) over the positions of a person's visits in date order (the grid form: the rows' order within a person).
    structure = Autoregressive(grid=True) if kind == "ar1" else Exchangeable()
    groups = d["subject"][order]
    result = _fit(lambda: GEE(y[order], exog, groups=groups, family=family, cov_struct=structure).fit(maxiter=100),
                  binomial=binary)
    _converged(result, f"the GEE ({kind})")
    if binary:
        _separation(result, exog, "the binomial GEE")
    prefix = f"ST7/gee_{kind}"
    out = _coefs(prefix, "F11", result, [n for n in columns if n != "intercept"], columns,
                 y[order] if binary else None)
    dep = float(np.asarray(structure.dep_params).reshape(-1)[0])
    out += [Estimate(f"{prefix}:working_corr", "F11", dep, None, len(order), ("workcorr",))]
    return out


def st7_gee_exchangeable(v: B.View) -> "list[Estimate]":
    """F11: the GEE with an exchangeable working correlation, robust standard errors."""
    return _gee(v, "exch")


def st7_gee_ar1(v: B.View) -> "list[Estimate]":
    """F11: the GEE with an AR(1) working correlation over a person's visits in date order."""
    return _gee(v, "ar1")


def st7_gee_binary(v: B.View) -> "list[Estimate]":
    """F11: the binomial GEE of the repeated yes-or-no outcome, exchangeable."""
    return _gee(v, "bin")


def st7_structure(v: B.View) -> "list[Estimate]":
    """F11: rows per person (margins: a column's own count) and the gaps between a person's visits in days."""
    d = _st7(v)
    subject = d["subject"][d["subject"] != ""]
    if len(subject) == 0:
        raise AnalysisError("empty filter", "no person")
    counts = np.asarray(pd.Series(subject.astype(str)).value_counts().to_numpy(), dtype=float)
    out = []
    persons = len(counts)
    for name, q in (("p50", 0.5), ("p90", 0.9), ("p99", 0.99)):
        out += [Estimate(f"ST7/rows:{name}", "F11", float(np.quantile(counts, q)), None, persons, ("margin",))]
    out += [Estimate("ST7/rows:mean", "F11", float(counts.mean()), float(counts.std() / math.sqrt(persons)),
                     persons, ("margin",))]
    keep = np.isfinite(d["days"]) & (d["subject"] != "")
    frame = pd.DataFrame({"s": d["subject"][keep].astype(str), "t": d["days"][keep]}).sort_values(["s", "t"])
    same = frame["s"].to_numpy()[1:] == frame["s"].to_numpy()[:-1]
    gaps = np.diff(frame["t"].to_numpy())[same]
    if len(gaps) >= 22:
        out += [Estimate("ST7/gaps:median", "F11", float(np.median(gaps)), None, len(gaps)),
                Estimate("ST7/gaps:p90", "F11", float(np.quantile(gaps, 0.9)), None, len(gaps))]
    return out


def st7_dropout(v: B.View) -> "list[Estimate]":
    """F17: who has no later visit, by the pressure at the visit and the years since entry (dropout on the previous value)."""
    d = _st7(v)
    keep = _complete(d["sbp"], d["years"], d["days"]) & (d["subject"] != "")
    frame = pd.DataFrame({"s": d["subject"][keep].astype(str), "t": d["days"][keep], "sbp10": (d["sbp"][keep] - 140.0)
                          / 10.0, "years": d["years"][keep]}).sort_values(["s", "t"], kind="stable")
    s = frame["s"].to_numpy()
    last = np.ones(len(s))
    last[:-1] = (s[1:] != s[:-1]).astype(float)
    columns = {"intercept": np.ones(len(s)), "sbp10": frame["sbp10"].to_numpy(), "years": frame["years"].to_numpy()}
    result = _glm(last, columns, sm.families.Binomial())
    return _coefs("ST7/dropout", "F17", result, ["sbp10", "years"], columns, last,
                  {"sbp10": ("missing",), "years": ("missing",)})


def _st7_growth(knots: "list[float]") -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F15: the growth curve, a restricted cubic spline in years by arm (knots fixed on the real table), a random intercept."""
        d = _st7(v)
        keep = _complete(d["sbp"], d["years"], d["arm"], d["age_c"], d["male"]) & (d["subject"] != "")
        years = d["years"][keep]
        arm = d["arm"][keep]
        basis = _rcs_columns(years, knots, "t")
        columns = {"intercept": np.ones(len(years))}
        columns.update(basis)
        columns["arm"] = arm
        for name, values in basis.items():
            columns[f"arm_{name}"] = arm * values
        columns["age"] = d["age_c"][keep]
        columns["male"] = d["male"][keep]
        exog = pd.DataFrame(columns)
        result = _fit(lambda: MixedLM(d["sbp"][keep], exog, groups=d["subject"][keep]).fit(reml=True, method=[
            "lbfgs", "bfgs"]))
        _converged(result, "the growth curve")
        holder = _FixedEffects(result)
        out = []
        for side, flag in (("A", 0.0), ("B", 1.0)):
            in_arm = arm == flag
            for point in (1.0, 2.0, 3.0, 4.0):
                weights = _curve_weights(knots, point, 0.0, flag)
                value, se = _contrast(holder, weights)
                support = min(_near(years, point, 0.5, in_arm), _near(years, 0.0, 0.5, in_arm))
                out += [Estimate(f"ST7/growth:{side}_{int(point)}", "F15", value, se, support, ("curve",))]
        # The growth curve's bend in arm B is read as a curve, inside its yardstick: a random intercept alone
        # understates its standard error about threefold and its ratio's noise at 20,000 rows is several times the
        # bend itself (the statistics check's item 3); ST7's curvature term is the random-slope model's
        # arm_years_sq.
        weights = _second_difference(knots, (0.0, 2.0, 4.0), 1.0)
        value, se = _contrast(holder, weights)
        support = min(_near(years, p, 0.5, arm == 1.0) for p in (0.0, 2.0, 4.0))
        out += [Estimate("ST7/growth:bend_B", "F15", value, se, support, ("curve",))]
        return out
    return run


class _FixedEffects:
    """A mixed model's fixed effects seen as a fit's `params` and `cov_params` (for `_contrast`)."""

    def __init__(self, result: object) -> None:
        self.params = getattr(result, "fe_params")
        names = list(self.params.index)
        cov = getattr(result, "cov_params")()
        self._cov = cov.loc[names, names]

    def cov_params(self) -> pd.DataFrame:
        return self._cov


def _rcs_columns(values: np.ndarray, knots: "list[float]", prefix: str) -> "dict[str, np.ndarray]":
    """A restricted cubic spline's columns (the linear term and each nonlinear term, E0b's `analyst_kit.rcs_term`)."""
    out = {f"{prefix}1": values.astype(float)}
    for j in range(len(knots) - 2):
        term = K.rcs_term(knots, j, 1.0)
        out[f"{prefix}{j + 2}"] = np.asarray([term(float(x)) for x in values], dtype=float)
    return out


def _rcs_point(point: float, knots: "list[float]", prefix: str) -> "dict[str, float]":
    out = {f"{prefix}1": point}
    for j in range(len(knots) - 2):
        out[f"{prefix}{j + 2}"] = K.rcs_term(knots, j, 1.0)(point)
    return out


def _curve_weights(knots: "list[float]", point: float, reference: float, arm: float) -> "dict[str, float]":
    at, base = _rcs_point(point, knots, "t"), _rcs_point(reference, knots, "t")
    weights = {k: at[k] - base[k] for k in at}
    if arm:
        weights.update({f"arm_{k}": at[k] - base[k] for k in at})
    return weights


def _second_difference(knots: "list[float]", points: "tuple[float, float, float]", arm: float) -> "dict[str, float]":
    a, b, c = (_rcs_point(p, knots, "t") for p in points)
    weights = {k: a[k] - 2.0 * b[k] + c[k] for k in a}
    if arm:
        weights.update({f"arm_{k}": a[k] - 2.0 * b[k] + c[k] for k in a})
    return weights


def plan_st7(real: B.View) -> "list[Analysis]":
    """ST7's analyses, with what they fix on the real table: the growth curve's knots, the random part's centre (the mean
    years) and the share of persons the variational check reads (`BAYES_PERSONS` over the real table's persons)."""
    d = _st7(real)
    years = d["years"]
    finite = np.sort(years[np.isfinite(years)])
    knots = [float(np.quantile(finite, q)) for q in (0.05, 0.275, 0.5, 0.725, 0.95)]
    centre = float(finite.mean()) if len(finite) else 0.0
    persons = len(set(d["subject"][d["subject"] != ""].astype(str).tolist()))
    share = min(1.0, BAYES_PERSONS / persons) if persons else 1.0
    return [Analysis("ST7/lmm", _st7_mixed(centre)), Analysis("ST7/ri", st7_intercept),
            Analysis("ST7/gee_exch", st7_gee_exchangeable), Analysis("ST7/gee_ar1", st7_gee_ar1),
            Analysis("ST7/gee_bin", st7_gee_binary), Analysis("ST7/structure", st7_structure),
            Analysis("ST7/dropout", st7_dropout), Analysis("ST7/growth", _st7_growth(knots)),
            Analysis("ST7/vb", _st7_bayes(share))]


# -- ST8: a treatment registry on start-stop rows (F12, F19, F21) ---------------------------------


ST8_TERMS = ["treated", "stage2", "stage3", "age10", "egfr_low"]


def _st8(v: B.View) -> "dict[str, object]":
    """ST8's rows and its persons: each person's follow-up, last status and baseline columns, as an analyst derives them."""
    held = _cache(v)
    if "st8" not in held:
        subject = np.asarray([s if s is not None else "" for s in _labels(v, "subject")], dtype=object)
        rows = {
            "subject": subject, "start": _numbers(v, "start_day") / 365.25, "stop": _numbers(v, "stop_day") / 365.25,
            "treated": _numbers(v, "treated"), "stage2": _flag(v, "stage", "II"), "stage3": _flag(v, "stage", "III"),
            "age10": (_numbers(v, "age") - 60.0) / 10.0, "egfr_low": _flag(v, "egfr_band", "low"),
            "status": _numbers(v, "status"), "male": _flag(v, "gender", "male"),
            "centre": np.asarray([c if c is not None else "" for c in _labels(v, "centre")], dtype=object),
        }
        frame = pd.DataFrame({k: rows[k] for k in ("subject", "start", "stop", "treated", "stage2", "stage3", "age10",
                                                   "egfr_low", "status", "male", "centre")})
        frame = frame[frame["subject"] != ""].sort_values(["subject", "start"], kind="stable")
        grouped = frame.groupby("subject", sort=False)
        persons = pd.DataFrame({
            "time": grouped["stop"].max(), "status": grouped["status"].last(), "ever": grouped["treated"].max(),
            "stage2": grouped["stage2"].first(), "stage3": grouped["stage3"].first(),
            "age10": grouped["age10"].first(), "egfr_low": grouped["egfr_low"].first(),
            "male": grouped["male"].first(), "centre": grouped["centre"].first(),
        })
        held["st8"] = {"rows": rows, "sorted": frame, "persons": persons}
    return held["st8"]  # type: ignore[return-value]


def _cox_cells(columns: "dict[str, np.ndarray]", status: np.ndarray) -> None:
    """E0b's event-counted cells for a Cox model's terms on this frame: a group with no event stops ('separation').

    statsmodels' PHReg keeps no record of whether its fit settled (its
    results hold the coefficients and their covariance only), and where
    every event of a frame falls in one group of an indicator its
    optimizer stops on a flat likelihood with no warning (skeptic 1's
    item 4: treated 24.716, standard error 6,291.5, read 'ok'); E0b's Cox
    stops there, so this one does too.
    """
    for name, values in columns.items():
        if cell(values, status) == 0:
            raise AnalysisError("separation", f"no event in a group of {name}")


def cox_start_stop(stop: np.ndarray, start: np.ndarray, status: np.ndarray,
                   columns: "dict[str, np.ndarray]") -> PHReg:
    """A Cox model on start-stop rows (Breslow's ties), each row at risk on (start, stop]: from the moment AFTER it
    starts, never at its own start.

    EXCLUSIVE STARTS (LANE MU RULINGS 6 (3), Codex's review, its item 3):
    statsmodels' PHReg counts a row at risk at every event time at or
    after its entry, so where a person's next row starts on the day
    another person's event falls, both of that person's rows stand in
    that event's risk set and the person is counted twice (ST8 at 20,000
    rows, table seed 1: 1,338 of its 1,569 days of an event of cause 1
    hold a row that starts that day). Each entry is handed in as the next
    float above it (`numpy.nextafter`), so a row is at risk at t exactly
    where start < t <= stop. Four rows at a coefficient of log 2 -- one
    person's exposure turning from 0 to 1 on day 1, another's event on
    day 1, a third exposed throughout -- read a partial likelihood of
    -log 4, not -log 6 (the gate file's case).
    """
    return PHReg(stop, pd.DataFrame(columns), status=status, entry=np.nextafter(start, np.inf))


def _st8_cox(v: B.View, cause: float, prefix: str) -> "list[Estimate]":
    rows = _st8(v)["rows"]  # type: ignore[index]
    keep = _complete(rows["start"], rows["stop"], rows["status"], *(rows[n] for n in ST8_TERMS))  # type: ignore[index]
    keep &= rows["stop"] > rows["start"]  # type: ignore[index]
    columns = {n: rows[n][keep] for n in ST8_TERMS}  # type: ignore[index]
    status = (rows["status"][keep] == cause).astype(float)  # type: ignore[index]
    _cox_cells(columns, status)
    # The model is BUILT inside `_fit`, as it is fitted there: PHReg's constructor refuses a start or stop below 0
    # (ValueError), which `_fit` reads as this analysis's 'fit error'; built outside, a twin that writes one such row
    # ended the whole measurement (the scoped verify 2's MINOR 1).
    result = _fit(lambda: cox_start_stop(rows["stop"][keep], rows["start"][keep], status, columns).fit())  # type: ignore[index]
    return _coefs(prefix, "F12", result, ST8_TERMS, columns, status)


def st8_cox_tv(v: B.View) -> "list[Estimate]":
    """F12: Cox on start-stop rows with entry times, the treatment counted from the day it starts."""
    return _st8_cox(v, 1.0, "ST8/cox_tv")


def st8_cox_competing(v: B.View) -> "list[Estimate]":
    """F12: the cause-specific Cox model of the competing event on the same rows."""
    return _st8_cox(v, 2.0, "ST8/cox_comp")


def _persons(v: B.View) -> pd.DataFrame:
    persons = _st8(v)["persons"]  # type: ignore[index]
    keep = np.isfinite(persons[["time", "status", "ever", "stage2", "stage3", "age10", "egfr_low"]].to_numpy()).all(axis=1)
    keep &= persons["time"].to_numpy() > 0
    out = persons[keep]
    if len(out) == 0:
        raise AnalysisError("empty filter", "no person")
    return out


def st8_cox_naive(v: B.View) -> "list[Estimate]":
    """F12: the naive model, treatment as 'ever treated' at entry (the immortal-time bias a twin must give back too)."""
    persons = _persons(v)
    names = ["ever", "stage2", "stage3", "age10", "egfr_low"]
    columns = {n: persons[n].to_numpy(dtype=float) for n in names}
    status = (persons["status"].to_numpy() == 1.0).astype(float)
    _cox_cells(columns, status)
    result = _fit(lambda: PHReg(persons["time"].to_numpy(dtype=float), pd.DataFrame(columns), status=status).fit())
    return _coefs("ST8/cox_naive", "F12", result, names, columns, status)


def st8_km(v: B.View) -> "list[Estimate]":
    """F12: Kaplan-Meier survival from the event (the competing event and censoring as censored) at 1, 3 and 5 years by stage."""
    persons = _persons(v)
    out = []
    stage = np.where(persons["stage3"].to_numpy() == 1.0, "III", np.where(persons["stage2"].to_numpy() == 1.0, "II", "I"))
    for level in ("I", "II", "III"):
        part = persons[stage == level]
        if len(part) < 2:
            continue
        status = (part["status"].to_numpy() == 1.0).astype(float)
        sf = _fit(lambda: SurvfuncRight(part["time"].to_numpy(dtype=float), status))
        times = np.asarray(getattr(sf, "surv_times"))
        prob = np.asarray(getattr(sf, "surv_prob"))
        se = np.asarray(getattr(sf, "surv_prob_se"))
        for point in (1.0, 3.0, 5.0):
            at = int(np.searchsorted(times, point, side="right")) - 1
            value, error = (1.0, 0.0) if at < 0 else (float(prob[at]), float(se[at]))
            ended = int(((part["time"].to_numpy() <= point) & (status == 1.0)).sum())
            out += [Estimate(f"ST8/km:{level}_{int(point)}", "F12", value, error if error > 0 else None,
                             min(ended, len(part) - ended))]
    return out


def st8_aft(v: B.View) -> "list[Estimate]":
    """F19: the Weibull accelerated failure time model on the per-person table (by hand), baseline columns."""
    persons = _persons(v)
    names = ["stage2", "stage3", "age10", "egfr_low"]
    x = {n: persons[n].to_numpy(dtype=float) for n in names}
    status = (persons["status"].to_numpy() == 1.0).astype(float)
    fit = weibull_aft(persons["time"].to_numpy(dtype=float), status, x)
    if not fit.converged:
        raise AnalysisError("no convergence", "the Weibull model")
    out = []
    events = int(status.sum())
    for name in ["intercept"] + names + ["log_scale"]:
        support = cell(x[name], status) if name in x else min(events, len(status) - events)
        out += [Estimate(f"ST8/aft:{name}", "F19", fit.params[name], fit.bse[name] or None, support)]
    return out


def st8_incidence(v: B.View) -> "list[Estimate]":
    """F19: the Aalen-Johansen incidence of the event and of the competing event at 1, 3 and 5 years (by hand)."""
    persons = _persons(v)
    cause = persons["status"].to_numpy(dtype=float)
    cause = np.where(np.isin(cause, (1.0, 2.0)), cause, 0.0).astype(int)
    found = aalen_johansen(persons["time"].to_numpy(dtype=float), cause, (1.0, 3.0, 5.0))
    out = []
    for k, label in ((1, "event"), (2, "competing")):
        for point in (1.0, 3.0, 5.0):
            ended = int(((persons["time"].to_numpy() <= point) & (cause == k)).sum())
            out += [Estimate(f"ST8/aj:{label}_{int(point)}", "F19", found.value[(k, point)],
                             found.se[(k, point)] or None, min(ended, len(cause) - ended))]
    return out


def st8_censoring(v: B.View) -> "list[Estimate]":
    """F19: the share of persons censored, centre by centre."""
    persons = _persons(v)
    censored = (persons["status"].to_numpy() == 0.0).astype(float).tolist()
    centres = persons["centre"].astype(str).to_numpy()
    out = []
    for level in sorted(set(centres.tolist())):
        if level:
            out += B.rate(f"ST8/censored:{level}", "F19", censored, [c == level for c in centres])
    return out


def st8_rules(v: B.View) -> "list[Estimate]":
    """F19: the four structure rules every row keeps, each read as E0b's rule (the share breaking it; its yardstick 0)."""
    frame = _st8(v)["sorted"]  # type: ignore[index]
    start = frame["start"].to_numpy(dtype=float)
    stop = frame["stop"].to_numpy(dtype=float)
    out = B.rule("ST8/rule:start_below_stop", "F19", [float(not (a < b)) if a == a and b == b else math.nan
                                                       for a, b in zip(start, stop)])
    s = frame["subject"].to_numpy()
    first = np.ones(len(s), dtype=bool)
    first[1:] = s[1:] != s[:-1]
    last = np.ones(len(s), dtype=bool)
    last[:-1] = s[1:] != s[:-1]
    joined = np.ones(len(s), dtype=bool)
    joined[1:] = np.isclose(start[1:], stop[:-1])
    contiguous = np.where(first, np.isclose(start, 0.0), joined)
    broken_person = pd.Series(~contiguous).groupby(s).any()
    out += B.rule("ST8/rule:contiguous_from_0", "F19", broken_person.astype(float).tolist())
    status = frame["status"].to_numpy(dtype=float)
    ended = np.isfinite(status) & (status != 0.0)
    early = pd.Series(ended & ~last).groupby(s).any() | (pd.Series(ended.astype(int)).groupby(s).sum() > 1)
    out += B.rule("ST8/rule:one_end_on_the_last_row", "F19", early.astype(float).tolist())
    treated = frame["treated"].to_numpy(dtype=float)
    back = np.zeros(len(s), dtype=bool)
    back[1:] = (~first[1:]) & (treated[:-1] == 1.0) & (treated[1:] == 0.0)
    out += B.rule("ST8/rule:treated_never_returns", "F19", pd.Series(back).groupby(s).any().astype(float).tolist())
    return out


def plan_st8(real: B.View) -> "list[Analysis]":
    persons = _persons(real)
    stage = np.where(persons["stage3"].to_numpy() == 1.0, "III", np.where(persons["stage2"].to_numpy() == 1.0, "II", "I"))
    return [Analysis("ST8/cox_tv", st8_cox_tv), Analysis("ST8/cox_naive", st8_cox_naive),
            Analysis("ST8/cox_comp", st8_cox_competing), Analysis("ST8/km", st8_km), Analysis("ST8/aft", st8_aft),
            Analysis("ST8/aj", st8_incidence), Analysis("ST8/censored", st8_censoring),
            Analysis("ST8/rules", st8_rules),
            Analysis("ST8/t1", _table1("ST8/t1", _st8_table1, t1_pairs(real, _st8_table1, sorted(set(stage.tolist())))))]


def _st8_table1(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    persons = _persons(v)
    stage = np.where(persons["stage3"].to_numpy() == 1.0, "III", np.where(persons["stage2"].to_numpy() == 1.0, "II", "I"))
    columns = {"age10": persons["age10"].tolist(), "male": persons["male"].tolist(),
               "egfr_low": persons["egfr_low"].tolist(), "ever_treated": persons["ever"].tolist(),
               "followup_years": persons["time"].tolist(),
               "censored": (persons["status"].to_numpy() == 0.0).astype(float).tolist()}
    return list(stage.tolist()), columns


# -- Table 1 by group (F21) --------------------------------------------------------------


T1_Z = 3.0


def _group_difference(values: "list[float]", groups: "list[str | None]", level: str,
                      reference: str) -> "tuple[float, float, int] | None":
    """A column's mean (or share) in one group minus its mean in the reference group, its standard error and its smallest cell."""
    a = np.asarray([x for x, g in zip(values, groups) if g == level and x == x], dtype=float)
    b = np.asarray([x for x, g in zip(values, groups) if g == reference and x == x], dtype=float)
    if len(a) < 2 or len(b) < 2:
        return None
    se = math.sqrt(float(a.var(ddof=1)) / len(a) + float(b.var(ddof=1)) / len(b))
    if np.all((a == 0.0) | (a == 1.0)) and np.all((b == 0.0) | (b == 1.0)):
        support = int(min(a.sum(), len(a) - a.sum(), b.sum(), len(b) - b.sum()))
    else:
        support = min(len(a), len(b))
    return float(a.mean() - b.mean()), se, support


def t1_pairs(real: B.View, read: "Callable[[B.View], tuple[list[str | None], dict[str, list[float]]]]",
             levels: "list[str]") -> "list[tuple[str, str, str]]":
    """The columns Table 1 by group shows apart, fixed on the real table: (column, level, reference level) where the real
    difference from the reference group stands 3 standard errors from 0 (a column the group does not move is no joint
    structure, and a column-wise shuffle keeps it)."""
    groups, columns = read(real)
    reference = levels[0]
    out = []
    for level in levels[1:]:
        for name, values in columns.items():
            found = _group_difference(values, groups, level, reference)
            if found is not None and found[1] > 0 and abs(found[0] / found[1]) >= T1_Z and found[2] >= B.SUPPORT:
                out += [(name, level, reference)]
    return out


def _table1(prefix: str, read: "Callable[[B.View], tuple[list[str | None], dict[str, list[float]]]]",
            pairs: "list[tuple[str, str, str]]") -> "Callable[[B.View], list[Estimate]]":
    """F21: Table 1 by group: each shown column's mean (or share) in a group minus the reference group's."""
    def run(v: B.View) -> "list[Estimate]":
        groups, columns = read(v)
        out = []
        for name, level, reference in pairs:
            found = _group_difference(columns.get(name, []), groups, level, reference)
            if found is not None:
                out += [Estimate(f"{prefix}:{name}@{level}", "F21", found[0], found[1] or None, found[2])]
        return out
    return run


def table1_smd(real: B.View, other: B.View, read: "Callable[[B.View], tuple[list[str | None], dict[str, list[float]]]]",
               levels: "list[str]") -> float:
    """The largest absolute standardized difference of a column's mean within a group, the frame against the real table.

    A MISSING RESULT IS NEVER A GOOD RESULT (Codex's review of the lane,
    its item 1; LANE MU RULINGS 6 (1)): every comparison the real table
    offers (a group of a column with two values or more) is made; where
    the frame cannot make it -- it replaced the group's label, lacks the
    column or holds fewer than two values there -- that is a difference
    (infinity), never a comparison skipped; two constants that differ
    (real values all 1 against the frame's all 0: both SDs 0) are a
    difference (infinity), two equal constants none.
    """
    rg, rc = read(real)
    og, oc = read(other)
    worst = 0.0
    for level in levels:
        for name in rc:
            a = np.asarray([x for x, g in zip(rc[name], rg) if g == level and x == x], dtype=float)
            if len(a) < 2:
                continue
            b = np.asarray([x for x, g in zip(oc.get(name, []), og) if g == level and x == x], dtype=float)
            if len(b) < 2:
                return math.inf
            gap = abs(float(a.mean()) - float(b.mean()))
            spread = math.sqrt((float(a.var(ddof=1)) + float(b.var(ddof=1))) / 2.0)
            if spread > 0:
                worst = max(worst, gap / spread)
            elif gap > 0:
                return math.inf
    return worst


# -- ST9: the cohort (F13, F15, F21; F14 below) -----------------------------------------------


def _st9(v: B.View) -> "dict[str, np.ndarray]":
    held = _cache(v)
    if "st9" not in held:
        age = _numbers(v, "age")
        a = (age - 60.0) / 10.0
        diabetes = _numbers(v, "diabetes")
        smoker = _flag(v, "smoker", "yes")
        lactate = _numbers(v, "lactate")
        creatinine = _numbers(v, "creatinine")
        sbp = _numbers(v, "sbp")
        held["st9"] = {
            "age": age, "a": a, "a2": a * a, "sbp": sbp, "sbp10": (sbp - 130.0) / 10.0, "diabetes": diabetes,
            "smoker": smoker, "diabetes_smoker": diabetes * smoker,
            "lactate": lactate, "lactate_over2": np.where(np.isfinite(lactate), (lactate > 2.0).astype(float), np.nan),
            "creatinine": creatinine, "creat_hinge": np.maximum(0.0, creatinine - U.ST9_HINGE),
            "treatment": _numbers(v, "treatment"), "female": _flag(v, "gender", "female"),
            "lab1": _numbers(v, "lab1"), "lab2": _numbers(v, "lab2"), "lab3": _numbers(v, "lab3"),
            "body_mass": _numbers(v, "body_mass"), "crp": _numbers(v, "crp"), "died": _numbers(v, "died"),
        }
    return held["st9"]  # type: ignore[return-value]


ST9_DEATH = ["a", "a2", "sbp10", "diabetes", "smoker", "diabetes_smoker", "lactate_over2", "creat_hinge",
             "treatment", "female", "lab1"]
ST9_KEYS = {"a": "age", "a2": "age_sq"}


def _glm(y: np.ndarray, columns: "dict[str, np.ndarray]", family: object) -> object:
    """A GLM fitted, settled, and -- a binomial one -- not separated (`_not_separated`, `_separation`)."""
    exog = pd.DataFrame(columns)
    binomial = isinstance(family, sm.families.Binomial)
    result = _fit(lambda: sm.GLM(y, exog, family=family).fit(), binomial=binomial)
    _converged(result, "the GLM")
    if binomial:
        _separation(result, columns, "the GLM")
    return result


def st9_quadratic(v: B.View) -> "list[Estimate]":
    """F15: the death model as generated: a quadratic age term, the interaction, a threshold step and a hinge."""
    d = _st9(v)
    keep = _complete(d["died"], *(d[n] for n in ST9_DEATH))
    columns = {"intercept": np.ones(int(keep.sum()))}
    columns.update({n: d[n][keep] for n in ST9_DEATH})
    result = _glm(d["died"][keep], columns, sm.families.Binomial())
    out = []
    y = d["died"][keep]
    for name in ST9_DEATH:
        tags = ("curvature",) if name in ("a2", "creat_hinge") else ()
        out += [Estimate(f"ST9/quad:{ST9_KEYS.get(name, name)}", "F15", float(getattr(result, "params")[name]),
                         float(getattr(result, "bse")[name]), cell(columns[name], y), tags)]
    return out


def st9_pressure(v: B.View) -> "list[Estimate]":
    """F15: the pressure's least squares on age with its quadratic term, body mass and smoking."""
    d = _st9(v)
    keep = _complete(d["sbp"], d["a"], d["body_mass"], d["smoker"])
    columns = {"intercept": np.ones(int(keep.sum())), "a": d["a"][keep], "a2": d["a2"][keep],
               "body_mass": d["body_mass"][keep] - 28.0, "smoker": d["smoker"][keep]}
    result = _glm(d["sbp"][keep], columns, sm.families.Gaussian())
    out = []
    for name in ("a", "a2", "body_mass", "smoker"):
        tags = ("curvature",) if name == "a2" else ()
        out += [Estimate(f"ST9/sbp:{ST9_KEYS.get(name, name)}", "F15", float(getattr(result, "params")[name]),
                         float(getattr(result, "bse")[name]), cell(columns[name]), tags)]
    return out


def st9_spline(v: B.View) -> "list[Estimate]":
    """F15: the death model with E0b's age spline (`analyst_battery.AGE_KNOTS`), read on its age grid against age 60."""
    d = _st9(v)
    others = [n for n in ST9_DEATH if n not in ("a", "a2")]
    keep = _complete(d["died"], d["age"], *(d[n] for n in others))
    age = d["age"][keep]
    columns = {"intercept": np.ones(len(age))}
    columns.update(_rcs_columns(age / 10.0, [k / 10.0 for k in B.AGE_KNOTS], "s"))
    columns.update({n: d[n][keep] for n in others})
    result = _glm(d["died"][keep], columns, sm.families.Binomial())
    y = d["died"][keep]
    knots = [k / 10.0 for k in B.AGE_KNOTS]
    out = []
    base = _rcs_point(6.0, knots, "s")
    for point in B.AGE_GRID:
        at = _rcs_point(point / 10.0, knots, "s")
        value, se = _contrast(result, {k: at[k] - base[k] for k in at})
        inside = np.abs(age - point) <= 5.0
        near60 = np.abs(age - 60.0) <= 5.0
        support = min(int(min((y[inside] == 1).sum(), (y[inside] == 0).sum())),
                      int(min((y[near60] == 1).sum(), (y[near60] == 0).sum())))
        out += [Estimate(f"ST9/spline:age_{int(point)}", "F15", value, se, support, ("curve",))]
    a, b, c = (_rcs_point(p, knots, "s") for p in (4.0, 6.0, 8.0))
    value, se = _contrast(result, {k: a[k] - 2.0 * b[k] + c[k] for k in a})
    support = min(int(min((y[np.abs(age - p) <= 5.0] == 1).sum(), (y[np.abs(age - p) <= 5.0] == 0).sum()))
                  for p in (40.0, 60.0, 80.0))
    out += [Estimate("ST9/spline:bend", "F15", value, se, support, ("curvature",))]
    return out


def _st9_gam(knots: "dict[str, tuple[list[float], float, float]]") -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F15: a GAM with fixed penalties on age and body mass (B-spline knots fixed on the real table), read on the age grid."""
        d = _st9(v)
        linear = [n for n in ST9_DEATH if n not in ("a", "a2")]
        keep = _complete(d["died"], d["age"], d["body_mass"], *(d[n] for n in linear))
        smooth = np.column_stack([d["age"][keep], d["body_mass"][keep]])
        smooth = np.column_stack([np.clip(smooth[:, 0], knots["age"][1], knots["age"][2]),
                                  np.clip(smooth[:, 1], knots["body_mass"][1], knots["body_mass"][2])])
        kwds = [{"knots": np.asarray(knots[name][0]), "lower_bound": knots[name][1], "upper_bound": knots[name][2]}
                for name in ("age", "body_mass")]
        splines = _fit(lambda: BSplines(smooth, df=[6, 6], degree=[3, 3], knot_kwds=kwds))
        exog = pd.DataFrame({"intercept": np.ones(int(keep.sum())), **{n: d[n][keep] for n in linear}})
        result = _fit(lambda: GLMGam(d["died"][keep], exog=exog, smoother=splines, alpha=[1.0, 1.0],
                                     family=sm.families.Binomial()).fit(), binomial=True)
        _converged(result, "the GAM")
        _separation(result, exog, "the GAM")
        params = np.asarray(getattr(result, "params"), dtype=float)
        cov = np.asarray(getattr(result, "cov_params")(), dtype=float)
        k_exog = exog.shape[1]
        age_spline = getattr(splines, "smoothers")[0]
        mask = np.asarray(getattr(splines, "mask")[0], dtype=bool)
        index = k_exog + np.flatnonzero(mask)
        base = np.asarray(age_spline.transform(np.asarray([60.0])), dtype=float)[0]
        y = d["died"][keep]
        age = d["age"][keep]
        out = []
        for point in B.AGE_GRID:
            if not knots["age"][1] <= point <= knots["age"][2]:
                continue
            row = np.asarray(age_spline.transform(np.asarray([point])), dtype=float)[0] - base
            value = float(row @ params[index])
            se = math.sqrt(max(float(row @ cov[np.ix_(index, index)] @ row), 0.0))
            inside = np.abs(age - point) <= 5.0
            support = int(min((y[inside] == 1).sum(), (y[inside] == 0).sum()))
            out += [Estimate(f"ST9/gam:age_{int(point)}", "F15", value, se, support, ("curve",))]
        return out
    return run


def _scales(real: B.View) -> "dict[str, tuple[float, float]]":
    """Each penalized column's mean and SD on the real table (fixed there, as a model fitted there is applied)."""
    d = _st9(real)
    out = {}
    for name in ST9_PENALIZED:
        values = d[name][np.isfinite(d[name])]
        sd = float(values.std()) if len(values) > 1 else 1.0
        out[name] = (float(values.mean()) if len(values) else 0.0, sd if sd > 0 else 1.0)
    return out


def plan_st9(real: B.View) -> "list[Analysis]":
    d = _st9(real)
    knots = {}
    for name in ("age", "body_mass"):
        values = np.sort(d[name][np.isfinite(d[name])])
        inner = [float(np.quantile(values, q)) for q in (1.0 / 3.0, 2.0 / 3.0)]
        knots[name] = (inner, float(values[0]), float(values[-1]))
    levels = ["0", "1"]
    scales = _scales(real)
    return [Analysis("ST9/lasso", _st9_penalized(scales, selection(real, scales))), Analysis("ST9/gmm", st9_mixture),
            Analysis("ST9/quad", st9_quadratic), Analysis("ST9/sbp", st9_pressure), Analysis("ST9/spline", st9_spline),
            Analysis("ST9/gam", _st9_gam(knots)), Analysis("ST9/prop", st9_propensity),
            Analysis("ST9/t1", _table1("ST9/t1", _st9_table1, t1_pairs(real, _st9_table1, levels)))]


def _st9_table1(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    d = _st9(v)
    groups = [None if x != x else str(int(x)) for x in d["treatment"]]
    columns = {name: d[name].tolist() for name in ("age", "body_mass", "sbp", "lactate", "creatinine", "lab1", "lab2",
                                                   "lab3", "crp", "female", "smoker", "diabetes", "died")}
    return groups, columns


ST9_SCORE = ["a", "diabetes", "female", "sbp10"]


def _score(d: "dict[str, np.ndarray]") -> "tuple[np.ndarray, dict[str, np.ndarray], object]":
    keep = _complete(d["treatment"], d["died"], *(d[n] for n in ST9_SCORE))
    columns = {"intercept": np.ones(int(keep.sum()))}
    columns.update({n: d[n][keep] for n in ST9_SCORE})
    result = _glm(d["treatment"][keep], columns, sm.families.Binomial())
    return keep, columns, result


def balance(x: "dict[str, np.ndarray]", t: np.ndarray, w: "np.ndarray | None" = None) -> float:
    """The largest absolute standardized mean difference between the treated and the untreated (weighted where given)."""
    w = np.ones(len(t)) if w is None else w
    worst = 0.0
    for values in x.values():
        m1 = float(np.average(values[t == 1], weights=w[t == 1]))
        m0 = float(np.average(values[t == 0], weights=w[t == 0]))
        spread = math.sqrt((float(values[t == 1].var()) + float(values[t == 0].var())) / 2.0)
        if spread > 0:
            worst = max(worst, abs(m1 - m0) / spread)
    return worst


def st9_propensity(v: B.View) -> "list[Estimate]":
    """F13: the treatment's model and its AUC, the weighted risk difference and matching on the score's log odds."""
    d = _st9(v)
    keep, columns, result = _score(d)
    t = d["treatment"][keep]
    y = d["died"][keep]
    out = []
    for name in ST9_SCORE:
        key = ST9_KEYS.get(name, name)
        out += [Estimate(f"ST9/prop:{key}", "F13", float(getattr(result, "params")[name]),
                         float(getattr(result, "bse")[name]), cell(columns[name], t))]
    e = np.clip(np.asarray(getattr(result, "fittedvalues"), dtype=float), 1e-6, 1.0 - 1e-6)
    treated, untreated = int(t.sum()), int(len(t) - t.sum())
    if treated < 2 or untreated < 2:
        raise AnalysisError("empty filter", "one arm holds no person")
    auc = float(roc_auc_score(t, e))
    q1, q2 = auc / (2.0 - auc), 2.0 * auc * auc / (1.0 + auc)
    auc_se = math.sqrt(max(auc * (1 - auc) + (treated - 1) * (q1 - auc * auc) + (untreated - 1) * (q2 - auc * auc), 0.0)
                       / (treated * untreated))
    out += [Estimate("ST9/prop:auc", "F13", auc, auc_se, min(treated, untreated))]
    w1, w0 = t / e, (1.0 - t) / (1.0 - e)
    mu1, mu0 = float(np.sum(w1 * y) / np.sum(w1)), float(np.sum(w0 * y) / np.sum(w0))
    var = float(np.sum((w1 * (y - mu1)) ** 2) / np.sum(w1) ** 2 + np.sum((w0 * (y - mu0)) ** 2) / np.sum(w0) ** 2)
    support = int(min((y[t == 1] == 1).sum(), (y[t == 1] == 0).sum(), (y[t == 0] == 1).sum(), (y[t == 0] == 0).sum()))
    out += [Estimate("ST9/ate:weighting", "F13", mu1 - mu0, math.sqrt(var), support)]
    odds = np.log(e / (1.0 - e))
    caliper = 0.2 * float(odds.std())
    pool = np.flatnonzero(t == 0)
    pool = pool[np.argsort(odds[pool], kind="stable")]
    sorted_odds = odds[pool]
    diffs = []
    for i in np.flatnonzero(t == 1):
        at = int(np.searchsorted(sorted_odds, odds[i]))
        best, gap = -1, math.inf
        for j in (at - 1, at):
            if 0 <= j < len(pool) and abs(sorted_odds[j] - odds[i]) < gap:
                best, gap = j, abs(sorted_odds[j] - odds[i])
        if best >= 0 and gap <= caliper:
            diffs += [y[i] - y[pool[best]]]
    if len(diffs) >= 2:
        # NO STANDARD ERROR (LANE MU RULINGS 6 (4), Codex's review, its item 4): matching keeps each control in the pool,
        # so one control stands in several pairs (ST9 at 20,000 rows, table seed 1: 6,734 pairs on 3,298 controls, one
        # used 16 times), and the pairs are not independent: their SD over sqrt(pairs) read 0.005404 where the
        # generator's own variances with the reuse read 0.008115, z 5.85 against 3.90. The estimate is read inside its
        # half-split yardstick alone, which carries the reuse; no significance, strong flip or SE ratio reads it.
        out += [Estimate("ST9/ate:matching", "F13", float(np.mean(np.asarray(diffs, dtype=float))), None, support)]
    return out


def st9_balance(v: B.View) -> "tuple[float, float]":
    """The frame's own balance: the largest absolute standardized difference before and after its own weighting."""
    d = _st9(v)
    keep, columns, result = _score(d)
    t = d["treatment"][keep]
    e = np.clip(np.asarray(getattr(result, "fittedvalues"), dtype=float), 1e-6, 1.0 - 1e-6)
    x = {n: columns[n] for n in ST9_SCORE}
    w = t / e + (1.0 - t) / (1.0 - e)
    return balance(x, t), balance(x, t, w)


# -- F14: prediction models trained on a frame, tested on the real table -------------------


def _st9_features(v: B.View) -> "tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]":
    """ST9's prediction rows: every patient, death from the columns a clinician has (crp kept with its empty cells)."""
    d = _st9(v)
    names = ["age", "female", "body_mass", "smoker", "sbp", "diabetes", "lactate", "creatinine", "lab1", "lab2",
             "lab3", "treatment", "crp"]
    rows = np.arange(v.rows)
    return {n: d[n] for n in names}, d["died"], rows


def _st7_features(v: B.View) -> "tuple[dict[str, np.ndarray], np.ndarray, np.ndarray]":
    """ST7's prediction rows: each visit after a person's first, the yes-or-no outcome from the last visit's and the person's columns."""
    d = _st7(v)
    order = d["order"]
    s = d["subject"][order].astype(str)
    previous = np.full(len(order), np.nan)
    same = np.zeros(len(order), dtype=bool)
    same[1:] = (s[1:] == s[:-1]) & (s[1:] != "")
    previous[1:] = np.where(same[1:], d["controlled"][order][:-1], np.nan)
    keep = np.isfinite(previous)
    rows = order[keep]
    columns = {"previous": previous[keep], "years": d["years"][rows], "arm": d["arm"][rows], "age_c": d["age_c"][rows],
               "male": d["male"][rows]}
    return columns, d["controlled"][rows], rows


def _model_rows(columns: "dict[str, np.ndarray]", y: np.ndarray, rows: np.ndarray, glm_terms: bool,
                knots: "list[float] | None") -> "tuple[np.ndarray, np.ndarray]":
    """The design of a prediction model on some rows: the GLM's (with a spline in age and the interaction), or the raw columns."""
    if not glm_terms:
        return np.column_stack([columns[k][rows] for k in columns]), y[rows]
    keep = rows[np.all(np.isfinite(np.column_stack([columns[k][rows] for k in columns if k != "crp"]
                                                   + [y[rows]])), axis=1)]
    parts = [np.ones(len(keep))]
    for name, values in columns.items():
        if name == "crp":
            continue
        if name == "age" and knots is not None:
            parts += list(_rcs_columns(values[keep] / 10.0, [k / 10.0 for k in knots], "s").values())
        else:
            parts += [values[keep]]
    if "diabetes" in columns and "smoker" in columns:
        parts += [columns["diabetes"][keep] * columns["smoker"][keep]]
    if "arm" in columns and "years" in columns:
        parts += [columns["arm"][keep] * columns["years"][keep]]
    return np.column_stack(parts), y[keep]


@dataclasses.dataclass
class Trained:
    """A prediction model fitted on one frame: the GLM's coefficients or the booster."""

    kind: str
    model: object


def _train(columns: "dict[str, np.ndarray]", y: np.ndarray, rows: np.ndarray, kind: str,
           knots: "list[float] | None") -> Trained:
    if kind == "glm":
        design, target = _model_rows(columns, y, rows, True, knots)
        if len(target) < 10 or target.min() == target.max():
            raise AnalysisError("empty filter", "no outcome to learn")
        result = _fit(lambda: sm.GLM(target, design, family=sm.families.Binomial()).fit(), binomial=True)
        _converged(result, "the prediction model")
        _separation(result, design, "the prediction model")
        return Trained(kind, result)
    design, target = _model_rows(columns, y, rows, False, None)
    finite = np.isfinite(target)
    if finite.sum() < 10 or np.nanmin(target) == np.nanmax(target):
        raise AnalysisError("empty filter", "no outcome to learn")
    booster = HistGradientBoostingClassifier(max_iter=100, random_state=0, early_stopping=False)
    with one_openmp_thread():
        model = _fit(lambda: booster.fit(design[finite], target[finite]))
    return Trained(kind, model)


def _predict(trained: Trained, columns: "dict[str, np.ndarray]", y: np.ndarray, rows: np.ndarray,
             knots: "list[float] | None") -> "tuple[np.ndarray, np.ndarray]":
    if trained.kind == "glm":
        design, target = _model_rows(columns, y, rows, True, knots)
        return np.asarray(getattr(trained.model, "predict")(design), dtype=float), target
    design, target = _model_rows(columns, y, rows, False, None)
    finite = np.isfinite(target)
    with one_openmp_thread():
        found = getattr(trained.model, "predict_proba")(design[finite])[:, 1]
    return np.asarray(found, dtype=float), target[finite]


def scores(p: np.ndarray, y: np.ndarray) -> "dict[str, float]":
    """A model's predictions against outcomes: AUC, calibration slope and intercept (on the log odds), Brier score."""
    p = np.clip(p, 1e-6, 1.0 - 1e-6)
    odds = np.log(p / (1.0 - p))
    if y.min() == y.max():
        raise AnalysisError("empty filter", "one outcome only")
    design = np.column_stack([np.ones(len(y)), odds])
    slope_fit = _fit(lambda: sm.GLM(y, design, family=sm.families.Binomial()).fit(), binomial=True)
    in_large = _fit(lambda: sm.GLM(y, np.ones((len(y), 1)), family=sm.families.Binomial(), offset=odds).fit(),
                    binomial=True)
    _converged(slope_fit, "the calibration slope")
    _converged(in_large, "the calibration intercept")
    _separation(slope_fit, design, "the calibration slope")
    _separation(in_large, np.ones((len(y), 1)), "the calibration intercept")
    return {"auc": float(roc_auc_score(y, p)), "slope": float(np.asarray(getattr(slope_fit, "params"))[1]),
            "intercept": float(np.asarray(getattr(in_large, "params"))[0]), "brier": float(np.mean((p - y) ** 2))}


PREDICTION = {"ST9": (_st9_features, B.AGE_KNOTS), "ST7": (_st7_features, None)}
PREDICTION_METRICS = ("auc", "slope", "intercept", "brier")


def tstr_yardstick(table: str, real: B.View, g: "list[int]") -> "dict[str, tuple[float, float]]":
    """The real table's own TRTR, each metric of each model: its half A model on half B (split 0), and its yardstick.

    The yardstick of a metric is the root mean square, over the four
    splits, of (half A's model on half B) minus (half B's on half A):
    E0b's F8 rule (`analyst_battery.run_table`).
    """
    features, knots = PREDICTION[table]
    columns, y, rows = features(real)
    rows_g = np.asarray(g, dtype=int)[rows]
    out: "dict[str, tuple[float, float]]" = {}
    for kind in ("glm", "hgb"):
        diffs: "dict[str, list[float]]" = {m: [] for m in PREDICTION_METRICS}
        first: "dict[str, float]" = {}
        try:
            for s in range(4):
                a = np.flatnonzero(((rows_g >> s) & 1) == 0)
                b = np.flatnonzero(((rows_g >> s) & 1) == 1)
                ab = scores(*_predict(_train(columns, y, a, kind, knots), columns, y, b, knots))
                ba = scores(*_predict(_train(columns, y, b, kind, knots), columns, y, a, knots))
                if s == 0:
                    first = ab
                for m in PREDICTION_METRICS:
                    diffs[m] += [ab[m] - ba[m]]
        except AnalysisError:
            continue
        for m in PREDICTION_METRICS:
            out[f"{table}/tstr_{kind}:{m}"] = (first[m], math.sqrt(sum(x * x for x in diffs[m]) / 4.0))
    return out


def prediction_models(table: str) -> "tuple[str, ...]":
    """The prediction models a table's frames are read by (F14), each named as an analysis: `ST9/tstr_glm` and so on."""
    return tuple(f"{table}/tstr_{kind}" for kind in ("glm", "hgb")) if table in PREDICTION else ()


def tstr_side(table: str, real: B.View, view: B.View, g_real: "list[int]",
              seed: int) -> "tuple[dict[str, float], dict[str, str]]":
    """A frame's models (fitted on its own half A, a TRTR model's size) tested on the real table's half B, and the risk
    correlation; and how each model ended on the frame ('ok' or why it stopped: its training, its predictions or their
    calibration), which `side` sets beside the panel's statuses (a prediction that stops on the twin is a stop)."""
    features, knots = PREDICTION[table]
    columns, y, rows = features(view)
    real_columns, real_y, real_rows = features(real)
    side_g = np.asarray(groups(view, table, seed), dtype=int)[rows]
    real_g = np.asarray(g_real, dtype=int)[real_rows]
    a = np.flatnonzero((side_g & 1) == 0)
    b_real = np.flatnonzero((real_g & 1) == 1)
    a_real = np.flatnonzero((real_g & 1) == 0)
    out: "dict[str, float]" = {}
    status: "dict[str, str]" = {}
    for kind in ("glm", "hgb"):
        name = f"{table}/tstr_{kind}"
        try:
            mine = _train(columns, y, a, kind, knots)
            p, target = _predict(mine, real_columns, real_y, b_real, knots)
            found = scores(p, target)
            reference, _t = _predict(_train(real_columns, real_y, a_real, kind, knots), real_columns, real_y, b_real,
                                     knots)
        except AnalysisError as error:
            status[name] = error.kind
            continue
        status[name] = "ok"
        for m in PREDICTION_METRICS:
            out[f"{name}:{m}"] = found[m]
        if float(np.std(p)) > 0 and float(np.std(reference)) > 0:
            out[f"{name}:risk_corr"] = float(np.corrcoef(p, reference)[0, 1])
    return out, status


def prediction_stops(table: str, tstr_yard: "dict[str, tuple[float, float]]", status: "dict[str, str]") -> "list[str]":
    """The prediction models robust on the real table (each with its TRTR yardstick: fitted and scored on all four
    splits of its halves) that stop on a frame, by the panel's rule (`analyst_battery.stops`): a model with no status
    on the frame stopped (Codex's review of the lane, its item 5: a prediction that failed on the twin vanished from
    the stops, and K-BC-14 read zero stopped analyses)."""
    return sorted(m for m in prediction_models(table) if f"{m}:auc" in tstr_yard and status.get(m, "missing") != "ok")


# -- ST10: counts over a time at risk (F16, F21) ----------------------------------------------


def _st10(v: B.View) -> "dict[str, np.ndarray]":
    held = _cache(v)
    if "st10" not in held:
        out = {"a": (_numbers(v, "age") - 60.0) / 10.0, "female": _flag(v, "gender", "female"),
               "diabetes": _numbers(v, "diabetes"), "days": _numbers(v, "days_at_risk"),
               "admissions": _numbers(v, "admissions"), "age": _numbers(v, "age")}
        for k in range(2, 9):
            out[f"ward{k}"] = _flag(v, "ward", f"W{k}")
        held["st10"] = out
    return held["st10"]  # type: ignore[return-value]


ST10_TERMS = ["age", "diabetes", "female"] + [f"ward{k}" for k in range(2, 9)]


def _st10_design(d: "dict[str, np.ndarray]") -> "tuple[dict[str, np.ndarray], np.ndarray, np.ndarray, np.ndarray]":
    keep = _complete(d["admissions"], d["days"], d["a"], d["diabetes"], d["female"], *(d[f"ward{k}"] for k in range(2, 9)))
    keep &= d["days"] > 0
    columns = {"intercept": np.ones(int(keep.sum())), "age": d["a"][keep], "diabetes": d["diabetes"][keep],
               "female": d["female"][keep]}
    columns.update({f"ward{k}": d[f"ward{k}"][keep] for k in range(2, 9)})
    return columns, d["admissions"][keep], np.log(d["days"][keep]), keep


def st10_poisson(v: B.View) -> "list[Estimate]":
    """F16: Poisson with the days at risk as the offset."""
    columns, y, offset, _keep = _st10_design(_st10(v))
    result = _fit(lambda: sm.GLM(y, pd.DataFrame(columns), family=sm.families.Poisson(), offset=offset).fit())
    _converged(result, "the Poisson model")
    return _coefs("ST10/pois", "F16", result, ST10_TERMS, columns, None)


def st10_naive(v: B.View) -> "list[Estimate]":
    """F16: the naive Poisson model without the offset (a twin must give back a wrong model's answer too)."""
    columns, y, _offset, _keep = _st10_design(_st10(v))
    result = _fit(lambda: sm.GLM(y, pd.DataFrame(columns), family=sm.families.Poisson()).fit())
    _converged(result, "the Poisson model without the offset")
    return _coefs("ST10/naive", "F16", result, ST10_TERMS, columns, None)


def st10_negbin(v: B.View) -> "list[Estimate]":
    """F16: the negative binomial model (NB2) with the offset, and its overdispersion alpha."""
    columns, y, offset, _keep = _st10_design(_st10(v))
    result = _fit(lambda: NegativeBinomial(y, pd.DataFrame(columns), offset=offset).fit(disp=0, maxiter=MAX_ITER))
    _converged(result, "the negative binomial model")
    out = _coefs("ST10/nb", "F16", result, ST10_TERMS, columns, None)
    out += [Estimate("ST10/nb:alpha", "F16", float(getattr(result, "params")["alpha"]),
                     float(getattr(result, "bse")["alpha"]), len(y))]
    return out


def st10_zinb(v: B.View) -> "list[Estimate]":
    """F16: the zero-inflated negative binomial model, its zeros by gender, with the offset."""
    columns, y, offset, _keep = _st10_design(_st10(v))
    inflate = pd.DataFrame({"intercept": np.ones(len(y)), "female": columns["female"]})
    model = ZeroInflatedNegativeBinomialP(y, pd.DataFrame(columns), exog_infl=inflate, offset=offset, p=2)
    result = _fit(lambda: model.fit(method="bfgs", maxiter=MAX_ITER, disp=0))
    _converged(result, "the zero-inflated model")
    params = getattr(result, "params")
    bse = getattr(result, "bse")
    out = []
    for name in ST10_TERMS + ["alpha"]:
        out += [Estimate(f"ST10/zinb:{name}", "F16", float(params[name]), float(bse[name]),
                         cell(columns[name]) if name in columns else len(y))]
    for name, key in (("inflate_intercept", "zero_intercept"), ("inflate_female", "zero_female")):
        out += [Estimate(f"ST10/zinb:{key}", "F16", float(params[name]), float(bse[name]),
                         cell(columns["female"]) if key == "zero_female" else len(y))]
    zero_fitted = float(np.mean(getattr(result, "predict")(which="prob-zero")))
    out += [Estimate("ST10/zinb:zero_share_fitted", "F16", zero_fitted, None, len(y))]
    return out


def st10_zeros(v: B.View) -> "list[Estimate]":
    """F16: the share of persons with no admission (a margin: the count column's own share)."""
    d = _st10(v)
    zero = [math.nan if x != x else float(x == 0.0) for x in d["admissions"]]
    return B.rate("ST10/zeros:share", "F16", zero, [True] * len(zero), ("margin",))


def plan_st10(real: B.View) -> "list[Analysis]":
    return [Analysis("ST10/pois", st10_poisson), Analysis("ST10/naive", st10_naive), Analysis("ST10/nb", st10_negbin),
            Analysis("ST10/zinb", st10_zinb), Analysis("ST10/zeros", st10_zeros),
            Analysis("ST10/t1", _table1("ST10/t1", _st10_table1, t1_pairs(real, _st10_table1, ["0", "1"])))]


def _st10_table1(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    d = _st10(v)
    groups = [None if x != x else str(int(x)) for x in d["diabetes"]]
    columns = {"age": d["age"].tolist(), "female": d["female"].tolist(), "days_at_risk": d["days"].tolist(),
               "admissions": d["admissions"].tolist()}
    columns.update({f"ward{k}": d[f"ward{k}"].tolist() for k in range(2, 9)})
    return groups, columns


# -- ST11: missing values at random (F17, F21) --------------------------------------------------


def _st11(v: B.View) -> "dict[str, np.ndarray]":
    held = _cache(v)
    if "st11" not in held:
        held["st11"] = {"a": (_numbers(v, "age") - 60.0) / 10.0, "female": _flag(v, "gender", "female"),
                        "outcome": _numbers(v, "outcome"), "lab_a": _numbers(v, "lab_a"),
                        "lab_b": _numbers(v, "lab_b"), "lab_c": _numbers(v, "lab_c"), "age": _numbers(v, "age")}
    return held["st11"]  # type: ignore[return-value]


def _missing_model(prefix: str, missing: np.ndarray, columns: "dict[str, np.ndarray]", keep: np.ndarray,
                   names: "list[str]") -> "list[Estimate]":
    data = {"intercept": np.ones(int(keep.sum()))}
    data.update({n: columns[n][keep] for n in names})
    y = missing[keep]
    result = _glm(y, data, sm.families.Binomial())
    return _coefs(prefix, "F17", result, names, data, y, {n: ("missing",) for n in names})


def st11_who_is_missing(v: B.View) -> "list[Estimate]":
    """F17: the three models of who is missing (lab_a by age and outcome; lab_b by gender and lab_a; lab_c by age once lab_b is seen)."""
    d = _st11(v)
    miss_a = np.where(np.isfinite(d["lab_a"]), 0.0, 1.0)
    miss_b = np.where(np.isfinite(d["lab_b"]), 0.0, 1.0)
    miss_c = np.where(np.isfinite(d["lab_c"]), 0.0, 1.0)
    out = _missing_model("ST11/miss_a", miss_a, {"age": d["a"], "outcome": d["outcome"]},
                         _complete(d["a"], d["outcome"]), ["age", "outcome"])
    out += _missing_model("ST11/miss_b", miss_b, {"female": d["female"], "lab_a": d["lab_a"]},
                          _complete(d["female"], d["lab_a"]), ["female", "lab_a"])
    seen_b = _complete(d["a"]) & np.isfinite(d["lab_b"])
    if not seen_b.any():
        raise AnalysisError("empty filter", "lab_b is never seen")
    out += _missing_model("ST11/miss_c", miss_c, {"age": d["a"]}, seen_b, ["age"])
    broken = [float((b != b) and (c == c)) for b, c in zip(d["lab_b"], d["lab_c"])]
    out += B.rule("ST11/rule:monotone_block", "F17", broken, ("missing",))
    return out


def st11_mice(v: B.View) -> "list[Estimate]":
    """F17: MICE (predictive mean matching, ten imputations after ten cycles) pooled by Rubin's rules, and each coefficient's
    fraction of missing information."""
    d = _st11(v)
    keep = _complete(d["outcome"], d["a"])
    data = pd.DataFrame({"outcome": d["outcome"][keep], "lab_a": d["lab_a"][keep], "lab_b": d["lab_b"][keep],
                         "lab_c": d["lab_c"][keep], "age": d["a"][keep]})
    if data[["lab_a", "lab_b", "lab_c"]].notna().all(axis=1).sum() < 22:
        raise AnalysisError("empty filter", "too few whole rows to impute from")
    imputed = _fit(lambda: mice.MICEData(data, rng=np.random.default_rng(MICE_SEED)))
    model = mice.MICE("outcome ~ lab_a + lab_c + age", sm.GLM, imputed, init_kwds={"family": sm.families.Binomial()})
    result = _fit(lambda: model.fit(n_burnin=MICE_BURN_IN, n_imputations=MICE_IMPUTATIONS), binomial=True)
    params = getattr(result, "params")
    bse = getattr(result, "bse")
    fmi = np.asarray(getattr(result, "frac_miss_info"), dtype=float)
    names = list(getattr(result, "model").exog_names) if hasattr(getattr(result, "model"), "exog_names") else \
        ["Intercept", "lab_a", "lab_c", "age"]
    out = []
    y = data["outcome"].to_numpy(dtype=float)
    events = int(y.sum())
    support = min(events, len(y) - events)
    for i, name in enumerate(names):
        if name == "Intercept":
            continue
        out += [Estimate(f"ST11/mice:{name}", "F17", float(np.asarray(params)[i]), float(np.asarray(bse)[i]), support,
                         ("missing",)),
                Estimate(f"ST11/mice_fmi:{name}", "F17", float(fmi[i]), None, support, ("missing", "fmi"))]
    return out


def st11_complete_case(v: B.View) -> "list[Estimate]":
    """F17: the complete-case model of the outcome."""
    d = _st11(v)
    keep = _complete(d["outcome"], d["lab_a"], d["lab_c"], d["a"])
    columns = {"intercept": np.ones(int(keep.sum())), "lab_a": d["lab_a"][keep], "lab_c": d["lab_c"][keep],
               "age": d["a"][keep]}
    result = _glm(d["outcome"][keep], columns, sm.families.Binomial())
    return _coefs("ST11/cc", "F17", result, ["lab_a", "lab_c", "age"], columns, d["outcome"][keep])


def plan_st11(real: B.View) -> "list[Analysis]":
    return [Analysis("ST11/missing", st11_who_is_missing), Analysis("ST11/mice", st11_mice),
            Analysis("ST11/cc", st11_complete_case), Analysis("ST11/t1", _table1("ST11/t1", _st11_table1, t1_pairs(real, _st11_table1, ["0", "1"])))]


def _st11_table1(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    d = _st11(v)
    groups = [None if x != x else str(int(x)) for x in d["outcome"]]
    columns = {"age": d["age"].tolist(), "female": d["female"].tolist(), "lab_a": d["lab_a"].tolist(),
               "lab_b": d["lab_b"].tolist(), "lab_c": d["lab_c"].tolist()}
    for name in ("lab_a", "lab_b", "lab_c"):
        columns[f"{name}_missing"] = np.where(np.isfinite(d[name]), 0.0, 1.0).tolist()
    return groups, columns


# -- ST12: rare levels, an ordinal and a nominal outcome (F18, F21) ---------------------------------


def level_rule(real: B.View) -> "tuple[list[str], str]":
    """E0b's rule for label levels, fixed on the real table: levels of at least 22 rows get a term, the rest one remainder.

    The commonest level is the reference. Returns the levels with a term
    and the remainder's name ('' where the remainder holds fewer than 22
    rows: it then joins the reference).
    """
    counts = pd.Series([x for x in _labels(real, "procedure_group") if x is not None]).value_counts()
    ordered = sorted(counts.items(), key=lambda kv: (-int(kv[1]), str(kv[0])))
    kept = [str(k) for k, n in ordered[1:] if int(n) >= B.SUPPORT]
    rest = int(sum(int(n) for k, n in ordered[1:] if int(n) < B.SUPPORT))
    return kept, ("remainder" if rest >= B.SUPPORT else "")


def _commonest(group: "list[str | None]") -> str:
    present = [g for g in group if g is not None]
    if not present:
        return ""
    counts = pd.Series(present).value_counts()
    return str(sorted(counts.items(), key=lambda kv: (-int(kv[1]), str(kv[0])))[0][0])


def _st12(v: B.View, kept: "list[str]", remainder: str) -> "dict[str, object]":
    held = _cache(v)
    if "st12" not in held:
        severity = np.asarray([math.nan if x not in U.SEVERITY_LEVELS else float(U.SEVERITY_LEVELS.index(x))
                               for x in _labels(v, "severity")], dtype=float)
        group = _labels(v, "procedure_group")
        known = set(kept)
        commonest = _commonest(group)
        levels = {f"lvl_{k}": np.asarray([math.nan if g is None else float(g == k) for g in group]) for k in kept}
        if remainder:
            levels["lvl_remainder"] = np.asarray([math.nan if g is None else float(g not in known and g != commonest)
                                                  for g in group])
        pooled = [None if g is None else g if g in known else ("remainder" if remainder and g != commonest else
                                                               "reference") for g in group]
        held["st12"] = {"a": (_numbers(v, "age") - 60.0) / 10.0, "female": _flag(v, "gender", "female"),
                        "severity": severity, "levels": levels, "pooled": pooled,
                        "discharge": _labels(v, "discharge"), "stay": _numbers(v, "stay_days"),
                        "group": group, "age": _numbers(v, "age")}
    return held["st12"]  # type: ignore[return-value]


def _st12_ordinal(kept: "list[str]", remainder: str) -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F18: the ordinal model of severity (a scipy logistic distribution) with level terms by E0b's rule of 22 rows."""
        d = _st12(v, kept, remainder)
        levels = d["levels"]  # type: ignore[index]
        keep = _complete(d["severity"], d["a"], d["female"], *levels.values())  # type: ignore[arg-type, union-attr]
        columns = {"age": d["a"][keep], "female": d["female"][keep]}  # type: ignore[index]
        columns.update({k: v_[keep] for k, v_ in levels.items()})  # type: ignore[union-attr]
        y = d["severity"][keep]  # type: ignore[index]
        if len(np.unique(y)) < len(U.SEVERITY_LEVELS):
            raise AnalysisError("level missing", "a severity level holds no row")
        empty = [k for k, x in columns.items() if k.startswith("lvl_") and float(x.sum()) == 0.0]
        if empty:
            raise AnalysisError("level missing", f"no row holds {empty[0][4:]}")
        model = OrderedModel(y, pd.DataFrame(columns), distr=scipy.stats.logistic)
        result = _fit(lambda: model.fit(method="bfgs", disp=False, maxiter=MAX_ITER))
        _converged(result, "the ordinal model")
        params = getattr(result, "params")
        bse = getattr(result, "bse")
        out = []
        for name in columns:
            out += [Estimate(f"ST12/ord:{name}", "F18", float(params[name]), float(bse[name]), cell(columns[name]))]
        cuts = np.asarray(model.transform_threshold_params(np.asarray(params, dtype=float)), dtype=float)[1:-1]
        first = list(params.index)[len(columns)]
        out += [Estimate("ST12/ord:cut1", "F18", float(cuts[0]), float(bse[first]), len(y))]
        for i in range(1, len(cuts)):
            out += [Estimate(f"ST12/ord:cut{i + 1}", "F18", float(cuts[i]), None, len(y))]
        return out
    return run


def _st12_multinomial(kept: "list[str]", remainder: str) -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F18: the multinomial model of discharge (home the reference) by age, gender and a severe stay, fitted by hand."""
        d = _st12(v, kept, remainder)
        severe = np.where(np.isfinite(d["severity"]), (d["severity"] >= 2.0).astype(float), np.nan)  # type: ignore
        discharge = d["discharge"]  # type: ignore[index]
        known = np.asarray([x in U.DISCHARGE_LEVELS for x in discharge])  # type: ignore[union-attr]
        keep = _complete(d["a"], d["female"], severe) & known  # type: ignore[arg-type]
        x = {"age": d["a"][keep], "female": d["female"][keep], "severe": severe[keep]}  # type: ignore[index]
        y = [str(t) for t, k in zip(discharge, keep) if k]  # type: ignore[call-overload]
        fit = multinomial(y, U.DISCHARGE_LEVELS, x)
        if not fit.converged:
            raise AnalysisError("no convergence", "the multinomial model")
        out = []
        for outcome in U.DISCHARGE_LEVELS[1:]:
            target = np.asarray([1.0 if t == outcome else 0.0 for t in y])
            for column in ("age", "female", "severe"):
                key = f"{outcome}_{column}"
                out += [Estimate(f"ST12/mnl:{key}", "F18", fit.params[key], fit.bse[key], cell(x[column], target))]
        return out
    return run


def _st12_tests(kept: "list[str]", remainder: str) -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F18: chi-square of the pooled procedure groups by discharge (Cramer's V) and Kruskal-Wallis of the stay by group."""
        d = _st12(v, kept, remainder)
        pooled = d["pooled"]  # type: ignore[index]
        out = B.cramer("ST12/chisq:cramers_v", "F18", pooled, d["discharge"])  # type: ignore[arg-type]
        stay = d["stay"]  # type: ignore[index]
        groups: "dict[str, list[float]]" = {}
        for g, s in zip(pooled, stay):  # type: ignore[call-overload]
            if g is not None and s == s:
                groups.setdefault(g, []).append(float(s))
        usable = [vals for vals in groups.values() if len(vals) >= 2]
        if len(usable) >= 2:
            statistic = float(_fit(lambda: scipy.stats.kruskal(*usable)).statistic)  # type: ignore[attr-defined]
            n = sum(len(x) for x in usable)
            out += [Estimate("ST12/kw:epsilon_sq", "F18", statistic / (n - 1), None, min(len(x) for x in usable))]
        return out
    return run


def st12_rare(v: B.View) -> "list[Estimate]":
    """F18: the share of rows in procedure groups of fewer than 22 rows, by the frame's own counts (a margin)."""
    group = [g for g in _labels(v, "procedure_group") if g is not None]
    counts = pd.Series(group).value_counts()
    rare = set(str(k) for k, n in counts.items() if int(n) < B.SUPPORT)
    flags = [float(g in rare) for g in group]
    return B.rate("ST12/rare:share", "F18", flags, [True] * len(flags), ("margin",))


def plan_st12(real: B.View) -> "list[Analysis]":
    kept, remainder = level_rule(real)
    return [Analysis("ST12/ord", _st12_ordinal(kept, remainder)), Analysis("ST12/mnl", _st12_multinomial(kept, remainder)),
            Analysis("ST12/tests", _st12_tests(kept, remainder)), Analysis("ST12/rare", st12_rare),
            Analysis("ST12/t1", _table1("ST12/t1", _st12_table1, t1_pairs(real, _st12_table1, list(U.DISCHARGE_LEVELS))))]


def _st12_table1(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    discharge = _labels(v, "discharge")
    age = _numbers(v, "age")
    columns = {"age": age.tolist(), "female": _flag(v, "gender", "female").tolist(),
               "stay_days": _numbers(v, "stay_days").tolist()}
    for level in U.SEVERITY_LEVELS:
        columns[f"severity_{level}"] = _flag(v, "severity", level).tolist()
    return discharge, columns


PLANS: "dict[str, Callable[[B.View], list[Analysis]]]" = {
    "ST7": plan_st7, "ST8": plan_st8, "ST9": plan_st9, "ST10": plan_st10, "ST11": plan_st11, "ST12": plan_st12}
# A frame of this many rows or more has its memory collected after each analysis: statsmodels' results and models
# hold each other, so their arrays wait for the cyclic collector, and over a frame's analyses they piled up (ST9 at
# 200,000 rows: 360 MB read, 1,756 MB after its eight analyses in one process, though none alone passed 925 MB; skeptic
# 1's item 3). Below it the arrays are small and a collection a fit would cost the suite's fast part its seconds.
COLLECT_ROWS = 50_000


def release_memory() -> None:
    """Collect, then hand the allocator's free pages back to the system (macOS's `malloc_zone_pressure_relief`, glibc's
    `malloc_trim`): the process's footprint falls to what it holds; no number changes."""
    gc.collect()
    try:
        lib = ctypes.CDLL(None)
    except (OSError, TypeError):
        return
    relief = getattr(lib, "malloc_zone_pressure_relief", None)
    if relief is not None:
        relief.restype = ctypes.c_size_t
        relief.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
        relief(None, 0)
        return
    trim = getattr(lib, "malloc_trim", None)
    if trim is not None:
        trim(0)


def _collected(run: "Callable[[B.View], list[Estimate]]") -> "Callable[[B.View], list[Estimate]]":
    def collected(v: B.View) -> "list[Estimate]":
        try:
            return run(v)
        finally:
            if v.rows >= COLLECT_ROWS:
                release_memory()
    return collected


# THE NIGHT'S MEMORY FALLBACK (skeptic 1's item 3, the brief's fallback): where a table's night child still passed the
# guard's bound with each frame let go and its memory handed back after every analysis, the analyses named here read a
# person-sampled half of each frame of `SAMPLED_ROWS` rows or more (the persons whose identifier hashes even, or the
# rows on a table of one row a person), and the run's notes and the stamp's detail say so: a fidelity cost of the
# MEASUREMENT (those estimates carry the noise of half the rows), never of the twin.
# MEASURED (repair 1, the night at 200,000 rows under the machine's guard, the driver its command): ST7's, ST8's, ST10's,
# ST11's and ST12's children peaked at 1,318, 807, 1,093, 1,105 and 825 MB; ST9's passed the guard's bound three times,
# each in its first minutes: at 2,063 MB with each analysis collected, at 1,856 MB with the free pages handed back as
# well, and at 1,951 MB with its curve family (F15, which grew its footprint most: by 308, 30, 148 and 354 MB of the
# 1,100 its eight analyses added on the real table) on a person-sampled half. So at the night EVERY FRAME of ST9 is read
# on a person-sampled half (`HALVED_FRAMES_AT_NIGHT`; the twin is still made from the whole table), and an analysis
# named in `SAMPLED_AT_NIGHT` would read one alone.
SAMPLED_ROWS = 150_000
SAMPLED_AT_NIGHT: "dict[str, tuple[str, ...]]" = {}
HALVED_FRAMES_AT_NIGHT: "tuple[str, ...]" = ("ST9",)


def person_half(v: B.View, table: str) -> "list[int]":
    """The rows of a person-sampled half: a person's rows all in or all out (CRC-32 of the identifier, even), or the rows
    whose SplitMix64 of their position is even on a table of one row a person."""
    person = U.PERSON.get(table)
    if person and v.has(person):
        return [i for i, s in enumerate(v.text(person)) if s is not None and zlib.crc32(s.encode("utf-8")) % 2 == 0]
    return [i for i in range(v.rows) if B.splitmix64(i) % 2 == 0]


def _sampled(run: "Callable[[B.View], list[Estimate]]", table: str) -> "Callable[[B.View], list[Estimate]]":
    def sampled(v: B.View) -> "list[Estimate]":
        if v.rows < SAMPLED_ROWS:
            return run(v)
        return run(v.subset(person_half(v, table), f"{v.name} sampled half"))
    return sampled


def plan_for(table: str, real: B.View) -> "list[Analysis]":
    """The table's analyses (`PLANS`), each frame of `COLLECT_ROWS` rows or more collected after each one (and the night's
    memory fallback where `SAMPLED_AT_NIGHT` names an analysis)."""
    halved = SAMPLED_AT_NIGHT.get(table, ()) if real.rows >= SAMPLED_ROWS else ()
    plan = [Analysis(a.name, _collected(_sampled(a.run, table) if a.name in halved else a.run))
            for a in PLANS[table](real)]
    if real.rows >= COLLECT_ROWS:
        release_memory()
    return plan
TABLE1 = {"ST8": _st8_table1, "ST9": _st9_table1, "ST10": _st10_table1, "ST11": _st11_table1, "ST12": _st12_table1}


# -- F20 regularised regression, F22 clustering (ST9); F24 a Bayesian check (ST7) ----------------------------------


ST9_PENALIZED = ["age", "female", "body_mass", "smoker", "sbp", "diabetes", "lactate", "creatinine", "lab1", "lab2",
                 "lab3", "treatment"]
PENALTIES = (0.003, 0.01, 0.03, 0.1, 0.3)
NET_PENALTY = 0.03


def _scaled(d: "dict[str, np.ndarray]", scales: "dict[str, tuple[float, float]]") -> "tuple[np.ndarray, np.ndarray]":
    keep = _complete(d["died"], *(d[n] for n in ST9_PENALIZED))
    x = np.column_stack([(d[n][keep] - scales[n][0]) / scales[n][1] for n in ST9_PENALIZED])
    y = d["died"][keep]
    if y.min() == y.max():
        raise AnalysisError("empty filter", "one outcome only")
    return x, y


def _l1(x: np.ndarray, y: np.ndarray, c: float, ratio: float) -> object:
    model = LogisticRegression(C=c, l1_ratio=ratio, solver="saga", max_iter=5000, tol=1e-5, random_state=0)
    fitted = _fit(lambda: model.fit(x, y))
    _converged(fitted, "the penalized model")
    return fitted


def lasso_path(x: np.ndarray, y: np.ndarray) -> "tuple[float, object]":
    """The lasso's penalty by 3-fold cross-validation (folds by row position, log loss) over `PENALTIES`, by the one-SE rule
    (the strongest penalty whose mean loss is within one standard error of the best), refitted on every row."""
    folds = np.arange(len(y)) % 3
    losses = {}
    for c in PENALTIES:
        per = []
        for f in range(3):
            train, test = folds != f, folds == f
            if y[train].min() == y[train].max():
                raise AnalysisError("empty filter", "a fold holds one outcome only")
            p = np.clip(getattr(_l1(x[train], y[train], c, 1.0), "predict_proba")(x[test])[:, 1], 1e-9, 1 - 1e-9)
            per += [-float(np.mean(y[test] * np.log(p) + (1 - y[test]) * np.log(1 - p)))]
        losses[c] = (float(np.mean(per)), float(np.std(per, ddof=1)) / math.sqrt(3.0))
    best = min(PENALTIES, key=lambda c: losses[c][0])
    chosen = min(c for c in PENALTIES if losses[c][0] <= losses[best][0] + losses[best][1])
    return chosen, _l1(x, y, chosen, 1.0)


def _lasso(v: B.View, scales: "dict[str, tuple[float, float]]") -> "tuple[np.ndarray, np.ndarray, object]":
    """The frame's standardized rows, outcome and lasso (`lasso_path`), fitted once a frame and kept on its view: F20's
    estimates and the selection's agreement read the same fit (the scales are the real table's, one set a run)."""
    held = _cache(v)
    if "lasso" not in held:
        x, y = _scaled(_st9(v), scales)
        held["lasso"] = (x, y, lasso_path(x, y)[1])
    return held["lasso"]  # type: ignore[return-value]


def _st9_penalized(scales: "dict[str, tuple[float, float]]", kept: "set[str]") -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F20: the lasso (3-fold cross-validation over five penalties) and an elastic net at one penalty (saga, the columns
        standardized by the real table's means and SDs); the standardized coefficient of each column the real table's lasso
        keeps (a column it sets to 0 carries no structure, and a column-wise shuffle sets it to 0 too), no standard error."""
        x, y, lasso = _lasso(v, scales)
        net = _l1(x, y, NET_PENALTY, 0.5)
        events = int(y.sum())
        support = min(events, len(y) - events)
        out = []
        for i, name in enumerate(ST9_PENALIZED):
            if name in kept:
                out += [Estimate(f"ST9/lasso:{name}", "F20", float(getattr(lasso, "coef_")[0][i]), None, support),
                        Estimate(f"ST9/enet:{name}", "F20", float(getattr(net, "coef_")[0][i]), None, support)]
        return out
    return run


def selection(view: B.View, scales: "dict[str, tuple[float, float]]") -> "set[str]":
    """The columns the lasso keeps on a frame."""
    _x, _y, lasso = _lasso(view, scales)
    return {name for i, name in enumerate(ST9_PENALIZED) if abs(float(getattr(lasso, "coef_")[0][i])) > 1e-8}


def _labs(v: B.View) -> np.ndarray:
    d = _st9(v)
    keep = _complete(d["lab1"], d["lab2"], d["lab3"])
    return np.column_stack([d["lab1"][keep], d["lab2"][keep], d["lab3"][keep]])


def mixture(x: np.ndarray) -> object:
    """A Gaussian mixture of one to five classes on the three laboratory values, the count chosen by BIC (each fit must
    settle: scikit-learn's `converged_`)."""
    fits = []
    for k in range(1, 6):
        fitted = _fit(lambda k=k: GaussianMixture(n_components=k, covariance_type="full", random_state=0).fit(x))
        _converged(fitted, f"the mixture of {k} classes")
        fits += [fitted]
    return min(fits, key=lambda f: float(getattr(f, "bic")(x)))


def _mixture(v: B.View) -> "tuple[np.ndarray, object]":
    """A frame's laboratory rows and its mixture (`mixture`), fitted once a frame and kept on its view: F22's estimates and
    the agreement against the real table read the same fit (the real table's is fitted once a run, not once a side)."""
    held = _cache(v)
    if "mixture" not in held:
        x = _labs(v)
        held["mixture"] = (x, mixture(x))
    return held["mixture"]  # type: ignore[return-value]


def st9_mixture(v: B.View) -> "list[Estimate]":
    """F22: the chosen class count, and each class's share and lab1 mean in the order of the lab1 means."""
    x, model = _mixture(v)
    weights = np.asarray(getattr(model, "weights_"), dtype=float)
    means = np.asarray(getattr(model, "means_"), dtype=float)
    n = len(x)
    out = [Estimate("ST9/gmm:classes", "F22", float(len(weights)), None, n)]
    for rank, j in enumerate(np.argsort(means[:, 0], kind="stable")):
        out += [Estimate(f"ST9/gmm:share_{rank + 1}", "F22", float(weights[j]), None, int(n * min(weights[j], 1 - weights[j]))),
                Estimate(f"ST9/gmm:lab1_{rank + 1}", "F22", float(means[j, 0]), None, int(n * weights[j]))]
    return out


def mixture_agreement(real: B.View, view: B.View) -> "tuple[float, float]":
    """Whether the mixture fitted on the frame chooses the class count the real table's chooses, and the adjusted Rand index
    of the real table's rows labelled by each."""
    x, mine = _mixture(real)
    _xv, theirs = _mixture(view)
    same = float(len(getattr(mine, "weights_")) == len(getattr(theirs, "weights_")))
    return same, float(adjusted_rand_score(getattr(mine, "predict")(x), getattr(theirs, "predict")(x)))


BAYES_PERSONS = 300
# The variational check's estimates carry NO standard error: a posterior SD is no sampling SE (skeptic 1's item 5:
# over 24 independent ST7 draws at 20,000 rows the arm's estimate spread 0.139 against a mean posterior SD of 0.059),
# so they enter no decision count, SE ratio or strong flip; their truths are held by the spread across independent
# draws (`utility_tables.ACROSS_DRAW_SD`).
APPROXIMATE = "approximate"


def bayes_chosen(subject: str, share: float) -> bool:
    """Whether the variational check reads a person: the CRC-32 of the identifier, modulo 1,000,000, under share x 10^6
    (the same rule on every frame, so a half reads about half as many persons as the whole table)."""
    return zlib.crc32(subject.encode("utf-8")) % 1_000_000 < share * 1_000_000


def _st7_bayes(share: float) -> "Callable[[B.View], list[Estimate]]":
    def run(v: B.View) -> "list[Estimate]":
        """F24 (APPROXIMATE): the binomial mixed model of the repeated yes-or-no outcome by variational Bayes, on the
        persons `bayes_chosen` reads at the share fixed on the real table (about `BAYES_PERSONS` there); posterior means,
        no standard error."""
        d = _st7(v)
        keep = _complete(d["controlled"], d["years"], d["arm"]) & (d["subject"] != "")
        subject = d["subject"].astype(str)
        rows = keep & np.asarray([bayes_chosen(s, share) for s in subject])
        frame = pd.DataFrame({"controlled": d["controlled"][rows], "years": d["years"][rows], "arm": d["arm"][rows],
                              "subject": subject[rows]})
        if frame["controlled"].nunique() < 2 or frame["subject"].nunique() < 2:
            raise AnalysisError("empty filter", "one outcome or one person only")
        model = BinomialBayesMixedGLM.from_formula("controlled ~ years + arm", {"subject": "0 + C(subject)"}, frame)
        fit = _fit(lambda: model.fit_vb(rng=np.random.default_rng(VB_SEED)))
        means = dict(zip(model.exog_names, np.asarray(getattr(fit, "fe_mean"), dtype=float)))
        n = len(frame)
        events = int(frame["controlled"].sum())
        out = [Estimate(f"ST7/vb:{name}", "F24", float(means[name]), None, min(events, n - events), (APPROXIMATE,))
               for name in ("years", "arm")]
        out += [Estimate("ST7/vb:sd_person", "F24", float(np.exp(np.asarray(getattr(fit, "vcp_mean"))[0])), None,
                         int(frame["subject"].nunique()), (APPROXIMATE,))]
        return out
    return run


# -- halves, sides and one table run --------------------------------------------------------------


def groups(view: B.View, table: str, seed: int) -> "list[int]":
    """Each row's group of sixteen (E0b's SplitMix64 rule): on ST7 and ST8 every row of a person shares the person's group."""
    person = U.PERSON.get(table)
    if person and view.has(person):
        return [B.splitmix64(seed * 1_000_003 + (zlib.crc32(s.encode("utf-8")) if s is not None else 0)) % 16
                for s in view.text(person)]
    return [B.splitmix64(seed * 1_000_003 + i) % 16 for i in range(view.rows)]


@dataclasses.dataclass
class Side:
    """One frame set against the real table: its comparisons, the analyses that stop on it, its panel, its extra measures."""

    compared: "list[B.Compared]"
    stops: "list[str]"
    panel: B.Panel
    extra: "dict[str, float]"


@dataclasses.dataclass
class Run:
    """Everything one table at one seed gave: the yardstick, each side's runs, the routes, the cost.

    ``real_extra`` holds the real table's own extra measures a bar reads
    against a side's (ST9's balance before and after its own weighting).
    """

    table: str
    rows: int
    seed: int
    route: str
    yard: B.Yardstick
    tstr_yard: "dict[str, tuple[float, float]]"
    sides: "dict[str, list[Side]]"
    seconds: float
    product_seconds: float
    notes: "list[str]" = dataclasses.field(default_factory=list)
    real_extra: "dict[str, float]" = dataclasses.field(default_factory=dict)


def _extra(table: str, real: B.View, view: B.View, g: "list[int]", seed: int,
           tstr_yard: "dict[str, tuple[float, float]]",
           levels: "list[str]") -> "tuple[dict[str, float], list[B.Compared], dict[str, str]]":
    """A frame's extra measures against the real table, its F14 comparisons (inside where within the TRTR yardstick),
    and how each prediction model ended on the frame (`tstr_side`; a frame whose columns a model cannot read stops both)."""
    extra: "dict[str, float]" = {}
    compared: "list[B.Compared]" = []
    predicted: "dict[str, str]" = {}
    if table in PREDICTION:
        try:
            found, predicted = tstr_side(table, real, view, g, seed)
        except AnalysisError as error:
            found, predicted = {}, {name: error.kind for name in prediction_models(table)}
        extra.update(found)
        for key, (real_value, h) in sorted(tstr_yard.items()):
            value = found.get(key)
            inside = value is not None and abs(value - real_value) <= h
            compared += [B.Compared(key, "F14", (), real_value, value, h, inside, None, None,
                                    value is not None and (value > 0) == (real_value > 0))]
    if table == "ST9":
        try:
            before, after = st9_balance(view)
            extra["smd_before"], extra["smd_after"] = before, after
        except AnalysisError:
            pass
        try:
            held = _cache(real)
            if "selection" not in held:
                held["selection"] = selection(real, _scales(real))
            mine, theirs = held["selection"], selection(view, _scales(real))
            union = mine | theirs  # type: ignore[operator]
            extra["lasso_jaccard"] = len(mine & theirs) / len(union) if union else 1.0  # type: ignore[operator, arg-type]
        except AnalysisError:
            pass
        try:
            extra["gmm_same_classes"], extra["gmm_ari"] = mixture_agreement(real, view)
        except AnalysisError:
            pass
    if table in TABLE1:
        try:
            extra["t1_smd_max"] = table1_smd(real, view, TABLE1[table], levels)
        except (AnalysisError, ValueError):
            pass
    if table == "ST7":
        for name, measure in (("ks_rows", _ks_rows), ("ks_gaps", _ks_gaps)):
            try:
                extra[name] = measure(real, view)
            except AnalysisError:
                pass
    return extra, compared, predicted


def _ks(a: np.ndarray, b: np.ndarray) -> float:
    if len(a) == 0 or len(b) == 0:
        raise AnalysisError("empty filter", "nothing to compare")
    return float(scipy.stats.ks_2samp(a, b).statistic)


def _rows_per_person(v: B.View) -> np.ndarray:
    d = _st7(v)
    s = d["subject"][d["subject"] != ""].astype(str)
    return np.asarray(pd.Series(s).value_counts().to_numpy(), dtype=float)


def _gaps(v: B.View) -> np.ndarray:
    d = _st7(v)
    keep = np.isfinite(d["days"]) & (d["subject"] != "")
    frame = pd.DataFrame({"s": d["subject"][keep].astype(str), "t": d["days"][keep]}).sort_values(["s", "t"])
    same = frame["s"].to_numpy()[1:] == frame["s"].to_numpy()[:-1]
    return np.diff(frame["t"].to_numpy())[same]


def _ks_rows(real: B.View, view: B.View) -> float:
    return _ks(_rows_per_person(real), _rows_per_person(view))


def _ks_gaps(real: B.View, view: B.View) -> float:
    return _ks(_gaps(real), _gaps(view))


def _table_levels(table: str, real: B.View) -> "list[str]":
    if table not in TABLE1:
        return []
    group, _columns = TABLE1[table](real)
    return sorted({g for g in group if g is not None})


def side(y: B.Yardstick, plan: "list[Analysis]", table: str, real: B.View, view: B.View, g: "list[int]", seed: int,
         tstr_yard: "dict[str, tuple[float, float]]", levels: "list[str]") -> Side:
    """One frame against the real table: E0b's comparisons and stops, then the F14 comparisons and the extra measures.

    Each prediction model's status on the frame stands beside the panel's
    (`Panel.status`), and a model robust on the real table that stops on
    the frame is one of its stops (`prediction_stops`), read by the same
    real-and-replicate rule as the panel's analyses (`stopping`)."""
    panel = B.run_panel(plan, view)
    extra, more, predicted = _extra(table, real, view, g, seed, tstr_yard, levels)
    panel.status.update(predicted)
    if view.rows >= COLLECT_ROWS:
        release_memory()
    return Side(B.compare(y, panel) + more, B.stops(y, panel) + prediction_stops(table, tstr_yard, predicted), panel,
                extra)


def not_made(y: B.Yardstick, tstr_yard: "dict[str, tuple[float, float]]") -> Side:
    """A twin the product could not make: every supported estimate outside and every robust analysis stopped on it (its
    prediction models robust on the real table among them)."""
    empty = B.Panel({}, {})
    f14 = [B.Compared(key, "F14", (), real_value, None, h, False, None, None, False)
           for key, (real_value, h) in sorted(tstr_yard.items())]
    models = sorted({key.split(":")[0] for key in tstr_yard if key.endswith(":auc")})
    return Side(B.compare(y, empty) + f14, B.stops(y, empty) + models, empty, {"not_made": 1.0})


def _trouble(route: str, step: str, error: BaseException) -> str:
    return f"route {route}: the product could not {step} the twin: {type(error).__name__}: {str(error)[:240]}"


def replicate_seed(seed: int, k: int) -> int:
    """The fresh replicate's seed at twin seed k (E0b's rule)."""
    return seed * 1000 + 100 + k


# A labelled route read at every twin seed (route U: its difference from route S on one head is the switch's effect,
# read over the same seeds); the others at the first twin seed only.
EVERY_TWIN_SEED = ("U",)


def run_table(table: str, rows: int, seed: int, twins: "tuple[int, ...]", folder: pathlib.Path, route: str = "S",
              extra_routes: "tuple[str, ...]" = (), flattened: bool = True, controls: bool = True) -> Run:
    """One table at one seed: the yardstick, the twin by ``route`` at each twin seed, the three controls.

    ``extra_routes`` adds sides named `twin_<route>` (route P on ST7 and
    ST8, route C, route U), labelled and never read by the KPIs, at the
    first twin seed only (route U at every twin seed); a route the tree
    lacks is noted, not raised. ``flattened`` False leaves the flattened
    replicate out (the gate file's fast part, whose own case reads that
    control at 20,000 rows); ``controls`` False leaves out the replicate,
    the shuffled twin and the flattened replicate (a night's route P
    child, whose controls the headline's run reads already).

    A route whose description reads the installation's key
    (`twin_routes.keyed`) is described once a twin seed, under that twin
    seed's own key (`twin_routes.key_for`), so a run reads three keys and
    their spread; a route that reads no key is described once. The
    answers each route gave and the entries it left blank are noted. Each
    side's frame is let go before the next side is read.
    """
    started = time.perf_counter()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{table}-{seed}.csv"
    U.write(path, table, rows, seed)
    text = path.read_text(encoding="utf-8")
    halve = rows >= SAMPLED_ROWS and table in HALVED_FRAMES_AT_NIGHT

    def frame(source: "str | pathlib.Path", name: str) -> B.View:
        """A frame as the analyses read it: the whole table, or its person-sampled half (the night's memory fallback)."""
        view = B.read(source, name)
        return view.subset(person_half(view, table), f"{name} sampled half") if halve else view

    real = frame(path, f"{table} real")
    plan = plan_for(table, real)
    g = groups(real, table, seed)
    y = B.yardstick(plan, real, g)
    tstr_yard = tstr_yardstick(table, real, g) if table in PREDICTION else {}
    levels = _table_levels(table, real)
    person = U.PERSON.get(table, "")
    knows = U.KNOWS.get(table)
    sides: "dict[str, list[Side]]" = {"twin": []}
    if controls:
        sides.update({"replicate": [], "shuffled": []})
    flat_side = controls and flattened and table in U.FLATTENED
    if flat_side:
        sides["flattened"] = []
    notes: "list[str]" = []
    real_extra: "dict[str, float]" = {}
    if table == "ST9":
        try:
            real_extra["smd_before"], real_extra["smd_after"] = st9_balance(real)
        except AnalysisError:
            pass
    product = 0.0
    if rows >= SAMPLED_ROWS and SAMPLED_AT_NIGHT.get(table):
        notes.append(f"{table}: {', '.join(SAMPLED_AT_NIGHT[table])} read a person-sampled half of each frame of "
                     f"{SAMPLED_ROWS:,} rows or more (the night's memory fallback: a cost of the measurement)")
    if halve:
        notes.append(f"{table}: every frame read on a person-sampled half of its {rows:,} rows, the twin made from the "
                     "whole table (the night's memory fallback: a cost of the measurement)")
    names = [route] + [n for n in extra_routes if n != route and not (n == "P" and not person)]
    for name in names[1:]:
        sides[f"twin_{name}"] = []
    described: "dict[tuple[str, int], twin_routes.Described]" = {}
    missing: "set[str]" = set()

    def description(name: str, k: int) -> "twin_routes.Described | None":
        """The route's description for twin seed k (one a key where the route reads it), made on first need."""
        nonlocal product
        keyed = twin_routes.keyed(name)
        at = (name, k if keyed else twins[0])
        if at in described or name in missing:
            return described.get(at)
        clock = time.perf_counter()
        place = folder / (f"route-{name}-k{k}" if keyed else f"route-{name}")
        key = twin_routes.key_for(seed, k) if keyed else twin_routes.TEST_KEY
        try:
            made = twin_routes.describe(name, place, f"{table}-{seed}", text, person, knows=knows, key=key)
            described[at] = made
            notes.append(f"{table} route {name}{f' key {k}' if keyed else ''}: {made.answered}")
            held = twin_routes.held_columns(made)
            if held:
                f4 = (" (lane MU's finding F4: an age held on a table of several rows a person, every model with age "
                      "reads a held column; owner lane HB3-a2)" if person and any(h.startswith("age ") for h in held)
                      else "")
                notes.append(f"{table} route {name}: held as record numbers: {'; '.join(held)}{f4}")
            return made
        except twin_routes.RouteMissing as gone:
            missing.add(name)
            notes.append(str(gone))
        except Exception as error:  # the product's own failure, recorded
            notes.append(_trouble(name, "describe", error))
        finally:
            product += time.perf_counter() - clock
        return None

    # A product that cannot describe or generate a table's twin is the finding itself: the twin's side then reads as
    # one on which nothing runs (`not_made`), and the note names the error.
    for k in twins:
        for name in names:
            if name != route and k != twins[0] and name not in EVERY_TWIN_SEED:
                continue
            label = "twin" if name == route else f"twin_{name}"
            made = description(name, k)
            if made is None and name in missing and name != route:
                sides.pop(label, None)
                continue
            clock = time.perf_counter()
            try:
                if made is None:
                    raise twin_routes.RouteTrouble("no description")
                twin_text, _report = twin_routes.generate(made, k)
            except Exception as error:  # the product's own failure, recorded
                if made is not None:
                    notes.append(_trouble(name, f"generate (twin seed {k})", error))
                sides[label] += [not_made(y, tstr_yard)]
                continue
            finally:
                product += time.perf_counter() - clock
            sides[label] += [side(y, plan, table, real, frame(twin_text, label), g, k, tstr_yard, levels)]
            del twin_text
            gc.collect()
        if not controls:
            continue
        r_seed = replicate_seed(seed, k)
        sides["replicate"] += [side(y, plan, table, real, frame(U.text(table, rows, r_seed), "replicate"), g, k,
                                    tstr_yard, levels)]
        gc.collect()
        sides["shuffled"] += [side(y, plan, table, real, frame(B.shuffled_text(text, seed * 31 + k), "shuffled"), g,
                                   k, tstr_yard, levels)]
        gc.collect()
        if flat_side:
            sides["flattened"] += [side(y, plan, table, real, frame(U.text(table, rows, r_seed, flat=True),
                                                                        "flattened"), g, k, tstr_yard, levels)]
            gc.collect()
    return Run(table, real.rows, seed, route, y, tstr_yard, sides, time.perf_counter() - started, product, notes,
               real_extra)


def run_to_dict(run: Run) -> "dict[str, object]":
    """A table run as plain data (a night's child hands it back as JSON; a kept run is read back from it)."""
    out = dataclasses.asdict(run)
    out["yard"]["robust"] = sorted(run.yard.robust)  # type: ignore[index]
    return out


def _panel_from(data: "dict") -> B.Panel:
    return B.Panel({k: Estimate(e["key"], e["family"], e["value"], e["se"], e["support"], tuple(e["tags"]))
                    for k, e in data["estimates"].items()}, dict(data["status"]))


def run_from_dict(data: "dict") -> Run:
    """The table run `run_to_dict` wrote."""
    yard = B.Yardstick(_panel_from(data["yard"]["real"]), dict(data["yard"]["h"]), set(data["yard"]["robust"]))
    sides = {name: [Side([B.Compared(c["key"], c["family"], tuple(c["tags"]), c["real"], c["value"], c["h"],
                                     c["inside"], c["sig_real"], c["sig_twin"], c["same_sign"]) for c in s["compared"]],
                         list(s["stops"]), _panel_from(s["panel"]), dict(s["extra"])) for s in items]
             for name, items in data["sides"].items()}
    return Run(data["table"], data["rows"], data["seed"], data["route"], yard,
               {k: (v[0], v[1]) for k, v in data["tstr_yard"].items()}, sides, data["seconds"],
               data["product_seconds"], list(data.get("notes", [])), dict(data.get("real_extra", {})))


# -- the measures and K-BC-14 ------------------------------------------------------------------


def finite(value: object) -> object:
    """A value the ledger can hold: every non-finite float (NaN, infinity) becomes None, at any depth, in dictionaries,
    lists and tuples alike (skeptic 1's item 7: a variance ratio of a twin whose SD is 0 read infinity, and JSON would
    write it as Infinity)."""
    if isinstance(value, float) and not math.isfinite(value):
        return None
    if isinstance(value, dict):
        return {k: finite(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite(v) for v in value]
    return value


def _median(values: "list[float]") -> float:
    clean = [x for x in values if x == x]
    return statistics.median(clean) if clean else math.nan


def _joint(c: B.Compared) -> bool:
    """A scored estimate of how columns go together (a margin, one column's own count, is left out, as E0b leaves it)."""
    return "margin" not in c.tags


def family_shares(runs: "list[Run]", side_name: str) -> "dict[str, list[float]]":
    """Per family, the share of supported joint estimates inside, one per twin seed, pooled over the table runs."""
    count = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    out: "dict[str, list[float]]" = {}
    for family in FAMILIES:
        per = []
        for k in range(count):
            rows = [c for r in runs if k < len(r.sides.get(side_name, [])) for c in r.sides[side_name][k].compared
                    if c.family == family and _joint(c)]
            if rows:
                per += [sum(1 for c in rows if c.inside) / len(rows)]
        if per:
            out[family] = per
    return out


def pooled_shares(runs: "list[Run]", side_name: str) -> "list[float]":
    count = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    out = []
    for k in range(count):
        rows = [c for r in runs if k < len(r.sides.get(side_name, [])) for c in r.sides[side_name][k].compared
                if _joint(c)]
        if rows:
            out += [sum(1 for c in rows if c.inside) / len(rows)]
    return out


def family_sizes(runs: "list[Run]") -> "dict[str, int]":
    sizes: "dict[str, int]" = {}
    for r in runs:
        for c in (r.sides["replicate"][0].compared if r.sides["replicate"] else []):
            if _joint(c):
                sizes[c.family] = sizes.get(c.family, 0) + 1
    return sizes


def controls(runs: "list[Run]") -> "dict[str, object]":
    """K-BC-01's controls on this battery: the replicate a fresh sample's share, the shuffle 10 points under it pooled and 25 in
    every family of at least five supported estimates (the others named void)."""
    fam = {s: family_shares(runs, s) for s in ("twin", "replicate", "shuffled")}
    pooled = {s: pooled_shares(runs, s) for s in fam}
    sizes = family_sizes(runs)
    supported = sum(sizes.values())
    rep = _median(pooled["replicate"])
    shuffle_gap = 100.0 * (rep - _median(pooled["shuffled"]))
    judged = [f for f in sorted(fam["replicate"]) if sizes.get(f, 0) >= B.FAMILY_MINIMUM]
    void = [f for f in judged
            if not 100.0 * (_median(fam["replicate"][f]) - _median(fam["shuffled"].get(f, [math.nan]))) > B.FAMILY_TARGET]
    gap = 100.0 * (rep - _median(pooled["twin"]))
    worst = max((100.0 * (_median(fam["replicate"][f]) - _median(fam["twin"].get(f, [0.0]))) for f in judged),
                default=math.nan)
    return {"fam": fam, "pooled": pooled, "sizes": sizes, "supported": supported, "gap": gap, "worst": worst,
            "void": void, "hold": bool(B.replicate_holds(rep, supported) and shuffle_gap > 10.0 and not void),
            "shuffle_gap": shuffle_gap}


def _per_seed(runs: "list[Run]", side_name: str, count: "Callable[[Side, Run], float]") -> float:
    k_max = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    totals = [sum(count(r.sides[side_name][k], r) for r in runs if k < len(r.sides.get(side_name, [])))
              for k in range(k_max)]
    return _median(totals) if totals else math.nan


def strong_flips(s: Side, r: Run) -> float:
    """Strong effects reversed on a frame: real |z| above 3.29 and the frame's sign opposite (an approximate estimate,
    which carries no standard error, never counts)."""
    n = 0
    for c in s.compared:
        est = r.yard.real.estimates.get(c.key)
        if est is None or not est.se or c.value is None or APPROXIMATE in est.tags:
            continue
        if abs(est.value / est.se) > STRONG_Z and (c.value > 0) != (est.value > 0):
            n += 1
    return float(n)


def robust_names(r: Run) -> "set[str]":
    """The analyses robust on the run's real table: the panel's (`Yardstick.robust`) and the prediction models with a
    TRTR yardstick."""
    return set(r.yard.robust) | {m for m in prediction_models(r.table) if f"{m}:auc" in r.tstr_yard}


def _fragile(r: Run) -> "set[str]":
    """The robust analyses that stop on a replicate draw of the run: a stop on the twin of one of them is not counted."""
    return {n for n in robust_names(r)
            if any(s.panel.status.get(n, "missing") != "ok" for s in r.sides.get("replicate", []))}


def stopping(s: Side, r: Run) -> float:
    """K-BC-10's form: robust analyses that stop on the frame, none that stops on a replicate draw of the same run."""
    weak = _fragile(r)
    return float(len([n for n in s.stops if n not in weak]))


def decisions(runs: "list[Run]", side_name: str) -> "tuple[float, float]":
    """K-BC-03's form: the share of real significant results kept (same sign) and of real null results made significant
    (an approximate estimate never counts)."""
    kept, invented = [], []
    k_max = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    for k in range(k_max):
        rows = [c for r in runs if k < len(r.sides.get(side_name, [])) for c in r.sides[side_name][k].compared
                if c.sig_real is not None and _joint(c) and APPROXIMATE not in c.tags]
        sig = [c for c in rows if c.sig_real]
        null = [c for c in rows if not c.sig_real]
        if sig:
            kept += [sum(1 for c in sig if c.sig_twin and c.same_sign) / len(sig)]
        if null:
            invented += [sum(1 for c in null if c.sig_twin) / len(null)]
    return _median(kept), _median(invented)


def se_ratio_share(runs: "list[Run]", side_name: str) -> float:
    """The share of coefficients whose standard error on the frame is 0.8 to 1.25 times the real one, on the tables where
    one person stands on several rows (ST7, ST8): there a twin that loses the persons' clustering misstates its SEs; on a
    table of one row a person a column-wise shuffle meets the bar (the statistics check's item 4)."""
    shares = []
    k_max = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    for k in range(k_max):
        ok = n = 0
        for r in runs:
            if r.table not in U.PERSON or k >= len(r.sides.get(side_name, [])):
                continue
            panel = r.sides[side_name][k].panel
            for key in r.yard.h:
                est = r.yard.real.estimates[key]
                got = panel.estimates.get(key)
                if not est.se or "curve" in est.tags or "margin" in est.tags or APPROXIMATE in est.tags:
                    continue
                n += 1
                if got is not None and got.se and 0.8 <= got.se / est.se <= 1.25:
                    ok += 1
        if n:
            shares += [ok / n]
    return _median(shares)


def _value(s: Side, key: str) -> float:
    got = s.panel.estimates.get(key)
    return math.nan if got is None else got.value


def varcomp(runs: "list[Run]", side_name: str) -> "list[float]":
    """[the worst variance ratio's distance (as max(r, 1/r)), the ICC gap, the slope-intercept correlation gap, the worst working
    correlation gap], medians over twin seeds, on ST7."""
    st7 = [r for r in runs if r.table == "ST7" and r.sides.get(side_name)]
    if not st7:
        return []
    worst, icc, corr, work = [], [], [], []
    for r in st7:
        real = r.yard.real.estimates
        for s in r.sides[side_name]:
            ratios = []
            for key in ("ST7/lmm:sd_patient", "ST7/lmm:sd_slope", "ST7/lmm:sd_residual"):
                if key in real and real[key].value > 0:
                    v = _value(s, key)
                    ratios += [math.inf if not v == v or v <= 0 else max((v / real[key].value) ** 2,
                                                                         (real[key].value / v) ** 2)]
            worst += [max(ratios) if ratios else math.nan]
            icc += [abs(_value(s, "ST7/ri:icc") - real["ST7/ri:icc"].value) if "ST7/ri:icc" in real else math.nan]
            corr += [abs(_value(s, "ST7/lmm:corr") - real["ST7/lmm:corr"].value) if "ST7/lmm:corr" in real
                     else math.nan]
            gaps = [abs(_value(s, k) - real[k].value) for k in real if k.endswith(":working_corr")]
            work += [max(gaps) if gaps else math.nan]
    return [round(_median(x), 3) for x in (worst, icc, corr, work)]


CURVATURE_SHARE = 0.5
# The 200,000-row ratio bar reads a curvature term only where a ratio's own noise is small: the SD of a frame's term
# over the real one is about h / (sqrt(2) |real|) at the size h was measured (h, the half-split yardstick, is about two
# standard errors of the whole table's estimate, and a ratio of two independent estimates has about sqrt(2) of one's
# noise); projected to the size read, times sqrt(h's rows / the rows read). A term above RATIO_NOISE is read inside its
# yardstick instead (the statistics check's item 3: ST7's growth bend read 0.71 to 2.57 on fresh replicates).
RATIO_NOISE = 0.1
CURVATURE_RATIO = 0.8


def ratio_noise(h: float, real: float, h_rows: int, rows: int) -> float:
    """A curvature ratio's noise SD at ``rows`` rows from a yardstick ``h`` measured at ``h_rows`` rows."""
    if not real:
        return math.inf
    return h / (math.sqrt(2.0) * abs(real)) * math.sqrt(h_rows / rows)


def curvature(runs: "list[Run]", side_name: str) -> "dict[str, object]":
    """A frame's curvature terms against the real table's: `ratio_min`, the minimum over the terms whose ratio is readable
    at the run's size (`ratio_noise` at most `RATIO_NOISE`) of the frame's term over the real one (median over twin
    seeds); `inside`, the median over twin seeds of the share of every curvature term inside its yardstick;
    `unread_inside`, that share over the terms whose ratio is not readable; `readable`, the readable terms."""
    ratios: "dict[str, list[float]]" = {}
    readable: "set[str]" = set()
    inside, unread = [], []
    k_max = max((len(r.sides.get(side_name, [])) for r in runs), default=0)
    for k in range(k_max):
        rows, unread_rows = [], []
        for r in runs:
            if k >= len(r.sides.get(side_name, [])):
                continue
            for c in r.sides[side_name][k].compared:
                if "curvature" not in c.tags:
                    continue
                rows += [c]
                term = f"{r.table}-{r.seed}-{c.key}"
                if ratio_noise(c.h, c.real, r.rows, r.rows) <= RATIO_NOISE:
                    readable.add(term)
                    if c.value is not None:
                        ratios.setdefault(term, []).append(c.value / c.real)
                    else:
                        ratios.setdefault(term, []).append(math.nan)
                else:
                    unread_rows += [c]
        if rows:
            inside += [sum(1 for c in rows if c.inside) / len(rows)]
        if unread_rows:
            unread += [sum(1 for c in unread_rows if c.inside) / len(unread_rows)]
    by_term = [_median(v) if any(x == x for x in v) else -math.inf for v in ratios.values()]
    return {"ratio_min": min(by_term) if by_term else math.nan, "inside": _median(inside),
            "unread_inside": _median(unread), "readable": sorted(readable)}


def curvature_value(reading: "dict[str, object]", suffix: str) -> float:
    """The curvature bar's reading: at 20,000 rows the share of curvature terms inside their yardsticks; at 200,000 rows 1.0
    where every readable term keeps at least `CURVATURE_RATIO` of the real bend and the others are inside their
    yardsticks at the 20,000-row share, 0.0 where not, NaN where nothing was read."""
    if suffix != "_200k":
        return float(reading["inside"])  # type: ignore[arg-type]
    ratio, unread = float(reading["ratio_min"]), float(reading["unread_inside"])  # type: ignore[arg-type]
    if ratio != ratio and unread != unread:
        return math.nan
    ok = (ratio != ratio or ratio >= CURVATURE_RATIO) and (unread != unread or unread >= CURVATURE_SHARE)
    return 1.0 if ok else 0.0


def curve_bar(suffix: str) -> "Callable[[float], bool]":
    return (lambda x: x >= 1.0) if suffix == "_200k" else (lambda x: x >= CURVATURE_SHARE)


def bar(name: str, twin: float, replicate: float, passes: "Callable[[float], bool]",
        shuffled: float = math.nan) -> "dict[str, object]":
    """An absolute bar, VOID where the replicate fails it (too tight for this table at this size) or where the shuffled
    twin meets it (it cannot tell a twin with no joint structure from a faithful one): recorded, never judged."""
    rep_ok = replicate == replicate and passes(replicate)
    twin_ok = twin == twin and passes(twin)
    shuffle_meets = shuffled == shuffled and passes(shuffled)
    reason = ("not read in this run" if replicate != replicate else "the replicate fails it" if not rep_ok
              else "the shuffle meets it" if shuffle_meets else "")
    return {"bar": name, "twin": bool(twin_ok), "replicate": bool(rep_ok), "shuffled": bool(shuffle_meets),
            "void": bool(reason), "void_reason": reason, "read": twin == twin and replicate == replicate,
            "value": None if twin != twin else round(float(twin), 4)}


def _entries(runs: "list[Run]", side_name: str, table: "str | None" = None) -> "list[tuple[Run, Side]]":
    return [(r, s) for r in runs if table is None or r.table == table for s in r.sides.get(side_name, [])]


def _extra_median(runs: "list[Run]", side_name: str, key: str) -> float:
    return _median([s.extra.get(key, math.nan) for _r, s in _entries(runs, side_name)])


def _table_max(runs: "list[Run]", side_name: str, key: str, tables: "tuple[str, ...] | None" = None) -> float:
    """A side's extra measure, the median over a table run's twin seeds, then the MAXIMUM over the table runs (a table
    that misses is never hidden by the tables that meet; the statistics check's item 5).

    Read on the runs of ``tables`` (by default the tables Table 1 is read
    on, `TABLE1`). A run of one of them that holds no reading of the
    measure on a twin seed (a twin not made, a Table 1 that could not be
    read) reads infinity there: a missing result is never a good result,
    and 0.04 beside a missing result is not 0.04 (Codex's review, its item
    1; LANE MU RULINGS 6 (1)). NaN only where no run of those tables is
    read at all.
    """
    wanted = tuple(TABLE1) if tables is None else tables

    def read(s: Side) -> float:
        value = s.extra.get(key, math.inf)
        return math.inf if value != value else value

    per = [_median([read(s) for s in r.sides[side_name]]) for r in runs if r.table in wanted and r.sides.get(side_name)]
    return max(per) if per else math.nan


def _gap(runs: "list[Run]", side_name: str, key: str, scale: float = 100.0) -> float:
    """|the side's estimate - the real one| x ``scale``, the median over table runs and twin seeds."""
    out = []
    for r, s in _entries(runs, side_name):
        est = r.yard.real.estimates.get(key)
        if est is not None:
            out += [abs(_value(s, key) - est.value) * scale]
    return _median(out) if out else math.nan


def _worst_gap(runs: "list[Run]", side_name: str, prefix: str, scale: float = 100.0) -> float:
    """The largest |side - real| x ``scale`` over the estimates whose key starts with ``prefix``, median over runs and seeds."""
    out = []
    for r, s in _entries(runs, side_name):
        keys = [k for k in r.yard.real.estimates if k.startswith(prefix)]
        if keys:
            out += [max(abs(_value(s, k) - r.yard.real.estimates[k].value) * scale for k in keys)]
    return _median(out) if out else math.nan


def _rules_broken(runs: "list[Run]", side_name: str) -> float:
    """The largest share of rows (or persons) breaking one of ST8's four structure rules, median over runs and seeds."""
    out = []
    for r, s in _entries(runs, side_name, "ST8"):
        keys = [k for k in r.yard.real.estimates if k.startswith("ST8/rule:")]
        if keys:
            out += [max(_value(s, k) for k in keys)]
    return _median(out) if out else math.nan


def _real_gap(runs: "list[Run]", side_name: str, key: str) -> float:
    """|the side's extra measure - the real table's own| (`Run.real_extra`), median over runs and seeds."""
    out = [abs(s.extra.get(key, math.nan) - r.real_extra[key]) for r, s in _entries(runs, side_name)
           if key in r.real_extra]
    return _median(out) if out else math.nan


def _tstr(runs: "list[Run]", side_name: str, model: str, metric: str) -> float:
    """A prediction model trained on the side and tested on the real table: its metric (the AUC less the run's OWN TRTR
    AUC), median over table runs and twin seeds."""
    out = []
    for r, s in _entries(runs, side_name):
        value = s.extra.get(f"{model}:{metric}", math.nan)
        if metric == "auc":
            trtr = r.tstr_yard.get(f"{model}:auc")
            value = value - trtr[0] if trtr is not None else math.nan
        if r.table == model.split("/")[0]:
            out += [value]
    return _median(out) if out else math.nan


def _yardsticks(runs: "list[Run]", side_name: str, key: str) -> float:
    """An estimate's distance from the real value in its own yardsticks, median over seeds and table runs."""
    out = []
    for r in runs:
        h = r.yard.h.get(key)
        if not h:
            continue
        for s in r.sides.get(side_name, []):
            v = _value(s, key)
            out += [(v - r.yard.real.estimates[key].value) / h]
    return _median(out)


def _ratio(runs: "list[Run]", side_name: str, keys: "tuple[str, ...]") -> float:
    out = []
    for r in runs:
        for key in keys:
            est = r.yard.real.estimates.get(key)
            if est is None or not est.value:
                continue
            for s in r.sides.get(side_name, []):
                out += [_value(s, key) / est.value]
    return _median(out)


FMI_KEYS = ("ST11/mice_fmi:lab_a", "ST11/mice_fmi:lab_c", "ST11/mice_fmi:age")
TSTR_MODELS = ("ST9/tstr_glm", "ST9/tstr_hgb", "ST7/tstr_glm", "ST7/tstr_hgb")


def measures(runs: "list[Run]", suffix: str) -> "dict[str, object]":
    """K-BC-14's value at one size (``suffix`` '_20k' or '_200k'), and its detail: the bars, each void where the replicate
    fails it or the shuffled twin meets it."""
    held = controls(runs)
    fam = held["fam"]
    sizes = held["sizes"]
    flips = _per_seed(runs, "twin", strong_flips)
    stops = _per_seed(runs, "twin", stopping)
    kept_t, inv_t = decisions(runs, "twin")
    kept_r, inv_r = decisions(runs, "replicate")
    kept_s, inv_s = decisions(runs, "shuffled")
    curve = {name: curvature(runs, name) for name in ("twin", "replicate", "flattened")}
    tstr = [_extra_median(runs, "twin", f"ST9/tstr_glm:{m}") for m in ("auc", "slope", "intercept", "risk_corr")]
    trtr = _median([r.tstr_yard["ST9/tstr_glm:auc"][0] for r in runs if "ST9/tstr_glm:auc" in r.tstr_yard])
    value: "dict[str, object]" = {
        f"controls_hold{suffix}": held["hold"],
        f"supported_estimates{suffix}": held["supported"],
        f"pooled_points_below_replicate{suffix}": round(held["gap"], 1),  # type: ignore[arg-type]
        f"worst_family_points_below_replicate{suffix}": round(held["worst"], 1),  # type: ignore[arg-type]
        f"strong_sign_flips{suffix}": int(flips) if flips == flips else None,
        f"stops{suffix}": int(stops) if stops == stops else None,
        f"fam{suffix}": {f: [round(_median(fam["twin"].get(f, [math.nan])), 3),  # type: ignore[index, union-attr]
                             round(_median(fam["replicate"][f]), 3),  # type: ignore[index]
                             round(_median(fam["shuffled"].get(f, [math.nan])), 3),  # type: ignore[index, union-attr]
                             sizes.get(f, 0)]  # type: ignore[union-attr]
                         for f in sorted(fam["replicate"])},  # type: ignore[index]
        f"families_control_void{suffix}": list(held["void"]),  # type: ignore[call-overload]
        f"decisions{suffix}": [round(x, 3) for x in (kept_t, kept_r, inv_t, inv_r)],
        f"se_ratio_ok{suffix}": [round(se_ratio_share(runs, "twin"), 3), round(se_ratio_share(runs, "replicate"), 3)],
        f"varcomp{suffix}": varcomp(runs, "twin"),
        f"tstr{suffix}": [round(tstr[0], 3), round(trtr, 3), round(tstr[1], 3), round(tstr[2], 3), round(tstr[3], 3)],
        f"ate{suffix}": [round(_yardsticks(runs, "twin", "ST9/ate:weighting"), 2),
                         round(_yardsticks(runs, "twin", "ST9/ate:matching"), 2)],
        f"smd_after_weighting_max{suffix}": round(_extra_median(runs, "twin", "smd_after"), 3),
        f"curve_retained{suffix}": [round(float(curve["twin"]["ratio_min"]), 3),  # type: ignore[arg-type]
                                    round(float(curve["flattened"]["ratio_min"]), 3)],  # type: ignore[arg-type]
        f"alpha_ratio{suffix}": round(_ratio(runs, "twin", ("ST10/zinb:alpha",)), 3),
        f"fmi_ratio{suffix}": round(_ratio(runs, "twin", FMI_KEYS), 3),
        f"selection{suffix}": [round(_extra_median(runs, "twin", "lasso_jaccard"), 3),
                               round(_extra_median(runs, "replicate", "lasso_jaccard"), 3)],
        f"mixture{suffix}": [round(_extra_median(runs, "twin", "gmm_same_classes"), 3),
                             round(_extra_median(runs, "twin", "gmm_ari"), 3),
                             round(_extra_median(runs, "replicate", "gmm_ari"), 3)],
        f"rare_share_gap{suffix}": round(_gap(runs, "twin", "ST12/rare:share"), 2),
    }

    def judged(name: str, read: "Callable[[str], float]", passes: "Callable[[float], bool]") -> "dict[str, object]":
        """A bar read the same way on the twin, the replicate and the shuffled twin."""
        return bar(name, read("twin"), read("replicate"), passes, read("shuffled"))

    curve["shuffled"] = curvature(runs, "shuffled")
    curve_t, curve_r, curve_f, curve_s = (curvature_value(curve[n], suffix)
                                          for n in ("twin", "replicate", "flattened", "shuffled"))
    passes_curve = curve_bar(suffix)
    curvature_bar = bar("curvature retained", curve_t, curve_r, passes_curve, curve_s)
    flattened_fails = curve_f == curve_f and not passes_curve(curve_f)
    curvature_bar["void"] = bool(curvature_bar["void"] or not flattened_fails)
    if not flattened_fails and not curvature_bar["void_reason"]:
        curvature_bar["void_reason"] = ("the flattened replicate has no reading" if curve_f != curve_f
                                        else "the flattened replicate meets it")
    curvature_bar["flattened_fails"] = flattened_fails
    curvature_bar["readable_terms"] = curve["twin"]["readable"]
    bars = [
        bar("pooled at most 10 points under the replicate", held["gap"], 0.0, lambda x: x <= 10.0,  # type: ignore
            held["shuffle_gap"]),  # type: ignore[arg-type]
        bar("decisions kept at least the replicate's minus 5 points", kept_t, kept_r, lambda x: x >= kept_r - 0.05,
            kept_s),
        bar("significance invented at most the replicate's plus 2 points", inv_t, inv_r, lambda x: x <= inv_r + 0.02,
            inv_s),
        judged("SE ratio 0.8 to 1.25 for 90 per cent of coefficients (several rows a person)",
               lambda n: se_ratio_share(runs, n), lambda x: x >= 0.9),
        curvature_bar,
    ]
    vc = {name: varcomp(runs, name) for name in ("twin", "replicate", "shuffled")}
    if vc["twin"] and vc["replicate"]:
        for i, (name, passes) in enumerate((("variance ratios 0.75 to 1.33", lambda x: x <= 1.0 / 0.75),
                                            ("ICC within 0.05", lambda x: x <= 0.05),
                                            ("slope-intercept correlation within 0.15", lambda x: x <= 0.15),
                                            ("working correlations within 0.05", lambda x: x <= 0.05))):
            bars += [bar(name, vc["twin"][i], vc["replicate"][i], passes,
                         vc["shuffled"][i] if vc["shuffled"] else math.nan)]
    ks_r, gaps_r = _extra_median(runs, "replicate", "ks_rows"), _extra_median(runs, "replicate", "ks_gaps")
    bars += [judged("rows per person KS at most the replicate's plus 0.05", lambda n: _extra_median(runs, n, "ks_rows"),
                    lambda x: x <= ks_r + 0.05),
             judged("gaps between visits KS at most the replicate's plus 0.05",
                    lambda n: _extra_median(runs, n, "ks_gaps"), lambda x: x <= gaps_r + 0.05)]
    for model in TSTR_MODELS:
        bars += [judged(f"{model}: AUC at least its run's TRTR minus 0.02", lambda n, m=model: _tstr(runs, n, m, "auc"),
                        lambda x: x >= -0.02),
                 judged(f"{model}: calibration slope 0.85 to 1.15", lambda n, m=model: _tstr(runs, n, m, "slope"),
                        lambda x: 0.85 <= x <= 1.15),
                 judged(f"{model}: calibration intercept within 0.1",
                        lambda n, m=model: _tstr(runs, n, m, "intercept"), lambda x: abs(x) <= 0.1),
                 judged(f"{model}: risk correlation at least 0.95", lambda n, m=model: _tstr(runs, n, m, "risk_corr"),
                        lambda x: x >= 0.95)]
    bars += [judged("max abs SMD after weighting under 0.1", lambda n: _extra_median(runs, n, "smd_after"),
                    lambda x: x < 0.1),
             judged("max abs SMD before weighting within 0.1 of the real's", lambda n: _real_gap(runs, n, "smd_before"),
                    lambda x: x <= 0.1),
             judged("propensity AUC within 0.02", lambda n: _gap(runs, n, "ST9/prop:auc", 1.0), lambda x: x <= 0.02),
             judged("the weighted ATE inside its yardstick", lambda n: abs(_yardsticks(runs, n, "ST9/ate:weighting")),
                    lambda x: x <= 1.0),
             judged("Table 1 SMDs under 0.1 (the worst table)", lambda n: _table_max(runs, n, "t1_smd_max"),
                    lambda x: x < 0.1),
             judged("alpha ratio 0.75 to 1.33", lambda n: _ratio(runs, n, ("ST10/zinb:alpha",)),
                    lambda x: 0.75 <= x <= 1.33),
             judged("fraction of missing information ratio 0.75 to 1.33", lambda n: _ratio(runs, n, FMI_KEYS),
                    lambda x: 0.75 <= x <= 1.33),
             judged("zero share within 1 point", lambda n: _gap(runs, n, "ST10/zeros:share"), lambda x: x <= 1.0),
             judged("rare-level share within 1 point", lambda n: _gap(runs, n, "ST12/rare:share"), lambda x: x <= 1.0),
             judged("censored share by centre within 2 points", lambda n: _worst_gap(runs, n, "ST8/censored:"),
                    lambda x: x <= 2.0),
             judged("structure rules broken 0", lambda n: _rules_broken(runs, n), lambda x: x == 0.0),
             judged("0 analyses that stop on the twin", lambda n: _per_seed(runs, n, stopping), lambda x: x == 0)]
    sel_r = _extra_median(runs, "replicate", "lasso_jaccard")
    bars += [judged("selection agreement at least the replicate's minus 0.1",
                    lambda n: _extra_median(runs, n, "lasso_jaccard"), lambda x: x >= sel_r - 0.1),
             judged("the same BIC class count", lambda n: _extra_median(runs, n, "gmm_same_classes"),
                    lambda x: x == 1.0),
             judged("adjusted Rand index at least 0.7", lambda n: _extra_median(runs, n, "gmm_ari"), lambda x: x >= 0.7)]
    return {"value": value, "bars": bars, "routes": sorted({r.route for r in runs}),
            "extra_sides": sorted({name for r in runs for name in r.sides if name.startswith("twin_")}),
            "curvature": curve}


def route_shares(runs: "list[Run]") -> "dict[str, dict[str, object]]":
    """Each labelled route's family shares beside the headline's computed over the SAME table runs (never read by the
    ratchet; the statistics check's item 8), and each one's variance components on ST7."""
    out: "dict[str, dict[str, object]]" = {}
    for name in sorted({n for r in runs for n in r.sides if n.startswith("twin_")}):
        same = [r for r in runs if r.sides.get(name)]
        out[name] = {
            "tables": sorted({f"{r.table}-{r.seed}" for r in same}),
            "route": {f: round(_median(v), 3) for f, v in family_shares(same, name).items()},
            "twin": {f: round(_median(v), 3) for f, v in family_shares(same, "twin").items()},
            "varcomp": varcomp(same, name),
        }
    return out


# THE OWNER'S FOUR (F11 to F14): an analysis of these that does not run on a real table and all eight halves leaves
# a family of his first analyses unmeasured, and the driver writes no stamp (the statistics check's item 2).
OWNER_FOUR = ("F11", "F12", "F13", "F14")
OWNER_FOUR_ANALYSES = {
    "ST7/lmm": "F11", "ST7/ri": "F11", "ST7/gee_exch": "F11", "ST7/gee_ar1": "F11", "ST7/gee_bin": "F11",
    "ST7/structure": "F11", "ST8/cox_tv": "F12", "ST8/cox_naive": "F12", "ST8/cox_comp": "F12", "ST8/km": "F12",
    "ST9/prop": "F13",
}


def owner_four_unrobust(runs: "list[Run]") -> "list[str]":
    """Every analysis of F11 to F14 that is not robust on a real table (stopped on it or on one of its eight halves), and
    every prediction model of F14 with no TRTR yardstick on its table, named with the table run."""
    out = []
    for r in runs:
        for name, family in OWNER_FOUR_ANALYSES.items():
            if name.split("/")[0] == r.table and name not in r.yard.robust:
                out += [f"{r.table}-{r.seed} {name} ({family}: {r.yard.real.status.get(name, 'missing')} on the real "
                        "table or a half)"]
        if r.table in PREDICTION:
            for kind in ("glm", "hgb"):
                if f"{r.table}/tstr_{kind}:auc" not in r.tstr_yard:
                    out += [f"{r.table}-{r.seed} {r.table}/tstr_{kind} (F14: no TRTR yardstick)"]
    return out


def drift(fam_20k: "dict[str, list[object]]", fam_200k: "dict[str, list[object]]") -> "dict[str, float]":
    """BC-ARCH's drift slot: per family, the gap to the replicate at 200,000 rows minus the gap at 20,000, in points."""
    out = {}
    for family in sorted(set(fam_20k) & set(fam_200k)):
        a, b = fam_20k[family], fam_200k[family]
        try:
            gap_20 = 100.0 * (float(a[1]) - float(a[0]))  # type: ignore[arg-type]
            gap_200 = 100.0 * (float(b[1]) - float(b[0]))  # type: ignore[arg-type]
        except (TypeError, ValueError):
            continue
        if gap_20 == gap_20 and gap_200 == gap_200:
            out[family] = round(gap_200 - gap_20, 1)
    return out


# -- the truths -----------------------------------------------------------------------------------


# A truth whose key does not begin with the name of the analysis that writes it: that analysis.
TRUTH_ANALYSIS = {"ST9/ate": "ST9/prop", "ST11/miss_a": "ST11/missing", "ST11/miss_b": "ST11/missing"}


def truth_plan(table: str, real: B.View) -> "list[Analysis]":
    """The analyses that hold a truth of the table (each truth's key names its analysis, or `TRUTH_ANALYSIS` does; the
    whole plan where an analysis named is not in it)."""
    plan = plan_for(table, real)
    wanted = {TRUTH_ANALYSIS.get(key.split(":")[0], key.split(":")[0]) for key, _value, _kind in U.TRUTHS[table].values()}
    held = [a for a in plan if a.name in wanted]
    return held if {a.name for a in held} == wanted else plan


def truth_tolerance(key: str, est: "Estimate | None", rows: int) -> float:
    """Four standard errors of the estimate; for an approximate estimate (no standard error), four times the spread its
    value showed over independent draws (`utility_tables.ACROSS_DRAW_SD`). That spread is NOT scaled by the rows: the
    variational check reads about `BAYES_PERSONS` persons at every size (the share is fixed on each real table), so its
    noise does not shrink as the table grows (at 200,000 rows on table seed 1 its arm read 0.1245 against 0.5, 2.9 of the
    spread measured at 20,000)."""
    if key in U.ACROSS_DRAW_SD:
        return 4.0 * U.ACROSS_DRAW_SD[key][0]
    if est is None or not est.se:
        return math.nan
    return 4.0 * est.se


def truth_misses(table: str, panel: B.Panel, rows: int) -> "list[str]":
    """Each truth of the table its estimate on ``panel`` misses by more than `truth_tolerance` (or lacks), named."""
    misses = []
    for name, (key, truth, _kind) in U.TRUTHS[table].items():
        est = panel.estimates.get(key)
        tolerance = truth_tolerance(key, est, rows)
        if est is None or not tolerance == tolerance or abs(est.value - truth) > tolerance:
            misses += [f"{name} ({key}): {None if est is None else round(est.value, 4)} against {truth}"
                       f" (tolerance {round(tolerance, 4) if tolerance == tolerance else None})"]
    return misses


def generated_truth_checks(tables: "tuple[str, ...]" = U.TABLES, rows: int = 20000,
                           seed: int = 1) -> "dict[str, dict[str, object]]":
    """Each table's truths against the battery's own fits on a real table of ``rows`` rows (its truth-holding analyses
    alone, `truth_plan`): per table the analyses that did not run and the truths missed (the night's first step at
    200,000 rows, `kpi_model_utility.py --night`; the gate file's truth cases at 20,000)."""
    out: "dict[str, dict[str, object]]" = {}
    for table in tables:
        real = B.read(U.text(table, rows, seed), f"{table} truth")
        panel = B.run_panel(truth_plan(table, real), real)
        out[table] = {"stopped": sorted(n for n, s in panel.status.items() if s != "ok"),
                      "misses": truth_misses(table, panel, rows)}
        del real
        gc.collect()
    return out


# -- K-BC-14's ledger entry ----------------------------------------------------------------------

KPI_NAME = "Model utility by family: advanced analyses on the twin a person gets, against the fresh replicate"
KPI_RULE = (
    "Per family (F11 to F22 and F24, plan P4-D485: six invented tables of known structure, ST7 to ST12, "
    "tests/model_utility.py), the share of supported estimates inside lane E0b's half-split yardstick on the twin a "
    "person gets (route S: the typed commands, every question of the questions file answered as the person who holds "
    "the table answers it), against the fresh replicate's share in the same run, at 20,000 rows (table seeds 1 to 3, "
    "twin seeds 0 to 2, each twin seed under its own installation key) and at 200,000 rows (seed 1). Controls: the "
    "replicate within three binomial SDs of 77 per cent; the shuffled twin more than 10 points under it pooled and 25 in "
    "every family of at least five estimates (families_control_void names the others); the flattened replicate (the "
    "curve halved) fails the curvature bar, else that bar is void; every absolute bar is void where the replicate fails "
    "it or the shuffled twin meets it. Bound, a ratchet from the first switched stamp: the controls hold; pooled no more "
    "than max(10, 318/sqrt(n)) points under the recorded stamp; supported estimates not fewer; strong effects reversed "
    "(real |z| above 3.29, the twin's sign opposite) not more than the stamp plus max(3, 3 sqrt(stamp)); analyses that "
    "stop not more. Target (the release candidate of 2026-12-11): pooled at most 10 points under the replicate, every "
    "family of at least five at most 25 (the worst family is a target only), and the bars of P4-D485. Routes C, U and P "
    "are labelled and never enter the ratchet. drift: per family, the gap at 200,000 rows minus the gap at 20,000 "
    "(BC-ARCH's reserved slot)."
)


# K-BC-14's two tiers, each key suffix with the command that measures it: an ordinary `kpi_run.py --slow` runs the
# registered `--kpi` and judges the `_20k` keys alone (`kpi_rules.tier_bounds`; LANE MU RULINGS 6 (6), Codex's review,
# its item 8: the 200,000-row keys of a stamp holding both tiers were rejected as not measured).
KPI_TIERS = {"_20k": "tools/measurements/kpi_model_utility.py --kpi",
             "_200k": "tools/measurements/kpi_model_utility.py --night"}


def allowance(n: int) -> float:
    """E0b's noise allowance for a pooled share of n estimates, in points: 318 / sqrt(n), never under 10."""
    return max(10.0, 318.0 / math.sqrt(n)) if n > 0 else 10.0


def flips_allowance(stamped: int) -> float:
    """The strong flips' noise allowance over a stamped count: max(3, 3 sqrt(stamped)) (the statistics check's item 7:
    one table seed's three twin seeds read 10, 18 and 16 on ST9)."""
    return max(3.0, 3.0 * math.sqrt(max(stamped, 0)))


def ledger_entry(value: "dict[str, object]", commit: str, date: str, measured_by: str) -> "dict[str, object]":
    """K-BC-14's ledger entry from a stamp's value: the ratchet's expected values set from it (the first switched stamp).

    The worst family is a TARGET ONLY (its replicate share swings within one
    run over a family of three to forty-five estimates); the strong flips
    are ratcheted with `flips_allowance`.
    """
    expected: "dict[str, object]" = {}
    kinds: "dict[str, str]" = {}
    target: "dict[str, object]" = {}
    for size in ("_20k", "_200k"):
        if f"controls_hold{size}" not in value:
            continue
        n = int(value.get(f"supported_estimates{size}") or 0)  # type: ignore[call-overload]
        expected[f"controls_hold{size}"] = True
        kinds[f"controls_hold{size}"] = "exact"
        expected[f"supported_estimates{size}"] = n
        kinds[f"supported_estimates{size}"] = "at_least"
        stamped = value.get(f"pooled_points_below_replicate{size}")
        if isinstance(stamped, (int, float)):
            expected[f"pooled_points_below_replicate{size}"] = round(float(stamped) + allowance(n), 1)
        flips = value.get(f"strong_sign_flips{size}")
        if isinstance(flips, int):
            expected[f"strong_sign_flips{size}"] = round(flips + flips_allowance(flips), 1)
        stops = value.get(f"stops{size}")
        if isinstance(stops, int):
            expected[f"stops{size}"] = stops
        target[f"pooled_points_below_replicate{size}"] = 10.0
        target[f"worst_family_points_below_replicate{size}"] = 25.0
        target[f"strong_sign_flips{size}"] = 0
        target[f"stops{size}"] = 0
    return {
        "id": "K-BC-14", "phase_stage": "The broad between-columns program (plan P4-D485, lane MU)", "category": "STATS",
        "headline": True, "name": KPI_NAME, "status": "OPEN", "rule": KPI_RULE, "rule_kind": "at_most",
        "expected": expected, "tier": "SLOW", "source": "driver", "nodes": [], "test": None,
        "driver": "tools/measurements/kpi_model_utility.py --kpi", "tiers": dict(KPI_TIERS), "pin_strength": "NONE",
        "measured_on": "tools/measurements/kpi_model_utility.py --kpi (the _20k keys) and --night (the _200k keys, drift)",
        "evidence": "The FID audit's pilot (one 9-column cohort at 20,000 rows) and lane MU's build and repair reports.",
        "key_kinds": kinds,
        "value_at": {"commit": commit, "date": date, "value": value, "measured_by": measured_by},
        "target_stage": "the release candidate of 2026-12-11", "target": target,
    }


def worst_case_value() -> "dict[str, object]":
    """Every key `measures` and the driver write, at both sizes, filled with the widest numbers they print (for the size case)."""
    fam = {f: [0.123, 0.789, 0.456, 1234] for f in FAMILIES}
    value: "dict[str, object]" = {}
    for size in ("_20k", "_200k"):
        value.update({
            f"controls_hold{size}": False, f"supported_estimates{size}": 12345,
            f"pooled_points_below_replicate{size}": -100.0, f"worst_family_points_below_replicate{size}": -100.0,
            f"strong_sign_flips{size}": 1234, f"stops{size}": 123, f"fam{size}": fam,
            f"families_control_void{size}": list(FAMILIES), f"decisions{size}": [0.123, 0.456, 0.789, 0.012],
            f"se_ratio_ok{size}": [0.123, 0.456], f"varcomp{size}": [12.345, 0.123, 0.456, 0.789],
            f"tstr{size}": [0.123, 0.456, -1.234, -0.123, 0.987], f"ate{size}": [-12.34, -12.34],
            f"smd_after_weighting_max{size}": 0.123, f"curve_retained{size}": [-0.123, 0.456],
            f"alpha_ratio{size}": 1.234, f"fmi_ratio{size}": 1.234, f"rare_share_gap{size}": 12.34,
            f"selection{size}": [0.123, 0.456], f"mixture{size}": [0.123, 0.456, 0.789],
            f"route{size}": {t: "S" for t in U.TABLES},
        })
    value["seconds_20k"] = 12345.6
    value["seconds_per_table_200k"] = {t: 12345.6 for t in U.TABLES}
    value["cpu_seconds_per_table_200k"] = {t: 12345.6 for t in U.TABLES}
    value["peak_mb_200k"] = 1234.5
    value["drift"] = {f: -100.0 for f in FAMILIES}
    return value

"""The model-utility battery's own guarantees (lane MU, plan P4-D485; K-BC-14).

The battery (`tests/model_utility.py`) measures whether advanced analyses
fitted on the twin give the real table's answers; its claims come from
its driver (`tools/measurements/kpi_model_utility.py`) at 20,000 and
200,000 rows, never from this file. This file holds what the claims rest
on, with no product run at 20,000 rows:

* each generator meets its truths at 20,000 rows, by the battery's own
  analyses (within four standard errors; the approximate variational
  estimates within four times their spread over independent draws), and
  the truth files hold the generators' constants;
* each fitter written by hand meets a known answer: the Weibull model of
  shape 1 is the exponential model's closed form, the Aalen-Johansen
  incidence with no competing event is one minus Kaplan and Meier's curve
  (statsmodels' own), meets a hand-worked case of two causes and, with
  two causes and no censoring, is each cause's share with the binomial
  standard error; the multinomial model meets its saturated closed forms;
* a fit is read only where it settled: a library warning that it did not
  stops the analysis (the boundary's aside), a fit's own record of not
  settling stops it, a Cox model with no event in a group stops, a
  separated binomial fit stops (at `_glm` and at each of the five other
  call sites: the binomial GEE, the GAM, the prediction model, the
  calibration fits and MICE), MICE and the variational fit are the same
  fit twice, a start-stop row is at risk from after its start and a row
  with a time below 0 is one failed analysis, and the booster runs on one
  OpenMP thread;
* the harness: a person's rows land in one half, an estimate under the
  support rule is never scored, the cells are E0b's, controls that are
  swapped void a run, the flattened replicate fails the curvature bar
  where the replicate passes it (ST9 and ST7) and a bar the flattened
  replicate meets or does not read is void, an absolute bar the replicate
  fails or the shuffled twin meets is void, a comparison Table 1 cannot
  make is a difference and a prediction that stops on the twin a stop,
  the driver's values hold no infinity, K-BC-14's entry stays within
  12,000 bytes and is judged by the runner on the tier its run produced,
  each check of an entry's tiers names its fault, a
  kept run is read back only for the routes it was asked for, the routes'
  installation folder lies outside the table's folder and every out
  folder, and route S answers every question of the questions file as the
  person who holds the table answers it;
* the fast part, ST7 and ST9 at 5,000 rows through route C: a TEST DEVICE
  (crash-freedom and the harness only, no claim; LANE I4m RULINGS 18 (4)).

THE TEST-ONLY LIBRARIES. statsmodels and scikit-learn are the development
lock's test-only libraries (plan P4-D409, zone P). CI's `minimums` cell
installs the declared floors alone, so there this file skips, with its
reason in the report line (LANE MU RULINGS 4 (1) item 1); in every cell
that installs the development lock a missing fitter is red, held by
`tests/test_dependencies.py`.

Every assertion on a fit is a tolerance in standard errors or a
known-answer tolerance, never a digit: CI runs Python 3.11 to 3.14 with
two numpy and scipy lines under the same statsmodels and scikit-learn pins.
"""

from __future__ import annotations

import pytest

pytest.importorskip("statsmodels", reason="a test-only library: CI's minimums cell installs the declared floors only")
pytest.importorskip("sklearn", reason="a test-only library: CI's minimums cell installs the declared floors only")

import ast  # noqa: E402
import gc  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import pathlib  # noqa: E402
import random  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402
import weakref  # noqa: E402

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import threadpoolctl  # noqa: E402
from sklearn.exceptions import ConvergenceWarning as LearnConvergenceWarning  # noqa: E402
from statsmodels.duration.survfunc import SurvfuncRight  # noqa: E402
from statsmodels.tools.sm_exceptions import ConvergenceWarning  # noqa: E402

import analyst_battery as B  # noqa: E402
import analyst_kit as K  # noqa: E402
import kpi_rules  # noqa: E402
import model_utility as M  # noqa: E402
import twin_routes  # noqa: E402
import utility_tables as U  # noqa: E402

TRUTH_ROWS = 20000
DRIVER = pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements" / "kpi_model_utility.py"
E0B_DRIVER = DRIVER.with_name("kpi_analyst_battery.py")


@pytest.mark.parametrize("table", U.TABLES)
def test_each_generator_meets_its_truths_at_20000_rows(table: str) -> None:
    """Every generating and computed truth lies within its tolerance of the battery's own estimate on one draw (four
    standard errors; an approximate estimate four times its spread over independent draws), and every analysis run for
    it runs (the analyses that hold a truth; ST7's other analyses run in the fast part)."""
    real = B.read(U.text(table, TRUTH_ROWS, 1), f"{table} truth")
    panel = B.run_panel(M.truth_plan(table, real), real)
    assert all(status == "ok" for status in panel.status.values()), panel.status
    misses = M.truth_misses(table, panel, TRUTH_ROWS)
    assert not misses, "; ".join(misses)
    approximate = [e for e in panel.estimates.values() if M.APPROXIMATE in e.tags]
    assert all(e.se is None for e in approximate), [e.key for e in approximate if e.se is not None]


def test_an_approximate_estimate_is_held_by_its_spread_over_draws() -> None:
    """The variational check's estimates carry no standard error: their truths are held by four times the spread over 24
    independent draws, neither dropped from the check nor held by a posterior SD (skeptic 1's item 5), and not scaled by
    the rows (the check reads about 300 persons at every size)."""
    sd, at = U.ACROSS_DRAW_SD["ST7/vb:arm"]
    truth = U.ST7_CTL[1]

    def panel(offset: float) -> B.Panel:
        est = B.Estimate("ST7/vb:arm", "F24", truth + offset, None, 500, (M.APPROXIMATE,))
        ok = {k: B.Estimate(k, "F11", value, 1e-9, 500) for k, value, _kind in U.TRUTHS["ST7"].values()
              if k != "ST7/vb:arm"}
        return B.Panel({**ok, "ST7/vb:arm": est}, {})

    assert any("ST7/vb:arm" in miss for miss in M.truth_misses("ST7", panel(5.0 * sd), at))
    assert not any("ST7/vb:arm" in miss for miss in M.truth_misses("ST7", panel(3.0 * sd), at))
    assert math.isclose(M.truth_tolerance("ST7/vb:arm", None, 10 * at), 4.0 * sd)
    assert {a.name for a in M.truth_plan("ST11", B.read(U.text("ST11", 600, 1), "small"))} == {"ST11/missing", "ST11/mice"}


def test_st7_stops_a_persons_visits_after_year_6_and_shares_its_clinics() -> None:
    """ST7: no visit falls more than six years after the person's first (the statistics check's item 2: the bend in arm
    B stays in a plausible range), and every table seed draws its pressures around the same twelve clinic effects."""
    rows = list(U.st7(6000, 3))
    first: "dict[str, str]" = {}
    for row in rows:
        first.setdefault(row[0], row[6])
    import datetime

    span = max((datetime.date.fromisoformat(row[6]) - datetime.date.fromisoformat(first[row[0]])).days for row in rows)
    assert span <= int(U.ST7_YEARS_MAX * 365.25) + 1, span
    assert len(U.ST7_CLINIC_EFFECT) == U.ST7_CLINICS


def test_every_table_seed_draws_its_pressures_around_the_same_clinic_effects(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 2 (a), read by behaviour: with the twelve clinic effects set 100 mmHg apart, each
    clinic's mean pressure follows its constant at two table seeds alike (a generator that drew its own clinic effects
    at each table seed would follow none)."""
    monkeypatch.setattr(U, "ST7_CLINIC_EFFECT", [100.0 * k for k in range(U.ST7_CLINICS)])
    for seed in (1, 2):
        by_clinic: "dict[int, list[float]]" = {}
        for row in U.st7(3000, seed):
            by_clinic.setdefault(int(row[1][1:]) - 1, []).append(float(row[7]))
        means = {k: sum(v) / len(v) for k, v in by_clinic.items()}
        assert len(means) == U.ST7_CLINICS
        assert all(abs((means[k] - means[0]) - 100.0 * k) < 25.0 for k in means), (seed, means)


def test_a_held_column_is_named_and_the_named_person_column_is_not(tmp_path: pathlib.Path) -> None:
    """`held_columns` names each column a typed description reads as record numbers though nobody named it, with the
    reason its text gives (the statistics check's item 8: finding F4 named on ST7)."""
    out = tmp_path / "typed"
    out.mkdir()
    (out / "T-profile.txt").write_text(
        "subject\n  read as: record numbers or codes (you named this column)\n"
        "age\n  read as: record numbers or codes, because too few people hold its values\n"
        "sbp\n  read as: a measurement\n", encoding="utf-8", newline="\n")
    made = twin_routes.Described("S", tmp_path, out, "T", out / "T-profile.json", False)
    assert twin_routes.held_columns(made) == ["age (because too few people hold its values)"]


def test_the_truth_files_hold_the_generators_constants() -> None:
    """Each GENERATING truth is the constant the generator sets; each COMPUTED one is its function's value (a smaller draw)."""
    assert U.TRUTHS["ST7"]["arm B x years"][1] == U.ST7_ARM_B_YEARS
    assert U.TRUTHS["ST8"]["treated, from its start"][1] == U.ST8_TREATED
    assert U.TRUTHS["ST9"]["quadratic age on death"][1] == U.ST9_DIED["age_sq"]
    assert U.TRUTHS["ST10"]["overdispersion"][1] == U.ST10_ALPHA
    assert U.TRUTHS["ST11"]["outcome by lab_a"][1] == U.ST11_OUTCOME["lab_a"]
    assert U.TRUTHS["ST12"]["severity per decade"][1] == U.ST12_SEVERITY["age"]
    incidence = U.st8_incidence_estimand(persons=100_000)
    stated = {key: value for key, value, _kind in U.TRUTHS["ST8"].values()}
    for cause, label in ((1, "event"), (2, "competing")):
        for t in (1, 3, 5):
            assert abs(incidence[f"{cause}_{t}"] - stated[f"ST8/aj:{label}_{t}"]) < 0.006, (label, t)
    stated_ate = [v for k, v, _kind in U.TRUTHS["ST9"].values() if k == "ST9/ate:weighting"][0]
    assert abs(U.st9_ate_estimand(persons=200_000) - stated_ate) < 0.002
    # ST7's repeated yes-or-no outcome, population-averaged (LANE MU RULINGS 7 (3)): the stated values are the function's
    # at its default 400,000 rows; a draw of 60,000 rows reads them within 0.002.
    controlled = U.st7_controlled_estimand(rows=60_000)
    stated7 = {key: value for key, value, _kind in U.TRUTHS["ST7"].values()}
    for term in ("arm", "years"):
        assert abs(controlled[term] - stated7[f"ST7/gee_bin:{term}"]) < 0.002, term
    for truths in U.TRUTHS.values():
        for key, _value, kind in truths.values():
            if kind == U.COMPUTED:
                assert callable(getattr(U, U.COMPUTED_BY[key.split(":")[0] + ":"], None)), key


def _exponential(n: int, seed: int, rate: float) -> "tuple[np.ndarray, np.ndarray]":
    r = random.Random(seed)
    times, events = [], []
    for _ in range(n):
        t, c = r.expovariate(rate), r.uniform(0.5, 6.0)
        times += [min(t, c)]
        events += [1.0 if t <= c else 0.0]
    return np.asarray(times), np.asarray(events)


def test_the_weibull_model_of_shape_one_is_the_exponential_closed_form() -> None:
    """Sigma held at 1 is the exponential model: its intercept is log(total time / events) to the digit of the optimizer;
    with sigma free on exponential data, sigma is 1 within four standard errors."""
    t, d = _exponential(4000, 3, 0.3)
    held = M.weibull_aft(t, d, {}, fixed_scale=1.0)
    assert abs(held.params["intercept"] - math.log(t.sum() / d.sum())) < 1e-7
    assert abs(held.bse["intercept"] - 1.0 / math.sqrt(d.sum())) < 1e-6
    free = M.weibull_aft(t, d, {})
    assert free.converged
    assert abs(free.params["log_scale"]) <= 4.0 * free.bse["log_scale"]
    x = np.asarray([float(i % 2) for i in range(len(t))])
    t2, d2 = t * np.exp(0.7 * x), d
    fit = M.weibull_aft(t2, d2, {"x": x}, fixed_scale=1.0)
    assert abs(fit.params["x"] - 0.7) <= 4.0 * fit.bse["x"]


def test_aalen_johansen_with_no_competing_event_is_one_minus_kaplan_meier() -> None:
    """With one cause, the incidence is one minus statsmodels' Kaplan-Meier curve at every asked time."""
    t, d = _exponential(3000, 5, 0.2)
    t = np.round(t, 1) + 0.1
    found = M.aalen_johansen(t, d.astype(int), (0.5, 1.0, 2.0, 4.0), causes=(1,))
    sf = SurvfuncRight(t, d)
    for point in (0.5, 1.0, 2.0, 4.0):
        at = int(np.searchsorted(sf.surv_times, point, side="right")) - 1
        assert abs(found.value[(1, point)] - (1.0 - sf.surv_prob[at])) < 1e-12
        assert abs(found.se[(1, point)] - sf.surv_prob_se[at]) < 1e-3


def test_aalen_johansen_meets_a_hand_worked_case_of_two_causes() -> None:
    """Five persons: times 1, 2, 2, 3, 4 ending by cause 1, cause 2, censored, cause 1, censored.

    At 1: five at risk, one by cause 1: F1 = 1/5, S = 4/5. At 2: four at
    risk (the one censored at 2 counted), one by cause 2: F2 = 4/5 x 1/4 =
    1/5, S = 3/5. At 3: two at risk, one by cause 1: F1 = 1/5 + 3/5 x 1/2 =
    1/2. At 4: censored, no change.
    """
    found = M.aalen_johansen(np.asarray([1.0, 2.0, 2.0, 3.0, 4.0]), np.asarray([1, 2, 0, 1, 0]), (0.5, 1.5, 2.5, 3.5, 9.0))
    expect = {(1, 0.5): 0.0, (2, 0.5): 0.0, (1, 1.5): 0.2, (2, 1.5): 0.0, (1, 2.5): 0.2, (2, 2.5): 0.2,
              (1, 3.5): 0.5, (2, 3.5): 0.2, (1, 9.0): 0.5, (2, 9.0): 0.2}
    for key, value in expect.items():
        assert abs(found.value[key] - value) < 1e-12, key


def test_aalen_johansen_with_two_causes_and_no_censoring_is_each_causes_share_and_its_binomial_se() -> None:
    """Two causes, no censoring, ties included: each cause's incidence at t is the share of persons ended by it by t, and
    its delta-method standard error is the binomial sqrt(F (1 - F) / n) (every term of the variance takes part)."""
    r = random.Random(41)
    t, c = [], []
    for _ in range(1500):
        a, b = r.expovariate(0.2), r.expovariate(0.1)
        t += [round(min(a, b), 2) + 0.01]
        c += [1 if a <= b else 2]
    times, causes = np.asarray(t), np.asarray(c)
    found = M.aalen_johansen(times, causes, (1.0, 3.0, 5.0))
    for k in (1, 2):
        for point in (1.0, 3.0, 5.0):
            share = float(((times <= point) & (causes == k)).mean())
            assert abs(found.value[(k, point)] - share) < 1e-12, (k, point)
            assert abs(found.se[(k, point)] - math.sqrt(share * (1.0 - share) / len(times))) < 1e-10, (k, point)


def test_the_multinomial_model_meets_its_saturated_closed_forms() -> None:
    """One flag: each outcome's intercept is log(n_k0 / n_ref0) and its flag term the log odds ratio of the 2 x 3 table,
    with the textbook standard errors sqrt(1/n_k0 + 1/n_ref0) and sqrt of the four reciprocals."""
    r = random.Random(11)
    x, y = [], []
    for _ in range(3000):
        flag = float(r.random() < 0.4)
        u = r.random()
        y += ["home" if u < 0.5 - 0.1 * flag else "rehabilitation" if u < 0.8 else "other"]
        x += [flag]
    xs = np.asarray(x)
    fit = M.multinomial(y, ("home", "rehabilitation", "other"), {"flag": xs})
    n = {(k, f): sum(1 for a, b in zip(y, x) if a == k and b == f) for k in ("home", "rehabilitation", "other")
         for f in (0.0, 1.0)}
    for k in ("rehabilitation", "other"):
        assert abs(fit.params[f"{k}_intercept"] - math.log(n[(k, 0.0)] / n[("home", 0.0)])) < 1e-8
        odds = math.log(n[(k, 1.0)] * n[("home", 0.0)] / (n[(k, 0.0)] * n[("home", 1.0)]))
        assert abs(fit.params[f"{k}_flag"] - odds) < 1e-8
        assert abs(fit.bse[f"{k}_intercept"] - math.sqrt(1 / n[(k, 0.0)] + 1 / n[("home", 0.0)])) < 1e-6
        se = math.sqrt(1 / n[(k, 1.0)] + 1 / n[("home", 0.0)] + 1 / n[(k, 0.0)] + 1 / n[("home", 1.0)])
        assert abs(fit.bse[f"{k}_flag"] - se) < 1e-6


def test_a_fit_that_did_not_settle_is_never_read() -> None:
    """A library warning that a fit did not settle stops the analysis ('no convergence'): statsmodels' and
    scikit-learn's; a variance component on its boundary, MixedLM's notice that it retries, and the Hessian's warning
    beside the boundary's do not (skeptic 1's item 4)."""

    def warns(*said: "tuple[str, type]") -> "M.Callable[[], object]":
        def fit() -> object:
            for text, category in said:
                warnings.warn(text, category, stacklevel=1)
            return "fitted"
        return fit

    for said in ([("Gradient optimization failed, |grad| = 14988.4", ConvergenceWarning)],
                 [("The max_iter was reached which means the coef_ did not converge", LearnConvergenceWarning)],
                 [(M.HESSIAN + ".", ConvergenceWarning)]):
        with pytest.raises(B.AnalysisError) as stopped:
            M._fit(warns(*said))
        assert stopped.value.kind == "no convergence"
    for said in ([(M.BOUNDARY + ".", ConvergenceWarning)], [(M.RETRYING + " with bfgs", ConvergenceWarning)],
                 [(M.BOUNDARY + ".", ConvergenceWarning), (M.HESSIAN + ".", ConvergenceWarning)],
                 [("an unrelated note", UserWarning)]):
        assert M._fit(warns(*said)) == "fitted"


class _Record:
    def __init__(self, **fields: object) -> None:
        self.__dict__.update(fields)


def test_a_fits_own_record_of_not_settling_stops_it() -> None:
    """statsmodels' `converged` and `mle_retvals`, scikit-learn's `converged_`, and an iteration count at its cap (saga)."""
    for record in (_Record(converged=False), _Record(converged_=False), _Record(mle_retvals={"converged": False}),
                   _Record(n_iter_=np.asarray([5000]), max_iter=5000)):
        with pytest.raises(B.AnalysisError):
            M._converged(record, "a fit")
    for record in (_Record(converged=True), _Record(converged_=True), _Record(mle_retvals={"converged": True}),
                   _Record(n_iter_=np.asarray([40]), max_iter=5000), _Record()):
        M._converged(record, "a fit")


def test_mice_and_the_variational_fit_are_the_same_fit_twice() -> None:
    """LANE MU RULINGS 6 (2) (Codex's review, its item 2): MICE and the variational fit draw from the generators handed
    to them through their own `rng` arguments, so two fits of one frame are the same fit: ST11 at 4,000 rows (table seed
    1) and ST7 at 4,000 rows, each fitted twice in one process, read identical coefficients, standard errors and
    fractions of missing information (unseeded, two MICE fits of the ST11 frame read lab_a 0.4244 and 0.4255)."""
    st11 = B.read(U.text("ST11", 4000, 1), "ST11")
    first = {e.key: (e.value, e.se) for e in M.st11_mice(st11)}
    assert first == {e.key: (e.value, e.se) for e in M.st11_mice(st11)}
    assert {"ST11/mice:lab_a", "ST11/mice_fmi:lab_a", "ST11/mice_fmi:age"} <= set(first)
    st7 = B.read(U.text("ST7", 4000, 1), "ST7")
    [vb] = [a for a in M.plan_st7(st7) if a.name == "ST7/vb"]
    once = {e.key: e.value for e in vb.run(st7)}
    assert once == {e.key: e.value for e in vb.run(st7)} and {"ST7/vb:arm", "ST7/vb:years"} <= set(once)


def _separated_frame(complete: bool) -> "tuple[np.ndarray, dict[str, np.ndarray]]":
    """2,000 invented rows whose flag separates the outcome: completely, or quasi-completely (one row breaks it)."""
    r = np.random.default_rng(5)
    flag = (r.random(2000) < 0.4).astype(float)
    y = flag.copy()
    if not complete:
        y[np.flatnonzero(flag == 0.0)[0]] = 1.0
    return y, {"intercept": np.ones(2000), "flag": flag, "z": r.normal(size=2000)}


def test_a_separated_binomial_fit_stops_as_separation() -> None:
    """LANE MU RULINGS 7 (2) (the combined verify's item 3): a binomial fit whose outcome a flag separates is no value
    (under the locked statsmodels it reads converged, a coefficient of tens and an SE of thousands): it stops as
    'separation', quasi-complete separation by its fitted risks at 0 or 1 on a whole group of the flag, complete
    separation also by statsmodels' warning; numpy's overflow recorded inside a binomial fit stops it; an ordinary
    frame does not stop; a fit that is not binomial reads no separation."""
    for complete in (False, True):
        y, columns = _separated_frame(complete)
        with pytest.raises(B.AnalysisError) as stopped:
            M._glm(y, columns, M.sm.families.Binomial())
        assert stopped.value.kind == "separation", complete
    y, columns = _separated_frame(False)
    result = M.sm.GLM(y, pd.DataFrame(columns), family=M.sm.families.Binomial()).fit()
    with pytest.raises(B.AnalysisError):
        M._separation(result, columns, "a GLM")
    r = np.random.default_rng(6)
    noisy = (r.random(2000) < 0.3 + 0.3 * columns["flag"]).astype(float)
    assert abs(float(M.sm.GLM(noisy, pd.DataFrame(columns), family=M.sm.families.Binomial()).fit().params["flag"])) < 5
    assert M._glm(noisy, columns, M.sm.families.Binomial()) is not None

    def overflowing() -> str:
        warnings.warn("overflow encountered in exp", RuntimeWarning, stacklevel=1)
        return "fitted"

    with pytest.raises(B.AnalysisError) as stopped:
        M._fit(overflowing, binomial=True)
    assert stopped.value.kind == "separation"
    assert M._fit(overflowing) == "fitted"


# THE SEPARATION STOP AT EACH OF ITS FIVE OTHER CALL SITES (the scoped verify 2's MINOR 2: one mutant removing it at the
# binomial GEE, the GAM, the prediction model, the calibration fits and MICE kept every case above green). Each case
# below reads its call site on a frame whose outcome a column separates, and is red on that site's mutant. The frames
# are test devices of 1,000 to 3,000 rows (no claim).


def _rewritten(text: str, column: str, value_of: "M.Callable[[dict[str, str]], str]", break_one: bool) -> str:
    """The table's text with one column of 0 and 1 written from each row's cells; ``break_one`` writes 1 on the first
    row that would read 0 (quasi-complete separation: one row breaks it)."""
    lines = text.splitlines()
    head = lines[0].split(",")
    at = head.index(column)
    broken = not break_one
    for n in range(1, len(lines)):
        cells = lines[n].split(",")
        value = value_of(dict(zip(head, cells)))
        if not broken and value == "0":
            value, broken = "1", True
        cells[at] = value
        lines[n] = ",".join(cells)
    assert broken, "no row to break"
    return "\n".join(lines) + "\n"


def test_the_binomial_gee_stops_where_the_arm_separates_the_outcome() -> None:
    """The binomial GEE's call site (LANE MU RULINGS 7 (2) names it): ST7 at 3,000 rows with the repeated yes-or-no
    outcome set to the arm (complete separation), and again with one row broken: `ST7/gee_bin` stops 'separation'
    through `run_panel`. Without the stop at its call site the first read 'ok', arm 61.13 with an SE of 0.108, and the
    second stopped as 'no convergence'."""
    text = U.text("ST7", 3000, 1)
    for break_one in (False, True):
        view = B.read(_rewritten(text, "controlled", lambda row: "1" if row["arm"] == "B" else "0", break_one), "ST7")
        panel = B.run_panel([B.Analysis("ST7/gee_bin", M.st7_gee_binary)], view)
        assert panel.status == {"ST7/gee_bin": "separation"}, (break_one, panel.status)


def test_the_gam_stops_where_a_linear_term_separates_the_outcome() -> None:
    """The GAM's call site: ST9 at 3,000 rows with the death outcome set to the treatment flag, and again with one row
    broken: `ST9/gam` (its knots fixed on that frame by `plan_st9`) stops 'separation' through `run_panel`. Without the
    stop at its call site the first still stops (statsmodels' own separation error, which `_fit` reads) and the second
    read 'ok' with its five estimates."""
    text = U.text("ST9", 3000, 1)
    for break_one in (False, True):
        view = B.read(_rewritten(text, "died", lambda row: row["treatment"], break_one), "ST9")
        [gam] = [a for a in M.plan_st9(view) if a.name == "ST9/gam"]
        panel = B.run_panel([gam], view)
        assert panel.status == {"ST9/gam": "separation"}, (break_one, panel.status)


def test_the_prediction_model_stops_where_an_indicator_separates_the_outcome() -> None:
    """The prediction model's call site (`_train`, its GLM, whose design adds its own intercept): the flag frame above,
    complete and with one row broken, stops 'separation'; an outcome the flag only shifts trains. Without the stop at
    its call site both separated frames returned a model."""
    rows = np.arange(2000)
    for complete in (True, False):
        y, columns = _separated_frame(complete)
        with pytest.raises(B.AnalysisError) as stopped:
            M._train({k: v for k, v in columns.items() if k != "intercept"}, y, rows, "glm", None)
        assert stopped.value.kind == "separation", complete
    _y, columns = _separated_frame(True)
    shifted = (np.random.default_rng(6).random(2000) < 0.3 + 0.3 * columns["flag"]).astype(float)
    assert M._train({k: v for k, v in columns.items() if k != "intercept"}, shifted, rows, "glm", None).kind == "glm"


def test_the_calibration_fits_stop_where_the_risks_separate_the_outcome() -> None:
    """The calibration fits' call site (`scores`): 2,000 invented outcomes whose risks separate them (0.8 on every
    event, 0.3 on every other row) stop 'separation'; risks that only rank them are scored. Without the stop at its call
    site the separated risks read a calibration slope of 24.7."""
    r = np.random.default_rng(7)
    y = (r.random(2000) < 0.4).astype(float)
    with pytest.raises(B.AnalysisError) as stopped:
        M.scores(np.where(y == 1.0, 0.8, 0.3), y)
    assert stopped.value.kind == "separation"
    ranked = np.clip(np.where(y == 1.0, 0.6, 0.4) + r.normal(scale=0.15, size=2000), 0.05, 0.95)
    assert 0.5 < M.scores(ranked, y)["auc"] < 1.0


def test_mice_stops_where_age_separates_the_outcome() -> None:
    """MICE's call site (its binomial model, read by its warnings): ST11 at 1,000 rows with the outcome set to 'aged 60
    or more': numpy's overflow warning is recorded inside the fit (`_fit(..., binomial=True)`), and `st11_mice` stops
    'separation'. Without the stop at its call site it read the age term at 538, SE 1,162,352."""
    text = _rewritten(U.text("ST11", 1000, 1), "outcome",
                      lambda row: "1" if row["age"] and float(row["age"]) >= 60.0 else "0", False)
    with pytest.raises(B.AnalysisError) as stopped:
        M.st11_mice(B.read(text, "ST11"))
    assert stopped.value.kind == "separation"


def test_a_start_stop_cox_model_counts_a_person_once_at_a_boundary() -> None:
    """LANE MU RULINGS 6 (3) (Codex's review, its item 3): a row is at risk on (start, stop], so a person whose next row
    starts on the day another person's event falls is in that risk set once. Four rows, worked by hand: A unexposed on
    (0, 1] and exposed on (1, 3]; B unexposed, its event on day 1; C exposed on (0, 3]. At a coefficient of log 2 the
    risk set of day 1 is A's first row, B and C: 1 + 1 + 2, so the partial log likelihood is -log 4 (statsmodels' entry
    as it stands, which counts A's second row too, reads -log 6)."""
    stop, start = np.asarray([1.0, 3.0, 1.0, 3.0]), np.asarray([0.0, 1.0, 0.0, 0.0])
    status, x = np.asarray([0.0, 0.0, 1.0, 0.0]), {"x": np.asarray([0.0, 1.0, 0.0, 1.0])}
    found = float(M.cox_start_stop(stop, start, status, x).loglike(np.asarray([math.log(2.0)])))
    assert abs(found + math.log(4.0)) < 1e-12, found


def test_a_start_stop_row_with_a_time_below_0_is_one_failed_analysis() -> None:
    """The scoped verify 2's MINOR 1: ST8 at 3,000 rows (a test device) with one row's start moved from day 0 to day -1
    (its stop over 30 days; a value outside the column's range, as a twin could write one). PHReg's constructor refuses
    it ('entry time must be non-negative'); built inside `_fit`, both start-stop Cox models read 'fit error' through
    `run_panel` and the panel goes on (the naive Cox model on the persons reads 'ok'). Built outside it, the ValueError
    left the panel and ended the table's whole run."""
    lines = U.text("ST8", 3000, 1).splitlines()
    head = lines[0].split(",")
    at_start, at_stop = head.index("start_day"), head.index("stop_day")
    moved = 0
    for n in range(1, len(lines)):
        cells = lines[n].split(",")
        if cells[at_start] == "0" and int(cells[at_stop]) > 30:
            cells[at_start] = "-1"
            lines[n], moved = ",".join(cells), n
            break
    assert moved, "no row starts on day 0"
    plan = [B.Analysis("ST8/cox_tv", M.st8_cox_tv), B.Analysis("ST8/cox_comp", M.st8_cox_competing),
            B.Analysis("ST8/cox_naive", M.st8_cox_naive)]
    panel = B.run_panel(plan, B.read("\n".join(lines) + "\n", "one start below 0"))
    assert panel.status == {"ST8/cox_tv": "fit error", "ST8/cox_comp": "fit error", "ST8/cox_naive": "ok"}, panel.status


def test_a_cox_terms_cell_counts_its_events_at_the_call_site() -> None:
    """The combined verify's item 2 (e): the start-stop Cox model's terms carry E0b's event-counted cell (the events and
    non-events in each group of an indicator), not the model's rows: a constructed frame whose treated group holds 4
    events among 60 rows reads a treated cell of 4."""
    r = random.Random(43)
    lines = ["subject,centre,stage,age,gender,enrolled_on,start_day,stop_day,treated,egfr_band,status"]
    events_treated = 0
    for p in range(400):
        treated = p < 60
        event = 1 if (treated and events_treated < 4) or (not treated and r.random() < 0.3) else 0
        events_treated += int(treated and event == 1)
        lines += [f"P{p:04d},A,{r.choice(['I', 'II', 'III'])},{r.randint(40, 80)},male,2015-01-01,0,"
                  f"{r.randint(30, 900)},{int(treated)},{r.choice(['low', 'normal'])},{event}"]
    found = {e.key: e for e in M.st8_cox_tv(B.read("\n".join(lines) + "\n", "constructed"))}
    assert found["ST8/cox_tv:treated"].support == 4, found["ST8/cox_tv:treated"].support


def test_a_cox_model_with_no_event_in_a_group_stops() -> None:
    """ST8's rows with every event moved onto a treated row: the treated term's untreated group holds no event, and the
    start-stop Cox model stops ('separation') instead of reading a coefficient of about 25 with an SE of thousands."""
    text = U.text("ST8", 3000, 7)
    header, *rows = text.splitlines()
    cells = [row.split(",") for row in rows]
    at_treated, at_status = header.split(",").index("treated"), header.split(",").index("status")
    for row in cells:
        if row[at_treated] == "0":
            row[at_status] = "0"
    view = B.read(header + "\n" + "".join(",".join(row) + "\n" for row in cells), "events on treated rows")
    panel = B.run_panel([B.Analysis("ST8/cox_tv", M.st8_cox_tv)], view)
    assert panel.status["ST8/cox_tv"] == "separation", panel.status
    whole = B.run_panel([B.Analysis("ST8/cox_tv", M.st8_cox_tv)], B.read(text, "as drawn"))
    assert whole.status["ST8/cox_tv"] == "ok"


def test_the_booster_runs_on_one_openmp_thread(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every booster fit and prediction holds OpenMP to one thread (skeptic 1's item 2: one a core by default)."""
    seen: "list[list[int]]" = []

    def counted(method: str) -> "M.Callable[..., object]":
        original = getattr(M.HistGradientBoostingClassifier, method)

        def run(self: object, *args: object, **kwargs: object) -> object:
            seen.append([p["num_threads"] for p in threadpoolctl.threadpool_info() if p["user_api"] == "openmp"])
            return original(self, *args, **kwargs)
        return run

    monkeypatch.setattr(M.HistGradientBoostingClassifier, "fit", counted("fit"))
    monkeypatch.setattr(M.HistGradientBoostingClassifier, "predict_proba", counted("predict_proba"))
    r = np.random.default_rng(3)
    x = r.normal(size=(400, 3))
    y = (x[:, 0] + r.normal(size=400) > 0).astype(float)
    columns = {"a": x[:, 0], "b": x[:, 1], "c": x[:, 2]}
    rows = np.arange(400)
    trained = M._train(columns, y, rows, "hgb", None)
    M._predict(trained, columns, y, rows, None)
    assert len(seen) == 2 and all(threads and set(threads) == {1} for threads in seen), seen


def test_a_persons_rows_land_in_one_half() -> None:
    """GENERATED: 2,000 small tables of persons on 1 to 9 rows each, ids written in any order: every row of a person shares
    the person's group, so a person's rows are in one half of each of the four splits."""
    r = random.Random(17)
    for case in range(2000):
        ids = []
        for person in range(r.randint(2, 30)):
            ids += [f"{r.choice(['P', 'S', 'id-'])}{r.randint(0, 99999):05d}-{person}"] * r.randint(1, 9)
        r.shuffle(ids)
        view = B.View(pd.DataFrame({"subject": ids}), "case")
        g = M.groups(view, "ST7", case)
        seen: "dict[str, int]" = {}
        for i, s in enumerate(ids):
            assert seen.setdefault(s, g[i]) == g[i], (case, s)
    plain = B.View(pd.DataFrame({"age": list(range(64))}), "rows")
    assert len(set(M.groups(plain, "ST9", 1))) > 1


def test_an_estimate_under_the_support_rule_is_not_scored() -> None:
    """GENERATED: 3,000 panels whose cells hold 0 to 40 rows on the real table and 0 to 20 in each half: an estimate is
    scored exactly where its real cell holds 22 and every half's 11 (E0b's rule, reused unchanged)."""
    r = random.Random(23)
    view = B.View(pd.DataFrame({"x": list(range(32))}), "real")
    g = [i % 16 for i in range(32)]
    for case in range(3000):
        full = r.randint(0, 40)
        halves = {}

        def analysis(v: B.View) -> "list[B.Estimate]":
            if v.rows == 32:
                return [B.Estimate("k", "F11", 1.0, 0.1, full)]
            cell = halves.setdefault(v.name, r.randint(0, 20))
            return [B.Estimate("k", "F11", 1.0 + 0.01 * cell, 0.1, cell)]

        y = B.yardstick([B.Analysis("a", analysis)], view, g)
        scored = "k" in y.h
        assert scored == (full >= B.SUPPORT and min(halves.values()) >= B.HALF_SUPPORT), (case, full, halves)


def test_a_terms_cell_is_e0bs() -> None:
    """GENERATED: 2,000 designs of 5 to 60 rows, indicators (all-zero and all-one ones among them) and other columns, with a
    two-valued outcome, a continuous one and none: `cell` gives each term the cell `analyst_battery.supports` gives it (an
    indicator of no 1 a cell of 0; skeptic 1's item 6 (b))."""
    r = random.Random(29)
    for case in range(2000):
        n = r.randint(5, 60)
        kind = r.choice(["zero", "one", "flag", "number"])
        x = ([0.0] * n if kind == "zero" else [1.0] * n if kind == "one" else
             [float(r.random() < r.random()) for _ in range(n)] if kind == "flag" else [r.gauss(0, 1) for _ in range(n)])
        outcome = r.choice(["binary", "number", "none"])
        y = ([float(r.random() < 0.4) for _ in range(n)] if outcome == "binary" else
             [r.gauss(0, 1) for _ in range(n)] if outcome == "number" else None)
        design = K.Design({"x": x}, [("x", B.col("x"))])
        expected = B.supports(design, y if outcome == "binary" else None, outcome == "binary")["x"]
        found = M.cell(np.asarray(x), None if y is None else np.asarray(y))
        assert found == expected, (case, kind, outcome, found, expected)


def _run(shares: "dict[str, float]", n: int = 40, families: "tuple[str, ...]" = ("F11", "F12")) -> M.Run:
    """A synthetic run: n estimates of each family, each side inside on the given share of them (a family's own share
    where ``shares`` names `side:family`)."""
    real = B.Panel({}, {})
    sides = {}
    for name in {k.split(":")[0] for k in shares}:
        compared = []
        for family in families:
            share = shares.get(f"{name}:{family}", shares.get(name, 0.0))
            for i in range(n):
                compared += [B.Compared(f"{family}:{i}", family, (), 1.0, 1.0, 0.1, i < share * n, None, None, True)]
        sides[name] = [M.Side(compared, [], B.Panel({}, {}), {})]
    return M.Run("ST9", 20000, 1, "S", B.Yardstick(real, {}, set()), {}, sides, 0.0, 0.0)


def test_swapped_controls_void_a_run() -> None:
    """The controls hold where the replicate is a fresh sample's and the shuffle stands under it; swapped, the run is void;
    a family whose shuffle meets the replicate voids the run even where the pooled shuffle stands far under it."""
    good = M.controls([_run({"twin": 0.6, "replicate": 0.8, "shuffled": 0.3})])
    assert good["hold"]
    swapped = M.controls([_run({"twin": 0.6, "replicate": 0.3, "shuffled": 0.8})])
    assert not swapped["hold"]
    near = M.controls([_run({"twin": 0.6, "replicate": 0.8, "shuffled": 0.7})])
    assert not near["hold"] and set(near["void"]) == {"F11", "F12"}
    clear = M.controls([_run({"twin": 0.6, "replicate": 0.8, "shuffled:F11": 0.2, "shuffled:F12": 0.6})])
    assert clear["shuffle_gap"] >= 30.0 and clear["void"] == ["F12"] and not clear["hold"], clear


def test_an_absolute_bar_the_replicate_fails_or_the_shuffle_meets_is_void() -> None:
    """An absolute bar is judged only where the replicate meets it and the shuffled twin does not."""
    held = M.bar("slope 0.85 to 1.15", 1.3, 1.0, lambda x: 0.85 <= x <= 1.15, 0.2)
    assert held["void"] is False and held["twin"] is False and held["replicate"] is True and held["read"] is True
    void = M.bar("slope 0.85 to 1.15", 1.3, 1.4, lambda x: 0.85 <= x <= 1.15)
    assert void["void"] and not void["replicate"] and void["void_reason"] == "the replicate fails it"
    nan = M.bar("slope", 1.0, math.nan, lambda x: 0.85 <= x <= 1.15)
    assert nan["void"]
    shuffled = M.bar("SMD under 0.1", 0.0, 0.01, lambda x: x < 0.1, 0.0002)
    assert shuffled["void"] and shuffled["void_reason"] == "the shuffle meets it"


def _curvature_run(inside: "dict[str, float]") -> M.Run:
    """A synthetic ST9 run of eight curvature terms (and four other estimates), each side inside on the given share."""
    sides = {}
    for name, share in inside.items():
        compared = [B.Compared(f"ST9/quad:c{i}", "F15", ("curvature",), 1.0, 1.0 if i < share * 8 else 0.3, 0.5,
                               i < share * 8, None, None, True) for i in range(8)]
        compared += [B.Compared(f"ST9/x:{i}", "F13", (), 1.0, 1.0, 0.1, True, None, None, True) for i in range(4)]
        sides[name] = [M.Side(compared, [], B.Panel({}, {}), {})]
    return M.Run("ST9", 20000, 1, "S", B.Yardstick(B.Panel({}, {}), {}, set()), {}, sides, 0.0, 0.0)


def _curvature_bar(run: M.Run) -> "dict[str, object]":
    return next(b for b in M.measures([run], "_20k")["bars"] if b["bar"] == "curvature retained")


def test_the_curvature_bar_is_void_where_the_flattened_replicate_meets_it_or_reads_nothing() -> None:
    """`measures`: judged where the flattened replicate fails the bar the replicate meets; void where the flattened
    replicate meets it, and void where it has no reading (skeptic 1's item 6 (a))."""
    judged = _curvature_bar(_curvature_run({"twin": 0.5, "replicate": 0.875, "shuffled": 0.0, "flattened": 0.125}))
    assert judged["void"] is False and judged["flattened_fails"] is True and judged["twin"] is True, judged
    met = _curvature_bar(_curvature_run({"twin": 0.5, "replicate": 0.875, "shuffled": 0.0, "flattened": 0.75}))
    assert met["void"] is True and met["flattened_fails"] is False, met
    absent = _curvature_bar(_curvature_run({"twin": 0.5, "replicate": 0.875, "shuffled": 0.0}))
    assert absent["void"] is True and absent["flattened_fails"] is False, absent


@pytest.mark.parametrize("table,analyses", (("ST9", ("ST9/quad", "ST9/sbp", "ST9/spline")), ("ST7", ("ST7/lmm",))))
def test_the_flattened_replicate_fails_the_curvature_bar_and_the_replicate_passes(table: str,
                                                                                  analyses: "tuple[str, ...]") -> None:
    """At 20,000 rows, the curvature analyses only (no product), the replicate and the flattened replicate at the three
    twin seeds of the 20,000-row tier: every term's ratio to the real one stays above 0.8 on the replicate and falls under
    0.8 on the flattened replicate (each curve halved), so each curve the generator halves is read (ST9's four, ST7's bend
    of the random-slope model); where a table holds several curvature terms (ST9), the replicate also keeps them inside
    their yardsticks (the median share at least `CURVATURE_SHARE`) and the flattened replicate does not. A share of one
    term is no measure for a gate: on ST7 at table seed 1 its yardstick from four splits reads 0.0104 against a standard
    error of 0.0197, and the replicate's three bends (-0.297, -0.315, -0.300 against the real -0.278) fall outside it."""
    real = B.read(U.text(table, TRUTH_ROWS, 1), "real")
    plan = [a for a in M.PLANS[table](real) if a.name in analyses]
    y = B.yardstick(plan, real, M.groups(real, table, 1))
    sides: "dict[str, list[M.Side]]" = {"replicate": [], "flattened": []}
    for name, flat in (("replicate", False), ("flattened", True)):
        for k in (0, 1, 2):
            panel = B.run_panel(plan, B.read(U.text(table, TRUTH_ROWS, M.replicate_seed(1, k), flat=flat), name))
            sides[name] += [M.Side(B.compare(y, panel), B.stops(y, panel), panel, {})]
    run = M.Run(table, real.rows, 1, "S", y, {}, sides, 0.0, 0.0)
    terms = sorted(c.key for c in sides["replicate"][0].compared if "curvature" in c.tags)
    assert len(terms) == (4 if table == "ST9" else 1), terms
    if len(terms) > 1:
        inside_r = M.curvature([run], "replicate")["inside"]
        inside_f = M.curvature([run], "flattened")["inside"]
        assert inside_r >= M.CURVATURE_SHARE > inside_f, (inside_r, inside_f)  # type: ignore[operator]
    for key in terms:
        real_value = y.real.estimates[key].value
        ratio = {name: sorted(s.panel.estimates[key].value / real_value for s in sides[name])[1] for name in sides}
        assert ratio["flattened"] < 0.8 < ratio["replicate"], (key, ratio)


def test_the_values_hold_no_infinity() -> None:
    """`finite` (the driver's values): NaN and both infinities become None at any depth, in lists, tuples and dictionaries
    alike (skeptic 1's item 7: a variance ratio of a twin whose SD is 0 reads infinity); the driver's night size is the
    battery's, read from its source (the night's parent never imports the battery)."""
    value = {"varcomp_20k": [math.inf, 0.5, (math.nan, -math.inf)], "deep": {"x": {"y": [1.0, math.inf]}}, "n": 3}
    found = M.finite(value)
    assert found == {"varcomp_20k": [None, 0.5, [None, None]], "deep": {"x": {"y": [1.0, None]}}, "n": 3}
    assert "Infinity" not in json.dumps(found) and "NaN" not in json.dumps(found)
    source = DRIVER.read_text(encoding="utf-8")
    night = [node.value for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == "NIGHT_ROWS" for t in node.targets)]
    assert len(night) == 1 and ast.literal_eval(night[0]) == M.TIERS["night"]["rows"]
    assert tuple(twin_routes.ROUTES) == ("S", "C", "U", "P")


def _driver(path: pathlib.Path = DRIVER) -> "object":
    """A driver module, loaded from its file with this process's import path and environment restored after."""
    saved_path, saved_omp = list(sys.path), os.environ.get("OMP_NUM_THREADS")
    try:
        spec = importlib.util.spec_from_file_location(f"{path.stem}_case", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path[:] = saved_path
        if saved_omp is None:
            os.environ.pop("OMP_NUM_THREADS", None)
        else:
            os.environ["OMP_NUM_THREADS"] = saved_omp


def test_the_driver_names_its_libraries_its_heads_and_its_cpu() -> None:
    """The kept-run digest reads the interpreter's and the fitting libraries' versions (the statistics check's item 13);
    the drift names the ledger stamp's commit (item 14: none here) and the children record CPU seconds (item 15); the
    night's truth step calls the battery's generated truth checks for every table; the driver's values hold no
    infinity."""
    driver = _driver()
    said = driver.versions()  # type: ignore[attr-defined]
    assert said.startswith(sys.version.split()[0]) and all(f"{name} " in said for name in driver.LIBRARIES)  # type: ignore
    digest = driver.panel_code_digest()  # type: ignore[attr-defined]
    original = driver.versions  # type: ignore[attr-defined]
    driver.versions = lambda: original() + "; another numpy"  # type: ignore[attr-defined]
    assert driver.panel_code_digest() != digest  # type: ignore[attr-defined]
    assert driver._finite({"x": [math.inf]}) == {"x": [None]}  # type: ignore[attr-defined]
    calls = {node.func.attr for node in ast.walk(ast.parse(DRIVER.read_text(encoding="utf-8")))
             if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)}
    assert {"generated_truth_checks", "owner_four_unrobust"} <= calls


def test_the_drivers_cpu_and_peak_are_what_the_platform_supports(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review, its item 6 (LANE MU RULINGS 6 (5)): where `resource` exists (macOS, Linux) the CPU seconds and the
    peak are numbers; where it does not (Windows) both are None, the branch read here on a platform that has it by
    hiding the module."""
    driver = _driver()
    has = importlib.util.find_spec("resource") is not None
    for read in (driver.cpu_seconds, driver.peak_mb):  # type: ignore[attr-defined]
        assert isinstance(read(), float) if has else read() is None
    monkeypatch.setitem(sys.modules, "resource", None)
    assert driver.cpu_seconds() is None and driver.peak_mb() is None  # type: ignore[attr-defined]


def _ledger_file(folder: pathlib.Path, entries: "list[dict]") -> pathlib.Path:
    path = folder / "ledger.json"
    path.write_text(json.dumps({"entries": entries}), encoding="utf-8", newline="\n")
    return path


def test_the_drift_reads_the_ledger_it_is_handed(tmp_path: pathlib.Path) -> None:
    """Codex's review, its item 7 (LANE MU RULINGS 6 (5)): the drift's 20,000-row shares come from the ledger's K-BC-14
    stamp, read on an empty ledger and a populated one handed in as fixtures (never the repository's own, whose first
    stamp is due)."""
    driver = _driver()
    assert driver.ledger_stamp_20k(_ledger_file(tmp_path, [])) == ({}, "")  # type: ignore[attr-defined]
    fam = {"F11": [0.4, 0.77, 0.3, 40]}
    entry = {"id": "K-BC-14", "value_at": {"commit": "0123456", "date": "2026-11-18", "value": {"fam_20k": fam}}}
    assert driver.ledger_stamp_20k(_ledger_file(tmp_path, [entry])) == (fam, "0123456 (2026-11-18)")  # type: ignore
    assert driver.ledger_stamp_20k(tmp_path / "absent.json") == ({}, "")  # type: ignore[attr-defined]


KPI_RUN = DRIVER.with_name("kpi_run.py")


def _both_tiers() -> "dict[str, object]":
    """A K-BC-14 value of both tiers that meets its own bound."""
    value: "dict[str, object]" = {}
    for size in ("_20k", "_200k"):
        value.update({f"controls_hold{size}": True, f"supported_estimates{size}": 300,
                      f"pooled_points_below_replicate{size}": 20.0, f"strong_sign_flips{size}": 4, f"stops{size}": 1})
    return value


def test_an_ordinary_slow_run_judges_k_bc_14_on_the_tier_it_produced(monkeypatch: pytest.MonkeyPatch,
                                                                      tmp_path: pathlib.Path) -> None:
    """Codex's review, its item 8 (LANE MU RULINGS 6 (6), tier-aware judging): a stamp holding both tiers, its entry
    naming them; the ordinary runner (`kpi_run.measure`, the driver's KPI line read as `kpi_run.py --slow` reads it)
    judges the `--kpi` line's 20,000-row keys and never rejects the 200,000-row keys as not measured; a 20,000-row key the
    line leaves out is a miss; a line that names no tiers is judged on every key."""
    runner = _driver(KPI_RUN)
    value = _both_tiers()
    entry = M.ledger_entry(value, "0123456", "2026-11-18", "a case")
    assert set(entry["tiers"]) == {"_20k", "_200k"} and entry["driver"] in entry["tiers"].values()
    ledger = dict(kpi_rules.load_ledger(), entries=[entry])
    produced = {k: v for k, v in value.items() if k.endswith("_20k")}

    def judged(record: "dict[str, object]") -> "dict[str, object]":
        line = "KPI " + json.dumps(record, sort_keys=True)
        monkeypatch.setattr(runner.subprocess, "run",  # type: ignore[attr-defined]
                            lambda *a, **k: subprocess.CompletedProcess(a[0], 0, stdout=line + "\n", stderr=""))
        [row] = runner.measure([entry], ledger, True, tmp_path)  # type: ignore[attr-defined]
        return row

    row = judged({"id": "K-BC-14", "value": produced, "detail": "", "tiers": ["_20k"]})
    assert row["pass"] and row["verdict"] == kpi_rules.OPEN_HELD and "not measured" not in row["message"], row
    assert "_200k keys are judged on their own runs" in row["message"], row["message"]
    short = {k: v for k, v in produced.items() if k != "stops_20k"}
    row = judged({"id": "K-BC-14", "value": short, "detail": "", "tiers": ["_20k"]})
    assert not row["pass"] and "stops_20k: not measured" in row["message"], row
    row = judged({"id": "K-BC-14", "value": produced, "detail": ""})
    assert not row["pass"] and "stops_200k: not measured" in row["message"], row
    malformed = dict(entry, tiers={"20k": "a command"})
    assert any("tiers must map" in p for p in kpi_rules.integrity_problems({**ledger, "entries": [malformed]}))
    assert not any("tier" in p for p in kpi_rules.integrity_problems(ledger)), kpi_rules.integrity_problems(ledger)
    # The driver's own KPI line names the tier its run produced.
    sent: "list[dict[str, object]]" = []
    monkeypatch.setattr(kpi_rules, "emit", lambda *_a, **k: sent.append(k))
    sides = {name: [M.Side([], [], B.Panel({}, {}), {})] for name in ("twin", "replicate", "shuffled")}
    _driver().emit([_measured("ST10", sides)], "_20k", 1.0, {})  # type: ignore[attr-defined]
    assert sent and sent[-1].get("tiers") == ["_20k"], sent


# THE THREE OTHER CHECKS OF AN ENTRY'S TIERS in `kpi_rules.integrity_problems` (the scoped verify 2's MINOR 2: the
# malformed field's is read above; these three were read by no case). Each names its fault on K-BC-14's own entry.


def _tier_problems(entry: "dict[str, object]") -> "list[str]":
    """The integrity problems that name a tier, of a ledger holding this entry alone."""
    ledger = dict(kpi_rules.load_ledger(), entries=[entry])
    return [p for p in kpi_rules.integrity_problems(ledger) if "tier" in p]


def _tiered_entry() -> "dict[str, object]":
    """K-BC-14's entry from a stamp of both tiers, as the driver writes it (its tiers named, each with its command)."""
    entry = M.ledger_entry(_both_tiers(), "0123456", "2026-11-18", "a case")
    assert _tier_problems(entry) == [], _tier_problems(entry)
    return entry


def test_a_bounded_key_in_no_tier_is_an_integrity_fault() -> None:
    """A bounded key whose suffix is no tier's would be left out of every tier's judging: it is named."""
    entry = _tiered_entry()
    loose = dict(entry, expected=dict(entry["expected"], stops_5k=0))  # type: ignore[call-overload]
    assert _tier_problems(loose) == ["K-BC-14: the bounded keys ['stops_5k'] belong to no tier it names"]


def test_a_tier_command_that_is_not_a_driver_is_an_integrity_fault() -> None:
    """A tier's command naming a script outside tools/measurements/ (one that exists), and one there that names no file,
    are each named: each half of the check has its own command."""
    entry = _tiered_entry()
    for command in ("tools/ci/shards.py --night", "tools/measurements/kpi_absent.py --night"):
        moved = dict(entry, tiers=dict(entry["tiers"], _200k=command))  # type: ignore[call-overload]
        assert _tier_problems(moved) == [f"K-BC-14: the tier command {command} is not a driver under tools/measurements/"]


def test_a_driver_that_measures_none_of_the_tiers_is_an_integrity_fault() -> None:
    """The registered driver's command is none of the tiers' commands (the same script with another flag, so the
    driver's own checks pass): it is named."""
    other = "tools/measurements/kpi_model_utility.py --preview"
    problems = _tier_problems(dict(_tiered_entry(), driver=other))
    assert problems == [f"K-BC-14: its driver {other} measures none of its tiers"], problems


def test_a_kept_run_is_read_back_only_for_the_routes_it_was_asked_for(monkeypatch: pytest.MonkeyPatch,
                                                                      tmp_path: pathlib.Path) -> None:
    """Codex's review, its item 9 (LANE MU RULINGS 6 (6)): a `--kpi` run kept under SYNTHTWIN_MODEL_RUNS is read back by a
    later `--kpi`, never by a `--preview` that asks for route C beside it (it runs again and keeps its own); the digest of
    the code a kept run came from reads the modules the battery imports only on first need (route P's `fixtures`)."""
    driver = _driver()
    made: "list[tuple[str, ...]]" = []

    def run_table(table: str, rows: int, seed: int, twins: "tuple[int, ...]", folder: pathlib.Path, route: str = "S",
                  extra_routes: "tuple[str, ...]" = (), **_kw: object) -> M.Run:
        made.append(tuple(extra_routes))
        return M.Run(table, rows, seed, route, B.Yardstick(B.Panel({}, {}), {}, set()), {}, {}, 0.0, 0.0)

    monkeypatch.setattr(M, "run_table", run_table)
    monkeypatch.setenv("SYNTHTWIN_MODEL_RUNS", str(tmp_path / "kept"))
    for extra in (("P",), ("P",), ("C", "P"), ("C", "P")):
        driver.run_tier("slow", tmp_path / "runs", ["ST10"], "S", extra, None, (1,))  # type: ignore[attr-defined]
    assert made == [("P",), ("C", "P")], made
    assert sorted(p.name for p in (tmp_path / "kept").iterdir()) == ["ST10-1-S+C+P.json", "ST10-1-S+P.json"]
    # A record whose own routes are not the ones asked for is never read back, whatever file it stands in.
    kept = tmp_path / "kept" / "ST10-1-S+C+P.json"
    record = json.loads(kept.read_text(encoding="utf-8"))
    kept.write_text(json.dumps(dict(record, routes=["S", "P"])), encoding="utf-8", newline="\n")
    driver.run_tier("slow", tmp_path / "runs", ["ST10"], "S", ("C", "P"), None, (1,))  # type: ignore[attr-defined]
    assert made == [("P",), ("C", "P"), ("C", "P")], made
    monkeypatch.delitem(sys.modules, "fixtures", raising=False)
    assert (pathlib.Path(B.__file__).with_name("fixtures.py").resolve()
            in driver.panel_code_files())  # type: ignore[attr-defined]


def test_a_labelled_routes_child_is_run_without_controls_through_the_driver(tmp_path: pathlib.Path,
                                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 2 (d), through the driver: the night's route P child is started with `--no-controls`
    (`layer_runs`) and the driver's `--one` hands `run_table` controls=False exactly where `--no-controls` is given (the
    table runs recorded here, no product run)."""
    driver = _driver()
    asked: "list[object]" = []

    def run_table(table: str, rows: int, seed: int, twins: "tuple[int, ...]", folder: pathlib.Path, route: str = "S",
                  extra_routes: "tuple[str, ...]" = (), flattened: bool = True, controls: bool = True) -> M.Run:
        asked.append(controls)
        return M.Run(table, rows, seed, route, B.Yardstick(B.Panel({}, {}), {}, set()), {}, {}, 0.0, 0.0)

    monkeypatch.setattr(M, "run_table", run_table)
    monkeypatch.setattr(driver.kpi_rules, "guard_this_tree", lambda: "")  # type: ignore[attr-defined]
    record = tmp_path / "record.json"
    for flag, wanted in ((["--no-controls"], False), ([], True)):
        assert driver.main(["--one", "ST10", "--rows", "3000", "--route", "P", "--json", str(record),  # type: ignore
                            "--out", str(tmp_path)] + flag) == 0
        assert asked[-1] is wanted, (flag, asked)
    started: "list[list[str]]" = []
    monkeypatch.setattr(driver, "child", lambda arguments, _record: started.append(arguments))
    driver.layer_runs("a tree", ["ST7", "ST9"], 20000, (1,), (0,), tmp_path)  # type: ignore[attr-defined]
    assert len(started) == 1 and "--no-controls" in started[0] and started[0][started[0].index("--route") + 1] == "P"


def test_e0bs_first_stamp_carries_route_us_reading_beside_route_s() -> None:
    """`kpi_analyst_battery.py --kpi --beside-unswitched` (LANE MU RULINGS 3 (2) item 6): each KPI's detail carries route
    U's reading of its keys, the stamped value stays route S's."""
    driver = _driver(E0B_DRIVER)
    values = {"K-BC-01": {"pooled_points_below_replicate_20k": 30.0, "_detail": "route S"}}
    driver.with_route_u(values, {"K-BC-01": {"pooled_points_below_replicate_20k": 41.5, "_detail": "x"}})  # type: ignore
    assert values["K-BC-01"]["pooled_points_below_replicate_20k"] == 30.0
    assert values["K-BC-01"]["_detail"].endswith('unswitched) on this head: {"pooled_points_below_replicate_20k": 41.5}')


def test_a_stamp_is_refused_where_the_owners_four_are_not_measured() -> None:
    """An analysis of F11 to F14 that is not robust on a real table (it stopped on the table or a half) is named and the
    driver exits with no KPI line (the statistics check's item 2)."""
    robust = {"ST7/lmm", "ST7/ri", "ST7/gee_exch", "ST7/gee_ar1", "ST7/gee_bin", "ST7/structure"}
    held = M.Run("ST7", 20000, 1, "S", B.Yardstick(B.Panel({}, {}), {}, robust), {"ST7/tstr_glm:auc": (0.7, 0.01),
                                                                                   "ST7/tstr_hgb:auc": (0.7, 0.01)},
                 {}, 0.0, 0.0)
    assert M.owner_four_unrobust([held]) == []
    broken = M.Run("ST7", 20000, 1, "S", B.Yardstick(B.Panel({}, {"ST7/lmm": "no convergence"}), {},
                                                     robust - {"ST7/lmm"}), held.tstr_yard, {}, 0.0, 0.0)
    assert [n.split()[1] for n in M.owner_four_unrobust([broken])] == ["ST7/lmm"]
    with pytest.raises(SystemExit):
        _driver().robust_or_exit([broken])  # type: ignore[attr-defined]


def _term(key: str, real: float, h: float, value: float) -> B.Compared:
    return B.Compared(key, "F15", ("curvature",), real, value, h, abs(value - real) <= h, None, None, True)


def test_a_curvature_ratio_is_read_only_where_its_noise_is_small() -> None:
    """At 200,000 rows a term's ratio is read where h / (sqrt(2) |real|) is at most 0.1; a noisier term is read inside its
    yardstick instead (the statistics check's item 3)."""
    assert math.isclose(M.ratio_noise(0.2, 1.0, 20000, 200000), 0.2 / math.sqrt(2.0) * math.sqrt(0.1))
    sides = {"twin": [M.Side([_term("ST9/a", 1.0, 0.05, 0.9), _term("ST9/b", 1.0, 0.9, 0.2)], [], B.Panel({}, {}), {})]}
    run = M.Run("ST9", 200000, 1, "S", B.Yardstick(B.Panel({}, {}), {}, set()), {}, sides, 0.0, 0.0)
    found = M.curvature([run], "twin")
    assert found["readable"] == ["ST9-1-ST9/a"] and math.isclose(found["ratio_min"], 0.9), found  # type: ignore
    assert M.curvature_value(found, "_200k") == 1.0 and found["unread_inside"] == 1.0
    sides["twin"][0].compared[0] = _term("ST9/a", 1.0, 0.05, 0.7)
    assert M.curvature_value(M.curvature([run], "twin"), "_200k") == 0.0


def _measured(table: str, sides: "dict[str, list[M.Side]]", real: "dict[str, B.Estimate] | None" = None,
              h: "dict[str, float] | None" = None, tstr: "dict[str, tuple[float, float]] | None" = None) -> M.Run:
    return M.Run(table, 20000, 1, "S", B.Yardstick(B.Panel(real or {}, {}), h or {}, set()), tstr or {}, sides, 0.0, 0.0)


def test_the_bars_read_what_the_rulings_name() -> None:
    """Table 1's bar reads the worst table (the median over a run's twin seeds, then the maximum over the runs); each
    prediction bar reads its run's own TRTR; the SE-ratio bar reads tables of several rows a person only; an approximate
    estimate enters no strong flip, decision or SE ratio; and every bar the rulings name is in the list."""
    def side(extra: "dict[str, float]", compared: "list[B.Compared] | None" = None,
             panel: "dict[str, B.Estimate] | None" = None) -> M.Side:
        return M.Side(compared or [], [], B.Panel(panel or {}, {}), extra)

    runs = [_measured("ST9", {"twin": [side({"t1_smd_max": 0.05})] * 3}),
            _measured("ST10", {"twin": [side({"t1_smd_max": x}) for x in (0.2, 0.3, 0.9)]})]
    assert M._table_max(runs, "twin", "t1_smd_max") == 0.3
    tstr = [_measured("ST9", {"twin": [side({"ST9/tstr_glm:auc": 0.70})]}, tstr={"ST9/tstr_glm:auc": (0.71, 0.01)}),
            _measured("ST9", {"twin": [side({"ST9/tstr_glm:auc": 0.80})]}, tstr={"ST9/tstr_glm:auc": (0.80, 0.01)})]
    assert math.isclose(M._tstr(tstr, "twin", "ST9/tstr_glm", "auc"), -0.005)
    real = {"k": B.Estimate("k", "F11", 1.0, 0.1, 500), "v": B.Estimate("v", "F24", 1.0, 0.01, 500, (M.APPROXIMATE,))}
    flipped = [B.Compared("v", "F24", (M.APPROXIMATE,), 1.0, -1.0, 0.1, False, True, True, False)]
    got = {"k": B.Estimate("k", "F11", 1.0, 0.1, 500), "v": B.Estimate("v", "F24", -1.0, 0.05, 500, (M.APPROXIMATE,))}
    for table in ("ST7", "ST9"):
        run = _measured(table, {"twin": [side({}, flipped, got)]}, real, {"k": 0.1, "v": 0.1})
        assert M.strong_flips(run.sides["twin"][0], run) == 0.0
        assert all(x != x for x in M.decisions([run], "twin")), M.decisions([run], "twin")
        share = M.se_ratio_share([run], "twin")
        assert (share == 1.0) if table == "ST7" else (share != share), (table, share)
    names = {b["bar"] for b in M.measures([_curvature_run({"twin": 0.5, "replicate": 0.875, "shuffled": 0.0})],
                                          "_20k")["bars"]}
    for wanted in ("max abs SMD before weighting within 0.1 of the real's", "propensity AUC within 0.02",
                   "the weighted ATE inside its yardstick", "fraction of missing information ratio 0.75 to 1.33",
                   "zero share within 1 point", "rare-level share within 1 point",
                   "censored share by centre within 2 points", "structure rules broken 0",
                   "ST9/tstr_hgb: AUC at least its run's TRTR minus 0.02", "ST7/tstr_glm: AUC at least its run's TRTR minus 0.02",
                   "Table 1 SMDs under 0.1 (the worst table)"):
        assert wanted in names, wanted


def _grouped(groups: "list[str]", values: "list[float]", name: str) -> B.View:
    return B.View(pd.DataFrame({"g": groups, "x": [float(v) for v in values]}), name)


def _read_x(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
    return v.text("g"), {"x": [float(x) for x in v.num("x")]}


def test_a_comparison_table_1_cannot_make_is_a_difference_never_0() -> None:
    """Codex's review, its item 1 (LANE MU RULINGS 6 (1)): a group the twin's labels replaced, a column it lacks and two
    unequal constants (real all 1, twin all 0) read as differences (infinity), never 0.0; two equal constants read 0;
    and `_table_max` keeps a table run with no reading visible (0.04 beside a missing result is not 0.04)."""
    real = _grouped(["a"] * 6 + ["b"] * 6, [1, 2, 3, 4, 5, 6, 1, 1, 1, 1, 1, 1], "real")
    same = _grouped(["a"] * 6 + ["b"] * 6, [1, 2, 3, 4, 5, 6, 1, 1, 1, 1, 1, 1], "same")
    assert M.table1_smd(real, same, _read_x, ["a", "b"]) == 0.0
    relabelled = _grouped(["z"] * 12, [1, 2, 3, 4, 5, 6, 1, 1, 1, 1, 1, 1], "relabelled")
    assert M.table1_smd(real, relabelled, _read_x, ["a", "b"]) == math.inf
    constants = _grouped(["a"] * 6 + ["b"] * 6, [1, 2, 3, 4, 5, 6, 0, 0, 0, 0, 0, 0], "constants")
    assert M.table1_smd(real, constants, _read_x, ["a", "b"]) == math.inf
    no_column = B.View(pd.DataFrame({"g": ["a"] * 6 + ["b"] * 6, "y": [1.0] * 12}), "no column")

    def read_if_there(v: B.View) -> "tuple[list[str | None], dict[str, list[float]]]":
        return v.text("g"), ({"x": [float(x) for x in v.num("x")]} if v.has("x") else {})

    assert M.table1_smd(real, no_column, read_if_there, ["a", "b"]) == math.inf

    def side(extra: "dict[str, float]") -> M.Side:
        return M.Side([], [], B.Panel({}, {}), extra)

    runs = [_measured("ST9", {"twin": [side({"t1_smd_max": 0.04})] * 3}),
            _measured("ST10", {"twin": [side({"not_made": 1.0})] * 3}),
            _measured("ST7", {"twin": [side({})] * 3})]
    assert M._table_max(runs, "twin", "t1_smd_max") == math.inf
    assert M._table_max(runs[::2], "twin", "t1_smd_max") == 0.04
    assert M._table_max(runs[2:], "twin", "t1_smd_max") != M._table_max(runs[2:], "twin", "t1_smd_max")


def test_a_prediction_that_stops_on_the_twin_is_a_stop(monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's review, its item 5 (LANE MU RULINGS 6 (1)): a prediction model robust on the real table (it holds its TRTR
    yardstick) that stops on the twin -- its training, its predictions or their calibration, or the frame's columns a
    model cannot read -- is a stop of the twin's side, its status beside the panel's; it is not counted where it also
    stops on a replicate draw of the run, as the panel's analyses are not; a model with no yardstick is no stop; a twin
    not made stops every robust model."""
    real = B.read(U.text("ST7", 900, 2), "real")
    yard = {f"ST7/tstr_{k}:{m}": (0.7, 0.01) for k in ("glm", "hgb") for m in M.PREDICTION_METRICS}
    empty = B.Yardstick(B.Panel({}, {}), {}, set())

    def unreadable(*_args: object) -> object:
        raise B.AnalysisError("not numbers", "a text column")

    monkeypatch.setattr(M, "tstr_side", unreadable)
    twin = M.side(empty, [], "ST7", real, real, [0] * real.rows, 1, yard, [])
    assert twin.stops == ["ST7/tstr_glm", "ST7/tstr_hgb"], twin.stops
    assert twin.panel.status["ST7/tstr_glm"] == "not numbers"
    monkeypatch.setattr(M, "tstr_side", lambda *_a: ({}, {"ST7/tstr_glm": "no convergence", "ST7/tstr_hgb": "ok"}))
    twin = M.side(empty, [], "ST7", real, real, [0] * real.rows, 1, yard, [])
    assert twin.stops == ["ST7/tstr_glm"], twin.stops
    ok = M.Side([], [], B.Panel({}, {"ST7/tstr_glm": "ok", "ST7/tstr_hgb": "ok"}), {})
    run = M.Run("ST7", 900, 1, "S", empty, yard, {"twin": [twin], "replicate": [ok]}, 0.0, 0.0)
    assert M.stopping(twin, run) == 1.0 and M.measures([run], "_20k")["value"]["stops_20k"] == 1
    fragile = M.Side([], [], B.Panel({}, {"ST7/tstr_glm": "no convergence", "ST7/tstr_hgb": "ok"}), {})
    assert M.stopping(twin, M.Run("ST7", 900, 1, "S", empty, yard, {"twin": [twin], "replicate": [fragile]}, 0.0,
                                  0.0)) == 0.0
    no_yard = {k: v for k, v in yard.items() if not k.startswith("ST7/tstr_glm")}
    assert M.side(empty, [], "ST7", real, real, [0] * real.rows, 1, no_yard, []).stops == []
    assert M.not_made(empty, yard).stops == ["ST7/tstr_glm", "ST7/tstr_hgb"]


def test_the_matching_estimate_carries_no_standard_error() -> None:
    """LANE MU RULINGS 6 (4) (Codex's review, its item 4): matching reuses its controls, so the pairs are not independent;
    the matched difference is read inside its yardstick alone: no standard error, so no significance or strong flip."""
    view = B.read(U.text("ST9", 3000, 2), "frame")
    found = {e.key: e for e in M.st9_propensity(view)}
    matched = found["ST9/ate:matching"]
    assert matched.se is None and found["ST9/ate:weighting"].se, matched
    y = B.Yardstick(B.Panel({matched.key: matched}, {}), {matched.key: 0.01}, set())
    flipped = B.Estimate(matched.key, "F13", -matched.value, 0.0001, matched.support)
    [compared] = B.compare(y, B.Panel({matched.key: flipped}, {}))
    assert compared.sig_real is None
    run = M.Run("ST9", 3000, 1, "S", y, {}, {"twin": [M.Side([compared], [], B.Panel({}, {}), {})]}, 0.0, 0.0)
    assert M.strong_flips(run.sides["twin"][0], run) == 0.0


def test_each_labelled_route_stands_beside_the_twin_over_the_same_runs() -> None:
    """`route_shares`: a labelled route's family shares beside the headline twin's computed over the runs that read the
    route alone (the statistics check's item 8), with its variance components."""
    def side(inside: bool) -> M.Side:
        return M.Side([B.Compared("x", "F11", (), 1.0, 1.0, 0.1, inside, None, None, True)], [], B.Panel({}, {}), {})

    with_p = _measured("ST7", {"twin": [side(True)], "twin_P": [side(False)]})
    without = _measured("ST9", {"twin": [side(False)]})
    found = M.route_shares([with_p, without])
    assert found["twin_P"]["tables"] == ["ST7-1"] and found["twin_P"]["twin"] == {"F11": 1.0}, found
    assert found["twin_P"]["route"] == {"F11": 0.0} and "varcomp" in found["twin_P"]


def test_the_variational_check_reads_its_real_tables_share_on_a_half(monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 2 (b): the plan's variational check (`plan_st7`) reads the share of persons fixed on the
    real table on every frame, so a half (a person's rows all in one) hands the fitter about half as many persons as
    the real table (a share recomputed on each frame would hand it about as many); the frames are read by a spy on the
    fitter, no fit is made."""
    seen: "list[int]" = []

    def spy(_formula: str, _parts: object, frame: pd.DataFrame) -> object:
        seen.append(int(frame["subject"].nunique()))
        raise B.AnalysisError("empty filter", "read by the case's spy")

    real = B.read(U.text("ST7", 6000, 2), "real")
    [vb] = [a for a in M.plan_st7(real) if a.name == "ST7/vb"]
    monkeypatch.setattr(M.BinomialBayesMixedGLM, "from_formula", staticmethod(spy))
    g = M.groups(real, "ST7", 2)
    half = real.subset([i for i, x in enumerate(g) if not x & 1], "half")
    for view in (real, half):
        with pytest.raises(B.AnalysisError):
            vb.run(view)
    assert seen[0] >= 250 and 0.35 < seen[1] / seen[0] < 0.65, seen


def test_the_variational_check_reads_a_share_of_persons_and_a_half_reads_half_as_many() -> None:
    """GENERATED: 20,000 identifiers: the share rule reads that share of them within 1 point, and the persons of a half
    (any half of the 16 groups) about half as many (the statistics check's item 9)."""
    r = random.Random(37)
    ids = [f"P{r.randint(0, 10 ** 9):09d}" for _ in range(20000)]
    for share in (0.015, 0.13, 0.5):
        assert abs(sum(M.bayes_chosen(s, share) for s in ids) / len(ids) - share) < 0.01, share
    half = ids[: len(ids) // 2]
    assert abs(sum(M.bayes_chosen(s, 0.13) for s in half) / sum(M.bayes_chosen(s, 0.13) for s in ids) - 0.5) < 0.05


def test_each_twin_seed_reads_a_key_of_its_own() -> None:
    """`key_for` gives each (table seed, twin seed) its own 32-byte key, and one installation folder never holds two."""
    keys = {twin_routes.key_for(s, k) for s in (1, 2, 3) for k in (0, 1, 2)}
    assert len(keys) == 9 and all(len(key) == 32 for key in keys) and twin_routes.TEST_KEY not in keys


def test_run_table_describes_each_twin_seed_under_its_own_key(tmp_path: pathlib.Path,
                                                               monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 2 (c), at the call site: `run_table` hands a keyed route's description of each twin
    seed that twin seed's key (`key_for(table seed, twin seed)`), and a route that reads no key the test key once (the
    descriptions and twins recorded here, no product run; the fast part holds that a description writes the key it is
    handed)."""
    handed: "list[tuple[str, bytes]]" = []
    text = U.text("ST10", 600, 3)

    def describe(name: str, place: pathlib.Path, stem: str, _text: str, _person: str = "", knows: object = None,
                 key: bytes = twin_routes.TEST_KEY) -> twin_routes.Described:
        handed.append((name, key))
        return twin_routes.Described(name, place, place, stem, place / f"{stem}-profile.json", True, "recorded", 0.0,
                                     (), key)

    monkeypatch.setattr(M, "plan_for", lambda _table, _real: [])
    monkeypatch.setattr(twin_routes, "describe", describe)
    monkeypatch.setattr(twin_routes, "generate", lambda _described, _seed: (text, ""))
    M.run_table("ST10", 600, 3, (0, 1), tmp_path / "C", route="C", controls=False)
    assert handed == [("C", twin_routes.key_for(3, 0)), ("C", twin_routes.key_for(3, 1))], handed
    handed.clear()
    M.run_table("ST10", 600, 3, (0, 1), tmp_path / "U", route="U", controls=False)
    assert handed == [("U", twin_routes.TEST_KEY)], handed


def test_a_frames_fits_are_kept_on_its_view() -> None:
    """The lasso path and the mixture are fitted once a frame (the statistics check's item 16): a second reading of the
    same view returns the same fit, a new view its own."""
    view = B.read(U.text("ST9", 1500, 4), "frame")
    scales = M._scales(view)
    assert M._lasso(view, scales) is M._lasso(view, scales)
    assert M._mixture(view) is M._mixture(view)
    assert M._mixture(B.read(U.text("ST9", 1500, 4), "again")) is not M._mixture(view)


def test_the_nights_memory_fallback_reads_a_person_sampled_half(monkeypatch: pytest.MonkeyPatch) -> None:
    """Where `SAMPLED_AT_NIGHT` names an analysis (skeptic 1's item 3, the brief's fallback), a frame of `SAMPLED_ROWS`
    rows or more is read on a person-sampled half (a person's rows all in or all out), a smaller frame whole (the run's
    notes say so: the labelled child's case); `release_memory` hands free pages back and changes no number."""
    view = B.read(U.text("ST8", 3000, 2), "frame")
    half = M.person_half(view, "ST8")
    subjects = view.text("subject")
    kept = {subjects[i] for i in half}
    assert all((subjects[i] in kept) == (i in set(half)) for i in range(view.rows))
    assert 0.4 < len(half) / view.rows < 0.6
    monkeypatch.setattr(M, "SAMPLED_ROWS", 2000)
    monkeypatch.setattr(M, "SAMPLED_AT_NIGHT", {"ST10": ("ST10/zeros",)})
    real = B.read(U.text("ST10", 3000, 1), "real")
    plan = {a.name: a for a in M.plan_for("ST10", real)}
    whole = B.run_panel([plan["ST10/pois"]], real).estimates
    halved = B.run_panel([plan["ST10/zeros"]], real).estimates["ST10/zeros:share"]
    assert whole["ST10/pois:age"].support == 3000 and halved.se is not None
    rows_read = round(halved.value * (1 - halved.value) / halved.se ** 2)
    assert 1200 < rows_read < 1800, rows_read
    M.release_memory()


def test_each_sides_frame_is_let_go_before_the_next(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A TEST DEVICE at 3,000 rows (skeptic 1's item 3): `run_table` lets each side's frame go before it reads the next,
    so only the real table's frame stands beside a new one, and none is left when the run ends."""
    views: "list[weakref.ref[B.View]]" = []
    alive: "list[int]" = []
    read = M.B.read

    def recorded(source: object, name: str) -> B.View:
        gc.collect()
        alive.append(sum(1 for v in views if v() is not None))
        view = read(source, name)  # type: ignore[arg-type]
        views.append(weakref.ref(view))
        return view

    monkeypatch.setattr(M.B, "read", recorded)
    M.run_table("ST10", 3000, 1, (0,), tmp_path, route="S")
    gc.collect()
    assert len(views) == 4 and max(alive) <= 1 and not any(v() is not None for v in views), alive


SUBJECT_ANSWER = "the subject question="


def test_route_u_is_route_s_where_the_typed_commands_do_not_switch(tmp_path: pathlib.Path) -> None:
    """A TEST DEVICE at 3,000 rows: on a tree whose `cli.main` takes no `unswitched` keyword, route U's description is
    route S's byte for byte and its answers are route S's; on a tree whose typed commands switch the chain on, route S
    also answers the subject question (which the unswitched commands never put) and every other answer is route U's;
    route U never reads the installation's key (`keyed`)."""
    text = U.text("ST10", 3000, 1)
    s_route = twin_routes.describe("S", tmp_path / "S", "ST10-1", text, knows=U.KNOWS["ST10"])
    u_route = twin_routes.describe("U", tmp_path / "U", "ST10-1", text, knows=U.KNOWS["ST10"])
    assert not twin_routes.keyed("U") and twin_routes.keyed("C")
    assert u_route.route == "U"
    if not twin_routes.typed_switched():
        assert s_route.description.read_bytes() == u_route.description.read_bytes()
        assert u_route.answered == s_route.answered
        return

    def without_subject(answered: str) -> "list[str]":
        return [a for a in answered.split("; ") if not a.startswith(SUBJECT_ANSWER)]

    assert any(a.startswith(SUBJECT_ANSWER) for a in s_route.answered.split("; ")), s_route.answered
    assert without_subject(u_route.answered) == without_subject(s_route.answered), (u_route.answered, s_route.answered)


def _inside(path: pathlib.Path, folder: pathlib.Path) -> bool:
    return path == folder or folder in path.parents


def test_the_installation_folder_lies_outside_the_tables_folder_and_every_out_folder(tmp_path: pathlib.Path) -> None:
    """For a run folder, the installation folder (and the data folder in it) is neither the folder that holds the table
    nor any route's out folder, nor inside either, nor do they stand in it (lane MU's combined verify, its item 1: the
    switched commands refuse a data folder there, `cli._data_folder_refusal`, and route S could not describe a table);
    where the measured tree has that screen, it accepts the routes' placement as they make it."""
    from synthtwin import cli

    folder = tmp_path / "ST10-1" / "route-S-k0"
    place = twin_routes.installation_place(folder)
    data = place / "synthtwin"
    table = twin_routes.table_file(folder, "ST10-1")
    screen = getattr(cli, "_data_folder_refusal", None)
    for route in twin_routes.ROUTES:
        out = twin_routes.out_folder(folder, "ST10-1", route)
        for there in (table.parent, out):
            assert not _inside(place, there) and not _inside(data, there) and data.parent != there, (route, there)
            assert not _inside(there, place), (route, there)
        if screen is not None:
            assert screen(data, str(table), str(out)) == "", route
    made = twin_routes.installation_folder(folder, twin_routes.key_for(1, 0))
    assert made == place and (data / "chain-key").read_bytes() == twin_routes.key_for(1, 0)


def test_a_labelled_routes_child_reads_no_controls(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A TEST DEVICE at 3,000 rows: `run_table(..., controls=False)` (a night's route P child) reads the twin alone; its
    route's answers are noted, and so is the night's memory fallback where it reads a person-sampled half."""
    monkeypatch.setattr(M, "SAMPLED_ROWS", 2000)
    monkeypatch.setattr(M, "SAMPLED_AT_NIGHT", {"ST10": ("ST10/zeros",)})
    monkeypatch.setattr(M, "HALVED_FRAMES_AT_NIGHT", ("ST10",))
    run = M.run_table("ST10", 3000, 1, (0,), tmp_path, route="S", controls=False)
    assert set(run.sides) == {"twin"} and len(run.sides["twin"]) == 1
    # Route S is keyed where the typed commands switch the chain on (its note then names the twin seed's key).
    assert any(note.startswith(("ST10 route S: ", "ST10 route S key 0: ")) for note in run.notes), run.notes
    assert any("ST10/zeros read a person-sampled half" in note for note in run.notes), run.notes
    assert any("every frame read on a person-sampled half" in note for note in run.notes), run.notes
    assert 1200 < run.rows < 1800, run.rows


def test_k_bc_14_fits_in_12000_bytes() -> None:
    """K-BC-14 is one compact entry: its value at both sizes, every family filled with long numbers, and its rule within
    12,000 bytes as compact JSON (the ledger's room); the worst family is a target only and the strong flips are
    ratcheted with their allowance."""
    entry = M.ledger_entry(M.worst_case_value(), "0123456789abcdef0123456789abcdef01234567", "2026-11-18",
                           "x" * 300)
    size = len(json.dumps(entry, separators=(",", ":"), sort_keys=True))
    assert size <= 12000, size
    assert len(entry["rule"]) <= 2600
    assert "worst_family_points_below_replicate_20k" not in entry["expected"]
    assert entry["target"]["worst_family_points_below_replicate_20k"] == 25.0
    assert entry["expected"]["strong_sign_flips_20k"] == round(1234 + 3.0 * math.sqrt(1234), 1)
    small = M.ledger_entry({"controls_hold_20k": True, "supported_estimates_20k": 300, "strong_sign_flips_20k": 0},
                           "c", "d", "m")
    assert small["expected"]["strong_sign_flips_20k"] == 3.0


def test_route_s_answers_every_question_as_the_person_who_holds_the_table(tmp_path: pathlib.Path) -> None:
    """A TEST DEVICE at 5,000 rows (`small_tables_refused=False`): ST12 described by route S, every blank entry of its
    questions file (the checklist's columns included) answered by the column's known reading: no column is read as
    record numbers (a route that left the checklist blank held the stay and the procedure group so; the statistics
    check's item 1), and the answers and the entries left blank are named."""
    text = U.text("ST12", 5000, 1)
    made = twin_routes.describe_typed(tmp_path, "ST12-1", text, "", knows=U.KNOWS["ST12"])
    lines = (made.out / "ST12-1-profile.txt").read_text(encoding="utf-8").splitlines()
    held = [lines[i - 1].strip() for i, line in enumerate(lines) if "read as:" in line and "record numbers" in line]
    assert not held, held
    assert "stay_days=measurement" in made.answered, made.answered
    assert all("no answer fits" not in left for left in made.left), made.left
    # LANE CHON RULINGS 6 item 6 (the combined verify's item 2): a part of a table described as the whole table was
    # answered -- E0b's `describe` hands the part's first `profile` run the whole table's answered questions file.
    part = B.describe(tmp_path / "part", "ST12-1-A", B.rows_text(text, list(range(0, 5000, 2))), "", True,
                      U.KNOWS["ST12"], answers_from=made.out / "ST12-1-questions.json")
    assert isinstance(part, twin_routes.Described)
    assert part.answered.startswith("the whole table's answers carried"), part.answered
    assert twin_routes.held_columns(part) == []


@pytest.mark.parametrize("table", ("ST7", "ST9"))
def test_the_fast_part_runs_through_route_c(table: str, tmp_path: pathlib.Path) -> None:
    """A TEST DEVICE at 5,000 rows (below the table floor, so `small_tables_refused=False`): the battery runs to its end
    through route C, every analysis runs on the real table, the replicate and the shuffled twin are read (the flattened
    replicate in its own case at 20,000 rows), K-BC-14's measures are computed, the route's answers are noted and the
    twin seed's key is its own.
    No claim. Where the product cannot make the twin (ST7 behind the switch on a line whose generator does not yet read
    the patient layer: lane MU's finding F1), the twin's side reads as one on which nothing runs and the run's notes name
    the product's error; ST9's twin is made."""
    run = M.run_table(table, 5000, 1, (0,), tmp_path / table, route="C", flattened=False)
    key = twin_routes.installation_place(tmp_path / table / "route-C-k0") / "synthtwin" / "chain-key"
    assert key.read_bytes() == twin_routes.key_for(1, 0)
    assert all(s == "ok" for s in run.yard.real.status.values()), run.yard.real.status
    assert run.sides["twin"] and run.sides["replicate"] and run.sides["shuffled"]
    assert "flattened" not in run.sides
    made = "not_made" not in run.sides["twin"][0].extra
    assert made or any(note.startswith("route C: the product could not") for note in run.notes), run.notes
    assert any(note.startswith(f"{table} route C key 0: ") for note in run.notes), run.notes
    if table == "ST9":
        assert made, run.notes
        assert run.sides["twin"][0].panel.estimates
        assert set(run.real_extra) == {"smd_before", "smd_after"}
    else:
        assert run.yard.real.estimates["ST7/growth:bend_B"].tags == ("curve",)
        assert run.yard.real.estimates["ST7/lmm:arm_years_sq"].tags == ("curvature",)
    found = M.measures([run], "_20k")
    assert set(found["value"]) >= {"controls_hold_20k", "supported_estimates_20k", "pooled_points_below_replicate_20k",
                                   "worst_family_points_below_replicate_20k", "strong_sign_flips_20k", "stops_20k"}
    assert found["value"]["supported_estimates_20k"] > 0
    assert set(found["value"]) <= set(M.worst_case_value()), set(found["value"]) - set(M.worst_case_value())

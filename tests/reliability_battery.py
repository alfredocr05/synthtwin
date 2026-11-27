"""The reliability battery: analysis code that runs unchanged on the twin and reaches the real table's conclusions (K-RU-01).

THE QUESTION IT ANSWERS. A person develops an analysis on the twin and
runs the same file, unchanged, on the real table. Does the file run, and
does it reach the conclusion the real table holds? About forty plain
analysis files (`tests/reliability_scripts/`), each written as an analyst
writes one -- it reads its table by its file name and nothing else,
cleans it as a researcher does (explicit date formats,
`to_numeric(errors="coerce")`, a filter on the sentinel and on "<"
results, `== code` and `isin` filters, dummies from a level list,
`groupby(patient).cumcount()`, pivots by key), fits its model and writes
its estimates to `results.json` -- are run on an invented REAL table
(`tests/reliability_tables.py`: seven tables with seeded relationships
and a null table of unrelated columns),
on the TWIN the shipped commands make of it, and on two controls in the
same run: a FRESH SAMPLE (a second draw of the same generator at the same
size: what a perfect twin scores, the ceiling) and a SHUFFLED TABLE (the
real table with every column permuted on its own: what a twin with no
relation between columns scores).

THE TWIN IS THE ONE A PERSON GETS (route S of lane MU's harness, written
here so the battery stands on any head): `synthtwin profile TABLE
--out-dir FOLDER`; every entry of the questions file it writes answered as
the person who holds the table answers it, truthfully (`truthful`), and
`synthtwin profile` again with `--answers`, round by round while a round
writes an answer (a round the record of earlier descriptions refuses runs
once more with `--replace-description`, the screen's own remedy, where the
tree has it); then `synthtwin generate DESCRIPTION --seed K`. The orders
table T5, whose patients are the cohort T1's, is described with
`--linked-to` naming T1's table and built with `--linked-to` naming T1's
description, in T1's installation (lane W5-F14), as one person who holds
both tables of a study makes their twins join. Nobody
is at the keyboard: the commands run in this process through `cli.main`,
the installation's data folder pointed at a folder of the run's own that
holds the fixed test key and an empty record, both readable by this
account alone, so a run never touches the
account's own folder and its twin is the same on every machine. Below the
owner's table floor (the suite's small tables only) `cli.main`'s internal
`small_tables_refused=False` is passed: a TEST DEVICE, whose results are
no product claim.

THE PASS RULE (K-RU-01), for one script on one table at one size and one
twin seed:

1. RUNS: the file ends without an error on the twin; every estimate it
   writes on the real table it writes, finite, on the twin; no warning
   class of the statistical libraries the real run lacks (`TROUBLE`:
   non-convergence, separation, a singular matrix, mixed types read); no
   date or number parsed worse than on the real table (a script's
   `unparsed_*` check more than 0.01 above the real one's) and no filter
   that keeps rows on the real table and none on the twin (`kept_*`).
2. SUPPORTED estimate: written on the real table and on all eight halves
   of it (four splits, each by one bit of a SplitMix64 group of sixteen;
   a patient's rows share a group), its smallest defining cell at least
   22 people on the real table and 11 in each half.
3. SAME estimate: (a) where the real p is under 0.05 the twin's sign is the
   real one; (b) the significance class at 5 per cent is the same, not
   charged where the real p lies from 0.01 to 0.10 (a fresh sample flips
   those often); (c) the twin's value within 2.77 standard errors of the
   real one (1.96 x root 2, the 95 per cent spread between two independent
   samples); an estimate with no standard error of its own takes the
   half-split yardstick's, h / 2 (h the root mean square of half A minus
   half B: halves have twice the variance, so A - B has four times it);
   (d) the twin's standard error 0.8 to 1.25 times the real one, where both
   report one; (e) the two 95 per cent intervals overlap.
4. PASS: RUNS, every supported primary estimate SAME, and at least 90 per
   cent of the supported estimates SAME.

THE CONTROLS: a family whose fresh sample passes under 80 per cent is
VOID (its bar too strict at that size) and named; the run is INVALID
where the shuffled table passes more than half the runs of the scripts
that read a relation between columns; on the control table T8, whose ten
columns are drawn independently, at most 8 per cent of their 45 pairs may
test as related at 5 per cent and never past 15 (the null clause); and on
T1 to T7 the share of the real table's non-significant supported estimates
the twin makes significant is set against the fresh sample's
(`invented_points`).

F0, the data handling of the zoo's analyst scripts over its kinds of
export, is K-HZ-01's own measurement: `f0_from_ledger` reads it from that
entry, and the driver runs the zoo itself only when asked.

Nothing here changes the product: the twin is made by the product's own
commands, and this module only reads what they write.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import math
import os
import pathlib
import random
import runpy
import shutil
import statistics
import time
import warnings
from typing import Iterator

import reliability_tables as T

SCRIPTS_FOLDER = pathlib.Path(__file__).resolve().parent / "reliability_scripts"
RESULTS_FILE = "results.json"
HOLDOUT_FILE = "cohort_holdout.csv"
# Every script: its table and whether it reads a relation between two
# columns or more (the shuffled table's control is counted over those).
# Its family is its file name's prefix: f07_... is F7.
SCRIPTS = {
    "f01_table_one": ("T1", False),
    "f01_table_one_by_complication": ("T1", True),
    "f02_group_tests": ("T1", True),
    "f03_linear_stay": ("T1", True),
    "f04_logistic_complication": ("T1", True),
    "f04_logistic_death": ("T1", True),
    "f05_poisson_medicines": ("T1", True),
    "f06_survival_curves": ("T1", True),
    "f06_cox": ("T1", True),
    "f06_exponential": ("T1", True),
    "f08_monthly_volume": ("T1", False),
    "f08_weekdays": ("T1", False),
    "f10_propensity": ("T1", True),
    "f11_prediction": ("T1", True),
    "f12_missing": ("T1", True),
    "f13_ordinal_class": ("T1", True),
    "f13_multinomial_technique": ("T1", True),
    "f01_visits_per_patient": ("T2", False),
    "f05_blood_loss_two_part": ("T2", True),
    "f07_random_intercept": ("T2", True),
    "f07_random_slope": ("T2", True),
    "f07_gee": ("T2", True),
    "f07_first_last_ancova": ("T2", True),
    "f09_visits_wide": ("T2", True),
    "f02_entry_lag": ("T3", True),
    "f07_heart_rate_trend": ("T3", True),
    "f08_charting_minutes": ("T3", True),
    "f09_item_values": ("T3", True),
    "f09_pressure_pairs": ("T3", True),
    "f02_recovery_time": ("T4", True),
    "f03_linear_duration": ("T4", True),
    "f04_logistic_critical_care": ("T4", True),
    "f08_case_starts": ("T4", False),
    "f09_clock_rules": ("T4", True),
    "f02_actions_by_drug": ("T5", True),
    "f05_orders_per_patient": ("T5", False),
    "f08_given_lag": ("T5", True),
    "f09_dose_units": ("T5", True),
    "f14_join_cohort": ("T5", True),
    "f01_lab_summary": ("T6", True),
    "f02_receipt_lag": ("T6", True),
    "f07_glucose_icc": ("T6", True),
    "f09_first_last_lab": ("T6", True),
    "f09_sentinel": ("T6", True),
    "f01_account_ids": ("T7", True),
    "f02_null_pairs": ("T8", False),
}
NULL_SCRIPT = "f02_null_pairs"
PAIR_PREFIX = "pair:"
FAMILIES = {
    "F0": "data handling over the zoo's kinds of export (K-HZ-01)",
    "F1": "Table 1 and summaries",
    "F2": "group tests",
    "F3": "linear regression",
    "F4": "logistic regression",
    "F5": "counts",
    "F6": "survival",
    "F7": "repeated measures and trajectories",
    "F8": "time trends",
    "F9": "reshape and link within one table",
    "F10": "propensity",
    "F11": "prediction",
    "F12": "missing data",
    "F13": "ordinal and multinomial",
    "F14": "link across two tables (informational, outside the headline)",
}
HEADLINE_FAMILIES = tuple(f"F{k}" for k in range(1, 14))
INFORMATIONAL = ("F14",)
# THE EXTENDED BATTERY (lane STATS-B): further analyses a physician-researcher runs that families F1 to F13 lack, on
# the same tables and on T9 (`reliability_tables.EXTENDED_TABLES`), judged by the same pass rule beside the same
# controls. They are NOT K-RU-01's: `kpi_value` reads F1 to F13 alone whether or not they ran, and
# `extended_value` reads these. They run where `WITH_EXTENDED` is set (`catalogue`).
EXTENDED_SCRIPTS = {
    "f15_time_varying_cox": ("T2", True),
    "f15_time_to_first_event": ("T2", True),
    "f16_repeated_anova": ("T2", True),
    "f17_bland_altman": ("T9", True),
    "f17_reader_agreement": ("T9", True),
    "f18_roc": ("T9", True),
    "f19_interactions": ("T9", True),
    "f20_matching": ("T9", True),
    "f21_counts_exposure": ("T9", True),
    "f22_multiple_testing": ("T1", True),
    "f23_tables_trends": ("T1", True),
    "f24_cox_interaction": ("T9", True),
    # ...and lane STATS-C's: the analyses the battery had not tried yet.
    "f25_ordinal_grades": ("T9", True),
    "f25_multinomial_grades": ("T9", True),
    "f26_death_rate_offset": ("T1", True),
    "f26_hospital_rate_per_patient": ("T2", True),
    "f27_gee_ar1_pressure": ("T2", True),
    "f27_gee_ar1_binary": ("T2", True),
    "f28_random_slope_years": ("T2", True),
    "f28_mixed_logistic": ("T2", True),
    "f29_cumulative_incidence": ("T9", True),
    "f29_fine_gray": ("T9", True),
    "f30_paired_rank_tests": ("T2", True),
    # ...and lane STATS-D's: the analyses of the owner's list the battery had not tried, T10 (operations: a surgeon
    # and an anaesthetist crossed) the table of four of them.
    "f31_zero_inflated_visits": ("T10", True),
    "f32_cox_time_varying_effect": ("T9", True),
    "f32_shared_frailty": ("T10", True),
    "f33_crossed_effects": ("T10", True),
    "f34_quantile_regression": ("T1", True),
    "f35_penalised_selection": ("T10", True),
    "f36_imputation_regression": ("T10", True),
    "f37_mediation": ("T1", True),
    "f38_repeated_roc": ("T2", True),
    "f39_thresholds": ("T9", True),
    "f40_trend_tests": ("T1", True),
    "f41_splines": ("T1", True),
}
EXTENDED_FAMILIES = {
    "F15": "time to an event with a measurement that changes over time, and from repeated rows",
    "F16": "repeated-measures analysis of variance, paired and rank tests",
    "F17": "agreement of two methods and of two readers",
    "F18": "diagnostic accuracy: ROC areas, sensitivity and specificity",
    "F19": "effect modification: interactions and strata",
    "F20": "propensity-score matching",
    "F21": "counts over observed times of different lengths",
    "F22": "many tests adjusted for their number",
    "F23": "contingency tables and trends",
    "F24": "survival curves and a Cox model with an interaction",
    "F25": "ordinal and multinomial regression of a reader's grade",
    "F26": "rates over follow-up and per visit, with the observed time as an offset",
    "F27": "generalised estimating equations under an autoregressive working correlation",
    "F28": "mixed models: a random slope over years, a mixed logistic model",
    "F29": "competing risks: cumulative incidence, cause-specific and Fine-Gray models",
    "F30": "repeated measurements without a model: Cochran's Q, McNemar, signed-rank and trend tests",
    "F31": "counts with many zeros: negative binomial, zero-inflated and hurdle models",
    "F32": "survival with an effect that changes over time, and with a frailty shared within a surgeon",
    "F33": "a mixed model with crossed random effects (a surgeon and an anaesthetist)",
    "F34": "quantile regression",
    "F35": "penalised regression (lasso and ridge) and the stability of its selection",
    "F36": "multiple imputation by chained equations, then regression",
    "F37": "mediation",
    "F38": "ROC areas with repeated measurements of a patient",
    "F39": "sensitivity, specificity and likelihood ratios at several thresholds",
    "F40": "tests without a model for ordered groups and trends",
    "F41": "a curved effect read through a natural cubic spline, and the risk it gives at two ages",
}
WITH_EXTENDED = False
SUPPORT = 22
HALF_SUPPORT = 11
Z = 1.959963984540054
SIZE_SE = 2.77
SE_RATIO = (0.8, 1.25)
NOT_CHARGED = (0.01, 0.10)
SAME_SHARE = 0.9
VOID_BELOW = 0.8
NULL_AT_MOST = 0.08
NULL_NEVER_PAST = 0.15
UNPARSED_MARGIN = 0.01
TINY = 1e-9
# The warning classes a run is charged for where the real run has none of
# that class: the libraries' words for a fit that did not settle, a
# separation, a singular matrix, and a column read with mixed types.
TROUBLE = frozenset({
    "ConvergenceWarning", "PerfectSeparationWarning", "HessianInversionWarning", "IterationLimitWarning",
    "LinAlgWarning", "DtypeWarning", "EstimationWarning",
})
TIERS = {
    # rows, table seeds, twin seeds
    "kpi": {"rows": 20000, "seeds": (1, 2, 3), "twins": (0, 1, 2)},
    "quick": {"rows": 20000, "seeds": (1,), "twins": (0,)},
    "night": {"rows": 200000, "seeds": (1,), "twins": (0, 1)},
}
# The fixed test key and the empty record of an installation folder of the
# run's own (`tests/conftest.py` hands each test the same key).
TEST_KEY = bytes(range(32))
_EMPTY_LEDGER = '{\n  "tables": [],\n  "version": 1\n}\n'
ROUNDS = 4


def family_of(stem: str) -> str:
    """A script's family from its file name: f07_random_slope -> F7, f13_... -> F13."""
    return f"F{int(stem[1:3])}"


@dataclasses.dataclass(frozen=True)
class Script:
    """One analysis file: its name, table, family, and whether it reads a relation between columns."""

    stem: str
    table: str
    family: str
    relation: bool

    @property
    def path(self) -> pathlib.Path:
        return SCRIPTS_FOLDER / f"{self.stem}.py"


def catalogue(tables: "tuple[str, ...] | None" = None, extended: "bool | None" = None) -> "list[Script]":
    """The scripts of the battery (of the named tables), in name order: K-RU-01's, and the extended battery's beside
    them where ``extended`` (by default `WITH_EXTENDED`) is set."""
    every = dict(SCRIPTS)
    if WITH_EXTENDED if extended is None else extended:
        every.update(EXTENDED_SCRIPTS)
    return [Script(stem, table, family_of(stem), relation) for stem, (table, relation) in sorted(every.items())
            if tables is None or table in tables]


def script_files() -> "list[str]":
    """The script files the folder holds, by name: every one must be in `SCRIPTS` or `EXTENDED_SCRIPTS`, and every entry a file."""
    return sorted(path.stem for path in SCRIPTS_FOLDER.glob("f*.py"))


# -- one script on one table ----------------------------------------------------


@dataclasses.dataclass
class ScriptRun:
    """One script's run on one table: whether it ended, its estimates, its checks, its warning classes.

    ``estimands`` are the estimates the script judges by (its conclusions);
    ``context`` the others it writes, read only for the significance the
    twin invents (`invented`).
    """

    ok: bool
    error: str
    estimands: "dict[str, dict]"
    checks: "dict[str, float]"
    trouble: "list[str]"
    seconds: float = 0.0
    context: "dict[str, dict]" = dataclasses.field(default_factory=dict)

    def every_estimate(self) -> "ScriptRun":
        """The same run with its context written beside its judged estimates (a judged one wins a shared name)."""
        return dataclasses.replace(self, estimands={**self.context, **self.estimands})


def finite(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def run_script(path: pathlib.Path, folder: pathlib.Path) -> ScriptRun:
    """Run one analysis file in ``folder`` as `python file.py` would there, in this process.

    The file reads its tables from the folder by name and writes
    `results.json` there. An error it raises (or a non-zero exit) is
    recorded, never raised; what it prints is dropped; every warning it
    triggers is recorded by class, and those of `TROUBLE` are kept.
    """
    out = folder / RESULTS_FILE
    if out.exists():
        out.unlink()
    error = ""
    started = time.perf_counter()
    previous = os.getcwd()
    sink = io.StringIO()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            os.chdir(folder)
            with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
                runpy.run_path(str(path), run_name="__main__")
        except SystemExit as stop:
            if stop.code not in (None, 0):
                error = f"exit {stop.code}"
        except Exception as failure:  # noqa: BLE001 -- a script's error is a result to record
            error = f"{type(failure).__name__}: {failure}"[:300]
        finally:
            os.chdir(previous)
    trouble = sorted({w.category.__name__ for w in caught if w.category.__name__ in TROUBLE})
    seconds = time.perf_counter() - started
    if error or not out.exists():
        return ScriptRun(False, error or "no results written", {}, {}, trouble, seconds)
    found = json.loads(out.read_text(encoding="utf-8"))
    out.unlink()
    estimands = {str(key): dict(value) for key, value in (found.get("estimands") or {}).items()}
    context = {str(key): dict(value) for key, value in (found.get("context") or {}).items()}
    checks = {str(key): float(value) for key, value in (found.get("checks") or {}).items() if finite(value)}
    return ScriptRun(True, "", estimands, checks, trouble, seconds, context)


# -- the pass rule -----------------------------------------------------------------


@dataclasses.dataclass
class Yard:
    """An estimate's half-split yardstick and whether it is supported (2.3, item 2)."""

    h: float
    supported: bool


def yardsticks(real: ScriptRun, halves: "list[ScriptRun]") -> "dict[str, Yard]":
    """Each real estimate's yardstick over the eight halves, in the order A0, B0, A1, B1, A2, B2, A3, B3.

    Supported where the real cell is at least `SUPPORT` people and each
    half's at least `HALF_SUPPORT`, and the estimate is finite on all
    eight; h is the root mean square of half A minus half B over the four
    splits (NaN where a half lacks it).
    """
    yards: "dict[str, Yard]" = {}
    for key, estimate in real.estimands.items():
        if not finite(estimate.get("estimate")):
            continue
        support = estimate.get("support")
        supported = support is None or (finite(support) and support >= SUPPORT)
        values: "list[float]" = []
        for half in halves:
            got = half.estimands.get(key) if half.ok else None
            if got is None or not finite(got.get("estimate")):
                supported = False
                values += [math.nan]
                continue
            cell = got.get("support")
            if cell is not None and (not finite(cell) or cell < HALF_SUPPORT):
                supported = False
            values += [float(got["estimate"])]
        if len(values) == 8 and all(math.isfinite(v) for v in values):
            h = math.sqrt(sum((values[2 * s] - values[2 * s + 1]) ** 2 for s in range(4)) / 4.0)
        else:
            h, supported = math.nan, False
        yards[key] = Yard(h, supported and len(halves) == 8)
    return yards


def _reported_se(estimate: dict) -> "float | None":
    se = estimate.get("se")
    return float(se) if finite(se) and se > 0 else None


def _p_of(estimate: dict) -> "float | None":
    """The estimate's p: its own, or the two-sided normal p of its value over its standard error."""
    p = estimate.get("p")
    if finite(p):
        return float(p)
    se = _reported_se(estimate)
    if se is None:
        return None
    return math.erfc(abs(float(estimate["estimate"]) / se) / math.sqrt(2.0))


def same(real: dict, other: "dict | None", h: float) -> str:
    """'' where the other table's estimate reaches the real one's conclusion (2.3, item 3), else the clause it fails."""
    if other is None or not finite(other.get("estimate")):
        return "absent"
    theta_r, theta_t = float(real["estimate"]), float(other["estimate"])
    se_r_own = _reported_se(real)
    se_r = se_r_own if se_r_own is not None else (h / 2.0 if math.isfinite(h) else math.nan)
    se_t_own = _reported_se(other)
    p_r, p_t = _p_of(real), _p_of(other)
    if p_r is not None and p_r < 0.05 and (theta_t > 0) - (theta_t < 0) != (theta_r > 0) - (theta_r < 0):
        return "direction"
    if (p_r is not None and p_t is not None and (p_r < 0.05) != (p_t < 0.05)
            and not NOT_CHARGED[0] <= p_r <= NOT_CHARGED[1]):
        return "significance"
    if not math.isfinite(se_r) or abs(theta_t - theta_r) > SIZE_SE * se_r + TINY:
        return "size"
    if se_r_own is not None and se_t_own is not None and not SE_RATIO[0] <= se_t_own / se_r_own <= SE_RATIO[1]:
        return "precision"
    se_t = se_t_own if se_t_own is not None else se_r
    if abs(theta_t - theta_r) > Z * (se_r + se_t) + TINY:
        return "intervals"
    return ""


def runs(real: ScriptRun, other: ScriptRun) -> str:
    """'' where the file runs unchanged on the other table (2.3, item 1), else why it does not."""
    if not other.ok:
        return f"stops: {other.error}"
    for key, estimate in sorted(real.estimands.items()):
        if finite(estimate.get("estimate")) and not finite((other.estimands.get(key) or {}).get("estimate")):
            return f"no estimate {key}"
    new = sorted(set(other.trouble) - set(real.trouble))
    if new:
        return f"warns: {new[0]}"
    for name, value in sorted(other.checks.items()):
        if name.startswith("unparsed_") and value > real.checks.get(name, 0.0) + UNPARSED_MARGIN:
            return f"parses worse: {name} {value:.3f}"
        if name.startswith("kept_") and value == 0 and real.checks.get(name, 0.0) > 0:
            return f"keeps no row: {name}"
    return ""


@dataclasses.dataclass
class Judged:
    """One script on one table (twin, fresh sample or shuffled) against the real table."""

    runs: bool
    passed: bool
    why: str
    supported: int
    same: int
    failing: "dict[str, str]"
    real_quiet: int = 0
    made_loud: int = 0
    null_share: "float | None" = None


def null_share(run: ScriptRun) -> "float | None":
    """The share of a null script's pairs called related at 5 per cent, or None where it wrote none."""
    ps = [float(e["p"]) for key, e in run.estimands.items() if key.startswith(PAIR_PREFIX) and finite(e.get("p"))]
    return None if not ps else sum(1 for p in ps if p < 0.05) / len(ps)


def invented(real: ScriptRun, yards: "dict[str, Yard]", other: ScriptRun) -> "tuple[int, int]":
    """The supported estimates the real table calls not significant at 5 per cent, and how many the other calls so."""
    quiet = loud = 0
    for key in sorted(k for k, y in yards.items() if y.supported):
        p_r = _p_of(real.estimands[key])
        if p_r is not None and p_r >= 0.05:
            quiet += 1
            got = other.estimands.get(key) if other.ok else None
            p_t = _p_of(got) if got is not None and finite(got.get("estimate")) else None
            loud += int(p_t is not None and p_t < 0.05)
    return quiet, loud


def judge(real: ScriptRun, yards: "dict[str, Yard]", other: ScriptRun,
          every: "tuple[ScriptRun, dict[str, Yard], ScriptRun] | None" = None) -> Judged:
    """The pass rule for one script on one table (2.3, items 1 to 4), with what each clause found.

    ``every`` (the real run, its yardsticks and the other run, each with its
    context beside its judged estimates) is what the significance the
    other table invents is counted over; without it, the judged estimates.
    """
    why = runs(real, other)
    ran = not why
    keys = sorted(k for k, y in yards.items() if y.supported)
    failing: "dict[str, str]" = {}
    for key in keys:
        clause = same(real.estimands[key], other.estimands.get(key) if other.ok else None, yards[key].h)
        if clause:
            failing[key] = clause
    quiet, loud = invented(*every) if every is not None else invented(real, yards, other)
    primaries = [k for k in keys if real.estimands[k].get("primary")]
    share = null_share(other) if other.ok else None
    if any(k.startswith(PAIR_PREFIX) for k in real.estimands):
        # THE NULL TABLE'S SCRIPT: its conclusion is that no pair is related
        # beyond chance, so a run passes where it runs and calls at most
        # `NULL_NEVER_PAST` of its pairs related at 5 per cent (2.3, item 6).
        passed = not why and share is not None and share <= NULL_NEVER_PAST
        if not why and not passed:
            why = f"invents relations: {share} of the pairs related at 5 per cent"
        return Judged(ran, passed, why, len(keys), len(keys) - len(failing), failing, 0, 0, share)
    passed = not why and all(k not in failing for k in primaries) and (
        len(keys) - len(failing) >= SAME_SHARE * len(keys) - TINY)
    if not why and not passed:
        first = next((k for k in primaries if k in failing), None) or sorted(failing)[0]
        why = f"not the same: {first} ({failing[first]})"
    return Judged(ran, passed, why, len(keys), len(keys) - len(failing), failing, quiet, loud, share)


# -- the halves and the controls ----------------------------------------------------

_MASK = (1 << 64) - 1


def splitmix64(x: int) -> int:
    """SplitMix64's output for one input."""
    z = (x + 0x9E3779B97F4A7C15) & _MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
    return z ^ (z >> 31)


def _cells(line: str) -> "list[str]":
    return line.split(",")


def groups_of(text: str, seed: int) -> "list[int]":
    """Each data row's group of sixteen, by its patient (every table names one), so a patient's rows share a group."""
    lines = text.splitlines()
    place = _cells(lines[0]).index("patient_id")
    out: "list[int]" = []
    for line in lines[1:]:
        key = "".join(ch for ch in _cells(line)[place] if ch.isdigit())
        out += [splitmix64(seed * 1_000_003 + (int(key) if key else 0)) % 16]
    return out


def halves_of(text: str, seed: int) -> "list[str]":
    """The eight halves of a table's text, A0, B0, A1, B1, A2, B2, A3, B3: half A of split s keeps the groups with bit s clear."""
    lines = text.splitlines()
    groups = groups_of(text, seed)
    out: "list[str]" = []
    for s in range(4):
        for wanted in (0, 1):
            out += [lines[0] + "\n" + "".join(line + "\n" for line, g in zip(lines[1:], groups)
                                              if (g >> s) & 1 == wanted)]
    return out


def shuffled_text(text: str, seed: int) -> str:
    """The table with every column shuffled on its own, each cell as written (the battery's tables quote no cell)."""
    lines = text.splitlines()
    columns = [list(c) for c in zip(*(_cells(line) for line in lines[1:]))]
    r = random.Random(seed)
    for column in columns:
        r.shuffle(column)
    return lines[0] + "\n" + "".join(",".join(row) + "\n" for row in zip(*columns))


def replicate_seed(seed: int, twin: int) -> int:
    """The fresh sample's seed at a table seed and a twin seed (as the analyst battery's)."""
    return seed * 1000 + 100 + twin


def holdout_seed(seed: int) -> int:
    """The held-out patients' seed at a table seed: a third draw of T1, the "real" patients a prediction is tested on."""
    return seed * 1000 + 999


# -- the twin a person gets ---------------------------------------------------------


def _entries(document: object) -> "list[dict]":
    """Every entry of a questions file that takes an answer: `about_your_file`, `asked` and the checklist's columns."""
    if not isinstance(document, dict):
        return []
    found: "list[dict]" = []
    for key in ("about_your_file", "asked"):
        found += [e for e in document.get(key) or [] if isinstance(e, dict) and "answers_you_can_give" in e]
    checklist = document.get("checklist")
    if isinstance(checklist, dict):
        found += [e for e in checklist.get("columns") or [] if isinstance(e, dict) and "answers_you_can_give" in e]
    # ...and each measurement of a long table asked about on its own (plan P4-D514), answered as its value column
    # is known: `measurement` for a column of readings.
    measured = document.get("measurements_asked") if ANSWER_MEASUREMENTS else None
    if isinstance(measured, dict):
        found += [e for e in measured.get("measurements") or [] if isinstance(e, dict) and "answers_you_can_give" in e]
    return found


# Whether the truthful holder answers the questions file's `measurements_asked` section (a gate case sets it off to
# keep every measurement's own question open).
ANSWER_MEASUREMENTS = True


def _offered(entry: dict) -> "list[str]":
    return [str(a.get("answer")) for a in entry.get("answers_you_can_give", []) if isinstance(a, dict)]


def _asks_for_people(entry: dict) -> bool:
    """Whether an entry is the person question: its `identifier` answer means the person the rows are about.

    Both wordings, as `health_zoo._asks_for_people` reads them: the first
    ("the people the rows are about") and the one every shipped run puts
    since the switch went on (plan P4-D464), "identifies the person" beside
    `record` (lane GRa), which holds no word "people". Read as the first
    alone, the switched question was taken for a record number's: on T7 the
    guarantor's and the staff member's keys were answered `identifier` there,
    said to name the person, so profile counted the people by the two keys
    together (P4-D479), 40 staff numbers joined every row into one person,
    and the table of 20,000 rows and 11,091 patients was refused at the
    1,000-people floor. Answered `keep` there, as `truthful` answers every
    column but the patient's, each is asked next as record numbers and
    answered `identifier`: held, and joining nobody.
    """
    return any(str(a.get("answer")) == "identifier"
               and ("people" in str(a.get("means", "")) or "identifies the person" in str(a.get("means", "")))
               for a in entry.get("answers_you_can_give", []) if isinstance(a, dict))


PATIENT = "patient_id"


def truthful(table: str, column: str, choices: "list[str]", people: bool) -> str:
    """The answer the person who holds the table gives a column's question, or '' where none offered fits.

    The zoo's rule (`health_zoo.answer_generally`) and lane MU's route S,
    from what the person knows of each column (`reliability_tables.KNOWS`):
    an age's Safe Harbor question `yes`; the known reading where offered;
    else `keep` where `identifier` and `keep` are offered; the person
    question (``people``) `identifier` for the patient column alone and
    `keep` for any other; any other yes-or-no question `no` (no column of
    these tables is a Safe Harbor element but an age and the record
    numbers, which are answered `identifier`).
    """
    known = T.KNOWS[table].get(column, "")
    if column in T.AGES[table] and "yes" in choices:
        return "yes"
    given = known if known in choices else ""
    if not given and known and "identifier" in choices and "keep" in choices:
        given = "keep"
    if given == "identifier" and people and column != PATIENT:
        given = "keep" if "keep" in choices else ""
    if not given and "yes" in choices and "no" in choices:
        given = "no"
    return given


def answer_questions(questions: pathlib.Path, table: str) -> "tuple[list[str], list[str]]":
    """Answer every blank entry of a questions file truthfully, and the subject question; what was written and what was left."""
    if not questions.exists():
        return [], []
    document = json.loads(questions.read_text(encoding="utf-8"))
    written: "list[str]" = []
    left: "list[str]" = []
    for entry in _entries(document):
        if entry.get("your_answer"):
            continue
        column = str(entry.get("column", ""))
        pick = truthful(table, column, _offered(entry), _asks_for_people(entry))
        if pick:
            entry["your_answer"] = pick
            written += [f"{column or 'the file'}={pick}"]
        else:
            left += [column or "the file"]
    between = document.get("between_columns") if isinstance(document, dict) else None
    question = between.get("rows_per_person") if isinstance(between, dict) else None
    if isinstance(question, dict) and not question.get("your_answer"):
        question["your_answer"] = T.PERSON[table] or "one row each"
        written += [f"the subject question={question['your_answer']}"]
    if written:
        questions.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8",
                             newline="\n")
    return written, left


@contextlib.contextmanager
def installed(folder: pathlib.Path) -> "Iterator[pathlib.Path]":
    """XDG_DATA_HOME and LOCALAPPDATA pointed at the run's own installation folder (the fixed test key, an empty record)."""
    place = folder / "installation"
    data = place / "synthtwin"
    if not data.exists():
        data.mkdir(parents=True, mode=0o700)
        (data / "chain-key").write_bytes(TEST_KEY)
        (data / "chain-ledger").write_text(_EMPTY_LEDGER, encoding="utf-8", newline="\n")
        if os.name != "nt":
            # Where the typed commands switch the chain on, they refuse a key or a record other accounts can
            # read (their remedy: chmod 600), so both are this account's alone, as
            # `twin_routes.installation_folder` makes them.
            data.chmod(0o700)
            (data / "chain-key").chmod(0o600)
            (data / "chain-ledger").chmod(0o600)
    saved = {name: os.environ.get(name) for name in ("XDG_DATA_HOME", "LOCALAPPDATA")}
    os.environ["XDG_DATA_HOME"] = str(place)
    os.environ["LOCALAPPDATA"] = str(place)
    try:
        yield place
    finally:
        for name, value in saved.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def command(argv: "list[str]", below_floor: bool) -> "tuple[int, str]":
    """One `synthtwin` command in this process: its exit code and the last of what it said (an error it raised: -1)."""
    from synthtwin import cli

    said = io.StringIO()
    try:
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(argv, small_tables_refused=not below_floor)
    except Exception as failure:  # noqa: BLE001 -- a command that raises is a result to record
        return -1, f"{type(failure).__name__}: {failure}"[:600]
    return int(code), said.getvalue()[-600:]


def replace_description_known() -> bool:
    """Whether the measured tree's `profile` takes `--replace-description` (a tree before the record has none)."""
    from synthtwin import cli

    return "--replace-description" in getattr(cli, "_RECORD_OPTIONS", ())


@dataclasses.dataclass
class Product:
    """What the shipped commands made of one table: a twin a seed (or why not), the answers, the seconds."""

    twins: "dict[int, str]"
    errors: "dict[int, str]"
    answered: "list[str]"
    left: "list[str]"
    held: "list[str]"
    relations: bool
    describe_seconds: float
    generate_seconds: float


def held_columns(page: pathlib.Path) -> "list[str]":
    """The columns the description's screen text says it holds as record numbers or codes, with the reason."""
    if not page.exists():
        return []
    lines = page.read_text(encoding="utf-8").splitlines()
    held: "list[str]" = []
    for i, line in enumerate(lines):
        if i and "read as:" in line and "record numbers" in line:
            held += [f"{lines[i - 1].strip()}: {line.split('read as:', 1)[1].strip()}"]
    return held


def linked_product(folder: pathlib.Path, table: str) -> "tuple[pathlib.Path, pathlib.Path, pathlib.Path]":
    """Where route S left a table's product: its installation's folder, its real table and its description."""
    source = folder / "table" / T.FILES[table]
    return folder, source, folder / "out" / f"{source.stem}-profile.json"


def make_twins(folder: pathlib.Path, table: str, text: str, twins: "tuple[int, ...]", below_floor: bool,
               linked: "tuple[pathlib.Path, pathlib.Path, pathlib.Path] | None" = None) -> Product:
    """Route S: profile, the truthful answers round by round, then generate at each twin seed.

    ``linked`` (lane W5-F14) is the product of the study's other table this
    one joins by its person column (`linked_product`: its installation's
    folder, its real table, its description): every `profile` round names
    that table with `--linked-to`, every `generate` names its description,
    and the commands run in its installation, where its description's
    private record stands, as one person's computer holds both.
    """
    started = time.perf_counter()
    source = folder / "table" / T.FILES[table]
    out = folder / "out"
    source.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    with open(source, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    stem = source.stem
    questions = out / f"{stem}-questions.json"
    description = out / f"{stem}-profile.json"
    answered: "list[str]" = []
    left: "list[str]" = []
    errors: "dict[int, str]" = {}
    made: "dict[int, str]" = {}
    home = folder if linked is None else linked[0]
    described_with = [] if linked is None else ["--linked-to", str(linked[1])]
    built_with = [] if linked is None else ["--linked-to", str(linked[2])]
    with installed(home):
        first = ["profile", str(source), "--out-dir", str(out), "--replace"] + described_with
        code, said = command(first, below_floor)
        if code != 0 and replace_description_known():
            # A table described before in this installation, its description publishing between columns, refuses a
            # different one in the record of earlier descriptions; the screen's remedy is the same run with
            # --replace-description, as the answered rounds below take it (a run made twice in one folder).
            code, said = command(first + ["--replace-description"], below_floor)
        for _round in range(ROUNDS):
            if code != 0:
                break
            written, left = answer_questions(questions, table)
            if not written:
                break
            answered += written
            again = ["profile", str(source), "--out-dir", str(out), "--answers", str(questions)] + described_with
            code, said = command(again, below_floor)
            if code != 0 and replace_description_known():
                # The record of earlier descriptions refuses an answered round that publishes relationships between
                # columns once an earlier round's description stands without them; the screen's remedy is the same
                # round with --replace-description, as route S does in `twin_routes._answered_rounds`.
                code, said = command(again + ["--replace-description"], below_floor)
        described = time.perf_counter() - started
        relations = False
        if code == 0 and description.exists():
            document = json.loads(description.read_text(encoding="utf-8"))
            manifest = document.get("relationships") if isinstance(document, dict) else None
            relations = isinstance(manifest, dict) and bool(manifest.get("statistical"))
        clock = time.perf_counter()
        for k in twins:
            if code != 0:
                errors[k] = f"synthtwin profile exited {code}: {said.strip()[-300:]}"
                continue
            done, words = command(["generate", str(description), "--out-dir", str(out), "--seed", str(k),
                                   "--replace"] + built_with, below_floor)
            twin = out / f"{stem}-twin.csv"
            if done != 0 or not twin.exists():
                errors[k] = f"synthtwin generate exited {done}: {words.strip()[-300:]}"
                continue
            made[k] = twin.read_text(encoding="utf-8")
    return Product(made, errors, answered, left, held_columns(out / f"{stem}-profile.txt"), relations, described,
                   time.perf_counter() - clock)


# -- one table at one seed --------------------------------------------------------------


@dataclasses.dataclass
class TableRun:
    """One table at one size and seed: every script on the real table, its halves and each side, and the product's notes."""

    table: str
    rows: int
    seed: int
    twins: "tuple[int, ...]"
    real: "dict[str, ScriptRun]"
    halves: "dict[str, list[ScriptRun]]"
    sides: "dict[str, dict[str, ScriptRun]]"
    product: "dict[str, object]"
    seconds: float


def run_side(folder: pathlib.Path, table: str, text: str, scripts: "list[Script]",
             extra: "dict[str, str]") -> "dict[str, ScriptRun]":
    """Every script of a table on one version of it, written in ``folder`` under its file name beside ``extra``."""
    folder.mkdir(parents=True, exist_ok=True)
    files = {T.FILES[table]: text}
    files.update(extra)
    for name, content in files.items():
        with open(folder / name, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
    found: "dict[str, ScriptRun]" = {}
    for script in scripts:
        if script.stem == "f14_join_cohort" and "cohort.csv" not in files:
            found[script.stem] = ScriptRun(False, "no cohort beside the orders", {}, {}, [])
            continue
        found[script.stem] = run_script(script.path, folder)
    shutil.rmtree(folder, ignore_errors=True)
    return found


def _extra(table: str, side: str, holdout: str, companions: "dict[str, str]") -> "dict[str, str]":
    if table == "T1":
        return {HOLDOUT_FILE: holdout}
    if table == "T5" and side in companions:
        return {"cohort.csv": companions[side]}
    if table == "T5" and side.startswith("half") and "real" in companions:
        return {"cohort.csv": companions["real"]}
    return {}


def run_table(table: str, rows: int, seed: int, twins: "tuple[int, ...]", folder: pathlib.Path,
              below_floor: bool = False, companions: "dict[str, str] | None" = None,
              keep: "dict[str, str] | None" = None, log: "object | None" = None) -> TableRun:
    """One table at one size and seed: the twin by route S, then every script on each version of the table.

    ``companions`` hands T5's scripts the cohort of the same side (the real
    cohort, its twin, its fresh sample, its shuffle), and ``keep`` (a dict)
    receives this table's own sides by name, which T1's run hands on.
    """
    started = time.perf_counter()
    folder.mkdir(parents=True, exist_ok=True)
    scripts = catalogue((table,))
    real_text = T.text(table, rows, seed)
    holdout = T.text("T1", rows, holdout_seed(seed)) if table == "T1" else ""
    companions = companions or {}
    # THE TWO TABLES OF ONE STUDY (lane W5-F14): T1's product is kept beside its folder for T5, whose route S names
    # T1's real table and description with `--linked-to` in T1's installation, as one person's computer holds both;
    # T5's run removes it.
    product_folder = folder / "product"
    if keep is not None and table == "T1":
        product_folder = folder.parent / f"{folder.name}-product"
    linked = None
    if table == "T5" and "product" in companions:
        linked = linked_product(pathlib.Path(companions["product"]), "T1")
    product = make_twins(product_folder, table, real_text, twins, below_floor, linked)
    if keep is not None and table == "T1":
        keep["product"] = str(product_folder)

    def say(words: str) -> None:
        if log is not None:
            print(f"{table} seed {seed}: {words}", file=log, flush=True)  # type: ignore[call-overload]

    say(f"described in {product.describe_seconds:.1f} s, {len(product.twins)} twin(s) in "
        f"{product.generate_seconds:.1f} s" + (f"; NOT MADE {product.errors}" if product.errors else ""))
    real = run_side(folder / "real", table, real_text, scripts, _extra(table, "real", holdout, companions))
    if keep is not None:
        keep["real"] = real_text
    halves: "dict[str, list[ScriptRun]]" = {script.stem: [] for script in scripts}
    for place, half in enumerate(halves_of(real_text, seed)):
        name = f"half-{'AB'[place % 2]}{place // 2}"
        found = run_side(folder / name, table, half, scripts, _extra(table, name, holdout, companions))
        for stem, run in found.items():
            halves[stem] += [run]
    sides: "dict[str, dict[str, ScriptRun]]" = {}
    for k in twins:
        versions = {
            f"twin-{k}": product.twins.get(k),
            f"replicate-{k}": T.text(table, rows, replicate_seed(seed, k)),
            f"shuffled-{k}": shuffled_text(real_text, seed * 31 + k),
        }
        for side, text in versions.items():
            if text is None:
                why = f"the twin was not made: {product.errors.get(k, 'unknown')}"
                sides[side] = {s.stem: ScriptRun(False, why, {}, {}, []) for s in scripts}
                continue
            sides[side] = run_side(folder / side, table, text, scripts, _extra(table, side, holdout, companions))
            if keep is not None:
                keep[side] = text
    say(f"scripts run in {time.perf_counter() - started:.1f} s")
    notes: "dict[str, object]" = {
        "answered": product.answered, "left_blank": product.left, "held": product.held,
        "relations_drawn": product.relations, "not_made": {str(k): v for k, v in product.errors.items()},
        "describe_seconds": round(product.describe_seconds, 1), "generate_seconds": round(product.generate_seconds, 1),
    }
    shutil.rmtree(folder, ignore_errors=True)
    if linked is not None:
        shutil.rmtree(linked[0], ignore_errors=True)
    return TableRun(table, rows, seed, tuple(twins), real, halves, sides, notes, time.perf_counter() - started)


def run_tables(tables: "tuple[str, ...]", rows: int, seeds: "tuple[int, ...]", twins: "tuple[int, ...]",
               folder: pathlib.Path, below_floor: bool = False, log: "object | None" = None) -> "list[TableRun]":
    """Every table at every seed; T1 first, so T5's join reads the cohort of the same side."""
    order = sorted(tables, key=lambda t: (t != "T1", t))
    out: "list[TableRun]" = []
    for seed in seeds:
        cohort: "dict[str, str]" = {}
        for table in order:
            out += [run_table(table, rows, seed, twins, folder / f"{table}-{seed}", below_floor,
                              companions=cohort if table == "T5" else None,
                              keep=cohort if table == "T1" else None, log=log)]
        # T1's product, kept for T5 (lane W5-F14), goes where no T5 ran to remove it.
        if "product" in cohort and "T5" not in tables:
            shutil.rmtree(cohort["product"], ignore_errors=True)
    return out


# -- the KPI ---------------------------------------------------------------------------


@dataclasses.dataclass
class Scored:
    """One script at one table seed and twin seed: the twin, the fresh sample and the shuffled table judged."""

    stem: str
    table: str
    family: str
    relation: bool
    seed: int
    twin: int
    sides: "dict[str, Judged]"
    real_ok: bool
    real_error: str


def score(run: TableRun) -> "list[Scored]":
    """Every script of a table run judged on each side at each twin seed."""
    out: "list[Scored]" = []
    for script in catalogue((run.table,)):
        real = run.real.get(script.stem) or ScriptRun(False, "not run", {}, {}, [])
        halves = run.halves.get(script.stem, [])
        yards = yardsticks(real, halves) if real.ok else {}
        real_every = real.every_estimate()
        yards_every = yardsticks(real_every, [half.every_estimate() for half in halves]) if real.ok else {}
        for k in run.twins:
            judged = {}
            for kind in ("twin", "replicate", "shuffled"):
                other = run.sides.get(f"{kind}-{k}", {}).get(script.stem) or ScriptRun(False, "not run", {}, {}, [])
                every = (real_every, yards_every, other.every_estimate())
                judged[kind] = judge(real, yards, other, every) if real.ok else Judged(
                    False, False, "the real run stopped", 0, 0, {})
            out += [Scored(script.stem, run.table, script.family, script.relation, run.seed, k, judged, real.ok,
                           real.error)]
    return out


def _share(numerator: int, denominator: int) -> "float | None":
    return None if denominator == 0 else round(numerator / denominator, 4)


def kpi_value(runs_: "list[TableRun]", suffix: str = "_20k",
              f0: "dict[str, object] | None" = None) -> "dict[str, object]":
    """K-RU-01's value from the table runs: runs, same and same_rel, family by family, with the controls."""
    scored = [s for run in runs_ for s in score(run)]
    counted = [s for s in scored if s.real_ok and s.family in HEADLINE_FAMILIES]
    families: "dict[str, dict[str, object]]" = {}
    void: "list[str]" = []
    for family in HEADLINE_FAMILIES:
        mine = [s for s in counted if s.family == family]
        if not mine:
            continue
        twin_pass = sum(s.sides["twin"].passed for s in mine)
        rep_pass = sum(s.sides["replicate"].passed for s in mine)
        families[family] = {
            "n": len(mine),
            "runs": _share(sum(s.sides["twin"].runs for s in mine), len(mine)),
            "twin": _share(twin_pass, len(mine)),
            "replicate": _share(rep_pass, len(mine)),
            "shuffled": _share(sum(s.sides["shuffled"].passed for s in mine), len(mine)),
        }
        if rep_pass < VOID_BELOW * len(mine):
            void += [family]
    kept = [s for s in counted if s.family not in void]
    same_twin = _share(sum(s.sides["twin"].passed for s in kept), len(kept))
    same_rep = _share(sum(s.sides["replicate"].passed for s in kept), len(kept))
    same_shuffled = _share(sum(s.sides["shuffled"].passed for s in kept), len(kept))
    relation = [s for s in counted if s.relation]
    shuffled_relation = _share(sum(s.sides["shuffled"].passed for s in relation), len(relation))
    invalid = shuffled_relation is not None and shuffled_relation > 0.5
    nulls = [s for s in scored if s.stem == NULL_SCRIPT and s.real_ok]
    twin_nulls = [s.sides["twin"].null_share for s in nulls if s.sides["twin"].null_share is not None]
    rep_nulls = [s.sides["replicate"].null_share for s in nulls if s.sides["replicate"].null_share is not None]
    structured = [s for s in counted if s.table != "T8"]

    def invented(kind: str) -> "float | None":
        quiet = sum(s.sides[kind].real_quiet for s in structured)
        loud = sum(s.sides[kind].made_loud for s in structured)
        return None if quiet == 0 else loud / quiet

    twin_invented, rep_invented = invented("twin"), invented("replicate")
    null_ok = bool(rep_nulls) and statistics.median(rep_nulls) <= NULL_AT_MOST
    value: "dict[str, object]" = {
        "runs" + suffix: _share(sum(s.sides["twin"].runs for s in counted), len(counted)),
        "same" + suffix: same_twin,
        "same_replicate" + suffix: same_rep,
        "same_shuffled" + suffix: same_shuffled,
        "same_rel" + suffix: None if same_twin is None or not same_rep else round(same_twin / same_rep, 4),
        "shuffled_relation_share" + suffix: shuffled_relation,
        "controls_hold" + suffix: (not invalid) and null_ok,
        "void_families" + suffix: void,
        "null_pairs_share" + suffix: round(statistics.median(twin_nulls), 4) if twin_nulls else None,
        "null_pairs_share_max" + suffix: round(max(twin_nulls), 4) if twin_nulls else None,
        "null_replicate_share" + suffix: round(statistics.median(rep_nulls), 4) if rep_nulls else None,
        "invented_points" + suffix: (None if twin_invented is None or rep_invented is None
                                     else round(100.0 * (twin_invented - rep_invented), 2)),
        "relations_drawn" + suffix: _share(sum(1 for r in runs_ if r.product.get("relations_drawn")), len(runs_)),
        "script_runs" + suffix: len(counted),
        "scripts" + suffix: len({s.stem for s in counted}),
        "families" + suffix: families,
    }
    joins = [s for s in scored if s.family in INFORMATIONAL and s.real_ok]
    if joins:
        value["F14_runs" + suffix] = _share(sum(s.sides["twin"].runs for s in joins), len(joins))
        value["F14_twin" + suffix] = _share(sum(s.sides["twin"].passed for s in joins), len(joins))
        value["F14_replicate" + suffix] = _share(sum(s.sides["replicate"].passed for s in joins), len(joins))
    if f0:
        value.update({key + suffix if not key.endswith(suffix) else key: v for key, v in f0.items()})
    return value


def extended_value(runs_: "list[TableRun]", suffix: str = "_20k") -> "dict[str, object]":
    """The extended battery's value (lane STATS-B) from the table runs: each family of `EXTENDED_FAMILIES` as K-RU-01's
    families are read (runs, twin, fresh sample, shuffled), its scripts' runs counted where the real run ends; a
    family whose fresh sample passes under `VOID_BELOW` is void and named; same_rel over the families not void."""
    scored = [s for run in runs_ for s in score(run)]
    counted = [s for s in scored if s.real_ok and s.family in EXTENDED_FAMILIES]
    families: "dict[str, dict[str, object]]" = {}
    void: "list[str]" = []
    for family in EXTENDED_FAMILIES:
        mine = [s for s in counted if s.family == family]
        if not mine:
            continue
        rep_pass = sum(s.sides["replicate"].passed for s in mine)
        families[family] = {
            "n": len(mine),
            "runs": _share(sum(s.sides["twin"].runs for s in mine), len(mine)),
            "twin": _share(sum(s.sides["twin"].passed for s in mine), len(mine)),
            "replicate": _share(rep_pass, len(mine)),
            "shuffled": _share(sum(s.sides["shuffled"].passed for s in mine), len(mine)),
        }
        if rep_pass < VOID_BELOW * len(mine):
            void += [family]
    kept = [s for s in counted if s.family not in void]
    same_twin = _share(sum(s.sides["twin"].passed for s in kept), len(kept))
    same_rep = _share(sum(s.sides["replicate"].passed for s in kept), len(kept))
    return {
        "extended_runs" + suffix: _share(sum(s.sides["twin"].runs for s in counted), len(counted)),
        "extended_same" + suffix: same_twin,
        "extended_same_replicate" + suffix: same_rep,
        "extended_same_rel" + suffix: None if same_twin is None or not same_rep else round(same_twin / same_rep, 4),
        "extended_same_shuffled" + suffix: _share(sum(s.sides["shuffled"].passed for s in kept), len(kept)),
        "extended_void_families" + suffix: void,
        "extended_script_runs" + suffix: len(counted),
        "extended_families" + suffix: families,
    }


def f0_from_ledger(ledger: "dict") -> "dict[str, object]":
    """F0 read from K-HZ-01's stamped value: the zoo's kinds that pass end to end, and the commit it was taken on."""
    entry = next((e for e in ledger.get("entries", []) if e.get("id") == "K-HZ-01"), None)
    if entry is None:
        return {}
    stamped = entry.get("value_at") or {}
    held = stamped.get("value") or {}
    passing, kinds = held.get("kinds_passing"), held.get("kinds_in_catalogue")
    if not finite(passing) or not finite(kinds) or not kinds:
        return {}
    return {"F0_twin": round(float(passing) / float(kinds), 4), "F0_kinds": int(kinds),
            "F0_from": f"K-HZ-01 on {stamped.get('commit', 'unknown')}"}


def reasons(runs_: "list[TableRun]") -> "dict[str, dict[str, int]]":
    """Why each script did not pass on the twin, counted over its runs: the first reason of each run."""
    found: "dict[str, dict[str, int]]" = {}
    for run in runs_:
        for s in score(run):
            judged = s.sides["twin"]
            if judged.passed or not s.real_ok:
                continue
            words = judged.why.split(":")[0] + ": " + judged.why.split(":", 1)[-1].strip()[:90]
            found.setdefault(s.stem, {})
            found[s.stem][words] = found[s.stem].get(words, 0) + 1
    return found


def run_to_dict(run: TableRun) -> "dict[str, object]":
    """A table run as plain data (a driver's child hands it back as JSON)."""
    return dataclasses.asdict(run)


def run_from_dict(data: "dict") -> TableRun:
    """The table run `run_to_dict` wrote."""

    def script_run(d: "dict") -> ScriptRun:
        return ScriptRun(bool(d["ok"]), str(d["error"]), dict(d["estimands"]), dict(d["checks"]),
                         list(d["trouble"]), float(d.get("seconds", 0.0)), dict(d.get("context", {})))

    return TableRun(
        str(data["table"]), int(data["rows"]), int(data["seed"]), tuple(data["twins"]),
        {k: script_run(v) for k, v in data["real"].items()},
        {k: [script_run(v) for v in vs] for k, vs in data["halves"].items()},
        {side: {k: script_run(v) for k, v in found.items()} for side, found in data["sides"].items()},
        dict(data["product"]), float(data["seconds"]))

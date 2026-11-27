"""Competing risks: the cumulative incidence of a readmission and of a death from another cause at a year (Aalen-Johansen, with its delta-method standard error) by treatment, and each cause's own Cox model (family F29, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def incidence_at(time, cause, day):
    """Aalen-Johansen: each cause's cumulative incidence at `day` (causes 1 and 2, 0 censored), with its delta-method
    variance (Marubini and Valsecchi, as Stata's stcompet and most texts give it)."""
    order = np.argsort(time, kind="mergesort")
    time, cause = time[order], cause[order]
    moments, first = np.unique(time, return_index=True)
    at_risk = (len(time) - first).astype(float)
    d1 = np.bincount(np.searchsorted(moments, time[cause == 1]), minlength=len(moments)).astype(float)
    d2 = np.bincount(np.searchsorted(moments, time[cause == 2]), minlength=len(moments)).astype(float)
    keep = moments <= day
    at_risk, d1, d2 = at_risk[keep], d1[keep], d2[keep]
    ended = d1 + d2
    free = np.cumprod(1.0 - ended / at_risk)
    before = np.concatenate([[1.0], free[:-1]])
    out = []
    left = at_risk - ended
    for events in (d1, d2):
        so_far = np.cumsum(before * events / at_risk)
        incidence = float(so_far[-1]) if len(so_far) else 0.0
        gap = incidence - so_far
        variance = float(np.sum(np.where(left > 0, gap * gap * ended / (at_risk * np.maximum(left, 1.0)), 0.0)
                                + before * before * events * (at_risk - events) / at_risk ** 3
                                - np.where(left > 0, 2.0 * gap * before * events * (at_risk - events)
                                           / (at_risk * at_risk * np.maximum(left, 1.0)), 0.0)))
        out += [incidence, variance]
    return tuple(out)


df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["exit_days"], errors="coerce"),
    "cause": df["exit_reason"].map({"readmitted": 1, "died": 2, "censored": 0}),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
checks["kept_rows"] = int(len(data))
outcomes = int((data["cause"] == 1).sum())
died_count = int((data["cause"] == 2).sum())
in_arms = int(min(((data["cause"] == 1) & (data["treated"] == 1)).sum(), ((data["cause"] == 1) & (data["treated"] == 0)).sum()))
died_in_arms = int(min(((data["cause"] == 2) & (data["treated"] == 1)).sum(),
                         ((data["cause"] == 2) & (data["treated"] == 0)).sum()))
treated = data[data["treated"] == 1]
untreated = data[data["treated"] == 0]
f1_t, v1_t, f2_t, v2_t = incidence_at(treated["time"].to_numpy(), treated["cause"].to_numpy(), 365)
f1_u, v1_u, f2_u, v2_u = incidence_at(untreated["time"].to_numpy(), untreated["cause"].to_numpy(), 365)
# The difference of two independent groups' incidences, with its standard error and normal p (lane STATS-D: before, no
# standard error was written and the battery's half-split yardstick, read on four splits, judged it).
for name, difference, variance, support, primary in (
        ("readmitted_by_a_year_treated_minus_not", f1_t - f1_u, v1_t + v1_u, in_arms, True),
        ("death_by_a_year_treated_minus_not", f2_t - f2_u, v2_t + v2_u, died_in_arms, False)):
    se = math.sqrt(variance)
    put(name, difference, se, math.erfc(abs(difference) / se / math.sqrt(2)), support, primary)
put("readmitted_by_a_year_untreated", f1_u, math.sqrt(v1_u), support=in_arms, judged=False)
for cause, name, support, primary in ((1, "readmission", in_arms, True), (2, "death", died_in_arms, False)):
    fit = smf.phreg("time ~ treated + age_c + diabetes", data=data,
                    status=(data["cause"] == cause).astype(int).to_numpy(), ties="breslow").fit()
    names = list(fit.model.exog_names)
    for term in ("treated", "age_c"):
        place = names.index(term)
        events = outcomes if cause == 1 else died_count
        put(f"{name}_cause_specific_{term}", fit.params[place], fit.bse[place], fit.pvalues[place],
            support if term == "treated" else events, primary and term == "treated")
put("died_of_another_cause", died_count, support=died_count, judged=False)
put("readmissions", outcomes, support=outcomes, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

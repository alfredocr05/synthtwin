"""Competing risks: the Fine-Gray model of a readmission's subdistribution hazard, a death from another cause kept in the risk set with censoring weights (family F29, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def censoring_survival(time, cause):
    """Kaplan-Meier of the censoring times, read just before each of `time` (G(t-))."""
    order = np.argsort(time, kind="mergesort")
    t, censored = time[order], (cause[order] == 0)
    moments = np.unique(t)
    at_risk = len(t) - np.searchsorted(t, moments, side="left")
    ended = np.array([censored[t == m].sum() for m in moments], dtype=float)
    survival = np.cumprod(1.0 - ended / at_risk)
    before = np.searchsorted(moments, time, side="left") - 1
    return np.where(before >= 0, survival[np.maximum(before, 0)], 1.0)


def fine_gray(time, cause, x, iterations=30):
    """Fine and Gray's estimator (Breslow ties): coefficients and model-based standard errors.

    At each time a readmission happens the risk set holds everyone still followed (weight 1) and everyone who died of
    another cause before it, weighted by the censoring curve then over the censoring curve at their death."""
    n, k = x.shape
    order = np.argsort(time, kind="mergesort")
    time, cause, x = time[order], cause[order], x[order]
    weight_at_exit = censoring_survival(time, cause)
    event_times = np.unique(time[cause == 1])
    moments = np.unique(time)
    at_risk = len(time) - np.searchsorted(time, moments, side="left")
    ended = np.array([((time == m) & (cause == 0)).sum() for m in moments], dtype=float)
    curve = np.cumprod(1.0 - ended / at_risk)
    place = np.searchsorted(moments, event_times, side="left") - 1
    g_event = np.where(place >= 0, curve[np.maximum(place, 0)], 1.0)
    first_at = np.searchsorted(time, event_times, side="left")
    tied = np.array([((time == m) & (cause == 1)).sum() for m in event_times], dtype=float)
    competing = cause == 2
    events_x = x[cause == 1].sum(axis=0)
    beta = np.zeros(k)
    information = np.eye(k)
    for _step in range(iterations):
        risk = np.exp(x @ beta)
        # those still followed at the event time: sums from its first row on
        s0_r = np.cumsum(risk[::-1])[::-1]
        s1_r = np.cumsum((risk[:, None] * x)[::-1], axis=0)[::-1]
        s2_r = np.cumsum((risk[:, None, None] * x[:, :, None] * x[:, None, :])[::-1], axis=0)[::-1]
        # those who died of another cause before it: sums up to its first row, each weighted 1 / G(T_i-)
        w = np.where(competing, risk / weight_at_exit, 0.0)
        s0_c = np.concatenate([[0.0], np.cumsum(w)])
        s1_c = np.concatenate([np.zeros((1, k)), np.cumsum(w[:, None] * x, axis=0)])
        s2_c = np.concatenate([np.zeros((1, k, k)), np.cumsum(w[:, None, None] * x[:, :, None] * x[:, None, :], axis=0)])
        s0 = s0_r[first_at] + g_event * s0_c[first_at]
        s1 = s1_r[first_at] + g_event[:, None] * s1_c[first_at]
        s2 = s2_r[first_at] + g_event[:, None, None] * s2_c[first_at]
        mean = s1 / s0[:, None]
        score = events_x - (tied[:, None] * mean).sum(axis=0)
        information = (tied[:, None, None] * (s2 / s0[:, None, None] - mean[:, :, None] * mean[:, None, :])).sum(axis=0)
        step = np.linalg.solve(information, score)
        beta = beta + step
        if np.max(np.abs(step)) < 1e-9:
            break
    return beta, np.sqrt(np.diag(np.linalg.inv(information)))


df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["exit_days"], errors="coerce"),
    "cause": df["exit_reason"].map({"readmitted": 1, "died": 2, "censored": 0}),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
checks["kept_rows"] = int(len(data))
terms = ["treated", "age_c", "diabetes"]
beta, se = fine_gray(data["time"].to_numpy(dtype=float), data["cause"].to_numpy(dtype=int),
                     data[terms].to_numpy(dtype=float))
outcomes = int((data["cause"] == 1).sum())
in_arms = int(min(((data["cause"] == 1) & (data["treated"] == 1)).sum(), ((data["cause"] == 1) & (data["treated"] == 0)).sum()))
for at, term in enumerate(terms):
    z = beta[at] / se[at]
    support = in_arms if term != "age_c" else outcomes
    put(f"subdistribution_{term}", beta[at], se[at], math.erfc(abs(z) / math.sqrt(2)), support, primary=term == "treated")
put("died_of_another_cause", int((data["cause"] == 2).sum()), support=int((data["cause"] == 2).sum()), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Tests without a model for trends and groups: Jonckheere-Terpstra's test of the stay across the ordered risk classes, Kendall's tau, Mann-Kendall's trend of the monthly admissions, Kruskal-Wallis by technique and Spearman's correlation (family F40, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "stay": pd.to_numeric(df["stay_days"], errors="coerce"),
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "technique": df["technique"],
    "age": pd.to_numeric(df["age"], errors="coerce"),
    "medicines": pd.to_numeric(df["n_medicines"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
    "admitted": pd.to_datetime(df["admit_date"], format="%Y-%m-%d", errors="coerce"),
}).dropna()
checks["kept_rows"] = int(len(data))
classes = sorted(data["risk_class"].unique())
groups = [data.loc[data["risk_class"] == c, "stay"].to_numpy() for c in classes]
smallest = int(min(len(g) for g in groups))
above, pairs = 0.0, 0.0
for i in range(len(groups)):
    for j in range(i + 1, len(groups)):
        ranked = stats.rankdata(np.concatenate([groups[i], groups[j]]))
        u = ranked[len(groups[i]):].sum() - len(groups[j]) * (len(groups[j]) + 1) / 2
        above += u
        pairs += len(groups[i]) * len(groups[j])
total = sum(len(g) for g in groups)
sizes = np.array([len(g) for g in groups], dtype=float)
mean = (total ** 2 - np.sum(sizes ** 2)) / 4
variance = (total ** 2 * (2 * total + 3) - np.sum(sizes ** 2 * (2 * sizes + 3))) / 72
z = (above - mean) / math.sqrt(variance)
put("jonckheere_later_class_longer", above / pairs, p=2 * stats.norm.sf(abs(z)), support=smallest, primary=True)
put("jonckheere_z", z, support=smallest, judged=False)
tau = stats.kendalltau(data["risk_class"], data["stay"])
put("kendall_tau_class_stay", tau.statistic, p=tau.pvalue, support=smallest)
by_month = data.groupby(data["admitted"].dt.to_period("M"))
volume = stats.kendalltau(np.arange(by_month.ngroups), by_month.size().to_numpy())
put("mann_kendall_monthly_admissions", volume.statistic, p=volume.pvalue, support=by_month.ngroups)
share = stats.kendalltau(np.arange(by_month.ngroups), by_month["complication"].mean().to_numpy())
put("mann_kendall_monthly_complication", share.statistic, p=share.pvalue, support=by_month.ngroups, judged=False)
by_technique = [g["stay"].to_numpy() for _, g in data.groupby("technique")]
h = stats.kruskal(*by_technique)
put("kruskal_technique_epsilon_squared", h.statistic / (len(data) - 1), p=h.pvalue,
    support=int(min(len(g) for g in by_technique)))
rho = stats.spearmanr(data["age"], data["medicines"])
put("spearman_age_medicines", rho.statistic, (1 - rho.statistic ** 2) / math.sqrt(len(data) - 3), rho.pvalue,
    len(data))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

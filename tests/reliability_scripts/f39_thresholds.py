"""Sensitivity and specificity at several thresholds: the cuff's reading against the arterial line's for a pressure of 140 or more (cuff cuts 130, 140 and 150), their likelihood ratios, and the risk score's cuts for the outcome (family F39, methods.csv)."""
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


def proportion(name, hits, total, support, primary=False, judged=True):
    share = hits / total
    put(name, share, math.sqrt(max(share * (1 - share), 1e-12) / total), support=support, primary=primary,
        judged=judged)
    return share


df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "arterial": pd.to_numeric(df["arterial_sbp"], errors="coerce"),
    "cuff": pd.to_numeric(df["cuff_sbp"], errors="coerce"),
    "score": pd.to_numeric(df["score"], errors="coerce"),
    "outcome": df["outcome"].eq("Y").astype(int),
}).dropna()
checks["kept_rows"] = int(len(data))
truth = data["arterial"] >= 140
diseased, healthy = int(truth.sum()), int((~truth).sum())
support = int(min(diseased, healthy))
for cut in (130, 140, 150):
    called = data["cuff"] >= cut
    sens = proportion(f"cuff_{cut}_sensitivity", int((called & truth).sum()), diseased, support, primary=(cut == 140))
    spec = proportion(f"cuff_{cut}_specificity", int((~called & ~truth).sum()), healthy, support)
    if 0 < spec < 1 and 0 < sens < 1:
        ratio = sens / (1 - spec)
        log_se = math.sqrt((1 - sens) / (sens * diseased) + spec / ((1 - spec) * healthy))
        put(f"cuff_{cut}_positive_likelihood_ratio_log", math.log(ratio), log_se, support=support,
            judged=(cut == 140))
    positives = int(called.sum())
    if positives:
        proportion(f"cuff_{cut}_positive_predictive_value", int((called & truth).sum()), positives, support,
                   judged=False)
youden = {cut: (data.loc[truth, "cuff"] >= cut).mean() + (data.loc[~truth, "cuff"] < cut).mean() - 1
          for cut in range(120, 171)}
put("cuff_best_cut_by_youden", max(youden, key=youden.get), support=support, judged=False)
events = int(data["outcome"].sum())
outcome_support = int(min(events, len(data) - events))
for cut in (3, 6):
    called = data["score"] >= cut
    proportion(f"score_{cut}_sensitivity", int((called & (data["outcome"] == 1)).sum()), events, outcome_support)
    proportion(f"score_{cut}_specificity", int((~called & (data["outcome"] == 0)).sum()), len(data) - events,
               outcome_support)
put("cuff_minus_arterial_mean", float(np.mean(data["cuff"] - data["arterial"])), support=len(data), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

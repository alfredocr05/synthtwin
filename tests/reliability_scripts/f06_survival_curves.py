"""Kaplan-Meier curves by complication and the log-rank test (family F6, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd
from statsmodels.duration.survfunc import SurvfuncRight, survdiff

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["fu_days"], errors="coerce"),
    "status": pd.to_numeric(df["died"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
}).dropna()
checks["kept_rows"] = int(len(data))


def survival_at(frame, day):
    curve = SurvfuncRight(frame["time"].to_numpy(), frame["status"].to_numpy())
    times = np.asarray(curve.surv_times)
    before = np.nonzero(times <= day)[0]
    if len(before) == 0:
        return 1.0, 0.0
    place = before[-1]
    return float(curve.surv_prob[place]), float(curve.surv_prob_se[place])


with_, without = data[data["complication"] == 1], data[data["complication"] == 0]
s1, e1 = survival_at(with_, 365)
s0, e0 = survival_at(without, 365)
se = math.sqrt(e1 ** 2 + e0 ** 2)
events = int(min(with_["status"].sum(), without["status"].sum()))
put("survival_year_difference", s1 - s0, se, 2 * (1 - 0.5 * (1 + math.erf(abs(s1 - s0) / se / math.sqrt(2)))),
    events, primary=True)
put("survival_year_with_complication", s1, e1, support=int(with_["status"].sum()))
put("survival_year_without_complication", s0, e0, support=int(without["status"].sum()))
s, e = survival_at(data, 730)
put("survival_two_years", s, e, support=int(data["status"].sum()), judged=False)
chi2, p = survdiff(data["time"].to_numpy(), data["status"].to_numpy(), data["complication"].to_numpy())
put("log_rank_chi_square", chi2, p=p, support=events, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

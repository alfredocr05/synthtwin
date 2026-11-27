"""Time to the outcome: Kaplan-Meier by treatment, a Cox model with the treatment's effect changing with age (family F24, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.duration.survfunc import SurvfuncRight, survdiff


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["outcome_days"], errors="coerce"),
    "status": df["outcome"].eq("Y").astype(int),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "score": pd.to_numeric(df["score"], errors="coerce"),
}).dropna()
checks["kept_rows"] = int(len(data))
fit = smf.phreg("time ~ treated * age_c + diabetes + score", data=data, status=data["status"].to_numpy(),
                ties="breslow").fit()
names = list(fit.model.exog_names)
events = int(data["status"].sum())
in_arms = int(min(data.loc[data["treated"] == 1, "status"].sum(), data.loc[data["treated"] == 0, "status"].sum()))
for term, support, primary in (("treated:age_c", in_arms, True), ("treated", in_arms, True), ("diabetes", events, False),
                               ("score", events, False)):
    place = names.index(term)
    put(term, fit.params[place], fit.bse[place], fit.pvalues[place], support, primary, primary)


def survival_at(frame, day):
    curve = SurvfuncRight(frame["time"].to_numpy(), frame["status"].to_numpy())
    times = np.asarray(curve.surv_times)
    before = np.nonzero(times <= day)[0]
    if len(before) == 0:
        return 1.0, 0.0
    return float(curve.surv_prob[before[-1]]), float(curve.surv_prob_se[before[-1]])


s1, e1 = survival_at(data[data["treated"] == 1], 365)
s0, e0 = survival_at(data[data["treated"] == 0], 365)
se = math.sqrt(e1 ** 2 + e0 ** 2)
put("free_at_a_year_treated_minus_not", s1 - s0, se, math.erfc(abs(s1 - s0) / se / math.sqrt(2)), in_arms)
chi2, p = survdiff(data["time"].to_numpy(), data["status"].to_numpy(), data["treated"].to_numpy())
put("log_rank_chi_square", chi2, p=p, support=in_arms, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

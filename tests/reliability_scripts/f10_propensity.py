"""Propensity score of diabetes, inverse probability weights, the weighted complication difference and balance (family F10, cohort.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "complication": df["complication"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "female": df["gender"].eq("F").astype(int),
    "weight_c": (pd.to_numeric(df["weight"], errors="coerce") - 84) / 15,
}).dropna()
checks["kept_complete_cases"] = int(len(data))
score = smf.glm("diabetes ~ age_c + female + weight_c", data=data, family=sm.families.Binomial()).fit()
p = score.predict(data).clip(0.01, 0.99)
weights = np.where(data["diabetes"] == 1, 1 / p, 1 / (1 - p))
put("score_age", score.params["age_c"], score.bse["age_c"], score.pvalues["age_c"],
    int(min(data["diabetes"].sum(), len(data) - data["diabetes"].sum())))
put("score_weight", score.params["weight_c"], score.bse["weight_c"], score.pvalues["weight_c"],
    int(min(data["diabetes"].sum(), len(data) - data["diabetes"].sum())))
outcome = smf.wls("complication ~ diabetes", data=data, weights=weights).fit(cov_type="HC0")
cells = pd.crosstab(data["diabetes"], data["complication"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
put("weighted_risk_difference", outcome.params["diabetes"], outcome.bse["diabetes"], outcome.pvalues["diabetes"],
    int(cells.to_numpy().min()), primary=True)
crude = smf.glm("complication ~ diabetes", data=data, family=sm.families.Binomial()).fit()
put("crude_log_odds", crude.params["diabetes"], crude.bse["diabetes"], crude.pvalues["diabetes"],
    int(cells.to_numpy().min()), judged=False)


def weighted_difference(column):
    treated, control = data["diabetes"] == 1, data["diabetes"] == 0
    mean_t = np.average(data.loc[treated, column], weights=weights[treated.to_numpy()])
    mean_c = np.average(data.loc[control, column], weights=weights[control.to_numpy()])
    spread = np.sqrt((data.loc[treated, column].var() + data.loc[control, column].var()) / 2)
    return (mean_t - mean_c) / spread


put("balance_age_after_weighting", weighted_difference("age_c"), support=int(data["diabetes"].sum()), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

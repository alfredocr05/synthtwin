"""A parametric survival model: exponential death rates by Poisson regression with the log follow-up as offset (family F6, cohort.csv)."""
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
    "time": pd.to_numeric(df["fu_days"], errors="coerce"),
    "status": pd.to_numeric(df["died"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
}).dropna()
data = data[data["time"] > 0]
fit = smf.glm("status ~ age_c + risk_class + complication", data=data, family=sm.families.Poisson(),
              offset=np.log(data["time"] / 365.25)).fit()
events = int(data["status"].sum())
low = int(min(data.loc[data["complication"] == 1, "status"].sum(), data.loc[data["complication"] == 0, "status"].sum()))
for term, support, primary in (("complication", low, True), ("age_c", events, False), ("risk_class", events, False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
put("death_rate_per_year_log", np.log(events / (data["time"].sum() / 365.25)), 1 / np.sqrt(events), support=events)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

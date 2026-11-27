"""Generalised estimating equations on a yes/no outcome over visits: hospitalisation on pressure and arm under a first-order autoregressive working correlation (family F27, visits.csv)."""
import json

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

df = pd.read_csv("visits.csv")
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "hospitalized": df["hospitalized"].eq("Y").astype(int),
    "sbp_c": (pd.to_numeric(df["sbp"], errors="coerce") - 138) / 10,
    "arm_a": df["arm"].eq("A").astype(int),
    "visit": pd.to_numeric(df["visit"], errors="coerce"),
}).dropna().sort_values(["patient_id", "visit"])
data["order"] = data.groupby("patient_id").cumcount()
fit = smf.gee("hospitalized ~ sbp_c + arm_a", groups="patient_id", data=data, time=data["order"].to_numpy(),
              family=sm.families.Binomial(), cov_struct=sm.cov_struct.Autoregressive(grid=True)).fit()
people_with = data.groupby("patient_id")["hospitalized"].max()
support = int(min(people_with.sum(), len(people_with) - people_with.sum()))
for term, primary in (("sbp_c", True), ("arm_a", False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
put("working_correlation", float(fit.model.cov_struct.dep_params), support=support, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

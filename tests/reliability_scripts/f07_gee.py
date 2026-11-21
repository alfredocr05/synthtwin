"""Generalised estimating equations: hospitalisation on pressure and arm, exchangeable within patient (family F7, visits.csv)."""
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
fit = smf.gee("hospitalized ~ sbp_c + arm_a", groups="patient_id", data=data, family=sm.families.Binomial(),
              cov_struct=sm.cov_struct.Exchangeable()).fit()
people_with = data.groupby("patient_id")["hospitalized"].max()
support = int(min(people_with.sum(), len(people_with) - people_with.sum()))
for term, primary in (("sbp_c", True), ("arm_a", False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
put("within_patient_correlation", fit.model.cov_struct.dep_params, support=support, judged=False)
share = data["hospitalized"].mean()
put("hospitalized_share", share, support=int(data["hospitalized"].sum()), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

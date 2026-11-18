"""Random-slope model: each patient's own trajectory, and the trend by arm (family F7, visits.csv)."""
import json

import pandas as pd
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
    "sbp": pd.to_numeric(df["sbp"], errors="coerce"),
    "visit": (pd.to_numeric(df["visit"], errors="coerce") - 1) / 10,
    "arm_b": df["arm"].eq("B").astype(int),
}).dropna()
fit = smf.mixedlm("sbp ~ visit * arm_b", data=data, groups=data["patient_id"], re_formula="~visit").fit(
    reml=True, method=["lbfgs"])
people = data["patient_id"].nunique()
arms = data.groupby("patient_id")["arm_b"].first()
in_arms = int(min(arms.sum(), people - arms.sum()))
for term, primary, judged in (("visit:arm_b", True, True), ("visit", False, True), ("arm_b", False, False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], in_arms if "arm" in term else people, primary, judged)
put("slope_sd", max(float(fit.cov_re.iloc[1, 1]), 0.0) ** 0.5, support=people, judged=False)
put("intercept_sd", max(float(fit.cov_re.iloc[0, 0]), 0.0) ** 0.5, support=people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

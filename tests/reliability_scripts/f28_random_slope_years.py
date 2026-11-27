"""A mixed model with a random intercept and a random slope over the years since a patient's first visit, the arm's change a year and the slopes' spread (family F28, visits.csv)."""
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
df["visit_date"] = pd.to_datetime(df["visit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_visit_date"] = float(df["visit_date"].isna().mean())
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "sbp": pd.to_numeric(df["sbp"], errors="coerce"),
    "years": (df["visit_date"] - df.groupby("patient_id")["visit_date"].transform("min")).dt.days / 365.25,
    "arm_b": df["arm"].eq("B").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
}).dropna()
fit = smf.mixedlm("sbp ~ years * arm_b + age_c", data=data, groups=data["patient_id"], re_formula="~years").fit(
    reml=True, method=["lbfgs"])
people = data["patient_id"].nunique()
arms = data.groupby("patient_id")["arm_b"].first()
in_arms = int(min(arms.sum(), people - arms.sum()))
for term, primary in (("years:arm_b", True), ("years", False), ("age_c", False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], in_arms if "arm" in term else people, primary)
put("slope_sd", max(float(fit.cov_re.iloc[1, 1]), 0.0) ** 0.5, support=people)
put("intercept_sd", max(float(fit.cov_re.iloc[0, 0]), 0.0) ** 0.5, support=people)
put("residual_sd", float(fit.scale) ** 0.5, support=people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

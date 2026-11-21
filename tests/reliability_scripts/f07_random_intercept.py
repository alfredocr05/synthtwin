"""Random-intercept model of systolic pressure over visits, and the intraclass correlation (family F7, visits.csv)."""
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
    "visit": pd.to_numeric(df["visit"], errors="coerce") - 1,
    "arm_b": df["arm"].eq("B").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
}).dropna()
fit = smf.mixedlm("sbp ~ visit + arm_b + age_c", data=data, groups=data["patient_id"]).fit(reml=True)
people = data["patient_id"].nunique()
between = float(fit.cov_re.iloc[0, 0])
put("intraclass_correlation", between / (between + fit.scale), support=people, primary=True)
for term, judged in (("arm_b", True), ("visit", False), ("age_c", False)):
    support = people if term != "arm_b" else int(min(data.groupby("patient_id")["arm_b"].first().sum(),
                                                     people - data.groupby("patient_id")["arm_b"].first().sum()))
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, judged=judged)
put("residual_sd", fit.scale ** 0.5, support=people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

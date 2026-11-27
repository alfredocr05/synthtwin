"""Each patient's last pressure on the first and the arm, an analysis of covariance (family F7, visits.csv)."""
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
df["visit"] = pd.to_numeric(df["visit"], errors="coerce")
df["sbp"] = pd.to_numeric(df["sbp"], errors="coerce")
ordered = df.dropna(subset=["visit", "sbp"]).sort_values(["patient_id", "visit"])
patients = ordered.groupby("patient_id").agg(first=("sbp", "first"), last=("sbp", "last"),
                                             visits=("sbp", "size"), arm=("arm", "first"))
patients = patients[patients["visits"] >= 2]
patients["arm_b"] = patients["arm"].eq("B").astype(int)
checks["kept_two_visits_or_more"] = int(len(patients))
fit = smf.ols("last ~ first + arm_b + visits", data=patients).fit()
in_arms = int(min(patients["arm_b"].sum(), len(patients) - patients["arm_b"].sum()))
for term, support, primary, judged in (("arm_b", in_arms, True, True), ("first", len(patients), False, True),
                                       ("visits", len(patients), False, False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary, judged)
change = patients["last"] - patients["first"]
put("mean_change", change.mean(), change.std() / len(change) ** 0.5, support=len(change), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

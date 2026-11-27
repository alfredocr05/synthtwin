"""Quantile regression: the median and the ninetieth percentile of the length of stay on age, a complication and diabetes (family F34, cohort.csv)."""
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


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "stay": pd.to_numeric(df["stay_days"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "complication": df["complication"].eq("Y").astype(int),
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
checks["kept_rows"] = int(len(data))
groups = {term: int(min(data[term].sum(), len(data) - data[term].sum())) for term in ("complication", "diabetes")}
groups["age_c"] = len(data)
for q, label in ((0.5, "median"), (0.9, "p90")):
    fit = smf.quantreg("stay ~ age_c + complication + diabetes", data=data).fit(q=q, max_iter=5000)
    for term in ("complication", "diabetes", "age_c"):
        put(f"{label}_{term}", fit.params[term], fit.bse[term], fit.pvalues[term], groups[term],
            primary=(label == "median" and term == "complication"))
    put(f"{label}_intercept", fit.params["Intercept"], fit.bse["Intercept"], support=len(data), judged=False)
put("median_stay", data["stay"].median(), support=len(data), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

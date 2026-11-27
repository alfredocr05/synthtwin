"""Multinomial logistic regression: the second reader's grade in three classes (none, mild, moderate or worse) on age and diabetes (family F25, methods.csv)."""
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

df = pd.read_csv("methods.csv")
codes = {"none": 0, "mild": 1, "moderate": 2, "severe": 2}
data = pd.DataFrame({
    "grade": df["grade_second"].str.strip().str.lower().map(codes),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
checks["kept_known_grades"] = int(len(data))
fit = smf.mnlogit("grade ~ age_c + diabetes", data=data).fit(disp=0, maxiter=200)
counts = data["grade"].value_counts()
for column, label in ((0, "mild"), (1, "moderate_or_worse")):
    level = column + 1
    cells = pd.crosstab(data["grade"], data["diabetes"]).reindex(index=[0, level], columns=[0, 1], fill_value=0)
    for term in ("diabetes", "age_c"):
        support = int(cells.to_numpy().min()) if term == "diabetes" else int(min(counts.get(0, 0), counts.get(level, 0)))
        put(f"{label}_{term}", fit.params.loc[term, column], fit.bse.loc[term, column], fit.pvalues.loc[term, column],
            support, primary=(label == "moderate_or_worse" and term == "diabetes"))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

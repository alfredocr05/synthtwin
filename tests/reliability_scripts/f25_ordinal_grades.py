"""Proportional odds: the first reader's grade of a finding (none, mild, moderate, severe) on age, diabetes and body-mass index (family F25, methods.csv)."""
import json

import pandas as pd
from scipy import stats
from statsmodels.miscmodels.ordinal_model import OrderedModel


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
grades = ["none", "mild", "moderate", "severe"]
data = pd.DataFrame({
    "grade": df["grade_first"].str.strip().str.lower(),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "mass_c": (pd.to_numeric(df["body_mass_index"], errors="coerce") - 28) / 5,
}).dropna()
data = data[data["grade"].isin(grades)]
checks["kept_known_grades"] = int(len(data))
codes = data["grade"].map({grade: place for place, grade in enumerate(grades)}).astype(int)
outcome = pd.Categorical(codes, categories=[0, 1, 2, 3], ordered=True).remove_unused_categories()
fit = OrderedModel(outcome, data[["age_c", "diabetes", "mass_c"]], distr=stats.logistic).fit(method="bfgs", disp=False,
                                                                                            maxiter=300)
smallest = int(data["grade"].value_counts().min())
for term, primary in (("diabetes", True), ("age_c", False), ("mass_c", False)):
    support = int(min(smallest, data[term].sum(), len(data) - data[term].sum())) if term == "diabetes" else smallest
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
share = data["grade"].isin(["moderate", "severe"]).mean()
put("share_moderate_or_worse", share, (share * (1 - share) / len(data)) ** 0.5, support=smallest, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Proportional-odds model of the physical-status class (family F13, cohort.csv)."""
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


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "hypertension": df["hypertension"].eq("Y").astype(int),
    "weight_c": (pd.to_numeric(df["weight"], errors="coerce") - 84) / 15,
}).dropna()
data = data[data["risk_class"].isin([1, 2, 3, 4, 5])]
checks["kept_classes_1_to_5"] = int(len(data))
outcome = pd.Categorical(data["risk_class"].astype(int), categories=[1, 2, 3, 4, 5], ordered=True)
outcome = outcome.remove_unused_categories()
fit = OrderedModel(outcome, data[["age_c", "diabetes", "hypertension", "weight_c"]], distr=stats.logistic).fit(
    method="bfgs", disp=False, maxiter=300)
smallest = int(data["risk_class"].value_counts().min())
for term, primary in (("diabetes", True), ("age_c", False), ("hypertension", False), ("weight_c", None)):
    if term in ("diabetes", "hypertension"):
        support = int(min(smallest, data[term].sum(), len(data) - data[term].sum()))
    else:
        support = smallest
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, bool(primary), primary is not None)
share = (data["risk_class"] >= 3).mean()
put("share_class_3_or_more", share, (share * (1 - share) / len(data)) ** 0.5, support=smallest, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

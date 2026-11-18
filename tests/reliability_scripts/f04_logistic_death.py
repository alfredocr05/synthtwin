"""Logistic regression of death within a year, among patients followed a year or who died (family F4, cohort.csv)."""
import json

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
follow = pd.to_numeric(df["fu_days"], errors="coerce")
died = pd.to_numeric(df["died"], errors="coerce")
known = (follow >= 365) | ((died == 1) & (follow < 365))
data = pd.DataFrame({
    "death_year": ((died == 1) & (follow < 365)).astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
    "diabetes": df["diabetes"].eq("Y").astype(int),
})[known].dropna()
checks["kept_followed_a_year"] = int(len(data))
fit = smf.glm("death_year ~ age_c + risk_class + complication + diabetes", data=data,
              family=sm.families.Binomial()).fit()
events = data["death_year"]
limit = int(min(events.sum(), len(events) - events.sum()))


def cells(column):
    table = pd.crosstab(data[column], events).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    return int(table.to_numpy().min())


for term, support, primary, judged in (
    ("complication", cells("complication"), True, True),
    ("age_c", limit, False, True),
    ("risk_class", limit, False, True),
    ("diabetes", cells("diabetes"), False, False),
):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary, judged)
put("auc", roc_auc_score(events, fit.predict(data)), support=limit, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

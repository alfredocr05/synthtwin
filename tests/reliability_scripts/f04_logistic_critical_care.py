"""Logistic regression of intensive care after a case, on its duration, class and emergency (family F4, cases.csv)."""
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


df = pd.read_csv("cases.csv")
incision = pd.to_datetime(df["incision"], format="%Y-%m-%d %H:%M", errors="coerce")
close = pd.to_datetime(df["close"], format="%Y-%m-%d %H:%M", errors="coerce")
data = pd.DataFrame({
    "critical_care": df["critical_care"].eq("Y").astype(int),
    "hours": (close - incision).dt.total_seconds() / 3600,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "emergency": df["emergency"].eq("Y").astype(int),
}).dropna()
fit = smf.glm("critical_care ~ hours + risk_class + emergency", data=data, family=sm.families.Binomial()).fit()
events = data["critical_care"]
limit = int(min(events.sum(), len(events) - events.sum()))
cells = pd.crosstab(data["emergency"], events).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
for term, support, primary in (("hours", limit, True), ("risk_class", limit, False),
                               ("emergency", int(cells.to_numpy().min()), False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
put("auc", roc_auc_score(events, fit.predict(data)), support=limit, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

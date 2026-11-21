"""Logistic regression of the complication: odds ratios, an interaction, a curved age, the AUC (family F4, cohort.csv)."""
import json

import numpy as np
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
creat = pd.to_numeric(df["creat"].astype("string").str.replace("<", "", regex=False), errors="coerce")
creat = creat.where(~df["creat"].astype("string").str.startswith("<").fillna(False), creat / 2)
data = pd.DataFrame({
    "complication": df["complication"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "smoker": df["smoker"].eq("Y").astype(int),
    "female": df["gender"].eq("F").astype(int),
    "creat_high": (creat > 1.3).astype(int),
}).dropna()
data["age_c2"] = data["age_c"] ** 2
checks["unparsed_creat"] = float(creat.isna().mean())
fit = smf.glm("complication ~ age_c + age_c2 + risk_class + diabetes * smoker + creat_high + female",
              data=data, family=sm.families.Binomial()).fit()
events = data["complication"]


def cells(column):
    table = pd.crosstab(data[column], events).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    return int(table.to_numpy().min())


limit = int(min(events.sum(), len(events) - events.sum()))
for term, support, primary, judged in (
    ("diabetes", cells("diabetes"), True, True),
    ("risk_class", limit, True, True),
    ("diabetes:smoker", int(((data["diabetes"] * data["smoker"]) * events).sum()), False, True),
    ("age_c2", limit, False, True),
    ("age_c", limit, False, False),
    ("smoker", cells("smoker"), False, False),
    ("creat_high", cells("creat_high"), False, False),
    ("female", cells("female"), False, False),
):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary, judged)
put("auc", roc_auc_score(events, fit.predict(data)), support=limit, judged=False)
put("events_share", events.mean(), np.sqrt(events.mean() * (1 - events.mean()) / len(events)), support=limit,
    judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

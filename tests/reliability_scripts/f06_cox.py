"""Cox proportional hazards model of death (family F6, cohort.csv)."""
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
    "time": pd.to_numeric(df["fu_days"], errors="coerce"),
    "status": pd.to_numeric(df["died"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
fit = smf.phreg("time ~ age_c + risk_class + complication + diabetes", data=data, status=data["status"].to_numpy(),
                ties="breslow").fit()
names = list(fit.model.exog_names)
events = int(data["status"].sum())


def events_in(column):
    return int(min(data.loc[data[column] == 1, "status"].sum(), data.loc[data[column] == 0, "status"].sum()))


for term, support, primary in (
    ("complication", events_in("complication"), True),
    ("age_c", events, False),
    ("risk_class", events, False),
    ("diabetes", events_in("diabetes"), False),
):
    place = names.index(term)
    put(term, fit.params[place], fit.bse[place], fit.pvalues[place], support, primary)
checks["rows_used"] = int(len(data))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

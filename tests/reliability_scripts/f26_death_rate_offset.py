"""Rates over follow-up: those who died per person-year by age, diabetes and complication, a Poisson model with the follow-up as an offset and robust errors, and a negative binomial beside it (family F26, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
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
    "died": pd.to_numeric(df["died"], errors="coerce"),
    "years": pd.to_numeric(df["fu_days"], errors="coerce") / 365.25,
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "complication": df["complication"].eq("Y").astype(int),
}).dropna()
data = data[data["years"] > 0]
checks["kept_rows"] = int(len(data))
offset = np.log(data["years"].to_numpy())
poisson = smf.glm("died ~ age_c + diabetes + complication", data=data, offset=offset,
                  family=sm.families.Poisson()).fit(cov_type="HC0")
died_count = int(data["died"].sum())
for term, primary in (("complication", True), ("diabetes", False), ("age_c", False)):
    if term == "age_c":
        support = died_count
    else:
        support = int(min(data.loc[data[term] == 1, "died"].sum(), data.loc[data[term] == 0, "died"].sum()))
    put(f"rate_ratio_log_{term}", poisson.params[term], poisson.bse[term], poisson.pvalues[term], support, primary)
crude = died_count / data["years"].sum()
put("died_per_person_year", crude, math.sqrt(died_count) / data["years"].sum(), support=died_count, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Linear regression of the log length of stay, with an interaction and a squared age (family F3, cohort.csv)."""
import json

import numpy as np
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
    "log_stay": np.log(pd.to_numeric(df["stay_days"], errors="coerce")),
    "age_c": pd.to_numeric(df["age"], errors="coerce") - 57,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "smoker": df["smoker"].eq("Y").astype(int),
    "complication": df["complication"].eq("Y").astype(int),
})
for level in ("PG02", "PG03", "PG04"):
    data["group_" + level] = df["proc_group"].eq(level).astype(int)
data = data.dropna()
data["age_c2"] = data["age_c"] ** 2
fit = smf.ols("log_stay ~ age_c + age_c2 + risk_class + diabetes * smoker + complication + group_PG02 + group_PG03"
              " + group_PG04", data=data).fit()


def binary_support(column):
    return min(data[column].sum(), len(data) - data[column].sum())


for term, support, primary, judged in (
    ("complication", binary_support("complication"), True, True),
    ("risk_class", len(data), True, True),
    ("diabetes", binary_support("diabetes"), False, True),
    ("group_PG04", binary_support("group_PG04"), False, True),
    ("age_c", len(data), False, False),
    ("age_c2", len(data), False, False),
    ("smoker", binary_support("smoker"), False, False),
    ("diabetes:smoker", int((data["diabetes"] * data["smoker"]).sum()), False, False),
    ("group_PG02", binary_support("group_PG02"), False, False),
    ("group_PG03", binary_support("group_PG03"), False, False),
):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary, judged)
put("r_squared", fit.rsquared, support=len(data), judged=False)
checks["rows_used"] = int(fit.nobs)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

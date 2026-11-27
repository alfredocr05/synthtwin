"""Counts over observed times of different lengths: negative binomial and Poisson rates with the observed time as an offset (family F21, methods.csv)."""
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

df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "admissions": pd.to_numeric(df["admissions"], errors="coerce"),
    "years": pd.to_numeric(df["exposure_days"], errors="coerce") / 365.0,
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
data = data[data["years"] > 0]
checks["kept_rows"] = int(len(data))
offset = np.log(data["years"].to_numpy())
negative = smf.negativebinomial("admissions ~ treated + age_c + diabetes", data=data, offset=offset).fit(disp=0,
                                                                                                        maxiter=200)
for term, primary in (("treated", True), ("diabetes", False), ("age_c", False)):
    support = len(data) if term == "age_c" else int(min(data[term].sum(), len(data) - data[term].sum()))
    put(f"rate_{term}", negative.params[term], negative.bse[term], negative.pvalues[term], support, primary)
put("dispersion_alpha", negative.params["alpha"], negative.bse["alpha"], support=len(data), judged=False)
poisson = smf.glm("admissions ~ treated + age_c + diabetes", data=data, offset=offset,
                  family=sm.families.Poisson()).fit(cov_type="HC0")
put("poisson_rate_treated", poisson.params["treated"], poisson.bse["treated"], poisson.pvalues["treated"],
    int(min(data["treated"].sum(), len(data) - data["treated"].sum())), judged=False)
rate = data["admissions"].sum() / data["years"].sum()
put("crude_rate_a_year", rate, math.sqrt(data["admissions"].sum()) / data["years"].sum(), support=len(data),
    judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

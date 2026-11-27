"""Count regression of the number of medicines: Poisson with robust errors, negative binomial (family F5, cohort.csv)."""
import json
import math

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
    "n_medicines": pd.to_numeric(df["n_medicines"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "hypertension": df["hypertension"].eq("Y").astype(int),
}).dropna()
poisson = smf.glm("n_medicines ~ age_c + diabetes + hypertension", data=data, family=sm.families.Poisson()).fit(cov_type="HC0")
for term, primary in (("diabetes", True), ("hypertension", False), ("age_c", False)):
    support = len(data) if term == "age_c" else int(min(data[term].sum(), len(data) - data[term].sum()))
    put("poisson_" + term, poisson.params[term], poisson.bse[term], poisson.pvalues[term], support, primary)
negative = smf.negativebinomial("n_medicines ~ age_c + diabetes + hypertension", data=data).fit(disp=0)
put("negative_binomial_diabetes", negative.params["diabetes"], negative.bse["diabetes"],
    negative.pvalues["diabetes"], int(min(data["diabetes"].sum(), len(data) - data["diabetes"].sum())), judged=False)
put("dispersion_alpha", negative.params["alpha"], negative.bse["alpha"], support=len(data), judged=False)
zero = (data["n_medicines"] == 0).mean()
put("zero_share", zero, math.sqrt(zero * (1 - zero) / len(data)), support=int((data["n_medicines"] == 0).sum()),
    judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

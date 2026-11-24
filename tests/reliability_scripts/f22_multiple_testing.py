"""Many factors screened against one outcome, each p adjusted for the number of tests (Holm, Benjamini-Hochberg) (family F22, cohort.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("cohort.csv")
creat = pd.to_numeric(df["creat"].astype("string").str.replace("<", "", regex=False), errors="coerce")
data = pd.DataFrame({
    "complication": df["complication"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "female": df["gender"].eq("F").astype(int),
    "weight_c": (pd.to_numeric(df["weight"], errors="coerce") - 84) / 15,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "hypertension": df["hypertension"].eq("Y").astype(int),
    "smoker": df["smoker"].eq("Y").astype(int),
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "creat_high": (creat > 1.3).astype(int),
    "regional": df["technique"].eq("RA").astype(int),
    "sedation": df["technique"].eq("SED").astype(int),
    "group_02": df["proc_group"].eq("PG02").astype(int),
    "group_03": df["proc_group"].eq("PG03").astype(int),
    "group_05": df["proc_group"].eq("PG05").astype(int),
    "medicines_c": pd.to_numeric(df["n_medicines"], errors="coerce") / 5,
})
factors = [name for name in data.columns if name != "complication"]
found = []
for factor in factors:
    part = data[["complication", factor]].dropna()
    fit = smf.glm(f"complication ~ {factor}", data=part, family=sm.families.Binomial()).fit()
    if set(part[factor].unique()) <= {0, 1}:
        table = pd.crosstab(part[factor], part["complication"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
        support = int(table.to_numpy().min())
    else:
        support = int(min(part["complication"].sum(), len(part) - part["complication"].sum()))
    found += [(factor, fit.params[factor], fit.bse[factor], fit.pvalues[factor], support)]
raw = np.array([p for _f, _e, _s, p, _n in found])
holm = multipletests(raw, alpha=0.05, method="holm")[1]
hochberg = multipletests(raw, alpha=0.05, method="fdr_bh")[1]
for at, (factor, estimate, se, _p, support) in enumerate(found):
    # The conclusions judged: the true factor of the largest effect and two true nulls (a twin must not make them
    # discoveries); every other factor's adjusted test is read as context.
    put(f"{factor}_holm", estimate, se, holm[at], support, primary=factor == "diabetes",
        judged=factor in ("diabetes", "female", "group_03"))
    put(f"{factor}_bh", estimate, se, hochberg[at], support, judged=False)
put("discoveries_holm", int((holm < 0.05).sum()), support=len(data), judged=False)
put("discoveries_bh", int((hochberg < 0.05).sum()), support=len(data), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

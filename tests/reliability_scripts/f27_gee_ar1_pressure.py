"""Generalised estimating equations on the pressure over visits: the arm's change a visit under a first-order autoregressive and an exchangeable working correlation (family F27, visits.csv)."""
import json

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

df = pd.read_csv("visits.csv")
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "sbp": pd.to_numeric(df["sbp"], errors="coerce"),
    "visit": pd.to_numeric(df["visit"], errors="coerce"),
    "arm_b": df["arm"].eq("B").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
}).dropna().sort_values(["patient_id", "visit"])
data["order"] = data.groupby("patient_id").cumcount()
data["visit_c"] = data["order"] / 10
people = data["patient_id"].nunique()
arms = data.groupby("patient_id")["arm_b"].first()
in_arms = int(min(arms.sum(), people - arms.sum()))
for name, structure in (("ar1", sm.cov_struct.Autoregressive(grid=True)), ("exchangeable", sm.cov_struct.Exchangeable())):
    fit = smf.gee("sbp ~ visit_c * arm_b + age_c", groups="patient_id", data=data, time=data["order"].to_numpy(),
                  cov_struct=structure, family=sm.families.Gaussian()).fit()
    for term, primary, judged in (("visit_c:arm_b", name == "ar1", True), ("visit_c", False, True),
                                  ("age_c", False, name == "ar1")):
        put(f"{name}_{term}", fit.params[term], fit.bse[term], fit.pvalues[term], in_arms if "arm" in term else people,
            primary, judged)
    put(f"{name}_working_correlation", float(fit.model.cov_struct.dep_params), support=people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

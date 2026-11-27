"""Counts per patient over the visits each one had: hospitalisations per visit by arm and the patient's mean pressure, a negative binomial model with the log number of visits as an offset (family F26, visits.csv)."""
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

df = pd.read_csv("visits.csv")
rows = pd.DataFrame({
    "patient_id": df["patient_id"],
    "hosp": df["hospitalized"].eq("Y").astype(int),
    "sbp": pd.to_numeric(df["sbp"], errors="coerce"),
    "arm_a": df["arm"].eq("A").astype(int),
}).dropna()
people = rows.groupby("patient_id").agg(stays=("hosp", "sum"), visits=("hosp", "size"), mean_sbp=("sbp", "mean"),
                                        arm_a=("arm_a", "first"))
people["sbp_c"] = (people["mean_sbp"] - 138) / 10
checks["kept_patients"] = int(len(people))
offset = np.log(people["visits"].to_numpy(dtype=float))
fit = smf.negativebinomial("stays ~ arm_a + sbp_c", data=people, offset=offset).fit(disp=0, maxiter=200)
in_arms = int(min(people["arm_a"].sum(), len(people) - people["arm_a"].sum()))
put("rate_ratio_log_arm_a", fit.params["arm_a"], fit.bse["arm_a"], fit.pvalues["arm_a"], in_arms, primary=True)
put("rate_ratio_log_sbp_c", fit.params["sbp_c"], fit.bse["sbp_c"], fit.pvalues["sbp_c"], len(people))
put("dispersion_alpha", fit.params["alpha"], fit.bse["alpha"], support=len(people), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

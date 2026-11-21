"""Blood loss in two parts: any loss (logistic), and how much when there is some (log-linear) (family F5, visits.csv)."""
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


df = pd.read_csv("visits.csv")
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "loss": pd.to_numeric(df["blood_loss_ml"], errors="coerce"),
    "arm_b": df["arm"].eq("B").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
}).dropna()
data["any_loss"] = (data["loss"] > 0).astype(int)
cells = pd.crosstab(data["arm_b"], data["any_loss"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
first = smf.glm("any_loss ~ arm_b + age_c", data=data, family=sm.families.Binomial()).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(data["patient_id"])[0]})
put("any_loss_arm_b", first.params["arm_b"], first.bse["arm_b"], first.pvalues["arm_b"], int(cells.to_numpy().min()),
    primary=True)
some = data[data["any_loss"] == 1]
second = smf.ols("np.log(loss) ~ arm_b", data=some).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(some["patient_id"])[0]})
put("log_amount_arm_b", second.params["arm_b"], second.bse["arm_b"], second.pvalues["arm_b"],
    int(min(some["arm_b"].sum(), len(some) - some["arm_b"].sum())))
zero = 1 - data["any_loss"].mean()
put("zero_share", zero, math.sqrt(zero * (1 - zero) / len(data)), support=int(cells.to_numpy().min()))
put("median_when_some", some["loss"].median(), support=len(some), judged=False)
put("mean_log_when_some", np.log(some["loss"]).mean(), np.log(some["loss"]).std() / math.sqrt(len(some)),
    support=len(some), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

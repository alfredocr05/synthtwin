"""Monthly admissions: the trend and an interrupted series' step in July 2021 (family F8, cohort.csv)."""
import json

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
admitted = pd.to_datetime(df["admit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_admit_date"] = float(admitted.isna().mean())
months = admitted.dropna().dt.to_period("M")
counts = months.value_counts().sort_index()
every = pd.period_range("2019-01", "2023-12", freq="M")
counts = counts.reindex(every, fill_value=0)
data = pd.DataFrame({"admissions": counts.to_numpy(), "month": np.arange(len(counts)),
                     "after": (every >= pd.Period("2021-07", freq="M")).astype(int)})
data["month_after"] = data["month"] * data["after"]
fit = smf.glm("admissions ~ month + after", data=data, family=sm.families.Poisson()).fit(scale="X2")
put("step_july_2021", fit.params["after"], fit.bse["after"], fit.pvalues["after"], int(counts.min()), primary=True)
put("monthly_growth", fit.params["month"], fit.bse["month"], fit.pvalues["month"], int(counts.min()))
put("mean_monthly_admissions_log", np.log(counts.mean()), np.sqrt(1 / counts.sum()), support=int(counts.sum()))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

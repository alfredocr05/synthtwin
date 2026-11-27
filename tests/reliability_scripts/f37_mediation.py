"""Mediation: how much of diabetes's effect on the length of stay passes through a complication (the mediator a logistic model, the outcome a linear model of the log stay; the effects averaged over the patients and their uncertainty by quasi-Bayesian simulation, as Imai and colleagues do), with the two paths of the product method (family F37, cohort.csv)."""
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
    "log_stay": np.log(pd.to_numeric(df["stay_days"], errors="coerce")),
    "complication": df["complication"].eq("Y").astype(int),
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
}).replace([np.inf, -np.inf], np.nan).dropna().reset_index(drop=True)
checks["kept_rows"] = int(len(data))
exposed = int(min(data["diabetes"].sum(), len(data) - data["diabetes"].sum()))
a_path = smf.glm("complication ~ diabetes + age_c + risk_class", data=data, family=sm.families.Binomial()).fit()
b_path = smf.ols("log_stay ~ diabetes + complication + age_c + risk_class", data=data).fit()
rest = np.column_stack([np.ones(len(data)), data["age_c"], data["risk_class"]])


def effects(a, b):
    """The average indirect (through the complication) and direct effects of diabetes on the log stay."""
    base = rest @ np.array([a["Intercept"], a["age_c"], a["risk_class"]])
    moved = 1.0 / (1.0 + np.exp(-(base + a["diabetes"]))) - 1.0 / (1.0 + np.exp(-base))
    return b["complication"] * float(np.mean(moved)), b["diabetes"]


indirect, direct = effects(a_path.params, b_path.params)
draws = np.random.default_rng(37)
a_draws = draws.multivariate_normal(a_path.params.to_numpy(), a_path.cov_params().to_numpy(), 1000)
b_draws = draws.multivariate_normal(b_path.params.to_numpy(), b_path.cov_params().to_numpy(), 1000)
simulated = np.array([effects(pd.Series(a, index=a_path.params.index), pd.Series(b, index=b_path.params.index))
                      for a, b in zip(a_draws, b_draws)])
total_draws = simulated.sum(axis=1)
for name, value, sample, primary in (("indirect", indirect, simulated[:, 0], True),
                                     ("direct", direct, simulated[:, 1], False),
                                     ("total", indirect + direct, total_draws, False),
                                     ("share_mediated", indirect / (indirect + direct),
                                      simulated[:, 0] / total_draws, False)):
    p = 2 * min(float(np.mean(sample <= 0)), float(np.mean(sample >= 0)))
    put(name, value, float(np.std(sample, ddof=1)), max(p, 1 / 1000), exposed, primary)
put("path_diabetes_to_complication", a_path.params["diabetes"], a_path.bse["diabetes"], a_path.pvalues["diabetes"],
    exposed)
put("path_complication_to_stay", b_path.params["complication"], b_path.bse["complication"],
    b_path.pvalues["complication"], int(min(data["complication"].sum(), len(data) - data["complication"].sum())))
put("indirect_sobel_log_odds_scale", a_path.params["diabetes"] * b_path.params["complication"],
    math.sqrt(a_path.params["diabetes"] ** 2 * b_path.bse["complication"] ** 2
              + b_path.params["complication"] ** 2 * a_path.bse["diabetes"] ** 2), support=exposed, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

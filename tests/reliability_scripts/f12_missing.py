"""Missing body-mass index: the model of who is missing, complete cases against multiple imputation (family F12, cohort.csv)."""
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
data = pd.DataFrame({
    "weight": pd.to_numeric(df["weight"], errors="coerce"),
    "log_stay": np.log(pd.to_numeric(df["stay_days"], errors="coerce")),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "female": df["gender"].eq("F").astype(int),
    "diabetes": df["diabetes"].eq("Y").astype(int),
})
data["missing"] = data["weight"].isna().astype(int)
data = data.dropna(subset=["log_stay", "age_c"])
lost = int(data["missing"].sum())
who = smf.glm("missing ~ age_c + female", data=data, family=sm.families.Binomial()).fit()
put("missing_by_age", who.params["age_c"], who.bse["age_c"], who.pvalues["age_c"], min(lost, len(data) - lost),
    primary=True)
put("missing_by_gender", who.params["female"], who.bse["female"], who.pvalues["female"], min(lost, len(data) - lost),
    judged=False)
complete = smf.ols("log_stay ~ weight + age_c + diabetes", data=data.dropna()).fit()
put("complete_case_weight", complete.params["weight"], complete.bse["weight"], complete.pvalues["weight"],
    int(complete.nobs))
put("complete_case_diabetes", complete.params["diabetes"], complete.bse["diabetes"], complete.pvalues["diabetes"],
    int(min(data.dropna()["diabetes"].sum(), complete.nobs - data.dropna()["diabetes"].sum())), judged=False)

imputer = smf.ols("weight ~ age_c + female + diabetes + log_stay", data=data.dropna()).fit()
draws = np.random.default_rng(2026)
estimates, variances = [], []
for _ in range(5):
    beta = draws.multivariate_normal(imputer.params.to_numpy(), imputer.cov_params().to_numpy())
    design = np.column_stack([np.ones(len(data)), data["age_c"], data["female"], data["diabetes"], data["log_stay"]])
    guess = design @ beta + draws.normal(0, np.sqrt(imputer.scale), len(data))
    filled = data.assign(weight=data["weight"].fillna(pd.Series(guess, index=data.index)))
    fit = smf.ols("log_stay ~ weight + age_c + diabetes", data=filled).fit()
    estimates += [fit.params["weight"]]
    variances += [fit.bse["weight"] ** 2]
within, between = np.mean(variances), np.var(estimates, ddof=1)
total = within + (1 + 1 / 5) * between
estimate = float(np.mean(estimates))
put("imputed_weight", estimate, np.sqrt(total), None, len(data))
put("missing_share", data["missing"].mean(), np.sqrt(data["missing"].mean() * (1 - data["missing"].mean()) / len(data)),
    support=min(lost, len(data) - lost), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

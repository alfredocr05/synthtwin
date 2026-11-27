"""Cox's model with an effect that changes over time: the treatment's hazard ratio in three periods of follow-up (episodes split at 180 and 365 days) and a test of proportional hazards on the scaled Schoenfeld residuals (family F32, methods.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["outcome_days"], errors="coerce"),
    "event": df["outcome"].eq("Y").astype(int),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
}).dropna()
data = data[data["time"] > 0].reset_index(drop=True)
checks["kept_rows"] = int(len(data))
cuts = [0, 180, 365, np.inf]
episodes = []
for k in range(3):
    low, high = cuts[k], cuts[k + 1]
    part = data[data["time"] > low].copy()
    part["entry"] = float(low)
    part["exit"] = np.minimum(part["time"], high)
    part["status"] = ((part["event"] == 1) & (part["time"] <= high)).astype(int)
    part["period"] = k
    episodes += [part]
split = pd.concat(episodes, ignore_index=True)
for k in range(3):
    split[f"treated_p{k}"] = split["treated"] * (split["period"] == k)
fit = sm.PHReg(split["exit"].to_numpy(), split[["treated_p0", "treated_p1", "treated_p2", "age_c", "diabetes"]],
               status=split["status"].to_numpy(), entry=split["entry"].to_numpy(), ties="breslow").fit()
names = list(fit.model.exog_names)
for k, label in enumerate(("first_half_year", "second_half_year", "after_a_year")):
    at = names.index(f"treated_p{k}")
    events = split[(split["period"] == k) & (split["status"] == 1)]
    support = int(min(events["treated"].sum(), len(events) - events["treated"].sum()))
    put(f"treated_{label}", fit.params[at], fit.bse[at], fit.pvalues[at], support, primary=(k == 0))
cov = fit.cov_params()
first, last = names.index("treated_p0"), names.index("treated_p2")
difference = fit.params[last] - fit.params[first]
spread = float(np.sqrt(cov[first, first] + cov[last, last] - 2 * cov[first, last]))
put("treated_late_minus_early", difference, spread, 2 * stats.norm.sf(abs(difference) / spread),
    int(min(data.loc[data["event"] == 1, "treated"].sum(), (data["event"] == 1).sum()
            - data.loc[data["event"] == 1, "treated"].sum())))
plain = smf.phreg("time ~ treated + age_c + diabetes", data=data, status=data["event"].to_numpy(), ties="breslow").fit()
residuals = plain.schoenfeld_residuals
at = list(plain.model.exog_names).index("treated")
happened = np.isfinite(residuals[:, at])
times = np.log(data["time"].to_numpy()[happened])
scaled = residuals[happened, at] * plain.cov_params()[at, at] * happened.sum() + plain.params[at]
line = sm.OLS(scaled, sm.add_constant(times)).fit()
put("treated_schoenfeld_slope_on_log_time", line.params[1], line.bse[1], line.pvalues[1],
    int(min(data.loc[data["event"] == 1, "treated"].sum(), (data["event"] == 1).sum()
            - data.loc[data["event"] == 1, "treated"].sum())))
put("treated_proportional", plain.params[at], plain.bse[at], plain.pvalues[at], judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

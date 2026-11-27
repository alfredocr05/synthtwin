"""Survival with a frailty shared within a surgeon: a Weibull model with a gamma frailty by surgeon (its marginal likelihood maximised), beside Cox's model with errors robust to the surgeon (family F32, operations.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import optimize, special


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("operations.csv")
data = pd.DataFrame({
    "time": pd.to_numeric(df["followup_days"], errors="coerce") / 365.25,
    "event": df["readmitted"].eq("Y").astype(int),
    "complication": df["complication"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
    "emergency": df["emergency"].eq("Y").astype(int),
    "surgeon": df["surgeon"],
}).dropna()
data = data[data["time"] > 0].reset_index(drop=True)
checks["kept_rows"] = int(len(data))
covariates = ["complication", "age_c", "emergency"]
x = data[covariates].to_numpy(dtype=float)
t = data["time"].to_numpy()
d = data["event"].to_numpy(dtype=float)
codes, surgeons = pd.factorize(data["surgeon"])
events_by = np.bincount(codes, weights=d, minlength=len(surgeons))
log_t = np.log(t)


def minus_log_likelihood(theta):
    """The Weibull model's marginal log likelihood with a gamma frailty of variance exp(theta[-1]) by surgeon, negated."""
    log_shape, log_scale, beta, log_var = theta[0], theta[1], theta[2:-1], min(3.0, max(-12.0, theta[-1]))
    shape, var = math.exp(log_shape), math.exp(log_var)
    eta = x @ beta
    cumulative = np.exp(log_scale + shape * log_t + eta)
    log_hazard = log_scale + log_shape + (shape - 1.0) * log_t + eta
    summed = np.bincount(codes, weights=cumulative, minlength=len(surgeons))
    inverse = 1.0 / var
    each = (events_by * log_var + special.gammaln(inverse + events_by) - special.gammaln(inverse)
            - (inverse + events_by) * np.log1p(var * summed))
    return -(float(np.sum(d * log_hazard)) + float(np.sum(each)))


start = np.concatenate([[0.0, math.log(max(d.sum(), 1.0) / t.sum())], np.zeros(len(covariates)), [math.log(0.2)]])
found = optimize.minimize(minus_log_likelihood, start, method="BFGS", options={"gtol": 1e-6, "maxiter": 2000})
estimate = found.x


def hessian(f, at, step=1e-4):
    """The matrix of second differences of f at a point (central differences)."""
    k = len(at)
    out = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            e_i, e_j = np.eye(k)[i] * step, np.eye(k)[j] * step
            value = (f(at + e_i + e_j) - f(at + e_i - e_j) - f(at - e_i + e_j) + f(at - e_i - e_j)) / (4 * step * step)
            out[i, j] = out[j, i] = value
    return out


covariance = np.linalg.pinv(hessian(minus_log_likelihood, estimate))
errors = np.sqrt(np.diag(covariance))
in_complication = int(min(data.loc[data["event"] == 1, "complication"].sum(),
                          (data["event"] == 1).sum() - data.loc[data["event"] == 1, "complication"].sum()))
events = int(d.sum())
for k, term in enumerate(covariates):
    value, se = estimate[2 + k], errors[2 + k]
    put(f"frailty_{term}", value, se, math.erfc(abs(value / se) / math.sqrt(2)),
        in_complication if term == "complication" else events, primary=(term == "complication"))
variance = math.exp(min(3.0, max(-12.0, estimate[-1])))
put("frailty_variance", variance, variance * errors[-1], support=len(surgeons), judged=True)
put("weibull_shape", math.exp(estimate[0]), math.exp(estimate[0]) * errors[0], support=events)
cox = sm.PHReg(t, data[covariates].astype(float), status=d.astype(int), ties="breslow").fit(
    groups=codes)
names = list(cox.model.exog_names)
at = names.index("complication")
put("cox_robust_complication", cox.params[at], cox.bse[at], cox.pvalues[at], in_complication)
put("surgeons", len(surgeons), support=len(surgeons), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

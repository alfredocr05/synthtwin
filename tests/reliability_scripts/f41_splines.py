"""Splines: a logistic model of the complication with a natural cubic spline of age (four degrees of freedom), the risk at 75 against 45 with its delta-method error, the spline's departure from a straight line (likelihood ratio), and an interaction (family F41, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from patsy import build_design_matrices
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
data = pd.DataFrame({
    "complication": df["complication"].eq("Y").astype(int),
    "age": pd.to_numeric(df["age"], errors="coerce"),
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "smoker": df["smoker"].eq("Y").astype(int),
}).dropna().reset_index(drop=True)
checks["kept_rows"] = int(len(data))
events = data["complication"]
support = int(min(events.sum(), len(events) - events.sum()))
curved = smf.glm("complication ~ cr(age, df=4, constraints='center') + risk_class + diabetes * smoker", data=data,
                 family=sm.families.Binomial()).fit()
straight = smf.glm("complication ~ age + risk_class + diabetes * smoker", data=data,
                   family=sm.families.Binomial()).fit()
ratio = 2 * (curved.llf - straight.llf)
put("spline_departure_chi_square", ratio, p=stats.chi2.sf(ratio, curved.df_model - straight.df_model),
    support=support, judged=False)

at = pd.DataFrame({"age": [75.0, 45.0], "risk_class": [float(data["risk_class"].median())] * 2,
                   "diabetes": [0, 0], "smoker": [0, 0], "complication": [0, 0]})
spec = getattr(curved.model.data, "model_spec", None) or curved.model.data.design_info  # statsmodels 0.15 or 0.14
matrix = np.asarray(build_design_matrices([spec], at)[0])
covariance = curved.cov_params().to_numpy()
eta = matrix @ curved.params.to_numpy()
chance = 1.0 / (1.0 + np.exp(-eta))
direction = (chance * (1 - chance))[:, None] * matrix
contrast = direction[0] - direction[1]
difference = chance[0] - chance[1]
spread = math.sqrt(float(contrast @ covariance @ contrast))
put("risk_at_75_minus_45", difference, spread, math.erfc(abs(difference / spread) / math.sqrt(2)), support,
    primary=True)
gap = matrix[0] - matrix[1]
log_odds = float(gap @ curved.params.to_numpy())
log_spread = math.sqrt(float(gap @ covariance @ gap))
put("log_odds_75_against_45", log_odds, log_spread, math.erfc(abs(log_odds / log_spread) / math.sqrt(2)), support)
put("diabetes:smoker", curved.params["diabetes:smoker"], curved.bse["diabetes:smoker"],
    curved.pvalues["diabetes:smoker"], int(((data["diabetes"] * data["smoker"]) * events).sum()))
put("risk_class", curved.params["risk_class"], curved.bse["risk_class"], curved.pvalues["risk_class"], support)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

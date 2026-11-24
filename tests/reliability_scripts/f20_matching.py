"""Propensity-score matching: one control a treated patient, nearest on the score's log odds within a caliper, the treated's outcome difference and the balance (family F20, methods.csv)."""
import bisect
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

df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "outcome": df["outcome"].eq("Y").astype(int),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "mass_c": (pd.to_numeric(df["body_mass_index"], errors="coerce") - 28) / 5,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "female": df["gender"].eq("F").astype(int),
}).dropna().reset_index(drop=True)
checks["kept_rows"] = int(len(data))
model = smf.glm("treated ~ age_c + mass_c + diabetes + female", data=data, family=sm.families.Binomial()).fit()
odds_scale = np.log(model.predict(data) / (1 - model.predict(data))).to_numpy()
caliper = 0.2 * odds_scale.std()
controls = sorted((odds_scale[k], k) for k in np.nonzero(data["treated"].to_numpy() == 0)[0])
keys = [value for value, _k in controls]
pairs = []
for k in sorted(np.nonzero(data["treated"].to_numpy() == 1)[0], key=lambda k: (-odds_scale[k], k)):
    at = bisect.bisect_left(keys, odds_scale[k])
    best = None
    for place in (at - 1, at):
        if 0 <= place < len(keys) and abs(keys[place] - odds_scale[k]) <= caliper:
            if best is None or abs(keys[place] - odds_scale[k]) < abs(keys[best] - odds_scale[k]):
                best = place
    if best is not None:
        pairs += [(k, controls[best][1])]
        del keys[best]
        del controls[best]
treated_rows = np.array([a for a, _b in pairs])
control_rows = np.array([b for _a, b in pairs])
differences = data["outcome"].to_numpy()[treated_rows] - data["outcome"].to_numpy()[control_rows]
put("matched_risk_difference", differences.mean(), differences.std(ddof=1) / math.sqrt(len(differences)),
    support=int(min(data["outcome"].to_numpy()[treated_rows].sum(), data["outcome"].to_numpy()[control_rows].sum())),
    primary=True)
put("matched_share_of_treated", len(pairs) / int(data["treated"].sum()), support=len(pairs), judged=False)
for column in ("age_c", "mass_c", "diabetes"):
    a, b = data[column].to_numpy()[treated_rows], data[column].to_numpy()[control_rows]
    put(f"balance_{column}_after_matching", (a.mean() - b.mean()) / math.sqrt((a.var() + b.var()) / 2),
        support=len(pairs), judged=False)
put("score_age", model.params["age_c"], model.bse["age_c"], model.pvalues["age_c"], int(data["treated"].sum()))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

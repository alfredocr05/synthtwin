"""Diagnostic accuracy: the ROC curve's area of a risk score for the outcome, two areas compared (DeLong), sensitivity and specificity at a cut (family F18, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
data = pd.DataFrame({"outcome": df["outcome"].eq("Y").astype(int),
                     "score": pd.to_numeric(df["score"], errors="coerce"),
                     "age": pd.to_numeric(df["age"], errors="coerce")}).dropna()
checks["kept_rows"] = int(len(data))
cases, controls = data[data["outcome"] == 1], data[data["outcome"] == 0]
limit = int(min(len(cases), len(controls)))


def components(marker):
    """DeLong's structural components of one marker's area: each case's and each control's placement."""
    x, y = cases[marker].to_numpy(dtype=float), controls[marker].to_numpy(dtype=float)
    ranked_all = stats.rankdata(np.concatenate([x, y]))
    ranked_x, ranked_y = stats.rankdata(x), stats.rankdata(y)
    v10 = (ranked_all[: len(x)] - ranked_x) / len(y)
    v01 = 1.0 - (ranked_all[len(x):] - ranked_y) / len(x)
    return v10.mean(), v10, v01


area_score, v10_s, v01_s = components("score")
area_age, v10_a, v01_a = components("age")
s10, s01 = np.cov(np.vstack([v10_s, v10_a])), np.cov(np.vstack([v01_s, v01_a]))
var = s10 / len(cases) + s01 / len(controls)
put("area_score", area_score, math.sqrt(var[0, 0]), support=limit, primary=True)
put("area_age", area_age, math.sqrt(var[1, 1]), support=limit)
difference_se = math.sqrt(var[0, 0] + var[1, 1] - 2 * var[0, 1])
difference = area_score - area_age
put("area_score_minus_age", difference, difference_se, math.erfc(abs(difference) / difference_se / math.sqrt(2)), limit)
positive = data["score"] >= 5
sensitivity = positive[data["outcome"] == 1].mean()
specificity = (~positive)[data["outcome"] == 0].mean()
put("sensitivity_at_5", sensitivity, math.sqrt(sensitivity * (1 - sensitivity) / len(cases)), support=len(cases))
put("specificity_at_5", specificity, math.sqrt(specificity * (1 - specificity) / len(controls)), support=len(controls))
cuts = sorted(data["score"].unique())
youden = max(cuts, key=lambda cut: (data.loc[data["outcome"] == 1, "score"] >= cut).mean()
             - (data.loc[data["outcome"] == 0, "score"] >= cut).mean())
put("best_cut_by_youden", youden, support=limit, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

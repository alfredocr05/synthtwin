"""Contingency tables: a trend across ordered classes (Cochran-Armitage), an r by c table (Cramer's V), a stratified 2 by 2 (Mantel-Haenszel), a relative risk (family F23, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import StratifiedTable


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("cohort.csv")
complication = df["complication"].eq("Y").astype(int)
classes = pd.to_numeric(df["risk_class"], errors="coerce")
part = pd.DataFrame({"y": complication, "x": classes}).dropna()
part = part[part["x"].isin([1, 2, 3, 4, 5])]
checks["kept_classes_1_to_5"] = int(len(part))
n, mean_x, share = len(part), part["x"].mean(), part["y"].mean()
slope = ((part["x"] - mean_x) * (part["y"] - share)).sum() / ((part["x"] - mean_x) ** 2).sum()
z = slope * math.sqrt(((part["x"] - mean_x) ** 2).sum() / (share * (1 - share)))
put("trend_per_class", slope, abs(slope / z), math.erfc(abs(z) / math.sqrt(2)),
    int(part.groupby("x")["y"].sum().min()), primary=True)
table = pd.crosstab(df["technique"], classes).to_numpy()
chi2, p, _dof, _expected = stats.chi2_contingency(table, correction=False)
put("technique_by_class_cramers_v", math.sqrt(chi2 / (table.sum() * (min(table.shape) - 1))), p=p,
    support=int(table.min()), judged=False)
smoker = df["smoker"].eq("Y").astype(int)
diabetes = df["diabetes"].eq("Y").astype(int)
strata = [pd.crosstab(smoker[diabetes == d], complication[diabetes == d]).reindex(index=[1, 0], columns=[1, 0],
                                                                                  fill_value=0).to_numpy()
          for d in (0, 1)]
pooled = StratifiedTable(strata)
low, high = pooled.oddsratio_pooled_confint()
put("smoking_mantel_haenszel_log_odds", math.log(pooled.oddsratio_pooled), (math.log(high) - math.log(low)) / (2 * 1.959964),
    pooled.test_null_odds().pvalue, int(np.min([t.min() for t in strata])))
put("smoking_odds_differ_by_diabetes_p", pooled.test_equal_odds().statistic, p=pooled.test_equal_odds().pvalue,
    support=int(np.min([t.min() for t in strata])), judged=False)
exposed, unexposed = complication[smoker == 1], complication[smoker == 0]
risk_ratio = exposed.mean() / unexposed.mean()
se = math.sqrt((1 - exposed.mean()) / exposed.sum() + (1 - unexposed.mean()) / unexposed.sum())
put("smoking_log_risk_ratio", math.log(risk_ratio), se, math.erfc(abs(math.log(risk_ratio) / se) / math.sqrt(2)),
    int(min(exposed.sum(), unexposed.sum())))
tau, p = stats.kendalltau(classes, pd.to_numeric(df["stay_days"], errors="coerce"), nan_policy="omit")
put("class_stay_kendall_tau", tau, p=p, support=n, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

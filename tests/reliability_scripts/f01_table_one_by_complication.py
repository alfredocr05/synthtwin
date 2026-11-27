"""Table 1 of the cohort by complication, with standardised differences (family F1, cohort.csv)."""
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


df = pd.read_csv("cohort.csv")
group = df["complication"].eq("Y")
yes, no = df[group], df[~group]


def difference_of_means(name, column, primary=False, log=False, judged=True):
    a = pd.to_numeric(yes[column], errors="coerce").dropna()
    b = pd.to_numeric(no[column], errors="coerce").dropna()
    if log:
        a, b = np.log(a[a > 0]), np.log(b[b > 0])
    test = stats.ttest_ind(a, b, equal_var=False)
    put(name, a.mean() - b.mean(), math.sqrt(a.var() / len(a) + b.var() / len(b)), test.pvalue,
        min(len(a), len(b)), primary, judged)
    put(name + "_standardised", (a.mean() - b.mean()) / math.sqrt((a.var() + b.var()) / 2),
        support=min(len(a), len(b)), judged=False)


def difference_of_shares(name, flag, primary=False, judged=True):
    a, b = flag[group].astype(float), flag[~group].astype(float)
    pa, pb = a.mean(), b.mean()
    se = math.sqrt(pa * (1 - pa) / len(a) + pb * (1 - pb) / len(b))
    p = 2 * stats.norm.sf(abs(pa - pb) / se) if se > 0 else 1.0
    cells = min(a.sum(), len(a) - a.sum(), b.sum(), len(b) - b.sum())
    put(name, pa - pb, se, p, cells, primary, judged)


difference_of_means("age_difference", "age", primary=True)
difference_of_means("log_stay_difference", "stay_days", log=True)
difference_of_means("weight_difference", "weight", judged=False)
difference_of_shares("diabetes_difference", df["diabetes"].eq("Y"), primary=True)
difference_of_shares("smoker_difference", df["smoker"].eq("Y"), judged=False)
difference_of_shares("class_3_difference", pd.to_numeric(df["risk_class"], errors="coerce") >= 3)
difference_of_shares("female_difference", df["gender"].eq("F"), judged=False)
checks["rows_with_complication"] = int(group.sum())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Repeated-measures analysis of variance over the first four visits (its sums of squares), paired and rank tests, and slopes compared between arms (family F16, visits.csv)."""
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

df = pd.read_csv("visits.csv")
df["sbp"] = pd.to_numeric(df["sbp"], errors="coerce")
df = df.dropna(subset=["sbp"]).sort_values(["patient_id", "visit_date"])
df["order"] = df.groupby("patient_id").cumcount() + 1
four = df[df["order"] <= 4]
complete = four.groupby("patient_id")["order"].transform("size") == 4
four = four[complete]
checks["kept_patients_with_four"] = int(four["patient_id"].nunique())
people = four["patient_id"].nunique()
wide = four.pivot(index="patient_id", columns="order", values="sbp")
values = wide[[1, 2, 3, 4]].to_numpy()
grand = values.mean()
visits_ss = len(values) * ((values.mean(axis=0) - grand) ** 2).sum()
people_ss = 4 * ((values.mean(axis=1) - grand) ** 2).sum()
error_ss = ((values - grand) ** 2).sum() - visits_ss - people_ss
freedom = (3, 3 * (len(values) - 1))
f_value = (visits_ss / freedom[0]) / (error_ss / freedom[1])
put("visit_f", f_value, p=stats.f.sf(f_value, *freedom), support=people, judged=False)
change = wide[4] - wide[1]
test = stats.ttest_rel(wide[4], wide[1])
put("change_first_to_fourth", change.mean(), change.std() / math.sqrt(len(change)), test.pvalue, people, primary=True)
signed = stats.wilcoxon(wide[4], wide[1])
falls = (change < 0).mean()
put("share_falling_first_to_fourth", falls, math.sqrt(falls * (1 - falls) / len(change)), signed.pvalue, people,
    judged=False)
chi2, p = stats.friedmanchisquare(wide[1], wide[2], wide[3], wide[4])
put("friedman_chi_square", chi2, p=p, support=people, judged=False)
visits = np.array([1.0, 2.0, 3.0, 4.0])
centred = visits - visits.mean()
slopes = (wide[[1, 2, 3, 4]].to_numpy() * centred).sum(axis=1) / (centred ** 2).sum()
arm = four.groupby("patient_id")["arm"].first().reindex(wide.index)
b, a = slopes[arm.eq("B").to_numpy()], slopes[arm.eq("A").to_numpy()]
welch = stats.ttest_ind(b, a, equal_var=False)
put("slope_b_minus_a", b.mean() - a.mean(), math.sqrt(b.var(ddof=1) / len(b) + a.var(ddof=1) / len(a)), welch.pvalue,
    int(min(len(a), len(b))), primary=True)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

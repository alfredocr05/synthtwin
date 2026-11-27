"""Group tests on the cohort: t, Mann-Whitney, chi-square, Fisher, Kruskal-Wallis, Spearman (family F2, cohort.csv)."""
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
stay = pd.to_numeric(df["stay_days"], errors="coerce")
diabetic = df["diabetes"].eq("Y")
a, b = stay[diabetic].dropna(), stay[~diabetic].dropna()
test = stats.ttest_ind(a, b, equal_var=False)
put("stay_by_diabetes", a.mean() - b.mean(), math.sqrt(a.var() / len(a) + b.var() / len(b)), test.pvalue,
    min(len(a), len(b)), primary=True)

female = df["gender"].eq("F")
a, b = stay[female].dropna(), stay[~female].dropna()
u = stats.mannwhitneyu(a, b, alternative="two-sided")
put("stay_by_gender_rank_effect", u.statistic / (len(a) * len(b)) - 0.5, p=u.pvalue, support=min(len(a), len(b)),
    judged=False)

smoker = df["smoker"].eq("Y")
complication = df["complication"].eq("Y")
table = pd.crosstab(smoker, complication).reindex(index=[False, True], columns=[False, True], fill_value=0)
chi2, p, _dof, _expected = stats.chi2_contingency(table.to_numpy(), correction=False)
p1 = table.loc[True, True] / table.loc[True].sum()
p0 = table.loc[False, True] / table.loc[False].sum()
se = math.sqrt(p1 * (1 - p1) / table.loc[True].sum() + p0 * (1 - p0) / table.loc[False].sum())
put("complication_by_smoking", p1 - p0, se, p, table.to_numpy().min(), primary=True)

group = df["proc_group"].eq("PG04")
table = pd.crosstab(group, complication).reindex(index=[False, True], columns=[False, True], fill_value=0)
cells = table.to_numpy()
odds, p = stats.fisher_exact(cells)
if cells.min() > 0:
    put("complication_in_group_04_log_odds", math.log(odds), math.sqrt((1.0 / cells).sum()), p, cells.min(),
        judged=False)
else:
    put("complication_in_group_04_log_odds", float("nan"), support=cells.min(), judged=False)

classes = pd.to_numeric(df["risk_class"], errors="coerce")
samples = [stay[classes == level].dropna() for level in (1, 2, 3, 4)]
h, p = stats.kruskal(*samples)
n = sum(len(sample) for sample in samples)
put("stay_by_class_epsilon_squared", h / (n - 1), p=p, support=min(len(sample) for sample in samples), judged=False)

pair = pd.DataFrame({"age": pd.to_numeric(df["age"], errors="coerce"),
                     "weight": pd.to_numeric(df["weight"], errors="coerce")}).dropna()
rho, p = stats.spearmanr(pair["age"], pair["weight"])
put("age_weight_spearman", rho, (1 - rho ** 2) / math.sqrt(len(pair) - 3), p, len(pair))
checks["rows"] = int(np.isfinite(stay).sum())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

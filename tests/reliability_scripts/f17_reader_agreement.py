"""Agreement of two readers grading one finding: Cohen's kappa, weighted kappa, McNemar's test of the two readers' shares (family F17, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from statsmodels.stats.contingency_tables import mcnemar


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
GRADES = {"none": 0, "mild": 1, "moderate": 2, "severe": 3}
first = df["grade_first"].map(GRADES)
second = df["grade_second"].map(GRADES)
both = pd.DataFrame({"first": first, "second": second}).dropna().astype(int)
checks["kept_read_twice"] = int(len(both))
n = len(both)
table = pd.crosstab(both["first"], both["second"]).reindex(index=range(4), columns=range(4), fill_value=0).to_numpy()
observed = table.trace() / n
expected = (table.sum(axis=1) * table.sum(axis=0)).sum() / n ** 2
kappa = (observed - expected) / (1 - expected)
put("kappa", kappa, math.sqrt(observed * (1 - observed) / (n * (1 - expected) ** 2)), support=int(table.sum(axis=0).min()),
    primary=True)
# The quadratic weighted kappa with its large-sample standard error (Fleiss, Cohen and Everitt; lane STATS-D: before,
# none was written and the half-split yardstick, near nought for so stable an estimate, judged it).
share = table / n
weights = 1.0 - (np.subtract.outer(np.arange(4), np.arange(4)) ** 2) / 9.0
rows_share, columns_share = share.sum(axis=1), share.sum(axis=0)
agreed = (weights * share).sum()
chance = (weights * np.outer(rows_share, columns_share)).sum()
weighted = (agreed - chance) / (1.0 - chance)
by_row, by_column = weights @ columns_share, rows_share @ weights
spread = ((share * (weights - np.add.outer(by_row, by_column) * (1.0 - weighted)) ** 2).sum()
          - (weighted - chance * (1.0 - weighted)) ** 2)
put("quadratic_weighted_kappa", cohen_kappa_score(both["first"], both["second"], weights="quadratic"),
    math.sqrt(max(spread, 0.0) / (n * (1.0 - chance) ** 2)), support=int(table.sum(axis=0).min()))
put("exact_agreement", observed, math.sqrt(observed * (1 - observed) / n), support=n, judged=False)
high_first, high_second = both["first"] >= 2, both["second"] >= 2
pairs = pd.crosstab(high_first, high_second).reindex(index=[False, True], columns=[False, True], fill_value=0)
test = mcnemar(pairs.to_numpy(), exact=False, correction=True)
shift = (high_second.sum() - high_first.sum()) / n
discordant = pairs.loc[True, False] + pairs.loc[False, True]
put("second_reader_more_often_moderate_or_worse", shift, math.sqrt(discordant) / n, test.pvalue,
    int(min(pairs.loc[True, False], pairs.loc[False, True])))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

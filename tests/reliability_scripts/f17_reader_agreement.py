"""Agreement of two readers grading one finding: Cohen's kappa, weighted kappa, McNemar's test of the two readers' shares (family F17, methods.csv)."""
import json
import math

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
put("quadratic_weighted_kappa", cohen_kappa_score(both["first"], both["second"], weights="quadratic"),
    support=int(table.sum(axis=0).min()))
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

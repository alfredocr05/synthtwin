"""Every pair of ten patient attributes tested for association (family F2, attributes.csv): the null table's control."""
import itertools
import json
import math

import pandas as pd
from scipy import stats

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("attributes.csv")
LABELS = ["plan_type", "region", "paperless", "contact_pref", "language"]
NUMBERS = ["balance", "visits_yr", "risk_score", "copay", "opened"]
columns = {name: df[name] for name in LABELS}
for name in NUMBERS:
    if name == "opened":
        days = pd.to_datetime(df[name], format="%Y-%m-%d", errors="coerce")
        columns[name] = (days - pd.Timestamp("2015-01-01")).dt.days
    else:
        columns[name] = pd.to_numeric(df[name], errors="coerce")
for first, second in itertools.combinations(LABELS + NUMBERS, 2):
    pair = pd.DataFrame({"a": columns[first], "b": columns[second]}).dropna()
    name = f"pair:{first}~{second}"
    if first in NUMBERS and second in NUMBERS:
        rho, p = stats.spearmanr(pair["a"], pair["b"])
        put(name, rho, 1 / math.sqrt(len(pair) - 3), p, len(pair))
    elif first in LABELS and second in LABELS:
        table = pd.crosstab(pair["a"], pair["b"]).to_numpy()
        chi2, p, _dof, _expected = stats.chi2_contingency(table, correction=False)
        put(name, math.sqrt(chi2 / (table.sum() * (min(table.shape) - 1))), p=p, support=int(table.min()))
    else:
        label, number = ("a", "b") if first in LABELS else ("b", "a")
        groups = [group[number].to_numpy() for _key, group in pair.groupby(label)]
        h, p = stats.kruskal(*groups)
        put(name, h / (len(pair) - 1), p=p, support=min(len(group) for group in groups))
checks["pairs"] = len(results)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

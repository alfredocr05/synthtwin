"""Orders given or not, by drug class: opioids against the rest, and a chi-square over the action words (family F2, orders.csv)."""
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


df = pd.read_csv("orders.csv")
opioid = df["drug"].isin(["fentanyl", "oxycodone", "hydromorphone", "morphine"])
given = df["action"].eq("Given").astype(float)
a, b = given[opioid], given[~opioid]
difference = a.mean() - b.mean()
se = math.sqrt(a.mean() * (1 - a.mean()) / len(a) + b.mean() * (1 - b.mean()) / len(b))
p = 2 * stats.norm.sf(abs(difference) / se) if se > 0 else 1.0
cells = min(a.sum(), len(a) - a.sum(), b.sum(), len(b) - b.sum())
put("given_share_opioid_minus_other", difference, se, p, int(cells), primary=True)
table = pd.crosstab(opioid, df["action"]).reindex(columns=["Given", "Held", "Refused", "Missed"], fill_value=0)
chi2, p, _dof, _expected = stats.chi2_contingency(table.to_numpy(), correction=False)
put("action_by_class_cramers_v", math.sqrt(chi2 / table.to_numpy().sum()), p=p, support=int(table.to_numpy().min()),
    judged=False)
put("given_share", given.mean(), math.sqrt(given.mean() * (1 - given.mean()) / len(given)),
    support=int(min(given.sum(), len(given) - given.sum())))
put("opioid_share", opioid.mean(), math.sqrt(opioid.mean() * (1 - opioid.mean()) / len(opioid)),
    support=int(min(opioid.sum(), len(opioid) - opioid.sum())), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""The weekday pattern of admissions (family F8, cohort.csv)."""
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


df = pd.read_csv("cohort.csv")
admitted = pd.to_datetime(df["admit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_admit_date"] = float(admitted.isna().mean())
days = admitted.dropna().dt.dayofweek
n = len(days)
for name, flag, primary in (("weekend_share", days >= 5, True), ("monday_share", days == 0, False),
                            ("sunday_share", days == 6, False)):
    value = flag.mean()
    put(name, value, math.sqrt(value * (1 - value) / n), support=int(min(flag.sum(), n - flag.sum())),
        primary=primary)
counts = days.value_counts().reindex(range(7), fill_value=0)
chi2, p = stats.chisquare(counts.to_numpy())
put("weekday_chi_square_per_row", chi2 / n, p=p, support=int(counts.min()), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

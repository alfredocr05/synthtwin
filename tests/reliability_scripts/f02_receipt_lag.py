"""From collection to receipt: bedside tests received at once, the rest later (family F2, labs.csv)."""
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


df = pd.read_csv("labs.csv")
collected = pd.to_datetime(df["collected_at"], format="%Y-%m-%d %H:%M", errors="coerce")
received = pd.to_datetime(df["received_at"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_received_at"] = float(received.isna().mean())
df["lag"] = (received - collected).dt.total_seconds() / 60
bedside = df["test"].isin(["GLU", "LACT"])
at_once = (df["lag"] == 0).astype(float)
a, b = at_once[bedside], at_once[~bedside]
difference = a.mean() - b.mean()
se = math.sqrt(a.mean() * (1 - a.mean()) / len(a) + b.mean() * (1 - b.mean()) / len(b))
p = 2 * stats.norm.sf(abs(difference) / se) if se > 0 else 1.0
put("received_at_once_bedside_minus_other", difference, se, p,
    min(df.loc[bedside, "patient_id"].nunique(), df.loc[~bedside, "patient_id"].nunique()), primary=True)
later = df.loc[~bedside, "lag"].dropna()
put("median_lag_other_tests", later.median(), support=df.loc[~bedside, "patient_id"].nunique(), judged=False)
put("received_before_collected_share", (df["lag"] < 0).mean(), support=df["patient_id"].nunique())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

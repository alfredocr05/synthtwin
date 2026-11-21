"""From order to administration: the lag of what was given, by route, and the hours of ordering (family F8, orders.csv)."""
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
ordered = pd.to_datetime(df["ordered_at"], format="%Y-%m-%d %H:%M", errors="coerce")
given = pd.to_datetime(df["given_at"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_ordered_at"] = float(ordered.isna().mean())
df["lag"] = (given - ordered).dt.total_seconds() / 60
done = df[df["action"].eq("Given")].dropna(subset=["lag"])
checks["kept_given_rows"] = int(len(done))
put("median_lag", done["lag"].median(), support=done["patient_id"].nunique(), judged=False)
vein, mouth = done.loc[done["route"] == "IV", "lag"], done.loc[done["route"] == "PO", "lag"]
difference = mouth.mean() - vein.mean()
se = math.sqrt(mouth.var() / len(mouth) + vein.var() / len(vein))
put("lag_by_mouth_minus_vein", difference, se, 2 * stats.norm.sf(abs(difference) / se),
    min(done.loc[done["route"] == "IV", "patient_id"].nunique(), done.loc[done["route"] == "PO", "patient_id"].nunique()),
    primary=True)
put("given_before_ordered_share", (done["lag"] < 0).mean(), support=done["patient_id"].nunique())
night = ((ordered.dt.hour < 7) | (ordered.dt.hour >= 22)).mean()
put("night_order_share", night, math.sqrt(night * (1 - night) / len(df)), support=df["patient_id"].nunique())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Table 1 of the cohort, overall (family F1, cohort.csv)."""
import json
import math

import numpy as np
import pandas as pd

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def share(name, flags, primary=False):
    flags = flags.dropna().astype(float)
    value = flags.mean()
    put(name, value, math.sqrt(value * (1 - value) / len(flags)),
        support=min(flags.sum(), len(flags) - flags.sum()), primary=primary)


df = pd.read_csv("cohort.csv")
age = pd.to_numeric(df["age"], errors="coerce").dropna()
put("mean_age", age.mean(), age.std() / math.sqrt(len(age)), support=len(age), primary=True)
weight = pd.to_numeric(df["weight"], errors="coerce").dropna()
put("mean_weight", weight.mean(), weight.std() / math.sqrt(len(weight)), support=len(weight))
stay = pd.to_numeric(df["stay_days"], errors="coerce")
stay = stay[stay > 0]
put("median_stay", stay.median(), support=len(stay))
put("mean_log_stay", np.log(stay).mean(), np.log(stay).std() / math.sqrt(len(stay)), support=len(stay))
share("share_female", df["gender"].eq("F"))
share("share_diabetes", df["diabetes"].eq("Y"))
share("share_hypertension", df["hypertension"].eq("Y"))
share("share_class_3_or_more", pd.to_numeric(df["risk_class"], errors="coerce") >= 3)
share("complication_rate", df["complication"].eq("Y"), primary=True)
share("death_share", pd.to_numeric(df["died"], errors="coerce") == 1)
share("weight_missing_share", df["weight"].isna())
checks["rows"] = len(df)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

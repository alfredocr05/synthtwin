"""Visits from long to wide: the correlation of a patient's visits, per-patient means merged back (family F9, visits.csv)."""
import json
import math

import pandas as pd

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def correlation(name, a, b, primary=False):
    pair = pd.DataFrame({"a": a, "b": b}).dropna()
    r = pair["a"].corr(pair["b"])
    put(name, r, (1 - r ** 2) / math.sqrt(len(pair) - 3), support=len(pair), primary=primary)


df = pd.read_csv("visits.csv")
df["sbp"] = pd.to_numeric(df["sbp"], errors="coerce")
df = df.sort_values(["patient_id", "visit_date"])
df["order"] = df.groupby("patient_id").cumcount() + 1
wide = df[df["order"] <= 3].pivot_table(index="patient_id", columns="order", values="sbp", aggfunc="first")
wide = wide.reindex(columns=[1, 2, 3])
correlation("first_second_correlation", wide[1], wide[2], primary=True)
correlation("first_third_correlation", wide[1], wide[3])
falls = (wide[2] < wide[1])[wide[2].notna()]
put("share_second_below_first", falls.mean(), math.sqrt(falls.mean() * (1 - falls.mean()) / len(falls)),
    support=int(min(falls.sum(), len(falls) - falls.sum())))
means = df.groupby("patient_id")["sbp"].mean().rename("patient_mean")
merged = df.merge(means, left_on="patient_id", right_index=True, how="left")
deviation = merged["sbp"] - merged["patient_mean"]
several = merged.groupby("patient_id")["sbp"].transform("size") >= 2
put("within_patient_sd", deviation[several].std(), support=int(merged.loc[several, "patient_id"].nunique()),
    judged=False)
put("between_patient_sd", means.std(), support=len(means), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

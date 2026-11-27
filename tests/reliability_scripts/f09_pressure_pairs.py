"""Blood pressure pairs split into systolic and diastolic: their correlation and the pulse pressure (family F9, charting.csv)."""
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


df = pd.read_csv("charting.csv")
pressure = df[df["item"] == "BP"].copy()
parts = pressure["value"].str.split("/", expand=True)
pressure["systolic"] = pd.to_numeric(parts[0], errors="coerce")
pressure["diastolic"] = pd.to_numeric(parts[1], errors="coerce")
pairs = pressure.dropna(subset=["systolic", "diastolic"])
checks["kept_pressure_pairs"] = int(len(pairs))
r = pairs["systolic"].corr(pairs["diastolic"])
put("systolic_diastolic_correlation", r, (1 - r ** 2) / math.sqrt(len(pairs) - 3),
    support=pairs["patient_id"].nunique(), primary=True)
for name, values in (("systolic_mean", pairs["systolic"]),
                     ("pulse_pressure_mean", pairs["systolic"] - pairs["diastolic"])):
    mean = values.mean()
    sums = (values - mean).groupby(pairs["patient_id"]).sum()
    put(name, mean, math.sqrt((sums ** 2).sum()) / len(values), support=pairs["patient_id"].nunique())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Cleaning the results: the sentinel of the numeric copy, the "<" results, potassium with its unit read in any case (family F9, labs.csv)."""
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


df = pd.read_csv("labs.csv")
SENTINEL = 9999999
number = pd.to_numeric(df["result"], errors="coerce")
copy = pd.to_numeric(df["result_num"], errors="coerce")
people = df["patient_id"].nunique()
put("sentinel_exactly_where_text_is_not_a_number", ((copy == SENTINEL) == number.isna()).mean(), support=people,
    primary=True)
put("copy_equals_text_where_a_number", (copy[number.notna()] == number[number.notna()]).mean(), support=people)
troponin = df["test"] == "TROP"
below = df.loc[troponin, "result"].astype("string").str.startswith("<").fillna(False)
put("troponin_below_limit_share", below.mean(), math.sqrt(below.mean() * (1 - below.mean()) / len(below)),
    support=df.loc[troponin, "patient_id"].nunique(), judged=False)
potassium = (df["test"] == "K") & df["unit"].astype("string").str.upper().eq("MMOL/L").fillna(False)
values = copy[potassium]
values = values[values != SENTINEL]
mean = values.mean()
sums = (values - mean).groupby(df.loc[values.index, "patient_id"]).sum()
put("potassium_mean", mean, math.sqrt((sums ** 2).sum()) / len(values), support=df.loc[potassium, "patient_id"].nunique(),
    primary=True)
put("rows_with_sentinel", (copy == SENTINEL).mean(), support=people, judged=False)
checks["kept_potassium_rows"] = int(len(values))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

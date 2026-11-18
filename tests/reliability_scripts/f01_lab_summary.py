"""A summary table of the laboratory: each test's mean, its share flagged, protein words (family F1, labs.csv)."""
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


def clustered_mean(name, values, patients, primary=False, judged=True):
    frame = pd.DataFrame({"v": values, "g": patients}).dropna()
    mean = frame["v"].mean()
    sums = (frame["v"] - mean).groupby(frame["g"]).sum()
    put(name, mean, math.sqrt((sums ** 2).sum()) / len(frame), support=frame["g"].nunique(), primary=primary,
        judged=judged)


df = pd.read_csv("labs.csv")
number = pd.to_numeric(df["result"], errors="coerce")
for test, name, primary in (("HGB", "haemoglobin_mean", True), ("CREAT", "creatinine_mean", True),
                            ("SOD", "sodium_mean", False), ("INR", "inr_mean", None)):
    rows = df["test"] == test
    clustered_mean(name, number[rows], df.loc[rows, "patient_id"], bool(primary), primary is not None)
potassium = df["test"] == "K"
flagged = pd.to_numeric(df.loc[potassium, "abnormal"], errors="coerce").eq(1).astype(float)
clustered_mean("potassium_flagged_share", flagged, df.loc[potassium, "patient_id"], judged=False)
protein = df["test"] == "UPROT"
clustered_mean("protein_negative_share", df.loc[protein, "result"].eq("NEG").astype(float),
               df.loc[protein, "patient_id"], judged=False)
tests = df.groupby("patient_id").size()
put("tests_per_patient", tests.mean(), tests.std() / math.sqrt(len(tests)), support=len(tests), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

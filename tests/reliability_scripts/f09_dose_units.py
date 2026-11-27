"""Dose texts split into amount and unit: one unit a drug, amounts put into one scale (family F9, orders.csv)."""
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


df = pd.read_csv("orders.csv")
parts = df["dose"].str.split(" ", n=1, expand=True)
df["amount"] = pd.to_numeric(parts[0], errors="coerce")
df["unit"] = parts[1]
checks["unparsed_dose"] = float(df["amount"].isna().mean())
usual = df.groupby("drug")["unit"].agg(lambda units: units.value_counts().index[0])
df["usual_unit"] = df["drug"].map(usual)
put("rows_in_their_drug_s_unit", (df["unit"] == df["usual_unit"]).mean(), support=df["patient_id"].nunique(),
    primary=True)
put("every_drug_in_one_unit", (df.groupby("drug")["unit"].nunique() == 1).mean(), support=df["drug"].nunique())
scale = {"g": 1000.0, "mg": 1.0, "mcg": 0.001}
df["amount_mg"] = df["amount"] * df["unit"].map(scale)
for drug, name in (("fentanyl", "fentanyl_mean_mg"), ("cefazolin", "cefazolin_mean_mg"),
                   ("acetaminophen", "acetaminophen_mean_mg")):
    rows = df["drug"] == drug
    clustered_mean(name, df.loc[rows, "amount_mg"], df.loc[rows, "patient_id"], judged=(drug == "cefazolin"))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

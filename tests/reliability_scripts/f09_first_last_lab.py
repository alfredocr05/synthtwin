"""First and last glucose of each patient, and the nearest earlier potassium before each creatinine (family F9, labs.csv)."""
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
df["collected"] = pd.to_datetime(df["collected_at"], format="%Y-%m-%d %H:%M", errors="coerce")
df["value"] = pd.to_numeric(df["result"], errors="coerce")
df = df.dropna(subset=["collected"]).sort_values(["patient_id", "collected"])
glucose = df[(df["test"] == "GLU") & df["unit"].eq("mg/dL")].dropna(subset=["value"])
ends = glucose.groupby("patient_id")["value"].agg(["first", "last", "size"])
ends = ends[ends["size"] >= 2]
r = ends["first"].corr(ends["last"])
put("first_last_glucose_correlation", r, (1 - r ** 2) / math.sqrt(len(ends) - 3), support=len(ends), primary=True)
put("last_minus_first_glucose", (ends["last"] - ends["first"]).mean(),
    (ends["last"] - ends["first"]).std() / math.sqrt(len(ends)), support=len(ends))
creatinine = df[df["test"] == "CREAT"].dropna(subset=["value"]).sort_values("collected")
potassium = df[df["test"] == "K"].dropna(subset=["value"]).sort_values("collected")
paired = pd.merge_asof(creatinine[["patient_id", "collected", "value"]],
                       potassium[["patient_id", "collected", "value"]].rename(columns={"value": "potassium"}),
                       on="collected", by="patient_id", direction="backward")
paired = paired.dropna(subset=["potassium"])
checks["kept_creatinine_with_earlier_potassium"] = int(len(paired))
r = paired["value"].corr(paired["potassium"])
put("creatinine_potassium_correlation", r, (1 - r ** 2) / math.sqrt(len(paired) - 3),
    support=paired["patient_id"].nunique(), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

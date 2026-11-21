"""Values by item key: numbers per key, temperatures put into Celsius, a choice list's shares (family F9, charting.csv)."""
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


df = pd.read_csv("charting.csv")
number = pd.to_numeric(df["value"], errors="coerce")
item = df["item"]
fahrenheit = df["unit"].astype("string").str.upper().isin(["F", "DEGF"]).fillna(False)
celsius = number.where(~fahrenheit, (number - 32) * 5 / 9)
clustered_mean("heart_rate_mean", number[item == "HR"], df.loc[item == "HR", "patient_id"], primary=True)
clustered_mean("temperature_celsius_mean", celsius[item == "TEMP"], df.loc[item == "TEMP", "patient_id"],
               primary=True)
clustered_mean("saturation_mean", number[item == "SPO2"], df.loc[item == "SPO2", "patient_id"], judged=False)
clustered_mean("respiratory_rate_mean", number[item == "RR"], df.loc[item == "RR", "patient_id"], judged=False)
clustered_mean("pain_score_mean", number[item == "PAIN"], df.loc[item == "PAIN", "patient_id"], judged=False)
alert = df.loc[item == "LOC", "value"].eq("Alert").astype(float)
clustered_mean("share_alert", alert, df.loc[item == "LOC", "patient_id"])
room_air = df.loc[item == "O2DEV", "value"].eq("Room air").astype(float)
clustered_mean("share_room_air", room_air, df.loc[item == "O2DEV", "patient_id"], judged=False)
checks["heart_rate_rows_not_numbers"] = float(number[item == "HR"].isna().mean())
checks["kept_temperature_rows"] = int((item == "TEMP").sum())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

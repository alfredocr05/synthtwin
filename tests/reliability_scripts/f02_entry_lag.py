"""Charted against entered times: the lag of device rows and of rows typed by hand (family F2, charting.csv)."""
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


df = pd.read_csv("charting.csv")
charted = pd.to_datetime(df["charted_at"], format="%Y-%m-%d %H:%M", errors="coerce")
entered = pd.to_datetime(df["entered_at"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_entered_at"] = float(entered.isna().mean())
df["lag"] = (entered - charted).dt.total_seconds() / 60
device = df["device"].eq("Y")
lag_device = df.loc[device, "lag"].dropna()
lag_hand = df.loc[~device, "lag"].dropna()
put("device_rows_entered_at_once", (lag_device == 0).mean(), support=df.loc[device, "patient_id"].nunique(),
    primary=True)
put("hand_rows_entered_at_once", (lag_hand == 0).mean(), support=df.loc[~device, "patient_id"].nunique(),
    judged=False)
mean = lag_hand.mean()
sums = (lag_hand - mean).groupby(df.loc[lag_hand.index, "patient_id"]).sum()
put("hand_rows_mean_lag", mean, math.sqrt((sums ** 2).sum()) / len(lag_hand),
    support=df.loc[~device, "patient_id"].nunique(), primary=True)
put("hand_rows_median_lag", lag_hand.median(), support=df.loc[~device, "patient_id"].nunique(), judged=False)
u = stats.mannwhitneyu(lag_hand, lag_device, alternative="two-sided")
put("lag_rank_effect", u.statistic / (len(lag_hand) * len(lag_device)) - 0.5, p=u.pvalue,
    support=min(df.loc[device, "patient_id"].nunique(), df.loc[~device, "patient_id"].nunique()), judged=False)
put("negative_lag_share", (df["lag"] < 0).mean(), support=df["patient_id"].nunique())

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

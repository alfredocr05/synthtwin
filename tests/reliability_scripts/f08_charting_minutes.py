"""The minutes charted: hand-typed rows on five-minute marks, device rows at any minute (family F8, charting.csv)."""
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
checks["unparsed_charted_at"] = float(charted.isna().mean())
on_mark = (charted.dt.minute % 5 == 0).astype(float)
device = df["device"].eq("Y")
hand, machine = on_mark[~device].dropna(), on_mark[device].dropna()
difference = hand.mean() - machine.mean()
se = math.sqrt(hand.mean() * (1 - hand.mean()) / len(hand) + machine.mean() * (1 - machine.mean()) / len(machine))
p = 2 * stats.norm.sf(abs(difference) / se) if se > 0 else 1.0
put("five_minute_mark_difference", difference, se, p,
    min(df.loc[device, "patient_id"].nunique(), df.loc[~device, "patient_id"].nunique()), primary=True)
put("hand_rows_on_five_minute_marks", hand.mean(), math.sqrt(hand.mean() * (1 - hand.mean()) / len(hand)),
    support=df.loc[~device, "patient_id"].nunique())
put("night_share", ((charted.dt.hour < 7) | (charted.dt.hour >= 22)).mean(), support=df["patient_id"].nunique(),
    judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

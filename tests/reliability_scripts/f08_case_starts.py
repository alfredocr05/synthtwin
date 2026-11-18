"""When cases are scheduled: weekend share, the first slot of the day, the starting hour (family F8, cases.csv)."""
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


df = pd.read_csv("cases.csv")
scheduled = pd.to_datetime(df["sched_start"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_sched_start"] = float(scheduled.isna().mean())
scheduled = scheduled.dropna()
n = len(scheduled)
for name, flag, primary in (("weekend_share", scheduled.dt.dayofweek >= 5, True),
                            ("first_slot_share", (scheduled.dt.hour == 7) & (scheduled.dt.minute == 30), True),
                            ("afternoon_share", scheduled.dt.hour >= 12, None)):
    value = flag.mean()
    put(name, value, math.sqrt(value * (1 - value) / n), support=int(min(flag.sum(), n - flag.sum())),
        primary=bool(primary), judged=primary is not None)
hours = scheduled.dt.hour + scheduled.dt.minute / 60
put("mean_start_hour", hours.mean(), hours.std() / math.sqrt(n), support=n)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

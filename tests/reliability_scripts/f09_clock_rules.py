"""The clocks of a case: universal time six hours after local time, the steps in order, the start delay (family F9, cases.csv)."""
import json

import pandas as pd

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cases.csv")
stamps = {}
for column in ("sched_start", "in_room", "incision", "close", "out_room"):
    stamps[column] = pd.to_datetime(df[column], format="%Y-%m-%d %H:%M", errors="coerce")
universal = pd.to_datetime(df["in_room_utc"], format="%Y-%m-%dT%H:%MZ", errors="coerce")
checks["unparsed_in_room_utc"] = float(universal.isna().mean())
people = df["patient_id"].nunique()
offset = (universal - stamps["in_room"]).dt.total_seconds() / 60
put("six_hours_apart", (offset == 360).mean(), support=people, primary=True)
in_order = ((stamps["in_room"] <= stamps["incision"]) & (stamps["incision"] <= stamps["close"])
            & (stamps["close"] <= stamps["out_room"]))
put("steps_in_order", in_order.mean(), support=people, primary=True)
delay = (stamps["in_room"] - stamps["sched_start"]).dt.total_seconds() / 60
on_time = (delay == 0).mean()
put("on_time_share", on_time, (on_time * (1 - on_time) / len(delay)) ** 0.5, support=int((delay == 0).sum()))
put("early_share", (delay < 0).mean(), support=int((delay < 0).sum()), judged=False)
put("median_delay", delay.median(), support=people, judged=False)
setup = (stamps["incision"] - stamps["in_room"]).dt.total_seconds() / 60
put("median_set_up", setup.median(), support=people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Orders per patient among the patients with any: the mean, the heavy tail (family F5, orders.csv)."""
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


df = pd.read_csv("orders.csv")
per_patient = df.groupby("patient_id").size()
people = len(per_patient)
put("mean_orders_per_patient", per_patient.mean(), per_patient.std() / math.sqrt(people), support=people,
    primary=True)
put("mean_log_orders_per_patient", per_patient.map(math.log).mean(),
    per_patient.map(math.log).std() / math.sqrt(people), support=people, judged=False)
for limit in (1, 20):
    flag = per_patient == limit if limit == 1 else per_patient >= limit
    share = flag.mean()
    put(f"share_{'one_order' if limit == 1 else 'twenty_or_more'}", share, math.sqrt(share * (1 - share) / people),
        support=int(min(flag.sum(), people - flag.sum())))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

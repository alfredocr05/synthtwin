"""How many visits each patient has (family F1, visits.csv)."""
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


df = pd.read_csv("visits.csv")
per_patient = df.groupby("patient_id").size()
people = len(per_patient)
put("mean_visits_per_patient", per_patient.mean(), per_patient.std() / math.sqrt(people), support=people,
    primary=True)
one = (per_patient == 1).mean()
put("share_with_one_visit", one, math.sqrt(one * (1 - one) / people), support=int((per_patient == 1).sum()))
many = (per_patient >= 20).mean()
put("share_with_twenty_or_more", many, math.sqrt(many * (1 - many) / people), support=int((per_patient >= 20).sum()))
arm = df.groupby("patient_id")["arm"].first()
share = arm.eq("B").mean()
put("share_arm_b", share, math.sqrt(share * (1 - share) / people), support=int(min(arm.eq("B").sum(), people - arm.eq("B").sum())),
    judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

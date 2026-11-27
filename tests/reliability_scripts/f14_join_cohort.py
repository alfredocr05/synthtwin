"""Orders linked to the cohort by patient: the share found, orders per cohort patient by diabetes (family F14, orders.csv and cohort.csv)."""
import json

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


orders = pd.read_csv("orders.csv")
cohort = pd.read_csv("cohort.csv")
counts = orders.groupby("patient_id").size().rename("orders")
found = counts.index.isin(cohort["patient_id"])
put("order_patients_found_in_cohort", found.mean(), support=len(counts), primary=True)
linked = cohort.merge(counts, left_on="patient_id", right_index=True, how="left")
linked["orders"] = linked["orders"].fillna(0)
linked["diabetes"] = linked["diabetes"].eq("Y").astype(int)
linked["age_c"] = (pd.to_numeric(linked["age"], errors="coerce") - 57) / 10
put("cohort_share_with_orders", (linked["orders"] > 0).mean(), support=len(linked))
fit = smf.glm("orders ~ diabetes + age_c", data=linked.dropna(subset=["age_c"]),
              family=sm.families.Poisson()).fit(cov_type="HC0")
put("orders_by_diabetes", fit.params["diabetes"], fit.bse["diabetes"], fit.pvalues["diabetes"],
    int(min(linked["diabetes"].sum(), len(linked) - linked["diabetes"].sum())))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Kaplan-Meier curves of the time to the first hospitalisation by arm, derived from the visits, and the log-rank test (family F15, visits.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.duration.survfunc import SurvfuncRight, survdiff


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("visits.csv")
df["visit_date"] = pd.to_datetime(df["visit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_visit_date"] = float(df["visit_date"].isna().mean())
df = df.dropna(subset=["visit_date"]).sort_values(["patient_id", "visit_date"])
df["day"] = (df["visit_date"] - df.groupby("patient_id")["visit_date"].transform("min")).dt.days
df["hosp"] = df["hospitalized"].eq("Y")
later = df[df["day"] > 0]
event_day = later[later["hosp"]].groupby("patient_id")["day"].min()
last_day = later.groupby("patient_id")["day"].max()
arm = df.groupby("patient_id")["arm"].first()
data = pd.DataFrame({"last": last_day}).join(event_day.rename("event"), how="left").join(arm)
data["time"] = data["event"].fillna(data["last"])
data["status"] = data["event"].notna().astype(int)
data["arm_b"] = data["arm"].eq("B").astype(int)
checks["kept_patients"] = int(len(data))


def survival_at(frame, day):
    curve = SurvfuncRight(frame["time"].to_numpy(), frame["status"].to_numpy())
    times = np.asarray(curve.surv_times)
    before = np.nonzero(times <= day)[0]
    if len(before) == 0:
        return 1.0, 0.0
    return float(curve.surv_prob[before[-1]]), float(curve.surv_prob_se[before[-1]])


a, b = data[data["arm_b"] == 0], data[data["arm_b"] == 1]
events = int(min(a["status"].sum(), b["status"].sum()))
sa, ea = survival_at(a, 180)
sb, eb = survival_at(b, 180)
se = math.sqrt(ea ** 2 + eb ** 2)
put("free_at_180_days_b_minus_a", sb - sa, se, math.erfc(abs(sb - sa) / se / math.sqrt(2)), events, primary=True)
put("free_at_180_days_a", sa, ea, support=int(a["status"].sum()))
put("free_at_180_days_b", sb, eb, support=int(b["status"].sum()))
chi2, p = survdiff(data["time"].to_numpy(), data["status"].to_numpy(), data["arm_b"].to_numpy())
put("log_rank_chi_square", chi2, p=p, support=events, judged=False)
fit = smf.phreg("time ~ arm_b", data=data, status=data["status"].to_numpy(), ties="breslow").fit()
put("hazard_ratio_log_arm_b", fit.params[0], fit.bse[0], fit.pvalues[0], events)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""Recovery-room minutes: by class (Kruskal-Wallis), with operating time (Spearman), by emergency (family F2, cases.csv)."""
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


df = pd.read_csv("cases.csv")
incision = pd.to_datetime(df["incision"], format="%Y-%m-%d %H:%M", errors="coerce")
close = pd.to_datetime(df["close"], format="%Y-%m-%d %H:%M", errors="coerce")
data = pd.DataFrame({
    "recovery": pd.to_numeric(df["recovery_min"], errors="coerce"),
    "minutes": (close - incision).dt.total_seconds() / 60,
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "emergency": df["emergency"].eq("Y"),
}).dropna()
rho, p = stats.spearmanr(data["minutes"], data["recovery"])
put("recovery_with_operating_time", rho, (1 - rho ** 2) / math.sqrt(len(data) - 3), p, len(data), primary=True)
samples = [data.loc[data["risk_class"] == level, "recovery"] for level in (1, 2, 3, 4)]
h, p = stats.kruskal(*samples)
put("recovery_by_class_epsilon_squared", h / (len(data) - 1), p=p, support=min(len(s) for s in samples), judged=False)
a, b = data.loc[data["emergency"], "recovery"], data.loc[~data["emergency"], "recovery"]
u = stats.mannwhitneyu(a, b, alternative="two-sided")
area = u.statistic / (len(a) * len(b))
q1, q2 = area / (2 - area), 2 * area ** 2 / (1 + area)
spread = math.sqrt((area * (1 - area) + (len(a) - 1) * (q1 - area ** 2) + (len(b) - 1) * (q2 - area ** 2))
                   / (len(a) * len(b)))
put("recovery_by_emergency_rank_effect", area - 0.5, spread, u.pvalue, min(len(a), len(b)))
put("median_recovery", data["recovery"].median(), support=len(data), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

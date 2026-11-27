"""Tests for repeated measurements without a model: Cochran's Q and McNemar on hospitalisation over the first visits, the signed-rank test and Page's trend test on the pressure (family F30, visits.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.contingency_tables import cochrans_q, mcnemar


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("visits.csv")
df["sbp"] = pd.to_numeric(df["sbp"], errors="coerce")
df["visit_date"] = pd.to_datetime(df["visit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_visit_date"] = float(df["visit_date"].isna().mean())
df = df.dropna(subset=["sbp", "visit_date"]).sort_values(["patient_id", "visit_date"])
df["order"] = df.groupby("patient_id").cumcount() + 1
df["hosp"] = df["hospitalized"].eq("Y").astype(int)
three = df[df["order"] <= 3]
three = three[three.groupby("patient_id")["order"].transform("size") == 3]
checks["kept_patients_with_three"] = int(three["patient_id"].nunique())
yes = three.pivot(index="patient_id", columns="order", values="hosp")
q = cochrans_q(yes[[1, 2, 3]].to_numpy())
first_minus_third = float(yes[1].mean() - yes[3].mean())
pairs = yes[1] - yes[3]
se = math.sqrt(max(pairs.var(ddof=1), 1e-12) / len(pairs))
put("hospitalised_first_minus_third", first_minus_third, se, float(q.pvalue), int(min(yes[1].sum(), yes[3].sum())),
    primary=True)
table = pd.crosstab(yes[1], yes[2]).reindex(index=[0, 1], columns=[0, 1], fill_value=0).to_numpy()
test = mcnemar(table, exact=False, correction=True)
discordant = int(table[0, 1] + table[1, 0])
change = (table[0, 1] - table[1, 0]) / table.sum()
se_change = math.sqrt(max(discordant - (table[0, 1] - table[1, 0]) ** 2 / table.sum(), 1e-12)) / table.sum()
put("hospitalised_second_minus_first", change, se_change, float(test.pvalue), int(min(table[0, 1], table[1, 0])))
pressure = three.pivot(index="patient_id", columns="order", values="sbp")
arm = three.groupby("patient_id")["arm"].first().reindex(pressure.index)
for label in ("A", "B"):
    mine = pressure[arm.eq(label).to_numpy()]
    differences = (mine[3] - mine[1]).to_numpy()
    signed = stats.wilcoxon(mine[3], mine[1])
    # the signed-rank test's effect as the share of patients whose pressure fell minus the share whose rose
    fell, rose = float(np.mean(differences < 0)), float(np.mean(differences > 0))
    se_net = math.sqrt(max(fell + rose - (fell - rose) ** 2, 1e-12) / len(differences))
    put(f"arm_{label.lower()}_net_share_falling_first_to_third", fell - rose, se_net, float(signed.pvalue),
        len(differences), primary=label == "B")
page = stats.page_trend_test(-pressure[[1, 2, 3]].to_numpy())
put("page_trend_statistic", float(page.statistic), p=float(page.pvalue), support=len(pressure), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

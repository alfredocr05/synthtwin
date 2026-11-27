"""ROC with repeated measurements: the area of the pressure for a hospitalisation over every visit, its variance clustered by patient (Obuchowski), two markers compared, and the area at the first visits (family F38, visits.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def placements(marker, outcome):
    """Each positive row's share of negatives it exceeds (ties a half), and each negative row's share of positives above it."""
    pos, neg = marker[outcome == 1], marker[outcome == 0]
    ranked = stats.rankdata(np.concatenate([pos, neg]))
    v10 = (ranked[: len(pos)] - stats.rankdata(pos)) / len(neg)
    v01 = 1.0 - (ranked[len(pos):] - stats.rankdata(neg)) / len(pos)
    return v10, v01


def clustered(markers, outcome, cluster):
    """The areas of several markers and their covariance with the rows clustered (Obuchowski 1997)."""
    codes, _ = pd.factorize(cluster)
    clusters = codes.max() + 1
    m, n = int((outcome == 1).sum()), int((outcome == 0).sum())
    m_i = np.bincount(codes[outcome == 1], minlength=clusters)
    n_i = np.bincount(codes[outcome == 0], minlength=clusters)
    areas, tens, ones = [], [], []
    for marker in markers:
        v10, v01 = placements(marker, outcome)
        area = v10.mean()
        areas += [area]
        tens += [np.bincount(codes[outcome == 1], weights=v10, minlength=clusters) - m_i * area]
        ones += [np.bincount(codes[outcome == 0], weights=v01, minlength=clusters) - n_i * area]
    k = len(markers)
    cov = np.zeros((k, k))
    factor = clusters / (clusters - 1)
    for a in range(k):
        for b in range(k):
            s10 = factor * np.sum(tens[a] * tens[b]) / m
            s01 = factor * np.sum(ones[a] * ones[b]) / n
            s11 = factor * np.sum(tens[a] * ones[b])
            cov[a, b] = s10 / m + s01 / n + 2 * s11 / (m * n)
    return np.array(areas), cov, m, n


df = pd.read_csv("visits.csv")
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "visit": pd.to_numeric(df["visit"], errors="coerce"),
    "sbp": pd.to_numeric(df["sbp"], errors="coerce"),
    "loss": pd.to_numeric(df["blood_loss_ml"], errors="coerce"),
    "hospitalized": df["hospitalized"].eq("Y").astype(int),
}).dropna().sort_values(["patient_id", "visit"])
checks["kept_rows"] = int(len(data))
outcome = data["hospitalized"].to_numpy()
areas, cov, m, n = clustered([data["sbp"].to_numpy(dtype=float), data["loss"].to_numpy(dtype=float)], outcome,
                             data["patient_id"].to_numpy())
people = data.groupby("patient_id")["hospitalized"].max()
support = int(min(people.sum(), len(people) - people.sum()))
put("area_pressure_all_visits", areas[0], math.sqrt(cov[0, 0]), support=support, primary=True)
put("area_blood_loss_all_visits", areas[1], math.sqrt(cov[1, 1]), support=support)
difference = areas[0] - areas[1]
spread = math.sqrt(cov[0, 0] + cov[1, 1] - 2 * cov[0, 1])
put("area_pressure_minus_blood_loss", difference, spread, math.erfc(abs(difference / spread) / math.sqrt(2)), support)
naive = placements(data["sbp"].to_numpy(dtype=float), outcome)
naive_se = math.sqrt(np.var(naive[0], ddof=1) / m + np.var(naive[1], ddof=1) / n)
put("area_pressure_naive_se", naive_se, support=support, judged=False)
put("clustered_over_naive_se", math.sqrt(cov[0, 0]) / naive_se, support=support, judged=False)
data["order"] = data.groupby("patient_id").cumcount() + 1
for visit in (1, 3):
    at = data[data["order"] == visit]
    y = at["hospitalized"].to_numpy()
    v10, v01 = placements(at["sbp"].to_numpy(dtype=float), y)
    se = math.sqrt(np.var(v10, ddof=1) / len(v10) + np.var(v01, ddof=1) / len(v01))
    put(f"area_pressure_visit_{visit}", v10.mean(), se, support=int(min(y.sum(), len(y) - y.sum())))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

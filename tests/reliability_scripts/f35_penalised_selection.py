"""Penalised regression and the stability of its selection: a lasso logistic model of a complication on eight markers and three patient columns (penalty by five-fold cross-validation), its coefficients' standard errors and its selection over a hundred bootstrap samples, a ridge model, and the cross-validated area with DeLong's error (family F35, operations.csv)."""
import json

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
from scipy import stats


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("operations.csv")
markers = ["albumin", "crp", "hemoglobin", "lactate", "sodium", "platelets", "glucose", "bilirubin"]
data = pd.DataFrame({name: pd.to_numeric(df[name], errors="coerce") for name in markers})
data["crp"] = np.log(data["crp"])
data["lactate"] = np.log(data["lactate"].where(data["lactate"] > 0))
data["age"] = pd.to_numeric(df["age"], errors="coerce")
data["female"] = df["gender"].eq("F").astype(int)
data["emergency"] = df["emergency"].eq("Y").astype(int)
data["complication"] = df["complication"].eq("Y").astype(int)
data = data.replace([np.inf, -np.inf], np.nan).dropna()
checks["kept_rows"] = int(len(data))
candidates = markers + ["age", "female", "emergency"]
x = data[candidates].to_numpy(dtype=float)
x = (x - x.mean(axis=0)) / x.std(axis=0)
y = data["complication"].to_numpy()
events = int(y.sum())
support = int(min(events, len(y) - events))
penalties = np.logspace(-3, 0, 13)
folds = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=0).split(x, y))
loss = []
for c in penalties:
    total = 0.0
    for train, test in folds:
        model = LogisticRegression(penalty="l1", C=c, solver="liblinear", max_iter=2000).fit(x[train], y[train])
        chance = np.clip(model.predict_proba(x[test])[:, 1], 1e-12, 1 - 1e-12)
        total -= float(np.sum(y[test] * np.log(chance) + (1 - y[test]) * np.log(1 - chance)))
    loss += [total]
best = float(penalties[int(np.argmin(loss))])
lasso = LogisticRegression(penalty="l1", C=best, solver="liblinear", max_iter=2000).fit(x, y)
ridge = LogisticRegression(penalty="l2", C=0.01, solver="lbfgs", max_iter=2000).fit(x, y)
# A hundred bootstrap samples (forty left the errors themselves 11 per cent noisy): each coefficient's standard error
# (their spread) and each candidate's selection share at the chosen penalty, the selection's stability.
draws = np.random.default_rng(7)
chosen = np.zeros(len(candidates))
lasso_boot, ridge_boot = [], []
for _ in range(100):
    pick = draws.integers(0, len(y), len(y))
    model = LogisticRegression(penalty="l1", C=best, solver="liblinear", max_iter=2000).fit(x[pick], y[pick])
    chosen += model.coef_[0] != 0
    lasso_boot += [model.coef_[0]]
    ridge_boot += [LogisticRegression(penalty="l2", C=0.01, solver="lbfgs", max_iter=2000).fit(x[pick], y[pick]).coef_[0]]
chosen /= 100
lasso_se, ridge_se = np.std(lasso_boot, axis=0, ddof=1), np.std(ridge_boot, axis=0, ddof=1)
true_ones = ("albumin", "crp", "lactate", "emergency", "age")
for k, name in enumerate(candidates):
    put(f"lasso_{name}", lasso.coef_[0][k], lasso_se[k] if lasso_se[k] > 0 else None, support=support,
        primary=(name == "albumin"), judged=name in true_ones)
    put(f"ridge_{name}", ridge.coef_[0][k], ridge_se[k] if ridge_se[k] > 0 else None, support=support,
        judged=name in true_ones + ("hemoglobin",))
    put(f"selected_share_{name}", chosen[k], support=support, judged=False)
put("lasso_selected", int(np.sum(lasso.coef_[0] != 0)), support=support, judged=False)
put("lasso_penalty_log10", np.log10(best), support=support, judged=False)
null = [k for k, name in enumerate(candidates) if name in ("sodium", "platelets", "glucose", "female")]
# The unrelated candidates' selection share: reported, not judged (between two real samples it moves from 0.5 to 0.85)
put("selected_share_of_unrelated", float(np.mean(chosen[null])), support=support, judged=False)
scores = np.zeros(len(y))
for train, test in folds:
    model = LogisticRegression(penalty="l1", C=best, solver="liblinear", max_iter=2000).fit(x[train], y[train])
    scores[test] = model.decision_function(x[test])
area = roc_auc_score(y, scores)
cases, controls = scores[y == 1], scores[y == 0]
ranked = stats.rankdata(np.concatenate([cases, controls]))
v10 = (ranked[: len(cases)] - stats.rankdata(cases)) / len(controls)
v01 = 1.0 - (ranked[len(cases):] - stats.rankdata(controls)) / len(cases)
put("cross_validated_auc", area, float(np.sqrt(np.var(v10, ddof=1) / len(cases) + np.var(v01, ddof=1) / len(controls))),
    support=support)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

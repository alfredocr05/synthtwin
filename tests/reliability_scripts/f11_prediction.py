"""Prediction: a logistic model and boosting trained on this table, tested on the held-out patients (family F11, cohort.csv and cohort_holdout.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import roc_auc_score

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


def area_error(area, positives, negatives):
    """Hanley and McNeil's standard error of an area under the curve."""
    q1, q2 = area / (2 - area), 2 * area ** 2 / (1 + area)
    return np.sqrt((area * (1 - area) + (positives - 1) * (q1 - area ** 2) + (negatives - 1) * (q2 - area ** 2))
                   / (positives * negatives))


def features(frame):
    creat = pd.to_numeric(frame["creat"].astype("string").str.replace("<", "", regex=False), errors="coerce")
    table = pd.DataFrame({
        "age": pd.to_numeric(frame["age"], errors="coerce") / 10,
        "risk_class": pd.to_numeric(frame["risk_class"], errors="coerce"),
        "diabetes": frame["diabetes"].eq("Y").astype(int),
        "smoker": frame["smoker"].eq("Y").astype(int),
        "female": frame["gender"].eq("F").astype(int),
        "creat": creat.fillna(creat.median()),
    }).astype(float)
    return table, frame["complication"].eq("Y").astype(int)


train_x, train_y = features(pd.read_csv("cohort.csv"))
test_x, test_y = features(pd.read_csv("cohort_holdout.csv"))
keep = train_x.notna().all(axis=1)
train_x, train_y = train_x[keep], train_y[keep]
test_keep = test_x.notna().all(axis=1)
test_x, test_y = test_x[test_keep], test_y[test_keep]
model = sm.GLM(train_y, sm.add_constant(train_x), family=sm.families.Binomial()).fit()
risk = model.predict(sm.add_constant(test_x, has_constant="add"))
limit = int(min(test_y.sum(), len(test_y) - test_y.sum()))
positives, negatives = int(test_y.sum()), int(len(test_y) - test_y.sum())
area = roc_auc_score(test_y, risk)
put("auc_logistic_on_held_out", area, area_error(area, positives, negatives), support=limit, primary=True)
linear = np.log(risk / (1 - risk))
slope = sm.GLM(test_y, sm.add_constant(linear), family=sm.families.Binomial()).fit()
put("calibration_slope", slope.params.iloc[1], slope.bse.iloc[1], support=limit)
put("predicted_minus_observed", risk.mean() - test_y.mean(), support=limit, judged=False)
boost = HistGradientBoostingClassifier(max_iter=60, random_state=0).fit(train_x, train_y)
area = roc_auc_score(test_y, boost.predict_proba(test_x)[:, 1])
put("auc_boosting_on_held_out", area, area_error(area, positives, negatives), support=limit)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

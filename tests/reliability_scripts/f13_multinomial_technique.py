"""Multinomial model of the anaesthetic technique, general anaesthesia the reference (family F13, cohort.csv)."""
import json

import pandas as pd
import statsmodels.formula.api as smf

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("cohort.csv")
codes = {"GA": 0, "RA": 1, "SED": 2}
data = pd.DataFrame({
    "technique": df["technique"].map(codes),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 57) / 10,
    "class_3": (pd.to_numeric(df["risk_class"], errors="coerce") >= 3).astype(int),
}).dropna()
checks["kept_known_techniques"] = int(len(data))
fit = smf.mnlogit("technique ~ age_c + class_3", data=data).fit(disp=0, maxiter=200)
counts = data["technique"].value_counts()
for column, label in ((0, "regional"), (1, "sedation")):
    level = column + 1
    cells = pd.crosstab(data["technique"], data["class_3"]).reindex(index=[0, level], columns=[0, 1], fill_value=0)
    for term in ("class_3", "age_c"):
        support = int(cells.to_numpy().min()) if term == "class_3" else int(min(counts.get(0, 0), counts.get(level, 0)))
        put(f"{label}_{term}", fit.params.loc[term, column], fit.bse.loc[term, column], fit.pvalues.loc[term, column],
            support, primary=(label == "regional" and term == "class_3"),
            judged=(label == "regional" or term == "class_3"))
for label, code in codes.items():
    share = (data["technique"] == code).mean()
    put(f"share_{label}", share, (share * (1 - share) / len(data)) ** 0.5, support=int(counts.get(code, 0)),
        judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

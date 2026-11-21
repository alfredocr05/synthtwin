"""Glucose within patient: its intraclass correlation and its trend over the days (family F7, labs.csv)."""
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


df = pd.read_csv("labs.csv")
df["collected"] = pd.to_datetime(df["collected_at"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_collected_at"] = float(df["collected"].isna().mean())
df["day"] = (df["collected"] - df.groupby("patient_id")["collected"].transform("min")).dt.total_seconds() / 86400
glucose = df[df["test"] == "GLU"].copy()
glucose["value"] = pd.to_numeric(glucose["result"], errors="coerce")
in_mmol = glucose["unit"].eq("mmol/L")
glucose.loc[in_mmol, "value"] = glucose.loc[in_mmol, "value"] * 18
glucose = glucose.dropna(subset=["value", "day"])
checks["kept_glucose_rows"] = int(len(glucose))
fit = smf.mixedlm("value ~ day", data=glucose, groups=glucose["patient_id"]).fit(reml=True)
people = glucose["patient_id"].nunique()
between = float(fit.cov_re.iloc[0, 0])
put("intraclass_correlation", between / (between + fit.scale), support=people, primary=True)
put("day", fit.params["day"], fit.bse["day"], fit.pvalues["day"], people, primary=True)
put("mean_glucose", fit.params["Intercept"], fit.bse["Intercept"], None, people, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

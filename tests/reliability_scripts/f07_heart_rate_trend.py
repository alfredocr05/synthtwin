"""Heart rate over the hours of a stay, a mixed model with a random intercept per patient (family F7, charting.csv)."""
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


df = pd.read_csv("charting.csv")
df["charted"] = pd.to_datetime(df["charted_at"], format="%Y-%m-%d %H:%M", errors="coerce")
checks["unparsed_charted_at"] = float(df["charted"].isna().mean())
df["first"] = df.groupby("patient_id")["charted"].transform("min")
df["hours"] = (df["charted"] - df["first"]).dt.total_seconds() / 3600
rate = df[df["item"] == "HR"].copy()
rate["hr"] = pd.to_numeric(rate["value"], errors="coerce")
rate = rate.dropna(subset=["hr", "hours"])
checks["kept_heart_rate_rows"] = int(len(rate))
fit = smf.mixedlm("hr ~ hours", data=rate, groups=rate["patient_id"]).fit(reml=True)
people = rate["patient_id"].nunique()
put("hours", fit.params["hours"], fit.bse["hours"], fit.pvalues["hours"], people, primary=True)
between = float(fit.cov_re.iloc[0, 0])
put("intraclass_correlation", between / (between + fit.scale), support=people, judged=False)
put("intercept", fit.params["Intercept"], fit.bse["Intercept"], None, people)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

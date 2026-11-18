"""Linear regression of the log operating time on service, class and emergency (family F3, cases.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

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
checks["unparsed_incision"] = float(incision.isna().mean())
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "log_minutes": np.log((close - incision).dt.total_seconds() / 60),
    "service": df["service"],
    "risk_class": pd.to_numeric(df["risk_class"], errors="coerce"),
    "emergency": df["emergency"].eq("Y").astype(int),
}).dropna()
fit = smf.ols("log_minutes ~ C(service, Treatment('GEN')) + risk_class + emergency", data=data).fit(
    cov_type="cluster", cov_kwds={"groups": pd.factorize(data["patient_id"])[0]})
for term, label, primary in (("emergency", "emergency", True), ("risk_class", "risk_class", False),
                             ("C(service, Treatment('GEN'))[T.CARD]", "service_card", False),
                             ("C(service, Treatment('GEN'))[T.ORTHO]", "service_ortho", None),
                             ("C(service, Treatment('GEN'))[T.URO]", "service_uro", None)):
    if term == "risk_class":
        support = len(data)
    elif term == "emergency":
        support = int(min(data["emergency"].sum(), len(data) - data["emergency"].sum()))
    else:
        support = int((data["service"] == label.split("_")[1].upper()).sum())
    put(label, fit.params[term], fit.bse[term], fit.pvalues[term], support, bool(primary), primary is not None)
put("residual_sd", np.sqrt(fit.scale), support=len(data), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

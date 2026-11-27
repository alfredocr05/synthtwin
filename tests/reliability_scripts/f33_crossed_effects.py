"""A mixed model with crossed random effects: the operation's minutes with a random effect of the surgeon crossed with one of the anaesthetist (family F33, operations.csv)."""
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


df = pd.read_csv("operations.csv")
data = pd.DataFrame({
    "minutes": pd.to_numeric(df["minutes"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
    "emergency": df["emergency"].eq("Y").astype(int),
    "complication": df["complication"].eq("Y").astype(int),
    "surgeon": df["surgeon"],
    "anaesthetist": df["anaesthetist"],
}).dropna()
checks["kept_rows"] = int(len(data))
data["everyone"] = 1
fit = smf.mixedlm("minutes ~ age_c + emergency + complication", data=data, groups="everyone",
                  vc_formula={"surgeon": "0 + C(surgeon)", "anaesthetist": "0 + C(anaesthetist)"}).fit(reml=True)
for term, primary in (("complication", True), ("emergency", False), ("age_c", False)):
    support = len(data) if term == "age_c" else int(min(data[term].sum(), len(data) - data[term].sum()))
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], support, primary)
variances = dict(zip(fit.model.exog_vc.names, np.asarray(fit.vcomp)))
surgeons, anaesthetists = data["surgeon"].nunique(), data["anaesthetist"].nunique()
put("surgeon_sd", np.sqrt(variances["surgeon"]), support=surgeons)
put("anaesthetist_sd", np.sqrt(variances["anaesthetist"]), support=anaesthetists)
put("residual_sd", np.sqrt(fit.scale), support=len(data))
total = variances["surgeon"] + variances["anaesthetist"] + fit.scale
put("surgeon_share", variances["surgeon"] / total, support=surgeons, judged=False)
put("anaesthetist_share", variances["anaesthetist"] / total, support=anaesthetists, judged=False)
# The surgeon alone, as a researcher often fits first: a random intercept by surgeon.
alone = smf.mixedlm("minutes ~ age_c + emergency + complication", data=data, groups="surgeon").fit(reml=True)
put("surgeon_alone_sd", np.sqrt(float(alone.cov_re.iloc[0, 0])), support=surgeons, judged=False)
put("surgeon_alone_complication", alone.params["complication"], alone.bse["complication"],
    alone.pvalues["complication"], int(min(data["complication"].sum(), len(data) - data["complication"].sum())))

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

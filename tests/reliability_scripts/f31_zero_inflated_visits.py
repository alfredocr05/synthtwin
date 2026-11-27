"""Counts with many zeros: emergency visits after discharge by negative binomial, zero-inflated negative binomial and hurdle (logistic, then zero-truncated Poisson) models (family F31, operations.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.discrete.count_model import ZeroInflatedNegativeBinomialP
from statsmodels.discrete.truncated_model import TruncatedLFPoisson


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("operations.csv")
data = pd.DataFrame({
    "visits": pd.to_numeric(df["visits_after"], errors="coerce"),
    "complication": df["complication"].eq("Y").astype(int),
    "emergency": df["emergency"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
    "log_crp": np.log(pd.to_numeric(df["crp"], errors="coerce")),
}).dropna()
data = data[np.isfinite(data["log_crp"])]
data["crp_z"] = (data["log_crp"] - data["log_crp"].mean()) / data["log_crp"].std()
checks["kept_rows"] = int(len(data))
zeros = int((data["visits"] == 0).sum())
some = len(data) - zeros
in_complication = int(min(data["complication"].sum(), len(data) - data["complication"].sum()))
in_emergency = int(min(data["emergency"].sum(), len(data) - data["emergency"].sum()))

negative = smf.negativebinomial("visits ~ complication + crp_z + age_c + emergency", data=data).fit(disp=0, maxiter=300)
put("negbin_complication", negative.params["complication"], negative.bse["complication"],
    negative.pvalues["complication"], in_complication)
put("negbin_age_c", negative.params["age_c"], negative.bse["age_c"], negative.pvalues["age_c"], some)
put("negbin_alpha", negative.params["alpha"], negative.bse["alpha"], support=some, judged=False)

count_x = sm.add_constant(data[["complication", "crp_z"]].astype(float))
zero_x = sm.add_constant(data[["age_c", "emergency"]].astype(float))
model = ZeroInflatedNegativeBinomialP(data["visits"].astype(float), count_x, exog_infl=zero_x)
start = np.concatenate([np.zeros(zero_x.shape[1]), negative.params[["Intercept", "complication", "crp_z"]].to_numpy(),
                        [max(0.05, float(negative.params["alpha"]))]])
inflated = model.fit(start_params=start, method="bfgs", maxiter=1000, disp=0)
names = list(inflated.model.exog_names)
for term, key, support, primary in (("complication", "complication", in_complication, True),
                                    ("crp_z", "crp_z", some, False),
                                    ("inflate_age_c", "inflate_age_c", zeros, False),
                                    ("inflate_emergency", "inflate_emergency", in_emergency, False)):
    at = names.index(key)
    put(f"zinb_{term}", inflated.params.iloc[at], inflated.bse.iloc[at], inflated.pvalues.iloc[at], support, primary)
put("zinb_alpha", inflated.params.iloc[names.index("alpha")], support=some, judged=False)

# The hurdle: whether any visit (a logistic model), then how many among those with one (a zero-truncated Poisson model
# with errors robust to its overdispersion).
data["any"] = (data["visits"] > 0).astype(int)
first = smf.glm("any ~ complication + crp_z + age_c + emergency", data=data, family=sm.families.Binomial()).fit()
put("hurdle_any_age_c", first.params["age_c"], first.bse["age_c"], first.pvalues["age_c"], min(zeros, some))
positive = data[data["visits"] > 0]
second = TruncatedLFPoisson(positive["visits"].astype(float),
                            sm.add_constant(positive[["complication", "crp_z"]].astype(float))).fit(
    method="newton", maxiter=200, disp=0, cov_type="HC0")
at = list(second.model.exog_names).index("complication")
put("hurdle_count_complication", second.params.iloc[at], second.bse.iloc[at], second.pvalues.iloc[at],
    int(min(positive["complication"].sum(), len(positive) - positive["complication"].sum())))
put("zero_share", zeros / len(data), math.sqrt(zeros * some / len(data) ** 3), support=min(zeros, some), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

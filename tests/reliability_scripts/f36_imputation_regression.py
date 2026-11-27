"""Multiple imputation by chained equations, then regression: albumin, missing more often after a complication and in emergencies, imputed ten times and the complication's logistic model pooled by Rubin's rules, beside complete cases (family F36, operations.csv)."""
import json

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.imputation import mice


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


np.random.seed(2026)
df = pd.read_csv("operations.csv")
data = pd.DataFrame({
    "complication": df["complication"].eq("Y").astype(float),
    "albumin": pd.to_numeric(df["albumin"], errors="coerce"),
    "log_crp": np.log(pd.to_numeric(df["crp"], errors="coerce")),
    "hemoglobin": pd.to_numeric(df["hemoglobin"], errors="coerce"),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 60) / 10,
    "emergency": df["emergency"].eq("Y").astype(float),
})
data = data.replace([np.inf, -np.inf], np.nan).dropna(subset=["log_crp", "hemoglobin", "age_c"]).reset_index(drop=True)
data["missing"] = data["albumin"].isna().astype(float)
checks["kept_rows"] = int(len(data))
lost = int(data["missing"].sum())
events = int(data["complication"].sum())
support = int(min(events, len(data) - events))
who = smf.glm("missing ~ complication + emergency + age_c", data=data, family=sm.families.Binomial()).fit()
put("missing_after_complication", who.params["complication"], who.bse["complication"], who.pvalues["complication"],
    int(min(lost, len(data) - lost)), primary=True)
formula = "complication ~ albumin + log_crp + hemoglobin + age_c + emergency"
complete = smf.glm(formula, data=data.dropna(), family=sm.families.Binomial()).fit()
for term in ("albumin", "log_crp"):
    put(f"complete_case_{term}", complete.params[term], complete.bse[term], complete.pvalues[term], support)
imputed_data = mice.MICEData(data[["complication", "albumin", "log_crp", "hemoglobin", "age_c", "emergency"]])
pooled = mice.MICE(formula, sm.GLM, imputed_data, init_kwds={"family": sm.families.Binomial()}).fit(
    n_burnin=5, n_imputations=10)
names = list(pooled.model.exog_names)
for term in ("albumin", "log_crp", "age_c"):
    at = names.index(term)
    put(f"imputed_{term}", pooled.params[at], pooled.bse[at], pooled.pvalues[at], support)
put("missing_share", lost / len(data), support=int(min(lost, len(data) - lost)), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

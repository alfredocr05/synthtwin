"""A mixed logistic model: hospitalisation on pressure and arm with a random intercept a patient, fitted by variational Bayes (family F28, visits.csv)."""
import json
import math

import numpy as np
import pandas as pd
from scipy import sparse
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("visits.csv")
data = pd.DataFrame({
    "patient_id": df["patient_id"],
    "hospitalized": df["hospitalized"].eq("Y").astype(int),
    "sbp_c": (pd.to_numeric(df["sbp"], errors="coerce") - 138) / 10,
    "arm_a": df["arm"].eq("A").astype(int),
}).dropna()
# one column a patient, held sparse (a dense design would hold rows x patients numbers)
codes, patients = pd.factorize(data["patient_id"])
exog_vc = sparse.csr_matrix((np.ones(len(data)), (np.arange(len(data)), codes)), shape=(len(data), len(patients)))
exog = np.column_stack([np.ones(len(data)), data["sbp_c"].to_numpy(), data["arm_a"].to_numpy(dtype=float)])
names = ["Intercept", "sbp_c", "arm_a"]
model = BinomialBayesMixedGLM(data["hospitalized"].to_numpy(dtype=float), exog, exog_vc, np.zeros(len(patients), dtype=int),
                              fep_names=names, vcp_names=["patient"])
fit = model.fit_vb(fit_method="L-BFGS-B")
people_with = data.groupby("patient_id")["hospitalized"].max()
support = int(min(people_with.sum(), len(people_with) - people_with.sum()))
for term, primary in (("sbp_c", True), ("arm_a", False)):
    at = names.index(term)
    mean, sd = float(fit.fe_mean[at]), float(fit.fe_sd[at])
    put(term, mean, sd, math.erfc(abs(mean / sd) / math.sqrt(2)), support, primary)
put("patient_sd", math.exp(float(fit.vcp_mean[0])), support=support, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

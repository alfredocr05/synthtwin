"""Effect modification: a treatment's effect on the outcome changing with age, in a logistic model and by age strata (family F19, methods.csv)."""
import json
import math

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.contingency_tables import StratifiedTable


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
data = pd.DataFrame({
    "outcome": df["outcome"].eq("Y").astype(int),
    "treated": df["treated"].eq("Y").astype(int),
    "age_c": (pd.to_numeric(df["age"], errors="coerce") - 62) / 10,
    "diabetes": df["diabetes"].eq("Y").astype(int),
    "mass_c": (pd.to_numeric(df["body_mass_index"], errors="coerce") - 28) / 5,
}).dropna()
checks["kept_rows"] = int(len(data))
fit = smf.glm("outcome ~ treated * age_c + diabetes + mass_c", data=data, family=sm.families.Binomial()).fit()


def cells(frame, column):
    table = pd.crosstab(frame[column], frame["outcome"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0)
    return int(table.to_numpy().min())


for term, primary, judged in (("treated:age_c", True, True), ("treated", True, True), ("age_c", False, False),
                              ("diabetes", False, False)):
    put(term, fit.params[term], fit.bse[term], fit.pvalues[term], cells(data, "treated" if "treated" in term else
                                                                         "diabetes"), primary, judged)
older = data["age_c"] >= 0
for name, part in (("younger", data[~older]), ("older", data[older])):
    table = pd.crosstab(part["treated"], part["outcome"]).reindex(index=[0, 1], columns=[0, 1], fill_value=0).to_numpy()
    log_odds = math.log(table[1, 1] * table[0, 0] / (table[1, 0] * table[0, 1]))
    put(f"treated_log_odds_{name}", log_odds, math.sqrt((1.0 / table).sum()), support=int(table.min()), judged=False)
strata = [pd.crosstab(part["treated"], part["outcome"]).reindex(index=[1, 0], columns=[1, 0], fill_value=0).to_numpy()
          for _key, part in data.groupby(pd.cut(data["age_c"], [-10, -1, 0, 1, 10]))]
pooled = StratifiedTable(strata)
low, high = pooled.oddsratio_pooled_confint()
put("mantel_haenszel_log_odds", math.log(pooled.oddsratio_pooled), (math.log(high) - math.log(low)) / (2 * 1.959964),
    pooled.test_null_odds().pvalue,
    int(np.min([table.min() for table in strata])))
put("breslow_day_p", pooled.test_equal_odds().statistic, p=pooled.test_equal_odds().pvalue,
    support=int(np.min([table.min() for table in strata])), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

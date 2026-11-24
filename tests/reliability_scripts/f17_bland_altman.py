"""Agreement of two methods measuring one quantity: Bland-Altman bias, limits of agreement, proportional bias, concordance (family F17, methods.csv)."""
import json
import math

import pandas as pd
import statsmodels.formula.api as smf


results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}

df = pd.read_csv("methods.csv")
data = pd.DataFrame({"arterial": pd.to_numeric(df["arterial_sbp"], errors="coerce"),
                     "cuff": pd.to_numeric(df["cuff_sbp"], errors="coerce")}).dropna()
checks["kept_pairs"] = int(len(data))
n = len(data)
difference = data["cuff"] - data["arterial"]
average = (data["cuff"] + data["arterial"]) / 2
bias, spread = difference.mean(), difference.std()
put("bias", bias, spread / math.sqrt(n), support=n, primary=True)
put("sd_of_differences", spread, spread / math.sqrt(2 * (n - 1)), support=n, primary=True)
limit_se = spread * math.sqrt(1 / n + 1.96 ** 2 / (2 * (n - 1)))
put("upper_limit_of_agreement", bias + 1.96 * spread, limit_se, support=n)
put("lower_limit_of_agreement", bias - 1.96 * spread, limit_se, support=n)
fit = smf.ols("difference ~ average", data=pd.DataFrame({"difference": difference, "average": average})).fit()
put("proportional_bias_slope", fit.params["average"], fit.bse["average"], fit.pvalues["average"], n)
covariance = ((data["cuff"] - data["cuff"].mean()) * (data["arterial"] - data["arterial"].mean())).mean()
ccc = 2 * covariance / (data["cuff"].var(ddof=0) + data["arterial"].var(ddof=0) + (data["cuff"].mean() - data["arterial"].mean()) ** 2)
put("concordance_correlation", ccc, support=n)
put("pearson_correlation", data["cuff"].corr(data["arterial"]), support=n, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

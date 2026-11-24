"""Time to the first hospitalisation after the first visit, the pressure a measurement that changes at each visit (family F15, visits.csv)."""
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

df = pd.read_csv("visits.csv")
df["visit_date"] = pd.to_datetime(df["visit_date"], format="%Y-%m-%d", errors="coerce")
checks["unparsed_visit_date"] = float(df["visit_date"].isna().mean())
df["sbp"] = pd.to_numeric(df["sbp"], errors="coerce")
df = df.dropna(subset=["visit_date", "sbp"]).sort_values(["patient_id", "visit_date"])
df["day"] = (df["visit_date"] - df.groupby("patient_id")["visit_date"].transform("min")).dt.days
df["hosp"] = df["hospitalized"].eq("Y").astype(int)
df["prev_day"] = df.groupby("patient_id")["day"].shift(1)
df["prev_sbp"] = df.groupby("patient_id")["sbp"].shift(1)
later = df[df["day"] > 0]
first = later[later["hosp"] == 1].groupby("patient_id")["day"].min().rename("event_day")
df = df.merge(first, left_on="patient_id", right_index=True, how="left")
spells = df[df["prev_day"].notna() & (df["day"] > df["prev_day"])
            & (df["event_day"].isna() | (df["day"] <= df["event_day"]))].copy()
spells["status"] = (spells["day"] == spells["event_day"]).astype(int)
spells["sbp_previous"] = (spells["prev_sbp"] - 138) / 10
spells["sbp_current"] = (spells["sbp"] - 138) / 10
spells["arm_b"] = spells["arm"].eq("B").astype(int)
checks["kept_spells"] = int(len(spells))
events = int(spells["status"].sum())
people = spells.groupby("patient_id")["arm_b"].first()
in_arms = int(min(spells.loc[spells["arm_b"] == 1, "status"].sum(), spells.loc[spells["arm_b"] == 0, "status"].sum()))
for pressure, primary in (("sbp_previous", True), ("sbp_current", False)):
    fit = smf.phreg(f"day ~ {pressure} + arm_b", data=spells, status=spells["status"].to_numpy(),
                    entry=spells["prev_day"].to_numpy(), ties="breslow").fit()
    names = list(fit.model.exog_names)
    for term, support in ((pressure, events), ("arm_b", in_arms)):
        place = names.index(term)
        label = term if term != "arm_b" else f"arm_b_with_{pressure}"
        put(label, fit.params[place], fit.bse[place], fit.pvalues[place], support,
            primary and term == pressure, term == pressure or pressure == "sbp_previous")
put("first_hospitalisations", events, support=events, judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

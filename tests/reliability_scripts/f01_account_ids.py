"""Accounts and the other people they name: who subscribes, guarantors shared by several accounts, balances (family F1, accounts.csv)."""
import json
import math

import pandas as pd

results = {}
context = {}
checks = {}


def put(name, estimate, se=None, p=None, support=None, primary=False, judged=True):
    (results if judged else context)[name] = {
        "estimate": float(estimate), "se": None if se is None else float(se), "p": None if p is None else float(p),
        "support": None if support is None else int(support), "primary": primary}


df = pd.read_csv("accounts.csv")
people = df["patient_id"].nunique()
own = df["relationship"].eq("Self")
share = own.mean()
put("self_share", share, math.sqrt(share * (1 - share) / len(df)), support=int(min(own.sum(), len(df) - own.sum())))
same = df["subscriber_id"].astype("string").eq(df["patient_id"].astype("string")).fillna(False)
put("self_subscriber_is_the_patient", same[own].mean(), support=people, primary=True)
put("other_subscriber_is_the_patient", same[~own].mean(), support=people)
per_guarantor = df.groupby("guarantor_id").size()
put("guarantors_with_several_accounts", (per_guarantor >= 2).mean(), support=len(per_guarantor), judged=False)
accounts = df.groupby("patient_id").size()
put("accounts_per_patient", accounts.mean(), accounts.std() / math.sqrt(len(accounts)), support=len(accounts),
    judged=False)
balance = pd.to_numeric(df["balance"], errors="coerce")
negative = (balance < 0).mean()
put("negative_balance_share", negative, math.sqrt(negative * (1 - negative) / len(df)),
    support=int((balance < 0).sum()), judged=False)

with open("results.json", "w", encoding="utf-8") as handle:
    json.dump({"estimands": results, "context": context, "checks": checks}, handle)

"""R-P4-61: do the two modules' windows ever disagree about a VERDICT?

They print numbers differing in the last places. The question that
matters is whether a twin the generator calls inside its range is ever
one the validator calls MISSED, or the other way round.
"""
import sys, pathlib, tempfile, random
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures
from synthtwin import (contract, generation, profile, reading, rendering,
                       taxonomy, validation)

random.seed(20260830)
built = compared = differ = verdict_differ = 0
examples = []
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    for index in range(160):
        n = random.choice([20, 60, 120, 240])
        kind = random.choice(["normal", "skewed", "grid", "counts", "wide", "bimodal"])
        if kind == "normal":
            rows = [repr(round(random.gauss(50, 12), 3)) for _ in range(n)]
        elif kind == "skewed":
            rows = [repr(round(random.expovariate(0.05), 2)) for _ in range(n)]
        elif kind == "grid":
            rows = [("%.1f" % (250 + (j % 40) * 1.1)) for j in range(n)]
        elif kind == "counts":
            rows = [str(random.randint(0, 40)) for _ in range(n)]
        elif kind == "bimodal":
            rows = [repr(round(random.gauss(random.choice([10, 90]), 4), 2)) for _ in range(n)]
        else:
            rows = [repr(random.uniform(1, 9) * 10 ** random.randint(0, 9)) for _ in range(n)]
        try:
            fixtures.write(home, f"c{index}.csv", "value\n" + "\n".join(rows) + "\n")
            table = reading.read_table(str(home / f"c{index}.csv"),
                                       first_row=reading.FIRST_ROW_AUTOMATIC)
            doc = profile.build_document(table, taxonomy.Settings(), [])
            loaded = contract.load_profile(
                str(fixtures.write_profile(home, f"c{index}-p.json", doc)))
        except Exception:
            continue
        built += 1
        col = loaded.columns[0]
        if not isinstance(col.facts, contract.NumericFacts):
            continue
        for seed in (3, 11):
            twin = generation.generate(loaded, seed)
            made = {a.fact: a for a in twin.approximations}
            out = validation.measure(
                loaded, str(fixtures.write(home, f"c{index}-{seed}.csv",
                                           rendering.twin_csv(twin))))
            seen = {c.fact.split(".")[-1]: c for c in out.checks
                    if c.fact.split(".")[-1] in ("mean", "std", "skew", "kurtosis")}
            for fact in ("mean", "std", "skew", "kurtosis"):
                if fact not in made or fact not in seen:
                    continue
                compared += 1
                g_inside = made[fact].inside
                v_ok = seen[fact].verdict in ("HELD", "WITHIN-BOUND",
                                              "AUTHORIZED-DEVIATION")
                if (made[fact].lowest, made[fact].highest) != (
                        seen[fact].published, seen[fact].achieved):
                    differ += 1
                if g_inside != v_ok:
                    verdict_differ += 1
                    if len(examples) < 6:
                        examples.append((index, seed, fact, g_inside,
                                         seen[fact].verdict))
print("columns built:", built)
print("facts compared across both modules:", compared)
print("  where the GENERATOR says inside and the VALIDATOR does not, or vice versa:",
      verdict_differ)
for e in examples:
    print("    column %d seed %d %s: generator inside=%s validator=%s" % e)

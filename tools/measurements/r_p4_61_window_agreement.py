"""R-P4-61: do the two reports print one window, and one verdict?

The twin's own report (the generator) and the quality report (the
validator) each print the window method G12.2 and G12.3 allow every
interior rung and every moment. This measures, for the same twin, both
things the residual asked:

- how many windows the quality report prints whose two ends differ, as
  PRINTED, from the twin report's window for the same fact; and
- how many facts one report calls inside while the other calls MISSED.

It compares what each report prints -- `Approximation.lowest` and
`.highest` against the `(between L and H)` of the quality check -- so it
runs unchanged on any commit that has both reports. The first writing
of this tool compared the generator's ends with the validator's
`(published, achieved)`, which are not a window, never printed its own
difference count, and built columns of 20 to 240 rows, where the widest
stratum could not tell the two modules apart. It builds 500 to 4,000.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import math
import pathlib
import random
import re
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures  # noqa: E402
from synthtwin import (  # noqa: E402
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

FACTS = ("p01", "p05", "p10", "p25", "p50", "p75", "p90", "p95", "p99",
         "mean", "std", "skew", "kurtosis")


def shapes(draw, rows):
    return {
        "weight": [f"{draw.gauss(80, 16):.1f}" for _ in range(rows)],
        "uniform": [f"{draw.random():.3f}" for _ in range(rows)],
        "income": [str(int(round(draw.lognormvariate(10.8, 0.7), -2)))
                   for _ in range(rows)],
        "creatinine": ["%.2f" % math.exp(draw.gauss(0, 0.35))
                       for _ in range(rows)],
        "body_mass": [f"{draw.gauss(27, 4):.1f}" for _ in range(rows)],
        "kilograms": [f"{draw.gauss(80, 16):.1f} kg" for _ in range(rows)],
        "percent": [f"{draw.gauss(55, 12):.1f}%" for _ in range(rows)],
        "age": [str(max(18, min(95, int(draw.gauss(55, 15)))))
                for _ in range(rows)],
        "cost": ["%.2f" % draw.expovariate(1 / 5000) for _ in range(rows)],
        "bimodal": ["%.2f" % draw.gauss(draw.choice([10, 90]), 4)
                    for _ in range(rows)],
        "change": [f"{draw.gauss(0, 5):.1f}" for _ in range(rows)],
        "charges": ["%.2f" % (1000 * draw.paretovariate(1.5))
                    for _ in range(rows)],
        "stripped": [("%.1f" % value).rstrip("0").rstrip(".")
                     for value in [draw.gauss(80, 16) for _ in range(rows)]],
        "mostly_zero": [("0" if draw.random() < 0.6
                         else "%.1f" % draw.expovariate(0.01))
                        for _ in range(rows)],
        "with_a_label": [("NOT DETECTED" if draw.random() < 0.15
                          else "%.2f" % draw.lognormvariate(0, 0.5))
                         for _ in range(rows)],
    }


def generator_windows(twin):
    found = {}
    for one in twin.approximations:
        last = one.fact.split(".")[-1]
        if last in FACTS:
            found[last] = (one.lowest, one.highest, one.inside)
    return found


def validator_windows(outcome):
    found = {}
    for check in outcome.checks:
        head = check.subcheck.split(" ")[-1]
        if head.split(".")[0] not in ("ladder", "moments"):
            continue
        last = head.split(".")[-1]
        if last not in FACTS:
            continue
        window = re.search(r"\(between (\S+) and (\S+)\)$", check.published)
        ends = (window.group(1), window.group(2)) if window else None
        found[last] = (ends, check.verdict)
    return found


def main():
    rows_list = [500, 2000, 4000]
    seeds = (3, 11)
    columns = compared = differ = verdicts = flips = 0
    examples = []
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for rows in rows_list:
            for kind, cells in shapes(random.Random(rows), rows).items():
                path = fixtures.write(home, f"{kind}{rows}.csv",
                                      "value\n" + "\n".join(cells) + "\n")
                document = profile.build_document(
                    reading.read_table(str(path)), taxonomy.Settings(), [])
                loaded = contract.load_profile(str(fixtures.write_profile(
                    home, f"{kind}{rows}-profile.json", document)))
                facts = loaded.columns[0].facts
                if isinstance(facts, (contract.TextFacts,
                                      contract.LabelFacts)):
                    continue
                columns += 1
                for seed in seeds:
                    twin = generation.generate(loaded, seed)
                    written = fixtures.write(home, f"{kind}{rows}-{seed}.csv",
                                             rendering.twin_csv(twin))
                    outcome = validation.measure(loaded, str(written))
                    mine = generator_windows(twin)
                    theirs = validator_windows(outcome)
                    for fact, (ends, verdict) in theirs.items():
                        if fact not in mine:
                            continue
                        low, high, inside = mine[fact]
                        verdicts += 1
                        if inside != (verdict != validation.MISSED):
                            flips += 1
                            if len(examples) < 8:
                                examples.append(("verdict", kind, rows, seed,
                                                 fact, inside, verdict))
                        if ends is None:
                            continue
                        compared += 1
                        if (low, high) != ends:
                            differ += 1
                            if len(examples) < 8:
                                examples.append(("window", kind, rows, seed,
                                                 fact, (low, high), ends))
    print("columns built:", columns)
    print("windows printed by both reports:", compared)
    print("  whose printed ends differ:", differ)
    print("rung and moment verdicts compared:", verdicts)
    print("  where one report says inside and the other MISSED:", flips)
    for example in examples:
        print("   ", example)


if __name__ == "__main__":
    main()

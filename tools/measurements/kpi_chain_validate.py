"""K-S6-04, K-S6-05 and K-S6-10: validator V12 for the chain's families, layer L1 (lane CHv, plan P4-D430).

Every run goes through the product's own commands with the chain's switch
handed in (`cli.main(..., chain=...)`, which no command-line option sets):
`synthtwin profile` writes a switched description of an invented table
under the oracle's fixed test key, `synthtwin validate` checks a file of
rows against it with V12's lines, and `synthtwin generate` makes today's
twin from the same table described without the switch. The chain's twin
is today's twin's own cells, column by column, arranged into rows by the
oracle's walk (method G16.2, `tools/reference/chain_oracle.py`) from the
published chain: the arrangement lane CHb builds into the generator, read
here from the oracle until it lands (`tests/chain_twins.py`).

- K-S6-04: on the clinic table (`tests/chain_twins.py`) at 800 and 20,000
  rows, every candidate pair one structural word with no published reason
  beside it (`pairs_without_one_word`, `pairs_with_a_reason`), every
  published family one line of the written report
  (`families_without_one_line`), every line HELD on the table itself
  (`lines_not_held_on_the_table`), and V12.4's six data mutants as the
  method states them (`mutants_as_expected` of `mutants`, at 800 rows).
- K-S6-05: whole real rows in the twin, over K-S6-01's table (1,000 rows
  of age, sbp, group and died; `tests/kpi_shapes.association_table`) and
  twin seeds 0 to 19: today's twin and the chain's twin, each row counted
  where it equals a real row in every column; the mean and the largest.
- K-S6-10: the blur, on the same table and seeds: the death-rate
  difference between rows of age 70 and above and the rest (a cut no
  description publishes), the chain's twin against the real table, its
  median and largest gap over the twenty seeds, today's twin's beside it.

    PYTHONPATH=src:tests python tools/measurements/kpi_chain_validate.py --kpi

About one to three minutes on the reference machine; one process of a few
hundred megabytes.
"""

import csv
import io
import json
import os
import pathlib
import random
import statistics
import sys
import tempfile
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402

kpi_rules.guard_this_tree()
import chain_twins as twins  # noqa: E402
import kpi_shapes  # noqa: E402
from synthtwin import cli  # noqa: E402

SIZES = (800, 20000)
SEEDS = range(20)
CUT = 70


def _structure(described):
    """The pair and family counts K-S6-04 reads, on the switched table checked against itself."""
    code, report, _screen = described.validate(described.rows)
    statistical = described.statistical
    eligible = [entry["column"] for entry in statistical["ladder"]]
    candidates = [(a, b) for at, a in enumerate(eligible) for b in eligible[at + 1 :]]
    seen = {}
    reasons = 0
    for entry in statistical["words"]:
        pair = tuple(entry["columns"])
        seen[pair] = seen.get(pair, 0) + 1
        if sorted(entry) != ["columns", "word"] or entry["word"] not in ("exact", "implied", "pinned"):
            reasons += 1
    without = sum(1 for pair in candidates if seen.get(pair, 0) != 1) + sum(1 for pair in seen if pair not in candidates)
    section = twins._section(report)
    lines = [line for line in section.split("\n") if line.startswith("  family ")]
    families = len(statistical["chain"])
    one_line = sum(1 for at in range(families) if sum(1 for line in lines if line.startswith(f"  family {at}: ")) == 1)
    totals, verdicts = twins._verdicts(report)
    not_held = sum(1 for v in totals.values() if v != "HELD") + sum(1 for v in verdicts.values() if v != "HELD")
    return {
        "candidate_pairs": len(candidates),
        "pairs_without_one_word": without,
        "pairs_with_a_reason": reasons,
        "families": families,
        "families_without_one_line": families - one_line,
        "lines_not_held_on_the_table": not_held + (1 if code != 0 else 0),
    }


def _shuffled(rows, place, seed):
    order = list(range(len(rows)))
    random.Random(seed).shuffle(order)
    out = [list(row) for row in rows]
    for at in range(len(out)):
        out[at][place] = rows[order[at]][place]
    return out


def _mutants(described, empty):
    """V12.4's six data mutants, each judged as the method states its outcome."""
    results = {}
    families = twins._families(described)
    # 1: a child's cells exchanged between two rows in different parent cells and different bands.
    at, family = twins._family_with_parents(described)
    codes = twins._band_codes(described, described.rows)

    def cell_of(row):
        return tuple(codes[p["column"]][0].coarsen(int(p["level"][1]))[codes[p["column"]][1][row]] for p in family["parents"])

    lad, row_l0 = codes[family["child"]]
    to_level = lad.coarsen(int(family["level"][1]))
    second = next(r for r in range(1, len(described.rows)) if cell_of(r) != cell_of(0) and to_level[row_l0[r]] != to_level[row_l0[0]])
    place = described.header.index(family["child"])
    rows = [list(row) for row in described.rows]
    rows[0][place], rows[second][place] = rows[second][place], rows[0][place]
    code, report, _screen = described.validate(rows)
    totals, verdicts = twins._verdicts(report)
    results["1"] = verdicts[at] == "MISSED" and set(totals.values()) == {"HELD"} and code == 3
    # 2: one column shuffled alone.
    column = "pressure"
    code, report, _screen = described.validate(_shuffled(described.rows, described.header.index(column), 11))
    totals, verdicts = twins._verdicts(report)
    holding = twins._holding(described, column)
    expected = {i: ("MISSED" if i in holding and not (f["child"] == column and not f["parents"]) else "HELD") for i, f in enumerate(families)}
    results["2"] = verdicts == expected and code == 3
    # 3: the records holding nothing placed by single-cell exchanges, each column paired its own way.
    grid = []
    for at_row in range(len(empty.rows)):
        if at_row in empty.empty_at:
            grid += [[""] * len(empty.header)]
        grid += [list(empty.rows[at_row])]
    blank_rows = [b + sorted(empty.empty_at).index(b) for b in sorted(empty.empty_at)]
    chosen_rows = [c + len(empty.empty_at) for c in range(400, 400 + len(blank_rows))]
    for place_at in range(len(empty.header)):
        for k in range(len(chosen_rows)):
            target = blank_rows[(k + place_at) % len(blank_rows)]
            grid[target][place_at], grid[chosen_rows[k]][place_at] = grid[chosen_rows[k]][place_at], grid[target][place_at]
    code, report, _screen = empty.validate(grid)
    totals, verdicts = twins._verdicts(report)
    results["3"] = "MISSED" in verdicts.values() and set(totals.values()) == {"HELD"} and code == 3
    # 4: whole rows shuffled together.
    order = list(range(len(described.rows)))
    random.Random(5).shuffle(order)
    code, report, _screen = described.validate([described.rows[i] for i in order])
    code_before, before, _screen = described.validate(described.rows)
    results["4"] = code == code_before == 0 and twins._section(report) == twins._section(before)
    # 5: a twin dealt from a chain that dropped a parent.
    at, _dropped, chain = twins._dropped_parent(described)
    code, report, _screen = described.validate(twins._walk_twin(described, chain, salt="drop"))
    totals, verdicts = twins._verdicts(report)
    results["5"] = verdicts[at] == "MISSED" and set(totals.values()) == {"HELD"} and code == 3
    # 6: band totals off by 3 and by 30: the same words, no number.
    sections = []
    good = True
    for moved in (3, 30):
        code, report, _screen = described.validate(twins._off_by(described, moved))
        totals, verdicts = twins._verdicts(report)
        good = good and totals["pressure"] == "MISSED" and code == 3
        good = good and all(verdicts[i] == ("WITHHELD" if i in twins._holding(described, "pressure") else "HELD") for i in range(len(families)))
        sections += [twins._section(report)]
    results["6"] = good and sections[0] == sections[1]
    return results


def _read_rows(path):
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return rows[0], rows[1:]


def _gap(header, rows):
    """The death rate at age 70 and above less the rate below it."""
    age = header.index("age")
    died = header.index("died")
    old = [row for row in rows if row[age] != "" and float(row[age]) >= CUT]
    young = [row for row in rows if row[age] != "" and float(row[age]) < CUT]
    rate = lambda group: sum(1 for row in group if row[died] == "yes") / len(group)  # noqa: E731
    return rate(old) - rate(young)


def _association(folder):
    """K-S6-05 and K-S6-10 over K-S6-01's table and twenty twin seeds."""
    text = kpi_shapes.association_table()
    reader = list(csv.reader(io.StringIO(text)))
    header, rows = reader[0], reader[1:]
    (folder / "switched").mkdir()
    switched = twins.Described(folder / "switched", header, rows)
    plain = folder / "plain"
    plain.mkdir()
    table = twins._write(plain / "association.csv", header, rows)
    code, said = twins._quiet(lambda: cli.main(["profile", str(table), "--out-dir", str(plain)]))
    if code != 0:
        raise SystemExit(f"profile failed: {said}")
    real = {tuple(row) for row in rows}
    real_gap = _gap(header, rows)
    product_whole = []
    chain_whole = []
    chain_blur = []
    product_blur = []
    for seed in SEEDS:
        out = plain / f"seed{seed}"
        out.mkdir()
        code, said = twins._quiet(lambda: cli.main(["generate", str(plain / "association-profile.json"), "--seed", str(seed), "--out-dir", str(out)]))
        if code != 0:
            raise SystemExit(f"generate failed: {said}")
        twin_header, twin_rows = _read_rows(out / "association-twin.csv")
        assert twin_header == header
        arranged = twins._walk_twin(switched, salt=f"seed{seed}", cells_from=twin_rows)
        product_whole += [sum(1 for row in twin_rows if tuple(row) in real)]
        chain_whole += [sum(1 for row in arranged if tuple(row) in real)]
        product_blur += [abs(_gap(header, twin_rows) - real_gap)]
        chain_blur += [abs(_gap(header, arranged) - real_gap)]
    chain = switched.statistical["chain"]
    age_level = next(f["level"] for f in chain if f["child"] == "age")
    return (
        {
            "rows": len(rows),
            "seeds": len(SEEDS),
            "product_whole_rows_mean": round(statistics.mean(product_whole), 2),
            "product_whole_rows_max": max(product_whole),
            "chain_whole_rows_mean": round(statistics.mean(chain_whole), 2),
            "chain_whole_rows_max": max(chain_whole),
        },
        {
            "seeds": len(SEEDS),
            "cut": CUT,
            "real_rate_difference": round(real_gap, 4),
            "chain_gap_median": round(statistics.median(chain_blur), 4),
            "chain_gap_largest": round(max(chain_blur), 4),
            "product_gap_median": round(statistics.median(product_blur), 4),
            "age_chain_level": age_level,
        },
    )


class _Empty(twins.Described):
    def __init__(self, folder, header, rows, empty_at):
        self.empty_at = set(empty_at)
        super().__init__(folder, header, rows, self.empty_at)


def measure():
    started = time.time()
    with tempfile.TemporaryDirectory(prefix="kpi-chain-validate-") as held:
        folder = pathlib.Path(held)
        for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
            os.environ[name] = str(folder / "home")
        structure = {}
        clinic = None
        for size in SIZES:
            place = folder / f"clinic{size}"
            place.mkdir()
            described = twins.Described(place, twins.HEADER, twins._clinic_rows(size))
            found = _structure(described)
            for key, value in found.items():
                structure[key] = structure.get(key, 0) + value
            if size == SIZES[0]:
                clinic = described
        empty_place = folder / "empty"
        empty_place.mkdir()
        empty = _Empty(empty_place, twins.HEADER, twins._clinic_rows(), range(100, 112))
        mutants = _mutants(clinic, empty)
        assoc_place = folder / "association"
        assoc_place.mkdir()
        whole, blur = _association(assoc_place)
    k_s6_04 = dict(structure)
    k_s6_04["sizes"] = len(SIZES)
    k_s6_04["mutants"] = len(mutants)
    k_s6_04["mutants_as_expected"] = sum(1 for good in mutants.values() if good)
    missed = ",".join(name for name, good in sorted(mutants.items()) if not good) or "none"
    seconds = round(time.time() - started, 1)
    return k_s6_04, whole, blur, seconds, missed


def main():
    k_s6_04, whole, blur, seconds, missed = measure()
    detail = f"lane CHv's V12 at layer L1 behind the switch; mutants not as stated: {missed}; {seconds} s for the three"
    records = (("K-S6-04", k_s6_04), ("K-S6-05", whole), ("K-S6-10", blur))
    for entry_id, value in records:
        if "--kpi" in sys.argv:
            print("KPI " + json.dumps({"id": entry_id, "value": value, "detail": detail}, sort_keys=True))
        else:
            print(entry_id, json.dumps(value, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())

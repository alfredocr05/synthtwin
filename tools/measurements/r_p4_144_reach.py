"""R-P4-144: which missed above-counts NO arrangement could have reached.

A joined column publishes, for each pair of positions, how many rows
hold the earlier value above the later one. The pairing walk tries to
reach those counts by swapping cells, and when a count is missed the
walk gets the blame. For a good share of them that blame is provably
wrong, which is what this driver measures.

The twin holds its own two multisets of numbers at those two
positions, drawn from each position's OWN published description. Over
every bijection of one onto the other there is a largest and a
smallest achievable count, and a published count outside that range is
one NO walk, no schedule and no acceptance rule can reach.

**THE BOUND IS PAIRWISE, AND THAT CUTS ONE WAY ONLY.** Outside the
range means impossible, whatever the rest of the column does: joint
constraints can only SHRINK what is feasible, and once the twin's two
multisets are fixed every joint arrangement projects to some bijection
of that pair. Inside the range does NOT mean the walk could have met
it, because a column's pairs must all hold under ONE arrangement.
Three positions each holding `[0, 1]` with every pair published at one
above-row is the standing counterexample: each pair alone is
reachable, two of the three positions must share an orientation, and a
shared orientation gives that pair zero. So this driver reports what
is impossible pairwise and what is NOT ATTRIBUTED -- never what the
walk could have fixed. Review round 5 of L7 found this driver's own
wording claiming otherwise.

**THE BOUND IS CHECKED RATHER THAN ASSERTED.** `--self-check`
enumerates every permutation of small multisets and compares the
greedy bounds against the truth, and also asks whether the achievable
set has holes -- because a bound is only a verdict on reachability if
every count between the two ends is reachable too. Two earlier
versions of these two functions were WRONG in a way that reading them
did not reveal and that the enumeration caught at once.

Usage:

    .venv/bin/python tools/measurements/r_p4_144_reach.py --self-check
    .venv/bin/python tools/measurements/r_p4_144_reach.py --seeds 8

No network, no program started, no import of anything but the standard
library and the package under measurement.
"""
import argparse
import collections
import itertools
import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "tools" / "measurements"))


def most_above(one: "list[float]", two: "list[float]") -> int:
    """The largest count of `a > b` over any bijection of the two.

    Both sorted, then the smallest `a` that beats each `b` in turn:
    spending the cheapest winner on the cheapest opponent leaves the
    dearer ones for the harder opponents, and a winner spent anywhere
    else can be exchanged back without losing a win.
    """
    one, two = sorted(one), sorted(two)
    index = got = 0
    for value in two:
        while index < len(one) and one[index] <= value:
            index = index + 1
        if index < len(one):
            got = got + 1
            index = index + 1
    return got


def fewest_above(one: "list[float]", two: "list[float]") -> int:
    """The smallest count of `a > b`, by maximising `a <= b` instead."""
    one, two = sorted(one), sorted(two)
    index = safe = 0
    for value in two:
        if index < len(one) and one[index] <= value:
            safe = safe + 1
            index = index + 1
    return len(one) - safe


def self_check(trials: int) -> int:
    """Every permutation of small multisets against the two bounds."""
    generator = random.Random(11)
    wrong = holes = 0
    for _trial in range(trials):
        count = generator.randint(2, 7)
        top = generator.choice((2, 3, 5, 12))
        one = [generator.randint(0, top) for _each in range(count)]
        two = [generator.randint(0, top) for _each in range(count)]
        seen = {
            sum(1 for a, b in zip(one, order) if a > b)
            for order in itertools.permutations(two)
        }
        if min(seen) != fewest_above(one, two):
            wrong = wrong + 1
        elif max(seen) != most_above(one, two):
            wrong = wrong + 1
        if seen != set(range(min(seen), max(seen) + 1)):
            holes = holes + 1
    print(f"  {trials} multiset pairs, up to seven rows, every "
          f"permutation enumerated")
    print(f"    the two bounds disagreed with the truth: {wrong}")
    print(f"    the achievable set had a hole in it: {holes}")
    print("  A hole would mean a count inside the range that no "
          "arrangement of THAT PAIR reaches, which would move a miss "
          "from the unattributed column to the impossible one.")
    return wrong + holes


def measure(seeds: int) -> None:
    import a_p4_52_l7_parity as parity
    sys.path.insert(0, str(ROOT / "src"))
    from synthtwin import contract, generation, profile, reading, taxonomy
    import fixtures

    verdict: "collections.Counter" = collections.Counter()
    outside_by: "collections.Counter" = collections.Counter()
    short_by: "collections.Counter" = collections.Counter()
    where: "collections.Counter" = collections.Counter()
    pairs = 0
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for stem, _parts, rows in parity.spread():
            fixtures.write(
                home, f"{stem}.csv", "reading\n" + "\n".join(rows) + "\n"
            )
            table = reading.read_table(
                str(home / f"{stem}.csv"),
                first_row=reading.FIRST_ROW_AUTOMATIC,
            )
            document = profile.build_document(
                table, taxonomy.Settings(), [], None, ["reading"]
            )
            loaded = contract.load_profile(str(fixtures.write_profile(
                home, f"{stem}.json", document
            )))
            facts = loaded.columns[0].facts
            firsts, seconds = generation._pair_seats(facts.n_parts)
            for seed in range(seeds):
                twin = generation.generate(loaded, seed)
                cells = [one for one in twin.columns[0] if one != ""]
                held = [
                    [float(one.split(facts.separator)[place]) for one in cells]
                    for place in range(facts.n_parts)
                ]
                for seat in range(len(facts.part_above)):
                    one, two = held[firsts[seat]], held[seconds[seat]]
                    pairs = pairs + 1
                    got = sum(
                        1 for row in range(len(cells)) if one[row] > two[row]
                    )
                    wanted = facts.part_above[seat]
                    if got == wanted:
                        continue
                    low, high = fewest_above(one, two), most_above(one, two)
                    near = min(wanted, len(cells) - wanted) / len(cells)
                    where[
                        "published at an end (under a twentieth)"
                        if near < 0.05 else
                        "published near an end (under a fifth)"
                        if near < 0.20 else
                        "published in the middle"
                    ] += 1
                    if wanted < low or wanted > high:
                        verdict["no arrangement of the twin's own values "
                                "reaches it"] += 1
                        outside_by[min(
                            abs(wanted - low), abs(wanted - high)
                        )] += 1
                    else:
                        verdict["pairwise reachable; joint "
                                "feasibility unmeasured"] += 1
                        short_by[abs(got - wanted)] += 1
    missed = sum(verdict.values())
    print(f"  twelve columns drawn apart, {seeds} seeds, {pairs} pairs")
    print(f"    above-counts missed: {missed}")
    for name in sorted(verdict):
        print(f"      {name}: {verdict[name]}")
    print(f"    how far outside the achievable range: "
          f"{dict(sorted(outside_by.items()))}")
    print(f"    how far the twin stopped from these: "
          f"{dict(sorted(short_by.items()))}")
    print(f"    where the published count sits: {dict(where)}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="r_p4_144_reach",
        description="which missed above-counts were impossible for "
                    "their pair alone",
    )
    parser.add_argument("--seeds", type=int, default=8)
    parser.add_argument("--trials", type=int, default=4000)
    parser.add_argument("--self-check", action="store_true")
    known = parser.parse_args()
    print("\n===== is the bound right? =====")
    if self_check(known.trials):
        raise SystemExit(
            "the bound disagreed with an enumeration; the split below "
            "would not mean what it says"
        )
    if known.self_check:
        return
    print("\n===== what the misses are =====")
    measure(known.seeds)


if __name__ == "__main__":
    main()

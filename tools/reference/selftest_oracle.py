"""The self-test's oracle, and the writer of its frozen vectors (lane ST, plan P4-D458).

This script NEVER imports synthtwin, numpy, pandas or a solver. It reads
contract 4.6b.8 as plan P4-D458 amends it, and method G16.8, from the
pages alone, in Python integers and binary64 arithmetic written out:

- THE WORDS: SplitMix64 (Steele, Lea and Flood 2014), each sampled row's
  stream seeded by the constant `0x53594E5448545354` XOR the first 8 bytes
  of the row's content hash read big-endian, plus its place among the
  sample's rows of the same hash times the golden gamma
  `0x9E3779B97F4A7C15`, modulo `2**64`; the `k`-th word (from 0) is the
  mix of `seed + (k + 1) * gamma`;
- THE SPLITS: word 0's low four bits are the row's group of sixteen, and
  split `j`'s half is bit `j` of it;
- THE WALK'S WORDS: family `f` reads words `1 + 3 f`, `2 + 3 f` and
  `3 + 3 f`, whose twelve 16-bit pieces sum to the row's hidden sum `S`
  (G16.8);
- THE SHUFFLE: column `c` of a chain of `F` families orders the sample's
  rows by word `1 + 3 F + c`, ties by row;
- THE YARDSTICK: `h` the root mean square over the four splits of half 0's
  value less half 1's, scaled to the whole table `h * sqrt(n_s / n)`;
  RULE W2: a pair is judged only where `n` times its scaled yardstick
  reaches the floor;
- THE WORDS JUDGED: a family reads `carried` where its share of estimates
  inside the scaled yardstick stands at most 25 points under the
  replicate's AND, over the estimates the shuffle moves beyond their
  yardstick (where five or more), the median of the twin's gap over the
  shuffle's is at most the median of the replicate's (one half against
  the other) over the shuffle's; inside but keeping less, `approximate`;
  otherwise `not carried` where the median of the twin's gap over the
  shuffle's is at least one half, else `approximate`; fewer than five
  supported estimates read `not judged`. The shares are read on the
  JOINT estimates (the sample value more than `h` from its value were the
  columns unrelated), on all of them where fewer than five are joint
  (amended 2026-11-05).
- THE TRIAL KEYS (amended 2026-11-05): a word is the worst of the keys'
  words, from carried through approximate to not carried, and `not
  judged` where any key reads `not judged`.
- A PAIR'S WORD (amended 2026-11-05): its table read at the first level,
  `L0` then `L1` then `L2`, at which every cell holding rows holds 22 on
  the sample and 11 in each of the eight halves (`not judged` where none
  does); one estimate's word is `carried` inside its scaled yardstick,
  `not carried` where its gap is at least half the shuffle's (the shuffle
  beyond its yardstick), `approximate` otherwise; a pair holding a fine
  column reads the worst of its table's word and its correlations' (the
  code scale's held at best `approximate` where a column of the pair is
  skewed), `not judged` where any of them is.
- THE TABLE WITHOUT RELATIONSHIPS (amended 2026-11-05, and again the
  same day: the share alone): a family between columns whose share of
  joint estimates is under twice 0.116 (P(|t_4| > 2)) is not judged; a
  correlation reads `not carried` only where it is joint (a table's
  distance where the shuffle moves it beyond its yardstick).
- A COMPARISON SKIPPED IS NO AFFIRMATION (amended 2026-11-05): a family
  inside the yardstick about as often as the replicate, with fewer than
  five estimates the shuffle moves beyond their yardstick, is not judged;
  EVERY COMPARISON PAST THE LINE (amended 2026-11-06): it reads `not
  carried` instead where each of those estimates reads `not carried` on its
  own (outside its scaled yardstick, its sample value more than `h` from
  its null, its gap at least half the shuffle's).
- F1'S LABEL LEVELS (amended 2026-11-05): a label's levels read as
  outcomes are its codes holding 22 rows or more, its empty band aside,
  the ten largest, ties by code.

Each case stands beside the outcome of its mutant. The vectors are a pure
function of the numbers written here; the seed argument is accepted and
ignored, as the provenance guard's convention asks.

Usage:  python3 selftest_oracle.py --seed 0 --out <path>
"""

import argparse
import json
import math

CONSTANT = 0x53594E5448545354
GAMMA = 0x9E3779B97F4A7C15
MASK = (1 << 64) - 1


def mix(z):
    """SplitMix64's finalizer on one state."""
    z &= MASK
    z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & MASK
    return z ^ (z >> 31)


def stream(seed, count):
    """The first `count` words of SplitMix64 seeded with `seed`, by advancing its state."""
    state = seed
    out = []
    for _k in range(count):
        state = (state + GAMMA) & MASK
        out.append(mix(state))
    return out


def seeds_of(hashes):
    """Each sampled row's seed, from the first 8 bytes of its content hash and its place among equal rows."""
    places = {}
    out = []
    for value in hashes:
        place = places.get(value, 0)
        places[value] = place + 1
        out.append(((CONSTANT ^ value) + place * GAMMA) & MASK)
    return out


def hidden_sum(words):
    """G16.8's `S`: the twelve 16-bit pieces of three words, added."""
    total = 0
    for value in words:
        for shift in (0, 16, 32, 48):
            total += (value >> shift) & 0xFFFF
    return total


def yardstick(halves, sample, rows):
    """The half-split yardstick, the replicate's (splits 1 to 3, times the square root of two), and the scaled one."""
    gaps = [halves[2 * j] - halves[2 * j + 1] for j in range(4)]
    whole = math.sqrt(sum(gap * gap for gap in gaps) / 4.0)
    rest = math.sqrt(sum(gap * gap for gap in gaps[1:]) / 3.0)
    return whole, math.sqrt(2.0) * rest, whole * math.sqrt(sample / rows)


def median_of(values):
    ordered = sorted(values)
    middle = len(ordered) // 2
    return ordered[middle] if len(ordered) % 2 else 0.5 * (ordered[middle - 1] + ordered[middle])


def judged(estimates, sample, rows, scaled=True, kept_rule=True, joint_rule=True, few_rule=True, past_rule=True,
           all_rule=True, own_word_rule=True):
    """A family's word from its estimates `(sample, twin, shuffle, null, halves)`."""
    if len(estimates) < 5:
        return "not judged"
    joint = [one for one in estimates if abs(one[0] - one[3]) > yardstick(one[4], sample, rows)[0]]
    basis = joint if joint_rule and len(joint) >= 5 else estimates
    inside = 0
    replicate = 0
    for value, twin, _shuffle, _null, halves in basis:
        whole, rest, small = yardstick(halves, sample, rows)
        bound = small if scaled else whole
        inside += 1 if abs(twin - value) <= bound else 0
        replicate += 1 if abs(halves[0] - halves[1]) <= rest else 0
    ratios = []
    kept = []
    past = []
    for value, twin, shuffle, null, halves in estimates:
        whole, _rest, _small = yardstick(halves, sample, rows)
        gap = abs(shuffle - value)
        if gap > whole and gap > 0.0:
            ratios.append(abs(twin - value) / gap)
            kept.append(abs(halves[0] - halves[1]) / gap)
            if own_word_rule:
                past.append(one_word(value, twin, shuffle, halves, sample, rows, null=null) == "not carried")
            else:
                past.append(abs(twin - value) / gap >= 0.5)
    near = inside / len(basis) >= replicate / len(basis) - 0.25
    if near and len(ratios) < 5 and few_rule:
        if past_rule and past and (all(past) or not all_rule):
            return "not carried"
        return "not judged"
    keeps = (len(ratios) >= 5 and median_of(ratios) <= median_of(kept)) or not kept_rule or (len(ratios) < 5 and not few_rule)
    if near and keeps:
        return "carried"
    if near:
        return "approximate"
    if ratios and median_of(ratios) >= 0.5:
        return "not carried"
    return "approximate"


RANK = {"carried": 0, "approximate": 1, "not carried": 2}


def worst_of(words):
    """The worst of several words; `not judged` where any is."""
    if any(word == "not judged" for word in words):
        return "not judged"
    out = words[0]
    for word in words[1:]:
        if RANK[word] > RANK[out]:
            out = word
    return out


def one_word(value, twin, shuffle, halves, sample, rows, kind="difference", null=0.0, shown_rule=True):
    """One estimate's word: inside its scaled yardstick, half the shuffle's gap where a relationship shows, or neither."""
    if kind == "distance":
        gaps = list(halves)
        whole = math.sqrt(sum(gap * gap for gap in gaps) / 4.0)
        twin_gap, shuffle_gap = twin, shuffle
        shown = True
    else:
        whole = yardstick(halves, sample, rows)[0]
        twin_gap, shuffle_gap = abs(twin - value), abs(shuffle - value)
        shown = abs(value - null) > whole or not shown_rule
    if twin_gap <= whole * math.sqrt(sample / rows):
        return "carried"
    if shown and shuffle_gap > whole and shuffle_gap > 0.0 and twin_gap / shuffle_gap >= 0.5:
        return "not carried"
    return "approximate"


def pair_level(levels):
    """The first level whose every cell holding rows holds 22 rows and 11 in each of the eight halves; -1 where none does.

    `levels[k]` is `(whole, halves)`: the cells' counts on the sample and in
    each half, at level `k`.
    """
    for level, (whole, halves) in enumerate(levels):
        if all(whole[cell] >= 22 and all(half.get(cell, 0) >= 11 for half in halves) for cell in whole):
            return level
    return -1


def pair_words(table_word, correlation_words, skewed):
    """A pair's word: its table's and its correlations', the code scale's held at best approximate where skewed."""
    said = [table_word]
    for scale, word in correlation_words:
        if skewed and scale == "code" and word == "carried":
            word = "approximate"
        said.append(word)
    return worst_of(said)


def label_levels(codes, missing):
    """A label's levels read as F1's outcomes: codes of 22 rows or more, the empty band aside, the ten largest, ties by code."""
    counted = {}
    for code in codes:
        counted[code] = counted.get(code, 0) + 1
    ranked = sorted((-count, code) for code, count in counted.items() if code != missing and count >= 22)
    return [code for _count, code in ranked[:10]]


CHANCE_JOINT = 0.116


def unrelated(joint, supported, count_rule=False):
    """A family is too weakly related to judge where its share of joint estimates is under twice chance (the share alone, amended 2026-11-05)."""
    return (count_rule and joint < 5) or joint / supported < 2 * CHANCE_JOINT


def cases():
    """Every case with its mutant's outcome beside it."""
    out = {}
    hashes = [0x0123456789ABCDEF, 0xFEDCBA9876543210, 0x0123456789ABCDEF, 0, MASK]
    seeds = seeds_of(hashes)
    words = [stream(seed, 4) for seed in seeds]
    out["words"] = {
        "hashes": hashes,
        "seeds": seeds,
        "words": words,
        "groups": [row[0] & 15 for row in words],
        # MUTANT: equal rows not told apart by their place take one seed.
        "mutant_equal_rows_one_seed": seeds_of(hashes[:2])[0] == ((CONSTANT ^ hashes[2]) & MASK),
    }
    out["halves"] = {
        "groups": [[group for group in range(16) if (group >> j) & 1 == half] for j in range(4) for half in range(2)],
    }
    walk = stream(seeds[1], 7)
    out["walk_sums"] = {
        "seed": seeds[1],
        "family_0": hidden_sum(walk[1:4]),
        "family_1": hidden_sum(walk[4:7]),
        # MUTANT: family 1 read from words 0 to 2.
        "mutant_from_word_0": hidden_sum(walk[0:3]),
    }
    families = 2
    shuffle = {}
    for column in range(2):
        keyed = sorted((stream(seed, 1 + 3 * families + column + 1)[-1], row) for row, seed in enumerate(seeds))
        shuffle[f"column_{column}"] = [row for _key, row in keyed]
    out["shuffle"] = {"families": families, **shuffle}
    halves = [0.31, 0.29, 0.33, 0.30, 0.28, 0.32, 0.30, 0.31]
    whole, rest, small = yardstick(halves, 20000, 200000)
    out["yardstick"] = {
        "halves": halves,
        "h": whole,
        "replicate": rest,
        "scaled_20000_of_200000": small,
        "w2_judged_at_floor_11": 200000 * small >= 11,
        # MUTANT: the yardstick left unscaled is sqrt(10) times wider.
        "mutant_unscaled_over_scaled": whole / small,
    }
    family = []
    for at in range(8):
        base = 0.40 + 0.01 * at
        half_values = [base + 0.004 * ((at + j) % 3 - 1) for j in range(8)]
        family.append((base, base + 0.001, base - 0.2, base - 0.2, half_values))
    loose = [(value, value + 0.003, shuffle_value, null, halves) for value, _twin, shuffle_value, null, halves in family]
    far = [(value, value - 0.15, shuffle_value, null, halves) for value, _twin, shuffle_value, null, halves in family]
    keeping_less = []
    for at in range(8):
        base = 0.40 + 0.01 * at
        half_values = [base + 0.02, base - 0.02] + [base + 0.05 * (1 if j % 2 == 0 else -1) for j in range(6)]
        keeping_less.append((base, base + 0.07, base - 0.2, base - 0.2, half_values))
    out["judged"] = {
        "close_at_20000_of_20000": judged(family, 20000, 20000),
        "close_at_20000_of_200000": judged(family, 20000, 200000),
        "loose_at_20000_of_200000": judged(loose, 20000, 200000),
        "far_at_20000_of_200000": judged(far, 20000, 200000),
        "four_estimates": judged(family[:4], 20000, 20000),
        # MUTANT: the loose family judged with the yardstick unscaled reads carried.
        "mutant_loose_unscaled": judged(loose, 20000, 200000, scaled=False),
        # Inside the yardstick, but keeping less of the relationships than a fresh half.
        "keeping_less_at_20000_of_20000": judged(keeping_less, 20000, 20000),
        # MUTANT: the rule on what a fresh half keeps dropped.
        "mutant_keeping_less_without_the_rule": judged(keeping_less, 20000, 20000, kept_rule=False),
    }
    # THE JOINT SHARE: four estimates beside their null are outside, eight
    # joint ones inside; the joint ones read carried, all of them would not.
    unrelated_rows = []
    for at in range(4):
        base = 0.30 + 0.01 * at
        half_values = [base + 0.004 * ((at + j) % 3 - 1) for j in range(8)]
        unrelated_rows.append((base, base + 0.04, base, base, half_values))
    mixed = family + unrelated_rows
    out["joint"] = {
        "mixed_at_20000_of_20000": judged(mixed, 20000, 20000),
        "joint_count": sum(1 for one in mixed if abs(one[0] - one[3]) > yardstick(one[4], 20000, 20000)[0]),
        # MUTANT: the shares read on every supported estimate.
        "mutant_all_estimates": judged(mixed, 20000, 20000, joint_rule=False),
        "four_joint_falls_back": judged(family[:4] + unrelated_rows, 20000, 20000),
    }
    out["keys"] = {
        "carried_carried_approximate": worst_of(["carried", "carried", "approximate"]),
        "carried_not_judged_carried": worst_of(["carried", "not judged", "carried"]),
        "approximate_not_carried": worst_of(["approximate", "not carried", "carried"]),
        # MUTANT: the first key's word alone.
        "mutant_first_key": ["carried", "carried", "approximate"][0],
    }
    halves_close = [0.004, 0.005, 0.003, 0.004]
    out["pairs"] = {
        "table_carried_correlation_not": pair_words("carried", [("code", "not carried")], False),
        "table_carried_skewed_correlation_carried": pair_words("carried", [("code", "carried"), ("log", "carried")], True),
        "table_carried_log_not_judged": pair_words("carried", [("code", "carried"), ("log", "not judged")], False),
        # MUTANT: the cross-table alone.
        "mutant_table_alone": pair_words("carried", [], False),
        "one_distance_inside": one_word(0.0, 0.003, 0.2, halves_close, 20000, 20000, "distance"),
        "one_distance_far": one_word(0.0, 0.15, 0.2, halves_close, 20000, 20000, "distance"),
        "one_correlation_between": one_word(0.35, 0.30, 0.0, [0.36, 0.34, 0.35, 0.35, 0.36, 0.34, 0.35, 0.35], 20000, 200000),
        # A correlation the sample shows none of, the twin outside and the
        # shuffle beyond its yardstick by chance: approximate, never not
        # carried (no relationship shown to be lost).
        "one_correlation_unshown": one_word(0.005, -0.02, -0.03, [0.02, -0.01, 0.0, 0.01, 0.01, 0.0, 0.005, 0.005], 20000, 20000),
        # MUTANT: the rule dropped reads it not carried.
        "mutant_unshown_without_the_rule": one_word(0.005, -0.02, -0.03, [0.02, -0.01, 0.0, 0.01, 0.01, 0.0, 0.005, 0.005], 20000, 20000, shown_rule=False),
    }
    sparse = ({"a": 300, "b": 21}, [{"a": 150, "b": 11}] * 8)
    halved = ({"a": 300, "b": 30}, [{"a": 150, "b": 15}] * 7 + [{"a": 150, "b": 10}])
    merged = ({"ab": 330}, [{"ab": 165}] * 8)
    out["levels"] = {
        "sparse_then_merged": pair_level([sparse, halved, merged]),
        "full_at_l0": pair_level([merged, merged, merged]),
        "none": pair_level([sparse, halved, halved]),
        # MUTANT: the half rule dropped reads the halved table at L1.
        "mutant_without_halves": pair_level([sparse, ({"a": 300, "b": 30}, [{"a": 150, "b": 15}] * 8), merged]),
    }
    out["labels"] = {
        "levels": label_levels([0] * 40 + [1] * 22 + [2] * 21 + [3] * 60 + [4] * 30 + list(range(5, 17)) * 25, 4),
        "missing": 4,
    }
    out["unrelated"] = {
        "null_table_nine_in_a_hundred": unrelated(9, 100),
        "related_thirty_in_a_hundred": unrelated(30, 100),
        # A model's handful: two joint coefficients of six read a third, over
        # twice chance, so the family is judged (amended 2026-11-05: the share
        # alone; the fallback to every supported estimate stands at family
        # level).
        "two_of_six": unrelated(2, 6),
        # A logistic model with three strong coefficients of eight is judged.
        "three_of_eight": unrelated(3, 8),
        # MUTANT: repair 1's count clause (fewer than five joint) leaves both unjudged.
        "mutant_two_of_six_with_the_count_clause": unrelated(2, 6, count_rule=True),
        "mutant_three_of_eight_with_the_count_clause": unrelated(3, 8, count_rule=True),
        "line": 2 * CHANCE_JOINT,
        # MUTANT: the branch dropped judges the null table.
        "mutant_without_the_branch": False,
    }
    # A COMPARISON SKIPPED IS NO AFFIRMATION (amended 2026-11-05): five joint
    # estimates inside, four of them moved beyond their yardstick by the
    # shuffle (the twin's gap over the shuffle's .727, the replicate's .455).
    few = [(1.0, 1.08, 0.89, 0.0, [1.025, 0.975, 1.05, 0.95, 1.05, 0.95, 1.05, 0.95]) for _at in range(4)]
    few.append((1.0, 1.08, 0.91, 0.0, [1.025, 0.975, 1.05, 0.95, 1.05, 0.95, 1.05, 0.95]))
    out["comparisons"] = {
        "four_comparisons": judged(few, 20000, 20000),
        # MUTANT: fewer than five comparisons read as keeping the relationships.
        "mutant_few_comparisons_affirmed": judged(few, 20000, 20000, few_rule=False),
        # MUTANT: a comparison read past the line on its ratio alone calls
        # not carried a family the twin holds inside on all five.
        "mutant_four_comparisons_on_the_ratio_alone": judged(few, 20000, 20000, own_word_rule=False),
    }
    # EVERY COMPARISON PAST THE LINE (amended 2026-11-06): a heavily censored
    # table's logistic model, three strong coefficients of eight (8.7, 5.5
    # and 3.5 yardsticks from nought) missed by the trial twin past the line,
    # the replicate inside on seven of eight, the twin on five; a 40 %-blank
    # table's linear model, three coefficients near 14 yardsticks outside
    # (at 0.93, 0.37 and 0.93 of the shuffle's gap), the replicate on six of
    # eight, a fourth comparison the twin keeps inside (at 0.63 of the
    # shuffle's gap, 0.7 yardsticks from nought); and three comparisons, one
    # inside and two past the line.
    out["past_the_line"] = {}
    for name, rows in sorted(_few_comparison_cases().items()):
        out["past_the_line"][name] = judged(rows, 20000, 20000)
        # MUTANT: before the amendment, every such family read not judged.
        out["past_the_line"][f"mutant_{name}_before_the_amendment"] = judged(rows, 20000, 20000, past_rule=False)
        # MUTANT: the all-comparisons clause dropped.
        out["past_the_line"][f"mutant_{name}_without_the_all_clause"] = judged(rows, 20000, 20000, all_rule=False)
    return out


def _few_comparison_cases():
    """The three cases of the amendment of 2026-11-06, each `(sample, twin, shuffle, null, halves)` with h = 0.1."""
    even = [0.05, -0.05] * 4
    wide = [0.15, -0.15] + [0.05, -0.05] * 3

    def at(value, twin, shuffle, halves=even):
        return (value, twin, shuffle, 0.0, [value + held for held in halves])

    near_nought = [at(0.06, 0.08, 0.09), at(-0.05, -0.03, -0.02), at(0.04, 0.06, 0.07), at(-0.04, -0.02, -0.01)]
    return {
        "censored_logistic": [at(0.87, 0.30, 0.02), at(0.55, 0.15, -0.03), at(0.35, 0.10, 0.01)] + near_nought
        + [at(0.05, 0.07, 0.08, wide)],
        "blank_linear": [at(1.43, 0.12, 0.02), at(1.42, 0.89, -0.01), at(1.39, 0.12, 0.03), at(0.07, 0.15, -0.057)]
        + [at(0.02, 0.03, 0.04), at(0.02, 0.03, 0.01), at(0.02, 0.03, 0.04, wide), at(0.01, 0.02, 0.03, wide)],
        "mixed": [at(0.87, 0.30, 0.02), at(0.55, 0.15, -0.03), at(0.35, 0.33, 0.01)] + near_nought
        + [at(0.05, 0.07, 0.08)],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    text = json.dumps(cases(), indent=1, sort_keys=True) + "\n"
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


if __name__ == "__main__":
    main()

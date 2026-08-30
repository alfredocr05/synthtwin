"""P4-G6-R1-F1: does the scaled branch move any merge the plain one made?

`_merge_nearest` normalises a pair's distance by the pair's own size.
The divisor `|high| + |low|` overflows on two large rungs of one sign,
so a second branch scales both by the larger magnitude first -- and
that branch is taken ONLY where the plain divisor has no answer,
because the two forms part by one unit in the last place on a fraction
of pairs. This walks random rung sets, works the shipped key out
alongside, and counts the merges where the two part.

Stated in `docs/plans/phase-4-columns.md` under P4-G6-R1 as 300000
merges with zero move.
"""

import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "src"))

from synthtwin import generation, parsing  # noqa: E402

MERGES = 300000


def shipped_choice(lengths: "list[int]", held: "list[float]") -> int:
    """The pair the key picked before the second branch was added."""
    best, best_key = 0, None
    for place in range(len(held) - 1):
        low, high = held[place], held[place + 1]
        span = abs(high) + abs(low)
        gap = 0.0
        if 0.0 < span < float("inf"):
            gap = abs(high / span - low / span)
        alike = parsing.is_whole_number(low) == parsing.is_whole_number(high)
        key = (min(lengths[place], lengths[place + 1]), 0 if alike else 1, gap)
        if best_key is None or key < best_key:
            best, best_key = place, key
    return best


def main() -> None:
    random.seed(11)
    tried = moved = overflowed = 0
    for _step in range(MERGES):
        count = random.randint(2, 8)
        held = sorted(
            random.uniform(-10, 10) * 10.0 ** random.randint(-300, 300)
            for _each in range(count)
        )
        if len(set(held)) < count:
            continue
        lengths = [random.randint(1, 9) for _each in range(count)]
        tried = tried + 1
        if any(
            abs(held[at]) + abs(held[at + 1]) == float("inf")
            for at in range(count - 1)
        ):
            overflowed = overflowed + 1
        best = shipped_choice(lengths, held)
        want = (
            lengths[:best]
            + [lengths[best] + lengths[best + 1]]
            + lengths[best + 2:]
        )
        got, _values = generation._merge_nearest(list(lengths), list(held))
        if got != want:
            moved = moved + 1
    print(f"merges tried: {tried}")
    print(f"  where the shipped divisor overflowed: {overflowed}")
    print(f"  where the shipped and current choice differ: {moved}")


if __name__ == "__main__":
    main()

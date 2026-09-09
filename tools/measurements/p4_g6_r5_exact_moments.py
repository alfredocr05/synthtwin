"""P4-G6-R5: what the exact moments cost a column that already worked.

The twin report used to recount the four moments from the finished
cells with a compensated sum in binary64. It now asks
`taxonomy.moments_of`, the same exact computation the description's own
numbers come from. This walks ordinary columns of several shapes and
counts where the reported number MOVES.

IT ALSO COUNTS THE TWO VERDICTS the twin report prints beside a moment
-- `inside`, whether the twin landed in its allowed range, and
`covers_published`, whether that range reaches the description's own
value -- because a number moving in its last digit only matters if it
changes what the report TELLS a reader. The first version of this file
said in its header that it counted those and its loop never read
either field (review item P4-G6-R6-F2). A tool committed so that a
claim can be re-derived is worth nothing if it makes a claim of its own
that its code does not support.

AND ITS COMPARATOR IS THE REAL PREDECESSOR. The first version of this
file wrote out a simplified recount that omitted the scaled fallback
the round-4 parent actually carried, so it credited this change with
answers round 4 already gave. `_recounted` below is the body of
`_moments_of` as it stood at commit 8ef1bb7, copied rather than
paraphrased.
"""

import math
import pathlib
import random
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
    taxonomy,
)

COLUMNS = 150


def recounted(values: "list[float]") -> tuple:
    """`_moments_of` exactly as it stood at commit 8ef1bb7.

    Copied from that commit rather than written again from memory: a
    comparator that is a paraphrase of the thing it compares against
    measures the paraphrase.
    """
    held = len(values)
    mean = generation._mean_of(values)
    if held < 2:
        return (mean, None, None, None)
    if len(set(values)) == 1:
        return (mean, 0.0, None, None)
    spread = generation._summed(
        [(value - mean) * (value - mean) / held for value in values]
    )
    root = 0.0
    if math.isfinite(spread) and spread > 0:
        root = math.sqrt(spread)
    else:
        widest = 0.0
        for value in values:
            step = abs(value - mean)
            if math.isfinite(step) and step > widest:
                widest = step
        if widest <= 0.0:
            return (mean, None, None, None)
        parts = generation._summed(
            [
                ((value - mean) / widest) * ((value - mean) / widest) / held
                for value in values
            ]
        )
        if not math.isfinite(parts) or parts <= 0.0:
            return (mean, None, None, None)
        root = widest * math.sqrt(parts)
    if not math.isfinite(root) or root <= 0.0:
        return (mean, None, None, None)
    deviation = root * math.sqrt(held / (held - 1))
    if not math.isfinite(deviation):
        return (mean, None, None, None)
    if held < 3:
        return (mean, deviation, None, None)
    shape = generation._summed(
        [
            ((value - mean) / root)
            * ((value - mean) / root)
            * ((value - mean) / root)
            / held
            for value in values
        ]
    )
    if held < 4:
        return (mean, deviation, shape, None)
    tails = generation._summed(
        [
            ((value - mean) / root)
            * ((value - mean) / root)
            * ((value - mean) / root)
            * ((value - mean) / root)
            / held
            for value in values
        ]
    )
    return (mean, deviation, shape, tails)


def main() -> None:
    random.seed(20260830)
    shapes = []
    for _trial in range(COLUMNS):
        count = random.choice([20, 60, 120, 240])
        kind = random.choice(["normal", "wide", "small", "negative", "counts"])
        if kind == "normal":
            rows = [repr(random.gauss(50, 12)) for _each in range(count)]
        elif kind == "wide":
            rows = [
                repr(random.uniform(1, 9) * 10 ** random.randint(0, 12))
                for _each in range(count)
            ]
        elif kind == "small":
            rows = [repr(random.uniform(0, 1)) for _each in range(count)]
        elif kind == "negative":
            rows = [repr(random.gauss(-500, 200)) for _each in range(count)]
        else:
            rows = [str(random.randint(0, 40)) for _each in range(count)]
        shapes.append(rows)

    built = refused = compared = moved = judged = appeared = 0
    worst = 0.0
    gained = []
    flipped = []
    verdicts: dict = {}
    exact = generation._moments_of
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for index, rows in enumerate(shapes):
            try:
                fixtures.write(
                    home, f"m{index}.csv", "value\n" + "\n".join(rows) + "\n"
                )
                table = reading.read_table(
                    str(home / f"m{index}.csv"),
                    first_row=reading.FIRST_ROW_AUTOMATIC,
                )
                document = profile.build_document(
                    table, taxonomy.Settings(), []
                )
                loaded = contract.load_profile(
                    str(
                        fixtures.write_profile(
                            home, f"m{index}-p.json", document
                        )
                    )
                )
            except Exception:      # a shape the loader refuses
                refused = refused + 1
                continue
            built = built + 1
            for label, recount in (("now", None), ("was", recounted)):
                if recount is None:
                    generation._moments_of = exact
                else:
                    generation._moments_of = recount
                twin = generation.generate(loaded, 7)
                verdicts[label] = {
                    step.fact: (step.inside, step.covers_published)
                    for step in twin.approximations
                    if step.fact in ("mean", "std", "skew", "kurtosis")
                }
                if label == "now":
                    values = [
                        float(cell) for cell in twin.columns[0] if cell != ""
                    ]
            generation._moments_of = exact
            for fact in set(verdicts["now"]) | set(verdicts["was"]):
                if fact not in verdicts["now"] or fact not in verdicts["was"]:
                    appeared = appeared + 1
                    continue
                judged = judged + 1
                if verdicts["now"][fact] != verdicts["was"][fact]:
                    flipped.append((index, fact,
                                    verdicts["was"][fact],
                                    verdicts["now"][fact]))
            if len(values) < 4:
                continue
            now = exact(values)
            was = recounted(values)
            for place in range(4):
                if was[place] is None and now[place] is not None:
                    gained.append((index, place))
                    continue
                if was[place] is None or now[place] is None:
                    continue
                compared = compared + 1
                if was[place] != now[place]:
                    moved = moved + 1
                    if was[place] != 0.0:
                        worst = max(
                            worst,
                            abs(was[place] - now[place]) / abs(was[place]),
                        )

    print(f"columns built: {built}   refused: {refused}")
    print(f"moments compared: {compared}")
    print(f"  where the reported number moves: {moved}")
    print(f"  largest relative move: {worst}")
    print(f"  moments the recount had NO answer for and this does: "
          f"{len(gained)}")
    print(f"report verdicts compared: {judged}   "
          f"lines present under one recount only: {appeared}")
    print(f"  where `inside` or `covers_published` FLIPS: {len(flipped)}")
    for row in flipped[:8]:
        print(f"    column {row[0]} {row[1]}: was {row[2]} now {row[3]}")


if __name__ == "__main__":
    main()

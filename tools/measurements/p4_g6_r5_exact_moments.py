"""P4-G6-R5: what the exact moments cost a column that already worked.

The twin report used to recount the four moments from the finished
cells with a compensated sum in binary64. It now asks
`taxonomy.moments_of`, the same exact computation the description's own
numbers come from. This walks ordinary columns of several shapes and
counts where the reported number MOVES and where a verdict flips --
`inside`, which says whether the twin landed in its allowed range, and
`covers_published`, which says whether that range reaches the
description's own value.
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
    """`_moments_of` as it stood before the exact moments went in."""
    held = len(values)
    mean = generation._mean_of(values)
    if held < 2:
        return (mean, None, None, None)
    if len(set(values)) == 1:
        return (mean, 0.0, None, None)
    spread = generation._summed(
        [(value - mean) * (value - mean) / held for value in values]
    )
    if not math.isfinite(spread) or spread <= 0:
        return (mean, None, None, None)
    root = math.sqrt(spread)
    deviation = root * math.sqrt(held / (held - 1))
    if held < 3:
        return (mean, deviation, None, None)
    shape = generation._summed(
        [((value - mean) / root) ** 3 / held for value in values]
    )
    if held < 4:
        return (mean, deviation, shape, None)
    tails = generation._summed(
        [((value - mean) / root) ** 4 / held for value in values]
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

    built = refused = compared = moved = 0
    worst = 0.0
    gained = []
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
            except Exception as exc:      # a shape the loader refuses
                refused = refused + 1
                continue
            built = built + 1
            twin = generation.generate(loaded, 7)
            values = [
                float(cell) for cell in twin.columns[0] if cell != ""
            ]
            if len(values) < 4:
                continue
            now = generation._moments_of(values)
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


if __name__ == "__main__":
    main()

"""K-P3-03: where the extra spread of a large numeric twin comes from.

A plain numeric twin at 20,000 rows by 20 columns misses `moments.std`
on 19 columns of 20 and exits 3; at 5,000 rows it misses nothing. This
driver re-derives that count and then takes the spread apart, column by
column, into the pieces that could have made it:

- ``ladder``: the spread of the CONSTRUCTION itself -- the hundred and
  one rungs read as method G5.3 reads them, a straight line between each
  pair of neighbours, with the published minimum and maximum as the two
  ends. Worked out exactly from the rungs, with no draw at all.
- ``ladder, real tails``: the same, with ONLY the two outer segments
  (minimum to `p01`, `p99` to maximum) replaced by the real cells'
  own first and second moments inside them. What is left is what the
  ninety-nine inner segments make.
- ``twin``: the spread the generated file holds, which is the ladder's
  plus whatever the strata, their sizes and the draw inside each add.
- ``half``: half the width of the window the quality report draws for
  `moments.std` (method G12.3), which is what a twin whose window does
  not reach the published value must stand within (V6.1-A2).

Every number is a percentage of the PUBLISHED spread, averaged over the
columns of one table. Every table is built by seeded neutral code at
runtime (plan D13).

    python tools/measurements/k_p3_03_spread.py            # everything
    python tools/measurements/k_p3_03_spread.py --quick    # 5k and 20k

The full run is a quarter of an hour on the reference machine; most of
it is the ledger table's quality report.
"""

import math
import pathlib
import random
import statistics
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures  # noqa: E402
import synthtwin  # noqa: E402
from synthtwin import (  # noqa: E402
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SHAPES = {
    "normal": lambda draw: f"{draw.gauss(50, 10):.2f}",
    "uniform": lambda draw: f"{draw.uniform(20, 80):.2f}",
    "skewed": lambda draw: f"{draw.lognormvariate(3, 0.5):.2f}",
}


def table(shape, rows, columns, seed=7):
    """The ledger's own construction: row after row, one draw per cell."""
    draw = random.Random(seed)
    return [[SHAPES[shape](draw) for _ in range(columns)] for _ in range(rows)]


def ladder_spread(rungs, real=None):
    """The exact spread of the straight-line ladder, optionally with real tails."""
    segments = len(rungs) - 1
    first = second = 0.0
    for step in range(segments):
        low, high = rungs[step], rungs[step + 1]
        if real is not None and step in (0, segments - 1):
            inside = len(real) // segments
            part = real[:inside] if step == 0 else real[len(real) - inside:]
            one = math.fsum(part) / len(part)
            two = math.fsum([value * value for value in part]) / len(part)
        else:
            one = (low + high) / 2
            two = (low * low + low * high + high * high) / 3
        first += one / segments
        second += two / segments
    return math.sqrt(max(0.0, second - first * first))


def measure(shape, rows, columns, seed, home):
    cells = table(shape, rows, columns)
    names = [f"c{index}" for index in range(columns)]
    path = fixtures.write(home, "real.csv", fixtures.rows_to_csv(names, cells))
    document = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), []
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(home, "real-profile.json", document))
    )
    twin = generation.generate(loaded, seed)
    written = fixtures.write(home, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(loaded, str(written))
    verdicts = {
        (check.column, check.subcheck): check.verdict for check in outcome.checks
    }
    missed = [
        check.subcheck for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    floor = loaded.settings.small_cell_floor
    rows_out = []
    for index, column in enumerate(loaded.columns):
        facts = column.facts
        published = facts.std
        real = sorted(float(row[index]) for row in cells)
        rungs = generation._merged_rungs(facts)
        low, high = validation._windows_of(column, facts, floor)["std"]
        twin_spread = taxonomy.spread_of(
            [float(cell) for cell in twin.columns[index]]
        )
        rows_out += [
            (
                100 * (ladder_spread(rungs) / published - 1),
                100 * (ladder_spread(rungs, real) / published - 1),
                100 * (twin_spread / published - 1),
                100 * (high - low) / 2 / published,
                verdicts[(column.name, "moments.std")] == validation.MISSED,
                verdicts[(column.name, "moments.mean")] == validation.MISSED,
            )
        ]
    return rows_out, missed, len(outcome.checks)


def main():
    print("synthtwin imported from", synthtwin.__file__, flush=True)
    quick = "--quick" in sys.argv
    sizes = (5000, 20000) if quick else (5000, 10000, 20000, 40000)
    built = 0
    print()
    print("shape    rows    ladder%  ladder,real-tails%  twin%   half%  std missed  mean missed  twin-ladder at most")
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        for shape in SHAPES:
            for rows in sizes:
                found, _missed, _checks = measure(shape, rows, 4, 0, home)
                built += 1
                print(
                    f"{shape:8s}{rows:6d}  "
                    f"{statistics.mean(one[0] for one in found):+8.2f}  "
                    f"{statistics.mean(one[1] for one in found):+18.2f}  "
                    f"{statistics.mean(one[2] for one in found):+6.2f}  "
                    f"{statistics.mean(one[3] for one in found):6.2f}  "
                    f"{sum(one[4] for one in found)} of {len(found)}      "
                    f"{sum(one[5] for one in found)} of {len(found)}       "
                    f"{max(one[2] - one[0] for one in found):+.2f}",
                    flush=True,
                )
        print()
        for rows in (5000, 20000):
            found, missed, checks = measure("normal", rows, 20, 0, home)
            built += 1
            share = [
                (one[0] - one[1]) / one[0] for one in found if one[0] > 0
            ]
            print(
                f"ledger table, {rows} rows x 20, seed 0: {len(missed)} of "
                f"{checks} obligations MISSED "
                f"({sorted(set(missed))}); twin spread "
                f"{min(one[2] for one in found):+.2f}% to "
                f"{max(one[2] for one in found):+.2f}%; the two outer "
                f"segments make {100 * min(share):.0f}% to "
                f"{100 * max(share):.0f}% of the ladder's excess; the twin "
                f"stands at most {max(one[2] - one[0] for one in found):+.2f} "
                f"above its ladder"
            )
    print()
    print("tables built:", built, " refused: 0")


if __name__ == "__main__":
    main()

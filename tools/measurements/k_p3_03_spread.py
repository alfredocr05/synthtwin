"""K-P3-03: where the extra spread of a numeric twin comes from.

A plain numeric twin at 20,000 rows by 20 columns misses `moments.std`
on 19 columns of 20 and exits 3; at 5,000 rows it misses nothing, and
on coarsely rounded columns it misses nothing at any size -- although
the twin's spread is 1.5 to 3.7 per cent too wide in every one of those
cases. This driver re-derives all of that and takes the spread apart,
column by column, into the pieces that could have made it:

- ``ladder``: the spread of the CONSTRUCTION itself -- the hundred and
  one rungs read as method G5.3 reads them, a straight line between each
  pair of neighbours, with the published minimum and maximum as the two
  ends. Worked out exactly from the rungs, with no draw at all.
- ``real tails``: the same, with ONLY the two outer segments (minimum
  to `p01`, `p99` to maximum) replaced by the real cells' own first and
  second moments inside them. What is left is what the ninety-nine inner
  segments make.
- ``bend``: the one power, found from the PUBLISHED spread alone, that
  bends those two outer segments toward `p01` and `p99` -- keeping every
  published rung as a segment end -- so the ladder's spread is exactly
  the published one. It shows the repair needs nothing the description
  does not publish.
- ``twin``: the spread the generated file holds.
- ``window``: the low and high ends of the `moments.std` window the
  quality report draws (method G12.3). It is centred on ``ladder``'s
  own reading, so where its low end is above nought the window excludes
  the published spread itself, and a twin repaired in G5.3 alone would
  be MISSED there.

Every number is a percentage of the PUBLISHED spread. Every table is
built by seeded neutral code at runtime (plan D13); the lab-like shapes
reproduce the ones the K-P3-03 review measured.

    python tools/measurements/k_p3_03_spread.py            # everything
    python tools/measurements/k_p3_03_spread.py --quick    # 5k and 20k

The full run is about half an hour on the reference machine; most of it
is the ledger table's two quality reports.
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

# Lab-like columns, two to a table: (seed, names, one row).
LAB = {
    "lab": (
        11,
        ["potassium_1dp", "sodium_int"],
        lambda d: [f"{d.gauss(4.2, 0.5):.1f}", f"{d.gauss(139, 3):.0f}"],
    ),
    "vitals": (
        12,
        ["sbp_int", "age_int"],
        lambda d: [str(int(d.gauss(128, 17))), str(int(d.triangular(18, 95, 60)))],
    ),
    "gappy": (
        14,
        ["hb_1dp", "mass_1dp"],
        lambda d: [
            "" if d.random() < 0.06 else f"{d.gauss(13.5, 1.6):.1f}",
            "" if d.random() < 0.1 else f"{d.gauss(27, 5):.1f}",
        ],
    ),
    "clipped": (
        15,
        ["spo2_int", "score_1dp"],
        lambda d: [
            f"{min(100.0, max(80.0, d.gauss(96, 2.5))):.0f}",
            f"{min(100.0, max(0.0, d.gauss(70, 20))):.1f}",
        ],
    ),
}

# The widest the ledger twin's spread may stand from the published one,
# either way, before this driver says so (measured largest 3.418).
WIDEST = 3.5


def table(shape, rows, columns, seed=7):
    """The ledger's own construction: row after row, one draw per cell."""
    draw = random.Random(seed)
    return [[SHAPES[shape](draw) for _ in range(columns)] for _ in range(rows)]


def ladder(rungs, bend=1.0, real=None):
    """Exact mean and spread of the ladder; bent or with real tails."""
    segments = len(rungs) - 1
    first = second = 0.0
    for step in range(segments):
        low, high = rungs[step], rungs[step + 1]
        outer = step in (0, segments - 1)
        if real is not None and outer:
            inside = len(real) // segments
            part = real[:inside] if step == 0 else real[len(real) - inside:]
            one = math.fsum(part) / len(part)
            two = math.fsum([value * value for value in part]) / len(part)
        elif outer:
            anchor = high if step == 0 else low
            reach = (low - high) if step == 0 else (high - low)
            one = anchor + reach / (bend + 1)
            two = (
                anchor * anchor
                + 2 * anchor * reach / (bend + 1)
                + reach * reach / (2 * bend + 1)
            )
        else:
            one = (low + high) / 2
            two = (low * low + low * high + high * high) / 3
        first += one / segments
        second += two / segments
    return first, math.sqrt(max(0.0, second - first * first))


def bend_meeting(rungs, published):
    """The outer-segment power whose ladder has the published spread."""
    low, high = 1.0, 64.0
    if ladder(rungs, low)[1] <= published or ladder(rungs, high)[1] >= published:
        return None
    for _ in range(60):
        middle = (low + high) / 2
        if ladder(rungs, middle)[1] > published:
            low = middle
        else:
            high = middle
    return high


def measure(names, cells, seed, home, real_too=False):
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
    real_missed = None
    if real_too:
        real_missed = [
            check.subcheck
            for check in validation.measure(loaded, str(path)).checks
            if check.verdict == validation.MISSED
        ]
    floor = loaded.settings.small_cell_floor
    rows_out = []
    for index, column in enumerate(loaded.columns):
        facts = column.facts
        published = facts.std
        real = sorted(float(row[index]) for row in cells if row[index] != "")
        rungs = generation._merged_rungs(facts)
        low, high = validation._windows_of(column, facts, floor)["std"]
        twin_spread = taxonomy.spread_of(
            [float(cell) for cell in twin.columns[index] if cell != ""]
        )
        rows_out += [
            {
                "name": column.name,
                "ladder": 100 * (ladder(rungs)[1] / published - 1),
                "real_tails": 100 * (ladder(rungs, 1.0, real)[1] / published - 1),
                "bend": bend_meeting(rungs, published),
                "twin": 100 * (twin_spread / published - 1),
                "low": 100 * (low / published - 1),
                "high": 100 * (high / published - 1),
                "std_missed": verdicts[(column.name, "moments.std")]
                == validation.MISSED,
                "mean_missed": verdicts[(column.name, "moments.mean")]
                == validation.MISSED,
            }
        ]
    return rows_out, missed, len(outcome.checks), real_missed


def shown(value):
    return "  none" if value is None else f"{value:6.2f}"


def main():
    print("synthtwin imported from", synthtwin.__file__, flush=True)
    quick = "--quick" in sys.argv
    sizes = (5000, 20000) if quick else (5000, 10000, 20000, 40000)
    built = 0
    print()
    print("1. By shape, four columns each, means over the columns")
    print("shape    rows    ladder%  real-tails%  twin%   window-low%  bend    std missed  mean missed")
    with tempfile.TemporaryDirectory() as folder:
        home = pathlib.Path(folder)
        names = [f"c{index}" for index in range(4)]
        for shape in SHAPES:
            for rows in sizes:
                found, _missed, _checks, _real = measure(
                    names, table(shape, rows, 4), 0, home
                )
                built += 1
                bends = [one["bend"] for one in found if one["bend"] is not None]
                print(
                    f"{shape:8s}{rows:6d}  "
                    f"{statistics.mean(one['ladder'] for one in found):+8.2f}  "
                    f"{statistics.mean(one['real_tails'] for one in found):+11.2f}  "
                    f"{statistics.mean(one['twin'] for one in found):+6.2f}  "
                    f"{statistics.mean(one['low'] for one in found):+11.2f}  "
                    f"{shown(statistics.mean(bends) if bends else None)}  "
                    f"{sum(one['std_missed'] for one in found)} of {len(found)}      "
                    f"{sum(one['mean_missed'] for one in found)} of {len(found)}",
                    flush=True,
                )
        print()
        print("2. Lab-like columns, one line each: the excess the verdict does not see")
        print("column          rows    twin%   ladder%  real-tails%  bend   window%            std missed")
        for key, (seed, labels, row) in LAB.items():
            for rows in (5000, 20000):
                draw = random.Random(seed)
                cells = [row(draw) for _ in range(rows)]
                found, _missed, _checks, _real = measure(labels, cells, 0, home)
                built += 1
                for one in found:
                    print(
                        f"{one['name']:14s}{rows:6d}  {one['twin']:+6.2f}  "
                        f"{one['ladder']:+7.2f}  {one['real_tails']:+11.2f}  "
                        f"{shown(one['bend'])}  "
                        f"[{one['low']:+8.2f}, {one['high']:+8.2f}]  "
                        f"{'yes' if one['std_missed'] else 'no'}",
                        flush=True,
                    )
        print()
        print("3. The ledger table, 20 columns of gauss(50, 10), seed 0")
        names = [f"c{index}" for index in range(20)]
        for rows in (5000, 20000):
            found, missed, checks, real_missed = measure(
                names, table("normal", rows, 20), 0, home, real_too=True
            )
            built += 1
            share = [
                (one["ladder"] - one["real_tails"]) / one["ladder"]
                for one in found if one["ladder"] > 0
            ]
            twins = [one["twin"] for one in found]
            excluded = sum(one["low"] > 0 for one in found)
            bends = [one["bend"] for one in found if one["bend"] is not None]
            print(
                f"{rows} rows: twin {len(missed)} of {checks} obligations "
                f"MISSED ({sorted(set(missed))}), real {len(real_missed)}; "
                f"twin spread {min(twins):+.2f}% to {max(twins):+.2f}%, "
                f"within +-{WIDEST}%: {'yes' if max(map(abs, twins)) <= WIDEST else 'NO'}; "
                f"the two outer segments make {100 * min(share):.0f}% to "
                f"{100 * max(share):.0f}% of the ladder's excess; the std "
                f"window excludes the published spread on {excluded} of "
                f"{len(found)} columns; the bend meeting the published spread "
                f"is {min(bends):.2f} to {max(bends):.2f} on {len(bends)} columns"
            )
    print()
    print("tables built:", built, " refused: 0")


if __name__ == "__main__":
    main()

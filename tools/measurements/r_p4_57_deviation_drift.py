"""Does the R-P4-57 repair move any window on an ORDINARY column?

The four sites now divide before they raise. On values whose squares
and cubes are representable the two arithmetics compute the same
quantity, but not necessarily the same binary64 -- so this measures it
rather than asserting it, over columns of many shapes and magnitudes.
"""
import math
import pathlib
import random
import sys
import tempfile
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import fixtures
from synthtwin import profile, taxonomy, reading, contract, validation


def old_sample(values, count):
    mean = math.fsum(values) / count
    return math.sqrt(
        math.fsum([(value - mean) ** 2 for value in values]) / (count - 1)
    )


def old_population(values, count):
    mean = math.fsum(values) / count
    return math.sqrt(
        math.fsum([(value - mean) ** 2 for value in values]) / count
    )


def old_windows(lows, highs, ladder, numbers):
    """`_moment_windows` as it shipped, for the mean/std/skew ends."""
    found = {}
    mean_low = math.fsum(lows) / numbers
    mean_high = math.fsum(highs) / numbers
    found["mean"] = (mean_low, mean_high)
    if numbers < 2:
        return found
    spread = 0.0
    for rank in range(numbers):
        reach = max(ladder[rank] - lows[rank], highs[rank] - ladder[rank])
        spread = spread + reach * reach
    displacement = math.sqrt(spread / numbers)
    sample = old_sample(ladder, numbers)
    widen = displacement * math.sqrt(numbers / (numbers - 1))
    found["std"] = (max(0.0, sample - widen), sample + widen)
    return found


random.seed(20260830)
shapes = []
for _trial in range(120):
    n = random.choice([20, 40, 80, 150])
    kind = random.choice(["small", "ordinary", "wide", "negative", "mixed"])
    if kind == "small":
        rows = [repr(random.uniform(0, 1)) for _ in range(n)]
    elif kind == "ordinary":
        rows = [repr(random.gauss(50, 12)) for _ in range(n)]
    elif kind == "wide":
        rows = [repr(random.uniform(1, 9) * 10 ** random.randint(0, 12))
                for _ in range(n)]
    elif kind == "negative":
        rows = [repr(random.gauss(-500, 200)) for _ in range(n)]
    else:
        rows = [repr(random.gauss(0, 1) * 10 ** random.randint(-6, 6))
                for _ in range(n)]
    shapes.append(rows)

built = compared = moved = 0
worst = 0.0
with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)
    for index, rows in enumerate(shapes):
        try:
            fixtures.write(home, f"o{index}.csv", "value\n" + "\n".join(rows) + "\n")
            table = reading.read_table(str(home / f"o{index}.csv"),
                                       first_row=reading.FIRST_ROW_AUTOMATIC)
            doc = profile.build_document(table, taxonomy.Settings(), [])
            loaded = contract.load_profile(
                str(fixtures.write_profile(home, f"o{index}-p.json", doc)))
        except Exception:
            continue
        built += 1
        column = loaded.columns[0]
        now = validation._windows_of(column, column.facts)
        if not now:
            continue
        # the shipped deviation, on the same ladder the validator reads
        facts = column.facts
        points = validation._fine_ladder_points(facts)
        numbers = validation._numeric_cells(facts)
        ladder = [validation._ladder_at(points, (rank + 0.5) / numbers)
                  for rank in range(numbers)]
        was = old_sample(ladder, numbers)
        is_now = validation._sample_deviation(ladder, numbers)
        compared += 1
        if was != is_now:
            moved += 1
            if was != 0.0:
                worst = max(worst, abs(was - is_now) / abs(was))

print("columns built:", built, " deviations compared:", compared)
print("  where the shipped and repaired deviation differ at all:", moved)
print("  largest relative difference seen:", worst)

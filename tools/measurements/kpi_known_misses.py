"""K-2B-47 (OPEN): the carried fidelity misses, held still until stage 3 closes them.

The stage-2b plan carries four measured misses that no other KPI holds,
each rebuilt here from its plan statement with a committed seed:

- percent: the study workbook's `0.00%` column (tests/workbooks.py,
  2,000 rows), whose twin missed both published fraction widths at
  seeds 4 and 11 (plan phase-4, P4-D238 item 5);
- dose: a dose written at two fraction widths beside point-free cells,
  400 rows, at nine seeds and floors 1 and 11 (the 2b.7 carried item:
  18 of 18 runs missed);
- temperature: 4,000 readings at one decimal, whose twin put more cells
  on one value than the published mode count (a carrier stratum above
  mode_count, 2b.1);
- heavy tail: 2,000 Pareto charges of shape 1.1, whose twin misses the
  published mean (stage 3, deferred by the owner).

Printed: per shape, the runs with any MISSED verdict (for temperature,
the runs holding a value more often than the mode count), and the runs
made. The ledger holds each as a must-not-get-worse bound with target
0. A few minutes.

    .venv/bin/python tools/measurements/kpi_known_misses.py --kpi
"""

import collections
import pathlib
import random
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import workbooks  # noqa: E402
from synthtwin import generation, parsing, rendering  # noqa: E402

kpi_rules.guard_this_tree()
value = {}
details = []


def column_text(name, cells):
    return name + "\n" + "\n".join(cells) + "\n"


with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)

    missed_runs = runs = 0
    for seed in ("4", "11"):
        here = home / f"percent-{seed}"
        here.mkdir()
        book = here / "study.xlsx"
        book.write_bytes(workbooks.study_book(2000, 0, "excel"))
        run = kpi_shapes.cycle(book, [], seed)
        runs += 1
        missed_runs += run["validate_twin"] != 0
        details += [f"percent seed {seed}: {run['validate_twin']}/{run['validate_real']}"]
    value.update(percent_missed_runs=missed_runs, percent_runs=runs)

    draw = random.Random(20260918)
    dose = []
    for _ in range(400):
        kind = draw.random()
        if kind < 0.4:
            dose += [f"{draw.randrange(1, 40)}"]
        elif kind < 0.7:
            dose += [f"{draw.randrange(10, 400) / 10:.1f}"]
        else:
            dose += [f"{draw.randrange(100, 4000) / 100:.2f}"]
    missed_runs = runs = 0
    for floor in (1, 11):
        described = kpi_shapes.describe(home / f"dose-{floor}", "dose", column_text("dose", dose), floor)
        for seed in range(1, 10):
            found = kpi_shapes.missed(kpi_shapes.measure(
                described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))
            runs += 1
            missed_runs += bool(found)
            if found:
                details += [f"dose f{floor} s{seed}: {found}"]
    value.update(dose_missed_runs=missed_runs, dose_runs=runs)

    draw = random.Random(4000)
    temperature = [f"{draw.gauss(37.0, 0.6):.1f}" for _ in range(4000)]
    described = kpi_shapes.describe(home / "temperature", "temperature",
                                    column_text("temperature", temperature))
    mode_count = described.block("temperature").get("mode_count")
    over = runs = 0
    for seed in (4, 11):
        cells = [c for c in generation.generate(described.loaded, seed).columns[0] if c]
        held = max(collections.Counter(parsing.parse_number(c) for c in cells).values())
        runs += 1
        over += mode_count is not None and held > mode_count
        details += [f"temperature seed {seed}: twin max {held} against mode_count {mode_count}"]
    value.update(temperature_over_mode_runs=over, temperature_runs=runs)

    draw = random.Random(7)
    charges = [f"{draw.paretovariate(1.1) * 100:.2f}" for _ in range(2000)]
    described = kpi_shapes.describe(home / "heavy", "charge", column_text("charge", charges))
    missed_runs = runs = 0
    for seed in (3, 11):
        twin = generation.generate(described.loaded, seed)
        found = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
        runs += 1
        missed_runs += bool(found)
        if found:
            details += [f"heavy tail s{seed}: {found}"]
    value.update(heavy_tail_missed_runs=missed_runs, heavy_tail_runs=runs)

for line in details:
    print(line)
kpi_rules.emit("K-2B-47", value, "; ".join(details)[:2000])

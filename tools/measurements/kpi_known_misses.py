"""K-2B-47 and K-2B-49 (OPEN): carried fidelity misses and the calls of 2026-09-18, held still.

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

The carried residue of the integration of 2026-09-19, each rebuilt from
its plan statement and added to the battery with the same rule:

- date joint word: fifteen `03/05/2020`, fifteen `04/06/2020`, seven
  `3/7/2020` and seven `03/8/2020` at a floor of eleven, whose twin writes
  every cell padded (plan P4-D294, carried defect a), seeds 4, 0 and 1;
- date remainder: ten `11/05/2020`, seventeen `11/15/2020`, seventeen
  `12/20/2020`, nine `3/15/2020`, nine `03/16/2020` and nine `11/5/2020`,
  whose remainder outnumbers the named word (P4-D294, defect b), at
  floors 1 and 11, seeds 4, 0 and 1;
- record layout: a declared record number of ten `(-6)`, four `(-71)` and
  one `8xEa` at the default floor, whose twin misses its `(-%)` layout
  (plan P4-D298), seeds 4, 0 and 1;
- band split: twelve negatives once each, a zero and 1 to 10 forty times
  each, where G5.2 gives a sign band more strata than it has points
  (plan P4-D274's named limit); the number of different values the twin
  falls short of the published count, summed over seeds 7 and 4 at
  floors 1 and 11 (the report authorizes it, so no MISSED is counted);
- read floor: a table with trailing blank lines read at the default
  floor of one and described at eleven, which `profile.build_document`
  accepts and describes differently from the same table read at eleven
  (its docstring states the rule and nothing checks it): 1 while
  unchecked.

K-2B-49 (OPEN): the orchestrator's calls of 2026-09-18, made under the
owner's rule and reversible by the owner, held still the same way:

- point-free grid: twenty-four saturated grids of tenths whose whole
  numbers are written bare, at a floor of eleven and seeds 4, 7 and 1,
  where the column-wide fill trades the style and width censuses against
  the count of different values (plan P4-D274); the style and width
  MISSED verdicts and the distinct-count MISSED verdicts, counted apart;
- subsecond: 400 moments written to the millisecond, every one with a
  fraction, whose twin writes every fraction as nought (plan P4-D296):
  the real cells with a fraction less the twin's;
- record class counts: a declared record number of forty whole numbers
  and one `ab` at a floor of eleven, whose block publishes
  `all_whole_numbers: false` beside a partition saying every cell is a
  number (plan P4-D298): 1 while it does.

Its fourth call, invariant W5 accepting a hand-written withheld map at a
raised floor (plan P4-D275), is held by the ledger's pinned nodes.

Printed: per shape, the MISSED verdicts summed over its runs (for
temperature, the runs holding a value more often than the mode count),
the runs with any MISSED verdict, and the runs made. The ledger bounds
the summed verdicts, not the runs: a bound equal to the number of runs
could never be passed, and a twin that misses one more check in a run
already missing is worse. Each is a must-not-get-worse bound with
target 0. A few minutes.

    .venv/bin/python tools/measurements/kpi_known_misses.py --kpi
"""

import collections
import datetime
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
from synthtwin import (  # noqa: E402
    contract, generation, parsing, profile, reading, rendering, taxonomy, validation,
)

kpi_rules.guard_this_tree()
value = {}
details = []


def column_text(name, cells):
    return name + "\n" + "\n".join(cells) + "\n"


with tempfile.TemporaryDirectory() as folder:
    home = pathlib.Path(folder)

    missed_runs = runs = missed_checks = 0
    for seed in ("4", "11"):
        here = home / f"percent-{seed}"
        here.mkdir()
        book = here / "study.xlsx"
        book.write_bytes(workbooks.study_book(2000, 0, "excel"))
        run = kpi_shapes.cycle(book, [], seed)
        runs += 1
        missed_runs += run["validate_twin"] != 0
        found = kpi_shapes.missed(validation.measure(
            contract.load_profile(str(run["description"])), str(run["twin"])))
        missed_checks += len(found)
        details += [f"percent seed {seed}: {run['validate_twin']}/{run['validate_real']} {found}"]
    value.update(percent_missed_checks=missed_checks, percent_missed_runs=missed_runs,
                 percent_runs=runs)

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
    missed_runs = runs = missed_checks = 0
    for floor in (1, 11):
        described = kpi_shapes.describe(home / f"dose-{floor}", "dose", column_text("dose", dose), floor)
        for seed in range(1, 10):
            found = kpi_shapes.missed(kpi_shapes.measure(
                described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))
            runs += 1
            missed_runs += bool(found)
            missed_checks += len(found)
            if found:
                details += [f"dose f{floor} s{seed}: {found}"]
    value.update(dose_missed_checks=missed_checks, dose_missed_runs=missed_runs, dose_runs=runs)

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
    missed_runs = runs = missed_checks = 0
    for seed in (3, 11):
        twin = generation.generate(described.loaded, seed)
        found = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
        runs += 1
        missed_runs += bool(found)
        missed_checks += len(found)
        if found:
            details += [f"heavy tail s{seed}: {found}"]
    value.update(heavy_tail_missed_checks=missed_checks, heavy_tail_missed_runs=missed_runs,
                 heavy_tail_runs=runs)

    def repeated(pairs):
        return [text for text, times in pairs for _copy in range(times)]

    def missed_over(stem, name, cells, floors, seeds, declared=None):
        checks = 0
        shuffled = list(cells)
        random.Random(1).shuffle(shuffled)
        for floor in floors:
            described = kpi_shapes.describe(home / f"{stem}-{floor}", name,
                                            column_text(name, shuffled), floor, declared)
            for seed in seeds:
                found = kpi_shapes.missed(kpi_shapes.measure(
                    described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))
                checks += len(found)
                if found:
                    details.append(f"{stem} f{floor} s{seed}: {found}")
        return checks

    value.update(date_joint_word_missed_checks=missed_over(
        "joint", "visit",
        repeated([("03/05/2020", 15), ("04/06/2020", 15), ("3/7/2020", 7), ("03/8/2020", 7)]),
        (11,), (4, 0, 1)))
    value.update(date_remainder_missed_checks=missed_over(
        "remainder", "visit",
        repeated([("11/05/2020", 10), ("11/15/2020", 17), ("12/20/2020", 17),
                  ("3/15/2020", 9), ("03/16/2020", 9), ("11/5/2020", 9)]),
        (1, 11), (4, 0, 1)))
    value.update(record_layout_missed_checks=missed_over(
        "layout", "record", repeated([("(-6)", 10), ("(-71)", 4), ("8xEa", 1)]),
        (None,), (4, 0, 1), ["record"]))

    band = [str(-index) for index in range(1, 13)] + ["0"] + repeated(
        [(str(index), 40) for index in range(1, 11)])
    short = 0
    for floor in (1, 11):
        described = kpi_shapes.describe(home / f"band-{floor}", "reading",
                                        column_text("reading", band), floor)
        published = described.block("reading")["n_distinct_values"]
        for seed in (7, 4):
            cells = [c for c in generation.generate(described.loaded, seed).columns[0] if c]
            held = len({parsing.parse_number(c) for c in cells})
            short += published - held
            details.append(f"band f{floor} s{seed}: {held} of {published}")
    value.update(band_split_distinct_short=short)

    calls = {}
    style_checks = distinct_checks = 0
    for case in range(24):
        draw = random.Random(1000 + case)
        low = draw.randrange(-30, 10)
        grid = []
        for step in range(draw.randrange(20, 60)):
            tenth = (low + step) / 10
            text = f"{tenth:.1f}"
            if text.endswith(".0"):
                text = str(int(round(tenth)))
            grid += [text] * draw.choice([1, 1, 1, 2, 3, 8, 12])
        draw.shuffle(grid)
        described = kpi_shapes.describe(home / f"grid-{case}", "v", column_text("v", grid), 11)
        for seed in (4, 7, 1):
            found = kpi_shapes.missed(kpi_shapes.measure(
                described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))
            distinct_checks += sum(1 for f in found if ":distinct." in f)
            style_checks += sum(1 for f in found if ":styles." in f or ":widths." in f)
            if found:
                details.append(f"grid {case} s{seed}: {found}")
    calls.update(point_free_style_missed_checks=style_checks,
                 point_free_distinct_missed_checks=distinct_checks)

    draw = random.Random(9)
    start = datetime.datetime(2021, 1, 1)
    moments = [
        (start + datetime.timedelta(seconds=draw.randrange(0, 86400 * 300),
                                    milliseconds=draw.randrange(1, 1000)))
        .strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        for _ in range(400)
    ]
    described = kpi_shapes.describe(home / "subsecond", "stamp", column_text("stamp", moments))
    twin_cells = kpi_shapes.twin_text(described, 4).splitlines()[1:]
    real_fractions = sum(1 for cell in moments if not cell.endswith(".000"))
    twin_fractions = sum(1 for cell in twin_cells if cell and not cell.endswith(".000"))
    calls.update(subsecond_fractions_lost=real_fractions - twin_fractions,
                 subsecond_real_fractions=real_fractions)
    details.append(f"subsecond: real {real_fractions} cells with a fraction, twin {twin_fractions}")

    records = [str(100001 + index) for index in range(40)] + ["ab"]
    described = kpi_shapes.describe(home / "record-classes", "record",
                                     column_text("record", records), 11, ["record"])
    block = described.block("record")
    reveals = block.get("all_whole_numbers") is False and block.get("n_numeric") == block.get(
        "n_present")
    calls.update(record_class_counts_reveal=int(reveals))
    details.append(f"record classes: all_whole_numbers {block.get('all_whole_numbers')}, "
                   f"n_numeric {block.get('n_numeric')} of {block.get('n_present')}")

    blank_tail = home / "blank-tail.csv"
    blank_tail.write_text("site\n" + "\n".join(["north"] * 30 + ["south"] * 30) + "\n\n\n\n",
                          encoding="utf-8")
    settings = taxonomy.Settings(small_cell_floor=11)
    documents = [
        profile.build_document(
            reading.read_table(str(blank_tail), small_cell_floor=read_at), settings, [], [], []
        )
        for read_at in (1, 11)
    ]
    value.update(read_floor_unchecked=int(documents[0] != documents[1]))
    details.append(f"read floor: described at 11, read at 1 and at 11 differ: {documents[0] != documents[1]}")

for line in details:
    print(line)
kpi_rules.emit("K-2B-47", value, "; ".join(details)[:2000])
kpi_rules.emit("K-2B-49", calls, "; ".join(line for line in details
                                         if line.startswith(("grid", "subsecond", "record classes")))[:2000])

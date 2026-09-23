"""K-2B-47, K-2B-49, K-2B-50 and K-2B-51 (OPEN): the carried misses and the two still with the owner.

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
  published mean (stage 3, deferred by the owner) -- at a floor of one;
  at the default of 11 the histogram and the mode are withheld and the
  mean comes back, so both floors are measured (landing 3.1's repair
  pass).

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
  (plan P4-D298), seeds 4, 0 and 1 -- at a floor of one, the default
  when this was written; at 11 the layouts of four and one cells are
  withheld and nothing is missed, so both floors are measured;
- band split: twelve negatives once each, a zero and 1 to 10 forty times
  each, where G5.2 gives a sign band more strata than it has points
  (plan P4-D274's named limit); the number of different values the twin
  falls short of the published count, summed over seeds 7 and 4 at
  floors 1 and 11 (the report authorizes it, so no MISSED is counted);
- read floor: a table with trailing blank lines read at a floor of one
  and described at eleven, which `profile.build_document` accepted and
  described differently from the same table read at eleven (its
  docstring states the rule and nothing checked it): HOW MANY PUBLISHED
  FACTS MOVE, which was 4, beside the boolean it used to be. CLOSED BY
  LANDING 3.1's GUARD (plan P4-D317): the publication guard now asks the
  file's blank places at the description's floor, so `build_document`
  REFUSES the table read at one, and a refused description publishes no
  fact at all -- the driver records that refusal (it crashed on it, the
  repair pass of that landing found) and counts nought facts moving;
- declared layout at the default: the 49-row declared identifier of
  plan P4-D182 at the shipped default of 11, whose twin misses
  `layout_forms.%%%` because its pooled groups' made-up spellings read
  as hexadecimal (plan P4-D320), seeds 1, 4 and 7.
- Fortran `D` exponent: 400 cells of the form `4.60D+03` at a floor of
  eleven, carried by the changelog's ceiling list and measured by
  nothing. The column is read as free text (0 of 400 numeric), so the
  twin writes stand-ins -- `1.55S-44` for `1.30D-08` -- and the
  validator misses NOTHING: the respelled cells are the report-only
  indicator, the MISSED verdicts are the bound that can fail.

WHAT THIS ENTRY DOES AND DOES NOT HOLD (round-2 ledger item 11, and
its repair pass). FOUR kinds of number live in K-2B-47 and they are not
the same thing:

* MEASURED REGRESSION BOUNDS -- every `*_missed_checks`, the band
  split's shortfall, the read floor's count of moving facts: each can
  rise, and a rise is red.
* THE SIZE OF THE SHAPE THE BOUND WAS TAKEN OVER -- `fortran_d_runs`
  (at least 3) and `fortran_d_cells` (at least 400). A ceiling held over
  less evidence is not the same ceiling: cutting the seeds here from
  (4, 0, 1) to one left the MISSED verdicts at 0 and the respelled count
  at 400, both inside their bounds, over a third of the runs, and
  nothing saw it (the repair pass of this pass, finding 3).
* REPORT-ONLY INDICATORS -- `read_floor_unchecked` and
  `fortran_d_cells_respelled`: each already stands at the largest value
  its shape can produce, so it cannot turn red; what moves it is its
  target of 0. `read_floor_unchecked` was the whole of this entry's read
  floor until this pass, and `int(a != b) <= 1` is a rule no description
  could ever break.
* COVERAGE TRACKED ELSEWHERE -- the two generator passes the oracle does
  not mirror (the width pass G6.6 and the empty-bin pass G6.7) are
  counted by K-P4-23's `uncovered`, not here, and the changelog's list
  of carried items should say so rather than sending every line to this
  entry.

K-2B-50 and K-2B-51 (OPEN), the two fidelity failures the changelog
leaves "still with the owner", which had no regression ceiling at all
until this pass (round-2 ledger item 1):

- pooled numbers beside labels: 100 `alpha`, twenty `100` and ten each
  of 200 to 209 at a floor of eleven. The numeric subset's mean and
  population spread came back as 100 and 3.027650 against 187.083333 and
  39.033017, and BOTH files validated with nothing missed, so no miss
  count could see it. The errors themselves are the bound; the existing
  test asserted only that the mean error is over 50, which a worse twin
  passes. CLOSED by the owner's decision of 2026-09-21 (plan P4-D302):
  the pool publishes its mean and not its spread, method G8.3c places
  the twin's made-up numbers on that mean, and the mean error is nought
  while the spread error, which nothing published constrains any more,
  is a recorded bound of 2.059274;
- the absorbed mark: sixty moments at midnight on each of two days
  beside five `T` spellings of the first, at a floor of eleven. The
  description publishes `datetime`, three distinct values and 125 space
  separators, and its twin comes back as `binary` and misses three
  checks while the real file misses none.

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
import statistics
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tests"))
import kpi_rules  # noqa: E402
import kpi_shapes  # noqa: E402
import workbooks  # noqa: E402
from synthtwin import (  # noqa: E402
    contract, errors, generation, parsing, profile, reading, rendering, taxonomy,
    validation,
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
    # AND AT A FLOOR OF ONE, where the carried miss still stands (the
    # repair pass of landing 3.1). At the default of 11 the charges'
    # histogram and mode are withheld and the twin's mean comes back, so
    # the key above fell from 2 to 0 by the default withholding more, not
    # by a repair; the miss the tail landing owns is watched here.
    described = kpi_shapes.describe(home / "heavy-one", "charge",
                                    column_text("charge", charges), 1)
    floor_one_checks = 0
    for seed in (3, 11):
        twin = generation.generate(described.loaded, seed)
        found = kpi_shapes.missed(kpi_shapes.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
        floor_one_checks += len(found)
        if found:
            details += [f"heavy tail f1 s{seed}: {found}"]
    value.update(heavy_tail_missed_checks_floor_one=floor_one_checks)

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
    # ...and at a floor of one, where P4-D298's miss still stands: the
    # default of 11 withholds the layouts of four and one cells, so the
    # key above fell from 3 to 0 by withholding, not by a repair.
    value.update(record_layout_missed_checks_floor_one=missed_over(
        "layout", "record", repeated([("(-6)", 10), ("(-71)", 4), ("8xEa", 1)]),
        (1,), (4, 0, 1), ["record"]))
    # THE DECLARED IDENTIFIER OF P4-D182 AT THE DEFAULT (plan P4-D320,
    # the repair pass of landing 3.1): its pooled groups are written
    # `A0`, `A1` and `0e0`, which read as hexadecimal and rename every
    # layout, so its twin misses `layout_forms.%%%` on every seed. Held
    # here so it can neither spread nor be repaired unseen.
    review = ([f"N_{index}" for index in range(13)] + ["no!!"] * 5 + ["x-y"] * 8
              + ["913"] * 12 + ["-3"] * 11)
    declared_checks = 0
    described = kpi_shapes.describe(home / "declared-layout", "value",
                                    column_text("value", review), None, ["value"])
    for seed in (1, 4, 7):
        found = kpi_shapes.missed(kpi_shapes.measure(
            described, kpi_shapes.twin_text(described, seed), f"t{seed}.csv"))
        declared_checks += len(found)
        details.append(f"declared layout default s{seed}: {found}")
    value.update(declared_layout_default_missed_checks=declared_checks)

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
                          encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    # A TABLE READ AT ONE FLOOR AND DESCRIBED AT ANOTHER IS NOW REFUSED
    # (plan P4-D317, stage 3 landing 3.1), and that refusal is the
    # measurement here rather than a crash: this driver built both
    # descriptions to count the facts that move between them, and the
    # product stopped the one that reads a table at a floor of one and
    # describes it at eleven -- the blank-line places such a read
    # publishes are below the describing floor. A refused description
    # publishes nothing, so nought facts move and the residue is
    # recorded as REFUSED, which is what "unchecked" became.
    documents = []
    refused = ""
    for read_at in (1, 11):
        try:
            documents += [
                profile.build_document(
                    reading.read_table(str(blank_tail), small_cell_floor=read_at),
                    settings,
                    [],
                    [],
                    [],
                )
            ]
        except errors.ProfileError as stopped:
            refused = f"read at {read_at}: {type(stopped).__name__}"
            break

    def leaves(node, path=""):
        """Every published fact of a description, as path -> value."""
        if isinstance(node, dict):
            for key in sorted(node):
                yield from leaves(node[key], f"{path}.{key}")
        elif isinstance(node, list):
            for place in range(len(node)):
                yield from leaves(node[place], f"{path}[{place}]")
        else:
            yield path, node

    read_at_one = dict(leaves(documents[0])) if documents else {}
    read_at_eleven = dict(leaves(documents[1])) if len(documents) > 1 else {}
    differing = sorted(
        key for key in set(read_at_one) | set(read_at_eleven)
        if read_at_one.get(key, "(absent)") != read_at_eleven.get(key, "(absent)")
    )
    if refused:
        # The description the two were to be compared through was never
        # written, so no published fact of it can differ from another.
        differing = []
    # THE FACTS, NOT THE BOOLEAN (round-2 ledger item 11). This key was
    # int(documents[0] != documents[1]) against a bound of at most 1, so
    # no description this defect could produce would ever fail it. The
    # COUNT of facts that move can rise; the boolean is kept beside it as
    # the report-only indicator it always was.
    value.update(
        read_floor_facts_differing=len(differing),
        read_floor_unchecked=0
        if refused or len(documents) < 2
        else int(documents[0] != documents[1]),
    )
    details.append(
        f"read floor: described at 11, {refused} -- no description was written"
        if refused
        else (
            f"read floor: described at 11, read at 1 and at 11 differ in "
            f"{len(differing)} published facts: {differing}"
        )
    )

    # The Fortran `D` exponent, carried by the changelog's ceiling list
    # and measured by nothing until this pass (round-2 ledger item 11).
    # The column is read as free text, so every cell is a stand-in and
    # the validator misses NOTHING: the respelling is the report-only
    # indicator and the missed checks are the bound that can fail.
    draw = random.Random("fortran-d")
    fortran = [
        f"{draw.randrange(100, 999) / 100:.2f}D{draw.choice('+-')}{draw.randrange(1, 10):02d}"
        for _ in range(400)
    ]
    described = kpi_shapes.describe(home / "fortran-d", "reading",
                                    column_text("reading", fortran), 11)
    block = described.block("reading")
    respelled = checks = runs = 0
    for seed in (4, 0, 1):
        twin = kpi_shapes.twin_text(described, seed)
        cells = [cell for cell in twin.splitlines()[1:] if cell]
        respelled += sum(1 for cell in cells if cell not in set(fortran))
        checks += len(kpi_shapes.missed(kpi_shapes.measure(described, twin, f"d{seed}.csv")))
        runs += 1
        details.append(f"fortran D s{seed}: twin writes {cells[0]!r} for a cell like "
                       f"{fortran[0]!r}; {respelled} respelled so far")
    value.update(fortran_d_missed_checks=checks, fortran_d_cells_respelled=respelled,
                 fortran_d_runs=runs, fortran_d_numeric_cells=block.get("n_numeric") or 0,
                 fortran_d_cells=block.get("n_present") or 0)
    details.append(f"fortran D: role {block['role']}, n_numeric {block.get('n_numeric')} "
                   f"of {block.get('n_present')}, {checks} MISSED over {runs} runs")

    # ---- K-2B-50: the pooled population of numbers beside labels -------
    # The first of the two fidelity failures that were still with the
    # owner (CHANGELOG "Still with the owner"), which no ceiling held:
    # the existing test asserted only that the mean error is over 50, so
    # a worse twin passed it (round-2 ledger item 1). CLOSED by the
    # owner's decision of 2026-09-21 (plan P4-D302). BOTH errors are
    # still measured here and both are bounds, but they are bounds of
    # different kinds: the mean is a published obligation and the spread
    # is not -- no description carries a pooled spread any more, so what
    # the second number records is how far the generator's own choice of
    # spacing lands from the table, which may not get worse.
    still_open = {}
    anchored = ["alpha"] * 100 + ["100"] * 20
    for number in range(200, 210):
        anchored += [str(number)] * 10
    described = kpi_shapes.describe(home / "anchored", "value",
                                    column_text("value", anchored), 11)

    def read_numbers(cells):
        found = []
        for cell in cells:
            number = parsing.parse_number(cell.strip())
            if number is not None:
                found += [float(number)]
        return found

    real_numbers = read_numbers(anchored)
    real_mean = statistics.fmean(real_numbers)
    real_spread = statistics.pstdev(real_numbers)
    mean_error = spread_error = 0.0
    pooled_checks = pooled_runs = 0
    for seed in (4, 0, 1):
        twin = kpi_shapes.twin_text(described, seed)
        twin_numbers = read_numbers([cell for cell in twin.splitlines()[1:] if cell])
        mean_error = max(mean_error, abs(statistics.fmean(twin_numbers) - real_mean))
        spread_error = max(spread_error, abs(statistics.pstdev(twin_numbers) - real_spread))
        pooled_checks += len(kpi_shapes.missed(
            kpi_shapes.measure(described, twin, f"p{seed}.csv")))
        pooled_runs += 1
        details.append(
            f"pooled numbers s{seed}: mean {statistics.fmean(twin_numbers):.6f} and spread "
            f"{statistics.pstdev(twin_numbers):.6f} against {real_mean:.6f} and "
            f"{real_spread:.6f}"
        )
    still_open.update(
        pooled_mean_error=round(mean_error, 6), pooled_spread_error=round(spread_error, 6),
        pooled_missed_checks=pooled_checks, pooled_runs=pooled_runs,
    )

    # ---- K-2B-51: the absorbed mark and the description no file meets --
    stamps = (["2025-01-01 00:00:00"] * 60 + ["2025-01-02 00:00:00"] * 60
              + ["2025-01-01T00:00:00"] * 5)
    random.Random(1).shuffle(stamps)
    described = kpi_shapes.describe(home / "absorbed-mark", "stamp",
                                    column_text("stamp", stamps), 11)
    block = described.block("stamp")
    twin_checks = real_checks = stamp_runs = 0
    for seed in (0, 4, 1):
        twin = kpi_shapes.twin_text(described, seed)
        found = kpi_shapes.missed(kpi_shapes.measure(described, twin, f"m{seed}.csv"))
        twin_checks = max(twin_checks, len(found))
        real_checks = max(real_checks, len(kpi_shapes.missed(kpi_shapes.measure(
            described, column_text("stamp", stamps), f"n{seed}.csv"))))
        stamp_runs += 1
        details.append(f"absorbed mark s{seed}: twin misses {found}, the real file misses none")
    still_open.update(
        stamp_twin_missed_checks=twin_checks, stamp_real_missed_checks=real_checks,
        stamp_runs=stamp_runs, stamp_published_distinct=block["n_distinct"],
    )
    details.append(f"absorbed mark: role {block['role']}, n_distinct {block['n_distinct']}, "
                   f"separators {block.get('datetime_separators')}")

for line in details:
    print(line)
kpi_rules.emit("K-2B-47", value, "; ".join(details)[:2000])
kpi_rules.emit("K-2B-49", calls, "; ".join(line for line in details
                                         if line.startswith(("grid", "subsecond", "record classes")))[:2000])
kpi_rules.emit("K-2B-50", {k: v for k, v in still_open.items() if k.startswith("pooled_")},
               "; ".join(line for line in details if line.startswith("pooled numbers"))[:2000])
kpi_rules.emit("K-2B-51", {k: v for k, v in still_open.items() if k.startswith("stamp_")},
               "; ".join(line for line in details if line.startswith("absorbed mark"))[:2000])

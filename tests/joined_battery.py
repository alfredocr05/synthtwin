"""The twelve-column battery of three- and four-number cells (ledger K-P4-06).

The battery `tools/measurements/r_p4_40_l7_joined.py` walks in its
`battery()` section, built by the same recipe from the same seed: twelve
columns of 150 cells, three positions on the even columns and four on the
odd ones, `first/second/third/fourth` with `second` within eight of
`first` and `fourth` equal to `100 - first`, so the pairs pull against
each other inside one cell. Each column goes through the real producer,
the real loader and the real generator, and every pair of every twin is
scored the way the driver scores it: the rank agreement against G12.9's
window of two hundredths, and the rows holding the earlier number above
the later against the published `part_above`.

It is a module of its own, beside `fixtures.py`, because two readers
share it: `tests/test_joined_battery_readings.py`, which pins three of
the twelve columns, and the whole battery itself. It used to be shared
with WORKER PROCESSES -- the test spread the columns over a
`ProcessPoolExecutor`, and a worker imports the function it runs by
module name -- and that is why `one_column` takes a column number and
builds its own column rather than receiving a loaded one. The pool is
gone (the suite is network-dead and the pool's machinery takes a
socket); the shape it left is the right one anyway, because each column
is measured independently.
"""

from __future__ import annotations

import pathlib
import random
import tempfile

import fixtures
import synthtwin
from synthtwin import contract, generation, parsing, profile, reading, taxonomy

# The driver's own seed for the battery's cells and its forty twin seeds.
BATTERY_SEED = 20260904
SEEDS = tuple(range(40))
COLUMNS = 12
ROWS = 150
# G12.9's window, read from where the generator and the validator read it.
WINDOW = parsing.RANK_AGREEMENT_WINDOW


def battery_rows() -> "list[list[str]]":
    """The twelve columns' cells, exactly as the driver draws them."""
    random.seed(BATTERY_SEED)
    shapes: "list[list[str]]" = []
    for case in range(COLUMNS):
        rows: "list[str]" = []
        parts = 3 + case % 2
        for _ in range(ROWS):
            first = random.randint(10, 60)
            second = first + random.randint(-8, 8)
            third = random.randint(1, 40)
            fourth = 100 - first
            held = [first, second, third, fourth][:parts]
            rows += ["/".join(str(one) for one in held)]
        shapes += [rows]
    return shapes


def described(rows: "list[str]", folder: pathlib.Path) -> contract.Profile:
    """One battery column through the real producer and the real loader."""
    fixtures.write(folder, "battery.csv", "reading\n" + "\n".join(rows) + "\n")
    table = reading.read_table(
        str(folder / "battery.csv"), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table, taxonomy.Settings(), [], None, ["reading"]
    )
    return contract.load_profile(
        str(fixtures.write_profile(folder, "battery-p.json", document))
    )


def position_numbers(
    cells: "list[str]", facts: contract.JoinedFacts
) -> "list[list[float]]":
    """Every number each position of a twin wrote, row by row."""
    held: "list[list[float]]" = [[] for _place in range(facts.n_parts)]
    for cell in cells:
        if cell == "":
            continue
        pieces = cell.split(facts.separator)
        for place in range(facts.n_parts):
            if len(pieces) <= place:
                continue
            if parsing.parse_number(pieces[place]) is not None:
                held[place] += [float(pieces[place])]
    return held


def pair_scores(
    held: "list[list[float]]", facts: contract.JoinedFacts
) -> "list[tuple[float, int]]":
    """Each pair's distance from its published agreement, and its rows above.

    The agreement is rounded to the four places the description publishes
    it at before it is compared, as the driver and both reports compare it.
    """
    scores: "list[tuple[float, int]]" = []
    seat = 0
    for first in range(facts.n_parts):
        for second in range(first + 1, facts.n_parts):
            got = generation._rank_agreement(held[first], held[second])
            gap = abs(round(got, 4) - facts.part_agreements[seat])
            above = 0
            for row in range(len(held[first])):
                if held[first][row] > held[second][row]:
                    above = above + 1
            scores += [(gap, above)]
            seat = seat + 1
    return scores


def one_column(case: int) -> "tuple[int, int, int, str]":
    """Pairs, agreements outside the window, above-counts missed, and where.

    One battery column over all forty seeds, built from the recipe here
    rather than received, and about 6.5 s for a three-position column
    and 9 s for a four-position one on the reference machine. It says
    which synthtwin it imported, so a caller that resolved some other
    installation cannot pass for this tree.
    """
    rows = battery_rows()[case]
    pairs = 0
    outside = 0
    missed = 0
    with tempfile.TemporaryDirectory() as folder:
        loaded = described(rows, pathlib.Path(folder))
        facts = loaded.columns[0].facts
        if not isinstance(facts, contract.JoinedFacts):
            raise AssertionError(
                f"battery column {case} was read as {loaded.columns[0].role}"
            )
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            held = position_numbers(list(twin.columns[0]), facts)
            for seat, (gap, above) in enumerate(pair_scores(held, facts)):
                pairs = pairs + 1
                if gap > WINDOW:
                    outside = outside + 1
                if above != facts.part_above[seat]:
                    missed = missed + 1
    return pairs, outside, missed, str(synthtwin.__file__)

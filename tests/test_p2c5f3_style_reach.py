"""Review item P2-C5-F3: the published style map, over a producer battery.

THE CLAIM THIS FILE MAKES IS GENERAL, and it is stated that way because
the two previous closures of this obligation were stated over a single
column and were reopened by the next reviewer on a second one.

- Round 2 (P2-C2-F2) closed the map on a 51-cell column by placing the
  styles cell by cell with a look-ahead. Round 4 (P2-C4-F3) reopened it:
  the look-ahead can only place a style on a cell whose VALUE can wear
  it, and how many such cells a column has is decided by the strata, so
  the map was unreachable before the placement began.
- Round 4's repair added G5.2's carrier step, which moves cells into the
  strata that can carry, and closed the 51-cell column. Round 5
  (P2-C5-F3) reopened it again: "can carry" was a PLAN -- every stratum
  that is not a pinned end was counted, because the values step MAY take
  it to a whole number -- and on a ladder that crowds several different
  values inside one unit the plan does not come true. The step then
  moved no cell, because by its own count nothing needed moving, and a
  genuine 82-cell producer column published 34 point-free cells while
  the twin wrote 20.

So this file asks the LADDER, on descriptions the shipped producer
built, at every seed:

1. 240 producer-emitted numeric columns, each described by the real
   profiler and generated at 8 seeds -- 1,920 runs -- with every count
   the description NAMES written exactly;
2. the same runs recount `n_zero`, `n_negative`, `n_numeric`, both
   ladder ends and the count of different spellings, because the repair
   could have bought the style map with any of them;
3. every measured approximation inside its own two-sided bound, because
   the reach step spends ladder conformance and G5.6 reads its window
   off the strata the step produces.

Half the battery is drawn from ordinary mixed columns and half from the
shape the review item names -- several different values crowded inside
one unit, a flat rung above them, and a long tail -- because that is
where the plan and the ladder part company.

What is NOT claimed: nothing here says every contract-valid document
reaches its map. A description whose point-free demand is larger than
its published ends can leave room for cannot, and
`tests/test_p2c4f3_style_capacity.py` holds that shape to the bound that
does apply to it and records the residue in words.
"""

import pathlib
import random

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

# Eight seeds, including the three the review item names and the seed
# every frozen reference vector is built at.
SEEDS = (0, 1, 2, 3, 17, 63, 113, 12345)

# How many columns each family contributes. The two families and this
# count are what the docstring's "240 columns, 1,920 runs" refers to;
# changing either changes the claim, so they are named here once.
FAMILY_SIZE = 120


def _mixed(seed: int) -> "list[str]":
    """An ordinary numeric column: whole and fractional values, mixed forms.

    Every spelling is built here rather than taken from anywhere, and
    the values are plain arithmetic on the seed.
    """
    rng = random.Random(seed)
    kind = rng.randrange(6)
    values: list[str] = []
    for _group in range(rng.randrange(3, 10)):
        if rng.random() < 0.55:
            number = rng.randrange(-60, 60)
            form = rng.randrange(5)
            if form == 0:
                text = f"{number}"
            elif form == 1:
                text = f"0{number}" if number >= 0 else f"-0{-number}"
            elif form == 2:
                text = f"+{number}" if number >= 0 else f"{number}"
            elif form == 3:
                text = f"{number}.0"
            else:
                text = f"{number}e0"
        else:
            amount = rng.randrange(-6000, 6000) / 8
            if float(amount).is_integer():
                amount = amount + 0.125
            text = f"{amount}"
        values = values + [text] * rng.randrange(1, 22)
    rng.shuffle(values)
    if kind == 5:
        values = values + ["n/a "] * rng.randrange(1, 4)
    if kind == 4:
        values = values + [""] * rng.randrange(1, 6)
    return values


def _crowded(seed: int) -> "list[str]":
    """The shape of the review item: several values inside one unit.

    A run of eighths, the whole number above them holding the largest
    group, a block of whole negatives, one fractional value at each end.
    The ladder such a column publishes is flat across the whole number
    and crowded below it, which is exactly where a stratum that the
    carrier step counted as a carrier turns out to have no whole number
    of its own.
    """
    rng = random.Random(seed)
    values: list[str] = []
    base = rng.randrange(0, 4)
    for step in range(rng.randrange(3, 7)):
        values = values + [f"{base + (step + 1) / 8}"] * rng.randrange(4, 14)
    values = values + [f"{base + 1}"] * rng.randrange(8, 26)
    values = values + [f"-{rng.randrange(4, 90)}"] * rng.randrange(6, 18)
    values = values + [f"-{rng.randrange(30, 99)}.5"] * rng.randrange(2, 6)
    values = values + [f"{rng.randrange(20, 99)}.75"] * rng.randrange(2, 6)
    rng.shuffle(values)
    return values


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it with the real producer, load it."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _styles(twin: generation.Twin) -> "dict[str, int]":
    """The form of every numeric cell, read off the contract's own ladder."""
    counted: dict[str, int] = {}
    for cell in twin.columns[0]:
        if cell == "" or parsing.classify_number(cell) != parsing.NUMBER:
            continue
        style = parsing.numeric_style(cell)
        counted[style] = counted.get(style, 0) + 1
    return counted


def _battery(folder: pathlib.Path) -> "list[tuple[str, dict, contract.Profile]]":
    """Every battery description, built once through the real producer."""
    built: list[tuple[str, dict, contract.Profile]] = []
    for maker, tag in ((_mixed, "mixed"), (_crowded, "crowded")):
        for seed in range(FAMILY_SIZE):
            here = folder / f"{tag}-{seed}"
            here.mkdir()
            document, loaded = _described(here, maker(seed))
            if "numeric_styles" not in document["columns"][0]:
                continue
            built = built + [(f"{tag}-{seed}", document, loaded)]
    return built


def test_the_battery_is_the_size_this_file_claims(
    tmp_path: pathlib.Path,
) -> None:
    """The coverage is asserted, not described.

    A claim about "a producer battery" is worth exactly what its size
    is, and a battery that quietly shrank to two columns would leave
    every other test in this file passing. So the count is checked
    here, and the seeds with it.
    """
    cases = _battery(tmp_path)
    assert len(cases) == 2 * FAMILY_SIZE, len(cases)
    assert len(cases) * len(SEEDS) == 1920
    assert len({name for name, _document, _loaded in cases}) == len(cases)


def test_every_named_style_count_comes_out_exactly(
    tmp_path: pathlib.Path,
) -> None:
    """Point 1, over all 1,920 runs.

    A count the description NAMES is the published fact; the anonymous
    pool is the part it held back, and G6.4 gives way there first. So
    what is asserted is every named count, on every column, on every
    seed -- which is the general form of the claim two earlier closures
    made about one column each.
    """
    for name, document, loaded in _battery(tmp_path):
        published = document["columns"][0]["numeric_styles"]
        named = {
            style: count
            for style, count in published.items()
            if style != contract.WITHHELD
        }
        for seed in SEEDS:
            written = _styles(generation.generate(loaded, seed))
            for style, count in named.items():
                assert written.get(style, 0) >= count, (
                    name, seed, style, count, written, published
                )


def test_the_map_is_not_bought_with_another_exact_count(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2: what the reach step is not allowed to spend.

    Moving cells between strata could buy a form with `n_negative` or
    `n_zero`; giving a stratum a whole number could buy one with an end
    of the ladder or with the count of different values; and writing one
    stratum in two forms buys one with the count of different
    spellings. Every one of those is recounted here from the finished
    cells, on every column and every seed.
    """
    for name, document, loaded in _battery(tmp_path):
        column = document["columns"][0]
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            present = [cell for cell in twin.columns[0] if cell != ""]
            held = [
                parsing.parse_number(cell)
                for cell in present
                if parsing.classify_number(cell) == parsing.NUMBER
            ]
            numbers = [value for value in held if value is not None]
            assert len(numbers) == column["n_numeric"], (name, seed)
            assert len([one for one in numbers if one < 0.0]) == (
                column["n_negative"] - column["n_negative_unrepresentable"]
            ), (name, seed)
            assert len([one for one in numbers if one == 0.0]) == (
                column["n_zero"]
            ), (name, seed)
            assert min(numbers) == column["percentiles"]["min"], (name, seed)
            assert max(numbers) == column["percentiles"]["max"], (name, seed)
            assert len(set(numbers)) <= column["n_distinct_folded"], (
                name, seed
            )


def test_every_measured_bound_still_holds_over_the_battery(
    tmp_path: pathlib.Path,
) -> None:
    """Point 3: the widened rung window is met on every run.

    The reach step spends ladder conformance to buy an exact style map,
    and G5.6 reads its own `g_max` off the strata the step produces --
    so the window widens by exactly what was spent and the measurement
    must still land inside it. A window that quietly stopped holding
    would be the same defect in another place.
    """
    for name, _document, loaded in _battery(tmp_path):
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            outside = [
                measured
                for measured in twin.approximations
                if not measured.inside
            ]
            assert outside == [], (name, seed, outside)


def test_the_reach_step_is_what_carries_the_battery(
    tmp_path: pathlib.Path, monkeypatch: "object"
) -> None:
    """The mutant that makes the three tests above mean something.

    `_reach_sizes` reverted to the identity is exactly G5.2's carrier
    step as round 5 found it. At least one column of the crowded family
    must then miss a NAMED published count -- if none does, this battery
    is not exercising the rule it was built for.
    """
    cases = _battery(tmp_path)
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation,
        "_reach_sizes",
        lambda sizes, bands, rungs, whole, numbers, demand, plus: sizes,
    )
    missed = 0
    for _name, document, loaded in cases:
        published = document["columns"][0]["numeric_styles"]
        named = {
            style: count
            for style, count in published.items()
            if style != contract.WITHHELD
        }
        for seed in SEEDS:
            written = _styles(generation.generate(loaded, seed))
            for style, count in named.items():
                if written.get(style, 0) < count:
                    missed = missed + 1
                    break
    assert missed > 0, "the battery reaches no column the reach step carries"

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
import types

import pytest

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


# FLOOR ONE (plan P4-D316). This file's columns are small, and the counts
# the generator is held to here are published only at a floor that names
# groups of one and two; the default of 11 withholds or absorbs them.
_FLOOR_ONE = 1


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it with the real producer, load it."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path), small_cell_floor=_FLOOR_ONE)
    document = profile.build_document(table, taxonomy.Settings(small_cell_floor=_FLOOR_ONE), [])
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


_DESCRIBED: "list[tuple[str, dict, contract.Profile]]" = []


def _battery(folder: pathlib.Path) -> "list[tuple[str, dict, contract.Profile]]":
    """Every battery description, built once through the real producer.

    Kept after the first build, the way the sibling identifier battery
    is: four cases ask for it and the descriptions are a function of
    the values alone. Nothing here patches the PRODUCER -- the two
    mutants in this file replace steps of the generator -- so every
    caller gets the same descriptions it would have built itself, and
    `contract.load_profile` has already read the file by the time this
    returns, so the folder of the first caller is not needed again.
    """
    if _DESCRIBED:
        return _DESCRIBED
    built: list[tuple[str, dict, contract.Profile]] = []
    for maker, tag in ((_mixed, "mixed"), (_crowded, "crowded")):
        for seed in range(FAMILY_SIZE):
            here = folder / f"{tag}-{seed}"
            here.mkdir()
            document, loaded = _described(here, maker(seed))
            if "numeric_styles" not in document["columns"][0]:
                continue
            built = built + [(f"{tag}-{seed}", document, loaded)]
    _DESCRIBED.extend(built)
    return _DESCRIBED


# Every twin of that battery, generated once. THREE CASES BELOW WALK
# THE SAME 1,920 RUNS and each of them used to generate all of them for
# itself. The generation is a pure function of the loaded description
# and the seed, and `generation.Twin` is a frozen dataclass of tuples,
# so no case can leave a mark on one for the next.
#
# THE MUTANT CASES MUST NOT BE ANSWERED FROM HERE: each replaces a step
# of the generator and then asks what the twins look like, so a kept
# twin would hand one of them the shipped generator's answer and the
# red case would read green. They call `generation.generate` directly,
# and the assertion below is what holds that -- a kept twin is served
# only while both shipped steps are the ones installed.
_TWINS: "dict[tuple[str, int], generation.Twin]" = {}
# The shipped generator, held at import.
# WHAT COUNTS AS "THE GENERATOR HAS NOT MOVED". Not the one step
# today's mutants replace -- every name the generator module holds, and
# every name held by each synthtwin module the generator names. A case
# added here later that patches some OTHER part of the generator, or
# part of `parsing` or `taxonomy` below it, must be refused by the cache
# exactly as today's mutants are; a guard that knew only today's mutants
# would hand that case the shipped generator's answer and let it read
# green while its mutation was live. Roughly 2,300 names are watched,
# by identity, at a measured cost of 0.07 ms a call.
_MODULES = [generation] + sorted(
    (
        held
        for held in vars(generation).values()
        if isinstance(held, types.ModuleType)
        and getattr(held, "__name__", "").startswith("synthtwin")
    ),
    key=lambda held: held.__name__,
)
_SHIPPED_SURFACE = [
    (vars(module), name, vars(module)[name])
    for module in _MODULES
    for name in sorted(vars(module))
    if not name.startswith("__")
]


def _the_generator_that_moved() -> "str | None":
    """The name of the first watched member that is no longer the shipped one."""
    for held, name, shipped in _SHIPPED_SURFACE:
        if name not in held or held[name] is not shipped:
            return name
    return None


def _twin_of(
    name: str, loaded: contract.Profile, seed: int
) -> generation.Twin:
    """One twin of the battery, generated on first ask and kept."""
    moved = _the_generator_that_moved()
    assert moved is None, (
        f"the generator has been replaced at `{moved}`, so a kept twin "
        "would be the shipped generator's answer to a mutant's question. "
        "A case that patches the generator calls generation.generate "
        "directly."
    )
    key = (name, seed)
    if key not in _TWINS:
        _TWINS[key] = generation.generate(loaded, seed)
    return _TWINS[key]


def test_a_kept_twin_is_the_twin_the_generator_makes(
    tmp_path: pathlib.Path,
) -> None:
    """The cache may hand back only what a fresh run would have built.

    Three cases below read the same 1,920 twins out of `_twin_of`
    instead of generating them three times over. That is sound because
    generation is a function of the description and the seed -- and
    this is that soundness asserted rather than argued, on the first
    case of the battery.
    """
    name, _document, loaded = _battery(tmp_path)[0]
    for seed in SEEDS:
        assert _twin_of(name, loaded, seed) == generation.generate(
            loaded, seed
        ), (name, seed)


def test_a_kept_twin_is_never_served_over_a_replaced_generator(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The one way a shared twin could make a red case read green.

    Two mutants in this file replace a step of the generator and then
    ask what the twins look like. If either reached the cache it would
    be handed the SHIPPED generator's answer and would go green while
    the mutation was live, which is the hazard every shared fixture
    carries. The cache refuses instead, for both steps.

    AND NOT ONLY THE STEP TODAY'S MUTANTS REPLACE. A case added here
    later may patch some other part of the generator, or part of
    `parsing` or `taxonomy` below it, and the cache has to refuse that
    one too -- otherwise the new case reads the shipped generator's
    twins and goes green with its mutation live. The members named
    below are stand-ins for every one the old guard could not see.
    """
    name, _document, loaded = _battery(tmp_path)[0]
    for holder, member in (
        (generation, "_reach_sizes"),
        (generation, "_style_strata"),
        (generation, "_allocation"),
        (parsing, "parse_datetime"),
        (taxonomy, "_matching_date_format"),
    ):
        with monkeypatch.context() as patched:
            patched.setattr(holder, member, lambda *a, **k: None)
            with pytest.raises(AssertionError):
                _twin_of(name, loaded, SEEDS[0])


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
    made about one column each -- except the padded count G6.1 gives up
    where no published width can hold the value, which must be named on
    the twin's own page and is pinned to the eleven runs measured.
    """
    given_up = []
    for name, document, loaded in _battery(tmp_path):
        published = document["columns"][0]["numeric_styles"]
        named = {
            style: count
            for style, count in published.items()
            if style != contract.WITHHELD
        }
        for seed in SEEDS:
            built = _twin_of(name, loaded, seed)
            written = _styles(built)
            for style, count in named.items():
                if written.get(style, 0) >= count:
                    continue
                # THE ONE SHORTFALL THE METHOD NOW CHOOSES (method G6.1,
                # landings 2b.7 and 2b.16, plans P4-D66.4 and P4-D105). A
                # padded cell whose value no published field width can
                # hold gives the style up rather than being written one
                # zero too wide: before landing 2b.7 this battery "met"
                # these counts by writing `010` into a column whose only
                # published pad width is two. The count is then missed
                # and NAMED, never silent -- which is what is asserted --
                # and how many runs reach it is pinned below.
                assert style == parsing.STYLE_LEADING_ZERO, (
                    name, seed, style, count, written, published
                )
                named_facts = {note.fact for note in built.deviations}
                assert {"numeric_styles", "pad_widths"} <= named_facts, (
                    name, seed, named_facts
                )
                given_up += [(name, seed)]
    # Measured at the stage-2b integration: eleven runs of 1,920, on three
    # columns (mixed-22 at seven seeds, mixed-58 and mixed-100 at two).
    # Re-measured on e53d5f4 for the KPI ledger (K-P2-11): eight runs, all
    # of them on mixed-22, so the bound falls to eight and names the
    # column -- a short run on any NEW column is a regression the old
    # bound of eleven would have let through.
    assert len(given_up) <= 8, given_up
    assert {name for name, _seed in given_up} <= {"mixed-22"}, given_up


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
            twin = _twin_of(name, loaded, seed)
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
            # THE TWO ENDS ARE THE LADDER'S, and on a tail block they
            # are DERIVED rather than published (contract 6.7a, method
            # G5.3b): the reach step may not move them either way, so
            # they are read from `contract.tail_ladder` -- the ladder
            # every consumer reads -- and compared exactly as the
            # published pair was.
            facts = loaded.columns[0].facts
            assert isinstance(facts, contract.NumericFacts)
            ladder = contract.tail_ladder(facts)
            if ladder is None:
                ends = (
                    column["percentiles"]["min"],
                    column["percentiles"]["max"],
                )
            else:
                ends = (ladder[0], ladder[len(ladder) - 1])
            assert (min(numbers), max(numbers)) == ends, (name, seed)
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
            twin = _twin_of(name, loaded, seed)
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
        lambda sizes, bands, rungs, whole, numbers, demand, plus, grid: sizes,
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


# THE COLUMN THAT HAS TO WRITE AN EXPONENT CASE PAIR (R-P4-55). Fourteen
# cells, ten of them values no fixed-point window holds, and one value
# written THREE times -- once with a lower-case exponent and twice with an
# upper-case one. G6.5 names that pair as the only construction a
# numeric column has for a raw spelling count above its folded one, so
# this description publishes `n_distinct` 12 against `n_distinct_folded`
# 11 and a twin reaches both counts only by writing the pair.
#
# SEARCHED RATHER THAN COMPOSED, TWICE. The first search found twelve rows,
# the smallest size at which the shipped guard and the repaired one part
# company, with the upper-case spelling written once. A form held by one
# cell is named by no forms map since plan P4-D221 (stage 2 closed by the
# owner rulings of 2026-09-17): it pooled with the lower-case three, a pool
# is spelled by its values, and no twin of it wrote the pair. The search
# was run again with the upper-case spelling written twice, over the same
# ten values and draws of up to two more; this is the first column of 400
# draws on which both counts come out exactly at every seed below and the
# mutant costs the raw count at every one of them.
CASE_PAIR = (
    "5.233046213770536E+18",
    "4562546.455625033",
    "5.233046213770536E+18",
    "5.233046213770536e+18",
    "81022.18879182487",
    "0.08258517838289767",
    "0.09859816242635232",
    "65041600349440.74",
    "0.0007690174397238888",
    "236035630.34334084",
    "0.7523187990707938",
    "90010990.39664085",
    "9.938011207754502e-06",
    "1.780748719032198e+17",
)


def test_a_raw_count_above_a_folded_one_is_reached_by_the_case_pair(
    tmp_path: pathlib.Path,
) -> None:
    """Both spelling counts exactly, on the column that needs the pair.

    `n_distinct` counts different SPELLINGS and `n_distinct_folded`
    counts different folded identities, so a column where the first is
    larger than the second holds two texts that fold together. In a
    numeric column there is exactly one way to write that (G6.5): one
    value in `exponent_lower` and the same value in `exponent_upper`.
    This asserts the twin writes it -- both counts exact, at every seed.
    """
    document, loaded = _described(tmp_path, list(CASE_PAIR))
    column = document["columns"][0]
    assert column["n_distinct"] == column["n_distinct_folded"] + 1, (
        "this witness no longer asks for a case pair, so it no longer "
        f"tests what it was built for: {column['n_distinct']} raw against "
        f"{column['n_distinct_folded']} folded."
    )
    for seed in SEEDS:
        written = [
            cell
            for cell in generation.generate(loaded, seed).columns[0]
            if cell != ""
        ]
        raw = len(set(written))
        folded = len({parsing.folded(cell) for cell in written})
        assert raw == column["n_distinct"], (
            f"seed {seed}: the twin wrote {raw} different spellings against "
            f"a published {column['n_distinct']}."
        )
        assert folded == column["n_distinct_folded"], (
            f"seed {seed}: the twin wrote {folded} folded identities against "
            f"a published {column['n_distinct_folded']}."
        )


def test_the_two_ceilings_are_what_keeps_the_case_pair(
    tmp_path: pathlib.Path, monkeypatch: "object"
) -> None:
    """The mutant that makes the test above mean something (R-P4-55).

    `_style_strata` packs the styles over whole strata where the cell
    walk would spend more spellings than the column has. It shipped
    counting the RAW supply -- the distinct pairs of value and style --
    and comparing that number against the FOLDED ceiling. Charged that
    way the guard fires on exactly the columns the case pair exists for,
    packs it away, and leaves the twin one raw spelling short.

    The mutant here is that arithmetic put back: the raw supply against
    `wanted`, which is the folded ceiling. Every seed must then miss.
    """
    document, loaded = _described(tmp_path, list(CASE_PAIR))
    column = document["columns"][0]
    kept = generation._style_strata
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation,
        "_style_strata",
        lambda quotas, layout, values, whole, wanted, raw, styles, absorbing=(
            "", 0
        ): kept(
            quotas, layout, values, whole, wanted, wanted, styles, absorbing
        ),
    )
    short = 0
    for seed in SEEDS:
        written = [
            cell
            for cell in generation.generate(loaded, seed).columns[0]
            if cell != ""
        ]
        if len(set(written)) < column["n_distinct"]:
            short = short + 1
    assert short == len(SEEDS), (
        "the shipped ceiling costs this column its raw spelling count at "
        f"every seed, and here it cost it at {short} of {len(SEEDS)}."
    )

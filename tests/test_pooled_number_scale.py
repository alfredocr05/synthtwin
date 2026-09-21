"""The pool of held-back NUMBERS keeps its scale (plan P4-D301, K-2B-50).

THE REPRODUCTION, and every number here is measured off it. A column of
100 `alpha`, twenty `100` and ten each of the integers 200 to 209, at a
floor of eleven and seed 4. The floor publishes `alpha` and `100` and
pools the ten rare numbers, so before this landing the generator had one
published number to place its made-up ones beside: it wrote 95 to 105,
the numeric population's mean came back 100 against 187.083333 and its
population spread 3.027650 against 39.033017 -- and BOTH files validated
with nothing missed, because no published fact spoke of the pool at all.

WHAT THIS LANDING ADDS. Contract section 6.3.3 publishes three
aggregates over the pool -- how many of its cells read as numbers, their
mean and their population spread -- and method G8.3c places the twin's
made-up numbers on them. The aggregates are safe because the pool is a
group, and that is ASKED rather than asserted: `parsing.census_nameable`
is asked of the pooled count against the column's numeric total by the
producer, and again by the loader as invariant B4d.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the placement of G8.3c withdrawn (`generation._pooled_numbers_placed`
  answering nothing) -- `test_the_pooled_numbers_come_back_at_the_
  tables_own_scale`, whose twin then writes 95 to 105 again, and
  `test_the_validator_sees_a_twin_written_at_the_wrong_scale`, whose
  file then misses `suppressed.numbers.mean`;
* the producer's publication withdrawn -- the same two, and
  `test_the_pool_publishes_its_scale_only_as_a_group`;
* the disclosure rule withdrawn from the producer -- the two refusal
  halves of `test_the_pool_publishes_its_scale_only_as_a_group`, whose
  descriptions then name a mean over three cells and over one;
* the loader's half of it -- the `B4d` entry of
  `tests/test_contract_loader.py`'s battery;
* the oracle's mirror of G8.3c -- the `pooled_number_scale` case of
  `tests/test_generation_reference.py` and its registered mutant.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import statistics

from synthtwin import contract, generation, parsing, validation
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

# The reproduction the ledger entry names: 100 `alpha`, twenty `100`,
# and ten each of 200 to 209, at a floor of eleven.
FLOOR = ("--smallest-group", "11")


def _anchored_cells() -> "list[str]":
    cells = ["alpha"] * 100 + ["100"] * 20
    for number in range(200, 210):
        cells += [str(number)] * 10
    return cells


def _numbers(cells: "list[str]") -> "list[float]":
    """Every cell that reads as a number, as a number."""
    found: "list[float]" = []
    for cell in cells:
        body = parsing.trimmed(cell)
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        size = parsing.parse_number(body)
        if size is not None:
            found += [float(size)]
    return found


def test_the_pooled_numbers_come_back_at_the_tables_own_scale(
    tmp_path: pathlib.Path,
) -> None:
    """The whole of ledger K-2B-50, on its own shape and its own seed.

    The twin's numeric mean and population spread are the table's own,
    EXACTLY, and both files validate at exit 0 -- which is the point of
    the entry: nothing was ever missed here, so no miss count could see
    the defect and only the two numbers can.
    """
    cells = _anchored_cells()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["role"] == "categorical"
    assert second["role"] == first["role"]
    real = _numbers(cells)
    twin = _numbers(written)
    assert len(twin) == len(real) == first["n_numeric"] == 120
    assert statistics.fmean(twin) == statistics.fmean(real)
    assert statistics.pstdev(twin) == statistics.pstdev(real)
    # AND THE TWIN'S OWN POOL IS THE PUBLISHED ONE, which is what the
    # validator checks and what a re-description reads back.
    assert second["suppressed_numbers"] == first["suppressed_numbers"]


def test_the_description_publishes_the_pools_mean_and_spread(
    tmp_path: pathlib.Path,
) -> None:
    """Three aggregates over the pool, and the arithmetic they state.

    The pooled cells are the hundred the ten rare levels cover; their
    mean is 204.5 and their population spread the spread of ten
    consecutive integers.
    """
    cells = _anchored_cells()
    first, _second, _written, _twin, _real = _round_trip(
        tmp_path / "anchored", cells, FLOOR
    )
    scale = first["suppressed_numbers"]
    assert sorted(scale) == ["mean", "n_cells", "spread"]
    pooled = [float(value) for value in range(200, 210) for _each in range(10)]
    assert scale["n_cells"] == len(pooled) == 100
    assert scale["mean"] == statistics.fmean(pooled)
    assert scale["spread"] == statistics.pstdev(pooled)
    # NO CENSUS OF THIS DESCRIPTION NAMES A COUNT BELOW THE LINE, the
    # pooled count included, and no held-back level is named anywhere.
    line = parsing.census_floor(11)
    assert scale["n_cells"] >= line
    assert first["n_numeric"] - scale["n_cells"] in (0,) or (
        first["n_numeric"] - scale["n_cells"] >= line
    )
    published = {level["label"] for level in first["levels"]}
    assert published == {"alpha", "100"}
    for value in range(200, 210):
        assert str(value) not in published
    # AND THE LOADER READS BACK THE SAME THREE NUMBERS, which is the
    # other half of invariant B4d: the block is accepted and typed.
    loaded = _described_again(tmp_path / "again", cells)
    facts = loaded.columns[0].facts
    assert isinstance(facts, (contract.LabelFacts,))
    assert facts.suppressed_numbers.n_cells == scale["n_cells"]
    assert facts.suppressed_numbers.mean == scale["mean"]
    assert facts.suppressed_numbers.spread == scale["spread"]


def test_the_pool_publishes_its_scale_only_as_a_group(
    tmp_path: pathlib.Path,
) -> None:
    """The disclosure rule, asked of the pooled count on both sides.

    A pool of three numeric cells would publish a mean that is three
    people's values averaged, and a pool of one would publish that one
    person's value under another name; and a pool that leaves ONE
    published numeric cell behind hands that cell over by subtraction.
    A pool of two numeric LEVELS is refused for a different reason,
    stated in contract 6.3.3 as a producer obligation: their sizes are
    pinned by the published pool, so a mean and a spread solve for both
    values exactly. In every such case the block reaches the state that
    says nothing, which is the state a column whose held-back levels
    hold no number reaches too -- they are deliberately
    indistinguishable.
    """
    silent = {"n_cells": 0, "mean": None, "spread": None}
    # A pool of three numeric cells: three levels of one row each,
    # counted as missing by the level pass, so the numbers never reach
    # the pool at all.
    small = ["alpha"] * 100 + ["7", "8", "9"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "small", small, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == silent
    # A POOL OF TWO NUMERIC LEVELS whose sizes the published pool pins
    # is SOLVED by a mean and a spread -- two equations, two unknowns --
    # so the producer publishes nothing there either. Measured on the
    # negative shape of contract 6.3.3: 420 `missing` beside `-59` and
    # `-37` on ten rows each published a mean of -48 and a spread of 11,
    # and -48 -+ 11 is the two values the table held. The shape here is
    # the same arithmetic written positive, so that the form census
    # names nothing and the twin's own exits stay at nought.
    two = ["alpha"] * 420 + ["59"] * 10 + ["37"] * 10
    pair, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "two", two, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert pair["suppressed_levels"] == 2
    assert pair["suppressed_numbers"] == silent
    # A column whose held-back levels hold no number at all reaches the
    # SAME state, which is what makes the refusals above unreadable.
    words = ["alpha"] * 100 + ["beta"] * 3 + ["gamma"] * 3 + ["delta"] * 3
    other, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "words", words, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert other["suppressed_numbers"] == silent


def test_a_pool_of_numbers_beside_published_numbers_keeps_both_groups(
    tmp_path: pathlib.Path,
) -> None:
    """The complement clause: what the pool leaves is a group or nothing.

    On the reproduction the published numeric level `100` covers twenty
    rows, so the pool of a hundred leaves twenty behind -- a group, and
    above the line. The block speaks.
    """
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "anchored", _anchored_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    left = first["n_numeric"] - first["suppressed_numbers"]["n_cells"]
    assert left == 20
    assert parsing.census_nameable(
        [first["suppressed_numbers"]["n_cells"]], [first["n_numeric"]], 11
    )


def test_the_validator_sees_a_twin_written_at_the_wrong_scale(
    tmp_path: pathlib.Path,
) -> None:
    """THE MUTATION CHECK for the validator's half of this landing.

    A file whose pool sits at the scale the twin wrote BEFORE G8.3c --
    95 to 105 against a published mean of 204.5 -- misses
    `suppressed.numbers.mean`, and the real table misses nothing. Before
    this landing neither file missed anything, which is exactly why the
    defect could stand.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    loaded = _loaded(folder)
    wrong = ["alpha"] * 100 + ["100"] * 20
    for value in list(range(95, 100)) + list(range(101, 106)):
        wrong += [str(value)] * 10
    missed = _missed(loaded, folder / "wrong.csv", wrong)
    assert "value:suppressed.numbers.mean" in missed
    assert _missed(loaded, folder / "right.csv", cells) == []


def test_withdrawing_the_placement_puts_the_defect_back(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for the generator's half, run in place.

    With `_pooled_numbers_placed` answering nothing -- which is the
    state before plan P4-D301, every group left to the ordinary walk of
    G8.3a step 3 -- the twin writes 95 to 105 again and the two errors
    the ledger entry records come back at 87.083333 and 36.005366.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, _twin, _real = _round_trip(folder, cells, FLOOR)
    loaded = _loaded(folder)
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation,
        "_pooled_numbers_placed",
        lambda *_arguments: {},
    )
    written = generation.generate(loaded, 4).columns[0]
    real = _numbers(cells)
    twin = _numbers(list(written))
    assert round(abs(statistics.fmean(twin) - statistics.fmean(real)), 6) == (
        87.083333
    )
    assert round(abs(statistics.pstdev(twin) - statistics.pstdev(real)), 6) == (
        36.005366
    )


def _loaded(folder: pathlib.Path) -> contract.Profile:
    """The description THE PRODUCT wrote for these cells, loaded.

    Written by `synthtwin profile` in this module rather than composed
    here: a description a test writes by hand is a description no
    producer would have written, and the line-ending rule of
    `tests/test_description_line_endings.py` holds every module that
    hands a file to the loader to one of the two honest routes.
    """
    return contract.load_profile(str(folder / "real-profile.json"))


def _described_again(
    folder: pathlib.Path, cells: "list[str]"
) -> contract.Profile:
    """A second description of the same cells, written by the product."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(
        folder,
        "own.csv",
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
        + list(FLOOR)
    ) == 0
    return contract.load_profile(str(folder / "own-profile.json"))


def _missed(
    loaded: contract.Profile, path: pathlib.Path, cells: "list[str]"
) -> "list[str]":
    """Every MISSED verdict a file of these cells draws, by subcheck."""
    fixtures.write(
        path.parent,
        path.name,
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    outcome = validation.measure(loaded, str(path))
    return sorted(
        f"{check.column}:{check.subcheck}"
        for check in outcome.checks
        if check.verdict == validation.MISSED
    )

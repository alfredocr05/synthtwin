"""The pool of held-back NUMBERS keeps its scale (plan P4-D301, K-2B-50).

THE DEFECT, and every number here is measured off it. A column of 100
`alpha`, twenty `100` and ten each of the integers 200 to 209, at a
floor of eleven and seed 4. The floor publishes `alpha` and `100` and
pools the ten rare numbers, so the generator has one published number to
place its made-up ones beside: it writes 95 to 105, the numeric
population's mean comes back 100 against 187.083333 and its population
spread 3.027650 against 39.033017 -- and BOTH files validate with
nothing missed, because no published fact speaks of the pool at all.

WHAT THIS LANDING ADDS. Contract section 6.3.3 publishes three
aggregates over the pool -- how many of its cells read as numbers, their
mean and their population spread -- and method G8.3c places the twin's
made-up numbers on them.

**AND WHAT THE REPAIR PASS OF 2026-09-21 TOOK BACK OUT: the shape above
is REFUSED, and ledger K-2B-50 is OPEN again.** Its published spread,
2.8722813232690143, is exactly the smallest a pool of ten distinct whole
numbers can have, so the pair names all ten of the values the floor held
back. `tests/test_pooled_scale_refusals.py` holds that arithmetic and
the three other refusals the pass added. What is left here is the part
that stands: where a pool IS loose enough for its mean and its spread to
name nothing, they are published and G8.3c places the twin's numbers on
them. The shape this file measures that on is the same one made loose --
100 `alpha`, twenty `100`, and ten each of 200, 201, 240, 290, 350 and
420.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the placement of G8.3c withdrawn (`generation._pooled_numbers_placed`
  answering nothing) -- `test_the_pooled_numbers_come_back_at_the_
  tables_own_scale` and `test_withdrawing_the_placement_puts_the_
  defect_back`;
* the producer's publication withdrawn -- the same two, and
  `test_the_pool_publishes_its_scale_only_as_a_group`;
* the disclosure rule withdrawn from the producer -- the two refusal
  halves of `test_the_pool_publishes_its_scale_only_as_a_group`, whose
  descriptions then name a mean over three cells and over one;
* the loader's half of it -- the two `B4d` entries of
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
# and ten each of 200 to 209, at a floor of eleven. It publishes no
# scale since the repair pass of 2026-09-21; what it is still for is
# `tests/test_pooled_scale_refusals.py`, which measures why.
FLOOR = ("--smallest-group", "11")

# THE VALUES THE LOOSE SHAPE HOLDS BACK, ten rows each. Their closest
# two stand one apart and the rest far wider, so the pool stands well
# clear of the tightest arrangement its own grid allows and its mean and
# spread name nothing.
LOOSE = (200, 201, 240, 290, 350, 420)


def _anchored_cells() -> "list[str]":
    cells = ["alpha"] * 100 + ["100"] * 20
    for number in range(200, 210):
        cells += [str(number)] * 10
    return cells


def _loose_cells() -> "list[str]":
    cells = ["alpha"] * 100 + ["100"] * 20
    for number in LOOSE:
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
    """What G8.3c is worth where the pool may be published at all.

    Measured at seed 4: the twin's numeric mean stands 0.0002 from the
    table's and its population spread 0.0651, against the 50 and more
    they stand away with the placement withdrawn (the last test in this
    file). Both files validate at exit 0.
    """
    cells = _loose_cells()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "loose", cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["role"] == "categorical"
    assert second["role"] == first["role"]
    real = _numbers(cells)
    twin = _numbers(written)
    assert len(twin) == len(real) == first["n_numeric"] == 80
    assert abs(statistics.fmean(twin) - statistics.fmean(real)) < 0.01
    assert abs(statistics.pstdev(twin) - statistics.pstdev(real)) < 0.1


def test_the_description_publishes_the_pools_mean_and_spread(
    tmp_path: pathlib.Path,
) -> None:
    """Three aggregates over the pool, and the arithmetic they state."""
    cells = _loose_cells()
    first, _second, _written, _twin, _real = _round_trip(
        tmp_path / "loose", cells, FLOOR
    )
    scale = first["suppressed_numbers"]
    assert sorted(scale) == ["mean", "n_cells", "spread"]
    pooled = [float(value) for value in LOOSE for _each in range(10)]
    assert scale["n_cells"] == len(pooled) == 60
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
    for value in LOOSE:
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
    person's value under another name. A pool of two numeric LEVELS is
    refused for a different reason, stated in contract 6.3.3 as a
    producer obligation. In every such case the block reaches the state
    that says nothing, which is the state a column whose held-back
    levels hold no number reaches too -- they are deliberately
    indistinguishable.
    """
    silent = {"n_cells": 0, "mean": None, "spread": None}
    small = ["alpha"] * 100 + ["7", "8", "9"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "small", small, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == silent
    two = ["alpha"] * 420 + ["59"] * 10 + ["37"] * 10
    pair, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "two", two, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert pair["suppressed_levels"] == 2
    assert pair["suppressed_numbers"] == silent
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

    On the loose shape the published numeric level `100` covers twenty
    rows, so the pool of sixty leaves twenty behind -- a group, and
    above the line. The block speaks.
    """
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "loose", _loose_cells(), FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    left = first["n_numeric"] - first["suppressed_numbers"]["n_cells"]
    assert left == 20
    assert parsing.census_nameable(
        [first["suppressed_numbers"]["n_cells"]], [first["n_numeric"]], 11
    )


def test_a_file_at_the_wrong_scale_is_withheld_and_not_missed(
    tmp_path: pathlib.Path,
) -> None:
    """WHAT THIS CHECK IS WORTH TODAY, pinned rather than assumed.

    A file whose pool sits nowhere near the published scale -- 95 to 105
    against a published mean of 283.5 -- is NOT caught. Its own
    description publishes no pool, because an evenly spaced pool is the
    tightest arrangement there is and the producer refuses to name one,
    so both obligations close their gate and come back WITHHELD.

    That is measured here rather than left to be discovered again. The
    repair pass of 2026-09-21 tried reading the closed gate as a MISS
    and withdrew it: method G8.3c spaces the twin's own groups evenly
    too, so every twin this product writes would then miss a fact it was
    told to write. What closes it is G8.3c placing the pool as loosely
    as the published pair allows, which is a change to the generator
    that pass did not make; `validation._pooled_scale_checks` states it
    and the landing's report puts it to the owner.
    """
    cells = _loose_cells()
    folder = tmp_path / "loose"
    _first, _second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    loaded = _loaded(folder)
    wrong = ["alpha"] * 100 + ["100"] * 20
    for value in list(range(95, 100)) + list(range(101, 106)):
        wrong += [str(value)] * 6
    verdicts = _verdicts(loaded, folder / "wrong.csv", wrong)
    assert verdicts["suppressed.numbers.mean"] == validation.WITHHELD
    assert verdicts["suppressed.numbers.spread"] == validation.WITHHELD
    assert _missed(loaded, folder / "right.csv", cells) == []


def test_withdrawing_the_placement_puts_the_defect_back(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for the generator's half, run in place.

    With `_pooled_numbers_placed` answering nothing -- which is the
    state before plan P4-D301, every group left to the ordinary walk of
    G8.3a step 3 -- the twin writes small numbers beside the published
    `100` again and the two errors come back in the tens.
    """
    cells = _loose_cells()
    folder = tmp_path / "loose"
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
    assert abs(statistics.fmean(twin) - statistics.fmean(real)) > 50.0
    assert abs(statistics.pstdev(twin) - statistics.pstdev(real)) > 50.0


def _verdicts(
    loaded: contract.Profile, path: pathlib.Path, cells: "list[str]"
) -> "dict[str, str]":
    """Every verdict a file of these cells draws, by subcheck."""
    fixtures.write(
        path.parent,
        path.name,
        fixtures.rows_to_csv(["value"], [[cell] for cell in cells]),
    )
    outcome = validation.measure(loaded, str(path))
    return {check.subcheck: check.verdict for check in outcome.checks}


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

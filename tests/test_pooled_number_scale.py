"""The pool of held-back NUMBERS keeps its MEAN (plan P4-D302, K-2B-50).

THE DEFECT, and every number here is measured off it. A column of 100
`alpha`, twenty `100` and ten each of the integers 200 to 209, at a
floor of eleven and seed 4. The floor publishes `alpha` and `100` and
pools the ten rare numbers, so the generator has one published number to
place its made-up ones beside: it writes 95 to 105, the numeric
population's mean comes back 100 against 187.083333 -- and BOTH files
validate with nothing missed, because no published fact speaks of the
pool at all.

WHAT THE LANDING OF 2026-09-21 TRIED AND WHAT ITS REPAIR TOOK BACK.
Contract 6.3.3 published three aggregates over the pool -- the cell
count, the mean and the POPULATION SPREAD -- and method G8.3c placed the
twin's made-up numbers on the last two. That closed this shape and then
reopened it: the published spread, 2.8722813232690143, is exactly the
smallest a pool of ten distinct whole numbers can have, so the ten
held-back values came back as 200 to 209 by arithmetic from the
description, and the producer had to refuse the shape the ledger is
measured on.

WHAT THE OWNER DECIDED ON 2026-09-21, which this file now measures:
PUBLISH THE MEAN AND NOT THE SPREAD. Two equations over a tightly spaced
pool solve it; one equation over as many unknowns as the pool has
different values does not. The shape above is published again, the twin
meets its mean exactly, and what it costs is stated where it is paid --
method G12.12's window is no longer drawn from a published spread, and
no check anywhere says anything about how far apart a file's held-back
numbers lie.

THE RED CHECKS, each measured by withdrawing the rule in place:

* the placement of G8.3c withdrawn (`generation._pooled_numbers_placed`
  answering nothing) -- `test_the_pooled_numbers_come_back_at_the_
  tables_own_mean` and `test_withdrawing_the_placement_puts_the_defect_
  back`, whose twin is MISSED by the validator;
* the producer's publication withdrawn -- the same two;
* the disclosure rule withdrawn from the producer -- the two refusal
  halves of `test_the_pool_publishes_its_scale_only_as_a_group`;
* the loader's half of it -- the `B4d` entries of
  `tests/test_contract_loader.py`'s battery;
* the room rule and the width rule -- `tests/test_pooled_scale_
  refusals.py`;
* the oracle's mirror of G8.3c -- the `pooled_number_scale` case of
  `tests/test_generation_reference.py` and its registered mutant.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import statistics

from synthtwin import contract, generation, parsing, taxonomy, validation
from tests import fixtures
from tests.test_stage2_round_trip import _exit_of, _round_trip

# The reproduction the ledger entry names: 100 `alpha`, twenty `100`,
# and ten each of 200 to 209, at a floor of eleven.
FLOOR = ("--smallest-group", "11")

# THE VALUES A LOOSE POOL HOLDS BACK, ten rows each: the same shape with
# its ten consecutive numbers replaced by six spread far apart. It is
# kept because it is the shape the repair pass of 2026-09-21 measured
# the placement's worth on, and because a rule that behaves the same on
# a tight pool and a loose one is the point of the owner's decision.
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


def test_the_pooled_numbers_come_back_at_the_tables_own_mean(
    tmp_path: pathlib.Path,
) -> None:
    """THE OWNER'S OWN SHAPE, and the number they asked about.

    Measured at seed 4: the twin's numeric mean IS the table's, so the
    error is 0.0 against the 87.083333 the defect gives. Its population
    spread stands 2.0593 away against the 36.005366 the defect gives --
    better by an order of magnitude and NOT nought, because nothing
    published says how far apart the held-back numbers stood and the
    spacing method G8.3c writes is the generator's own.
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
    assert abs(statistics.pstdev(twin) - statistics.pstdev(real)) < 3.0


def test_the_description_publishes_the_pools_mean_and_no_spread(
    tmp_path: pathlib.Path,
) -> None:
    """Two aggregates over the pool, and no third."""
    cells = _anchored_cells()
    first, _second, _written, _twin, _real = _round_trip(
        tmp_path / "anchored", cells, FLOOR
    )
    scale = first["suppressed_numbers"]
    assert sorted(scale) == ["mean", "n_cells"]
    pooled = [float(value) for value in range(200, 210) for _each in range(10)]
    assert scale["n_cells"] == len(pooled) == 100
    assert scale["mean"] == statistics.fmean(pooled)
    # NO CENSUS OF THIS DESCRIPTION NAMES A COUNT BELOW THE LINE, the
    # pooled count included, and no held-back level is named anywhere.
    line = parsing.census_floor(11)
    assert scale["n_cells"] >= line
    assert first["n_numeric"] - scale["n_cells"] >= line
    published = {level["label"] for level in first["levels"]}
    assert published == {"alpha", "100"}
    for value in range(200, 210):
        assert str(value) not in published
    # AND THE LOADER READS BACK THE SAME TWO NUMBERS, which is the other
    # half of invariant B4d: the block is accepted and typed.
    loaded = _described_again(tmp_path / "again", cells)
    facts = loaded.columns[0].facts
    assert isinstance(facts, (contract.LabelFacts,))
    assert facts.suppressed_numbers.n_cells == scale["n_cells"]
    assert facts.suppressed_numbers.mean == scale["mean"]


def test_the_pool_publishes_its_scale_only_as_a_group(
    tmp_path: pathlib.Path,
) -> None:
    """The disclosure rule, asked of the pooled count on both sides.

    A pool of three numeric cells would publish a mean that is three
    people's values averaged, and a pool of one would publish that one
    person's value under another name. In every such case the block
    reaches the state that says nothing, which is the state a column
    whose held-back levels hold no number reaches too -- they are
    deliberately indistinguishable.
    """
    silent = {"n_cells": 0, "mean": None}
    small = ["alpha"] * 100 + ["7", "8", "9"]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "small", small, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"] == silent
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

    On the owner's own shape the published numeric level `100` covers
    twenty rows, so the pool of a hundred leaves twenty behind -- a
    group, and above the line. The block speaks.
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


def test_a_file_at_the_wrong_scale_is_missed_and_not_withheld(
    tmp_path: pathlib.Path,
) -> None:
    """WHAT THIS CHECK IS WORTH NOW, pinned rather than assumed.

    A file whose pool sits nowhere near the published mean -- 95 to 105
    against a published 204.5 -- IS caught, and that is the change the
    owner's decision bought. While the pool published a spread as well,
    the producer refused any pool standing at the tightest arrangement
    its values could take, method G8.3c wrote exactly that arrangement,
    and every twin this product wrote published no pool of its own: the
    check closed its own gate on every file and said so. A mean names no
    arrangement, tight or loose, so the twin's own description publishes
    its pool and the comparison happens.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert second["suppressed_numbers"]["n_cells"] == 100
    loaded = _loaded(folder)
    wrong = ["alpha"] * 100 + ["100"] * 20
    for value in list(range(95, 100)) + list(range(101, 106)):
        wrong += [str(value)] * 10
    verdicts = _verdicts(loaded, folder / "wrong.csv", wrong)
    assert verdicts["suppressed.numbers.mean"] == validation.MISSED
    assert "suppressed.numbers.spread" not in verdicts
    assert _missed(loaded, folder / "right.csv", cells) == []


def test_the_window_is_drawn_from_the_reach_and_not_from_a_spread(
    tmp_path: pathlib.Path,
) -> None:
    """METHOD G12.12's window, and the two numbers that decide it.

    A fifth of the largest magnitude the description states for this
    column: the pool's own mean of 204.5 against the published `100`,
    so 204.5 and a window of 40.9. The defect's pool sits 104.5 away,
    which is outside it; the twin as built sits on the mean.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, _twin, _real = _round_trip(
        folder, cells, FLOOR
    )
    facts = _loaded(folder).columns[0].facts
    assert isinstance(facts, (contract.LabelFacts,))
    scale = facts.suppressed_numbers
    assert scale.mean == 204.5
    reach = taxonomy.pooled_window(
        scale.mean, [entry.label for entry in facts.levels]
    )
    assert reach == 204.5 / 5.0
    assert abs(100.0 - scale.mean) > reach


def test_withdrawing_the_placement_puts_the_defect_back(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE MUTATION CHECK for the generator's half, run in place.

    With `_pooled_numbers_placed` answering nothing -- which is the
    state before this landing, every group left to the ordinary walk of
    G8.3a step 3 -- the twin writes 95 to 105 beside the published `100`
    again, the numeric mean falls back to 100, and the validator says so.
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
    assert abs(statistics.fmean(twin) - statistics.fmean(real)) > 50.0
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "mutant.csv", list(written)
    )


def test_a_twin_whose_pool_is_shifted_is_caught(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE WINDOW IS NOT A BLANKET EXCUSE, and this is the proof.

    The mutant moves the whole pooled population one held-back level's
    worth off its own centre -- the twin's pool moves a long way
    against a published 204.5 -- while every other rule of G8.3c stands
    and every other published fact is met. The window is 40.9 either
    side, so the check says so.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, _twin, _real = _round_trip(folder, cells, FLOOR)
    loaded = _loaded(folder)
    keep = generation._pooled_centre
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation,
        "_pooled_centre",
        lambda sizes, positions: keep(sizes, positions) - 20.0,
    )
    written = list(generation.generate(loaded, 4).columns[0])
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "shifted.csv", written
    )


def test_widening_the_window_without_bound_lets_the_defect_through(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """...AND THE WINDOW IS WHAT CATCHES IT, not something else.

    The same twin the first mutation check builds -- the placement
    withdrawn, its pool at 100 against a published 204.5 -- passes
    every check once `taxonomy.pooled_window` answers a width nothing
    can fall outside. Without this the two checks above would be
    consistent with the miss coming from some other obligation.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, _twin, _real = _round_trip(folder, cells, FLOOR)
    loaded = _loaded(folder)
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation, "_pooled_numbers_placed", lambda *_arguments: {}
    )
    written = list(generation.generate(loaded, 4).columns[0])
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "narrow.csv", written
    )
    monkeypatch.setattr(  # type: ignore[attr-defined]
        taxonomy, "pooled_window", lambda _middle, _labels: 1.0e18
    )
    assert _missed(loaded, folder / "wide.csv", written) == []


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

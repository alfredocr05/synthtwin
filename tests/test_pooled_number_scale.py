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

import dataclasses
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


def test_the_window_is_drawn_from_the_grid_and_not_from_a_magnitude(
    tmp_path: pathlib.Path,
) -> None:
    """METHOD G12.12's window, and the one thing that decides it.

    TWO PLACES OF THE COLUMN'S OWN GRID, and nothing else on the page.
    The owner's shape publishes `100` beside a pooled mean of 204.5 and
    writes whole numbers, so the window is 2; the defect's pool sits
    104.5 away, which is outside it, and the twin as built sits on the
    mean.

    AND THE SAME WINDOW WHATEVER THE MAGNITUDES ARE. A column of the
    same shape whose published number is `990` and whose pool is 940 to
    949 draws the same 2, where the withdrawn rule -- a fifth of the
    largest magnitude the description stated -- drew 198.0 from the
    `990` and admitted an error of 45.5 in a pool published at 944.5.
    A column written at one decimal place draws a fifth of a unit.
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
    reach = taxonomy.pooled_window([entry.label for entry in facts.levels])
    assert reach == 2.0
    assert abs(100.0 - scale.mean) > reach
    # The magnitudes move and the window does not.
    assert taxonomy.pooled_window(["alpha", "990"]) == 2.0
    assert taxonomy.pooled_window(["alpha", "3"]) == 2.0
    assert taxonomy.pooled_window(["alpha"]) == 2.0
    # ...but the GRID moves it, which is what it is drawn from.
    assert taxonomy.pooled_window(["alpha", "48.0"]) == 0.2
    assert taxonomy.pooled_window(["alpha", "4.500"]) == 0.002
    # The COARSEST published place wins, because the ladder's tiers end
    # on whole numbers and a placement may be rounded onto any of them.
    assert taxonomy.pooled_window(["alpha", "48.0", "50"]) == 2.0


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


def _with_a_shifted_pool(
    loaded: contract.Profile, moved: float
) -> contract.Profile:
    """The same description with the pool's published mean moved."""
    column = loaded.columns[0]
    facts = column.facts
    assert isinstance(facts, (contract.LabelFacts,))
    scale = facts.suppressed_numbers
    assert scale.mean is not None
    return dataclasses.replace(
        loaded,
        columns=(
            dataclasses.replace(
                column,
                facts=dataclasses.replace(
                    facts,
                    suppressed_numbers=dataclasses.replace(
                        scale, mean=scale.mean + moved
                    ),
                ),
            ),
        ),
    )


def test_a_twin_whose_pool_is_shifted_is_caught(
    tmp_path: pathlib.Path,
) -> None:
    """THE WINDOW IS NOT A BLANKET EXCUSE, and this is the proof.

    NOTHING IS PATCHED HERE. The generator is handed a description
    whose pooled mean stands 60 above the true one and writes a twin
    that obeys method G8.3c to the letter against it; that twin is then
    checked against the description the real table produced. Every
    other published fact is met -- the level counts, the spellings, the
    censuses, the row counts -- and the pool alone is in the wrong
    place, which is the shape of a generator defect rather than of a
    broken file.

    THE BOUNDARY IS WHERE THE RULE PUTS IT, measured either side: a
    pool moved by one place of the column's grid is inside the window
    of two and passes, a pool moved by three places is outside it and
    is MISSED. The arrears of G8.3c step 4 put the twin's pool on
    whatever mean it was given, so the miss is the whole of the shift.
    """
    cells = _anchored_cells()
    folder = tmp_path / "anchored"
    _first, _second, _written, _twin, _real = _round_trip(folder, cells, FLOOR)
    loaded = _loaded(folder)
    far = list(generation.generate(_with_a_shifted_pool(loaded, 60.0), 4).columns[0])
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "shifted.csv", far
    )
    near = list(generation.generate(_with_a_shifted_pool(loaded, 1.0), 4).columns[0])
    assert _missed(loaded, folder / "nudged.csv", near) == []
    out = list(generation.generate(_with_a_shifted_pool(loaded, 3.0), 4).columns[0])
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "past.csv", out
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
        taxonomy, "pooled_window", lambda _labels: 1.0e18
    )
    assert _missed(loaded, folder / "wide.csv", written) == []


def _dwarfed_cells() -> "list[str]":
    """The owner's shape with a published number LARGER than its pool.

    100 `alpha`, twenty `990`, ten each of 940 to 949: the floor
    publishes `alpha` and `990` and pools the ten rare numbers, whose
    mean is 944.5. It is the ordinary shape of a common code published
    beside rarer neighbours, and it is the shape the repair pass of
    2026-09-21 found the window could not see.
    """
    cells = ["alpha"] * 100 + ["990"] * 20
    for number in range(940, 950):
        cells += [str(number)] * 10
    return cells


def test_a_column_whose_published_number_dwarfs_its_pool_is_still_checked(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """THE BLOCKER OF THE 2026-09-21 REVIEW, closed and pinned.

    While method G12.12's window was a fifth of the largest magnitude
    the description stated, this column's published `990` set a window
    of 198.0 around a pooled mean of 944.5 -- a width drawn from a
    number that has nothing to do with the pool. The very defect ledger
    K-2B-50 names, G8.3c's placement withdrawn, puts the twin's pool at
    990.0 and its numeric mean at 990.000 against the table's 952.083,
    and that file EXITED CLEAN.

    The window is two places of this column's whole-number grid, so the
    45.5 the defect stands out by is outside it and the file is MISSED.
    The twin as built meets the published mean exactly.
    """
    cells = _dwarfed_cells()
    folder = tmp_path / "dwarfed"
    first, second, written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    assert first["suppressed_numbers"]["mean"] == 944.5
    assert second["suppressed_numbers"]["mean"] == 944.5
    assert statistics.fmean(_numbers(written)) == statistics.fmean(
        _numbers(cells)
    )
    loaded = _loaded(folder)
    facts = loaded.columns[0].facts
    assert isinstance(facts, (contract.LabelFacts,))
    assert taxonomy.pooled_window(
        [entry.label for entry in facts.levels]
    ) == 2.0
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation, "_pooled_numbers_placed", lambda *_arguments: {}
    )
    defect = list(generation.generate(loaded, 4).columns[0])
    assert abs(statistics.fmean(_numbers(defect)) - 990.0) < 0.001
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "defect.csv", defect
    )
    # ...and the withdrawn rule would have admitted it: a fifth of 990.
    assert abs(990.0 - 944.5) < 990.0 / 5.0


def _pushed_cells() -> "list[str]":
    """A pool with one group the census pushes a long way from its value.

    200 `alpha`, thirty `48.0` and five held-back one-decimal levels.
    Four of the five owe the census's `%%.%`; the fifth owes no form at
    all, and every two-figure one-place spelling near the pool's mean
    WEARS that form, so nothing near 52.7 may be written for it.
    """
    cells = ["alpha"] * 200 + ["48.0"] * 30
    for number in ("0.6", "20.1", "64.0", "90.8", "93.1"):
        cells += [number] * 10
    return cells


def test_a_group_the_census_pushes_away_is_carried_by_the_others(
    tmp_path: pathlib.Path, monkeypatch: object
) -> None:
    """METHOD G8.3c STEP 4, and the defect it closes.

    Before the arrears, the group owing no form was refused every
    spelling near the value it was asked for and the offer of step 3
    walked four hundred and twenty-eight places to `9.9`: the twin's
    own pool came back at 45.14 against a published 53.72, a sixth of
    the published mean out, on a twin that broke no other rule. That is
    what made a window drawn from the grid impossible and a window
    drawn from a magnitude the only thing left.

    Now the pushed group goes FIRST and the four after it are asked for
    what the cells still to be written must average, so the published
    mean is met inside the window of two places of this column's grid,
    which is a fifth of a unit.

    THE MUTATION CHECK, run in place: with `_pooled_value` answering
    nothing -- the placement no longer reading back what it wrote, so
    no group carries another's arrears -- the same twin is MISSED.
    """
    cells = _pushed_cells()
    folder = tmp_path / "pushed"
    first, second, _written, twin_exit, real_exit = _round_trip(
        folder, cells, FLOOR
    )
    assert (twin_exit, real_exit) == (0, 0)
    published = first["suppressed_numbers"]["mean"]
    assert published is not None
    loaded = _loaded(folder)
    facts = loaded.columns[0].facts
    assert isinstance(facts, (contract.LabelFacts,))
    window = taxonomy.pooled_window([entry.label for entry in facts.levels])
    assert window == 0.2
    assert second["suppressed_numbers"]["mean"] is not None
    assert abs(second["suppressed_numbers"]["mean"] - published) <= window
    monkeypatch.setattr(  # type: ignore[attr-defined]
        generation, "_pooled_value", lambda _spelling, _comma: None
    )
    adrift = list(generation.generate(loaded, 4).columns[0])
    assert "value:suppressed.numbers.mean" in _missed(
        loaded, folder / "adrift.csv", adrift
    )


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

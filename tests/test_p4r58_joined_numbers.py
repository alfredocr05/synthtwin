"""Residual R-P4-58: a joined position's numbers, checked at last.

`JoinedFacts.parts` holds a whole `NumericFacts` for each position of a
joined cell -- its own hundred-and-one-rung ladder, its own mean,
spread, shape and tail weight, its own count of different numbers. The
validator measured the two ENDS of each ladder, whether the position is
whole, and its style census. EVERYTHING BETWEEN was checked nowhere and
listed nowhere, while `_quantitative_of`'s own docstring said a joined
column's parts "are checked in their own right".

On a blood-pressure column that is about thirty obligations a reader
was never told about: the systolic average, spread, shape and tail
weight, its nine interior rungs and its ninety finer ones, and the same
again for the diastolic.

AND THE ENTRY TABLE'S RED BATTERY DOES NOT REACH THIS ROLE. Its
`every-role` fixture carries thirteen columns and none of them is
joined, so no perturbation there can turn a joined check red -- which
is true of the checks that shipped with the role, not only of these.
The red cases below are therefore written here, against a tampered
twin, rather than registered in that table.
"""

import pathlib
import random

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 5
FLOOR = 11


def _readings() -> "list[str]":
    """A hundred and twenty blood-pressure readings."""
    spread = random.Random(5)
    return [
        f"{spread.randint(105, 145)}/{spread.randint(65, 95)}"
        for _each in range(120)
    ]


def _described(folder: pathlib.Path):
    rows = _readings()
    path = fixtures.write(folder, "bp.csv", "bp\n" + "\n".join(rows) + "\n")
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(
        table,
        taxonomy.Settings(small_cell_floor=FLOOR),
        [],
        forced_measurements=["bp"],
    )
    written = fixtures.write_profile(folder, "bp-profile.json", document)
    return document, contract.load_profile(str(written))


def test_each_position_publishes_a_block_that_is_now_measured(
    tmp_path: pathlib.Path,
) -> None:
    """The facts, and the subchecks that hold the twin to them."""
    document, described = _described(tmp_path)
    block = document["columns"][0]
    assert block["role"] == "joined_numbers"
    first = block["parts"][0]
    for owed in ("mean", "std", "skew", "kurtosis", "n_distinct_values"):
        assert first.get(owed) is not None, owed
    assert "percentiles" in first and "percentiles_between" in first

    twin = generation.generate(described, SEED)
    outcome = validation.measure(
        described,
        str(fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))),
    )
    subchecks = {one.subcheck for one in outcome.checks}
    for owed in (
        "number 1 moments.mean",
        "number 1 moments.std",
        "number 1 moments.skew",
        "number 1 ladder.p50",
        "number 2 moments.mean",
        "number 2 ladder.p50",
    ):
        assert owed in subchecks, sorted(subchecks)

    # AND EACH IS BOUND TO ITS OWN POSITION'S FACT, so two positions
    # cannot hide behind one identity.
    for one in outcome.checks:
        if one.subcheck.startswith("number 1 moments."):
            assert one.fact.startswith("joined.parts[0]."), one
        if one.subcheck.startswith("number 2 moments."):
            assert one.fact.startswith("joined.parts[1]."), one


def test_no_obligation_of_a_joined_column_is_named_twice(
    tmp_path: pathlib.Path,
) -> None:
    """One published value, one subcheck.

    The ladder walk files `ladder.min` and `ladder.max`, which this
    role already measures as `ends.number N min` and `max`. Filing both
    would name one obligation twice under two identities -- the defect
    this residual is an instance of, made a second time by its own
    repair.
    """
    _document, described = _described(tmp_path)
    twin = generation.generate(described, SEED)
    outcome = validation.measure(
        described,
        str(fixtures.write(tmp_path, "once.csv", rendering.twin_csv(twin))),
    )
    seen: "dict[str, int]" = {}
    for one in outcome.checks:
        seen[one.subcheck] = seen.get(one.subcheck, 0) + 1
    assert not [key for key in seen if seen[key] > 1], seen
    assert "ends.number 1 min" in seen
    assert "number 1 ladder.min" not in seen


def test_a_position_that_moved_is_reported(tmp_path: pathlib.Path) -> None:
    """The red case, because the entry table's battery cannot reach here.

    Every systolic reading is shifted by twenty and the diastolic left
    alone. Before this residual was built the interior of that
    position's ladder and all four of its moments were checked nowhere,
    so most of this edit was invisible.
    """
    _document, described = _described(tmp_path)
    honest = rendering.twin_csv(generation.generate(described, SEED))
    lines = honest.splitlines()
    moved = [lines[0]] + [
        f"{int(line.split('/')[0]) + 20}/{line.split('/')[1]}"
        if "/" in line
        else line
        for line in lines[1:]
    ]

    kept = validation.measure(
        described, str(fixtures.write(tmp_path, "kept.csv", honest))
    )
    assert not [
        one for one in kept.checks if one.verdict == validation.MISSED
    ]

    seen = validation.measure(
        described,
        str(fixtures.write(tmp_path, "moved.csv", "\n".join(moved) + "\n")),
    )
    missed = {
        one.subcheck for one in seen.checks
        if one.verdict == validation.MISSED
    }
    # The interior rungs of the moved position, which nothing measured
    # before, are what this asserts -- the two ends were always checked.
    for owed in ("number 1 ladder.p25", "number 1 ladder.p50",
                 "number 1 ladder.p75"):
        assert owed in missed, sorted(missed)
    # AND THE POSITION THAT DID NOT MOVE IS NOT ACCUSED.
    assert not [one for one in missed if one.startswith("number 2 ")], missed

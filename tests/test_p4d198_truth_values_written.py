"""Plan P4-D198: a workbook column of free text writes its truth values.

THE REPRODUCTION (final skeptic of stage 2's close, MAJOR). A workbook column
of 160 whole numbers, 138 codes `noteNN` and two TRUE cells, beside boolean,
date and moment columns: at the default floor its census publishes
`boolean 2`, and the twin wrote no boolean cell at seeds 4 and 11, missing
`workbook.cell-classes` while the real workbook passed. The writer gives the
boolean class only to a cell spelled `TRUE` or `FALSE` (plan P4-D166), and the
made-up words of G9.5 were never spelled so.

Now groups of the column's text are spelled `TRUE` and `FALSE` to the
census's count, their lengths fixed before the walk spends the average.

NOT EVERY COUNT IS REACHED, and the battery below pins how many are. The
packing of classes and alphabets decides which group sizes stand in the
code alphabet as text before any spelling exists, and at most two groups can
be spelled as truth values; where the open groups there are singletons and
the census counts three or more, the twin still misses the census, and the
validator says MISSED. Measured over sixteen twins of eight such columns:
two held the census before this rule and eight hold it after.

Every test is a round trip: describe, generate, describe the twin, and
validate the twin and the real workbook at exit 0. The mutation named is
`generation._truth_words` choosing no group.
"""

import pathlib
import random

import pytest

from tests.test_files_review_repairs import _book, _cell, _held, _rows, _trip


def _flags(rows: int, truths: "list[bool]", seed: int) -> bytes:
    """Whole numbers, `noteNN` codes, and the truth values given, shuffled."""
    draw = random.Random(seed)
    kinds: "list[object]" = []
    for place in range(rows - len(truths)):
        if draw.random() < 0.55:
            kinds += [draw.randrange(1, 99)]
        else:
            kinds += [f"note{draw.randrange(10, 99)}"]
    kinds += list(truths)
    draw.shuffle(kinds)
    strings = ["flag", "arm"]
    grid = {1: [_cell("A1", "0", "s"), _cell("B1", "1", "s")]}
    for place in range(rows):
        number = 2 + place
        value = kinds[place]
        if isinstance(value, bool):
            cell = _cell(f"A{number}", "1" if value else "0", "b")
        elif isinstance(value, int):
            cell = _cell(f"A{number}", f"{value}")
        else:
            strings += [value]
            cell = _cell(f"A{number}", f"{len(strings) - 1}", "s")
        grid[number] = [cell, _cell(f"B{number}", f"{place % 3}")]
    return _book([("Data", _rows(grid))], strings)


@pytest.mark.parametrize(
    "truths",
    [[True, True], [True, False]],
)
def test_the_twin_writes_as_many_truth_values_as_the_census_counts(
    tmp_path: pathlib.Path, truths: "list[bool]"
) -> None:
    """Mutation: with `_truth_words` choosing nothing, every shape exits 3 on
    `workbook.cell-classes` at the default floor.
    """
    data = _flags(300, truths, 505)
    for seed in (4, 11):
        result = _trip(tmp_path / f"s{seed}", "flags", data, seed=seed)
        column = result["document"]["columns"][0]
        census = result["document"]["source"]["workbook"]["columns"][0]["cell_classes"]
        assert column["role"] == "free_text", column["role"]
        assert census["boolean"] == len(truths), census
        _held(result)
        again = result["again"]["source"]["workbook"]["columns"][0]["cell_classes"]
        assert again["boolean"] == len(truths), (seed, again)


def test_a_battery_of_truth_counts_holds_at_least_the_measured_share(
    tmp_path: pathlib.Path,
) -> None:
    """Eight columns of one to six truth values at two seeds: at least eight
    twins of sixteen meet the census, against two before the rule.

    Mutation: with `_truth_words` choosing nothing, two twins meet it.
    """
    held = 0
    for source in range(8):
        draw = random.Random(source)
        truths = [draw.random() < 0.7 for _each in range(draw.randrange(1, 7))]
        data = _flags(300, truths, 900 + source)
        for seed in (4, 11):
            result = _trip(tmp_path / f"{source}-{seed}", "flags", data, seed=seed)
            assert result["exits"]["real"] == 0
            if result["exits"]["twin"] == 0:
                held = held + 1
    assert held >= 8, held

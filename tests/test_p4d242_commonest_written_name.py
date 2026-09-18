"""A pooled closed census names a mark the CELLS wrote, not a default.

Plan P4-D242, closing the fourth of the five costs P4-D222 named and the
half of the final review of 2026-09-18's finding 5 that is a defect
rather than ruling 6's own cost.

Where no name of a CLOSED vocabulary reaches the disclosure line and
`parsing.census_pools` refuses a pool, `parsing.absorbed_census` counts
the whole population under one name. That name was the vocabulary's
DEFAULT -- `upper_t` for the marks between day and clock -- whether or
not a cell wrote it: twenty-four moments written twelve with a space and
twelve with a lower-case `t`, at a floor of eleven, published
`{"upper_t": 24}`. The name is the commonest the CELLS wrote now, ties to
the first in sorted order, which is the rule ruling 6 states everywhere
else: a rare spelling is counted into the COLUMN'S commonest spelling.

WHAT IS NOT CLOSED, AND THE ARITHMETIC THAT SAYS SO. The twin still
writes one mark where the source wrote three, and that is ruling 6's own
cost at a floor no spelling of the column clears. The review's proposed
repair -- publish the pure pool 0b0e0fc published -- is refused by the
disclosure rule and not by preference: the default branch is reached
only when `population > (names - 1) * (line - 1)` while every name is
below the line, which forces EVERY name of the vocabulary to have been
written, and the smallest of them can be as few as
`population - (names - 1) * (line - 1)` cells -- ONE, at a population of
twenty-one over three marks at a floor of eleven. A pool there names a
row. That is why `census_pools` refuses it and why no representable
census can hold all three spellings.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib

import pytest

from synthtwin import parsing
from tests.test_final_review_labels import _round_trip, _column


def _moments(marks: "list[str]") -> "list[str]":
    """One stamp per mark, over two days, at a minute each."""
    made = []
    for index in range(len(marks)):
        day = 1 + index % 2
        made += [
            f"2025-03-{day:02d}{marks[index]}09:{index % 60:02d}:00"
        ]
    return made


def test_a_tie_names_a_mark_the_cells_wrote(tmp_path: pathlib.Path) -> None:
    """Eight `T`, eight spaces and eight `t` at a floor of eleven."""
    marks = ["T"] * 8 + [" "] * 8 + ["t"] * 8
    result = _round_trip(
        tmp_path, {"moment": _moments(marks)}, ("--smallest-group", "11")
    )
    census = _column(result, "moment")["datetime_separators"]
    assert census == {"lower_t": 24}
    assert (result["twin_exit"], result["real_exit"]) == (0, 0)


def test_the_default_name_is_no_longer_written_for_an_unwritten_mark() -> None:
    """The rule itself, where the vocabulary's default was never used.

    Twelve spaces and twelve lower-case `t` over a closed vocabulary of
    three at a floor of eleven: no name reaches the line, the pool is
    refused, and the name written is the commonest of the two the cells
    wore -- never `upper_t`, which no cell of this column wrote.
    """
    counts = {"space": 12, "lower_t": 9}
    census = parsing.absorbed_census(
        counts, 21, 11, 3, parsing.SEPARATOR_UPPER_T
    )
    assert census == {"space": 21}
    # ...and where the two tie, the first name in sorted order takes it.
    tied = parsing.absorbed_census(
        {"space": 8, "lower_t": 8, "upper_t": 8}, 24, 11, 3,
        parsing.SEPARATOR_UPPER_T,
    )
    assert tied == {"lower_t": 24}


def test_a_pool_still_stands_where_the_rule_allows_one() -> None:
    """Below the band the census is one pool, exactly as it was."""
    census = parsing.absorbed_census(
        {"space": 10, "lower_t": 10}, 20, 11, 3, parsing.SEPARATOR_UPPER_T
    )
    assert census == {parsing.MISSING_WITHHELD: 20}


@pytest.mark.parametrize("names", [2, 3, 6])
def test_the_band_forces_every_name_to_have_been_written(names: int) -> None:
    """The arithmetic that refuses the review's proposed pool.

    In the band a pool is refused in, the population is more than
    `(names - 1) * (line - 1)` while every name is below the line, so no
    `names - 1` of them can cover it: every name of the vocabulary was
    written, and the smallest can be a single row.
    """
    line = parsing.census_floor(11)
    for population in range((names - 1) * (line - 1) + 1, names * line):
        assert not parsing.census_pools(population, 11, names)
        forced = population - (names - 1) * (line - 1)
        assert forced >= 1
